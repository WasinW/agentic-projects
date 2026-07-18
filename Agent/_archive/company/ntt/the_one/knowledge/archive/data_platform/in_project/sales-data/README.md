# Sales-Collector Documentation

> **GCP Project:** `the1-sales-data-{env}` (env: stg, prod)
> **Repository:** `gitlab.com/The1central/The1/the1-data/sales-data`
> **Region:** asia-southeast1
> **Last Updated:** 2026-02-22

---

## Overview

Sales-collector is a streaming data pipeline that ingests sales transaction events from two Kafka topics (`loyalty.sales.created`, `loyalty.sales.updated`), writes raw events to Apache Iceberg tables on GCS via BigLake Metastore REST Catalog, and fans out to three BigQuery refined tables (`sales_receipt`, `sales_sku`, `sales_tender`). The pipeline runs on Google Cloud Dataflow as a Flex Template, follows hexagonal architecture, and is deployed through GitLab CI/CD.

Currently the pipeline writes to Iceberg (source layer) with BQ writes commented out pending end-to-end validation.

---

## Quick Reference

| Topic | Iceberg Table | BQ Table(s) | Description |
|-------|---------------|-------------|-------------|
| `loyalty.sales.created` | `source.raw_sales_created` | `refined.sales_receipt` | Receipt headers (1 row/event) |
| `loyalty.sales.updated` | `source.raw_sales_updated` | `refined.sales_sku` | SKU line items (N rows/event) |
| | | `refined.sales_tender` | Tender/payments (M rows/event) |

| Property | Value |
|----------|-------|
| Language | Python 3.12 |
| Framework | Apache Beam 2.70.0 |
| Deployment | Dataflow Flex Template |
| Kafka Group | `sales-data-sales` |
| Window Size | 5 seconds |
| Iceberg Trigger | 300 seconds |
| Service Account | `t1-sales-collector@the1-sales-data-{env}.iam.gserviceaccount.com` |

---

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | High-level and detailed architecture diagrams, hexagonal layers, infrastructure, BLMS auth flow |
| [CICD_WORKFLOW.md](./CICD_WORKFLOW.md) | CI/CD stages, job dependencies, deploy strategy, STG vs PROD comparison |
| [DATA_PIPELINE.md](./DATA_PIPELINE.md) | Data pipeline flow, per-topic branching, merge + fan-out, message format handling, timestamp logic |
| [SCHEMA_MAPPING.md](./SCHEMA_MAPPING.md) | Kafka event structure, field mappings for all 3 BQ tables, type conversions, Avro unwrapping |
