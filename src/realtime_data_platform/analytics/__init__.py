"""Local dashboard-ready analytics package."""

from realtime_data_platform.analytics.analytics_runner import run_analytics
from realtime_data_platform.analytics.customer_activity import (
    generate_customer_activity_summary,
)
from realtime_data_platform.analytics.funnel_metrics import generate_funnel_metrics
from realtime_data_platform.analytics.hourly_metrics import generate_hourly_event_metrics
from realtime_data_platform.analytics.io import read_jsonl, write_csv
from realtime_data_platform.analytics.product_activity import generate_product_activity_summary
from realtime_data_platform.analytics.transaction_summary import (
    generate_transaction_value_summary,
)

__all__ = [
    "generate_customer_activity_summary",
    "generate_funnel_metrics",
    "generate_hourly_event_metrics",
    "generate_product_activity_summary",
    "generate_transaction_value_summary",
    "read_jsonl",
    "run_analytics",
    "write_csv",
]
