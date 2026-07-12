"""
compress.py
------------------------------------------------------------
Compress page: file selection, compression button, and stats display.
------------------------------------------------------------
"""

import os
import threading
import tkinter.filedialog as fd
from tkinter import messagebox
import customtkinter as ctk
import traceback

# Backend imports
from backend.compressor import compress_file
from backend.history import add_compression_record
from backend.utils import format_bytes, get_file_type_label

# Debugging flag
DEBUG = True

def debug_print(msg):
    if DEBUG:
        print(f"[COMPRESS] {msg}")


class CompressPage(ctk.CTkFrame):
    """Compression page with file selector, progress, and stats."""

    def __init__(self, parent, theme, show_toast_fn):
        debug_print("CompressPage __init__ started")
        super().__init__(parent, fg_color=theme["bg"])
        self.theme = theme
        self.show_toast = show_toast_fn
        self.selected_file = None
        self.is_running = False

        self._build_ui()
        debug_print("CompressPage __init__ finished")

    def _build_ui(self):
        debug_print("Building UI...")
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=30)

        ctk.CTkLabel(
            container,
            text="📦 Compress Files",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=self.theme["text"],
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            container,
            text="Compress PDF, images, Office docs, and any file type",
            font=ctk.CTkFont(size=14),
            text_color=self.theme["text_muted"],
        ).pack(anchor="w", pady=(0, 24))

        # File selection area
        file_frame = ctk.CTkFrame(
            container,
            fg_color=self.theme["card"],
            corner_radius=16,
            border_width=2,
            border_color=self.theme["bg"],   # fixed KeyError
        )
        file_frame.pack(fill="x", pady=(0, 20))

        self.file_label = ctk.CTkLabel(
            file_frame,
            text="No file selected",
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

        # Compress button
        self.compress_btn = ctk.CTkButton(
            container,
            text="▶ Compress File",
            height=48,
            corner_radius=12,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.theme["primary"],
            hover_color=self.theme["primary_hover"],
            state="disabled",
            command=self._compress,
        )
        self.compress_btn.pack(fill="x", pady=(0, 16))

        # Progress bar
        self.progress = ctk.CTkProgressBar(
            container,
            height=8,
            corner_radius=4,
            progress_color=self.theme["primary"],
        )
        self.progress.pack(fill="x", pady=(0, 16))
        self.progress.set(0)

        # Status label
        self.status_label = ctk.CTkLabel(
            container,
            text="Ready to compress",
            font=ctk.CTkFont(size=13),
            text_color=self.theme["text_muted"],
        )
        self.status_label.pack(anchor="w", pady=(0, 16))

        # Statistics frame
        stats_frame = ctk.CTkFrame(
            container,
            fg_color=self.theme["card"],
            corner_radius=12,
        )
        stats_frame.pack(fill="x", pady=(0, 10))

        self.stats_labels = {}
        stats_data = [
            ("Original Size", "0 B"),
            ("Compressed Size", "0 B"),
            ("Space Saved", "0%"),
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
            title="Select a file to compress",
            filetypes=[("All files", "*.*")]
        )
        if file_path:
            debug_print(f"File selected: {file_path}")
            self.selected_file = file_path
            self.file_label.configure(
                text=os.path.basename(file_path),
                text_color=self.theme["text"],
            )
            self.compress_btn.configure(state="normal")
            self.status_label.configure(text=f"Ready: {os.path.basename(file_path)}")
            self.progress.set(0)
            file_size = os.path.getsize(file_path)
            self.stats_labels["Original Size"].configure(text=format_bytes(file_size))
            self.stats_labels["Compressed Size"].configure(text="0 B")
            self.stats_labels["Space Saved"].configure(text="0%")
            self.stats_labels["Time Taken"].configure(text="0s")
            debug_print(f"File size: {file_size} bytes")
        else:
            debug_print("No file selected")

    def _compress(self):
        debug_print("=== _compress START ===")
        if not self.selected_file or self.is_running:
            debug_print("Exiting early - no file or already running")
            return

        default_name = os.path.splitext(os.path.basename(self.selected_file))[0] + ".huff"
        debug_print(f"default_name: {default_name}")

        output_path = fd.asksaveasfilename(
            title="Save compressed file as",
            defaultextension=".huff",
            initialfile=default_name,
            filetypes=[("Huffman compressed", "*.huff")]
        )
        debug_print(f"output_path: {output_path}")
        if not output_path:
            debug_print("User cancelled save dialog")
            return

        debug_print("Starting compression...")
        self.is_running = True
        self.compress_btn.configure(state="disabled", text="⏳ Compressing...")
        self.status_label.configure(text="Compressing... Please wait")
        self.progress.set(0)

        def worker():
            debug_print("=== WORKER THREAD STARTED ===")
            try:
                debug_print(f"Calling compress_file with: {self.selected_file} -> {output_path}")
                stats = compress_file(
                    self.selected_file,
                    output_path,
                    progress_callback=self._update_progress
                )
                debug_print(f"compress_file returned: {stats}")
                debug_print("=== WORKER THREAD FINISHED SUCCESS ===")

                add_compression_record(
                    file_name=os.path.basename(self.selected_file),
                    file_type=get_file_type_label(self.selected_file),
                    original_size=stats['original_size'],
                    compressed_size=stats['compressed_size']
                )

                self.after(0, lambda: self._on_compress_done(output_path, stats))

            except Exception as e:
                debug_print(f"=== WORKER THREAD EXCEPTION ===")
                debug_print(f"Exception type: {type(e).__name__}")
                debug_print(f"Exception message: {str(e)}")
                debug_print("Full traceback:")
                traceback.print_exc()
                # FIX: capture the exception object properly
                self.after(0, lambda e=e: self._on_error(e))

        thread = threading.Thread(target=worker, daemon=True)
        debug_print("Starting worker thread...")
        thread.start()
        debug_print("Worker thread started (main thread continues)")

    def _update_progress(self, fraction):
        """Thread-safe progress update"""
        debug_print(f"Progress update: {fraction:.2f}")
        def update():
            self.progress.set(fraction)
        self.after(0, update)

    def _on_compress_done(self, output_path, stats):
        debug_print(f"=== _on_compress_done ===")
        self.progress.set(1.0)
        self.is_running = False
        self.compress_btn.configure(state="normal", text="▶ Compress File")
        self.status_label.configure(
            text=f"✅ Compressed to: {os.path.basename(output_path)}",
            text_color=self.theme.get("success", "#00FF00"),
        )

        self.stats_labels["Original Size"].configure(text=format_bytes(stats['original_size']))
        self.stats_labels["Compressed Size"].configure(text=format_bytes(stats['compressed_size']))
        self.stats_labels["Space Saved"].configure(text=f"{stats['ratio_percent']:.1f}%")
        self.stats_labels["Time Taken"].configure(text=f"{stats['seconds_taken']:.2f}s")

        self.show_toast(self, "Compression Complete!", "success")
        messagebox.showinfo("Success", f"File compressed successfully!\n\n"
                            f"Original:   {format_bytes(stats['original_size'])}\n"
                            f"Compressed: {format_bytes(stats['compressed_size'])}\n"
                            f"Saved:      {stats['ratio_percent']:.1f}%")

    def _on_error(self, exc):
        debug_print(f"=== _on_error ===")
        debug_print(f"Error: {exc}")
        self.is_running = False
        self.compress_btn.configure(state="normal", text="▶ Compress File")
        self.status_label.configure(
            text=f"❌ Error: {str(exc)}",
            text_color=self.theme.get("error", "#FF0000"),
        )
        self.progress.set(0)
        self.show_toast(self, f"Error: {str(exc)}", "error")
        messagebox.showerror("Compression Failed", str(exc))

    def apply_theme(self, theme):
        debug_print("apply_theme called")
        self.theme = theme
        self.configure(fg_color=theme["bg"])
        for child in self.winfo_children():
            if hasattr(child, "configure"):
                try:
                    child.configure(fg_color=theme["bg"])
                except:
                    pass

    def on_show(self):
        debug_print("on_show called")
        pass