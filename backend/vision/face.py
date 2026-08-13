"""
Face Processing Module.
Extracts facial metrics including head pitch, yaw, roll, normalized face width, eye openness, and iris gaze proxy.
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple


# Eye landmark definitions
LEFT_EYE = {"outer": 33, "inner": 133, "top": 159, "bottom": 145}
RIGHT_EYE = {"outer": 362, "inner": 263, "top": 386, "bottom": 374}

LEFT_IRIS_INDICES = [468, 469, 470, 471, 472]
RIGHT_IRIS_INDICES = [473, 474, 475, 476, 477]


def _2d_dist(p1: np.ndarray, p2: np.ndarray) -> float:
    return float(np.linalg.norm(p1 - p2))


def extract_eye_open_ratio(landmarks, eye: Dict[str, int]) -> float:
    """Compute vertical-to-horizontal aspect ratio for an eye."""
    outer = np.array([landmarks[eye["outer"]].x, landmarks[eye["outer"]].y])
    inner = np.array([landmarks[eye["inner"]].x, landmarks[eye["inner"]].y])
    top = np.array([landmarks[eye["top"]].x, landmarks[eye["top"]].y])
    bottom = np.array([landmarks[eye["bottom"]].x, landmarks[eye["bottom"]].y])

    width = _2d_dist(outer, inner)
    height = _2d_dist(top, bottom)

    if width < 1e-6:
        return 0.0
    return float(height / width)


def extract_gaze_proxy(landmarks, eye: Dict[str, int], iris_indices: list) -> Tuple[float, float]:
    """Compute relative gaze offset gx, gy inside eye bounding box."""
    outer = np.array([landmarks[eye["outer"]].x, landmarks[eye["outer"]].y])
    inner = np.array([landmarks[eye["inner"]].x, landmarks[eye["inner"]].y])
    top = np.array([landmarks[eye["top"]].x, landmarks[eye["top"]].y])
    bottom = np.array([landmarks[eye["bottom"]].x, landmarks[eye["bottom"]].y])

    iris_pts = np.array([[landmarks[i].x, landmarks[i].y] for i in iris_indices])
    iris_center = np.mean(iris_pts, axis=0)

    left_x = min(outer[0], inner[0])
    right_x = max(outer[0], inner[0])
    top_y = min(top[1], bottom[1])
    bottom_y = max(top[1], bottom[1])

    dx = right_x - left_x
    dy = bottom_y - top_y

    gx = (iris_center[0] - left_x) / (dx + 1e-8)
    gy = (iris_center[1] - top_y) / (dy + 1e-8)
    return float(gx), float(gy)


def process_face_landmarks(face_result) -> Dict[str, Any]:
    """
    Process MediaPipe FaceLandmarker result object and return extracted metrics dictionary.
    """
    res = {
        "face_detected": False,
        "face_width_norm": float("nan"),
        "head_pitch_deg": float("nan"),
        "head_yaw_deg": float("nan"),
        "head_roll_deg": float("nan"),
        "left_eye_open_ratio": float("nan"),
        "right_eye_open_ratio": float("nan"),
        "mean_eye_open_ratio": float("nan"),
        "mean_gaze_x": float("nan"),
        "mean_gaze_y": float("nan")
    }

    if not face_result or not face_result.face_landmarks or len(face_result.face_landmarks) == 0:
        return res

    landmarks = face_result.face_landmarks[0]
    res["face_detected"] = True

    # 1. Face width normalized (left cheek 234, right cheek 454)
    p_left = np.array([landmarks[234].x, landmarks[234].y])
    p_right = np.array([landmarks[454].x, landmarks[454].y])
    res["face_width_norm"] = _2d_dist(p_left, p_right)

    # 2. Eye openness
    left_open = extract_eye_open_ratio(landmarks, LEFT_EYE)
    right_open = extract_eye_open_ratio(landmarks, RIGHT_EYE)
    res["left_eye_open_ratio"] = left_open
    res["right_eye_open_ratio"] = right_open
    res["mean_eye_open_ratio"] = float((left_open + right_open) / 2.0)

    # 3. Iris / Gaze proxy
    if len(landmarks) > max(RIGHT_IRIS_INDICES):
        lgx, lgy = extract_gaze_proxy(landmarks, LEFT_EYE, LEFT_IRIS_INDICES)
        rgx, rgy = extract_gaze_proxy(landmarks, RIGHT_EYE, RIGHT_IRIS_INDICES)
        res["mean_gaze_x"] = float((lgx + rgx) / 2.0)
        res["mean_gaze_y"] = float((lgy + rgy) / 2.0)

    # 4. Facial transformation matrix (Head Pose Euler Angles)
    if hasattr(face_result, "facial_transformation_matrixes") and face_result.facial_transformation_matrixes:
        matrix = np.array(face_result.facial_transformation_matrixes[0])
        R = matrix[:3, :3]
        sy = np.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
        singular = sy < 1e-6

        if not singular:
            pitch = np.arctan2(R[2, 1], R[2, 2])
            yaw = np.arctan2(-R[2, 0], sy)
            roll = np.arctan2(R[1, 0], R[0, 0])
        else:
            pitch = np.arctan2(-R[1, 2], R[1, 1])
            yaw = np.arctan2(-R[2, 0], sy)
            roll = 0.0

        res["head_pitch_deg"] = float(np.degrees(pitch))
        res["head_yaw_deg"] = float(np.degrees(yaw))
        res["head_roll_deg"] = float(np.degrees(roll))

    return res
