from realtime_data_platform.consumer import LocalEventConsumer
from realtime_data_platform.publisher import InMemoryEventQueue


def test_queue_consumes_messages_in_fifo_order() -> None:
    queue = InMemoryEventQueue()
    queue.publish({"event_id": "first"})
    queue.publish({"event_id": "second"})

    first = queue.consume()
    second = queue.consume()

    assert first is not None
    assert second is not None
    assert first.event["event_id"] == "first"
    assert second.event["event_id"] == "second"
    assert queue.consume() is None


def test_consumer_drains_batch_and_tracks_count() -> None:
    queue = InMemoryEventQueue()
    queue.publish({"event_id": "event-1"})
    queue.publish({"event_id": "event-2"})
    consumer = LocalEventConsumer(queue)

    messages = consumer.consume_batch(max_messages=1)

    assert len(messages) == 1
    assert messages[0].event["event_id"] == "event-1"
    assert consumer.consumed_count == 1
    assert queue.size() == 1

    remaining = consumer.consume_all()

    assert len(remaining) == 1
    assert remaining[0].event["event_id"] == "event-2"
    assert consumer.consumed_count == 2
    assert queue.size() == 0


def test_consumer_invokes_handler() -> None:
    queue = InMemoryEventQueue()
    queue.publish({"event_id": "event-1"})
    handled_event_ids = []
    consumer = LocalEventConsumer(
        queue,
        handler=lambda message: handled_event_ids.append(message.event["event_id"]),
    )

    consumer.consume_one()

    assert handled_event_ids == ["event-1"]
