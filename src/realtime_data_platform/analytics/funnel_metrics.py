"""Retail funnel metric aggregations."""

from __future__ import annotations

from typing import Any

FUNNEL_METRICS_FIELDS = [
    "sessions_started",
    "product_views",
    "basket_additions",
    "checkout_started",
    "purchases_completed",
    "checkout_abandoned",
    "conversion_rate",
    "abandonment_rate",
]


def generate_funnel_metrics(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate a single-row retail funnel summary."""
    event_types = [event.get("event_type") for event in events]
    sessions_started = event_types.count("session_started")
    checkout_started = event_types.count("checkout_started")
    purchases_completed = event_types.count("purchase_completed")
    checkout_abandoned = event_types.count("checkout_abandoned")

    return [
        {
            "sessions_started": sessions_started,
            "product_views": event_types.count("product_viewed"),
            "basket_additions": event_types.count("product_added_to_basket"),
            "checkout_started": checkout_started,
            "purchases_completed": purchases_completed,
            "checkout_abandoned": checkout_abandoned,
            "conversion_rate": safe_rate(purchases_completed, sessions_started),
            "abandonment_rate": safe_rate(checkout_abandoned, checkout_started),
        }
    ]


def safe_rate(numerator: int, denominator: int) -> float:
    """Calculate a rounded rate, returning 0 when denominator is absent."""
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)
