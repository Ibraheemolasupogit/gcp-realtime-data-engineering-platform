"""Data quality validation package."""

from realtime_data_platform.validation.duplicate_detector import DuplicateDetector
from realtime_data_platform.validation.quality_rules import (
    QUALITY_RULE_WEIGHTS,
    ValidationError,
    quality_band,
)
from realtime_data_platform.validation.quality_scoring import score_event, summarize_scores
from realtime_data_platform.validation.schema_validator import (
    EventSchemaValidator,
    EventValidationResult,
    build_quality_summary,
    validate_jsonl_files,
    write_quality_summary,
)

__all__ = [
    "DuplicateDetector",
    "EventSchemaValidator",
    "EventValidationResult",
    "QUALITY_RULE_WEIGHTS",
    "ValidationError",
    "build_quality_summary",
    "quality_band",
    "score_event",
    "summarize_scores",
    "validate_jsonl_files",
    "write_quality_summary",
]
