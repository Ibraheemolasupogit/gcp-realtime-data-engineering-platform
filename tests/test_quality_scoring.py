from realtime_data_platform.validation import (
    ValidationError,
    quality_band,
    score_event,
    summarize_scores,
)


def test_score_event_applies_rule_penalties() -> None:
    score = score_event(
        [
            ValidationError(
                rule="missing_required_field",
                field="customer_id",
                message="missing",
            ),
            ValidationError(
                rule="invalid_timestamp",
                field="event_timestamp",
                message="invalid",
            ),
        ]
    )

    assert score == 82


def test_quality_bands() -> None:
    assert quality_band(100) == "Excellent"
    assert quality_band(90) == "Good"
    assert quality_band(75) == "Review"
    assert quality_band(55) == "Poor"
    assert quality_band(20) == "Critical"


def test_summarize_scores_returns_average_and_band() -> None:
    average, band = summarize_scores([100, 90, 80])

    assert average == 90
    assert band == "Good"
