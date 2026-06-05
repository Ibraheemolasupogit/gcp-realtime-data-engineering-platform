"""Run local analytical aggregations over clean stream outputs."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from realtime_data_platform.analytics.customer_activity import (
    CUSTOMER_ACTIVITY_FIELDS,
    generate_customer_activity_summary,
)
from realtime_data_platform.analytics.funnel_metrics import (
    FUNNEL_METRICS_FIELDS,
    generate_funnel_metrics,
)
from realtime_data_platform.analytics.hourly_metrics import (
    HOURLY_METRICS_FIELDS,
    generate_hourly_event_metrics,
)
from realtime_data_platform.analytics.io import read_jsonl, write_csv, write_json
from realtime_data_platform.analytics.product_activity import (
    PRODUCT_ACTIVITY_FIELDS,
    generate_product_activity_summary,
)
from realtime_data_platform.analytics.transaction_summary import (
    TRANSACTION_VALUE_FIELDS,
    generate_transaction_value_summary,
)


def run_analytics(
    *,
    clean_events_path: str | Path = "outputs/clean_events.jsonl",
    output_dir: str | Path = "outputs",
) -> dict[str, Any]:
    """Generate all local dashboard-ready analytics outputs."""
    events = read_jsonl(clean_events_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    hourly_rows = generate_hourly_event_metrics(events)
    customer_rows = generate_customer_activity_summary(events)
    product_rows = generate_product_activity_summary(events)
    transaction_rows = generate_transaction_value_summary(events)
    funnel_rows = generate_funnel_metrics(events)

    outputs = {
        "hourly_event_metrics": output_path / "hourly_event_metrics.csv",
        "customer_activity_summary": output_path / "customer_activity_summary.csv",
        "product_activity_summary": output_path / "product_activity_summary.csv",
        "transaction_value_summary": output_path / "transaction_value_summary.csv",
        "funnel_metrics": output_path / "funnel_metrics.csv",
        "analytics_summary": output_path / "analytics_summary.json",
    }

    write_csv(outputs["hourly_event_metrics"], hourly_rows, HOURLY_METRICS_FIELDS)
    write_csv(outputs["customer_activity_summary"], customer_rows, CUSTOMER_ACTIVITY_FIELDS)
    write_csv(outputs["product_activity_summary"], product_rows, PRODUCT_ACTIVITY_FIELDS)
    write_csv(outputs["transaction_value_summary"], transaction_rows, TRANSACTION_VALUE_FIELDS)
    write_csv(outputs["funnel_metrics"], funnel_rows, FUNNEL_METRICS_FIELDS)

    summary = {
        "clean_events_read": len(events),
        "hourly_metric_rows": len(hourly_rows),
        "customer_activity_rows": len(customer_rows),
        "product_activity_rows": len(product_rows),
        "transaction_summary_rows": len(transaction_rows),
        "funnel_metric_rows": len(funnel_rows),
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "outputs": {name: str(path) for name, path in outputs.items()},
    }
    write_json(outputs["analytics_summary"], summary)
    return summary
