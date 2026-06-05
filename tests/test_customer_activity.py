from realtime_data_platform.analytics.customer_activity import generate_customer_activity_summary


def test_customer_activity_summary() -> None:
    events = [
        {
            "customer_id": "cust_00001",
            "session_id": "sess_00001",
            "event_timestamp": "2026-01-15T12:00:00Z",
            "event_type": "purchase_completed",
        },
        {
            "customer_id": "cust_00001",
            "session_id": "sess_00002",
            "event_timestamp": "2026-01-15T12:05:00Z",
            "event_type": "checkout_abandoned",
        },
        {
            "customer_id": "cust_00001",
            "session_id": "sess_00002",
            "event_timestamp": "2026-01-15T12:03:00Z",
            "event_type": "product_added_to_basket",
        },
    ]

    rows = generate_customer_activity_summary(events)

    assert rows == [
        {
            "customer_id": "cust_00001",
            "total_events": 3,
            "sessions_count": 2,
            "first_event_timestamp": "2026-01-15T12:00:00Z",
            "last_event_timestamp": "2026-01-15T12:05:00Z",
            "purchases_count": 1,
            "refunds_count": 0,
            "basket_additions_count": 1,
            "checkout_abandonments_count": 1,
        }
    ]
