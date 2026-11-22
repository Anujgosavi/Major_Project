# AI Ergonomics & Digital-Wellness Monitoring System

A comprehensive, real-time AI-powered ergonomic posture, screen distance, and digital-wellness monitor. Built with a **MediaPipe Face & Pose vision pipeline**, **temporal state machine policy enforcement**, an ultra-low-latency **WebRTC streaming & Flask REST API backend (`aiortc`)**, and a modern **React 19 dark-themed Web UI dashboard**.

---

## 🌟 System Architecture Overview

```
                        ┌───────────────────────────────────────────────┐
                        │              Built-in Webcam Frame            │
                        └───────────────────────┬───────────────────────┘
                                                │
                                                ▼
                        ┌───────────────────────────────────────────────┐
                        │      MediaPipe Vision Pipeline (EMA Smoothed) │
                        │  • FaceLandmarker (478 pts) • Pose (33 pts)   │
                        │  • Distance Model           • Iris & Gaze     │
                        └───────────────────────┬───────────────────────┘
                                                │
                                                ▼
                        ┌───────────────────────────────────────────────┐
                        │     Temporal Persistence Safety Engine        │
                        │   SAFE ──(2s)──► WARNING ──(5s)──► NON-SAFE   │
                        └───────────────────────┬───────────────────────┘
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
┌──────────────────────────────────────────┐             ┌──────────────────────────────────────────┐
│     Flask & WebRTC Backend (aiortc)      │             │         React 19 Frontend Web UI         │
│  • POST /api/webrtc/offer (Low-latency)  │◄───────────►│  • Live Monitor (<video> WebRTC stream)  │
│  • GET  /api/status       (Live stats)   │             │  • Compact 2-Column Live Metrics Sidebar │
│  • POST /api/start        (Start pipeline│             │  • Dashboard & Ergonomic Metrics         │
│  • POST /api/stop         (Stop & PDF)   │             │  • Reports & Session History Viewer      │
│  • POST /api/dismiss_alert               │             │  • 20-20-20 & Hydration Toast Alerts     │
│  • GET  /video_feed       (MJPEG fallback│             │  • Authentication (Login / Signup)       │
└──────────────────────────────────────────┘             └──────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│      Session & Telemetry Reports         │
│  • Local JSONL Frame Telemetry (logs/)   │
│  • MongoDB 1-second Telemetry Rollups    │
│  • Gemini / Groq AI Insights             │
│  • ReportLab Multi-Page PDF Report       │
└──────────────────────────────────────────┘
```

---

## 🎯 System Capabilities

### 1. Ultra-Low-Latency WebRTC Video Streaming
- **WebRTC Pipeline (`aiortc` + `av`)**: Uses direct peer-to-peer real-time RTP video tracks streamed directly to native HTML5 `<video>` elements, cutting stream delay from ~1000ms down to **sub-100ms** with zero buffer backlog.
- **Hardware Acceleration**: Client-side GPU-accelerated decoding with minimal browser CPU overhead.

### 2. Primary Posture & Ergonomic Safety
- **Screen Distance (cm)**: Calibrated inverse distance model ($d = a / (w - b)$) with EMA smoothing.
- **Head Pitch & Yaw (°)**: Euler angle rotation matrix deviations from calibrated neutral baseline.
- **Shoulder Alignment / Tilt (°)**: 2D shoulder keypoint angle with personal neutral offset compensation.
- **Slouch / Neck Compression**: Ratio of vertical nose-to-shoulder distance to shoulder width.
- **Temporal Persistence State Machine**: Eliminates UI flicker (~2s threshold for `WARNING`, ~5s for `NON-SAFE`, instant recovery to `SAFE`).

### 3. Digital Wellness & Eye-Strain Monitoring
- **Adaptive Blink Rate**: Rolling 60-second window blink tracking via live 80th-percentile EAR baseline.
- **Sustained Squinting**: Detects partial eye closures in the 30%–70% EAR range persisting > 20% of 60s.
- **Screen Fixation / Stare**: Tracks iris micro-saccades to catch motionless gaze > 40% of 60s.
- **Forward Lean (Turtle-Neck)**: Distance-gated session baseline tracking, triggering when face width increases $\ge 20\%$.
- **Ambient Brightness Strain**: YCrCb luma analysis detecting dark room, bright glare, and backlight silhouette conditions.
- **20-20-20 Rule**: Periodic visual rest break alerts (every 20 minutes look 20 feet away for 20 seconds).
- **Hydration Reminders**: Automated reminders with on-screen actions.

### 4. Web Dashboard & User Experience
- **Live Monitor Page**: Side-by-side view with WebRTC live stream and a scroll-free **2-column compact Live Metrics grid**.
- **Interactive Notifications**: Global break and hydration toasts with sound alerts and 60-second auto-dismiss.
- **Dashboard Overview**: Score trends, weekly posture distributions, session logs, and system summary cards.
- **Session Reports**: Historical analytics with filtering, score indicators, and downloadable PDF summaries.
- **Dark Glassmorphism Theme**: Custom modular CSS with smooth animations and responsive mobile layouts.

### Telemetry Storage Strategy
- Every processed frame is kept in the local session JSONL file while a session is
  running, so the PDF generator can render detailed time-series charts.
- MongoDB stores one asynchronous aggregate document per second, including sample
  count, averages, dominant status, and reason counts. This keeps session history
  and analytics useful without storing a document for every camera frame.
- The generated PDF is stored separately in MongoDB GridFS after report generation.

---

## 📐 Ergonomic Safety Policy

