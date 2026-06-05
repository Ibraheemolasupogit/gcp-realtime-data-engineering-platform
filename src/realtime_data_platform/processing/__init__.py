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
from realtime_data_platform.processing.replay_handler import (
    build_dead_letter_review_summary,
    classify_replay_candidate,
    read_dead_letter_events,
    simulate_replay_candidates,
    write_dead_letter_review_summary,
)
from realtime_data_platform.processing.retry_policy import RetryPolicy
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
    "RetryPolicy",
    "build_dead_letter_record",
    "build_dead_letter_review_summary",
    "calculate_lateness_seconds",
    "classify_replay_candidate",
    "choose_rejection_reason",
    "generate_idempotency_key",
    "is_late_event",
    "read_jsonl",
    "read_dead_letter_events",
    "run_local_processing_pipeline",
    "simulate_replay_candidates",
    "transform_event",
    "write_dead_letter_review_summary",
    "write_jsonl",
]
