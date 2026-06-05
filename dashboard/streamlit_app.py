"""Optional local Streamlit dashboard for generated analytics outputs.

The dashboard is defensive and local-only. It does not connect to BigQuery,
Looker Studio, or any GCP service. Streamlit is optional; importing this module
does not require Streamlit to be installed.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

PANEL_NAMES = [
    "Total clean events",
    "Dead-letter events",
    "Data quality score",
    "Pipeline status",
    "Hourly event volume",
    "Customer activity summary",
    "Product activity summary",
    "Transaction value summary",
    "Funnel metrics",
    "Dead-letter/replay summary",
    "Monitoring alerts",
]


def get_dashboard_panel_summary(project_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    """Return compact dashboard metrics without requiring Streamlit."""
    from realtime_data_platform.reporting import build_report_context

    context = build_report_context(project_root)
    metrics = context["metrics"]
    quality_summary = context["quality_summary"]
    monitoring_summary = context["monitoring_summary"]
    dead_letter_summary = context["dead_letter_summary"]
    transaction_summary = context["transaction_summary"]
    funnel_summary = context["funnel_summary"]

    return {
        "total_clean_events": metrics.get("clean_events_written", 0),
        "dead_letter_events": metrics.get("dead_letter_events_written", 0),
        "data_quality_score": quality_summary.get("average_quality_score", 0),
        "pipeline_status": monitoring_summary.get("pipeline_status", "unknown"),
        "hourly_event_rows": len(context["hourly_rows"]),
        "customer_rows": len(context["customer_rows"]),
        "product_rows": len(context["product_rows"]),
        "transaction_value_summary": transaction_summary,
        "funnel_metrics": funnel_summary,
        "replayable_dead_letter_events": dead_letter_summary.get("replayable_events", 0),
        "critical_alerts": monitoring_summary.get("alert_counts_by_severity", {}).get(
            "critical", 0
        ),
        "missing_sources": context["missing_sources"],
    }


def main() -> None:
    """Run the optional local Streamlit dashboard."""
    try:
        import streamlit as st
    except ImportError:
        summary = get_dashboard_panel_summary(PROJECT_ROOT)
        print("Streamlit is not installed. Local dashboard data is still available.")
        print(summary)
        return

    from realtime_data_platform.reporting import build_report_context

    context = build_report_context(PROJECT_ROOT)
    panel_summary = get_dashboard_panel_summary(PROJECT_ROOT)

    st.set_page_config(page_title="Realtime Retail Pipeline", layout="wide")
    st.title("Realtime Retail Pipeline")
    st.caption("Local dashboard over generated outputs. No live GCP services are used.")

    if panel_summary["missing_sources"]:
        st.warning(f"Missing source files: {', '.join(panel_summary['missing_sources'])}")

    metric_columns = st.columns(4)
    metric_columns[0].metric("Clean Events", panel_summary["total_clean_events"])
    metric_columns[1].metric("Dead-Letter Events", panel_summary["dead_letter_events"])
    metric_columns[2].metric("Quality Score", panel_summary["data_quality_score"])
    metric_columns[3].metric("Pipeline Status", panel_summary["pipeline_status"])

    st.subheader("Hourly Event Volume")
    st.dataframe(context["hourly_rows"], use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Customer Activity")
        st.dataframe(context["customer_rows"], use_container_width=True)
        st.subheader("Transaction Value")
        st.json(panel_summary["transaction_value_summary"])
    with right:
        st.subheader("Product Activity")
        st.dataframe(context["product_rows"], use_container_width=True)
        st.subheader("Funnel Metrics")
        st.json(panel_summary["funnel_metrics"])

    st.subheader("Dead-Letter And Replay")
    st.json(context["dead_letter_summary"])

    st.subheader("Monitoring Alerts")
    st.json(context["monitoring_summary"].get("alerts", []))


if __name__ == "__main__":
    main()
