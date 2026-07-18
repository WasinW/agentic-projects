# Loyalty Data Project

> **GCP Project:** `the1-loyalty-data-{env}` (env: stg, prod)
> **Repository:** `gitlab.com/The1central/The1/the1-data/loyalty-data`
> **Team:** Data Platform (section 2.1.1)
> **Region:** asia-southeast1
> **Last Updated:** 2026-02-20

---

## Table of Contents

1. [Overview](#1-overview)
2. [Collectors](#2-collectors)
3. [Architecture](#3-architecture)
4. [Infrastructure](#4-infrastructure)
5. [Configuration System](#5-configuration-system)
6. [Iceberg Write Path](#6-iceberg-write-path)
7. [BigQuery Write Path](#7-bigquery-write-path)
8. [Option B Migration](#8-option-b-migration)
9. [CI/CD Pipeline](#9-cicd-pipeline)
10. [Key Patterns](#10-key-patterns)
11. [Known Issues and Pending Items](#11-known-issues-and-pending-items)
12. [Key File Paths](#12-key-file-paths)

---

## 1. Overview

Loyalty Data is a data ingestion platform that collects loyalty program data from multiple sources (Kafka, REST APIs, PostgreSQL) and writes to both Apache Iceberg tables (source/raw layer) and BigQuery tables (refined layer).

### Data Flow

```
STREAMING: Kafka --> members-collector (job_type=normal)  --> Iceberg + BQ
           Kafka --> purchases-collector                  --> Iceberg + BQ
           Kafka --> transactions-collector                --> Iceberg + BQ

BATCH:     Cloud Scheduler (1AM BKK) --> tiers-collector            --> Iceberg + BQ
           Cloud Scheduler (1AM BKK) --> members-tiers-history      --> Iceberg + BQ
           Cloud Scheduler (1AM BKK) --> rewards-collector           --> GCS Parquet (via Cloud Run)

INIT:      GitLab CI (TRIGGER_INIT_DATA_LOAD=1) --> job_type=initial_data --> Iceberg + BQ
```

---

## 2. Collectors

### 2.1 members-collector (Our code - Section 2.1.1)

| Property | Value |
|----------|-------|
| Type | Streaming |
| Source | Kafka topics: `loyalty.members.upgraded`, `loyalty.members.downgraded` |
| Sink (Raw) | Iceberg: `tier_events_upgraded`, `tier_events_downgraded`, `member_tier`, `member_tier_maintenance` |
| Sink (Refined) | BigQuery: `member_tier` (CDC in prod), `tier_maintenance`, `tier_events_upgraded` (optional), `tier_events_downgraded` (optional) |
| Secret | `members-collector` (Kafka + OAuth2) |
| Python | 3.12 |
| Beam | 2.70.0 |
| Deployment | Dataflow Flex Template |

**Features:**
- Streaming mode with windowed writes
- Fetches member tier and maintenance data from Loyalty API after receiving Kafka events
- CDC write mode for `member_tier` table in production (primary key: memberTierId)
- Initial data load mode via `job_type=initial_data`
- BQ Metadata Refresh (Option B) prepared but disabled

### 2.2 tiers-collector (Our code - Section 2.1.1)

| Property | Value |
|----------|-------|
| Type | Batch |
| Source | Loyalty Tiers Master API |
| Sink (Raw) | Iceberg: `raw_tiers_master` |
| Sink (Refined) | BigQuery: `tiers_master` |
| Trigger | Cloud Scheduler: `tiers-collector-daily-trigger` (1 AM Asia/Bangkok) |
| Secret | `tiers-collector` |

### 2.3 members-tiers-history-collector (Our code - Section 2.1.1)

| Property | Value |
|----------|-------|
| Type | Batch |
| Source | PostgreSQL database (via SSH tunnel) |
| Sink (Raw) | Iceberg: `members_tiers_history` |
| Sink (Refined) | BigQuery: `members_tiers_history` |
| Trigger | Cloud Scheduler: `members-tiers-history-daily-trigger` (1 AM Asia/Bangkok) |
| Secret | `members-tiers-history-collector` (PostgreSQL + SSH) |
| Note | Uses `process_date` parameter (yesterday) for incremental loads |

### 2.4 purchases-collector (Reference - read-only)

| Property | Value |
|----------|-------|
| Type | Streaming |
| Source | Kafka (purchase events) |
| Sink | Iceberg + BigQuery |
| Note | Reference implementation; used as pattern basis for other collectors |

### 2.5 transactions-collector (NOT ours - coordinate with other team)

| Property | Value |
|----------|-------|
| Type | Streaming |
| Source | Kafka (transaction earned events) |
| Sink | Iceberg + BigQuery |
| Note | Managed by another team; coordinate before making changes |

### 2.6 rewards-collector

| Property | Value |
|----------|-------|
| Type | Batch (scheduled) |
| Source | Rewards API |
| Sink | GCS Parquet files (via PyIceberg) |
| Deployment | Cloud Run (FastAPI + uvicorn) |
| Trigger | Cloud Scheduler: `rewards-collector-scheduler` (1 AM daily) |
| Library | `common-data-python-cloudrun` |

---

## 3. Architecture

### Hexagonal Architecture

All collectors follow the hexagonal (ports and adapters) architecture pattern:

```
src/
+-- main.py                          # Entry point
+-- domain/
|   +-- models.py                    # Domain models (dataclasses)
|   +-- schemas.py                   # Beam/Iceberg/BQ schemas
|   +-- transformers.py              # Pure transform functions
|   +-- blms_catalog_config.py       # BLMS REST Catalog configuration
|   +-- managed_iceberg_write_config.py  # Managed IcebergIO write config
|   +-- pipeline_config.py           # Aggregated pipeline config
+-- adapters/
|   +-- input/
|   |   +-- configuration/           # YAML config loading + Pydantic validation
|   |   +-- kafka/                   # Kafka reader adapter (uses common library)
|   +-- output/
|       +-- iceberg_writer.py        # write_to_iceberg(config=ManagedIcebergWriteConfig, ...)
|       +-- iceberg_sink.py          # IcebergSink(config, schema, row_mapper)
|       +-- bigquery_sink.py         # BigQuery Storage Write API
|       +-- bigquery_storage.py      # BQ writer configuration
|       +-- bq_metadata_refresh.py   # Option B BQ refresh (DISABLED)
|       +-- pyiceberg_writer.py      # Legacy manual Iceberg writer
+-- application/
    +-- pipeline/
        +-- builder.py               # Pipeline construction (members-collector)
```

### Domain Models

- `BlmsCatalogConfig` - Frozen dataclass for BigLake REST catalog connection
- `ManagedIcebergWriteConfig` - Frozen dataclass for Managed IcebergIO write settings

### Write Path

```
YAML Config --> Settings (Pydantic) --> ConfigAdapter --> BlmsCatalogConfig
                                                     --> ManagedIcebergWriteConfig
                                                     --> IcebergSink --> managed.Write
```

---

## 4. Infrastructure

### Terraform Resources per Collector

Each collector has its own infrastructure directory: `infrastructure/{collector}/`

| Resource | File | Description |
|----------|------|-------------|
| Artifact Registry | `artifact.tf` | GAR Docker repository |
| GCS Bucket | `bucket.tf` | Per-collector bucket (staging/temp/templates) |
| BigLake IAM | `biglake-metastore.tf` | IAM: source + refined dataset access |
| Secret Manager | `secret-manager.tf` | Service secret |
| Container Spec | `templates/container_spec.json` | Flex Template specification |
| Schema Files | `schemas/deploy.py` | BQ table creation/registration |
| Variables | `variables.tf`, `terraform.tfvars` | Terraform variables |
| Cloud Scheduler | `scheduler.tf` | Batch job triggers (tiers, m-t-h only) |
| DTS | `dts.tf` | Data Transfer Service (members, m-t-h only - for init migration) |

### Common Infrastructure (`infrastructure/common/GCP/`)

| Resource | File | Description |
|----------|------|-------------|
| BigLake Catalog | `biglake-metastore.tf` | Shared Iceberg catalog + IAM for all collectors |
| GCS Buckets | `buckets.tf` | Shared source/refined/public buckets |
| Service Accounts | `service-accounts.tf` | SA definitions (mostly commented - SAs managed elsewhere) |
| Secret Manager | `secret-manager.tf` | Common secrets |

### AWS Infrastructure (`infrastructure/common/AWS/`)

Legacy cross-cloud resources: ECR, EKS, Route53, Secret Manager.

---

## 5. Configuration System

### YAML Config Files

Each collector has: `config/base.yaml`, `config/stg.yaml`, `config/prod.yaml`

**Merge strategy:** Environment config overrides base config. Deep merge for nested keys (iceberg, refined, etc.).

### Configuration Flow

```
base.yaml + {env}.yaml --> Pydantic Settings --> PipelineConfig --> Pipeline
```

### Key Config Sections (members-collector example)

```yaml
secret_name: "members-collector"

kafka:
  topics: ["loyalty.members.upgraded", "loyalty.members.downgraded"]
  group_id: "loyalty-sem-members"
  window_size_seconds: 60
  message_format: "auto"

iceberg:
  writer: "managed_io"
  blms_rest_uri_prefix: "https://biglake.googleapis.com/iceberg/v1/restcatalog"
  blms_namespace: "source"
  triggering_frequency_secs: 60

refined:
  member_tier:
    enable: true
    partition_field: "etlLoadTime"
    write_mode: "append"     # prod overrides to "cdc"

bq_refresh:
  enabled: false             # Option B disabled

log_level: "ERROR"
```

### Environment Overrides

| Setting | STG | PROD |
|---------|-----|------|
| `refined.member_tier.write_mode` | `append` | `cdc` |
| `refined.*.write_mode` (other tables) | `append` | `append` |
| Kafka bootstrap servers | STG cluster | PROD cluster |
| GCS buckets | `*-stg` | `*-prod` |

---

## 6. Iceberg Write Path

### BLMS REST Catalog (Active)

All three section 2.1.1 collectors use BigLake Managed Storage (BLMS) REST Catalog:

```python
BlmsCatalogConfig:
    catalog_type: "rest"
    rest_uri: "https://biglake.googleapis.com/iceberg/v1/restcatalog"
    warehouse_path: "gs://the1-loyalty-data-source-{env}"
    credential_mode: "vended-credentials"  # GoogleAuthManager
```

### Managed IcebergIO (Beam Cross-Language)

```python
ManagedIcebergWriteConfig:
    table: "{namespace}.{table_name}"           # e.g., "source.member_tier"
    table_location: "gs://{bucket}/{namespace}/{table}"
    triggering_frequency_seconds: 60
    table_properties: { "location": "gs://..." }
```

### Hadoop Catalog (Preserved as Comments)

Hadoop catalog configuration is preserved in comments in each `blms_catalog_config.py` and `managed_iceberg_write_config.py`. Search for `"Hadoop Catalog"` to find rollback points.

### Iceberg Table Properties

- Partition: `identity(etlLoadTime)` where `etlLoadTime` is INT64 YYYYMMDDHH format
- The `register_table` approach (not `create_table`) preserves field IDs and partition specs

---

## 7. BigQuery Write Path

### BigQuery Storage Write API

All collectors use the Beam BigQuery Storage Write API (`WriteToBigQuery` with `STORAGE_WRITE_API` method).

**Critical requirement:** MUST use `apache_beam.utils.timestamp.Timestamp` -- NOT `datetime.datetime`. The BQ Storage Write API RowCoder uses `MicrosInstant` which calls `value.micros`.

### Write Modes

| Mode | Use Case | PROD Tables |
|------|----------|-------------|
| `WRITE_APPEND` | Append-only tables | tier_maintenance, tier_events_*, tiers_master, members_tiers_history |
| CDC (UPSERT) | Dedup by primary key | member_tier (pk: memberTierId) |

### Schema Deployment (`deploy.py`)

Each collector's `infrastructure/{collector}/schemas/deploy.py` handles:
1. `register_table` -- Register Iceberg tables in BigLake catalog (preserves field IDs)
2. Create/update BigQuery refined tables with correct schemas

Currently `GOOGLE_AUTH_AVAILABLE = False` in deploy.py (Option B creation disabled).

---

## 8. Option B Migration

### Terminology

**"Option B" has two separate parts:**

1. **Write via Option B (BLMS REST Catalog)** -- ACTIVE. All three collectors write to Iceberg via BLMS REST Catalog with vended credentials. This is identical to the messaging-collector pattern.

2. **BQ Table Creation via Option B** -- DISABLED. Uses `externalCatalogTableOptions` + `tables.patch` to auto-refresh BQ external tables linked to Iceberg. Waiting for terraform dataset with `externalCatalogDatasetOptions` (needs coordination with transaction/ team).

### Current State

| Component | Status | Location |
|-----------|--------|----------|
| BLMS REST Catalog write | ACTIVE | `blms_catalog_config.py` x3 |
| Managed IcebergIO write | ACTIVE | `managed_iceberg_write_config.py` x3 |
| BQ Metadata Refresh module | EXISTS (disabled) | `bq_metadata_refresh.py` x3 |
| PeriodicImpulse (members) | COMMENTED OUT | `builder.py` |
| BQ refresh post-hook (tiers, m-t-h) | COMMENTED OUT | `main.py` |
| deploy.py Option B creation | COMMENTED OUT | `deploy.py` x3 |
| base.yaml bq_refresh.enabled | `false` | `config/base.yaml` (members) |

### Re-enable Steps

1. `base.yaml` (members): `bq_refresh.enabled: true`
2. `builder.py` (members): Uncomment PeriodicImpulse block
3. `main.py` (tiers + m-t-h): Uncomment BQ refresh post-hook
4. `deploy.py` x3: Uncomment google.auth imports + Option B call sites
5. Coordinate with transaction/ team: `external_catalog_dataset_options` + IAM

---

## 9. CI/CD Pipeline

### GitLab CI Stages

1. **sonar-scan** -- Code quality (shared `.common-sonar-scan` extends)
2. **gitleaks** -- Secret scanning (shared extends)
3. **trivy** -- Container vulnerability scanning (shared extends)
4. **create-image** -- Docker build (4 destinations: STG active + PROD active)
5. **terraform:plan** -- Plan for stg and prod
6. **terraform:apply** -- Apply for stg and prod
7. **deploy-tables** -- Schema deployment via deploy.py
8. **deploy** -- Dataflow job launch

### Image Build

Multi-stage Docker:
- **Stage 1 (Builder):** `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` -- dependency resolution
- **Stage 2 (Runtime):** `gcr.io/dataflow-templates-base/python312-template-launcher-base` -- Dataflow Flex Template
- Java 17 JRE for Kafka cross-language transforms

### Deployment Scripts

Located at `scripts/`:
- `prepare_dataflow_config.sh` -- Merge YAML configs, base64 encode
- `prepare_dataflow_spec.sh` -- Generate Flex Template spec JSON
- `deploy_dataflow.sh` -- Launch Dataflow job via API

### Deploy Behavior

| Collector | Deploy Type | Pre-deploy Action |
|-----------|------------|-------------------|
| members-collector | Streaming | Cancel existing job (should upgrade to drain-first) |
| tiers-collector | Batch | No pre-deploy (new job each run) |
| members-tiers-history | Batch | No pre-deploy (new job each run) |

---

## 10. Key Patterns

### Bangkok Timezone (+7)

ALL timestamps must use Bangkok timezone offset. This is critical for data consistency.

**Source Layer (Iceberg):**
```python
_BANGKOK_TZ = timezone(timedelta(hours=7))
etl_load_time = int(datetime.now(_BANGKOK_TZ).strftime("%Y%m%d%H"))  # INT YYYYMMDDHH
```

**Refined Layer (BigQuery):**
```python
_BANGKOK_OFFSET_SECONDS = 7 * 3600
_BANGKOK_OFFSET_MICROS = _BANGKOK_OFFSET_SECONDS * 1_000_000

# Current time with Bangkok offset
etlLoadTime = Timestamp(micros=Timestamp.now().micros + _BANGKOK_OFFSET_MICROS)

# Date/time column conversion
timestamp_val = Timestamp(seconds=unix_ts + _BANGKOK_OFFSET_SECONDS)
```

**CDC path** (members): `.to_utc_datetime()` preserves +7 because offset is baked into Timestamp micros.

### etlLoadTime Pattern

- Type: INT64 (format: YYYYMMDDHH)
- Partition: `identity(etlLoadTime)` in Iceberg
- Used for both source and refined layers

### Avro Unwrapping

Kafka messages from Confluent use Avro with union types. The `message_format: "auto"` setting handles automatic detection and unwrapping of Avro payloads from Confluent Schema Registry.

### Job Types

- `job_type=normal` -- Streaming mode (Kafka consumer)
- `job_type=initial_data` -- Batch mode (historical data load via GitLab CI trigger)

---

## 11. Known Issues and Pending Items

### Pending

- **STG-to-PROD dependency chain** -- Add `needs: deploy:stg` to deploy:prod
- **Members drain-first** -- Upgrade from cancel to drain-then-cancel (like purchases)
- **BQ backup before deploy-tables:prod** -- Prevent data loss on schema changes
- **DLQ implementation** -- Research done (`docs/dlq/DLQ_RESEARCH.md`), not implemented
- **Dataplex setup** -- Enable API, create Lake/Zone
- **Option B BQ table creation** -- Waiting for terraform dataset coordination

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| OOM on GitLab Runner | Processing too much data locally | Use Dataflow batch (`job_type=initial_data`) |
| Ruff RUF043 (regex) | Non-raw regex string | Use raw string: `match=r"kafka\.topics"` |
| pre-commit purchases-collector fail | pyarrow 17.0.0 + Python 3.13 | Known issue, ignore |
| ClassCastException: String to Long | Schema mismatch in IcebergIO | Ensure etlLoadTime is INT64, not STRING |
| AttributeError: datetime has no 'micros' | Using datetime instead of Beam Timestamp | Use `apache_beam.utils.timestamp.Timestamp` |

---

## 12. Key File Paths

### Source Code (relative to loyalty-data/)

```
members-collector/
+-- src/main.py
+-- src/domain/blms_catalog_config.py
+-- src/domain/managed_iceberg_write_config.py
+-- src/domain/models.py
+-- src/domain/schemas.py
+-- src/domain/transformers.py
+-- src/domain/pipeline_config.py
+-- src/adapters/input/configuration/
+-- src/adapters/output/iceberg_writer.py
+-- src/adapters/output/iceberg_sink.py
+-- src/adapters/output/bigquery_sink.py
+-- src/adapters/output/bq_metadata_refresh.py
+-- src/application/pipeline/builder.py
+-- config/base.yaml
+-- config/stg.yaml
+-- config/prod.yaml

tiers-collector/                          # Same structure as members
members-tiers-history-collector/          # Same structure as members
```

### Infrastructure (relative to loyalty-data/)

```
infrastructure/
+-- common/GCP/
|   +-- biglake-metastore.tf              # Shared BigLake catalog + IAM
|   +-- buckets.tf                        # Shared source/refined/public buckets
|   +-- service-accounts.tf
|   +-- secret-manager.tf
+-- members/
|   +-- artifact.tf                       # GAR repo
|   +-- bucket.tf                         # Per-collector GCS bucket
|   +-- biglake-metastore.tf              # Per-collector BigLake IAM
|   +-- secret-manager.tf
|   +-- schemas/deploy.py                 # BQ table deployment
|   +-- templates/container_spec.json     # Flex Template spec
+-- tiers/
|   +-- scheduler.tf                      # Cloud Scheduler (1 AM BKK)
|   +-- (same pattern as members)
+-- members-tiers-history/
|   +-- scheduler.tf                      # Cloud Scheduler (1 AM BKK)
|   +-- (same pattern as members)
+-- purchases/                            # Reference
+-- transaction/                          # NOT ours
+-- rewards-collector/
    +-- cloud-run.tf                      # Cloud Run deployment
    +-- artifact.tf
    +-- secret-manager.tf
```

### Scripts (shared)

```
scripts/
+-- deploy_dataflow.sh
+-- prepare_dataflow_config.sh
+-- prepare_dataflow_spec.sh
```

### Documentation

```
docs/
+-- README.md                             # Master index
+-- option-b-migration/OPTION_B_SUMMARY.md
+-- dlq/DLQ_RESEARCH.md
+-- architecture/CICD_COMPARISON_AND_PROD_SAFETY.md
```
