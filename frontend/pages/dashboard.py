"""
dashboard.py
------------------------------------------------------------
Dashboard / History page with stats, search, export, and clear.
------------------------------------------------------------
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Callable, Dict, Optional

from backend import history
from backend.utils import format_bytes
from frontend.components.history_table import HistoryTable
from frontend.components.toast import show_toast


class DashboardPage(ctk.CTkFrame):
    """Analytics dashboard with combined activity history."""

    def __init__(
        self,
        master,
        theme: Dict[str, str],
        show_toast_fn: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=theme["bg"], **kwargs)
        self.theme = theme
        self.show_toast_fn = show_toast_fn or show_toast
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(28, 16))

        ctk.CTkLabel(
            header,
            text="📊  Dashboard",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=self.theme["text"],
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="Overview of compression activity and storage savings",
            font=ctk.CTkFont(size=13),
            text_color=self.theme["text_muted"],
        ).pack(side="left", padx=(16, 0))

        # Stat cards row
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=32, pady=(0, 16))

        self.card_compressed = self._stat_card(cards, "📦", "Files Compressed", "0")
        self.card_decompressed = self._stat_card(cards, "📂", "Files Decompressed", "0")
        self.card_saved = self._stat_card(cards, "💾", "Storage Saved", "0 B")

        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=32, pady=(0, 12))

        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="🔍  Search history by file name...",
            width=320,
            height=38,
            corner_radius=19,
            border_color=self.theme["input_border"],
            fg_color=self.theme["card"],
            text_color=self.theme["text"],
            font=ctk.CTkFont(size=13),
        )
        self.search_entry.pack(side="left", padx=(0, 12))
        self.search_entry.bind("<KeyRelease>", lambda _: self._search())

        ctk.CTkButton(
            toolbar,
            text="Export CSV",
            width=110,
            height=38,
            corner_radius=19,
            fg_color=self.theme["secondary"],
            hover_color="#0284C7",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._export_csv,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            toolbar,
            text="Clear History",
            width=120,
            height=38,
            corner_radius=19,
            fg_color=self.theme["error"],
            hover_color="#B91C1C",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._clear_history,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            toolbar,
            text="↻  Refresh",
            width=100,
            height=38,
            corner_radius=19,
            fg_color=self.theme["primary"],
            hover_color=self.theme["primary_hover"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.refresh,
        ).pack(side="right")

        # Recent activities
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=32, pady=(0, 24))

        recent_frame = ctk.CTkFrame(
            body,
            fg_color=self.theme["card"],
            border_color=self.theme["card_border"],
            border_width=1,
            corner_radius=16,
        )
        recent_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            recent_frame,
            text="🕐  Recent Activities",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.theme["text"],
        ).pack(anchor="w", padx=20, pady=(16, 8))

        self.activity_table = HistoryTable(
            recent_frame,
            self.theme,
            columns=[
                ("activity_type", "Type", 2),
                ("file_name", "File", 4),
                ("detail", "Details", 3),
                ("date", "Date", 2),
                ("time", "Time", 2),
                ("status", "Status", 1),
            ],
        )
        self.activity_table.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _stat_card(self, parent, icon: str, title: str, value: str) -> ctk.CTkLabel:
        card = ctk.CTkFrame(
            parent,
            fg_color=self.theme["card"],
            border_color=self.theme["card_border"],
            border_width=1,
            corner_radius=16,
        )
        card.pack(side="left", fill="x", expand=True, padx=(0, 12))

        ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=28),
        ).pack(anchor="w", padx=20, pady=(16, 4))

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color=self.theme["text_muted"],
        ).pack(anchor="w", padx=20)

        val_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=self.theme["primary"],
        )
        val_label.pack(anchor="w", padx=20, pady=(4, 20))
        return val_label

    def refresh(self) -> None:
        stats = history.get_dashboard_stats()
        self.card_compressed.configure(text=str(stats["total_compressed"]))
        self.card_decompressed.configure(text=str(stats["total_decompressed"]))
        self.card_saved.configure(text=format_bytes(stats["total_storage_saved"]))
        self._load_activities(stats["recent_activities"])

    def _load_activities(self, activities: list) -> None:
        def formatter(r):
            if r.get("activity_type") == "Compression":
                detail = f"Saved {r.get('ratio_percent', 0)}%"
            else:
                detail = format_bytes(r.get("restored_size", 0))
            return [
                r.get("activity_type", ""),
                r.get("file_name", "")[:30],
                detail,
                r.get("date", ""),
                r.get("time", ""),
                r.get("status", ""),
            ]

        self.activity_table.load_records(activities, formatter)

    def _search(self) -> None:
        query = self.search_entry.get()
        if not query.strip():
            self.refresh()
            return

        results = history.search_history(query)
        combined = []
        for r in results["compression"]:
            combined.append({**r, "activity_type": "Compression"})
        for r in results["decompression"]:
            combined.append({**r, "activity_type": "Decompression"})
        combined.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        self._load_activities(combined)

    def _export_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export history to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="compression_history.csv",
        )
        if not path:
            return
        try:
            history.export_to_csv(path)
            self.show_toast_fn(self.winfo_toplevel(), "History exported successfully!", "success", self.theme)
        except Exception as exc:
            self.show_toast_fn(self.winfo_toplevel(), str(exc), "error", self.theme)

    def _clear_history(self) -> None:
        if messagebox.askyesno(
            "Clear History",
            "Are you sure you want to clear all compression and decompression history?",
        ):
            history.clear_history()
            self.search_entry.delete(0, "end")
            self.refresh()
            self.show_toast_fn(self.winfo_toplevel(), "History cleared.", "info", self.theme)

    def on_show(self) -> None:
        self.refresh()
