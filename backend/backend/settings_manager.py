"""
settings_manager.py
------------------------------------------------------------
Application settings persistence (theme, defaults, recent files).
------------------------------------------------------------
"""

import json
import os
from typing import Any, Dict, List

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

DEFAULT_SETTINGS: Dict[str, Any] = {
    "theme": "light",
    "default_output_dir": "",
    "recent_files": [],
    "max_recent_files": 10,
    "show_notifications": True,
}


def load_settings() -> Dict[str, Any]:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = DEFAULT_SETTINGS.copy()
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: Dict[str, Any]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def update_setting(key: str, value: Any) -> Dict[str, Any]:
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
    return settings


def add_recent_file(path: str) -> None:
    """Push a file path to the recent files list (most recent first)."""
    settings = load_settings()
    recent: List[str] = settings.get("recent_files", [])
    path = os.path.abspath(path)

    if path in recent:
        recent.remove(path)
    recent.insert(0, path)

    max_count = settings.get("max_recent_files", 10)
    settings["recent_files"] = recent[:max_count]
    save_settings(settings)
