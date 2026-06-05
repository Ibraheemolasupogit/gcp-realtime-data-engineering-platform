# Dashboard Design

Milestone 11 adds a local dashboard and reporting layer over the generated analytics, monitoring, data quality, and reliability outputs. This is a local reporting surface only. It does not provision or connect to Looker Studio, BigQuery, Pub/Sub, Dataflow, Cloud Storage, Cloud Logging, Cloud Monitoring, or any GCP service.

## Purpose

The dashboard/reporting layer turns pipeline artifacts into portfolio-ready reporting surfaces. It helps reviewers inspect the platform from an analytics and operations perspective without needing cloud infrastructure.

## Data Sources

The dashboard and Markdown report read:

- `outputs/hourly_event_metrics.csv`
- `outputs/customer_activity_summary.csv`
- `outputs/product_activity_summary.csv`
- `outputs/transaction_value_summary.csv`
- `outputs/funnel_metrics.csv`
- `outputs/analytics_summary.json`
- `outputs/pipeline_monitoring_summary.json`
- `outputs/event_quality_summary.json`
- `outputs/dead_letter_review_summary.json`

## Dashboard Panels

- Total clean events
- Dead-letter events
- Data quality score
- Pipeline status
- Hourly event volume
- Customer activity summary
- Product activity summary
- Transaction value summary
- Funnel metrics
- Dead-letter and replay summary
- Monitoring alerts

## Intended Users

- Data engineering reviewers checking end-to-end local pipeline behavior.
- Cloud engineering reviewers evaluating GCP-aligned architecture.
- Analytics reviewers validating dashboard-ready output shapes.
- Operators or maintainers reviewing quality, dead-letter, and monitoring signals.

## Local Streamlit Usage

Streamlit is optional. If installed, run:

```bash
python -m streamlit run dashboard/streamlit_app.py
```

If Streamlit is not installed, the dashboard module remains import-safe and testable. It can still produce a compact panel summary from local files.

## Looker Studio Mapping

The local dashboard panels map conceptually to Looker Studio charts over BigQuery tables:

| Local dashboard panel | Future Looker Studio source |
| --- | --- |
| Hourly event volume | `realtime_analytics.hourly_event_metrics` |
| Customer activity | `realtime_analytics.customer_activity_summary` |
| Product activity | `realtime_analytics.product_activity_summary` |
| Transaction value | `realtime_analytics.transaction_value_summary` |
| Funnel metrics | `realtime_analytics.funnel_metrics` |
| Monitoring alerts | Cloud Monitoring alert metrics or exported operational tables |

## BigQuery Table Mapping

The dashboard uses local CSV outputs generated from `outputs/clean_events.jsonl`. In a real deployment, those CSVs would be replaced by BigQuery analytical tables or views documented in the SQL layer.

## Limitations

- No live Looker Studio dashboard is created.
- No BigQuery queries are executed.
- No GCP resources or credentials are used.
- Streamlit is optional and not required for CI.
- Visual styling is intentionally lightweight because this milestone focuses on reporting surfaces, not dashboard polish.
