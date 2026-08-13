"""
Squint Detector.

Sustained squinting (partial eye closure without a full blink) is a reliable
visual strain indicator — people squint to reduce glare, improve focus, or
compensate for eye fatigue.

Detection logic:
  A "squint event" is active when:
    - Eye openness is between 30% and 70% of the rolling EAR baseline
      (not a full blink — those drop below 40%)
    - This partial closure persists for at least SQUINT_ONSET_SEC seconds

  Squint resolves when eye openness returns above 75% of baseline.

A rolling 60-second squint duty cycle is computed:
  squint_fraction = total_squint_seconds_in_window / window_size
  If squint_fraction >= 0.25 (squinting >15s out of 60s), warn = True.
"""

import time
import collections
from typing import Dict, Any, Optional


class SquintDetector:
    # EAR thresholds as fraction of rolling baseline
    SQUINT_LOW_FRAC    = 0.30   # below this = full blink (handled by BlinkDetector)
    SQUINT_HIGH_FRAC   = 0.70   # above this = eyes sufficiently open
    RESOLVE_FRAC       = 0.75   # hysteresis: must reopen to this to clear squint

    SQUINT_ONSET_SEC   = 0.8    # must sustain partial closure this long to count
    WARN_FRACTION      = 0.20   # warn if squinting >20% of the rolling window

    BASELINE_HISTORY   = 150    # frames (~10s at 15 FPS)
    RATE_WINDOW_SEC    = 60.0

    def __init__(self, baseline_openness: float = 0.245):
        self._ear_history: collections.deque = collections.deque(
            [baseline_openness] * self.BASELINE_HISTORY,
            maxlen=self.BASELINE_HISTORY
        )
        self.is_squinting: bool = False
        self._onset_ts: Optional[float] = None

        # Sliding window: (start, end) pairs of squint intervals in last 60s
        self._intervals: collections.deque = collections.deque()
        self._current_start: Optional[float] = None

    def _baseline(self) -> float:
        sorted_h = sorted(self._ear_history)
        return sorted_h[int(len(sorted_h) * 0.80)]

    def update(self, eye_open_ratio: float, timestamp: float) -> Dict[str, Any]:
        if eye_open_ratio is None or eye_open_ratio <= 0:
            return self._emit(timestamp)

        self._ear_history.append(eye_open_ratio)
        bl = self._baseline()

        low  = bl * self.SQUINT_LOW_FRAC
        high = bl * self.SQUINT_HIGH_FRAC
        res  = bl * self.RESOLVE_FRAC

        in_squint_zone = low < eye_open_ratio < high

        if not self.is_squinting:
            if in_squint_zone:
                if self._onset_ts is None:
                    self._onset_ts = timestamp
                elif (timestamp - self._onset_ts) >= self.SQUINT_ONSET_SEC:
                    self.is_squinting = True
                    self._current_start = self._onset_ts
            else:
                self._onset_ts = None
        else:
            if eye_open_ratio >= res:
                # Squint ended — record interval
                if self._current_start is not None:
                    self._intervals.append((self._current_start, timestamp))
                self.is_squinting = False
                self._current_start = None
                self._onset_ts = None

        return self._emit(timestamp)

    def _emit(self, timestamp: float) -> Dict[str, Any]:
        cutoff = timestamp - self.RATE_WINDOW_SEC

        # Prune old intervals
        while self._intervals and self._intervals[0][1] < cutoff:
            self._intervals.popleft()

        # Total squint seconds in window (clamp start to cutoff)
        total_squint = 0.0
        for start, end in self._intervals:
            s = max(start, cutoff)
            total_squint += max(0.0, end - s)

        # Add ongoing squint duration
        if self.is_squinting and self._current_start is not None:
            s = max(self._current_start, cutoff)
            total_squint += max(0.0, timestamp - s)

        squint_fraction = total_squint / self.RATE_WINDOW_SEC
        squint_warning  = squint_fraction >= self.WARN_FRACTION

        return {
            "is_squinting":        self.is_squinting,
            "squint_fraction_60s": round(squint_fraction, 3),
            "squint_warning":      squint_warning,
        }
