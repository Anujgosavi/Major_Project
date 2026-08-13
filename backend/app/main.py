"""
Main Application Entry Point.
Continuous real-time laptop webcam monitoring for ergonomic safety.
"""

import argparse
import sys
import time
from pathlib import Path

import cv2

# Add project root to sys.path for direct module execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.vision.pipeline import FrontCameraPipeline
from backend.safety.engine import SafetyEngine
from backend.app.annotator import annotate_frame
from backend.app.notifier import PostureNotifier
from backend.app.reporter import SessionReporter
from backend.telemetry.logger import TelemetryLogger


def run_continuous_monitor(
    source=0,
    models_dir=None,
    config_dir=None,
    calib_dir=None,
    headless=False,
    max_frames=None,
    enable_notifier=True,
    generate_pdf=False,
    api_key=None
):
    print("=" * 65)
    print("  AI Ergonomics & Digital-Wellness System")
    print("  Front-Camera Laptop Continuous Monitoring")
    print("=" * 65)

    # Convert numeric camera source
    try:
        source_input = int(source)
    except ValueError:
        source_input = str(source)

    # Initialize Pipeline, Safety Engine, Notifier, Reporter & Telemetry Logger
    print("[..] Initializing Vision Pipeline & Safety Engine...")
    pipeline = FrontCameraPipeline(models_dir=models_dir, calib_dir=calib_dir)
    safety_engine = SafetyEngine(config_dir=config_dir, reference_profile=pipeline.reference)
    notifier = PostureNotifier(enabled=enable_notifier)
    reporter = SessionReporter()
    telemetry_logger = TelemetryLogger()
    print("[+] Vision Pipeline, Safety Engine, Notifier, Reporter & Telemetry Logger Initialized.")

    # Open Video Capture Stream
    print(f"[..] Opening video stream source: {source_input}")
    cap = cv2.VideoCapture(source_input)

    if not cap.isOpened():
        print(f"[!] Error: Unable to open video source {source_input}")
        pipeline.close()
        return

    # Setup timing and metrics
    start_time = time.time()
    last_fps_time = start_time
    frame_count = 0
    fps_val = 0.0

    # 20-20-20 Rule Tracking
    last_break_time = start_time
    rule_20_active = False

    # Get camera frame dimensions for window setup
    cam_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cam_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if not headless:
        cv2.namedWindow("AI Ergonomics Monitor", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("AI Ergonomics Monitor", cam_w, cam_h)
        # Allow window to go fullscreen when maximized and content fills it
        cv2.setWindowProperty("AI Ergonomics Monitor", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    print("[+] Monitoring running. Press 'q' or ESC in window to exit. Press 'f' to toggle fullscreen.")

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame is None:
                print("[!] End of video stream or error reading frame.")
                break

            frame_count += 1
            current_time = time.time()

            # Mirror frame horizontally for natural selfie-view
            frame = cv2.flip(frame, 1)

            # Process Vision Pipeline (timed)
            t0 = time.perf_counter()
            result = pipeline.process_frame(frame, timestamp=current_time)
            inference_ms = (time.perf_counter() - t0) * 1000.0

            # Evaluate Safety Rules & Temporal State
            decision = safety_engine.evaluate(result)

            # Update Session Reporter & Telemetry Logger
            reporter.update(result, decision)
            telemetry_logger.log_frame(result, decision)

            # Desktop / Audio Notification when NON-SAFE persists >= 10s
            if decision.get("final_status") == "NON-SAFE" and decision.get("persisted_duration", 0) >= 10.0:
                notifier.notify_non_safe(
                    duration_sec=decision.get("persisted_duration", 10.0),
                    reasons=decision.get("reasons", []),
                    timestamp=current_time
                )

            # -------------------------------------------------------------
            # 20-20-20 Rule Logic
            # -------------------------------------------------------------
            # 20 minutes = 1200 seconds
            time_since_break = current_time - last_break_time
            if time_since_break >= 1200.0:
                if not rule_20_active:
                    rule_20_active = True
                    notifier.notify_20_20_20(timestamp=current_time)
            
            # Active for exactly 20 seconds
            if rule_20_active and (time_since_break >= 1220.0):
                rule_20_active = False
                last_break_time = current_time  # Reset the 20-minute timer

            # Annotate Frame (pass inference time and 20-20-20 flag)
            annotated_frame = annotate_frame(
                frame, 
                result, 
                decision, 
                inference_ms=inference_ms,
                rule_20_20_20_active=rule_20_active
            )

            # Terminal log every 30 frames
            if frame_count % 30 == 0:
                dist_str = f"{result.get('estimated_distance_cm', 0):.1f}cm" if result.get('face_detected') else "N/A"
                print(f"Frame {frame_count:4d} | Status: {decision['final_status']:<8} | Dist: {dist_str} | Reasons: {decision['reasons']}")

            # Display window unless headless
            if not headless:
                # Scale annotated frame to fill the current window size
                try:
                    win_rect = cv2.getWindowImageRect("AI Ergonomics Monitor")
                    win_w, win_h = win_rect[2], win_rect[3]
                    if win_w > 0 and win_h > 0:
                        annotated_frame = cv2.resize(annotated_frame, (win_w, win_h), interpolation=cv2.INTER_LINEAR)
                except Exception:
                    pass  # Fall back to native display if rect unavailable

                cv2.imshow("AI Ergonomics Monitor", annotated_frame)
                key = cv2.waitKey(1) & 0xFF
                if key in (27, ord('q')):
                    print("[+] Exit key pressed.")
                    break
                elif key == ord('f'):
                    # Toggle fullscreen
                    prop = cv2.getWindowProperty("AI Ergonomics Monitor", cv2.WND_PROP_FULLSCREEN)
                    new_prop = cv2.WINDOW_FULLSCREEN if prop != cv2.WINDOW_FULLSCREEN else cv2.WINDOW_NORMAL
                    cv2.setWindowProperty("AI Ergonomics Monitor", cv2.WND_PROP_FULLSCREEN, new_prop)
                
                # Check if the user clicked the 'X' button on the window
                if cv2.getWindowProperty("AI Ergonomics Monitor", cv2.WND_PROP_VISIBLE) < 1:
                    print("[+] Window closed by user.")
                    break

            if max_frames and frame_count >= max_frames:
                print(f"[+] Reached maximum frame count ({max_frames}). Stopping.")
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        pipeline.close()
        telemetry_logger.close()
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        print(f"[+] Shutdown complete. Processed {frame_count} frames in {elapsed:.2f}s ({fps:.1f} FPS).")
        print(f"[+] Frame-by-frame telemetry recorded to: {telemetry_logger.log_file}")

        # Generate & output session posture report card
        print("\n" + reporter.generate_report())

        if generate_pdf:
            print("\n[..] Generating Gemini AI & PDF Ergonomic Report...")
            try:
                import subprocess
                cmd = [sys.executable, str(PROJECT_ROOT / "generate_ai_pdf_report.py"), "--telemetry", str(telemetry_logger.log_file)]
                if api_key:
                    cmd.extend(["--api-key", api_key])
                subprocess.run(cmd, check=True)
            except Exception as e:
                print(f"[!] Could not generate PDF report: {e}")


def main():
    parser = argparse.ArgumentParser(description="AI Ergonomics Front-Camera Monitoring System")
    parser.add_argument("--source", default="0", help="Webcam device index (0) or path to video file")
    parser.add_argument("--models-dir", type=Path, default=None, help="Directory containing MediaPipe models")
    parser.add_argument("--config-dir", type=Path, default=None, help="Directory containing policy JSON files")
    parser.add_argument("--calib-dir", type=Path, default=None, help="Directory containing calibration JSON files")
    parser.add_argument("--headless", action="store_true", help="Run without GUI window display")
    parser.add_argument("--max-frames", type=int, default=None, help="Stop after N frames (for testing)")
    parser.add_argument("--no-notifier", action="store_true", help="Disable audio/desktop popup alerts")
    parser.add_argument("--generate-pdf", action="store_true", help="Generate Gemini AI & PDF Ergonomic Report on exit")
    parser.add_argument("--api-key", default=None, help="Gemini API Key for PDF report generation")
    args = parser.parse_args()

    try:
        run_continuous_monitor(
            source=args.source,
            models_dir=args.models_dir,
            config_dir=args.config_dir,
            calib_dir=args.calib_dir,
            headless=args.headless,
            max_frames=args.max_frames,
            enable_notifier=not args.no_notifier,
            generate_pdf=args.generate_pdf,
            api_key=args.api_key
        )
    except KeyboardInterrupt:
        print("\n[+] Session ended by user via keyboard interrupt.")


if __name__ == "__main__":
    main()
