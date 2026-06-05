"""Synthetic retail event generation for local development and tests."""

from __future__ import annotations

import argparse
import json
import random
import uuid
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from realtime_data_platform.utils.config_loader import load_yaml_config

EventRecord = dict[str, Any]

CUSTOMER_EVENT_TYPES = (
    "customer_registered",
    "customer_logged_in",
    "customer_profile_updated",
    "customer_marketing_opt_in",
    "customer_marketing_opt_out",
)
PRODUCT_EVENT_TYPES = (
    "product_viewed",
    "product_added_to_basket",
    "product_removed_from_basket",
    "product_wishlisted",
)
TRANSACTION_EVENT_TYPES = (
    "purchase_completed",
    "payment_failed",
    "refund_requested",
    "refund_completed",
)
SESSION_EVENT_TYPES = (
    "session_started",
    "session_ended",
    "checkout_started",
    "checkout_abandoned",
)

EVENT_TYPES_BY_CATEGORY = {
    "customer": CUSTOMER_EVENT_TYPES,
    "product": PRODUCT_EVENT_TYPES,
    "transaction": TRANSACTION_EVENT_TYPES,
    "session": SESSION_EVENT_TYPES,
}

OUTPUT_FILES = {
    "customer": "customer_events.jsonl",
    "product": "product_events.jsonl",
    "transaction": "transaction_events.jsonl",
    "session": "session_events.jsonl",
}

REQUIRED_SHARED_FIELDS = (
    "event_id",
    "event_type",
    "event_timestamp",
    "ingestion_timestamp",
    "event_source",
    "customer_id",
    "session_id",
    "event_version",
)


def parse_utc_timestamp(value: str) -> datetime:
    """Parse an ISO-8601 timestamp with a required UTC timezone."""
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def format_utc_timestamp(value: datetime) -> str:
    """Format a datetime as a compact UTC ISO-8601 timestamp."""
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def load_generation_config(config_path: str | Path) -> dict[str, Any]:
    """Load synthetic event generation config."""
    config = load_yaml_config(config_path)
    return config.get("event_generation", config)


def deterministic_event_id(category: str, seed: int, index: int) -> str:
    """Create a stable event identifier for reproducible sample data."""
    namespace = uuid.uuid5(uuid.NAMESPACE_DNS, "gcp-realtime-data-engineering-platform")
    return str(uuid.uuid5(namespace, f"{category}:{seed}:{index}"))


def build_common_fields(
    *,
    category: str,
    event_type: str,
    seed: int,
    index: int,
    event_timestamp: datetime,
    ingestion_timestamp: datetime,
    event_version: str,
) -> EventRecord:
    """Build the shared envelope used by all generated event categories."""
    customer_number = (index % 8) + 1
    session_number = (index % 10) + 1
    return {
        "event_id": deterministic_event_id(category, seed, index),
        "event_type": event_type,
        "event_timestamp": format_utc_timestamp(event_timestamp),
        "ingestion_timestamp": format_utc_timestamp(ingestion_timestamp),
        "event_source": f"local.synthetic.{category}",
        "customer_id": f"cust_{customer_number:05d}",
        "session_id": f"sess_{session_number:05d}",
        "event_version": event_version,
        "event_category": category,
        "quality_case": "normal",
    }


def add_category_fields(event: EventRecord, rng: random.Random, index: int) -> EventRecord:
    """Add category-specific attributes to an event record."""
    category = event["event_category"]
    if category == "customer":
        event.update(
            {
                "email_domain": rng.choice(["example.com", "retail.test", "customer.local"]),
                "loyalty_tier": rng.choice(["bronze", "silver", "gold"]),
                "marketing_channel": rng.choice(["email", "search", "social", "direct"]),
            }
        )
    elif category == "product":
        event.update(
            {
                "product_id": f"prod_{(index % 9) + 1:05d}",
                "product_category": rng.choice(["apparel", "home", "electronics", "beauty"]),
                "unit_price": round(rng.uniform(8.0, 250.0), 2),
                "quantity": rng.randint(1, 3),
            }
        )
    elif category == "transaction":
        amount = round(rng.uniform(12.0, 500.0), 2)
        event.update(
            {
                "transaction_id": f"txn_{index:06d}",
                "order_id": f"ord_{index:06d}",
                "currency": "GBP",
                "transaction_amount": amount,
                "payment_method": rng.choice(["card", "wallet", "gift_card"]),
            }
        )
    elif category == "session":
        event.update(
            {
                "device_type": rng.choice(["desktop", "mobile", "tablet"]),
                "traffic_source": rng.choice(["organic", "paid_search", "email", "affiliate"]),
                "page_count": rng.randint(1, 12),
            }
        )
    else:
        raise ValueError(f"Unsupported event category: {category}")

    return event


