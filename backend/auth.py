"""
auth.py
------------------------------------------------------------
Simple authentication service for the login screen.

Credentials are stored in data/users.json. Default user is created
on first run for demonstration purposes.
------------------------------------------------------------
"""

import json
import os
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

DEFAULT_USERS = {
    "admin": "admin123",
    "student": "dsa2026",
}


def _ensure_users_file() -> None:
    """Create default users file if it does not exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_USERS, f, indent=2)


def authenticate(username: str, password: str) -> bool:
    """
    Validate username and password against stored credentials.

    Returns True on success, False otherwise.
    """
    _ensure_users_file()
    username = username.strip()

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except (json.JSONDecodeError, OSError):
        users = DEFAULT_USERS

    return users.get(username) == password


def get_current_user_display(username: str) -> str:
    """Friendly display name for the sidebar header."""
    return username.strip().title() if username else "User"
