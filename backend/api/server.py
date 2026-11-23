"""
Flask API Server for AI Ergonomics Monitor.
Provides REST endpoints to control the vision pipeline from the React frontend.
"""

import sys
import time
import threading
import math
import os
import argparse
from pathlib import Path

import io
import datetime
import cv2
import numpy as np
from flask import Flask, Response, jsonify, request, send_file, send_from_directory, g
from flask_cors import CORS
import asyncio
import uuid
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from av import VideoFrame

def _safe_float(val, default=0.0, ndigits=1):
    try:
        if val is None:
            return default
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return round(f, ndigits)
    except (TypeError, ValueError):
        return default

def sanitize_for_json(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    return obj

# Ensure Major_Project root is in sys.path before package imports
_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Import centralized project paths
from backend.paths import PROJECT_ROOT, REPORTS_DIR, LOGS_DIR, FRONTEND_BUILD_DIR

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv()

from backend.vision.pipeline import FrontCameraPipeline
from backend.safety.engine import SafetyEngine
from backend.app.annotator import annotate_frame
from backend.app.notifier import PostureNotifier
from backend.app.reporter import SessionReporter
from backend.telemetry.logger import TelemetryLogger
from backend.auth.routes import auth_bp, require_auth
from backend.db.mongo import sessions_col, get_fs
from backend.api.sessions_routes import sessions_bp

app = Flask(
    __name__,
    static_folder=str(FRONTEND_BUILD_DIR / "static"),
    static_url_path="/static"
)
CORS(app, supports_credentials=True)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(sessions_bp, url_prefix='/api/sessions')

# ---------------------------------------------------------------------------
# Shared State
# ---------------------------------------------------------------------------
class MonitorState:
    def __init__(self):
        self.running = False
        self.stopping = False
        self.lock = threading.Lock()
        self.thread = None
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.show_measurements = False
        # Session stats exposed to the frontend
        self.session_stats = {}
        self.pdf_path = None
        self.rule_20_active = False
        self.water_active = False
        self.last_break_time = 0
        self.last_water_time = 0
        self.pdf_generating = False
        self.user_id = None
        self.session_id = None
        self.latest_frame_time = 0.0

state = MonitorState()

# ---------------------------------------------------------------------------
# WebRTC Loop and Track
# ---------------------------------------------------------------------------
webrtc_loop = asyncio.new_event_loop()
def _run_webrtc_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
threading.Thread(target=_run_webrtc_loop, args=(webrtc_loop,), daemon=True).start()

pcs = set()

class MonitorVideoTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        frame = None
        while True:
            if not state.running and state.latest_frame is None:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                break
            with state.frame_lock:
                if state.latest_frame is not None:
                    frame = state.latest_frame.copy()
                    break
            await asyncio.sleep(0.005)

        # aiortc handles BGR conversion
        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame

def _monitor_loop():
    """Background thread that runs the vision pipeline."""
    print("=" * 65)
    print("  AI Ergonomics — Vision Pipeline Thread Starting")
    print("=" * 65)

    pipeline = FrontCameraPipeline()
    safety_engine = SafetyEngine(reference_profile=pipeline.reference)
    notifier = PostureNotifier(enabled=True)
    reporter = SessionReporter()
    telemetry_logger = TelemetryLogger(
        session_id=state.session_id,
        user_id=state.user_id,
    )

    # Open camera with zero buffer latency settings
    if sys.platform.startswith('win'):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[!] Error: Unable to open webcam.")
        with state.lock:
            state.running = False
        return

    # DirectShow / Camera buffer optimization: set 640x480 & buffer size = 1 to eliminate frame backlog
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    start_time = time.time()
    frame_count = 0

    # 20-20-20 and water tracking
    start_time = time.time()
    
    with state.lock:
        state.last_break_time = start_time
        state.last_water_time = start_time
        state.rule_20_active = False
        state.water_active = False

    print("[+] Vision pipeline running with sub-80ms zero-latency buffer settings...")

    try:
        while not state.stop_event.is_set() and cap.isOpened():
            # Discard buffered frames and retrieve the latest available frame.
            # One extra grab is enough for DirectShow's single-frame buffer.
            grabbed = False
            for _ in range(2):
                if not cap.grab():
                    break
                grabbed = True
            if not grabbed:
                break
            ret, frame = cap.retrieve()
            if not ret or frame is None:
                ret, frame = cap.read()

            if not ret or frame is None:
                break

            frame_count += 1
            current_time = time.time()
            frame = cv2.flip(frame, 1)

            # Process
            t0 = time.perf_counter()
            result = pipeline.process_frame(frame, timestamp=current_time)
            inference_ms = (time.perf_counter() - t0) * 1000.0

            decision = safety_engine.evaluate(result)
            reporter.update(result, decision)
            telemetry_logger.log_frame(result, decision)

            # Notifications
            if decision.get("final_status") == "NON-SAFE" and decision.get("persisted_duration", 0) >= 10.0:
                notifier.notify_non_safe(
                    duration_sec=decision.get("persisted_duration", 10.0),
                    reasons=decision.get("reasons", []),
                    timestamp=current_time
                )

            b_strain = result.get("brightness_strain", "ok")
            if b_strain != "ok":
                notifier.notify_brightness(b_strain, timestamp=current_time)

            # 20-20-20 Rule (Demo: 2 min interval, 1 min break)
            time_since_break = current_time - state.last_break_time
            if time_since_break >= 120.0:
                if not state.rule_20_active:
                    with state.lock:
                        state.rule_20_active = True
                    notifier.notify_20_20_20(timestamp=current_time)
            if state.rule_20_active and (time_since_break >= 180.0):
                with state.lock:
                    state.rule_20_active = False
                    state.last_break_time = current_time

            rem_sec = max(0, int(120.0 - time_since_break))
            countdown_str = f"{rem_sec//60:02d}:{rem_sec%60:02d}"

            # Water (45 mins interval, 1 min active)
            time_since_water = current_time - state.last_water_time
            if time_since_water >= 2700.0:
                if not state.water_active:
                    with state.lock:
                        state.water_active = True
                    notifier.notify_water()
            if state.water_active and (time_since_water >= 2760.0):
                with state.lock:
                    state.water_active = False
                    state.last_water_time = current_time

            # Annotate
            annotated = annotate_frame(
                frame, result, decision,
                inference_ms=inference_ms,
                rule_20_20_20_active=state.rule_20_active,
                countdown_str=countdown_str,
                show_measurements=state.show_measurements
            )

            # Determine UI alerts
            ui_alerts = []
            if state.rule_20_active:
                ui_alerts.append("BREAK")
            if state.water_active:
                ui_alerts.append("WATER")
            # Posture only plays sound (via notifier), no on-screen UI overlay

            # Push frame for MJPEG streaming
            with state.frame_lock:
                state.latest_frame = annotated.copy()
                state.latest_frame_time = current_time

            # Update live stats for frontend polling
            elapsed = current_time - start_time
            state.session_stats = {
                "frame_count": frame_count,
                "elapsed_sec": _safe_float(elapsed, 0.0, 1),
                "status": decision.get("final_status", "UNKNOWN"),
                "distance_cm": _safe_float(result.get("estimated_distance_cm"), 0.0, 1),
                "pitch_deg": _safe_float(result.get("head_pitch_deg"), 0.0, 1),
                "yaw_deg": _safe_float(result.get("head_yaw_deg"), 0.0, 1),
                "shoulder_deg": _safe_float(result.get("shoulder_tilt_deg"), 0.0, 1),
                "eye_open": _safe_float(result.get("mean_eye_open_ratio"), 0.0, 3),
                "total_blinks": int(result.get("blink_count") or 0) if not (isinstance(result.get("blink_count"), float) and math.isnan(result.get("blink_count"))) else 0,
                "blink_rate": _safe_float(result.get("blink_rate_per_min"), 0.0, 1),
                "slouch_ratio": _safe_float(result.get("slouch_ratio"), 0.0, 2),
                "countdown": countdown_str,
                "inference_ms": _safe_float(inference_ms, 0.0, 1),
                "stream_age_ms": _safe_float((time.time() - state.latest_frame_time) * 1000.0, 0.0, 1),
                "active_alerts": ui_alerts
            }

            if frame_count % 30 == 0:
                dist_str = f"{result.get('estimated_distance_cm', 0):.1f}cm" if result.get('face_detected') else "N/A"
                print(f"Frame {frame_count:4d} | Status: {decision['final_status']:<8} | Dist: {dist_str}")

    finally:
        cap.release()
        pipeline.close()
        telemetry_logger.close()
        with state.frame_lock:
            state.latest_frame = None
        with state.lock:
            state.running = False
            state.stopping = False
            state.pdf_generating = True

        elapsed = time.time() - start_time

        print(f"\n[+] Shutdown. {frame_count} frames in {elapsed:.2f}s.")
        print("\n" + reporter.generate_report())

        # --- Auto-generate PDF ---
        print("\n[..] Generating Gemini AI & PDF Ergonomic Report...")
        pdf_gridfs_id = None
        try:
            from backend.generate_ai_pdf_report import generate_pdf_report
            pdf_path_obj = generate_pdf_report(
                telemetry_path=telemetry_logger.log_file,
                output_pdf="Ergonomic_Report.pdf",
                output_dir=REPORTS_DIR
            )
            if pdf_path_obj and pdf_path_obj.exists():
                state.pdf_path = str(pdf_path_obj)
                print(f"[+] PDF saved to: {state.pdf_path}")
                # Store PDF in MongoDB GridFS
                try:
                    fs = get_fs()
                    with open(pdf_path_obj, "rb") as pdf_file:
                        pdf_gridfs_id = fs.put(
                            pdf_file.read(),
                            filename=f"report_{state.session_id or 'session'}.pdf",
                            content_type="application/pdf",
                            session_id=state.session_id,
                            user_id=state.user_id,
                            created_at=datetime.datetime.utcnow()
                        )
                    print(f"[+] PDF stored in GridFS id: {pdf_gridfs_id}")
                except Exception as gfs_err:
                    print(f"[!] Warning: GridFS upload failed: {gfs_err}")
        except Exception as e:
            print(f"[!] PDF generation error: {e}")
        finally:
            with state.lock:
                state.pdf_generating = False

        # Update session document in MongoDB
        if state.session_id:
            try:
                from bson import ObjectId
                col = sessions_col()
                ended_at = datetime.datetime.utcnow()
                update_fields = {
                    "ended_at": ended_at,
                    "duration_sec": round(elapsed, 1),
                    "frame_count": frame_count,
                    "status": "completed",
                    "final_stats": state.session_stats,
                }
                if pdf_gridfs_id:
                    update_fields["pdf_gridfs_id"] = str(pdf_gridfs_id)
                col.update_one({"_id": ObjectId(state.session_id)}, {"$set": update_fields})
                print(f"[+] Session {state.session_id} updated in MongoDB.")
            except Exception as s_err:
                print(f"[!] Warning: Failed to update session in MongoDB: {s_err}")

        with state.lock:
            state.running = False
            state.stopping = False
            state.pdf_generating = False
        with state.frame_lock:
            state.latest_frame = None
        print("[+] Monitor thread fully stopped.")


# ---------------------------------------------------------------------------
# HTTP API Routes
# ---------------------------------------------------------------------------

@app.route('/api/start', methods=['POST'])
@require_auth
def start_monitor():
    user_id = g.user_id
    with state.lock:
        if state.running:
            return jsonify({"status": "already_running"}), 200

        # Create session in MongoDB
        session_id = None
        try:
            col = sessions_col()
            now = datetime.datetime.utcnow()
            res = col.insert_one({
                "user_id": user_id,
                "started_at": now,
                "ended_at": None,
                "duration_sec": 0.0,
                "frame_count": 0,
                "status": "running",
            })
            session_id = str(res.inserted_id)
        except Exception as e:
            print(f"[!] Warning: Failed to create session in MongoDB: {e}")

        state.running = True
        state.stopping = False
        state.user_id = user_id
        state.session_id = session_id
        state.pdf_generating = False
        state.pdf_path = None
        state.session_stats = {}
        state.stop_event.clear()
    threading.Thread(target=_monitor_loop, daemon=True).start()
    return jsonify({"status": "started", "session_id": session_id}), 200


@app.route('/api/stop', methods=['POST'])
@require_auth
def stop_monitor():
    with state.lock:
        if not state.running and not state.stopping:
            return jsonify({"status": "not_running"}), 200
        state.running = False
        state.stopping = True
    state.stop_event.set()
    with state.frame_lock:
        state.latest_frame = None

    async def _close_pcs():
        coros = [pc.close() for pc in list(pcs)]
        pcs.clear()
        if coros:
            await asyncio.gather(*coros, return_exceptions=True)

    try:
        asyncio.run_coroutine_threadsafe(_close_pcs(), webrtc_loop)
    except Exception as e:
        print(f"[!] Warning: closing WebRTC pcs failed: {e}")

    return jsonify({"status": "stopping"}), 200


@app.route('/api/dismiss_alert', methods=['POST'])
def dismiss_alert():
    data = request.json or {}
    alert_type = data.get("alert_type")
    with state.lock:
        if alert_type == "BREAK":
            state.rule_20_active = False
            state.last_break_time = time.time()
        elif alert_type == "WATER":
            state.water_active = False
            state.last_water_time = time.time()
    return jsonify({"status": "success"}), 200


@app.route('/api/status', methods=['GET'])
@require_auth
def get_status():
    return jsonify(sanitize_for_json({
        "running": state.running,
        "stopping": state.stopping,
        "pdf_generating": state.pdf_generating,
        "pdf_path": state.pdf_path,
        "stats": state.session_stats,
    })), 200


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "app": "wellness_backend",
        "running": state.running,
        "pdf_generating": state.pdf_generating
    }), 200


