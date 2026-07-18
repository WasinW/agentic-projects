# Loyalty Domain - Knowledge Base
**Cleaned: 2026-04-05 | Source: full codebase deep scan (all 8 collectors)**

---

## 1. Architecture Overview

### System Diagram (All 8 Collectors)
```
STREAMING (Dataflow):
  Kafka (earned/burned/canceled)
    -> transactions-collector [EXTERNAL: other team]
    -> Iceberg (source) + BQ refined (transactions, transactions_cancelled)
    -> BQ SEM (enriched_transactions) + GCS Parquet

  Kafka (upgraded/downgraded)
    -> members-collector (job_type=normal)
    -> Iceberg (4 tables) + BQ refined (4 tables)

  Kafka (5 topics: created/used/expired/revoked/reinstated)
    -> coupons-collector
    -> Iceberg (5+1 tables) + BQ refined CDC (enriched_coupons)

  Kafka (created/updated)
    -> purchases-collector
    -> Iceberg (2 tables) + BQ refined (3 tables: receipt/detail/payment) + PubSub

BATCH (Scheduled):
  Cloud Scheduler (1AM BKK)
    -> tiers-collector -> Loyalty Tiers API -> Iceberg + BQ refined
    -> members-tiers-history-collector -> PostgreSQL -> Iceberg + BQ refined

  Cloud Scheduler (HTTP trigger)
    -> rewards-collector (CloudRun) -> Rewards API -> Iceberg only

BATCH (Manual/GitLab):
  GitLab Pipeline (manual trigger)
    -> backward-compatible-collector -> BQ -> Parquet -> GCS -> S3

INIT DATA (One-time):
  GitLab CI (TRIGGER_INIT_DATA_LOAD=1)
    -> members-collector (job_type=initial_data) -> BQ staging -> Iceberg + BQ refined
    -> members-tiers-history (job_type=initial_data) -> BQ staging -> Iceberg + BQ refined

  DTS (S3 -> BQ loyalty dataset) -> init staging tables (temporary)
```

### Data Layers
| Layer | Storage | Dataset | Table Type | Partition Field | Catalog |
|-------|---------|---------|------------|-----------------|---------|
| Source (Raw) | Iceberg on GCS | source | external_iceberg | ingestedTHDate (INT) or ingested_date (INT) | BigLake REST |
| Refined | BigQuery | refined | native | varies per collector | N/A |
| SEM | BigQuery | public | native | event_datetime (DAY) | N/A |
| Init Staging | BigQuery | loyalty | native | varies | N/A |

### Shared Domain Models (D-H IcebergIO Refactor)
All Dataflow collectors (members, tiers, m-t-h, coupons, transactions, purchases) use:
```python
BlmsCatalogConfig(warehouse_path, namespace, rest_uri, project_id, region, catalog_name)
ManagedIcebergWriteConfig(catalog, table_name, triggering_frequency_seconds, partition_fields)
  .get_full_table_identifier()  -> "namespace.table"
  .get_table_location()         -> "gs://catalog_name/table"
  .build_writer_config()        -> dict for managed.Write(ICEBERG, config=...)

IcebergSink(config, schema, row_mapper)  # PTransform wrapper
```

Exception: rewards-collector uses `common-python-cloudrun` framework with `IcebergSchemaStrategy` instead.

---

## 2. Collectors

---

### 2.1 transactions-collector [EXTERNAL: other team]
- **Path**: `loyalty/loyalty_paralel/loyalty-data/transactions-collector/`
- **Mode**: Streaming (Kafka) via Dataflow
- **Beam**: 2.71.0
- **Owner**: Transaction team (not ours -- coordinate before changes)

#### Solution Architecture
- **Source**: Kafka 3 topics: `loyalty.transactions.earned`, `loyalty.transactions.burned`, `loyalty.transactions.canceled`
- **Sinks** (4 parallel):
  1. **BQ Refined** (topic-routed): `refined.transactions` (earned+burned), `refined.transactions_cancelled` (canceled) -- WRITE_APPEND, STORAGE_WRITE_API
  2. **BQ SEM**: `public.enriched_transactions` (all topics merged) -- WRITE_APPEND
  3. **Iceberg**: Source layer via Managed I/O (BLMS REST), optional (`iceberg_enabled` config)
  4. **GCS Parquet**: Hive-style partition on `ingestedTHDate`, optional (`parquet_enabled` config)
- **Window**: FixedWindows(300s) + Repeatedly(AfterWatermark()) + DISCARDING
- **Topic routing**: `topic_type_mapping` dict maps topic name -> `topic_source` field value (earned/burned/canceled), `topic_source` field drives BQ table routing via Filter
- **Avro**: Confluent Schema Registry integration (`use_schema_registry: true`)

