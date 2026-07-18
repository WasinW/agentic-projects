# Sales Domain -- Knowledge Base

> Merged from: sales_knowledge_base.md + sales_pipeline_knowledge_base.md + SESSION_SUMMARY.md
> Updated: 2026-04-05

---

## 1. Solution Architecture

```
                                                    Iceberg Source
Kafka (loyalty.sales.*)                            (GCS via BLMS REST)       BQ Source
  loyalty.sales.created  ──┐                      ┌───────────────────┐    ┌──────────┐
  loyalty.sales.updated  ──┼──> sales-collector ──>│  raw_sales        │───>│ data col │
                           │   (Dataflow stream)   └───────────────────┘    └──────────┘
                           │                       
                           │   ┌─────────────┐     ┌───────────────────┐    ┌──────────┐
                           └──>│ EnrichDoFn  │────>│  BQ Refined       │───>│ Dataform │
                               │ (MasterCache│     │  (CDC UPSERT)     │    │ (public  │
                               │  BQ lookup) │     │  - sales_receipt  │    │  views)  │
                               └─────────────┘     │  - sales_sku      │    └──────────┘
                                                   │  - sales_tender   │
                                                   └───────────────────┘
```

**GCP Projects**: `the1-sales-data-stg` / `the1-sales-data-prod`
**Local Path**: `sale/sales-data/sales-collector/`
**Repo**: `gitlab.com/The1central/The1/the1-data/sales-data`

### Key Architecture Characteristics
- **Streaming** Kafka consumer (2 topics: `loyalty.sales.created`, `loyalty.sales.updated`)
- **Custom SalesKafkaReaderAdapter** (avoids MapCoder crash CVE-2025-68121)
- **Windowing**: 5-second fixed windows, 300s Iceberg flush, 60s BQ flush
- **Multi-sink**: Iceberg (2 tables) + BQ refined CDC (3 tables)
- **Enrichment**: 6-level priority chain via MasterCache BQ lookups

### Modes
- `--job_type=normal` = streaming (Kafka -> Iceberg + BQ refined)
- `--job_type=initial_data` = batch (BQ prev_raw_sales -> Iceberg)

---

## 2. Pipeline Flow (Kafka -> Iceberg + BQ)

```
Kafka (2 topics, merged) -> ReadFromKafka (SalesKafkaReaderAdapter)
  -> _SafeDecodeWithHeadersDoFn (attach _kafka_headers)
  -> ApplyWindow(FixedWindows(5s))
  -> AttachEventNameDoFn -> BuildRawEventDoFn
  -> WriteToIceberg (single managed.Write -> raw_sales)
  -> Fan-out to 3 BQ refined tables:
      EnrichSalesDoFn (MasterCache BQ lookup)
      Map(to_receipt_row)  -> BigQueryWriterAdapter -> sales_receipt  (CDC UPSERT)
      FlatMap(to_sku_rows) -> BigQueryWriterAdapter -> sales_sku     (CDC UPSERT)
      FlatMap(to_tender_rows) -> BigQueryWriterAdapter -> sales_tender (CDC UPSERT)
```

### Source Table Format
```json
{"value": {eventId, source, eventName, timestamp, payload: {...}}, "headers": [{key, value}]}
```
Kafka headers (e.g. `source: "RIS"`) needed for downstream enrichment.

### Key Design Decisions
- **Single managed.Write** -- multiple managed.Write causes Dataflow upgrade error
- **Both topics merged** -- no per-topic branching (simplifies pipeline)
- **Monthly BQ partitioning** -- `transaction_date` MONTH (not DAY)
- **Clustering per table** -- different clustering fields per table
- **CDC UPSERT** -- same receipt sent multiple times (created + updated), dedup via PK

---

## 3. Code Structure

