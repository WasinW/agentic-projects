# The1 Data Platform - Overall Enterprise Architecture

## 1. Platform Context

The1 Data Platform is being migrated from AWS to GCP. The legacy platform on AWS houses the existing data marts, analytics, and SVOC (Single View of Customer). The new GCP platform follows a domain-driven design with clear separation between data domains, app domains, and data marts.

### Migration Strategy
- **Phase 1 (Current)**: Build new data domain pipelines on GCP (Dataflow, Iceberg, BigQuery)
- **Phase 2 (Current)**: Interim solutions — DTS from AWS S3 to GCP for data not yet natively produced on GCP (e.g., SVOC)
- **Phase 3 (Future)**: Build native SVOC and analytics on GCP, deprecate AWS pipelines

---

## 2. Architecture Layers

```
+------------------------------------------------------------------+
|                        Consumptions                               |
|   THE1 | CDS/RBS | TWD | B2S | CFR | OFM | PWB | SSP | ...     |
+------------------------------------------------------------------+
|  The1 Portal      |    The1 BI       |     The1 Datahub          |
+------------------------------------------------------------------+
|                     Data Governance                               |
| Catalog | Lineage | Profiling | Observability | Quality | Access |
+------------------------------------------------------------------+

+-----------+  +-------------+  +---------------+  +--------------+
|  Source   |  |  The1 Core  |  |   The1 Data   |  | Data Product |
|           |  |  (App)      |  |   (Domain)    |  |  (Mart)      |
| Call Ctr  |  | PROFILE     |  | GAMIFICATION  |  | ENGAGEMENT   |
| The1 App  |  | IDENTITY    |  | DISCOVERY(SA) |  | CUSTOMER     |
| BU eCom   |  | GAMIFICATION|  | COMMERCE      |  | SALES        |
| Geofence  |  | DISCOVERY   |  | MESSAGING     |  | MARTECH      |
|           |  | COMMERCE    |  | LOYALTY       |  | LOYALTY      |
| Sales Txn |  | MESSAGING   |  | SALES         |  |              |
| ALL BU POS|  | LOYALTY     |  | CATALOG       |  | AI/ML:       |
|           |  | SALES COLL. |  | ACCOUNTING    |  | FOUNDRY      |
| Other src |  | CATALOG     |  | PARTNER       |  | RISK         |
| GCS/TICC  |  | ACCOUNTING  |  | EXTERNAL      |  | TARGET       |
| Insurance |  | PARTNER     |  |               |  |              |
| CC Partner|  |             |  |               |  |              |
| BU Excel  |  | * INSIGHT   |  |               |  |              |
+-----------+  +-------------+  +---------------+  +--------------+

Data Flow: Raw --> Structure --> Refined --> Semantic
```

---

## 3. Domain Projects

### 3.1 Data Domains (GCP Projects)

Each data domain has its own GCP project (`the1-{domain}-data-{env}`) and GitLab repository. They follow the collector pattern: Source -> Dataflow/Cloud Run -> Iceberg (source) -> BigQuery (refined).

| Domain | GCP Project | Collectors | Source Type |
|--------|-------------|------------|-------------|
| **Loyalty** | `the1-loyalty-data-{env}` | tiers, members, members-tiers-history, purchases, rewards, transactions, coupons | Kafka, API |
| **Sales** | `the1-sales-data-{env}` | sales-collector | Kafka |
| **Catalog** | `the1-catalog-data-{env}` | products-collector | DTS (S3), API |
| **Gamification** | `the1-gamification-data-{env}` | account-missions, master | API |
| **Messaging** | `the1-messaging-data-{env}` | master, messages, communications, templates | Kafka, API |
| **Partner** | `the1-partner-data-{env}` | master, companies, branches | API |

### 3.2 App Domain with Data Pipelines (Exception)

| Domain | GCP Project | Pipelines | Note |
|--------|-------------|-----------|------|
| **Insight** | `the1-insight-{env}` | customer-profile-pipeline, last-purchases-collector, **customer-svoc-interim** | App domain ที่มี data pipeline อยู่ด้วย (legacy design) |

Insight is an **app domain** (contains APIs, Collector service, Personas service, etc.) but also hosts data pipelines. This is a legacy architecture decision that is unlikely to change.

### 3.3 Data Mart Projects

