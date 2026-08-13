"""
Automated unit tests for distance estimation and distance safety threshold classification.
"""

import math
import unittest
from backend.vision.distance import estimate_distance_cm
from backend.safety.rules import evaluate_frame_safety
from backend.config.loader import DEFAULT_FINAL_POLICY


class TestDistance(unittest.TestCase):
    def test_estimate_distance_cm_inverse(self):
        a = 15.244
        b = -0.0543

        # Normal face width ~0.285 norm
        dist = estimate_distance_cm(0.285, a=a, b=b)
        self.assertFalse(math.isnan(dist))
        self.assertTrue(40.0 < dist < 80.0)

        # Invalid / NaN input
        self.assertTrue(math.isnan(estimate_distance_cm(0.0, a=a, b=b)))
        self.assertTrue(math.isnan(estimate_distance_cm(None, a=a, b=b)))

    def test_distance_safety_rules(self):
        test_cases = [
            (35.0, "NON-SAFE", "screen_too_close"),
            (42.0, "WARNING", "screen_distance_low"),
            (60.0, "SAFE", None),
            (80.0, "WARNING", "screen_distance_high"),
            (90.0, "NON-SAFE", "screen_too_far"),
        ]
        for dist_cm, expected_status, expected_violation in test_cases:
            with self.subTest(dist_cm=dist_cm):
                mock_result = {
                    "face_detected": True,
                    "pose_detected": True,
                    "estimated_distance_cm": dist_cm,
                    "head_pitch_deg": 0.0,
                    "head_yaw_deg": 0.0,
                    "shoulder_tilt_deg": 0.0,
                }
                eval_res = evaluate_frame_safety(mock_result, DEFAULT_FINAL_POLICY)
                self.assertEqual(eval_res["frame_status"], expected_status)
                if expected_violation:
                    self.assertIn(expected_violation, eval_res["violations"])
                else:
                    self.assertEqual(len(eval_res["violations"]), 0)


if __name__ == "__main__":
    unittest.main()
