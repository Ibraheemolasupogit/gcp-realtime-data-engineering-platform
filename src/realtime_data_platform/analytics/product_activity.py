"""Product activity aggregations."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

PRODUCT_ACTIVITY_FIELDS = [
    "product_id",
    "product_views",
    "basket_additions",
    "basket_removals",
    "wishlist_events",
    "purchase_events",
    "refund_events",
]


def generate_product_activity_summary(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate product-level interaction summaries."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        product_id = event.get("product_id")
        if product_id:
            grouped[str(product_id)].append(event)

    rows = []
    for product_id in sorted(grouped):
        product_events = grouped[product_id]
        event_types = [event.get("event_type") for event in product_events]
        rows.append(
            {
                "product_id": product_id,
                "product_views": event_types.count("product_viewed"),
                "basket_additions": event_types.count("product_added_to_basket"),
                "basket_removals": event_types.count("product_removed_from_basket"),
                "wishlist_events": event_types.count("product_wishlisted"),
                "purchase_events": event_types.count("purchase_completed"),
                "refund_events": event_types.count("refund_requested")
                + event_types.count("refund_completed"),
            }
        )
    return rows
