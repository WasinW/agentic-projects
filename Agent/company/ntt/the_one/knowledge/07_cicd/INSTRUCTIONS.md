# CI/CD Instructions

> AI: Read this file when modifying `.gitlab-ci.yml`, deploy scripts, Terraform, or deployment workflows.

## Quick Reference

```
GitLab CI Pipeline Flow:
  linter → test → create-image (Kaniko) → sonar/gitleaks/trivy
                                       ↓
                              terraform:apply:stg → deploy-tables:stg → deploy:stg
                                       ↓
                              terraform:apply:prod → deploy-tables:prod → deploy:prod
```

---

## 1. Pipeline Stages

```yaml
stages:
  - build        # lint, test, create-image, security scans
  - deploy-stg   # terraform + BQ tables + Dataflow (STG)
  - test-stg     # (placeholder for smoke tests)
  - deploy-prod  # terraform + BQ tables + Dataflow (PROD)
  - test-prod    # (placeholder)
  - rollback     # (placeholder)
```

## 2. Build Stage — What Each Job Does

### linter
```yaml
image: ghcr.io/astral-sh/uv:python3.12-bookworm-slim
script:
  - cd $SVC_NAME
  - uv sync
  - uv run ruff check .
  - uv run ruff format --check .
  - uv run mypy .
```

### test
```yaml
script:
  - cd $SVC_NAME
  - uv sync
  - uv run pytest
needs: [<collector>:linter]
```

### create-image (Kaniko)

Builds Docker image and pushes to **4 destinations** (STG + PROD, each with tag + latest):

```yaml
image: gcr.io/kaniko-project/executor:v1.9.0-debug
tags: [prod-docker-cicd-x86]
script:
  - /kaniko/executor \
    --context "$CI_PROJECT_DIR/$SVC_NAME" \
    --dockerfile "$CI_PROJECT_DIR/$SVC_NAME/Dockerfile" \
    --destination "$GAR_BASE/$PROJECT-prod/$GAR_REPO/$IMAGE:$ARCH-$TAG" \
    --destination "$GAR_BASE/$PROJECT-prod/$GAR_REPO/$IMAGE:latest" \
    --destination "$GAR_BASE/$PROJECT-stg/$GAR_REPO/$IMAGE:$ARCH-$TAG" \
    --destination "$GAR_BASE/$PROJECT-stg/$GAR_REPO/$IMAGE:latest" \
    --image-name-tag-with-digest-file /workspace/image-digest-ref.txt
```

**Key**: Single build → multi-destination. Image digest saved as CI artifact for deploy jobs.

## 3. Deployment — 3-Step Script Chain

Every deploy job runs these 3 scripts in order:

```
prepare_dataflow_config.sh → prepare_dataflow_spec.sh → deploy_dataflow.sh
```

### Step 1: prepare_dataflow_config.sh
Merges `base.yaml` + `{env}.yaml` → base64 encoded string.

```bash
DATAFLOW_CONFIG=$(./scripts/prepare_dataflow_config.sh \
  --base "$SVC_NAME/config/base.yaml" \
  --env "$SVC_NAME/config/$ENV.yaml")
```

Uses `yq -s '.[0] * .[1]'` for deep merge.

### Step 2: prepare_dataflow_spec.sh
Renders `container_spec.json` template with actual image digest → uploads to GCS.

```bash
./scripts/prepare_dataflow_spec.sh \
  --image-file "image-digest-ref-${ENV}.txt" \
  --template-path "$INFRA/templates/container_spec.json" \
  --gcs-destination "$SPEC_GCS_PATH"
```

### Step 3: deploy_dataflow.sh
Launches Dataflow Flex Template with smart job management.

```bash
./scripts/deploy_dataflow.sh \
  --project-id "$PROJECT-$ENV" \
  --region "asia-southeast1" \
  --job-name "$DATAFLOW_JOB_NAME" \
  --template-path "$SPEC_GCS_PATH" \
  --service-account "$SA@$PROJECT.iam.gserviceaccount.com" \
  --network "projects/the1-network-$ENV/global/networks/the1-vpc-net-share-$ENV" \
  --subnetwork ".../subnetworks/the1-subnet-dataflow-$ENV" \
  --staging-location "gs://$BUCKET/dataflow/staging" \
  --temp-location "gs://$BUCKET/dataflow/temp" \
  --max-workers 1 \
  --pipeline-opts "$PIPELINE_OPTS"
```

**Smart logic**: Checks for existing running job → tries update → falls back to drain → fresh deploy.

## 4. Streaming vs Batch Deployment

### Streaming (members-collector, purchases-collector)
1. Find running job
2. Drain existing job (10 min timeout) → cancel if drain fails
3. Launch new Flex Template
4. New job resumes from last Kafka offset