| Mart | GCP Project | Engine | Status |
|------|-------------|--------|--------|
| **Loyalty Insights** | `the1-loyalty-data-{env}` (shared) | Dataform | Infrastructure ready, SQL definitions in progress |
| **Future Marts** | TBD | Dataform | ENGAGEMENT, CUSTOMER, SALES, MARTECH per diagram |
| **AI/ML** | TBD | TBD | FOUNDRY, RISK, TARGET |

### 3.4 Shared/Common

| Project | Purpose |
|---------|---------|
| **common-data** | Shared Python libraries: Kafka reader, BigQuery writer, Iceberg writer, CI templates |

---

## 4. Standard Collector Architecture

All data domain collectors follow hexagonal architecture:

```
config/
  base.yaml, stg.yaml, prod.yaml
src/
  main.py                          # Composition root
  adapters/
    input/
      configuration/               # YAML + Pydantic -> PipelineConfig
    output/
      bigquery_sink.py             # BQ Storage Write API (CDC)
      iceberg_sink.py              # IcebergIO via BLMS REST
  application/
    pipeline/
      builder.py                   # Beam pipeline definition
      dofns.py                     # DoFn implementations
  domain/
    models.py, schemas.py          # Pure domain logic
infrastructure/
  {collector}/
    schemas/*.json                 # BQ table definitions
    templates/container_spec.json  # Flex template spec
    *.tf                           # Terraform (IAM, buckets, etc.)
Dockerfile, Dockerfile.base
pyproject.toml, uv.lock
```

### Technology Stack
- **Processing**: Apache Beam 2.70+ on Google Cloud Dataflow
- **Storage**: Iceberg (BLMS REST Catalog) + BigQuery (CDC via Storage Write API)
- **Config**: YAML (base64-encoded) -> Pydantic -> frozen dataclass
- **Tooling**: uv, ruff, mypy, pytest, pre-commit
- **CI/CD**: GitLab CI, Kaniko (container builds), Terraform
- **Orchestration**: Cloud Composer (Airflow)

---

## 5. Data Flow Patterns

### 5.1 Streaming (Real-time)
```
Kafka/Pub/Sub -> Dataflow (Beam) -> Iceberg (source) -> BigQuery (refined)
```
Examples: members-collector, messages-collector, customer-profile-pipeline

### 5.2 Batch (Scheduled)
```
Cloud Scheduler -> Dataflow (Beam) -> Iceberg (source) -> BigQuery (refined)
```
Examples: tiers-collector, members-tiers-history-collector

### 5.3 DTS Ingest (S3 -> BQ)
```
AWS S3 (Parquet) -> BigQuery DTS -> refined table -> view (public/semantic)
```
Examples: mapping data, member data, **SVOC interim**

### 5.4 Export (BQ -> GCS)
```
BigQuery (refined) -> Dataflow (Beam SQL) -> GCS (Parquet files)
```
Examples: consent export, **SVOC export to GCS**

### 5.5 Mart (Analytics)
```
BigQuery (refined) -> Dataform (SQL) -> BigQuery (public/semantic)
```
Examples: loyalty-insights earn-analysis

---

## 6. GCP Project Topology

```
the1-insight-{env}              # App domain + data pipelines
the1-loyalty-data-{env}         # Loyalty domain + loyalty-insights mart
the1-sales-data-{env}           # Sales domain
the1-catalog-data-{env}         # Catalog domain
the1-gamification-data-{env}    # Gamification domain
the1-messaging-data-{env}       # Messaging domain
the1-partner-data-{env}         # Partner domain
```

---

## 7. Key Infrastructure Components

| Component | Service | Usage |
|-----------|---------|-------|
| **Compute** | Dataflow, Cloud Run | Pipeline execution |
| **Storage** | BigQuery, GCS, Iceberg | Data warehouse + lake |
| **Messaging** | Kafka, Pub/Sub | Event streaming |
| **Cache** | Bigtable | Real-time lookups |
| **Secrets** | Secret Manager | Credentials, API keys |
| **Registry** | Artifact Registry | Docker images |
| **Catalog** | BigLake Metastore | Iceberg table catalog |
| **Orchestration** | Cloud Composer (Airflow) | DAG scheduling |
| **Transfer** | BigQuery DTS | S3 -> BQ batch ingestion |
| **IaC** | Terraform | All infrastructure |
| **CI/CD** | GitLab CI | Build, test, deploy |
