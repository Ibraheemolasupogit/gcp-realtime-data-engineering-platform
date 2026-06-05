"""Hourly event metric aggregations."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any

HOURLY_METRICS_FIELDS = [
    "event_hour",
    "total_events",
    "unique_customers",
    "unique_sessions",
    "customer_events",
    "product_events",
    "transaction_events",
    "session_events",
]


def generate_hourly_event_metrics(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate hourly event metrics for dashboard use."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        event_hour = truncate_to_hour(str(event.get("event_timestamp", "")))
        if event_hour:
            grouped[event_hour].append(event)

    rows = []
    for event_hour in sorted(grouped):
        hour_events = grouped[event_hour]
        category_counts = Counter(event.get("event_category", "") for event in hour_events)
        rows.append(
            {
                "event_hour": event_hour,
                "total_events": len(hour_events),
                "unique_customers": len(
                    {event.get("customer_id") for event in hour_events if event.get("customer_id")}
                ),
                "unique_sessions": len(
                    {event.get("session_id") for event in hour_events if event.get("session_id")}
                ),
                "customer_events": category_counts.get("customer", 0),
                "product_events": category_counts.get("product", 0),
                "transaction_events": category_counts.get("transaction", 0),
                "session_events": category_counts.get("session", 0),
            }
        )
    return rows


def truncate_to_hour(timestamp: str) -> str:
    """Normalize an ISO timestamp to an hourly bucket."""
    if not timestamp:
        return ""
    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return parsed.replace(minute=0, second=0, microsecond=0).isoformat().replace("+00:00", "Z")
