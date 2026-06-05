from realtime_data_platform.processing.dead_letter_handler import (
    build_dead_letter_record,
    choose_rejection_reason,
)
from realtime_data_platform.validation import EventSchemaValidator, ValidationError


def test_choose_rejection_reason_prioritizes_malformed_identifier() -> None:
    reason = choose_rejection_reason(
        [
            ValidationError(
                rule="malformed_customer_id",
                field="customer_id",
                message="bad",
            )
        ]
    )

    assert reason == "malformed_identifier"


def test_dead_letter_record_contains_replay_metadata(valid_customer_event: dict) -> None:
    event = {**valid_customer_event, "customer_id": "bad"}
    validation_result = EventSchemaValidator().validate(event)

    record = build_dead_letter_record(
        validation_result=validation_result,
        failed_at="2026-01-15T12:01:00Z",
        source_file="sample.jsonl",
    )

    assert record["original_event"] == event
    assert record["event_id"] == event["event_id"]
    assert record["rejection_reason"] == "malformed_identifier"
    assert record["quality_score"] == 92
    assert record["source_file"] == "sample.jsonl"
    assert record["failed_at"] == "2026-01-15T12:01:00Z"
    assert record["validation_errors"][0]["rule"] == "malformed_customer_id"
    assert "recommended_action" in record
