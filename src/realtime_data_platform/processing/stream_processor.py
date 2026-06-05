"""Local stream processing pipeline for synthetic retail events."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from realtime_data_platform.consumer import LocalEventConsumer
from realtime_data_platform.processing.dead_letter_handler import (
    build_dead_letter_record,
    build_processing_error_record,
)
from realtime_data_platform.processing.transformations import transform_event
from realtime_data_platform.publisher import InMemoryEventQueue, LocalEventPublisher
from realtime_data_platform.publisher.queue import LocalQueueMessage
from realtime_data_platform.validation import EventSchemaValidator

DEFAULT_INPUT_FILES = (
    "data/sample/customer_events.jsonl",
    "data/sample/product_events.jsonl",
    "data/sample/transaction_events.jsonl",
    "data/sample/session_events.jsonl",
)


@dataclass(frozen=True)
class ProcessingOutputs:
    """Output paths produced by one local processing run."""

    clean_events_path: Path
    dead_letter_events_path: Path
    summary_path: Path


class LocalStreamProcessor:
    """Consume local queue messages, validate them, and route outputs."""

    def __init__(
        self,
        *,
        allowed_lateness_seconds: int = 300,
        validator: EventSchemaValidator | None = None,
    ) -> None:
        self.validator = validator or EventSchemaValidator(
            allowed_lateness_seconds=allowed_lateness_seconds
        )
        self.allowed_lateness_seconds = allowed_lateness_seconds

    def process_messages(
        self, messages: list[LocalQueueMessage]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
        """Process queued messages into clean and dead-letter collections."""
        processing_started_at = utc_now()
        clean_events: list[dict[str, Any]] = []
        dead_letter_events: list[dict[str, Any]] = []
        duplicate_events = 0
        late_events = 0
        processing_errors = 0

        for message in messages:
            processed_at = utc_now()
            try:
                validation_result = self.validator.validate(message.event)
                error_rules = {error.rule for error in validation_result.errors}
                if "duplicate_event_id" in error_rules:
                    duplicate_events += 1
                if "late_event" in error_rules:
                    late_events += 1

                if validation_result.is_valid:
                    clean_events.append(
                        transform_event(
                            validation_result.event,
                            processed_at=processed_at,
                            quality_score=validation_result.quality_score,
                            source_file=message.source_file,
                        )
                    )
                else:
                    dead_letter_events.append(
                        build_dead_letter_record(
                            validation_result=validation_result,
                            failed_at=processed_at,
                            source_file=message.source_file,
                        )
                    )
            except Exception as error:  # pragma: no cover - defensive path
                processing_errors += 1
                dead_letter_events.append(
                    build_processing_error_record(
                        event=message.event,
                        error=error,
                        failed_at=processed_at,
                        source_file=message.source_file,
                    )
                )

        processing_completed_at = utc_now()
        summary = {
            "total_events_processed": len(messages),
            "clean_events_written": len(clean_events),
            "dead_letter_events_written": len(dead_letter_events),
            "duplicate_events": duplicate_events,
            "late_events": late_events,
            "processing_errors": processing_errors,
            "processing_started_at": processing_started_at,
            "processing_completed_at": processing_completed_at,
        }
        return clean_events, dead_letter_events, summary


def run_local_processing_pipeline(
    *,
    input_files: list[str | Path] | None = None,
    output_dir: str | Path = "outputs",
    event_rate_per_second: float = 0,
    replay: bool = False,
    allowed_lateness_seconds: int = 300,
    project_root: str | Path = ".",
) -> dict[str, Any]:
    """Run the local publish, consume, validate, transform, and route flow."""
    root = Path(project_root)
    selected_inputs = input_files or list(DEFAULT_INPUT_FILES)
    resolved_inputs = [
        Path(path) if Path(path).is_absolute() else root / path for path in selected_inputs
    ]
    resolved_output_dir = Path(output_dir)
    if not resolved_output_dir.is_absolute():
        resolved_output_dir = root / resolved_output_dir

    queue = InMemoryEventQueue(topic_name="local-retail-events")
    publisher = LocalEventPublisher(queue, event_rate_per_second=event_rate_per_second)
    publisher.publish_jsonl_files(resolved_inputs)
    if replay:
        publisher.publish_jsonl_files(resolved_inputs, replay=True)

    consumer = LocalEventConsumer(queue)
    messages = consumer.consume_all()
    processor = LocalStreamProcessor(allowed_lateness_seconds=allowed_lateness_seconds)
    clean_events, dead_letter_events, summary = processor.process_messages(messages)

    outputs = ProcessingOutputs(
        clean_events_path=resolved_output_dir / "clean_events.jsonl",
        dead_letter_events_path=resolved_output_dir / "dead_letter_events.jsonl",
        summary_path=resolved_output_dir / "stream_processing_summary.json",
    )
    write_jsonl(outputs.clean_events_path, clean_events)
    write_jsonl(outputs.dead_letter_events_path, dead_letter_events)
    write_json(outputs.summary_path, summary)
    return {"outputs": outputs, "summary": summary}


def write_jsonl(path: str | Path, records: list[dict[str, Any]]) -> None:
    """Write records as newline-delimited JSON."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, sort_keys=True))
            file.write("\n")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Read newline-delimited JSON records."""
    with Path(path).open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    """Write a JSON document."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def utc_now() -> str:
    """Return the current UTC timestamp in Z format."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
