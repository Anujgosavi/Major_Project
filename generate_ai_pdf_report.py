"""
Groq AI & PDF Ergonomic Report Generator CLI.

Reads frame-by-frame telemetry logs (JSONL), aggregates stats, calls Groq LLM API
for AI ergonomic insights, and generates a downloadable PDF report with embedded graphs & tables.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.reports.ai_insights import GeminiInsightsGenerator
from backend.reports.pdf_generator import ErgonomicPDFReportGenerator


def load_telemetry(log_file: Path) -> List[Dict[str, Any]]:
    records = []
    if not log_file.exists():
        print(f"[!] Log file not found: {log_file}")
        return records

    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass
    return records


def compute_summary_stats(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {}

    total_frames = len(records)
    t_start = records[0].get("timestamp", 0)
    t_end = records[-1].get("timestamp", 0)
    duration_sec = max(1.0, t_end - t_start)
    duration_min = duration_sec / 60.0

    statuses = [r.get("final_status", "UNKNOWN") for r in records]
    safe_cnt = statuses.count("SAFE")
    warn_cnt = statuses.count("WARNING")
    ns_cnt = statuses.count("NON-SAFE")

    posture_score = ((safe_cnt + 0.5 * warn_cnt) / total_frames) * 100.0

    def _avg(lst):
        vals = [v for v in lst if v is not None and not (isinstance(v, float) and (v != v))]
        return float(sum(vals) / len(vals)) if vals else 0.0

    distances = [r.get("estimated_distance_cm") for r in records]
    pitches = [r.get("head_pitch_deg") for r in records]
    yaws = [r.get("head_yaw_deg") for r in records]
    shoulder_tilts = [r.get("shoulder_tilt_deg") for r in records]
    blink_rates = [r.get("blink_rate_per_min") for r in records]

    reason_counts = {}
    wellness_counts = {}

    for r in records:
        for reas in r.get("reasons", []):
            if reas == "eye_openness_non_safe":
                reas = "eye_openness_warning"
            elif reas == "sustained_squint_non_safe":
                continue
            reason_counts[reas] = reason_counts.get(reas, 0) + 1

        if r.get("brightness_strain") and r.get("brightness_strain") != "ok":
            b_code = f"brightness_{r['brightness_strain']}"
            wellness_counts[b_code] = wellness_counts.get(b_code, 0) + 1
        if r.get("squint_warning"):
            wellness_counts["squint"] = wellness_counts.get("squint", 0) + 1
        if r.get("gaze_fixation_warning"):
            wellness_counts["gaze_fixation"] = wellness_counts.get("gaze_fixation", 0) + 1
        if r.get("forward_lean_warning"):
            wellness_counts["forward_lean"] = wellness_counts.get("forward_lean", 0) + 1

    return {
        "total_frames":      total_frames,
        "duration_min":      duration_min,
        "posture_score":     posture_score,
        "safe_pct":          (safe_cnt / total_frames) * 100.0,
        "warning_pct":       (warn_cnt / total_frames) * 100.0,
        "non_safe_pct":      (ns_cnt / total_frames) * 100.0,
        "avg_distance":      _avg(distances),
        "avg_pitch":         _avg(pitches),
        "avg_yaw":           _avg(yaws),
        "avg_shoulder_tilt": _avg(shoulder_tilts),
        "avg_blink_rate":    _avg(blink_rates),
        "reason_counts":     reason_counts,
        "wellness_counts":   wellness_counts
    }


def main():
    parser = argparse.ArgumentParser(description="Gemini AI & PDF Ergonomic Report Generator")
    parser.add_argument("--telemetry", type=Path, default=PROJECT_ROOT / "logs" / "latest_telemetry.jsonl",
                        help="Path to telemetry JSONL log file")
    parser.add_argument("--api-key", default=None, help="Gemini API Key (defaults to project key)")
    parser.add_argument("--output-pdf", default="Ergonomic_Report.pdf", help="Output PDF filename")
    args = parser.parse_args()

    print("=" * 65)
    print("  Gemini AI & PDF Ergonomic Report Generator")
    print("=" * 65)

    print(f"[..] Loading frame telemetry from: {args.telemetry}")
    records = load_telemetry(args.telemetry)
    if not records:
        print("[!] Error: No valid telemetry records found. Run backend/app/main.py first.")
        sys.exit(1)

    print(f"[+] Loaded {len(records)} frame records.")
    summary = compute_summary_stats(records)
    print(f"[+] Posture Score: {summary['posture_score']:.1f}% | Duration: {summary['duration_min']:.2f} mins")

    print("[..] Calling Gemini LLM API (gemini-2.5-flash) for Ergonomic Insights...")
    gemini_gen = GeminiInsightsGenerator(api_key=args.api_key)
    ai_insights = gemini_gen.generate_insights(summary)
    print("[+] AI Insights generated successfully.")

    print("[..] Rendering Matplotlib charts & compiling ReportLab PDF...")
    pdf_gen = ErgonomicPDFReportGenerator(output_dir=PROJECT_ROOT)
    pdf_path = pdf_gen.build_pdf(
        summary_data=summary,
        records=records,
        ai_insights=ai_insights,
        filename=args.output_pdf
    )

    print("\n" + "=" * 65)
    print(f"[+] PDF REPORT READY FOR DOWNLOAD:")
    print(f"    Path: {pdf_path}")
    print("=" * 65)


if __name__ == "__main__":
    main()
