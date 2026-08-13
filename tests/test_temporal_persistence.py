"""
Automated unit tests for temporal persistence engine (~2s WARNING, ~5s NON-SAFE, recovery to SAFE).
"""

import unittest
from backend.safety.temporal import TemporalPersistenceEngine


class TestTemporalPersistence(unittest.TestCase):
    def test_warning_persistence_2_seconds(self):
        engine = TemporalPersistenceEngine(warning_seconds=2.0, non_safe_seconds=5.0)

        # t = 0.0s: Initial SAFE
        self.assertEqual(engine.update("SAFE", timestamp=0.0), "SAFE")

        # t = 1.0s: Frame becomes WARNING (duration 0.0s) -> Status SAFE
        self.assertEqual(engine.update("WARNING", timestamp=1.0), "SAFE")

        # t = 2.5s: Frame is WARNING (duration 1.5s < 2.0s) -> Status SAFE
        self.assertEqual(engine.update("WARNING", timestamp=2.5), "SAFE")

        # t = 3.1s: Frame is WARNING (duration 2.1s >= 2.0s) -> Status WARNING
        self.assertEqual(engine.update("WARNING", timestamp=3.1), "WARNING")

    def test_non_safe_persistence_5_seconds(self):
        engine = TemporalPersistenceEngine(warning_seconds=2.0, non_safe_seconds=5.0)

        # t = 0.0s: Start NON-SAFE violation
        self.assertEqual(engine.update("NON-SAFE", timestamp=0.0), "SAFE")

        # t = 1.5s: 1.5s elapsed -> SAFE
        self.assertEqual(engine.update("NON-SAFE", timestamp=1.5), "SAFE")

        # t = 2.5s: 2.5s elapsed (>= 2.0s) -> WARNING
        self.assertEqual(engine.update("NON-SAFE", timestamp=2.5), "WARNING")

        # t = 5.2s: 5.2s elapsed (>= 5.0s) -> NON-SAFE
        self.assertEqual(engine.update("NON-SAFE", timestamp=5.2), "NON-SAFE")

    def test_recovery_to_safe_is_instant(self):
        engine = TemporalPersistenceEngine(warning_seconds=2.0, non_safe_seconds=5.0)

        # Force to NON-SAFE state
        engine.update("NON-SAFE", timestamp=0.0)
        engine.update("NON-SAFE", timestamp=6.0)
        self.assertEqual(engine.status, "NON-SAFE")

        # Next frame is SAFE -> Status instantly reverts to SAFE
        self.assertEqual(engine.update("SAFE", timestamp=6.1), "SAFE")
        self.assertEqual(engine.status, "SAFE")

    def test_missing_face_unknown_handling(self):
        engine = TemporalPersistenceEngine(warning_seconds=2.0, non_safe_seconds=5.0)

        # Established WARNING state
        engine.update("WARNING", timestamp=0.0)
        engine.update("WARNING", timestamp=3.0)
        self.assertEqual(engine.status, "WARNING")

        # Frame drops (UNKNOWN) -> Maintains current status
        self.assertEqual(engine.update("UNKNOWN", timestamp=3.5), "WARNING")


if __name__ == "__main__":
    unittest.main()
