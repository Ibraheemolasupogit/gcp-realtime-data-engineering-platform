import json
from pathlib import Path

from realtime_data_platform.processing import (
    LocalStreamProcessor,
    read_jsonl,
    run_local_processing_pipeline,
)
from realtime_data_platform.publisher import InMemoryEventQueue


def queue_messages(*events: dict):
    queue = InMemoryEventQueue()
    for event in events:
        queue.publish(event, source_file="sample.jsonl")
    return queue.consume_batch()


def test_valid_event_is_transformed_to_clean_output(valid_customer_event: dict) -> None:
    processor = LocalStreamProcessor()

    clean_events, dead_letter_events, summary = processor.process_messages(
        queue_messages(valid_customer_event)
    )

    assert len(clean_events) == 1
    assert dead_letter_events == []
    assert clean_events[0]["processing_metadata"]["processing_status"] == "clean"
    assert clean_events[0]["processing_metadata"]["quality_score"] == 100
    assert summary["clean_events_written"] == 1
    assert summary["dead_letter_events_written"] == 0


def test_invalid_event_routes_to_dead_letter(valid_customer_event: dict) -> None:
    processor = LocalStreamProcessor()
    invalid_event = {**valid_customer_event}
    invalid_event.pop("customer_id")

    clean_events, dead_letter_events, summary = processor.process_messages(
        queue_messages(invalid_event)
    )

    assert clean_events == []
    assert len(dead_letter_events) == 1
    assert dead_letter_events[0]["rejection_reason"] == "missing_required_field"
    assert summary["dead_letter_events_written"] == 1


def test_duplicate_event_routes_second_record_to_dead_letter(valid_customer_event: dict) -> None:
    processor = LocalStreamProcessor()

    clean_events, dead_letter_events, summary = processor.process_messages(
        queue_messages(valid_customer_event, dict(valid_customer_event))
    )

    assert len(clean_events) == 1
    assert len(dead_letter_events) == 1
    assert dead_letter_events[0]["rejection_reason"] == "duplicate_event_id"
    assert summary["duplicate_events"] == 1


def test_late_event_routes_to_dead_letter(valid_customer_event: dict) -> None:
    processor = LocalStreamProcessor(allowed_lateness_seconds=300)
    late_event = {
        **valid_customer_event,
        "event_id": "late-event-1",
        "ingestion_timestamp": "2026-01-15T12:10:01Z",
    }

    clean_events, dead_letter_events, summary = processor.process_messages(
        queue_messages(late_event)
    )

    assert clean_events == []
    assert dead_letter_events[0]["rejection_reason"] == "late_event"
    assert summary["late_events"] == 1


def test_run_local_processing_pipeline_writes_outputs(
    tmp_path: Path,
    valid_customer_event: dict,
) -> None:
    input_file = tmp_path / "events.jsonl"
    invalid_event = {**valid_customer_event, "event_id": "event-2", "customer_id": "bad"}
    input_file.write_text(
        "\n".join(json.dumps(event) for event in [valid_customer_event, invalid_event]),
        encoding="utf-8",
    )

    result = run_local_processing_pipeline(
        input_files=[input_file],
        output_dir=tmp_path / "outputs",
        project_root=tmp_path,
    )
    outputs = result["outputs"]
    summary = result["summary"]

    assert outputs.clean_events_path.exists()
    assert outputs.dead_letter_events_path.exists()
    assert outputs.summary_path.exists()
    assert len(read_jsonl(outputs.clean_events_path)) == 1
    assert len(read_jsonl(outputs.dead_letter_events_path)) == 1
    assert summary["total_events_processed"] == 2
    assert summary["clean_events_written"] == 1
    assert summary["dead_letter_events_written"] == 1
