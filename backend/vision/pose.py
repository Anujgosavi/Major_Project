"""
Pose Processing Module.
Extracts body posture metrics including shoulder width, shoulder tilt, and head-to-shoulder offset.
"""

import numpy as np
from typing import Dict, Any


def process_pose_landmarks(pose_result) -> Dict[str, Any]:
    """
    Process MediaPipe PoseLandmarker result object and return extracted metrics.
    """
    res = {
        "pose_detected": False,
        "shoulder_width": float("nan"),
        "shoulder_tilt_deg": float("nan"),
        "shoulder_alignment_ratio": float("nan"),
        "head_offset_x": float("nan"),
        "head_offset_y": float("nan")
    }

    if not pose_result or not pose_result.pose_landmarks or len(pose_result.pose_landmarks) == 0:
        return res

    pose = pose_result.pose_landmarks[0]
    res["pose_detected"] = True

    # MediaPipe pose landmark indices
    nose = pose[0]
    left_shoulder = pose[11]
    right_shoulder = pose[12]

    ls = np.array([left_shoulder.x, left_shoulder.y])
    rs = np.array([right_shoulder.x, right_shoulder.y])
    nose_xy = np.array([nose.x, nose.y])

    shoulder_center = (ls + rs) / 2.0
    shoulder_width = float(np.linalg.norm(ls - rs))
    res["shoulder_width"] = shoulder_width

    # Tilt angle in degrees.
    # Use abs(dx) to normalize to [-90, +90] regardless of
    # landmark ordering direction (front camera often mirrors L/R).
    # This is the authoritative formula from NB1 Cell 78 (front_shoulder_tilt_degrees).
    dx = rs[0] - ls[0]
    dy = rs[1] - ls[1]
    tilt_angle = float(np.degrees(np.arctan2(dy, abs(dx) + 1e-12)))
    res["shoulder_tilt_deg"] = tilt_angle

    # Alignment ratio
    alignment_ratio = float(abs(ls[1] - rs[1]) / (shoulder_width + 1e-8))
    res["shoulder_alignment_ratio"] = alignment_ratio

    # Head offset relative to shoulder center
    res["head_offset_x"] = float(nose_xy[0] - shoulder_center[0])
    res["head_offset_y"] = float(nose_xy[1] - shoulder_center[1])

    return res
