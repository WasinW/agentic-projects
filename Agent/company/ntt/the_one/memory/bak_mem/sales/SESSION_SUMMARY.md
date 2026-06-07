# Sales Collector — Session Summary

> Exported: 2026-04-05
> Domain: sales-collector (streaming pipeline)
> Session: Multi-session spanning 2026-03-17 to 2026-04-01+

---

## a. Session Owner & Role

| Key | Value |
|-----|-------|
| Name | Wasin |
| Role | Data Engineer / Platform Engineer |
| Language | Thai (primary), English (code/docs) |
| Working Style | Fast-paced, direct, expects concise answers. Prefers action over explanation. Reviews code carefully before push. Manages multiple domains (loyalty, sales, catalog, insight). |
| Preference | "สั้น กระชับ ลงมือทำ — ไม่ต้องอธิบายยาว" |
| Git Policy | User handles git add/commit/push manually. Agent must NOT run git commands. |

---

## b. Project Overview

| Key | Value |
|-----|-------|
| GCP Project | `the1-sales-data-{stg,prod}` |
| Repo | `gitlab.com/The1central/The1/the1-data/sales-data` |
| Local Path | `/Users/wasin/Documents/ntt_project/the_one/realproject/sale/sales-data/` |
| Collector Path | `sale/sales-data/sales-collector/` |
| Language | Python 3.12 |
| Framework | Apache Beam 2.71.0 on Google Cloud Dataflow |
| Build | `uv` (package manager), `ruff` (linter), `mypy` (type checker), `pytest` (tests) |
| CI/CD | GitLab CI → Kaniko build → GAR → Dataflow deploy |
| Dataform | `sales-collector/dataform/` — public views on refined tables |
| BLMS Scripts | `/realproject/blms_scripts/` — BigLake Metastore management |

---

## c. Architecture

```
┌─────────────┐    ┌──────────────────────┐    ┌────────────────┐    ┌──────────────┐
│  Kafka       │───>│  sales-collector     │───>│  Iceberg       │───>│  BQ Source    │
│  (loyalty.   │    │  (Dataflow streaming)│    │  (GCS via BLMS │    │  (data col)  │
│   sales.*)   │    │                      │    │   REST catalog)│    │              │
└─────────────┘    │  ┌─────────────┐     │    └────────────────┘    └──────────────┘
                   │  │ Enrich DoFn │     │
                   │  │ (MasterCache│     │    ┌────────────────┐    ┌──────────────┐
                   │  │  BQ lookup) │     │───>│  BQ Refined    │───>│  BQ Public   │
                   │  └─────────────┘     │    │  (CDC UPSERT)  │    │  (Dataform   │
                   │                      │    │  - sales_receipt│    │   views)     │
                   └──────────────────────┘    │  - sales_sku   │    └──────────────┘
                                               │  - sales_tender│
                                               └────────────────┘

Source: Kafka topics: loyalty.sales.created, loyalty.sales.updated
Format: {"value": {eventId, source, eventName, timestamp, payload:{...}}, "headers": [{key, value}]}
Sink: 
  - Iceberg source tables (raw JSON in `data` column)
  - BQ refined tables (3 tables: receipt, sku, tender) via Storage Write API CDC
  - BQ public views (Dataform) — JOIN with partner + catalog cross-project tables
```

---

## d. Components Managed

| Component | Mode | Source | Sink | Status |
|-----------|------|--------|------|--------|
| sales-collector | Streaming | Kafka (loyalty.sales.*) | Iceberg + BQ refined | PROD active |
| Dataform (sales) | CI-triggered | BQ refined | BQ public (views) | STG active, PROD pending IAM |
| BLMS scripts | Manual CLI | BigLake Metastore | Snapshot management | Active |
| deploy.py | CI-triggered | JSON schemas | BQ refined tables (DDL) | Active |

---

## e. Key Technical Decisions

### 1. Source table format: `{"value": {...}, "headers": [...]}`
- **Why**: Need Kafka headers (e.g. `source: "RIS"`) for downstream enrichment
- **How**: `_SafeDecodeWithHeadersDoFn` attaches `_kafka_headers` to decoded dict, `build_raw_event` wraps as `{"value": inner, "headers": kafka_headers}`
- **Impact**: `_extract_sales_payload()` handles both old format (flat) and new format (value+headers)

### 2. MasterCache with force-refresh-on-miss (Option 2)
- **Why**: DTS sync delays cause cache misses when Kafka messages arrive before master data in BQ
- **How**: `_try_force_refresh()` with cooldown (30s default), `retry_on_miss` config flag
- **Alternative rejected**: Redis/Bigtable (too much infra overhead), jittered refresh (not needed with few workers)

### 3. BLMS REST Catalog for Iceberg writes
- **Why**: BigLake Metastore is the managed Iceberg catalog on GCP
- **How**: `BlmsCatalogConfig` → `ManagedIcebergWriteConfig` → `managed.Write`
- **Pattern**: Identical to messaging-collector (loyalty domain)

