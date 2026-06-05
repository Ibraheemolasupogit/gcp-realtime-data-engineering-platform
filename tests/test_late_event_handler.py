from realtime_data_platform.processing import calculate_lateness_seconds, is_late_event


def test_lateness_is_calculated_from_event_and_ingestion_timestamps(
    valid_customer_event: dict,
) -> None:
    event = {
        **valid_customer_event,
        "event_timestamp": "2026-01-15T12:00:00Z",
        "ingestion_timestamp": "2026-01-15T12:05:01Z",
    }

    assert calculate_lateness_seconds(event) == 301
    assert is_late_event(event, allowed_lateness_seconds=300) is True


def test_on_time_event_is_not_late(valid_customer_event: dict) -> None:
    assert is_late_event(valid_customer_event, allowed_lateness_seconds=300) is False
