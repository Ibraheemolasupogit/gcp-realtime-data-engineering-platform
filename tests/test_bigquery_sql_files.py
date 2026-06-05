from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "sql"

EXPECTED_SQL_FILES = {
    "bigquery_raw_events_schema.sql": {
        "table": "realtime_analytics.raw_events",
        "fields": ["event_id", "event_type", "event_timestamp", "raw_payload", "loaded_at"],
    },
    "bigquery_clean_events_schema.sql": {
        "table": "realtime_analytics.clean_events",
        "fields": [
            "processed_at",
            "quality_score",
            "processing_status",
            "idempotency_key",
        ],
    },
    "bigquery_dead_letter_events_schema.sql": {
        "table": "realtime_analytics.dead_letter_events",
        "fields": [
            "rejection_reason",
            "validation_errors",
            "recommended_action",
            "original_event",
        ],
    },
    "bigquery_hourly_metrics.sql": {
        "table": "realtime_analytics.hourly_event_metrics",
        "fields": ["event_hour", "total_events", "unique_customers", "unique_sessions"],
    },
    "bigquery_customer_activity.sql": {
        "table": "realtime_analytics.customer_activity_summary",
        "fields": ["customer_id", "total_events", "purchases_count", "refunds_count"],
    },
    "bigquery_product_activity.sql": {
        "table": "realtime_analytics.product_activity_summary",
        "fields": ["product_id", "product_views", "basket_additions", "wishlist_events"],
    },
    "bigquery_transaction_summary.sql": {
        "table": "realtime_analytics.transaction_value_summary",
        "fields": [
            "total_purchase_value",
            "total_refund_value",
            "net_transaction_value",
            "average_purchase_value",
        ],
    },
    "bigquery_funnel_metrics.sql": {
        "table": "realtime_analytics.funnel_metrics",
        "fields": ["sessions_started", "conversion_rate", "abandonment_rate"],
    },
}


def test_required_bigquery_sql_files_exist_and_are_not_empty() -> None:
    for filename in EXPECTED_SQL_FILES:
        path = SQL_DIR / filename

        assert path.exists(), f"Missing SQL file: {filename}"
        assert path.read_text(encoding="utf-8").strip(), f"Empty SQL file: {filename}"


def test_sql_files_use_bigquery_standard_sql_comments_and_table_names() -> None:
    for filename, expectations in EXPECTED_SQL_FILES.items():
        sql = (SQL_DIR / filename).read_text(encoding="utf-8")

        assert "-- BigQuery Standard SQL" in sql
        assert expectations["table"] in sql
        assert "realtime_analytics." in sql


def test_sql_files_include_key_fields() -> None:
    for filename, expectations in EXPECTED_SQL_FILES.items():
        sql = (SQL_DIR / filename).read_text(encoding="utf-8")

        for field in expectations["fields"]:
            assert field in sql, f"{field} missing from {filename}"


def test_schema_files_include_partitioning_or_clustering_recommendations() -> None:
    schema_files = [
        "bigquery_raw_events_schema.sql",
        "bigquery_clean_events_schema.sql",
        "bigquery_dead_letter_events_schema.sql",
        "bigquery_hourly_metrics.sql",
    ]

    for filename in schema_files:
        sql = (SQL_DIR / filename).read_text(encoding="utf-8")

        assert "PARTITION BY" in sql
        assert "CLUSTER BY" in sql


def test_sql_readme_documents_local_design_boundary() -> None:
    readme = (SQL_DIR / "README.md").read_text(encoding="utf-8")

    assert "not executed" in readme
    assert "do not connect to BigQuery" in readme
    assert "raw_events" in readme
    assert "clean_events" in readme