| Measurement | `SAFE` | `WARNING` (Requires 2s persistence) | `NON-SAFE` (Requires 5s persistence) |
| :--- | :--- | :--- | :--- |
| **Distance** | 45 – 75 cm | 40–45 cm or 75–85 cm | < 40 cm or > 85 cm |
| **Head Pitch Deviation** | < 15° | $\ge 15^\circ$ | $\ge 30^\circ$ |
| **Head Yaw Deviation** | < 15° | $\ge 15^\circ$ | $\ge 30^\circ$ |
| **Shoulder Tilt Deviation** | < 10° | $\ge 10^\circ$ | $\ge 20^\circ$ |
| **Slouch Ratio** | > 0.65 | $\le 0.65$ | $\le 0.55$ |

---

## 📁 Repository Structure

```
Major_Project/
├── backend/
│   ├── api/
│   │   └── server.py                # Flask REST API & WebRTC (aiortc) streaming server
│   ├── app/
│   │   ├── main.py                  # Standalone CLI / OpenCV runner
│   │   ├── annotator.py             # Frame annotation, HUD overlays, alerts
│   │   ├── notifier.py              # Desktop toast notifications & audio chimes
│   │   └── reporter.py              # Session report summary builder
│   ├── vision/
│   │   ├── pipeline.py              # FrontCameraPipeline with EMA smoothing
│   │   ├── face.py                  # Face mesh (478 pts), iris, Euler angles
│   │   ├── pose.py                  # Pose landmarks & shoulder tilt
│   │   ├── distance.py              # Inverse distance calculation
│   │   ├── blink.py                 # Adaptive EAR blink detector
│   │   ├── squint.py                # Squint duration detector
│   │   ├── gaze_fixation.py         # Eye motionless stare detection
│   │   ├── forward_lean.py          # Session-gated turtle-neck detector
│   │   └── brightness.py            # YCrCb ambient luma analyzer
│   ├── safety/
│   │   ├── rules.py                 # Single-frame safety rules
│   │   ├── temporal.py              # Temporal persistence state machine
│   │   └── engine.py                # SafetyEngine wrapper
│   ├── telemetry/
│   │   └── logger.py                # Local frame log + compact MongoDB rollups
│   └── reports/
│       ├── ai_insights.py           # Gemini / Groq LLM API insights
│       └── pdf_generator.py         # ReportLab multi-page PDF generator
│
├── frontend/                        # React 19 Web Dashboard
│   ├── public/                      # Static assets & HTML template
│   ├── src/
│   │   ├── components/              # Navbar, Sidebar, Footer, Layout, HeroSection
│   │   ├── context/                 # AuthContext & state management
│   │   ├── pages/
│   │   │   ├── Dashboard.js/.css    # Metrics, charts, and summary cards
│   │   │   ├── LiveFeed.js/.css     # WebRTC Live camera monitor with 2-col sidebar
│   │   │   ├── Reports.js/.css      # Session analytics & PDF reports
│   │   │   ├── LandingPage.js/.css  # Product landing page
│   │   │   ├── Login.js/.css        # User sign-in
│   │   │   └── Signup.js/.css       # Account registration
│   │   ├── setupProxy.js            # Webpack proxy routing (/api & /video_feed)
│   │   └── App.js                   # Route definitions
│   └── package.json                 # Node.js dependencies
│
├── models/                          # MediaPipe task models (.task files)
├── scripts/
│   └── download_models.py           # Automated model downloader
├── tests/                           # Pytest automated test suite (22 tests)
├── backend/
│   └── generate_ai_pdf_report.py    # Standalone AI PDF report generator
├── requirements.txt                 # Backend Python dependencies (includes aiortc, av, flask)
└── md_files/                        # Centralized Markdown and LaTeX documentation
    ├── README.md                    # Main project documentation
    └── Project_Report.tex           # Detailed LaTeX project report
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.9+**
- **Node.js 18+ & npm**
- Built-in or USB Webcam

---

### 2. Backend Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download MediaPipe Models**:
   ```bash
   python scripts/download_models.py
   ```

3. **Start the Flask & WebRTC API Server**:
   ```bash
   python backend/api/server.py
   ```
   *The server starts on `http://127.0.0.1:5000`.*

---

### 3. Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node dependencies**:
   ```bash
   npm install
   ```

3. **Start the React Web Dashboard**:
   ```bash
   npm start
   ```
   *The web app opens automatically at `http://localhost:3000`.*

---

### 4. Running Standalone CLI / OpenCV Window (Optional)
If you prefer running without the web UI:
```bash
# Standard live monitoring
python backend/app/main.py

# With automatic AI PDF report on exit
python backend/app/main.py --generate-pdf
```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/webrtc/offer` | Handles WebRTC peer connection SDP handshake for real-time video streaming. |
| `GET` | `/api/status` | Returns running state, PDF generation status, and sanitized live stats. |
| `POST` | `/api/start` | Starts the vision pipeline thread and camera capture. |
| `POST` | `/api/stop` | Stops monitoring and triggers PDF report generation. |
| `POST` | `/api/dismiss_alert` | Dismisses active `BREAK` or `WATER` notifications (`{"alert_type": "BREAK"}`). |
| `GET` | `/video_feed` | Fallback multipart MJPEG video stream. |

---

## 🧪 Running Automated Tests

Run the full pytest suite:
```bash
pytest
```

Run specific test modules:
```bash
pytest tests/test_distance.py
pytest tests/test_pitch_yaw.py
pytest tests/test_shoulder.py
pytest tests/test_temporal_persistence.py
pytest tests/test_new_features.py
```

---

## 📄 License & Credits
Built for AI Ergonomics & Posture Safety Research using Google MediaPipe, aiortc, Flask, and React.
