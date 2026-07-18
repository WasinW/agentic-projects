# Catalog Domain — Knowledge Base

## Current State (2026-04-05) — SETUP COMPLETE, CODE ADAPTATION PENDING

> **NOTE: Code structure still uses purchases-collector domain models** (PurchasePayload, purchases schemas, receipt/detail/payment BQ tables). Not yet adapted to products domain. This is the **#1 pending task** -- all domain models, schemas, transformers, and BQ table definitions need to be rewritten for product entity data.

### Location
- **Active repo**: `catalog/catalog-data/` (has .git, full structure)
- **Old/empty**: `catalog/catalogs-data/` (incomplete, ignore)
- **Source**: Copied from purchases-collector [REF: purchases-collector pattern]
- **Status**: Structure complete, terraform active (GAR/bucket/secret/BQ refined), 94 tests pass

### GCP Project
- STG: `the1-catalog-data-stg` (folder: `801076874630`)
- PROD: `the1-catalog-data-prod` (folder: `354078186135`)
- SA: `t1-products-collector@the1-catalog-data-{env}.iam.gserviceaccount.com`

### Structure

```
catalog/catalog-data/
├── .git/
├── .gitlab-ci.yml                    # Main CI (stages: build, deploy-stg/prod, test, rollback)
├── .gitlab/ci/dataform-template.gitlab-ci.yml
├── scripts/                          # Shared (deploy_dataflow.sh, prepare_*.sh, deploy_schemas.py, etc.)
├── infrastructure/products-collector/
│   ├── main.tf         (backend: the1-catalog-data/services/data-pipeline-products)
│   ├── variables.tf    (region, domain, pubsub_topic, service_name, s3_ms_product_all_path)
│   ├── terraform.tfvars (domain=catalog-data)
│   ├── artifact-registry.tf  -- ACTIVE
│   ├── bucket.tf              -- ACTIVE (source + config GCS buckets)
│   ├── secret-manager.tf      -- ACTIVE (products-collector + s3-credentials)
│   ├── bigquery.tf            -- ACTIVE (refined dataset + IAM), source dataset COMMENTED
│   ├── dts.tf                 -- ACTIVE (S3->BQ transfer, disabled=false, on-demand)
│   ├── biglake-metastore.tf   (COMMENTED -- waiting for BigLake catalog readiness)
│   ├── service-accounts.tf    (COMMENTED -- externally managed)
│   ├── pubsub.tf              (COMMENTED)
│   ├── dataform.tf            (ACTIVE)
│   ├── schemas/               (placeholder JSONs: purchases_receipt, detail, payment)
│   └── templates/container_spec.json
├── README.md
└── products-collector/
    ├── .gitlab-ci.yml          # terraform + dataform ACTIVE, build/deploy COMMENTED
    ├── Dockerfile              (2-stage: uv builder + dataflow base)
    ├── Dockerfile.base         (multi-stage: python3.12 + java17 + beam JARs)
    ├── pyproject.toml          (name=products-collector, beam 2.71.0, common-data 0.0.23)
    ├── sonar-project.properties
    ├── config/
    │   ├── base.yaml           (kafka topics, iceberg tables, BQ config)
    │   ├── stg.yaml            (the1-catalog-data-stg, DEBUG)
    │   └── prod.yaml           (the1-catalog-data-prod, INFO)
    ├── src/
    │   ├── main.py             (entry point: config -> adapters -> builder -> run)
    │   ├── domain/
    │   │   ├── models.py       (TypedDicts: PurchasePayload, RawEvent, IntermediateEvent)
    │   │   ├── schemas.py      (Iceberg RowTypeConstraint)
    │   │   ├── transformers.py (encode/decode, event building, event filters)
    │   │   ├── bq_transformers.py (to_receipt_row, to_detail_rows, to_payment_rows)
    │   │   └── config/
    │   │       ├── pipeline_config.py
    │   │       └── bigquery_purchases_config.py
    │   ├── adapters/
    │   │   ├── input/configuration/
    │   │   │   ├── configuration_adapter.py (YAML+secrets->PipelineConfig)
    │   │   │   ├── settings.py (Pydantic: DataflowConfig, SettingsLoader)
    │   │   │   ├── secret_adapter.py (GCP Secret Manager)
    │   │   │   └── logging_adapter.py
    │   │   └── output/
    │   │       ├── gcs/ (biglake_metastore_config, iceberg_writer + config)
    │   │       ├── bigquery/ (bigquery_writer + config)
    │   │       ├── bq_metadata_refresh.py (Option B -- disabled)
    │   │       └── pubsub.py
    │   └── application/pipeline/
    │       ├── builder.py      (pipeline DAG: kafka->window->transform->fan-out)
    │       ├── dofns.py        (AttachEventNameDoFn, BuildRawEventDoFn + metrics)
    │       └── avro_dofn.py    (DecodeAvroOrJsonDoFn for Confluent)
    └── tests/                  (94 tests: unit + integration)
```

