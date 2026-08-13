"""
Distance Estimation Module.
Computes approximate screen distance in centimeters from normalized face width using inverse distance model.
"""

import math


def estimate_distance_cm(face_width_norm: float, a: float = 15.244, b: float = -0.0543) -> float:
    """
    Compute distance in cm: distance = a / (face_width_norm - b).
    Returns NaN if face_width_norm is invalid or zero-denominator encountered.
    """
    if face_width_norm is None or math.isnan(face_width_norm) or face_width_norm <= 0:
        return float("nan")

    denominator = face_width_norm - b
    if abs(denominator) < 1e-8:
        return float("nan")

    return float(a / denominator)
