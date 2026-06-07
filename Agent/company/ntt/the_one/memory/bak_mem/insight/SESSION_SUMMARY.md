# Insight Domain — Session Summary

> Exported: 2026-04-05
> Domain: `insight` (insight-api repo)
> Sessions covered: Multiple sessions up to 2026-04-04

---

## A. Session Owner & Role

| Key | Value |
|-----|-------|
| **Role** | Data Engineer / Platform Engineer |
| **Language** | Thai (working), English (code/docs) |
| **Working Style** | ลงมือทำเลย ไม่ต้องอธิบายยาว, ตรงประเด็น, ใช้ภาษาตรงๆ |
| **Communication** | จะด่าถ้าผิดซ้ำ ("มึงมั่วป่าววะ", "ควย") — ต้อง verify ก่อนตอบเสมอ |
| **Rules** | ไม่ทำ git commands (no branch/add/commit/push), ต้อง run ruff/mypy/pytest หลังแก้ code |

---

## B. Project Overview

| Key | Value |
|-----|-------|
| **GCP Projects** | `the1-insight-stg` / `the1-insight-prod` |
| **Repo** | `insight-api` (GitLab: The1central/The1/the1-api/insight-api) |
| **Local Path** | `/Users/wasin/Documents/ntt_project/the_one/realproject/insight/insight-api/` |
| **Tech Stack** | Apache Beam (Dataflow), BigQuery, Bigtable, Pub/Sub, S3, Iceberg, Airflow (Composer), Terraform |
| **Python** | 3.11 (V1/V2), 3.12 (V3 collector) |
| **Beam** | 2.69.0 (pipeline), 2.71.0 (collector) |
| **SA** | `t1-ins-{env}-sa-data@the1-insight-{env}.iam.gserviceaccount.com` |

---

## C. Architecture

