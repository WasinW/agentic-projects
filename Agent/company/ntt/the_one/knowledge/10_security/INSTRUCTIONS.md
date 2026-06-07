# Security Instructions

> AI: Read this file when configuring service accounts, IAM, secrets, VPC, or BLMS credentials.

## Quick Reference

```
Security Pattern:
  Per-collector Service Account → Least Privilege IAM → Secret Manager → Shared VPC

BLMS Authentication:
  GoogleAuthManager + vended-credentials → auto-scoped GCS access via REST Catalog
```

---

## 1. Service Accounts

### Per-Collector Strategy

Each collector has a dedicated service account following least privilege:

| Collector | Service Account | Key Permissions |
|-----------|----------------|-----------------|
| members-collector | `t1-members-collector` | BigLake Editor, Storage Admin, BQ DataEditor |
| tiers-collector | `t1-tiers-collector` | BigLake Editor, Storage Admin, BQ DataEditor |
| members-tiers-history | `t1-members-tiers-his-collector` | BigLake Editor, Storage Admin, BQ DataEditor |

### Service Account Naming

```
t1-{collector}@the1-{domain}-{env}.iam.gserviceaccount.com
```

Example: `t1-members-collector@the1-loyalty-data-prod.iam.gserviceaccount.com`

### IAM Roles Per Collector

| Role | Resource | Purpose |
|------|----------|---------|
| `roles/biglake.editor` | BigLake catalog | Manage Iceberg tables |
| `roles/storage.objectAdmin` | Source GCS bucket | Read/write Iceberg data |
| `roles/bigquery.dataEditor` | `source` dataset | Write Iceberg external tables |
| `roles/bigquery.dataEditor` | `refined` dataset | Write refined BQ tables |
| `roles/secretmanager.secretAccessor` | Collector secret | Read credentials |
| `roles/serviceusage.serviceUsageConsumer` | Project | Use GCP APIs |
| `roles/dataflow.worker` | Project | Run Dataflow jobs |

### Terraform IAM (biglake-metastore.tf)

```hcl
# infrastructure/{collector}/biglake-metastore.tf
resource "google_bigquery_dataset_iam_member" "source_editor" {
  dataset_id = "source"
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${var.collector_sa}"
}

resource "google_bigquery_dataset_iam_member" "refined_editor" {
  dataset_id = "refined"
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${var.collector_sa}"
}
```

---

## 2. BigLake Catalog IAM

### BLMS REST Catalog Authentication Chain

```
Pipeline (Beam IcebergIO)
  → GoogleAuthManager (auto OAuth2)
  → BLMS REST Catalog API
  → Vended Credentials (auto-scoped GCS access)
  → GCS (read/write Parquet files)
```

### Catalog Properties (Security-Related)

```python
catalog_properties = {
    "type": "rest",
    "uri": "https://biglake.googleapis.com/iceberg/v1/restcatalog",
    "rest.auth.type": "org.apache.iceberg.gcp.auth.GoogleAuthManager",
    "header.X-Iceberg-Access-Delegation": "vended-credentials",
    "header.x-goog-user-project": project_id,
    "io-impl": "org.apache.iceberg.gcp.gcs.GCSFileIO",
}
```

**How vended-credentials work:**
1. Pipeline authenticates to BLMS REST API using SA credentials
2. BLMS validates SA has `roles/biglake.editor` on the catalog
3. BLMS returns temporary, scoped GCS credentials (vended)
4. Pipeline uses vended credentials to read/write Parquet files on GCS
5. No direct GCS credentials needed in pipeline code

### Catalog SA IAM

The BigLake Metastore creates an auto-managed SA that needs GCS access:

```hcl
# common/GCP/biglake-metastore.tf
resource "google_storage_bucket_iam_member" "biglake_sa_source" {
  bucket = var.source_bucket
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_biglake_catalog.default.biglake_service_account}"
}
```

---

## 3. Secrets Management

### GCP Secret Manager

All sensitive credentials are stored in Secret Manager, NEVER in code or YAML:

