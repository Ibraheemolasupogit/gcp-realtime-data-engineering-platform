# Pipeline Monitoring Report

## Executive Summary

Local pipeline status is **failed**.
Monitoring was generated at `2026-06-05T09:10:28.722334Z` from local output
artifacts only.

## Pipeline Status

- Status: `failed`
- Total events processed: `64`
- Clean events written: `48`
- Dead-letter events written: `16`
- Processing errors: `0`

## Key Operational Metrics

| Metric | Value |
| --- | ---: |
| Error rate | 0.0 |
| Dead-letter rate | 0.25 |
| Duplicate rate | 0.0625 |
| Late-event rate | 0.125 |
| Average quality score | 98.22 |
| Quality band | Excellent |

## Alert Summary

- **CRITICAL** `dead_letter_rate_high`: Dead-letter rate is above the configured threshold. Observed `0.25` against threshold `0.2`.

Alert counts by severity:

- Critical: `1`
- Warning: `0`
- Info: `0`

## Data Quality Summary

- Valid events: `48`
- Invalid events: `16`
- Average quality score: `98.22`
- Quality band: `Excellent`

## Dead-Letter Summary

- Dead-letter events: `16`
- Dead-letter rate: `0.25`
- Dead-letter output exists: `True`

## Late-Event And Duplicate Summary

- Late events: `8`
- Late-event rate: `0.125`
- Duplicate events: `4`
- Duplicate rate: `0.0625`

## Recommended Actions

- Inspect dead-letter records and validation rules before replay.

## GCP Monitoring Mapping

This local report maps conceptually to Cloud Logging and Cloud Monitoring.
JSON summaries are analogous to structured log entries, metric fields map to custom
monitoring metrics, and alert records map to alert policies.
In a real GCP deployment, Dataflow jobs could emit counters and structured logs,
Pub/Sub dead-letter topics could feed error metrics, and Cloud Monitoring alert
policies could notify operators.

No live GCP monitoring resources, log sinks, alert policies, dashboards, Pub/Sub
topics, Dataflow jobs, or credentials are provisioned by this milestone.
