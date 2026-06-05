"""Transaction value aggregations."""

from __future__ import annotations

from typing import Any

TRANSACTION_VALUE_FIELDS = [
    "total_purchase_value",
    "total_refund_value",
    "net_transaction_value",
    "purchase_count",
    "refund_count",
    "failed_payment_count",
    "average_purchase_value",
]


def generate_transaction_value_summary(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate a transaction value summary row."""
    purchase_values = [
        float(event.get("transaction_amount", 0))
        for event in events
        if event.get("event_type") == "purchase_completed"
    ]
    refund_values = [
        float(event.get("transaction_amount", 0))
        for event in events
        if event.get("event_type") in {"refund_requested", "refund_completed"}
    ]
    total_purchase_value = round(sum(purchase_values), 2)
    total_refund_value = round(sum(refund_values), 2)
    purchase_count = len(purchase_values)
    refund_count = len(refund_values)
    average_purchase_value = (
        round(total_purchase_value / purchase_count, 2) if purchase_count else 0.0
    )

    return [
        {
            "total_purchase_value": total_purchase_value,
            "total_refund_value": total_refund_value,
            "net_transaction_value": round(total_purchase_value - total_refund_value, 2),
            "purchase_count": purchase_count,
            "refund_count": refund_count,
            "failed_payment_count": sum(
                1 for event in events if event.get("event_type") == "payment_failed"
            ),
            "average_purchase_value": average_purchase_value,
        }
    ]
