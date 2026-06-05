import pytest

from realtime_data_platform.processing import RetryPolicy


def test_retry_policy_classifies_retryable_reasons() -> None:
    policy = RetryPolicy()

    assert policy.is_retryable("late_event") is True
    assert policy.is_retryable("processing_error") is True
    assert policy.is_retryable("invalid_transaction_amount") is False


def test_retry_policy_backoff_is_deterministic() -> None:
    policy = RetryPolicy(max_attempts=3, backoff_seconds=5, backoff_multiplier=2)

    assert policy.next_delay_seconds(1) == 5
    assert policy.next_delay_seconds(2) == 10
    assert policy.next_delay_seconds(3) == 20
    assert policy.should_retry("late_event", 1) is True
    assert policy.should_retry("late_event", 3) is False


def test_retry_policy_rejects_invalid_attempt_number() -> None:
    with pytest.raises(ValueError, match="attempt_number"):
        RetryPolicy().next_delay_seconds(0)