```
src/
├── main.py                          # Composition root
├── adapters/
│   ├── input/
│   │   ├── kafka/
│   │   │   └── sales_kafka_reader.py    # Custom Kafka reader (CVE-2025-68121 workaround)
│   │   └── configuration/
│   │       ├── settings.py              # Pydantic DTOs
│   │       ├── configuration_adapter.py # YAML -> PipelineConfig
│   │       ├── logging_adapter.py       # Structured logging
│   │       └── secret_adapter.py        # GCP Secret Manager
│   └── output/
│       ├── iceberg_writer.py            # write_to_iceberg()
│       ├── iceberg_sink.py              # IcebergSink(config, schema, row_mapper)
│       ├── bq_lookup_cache.py           # MasterCache (thread-safe, auto-refresh)
│       └── bigquery/
│           ├── bigquery_writer_config.py
│           └── bigquery_writer.py
├── application/
│   ├── row_mappers.py                   # dict -> beam.Row converters
│   └── pipeline/
│       ├── builder.py                   # PipelineBuilder
│       ├── dofns.py                     # Beam DoFns with metrics
│       └── enrich_dofns.py              # EnrichSalesDoFn
└── domain/
    ├── models.py                        # RawEvent, IntermediateEvent TypedDicts
    ├── schemas.py                       # PyArrow (Iceberg) + BQ schemas (3 tables)
    ├── validators.py                    # Shared validation
    ├── transformers.py                  # Kafka -> RawEvent pure functions
    ├── bq_transformers.py               # to_receipt_row, to_sku_rows, to_tender_rows
    ├── enrichment_logic.py              # 6-level priority chain
    ├── blms_catalog_config.py           # BlmsCatalogConfig (frozen dataclass)
    ├── managed_iceberg_write_config.py  # ManagedIcebergWriteConfig
    └── config/
        ├── pipeline_config.py           # PipelineConfig (Pydantic)
        └── bigquery_sales_config.py     # Per-table BQ config
```

### Full Project Layout
```
sale/sales-data/
├── .gitlab-ci.yml              # Top-level CI
├── sales-collector/
│   ├── .gitlab-ci.yml          # Collector CI (build -> deploy-stg -> deploy-prod)
│   ├── Dockerfile              # Multi-stage (uv builder + Dataflow launcher + Java 17)
│   ├── pyproject.toml          # Python >=3.12, apache-beam==2.71.0
│   ├── config/
│   │   ├── base.yaml           # Shared config (kafka, iceberg, bq, lookup)
│   │   ├── stg.yaml            # STG overrides
│   │   └── prod.yaml           # PROD overrides
│   ├── src/                    # (see detailed tree above)
│   ├── resources/init/
│   │   └── load_raw_sales_source.sql  # SQL for initial data load
│   ├── dataform/               # Public views on refined tables
│   └── tests/unit/
├── infrastructure/sales-collector/
│   ├── main.tf, variables.tf, gcs-bucket.tf, artifact-registry.tf
│   ├── secret-manager.tf, biglake-metastore.tf, bigquery.tf, pubsub.tf
│   ├── schemas/
│   │   ├── deploy.py           # BQ table deployer
│   │   ├── raw_sales.json      # Source: external_iceberg, 6 fields
│   │   ├── sales_receipt.json  # Refined: native, MONTH partition
│   │   ├── sales_sku.json      # Refined: native, MONTH partition
│   │   └── sales_tender.json   # Refined: native, MONTH partition
│   └── templates/container_spec.json
└── scripts/
    ├── prepare_dataflow_config.sh
    ├── prepare_dataflow_spec.sh
    └── deploy_dataflow.sh
```

---

## 4. Data Architecture

### Iceberg Source Tables

| Table | Partition | Schema |
|-------|-----------|--------|
| `source.sales_created` | `ingested_date` (int64) | data(string), ingested_date(int64), ingested_at(string) |
| `source.sales_updated` | `ingested_date` (int64) | data(string), ingested_date(int64), ingested_at(string) |

### BQ Refined Tables (ALL CDC UPSERT, MONTH on transaction_date)

#### sales_receipt (62 columns)
- **Primary Key**: `[receipt_number, partner_code, branch_code, sale_type_code, transaction_date, display_receipt_number]`
- **Clustering**: `[partner_code, member_id, branch_code]`
- **Cardinality**: 1:1 (one row per event)
- **Key fields**: event_id, member_id, partner_code, branch_code, receipt_number, sale_type_code, total_price, total_discount, total_payment, sales_channel (enriched)

