# Loyalty-Mart — Pending Work

## From Session Summary

| Item | Priority | Notes |
|------|----------|-------|
| **CI/CD variables** | HIGH | Set `T1_PIPELINE_NP_SA` + `T1_PIPELINE_SA` in GitLab project settings (ask DevOps). These are base64 File-type CI/CD variables required by common-data pipeline. |
| **Terraform apply** | HIGH | Run pipeline with `TRIGGER_EVENT=terraform-apply` + `SERVICE_NAME=earn-analysis` to create Dataform repository in GCP |
| **Dataform definitions** | NEXT | Create refined declarations, public views, assertions -- user wants to discuss details before creating views |
| **Earn-analysis view logic** | NEXT | Complex joins (purchases x member_tier x tiers), aggregations, business logic for earn-analysis |
| **Uncomment dataform CI** | LATER | Enable dataform build/deploy stages in `earn-analysis/.gitlab-ci.yml` when definitions are ready |
| **Dataform scheduling** | LATER | Optional: add `release_config` + `workflow_config` in `dataform.tf` for automated execution (cron daily) |

## Common Errors to Watch For

| Error | Root Cause | Fix |
|-------|-----------|-----|
| `base64: '': No such file or directory` | CI/CD variables `T1_PIPELINE_NP_SA`/`T1_PIPELINE_SA` not set in GitLab | Add File-type CI/CD variables in project Settings > CI/CD > Variables |
| Pipeline empty / "cannot be run" | No jobs matching current trigger | `earn-analysis:validate` job runs on every push to prevent this |
| Terraform jobs don't run on push | Only triggered by `changes: infrastructure/earn-analysis/**/*` | Use manual trigger: `TRIGGER_EVENT=terraform-apply` |
| Wrong infrastructure path | Was `earn-analysis/infrastructure/earn-analysis` | Moved to `infrastructure/earn-analysis` (repo root) -- matches purchases-collector pattern |
| Missing `LBL_SELECT_OPTION` | Common rules reference this variable | Added `LBL_SELECT_OPTION: "Select Option"` in root CI variables |
| Nested `!reference` in custom rules | GitLab CI doesn't resolve nested references reliably | Use common rules directly (`!reference [.rules_infra_changes, rules]`) |

## Cross-Domain Dependencies

| Dependency | Type | Details |
|-----------|------|---------|
| **common-data** | CI/CD templates | Provides `.common-gcp-prepare`, `.common-terraform-plan`, `.common-terraform-apply`, `.rules_infra_changes`, `.rules_infra_manual_trigger`, `.uv_base` |
| **loyalty-data collectors** | Data source | members-collector, tiers-collector, m-t-h-collector, purchases-collector, coupons-collector write to `refined.*` BQ tables that earn-analysis reads |
| **GCP project** | Infrastructure | Uses `the1-loyalty-data-stg`/`prod` -- same project as loyalty collectors |
| **Terraform state** | Shared bucket | `devops-terraformstate-nonprod` with prefix `the1-loyalty-data/services/earn-analysis` |
| **Service account** | IAM | `t1-earn-analysis@the1-loyalty-data-{env}.iam.gserviceaccount.com` needs BigQuery dataViewer on refined, dataEditor on public |
