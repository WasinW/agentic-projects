# Architecture Instructions

> AI: Read this file to understand platform overview, data flow, GCP project structure, and domain boundaries.

## Quick Reference

```
Platform: GCP-based, domain-driven, multi-project
Domains: Loyalty (6 collectors), Sales (1 collector), Insight (pipeline + APIs)
Architecture: Hexagonal (Ports & Adapters) per collector

Data Flow:
  Sources (Kafka/API/PostgreSQL) → Dataflow (Beam) → Iceberg (GCS) → BigQuery → Consumers

Storage Layers:
  Source (Iceberg on GCS via BLMS REST Catalog)
  → Refined (BigQuery, Storage Write API)
  → Public/Curated (BigQuery views, Dataform)
```

---

## 1. GCP Project Organization

| Domain | STG Project | PROD Project |
|--------|-------------|--------------|
| Loyalty Data | `the1-loyalty-data-stg` | `the1-loyalty-data-prod` |
| Sales Data | `the1-sales-data-stg` | `the1-sales-data-prod` |
| Insight | `the1-insight-stg` | `the1-insight-prod` |
| Monitoring | `the1-monitoring-stg` | `the1-monitoring-prod` |

**Key principle**: Each domain has its own GCP project, service accounts, IAM, and infrastructure. No cross-domain resource sharing except via authorized views.

---

## 2. Collectors by Domain

### Loyalty (our focus)

| Collector | Type | Source | Iceberg Tables | BQ Tables | Trigger |
|-----------|------|--------|---------------|-----------|---------|
| **members-collector** | Streaming | Kafka (2 topics) | 4 | 4 | Continuous |
| **tiers-collector** | Batch | REST API | 1 | 1 | Cloud Scheduler 1AM BKK |
| **members-tiers-history** | Batch | PostgreSQL (SSH) | 1 | 1 | Cloud Scheduler 1AM BKK |
| **transactions-collector** | Streaming | Kafka (3 topics) | 1+ | 3+ | Continuous |
| **purchases-collector** | Streaming | Kafka (2 topics) | 1 | 3 + Pub/Sub | Continuous |
| **rewards-collector** | Batch | REST API | 0 | GCS Parquet | Cloud Scheduler |

**Ownership rules:**
- **Our code** (2.1.1): members-collector, tiers-collector, members-tiers-history
- **Reference only**: purchases-collector (read-only)
- **NOT ours**: transactions-collector (coordinate with other team)
- **DEPRECATED**: member-tiers

### Sales

| Collector | Type | Source | BQ Tables | Trigger |
|-----------|------|--------|-----------|---------|
| **sales-collector** | Streaming | Kafka (1 topic) | 3 (receipt, sku, tender) | Continuous |

### Insight

| Component | Runtime | Language | Purpose |
|-----------|---------|----------|---------|
| Customer Profile Pipeline | Dataflow | Python/Beam | Pub/Sub → BQ CDC + S3 + Iceberg |
| Personas API | GKE | Kotlin | Bigtable + Redis serving |
| Audiences API | GKE | Kotlin | BQ + ClickHouse serving |
| Collector | Cloud Run | Node.js | Event collection |

---

## 3. Data Architecture Layers

| Layer | Storage | Format | Purpose |
|-------|---------|--------|---------|
| **Source** | GCS | Apache Iceberg (Parquet + metadata) | Immutable RAW event archive |
| **Refined** | BigQuery | Native BQ (Storage Write API) | Cleaned, partitioned, analytics-ready |
| **Public/Curated** | BigQuery | Views + materialized tables | Business-ready golden datasets |
| **Export** | AWS S3 | Parquet | Cross-cloud sharing (Insight only) |

### Source Layer (Iceberg)

```
gs://the1-loyalty-data-source-{env}/
└── source/                          # BigLake namespace
    ├── member_tier/                  # Iceberg table
    │   ├── metadata/                # JSON + Avro manifests
    │   └── data/                    # Parquet data files
    ├── member_tier_maintenance/
    ├── tier_events_upgraded/
    ├── tier_events_downgraded/
    ├── tiers/
    └── members_tiers_history/
```

### Refined Layer (BigQuery)

```
BigQuery (the1-loyalty-data-{env}):
├── source/                          # BigLake external tables (Iceberg)
├── refined/                         # Transformed analytics tables
│   ├── member_tier                  # CDC in PROD, append in STG
│   ├── member_tier_maintenance      # CDC by tierMaintenanceId
│   ├── tier_events_upgraded
│   ├── tier_events_downgraded
│   ├── tiers_master
│   └── members_tiers_history
└── public/                          # Views, golden datasets
```

---

## 4. Pipeline Modes

```
STREAMING: Kafka → collector (job_type=normal) → Iceberg + BQ (continuous)
BATCH:     Cloud Scheduler (1AM BKK) → collector → Iceberg + BQ (self-terminating)
INIT:      GitLab CI (TRIGGER_INIT_DATA_LOAD=1) → job_type=initial_data → Iceberg + BQ
```

---

## 5. Hexagonal Architecture

ALL Python Dataflow pipelines follow hexagonal architecture:

