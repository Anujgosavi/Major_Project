"""
Session Health & Posture Summary Reporter.

Tracks session statistics across monitoring frames and generates a comprehensive
Ergonomic Health & Posture Score summary report upon shutdown.
"""

import time
import math
from pathlib import Path
from typing import Dict, Any, Optional, List


class SessionReporter:
    """
    Accumulates real-time monitoring data and exports a session posture summary report.
    """
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(__file__).resolve().parent.parent.parent
        self.start_time = time.time()
        self.total_frames = 0
        
        self.status_counts = {"SAFE": 0, "WARNING": 0, "NON-SAFE": 0, "UNKNOWN": 0}
        self.reason_counts: Dict[str, int] = {}
        self.wellness_counts: Dict[str, int] = {}

        self.distances: List[float] = []
        self.pitches: List[float] = []
        self.yaws: List[float] = []
        self.shoulder_tilts: List[float] = []
        self.blink_rates: List[float] = []

    def update(self, result: Dict[str, Any], decision: Dict[str, Any]):
        """
        Record frame results and safety decisions.
        """
        self.total_frames += 1

        # Track status
        status = decision.get("final_status", "UNKNOWN")
        self.status_counts[status] = self.status_counts.get(status, 0) + 1

        # Track reasons
        for r in decision.get("reasons", []):
            self.reason_counts[r] = self.reason_counts.get(r, 0) + 1

        # Track wellness alerts
        if result.get("brightness_warning"):
            w_code = f"brightness_{result.get('brightness_strain')}"
            self.wellness_counts[w_code] = self.wellness_counts.get(w_code, 0) + 1
        if result.get("squint_warning"):
            self.wellness_counts["squint"] = self.wellness_counts.get("squint", 0) + 1
        if result.get("gaze_fixation_warning"):
            self.wellness_counts["gaze_fixation"] = self.wellness_counts.get("gaze_fixation", 0) + 1
        if result.get("forward_lean_warning"):
            self.wellness_counts["forward_lean"] = self.wellness_counts.get("forward_lean", 0) + 1
        
        blk_rate = result.get("blink_rate_per_min", 0)
        if blk_rate > 0:
            self.blink_rates.append(blk_rate)
            if blk_rate < 12.0:
                self.wellness_counts["low_blink_rate"] = self.wellness_counts.get("low_blink_rate", 0) + 1

        # Track numeric metrics
        if result.get("face_detected"):
            d = result.get("estimated_distance_cm")
            if d and not math.isnan(d): self.distances.append(d)
            p = result.get("head_pitch_deg")
            if p and not math.isnan(p): self.pitches.append(p)
            y = result.get("head_yaw_deg")
            if y and not math.isnan(y): self.yaws.append(y)

        if result.get("pose_detected"):
            st = result.get("shoulder_tilt_deg")
            if st and not math.isnan(st): self.shoulder_tilts.append(st)

    def generate_report(self, filename: str = "session_summary.txt") -> str:
        """
        Generate and save session summary report.
        """
        elapsed_sec = time.time() - self.start_time
        if self.total_frames == 0:
            return "No frames processed during session."

        safe_cnt = self.status_counts.get("SAFE", 0)
        warn_cnt = self.status_counts.get("WARNING", 0)
        non_safe_cnt = self.status_counts.get("NON-SAFE", 0)

        # Posture Health Score formula
        posture_score = ((safe_cnt + 0.5 * warn_cnt) / self.total_frames) * 100.0

        lines = []
        lines.append("=" * 65)
        lines.append("       SESSION ERGONOMIC HEALTH & POSTURE SUMMARY REPORT")
        lines.append("=" * 65)
        fps = self.total_frames / elapsed_sec if elapsed_sec > 0 else 0.0
        lines.append(f"Total Session Duration: {elapsed_sec / 60.0:.2f} minutes ({elapsed_sec:.1f}s)")
        lines.append(f"Total Frames Processed: {self.total_frames} frames ({fps:.1f} FPS)")
        lines.append("")
        lines.append(f"--- OVERALL POSTURE SCORE: {posture_score:.1f}% / 100% ---")
        lines.append("")
        lines.append("--- STATUS TIME DISTRIBUTION ---")
        lines.append(f"  [SAFE]     {safe_cnt:5d} frames ({safe_cnt / self.total_frames * 100:5.1f}%)")
        lines.append(f"  [WARNING]  {warn_cnt:5d} frames ({warn_cnt / self.total_frames * 100:5.1f}%)")
        lines.append(f"  [NON-SAFE] {non_safe_cnt:5d} frames ({non_safe_cnt / self.total_frames * 100:5.1f}%)")
        lines.append("")

        if self.reason_counts:
            lines.append("--- TOP POSTURE VIOLATIONS ---")
            for r, cnt in sorted(self.reason_counts.items(), key=lambda x: x[1], reverse=True):
                pct = (cnt / self.total_frames) * 100.0
                lines.append(f"  - {r:<30}: {cnt:5d} hits ({pct:5.1f}%)")
            lines.append("")

        if self.wellness_counts:
            lines.append("--- WELLNESS & EYE STRAIN ALERTS ---")
            for w, cnt in sorted(self.wellness_counts.items(), key=lambda x: x[1], reverse=True):
                pct = (cnt / self.total_frames) * 100.0
                lines.append(f"  - {w:<30}: {cnt:5d} hits ({pct:5.1f}%)")
            lines.append("")

        lines.append("--- AVERAGE MEASUREMENTS ---")
        def _avg(lst): return sum(lst) / len(lst) if lst else float("nan")
        lines.append(f"  - Screen Distance:   {_avg(self.distances):.1f} cm")
        lines.append(f"  - Head Pitch:         {_avg(self.pitches):.1f} deg")
        lines.append(f"  - Head Yaw:           {_avg(self.yaws):.1f} deg")
        lines.append(f"  - Shoulder Tilt:      {_avg(self.shoulder_tilts):.1f} deg")
        lines.append(f"  - Average Blink Rate: {_avg(self.blink_rates):.1f} blinks/min")
        lines.append("=" * 65)

        report_str = "\n".join(lines)

        # Save to output file
        try:
            out_file = self.output_dir / filename
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(report_str)
            print(f"\n[+] Session summary report saved to {out_file}")
        except Exception as e:
            print(f"[!] Could not save report file: {e}")

        return report_str
