"""Apache Beam / Dataflow reference pipeline skeleton.

This module is intentionally import-safe without apache-beam installed. It documents and
partially sketches how the local processing pipeline maps to a future Beam/Dataflow
implementation while keeping all execution local/design-oriented.

No GCP credentials are required. This module does not launch Dataflow, connect to Pub/Sub,
write BigQuery tables, or access Cloud Storage.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:  # Optional dependency: keep CI and imports lightweight.
    import apache_beam as beam
except ImportError:  # pragma: no cover - depends on optional local environment.
    beam = None


LOCAL_INPUT_DESCRIPTION = "Read newline-delimited JSON from local files for DirectRunner design."
PUBSUB_INPUT_PLACEHOLDER = (
    "Production placeholder: beam.io.ReadFromPubSub(topic=...) with event-time attributes."
)
BIGQUERY_OUTPUT_PLACEHOLDER = (
    "Production placeholder: beam.io.WriteToBigQuery('realtime_analytics.clean_events')."
)
DEAD_LETTER_OUTPUT_PLACEHOLDER = (
    "Production placeholder: side output to Pub/Sub dead-letter topic and BigQuery table."
)


@dataclass(frozen=True)
class ReferencePipelineConfig:
    """Configuration for the local Beam/Dataflow reference skeleton."""

    input_path: str = "data/sample/*.jsonl"
    clean_output_path: str = "outputs/beam_reference_clean_events.jsonl"
    dead_letter_output_path: str = "outputs/beam_reference_dead_letter_events.jsonl"
    allowed_lateness_seconds: int = 300
    fixed_window_seconds: int = 300
    runner: str = "DirectRunner"


def parse_json_record(record: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Parse one JSON record, returning either event or malformed dead-letter metadata."""
    try:
        parsed = json.loads(record)
    except json.JSONDecodeError as error:
        return None, {
            "original_event": record,
            "event_id": None,
            "rejection_reason": "malformed_event_record",
            "validation_errors": [
                {
                    "rule": "malformed_event_record",
                    "field": None,
                    "message": str(error),
                    "severity": "error",
                    "value": record,
                }
            ],
            "quality_score": 0,
            "source_file": None,
            "failed_at": None,
            "recommended_action": "Fix JSON object shape before replay.",
        }

    if not isinstance(parsed, dict):
        return None, {
            "original_event": parsed,
            "event_id": None,
            "rejection_reason": "malformed_event_record",
            "validation_errors": [],
            "quality_score": 0,
            "source_file": None,
            "failed_at": None,
            "recommended_action": "Fix JSON object shape before replay.",
        }
    return parsed, None