```
{collector}/src/
├── main.py                    # Composition Root — wire everything here
├── domain/                    # PURE LOGIC — no I/O, no Beam imports
│   ├── models.py              # @dataclass(frozen=True) domain objects
│   ├── schemas.py             # Schema definitions
│   ├── transformers.py        # Pure transform functions
│   ├── blms_catalog_config.py # BLMS REST config
│   ├── managed_iceberg_write_config.py
│   └── pipeline_config.py     # Runtime config
├── adapters/                  # I/O — Kafka, BQ, Iceberg, config
│   ├── input/configuration/   # YAML loading + Pydantic Settings
│   └── output/                # Iceberg writer, BQ sink
└── application/pipeline/      # Pipeline builder (Beam DAG)
    ├── builder.py             # PipelineBuilder
    ├── dofns.py               # DoFn implementations
    └── transform_dofns.py     # Payload extraction DoFns
```

### Layer Import Rules

| Layer | CAN import | MUST NOT import |
|-------|-----------|-----------------|
| **domain/** | Python stdlib only | `apache_beam`, `google.cloud`, adapters, application |
| **adapters/** | domain/ | application/ |
| **application/** | domain/, adapters/ | — |
| **main.py** | everything | — |

### Composition Root Pattern

`main.py` is the only place where concrete adapters are instantiated. The PipelineBuilder receives pre-configured PTransforms via dependency injection:

```python
# main.py
config = ConfigurationAdapter().load()
blms_config = BlmsCatalogConfig(...)
iceberg_sink = IcebergSink(config=..., schema=..., row_mapper=...)
bq_sink = BigQuerySink(table=..., schema=..., write_mode=...)

builder = PipelineBuilder(
    options=pipeline_options,
    config=config,
    iceberg_sink=iceberg_sink,
    bq_sink=bq_sink,
)
builder.build_and_run()
```

---

## 6. Technology Stack

| Category | Technology | Use |
|----------|-----------|-----|
| Compute | Google Cloud Dataflow | Beam pipelines (streaming + batch) |
| Compute | Cloud Run | Batch jobs (rewards), event collection |
| Source Layer | Apache Iceberg + GCS | Lakehouse (Parquet + metadata) |
| Catalog | BigLake Metastore (BLMS) | Iceberg REST Catalog |
| Warehouse | BigQuery | Refined + public layers |
| Messaging | Confluent Kafka (SASL/SSL) | Event streaming |
| Messaging | Google Pub/Sub | GCP-native events (Insight) |
| Secrets | GCP Secret Manager | Kafka/API credentials |
| IaC | Terraform | Infrastructure provisioning |
| CI/CD | GitLab CI + Kaniko | Build, test, deploy |
| Dependencies | uv | Python dependency management |
| Language | Python 3.12 + Apache Beam | Pipeline code |

---

## 7. Infrastructure Pattern

### Per-Collector

```
infrastructure/{collector}/
├── artifact.tf                # GAR repository
├── bucket.tf                  # GCS bucket
├── biglake-metastore.tf       # BigLake catalog IAM
├── secret-manager.tf          # Secrets (manual populate)
├── schemas/
│   ├── deploy.py              # BQ table deployer
│   └── refined_*.json         # BQ table schemas
└── templates/
    └── container_spec.json    # Flex Template spec
```

### Common (Shared)

```
infrastructure/common/GCP/
├── biglake-metastore.tf       # BigLake catalog creation
├── source-bucket.tf           # Shared source GCS bucket
└── service-account.tf         # SA IAM
```

---

## 8. Naming Conventions

| Resource | Pattern | Example |
|----------|---------|---------|
| GCP Project | `the1-{domain}-{env}` | `the1-loyalty-data-prod` |
| GCS Bucket (source) | `the1-{domain}-source-{env}` | `the1-loyalty-data-source-prod` |
| Service Account | `t1-{collector}@{project}.iam` | `t1-members-collector@the1-loyalty-data-prod.iam` |
| GAR Repository | `{collector}` in project GAR | `members-collector` |
| Dataflow Job | `{collector}` | `members-collector` |
| Secret | `{collector}` | `members-collector` |
| BigLake Catalog | GCS bucket name | `the1-loyalty-data-source-prod` |
| Iceberg namespace | `source` | `source` |
| Iceberg table | snake_case entity | `member_tier` |
| BQ dataset | `source`, `refined`, `public` | `refined` |
| Kafka topic | `loyalty.{entity}.{event}` | `loyalty.members.upgraded` |

---

## 9. Network Topology

| Setting | Value |
|---------|-------|
| VPC | `the1-vpc-net-share-{env}` (Shared VPC) |
| Dataflow Subnet | `the1-subnet-dataflow-{env}` |
| Worker IP Mode | Private only (`WORKER_IP_PRIVATE`) |
| Kafka Connection | SASL/SSL over internet (Confluent Cloud) |
| GCP Service Access | Private Google Access |

---

## 10. Cross-Domain Data Flow

| From | To | Method |
|------|----|--------|
| Insight APIs | Loyalty BQ | Cross-project BQ reads |
| Insight Pipeline | AWS S3 | Direct S3 write (Parquet) |
| Monitoring | All projects | Metric/Log scoping |
| BI Tools | All BQ datasets | Authorized views |