### Data Flow Overview
```
┌─────────────────────────────────────────────────────────────────────────┐
│                        INSIGHT DATA PLATFORM                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STREAMING (customer-profile-collector):                                │
│    Pub/Sub → Bigtable Read → Transform (to_ms_personas_row)            │
│      ├→ BigQuery CDC UPSERT (ms_personas, primary_key=member_id)       │
│      ├→ S3 Parquet (windowed, via boto3)                               │
│      └→ Periodic MERGE → Iceberg (ms_personas_iceberg)                 │
│                                                                         │
│  STREAMING (customer-profile-pipeline V3):                              │
│    Pub/Sub → Bigtable Read → Mapping Table Transform                   │
│      ├→ BigQuery CDC UPSERT (ms_personas)                              │
│      ├→ S3 Parquet (windowed)                                          │
│      ├→ Consent → BigQuery/Iceberg (events_consents)                   │
│      └→ Consent Export → GCS → S3                                      │
│                                                                         │
│  STREAMING (last-purchases-collector):                                  │
│    Pub/Sub → Bigtable Read → Transform → BigQuery CDC UPSERT           │
│                                                                         │
│  BATCH (customer-svoc-interim):                                         │
│    DTS (S3→BQ) → BQ EXPORT DATA → GCS Parquet                         │
│    Triggered by: Airflow DAG (BigQueryInsertJobOperator)                │
│                                                                         │
│  DTS (S3→BQ):                                                          │
│    mapping_reconcile (hourly), ms_member (daily 6AM),                  │
│    consent_history (disabled), s3_member_accountid_mapping              │
│                                                                         │
│  INFRASTRUCTURE:                                                        │
│    Terraform: infrastructure/data-pipeline/ (BQ, Composer, DTS, etc.)  │
│    Terraform: infrastructure/customer-svoc-interim/ (DTS + BQ views)   │
│    Terraform: infrastructure/last-purchases-collector/ (Dataform)      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## D. Components Managed

| Component | Mode | Source | Sink | Status |
|-----------|------|--------|------|--------|
| **customer-profile-collector** | Streaming | Pub/Sub → Bigtable | BQ CDC + S3 Parquet + Iceberg | Active (refactored: mapping→pure function) |
| **customer-profile-pipeline** (V3) | Streaming | Pub/Sub → Bigtable | BQ CDC + S3 + Iceberg + Consent | Active (CI fixed: base image + COMPOSER_BUCKET) |
| **last-purchases-collector** | Streaming | Pub/Sub → Bigtable | BQ CDC (personas_last_purchases) | Active |
| **customer-svoc-interim** | Batch | DTS (S3→BQ) | BQ EXPORT DATA → GCS Parquet | Active (Airflow DAG) |
| **ms-personas** (V1/V2) | Streaming/Batch | Various | BQ + S3 | Legacy (terraform CI fixed) |

---

## E. Key Technical Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| SVOC export approach | BQ `EXPORT DATA` via Airflow | Dataflow failed after 9hrs OOM on 20GB/300 cols; EXPORT DATA completes in minutes |
| Mapping table → pure function | `to_ms_personas_row()` | Removes BQ mapping table dependency; deterministic, testable, no refresh interval |
| S3 export lag fix | Change `export_interval_sec` 300→3600 | PeriodicImpulse 5min × 3GB S3 copy = watermark backlog 14hrs; 1hr interval matches consent pattern |
| CI variable collision fix | Job-level `INFRASTRUCTURE_RUN_PATH` | GitLab CI merges all included files' top-level variables; svoc overwrote ms-personas |
| COMPOSER_BUCKET | Hardcode `the1-insight-${WORKSPACE_ENV}-data-pipeline-composer` | terraform output unreliable in upload jobs; matches ms-personas fix |
| Docker multi-stage | uv builder + `ARG BASE_IMAGE` | Matches loyalty standard (Dockerfile.base + Dockerfile pattern) |
| Kaniko version | `ghcr.io/osscontainertools/kaniko:v1.26.6-debug` with `entrypoint: [""]` | Old `gcr.io/kaniko-project/executor:v1.9.0-debug` without entrypoint override fails |
| BQ CDC primary_key | `member_id` (snake_case) | BQ column name is snake_case, not camelCase |
| Dataform semantic layer | deploy.py view creation (interim) | Dataform IAM not ready; deploy.py creates public views directly |

---

## F. Completed Work (This Session)

### customer-profile-collector refactoring
- Replaced `TransformSchemasDoFn` + `FullfillSchemasDoFn` (mapping table) → `beam.Map(to_ms_personas_row)` pure function
- Commented consent steps (5/7/9/12-14) in `builder.py`
- Changed `primary_key=["memberId"]` → `["member_id"]`
- Created separate CI: `pipeline/data/customer-profile-collector.gitlab-ci.yml`
- Removed collector jobs from `customer-profile-data-pipeline.gitlab-ci.yml`
- Added CI to `.gitlab-ci.yml` includes

### customer-profile-pipeline V3 CI fix
- Added `create-base-image` steps (stg + prod) for `Dockerfile.base`
- Added `--build-arg BASE_IMAGE` + `--build-arg CI_JOB_TOKEN` to kaniko executor
- Updated kaniko image to `ghcr.io/osscontainertools/kaniko:v1.26.6-debug` with `entrypoint: [""]`
- Hardcoded `COMPOSER_BUCKET` (removed unreliable terraform output)

### ms-personas terraform CI fix
- Added `INFRASTRUCTURE_RUN_PATH: 'infrastructure/data-pipeline/'` to job-level variables (plan/apply × stg/prod)
- Fixed variable collision: svoc CI's top-level `INFRASTRUCTURE_RUN_PATH` was overwriting ms-personas

### ms-personas terraform outputs fix
- Fixed `outputs.tf:39` — reference `s3_member_accountid_mapping` was changed to `aws_member_accountid_mapping` but resource name in `dts.tf` is still `s3_member_accountid_mapping`

### S3 export lag fix (customer-profile-pipeline)
- Changed `export_interval_sec` from 300 to 3600 in `settings.py`
- Root cause: PeriodicImpulse 5min × 3GB blocking S3 copy = watermark backlog

### last-purchases-collector
- Added debug logging in `ParsePayloadDoFn`
- Added `etl_load_timestamp` field
- Created adhoc initial SQL script (TRUNCATE + INSERT for CDC tables)
- Created Dataform semantic layer (public view)
- Created terraform + CI for Dataform (commented, waiting IAM)
- deploy.py `_reconcile_primary_key` added to shared deploy.py

### customer-svoc-interim (full build)
- DTS S3→BQ terraform (727 columns)
- BQ EXPORT DATA via Airflow DAG (replaced failed Dataflow approach)
- Full CI with terraform jobs
- Schema JSONs + views

### ms-personas CI fixes
- Fixed `gsutil rm -r` → `gsutil rm` for `*.py` wildcard
- Hardcoded COMPOSER_BUCKET (removed terraform dependency)
- Fixed YAML invalid (blank line after `!reference`)
- Fixed echo with colon causing YAML dict parse

### deploy.py primary key reconciliation
- Added `_reconcile_primary_key` to shared deploy.py
- ALTER TABLE ADD/DROP PRIMARY KEY with CDC max_staleness handling

---

## G. Pending Work

| Item | Priority | Notes |
|------|----------|-------|
| customer-profile-pipeline deploy error log | Waiting | User said "deploy พังนะ เดี๋ยวเอา log ให้ดู" — not received |
| `src/customer_profile/` cleanup in collector | Medium | Legacy code structure inside collector, not matching standard (`src/domain/`, `src/application/`) |
| `view_events_consents` terraform state | Low | terraform wants to destroy but `deletion_protection=true`; needs `state rm` or re-add to `.tf` |
| Dataform IAM for last-purchases | Blocked | Dataform CI commented; waiting for IAM permissions |
| customer-svoc-interim DAG validation | Medium | Changed from Dataflow to BQ EXPORT DATA; needs prod validation |

---

## H. Memory Files Exported

| File | Description |
|------|-------------|
| `MEMORY.md` | Master index — all memory entries (loyalty + insight + sales) |
| `insight_knowledge_base.md` | Complete insight-api knowledge base (paths, architecture, tables, CI/CD, deps) |
| `loyalty_knowledge_base.md` | Complete loyalty knowledge base (all collectors, infra, schemas, patterns) |
| `catalog_products_knowledge_base.md` | Catalog/products-collector setup KB |
| `sales_knowledge_base.md` | Sales-collector knowledge base |
| `sales_pipeline_knowledge_base.md` | Sales pipeline details |
| `sales_initial_data.md` | Sales initial data load process |
| `sales_schema_migration.md` | Sales schema migration plan |
| `sales_schema_migration_done.md` | Sales schema migration completed summary |
| `sales_deploy_fix.md` | deploy.py INTERVAL syntax fix |
| `mistakes_and_rules.md` | Critical rules + past mistakes to avoid |
| `feedback_verify_before_answer.md` | Feedback: always verify before answering |
| `dofns_comparison.md` | DoFns comparison (members vs messaging pattern) |
| `kafka_schema_changes.md` | New Kafka schema (eligibleTierCode) migration plan |

---

## I. Key Rules

### Paths (CRITICAL — variable collision!)
```yaml
# ms-personas terraform
INFRASTRUCTURE_RUN_PATH: 'infrastructure/data-pipeline/'   # MUST be job-level, not top-level