### 4. CDC UPSERT for refined tables
- **Why**: Same receipt can be sent multiple times (created + updated), need dedup
- **How**: `write_mode: "cdc"` + primary_key in base.yaml → Storage Write API CDC mode

### 5. Sign-flip for return transactions
- **Why**: RETURN/VOID types need negative quantities/amounts
- **Types**: `RETURN_NORMAL`, `RETURN_DEPOSIT`, `VOID`, `VOID_SALE_DEPOSIT`
- **Fields flipped**: quantity, subtotal_price, net_subtotal_price, unit_discount, amount, totals

### 6. Dataform public views with cross-project JOINs
- **Why**: Public layer needs partner branch info + product catalog
- **How**: `external_sources.js` with `dataform.projectConfig.vars.{partner_project,catalog_project}`
- **Env switch**: CI template regex replaces `-stg` → `-prod` in vars automatically

### 7. Future date filter
- **Why**: Source system occasionally sends incorrect future transactionDate
- **How**: `_is_future_transaction()` filters dates > tomorrow (Bangkok time)

---

## f. Completed Work

### Production Fixes
- `'int' object has no attribute 'encode'` — `str()` conversion in enrichment_logic.py
- Schema B/C nested payload fix in transformers.py
- deploy.py `INTERVAL '0'` syntax fix for max_staleness
- deploy.py clustering bug fix

### Schema & Logic Changes
- Column renames: `receipt_no` → `receipt_number`, `trans_type` → `sale_type_code`, etc.
- Sign-flip types: numeric codes → descriptive names (`RETURN_NORMAL`, `VOID`, etc.)
- Filter: `CEN` partner + `SALE_CLEAR_DEPOSIT` excluded
- Future date filter: transactionDate > tomorrow filtered out
- `event_id` column added to all 3 refined tables
- `ca_sales_channel_chg`, `storage_location`, `channel_type`, `sap_channel`, `online_order_id` added
- `display_receipt_no_2` from `references[SECOND_DISPLAY_RECEIPT_NUMBER]`
- `credit_card` validation (BIN extraction, length 14-19, XXXX pattern)
- `issuer_bank` via creditcard_master range lookup
- SKU channel fields: `sales_channel_main`, `sales_channel_assist`, `sales_info`, `sales_channel_platform`
- Sales channel priority reorder: Tender > Branch (match SQL)
- Tender MIN across all payments (not first match)
- Numeric COALESCE to 0, string COALESCE to ''

### Infrastructure & CI
- Kafka headers extraction (`_SafeDecodeWithHeadersDoFn`)
- Source table format change: flat → `{"value": {...}, "headers": [...]}`
- MasterCache force-refresh-on-miss (Option 2)
- BLMS `compact-snapshots` command added
- `triggering_frequency_seconds` reduced to 60s (from 1800s due to OOM)
- Dataform setup: views, assertions, CI pipeline, cross-project vars
- Sonar scan cognitive complexity fixes (6 functions refactored)
- CVE fixes: pyasn1 >= 0.6.3, grpc boot binary, libc6

### Documentation
- `SALES_ENRICHMENT_LOGIC.md` (V1 → V2 → V3)
- `DATAFLOW_VS_SQL_CHECKLIST.md`
- `STREAMING_ENRICHMENT_DEEP_DIVE.md`
- `STREAMING_BATCH_JOIN_RESEARCH.md`
- `BQ_CDC_MERGE_COMPATIBILITY.md`
- CVE documentation in `scancode/issue/`

---

## g. Pending Work

| # | Task | Priority | Notes |
|---|------|----------|-------|
| 1 | `sales_channel_partner` column name fix | HIGH | BQ table has `sales_channel_partner_name` not `sales_channel_partner_id` — team notified |
| 2 | `triggering_frequency_seconds` → 1800 | MEDIUM | Need upgrade worker memory first (OOM at 1800s) |
| 3 | Streaming join approach | LOW | Research done (PeriodicImpulse → BQ query, MV, Views). User leaning toward no-extra-instance approach |
| 4 | Dataform prod deploy | MEDIUM | Needs IAM grant for partner-prod + catalog-prod |
| 5 | Dataform assertions | LOW | Disabled (tag `sales_assertion_disabled`), enable after data stabilizes |

---

## h. Memory Files Exported

| File | Description |
|------|-------------|
| `MEMORY.md` | Index of all memory files |
| `mistakes_and_rules.md` | Errors to avoid + working rules |
| `feedback_verify_before_answer.md` | User feedback: always verify code before answering |
| `sales_knowledge_base.md` | Sales collector architecture + patterns |
| `sales_pipeline_knowledge_base.md` | Pipeline flow details |
| `sales_schema_migration.md` | Schema migration plan (column renames, logic changes) |
| `sales_schema_migration_done.md` | Completed migration items |
| `sales_deploy_fix.md` | Deploy.py fixes and patterns |
| `sales_initial_data.md` | Initial data load approach |
| `kafka_schema_changes.md` | Kafka schema (eligibleTierCode) + init data migration |
| `loyalty_knowledge_base.md` | Loyalty domain KB (collectors, infra, schemas) |
| `catalog_products_knowledge_base.md` | Catalog/products-collector setup KB |
| `insight_knowledge_base.md` | Insight domain KB |
| `dofns_comparison.md` | DoFn patterns comparison across collectors |

