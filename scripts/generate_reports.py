"""Generate local dashboard-ready analytics outputs."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def build_arg_parser() -> argparse.ArgumentParser:
    """Build CLI arguments for local analytics and monitoring generation."""
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
    parser.add_argument(
        "--skip-monitoring",
        action="store_true",
        help="Generate analytics outputs without monitoring summary/report outputs.",
    )
    parser.add_argument(
        "--monitoring-only",
        action="store_true",
        help="Generate only pipeline monitoring outputs from existing artifacts.",
    )
    parser.add_argument(
        "--skip-analytics-report",
        action="store_true",
        help="Skip Markdown analytics summary report generation.",
    )
    return parser


def resolve_path(path: str) -> Path:
    """Resolve a path relative to the project root."""
    candidate = Path(path)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


def main(argv: list[str] | None = None) -> None:
    """Generate local analytics and monitoring outputs from local artifacts."""
    from realtime_data_platform.analytics import run_analytics
    from realtime_data_platform.monitoring import run_monitoring
    from realtime_data_platform.reporting import (
        build_report_context,
        write_analytics_summary_report,
    )

    args = build_arg_parser().parse_args(argv)
    if not args.monitoring_only:
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

    if args.monitoring_only or not args.skip_monitoring:
        monitoring_summary = run_monitoring(project_root=PROJECT_ROOT)
        print(
            "Local monitoring generation complete: "
            f"status={monitoring_summary['pipeline_status']} "
            f"critical_alerts={monitoring_summary['alert_counts_by_severity']['critical']} "
            f"warning_alerts={monitoring_summary['alert_counts_by_severity']['warning']} "
            f"summary={PROJECT_ROOT / 'outputs/pipeline_monitoring_summary.json'} "
            f"report={PROJECT_ROOT / 'reports/pipeline_monitoring_report.md'}"
        )

    if not args.skip_analytics_report:
        context = build_report_context(PROJECT_ROOT)
        report_path = PROJECT_ROOT / "reports/analytics_summary.md"
        write_analytics_summary_report(context, report_path)
        print(f"Local analytics summary report complete: report={report_path}")


if __name__ == "__main__":
    main()
