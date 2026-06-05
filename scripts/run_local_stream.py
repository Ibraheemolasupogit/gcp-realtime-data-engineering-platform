"""Run the local Pub/Sub-style stream processing pipeline."""

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
    """Build CLI arguments for the local stream processing pipeline."""
    parser = argparse.ArgumentParser(
        description="Run the local Pub/Sub-style stream processing pipeline."
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
        help="Deprecated. Processing currently consumes all queued messages.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory for clean, dead-letter, and summary outputs.",
    )
    parser.add_argument(
        "--allowed-lateness-seconds",
        type=int,
        default=300,
        help="Allowed difference between ingestion_timestamp and event_timestamp.",
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
    """Run local publish, consume, validate, transform, and route flow."""
    from realtime_data_platform.processing import run_local_processing_pipeline

    args = build_arg_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s - %(message)s",
    )

    result = run_local_processing_pipeline(
        input_files=resolve_input_files(args.inputs),
        output_dir=PROJECT_ROOT / args.output_dir,
        event_rate_per_second=args.event_rate,
        replay=args.replay,
        allowed_lateness_seconds=args.allowed_lateness_seconds,
        project_root=PROJECT_ROOT,
    )
    summary = result["summary"]
    print(
        "Local stream processing complete: "
        f"processed={summary['total_events_processed']} "
        f"clean={summary['clean_events_written']} "
        f"dead_letter={summary['dead_letter_events_written']} "
        f"duplicates={summary['duplicate_events']} "
        f"late={summary['late_events']} "
        f"output_dir={PROJECT_ROOT / args.output_dir}"
    )


if __name__ == "__main__":
    main()
