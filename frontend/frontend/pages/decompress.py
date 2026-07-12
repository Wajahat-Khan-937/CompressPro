"""
decompress.py
------------------------------------------------------------
Decompress page: .huff file selection, decompression, and stats.
------------------------------------------------------------
"""

import os
import threading
import tkinter.filedialog as fd
from tkinter import messagebox
import customtkinter as ctk
import traceback

# Backend imports
from backend.compressor import decompress_file, is_huff_archive
from backend.history import add_decompression_record
from backend.utils import format_bytes

DEBUG = True

def debug_print(msg):
    if DEBUG:
        print(f"[DECOMPRESS] {msg}")


class DecompressPage(ctk.CTkFrame):
    def __init__(self, parent, theme, show_toast_fn):
        debug_print("DecompressPage __init__ started")
        super().__init__(parent, fg_color=theme["bg"])
        self.theme = theme
        self.show_toast = show_toast_fn
        self.selected_file = None
        self.is_running = False
        self._build_ui()
        debug_print("DecompressPage __init__ finished")

    def _build_ui(self):
        debug_print("Building UI...")
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=30)

        ctk.CTkLabel(
            container,
            text="📂 Decompress Files",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=self.theme["text"],
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            container,
            text="Restore .huff files back to their original format",
            font=ctk.CTkFont(size=14),
            text_color=self.theme["text_muted"],
        ).pack(anchor="w", pady=(0, 24))

        file_frame = ctk.CTkFrame(
            container,
            fg_color=self.theme["card"],
            corner_radius=16,
            border_width=2,
            border_color=self.theme["bg"],
        )
        file_frame.pack(fill="x", pady=(0, 20))

        self.file_label = ctk.CTkLabel(
            file_frame,
            text="No .huff file selected",
            font=ctk.CTkFont(size=14),
            text_color=self.theme["text_muted"],
        )
        self.file_label.pack(side="left", padx=20, pady=16)

        select_btn = ctk.CTkButton(
            file_frame,
            text="Browse",
            width=120,
            height=38,
            corner_radius=10,
            fg_color=self.theme["primary"],
            hover_color=self.theme["primary_hover"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._select_file,
        )
        select_btn.pack(side="right", padx=16)

        self.decompress_btn = ctk.CTkButton(
            container,
            text="📂 Decompress File",
            height=48,
            corner_radius=12,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.theme["primary"],
            hover_color=self.theme["primary_hover"],
            state="disabled",
            command=self._decompress,
        )
        self.decompress_btn.pack(fill="x", pady=(0, 16))

        self.progress = ctk.CTkProgressBar(
            container,
            height=8,
            corner_radius=4,
            progress_color=self.theme["primary"],
        )
        self.progress.pack(fill="x", pady=(0, 16))
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(
            container,
            text="Ready to decompress",
            font=ctk.CTkFont(size=13),
            text_color=self.theme["text_muted"],
        )
        self.status_label.pack(anchor="w", pady=(0, 16))

        stats_frame = ctk.CTkFrame(
            container,
            fg_color=self.theme["card"],
            corner_radius=12,
        )
        stats_frame.pack(fill="x", pady=(0, 10))

        self.stats_labels = {}
        stats_data = [
            ("Original .huff", "0 B"),
            ("Restored Size", "0 B"),
            ("Time Taken", "0s"),
        ]

        for i, (label, value) in enumerate(stats_data):
            frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            frame.pack(side="left", padx=20, pady=12, expand=True, fill="x")

            ctk.CTkLabel(
                frame,
                text=label,
                font=ctk.CTkFont(size=11),
                text_color=self.theme["text_muted"],
            ).pack(anchor="center")

            val_label = ctk.CTkLabel(
                frame,
                text=value,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.theme["text"],
            )
            val_label.pack(anchor="center", pady=(4, 0))
            self.stats_labels[label] = val_label

        debug_print("UI built")

    def _select_file(self):
        debug_print("_select_file called")
        file_path = fd.askopenfilename(
            title="Select a .huff file to decompress",
            filetypes=[("Huffman compressed", "*.huff")]
        )
        if file_path:
            if not is_huff_archive(file_path):
                messagebox.showerror("Invalid File", "This is not a valid .huff archive.")
                return
            self.selected_file = file_path
            self.file_label.configure(
                text=os.path.basename(file_path),
                text_color=self.theme["text"],
            )
            self.decompress_btn.configure(state="normal")
            self.status_label.configure(text=f"Ready: {os.path.basename(file_path)}")
            self.progress.set(0)
            self.stats_labels["Original .huff"].configure(text=format_bytes(os.path.getsize(file_path)))
            self.stats_labels["Restored Size"].configure(text="0 B")
            self.stats_labels["Time Taken"].configure(text="0s")
            debug_print(f"File size: {os.path.getsize(file_path)} bytes")

    def _decompress(self):
        debug_print("=== _decompress START ===")
        if not self.selected_file or self.is_running:
            return

        output_dir = fd.askdirectory(title="Select output folder")
        if not output_dir:
            return

        self.is_running = True
        self.decompress_btn.configure(state="disabled", text="⏳ Decompressing...")
        self.status_label.configure(text="Decompressing... Please wait")
        self.progress.set(0)

        def worker():
            debug_print("=== WORKER THREAD STARTED ===")
            try:
                result = decompress_file(
                    self.selected_file,
                    output_dir,
                    progress_callback=self._update_progress
                )
                debug_print(f"decompress_file returned: {result}")
                add_decompression_record(
                    file_name=os.path.basename(result['output_path']),
                    restored_size=result['decompressed_size']
                )
                self.after(0, lambda: self._on_decompress_done(result))
            except Exception as e:
                debug_print(f"=== WORKER THREAD EXCEPTION ===")
                debug_print(f"Exception: {e}")
                traceback.print_exc()
                # FIXED: capture the exception
                self.after(0, lambda e=e: self._on_error(e))

        threading.Thread(target=worker, daemon=True).start()

    def _update_progress(self, fraction):
        def update():
            self.progress.set(fraction)
        self.after(0, update)

    def _on_decompress_done(self, result):
        debug_print(f"=== _on_decompress_done ===")
        self.progress.set(1.0)
        self.is_running = False
        self.decompress_btn.configure(state="normal", text="📂 Decompress File")
        self.status_label.configure(
            text=f"✅ Restored to: {os.path.basename(result['output_path'])}",
            text_color=self.theme.get("success", "#00FF00"),
        )

        self.stats_labels["Original .huff"].configure(
            text=format_bytes(os.path.getsize(self.selected_file))
        )
        self.stats_labels["Restored Size"].configure(
            text=format_bytes(result['decompressed_size'])
        )
        self.stats_labels["Time Taken"].configure(
            text=f"{result['seconds_taken']:.2f}s"
        )

        self.show_toast(self, "Decompression Complete!", "success")
        messagebox.showinfo("Success", f"File restored successfully!\n\n"
                            f"Output: {result['output_path']}\n"
                            f"Size:   {format_bytes(result['decompressed_size'])}")

    def _on_error(self, exc):
        debug_print(f"=== _on_error ===")
        self.is_running = False
        self.decompress_btn.configure(state="normal", text="📂 Decompress File")
        self.status_label.configure(
            text=f"❌ Error: {str(exc)}",
            text_color=self.theme.get("error", "#FF0000"),
        )
        self.progress.set(0)
        self.show_toast(self, f"Error: {str(exc)}", "error")
        messagebox.showerror("Decompression Failed", str(exc))

    def apply_theme(self, theme):
        self.theme = theme
        self.configure(fg_color=theme["bg"])

    def on_show(self):
        debug_print("on_show called")
        pass