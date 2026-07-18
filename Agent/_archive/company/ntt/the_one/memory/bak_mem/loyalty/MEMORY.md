# Loyalty Data Project - Key Learnings

## CRITICAL: อ่านก่อนทำอะไรทุกครั้ง
- **`memory/mistakes_and_rules.md`** — ข้อผิดพลาดที่ห้ามทำซ้ำ + rules การทำงาน
- อ่าน code จริงก่อนพูด อย่าเดา — verify ก่อนตอบเสมอ
- สั้น กระชับ ลงมือทำ — ไม่ต้องอธิบายยาว

## IMPORTANT: Knowledge Base & Documentation
**อ่าน knowledge base ที่สร้างจาก full codebase exploration ก่อน:**
- `memory/loyalty_knowledge_base.md` - **COMPLETE** knowledge base (all collectors, infra, schemas, patterns)
- `memory/catalog_products_knowledge_base.md` - **Catalog/products-collector** setup KB (terraform, CI/CD, code patterns from purchases-collector)
- `loyalty/docs/README.md` - **Master index** (all docs organized by topic)
- `loyalty/docs/option-b-migration/OPTION_B_SUMMARY.md` - Option B migration summary + pending items
- `loyalty/docs/dlq/DLQ_RESEARCH.md` - DLQ research (patterns, storage, replay)
- `memory/kafka_schema_changes.md` - New Kafka schema (eligibleTierCode) + init data migration plan

