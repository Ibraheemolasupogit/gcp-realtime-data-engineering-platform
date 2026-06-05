from pathlib import Path

from realtime_data_platform.reporting.dead_letter_report import (
    render_dead_letter_review_report,
    write_dead_letter_review_report,
)


def review_summary() -> dict:
    return {
        "total_dead_letter_events": 2,
        "counts_by_rejection_reason": {"late_event": 1, "missing_required_field": 1},
        "replayable_events": 1,
        "non_replayable_events": 1,
        "recommended_actions_by_reason": {
            "late_event": ["Replay through a controlled late-event path if business rules allow."],
            "missing_required_field": ["Repair or enrich missing critical fields before replay."],
        },
        "sample_events": [],
        "replay_candidates": [
            {
                "event_id": "event-1",
                "rejection_reason": "late_event",
                "classification_reason": "retryable_transient_or_late_event",
                "idempotency_key": "abc123",
            }
        ],
        "retry_policy": {
            "max_attempts": 3,
            "backoff_seconds": 5,
            "backoff_multiplier": 2.0,
            "retryable_reasons": ["late_event"],
            "non_retryable_reasons": ["missing_required_field"],
        },
        "reviewed_at": "2026-01-15T12:00:00Z",
    }


def test_render_dead_letter_report_contains_required_sections() -> None:
    report = render_dead_letter_review_report(review_summary())

    assert "# Dead-Letter Review Report" in report
    assert "Replayable Versus Non-Replayable Summary" in report
    assert "Retry Policy Summary" in report
    assert "GCP Reliability Mapping" in report
    assert "No live GCP reliability resources" in report


def test_write_dead_letter_report(tmp_path: Path) -> None:
    output = tmp_path / "dead_letter_report.md"

    write_dead_letter_review_report(review_summary(), output)

    assert "Dead-Letter Review Report" in output.read_text(encoding="utf-8")
