"""
Brightness Strain Detector.

Estimates ambient lighting stress on the user's eyes from the webcam frame itself.

Two independent signals are computed:
  1. frame_luminance  — mean Y (luma) of the full frame in YCrCb space.
                        Very dark → eye strain from trying to see.
                        Very bright / overexposed → glare strain.
  2. face_luminance   — same luma restricted to the face bounding box.
                        Used to detect the user's face being washed out by a
                        bright window or backlight behind them (backlight glare).

Strain classification:
  - "dark_room"       → frame too dark (luminance < dark_thresh)
  - "bright_glare"    → frame overexposed (luminance > bright_thresh)
  - "backlight_glare" → face much darker than background (face_luma << frame_luma)
  - "ok"              → no brightness strain detected

No machine learning model required. Pure numpy / OpenCV math.
"""

import cv2
import numpy as np
from typing import Dict, Any, Optional


# Default luminance thresholds (0-255 scale)
DARK_THRESH       = 50    # below this → room is too dark
BRIGHT_THRESH     = 210   # above this → overexposed / bright glare
BACKLIGHT_DELTA   = 40    # face ≥40 units darker than scene → backlight behind user


def _mean_luma(bgr: np.ndarray) -> float:
    """Convert BGR region to YCrCb and return mean luma (Y channel)."""
    ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
    return float(np.mean(ycrcb[:, :, 0]))


def analyze_brightness(
    frame_bgr: np.ndarray,
    face_bbox: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    Analyze lighting conditions from the webcam frame.

    Args:
        frame_bgr: Full BGR frame from OpenCV.
        face_bbox: Optional dict with keys x, y, w, h (pixel coords) for
                   the detected face region. If None, backlight detection is skipped.

    Returns:
        dict with:
          - frame_luminance (float, 0–255)
          - face_luminance  (float, 0–255) or None
          - brightness_strain (str): "ok" | "dark_room" | "bright_glare" | "backlight_glare"
          - brightness_warning (bool)
    """
    frame_luma = _mean_luma(frame_bgr)
    face_luma: Optional[float] = None

    if face_bbox is not None:
        x, y, w, h = face_bbox["x"], face_bbox["y"], face_bbox["w"], face_bbox["h"]
        # Clamp to frame boundaries
        h_f, w_f = frame_bgr.shape[:2]
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(w_f, x + w), min(h_f, y + h)
        if x2 > x1 and y2 > y1:
            face_region = frame_bgr[y1:y2, x1:x2]
            face_luma = _mean_luma(face_region)

    # Classify
    strain = "ok"
    if frame_luma < DARK_THRESH:
        strain = "dark_room"
    elif frame_luma > BRIGHT_THRESH:
        strain = "bright_glare"
    elif face_luma is not None and (frame_luma - face_luma) > BACKLIGHT_DELTA:
        strain = "backlight_glare"

    return {
        "frame_luminance":    round(frame_luma, 1),
        "face_luminance":     round(face_luma, 1) if face_luma is not None else None,
        "brightness_strain":  strain,
        "brightness_warning": strain != "ok",
    }
