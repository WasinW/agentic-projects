# Insight Domain -- Knowledge Base

## Overview

insight-api contains 4 data pipelines across 3 generations (V1/V3).
Data pipelines live under `insight/insight-api/data/`.
This KB covers all 4 pipelines with detailed architecture.

## Key Paths

```
insight/insight-api/
├── data/
│   ├── customer-profile-pipeline/    # V3 Streaming (Hexagonal) -- ORIGINAL
│   ├── customer-profile-collector/   # V3 Streaming (Hexagonal + Pydantic) -- MODERNIZED FORK
│   ├── last-purchases-collector/     # V1 Streaming (simple CDC)
│   └── customer-svoc-interim/        # V1 Batch (BQ SQL -> GCS Parquet)
├── infrastructure/
│   ├── data-pipeline/                # Terraform (BQ, Composer, Buckets, DTS, Dataplex, Pub/Sub)
│   ├── last-purchases-collector/     # Terraform (main.tf, dataform.tf, schemas/)
│   └── customer-svoc-interim/        # Terraform (main.tf, dts.tf, schemas/)
└── pipeline/data/
    ├── ms-personas.gitlab-ci.yml                      # V1/V2 CI/CD (874 lines)
    └── customer-profile-data-pipeline.gitlab-ci.yml   # V3 CI/CD (318 lines)
```

## Pipeline Generations Summary

| Gen | Pipeline | Beam | Python | Pattern | Mode |
|-----|----------|------|--------|---------|------|
| V3 | customer-profile-pipeline | 2.69.0 | 3.11+ | Hexagonal (Ports+Adapters) | Streaming |
| V3 | customer-profile-collector | 2.71.0 | 3.12 | Hexagonal + Pydantic config | Streaming |
| V1 | last-purchases-collector | 2.71.0 | 3.12 | Simple 3-step pipeline | Streaming |
| V1 | customer-svoc-interim | 2.71.0 | 3.12 | BQ Read -> GCS Parquet | Batch |

---

## 1. customer-profile-pipeline (V3 Streaming -- ORIGINAL)

**Path:** `insight/insight-api/data/customer-profile-pipeline/`
**Version:** 3.0.0 | Beam 2.69.0 | Python >=3.11,<3.13
**Dockerfile base:** `gcr.io/dataflow-templates-base/python311-template-launcher-base:latest`
**Config pattern:** Hardcoded `get_config(env)` dict in `config/settings.py`

### Solution Architecture

```
customer-profile-pipeline/
├── src/customer_profile/
│   ├── main.py              # Entry point: parse CLI -> PipelineBuilder
│   ├── pipeline.py          # (legacy, unused)
│   ├── config/
│   │   ├── logging.py       # configure_logging() with run_id
│   │   ├── options.py       # CustomOptions: --env, --debug_mode
│   │   └── settings.py      # get_config(env) -> dict (hardcoded per-env)
│   ├── domain/
│   │   ├── constants.py     # TZ_BANGKOK, SQL_FUNCTION_MAPPING, DATA_TYPE_CONVERTERS
│   │   ├── models.py        # TypedDicts: MappingValue, BigtableRow, CdcRow, DlqRecord, etc.
│   │   ├── schemas.py       # build_cdc_schema() -- wraps record_fields with row_mutation_info
│   │   └── transformers.py  # 600+ lines, 20+ pure funcs (get_nested_value, mapping transforms)
│   ├── ports/
│   │   ├── input_ports.py   # Protocol: SecretProvider, MappingProvider, BigtableReader
│   │   ��── output_ports.py  # Protocol: ParquetWriter, IcebergSyncer, SchemaProvider
│   ├── adapters/
│   │   ├── input/
│   │   │   ├── bigquery_mapping.py  # BigQueryMappingFetcher (fetches mapping_reconcile)
│   │   │   ├── bigtable_reader.py   # BigtableRowFetcher (reads personas table)
│   │   │   ├── secret_manager.py    # SecretManagerAdapter (AWS creds for S3)
│   │   │   └── sql_loader.py        # SqlLoader (resources or GCS SQL loading)
│   │   └── output/
│   │       ├── bigquery_cdc.py      # get_bq_schema(), get_simple_bq_schema()
│   │       ├── s3_parquet.py        # S3ParquetWriter (GCS -> S3 copy)
│   │       ├── iceberg_writer.py    # Manual Iceberg writer (1000+ lines, currently commented out)
│   │       └── iceberg_sync.py      # MERGE ms_personas -> ms_personas_iceberg
│   ├── pipeline/
│   │   ├── builder.py       # PipelineBuilder: 14-step streaming pipeline
│   │   └── dofns.py         # 17 DoFn classes
│   ├── core/
│   │   └── logging_utils.py # RateLimitedLogger (prevents log flooding in streaming)
│   └── resources/sql/streaming/
│       ├── mapping_reconcile.sql
│       ├── ms_personas_export_s3.sql
│       ├── ms_personas_iceberg_merge.sql
│       ├── ms_personas_consents_history.sql
│       ├── ms_personas_consents_internal_partner.sql
│       ├── ms_personas_consents_external_partner.sql
│       └── ms_personas_suppression.sql
├── tests/
│   ├── unit/ (domain, pipeline, adapters, core)
│   └── integration/ (consent_processing)
├── pyproject.toml
└── Dockerfile
```