@app.route('/api/shutdown', methods=['POST', 'GET'])
def shutdown_server():
    def _delayed_exit():
        time.sleep(0.5)
        os._exit(0)
    threading.Thread(target=_delayed_exit, daemon=True).start()
    return jsonify({"status": "shutting_down"}), 200


@app.route('/api/download_pdf', methods=['GET'])
@require_auth
def download_pdf():
    candidates = []
    if state.pdf_path:
        candidates.append(Path(state.pdf_path))
    candidates.append(REPORTS_DIR / "Ergonomic_Report.pdf")
    candidates.append(PROJECT_ROOT / "Ergonomic_Report.pdf")

    for pdf_file in candidates:
        if pdf_file and pdf_file.exists():
            return send_file(
                str(pdf_file),
                mimetype="application/pdf",
                as_attachment=True,
                download_name="Ergonomic_Report.pdf"
            )
    return jsonify({"error": "Report PDF not found. Please stop a monitor session first."}), 404



def _generate_mjpeg():
    """Generator that yields MJPEG frames for the /video_feed endpoint."""
    while True:
        with state.frame_lock:
            frame = state.latest_frame

        if frame is None:
            # Send a tiny blank JPEG to keep connection alive
            time.sleep(0.1)
            continue

        ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(_generate_mjpeg(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/webrtc/offer', methods=['POST'])
def webrtc_offer():
    try:
        params = request.json
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

        async def process_offer():
            pc = RTCPeerConnection()
            pc_id = "PeerConnection(%s)" % uuid.uuid4()
            pcs.add(pc)

            @pc.on("connectionstatechange")
            async def on_connectionstatechange():
                print(f"[{pc_id}] Connection state is {pc.connectionState}")
                if pc.connectionState == "failed" or pc.connectionState == "closed":
                    pcs.discard(pc)

            # Attach the video track
            video_track = MonitorVideoTrack()
            pc.addTrack(video_track)

            await pc.setRemoteDescription(offer)
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}

        future = asyncio.run_coroutine_threadsafe(process_offer(), webrtc_loop)
        answer = future.result(timeout=10)
        return jsonify(answer)
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ---------------------------------------------------------------------------
# React Production Build Static Server (SPA Catch-all)
# ---------------------------------------------------------------------------
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path.startswith("api/") or path.startswith("video_feed"):
        return jsonify({"error": "Endpoint not found"}), 404

    target = FRONTEND_BUILD_DIR / path
    if path != "" and target.exists() and not target.is_dir():
        return send_from_directory(str(FRONTEND_BUILD_DIR), path)

    index_file = FRONTEND_BUILD_DIR / "index.html"
    if index_file.exists():
        return send_from_directory(str(FRONTEND_BUILD_DIR), "index.html")

    return jsonify({
        "status": "AI Ergonomics backend is running.",
        "frontend_dir": str(FRONTEND_BUILD_DIR),
        "frontend_exists": FRONTEND_BUILD_DIR.exists()
    }), 200


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="AI Ergonomics — Flask API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind (default: 5000)")
    args = parser.parse_args()

    print("=" * 65)
    print("  AI Ergonomics & Digital Wellness — Flask API Server")
    print(f"  Listening on: http://{args.host}:{args.port}")
    print(f"  Frontend UI : {FRONTEND_BUILD_DIR}")
    print(f"  Logs Dir    : {LOGS_DIR}")
    print(f"  Reports Dir : {REPORTS_DIR}")
    print("  Endpoints:")
    print("    GET  /health             — Health check for desktop shell")
    print("    POST /api/shutdown       — Clean server shutdown")
    print("    POST /api/start          — Start live monitor")
    print("    POST /api/stop           — Stop monitor & generate PDF")
    print("    POST /api/dismiss_alert  — Dismiss active warnings")
    print("    GET  /api/status         — Get current session status")
    print("    GET  /video_feed         — MJPEG live stream")
    print("    POST /api/webrtc/offer   — WebRTC SDP Offer")
    print("=" * 65)
    app.run(host=args.host, port=args.port, debug=False, threaded=True)
