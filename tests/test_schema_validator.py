from realtime_data_platform.validation import EventSchemaValidator, build_quality_summary


def test_valid_event_passes_schema_validation(valid_customer_event: dict) -> None:
    result = EventSchemaValidator().validate(valid_customer_event)

    assert result.is_valid is True
    assert result.quality_score == 100
    assert result.errors == []


def test_missing_required_field_is_invalid(valid_customer_event: dict) -> None:
    event = valid_customer_event
    event.pop("customer_id")

    result = EventSchemaValidator().validate(event)

    assert result.is_valid is False
    assert result.quality_score == 90
    assert [error.rule for error in result.errors] == ["missing_required_field"]


def test_invalid_timestamp_and_unknown_event_type_are_reported(
    valid_customer_event: dict,
) -> None:
    event = valid_customer_event
    event["event_type"] = "customer_evaporated"
    event["event_timestamp"] = "not-a-timestamp"

    result = EventSchemaValidator().validate(event)
    rules = {error.rule for error in result.errors}

    assert result.is_valid is False
    assert {"invalid_timestamp", "unknown_event_type"}.issubset(rules)


def test_malformed_event_record_is_reported() -> None:
    result = EventSchemaValidator().validate(["not", "an", "object"])

    assert result.is_valid is False
    assert result.quality_score == 90
    assert result.errors[0].rule == "malformed_event_record"


def test_quality_summary_counts_invalid_examples(valid_customer_event: dict) -> None:
    validator = EventSchemaValidator()
    results = [
        validator.validate(valid_customer_event),
        validator.validate({**valid_customer_event, "event_id": "event-2", "customer_id": "bad"}),
    ]

    summary = build_quality_summary(results)

    assert summary["total_events_checked"] == 2
    assert summary["valid_events"] == 1
    assert summary["invalid_events"] == 1
    assert summary["malformed_events"] == 1
    assert summary["error_counts_by_rule"] == {"malformed_customer_id": 1}
    assert summary["invalid_event_examples"][0]["event_id"] == "event-2"
