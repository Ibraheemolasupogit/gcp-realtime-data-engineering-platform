# Pub/Sub Topic And Subscription Design

This document describes the production Pub/Sub design that the local publisher, consumer, and queue simulate. It is a design artifact only and does not create Pub/Sub resources.

## Topics

Recommended production topics:

- `retail-events`: primary customer, product, transaction, and session event stream.
- `retail-events-dead-letter`: invalid, malformed, duplicate, late, or failed events.
- `retail-events-replay`: controlled replay input for repaired or approved events.

## Subscriptions

Recommended subscriptions:

- `dataflow-retail-events`: consumed by the Dataflow streaming pipeline.
- `dead-letter-review`: consumed by operational review or replay tooling.
- `replay-validation`: consumed by replay validation workflows.

## Message Design

Messages should contain JSON payloads matching the event schema, with attributes for schema version, event source, event category, and event time where useful.

## Local Mapping

| Local component | Pub/Sub mapping |
| --- | --- |
| `LocalEventPublisher` | Publisher client |
| `InMemoryEventQueue` | Topic/subscription boundary |
| `LocalEventConsumer` | Subscriber client |
| `outputs/dead_letter_events.jsonl` | Dead-letter topic payloads |

## Reliability Notes

Pub/Sub delivery should be treated as at least once. Duplicate delivery is expected and handled through `event_id`, idempotency keys, and downstream deduplication.

No live Pub/Sub topics or subscriptions are created by this repository.
