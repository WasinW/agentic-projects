# Gamification Domain -- Knowledge Base

> Last updated: 2026-04-05

## 1. Overview

| Key | Value |
|-----|-------|
| GCP Project | `the1-gamification-data-{stg,prod}` |
| Repo | `gitlab.com/The1central/The1/the1-data/gamification-data` |
| Local Path | `gamification/gamification-data/` |
| Collectors | 2: account-missions-collector (streaming), master-collector (batch) |
| Language | Python 3.12 |
| Build | uv, ruff, mypy, pytest, pre-commit |

## 2. account-missions-collector (Streaming / Dataflow)

**Architecture**: Kafka -> Apache Beam (Dataflow) -> Iceberg + Bigtable + BQ

| Key | Value |
|-----|-------|
| Framework | Apache Beam 2.72.0rc2 |
| Common lib | common-data-python-dataflow 0.0.24 |
| Kafka bootstrap | `pkc-312o0.ap-southeast-1.aws.confluent.cloud:9092` |
| Group ID | `gamification-data-account-missions-collector` |
| Window | 5 seconds |
| Iceberg trigger | STG 60s, PROD 300s |
| Max workers | STG 1, PROD 2 |

**Kafka Topics** (5):
- `gamification.missions.eligible`
- `gamification.missions.activated`
- `gamification.missions.inprogress`
- `gamification.missions.completed`
- `gamification.missions.failed`

**Sinks**:
- **Iceberg**: 5 per-topic tables via `TopicRoutedIcebergAdapter` (BLMS REST catalog, namespace `source`, partitioned by `ingested_date`). Uses **staggered flush**: base triggering frequency 300s (PROD) + `topic_index * 60s` per topic to avoid concurrent Iceberg commits across all 5 tables.
- **Bigtable**: `martech_map` table in `t1-insight-bt` instance (only `eligible` + `activated` topics filtered). Column family `gamification`, columns: `missionCode`, `companyCode`. Row key pattern: `accountId#memberId` -- the martech_map adapter creates **3 row keys** from a single record: `{accountId}`, `{memberId}`, and `{accountId}#{memberId}` (all pointing to same data).
- **BQ refined**: `account_missions` table with `join_with` enrichment from `refined.missions` (scheduled at `0 3 * * *` BKK time, i.e., 3AM daily). Joined on `mission_id`, pulling **13 joined columns**: outcome, outcomeDate, outcomeExpirationDate, milestoneGroupType, milestoneGroupName, milestoneDescription, milestoneTrackerType, milestoneTrackerTarget, milestoneTrackerUnit, rewardName, rewardDescription, rewardType, rewardValue.

**Code structure** (`account-missions-collector/`):
- `src/main.py` -- Composition root: KafkaReaderAdapter, BigtableAdapter, TopicRoutedIcebergAdapter -> PipelineBuilder
- `src/adapters/output/iceberg.py` -- TopicRoutedIcebergAdapter (per-topic Iceberg routing with staggered flush)
- `src/adapters/output/bigtable.py` -- BigtableAdapter (filter + write)
- `src/adapters/output/bigquery/` -- BigQuery writer with join enrichment
- `config/base.yaml` -- All config (kafka, iceberg, bigquery, bigtable)
- `config/{stg,prod}.yaml` -- Environment overrides (warehouse_path, trigger freq, bigtable project)

## 3. master-collector (Batch / Cloud Run)

**Architecture**: Cloud Scheduler (1AM BKK) -> Cloud Run (FastAPI) -> REST API -> Iceberg -> Dataform -> BQ

| Key | Value |
|-----|-------|
| Framework | FastAPI + uvicorn on Cloud Run |
| Common lib | common-data-python-cloudrun 0.0.35 |
| PyIceberg | 0.11.0 (gcsfs, pyiceberg-core) |
| Auth | Keycloak OAuth (realm: `integration` prod, `integration-np` stg) |
| API gateway | `private-gateway.the1.co.th` (prod), `private-gateway-stg.the1.co.th` (stg) |
| Billing mode | requests (scale to zero) |

**Pipelines** (2):
1. **missions**: `GET /gamification/v1/missions` (paginated, 200/page, sorted by missionId) -> **passthrough transform** -> Iceberg `source.missions`
2. **ballots**: `GET /gamification/v1/ballots` (paginated, 200/page, sorted by ballotId) -> **passthrough transform** -> Iceberg `source.ballots`

**Key difference from message master-collector**: Uses passthrough transform (no detail enrichment) -- list API response is written directly to Iceberg.

**Code structure** (`master-collector/`):
- `src/main.py` -- Composition root: FastAPI app factory with builder dicts (AUTH/SOURCE/DESTINATION/TRANSFORM)
- `src/adapters/output/gcs_iceberg/master_schema_strategy.py` -- `MissionsSchemaStrategy` and `BallotsSchemaStrategy`, both inheriting from `MasterBaseSchemaStrategy`. The base strategy defines the shared Iceberg schema structure (raw JSON `data` column + `ingested_date` + `ingested_at`); subclasses provide entity-specific table names.
- `config/base.yml` -- Sources, sinks, pipelines, auth config
- `config/{stg,prod}.yml` -- Environment overrides (project_id, base_url, catalog/warehouse)

