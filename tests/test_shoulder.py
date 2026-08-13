"""
Automated unit tests for shoulder alignment / tilt thresholds.
"""

import unittest
from backend.safety.rules import evaluate_frame_safety
from backend.config.loader import DEFAULT_FINAL_POLICY


class TestShoulder(unittest.TestCase):
    def test_shoulder_tilt_thresholds(self):
        test_cases = [
            (2.0, "SAFE", None),
            (12.0, "WARNING", "shoulder_tilt_warning"),
            (22.0, "NON-SAFE", "shoulder_tilt_non_safe"),
            (-11.0, "WARNING", "shoulder_tilt_warning"),
            (-25.0, "NON-SAFE", "shoulder_tilt_non_safe"),
        ]
        for shoulder_tilt_deg, expected_status, expected_violation in test_cases:
            with self.subTest(shoulder_tilt_deg=shoulder_tilt_deg):
                mock_result = {
                    "face_detected": True,
                    "pose_detected": True,
                    "estimated_distance_cm": 60.0,
                    "head_pitch_deg": 0.0,
                    "head_yaw_deg": 0.0,
                    "shoulder_tilt_deg": shoulder_tilt_deg,
                }
                eval_res = evaluate_frame_safety(mock_result, DEFAULT_FINAL_POLICY)
                self.assertEqual(eval_res["frame_status"], expected_status)
                if expected_violation:
                    self.assertIn(expected_violation, eval_res["violations"])


if __name__ == "__main__":
    unittest.main()