### 17 DoFn Classes (dofns.py)

| DoFn | Purpose |
|------|---------|
| MappingRefreshDoFn | Periodic BQ mapping_reconcile refresh (300s) |
| ExtractPersonasDoFn | Extract personaId from Pub/Sub JSON |
| FetchFromBigtableDoFn | Fetch row from Bigtable by personaId (5 column families) |
| FilterEmptyPKDoFn | Filter records with empty primary key |
| FilterEmptyFamilyDoFn | Filter records missing specific column family |
| TransformSchemasDoFn | Apply mapping transforms -> tagged output (gcp/aws) |
| FullfillSchemasDoFn | Fill default values for missing schema fields |
| WriteToBigLakeDoFn | Prepare consents for BigQuery/Iceberg write |
| MapToCdcTableRowDoFn | Wrap record in CDC envelope (row_mutation_info + record) |
| ExtractWindowPathDoFn | Extract window partition path for S3 |
| WritePartitionToParquetDoFn | Write Parquet partitions |
| WriteRecordToGCSDoFn | Write individual records to GCS |
| CompactAndCopyToS3DoFn | Compact GCS files and copy to S3 |
| SyncToIcebergDoFn | MERGE ms_personas -> ms_personas_iceberg (periodic) |
| SQLSubmitDoFn | Execute SQL in BQ (consent loading) |
| SQLExportDoFn | BQ EXPORT DATA to GCS (hourly) |
| CopyGCSToS3DoFn | Copy GCS files to S3 (boto3 + Secret Manager) |

### Data Flow (14-step streaming pipeline)

```
STEP 2:  Pub/Sub subscription -> ReadPubSub (bytes)
STEP 3:  ExtractPersonasDoFn -> {personaId: str}
STEP 4:  FetchFromBigtableDoFn -> Bigtable row (5 families: profiles, consents, members, reach, status)
STEP 5:  FilterEmptyPKDoFn -> FilterEmptyFamilyDoFn (split: profiles vs consents)
STEP 6:  TransformSchemasDoFn("ms_member") -> tagged output (gcp, aws)
STEP 7:  TransformSchemasDoFn("events_consents") -> tagged output (gcp, aws)
STEP 8:  MapToCdcTableRowDoFn -> WriteToBigQuery CDC (ms_personas, Storage Write API, primary_key=member_id)
         DLQ -> WriteToBigQuery (data_pipeline_dlq)
STEP 9:  WriteToBigLakeDoFn -> WriteToBigQuery (events_consents, Storage Write API)
         (Iceberg approach commented out -- waiting for GCS solution clarity)
STEP 10: PeriodicImpulse(1hr) -> SQLExportDoFn (BQ EXPORT DATA -> GCS) -> CopyGCSToS3DoFn (ms_personas -> S3)
STEP 11: PeriodicImpulse(300s) -> SyncToIcebergDoFn (MERGE ms_personas -> ms_personas_iceberg)
STEP 12-14: Consent processing (if enabled):
         PeriodicImpulse(300s) -> SQLSubmitDoFn x4 (consents_history, internal_partner, external_partner, suppression)
         PeriodicImpulse(1hr) -> SQLExportDoFn -> CopyGCSToS3DoFn (consent history + suppression -> S3)
```