#### Code Structure
```
transactions-collector/src/
  main.py                    # Composition Root: wire sinks + PipelineBuilder
  domain/
    models.py                # RawEvent (3-col), IntermediateEvent
    schemas.py               # REFINED_BQ_SCHEMA (27 fields), SEM_BQ_SCHEMA (+3 fields), Iceberg (camelCase nested)
    transformers.py           # Topic routing, normalize, flatten nested amount/acquisition
    validators.py             # Payload validation
    pipeline_config.py        # PipelineConfig (Pydantic): KafkaConfig, BigQueryOutputConfig, IcebergOutputConfig, GcsOutputConfig
    blms_catalog_config.py    # BLMS REST catalog
    managed_iceberg_write_config.py
  adapters/
    input/
      kafka_consumer.py       # build_consumer_config
      kafka_helpers.py        # DNS resolution, connectivity preflight
      avro_deserializer.py    # Schema Registry Avro decode
      configuration/          # ConfigurationAdapter, SecretAdapter, CLI options
    output/
      bigquery/               # BigQueryWriterAdapter, BigQueryWriterConfig
      iceberg_writer.py       # Beam Row conversion, Arrow schema, Managed I/O write
      gcs_parquet.py          # Dynamic Parquet writer with Hive partitioning
  application/pipeline/
    builder.py                # PipelineBuilder: Kafka -> Decode -> Enrich -> Window -> Parse -> Normalize -> ToRefined -> 4 sinks
    dofns.py                  # DecodeKafkaValueSafelyDoFn, TopicEnricherDoFn, ParseJsonSafelyDoFn, NormalizeToRowDoFn, ToRefinedDoFn
```

#### Data Architecture
- **BQ Refined Schema** (transactions.json): 27 fields including 3 REPEATED RECORD (redemptions, transaction_origins, references), DAY partition on `event_datetime`
- **BQ SEM Schema** (enriched_transactions.json): Refined + `subscription_code`, `ingested_th_date`, `topic_source`
- **Cancelled Schema** (transactions_cancelled.json): Subset of refined fields (11 fields), shared via `SEM_BQ_SCHEMA`
- **Iceberg Schema**: camelCase nested (eventId, source, eventName, eventTimestamp, payload{...}), complex nested structs (amount, acquisition, redemptions, transactionOrigins, references)
- **Parquet Schema**: Same Arrow schema as Iceberg, Hive-style partition `ingestedTHDate=YYYYMMDD`

#### Infrastructure
```
infrastructure/transactions-collector/
  artifact.tf, buckets.tf, bigquery.tf, biglake-metastore.tf, secret-manager.tf, tables.tf
  schemas/: transactions.json, transactions_cancelled.json, enriched_transactions.json
  sql/: enriched_transactions.sql, golden_transactions_earned.sql, golden_transactions_earned_view.sql
  templates/container_spec.json
```

---

### 2.2 members-collector (Streaming + Batch)
- **Path**: `loyalty/loyalty_paralel/loyalty-data/members-collector/`
- **Mode**: Streaming (Kafka) + Batch (init data)
- **Beam**: 2.71.0
- **Owner**: Our team (scope 2.1.1)

#### Solution Architecture
- **Source (Streaming)**: Kafka 2 topics: `loyalty.members.upgraded`, `loyalty.members.downgraded`
- **Source (Init)**: BQ staging tables (condition_parts)
- **Sinks**:
  - Iceberg: 4 source tables (tier_events_upgraded, tier_events_downgraded, member_tier, member_tier_maintenance)
  - BQ Refined: 4 tables (member_tier CDC, member_tier_maintenance, tier_events_upgraded, tier_events_downgraded)
- **Window**: FixedWindows(60s) + AfterWatermark(early=Repeatedly(AfterProcessingTime(60))) + DISCARDING
- **member_tier**: CDC mode in prod (PK: member_id, program_code), append in stg
- **CDC DELETE**: 3-layer safety (tierCode from Kafka, API check, BQ confirm)
- **Schema A/B/C handling**: `attach_event_name()` handles flat, wrapped, and stringified message formats
- **API enrichment**: Optional FetchMemberTierDoFn + FetchTierMaintenanceDoFn for member details

#### Pipeline Flow (Streaming)
```
ReadFromKafka -> ExtractValue -> DecodeAvroOrJson -> Window(60s)
  -> AttachEventName (Schema A/B/C) -> BuildRawEvent
  |
  +-> Write Iceberg (tier_events_upgraded/downgraded)
  +-> Write BQ refined (tier_events)
  |
  +-> Merge topics -> ExtractMemberIdAndTierCode -> pairs (shared)
      +-> member_tier:     DeduplicatePairsDoFn -> FetchMemberTierDoFn -> Write Iceberg + BQ (CDC)
      +-> tier_maintenance: Map(x[0]) -> Distinct -> FetchTierMaintenanceDoFn -> Write Iceberg + BQ
```

