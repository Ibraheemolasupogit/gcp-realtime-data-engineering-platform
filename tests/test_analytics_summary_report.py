import json
from pathlib import Path

from realtime_data_platform.reporting import (
    build_report_context,
    detect_dashboard_sources,
    render_analytics_summary_report,
    write_analytics_summary_report,
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_detect_dashboard_sources_reports_missing_files(tmp_path: Path) -> None:
    sources = detect_dashboard_sources(tmp_path)

    assert sources["hourly_event_metrics"]["exists"] is False
    assert sources["event_quality_summary"]["exists"] is False


def test_build_report_context_handles_missing_files(tmp_path: Path) -> None:
    context = build_report_context(tmp_path)

    assert "hourly_event_metrics" in context["missing_sources"]
    assert context["analytics_summary"] == {}
    assert context["hourly_rows"] == []


def test_render_analytics_summary_report_contains_required_sections(tmp_path: Path) -> None:
    outputs = tmp_path / "outputs"
    write_json(outputs / "analytics_summary.json", {"clean_events_read": 10})
    write_json(
        outputs / "event_quality_summary.json",
        {"average_quality_score": 98.5, "quality_band": "Excellent"},
    )
    write_json(
        outputs / "pipeline_monitoring_summary.json",
        {
            "pipeline_status": "warning",
            "metrics": {"clean_events_written": 10, "dead_letter_events_written": 2},
            "alert_counts_by_severity": {"critical": 0, "warning": 1},
        },
    )
    write_json(
        outputs / "dead_letter_review_summary.json",
        {"total_dead_letter_events": 2, "replayable_events": 1, "non_replayable_events": 1},
    )

    context = build_report_context(tmp_path)
    report = render_analytics_summary_report(context)

    assert "# Analytics Summary Report" in report
    assert "Executive Summary" in report
    assert "Transaction Value Summary" in report
    assert "GCP And Looker Studio Mapping" in report
    assert "not a live Looker Studio dashboard" in report


def test_write_analytics_summary_report(tmp_path: Path) -> None:
    context = build_report_context(tmp_path)
    output = tmp_path / "reports/analytics_summary.md"

    write_analytics_summary_report(context, output)

    assert "Analytics Summary Report" in output.read_text(encoding="utf-8")
