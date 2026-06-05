"""Deterministic event transformations for clean local outputs."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from realtime_data_platform.processing.idempotency import generate_idempotency_key
from realtime_data_platform.processing.late_event_handler import (
    calculate_lateness_seconds,
    parse_event_timestamp,
)


def transform_event(
    event: dict[str, Any],
    *,
    processed_at: str,
    quality_score: int,
    source_file: str | None = None,
) -> dict[str, Any]:
    """Transform a valid event into the clean canonical output format."""
    transformed = deepcopy(event)
    transformed["event_type"] = str(transformed["event_type"]).lower()
    transformed["event_timestamp"] = parse_event_timestamp(str(transformed["event_timestamp"]))
    transformed["ingestion_timestamp"] = parse_event_timestamp(
        str(transformed["ingestion_timestamp"])
    )
    transformed["processing_metadata"] = {
        "processed_at": processed_at,
        "processing_status": "clean",
        "quality_score": quality_score,
        "idempotency_key": generate_idempotency_key(transformed),
        "source_file": source_file,
        "lateness_seconds": calculate_lateness_seconds(transformed),
    }
    return transformed
