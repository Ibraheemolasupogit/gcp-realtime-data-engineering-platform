# Production Deployment Roadmap

This roadmap describes future deployment work. It is not implemented by this repository.

## 1. Provision GCP Project And IAM

- Create or select a GCP project.
- Define service accounts for publishers, Dataflow, BigQuery, and operations.
- Apply least-privilege IAM roles.

## 2. Create Pub/Sub Topics And Subscriptions

- Create event ingestion topic.
- Create Dataflow subscription.
- Create dead-letter and replay topics.
- Configure retry and dead-letter policies.

## 3. Configure Cloud Storage Raw Archive

- Create raw archive bucket.
- Add lifecycle and retention policies.
- Define partitioned object layout.

## 4. Deploy Dataflow Pipeline

- Package Beam pipeline.
- Configure staging and temp buckets.
- Deploy with DataflowRunner.
- Configure autoscaling and worker options.

## 5. Create BigQuery Datasets And Tables

- Create `realtime_analytics` dataset.
- Apply table schemas from `sql/`.
- Configure partitioning, clustering, and access controls.

## 6. Configure Dead-Letter Topics And Tables

- Route validation and processing failures.
- Store structured dead-letter metadata.
- Define replay review and approval workflow.

## 7. Configure Cloud Logging And Cloud Monitoring

- Emit structured logs.
- Create metrics for throughput, lag, dead-letter rate, late-event rate, and write failures.
- Add alert policies.

## 8. Connect Looker Studio

- Connect to BigQuery aggregate tables.
- Build event volume, customer, product, transaction, funnel, and monitoring pages.

## 9. Add CI/CD Deployment Pipeline

- Build deployable Beam artifacts.
- Add environment-specific configs.
- Add promotion and rollback process.

## 10. Add Secret Management

- Move sensitive runtime config to Secret Manager.
- Avoid local or committed credentials.

## 11. Add Governance And Catalog Integration

- Register datasets and tables.
- Add field descriptions, lineage, quality policies, and ownership metadata.

## 12. Add Cost Controls

- Configure budgets and alerts.
- Review Pub/Sub retention, Dataflow autoscaling, BigQuery partition pruning, and storage lifecycle policies.

## Current Status

The repository is local-first and GCP-aligned. None of these production deployment steps are active.
