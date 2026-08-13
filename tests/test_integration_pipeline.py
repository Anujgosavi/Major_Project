"""
Automated integration test feeding a synthetic frame image through FrontCameraPipeline and SafetyEngine.
"""

import unittest
import numpy as np
from backend.vision.pipeline import FrontCameraPipeline
from backend.safety.engine import SafetyEngine
from backend.app.annotator import annotate_frame


class TestIntegrationPipeline(unittest.TestCase):
    def test_integration_pipeline_synthetic_frame(self):
        # Create synthetic 480x640 BGR image
        synthetic_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        synthetic_frame[100:380, 200:440] = 200

        # Initialize Pipeline & Safety Engine
        pipeline = FrontCameraPipeline()
        safety_engine = SafetyEngine(reference_profile=pipeline.reference)

        # Process Frame
        result = pipeline.process_frame(synthetic_frame, timestamp=1.0)
        self.assertIn("timestamp", result)
        self.assertIn("face_detected", result)
        self.assertIn("pose_detected", result)

        # Evaluate Safety
        decision = safety_engine.evaluate(result)
        self.assertIn("frame_status", decision)
        self.assertIn("final_status", decision)
        self.assertIn("reasons", decision)

        # Annotate Frame
        annotated = annotate_frame(synthetic_frame, result, decision)
        self.assertEqual(annotated.shape, synthetic_frame.shape)

        pipeline.close()


if __name__ == "__main__":
    unittest.main()
