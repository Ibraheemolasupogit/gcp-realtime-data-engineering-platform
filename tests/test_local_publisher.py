import json
from pathlib import Path

from realtime_data_platform.publisher import InMemoryEventQueue, LocalEventPublisher


def write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record))
            file.write("\n")


def test_publisher_reads_jsonl_and_pushes_to_queue(tmp_path: Path) -> None:
    input_file = tmp_path / "events.jsonl"
    records = [
        {"event_id": "event-1", "event_type": "customer_logged_in"},
        {"event_id": "event-2", "event_type": "customer_profile_updated"},
    ]
    write_jsonl(input_file, records)

    queue = InMemoryEventQueue()
    publisher = LocalEventPublisher(queue)

    messages = publisher.publish_jsonl_file(input_file)

    assert len(messages) == 2
    assert queue.size() == 2
    assert messages[0].event == records[0]
    assert messages[0].source_file == str(input_file.resolve())
    assert messages[0].sequence_number == 1


def test_publisher_skips_same_file_without_replay(tmp_path: Path) -> None:
    input_file = tmp_path / "events.jsonl"
    write_jsonl(input_file, [{"event_id": "event-1"}])

    queue = InMemoryEventQueue()
    publisher = LocalEventPublisher(queue)

    first_publish = publisher.publish_jsonl_file(input_file)
    second_publish = publisher.publish_jsonl_file(input_file)

    assert len(first_publish) == 1
    assert second_publish == []
    assert queue.size() == 1


def test_publisher_event_rate_uses_injected_sleep(tmp_path: Path) -> None:
    input_file = tmp_path / "events.jsonl"
    write_jsonl(input_file, [{"event_id": "event-1"}, {"event_id": "event-2"}])
    sleep_calls = []

    queue = InMemoryEventQueue()
    publisher = LocalEventPublisher(
        queue,
        event_rate_per_second=4,
        sleep_fn=sleep_calls.append,
    )

    publisher.publish_jsonl_file(input_file)

    assert sleep_calls == [0.25, 0.25]
