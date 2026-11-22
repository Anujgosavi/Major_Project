# Mid-Semester Project Review Presentation
## Title: AI Ergonomics & Digital Wellness Monitoring System

---

## 👥 Project Team & Responsibility Matrix

| Team Member | Assigned Sections / Slide Responsibilities |
| :--- | :--- |
| **Siddhesh (Presenter)** | **Problem Statement, Approach & ML Model Evolution (Side-View vs. Front-Camera), Methodology / Work Flow, Tech Stack, Phase-wise Distribution** |
| **Asmita** | Project Objectives & Major System Modules |
| **Anuj** | System Architecture & Network Streaming Block Diagram |

---

# ============================================================
# SECTION 1: SIDDHESH'S SLIDES (PRIMARY FOCUS)
# ============================================================

## 📌 Slide 1: Problem Statement (PS)
### *Title: The Ergonomic & Digital Wellness Crisis in Modern Computing*

* **The Modern Workplace Problem**:
  * Knowledge workers and students spend **8–12 hours daily** in front of computer screens.
  * Over **60% of computer users** suffer from Computer Vision Syndrome (CVS), Forward Head Posture ("Text Neck"), and chronic musculoskeletal disorders (MSDs) in neck and shoulders.
  * Slouching and improper screen distance silently cause long-term spinal misalignment and severe eye fatigue.

* **Existing Solutions & Their Limitations**:
  * **Wearable Ergonomic Sensors**: Require physical hardware, charging, and cause user discomfort.
  * **Static Posture Timers**: Lack intelligence; trigger annoying alerts regardless of actual posture.
  * **Specialized Side-Camera Setup**: Require secondary external webcams or tripods positioned at 90° angles to the desk, creating severe user setup friction.

* **Our Proposed Solution**:
  * A **non-intrusive, real-time AI Ergonomics Monitor** using the **existing built-in laptop webcam**.
  * Tracks 3D head pose, slouching, screen distance, eye blink rate, and lighting strain in real time.
  * Powered by sub-100ms WebRTC streaming, intelligent temporal persistence safety rules, and automated AI health reports.

---

## 🔬 Slide 2: Approach & Model Evolution (Side-View ML Model vs. Front-Camera Paradigm)
### *Title: System Approach: From Side-View Machine Learning to Front-Camera Computer Vision*

> **Key Context**: During initial research & development, our team explored and implemented a **side-view profile posture classification model** before evolving into our production **front-facing laptop webcam architecture**.

### 1. Initial Approach: Standalone Side-View ML Posture Classifier
* **Concept & Setup**:
  * Positioned a camera at the **side profile (90° angle)** of the user's desk setup to capture full lateral torso and neck profile views.
* **Dataset & Feature Extraction**:
  * Collected and annotated side-profile posture images (Good Posture vs. Slouched / Forward Head Posture).
  * Extracted upper-body skeletal landmarks (Ear, Shoulder, Hip, C terminus angle, Neck inclination angle $\theta_{\text{neck}}$, Torso inclination angle $\theta_{\text{torso}}$).
* **ML Model Training & Results**:
  * Trained Supervised ML Classifiers (**SVM / Random Forest / Logistic Regression**) on extracted geometric feature vectors.
  * Achieved high offline classification accuracy (~90-93%) on clean side-profile image datasets.
* **Practical Drawbacks & Limitations Identified**:
  1. **High User Friction**: Required external tripods or second webcams positioned at the side of the desk—impractical for daily laptop users.
  2. **Lateral Occlusion**: Arms, clothing, and office furniture frequently blocked side keypoints.
  3. **Inflexibility**: Required retraining/fine-tuning ML models for varying body types and side angles.

