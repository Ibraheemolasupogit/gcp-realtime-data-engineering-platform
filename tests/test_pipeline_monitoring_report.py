import json
from pathlib import Path

from realtime_data_platform.monitoring.monitoring_runner import run_monitoring
from realtime_data_platform.reporting import (
    render_monitoring_report,
    write_monitoring_report,
    write_monitoring_summary,
)


def monitoring_summary() -> dict:
    return {
        "monitoring_generated_at": "2026-01-15T12:00:00Z",
        "pipeline_status": "warning",
        "metrics": {
            "total_events_processed": 10,
            "clean_events_written": 8,
            "dead_letter_events_written": 2,
            "valid_events": 8,
            "invalid_events": 2,
            "duplicate_events": 1,
            "late_events": 1,
            "processing_errors": 0,
            "error_rate": 0.0,
            "dead_letter_rate": 0.2,
            "duplicate_rate": 0.1,
            "late_event_rate": 0.1,
            "average_quality_score": 95.0,
            "quality_band": "Excellent",
            "dead_letter_output_exists": True,
        },
        "alerts": [
            {
                "alert_name": "duplicate_rate_high",
                "severity": "warning",
                "status": "triggered",
                "metric_name": "duplicate_rate",
                "observed_value": 0.1,
                "threshold": 0.05,
                "message": "Duplicate rate high.",
                "recommended_action": "Review replay behavior.",
            }
        ],
        "alert_counts_by_severity": {"critical": 0, "warning": 1, "info": 0},
        "source_outputs_checked": {},
    }


def test_render_monitoring_report_contains_required_sections() -> None:
    report = render_monitoring_report(monitoring_summary())

    assert "# Pipeline Monitoring Report" in report
    assert "Executive Summary" in report
    assert "GCP Monitoring Mapping" in report
    assert "No live GCP monitoring resources" in report


def test_monitoring_summary_and_report_are_written(tmp_path: Path) -> None:
    summary_path = tmp_path / "summary.json"
    report_path = tmp_path / "report.md"

    write_monitoring_summary(monitoring_summary(), summary_path)
    write_monitoring_report(monitoring_summary(), report_path)

    assert json.loads(summary_path.read_text(encoding="utf-8"))["pipeline_status"] == "warning"
    assert "Pipeline Monitoring Report" in report_path.read_text(encoding="utf-8")


def test_run_monitoring_writes_outputs_from_existing_artifacts(tmp_path: Path) -> None:
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    (outputs / "clean_events.jsonl").write_text("", encoding="utf-8")
    (outputs / "dead_letter_events.jsonl").write_text("", encoding="utf-8")
    (outputs / "stream_processing_summary.json").write_text(
        json.dumps(
            {
                "total_events_processed": 10,
                "clean_events_written": 9,
                "dead_letter_events_written": 1,
                "duplicate_events": 0,
                "late_events": 0,
                "processing_errors": 0,
            }
        ),
        encoding="utf-8",
    )
    (outputs / "event_quality_summary.json").write_text(
        json.dumps(
            {
                "valid_events": 9,
                "invalid_events": 1,
                "average_quality_score": 98,
                "quality_band": "Excellent",
            }
        ),
        encoding="utf-8",
    )
    (outputs / "analytics_summary.json").write_text(
        json.dumps({"clean_events_read": 9}),
        encoding="utf-8",
    )
    for filename in [
        "hourly_event_metrics.csv",
        "customer_activity_summary.csv",
        "product_activity_summary.csv",
        "transaction_value_summary.csv",
        "funnel_metrics.csv",
    ]:
        (outputs / filename).write_text("header\n", encoding="utf-8")

    summary = run_monitoring(project_root=tmp_path)

    assert summary["metrics"]["total_events_processed"] == 10
    assert (outputs / "pipeline_monitoring_summary.json").exists()
    assert (tmp_path / "reports/pipeline_monitoring_report.md").exists()
