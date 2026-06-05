"""Late-event helpers for local stream processing."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def parse_event_timestamp(value: str) -> str:
    """Normalize an ISO-8601 timestamp to UTC Z format."""
    return (
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        .astimezone(UTC)
        .isoformat()
        .replace("+00:00", "Z")
    )


def calculate_lateness_seconds(event: dict[str, Any]) -> int | None:
    """Calculate ingestion lateness in seconds when timestamps are parseable."""
    try:
        event_timestamp = datetime.fromisoformat(
            str(event["event_timestamp"]).replace("Z", "+00:00")
        ).astimezone(UTC)
        ingestion_timestamp = datetime.fromisoformat(
            str(event["ingestion_timestamp"]).replace("Z", "+00:00")
        ).astimezone(UTC)
    except (KeyError, ValueError):
        return None

    return int((ingestion_timestamp - event_timestamp).total_seconds())


def is_late_event(event: dict[str, Any], *, allowed_lateness_seconds: int) -> bool:
    """Return True when event-time lateness exceeds the configured threshold."""
    lateness_seconds = calculate_lateness_seconds(event)
    return lateness_seconds is not None and lateness_seconds > allowed_lateness_seconds
