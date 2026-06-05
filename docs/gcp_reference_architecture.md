# GCP Reference Architecture

This project is GCP-aligned and local-first. Milestone 10 documents how the local event pipeline maps conceptually to a production GCP architecture without provisioning resources or requiring credentials.

## Reference Flow

1. Retail and customer event producers publish event payloads.
2. Pub/Sub receives events on a topic and exposes them through a subscription.
3. Dataflow runs an Apache Beam streaming pipeline.
4. Dataflow validates, deduplicates, windows, transforms, and routes events.
5. Clean events land in BigQuery analytical tables.
6. Invalid or late records flow to dead-letter topics/tables.
7. Cloud Storage archives raw payloads for replay and audit.
8. Looker Studio reads dashboard-ready BigQuery tables.
9. Cloud Logging and Cloud Monitoring capture metrics, logs, and alert signals.

## GCP Service Mapping

| Platform concern | GCP-aligned service |
| --- | --- |
| Event ingestion | Pub/Sub topic |
| Event consumption | Pub/Sub subscription |
| Stream processing | Dataflow running Apache Beam |
| Raw event archive | Cloud Storage |
| Analytical warehouse | BigQuery |
| Dashboard layer | Looker Studio |
| Logs and metrics | Cloud Logging and Cloud Monitoring |
| Secrets in real deployment | Secret Manager |
| Governance | Dataplex / Data Catalog |

## Pub/Sub Ingestion

Pub/Sub provides decoupling between event producers and stream processors. A production deployment would use topic and subscription IAM, retry policies, dead-letter topics, and message attributes for event-time or schema metadata.

This repository does not create topics, subscriptions, or publishers connected to GCP.

## Dataflow Stream Processing

Dataflow would host the Apache Beam pipeline described in `pipelines/apache_beam_pipeline.py` and `pipelines/dataflow_pipeline_design.md`. The intended stages are parse, validate, deduplicate, assign event time, window, transform, route clean outputs, and route dead-letter side outputs.

This repository does not launch Dataflow jobs.

## Cloud Storage Raw Archive

A production architecture may archive raw Pub/Sub payloads to Cloud Storage for audit, replay, and incident recovery. Locally, `data/sample/*.jsonl` and output artifacts play that role.

This repository does not create buckets or write to Cloud Storage.

## BigQuery Analytical Warehouse

The SQL layer under `sql/` defines BigQuery-style schemas and transformations for raw, clean, dead-letter, and aggregate tables. The local CSV outputs from Milestone 6 map to future BigQuery dashboard tables.

This repository does not connect to BigQuery or run SQL against GCP.

## Looker Studio Dashboard Layer

Looker Studio could read BigQuery aggregate tables for event volume, customer activity, product activity, transaction value, and funnel metrics. Dashboard UI is intentionally out of scope at this milestone.

## Cloud Logging And Cloud Monitoring

Structured validation errors, dead-letter counts, late-event counts, and processing summaries would map to Cloud Logging records and Cloud Monitoring metrics. The local monitoring outputs from Milestone 8 model those concepts offline.

## Secret Manager And Governance

In a real deployment, service account credentials or sensitive runtime configuration should be managed through Secret Manager and IAM rather than committed files. Dataset and schema governance could be documented through Dataplex or Data Catalog.

This repository does not include secrets, service account keys, or live governance setup.

## Local-First Limitation

All GCP references in this repository are architecture/design alignment only. No live Pub/Sub, Dataflow, BigQuery, Cloud Storage, Cloud Logging, Cloud Monitoring, Secret Manager, Dataplex, or Data Catalog resources are provisioned.