## Project Rules (MUST FOLLOW)
- **No git commands** (no branch, add, commit, push)
- **Must run** after code changes: `uv sync`, `ruff`, `mypy`, `pytest`, `pre-commit`
- **Focus on 2.1.1** (user's code): members-collector, tiers-collector, members-tiers-history-collector
- **purchases-collector** = reference/read-only
- **member-tiers** = DEPRECATED
- **transaction/** = NOT ours — coordinate with other team before changes

## Architecture Overview
```
STREAMING: Kafka → members-collector (job_type=normal) → Iceberg → BQ
BATCH:     Cloud Scheduler (1AM BKK) → tiers-collector → Iceberg → BQ
           Cloud Scheduler (1AM BKK) → members-tiers-history → Iceberg → BQ
INIT:      GitLab CI (TRIGGER_INIT_DATA_LOAD=1) → job_type=initial_data → Iceberg → BQ
```

## Current State (2026-02-25)

### IMPORTANT: Option B Terminology Clarification
**"Option B" มี 2 ส่วนที่แยกกัน:**
1. **Write แบบ Option B** = Iceberg writes via BLMS REST Catalog → **ACTIVE เหมือน messaging ทุกประการ**
2. **BQ Table Creation แบบ Option B** = `externalCatalogTableOptions` + `tables.patch` refresh → **DISABLED** (waiting for terraform dataset)

**อย่าสับสน!** Write path เปิดอยู่แล้ว (BLMS REST) — แค่ BQ table creation ยังใช้ Option A ไปก่อน
เพราะ terraform dataset `externalCatalogDatasetOptions` ยังไม่พร้อม (ต้อง coordinate กับ transaction/ team)
เดี๋ยวค่อยกลับมา enable BQ table creation (Option B) ทีหลัง

### IcebergIO Write: BLMS REST Catalog ACTIVE (= Option B write, เหมือน messaging)
- `blms_catalog_config.py` x3: **BLMS REST active** (`type: rest`, GoogleAuthManager, vended-credentials)
- `managed_iceberg_write_config.py` x3: **BLMS writer** (`namespace.table`, `table_properties.location`)
- Hadoop preserved as comments — search `"Hadoop Catalog"` to rollback
- BigLake catalog exists in terraform (`common/GCP/biglake-metastore.tf`)
- **Verified 2026-02-17**: Full trace YAML→Settings→ConfigAdapter→BlmsCatalogConfig→ManagedIcebergWriteConfig→IcebergSink→managed.Write — IDENTICAL to messaging-collector

### BQ Table Creation (Option B part): DISABLED — waiting for transaction/ team
- `builder.py` (members): PeriodicImpulse block **commented out**
- `base.yaml` (members): `bq_refresh.enabled: false`
- `main.py` (tiers + m-t-h): BQ refresh post-hook **commented out**
- `deploy.py` x3: **CLEANED** — Option B code fully removed (not just commented), native BQ only
- `bq_metadata_refresh.py` x3: module stays (not deleted), tests pass

### GitLab CI: PROD COMMENTED (testing STG first)
- `create-image` x3: **4 destinations** (STG active + PROD commented) — like purchases-collector
- `terraform:apply:prod` x3: **commented** (testing stg first)
- `deploy-tables:prod` x3: **commented** (testing stg first)
- `deploy:prod` x3: **full logic commented** — members has streaming cancel, tiers/m-t-h batch
- All deploy:prod scripts have: prepare_dataflow_config.sh, prepare_dataflow_spec.sh, deploy_dataflow.sh, network/subnetwork, staging/temp locations
- m-t-h deploy:prod has `process_date` (yesterday)
- Remote refactored sonar/gitleaks/trivy to shared extends (`.common-sonar-scan`, etc.)
- Merged our changes into remote base (2026-02-17)

### Infrastructure: COMPLETE (existed before our sessions)
- Per-collector GCS buckets: `infrastructure/{collector}/bucket.tf`
- Per-collector GAR repos: `infrastructure/{collector}/artifact.tf`
- Per-collector IAM: `infrastructure/{collector}/biglake-metastore.tf` (source + refined datasets)
- Config files: `{collector}/config/{base,stg,prod}.yaml` — all exist
- Scripts: `scripts/{deploy_dataflow,prepare_dataflow_config,prepare_dataflow_spec}.sh`
- Templates: `infrastructure/{collector}/templates/container_spec.json`
- Common infra: BigLake catalog + source bucket + SA IAM in `common/GCP/`

## Completed Work

### D-H IcebergIO Refactor (DONE)
- Domain models: `BlmsCatalogConfig` + `ManagedIcebergWriteConfig` (frozen dataclasses)
- `iceberg_writer.py`: `write_to_iceberg(config=ManagedIcebergWriteConfig, ...)`
- `iceberg_sink.py`: `IcebergSink(config, schema, row_mapper)` — 3 params
- All 3 collectors: identical patterns, 498 tests passing (197+197+104)

### Option B Migration CODE (DONE, partially cleaned 2026-02-24)
- `bq_metadata_refresh.py` x3 — refresh logic + DoFn (module kept, not deleted)
- `deploy.py` x3 — **Option B code fully removed** (deploy.py is now native BQ only)
- `builder.py` (members) — PeriodicImpulse branch (commented out)
- `main.py` (tiers + m-t-h) — post-hook refresh (commented out)

### deploy.py register_table fix (DONE)
- `register_table` instead of `create_table` — preserves field IDs + partition spec

### GitLab CI prod (DONE)
- Uncommented all prod steps, added prod destinations, full deploy:prod logic

### biglake-metastore.tf per-collector IAM (DONE)
- Each collector has own biglake-metastore.tf granting SA access to source + refined datasets

### Schema B nested payload fix (DONE 2026-02-23)
- **Bug**: `attach_event_name()` in `members-collector/src/domain/transformers.py` double-wrapped Schema B messages
- **Schema B**: Kafka `{eventId, source, eventName, timestamp, payload: {actual_data}}`
- **Fix**: Detect `isinstance(payload.get("payload"), dict)` → unwrap inner payload instead of re-wrapping
- **Effect**: Fixed both Iceberg double-nesting AND refined BQ null fields (ExtractTierEvent*PayloadDoFn now finds fields)
- **Tests**: 4 new tests (3 in test_transformers.py + 1 in test_dofns.py), 197 tests pass

### partition_fields alignment (DONE 2026-02-23)
- **Issue**: Our 3 collectors' `ManagedIcebergWriteConfig` didn't pass `partition_fields` to `managed.Write`
- **Risk**: If managed.Write auto-creates table (after BLMS drop), table won't have partition
- **Fix**: Added `partition_fields: list[str] = field(default_factory=list)` to all 3 collectors
- **All instantiation sites** now pass partition_fields:
  - members: member_info `["ingestedTHDate"]` (main.py+builder.py), tier_events `["etlLoadTime"]` (main.py)
  - tiers: `["etlLoadTime"]` (main.py)
  - m-t-h: `["etlLoadTime"]` (main.py+builder.py)
- **498 tests pass** (197+197+104), ruff/mypy/pre-commit all green

### Schema C stringified message fix (DONE 2026-02-24)
- **Bug**: STG Kafka messages arrive as `{"message": "<stringified JSON>"}` (Schema C variant)
- **Schema C**: Outer JSON parsed → `{"message": "{ \"eventId\": \"...\", \"payload\": {...}}"}` — inner value is string, not dict
- **Previous Schema B fix** only handled `payload` key as dict — didn't handle `message` string wrapper
- **Fix**: `attach_event_name()` now handles 3 schemas in order:
  1. Schema C: detect `message` key with string value → `json.loads()` → replace payload → fall through
  2. Schema B: detect `payload` key as dict → unwrap inner payload
  3. Schema A: flat message → wrap entire dict as payload
- **Code**: `members-collector/src/domain/transformers.py` lines 62-80
- **Tests**: 3 new Schema C tests in `test_transformers.py`, total 200 tests pass
- **Only members-collector** has `attach_event_name()` — tiers/m-t-h not affected

### CDC DELETE for member_tier (DONE 2026-02-24)
- **Problem**: CDC-enabled `refined.member_tier` table cannot use DML DELETE — stale rows stay forever when tier removed
- **Approach**: Variant of "CDC DELETE via Diff" — carry `tierCode` from Kafka, match against API, BQ query only for DELETE
- **Pipeline flow change**:
  - Before: `ExtractMemberIdDoFn → DeduplicateMemberIdsDoFn → member_ids (shared)`
  - After: `ExtractMemberIdAndTierCodeDoFn → pairs (shared)`
    - member_tier: `DeduplicatePairsDoFn → FetchMemberTierDoFn` (with CDC DELETE support)
    - tier_maintenance: `Map(x[0]) → DeduplicateMemberIdsDoFn → FetchTierMaintenanceDoFn`
- **FetchMemberTierDoFn logic**:
  - `tier_code is None` → yield all tiers (UPSERT) — original behavior
  - `tier_code` found in API → yield only matching item (UPSERT)
  - `tier_code` NOT in API → query BQ for programCode → CDC DELETE (if found in BQ)
- **3-layer DELETE safety**: (1) tier_code not None, (2) API doesn't have it, (3) BQ confirms it existed
- **`_is_delete` flag pattern**: element carries `_is_delete: True`, popped by `_WrapCdcRowDoFn` → `mutation_type: "DELETE"`
- **Files changed**: `api_dofns.py`, `bigquery_storage.py`, `transform_dofns.py`, `builder.py`, `base.yaml`
- **New tests**: 17 new tests (10 api_dofns + 2 transform_dofns + 5 bigquery_storage), total 215 pass
- **Edge case (MUST VERIFY)**: tierCode in Kafka = current or old tier? Affects 2→1 downgrade safety
- **Docs**: `loyalty/docs/bigquery/CDC_DELETE_RESEARCH.md`, platform doc updated

### Tier maintenance dedup + CDC upsert (DONE 2026-02-25)
- **Bug**: Same member_id from 2 Kafka topics → `DeduplicateMemberIdsDoFn` per-bundle ไม่ catch ข้าม bundle → API ยิงซ้ำ + write dup
- **Fix 1**: `builder.py` → `beam.Distinct()` (GroupByKey-based dedup ใน window)
- **Fix 2**: CDC upsert by `tierMaintenanceId` — sink-level dedup safety net
  - `refined_member_tier_maintenance.json`: เพิ่ม `primary_key: ["tierMaintenanceId"]`
  - `prod.yaml` + `stg.yaml`: เพิ่ม `write_mode: "cdc"` + `primary_key`
  - **Deploy ต้อง ALTER มือ**: `ALTER TABLE ... ADD PRIMARY KEY (tierMaintenanceId) NOT ENFORCED`
  - `max_staleness` ไม่จำเป็น (member_tier prod ก็ไม่มี)
- **Doc**: `loyalty/docs/bigquery/TIER_MAINTENANCE_CDC_UPSERT.md`

### etlLoadTime → ingestedTHDate rename (DONE 2026-03-02)
- **Scope**: members-collector only — `member_tier` + `member_tier_maintenance` tables
- **tier_events** (upgraded + downgraded) **UNCHANGED** — still uses `etlLoadTime`
- **Iceberg source**: `etlLoadTime` INT YYYYMMDDHH → `ingestedTHDate` INT YYYYMMDD
- **BQ refined**: `etlLoadTime` TIMESTAMP (HOUR partition) → `ingestedTHDate` DATE (DAY partition)
- **14 files changed**: iceberg_writer.py, transform_dofns.py, schemas.py, main.py, builder.py, settings.py, pipeline_config.py, base.yaml, 2 JSON schemas, 4 SQL init files, 3 test files
- **New helper**: `_get_ingested_th_date()` → INT YYYYMMDD Bangkok time (Iceberg); `"%Y-%m-%d"` string (BQ refined)
- **Config defaults split**: `RefinedTableConfig.partition_field="ingestedTHDate"` vs `RefinedTierEventsConfig.partition_field="etlLoadTime"`
- **NOT changed**: `bigquery_sink.py` default, `bigquery_storage.py` HOUR type, `pyiceberg_writer.py` (dead code)
- **220 tests pass**, ruff/mypy/pre-commit green

### Kafka config + Secret structure migration (DONE 2026-02-25)
- **members-collector only** (tiers/m-t-h ไม่ใช้ Kafka)
- **Secret keys**: `kafka_connection` → `kafkaCredentials`, `api_connection` → `apiCredentials`
- **Bug caught**: deploy แล้ว Kafka timeout เพราะ secret key เปลี่ยนแต่ code ยังอ่าน key เดิม

### deploy.py cleanup — Iceberg code removed (DONE 2026-02-24)
- **Reason**: Source Iceberg tables auto-created by `managed.Write` via BLMS REST on first Dataflow write
- **deploy.py**: Rewritten from ~2290 lines → ~370 lines (native BQ only)
  - **Removed**: PyIceberg imports, BQ_TO_ICEBERG_TYPES, generate_iceberg_metadata, create_iceberg_with_dummy_data, delete_iceberg_dummy_data, create_iceberg_table_for_icebergio, register_table_in_biglake_catalog, evolve_iceberg_schema, ensure_iceberg_metadata, Option B methods, _get_access_token, _get_authorized_session, ensure_dataset_catalog_options, create_external_catalog_table, refresh_bq_metadata, Java tool methods
  - **Kept**: native BQ table handling (CREATE, ALTER, backup/restore, schema compare)
  - **Added**: `if not content: continue` to skip empty JSON files
  - **Removed**: `enable_biglake_catalog` param, `run_gsutil` method
- **Deleted 6 empty (0B) JSON source table placeholders**:
  - members: `member_tier.json`, `member_tier_maintenance.json`, `tier_events_downgraded.json`, `tier_events_upgraded.json`
  - tiers: `tiers.json`
  - m-t-h: `members_tiers_history.json`
- **CI (.gitlab-ci.yml x3)**: Removed `pip install pyiceberg[gcs,sql-sqlite] pyarrow gcsfs` and `ICEBERG_CREATE_METHOD` from deploy-tables jobs
- **All 3 collectors**: identical deploy.py, 501 tests pass (200+197+104)

## Re-enable Option B (when transaction/ team is ready)
1. `base.yaml` (members): `bq_refresh.enabled: true`
2. `builder.py` (members): uncomment PeriodicImpulse block
3. `main.py` (tiers + m-t-h): uncomment BQ refresh post-hook
4. `deploy.py` x3: **Option B code was removed** — would need to re-add if BQ table creation via deploy.py is needed
5. Coordinate with transaction/ team: `external_catalog_dataset_options` + IAM

## CI/CD Status (2026-02-25)
- **PROD uncommented** — all 3 collectors have active prod jobs
- **No STG→PROD gate** — deploy:prod doesn't depend on deploy:stg (unlike purchases/transactions)
- **members cancel vs purchases drain** — should upgrade to drain-first
- **Full comparison**: `docs/architecture/CICD_COMPARISON_AND_PROD_SAFETY.md`

## Sales-Collector Schema Migration (DONE 2026-03-17)
- **`memory/sales_schema_migration_done.md`** — Complete summary of all changes
- **`memory/sales_deploy_fix.md`** — deploy.py INTERVAL syntax fix
- **`sale/doc/SCHEMA_MIGRATION_PLAN.md`** — Original plan with open questions
- **Status**: CODE DONE (269 tests pass) — BQ table migration pending (ALTER/recreate)
- **Pending**: Streaming join research with 5 large batch tables (agent was running, may need re-run)

## Pending / Future
- **Secret key migration (tiers-collector)** — DevOps อาจเปลี่ยน secret key จาก `api_connection` → `apiCredentials` เหมือน members-collector ถ้าเปลี่ยนต้องแก้ `configuration_adapter.py` ด้วย (ปัจจุบันยัง `api_connection` อยู่)
- **Secret key migration (m-t-h)** — ใช้ configurable keys จาก YAML (`rds_endpoint`, `rds_username`, `rds_password`) + `ssh_connection` — ไม่น่าเกี่ยวกับ kafka/api rename แต่ถ้า DevOps เปลี่ยน SSH key name ต้องแก้เหมือนกัน
- **CDC DELETE tierCode** — CLOSED (2026-03-02): keep tierCode matching as-is. Source sends wrong = source's problem.
- **DoFns alignment with messaging** — members/purchases ใช้ `AttachEventNameDoFn`+`BuildRawEventDoFn` (raw Kafka bytes, attach event name from topic). messaging ใช้ `FilterEventNameDoFn`+`FilterValidEventFieldsDoFn` (event มี eventName มาแล้ว, filter แทน). ถ้าวันนึงต้อง align ให้เหมือน messaging → เพิ่ม Filter DoFns แทน Attach. See `memory/dofns_comparison.md`
- **Verify Schema B/C fix in PROD** — user showed PROD log with old behavior, unclear if fix deployed yet
- **Remove debug logger.info in dofns.py** — lines 107+140 log every message (very noisy), should be debug level
- **STG→PROD dependency chain** — add `needs: deploy:stg` to deploy:prod
- **members drain-first** — upgrade cancel to drain-then-cancel (like purchases)
- **BQ backup before deploy-tables:prod** — prevent data loss on schema changes
- **DLQ implementation** — `docs/dlq/DLQ_CHECKLIST.md`
- **Dataplex setup** — Enable API, create Lake/Zone
- **transaction/biglake-metastore.tf** — remove cross-collector grants after collector IAM deployed
- **Kafka schema: eligibleTierCode migration** — New fields in Kafka payload, code written with comments (pending confirm to uncomment). See `memory/kafka_schema_changes.md`
- **Init data migration** — DTS S3->BQ (blocked on AWS perm), then BQ->BQ + BQ->Iceberg pipeline needed
- **Source Iceberg `timestamp` column** — ปัจจุบันเป็น STRING (epoch string เช่น "1771773636") อาจเปลี่ยนเป็น INT ในอนาคต (members-collector + tiers-collector, m-t-h ไม่มี column นี้)

## Key Technical Patterns
- job_type: `normal` = streaming, `initial_data` = batch
- **member_tier/maintenance**: `ingestedTHDate` INT YYYYMMDD (Iceberg) / DATE DAY (BQ refined)
- **tier_events**: `etlLoadTime` INT YYYYMMDDHH (Iceberg) / TIMESTAMP HOUR (BQ refined)
- BQ Storage Write API: MUST use `apache_beam.utils.timestamp.Timestamp` NOT datetime
- CDC Mode: prod `write_mode: cdc`, stg `write_mode: append`

### Bangkok Timezone +7 (MUST follow for ALL refined timestamps)
- **Source (Iceberg)**: `iceberg_writer.py` → `_BANGKOK_TZ = timezone(timedelta(hours=7))`
  - member_tier/maintenance: `_get_ingested_th_date()` → INT YYYYMMDD Bangkok
  - tier_events: `_get_etl_load_time()` → INT YYYYMMDDHH Bangkok
- **Refined (BQ)**: TIMESTAMP fields use Beam Timestamp with +7h offset; DATE fields use `"%Y-%m-%d"` string
  - `ingestedTHDate` (member_tier/maintenance): `datetime.now(_BANGKOK_TZ).strftime("%Y-%m-%d")` → DATE
  - `etlLoadTime` (tier_events): `Timestamp(micros=now + _BANGKOK_OFFSET_MICROS)` → TIMESTAMP
- **members-collector**: transform_dofns.py ✓ (all DoFns apply +7)
- **tiers-collector**: transform_dofns.py ✓ (fixed 2026-02-17)
- **members-tiers-history**: transformers.py `convert_for_bigquery()` ✓ (fixed 2026-02-17)
- **CDC path** (members): `.to_utc_datetime()` preserves +7 — offset baked into Timestamp micros

## Sales-Collector (2026-03-09)
- **GCP Project**: `the1-sales-data-stg`/`the1-sales-data-prod`
- **Iceberg**: `ManagedIcebergWriteConfig` + `IcebergSink` (aligned with members pattern 2026-02-26)
- **TF**: `external_catalog_dataset_options` removed, `biglake.editor` (not admin)
- **BQ refined CDC**: ACTIVE — 3 tables (receipt/sku/tender) write via CDC upsert
- **CDC fix (2026-03-09)**: ลบ Z suffix จาก strftime → BQ DATETIME accept
- **Timestamp parse fix (2026-03-09)**: DDMMYYYY fallback (try YYYYMMDD first, then DDMMYYYY)
- **Initial data load**: `--job_type=initial_data` → ReadFromBQ(prev_raw_sales) → managed.Write(ICEBERG) (148 tests)
- **BLMS cleanup**: `_cleanup_blms_entry()` REMOVED — user does manual via `blms_helper 1.py`
- **Partition fields**: `["ingestedTHDate", "ingestedTHHour"]` (2 fields, unlike loyalty's 1 field)
- **Docs**: `memory/sales_knowledge_base.md`, `memory/sales_initial_data.md`

### Checklist: Rename date/datetime columns (sales-collector)
**Reason**: Column names ควรสะท้อน data type จริง — columns ที่มี time ต้องลงท้าย `_datetime`
| Column เดิม | Source data | Action |
|---|---|---|
| `trans_date` | `2026-02-23T03:04:00.342Z` (has time) | → `trans_datetime` |
| `business_date` | `2026-02-22T17:00:00Z` (has time) | → `business_datetime` |
| `invoice_date` | `23022026` (date only) | ✅ keep |
| `delivery_date` | `23022026` (date only) | ✅ keep |
| `etl_updated_date` | runtime Bangkok datetime | → `etl_updated_datetime` |

**Files to change** (all 3 tables: receipt/sku/tender):
- [ ] `schemas/sales_receipt.json`, `sales_sku.json`, `sales_tender.json` — column name rename
- [ ] `schemas.py` — SALES_RECEIPT_SCHEMA, SALES_SKU_SCHEMA, SALES_TENDER_SCHEMA
- [ ] `bq_transformers.py` — `_extract_header_fields()` dict keys
- [ ] `base.yaml` / `stg.yaml` / `prod.yaml` — primary_key list (trans_date → trans_datetime)
- [ ] `config/bigquery_sales_config.py` — if partition_field references trans_date
- [ ] `builder.py` — if any hardcoded references
- [ ] Tests — update all test fixtures/assertions
- [ ] **BQ table**: BREAKING change → deploy.py backup+recreate (หรือ ALTER RENAME COLUMN ถ้า BQ support)
- [ ] **Partition**: `PARTITION BY DATE(trans_datetime)` ยังใช้ได้เหมือนเดิม

### Checklist: BQ Lookup/Enrichment for calculated columns (sales-collector)
**Solution**: Technique 7 — Shared In-process Cache (Singleton per worker)
**Research doc**: `the1-re-data-platform/doc/dataflow/BQ_LOOKUP_TECHNIQUES.md` (DONE)
**Why Singleton over Side Input**: ไม่ block watermark, simple (ไม่ต้อง pipeline branch), cost ต่ำ, failure-resilient (ใช้ stale data ต่อ)

**DONE (infrastructure)**:
- [x] `bq_lookup_cache.py` — `MasterCache` class (thread-safe, auto-refresh, atomic swap)
- [x] `enrich_dofns.py` — `EnrichSalesDoFn` (lookup sales_channel → TODO: add columns)
- [x] `settings.py` — `LookupTableConfigDto`, `LookupConfigDto`
- [x] `pipeline_config.py` — `lookup_config: LookupConfig`
- [x] `configuration_adapter.py` — wire lookup config
- [x] `main.py` — create `MasterCache`, inject into builder
- [x] `builder.py` — enrich step between transform → write (conditional on config)
- [x] `base.yaml` — `lookup` section (sales_channel_branch, key=sales_channel, refresh 1hr)
- [x] Tests: 11 cache + 4 enrich = 15 new tests (134 total pass)

**TODO (when column mapping is known)**:
- [ ] `enrich_dofns.py` — เติม column mapping ใน `EnrichSalesDoFn.process()` (ตอนนี้ lookup แล้วแต่ยัง pass)
- [ ] `schemas.py` + JSON schemas — เพิ่ม calculated columns
- [ ] `base.yaml` — `value_columns` (ระบุ columns ที่ต้องการ ลด BQ scan)
- [ ] เพิ่ม lookup tables อื่นๆ (รวม ~5 tables) — เพิ่มใน yaml + enrich logic
- [ ] `stg.yaml` / `prod.yaml` — override `full_table_id` per env ถ้า project ต่างกัน
- [ ] Tests: enrich with actual column mapping
- [ ] **Tests**: test enrichment logic + cache refresh
- [ ] **Deploy**: deploy new columns (ADDITIVE change — ALTER TABLE ADD COLUMN)

### Checklist: Migrate sales BQ write to common BigQueryWriterAdapter
- [ ] **common**: เพิ่ม `from decimal import Decimal` + `elif isinstance(v, Decimal): str(v)` ใน `_WrapCdcRowDoFn`
- [ ] **common**: เพิ่ม `"NUMERIC"` ใน `_wrap_schema_for_cdc` temporal_types set
- [ ] **common**: verify tests pass with Decimal/NUMERIC changes
- [ ] **sales main.py**: uncomment `BigQueryWriterAdapter`/`BigQueryWriterConfig` imports (line 19-20)
- [ ] **sales main.py**: rename `_create_bq_sink` → use `_create_bq_sink_common` (commented code ready)
- [ ] **sales bigquery_sink.py**: can be removed (replaced by common `BigQueryWriterAdapter`)
- [ ] **sales bigquery_storage.py**: can be removed (replaced by common `bigquery_writer.py`)
- [ ] Run tests: `uv run pytest tests/ -q` + `ruff` + `mypy`

## Common Errors & Fixes
| Error | Fix |
|-------|-----|
| OOM on GitLab Runner | Use Dataflow batch (`job_type=initial_data`) |
| Ruff RUF043 (regex) | Use raw string: `match=r"kafka\.topics"` |
| pre-commit purchases-collector fail | pyarrow 17.0.0 + Python 3.13 issue (ignore) |
| Managed transform artifact staging fail | เพิ่ม `--staging-location` + `--temp-location` ใน deploy (ชี้ GCS bucket ที่ SA มีสิทธิ์) |
| pre-commit modifies transactions-collector | `ruff format` fixes trailing whitespace in `pipeline_config.py` — MUST `git checkout -- transactions-collector/` after every pre-commit |

## File Locations
```
{collector}/src/domain/
├── blms_catalog_config.py           # BLMS REST active, Hadoop commented
├── managed_iceberg_write_config.py  # BLMS REST active, Hadoop commented

{collector}/src/adapters/output/
├── iceberg_writer.py       # write_to_iceberg(config=ManagedIcebergWriteConfig, ...)
├── iceberg_sink.py         # IcebergSink(config, schema, row_mapper)
├── bq_metadata_refresh.py  # Option B refresh (DISABLED, module kept)

infrastructure/{members,tiers,members-tiers-history}/
├── artifact.tf             # GAR repo per-collector
├── bucket.tf               # GCS bucket per-collector
├── biglake-metastore.tf    # IAM: source + refined dataset access
└── schemas/deploy.py       # Native BQ only (~370 lines, Iceberg code removed)
```
