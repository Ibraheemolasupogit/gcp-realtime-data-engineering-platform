"""Dead-letter review Markdown report generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def render_dead_letter_review_report(summary: dict[str, Any]) -> str:
    """Render a Markdown report for local dead-letter review."""
    reason_lines = "\n".join(
        f"- `{reason}`: `{count}`"
        for reason, count in summary["counts_by_rejection_reason"].items()
    )
    action_lines = "\n".join(
        f"- `{reason}`: {'; '.join(actions)}"
        for reason, actions in summary["recommended_actions_by_reason"].items()
    )
    retry_policy = summary["retry_policy"]
    replay_lines = (
        "\n".join(
            f"- `{candidate['event_id']}`: `{candidate['rejection_reason']}` "
            f"({candidate['classification_reason']})"
            for candidate in summary["replay_candidates"][:10]
        )
        if summary["replay_candidates"]
        else "- No replay candidates identified."
    )

    return f"""# Dead-Letter Review Report

## Executive Summary

Reviewed `{summary["total_dead_letter_events"]}` local dead-letter events at
`{summary["reviewed_at"]}`.
Replayable events: `{summary["replayable_events"]}`.
Non-replayable events: `{summary["non_replayable_events"]}`.

## Dead-Letter Reason Breakdown

{reason_lines}

## Replayable Versus Non-Replayable Summary

- Replayable events: `{summary["replayable_events"]}`
- Non-replayable events: `{summary["non_replayable_events"]}`

Replay candidates:

{replay_lines}

## Recommended Actions

{action_lines}

## Retry Policy Summary

- Max attempts: `{retry_policy["max_attempts"]}`
- Base backoff seconds: `{retry_policy["backoff_seconds"]}`
- Backoff multiplier: `{retry_policy["backoff_multiplier"]}`
- Retryable reasons: `{", ".join(retry_policy["retryable_reasons"])}`
- Non-retryable reasons: `{", ".join(retry_policy["non_retryable_reasons"])}`

## Idempotency Safeguards

Replay candidates include deterministic idempotency keys derived from original event context.
Duplicate events are only conditionally replayable and require an idempotency-state
check before reprocessing.
Replay jobs should be safe to run more than once only when writes are idempotent.

## GCP Reliability Mapping

This local workflow maps conceptually to Pub/Sub dead-letter topics, Dataflow side outputs,
BigQuery retry-safe writes, Cloud Logging error records, and Cloud Monitoring alerts.
No live GCP reliability resources are provisioned.

## Limitations

- Replay is simulated locally and does not republish to Pub/Sub.
- Data repair and enrichment are not implemented yet.
- Exactly-once semantics are not claimed; the design favors at-least-once
  processing with idempotent writes.
- Dataflow watermarking and BigQuery write retries are described as future deployment concerns only.
"""


def write_dead_letter_review_report(summary: dict[str, Any], path: str | Path) -> None:
    """Write the dead-letter review Markdown report."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_dead_letter_review_report(summary), encoding="utf-8")
