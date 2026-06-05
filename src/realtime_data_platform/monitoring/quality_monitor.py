"""Quality summary loading helpers for local monitoring."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json_file(path: str | Path) -> dict[str, Any]:
    """Read a JSON object, returning an empty mapping when missing."""
    input_path = Path(path)
    if not input_path.exists():
        return {}
    return json.loads(input_path.read_text(encoding="utf-8"))


def file_exists(path: str | Path) -> bool:
    """Return whether a local output file exists."""
    return Path(path).exists()
