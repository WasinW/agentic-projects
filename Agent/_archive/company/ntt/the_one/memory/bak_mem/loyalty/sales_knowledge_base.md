# Sales Collector - Knowledge Base

## Created: 2026-02-19
## Updated: 2026-02-23
## Purpose: Comprehensive reference for sales-collector — VERIFIED from actual code

---

## 0. Current State (2026-02-23)

**Sales-collector pipeline RUNNING on Dataflow STG** — Iceberg writing, BQ refined COMMENTED.

### What's Active
- Kafka → Dataflow (streaming) → Iceberg source layer
- 2 Kafka topics: `loyalty.sales.created` + `loyalty.sales.updated`
- Single managed.Write → `raw_sales` table (both topics merged)
- BLMS REST Catalog + vended-credentials (same as messaging/loyalty)
- Full CI/CD pipeline active (build + deploy-stg + deploy-prod)
- Full Terraform infrastructure deployed (buckets, GAR, BLMS catalog, BQ datasets, secrets)

### GCP Projects
- **STG:** `the1-sales-data-stg`
- **PROD:** `the1-sales-data-prod`

### What's Still Commented/Disabled
- **BQ refined writes** — code exists in builder.py but COMMENTED (debug mode)
- **DebugLogDoFn** — active (temporary, remove when enabling BQ writes)
- **Per-topic Kafka branching** — commented (single merged write avoids Dataflow upgrade error)
- **pubsub.tf** — commented (future use)

### BLMS Cleanup
- `_cleanup_blms_entry()` in main.py — ACTIVE (one-time, drops stale BLMS entries)
- Runs inside Dataflow (GitLab CI SA lacks Service Usage Consumer)
- Comment out after first successful deploy

### Key Lessons (CRITICAL)
1. `--staging-location` + `--temp-location` ต้องส่งให้ deploy_dataflow.sh (managed transform needs GCS staging)
2. `table_properties.location` ใช้ได้แค่ตอน CREATE — stale BLMS entry ต้อง drop ก่อน
3. BLMS catalog SA ต้องมี `storage.objectAdmin` บน source bucket

---

## 1. Project Location & Structure

**Root:** `/Users/wasin/Documents/ntt_project/the_one/realproject/sale/sales-data/`