### Batch (tiers-collector, members-tiers-history)
1. Launch Flex Template (Cloud Scheduler triggers at 1 AM BKK)
2. Job self-terminates on completion
3. No drain needed

## 5. deploy.py — BQ Table Management

```bash
# Runs in deploy-tables job
cd infrastructure/<collector>/schemas
python3 deploy.py "$PROJECT-$ENV" "$ENV"
```

**What it does**:
- Reads JSON schemas from `schemas/refined_*.json`
- `CREATE TABLE IF NOT EXISTS` for BQ native tables
- Smart change detection: skip if no changes, `ALTER` for additive, migrate for breaking
- Uses `register_table` (NOT `create_table`) for Iceberg — preserves field IDs + partition spec
- Skips empty JSON files (`if not content: continue`)

## 6. Terraform

```yaml
# Uses shared extends from common-data
script:
  - !reference [.common-gcp-prepare, script]
  - !reference [.common-terraform-plan, script]
  - !reference [.common-terraform-apply, script]
```

**Per-collector infrastructure** (`infrastructure/<collector>/`):
- `artifact.tf` — GAR repository
- `bucket.tf` — GCS bucket
- `biglake-metastore.tf` — BigLake catalog IAM
- `scheduler.tf` — Cloud Scheduler (batch only)
- `secret-manager.tf` — Secrets

## 7. Initial Data Load (Backfill)

Set GitLab CI pipeline variable: `TRIGGER_INIT_DATA_LOAD=1`

```yaml
# In deploy:prod script
if [ "$TRIGGER_INIT_DATA_LOAD" == "1" ]; then
  JOB_TYPE="initial_data"
  JOB_NAME="members-collector-init-$(date +%Y%m%d-%H%M%S)"
  MAX_WORKERS="50"
fi
```

## 8. Environment Variables

| Variable | Example | Purpose |
|----------|---------|---------|
| `GCP_PROJECT_ID` | `the1-loyalty-data` | GCP project prefix |
| `SVC_NAME` | `members-collector` | Collector directory |
| `DATAFLOW_JOB_NAME` | `members-collector` | Dataflow job name |
| `T1_PIPELINE_SA` | base64 SA key | PROD authentication |
| `RUNNER_TAG_STG` | `nonprod-docker-cicd-x86` | STG runner |
| `RUNNER_TAG_PROD` | `prod-docker-cicd-x86` | PROD runner |

## 9. Adding a New Collector — CI/CD Checklist

1. Create `{collector}/.gitlab-ci.yml` with all jobs (copy from existing collector)
2. Add `include` in top-level `.gitlab-ci.yml`
3. Set collector-specific variables (`SVC_NAME`, `INFRA_PATH`, `DATAFLOW_JOB_NAME`, etc.)
4. Create `infrastructure/{collector}/` with Terraform files
5. Create `infrastructure/{collector}/schemas/deploy.py` + JSON schemas
6. Create `infrastructure/{collector}/templates/container_spec.json`
7. Create `{collector}/config/base.yaml`, `stg.yaml`, `prod.yaml`
8. Set up GCP service account + IAM bindings
9. Test: lint → test → create-image → deploy:stg → deploy:prod

## 10. DO / DON'T

| DO | DON'T |
|----|-------|
| Use drain for streaming jobs before redeploying | Use cancel (loses in-flight messages) |
| Pin images by SHA256 digest | Deploy by tag (not reproducible) |
| Run terraform plan before apply | Apply without plan |
| Use shared extends from common-data | Duplicate CI templates per collector |
| Add STG→PROD gate (`needs: [deploy:stg]`) | Let PROD deploy run without STG validation |
| Clean up credentials in `after_script` | Leave SA keys on CI runner |

## 11. Known Issues

| Issue | Status | Workaround |
|-------|--------|------------|
| members-collector uses cancel instead of drain | Should upgrade | Minimal message loss at deploy time |
| No STG→PROD gate for loyalty collectors | Should add | PROD can deploy before STG validates |
| No BQ backup before deploy-tables:prod | Should add | Manual backup before breaking schema changes |

## 12. File Locations

```
scripts/
├── prepare_dataflow_config.sh    # Merge YAML configs → base64
├── prepare_dataflow_spec.sh      # Render container_spec.json → GCS
└── deploy_dataflow.sh            # Launch Dataflow Flex Template

infrastructure/<collector>/
├── templates/container_spec.json # Flex Template spec
├── schemas/deploy.py             # BQ table deployer
├── schemas/*.json                # Table schema definitions
├── artifact.tf                   # GAR repository
├── bucket.tf                     # GCS bucket
└── biglake-metastore.tf          # BigLake catalog IAM
```
