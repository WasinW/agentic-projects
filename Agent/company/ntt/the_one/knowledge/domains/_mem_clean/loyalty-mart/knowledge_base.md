# Loyalty-Mart (earn-analysis) — Knowledge Base

## 1. Project Location & Status
- **Path**: `/Users/wasin/Documents/ntt_project/the_one/realproject/loyalty-mart/loyalty-insights`
- **Git Remote**: `gitlab.com:The1central/The1/the1-insights/loyalty-insights.git`
- **GitLab Group**: `The1central/The1/the1-insights/` (NOT `the1-data/`)
- **Current State**: Scaffold DONE -- CI pipeline passed, terraform ready, dataform definitions pending
- **Purpose**: Data mart project -- Dataform views on top of collector refined tables
- **Focus**: earn-analysis (complex joins, aggregations, no Python code)

## 2. Architecture

```
COLLECTORS (upstream -- separate repos/pipelines)
  Kafka/API -> members-collector  -> refined.member_tier
                                  -> refined.member_tier_maintenance
                                  -> refined.tier_events_*
  Scheduler -> tiers-collector    -> refined.tiers
  Scheduler -> m-t-h-collector    -> refined.members_tiers_history
  Kafka     -> purchases-collector-> refined.purchases_*
               coupons-collector  -> refined.coupons/rewards
                     |
                     | BQ refined tables (source)
                     v
LOYALTY-INSIGHTS (this project)
  Dataform definitions:
    refined/ declarations -> public/ views -> tests/ assertions
  Output: BQ public dataset (views -- no storage cost)
  Focus: earn-analysis (complex joins, aggregations)
```

## 3. Reference Projects (ranked by relevance)

### 3.1 purchases-collector (PRIMARY reference)
**Key files copied/referenced:**
- `.gitlab-ci.yml` (720 lines) -- full CI/CD with dataform stages
- `infrastructure/purchases-collector/dataform.tf` -- dataform terraform
- `infrastructure/purchases-collector/main.tf` -- provider + locals
- `dataform/workflow_settings.yaml` -- defaultProject, defaultDataset, defaultLocation
- `dataform/definitions/` -- public views, refined declarations, tests

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

### 3.2 Other Domain Dataform patterns

| Domain | Path | .sqlx count | Scheduled | Notes |
|--------|------|-------------|-----------|-------|
| Partner | partner/partner-data/master-collector/dataform/ | 33 | Daily 03:00 BKK | Most extensive |
| Gamification | gamification/gamification-data/master-collector/dataform/ | 12 | Daily 01:00 BKK | missions + ballots tags |
| Messaging | message/messaging-data/master-collector/dataform/ | 6 | templates + communications | |
| Coupons | loyalty_paralel/loyalty-data/coupons-collector/dataform/ | 5 | No | Loyalty domain |
| Catalog | catalog/catalog-data/products-collector/dataform/ | 4 | No | Minimal |

### 3.3 Sales-data (has scheduled release+workflow in terraform)
- Has `google_dataform_repository_release_config` (daily 02:00 BKK)
- Has `google_dataform_repository_workflow_config` (tag-scoped execution)

## 4. CI/CD Architecture

### Root CI Pattern
Root `.gitlab-ci.yml`:
1. Includes `common-data` shared pipeline: `project: "The1central/The1/the1-data/common-data"` -> `pipeline/common.gitlab-ci.yml`
2. Includes `dataform-template.gitlab-ci.yml` (shared template)
3. Includes per-service CI files (`earn-analysis/.gitlab-ci.yml`)

**Root CI Variables:**
```yaml
variables:
  TRIGGER_EVENT:
    description: "Select pipeline type"
    options: ["manual-deploy", "terraform-apply", "dataform-deploy"]
  SERVICE_NAME:
    description: "Select service"
    options: ["earn-analysis"]
  LBL_SELECT_OPTION: "Select Option"  # REQUIRED by common rules
```

