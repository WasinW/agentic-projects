# Shared Infrastructure

## 1. BigLake Catalog (BLMS REST)

- Endpoint: `biglake.googleapis.com` per GCP project
- Credential mode: `VENDED_CREDENTIALS` (GoogleAuthManager)
- Per-domain catalogs defined in terraform: `common/GCP/biglake-metastore.tf`
- Per-collector IAM: `infrastructure/{collector}/biglake-metastore.tf` grants SA access to source + refined datasets
- Catalog type: `rest` with namespace `"source"`
- Table location: `gs://{catalog_name}/{table_name}` (flat path, no `source/` prefix)

## 2. Common Scripts

Located at `scripts/` in each collector (or shared):

| Script | Purpose |
|--------|---------|
| `deploy_dataflow.sh` | `gcloud dataflow flex-template run` with staging/temp locations |
| `prepare_dataflow_config.sh` | Merge base + env YAML into final config |
| `prepare_dataflow_spec.sh` | Generate container_spec.json with GAR image URI |

All Dataflow collectors share this pattern. CloudRun services use different deploy scripts.

## 3. CI Templates

Located in shared CI config (common-base or included templates):

| Template | Provides |
|----------|----------|
| `common-base.gitlab-ci.yml` | `.uv_base`, `.common-sonar-scan`, `.common-gcp-prepare`, `.common-gitleaks`, `.common-trivy` |
| `common.gitlab-ci.yml` | Rules for branch-based triggers (MR, main, tags) |
| `dataflow.gitlab-ci.yml` | Dataflow-specific jobs (build image, deploy flex-template) |
| `terraform.gitlab-ci.yml` | `terraform:plan`, `terraform:apply` per env |
| V2 templates | Newer collectors use updated V2 CI structure |

Collectors extend these via `extends:` and `!reference` in their `.gitlab-ci.yml`.

## 4. Terraform Patterns

- **Backend**: GCS bucket `devops-terraformstate-nonprod` (shared state)
- **Workspaces**: Environment selection via `terraform workspace` (stg/prod)
- **Module library**: 27+ reusable modules (e.g., GCS bucket, GAR repo, IAM, BigLake)
- **Per-collector infra**: `infrastructure/{collector}/` contains:
  - `bucket.tf` -- GCS buckets (source, staging)
  - `artifact.tf` -- GAR repository
  - `biglake-metastore.tf` -- BigLake IAM bindings
  - `templates/container_spec.json` -- Flex template spec
- **Common infra**: `common/GCP/` contains:
  - `biglake-metastore.tf` -- BigLake catalog + source bucket + SA IAM
  - Network, VPC, shared resources

## 5. GCP Project Naming

```
the1-{domain}-data-{env}
```

Examples:
- `the1-loyalty-data-prod`, `the1-loyalty-data-stg`
- `the1-sales-data-prod`
- `the1-gamification-data-prod`
- `the1-messaging-data-prod`
- `the1-partner-data-prod`
- `the1-catalog-data-prod`
- `the1-insight-data-prod`

## 6. Network

- **VPC**: `the1-vpc-net-share-{env}` (shared VPC)
- **Subnets**:
  - Dataflow: dedicated subnet for Dataflow workers
  - Backend: for CloudRun and other services
- Dataflow deploy passes `--network` and `--subnetwork` flags

## 7. Container Registry (GAR)

```
asia-southeast1-docker.pkg.dev/{gcp-project}/{collector-name}
```
- Each collector has its own GAR repository
- Images tagged by CI pipeline (commit SHA or tag)
- CI builds with Kaniko, pushes to GAR
- Flex template references GAR image URI in container_spec.json

## 8. Secret Manager

- Per-collector secrets in GCP Secret Manager
- Key naming patterns:
  - `kafkaCredentials` -- Kafka connection (bootstrap servers, SASL)
  - `apiCredentials` -- REST API credentials
  - `bigqueryCredentials` -- BQ service account (if separate)
- Accessed at runtime by Dataflow worker SA or CloudRun SA
- Secret keys may differ between collectors (e.g., loyalty migrated from `kafka_connection` to `kafkaCredentials`)
