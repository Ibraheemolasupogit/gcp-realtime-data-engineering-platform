-- BigQuery Standard SQL
-- Purpose: Design-only schema for raw local event payloads mapped to
-- `realtime_analytics.raw_events`.
-- This file is not executed by this repository and does not provision BigQuery resources.

CREATE TABLE IF NOT EXISTS `realtime_analytics.raw_events` (
  event_id STRING NOT NULL,
  event_type STRING NOT NULL,
  event_timestamp TIMESTAMP NOT NULL,
  ingestion_timestamp TIMESTAMP NOT NULL,
  event_source STRING NOT NULL,
  customer_id STRING,
  session_id STRING,
  event_version STRING NOT NULL,
  raw_payload JSON NOT NULL,
  source_file STRING,
  loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(event_timestamp)
CLUSTER BY event_type, customer_id, source_file
OPTIONS (
  description = "Raw retail and customer event payloads loaded from local JSONL inputs."
);
