# Common Shared Libraries -- Knowledge Base

## Overview

The common layer provides reusable packages, CI/CD templates, deployment scripts, and Terraform modules shared across all data platform domains (loyalty, partner, sales, message, gamification, etc.).

**Components:**

1. **common-python-dataflow** (v0.1.0) -- Apache Beam adapters for Dataflow pipelines
2. **common-python-cloudrun** (v0.0.7) -- Ports & Adapters framework for CloudRun batch services
3. **CI/CD templates** (`pipeline/`) -- Reusable GitLab CI job templates
4. **Deployment scripts** (`scripts/dataflow/`) -- Shell scripts for Dataflow deployment
5. **Terraform modules** (separate repo: `the1-terraform-gcp`) -- 23 GCP infrastructure modules

**Repository:** `The1central/The1/the1-data/common-data`
**Terraform repo:** `The1central/platform/the1-terraform-gcp`

## 1. common-python-dataflow (v0.1.0)

Package name: `common-data-python-dataflow`
Python: >=3.12, Build: hatchling

### Input Adapters

| Adapter | Module | Purpose |
|---------|--------|---------|
| KafkaReader | `common.beam.adapters.input.kafka_reader/` | Kafka consumer with Avro deserialization, schema registry |
| BigQueryReader | `common.beam.adapters.input.bigquery/` | BQ read via config |

KafkaReader includes: `kafka_config.py`, `kafka_reader_adapter.py`, `avro_deserializer.py`, `kafka_transforms.py`, `utils.py`

**KafkaReaderAdapter composite transform (deep detail):**

The `KafkaReaderAdapter` is a Beam composite PTransform that chains 4 steps:

1. **ReadFromKafka** -- reads raw Kafka records (key/value bytes) from configured topics with consumer group
2. **ExtractValue** -- strips Kafka metadata, extracts just the message value bytes
3. **DecodeMessage** -- deserializes bytes to Python dict (supports JSON, Avro with Schema Registry, and auto-detect modes)
4. **FilterDecodeFailures** -- splits stream into success/failure branches; failures go to dead-letter side output for monitoring

This composite is the standard entry point for all streaming Dataflow collectors (loyalty members, sales, gamification account-missions, messages, catalog products).

### Output Adapters

| Adapter | Module | Purpose |
|---------|--------|---------|
| BigQueryWriter | `common.beam.adapters.output.bigquery/` | BQ write with config |
| BigtableWriter | `common.beam.adapters.output.bigtable_writer/` | Bigtable write adapter |
| GCS Iceberg Writer | `common.beam.adapters.output.gcs/` | Iceberg via BigLake Metastore REST catalog |

GCS Iceberg includes: `gcs_biglake_iceberg_writer.py`, `gcs_biglake_iceberg_writer_config.py`, `biglake_metastore_config.py`

**BigQueryWriterAdapter (deep detail):**

- Supports two write modes configured via YAML:
  - **append** mode: standard `WriteToBigQuery` with `WRITE_APPEND` disposition, schema auto-detect or explicit
  - **CDC** mode: uses `row_mutation_info` wrapping -- each row is wrapped with `mutation_type` ("UPSERT" or "DELETE") for BigQuery CDC tables with primary keys
- **DATETIME to STRING normalization**: automatically converts Python `datetime` objects to ISO format strings before writing, because Beam's BQ sink requires string representation for DATETIME columns
- Row mapper function is injected per-collector (transforms domain objects to BQ row dicts)

### Testing Framework

| Module | Purpose |
|--------|---------|
| `common.beam.testing.fixtures` | DirectRunner test fixtures for Beam pipelines |
| `common.beam.testing.fakes` | FakeSink and mock adapters |
| `common.beam.testing.containers` | TestContainers integration (Bigtable, Kafka) |

### Key Dependencies

- `apache-beam[gcp]>=2.70.0`, `pyarrow>=14.0.0,<18.0.0`
- `confluent-kafka>=2.8.0` (avro, schemaregistry)
- `authlib==1.6.9` (for auth flows)
- Dev: `testcontainers>=4.9.0`, `ruff`, `mypy`, `pytest`

## 2. common-python-cloudrun (v0.0.7)

Package name: `common-data-python-cloudrun`
Python: ==3.12.*, Build: hatchling

### Ports (Protocol Interfaces)

Defined in `common_cloudrun/ports.py`:

| Port | Method | Description |
|------|--------|-------------|
| `AuthPort` | `get_auth() -> str` | Authentication credential provider |
| `SourcePort[DataT]` | `extract(params) -> DataContainer[DataT]` | Data extraction from external source |
| `TransformPort[DataT, OutT]` | `transform(container, params) -> DataContainer[OutT]` | Data transformation |
| `SinkPort[OutT]` | `save(container, params) -> None` | Data persistence |
| `PipelinePort` | `execute(params) -> PipelineResult` | Pipeline orchestration |

### Adapters

**Output adapters** (in `adapters/output/`):

- `api_source/` -- `ApiAuthAdapter` (Keycloak OAuth), `ApiSourceAdapter` (paginated REST API client)
- `gcs_iceberg/` -- `IcebergAdapter` (PyIceberg write), `IcebergCatalogProvider` (BLMS REST), `IcebergGcpAuth`, `IcebergSchemaStrategy` (abstract)

**IcebergAdapter (CloudRun, deep detail):**

- Async **append-only** writes -- each batch of records is appended as a new data file to the Iceberg table
- **Auto-create table**: if the table does not exist in the BLMS REST catalog, IcebergAdapter creates it using the schema from the `IcebergSchemaStrategy` subclass
- **PyArrow schema**: converts the strategy's field definitions to a PyArrow schema, then writes Parquet data files to GCS via PyIceberg's `append()` method
- Partition by `ingested_date` (identity partition on INT column)
- Used by all CloudRun master-collectors (partner, gamification, message)

### Application Layer

| Module | Description |
|--------|-------------|
| `batch_pipeline.py` | `BatchPipeline` orchestrator: extract -> transform once -> write to all destinations in parallel |
| `builtin_transforms.py` | Built-in transforms (passthrough, etc.) |
| `api_enrichment_transform.py` | API enrichment transform |

**ApiEnrichmentTransform (deep detail):**

- Used by message master-collector (communications + templates pipelines)
- Performs **semaphore-bounded concurrent detail lookups**: for each record from the list API, fetches the full detail from `GET /{entity}/{id}` with configurable `max_concurrency` (typically 50)
- **Merge strategies** (configured per-pipeline in YAML):
  - `replace` -- detail response completely replaces the list record
  - `merge_detail` -- detail fields are merged into the list record (detail wins on conflict)
  - `merge_source` -- list record fields are merged into detail response (source wins on conflict)
- Uses `asyncio.Semaphore` to bound concurrent HTTP requests and avoid overwhelming the upstream API
- Auth token is passed through from the pipeline's `AuthPort`

### Infrastructure Layer

| Module | Description |
|--------|-------------|
| `builders.py` | `DEFAULT_AUTH_BUILDERS`, `DEFAULT_SOURCE_BUILDERS`, `DEFAULT_DESTINATION_BUILDERS`, `build_passthrough_transform()` |
| `settings.py` | YAML config loader (base + env overlay) |
| `settings_models.py` | Pydantic settings models |
| `gcp_auth.py` | GCP auth utilities |
| `gcp_logging.py` | Structured logging (`ContextLogger`, `LogContext`, `LoggingConfig`, `LoggingConfigurator`) |
| `secret_manager.py` | GCP Secret Manager client |

### Optional Dependencies

- `[iceberg]`: pyiceberg 0.11.0, pyarrow 18.0.0, google-auth
- `[kafka]`: confluent-kafka 2.8.2
- `[pubsub]`: google-cloud-pubsub
- `[gcs]`: google-cloud-storage

### Key Dependencies

- `fastapi>=0.135.2`, `uvicorn>=0.42.0`, `pydantic==2.12.5`, `pydantic-settings==2.13.1`
- `httpx==0.28.1`, `google-cloud-secret-manager==2.27.0`, `pyyaml==6.0.3`

## 3. CI/CD Templates (`pipeline/`)

### V1 Templates (current, used by most domains)

