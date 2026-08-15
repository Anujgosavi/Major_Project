# AI Ergonomics Monitor — Complete Technical Reference Guide

> **System**: Front-camera laptop ergonomic posture & digital wellness monitor using MediaPipe Face & Pose landmarks, Flask REST/MJPEG streaming, and a React 19 web dashboard.
> **Camera**: Standard built-in laptop webcam (front-facing).
> **User setup**: One seated person, upper body visible, directly facing the screen.

---

## 🏗️ Architecture & Data Flow

```
Webcam Frame (30 FPS)
     │
     ▼
MediaPipe FaceLandmarker  ──►  Face mesh (478 landmarks) + Iris + Transformation Matrix
MediaPipe PoseLandmarker  ──►  Upper-body pose (33 landmarks)
     │
     ▼
Feature Extraction (EMA Low-Pass Filter α = 0.70)
  • Distance (Inverse Model)
  • Pitch, Yaw, Roll (Euler Angles)
  • Shoulder Tilt & Slouch Ratio
  • EAR Blink Rate, Squint & Gaze Fixation
  • Ambient Luma Brightness Strain
     │
     ▼
Single-Frame Safety Rules  ──►  Raw Status (SAFE / WARNING / NON-SAFE)
     │
     ▼
Temporal Persistence Engine
  • SAFE ──► WARNING (Must persist ≥ 2.0s continuously)
  • WARNING / SAFE ──► NON-SAFE (Must persist ≥ 5.0s continuously)
  • Recovery to SAFE (Instant)
     │
     ▼
Annotator & State Sync
     │
     ├──► MJPEG Stream Generator (/video_feed)
     ├──► Flask REST Status API (/api/status) [Sanitized JSON: no NaNs]
     └──► Frame Telemetry Logger (JSONL in logs/)
```

---

## 🟢 Status Classifications

| Status | Meaning | Required Continuous Persistence | Recovery Time |
|---|---|---|---|
| **`SAFE`** | All measurements within healthy limits | Instant | Instant |
| **`WARNING`** | Mild posture or distance deviation | $\ge 2.0$ seconds | Instant on return to SAFE |
| **`NON-SAFE`** | Significant posture violation or neck compression | $\ge 5.0$ seconds | Instant on return to SAFE |
| **`UNKNOWN`** | Face or upper body briefly out of frame | Held from last valid frame | Instant on redetection |

---

## 📐 Posture & Safety Metrics

### 1. Approximate Screen Distance ($d$)
- **Algorithm**: Face-width inverse distance function:
  $$d = \frac{a}{w_{\text{norm}} - b}$$
  where $w_{\text{norm}} = |x_{454} - x_{234}|$ (distance between outer cheek landmarks).
  Calibrated constants: $a = 15.244$, $b = -0.0543$.
- **Policy**:
  - $< 40\text{ cm}$: `NON-SAFE` (`screen_too_close`)
  - $40\text{–}45\text{ cm}$: `WARNING` (`screen_distance_low`)
  - $45\text{–}75\text{ cm}$: `SAFE` (Optimal zone)
  - $75\text{–}85\text{ cm}$: `WARNING` (`screen_distance_high`)
  - $> 85\text{ cm}$: `NON-SAFE` (`screen_too_far`)

### 2. Head Pitch (Tilt Up / Down)
- **Algorithm**: Extracted via 3D facial rotation matrix decomposition (ZYX Euler angles) relative to neutral reference.
- **Thresholds**:
  - Deviation $< 15^\circ$: `SAFE`
  - Deviation $\ge 15^\circ$: `WARNING` (`head_pitch_warning`)
  - Deviation $\ge 20^\circ$: `NON-SAFE` (`head_pitch_non_safe`)

### 3. Head Yaw (Turn Left / Right)
- **Algorithm**: Horizontal facial rotation angle decomposed from FaceLandmarker transform matrix.
- **Thresholds**:
  - Deviation $< 15^\circ$: `SAFE`
  - Deviation $\ge 15^\circ$: `WARNING` (`head_yaw_warning`)
  - Deviation $\ge 30^\circ$: `NON-SAFE` (`head_yaw_non_safe`)

