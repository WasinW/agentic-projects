# Skills & Work Checklist — Wasin Wangsombut (The 1 Project, 2025-2026)

> เอกสารนี้รวบรวม skills และรายละเอียดงานทั้งหมดจาก 5 โปรเจกต์ data pipeline ที่รับผิดชอบ
> ไว้สำหรับเกลาและตัด scope ทีหลัง — part ไหนไม่ได้ทำจริงก็ลบออก / part ไหนขาดก็เพิ่ม

---

## สารบัญ

1. [ภาพรวมโปรเจกต์ทั้งหมด](#1-ภาพรวมโปรเจกต์ทั้งหมด)
2. [Skills Map (สรุปทักษะที่ใช้จริง)](#2-skills-map)
3. [Project 1: Insight / Data — Customer Profile Pipeline](#3-project-1-insight--data)
4. [Project 2: Loyalty — Members Collector](#4-project-2-loyalty--members-collector)
5. [Project 3: Loyalty — Tiers Collector](#5-project-3-loyalty--tiers-collector)
6. [Project 4: Loyalty — Members Tiers History Collector](#6-project-4-loyalty--members-tiers-history-collector)
7. [Project 5: Sales — Sales Collector](#7-project-5-sales--sales-collector)
8. [Cross-Project Shared Work](#8-cross-project-shared-work)
9. [เปรียบเทียบกับ CV 2024 — Skills ใหม่ที่ได้เพิ่ม](#9-เปรียบเทียบกับ-cv-2024)

---

## 1. ภาพรวมโปรเจกต์ทั้งหมด

| # | Project | Pipeline Type | Data Source | Sink | Output Tables | Tests |
|---|---------|--------------|-------------|------|---------------|-------|
| 1 | insight/data (customer-profile-pipeline) | Streaming | Pub/Sub + Bigtable | BigQuery + S3 + Iceberg | ms_personas, events_consents, DLQ | ~84 files |
| 2 | loyalty/members-collector | Streaming | Kafka (2 topics) + Loyalty API | Iceberg + BigQuery | 4 source + 4 refined | 220+ |
| 3 | loyalty/tiers-collector | Batch | Loyalty Tiers API | Iceberg + BigQuery | 1 source + 1 refined | 197 |
| 4 | loyalty/members-tiers-history-collector | Batch | PostgreSQL | Iceberg + BigQuery | 1 source + 1 refined | 104 |
| 5 | sales/sales-collector | Streaming | Kafka (2 topics) | Iceberg + BigQuery | 2 source + 3 refined | 126 |

**Tech Stack ที่ใช้ร่วมกัน:** Python 3.11-3.12, Apache Beam 2.69-2.70, Google Cloud Dataflow, BigQuery, GCS, Iceberg (BigLake REST Catalog), Kafka (Confluent Cloud), GitLab CI/CD, Terraform

---

## 2. Skills Map

### 2.1 Programming & Frameworks

| Skill | รายละเอียด | ใช้ในโปรเจกต์ |
|-------|-----------|---------------|
| **Python 3.11/3.12** | ภาษาหลักทุก pipeline | ทุกโปรเจกต์ |
| **Apache Beam** | Data processing framework (DoFn, PTransform, Pipeline, Windowing, Triggers) | ทุกโปรเจกต์ |
| **PySpark** (จาก CV เดิม) | ไม่ได้ใช้ในโปรเจกต์นี้ แต่เป็น background skill | - |
| **Pydantic** | Configuration validation, DTO models | sales, insight |
| **Dataclasses (frozen)** | Domain models (BlmsCatalogConfig, ManagedIcebergWriteConfig) | loyalty x3, sales |
| **TypedDict** | Data models (RawEvent, IntermediateEvent, MemberTierPayload) | loyalty, sales |

### 2.2 Data Pipeline Design & Architecture

| Skill | รายละเอียด | ใช้ในโปรเจกต์ |
|-------|-----------|---------------|
| **Streaming Pipeline Design** | Real-time Kafka → Transform → Multi-sink | members, sales, insight |
| **Batch Pipeline Design** | Periodic trigger → API/DB fetch → Transform → Write | tiers, m-t-h |
| **Fan-out Pattern** | Single source → multiple output tables | members (4 tables), sales (3+2 tables) |
| **CDC (Change Data Capture)** | UPSERT/DELETE semantics, primary key dedup | members, sales |
| **CDC DELETE Pattern** | 3-layer safety: Kafka tier_code → API verify → BQ confirm → DELETE | members |
| **Initial Data Load** | Batch backfill from staging tables (job_type=initial_data) | members, m-t-h |
| **Hexagonal Architecture** | Ports/Adapters pattern (input/output separation) | insight (V3) |
| **Domain-Driven Design** | Pure domain models + transformers separated from infra | ทุกโปรเจกต์ |
| **Composition Root** | main.py creates all dependencies, injects into builder | sales, insight |

### 2.3 Data Ingestion & Sources

| Skill | รายละเอียด | ใช้ในโปรเจกต์ |
|-------|-----------|---------------|
| **Kafka Consumer** | Confluent Cloud, SASL_SSL, Schema Registry | members, sales |
| **Avro Deserialization** | Confluent Schema Registry magic byte detection, Avro → dict | members, sales |
| **JSON Message Parsing** | Multi-schema support (Schema A/B/C) with auto-detection | members, sales |
| **REST API Integration** | Loyalty API (/v2/members/{id}/tiers, /v2/tiers) | members, tiers |
| **PostgreSQL Read** | Parameterized batch query with date range, SSH tunnel option | m-t-h |
| **Pub/Sub Consumer** | Google Cloud Pub/Sub streaming read | insight |
| **Bigtable Read** | Fetch profiles/consents from Cloud Bigtable | insight |
| **BigQuery Read** | Initial data load from staging tables, CDC DELETE verification | members |

### 2.4 Data Transformation

| Skill | รายละเอียด | ใช้ในโปรเจกต์ |
|-------|-----------|---------------|
| **Message Schema Detection** | Auto-detect Schema A (flat), B (nested payload), C (stringified wrapper) | members |
| **Avro Union Unwrapping** | `{"string": "x"}` → `"x"`, nested Avro type handling | sales |
| **Payload Extraction** | Extract specific fields from nested JSON → flat BigQuery rows | ทุกโปรเจกต์ |
| **Type Conversion** | String → INT64, TIMESTAMP, NUMERIC, DATE for BigQuery | ทุกโปรเจกต์ |
| **Timestamp Handling** | Unix seconds/millis/ISO 8601 → Bangkok UTC+7 offset | ทุกโปรเจกต์ |
| **Denormalization** | Nested arrays → multiple flat rows (items → SKU rows, payments → tender rows) | sales |
| **Deduplication** | Per-bundle (DoFn state) + cross-bundle (Beam.Distinct / GroupByKey) | members |
| **Data Enrichment** | Kafka event + API response → enriched output | members |
| **Partition Field Calculation** | `etlLoadTime` (INT YYYYMMDDHH) → `ingestedTHDate` (INT YYYYMMDD) | members, m-t-h |
| **CDC Row Wrapping** | `_is_delete` flag → `mutation_type: "DELETE"` / `"UPSERT"` | members |
| **Mapping Reconciliation** | Dynamic column mapping from BigQuery reference table | insight |

### 2.5 Data Sink & Storage

| Skill | รายละเอียด | ใช้ในโปรเจกต์ |
|-------|-----------|---------------|
| **Apache Iceberg (Source Layer)** | Write via BigLake Managed Storage (BLMS) REST Catalog | ทุกโปรเจกต์ |
| **Beam Managed IcebergIO** | `managed.Write()` with BLMS vended credentials, auto table creation | loyalty x3, sales |
| **BigQuery Native Tables** | STORAGE_WRITE_API, append/CDC/truncate modes | ทุกโปรเจกต์ |
| **BigQuery CDC Writes** | Primary key-based UPSERT with StorageWriteAPI, triggering frequency | members, sales |
| **BigQuery Partitioning** | DAY partition on date fields (trans_date, created_date, ingestedTHDate) | ทุกโปรเจกต์ |
| **BigQuery Clustering** | Cluster keys for query performance (member_id, partner_code, sku) | sales, m-t-h |
| **S3 Parquet Export** | Windowed writes to AWS S3 with gzip compression | insight |
| **Iceberg Sync (MERGE)** | Periodic MERGE from BigQuery to Iceberg tables | insight |

### 2.6 Schema Design (BigQuery)

| Skill | รายละเอียด | ใช้ในโปรเจกต์ |
|-------|-----------|---------------|
| **BigQuery Schema Design** | JSON schema files สำหรับ refined tables | ทุกโปรเจกต์ |
| **Iceberg Schema Design** | PyArrow schemas สำหรับ source layer | ทุกโปรเจกต์ |
| **Schema Evolution** | Handle schema changes without breaking existing data | loyalty |
| **Primary Key Design** | Composite keys for CDC tables (e.g., partner_code + branch_code + trans_date + receipt_no) | members, sales |
| **Partition Strategy** | DAY vs HOUR partition, choosing partition field | ทุกโปรเจกต์ |
| **Clustering Strategy** | Choosing cluster columns for query optimization | sales, m-t-h |
| **Write Disposition** | WRITE_APPEND vs WRITE_TRUNCATE vs CDC selection | ทุกโปรเจกต์ |

### 2.7 Testing

| Skill | รายละเอียด | ใช้ในโปรเจกต์ |
|-------|-----------|---------------|
| **Unit Testing (pytest)** | Pure function tests สำหรับ transformers, validators | ทุกโปรเจกต์ |
| **DoFn Testing** | Test Beam DoFn classes (metrics, logging, output) | ทุกโปรเจกต์ |
| **Configuration Testing** | Validate Pydantic DTOs, YAML parsing, secret loading | sales, insight |
| **Schema Validation Testing** | Verify BigQuery/Iceberg schema correctness | ทุกโปรเจกต์ |
| **Edge Case Testing** | Schema A/B/C variants, missing fields, type mismatches, CDC DELETE | members, sales |
| **Test Fixtures** | conftest.py shared fixtures (sample payloads, raw events) | ทุกโปรเจกต์ |
| **Coverage Reporting** | pytest-cov with Cobertura reports for CI | ทุกโปรเจกต์ |
| **Total Tests Written** | 220+ (members) + 197 (tiers) + 104 (m-t-h) + 126 (sales) = **647+ tests** | - |

### 2.8 Infrastructure & DevOps

| Skill | รายละเอียด | ใช้ในโปรเจกต์ |
|-------|-----------|---------------|
| **Terraform (IaC)** | GCS buckets, GAR repos, BigLake catalog, IAM, Secret Manager | ทุกโปรเจกต์ |
| **GitLab CI/CD** | Multi-stage pipeline (build → test → deploy STG → deploy PROD) | ทุกโปรเจกต์ |
| **Docker / Kaniko** | Multi-stage Dockerfile, Flex Template images | ทุกโปรเจกต์ |
| **Google Cloud Dataflow** | Streaming + Batch job deployment via Flex Templates | ทุกโปรเจกต์ |
| **Google Secret Manager** | Per-collector secrets (Kafka creds, API creds, DB creds) | ทุกโปรเจกต์ |
| **BigLake Metastore** | BLMS REST Catalog for Iceberg table management | ทุกโปรเจกต์ |
| **Cloud Scheduler** | Batch job triggers (1AM BKK daily) | tiers, m-t-h |
| **deploy.py Script** | Automated BQ table creation, ALTER, backup/restore, schema compare | loyalty x3 |

### 2.9 Code Quality & Tooling

| Skill | รายละเอียด | ใช้ในโปรเจกต์ |
|-------|-----------|---------------|
| **ruff** | Python linter + formatter | ทุกโปรเจกต์ |
| **mypy** | Static type checking | ทุกโปรเจกต์ |
| **pre-commit** | Git hooks for code quality | ทุกโปรเจกต์ |
| **SonarQube** | Code quality analysis in CI | ทุกโปรเจกต์ |
| **gitleaks** | Secret scanning | ทุกโปรเจกต์ |
| **uv** | Python package management (fast pip alternative) | loyalty, sales |
| **poethepoet (poe)** | Task runner for lint/test/format/typecheck | sales |

---

## 3. Project 1: Insight / Data

**Path:** `insight-api/data/customer-profile-pipeline/`
**Type:** Streaming pipeline (Pub/Sub → Bigtable → BigQuery + S3 + Iceberg)
**Framework:** Apache Beam 2.69.0, Python 3.11+
**Architecture:** Hexagonal (Ports/Adapters)

### 3.1 งานที่ทำ — Checklist

#### Schema Design

- [ ] ออกแบบ BigQuery schema สำหรับ `ms_personas` (CDC-enabled, primary key: memberId)
- [ ] ออกแบบ BigQuery schema สำหรับ `events_consents`
- [ ] ออกแบบ BigQuery schema สำหรับ `data_pipeline_dlq` (Dead Letter Queue)
- [ ] ออกแบบ BigQuery schema สำหรับ `ms_personas_consents_history`
- [ ] ออกแบบ BigQuery schema สำหรับ `ms_personas_consents_internal_partner`
- [ ] ออกแบบ BigQuery schema สำหรับ `ms_personas_consents_external_partner`
- [ ] ออกแบบ BigQuery schema สำหรับ `ms_personas_suppression`
- [ ] ออกแบบ `mapping_reconcile` table สำหรับ dynamic column mapping
- [ ] ออกแบบ Iceberg schema สำหรับ `ms_personas_iceberg` (BigLake)

#### Transformer Development

- [ ] พัฒนา `TransformSchemasDoFn` — แปลง Bigtable dict + mapping → AWS + GCP schemas
- [ ] พัฒนา `FullfillSchemasDoFn` — เติม default values สำหรับ fields ที่ขาด
- [ ] พัฒนา `MapToCdcTableRowDoFn` — เพิ่ม CDC metadata (UPSERT)
- [ ] พัฒนา `ExtractPersonasDoFn` — extract persona ID จาก Pub/Sub message
- [ ] พัฒนา `FetchFromBigtableDoFn` — fetch profiles/consents จาก Bigtable
- [ ] พัฒนา `FilterEmptyPKDoFn` — filter records ที่ member ID ว่าง
- [ ] พัฒนา `FilterEmptyFamilyDoFn` — filter by column family
- [ ] พัฒนา `MappingRefreshDoFn` — periodic refresh mapping จาก BigQuery
- [ ] พัฒนา `WritePartitionToParquetDoFn` — write ไป S3 เป็น Parquet files
- [ ] พัฒนา `SyncToIcebergDoFn` — sync ไป Iceberg via MERGE
- [ ] พัฒนา `SQLSubmitDoFn` — execute SQL queries on schedule
- [ ] พัฒนา `WriteDLQToBigQuery` — write failed records to DLQ table

#### Pipeline Architecture

- [ ] ออกแบบ pipeline flow: Pub/Sub → Bigtable fetch → Transform → Multi-sink
- [ ] Implement V3 Flex Template architecture (self-contained Docker image)
- [ ] Implement hexagonal architecture (ports/adapters pattern)
- [ ] Implement composition root pattern ใน `main.py`
- [ ] ออกแบบ DLQ pattern — write failed records to BigQuery (improvement over V1 logging)
- [ ] Implement rate-limited logging (prevent log flooding)

#### Data Sink

- [ ] Implement BigQuery CDC writer (STORAGE_WRITE_API, 5 parallel streams)
- [ ] Implement S3 Parquet writer (windowed writes, gzip, date column handling)
- [ ] Implement Iceberg sync writer (MERGE every 5 min, 30-min lookback)

#### Configuration

- [ ] ออกแบบ environment-based config (settings.py)
- [ ] Implement pipeline options (CustomOptions)
- [ ] เขียน config YAML files (stg, uat, prod)

#### Testing

- [ ] เขียน unit tests สำหรับ adapters (input: bigquery_mapping, sql_loader; output: iceberg_sync, s3_parquet)
- [ ] เขียน unit tests สำหรับ domain (constants, transformers)
- [ ] เขียน unit tests สำหรับ pipeline (dofns)
- [ ] เขียน unit tests สำหรับ core (logging_utils)
- [ ] เขียน integration tests (consent_processing)

#### Infrastructure

- [ ] Terraform: BigQuery datasets, Pub/Sub, Bigtable, GCS, GAR, DTS
- [ ] Cloud Composer (Airflow) configuration
- [ ] GitLab CI/CD: build, deploy-stg, test-stg, deploy-prod
- [ ] Dockerfile สำหรับ Flex Template

---

## 4. Project 2: Loyalty — Members Collector

**Path:** `loyalty/loyalty-data/members-collector/`
**Type:** Streaming pipeline (Kafka → API enrichment → Iceberg + BigQuery)
**Framework:** Apache Beam 2.70.0, Python 3.12
**Kafka Topics:** `loyalty.members.upgraded`, `loyalty.members.downgraded`

### 4.1 งานที่ทำ — Checklist

#### Schema Design

- [ ] ออกแบบ Iceberg source schema: `source.tier_events_upgraded` (partition: etlLoadTime)
- [ ] ออกแบบ Iceberg source schema: `source.tier_events_downgraded` (partition: etlLoadTime)
- [ ] ออกแบบ Iceberg source schema: `source.member_tier` (partition: ingestedTHDate → INT YYYYMMDD)
- [ ] ออกแบบ Iceberg source schema: `source.member_tier_maintenance` (partition: ingestedTHDate)
- [ ] ออกแบบ BigQuery refined schema: `refined.tier_events_upgraded` (12 fields, partition: etl_created_date)
- [ ] ออกแบบ BigQuery refined schema: `refined.tier_events_downgraded` (11 fields, partition: etl_created_date)
- [ ] ออกแบบ BigQuery refined schema: `refined.member_tier` (13 fields, CDC, PK: member_id + program_code)
- [ ] ออกแบบ BigQuery refined schema: `refined.member_tier_maintenance` (27 fields, CDC, PK: tierMaintenanceId)
- [ ] เขียน JSON schema files สำหรับ deploy.py

#### Transformer Development

- [ ] พัฒนา `attach_event_name()` — handle 3 schemas:
  - [ ] Schema A: flat message → wrap entire dict as payload
  - [ ] Schema B: nested `payload` dict → unwrap inner payload
  - [ ] Schema C: `message` key with stringified JSON → `json.loads()` → unwrap
- [ ] พัฒนา `ExtractMemberIdAndTierCodeDoFn` — extract (member_id, tier_code, tier_event_id) จาก Kafka message
- [ ] พัฒนา `DeduplicatePairsDoFn` — per-bundle dedup ของ (member_id, tier_code) pairs
- [ ] พัฒนา `FetchMemberTierDoFn` — call `/v2/members/{id}/tiers` API with CDC DELETE support:
  - [ ] `tier_code is None` → yield all tiers (UPSERT) — original behavior
  - [ ] `tier_code` found in API → yield only matching item (UPSERT)
  - [ ] `tier_code` NOT in API → query BQ → CDC DELETE (3-layer safety)
- [ ] พัฒนา `FetchTierMaintenanceDoFn` — call tier maintenance endpoint
- [ ] พัฒนา `ExtractTierEventUpgradedPayloadDoFn` — 12 fields (includes isExistingTier)
- [ ] พัฒนา `ExtractTierEventDowngradedPayloadDoFn` — 11 fields (no isExistingTier)
- [ ] พัฒนา `ExtractMemberTierPayloadDoFn` — member tier details
- [ ] พัฒนา `ExtractTierMaintenancePayloadDoFn` — maintenance details
- [ ] พัฒนา `_WrapCdcRowDoFn` — `_is_delete: True` → `mutation_type: "DELETE"`
- [ ] พัฒนา `_get_ingested_th_date()` — INT YYYYMMDD Bangkok time (Iceberg) / "%Y-%m-%d" string (BQ)

#### Pipeline Architecture

- [ ] ออกแบบ pipeline flow: Kafka → ExtractMemberIdAndTierCode → Dedup → API Fetch → Transform → Write
- [ ] Implement fan-out: shared member_ids → member_tier branch + tier_maintenance branch
- [ ] Implement `Beam.Distinct()` for cross-bundle deduplication (fix tier maintenance dup)
- [ ] Implement initial data load path (job_type=initial_data จาก BigQuery staging)
- [ ] Implement 60-second windowing for Kafka messages

#### CDC DELETE Implementation

- [ ] ออกแบบ CDC DELETE via Diff pattern (carry tierCode from Kafka, match against API, BQ query for DELETE)
- [ ] Implement 3-layer DELETE safety: (1) tier_code not None, (2) API doesn't have it, (3) BQ confirms existed
- [ ] Implement `_is_delete` flag pattern in elements
- [ ] Implement BigQuery query for existing records (`bigquery_storage.py`)

#### Bug Fixes & Migrations

- [ ] Fix Schema B nested payload double-wrapping bug (`attach_event_name()`)
- [ ] Fix Schema C stringified message variant
- [ ] Rename `etlLoadTime` → `ingestedTHDate` (14 files: iceberg_writer, transform_dofns, schemas, main, builder, settings, pipeline_config, base.yaml, 2 JSON schemas, 4 SQL init, 3 test files)
- [ ] Migrate Kafka secret keys: `kafka_connection` → `kafkaCredentials`, `api_connection` → `apiCredentials`
- [ ] Fix partition_fields alignment (add `partition_fields` to `ManagedIcebergWriteConfig` instantiation sites)

#### Data Sink

- [ ] Implement IcebergSink with BLMS REST Catalog (managed.Write)
- [ ] Implement BigQuery CDC sink (STORAGE_WRITE_API, primary key dedup)
- [ ] Implement BigQuery append sink (tier events)
- [ ] Configure partition fields per table (ingestedTHDate vs etlLoadTime)

#### Configuration

- [ ] เขียน `base.yaml` — Kafka, Iceberg, refined table configs
- [ ] เขียน `stg.yaml` / `prod.yaml` — environment overrides
- [ ] Implement `PipelineConfig` domain model
- [ ] Implement `BlmsCatalogConfig` (frozen dataclass, BLMS REST settings)
- [ ] Implement `ManagedIcebergWriteConfig` (frozen dataclass, table + partition settings)

#### Testing (220+ tests)

- [ ] เขียน tests สำหรับ configuration loading (`test_configuration_adapter.py`)
- [ ] เขียน tests สำหรับ API interactions (`test_api_dofns.py`) — includes 10 CDC DELETE tests
- [ ] เขียน tests สำหรับ payload transformation (`test_transform_dofns.py`) — 200 tests
- [ ] เขียน tests สำหรับ Schema A/B/C handling (`test_transformers.py`) — 3 Schema C tests
- [ ] เขียน tests สำหรับ CDC DELETE logic — 17 new tests (10 api_dofns + 2 transform_dofns + 5 bigquery_storage)
- [ ] เขียน tests สำหรับ message parsing (`test_dofns.py`)
- [ ] เขียน tests สำหรับ BigQuery schema validation (`test_schemas.py`)
- [ ] เขียน tests สำหรับ Iceberg sink/writer

#### deploy.py & Infrastructure

- [ ] Rewrite deploy.py: ~2290 lines → ~370 lines (native BQ only, removed PyIceberg)
- [ ] Implement: CREATE TABLE, ALTER TABLE, backup/restore, schema compare
- [ ] Remove: 6 empty (0B) JSON source table placeholders
- [ ] Terraform: GCS bucket, GAR repo, BigLake metastore IAM, Secret Manager
- [ ] GitLab CI: linter, mypy, pytest, create-image (4 destinations), terraform, deploy

---

## 5. Project 3: Loyalty — Tiers Collector

**Path:** `loyalty/loyalty-data/tiers-collector/`
**Type:** Batch pipeline (API poll → Iceberg + BigQuery)
**Framework:** Apache Beam 2.70.0, Python 3.12
**Trigger:** Cloud Scheduler 1AM BKK daily

### 5.1 งานที่ทำ — Checklist

#### Schema Design

- [ ] ออกแบบ Iceberg source schema: `source.tiers` (18 fields, all STRING, partition: etlLoadTime)
- [ ] ออกแบบ BigQuery refined schema: `refined.tiers_master` (21 fields, no partition, WRITE_TRUNCATE)
- [ ] เขียน JSON schema files สำหรับ deploy.py

#### Transformer Development

- [ ] พัฒนา `FetchTiersDoFn` — call `/v2/tiers` endpoint, flatten nested tier arrays
- [ ] พัฒนา `ExtractTiersMasterPayloadDoFn` — flatten nested tiers:
  - [ ] Map API fields → flat row (tiers_code → tierCode)
  - [ ] Convert types (tiers_rank: string → int)
  - [ ] JSON-encode array fields (benefits, privileges)

#### Pipeline Architecture

- [ ] ออกแบบ simple batch pipeline: PeriodicImpulse → FetchTiers → Transform → Write
- [ ] ไม่มี Kafka, ไม่มี CDC — simple fetch + replace

#### Data Sink

- [ ] Implement IcebergSink with BLMS REST Catalog
- [ ] Implement BigQuery batch sink (WRITE_TRUNCATE — replaces entire master table)

#### Configuration

- [ ] เขียน `base.yaml`, `stg.yaml`, `prod.yaml`
- [ ] Implement config adapter, pipeline config, BLMS catalog config

#### Testing (197 tests)

- [ ] เขียน tests สำหรับ API fetch (`test_api_dofns.py`)
- [ ] เขียน tests สำหรับ tiers payload transformation (`test_transform_dofns.py`)
- [ ] เขียน tests สำหรับ configuration (3 config test files)
- [ ] เขียน tests สำหรับ Iceberg/BQ sinks

#### deploy.py & Infrastructure

- [ ] deploy.py: native BQ only (identical pattern to members-collector)
- [ ] Terraform: GCS bucket, GAR repo, BigLake metastore IAM
- [ ] GitLab CI: same multi-stage pipeline

---

## 6. Project 4: Loyalty — Members Tiers History Collector

**Path:** `loyalty/loyalty-data/members-tiers-history-collector/`
**Type:** Batch pipeline (PostgreSQL → Iceberg + BigQuery)
**Framework:** Apache Beam 2.70.0, Python 3.12
**Trigger:** Cloud Scheduler 1AM BKK daily

### 6.1 งานที่ทำ — Checklist

#### Schema Design

- [ ] ออกแบบ Iceberg source schema: `source.members_tiers_history` (13 fields, all STRING, partition: ingestedTHDate)
- [ ] ออกแบบ BigQuery refined schema: `refined.member_tier_history` (13 fields, partition: created_date, clustering: member_id + tier_code)
- [ ] เขียน JSON schema files สำหรับ deploy.py

#### Transformer Development

- [ ] พัฒนา `ReadFromPostgresDoFn` — parameterized batch query:
  - [ ] Query template with `{prev_date}` placeholder
  - [ ] Reads in configurable batch size (default 10k)
  - [ ] Time range based on `--process_date` (default: yesterday)
- [ ] พัฒนา `convert_for_bigquery()` — PostgreSQL → BigQuery type conversion:
  - [ ] Timestamp handling (origin_created_date → TIMESTAMP)
  - [ ] Partition field: created_date (DATETIME)

#### Pipeline Architecture

- [ ] ออกแบบ batch pipeline: PeriodicImpulse → ReadFromPostgres → Transform → Write
- [ ] Implement initial data load path (job_type=initial_data)
- [ ] Implement parameterized date range query

#### Data Sink

- [ ] Implement IcebergSink with BLMS REST Catalog
- [ ] Implement BigQuery sink (WRITE_APPEND default, WRITE_TRUNCATE configurable)
- [ ] Configure clustering on (member_id, tier_code)

#### Configuration

- [ ] เขียน `base.yaml` with PostgreSQL connection settings:
  - [ ] Database, port, batch_size, query_template
  - [ ] Secret keys: rds_endpoint, rds_username, rds_password
  - [ ] Optional SSH tunnel settings
- [ ] เขียน `stg.yaml`, `prod.yaml`

#### Testing (104 tests)

- [ ] เขียน tests สำหรับ PostgreSQL client (`test_postgres_client.py`)
- [ ] เขียน tests สำหรับ configuration (3 standard config tests)
- [ ] เขียน tests สำหรับ Iceberg/BQ sinks
- [ ] เขียน tests สำหรับ schema validation

#### deploy.py & Infrastructure

- [ ] deploy.py: native BQ only (identical pattern)
- [ ] Terraform: GCS bucket, GAR repo, BigLake metastore IAM
- [ ] GitLab CI: same multi-stage pipeline

---

## 7. Project 5: Sales — Sales Collector

**Path:** `sales/sales-data/sales-collector/`
**Type:** Streaming pipeline (Kafka → Iceberg + BigQuery)
**Framework:** Apache Beam 2.70.0, Python 3.12
**Kafka Topics:** `loyalty.sales.created`, `loyalty.sales.updated`

### 7.1 งานที่ทำ — Checklist

#### Schema Design

- [ ] ออกแบบ Iceberg source schema: `source.raw_sales_created` (data + ingested_date + ingested_at)
- [ ] ออกแบบ Iceberg source schema: `source.raw_sales_updated`
- [ ] ออกแบบ BigQuery refined schema: `refined.sales_receipt` (26 fields):
  - [ ] PK: [partner_code, branch_code, trans_type, trans_date, display_receipt_no]
  - [ ] Partition: DAY on trans_date
  - [ ] Clustering: [partner_code, member_number, branch_code]
- [ ] ออกแบบ BigQuery refined schema: `refined.sales_sku` (28 fields):
  - [ ] PK: [partner_code, branch_code, trans_type, trans_date, display_receipt_no, sku]
  - [ ] Partition: DAY on trans_date
  - [ ] Clustering: [partner_code, sku, member_number]
- [ ] ออกแบบ BigQuery refined schema: `refined.sales_tender` (27 fields):
  - [ ] PK: [partner_code, branch_code, trans_type, trans_date, display_receipt_no, tender_type, member_number]
  - [ ] Partition: DAY on trans_date
  - [ ] Clustering: [partner_code, tender_type, member_number]
- [ ] เขียน JSON schema files (raw_sales.json, sales_receipt.json, sales_sku.json, sales_tender.json)
- [ ] เขียน SCHEMA_MAPPING.md documentation

#### Transformer Development

- [ ] พัฒนา `transformers.py` — Kafka message handling:
  - [ ] `is_avro_message(data)` — detect Confluent Schema Registry magic byte
  - [ ] `extract_value(record)` — extract bytes from tuple/dict/bytes Kafka record
  - [ ] `safe_decode_and_parse(element)` — decode bytes + JSON parse with logging
  - [ ] `attach_event_name(payload)` — wrap with eventName
  - [ ] `build_raw_event(record)` — create RawEvent envelope (filter Schema A, keep Schema B)
- [ ] พัฒนา `bq_transformers.py` — BigQuery table extraction:
  - [ ] `unwrap_avro_value()` / `unwrap_avro_array()` — Avro union unwrapping
  - [ ] `_parse_timestamp()` — unix seconds/millis/ISO 8601 → Bangkok +7h Beam Timestamp
  - [ ] `_parse_numeric()` — string → Decimal for NUMERIC fields
  - [ ] `_safe_str()` — safe string conversion
  - [ ] `_extract_header_fields()` — 19 shared header fields extraction
  - [ ] `to_receipt_row(raw_event)` → 1 row per event (receipt-level)
  - [ ] `to_sku_rows(raw_event)` → N rows per event (item-level denormalization)
  - [ ] `to_tender_rows(raw_event)` → M rows per event (payment-level denormalization)
- [ ] พัฒนา `validators.py` — value & field validation helpers

#### Pipeline Architecture

- [ ] ออกแบบ streaming pipeline flow:
  ```
  Kafka → ExtractValue → DecodeParse → AttachEventName → BuildRawEvent
    ├─ Per-topic Iceberg write (source layer)
    └─ Flatten all → FlatMap(to_receipt/sku/tender) → BQ CDC write (refined layer)
  ```
- [ ] Implement fan-out: single Kafka read → 2 Iceberg writes + 3 BigQuery writes
- [ ] Implement composition root pattern (`main.py`)
- [ ] Implement `PipelineBuilder` orchestrator

#### DoFn Development

- [ ] พัฒนา `ExtractValueDoFn` — extract value bytes with metrics counters
- [ ] พัฒนา `DecodeParseDoFn` — decode & JSON parse with progress logging
- [ ] พัฒนา `AttachEventNameDoFn` — wrapper for `attach_event_name()`
- [ ] พัฒนา `BuildRawEventDoFn` — wrapper for `build_raw_event()` with dropped metrics

#### Data Sink

- [ ] Implement IcebergSink with BLMS REST Catalog
- [ ] Implement BigQuery CDC sink (3 tables, all CDC mode with primary keys)
- [ ] Configure per-table partition + clustering

#### Configuration

- [ ] ออกแบบ Pydantic-based config DTOs (`settings.py`):
  - [ ] `DataflowCliOptions` — base64-encoded YAML from CLI
  - [ ] `RefinedTableConfig` — per-table config with CDC validation
  - [ ] `DataflowConfigDto` — top-level validated DTO
- [ ] เขียน `base.yaml`, `stg.yaml`, `prod.yaml`
- [ ] Implement `ConfigurationAdapter` — loads config + secrets → `PipelineConfig`

#### Testing (126 tests)

- [ ] เขียน tests สำหรับ transformers (`test_transformers.py` — 31 tests):
  - [ ] Kafka extraction, event detection, raw event building
- [ ] เขียน tests สำหรับ bq_transformers (`test_bq_transformers.py` — 61 tests):
  - [ ] Avro unwrapping, timestamp/numeric parsing, table extraction
- [ ] เขียน tests สำหรับ validators (`test_validators.py` — 14 tests)
- [ ] เขียน tests สำหรับ DoFns (`test_dofns.py` — 8 tests):
  - [ ] Input validation, process behavior, metrics
- [ ] เขียน tests สำหรับ settings (`test_settings.py` — 35 tests):
  - [ ] Pydantic validation, missing fields, invalid enums, CDC constraints
- [ ] เขียน test fixtures (`conftest.py` — sample payloads, raw events, avro wrapped)

#### Infrastructure

- [ ] Terraform: GCS buckets (source warehouse, config), BigQuery datasets, BigLake catalog, GAR, Secret Manager, Dataform
- [ ] GitLab CI: linter, test, create-image, sonar-scan, deploy
- [ ] Multi-stage Dockerfile (Python 3.12 + Java 17 for Kafka cross-language)

---

## 8. Cross-Project Shared Work

### 8.1 Iceberg Writer Refactoring (D-H Pattern)

สร้าง shared pattern ที่ใช้เหมือนกันใน 4 collectors (loyalty x3 + sales):

- [ ] ออกแบบ `BlmsCatalogConfig` (frozen dataclass) — BLMS REST catalog connection
- [ ] ออกแบบ `ManagedIcebergWriteConfig` (frozen dataclass) — table name, partition, frequency
- [ ] พัฒนา `iceberg_writer.py` — `write_to_iceberg(config, ...)` shared function
- [ ] พัฒนา `IcebergSink` — composite PTransform wrapper (config, schema, row_mapper)
- [ ] Verify identical pattern across all collectors

### 8.2 Option B Migration (BLMS REST Catalog)

- [ ] Migrate Iceberg writes: Hadoop Catalog → BLMS REST Catalog (vended credentials)
- [ ] Verify YAML → Settings → ConfigAdapter → BlmsCatalogConfig → ManagedIcebergWriteConfig → IcebergSink → managed.Write path
- [ ] Preserve Hadoop as comments for rollback
- [ ] BQ table creation (Option B part): implemented code, then disabled (waiting for terraform from transaction/ team)
- [ ] Implement `bq_metadata_refresh.py` x3 — refresh DoFn (module kept for future use)
- [ ] Clean deploy.py x3 — remove Option B code, keep native BQ only

### 8.3 deploy.py Standardization

- [ ] Rewrite deploy.py for all 3 loyalty collectors (identical pattern):
  - [ ] ~2290 lines → ~370 lines each
  - [ ] Remove: PyIceberg imports, Iceberg creation, Option B methods, Java tools
  - [ ] Keep: native BQ table handling (CREATE, ALTER, backup/restore, schema compare)
  - [ ] Add: `if not content: continue` to skip empty JSON files
- [ ] Delete 6 empty (0B) JSON source table placeholders
- [ ] Clean CI (.gitlab-ci.yml): remove PyIceberg install + ICEBERG_CREATE_METHOD

### 8.4 GitLab CI/CD

- [ ] Implement multi-stage CI: build (linter + test + image) → deploy STG → deploy PROD
- [ ] Implement 4-destination image build (STG active + PROD commented)
- [ ] Implement deploy:prod scripts (prepare_dataflow_config, prepare_dataflow_spec, deploy_dataflow)
- [ ] Refactor sonar/gitleaks/trivy to shared extends
- [ ] Members: streaming deploy with cancel (should upgrade to drain-first)
- [ ] Tiers/M-T-H: batch deploy

### 8.5 Terraform Per-Collector

- [ ] GCS buckets per collector (`infrastructure/{collector}/bucket.tf`)
- [ ] GAR repos per collector (`infrastructure/{collector}/artifact.tf`)
- [ ] BigLake metastore IAM per collector (`infrastructure/{collector}/biglake-metastore.tf`)
- [ ] Secret Manager per collector
- [ ] Common infra: BigLake catalog + source bucket + SA IAM (`common/GCP/`)

---

## 9. เปรียบเทียบกับ CV 2024 — Skills ใหม่ที่ได้เพิ่ม

### Skills ที่มีอยู่แล้วใน CV 2024 และยังใช้:
| CV 2024 Skill | ใช้ในโปรเจกต์นี้อย่างไร |
|---------------|-------------------------|
| Python | ภาษาหลักทุก pipeline |
| ETL Development | ออกแบบ + สร้าง data pipeline ทั้งหมด |
| Data Pipeline Design | 5 pipelines (streaming + batch) |
| Data Modeling | BigQuery + Iceberg schema design |
| Data Validation | Type conversion, schema validation, unit testing |
| Kafka | Kafka consumer (Confluent Cloud, SASL_SSL, Schema Registry) |
| Unit Testing | 647+ tests across 5 projects |
| Integration Testing | Pipeline integration tests |
| Git (GitLab) | GitLab CI/CD, merge requests |
| PostgreSQL | Members-tiers-history-collector source |

### Skills ใหม่ที่ได้เพิ่มจากโปรเจกต์นี้:

| New Skill | รายละเอียด |
|-----------|-----------|
| **Apache Beam** | Data processing framework (DoFn, PTransform, Pipeline, Windowing, Triggers, managed.Write) |
| **Google Cloud Dataflow** | Streaming + Batch job deployment (Flex Templates) |
| **BigQuery (Advanced)** | Schema design, CDC writes, STORAGE_WRITE_API, partitioning, clustering, primary keys |
| **Apache Iceberg** | BigLake REST Catalog (BLMS), PyArrow schemas, partition management |
| **BigLake Metastore** | BLMS REST Catalog setup + IAM |
| **Terraform** | IaC for GCP resources (GCS, GAR, BigLake, IAM, Secret Manager) |
| **GitLab CI/CD** | Multi-stage pipeline design (vs Jenkins/GitHub Workflow in CV) |
| **Docker / Kaniko** | Multi-stage Dockerfile, Flex Template images |
| **Google Secret Manager** | Per-service secret management |
| **Cloud Scheduler** | Batch job scheduling |
| **Avro** | Confluent Schema Registry, Avro deserialization, union unwrapping |
| **CDC Pattern** | Change Data Capture (UPSERT + DELETE), primary key dedup |
| **Hexagonal Architecture** | Ports/Adapters design pattern |
| **Domain-Driven Design** | Pure domain models + transformers, composition root |
| **Pydantic** | Configuration validation, DTO models |
| **ruff / mypy** | Modern Python linting + type checking (vs older tools) |
| **pre-commit** | Git hooks for code quality |
| **SonarQube** | Code quality analysis |
| **uv** | Fast Python package management |

### สรุป Impact:
- **5 data pipelines** designed and implemented end-to-end
- **647+ unit tests** written and maintained
- **8 BigQuery refined tables** + **8 Iceberg source tables** designed
- **Streaming + Batch** pipeline patterns
- **CDC pattern** (UPSERT + DELETE) for real-time data consistency
- **Multi-schema** message handling (Schema A/B/C + Avro)
- **Full CI/CD** pipeline with automated testing, linting, security scanning
- **Infrastructure as Code** with Terraform

---

> **Next steps**: เกลาเอกสารนี้ร่วมกัน — ลบ part ที่ไม่ได้ทำจริง, เพิ่ม part ที่ขาด, ปรับ detail ให้ตรงกับ scope จริง