#### sales_sku (61 columns)
- **Primary Key**: `[receipt_number, partner_code, branch_code, sale_type_code, transaction_date, display_receipt_number, line_number]`
- **Clustering**: `[partner_code, sku, member_id]`
- **Cardinality**: 1:N FlatMap (one row per `items[]` entry)
- **Key fields**: sku, barcode, quantity, unit_price, subtotal_price + sign-flip for returns

#### sales_tender (42 columns)
- **Primary Key**: `[receipt_number, partner_code, branch_code, sale_type_code, transaction_date, display_receipt_number, payment_type, reference_number]`
- **Clustering**: `[partner_code, payment_type, member_id]`
- **Cardinality**: 1:M FlatMap (one row per `payments[]` entry)
- **Key fields**: payment_type, reference_number, amount, credit_card, issuer_bank (BIN lookup)

### Column Naming (post-migration)
- `receipt_no` -> `receipt_number`
- `trans_type` -> `sale_type_code`
- `card_no` -> `card_number`
- `member_number` -> `member_id`
- `pos_no` -> `device_number`
- `qty` -> `quantity`
- `tender_type` -> `payment_type`
- `trans_date` -> `transaction_date` (pending further rename to `transaction_datetime`)

### Dataform Layer
- `public/sales/`: `sales_receipt.sqlx`, `sales_sku.sqlx`, `sales_tender.sqlx`
- `refined/sales/`: same 3 tables
- `external_sources.js`: cross-project JOINs with partner + catalog datasets

---

## 5. Domain Models & Schemas

### models.py
- `RawEvent(TypedDict)`: eventId, source, eventName, timestamp, payload(JSON str), etlLoadTime(YYYYMMDDHH)
- `IntermediateEvent(TypedDict)`: eventName, payload(dict)

### schemas.py
- `RAW_SALES_SCHEMA`: PyArrow schema for Iceberg (6 fields)
- `SALES_RECEIPT_SCHEMA`: BQ schema with `_HEADER_FIELDS` shared pattern
- `SALES_SKU_SCHEMA`: BQ schema (1:N from items array)
- `SALES_TENDER_SCHEMA`: BQ schema (1:M from tenders array)

### bq_transformers.py
- `to_receipt_row(RawEvent) -> dict` -- 1:1 (1 row per event)
- `to_sku_rows(RawEvent) -> list[dict]` -- 1:N (items array)
- `to_tender_rows(RawEvent) -> list[dict]` -- 1:M (tenders array)
- `unwrap_avro_value()`, `unwrap_avro_array()` for Avro unwrapping
- Bangkok timezone +7h: `_BANGKOK_OFFSET_SECONDS = 25200`

---

## 6. 6-Level Sales Channel Enrichment (Priority Chain)

The enrichment pipeline resolves `sales_channel` via a cascading priority lookup against BQ master tables. Each level is tried in order; the first match wins.

| Priority | Level | Lookup Key | Approx Rows | Notes |
|----------|-------|-----------|-------------|-------|
| 1 | Branch-level | `partner_code` + `branch_code` | ~1K | Most common match |
| 2 | Tender-level | `partner_code` + `tender_type` | 3 | B2S only |
| 3 | Product-level | `partner_code` + `sku` | ~10K | MIN across items |
| 4 | SAP Channel | `partner_code` + `sap_channel` | ~10 | CMG only |
| 5 | Channel Code | `sales_channel_code` | ~30 | HWS/TWD |
| 6 | Translator | `salePersonId` | 3 | Fallback |

### MasterCache (BQ Lookup Engine)
```python
MasterCache(config=LookupConfig)
# Thread-safe singleton per worker
# Auto-refresh on interval (default 1hr)
# Force-refresh-on-miss with cooldown (30s)
# retry_on_miss flag for handling DTS sync delays
```

**Lookup tables loaded**: `sales_channel_branch`, `sales_channel_tender`, `sales_channel_product`, `creditcard_master`, `sales_channel_partner`, `sales_channel_sap`, `sales_channel_code`, `sales_channel_translator`

---

## 7. Iceberg Write (BLMS REST)

### BlmsCatalogConfig (frozen dataclass)
```python
@dataclass(frozen=True)
class BlmsCatalogConfig:
    warehouse_path: str    # "gs://the1-sales-data-source-{env}"
    namespace: str         # "source"
    rest_uri: str          # "https://biglake.googleapis.com/iceberg/v1/restcatalog"
    project_id: str
    region: str
    catalog_name: str      # = bucket name from warehouse_path

    def build_catalog_properties(self) -> dict:
        # type: rest, GoogleAuthManager, vended-credentials
```

