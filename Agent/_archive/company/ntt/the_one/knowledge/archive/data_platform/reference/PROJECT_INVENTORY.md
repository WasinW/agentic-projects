# Data Platform - Project Inventory

> **Last Updated:** 2026-02-20
> **Scope:** Complete inventory of ALL projects, services, and infrastructure resources across the Data Platform

---

## 1. Projects

| Project | GCP Project ID Pattern | Domain | Team | Region |
|---------|----------------------|--------|------|--------|
| Loyalty Data | `the1-loyalty-data-{env}` | loyalty-data | Data Platform | asia-southeast1 |
| Sales Data | `the1-sales-data-{env}` | sales-data | Data Platform | asia-southeast1 |
| Insight | `the1-insight-{env}` | insight | Insight Squad | asia-southeast1 |
| Network (shared) | `the1-network-{env}` | network | Platform | asia-southeast1 |

Where `{env}` is one of: `stg`, `prod`

---

## 2. Collectors / Services

### Loyalty Data (`the1-loyalty-data-{env}`)

| Service | Type | Language | Framework | Deployment | Source | Status |
|---------|------|----------|-----------|------------|--------|--------|
| members-collector | Streaming | Python 3.12 | Apache Beam 2.70.0 | Dataflow Flex Template | Kafka (loyalty.members.upgraded, loyalty.members.downgraded) | Active |
| tiers-collector | Batch | Python 3.12 | Apache Beam 2.70.0 | Dataflow Flex Template | Loyalty Tiers Master API | Active |
| members-tiers-history-collector | Batch | Python 3.12 | Apache Beam 2.70.0 | Dataflow Flex Template | PostgreSQL (via SSH tunnel) | Active |
| transactions-collector | Streaming | Python 3.12 | Apache Beam 2.70.0 | Dataflow Flex Template | Kafka (transaction earned events) | Active |
| purchases-collector | Streaming | Python 3.12 | Apache Beam 2.70.0 | Dataflow Flex Template | Kafka (purchase events) | Active |
| rewards-collector | Batch (scheduled) | Python 3.12 | FastAPI + PyIceberg | Cloud Run | Rewards API | Active |

### Sales Data (`the1-sales-data-{env}`)

| Service | Type | Language | Framework | Deployment | Source | Status |
|---------|------|----------|-----------|------------|--------|--------|
| sales-collector | Streaming | Python 3.12 | Apache Beam 2.70.0 | Dataflow Flex Template | Kafka (loyalty.sales.created) | Development |

### Insight (`the1-insight-{env}`)

| Service | Type | Language | Framework | Deployment | Source | Status |
|---------|------|----------|-----------|------------|--------|--------|
| Customer Profile Pipeline | Streaming | Python 3.11 | Apache Beam 2.69.0 | Dataflow Flex Template | Pub/Sub + Bigtable | Active (V3.2.0) |
| Personas API | REST API | Kotlin (JDK 21) | Spring Boot 3.5.x | Cloud Run / GKE | Bigtable + BigQuery | Active |
| Personas Resolver | Service | Kotlin (JDK 21) | Spring Boot 3.5.x | Cloud Run / GKE | Bigtable | Active |
| Audiences API | REST API | Kotlin (JDK 21) | Spring Boot 3.5.x | Cloud Run / GKE | BigQuery + ClickHouse | Active |
| Collector | Event API | Node.js (TypeScript) | Express | Cloud Run | HTTP events | Active |
| Triggers | Batch | Node.js (TypeScript) | tsx | Cloud Run + Scheduler | Multiple | Active |

---

## 3. GCS Buckets

### Loyalty Data

| Bucket Name Pattern | Purpose | IAM (objectAdmin/admin) |
|---------------------|---------|------------------------|
| `the1-loyalty-data-source-{env}` | BigLake Iceberg source data (new naming, BLMS catalog) | All 4 Dataflow collector SAs (admin) |
| `the1-loyalty-data-{env}-source` | BigLake Iceberg source data (old naming) | All 4 Dataflow collector SAs (admin) |
| `the1-loyalty-data-{env}-refined` | Refined data | transactions-collector SA (objectAdmin) |
| `the1-loyalty-data-{env}-public` | Public datasets | transactions-collector SA (objectAdmin) |
| `the1-loyalty-data-{env}-members-collector` | Members-collector per-service bucket (staging/temp/templates) | t1-members-collector SA |
| `the1-loyalty-data-{env}-tiers-collector` | Tiers-collector per-service bucket (staging/temp/templates) | t1-tiers-collector SA |
| `the1-loyalty-data-{env}-members-tiers-history-collector` | Members-tiers-history per-service bucket (staging/temp/templates) | t1-members-tiers-his-collector SA |
| `the1-loyalty-data-{env}-purchases-collector` | Purchases-collector per-service bucket (staging/temp/templates) | t1-purchases-collector SA |