### 4. Shoulder Tilt (Alignment)
- **Algorithm**: Angle formed by left shoulder (#11) and right shoulder (#12) keypoints:
  $$\theta = \arctan\left(\frac{\Delta y}{|\Delta x|}\right) \times \frac{180}{\pi}$$
- **Thresholds**:
  - Deviation $< 10^\circ$: `SAFE`
  - Deviation $\ge 10^\circ$: `WARNING` (`shoulder_tilt_warning`)
  - Deviation $\ge 20^\circ$: `NON-SAFE` (`shoulder_tilt_non_safe`)

### 5. Slouch & Neck Compression Ratio
- **Algorithm**: Vertical ratio of nose-to-shoulder-center distance relative to shoulder width.
- **Thresholds**:
  - Ratio $> 0.65$: `SAFE`
  - Ratio $\le 0.65$: `WARNING` (`slouch_warning`)
  - Ratio $\le 0.55$: `NON-SAFE` (`slouch_non_safe`)

---

## 👁️ Digital Wellness & Eye Strain Features

### 6. Adaptive Blink Rate Detector
- **Algorithm**: Eye Aspect Ratio (EAR) calculated on outer/inner corners and upper/lower eyelids. Uses an adaptive rolling 80th-percentile baseline over 150 frames to compensate for lighting and glasses.
- **Threshold**: Warning triggered if 60-second rolling blink rate drops below **12 blinks/min**.

### 7. Sustained Squinting
- **Algorithm**: Identifies partial closures (30%–70% of baseline EAR) lasting $\ge 0.8\text{s}$.
- **Alert**: Triggers when squinting duration exceeds **20% of the last 60 seconds**.

### 8. Gaze Fixation / Screen Stare
- **Algorithm**: Computes the standard deviation dispersion of iris center coordinates over a rolling 30-frame window.
- **Alert**: Triggers when eye gaze remains stationary (< 0.03 normalized dispersion) for $> 40\%$ of a 60-second window.

### 9. Forward Lean (Turtle-Neck)
- **Algorithm**: Builds a session baseline face width during the first 60 frames in the SAFE distance zone.
- **Alert**: Triggers when face width increases $\ge 20\%$ above baseline for $\ge 4.0\text{s}$.

### 10. Ambient Brightness Strain
- **Algorithm**: Evaluates YCrCb luma channel across the full frame and face bounding box:
  - `dark_room`: Frame luma $< 50$.
  - `bright_glare`: Frame luma $> 210$.
  - `backlight_glare`: Background luma is $\ge 40$ units brighter than face luma.

### 11. 20-20-20 Rule & Hydration Reminders
- **20-20-20 Rule**: Every 20 minutes (configurable demo intervals), triggers a full-width overlay and audio chime for visual rest.
- **Hydration Reminder**: Timed reminder overlay with one-click **Accept** dismiss action.

---

## 💻 Web Frontend & API Architecture

### Frontend Pages
1. **`LiveFeed` (`/live`)**:
   - Live stream from `/video_feed`.
   - Compact **2-Column Live Metrics sidebar** displaying Distance, Pitch, Yaw, Shoulder Tilt, Blink Rate, Eye Openness, and Next Break Countdown without requiring vertical scrolling.
   - Interactive Toast and Video overlay notifications with auto-dismiss timers.
2. **`Dashboard` (`/dashboard`)**:
   - Ergonomic score summaries, activity charts, posture breakdown donuts, and recent session logs.
3. **`Reports` (`/reports`)**:
   - Historical session search, filtering by date and score, and PDF generation triggers.
4. **`LandingPage` (`/`)**:
   - Modern hero section, capability highlights, and feature cards.
5. **`Login` & `Signup` (`/login`, `/signup`)**:
   - Authentication forms with real-time password strength validation.

### Robust Proxy & JSON Sanitization
- **`setupProxy.js`**: Uses `http-proxy-middleware` to cleanly route `/api` and `/video_feed` requests from `localhost:3000` to `127.0.0.1:5000`.
- **JSON Sanitization (`server.py`)**: All numeric outputs are passed through `_safe_float()` and `sanitize_for_json()`, ensuring `NaN` or `Inf` values are cleanly converted to valid JSON numbers (`0.0`) so `JSON.parse` in browsers never throws syntax errors.

---

## 📊 Session Telemetry & AI Report Generation

1. **Telemetry Logging**: Every processed frame writes a JSONL entry to `logs/telemetry_YYYYMMDD_HHMMSS.jsonl`.
2. **AI Analysis**: `generate_ai_pdf_report.py` aggregates session metrics and queries Gemini/Groq LLMs for custom ergonomic recommendations.
3. **PDF Generation**: Renders Matplotlib trend charts and formats a complete ReportLab PDF summary (`Ergonomic_Report.pdf`).
