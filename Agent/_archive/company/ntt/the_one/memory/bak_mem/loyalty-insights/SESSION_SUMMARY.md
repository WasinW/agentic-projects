# Session Summary: loyalty-insights (earn-analysis)

**Domain**: loyalty-insights  
**Session Date**: 2026-04-01 ~ 2026-04-05  
**Export Date**: 2026-04-05  

---

## a. Session Owner & Role

| Field | Value |
|-------|-------|
| **Name** | Wasin Wangsombut |
| **Role** | Data Engineer (Consultant) at NTT DATA → Client: The 1 Central Group |
| **Experience** | 8+ years (Telecom, Banking, Retail) |
| **Language** | Thai (native), English |
| **Working Style** | สั้น กระชับ ลงมือทำ — ไม่ต้องอธิบายยาว, อ่าน code จริงก่อนพูด, verify ก่อนตอบ |
| **Key Skills** | Apache Beam/Dataflow, Iceberg+BLMS, BigQuery CDC, Kafka, Terraform, GitLab CI/CD, Python 3.12 |

---

## b. Project Overview

| Field | Value |
|-------|-------|
| **Project** | loyalty-insights (earn-analysis) |
| **Purpose** | Data mart — Dataform views on top of collector refined tables |
| **Repo** | `gitlab.com:The1central/The1/the1-insights/loyalty-insights.git` |
| **GitLab Group** | `The1central/The1/the1-insights/` (NOT `the1-data/`) |
| **Local Path** | `/Users/wasin/Documents/ntt_project/the_one/realproject/loyalty-mart/loyalty-insights` |
| **GCP Project** | `the1-loyalty-data-stg` / `the1-loyalty-data-prod` |
| **Region** | `asia-southeast1` |
| **Tech Stack** | Dataform (SQLX), Terraform, GitLab CI/CD |
| **No Python code** | This is a dataform-only project (no Beam/Dataflow) |

---

## c. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  COLLECTORS (upstream — separate repos/pipelines)           │
│                                                             │
│  Kafka/API → members-collector  → refined.member_tier       │
│                                 → refined.member_tier_maint │
│                                 → refined.tier_events_*     │
│  Scheduler → tiers-collector    → refined.tiers             │
│  Scheduler → m-t-h-collector    → refined.members_tiers_hist│
│  Kafka     → purchases-collector→ refined.purchases_*       │
│             coupons-collector   → refined.coupons/rewards   │
└─────────────┬───────────────────────────────────────────────┘
              │ BQ refined tables (source)
              ▼
