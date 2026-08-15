import threading
import cv2
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

# Global thread-safe frame storage
class FrameStore:
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()

    def update(self, frame):
        with self.condition:
            self.frame = frame
            self.condition.notify_all()

    def get_frame(self):
        with self.condition:
            self.condition.wait()
            return self.frame

global_store = FrameStore()

class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('/video_feed'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            # CORS Headers so React can fetch if needed, though img tag doesn't strictly need it
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            while True:
                try:
                    frame = global_store.get_frame()
                    if frame is None:
                        time.sleep(0.1)
                        continue

                    # Encode frame as JPEG
                    ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                    if not ret:
                        continue
                    
                    self.wfile.write(b'--jpgboundary\r\n')
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', str(len(jpeg)))
                    self.end_headers()
                    self.wfile.write(jpeg.tobytes())
                    self.wfile.write(b'\r\n')
                except Exception as e:
                    break
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress HTTP logging to avoid spamming the console
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def start_server(port=5000):
    server = ThreadedHTTPServer(('0.0.0.0', port), CamHandler)
    t = threading.Thread(target=server.serve_forever)
    t.daemon = True
    t.start()
    print(f"[+] MJPEG Video Stream Server started on port {port}")
    return server

def update_frame(frame):
    if frame is not None:
        global_store.update(frame.copy())