### 2. Paradigm Shift: Front-Camera Geometric & Computer Vision Pipeline
* **The Breakthrough**: Transitioned to **front-facing built-in laptop webcam** (zero extra hardware needed).
* **Mathematical Inverse Modeling & High-Density Landmark Mesh**:
  * Utilized MediaPipe 3D Face Mesh (**478 landmarks**) & Upper-Body Pose (**33 landmarks**).
  * Derived physical distance ($d = \frac{a}{w_{\text{norm}} - b}$) using facial landmark width inverse curves calibrated on real distance measurements.
  * Extracted 3D Euler angles (Pitch, Yaw, Roll) via facial transformation matrices.
  * Designed Exponential Moving Average (EMA) low-pass filtering to remove sensor noise without model training latency.

---

## 🔄 Slide 3: Methodology & Analytical Work Flow
### *Title: Step-by-Step Data Processing & Decision-Engine Work Flow*

> ⚠️ **Note for Reviewers**: *Methodology / Work Flow details the sequential mathematical frame-by-frame data transformation pipeline, whereas System Architecture details the software component blocks.*

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Live Frame Acquisition                                           │
│  • Built-in Webcam captures raw video frames at 30 FPS                   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Frame Preprocessing & EMA Low-Pass Filtering                    │
│  • Convert BGR to RGB; apply Exponential Moving Average (α = 0.70)       │
│  • Eliminates high-frequency jitter while preserving rapid movements     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 3: High-Density Landmark Extraction                                │
│  • MediaPipe FaceLandmarker: 478 3D mesh points + Iris landmarks        │
│  • MediaPipe PoseLandmarker: 33 upper-body skeletal keypoints           │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 4: Feature & Metric Computation (Mathematical Engine)             │
│  • Distance Estimation: Inverse distance formula d = a / (w_norm - b)   │
│  • 3D Head Orientation: Euler angles (Pitch, Yaw, Roll) from rotation matrix
│  • Shoulder Tilt: θ = arctan(Δy / |Δx|)                                │
│  • Slouch Ratio: Nose-to-shoulder vertical distance / shoulder width     │
│  • Eye Aspect Ratio (EAR): Adaptive 80th percentile rolling baseline     │
│  • Ambient Luma: YCrCb luminance average (Dark room / Glare detection)  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 5: Temporal Persistence State Machine (Safety Evaluation)           │
│  • Evaluates instant metric thresholds (SAFE / WARNING / NON-SAFE)       │
│  • Enforces hysteresis time windows:                                    │
│    - SAFE ──► WARNING requires continuous violation ≥ 2.0 seconds       │
│    - WARNING/SAFE ──► NON-SAFE requires continuous violation ≥ 5.0 seconds│
│    - Recovery to SAFE is INSTANT (prevents false alarms and UI jitter)  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 6: Multi-Channel Output & Action Execution                         │
│  • Sub-100ms WebRTC peer connection video stream to React Dashboard     │
│  • Sanitized JSON REST API response (/api/status)                        │
│  • JSONL Frame Telemetry logging (logs/) for session analytics          │
│  • Trigger desktop audio chimes & break toast notifications             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Slide 4: Technology Stack
### *Title: Technology & Tooling Matrix*

| Domain | Technology / Library | Purpose & Justification |
| :--- | :--- | :--- |
| **Computer Vision & AI** | `Google MediaPipe` (Face Mesh + Pose) | 478 3D face points & 33 pose landmarks; lightweight GPU/CPU inference |
| | `OpenCV` & `NumPy` | Frame manipulation, color space conversion (YCrCb), matrix math |
| | `Scipy` | Curve fitting for facial width distance calibration models |
| **Streaming Backend** | `Python 3.12` & `Flask` | Lightweight REST API server for state management & WebRTC endpoints |
| | `aiortc` & `av` (PyAV) | WebRTC peer-to-peer video streaming protocol delivering **sub-100ms latency** |
| **Web Frontend** | `React 19` & `JavaScript ES6+` | Modern web application dashboard framework |
| | `Lucide React` & `Vanilla CSS3` | Custom responsive dark glassmorphism styling and UI components |
| **Telemetry & AI Analytics**| `JSONL` Telemetry Logger | High-frequency frame-by-frame metric logging without database overhead |
| | `Google Gemini / Groq LLM` | Generative AI health report synthesis and personalized ergonomic recommendations |
| | `ReportLab` & `Matplotlib` | Dynamic PDF generation with trend visualizations (`Ergonomic_Report.pdf`) |

