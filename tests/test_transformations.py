from realtime_data_platform.processing import transform_event


def test_transform_event_adds_processing_metadata(valid_customer_event: dict) -> None:
    event = {**valid_customer_event, "event_type": "CUSTOMER_REGISTERED"}

    transformed = transform_event(
        event,
        processed_at="2026-01-15T12:01:00Z",
        quality_score=100,
        source_file="sample.jsonl",
    )

    assert transformed["event_type"] == "customer_registered"
    assert transformed["event_timestamp"] == "2026-01-15T12:00:00Z"
    assert transformed["processing_metadata"]["processed_at"] == "2026-01-15T12:01:00Z"
    assert transformed["processing_metadata"]["processing_status"] == "clean"
    assert transformed["processing_metadata"]["quality_score"] == 100
    assert transformed["processing_metadata"]["source_file"] == "sample.jsonl"
    assert transformed["processing_metadata"]["lateness_seconds"] == 30
    assert len(transformed["processing_metadata"]["idempotency_key"]) == 64
