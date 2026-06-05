"""Deterministic retry policy for local replay design."""

from __future__ import annotations

from dataclasses import dataclass, field

DEFAULT_RETRYABLE_REASONS = frozenset(
    {
        "late_event",
        "processing_error",
        "duplicate_event_id",
    }
)
DEFAULT_NON_RETRYABLE_REASONS = frozenset(
    {
        "malformed_event_record",
        "missing_required_field",
        "invalid_transaction_amount",
        "unknown_event_type",
        "malformed_identifier",
        "invalid_timestamp",
    }
)


@dataclass(frozen=True)
class RetryPolicy:
    """Local retry policy used to classify replay and retry decisions."""

    max_attempts: int = 3
    backoff_seconds: int = 5
    backoff_multiplier: float = 2.0
    retryable_reasons: frozenset[str] = field(default_factory=lambda: DEFAULT_RETRYABLE_REASONS)
    non_retryable_reasons: frozenset[str] = field(
        default_factory=lambda: DEFAULT_NON_RETRYABLE_REASONS
    )

    def is_retryable(self, rejection_reason: str) -> bool:
        """Return whether a rejection reason can be retried locally."""
        return rejection_reason in self.retryable_reasons

    def next_delay_seconds(self, attempt_number: int) -> int:
        """Return deterministic exponential backoff delay for an attempt."""
        if attempt_number < 1:
            raise ValueError("attempt_number must be >= 1")
        return int(self.backoff_seconds * (self.backoff_multiplier ** (attempt_number - 1)))

    def should_retry(self, rejection_reason: str, attempt_number: int) -> bool:
        """Return whether another retry should be attempted."""
        return self.is_retryable(rejection_reason) and attempt_number < self.max_attempts

    def as_dict(self) -> dict:
        """Return a JSON-serializable retry policy summary."""
        return {
            "max_attempts": self.max_attempts,
            "backoff_seconds": self.backoff_seconds,
            "backoff_multiplier": self.backoff_multiplier,
            "retryable_reasons": sorted(self.retryable_reasons),
            "non_retryable_reasons": sorted(self.non_retryable_reasons),
        }