### Mapping-Driven Transformation

The core transformation is driven by a BQ mapping table (`mapping_reconcile`):
- **3 mapping types**: path (dot-notation extraction from Bigtable), logic (SQL function), constant (fixed value)
- **Dual output**: GCP target (BQ CDC) and AWS target (S3 Parquet) via tagged outputs
- **Periodic refresh**: TransformSchemasDoFn refreshes mapping every 300s from BQ
- **Type conversion**: DATA_TYPE_CONVERTERS handles STRING, INT64, FLOAT64, DATE, TIMESTAMP, DATETIME, BOOLEAN

### CDC Format

```python
{
    "row_mutation_info": {
        "mutation_type": "UPSERT",           # or "DELETE"
        "change_sequence_number": "<timestamp>"
    },
    "record": {
        "memberId": "...",
        "accountId": "...",
        # ... 90+ fields
    }
}
```
- Storage Write API with `use_cdc_writes=True`
- Primary key: `member_id`
- Temporal types (DATE, TIMESTAMP, DATETIME) converted to STRING in CDC schema
- Java 17 required for BigQuery CDC expansion service

### Key Design Patterns

- **Hexagonal Architecture**: domain (pure logic) -> ports (Protocol interfaces) -> adapters (I/O)
- **Self-contained DoFns**: All adapter/domain imports INSIDE setup()/process() for Dataflow serialization
- **Rate-limited logging**: RateLimitedLogger prevents log flooding in streaming
- **SQL dual-source**: Load SQL from package resources (Docker) or GCS bucket (dynamic)
- **DLQ pattern**: Failed records tagged to separate BQ table with error info

---

## 2. customer-profile-collector (V3 Streaming -- MODERNIZED FORK)

**Path:** `insight/insight-api/data/customer-profile-collector/`
**Version:** 3.0.0 | Beam 2.71.0 | Python ==3.12.*
**Config pattern:** Pydantic-validated YAML (`DataflowConfigDto` + `PipelineConfig` frozen dataclass)

### What Changed from customer-profile-pipeline

| Aspect | customer-profile-pipeline (original) | customer-profile-collector (modernized) |
|--------|--------------------------------------|----------------------------------------|
| Beam | 2.69.0 | 2.71.0 |
| Python | >=3.11,<3.13 | ==3.12.* |
| Config | `get_config(env)` hardcoded dict | Pydantic `DataflowConfigDto` + YAML files |
| Config CLI | `--env stg/uat/prod` | `--dataflow_config` (base64 YAML) + `--env` fallback |
| Config validation | None (raw dict) | Pydantic `model_config = ConfigDict(extra="forbid")` |
| Pandas | >=1.5.0,<2.1.0 | >=2.1.0,<2.3.0 |
| Dev tools | pytest, ruff | pytest, ruff, mypy (strict=false), pre-commit, poethepoet, uv-secure |
| Dockerfile | Single-stage, system pip install | Multi-stage (uv builder + pre-built base) |
| Package structure | `src/customer_profile/` only | `src/` (new) + `src/customer_profile/` (copy) -- dual for gradual migration |

### Dual Package Structure

```
customer-profile-collector/src/
├── main.py                          # NEW: uses ConfigurationAdapter
├── domain/
│   ├── pipeline_config.py           # NEW: frozen dataclass PipelineConfig (94 fields)
│   ├── constants.py, models.py, schemas.py, transformers.py  # COPY from pipeline
│   ��── bq_transformers.py           # NEW: (extra BQ transform logic)
├── adapters/input/configuration/    # NEW: Pydantic config layer
│   ├── configuration_adapter.py     # ConfigurationAdapter: YAML merge + Pydantic validate
│   ├── settings.py                  # 12 Pydantic models (DataflowConfigDto root)
│   ├── secret_adapter.py            # Secret Manager adapter
│   └── logging_adapter.py           # Logging adapter with run_id
├── adapters/ (input/output)         # COPY from pipeline (bigquery_mapping, bigtable_reader, etc.)
├── application/pipeline/            # NEW: builder.py, dofns.py (using PipelineConfig)
├── customer_profile/                # COPY: full hexagonal structure from pipeline
│   ├── config/, domain/, ports/, adapters/, pipeline/, core/, resources/
│   └── main.py, pipeline.py
└── resources/sql/streaming/         # COPY from pipeline
```

