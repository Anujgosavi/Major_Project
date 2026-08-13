"""
Temporal Persistence Module.
Maintains state machine over time requiring ~2 seconds persistence for WARNING and ~5 seconds persistence for NON-SAFE.
"""

from typing import Optional, Dict, Any


class TemporalPersistenceEngine:
    def __init__(
        self,
        warning_seconds: float = 2.0,
        non_safe_seconds: float = 5.0,
        safe_recovery_seconds: float = 0.0
    ):
        self.warning_seconds = float(warning_seconds)
        self.non_safe_seconds = float(non_safe_seconds)
        self.safe_recovery_seconds = float(safe_recovery_seconds)

        self.violation_start: Optional[float] = None
        self.safe_start: Optional[float] = None
        self.status = "SAFE"
        self.persisted_duration = 0.0

    def update(self, frame_status: str, timestamp: float) -> str:
        """
        Update temporal state based on current frame status and timestamp (seconds).
        Returns persistent final status: "SAFE", "WARNING", "NON-SAFE", or "UNKNOWN".
        """
        if frame_status == "SAFE":
            if self.violation_start is None:
                self.safe_start = None
                self.status = "SAFE"
                self.persisted_duration = 0.0
                return self.status
            
            if self.safe_start is None:
                self.safe_start = timestamp
            
            if (timestamp - self.safe_start) >= self.safe_recovery_seconds:
                self.violation_start = None
                self.safe_start = None
                self.status = "SAFE"
                self.persisted_duration = 0.0
                return self.status
            # Still in recovery grace period for an active violation
            return self.status
        else:
            self.safe_start = None

        if frame_status == "UNKNOWN":
            return self.status

        # If entering a non-SAFE state for the first time
        if self.violation_start is None:
            self.violation_start = timestamp
            self.status = "SAFE"
            self.persisted_duration = 0.0
            return self.status

        elapsed = timestamp - self.violation_start
        self.persisted_duration = elapsed

        # Check NON-SAFE persistence (>= 5.0 seconds)
        if frame_status == "NON-SAFE" and elapsed >= self.non_safe_seconds:
            self.status = "NON-SAFE"
            return self.status

        # Check WARNING persistence (>= 2.0 seconds)
        if frame_status in ("WARNING", "NON-SAFE") and elapsed >= self.warning_seconds:
            self.status = "WARNING"
            return self.status

        # Persistent status remains SAFE until duration threshold met
        self.status = "SAFE"
        return self.status

    def reset(self):
        """Reset temporal persistence state."""
        self.violation_start = None
        self.safe_start = None
        self.status = "SAFE"
        self.persisted_duration = 0.0
