# Dataflow Pipeline Design

Milestone 10 adds an Apache Beam / Dataflow reference pipeline skeleton that maps the local-first stream processing design to a production-style GCP architecture. This is a design and local DirectRunner reference only. It does not provision, deploy, or run Dataflow.

## Pipeline Purpose

The future Dataflow pipeline would process retail and customer events in near real time:

1. Read events from Pub/Sub.
2. Parse JSON payloads.
3. Assign event time from `event_timestamp`.
4. Validate schema, identifiers, timestamps, and business rules.
5. Detect duplicates and generate idempotency metadata.
6. Apply fixed windows and allowed lateness.
7. Route clean events to BigQuery.
8. Route invalid, malformed, duplicate, or late events to dead-letter side outputs.
9. Emit structured logs and operational metrics.

## Local-To-GCP Mapping

| Local component | Dataflow/GCP reference |
| --- | --- |
| `data/sample/*.jsonl` | Pub/Sub topic messages |
| `LocalEventPublisher` | Pub/Sub publisher |
| `InMemoryEventQueue` | Pub/Sub topic/subscription boundary |
| `LocalStreamProcessor` | Apache Beam transforms on Dataflow |
| `outputs/clean_events.jsonl` | BigQuery `clean_events` table |
| `outputs/dead_letter_events.jsonl` | Pub/Sub dead-letter topic and BigQuery `dead_letter_events` |
| Monitoring JSON/report | Cloud Logging and Cloud Monitoring |

## Pub/Sub Input Design

Production input would use a Pub/Sub topic such as `retail-events` and a subscription dedicated to the Dataflow job. Messages would carry JSON payloads and ideally include event-time metadata. The repository does not create topics or subscriptions.

Design placeholder:

```python
beam.io.ReadFromPubSub(topic="projects/<project>/topics/retail-events")
```

The placeholder is documented only. No live project ID, credentials, or Pub/Sub connection is required.

## Dataflow Transform Stages

Recommended Beam stages:

1. `ReadFromPubSub`
2. `ParseJson`
3. `AssignEventTimestamps`
4. `WindowIntoFixedWindows`
5. `ValidateEvent`
6. `DetectDuplicates`
7. `TransformCleanEvent`
8. `WriteCleanBigQuery`
9. `WriteDeadLetterSideOutput`
10. `EmitOperationalMetrics`

The local `pipelines/apache_beam_pipeline.py` skeleton demonstrates parser and validation helper functions while keeping Beam optional.

## Windowing And Watermarking

Recommended starting point:

- Fixed windows of 5 minutes.
- Event time based on `event_timestamp`.
- Allowed lateness of 5 minutes.
- Late records beyond allowed lateness routed to a dead-letter or late-event side output.

Dataflow watermarks would estimate event-time completeness from Pub/Sub input. This repository does not implement watermarking; it documents the intended production behavior.

## Duplicate Handling

Duplicate detection should use stable `event_id` and deterministic idempotency keys. In a distributed runner, duplicate state would need a bounded state strategy, external idempotency table, or BigQuery merge/deduplication pattern depending on throughput and retention requirements.

## Dead-Letter Side Output

Invalid records should be emitted as structured dead-letter records containing:

- original payload
- event ID where available
- rejection reason
- validation errors
- quality score
- failed timestamp
- recommended action

Dataflow can model this using tagged side outputs. Downstream sinks may include Pub/Sub dead-letter topics, BigQuery dead-letter tables, and Cloud Logging structured entries.

## BigQuery Sink Strategy

Clean events map to `realtime_analytics.clean_events`. Dead-letter records map to `realtime_analytics.dead_letter_events`. Dashboard aggregates can be produced by SQL models or scheduled transformations downstream.

BigQuery writes should be retry-safe through deterministic idempotency keys, staging tables, merge statements, or deduplicating views. The repository does not execute BigQuery writes.

## Cloud Storage Raw Archive Strategy

A production pipeline may archive raw Pub/Sub payloads to Cloud Storage before or during processing. This supports replay, audit, and incident investigation. The local equivalent is the retained `data/sample/*.jsonl` and `outputs/dead_letter_events.jsonl` artifacts.

## Logging And Monitoring Integration

Production Dataflow should emit:

- parse error counts
- validation failure counts
- duplicate counts
- late-event counts
- dead-letter counts
- BigQuery write failures
- watermark lag
- system backlog and throughput

These map to Cloud Logging structured records and Cloud Monitoring metrics/alerts. The local monitoring layer added in Milestone 8 models those concepts offline.

## Operational Failure Modes

- Pub/Sub backlog grows faster than Dataflow can process.
- Consumer retries cause duplicate delivery.
- Schema changes cause validation failures.
- Event-time skew increases late-event side output volume.
- BigQuery insert or merge failures require retry-safe writes.
- Dead-letter replay is run twice and must remain idempotent.
- A malformed event causes parser failures and must be isolated.

## Deployment Assumptions

A future deployment would require explicit project configuration, service accounts, IAM, Pub/Sub topics/subscriptions, Dataflow templates or jobs, BigQuery datasets/tables, Cloud Storage buckets, and monitoring policies. None of those are included in this milestone.

Milestone 10 is a local-first Beam/Dataflow reference only.
