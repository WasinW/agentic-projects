# Catalog Domain — Session Summary

**Export Date**: 2026-04-01
**Domain**: catalog (products-collector)
**Session Focus**: Infrastructure setup, CI/CD, Terraform, Dataform, DTS (S3→BQ)

---

## a. Session Owner & Role

| Key | Value |
|-----|-------|
| **Role** | Data Engineer / Data Architect / Enterprise Architect |
| **Expertise** | GCP Data Platform, Apache Beam (Dataflow), Python, GitLab CI/CD, Terraform |
| **Working Style** | สั้น กระชับ ลงมือทำ — action before explanation |
| **Language** | Thai (primary), English (technical terms) |
| **Key Rule** | ห้ามใช้ git commands (branch/add/commit/push) — user ทำเอง |
| **Validation** | ต้องรัน uv sync, ruff, mypy, pytest, pre-commit หลังแก้โค้ดทุกครั้ง |

---

## b. Project Overview

| Key | Value |
|-----|-------|
| **GCP Project STG** | `the1-catalog-data-stg` (folder: `801076874630`) |
| **GCP Project PROD** | `the1-catalog-data-prod` (folder: `354078186135`) |
| **Service Account** | `t1-products-collector@the1-catalog-data-{env}.iam.gserviceaccount.com` |
| **Repo Location** | `catalog/catalog-data/` (has .git) |
| **Old/Empty (ignore)** | `catalog/catalogs-data/` |
| **Source Template** | Copied from `loyalty/loyalty_paralel/loyalty-data/purchases-collector/` |
| **Tech Stack** | Python 3.12, Apache Beam 2.71.0, Dataflow, Terraform, GitLab CI, Dataform, BigQuery, Iceberg, Kafka, GCS |

---

## c. Architecture

### Current Architecture (products-collector)
```
DATA SOURCES:
  1. S3 (Delta/Parquet) → DTS → BQ refined.ms_product_all (~54.3GB)
  2. Kafka (future) → Dataflow → Iceberg → BQ (not active yet)

SEMANTIC LAYER:
  BQ refined.ms_product_all → Dataform → BQ public.ms_product_all (VIEW)

FLOW:
  S3 (t1-analytics)
    └── s3://t1-analytics/refined/master_data/product/gcp_product_master/*
          ↓ (DTS: Amazon S3 Transfer)
  BQ refined.ms_product_all (TABLE, WRITE_TRUNCATE)
          ↓ (Dataform: products tag)
  BQ public.ms_product_all (VIEW)

FUTURE (Kafka streaming):
  Kafka → ReadFromKafka
    → FixedWindow(5s)
    → AttachEventNameDoFn
    → BuildRawEventDoFn
    → Fan-out:
      1. Filter → Iceberg (products_created)
      2. Filter → Iceberg (products_updated)
      3. All → BQ refined tables
```

---

## d. Components Managed

| Component | Mode | Source | Sink | Status |
|-----------|------|--------|------|--------|
| **DTS (S3→BQ)** | Batch (on-demand/scheduled) | S3 Parquet (Delta) | BQ `refined.ms_product_all` | ACTIVE (disabled=false) |
| **Dataform** | CI-triggered | BQ `refined.ms_product_all` | BQ `public.ms_product_all` (VIEW) | ACTIVE (STG deploy working) |
| **Dataflow Pipeline** | Streaming (future) | Kafka topics | Iceberg + BQ | COMMENTED (code from purchases, needs adaptation) |
| **Terraform** | CI-triggered | HCL in `infrastructure/products-collector/` | GCP resources | ACTIVE (stg + prod) |

---

## e. Key Technical Decisions

| Decision | Reason |
|----------|--------|
| **Copy from purchases-collector** | purchases-collector มี pattern ที่ดีกว่า collector อื่น |
| **DTS for S3→BQ** | Data อยู่ใน S3 (Delta/Parquet) ต้องโหลดเข้า BQ — DTS เป็น managed service ไม่ต้องเขียน pipeline |
| **Dataform for semantic layer** | สร้าง public view จาก refined table — pattern เหมือน purchases |
| **Comment Dataflow CI steps** | Code ยังเป็น purchases logic — uncomment เมื่อ adapt เสร็จ |
| **Comment most terraform resources** | เหลือแค่ GAR, bucket, secret, BQ refined, DTS, dataform — อื่นๆ ค่อย enable |
| **DTS path changed** | `product_all/**` → `gcp_product_master/*` ตามที่ data อยู่จริง |
| **Schema: all STRING** | BQ table จาก DTS/Parquet สร้าง columns ทั้งหมดเป็น STRING |

---

## f. Completed Work

| Item | Details |
|------|---------|
| **Project structure** | `catalog/catalog-data/` — full structure with .git, scripts, infrastructure, products-collector |
| **Parent CI** | `.gitlab-ci.yml` — stages, includes, workflow rules (from loyalty parent) |
| **Products CI** | `products-collector/.gitlab-ci.yml` — terraform + deploy-tables + dataform ACTIVE, build/deploy COMMENTED |
| **Terraform infra** | GAR repo, GCS buckets (source + config), Secret Manager, BQ refined dataset, DTS, Dataform repo |
| **DTS setup** | `dts.tf` — S3→BQ transfer for `ms_product_all`, disabled=false, on-demand |
| **DTS path fix** | Changed to `s3://t1-analytics/refined/master_data/product/gcp_product_master/*` |
| **Schema JSON** | `schemas/ms_product_all.json` — 43 STRING columns matching BQ table |
| **Dataform repo** | `google_dataform_repository` created in GCP STG via terraform |
| **Dataform deploy** | STG deploy passing (compile + validate + invoke) after IAM grant |
| **IAM fix** | Granted `roles/iam.serviceAccountTokenCreator` to Dataform SA on products-collector SA |
| **Code structure** | `products-collector/src/` — full purchases-collector code copied, `configuration_adapter.py` path fixed |
| **Python checks** | uv sync, ruff, mypy, pytest (94 tests) — all passing |
| **Dataform code** | `definitions/public/products/ms_product_all.sqlx` + refined declaration + assertions |

