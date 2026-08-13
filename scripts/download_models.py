"""
Download required MediaPipe task models if not present locally.
"""

import os
import urllib.request
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"

FACE_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/1/"
    "face_landmarker.task"
)

POSE_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_full/float16/1/"
    "pose_landmarker_full.task"
)

FACE_MODEL_PATH = MODELS_DIR / "face_landmarker.task"
POSE_MODEL_PATH = MODELS_DIR / "pose_landmarker_full.task"


def download_model(url: str, dest_path: Path):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if dest_path.exists() and dest_path.stat().st_size > 0:
        print(f"[+] Model already exists: {dest_path.name} ({dest_path.stat().st_size} bytes)")
        return

    print(f"[..] Downloading {dest_path.name} from {url} ...")
    urllib.request.urlretrieve(url, dest_path)
    print(f"[+] Download complete: {dest_path.name} ({dest_path.stat().st_size} bytes)")


def main():
    print("=" * 60)
    print("  Downloading MediaPipe Task Models")
    print("=" * 60)
    download_model(FACE_MODEL_URL, FACE_MODEL_PATH)
    download_model(POSE_MODEL_URL, POSE_MODEL_PATH)
    print("All models ready.\n")


if __name__ == "__main__":
    main()
