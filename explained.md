# AI Ergonomics Monitor — Feature Reference Guide

> **System**: Front-camera laptop posture monitoring using MediaPipe Face & Pose landmark models.
> **Camera**: Built-in laptop webcam (front-facing only).
> **User setup**: One person, seated, upper body visible, facing screen directly.

---

## How the System Works (Overview)

```
Webcam Frame
     │
     ▼
MediaPipe FaceLandmarker  ──►  Face mesh (478 landmarks)
MediaPipe PoseLandmarker  ──►  Body pose (33 landmarks)
     │
     ▼
Feature Extraction (per frame)
     │
     ▼
Single-Frame Safety Rules  ──►  SAFE / WARNING / NON-SAFE
     │
     ▼
Temporal Persistence Engine
(delay: ~2s for WARNING, ~5s for NON-SAFE)
     │
     ▼
Final Display Status + Violation Reasons
```

The **Temporal Persistence Engine** prevents flicker — brief violations do not immediately change the displayed status. You must hold a violation continuously for the required duration.

---

## 🟢 Status Levels

| Status | Meaning | How long violation must persist |
|---|---|---|
| **SAFE** | All measurements within acceptable range | — |
| **WARNING** | One or more measurements slightly out of range | ≥ **2.0 seconds** continuous |
| **NON-SAFE** | One or more measurements significantly out of range | ≥ **5.0 seconds** continuous |
| **UNKNOWN** | Face or pose was not detected in this frame | Status is held from previous frame |

> Recovery to **SAFE** is **instant** — as soon as all measurements return to acceptable range, the status resets immediately.

---

## 📏 Feature 1 — Screen Distance

**What it is**: Estimated distance between the user's face and the laptop screen, in centimetres.

