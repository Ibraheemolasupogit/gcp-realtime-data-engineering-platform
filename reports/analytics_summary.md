# Analytics Summary Report

## Executive Summary

This local report summarizes dashboard-ready analytics, data quality, monitoring, and
dead-letter reliability outputs. It was generated at `2026-06-05T09:52:07.775650Z`.

All expected local dashboard source files were found.

## Event Volume Summary

- Clean events read by analytics: `48`
- Total events processed: `64`
- Clean events written: `48`
- Dead-letter events written: `16`
- Hourly metric rows: `1`

## Customer Activity Summary

- Customer summary rows: `8`
- Top customer rows available: `8`
- Dashboard use: customer activity, sessions, purchases, refunds, basket additions,
  and checkout abandonments.

## Product Activity Summary

- Product summary rows: `9`
- Product rows available: `9`
- Dashboard use: product views, basket interactions, wishlist activity, and
  transaction-linked product metrics where available.

## Transaction Value Summary

- Total purchase value: `1158.58`
- Total refund value: `1726.94`
- Net transaction value: `-568.36`
- Purchase count: `3`
- Failed payment count: `3`

## Funnel And Conversion Summary

- Sessions started: `3`
- Product views: `3`
- Basket additions: `3`
- Checkout started: `3`
- Purchases completed: `3`
- Checkout abandoned: `3`
- Conversion rate: `1.0`
- Abandonment rate: `1.0`

## Data Quality Summary

- Average quality score: `98.22`
- Quality band: `Excellent`
- Valid events: `48`
- Invalid events: `16`

## Dead-Letter And Reliability Summary

- Total dead-letter events reviewed: `16`
- Replayable events: `8`
- Non-replayable events: `8`
- Duplicate rate: `0.0625`
- Late-event rate: `0.125`

## Pipeline Monitoring Summary

- Pipeline status: `failed`
- Critical alerts: `1`
- Warning alerts: `0`
- Dead-letter rate: `0.25`
- Processing errors: `0`

## Recommended Interpretation

The local outputs are suitable for portfolio review of the platform's analytical and
operational surfaces. A high dead-letter rate in the sample data is expected because
the generated fixture intentionally includes malformed, duplicate, late, and invalid
records for validation and reliability testing.

## GCP And Looker Studio Mapping

These local CSV and JSON artifacts map conceptually to BigQuery aggregate tables and
Looker Studio dashboard panels. In a real GCP deployment, BigQuery would hold the
clean and aggregate models, Looker Studio would provide visualization, and Cloud
Monitoring would track operational health.

This is a local reporting artifact only. It is not a live Looker Studio dashboard,
does not connect to BigQuery, and does not provision GCP resources.