┌─────────────────────────────────────────────────────────────┐
│  LOYALTY-INSIGHTS (this project)                            │
│                                                             │
│  Dataform definitions:                                      │
│    refined/ declarations → public/ views → tests/ assertions│
│                                                             │
│  Output: BQ public dataset (views — no storage cost)        │
│  Focus: earn-analysis (complex joins, aggregations)         │
└─────────────────────────────────────────────────────────────┘
```

---

## d. Components Managed

| Component | Type | Source | Sink | Status |
|-----------|------|--------|------|--------|
| **earn-analysis** | Dataform views | BQ refined.* (from collectors) | BQ public.* (views) | Scaffold DONE, views pending |
| **infrastructure/earn-analysis** | Terraform | N/A | GCP Dataform repository | DONE (dataform.tf only) |
| **CI/CD** | GitLab CI | common-data include | terraform stg+prod | Pipeline PASSED |

---

## e. Key Technical Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| **CI pattern** | Include `common-data` pipeline | loyalty-insights is in `the1-insights` group but uses same `common-data` templates as `the1-data` projects |
| **Infrastructure** | `infrastructure/` at repo root (NOT inside `earn-analysis/`) | Matches purchases-collector pattern |
| **Terraform** | Only `dataform.tf` initially | Minimal setup — other TF (buckets, GAR, etc.) not needed for dataform-only project |
| **Dataform definitions** | Empty for now | User wants to discuss details before creating views |
| **Rule overrides** | Override `.rules_app_changes`, `.rules_infra_changes`, `.rules_infra_manual_trigger` in dataform-template | Required for correct job trigger behavior with common-data include |
| **Validate job** | `earn-analysis:validate` (echo) on every push | Prevents empty pipeline on push (only terraform jobs exist, triggered by infra changes only) |
| **Credentials** | `T1_PIPELINE_NP_SA` / `T1_PIPELINE_SA` (base64 File vars) | Standard common-data pattern — needs CI/CD variables set in GitLab project settings |
| **Scripts** | Copied from gamification (latest version) | `deploy_dataform.sh` + `dataform_api.py` — 5-step deploy cycle with REST API |

---

## f. Completed Work

1. **Root `.gitlab-ci.yml`** — include common-data + dataform-template + earn-analysis CI, workflow rules, LBL_SELECT_OPTION
2. **`.gitlab/ci/dataform-template.gitlab-ci.yml`** — full template with rule overrides, dataform build/deploy/prod templates (copied from sales-data pattern)
3. **`earn-analysis/.gitlab-ci.yml`** — terraform stg+prod active, validate job, dataform stages commented
4. **`infrastructure/earn-analysis/`** — main.tf, variables.tf, terraform.tfvars, dataform.tf (Dataform repository only)
5. **`scripts/`** — deploy_dataform.sh + dataform_api.py (copied from gamification)
6. **`earn-analysis/dataform/`** — workflow_settings.yaml + empty definitions/
7. **Knowledge base** — full exploration of all domains (purchases, gamification, catalog, messaging, partner, sales) CI/CD and dataform patterns
8. **Pipeline validation** — pipeline #2419638964 passed on GitLab

---

## g. Pending Work

| Item | Priority | Notes |
|------|----------|-------|
| **CI/CD variables** | HIGH | Set `T1_PIPELINE_NP_SA` + `T1_PIPELINE_SA` in GitLab project settings (ask DevOps) |
| **Terraform apply** | HIGH | Run pipeline with `terraform-apply` + `earn-analysis` to create Dataform repository |
| **Dataform definitions** | NEXT | Create refined declarations, public views, assertions — user wants to discuss details first |
| **Earn-analysis view logic** | NEXT | Complex joins (purchases × member_tier × tiers), aggregations, business logic |
| **Uncomment dataform CI** | LATER | Enable dataform build/deploy stages when definitions are ready |
| **Dataform scheduling** | LATER | Optional: add release_config + workflow_config for automated execution |

---

## h. Memory Files Exported

| Filename | Description |
|----------|-------------|
| `MEMORY.md` | Memory index from this session's auto-memory |
| `user_profile.md` | Wasin's role, skills, experience at NTT DATA / The1 |
| `loyalty_insights_knowledge_base.md` | Complete KB: all reference projects, CI/CD patterns, terraform, dataform structure, source tables |
| `SESSION_SUMMARY.md` | This file — full session context export |

---

## i. Key Rules

### MUST FOLLOW
- **No git commands** (no branch, add, commit, push) — user manages git manually
- **infrastructure/ at repo root** — NOT inside earn-analysis/ (matches purchases-collector pattern)
- **Read code before answering** — verify against real files, never guess
- **Run after code changes**: `uv sync`, `ruff`, `mypy`, `pytest`, `pre-commit` (when applicable — this project has no Python code yet)

### CI/CD Rules
- **common-data include works** — `The1central/The1/the1-data/common-data` accessible from `the1-insights` group
- **Pipeline needs at least 1 matching job** — `earn-analysis:validate` ensures push pipelines aren't empty
- **Terraform trigger**: Run pipeline > `TRIGGER_EVENT=terraform-apply` > `SERVICE_NAME=earn-analysis`
- **`LBL_SELECT_OPTION`** variable is REQUIRED — common rules use it for matching

### Dataform Rules
- **Views only** (no materialized tables) — no storage cost
- **Three-layer**: refined declarations → public views → assertions
- **`${ref()}` for dependencies** — auto-resolves between environments
- **`defaultDatabase` override** — STG/PROD isolation via compilation config

---

## j. Common Errors & Fixes

| Error | Root Cause | Fix |
|-------|-----------|-----|
| `base64: '': No such file or directory` | CI/CD variables `T1_PIPELINE_NP_SA`/`T1_PIPELINE_SA` not set in GitLab | Add File-type CI/CD variables in project Settings > CI/CD > Variables |
| Pipeline empty / "cannot be run" | No jobs matching current trigger | Added `earn-analysis:validate` job that runs on every push |
| Terraform jobs don't run on push | Only triggered by `changes: infrastructure/earn-analysis/**/*` | Use manual trigger: `TRIGGER_EVENT=terraform-apply` |
| Wrong infrastructure path | Was `earn-analysis/infrastructure/earn-analysis` | Moved to `infrastructure/earn-analysis` (repo root) |
| Missing `LBL_SELECT_OPTION` | Common rules reference this variable | Added `LBL_SELECT_OPTION: "Select Option"` in root CI variables |
| Nested `!reference` in custom rules | GitLab CI doesn't resolve nested references reliably | Use common rules directly (`!reference [.rules_infra_changes, rules]`) |

---

## k. Cross-Domain Dependencies

| Dependency | Type | Details |
|-----------|------|---------|
| **common-data** | CI/CD templates | `pipeline/common.gitlab-ci.yml` — provides `.common-gcp-prepare`, `.common-terraform-plan`, `.common-terraform-apply`, `.rules_infra_changes`, `.rules_infra_manual_trigger`, `.uv_base` |
| **loyalty-data collectors** | Data source | members-collector, tiers-collector, m-t-h-collector, purchases-collector, coupons-collector write to `refined.*` BQ tables that earn-analysis reads |
| **GCP project** | Infrastructure | Uses `the1-loyalty-data-stg`/`prod` — same project as loyalty collectors |
| **Terraform state** | Shared bucket | `devops-terraformstate-nonprod` with prefix `the1-loyalty-data/services/earn-analysis` |
| **Service account** | IAM | `t1-earn-analysis@the1-loyalty-data-{env}.iam.gserviceaccount.com` needs BigQuery dataViewer on refined, dataEditor on public |

---

## Current File Structure

```
loyalty-insights/
├── .gitlab-ci.yml                          # Root CI (common-data include + dataform template)
├── .gitlab/ci/
│   └── dataform-template.gitlab-ci.yml     # Shared dataform deploy templates
├── earn-analysis/
│   ├── .gitlab-ci.yml                      # Per-service CI (terraform active, dataform commented)
│   └── dataform/
│       ├── workflow_settings.yaml          # Dataform config
│       └── definitions/                    # Empty — views TBD
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
