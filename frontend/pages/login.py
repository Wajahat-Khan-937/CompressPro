"""
login.py
------------------------------------------------------------
Professional login screen with gradient-style background.
------------------------------------------------------------
"""

import customtkinter as ctk
from typing import Callable, Dict

from backend.auth import authenticate


class LoginPage(ctk.CTkFrame):
    """Full-screen login view shown before the main application."""

    def __init__(
        self,
        master,
        theme: Dict[str, str],
        on_login_success: Callable[[str], None],
        **kwargs,
    ):
        super().__init__(master, fg_color=theme["bg"], **kwargs)
        self.theme = theme
        self.on_login_success = on_login_success

        self._build_ui()

    def _build_ui(self) -> None:
        # Decorative left panel
        left = ctk.CTkFrame(
            self,
            fg_color=self.theme["gradient_start"],
            corner_radius=0,
            width=380,
        )
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        ctk.CTkLabel(
            left,
            text="⚡",
            font=ctk.CTkFont(size=64),
            text_color="#FFFFFF",
        ).pack(pady=(80, 16))

        ctk.CTkLabel(
            left,
            text="CompressPro",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color="#FFFFFF",
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            left,
            text="Universal File Compression\n& Decompression System",
            font=ctk.CTkFont(size=14),
            text_color="#E0E7FF",
            justify="center",
        ).pack(pady=(0, 40))

        features = [
            "✦  Compress any file type",
            "✦  Huffman coding engine",
            "✦  History & analytics",
            "✦  Secure login access",
        ]
        for feat in features:
            ctk.CTkLabel(
                left,
                text=feat,
                font=ctk.CTkFont(size=13),
                text_color="#C7D2FE",
                anchor="w",
            ).pack(padx=48, pady=6, anchor="w")

        # Login form panel
        right = ctk.CTkFrame(self, fg_color=self.theme["bg"], corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            form,
            text="Welcome Back",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=self.theme["text"],
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            form,
            text="Sign in to access your compression dashboard",
            font=ctk.CTkFont(size=13),
            text_color=self.theme["text_muted"],
        ).pack(anchor="w", pady=(0, 32))

        ctk.CTkLabel(
            form,
            text="Username",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.theme["text"],
        ).pack(anchor="w", pady=(0, 6))

        self.username_entry = ctk.CTkEntry(
            form,
            width=340,
            height=44,
            corner_radius=12,
            border_color=self.theme["input_border"],
            fg_color=self.theme["input_bg"],
            text_color=self.theme["text"],
            placeholder_text="Enter username",
            font=ctk.CTkFont(size=14),
        )
        self.username_entry.pack(pady=(0, 16))

        ctk.CTkLabel(
            form,
            text="Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.theme["text"],
        ).pack(anchor="w", pady=(0, 6))

        self.password_entry = ctk.CTkEntry(
            form,
            width=340,
            height=44,
            corner_radius=12,
            border_color=self.theme["input_border"],
            fg_color=self.theme["input_bg"],
            text_color=self.theme["text"],
            placeholder_text="Enter password",
            show="•",
            font=ctk.CTkFont(size=14),
        )
        self.password_entry.pack(pady=(0, 8))

        self.error_label = ctk.CTkLabel(
            form,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.theme["error"],
        )
        self.error_label.pack(anchor="w", pady=(0, 12))

        self.login_btn = ctk.CTkButton(
            form,
            text="Sign In  →",
            width=340,
            height=46,
            corner_radius=23,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.theme["primary"],
            hover_color=self.theme["primary_hover"],
            command=self._attempt_login,
        )
        self.login_btn.pack(pady=(8, 16))

        ctk.CTkLabel(
            form,
            text="Demo: admin / admin123  •  student / dsa2026",
            font=ctk.CTkFont(size=11),
            text_color=self.theme["text_muted"],
        ).pack()

        self.username_entry.bind("<Return>", lambda _: self._attempt_login())
        self.password_entry.bind("<Return>", lambda _: self._attempt_login())

    def _attempt_login(self) -> None:
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.error_label.configure(text="Please enter username and password.")
            return

        if authenticate(username, password):
            self.error_label.configure(text="")
            self.on_login_success(username)
        else:
            self.error_label.configure(text="Invalid username or password.")

    def reset(self) -> None:
        """Clear form fields when returning to login."""
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.error_label.configure(text="")
