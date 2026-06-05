import json
from pathlib import Path

from realtime_data_platform.validation import (
    build_quality_summary,
    validate_jsonl_files,
    write_quality_summary,
)


def test_quality_summary_output_file_is_written(tmp_path: Path) -> None:
    input_file = tmp_path / "events.jsonl"
    input_file.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "event_id": "event-1",
                        "event_type": "customer_registered",
                        "event_timestamp": "2026-01-15T12:00:00Z",
                        "ingestion_timestamp": "2026-01-15T12:00:01Z",
                        "event_source": "local.synthetic.customer",
                        "customer_id": "cust_00001",
                        "session_id": "sess_00001",
                        "event_version": "1.0",
                        "event_category": "customer",
                    }
                ),
                json.dumps(
                    {
                        "event_id": "event-1",
                        "event_type": "customer_registered",
                        "event_timestamp": "2026-01-15T12:00:00Z",
                        "ingestion_timestamp": "2026-01-15T12:00:01Z",
                        "event_source": "local.synthetic.customer",
                        "customer_id": "cust_00001",
                        "session_id": "sess_00001",
                        "event_version": "1.0",
                        "event_category": "customer",
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )
    output_file = tmp_path / "summary.json"

    results = validate_jsonl_files([input_file])
    summary = build_quality_summary(results)
    write_quality_summary(summary, output_file)

    written_summary = json.loads(output_file.read_text(encoding="utf-8"))

    assert written_summary["total_events_checked"] == 2
    assert written_summary["valid_events"] == 1
    assert written_summary["invalid_events"] == 1
    assert written_summary["duplicate_events"] == 1
    assert written_summary["error_counts_by_rule"] == {"duplicate_event_id": 1}
