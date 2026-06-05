"""Schema validation and quality summary generation."""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from realtime_data_platform.data_generation import read_jsonl
from realtime_data_platform.validation.duplicate_detector import DuplicateDetector
from realtime_data_platform.validation.quality_rules import (
    ALL_VALID_EVENT_TYPES,
    REQUIRED_FIELD_TYPES,
    REQUIRED_FIELDS,
    ValidationError,
    infer_event_category,
)
from realtime_data_platform.validation.quality_scoring import score_event, summarize_scores

CUSTOMER_ID_PATTERN = re.compile(r"^cust_\d{5}$")
PRODUCT_ID_PATTERN = re.compile(r"^prod_\d{5}$")
SESSION_ID_PATTERN = re.compile(r"^sess_\d{5}$")


@dataclass(frozen=True)
class EventValidationResult:
    """Validation result for one event record."""

    event: dict[str, Any]
    is_valid: bool
    quality_score: int
    errors: list[ValidationError]


class EventSchemaValidator:
    """Validate local synthetic event records against schema and quality rules."""

    def __init__(
        self,
        *,
        duplicate_detector: DuplicateDetector | None = None,
        allowed_lateness_seconds: int = 300,
    ) -> None:
        self.duplicate_detector = duplicate_detector or DuplicateDetector()
        self.allowed_lateness_seconds = allowed_lateness_seconds

    def validate(self, event: object) -> EventValidationResult:
        """Validate one event record."""
        errors: list[ValidationError] = []
        if not isinstance(event, dict):
            errors.append(
                ValidationError(
                    rule="malformed_event_record",
                    field=None,
                    message="Event record must be a JSON object.",
                    value=event,
                )
            )
            return EventValidationResult(
                event={},
                is_valid=False,
                quality_score=score_event(errors),
                errors=errors,
            )

        self._validate_required_fields(event, errors)
        self._validate_types(event, errors)
        self._validate_timestamps(event, errors)
        self._validate_event_type(event, errors)
        self._validate_identifiers(event, errors)
        self._validate_transaction_amount(event, errors)
        self._validate_duplicate(event, errors)

        return EventValidationResult(
            event=event,
            is_valid=not errors,
            quality_score=score_event(errors),
            errors=errors,
        )

    def validate_many(self, events: list[object]) -> list[EventValidationResult]:
        """Validate multiple event records using the same duplicate detector."""
        return [self.validate(event) for event in events]

    def _validate_required_fields(
        self, event: dict[str, Any], errors: list[ValidationError]
    ) -> None:
        for field in REQUIRED_FIELDS:
            if field not in event:
                errors.append(
                    ValidationError(
                        rule="missing_required_field",
                        field=field,
                        message=f"Missing required field: {field}.",
                    )
                )

    def _validate_types(self, event: dict[str, Any], errors: list[ValidationError]) -> None:
        for field, expected_type in REQUIRED_FIELD_TYPES.items():
            if field in event and not isinstance(event[field], expected_type):
                errors.append(
                    ValidationError(
                        rule="invalid_data_type",
                        field=field,
                        message=f"Field {field} must be {expected_type.__name__}.",
                        value=event[field],
                    )
                )

    def _validate_timestamps(self, event: dict[str, Any], errors: list[ValidationError]) -> None:
        event_timestamp = _parse_timestamp(event.get("event_timestamp"), "event_timestamp", errors)
        ingestion_timestamp = _parse_timestamp(
            event.get("ingestion_timestamp"), "ingestion_timestamp", errors
        )
        if event_timestamp is None or ingestion_timestamp is None:
            return

        lateness_seconds = (ingestion_timestamp - event_timestamp).total_seconds()
        if lateness_seconds > self.allowed_lateness_seconds:
            errors.append(
                ValidationError(
                    rule="late_event",
                    field="event_timestamp",
                    message="Event timestamp exceeds configured allowed lateness.",
                    severity="warning",
                    value=int(lateness_seconds),
                )
            )

    def _validate_event_type(self, event: dict[str, Any], errors: list[ValidationError]) -> None:
        event_type = event.get("event_type")
        if isinstance(event_type, str) and event_type not in ALL_VALID_EVENT_TYPES:
            errors.append(
                ValidationError(
                    rule="unknown_event_type",
                    field="event_type",
                    message=f"Unknown event_type: {event_type}.",
                    value=event_type,
                )
            )

    def _validate_identifiers(self, event: dict[str, Any], errors: list[ValidationError]) -> None:
        customer_id = event.get("customer_id")
        if isinstance(customer_id, str) and not CUSTOMER_ID_PATTERN.match(customer_id):
            errors.append(
                ValidationError(
                    rule="malformed_customer_id",
                    field="customer_id",
                    message="customer_id must match cust_00000 format.",
                    value=customer_id,
                )
            )

        session_id = event.get("session_id")
        if isinstance(session_id, str) and not SESSION_ID_PATTERN.match(session_id):
            errors.append(
                ValidationError(
                    rule="malformed_session_id",
                    field="session_id",
                    message="session_id must match sess_00000 format.",
                    value=session_id,
                )
            )

        event_category = event.get("event_category") or infer_event_category(
            event.get("event_type")
        )
        product_id = event.get("product_id")
        if event_category in {"product", "transaction"} and product_id is not None:
            if not isinstance(product_id, str) or not PRODUCT_ID_PATTERN.match(product_id):
                errors.append(
                    ValidationError(
                        rule="malformed_product_id",
                        field="product_id",
                        message="product_id must match prod_00000 format.",
                        value=product_id,
                    )
                )

    def _validate_transaction_amount(
        self, event: dict[str, Any], errors: list[ValidationError]
    ) -> None:
        event_category = event.get("event_category") or infer_event_category(
            event.get("event_type")
        )
        if event_category != "transaction" or "transaction_amount" not in event:
            return

        amount = event["transaction_amount"]
        if not isinstance(amount, int | float) or amount < 0:
            errors.append(
                ValidationError(
                    rule="invalid_transaction_amount",
                    field="transaction_amount",
                    message="transaction_amount must be a non-negative number.",
                    value=amount,
                )
            )

    def _validate_duplicate(self, event: dict[str, Any], errors: list[ValidationError]) -> None:
        event_id = event.get("event_id")
        if self.duplicate_detector.is_duplicate(event_id):
            errors.append(
                ValidationError(
                    rule="duplicate_event_id",
                    field="event_id",
                    message="Duplicate event_id detected in validation run.",
                    value=event_id,
                )
            )


