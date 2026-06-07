# Sales Collector Pipeline - Detailed Knowledge Base

> Updated: 2026-02-23 — VERIFIED from full code exploration
> Quick ref: `memory/sales_knowledge_base.md` (overview)
> This file: deep-dive into code patterns, adapters, terraform, CI/CD

---

## 1. MAIN.PY — Composition Root (VERIFIED)

```python
def run():
    # 1. Load config
    config = ConfigurationAdapter().load(options)

    # 2. BLMS cleanup (one-time, active)
    _cleanup_blms_entry(config)

    # 3. Create adapters
    kafka_reader = KafkaReaderAdapter(config.kafka_config)  # All topics merged
    iceberg_writer = GcsIcebergWriter(config.iceberg_write_config, RAW_EVENT_FIELDS, to_raw_event_row)
    bq_receipt = BigQueryWriterAdapter(config.bq_config.to_table_config("sales_receipt"))
    bq_sku = BigQueryWriterAdapter(config.bq_config.to_table_config("sales_sku"))
    bq_tender = BigQueryWriterAdapter(config.bq_config.to_table_config("sales_tender"))

    # 4. Build + run pipeline
    builder = PipelineBuilder(options, config, kafka_reader, iceberg_writer,
                              bq_receipt, bq_sku, bq_tender)
    builder.run()
```