---

## 📅 Slide 5: Phase-Wise Distribution & Timeline
### *Title: Project Roadmap & Execution Plan*

```
Phase 1: Research & Side-View Experimentation (COMPLETED)
  ├── Problem identification & literature survey
  ├── Dataset collection of side-profile posture images
  └── Feature extraction & SVM/RandomForest baseline training

Phase 2: Core Vision Engine & Front-Camera Migration (COMPLETED)
  ├── Migration to MediaPipe FaceLandmarker (478 pts) & PoseLandmarker (33 pts)
  ├── Mathematical formulation for distance, pitch, yaw, shoulder tilt, slouch
  └── EMA low-pass filtering and calibration inverse distance curves

Phase 3: Real-Time WebRTC Streaming & Persistence Engine (COMPLETED)
  ├── Implementation of sub-100ms WebRTC backend via aiortc & Flask
  ├── Temporal persistence state machine (2s WARNING / 5s NON-SAFE thresholds)
  └── Digital wellness features: Blink EAR rate, Squint, Screen stare, Ambient luma

Phase 4: Web Dashboard UI & React Integration (COMPLETED)
  ├── React 19 web application development (Live Monitor, Dashboard, Reports)
  ├── Sub-100ms WebRTC <video> mounting & compact 2-column live metrics grid
  └── REST API synchronization, proxy routing, and authentication flows

Phase 5: Telemetry, AI Report Generation & Final Testing (IN PROGRESS / CURRENT)
  ├── Session JSONL telemetry logging
  ├── Automated LLM (Gemini/Groq) insights & PDF report generation (ReportLab)
  └── Pytest suite validation (22 unit & pipeline test cases passing)

Phase 6: Long-Term Session Tracking & Deployment (PLANNED FOR FINAL SEMESTER)
  ├── Multi-session database persistence & user trends over weeks/months
  ├── Cross-platform edge desktop packaging (Electron / Desktop service integration)
  └── User field trials & clinical ergonomic validation
```

---

# ============================================================
# SECTION 2: ASMITA'S SLIDES (OBJECTIVES & MODULES)
# ============================================================

## 🎯 Slide 6: Project Objectives
### *Title: Core Project Objectives & Goals*

1. **Non-Intrusive Real-Time Posture Detection**:
   * Monitor user posture continuously using a single standard laptop webcam without requiring specialized wearable hardware or side-profile camera setups.
2. **Sub-100ms Streaming & Low Overhead**:
   * Implement real-time video streaming with sub-100ms latency to deliver immediate visual feedback without lagging or high CPU/GPU load.
3. **Flicker-Free Temporal Safety Engine**:
   * Develop a state machine to eliminate false positives and alert fatigue by requiring posture violations to persist continuously before escalating alerts.
4. **Comprehensive Digital Wellness Monitoring**:
   * Go beyond basic posture to monitor eye strain (blink rate, squinting, screen stare), ambient lighting conditions, and enforce the 20-20-20 visual break rule.
5. **Actionable AI Health Analytics**:
   * Aggregate daily telemetry into personalized, AI-generated health reports with dynamic PDF summaries and targeted posture improvement recommendations.

---

## 🧩 Slide 7: Major Modules Overview
### *Title: Major System Modules*

1. **Computer Vision & Feature Engine**:
   * Extracts 3D facial mesh, iris landmarks, and shoulder alignment keypoints. Computes normalized metrics (Distance, Pitch, Yaw, Shoulder Tilt, Slouch).
2. **Temporal Safety & Persistence Engine**:
   * Evaluates metrics against clinical ergonomic thresholds. Implements a temporal window state machine (`SAFE`, `WARNING`, `NON-SAFE`) to ensure alert stability.
3. **WebRTC Streaming & REST API Service**:
   * `aiortc`-powered media pipeline streaming RTP video tracks to HTML5 video components alongside Flask endpoints for live status JSON feeds.
