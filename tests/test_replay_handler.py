import json
from pathlib import Path

from realtime_data_platform.processing import (
    build_dead_letter_review_summary,
    classify_replay_candidate,
    read_dead_letter_events,
    simulate_replay_candidates,
)


def dead_letter_record(reason: str, event_id: str = "event-1") -> dict:
    return {
        "event_id": event_id,
        "rejection_reason": reason,
        "original_event": {
            "event_id": event_id,
            "event_type": "customer_registered",
            "event_timestamp": "2026-01-15T12:00:00Z",
            "customer_id": "cust_00001",
            "session_id": "sess_00001",
        },
        "source_file": "sample.jsonl",
    }


def test_read_dead_letter_events_from_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "dead_letter.jsonl"
    path.write_text(json.dumps(dead_letter_record("late_event")) + "\n", encoding="utf-8")

    records = read_dead_letter_events(path)

    assert len(records) == 1
    assert records[0]["rejection_reason"] == "late_event"


def test_replay_candidate_classification() -> None:
    late_candidate = classify_replay_candidate(dead_letter_record("late_event"))
    invalid_candidate = classify_replay_candidate(dead_letter_record("invalid_transaction_amount"))
    duplicate_candidate = classify_replay_candidate(dead_letter_record("duplicate_event_id"))

    assert late_candidate["replayable"] is True
    assert invalid_candidate["replayable"] is False
    assert duplicate_candidate["replayable"] is True
    assert duplicate_candidate["classification_reason"] == (
        "conditionally_replayable_with_idempotency_check"
    )


def test_dead_letter_review_summary_counts_reasons_and_candidates() -> None:
    records = [
        dead_letter_record("late_event", "event-1"),
        dead_letter_record("missing_required_field", "event-2"),
        dead_letter_record("duplicate_event_id", "event-3"),
    ]

    summary = build_dead_letter_review_summary(records)

    assert summary["total_dead_letter_events"] == 3
    assert summary["counts_by_rejection_reason"] == {
        "duplicate_event_id": 1,
        "late_event": 1,
        "missing_required_field": 1,
    }
    assert summary["replayable_events"] == 2
    assert summary["non_replayable_events"] == 1
    assert len(summary["sample_events"]) == 3


def test_simulate_replay_candidates_returns_original_events() -> None:
    records = [
        dead_letter_record("late_event", "event-1"),
        dead_letter_record("unknown_event_type", "event-2"),
    ]

    candidates = simulate_replay_candidates(records)

    assert len(candidates) == 1
    assert candidates[0]["event_id"] == "event-1"
    assert candidates[0]["original_event"]["event_id"] == "event-1"