#### Data Architecture
- **Partition**: member_tier/maintenance use `ingestedTHDate` (DATE/DAY); tier_events use `etlLoadTime` (TIMESTAMP/HOUR)
- **Iceberg source**: 3-column schema (data STRING, ingested_date INT, ingested_at INT)
- **Refined**: member_tier 12+ fields (CDC upsert), tier_events_upgraded 12 fields, tier_events_downgraded 11 fields

#### Infrastructure
```
infrastructure/members-collector/
  bucket.tf, artifact.tf, secret-manager.tf, dts.tf, biglake-metastore.tf
  schemas/: 12 schema files (source + refined for each table)
```

---

### 2.3 tiers-collector (Batch)
- **Path**: `loyalty/loyalty_paralel/loyalty-data/tiers-collector/`
- **Mode**: Batch (PeriodicImpulse every 600s on Dataflow, Cloud Scheduler 1AM BKK)
- **Beam**: 2.71.0
- **Owner**: Our team (scope 2.1.1)

#### Solution Architecture
- **Source**: Loyalty Tiers Master REST API `/loyalty/v2/tiers` (paginated, page_size=200)
- **Sinks**:
  - Iceberg: 1 table (`tiers`)
  - BQ Refined: 1 table (`tiers_master`) -- WRITE_TRUNCATE (full replace each run)
- **No partition** on BQ refined (master table, always full overwrite)
- **Schedule**: Cloud Scheduler 1AM daily BKK

#### Pipeline Flow
```
Create([None]) -> FetchTiersDoFn (paginated API) -> flatten programs[].tiers[]
  +-> IcebergSink(tiers)
  +-> BQ refined (WRITE_TRUNCATE, tiers_master)
```

#### Data Architecture
- **Partition (Iceberg)**: `etlLoadTime` (INT YYYYMMDDHH)
- **Refined schema**: 23 fields (14+ core: program/tier hierarchy), clustering on [programCode, tierCode]
- **Schema**: Program code, tier code, tier name, points range, status, expiry rules, etc.

#### Infrastructure
```
infrastructure/tiers-collector/
  bucket.tf, artifact.tf, secret-manager.tf, scheduler.tf, biglake-metastore.tf
  schemas/: 2 files (source + refined)
```

---

### 2.4 members-tiers-history-collector (Batch)
- **Path**: `loyalty/loyalty_paralel/loyalty-data/members-tiers-collector/`
- **Mode**: Batch (Cloud Scheduler daily 1AM BKK)
- **Beam**: 2.71.0
- **Owner**: Our team (scope 2.1.1)

#### Solution Architecture
- **Source**: PostgreSQL RDS `public.member_tier_history` (24-hour sliding window on `updated_date`)
- **Sinks**:
  - Iceberg: 1 table (`members_tiers_history`)
  - BQ Refined: 1 table -- WRITE_APPEND, DAY partition on `created_date`
- **SSH tunnel**: Optional for DB access (configurable)
- **Schedule**: Cloud Scheduler 1AM daily BKK with `process_date` param (yesterday)

#### Pipeline Flow
```
ReadFromPostgresDoFn (SSH optional) -> add_etl_metadata -> convert_to_raw
  +-> IcebergSink(members_tiers_history)
  +-> convert_for_bigquery -> BQ refined (WRITE_APPEND)
```

#### Data Architecture
- **Schema**: 12 fields (member_id, tier_code, status, effective dates, 6 TIMESTAMP fields)
- **Partition (Iceberg)**: `etlLoadTime` (INT YYYYMMDDHH)
- **Partition (BQ)**: `created_date` DAY
- **Clustering**: [member_id, tier_code]

#### Infrastructure
```
infrastructure/members-tiers-history-collector/
  bucket.tf, artifact.tf, secret-manager.tf, scheduler.tf, dts.tf, biglake-metastore.tf
  schemas/: 4 files (source + refined)
```

---

### 2.5 purchases-collector
- **Path**: `loyalty/loyalty_paralel/loyalty-data/purchases-collector/`
- **Mode**: Streaming (Kafka) via Dataflow
- **Beam**: 2.71.0
- **Owner**: Our team (read-only reference)

