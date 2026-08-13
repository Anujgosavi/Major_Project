"""
Telemetry Logger Module.
Records frame-by-frame ergonomic measurements, safety statuses, and wellness alerts to structured JSONL logs.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"


class TelemetryLogger:
    """
    Frame-by-frame telemetry recorder for logging continuous monitoring data.
    """
    def __init__(self, logs_dir: Optional[Path] = None, filename: Optional[str] = None):
        self.logs_dir = logs_dir or DEFAULT_LOGS_DIR
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        if not filename:
            timestr = time.strftime("%Y%m%d_%H%M%S")
            filename = f"telemetry_{timestr}.jsonl"

        self.log_file = self.logs_dir / filename
        self.latest_log_file = self.logs_dir / "latest_telemetry.jsonl"

        self._f = open(self.log_file, "a", encoding="utf-8")
        self.frame_count = 0

    def log_frame(self, result: Dict[str, Any], decision: Dict[str, Any]):
        """
        Record a single frame's vision results and safety decision to JSONL log.
        """
        self.frame_count += 1

        record = {
            "frame_index":             self.frame_count,
            "timestamp":               result.get("timestamp", time.time()),
            "face_detected":           result.get("face_detected", False),
            "pose_detected":           result.get("pose_detected", False),
            "estimated_distance_cm":   result.get("estimated_distance_cm"),
            "head_pitch_deg":          result.get("head_pitch_deg"),
            "head_yaw_deg":            result.get("head_yaw_deg"),
            "head_roll_deg":           result.get("head_roll_deg"),
            "shoulder_tilt_deg":       result.get("shoulder_tilt_deg"),
            "mean_eye_open_ratio":     result.get("mean_eye_open_ratio"),
            "blink_count":             result.get("blink_count", 0),
            "blink_rate_per_min":      result.get("blink_rate_per_min", 0.0),
            "squint_warning":          result.get("squint_warning", False),
            "gaze_fixation_warning":   result.get("gaze_fixation_warning", False),
            "forward_lean_warning":    result.get("forward_lean_warning", False),
            "brightness_strain":       result.get("brightness_strain", "ok"),
            "frame_status":            decision.get("frame_status", "UNKNOWN"),
            "final_status":            decision.get("final_status", "UNKNOWN"),
            "persisted_duration":     decision.get("persisted_duration", 0.0),
            "reasons":                 decision.get("reasons", [])
        }

        line = json.dumps(record) + "\n"
        self._f.write(line)
        self._f.flush()

    def close(self):
        """Close log file and update latest_telemetry.jsonl symlink/copy."""
        if hasattr(self, "_f") and self._f and not self._f.closed:
            self._f.close()

        # Update latest_telemetry.jsonl
        try:
            if self.log_file.exists():
                import shutil
                shutil.copyfile(self.log_file, self.latest_log_file)
        except Exception:
            pass
