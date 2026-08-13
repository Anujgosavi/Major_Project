"""
Automated unit tests for head pitch and head yaw safety thresholds.
"""

import unittest
from backend.safety.rules import evaluate_frame_safety
from backend.config.loader import DEFAULT_FINAL_POLICY


class TestPitchYaw(unittest.TestCase):
    def test_head_pitch_thresholds(self):
        test_cases = [
            (5.0, "SAFE", None),
            (16.0, "WARNING", "head_pitch_warning"),
            (32.0, "NON-SAFE", "head_pitch_non_safe"),
            (-18.0, "WARNING", "head_pitch_warning"),
            (-35.0, "NON-SAFE", "head_pitch_non_safe"),
        ]
        for pitch_deg, expected_status, expected_violation in test_cases:
            with self.subTest(pitch_deg=pitch_deg):
                mock_result = {
                    "face_detected": True,
                    "pose_detected": True,
                    "estimated_distance_cm": 60.0,
                    "head_pitch_deg": pitch_deg,
                    "head_yaw_deg": 0.0,
                    "shoulder_tilt_deg": 0.0,
                }
                eval_res = evaluate_frame_safety(mock_result, DEFAULT_FINAL_POLICY)
                self.assertEqual(eval_res["frame_status"], expected_status)
                if expected_violation:
                    self.assertIn(expected_violation, eval_res["violations"])

    def test_head_yaw_thresholds(self):
        test_cases = [
            (5.0, "SAFE", None),
            (18.0, "WARNING", "head_yaw_warning"),
            (35.0, "NON-SAFE", "head_yaw_non_safe"),
            (-16.0, "WARNING", "head_yaw_warning"),
            (-32.0, "NON-SAFE", "head_yaw_non_safe"),
        ]
        for yaw_deg, expected_status, expected_violation in test_cases:
            with self.subTest(yaw_deg=yaw_deg):
                mock_result = {
                    "face_detected": True,
                    "pose_detected": True,
                    "estimated_distance_cm": 60.0,
                    "head_pitch_deg": 0.0,
                    "head_yaw_deg": yaw_deg,
                    "shoulder_tilt_deg": 0.0,
                }
                eval_res = evaluate_frame_safety(mock_result, DEFAULT_FINAL_POLICY)
                self.assertEqual(eval_res["frame_status"], expected_status)
                if expected_violation:
                    self.assertIn(expected_violation, eval_res["violations"])

    def test_head_roll_thresholds(self):
        # We need to temporarily force head_roll enabled in our mock policy
        # because DEFAULT_FINAL_POLICY might have it disabled if we didn't reload it correctly,
        # but since we already updated the JSON, it should be enabled.
        test_cases = [
            (5.0, "SAFE", None),
            (16.0, "WARNING", "head_roll_warning"),
            (32.0, "NON-SAFE", "head_roll_non_safe"),
            (-18.0, "WARNING", "head_roll_warning"),
            (-35.0, "NON-SAFE", "head_roll_non_safe"),
        ]
        
        # Override policy for test safety in case of cache issues
        mock_policy = dict(DEFAULT_FINAL_POLICY)
        mock_policy["head_roll"] = {"enabled": True, "warning_deg": 15.0, "non_safe_deg": 30.0}

        for roll_deg, expected_status, expected_violation in test_cases:
            with self.subTest(roll_deg=roll_deg):
                mock_result = {
                    "face_detected": True,
                    "pose_detected": True,
                    "estimated_distance_cm": 60.0,
                    "head_pitch_deg": 0.0,
                    "head_yaw_deg": 0.0,
                    "head_roll_deg": roll_deg,
                    "shoulder_tilt_deg": 0.0,
                }
                eval_res = evaluate_frame_safety(mock_result, mock_policy)
                self.assertEqual(eval_res["frame_status"], expected_status)
                if expected_violation:
                    self.assertIn(expected_violation, eval_res["violations"])


if __name__ == "__main__":
    unittest.main()
