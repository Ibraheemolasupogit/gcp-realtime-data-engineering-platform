import pytest


@pytest.fixture
def valid_customer_event() -> dict:
    return {
        "event_id": "event-1",
        "event_type": "customer_registered",
        "event_timestamp": "2026-01-15T12:00:00Z",
        "ingestion_timestamp": "2026-01-15T12:00:30Z",
        "event_source": "local.synthetic.customer",
        "customer_id": "cust_00001",
        "session_id": "sess_00001",
        "event_version": "1.0",
        "event_category": "customer",
    }