#### Solution Architecture
- **Source**: Kafka 2 topics: `loyalty.purchases.created`, `loyalty.purchases.updated`
- **Sinks** (5 parallel):
  1. **Iceberg** (created): `source.purchases_created` -- Managed I/O via BLMS REST
  2. **Iceberg** (updated): `source.purchases_updated` -- Managed I/O via BLMS REST
  3. **BQ Refined**: `refined.purchases_receipt` (1:1 from event) -- WRITE_APPEND
  4. **BQ Refined**: `refined.purchases_detail` (1:N FlatMap) -- WRITE_APPEND
  5. **BQ Refined**: `refined.purchases_payment` (1:M FlatMap) -- WRITE_APPEND
  6. **PubSub**: Forward `purchases.created` events to downstream
- **Window**: FixedWindows(5s)
- **BQ Refresh**: PeriodicImpulse-driven BQ metadata refresh (Option B) for Iceberg external tables -- only on DataflowRunner
- **FlatMap pattern**: 1 purchase event explodes to receipt header + N detail lines + M payment lines

#### Pipeline Flow
```
ReadFromKafka -> ApplyWindow(5s) -> AttachEventName -> BuildRawEvent
  |
  +-> FilterCreated -> PubSub
  +-> FilterCreated -> IcebergSink(purchases_created)
  +-> FilterUpdated -> IcebergSink(purchases_updated)
  +-> Map(to_receipt_row) -> BQ purchases_receipt
  +-> FlatMap(to_detail_rows) -> BQ purchases_detail
  +-> FlatMap(to_payment_rows) -> BQ purchases_payment
  +-> PeriodicImpulse -> RefreshBQMetadataDoFn (DataflowRunner only)
```

#### Data Architecture
- **Partition (BQ)**: DAY on `transaction_datetime`
- **Clustering**: detail [partnerCode, memberId, sku, the1CategoryLevel1]; payment [partnerCode, paymentType, memberId, issuerBank]; receipt [partnerCode, memberId, storeCode]
- **Iceberg triggering**: 300s snapshot frequency

#### Key Difference from Other Collectors
- Uses **manual Iceberg writer** pattern (GroupIntoBatches + ManualIcebergWriterDoFn) via `gcs_biglake_iceberg_writer.py`, NOT Beam Managed IcebergIO
- Reference for: Ports & Adapters pattern, composition root, pure transformers, DoFn wrappers

#### Infrastructure
```
infrastructure/purchases-collector/
  artifact.tf, bucket.tf, biglake-metastore.tf, secret-manager.tf
  schemas/: purchases_receipt.json, purchases_detail.json, purchases_payment.json
  templates/container_spec.json
```

---

### 2.6 coupons-collector (Streaming)
- **Path**: `loyalty/loyalty_paralel/loyalty-data/coupons-collector/`
- **Mode**: Streaming (Kafka) via Dataflow
- **Beam**: 2.71.0

#### Solution Architecture
- **Source**: Kafka 5 topics: `loyalty.coupons.created`, `.used`, `.expired`, `.revoked`, `.reinstated`
- **Sinks**:
  - Iceberg: 6 source tables (5 per-topic + 1 consolidated `coupons` from API response)
  - BQ Refined: 1 table `refined.enriched_coupons` -- CDC mode (PK: coupon_id), optional API enrichment
- **Window**: FixedWindows(60s) + AfterWatermark(early=Repeatedly(AfterProcessingTime(60s))) + DISCARDING
- **API enrichment**: Optional coupon detail fetch, rate-limited (~14 TPS, 140ms delay/call, 3 retries with backoff 0.5s)
- **Schema A/B/C handling**: Same 3-schema pattern as members-collector
- **Kafka message format**: `auto` (detects Avro magic byte)
- **Common lib**: Uses `common.beam.adapters.input.kafka_reader` (DecodeMessageDoFn, ExtractValueDoFn, build_consumer_config)

#### Pipeline Flow
```
For each topic:
  ReadFromKafka -> ExtractValue -> DecodeMessage -> FilterNones
    -> ApplyWindow(60s) -> AttachEventName -> BuildRawEvent(3-col)
    -> WriteIceberg(topic-specific table)
    |
    -> collect all raw_event streams

Merge all topic streams:
  -> ExtractMemberCouponId -> DeduplicateTriple (per-bundle)
  -> FetchCouponDoFn (API) -> results
     +-> BuildRawEvent -> WriteIceberg(coupons)           [API response source]
     +-> ExtractCouponPayloadDoFn -> WriteBQ(CDC upsert)  [refined layer]
```

#### Data Architecture
- **Iceberg source**: 3-column schema (data, ingested_date, ingested_at), partition on `ingested_date`
- **BQ Refined** (enriched_coupons): ~35 active fields (coupon IDs, status, dates, partner, redemption, outcome, used info, issuer origin, event_name, ingested_datetime)
- **CDC config**: write_mode=cdc, primary_key=[coupon_id], triggering_frequency=300s
- **Topic-to-table mapping**: `TOPIC_TO_TABLE` dict in transformers.py
- **Iceberg triggering**: 14400s (4 hours)

