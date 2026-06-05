"""Local stream processing package."""

from realtime_data_platform.processing.dead_letter_handler import (
    build_dead_letter_record,
    choose_rejection_reason,
)
from realtime_data_platform.processing.idempotency import generate_idempotency_key
from realtime_data_platform.processing.late_event_handler import (
    calculate_lateness_seconds,
    is_late_event,
)
from realtime_data_platform.processing.stream_processor import (
    LocalStreamProcessor,
    ProcessingOutputs,
    read_jsonl,
    run_local_processing_pipeline,
    write_jsonl,
)
from realtime_data_platform.processing.transformations import transform_event

__all__ = [
    "LocalStreamProcessor",
    "ProcessingOutputs",
    "build_dead_letter_record",
    "calculate_lateness_seconds",
    "choose_rejection_reason",
    "generate_idempotency_key",
    "is_late_event",
    "read_jsonl",
    "run_local_processing_pipeline",
    "transform_event",
    "write_jsonl",
]
