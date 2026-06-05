from realtime_data_platform.validation import DuplicateDetector, EventSchemaValidator


def test_duplicate_detector_tracks_seen_event_ids() -> None:
    detector = DuplicateDetector()

    assert detector.is_duplicate("event-1") is False
    assert detector.is_duplicate("event-1") is True
    assert detector.seen_count == 1

    detector.reset()

    assert detector.is_duplicate("event-1") is False


def test_schema_validator_reports_duplicate_event_id(valid_customer_event: dict) -> None:
    validator = EventSchemaValidator()
    event = valid_customer_event

    first = validator.validate(event)
    second = validator.validate(dict(event))

    assert first.is_valid is True
    assert second.is_valid is False
    assert [error.rule for error in second.errors] == ["duplicate_event_id"]
    assert second.quality_score == 95
