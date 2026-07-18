# Gamification — Session Summary

> Exported: 2026-04-02
> Domain: gamification-data (master-collector + account-missions-collector)
> Session: Single session 2026-04-02

---

## a. Session Owner & Role

| Key | Value |
|-----|-------|
| Name | Wasin |
| Role | Data Engineer / Platform Engineer |
| Language | Thai (primary), English (code/docs) |
| Working Style | Fast-paced, direct, expects concise answers. Prefers action over explanation. Reviews code carefully before push. Manages multiple domains (loyalty, sales, gamification, insight). |
| Preference | "สั้น กระชับ ลงมือทำ — ไม่ต้องอธิบายยาว" |
| Git Policy | User handles git add/commit/push manually. Agent must NOT run git commands. |

---

## b. Project Overview

| Key | Value |
|-----|-------|
| GCP Project | `the1-gamification-data-{stg,prod}` |
| Repo | `gitlab.com/The1central/The1/the1-data/gamification-data` |
| Local Path | `/Users/wasin/Documents/ntt_project/the_one/realproject/gamification/gamification-data/` |
| Master-collector Path | `gamification/gamification-data/master-collector/` |
| Account-missions Path | `gamification/gamification-data/account-missions-collector/` |
| Infrastructure Path | `gamification/gamification-data/infrastructure/` |
| Language | Python 3.12 |
| Framework (master) | FastAPI + uvicorn on Cloud Run |
| Framework (account-missions) | Apache Beam 2.71.0 on Dataflow |
| Build | `uv` (package manager), `ruff` (linter), `mypy` (type checker), `pytest` (tests) |
| CI/CD | GitLab CI → Kaniko build → GAR → Cloud Run / Dataflow deploy |
| Dataform | `master-collector/dataform/` — source Iceberg → BQ refined |
| BLMS Scripts | `/realproject/blms_scripts/` — BigLake Metastore management |

---

## c. Architecture

### master-collector (Cloud Run batch)

```
┌──────────────────┐    ┌──────────────────────┐    ┌────────────────┐    ┌──────────────┐
│  Cloud Scheduler │───>│  master-collector    │───>│  Iceberg       │    │  BQ Refined  │
│  (1 AM Bangkok)  │    │  (Cloud Run FastAPI) │    │  (GCS via BLMS │    │  (Dataform)  │
│  POST /trigger   │    │                      │    │   REST catalog)│    │              │
└──────────────────┘    │  Pipeline 1: missions│    │  source.       │───>│  refined.    │
                        │   REST API → passthru│    │   missions     │    │   missions   │
                        │   → IcebergAdapter   │    │                │    │   missions_  │
                        │                      │    │  source.       │───>│    outcome   │
                        │  Pipeline 2: ballots │    │   ballots      │    │  refined.    │
                        │   REST API → passthru│    │                │    │   ballots    │
                        │   → IcebergAdapter   │    └────────────────┘    └──────────────┘
                        └──────────────────────┘

Source: REST API (Private Gateway)
  - GET /gamification/v1/missions (paginated, 200/page)
  - GET /gamification/v1/ballots (paginated, 200/page)
  - Auth: Keycloak OAuth (realm: integration / integration-np)
Sink: Iceberg source tables (raw JSON in `data` column, partitioned by ingested_date)
Refined: Dataform SQL (JSON extraction + UNNEST → BQ refined tables)
```

### account-missions-collector (Dataflow streaming)

```
┌─────────────┐    ┌───────────────────────┐    ┌────────────────┐
│  Kafka       │───>│ account-missions-     │───>│  Iceberg       │
│  (gamification│   │  collector            │    │  (5 per-topic  │
│   .missions.*)│   │  (Dataflow streaming) │    │   tables)      │
│  5 topics     │   │                       │    └────────────────┘
└─────────────┘    │  ┌──────────────┐     │
                   │  │ Filter:      │     │    ┌────────────────┐
                   │  │ eligible +   │─────│───>│  Bigtable      │
                   │  │ activated    │     │    │  (martech_map) │
                   │  └──────────────┘     │    └────────────────┘
                   └───────────────────────┘

Source: 5 Kafka topics
  - gamification.missions.{eligible,activated,inprogress,completed,failed}
Sink:
  - Iceberg: 5 per-topic tables (TopicRoutedIcebergAdapter)
  - Bigtable: martech_map (only eligible + activated events)
```

---

## d. Components Managed

