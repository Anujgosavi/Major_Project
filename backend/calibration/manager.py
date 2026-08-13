"""
Calibration Manager Module.
Manages reading and writing user reference profiles and distance calibration parameters.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

DEFAULT_CALIB_DIR = Path(__file__).resolve().parent.parent.parent / "calibration"

DEFAULT_DISTANCE_CALIB = {
    "model_type": "inverse",
    "a": 15.244,
    "b": -0.0543,
    "norm_type": "face_width_norm",
    "unit": "cm"
}

DEFAULT_REFERENCE_PROFILE = {
    "face_width_norm": 0.285,
    "estimated_distance_cm": 60.0,
    "head_pitch_deg": 0.0,
    "head_yaw_deg": 0.0,
    "head_roll_deg": 0.0,
    "shoulder_tilt_deg": 0.0,
    "mean_eye_open_ratio": 0.245,
    "shoulder_width": 0.42
}


class CalibrationManager:
    def __init__(self, calib_dir: Optional[Path] = None):
        self.calib_dir = calib_dir or DEFAULT_CALIB_DIR
        self.calib_dir.mkdir(parents=True, exist_ok=True)
        
        self.distance_calib_file = self.calib_dir / "front_camera_distance_calibration.json"
        self.user_calib_file = self.calib_dir / "front_camera_calibration.json"
        
        self.distance_params = self._load_distance_calib()
        self.reference_profile = self._load_reference_profile()

    def _load_distance_calib(self) -> Dict[str, Any]:
        if not self.distance_calib_file.exists():
            return DEFAULT_DISTANCE_CALIB.copy()
        try:
            with open(self.distance_calib_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Error loading distance calibration: {e}. Using defaults.")
            return DEFAULT_DISTANCE_CALIB.copy()

    def _load_reference_profile(self) -> Dict[str, Any]:
        if not self.user_calib_file.exists():
            return DEFAULT_REFERENCE_PROFILE.copy()
        try:
            with open(self.user_calib_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("reference_profile", DEFAULT_REFERENCE_PROFILE.copy())
        except Exception as e:
            print(f"[!] Error loading reference profile: {e}. Using defaults.")
            return DEFAULT_REFERENCE_PROFILE.copy()

    def save_reference_profile(self, profile: Dict[str, Any]):
        self.reference_profile.update(profile)
        payload = {
            "reference_profile": self.reference_profile,
            "distance_calibration": self.distance_params
        }
        with open(self.user_calib_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def get_inverse_distance_params(self) -> Tuple[float, float]:
        a = float(self.distance_params.get("a", 15.244))
        b = float(self.distance_params.get("b", -0.0543))
        return a, b
