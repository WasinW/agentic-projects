---
name: Loyalty Insights Knowledge Base
description: Complete KB for loyalty-insights (earn-analysis) project - dataform-focused mart, CI/CD, terraform patterns from all domains
type: project
---

# Loyalty Insights (earn-analysis) Knowledge Base

## 1. Project Location & Status
- **Path**: `/Users/wasin/Documents/ntt_project/the_one/realproject/loyalty-mart/loyalty-insights`
- **Git Remote**: `gitlab.com:The1central/The1/the1-insights/loyalty-insights.git`
- **Current State**: EMPTY — only default GitLab README.md (881f8b8 Initial commit, 2026-03-30)
- **Purpose**: Data mart project — Dataform views on top of collector refined tables
- **Focus**: Dataform definitions, dependency management, complex view logic

## 2. Reference Projects (ranked by relevance)

### 2.1 purchases-collector (PRIMARY reference)
**Path**: `/Users/wasin/Documents/ntt_project/the_one/realproject/loyalty/loyalty_paralel/loyalty-data/purchases-collector/`

**Key files to copy/reference:**
- `.gitlab-ci.yml` (720 lines) — full CI/CD with dataform stages
- `infrastructure/purchases-collector/dataform.tf` — dataform terraform
- `infrastructure/purchases-collector/main.tf` — provider + locals
- `infrastructure/purchases-collector/variables.tf` — input variables
- `infrastructure/purchases-collector/terraform.tfvars` — region, domain, service_name
- `dataform/workflow_settings.yaml` — defaultProject, defaultDataset, defaultLocation
- `dataform/definitions/` — public views, refined declarations, tests

**Terraform pattern:**
```hcl
terraform {
  required_providers {
    google = "~> 7.17.0"
    google-beta = "~> 7.17.0"
  }
  backend "gcs" {
    bucket = "devops-terraformstate-nonprod"
    prefix = "the1-loyalty-data/services/data-pipeline-purchases"
  }
}
# Dynamic project: the1-loyalty-data-${workspace}
```

**Dataform CI stages in purchases-collector:**
1. `purchases-dataform:unit-test` — npm-based unit tests
2. `purchases-dataform:build` — compile dataform
3. `purchases-dataform:deploy:stg` — deploy to STG workspace
4. `purchases-dataform:assertion:stg` — run assertions
5. `purchases-dataform:deploy:prod` — deploy to PROD workspace

### 2.2 Other Domain Insights/Dataform patterns

| Domain | Path | .sqlx count | Scheduled | Notes |
|--------|------|-------------|-----------|-------|
| Partner | partner/partner-data/master-collector/dataform/ | 33 | Daily 03:00 BKK | Most extensive |
| Gamification | gamification/gamification-data/master-collector/dataform/ | 12 | Daily 01:00 BKK | missions + ballots tags |
| Messaging | message/messaging-data/master-collector/dataform/ | 6 | templates + communications | |
| Coupons | loyalty_paralel/loyalty-data/coupons-collector/dataform/ | 5 | No | Loyalty domain |
| Catalog | catalog/catalog-data/products-collector/dataform/ | 4 | No | Minimal |

### 2.3 Sales-data (has scheduled release+workflow in terraform)
**Path**: `/Users/wasin/Documents/ntt_project/the_one/realproject/sale/sales-data/`
- Has `google_dataform_repository_release_config` (daily 02:00 BKK)
- Has `google_dataform_repository_workflow_config` (tag-scoped execution)

## 3. CI/CD Architecture

### Root CI Pattern (domain-level)
All domains use root `.gitlab-ci.yml` that:
1. Includes `common-data` shared pipeline: `project: "The1central/The1/the1-data/common-data"` → `pipeline/common.gitlab-ci.yml`
2. Includes `dataform-template.gitlab-ci.yml` (shared template)
3. Includes per-collector CI files

**Root CI Variables pattern:**
```yaml
variables:
  TRIGGER_EVENT:
    description: "Select pipeline type"
    options: ["manual-deploy", "terraform-apply", "dataform-deploy"]
  SERVICE_NAME:
    description: "Select service"
    options: ["earn-analysis"]  # or multiple services
```

