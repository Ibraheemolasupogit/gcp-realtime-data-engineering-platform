# Cloud Storage Raw Archive Design

Cloud Storage is the recommended raw archive location for a future GCP deployment. This repository models raw event retention locally using JSONL files.

## Purpose

Raw archives support replay, audit, investigation, schema migration, and incident recovery. They preserve the original payload before transformation.

## Proposed Bucket Layout

```text
gs://<project>-retail-event-archive/
  raw/events/year=YYYY/month=MM/day=DD/hour=HH/
  dead-letter/year=YYYY/month=MM/day=DD/
  replay/year=YYYY/month=MM/day=DD/
```

## Local Mapping

| Local artifact | Cloud Storage mapping |
| --- | --- |
| `data/sample/*.jsonl` | raw event archive |
| `outputs/dead_letter_events.jsonl` | dead-letter archive |
| `outputs/dead_letter_review_summary.json` | replay review metadata |

## Governance And Retention

Production storage should include lifecycle policies, retention settings, encryption, IAM, and naming conventions. Sensitive data should be classified before archive retention is finalized.

No Cloud Storage buckets are created by this repository.