#### Infrastructure
```
infrastructure/coupons-collector/
  artifact.tf, bucket.tf, biglake-metastore.tf, secret-manager.tf, dataform.tf
  schemas/: refined_coupons.json
  templates/container_spec.json
```

---

### 2.7 rewards-collector (CloudRun)
- **Path**: `loyalty/loyalty_paralel/loyalty-data/rewards-collector/`
- **Mode**: CloudRun + Cloud Scheduler (HTTP trigger, batch)
- **Framework**: common-python-cloudrun (FastAPI-based, NOT Apache Beam Dataflow)
- **Python**: 3.12

#### Solution Architecture
- **Source**: Loyalty Rewards REST API (paginated, page_size=200, `page_number` style pagination)
  - List API: `GET /loyalty/v2/rewards` (paginated list)
  - Detail API: `GET /loyalty/v2/rewards/{rewardId}` (per-item enrichment, max 50 concurrent)
- **Sink**: Iceberg only (GCS via PyIceberg + BigLake REST catalog) -- NO BQ refined
- **Auth**: Keycloak via private gateway (client_id/client_secret from Secret Manager)
- **Trigger**: CloudScheduler POST to `/trigger` endpoint
- **Lineage**: DataLineageAdapter emits source->target lineage events

#### Code Structure (different from Dataflow collectors)
```
rewards-collector/src/
  main.py                     # FastAPI app factory (Composition Root)
  adapters/
    input/http/
      http_adapter.py          # FastAPI routes: /health, /trigger
    output/
      gcs_iceberg/
        rewards_schema_strategy.py  # RewardsSchemaStrategy (3 fields: IngestedDate, IngestedDateTime, payload)
      lineage_client.py        # DataLineageAdapter, LineagePipelineDecorator
  infrastructure/
    settings.py                # Settings(PipelineSettings) -- YAML-based config
    secret_manager.py          # AppSecretsAdapter
```

#### YAML Config Architecture (base.yml, stg.yml, prod.yml)
```yaml
auth:
  private_gw: {type: keycloak, url: https://..., realm: per-env}
sources:
  rewards_api: {type: rest_api, auth: private_gw, endpoint: /loyalty/v2/rewards, pagination: {style: page_number, page_size: 200}}
  rewards_detail_api: {type: rest_api, auth: private_gw, endpoint: /loyalty/v2/rewards/{rewardId}}
transforms:
  rewards_enricher: {type: api_detail_lookup, lookup_field: rewardId, source: rewards_detail_api, max_concurrency: 50}
sinks:
  rewards_iceberg: {type: gcs_iceberg, schema_strategy: rewards, catalog_uri: biglake REST, namespace: source, table_name: rewards}
pipelines:
  rewards: {source: rewards_api, transform: rewards_enricher, sinks: [rewards_iceberg]}
```

#### Data Architecture
- **Iceberg schema** (RewardsSchemaStrategy): 3 fields: IngestedDate (INT32 YYYYMMDD), IngestedDateTime (TIMESTAMP us), payload (STRING JSON)
- **Partition**: Identity on `IngestedDate`
- **No BQ refined** -- Iceberg source only, presumably consumed by downstream

#### Infrastructure
```
infrastructure/rewards-collector/
  artifact.tf, biglake-metastore.tf, cloud-run.tf, dataform.tf, secret-manager.tf
  (no bucket.tf -- uses shared GCS, no scheduler.tf -- Cloud Scheduler at CloudRun level)
```

---

### 2.8 backward-compatible-collector (Batch Export)
- **Path**: `loyalty/loyalty_paralel/backward-compatible/backward-compatible-collector/`
- **Mode**: Batch (manual/scheduled via GitLab Pipeline)
- **Purpose**: Export BQ refined data to S3 for legacy systems

#### Solution Architecture
- **Source**: BigQuery refined tables (parameterized SQL queries)
- **Pipeline**: ReadFromBigQuery -> WriteToParquet (GCS temp) -> boto3 upload to S3
- **S3 destination**: `s3://the1-insight-data/` (ap-southeast-1)
- **Config-driven**: Base YAML + per-table job YAML configs

#### Pipeline Flow
```
1. Load config (base + job YAML, both base64-encoded CLI args)
2. Dataflow: ReadFromBQ(query with ${PROJECT_ID}, ${PROCESS_DATE}) -> WriteToParquet(GCS temp)
3. Post-pipeline: boto3 GCS -> local temp -> S3 (multipart upload, 64MB chunks, 10 concurrency)
4. Verify: head_object size check per file
```

