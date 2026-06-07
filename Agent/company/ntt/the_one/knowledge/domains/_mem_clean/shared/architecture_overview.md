# The1 Data Platform -- Architecture Overview

## Platform Summary

Multi-domain data platform on GCP collecting data from Kafka topics and REST APIs. Data flows through three layers: raw Iceberg (source), refined BigQuery (CDC/upsert), and public BigQuery (Dataform-managed views and tables). Each business domain has its own GCP project, pipelines, and infrastructure.

## Layer Model

```
Source (raw)     : Iceberg tables on GCS -- raw JSON/Avro, partitioned by ingested date
                   Written by Dataflow (managed.Write) or CloudRun (PyIceberg)

Refined (clean)  : BigQuery tables -- CDC upsert/delete, typed columns, primary keys
                   Written by Dataflow (BQ Storage Write API) or deploy.py (CREATE/ALTER)

Public (served)  : BigQuery views/tables -- Dataform SQL transformations, JOINs across domains
                   Managed by Dataform repositories with scheduled runs
```

## Domain Map

| Domain | GCP Project Pattern | Pipeline Type | Collectors |
|--------|-------------------|---------------|------------|
| loyalty | the1-loyalty-data-{env} | Dataflow streaming + batch | members, tiers, m-t-h, coupons, purchases, transactions |
| loyalty-mart | the1-loyalty-data-{env} | Dataform | BQ mart views on loyalty refined |
| sales | the1-sales-data-{env} | Dataflow streaming | sales-collector |
| catalog | the1-catalog-data-{env} | Dataflow streaming | products-collector |
| gamification | the1-gamification-data-{env} | Dataflow streaming + CloudRun batch | account-missions, master |
| message | the1-messaging-data-{env} | Dataflow streaming + CloudRun batch | messages, master |
| partner | the1-partner-data-{env} | CloudRun batch | master |
| insight | the1-insight-data-{env} | Dataflow streaming | customer-profile, customer-activity |

## Technology Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.12 |
| Stream/Batch Framework | Apache Beam 2.6x/2.7x |
| Managed Runner | Google Cloud Dataflow (Flex Templates) |
| Web Framework | FastAPI (CloudRun services) |
| Message Broker | Kafka (Confluent Cloud) with Schema Registry + Avro |
| Data Lake | Apache Iceberg on GCS (via BigLake Metastore) |
| Data Warehouse | Google BigQuery (Storage Write API, CDC mode) |
| Catalog | BigLake Metastore (BLMS REST, vended credentials) |
| Key-Value Store | Cloud Bigtable (martech_map for insight) |
| Event Bus | Google PubSub (message domain triggers) |
| SQL Transform | Google Dataform (public layer) |
| IaC | Terraform (GCS backend, workspace-based envs) |
| CI/CD | GitLab CI (shared templates, Kaniko builds) |
| Package Mgmt | uv (Python), pyproject.toml |
| Linting | ruff (check + format), mypy (type check) |
| Testing | pytest |
| Pre-commit | pre-commit hooks (ruff, mypy, YAML lint) |

## Data Flow Diagram

```
                    +------------------+
                    |   Kafka Topics   |
                    | (Confluent Cloud)|
                    +--------+---------+
                             |
              +--------------+--------------+
              |                             |
     Streaming (Dataflow)          Batch (CloudRun)
     members, sales, messages      tiers, m-t-h, partner,
     account-missions, products    gamification master,
     customer-profile/activity     message master
              |                             |
              v                             v
     +------------------+         +------------------+
     | managed.Write    |         | PyIceberg write  |
     | (Beam IcebergIO) |         | (direct)         |
     +--------+---------+         +--------+---------+
              |                             |
              +-------------+---------------+
                            |
                            v
                 +---------------------+
                 | Iceberg on GCS      |
                 | (Source layer)       |
                 | BigLake Metastore    |
                 +----------+----------+
                            |
                            v
                 +---------------------+
                 | BigQuery            |
                 | (Refined layer)     |
                 | CDC upsert/delete   |
                 +----------+----------+
                            |
                            v
                 +---------------------+
                 | BigQuery / Dataform |
                 | (Public layer)      |
                 | Views, JOINs,       |
                 | aggregations        |
                 +---------------------+
```

## Pipeline Types

### Streaming (Dataflow)
- Reads from Kafka continuously
- Processes: decode, filter/attach event name, transform, write
- Writes to both Iceberg (source) and BQ (refined) simultaneously
- Update via cancel+redeploy or drain+redeploy
- Example: members-collector, sales-collector

### Batch via Cloud Scheduler (CloudRun or Dataflow)
- Triggered by Cloud Scheduler (cron, typically 1AM Bangkok time)
- Fetches from REST APIs or processes accumulated data
- Writes to Iceberg then BQ
- Example: tiers-collector (Dataflow batch), partner-master (CloudRun)

### Initial Data Load (CI-triggered)
- Triggered by `TRIGGER_INIT_DATA_LOAD=1` in GitLab CI
- `job_type=initial_data` -- full historical load
- One-time or on-demand backfill
- Example: members-collector init load

### Dataform (SQL transforms)
- Scheduled SQL transforms on BQ refined tables
- Produces public-layer views and tables
- Cross-domain JOINs (e.g., partner + sales)
- Example: loyalty-mart