### Configuration Flow

```
CLI --dataflow_config (base64 YAML) or --env
  -> ConfigurationAdapter.load()
    -> _load_yaml(base.yaml) + _deep_merge(env.yaml)
    -> DataflowConfigDto(**merged)  -- Pydantic validation (extra="forbid")
    -> _build_pipeline_config(dto)  -- resolve templates (project, GCS paths)
    -> PipelineConfig (frozen dataclass, 94 fields)
      -> to_legacy_config_dict()    -- backward compat for builder.py
```

### Pydantic Config Models (settings.py)

12 Pydantic models validate YAML structure:
`PipelineInfoConfig`, `PubSubConfig`, `BigtableConfig`, `BqConfig`, `S3Config`,
`MappingConfig`, `ParquetConfig`, `SyncConfig`, `IcebergConfig`, `ConsentSqlConfig`,
`ConsentGcsOutboundConfig`, `ConsentS3Config`, `ConsentConfig`, `TablesConfig`,
`DataflowConfigDto` (root, `extra="forbid"`)

### 15 DoFn Classes (application/pipeline/dofns.py)

Same as customer-profile-pipeline minus `WriteRecordToGCSDoFn` and `CompactAndCopyToS3DoFn` (S3 export simplified).

### Data Flow

Identical to customer-profile-pipeline. Builder uses `config.to_legacy_config_dict()` for backward compatibility with the same pipeline steps.

---

## 3. last-purchases-collector (V1 Streaming)

**Path:** `insight/insight-api/data/last-purchases-collector/`
**Version:** 1.0.0 | Beam 2.71.0 | Python >=3.12,<3.13
**Config pattern:** Pydantic `DataflowConfigDto` + base64 YAML
**Dockerfile:** Multi-stage (uv builder + pre-built base with Java 17)

### Solution Architecture

```
last-purchases-collector/
├── src/
│   ├── main.py
│   ├── domain/
│   │   ├── models.py           # BigtableRow, LastPurchasesRow (TypedDicts)
│   │   ├── transformers.py     # get_nested_value(), extract_persona_id(), get_family()
│   │   └── bq_transformers.py  # BRANDS list, to_last_purchases_row(), LAST_PURCHASES_SCHEMA
│   ├── adapters/
│   │   ├── input/configuration/
│   │   │   ├── configuration_adapter.py  # PipelineConfig (frozen dataclass, 8 fields)
│   │   │   └── settings.py               # DataflowCliOptions, StreamingConfig, DataflowConfigDto
│   │   └── output/
│   │       ├── bigquery_sink.py     # BigQuerySink PTransform (append/cdc/batch modes)
│   │       ├── bigquery_storage.py  # write_to_bigquery_append/cdc/batch + _WrapCdcRowDoFn
│   │       └── bigquery_cdc.py      # get_bq_schema() -- fetch schema at startup
│   └── application/pipeline/
│       ├── builder.py   # PipelineBuilder: 4-step streaming pipeline
│       └── dofns.py     # ParsePayloadDoFn, TransformDoFn
├── dataform/
│   └── definitions/
│       ├── refined/last_purchases/personas_last_purchases.sqlx  # Source declaration
│       └���─ public/last_purchases/personas_last_purchases.sqlx   # Public semantic view
├── config/ (base.yaml, stg.yaml, prod.yaml)
├── flex-template-spec.json
├── Dockerfile, Dockerfile.base
└── tests/
```

### Data Flow (4-step streaming pipeline)

```
STEP 1: Pub/Sub subscription -> ReadPubSub (bytes)
STEP 2: ParsePayloadDoFn -> unwrap JSON/Avro payload, detect unknown brands
STEP 3: TransformDoFn -> to_last_purchases_row() -> flat wide-table BQ row
STEP 4: BigQuerySink(write_mode="cdc", primary_key=["personas_id"]) -> BQ CDC UPSERT
```

### Brand Schema (19 brands x 2 fields = 38 brand columns + 2 meta)