### CI/CD Status

- **Active jobs**: `terraform:apply:stg`, `terraform:apply:prod`, dataform jobs, deploy-tables
- **Commented**: linter, test, create-image, scan, deploy (Dataflow)
- **Domain vars**: `DOMAIN_NAME=the1-catalog-data`, `GCP_PROJECT_ID=the1-catalog-data`
- **Parent CI**: includes common-data templates, dataform templates, products-collector child

### Config (base.yaml)

```yaml
secret_name: "products-collector"
kafka_topics: ["catalog.products.created", "catalog.products.updated"]
kafka_group_id: "catalog-data-products"
kafka_bootstrap_servers: "pkc-312o0.ap-southeast-1.aws.confluent.cloud:9092"
iceberg_table_created: "products_created"
iceberg_table_updated: "products_updated"
blms_rest_uri: "https://biglake.googleapis.com/iceberg/v1/restcatalog"
blms_namespace: "source"
triggering_frequency_seconds: 300
window_size_seconds: 5
message_format: "auto"
region: "asia-southeast1"
bq_dataset_id: "refined"    # TODO: verify
bq_tables:                   # TODO: replace with actual products schema
  purchases_detail: {time_partitioning: {type: DAY, field: transaction_datetime}, ...}
  purchases_payment: {...}
  purchases_receipt: {...}
```

### Pipeline Architecture [REF: purchases-collector pattern]

```
Kafka -> ReadFromKafka
  -> FixedWindow(5s)
  -> AttachEventNameDoFn (parse kafka, add eventName)
  -> BuildRawEventDoFn (envelope: eventId, source, timestamp, ingestedDate)
  -> Fan-out:
    1. Filter created -> PubSub
    2. Filter created -> Iceberg (products_created)
    3. Filter updated -> Iceberg (products_updated)
    4. All -> BQ (3 tables: receipt, detail, payment via FlatMap)
    5. PeriodicImpulse -> RefreshBQMetadata (Option B -- disabled)
```

### Domain Models (currently = purchases, needs products adaptation)

- **RawEvent**: {eventId, source, eventName, timestamp, data (JSON str), ingestedDate, ingestedAt}
- **IntermediateEvent**: {eventName, payload}
- **Iceberg schema**: {data: STRING, ingested_date: INT, ingested_at: INT}
- **BQ tables**: 3 tables (receipt 14 cols, detail 27 cols, payment 8 cols) -- all purchases-specific [REF: purchases-collector pattern]

### Current Architecture (products-collector)

```
DATA SOURCES:
  1. S3 (Delta/Parquet) -> DTS -> BQ refined.ms_product_all (~54.3GB)
  2. Kafka (future) -> Dataflow -> Iceberg -> BQ (not active yet)

SEMANTIC LAYER:
  BQ refined.ms_product_all -> Dataform -> BQ public.ms_product_all (VIEW)

FLOW:
  S3 (t1-analytics)
    +-- s3://t1-analytics/refined/master_data/product/gcp_product_master/*
          | (DTS: Amazon S3 Transfer)
  BQ refined.ms_product_all (TABLE, WRITE_TRUNCATE)
          | (Dataform: products tag)
  BQ public.ms_product_all (VIEW)
```

### Terraform Details

- **Backend**: `gcs bucket devops-terraformstate-nonprod, prefix the1-catalog-data/services/data-pipeline-products`
- **DTS (Data Transfer Service)**: S3 -> BQ `refined.ms_product_all` (~54.3GB Parquet/Delta), disabled=false
- **BQ refined dataset**: ACTIVE with IAM (workload SA -> dataOwner)
- **BQ source dataset**: COMMENTED (waiting for BigLake catalog)
- **Secrets**: `products-collector` (kafka creds) + `catalog-data-s3-credentials` (AWS S3 for DTS)