4. **React 19 Web Dashboard**:
   * Modern dark-themed dashboard providing live camera feeds, 2-column metric cards, posture history donuts, score cards, and session logs.
5. **Digital Wellness & Break Alert Suite**:
   * Tracks Eye Aspect Ratio (EAR) blinks, gaze fixations, and room glare while managing timed 20-20-20 visual rest and hydration overlays.
6. **Telemetry & AI PDF Report Generator**:
   * Logs frame telemetry to JSONL, passes session metrics to Gemini/Groq LLMs, and formats downloadable ReportLab PDF summary reports.

---

# ============================================================
# SECTION 3: ANUJ'S SLIDES (SYSTEM ARCHITECTURE)
# ============================================================

## 🏗️ Slide 8: System Architecture
### *Title: High-Level Hardware & Software System Architecture*

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
 └──────────────────────────────────────────┘             └──────────────────────────────────────────┘
                  │
                  ▼
 ┌──────────────────────────────────────────┐
 │      Session & Telemetry Reports         │
 │  • JSONL Frame Telemetry (logs/)         │
 │  • Gemini / Groq AI Insights             │
 │  • ReportLab Multi-Page PDF Report       │
 └──────────────────────────────────────────┘
```

---

## 📡 Slide 9: WebRTC Streaming & Communication Layer
### *Title: WebRTC Peer Connection & REST API Architecture*

* **Why WebRTC Over Standard HTTP/MJPEG**:
  * **Latency Reduction**: Standard HTTP video streams (MJPEG) buffer frames, causing 800ms–1500ms delay. WebRTC uses UDP/RTP streaming to achieve **sub-100ms real-time playback**.
  * **Hardware Acceleration**: Video is rendered directly in native HTML5 `<video>` elements using GPU acceleration rather than CPU-intensive canvas repainting.
* **Handshake & Signaling Protocol**:
  1. React Client initiates `RTCPeerConnection` with a `recvonly` video transceiver and generates an SDP Offer.
  2. Frontend sends SDP Offer to Flask backend via `POST /api/webrtc/offer`.
  3. Flask server mounts a custom `aiortc` `VideoStreamTrack` (fetching latest pipeline frames), generates an SDP Answer, and returns it.
  4. WebRTC peer connection is established; stream binds directly to `<video>` player.

---

# ============================================================
# SECTION 4: CURRENT WORK COMPLETED & SUMMARY
# ============================================================

## 📊 Slide 10: Current Work Completed (Mid-Sem Review Summary)

* ✅ **Full Vision Engine Operational**: Face Mesh (478 pts) and Pose (33 pts) landmark extraction running smoothly with EMA smoothing.
* ✅ **Calibrated Safety Metrics**: Screen Distance, Head Pitch/Yaw, Shoulder Tilt, Slouch Ratio, and Ambient Luma rules calibrated.
* ✅ **Sub-100ms WebRTC Pipeline**: Fully integrated `aiortc` backend streaming to React `<video>` element.
* ✅ **Temporal State Hysteresis**: Persistence engine active (2s WARNING, 5s NON-SAFE) preventing false alarms.
* ✅ **Complete Web Dashboard**: React 19 frontend functional with Live Monitor, Dashboard charts, Reports viewer, and Auth pages.
* ✅ **AI Telemetry & PDF Generation**: Frame telemetry logging, Gemini/Groq LLM analysis, and ReportLab PDF compilation validated.
* ✅ **Automated Test Suite**: 22 automated unit and integration tests passing (`run_tests.py`).

---

## 🎯 Slide 11: Conclusion & Future Roadmap

* **Summary**:
  * Successfully built an end-to-end, privacy-focused, real-time AI Ergonomics Monitor running entirely locally on user hardware.
  * Solved hardware setup friction by evolving from side-view ML models to a single front-facing webcam vision pipeline.
* **Next Steps for Final Semester**:
  1. Multi-session database storage and long-term posture trend analytics.
  2. Edge desktop application packaging (Electron / background tray agent).
  3. User study field validation & feedback iteration.
