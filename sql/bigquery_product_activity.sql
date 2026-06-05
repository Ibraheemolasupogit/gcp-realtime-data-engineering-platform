-- BigQuery Standard SQL
-- Purpose: Model product-level engagement from `realtime_analytics.clean_events`
-- into `realtime_analytics.product_activity_summary`.
-- This file is a local design artifact only; it is not executed against BigQuery.

CREATE OR REPLACE TABLE `realtime_analytics.product_activity_summary`
CLUSTER BY product_id
AS
SELECT
  product_id,
  COUNTIF(event_type = 'product_viewed') AS product_views,
  COUNTIF(event_type = 'product_added_to_basket') AS basket_additions,
  COUNTIF(event_type = 'product_removed_from_basket') AS basket_removals,
  COUNTIF(event_type = 'product_wishlisted') AS wishlist_events,
  COUNTIF(event_type = 'purchase_completed') AS purchase_events,
  COUNTIF(event_type IN ('refund_requested', 'refund_completed')) AS refund_events
FROM `realtime_analytics.clean_events`
WHERE product_id IS NOT NULL
GROUP BY product_id;