def generate_normal_events(
    *, category: str, count: int, seed: int, base_timestamp: datetime, event_version: str
) -> list[EventRecord]:
    """Generate deterministic valid events for one category."""
    rng = random.Random(f"{seed}:{category}")
    event_types = EVENT_TYPES_BY_CATEGORY[category]
    events = []
    for index in range(count):
        event_timestamp = base_timestamp + timedelta(seconds=index * 37)
        ingestion_timestamp = event_timestamp + timedelta(seconds=rng.randint(1, 45))
        event = build_common_fields(
            category=category,
            event_type=event_types[index % len(event_types)],
            seed=seed,
            index=index,
            event_timestamp=event_timestamp,
            ingestion_timestamp=ingestion_timestamp,
            event_version=event_version,
        )
        events.append(add_category_fields(event, rng, index))
    return events


def build_edge_cases(
    *,
    category: str,
    normal_events: list[EventRecord],
    seed: int,
    base_timestamp: datetime,
    event_version: str,
    late_event_lag_minutes: int,
) -> list[EventRecord]:
    """Build intentional data quality edge cases for validation milestones."""
    if not normal_events:
        return []

    duplicate_event = dict(normal_events[0])
    duplicate_event["quality_case"] = "duplicate_event_id"
    duplicate_event["ingestion_timestamp"] = format_utc_timestamp(
        base_timestamp + timedelta(minutes=10)
    )

    late_event = build_common_fields(
        category=category,
        event_type=EVENT_TYPES_BY_CATEGORY[category][0],
        seed=seed,
        index=10_000,
        event_timestamp=base_timestamp - timedelta(minutes=late_event_lag_minutes),
        ingestion_timestamp=base_timestamp + timedelta(minutes=5),
        event_version=event_version,
    )
    late_event["quality_case"] = "late_arriving_event"
    late_event = add_category_fields(late_event, random.Random(f"{seed}:{category}:late"), 10_000)

    edge_cases = [duplicate_event, late_event]

    if category == "customer":
        missing_required = dict(normal_events[1])
        missing_required["event_id"] = deterministic_event_id(category, seed, 20_001)
        missing_required["quality_case"] = "missing_required_field"
        missing_required.pop("customer_id", None)

        malformed_customer = dict(normal_events[2])
        malformed_customer["event_id"] = deterministic_event_id(category, seed, 20_002)
        malformed_customer["quality_case"] = "malformed_customer_id"
        malformed_customer["customer_id"] = "customer without stable id"
        edge_cases.extend([missing_required, malformed_customer])

    elif category == "product":
        unknown_type = dict(normal_events[1])
        unknown_type["event_id"] = deterministic_event_id(category, seed, 21_001)
        unknown_type["quality_case"] = "unknown_event_type"
        unknown_type["event_type"] = "product_color_changed"

        malformed_product = dict(normal_events[2])
        malformed_product["event_id"] = deterministic_event_id(category, seed, 21_002)
        malformed_product["quality_case"] = "malformed_product_id"
        malformed_product["product_id"] = "product###"
        edge_cases.extend([unknown_type, malformed_product])

    elif category == "transaction":
        invalid_timestamp = dict(normal_events[1])
        invalid_timestamp["event_id"] = deterministic_event_id(category, seed, 22_001)
        invalid_timestamp["quality_case"] = "invalid_timestamp"
        invalid_timestamp["event_timestamp"] = "not-a-timestamp"

        negative_amount = dict(normal_events[2])
        negative_amount["event_id"] = deterministic_event_id(category, seed, 22_002)
        negative_amount["quality_case"] = "negative_transaction_amount"
        negative_amount["transaction_amount"] = -19.99
        edge_cases.extend([invalid_timestamp, negative_amount])

    elif category == "session":
        missing_required = dict(normal_events[1])
        missing_required["event_id"] = deterministic_event_id(category, seed, 23_001)
        missing_required["quality_case"] = "missing_required_field"
        missing_required.pop("session_id", None)

        unknown_type = dict(normal_events[2])
        unknown_type["event_id"] = deterministic_event_id(category, seed, 23_002)
        unknown_type["quality_case"] = "unknown_event_type"
        unknown_type["event_type"] = "session_paused"
        edge_cases.extend([missing_required, unknown_type])

    return edge_cases


