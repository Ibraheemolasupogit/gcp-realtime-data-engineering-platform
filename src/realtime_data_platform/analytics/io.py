"""Local analytics input and output helpers."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Read newline-delimited JSON records."""
    input_path = Path(path)
    if not input_path.exists():
        return []
    with input_path.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def write_csv(path: str | Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    """Write rows to CSV with stable headers."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fieldnames} for row in rows])


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    """Write a JSON document."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
