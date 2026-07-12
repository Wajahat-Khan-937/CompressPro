"""
themes.py
------------------------------------------------------------
Light and dark theme palettes for CustomTkinter widgets.
------------------------------------------------------------
"""

from typing import Dict

LIGHT_THEME: Dict[str, str] = {
    "mode": "light",
    "bg": "#F4F6FB",
    "sidebar": "#FFFFFF",
    "card": "#FFFFFF",
    "card_border": "#E2E8F0",
    "primary": "#4F46E5",
    "primary_hover": "#4338CA",
    "secondary": "#0EA5E9",
    "accent": "#10B981",
    "text": "#1E293B",
    "text_muted": "#64748B",
    "text_inverse": "#FFFFFF",
    "input_bg": "#F8FAFC",
    "input_border": "#CBD5E1",
    "success": "#059669",
    "error": "#DC2626",
    "warning": "#D97706",
    "shadow": "#94A3B8",
    "gradient_start": "#4F46E5",
    "gradient_end": "#7C3AED",
    "table_header": "#EEF2FF",
    "table_row_alt": "#F8FAFC",
    "hover": "#EEF2FF",
}

DARK_THEME: Dict[str, str] = {
    "mode": "dark",
    "bg": "#0F172A",
    "sidebar": "#1E293B",
    "card": "#1E293B",
    "card_border": "#334155",
    "primary": "#6366F1",
    "primary_hover": "#818CF8",
    "secondary": "#38BDF8",
    "accent": "#34D399",
    "text": "#F1F5F9",
    "text_muted": "#94A3B8",
    "text_inverse": "#FFFFFF",
    "input_bg": "#0F172A",
    "input_border": "#475569",
    "success": "#34D399",
    "error": "#F87171",
    "warning": "#FBBF24",
    "shadow": "#020617",
    "gradient_start": "#4338CA",
    "gradient_end": "#7C3AED",
    "table_header": "#334155",
    "table_row_alt": "#1E293B",
    "hover": "#334155",
}


def get_theme(name: str) -> Dict[str, str]:
    """Return theme dict by name ('light' or 'dark')."""
    return DARK_THEME if name == "dark" else LIGHT_THEME
