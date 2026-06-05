-- BigQuery Standard SQL
-- Purpose: Model customer-level activity from `realtime_analytics.clean_events`
-- into `realtime_analytics.customer_activity_summary`.
-- This file is a local design artifact only; it is not executed against BigQuery.

CREATE OR REPLACE TABLE `realtime_analytics.customer_activity_summary`
CLUSTER BY customer_id
AS
SELECT
  customer_id,
  COUNT(*) AS total_events,
  COUNT(DISTINCT session_id) AS sessions_count,
  MIN(event_timestamp) AS first_event_timestamp,
  MAX(event_timestamp) AS last_event_timestamp,
  COUNTIF(event_type = 'purchase_completed') AS purchases_count,
  COUNTIF(event_type IN ('refund_requested', 'refund_completed')) AS refunds_count,
  COUNTIF(event_type = 'product_added_to_basket') AS basket_additions_count,
  COUNTIF(event_type = 'checkout_abandoned') AS checkout_abandonments_count
FROM `realtime_analytics.clean_events`
WHERE customer_id IS NOT NULL
GROUP BY customer_id;