**Brands:** B2S, CDS, CFM, CFR, CFW, CGT, CMG, CRC, HCD, HWS, MJT, OFM, PNM, PWB, RBS, SSP, TOC, TWD, TWT

**BQ Table:** `personas_last_purchases` (insight dataset)
**Columns:** `personas_id` (PK, STRING), `etl_load_timestamp` (TIMESTAMP), then per brand:
- `{brand_lower}_last_purchase_time` (TIMESTAMP) -- epoch ms converted to ISO
- `{brand_lower}_last_purchase_store_code` (STRING)

Total: 40 columns (2 meta + 19*2 brand columns)

### Input Payload Structure (Avro from Pub/Sub)

```json
{
    "personaId": "...",
    "profiles": {"memberId": "..."},
    "purchases": {
        "B2S": {"lastPurchasedTime": 1609459200000, "lastPurchasedStoreCode": "..."},
        "CDS": {"lastPurchasedTime": 1709000000000, "lastPurchasedStoreCode": null},
        ...
    }
}
```

### Avro Union Handling

ParsePayloadDoFn and bq_transformers both use `_unwrap_avro()`:
- Detects Avro union format `{"string": "value"}` (dict with single key)
- Unwraps to raw value

### BigQuerySink (Reusable PTransform)

```python
BigQuerySink(
    table=config.bq_table,
    schema=LAST_PURCHASES_SCHEMA,
    write_mode="cdc",              # -> write_to_bigquery_cdc()
    primary_key=["personas_id"],
    triggering_frequency=5,        # seconds
)
```

CDC wrapping done by `_WrapCdcRowDoFn`:
- Sanitizes Beam Timestamp -> ISO string
- Wraps in `{row_mutation_info: {mutation_type, change_sequence_number}, record: {...}}`
- Supports `_is_delete` flag for DELETE mutations

### Dataform Integration

- `definitions/refined/` -> source declaration (insight.personas_last_purchases)
- `definitions/public/` -> semantic view (public.personas_last_purchases) with all 40 columns

### Configuration (PipelineConfig)

```python
@dataclass(frozen=True)
class PipelineConfig:
    project: str
    pubsub_subscription: str
    bq_table: str                   # "project.dataset.personas_last_purchases"
    bq_dataset: str
    log_level: str
    triggering_frequency: int       # default 5
    num_storage_api_streams: int    # default 2
    use_at_least_once: bool         # default True
```

---

## 4. customer-svoc-interim (V1 Batch)

**Path:** `insight/insight-api/data/customer-svoc-interim/`
**Version:** 1.0.0 | Beam 2.71.0 | Python >=3.12,<3.13
**Config pattern:** Pydantic `DataflowConfigDto` + base64 YAML + `--par_month`
**Dockerfile:** Multi-stage (uv builder + pre-built base)

### Solution Architecture

```
customer-svoc-interim/
├── src/
│   ├── main.py
│   ├── adapters/input/configuration/
│   │   ├── configuration_adapter.py  # PipelineConfig (frozen dataclass, 7 fields)
│   │   └── settings.py               # DataflowCliOptions, ExportConfig, DataflowConfigDto
│   ├── application/pipeline/
│   │   └── builder.py   # PipelineBuilder: 3-step batch pipeline
│   └── resources/sql/
│       └── export_svoc.sql  # 305 lines, ~280 SELECT columns
├── config/ (base.yaml, stg.yaml, prod.yaml)
├── flex-template-spec.json
└── Dockerfile
```

### Why Batch, Not Streaming

This pipeline replaces a previous streaming approach that caused OOM after 9 hours.
The solution uses BQ `ReadFromBigQuery` (SQL query) -> GCS Parquet write -- a simple 3-step batch pipeline
that runs on-demand via Airflow DAG.

### Data Flow (3-step batch pipeline)

```
STEP 1: ReadFromBigQuery(query=export_sql, use_standard_sql=True)
STEP 2: CastToString -> {k: str(v) if v is not None else None}
STEP 3: WriteToParquet(num_shards=15, snappy compression)
```

### Source Table

`refined.full_customer_svoc_ingt` -- BQ table populated by DTS (S3 Parquet -> BQ)
- DTS source: `s3://t1-analytics/analysis/the1_support/full_customer_svoc/par_month={YYYYMM}/**`
- DTS config: PARQUET format, WRITE_TRUNCATE, 0 bad records allowed
- ~280 columns, ALL STRING type

