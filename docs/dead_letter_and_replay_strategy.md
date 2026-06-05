# Dead-Letter and Replay Strategy

Milestone 9 adds local dead-letter inspection, replay candidate classification, retry policy design, and reliability reporting. This remains local-first and design-oriented: no Pub/Sub dead-letter topics, Dataflow jobs, BigQuery writes, Cloud Logging sinks, Cloud Monitoring alerts, credentials, or live GCP resources are used.

## Why Dead-Letter Queues Exist

Dead-letter queues isolate events that cannot be safely processed in the primary path. They protect clean analytical outputs from malformed, duplicate, late, unknown, or otherwise unsafe records while preserving enough context for investigation, repair, and replay.

In this repository, `outputs/dead_letter_events.jsonl` is the local equivalent of a dead-letter topic or side output.

## Local Dead-Letter Workflow

Run the review workflow:

```bash
python scripts/run_dead_letter_review.py
```

The script reads:

```text
outputs/dead_letter_events.jsonl
```

It writes:

```text
outputs/dead_letter_review_summary.json
reports/dead_letter_review_report.md
```

The workflow:

1. Reads local dead-letter records.
2. Counts rejection reasons.
3. Classifies replayable and non-replayable records.
4. Adds retry and reliability metadata.
5. Writes JSON and Markdown review artifacts.

## Replay Candidate Selection

Replayable examples:

- `late_event`: replay through a controlled late-event path if business rules allow.
- `processing_error`: retry after confirming the failure was transient.
- `duplicate_event_id`: conditionally replay only if idempotency state confirms no successful write occurred.

Non-replayable examples:

- `malformed_event_record`
- `missing_required_field`
- `invalid_transaction_amount`
- `unknown_event_type`
- `malformed_identifier`
- `invalid_timestamp`

Non-replayable records require producer fixes, schema updates, enrichment, or data repair before replay.

## Retry Policy Design

The local retry policy is deterministic:

- `max_attempts`: `3`
- `backoff_seconds`: `5`
- `backoff_multiplier`: `2.0`
- Retryable reasons: `late_event`, `processing_error`, `duplicate_event_id`
- Non-retryable reasons: malformed records, missing critical fields, invalid transaction amount, unknown event type, malformed identifiers, and invalid timestamps

Backoff sequence with defaults:

```text
attempt 1 -> 5 seconds
attempt 2 -> 10 seconds
attempt 3 -> 20 seconds
```

The repository does not sleep, schedule, or execute replay jobs; it models the policy for local inspection and tests.

## Idempotency During Replay

Replay candidates include deterministic idempotency keys derived from original event context. This supports retry-safe processing by allowing downstream writes to identify repeated attempts.

The local design assumes at-least-once processing with idempotent writes. It does not claim exactly-once delivery. Exactly-once outcomes are approached through stable event IDs, deterministic idempotency keys, duplicate detection, and write-side safeguards.

## At-Least-Once Versus Exactly-Once

Pub/Sub-style systems commonly provide at-least-once delivery. A publisher may retry after a crash, a consumer may fail mid-batch, or a replay job may be run twice. The platform should assume duplicates are possible.

Exactly-once business outcomes require idempotent processing and storage semantics. In a future BigQuery deployment, this could mean deterministic merge keys, staging tables, or deduplicating views keyed by `idempotency_key`.

## Failure Scenarios

| Scenario | Local handling | Recommended action |
| --- | --- | --- |
| Malformed event enters pipeline | Routed to dead letter | Repair event shape before replay. |
| Duplicate event is published | Routed to dead letter when duplicate ID is observed | Check idempotency state before replay. |
| Event arrives after lateness threshold | Routed to dead letter as `late_event` | Replay through a late-event side path if allowed. |
| BigQuery write fails temporarily | Modelled as `processing_error` | Retry with backoff after transient failure clears. |
| Schema changes unexpectedly | Routed as `unknown_event_type` or schema error | Update schema mapping intentionally. |
| Publisher republishes after crash | Duplicate detection and idempotency key protect clean output | Suppress already-written events. |
| Consumer fails mid-batch | Retry may reprocess earlier events | Use idempotency keys and checkpointing. |
| Replay job runs twice | Duplicate replay candidates can recur | Ensure replay writes are idempotent. |

## GCP Reliability Mapping

| Local concept | GCP-aligned concept |
| --- | --- |
| `outputs/dead_letter_events.jsonl` | Pub/Sub dead-letter topic or Dataflow side output |
| Replay candidate selector | Replay job or controlled subscriber |
| Retry policy | Pub/Sub retry policy, Dataflow retry behavior, or orchestration policy |
| Idempotency key | BigQuery merge key or deduplication key |
| Dead-letter report | Operational runbook or incident review |
| Monitoring alerts | Cloud Monitoring alert policies |
| Structured rejection metadata | Cloud Logging structured error records |

## Limitations

- Replay is simulated and classified locally only.
- No event repair workflow is implemented.
- No live Pub/Sub topics, Dataflow jobs, BigQuery tables, Cloud Logging sinks, or Cloud Monitoring policies are created.
- No exactly-once guarantee is claimed.
- Watermarking and side outputs remain conceptual until a future Dataflow milestone.
