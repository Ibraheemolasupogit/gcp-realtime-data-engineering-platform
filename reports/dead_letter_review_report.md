# Dead-Letter Review Report

## Executive Summary

Reviewed `16` local dead-letter events at
`2026-06-05T09:34:12.101928Z`.
Replayable events: `8`.
Non-replayable events: `8`.

## Dead-Letter Reason Breakdown

- `duplicate_event_id`: `4`
- `invalid_timestamp`: `1`
- `invalid_transaction_amount`: `1`
- `late_event`: `4`
- `malformed_identifier`: `2`
- `missing_required_field`: `2`
- `unknown_event_type`: `2`

## Replayable Versus Non-Replayable Summary

- Replayable events: `8`
- Non-replayable events: `8`

Replay candidates:

- `68daaa6a-1db3-50e1-a7f4-43d0f2589e6c`: `duplicate_event_id` (conditionally_replayable_with_idempotency_check)
- `f7160cb1-f22e-52bc-971e-15e66ddf8720`: `late_event` (retryable_transient_or_late_event)
- `9ba0c416-454d-5919-8515-3e8f16f9e2ba`: `duplicate_event_id` (conditionally_replayable_with_idempotency_check)
- `3c1a3c2f-cf07-563d-8bf3-cd833806ea30`: `late_event` (retryable_transient_or_late_event)
- `240552e9-783e-5d8a-8502-1808de834994`: `duplicate_event_id` (conditionally_replayable_with_idempotency_check)
- `087fe944-139a-5ef8-928c-39354be4ab49`: `late_event` (retryable_transient_or_late_event)
- `266465b1-ec2f-506f-b22e-8d0d03782302`: `duplicate_event_id` (conditionally_replayable_with_idempotency_check)
- `88981c07-a733-50bb-b152-7a1105fe8037`: `late_event` (retryable_transient_or_late_event)

## Recommended Actions

- `duplicate_event_id`: Replay only if idempotency state confirms the event was not already written.
- `invalid_timestamp`: Correct timestamp format before replay.
- `invalid_transaction_amount`: Correct business-rule violations before replay.
- `late_event`: Replay through a controlled late-event path if business rules allow.
- `malformed_identifier`: Correct customer, product, or session identifiers before replay.
- `missing_required_field`: Repair or enrich missing critical fields before replay.
- `unknown_event_type`: Update schema mapping intentionally before replay.

## Retry Policy Summary

- Max attempts: `3`
- Base backoff seconds: `5`
- Backoff multiplier: `2.0`
- Retryable reasons: `duplicate_event_id, late_event, processing_error`
- Non-retryable reasons: `invalid_timestamp, invalid_transaction_amount, malformed_event_record, malformed_identifier, missing_required_field, unknown_event_type`

## Idempotency Safeguards

Replay candidates include deterministic idempotency keys derived from original event context.
Duplicate events are only conditionally replayable and require an idempotency-state
check before reprocessing.
Replay jobs should be safe to run more than once only when writes are idempotent.

## GCP Reliability Mapping

This local workflow maps conceptually to Pub/Sub dead-letter topics, Dataflow side outputs,
BigQuery retry-safe writes, Cloud Logging error records, and Cloud Monitoring alerts.
No live GCP reliability resources are provisioned.

## Limitations

- Replay is simulated locally and does not republish to Pub/Sub.
- Data repair and enrichment are not implemented yet.
- Exactly-once semantics are not claimed; the design favors at-least-once
  processing with idempotent writes.
- Dataflow watermarking and BigQuery write retries are described as future deployment concerns only.
