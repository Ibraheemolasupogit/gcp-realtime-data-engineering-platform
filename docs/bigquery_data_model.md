# BigQuery Data Model

Milestone 7 defines a BigQuery-style analytical warehouse layer for the local-first real-time retail event analytics platform. It maps the repository's local JSONL and CSV outputs into warehouse-ready table schemas and transformation SQL without connecting to BigQuery or provisioning any GCP resources.

## Purpose

The warehouse layer shows how the platform's local processing outputs could be represented downstream of Pub/Sub and Dataflow in a real GCP deployment. It provides:

- Raw event landing schema.
- Clean validated event schema.
- Dead-letter event schema for rejected records.
- Dashboard-ready analytical tables for hourly activity, customers, products, transactions, and funnel performance.
- BigQuery Standard SQL transformation queries that mirror the Milestone 6 local aggregations.

## Table Model

| Table | Source | Purpose |
| --- | --- | --- |
| `realtime_analytics.raw_events` | `data/sample/*.jsonl` or future Pub/Sub/Dataflow landing output | Stores original event envelope and full raw payload. |
| `realtime_analytics.clean_events` | `outputs/clean_events.jsonl` | Stores validated, transformed, idempotent events ready for analytics. |
| `realtime_analytics.dead_letter_events` | `outputs/dead_letter_events.jsonl` | Stores rejected events and remediation metadata. |
| `realtime_analytics.hourly_event_metrics` | `clean_events` | Supports time-series event volume and engagement dashboards. |
| `realtime_analytics.customer_activity_summary` | `clean_events` | Supports customer behavior and lifecycle analysis. |
| `realtime_analytics.product_activity_summary` | `clean_events` | Supports product interaction and merchandising analysis. |
| `realtime_analytics.transaction_value_summary` | `clean_events` | Supports purchase, refund, failed payment, and net value reporting. |
| `realtime_analytics.funnel_metrics` | `clean_events` | Supports checkout funnel conversion and abandonment reporting. |

## Schema Design Decisions

`raw_events` keeps both parsed envelope fields and `raw_payload` as JSON. This preserves replay and audit flexibility while still allowing common filters on event type, event time, customer, and source file.

`clean_events` flattens the canonical fields produced by the local stream processor. Optional fields such as `product_id`, `transaction_id`, `transaction_amount`, and `currency` remain nullable because not every event category carries them.

`dead_letter_events` stores structured validation errors and the original event as JSON. This keeps invalid data out of clean analytics while preserving enough context for replay or producer remediation.

Aggregate tables intentionally match the Milestone 6 CSV outputs so local artifacts can be reviewed as future BigQuery table shapes.

## Partitioning And Clustering

Recommended partitioning:

- `raw_events`: partition by `DATE(event_timestamp)` for event-time filtering.
- `clean_events`: partition by `DATE(event_timestamp)` for analytics and retention policies.
- `dead_letter_events`: partition by `DATE(failed_at)` for remediation and operations review.
- `hourly_event_metrics`: partition by `DATE(event_hour)` for dashboard time windows.

Recommended clustering:

- `raw_events`: `event_type`, `customer_id`, `source_file`.
- `clean_events`: `event_type`, `customer_id`, `product_id`.
- `dead_letter_events`: `rejection_reason`, `source_file`.
- Customer and product summary tables cluster by their entity identifiers.

These choices are meant to support common filters while keeping the design easy to understand. They are recommendations only and have not been applied to a live BigQuery dataset.

## Local Output Mapping

| Local output | BigQuery-style target |
| --- | --- |
| `data/sample/*.jsonl` | `realtime_analytics.raw_events` |
| `outputs/clean_events.jsonl` | `realtime_analytics.clean_events` |
| `outputs/dead_letter_events.jsonl` | `realtime_analytics.dead_letter_events` |
| `outputs/hourly_event_metrics.csv` | `realtime_analytics.hourly_event_metrics` |
| `outputs/customer_activity_summary.csv` | `realtime_analytics.customer_activity_summary` |
| `outputs/product_activity_summary.csv` | `realtime_analytics.product_activity_summary` |
| `outputs/transaction_value_summary.csv` | `realtime_analytics.transaction_value_summary` |
| `outputs/funnel_metrics.csv` | `realtime_analytics.funnel_metrics` |

## Dashboard Support

The aggregate SQL layer supports Looker Studio-style dashboards for:

- Hourly event volume and unique customer/session activity.
- Customer behavior and checkout abandonment.
- Product views, basket interactions, and wishlist activity.
- Purchase, refund, failed payment, and net transaction value reporting.
- Funnel conversion and abandonment rates.

The SQL files under `sql/` are intentionally readable transformation models, not deployment scripts.

## GCP Deployment Positioning

In a future GCP deployment, this warehouse layer would sit downstream of:

1. Pub/Sub topics receiving retail/customer events.
2. Dataflow / Apache Beam pipelines validating, deduplicating, transforming, and routing events.
3. BigQuery tables receiving raw, clean, dead-letter, and aggregate outputs.
4. Looker Studio dashboards reading analytical tables or views.

Milestone 7 does not create datasets, run queries, provision infrastructure, deploy Dataflow jobs, connect to Pub/Sub, or authenticate with GCP. It is a local SQL and design layer only.