### Export SQL

`src/resources/sql/export_svoc.sql` (305 lines):
- ~280 `column_name AS alias_name` selects (currently 1:1, future: rename)
- Categories: life_stage, kids, visit patterns, payment, spending, brand rankings, brand shares of wallet
- `{project_id}` placeholder substituted at runtime
- All values cast to STRING in pipeline step 2

### Dynamic Parquet Schema

`_build_parquet_schema_from_sql(sql)` parses `AS alias_name` patterns from SQL:
- Extracts all column aliases via regex
- Creates pyarrow schema with ALL STRING fields
- No hardcoded schema file needed -- schema derived from SQL

### Output

GCS Parquet files:
- Path: `gs://{project}-data-pipeline-data-staging/export/svoc/{par_month}/svoc`
- Format: Parquet with snappy compression
- Shards: configurable (default 15)
- Suffix: `.parquet`

### Configuration (PipelineConfig)

```python
@dataclass(frozen=True)
class PipelineConfig:
    project: str
    par_month: str                  # YYYYMM (required, from CLI or YAML)
    source_table: str               # "refined.full_customer_svoc_ingt"
    gcs_export_path: str            # "gs://...data-staging/export/svoc"
    num_export_files: int           # default 15
    sql_file: str                   # "export_svoc.sql"
    log_level: str                  # default "INFO"
```

### Terraform: DTS from S3

`infrastructure/customer-svoc-interim/dts.tf`:
- `google_bigquery_data_transfer_config.svoc_transfer`
- Source: `s3://t1-analytics/analysis/the1_support/full_customer_svoc/par_month={var.svoc_par_month}/**`
- Destination: `refined.full_customer_svoc_ingt`
- AWS creds from Secret Manager (`insight-data-pipeline`)
- `null_resource.trigger_svoc_transfer` runs the transfer immediately after apply

---

## Cross-Cutting Patterns

### Configuration Pattern Comparison

| Pipeline | Config Style | CLI | Validation |
|----------|-------------|-----|------------|
| customer-profile-pipeline | `get_config(env)` hardcoded dict | `--env stg/uat/prod` | None |
| customer-profile-collector | YAML + Pydantic DTO -> frozen dataclass | `--dataflow_config` (base64) | Pydantic `extra="forbid"` |
| last-purchases-collector | YAML + Pydantic DTO -> frozen dataclass | `--dataflow_config` (base64) | Pydantic `extra="allow"` |
| customer-svoc-interim | YAML + Pydantic DTO -> frozen dataclass | `--dataflow_config` + `--par_month` | Pydantic + model_validator |

### Dockerfile Pattern Comparison

| Pipeline | Base Image | Build | Java | S3 |
|----------|-----------|-------|------|----|
| customer-profile-pipeline | python311-template-launcher-base | Single-stage, system pip | openjdk-17 (apt) | boto3 in system Python |
| customer-profile-collector | Pre-built BASE_IMAGE | Multi-stage (uv builder) | temurin-17 (in base) | boto3 in venv |
| last-purchases-collector | Pre-built BASE_IMAGE | Multi-stage (uv builder) | temurin-17 (in base) | Not needed |
| customer-svoc-interim | Pre-built BASE_IMAGE | Multi-stage (uv builder) | temurin-17 (in base) | Not needed |

### BigQuery Write Pattern Comparison

| Pipeline | Method | Mode | Primary Key | Triggering |
|----------|--------|------|-------------|------------|
| customer-profile-pipeline | WriteToBigQuery direct | CDC (use_cdc_writes) | member_id | 5s, 2 streams |
| customer-profile-collector | WriteToBigQuery direct | CDC (use_cdc_writes) | member_id | 5s, 2 streams |
| last-purchases-collector | BigQuerySink PTransform | CDC (auto-wrap) | personas_id | 5s, auto-sharding |
| customer-svoc-interim | WriteToParquet (no BQ write) | N/A (GCS only) | N/A | N/A |

### Shared Reusable Components

