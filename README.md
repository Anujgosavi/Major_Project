# AI Ergonomics & Digital-Wellness Monitoring System

A continuous, real-time laptop built-in webcam system for single-user ergonomic posture, screen distance, and digital wellness monitoring. Built using MediaPipe Face & Pose vision pipelines, EMA metric smoothing, temporal state machine policy enforcement, desktop alerts, and AI-powered PDF report generation.

---

## 🎯 System Capabilities

### Primary Safety Monitoring
- **Approximate Screen Distance (cm)**: Inverse calibration model ($d = a / (w - b)$) with EMA smoothing.
- **Head Pitch & Yaw (°)**: Rotation matrix Euler angle deviations relative to user reference.
- **Shoulder Alignment / Tilt (°)**: 2D shoulder keypoint angle and alignment ratio with optional neutral calibration.
- **Safety Classification**: Continuous state classification (`SAFE`, `WARNING`, `NON-SAFE`) with temporal persistence (~2s `WARNING`, ~5s `NON-SAFE`).

### Digital Wellness & Eye-Strain Monitoring
- **Blink Rate (per minute)**: Rolling 60-second window blink rate with EAR (Eye Aspect Ratio) based detection.
- **Squint Detection**: Monitors sustained squinting > 20% of the last 60 seconds.
- **Gaze Fixation / Screen Stare**: Detects motionless gaze > 40% of the last 60 seconds.
- **Forward Lean / Turtle-Neck**: Smart baseline comparison with distance-gated calibration, triggers at ≥ 20% face-width increase.
- **Brightness Strain**: Ambient brightness analysis detecting dark room, bright glare, and backlight conditions.

### Reporting & Insights
- **Session Posture Health Report**: Auto-generated on exit with posture score %, time distribution, and top violations.
- **Frame-by-Frame Telemetry Logging**: JSONL log of every frame's metrics, status, and wellness alerts.
- **AI-Powered PDF Ergonomic Report**: Gemini 2.5 LLM analysis with charts, tables, and downloadable PDF.
- **Desktop & Audio Notifications**: OS toast + audio chime when NON-SAFE persists ≥ 10 seconds (30s cooldown).

---

## 📐 Validated Ergonomic Policy

| Measurement | `SAFE` | `WARNING` (Requires 2s persistence) | `NON-SAFE` (Requires 5s persistence) |
| :--- | :--- | :--- | :--- |
| **Distance** | 45 – 75 cm | 40–45 cm or 75–85 cm | < 40 cm or > 85 cm |
| **Head Pitch Deviation** | < 15° | $\ge 15^\circ$ | $\ge 30^\circ$ |
| **Head Yaw Deviation** | < 15° | $\ge 15^\circ$ | $\ge 30^\circ$ |
| **Shoulder Tilt Deviation** | < 10° | $\ge 10^\circ$ | $\ge 20^\circ$ |

### Wellness Alert Thresholds (Independent Timers)

| Indicator | Trigger |
|---|---|
| Brightness Strain | Dark room / Bright glare / Backlight detected |
| Sustained Squinting | Squinting > 20% of last 60 seconds |
| Screen Fixation | Gaze motionless > 40% of last 60 seconds |
| Forward Lean | Face width ≥ 20% larger than session baseline |
| Low Blink Rate | Blink rate < 12 per minute |
| Slouch / Neck Compression | Nose-to-shoulder vertical distance ratio drops below 0.65 |
| 20-20-20 Rule | Every 20 minutes: Look 20 feet away for 20 seconds (Timed banner + notification) |

> **Note**: Wellness alerts have their own internal timing and are NOT subject to the temporal persistence engine.

---

## 📁 Repository Architecture

```
Major_Project/
│
├── backend/
│   ├── app/
│   │   ├── main.py                  # CLI / Continuous execution entry point
│   │   ├── annotator.py             # OpenCV status banner, metrics, wellness alerts overlay
│   │   ├── notifier.py              # Desktop toast & audio notifications
│   │   └── reporter.py              # Session posture health report generator
│   │
│   ├── vision/
│   │   ├── face.py                  # Face Mesh & Iris (Pitch, Yaw, Roll, Gaze, Eye Openness)
│   │   ├── pose.py                  # Body Pose (Shoulder width & tilt)
│   │   ├── distance.py              # Inverse distance calculation
│   │   ├── blink.py                 # Temporal eye closure / blink detector (EAR-based)
│   │   ├── squint.py                # Sustained squint detection (60s rolling window)
│   │   ├── gaze_fixation.py         # Gaze fixation / screen stare detection
│   │   ├── forward_lean.py          # Forward lean (face-width baseline, distance-gated)
│   │   ├── brightness.py            # Ambient brightness & strain detection
│   │   └── pipeline.py              # Unified FrontCameraPipeline (EMA-smoothed)
│   │
│   ├── safety/
│   │   ├── rules.py                 # Single-frame policy evaluator
│   │   ├── temporal.py              # Temporal persistence state machine (2s/5s)
│   │   └── engine.py                # Combined SafetyEngine wrapper
│   │
│   ├── telemetry/
│   │   └── logger.py                # JSONL frame-by-frame telemetry logger
│   │
│   ├── reports/
│   │   ├── ai_insights.py           # Groq LLM API integration for AI analysis
│   │   └── pdf_generator.py         # ReportLab + Matplotlib PDF chart generator
│   │
│   ├── calibration/
│   │   └── manager.py               # Calibration & user reference profile manager
│   └── config/
│       └── loader.py                # JSON policy & safety config loader
│
├── models/                          # MediaPipe task models (.task files)
├── calibration/                     # Calibration JSON artifacts
├── config/                          # Policy JSON artifacts
├── notebooks/                       # Preserved Jupyter development notebooks
│   ├── NB1.ipynb                    # Calibration & pipeline creation
│   ├── Nb2.ipynb                    # Video feed validation & policy refinement
│   └── Nb3.ipynb                    # Sponsor demo & live batch runner
├── scripts/
│   └── download_models.py           # Automated model downloader
├── tests/                           # Unit & integration automated tests
├── logs/                            # Runtime telemetry JSONL logs (auto-created)
│
├── generate_ai_pdf_report.py        # Standalone CLI: Groq AI + PDF report from telemetry
├── requirements.txt
├── explained.md                     # Detailed feature reference guide
├── README.md
└── .gitignore
```

