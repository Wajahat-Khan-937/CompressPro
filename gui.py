"""
gui.py
------------------------------------------------------------
Tkinter GUI for the Huffman Compression Tool.

Cyberpunk styling: black background, neon green (#00FF41) text 
and accents, monospace font.

FIXED VERSION: Progress updates are now thread-safe by using
self.root.after() to schedule UI updates on the main thread.
This prevents the freeze/crash that occurred when update_idletasks()
was called directly from the worker thread.
------------------------------------------------------------
"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

import file_handler

# ---- Color palette (cyberpunk / Matrix theme) --------------------
BG_COLOR = "#0a0e0a"
PANEL_COLOR = "#0d1a0d"
NEON_GREEN = "#00FF41"
DIM_GREEN = "#0a5c1f"
TEXT_COLOR = "#c8ffc8"
FONT_MAIN = ("Consolas", 11)
FONT_TITLE = ("Consolas", 18, "bold")
FONT_BUTTON = ("Consolas", 11, "bold")


class HuffmanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("StegaCompress // Huffman Coding Tool")
        self.root.geometry("640x520")
        self.root.minsize(640, 520)
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(True, True)

        self._build_style()
        self._build_widgets()

    def _build_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "Neon.Horizontal.TProgressbar",
            troughcolor=PANEL_COLOR,
            background=NEON_GREEN,
            bordercolor=BG_COLOR,
            lightcolor=NEON_GREEN,
            darkcolor=NEON_GREEN,
        )

    def _build_widgets(self):
        title = tk.Label(
            self.root,
            text="▓▓ HUFFMAN FILE COMPRESSION ▓▓",
            font=FONT_TITLE,
            fg=NEON_GREEN,
            bg=BG_COLOR,
        )
        title.pack(pady=(20, 5))

        subtitle = tk.Label(
            self.root,
            text="Data Structures & Algorithms Project",
            font=("Consolas", 10),
            fg=DIM_GREEN,
            bg=BG_COLOR,
        )
        subtitle.pack(pady=(0, 20))

        # --- Action buttons frame ---
        button_frame = tk.Frame(self.root, bg=BG_COLOR)
        button_frame.pack(pady=10)

        self.compress_btn = self._make_button(
            button_frame, "▶ COMPRESS FILE", self.on_compress
        )
        self.compress_btn.grid(row=0, column=0, padx=10)

        self.decompress_btn = self._make_button(
            button_frame, "◀ DECOMPRESS FILE", self.on_decompress
        )
        self.decompress_btn.grid(row=0, column=1, padx=10)

        # --- Progress bar ---
        self.progress = ttk.Progressbar(
            self.root,
            style="Neon.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
        )
        self.progress.pack(pady=20, padx=20, fill="x")

        # --- Stats / log display ---
        log_frame = tk.Frame(self.root, bg=PANEL_COLOR, highlightbackground=DIM_GREEN, highlightthickness=1)
        log_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.log_text = tk.Text(
            log_frame,
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            insertbackground=NEON_GREEN,
            font=FONT_MAIN,
            wrap="word",
            relief="flat",
            padx=10,
            pady=10,
        )
        self.log_text.pack(fill="both", expand=True)
        self.log_text.insert("end", "> System ready.\n> Select a file to compress or decompress.\n")
        self.log_text.configure(state="disabled")

    def _make_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            font=FONT_BUTTON,
            fg=BG_COLOR,
            bg=NEON_GREEN,
            activebackground=DIM_GREEN,
            activeforeground=NEON_GREEN,
            relief="flat",
            padx=14,
            pady=8,
            command=command,
            cursor="hand2",
        )

    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"> {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def set_progress(self, fraction):
        """Thread-safe progress update using after()"""
        def update():
            self.progress["value"] = fraction * 100
        self.root.after(0, update)

    def set_buttons_enabled(self, enabled):
        def update():
            state = "normal" if enabled else "disabled"
            self.compress_btn.configure(state=state)
            self.decompress_btn.configure(state=state)
        self.root.after(0, update)

    def on_compress(self):
        input_path = filedialog.askopenfilename(
            title="Select a text file to compress",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not input_path:
            return

        default_name = os.path.splitext(os.path.basename(input_path))[0] + ".huff"
        output_path = filedialog.asksaveasfilename(
            title="Save compressed file as",
            defaultextension=".huff",
            initialfile=default_name,
            filetypes=[("Huffman compressed file", "*.huff")],
        )
        if not output_path:
            return

        self.log(f"Compressing: {os.path.basename(input_path)}")
        self.set_buttons_enabled(False)
        self.set_progress(0)

        def worker():
            try:
                stats = file_handler.compress_file(
                    input_path, output_path, progress_callback=self.set_progress
                )
                self.root.after(0, lambda: self._on_compress_done(output_path, stats))
            except Exception as exc:
                self.root.after(0, lambda: self._on_error(exc))

        threading.Thread(target=worker, daemon=True).start()

    def _on_compress_done(self, output_path, stats):
        self.log(f"Saved: {output_path}")
        self.log(f"Original size:   {stats['original_size']:,} bytes")
        self.log(f"Compressed size: {stats['compressed_size']:,} bytes")
        self.log(f"Space saved:     {stats['ratio_percent']:.2f}%")
        self.log(f"Time taken:      {stats['seconds_taken']:.4f}s")
        self.set_buttons_enabled(True)
        messagebox.showinfo(
            "Compression Complete",
            f"Compressed successfully!\n\n"
            f"Original:   {stats['original_size']:,} bytes\n"
            f"Compressed: {stats['compressed_size']:,} bytes\n"
            f"Saved:      {stats['ratio_percent']:.2f}%",
        )

    def on_decompress(self):
        input_path = filedialog.askopenfilename(
            title="Select a .huff file to decompress",
            filetypes=[("Huffman compressed file", "*.huff"), ("All files", "*.*")],
        )
        if not input_path:
            return

        default_name = os.path.splitext(os.path.basename(input_path))[0] + "_restored.txt"
        output_path = filedialog.asksaveasfilename(
            title="Save decompressed file as",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text files", "*.txt")],
        )
        if not output_path:
            return

        self.log(f"Decompressing: {os.path.basename(input_path)}")
        self.set_buttons_enabled(False)
        self.set_progress(0)

        def worker():
            try:
                stats = file_handler.decompress_file(
                    input_path, output_path, progress_callback=self.set_progress
                )
                self.root.after(0, lambda: self._on_decompress_done(output_path, stats))
            except Exception as exc:
                self.root.after(0, lambda: self._on_error(exc))

        threading.Thread(target=worker, daemon=True).start()

    def _on_decompress_done(self, output_path, stats):
        self.log(f"Saved: {output_path}")
        self.log(f"Restored size: {stats['decompressed_size']:,} bytes")
        self.log(f"Time taken:    {stats['seconds_taken']:.4f}s")
        self.set_buttons_enabled(True)
        messagebox.showinfo("Decompression Complete", f"File restored to:\n{output_path}")

    def _on_error(self, exc):
        self.log(f"ERROR: {exc}")
        self.set_buttons_enabled(True)
        messagebox.showerror("Error", str(exc))


def launch():
    root = tk.Tk()
    HuffmanGUI(root)
    root.mainloop()