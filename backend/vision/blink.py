"""
Blink Detection Module.

Fixes over v1:
- Adaptive baseline: rolling percentile of eye openness (top 20%) is used as the
  live baseline instead of a static calibration constant. This handles glasses,
  lighting changes, and individuals whose eye shape differs from the calibration.
- Hysteresis: separate close-threshold (40% of baseline) and reopen-threshold (65%),
  wider gap prevents chattering on noisy EAR signals.
- Minimum inter-blink interval (80ms) prevents double-counting a single blink.
- Duration guard: 40ms – 600ms (natural blinks are 100-400ms; wider window catches
  slower blinks in tired users).
- Blink rate (blinks per minute) tracked over a sliding 60-second window.
- eyes_closed flag exported for downstream squint / fatigue use.
"""

import collections
import time
from typing import Dict, Any, Optional, List


class BlinkDetector:
    """
    Adaptive EAR-based blink detector with sliding-window blink rate.
    """

    # Fraction of rolling baseline below which eyes are considered closed
    CLOSE_FRAC   = 0.60   # Less strict threshold to catch faster, shallower blinks
    REOPEN_FRAC  = 0.80   # hysteresis gap prevents double-firing

    MIN_BLINK_MS = 10     # ms  (genuine blink must be at least this long)
    MAX_BLINK_MS = 600    # ms  (longer = deliberate closure, not counted)
    MIN_INTER_MS = 80     # ms  (ignore re-close within this window after a blink)

    BASELINE_HISTORY = 150   # frames used for rolling baseline (≈10s at 15 FPS)
    RATE_WINDOW_SEC  = 60.0  # sliding window for blink rate computation

    def __init__(self, baseline_openness: float = 0.245):
        # Seed the rolling history with the calibration value
        self._ear_history: collections.deque = collections.deque(
            [baseline_openness] * self.BASELINE_HISTORY,
            maxlen=self.BASELINE_HISTORY
        )
        self.blink_count:  int   = 0
        self.eyes_closed:  bool  = False
        self._closure_start: Optional[float] = None
        self._last_blink_ts: Optional[float] = None

        # Sliding window: timestamps of recent blinks for rate computation
        self._blink_times: collections.deque = collections.deque()

    # ------------------------------------------------------------------
    def _rolling_baseline(self) -> float:
        """80th-percentile of recent EAR history — approximates 'open' state."""
        sorted_h = sorted(self._ear_history)
        idx = int(len(sorted_h) * 0.80)
        return sorted_h[idx]

    # ------------------------------------------------------------------
    def update(self, eye_open_ratio: float, timestamp: float) -> Dict[str, Any]:
        """
        Feed current mean EAR and wall-clock timestamp (seconds).
        Returns blink metrics dict.
        """
        if eye_open_ratio is None or eye_open_ratio <= 0:
            return self._emit()

        # Update rolling baseline
        self._ear_history.append(eye_open_ratio)
        baseline = self._rolling_baseline()

        closed_thr  = baseline * self.CLOSE_FRAC
        reopen_thr  = baseline * self.REOPEN_FRAC

        now_ms = timestamp * 1000.0

        if not self.eyes_closed:
            if eye_open_ratio < closed_thr:
                # Check minimum inter-blink interval
                if (self._last_blink_ts is None or
                        now_ms - self._last_blink_ts * 1000.0 >= self.MIN_INTER_MS):
                    self.eyes_closed = True
                    self._closure_start = timestamp
        else:
            if eye_open_ratio > reopen_thr:
                if self._closure_start is not None:
                    duration_ms = (timestamp - self._closure_start) * 1000.0
                    if self.MIN_BLINK_MS <= duration_ms <= self.MAX_BLINK_MS:
                        self.blink_count += 1
                        self._last_blink_ts = timestamp
                        self._blink_times.append(timestamp)
                self.eyes_closed = False
                self._closure_start = None

        # Prune old blink timestamps outside the rate window
        cutoff = timestamp - self.RATE_WINDOW_SEC
        while self._blink_times and self._blink_times[0] < cutoff:
            self._blink_times.popleft()

        return self._emit()

    def _emit(self) -> Dict[str, Any]:
        # Blink rate: scale count in window to per-minute
        n = len(self._blink_times)
        blink_rate_per_min = (n / self.RATE_WINDOW_SEC) * 60.0
        return {
            "blink_count":         self.blink_count,
            "eyes_closed":         self.eyes_closed,
            "blink_rate_per_min":  round(blink_rate_per_min, 1),
            "last_blink_time":     self._last_blink_ts,
        }
