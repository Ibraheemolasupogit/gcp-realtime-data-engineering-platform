from realtime_data_platform.analytics.hourly_metrics import generate_hourly_event_metrics


def test_hourly_metrics_generation() -> None:
    events = [
        {
            "event_timestamp": "2026-01-15T12:01:00Z",
            "event_category": "customer",
            "customer_id": "cust_00001",
            "session_id": "sess_00001",
        },
        {
            "event_timestamp": "2026-01-15T12:30:00Z",
            "event_category": "product",
            "customer_id": "cust_00001",
            "session_id": "sess_00002",
        },
        {
            "event_timestamp": "2026-01-15T13:00:00Z",
            "event_category": "transaction",
            "customer_id": "cust_00002",
            "session_id": "sess_00003",
        },
    ]

    rows = generate_hourly_event_metrics(events)

    assert rows == [
        {
            "event_hour": "2026-01-15T12:00:00Z",
            "total_events": 2,
            "unique_customers": 1,
            "unique_sessions": 2,
            "customer_events": 1,
            "product_events": 1,
            "transaction_events": 0,
            "session_events": 0,
        },
        {
            "event_hour": "2026-01-15T13:00:00Z",
            "total_events": 1,
            "unique_customers": 1,
            "unique_sessions": 1,
            "customer_events": 0,
            "product_events": 0,
            "transaction_events": 1,
            "session_events": 0,
        },
    ]


def test_hourly_metrics_handles_empty_input() -> None:
    assert generate_hourly_event_metrics([]) == []
