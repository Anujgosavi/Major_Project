"""
UI / Frame Annotator Module.
Renders status banner, measurements panel, inference time, and active violation causes on OpenCV frames.
"""

import math
import cv2
import numpy as np
from typing import Dict, Any, Optional


# Human-readable labels for violation codes
VIOLATION_LABELS = {
    "screen_too_close":        "Distance too close (<40 cm)",
    "screen_distance_low":     "Distance low (40-45 cm)",
    "screen_distance_high":    "Distance high (75-85 cm)",
    "screen_too_far":          "Distance too far (>85 cm)",
    "head_pitch_warning":      "Head Pitch deviation >=15 deg",
    "head_pitch_non_safe":     "Head Pitch deviation >=30 deg",
    "head_yaw_warning":        "Head Yaw deviation >=15 deg",
    "head_yaw_non_safe":       "Head Yaw deviation >=30 deg",
    "head_roll_warning":       "Head Roll deviation >=15 deg",
    "head_roll_non_safe":      "Head Roll deviation >=30 deg",
    "shoulder_tilt_warning":   "Shoulder Tilt deviation >=10 deg",
    "shoulder_tilt_non_safe":  "Shoulder Tilt deviation >=20 deg",
    "eye_openness_warning":    "Eye Openness low (Squinting/Drowsy)",
    "eye_openness_non_safe":   "Eye Openness critical (Eyes closed)",
    "face_or_pose_not_detected": "Face / Pose not detected",
}

# Wellness indicator descriptions
WELLNESS_LABELS = {
    "dark_room":       "Dark Room (eye strain)",
    "bright_glare":    "Bright Glare / Overexposed",
    "backlight_glare": "Backlight Behind You",
    "squint":          "Sustained Squinting",
    "gaze_fixation":   "Screen Fixation (no eye movement)",
    "forward_lean":    "Forward Lean / Turtle-neck",
    "low_blink_rate":  "Low Blink Rate (eye dryness risk)",
}


def _safe_val(result: Dict[str, Any], key: str) -> Optional[float]:
    v = result.get(key)
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    return float(v)


