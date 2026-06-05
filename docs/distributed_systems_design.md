# Distributed Systems Design

Milestone 10 documents the distributed systems choices behind the GCP-aligned real-time event platform. The implementation remains local-first; this document explains how the design would behave in a production Pub/Sub + Dataflow + BigQuery architecture.

## Ordering Considerations

Retail events may arrive out of order because customers use multiple devices, networks retry requests, and publishers can batch or retry. The platform should not rely on global ordering. Event-time processing uses `event_timestamp`, while operational monitoring also tracks `ingestion_timestamp`.

Per-key ordering can be considered for specific use cases such as customer session reconstruction, but broad analytics should tolerate out-of-order delivery.

## At-Least-Once Delivery

Pub/Sub-style systems commonly deliver messages at least once. Duplicates can happen when publishers retry after crashes, subscriptions redeliver unacknowledged messages, or replay jobs are run manually.

The design assumes duplicates are possible and manages them through validation, duplicate detection, and idempotency keys.

## Idempotency

The local platform generates deterministic idempotency keys from stable event context. In a production BigQuery design, these keys can support merge operations, staging tables, deduplicating views, or write-side suppression.

The project does not claim exactly-once delivery. It aims for exactly-once business outcomes through idempotent processing patterns.

## Replay Safety

Dead-letter replay must be controlled. Late events and transient processing errors may be replayable. Schema failures, malformed identifiers, invalid amounts, and unknown event types require repair before replay.

Replay jobs should be safe to run repeatedly only when downstream writes are idempotent.

## Backpressure Considerations

In production, Pub/Sub backlog and Dataflow autoscaling would indicate pressure. Slow BigQuery writes, schema errors, or high dead-letter rates can increase backlog. Monitoring should track throughput, backlog, watermark lag, and error rates.

The local project models these with output summaries and monitoring reports.

## Late And Duplicate Event Handling

The local pipeline routes events beyond the configured lateness threshold to dead letter. A future Dataflow implementation could use event-time timers, watermarks, allowed lateness, and side outputs for late data.

Duplicate handling uses `event_id` and idempotency metadata. In Dataflow, duplicate state must be bounded or externalized depending on retention and throughput requirements.

## Schema Evolution

Event schemas should evolve intentionally with versioning. Unknown event types and missing critical fields are isolated from clean outputs. In a real deployment, schema changes should include compatibility checks, rollout plans, and alerting.

## Failure Recovery

Failure scenarios include malformed records, transient BigQuery write failures, subscription redelivery, consumer crashes mid-batch, and accidental replay duplication. Recovery should combine dead-letter isolation, retry policies, idempotency, and operator-visible monitoring.

## Why Pub/Sub + Dataflow + BigQuery

Pub/Sub decouples producers from processors and absorbs bursty event traffic. Dataflow provides scalable streaming transforms, event-time windowing, side outputs, and operational integration. BigQuery provides analytical storage and SQL modelling for dashboard-ready outputs.

This combination fits real-time retail analytics where ingestion, validation, reliability, and analytical modelling must remain separately understandable and operable.
