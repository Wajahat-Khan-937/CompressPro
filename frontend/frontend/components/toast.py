"""
toast.py
------------------------------------------------------------
Non-blocking toast notification overlay.
------------------------------------------------------------
"""

import customtkinter as ctk
from typing import Dict, Optional


class ToastNotification(ctk.CTkToplevel):
    """Small popup toast for success/error/info messages."""

    COLORS = {
        "success": ("#059669", "#D1FAE5"),
        "error": ("#DC2626", "#FEE2E2"),
        "info": ("#2563EB", "#DBEAFE"),
        "warning": ("#D97706", "#FEF3C7"),
    }

    def __init__(
        self,
        parent,
        message: str,
        toast_type: str = "info",
        duration_ms: int = 3000,
        theme: Optional[Dict[str, str]] = None,
    ):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        accent, bg = self.COLORS.get(toast_type, self.COLORS["info"])
        if theme and theme.get("mode") == "dark":
            bg = theme.get("card", "#1E293B")
            text_color = theme.get("text", "#F1F5F9")
        else:
            text_color = "#1E293B"

        self.configure(fg_color=bg)

        icons = {"success": "✓", "error": "✕", "info": "ℹ", "warning": "!"}
        icon = icons.get(toast_type, "ℹ")

        frame = ctk.CTkFrame(self, fg_color=bg, corner_radius=12)
        frame.pack(padx=2, pady=2)

        ctk.CTkLabel(
            frame,
            text=f"  {icon}  {message}  ",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=accent if toast_type != "info" else text_color,
            fg_color=bg,
        ).pack(padx=16, pady=12)

        self.update_idletasks()
        self._position(parent)
        self.after(duration_ms, self.destroy)

    def _position(self, parent) -> None:
        parent.update_idletasks()
        x = parent.winfo_rootx() + parent.winfo_width() - self.winfo_width() - 24
        y = parent.winfo_rooty() + 24
        self.geometry(f"+{x}+{y}")


def show_toast(parent, message: str, toast_type: str = "info", theme=None) -> None:
    """Convenience wrapper to display a toast notification."""
    ToastNotification(parent, message, toast_type, theme=theme)
