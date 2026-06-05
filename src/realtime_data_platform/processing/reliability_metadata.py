"""Reliability metadata helpers for replay design."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from realtime_data_platform.processing.idempotency import generate_idempotency_key


def build_reliability_metadata(
    dead_letter_record: dict[str, Any],
    *,
    replayable: bool,
    classification_reason: str,
) -> dict[str, Any]:
    """Build deterministic reliability metadata for a dead-letter record."""
    original_event = dead_letter_record.get("original_event") or {}
    return {
        "event_id": dead_letter_record.get("event_id"),
        "rejection_reason": dead_letter_record.get("rejection_reason"),
        "replayable": replayable,
        "classification_reason": classification_reason,
        "idempotency_key": generate_idempotency_key(original_event) if original_event else None,
        "source_file": dead_letter_record.get("source_file"),
        "classified_at": utc_now(),
    }


def utc_now() -> str:
    """Return current UTC timestamp in Z format."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
