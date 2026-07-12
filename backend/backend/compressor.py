"""
compressor.py
------------------------------------------------------------
Universal file compression and decompression service.

Uses Huffman coding on raw bytes so ANY file type can be handled.
The .huff format is self-contained: frequency table + metadata +
packed bit stream.

.huff file format (HUF2 — universal binary):

    [4 bytes]  magic number   b"HUF2"
    [4 bytes]  header_length  (unsigned int, little endian)
    [N bytes]  header         (pickled dict with freq_table,
                                original_filename, file_extension)
    [1 byte]   padding        (trailing zero-bits added for byte alignment)
    [M bytes]  packed data    (Huffman-encoded bits, 8 per byte)
------------------------------------------------------------
"""

import os
import pickle
import struct
import time
from typing import Callable, Dict, Optional

from backend import huffman
from backend.utils import compression_ratio, get_file_extension, safe_filename

MAGIC = b"HUF2"
LEGACY_MAGIC = b"HUF1"  # Original text-only format for backward compatibility
CHUNK_SIZE = 1024 * 1024  # 1 MB chunks for large file reads


def _bits_to_bytes(bit_string: str) -> tuple[bytes, int]:
    """Pack a bit string into bytes with end padding."""
    padding = (8 - len(bit_string) % 8) % 8
    bit_string += "0" * padding

    byte_array = bytearray()
    for i in range(0, len(bit_string), 8):
        byte_chunk = bit_string[i : i + 8]
        byte_array.append(int(byte_chunk, 2))

    return bytes(byte_array), padding


def _bytes_to_bits(data_bytes: bytes, padding: int) -> str:
    """Unpack bytes back into a bit string, stripping padding."""
    bit_string = "".join(f"{byte:08b}" for byte in data_bytes)
    if padding:
        bit_string = bit_string[:-padding]
    return bit_string


def _read_file_bytes(path: str, progress_callback: Optional[Callable[[float], None]] = None) -> bytes:
    """
    Read entire file in chunks to limit peak memory spikes.

    For Huffman encoding the full content is still required in memory,
    but chunked reading avoids a single large read syscall.
    """
    chunks = []
    total_size = os.path.getsize(path)
    read_so_far = 0

    with open(path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            chunks.append(chunk)
            read_so_far += len(chunk)
            if progress_callback and total_size > 0:
                progress_callback(0.05 + 0.15 * (read_so_far / total_size))

    return b"".join(chunks)


def compress_file(
    input_path: str,
    output_path: str,
    progress_callback: Optional[Callable[[float], None]] = None,
) -> Dict[str, float]:
    """
    Compress any file into a .huff archive using Huffman coding.

    Args:
        input_path: Path to the source file.
        output_path: Destination .huff file path.
        progress_callback: Optional callable receiving 0.0–1.0 progress.

    Returns:
        Dict with original_size, compressed_size, ratio_percent, seconds_taken.

    Raises:
        FileNotFoundError, ValueError, OSError on failure.
    """
    start_time = time.time()

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Source file not found: {input_path}")

    if progress_callback:
        progress_callback(0.02)

    data = _read_file_bytes(input_path, progress_callback)

    if not data:
        raise ValueError("Cannot compress an empty file.")

    if progress_callback:
        progress_callback(0.25)

    freq_table = huffman.build_frequency_table(data)
    tree = huffman.build_huffman_tree(freq_table)
    codes = huffman.generate_codes(tree)

    if progress_callback:
        progress_callback(0.50)

    encoded_bits = huffman.encode(data, codes)

    if progress_callback:
        progress_callback(0.70)

    packed_data, padding = _bits_to_bytes(encoded_bits)

    original_name = safe_filename(os.path.basename(input_path))
    header_payload = {
        "freq_table": freq_table,
        "original_filename": original_name,
        "file_extension": get_file_extension(input_path),
    }
    header = pickle.dumps(header_payload)

    with open(output_path, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack("<I", len(header)))
        f.write(header)
        f.write(struct.pack("<B", padding))
        f.write(packed_data)

    if progress_callback:
        progress_callback(1.0)

    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)

    return {
        "original_size": original_size,
        "compressed_size": compressed_size,
        "ratio_percent": compression_ratio(original_size, compressed_size),
        "seconds_taken": time.time() - start_time,
    }


