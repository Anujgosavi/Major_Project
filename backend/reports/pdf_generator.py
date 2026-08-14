"""
Ergonomic PDF Report Generator Module.
Generates publication-quality PDF ergonomic reports with embedded Matplotlib data visualizations,
summary metric tables, and Groq AI personalized insights using ReportLab.
"""

import os
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

import matplotlib
matplotlib.use("Agg")  # Non-GUI backend for PDF chart rendering
import matplotlib.pyplot as plt
import numpy as np

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas for adding running header and 'Page X of Y' footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#666666"))

        # Footer line
        self.setLineWidth(0.5)
        self.setStrokeColor(colors.HexColor("#CCCCCC"))
        self.line(54, 36, 558, 36)

        # Footer text
        self.drawString(54, 22, "AI Ergonomics & Digital-Wellness Monitoring System — Confidential Report")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 22, page_str)
        self.restoreState()


class ErgonomicPDFReportGenerator:
    """
    Compiles session telemetry data and Groq AI insights into a PDF document.
    """
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(__file__).resolve().parent.parent.parent
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_charts(self, records: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Render Matplotlib visualizations and save to temp image files.
        """
        temp_dir = tempfile.mkdtemp()
        chart_paths = {}

        if not records:
            return chart_paths

        times = [r.get("timestamp", i) - records[0].get("timestamp", 0) for i, r in enumerate(records)]
        distances = [r.get("estimated_distance_cm") for r in records]
        pitches = [r.get("head_pitch_deg") for r in records]
        yaws = [r.get("head_yaw_deg") for r in records]
        shoulder_tilts = [r.get("shoulder_tilt_deg") for r in records]
        statuses = [r.get("final_status", "UNKNOWN") for r in records]

        # Filter None values for plotting
        valid_dist_t = [t for t, d in zip(times, distances) if d is not None and not np.isnan(d)]
        valid_dist = [d for d in distances if d is not None and not np.isnan(d)]

        valid_pitch_t = [t for t, p in zip(times, pitches) if p is not None and not np.isnan(p)]
        valid_pitch = [p for p in pitches if p is not None and not np.isnan(p)]

        valid_tilt_t = [t for t, st in zip(times, shoulder_tilts) if st is not None and not np.isnan(st)]
        valid_tilt = [st for st in shoulder_tilts if st is not None and not np.isnan(st)]

        # --- Chart 1: Distance & Head Angles Time-Series ---
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.5, 4.0), sharex=True, dpi=200)
        fig.patch.set_facecolor("#FFFFFF")

        ax1.plot(valid_dist_t, valid_dist, color="#1f77b4", linewidth=1.5, label="Screen Distance (cm)")
        ax1.axhspan(45, 75, color="#2ca02c", alpha=0.15, label="Ideal Distance (45-75 cm)")
        ax1.axhline(40, color="#ff7f0e", linestyle="--", alpha=0.7)
        ax1.axhline(85, color="#ff7f0e", linestyle="--", alpha=0.7)
        ax1.set_ylabel("Distance (cm)", fontsize=9, fontweight="bold")
        ax1.grid(True, linestyle=":", alpha=0.5)
        ax1.legend(loc="upper right", fontsize=7)
        ax1.set_title("Screen Distance & Head Pose Dynamics Over Time", fontsize=11, fontweight="bold", pad=8)

        ax2.plot(valid_pitch_t, valid_pitch, color="#d62728", linewidth=1.2, label="Head Pitch (°)")
        ax2.plot(valid_pitch_t, [y for y in yaws if y is not None and not np.isnan(y)], color="#9467bd", linewidth=1.2, label="Head Yaw (°)")
        ax2.axhspan(-15, 15, color="#2ca02c", alpha=0.15, label="Safe Range (±15°)")
        ax2.set_xlabel("Elapsed Session Time (seconds)", fontsize=9, fontweight="bold")
        ax2.set_ylabel("Angle (°)", fontsize=9, fontweight="bold")
        ax2.grid(True, linestyle=":", alpha=0.5)
        ax2.legend(loc="upper right", fontsize=7)

        plt.tight_layout()
        chart1_path = os.path.join(temp_dir, "chart_distance_head.png")
        plt.savefig(chart1_path, bbox_inches="tight")
        plt.close(fig)
        chart_paths["distance_head"] = chart1_path

        # --- Chart 2: Shoulder Tilt Time-Series ---
        fig, ax = plt.subplots(figsize=(7.5, 2.5), dpi=200)
        ax.plot(valid_tilt_t, valid_tilt, color="#ff7f0e", linewidth=1.5, label="Shoulder Tilt (°)")
        ax.axhspan(-10, 10, color="#2ca02c", alpha=0.15, label="Safe Range (<10°)")
        ax.axhline(20, color="#d62728", linestyle="--", linewidth=1, label="Non-Safe Threshold (20°)")
        ax.axhline(-20, color="#d62728", linestyle="--", linewidth=1)
        ax.set_title("Shoulder Tilt & Symmetry Over Time", fontsize=11, fontweight="bold", pad=8)
        ax.set_xlabel("Elapsed Session Time (seconds)", fontsize=9, fontweight="bold")
        ax.set_ylabel("Tilt Angle (°)", fontsize=9, fontweight="bold")
        ax.grid(True, linestyle=":", alpha=0.5)
        ax.legend(loc="upper right", fontsize=7)

        plt.tight_layout()
        chart2_path = os.path.join(temp_dir, "chart_shoulder_tilt.png")
        plt.savefig(chart2_path, bbox_inches="tight")
        plt.close(fig)
        chart_paths["shoulder_tilt"] = chart2_path

        # --- Chart 3: Eye Openness & Blink Rate ---
        eye_openness = [r.get("mean_eye_open_ratio") for r in records]
        blink_rates = [r.get("blink_rate_per_min") for r in records]
        
        valid_eye_t = [t for t, eo in zip(times, eye_openness) if eo is not None and not np.isnan(eo)]
        valid_eye = [eo for eo in eye_openness if eo is not None and not np.isnan(eo)]
        
        valid_blink_t = [t for t, br in zip(times, blink_rates) if br is not None and not np.isnan(br)]
        valid_blink = [br for br in blink_rates if br is not None and not np.isnan(br)]

        fig, ax1 = plt.subplots(figsize=(7.5, 2.5), dpi=200)
        
        ax1.plot(valid_eye_t, valid_eye, color="#17becf", linewidth=1.5, label="Eye Openness Ratio")
        ax1.axhline(0.25, color="#ff7f0e", linestyle="--", linewidth=1, label="Squinting (<0.25)")
        ax1.axhline(0.15, color="#d62728", linestyle="--", linewidth=1, label="Critically Low (<0.15)")
        ax1.set_xlabel("Elapsed Session Time (seconds)", fontsize=9, fontweight="bold")
        ax1.set_ylabel("Openness Ratio", fontsize=9, fontweight="bold")
        ax1.tick_params(axis='y', labelcolor="#17becf")
        ax1.grid(True, linestyle=":", alpha=0.5)
        
        # Secondary y-axis for Blink Rate
        ax2_blink = ax1.twinx()
        ax2_blink.plot(valid_blink_t, valid_blink, color="#8c564b", linewidth=1.2, linestyle="-.", label="Blink Rate (/min)")
        ax2_blink.set_ylabel("Blink Rate (/min)", fontsize=9, fontweight="bold")
        ax2_blink.tick_params(axis='y', labelcolor="#8c564b")
        
        # Combine legends
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2_blink.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper right", fontsize=7)
        
        plt.title("Eye Strain Dynamics: Openness & Blinking", fontsize=11, fontweight="bold", pad=8)
        
        plt.tight_layout()
        chart3_path = os.path.join(temp_dir, "chart_eye_openness.png")
        plt.savefig(chart3_path, bbox_inches="tight")
        plt.close(fig)
        chart_paths["eye_openness"] = chart3_path

        # --- Chart 3: Posture Status Donut & Violation Bar Chart ---
        fig, (ax_pie, ax_bar) = plt.subplots(1, 2, figsize=(7.5, 2.8), dpi=200)
        
        # Donut Chart
        safe_c = statuses.count("SAFE")
        warn_c = statuses.count("WARNING")
        ns_c = statuses.count("NON-SAFE")
        unk_c = statuses.count("UNKNOWN")
        
        counts = [safe_c, warn_c, ns_c]
        labels = ["SAFE", "WARNING", "NON-SAFE"]
        colors_pie = ["#2ca02c", "#ff7f0e", "#d62728"]
        
        if sum(counts) > 0:
            wedges, texts, autotexts = ax_pie.pie(
                counts, labels=labels, colors=colors_pie, autopct="%1.1f%%",
                startangle=90, pctdistance=0.75, wedgeprops=dict(width=0.4, edgecolor="w")
            )
            for t in texts: t.set_fontsize(8)
            for at in autotexts: at.set_fontsize(8); at.set_fontweight("bold")
            ax_pie.set_title("Posture Status Distribution", fontsize=10, fontweight="bold")
        else:
            ax_pie.text(0.5, 0.5, "No Status Data", ha="center", va="center")

        # Violation Reasons Bar Chart
        reason_counts = {}
        for r in records:
            for reas in r.get("reasons", []):
                reason_counts[reas] = reason_counts.get(reas, 0) + 1

        if reason_counts:
            r_sorted = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            r_names = [x[0].replace("_", " ").title() for x in r_sorted]
            r_vals = [x[1] for x in r_sorted]
            
            y_pos = np.arange(len(r_names))
            ax_bar.barh(y_pos, r_vals, color="#1f77b4", alpha=0.85)
            ax_bar.set_yticks(y_pos)
            ax_bar.set_yticklabels(r_names, fontsize=7.5)
            ax_bar.invert_yaxis()
            ax_bar.set_xlabel("Frame Hits", fontsize=8, fontweight="bold")
            ax_bar.set_title("Top Posture Violations", fontsize=10, fontweight="bold")
            ax_bar.grid(True, linestyle=":", alpha=0.4)
        else:
            ax_bar.text(0.5, 0.5, "Zero Posture Violations", ha="center", va="center", fontsize=9, color="#2ca02c")

        plt.tight_layout()
        chart3_path = os.path.join(temp_dir, "chart_distribution.png")
        plt.savefig(chart3_path, bbox_inches="tight")
        plt.close(fig)
        chart_paths["distribution"] = chart3_path

        return chart_paths

    def _parse_markdown_text(self, text: str, body_style, bullet_style) -> List:
        """Parses LLM markdown into ReportLab Paragraphs, handling bullets and newlines."""
        flowables = []
        if not text:
            return flowables

        # ReportLab supports simple HTML like <b> for bold
        # Replace **bold** with <b>bold</b>
        import re
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            if line.startswith("-") or line.startswith("*"):
                # Clean up the bullet marker
                clean_line = line.lstrip("-* ").strip()
                flowables.append(Paragraph(f"• {clean_line}", bullet_style))
            elif line[0].isdigit() and len(line) > 1 and (line[1] == "." or line[1] == ")"):
                # Clean numbered lists
                clean_line = line.split(maxsplit=1)[-1].strip() if " " in line else line
                flowables.append(Paragraph(f"{line.split()[0]} {clean_line}", bullet_style))
            elif line.startswith("#"):
                # Subheaders (H3, H4) inside the text
                clean_line = line.lstrip("# ").strip()
                flowables.append(Spacer(1, 6))
                flowables.append(Paragraph(f"<b>{clean_line}</b>", body_style))
            else:
                flowables.append(Paragraph(line, body_style))
                
        return flowables

    def build_pdf(
        self,
        summary_data: Dict[str, Any],
        records: List[Dict[str, Any]],
        ai_insights: Dict[str, str],
        filename: str = "Ergonomic_Report.pdf"
    ) -> Path:
        """
        Compile full PDF report.
        """
        pdf_path = self.output_dir / filename
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=40,
            bottomMargin=50
        )

        styles = getSampleStyleSheet()

        # Custom Styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1A365D"),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#4A5568"),
            spaceAfter=15
        )
        h2_style = ParagraphStyle(
            "Heading2Custom",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#2B6CB0"),
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=True
        )
        body_style = ParagraphStyle(
            "BodyCustom",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#2D3748"),
            spaceAfter=8
        )
        bullet_style = ParagraphStyle(
            "BulletCustom",
            parent=body_style,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=4
        )

        story = []

        # Header Title Banner
        story.append(Paragraph("AI Ergonomic & Digital-Wellness Health Report", title_style))
        story.append(Paragraph("Continuous Front-Camera Laptop Posture & Biomechanical Evaluation", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2B6CB0"), spaceAfter=15))

        # Metadata & Posture Score Card Table
        score = summary_data.get("posture_score", 100.0)
        score_color = colors.HexColor("#2F855A") if score >= 80 else (colors.HexColor("#DD6B20") if score >= 60 else colors.HexColor("#C53030"))
        score_badge = f"<font size='18' color='{score_color.hexval()}'><b>{score:.1f}%</b></font>"

        meta_data = [
            [
                Paragraph(f"<b>Session Date:</b> {time.strftime('%Y-%m-%d %H:%M')}", body_style),
                Paragraph(f"<b>Monitoring Duration:</b> {summary_data.get('duration_min', 0):.1f} mins", body_style),
                Paragraph(f"<b>POSTURE HEALTH SCORE:</b><br/>{score_badge}", body_style)
            ],
            [
                Paragraph(f"<b>Total Frames Analyzed:</b> {summary_data.get('total_frames', 0)}", body_style),
                Paragraph(f"<b>Average Blink Rate:</b> {summary_data.get('avg_blink_rate', 0):.1f} /min", body_style),
                Paragraph(f"<b>Status:</b> SAFE ({summary_data.get('safe_pct', 0):.0f}%) | WARN ({summary_data.get('warning_pct', 0):.0f}%) | NON-SAFE ({summary_data.get('non_safe_pct', 0):.0f}%)", body_style)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[170, 170, 164])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 14))

        # Render Charts
        charts = self._generate_charts(records)

        # 1. Executive Summary & Biomechanical Analysis
        story.append(Paragraph("1. Executive Ergonomic Summary & Assessment", h2_style))
        story.extend(self._parse_markdown_text(ai_insights.get("executive_summary", ""), body_style, bullet_style))

        if "distribution" in charts:
            story.append(Spacer(1, 6))
            story.append(Image(charts["distribution"], width=500, height=186))
            story.append(Spacer(1, 10))

        story.append(Paragraph("2. Biomechanical & Pose Dynamics Analysis", h2_style))
        story.extend(self._parse_markdown_text(ai_insights.get("biomechanical_analysis", ""), body_style, bullet_style))

        # Embedded Time-Series Charts
        if "distance_head" in charts:
            story.append(Spacer(1, 6))
            story.append(Image(charts["distance_head"], width=500, height=266))
            story.append(Spacer(1, 8))

        if "shoulder_tilt" in charts:
            story.append(Image(charts["shoulder_tilt"], width=500, height=166))
            story.append(Spacer(1, 12))

        if "eye_openness" in charts:
            story.append(Image(charts["eye_openness"], width=500, height=166))
            story.append(Spacer(1, 12))

        # Page 2 / Recommendations Section
        story.append(Paragraph("3. Targeted Posture Exercises & Physical Coaching", h2_style))
        story.extend(self._parse_markdown_text(ai_insights.get("exercises_coaching", ""), body_style, bullet_style))

        story.append(Spacer(1, 8))
        story.append(Paragraph("4. Workstation & Environment Optimization Guidelines", h2_style))
        story.extend(self._parse_markdown_text(ai_insights.get("workstation_optimization", ""), body_style, bullet_style))

        # Hardcoded 20-20-20 Rule Callout
        story.append(Spacer(1, 15))
        story.append(Paragraph("Eye Wellness: The 20-20-20 Rule", h2_style))
        story.append(Paragraph(
            "<b>To prevent digital eye strain, follow this universally recommended ergonomic practice:</b><br/>"
            "Every 20 minutes of screen time, take a visual break by looking at an object at least 20 feet away for a minimum of 20 seconds.",
            body_style
        ))

        # Build PDF using NumberedCanvas
        doc.build(story, canvasmaker=NumberedCanvas)
        print(f"\n[+] PDF Ergonomic Report generated successfully at: {pdf_path}")
        return pdf_path
