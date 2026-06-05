"""Markdown monitoring report generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_monitoring_summary(summary: dict[str, Any], path: str | Path) -> None:
    """Write monitoring summary JSON."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")


def write_monitoring_report(summary: dict[str, Any], path: str | Path) -> None:
    """Write a Markdown pipeline monitoring report."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_monitoring_report(summary), encoding="utf-8")


def render_monitoring_report(summary: dict[str, Any]) -> str:
    """Render a local pipeline monitoring report as Markdown."""
    metrics = summary["metrics"]
    triggered_alerts = [alert for alert in summary["alerts"] if alert["status"] == "triggered"]
    alert_lines = (
        "\n".join(
            f"- **{alert['severity'].upper()}** `{alert['alert_name']}`: "
            f"{alert['message']} Observed `{alert['observed_value']}` "
            f"against threshold `{alert['threshold']}`."
            for alert in triggered_alerts
        )
        if triggered_alerts
        else "- No triggered alerts."
    )
    action_lines = (
        "\n".join(f"- {alert['recommended_action']}" for alert in triggered_alerts)
        if triggered_alerts
        else "- Continue running the local pipeline and monitoring checks after each change."
    )

    return f"""# Pipeline Monitoring Report

## Executive Summary

Local pipeline status is **{summary["pipeline_status"]}**.
Monitoring was generated at `{summary["monitoring_generated_at"]}` from local output
artifacts only.

## Pipeline Status

- Status: `{summary["pipeline_status"]}`
- Total events processed: `{metrics["total_events_processed"]}`
- Clean events written: `{metrics["clean_events_written"]}`
- Dead-letter events written: `{metrics["dead_letter_events_written"]}`
- Processing errors: `{metrics["processing_errors"]}`

## Key Operational Metrics

| Metric | Value |
| --- | ---: |
| Error rate | {metrics["error_rate"]} |
| Dead-letter rate | {metrics["dead_letter_rate"]} |
| Duplicate rate | {metrics["duplicate_rate"]} |
| Late-event rate | {metrics["late_event_rate"]} |
| Average quality score | {metrics["average_quality_score"]} |
| Quality band | {metrics["quality_band"]} |

## Alert Summary

{alert_lines}

Alert counts by severity:

- Critical: `{summary["alert_counts_by_severity"]["critical"]}`
- Warning: `{summary["alert_counts_by_severity"]["warning"]}`
- Info: `{summary["alert_counts_by_severity"]["info"]}`

## Data Quality Summary

- Valid events: `{metrics["valid_events"]}`
- Invalid events: `{metrics["invalid_events"]}`
- Average quality score: `{metrics["average_quality_score"]}`
- Quality band: `{metrics["quality_band"]}`

## Dead-Letter Summary

- Dead-letter events: `{metrics["dead_letter_events_written"]}`
- Dead-letter rate: `{metrics["dead_letter_rate"]}`
- Dead-letter output exists: `{metrics["dead_letter_output_exists"]}`

## Late-Event And Duplicate Summary

- Late events: `{metrics["late_events"]}`
- Late-event rate: `{metrics["late_event_rate"]}`
- Duplicate events: `{metrics["duplicate_events"]}`
- Duplicate rate: `{metrics["duplicate_rate"]}`

## Recommended Actions

{action_lines}

## GCP Monitoring Mapping

This local report maps conceptually to Cloud Logging and Cloud Monitoring.
JSON summaries are analogous to structured log entries, metric fields map to custom
monitoring metrics, and alert records map to alert policies.
In a real GCP deployment, Dataflow jobs could emit counters and structured logs,
Pub/Sub dead-letter topics could feed error metrics, and Cloud Monitoring alert
policies could notify operators.

No live GCP monitoring resources, log sinks, alert policies, dashboards, Pub/Sub
topics, Dataflow jobs, or credentials are provisioned by this milestone.
"""
