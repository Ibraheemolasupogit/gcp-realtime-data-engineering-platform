"""Run local pipeline monitoring and reporting."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from realtime_data_platform.monitoring.alert_rules import (
    alert_counts_by_severity,
    classify_pipeline_status,
    evaluate_alerts,
)
from realtime_data_platform.monitoring.pipeline_metrics import collect_pipeline_metrics
from realtime_data_platform.reporting import write_monitoring_report, write_monitoring_summary


def run_monitoring(
    *,
    project_root: str | Path = ".",
    summary_output: str | Path = "outputs/pipeline_monitoring_summary.json",
    report_output: str | Path = "reports/pipeline_monitoring_report.md",
    thresholds: dict[str, float | int] | None = None,
) -> dict[str, Any]:
    """Generate local monitoring summary JSON and Markdown report."""
    root = Path(project_root)
    collected = collect_pipeline_metrics(root)
    metrics = collected["metrics"]
    alerts = evaluate_alerts(metrics, thresholds)
    summary = {
        "monitoring_generated_at": collected["monitoring_generated_at"],
        "pipeline_status": classify_pipeline_status(alerts, metrics),
        "metrics": metrics,
        "alerts": alerts,
        "alert_counts_by_severity": alert_counts_by_severity(alerts),
        "source_outputs_checked": collected["source_outputs_checked"],
    }

    summary_path = Path(summary_output)
    if not summary_path.is_absolute():
        summary_path = root / summary_path
    report_path = Path(report_output)
    if not report_path.is_absolute():
        report_path = root / report_path

    write_monitoring_summary(summary, summary_path)
    write_monitoring_report(summary, report_path)
    return summary
