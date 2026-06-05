"""Data quality rule definitions for local event validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from realtime_data_platform.data_generation import (
    CUSTOMER_EVENT_TYPES,
    PRODUCT_EVENT_TYPES,
    REQUIRED_SHARED_FIELDS,
    SESSION_EVENT_TYPES,
    TRANSACTION_EVENT_TYPES,
)

VALID_EVENT_TYPES_BY_CATEGORY = {
    "customer": set(CUSTOMER_EVENT_TYPES),
    "product": set(PRODUCT_EVENT_TYPES),
    "transaction": set(TRANSACTION_EVENT_TYPES),
    "session": set(SESSION_EVENT_TYPES),
}

ALL_VALID_EVENT_TYPES = set().union(*VALID_EVENT_TYPES_BY_CATEGORY.values())

REQUIRED_FIELD_TYPES = {
    "event_id": str,
    "event_type": str,
    "event_timestamp": str,
    "ingestion_timestamp": str,
    "event_source": str,
    "customer_id": str,
    "session_id": str,
    "event_version": str,
}

QUALITY_RULE_WEIGHTS = {
    "missing_required_field": 10,
    "invalid_data_type": 8,
    "invalid_timestamp": 8,
    "duplicate_event_id": 5,
    "late_event": 3,
    "unknown_event_type": 8,
    "invalid_transaction_amount": 10,
    "malformed_customer_id": 8,
    "malformed_product_id": 8,
    "malformed_session_id": 8,
    "malformed_event_record": 10,
}

REQUIRED_FIELDS = tuple(REQUIRED_SHARED_FIELDS)


@dataclass(frozen=True)
class ValidationError:
    """Structured validation error suitable for future dead-letter routing."""

    rule: str
    field: str | None
    message: str
    severity: str = "error"
    value: Any | None = None


def quality_band(score: float) -> str:
    """Convert a numeric quality score into a review band."""
    if score >= 95:
        return "Excellent"
    if score >= 85:
        return "Good"
    if score >= 70:
        return "Review"
    if score >= 50:
        return "Poor"
    return "Critical"


def infer_event_category(event_type: str | None) -> str | None:
    """Infer event category from a known event type."""
    if event_type is None:
        return None
    for category, event_types in VALID_EVENT_TYPES_BY_CATEGORY.items():
        if event_type in event_types:
            return category
    return None
