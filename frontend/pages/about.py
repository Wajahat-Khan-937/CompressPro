"""
about.py
------------------------------------------------------------
About page with project information and technology credits.
------------------------------------------------------------
"""

import customtkinter as ctk
from typing import Dict


class AboutPage(ctk.CTkFrame):
    """Project information and credits for demonstration."""

    def __init__(self, master, theme: Dict[str, str], **kwargs):
        super().__init__(master, fg_color=theme["bg"], **kwargs)
        self.theme = theme
        self._build_ui()

    def _build_ui(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        card = ctk.CTkFrame(
            container,
            fg_color=self.theme["card"],
            border_color=self.theme["card_border"],
            border_width=1,
            corner_radius=24,
            width=520,
        )
        card.pack()
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text="⚡",
            font=ctk.CTkFont(size=56),
        ).pack(pady=(36, 8))

        ctk.CTkLabel(
            card,
            text="CompressPro",
            font=ctk.CTkFont(family="Segoe UI", size=30, weight="bold"),
            text_color=self.theme["primary"],
        ).pack()

        ctk.CTkLabel(
            card,
            text="Universal File Compression & Decompression System",
            font=ctk.CTkFont(size=14),
            text_color=self.theme["text_muted"],
        ).pack(pady=(4, 20))

        details = [
            ("Version", "2.0.0"),
            ("Algorithm", "Huffman Coding (Binary)"),
            ("Framework", "Python 3 + CustomTkinter"),
            ("Platform", "Windows Desktop Application"),
            ("Course", "Data Structures & Algorithms"),
            ("Type", "Final Year University Project"),
        ]

        for label, value in details:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=48, pady=5)
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.theme["text_muted"],
                width=100,
                anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                row,
                text=value,
                font=ctk.CTkFont(size=12),
                text_color=self.theme["text"],
                anchor="w",
            ).pack(side="left")

        ctk.CTkLabel(
            card,
            text=(
                "Compresses any file type using Huffman coding on raw bytes.\n"
                "Features login, history tracking, dashboard analytics,\n"
                "dark/light themes, and drag-and-drop support."
            ),
            font=ctk.CTkFont(size=12),
            text_color=self.theme["text_muted"],
            justify="center",
        ).pack(pady=(24, 12))

        ctk.CTkLabel(
            card,
            text="© 2026 CompressPro — Built for Academic Excellence",
            font=ctk.CTkFont(size=11),
            text_color=self.theme["text_muted"],
        ).pack(pady=(8, 32))