def annotate_frame(
    frame: np.ndarray,
    result: Dict[str, Any],
    decision: Dict[str, Any],
    inference_ms: float = 0.0,
    rule_20_20_20_active: bool = False
) -> np.ndarray:
    """
    Overlay status banner, measurements, inference time, and active violation causes on a BGR frame.
    """
    output = frame.copy()
    h, w = output.shape[:2]

    status = decision.get("final_status", "UNKNOWN")
    frame_status = decision.get("frame_status", "UNKNOWN")
    reasons = decision.get("reasons", [])

    # --- Color mapping (BGR) ---
    STATUS_COLORS = {
        "SAFE":     (34, 170, 34),    # Green
        "WARNING":  (0, 165, 255),    # Amber/Orange
        "NON-SAFE": (0, 30, 210),     # Red
    }
    color = STATUS_COLORS.get(status, (100, 100, 100))  # Gray for UNKNOWN

    # ----------------------------------------------------------------
    # 1. Top Status Banner
    # ----------------------------------------------------------------
    banner_h = 72
    cv2.rectangle(output, (0, 0), (w, banner_h), color, -1)
    # Subtle dark gradient at bottom of banner
    cv2.rectangle(output, (0, banner_h - 5), (w, banner_h), (0, 0, 0), -1)

    status_text = f"STATUS: {status}"
    cv2.putText(output, status_text, (22, 51), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 5, cv2.LINE_AA)
    cv2.putText(output, status_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 3, cv2.LINE_AA)

    # Frame status badge (right side of banner, smaller)
    if frame_status != status:
        badge = f"frame: {frame_status}"
        cv2.putText(output, badge, (w - 200, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1, cv2.LINE_AA)

    # ----------------------------------------------------------------
    # 2. Semi-transparent side panel background for readability
    # ----------------------------------------------------------------
    panel_w = 280
    overlay_panel = output.copy()
    cv2.rectangle(overlay_panel, (0, banner_h), (panel_w, h), (20, 20, 20), -1)
    cv2.addWeighted(overlay_panel, 0.55, output, 0.45, 0, output)

    # ----------------------------------------------------------------
    # 3. Measurements
    # ----------------------------------------------------------------
    dist = _safe_val(result, "estimated_distance_cm")
    pitch = _safe_val(result, "head_pitch_deg")
    yaw = _safe_val(result, "head_yaw_deg")
    shoulder = _safe_val(result, "shoulder_tilt_deg")
    slouch = _safe_val(result, "slouch_ratio")
    eye_open = _safe_val(result, "mean_eye_open_ratio")
    blink_count = result.get("blink_count", 0)

    def _fmt(label, val, unit="", fmt=".1f", warn_key=None, danger_key=None):
        if val is None:
            return label, "N/A", (180, 180, 180)
        val_str = f"{val:{fmt}} {unit}".strip()
        if warn_key and warn_key in reasons:
            clr = (0, 200, 255)   # Amber
        elif danger_key and danger_key in reasons:
            clr = (60, 60, 255)   # Red
        else:
            clr = (255, 255, 255) # White
        return label, val_str, clr

    entries = [
        _fmt("Dist",    dist,     "cm",  warn_key="screen_distance_low",   danger_key="screen_too_close"),
        _fmt("Pitch",   pitch,    "deg", warn_key="head_pitch_warning",     danger_key="head_pitch_non_safe"),
        _fmt("Yaw",     yaw,      "deg", warn_key="head_yaw_warning",       danger_key="head_yaw_non_safe"),
        _fmt("Shoulder",shoulder, "deg", warn_key="shoulder_tilt_warning",  danger_key="shoulder_tilt_non_safe"),
        _fmt("Slouch",  slouch,   "",    warn_key="slouch_warning",         danger_key="slouch_non_safe", fmt=".2f"),
        _fmt("Eye Open",eye_open, "",    fmt=".3f"),
        ("Blinks", str(int(blink_count)), (200, 200, 200)),
    ]

    y = banner_h + 28
    for label, val_str, clr in entries:
        # Label in dimmer color
        cv2.putText(output, f"{label}:", (14, y), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (160, 160, 160), 1, cv2.LINE_AA)
        # Value in status-appropriate color
        cv2.putText(output, val_str, (130, y), cv2.FONT_HERSHEY_SIMPLEX, 0.60, clr, 2, cv2.LINE_AA)
        y += 32

    # ----------------------------------------------------------------
    # 4. Inference Time
    # ----------------------------------------------------------------
    # 7. Draw 20-20-20 Rule Reminder Banner
    # ----------------------------------------------------------------
    if rule_20_20_20_active:
        msg1 = "20-20-20 RULE: VISUAL BREAK"
        msg2 = "Look at something 20 feet away!"
        
        cv2.rectangle(output, (0, banner_h), (w, banner_h + 60), (0, 140, 255), -1)
        
        (tw1, th1), _ = cv2.getTextSize(msg1, cv2.FONT_HERSHEY_DUPLEX, 0.7, 2)
        cv2.putText(output, msg1, (w//2 - tw1//2, banner_h + 25), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        
        (tw2, th2), _ = cv2.getTextSize(msg2, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.putText(output, msg2, (w//2 - tw2//2, banner_h + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    inf_text = f"Inference: {inference_ms:.1f} ms"
    cv2.putText(output, inf_text, (14, y + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (120, 220, 120), 1, cv2.LINE_AA)

    # ----------------------------------------------------------------
    # 5. Models used (informational)
    # ----------------------------------------------------------------
    cv2.putText(output, "Model: MediaPipe", (14, y + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (90, 90, 90), 1, cv2.LINE_AA)

    # ----------------------------------------------------------------
    # 6. Wellness Indicators Panel
    # ----------------------------------------------------------------
    wellness_items = []

    # Brightness
    b_strain = result.get("brightness_strain", "ok")
    if b_strain != "ok":
        wellness_items.append((WELLNESS_LABELS.get(b_strain, b_strain), (0, 180, 255)))

    # Squint
    if result.get("squint_warning", False):
        wellness_items.append((WELLNESS_LABELS["squint"], (0, 200, 255)))

    # Gaze fixation
    if result.get("gaze_fixation_warning", False):
        wellness_items.append((WELLNESS_LABELS["gaze_fixation"], (80, 180, 255)))

    # Forward lean
    if result.get("forward_lean_warning", False):
        lean_ratio = result.get("forward_lean_ratio")
        label = WELLNESS_LABELS["forward_lean"]
        if lean_ratio:
            label += f" ({lean_ratio:.2f}x)"
        wellness_items.append((label, (0, 160, 255)))

    # Low blink rate
    blink_rate = result.get("blink_rate_per_min", 0)
    if blink_rate > 0 and blink_rate < 12.0:
        wellness_items.append((f"{WELLNESS_LABELS['low_blink_rate']} ({blink_rate:.1f}/min)", (0, 200, 180)))

    if wellness_items:
        # Draw wellness panel on right side of frame
        panel_x = w - 310
        panel_y_start = banner_h + 10
        well_panel = output.copy()
        cv2.rectangle(well_panel, (panel_x - 8, panel_y_start), (w, panel_y_start + len(wellness_items) * 30 + 14), (20, 20, 30), -1)
        cv2.addWeighted(well_panel, 0.65, output, 0.35, 0, output)

        cv2.putText(output, "WELLNESS ALERTS", (panel_x, panel_y_start + 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (160, 160, 160), 1, cv2.LINE_AA)
        for i, (label, dot_color) in enumerate(wellness_items):
            wy = panel_y_start + 34 + i * 28
            cv2.circle(output, (panel_x, wy - 5), 5, dot_color, -1)
            cv2.putText(output, label, (panel_x + 12, wy), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (230, 230, 230), 1, cv2.LINE_AA)

    # Blink rate (always shown in measurements area)
    blink_rate_text = f"Blink rate: {blink_rate:.1f}/min"
    cv2.putText(output, blink_rate_text, (14, y + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1, cv2.LINE_AA)

    # ----------------------------------------------------------------
    # 6. Active Causes bottom bar (only when not SAFE)
    # ----------------------------------------------------------------
    if reasons:
        cause_lines = []
        for r in reasons:
            cause_lines.append(VIOLATION_LABELS.get(r, r))

        bar_h = 28 * len(cause_lines) + 12
        cv2.rectangle(output, (0, h - bar_h), (w, h), (20, 20, 20), -1)
        # Colored left edge strip
        cv2.rectangle(output, (0, h - bar_h), (6, h), color, -1)

        for i, line in enumerate(cause_lines):
            cy = h - bar_h + 22 + i * 28
            cv2.putText(output, f"! {line}", (14, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 2, cv2.LINE_AA)

    return output