### _cleanup_blms_entry()
- Drops stale BLMS entries so IcebergIO re-creates with correct `table_properties.location`
- Uses RestCatalog with vended credentials
- **Must run inside Dataflow** (workload SA has correct roles; CI SA doesn't)
- One-time: comment out after first successful deploy

---

## 2. BLMS CATALOG CONFIG (VERIFIED)

```python
# adapters/output/gcs/biglake_metastore_config.py
@dataclass(frozen=True)
class BlmsCatalogConfig:
    warehouse_path: str    # "gs://the1-sales-data-source-{env}"
    namespace: str         # "source"
    rest_uri: str          # "https://biglake.googleapis.com/iceberg/v1/restcatalog"
    project_id: str
    region: str
    # Auto-derived:
    catalog_name: str      # = bucket name from warehouse_path

    def build_catalog_properties(self) -> dict:
        return {
            "type": "rest",
            "uri": self.rest_uri,
            "warehouse": f"gs://{self.catalog_name}",
            "rest.auth.type": "org.apache.iceberg.gcp.auth.GoogleAuthManager",
            "header.X-Iceberg-Access-Delegation": "vended-credentials",
            "header.x-goog-user-project": self.project_id,
            "io-impl": "org.apache.iceberg.gcp.gcs.GCSFileIO",
            "rest-metrics-reporting-enabled": "false",
        }
```

---

## 3. ICEBERG WRITER CONFIG (VERIFIED)

```python
# adapters/output/gcs/gcs_biglake_iceberg_writer_config.py
@dataclass(frozen=True)
class GcsIcebergWriterConfig:
    catalog: BlmsCatalogConfig
    table_name: str               # "raw_sales"
    schema: type                  # Schema class
    triggering_frequency_seconds: int  # 300

    @property
    def writer_config(self) -> dict:
        return {
            "table": f"{self.catalog.namespace}.{self.table_name}",
            "catalog_name": self.catalog.catalog_name,
            "catalog_properties": self.catalog.build_catalog_properties(),
            "triggering_frequency_seconds": self.triggering_frequency_seconds,
            "partition_fields": ["etlLoadTime"],
            "table_properties": {"location": f"gs://{self.catalog.catalog_name}/{self.table_name}"},
        }
```

---

## 4. BIGQUERY SALES CONFIG (VERIFIED)

```python
# domain/config/bigquery_sales_config.py
class BigQuerySalesConfig:
    project_id: str
    dataset_id: str         # "refined"
    schemas: dict           # {table_key: BQ_SCHEMA}
    tables: dict            # {table_key: RefinedTableRuntimeConfig}

    def to_table_config(self, table_key: str) -> BigQueryWriterConfig:
        # Returns BigQueryWriterConfig with partitioning + clustering
        # Partitioning: MONTH on trans_date
        # Clustering varies per table
```

### Per-Table Config
| Table | Partition | Clustering |
|-------|-----------|------------|
| sales_receipt | MONTH on trans_date | partner_code, member_number, branch_code |
| sales_sku | MONTH on trans_date | partner_code, sku_code, member_number |
| sales_tender | MONTH on trans_date | partner_code, tender_type, member_number |

---

## 5. PIPELINE BUILDER (VERIFIED)

### Current Flow (builder.py)
```python
class PipelineBuilder:
    def run(self):
        options.view_as(StandardOptions).streaming = True
        with beam.Pipeline(options=self.options) as p:
            raw_bytes = p | kafka_reader                    # All topics merged
            decoded = raw_bytes | ExtractValueDoFn() | DecodeParseDoFn()
            windowed = decoded | FixedWindows(5s)
            raw_events = windowed | AttachEventNameDoFn() | BuildRawEventDoFn()

            # Debug (active)
            raw_events | DebugLogDoFn()

            # Iceberg write (active)
            raw_events | iceberg_writer

            # BQ writes (COMMENTED — uncomment when ready)
            # raw_events | Map(to_receipt_row) | bq_receipt_sink
            # raw_events | FlatMap(to_sku_rows) | bq_sku_sink
            # raw_events | FlatMap(to_tender_rows) | bq_tender_sink
```

---

## 6. DOFNS (VERIFIED)

Each DoFn has: `setup()` → metrics init, `process()` → try/except/log

| DoFn | Metrics Namespace | Purpose |
|------|-------------------|---------|
| ExtractValueDoFn | extract/ | Kafka record → bytes |
| DecodeParseDoFn | decode/ | bytes → dict (JSON) |
| AttachEventNameDoFn | transform/ | dict → IntermediateEvent |
| BuildRawEventDoFn | build/ | IntermediateEvent → RawEvent |

---

## 7. SETTINGS & VALIDATION (VERIFIED)

```python
# adapters/input/configuration/settings.py
class DataflowConfigDto(BaseModel):
    project: str
    secret_name: str
    kafka_topics: list[str]
    kafka_group_id: str
    window_size_seconds: int
    message_format: str          # avro/json/auto
    blms_rest_uri: str
    blms_namespace: str
    iceberg_tables: dict[str, str]  # topic → table name
    iceberg_warehouse: str
    triggering_frequency_seconds: int
    region: str
    refined: RefinedConfig
    log_level: str

# Validates:
# - Every kafka_topic has iceberg_table mapping
# - CDC mode requires primary_key
# - log_level in [DEBUG, INFO, WARNING, ERROR, CRITICAL]
```

---

## 8. CI/CD DETAILS (VERIFIED)

### Collector .gitlab-ci.yml Key Sections

**Build Stage:**
- `linter`: `uv sync && ruff check . && ruff format --check . && mypy .`
- `test`: `uv sync && uv run poe test:cov` (coverage XML)
- `create-image`: Kaniko → 4 destinations (STG latest+SHA, PROD latest+SHA)
  - Outputs `image-digest-ref.txt` (SHA digest for immutable reference)

**Deploy Stage (STG/PROD):**
```bash
# 1. Prepare config
scripts/prepare_dataflow_config.sh --base config/base.yaml --env config/{env}.yaml

# 2. Prepare template
scripts/prepare_dataflow_spec.sh --image-file image-digest-ref-{env}.txt \
  --template-path infrastructure/sales-collector/templates/container_spec.json ...

# 3. Deploy
scripts/deploy_dataflow.sh --project-id the1-sales-data-{env} \
  --job-name sales-collector --max-workers {1|2} \
  --staging-location gs://the1-sales-data-source-{env}/dataflow/staging \
  --temp-location gs://the1-sales-data-source-{env}/dataflow/temp ...
```

### deploy_dataflow.sh Strategy:
1. Find existing running job
2. Compatible → try --update (zero downtime)
3. Incompatible → drain → cancel (fallback) → fresh deploy
4. Config hash (MD5) stored as job label for change detection
5. Poll every 15s, timeout 10min

---

## 9. TERRAFORM DETAILS (VERIFIED)

### main.tf
```hcl
terraform {
  required_providers { google = "~> 7.17.0" }
  backend "gcs" {
    bucket = "devops-terraformstate-nonprod"
    prefix = "the1-sales-data/services/sales-collector"
  }
}
locals {
  project_id = "the1-sales-data-${terraform.workspace}"
  workload_service_account = "serviceAccount:t1-sales-collector@${local.project_id}.iam.gserviceaccount.com"
  gcs_source_bucket_name = "the1-sales-data-source-${terraform.workspace}"
  gcs_flex_templates_bucket_name = "the1-sales-data-config-${terraform.workspace}"
}
```

### biglake-metastore.tf
```hcl
resource "google_biglake_iceberg_catalog" "source_catalog" {
  name = local.gcs_source_bucket_name        # Same as bucket name
  catalog_type = "CATALOG_TYPE_GCS_BUCKET"
  credential_mode = "CREDENTIAL_MODE_VENDED_CREDENTIALS"
  depends_on = [module.source_bucket]
}
resource "google_biglake_iceberg_catalog_iam_member" "source_catalog_admin" {
  role = "roles/biglake.admin"
  member = local.workload_service_account
}
```

### bigquery.tf
```hcl
resource "google_bigquery_dataset" "source" {
  dataset_id = "source"
  external_catalog_dataset_options {
    default_storage_location_uri = "gs://${local.gcs_source_bucket_name}"
    parameters = {}
  }
  depends_on = [google_biglake_iceberg_catalog.source_catalog]
}
resource "google_bigquery_dataset" "refined" {
  dataset_id = "refined"
}
# Both datasets: workload SA as dataOwner
```

### gcs-bucket.tf
```hcl
module "source_bucket" {
  name = local.gcs_source_bucket_name
  objectAdmin = [local.workload_service_account]
  # + BLMS SA objectAdmin (with 30s wait for propagation)
}
module "config_bucket" {
  name = local.gcs_flex_templates_bucket_name
  admin = [local.workload_service_account]
}
```

---

## 10. DOCKERFILE (VERIFIED)

```dockerfile
# Stage 1: Builder
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS builder
# CI_JOB_TOKEN for private git deps, uv sync, compileall

# Stage 2: Runtime
FROM gcr.io/dataflow-templates-base/python312-template-launcher-base:flex_templates_base_image_release_20260112_RC00
# Java 17 (Kafka/Iceberg cross-language)
# FLEX_TEMPLATE_PYTHON_PY_FILE=/app/src/main.py
# ENTRYPOINT ["/opt/apache/beam/boot"]
```

---

## 11. DEPENDENCIES (pyproject.toml VERIFIED)

### Core:
- `apache-beam[gcp,hadoop]==2.70.0`
- `google-cloud-secret-manager>=2.26.0`
- `pyarrow>=14.0.0,<18.0.0`
- `pydantic>=2.12.5`
- `common-data-python` (git tag 0.0.9)

### Dev:
- `mypy>=1.19.1` (strict, pydantic plugin)
- `ruff>=0.14.9` (line-length 120)
- `pytest>=9.0.2`, `pytest-cov>=6.0.0`
- `pyiceberg[pyarrow,sql-sqlite]>=0.11.0`

---

## 12. MESSAGING VS PURCHASES VS SALES COMPARISON

| Feature | Messaging | Purchases | Sales |
|---------|-----------|-----------|-------|
| Iceberg Writer | Managed IcebergIO | Manual Writer | Managed IcebergIO |
| BQ Tables | 1 (enriched) | 3 (receipt/detail/payment) | 3 (receipt/sku/tender) |
| Extra Sinks | PubSub + BigTable | PubSub | None |
| Kafka Topics | 5 | 2 | 2 |
| BQ Partition | DAY | DAY | MONTH |
| Provider | google ~>7.17.0 | google ~>5.0 | google ~>7.17.0 |
| Config Pattern | Pydantic | Pydantic | Pydantic |
| Domain Models | TypedDict | TypedDict | TypedDict |
| Python | 3.12 | 3.12 | 3.12 |
| Beam | 2.70.0 | 2.70.0 | 2.70.0 |

---

## 13. NEXT STEPS (User's Plan)

### Current Session Focus:
User wants to continue improving sales-collector. Key areas:
1. ~~Copy CI/CD from messaging~~ — DONE (full pipeline active)
2. ~~Copy terraform from messaging~~ — DONE (all resources active)
3. ~~Copy code structure~~ — DONE (hexagonal architecture)
4. **Enable BQ writes** — uncomment in builder.py when Iceberg verified
5. **Remove DebugLogDoFn** — when BQ writes enabled
6. **Comment out _cleanup_blms_entry()** — after first successful deploy
7. **Verify Iceberg data at correct path** — flat path, not nested
