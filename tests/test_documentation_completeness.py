from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

KEY_DOCS = [
    "docs/gcp_reference_architecture.md",
    "docs/pubsub_topic_design.md",
    "docs/dataflow_pipeline_design.md",
    "docs/bigquery_data_model.md",
    "docs/cloud_storage_archive_design.md",
    "docs/looker_studio_mapping.md",
    "docs/monitoring_strategy.md",
    "docs/governance_and_catalog_design.md",
    "docs/local_runbook.md",
    "docs/portfolio_positioning.md",
    "docs/limitations.md",
    "docs/production_roadmap.md",
]

README_SECTIONS = [
    "Problem Statement",
    "What This Project Demonstrates",
    "Architecture Overview",
    "Local-First Implementation Note",
    "GCP Service Mapping",
    "End-To-End Local Workflow",
    "Outputs Generated",
    "Repository Structure",
    "How To Run",
    "Milestone Summary",
    "Portfolio Positioning",
    "Limitations",
    "Future Production Roadmap",
    "No Credentials Or Cloud Cost",
]

RUNBOOK_COMMANDS = [
    "python -m venv .venv",
    "python -m pip install -r requirements.txt",
    "python -m pytest",
    "python scripts/generate_demo_events.py",
    "python scripts/run_local_stream.py",
    "python scripts/run_quality_checks.py",
    "python scripts/generate_reports.py",
    "python scripts/run_dead_letter_review.py",
    "python -m streamlit run dashboard/streamlit_app.py",
]

GCP_SERVICES = [
    "Pub/Sub",
    "Dataflow",
    "Apache Beam",
    "Cloud Storage",
    "BigQuery",
    "Looker Studio",
    "Cloud Logging",
    "Cloud Monitoring",
    "Secret Manager",
    "Dataplex",
    "Data Catalog",
]


def test_key_documentation_files_exist_and_are_not_empty() -> None:
    for relative_path in KEY_DOCS:
        path = PROJECT_ROOT / relative_path

        assert path.exists(), f"Missing documentation file: {relative_path}"
        assert path.read_text(encoding="utf-8").strip()


def test_readme_contains_required_sections() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    for section in README_SECTIONS:
        assert f"## {section}" in readme


def test_local_runbook_contains_end_to_end_command_sequence() -> None:
    runbook = (PROJECT_ROOT / "docs/local_runbook.md").read_text(encoding="utf-8")

    for command in RUNBOOK_COMMANDS:
        assert command in runbook


def test_architecture_docs_mention_core_gcp_services() -> None:
    architecture = (PROJECT_ROOT / "docs/gcp_reference_architecture.md").read_text(encoding="utf-8")

    for service in GCP_SERVICES:
        assert service in architecture


def test_limitations_clearly_state_no_live_gcp_resources() -> None:
    limitations = (PROJECT_ROOT / "docs/limitations.md").read_text(encoding="utf-8")

    assert "No live GCP resources are provisioned" in limitations
    assert "No GCP credentials" in limitations
    assert "BigQuery SQL is design/portfolio SQL" in limitations


def test_mermaid_diagrams_exist() -> None:
    for relative_path in [
        "diagrams/architecture.mmd",
        "diagrams/streaming_pipeline.mmd",
        "diagrams/dataflow_reference_architecture.mmd",
        "diagrams/monitoring_workflow.mmd",
    ]:
        path = PROJECT_ROOT / relative_path

        assert path.exists()
        assert "flowchart" in path.read_text(encoding="utf-8")


def test_no_obvious_credentials_or_secret_placeholders_are_present() -> None:
    searchable_files = [
        *KEY_DOCS,
        "README.md",
        "pipelines/apache_beam_pipeline.py",
    ]
    forbidden = [
        "-----BEGIN PRIVATE KEY-----",
        "client_secret",
        "private_key_id",
        "GOOGLE_APPLICATION_CREDENTIALS=",
        "AIza",
    ]

    for relative_path in searchable_files:
        content = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
        for pattern in forbidden:
            assert pattern not in content
