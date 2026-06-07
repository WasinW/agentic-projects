# The1 Data Platform - Data Pipeline Architecture

> **Version:** 1.0.0
> **Last Updated:** 2026-02-20
> **Status:** Production Documentation
> **Scope:** All data pipelines across The1 Data Platform

---

## Table of Contents

1. [Platform Overview](#1-platform-overview)
2. [Pipeline Types](#2-pipeline-types)
3. [Streaming Pipelines (Dataflow)](#3-streaming-pipelines-dataflow)
4. [Batch Pipelines (Dataflow)](#4-batch-pipelines-dataflow)
5. [Cloud Run Pipelines](#5-cloud-run-pipelines)
6. [Customer Profile Pipeline (Insight)](#6-customer-profile-pipeline-insight)
7. [Messaging Pipelines](#7-messaging-pipelines)
8. [Code Architecture Pattern (Hexagonal)](#8-code-architecture-pattern-hexagonal)
9. [Configuration System](#9-configuration-system)
10. [Iceberg Write Path (BLMS REST Catalog)](#10-iceberg-write-path-blms-rest-catalog)
11. [BigQuery Write Patterns](#11-bigquery-write-patterns)
12. [Multi-Table Fan-Out Pattern](#12-multi-table-fan-out-pattern)
13. [Deployment and CI/CD](#13-deployment-and-cicd)
14. [Key Technical Patterns](#14-key-technical-patterns)
15. [Per-Collector Summary](#15-per-collector-summary)
16. [Infrastructure Overview](#16-infrastructure-overview)

---

## 1. Platform Overview

The1 Data Platform ingests, transforms, and stores data from multiple business domains. Each domain has dedicated data collectors that follow consistent architectural patterns while adapting to domain-specific requirements.

### High-Level Platform Architecture

```mermaid
graph TB
    subgraph Sources["Data Sources"]
        KAFKA["Confluent Kafka<br/>(SASL/SSL)"]
        PUBSUB["Google Pub/Sub"]
        API["REST APIs<br/>(Loyalty, Rewards)"]
        PG["PostgreSQL RDS<br/>(via SSH Tunnel)"]
        BT["Cloud Bigtable"]
    end

    subgraph Compute["Compute Layer"]
        DF_STREAM["Dataflow Streaming<br/>(Apache Beam)"]
        DF_BATCH["Dataflow Batch<br/>(Apache Beam)"]
        CR["Cloud Run<br/>(FastAPI)"]
    end

    subgraph Storage["Storage Layer"]
        ICE["Apache Iceberg<br/>(GCS + BigLake Metastore)"]
        BQ["BigQuery<br/>(Storage Write API)"]
        GCS["Google Cloud Storage<br/>(Parquet / Raw)"]
        S3["AWS S3<br/>(Parquet Export)"]
    end

    subgraph Orchestration["Orchestration"]
        SCHED["Cloud Scheduler"]
        GITLAB["GitLab CI/CD"]
    end

    KAFKA --> DF_STREAM
    PUBSUB --> DF_STREAM
    API --> DF_BATCH
    API --> CR
    PG --> DF_BATCH
    BT --> DF_STREAM

    DF_STREAM --> ICE
    DF_STREAM --> BQ
    DF_STREAM --> GCS
    DF_STREAM --> S3
    DF_BATCH --> ICE
    DF_BATCH --> BQ
    CR --> GCS

    SCHED --> DF_BATCH
    SCHED --> CR
    GITLAB --> DF_STREAM
    GITLAB --> DF_BATCH
```

### Domain Organization

```
realproject/
+-- loyalty/           # Loyalty domain (members, tiers, purchases, transactions)
+-- sale/              # Sales domain (sales-collector)
+-- insight/           # Insight domain (customer-profile)
+-- message/           # Messaging domain (messages, communications, templates)
+-- common/            # Shared libraries (common.beam, common_cloudrun)
+-- terraform/         # Infrastructure-as-code
```

---

## 2. Pipeline Types

The platform uses four distinct pipeline patterns, chosen based on data source characteristics and latency requirements.

| Pipeline Type | Runtime | Trigger | Latency | Use Cases |
|---------------|---------|---------|---------|-----------|
| **Streaming (Dataflow)** | Apache Beam | Continuous (Kafka/Pub/Sub) | Seconds-minutes | members, transactions, purchases, sales, customer-profile, messages |
| **Batch (Dataflow)** | Apache Beam | Cloud Scheduler (daily) | Daily | tiers-collector, members-tiers-history |
| **Cloud Run** | FastAPI | Cloud Scheduler (daily) | Daily | rewards-collector |
| **Init Data (Dataflow Batch)** | Apache Beam | GitLab CI manual trigger | One-time | Initial data load for any collector |

```mermaid
graph LR
    subgraph "Pipeline Patterns"
        direction TB
        A["Streaming<br/>Kafka/PubSub -> Dataflow -> Iceberg + BQ"]
        B["Batch<br/>Scheduler -> Dataflow -> Iceberg + BQ"]
        C["Cloud Run<br/>Scheduler -> HTTP -> API -> GCS"]
        D["Init Data<br/>GitLab CI -> Dataflow Batch -> Iceberg + BQ"]
    end
```

---

## 3. Streaming Pipelines (Dataflow)

### 3.1 General Streaming Pattern

All Kafka-based streaming pipelines follow this pattern:

```
Confluent Kafka (SASL/SSL)
  -> KafkaReaderAdapter (from common.beam library) / ReadFromKafka (native)
  -> ExtractValueDoFn (extract bytes from Kafka record)
  -> DecodeAvroOrJsonDoFn / DecodeParseDoFn (JSON/Avro decode)
  -> AttachEventNameDoFn (add topic name as eventName)
  -> BuildRawEventDoFn (wrap in envelope: eventId, source, eventName, timestamp, payload)
  -> WindowInto(FixedWindows)
  -> Fan-out:
    +-> IcebergSink / GcsIcebergWriter -> managed.Write(ICEBERG) -> GCS (Iceberg via BigLake REST)
    +-> Map/FlatMap transformers -> BigQuerySink / WriteToBigQuery (Storage Write API)
```

### 3.2 Sales Collector (Streaming)

**Source:** Kafka topic `loyalty.sales.created`
**Output:** 1 Iceberg table (raw_sales) + 3 BigQuery tables (sales_receipt, sales_sku, sales_tender)

```mermaid
graph TD
    subgraph Source["Kafka Source"]
        K["Confluent Kafka<br/>topic: loyalty.sales.created"]
    end

    subgraph Ingest["Ingestion Layer"]
        KR["KafkaReaderAdapter<br/>(common.beam)"]
        W["WindowInto<br/>(FixedWindows 5s)"]
        AE["AttachEventNameDoFn"]
        BR["BuildRawEventDoFn"]
    end

    subgraph SourceLayer["Source Layer (Iceberg)"]
        ICE["GcsIcebergWriter<br/>managed.Write(ICEBERG)<br/>table: source.raw_sales"]
    end

    subgraph RefinedLayer["Refined Layer (BigQuery)"]
        TR["to_receipt_row<br/>(beam.Map)"]
        TS["to_sku_rows<br/>(beam.FlatMap)"]
        TT["to_tender_rows<br/>(beam.FlatMap)"]
        BQR["BigQueryWriterAdapter<br/>sales_receipt"]
        BQS["BigQueryWriterAdapter<br/>sales_sku"]
        BQT["BigQueryWriterAdapter<br/>sales_tender"]
    end

    K --> KR
    KR --> W
    W --> AE
    AE --> BR

    BR -->|"all events"| ICE

    BR -->|"1:1 map"| TR --> BQR
    BR -->|"1:N flatmap"| TS --> BQS
    BR -->|"1:M flatmap"| TT --> BQT

    style Source fill:#e8f5e9
    style SourceLayer fill:#e3f2fd
    style RefinedLayer fill:#fff3e0
```

**Key characteristics:**
- Window size: 5 seconds
- Iceberg triggering frequency: 300 seconds (5 minutes)
- Fan-out: 1 receipt per event, N SKU rows per event, M tender rows per event
- BQ partitioning: MONTH on `trans_date`, with clustering on partner_code, member_number

### 3.3 Members Collector (Streaming)

**Source:** 2 Kafka topics (`loyalty.members.upgraded`, `loyalty.members.downgraded`)
**Output:** Up to 4 Iceberg tables + 4 BigQuery tables
**Special:** API enrichment (Loyalty API for member tier + tier maintenance data)

```mermaid
graph TD
    subgraph Source["Kafka Sources"]
        K1["Kafka: loyalty.members.upgraded"]
        K2["Kafka: loyalty.members.downgraded"]
    end

    subgraph PerTopic["Per-Topic Processing"]
        direction TB
        EV1["ExtractValue -> Decode -> Window"]
        EV2["ExtractValue -> Decode -> Window"]
        AE1["AttachEventName -> BuildRawEvent"]
        AE2["AttachEventName -> BuildRawEvent"]
    end

    subgraph IcebergSinks["Iceberg Source Layer"]
        ICE_UP["IcebergSink<br/>tier_events_upgraded"]
        ICE_DN["IcebergSink<br/>tier_events_downgraded"]
        ICE_MT["IcebergSink<br/>member_tier"]
        ICE_TM["IcebergSink<br/>member_tier_maintenance"]
    end

    subgraph BQSinks["BigQuery Refined Layer"]
        BQ_UP["BigQuerySink<br/>tier_events_upgraded"]
        BQ_DN["BigQuerySink<br/>tier_events_downgraded"]
        BQ_MT["BigQuerySink<br/>member_tier"]
        BQ_TM["BigQuerySink<br/>tier_maintenance"]
    end

    subgraph APIEnrich["API Enrichment Branch"]
        MERGE["Flatten (Merge Topics)"]
        EXTRACT["ExtractMemberIdDoFn"]
        DEDUP["DeduplicateMemberIdsDoFn"]
        FETCH_MT["FetchMemberTierDoFn<br/>(Loyalty API)"]
        FETCH_TM["FetchTierMaintenanceDoFn<br/>(Loyalty API)"]
    end

    K1 --> EV1 --> AE1
    K2 --> EV2 --> AE2

    AE1 -->|"upgraded"| ICE_UP
    AE1 -->|"upgraded"| BQ_UP
    AE2 -->|"downgraded"| ICE_DN
    AE2 -->|"downgraded"| BQ_DN

    AE1 --> MERGE
    AE2 --> MERGE
    MERGE --> EXTRACT --> DEDUP

    DEDUP --> FETCH_MT --> ICE_MT
    FETCH_MT --> BQ_MT
    DEDUP --> FETCH_TM --> ICE_TM
    FETCH_TM --> BQ_TM

    style Source fill:#e8f5e9
    style IcebergSinks fill:#e3f2fd
    style BQSinks fill:#fff3e0
    style APIEnrich fill:#f3e5f5
```

**Key characteristics:**
- Window size: 60 seconds
- Per-topic Iceberg/BQ writes (upgraded vs downgraded have different schemas)
- API enrichment: Extracts member IDs from Kafka events, deduplicates, then calls Loyalty API
- Avro/JSON auto-detection with Confluent Schema Registry support
- Supports CDC mode for member_tier table (prod uses UPSERT with primary key `memberTierId`)
- Initial data load mode: `job_type=initial_data` reads from BQ staging tables

### 3.4 Purchases Collector (Streaming)

**Source:** Kafka topics (2 topics for purchases)
**Output:** 1 Iceberg table + 3 BigQuery tables + Pub/Sub (filtered)

```mermaid
graph TD
    subgraph Source["Kafka Source"]
        K["Confluent Kafka<br/>(purchases topics)"]
    end

    subgraph Process["Processing"]
        KR["KafkaReaderAdapter"]
        W["WindowInto(FixedWindows)"]
        AE["AttachEventNameDoFn"]
        BR["BuildRawEventDoFn"]
    end

    subgraph Sinks["Output Sinks"]
        PS["PubSubSink<br/>(filtered: purchases_created only)"]
        ICE["GcsIcebergWriter<br/>(all events)"]
        BQ_R["BigQueryWriterAdapter<br/>purchases_receipt"]
        BQ_D["BigQueryWriterAdapter<br/>purchases_detail"]
        BQ_P["BigQueryWriterAdapter<br/>purchases_payment"]
    end

    K --> KR --> W --> AE --> BR

    BR -->|"Filter: is_purchases_created"| PS
    BR -->|"all events"| ICE
    BR -->|"Map: to_receipt_row"| BQ_R
    BR -->|"FlatMap: to_detail_rows"| BQ_D
    BR -->|"FlatMap: to_payment_rows"| BQ_P

    style Source fill:#e8f5e9
    style Sinks fill:#fff3e0
```

**Key characteristics:**
- Same fan-out pattern as sales-collector (receipt + detail + payment)
- Additional Pub/Sub output for downstream event consumers (filtered to purchases_created events only)
- Uses common.beam shared library for Kafka reader and BigQuery writer

### 3.5 Transactions Collector (Streaming)

**Source:** Kafka topics (3 topics: earned, burned, cancelled)
**Output:** GCS Parquet + RAW BQ + REFINED BQ (topic-routed) + SEM BQ + Iceberg (optional)

```mermaid
graph TD
    subgraph Source["Kafka Source"]
        K["Confluent Kafka<br/>3 topics: earned, burned, cancelled"]
    end

    subgraph Process["Processing"]
        RFK["ReadFromKafka<br/>(with_metadata=true)"]
        DEC["DecodeKafkaValueSafelyDoFn<br/>(Avro/Schema Registry)"]
        TOPIC["TopicEnricherDoFn<br/>(add topic_source)"]
        WIN["WindowInto(FixedWindows)"]
        PARSE["ParseJsonSafelyDoFn"]
        NORM["NormalizeToRowDoFn"]
        REF["ToRefinedDoFn"]
    end

    subgraph Sinks["5 Output Sinks"]
        S1["Sink 1: RAW Parquet<br/>(GCS, dynamic partitioning)"]
        S2["Sink 2: RAW BigQuery<br/>(Storage Write API)"]
        S3["Sink 3: REFINED BigQuery<br/>(topic-routed to N tables)"]
        S4["Sink 4: SEM BigQuery<br/>(semantic/public table)"]
        S5["Sink 5: Iceberg<br/>(Managed I/O, optional)"]
    end

    K --> RFK --> DEC --> TOPIC --> WIN --> PARSE --> NORM

    NORM --> S1
    NORM --> S2
    NORM --> REF
    NORM --> S5

    REF --> S3
    REF --> S4

    style Source fill:#e8f5e9
    style Process fill:#f5f5f5
    style Sinks fill:#fff3e0
```

**Key characteristics:**
- Multi-topic with metadata extraction (topic name determines routing)
- Avro deserialization with Confluent Schema Registry
- Topic-based routing: different topics route to different refined BQ tables
- 5 parallel output sinks (most complex pipeline)
- Supports both BigLake REST and Hadoop Iceberg catalog types
- Kafka connectivity validation at startup (DNS resolution + preflight check)

---

## 4. Batch Pipelines (Dataflow)

### 4.1 Tiers Collector (Batch)

**Source:** Loyalty Tiers Master REST API
**Trigger:** Cloud Scheduler (1AM BKK daily)
**Output:** 1 Iceberg table + 1 BigQuery table

```mermaid
graph TD
    subgraph Trigger["Trigger"]
        SCHED["Cloud Scheduler<br/>1AM BKK daily"]
    end

    subgraph Pipeline["Dataflow Batch Pipeline"]
        FLEX["Dataflow Flex Template<br/>Launch"]
        CREATE["beam.Create([None])<br/>(single trigger)"]
        FETCH["FetchTiersDoFn<br/>(Loyalty Tiers Master API<br/>via Secret Manager credentials)"]
    end

    subgraph Output["Output"]
        ICE["IcebergSink<br/>source.tiers"]
        EXTRACT["ExtractTiersMasterPayloadDoFn"]
        BQ["BigQuerySink<br/>refined.tiers_master<br/>(batch write mode)"]
    end

    SCHED --> FLEX --> CREATE --> FETCH

    FETCH -->|"all tiers"| ICE
    FETCH -->|"extract payload"| EXTRACT --> BQ

    style Trigger fill:#e8f5e9
    style Pipeline fill:#f5f5f5
    style Output fill:#fff3e0
```

**Key characteristics:**
- Pure batch: no Kafka, no PeriodicImpulse, no streaming
- Single trigger via `beam.Create([None])` -- fetches all tiers once
- API authentication via Secret Manager (clientId/clientSecret)
- Supports both manual (PyIceberg) and managed_io (Beam Managed I/O) Iceberg writers
- BQ refresh (Option B) disabled pending infrastructure readiness

### 4.2 Members Tiers History Collector (Batch)

**Source:** PostgreSQL RDS (via SSH tunnel)
**Trigger:** Cloud Scheduler (1AM BKK daily, with process_date=yesterday)
**Output:** 1 Iceberg table + 1 BigQuery table

```mermaid
graph TD
    subgraph Trigger["Trigger"]
        SCHED["Cloud Scheduler<br/>1AM BKK daily<br/>process_date=yesterday"]
    end

    subgraph Pipeline["Dataflow Batch Pipeline"]
        FLEX["Dataflow Flex Template<br/>Launch"]
        QC["beam.Create([query_config])<br/>(query + process_date)"]
        PG["ReadFromPostgresDoFn<br/>(SSH tunnel to RDS<br/>batch_size configurable)"]
    end

    subgraph Output["Output"]
        ICE["IcebergSink<br/>source.members_tiers_history"]
        CONV["beam.Map(convert_for_bigquery)"]
        BQ["BigQuerySink<br/>refined.members_tiers_history<br/>(batch write mode)"]
    end

    SCHED --> FLEX --> QC --> PG

    PG -->|"all records"| ICE
    PG -->|"convert timestamps"| CONV --> BQ

    style Trigger fill:#e8f5e9
    style Pipeline fill:#f5f5f5
    style Output fill:#fff3e0
```

**Key characteristics:**
- SSH tunnel to PostgreSQL RDS (host, port, user, private_key from config)
- SQL query template with `{prev_date}` placeholder resolved to process_date
- process_date: CLI `--process_date` or default to yesterday
- BQ write_disposition configurable (WRITE_APPEND default)
- Initial data load mode: `job_type=initial_data` reads from BQ staging tables

### 4.3 Initial Data Load (Batch, All Collectors)

Used for one-time data backfill. Available for members-collector and members-tiers-history-collector.

```mermaid
graph TD
    subgraph Trigger["Trigger"]
        CI["GitLab CI<br/>TRIGGER_INIT_DATA_LOAD=1"]
    end

    subgraph Pipeline["Dataflow Batch Pipeline"]
        CONFIG["Init Data Config<br/>(YAML: scripts, targets,<br/>condition_parts)"]
        BQ_READ["ReadFromBigQuery<br/>(SQL from resources/init/)"]
        BQ_READ2["ReadFromBigQuery<br/>(parallel branches<br/>per condition_part)"]
    end

    subgraph Output["Output"]
        ICE_WRITE["write_to_iceberg<br/>(batch, preserves etlLoadTime)"]
        BQ_WRITE["WriteToBigQuery<br/>(WRITE_APPEND)"]
    end

    CI --> CONFIG
    CONFIG -->|"source tables"| BQ_READ --> ICE_WRITE
    CONFIG -->|"refined tables"| BQ_READ2 --> BQ_WRITE

    style Trigger fill:#e8f5e9
    style Output fill:#fff3e0
```

**Key characteristics:**
- SQL files embedded in Docker image (`resources/init/`)
- Supports `condition_parts` for parallel branch splitting (handles large datasets)
- Preserves `etlLoadTime` from source (passthrough, not regenerated)
- Creates BLMS catalog config without triggering_frequency (batch mode)

---

## 5. Cloud Run Pipelines

### 5.1 Rewards Collector (Cloud Run)

**Runtime:** FastAPI on Cloud Run
**Trigger:** Cloud Scheduler (daily HTTP POST)
**Output:** GCS (Parquet files)

```mermaid
graph TD
    subgraph Trigger["Trigger"]
        SCHED["Cloud Scheduler<br/>Daily"]
    end

    subgraph CloudRun["Cloud Run (FastAPI)"]
        HTTP["POST /trigger<br/>(HTTP endpoint)"]
        AUTH["ApiAuthAdapter<br/>(Keycloak OAuth2)"]
        SRC["ApiSourceAdapter<br/>(REST API polling<br/>with pagination)"]
        UC["CollectUseCase<br/>(orchestrator)"]
    end

    subgraph Output["Output"]
        GCS["GcsParquetAdapter<br/>(GCS bucket)"]
    end

    SCHED -->|"POST"| HTTP
    HTTP --> UC
    UC --> AUTH
    UC --> SRC
    SRC -->|"paginated results"| UC
    UC --> GCS

    style Trigger fill:#e8f5e9
    style CloudRun fill:#f5f5f5
    style Output fill:#fff3e0
```

**Key characteristics:**
- Clean Architecture / Hexagonal pattern with Ports and Adapters
- YAML-driven pipeline configuration (sources, destinations, auth profiles)
- Auth via Keycloak (OAuth2 client_credentials flow)
- Secrets from GCP Secret Manager
- Multiple pipelines configurable from single YAML
- Destination type: `gcs_parquet` (writes Parquet files to GCS bucket)
- Uses `common_cloudrun` shared library

---

## 6. Customer Profile Pipeline (Insight)

### 6.1 Overview

The customer profile pipeline is the most complex streaming pipeline, with CDC writes to BigQuery, S3 Parquet exports, Iceberg merge operations, and consent processing.

**Source:** Pub/Sub (ms-personas events) + Bigtable (profiles, consents)
**Output:** BigQuery CDC + AWS S3 (Parquet) + Iceberg (periodic merge)

```mermaid
graph TD
    subgraph Sources["Input Sources"]
        PS["Pub/Sub<br/>(ms-personas events)"]
        BT["Bigtable<br/>(profiles, consents)"]
        MAP["BigQuery<br/>(mapping tables)"]
    end

    subgraph MainPipeline["Main Pipeline (Steps 1-11)"]
        direction TB
        MR["Step 1: MappingRefreshDoFn<br/>(periodic refresh)"]
        READ["Step 2: ReadFromPubSub"]
        EXT["Step 3: ExtractPersonasDoFn"]
        FETCH["Step 4: FetchFromBigtableDoFn"]
        FILT["Step 5: Filter<br/>(empty PK, empty family)"]
        TRANS["Step 6-7: TransformSchemasDoFn"]
    end

    subgraph OutputSinks["Output Sinks"]
        CDC["Step 8: BigQuery CDC<br/>(ms_personas - UPSERT<br/>via Storage Write API)"]
        S3P["Step 10: AWS S3<br/>(Parquet - hourly windowed)"]
        ICE["Step 11: Iceberg Merge<br/>(periodic SyncToIcebergDoFn)"]
        DLQ["DLQ: BigQuery<br/>(dead letter queue)"]
    end

    subgraph ConsentPipeline["Consent Processing (Steps 12-14)"]
        IMP["Step 12: PeriodicImpulse<br/>(every 5 min)"]
        SQL["Step 13: SQLSubmitDoFn<br/>(MERGE queries)"]
        EXPORT["Step 14: SQLExportDoFn<br/>+ CopyGCSToS3DoFn"]
    end

    PS --> READ
    MAP --> MR
    READ --> EXT
    EXT --> FETCH
    BT --> FETCH
    FETCH --> FILT --> TRANS

    TRANS --> CDC
    TRANS --> S3P
    TRANS --> ICE

    IMP --> SQL
    SQL -->|"consents_history"| EXPORT
    SQL -->|"suppression"| EXPORT

    style Sources fill:#e8f5e9
    style MainPipeline fill:#f5f5f5
    style OutputSinks fill:#fff3e0
    style ConsentPipeline fill:#f3e5f5
```

### 6.2 Consent Processing Flow

```mermaid
graph TD
    IMP["PeriodicImpulse<br/>(every 5 min)"]
    WIN["ConsentLoadWindow<br/>(FixedWindows 5 min)"]

    IMP --> WIN

    WIN -->|"Signal A"| LOAD_C["LoadConsentsHistory<br/>(SQLSubmitDoFn: MERGE)"]
    WIN -->|"Signal B"| LOAD_S["LoadSuppression<br/>(SQLSubmitDoFn: MERGE)"]

    LOAD_C --> INT["internal_partner"]
    LOAD_C --> EXT["external_partner"]

    subgraph HourlyExport["Hourly Export"]
        EXP_C["SQLExportDoFn<br/>consents_history -> GCS"]
        EXP_S["SQLExportDoFn<br/>suppression -> GCS"]
        COPY_C["CopyGCSToS3DoFn<br/>-> AWS S3"]
        COPY_S["CopyGCSToS3DoFn<br/>-> AWS S3"]
    end

    LOAD_C -->|"every 1 hour"| EXP_C --> COPY_C
    LOAD_S -->|"every 1 hour"| EXP_S --> COPY_S

    style HourlyExport fill:#fff3e0
```

**Key characteristics:**
- V3 architecture: Hexagonal (Ports & Adapters) + V2 DoFn pattern (self-contained)
- Flex Template deployment (Docker-based)
- BigQuery CDC: Storage Write API with UPSERT semantics
- AWS S3: Parquet files, hourly windowed, cross-cloud export
- Iceberg merge: Periodic sync from BQ to BigLake Iceberg history table
- Consent processing: SQL-based MERGE queries, GCS-to-S3 copy
- Rate-limited logging to prevent log quota exhaustion
- SQL source switch: GCS bucket or embedded resources

---

## 7. Messaging Pipelines

### 7.1 Messages Collector (Streaming)

**Source:** Kafka (messaging topics)
**Output:** Iceberg + BigQuery + Bigtable + Pub/Sub

```mermaid
graph TD
    subgraph Source["Kafka Source"]
        K["Confluent Kafka<br/>(messaging topics)"]
    end

    subgraph Process["Processing"]
        KR["KafkaReaderAdapter<br/>(common.beam)"]
        PROC["Decode + Transform"]
    end

    subgraph Sinks["Output Sinks"]
        ICE["GcsIcebergWriterAdapter<br/>(Iceberg via BLMS)"]
        BQ["BigQueryWriterAdapter<br/>(refined layer)"]
        BT["BigtableAdapter<br/>(BigtableWriterAdapter)"]
        PS["PubSubWriterAdapter<br/>(event notification)"]
    end

    K --> KR --> PROC

    PROC --> ICE
    PROC --> BQ
    PROC --> BT
    PROC --> PS

    style Source fill:#e8f5e9
    style Sinks fill:#fff3e0
```

**Key characteristics:**
- 4 output sinks (most diverse output set: Iceberg, BQ, Bigtable, Pub/Sub)
- Bigtable used for real-time lookup/enrichment downstream
- Uses common.beam shared library for Kafka reader, BigQuery writer, and Bigtable writer
- Pub/Sub for downstream event consumers

---

## 8. Code Architecture Pattern (Hexagonal)

ALL Python Dataflow pipelines follow hexagonal architecture (Ports & Adapters), with the Composition Root pattern in `main.py`.

### 8.1 Standard Directory Structure

```
{collector}/
+-- src/
|   +-- main.py                          # Composition Root (wires everything)
|   +-- domain/                          # Pure business logic (no I/O)
|   |   +-- models.py                    # TypedDict data models
|   |   +-- schemas.py                   # PyArrow + BigQuery schemas
|   |   +-- transformers.py              # Pure transform functions
|   |   +-- validators.py               # Validation helpers
|   |   +-- config/
|   |   |   +-- pipeline_config.py       # Runtime config (Pydantic/dataclass)
|   |   |   +-- bigquery_*_config.py     # BQ config with to_table_config() factory
|   |   +-- blms_catalog_config.py       # BLMS REST catalog config (frozen dataclass)
|   |   +-- managed_iceberg_write_config.py  # Iceberg write config (frozen dataclass)
|   +-- adapters/
|   |   +-- input/
|   |   |   +-- configuration/
|   |   |       +-- settings.py          # Pydantic DTOs (validate YAML config)
|   |   |       +-- configuration_adapter.py  # YAML -> PipelineConfig loader
|   |   |       +-- secret_adapter.py    # GCP Secret Manager client
|   |   |       +-- logging_adapter.py   # Structured logging setup
|   |   +-- output/
|   |       +-- gcs/
|   |       |   +-- biglake_metastore_config.py  # BLMS catalog config (frozen)
|   |       |   +-- gcs_biglake_iceberg_writer_config.py  # Iceberg write config
|   |       |   +-- gcs_biglake_iceberg_writer.py  # IcebergIO PTransform
|   |       +-- bigquery/
|   |       |   +-- bigquery_writer_config.py
|   |       |   +-- bigquery_writer.py   # WriteToBigQuery PTransform
|   |       +-- iceberg_sink.py          # IcebergSink(config, schema, row_mapper)
|   |       +-- iceberg_writer.py        # write_to_iceberg() helper
|   |       +-- bigquery_sink.py         # BigQuerySink PTransform
|   +-- application/
|       +-- pipeline/
|           +-- builder.py               # PipelineBuilder orchestration
|           +-- dofns.py                 # DoFn implementations (Beam-specific)
|           +-- transform_dofns.py       # Payload extraction DoFns
|           +-- api_dofns.py             # API fetch DoFns (optional)
+-- config/
|   +-- base.yaml                        # Common settings (all environments)
|   +-- stg.yaml                         # STG overrides
|   +-- prod.yaml                        # PROD overrides
+-- tests/
+-- Dockerfile
+-- pyproject.toml
+-- .gitlab-ci.yml
```

### 8.2 Composition Root Pattern

The `main.py` file is the only place where concrete adapters are instantiated. The PipelineBuilder receives pre-configured PTransforms via dependency injection.

```mermaid
graph TD
    subgraph Main["main.py (Composition Root)"]
        OPT["PipelineOptions()"]
        CFG["ConfigurationAdapter().load()"]
        LOG["LoggingAdapter().configure()"]
        SINKS["Create Configured Sinks<br/>(Iceberg, BigQuery, etc.)"]
        BUILD["PipelineBuilder(<br/>options, config,<br/>sink_a, sink_b, ...)"]
    end

    subgraph Builder["PipelineBuilder"]
        RUN["build_and_run()"]
        PIPE["beam.Pipeline(options)"]
        DOFN["DoFn chain"]
        WRITE["injected_sink >> write"]
    end

    OPT --> CFG --> LOG --> SINKS --> BUILD
    BUILD --> RUN --> PIPE --> DOFN --> WRITE

    style Main fill:#e3f2fd
    style Builder fill:#f5f5f5
```

### 8.3 Domain Model Pattern

All events flow through a standard envelope:

```python
class RawEvent(TypedDict):
    eventId: str       # UUID v4, auto-generated
    source: str        # e.g. "sales-collector"
    eventName: str     # e.g. "loyalty.sales" (from topic name)
    timestamp: int     # Unix epoch seconds
    payload: str       # JSON-serialized original payload
```

The `IntermediateEvent` is used between decode and envelope wrapping:

```python
class IntermediateEvent(TypedDict):
    eventName: str
    payload: dict[str, Any]
```

---

## 9. Configuration System

### 9.1 Configuration Loading Flow

```mermaid
graph LR
    subgraph Files["YAML Files"]
        BASE["config/base.yaml<br/>(common settings)"]
        ENV["config/{stg,prod}.yaml<br/>(env overrides)"]
    end

    subgraph Merge["CI/CD Merge"]
        SCRIPT["prepare_dataflow_config.sh<br/>(yq merge + base64)"]
    end

    subgraph Runtime["Dataflow Runtime"]
        CLI["--dataflow_config=<base64>"]
        DECODE["ConfigurationAdapter<br/>(base64 decode)"]
        VALIDATE["DataflowConfigDto<br/>(Pydantic validation)"]
        CONFIG["PipelineConfig<br/>(runtime model)"]
    end

    BASE --> SCRIPT
    ENV --> SCRIPT
    SCRIPT -->|"base64-encoded YAML"| CLI
    CLI --> DECODE --> VALIDATE --> CONFIG
```

### 9.2 Configuration Hierarchy

```yaml
# base.yaml (common across environments)
secret_name: "sales-collector"
window_size_seconds: 5
kafka_topics: ["loyalty.sales.created"]
kafka_group_id: "the1-sales-collector"
blms_rest_uri: "https://biglake.googleapis.com/iceberg/v1/restcatalog"
blms_namespace: "source"
iceberg_table: "raw_sales"
region: "asia-southeast1"
refined:
  sales_receipt:
    enable: true
    partition_field: "trans_date"
    write_mode: "append"

# stg.yaml (STG overrides)
project_id: "the1-loyalty-data-stg"
iceberg_warehouse: "gs://the1-loyalty-data-stg-pipeline-source"
log_level: "DEBUG"
refined:
  dataset_id: "refined"

# prod.yaml (PROD overrides)
project_id: "the1-loyalty-data-prod"
iceberg_warehouse: "gs://the1-loyalty-data-prod-pipeline-source"
log_level: "ERROR"
refined:
  dataset_id: "refined"
  member_tier:
    write_mode: "cdc"  # Override to CDC in prod
    primary_key: "memberTierId"
```

### 9.3 Secret Management

```mermaid
graph LR
    SM["GCP Secret Manager<br/>(secret_name from YAML)"]
    SA["SecretAdapter<br/>(load + parse JSON)"]
    CFG["PipelineConfig<br/>(credentials injected)"]

    SM -->|"JSON secret"| SA -->|"parsed fields"| CFG

    subgraph SecretFields["Secret Contents"]
        KF["kafka.bootstrap_servers"]
        KU["kafka.username / password"]
        SR["schema_registry.url / user / pass"]
        API["api.client_id / client_secret"]
        DB["postgres.host / port / user / pass"]
        SSH["ssh.host / private_key"]
    end

    SA --> SecretFields
```

---

## 10. Iceberg Write Path (BLMS REST Catalog)

All Iceberg writes use the BigLake Metastore (BLMS) REST Catalog for metadata management.

### 10.1 BLMS REST Catalog Configuration

```python
@dataclass(frozen=True)
class BlmsCatalogConfig:
    warehouse_path: str   # e.g. "gs://the1-loyalty-data-stg-pipeline-source"
    namespace: str        # e.g. "source"
    rest_uri: str         # "https://biglake.googleapis.com/iceberg/v1/restcatalog"
    project_id: str       # e.g. "the1-loyalty-data-stg"
    catalog_name: str     # Auto-derived from warehouse_path (bucket name)
```

### 10.2 Catalog Properties

```python
catalog_properties = {
    "type": "rest",
    "uri": "https://biglake.googleapis.com/iceberg/v1/restcatalog",
    "warehouse": "gs://{catalog_name}",
    "rest.auth.type": "org.apache.iceberg.gcp.auth.GoogleAuthManager",
    "header.X-Iceberg-Access-Delegation": "vended-credentials",
    "header.x-goog-user-project": "{project_id}",
    "io-impl": "org.apache.iceberg.gcp.gcs.GCSFileIO",
    "rest-metrics-reporting-enabled": "false",
}
```

### 10.3 Write Flow

```mermaid
graph TD
    subgraph App["Application Code"]
        SINK["IcebergSink / GcsIcebergWriter"]
        MAPPER["row_mapper function<br/>(domain -> Row)"]
        MANAGED["managed.Write(managed.ICEBERG)"]
    end

    subgraph Beam["Apache Beam (Cross-Language)"]
        JAVA["Java IcebergIO<br/>(cross-language transform)"]
    end

    subgraph BLMS["BigLake Metastore"]
        REST["BLMS REST Catalog<br/>(metadata management)"]
        VEND["Vended Credentials<br/>(GCS access delegation)"]
    end

    subgraph Storage["Storage"]
        GCS["GCS<br/>(Parquet data files)"]
        META["Iceberg Metadata<br/>(manifest, snapshots)"]
    end

    SINK --> MAPPER --> MANAGED --> JAVA
    JAVA --> REST
    REST --> VEND
    JAVA -->|"data"| GCS
    JAVA -->|"metadata"| META

    style BLMS fill:#e3f2fd
    style Storage fill:#e8f5e9
```

### 10.4 Two Writer Modes

| Mode | Implementation | Usage |
|------|---------------|-------|
| `managed_io` | `IcebergSink` -> `managed.Write(managed.ICEBERG)` | **Active** (all collectors) |
| `manual` | `ManualIcebergSink` -> PyIceberg direct writes | Legacy fallback (preserved as option) |

The managed_io path uses Beam's cross-language Java IcebergIO connector, which handles schema evolution, partition management, and concurrent writes automatically.

---

## 11. BigQuery Write Patterns

### 11.1 Write Modes

| Mode | Method | Semantics | Use Cases |
|------|--------|-----------|-----------|
| `append` | `STORAGE_WRITE_API` / `WRITE_APPEND` | At-least-once | Most collectors (default) |
| `cdc` | Storage Write API with CDC | UPSERT (exactly-once) | members-collector member_tier (prod) |
| `batch` | `WriteToBigQuery` | WRITE_APPEND | tiers-collector, m-t-h (batch mode) |

### 11.2 BigQuery Sink Configuration

```python
BigQuerySink(
    table="project:dataset.table_name",
    schema=SCHEMA_DICT,              # BigQuery schema definition
    write_mode="append",              # append, cdc, batch
    partition_field="etlLoadTime",    # Time partitioning field
    triggering_frequency=60,          # Seconds between writes (streaming)
    primary_key="memberTierId",       # Required for CDC mode
)
```

### 11.3 Timestamp Handling for BigQuery

```python
# CRITICAL: BigQuery Storage Write API requires apache_beam.utils.timestamp.Timestamp
# datetime.datetime WILL FAIL with: AttributeError: 'datetime' object has no attribute 'micros'

from apache_beam.utils.timestamp import Timestamp

# Bangkok timezone offset (+7 hours)
_BANGKOK_OFFSET_SECONDS = 7 * 3600
_BANGKOK_OFFSET_MICROS = _BANGKOK_OFFSET_SECONDS * 1_000_000

# Current time in Bangkok
etlLoadTime = Timestamp(micros=Timestamp.now().micros + _BANGKOK_OFFSET_MICROS)

# Unix timestamp to Bangkok
timestamp_ts = Timestamp(seconds=unix_ts + _BANGKOK_OFFSET_SECONDS)
```

---

## 12. Multi-Table Fan-Out Pattern

Several pipelines use the fan-out pattern where one Kafka event produces rows for multiple output tables.

### 12.1 Fan-Out Examples

```mermaid
graph TD
    subgraph Input["1 Kafka Event"]
        EVT["Sales Event<br/>(receipt + SKUs + tenders)"]
    end

    subgraph Sales["Sales Fan-Out"]
        R["sales_receipt<br/>(1 row per event)"]
        S["sales_sku<br/>(N rows per event)"]
        T["sales_tender<br/>(M rows per event)"]
    end

    subgraph Purchases["Purchases Fan-Out"]
        PR["purchases_receipt<br/>(1 row per event)"]
        PD["purchases_detail<br/>(N rows per event)"]
        PP["purchases_payment<br/>(M rows per event)"]
    end

    EVT -->|"beam.Map"| R
    EVT -->|"beam.FlatMap"| S
    EVT -->|"beam.FlatMap"| T

    EVT -->|"beam.Map"| PR
    EVT -->|"beam.FlatMap"| PD
    EVT -->|"beam.FlatMap"| PP

    style Input fill:#e8f5e9
    style Sales fill:#fff3e0
    style Purchases fill:#fff3e0
```

**Mapping rules:**
- `beam.Map` (1:1): One input record produces exactly one output record (receipt)
- `beam.FlatMap` (1:N): One input record produces zero or more output records (SKUs, tenders, details, payments)

---

## 13. Deployment and CI/CD

### 13.1 Deployment Architecture

```mermaid
graph TD
    subgraph CI["GitLab CI/CD"]
        SONAR["sonar-scan"]
        GITLEAK["gitleaks"]
        TRIVY["trivy"]
        BUILD["create-image<br/>(Docker build + push)"]
        DEPLOY_T["deploy-tables<br/>(schema deployment)"]
        DEPLOY_S["deploy:stg<br/>(Dataflow job)"]
        DEPLOY_P["deploy:prod<br/>(Dataflow job)"]
    end

    subgraph Registry["Artifact Registry"]
        GAR["asia-southeast1-docker.pkg.dev<br/>/the1-*-data-{env}<br/>/{collector}"]
    end

    subgraph Scripts["Shared Scripts"]
        PREP_CFG["prepare_dataflow_config.sh<br/>(merge YAML + base64)"]
        PREP_SPEC["prepare_dataflow_spec.sh<br/>(update container spec)"]
        DEPLOY_DF["deploy_dataflow.sh<br/>(launch Flex Template)"]
    end

    subgraph Infra["Infrastructure"]
        TF["Terraform<br/>(bucket, GAR, IAM,<br/>BigLake catalog)"]
    end

    SONAR --> BUILD
    GITLEAK --> BUILD
    TRIVY --> BUILD
    BUILD --> GAR
    BUILD --> DEPLOY_T
    DEPLOY_T --> DEPLOY_S
    DEPLOY_S --> DEPLOY_P

    DEPLOY_S --> PREP_CFG
    DEPLOY_S --> PREP_SPEC
    DEPLOY_S --> DEPLOY_DF

    TF --> GAR

    style CI fill:#f5f5f5
    style Registry fill:#e3f2fd
    style Scripts fill:#e8f5e9
```

### 13.2 Deployment Script Chain

```bash
# 1. Merge YAML configs and base64 encode
./scripts/prepare_dataflow_config.sh \
  --base config/base.yaml \
  --env config/${ENV}.yaml

# 2. Update container spec with image tag
./scripts/prepare_dataflow_spec.sh

# 3. Deploy Dataflow Flex Template
./scripts/deploy_dataflow.sh
```

### 13.3 Streaming vs Batch Deployment

| Aspect | Streaming (members-collector) | Batch (tiers-collector) |
|--------|------------------------------|------------------------|
| Mode | Continuous | Daily scheduled |
| Deploy | Cancel existing -> launch new | Direct launch |
| Template | Flex Template (Docker) | Flex Template (Docker) |
| Shutdown | Cancel (or drain-then-cancel) | Auto-terminates |
| Scaling | Auto-scaling (Dataflow) | Fixed workers |

---

## 14. Key Technical Patterns

### 14.1 Bangkok Timezone (+7)

ALL timestamps across the platform use Bangkok timezone (UTC+7). This is a hard requirement for consistency.

```
Source (Iceberg):
  iceberg_writer.py -> _BANGKOK_TZ = timezone(timedelta(hours=7))
  etlLoadTime stored as INT64 YYYYMMDDHH in Bangkok time

Refined (BigQuery):
  ALL TIMESTAMP fields have +7h offset baked in
  _BANGKOK_OFFSET_SECONDS = 7 * 3600
  _BANGKOK_OFFSET_MICROS = _BANGKOK_OFFSET_SECONDS * 1_000_000
  etlLoadTime = Timestamp(micros=Timestamp.now().micros + _BANGKOK_OFFSET_MICROS)
```

### 14.2 Iceberg Partitioning

```
etlLoadTime: INT64 (YYYYMMDDHH format in Bangkok time)
Partition: identity(etlLoadTime)
```

### 14.3 Write Mode by Environment

| Setting | STG | PROD |
|---------|-----|------|
| `write_mode` | `append` | `cdc` (for member_tier) |
| `log_level` | `DEBUG` | `ERROR` |
| BLMS Catalog | Same REST endpoint | Same REST endpoint |

### 14.4 Error Handling

- DoFns use metrics counters (seen, ok, errors) for observability
- Failed records are logged (warning level) and dropped (no DLQ yet for most collectors)
- Customer profile pipeline has BigQuery DLQ
- API DoFns have retry logic with exponential backoff
- Pipeline-level exception handling in `main.py` with `logger.exception()`

### 14.5 Shared Libraries

| Library | Location | Used By |
|---------|----------|---------|
| `common.beam` | `common/` | sales, purchases, messages (Kafka reader, BQ writer, Bigtable writer) |
| `common_cloudrun` | `common/` | rewards-collector (config, API source, logging) |

---

## 15. Per-Collector Summary

| Collector | Domain | Type | Source | Iceberg Tables | BQ Tables | Trigger | Architecture |
|-----------|--------|------|--------|---------------|-----------|---------|--------------|
| **members-collector** | loyalty | streaming | Kafka (2 topics) + Loyalty API | 4 (tier_events_upgraded, tier_events_downgraded, member_tier, member_tier_maintenance) | 4 (matching) | continuous | Hexagonal + DI |
| **tiers-collector** | loyalty | batch | Loyalty Tiers Master API | 1 (tiers) | 1 (tiers_master) | Cloud Scheduler 1AM BKK | Hexagonal + DI |
| **members-tiers-history** | loyalty | batch | PostgreSQL RDS (SSH tunnel) | 1 (members_tiers_history) | 1 (members_tiers_history) | Cloud Scheduler 1AM BKK | Hexagonal + DI |
| **transactions-collector** | loyalty | streaming | Kafka (3 topics: earned, burned, cancelled) | 1 (optional) | 3+ (raw, refined per-topic, SEM) | continuous | Hexagonal (legacy flat config) |
| **purchases-collector** | loyalty | streaming | Kafka (2 topics) | 1 | 3 (receipt, detail, payment) + Pub/Sub | continuous | Hexagonal + DI |
| **rewards-collector** | loyalty | cloud-run | Rewards REST API | 0 | 0 (GCS Parquet) | Cloud Scheduler daily | Clean Architecture (FastAPI) |
| **sales-collector** | sales | streaming | Kafka (1 topic: loyalty.sales.created) | 1 (raw_sales) | 3 (receipt, sku, tender) | continuous | Hexagonal + DI |
| **customer-profile** | insight | streaming | Pub/Sub + Bigtable | 1 (periodic merge) | 1 (CDC: ms_personas) + consent tables | continuous | Hexagonal + V2 DoFn |
| **messages-collector** | messaging | streaming | Kafka | 1 | 1 + Bigtable + Pub/Sub | continuous | Hexagonal + DI |

---

## 16. Infrastructure Overview

### 16.1 Per-Collector Infrastructure (Terraform)

```
infrastructure/{collector}/
+-- artifact.tf              # Google Artifact Registry (Docker images)
+-- bucket.tf                # GCS bucket (Iceberg warehouse)
+-- biglake-metastore.tf     # IAM: SA access to source + refined datasets
+-- schemas/
|   +-- deploy.py            # BQ table creation (Option A active, Option B disabled)
|   +-- *.json               # BigQuery schema definitions
+-- templates/
    +-- container_spec.json  # Dataflow Flex Template spec
```

### 16.2 Common Infrastructure

```
common/GCP/
+-- biglake-metastore.tf     # BigLake catalog creation
+-- source-bucket.tf         # Shared source GCS bucket
+-- service-account.tf       # Service account IAM
```

### 16.3 GCP Services Used

| Service | Purpose |
|---------|---------|
| **Dataflow** | Apache Beam pipeline execution (streaming + batch) |
| **Cloud Run** | REST API-based collectors (rewards) |
| **Cloud Scheduler** | Trigger batch pipelines (daily) |
| **Confluent Kafka** | Event streaming source (SASL/SSL) |
| **Pub/Sub** | Event bus (customer-profile source, purchases output) |
| **BigQuery** | Analytical data warehouse (refined layer) |
| **Cloud Storage (GCS)** | Iceberg data files, Parquet raw files |
| **BigLake Metastore** | Iceberg REST catalog (metadata management) |
| **Bigtable** | Real-time key-value store (customer-profile, messages) |
| **Secret Manager** | Credentials storage (Kafka, API, DB) |
| **Artifact Registry** | Docker image storage |
| **Cloud Build / GitLab CI** | CI/CD pipeline |

### 16.4 Network Topology

```mermaid
graph TB
    subgraph External["External Networks"]
        CONFLUENT["Confluent Cloud<br/>(Kafka SASL/SSL)"]
        AWS["AWS S3<br/>(ap-southeast-1)"]
        KEYCLOAK["Keycloak<br/>(OAuth2 IDP)"]
        PG_RDS["AWS RDS<br/>(PostgreSQL)"]
    end

    subgraph GCP["GCP (asia-southeast1)"]
        subgraph VPC["VPC Network"]
            DF["Dataflow Workers<br/>(private IPs)"]
            CR["Cloud Run"]
        end

        subgraph Managed["Managed Services"]
            BQ["BigQuery"]
            GCS["Cloud Storage"]
            BLMS["BigLake Metastore"]
            BT["Cloud Bigtable"]
            SM["Secret Manager"]
            PS["Pub/Sub"]
        end
    end

    CONFLUENT -->|"SASL/SSL"| DF
    PG_RDS -->|"SSH Tunnel"| DF
    DF --> BQ
    DF --> GCS
    DF --> BLMS
    DF --> BT
    DF --> PS
    DF --> SM
    DF --> AWS
    CR --> SM
    CR --> GCS
    CR --> KEYCLOAK

    style External fill:#ffebee
    style VPC fill:#e3f2fd
    style Managed fill:#e8f5e9
```

---

## Appendix A: DoFn Processing Chain (Canonical Order)

The standard DoFn chain for Kafka-based streaming pipelines:

```
1. ExtractValueDoFn        - Extract bytes from Kafka record (key, value) tuple
2. DecodeAvroOrJsonDoFn    - Decode Avro (Schema Registry) or JSON bytes
   OR DecodeParseDoFn      - Simpler JSON-only decoder
3. AttachEventNameDoFn     - Attach eventName from topic name
4. BuildRawEventDoFn       - Wrap in RawEvent envelope (eventId, source, eventName, timestamp, payload)
5. [domain-specific]       - Extract payload for refined tables (e.g., ExtractTierEventPayloadDoFn)
```

Each DoFn includes:
- Beam Metrics counters (seen, ok, errors)
- Periodic progress logging (configurable via `log_every_n`)
- Graceful error handling (log warning, drop record)

## Appendix B: Iceberg Schema Convention

All Iceberg source tables follow the same RAW event schema:

```
eventId:     STRING   (UUID v4)
source:      STRING   (collector name)
eventName:   STRING   (Kafka topic / event type)
timestamp:   INT64    (Unix epoch seconds)
payload:     STRING   (JSON-serialized original event)
etlLoadTime: INT64    (YYYYMMDDHH in Bangkok timezone, identity partition)
```

## Appendix C: Configuration Reference

### Environment Variables (Dataflow Workers)

| Variable | Purpose | Set By |
|----------|---------|--------|
| `AVRO_USE_SCHEMA_REGISTRY` | Enable Schema Registry decoding | dataflow_config |
| `AVRO_PAYLOAD_FORMAT` | `avro` or `json` | dataflow_config |
| `AVRO_SCHEMA_REGISTRY_URL` | Confluent Schema Registry URL | dataflow_config |
| `SDK_CONTAINER_IMAGE` | Custom Docker image for Runner V2 | Flex Template |

### CLI Parameters

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `--dataflow_config` | Base64-encoded merged YAML | (auto from CI) |
| `--job_type` | `normal` or `initial_data` | `--job_type=initial_data` |
| `--process_date` | Date to process (batch) | `--process_date=2026-02-19` |
| `--runner` | Beam runner | `DataflowRunner` |
| `--region` | GCP region | `asia-southeast1` |

---

*Document generated from codebase analysis of The1 Data Platform.*
*Last Updated: 2026-02-20*
