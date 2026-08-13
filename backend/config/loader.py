"""
Configuration Loader Module.
Handles loading, schema validation, and fallback defaults for safety policies and configs.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"

DEFAULT_FINAL_POLICY: Dict[str, Any] = {
    "distance": {
        "non_safe_min_cm": 40.0,
        "warning_min_cm": 40.0,
        "safe_min_cm": 45.0,
        "safe_max_cm": 75.0,
        "warning_max_cm": 85.0,
        "non_safe_max_cm": 85.0
    },
    "head_pitch": {
        "warning_deg": 15.0,
        "non_safe_deg": 30.0
    },
    "head_yaw": {
        "warning_deg": 15.0,
        "non_safe_deg": 30.0
    },
    "shoulder_tilt": {
        "warning_deg": 10.0,
        "non_safe_deg": 20.0
    },
    "gaze": {
        "enabled": False,
        "reason": "Supporting measurement; not currently used as an independent safety trigger."
    },
    "blink": {
        "enabled": False,
        "reason": "Informational measurement; not currently used as an independent safety trigger."
    },
    "head_roll": {
        "enabled": False,
        "reason": "Not used as an independent ergonomic safety trigger."
    },
    "temporal": {
        "warning_seconds": 2.0,
        "non_safe_seconds": 5.0
    }
}


def load_final_policy(config_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load front_camera_final_policy.json from config directory.
    Falls back to default validated sponsor policy if file is missing or invalid.
    """
    cdir = config_dir or DEFAULT_CONFIG_DIR
    policy_path = cdir / "front_camera_final_policy.json"

    if not policy_path.exists():
        print(f"[!] Policy file missing at {policy_path}. Using validated default policy.")
        return DEFAULT_FINAL_POLICY.copy()

    try:
        with open(policy_path, "r", encoding="utf-8") as f:
            policy = json.load(f)
        _validate_policy_schema(policy)
        return policy
    except Exception as e:
        print(f"[!] Error loading policy from {policy_path}: {e}. Using validated default policy.")
        return DEFAULT_FINAL_POLICY.copy()


def load_safety_config(config_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load base safety configuration file.
    """
    cdir = config_dir or DEFAULT_CONFIG_DIR
    config_path = cdir / "front_camera_safety_config.json"

    if not config_path.exists():
        return {
            "version": "front-camera-safety-v2",
            "states": ["SAFE", "WARNING", "NON-SAFE"],
            "warning_persistence_seconds": 2.0,
            "non_safe_persistence_seconds": 5.0
        }

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _validate_policy_schema(policy: Dict[str, Any]):
    """Ensure essential policy keys exist."""
    required_keys = ["distance", "head_pitch", "head_yaw", "shoulder_tilt", "temporal"]
    for key in required_keys:
        if key not in policy:
            raise ValueError(f"Missing required policy section: {key}")
