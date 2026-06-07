# Message Domain -- Knowledge Base

> Last updated: 2026-04-05

## 1. Overview

| Key | Value |
|-----|-------|
| GCP Project | `the1-messaging-data-{stg,prod}` |
| Repo | `gitlab.com/The1central/The1/the1-data/messaging-data` |
| Local Path | `message/messaging-data/` |
| Active collectors | 2: messages-collector (streaming), master-collector (batch) |
| Inactive collectors | 2: communications-collector, templates-collector (empty placeholders) |
| Language | Python 3.12 |
| Build | uv, ruff, mypy, pytest, pre-commit |

## 2. messages-collector (Streaming / Dataflow)

**Architecture**: Kafka -> Apache Beam (Dataflow) -> Iceberg + BQ + PubSub + Bigtable

| Key | Value |
|-----|-------|
| Framework | Apache Beam 2.71.0 |
| Common lib | common-data-python-dataflow 0.0.24 |
| Kafka bootstrap | `pkc-312o0.ap-southeast-1.aws.confluent.cloud:9092` |
| Group ID | `messaging-data-messages-collector` |
| Window | 5 seconds |
| Iceberg trigger | STG 60s, PROD 300s |
| Max workers | STG 1, PROD 2 |

**Kafka Topics** (5):
- `messaging.messages.created`
- `messaging.messages.sent`
- `messaging.messages.opened`
- `messaging.messages.clicked`
- `messaging.messages.delivered`

**Filter**: Only `messaging.messages.delivered` topic is filtered (for Bigtable)

**Sinks** (4 destinations -- multi-sink fanout from single Kafka stream):
1. **Iceberg**: Single `source.messages` table via `GcsIcebergWriterAdapter` (BLMS REST catalog, namespace `source`, partitioned by `ingested_date`). Warehouse: `gs://the1-messaging-data-source-{env}`
2. **BigQuery refined**: `refined.enriched_messages_communications` table via `BigQueryWriterAdapter`. **BQ schema** (9 columns): `accountId`, `memberId`, `messageId`, `communicationId`, `communicationCode`, `templateId`, `messageCode`, `transactionAt`, `status`. Partitioned by **DAY** on `transactionAt`.
3. **PubSub**: Topic `messages` in project -- published via `PubSubWriterAdapter`. Subscribers: `t1-martech-map` SA and `t1-martech-purchases` SA (cross-project to `the1-martech-insights-{env}`)
4. **Bigtable**: `martech_map` table in `t1-insight-bt` instance (project `the1-insight-{env}`). Column family `messaging`, column `communicationCode`. Row key: `accountId#memberId`

**Code structure** (`messages-collector/`):
- `src/main.py` -- Composition root: KafkaReaderAdapter, BigtableAdapter, GcsIcebergWriterAdapter, PubSubWriterAdapter, BigQueryWriterAdapter -> PipelineBuilder
- `src/domain/schemas.py` -- RAW_EVENT_BEAM_SCHEMA
- `src/application/row_mappers.py` -- to_raw_event_row
- `config/base.yaml` -- All config (kafka, iceberg, bigquery, bigtable, pubsub)
- `config/{stg,prod}.yaml` -- Environment overrides

## 3. master-collector (Batch / Cloud Run)

**Architecture**: Cloud Scheduler -> Cloud Run (FastAPI) -> REST API (with detail enrichment) -> Iceberg -> Dataform -> BQ

| Key | Value |
|-----|-------|
| Framework | FastAPI + uvicorn on Cloud Run |
| Common lib | common-data-python-cloudrun 0.0.35 |
| PyIceberg | 0.11.0 (gcsfs, pyiceberg-core) |
| Auth | Keycloak OAuth (realm: `integration` prod, `integration-np` stg) |
| API gateway | `private-gateway.the1.co.th` (prod), `private-gateway-stg.the1.co.th` (stg) |
| Billing mode | requests (scale to zero) |

**Pipelines** (2):
1. **communications**: `GET /messaging/v1/communications` (paginated, 200/page) -> `api_detail_lookup` transform (per-record `GET /messaging/v1/communications/{id}`, **max_concurrency 50**, merge_strategy replace) -> Iceberg `source.communications`
2. **templates**: `GET /messaging/v1/templates` (paginated, 200/page) -> `api_detail_lookup` transform (per-record `GET /messaging/v1/templates/{templateId}`, **max_concurrency 50**) -> Iceberg `source.templates`

**Key difference from gamification master-collector**: Uses `api_detail_lookup` transform (not passthrough) -- fetches detail per record with semaphore-bounded concurrency (50 concurrent) and replaces list data with full detail response.

**Schema strategies**: `CommunicationsSchemaStrategy` and `TemplatesSchemaStrategy` -- each defines entity-specific Iceberg table name and schema fields.

**Code structure** (`master-collector/`):
- `src/main.py` -- Composition root: DEFAULT_TRANSFORM_BUILDERS for api_detail_lookup, CommunicationsSchemaStrategy + TemplatesSchemaStrategy
- `config/base.yml` -- Sources (list + detail endpoints), transforms (enricher configs), sinks, pipelines
- `config/{stg,prod}.yml` -- Environment overrides

**Iceberg sinks**: BLMS REST catalog, namespace `source`, partition by `ingested_date`. Warehouse: `gs://the1-messaging-data-source-{env}`

## 4. Dataform Layer

