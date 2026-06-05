from pathlib import Path

from realtime_data_platform.data_generation import (
    CUSTOMER_EVENT_TYPES,
    PRODUCT_EVENT_TYPES,
    REQUIRED_SHARED_FIELDS,
    SESSION_EVENT_TYPES,
    TRANSACTION_EVENT_TYPES,
    generate_events,
    read_jsonl,
    write_generated_events,
)
from realtime_data_platform.data_generation.events import parse_utc_timestamp


def test_generation_is_deterministic() -> None:
    config = {"seed": 123, "events_per_category": 3, "include_edge_cases": True}

    first = generate_events(config)
    second = generate_events(config)

    assert first == second


def test_generated_normal_events_have_required_shape() -> None:
    generated = generate_events({"seed": 42, "events_per_category": 5, "include_edge_cases": True})
    allowed_types = {
        "customer": set(CUSTOMER_EVENT_TYPES),
        "product": set(PRODUCT_EVENT_TYPES),
        "transaction": set(TRANSACTION_EVENT_TYPES),
        "session": set(SESSION_EVENT_TYPES),
    }

    for category, records in generated.items():
        normal_records = [record for record in records if record["quality_case"] == "normal"]
        assert normal_records

        for record in normal_records:
            assert set(REQUIRED_SHARED_FIELDS).issubset(record)
            assert record["event_category"] == category
            assert record["event_type"] in allowed_types[category]
            assert record["event_source"] == f"local.synthetic.{category}"
            assert record["customer_id"].startswith("cust_")
            assert record["session_id"].startswith("sess_")
            assert parse_utc_timestamp(record["event_timestamp"])
            assert parse_utc_timestamp(record["ingestion_timestamp"])


def test_intentional_edge_cases_are_generated() -> None:
    generated = generate_events({"seed": 42, "events_per_category": 5, "include_edge_cases": True})
    quality_cases = {record["quality_case"] for records in generated.values() for record in records}

    assert {
        "duplicate_event_id",
        "late_arriving_event",
        "missing_required_field",
        "invalid_timestamp",
        "unknown_event_type",
        "negative_transaction_amount",
        "malformed_customer_id",
        "malformed_product_id",
    }.issubset(quality_cases)


def test_duplicate_event_ids_are_present_for_validation_testing() -> None:
    generated = generate_events({"seed": 42, "events_per_category": 5, "include_edge_cases": True})

    for records in generated.values():
        event_ids = [record["event_id"] for record in records]
        assert len(event_ids) > len(set(event_ids))


def test_writes_expected_jsonl_files(tmp_path: Path) -> None:
    config = {
        "seed": 42,
        "events_per_category": 2,
        "include_edge_cases": False,
        "output_dir": "sample",
    }

    output_paths = write_generated_events(config, project_root=tmp_path)

    assert set(output_paths) == {"customer", "product", "transaction", "session"}
    for path in output_paths.values():
        assert path.exists()
        records = read_jsonl(path)
        assert len(records) == 2