| Secret | Contents |
|--------|----------|
| `members-collector` | Kafka credentials, Loyalty API keys |
| `tiers-collector` | Loyalty Tiers Master API credentials |
| `members-tiers-history` | PostgreSQL credentials, SSH key |

### Secret Structure (JSON)

```json
{
  "kafkaCredentials": {
    "bootstrap_servers": "pkc-xxx.confluent.cloud:9092",
    "username": "...",
    "password": "...",
    "schema_registry_url": "https://psrc-xxx.confluent.cloud",
    "schema_registry_user": "...",
    "schema_registry_password": "..."
  },
  "apiCredentials": {
    "base_url": "https://api.the1.co.th",
    "token_url": "https://auth.the1.co.th/token",
    "client_id": "...",
    "client_secret": "...",
    "api_id": "..."
  }
}
```

### Secret Access in Pipeline

```python
# adapters/input/configuration/secret_adapter.py
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
secret = client.access_secret_version(
    name=f"projects/{project_id}/secrets/{secret_name}/versions/latest"
)
credentials = json.loads(secret.payload.data.decode("utf-8"))
```

### Secret Key Migration Notes

- `kafka_connection` → `kafkaCredentials` (current)
- `api_connection` → `apiCredentials` (current)
- Changing secret keys without updating code = Kafka timeout at runtime

---

## 4. Network Security

### Shared VPC

| Setting | Value |
|---------|-------|
| VPC | `the1-vpc-net-share-{env}` |
| Dataflow Subnet | `the1-subnet-dataflow-{env}` |
| Backend Subnet | `the1-subnet-backend-{env}` |
| Worker IP Mode | `WORKER_IP_PRIVATE` (private IPs only) |
| GCP Service Access | Private Google Access (no public IPs) |

### External Connections

| Destination | Protocol | Auth |
|-------------|----------|------|
| Confluent Kafka | SASL/SSL over internet | Username/password |
| Loyalty REST API | HTTPS | OAuth2 client credentials |
| AWS RDS (PostgreSQL) | SSH tunnel via bastion | SSH key + DB credentials |

### Deploy Script Network Config

```bash
# deploy_dataflow.sh
--network "projects/the1-network-{env}/global/networks/the1-vpc-net-share-{env}"
--subnetwork "regions/asia-southeast1/subnetworks/the1-subnet-dataflow-{env}"
```

---

## 5. CI/CD Security

### GitLab CI Credentials

| Variable | Purpose | Scope |
|----------|---------|-------|
| `T1_PIPELINE_SA` | Base64 SA key for PROD auth | PROD jobs only |
| `GCP_PROJECT_ID` | GCP project prefix | Per-collector |

### Credential Cleanup

```yaml
# .gitlab-ci.yml — always clean up
after_script:
  - rm -f /tmp/sa-key.json
  - unset GOOGLE_APPLICATION_CREDENTIALS
```

### Security Scanning

| Scanner | Purpose | Stage |
|---------|---------|-------|
| SonarQube | Static code analysis | build |
| Gitleaks | Secret detection in source | build |
| Trivy | Container image vulnerabilities | build |

---

## 6. DO / DON'T

| DO | DON'T |
|----|-------|
| Use per-collector service accounts | Share SAs across collectors |
| Store all secrets in Secret Manager | Put credentials in YAML, code, or env vars |
| Use vended-credentials for BLMS | Manage GCS credentials manually |
| Use private IPs for Dataflow workers | Use public IPs |
| Clean up SA keys in CI `after_script` | Leave keys on CI runners |
| Use SASL/SSL for Kafka | Use plaintext Kafka connections |
| Use SSH tunnel for PostgreSQL access | Expose RDS to public internet |

---

## 7. File Locations

```
infrastructure/{collector}/
├── biglake-metastore.tf        # BigLake catalog IAM (per-collector)
├── secret-manager.tf           # Secret resource (manual populate)
└── main.tf                     # Provider + SA config

infrastructure/common/GCP/
├── biglake-metastore.tf        # BigLake catalog creation + catalog SA IAM
├── service-account.tf          # Collector SA creation
└── source-bucket.tf            # Source GCS bucket + permissions
```
