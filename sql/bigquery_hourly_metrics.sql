-- BigQuery Standard SQL
-- Purpose: Model hourly dashboard metrics from `realtime_analytics.clean_events`
-- into `realtime_analytics.hourly_event_metrics`.
-- This file is a local design artifact only; it is not executed against BigQuery.

CREATE OR REPLACE TABLE `realtime_analytics.hourly_event_metrics`
PARTITION BY DATE(event_hour)
CLUSTER BY event_hour
AS
SELECT
  TIMESTAMP_TRUNC(event_timestamp, HOUR) AS event_hour,
  COUNT(*) AS total_events,
  COUNT(DISTINCT customer_id) AS unique_customers,
  COUNT(DISTINCT session_id) AS unique_sessions,
  COUNTIF(event_type LIKE 'customer_%') AS customer_events,
  COUNTIF(event_type LIKE 'product_%') AS product_events,
  COUNTIF(event_type IN (
    'purchase_completed',
    'payment_failed',
    'refund_requested',
    'refund_completed'
  )) AS transaction_events,
  COUNTIF(event_type IN (
    'session_started',
    'session_ended',
    'checkout_started',
    'checkout_abandoned'
  )) AS session_events
FROM `realtime_analytics.clean_events`
GROUP BY event_hour;
