# Monitoring Strategy

Milestone 8 adds local operational monitoring and reporting around the pipeline outputs. This milestone is local-only: it does not connect to Cloud Logging, Cloud Monitoring, BigQuery, Pub/Sub, Dataflow, or any live GCP service.

## Local Monitoring Design

The monitoring layer reads existing artifacts:

- `outputs/clean_events.jsonl`
- `outputs/dead_letter_events.jsonl`
- `outputs/event_quality_summary.json`
- `outputs/stream_processing_summary.json`
- `outputs/analytics_summary.json`
- Dashboard-ready CSV outputs under `outputs/`

It generates:

- `outputs/pipeline_monitoring_summary.json`
- `reports/pipeline_monitoring_report.md`

## Operational Metrics

Collected metrics include:

- `total_events_processed`
- `clean_events_written`
- `dead_letter_events_written`
- `valid_events`
- `invalid_events`
- `duplicate_events`
- `late_events`
- `processing_errors`
- `error_rate`
- `dead_letter_rate`
- `duplicate_rate`
- `late_event_rate`
- `average_quality_score`
- `quality_band`
- Output existence flags for clean events, dead-letter events, and analytics files

## Alert Rules

Local threshold-based alerts are evaluated for:

- Dead-letter rate above threshold.
- Duplicate rate above threshold.
- Late-event rate above threshold.
- Average quality score below threshold.
- Missing clean-event output.
- Missing analytics output.
- Processing errors greater than the configured threshold.

Default thresholds are configured in `configs/monitoring_config.yaml`:

| Threshold | Default |
| --- | ---: |
| `max_dead_letter_rate` | `0.20` |
| `max_duplicate_rate` | `0.10` |
| `max_late_event_rate` | `0.15` |
| `min_average_quality_score` | `90` |
| `max_processing_errors` | `0` |

These values are intentionally conservative for a small local dataset. In a real production system, thresholds would be tuned using historical baselines and operational SLOs.

## Pipeline Status Model

The local status classifier uses:

- `healthy`: no triggered alerts.
- `warning`: one or more warning alerts.
- `degraded`: high dead-letter or late-event rates.
- `failed`: missing required outputs or processing errors above threshold.

The implementation prioritizes critical alerts as `failed` because missing outputs or processing errors block downstream reliability.

## GCP Conceptual Mapping

| Local monitoring concept | GCP-aligned concept |
| --- | --- |
| JSON summaries | Structured logs in Cloud Logging |
| Metric fields | Custom Cloud Monitoring metrics |
| Alert records | Cloud Monitoring alert policies |
| Markdown report | Operational runbook or incident summary |
| Dead-letter counts | Pub/Sub dead-letter topic metrics |
| Processing summaries | Dataflow job counters and logs |

## Real GCP Deployment Differences

In a real GCP deployment, Dataflow would emit counters and structured logs, Pub/Sub would expose topic/subscription metrics, BigQuery load or write jobs would emit job metadata, and Cloud Monitoring alert policies would notify operators. This repository does not create those resources yet.

Milestone 8 remains local-first and testable. It demonstrates observability thinking without provisioning log sinks, dashboards, alert policies, service accounts, topics, jobs, or datasets.