def generate_events(config: dict[str, Any]) -> dict[str, list[EventRecord]]:
    """Generate all configured synthetic event categories."""
    seed = int(config.get("seed", 42))
    count = int(config.get("events_per_category", 12))
    event_version = str(config.get("event_version", "1.0"))
    include_edge_cases = bool(config.get("include_edge_cases", True))
    late_event_lag_minutes = int(config.get("late_event_lag_minutes", 180))
    base_timestamp = parse_utc_timestamp(str(config.get("base_timestamp", "2026-01-15T12:00:00Z")))

    generated: dict[str, list[EventRecord]] = {}
    for category in EVENT_TYPES_BY_CATEGORY:
        normal_events = generate_normal_events(
            category=category,
            count=count,
            seed=seed,
            base_timestamp=base_timestamp,
            event_version=event_version,
        )
        if include_edge_cases:
            normal_events.extend(
                build_edge_cases(
                    category=category,
                    normal_events=normal_events,
                    seed=seed,
                    base_timestamp=base_timestamp,
                    event_version=event_version,
                    late_event_lag_minutes=late_event_lag_minutes,
                )
            )
        generated[category] = normal_events

    return generated


def write_jsonl(path: str | Path, records: Iterable[EventRecord]) -> None:
    """Write event records as newline-delimited JSON."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, sort_keys=True))
            file.write("\n")


def read_jsonl(path: str | Path) -> list[EventRecord]:
    """Read newline-delimited JSON event records."""
    with Path(path).open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def write_generated_events(
    config: dict[str, Any], project_root: str | Path = "."
) -> dict[str, Path]:
    """Generate and write configured sample event files."""
    root = Path(project_root)
    output_dir = root / str(config.get("output_dir", "data/sample"))
    category_config = config.get("categories", {})
    generated = generate_events(config)

    output_paths = {}
    for category, records in generated.items():
        file_name = category_config.get(category, {}).get("output_file", OUTPUT_FILES[category])
        output_path = output_dir / file_name
        write_jsonl(output_path, records)
        output_paths[category] = output_path

    return output_paths


def build_arg_parser() -> argparse.ArgumentParser:
    """Build CLI arguments for local synthetic event generation."""
    parser = argparse.ArgumentParser(
        description="Generate local synthetic retail event JSONL files."
    )
    parser.add_argument(
        "--config",
        default="configs/event_generation.yaml",
        help="Path to the event generation YAML config.",
    )
    parser.add_argument("--seed", type=int, help="Override the configured random seed.")
    parser.add_argument(
        "--events-per-category",
        type=int,
        help="Override the configured normal event count per category.",
    )
    parser.add_argument(
        "--output-dir",
        help="Override the configured output directory.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    """Generate sample event files from the command line."""
    args = build_arg_parser().parse_args(argv)
    config = load_generation_config(args.config)

    if args.seed is not None:
        config["seed"] = args.seed
    if args.events_per_category is not None:
        config["events_per_category"] = args.events_per_category
    if args.output_dir is not None:
        config["output_dir"] = args.output_dir

    output_paths = write_generated_events(config)
    for category, path in output_paths.items():
        print(f"Wrote {category} events to {path}")


if __name__ == "__main__":
    main()
