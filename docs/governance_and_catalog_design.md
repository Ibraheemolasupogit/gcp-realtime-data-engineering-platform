# Governance And Catalog Design

This repository includes local schema, quality, and SQL design artifacts that could map to governance tools in a production GCP environment.

## Dataplex And Data Catalog Mapping

| Local artifact | Governance mapping |
| --- | --- |
| `configs/event_schema.yaml` | schema documentation and metadata entry |
| `configs/quality_rules.yaml` | data quality policy metadata |
| `sql/*.sql` | BigQuery table and view definitions |
| `docs/data_dictionary.md` | business glossary and field definitions |
| `docs/bigquery_data_model.md` | dataset and lineage documentation |

## Governance Considerations

- Dataset ownership.
- Field-level descriptions.
- Schema versioning.
- Data quality rule ownership.
- Retention policy.
- PII classification.
- Lineage from Pub/Sub to Dataflow to BigQuery to dashboards.

## Local Limitation

No Dataplex, Data Catalog, policy tags, lineage APIs, or governance resources are created by this repository.
