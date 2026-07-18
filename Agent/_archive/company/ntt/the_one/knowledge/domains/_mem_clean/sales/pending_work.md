# Sales Domain -- Pending Work

> Extracted from: sales_deploy_fix.md, sales_initial_data.md, MEMORY.md, SESSION_SUMMARY.md
> Updated: 2026-04-05

---

## HIGH Priority

### 1. `sales_channel_partner` column name fix
- **Issue**: BQ table has `sales_channel_partner_name` but code references `sales_channel_partner_id`
- **Team notified**: waiting for confirmation on correct name
- **Files to check**: `base.yaml` `value_columns`, `enrich_dofns.py`, `bq_transformers.py`

### 2. Finish enrichment column mapping
- **Status**: MasterCache infrastructure DONE (cache + enrich DoFn + settings + config + tests)
- **Remaining**:
  - `enrich_dofns.py` -- fill in actual column mapping in `EnrichSalesDoFn.process()` (currently lookup then pass-through)
  - `schemas.py` + JSON schemas -- add calculated columns
  - `base.yaml` -- add `value_columns` to reduce BQ scan
  - Add remaining lookup tables (~5 total): sales_channel_tender, sales_channel_product, creditcard_master, sales_channel_sap, sales_channel_code, sales_channel_translator
  - `stg.yaml` / `prod.yaml` -- override `full_table_id` per env if cross-project
  - Tests for enrichment logic + cache refresh

---

## MEDIUM Priority

### 3. `triggering_frequency_seconds` -> 1800
- **Current**: 60s (reduced from 1800 due to OOM)
- **Need**: Upgrade worker memory first, then increase back to 1800s
- **Impact**: Lower triggering frequency = fewer Iceberg snapshots = lower storage cost

### 4. Dataform prod deploy
- **Status**: STG active, PROD pending
- **Blocker**: Needs IAM grant for `the1-partner-data-prod` + `the1-catalog-data-prod`
- **Action**: Request `bigquery.dataViewer` on partner-prod + catalog-prod for sales SA
- **Also**: Dataform assertions disabled (tag `sales_assertion_disabled`), enable after data stabilizes

### 5. Rename date/datetime columns
- **Reason**: Column names should reflect actual data type -- columns with time need `_datetime` suffix
- **Changes**:
  - `trans_date` (has time) -> `transaction_datetime`
  - `business_date` (has time) -> `business_datetime`
  - `etl_updated_date` (has time) -> `etl_updated_datetime`
  - `invoice_date` (date only) -> keep
  - `delivery_date` (date only) -> keep
- **Files**: schemas/*.json, schemas.py, bq_transformers.py, base.yaml PKs, config, builder.py, tests
- **BQ impact**: BREAKING change -> deploy.py backup+recreate

### 6. Migrate BQ write to common BigQueryWriterAdapter
- **Checklist**:
  - common: Add `Decimal` support + `"NUMERIC"` in `_wrap_schema_for_cdc`
  - sales main.py: Uncomment common adapter imports, use common sink
  - Remove sales-specific `bigquery_sink.py` + `bigquery_storage.py`
  - Run tests

---

## LOW Priority

### 7. Streaming join approach (research done)
- **Context**: Need to join with 5 large batch tables (15M rows each) for sales enrichment
- **Research**: PeriodicImpulse -> BQ query, MV, Views, Bigtable/Redis
- **User preference**: No-extra-instance approach (in-process cache, which is MasterCache)
- **Status**: MasterCache implemented (see #2 above)

### 8. Initial data load cleanup
- **Feature DONE**: `--job_type=initial_data` -> ReadFromBQ(prev_raw_sales) -> managed.Write(ICEBERG)
- **Remaining after migration**:
  - Verify row counts match
  - Disable `init_data` in config
  - Clean up `prev_raw_sales` external table

### 9. deploy.py max_staleness INTERVAL
- **Fixed**: `INTERVAL '0'` -> `INTERVAL '0:0:0' HOUR TO SECOND`
- **Apply to**: Check other domain deploy.py files if they have same bug

---

## FUTURE / BACKLOG

### 10. DLQ implementation
- Currently: all DoFns try/except -> log -> drop
- Future: DLQ for failed messages (see loyalty DLQ research patterns)

### 11. Remove DebugLogDoFn
- Active as temporary debug aid
- Remove when BQ writes are fully verified in production

### 12. Comment out _cleanup_blms_entry()
- **Status**: Already REMOVED from main.py (user does manual via `blms_helper 1.py`)
- No action needed

### 13. Common library update
- `common-data-python` tag 0.0.33 pending
- May include shared `_WrapCdcRowDoFn` improvements (Decimal support)
