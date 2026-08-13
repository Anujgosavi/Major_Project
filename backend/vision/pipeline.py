"""
Front Camera Vision Pipeline.
Unified orchestrator loading MediaPipe Face & Pose models, extracting features per frame,
and running all wellness detectors: blink, squint, gaze fixation, forward lean, brightness.
"""

import time
from pathlib import Path
from typing import Dict, Any, Optional

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from backend.calibration.manager import CalibrationManager
from backend.vision.face import process_face_landmarks
from backend.vision.pose import process_pose_landmarks
from backend.vision.distance import estimate_distance_cm
from backend.vision.blink import BlinkDetector
from backend.vision.squint import SquintDetector
from backend.vision.gaze_fixation import GazeFixationDetector
from backend.vision.forward_lean import ForwardLeanDetector
from backend.vision.brightness import analyze_brightness

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_MODELS_DIR = PROJECT_ROOT / "models"


class FrontCameraPipeline:
    def __init__(
        self,
        models_dir: Optional[Path] = None,
        calib_dir: Optional[Path] = None
    ):
        self.models_dir = models_dir or DEFAULT_MODELS_DIR
        self.calib_manager = CalibrationManager(calib_dir)

        # Retrieve inverse distance calibration params
        self.dist_a, self.dist_b = self.calib_manager.get_inverse_distance_params()

        # Retrieve user reference profile
        self.reference = self.calib_manager.reference_profile

        baseline_openness = self.reference.get("mean_eye_open_ratio", 0.245)

        # Initialize all wellness detectors
        self.blink_detector        = BlinkDetector(baseline_openness=baseline_openness)
        self.squint_detector       = SquintDetector(baseline_openness=baseline_openness)
        self.gaze_fixation_detector = GazeFixationDetector()
        self.forward_lean_detector  = ForwardLeanDetector()

        # EMA smoothing filter state (alpha = 0.7)
        self.ema_alpha = 0.70
        self._ema_state: Dict[str, float] = {}

        # Initialize MediaPipe models
        self._initialize_models()

    def _initialize_models(self):
        face_model_path = self.models_dir / "face_landmarker.task"
        pose_model_path = self.models_dir / "pose_landmarker_full.task"

        if not face_model_path.exists():
            raise FileNotFoundError(f"Missing face model at {face_model_path}. Run scripts/download_models.py.")
        if not pose_model_path.exists():
            raise FileNotFoundError(f"Missing pose model at {pose_model_path}. Run scripts/download_models.py.")

        base_opts = python.BaseOptions

        # Face Landmarker
        face_options = vision.FaceLandmarkerOptions(
            base_options=base_opts(model_asset_path=str(face_model_path)),
            running_mode=vision.RunningMode.IMAGE,
            num_faces=1,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True
        )
        self.face_landmarker = vision.FaceLandmarker.create_from_options(face_options)

        # Pose Landmarker
        pose_options = vision.PoseLandmarkerOptions(
            base_options=base_opts(model_asset_path=str(pose_model_path)),
            running_mode=vision.RunningMode.IMAGE,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_segmentation_masks=False
        )
        self.pose_landmarker = vision.PoseLandmarker.create_from_options(pose_options)

    def process_frame(self, frame_bgr, timestamp: Optional[float] = None) -> Dict[str, Any]:
        """
        Process a single BGR OpenCV frame and extract all ergonomic and wellness measurements.
        """
        ts = timestamp if timestamp is not None else time.time()

        # Convert BGR to RGB MediaPipe Image
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        # Run MediaPipe inference
        face_result = self.face_landmarker.detect(mp_image)
        pose_result = self.pose_landmarker.detect(mp_image)

        # Extract landmark-based metrics
        face_metrics = process_face_landmarks(face_result)
        pose_metrics = process_pose_landmarks(pose_result)

        # Combine base results
        result = {
            "timestamp":   ts,
            "image_shape": frame_bgr.shape
        }
        result.update(face_metrics)
        result.update(pose_metrics)

        # Estimated screen distance
        dist_cm = estimate_distance_cm(
            face_metrics["face_width_norm"],
            a=self.dist_a,
            b=self.dist_b
        )
        result["estimated_distance_cm"] = dist_cm

        # ── Low-Pass Metric Smoothing (EMA Filter) ────────────────────
        if face_metrics.get("face_detected", False):
            smooth_keys = [
                "head_pitch_deg", "head_yaw_deg", "head_roll_deg",
                "shoulder_tilt_deg", "estimated_distance_cm"
            ]
            import math
            for k in smooth_keys:
                raw_val = result.get(k)
                if raw_val is not None and not math.isnan(raw_val):
                    if k not in self._ema_state or math.isnan(self._ema_state[k]):
                        self._ema_state[k] = float(raw_val)
                    else:
                        smoothed = self.ema_alpha * float(raw_val) + (1.0 - self.ema_alpha) * self._ema_state[k]
                        self._ema_state[k] = float(smoothed)
                        result[k] = float(smoothed)
        else:
            self._ema_state.clear()

        # ── Wellness Detectors ──────────────────────────────────────────
        ear = face_metrics.get("mean_eye_open_ratio")

        # 1. Blink (improved adaptive detector)
        result.update(self.blink_detector.update(
            eye_open_ratio=ear,
            timestamp=ts
        ))

        # 2. Squint
        result.update(self.squint_detector.update(
            eye_open_ratio=ear,
            timestamp=ts
        ))

        # 3. Gaze fixation
        gaze_x = face_metrics.get("mean_gaze_x")
        gaze_y = face_metrics.get("mean_gaze_y")
        if gaze_x is not None and gaze_y is not None:
            result.update(self.gaze_fixation_detector.update(
                gaze_x=gaze_x,
                gaze_y=gaze_y,
                timestamp=ts
            ))

        # 4. Forward lean (turtle-neck, with smart SAFE distance check)
        fw = face_metrics.get("face_width_norm")
        result.update(self.forward_lean_detector.update(
            face_width_norm=fw,
            timestamp=ts,
            estimated_distance_cm=result.get("estimated_distance_cm")
        ))

        # 5. Brightness / screen glare strain (uses raw BGR frame, no face bbox needed)
        brightness_info = analyze_brightness(frame_bgr)
        result.update(brightness_info)

        return result

    def close(self):
        """Release MediaPipe resources."""
        try:
            self.face_landmarker.close()
        except Exception:
            pass
        try:
            self.pose_landmarker.close()
        except Exception:
            pass
