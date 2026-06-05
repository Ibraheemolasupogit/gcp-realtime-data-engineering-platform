# Streaming Reliability

Milestone 5 implements a local-first stream processing pipeline that integrates the existing JSONL sample events, local Pub/Sub-style publisher, in-memory queue, consumer, validation layer, transformations, clean-event output, and dead-letter routing.

No GCP resources are provisioned in this milestone.

## Local Stream Processing Flow

The local pipeline follows this flow:

1. Load JSONL sample events from `data/sample/*.jsonl`.
2. Publish events into `InMemoryEventQueue` through `LocalEventPublisher`.
3. Consume queued messages through `LocalEventConsumer`.
4. Validate each event with the Milestone 4 schema validator and duplicate detector.
5. Transform valid events into a clean canonical JSONL format.
6. Route clean events to `outputs/clean_events.jsonl`.
7. Route rejected events to `outputs/dead_letter_events.jsonl`.
8. Write run metrics to `outputs/stream_processing_summary.json`.

## Clean-Event Routing

Valid events are transformed into a canonical clean-event record. The processor preserves business fields and adds `processing_metadata`:

- `processed_at`
- `processing_status`
- `quality_score`
- `idempotency_key`
- `source_file`
- `lateness_seconds`

This local clean output maps conceptually to records that could later be written to BigQuery clean-event tables.

## Dead-Letter Routing

Invalid events are routed to `outputs/dead_letter_events.jsonl` with structured metadata:

- `original_event`
- `event_id`
- `rejection_reason`
- `validation_errors`
- `quality_score`
- `source_file`
- `failed_at`
- `recommended_action`

Recommended rejection reasons include missing required fields, invalid timestamps, unknown event types, duplicate event IDs, late events, invalid transaction amounts, malformed identifiers, malformed records, and processing errors.

Future milestones can use this structure as the local equivalent of Pub/Sub dead-letter topics or Dataflow side outputs.

## Duplicate Handling

Duplicate detection uses the Milestone 4 `DuplicateDetector` during one processing run. The first event ID is accepted if otherwise valid; later occurrences of the same `event_id` are routed to the dead-letter output with `duplicate_event_id`.

## Late-Event Handling

Late events are detected by comparing `ingestion_timestamp` to `event_timestamp`. If the difference exceeds the configured threshold, the event is routed to dead letter with the `late_event` reason.

This is intentionally conservative for Milestone 5. Apache Beam watermarking, allowed lateness windows, and late-pane outputs are not implemented yet. Conceptually, this local rule maps to a future Dataflow watermark and side-output strategy.

## Idempotency Strategy

The processor generates a deterministic SHA-256 idempotency key from:

- `event_id`
- `event_type`
- `event_timestamp`
- `customer_id`
- `session_id`

The same event context produces the same key across repeated processing runs. This supports future idempotent writes to analytical storage.

## GCP Conceptual Mapping

| Local component | Future GCP-aligned concept |
| --- | --- |
| `LocalEventPublisher` | Pub/Sub publisher |
| `InMemoryEventQueue` | Pub/Sub topic boundary |
| `LocalEventConsumer` | Pub/Sub subscription consumer |
| `LocalStreamProcessor` | Dataflow / Apache Beam pipeline |
| `outputs/clean_events.jsonl` | BigQuery clean-event table write |
| `outputs/dead_letter_events.jsonl` | Pub/Sub dead-letter topic or Dataflow side output |
| `outputs/stream_processing_summary.json` | Operational pipeline metrics |

This remains a local-first design exercise and does not create Pub/Sub topics, Dataflow jobs, BigQuery datasets, service accounts, or cloud monitoring resources.
