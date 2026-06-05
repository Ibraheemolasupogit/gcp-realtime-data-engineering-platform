"""Local Pub/Sub-style queue abstraction for development and tests."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

EventPayload = dict[str, Any]


@dataclass(frozen=True)
class LocalQueueMessage:
    """Message envelope used by the local queue simulation."""

    event: EventPayload
    sequence_number: int
    published_at: str
    source_file: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)


class InMemoryEventQueue:
    """Small FIFO queue that mirrors a Pub/Sub topic boundary locally."""

    def __init__(self, topic_name: str = "local-retail-events") -> None:
        self.topic_name = topic_name
        self._messages: deque[LocalQueueMessage] = deque()
        self._next_sequence_number = 1

    def publish(
        self,
        event: EventPayload,
        *,
        source_file: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> LocalQueueMessage:
        """Publish one event into the queue."""
        message = LocalQueueMessage(
            event=deepcopy(event),
            sequence_number=self._next_sequence_number,
            published_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            source_file=source_file,
            attributes=attributes or {},
        )
        self._messages.append(message)
        self._next_sequence_number += 1
        return message

    def publish_many(
        self,
        events: Iterable[EventPayload],
        *,
        source_file: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> list[LocalQueueMessage]:
        """Publish multiple events into the queue."""
        return [
            self.publish(event, source_file=source_file, attributes=attributes) for event in events
        ]

    def consume(self) -> LocalQueueMessage | None:
        """Consume a single message from the queue."""
        if not self._messages:
            return None
        return self._messages.popleft()

    def consume_batch(self, max_messages: int | None = None) -> list[LocalQueueMessage]:
        """Consume up to max_messages from the queue."""
        if max_messages is not None and max_messages < 1:
            return []

        messages = []
        while self._messages and (max_messages is None or len(messages) < max_messages):
            messages.append(self._messages.popleft())
        return messages

    def clear(self) -> None:
        """Remove all queued messages."""
        self._messages.clear()

    def size(self) -> int:
        """Return the number of queued messages."""
        return len(self._messages)

    def __len__(self) -> int:
        return self.size()