### Sales Data

| Bucket Name Pattern | Purpose | IAM |
|---------------------|---------|-----|
| `the1-sales-data-source-{env}` | BigLake Iceberg source data | t1-sales-collector SA (objectAdmin) |
| `the1-sales-data-config-{env}` | Flex templates + config | t1-sales-collector SA (admin) |

### Insight

| Bucket Name Pattern | Purpose | IAM |
|---------------------|---------|-----|
| Various per-service buckets | Dataflow staging, Collector storage | Per-service SAs |

---

## 4. Artifact Registry (GAR) Repositories

### Loyalty Data

| Repository ID | Format | Description |
|--------------|--------|-------------|
| `members-collector` | Docker | Members-collector images |
| `tiers-collector` | Docker | Tiers-collector images |
| `members-tiers-history-collector` | Docker | Members-tiers-history-collector images |
| `purchases-collector` | Docker | Purchases-collector images |
| `transactions-collector` | Docker | Transactions-collector images |
| `rewards-collector` | Docker | Rewards-collector images (Cloud Run) |

### Sales Data

| Repository ID | Format | Description |
|--------------|--------|-------------|
| `sales-collector` | Docker | Sales-collector images |

### Insight

| Repository ID | Format | Description |
|--------------|--------|-------------|
| Various per-service | Docker | Personas API, Audiences API, Collector, Triggers, Customer Profile Pipeline |

Location for all: `asia-southeast1-docker.pkg.dev/{project_id}/{repo_id}`

---

## 5. BigQuery Datasets

### Loyalty Data (`the1-loyalty-data-{env}`)

| Dataset ID | Type | Description |
|-----------|------|-------------|
| `source` | External (BigLake linked) | Iceberg tables linked via BigLake catalog (raw data) |
| `refined` | Native BQ | Refined/transformed data (per-collector tables) |

**Refined Tables:**
- `member_tier` - Member tier assignments (CDC in prod)
- `tier_maintenance` - Tier maintenance events
- `tier_events_upgraded` - Tier upgrade events (optional)
- `tier_events_downgraded` - Tier downgrade events (optional)
- `tiers_master` - Tiers master data
- `members_tiers_history` - Member-tier relationship history
- Transaction/purchase tables (managed by other team)

### Sales Data (`the1-sales-data-{env}`)

| Dataset ID | Type | Description |
|-----------|------|-------------|
| `source` | Planned (commented) | Iceberg tables (pending BigLake catalog setup) |
| `refined` | Native BQ | Refined sales data |

**Refined Tables:**
- `sales_receipt` - Sales receipt header (MONTH partition on trans_date)
- `sales_sku` - Sales SKU line items (MONTH partition on trans_date)
- `sales_tender` - Sales tender/payment details (MONTH partition on trans_date)

### Insight (`the1-insight-{env}`)

| Dataset ID | Type | Description |
|-----------|------|-------------|
| `ms_personas` | Native BQ | Customer profile data (CDC from pipeline) |
| Various analytics datasets | Native BQ | Audiences, consent, reporting |

---

## 6. Secret Manager Secrets

### Loyalty Data

| Secret Name | Purpose | Accessors |
|-------------|---------|-----------|
| `members-collector` | Kafka + OAuth2 credentials (kafka_connection, api_connection) | t1-members-collector SA, IAC SA |
| `tiers-collector` | Tiers API OAuth2 credentials | t1-tiers-collector SA |
| `members-tiers-history-collector` | PostgreSQL + SSH tunnel credentials | t1-members-tiers-his-collector SA |
| `purchases-collector` | Kafka credentials | t1-purchases-collector SA |
| `transactions-collector` | Kafka + API credentials | t1-transactions-collector SA |
| `rewards-collector` | Rewards API credentials | t1-rewards-collector SA |
| `loyalty-data-migration` | AWS S3 credentials for DTS init migration (temporary) | t1-members-collector SA, IAC SA |

### Sales Data

| Secret Name | Purpose | Accessors |
|-------------|---------|-----------|
| `sales-collector` | Kafka credentials | t1-sales-collector SA |

### Insight