---

## 🗺️ Notebook Component Mapping

| Notebook Source | Production Module | Description |
| :--- | :--- | :--- |
| `NB1` Cell 102, `NB2` Cell 49 | `backend/vision/pipeline.py`, `face.py`, `pose.py` | Front-camera vision pipeline, landmark processing, and iris gaze extraction. |
| `NB2` Cell 56, `NB3` Cell 1 | `config/front_camera_final_policy.json`, `backend/config/loader.py` | Authoritative sponsor-validated policy thresholds and loader. |
| `NB2` Cell 56, `NB3` Cell 9 | `backend/safety/rules.py` | Frame-level safety rule evaluation. |
| `NB2` Cell 57, `NB3` Cell 9 | `backend/safety/temporal.py` | Temporal persistence state machine (`FinalTemporalState` / `SponsorTemporalState`). |
| `NB3` Cell 10 | `backend/app/annotator.py` | OpenCV sponsor-facing frame status banner and overlay drawing. |

---

## 🛠️ Setup & Execution Instructions

### 1. Install Dependencies
Ensure Python 3.9+ is installed:
```bash
pip install -r requirements.txt
```

### 2. Download MediaPipe Models
Download official MediaPipe task models (`face_landmarker.task` and `pose_landmarker_full.task`):
```bash
python scripts/download_models.py
```

### 3. Run Continuous Real-Time Monitoring
Start live webcam monitoring (uses camera device index `0` by default):
```bash
python backend/app/main.py
```

To run on a recorded video file:
```bash
python backend/app/main.py --source path/to/video.mp4
```

To run headless (without GUI display):
```bash
python backend/app/main.py --headless --max-frames 100
```

### 4. Generate AI-Powered PDF Report
Add `--generate-pdf` to automatically generate a Gemini AI insights PDF on session exit:
```bash
python backend/app/main.py --source video.mp4 --generate-pdf --api-key YOUR_GEMINI_KEY
```

Or generate from a previously saved telemetry log:
```bash
python generate_ai_pdf_report.py --telemetry logs/telemetry_YYYYMMDD_HHMMSS.jsonl --api-key YOUR_GEMINI_KEY
```

> **Note**: You can also set a `.env` file with `GEMINI_API_KEY` to avoid passing it via the command line.

### 5. Disable Desktop Notifications
```bash
python backend/app/main.py --no-notifier
```

### CLI Flags Summary

| Flag | Description |
|---|---|
| `--source <path\|0>` | Webcam device index (default: `0`) or path to video file |
| `--headless` | Run without GUI window |
| `--max-frames <N>` | Stop after N frames |
| `--generate-pdf` | Generate Gemini AI + PDF report on exit |
| `--api-key` | Gemini API Key for PDF generation |
| `--no-notifier` | Disable desktop/audio notifications |
| `--models-dir` | Custom directory for MediaPipe `.task` files |
| `--config-dir` | Custom directory for policy JSON files |
| `--calib-dir` | Custom directory for calibration JSON files |

---

## 🧪 Running Automated Tests

Run the complete test suite with `pytest`:
```bash
pytest
```

To run specific test modules:
- Distance rules: `pytest tests/test_distance.py`
- Head pose thresholds: `pytest tests/test_pitch_yaw.py`
- Shoulder tilt: `pytest tests/test_shoulder.py`
- Temporal persistence: `pytest tests/test_temporal_persistence.py`
- Configuration loader: `pytest tests/test_config_loader.py`
- Integration pipeline: `pytest tests/test_integration_pipeline.py`
- New wellness features: `pytest tests/test_new_features.py`

---

## ⚡ v2.1 Advanced Features

| Feature | Module | Description |
|---|---|---|
| **EMA Metric Smoothing** | `pipeline.py` | Exponential Moving Average ($\alpha = 0.70$) filters single-frame jitter on pitch, yaw, roll, shoulder tilt, and distance. |
| **Neutral Shoulder Calibration** | `manager.py` | Supports personal neutral shoulder tilt offset in reference profile. |
| **Smart Forward Lean Baseline** | `forward_lean.py` | Baseline only collected when distance is in the SAFE zone (45–75 cm). |
| **Desktop & Audio Alerts** | `notifier.py` | OS toast + audio when NON-SAFE persists ≥ 10s (30s cooldown). |
| **Session Health Report** | `reporter.py` | Posture score %, time distribution, top violations → `session_summary.txt`. |
| **Frame Telemetry Logger** | `logger.py` | JSONL log of every frame's metrics, status, and alerts. |
| **Groq AI PDF Reports** | `ai_insights.py`, `pdf_generator.py` | LLM-powered analysis with Matplotlib charts and ReportLab PDF. |

---

## ⚠️ Known Limitations

1. **Laptop Lid Angle**: Laptop lid tilt cannot be reliably determined from built-in webcam view.
2. **Lighting Sensitivity**: Extremely low light environments may reduce MediaPipe landmark detection confidence.
3. **Single-User Target**: System is calibrated for one seated user directly facing the screen. Multiple faces in view are not tracked simultaneously.
4. **Gemini API Key Required**: AI-powered PDF reports require a valid Gemini API key.
