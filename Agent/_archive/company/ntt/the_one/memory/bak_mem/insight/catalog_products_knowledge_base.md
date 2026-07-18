---
name: Catalog Products-Collector Knowledge Base
description: Complete setup KB for catalog/catalog-data/products-collector - terraform, CI/CD, code structure, pipeline architecture, all reference patterns from purchases-collector
type: project
---

# Catalog Products-Collector Knowledge Base

## Current State (2026-03-25) — SETUP COMPLETE, CODE ADAPTATION PENDING

### Location
- **Active repo**: `catalog/catalog-data/` (has .git, full structure)
- **Old/empty**: `catalog/catalogs-data/` (incomplete, ignore)
- **Source**: Copied from `loyalty/loyalty_paralel/loyalty-data/purchases-collector/`
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
│   ├── artifact-registry.tf  ← ACTIVE
│   ├── bucket.tf              ← ACTIVE (source + config GCS buckets)
│   ├── secret-manager.tf      ← ACTIVE (products-collector + s3-credentials)
│   ├── bigquery.tf            ← ACTIVE (refined dataset + IAM), source dataset COMMENTED
│   ├── dts.tf                 ← ACTIVE (S3→BQ transfer, disabled=true, on-demand)
│   ├── biglake-metastore.tf   (COMMENTED — waiting for BigLake catalog readiness)
│   ├── service-accounts.tf    (COMMENTED — externally managed)
│   ├── pubsub.tf              (COMMENTED)
│   ├── dataform.tf            (COMMENTED)
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
    │   ├── main.py             (entry point: config → adapters → builder → run)
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
    │   │   │   ├── configuration_adapter.py (YAML+secrets→PipelineConfig)
    │   │   │   ├── settings.py (Pydantic: DataflowConfig, SettingsLoader)
    │   │   │   ├── secret_adapter.py (GCP Secret Manager)
    │   │   │   └── logging_adapter.py
    │   │   └── output/
    │   │       ├── gcs/ (biglake_metastore_config, iceberg_writer + config)
    │   │       ├── bigquery/ (bigquery_writer + config)
    │   │       ├── bq_metadata_refresh.py (Option B — disabled)
    │   │       └── pubsub.py
    │   └── application/pipeline/
    │       ├── builder.py      (pipeline DAG: kafka→window→transform→fan-out)
    │       ├── dofns.py        (AttachEventNameDoFn, BuildRawEventDoFn + metrics)
    │       └── avro_dofn.py    (DecodeAvroOrJsonDoFn for Confluent)
    └── tests/                  (94 tests: unit + integration)
```

### CI/CD Status
- **Active jobs**: `terraform:apply:stg`, `terraform:apply:prod`, dataform jobs
- **Commented**: linter, test, create-image, scan, deploy-tables, deploy (Dataflow)
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

### Pipeline Architecture (from purchases-collector)
```
Kafka → ReadFromKafka
  → FixedWindow(5s)
  → AttachEventNameDoFn (parse kafka, add eventName)
  → BuildRawEventDoFn (envelope: eventId, source, timestamp, ingestedDate)
  → Fan-out:
    1. Filter created → PubSub
    2. Filter created → Iceberg (products_created)
    3. Filter updated → Iceberg (products_updated)
    4. All → BQ (3 tables: receipt, detail, payment via FlatMap)
    5. PeriodicImpulse → RefreshBQMetadata (Option B — disabled)
```

### Domain Models (currently = purchases, needs products adaptation)
- **RawEvent**: {eventId, source, eventName, timestamp, data (JSON str), ingestedDate, ingestedAt}
- **IntermediateEvent**: {eventName, payload}
- **Iceberg schema**: {data: STRING, ingested_date: INT, ingested_at: INT}
- **BQ tables**: 3 tables (receipt 14 cols, detail 27 cols, payment 8 cols) — all purchases-specific

### Terraform Details
- **Backend**: `gcs bucket devops-terraformstate-nonprod, prefix the1-catalog-data/services/data-pipeline-products`
- **DTS (Data Transfer Service)**: S3 → BQ `refined.ms_product_all` (~54.3GB Parquet/Delta), disabled=true
- **BQ refined dataset**: ACTIVE with IAM (workload SA → dataOwner)
- **BQ source dataset**: COMMENTED (waiting for BigLake catalog)
- **Secrets**: `products-collector` (kafka creds) + `catalog-data-s3-credentials` (AWS S3 for DTS)

### Code Fix Applied
- `configuration_adapter.py`: `infrastructure/purchases-collector` → `infrastructure/products-collector`

### Checks Passing (2026-03-24)
- `uv sync` — 166 packages installed
- `ruff check` — all passed
- `ruff format` — 49 files formatted
- `mypy` — no issues in 49 files
- `pytest` — 94 passed
- `pre-commit` — runs in catalog-data (has .git)

### What Still Needs Adaptation
1. **Domain models**: PurchasePayload → ProductPayload (TypedDicts)
2. **BQ transformers**: to_receipt_row/to_detail_rows/to_payment_rows → product-specific extractors
3. **BQ schemas**: Replace purchases JSON schemas with products schemas
4. **Config**: bq_tables section with actual products table definitions
5. **Event filters**: is_purchases_created → is_products_created
6. **PubSub**: topic name for products domain
7. **BigLake catalog**: Uncomment biglake-metastore.tf when ready
8. **CI/CD**: Uncomment build/test/deploy jobs when code ready
9. **Dataform**: Set up products semantic layer definitions

## Reference: Purchases-Collector Patterns (Source of Truth)

### Key Architecture Patterns
1. **Ports & Adapters**: Domain (pure functions) → Adapters (I/O) → Application (wiring)
2. **Config flow**: base.yaml + env.yaml → prepare_dataflow_config.sh (yq merge) → base64 → CLI arg → ConfigurationAdapter → PipelineConfig
3. **Iceberg via BLMS REST**: GoogleAuthManager + vended-credentials, managed.Write transform
4. **Multi-table BQ**: Single pipeline → N BQ tables via FlatMap
5. **Image digest**: Kaniko → image-digest-ref.txt → deploy jobs read digest
6. **Secrets**: GCP Secret Manager → {kafkaCredentials: {confluentId, confluentSecret, ...}}

### Deploy Flow (STG)
```
create-image (Kaniko → GAR 4 destinations)
  → terraform:apply:stg
  → deploy-tables:stg (deploy_schemas.py)
  → deploy:stg
    1. Drain/cancel existing job (5 min timeout)
    2. prepare_dataflow_config.sh (merge YAML → base64)
    3. prepare_dataflow_spec.sh (template → GCS)
    4. deploy_dataflow.sh (gcloud dataflow jobs create)
```

### Deploy Flow (PROD)
```
approve:prod (manual gate)
  → terraform:apply:prod
  → deploy-tables:prod
  → deploy:prod (same as STG but prod params)
```

### Dataflow Parameters
| Param | STG | PROD |
|-------|-----|------|
| project | the1-catalog-data-stg | the1-catalog-data-prod |
| region | asia-southeast1 | asia-southeast1 |
| max-workers | 1 | 2 |
| network | the1-vpc-net-share-stg | the1-vpc-net-share-prod |
| subnetwork | the1-subnet-dataflow-stg | the1-subnet-dataflow-prod |

### Dockerfile Build
- **Dockerfile.base**: python3.12 + java17 + beam 2.71.0 JARs (distroless)
- **Dockerfile**: uv sync → bytecode compile → copy to base image
- **ENTRYPOINT**: /opt/apache/beam/boot
- **ENV**: FLEX_TEMPLATE_PYTHON_PY_FILE="/app/src/main.py"
