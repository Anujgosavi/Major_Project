"""
Automated unit tests for config & calibration loading modules.
"""

import unittest
from backend.config.loader import load_final_policy, load_safety_config
from backend.calibration.manager import CalibrationManager


class TestConfigLoader(unittest.TestCase):
    def test_load_final_policy_schema(self):
        policy = load_final_policy()
        self.assertIn("distance", policy)
        self.assertIn("head_pitch", policy)
        self.assertIn("head_yaw", policy)
        self.assertIn("shoulder_tilt", policy)
        self.assertIn("temporal", policy)

        self.assertEqual(policy["distance"]["non_safe_min_cm"], 40.0)
        self.assertEqual(policy["head_pitch"]["warning_deg"], 15.0)
        self.assertEqual(policy["head_yaw"]["non_safe_deg"], 30.0)
        self.assertEqual(policy["shoulder_tilt"]["warning_deg"], 10.0)
        self.assertEqual(policy["temporal"]["warning_seconds"], 2.0)
        self.assertEqual(policy["temporal"]["non_safe_seconds"], 5.0)

    def test_calibration_manager_defaults(self):
        mgr = CalibrationManager()
        a, b = mgr.get_inverse_distance_params()
        self.assertEqual(a, 15.244)
        self.assertEqual(b, -0.0543)
        self.assertIsNotNone(mgr.reference_profile)


if __name__ == "__main__":
    unittest.main()
