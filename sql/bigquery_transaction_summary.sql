-- BigQuery Standard SQL
-- Purpose: Model transaction value metrics from `realtime_analytics.clean_events`
-- into `realtime_analytics.transaction_value_summary`.
-- This file is a local design artifact only; it is not executed against BigQuery.

CREATE OR REPLACE TABLE `realtime_analytics.transaction_value_summary`
AS
SELECT
  COALESCE(SUM(IF(event_type = 'purchase_completed', transaction_amount, 0)), 0)
    AS total_purchase_value,
  COALESCE(SUM(IF(event_type IN ('refund_requested', 'refund_completed'), transaction_amount, 0)), 0)
    AS total_refund_value,
  COALESCE(SUM(IF(event_type = 'purchase_completed', transaction_amount, 0)), 0)
    - COALESCE(SUM(IF(event_type IN ('refund_requested', 'refund_completed'), transaction_amount, 0)), 0)
    AS net_transaction_value,
  COUNTIF(event_type = 'purchase_completed') AS purchase_count,
  COUNTIF(event_type IN ('refund_requested', 'refund_completed')) AS refund_count,
  COUNTIF(event_type = 'payment_failed') AS failed_payment_count,
  COALESCE(AVG(IF(event_type = 'purchase_completed', transaction_amount, NULL)), 0)
    AS average_purchase_value
FROM `realtime_analytics.clean_events`;
