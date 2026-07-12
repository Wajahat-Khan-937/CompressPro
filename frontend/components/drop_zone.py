"""
drop_zone.py
------------------------------------------------------------
Drag-and-drop file zone with browse fallback.
------------------------------------------------------------
"""

import os
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Dict, Optional

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD

    DND_AVAILABLE = True
except ImportError:
    DND_FILES = None
    TkinterDnD = None
    DND_AVAILABLE = False


class DropZone(ctk.CTkFrame):
    """
    Styled drop zone accepting file drag-and-drop (when tkinterdnd2
    is installed) plus a Browse button fallback.
    """

    def __init__(
        self,
        master,
        theme: Dict[str, str],
        on_file_selected: Callable[[str], None],
        label: str = "Drag & drop a file here",
        filetypes: Optional[list] = None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=theme["input_bg"],
            border_color=theme["input_border"],
            border_width=2,
            corner_radius=16,
            **kwargs,
        )
        self.theme = theme
        self.on_file_selected = on_file_selected
        self.filetypes = filetypes or [("All files", "*.*")]
        self._hover = False

        self.icon_label = ctk.CTkLabel(
            self,
            text="📁",
            font=ctk.CTkFont(size=36),
            text_color=theme["primary"],
        )
        self.icon_label.pack(pady=(24, 8))

        self.text_label = ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(size=14),
            text_color=theme["text_muted"],
        )
        self.text_label.pack(pady=(0, 4))

        self.path_label = ctk.CTkLabel(
            self,
            text="No file selected",
            font=ctk.CTkFont(size=12),
            text_color=theme["text"],
            wraplength=400,
        )
        self.path_label.pack(pady=(0, 12))

        self.browse_btn = ctk.CTkButton(
            self,
            text="Browse File",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=theme["primary"],
            hover_color=theme["primary_hover"],
            corner_radius=20,
            height=36,
            command=self._browse,
        )
        self.browse_btn.pack(pady=(0, 24))

        self._bind_hover(self)
        self._setup_dnd()

    def _bind_hover(self, widget) -> None:
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event=None) -> None:
        if not self._hover:
            self._hover = True
            self.configure(border_color=self.theme["primary"])

    def _on_leave(self, _event=None) -> None:
        self._hover = False
        self.configure(border_color=self.theme["input_border"])

    def _setup_dnd(self) -> None:
        if not DND_AVAILABLE:
            return
        try:
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            pass

    def _parse_drop_path(self, data: str) -> str:
        data = data.strip()
        if data.startswith("{") and data.endswith("}"):
            return data[1:-1]
        return data.split()[0] if data else ""

    def _on_drop(self, event) -> None:
        path = self._parse_drop_path(event.data)
        if path and os.path.isfile(path):
            self.set_file(path)
            self.on_file_selected(path)

    def _browse(self) -> None:
        path = filedialog.askopenfilename(filetypes=self.filetypes)
        if path:
            self.set_file(path)
            self.on_file_selected(path)

    def set_file(self, path: str) -> None:
        display = os.path.basename(path)
        self.path_label.configure(text=display)

    def clear(self) -> None:
        self.path_label.configure(text="No file selected")
