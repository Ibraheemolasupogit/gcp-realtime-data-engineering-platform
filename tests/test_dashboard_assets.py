import importlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_module_is_import_safe_without_streamlit() -> None:
    dashboard = importlib.import_module("dashboard.streamlit_app")

    assert "Total clean events" in dashboard.PANEL_NAMES
    assert "Monitoring alerts" in dashboard.PANEL_NAMES


def test_dashboard_panel_summary_handles_missing_files(tmp_path: Path) -> None:
    dashboard = importlib.import_module("dashboard.streamlit_app")

    summary = dashboard.get_dashboard_panel_summary(tmp_path)

    assert summary["total_clean_events"] == 0
    assert "hourly_event_metrics" in summary["missing_sources"]


def test_dashboard_docs_contain_expected_sections() -> None:
    dashboard_readme = (PROJECT_ROOT / "dashboard/README.md").read_text(encoding="utf-8")
    design_doc = (PROJECT_ROOT / "docs/dashboard_design.md").read_text(encoding="utf-8")

    for concept in [
        "Total clean events",
        "Dead-letter events",
        "Data quality score",
        "Pipeline status",
        "Funnel metrics",
    ]:
        assert concept in dashboard_readme
        assert concept in design_doc

    assert "Looker Studio" in design_doc
    assert "No BigQuery queries are executed" in design_doc
