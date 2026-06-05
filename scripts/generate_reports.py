"""Generate local dashboard-ready analytics outputs."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def build_arg_parser() -> argparse.ArgumentParser:
    """Build CLI arguments for local analytics generation."""
    parser = argparse.ArgumentParser(
        description="Generate local dashboard-ready analytics CSV outputs."
    )
    parser.add_argument(
        "--clean-events",
        default="outputs/clean_events.jsonl",
        help="Path to clean event JSONL input.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory for analytics CSV and summary outputs.",
    )
    return parser


def resolve_path(path: str) -> Path:
    """Resolve a path relative to the project root."""
    candidate = Path(path)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


def main(argv: list[str] | None = None) -> None:
    """Generate local analytics outputs from clean stream events."""
    from realtime_data_platform.analytics import run_analytics

    args = build_arg_parser().parse_args(argv)
    summary = run_analytics(
        clean_events_path=resolve_path(args.clean_events),
        output_dir=resolve_path(args.output_dir),
    )
    print(
        "Local analytics generation complete: "
        f"clean_events={summary['clean_events_read']} "
        f"hourly_rows={summary['hourly_metric_rows']} "
        f"customer_rows={summary['customer_activity_rows']} "
        f"product_rows={summary['product_activity_rows']} "
        f"output_dir={resolve_path(args.output_dir)}"
    )


if __name__ == "__main__":
    main()