---

## g. Pending Work

| Item | Priority | Details |
|------|----------|---------|
| **IAM Terraform** | HIGH | Grant `serviceAccountTokenCreator` to Dataform SA via terraform (currently manual) |
| **Dataform PROD** | HIGH | Deploy to prod (needs prod terraform + IAM) |
| **DTS schedule** | MEDIUM | Set `schedule = "every day 01:00"` when ready for automated sync |
| **Adapt Python code** | MEDIUM | Change purchases domain logic → products domain (models, transformers, schemas) |
| **BQ schemas** | MEDIUM | Replace purchases JSON schemas with actual products schemas |
| **Kafka streaming** | LOW | Uncomment build/deploy CI steps when Dataflow pipeline is ready |
| **BigLake catalog** | LOW | Uncomment `biglake-metastore.tf` when Iceberg write needed |
| **PubSub** | LOW | Uncomment `pubsub.tf` when event publishing needed |
| **Service accounts** | LOW | Currently managed externally, uncomment when needed |

---

## h. Memory Files Exported

| Filename | Description |
|----------|-------------|
| `MEMORY.md` | Master index — all memory entries across loyalty, sales, catalog |
| `catalog_products_knowledge_base.md` | Complete KB: structure, CI/CD, terraform, config, pipeline arch |
| `mistakes_and_rules.md` | Critical rules: verify before answer, no guessing, short action-first |
| `feedback_verify_before_answer.md` | Root cause patterns of repeated mistakes |
| `loyalty_knowledge_base.md` | Loyalty domain KB (reference for patterns) |
| `dofns_comparison.md` | DoFns comparison: members vs messaging patterns |
| `SESSION_SUMMARY.md` | This file |

---

## i. Key Rules

| Rule | Detail |
|------|--------|
| **No git commands** | ห้าม branch/add/commit/push — user ทำเอง |
| **Correct repo path** | `catalog/catalog-data/` (NOT `catalog/catalogs-data/`) |
| **Reference collector** | purchases-collector = read-only reference, ลอก pattern ได้ |
| **Validation after code changes** | uv sync → ruff → mypy → pytest → pre-commit |
| **Verify before answer** | อ่าน code/schema จริงก่อนตอบ ห้ามเดา |
| **Action before explanation** | สั้น กระชับ ลงมือทำ ไม่ต้อง lecture |
| **DTS path** | `s3://t1-analytics/refined/master_data/product/gcp_product_master/*` |
| **All columns STRING** | `ms_product_all` schema ทุก column เป็น STRING |

---

## j. Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Cannot find destination table ms_product_all in dataset refined` | DTS terraform tries to create transfer before table exists | Comment `dts.tf` → run terraform → create table → uncomment `dts.tf` → run terraform again. Or use `depends_on` |
| `Transfer is disabled` | DTS `disabled = true` in terraform | Change to `disabled = false` in `dts.tf` |
| Dataform 404: `products-dataform repository not found` | Terraform hasn't created dataform repo yet | Uncomment `dataform.tf` → run terraform first |
| Dataform `cannot actAs` permission denied | Dataform SA lacks `serviceAccountTokenCreator` on workload SA | `gcloud iam service-accounts add-iam-policy-binding` grant the role |
| GitLab deploy-stg blocked (shows play button) | `products-dataform:build` failed in build stage → blocks all deploy-stg jobs | Add `needs: []` to terraform job, or fix build failure first |
| Chicken-and-egg: terraform blocked by build | Dataform build fails (no repo) → blocks terraform (which creates repo) | Use `TRIGGER_EVENT=terraform-apply` dropdown to bypass, or add `needs: []` |
| `pre-commit` modifies other collector files | ruff format scope covers entire monorepo | `git checkout -- <other-collector>/` after pre-commit |

---

## k. Cross-Domain Dependencies

| Dependency | Detail |
|------------|--------|
| **purchases-collector (loyalty)** | Source template — code, CI/CD patterns, terraform structure all copied from here |
| **common-data library** | `common-data 0.0.23` — shared Beam transforms, BQ writers, Iceberg sink |
| **Shared CI templates** | `common.gitlab-ci.yml`, `dataform-template.gitlab-ci.yml` — shared across all collectors |
| **Shared scripts** | `deploy_dataform.sh`, `dataform_api.py`, `deploy_schemas.py` — shared in `scripts/` |
| **GCP IAM** | Dataform SA (`service-*@gcp-sa-dataform.iam.gserviceaccount.com`) needs cross-SA permissions |
| **S3 (AWS)** | DTS reads from `s3://t1-analytics/` — needs AWS credentials in Secret Manager |

---

## Terraform Resources Status

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
| `google_bigquery_data_transfer_config` | `dts.tf` | ACTIVE | S3→BQ, disabled=false |
| BigLake metastore | `biglake-metastore.tf` | COMMENTED | Waiting for Iceberg readiness |
| Service accounts | `service-accounts.tf` | COMMENTED | Externally managed |
| PubSub | `pubsub.tf` | COMMENTED | Not needed yet |

---

## CI/CD Jobs Status

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
| `scan-defect-dojo` | — | COMMENTED |
