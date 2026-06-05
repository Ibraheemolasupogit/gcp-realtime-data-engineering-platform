from realtime_data_platform.analytics.transaction_summary import generate_transaction_value_summary


def test_transaction_value_summary() -> None:
    events = [
        {"event_type": "purchase_completed", "transaction_amount": 100},
        {"event_type": "purchase_completed", "transaction_amount": 50},
        {"event_type": "refund_completed", "transaction_amount": 25},
        {"event_type": "payment_failed", "transaction_amount": 20},
    ]

    rows = generate_transaction_value_summary(events)

    assert rows == [
        {
            "total_purchase_value": 150.0,
            "total_refund_value": 25.0,
            "net_transaction_value": 125.0,
            "purchase_count": 2,
            "refund_count": 1,
            "failed_payment_count": 1,
            "average_purchase_value": 75.0,
        }
    ]


def test_transaction_value_summary_handles_no_purchases() -> None:
    assert generate_transaction_value_summary([])[0]["average_purchase_value"] == 0.0
