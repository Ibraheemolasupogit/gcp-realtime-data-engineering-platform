-- BigQuery Standard SQL
-- Purpose: Design-only schema for rejected event records mapped to
-- `realtime_analytics.dead_letter_events`.
-- This file is not executed by this repository and does not provision BigQuery resources.

CREATE TABLE IF NOT EXISTS `realtime_analytics.dead_letter_events` (
  event_id STRING,
  rejection_reason STRING NOT NULL,
  validation_errors JSON,
  quality_score INT64,
  source_file STRING,
  failed_at TIMESTAMP NOT NULL,
  recommended_action STRING,
  original_event JSON
)
PARTITION BY DATE(failed_at)
CLUSTER BY rejection_reason, source_file
OPTIONS (
  description = "Rejected events and validation metadata for replay and remediation design."
);