```
sale/sales-data/
├── .gitlab-ci.yml              # Top-level CI (includes collector + common)
├── .pre-commit-config.yaml     # gitleaks, ruff, terraform, pytest hooks
├── .gitleaks.toml              # Secret scanning config
├── README.md                   # Project template
├── sales-collector/            # Main application
│   ├── .gitlab-ci.yml          # Collector-level CI (build → deploy-stg → deploy-prod)
│   ├── Dockerfile              # Multi-stage (uv builder + Dataflow launcher + Java 17)
│   ├── pyproject.toml          # Python >=3.12, apache-beam==2.70.0
│   ├── README.md               # Dev quick-start
│   ├── config/
│   │   ├── base.yaml           # Shared config (kafka, iceberg, bq, etc.)
│   │   ├── stg.yaml            # STG overrides (project, warehouse)
│   │   └── prod.yaml           # PROD overrides
│   ├── src/
│   │   ├── main.py             # Composition root + BLMS cleanup
│   │   ├── domain/
│   │   │   ├── models.py       # RawEvent, IntermediateEvent TypedDicts
│   │   │   ├── schemas.py      # PyArrow (Iceberg) + BQ schemas (3 tables)
│   │   │   ├── validators.py   # Shared validation helpers
│   │   │   ├── transformers.py # Kafka→RawEvent pure functions
│   │   │   ├── bq_transformers.py  # RawEvent→BQ rows (receipt/sku/tender)
│   │   │   └── config/
│   │   │       ├── pipeline_config.py        # PipelineConfig (Pydantic)
│   │   │       └── bigquery_sales_config.py  # Per-table BQ config
│   │   ├── adapters/
│   │   │   ├── input/configuration/
│   │   │   │   ├── settings.py               # Pydantic DTOs
│   │   │   │   ├── configuration_adapter.py  # YAML→PipelineConfig
│   │   │   │   ├── logging_adapter.py        # Structured logging with run_id
│   │   │   │   └── secret_adapter.py         # GCP Secret Manager
│   │   │   └── output/
│   │   │       ├── gcs/
│   │   │       │   ├── biglake_metastore_config.py      # BlmsCatalogConfig (frozen dataclass)
│   │   │       │   ├── gcs_biglake_iceberg_writer_config.py  # GcsIcebergWriterConfig
│   │   │       │   └── gcs_biglake_iceberg_writer.py    # GcsIcebergWriter PTransform
│   │   │       └── bigquery/
│   │   │           ├── bigquery_writer_config.py   # BigQueryWriterConfig
│   │   │           └── bigquery_writer.py          # BigQueryWriterAdapter PTransform
│   │   └── application/
│   │       ├── row_mappers.py  # dict→beam.Row converters
│   │       └── pipeline/
│   │           ├── builder.py  # PipelineBuilder (orchestrates full pipeline)
│   │           └── dofns.py    # Beam DoFns with metrics
│   └── tests/
│       ├── conftest.py         # Fixtures (sample payloads, events)
│       └── unit/               # Unit tests
├── infrastructure/sales-collector/
│   ├── main.tf                 # Provider google ~>7.17.0, backend GCS
│   ├── variables.tf            # region, domain="sales-data", service_name="sales-collector"
│   ├── gcs-bucket.tf           # Source + config buckets (+ BLMS SA IAM)
│   ├── artifact-registry.tf    # GAR Docker repo
│   ├── secret-manager.tf       # Secret container
│   ├── biglake-metastore.tf    # BLMS Iceberg catalog + vended-credentials
│   ├── bigquery.tf             # Source (external_catalog) + refined datasets
│   ├── pubsub.tf               # COMMENTED (future)
│   ├── schemas/
│   │   ├── deploy.py           # BQ table deployer (native + external Iceberg)
│   │   ├── raw_sales.json      # Source: external_iceberg, 6 fields
│   │   ├── sales_receipt.json  # Refined: native, 31 fields, MONTH partition
│   │   ├── sales_sku.json      # Refined: native, 34 fields, MONTH partition
│   │   └── sales_tender.json   # Refined: native, 27 fields, MONTH partition
│   └── templates/
│       └── container_spec.json # Dataflow Flex Template spec
└── scripts/
    ├── prepare_dataflow_config.sh  # Merge YAML → base64
    ├── prepare_dataflow_spec.sh    # Render template + upload GCS
    └── deploy_dataflow.sh          # Smart deploy (update/drain/fresh)
```

---

## 2. Configuration (VERIFIED from actual files)

### base.yaml
```yaml
secret_name: "sales-collector"
window_size_seconds: 5
message_format: "auto"
kafka_topics: [loyalty.sales.created, loyalty.sales.updated]
kafka_group_id: "sales-data-sales"
blms_rest_uri: "https://biglake.googleapis.com/iceberg/v1/restcatalog"
blms_namespace: "source"
iceberg_tables:
  loyalty.sales.created: raw_sales_created
  loyalty.sales.updated: raw_sales_updated
triggering_frequency_seconds: 300
region: "asia-southeast1"
refined:
  dataset_id: "refined"
  sales_receipt: {enable: true, partition: MONTH on trans_date, clustering: [partner_code, member_number, branch_code]}
  sales_sku: {enable: true, partition: MONTH on trans_date, clustering: [partner_code, sku_code, member_number]}
  sales_tender: {enable: true, partition: MONTH on trans_date, clustering: [partner_code, tender_type, member_number]}
```

### stg.yaml
```yaml
project: "the1-sales-data-stg"
iceberg_warehouse: "gs://the1-sales-data-source-stg"
log_level: "DEBUG"
```

### prod.yaml
```yaml
project: "the1-sales-data-prod"
iceberg_warehouse: "gs://the1-sales-data-source-prod"
log_level: "INFO"
```

---

## 3. Pipeline Architecture (VERIFIED)