### ManagedIcebergWriteConfig
```python
@dataclass(frozen=True)
class ManagedIcebergWriteConfig:
    catalog: BlmsCatalogConfig
    table_name: str               # "raw_sales"
    triggering_frequency_seconds: int  # 60
    partition_fields: list[str]   # ["ingestedTHDate", "ingestedTHHour"]

    @property
    def writer_config(self) -> dict:
        # table, catalog_name, catalog_properties, triggering_frequency_seconds,
        # partition_fields, table_properties.location
```

### IcebergSink PTransform
```python
IcebergSink(config=ManagedIcebergWriteConfig, schema=RAW_EVENT_FIELDS, row_mapper=to_raw_event_row)
# -> managed.Write(managed.ICEBERG, config=writer_config)
```

---

## 8. BQ Refined (CDC UPSERT)

### CDC Write Mode
- `write_mode: "cdc"` in base.yaml -> Storage Write API CDC mode
- Primary keys per table defined in config
- Same receipt sent via created + updated topics -> dedup via PK

### Sign-Flip Logic for Returns
```python
_SIGN_FLIP_TYPES = {"RETURN_NORMAL", "RETURN_DEPOSIT", "VOID", "VOID_SALE_DEPOSIT"}
# Return type codes: 07, 08, 09, 10
```

**Fields multiplied by -1** for return/void transactions:
- Receipt: `total_price`, `total_discount`, `total_payment`, `net_total_price`, `total_payable_amount`, `total_point`
- SKU: `quantity`, `unit_price`, `subtotal_price`, `net_subtotal_price`, `unit_discount`
- Tender: `amount`

### Data Quality Filters

| Filter | Behavior |
|--------|----------|
| `partner_code == "CEN"` | Filtered out (excluded from BQ refined) |
| `sale_type_code == "SALE_CLEAR_DEPOSIT"` | Filtered out |
| `transactionDate > tomorrow` (Bangkok TZ) | Filtered out (future date filter) |

**Important**: Filtered events still land in Iceberg (audit trail), only skipped in BQ refined tables.

### Future Date Filter
```python
_is_future_transaction(transaction_date, bangkok_now)
# Filters dates > tomorrow (Bangkok time)
# Source system occasionally sends incorrect future transactionDate
```

---

## 9. Config Structure

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
triggering_frequency_seconds: 60
region: "asia-southeast1"
refined:
  dataset_id: "refined"
  sales_receipt: {enable: true, partition: MONTH on transaction_date, clustering: [...], write_mode: cdc, primary_key: [...]}
  sales_sku: {enable: true, ...}
  sales_tender: {enable: true, ...}
lookup:
  sales_channel_branch: {key: sales_channel, refresh: 3600}
  # + other lookup tables
```

### stg.yaml / prod.yaml
```yaml
project: "the1-sales-data-{env}"
iceberg_warehouse: "gs://the1-sales-data-source-{env}"
log_level: "DEBUG"  # (INFO for prod)
```

### Settings (Pydantic DTOs)
```python
class DataflowConfigDto(BaseModel):
    project, secret_name, kafka_topics, kafka_group_id
    window_size_seconds, message_format
    blms_rest_uri, blms_namespace, iceberg_tables, iceberg_warehouse
    triggering_frequency_seconds, region
    refined: RefinedConfig
    lookup: LookupConfigDto
    log_level, job_type
    init_data: InitDataConfig  # for batch mode
```

### Config Flow
```
CLI --dataflow_config=<base64 YAML> --job_type=normal
  -> Decode -> Validate (Pydantic) -> Fetch secrets
  -> Build BlmsCatalogConfig + ManagedIcebergWriteConfig + BigQuerySalesConfig + MasterCache
  -> PipelineConfig
