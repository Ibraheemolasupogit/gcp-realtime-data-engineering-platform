# Data Quality Rules

Milestone 4 implements local-first event schema validation and data quality scoring for the synthetic retail event files. These checks are intentionally Python-local and do not provision GCP resources.

## Validation Rules

The validator checks each JSON event record for:

- Required shared fields: `event_id`, `event_type`, `event_timestamp`, `ingestion_timestamp`, `event_source`, `customer_id`, `session_id`, and `event_version`.
- Expected data types for required shared fields.
- ISO-8601 timestamp parsing for `event_timestamp` and `ingestion_timestamp`.
- Late-event detection when ingestion time is more than the configured allowed lateness after event time.
- Event type allow-list checks across customer, product, transaction, and session events.
- `customer_id` format: `cust_00000`.
- `session_id` format: `sess_00000`.
- `product_id` format for product and transaction records when present: `prod_00000`.
- Non-negative `transaction_amount` for transaction records.
- Duplicate `event_id` detection within one validation run.
- Malformed event record detection for non-object JSON records passed to the validator.

## Event Types

Customer event types:

- `customer_registered`
- `customer_logged_in`
- `customer_profile_updated`
- `customer_marketing_opt_in`
- `customer_marketing_opt_out`

Product event types:

- `product_viewed`
- `product_added_to_basket`
- `product_removed_from_basket`
- `product_wishlisted`

Transaction event types:

- `purchase_completed`
- `payment_failed`
- `refund_requested`
- `refund_completed`

Session event types:

- `session_started`
- `session_ended`
- `checkout_started`
- `checkout_abandoned`

## Scoring Logic

Each event starts with a quality score of `100`. Penalties are applied per validation error:

| Rule | Penalty |
| --- | ---: |
| Missing required field | -10 |
| Invalid data type | -8 |
| Invalid timestamp | -8 |
| Duplicate `event_id` | -5 |
| Late event | -3 |
| Unknown `event_type` | -8 |
| Invalid transaction amount | -10 |
| Malformed customer, product, or session ID | -8 |
| Malformed event record | -10 |

Scores are floored at `0`.

## Quality Bands

| Score range | Band |
| --- | --- |
| 95-100 | Excellent |
| 85-94 | Good |
| 70-84 | Review |
| 50-69 | Poor |
| 0-49 | Critical |

The summary-level score is the average event-level score across the validation run.

## Local Quality Summary

Run validation locally:

```bash
python scripts/run_quality_checks.py
```

The command validates the sample JSONL files under `data/sample/` and writes:

```text
outputs/event_quality_summary.json
```

The summary includes total events checked, valid and invalid counts, duplicate and malformed counts, average quality score, quality band, error counts by rule, invalid examples, and generation timestamp.

## Future Dead-Letter Routing

Validation errors are represented as structured records with `rule`, `field`, `message`, `severity`, and `value`. Future milestones can use these structures to route invalid events to a local dead-letter queue and later map the same concept to Pub/Sub dead-letter topics or Dataflow side outputs.

## GCP Conceptual Mapping

This validation layer maps conceptually to checks that could run inside a Dataflow / Apache Beam pipeline before events are written to BigQuery-style analytical tables. The summary output is also aligned with BigQuery data quality reporting patterns, but this milestone remains local-first and does not create Dataflow jobs, BigQuery datasets, Pub/Sub topics, or cloud monitoring resources.
