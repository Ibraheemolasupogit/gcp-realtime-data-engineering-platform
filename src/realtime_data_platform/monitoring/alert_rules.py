"""Local threshold-based alert rules for pipeline monitoring."""

from __future__ import annotations

from collections import Counter
from typing import Any

DEFAULT_THRESHOLDS = {
    "max_dead_letter_rate": 0.20,
    "max_duplicate_rate": 0.10,
    "max_late_event_rate": 0.15,
    "min_average_quality_score": 90,
    "max_processing_errors": 0,
}


def evaluate_alerts(
    metrics: dict[str, Any],
    thresholds: dict[str, float | int] | None = None,
) -> list[dict[str, Any]]:
    """Evaluate local alert rules against collected metrics."""
    active_thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    return [
        rate_alert(
            "dead_letter_rate_high",
            "critical",
            "dead_letter_rate",
            metrics.get("dead_letter_rate", 0),
            active_thresholds["max_dead_letter_rate"],
            "Dead-letter rate is above the configured threshold.",
            "Inspect dead-letter records and validation rules before replay.",
        ),
        rate_alert(
            "duplicate_rate_high",
            "warning",
            "duplicate_rate",
            metrics.get("duplicate_rate", 0),
            active_thresholds["max_duplicate_rate"],
            "Duplicate event rate is above the configured threshold.",
            "Review idempotency keys and replay behavior.",
        ),
        rate_alert(
            "late_event_rate_high",
            "warning",
            "late_event_rate",
            metrics.get("late_event_rate", 0),
            active_thresholds["max_late_event_rate"],
            "Late-event rate is above the configured threshold.",
            "Review event-time lag and future watermark strategy.",
        ),
        minimum_alert(
            "quality_score_low",
            "warning",
            "average_quality_score",
            metrics.get("average_quality_score", 0),
            active_thresholds["min_average_quality_score"],
            "Average data quality score is below the configured threshold.",
            "Inspect validation error counts and upstream event contracts.",
        ),
        boolean_alert(
            "clean_event_output_missing",
            "critical",
            "clean_event_output_exists",
            metrics.get("clean_event_output_exists", False),
            True,
            "Clean event output is missing.",
            "Run the local stream processing pipeline before analytics or monitoring.",
        ),
        boolean_alert(
            "analytics_output_missing",
            "warning",
            "analytics_outputs_exist",
            metrics.get("analytics_outputs_exist", False),
            True,
            "One or more analytics outputs are missing.",
            "Run local analytics generation to refresh dashboard-ready CSVs.",
        ),
        maximum_alert(
            "processing_errors_present",
            "critical",
            "processing_errors",
            metrics.get("processing_errors", 0),
            active_thresholds["max_processing_errors"],
            "Processing errors are present in the latest run.",
            "Inspect processor logs and dead-letter processing_error records.",
        ),
    ]


def classify_pipeline_status(alerts: list[dict[str, Any]], metrics: dict[str, Any]) -> str:
    """Classify pipeline health from alert state and key rates."""
    active_alerts = [alert for alert in alerts if alert["status"] == "triggered"]
    if any(alert["severity"] == "critical" for alert in active_alerts):
        return "failed"
    if metrics.get("dead_letter_rate", 0) > 0.20 or metrics.get("late_event_rate", 0) > 0.15:
        return "degraded"
    if active_alerts:
        return "warning"
    return "healthy"


def alert_counts_by_severity(alerts: list[dict[str, Any]]) -> dict[str, int]:
    """Count triggered alerts by severity."""
    counter = Counter(alert["severity"] for alert in alerts if alert["status"] == "triggered")
    return {
        "critical": counter.get("critical", 0),
        "warning": counter.get("warning", 0),
        "info": counter.get("info", 0),
    }


def rate_alert(
    alert_name: str,
    severity: str,
    metric_name: str,
    observed_value: float,
    threshold: float | int,
    message: str,
    recommended_action: str,
) -> dict[str, Any]:
    """Build an alert that triggers when a rate is above a maximum threshold."""
    return build_alert(
        alert_name,
        severity,
        metric_name,
        observed_value,
        threshold,
        observed_value > threshold,
        message,
        recommended_action,
    )


def maximum_alert(
    alert_name: str,
    severity: str,
    metric_name: str,
    observed_value: float | int,
    threshold: float | int,
    message: str,
    recommended_action: str,
) -> dict[str, Any]:
    """Build an alert that triggers above a maximum threshold."""
    return build_alert(
        alert_name,
        severity,
        metric_name,
        observed_value,
        threshold,
        observed_value > threshold,
        message,
        recommended_action,
    )


def minimum_alert(
    alert_name: str,
    severity: str,
    metric_name: str,
    observed_value: float | int,
    threshold: float | int,
    message: str,
    recommended_action: str,
) -> dict[str, Any]:
    """Build an alert that triggers below a minimum threshold."""
    return build_alert(
        alert_name,
        severity,
        metric_name,
        observed_value,
        threshold,
        observed_value < threshold,
        message,
        recommended_action,
    )


def boolean_alert(
    alert_name: str,
    severity: str,
    metric_name: str,
    observed_value: bool,
    threshold: bool,
    message: str,
    recommended_action: str,
) -> dict[str, Any]:
    """Build an alert that triggers when a boolean does not match expectation."""
    return build_alert(
        alert_name,
        severity,
        metric_name,
        observed_value,
        threshold,
        observed_value is not threshold,
        message,
        recommended_action,
    )


def build_alert(
    alert_name: str,
    severity: str,
    metric_name: str,
    observed_value: Any,
    threshold: Any,
    triggered: bool,
    message: str,
    recommended_action: str,
) -> dict[str, Any]:
    """Build a normalized alert record."""
    return {
        "alert_name": alert_name,
        "severity": severity,
        "status": "triggered" if triggered else "ok",
        "metric_name": metric_name,
        "observed_value": observed_value,
        "threshold": threshold,
        "message": message,
        "recommended_action": recommended_action,
    }
