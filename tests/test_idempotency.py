from realtime_data_platform.processing import generate_idempotency_key


def test_idempotency_key_is_stable(valid_customer_event: dict) -> None:
    first_key = generate_idempotency_key(valid_customer_event)
    second_key = generate_idempotency_key(dict(valid_customer_event))

    assert first_key == second_key
    assert len(first_key) == 64


def test_idempotency_key_changes_when_event_context_changes(valid_customer_event: dict) -> None:
    changed_event = {**valid_customer_event, "session_id": "sess_99999"}

    assert generate_idempotency_key(valid_customer_event) != generate_idempotency_key(changed_event)