```

---

## 10. Collectors & Components

| Component | Mode | Source | Sink | Status |
|-----------|------|--------|------|--------|
| sales-collector | Streaming | Kafka (loyalty.sales.*) | Iceberg + BQ refined | PROD active |
| Dataform (sales) | CI-triggered | BQ refined | BQ public (views) | STG active, PROD pending IAM |
| deploy.py | CI-triggered | JSON schemas | BQ refined tables (DDL) | Active |
| BLMS scripts | Manual CLI | BigLake Metastore | Snapshot management | Active |

---

## 11. CI/CD

### Pipeline Stages
```
build -> deploy-stg -> test-stg -> deploy-prod -> test-prod -> rollback
```

### Jobs (ALL ACTIVE)
| Job | Stage | Details |
|-----|-------|---------|
| linter | build | ruff + mypy |
| test | build | pytest + coverage |
| create-image | build | Kaniko -> 4 destinations (STG+PROD latest+SHA) |
| sonar-scan | build | SonarQube |
| scan-gitleaks | build | Secret scanning |
| scan-image | build | Trivy |
| terraform:apply:stg | deploy-stg | TF apply |
| deploy-tables:stg | deploy-stg | deploy.py |
| deploy:stg | deploy-stg | Dataflow (max-workers 1) |
| terraform:apply:prod | deploy-prod | TF apply |
| deploy-tables:prod | deploy-prod | deploy.py |
| deploy:prod | deploy-prod | Dataflow (max-workers 2) |

### Deploy Script Flow
```bash
# 1. Prepare config
scripts/prepare_dataflow_config.sh --base config/base.yaml --env config/{env}.yaml

# 2. Prepare template
scripts/prepare_dataflow_spec.sh --image-file image-digest-ref-{env}.txt \
  --template-path infrastructure/sales-collector/templates/container_spec.json

# 3. Deploy (update -> drain -> cancel -> fresh)
scripts/deploy_dataflow.sh --project-id the1-sales-data-{env} \
  --job-name sales-collector --max-workers {1|2} \
  --staging-location gs://the1-sales-data-source-{env}/dataflow/staging \
  --temp-location gs://the1-sales-data-source-{env}/dataflow/temp
