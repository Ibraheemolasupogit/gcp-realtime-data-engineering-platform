"""Idempotency helpers for local stream processing."""

from __future__ import annotations

import hashlib
import json
from typing import Any

IDEMPOTENCY_FIELDS = (
    "event_id",
    "event_type",
    "event_timestamp",
    "customer_id",
    "session_id",
)


def generate_idempotency_key(event: dict[str, Any]) -> str:
    """Generate a deterministic idempotency key from stable event context."""
    payload = {field: event.get(field) for field in IDEMPOTENCY_FIELDS}
    encoded_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded_payload).hexdigest()