**Stages**: build, deploy-stg, test-stg, deploy-prod, test-prod, rollback

### Dataform Template
**Reference**: `/gamification/gamification-data/.gitlab/ci/dataform-template.gitlab-ci.yml` (166 lines)

Templates provided:
- `.dataform-build-template` — validate/compile
- `.dataform-deploy-stg-template` — deploy STG
- `.dataform-deploy-prod-template` — deploy PROD
- `.dataform-api-setup` — install git, resolve Python
- `.dataform-resolve-vars` — parse YAML workflow_settings
- `.dataform-prod-auth` — SA authentication

**Tag pipeline convention**: `{service-name}-dataform/vX.Y.Z`

### Deployment Model: Workspace (modern, not pull)
CI pushes files via REST API → Dataform compiles from workspace
- `scripts/deploy_dataform.sh` — 5-step orchestration (clean, push, commit, compile, invoke, poll)
- `scripts/dataform_api.py` — REST API wrapper

## 4. Terraform for Dataform

### Minimal (earn-analysis needs only this initially)
```hcl
resource "google_dataform_repository" "earn_analysis_dataform" {
  provider = google-beta
  project  = local.project_id
  name     = "earn-analysis-dataform"
  region   = var.region

  workspace_compilation_overrides {
    default_database = local.project_id
  }
}
```

### With Scheduling (optional, later)
```hcl
resource "google_dataform_repository_release_config" "earn_analysis_daily" {
  provider   = google-beta
  project    = local.project_id
  region     = var.region
  repository = google_dataform_repository.earn_analysis_dataform.name
  name       = "earn-analysis-daily"

  git_commitish = "main"
  cron_schedule = "0 2 * * *"
  time_zone     = "Asia/Bangkok"
}

resource "google_dataform_repository_workflow_config" "earn_analysis_daily" {
  provider       = google-beta
  project        = local.project_id
  region         = var.region
  repository     = google_dataform_repository.earn_analysis_dataform.name
  name           = "earn-analysis-daily"
  release_config = google_dataform_repository_release_config.earn_analysis_daily.id

  invocation_config {
    included_tags             = ["earn-analysis"]
    transitive_dependencies_included = true
  }
  cron_schedule = "0 2 * * *"
  time_zone     = "Asia/Bangkok"
}
```

## 5. Dataform Structure Pattern

### Three-Layer Architecture
```
definitions/
├── refined/          # Layer 1: Declarations (pointers to existing BQ tables from collectors)
│   └── {entity}/
│       └── {table}.sqlx    # type: "declaration", schema: "refined"
├── public/           # Layer 2: Semantic Views (business-facing)
│   └── {entity}/
│       └── {table}.sqlx    # type: "view", schema: "public"
└── tests/            # Layer 3: Assertions (data quality)
    └── {entity}/
        └── {table}_test.sqlx  # type: "assertion"
```

### workflow_settings.yaml
```yaml
defaultProject: "the1-loyalty-data-stg"
defaultDataset: "public"
defaultLocation: "asia-southeast1"
dataformCoreVersion: 3.0.35
```

### Declaration Example (refined)
```sqlx
config {
  type: "declaration",
  schema: "refined",
  name: "purchases_receipt",
  description: "Refined purchases receipt data from collector pipeline"
}
```

### View Example (public)
```sqlx
config {
  type: "view",
  schema: "public",
  name: "purchases_receipt",
  description: "Public view of purchases receipt",
  tags: ["purchases"]
}

SELECT
  purchase_id,
  member_id,
  partner_code,
  -- column selection (business decision)
FROM ${ref({schema: "refined", name: "purchases_receipt"})}
```

### Assertion Example (tests)
```sqlx
config {
  type: "assertion",
  schema: "public",
  description: "Assert purchases_receipt has no NULL purchase_id",
  tags: ["purchases", "assertion"]
}

SELECT purchase_id
FROM ${ref({schema: "public", name: "purchases_receipt"})}
WHERE purchase_id IS NULL
LIMIT 1
```

