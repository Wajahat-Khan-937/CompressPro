"""
history_table.py
------------------------------------------------------------
Scrollable history table for compression/decompression records.
------------------------------------------------------------
"""

import customtkinter as ctk
from typing import Callable, Dict, List, Optional

from backend.utils import format_bytes


class HistoryTable(ctk.CTkScrollableFrame):
    """Renders history records as aligned rows inside a scrollable frame."""

    def __init__(
        self,
        master,
        theme: Dict[str, str],
        columns: List[tuple],
        **kwargs,
    ):
        """
        columns: list of (key, label, width_weight) tuples.
        """
        super().__init__(master, fg_color=theme["card"], corner_radius=12, **kwargs)
        self.theme = theme
        self.columns = columns
        self._build_header()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color=self.theme["table_header"], corner_radius=8)
        header.pack(fill="x", padx=4, pady=(4, 8))

        for _key, label, weight in self.columns:
            ctk.CTkLabel(
                header,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.theme["text"],
                anchor="w",
            ).pack(side="left", fill="x", expand=weight, padx=8, pady=10)

    def clear_rows(self) -> None:
        for child in self.winfo_children()[1:]:
            child.destroy()

    def load_records(self, records: List[Dict], row_formatter: Callable[[Dict], List[str]]) -> None:
        """Populate table rows from record dicts."""
        self.clear_rows()

        if not records:
            empty = ctk.CTkLabel(
                self,
                text="No history records yet.",
                font=ctk.CTkFont(size=13),
                text_color=self.theme["text_muted"],
            )
            empty.pack(pady=24)
            return

        for idx, record in enumerate(records):
            values = row_formatter(record)
            bg = self.theme["table_row_alt"] if idx % 2 else self.theme["card"]
            row = ctk.CTkFrame(self, fg_color=bg, corner_radius=6)
            row.pack(fill="x", padx=4, pady=2)

            status_color = (
                self.theme["success"]
                if record.get("status") == "Success"
                else self.theme["error"]
            )

            for col_idx, (_key, _label, weight) in enumerate(self.columns):
                text = values[col_idx] if col_idx < len(values) else ""
                color = status_color if _key == "status" else self.theme["text"]
                ctk.CTkLabel(
                    row,
                    text=text,
                    font=ctk.CTkFont(size=11),
                    text_color=color,
                    anchor="w",
                ).pack(side="left", fill="x", expand=weight, padx=8, pady=8)
