# Local Dashboard

This folder contains an optional Streamlit dashboard over local generated outputs.

The dashboard is local-first and does not connect to BigQuery, Looker Studio, Pub/Sub, Dataflow, Cloud Storage, Cloud Logging, Cloud Monitoring, or any live GCP service.

## Run Locally

Generate local outputs first:

```bash
python scripts/run_local_stream.py
python scripts/generate_reports.py
python scripts/run_dead_letter_review.py
```

Run the dashboard if Streamlit is installed:

```bash
python -m streamlit run dashboard/streamlit_app.py
```

If Streamlit is not installed, the module can still be imported and tested. Running `python dashboard/streamlit_app.py` prints a compact local dashboard summary.

## Panels

- Total clean events
- Dead-letter events
- Data quality score
- Pipeline status
- Hourly event volume
- Customer activity summary
- Product activity summary
- Transaction value summary
- Funnel metrics
- Dead-letter/replay summary
- Monitoring alerts

## Source Files

The dashboard reads CSV, JSON, and Markdown-ready artifacts from `outputs/` and `reports/`. Missing files are handled gracefully so the dashboard remains useful during local development.
