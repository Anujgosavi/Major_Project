"""
Single-Frame Safety Rules Module.
Evaluates single frame extracted metrics against policy thresholds to compute immediate frame status and violations.
"""

import math
from typing import Dict, Any, List, Optional


def evaluate_frame_safety(
    result: Dict[str, Any],
    policy: Dict[str, Any],
    reference_profile: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Evaluates single frame metrics against front_camera_final_policy rules.
    Returns dictionary with 'frame_status' ("SAFE", "WARNING", "NON-SAFE", or "UNKNOWN") and 'violations' list.
    """
    violations: List[str] = []

    # 1. Detection check
    if not result.get("face_detected", False) or not result.get("pose_detected", False):
        return {
            "frame_status": "UNKNOWN",
            "violations": ["face_or_pose_not_detected"]
        }

    warning = False
    non_safe = False
    ref = reference_profile or {}

    # 2. Distance Evaluation
    distance = result.get("estimated_distance_cm", float("nan"))
    if not math.isnan(distance):
        d_cfg = policy.get("distance", {})
        ns_min = d_cfg.get("non_safe_min_cm", 40.0)
        s_min = d_cfg.get("safe_min_cm", 45.0)
        s_max = d_cfg.get("safe_max_cm", 75.0)
        ns_max = d_cfg.get("non_safe_max_cm", 85.0)

        if distance < ns_min:
            violations.append("screen_too_close")
            non_safe = True
        elif distance < s_min:
            violations.append("screen_distance_low")
            warning = True
        elif distance > ns_max:
            violations.append("screen_too_far")
            non_safe = True
        elif distance > s_max:
            violations.append("screen_distance_high")
            warning = True

    # 3. Head Pitch Evaluation
    if "head_pitch_deg" in result and not math.isnan(result["head_pitch_deg"]):
        pitch_cfg = policy.get("head_pitch", {})
        w_deg = pitch_cfg.get("warning_deg", 15.0)
        ns_deg = pitch_cfg.get("non_safe_deg", 22.0)

        ref_pitch = ref.get("head_pitch_deg", 0.0)
        deviation = abs(result["head_pitch_deg"] - ref_pitch)

        if deviation >= ns_deg:
            violations.append("head_pitch_non_safe")
            non_safe = True
        elif deviation >= w_deg:
            violations.append("head_pitch_warning")
            warning = True

    # 4. Head Yaw Evaluation
    if "head_yaw_deg" in result and not math.isnan(result["head_yaw_deg"]):
        yaw_cfg = policy.get("head_yaw", {})
        w_deg = yaw_cfg.get("warning_deg", 15.0)
        ns_deg = yaw_cfg.get("non_safe_deg", 25.0)

        ref_yaw = ref.get("head_yaw_deg", 0.0)
        deviation = abs(result["head_yaw_deg"] - ref_yaw)

        if deviation >= ns_deg:
            violations.append("head_yaw_non_safe")
            non_safe = True
        elif deviation >= w_deg:
            violations.append("head_yaw_warning")
            warning = True

    # 5. Shoulder Tilt Evaluation
    if "shoulder_tilt_deg" in result and not math.isnan(result["shoulder_tilt_deg"]):
        shoulder_cfg = policy.get("shoulder_tilt", {})
        w_deg = shoulder_cfg.get("warning_deg", 10.0)
        ns_deg = shoulder_cfg.get("non_safe_deg", 20.0)

        ref_shoulder = ref.get("shoulder_tilt_deg", 0.0)
        deviation = abs(result["shoulder_tilt_deg"] - ref_shoulder)

        if deviation >= ns_deg:
            violations.append("shoulder_tilt_non_safe")
            non_safe = True
        elif deviation >= w_deg:
            violations.append("shoulder_tilt_warning")
            warning = True

    # 6. Head Roll Evaluation
    if "head_roll_deg" in result and not math.isnan(result["head_roll_deg"]):
        roll_cfg = policy.get("head_roll", {})
        if roll_cfg.get("enabled", False):
            w_deg = roll_cfg.get("warning_deg", 15.0)
            ns_deg = roll_cfg.get("non_safe_deg", 30.0)

            ref_roll = ref.get("head_roll_deg", 0.0)
            deviation = abs(result["head_roll_deg"] - ref_roll)

            if deviation >= ns_deg:
                violations.append("head_roll_non_safe")
                non_safe = True
            elif deviation >= w_deg:
                violations.append("head_roll_warning")
                warning = True

    # 7. Eye Openness Evaluation
    if "mean_eye_open_ratio" in result and not math.isnan(result["mean_eye_open_ratio"]):
        eye_cfg = policy.get("eye_openness", {})
        if eye_cfg.get("enabled", False):
            w_ratio = eye_cfg.get("warning_ratio", 0.45)
            ns_ratio = eye_cfg.get("non_safe_ratio", 0.30)

            openness = result["mean_eye_open_ratio"]

            if openness <= ns_ratio:
                violations.append("eye_openness_non_safe")
                non_safe = True
            elif openness <= w_ratio:
                violations.append("eye_openness_warning")
                warning = True

    # Note: Gaze, Blink count, and Squint are informational / supporting only (explicitly disabled as safety triggers)

    # 9. Slouch / Neck Compression Evaluation
    if "slouch_ratio" in result and not math.isnan(result["slouch_ratio"]):
        slouch_cfg = policy.get("slouch", {})
        if slouch_cfg.get("enabled", True):
            w_ratio = slouch_cfg.get("warning_ratio", 0.40)
            ns_ratio = slouch_cfg.get("non_safe_ratio", 0.30)
            
            slouch = result["slouch_ratio"]
            
            if slouch <= ns_ratio:
                violations.append("slouch_non_safe")
                non_safe = True
            elif slouch <= w_ratio:
                violations.append("slouch_warning")
                warning = True

    # Note: Gaze and Blink count are informational / supporting only (explicitly disabled as safety triggers)

    # Determine frame status
    if non_safe:
        frame_status = "NON-SAFE"
    elif warning:
        frame_status = "WARNING"
    else:
        frame_status = "SAFE"

    return {
        "frame_status": frame_status,
        "violations": violations
    }