#### Job Configs (per-table)
```
config/jobs/
  member_tier.yaml           # SELECT * FROM refined.member_tier WHERE DATE(ingested_datetime) = '${PROCESS_DATE}'
  member_tier_history.yaml   # Similar pattern
  member_tier_maintenance.yaml
```

#### S3 Transfer Config
- Multipart threshold: 64MB, chunk size: 64MB
- Max concurrency: 10, adaptive retries (max 10)
- Connect/read timeout: 300s each
- Parquet: snappy compression, 15 shards default

#### Data Architecture
- **Input**: BQ refined tables (filtered by PROCESS_DATE)
- **Output**: Parquet files in `gs://{bucket}/export/{job_name}/{date}/` -> `s3://the1-insight-data/loyalty/refined/{table}/{date}/`
- **No Iceberg** (pure export pipeline)

#### Infrastructure
```
backward-compatible/
  infrastructure/backward-compatible-collector/ (separate from loyalty-data)
  infrastructure/schemas/
  infrastructure/templates/
```

---

### 2.9 [REF] purchases-data (Older Version, Read-Only)
- **Path**: `loyalty/purchases-data/`
- **Beam**: 2.70.0 (older)
- **Status**: Older version of purchases-collector, reference only
- **Note**: Do not modify; kept for comparison

### 2.10 [DEPRECATED] member-tiers
- Legacy collector, do not use or modify
- Superseded by members-collector + tiers-collector split

---

## 3. Iceberg Write (BLMS REST Active)

### Option B Terminology
- **Write (Option B)** = Iceberg writes via BLMS REST Catalog -> **ACTIVE** (identical to messaging-collector)
- **BQ Table Creation (Option B)** = `externalCatalogTableOptions` + `tables.patch` refresh -> **DISABLED**

### BLMS REST Catalog Config
```python
catalog_properties = {
    "type": "rest",
    "uri": "https://biglake.googleapis.com/iceberg/v1/restcatalog",
    "warehouse": "gs://the1-loyalty-data-source-{env}",
    "rest.auth.type": "org.apache.iceberg.gcp.auth.GoogleAuthManager",
    "header.X-Iceberg-Access-Delegation": "vended-credentials",
    "header.x-goog-user-project": project_id,
    "io-impl": "org.apache.iceberg.gcp.gcs.GCSFileIO",
    "rest-metrics-reporting-enabled": "false",
}
```

### Key Behaviors
- `table_properties.location` works ONLY on CREATE (not LOAD)
- If table exists in BLMS -> IcebergIO LOAD, ignores location override
- Source Iceberg tables auto-created by `managed.Write` on first Dataflow write
- Hadoop catalog preserved as comments (search `"Hadoop Catalog"` to rollback)

### Source Iceberg Schemas (Two Variants)
**Variant 1: 3-Column Schema** (members, tiers, m-t-h, coupons)
- `data` (STRING) - JSON payload
- `ingested_date` (INT) - YYYYMMDD
- `ingested_at` (STRING or INT) - epoch timestamp or ISO string

**Variant 2: Structured Nested Schema** (transactions)
- `eventId` (STRING), `source` (STRING), `eventName` (STRING), `eventTimestamp` (LONG)
- `payload` (STRUCT) - full nested camelCase fields (amount, acquisition, redemptions, etc.)

**Variant 3: RewardsSchemaStrategy** (rewards -- via CloudRun/PyIceberg)
- `IngestedDate` (INT32) - YYYYMMDD
- `IngestedDateTime` (TIMESTAMP) - microseconds
- `payload` (STRING) - JSON

---

## 4. BQ Table Creation (Option B Status)

### Current: DISABLED - waiting for [EXTERNAL: transaction/ team]
- `builder.py` (members): PeriodicImpulse block **commented out**
- `base.yaml` (members): `bq_refresh.enabled: false`
- `main.py` (tiers + m-t-h): BQ refresh post-hook **commented out**
- `deploy.py` x3: Option B code **fully removed** (native BQ only, ~370 lines)
- `bq_metadata_refresh.py` x3: module kept (not deleted), tests pass

### Re-enable Steps (when [EXTERNAL: transaction/ team] is ready)
1. `base.yaml` (members): `bq_refresh.enabled: true`
2. `builder.py` (members): uncomment PeriodicImpulse block
3. `main.py` (tiers + m-t-h): uncomment BQ refresh post-hook
4. `deploy.py` x3: Option B code was removed, would need re-add
5. Coordinate: `external_catalog_dataset_options` + IAM

---

## 5. CI/CD Status

