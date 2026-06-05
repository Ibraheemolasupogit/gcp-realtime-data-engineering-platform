"""Quality scoring helpers for event validation."""

from __future__ import annotations

from realtime_data_platform.validation.quality_rules import (
    QUALITY_RULE_WEIGHTS,
    ValidationError,
    quality_band,
)


def score_event(errors: list[ValidationError]) -> int:
    """Score an event from 0 to 100 based on validation errors."""
    penalty = sum(QUALITY_RULE_WEIGHTS.get(error.rule, 5) for error in errors)
    return max(0, 100 - penalty)


def summarize_scores(scores: list[int]) -> tuple[float, str]:
    """Return average score and quality band for a validation run."""
    if not scores:
        return 0.0, "Critical"
    average_score = round(sum(scores) / len(scores), 2)
    return average_score, quality_band(average_score)