```
Kafka (2 topics) → ReadFromKafka (merged)
    → ApplyWindow(FixedWindows(5s))
    → AttachEventName → BuildRawEvent
    → DebugLog (active, temporary)
    → WriteToIceberg (single managed.Write → raw_sales)
    → [COMMENTED] Fan-out to 3 BQ tables:
        Map(to_receipt_row) → BigQueryWriterAdapter → sales_receipt
        FlatMap(to_sku_rows) → BigQueryWriterAdapter → sales_sku
        FlatMap(to_tender_rows) → BigQueryWriterAdapter → sales_tender
```

### Key Design Decisions
- **Single managed.Write** — multiple managed.Write causes Dataflow upgrade error
- **Both topics merged** — no per-topic branching (simplifies pipeline)
- **Monthly BQ partitioning** — trans_date MONTH (not DAY like purchases)
- **Clustering per table** — different clustering fields per table
- **Schema B only** — filters out Schema A messages, keeps wrapped events

---

## 4. Domain Layer (VERIFIED)

### models.py
- `RawEvent(TypedDict)`: eventId, source, eventName, timestamp, payload(JSON str), etlLoadTime(YYYYMMDDHH)
- `IntermediateEvent(TypedDict)`: eventName, payload(dict)

### schemas.py
- `RAW_EVENT_FIELDS`: [(eventId, str), (source, str), ..., (etlLoadTime, int)]
- `RAW_SALES_SCHEMA`: PyArrow schema for Iceberg
- `SALES_RECEIPT_SCHEMA`: 31 BQ fields
- `SALES_SKU_SCHEMA`: 34 BQ fields
- `SALES_TENDER_SCHEMA`: 27 BQ fields

### transformers.py
- `is_avro_message()` — magic byte 0x00 detection
- `extract_value()` — handle Kafka record formats
- `safe_decode_and_parse()` — bytes → JSON
- `attach_event_name()` — wrap in IntermediateEvent
- `build_raw_event()` — Schema B unwrap → RawEvent envelope

### bq_transformers.py
- `to_receipt_row(RawEvent) → dict` — 1:1 (1 row per event)
- `to_sku_rows(RawEvent) → list[dict]` — 1:N (items array)
- `to_tender_rows(RawEvent) → list[dict]` — 1:M (tenders array)
- Bangkok timezone +7h: `_BANGKOK_OFFSET_SECONDS = 25200`
- Avro unwrapping: `unwrap_avro_value()`, `unwrap_avro_array()`

---

## 5. Adapters (VERIFIED)

### Input: Configuration
- `settings.py` — Pydantic DTOs (DataflowConfigDto, RefinedTableConfig, WriteMode enum)
- `configuration_adapter.py` — base64 YAML → validate → fetch secrets → build PipelineConfig
- `logging_adapter.py` — structured logging with run_id
- `secret_adapter.py` — GCP Secret Manager wrapper

### Output: Iceberg (BLMS REST)
- `biglake_metastore_config.py` — BlmsCatalogConfig (frozen dataclass)
  - `build_catalog_properties()` → REST + GoogleAuthManager + vended-credentials
- `gcs_biglake_iceberg_writer_config.py` — GcsIcebergWriterConfig
  - `writer_config` property → dict for managed.Write
  - Includes `partition_fields: ["etlLoadTime"]`
- `gcs_biglake_iceberg_writer.py` — GcsIcebergWriter PTransform
  - Single managed.Write(managed.ICEBERG, config=writer_config)

### Output: BigQuery
- `bigquery_writer_config.py` — BigQueryWriterConfig dataclass
- `bigquery_writer.py` — BigQueryWriterAdapter wrapping WriteToBigQuery

---

## 6. CI/CD Pipeline (VERIFIED)

### Top-level `.gitlab-ci.yml` (sales-data/)
- Stages: build → deploy-stg → test-stg → deploy-prod → test-prod → rollback
- Includes: sales-collector + common-data external pipeline
- Variables: TRIGGER_EVENT, ENVIRONMENT, SERVICE_NAME

