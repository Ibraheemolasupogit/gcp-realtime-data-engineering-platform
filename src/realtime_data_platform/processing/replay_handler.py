"""Dead-letter inspection and replay candidate selection."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from realtime_data_platform.processing.reliability_metadata import build_reliability_metadata
from realtime_data_platform.processing.retry_policy import RetryPolicy

REPLAYABLE_REASONS = {
    "late_event",
    "processing_error",
}
CONDITIONALLY_REPLAYABLE_REASONS = {
    "duplicate_event_id",
}
NON_REPLAYABLE_REASONS = {
    "malformed_event_record",
    "missing_required_field",
    "invalid_transaction_amount",
    "unknown_event_type",
    "malformed_identifier",
    "invalid_timestamp",
}

RECOMMENDED_ACTIONS_BY_REASON = {
    "late_event": "Replay through a controlled late-event path if business rules allow.",
    "processing_error": "Retry after confirming the processor failure was transient.",
    "duplicate_event_id": (
        "Replay only if idempotency state confirms the event was not already written."
    ),
    "malformed_event_record": "Do not replay until the JSON object shape is corrected.",
    "missing_required_field": "Repair or enrich missing critical fields before replay.",
    "invalid_transaction_amount": "Correct business-rule violations before replay.",
    "unknown_event_type": "Update schema mapping intentionally before replay.",
    "malformed_identifier": "Correct customer, product, or session identifiers before replay.",
    "invalid_timestamp": "Correct timestamp format before replay.",
}


def read_dead_letter_events(path: str | Path) -> list[dict[str, Any]]:
    """Read local dead-letter JSONL records."""
    input_path = Path(path)
    if not input_path.exists():
        return []
    with input_path.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def classify_replay_candidate(
    dead_letter_record: dict[str, Any],
    retry_policy: RetryPolicy | None = None,
) -> dict[str, Any]:
    """Classify a dead-letter record for local replay suitability."""
    policy = retry_policy or RetryPolicy()
    reason = str(dead_letter_record.get("rejection_reason", "processing_error"))

    if reason in REPLAYABLE_REASONS and policy.is_retryable(reason):
        replayable = True
        classification_reason = "retryable_transient_or_late_event"
    elif reason in CONDITIONALLY_REPLAYABLE_REASONS and policy.is_retryable(reason):
        replayable = True
        classification_reason = "conditionally_replayable_with_idempotency_check"
    elif reason in NON_REPLAYABLE_REASONS:
        replayable = False
        classification_reason = "requires_data_or_schema_repair_before_replay"
    else:
        replayable = False
        classification_reason = "unknown_rejection_reason_requires_manual_review"

    metadata = build_reliability_metadata(
        dead_letter_record,
        replayable=replayable,
        classification_reason=classification_reason,
    )
    return {
        "event_id": dead_letter_record.get("event_id"),
        "rejection_reason": reason,
        "replayable": replayable,
        "classification_reason": classification_reason,
        "recommended_action": RECOMMENDED_ACTIONS_BY_REASON.get(
            reason, "Review manually before replay."
        ),
        "retry_policy": policy.as_dict(),
        "reliability_metadata": metadata,
        "original_event": dead_letter_record.get("original_event"),
    }


def build_dead_letter_review_summary(
    dead_letter_records: list[dict[str, Any]],
    retry_policy: RetryPolicy | None = None,
) -> dict[str, Any]:
    """Build a deterministic dead-letter review summary."""
    policy = retry_policy or RetryPolicy()
    candidates = [classify_replay_candidate(record, policy) for record in dead_letter_records]
    counts_by_reason = Counter(
        record.get("rejection_reason", "unknown") for record in dead_letter_records
    )
    actions_by_reason: dict[str, set[str]] = defaultdict(set)
    for candidate in candidates:
        actions_by_reason[candidate["rejection_reason"]].add(candidate["recommended_action"])

    replayable_candidates = [candidate for candidate in candidates if candidate["replayable"]]
    non_replayable_candidates = [
        candidate for candidate in candidates if not candidate["replayable"]
    ]

    return {
        "total_dead_letter_events": len(dead_letter_records),
        "counts_by_rejection_reason": dict(sorted(counts_by_reason.items())),
        "replayable_events": len(replayable_candidates),
        "non_replayable_events": len(non_replayable_candidates),
        "recommended_actions_by_reason": {
            reason: sorted(actions) for reason, actions in sorted(actions_by_reason.items())
        },
        "sample_events": [
            {
                "event_id": candidate["event_id"],
                "rejection_reason": candidate["rejection_reason"],
                "replayable": candidate["replayable"],
                "classification_reason": candidate["classification_reason"],
                "recommended_action": candidate["recommended_action"],
            }
            for candidate in candidates[:5]
        ],
        "replay_candidates": [
            {
                "event_id": candidate["event_id"],
                "rejection_reason": candidate["rejection_reason"],
                "classification_reason": candidate["classification_reason"],
                "idempotency_key": candidate["reliability_metadata"]["idempotency_key"],
            }
            for candidate in replayable_candidates
        ],
        "retry_policy": policy.as_dict(),
        "reviewed_at": utc_now(),
    }


def simulate_replay_candidates(
    dead_letter_records: list[dict[str, Any]],
    retry_policy: RetryPolicy | None = None,
) -> list[dict[str, Any]]:
    """Return original events that are safe candidates for local replay simulation."""
    policy = retry_policy or RetryPolicy()
    candidates = [classify_replay_candidate(record, policy) for record in dead_letter_records]
    return [
        {
            "event_id": candidate["event_id"],
            "rejection_reason": candidate["rejection_reason"],
            "original_event": candidate["original_event"],
            "idempotency_key": candidate["reliability_metadata"]["idempotency_key"],
        }
        for candidate in candidates
        if candidate["replayable"]
    ]


def write_dead_letter_review_summary(summary: dict[str, Any], path: str | Path) -> None:
    """Write dead-letter review summary JSON."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")


def utc_now() -> str:
    """Return current UTC timestamp in Z format."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
