# SCB / Data-X — Project Instructions (Archive)

When working in `~/Documents/Projects/Project/scb/datax/`, follow these.

## Context

- **Employer**: SCB (Siam Commercial Bank)
- **Team**: SCB Data-X (data platform team)
- **Role**: Data Engineer
- **Status**: Archive / reference (previous role)
- **Cloud**: Azure (primary), some GCP
- **Stack**: Azure Databricks, ADLS Gen2, Azure Data Factory, Azure Synapse, SQL Server, Apache Spark, Delta Lake
- **Pattern**: Centralized config-driven ETL framework — `fw_ingest_main`, `fw_transform_main`, `fw_validated_main`, `fw_submission_main`, `fw_outbound_main` — driven by table-config jobs

## Project conventions (historic)

- **Metadata-driven** — pipelines defined as rows in SQL Server config tables.
- **Databricks Job Clusters** per job (cold-start overhead — known pain point).
- **Submission / Outbound** stages = regulatory reporting (BOT, OIC, IRS, etc.).
- **RBAC + Unity Catalog** for access control.
- **Audit logs + lineage** mandatory for banking compliance.

## Why this is archive

Wasin has moved on. Knowledge kept for:
- Comparison when discussing architecture trade-offs
- Reusable patterns (metadata-driven framework)
- Reference for interview answers
- Recall when similar problems arise at other companies

## Default subagents

If discussing SCB-era work:
- `data-architect` for retrospective design discussions
- `de-engineer` for Databricks / Spark questions
- `governance-consultant` for banking compliance