**Iceberg sinks**: BLMS REST catalog (`biglake.googleapis.com`), namespace `source`, partition by `ingested_date` (identity). Warehouse: `gs://the1-gamification-data-source-{env}`

## 4. Dataform Layer

**Location**: `master-collector/dataform/` and `account-missions-collector/dataform/`

### master-collector Dataform
3-layer model: **source -> refined -> public**

**Source declarations** (`.sqlx`): `source/missions.sqlx`, `source/ballots.sqlx`
**Refined transformations**: `refined/missions.sqlx`, `refined/ballots.sqlx` (JSON extract from `data` column, UNNEST arrays, SAFE_CAST)
**Public views**: `public/missions.sqlx`, `public/ballots.sqlx`
**Tests**: assertions + unit tests per entity (`tests/missions_*.sqlx`, `tests/ballots_*.sqlx`)

Scheduled via Terraform (`dataform.tf`):
- Release configs: `missions-daily`, `ballots-daily` (git `main`, every 5 min demo schedule)
- Workflow configs: daily at 01:00 BKK, tagged execution (`missions` / `ballots`)
- SA: `t1-master-collector@the1-gamification-data-{env}`

### account-missions Dataform
- `public/account_missions.sqlx` -- single public view

### Key SQL patterns
- `LEFT JOIN UNNEST(...) ON TRUE` (not implicit INNER JOIN) to preserve rows with empty arrays
- `nullifyEmpty()` JS function: converts empty strings/undefined/null to SQL NULL
- `SAFE_CAST` for cross-env type differences (e.g., float vs int spendingRate)
- Source refs: `${ref({schema: "source", name: "missions"})}` with `vars.source_catalog`

## 5. Infrastructure (Terraform)

### Per-collector infra (`infrastructure/{collector}/`)

**account-missions-collector**:
- `artifact-registry.tf` -- GAR repo
- `biglake-metastore.tf` -- BLMS catalog IAM (editor role for SA)
- `gcs-bucket.tf` -- Dataflow staging bucket IAM (objectAdmin for managed transforms)
- `secret-manager.tf` -- Secret container for Kafka/API credentials
- `templates/container_spec.json` -- Dataflow flex template spec

**master-collector**:
- `artifact-registry.tf` -- GAR repo
- `biglake-metastore.tf` -- BLMS catalog IAM
- `cloud-run.tf` -- Cloud Run service (scale 0-5, internal ingress, VPC egress, health probes)
- `cloud-scheduler.tf` -- Scheduler job (1AM BKK, POST `/trigger`, OIDC auth, 30min deadline)
- `dataform.tf` -- Dataform repository + release/workflow configs (missions + ballots)
- `gcs-bucket.tf` -- Source bucket
- `secret-manager.tf` -- Secret container

### Common infra (`infrastructure/common/GCP/`)
- `biglake-metastore.tf` -- Shared BigLake catalog
- `bigquery.tf` -- BQ datasets (source, refined, public)
- `gcs-bucket.tf` -- Shared GCS source bucket

### Service Accounts
| Collector | SA |
|-----------|-----|
| account-missions-collector | `t1-account-missions-collector@the1-gamification-data-{env}` |
| master-collector | `t1-missions-collector@the1-gamification-data-{env}` |

## 6. CI/CD Structure

**Root** `.gitlab-ci.yml`: stages `build -> deploy-stg -> deploy-prod`, includes common-data pipeline, collector CIs, dataform template. Trigger events: `manual-deploy`, `terraform-apply`, `dataform-deploy`. Pipeline type guards block cross-type job execution.

**account-missions-collector CI** (Dataflow):
- lint -> test -> sonar-scan + gitleaks -> create-base-image (on Dockerfile.base change) -> create-image (STG GAR) -> scan-image -> deploy:stg (Dataflow flex template via deploy_dataflow.sh) -> approve:prod (manual) -> promote-image:prod (crane copy STG->PROD) -> deploy:prod
- Dataform section: build -> deploy:stg -> deploy:prod (SA-scoped)

**master-collector CI** (Cloud Run):
- lint -> test -> sonar-scan + gitleaks -> create-image (4 destinations: STG+PROD GAR) -> scan-image -> terraform:apply:stg -> deploy:stg (gcloud run deploy) -> terraform:apply:prod -> deploy:prod
- redeploy jobs: after terraform-only pipelines, re-deploy `:latest` to avoid placeholder image
- Dataform section: unit-test (Node.js + dataform cli) -> build -> deploy:stg -> assertion:stg -> deploy:prod

## 7. Config Overview

| Config | account-missions | master-collector |
|--------|-----------------|-----------------|
| Format | YAML (.yaml) | YAML (.yml) |
| Base | `config/base.yaml` | `config/base.yml` |
| STG | `config/stg.yaml` | `config/stg.yml` |
| PROD | `config/prod.yaml` | `config/prod.yml` |
| Secret | `account-missions-collector` | `master-collector` |
| Iceberg catalog | BLMS REST (biglake.googleapis.com) | BLMS REST (biglake.googleapis.com) |
| Warehouse | `gs://the1-gamification-data-source-{env}` | `gs://the1-gamification-data-source-{env}` |
