# Partner Domain -- Knowledge Base

## Overview

- **1 active collector**: `master-collector` (CloudRun + Cloud Scheduler, batch)
- **2 deprecated empty dirs**: `branches-collector/`, `companies-collector/` (contain only empty `tests/` dir)
- **GCP project**: `the1-partner-data-{stg,prod}`
- **Dependency**: `common-data-python-cloudrun` tag `0.0.35`

## master-collector

### Architecture

```
Cloud Scheduler (CRON) --> POST /pipelines/{entity} --> CloudRun (FastAPI)
  --> REST API (Keycloak auth) --> Passthrough transform --> Iceberg (BLMS REST catalog)
```

### 4 Batch Pipelines (Daily, Asia/Bangkok)

| Pipeline       | Schedule  | API Endpoint                | Iceberg Table  |
|----------------|----------|-----------------------------|----------------|
| branches       | 01:00 AM | /partner/v1/branches        | source.branches |
| companies      | 01:30 AM | /partner/v1/companies       | source.companies |
| brands         | 02:00 AM | /partner/v1/brands          | source.brands |
| subscriptions  | 02:30 AM | /partner/v1/subscriptions   | source.subscriptions |

### Source: REST APIs

- Auth: **Keycloak** (realm `integration` prod / `integration-np` stg)
- Base URL: `https://private-gateway.the1.co.th` (prod) / `https://private-gateway-stg.the1.co.th` (stg)
- Pagination: `page_number` style, pageSize=200, extracts `data` field
- Secrets: GCP Secret Manager (`master-collector`)

### Sink: Iceberg (Passthrough)

- Catalog: **BLMS REST** (`https://biglake.googleapis.com/iceberg/v1/restcatalog`)
- Catalog name: `the1-partner-data-source-{env}` (= GCS bucket name)
- Warehouse: `gs://the1-partner-data-source-{env}`
- Namespace: `source`
- Schema strategies: `BranchesSchemaStrategy`, `CompaniesSchemaStrategy`, `BrandsSchemaStrategy`, `SubscriptionsSchemaStrategy` (raw JSON as string columns)
- PyIceberg 0.11.0

### Code Structure (Ports & Adapters)

- `src/main.py` -- Composition root: FastAPI app, builder dicts, pipeline wiring
- `src/adapters/input/http/http_adapter.py` -- HTTP routes (`POST /pipelines/{name}`)
- `src/adapters/output/gcs_iceberg/master_schema_strategies.py` -- 4 schema strategies
- `src/infrastructure/settings.py` -- YAML config loader
- `src/infrastructure/secret_manager.py` -- GCP Secret Manager adapter
- Config: `config/{base,stg,prod}.yml`

### Dataform (source -> refined -> public)

**Layers:**

1. **source** (Iceberg) -- raw JSON `data` column + `ingested_date` + `ingested_at`
2. **refined** (incremental merge) -- extracted/typed columns, deduped by unique key, row_hash change detection
3. **public** (views) -- clean views on refined tables

**Refined tables** (incremental, uniqueKey-based merge with row_hash):

- `branches` (uniqueKey: `branch_id`)
- `companies` (uniqueKey: `company_code`)
- `brands` (uniqueKey: `brand_code`)
- `subscriptions` (uniqueKey: `subscription_id`)
- `cg_location_master` (uniqueKey: `[company_code, branch_code]`, source = CSV external table)

**Refined layer -- incremental CDC pattern:**

- Uses **FARM_FINGERPRINT** change detection: computes `row_hash` over all data columns via `FARM_FINGERPRINT(TO_JSON_STRING(...))`, only merges rows where hash differs from existing record
- **ROW_NUMBER deduplication**: `PARTITION BY entity_id ORDER BY updated_date DESC, ingested_at DESC` -- ensures latest version wins when multiple records exist for same entity
- **`nullifyEmpty()` JS UDF**: custom JavaScript function for data cleaning -- converts empty strings (`""`), `undefined`, and `null` values to SQL `NULL` before insertion. Applied to string fields during JSON extraction.

**Public views:**

- `branches`, `companies`, `brands`, `subscriptions`, `cg_location_master` -- simple SELECT from refined
- `companies_branch_brand_cg_location` -- **composite table** (not view) joining companies + branches + brands + cg_location_master

**Extra: cglocationmaster CSV external table:**

- BQ external table (`source.cglocationmaster`) pointing to `gs://the1-partner-data-source-{env}/cglocationmaster/cg_location_master.csv`
- Autodetect schema, skip header row
- Defined in `infrastructure/master-collector/bigquery.tf`

**Dataform config:**

- `workflow_settings.yaml`: project=`the1-partner-data-stg`, dataset=`public`, dataformCoreVersion=3.0.35
- Var: `source_catalog` (env-substituted in CI)
- All definitions tagged `["master"]`

### Dataform CI/CD

- Uses shared templates from `.gitlab/ci/dataform-template.gitlab-ci.yml`
- Pipeline: `master-dataform:build` -> `master-dataform:deploy:stg` -> `master-dataform:deploy:prod`
- Deploy via REST API (`writeFile` to managed workspace), then compile + invoke
- Release config: `master-daily`

## Infrastructure (Terraform)

All in `infrastructure/master-collector/`:

| File | Resources |
|------|-----------|
| `cloud-run.tf` | CloudRun service (module `cloud-run`) + 4 Cloud Scheduler jobs |
| `bigquery.tf` | BiglakeConnection + `source`/`refined` datasets + CSV external table |
| `biglake-metastore.tf` | Iceberg catalog (`CATALOG_TYPE_GCS_BUCKET`, `CREDENTIAL_MODE_VENDED_CREDENTIALS`) + IAM |
| `bucket.tf` | GCS buckets (source + refined) + BLMS SA storage IAM |
| `artifact-registry.tf` | GAR repo (Docker) |
| `secret-manager.tf` | Secret Manager secret |
| `dataform.tf` | Dataform repo + release config + workflow config |
| `main.tf` | Backend (`gcs`), locals |
| `variable.tf` | Variables (domain, region, service_name, CloudRun config) |
| `terraform.tfvars` | `region=asia-southeast1`, `domain=partner-data`, `service_name=master-collector` |

Terraform modules sourced from: `git::https://gitlab.com/The1central/platform/the1-terraform-gcp.git//modules/{module}?ref=main`

CloudRun config: scale-to-zero (`min_instances=0`, `max_instances=5`), internal-only ingress, VPC egress, billing=requests, health checks on `/health`.

## CI/CD (.gitlab-ci.yml)

**Root** (`.gitlab-ci.yml`): stages build/deploy-stg/test-stg/deploy-prod/test-prod/rollback. Includes common templates + dataform template + master-collector CI.

**master-collector** (`master-collector/.gitlab-ci.yml`):

- `linter` -> `test` -> `create-image` (Kaniko, 4 destinations: stg+prod x tag+latest) -> `sonar-scan` + `scan-gitleaks` + `scan-image`
- `terraform:apply:stg` -> `deploy:stg` -> `terraform:apply:prod` -> `deploy:prod`
- `scan-defect-dojo` (aggregates gitleaks + trivy)
- Deploy = `gcloud run deploy` with image digest ref
- Prod deploy depends on stg deploy completion

## Key Dependencies

- Python 3.12, FastAPI, uvicorn, pydantic 2.x, PyYAML
- `common-data-python-cloudrun` @ tag 0.0.35
- PyIceberg 0.11.0 (gcsfs), pyarrow 18.0.0
- confluent-kafka (avro, schema-registry) -- listed in deps but not visibly used in master-collector
