"""Run a local Pub/Sub-style publish and consume simulation."""

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

DEFAULT_INPUT_FILES = (
    "data/sample/customer_events.jsonl",
    "data/sample/product_events.jsonl",
    "data/sample/transaction_events.jsonl",
    "data/sample/session_events.jsonl",
)


def build_arg_parser() -> argparse.ArgumentParser:
    """Build CLI arguments for the local queue simulation."""
    parser = argparse.ArgumentParser(
        description="Run a local Pub/Sub-style publisher and consumer simulation."
    )
    parser.add_argument(
        "--input",
        action="append",
        dest="inputs",
        help="JSONL input file to publish. Can be provided multiple times.",
    )
    parser.add_argument(
        "--event-rate",
        type=float,
        default=0,
        help="Publish rate in events per second. Use 0 for no delay.",
    )
    parser.add_argument(
        "--replay",
        action="store_true",
        help="Publish each input file twice to demonstrate deterministic replay.",
    )
    parser.add_argument(
        "--max-events",
        type=int,
        help="Maximum number of queued messages to consume.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable publish and consume activity logs.",
    )
    return parser


def resolve_input_files(paths: list[str] | None) -> list[Path]:
    """Resolve input file paths relative to the project root."""
    selected_paths = paths or list(DEFAULT_INPUT_FILES)
    return [
        Path(path) if Path(path).is_absolute() else PROJECT_ROOT / path for path in selected_paths
    ]


def main(argv: list[str] | None = None) -> None:
    """Publish sample JSONL events into a local queue and consume them."""
    from realtime_data_platform.consumer import LocalEventConsumer
    from realtime_data_platform.publisher import InMemoryEventQueue, LocalEventPublisher

    args = build_arg_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s - %(message)s",
    )

    queue = InMemoryEventQueue(topic_name="local-retail-events")
    publisher = LocalEventPublisher(queue, event_rate_per_second=args.event_rate)
    consumer = LocalEventConsumer(queue)

    input_files = resolve_input_files(args.inputs)
    published_messages = publisher.publish_jsonl_files(input_files)
    if args.replay:
        published_messages.extend(publisher.publish_jsonl_files(input_files, replay=True))

    consumed_messages = consumer.consume_batch(max_messages=args.max_events)

    print(
        "Local Pub/Sub-style simulation complete: "
        f"published={len(published_messages)} "
        f"consumed={len(consumed_messages)} "
        f"remaining={queue.size()}"
    )


if __name__ == "__main__":
    main()
