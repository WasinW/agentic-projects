# Shared Patterns -- Cross-Domain

## 1. Iceberg via BLMS REST Catalog

Two variants across domains:

**Dataflow collectors (loyalty, sales, catalog):**
```
YAML config → BlmsCatalogConfig (type: rest, GoogleAuthManager, vended-credentials)
           → ManagedIcebergWriteConfig (namespace.table, table_properties.location)
           → managed.Write(managed.ICEBERG)
```
- Frozen dataclasses: `BlmsCatalogConfig` + `ManagedIcebergWriteConfig`
- `iceberg_writer.py`: `write_to_iceberg(config=ManagedIcebergWriteConfig, ...)`
- `iceberg_sink.py`: `IcebergSink(config, schema, row_mapper)` -- 3 params
- Table auto-created by managed.Write on first write

**CloudRun services (gamification master, message master, partner master):**
```
common-cloudrun library → PyIceberg direct write → GCS Iceberg files
```
- Uses PyIceberg client directly (not Beam managed.Write)
- Passthrough pattern: raw JSON stored, Dataform extracts fields later

## 2. BQ Storage Write API + CDC

```python
BigQueryWriterAdapter → StorageWriteBigQuery (CDC mode)
```
- Config-driven: `write_mode: "cdc"`, `primary_key: ["field"]` in YAML
- BQ table must have: `ALTER TABLE ... ADD PRIMARY KEY (...) NOT ENFORCED`
- `_WrapCdcRowDoFn` adds `mutation_type` (UPSERT/DELETE) + `_change_type` pseudo-column
- DATETIME columns: no Z suffix (`%Y-%m-%dT%H:%M:%S`). TIMESTAMP: Z is ok.
- `_is_delete` flag pattern: element carries flag, popped by wrapper DoFn

## 3. Dataflow Deploy Pattern

```
container_spec.json → GAR image (asia-southeast1-docker.pkg.dev/{project}/{collector})
                    → gcloud dataflow flex-template run
                    → --staging-location, --temp-location (REQUIRED for managed transforms)
```
- Scripts: `deploy_dataflow.sh`, `prepare_dataflow_config.sh`, `prepare_dataflow_spec.sh`
- Streaming: `--update` flag, cancel-then-deploy or drain-then-deploy
- Batch: Cloud Scheduler triggers, no update needed

## 4. CloudRun + Cloud Scheduler Pattern

```
Cloud Scheduler (cron, e.g., 1AM BKK) → POST /trigger → CloudRun FastAPI service
                                                       → scale-to-zero when idle
```
- Health check endpoint required
- Used by: tiers-collector, members-tiers-history, gamification master, message master, partner master
- FastAPI service with Pydantic models

## 5. Config-Driven Pipeline

```
base.yaml + {env}.yaml → Pydantic Settings → Pipeline Config adapters → Pipeline components
```
- `base.yaml`: defaults shared across environments
- `stg.yaml` / `prod.yaml`: env-specific overrides (project IDs, buckets, topics)
- Settings classes validate and merge configs
- Adapter pattern converts config to domain objects (BlmsCatalogConfig, etc.)

## 6. Schema Evolution

- `deploy.py`: handles CREATE TABLE (if not exists) + ALTER TABLE ADD COLUMN for BQ
- `register_table` (not `create_table`) for Iceberg: preserves field IDs + partition spec
- Source Iceberg tables: auto-created by managed.Write (no deploy.py needed)
- Refined BQ tables: managed by deploy.py with JSON schema files

## 7. Bangkok Timezone +7

- All refined timestamps in Bangkok time (Asia/Bangkok, UTC+7)
- Iceberg source: `ingestedTHDate` INT YYYYMMDD or `etlLoadTime` INT YYYYMMDDHH
- BQ refined: `ingestedTHDate` DATE (DAY partition) or `etlLoadTime` TIMESTAMP (HOUR partition)
- Helper: `_get_ingested_th_date()` for Bangkok time conversion

## 8. Passthrough to Dataform

- Raw JSON stored as-is in Iceberg (no field extraction at ingestion)
- Dataform SQL extracts and transforms fields into public BQ tables
- Used by: partner master, gamification master, message master

## 9. DoFn Pipeline Pattern

**members/purchases (raw Kafka):**
```
Kafka raw bytes → ExtractValueDoFn → DecodeParseDoFn → AttachEventNameDoFn → BuildRawEventDoFn
```

**messaging (structured Kafka):**
```
Kafka event → FilterEventNameDoFn → FilterValidEventFieldsDoFn → BuildRawEventDoFn
```

**members additional (refined path):**
```
Extract → Dedup → FetchAPI → TransformPayload → WriteBQ (CDC)
```

Key: members/purchases ATTACH event name (raw). messaging FILTERS by event name (pre-structured).

## 10. Composition Root

`main.py` is the wiring point for every collector:
- Loads config (YAML → Settings)
- Builds adapters (config → domain objects)
- Constructs and runs pipeline
- Post-hooks (e.g., BQ refresh for batch collectors)

## 11. Avro Unwrapping

- `DecodeAvroOrJsonDoFn`: handles Schema Registry + Avro deserialization
- Members-collector: Kafka messages may arrive as Avro (Schema Registry) or JSON
- Schema variants: A (flat), B (nested payload dict), C (stringified message wrapper)
- `attach_event_name()` handles all 3 schemas in order: C → B → A
