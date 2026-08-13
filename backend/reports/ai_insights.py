"""
Gemini AI Ergonomic Insights Generator.

Generates a structured, telemetry-grounded ergonomic report for the
front-camera laptop monitoring system.

Important:
- This is an ergonomic/wellness interpretation layer.
- It must NOT present itself as a medical diagnosis.
- It must not infer medical conditions that are not directly supported
  by telemetry.
"""

import json
import math
import re
from typing import Dict, Any, Optional


import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


DEFAULT_GEMINI_KEY = os.environ.get("GEMINI_API_KEY")


class GeminiInsightsGenerator:
    """
    Generates personalized ergonomic insights from session telemetry.
    """

    SECTION_KEYS = {
        "executive":
            "executive_summary",

        "biomechanical":
            "biomechanical_analysis",

        "exercise":
            "exercises_coaching",

        "workstation":
            "workstation_optimization",
    }


    REQUIRED_SECTIONS = [
        "executive_summary",
        "biomechanical_analysis",
        "exercises_coaching",
        "workstation_optimization",
    ]


    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash"
    ):

        self.api_key = (
            api_key or
            DEFAULT_GEMINI_KEY
        )

        self.model = model

        if HAS_GEMINI:

            if not self.api_key:

                raise ValueError(
                    "Gemini API key was not provided."
                )

            genai.configure(
                api_key=self.api_key
            )


    # =========================================================
    # PUBLIC API
    # =========================================================

    def generate_insights(
        self,
        summary_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate a structured four-section ergonomic report.

        Returns:
            {
                "executive_summary": str,
                "biomechanical_analysis": str,
                "exercises_coaching": str,
                "workstation_optimization": str
            }
        """

        cleaned = (
            self._clean_summary_data(
                summary_data
            )
        )

        if not HAS_GEMINI:

            return self._fallback_insights(
                cleaned
            )

        if not self.api_key:

            return self._fallback_insights(
                cleaned
            )

        prompt = self._build_prompt(
            cleaned
        )

        try:

            model = genai.GenerativeModel(
                self.model
            )

            response = model.generate_content(
                prompt,
                generation_config=(
                    genai.GenerationConfig(
                        temperature=0.25,
                        max_output_tokens=5000
                    )
                )
            )

            raw_text = (
                getattr(
                    response,
                    "text",
                    ""
                )
                or ""
            )

            parsed = self._parse_sections(
                raw_text
            )

            if self._is_valid_report(
                parsed
            ):

                return parsed

            print(
                "[!] Gemini response did not contain "
                "all required sections. Using fallback."
            )

            return self._fallback_insights(
                cleaned
            )

        except Exception as e:

            print(
                f"[!] Gemini generation failed: "
                f"{e}. Using fallback."
            )

            return self._fallback_insights(
                cleaned
            )


    # =========================================================
    # DATA CLEANING
    # =========================================================

    def _safe_float(
        self,
        value,
        default: float = 0.0
    ) -> float:

        try:

            result = float(value)

            if not math.isfinite(result):

                return default

            return result

        except (
            TypeError,
            ValueError
        ):

            return default


    def _safe_pct(
        self,
        value
    ) -> float:

        return max(
            0.0,
            min(
                100.0,
                self._safe_float(
                    value
                )
            )
        )


    def _clean_summary_data(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:

        cleaned = dict(
            data or {}
        )

        numeric_fields = [

            "duration_min",
            "total_frames",

            "posture_score",

            "safe_pct",
            "warning_pct",
            "non_safe_pct",

            "avg_distance",
            "avg_pitch",
            "avg_yaw",
            "avg_head_roll",
            "avg_shoulder_tilt",

            "avg_blink_rate",
            "avg_eye_openness",

            "min_distance",
            "max_distance",

            "max_abs_pitch",
            "max_abs_yaw",
            "max_abs_shoulder_tilt",

            "warning_events",
            "non_safe_events",
        ]

        for field in numeric_fields:

            if field in cleaned:

                cleaned[field] = (
                    self._safe_float(
                        cleaned[field]
                    )
                )


        # Percentages
        for field in [
            "safe_pct",
            "warning_pct",
            "non_safe_pct",
        ]:

            cleaned[field] = (
                self._safe_pct(
                    cleaned.get(
                        field,
                        0
                    )
                )
            )


        # Reason counts
        if not isinstance(
            cleaned.get(
                "reason_counts"
            ),
            dict
        ):

            cleaned[
                "reason_counts"
            ] = {}


        # Wellness counts
        if not isinstance(
            cleaned.get(
                "wellness_counts"
            ),
            dict
        ):

            cleaned[
                "wellness_counts"
            ] = {}


        # Optional validated thresholds
        if not isinstance(
            cleaned.get(
                "policy"
            ),
            dict
        ):

            cleaned[
                "policy"
            ] = {}


        return cleaned


    # =========================================================
    # PROMPT
    # =========================================================

    def _build_prompt(
        self,
        summary: Dict[str, Any]
    ) -> str:

        reason_counts = json.dumps(
            summary.get(
                "reason_counts",
                {}
            ),
            indent=2
        )

        wellness_counts = json.dumps(
            summary.get(
                "wellness_counts",
                {}
            ),
            indent=2
        )

        policy = json.dumps(
            summary.get(
                "policy",
                {}
            ),
            indent=2
        )

        prompt = f"""
You are an AI ergonomic wellness analysis assistant.

You are NOT a physician, physiotherapist, or clinical diagnostician.
You must NOT diagnose a disease, injury, disorder, or medical condition.

Your job is to interpret ONLY the provided laptop-monitoring telemetry
and produce an evidence-based ergonomic wellness report.

Do not invent observations that are not present in the telemetry.

------------------------------------------------------------
SESSION SUMMARY
------------------------------------------------------------

Duration:
{summary.get('duration_min', 0):.2f} minutes

Frames analyzed:
{summary.get('total_frames', 0):.0f}

Overall posture score:
{summary.get('posture_score', 0):.1f}%

Time in SAFE:
{summary.get('safe_pct', 0):.1f}%

Time in WARNING:
{summary.get('warning_pct', 0):.1f}%

Time in NON-SAFE:
{summary.get('non_safe_pct', 0):.1f}%

Warning events:
{summary.get('warning_events', 0):.0f}

Non-safe events:
{summary.get('non_safe_events', 0):.0f}


------------------------------------------------------------
PRIMARY ERGONOMIC TELEMETRY
------------------------------------------------------------

Average screen distance:
{summary.get('avg_distance', 0):.1f} cm

Observed minimum distance:
{summary.get('min_distance', 0):.1f} cm

Observed maximum distance:
{summary.get('max_distance', 0):.1f} cm


Average head pitch:
{summary.get('avg_pitch', 0):.1f}°

Maximum absolute pitch deviation:
{summary.get('max_abs_pitch', 0):.1f}°


Average head yaw:
{summary.get('avg_yaw', 0):.1f}°

Maximum absolute yaw deviation:
{summary.get('max_abs_yaw', 0):.1f}°


Average head roll:
{summary.get('avg_head_roll', 0):.1f}°


Average shoulder tilt:
{summary.get('avg_shoulder_tilt', 0):.1f}°

Maximum absolute shoulder tilt:
{summary.get('max_abs_shoulder_tilt', 0):.1f}°


------------------------------------------------------------
EYE / VISUAL TELEMETRY
------------------------------------------------------------

Average blink rate:
{summary.get('avg_blink_rate', 0):.1f} blinks/min

Average eye openness ratio:
{summary.get('avg_eye_openness', 0):.3f}


IMPORTANT:
Eye openness and blink rate are observational telemetry only.

Do NOT state that the user has dry eye, eye disease, vision problems,
or another medical condition based solely on these measurements.

You may say that the observed pattern MAY be associated with reduced
visual comfort or prolonged screen exposure, but clearly label this
as a possible wellness consideration rather than a diagnosis.


------------------------------------------------------------
RECORDED POSTURE REASONS
------------------------------------------------------------

{reason_counts}


------------------------------------------------------------
RECORDED WELLNESS EVENTS
------------------------------------------------------------

{wellness_counts}


------------------------------------------------------------
VALIDATED PROJECT POLICY
------------------------------------------------------------

{policy}


------------------------------------------------------------
ANALYSIS REQUIREMENTS
------------------------------------------------------------

Your report must:

1. Prioritize the most persistent and significant deviations.
2. Distinguish between:
   - directly observed telemetry,
   - reasonable ergonomic interpretation,
   - recommendations.
3. Do not overreact to isolated single-frame deviations.
4. Consider persistence and session duration.
5. Mention good behavior as well as problems.
6. Avoid generic advice when telemetry supports more specific advice.
7. Keep recommendations practical for laptop users.
8. Explain WHY each recommendation follows from the measured data.
9. Do not claim that the system provides medical diagnosis.
10. Do not invent symptoms reported by the user.
11. Do not claim a health condition from posture telemetry alone.
12. Do not use head roll as a primary warning unless the telemetry explicitly
    marks it as a validated safety signal.
13. Do not use gaze or blink as safety violations unless the telemetry
    explicitly indicates that the current project policy enables them.


------------------------------------------------------------
OUTPUT FORMAT
------------------------------------------------------------

Return EXACTLY four sections with these exact headings:

## 1. Executive Posture Health Assessment

## 2. Biomechanical & Eye Strain Analysis

## 3. Targeted Posture Exercises & Correction Plan

## 4. Workstation & Environment Optimization


SECTION 1:
Provide:
- overall assessment
- strongest positive findings
- most important concerns
- persistence/severity interpretation
- practical priority level

SECTION 2:
Analyze separately:
- screen distance
- head pitch
- head yaw
- head roll
- shoulder alignment
- eye openness
- blinking

For each relevant issue:
- state what was measured
- state whether the measurement is within the project's configured range
- explain the ergonomic implication
- distinguish observation from inference

SECTION 3:
Give 4–5 practical micro-break or posture exercises.
You MUST include the "20-20-20 Rule" (every 20 mins, look 20 feet away for 20 seconds) as one of the exercises.

For every exercise include:
- purpose
- step-by-step instructions
- duration/repetitions
- what telemetry issue it is intended to address

Do not prescribe treatment for a medical condition.

SECTION 4:
Give practical workstation changes covering:
- laptop/screen height
- viewing distance
- chair/desk positioning
- keyboard/mouse setup
- lighting
- glare
- break scheduling

Prioritize changes according to the actual telemetry.

Target approximately 1000–1400 words.

Use concise paragraphs and bullets.
Do not add any fifth section.
Do not add an introduction before section 1.
"""

        return prompt


    # =========================================================
    # SECTION PARSER
    # =========================================================

    def _parse_sections(
        self,
        text: str
    ) -> Dict[str, str]:

        sections = {
            key: ""
            for key in self.REQUIRED_SECTIONS
        }

        if not text:

            return sections


        heading_patterns = {

            "executive_summary": re.compile(
                r"^##\s*1\.\s*Executive",
                re.I
            ),

            "biomechanical_analysis": re.compile(
                r"^##\s*2\.\s*Biomechanical",
                re.I
            ),

            "exercises_coaching": re.compile(
                r"^##\s*3\.\s*Targeted",
                re.I
            ),

            "workstation_optimization": re.compile(
                r"^##\s*4\.\s*Workstation",
                re.I
            ),
        }


        current = None
        buffer = []


        def flush():

            nonlocal buffer

            if (
                current is not None
                and
                buffer
            ):

                sections[
                    current
                ] = "\n".join(
                    buffer
                ).strip()

            buffer = []


        for line in text.splitlines():

            matched_key = None

            for key, pattern in (
                heading_patterns.items()
            ):

                if pattern.search(
                    line.strip()
                ):

                    matched_key = key
                    break


            if matched_key is not None:

                flush()

                current = matched_key

            else:

                if current is not None:

                    buffer.append(
                        line
                    )


        flush()

        return sections


    # =========================================================
    # VALIDATION
    # =========================================================

    def _is_valid_report(
        self,
        sections: Dict[str, str]
    ) -> bool:

        if not sections:

            return False


        for key in self.REQUIRED_SECTIONS:

            content = sections.get(
                key,
                ""
            )

            # Require meaningful content.
            if (
                not isinstance(
                    content,
                    str
                )
                or
                len(
                    content.strip()
                ) < 150
            ):

                return False


        total_words = sum(
            len(
                sections[key].split()
            )
            for key in self.REQUIRED_SECTIONS
        )

        return (
            total_words >= 700
        )


    # =========================================================
    # FALLBACK
    # =========================================================

    def _fallback_insights(
        self,
        summary_data: Dict[str, Any]
    ) -> Dict[str, str]:

        score = (
            summary_data.get(
                "posture_score",
                100.0
            )
        )

        safe_pct = (
            summary_data.get(
                "safe_pct",
                0.0
            )
        )

        warning_pct = (
            summary_data.get(
                "warning_pct",
                0.0
            )
        )

        non_safe_pct = (
            summary_data.get(
                "non_safe_pct",
                0.0
            )
        )

        distance = (
            summary_data.get(
                "avg_distance",
                0.0
            )
        )

        pitch = (
            summary_data.get(
                "avg_pitch",
                0.0
            )
        )

        yaw = (
            summary_data.get(
                "avg_yaw",
                0.0
            )
        )

        shoulder = (
            summary_data.get(
                "avg_shoulder_tilt",
                0.0
            )
        )

        eye_open = (
            summary_data.get(
                "avg_eye_openness",
                0.0
            )
        )

        blink_rate = (
            summary_data.get(
                "avg_blink_rate",
                0.0
            )
        )


        reasons = (
            summary_data.get(
                "reason_counts",
                {}
            )
        )


        reason_text = (
            ", ".join(
                key.replace(
                    "_",
                    " "
                )
                for key in reasons.keys()
            )
            if reasons
            else
            "No major posture violations were recorded."
        )


        return {

            "executive_summary": f"""
- **Overall posture score:** {score:.1f}%.
- **Safe time:** {safe_pct:.1f}% of the monitored session.
- **Warning time:** {warning_pct:.1f}%.
- **Non-safe time:** {non_safe_pct:.1f}%.
- The most frequently recorded posture concerns were: {reason_text}.
- The current session should be interpreted as an ergonomic monitoring result, not a medical diagnosis.
- The highest-value improvement should focus on reducing persistent deviations rather than reacting to isolated frames.
""",

            "biomechanical_analysis": f"""
- **Screen distance:** Average estimated distance was {distance:.1f} cm. Compare this value with the configured safe operating range rather than treating a single frame as diagnostic.
- **Head pitch:** Average pitch was {pitch:.1f}°. Sustained forward/downward head positioning should be minimized where possible.
- **Head yaw:** Average yaw was {yaw:.1f}°. Persistent turning away from the screen may indicate an inefficient viewing position.
- **Shoulder alignment:** Average shoulder tilt was {shoulder:.1f}°. Keeping the shoulders relatively level is preferable during prolonged laptop work.
- **Eye openness:** Average eye openness was {eye_open:.3f}. Lower values should be interpreted as an observed visual behavior, not evidence of an eye disease.
- **Blinking:** Average blink rate was {blink_rate:.1f} blinks/min. Blink measurements are best interpreted as a screen-comfort indicator rather than a medical finding.
""",

            "exercises_coaching": """
1. **Chin Tuck**
   - Sit upright.
   - Gently draw the head backward without looking down.
   - Hold for 3–5 seconds.
   - Repeat 8–10 times.

2. **Scapular Retraction**
   - Relax your shoulders.
   - Gently draw the shoulder blades back and down.
   - Hold for 3 seconds.
   - Repeat 10 times.

3. **Neck Mobility**
   - Slowly rotate the head left and right within a comfortable range.
   - Do not force the movement.
   - Repeat 5 times per side.

4. **Shoulder Rolls**
   - Roll both shoulders backward slowly.
   - Perform 10 controlled repetitions.

5. **20-20-20 Rule (Visual Break)**
   - Every 20 minutes, take a break from the screen.
   - Look at an object at least 20 feet (6 meters) away.
   - Maintain focus on it for at least 20 seconds to relax eye muscles.
""",

            "workstation_optimization": f"""
- Keep the screen at a comfortable viewing distance; the monitored average was {distance:.1f} cm.
- Raise the laptop display when possible so prolonged viewing does not require excessive downward head positioning.
- Use an external keyboard and mouse if the laptop is elevated.
- Keep the chair and desk height configured so that the shoulders can remain relaxed.
- Avoid strong reflections or direct glare on the display.
- Use balanced room lighting rather than relying on a bright screen in a dark room.
- Take short movement breaks during prolonged sessions instead of remaining stationary for long periods.
"""
        }