### GitLab CI (as of 2026-02-25)
- **PROD uncommented** -- all 3 collectors (members, tiers, m-t-h) have active prod jobs
- **No STG->PROD gate** -- deploy:prod doesn't depend on deploy:stg
- **members cancel vs purchases drain** -- should upgrade to drain-first
- `create-image` x3: 4 destinations (STG active + PROD)
- deploy:prod scripts use: prepare_dataflow_config.sh, prepare_dataflow_spec.sh, deploy_dataflow.sh
- m-t-h deploy:prod has `process_date` (yesterday)
- Sonar/gitleaks/trivy refactored to shared extends (`.common-sonar-scan`, etc.)

### deploy.py (Table Deployer)
- ~370 lines (cleaned from ~2290), native BQ only
- Schema evolution: `compare_schemas()` -> NO_CHANGE | ADDITIVE | BREAKING
- ADDITIVE: ALTER TABLE ADD COLUMN
- BREAKING: backup -> drop -> recreate -> restore
- Usage: `python deploy.py <PROJECT_ID> <ENV> [--force] [--table=<name>]`

### Infrastructure (Terraform) -- All Collectors
```
infrastructure/
  common/GCP/                    (biglake-metastore.tf, buckets.tf, bigquery.tf, service-accounts.tf)
  members-collector/             (bucket.tf, artifact.tf, secret-manager.tf, dts.tf, biglake-metastore.tf + 12 schemas)
  tiers-collector/               (bucket.tf, artifact.tf, secret-manager.tf, scheduler.tf, biglake-metastore.tf + 2 schemas)
  members-tiers-history-collector/ (bucket.tf, artifact.tf, secret-manager.tf, scheduler.tf, dts.tf, biglake-metastore.tf + 4 schemas)
  purchases-collector/           (artifact.tf, bucket.tf, biglake-metastore.tf, secret-manager.tf + 3 schemas)
  transactions-collector/        (artifact.tf, buckets.tf, bigquery.tf, biglake-metastore.tf, secret-manager.tf, tables.tf + 3 schemas + 3 SQL)
  coupons-collector/             (artifact.tf, bucket.tf, biglake-metastore.tf, dataform.tf, secret-manager.tf + 1 schema)
  rewards-collector/             (artifact.tf, biglake-metastore.tf, cloud-run.tf, dataform.tf, secret-manager.tf)
```

| Component | Members | Tiers | M-T-H | Purchases | Transactions | Coupons | Rewards | Backward-Compat |
|-----------|---------|-------|-------|-----------|--------------|---------|---------|-----------------|
| Runtime | Dataflow | Dataflow | Dataflow | Dataflow | Dataflow | Dataflow | CloudRun | Dataflow |
| Mode | Streaming | Batch | Batch | Streaming | Streaming | Streaming | Batch (HTTP) | Batch |
| Beam Version | 2.71.0 | 2.71.0 | 2.71.0 | 2.71.0 | 2.71.0 | 2.71.0 | N/A | N/A |
| Scheduler | No | 1AM BKK | 1AM BKK | No | No | No | CloudScheduler | GitLab |
| biglake-metastore.tf | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No |

---

## 6. Key Technical Patterns

### Bangkok Timezone +7 (ALL refined timestamps)
```python
_BANGKOK_TZ = timezone(timedelta(hours=7))

# Source (Iceberg): INT format
_get_ingested_th_date() -> INT YYYYMMDD Bangkok  # member_tier/maintenance
_get_etl_load_time()    -> INT YYYYMMDDHH Bangkok # tier_events

# Refined (BQ):
ingestedTHDate -> datetime.now(_BANGKOK_TZ).strftime("%Y-%m-%d") -> DATE
etlLoadTime    -> Timestamp(micros=now + _BANGKOK_OFFSET_MICROS) -> TIMESTAMP
```

### CDC DELETE for member_tier (3-layer safety)
1. `tier_code` is not None (from Kafka)
2. API does not have the tier
3. BQ confirms it existed (query for programCode)
- `_is_delete: True` flag -> `_WrapCdcRowDoFn` -> `mutation_type: "DELETE"`

### Schema A/B/C Handling (members-collector + coupons-collector)
- **Schema A**: flat message -> wrap as payload
- **Schema B**: `{payload: {actual_data}}` -> unwrap inner payload
- **Schema C**: `{message: "<stringified JSON>"}` -> json.loads -> fall through to B/A
- Code: `{collector}/src/domain/transformers.py` `attach_event_name()`

### Avro Detection
```python
if data[0] == 0x00 and len(data) >= 5:  # Confluent Schema Registry Avro
```

### BigQuery Storage Write API
- MUST use `apache_beam.utils.timestamp.Timestamp`, NOT datetime.datetime
- CDC mode: prod `write_mode: cdc`, stg `write_mode: append`
- CDC only for native BQ tables, NOT BigLake Iceberg