| Component | Mode | Source | Sink | Status |
|-----------|------|--------|------|--------|
| master-collector | Batch (Cloud Run + Scheduler) | REST API (missions, ballots) | Iceberg source | Active (STG + PROD) |
| Dataform (master) | CI-triggered / Scheduled | Iceberg source | BQ refined (missions, ballots, missions_outcome) | Active, has bugs |
| account-missions-collector | Streaming (Dataflow) | Kafka (5 topics) | Iceberg + Bigtable | Active |
| Infrastructure (terraform) | CI-triggered | - | GCS, GAR, BLMS, Secret Manager, Cloud Run, Scheduler | Active |

---

## e. Key Technical Decisions

### 1. UNNEST fix: INNER JOIN → LEFT JOIN
- **Issue**: `, UNNEST(...)` = implicit INNER JOIN → rows with empty arrays silently dropped
- **Fix**: `LEFT JOIN UNNEST(...) ON TRUE` → preserves rows with empty arrays (NULL columns)
- **Applies to**: missions.sqlx (outcomes), ballots.sqlx (rules), missions_outcomes.sqlx (outcomes)
- **Ref**: [Google BQ docs - Work with arrays](https://docs.google.com/bigquery/docs/arrays)

### 2. nullifyEmpty JS function — keep as-is
- Converts `''`, `'undefined'`, `'null'`, `'[]'`, `'{}'` → NULL
- Safe on INT64/DATETIME columns (those values don't appear, acts as safety net)
- `[]` → NULL doesn't impact UNNEST (both produce 0 rows)

### 3. SAFE_CAST for cross-env data differences
- STG `spendingRate` is FLOAT, PROD is INT
- `CAST(... AS INT64)` crashes on float string `'2500.5'`
- `SAFE_CAST(... AS INT64)` returns NULL for float values (acceptable for STG)
- Alternative: promote to FLOAT64 first, then downcast

### 4. Passthrough transform pattern
- master-collector does NO field extraction in Python pipeline
- Raw JSON stored in Iceberg `data` column
- All extraction deferred to Dataform SQL layer (separation of concerns)

### 5. Dataform source reference
- Uses `${ref({schema: "source", name: "missions"})}` for table references
- `workflow_settings.yaml` has `vars.source_catalog` for cross-catalog access
- `source_catalog` value is environment-specific (STG/PROD)

---

## f. Completed Work

| Item | Status |
|------|--------|
| Full codebase exploration (master-collector, account-missions-collector, infrastructure) | DONE |
| Full reference collector exploration (sales, messages, partner, loyalty) | DONE |
| Platform docs + BLMS scripts exploration | DONE |
| Identified UNNEST INNER JOIN bug in all 3 .sqlx files | DONE |
| Identified missions_assertions.sqlx `code` → `mission_code` bug | DONE |
| Identified ballots.sqlx missing comma syntax issue | DONE |
| Identified ingested_date_time missing from final SELECT | DONE |
| User applied LEFT JOIN UNNEST fix to missions.sqlx + ballots.sqlx | DONE (by user) |
| User applied SAFE_CAST for spendingRate/multiplier | DONE (by user) |
| User applied nullifyEmpty to ballots.sqlx | DONE (by user) |
| User applied CTE pattern (EXTRACT_SCHEMAS) to ballots.sqlx | DONE (by user) |
| User changed `${ref()}` syntax for source table references | DONE (by user) |

---

## g. Pending Work

| Item | Priority | Notes |
|------|----------|-------|
| missions_outcomes.sqlx LEFT JOIN UNNEST fix | HIGH | Same INNER JOIN bug |
| missions_assertions.sqlx: `code` → `mission_code` | HIGH | Column doesn't exist, causes runtime error |
| Test files (missions_test.sqlx, ballots_test.sqlx) update | MEDIUM | Column names don't match query output |
| Dataform workflow FAILED investigation | HIGH | 200ms failure = likely permission issue, not SQL |
| ingested_date_time missing from missions.sqlx final SELECT | LOW | Column created in CTE but not selected |
| account-missions-collector Iceberg write error | MEDIUM | `Expected all data writers to be closed` — known Beam IcebergIO bug |

---

## h. Memory Files Exported

| Filename | Description |
|----------|-------------|
| SESSION_SUMMARY.md | This file — complete session context |
| MEMORY.md | Memory index (copied from auto memory) |
| mistakes_and_rules.md | Critical rules + past mistakes log |
| feedback_verify_before_answer.md | Feedback patterns: verify before answering |

Note: No gamification-specific memory files existed in auto memory. All gamification context is captured in this SESSION_SUMMARY.md.

---

## i. Key Rules

### Project Rules (MUST FOLLOW)
1. **No git commands** — no branch, add, commit, push
2. **Must run after code changes**: `uv sync`, `ruff`, `mypy`, `pytest`, `pre-commit`
3. **Verify before answering** — read actual code/data, don't guess
4. **Short and direct** — action over explanation

### Path Reference
| Resource | Path |
|----------|------|
| master-collector | `gamification/gamification-data/master-collector/` |
| account-missions-collector | `gamification/gamification-data/account-missions-collector/` |
| Infrastructure | `gamification/gamification-data/infrastructure/{collector}/` |
| Common infra | `gamification/gamification-data/infrastructure/common/GCP/` |
| Scripts | `gamification/gamification-data/scripts/` |
| Root CI | `gamification/gamification-data/.gitlab-ci.yml` |
| Dataform | `gamification/gamification-data/master-collector/dataform/` |
| Platform docs | `the1-re-data-platform/doc/` |
| BLMS scripts | `blms_scripts/` |

### Service Accounts
| Collector | Service Account |
|-----------|----------------|
| account-missions-collector | `t1-account-missions-collector@the1-gamification-data-{env}` |
| master-collector | `t1-missions-collector@the1-gamification-data-{env}` (shared) |
| CI/CD (terraform) | `t1-gam-data-{env}-sa-iac@the1-gamification-data-{env}` |

### Validation Steps (after code changes)
```bash
cd gamification/gamification-data/master-collector
uv sync
ruff check . && ruff format .
mypy src tests
pytest
pre-commit run --all-files
```

---

## j. Common Errors & Fixes

### 1. Dataform UNNEST drops rows silently
- **Error**: No error — rows just missing from output
- **Cause**: `, UNNEST(...)` = INNER JOIN, empty array → 0 rows → row eliminated
- **Fix**: `LEFT JOIN UNNEST(...) ON TRUE`

### 2. CAST float string to INT64 fails
- **Error**: `Bad int64 value: 2500.5`
- **Cause**: STG data has float values, CAST AS INT64 rejects them
- **Fix**: `SAFE_CAST(... AS INT64)` or promote to FLOAT64 first then downcast

### 3. Dataform workflow FAILED instantly (~200ms)
- **Error**: `state: FAILED` with no action-level detail
- **Cause**: Likely permission issue (SA missing roles)
- **Fix**: Check with `gcloud dataform workflow-invocations query-actions <invocation_id>`
- **Needed roles**: `bigquery.jobUser`, `bigquery.dataEditor`, BigLake access

### 4. account-missions-collector: data writers still open
- **Error**: `Expected all data writers to be closed, but found 1 data writer(s) still open`
- **Cause**: Known Apache Beam IcebergIO bug — race condition in `RecordWriterManager.close()`
- **Possible fixes**: Increase `triggering_frequency_seconds`, reduce max_workers, upgrade Beam version

---

## k. Cross-Domain Dependencies

### Shared Infrastructure
| Resource | Used By | Location |
|----------|---------|----------|
| BigLake Metastore catalog | Both collectors | `infrastructure/common/GCP/biglake-metastore.tf` |
| GCS source bucket | Both collectors | `infrastructure/common/GCP/gcs-bucket.tf` |
| BQ datasets (source, refined, public) | Both collectors + Dataform | `infrastructure/common/GCP/bigquery.tf` |
| VPC network | Both collectors | `the1-vpc-net-share-{env}` (shared with other domains) |

### Common Libraries
| Library | Version | Used By |
|---------|---------|---------|
| `common-data-python-dataflow` | 0.0.24 | account-missions-collector |
| `common-data-python-cloudrun` | 0.0.29 | master-collector |
| Both from | `common/common-data/` repo | Shared across all domains |

### Cross-Domain
| Dependency | Details |
|------------|---------|
| Bigtable (insight) | account-missions writes to `the1-insight-{env}` project's Bigtable `martech_map` table |
| Private Gateway | master-collector calls `private-gateway{-stg}.the1.co.th` (shared API gateway) |
| Keycloak IAM | master-collector authenticates via `the1-corporate-iam.cloud-iam.com` |
| Kafka (Confluent) | account-missions reads from Confluent Cloud Kafka (AWS ap-southeast-1) |

---

## Active Plan

No active plan in this session. Session was exploratory + advisory (review dataform SQL, identify bugs, provide fixes).