```

### CI Variables
```
SVC_NAME: "sales-collector"
DOMAIN_NAME: "the1-sales-data"
DATAFLOW_JOB_NAME: "sales-collector"
GCP_PROJECT_ID: "the1-sales-data"
GCP_SERVICE_ACCOUNT: "t1-sales-collector"
```

### Dataform CI
- `sales-collector/dataform/` -- public views on refined tables
- `external_sources.js` with cross-project vars (`partner_project`, `catalog_project`)
- CI template regex replaces `-stg` -> `-prod` in vars

---

## 12. Infrastructure (Terraform)

### All .tf Files ACTIVE
| File | Resources |
|------|-----------|
| main.tf | Provider google ~>7.17.0, backend GCS, locals |
| variables.tf | region, domain="sales-data", service_name="sales-collector" |
| gcs-bucket.tf | Source + config buckets, BLMS SA objectAdmin |
| artifact-registry.tf | GAR Docker repo |
| secret-manager.tf | Secret container |
| biglake-metastore.tf | BLMS catalog + vended-credentials + workload SA editor |
| bigquery.tf | Source dataset (external_catalog) + refined dataset |
| pubsub.tf | COMMENTED (future) |

### Naming Convention
```
Backend:  devops-terraformstate-nonprod / the1-sales-data/services/sales-collector
Project:  the1-sales-data-{env}
SA:       t1-sales-collector@the1-sales-data-{env}.iam.gserviceaccount.com
Source:   the1-sales-data-source-{env}
Config:   the1-sales-data-config-{env}
Catalog:  the1-sales-data-source-{env} (same as bucket name)
```

### TF Key Config
- `external_catalog_dataset_options` REMOVED from source dataset
- Collector SA role: `biglake.editor` (not admin)
- Source + config buckets with SA objectAdmin
- BQ source + refined datasets with SA dataOwner

### deploy.py (Schema Deployment)
- Location: `infrastructure/sales-collector/schemas/deploy.py`
- Native BQ tables (CREATE, ALTER, backup/restore, schema compare)
- Smart change detection (NO_CHANGE / ADDITIVE / BREAKING)
- INTERVAL bug fixed: `'0:0:0'` HOUR TO SECOND (not `'0'`)

---

## 13. Key Patterns

### Avro Unwrapping
```python
unwrap_avro_value({"string": "x"}) -> "x"
unwrap_avro_array({"array": [...]}) -> [...]
# Magic byte 0x00 detection for Avro messages
```

### Bangkok Timezone +7
```python
_BANGKOK_TZ = timezone(timedelta(hours=7))
_BANGKOK_OFFSET_SECONDS = 7 * 3600
# Iceberg: ingestedTHDate = YYYYMMDD Bangkok, ingestedTHHour = HH Bangkok
# BQ refined: etl_updated_date = DATETIME Bangkok (no Z suffix!)
```

### Timestamp Parsing
- YYYYMMDD primary format, DDMMYYYY fallback
- BQ DATETIME columns: NO Z suffix (`strftime("%Y-%m-%dT%H:%M:%S")`)
- BQ TIMESTAMP columns: Z suffix OK

### Error Handling
- All DoFns: try/except -> log -> drop (no DLQ yet)
- Beam metrics counters per DoFn (seen/ok/errors)

### DoFn Metrics
| DoFn | Namespace | Purpose |
|------|-----------|---------|
| ExtractValueDoFn | extract/ | Kafka record -> bytes |
| DecodeParseDoFn | decode/ | bytes -> dict (JSON) |
| AttachEventNameDoFn | transform/ | dict -> IntermediateEvent |
| BuildRawEventDoFn | build/ | IntermediateEvent -> RawEvent |
| EnrichSalesDoFn | enrich/ | RawEvent -> enriched dict |

### Numeric Handling
- All NUMERIC fields: COALESCE to 0
- All STRING fields: COALESCE to ''
- `display_receipt_no_2`: extracted from `references[SECOND_DISPLAY_RECEIPT_NUMBER]` array
- `credit_card` validation: BIN extraction, length 14-19, XXXX pattern
- `issuer_bank`: via creditcard_master range lookup
- Sales channel priority: Tender > Branch (match SQL)
- Tender MIN across all payments (not first match)

---

## 14. Dependencies

### Python (pyproject.toml)
- `apache-beam[gcp,hadoop]==2.71.0`
- `google-cloud-secret-manager>=2.26.0`
- `pyarrow>=14.0.0,<18.0.0`
- `pydantic>=2.12.5`
- `common-data-python` (git tag)

### Dev
- `mypy>=1.19.1` (strict, pydantic plugin)
- `ruff>=0.14.9` (line-length 120)
- `pytest>=9.0.2`, `pytest-cov>=6.0.0`

### Cross-Domain Dependencies
| Dependency | Direction | Details |
|------------|-----------|---------|
| `common-python-dataflow` | sales <- common | Shared Beam adapters (KafkaReader, DecodeMessageDoFn) |
| `the1-partner-data` | sales -> partner (read) | Dataform views JOIN companies_branch. Needs IAM. |
| `the1-catalog-data` | sales -> catalog (read) | Dataform views JOIN ms_product_all. Needs IAM. |
| `blms_scripts` | sales uses | Shared BigLake CLI at `/realproject/blms_scripts/` |
| Kafka (loyalty.sales.*) | upstream -> sales | 2 topics, Avro/JSON with value+headers wrapper |
| BQ refined master tables | upstream -> sales | DTS-synced from AWS: 8 lookup tables |

---

## 15. Documentation Index

### Sales-specific
- `sale/doc/architecture/SALES_PIPELINE_ARCHITECTURE.md`
- `sale/doc/cicd/SALES_CICD.md`
- `sale/doc/operations/SALES_OPERATIONS.md`
- `sale/doc/SCHEMA_MIGRATION_PLAN.md`
- `sale/doc/refined_sales.sql` -- SQL reference for refined schema
- `sales-collector/doc/SALES_ENRICHMENT_LOGIC.md` (V1 -> V2 -> V3)
- `sales-collector/doc/STREAMING_ENRICHMENT_DEEP_DIVE.md`
- `sales-collector/doc/STREAMING_BATCH_JOIN_RESEARCH.md`
- `sales-collector/doc/BQ_CDC_MERGE_COMPATIBILITY.md`

### Validation Steps
```bash
cd sale/sales-data/sales-collector
uv sync
uv run ruff check .
uv run mypy .
uv run poe test:cov
uv run pre-commit run --all-files
```