### Collector `.gitlab-ci.yml` (sales-collector/)
**ALL STAGES ACTIVE:**

| Job | Stage | Status |
|-----|-------|--------|
| linter | build | ACTIVE (ruff + mypy) |
| test | build | ACTIVE (pytest + coverage) |
| create-image | build | ACTIVE (Kaniko → 4 destinations: STG+PROD) |
| sonar-scan | build | ACTIVE |
| scan-gitleaks | build | ACTIVE |
| scan-image | build | ACTIVE (trivy) |
| terraform:apply:stg | deploy-stg | ACTIVE |
| deploy-tables:stg | deploy-stg | ACTIVE |
| deploy:stg | deploy-stg | ACTIVE (max-workers 1) |
| terraform:apply:prod | deploy-prod | ACTIVE |
| deploy-tables:prod | deploy-prod | ACTIVE |
| deploy:prod | deploy-prod | ACTIVE (max-workers 2) |

**Key CI Variables:**
```
SVC_NAME: "sales-collector"
DOMAIN_NAME: "the1-sales-data"
DATAFLOW_JOB_NAME: "sales-collector"
GCP_PROJECT_ID: "the1-sales-data"
GCP_SERVICE_ACCOUNT: "t1-sales-collector"
staging-location: gs://the1-sales-data-source-{env}/dataflow/staging
temp-location: gs://the1-sales-data-source-{env}/dataflow/temp
```

---

## 7. Infrastructure Terraform (VERIFIED)

### All .tf files ACTIVE:
| File | Resources | Status |
|------|-----------|--------|
| main.tf | Provider google ~>7.17.0, backend GCS, locals | ACTIVE |
| variables.tf | region, domain="sales-data", service_name="sales-collector" | ACTIVE |
| gcs-bucket.tf | Source + config buckets, BLMS SA objectAdmin | ACTIVE |
| artifact-registry.tf | GAR Docker repo | ACTIVE |
| secret-manager.tf | Secret container (manual value) | ACTIVE |
| biglake-metastore.tf | BLMS catalog + vended-credentials + workload SA admin | ACTIVE |
| bigquery.tf | Source dataset (external_catalog) + refined dataset | ACTIVE |
| pubsub.tf | Pub/Sub topic + subscription | COMMENTED |

### Naming Convention:
```
Backend:    devops-terraformstate-nonprod / the1-sales-data/services/sales-collector
Project:    the1-sales-data-{env}
SA:         t1-sales-collector@the1-sales-data-{env}.iam.gserviceaccount.com
Source:     the1-sales-data-source-{env}
Config:     the1-sales-data-config-{env}
Catalog:    the1-sales-data-source-{env} (same as bucket name)
```

---

## 8. Schema Deployment (deploy.py)

**Location:** `infrastructure/sales-collector/schemas/deploy.py`

### Capabilities:
- Native tables (CREATE TABLE with schema)
- External Iceberg tables (externalCatalogTableOptions)
- Smart change detection (NO_CHANGE / ADDITIVE / BREAKING)
- PyIceberg integration (dummy data, schema evolution)
- Option B support (create_external_catalog_table, refresh_bq_metadata)
- Data migration for breaking changes (backup → drop → create → restore)

### Table Schemas:
| File | Type | Fields | Partition | Clustering |
|------|------|--------|-----------|------------|
| raw_sales.json | external_iceberg | 6 | etlLoadTime (identity) | - |
| sales_receipt.json | native | 31 | MONTH on trans_date | partner_code, member_number, branch_code |
| sales_sku.json | native | 34 | MONTH on trans_date | partner_code, sku_code, member_number |
| sales_tender.json | native | 27 | MONTH on trans_date | partner_code, tender_type, member_number |

---

## 9. Reference Projects

### Messaging Collector (PRIMARY for TF + Iceberg)
**Path:** `message/messaging-data/`
- `messages-collector/` — code
- `infrastructure/messages-collector/` — Terraform
- Provider google ~>7.17.0 (same as sales)
- BLMS REST + vended-credentials (identical pattern)
- 5 Kafka topics, Pub/Sub + BigTable + BQ sinks
- Managed IcebergIO writer

