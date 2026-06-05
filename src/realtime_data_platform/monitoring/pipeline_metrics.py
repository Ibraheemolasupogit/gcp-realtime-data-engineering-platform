"""Collect local operational metrics from pipeline output artifacts."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from realtime_data_platform.monitoring.quality_monitor import file_exists, read_json_file

ANALYTICS_OUTPUTS = [
    "outputs/hourly_event_metrics.csv",
    "outputs/customer_activity_summary.csv",
    "outputs/product_activity_summary.csv",
    "outputs/transaction_value_summary.csv",
    "outputs/funnel_metrics.csv",
]


def collect_pipeline_metrics(project_root: str | Path = ".") -> dict[str, Any]:
    """Collect monitoring metrics from existing local outputs."""
    root = Path(project_root)
    quality_summary = read_json_file(root / "outputs/event_quality_summary.json")
    processing_summary = read_json_file(root / "outputs/stream_processing_summary.json")
    analytics_summary = read_json_file(root / "outputs/analytics_summary.json")

    total_events_processed = int(processing_summary.get("total_events_processed", 0))
    clean_events_written = int(processing_summary.get("clean_events_written", 0))
    dead_letter_events_written = int(processing_summary.get("dead_letter_events_written", 0))
    duplicate_events = int(processing_summary.get("duplicate_events", 0))
    late_events = int(processing_summary.get("late_events", 0))
    processing_errors = int(processing_summary.get("processing_errors", 0))
    invalid_events = int(quality_summary.get("invalid_events", dead_letter_events_written))
    valid_events = int(quality_summary.get("valid_events", clean_events_written))

    source_outputs_checked = {
        "clean_events": str(root / "outputs/clean_events.jsonl"),
        "dead_letter_events": str(root / "outputs/dead_letter_events.jsonl"),
        "event_quality_summary": str(root / "outputs/event_quality_summary.json"),
        "stream_processing_summary": str(root / "outputs/stream_processing_summary.json"),
        "analytics_summary": str(root / "outputs/analytics_summary.json"),
        "analytics_outputs": [str(root / path) for path in ANALYTICS_OUTPUTS],
    }

    metrics = {
        "total_events_processed": total_events_processed,
        "clean_events_written": clean_events_written,
        "dead_letter_events_written": dead_letter_events_written,
        "valid_events": valid_events,
        "invalid_events": invalid_events,
        "duplicate_events": duplicate_events,
        "late_events": late_events,
        "processing_errors": processing_errors,
        "error_rate": safe_rate(processing_errors, total_events_processed),
        "dead_letter_rate": safe_rate(dead_letter_events_written, total_events_processed),
        "duplicate_rate": safe_rate(duplicate_events, total_events_processed),
        "late_event_rate": safe_rate(late_events, total_events_processed),
        "average_quality_score": float(quality_summary.get("average_quality_score", 0)),
        "quality_band": quality_summary.get("quality_band", "Unknown"),
        "clean_event_output_exists": file_exists(root / "outputs/clean_events.jsonl"),
        "dead_letter_output_exists": file_exists(root / "outputs/dead_letter_events.jsonl"),
        "analytics_outputs_exist": all(file_exists(root / path) for path in ANALYTICS_OUTPUTS),
        "analytics_clean_events_read": int(analytics_summary.get("clean_events_read", 0)),
    }

    return {
        "monitoring_generated_at": utc_now(),
        "metrics": metrics,
        "source_outputs_checked": source_outputs_checked,
    }


def safe_rate(numerator: int, denominator: int) -> float:
    """Calculate a stable rate rounded for JSON output."""
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def utc_now() -> str:
    """Return current UTC timestamp in Z format."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
