from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gcp_reference_architecture_documents_expected_components() -> None:
    content = (PROJECT_ROOT / "docs/gcp_reference_architecture.md").read_text(encoding="utf-8")

    for concept in [
        "Pub/Sub",
        "Dataflow",
        "Cloud Storage",
        "BigQuery",
        "Looker Studio",
        "Cloud Logging",
        "Cloud Monitoring",
        "Secret Manager",
        "Dataplex",
        "Data Catalog",
        "No live",
    ]:
        assert concept in content


def test_distributed_systems_design_documents_reliability_concepts() -> None:
    content = (PROJECT_ROOT / "docs/distributed_systems_design.md").read_text(encoding="utf-8")

    for concept in [
        "Ordering Considerations",
        "At-Least-Once Delivery",
        "Idempotency",
        "Replay Safety",
        "Backpressure",
        "Late And Duplicate Event Handling",
        "Schema Evolution",
        "Failure Recovery",
        "Pub/Sub + Dataflow + BigQuery",
    ]:
        assert concept in content


def test_dataflow_mermaid_diagram_includes_expected_gcp_components() -> None:
    content = (PROJECT_ROOT / "diagrams/dataflow_reference_architecture.mmd").read_text(
        encoding="utf-8"
    )

    for concept in [
        "Pub/Sub Topic",
        "Pub/Sub Subscription",
        "Dataflow / Apache Beam Pipeline",
        "Validation, Deduplication, and Event-Time Checks",
        "BigQuery Table",
        "Dead-Letter Topic",
        "Cloud Storage Raw Archive",
        "Cloud Logging",
        "Cloud Monitoring",
        "Looker Studio Dashboard",
    ]:
        assert concept in content
