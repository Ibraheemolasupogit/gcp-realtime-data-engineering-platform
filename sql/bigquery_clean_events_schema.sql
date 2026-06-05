-- BigQuery Standard SQL
-- Purpose: Design-only schema for validated, deduplicated, dashboard-ready
-- clean events mapped to `realtime_analytics.clean_events`.
-- This file is not executed by this repository and does not provision BigQuery resources.

CREATE TABLE IF NOT EXISTS `realtime_analytics.clean_events` (
  event_id STRING NOT NULL,
  event_type STRING NOT NULL,
  event_timestamp TIMESTAMP NOT NULL,
  ingestion_timestamp TIMESTAMP NOT NULL,
  processed_at TIMESTAMP NOT NULL,
  event_source STRING NOT NULL,
  customer_id STRING,
  session_id STRING,
  product_id STRING,
  transaction_id STRING,
  transaction_amount NUMERIC,
  currency STRING,
  quality_score INT64,
  processing_status STRING NOT NULL,
  idempotency_key STRING NOT NULL,
  source_file STRING
)
PARTITION BY DATE(event_timestamp)
CLUSTER BY event_type, customer_id, product_id
OPTIONS (
  description = "Clean event records produced after local validation and transformation."
);
