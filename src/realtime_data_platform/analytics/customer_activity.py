"""Customer activity aggregations."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

CUSTOMER_ACTIVITY_FIELDS = [
    "customer_id",
    "total_events",
    "sessions_count",
    "first_event_timestamp",
    "last_event_timestamp",
    "purchases_count",
    "refunds_count",
    "basket_additions_count",
    "checkout_abandonments_count",
]


def generate_customer_activity_summary(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate customer-level activity summaries."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        customer_id = event.get("customer_id")
        if customer_id:
            grouped[str(customer_id)].append(event)

    rows = []
    for customer_id in sorted(grouped):
        customer_events = grouped[customer_id]
        timestamps = sorted(str(event["event_timestamp"]) for event in customer_events)
        event_types = [event.get("event_type") for event in customer_events]
        rows.append(
            {
                "customer_id": customer_id,
                "total_events": len(customer_events),
                "sessions_count": len(
                    {
                        event.get("session_id")
                        for event in customer_events
                        if event.get("session_id")
                    }
                ),
                "first_event_timestamp": timestamps[0],
                "last_event_timestamp": timestamps[-1],
                "purchases_count": event_types.count("purchase_completed"),
                "refunds_count": event_types.count("refund_requested")
                + event_types.count("refund_completed"),
                "basket_additions_count": event_types.count("product_added_to_basket"),
                "checkout_abandonments_count": event_types.count("checkout_abandoned"),
            }
        )
    return rows