### Windowing Summary
| Collector | Window | Trigger | Accumulation |
|-----------|--------|---------|-------------|
| transactions | FixedWindows(300s) | Repeatedly(AfterWatermark()) | DISCARDING |
| members | FixedWindows(60s) | AfterWatermark(early=Repeatedly(AfterProcessingTime(60))) | DISCARDING |
| purchases | FixedWindows(5s) | default | default |
| coupons | FixedWindows(60s) | AfterWatermark(early=Repeatedly(AfterProcessingTime(60))) | DISCARDING |

### Topic-to-Table Routing Patterns
- **transactions**: `topic_type_mapping` dict -> `TopicEnricherDoFn` adds `topic_source` field -> Filter by topic_source for BQ table routing
- **coupons**: `TOPIC_TO_TABLE` dict in transformers.py -> per-topic Iceberg sinks + merged API branch
- **purchases**: Filter by event name (`is_purchases_created_event` / `is_purchases_updated_event`) for Iceberg + PubSub routing
- **members**: Topic name embedded in event, used for Iceberg table selection + refined table routing

---

## 7. Config Structure

### YAML Merge Strategy (Dataflow collectors)
```
base.yaml (common) + {env}.yaml (stg/prod) -> merged config
  -> base64encode(yamlencode(merged))
  -> --dataflow_config CLI parameter
```

### YAML Merge Strategy (rewards-collector / CloudRun)
```
base.yml + {env}.yml -> deep merge via pydantic-settings
  -> Settings() auto-loads from environment + YAML
```

### Config Loading Pipeline (Dataflow)
```
CLI --dataflow_config=<base64> -> Decode -> YAML parse
  -> Pydantic validation (DataflowConfigDto or PipelineConfig)
  -> Secret Manager fetch (project_id + secret_name)
  -> Build domain configs (BlmsCatalogConfig, ManagedIcebergWriteConfig)
  -> Return PipelineConfig (runtime)
```

### Key Config Files per Collector
- `config/base.yaml` (or `base.yml`) - common settings
- `config/stg.yaml` (or `stg.yml`) - STG overrides
- `config/prod.yaml` (or `prod.yml`) - PROD overrides

### File Locations (Dataflow Collectors)
```
{collector}/src/domain/
  blms_catalog_config.py           # BLMS REST active, Hadoop commented
  managed_iceberg_write_config.py  # BLMS REST active, Hadoop commented

{collector}/src/adapters/output/
  iceberg_writer.py       # write_to_iceberg(config=ManagedIcebergWriteConfig)
  iceberg_sink.py         # IcebergSink(config, schema, row_mapper)
  bq_metadata_refresh.py  # Option B refresh (DISABLED, module kept)

infrastructure/{collector}/
  artifact.tf             # GAR repo per-collector
  bucket.tf               # GCS bucket per-collector
  biglake-metastore.tf    # IAM: source + refined dataset access
  schemas/deploy.py       # Native BQ only (~370 lines)
```

### Common Errors & Fixes
| Error | Fix |
|-------|-----|
| OOM on GitLab Runner | Use Dataflow batch (`job_type=initial_data`) |
| Ruff RUF043 (regex) | Use raw string: `match=r"kafka\.topics"` |
| pre-commit modifies [EXTERNAL: transaction/] | `git checkout -- transactions-collector/` after pre-commit |
| Managed transform artifact staging fail | Add `--staging-location` + `--temp-location` in deploy |
| BQ TIMESTAMP type error | Use `Timestamp(seconds=...)` not datetime |
| IcebergIO ClassCastException String->Long | Schema mismatch: use INT64 (microseconds) for timestamptz, not STRING |

### Quality Check Commands (MUST run after EVERY change)
```bash
cd loyalty/loyalty_paralel/loyalty-data/{collector}/
uv sync
ruff check . && ruff format --check .
mypy src tests
pytest
pre-commit run --all-files
```

### Test Counts
- members-collector: ~220 tests
- tiers-collector: ~107 tests
- members-tiers-history: ~104 tests

### Documentation Map
| Doc | Path |
|-----|------|
| Master Index | `loyalty/docs/README.md` |
| Option B Summary | `loyalty/docs/option-b-migration/OPTION_B_SUMMARY.md` |
| DLQ Research | `loyalty/docs/dlq/DLQ_RESEARCH.md` |
| CI/CD Comparison | `loyalty/docs/architecture/CICD_COMPARISON_AND_PROD_SAFETY.md` |
| CDC DELETE Research | `loyalty/docs/bigquery/CDC_DELETE_RESEARCH.md` |
| Tier Maintenance CDC | `loyalty/docs/bigquery/TIER_MAINTENANCE_CDC_UPSERT.md` |