**BigQuerySink** (last-purchases-collector) -- composite PTransform:
- 3 modes: append, cdc, batch
- CDC auto-wraps via `_WrapCdcRowDoFn` (no manual CDC envelope needed)
- Supports `_is_delete` flag for CDC DELETE
- TIMESTAMP/DATETIME -> STRING conversion for CDC compatibility
- Reusable across any pipeline

**ConfigurationAdapter pattern** (collector + last-purchases + svoc):
- base64-encoded YAML via `--dataflow_config`
- Pydantic validation with `DataflowConfigDto`
- Frozen dataclass `PipelineConfig` output

---

## Infrastructure

### Bigtable

- **Instance:** `t1-insight-bt`
- **Table:** `personas`
- **5 Column Families:** profiles, consents, members, reach, status
- Used by: customer-profile-pipeline, customer-profile-collector

### BigQuery Tables

| Table | Dataset | Type | Pipeline |
|-------|---------|------|----------|
| ms_personas | insight | CDC (100+ cols, member_id PK, timestamp partition) | customer-profile-* |
| ms_personas_iceberg | insight | External Iceberg (MERGE target) | customer-profile-* |
| events_consents | insight | Managed Iceberg / Storage Write | customer-profile-* |
| data_pipeline_dlq | insight | Native (DLQ) | customer-profile-* |
| mapping_reconcile | insight | Native (DTS from S3, hourly refresh) | customer-profile-* |
| ms_member | insight | Native (DTS from S3, daily 6AM) | customer-profile-* |
| ms_personas_consents_history | data_refined | Native | customer-profile-* |
| ms_personas_consents_history_s3 | data_refined | Native | customer-profile-* |
| ms_personas_consents_internal_partner | data_refined | Native | customer-profile-* |
| ms_personas_consents_external_partner | data_refined | Native | customer-profile-* |
| ms_personas_suppression | data_refined | Native | customer-profile-* |
| personas_last_purchases | insight | CDC (40 cols, personas_id PK) | last-purchases-collector |
| full_customer_svoc_ingt | refined | Native (DTS landing, ~280 cols) | customer-svoc-interim |

### S3 Export Paths

- ms_personas: `s3://t1-analytics/refined/insights/ms_personas_{env}/`
- Consents history: `s3://t1-analytics/refined/insights/ms_personas_consents_history_{env}/`
- Suppression: `s3://t1-analytics/refined/insights/ms_personas_suppression_{env}/`
- SVOC source: `s3://t1-analytics/analysis/the1_support/full_customer_svoc/par_month={YYYYMM}/`

### Secrets

- **insight-data-pipeline**: AWS credentials (aws-access-key, aws-secret-key) for S3 access + DTS

### GAR (Artifact Registry)

- `asia-southeast1-docker.pkg.dev/{PROJECT_ID}/insight-datapipeline-dataflow-common/`
- Images: `last-purchases-collector:{TAG}`, `customer-svoc-interim:{TAG}`

### Terraform State

| Pipeline | Prefix |
|----------|--------|
| data-pipeline (main) | `the1-insight/services/personas/ms-personas` |
| last-purchases-collector | `the1-insight/services/data-pipeline/last-purchases-collector` |
| customer-svoc-interim | `the1-insight/services/data-pipeline/customer-svoc-interim` |

All use bucket `devops-terraformstate-nonprod`, provider `hashicorp/google >= 5.0`, region `asia-southeast1`.

### Environments

- **Projects:** `the1-insight-stg`, `the1-insight-uat`, `the1-insight-prod`
- **SA:** `t1-ins-{env}-sa-data@the1-insight-{env}.iam.gserviceaccount.com`

---

## CI/CD

### ms-personas.gitlab-ci.yml (V1/V2 -- 874 lines)

For V1/V2 pipelines (processor/dataflow):
- Build: sec scan + test + build wheel
- Deploy: terraform plan/apply + deploy-tables + create-image (Kaniko) + upload wheel + scripts + setup composer vars
- Uploads wheel + DAGs + scripts + configs to Composer GCS bucket
- 9 Airflow variables

### customer-profile-data-pipeline.gitlab-ci.yml (V3 -- 318 lines)

