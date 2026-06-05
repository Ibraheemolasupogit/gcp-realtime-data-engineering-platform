"""Dead-letter record construction for rejected local events."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from realtime_data_platform.validation import EventValidationResult, ValidationError

RECOMMENDED_ACTIONS = {
    "missing_required_field": (
        "Inspect producer schema contract and replay after required fields are fixed."
    ),
    "invalid_timestamp": "Correct timestamp format to ISO-8601 UTC before replay.",
    "unknown_event_type": "Confirm event type allow-list or update schema version intentionally.",
    "duplicate_event_id": (
        "Check idempotency state and suppress duplicate replay if already processed."
    ),
    "late_event": "Review lateness threshold or replay through a late-event recovery path.",
    "invalid_transaction_amount": (
        "Correct transaction amount business rule violation before replay."
    ),
    "malformed_identifier": "Correct identifier format before replay.",
    "malformed_event_record": "Fix JSON object shape before replay.",
    "processing_error": "Inspect processor exception and retry after code or data fix.",
}

IDENTIFIER_RULES = {
    "malformed_customer_id",
    "malformed_product_id",
    "malformed_session_id",
}


def choose_rejection_reason(errors: list[ValidationError]) -> str:
    """Choose a stable top-level dead-letter rejection reason."""
    rules = [error.rule for error in errors]
    if any(rule in IDENTIFIER_RULES for rule in rules):
        return "malformed_identifier"

    priority = (
        "malformed_event_record",
        "missing_required_field",
        "invalid_timestamp",
        "unknown_event_type",
        "duplicate_event_id",
        "late_event",
        "invalid_transaction_amount",
    )
    for rule in priority:
        if rule in rules:
            return rule
    return "processing_error"


def build_dead_letter_record(
    *,
    validation_result: EventValidationResult,
    failed_at: str,
    source_file: str | None = None,
) -> dict[str, Any]:
    """Build a structured dead-letter record from validation output."""
    rejection_reason = choose_rejection_reason(validation_result.errors)
    original_event = validation_result.event or None
    return {
        "original_event": original_event,
        "event_id": validation_result.event.get("event_id") if validation_result.event else None,
        "rejection_reason": rejection_reason,
        "validation_errors": [asdict(error) for error in validation_result.errors],
        "quality_score": validation_result.quality_score,
        "source_file": source_file,
        "failed_at": failed_at,
        "recommended_action": RECOMMENDED_ACTIONS[rejection_reason],
    }


def build_processing_error_record(
    *,
    event: dict[str, Any] | None,
    error: Exception,
    failed_at: str,
    source_file: str | None = None,
) -> dict[str, Any]:
    """Build a dead-letter record for unexpected processor failures."""
    return {
        "original_event": event,
        "event_id": event.get("event_id") if event else None,
        "rejection_reason": "processing_error",
        "validation_errors": [
            {
                "rule": "processing_error",
                "field": None,
                "message": str(error),
                "severity": "error",
                "value": None,
            }
        ],
        "quality_score": 0,
        "source_file": source_file,
        "failed_at": failed_at,
        "recommended_action": RECOMMENDED_ACTIONS["processing_error"],
    }