**Location**: `master-collector/dataform/`

### Entities

**Communications** (2-layer):
- `communications/source/communications.sqlx` -- Source declaration
- `communications/refined/communications.sqlx` -- JSON extraction -> refined table. Extracts **30+ fields** including: `channels` array (UNNEST), `time` struct (with timezone fields), `messages` array (with per-message content/subject/sender), `links` array (with URL/label pairs), plus standard metadata fields. Uses incremental merge with `communication_id` as unique key.

**Templates** (2-layer + tests):
- `templates/source/templates.sqlx` -- Source declaration
- `templates/refined/templates.sqlx` -- JSON extraction -> refined table
- `templates/tests/refined/templates_assertion_refined.sqlx` -- Assertions
- `templates/tests/refined/templates_test_refined.sqlx` -- Tests

### Terraform scheduling (`infrastructure/master-collector/dataform.tf`)
- Release configs: `templates-daily`, `communications-daily` (git `main`, every 5 min demo schedule)
- Workflow configs: daily at 01:00 BKK, tagged execution (`templates` / `communications`)
- SA: `service_account_iac` (IAC SA, not workload SA)

## 5. Infrastructure (Terraform)

### Per-collector infra (`infrastructure/{collector}/`)

**messages-collector**:
- `artifact-registry.tf` -- GAR repo
- `biglake-metastore.tf` -- BigLake catalog creation + IAM (SA editor + admin for specific users)
- `bigquery.tf` -- Source BQ dataset linked to BigLake catalog + dataset IAM (dataOwner for SA)
- `gcs-bucket.tf` -- Source bucket + config/flex-template bucket + legacy bucket (old naming)
- `pubsub.tf` -- PubSub topic `messages` with exactly-once delivery, 7-day retention, publishers (SA) + subscribers (martech SAs)
- `secret-manager.tf` -- Secret container
- `schemas/` -- BQ table schemas + deploy.py
- `templates/` -- Dataflow flex template spec

**master-collector**:
- `artifact-registry.tf` -- GAR repo
- `biglake-metastore.tf` -- BLMS catalog IAM (editor for SA, admin for 2 hardcoded admin emails)
- `cloud-run.tf` -- Cloud Run service (scale 0-5, internal ingress, VPC egress, health probes) + 2 Cloud Schedulers (communications at 1:00 AM, templates at 1:30 AM BKK)
- `dataform.tf` -- Dataform repository + release/workflow configs (communications + templates)
- `secret-manager.tf` -- Secret container

### Common infra (`infrastructure/common/GCP/`)
- `artifact-registry.tf` -- Shared GAR (no BigLake catalog here -- each collector has own)
- `main.tf`, `providers.tf`, `variables.tf` -- Terraform base config

**Note**: Unlike gamification, message domain has no common BigLake catalog or BQ datasets in common infra. Each collector manages its own catalog.

### Legacy resources
- `legacy_source_bucket` and `legacy_catalog` in messages-collector -- old naming convention `the1-<domain>-<env>-<layer>` (should be `the1-<domain>-<layer>-<env>`). Marked with `TODO(legacy)` and `prevent_destroy = true`. Non-empty, requires manual cleanup.

## 6. CI/CD Structure

**Root** `.gitlab-ci.yml`: stages `build -> deploy-stg -> test-stg -> deploy-prod -> test-prod -> rollback`. Trigger events: `manual-deploy`, `terraform-apply`, `rollback`. Includes messages-collector + master-collector CIs. communications-collector and templates-collector CIs are **commented out**.

**messages-collector CI** (Dataflow):
- lint -> test -> sonar-scan + gitleaks -> create-base-image (on Dockerfile.base change) -> create-image (STG GAR) -> scan-image -> terraform:apply:stg -> deploy:stg (Dataflow flex template) + deploy-tables:stg (BQ schemas) -> approve:prod (manual) -> promote-image:prod (crane copy) -> deploy:prod + deploy-tables:prod
- deploy-tables jobs: runs `deploy.py` for BQ table creation/migration

**master-collector CI** (Cloud Run):
- lint -> test -> create-image (4 destinations: STG+PROD GAR) -> sonar-scan + gitleaks + scan-image -> terraform:apply:stg -> deploy:stg (gcloud run deploy) -> terraform:apply:prod -> deploy:prod
- redeploy jobs: after terraform-only pipelines

## 7. Inactive Collectors

### communications-collector
- Directory exists at `communications-collector/` but is **empty** (only `.ruff_cache`)
- CI include is **commented out** in root `.gitlab-ci.yml`
- Communications data is collected by **master-collector** instead

### templates-collector
- Directory exists at `templates-collector/` but is **empty** (only `.ruff_cache`)
- CI include is **commented out** in root `.gitlab-ci.yml`
- Templates data is collected by **master-collector** instead

## 8. Config Overview

| Config | messages-collector | master-collector |
|--------|-------------------|-----------------|
| Format | YAML (.yaml) | YAML (.yml) |
| Base | `config/base.yaml` | `config/base.yml` |
| STG | `config/stg.yaml` | `config/stg.yml` |
| PROD | `config/prod.yaml` | `config/prod.yml` |
| Secret | `messages-collector` | `master-collector` |
| Iceberg catalog | BLMS REST | BLMS REST |
| Warehouse | `gs://the1-messaging-data-source-{env}` | `gs://the1-messaging-data-source-{env}` |