# customer-svoc-interim terraform
INFRASTRUCTURE_RUN_PATH: 'infrastructure/customer-svoc-interim/'  # top-level in svoc CI

# customer-profile-collector code
RUN_PATH: 'data/customer-profile-collector'

# customer-profile-pipeline code
RUN_PATH: 'data/customer-profile-pipeline'
```

### CI/CD Rules
- **COMPOSER_BUCKET**: Hardcode `the1-insight-${WORKSPACE_ENV}-data-pipeline-composer` — don't rely on terraform output in upload jobs
- **Kaniko**: Use `ghcr.io/osscontainertools/kaniko:v1.26.6-debug` with `entrypoint: [""]` for multi-stage Dockerfiles
- **Dockerfile.base**: Must `create-base-image` (manual) before first `build:image`
- **`!reference` in GitLab CI**: Requires blank line separator in script arrays
- **Terraform in runner**: Use runner default image (has terraform); don't specify `image: hashicorp/terraform` or `image: google/cloud-sdk:slim`

### Validation Steps
```bash
# After code changes
uv sync
uv run ruff check src/ tests/
uv run mypy src/
uv run pytest -v
pre-commit run --all-files
```

### Constraints
- No git commands (user manages git)
- Don't modify files outside scope without asking
- Always `git checkout --` files modified by pre-commit in other collectors
- S3 dependency chain: `boto3==1.34.106`, `botocore==1.34.106`, `s3fs==2024.6.1` — exact pins required

---

## J. Common Errors & Fixes

| Error | Root Cause | Fix |
|-------|-----------|-----|
| `could not parse reference:` (kaniko) | `FROM ${BASE_IMAGE}` without `--build-arg` | Add `create-base-image` step + `--build-arg BASE_IMAGE=$FULL_BASE_IMAGE` |
| `Destination must match exactly 1 URL` (gsutil) | `COMPOSER_BUCKET` empty from terraform output | Hardcode `the1-insight-${WORKSPACE_ENV}-data-pipeline-composer` |
| terraform `No changes` when changes exist | `INFRASTRUCTURE_RUN_PATH` overwritten by svoc CI (variable collision) | Add `INFRASTRUCTURE_RUN_PATH` to job-level variables |
| terraform `Reference to undeclared resource` | `outputs.tf` references resource name different from `dts.tf` | Ensure resource names match between `.tf` files |
| `deletion_protection=true` terraform destroy | Resource removed from `.tf` but still in state with protection | `terraform state rm` the resource |
| YAML invalid after `!reference` | Missing blank line after `!reference` tag in script array | Add blank line separator |
| `echo` line with colon in YAML | YAML parser interprets colon as dict separator | Remove colon or quote the string |
| Dataflow WriteParquet OOM (9hrs) | 20GB × 300 cols + num_shards shuffle | Use BQ `EXPORT DATA` instead |
| S3 export 14hr lag | PeriodicImpulse 5min × 3GB blocking copy | Change interval to 3600s |
| DTS table CDC restriction | `DELETE/UPDATE/MERGE` not supported on CDC UPSERT stream tables | Use `TRUNCATE TABLE; INSERT INTO` |
| `terraform: command not found` | Used `image: google/cloud-sdk:slim` (no terraform) | Use runner default (has terraform) |
| `gcloud dataform: Invalid choice` | `google/cloud-sdk:slim` missing dataform | Use `google/cloud-sdk:552.0.0-stable` or REST API script |

---

## K. Cross-Domain Dependencies

| Dependency | From | To | Notes |
|------------|------|----|-------|
| **Shared deploy.py** | `infrastructure/data-pipeline/schemas/deploy.py` | ms-personas + last-purchases | `_reconcile_primary_key` added — affects all tables |
| **GitLab CI variable collision** | `customer-svoc-interim.gitlab-ci.yml` | `ms-personas.gitlab-ci.yml` | Top-level `INFRASTRUCTURE_RUN_PATH` overwrites; fixed with job-level vars |
| **Terraform state** | `infrastructure/data-pipeline/` | ms-personas CI | Backend prefix `the1-insight/services/personas/ms-personas` — shared state for all data-pipeline resources |
| **GAR repository** | `insight-datapipeline-dataflow-common` | All pipelines | Shared container registry for all Dataflow images |
| **Composer bucket** | `the1-insight-{env}-data-pipeline-composer` | All pipelines | Shared for DAGs, specs, scripts, configs |
| **S3 credentials** | Secret Manager `insight-data-pipeline` | DTS + Dataflow S3 writes | Shared AWS keys |
| **Loyalty domain** | `loyalty-data/` repo | Pattern reference | Collector patterns, IcebergIO, deploy.py — used as reference |
| **Sales domain** | `sales-data/` repo | Pattern reference | BQ lookup cache, enrich DoFn patterns |

---

## L. Active Plan

> From plan file: `/Users/wasin/.claude/plans/crystalline-knitting-micali.md`
> **Status**: Plan for customer-profile-pipeline refactoring to loyalty standard
> **Note**: This plan was created for a separate refactoring effort (not the current session's work)

### Summary
Refactor `customer-profile-pipeline` from legacy structure to loyalty collector standard:
- Phase 1: Config system (YAML + Pydantic + PipelineConfig)
- Phase 2: Restructure directories (`src/customer_profile/` → `src/domain/`, `src/application/`)
- Phase 3: Wire new config flow
- Phase 4: Docker & Tooling (Dockerfile.base, pyproject.toml, uv)
- Phase 5: Cleanup & Verify

**Current status**: Plan exists but execution not started in this session. The collector (`customer-profile-collector`) was refactored separately (builder.py mapping→pure function + CI separation).
