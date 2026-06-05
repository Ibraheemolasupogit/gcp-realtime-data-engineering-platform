"""Local Pub/Sub-style consumer for queued event messages."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from realtime_data_platform.publisher.queue import InMemoryEventQueue, LocalQueueMessage
from realtime_data_platform.utils.logger import get_logger

logger = get_logger(__name__)


class LocalEventConsumer:
    """Consume messages from a local queue simulation."""

    def __init__(
        self,
        queue: InMemoryEventQueue,
        *,
        handler: Callable[[LocalQueueMessage], Any] | None = None,
    ) -> None:
        self.queue = queue
        self.handler = handler
        self.consumed_count = 0

    def consume_one(self) -> LocalQueueMessage | None:
        """Consume one message, optionally passing it to a handler."""
        message = self.queue.consume()
        if message is None:
            logger.info("no messages available on topic=%s", self.queue.topic_name)
            return None

        self.consumed_count += 1
        logger.info(
            "consumed event_id=%s sequence_number=%s",
            message.event.get("event_id"),
            message.sequence_number,
        )
        if self.handler is not None:
            self.handler(message)
        return message

    def consume_batch(self, max_messages: int | None = None) -> list[LocalQueueMessage]:
        """Consume a batch of messages."""
        messages = self.queue.consume_batch(max_messages)
        for message in messages:
            self.consumed_count += 1
            logger.info(
                "consumed event_id=%s sequence_number=%s",
                message.event.get("event_id"),
                message.sequence_number,
            )
            if self.handler is not None:
                self.handler(message)
        return messages

    def consume_all(self) -> list[LocalQueueMessage]:
        """Drain all currently queued messages."""
        return self.consume_batch(max_messages=None)
