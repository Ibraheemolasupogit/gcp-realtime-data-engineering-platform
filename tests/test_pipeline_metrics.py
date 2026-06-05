import json
from pathlib import Path

from realtime_data_platform.monitoring.pipeline_metrics import collect_pipeline_metrics


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_collect_pipeline_metrics_from_local_outputs(tmp_path: Path) -> None:
    outputs = tmp_path / "outputs"
    write_json(
        outputs / "stream_processing_summary.json",
        {
            "total_events_processed": 10,
            "clean_events_written": 8,
            "dead_letter_events_written": 2,
            "duplicate_events": 1,
            "late_events": 1,
            "processing_errors": 0,
        },
    )
    write_json(
        outputs / "event_quality_summary.json",
        {
            "valid_events": 8,
            "invalid_events": 2,
            "average_quality_score": 96.5,
            "quality_band": "Excellent",
        },
    )
    write_json(outputs / "analytics_summary.json", {"clean_events_read": 8})
    (outputs / "clean_events.jsonl").write_text("", encoding="utf-8")
    (outputs / "dead_letter_events.jsonl").write_text("", encoding="utf-8")
    for filename in [
        "hourly_event_metrics.csv",
        "customer_activity_summary.csv",
        "product_activity_summary.csv",
        "transaction_value_summary.csv",
        "funnel_metrics.csv",
    ]:
        (outputs / filename).write_text("header\n", encoding="utf-8")

    collected = collect_pipeline_metrics(tmp_path)
    metrics = collected["metrics"]

    assert metrics["total_events_processed"] == 10
    assert metrics["dead_letter_rate"] == 0.2
    assert metrics["duplicate_rate"] == 0.1
    assert metrics["late_event_rate"] == 0.1
    assert metrics["average_quality_score"] == 96.5
    assert metrics["clean_event_output_exists"] is True
    assert metrics["analytics_outputs_exist"] is True


def test_collect_pipeline_metrics_handles_missing_outputs(tmp_path: Path) -> None:
    metrics = collect_pipeline_metrics(tmp_path)["metrics"]

    assert metrics["total_events_processed"] == 0
    assert metrics["clean_event_output_exists"] is False
    assert metrics["dead_letter_output_exists"] is False
    assert metrics["analytics_outputs_exist"] is False
