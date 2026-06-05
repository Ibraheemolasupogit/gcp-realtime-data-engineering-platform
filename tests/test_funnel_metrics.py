from realtime_data_platform.analytics.funnel_metrics import generate_funnel_metrics


def test_funnel_metrics() -> None:
    events = [
        {"event_type": "session_started"},
        {"event_type": "session_started"},
        {"event_type": "product_viewed"},
        {"event_type": "product_added_to_basket"},
        {"event_type": "checkout_started"},
        {"event_type": "purchase_completed"},
        {"event_type": "checkout_abandoned"},
    ]

    rows = generate_funnel_metrics(events)

    assert rows == [
        {
            "sessions_started": 2,
            "product_views": 1,
            "basket_additions": 1,
            "checkout_started": 1,
            "purchases_completed": 1,
            "checkout_abandoned": 1,
            "conversion_rate": 0.5,
            "abandonment_rate": 1.0,
        }
    ]


def test_funnel_metrics_handles_empty_input() -> None:
    assert generate_funnel_metrics([])[0]["conversion_rate"] == 0.0
