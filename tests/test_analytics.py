import csv
import json
from pathlib import Path

from realtime_data_platform.analytics import run_analytics
from realtime_data_platform.analytics.io import write_csv


def test_run_analytics_writes_dashboard_ready_outputs(tmp_path: Path) -> None:
    clean_events = tmp_path / "clean_events.jsonl"
    clean_events.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "event_timestamp": "2026-01-15T12:00:00Z",
                        "event_category": "session",
                        "event_type": "session_started",
                        "customer_id": "cust_00001",
                        "session_id": "sess_00001",
                    }
                ),
                json.dumps(
                    {
                        "event_timestamp": "2026-01-15T12:01:00Z",
                        "event_category": "transaction",
                        "event_type": "purchase_completed",
                        "customer_id": "cust_00001",
                        "session_id": "sess_00001",
                        "transaction_amount": 42.5,
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )

    summary = run_analytics(clean_events_path=clean_events, output_dir=tmp_path / "outputs")

    assert summary["clean_events_read"] == 2
    assert (tmp_path / "outputs" / "hourly_event_metrics.csv").exists()
    assert (tmp_path / "outputs" / "customer_activity_summary.csv").exists()
    assert (tmp_path / "outputs" / "product_activity_summary.csv").exists()
    assert (tmp_path / "outputs" / "transaction_value_summary.csv").exists()
    assert (tmp_path / "outputs" / "funnel_metrics.csv").exists()
    assert (tmp_path / "outputs" / "analytics_summary.json").exists()


def test_write_csv_writes_headers_for_empty_rows(tmp_path: Path) -> None:
    output = tmp_path / "empty.csv"

    write_csv(output, [], ["first", "second"])

    with output.open(encoding="utf-8", newline="") as file:
        rows = list(csv.reader(file))

    assert rows == [["first", "second"]]
