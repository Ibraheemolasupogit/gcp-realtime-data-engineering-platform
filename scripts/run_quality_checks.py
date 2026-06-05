"""Run local event schema validation and data quality checks."""

import argparse
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
DEFAULT_OUTPUT_FILE = "outputs/event_quality_summary.json"


def build_arg_parser() -> argparse.ArgumentParser:
    """Build CLI arguments for local quality checks."""
    parser = argparse.ArgumentParser(
        description="Validate local sample events and write a quality summary."
    )
    parser.add_argument(
        "--input",
        action="append",
        dest="inputs",
        help="JSONL input file to validate. Can be provided multiple times.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_FILE,
        help="Output JSON file for the quality summary.",
    )
    parser.add_argument(
        "--allowed-lateness-seconds",
        type=int,
        default=300,
        help="Allowed difference between ingestion_timestamp and event_timestamp.",
    )
    return parser


def resolve_paths(paths: list[str] | None) -> list[Path]:
    """Resolve paths relative to the project root."""
    selected_paths = paths or list(DEFAULT_INPUT_FILES)
    return [
        Path(path) if Path(path).is_absolute() else PROJECT_ROOT / path for path in selected_paths
    ]


def resolve_output(path: str) -> Path:
    """Resolve output path relative to the project root."""
    output_path = Path(path)
    return output_path if output_path.is_absolute() else PROJECT_ROOT / output_path


def main(argv: list[str] | None = None) -> None:
    """Validate sample events and write the local quality summary."""
    from realtime_data_platform.validation import (
        build_quality_summary,
        validate_jsonl_files,
        write_quality_summary,
    )

    args = build_arg_parser().parse_args(argv)
    input_paths = resolve_paths(args.inputs)
    output_path = resolve_output(args.output)
    results = validate_jsonl_files(
        input_paths,
        allowed_lateness_seconds=args.allowed_lateness_seconds,
    )
    summary = build_quality_summary(results)
    write_quality_summary(summary, output_path)

    print(
        "Local quality checks complete: "
        f"checked={summary['total_events_checked']} "
        f"valid={summary['valid_events']} "
        f"invalid={summary['invalid_events']} "
        f"average_score={summary['average_quality_score']} "
        f"band={summary['quality_band']} "
        f"output={output_path}"
    )


if __name__ == "__main__":
    main()
