"""
Telemetry Logger Module.
Records frame-by-frame ergonomic measurements, safety statuses, and wellness alerts to structured JSONL logs.
"""

import json
import math
import time
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"


class TelemetryLogger:
    """
    Frame-by-frame local recorder with compact, one-second MongoDB rollups.

    The local JSONL file remains frame-level so PDF reports retain their
    resolution. MongoDB receives one aggregate document per second instead of
    one document per camera frame.
    """
    def __init__(
        self,
        logs_dir: Optional[Path] = None,
        filename: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        self.logs_dir = logs_dir or DEFAULT_LOGS_DIR
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = session_id
        self.user_id = user_id

        if not filename:
            timestr = time.strftime("%Y%m%d_%H%M%S")
            filename = f"telemetry_{timestr}.jsonl"

        self.log_file = self.logs_dir / filename
        self.latest_log_file = self.logs_dir / "latest_telemetry.jsonl"

        self._f = open(self.log_file, "a", encoding="utf-8")
        self.frame_count = 0
        self._last_flush_time = time.monotonic()
        self._mongo_bucket = None
        self._mongo_futures: list[Future] = []
        self._mongo_executor = (
            ThreadPoolExecutor(max_workers=1, thread_name_prefix="telemetry-sync")
            if self.session_id else None
        )

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
        now = time.monotonic()
        if now - self._last_flush_time >= 1.0:
            self._f.flush()
            self._last_flush_time = now

        if self.session_id:
            self._add_to_mongo_bucket(record)

    @staticmethod
    def _finite_number(value: Any) -> Optional[float]:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        return number if math.isfinite(number) else None

    def _add_to_mongo_bucket(self, record: Dict[str, Any]) -> None:
        """Accumulate a frame into a one-second aggregate and flush old buckets."""
        bucket_start = int(record["timestamp"])
        if self._mongo_bucket is None:
            self._mongo_bucket = self._new_bucket(bucket_start, record)
        elif bucket_start != self._mongo_bucket["bucket_start"]:
            self._queue_bucket(self._mongo_bucket)
            self._mongo_bucket = self._new_bucket(bucket_start, record)
        else:
            self._update_bucket(self._mongo_bucket, record)

    @staticmethod
    def _new_bucket(bucket_start: int, record: Dict[str, Any]) -> Dict[str, Any]:
        bucket = {
            "bucket_start": bucket_start,
            "timestamp": bucket_start,
            "frame_index": record["frame_index"],
            "sample_count": 0,
            "status_counts": {},
            "reason_counts": {},
            "_sums": {},
            "_counts": {},
        }
        TelemetryLogger._update_bucket(bucket, record)
        return bucket

    @staticmethod
    def _update_bucket(bucket: Dict[str, Any], record: Dict[str, Any]) -> None:
        bucket["sample_count"] += 1
        status = record.get("final_status", "UNKNOWN")
        status_counts = bucket["status_counts"]
        status_counts[status] = status_counts.get(status, 0) + 1
        for reason in record.get("reasons", []):
            reason_counts = bucket["reason_counts"]
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

        for field in (
            "estimated_distance_cm",
            "head_pitch_deg",
            "head_yaw_deg",
            "head_roll_deg",
            "shoulder_tilt_deg",
            "mean_eye_open_ratio",
            "blink_rate_per_min",
        ):
            value = TelemetryLogger._finite_number(record.get(field))
            if value is not None:
                bucket["_sums"][field] = bucket["_sums"].get(field, 0.0) + value
                bucket["_counts"][field] = bucket["_counts"].get(field, 0) + 1

    def _queue_bucket(self, bucket: Dict[str, Any]) -> None:
        if not self._mongo_executor:
            return
        document = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "bucket_start": bucket["bucket_start"],
            "timestamp": bucket["timestamp"],
            "frame_index": bucket["frame_index"],
            "sample_count": bucket["sample_count"],
            "status_counts": bucket["status_counts"],
            "reason_counts": bucket["reason_counts"],
        }
        for field, total in bucket["_sums"].items():
            document[field] = total / bucket["_counts"][field]
        dominant_status = max(
            bucket["status_counts"],
            key=bucket["status_counts"].get,
            default="UNKNOWN",
        )
        document["final_status"] = dominant_status
        self._mongo_futures.append(
            self._mongo_executor.submit(self._insert_bucket, document)
        )

    @staticmethod
    def _insert_bucket(document: Dict[str, Any]) -> None:
        from backend.db.mongo import telemetry_col
        telemetry_col().insert_one(document)

    def close(self):
        """Close log file, update latest_telemetry.jsonl, and sync records to MongoDB."""
        if hasattr(self, "_f") and self._f and not self._f.closed:
            self._f.flush()
            self._f.close()

        # Update latest_telemetry.jsonl
        try:
            if self.log_file.exists():
                import shutil
                shutil.copyfile(self.log_file, self.latest_log_file)
        except Exception:
            pass

        if self._mongo_bucket:
            self._queue_bucket(self._mongo_bucket)
            self._mongo_bucket = None

        if self._mongo_executor:
            for future in self._mongo_futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"[!] Warning: Failed to sync telemetry bucket to MongoDB: {e}")
            self._mongo_executor.shutdown(wait=True)
            print(f"[+] Synced {len(self._mongo_futures)} one-second telemetry buckets to MongoDB.")
            self._mongo_futures.clear()
