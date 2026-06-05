from realtime_data_platform.validation import EventSchemaValidator


def test_identifier_validation_for_customer_and_session_ids(valid_customer_event: dict) -> None:
    event = valid_customer_event
    event["customer_id"] = "customer-1"
    event["session_id"] = "session-1"

    result = EventSchemaValidator().validate(event)
    rules = {error.rule for error in result.errors}

    assert {"malformed_customer_id", "malformed_session_id"}.issubset(rules)


def test_product_id_validation_for_product_events(valid_customer_event: dict) -> None:
    event = {
        **valid_customer_event,
        "event_id": "event-product",
        "event_type": "product_viewed",
        "event_category": "product",
        "product_id": "product###",
    }

    result = EventSchemaValidator().validate(event)

    assert [error.rule for error in result.errors] == ["malformed_product_id"]


def test_negative_transaction_amount_is_invalid(valid_customer_event: dict) -> None:
    event = {
        **valid_customer_event,
        "event_id": "event-transaction",
        "event_type": "purchase_completed",
        "event_category": "transaction",
        "transaction_amount": -1.5,
    }

    result = EventSchemaValidator().validate(event)

    assert [error.rule for error in result.errors] == ["invalid_transaction_amount"]


def test_late_event_is_detected_from_timestamps(valid_customer_event: dict) -> None:
    event = valid_customer_event
    event["ingestion_timestamp"] = "2026-01-15T12:10:01Z"

    result = EventSchemaValidator(allowed_lateness_seconds=300).validate(event)

    assert [error.rule for error in result.errors] == ["late_event"]
    assert result.quality_score == 97
