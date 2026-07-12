"""
settings.py
------------------------------------------------------------
Settings page: theme toggle, defaults, recent files, notifications.
------------------------------------------------------------
"""

import os
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Dict, Optional

from backend.settings_manager import load_settings, save_settings, update_setting
from frontend.components.toast import show_toast


class SettingsPage(ctk.CTkFrame):
    """Application preferences and recent files management."""

    def __init__(
        self,
        master,
        theme: Dict[str, str],
        on_theme_change: Callable[[str], None],
        show_toast_fn: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=theme["bg"], **kwargs)
        self.theme = theme
        self.on_theme_change = on_theme_change
        self.show_toast_fn = show_toast_fn or show_toast
        self.settings = load_settings()
        self._build_ui()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(28, 16))

        ctk.CTkLabel(
            header,
            text="⚙️  Settings",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=self.theme["text"],
        ).pack(side="left")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=32, pady=(0, 24))

        # Appearance
        self._section(scroll, "Appearance")
        appear_card = self._card(scroll)

        theme_row = ctk.CTkFrame(appear_card, fg_color="transparent")
        theme_row.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(
            theme_row,
            text="Theme Mode",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme["text"],
        ).pack(side="left")

        self.theme_switch = ctk.CTkSwitch(
            theme_row,
            text="Dark Mode",
            font=ctk.CTkFont(size=13),
            text_color=self.theme["text"],
            progress_color=self.theme["primary"],
            command=self._toggle_theme,
        )
        self.theme_switch.pack(side="right")
        if self.settings.get("theme") == "dark":
            self.theme_switch.select()

        # Defaults
        self._section(scroll, "Defaults")
        default_card = self._card(scroll)

        dir_row = ctk.CTkFrame(default_card, fg_color="transparent")
        dir_row.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(
            dir_row,
            text="Default Output Folder",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme["text"],
        ).pack(anchor="w")

        dir_btn_row = ctk.CTkFrame(dir_row, fg_color="transparent")
        dir_btn_row.pack(fill="x", pady=(8, 0))

        self.default_dir_label = ctk.CTkLabel(
            dir_btn_row,
            text=self.settings.get("default_output_dir") or "Not set",
            font=ctk.CTkFont(size=12),
            text_color=self.theme["text_muted"],
            anchor="w",
        )
        self.default_dir_label.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            dir_btn_row,
            text="Browse",
            width=90,
            height=34,
            corner_radius=17,
            fg_color=self.theme["primary"],
            hover_color=self.theme["primary_hover"],
            command=self._set_default_dir,
        ).pack(side="right")

        # Notifications
        self._section(scroll, "Notifications")
        notif_card = self._card(scroll)

        notif_row = ctk.CTkFrame(notif_card, fg_color="transparent")
        notif_row.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(
            notif_row,
            text="Show toast notifications",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.theme["text"],
        ).pack(side="left")

        self.notif_switch = ctk.CTkSwitch(
            notif_row,
            text="",
            progress_color=self.theme["accent"],
            command=self._toggle_notifications,
        )
        self.notif_switch.pack(side="right")
        if self.settings.get("show_notifications", True):
            self.notif_switch.select()

        # Recent files
        self._section(scroll, "Recent Files")
        self.recent_card = self._card(scroll)
        self._load_recent_files()

    def _section(self, parent, title: str) -> None:
        ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.theme["text_muted"],
        ).pack(anchor="w", pady=(16, 8))

    def _card(self, parent) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            parent,
            fg_color=self.theme["card"],
            border_color=self.theme["card_border"],
            border_width=1,
            corner_radius=16,
        )
        card.pack(fill="x", pady=(0, 8))
        return card

    def _toggle_theme(self) -> None:
        new_theme = "dark" if self.theme_switch.get() else "light"
        update_setting("theme", new_theme)
        self.on_theme_change(new_theme)
        self.show_toast_fn(
            self.winfo_toplevel(),
            f"{new_theme.title()} mode enabled.",
            "info",
            self.theme,
        )

    def _toggle_notifications(self) -> None:
        update_setting("show_notifications", bool(self.notif_switch.get()))

    def _set_default_dir(self) -> None:
        path = filedialog.askdirectory(title="Select default output folder")
        if path:
            update_setting("default_output_dir", path)
            self.default_dir_label.configure(text=path)

    def _load_recent_files(self) -> None:
        for child in self.recent_card.winfo_children():
            child.destroy()

        recent = load_settings().get("recent_files", [])
        if not recent:
            ctk.CTkLabel(
                self.recent_card,
                text="No recent files yet.",
                font=ctk.CTkFont(size=13),
                text_color=self.theme["text_muted"],
            ).pack(padx=20, pady=16)
            return

        for path in recent:
            row = ctk.CTkFrame(self.recent_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=6)
            exists = os.path.exists(path)
            color = self.theme["text"] if exists else self.theme["text_muted"]
            ctk.CTkLabel(
                row,
                text=f"{'📄' if exists else '⚠'} {os.path.basename(path)}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=color,
                anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                row,
                text=path,
                font=ctk.CTkFont(size=10),
                text_color=self.theme["text_muted"],
                anchor="e",
            ).pack(side="right")

    def on_show(self) -> None:
        self.settings = load_settings()
        self._load_recent_files()

    def apply_theme(self, theme: Dict[str, str]) -> None:
        self.theme = theme
