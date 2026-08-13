"""
Combined Safety Engine Module.
Integrates single-frame rule evaluation with temporal persistence engine.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from backend.config.loader import load_final_policy
from backend.safety.rules import evaluate_frame_safety
from backend.safety.temporal import TemporalPersistenceEngine


class SafetyEngine:
    def __init__(
        self,
        config_dir: Optional[Path] = None,
        reference_profile: Optional[Dict[str, Any]] = None
    ):
        self.policy = load_final_policy(config_dir)
        self.reference_profile = reference_profile or {}

        temporal_cfg = self.policy.get("temporal", {})
        warning_sec = temporal_cfg.get("warning_seconds", 2.0)
        non_safe_sec = temporal_cfg.get("non_safe_seconds", 5.0)
        recovery_sec = temporal_cfg.get("safe_recovery_seconds", 0.5)

        self.temporal_engine = TemporalPersistenceEngine(
            warning_seconds=warning_sec,
            non_safe_seconds=non_safe_sec,
            safe_recovery_seconds=recovery_sec
        )

    def evaluate(self, frame_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate frame result dictionary and return complete safety decision object.
        """
        ts = frame_result.get("timestamp", 0.0)

        # Single frame evaluation
        frame_eval = evaluate_frame_safety(
            frame_result,
            self.policy,
            reference_profile=self.reference_profile
        )

        frame_status = frame_eval["frame_status"]
        reasons = frame_eval["violations"]

        # Temporal state update
        final_status = self.temporal_engine.update(frame_status, timestamp=ts)

        return {
            "timestamp": ts,
            "frame_status": frame_status,
            "final_status": final_status,
            "persisted_duration": self.temporal_engine.persisted_duration,
            "reasons": reasons
        }

    def reset(self):
        """Reset temporal state."""
        self.temporal_engine.reset()