---

## i. Key Rules

### MUST FOLLOW
1. **No git commands** — user handles git add/commit/push manually
2. **Must run after code changes**: `uv sync`, `ruff check .`, `mypy .`, `uv run poe test:cov`, `uv run pre-commit run --all-files`
3. **Focus on sales-collector** — other collectors are reference only
4. **Read code before answering** — never guess, always verify
5. **Don't over-explain** — be concise, act fast

### Validation Steps
```bash
cd sale/sales-data/sales-collector
uv sync
uv run ruff check .
uv run mypy .
uv run poe test:cov
uv run pre-commit run --all-files
```

### Path Rules
- Sales collector: `sale/sales-data/sales-collector/`
- Dataform: `sale/sales-data/sales-collector/dataform/` (inside collector, NOT repo root)
- Deploy scripts: `sale/sales-data/scripts/` (deploy_dataform.sh, dataform_api.py)
- Schemas (deploy): `sale/sales-data/infrastructure/sales-collector/schemas/`
- BQ write schemas (code): `sale/sales-data/sales-collector/src/domain/schemas.py`
- Config: `sale/sales-data/sales-collector/config/{base,stg,prod}.yaml`
- CI: `sale/sales-data/sales-collector/.gitlab-ci.yml`
- Root CI: `sale/sales-data/.gitlab-ci.yml`
- Dataform template: `sale/sales-data/.gitlab/ci/dataform-template.gitlab-ci.yml`

---

## j. Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `'int' object has no attribute 'encode'` | MasterCache returns raw BQ types (int for INTEGER) | `str()` conversion in all resolve functions |
| `Table metadata is too large` | Too many Iceberg snapshots | `compact-snapshots` or `expire-snapshots` via blms_helper.py |
| OOM (Out of Memory) | `triggering_frequency_seconds` too high (1800s) | Reduce to 60s or upgrade worker memory |
| `Invalid INTERVAL value '0'` | deploy.py syntax `INTERVAL '0' HOUR TO SECOND` | Change to `INTERVAL '0:0:0' HOUR TO SECOND` |
| Dataform `Access Denied` cross-project | Missing IAM grant for cross-project BQ access | Grant `bigquery.dataViewer` to SA on target project |
| Dataform `Unrecognized name: event_id` | Column not yet in BQ table | Run deploy-tables first, or ALTER TABLE ADD COLUMN |
| `event_id` not written to refined | Missing from `schemas.py` `_HEADER_FIELDS` | Add `{"name": "event_id", ...}` to `_HEADER_FIELDS` |
| Cache miss / stale data | BQ master data not yet synced when Kafka msg arrives | Force-refresh-on-miss (Option 2) in MasterCache |
| `sales_channel_partner_id` not found | Wrong column name in base.yaml | Check BQ table schema, fix `value_columns` |
| CI grep fail (deploy:prod) | `image-digest-ref.txt` has STG path, grep for "prod" fails | Fix grep validation or use correct file |
| Unit test `DefaultCredentialsError` | `retry_on_miss` triggers BQ client in test env | Add `retry_on_miss=False` to LookupConfig in tests |

---

## k. Cross-Domain Dependencies

| Dependency | Direction | Details |
|------------|-----------|---------|
| `common-python-dataflow` | sales ← common | Shared Beam adapters (KafkaReader, DecodeMessageDoFn). Common library tag: 0.0.33 pending |
| `the1-partner-data` | sales → partner (read) | Dataform views JOIN `companies_branch_brand_cg_location`. Needs IAM cross-project grant. |
| `the1-catalog-data` | sales → catalog (read) | Dataform views JOIN `ms_product_all`. Needs IAM cross-project grant. |
| `blms_scripts` | sales uses | Shared BigLake Metastore CLI at `/realproject/blms_scripts/`. Added `compact-snapshots` command. |
| `loyalty-data` (purchases) | reference | Purchases-collector used as pattern reference for CI, dataform, deploy scripts |
| Kafka (loyalty.sales.*) | upstream → sales | Topics: `loyalty.sales.created`, `loyalty.sales.updated`. Schema: Avro/JSON with value+headers wrapper |
| BQ refined master tables | upstream → sales | DTS-synced from AWS: `sales_channel_branch`, `sales_channel_tender`, `sales_channel_product`, `creditcard_master`, `sales_channel_partner`, `sales_channel_sap`, `sales_channel_code`, `sales_channel_translator` |
