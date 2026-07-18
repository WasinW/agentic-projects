# Loyalty Data Platform - Complete Knowledge Base
**Updated: 2026-02-18 (Session 8) | Source: Full codebase re-exploration of all collectors + infra + docs**

## Table of Contents
1. [Architecture Overview](#1-architecture-overview)
2. [Members-Collector (Streaming)](#2-members-collector)
3. [Tiers-Collector (Batch)](#3-tiers-collector)
4. [Members-Tiers-History-Collector (Batch)](#4-members-tiers-history-collector)
5. [Purchases-Collector (Reference)](#5-purchases-collector-reference)
6. [Messages-Collector (Reference)](#6-messages-collector-reference)
7. [Infrastructure & Terraform](#7-infrastructure--terraform)
8. [Schema Catalog](#8-schema-catalog)
9. [Configuration Patterns](#9-configuration-patterns)
10. [Critical Technical Patterns](#10-critical-technical-patterns)
11. [Common Pitfalls & Fixes](#11-common-pitfalls--fixes)
12. [Current State & Pending Work](#12-current-state--pending-work)

---

## 1. Architecture Overview

### System Diagram
```
STREAMING:
  Kafka (upgraded/downgraded topics)
    -> members-collector (job_type=normal)
    -> Iceberg (source via BLMS REST) + BigQuery (refined)

BATCH (Scheduled):
  Cloud Scheduler (1AM BKK) -> tiers-collector -> API -> Iceberg + BQ
  Cloud Scheduler (1AM BKK) -> members-tiers-history -> PostgreSQL -> Iceberg + BQ

INIT DATA:
  GitLab CI (TRIGGER_INIT_DATA_LOAD=1)
    -> members-collector (job_type=initial_data)
    -> members-tiers-history (job_type=initial_data)
    -> BQ staging -> Iceberg + BQ refined

  DTS (S3 -> BQ loyalty dataset) -> init tables (temporary staging)
```

### Data Layers
| Layer | Storage | Dataset | Table Type | etlLoadTime | Catalog |
|-------|---------|---------|------------|-------------|---------|
| Source (Raw) | Iceberg on GCS | source | external_iceberg | STRING (YYYYMMDDHH) | BigLake REST |
| Refined | BigQuery | refined | native | TIMESTAMP (HOUR partition) | N/A |
| Init Staging | BigQuery | loyalty | native | varies | N/A |

### Collectors Overview
| Collector | Mode | Source | Sink | Schedule | Tables |
|-----------|------|--------|------|----------|--------|
| members-collector | Streaming + Batch | Kafka / BQ init | Iceberg + BQ | Always-on / Manual | 4 raw + 4 refined |
| tiers-collector | Batch | Loyalty API | Iceberg + BQ | 1AM daily (BKK) | 1 raw + 1 refined |
| members-tiers-history | Batch | PostgreSQL | Iceberg + BQ | 1AM daily (BKK) | 1 raw + 1 refined |
| purchases-collector (ref) | Streaming | Kafka | Iceberg + Pub/Sub + 3 BQ | Always-on | 1 raw + 3 refined |
| messages-collector (ref) | Streaming | Kafka | Iceberg + Pub/Sub + Bigtable + BQ | Always-on | 1 raw + 1 refined |

### Shared Domain Models (D-H IcebergIO Refactor)
All 3 collectors now use identical patterns:
```python
# domain/blms_catalog_config.py (frozen dataclass)
BlmsCatalogConfig(warehouse_path, namespace, rest_uri, project_id, region, catalog_name)

# domain/managed_iceberg_write_config.py (frozen dataclass)
ManagedIcebergWriteConfig(catalog: BlmsCatalogConfig, table_name, triggering_frequency_seconds)
  .get_full_table_identifier()  -> "namespace.table"
  .get_table_location()         -> "gs://catalog_name/table"
  .build_writer_config()        -> dict for managed.Write(ICEBERG, config=...)

# adapters/output/gcs/iceberg_writer.py
write_to_iceberg(config=ManagedIcebergWriteConfig, ...)

# adapters/output/gcs/iceberg_sink.py
IcebergSink(config, schema, row_mapper)  # 3 params, PTransform wrapper
```

---

## 2. Members-Collector

### Path: `loyalty/loyalty-data/members-collector/`

### Key Files
```
src/
├── main.py                                    # Entry point: DI composition root (227 lines)
├── domain/
│   ├── models.py                              # MemberTierPayload, RawEvent, IntermediateEvent
│   ├── schemas.py                             # PyArrow + BQ schemas (5 refined schemas, 339 lines)
│   ├── transformers.py                        # Pure functions: is_avro, parse, extract_value (142 lines)
│   ├── pipeline_config.py                     # PipelineConfig, KafkaReaderConfig, InitData (271 lines)
│   ├── blms_catalog_config.py                 # BlmsCatalogConfig (frozen dataclass) — BLMS REST
│   └── managed_iceberg_write_config.py        # ManagedIcebergWriteConfig (frozen dataclass)
├── adapters/
│   ├── input/
│   │   ├── kafka_consumer.py                  # build_consumer_config(), get_schema_registry_config()
│   │   ├── loyalty_api.py                     # LoyaltyAPIClient (OAuth2, get_member_info/tier/maintenance)
│   │   ├── avro_deserializer.py               # AvroMessageDeserializer (Schema Registry)
│   │   └── configuration/
│   │       ├── settings.py                    # JobType, MessageFormat, IcebergWriter enums + Pydantic (273 lines)
│   │       ├── configuration_adapter.py       # DataflowCliOptions, ConfigurationAdapter.load() (231 lines)
│   │       ├── logging_adapter.py             # LoggingAdapter with run_id
│   │       └── secret_adapter.py              # SecretAdapter (GCP Secret Manager)
│   └── output/
│       ├── gcs/
│       │   ├── iceberg_writer.py              # write_to_iceberg(config=ManagedIcebergWriteConfig) (300 lines)
│       │   ├── iceberg_sink.py                # IcebergSink PTransform wrappers (200 lines)
│       │   └── gcs_parquet.py                 # Parquet fallback writer
│       └── bigquery/
│           ├── bigquery_writer.py             # BigQueryWriterAdapter (append/CDC/batch) (163 lines)
│           ├── bigquery_writer_config.py       # BigQueryWriterConfig dataclass (46 lines)
│           └── bq_metadata_refresh.py         # Option B refresh (DISABLED, module kept)
└── application/pipeline/
    ├── builder.py                             # PipelineBuilder: streaming + init_data (608 lines)
    ├── dofns.py                               # ExtractValue, DecodeParse, AttachEventName, BuildRawEvent (146 lines)
    ├── avro_dofn.py                           # DecodeAvroOrJsonDoFn (auto-detect Avro/JSON) (164 lines)
    ├── transform_dofns.py                     # Extract*PayloadDoFn (5 variants for BQ refined) (562 lines)
    └── api_dofns.py                           # ExtractMemberId, FetchMember*, Deduplicate (445 lines)
```

### Pipeline Flow (Streaming - job_type=normal)
```
Per Kafka Topic (upgraded, downgraded):
  ReadFromKafka -> ExtractValue -> DecodeAvroOrJson
  -> Window(60s) -> AttachEventName -> BuildRawEvent
  -> Write Iceberg (topic-specific table: tier_events_upgraded/downgraded)
  -> Optional: ExtractTierEventPayload -> Write BQ refined

Merge all topics -> ExtractMemberId -> Deduplicate
  -> FetchMemberTier (API) -> Write Iceberg (member_tier) + BQ refined
  -> FetchTierMaintenance (API) -> Write Iceberg (member_tier_maintenance) + BQ refined
```

### Pipeline Flow (Batch - job_type=initial_data)
```
For each enabled source table:
  ReadFromBigQuery (with condition_parts) -> Write Iceberg batch (preserves etlLoadTime)

For each enabled refined table:
  ReadFromBigQuery (with condition_parts) -> Write BQ refined
```

### Iceberg Tables (4)
- `tier_events_upgraded` - Raw Kafka upgraded events
- `tier_events_downgraded` - Raw Kafka downgraded events
- `member_tier` - API member tier data (7 fields incl memberId)
- `member_tier_maintenance` - API tier maintenance data (7 fields incl memberId)

### BQ Refined Tables (4 schemas)
- `TIER_EVENT_UPGRADED_REFINED_SCHEMA` (12 fields, includes isExistingTier)
- `TIER_EVENT_DOWNGRADED_REFINED_SCHEMA` (11 fields, NO isExistingTier)
- `MEMBER_TIER_REFINED_SCHEMA` (13 fields, primary_key=memberId for CDC)
- `TIER_MAINTENANCE_REFINED_SCHEMA` (27 fields)

### BigQuery Write Modes
| Table | stg | prod |
|-------|-----|------|
| member_tier | append | **cdc** (upsert with PRIMARY KEY=memberId) |
| member_tier_maintenance | append | append |
| tier_events_upgraded | append | append |
| tier_events_downgraded | append | append |

### Key Iceberg Writer Functions (iceberg_writer.py)
- `_to_tier_event_row()` - TIER_EVENT_SCHEMA (6 fields), etlLoadTime=now
- `_to_member_info_row()` - MEMBER_INFO_SCHEMA (7 fields), etlLoadTime=now
- `_to_member_info_row_passthrough()` - Preserves etlLoadTime from source (batch init)
- `write_to_iceberg(config=ManagedIcebergWriteConfig, ...)` - Generic managed write
- `write_member_info_to_iceberg(...)` - Member info streaming
- `write_member_info_to_iceberg_batch(...)` - Member info batch

### API DoFns (api_dofns.py)
- `ExtractMemberIdDoFn` - Recursively searches payload for memberId
- `DeduplicateMemberIdsDoFn` - Set-based dedup per bundle
- `FetchMemberInfoDoFn` - `/loyalty/v2/members/{id}/tiers` -> source="loyalty-member-info-api"
- `FetchMemberTierDoFn` - Same endpoint -> source="loyalty-member-tier-api"
- `FetchTierMaintenanceDoFn` - `/loyalty/v2/members/{id}/tiers/events` -> explodes array

### Transform DoFns (transform_dofns.py) - ALL use Bangkok TZ +7h
- `ExtractMemberInfoPayloadDoFn` - Raw API -> accountId, memberId, tierEventId...
- `ExtractMemberTierPayloadDoFn` - API data[] -> per-item, ranking(int), timestamps(+7h)
- `ExtractTierMaintenancePayloadDoFn` - Event -> 27 fields, spending(float)
- `ExtractTierEventUpgradedPayloadDoFn` - Kafka -> 12 fields WITH isExistingTier
- `ExtractTierEventDowngradedPayloadDoFn` - Kafka -> 11 fields WITHOUT isExistingTier

### Init Data (prod.yaml)
- Source: member_tier (disabled), member_tier_maintenance (with condition_parts)
- condition_parts: date-range WHERE clauses for parallel BQ reads
- SQL files: `src/resources/init/load_member_tier_source.sql`, `load_member_tier_refined.sql`
- Init mode: max-workers=50, machine-type=n1-highmem-4

---

## 3. Tiers-Collector

### Path: `loyalty/loyalty-data/tiers-collector/`

### Key Files
```
src/
├── main.py                                    # Entry + DI composition root (85 lines)
├── domain/
│   ├── models.py                              # MemberTierPayload, RawEvent, IntermediateEvent
│   ├── schemas.py                             # TIERS_MASTER_RAW/REFINED schemas (241 lines)
│   ├── transformers.py                        # Pure functions (142 lines)
│   ├── pipeline_config.py                     # PipelineConfig (no Kafka, has API config) (76 lines)
│   ├── blms_catalog_config.py                 # BlmsCatalogConfig (frozen dataclass)
│   └── managed_iceberg_write_config.py        # ManagedIcebergWriteConfig (frozen dataclass)
├── adapters/
│   ├── input/
│   │   ├── loyalty_api.py                     # LoyaltyAPIClient with get_tiers() (256 lines)
│   │   └── configuration/
│   │       ├── settings.py                    # Pydantic DTOs (135 lines)
│   │       ├── configuration_adapter.py       # ConfigAdapter (156 lines)
│   │       ├── secret_adapter.py              # SecretAdapter (56 lines)
│   │       └── logging_adapter.py             # LoggingAdapter (63 lines)
│   └── output/
│       ├── gcs/
│       │   ├── iceberg_writer.py              # Managed I/O writer (241 lines)
│       │   ├── iceberg_sink.py                # IcebergSink PTransform (62 lines)
│       │   └── gcs_parquet.py                 # GCS Parquet fallback
│       └── bigquery/
│           ├── bigquery_writer.py             # BigQueryWriterAdapter (163 lines)
│           ├── bigquery_writer_config.py       # Config dataclass (46 lines)
│           └── bq_metadata_refresh.py         # Option B refresh (DISABLED)
└── application/pipeline/
    ├── builder.py                             # PipelineBuilder (126 lines)
    ├── api_dofns.py                           # FetchTiersDoFn (142 lines)
    └── transform_dofns.py                     # ExtractTiersMasterPayloadDoFn (187 lines)
```

### Pipeline Flow
```
Create([None]) -> FetchTiersDoFn (API /loyalty/v2/tiers)
  -> Yields 1 row per tier (flattened from programs[].tiers[])
  -> IcebergSink (write to source.tiers)
  -> If refined enabled: ExtractTiersMasterPayloadDoFn -> BigQueryWriterAdapter
```

### API Response Processing
- Calls `/loyalty/v2/tiers` -> returns `{ data: [{ program, tiers: [...] }] }`
- FetchTiersDoFn flattens: 1 RAW row per tier
- Each row: eventId(UUID), source("loyalty-tiers-master-api"), eventName, timestamp(unix INT), payload(JSON)

### Iceberg Schema (TIER_EVENT_SCHEMA)
```python
RowTypeConstraint: (eventId:str, source:str, eventName:str, timestamp:str, payload:str, etlLoadTime:str)
```

### Refined Schema (23 fields)
- Metadata: eventId, source, eventName, timestamp(TIMESTAMP)
- Program: programCode, programTitleEn, programTitleTh
- Tier: tierCode, tierRank(INT64), tierStatus, tierIsPublished(BOOLEAN), tierNameEn/Th, tierDescriptionEn/Th
- Additional: additionalInfoTitle, additionalInfoUrl
- Complex arrays as JSON strings: spendings, colourCodes, images, benefits, privileges
- etlLoadTime (TIMESTAMP, HOUR partition)
- Clustering: [programCode, tierCode]

---

## 4. Members-Tiers-History-Collector

### Path: `loyalty/loyalty-data/members-tiers-collector/` (also called members-tiers-history-collector)

### Key Files
```
src/
├── main.py                                    # Entry + DI composition root
├── domain/
│   ├── models.py                              # HistoryRecord domain model
│   ├── schemas.py                             # MEMBER_TIERS_HISTORY_SCHEMA (15 fields)
│   ├── transformers.py                        # add_etl_metadata, convert_for_bigquery, convert_to_raw
│   ├── pipeline_config.py                     # PostgresConnectionConfig, InitDataPipelineConfig
│   ├── blms_catalog_config.py                 # BlmsCatalogConfig (frozen dataclass)
│   └── managed_iceberg_write_config.py        # ManagedIcebergWriteConfig (frozen dataclass)
├── adapters/
│   ├── input/
│   │   ├── postgres_client.py                 # PostgresClient with SSH tunnel support
│   │   └── configuration/
│   │       ├── settings.py                    # Pydantic DTOs
│   │       ├── configuration_adapter.py       # ConfigAdapter + CustomOptions (--process_date)
│   │       ├── options.py                     # --process_date, --query, --query_file
│   │       ├── secret_adapter.py              # SecretAdapter
│   │       └── logging_adapter.py             # LoggingAdapter
│   └── output/
│       ├── gcs/
│       │   ├── iceberg_writer.py              # Managed I/O writer (15 STRING fields)
│       │   ├── iceberg_sink.py                # IcebergSink PTransform
│       │   └── parquet_writer.py              # Parquet fallback
│       └── bigquery/
│           ├── bigquery_writer.py             # BigQueryWriterAdapter
│           ├── bigquery_writer_config.py       # Config dataclass
│           └── bq_metadata_refresh.py         # Option B refresh (DISABLED)
└── application/pipeline/
    ├── builder.py                             # PipelineBuilder: PostgreSQL or BQ init
    └── dofns.py                               # ReadFromPostgresDoFn
```

### Pipeline Flow (Normal - job_type=normal)
```
ReadFromPostgresDoFn (query with {prev_date} placeholder, defaults to yesterday)
  -> add_etl_metadata (etlLoadTime, process_date, _extracted_at, _source_table)
  -> convert_to_raw_format (all strings for Iceberg)
  -> IcebergSink (write to source.members_tiers_history)
  -> convert_for_bigquery (TIMESTAMP fields + Bangkok +7h) -> BigQueryWriterAdapter
```

### Pipeline Flow (Init - job_type=initial_data)
```
Source branches: ReadFromBigQuery (condition_parts) -> write_history_to_iceberg_batch
Refined branches: ReadFromBigQuery -> WriteToBigQuery
```

### PostgreSQL Source
- Database: `loyalty_members_api`
- Table: `public.member_tier_history`
- Query template: `SELECT * FROM public.member_tier_history WHERE updated_date >= '{prev_date}'`
- batch_size: 10000, SSH tunnel optional

### Key Transformers (domain/transformers.py)
- `add_etl_metadata(record, source_table, process_date)` - Adds metadata fields
- `serialize_complex_types(record)` - datetime->ISO, dict/list->JSON, numbers->string
- `convert_to_raw_format(record)` - ALL values to strings (Iceberg raw)
- `convert_for_bigquery(record)` - STRING timestamps -> Beam `Timestamp` with Bangkok +7h offset

### Iceberg Schema (HISTORY_RECORD_SCHEMA)
```python
RowTypeConstraint: 15 STRING fields
(id, member_id, trigger_type, program_code, tier_code, tracker_code,
 invite_channel, start_date, expiry_date, status,
 created_date, updated_date, etl_created_date, par_day, etlLoadTime)
```

### Refined Schema (15 fields)
- TIMESTAMP fields: start_date, expiry_date, created_date, updated_date, etl_created_date, etlLoadTime
- All other: STRING
- Partition: HOUR on etlLoadTime
- Clustering: member_id, tier_code

---

## 5. Purchases-Collector (Reference)

### Path: `loyalty/loyalty-data/purchases-collector/`
### Architecture: Ports & Adapters with full DI

### Key Patterns to Follow
1. **Composition Root** (`main.py`): Creates all PTransforms, injects into PipelineBuilder
2. **Pure Transformers** (`domain/transformers.py`): NO Beam imports, NO I/O
3. **DoFn Wrappers** (`pipeline/dofns.py`): Wrap pure functions + add Beam metrics
4. **PTransform Adapters** (`adapters/output/`): Compose Beam transforms for each sink
5. **Config Factory** (`BigQueryPurchasesConfig.to_table_config()`): Per-table config from dataset config
6. **Manual Iceberg Writer**: Full control over V2 metadata, manifest files, partition by hour(etlLoadTime)

### Pipeline Flow
```
Kafka -> Window(5s) -> AttachEventName -> BuildRawEvent
  -> Fan-out:
    |- Filter(purchases.created) -> PubSubSink
    |- GcsIcebergSink (manual Iceberg writer: GroupIntoBatches + ManualIcebergWriterDoFn)
    |- Map(to_receipt_row) -> BigQueryWriterAdapter (refined.purchases_receipt)
    |- FlatMap(to_detail_rows) -> BigQueryWriterAdapter (refined.purchases_detail)
    |- FlatMap(to_payment_rows) -> BigQueryWriterAdapter (refined.purchases_payment)
```

### Key Difference: Manual Iceberg Writer
- Uses `GroupIntoBatches` + `ManualIcebergWriterDoFn` (not Beam Managed IcebergIO)
- Handles Iceberg V2 metadata, manifest files, snapshots directly
- Partition: `hour(etlLoadTime)` with hours-since-epoch
- Schema: PyArrow with explicit field IDs (`PARQUET:field_id` metadata)

---

## 6. Messages-Collector (Reference)

### Path: `message/messaging-data/messages-collector/`
### Architecture: Same Ports & Adapters as purchases, but uses BLMS REST catalog

### Key Patterns (IDENTICAL to our collectors)
1. **BlmsCatalogConfig** + **ManagedIcebergWriteConfig** frozen dataclasses
2. **BLMS REST catalog properties**: type=rest, GoogleAuthManager, vended-credentials
3. **beam.Select()** for schema-aware rows (required for cross-language IcebergIO)
4. **ConfigurationAdapter** with Pydantic validation + Secret Manager

### Pipeline Flow
```
Kafka (5 topics: created/sent/opened/clicked/delivered)
  -> Window(5s) -> BuildRawEvent
  -> Write ALL to Iceberg (source.messages)
  -> Filter(delivered) -> FilterValid -> PubSub + Bigtable
  -> BuildBigQueryMessage -> BigQuery (refined.messages)
```

### BLMS REST Catalog Config (messages-collector)
```python
catalog_properties = {
    "type": "rest",
    "uri": "https://biglake.googleapis.com/iceberg/v1/restcatalog",
    "warehouse": "gs://the1-messaging-data-source-{env}",
    "rest.auth.type": "org.apache.iceberg.gcp.auth.GoogleAuthManager",
    "header.X-Iceberg-Access-Delegation": "vended-credentials",
    "header.x-goog-user-project": project_id,
    "io-impl": "org.apache.iceberg.gcp.gcs.GCSFileIO",
    "rest-metrics-reporting-enabled": "false",
}
```

---

## 7. Infrastructure & Terraform

### Directory Structure
```
infrastructure/
├── common/GCP/         (biglake-metastore.tf, buckets.tf, bigquery.tf, service-accounts.tf)
├── members/            (main.tf, bucket.tf, artifact.tf, secret-manager.tf, dts.tf + 12 schemas)
├── tiers/              (main.tf, bucket.tf, artifact.tf, secret-manager.tf, scheduler.tf + 2 schemas)
├── members-tiers-history/ (main.tf, bucket.tf, artifact.tf, secret-manager.tf, scheduler.tf, dts.tf + 4 schemas)
└── purchases/          (bucket.tf, artifact-registry.tf, service-accounts.tf, pubsub.tf + 3 schemas)
```

### Per-Collector Infrastructure
| Component | Members | Tiers | M-T-H |
|-----------|---------|-------|-------|
| GCS Bucket | `{project}-members-collector` | `{project}-tiers-collector` | `{project}-members-tiers-history-collector` |
| GAR Repo | `members-collector` | `tiers-collector` | `members-tiers-history-collector` |
| SA Name | `t1-members-collector` | `t1-tiers-collector` | `t1-members-tiers-his-collector` |
| Secret | `members-collector` (kafka+api) | `tiers-collector` (api) | `members-tiers-history-collector` (postgres+ssh) |
| Scheduler | No (streaming) | 1AM daily BKK | 1AM daily BKK |
| DTS | Yes (COMMENTED OUT) | No | Yes |
| biglake-metastore.tf | Per-collector IAM | Per-collector IAM | Per-collector IAM |

### BigLake Metastore (common/GCP/)
```hcl
# biglake-metastore.tf
google_biglake_iceberg_catalog:
  name = bucket name (the1-loyalty-data-source-{env})
  catalog_type = CATALOG_TYPE_GCS_BUCKET
  credential_mode = CREDENTIAL_MODE_VENDED_CREDENTIALS

# buckets.tf
Source bucket: the1-loyalty-data-source-{env}
BigLake SA gets objectAdmin on source bucket
```

### Cloud Scheduler Pattern (tiers + m-t-h)
```
Cloud Scheduler -> Dataflow REST API (flexTemplates:launch)
  - Terraform reads YAML configs -> deep merge -> base64 encode
  - HTTP POST with oauth_token (service account)
  - Schedule: 0 1 * * * (Asia/Bangkok)
  - tiers: max_workers=1
  - m-t-h: max_workers=2, includes process_date param
```

### deploy.py (Table Deployer, ~1853 lines, identical in all 3)

**Main Flow:**
1. `ensure_iceberg_metadata_v2()` - Create V2 metadata with partition spec
2. `create_iceberg_with_dummy_data()` - PyIceberg catalog -> dummy row -> snapshot
3. `execute_sql()` - CREATE EXTERNAL TABLE pointing to metadata
4. `delete_iceberg_dummy_data()` - Clean up dummy rows

**Schema Evolution:**
- `compare_schemas()` -> NO_CHANGE | ADDITIVE | BREAKING
- ADDITIVE: evolve_iceberg_schema() + drop/recreate BQ table
- BREAKING: backup -> drop -> recreate -> restore

**Key Flags:**
- `GOOGLE_AUTH_AVAILABLE = False` (Option B DISABLED)
- `register_table` instead of `create_table` (preserves field IDs + partition spec)

**Usage:**
```bash
python deploy.py <PROJECT_ID> <ENV> [--force] [--table=<name>] [--dataset=<name>]
```

---

## 8. Schema Catalog

### Members Infrastructure (12 schemas)
| Schema File | Dataset | Type | Fields | Partition |
|-------------|---------|------|--------|-----------|
| member_tier.json | source | external_iceberg | 7 (STRING) | IDENTITY(etlLoadTime) |
| refined_member_tier.json | refined | native | 13 | HOUR(etlLoadTime) |
| member_tier_maintenance.json | source | external_iceberg | 7 (STRING) | IDENTITY(etlLoadTime) |
| refined_member_tier_maintenance.json | refined | native | 28 | HOUR(etlLoadTime) |
| tier_events_upgraded.json | source | external_iceberg | 6 (STRING) | IDENTITY(etlLoadTime) |
| refined_tier_events_upgraded.json | refined | native | 12 | HOUR(etlLoadTime) |
| tier_events_downgraded.json | source | external_iceberg | 6 (STRING) | IDENTITY(etlLoadTime) |
| refined_tier_events_downgraded.json | refined | native | 11 | HOUR(etlLoadTime) |
| member_tier_init_raw.json | loyalty | native | 11 | None |
| member_tier_init_refined.json | loyalty | native | 11 | None |
| member_tier_maintenance_init_raw.json | loyalty | native | 19 | None |
| member_tier_maintenance_init_refined.json | loyalty | native | 19 | None |

### Tiers Infrastructure (2 schemas)
| Schema File | Dataset | Type | Fields | Partition |
|-------------|---------|------|--------|-----------|
| tiers.json | source | external_iceberg | 6 (STRING) | IDENTITY(etlLoadTime) |
| refined_tiers.json | refined | native | 23 | HOUR(etlLoadTime) |

### Members-Tiers-History Infrastructure (4 schemas)
| Schema File | Dataset | Type | Fields | Partition |
|-------------|---------|------|--------|-----------|
| members_tiers_history.json | source | external_iceberg | 15 (STRING) | IDENTITY(etlLoadTime) |
| refined_members_tiers_history.json | refined | native | 15 | HOUR(etlLoadTime) |
| members_tiers_history_init_raw.json | loyalty | native | 14 | None |
| members_tiers_history_init_refined.json | loyalty | native | 14 | None |

### Init Tables
- Init tables use dataset `loyalty` (NOT source/refined)
- Different schema from regular tables (full load format)
- Used with DTS (Data Transfer Service) for one-time S3->BQ load
- After init load -> run Dataflow job_type=initial_data -> write to real tables

---

## 9. Configuration Patterns

### YAML Merge Strategy
```
base.yaml (common) + {env}.yaml (stg/prod) -> merged config
  -> base64encode(yamlencode(merged))
  -> --dataflow_config CLI parameter
```

### Config Loading Pipeline
```
CLI --dataflow_config=<base64> -> Decode -> YAML parse
  -> Pydantic validation (DataflowConfigDto)
  -> Secret Manager fetch (project_id + secret_name)
  -> Build domain configs (BlmsCatalogConfig, ManagedIcebergWriteConfig)
  -> Return PipelineConfig (runtime)
```

### BLMS REST Catalog Config Chain
```
base.yaml:
  iceberg:
    blms_rest_uri_prefix: "https://biglake.googleapis.com/iceberg/v1/restcatalog"
    blms_namespace: "source"

-> settings.py (Pydantic DTO) validates
-> configuration_adapter.py builds BlmsCatalogConfig
-> ManagedIcebergWriteConfig wraps BlmsCatalogConfig + table_name
-> IcebergSink uses config.build_writer_config()
-> managed.Write(ICEBERG, config=writer_config)
```

### BigQuery Writer Config
```python
BigQueryWriterConfig(
    table="project:dataset.table",
    schema=BQ_SCHEMA_DICT,
    write_mode="append"|"cdc"|"batch",
    partition_field="etlLoadTime",
    primary_key=["memberId"],  # Required for CDC
    triggering_frequency=60,
    with_auto_sharding=True,
)
```

---

## 10. Critical Technical Patterns

### Bangkok Timezone +7 (MUST follow for ALL refined timestamps)
```python
# Source (Iceberg): STRING format YYYYMMDDHH in Bangkok time
_BANGKOK_TZ = timezone(timedelta(hours=7))
def _get_etl_load_time() -> str:
    return datetime.now(_BANGKOK_TZ).strftime("%Y%m%d%H")  # "2026021813"

# Refined (BQ): Beam Timestamp with +7h offset baked in
_BANGKOK_OFFSET_SECONDS = 7 * 3600  # 25200
_BANGKOK_OFFSET_MICROS = _BANGKOK_OFFSET_SECONDS * 1_000_000

# Current time + Bangkok offset
etlLoadTime = Timestamp(micros=Timestamp.now().micros + _BANGKOK_OFFSET_MICROS)

# Date/time columns from unix timestamp
Timestamp(seconds=unix_ts + _BANGKOK_OFFSET_SECONDS)
```

**Applied in all 3 collectors:**
- members-collector: `transform_dofns.py` (all 5 DoFns)
- tiers-collector: `transform_dofns.py` (ExtractTiersMasterPayloadDoFn)
- members-tiers-history: `transformers.py` (convert_for_bigquery)

### BigQuery Storage Write API + TIMESTAMP
```python
# MUST use apache_beam.utils.timestamp.Timestamp — NOT datetime.datetime
from apache_beam.utils.timestamp import Timestamp

ts = Timestamp(seconds=unix_ts)                    # Unix -> Timestamp
ts = Timestamp(micros=Timestamp.now().micros + offset)  # Current + offset
```

### CDC Mode (members member_tier in prod)
```python
# Wraps rows in mutation envelope:
row_mutation_info = {
    "mutation_type": "UPSERT",
    "change_sequence_number": hex_string
}
record = { all fields as STRING (timestamps lose type) }

# CDC only for native tables, NOT BigLake Iceberg
```

### Iceberg Write via BLMS REST
```python
config = ManagedIcebergWriteConfig(catalog=blms_config, table_name="tiers")
writer_config = config.build_writer_config()
# Returns:
{
    "table": "source.tiers",
    "catalog_name": "the1-loyalty-data-source-stg",
    "catalog_properties": {
        "type": "rest",
        "uri": "https://biglake.googleapis.com/iceberg/v1/restcatalog",
        "warehouse": "gs://the1-loyalty-data-source-stg",
        "rest.auth.type": "org.apache.iceberg.gcp.auth.GoogleAuthManager",
        "header.X-Iceberg-Access-Delegation": "vended-credentials",
        ...
    },
    "triggering_frequency_seconds": 300,
    "table_properties": {"location": "gs://the1-loyalty-data-source-stg/tiers"},
}
pcoll | managed.Write(managed.ICEBERG, config=writer_config)
```

### Windowing (members streaming)
```python
FixedWindows(60)
  + AfterWatermark(early=Repeatedly(AfterProcessingTime(60)))
  + AccumulationMode.DISCARDING
```

### Avro Detection
```python
if data[0] == 0x00 and len(data) >= 5:
    # Confluent Schema Registry Avro format
else:
    # JSON format
```

---

## 11. Common Pitfalls & Fixes

| Error | Root Cause | Fix |
|-------|-----------|-----|
| OOM on GitLab Runner (exit 137) | 10M+ rows in memory | Use Dataflow batch (job_type=initial_data) |
| Ruff RUF043 | Unescaped regex | Use raw string: `match=r"kafka\.topics"` |
| BigQuery TIMESTAMP type error | Using datetime.datetime | Use `Timestamp(seconds=...)` |
| Partition writing flat | deploy.py missing partition_spec | Fixed: `create_iceberg_with_dummy_data()` passes partition_spec |
| Token expiry (IcebergIO managed) | 1-hour OAuth2 token | BLMS REST handles refresh via GoogleAuthManager |
| pre-commit purchases-collector fail | pyarrow 17.0.0 + Python 3.13 | Known issue, ignore |
| CDC TIMESTAMP in nested RECORD | Cross-language serialization | Convert TIMESTAMP to STRING in CDC envelope |

### Quality Check Commands (MUST run after EVERY change)
```bash
cd loyalty/loyalty-data/{collector}/
uv sync
ruff check . && ruff format --check .
mypy .
pytest
pre-commit run --all-files
```

---

## 12. Current State & Pending Work

### IcebergIO Write: BLMS REST Catalog ACTIVE
- All 3 collectors use BlmsCatalogConfig + ManagedIcebergWriteConfig
- Hadoop catalog preserved as comments (search `"Hadoop Catalog"`)
- Verified identical to messaging-collector pattern

### Option B (BQ metadata refresh): CODE DONE, DISABLED
- `bq_metadata_refresh.py` x3 - Module exists, tests pass
- `deploy.py` x3 - `GOOGLE_AUTH_AVAILABLE = False`, Option B call sites commented
- Waiting for terraform dataset (`externalCatalogDatasetOptions`) from transaction/ team

### GitLab CI: PROD COMMENTED (testing STG first)
- create-image: 4 destinations (STG active + PROD commented)
- terraform:apply:prod, deploy-tables:prod, deploy:prod: ALL COMMENTED

### Pending Work
1. **STG->PROD dependency chain** - add `needs: deploy:stg` to deploy:prod
2. **members drain-first** - upgrade cancel to drain-then-cancel (like purchases)
3. **BQ backup before deploy-tables:prod** - prevent data loss on schema changes
4. **DLQ implementation** - `docs/dlq/DLQ_CHECKLIST.md` (Phase 1: API DoFns)
5. **Re-enable Option B** when transaction/ team provides terraform dataset
6. **Dataplex setup** - Enable API, create Lake/Zone

### Test Counts (verified)
- members-collector: ~198 tests
- tiers-collector: ~107 tests
- members-tiers-history: ~104 tests
- **Total: ~409 tests**

### Documentation Map
| Doc | Path |
|-----|------|
| Master Index | `loyalty/docs/README.md` |
| Option B Summary | `loyalty/docs/option-b-migration/OPTION_B_SUMMARY.md` |
| DLQ Research | `loyalty/docs/dlq/DLQ_RESEARCH.md` |
| DLQ Checklist | `loyalty/docs/dlq/DLQ_CHECKLIST.md` |
| CI/CD Comparison | `loyalty/docs/architecture/CICD_COMPARISON_AND_PROD_SAFETY.md` |
| Refactoring Plan | `loyalty/docs/architecture/REFACTORING_CHECKLIST_TO_PURCHASES_STANDARD.md` |
| Init Data Pipeline | `loyalty/docs/pipeline/MEMBERS_COLLECTOR_INIT_DATA_PIPELINE.md` |
| BQ Deploy Guide | `loyalty/docs/bigquery/deploy-table/README.md` |
