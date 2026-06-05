"""Analytics summary report helpers for local dashboard-ready outputs."""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DASHBOARD_SOURCE_FILES = {
    "hourly_event_metrics": "outputs/hourly_event_metrics.csv",
    "customer_activity_summary": "outputs/customer_activity_summary.csv",
    "product_activity_summary": "outputs/product_activity_summary.csv",
    "transaction_value_summary": "outputs/transaction_value_summary.csv",
    "funnel_metrics": "outputs/funnel_metrics.csv",
    "analytics_summary": "outputs/analytics_summary.json",
    "pipeline_monitoring_summary": "outputs/pipeline_monitoring_summary.json",
    "event_quality_summary": "outputs/event_quality_summary.json",
    "dead_letter_review_summary": "outputs/dead_letter_review_summary.json",
}


def detect_dashboard_sources(project_root: str | Path = ".") -> dict[str, dict[str, Any]]:
    """Detect dashboard source files and return existence metadata."""
    root = Path(project_root)
    return {
        name: {
            "path": str(root / relative_path),
            "exists": (root / relative_path).exists(),
        }
        for name, relative_path in DASHBOARD_SOURCE_FILES.items()
    }


def load_dashboard_sources(project_root: str | Path = ".") -> dict[str, Any]:
    """Load dashboard/report source artifacts with graceful missing-file handling."""
    root = Path(project_root)
    return {
        "source_status": detect_dashboard_sources(root),
        "hourly_event_metrics": read_csv_rows(
            root / DASHBOARD_SOURCE_FILES["hourly_event_metrics"]
        ),
        "customer_activity_summary": read_csv_rows(
            root / DASHBOARD_SOURCE_FILES["customer_activity_summary"]
        ),
        "product_activity_summary": read_csv_rows(
            root / DASHBOARD_SOURCE_FILES["product_activity_summary"]
        ),
        "transaction_value_summary": read_csv_rows(
            root / DASHBOARD_SOURCE_FILES["transaction_value_summary"]
        ),
        "funnel_metrics": read_csv_rows(root / DASHBOARD_SOURCE_FILES["funnel_metrics"]),
        "analytics_summary": read_json(root / DASHBOARD_SOURCE_FILES["analytics_summary"]),
        "pipeline_monitoring_summary": read_json(
            root / DASHBOARD_SOURCE_FILES["pipeline_monitoring_summary"]
        ),
        "event_quality_summary": read_json(root / DASHBOARD_SOURCE_FILES["event_quality_summary"]),
        "dead_letter_review_summary": read_json(
            root / DASHBOARD_SOURCE_FILES["dead_letter_review_summary"]
        ),
    }


def build_report_context(project_root: str | Path = ".") -> dict[str, Any]:
    """Build normalized report context from dashboard source artifacts."""
    sources = load_dashboard_sources(project_root)
    analytics_summary = sources["analytics_summary"]
    monitoring_summary = sources["pipeline_monitoring_summary"]
    quality_summary = sources["event_quality_summary"]
    dead_letter_summary = sources["dead_letter_review_summary"]
    transaction_rows = sources["transaction_value_summary"]
    funnel_rows = sources["funnel_metrics"]

    transaction_summary = transaction_rows[0] if transaction_rows else {}
    funnel_summary = funnel_rows[0] if funnel_rows else {}
    metrics = monitoring_summary.get("metrics", {})

    return {
        "generated_at": utc_now(),
        "source_status": sources["source_status"],
        "analytics_summary": analytics_summary,
        "monitoring_summary": monitoring_summary,
        "quality_summary": quality_summary,
        "dead_letter_summary": dead_letter_summary,
        "transaction_summary": transaction_summary,
        "funnel_summary": funnel_summary,
        "hourly_rows": sources["hourly_event_metrics"],
        "customer_rows": sources["customer_activity_summary"],
        "product_rows": sources["product_activity_summary"],
        "metrics": metrics,
        "missing_sources": [
            name for name, metadata in sources["source_status"].items() if not metadata["exists"]
        ],
    }