## 6. Source Tables Available (from collectors)

### Loyalty Refined Tables (source for earn-analysis views)
From members-collector:
- `refined.member_tier` — member tier info (CDC enabled, PK: memberTierId)
- `refined.member_tier_maintenance` — tier maintenance records (CDC, PK: tierMaintenanceId)
- `refined.tier_events_upgraded` — upgrade events
- `refined.tier_events_downgraded` — downgrade events

From tiers-collector:
- `refined.tiers` — master tier data

From members-tiers-history-collector:
- `refined.members_tiers_history` — historical tier data

From purchases-collector:
- `refined.purchases_receipt` — purchase headers (partitioned by transaction_datetime DAY)
- `refined.purchases_detail` — purchase line items
- `refined.purchases_payment` — payment details

From coupons-collector:
- `refined.coupons` — coupon data
- `refined.rewards` — reward data

## 7. Directory Structure for loyalty-insights (proposed)

```
loyalty-insights/
├── .gitlab-ci.yml                    # Root CI (include common + dataform template)
├── earn-analysis/
│   ├── .gitlab-ci.yml                # Per-service CI (terraform + dataform stages)
│   ├── dataform/
│   │   ├── workflow_settings.yaml
│   │   ├── package.json              # (if needed for dataform CLI)
│   │   └── definitions/
│   │       ├── refined/              # Declarations for source tables
│   │       ├── public/               # Views (earn analysis logic)
│   │       └── tests/                # Assertions
│   └── infrastructure/
│       └── earn-analysis/
│           ├── main.tf
│           ├── variables.tf
│           ├── terraform.tfvars
│           └── dataform.tf           # Only dataform TF (start minimal)
├── .gitlab/
│   └── ci/
│       └── dataform-template.gitlab-ci.yml  # Shared template (copy from gamification)
└── README.md
```

## 8. Key Technical Details

### GCP Project Naming
- STG: `the1-loyalty-data-stg` (or `the1-loyalty-insights-stg` — TBD)
- PROD: `the1-loyalty-data-prod`
- Terraform state bucket: `devops-terraformstate-nonprod`

### Service Account Pattern
- `t1-earn-analysis@${project_id}.iam.gserviceaccount.com`

### Runner Tags
- nonprod: `nonprod-docker-cicd-x86`
- prod: `prod-docker-cicd-x86`

### Dataform API Flow (CI → Dataform)
1. Clean workspace
2. Push files (writeFile REST API)
3. Commit
4. Compile (with defaultDatabase override)
5. Invoke workflow
6. Poll until complete

### Critical: Views vs Tables
- **Views only** (no storage cost, always fresh)
- ${ref()} resolves dependencies automatically
- Environment isolation via `defaultDatabase` override (STG/PROD)

## 9. Comparison: loyalty-insights vs collector projects

| Aspect | Collectors (purchases, members, etc.) | loyalty-insights (earn-analysis) |
|--------|---------------------------------------|----------------------------------|
| **Purpose** | Ingest data from Kafka/APIs | Create business views from refined data |
| **Pipeline** | Apache Beam / Dataflow | Dataform only |
| **Code** | Python (src/, tests/) | SQLX definitions only |
| **Infra** | Dataflow, GCS, Pub/Sub, Iceberg, BQ | Dataform repository only |
| **CI/CD** | Build image, deploy Dataflow, deploy schemas | Terraform + Dataform deploy |
| **Docker** | Yes (Flex Template) | No |
| **Testing** | pytest + mypy + ruff | Dataform assertions |

## 10. Implementation Order (from user request)

1. ✅ Copy root `.gitlab-ci.yml` from loyalty → adapt for earn-analysis
2. ✅ Copy per-service `.gitlab-ci.yml` from purchases-collector → comment non-terraform steps
3. ✅ Copy terraform from purchases-collector → keep only dataform.tf
4. ✅ Copy code structure → adapt for dataform-only project
5. 🔜 Create dataform definitions (views, declarations, assertions)
6. 🔜 Complex dependency logic for earn-analysis views
