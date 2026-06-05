# Analytics Outputs

Milestone 6 generates local dashboard-ready analytical outputs from `outputs/clean_events.jsonl`. These outputs are CSV and JSON artifacts for local review only. They are not live BigQuery tables, Looker Studio dashboards, or cloud-managed resources.

## Output Files

| File | Purpose |
| --- | --- |
| `outputs/hourly_event_metrics.csv` | Hourly event volume, unique customer, unique session, and category counts. |
| `outputs/customer_activity_summary.csv` | Customer-level activity, sessions, purchases, refunds, basket additions, and checkout abandonments. |
| `outputs/product_activity_summary.csv` | Product-level interaction counts for views, basket actions, wishlist events, purchases, and refunds where product IDs are available. |
| `outputs/transaction_value_summary.csv` | Overall purchase, refund, net transaction value, failed payment, and average purchase metrics. |
| `outputs/funnel_metrics.csv` | Single-row funnel summary for sessions, product views, basket additions, checkouts, purchases, abandonment, and conversion. |
| `outputs/analytics_summary.json` | Run metadata and row counts for generated analytics outputs. |

## Field Definitions

Hourly metrics:

- `event_hour`: UTC hour bucket.
- `total_events`: Total clean events in the hour.
- `unique_customers`: Distinct customers active in the hour.
- `unique_sessions`: Distinct sessions active in the hour.
- `customer_events`, `product_events`, `transaction_events`, `session_events`: Category-level counts.

Customer activity:

- `customer_id`: Stable customer identifier.
- `total_events`: Total clean events for the customer.
- `sessions_count`: Distinct session count.
- `first_event_timestamp`, `last_event_timestamp`: Customer activity bounds.
- `purchases_count`, `refunds_count`, `basket_additions_count`, `checkout_abandonments_count`: Key behavior counts.

Product activity:

- `product_id`: Stable product identifier.
- `product_views`, `basket_additions`, `basket_removals`, `wishlist_events`: Product interaction counts.
- `purchase_events`, `refund_events`: Transaction-linked product counts where product IDs are available.

Transaction value:

- `total_purchase_value`: Sum of `purchase_completed` transaction amounts.
- `total_refund_value`: Sum of refund-requested and refund-completed amounts.
- `net_transaction_value`: Purchase value less refund value.
- `purchase_count`, `refund_count`, `failed_payment_count`: Transaction event counts.
- `average_purchase_value`: Mean purchase amount when purchases exist.

Funnel metrics:

- `sessions_started`, `product_views`, `basket_additions`, `checkout_started`, `purchases_completed`, `checkout_abandoned`: Funnel stage counts.
- `conversion_rate`: Purchases divided by sessions started.
- `abandonment_rate`: Checkout abandonments divided by checkout starts.

## Dashboard Use Cases

These outputs can support a local dashboard or BI prototype for:

- Event throughput and engagement monitoring.
- Customer activity ranking and lifecycle review.
- Product interaction and merchandising analysis.
- Transaction health and refund monitoring.
- Funnel conversion and abandonment review.

## GCP Conceptual Mapping

The local CSV outputs map conceptually to BigQuery analytical tables or views that could later feed Looker Studio dashboards:

| Local CSV | Future BigQuery-style model |
| --- | --- |
| `hourly_event_metrics.csv` | `hourly_event_metrics` aggregate table |
| `customer_activity_summary.csv` | `customer_activity_summary` table |
| `product_activity_summary.csv` | `product_activity_summary` table |
| `transaction_value_summary.csv` | `transaction_value_summary` table |
| `funnel_metrics.csv` | `funnel_metrics` table |

This milestone remains local-first and does not create BigQuery datasets, tables, views, scheduled queries, Looker Studio reports, credentials, or cloud deployment logic.
