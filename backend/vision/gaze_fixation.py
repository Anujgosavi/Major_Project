"""
Gaze Fixation Detector.

Screen fixation (staring at one spot for a long time without eye movement)
is associated with reduced blink rate, eye dryness, and visual fatigue.

Detection logic:
  - A rolling buffer of the last HISTORY frames of (gaze_x, gaze_y) is maintained.
  - Gaze displacement = std-dev of recent positions (both axes combined).
  - If displacement < FIXATION_THRESHOLD for FIXATION_ONSET_SEC seconds,
    a fixation event is active.
  - A rolling 60-second fixation fraction is tracked.
  - If fixation_fraction >= 0.40 (fixated >24s of 60s), warn = True.

Note: Gaze proxy coordinates from MediaPipe iris landmarks are relative to
the eye bounding box (0.0–1.0). Typical saccade amplitude in the proxy
space is 0.05–0.15. Below 0.03 std-dev → essentially motionless.
"""

import collections
import math
from typing import Dict, Any, Optional, Deque, Tuple


class GazeFixationDetector:
    HISTORY            = 30      # frames of gaze history (~2s at 15 FPS)
    FIXATION_THRESHOLD = 0.03    # std-dev below this = fixated
    FIXATION_ONSET_SEC = 5.0     # must be still this long before reporting
    WARN_FRACTION      = 0.40    # warn if fixating >40% of 60s window
    RATE_WINDOW_SEC    = 60.0

    def __init__(self):
        self._gaze_buf: Deque[Tuple[float, float]] = collections.deque(maxlen=self.HISTORY)
        self.is_fixated: bool = False
        self._still_since: Optional[float] = None
        self._intervals: collections.deque = collections.deque()
        self._current_start: Optional[float] = None

    def update(
        self,
        gaze_x: float,
        gaze_y: float,
        timestamp: float
    ) -> Dict[str, Any]:
        if gaze_x is None or math.isnan(gaze_x) or gaze_y is None or math.isnan(gaze_y):
            return self._emit(timestamp)

        self._gaze_buf.append((gaze_x, gaze_y))

        if len(self._gaze_buf) < self.HISTORY // 2:
            return self._emit(timestamp)

        xs = [p[0] for p in self._gaze_buf]
        ys = [p[1] for p in self._gaze_buf]
        std_x = float(_std(xs))
        std_y = float(_std(ys))
        dispersion = math.sqrt(std_x**2 + std_y**2)

        if not self.is_fixated:
            if dispersion < self.FIXATION_THRESHOLD:
                if self._still_since is None:
                    self._still_since = timestamp
                elif (timestamp - self._still_since) >= self.FIXATION_ONSET_SEC:
                    self.is_fixated = True
                    self._current_start = self._still_since
            else:
                self._still_since = None
        else:
            if dispersion >= self.FIXATION_THRESHOLD * 1.5:  # hysteresis
                if self._current_start is not None:
                    self._intervals.append((self._current_start, timestamp))
                self.is_fixated = False
                self._current_start = None
                self._still_since = None

        return self._emit(timestamp)

    def _emit(self, timestamp: float) -> Dict[str, Any]:
        cutoff = timestamp - self.RATE_WINDOW_SEC
        while self._intervals and self._intervals[0][1] < cutoff:
            self._intervals.popleft()

        total = 0.0
        for start, end in self._intervals:
            total += max(0.0, end - max(start, cutoff))
        if self.is_fixated and self._current_start is not None:
            total += max(0.0, timestamp - max(self._current_start, cutoff))

        fraction = total / self.RATE_WINDOW_SEC
        return {
            "gaze_fixated":          self.is_fixated,
            "gaze_fixation_frac_60s": round(fraction, 3),
            "gaze_fixation_warning": fraction >= self.WARN_FRACTION,
        }


def _std(values):
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    return math.sqrt(sum((v - mean) ** 2 for v in values) / n)