def validate_jsonl_files(
    paths: list[str | Path],
    *,
    allowed_lateness_seconds: int = 300,
) -> list[EventValidationResult]:
    """Validate JSONL records from one or more files."""
    validator = EventSchemaValidator(allowed_lateness_seconds=allowed_lateness_seconds)
    results = []
    for path in paths:
        results.extend(validator.validate_many(read_jsonl(path)))
    return results


def build_quality_summary(results: list[EventValidationResult]) -> dict[str, Any]:
    """Build a validation summary suitable for local JSON output."""
    scores = [result.quality_score for result in results]
    average_score, band = summarize_scores(scores)
    error_counter = Counter(error.rule for result in results for error in result.errors)
    invalid_results = [result for result in results if not result.is_valid]

    return {
        "total_events_checked": len(results),
        "valid_events": sum(result.is_valid for result in results),
        "invalid_events": len(invalid_results),
        "duplicate_events": error_counter.get("duplicate_event_id", 0),
        "malformed_events": sum(
            1
            for result in results
            if any(
                error.rule.startswith("malformed") or error.rule == "malformed_event_record"
                for error in result.errors
            )
        ),
        "average_quality_score": average_score,
        "quality_band": band,
        "error_counts_by_rule": dict(sorted(error_counter.items())),
        "invalid_event_examples": [
            {
                "event_id": result.event.get("event_id"),
                "event_type": result.event.get("event_type"),
                "quality_score": result.quality_score,
                "errors": [asdict(error) for error in result.errors],
            }
            for result in invalid_results[:5]
        ],
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }


def write_quality_summary(summary: dict[str, Any], path: str | Path) -> None:
    """Write a quality summary JSON file."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")


def _parse_timestamp(value: object, field: str, errors: list[ValidationError]) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        errors.append(
            ValidationError(
                rule="invalid_timestamp",
                field=field,
                message=f"Invalid timestamp format for {field}.",
                value=value,
            )
        )
        return None
