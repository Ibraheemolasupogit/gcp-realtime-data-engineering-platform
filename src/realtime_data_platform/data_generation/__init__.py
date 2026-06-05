"""Synthetic event generation package."""

from realtime_data_platform.data_generation.events import (
    CUSTOMER_EVENT_TYPES,
    PRODUCT_EVENT_TYPES,
    REQUIRED_SHARED_FIELDS,
    SESSION_EVENT_TYPES,
    TRANSACTION_EVENT_TYPES,
    generate_events,
    read_jsonl,
    write_generated_events,
    write_jsonl,
)

__all__ = [
    "CUSTOMER_EVENT_TYPES",
    "PRODUCT_EVENT_TYPES",
    "REQUIRED_SHARED_FIELDS",
    "SESSION_EVENT_TYPES",
    "TRANSACTION_EVENT_TYPES",
    "generate_events",
    "read_jsonl",
    "write_generated_events",
    "write_jsonl",
]