**How it is measured**: The horizontal width of the face in normalized image coordinates is extracted from two cheek landmarks (MediaPipe landmark #234 and #454). An **inverse distance model** converts this to centimetres:

```
distance = a / (face_width_norm - b)
```

Calibrated parameters: `a = 15.244`, `b = -0.0543`

**Why it matters**: Sitting too close causes eye strain and poor posture. Sitting too far causes leaning forward.

| Distance | Status | Violation code |
|---|---|---|
| **< 40 cm** | 🔴 NON-SAFE | `screen_too_close` |
| **40 – 45 cm** | 🟠 WARNING | `screen_distance_low` |
| **45 – 75 cm** | 🟢 SAFE | — |
| **75 – 85 cm** | 🟠 WARNING | `screen_distance_high` |
| **> 85 cm** | 🔴 NON-SAFE | `screen_too_far` |

---

## 📐 Feature 2 — Head Pitch

**What it is**: Vertical tilt of the head — nodding forward (chin down) or backward (chin up), measured in degrees relative to the user's neutral calibrated position.

**How it is measured**: Extracted from the 4×4 facial transformation matrix output by MediaPipe FaceLandmarker. The rotation matrix is decomposed into Euler angles using the standard ZYX convention.

**What it looks like**:
- `+` = chin up / head tilted back
- `−` = chin down / head tilted forward (common when slouching)

| Deviation from neutral | Status | Violation code |
|---|---|---|
| **< 15°** | 🟢 SAFE | — |
| **≥ 15°** | 🟠 WARNING | `head_pitch_warning` |
| **≥ 20°** | 🔴 NON-SAFE | `head_pitch_non_safe` |

*Deviation is the absolute difference from the calibrated neutral position.*

---

## 📐 Feature 3 — Head Yaw

**What it is**: Horizontal rotation of the head — turning left or right, measured in degrees relative to neutral.

**How it is measured**: Same facial transformation matrix decomposition as pitch.

**What it looks like**:
- `+` = head turned right
- `−` = head turned left

| Deviation from neutral | Status | Violation code |
|---|---|---|
| **< 15°** | 🟢 SAFE | — |
| **≥ 15°** | 🟠 WARNING | `head_yaw_warning` |
| **≥ 30°** | 🔴 NON-SAFE | `head_yaw_non_safe` |

---

## 📐 Feature 4 — Head Roll

**What it is**: Side tilt of the head — tilting left or right ear toward the shoulder, measured in degrees.

**How it is measured**: Third Euler angle from the same rotation matrix decomposition.

**Safety thresholds**:
- **Deviation $\ge 15^\circ$** → `WARNING`
- **Deviation $\ge 30^\circ$** → `NON-SAFE`

---

## 🤷 Feature 5 — Shoulder Tilt

**What it is**: The angular deviation of the shoulder line from horizontal, measured in degrees.

**How it is measured**: MediaPipe PoseLandmarker provides landmark positions for left shoulder (#11) and right shoulder (#12) in normalized image coordinates. The tilt angle is:

```python
tilt = degrees( atan2(dy, abs(dx)) )
```

> `abs(dx)` is used instead of `dx` to normalize the result to `[−90°, +90°]` regardless of whether the camera mirrors the left/right landmark ordering (which front cameras typically do).

**What it looks like**:
- `0°` = shoulders perfectly level
- `+` / `−` = one shoulder raised relative to the other

| Deviation from neutral (0°) | Status | Violation code |
|---|---|---|
| **< 10°** | 🟢 SAFE | — |
| **≥ 10°** | 🟠 WARNING | `shoulder_tilt_warning` |
| **≥ 20°** | 🔴 NON-SAFE | `shoulder_tilt_non_safe` |

---

## 👁️ Feature 6 — Eye Openness Ratio

**What it is**: A ratio describing how open the eyes are. Computed separately for left and right eye, then averaged.

**How it is measured**: Vertical eye height divided by horizontal eye width using four eye-corner landmarks:

```
eye_open_ratio = vertical_height / horizontal_width
```

| Eye | Landmarks used |
|---|---|
| Left | Outer #33, Inner #133, Top #159, Bottom #145 |
| Right | Outer #362, Inner #263, Top #386, Bottom #374 |

**Typical values**:
- Eyes fully open: ~0.30 – 0.45
- Eyes half-closed: ~0.15 – 0.25
- Eyes closed: ~0.0 – 0.10

**Safety thresholds**:
- **Ratio $\le 0.25$** → `WARNING` (Heavy squinting or drowsiness)
- **Ratio $\le 0.15$** → `NON-SAFE` (Eyes critically closed)

---

## 👁️ Feature 7 — Blink Count & Blink Rate *(v2 — Improved)*

**What it is**: Running count of detected blinks, plus a per-minute blink rate over the last 60 seconds.

### Why the old version was unreliable
The original detector used a fixed baseline (`0.245`) calibrated at setup time and a single close-threshold at 55% of that fixed value. Problems:
- With glasses, face at a different angle, or changed lighting the baseline drifts → threshold no longer matches the real "closed" EAR
- Close-threshold (55%) and reopen-threshold (75%) were too close together → noisy EAR values caused the same blink to fire twice

### How v2 fixes this

| Parameter | v1 | v2 |
|---|---|---|
| Baseline | Fixed from calibration | **Rolling 80th-percentile** of last 150 frames (~10s) — adapts live |
| Close threshold | 55% of baseline | **40% of baseline** — deeper, less prone to noise false-fires |
| Reopen threshold | 75% of baseline | **65% of baseline** — wider hysteresis gap |
| Blink duration guard | 50ms – 1000ms | **40ms – 600ms** — excludes long deliberate closures |
| Min inter-blink interval | none | **80ms** — prevents double-counting one blink |

**Normal healthy blink rate**: 12 – 20 blinks / minute.

**Blink rate warning**: if rate drops below **12 / min** (sustained exposure to screen without blinking) → `low_blink_rate` wellness alert.

---

## 👁️ Feature 8 — Squint Detection *(New)*

**What it is**: Detection of sustained partial eye closure — squinting — which is distinct from blinking. Squinting occurs when a person tries to see through glare, compensate for eye fatigue, or focus on a bright/dim screen.

**How it works**: Uses the same EAR ratio but looks for values in the **30%–70% of baseline** range (not a blink, not fully open). If this partial closure persists for ≥ **0.8 seconds**, a squint event begins.

**Wellness alert triggered**: if squinting occupies **>20% of the last 60 seconds** (`squint_warning = True`).

| EAR zone | Interpretation |
|---|---|
| > 70% baseline | Eyes open (normal) |
| 30%–70% baseline | **Squinting** |
| < 30% baseline | Full closure / blink |

---

## 👁️ Feature 9 — Gaze Fixation Detection *(New)*

**What it is**: Detects when the user stares at the screen without moving their eyes — "screen hypnosis." Normal vision involves frequent micro-saccades (tiny eye movements). Absence of these movements indicates unhealthy fixation linked to reduced blink rate and eye dryness.

**How it works**: A rolling buffer of the last 30 gaze positions (gaze_x, gaze_y from iris landmarks) is maintained. The standard deviation of recent positions is computed:
- `dispersion = sqrt(std(gaze_x)² + std(gaze_y)²)`
- Below `0.03` in normalized eye-box units = essentially no eye movement

**Onset**: must remain still for **≥ 5 seconds** to be classified as fixated.

**Wellness alert triggered**: if fixation fraction exceeds **40% of the last 60 seconds** (`gaze_fixation_warning = True`).

---

## 🧠 Feature 10 — Head Forward Lean / Turtle-Neck *(New)*

**What it is**: Detects gradual forward head projection — the user slowly leaning toward the screen over time. This is different from the distance rule (which fires on absolute cm thresholds). A user may be at 65 cm but 15 cm closer than when they sat down.

**How it works**: In the first 60 frames, the system builds a **session baseline** face width (median of first 60 good measurements). Then each frame:

```
lean_ratio = current_face_width_norm / session_baseline_width
```

If `lean_ratio ≥ 1.20` (face appears 20% bigger = ~15 cm closer) for **≥ 4 seconds** continuously → `forward_lean_warning = True`.

The ratio is shown in the wellness panel, e.g. `Forward Lean / Turtle-neck (1.23x)`.

**Resolves** when lean_ratio drops below `1.10` (10% over baseline).

---

## 💡 Feature 11 — Brightness Strain Detection *(New)*

**What it is**: Detects lighting conditions that strain the eyes, computed purely from the webcam frame itself using YCrCb luma analysis.

**Three strain types detected**:

| Strain type | Condition | What it means |
|---|---|---|
| `dark_room` | Frame luma **< 50** | Room is too dark — eyes work harder to see the screen |
| `bright_glare` | Frame luma **> 210** | Overexposed / very bright room or direct sunlight — screen washes out |
| `backlight_glare` | Frame luma fine, but **face luma ≥ 40 units darker than scene** | Bright window or light source behind the user causes backlight silhouette |

No machine learning model used — pure pixel analysis.

**Wellness alert triggered**: any non-`ok` brightness strain code → `brightness_warning = True` with description shown in the WELLNESS ALERTS panel.

---

## 📊 Wellness Alerts Panel (Display)

When any wellness condition is active, a **WELLNESS ALERTS** panel appears on the right side of the frame with colored indicator dots:

| Indicator | Trigger |
|---|---|
| 🟠 Dark Room / Bright Glare / Backlight | Brightness strain detected |
| 🟡 Sustained Squinting | Squinting >20% of last 60s |
| 🔵 Screen Fixation | Gaze still >40% of last 60s |
| 🟠 Forward Lean / Turtle-neck | Face width 20%+ larger than session start |
| 🟢 Low Blink Rate | Blink rate < 12/min |

Blink rate is always shown at the bottom of the left measurement panel as `Blink rate: X.X/min`.

---

## 🚫 What the System Deliberately Does NOT Do

| Excluded feature | Reason |
|---|---|
| Laptop lid angle | Not observable from the built-in front camera |
| RTMPose side-camera classifier | Requires side-view camera; excluded from final sponsor requirement |
| Gaze as absolute safety trigger | Too noisy without per-user gaze calibration |
| CUDA / GPU acceleration | Not required; CPU inference is sufficient at ~14 FPS |
| Multiple-person tracking | Designed for single seated user only |

---

## ⏱️ Temporal Persistence Rules

The system does **not** immediately change status on a single bad frame. Violations must be **continuous** for the following durations:

| Transition | Required duration |
|---|---|
| SAFE → WARNING | ≥ **2.0 seconds** |
| SAFE / WARNING → NON-SAFE | ≥ **5.0 seconds** |
| Any → SAFE | **Instant** (next SAFE frame) |
| UNKNOWN frame (no detection) | Status **held** from previous frame |

This prevents false alarms from momentary head movements, blinking, or brief sensor glitches.

> **Note**: Wellness detectors (blink rate, squint, gaze fixation, forward lean, brightness) have their own internal timing logic and are **not** subject to the temporal persistence engine — they fire independently based on their own duration thresholds.

---

## 🤖 Models Used

| Model | File | Role |
|---|---|---|
| MediaPipe Face Landmarker | `face_landmarker.task` | 478-point face mesh, head pose transformation matrix, blendshapes |
| MediaPipe Pose Landmarker Full | `pose_landmarker_full.task` | 33-point body pose with shoulder, hip, and limb positions |

**Backend**: TensorFlow Lite (XNNPACK CPU delegate) via MediaPipe Tasks Python API.  
**No GPU required.** CPU-only inference. Typical inference time: 30–70 ms per frame on a mid-range laptop CPU.

> **RTMPose is NOT used.** The original project had an experimental side-camera RTMPose posture classifier. That was discarded. The current production system is MediaPipe front-camera only.

---

## 📋 Display Overlay Guide

### Left Panel (Posture Measurements)

| Element | Description |
|---|---|
| **Top banner colour** | Green = SAFE, Amber = WARNING, Red = NON-SAFE, Gray = UNKNOWN |
| **Dist** | Estimated distance to screen in cm (amber/red when violating) |
| **Pitch** | Head pitch in degrees (amber/red when violating) |
| **Yaw** | Head yaw in degrees (amber/red when violating) |
| **Shoulder** | Shoulder tilt in degrees (amber/red when violating) |
| **Eye Open** | Mean eye openness ratio |
| **Blinks** | Running blink count for this session |
| **Inference: X ms** | Time for MediaPipe face + pose inference per frame |
| **Model: MediaPipe** | Confirms model backend |
| **Blink rate: X/min** | Blink rate over last 60 seconds |
| **`frame: <status>`** | Instantaneous per-frame status before temporal persistence |

### Right Panel (Wellness Alerts — shown only when active)

| Element | Description |
|---|---|
| **WELLNESS ALERTS** header | Appears when any wellness condition fires |
| 🟠 **Dark Room / Bright Glare / Backlight** | Brightness strain detected |
| 🟡 **Sustained Squinting** | Squinting > 20% of last 60 seconds |
| 🔵 **Screen Fixation** | Gaze motionless > 40% of last 60 seconds |
| 🟠 **Forward Lean / Turtle-neck (X.XXx)** | Face width ≥ 20% larger than session baseline |
| 🟢 **Low Blink Rate (X/min)** | Blink rate < 12 per minute |

### Bottom Bar (Safety Violations — shown only when not SAFE)

| Element | Description |
|---|---|
| **`! Reason text`** | Human-readable cause of the current WARNING/NON-SAFE status |

### Keyboard Controls

| Key | Action |
|---|---|
| `Q` or `ESC` | Quit |
| `F` | Toggle fullscreen |

---

## ⚡ System Improvements & Advanced Features (v2.1)

| Feature | Module | Description |
|---|---|---|
| **EMA Metric Smoothing** | `backend/vision/pipeline.py` | Low-pass Exponential Moving Average ($\alpha = 0.70$) filters out single-frame 1–2° landmark jitter on head pitch, yaw, roll, shoulder tilt, and distance. |
| **Neutral Shoulder Calibration** | `backend/calibration/manager.py` | Supports saving user's neutral shoulder tilt in reference profile to evaluate relative deviation $|\text{tilt} - \text{neutral}| \ge 10^\circ$. |
| **Smart Forward Lean Baseline** | `backend/vision/forward_lean.py` | Gated baseline collection: initial face-width baseline is only recorded when estimated distance is in the **SAFE zone (45–75 cm)**. |
| **Desktop & Audio Alerts** | `backend/app/notifier.py` | Triggers OS desktop toast notifications & Windows audio chimes when **NON-SAFE** status persists for $\ge 10$ seconds (30s cooldown prevents spam). |
| **Session Posture Health Report** | `backend/app/reporter.py` | Computes an overall **Posture Health Score %**, tracks time distribution across SAFE / WARNING / NON-SAFE, and outputs `session_summary.txt` on exit. |
| **Frame-by-Frame Telemetry Logger** | `backend/telemetry/logger.py` | Records every frame's metrics, final status, violation reasons, and wellness alerts to a timestamped JSONL file in `logs/`. Used as input for AI PDF reports. |
| **Groq AI PDF Ergonomic Report** | `backend/reports/ai_insights.py`, `pdf_generator.py` | Sends aggregated session telemetry to Groq LLM (llama-3.3-70b-versatile) for personalized ergonomic insights. Renders Matplotlib charts (status timeline, metric distributions, wellness alert breakdown) and compiles everything into a downloadable ReportLab PDF at `Ergonomic_Report.pdf`. |

---

## 📊 Telemetry & AI Report Pipeline

```
Frame Processing Loop
     │
     ▼
TelemetryLogger.log_frame()
     │  (writes one JSON line per frame to logs/telemetry_YYYYMMDD_HHMMSS.jsonl)
     │
     ▼  (on session exit, if --generate-pdf)
generate_ai_pdf_report.py
     │
     ├── 1. Load JSONL telemetry file
     ├── 2. Compute aggregate statistics (posture score, violation counts, metric ranges)
     ├── 3. Call Groq LLM API → AI-generated ergonomic insights & recommendations
     ├── 4. Render Matplotlib charts (status timeline, metric distributions, wellness breakdown)
     └── 5. Compile ReportLab PDF → Ergonomic_Report.pdf
```

### Telemetry JSONL Format (one line per frame)

| Field | Type | Description |
|---|---|---|
| `frame_index` | int | Sequential frame number |
| `timestamp` | float | Unix epoch timestamp |
| `face_detected` | bool | Whether MediaPipe detected a face |
| `pose_detected` | bool | Whether MediaPipe detected body pose |
| `estimated_distance_cm` | float | Screen distance estimate |
| `head_pitch_deg` | float | Head pitch angle |
| `head_yaw_deg` | float | Head yaw angle |
| `shoulder_tilt_deg` | float | Shoulder tilt angle |
| `eye_openness` | float | Mean eye openness ratio |
| `blink_count` | int | Running blink count |
| `blink_rate_per_min` | float | 60-second rolling blink rate |
| `final_status` | string | SAFE, WARNING, NON-SAFE, or UNKNOWN |
| `reasons` | list | Active violation reason codes |
| `wellness_alerts` | list | Active wellness alert strings |
| `inference_ms` | float | Frame processing time in ms |

### CLI Usage

```bash
# Auto-generate PDF on exit
python backend/app/main.py --generate-pdf

# Generate PDF from a saved telemetry log
python generate_ai_pdf_report.py --telemetry logs/telemetry_20260813_011906.jsonl
```

> **Requires**: `GROQ_API_KEY` environment variable or key configured in `generate_ai_pdf_report.py`.
