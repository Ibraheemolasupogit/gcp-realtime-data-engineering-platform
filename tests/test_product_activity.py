from realtime_data_platform.analytics.product_activity import generate_product_activity_summary


def test_product_activity_summary_handles_missing_product_ids() -> None:
    events = [
        {"product_id": "prod_00001", "event_type": "product_viewed"},
        {"product_id": "prod_00001", "event_type": "product_added_to_basket"},
        {"product_id": "prod_00001", "event_type": "product_removed_from_basket"},
        {"product_id": "prod_00001", "event_type": "product_wishlisted"},
        {"event_type": "product_viewed"},
    ]

    rows = generate_product_activity_summary(events)

    assert rows == [
        {
            "product_id": "prod_00001",
            "product_views": 1,
            "basket_additions": 1,
            "basket_removals": 1,
            "wishlist_events": 1,
            "purchase_events": 0,
            "refund_events": 0,
        }
    ]
