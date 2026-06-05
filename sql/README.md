# BigQuery SQL Layer

This directory contains BigQuery Standard SQL design artifacts for the local-first real-time retail analytics platform.

These files are not executed by the repository, do not connect to BigQuery, and do not provision cloud resources. They show how local JSONL and CSV outputs can map to warehouse-ready tables and transformation queries.

## Tables And Queries

| File | BigQuery-style object |
| --- | --- |
| `bigquery_raw_events_schema.sql` | `realtime_analytics.raw_events` |
| `bigquery_clean_events_schema.sql` | `realtime_analytics.clean_events` |
| `bigquery_dead_letter_events_schema.sql` | `realtime_analytics.dead_letter_events` |
| `bigquery_hourly_metrics.sql` | `realtime_analytics.hourly_event_metrics` |
| `bigquery_customer_activity.sql` | `realtime_analytics.customer_activity_summary` |
| `bigquery_product_activity.sql` | `realtime_analytics.product_activity_summary` |
| `bigquery_transaction_summary.sql` | `realtime_analytics.transaction_value_summary` |
| `bigquery_funnel_metrics.sql` | `realtime_analytics.funnel_metrics` |

## Local Mapping

- `data/sample/*.jsonl` maps conceptually to `raw_events`.
- `outputs/clean_events.jsonl` maps conceptually to `clean_events`.
- `outputs/dead_letter_events.jsonl` maps conceptually to `dead_letter_events`.
- `outputs/*.csv` analytics files map conceptually to dashboard-ready aggregate tables.

Use these SQL files as portfolio-quality warehouse design references, not as deployment scripts.
