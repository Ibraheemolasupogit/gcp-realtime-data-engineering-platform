"""Local Pub/Sub-style publisher for JSONL event files."""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from pathlib import Path

from realtime_data_platform.data_generation import read_jsonl
from realtime_data_platform.publisher.queue import InMemoryEventQueue, LocalQueueMessage
from realtime_data_platform.utils.logger import get_logger

logger = get_logger(__name__)


class LocalEventPublisher:
    """Publish JSONL events into a local queue simulation."""

    def __init__(
        self,
        queue: InMemoryEventQueue,
        *,
        event_rate_per_second: float = 0,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self.queue = queue
        self.event_rate_per_second = event_rate_per_second
        self.sleep_fn = sleep_fn
        self._published_sources: set[Path] = set()

    def publish_event(
        self,
        event: dict,
        *,
        source_file: str | None = None,
        attributes: dict | None = None,
    ) -> LocalQueueMessage:
        """Publish a single event to the local queue."""
        message = self.queue.publish(event, source_file=source_file, attributes=attributes)
        logger.info(
            "published event_id=%s sequence_number=%s source_file=%s",
            event.get("event_id"),
            message.sequence_number,
            source_file,
        )
        self._sleep_between_events()
        return message

    def publish_events(
        self,
        events: Iterable[dict],
        *,
        source_file: str | None = None,
        attributes: dict | None = None,
    ) -> list[LocalQueueMessage]:
        """Publish a collection of events to the local queue."""
        return [
            self.publish_event(event, source_file=source_file, attributes=attributes)
            for event in events
        ]

    def publish_jsonl_file(
        self,
        path: str | Path,
        *,
        replay: bool = False,
    ) -> list[LocalQueueMessage]:
        """Publish records from a JSONL file.

        A file is published once per publisher instance unless replay=True is supplied.
        This keeps accidental duplicate publishes visible while supporting explicit
        deterministic replay tests.
        """
        source_path = Path(path).resolve()
        if source_path in self._published_sources and not replay:
            logger.info("skipped already-published source_file=%s", source_path)
            return []

        records = read_jsonl(source_path)
        messages = self.publish_events(
            records,
            source_file=str(source_path),
            attributes={"replay": replay},
        )
        self._published_sources.add(source_path)
        logger.info("published %s records from source_file=%s", len(messages), source_path)
        return messages

    def publish_jsonl_files(
        self,
        paths: Iterable[str | Path],
        *,
        replay: bool = False,
    ) -> list[LocalQueueMessage]:
        """Publish records from multiple JSONL files."""
        messages = []
        for path in paths:
            messages.extend(self.publish_jsonl_file(path, replay=replay))
        return messages

    def _sleep_between_events(self) -> None:
        if self.event_rate_per_second > 0:
            self.sleep_fn(1 / self.event_rate_per_second)