| Secret Name | Purpose | Accessors |
|-------------|---------|-----------|
| Various per-service | Bigtable, BigQuery, AWS S3, API keys | Per-service SAs |

---

## 7. BigLake Iceberg Catalogs

### Loyalty Data

| Catalog Name | Type | Credential Mode | Description |
|-------------|------|-----------------|-------------|
| `the1-loyalty-data-source-{env}` | `CATALOG_TYPE_GCS_BUCKET` | `CREDENTIAL_MODE_VENDED_CREDENTIALS` | Shared Iceberg catalog for all loyalty collectors |

**Catalog IAM (roles/biglake.editor):**
- `t1-members-collector@the1-loyalty-data-{env}.iam.gserviceaccount.com`
- `t1-tiers-collector@the1-loyalty-data-{env}.iam.gserviceaccount.com`
- `t1-members-tiers-his-collector@the1-loyalty-data-{env}.iam.gserviceaccount.com`
- `t1-transactions-collector@the1-loyalty-data-{env}.iam.gserviceaccount.com`

The BLMS service account (auto-created by BigLake) gets `roles/storage.objectAdmin` on the source bucket.

### Sales Data (Planned)

| Catalog Name | Type | Credential Mode | Status |
|-------------|------|-----------------|--------|
| `the1-sales-data-source-{env}` | `CATALOG_TYPE_GCS_BUCKET` | `CREDENTIAL_MODE_VENDED_CREDENTIALS` | Commented in Terraform (pending) |

---

## 8. Service Accounts

### Naming Convention

Pattern: `t1-{service-name}@{project-id}.iam.gserviceaccount.com`

### Loyalty Data

| Service Account | Service | Roles |
|----------------|---------|-------|
| `t1-members-collector@the1-loyalty-data-{env}` | members-collector | dataflow.worker, dataflow.admin, storage.objectAdmin, artifactregistry.reader, bigquery.dataEditor, bigquery.jobUser, biglake.editor |
| `t1-tiers-collector@the1-loyalty-data-{env}` | tiers-collector | dataflow.worker, dataflow.admin, storage.objectAdmin, artifactregistry.reader, bigquery.dataEditor, bigquery.jobUser, biglake.editor |
| `t1-members-tiers-his-collector@the1-loyalty-data-{env}` | members-tiers-history | dataflow.worker, dataflow.admin, storage.objectAdmin, artifactregistry.reader, bigquery.dataEditor, bigquery.jobUser, biglake.editor |
| `t1-transactions-collector@the1-loyalty-data-{env}` | transactions-collector | dataflow.worker, dataflow.admin, storage.objectAdmin, artifactregistry.reader, bigquery.dataEditor, bigquery.jobUser, biglake.editor |
| `t1-purchases-collector@the1-loyalty-data-{env}` | purchases-collector | dataflow.worker, dataflow.admin, storage.objectAdmin, artifactregistry.reader, bigquery.dataEditor, bigquery.jobUser |
| `t1-rewards-collector@the1-loyalty-data-{env}` | rewards-collector | run.invoker, storage.objectAdmin, secretmanager.secretAccessor |
| `t1-loy-data-{env}-sa-iac@the1-loyalty-data-{env}` | Terraform IAC | Admin roles for infrastructure provisioning |

### Sales Data

| Service Account | Service | Roles |
|----------------|---------|-------|
| `t1-sales-collector@the1-sales-data-{env}` | sales-collector | dataflow.worker, dataflow.admin, storage.objectAdmin, artifactregistry.reader, bigquery.dataEditor, bigquery.jobUser |

---

## 9. Cloud Schedulers

| Scheduler Name | Project | Schedule | Timezone | Target | Description |
|---------------|---------|----------|----------|--------|-------------|
| `tiers-collector-daily-trigger` | loyalty-data | `0 1 * * *` | Asia/Bangkok | Dataflow REST API (flexTemplates:launch) | Daily tiers batch job at 1 AM BKK |
| `members-tiers-history-daily-trigger` | loyalty-data | `0 1 * * *` | Asia/Bangkok | Dataflow REST API (flexTemplates:launch) | Daily M-T-H batch job at 1 AM BKK |
| `rewards-collector-scheduler` | loyalty-data | `0 1 * * *` | (server default) | Cloud Run POST /trigger | Daily rewards collection at 1 AM |

All schedulers have retry_count=3 with exponential backoff.

---

## 10. Network Resources

### Shared VPC (Loyalty + Sales)