**Stages**: build, deploy-stg, test-stg, deploy-prod, test-prod, rollback

### Dataform Template
Templates provided:
- `.dataform-build-template` -- validate/compile
- `.dataform-deploy-stg-template` -- deploy STG
- `.dataform-deploy-prod-template` -- deploy PROD
- `.dataform-api-setup` -- install git, resolve Python
- `.dataform-resolve-vars` -- parse YAML workflow_settings
- `.dataform-prod-auth` -- SA authentication

**Tag pipeline convention**: `{service-name}-dataform/vX.Y.Z`

### Deployment Model: Workspace (modern, not pull)
CI pushes files via REST API -> Dataform compiles from workspace
- `scripts/deploy_dataform.sh` -- 5-step orchestration (clean, push, commit, compile, invoke, poll)
- `scripts/dataform_api.py` -- REST API wrapper

## 5. Terraform for Dataform

### Minimal (current)
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

## 6. Dataform Structure Pattern

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
  partner_code
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

## 7. Source Tables Available (from collectors)

### Loyalty Refined Tables (source for earn-analysis views)
From members-collector:
- `refined.member_tier` -- member tier info (CDC enabled, PK: memberTierId)
- `refined.member_tier_maintenance` -- tier maintenance records (CDC, PK: tierMaintenanceId)
- `refined.tier_events_upgraded` -- upgrade events
- `refined.tier_events_downgraded` -- downgrade events

From tiers-collector:
- `refined.tiers` -- master tier data

From members-tiers-history-collector:
- `refined.members_tiers_history` -- historical tier data

From purchases-collector:
- `refined.purchases_receipt` -- purchase headers (partitioned by transaction_datetime DAY)
- `refined.purchases_detail` -- purchase line items
- `refined.purchases_payment` -- payment details

From coupons-collector:
- `refined.coupons` -- coupon data
- `refined.rewards` -- reward data

## 8. GCP & Infrastructure Details

| Key | Value |
|-----|-------|
| GCP Project STG | `the1-loyalty-data-stg` |
| GCP Project PROD | `the1-loyalty-data-prod` |
| Region | `asia-southeast1` |
| Terraform state bucket | `devops-terraformstate-nonprod` |
| Terraform state prefix | `the1-loyalty-data/services/earn-analysis` |
| SA pattern | `t1-earn-analysis@the1-loyalty-data-{env}.iam.gserviceaccount.com` |
| Runner tags (nonprod) | `nonprod-docker-cicd-x86` |
| Runner tags (prod) | `prod-docker-cicd-x86` |

## 9. Current File Structure

```
loyalty-insights/
├── .gitlab-ci.yml                          # Root CI (common-data include + dataform template)
├── .gitlab/ci/
│   └── dataform-template.gitlab-ci.yml     # Shared dataform deploy templates
├── earn-analysis/
│   ├── .gitlab-ci.yml                      # Per-service CI (terraform active, dataform commented)
│   └── dataform/
│       ├── workflow_settings.yaml          # Dataform config
│       └── definitions/                    # Empty -- views TBD
├── infrastructure/
│   └── earn-analysis/
│       ├── main.tf                         # Provider, backend, locals
│       ├── variables.tf                    # region, domain, service_name
│       ├── terraform.tfvars                # asia-southeast1, loyalty-data, earn-analysis
│       └── dataform.tf                     # Dataform repository only
├── scripts/
│   ├── deploy_dataform.sh                  # 5-step deploy cycle
│   └── dataform_api.py                     # Dataform REST API wrapper
└── README.md
```

## 10. Key Technical Details

### Dataform API Flow (CI -> Dataform)
1. Clean workspace
2. Push files (writeFile REST API)
3. Commit
4. Compile (with defaultDatabase override)
5. Invoke workflow
6. Poll until complete

### Critical: Views vs Tables
- **Views only** (no storage cost, always fresh)
- `${ref()}` resolves dependencies automatically
- Environment isolation via `defaultDatabase` override (STG/PROD)
