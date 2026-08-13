"""
Unit tests for TelemetryLogger and SessionReporter.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.telemetry.logger import TelemetryLogger
from backend.app.reporter import SessionReporter


class TestTelemetryLogger(unittest.TestCase):
    """Tests for TelemetryLogger JSONL output."""

    def test_log_frame_writes_jsonl(self):
        """Verify that log_frame writes valid JSONL and records correct fields."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            logger = TelemetryLogger(logs_dir=Path(tmp_dir))

            result = {
                "face_detected": True,
                "pose_detected": True,
                "estimated_distance_cm": 55.0,
                "head_pitch_deg": -3.0,
                "head_yaw_deg": 2.5,
                "head_roll_deg": 1.0,
                "shoulder_tilt_deg": 5.0,
                "mean_eye_open_ratio": 0.35,
                "blink_count": 10,
                "blink_rate_per_min": 14.0,
                "gaze_x": 0.5,
                "gaze_y": 0.5,
                "brightness_mean": 120.0,
            }
            decision = {
                "final_status": "SAFE",
                "frame_status": "SAFE",
                "reasons": [],
            }

            logger.log_frame(result, decision)
            logger.log_frame(result, decision)
            logger.close()

            # Verify file was created
            log_file = logger.log_file
            self.assertTrue(os.path.exists(log_file))

            # Verify content is valid JSONL
            with open(log_file, "r") as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 2)

            record = json.loads(lines[0])
            self.assertEqual(record["frame_index"], 1)
            self.assertEqual(record["final_status"], "SAFE")
            self.assertEqual(record["estimated_distance_cm"], 55.0)
            self.assertEqual(record["head_pitch_deg"], -3.0)
            self.assertEqual(record["blink_count"], 10)
            self.assertIn("timestamp", record)

    def test_log_frame_with_missing_face(self):
        """Verify that frames without face detection still log correctly."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            logger = TelemetryLogger(logs_dir=Path(tmp_dir))

            result = {
                "face_detected": False,
                "pose_detected": False,
            }
            decision = {
                "final_status": "UNKNOWN",
                "frame_status": "UNKNOWN",
                "reasons": ["face_or_pose_not_detected"],
            }

            logger.log_frame(result, decision)
            logger.close()

            with open(logger.log_file, "r") as f:
                record = json.loads(f.readline())

            self.assertFalse(record["face_detected"])
            self.assertEqual(record["final_status"], "UNKNOWN")
            self.assertIn("face_or_pose_not_detected", record["reasons"])

    def test_latest_symlink_created(self):
        """Verify that latest_telemetry.jsonl copy is created on close."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            logger = TelemetryLogger(logs_dir=Path(tmp_dir))
            result = {"face_detected": True}
            decision = {"final_status": "SAFE", "frame_status": "SAFE", "reasons": []}
            logger.log_frame(result, decision)
            logger.close()

            latest_path = os.path.join(tmp_dir, "latest_telemetry.jsonl")
            self.assertTrue(os.path.exists(latest_path))


class TestSessionReporter(unittest.TestCase):
    """Tests for SessionReporter output."""

    def test_reporter_generates_report(self):
        """Verify SessionReporter computes posture score and generates summary."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            reporter = SessionReporter(output_dir=Path(tmp_dir))

            # Simulate 100 frames: 80 SAFE, 10 WARNING, 10 NON-SAFE
            for i in range(80):
                result = {"face_detected": True, "estimated_distance_cm": 55.0}
                decision = {"final_status": "SAFE", "reasons": []}
                reporter.update(result, decision)

            for i in range(10):
                result = {"face_detected": True, "estimated_distance_cm": 42.0}
                decision = {"final_status": "WARNING", "reasons": ["screen_distance_low"]}
                reporter.update(result, decision)

            for i in range(10):
                result = {"face_detected": True, "estimated_distance_cm": 35.0}
                decision = {"final_status": "NON-SAFE", "reasons": ["screen_too_close"]}
                reporter.update(result, decision)

            report = reporter.generate_report(filename="test_summary.txt")
            self.assertIn("POSTURE SCORE", report)
            self.assertIn("SAFE", report)
            self.assertIn("WARNING", report)
            self.assertIn("NON-SAFE", report)

            # Verify file was saved
            out_file = Path(tmp_dir) / "test_summary.txt"
            self.assertTrue(out_file.exists())

    def test_reporter_empty_session(self):
        """Verify SessionReporter handles empty session gracefully."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            reporter = SessionReporter(output_dir=Path(tmp_dir))
            report = reporter.generate_report()
            self.assertEqual(report, "No frames processed during session.")


if __name__ == "__main__":
    unittest.main()
