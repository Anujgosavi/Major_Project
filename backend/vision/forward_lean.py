"""
Head Forward Lean (Turtle-Neck) Detector.

"Screen hypnosis" / turtle-neck posture: the user gradually leans their head
forward toward the screen over time — even while maintaining a roughly level
pitch angle — causing neck compression.

Detection method:
  Face apparent width in normalized image coordinates increases as the user
  approaches the camera. We track this relative to the session's initial
  face-width baseline (first N frames after start).

  lean_ratio = current_face_width / initial_face_width

  If lean_ratio > LEAN_THRESHOLD (face appears >20% bigger than baseline)
  for ONSET_SEC seconds continuously, we classify as forward-lean.

This complements distance detection (which fires on absolute cm thresholds)
by catching gradual drift relative to the session start position — the user
may still be at an "acceptable" absolute distance but 15 cm closer than when
they sat down.
"""

import collections
from typing import Dict, Any, Optional


class ForwardLeanDetector:
    BASELINE_FRAMES  = 60      # first N frames used to establish session baseline
    LEAN_THRESHOLD   = 1.20    # 20% increase in face apparent size = lean
    ONSET_SEC        = 4.0     # must sustain lean this long before warning
    RESOLVE_THRESH   = 1.10    # hysteresis: must reduce to <10% to clear

    def __init__(self):
        self._baseline_samples: list = []
        self._baseline: Optional[float] = None
        self.is_leaning: bool = False
        self._lean_since: Optional[float] = None

    def update(
        self,
        face_width_norm: float,
        timestamp: float,
        estimated_distance_cm: Optional[float] = None
    ) -> Dict[str, Any]:
        import math
        if face_width_norm is None or math.isnan(face_width_norm) or face_width_norm <= 0:
            return self._emit(None)

        # Build baseline from first N good frames seated in SAFE distance zone (45-75 cm)
        if self._baseline is None:
            # If distance is provided, only collect sample when in SAFE distance zone
            valid_dist = True
            if estimated_distance_cm is not None and not math.isnan(estimated_distance_cm):
                valid_dist = (45.0 <= estimated_distance_cm <= 75.0)

            if valid_dist:
                self._baseline_samples.append(face_width_norm)
                if len(self._baseline_samples) >= self.BASELINE_FRAMES:
                    # Use median to resist outliers at session start
                    sorted_s = sorted(self._baseline_samples)
                    self._baseline = sorted_s[len(sorted_s) // 2]
            return self._emit(None)

        lean_ratio = face_width_norm / self._baseline

        if not self.is_leaning:
            if lean_ratio >= self.LEAN_THRESHOLD:
                if self._lean_since is None:
                    self._lean_since = timestamp
                elif (timestamp - self._lean_since) >= self.ONSET_SEC:
                    self.is_leaning = True
            else:
                self._lean_since = None
        else:
            if lean_ratio < self.RESOLVE_THRESH:
                self.is_leaning = False
                self._lean_since = None

        return self._emit(lean_ratio)

    def _emit(self, lean_ratio: Optional[float]) -> Dict[str, Any]:
        return {
            "forward_lean_ratio":   round(lean_ratio, 3) if lean_ratio is not None else None,
            "forward_lean_active":  self.is_leaning,
            "forward_lean_warning": self.is_leaning,
        }
