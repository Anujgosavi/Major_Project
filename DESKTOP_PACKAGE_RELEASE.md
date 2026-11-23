# Digital Wellness Assistant — Windows Desktop Package Release

## 📦 Package Summary

| Property | Details |
| :--- | :--- |
| **Application Name** | **Digital Wellness Assistant** |
| **Version** | `1.0.0` |
| **Target OS** | Windows 10 & 11 (64-bit / x64) |
| **Installer Type** | Windows NSIS Setup Executable (`.exe`) |
| **Installer Size** | ~715 MB (Self-contained, includes Python 3.11, MediaPipe, OpenCV, Electron, React UI) |
| **Prerequisites** | **None** (No Python, No Node.js, No OpenCV, No npm/pip required on target PC) |
| **Installer File** | `Major_Project\Digital Wellness Assistant Setup 1.0.0.exe` |
| **Output Directory** | `Major_Project\desktop\dist-installer\` |
| **SHA-256 Checksum** | `26EA3811D8CEDC4CD24DA941521C68EB73AD80531C9061726BC3746E92422A47` |

---

## 🏗️ Desktop Architecture

```
                                  [ User Double-Clicks Setup.exe ]
                                                 │
                                                 ▼
                                [ Installs Desktop App via NSIS ]
                                                 │
                                                 ▼
                        ┌─────────────────────────────────────────────────┐
                        │      Electron Desktop Shell (Chromium / C++)    │
                        │  • Manages desktop window & splash screen       │
                        │  • Automatically manages Python subprocess       │
                        │  • Auto-approves local camera permissions       │
                        │  • Zero-leak process termination on exit        │
                        └───────────────┬─────────────────┬───────────────┘
                                        │                 │
                Starts & monitors on    │                 │ Loads same-origin UI
                http://127.0.0.1:5000   │                 │ via HTTP GET /
                                        ▼                 ▼
             ┌───────────────────────────────────┐      ┌───────────────────────────────────┐
             │    Frozen Python AI Backend       │◄────►│     React 19 Dashboard Web UI     │
             │   (PyInstaller onedir bundle)     │      │  (Served directly from backend)   │
             │  • MediaPipe Face & Pose Tasks    │      │  • WebRTC Live Monitor (<video>)  │
             │  • Real-time OpenCV Video Capture │      │  • 2-Column Metrics Dashboard     │
             │  • aiortc Low-Latency WebRTC      │      │  • Session Reports & PDF Downloader│
             │  • Safety State Machine Engine    │      │  • 20-20-20 & Hydration Alerts    │
             │  • ReportLab / Matplotlib Reports │      │  • Glassmorphism Dark Theme       │
             └───────────────────────────────────┘      └───────────────────────────────────┘
```

---

## 🔒 Security & Performance Hardening

1. **Localhost-Only Binding**: The backend Flask server binds strictly to `127.0.0.1` (never `0.0.0.0`), preventing LAN interception.
2. **Same-Origin Architecture**: The backend serves the compiled React production SPA directly. All `/api`, WebRTC signaling, and video streams share the exact same origin, eliminating CORS issues and proxy delays.
3. **Electron Security Standards**:
   - `nodeIntegration: false`
   - `contextIsolation: true`
   - `sandbox: true`
   - External link navigation restricted and delegated to the system default browser.
4. **Clean Process Teardown**: Closing the desktop window sends a graceful `/api/shutdown` request to the backend and triggers Windows `taskkill /T /F` to guarantee no zombie camera captures or background Python processes are orphaned.
5. **Standard User Permissions**: Logs and reports are written to `%LOCALAPPDATA%\DigitalWellness\`, allowing standard non-admin Windows users to run the application without permission errors.

---

## 🚀 How End Users Install & Run

1. **Download**:
   Distribute `Digital Wellness Assistant Setup 1.0.0.exe` to end users.
2. **Install**:
   - Double-click `Digital Wellness Assistant Setup 1.0.0.exe`.
   - *(Optional note for unsigned university releases)*: If Windows SmartScreen appears ("Windows protected your PC"), click **"More info"** and then **"Run anyway"**.
   - Choose install directory and click **Install**.
3. **Run**:
   - Launch from the Desktop shortcut or Start Menu: **Digital Wellness Assistant**.
   - The application displays the startup splash window while initializing the AI engine, then automatically presents the main dashboard.
   - Click **"Start Monitor"** on the Live Feed page to begin AI ergonomics tracking!