def validate_and_transform_event(
    event: dict[str, Any],
    *,
    validator: Any,
    processed_at: str,
    source_file: str | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Validate and transform one event for Beam-style clean/dead-letter routing."""
    from realtime_data_platform.processing.dead_letter_handler import build_dead_letter_record
    from realtime_data_platform.processing.transformations import transform_event

    validation_result = validator.validate(event)
    if not validation_result.is_valid:
        return None, build_dead_letter_record(
            validation_result=validation_result,
            failed_at=processed_at,
            source_file=source_file,
        )

    return (
        transform_event(
            validation_result.event,
            processed_at=processed_at,
            quality_score=validation_result.quality_score,
            source_file=source_file,
        ),
        None,
    )


def describe_reference_pipeline() -> dict[str, Any]:
    """Return a structured description of the Beam/Dataflow reference flow."""
    return {
        "runner": "DirectRunner for local design; DataflowRunner is a future deployment option.",
        "inputs": {
            "local": LOCAL_INPUT_DESCRIPTION,
            "pubsub_placeholder": PUBSUB_INPUT_PLACEHOLDER,
        },
        "transforms": [
            "Parse JSON records and route malformed records to dead-letter side output.",
            "Assign event time from event_timestamp in a future Beam implementation.",
            "Apply fixed windows for event-time aggregation design.",
            "Validate events using existing local validation rules.",
            "Route invalid, duplicate, late, or malformed records to a dead-letter side output.",
            "Transform valid events into clean canonical records with idempotency metadata.",
        ],
        "windowing": {
            "type": "FixedWindows",
            "duration_seconds": 300,
            "allowed_lateness_seconds": 300,
            "watermarking": "Future Dataflow watermark driven by Pub/Sub event-time attributes.",
        },
        "outputs": {
            "local_clean_file": "outputs/beam_reference_clean_events.jsonl",
            "local_dead_letter_file": "outputs/beam_reference_dead_letter_events.jsonl",
            "bigquery_placeholder": BIGQUERY_OUTPUT_PLACEHOLDER,
            "dead_letter_placeholder": DEAD_LETTER_OUTPUT_PLACEHOLDER,
        },
        "safety": [
            "No credentials required.",
            "No Dataflow job is launched.",
            (
                "No Pub/Sub, BigQuery, Cloud Storage, Cloud Logging, "
                "or Cloud Monitoring calls are made."
            ),
        ],
    }


def build_beam_pipeline(config: ReferencePipelineConfig) -> Any:
    """Build a local DirectRunner Beam pipeline when apache-beam is installed.

    The implementation is intentionally skeletal. It demonstrates local file input/output and
    keeps production Pub/Sub and BigQuery IO as documented placeholders.
    """
    if beam is None:
        raise RuntimeError(
            "apache-beam is not installed. This reference skeleton remains import-safe; "
            "install apache-beam separately only for local DirectRunner experimentation."
        )

    pipeline_options = beam.options.pipeline_options.PipelineOptions(
        runner=config.runner,
        save_main_session=False,
    )
    pipeline = beam.Pipeline(options=pipeline_options)

    # Local DirectRunner-safe sketch:
    # records = pipeline | "ReadLocalJsonl" >> beam.io.ReadFromText(config.input_path)
    # parsed = records | "ParseJson" >> beam.Map(parse_json_record)
    # In a full Beam implementation, parsed tuples would be split into clean/dead-letter
    # PCollections using tagged outputs, then windowed with beam.WindowInto(FixedWindows(...)).
    #
    # Production design placeholders only:
    # - beam.io.ReadFromPubSub(topic="projects/.../topics/retail-events")
    # - beam.WindowInto(beam.window.FixedWindows(config.fixed_window_seconds),
    #                   allowed_lateness=config.allowed_lateness_seconds)
    # - beam.io.WriteToBigQuery("realtime_analytics.clean_events")
    # - side output to Pub/Sub dead-letter topic and dead_letter_events table
    return pipeline


def build_arg_parser() -> argparse.ArgumentParser:
    """Build CLI arguments for the reference pipeline skeleton."""
    parser = argparse.ArgumentParser(description="Describe or build the Beam reference pipeline.")
    parser.add_argument("--describe", action="store_true", help="Print the reference design JSON.")
    parser.add_argument("--input-path", default="data/sample/*.jsonl")
    parser.add_argument("--clean-output-path", default="outputs/beam_reference_clean_events.jsonl")
    parser.add_argument(
        "--dead-letter-output-path",
        default="outputs/beam_reference_dead_letter_events.jsonl",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    """CLI entrypoint for local/design-oriented Beam reference work."""
    args = build_arg_parser().parse_args(argv)
    if args.describe:
        print(json.dumps(describe_reference_pipeline(), indent=2, sort_keys=True))
        return

    config = ReferencePipelineConfig(
        input_path=args.input_path,
        clean_output_path=args.clean_output_path,
        dead_letter_output_path=args.dead_letter_output_path,
    )
    if beam is None:
        print(json.dumps(describe_reference_pipeline(), indent=2, sort_keys=True))
        return

    pipeline = build_beam_pipeline(config)
    # Intentionally do not call pipeline.run() automatically. Running Beam pipelines should be an
    # explicit local developer action, and DataflowRunner is out of scope for this milestone.
    Path(config.clean_output_path).parent.mkdir(parents=True, exist_ok=True)
    print(f"Built Beam reference pipeline with runner={config.runner}; not executed: {pipeline!r}")


if __name__ == "__main__":
    main()
