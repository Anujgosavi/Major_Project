"""
Flask API Server for AI Ergonomics Monitor.
Provides REST endpoints to control the vision pipeline from the React frontend.
"""

import sys
import time
import threading
import math
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, Response, jsonify, request
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

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.vision.pipeline import FrontCameraPipeline
from backend.safety.engine import SafetyEngine
from backend.app.annotator import annotate_frame
from backend.app.notifier import PostureNotifier
from backend.app.reporter import SessionReporter
from backend.telemetry.logger import TelemetryLogger

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------------
# Shared State
# ---------------------------------------------------------------------------
class MonitorState:
    def __init__(self):
        self.running = False
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
            with state.frame_lock:
                if state.latest_frame is not None:
                    frame = state.latest_frame.copy()
                    break
            await asyncio.sleep(0.05)

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
    telemetry_logger = TelemetryLogger()

    # Open camera
    if sys.platform.startswith('win'):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[!] Error: Unable to open webcam.")
        with state.lock:
            state.running = False
        return

    start_time = time.time()
    frame_count = 0

    # 20-20-20 and water tracking
    start_time = time.time()
    
    with state.lock:
        state.last_break_time = start_time
        state.last_water_time = start_time
        state.rule_20_active = False
        state.water_active = False

    print("[+] Vision pipeline running. Streaming to React frontend...")

    try:
        while not state.stop_event.is_set() and cap.isOpened():
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
                "active_alerts": ui_alerts
            }

            if frame_count % 30 == 0:
                dist_str = f"{result.get('estimated_distance_cm', 0):.1f}cm" if result.get('face_detected') else "N/A"
                print(f"Frame {frame_count:4d} | Status: {decision['final_status']:<8} | Dist: {dist_str}")

    finally:
        cap.release()
        pipeline.close()
        telemetry_logger.close()
        elapsed = time.time() - start_time

        print(f"\n[+] Shutdown. {frame_count} frames in {elapsed:.2f}s.")
        print("\n" + reporter.generate_report())

        # --- Auto-generate PDF ---
        state.pdf_generating = True
        print("\n[..] Generating Gemini AI & PDF Ergonomic Report...")
        try:
            import subprocess
            cmd = [sys.executable, str(PROJECT_ROOT / "generate_ai_pdf_report.py"),
                   "--telemetry", str(telemetry_logger.log_file)]
            subprocess.run(cmd, check=True)
            state.pdf_path = str(PROJECT_ROOT / "Ergonomic_Report.pdf")
            print(f"[+] PDF saved to: {state.pdf_path}")
        except Exception as e:
            print(f"[!] PDF generation error: {e}")
        finally:
            state.pdf_generating = False

        with state.lock:
            state.running = False
        state.latest_frame = None
        print("[+] Monitor thread fully stopped.")


# ---------------------------------------------------------------------------
# HTTP API Routes
# ---------------------------------------------------------------------------

@app.route('/api/start', methods=['POST'])
def start_monitor():
    with state.lock:
        if state.running:
            return jsonify({"status": "already_running"}), 200
        state.running = True
        state.pdf_generating = False
        state.pdf_path = None
        state.session_stats = {}
        state.stop_event.clear()
    threading.Thread(target=_monitor_loop, daemon=True).start()
    return jsonify({"status": "started"}), 200


@app.route('/api/stop', methods=['POST'])
def stop_monitor():
    with state.lock:
        if not state.running:
            return jsonify({"status": "not_running"}), 200
    state.stop_event.set()
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
def get_status():
    return jsonify(sanitize_for_json({
        "running": state.running,
        "pdf_generating": state.pdf_generating,
        "pdf_path": state.pdf_path,
        "stats": state.session_stats,
    })), 200


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
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 65)
    print("  AI Ergonomics — Flask API Server")
    print("  Endpoints:")
    print("    POST /api/start          — Start the live monitor")
    print("    POST /api/stop           — Stop monitor & generate PDF")
    print("    POST /api/dismiss_alert  — Dismiss active warnings")
    print("    GET  /api/status         — Get current session status")
    print("    GET  /video_feed         — MJPEG live stream")
    print("    POST /api/webrtc/offer   — WebRTC SDP Offer")
    print("=" * 65)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
