"""
Unit Tests for New Features & Improvements.

Tests EMA metric smoothing, smart forward lean distance gating,
PostureNotifier notification cooldown, and SessionReporter posture score output.
"""

import math
import tempfile
import unittest
from pathlib import Path

from backend.vision.pipeline import FrontCameraPipeline
from backend.vision.forward_lean import ForwardLeanDetector
from backend.app.notifier import PostureNotifier
from backend.app.reporter import SessionReporter


class TestNewFeatures(unittest.TestCase):
    def test_forward_lean_smart_distance_gating(self):
        detector = ForwardLeanDetector()
        
        # 1. Samples with distance outside 45-75 cm should NOT build baseline
        detector.update(face_width_norm=0.30, timestamp=1.0, estimated_distance_cm=35.0)  # Too close
        detector.update(face_width_norm=0.30, timestamp=2.0, estimated_distance_cm=80.0)  # Too far
        self.assertIsNone(detector._baseline)
        self.assertEqual(len(detector._baseline_samples), 0)

        # 2. Samples within 45-75 cm SHOULD be accepted
        for i in range(65):
            detector.update(face_width_norm=0.25, timestamp=3.0 + i * 0.1, estimated_distance_cm=60.0)

        self.assertIsNotNone(detector._baseline)
        self.assertAlmostEqual(detector._baseline, 0.25, places=4)

    def test_posture_notifier_cooldown(self):
        notifier = PostureNotifier(cooldown_sec=30.0, enabled=True)

        # First trigger at t=0
        notifier.notify_non_safe(duration_sec=12.0, reasons=["shoulder_tilt_non_safe"], timestamp=100.0)
        self.assertEqual(notifier._last_notif_time, 100.0)

        # Second trigger at t=15s (should be throttled by 30s cooldown)
        notifier.notify_non_safe(duration_sec=27.0, reasons=["shoulder_tilt_non_safe"], timestamp=115.0)
        self.assertEqual(notifier._last_notif_time, 100.0)  # Unchanged

        # Third trigger at t=35s (past 30s cooldown -> should fire)
        notifier.notify_non_safe(duration_sec=47.0, reasons=["shoulder_tilt_non_safe"], timestamp=135.0)
        self.assertEqual(notifier._last_notif_time, 135.0)

    def test_session_reporter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            reporter = SessionReporter(output_dir=Path(tmpdir))

            # Simulate 10 frames: 8 SAFE, 2 NON-SAFE
            for i in range(8):
                res = {"face_detected": True, "pose_detected": True, "estimated_distance_cm": 60.0,
                       "head_pitch_deg": 0.0, "head_yaw_deg": 0.0, "shoulder_tilt_deg": 0.0, "blink_rate_per_min": 15.0}
                dec = {"final_status": "SAFE", "reasons": []}
                reporter.update(res, dec)

            for i in range(2):
                res = {"face_detected": True, "pose_detected": True, "estimated_distance_cm": 38.0,
                       "head_pitch_deg": 0.0, "head_yaw_deg": 0.0, "shoulder_tilt_deg": 25.0, "blink_rate_per_min": 10.0}
                dec = {"final_status": "NON-SAFE", "reasons": ["shoulder_tilt_non_safe", "screen_too_close"]}
                reporter.update(res, dec)

            report_str = reporter.generate_report(filename="test_summary.txt")

            self.assertIn("OVERALL POSTURE SCORE: 80.0%", report_str)
            self.assertIn("shoulder_tilt_non_safe", report_str)
            # Verify file was written
            summary_file = Path(tmpdir) / "test_summary.txt"
            self.assertTrue(summary_file.exists())

    def test_eye_openness_thresholds(self):
        from backend.safety.rules import evaluate_frame_safety
        from backend.config.loader import DEFAULT_FINAL_POLICY
        
        mock_policy = dict(DEFAULT_FINAL_POLICY)
        mock_policy["eye_openness"] = {"enabled": True, "warning_ratio": 0.25, "non_safe_ratio": 0.15}

        # Test SAFE (> 0.25)
        res_safe = evaluate_frame_safety({
            "face_detected": True, "pose_detected": True, "mean_eye_open_ratio": 0.35
        }, mock_policy)
        self.assertEqual(res_safe["frame_status"], "SAFE")

        # Test WARNING (<= 0.25, > 0.15)
        res_warn = evaluate_frame_safety({
            "face_detected": True, "pose_detected": True, "mean_eye_open_ratio": 0.20
        }, mock_policy)
        self.assertEqual(res_warn["frame_status"], "WARNING")
        self.assertIn("eye_openness_warning", res_warn["violations"])

        # Test NON-SAFE (<= 0.15)
        res_ns = evaluate_frame_safety({
            "face_detected": True, "pose_detected": True, "mean_eye_open_ratio": 0.10
        }, mock_policy)
        self.assertEqual(res_ns["frame_status"], "NON-SAFE")
        self.assertIn("eye_openness_non_safe", res_ns["violations"])


if __name__ == "__main__":
    unittest.main()