For customer-profile-pipeline + customer-profile-collector:
- Build: sec scan + test
- Deploy: build image (Kaniko) + upload Flex Template spec + DAG
- Flex Template pattern: `gs://{composer_bucket}/template/customer-profile-pipeline/spec.json`
- 2 Airflow variables (flex_template_bucket, workspace_env)

### Flex Template Pattern (shared by V1 collectors)

All 3 newer pipelines use Flex Templates:
- Image built via multi-stage Dockerfile (uv builder + pre-built base)
- `flex-template-spec.json` specifies image, parameters, SDK language
- Launched via Airflow DAG or `gcloud dataflow flex-template run`

---

## Airflow DAGs (10 DAGs)

1. `dag_customer_profile_batch_initial.py` -- One-time batch load (8 workers, n1-standard-8)
2. `dag_customer_profile_v3.py` -- V3 Streaming via Flex Template
3. `dag_customer_profile_realtime_v2_test.py` -- V2 Streaming (config-driven)
4. `dag_customer_profile_realtime.py` -- V1 Streaming (original)
5. `dag_customer_profile_batch_test.py` -- V2 Batch
6. `dag_trigger_dts.py` -- Trigger BQ Data Transfer Service
7. `dag_customer_profile_clear_job.py` -- Cancel/Drain Dataflow jobs
8. `clear_bucket.py` -- Delete GCS contents
9. `copy_gcs_to_s3.py` -- GCS->S3 copy utility
10. `simple_bigquery_query_dag.py` -- Ad-hoc BQ queries

---

## Dependencies (CRITICAL -- Tested Compatible Sets)

### customer-profile-pipeline (V3 original)

```
apache-beam[gcp]==2.69.0
numpy>=1.21,<2                    # CRITICAL for pyarrow
pyarrow>=14.0.0,<18.0.0
pandas>=1.5.0,<2.1.0
fastavro>=1.9.0
boto3==1.34.106                   # EXACT -- S3 dep chain
botocore==1.34.106
aiobotocore==2.13.0
s3fs==2024.6.1
fsspec==2024.6.1
google-cloud-bigquery>=3.25.0
google-cloud-bigtable>=2.26.0
google-cloud-secret-manager>=2.20.0
pyiceberg[gcsfs]>=0.7.0
```

### customer-profile-collector (V3 modernized)

```
apache-beam[gcp]==2.71.0
pydantic>=2.12.5                  # NEW: config validation
pandas>=2.1.0,<2.3.0             # UPGRADED from <2.1.0
mypy>=1.19.1                     # NEW: dev tool
poethepoet>=0.40.0               # NEW: task runner
pre-commit>=4.5.1                # NEW: git hooks
uv-secure>=0.7.0                 # NEW: security scanning
```
(rest same as pipeline)

### last-purchases-collector (V1)

```
apache-beam[gcp]==2.71.0
pydantic>=2.0.0
numpy>=1.21,<2
pyarrow>=14.0.0,<18.0.0
google-cloud-bigquery>=3.25.0
google-cloud-bigtable>=2.26.0    # (in deps but not used by pipeline)
google-cloud-secret-manager>=2.20.0
```
NO boto3/s3fs/pandas -- no S3 export

### customer-svoc-interim (V1)

```
apache-beam[gcp]==2.71.0
pydantic>=2.0.0
numpy>=1.21,<2
pyarrow>=14.0.0,<18.0.0
google-cloud-bigquery>=3.25.0
```
MINIMAL deps -- BQ read + GCS Parquet write only

---

## Gotchas

- `use_public_ips=True` REQUIRED for S3 access (customer-profile-*)
- `sdkContainerImage` must include boto3 for S3 pipelines
- `numpy<2` CRITICAL for pyarrow compiled with numpy 1.x
- S3 dep chain (s3fs->aiobotocore->botocore) has EXACT version requirements
- `RUN_PYTHON_SDK_IN_DEFAULT_ENVIRONMENT=1` for S3 boto3 in Dockerfile (pipeline only)
- Java 17 required for BigQuery CDC expansion service
- Avro union unwrapping needed for last-purchases-collector Pub/Sub messages
- SVOC export: all 280+ columns are STRING (source DTS landing table is all-string)
- customer-profile-collector has `to_legacy_config_dict()` bridge for gradual migration
- Pydantic `extra="forbid"` in collector catches unknown YAML keys early
