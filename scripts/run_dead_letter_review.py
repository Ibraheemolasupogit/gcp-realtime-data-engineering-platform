"""Run local dead-letter inspection and replay candidate review."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def build_arg_parser() -> argparse.ArgumentParser:
    """Build CLI arguments for dead-letter review."""
    parser = argparse.ArgumentParser(
        description="Inspect local dead-letter events and classify replay candidates."
    )
    parser.add_argument(
        "--dead-letter-input",
        default="outputs/dead_letter_events.jsonl",
        help="Path to local dead-letter JSONL input.",
    )
    parser.add_argument(
        "--summary-output",
        default="outputs/dead_letter_review_summary.json",
        help="Path for dead-letter review summary JSON.",
    )
    parser.add_argument(
        "--report-output",
        default="reports/dead_letter_review_report.md",
        help="Path for dead-letter review Markdown report.",
    )
    return parser


def resolve_path(path: str) -> Path:
    """Resolve a path relative to the project root."""
    candidate = Path(path)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


def main(argv: list[str] | None = None) -> None:
    """Run local dead-letter inspection and write outputs."""
    from realtime_data_platform.processing import (
        build_dead_letter_review_summary,
        read_dead_letter_events,
        write_dead_letter_review_summary,
    )
    from realtime_data_platform.reporting import write_dead_letter_review_report

    args = build_arg_parser().parse_args(argv)
    dead_letter_records = read_dead_letter_events(resolve_path(args.dead_letter_input))
    summary = build_dead_letter_review_summary(dead_letter_records)
    write_dead_letter_review_summary(summary, resolve_path(args.summary_output))
    write_dead_letter_review_report(summary, resolve_path(args.report_output))
    print(
        "Local dead-letter review complete: "
        f"total={summary['total_dead_letter_events']} "
        f"replayable={summary['replayable_events']} "
        f"non_replayable={summary['non_replayable_events']} "
        f"summary={resolve_path(args.summary_output)} "
        f"report={resolve_path(args.report_output)}"
    )


if __name__ == "__main__":
    main()
