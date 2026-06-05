"""Duplicate event identifier detection."""

from __future__ import annotations


class DuplicateDetector:
    """Track seen event identifiers during a local validation run."""

    def __init__(self) -> None:
        self._seen_event_ids: set[str] = set()

    def is_duplicate(self, event_id: object) -> bool:
        """Return True if the event ID was already observed."""
        if not isinstance(event_id, str) or not event_id:
            return False
        if event_id in self._seen_event_ids:
            return True
        self._seen_event_ids.add(event_id)
        return False

    def reset(self) -> None:
        """Clear all tracked event identifiers."""
        self._seen_event_ids.clear()

    @property
    def seen_count(self) -> int:
        """Return the number of unique event identifiers seen."""
        return len(self._seen_event_ids)