### Purchases Collector (PRIMARY for fan-out pattern)
**Path:** `loyalty/loyalty_paralel_purchases/loyalty-data/purchases-collector/`
- 2 Kafka topics → 3 BQ tables (receipt/detail/payment)
- Same 1→N fan-out pattern as sales
- Manual Iceberg writer (different from sales)
- Avro unwrapping patterns

---

## 10. BQ Refined Schema Summary

### sales_receipt (31 fields, 1:1)
Header: receipt_no, trans_type, partner_code, branch_code, card_no, member_number, pos_no
Dates: trans_date(TIMESTAMP), business_date(TIMESTAMP), invoice_date(STRING), delivery_date(STRING)
Amount: net_price_tot(NUMERIC)
Channel: customer_type, sales_channel, return_all_flag, sales_channel_main/assist/platform, sales_info
Extra: staff_id, storage_location, channel_type, sap_channel, online_order_id
Meta: etl_updated_date(TIMESTAMP), par_month, par_day, par_hour

### sales_sku (34 fields, 1:N)
Adds: sku_code, sku_name, barcode, dept_code, dept_name, sub_dept_code, brand_code
Amount: qty, price_unit, price_tot, net_price_unit, net_price_tot, discount_tot (all NUMERIC)

### sales_tender (27 fields, 1:M)
Adds: tender_type, credit_card, issuing_bank, item_seq_no
Amount: net_price_tot(NUMERIC)

---

## 11. Documentation Index

### Sales-specific docs:
- `sale/doc/architecture/SALES_PIPELINE_ARCHITECTURE.md` — Full architecture
- `sale/doc/cicd/SALES_CICD.md` — CI/CD details
- `sale/doc/operations/SALES_OPERATIONS.md` — Runbooks
- `sale/doc/session_20260222/SESSION_SUMMARY.md` — Last session summary
- `sale/doc/claude_ai/SALES_PIPELINE_KNOWLEDGE_BASE.md` — AI context
- `sale/doc/claude_ai/IMPLEMENTATION_CHECKLIST.md` — Checklist

### Platform docs:
- `the1-re-data-platform/doc/data_platform/development/DEVELOPMENT_GUIDE.md` — Dev standards
- `the1-re-data-platform/doc/data_platform/cicd/CICD_PIPELINE.md` — CI/CD patterns
- `the1-re-data-platform/doc/data_platform/architecture/HIGH_LEVEL_ARCHITECTURE.md` — Platform arch

### Loyalty reference docs:
- `loyalty/docs/README.md` — Master index
- `loyalty/docs/option-b-migration/OPTION_B_SUMMARY.md` — Option B state
- `loyalty/docs/iceberg/BLMS_STALE_ENTRY_FIX.md` — BLMS cleanup guide
- `loyalty/docs/dlq/DLQ_RESEARCH.md` — DLQ patterns

---

## 12. Key Patterns (MUST FOLLOW)

### Bangkok Timezone +7
```python
_BANGKOK_TZ = timezone(timedelta(hours=7))
_BANGKOK_OFFSET_SECONDS = 7 * 3600
_BANGKOK_OFFSET_MICROS = _BANGKOK_OFFSET_SECONDS * 1_000_000
# Iceberg: etlLoadTime = datetime.now(_BANGKOK_TZ).strftime("%Y%m%d%H")
# BQ: Timestamp(micros=Timestamp.now().micros + _BANGKOK_OFFSET_MICROS)
```

### Avro Unwrapping
```python
unwrap_avro_value({"string": "x"}) → "x"
unwrap_avro_array({"array": [...]}) → [...]
```

### Error Handling
- All DoFns: try/except → log → drop (no DLQ yet)
- Beam metrics counters per DoFn (seen/ok/errors)

### Config Flow
```
CLI --dataflow_config=<base64 YAML>
→ Decode → Validate (Pydantic) → Fetch secrets
→ Build BlmsCatalogConfig + GcsIcebergWriterConfig + BigQuerySalesConfig
→ PipelineConfig
```
