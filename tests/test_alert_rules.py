from realtime_data_platform.monitoring import (
    alert_counts_by_severity,
    classify_pipeline_status,
    evaluate_alerts,
)


def healthy_metrics() -> dict:
    return {
        "dead_letter_rate": 0.01,
        "duplicate_rate": 0.01,
        "late_event_rate": 0.01,
        "average_quality_score": 99,
        "clean_event_output_exists": True,
        "analytics_outputs_exist": True,
        "processing_errors": 0,
    }


def test_alerts_are_ok_when_metrics_within_thresholds() -> None:
    alerts = evaluate_alerts(healthy_metrics())

    assert {alert["status"] for alert in alerts} == {"ok"}
    assert classify_pipeline_status(alerts, healthy_metrics()) == "healthy"


def test_alerts_trigger_when_thresholds_are_exceeded() -> None:
    metrics = {
        **healthy_metrics(),
        "dead_letter_rate": 0.25,
        "duplicate_rate": 0.12,
        "late_event_rate": 0.2,
        "average_quality_score": 80,
    }

    alerts = evaluate_alerts(metrics)
    triggered = [alert for alert in alerts if alert["status"] == "triggered"]

    assert {alert["alert_name"] for alert in triggered} == {
        "dead_letter_rate_high",
        "duplicate_rate_high",
        "late_event_rate_high",
        "quality_score_low",
    }
    assert alert_counts_by_severity(alerts) == {"critical": 1, "warning": 3, "info": 0}
    assert classify_pipeline_status(alerts, metrics) == "failed"


def test_missing_output_and_processing_errors_classify_failed() -> None:
    metrics = {**healthy_metrics(), "clean_event_output_exists": False, "processing_errors": 1}
    alerts = evaluate_alerts(metrics)

    assert classify_pipeline_status(alerts, metrics) == "failed"
