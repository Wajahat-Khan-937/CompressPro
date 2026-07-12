"""
history.py
------------------------------------------------------------
Persistent compression and decompression history manager.

Stores records in data/history.json and supports search, clear,
and CSV export for the dashboard.
------------------------------------------------------------
"""

import csv
import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")


def _empty_store() -> Dict[str, List[Dict[str, Any]]]:
    return {"compression": [], "decompression": []}


def _load() -> Dict[str, List[Dict[str, Any]]]:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        return _empty_store()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "compression" not in data or "decompression" not in data:
            return _empty_store()
        return data
    except (json.JSONDecodeError, OSError):
        return _empty_store()


def _save(data: Dict[str, List[Dict[str, Any]]]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def add_compression_record(
    file_name: str,
    file_type: str,
    original_size: int,
    compressed_size: int,
    status: str = "Success",
) -> Dict[str, Any]:
    """Append a compression history entry and persist to disk."""
    date_str, time_str = _timestamp_parts()
    record = {
        "id": str(uuid.uuid4()),
        "file_name": file_name,
        "file_type": file_type,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "ratio_percent": round(
            (1 - compressed_size / original_size) * 100 if original_size else 0, 2
        ),
        "date": date_str,
        "time": time_str,
        "status": status,
        "timestamp": datetime.now().isoformat(),
    }
    data = _load()
    data["compression"].insert(0, record)
    _save(data)
    return record


def add_decompression_record(
    file_name: str,
    restored_size: int,
    status: str = "Success",
) -> Dict[str, Any]:
    """Append a decompression history entry and persist to disk."""
    date_str, time_str = _timestamp_parts()
    record = {
        "id": str(uuid.uuid4()),
        "file_name": file_name,
        "restored_size": restored_size,
        "date": date_str,
        "time": time_str,
        "status": status,
        "timestamp": datetime.now().isoformat(),
    }
    data = _load()
    data["decompression"].insert(0, record)
    _save(data)
    return record


def get_compression_history() -> List[Dict[str, Any]]:
    return _load()["compression"]


def get_decompression_history() -> List[Dict[str, Any]]:
    return _load()["decompression"]


def get_dashboard_stats() -> Dict[str, Any]:
    """Aggregate statistics for the dashboard page."""
    data = _load()
    compressions = data["compression"]
    decompressions = data["decompression"]

    total_saved = sum(
        max(0, r["original_size"] - r["compressed_size"])
        for r in compressions
        if r.get("status") == "Success"
    )

    recent = sorted(
        [
            {**r, "activity_type": "Compression"}
            for r in compressions
        ]
        + [
            {**r, "activity_type": "Decompression"}
            for r in decompressions
        ],
        key=lambda x: x.get("timestamp", ""),
        reverse=True,
    )[:15]

    return {
        "total_compressed": len(compressions),
        "total_decompressed": len(decompressions),
        "total_storage_saved": total_saved,
        "recent_activities": recent,
    }


def search_history(query: str) -> Dict[str, List[Dict[str, Any]]]:
    """Filter both history lists by filename substring (case-insensitive)."""
    query = query.strip().lower()
    data = _load()
    if not query:
        return data

    def _match(record: Dict[str, Any]) -> bool:
        return query in record.get("file_name", "").lower()

    return {
        "compression": [r for r in data["compression"] if _match(r)],
        "decompression": [r for r in data["decompression"] if _match(r)],
    }


def clear_history(kind: Optional[str] = None) -> None:
    """
    Clear history records.

    kind: 'compression', 'decompression', or None for all.
    """
    data = _load()
    if kind == "compression":
        data["compression"] = []
    elif kind == "decompression":
        data["decompression"] = []
    else:
        data = _empty_store()
    _save(data)


def export_to_csv(output_path: str) -> None:
    """Export combined history to a CSV file."""
    data = _load()
    rows: List[Dict[str, Any]] = []

    for r in data["compression"]:
        rows.append(
            {
                "Type": "Compression",
                "File Name": r["file_name"],
                "File Type": r.get("file_type", ""),
                "Original Size": r["original_size"],
                "Compressed Size": r["compressed_size"],
                "Ratio %": r.get("ratio_percent", ""),
                "Restored Size": "",
                "Date": r["date"],
                "Time": r["time"],
                "Status": r["status"],
            }
        )

    for r in data["decompression"]:
        rows.append(
            {
                "Type": "Decompression",
                "File Name": r["file_name"],
                "File Type": "",
                "Original Size": "",
                "Compressed Size": "",
                "Ratio %": "",
                "Restored Size": r["restored_size"],
                "Date": r["date"],
                "Time": r["time"],
                "Status": r["status"],
            }
        )

    fieldnames = [
        "Type",
        "File Name",
        "File Type",
        "Original Size",
        "Compressed Size",
        "Ratio %",
        "Restored Size",
        "Date",
        "Time",
        "Status",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _timestamp_parts() -> tuple[str, str]:
    now = datetime.now()
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")
