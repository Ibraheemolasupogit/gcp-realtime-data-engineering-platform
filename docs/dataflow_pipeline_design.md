# Dataflow Pipeline Design Summary

The detailed reference design lives in `pipelines/dataflow_pipeline_design.md`. This document provides a concise documentation entry point for the docs folder.

## Purpose

Dataflow would run the Apache Beam pipeline that reads Pub/Sub events, parses payloads, validates schema and quality rules, handles event time, routes dead-letter records, and writes clean events to BigQuery.

## Local Mapping

| Local implementation | Dataflow mapping |
| --- | --- |
| `LocalStreamProcessor` | Beam transform graph |
| validation modules | validation DoFns |
| transformation modules | clean-event transform DoFns |
| dead-letter handler | tagged side output |
| monitoring summaries | Dataflow counters and logs |

## Production Notes

A production Dataflow deployment would need project configuration, service accounts, IAM, staging and temp locations, Pub/Sub topics/subscriptions, BigQuery tables, and monitoring policies.

This repository does not deploy or run Dataflow.
