"""
app.py
------------------------------------------------------------
Main application shell: sidebar navigation, page routing,
theme management, and login flow.
------------------------------------------------------------
"""

import os
import sys
import customtkinter as ctk
from typing import Dict, Optional
import threading
import tkinter.filedialog as fd
from tkinter import messagebox


# Ensure project root is on sys.path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Backend imports
from backend.compressor import compress_file, decompress_file
from backend.history import add_compression_record, add_decompression_record
from backend.utils import format_bytes, get_file_type_label
from backend.auth import get_current_user_display
from backend.settings_manager import load_settings, update_setting
from frontend.components.toast import show_toast
from frontend.pages.about import AboutPage
from frontend.pages.compress import CompressPage
from frontend.pages.dashboard import DashboardPage
from frontend.pages.decompress import DecompressPage
from frontend.pages.login import LoginPage
from frontend.pages.settings import SettingsPage
from frontend.themes import get_theme

# Enable drag-and-drop on the CustomTkinter root when tkinterdnd2 is available
try:
    from tkinterdnd2 import TkinterDnD

    class BaseWindow(ctk.CTk, TkinterDnD.DnDWrapper):
        """CTk root with drag-and-drop support."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.TkdndVersion = TkinterDnD._require(self)

except ImportError:
    BaseWindow = ctk.CTk


class CompressProApp(BaseWindow):
    """Root application window with sidebar and page container."""

    APP_TITLE = "CompressPro — Universal File Compression"
    MIN_WIDTH = 1100
    MIN_HEIGHT = 700

    NAV_ITEMS = [
        ("dashboard", "📊  Dashboard", "dashboard"),
        ("compress", "📦  Compress", "compress"),
        ("decompress", "📂  Decompress", "decompress"),
        ("settings", "⚙️  Settings", "settings"),
        ("about", "ℹ️  About", "about"),
    ]

    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.theme_name = self.settings.get("theme", "light")
        self.theme = get_theme(self.theme_name)
        self.current_user: Optional[str] = None
        self.pages: Dict[str, ctk.CTkFrame] = {}
        self.nav_buttons: Dict[str, ctk.CTkButton] = {}
        self.active_page = ""

        self._configure_window()
        self._build_login()
        self._build_main_shell()
        self._show_login()

    def _configure_window(self) -> None:
        ctk.set_appearance_mode(self.theme_name)
        ctk.set_default_color_theme("blue")
        self.title(self.APP_TITLE)
        self.geometry(f"{self.MIN_WIDTH}x{self.MIN_HEIGHT}")
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.configure(fg_color=self.theme["bg"])

        # Window icon (taskbar) when assets exist
        icon_path = os.path.join(PROJECT_ROOT, "assets", "logo.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

    def _build_login(self) -> None:
        self.login_page = LoginPage(
            self,
            self.theme,
            on_login_success=self._on_login,
        )

    def _build_main_shell(self) -> None:
        self.main_frame = ctk.CTkFrame(self, fg_color=self.theme["bg"], corner_radius=0)

        # Sidebar
        self.sidebar = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.theme["sidebar"],
            width=240,
            corner_radius=0,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(28, 24))

        ctk.CTkLabel(
            brand,
            text="⚡ CompressPro",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=self.theme["primary"],
        ).pack(anchor="w")

        self.user_label = ctk.CTkLabel(
            brand,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.theme["text_muted"],
        )
        self.user_label.pack(anchor="w", pady=(4, 0))

        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=12, pady=(8, 0))

        for key, label, page_key in self.NAV_ITEMS:
            btn = ctk.CTkButton(
                nav_frame,
                text=label,
                anchor="w",
                height=42,
                corner_radius=12,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="transparent",
                text_color=self.theme["text"],
                hover_color=self.theme["hover"],
                command=lambda k=page_key: self.show_page(k),
            )
            btn.pack(fill="x", pady=4)
            self.nav_buttons[page_key] = btn

        # Theme quick toggle in sidebar
        self.sidebar_theme_switch = ctk.CTkSwitch(
            self.sidebar,
            text="Dark Mode",
            font=ctk.CTkFont(size=12),
            text_color=self.theme["text_muted"],
            progress_color=self.theme["primary"],
            command=self._sidebar_theme_toggle,
        )
        self.sidebar_theme_switch.pack(side="bottom", padx=20, pady=(0, 12))
        if self.theme_name == "dark":
            self.sidebar_theme_switch.select()

        ctk.CTkButton(
            self.sidebar,
            text="🚪  Logout",
            height=38,
            corner_radius=12,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.theme["hover"],
            hover_color=self.theme["error"],
            text_color=self.theme["text"],
            command=self._logout,
        ).pack(side="bottom", fill="x", padx=16, pady=16)

        # Page container
        self.page_container = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.theme["bg"],
            corner_radius=0,
        )
        self.page_container.pack(side="left", fill="both", expand=True)

        toast_fn = self._toast_wrapper

        self.pages["dashboard"] = DashboardPage(self.page_container, self.theme, toast_fn)
        self.pages["compress"] = CompressPage(self.page_container, self.theme, toast_fn)
        self.pages["decompress"] = DecompressPage(self.page_container, self.theme, toast_fn)
        self.pages["settings"] = SettingsPage(
            self.page_container,
            self.theme,
            on_theme_change=self._apply_theme,
            show_toast_fn=toast_fn,
        )
        self.pages["about"] = AboutPage(self.page_container, self.theme)

    def _toast_wrapper(self, parent, message, toast_type="info", theme=None):
        if load_settings().get("show_notifications", True):
            show_toast(parent, message, toast_type, theme or self.theme)

    def _show_login(self) -> None:
        self.main_frame.pack_forget()
        self.login_page.pack(fill="both", expand=True)

    def _on_login(self, username: str) -> None:
        self.current_user = username
        self.user_label.configure(text=f"Signed in as {get_current_user_display(username)}")
        self.login_page.pack_forget()
        self.main_frame.pack(fill="both", expand=True)
        self.show_page("dashboard")
        self._toast_wrapper(self, f"Welcome, {get_current_user_display(username)}!", "success")

    def _logout(self) -> None:
        self.current_user = None
        self.main_frame.pack_forget()
        self.login_page.reset()
        self._show_login()

    def show_page(self, name: str) -> None:
        for key, page in self.pages.items():
            page.pack_forget()

        page = self.pages.get(name)
        if page:
            page.pack(fill="both", expand=True)
            if hasattr(page, "on_show"):
                page.on_show()

        self.active_page = name
        self._highlight_nav(name)

    def _highlight_nav(self, active: str) -> None:
        for key, btn in self.nav_buttons.items():
            if key == active:
                btn.configure(
                    fg_color=self.theme["primary"],
                    text_color=self.theme["text_inverse"],
                    hover_color=self.theme["primary_hover"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self.theme["text"],
                    hover_color=self.theme["hover"],
                )

    def _sidebar_theme_toggle(self) -> None:
        new_theme = "dark" if self.sidebar_theme_switch.get() else "light"
        self._apply_theme(new_theme)

    def _apply_theme(self, theme_name: str) -> None:
        self.theme_name = theme_name
        self.theme = get_theme(theme_name)
        update_setting("theme", theme_name)
        ctk.set_appearance_mode(theme_name)

        self.configure(fg_color=self.theme["bg"])
        self.main_frame.configure(fg_color=self.theme["bg"])
        self.sidebar.configure(fg_color=self.theme["sidebar"])
        self.page_container.configure(fg_color=self.theme["bg"])

        if self.sidebar_theme_switch.get() != (theme_name == "dark"):
            if theme_name == "dark":
                self.sidebar_theme_switch.select()
            else:
                self.sidebar_theme_switch.deselect()

        self.login_page.configure(fg_color=self.theme["bg"])

        for page in self.pages.values():
            if hasattr(page, "configure"):
                page.configure(fg_color=self.theme["bg"])
            if hasattr(page, "apply_theme"):
                page.apply_theme(self.theme)

        for btn in self.nav_buttons.values():
            btn.configure(
                hover_color=self.theme["hover"],
                text_color=self.theme["text"],
            )
        self._highlight_nav(self.active_page)

        settings_page = self.pages.get("settings")
        if settings_page and hasattr(settings_page, "apply_theme"):
            settings_page.apply_theme(self.theme)
            if hasattr(settings_page, "theme_switch"):
                if theme_name == "dark":
                    settings_page.theme_switch.select()
                else:
                    settings_page.theme_switch.deselect()


# frontend/app.py - at the very end

def launch():
    app = CompressProApp()   # or whatever your main class is called
    app.mainloop()