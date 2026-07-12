"""
Backend package for the Universal File Compression System.

Contains core algorithms, file I/O, authentication, and history management.
Separated from the frontend for clean architecture and easier testing.
"""
"""
Backend package for the Universal File Compression System.
"""

from .auth import authenticate
from .compressor import compress_file, decompress_file, is_huff_archive
from .history import add_compression_record, add_decompression_record, get_dashboard_stats
from .utils import format_bytes, get_file_type_label