# Looker Studio Mapping

This document maps local dashboard-ready outputs to future Looker Studio dashboard panels. No live Looker Studio report is created.

## Dashboard Sources

| Local output | Future BigQuery source | Dashboard panel |
| --- | --- | --- |
| `outputs/hourly_event_metrics.csv` | `realtime_analytics.hourly_event_metrics` | Hourly event volume |
| `outputs/customer_activity_summary.csv` | `realtime_analytics.customer_activity_summary` | Customer activity |
| `outputs/product_activity_summary.csv` | `realtime_analytics.product_activity_summary` | Product engagement |
| `outputs/transaction_value_summary.csv` | `realtime_analytics.transaction_value_summary` | Transaction value |
| `outputs/funnel_metrics.csv` | `realtime_analytics.funnel_metrics` | Funnel conversion |
| `outputs/pipeline_monitoring_summary.json` | operational metrics table or Cloud Monitoring export | Pipeline health |

## Intended Dashboard Sections

- Event volume and traffic.
- Customer behavior.
- Product engagement.
- Transaction health.
- Funnel performance.
- Data quality and dead-letter health.
- Operational alerts.

## Limitations

The local Streamlit app and Markdown reports are portfolio reporting surfaces. They do not connect to Looker Studio or BigQuery.