| Resource | Name Pattern | Project |
|----------|-------------|---------|
| VPC | `the1-vpc-net-share-{env}` | `the1-network-{env}` |
| Dataflow Subnet | `the1-subnet-dataflow-{env}` | `the1-network-{env}` |
| Backend Subnet | `the1-subnet-backend-{env}` | `the1-network-{env}` (used by Cloud Run) |

**Dataflow workers:**
- `ipConfiguration: WORKER_IP_PRIVATE` (private IP only)
- Network: `projects/the1-network-{env}/global/networks/the1-vpc-net-share-{env}`
- Subnetwork: `projects/the1-network-{env}/regions/asia-southeast1/subnetworks/the1-subnet-dataflow-{env}`

### Insight VPC (Separate)

| Resource | Name | Description |
|----------|------|-------------|
| VPC | `dataflow` | Dedicated VPC for Insight Dataflow jobs |
| Subnet | `dataflow-private` | Private subnet (192.168.1.0/24) |

---

## 11. Common Shared Library

| Library | Package Name | Repository | Used By |
|---------|-------------|------------|---------|
| common-data-python | `common-data-python` | `gitlab.com/The1central/The1/the1-data/common-data` (subdirectory: common-python) | All Dataflow collectors (loyalty + sales) |
| common-data-python-cloudrun | `common-data-python-cloudrun` | Same repo (subdirectory: common-python-cloudrun) | rewards-collector (Cloud Run) |

**common-data-python provides:**
- `common.beam.adapters.input.kafka_reader` - KafkaReaderConfig, Kafka cross-language transform
- Common Beam utilities for all collectors

---

## 12. Terraform State

| Project | State Bucket | Prefix |
|---------|-------------|--------|
| Loyalty Common GCP | `devops-terraformstate-nonprod` | `the1-loyalty-data/services/common` |
| Loyalty Members | `devops-terraformstate-nonprod` | `the1-loyalty-data/services/members` |
| Loyalty Tiers | `devops-terraformstate-nonprod` | `the1-loyalty-data/services/tiers` |
| Loyalty M-T-H | `devops-terraformstate-nonprod` | `the1-loyalty-data/services/members-tiers-history` |
| Loyalty Purchases | `devops-terraformstate-nonprod` | `the1-loyalty-data/services/purchases` |
| Loyalty Transactions | `devops-terraformstate-nonprod` | `the1-loyalty-data/services/transaction` |
| Loyalty Rewards | `devops-terraformstate-nonprod` | `the1-loyalty-data/services/rewards-collector` |
| Sales Collector | `devops-terraformstate-nonprod` | `the1-sales-data/services/sales-collector` |

---

## 13. CI/CD (GitLab)

### Pipeline Stages (Common across collectors)

1. **sonar-scan** - SonarQube code quality (shared extends `.common-sonar-scan`)
2. **gitleaks** - Secret scanning (shared extends)
3. **trivy** - Container vulnerability scanning (shared extends)
4. **create-image** - Docker build + push to GAR (multi-destination: STG + PROD)
5. **terraform:plan** - Infrastructure plan (stg + prod)
6. **terraform:apply** - Infrastructure apply (stg + prod)
7. **deploy-tables** - BQ schema deployment via deploy.py (stg + prod)
8. **deploy** - Dataflow job deployment (stg + prod)

### Image Build

All collectors use multi-stage Docker builds with:
- **Builder stage:** `ghcr.io/astral-sh/uv:python3.12-bookworm` (uv for fast dependency resolution)
- **Runtime stage:** `gcr.io/dataflow-templates-base/python312-template-launcher-base` (Dataflow Flex Template base)
- Java 17 JRE installed for Kafka cross-language transforms

---

## 14. Cross-Cloud Resources (AWS)

### Loyalty Data (AWS)

| Resource | Purpose |
|----------|---------|
| AWS ECR | Container registry (legacy) |
| AWS EKS | Kubernetes cluster (legacy) |
| AWS S3 | Data export destination (customer profiles) |
| AWS Secret Manager | Legacy credentials |
| AWS Route53 | DNS (legacy) |

### Insight (AWS)

| Resource | Purpose |
|----------|---------|
| AWS S3 | Customer profile Parquet exports from pipeline |
| AWS RDS | Historical data source |

---

## 15. Environment Matrix

| Environment | Suffix | Write Mode | Streaming Engine | Workers |
|------------|--------|------------|-----------------|---------|
| STG | `stg` | `append` | Varies | 1 |
| PROD | `prod` | `cdc` (where applicable) | Varies | 1-2 |
