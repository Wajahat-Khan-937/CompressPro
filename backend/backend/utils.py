"""
utils.py
------------------------------------------------------------
Shared utility helpers for formatting, paths, and file metadata.
------------------------------------------------------------
"""

import os
from datetime import datetime
from typing import Optional


def format_bytes(size: int) -> str:
    """Human-readable byte size (B, KB, MB, GB)."""
    if size < 1024:
        return f"{size} B"
    if size < 1024 ** 2:
        return f"{size / 1024:.2f} KB"
    if size < 1024 ** 3:
        return f"{size / (1024 ** 2):.2f} MB"
    return f"{size / (1024 ** 3):.2f} GB"


def get_file_extension(path: str) -> str:
    """Return lowercase extension without dot, or 'unknown'."""
    _, ext = os.path.splitext(path)
    return ext.lstrip(".").lower() or "unknown"


def get_file_type_label(path: str) -> str:
    """Map extension to a friendly file type label."""
    ext = get_file_extension(path)
    labels = {
        "pdf": "PDF Document",
        "doc": "Word Document",
        "docx": "Word Document",
        "xls": "Excel Spreadsheet",
        "xlsx": "Excel Spreadsheet",
        "ppt": "PowerPoint",
        "pptx": "PowerPoint",
        "txt": "Text File",
        "jpg": "JPEG Image",
        "jpeg": "JPEG Image",
        "png": "PNG Image",
        "bmp": "Bitmap Image",
        "gif": "GIF Image",
        "zip": "ZIP Archive",
        "huff": "Huffman Archive",
        "huf": "Huffman Archive",
    }
    return labels.get(ext, f"{ext.upper()} File" if ext != "unknown" else "Unknown")


def now_date_time() -> tuple[str, str]:
    """Return current date and time strings for history records."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")


def safe_filename(name: str) -> str:
    """Strip path separators from a filename for safe storage."""
    return os.path.basename(name).replace("\\", "_").replace("/", "_")


def compression_ratio(original: int, compressed: int) -> float:
    """Percentage of space saved; 0 if original is zero."""
    if original <= 0:
        return 0.0
    return max(0.0, (1 - compressed / original) * 100)