def decompress_file(
    input_path: str,
    output_dir: str,
    output_filename: Optional[str] = None,
    progress_callback: Optional[Callable[[float], None]] = None,
) -> Dict[str, object]:
    """
    Decompress a .huff file and restore the original file.

    Args:
        input_path: Path to .huff archive.
        output_dir: Folder where restored file will be saved.
        output_filename: Optional override for restored filename.
        progress_callback: Optional progress callback (0.0–1.0).

    Returns:
        Dict with output_path, decompressed_size, seconds_taken, original_filename.

    Raises:
        ValueError if file format is invalid.
    """
    start_time = time.time()

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Archive not found: {input_path}")

    os.makedirs(output_dir, exist_ok=True)

    if progress_callback:
        progress_callback(0.10)

    with open(input_path, "rb") as f:
        magic = f.read(4)

        if magic == LEGACY_MAGIC:
            result = _decompress_legacy_huf1(f, output_dir, output_filename, progress_callback)
            result["seconds_taken"] = time.time() - start_time
            return result

        if magic != MAGIC:
            raise ValueError(
                "Invalid archive format. Please select a valid .huff file "
                "created by this application."
            )

        header_length = struct.unpack("<I", f.read(4))[0]
        header = f.read(header_length)
        header_data = pickle.loads(header)

        padding = struct.unpack("<B", f.read(1))[0]
        packed_data = f.read()

    if progress_callback:
        progress_callback(0.40)

    freq_table = header_data["freq_table"]
    original_filename = header_data.get("original_filename", "restored_file")
    file_extension = header_data.get("file_extension", "")

    bit_string = _bytes_to_bits(packed_data, padding)

    if progress_callback:
        progress_callback(0.60)

    tree = huffman.build_huffman_tree(freq_table)

    if progress_callback:
        progress_callback(0.75)

    restored_bytes = huffman.decode(bit_string, tree)

    if output_filename:
        final_name = output_filename
    else:
        final_name = original_filename
        if file_extension and not final_name.lower().endswith(f".{file_extension}"):
            base, ext = os.path.splitext(final_name)
            if not ext:
                final_name = f"{final_name}.{file_extension}"

    output_path = os.path.join(output_dir, safe_filename(final_name))

    with open(output_path, "wb") as f:
        f.write(restored_bytes)

    if progress_callback:
        progress_callback(1.0)

    return {
        "output_path": output_path,
        "decompressed_size": os.path.getsize(output_path),
        "seconds_taken": time.time() - start_time,
        "original_filename": original_filename,
    }


def _decompress_legacy_huf1(
    file_handle,
    output_dir: str,
    output_filename: Optional[str],
    progress_callback: Optional[Callable[[float], None]],
) -> Dict[str, object]:
    """
    Backward-compatible decompression for original text-only HUF1 files.
    """
    header_length = struct.unpack("<I", file_handle.read(4))[0]
    header = file_handle.read(header_length)
    freq_table = pickle.loads(header)

    padding = struct.unpack("<B", file_handle.read(1))[0]
    packed_data = file_handle.read()

    if progress_callback:
        progress_callback(0.50)

    # Legacy tables used char keys; convert to int byte keys.
    freq_table_int = {}
    for key, val in freq_table.items():
        if isinstance(key, str):
            freq_table_int[ord(key)] = val
        else:
            freq_table_int[int(key)] = val

    bit_string = _bytes_to_bits(packed_data, padding)
    tree = huffman.build_huffman_tree(freq_table_int)
    restored_bytes = huffman.decode(bit_string, tree)

    final_name = output_filename or "restored_file.txt"
    output_path = os.path.join(output_dir, safe_filename(final_name))

    with open(output_path, "wb") as f:
        f.write(restored_bytes)

    return {
        "output_path": output_path,
        "decompressed_size": os.path.getsize(output_path),
        "original_filename": final_name,
    }


def is_huff_archive(path: str) -> bool:
    """Check whether a file has a valid HUF1/HUF2 magic header."""
    try:
        with open(path, "rb") as f:
            magic = f.read(4)
        return magic in (MAGIC, LEGACY_MAGIC)
    except OSError:
        return False