### Deploy Flow [REF: purchases-collector pattern]

```
STG:
  create-image (Kaniko -> GAR 4 destinations)
    -> terraform:apply:stg
    -> deploy-tables:stg (deploy_schemas.py)
    -> deploy:stg
      1. Drain/cancel existing job (5 min timeout)
      2. prepare_dataflow_config.sh (merge YAML -> base64)
      3. prepare_dataflow_spec.sh (template -> GCS)
      4. deploy_dataflow.sh (gcloud dataflow jobs create)

PROD:
  approve:prod (manual gate)
    -> terraform:apply:prod
    -> deploy-tables:prod
    -> deploy:prod (same as STG but prod params)
```

### Dockerfile Build [REF: purchases-collector pattern]

- **Dockerfile.base**: python3.12 + java17 + beam 2.71.0 JARs (distroless)
- **Dockerfile**: uv sync -> bytecode compile -> copy to base image
- **ENTRYPOINT**: /opt/apache/beam/boot
- **ENV**: FLEX_TEMPLATE_PYTHON_PY_FILE="/app/src/main.py"

### Terraform Resources Status

| Resource | File | Status | Notes |
|----------|------|--------|-------|
| `google_artifact_registry_repository` | `artifact-registry.tf` | ACTIVE | GAR repo for Docker images |
| `google_storage_bucket` (source) | `bucket.tf` | ACTIVE | `the1-catalog-data-source-{env}` |
| `google_storage_bucket` (config) | `bucket.tf` | ACTIVE | `the1-catalog-data-config-{env}` |
| `google_secret_manager_secret` (products) | `secret-manager.tf` | ACTIVE | Kafka credentials |
| `google_secret_manager_secret` (s3-creds) | `secret-manager.tf` | ACTIVE | AWS S3 credentials for DTS |
| `google_bigquery_dataset` (refined) | `bigquery.tf` | ACTIVE | Refined dataset + IAM |
| `google_bigquery_dataset` (source) | `bigquery.tf` | COMMENTED | Waiting for BigLake |
| `google_dataform_repository` | `dataform.tf` | ACTIVE | `products-dataform` repo |
| `google_bigquery_data_transfer_config` | `dts.tf` | ACTIVE | S3->BQ, disabled=false |
| BigLake metastore | `biglake-metastore.tf` | COMMENTED | Waiting for Iceberg readiness |
| Service accounts | `service-accounts.tf` | COMMENTED | Externally managed |
| PubSub | `pubsub.tf` | COMMENTED | Not needed yet |

### CI/CD Jobs Status

| Job | Stage | Status |
|-----|-------|--------|
| `terraform:apply:stg` | deploy-stg | ACTIVE |
| `terraform:apply:prod` | deploy-prod | ACTIVE |
| `deploy-tables:stg` | deploy-stg | ACTIVE |
| `deploy-tables:prod` | deploy-prod | ACTIVE |
| `dataform:build` | build | ACTIVE |
| `dataform:deploy:stg` | deploy-stg | ACTIVE |
| `dataform:assertion:stg` | deploy-stg | ACTIVE |
| `dataform:deploy:prod` | deploy-prod | ACTIVE |
| `linter` | build | COMMENTED |
| `test` | build | COMMENTED |
| `sonar-scan` | build | COMMENTED |
| `create-base-image` | build | COMMENTED |
| `create-image` | build | COMMENTED |
| `scan-gitleaks` | build | COMMENTED |
| `scan-image` | build | COMMENTED |
| `deploy:stg` | deploy-stg | COMMENTED |
| `approve:prod` | deploy-prod | COMMENTED |
| `deploy:prod` | deploy-prod | COMMENTED |

### Checks Passing (2026-03-24)

- `uv sync` -- 166 packages installed
- `ruff check` -- all passed
- `ruff format` -- 49 files formatted
- `mypy` -- no issues in 49 files
- `pytest` -- 94 passed
- `pre-commit` -- runs in catalog-data (has .git)

### Code Fix Applied

- `configuration_adapter.py`: `infrastructure/purchases-collector` -> `infrastructure/products-collector`
