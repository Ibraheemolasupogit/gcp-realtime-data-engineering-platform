# Limitations

This repository is intentionally local-first and GCP-aligned. It does not claim to be a live deployed platform.

## Current Limitations

- Local-first simulation only.
- Synthetic data only.
- No live GCP resources are provisioned.
- No real Pub/Sub, Dataflow, BigQuery, Cloud Storage, Cloud Logging, Cloud Monitoring, Secret Manager, Dataplex, Data Catalog, or Looker Studio calls are made.
- No GCP credentials, service account keys, or secrets are required.
- Apache Beam / Dataflow code is a reference skeleton and is not executed as a Dataflow job.
- BigQuery SQL is design/portfolio SQL and is not executed against BigQuery.
- Monitoring uses local output files, not Cloud Monitoring.
- Dashboard is local and optional.
- No benchmarking or production SLO claims are included.

## Why These Limits Are Intentional

The repository prioritizes reproducibility, safety, and reviewability. A reviewer can run the entire workflow locally without cloud cost, credentials, or project setup.
