import json
from pathlib import Path

from realtime_data_platform.consumer import LocalEventConsumer
from realtime_data_platform.publisher import InMemoryEventQueue, LocalEventPublisher


def test_replay_publishes_same_input_file_again_deterministically(tmp_path: Path) -> None:
    input_file = tmp_path / "events.jsonl"
    records = [{"event_id": "event-1"}, {"event_id": "event-2"}]
    with input_file.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record))
            file.write("\n")

    queue = InMemoryEventQueue()
    publisher = LocalEventPublisher(queue)
    consumer = LocalEventConsumer(queue)

    initial_messages = publisher.publish_jsonl_file(input_file)
    replayed_messages = publisher.publish_jsonl_file(input_file, replay=True)
    consumed_messages = consumer.consume_all()

    assert len(initial_messages) == 2
    assert len(replayed_messages) == 2
    assert [message.event for message in consumed_messages] == records + records
    assert [message.attributes["replay"] for message in consumed_messages] == [
        False,
        False,
        True,
        True,
    ]
