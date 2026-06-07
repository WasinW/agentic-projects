# The1 Data Platform Documentation

> **Master Index** | AI: Start here to find the right documentation for any task.

## How AI Should Use This Documentation

```
Building a new collector?     → 08_development → 02_ingestion → 03_storage → 04_processing → 07_cicd
Adding a new BQ table?        → 03_storage (schema + deploy.py)
Adding CDC DELETE?            → 04_processing (CDC pattern) → 03_storage (BigQuerySink)
Writing a new DoFn?           → 04_processing (DoFn patterns)
Fixing a bug?                 → 09_operations (troubleshooting) → relevant topic
Comparing cloud platforms?    → {topic}/REFERENCE.md
Understanding architecture?   → 01_architecture
```

---

## Topic-Based Documentation

Each topic has two files:
- **INSTRUCTIONS.md** — Practical guide for AI coding (patterns, code templates, do/don't)
- **REFERENCE.md** — Cross-cloud comparison encyclopedia (for learning/comparing)

| # | Topic | INSTRUCTIONS.md | REFERENCE.md | When to Read |
|---|-------|-----------------|--------------|--------------|
| 01 | [Architecture](01_architecture/) | Platform overview, layers, hexagonal arch | Cross-cloud architecture patterns | Understanding the platform |
| 02 | [Ingestion](02_ingestion/) | Kafka, API batch, PostgreSQL, init load | Streaming services comparison | Reading data from sources |
| 03 | [Storage](03_storage/) | Iceberg (BLMS), BQ (Storage Write API), schemas | Warehouse/lakehouse comparison | Writing data to storage |
| 04 | [Processing](04_processing/) | Beam DoFns, transforms, CDC, fan-out | Processing engine comparison | Transforming data |
| 05 | [Serving](05_serving/) | Dataform views, public layer, BI | BI tools comparison | Exposing data to consumers |
| 06 | [Governance](06_governance/) | DLQ, data quality, naming, access control | Governance comparison | Data quality + governance |
| 07 | [CI/CD](07_cicd/) | GitLab CI, Terraform, deploy scripts | CI/CD patterns comparison | Deploying pipelines |
| 08 | [Development](08_development/) | Repo structure, config, testing, code quality | Tool comparison | Writing + testing code |
| 09 | [Operations](09_operations/) | Troubleshooting, monitoring, alerting | Observability patterns | Running + debugging pipelines |
| 10 | [Security](10_security/) | Service accounts, IAM, secrets, VPC | Cloud security comparison | Security + access |

---

## Per-Project Documentation

| Project | Document | Description |
|---------|----------|-------------|
| Loyalty Data | [projects/loyalty-data/](projects/loyalty-data/) | 6 collectors, Iceberg/BQ write paths, CI/CD |
| Sales Data | [projects/sales-data/](projects/sales-data/) | sales-collector (streaming), 3 BQ tables |
| Insight | [projects/insight/](projects/insight/) | Pipeline + APIs (Kotlin) + Collector (Node.js) |
| Common Data | [projects/common-data/](projects/common-data/) | Shared library: Beam adapters + Cloud Run utils |
| Partner Data | [projects/partner-data/](projects/partner-data/) | companies-collector + master-collector |

---

## Quick Reference: Common Tasks

### After ANY code change — run all 5:
```bash
uv sync && uv run ruff check --fix . && uv run ruff format . && uv run mypy src tests && uv run pytest
```

### Key Patterns

| Pattern | Where to Find |
|---------|--------------|
| Bangkok timezone (+7) | [03_storage](03_storage/INSTRUCTIONS.md#3-timestamp-handling-critical), [04_processing](04_processing/INSTRUCTIONS.md#4-payload-extraction-dofns-refined-layer) |
| Beam Timestamp (not datetime) | [03_storage](03_storage/INSTRUCTIONS.md#3-timestamp-handling-critical) |
| CDC UPSERT/DELETE | [04_processing](04_processing/INSTRUCTIONS.md#5-cdc-logic-upsertdelete) |
| Schema A/B/C detection | [02_ingestion](02_ingestion/INSTRUCTIONS.md#2-schema-detection--attach_event_name) |
| IcebergSink config chain | [03_storage](03_storage/INSTRUCTIONS.md#1-iceberg-write--blms-rest-catalog) |
| DoFn template | [04_processing](04_processing/INSTRUCTIONS.md#1-dofn-patterns) |
| deploy.py (BQ tables) | [03_storage](03_storage/INSTRUCTIONS.md#6-table-deployment-deploypy) |
| Kafka consumer setup | [02_ingestion](02_ingestion/INSTRUCTIONS.md#1-kafka-streaming-ingestion-members-collector) |

---

## Document Map

```
doc/
├── README.md                    ← You are here (Master Index)
├── 01_architecture/
│   ├── INSTRUCTIONS.md          Platform overview, layers, hexagonal arch
│   └── REFERENCE.md             Cross-cloud architecture patterns
├── 02_ingestion/
│   ├── INSTRUCTIONS.md          Kafka, API batch, PostgreSQL, init load
│   └── REFERENCE.md             Streaming services comparison
├── 03_storage/
│   ├── INSTRUCTIONS.md          Iceberg (BLMS), BQ (Storage Write API), schemas
│   └── REFERENCE.md             Warehouse/lakehouse comparison
├── 04_processing/
│   ├── INSTRUCTIONS.md          Beam DoFns, transforms, CDC, fan-out
│   └── REFERENCE.md             Processing engine comparison
├── 05_serving/
│   ├── INSTRUCTIONS.md          Dataform views, public layer, BI
│   └── REFERENCE.md             BI tools comparison
├── 06_governance/
│   ├── INSTRUCTIONS.md          DLQ, data quality, naming, access control
│   └── REFERENCE.md             Governance comparison
├── 07_cicd/
│   ├── INSTRUCTIONS.md          GitLab CI, Terraform, deploy scripts
│   └── REFERENCE.md             CI/CD patterns comparison
├── 08_development/
│   ├── INSTRUCTIONS.md          Repo structure, config, testing, code quality
│   └── REFERENCE.md             Tool comparison
├── 09_operations/
│   ├── INSTRUCTIONS.md          Troubleshooting, monitoring, alerting
│   └── REFERENCE.md             Observability patterns
├── 10_security/
│   ├── INSTRUCTIONS.md          Service accounts, IAM, secrets, VPC
│   └── REFERENCE.md             Cloud security comparison
├── projects/                    Per-project documentation
│   ├── loyalty-data/
│   ├── sales-data/
│   ├── common-data/
│   ├── insight/
│   └── partner-data/
└── archive/                     Old structure (preserved for reference)
    ├── knowledge_base/
    └── data_platform/
```
