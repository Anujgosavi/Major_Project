"""
Gemini AI Ergonomic Insights Generator.
Uses Google Gemini API (gemini-2.5-pro or gemini-2.0-flash) to generate personalized clinical ergonomic analysis,
risk assessment, and posture coaching recommendations from frame telemetry.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

DEFAULT_GEMINI_KEY = None


class GeminiInsightsGenerator:
    """
    Interfaces with Gemini LLM to generate AI ergonomic insights.
    """
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or DEFAULT_GEMINI_KEY
        self.model = model
        if HAS_GEMINI:
            genai.configure(api_key=self.api_key)

    def generate_insights(self, summary_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Send summary statistics to Gemini and retrieve structured markdown sections.
        """
        if not HAS_GEMINI:
            return self._fallback_insights(summary_data)

        # Build informative prompt
        prompt = f"""
You are a Senior Physical Therapist & Ergonomics Expert analyzing a user's laptop monitoring telemetry session.

### Session Telemetry Summary:
- Total Session Duration: {summary_data.get('duration_min', 0):.2f} minutes ({summary_data.get('total_frames', 0)} frames)
- Overall Posture Score: {summary_data.get('posture_score', 0):.1f}% / 100%
- Time in SAFE Status: {summary_data.get('safe_pct', 0):.1f}%
- Time in WARNING Status: {summary_data.get('warning_pct', 0):.1f}%
- Time in NON-SAFE Status: {summary_data.get('non_safe_pct', 0):.1f}%

### Key Ergonomic Metrics:
- Distance (Screen to Face): Mean = {summary_data.get('avg_distance', 0):.1f} cm (Target: 45-75 cm)
- Head Pitch (Vertical Tilt): Mean = {summary_data.get('avg_pitch', 0):.1f}° (Target: ±15°)
- Head Yaw (Horizontal Turn): Mean = {summary_data.get('avg_yaw', 0):.1f}° (Target: ±15°)
- Head Roll (Neck Tilt): Mean = {summary_data.get('avg_head_roll', 0):.1f}° (Target: ±15°)
- Shoulder Tilt: Mean = {summary_data.get('avg_shoulder_tilt', 0):.1f}° (Target: <10°)
- Average Blink Rate: {summary_data.get('avg_blink_rate', 0):.1f} blinks/min (Target: 12-20/min)
- Eye Openness Ratio: Mean = {summary_data.get('avg_eye_openness', 0):.2f} (Target: >0.25)

### Primary Posture & Eye Strain Violations Recorded:
{json.dumps(summary_data.get('reason_counts', {}), indent=2)}

### Wellness Alerts Recorded:
{json.dumps(summary_data.get('wellness_counts', {}), indent=2)}

---

Please provide an EXTREMELY descriptive, comprehensive, and professional Ergonomic & Health Evaluation Report in markdown format. 
You MUST write a lengthy, deeply analytical report (at least 800 words total). Use structured, point-wise explanations, bulleted lists, and clear bold headings to make the report easy to read. 
Avoid long, dense paragraphs. Write like a true clinical expert providing an in-depth, exhaustive diagnosis and action plan. Every section must be highly detailed but formatted with bullet points for maximum readability.

Provide EXACTLY 4 distinct sections with these markdown H2 headings:

## 1. Executive Posture Health Assessment
(Provide an exhaustive evaluation of the overall posture score, risk level, and main takeaways using bullet points)

## 2. Biomechanical & Eye Strain Analysis
(Provide a comprehensive, point-wise analysis detailing distance, neck/spine angles (pitch, yaw, roll), shoulder asymmetry, squinting, eye openness, and blink/eye dryness risks in immense detail)

## 3. Targeted Posture Exercises & Correction Plan
(Provide 4-5 specific, well-described stretching or micro-break exercises tailored precisely to their specific posture flaws and eye strain patterns. Use a numbered list with step-by-step bulleted instructions for each exercise)

## 4. Workstation & Environment Optimization
(Provide highly detailed, practical, point-wise adjustments for laptop height, monitor distance, chair height, room lighting, and glare reduction based on the telemetry)

"""

        try:
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.4,
                    max_output_tokens=4000,
                )
            )
            raw_text = response.text
            return self._parse_sections(raw_text)

        except Exception as e:
            print(f"[!] Error calling Gemini API: {e}. Using fallback generator.")
            return self._fallback_insights(summary_data)

    def _parse_sections(self, text: str) -> Dict[str, str]:
        sections = {
            "executive_summary": "",
            "biomechanical_analysis": "",
            "exercises_coaching": "",
            "workstation_optimization": ""
        }

        # Simple section parser by header
        current_key = "executive_summary"
        lines = text.splitlines()
        buf = []

        for line in lines:
            l_lower = line.lower()
            if "1. executive" in l_lower or "executive posture" in l_lower:
                if buf: sections[current_key] = "\n".join(buf).strip()
                current_key = "executive_summary"
                buf = []
            elif "2. biomechanical" in l_lower or "eye strain analysis" in l_lower:
                if buf: sections[current_key] = "\n".join(buf).strip()
                current_key = "biomechanical_analysis"
                buf = []
            elif "3. targeted" in l_lower or "exercise" in l_lower:
                if buf: sections[current_key] = "\n".join(buf).strip()
                current_key = "exercises_coaching"
                buf = []
            elif "4. workstation" in l_lower or "environment" in l_lower:
                if buf: sections[current_key] = "\n".join(buf).strip()
                current_key = "workstation_optimization"
                buf = []
            else:
                buf.append(line)

        if buf:
            sections[current_key] = "\n".join(buf).strip()

        return sections

    def _fallback_insights(self, summary_data: Dict[str, Any]) -> Dict[str, str]:
        score = summary_data.get("posture_score", 100.0)
        return {
            "executive_summary": f"Your overall posture health score for this monitoring session was {score:.1f}%. Staying seated for extended periods without movement increases fatigue. Regular breaks are strongly recommended.",
            "biomechanical_analysis": f"Screen distance averaged {summary_data.get('avg_distance', 60.0):.1f} cm. Shoulder tilt averaged {summary_data.get('avg_shoulder_tilt', 0.0):.1f} degrees. Keep your shoulders level and eyes aligned with the top third of your laptop screen.",
            "exercises_coaching": "1. **Chin Tucks**: Pull head straight back to realign cervical spine (10 reps).\n2. **Shoulder Rolls**: Roll shoulders backwards 10 times to relieve upper back tension.\n3. **20-20-20 Eye Rest**: Every 20 minutes, look at an object 20 feet away for 20 seconds.",
            "workstation_optimization": "Use a laptop stand to elevate your display to eye level and connect an external keyboard and mouse to keep shoulders relaxed."
        }
