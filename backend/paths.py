"""
Centralized Paths Utility for AI Ergonomics & Digital-Wellness Monitor.
Handles both standard development environments and frozen PyInstaller standalone packages.
"""
import os
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Resolve the project root or bundled assets directory."""
    if getattr(sys, "frozen", False):
        # Running inside PyInstaller onedir or onefile
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass and (Path(meipass) / "models").exists():
            return Path(meipass)
        exe_dir = Path(sys.executable).parent
        if (exe_dir / "models").exists():
            return exe_dir
        if (exe_dir / "_internal" / "models").exists():
            return exe_dir / "_internal"
        if meipass:
            return Path(meipass)
        return exe_dir

    # Normal development environment: Major_Project/
    return Path(__file__).resolve().parent.parent


PROJECT_ROOT = get_project_root()
MODELS_DIR = PROJECT_ROOT / "models"
CONFIG_DIR = PROJECT_ROOT / "config"
CALIB_DIR = PROJECT_ROOT / "calibration"

# User-writable application data directory for logs, reports, and local databases
def get_user_data_dir() -> Path:
    if getattr(sys, "frozen", False):
        local_app_data = os.getenv("LOCALAPPDATA") or str(Path.home())
        data_dir = Path(local_app_data) / "DigitalWellness"
    else:
        data_dir = PROJECT_ROOT

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


USER_DATA_DIR = get_user_data_dir()
LOGS_DIR = USER_DATA_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR = USER_DATA_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Frontend build directory resolution
def get_frontend_build_dir() -> Path:
    candidates = [
        PROJECT_ROOT / "frontend" / "build",
        PROJECT_ROOT / "frontend_build",
        Path(getattr(sys, "_MEIPASS", "")) / "frontend_build",
        Path(sys.executable).parent / "frontend_build" if getattr(sys, "frozen", False) else None,
        Path(sys.executable).parent / "_internal" / "frontend_build" if getattr(sys, "frozen", False) else None,
    ]
    for c in candidates:
        if c and c.exists() and (c / "index.html").exists():
            return c
    return PROJECT_ROOT / "frontend" / "build"


FRONTEND_BUILD_DIR = get_frontend_build_dir()
