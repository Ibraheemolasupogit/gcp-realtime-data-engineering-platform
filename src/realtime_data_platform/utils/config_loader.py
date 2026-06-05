"""Configuration loading helpers for local YAML files."""

from pathlib import Path
from typing import Any

import yaml


def load_yaml_config(path: str | Path) -> dict[str, Any]:
    """Load a YAML configuration file from disk."""
    config_path = Path(path)
    with config_path.open(encoding="utf-8") as file:
        loaded = yaml.safe_load(file) or {}

    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping at {config_path}")

    return loaded