def render_analytics_summary_report(context: dict[str, Any]) -> str:
    """Render the local analytics summary Markdown report."""
    analytics_summary = context["analytics_summary"]
    quality_summary = context["quality_summary"]
    dead_letter_summary = context["dead_letter_summary"]
    monitoring_summary = context["monitoring_summary"]
    transaction_summary = context["transaction_summary"]
    funnel_summary = context["funnel_summary"]
    metrics = context["metrics"]
    missing_sources = context["missing_sources"]
    missing_line = (
        "All expected local dashboard source files were found."
        if not missing_sources
        else f"Missing source files: {', '.join(missing_sources)}."
    )

    return f"""# Analytics Summary Report

## Executive Summary

This local report summarizes dashboard-ready analytics, data quality, monitoring, and
dead-letter reliability outputs. It was generated at `{context["generated_at"]}`.

{missing_line}

## Event Volume Summary

- Clean events read by analytics: `{analytics_summary.get("clean_events_read", 0)}`
- Total events processed: `{metrics.get("total_events_processed", 0)}`
- Clean events written: `{metrics.get("clean_events_written", 0)}`
- Dead-letter events written: `{metrics.get("dead_letter_events_written", 0)}`
- Hourly metric rows: `{analytics_summary.get("hourly_metric_rows", 0)}`

## Customer Activity Summary

- Customer summary rows: `{analytics_summary.get("customer_activity_rows", 0)}`
- Top customer rows available: `{len(context["customer_rows"])}`
- Dashboard use: customer activity, sessions, purchases, refunds, basket additions,
  and checkout abandonments.

## Product Activity Summary

- Product summary rows: `{analytics_summary.get("product_activity_rows", 0)}`
- Product rows available: `{len(context["product_rows"])}`
- Dashboard use: product views, basket interactions, wishlist activity, and
  transaction-linked product metrics where available.

## Transaction Value Summary

- Total purchase value: `{transaction_summary.get("total_purchase_value", 0)}`
- Total refund value: `{transaction_summary.get("total_refund_value", 0)}`
- Net transaction value: `{transaction_summary.get("net_transaction_value", 0)}`
- Purchase count: `{transaction_summary.get("purchase_count", 0)}`
- Failed payment count: `{transaction_summary.get("failed_payment_count", 0)}`

## Funnel And Conversion Summary

- Sessions started: `{funnel_summary.get("sessions_started", 0)}`
- Product views: `{funnel_summary.get("product_views", 0)}`
- Basket additions: `{funnel_summary.get("basket_additions", 0)}`
- Checkout started: `{funnel_summary.get("checkout_started", 0)}`
- Purchases completed: `{funnel_summary.get("purchases_completed", 0)}`
- Checkout abandoned: `{funnel_summary.get("checkout_abandoned", 0)}`
- Conversion rate: `{funnel_summary.get("conversion_rate", 0)}`
- Abandonment rate: `{funnel_summary.get("abandonment_rate", 0)}`

## Data Quality Summary

- Average quality score: `{quality_summary.get("average_quality_score", 0)}`
- Quality band: `{quality_summary.get("quality_band", "Unknown")}`
- Valid events: `{quality_summary.get("valid_events", 0)}`
- Invalid events: `{quality_summary.get("invalid_events", 0)}`

## Dead-Letter And Reliability Summary

- Total dead-letter events reviewed: `{dead_letter_summary.get("total_dead_letter_events", 0)}`
- Replayable events: `{dead_letter_summary.get("replayable_events", 0)}`
- Non-replayable events: `{dead_letter_summary.get("non_replayable_events", 0)}`
- Duplicate rate: `{metrics.get("duplicate_rate", 0)}`
- Late-event rate: `{metrics.get("late_event_rate", 0)}`

## Pipeline Monitoring Summary

- Pipeline status: `{monitoring_summary.get("pipeline_status", "unknown")}`
- Critical alerts: `{monitoring_summary.get("alert_counts_by_severity", {}).get("critical", 0)}`
- Warning alerts: `{monitoring_summary.get("alert_counts_by_severity", {}).get("warning", 0)}`
- Dead-letter rate: `{metrics.get("dead_letter_rate", 0)}`
- Processing errors: `{metrics.get("processing_errors", 0)}`

## Recommended Interpretation

The local outputs are suitable for portfolio review of the platform's analytical and
operational surfaces. A high dead-letter rate in the sample data is expected because
the generated fixture intentionally includes malformed, duplicate, late, and invalid
records for validation and reliability testing.

## GCP And Looker Studio Mapping

These local CSV and JSON artifacts map conceptually to BigQuery aggregate tables and
Looker Studio dashboard panels. In a real GCP deployment, BigQuery would hold the
clean and aggregate models, Looker Studio would provide visualization, and Cloud
Monitoring would track operational health.

This is a local reporting artifact only. It is not a live Looker Studio dashboard,
does not connect to BigQuery, and does not provision GCP resources.
"""


def write_analytics_summary_report(
    context: dict[str, Any],
    path: str | Path,
) -> None:
    """Write the analytics summary Markdown report."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_analytics_summary_report(context), encoding="utf-8")


def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    """Read CSV rows, returning an empty list when the file is missing."""
    input_path = Path(path)
    if not input_path.exists():
        return []
    with input_path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def read_json(path: str | Path) -> dict[str, Any]:
    """Read a JSON object, returning an empty mapping when missing."""
    input_path = Path(path)
    if not input_path.exists():
        return {}
    return json.loads(input_path.read_text(encoding="utf-8"))


def utc_now() -> str:
    """Return current UTC timestamp in Z format."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