| Template | Key Jobs/Scripts |
|----------|-----------------|
| `common-base.gitlab-ci.yml` | Rules (`.rules_app_changes`, `.rules_infra_*`, `.rules_dataform_changes`), `.common-gcp-prepare`, `.uv_base`, `.resource_lock` |
| `common.gitlab-ci.yml` | Extends common-base + adds `.common-terraform-plan/apply`, `.common-sonar-scan`, `.common-scan-gitleaks`, `.common-scan-image`, `.common-scan-defect-dojo`, DefectDojo upload mixins, `common-gcp:terraform:apply:{stg,prod}` |
| `dataflow.gitlab-ci.yml` | `.dataflow-linter`, `.dataflow-test`, `.dataflow-check-registry`, `.dataflow-terraform-apply`, `.dataflow-build-image`, `.dataflow-promote-image`, `.dataflow-deploy`, `.dataflow-approve-prod` |
| `terraform.gitlab-ci.yml` | `.common-terraform-plan`, `.common-terraform-apply` (standalone reusable blocks) |

### V2 Templates (newer, not universally adopted)

| Template | Description |
|----------|-------------|
| `v2/base.gitlab-ci.yml` | Trigger rules, GCP prepare, UV base, resource lock |
| `v2/dataflow.gitlab-ci.yml` | Dataflow-specific templates |
| `v2/scan.gitlab-ci.yml` | Security scanning templates |
| `v2/terraform.gitlab-ci.yml` | Terraform templates |
| `v2/example-service.gitlab-ci.yml` | Example usage pattern |

### Usage Pattern

Domains include common templates in root `.gitlab-ci.yml`:

```yaml
include:
  - project: "The1central/The1/the1-data/common-data"
    file: "pipeline/common.gitlab-ci.yml"
```

Then extend in service-level CI files: `.my-service-vars` + `extends: [.dataflow-test]`

## 4. Deployment Scripts (`scripts/dataflow/`)

| Script | Purpose |
|--------|---------|
| `deploy_dataflow.sh` | Deploy Dataflow job: create from template, set pipeline options, SA, network |
| `prepare_dataflow_config.sh` | Merge base + env YAML configs into single config string |
| `prepare_dataflow_spec.sh` | Render container_spec.json template with image digest, upload to GCS |

Used by `.dataflow-deploy` CI template. Can be downloaded at CI runtime from common-data repo or used from local `scripts/` copy.

## 5. Terraform Modules (`the1-terraform-gcp`)

23 modules in `modules/` directory:

| Category | Modules |
|----------|---------|
| Compute | `cloud-run`, `clickhouse` |
| Storage | `gcs-bucket`, `gcs-bucket-iam` |
| Data | `bigquery-connection`, `bigquery-dataset`, `bigquery-dataset-iam`, `bigquery-job-iam`, `bigquery-metadata-iam`, `bigquery-table-iam` |
| Bigtable | `bigtable-instance-access`, `bigtable-instance-iam`, `bigtable-table-iam` |
| Messaging | `pubsub` |
| Registry | `artifact-registry` |
| IAM | `common-iam`, `service-accounts`, `organizations-iam`, `projects-iam` |
| Networking | `cloud-armor-waf`, `external-serverless-xlb`, `internal-loadbalancer`, `internal-serverless-ilb`, `common-services` |

Sourced via: `git::https://gitlab.com/The1central/platform/the1-terraform-gcp.git//modules/{module}?ref=main`

## 6. Version Matrix

### common-python-dataflow

Used by: loyalty (members/tiers/m-t-h/purchases-collector), sales, message, catalog domains.
Referenced via git tag in each domain's `pyproject.toml`.

### common-python-cloudrun (v0.0.7)

| Domain | Version |
|--------|---------|
| Partner (master-collector) | tag 0.0.35 |

### CI Templates

| Domain | Template Version |
|--------|-----------------|
| Partner | V1 (`pipeline/common.gitlab-ci.yml`) |
| Loyalty | V1 (`pipeline/common.gitlab-ci.yml` + `pipeline/common-base.gitlab-ci.yml`) |
| Most domains | V1 |
| Some newer domains | V2 available but adoption varies |

## Key Patterns

1. **Ports & Adapters**: Both packages enforce clean architecture via Protocol interfaces
2. **YAML-driven config**: `base.yml` + `{env}.yml` overlay pattern (both dataflow and cloudrun)
3. **Builder dicts**: Map YAML `type` strings to concrete adapter constructors
4. **BLMS REST catalog**: Standard Iceberg catalog for all domains (BigLake Metastore, vended credentials)
5. **Kaniko builds**: Container images built with Kaniko, pushed to GAR (stg+prod)
6. **Terraform workspaces**: `stg`/`prod` workspaces from same .tf files
