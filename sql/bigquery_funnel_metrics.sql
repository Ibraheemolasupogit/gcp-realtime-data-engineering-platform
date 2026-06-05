-- BigQuery Standard SQL
-- Purpose: Model retail funnel metrics from `realtime_analytics.clean_events`
-- into `realtime_analytics.funnel_metrics`.
-- This file is a local design artifact only; it is not executed against BigQuery.

CREATE OR REPLACE TABLE `realtime_analytics.funnel_metrics`
AS
WITH funnel_counts AS (
  SELECT
    COUNTIF(event_type = 'session_started') AS sessions_started,
    COUNTIF(event_type = 'product_viewed') AS product_views,
    COUNTIF(event_type = 'product_added_to_basket') AS basket_additions,
    COUNTIF(event_type = 'checkout_started') AS checkout_started,
    COUNTIF(event_type = 'purchase_completed') AS purchases_completed,
    COUNTIF(event_type = 'checkout_abandoned') AS checkout_abandoned
  FROM `realtime_analytics.clean_events`
)
SELECT
  sessions_started,
  product_views,
  basket_additions,
  checkout_started,
  purchases_completed,
  checkout_abandoned,
  SAFE_DIVIDE(purchases_completed, sessions_started) AS conversion_rate,
  SAFE_DIVIDE(checkout_abandoned, checkout_started) AS abandonment_rate
FROM funnel_counts;
