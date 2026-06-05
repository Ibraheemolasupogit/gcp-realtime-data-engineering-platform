# Local Runbook

This runbook executes the project end to end using local files only. It does not require GCP credentials and does not create cloud resources.

## 1. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

## 2. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

## 3. Run Tests

```bash
python -m pytest
```

Optional linting:

```bash
ruff format --check .
ruff check .
```

## 4. Generate Synthetic Events

```bash
python scripts/generate_demo_events.py
```

Generated files:

- `data/sample/customer_events.jsonl`
- `data/sample/product_events.jsonl`
- `data/sample/transaction_events.jsonl`
- `data/sample/session_events.jsonl`

## 5. Run Local Stream Pipeline

```bash
python scripts/run_local_stream.py
```

Generated files:

- `outputs/clean_events.jsonl`
- `outputs/dead_letter_events.jsonl`
- `outputs/stream_processing_summary.json`

## 6. Run Quality Checks

```bash
python scripts/run_quality_checks.py
```

Generated file:

- `outputs/event_quality_summary.json`

## 7. Generate Analytics And Reporting Outputs

```bash
python scripts/generate_reports.py
```

Generated files include:

- `outputs/hourly_event_metrics.csv`
- `outputs/customer_activity_summary.csv`
- `outputs/product_activity_summary.csv`
- `outputs/transaction_value_summary.csv`
- `outputs/funnel_metrics.csv`
- `outputs/analytics_summary.json`
- `outputs/pipeline_monitoring_summary.json`
- `reports/pipeline_monitoring_report.md`
- `reports/analytics_summary.md`

## 8. Generate Monitoring Outputs Only

```bash
python scripts/generate_reports.py --monitoring-only
```

## 9. Run Dead-Letter Review

```bash
python scripts/run_dead_letter_review.py
```

Generated files:

- `outputs/dead_letter_review_summary.json`
- `reports/dead_letter_review_report.md`

## 10. Optionally Run Dashboard

If Streamlit is installed:

```bash
python -m streamlit run dashboard/streamlit_app.py
```

If Streamlit is not installed:

```bash
python dashboard/streamlit_app.py
```

The fallback prints a compact dashboard summary.

## 11. Review Generated Outputs And Reports

Key review targets:

- `reports/analytics_summary.md`
- `reports/pipeline_monitoring_report.md`
- `reports/dead_letter_review_report.md`
- `outputs/*.csv`
- `sql/*.sql`
- `docs/gcp_reference_architecture.md`
- `pipelines/dataflow_pipeline_design.md`

## Notes

All commands are local. No Pub/Sub, Dataflow, BigQuery, Cloud Storage, Cloud Logging, Cloud Monitoring, Secret Manager, Dataplex, Data Catalog, or Looker Studio resources are provisioned.
