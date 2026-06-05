from realtime_data_platform.processing.reliability_metadata import build_reliability_metadata


def test_reliability_metadata_includes_idempotency_key(valid_customer_event: dict) -> None:
    dead_letter_record = {
        "event_id": valid_customer_event["event_id"],
        "rejection_reason": "late_event",
        "original_event": valid_customer_event,
        "source_file": "sample.jsonl",
    }

    metadata = build_reliability_metadata(
        dead_letter_record,
        replayable=True,
        classification_reason="retryable_transient_or_late_event",
    )

    assert metadata["event_id"] == valid_customer_event["event_id"]
    assert metadata["replayable"] is True
    assert len(metadata["idempotency_key"]) == 64
    assert metadata["source_file"] == "sample.jsonl"
    assert metadata["classified_at"].endswith("Z")
