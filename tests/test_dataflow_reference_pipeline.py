import importlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_apache_beam_reference_pipeline_is_import_safe() -> None:
    module = importlib.import_module("pipelines.apache_beam_pipeline")

    description = module.describe_reference_pipeline()

    assert "DirectRunner" in description["runner"]
    assert "ReadFromPubSub" in description["inputs"]["pubsub_placeholder"]
    assert "WriteToBigQuery" in description["outputs"]["bigquery_placeholder"]
    assert "No credentials required." in description["safety"]


def test_apache_beam_reference_file_contains_expected_concepts() -> None:
    content = (PROJECT_ROOT / "pipelines/apache_beam_pipeline.py").read_text(encoding="utf-8")

    for concept in [
        "apache-beam is not installed",
        "ReadFromPubSub",
        "WriteToBigQuery",
        "FixedWindows",
        "allowed_lateness",
        "dead-letter",
        "DirectRunner",
    ]:
        assert concept in content


def test_dataflow_design_doc_contains_required_sections() -> None:
    content = (PROJECT_ROOT / "pipelines/dataflow_pipeline_design.md").read_text(encoding="utf-8")

    for concept in [
        "Pub/Sub Input Design",
        "Dataflow Transform Stages",
        "Windowing And Watermarking",
        "Dead-Letter Side Output",
        "BigQuery Sink Strategy",
        "Cloud Storage Raw Archive Strategy",
        "Cloud Logging",
        "Cloud Monitoring",
        "does not provision",
    ]:
        assert concept in content


def test_dataflow_reference_does_not_require_live_credentials() -> None:
    content = (PROJECT_ROOT / "pipelines/apache_beam_pipeline.py").read_text(encoding="utf-8")

    forbidden_runtime_patterns = [
        "GOOGLE_APPLICATION_CREDENTIALS",
        "\npipeline.run(",
        "google.cloud",
    ]
    for pattern in forbidden_runtime_patterns:
        assert pattern not in content
