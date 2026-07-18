# Security Reference — Cross-Cloud Comparison

> Cross-cloud comparison of security, identity, and compliance patterns.

## Identity & Access Management Comparison

| Feature | **GCP IAM** | **AWS IAM** | **Azure AD** | **Databricks** |
|---------|-----------|-----------|------------|---------------|
| Identity | Google accounts, SA | IAM users, roles | Entra ID | Unity Catalog |
| Service identity | Service accounts | IAM roles (assume) | Managed identity | Service principals |
| Fine-grained | IAM conditions | IAM policies | Conditional access | GRANTS (SQL) |
| Cross-project | Org-level IAM | Cross-account roles | Subscriptions | Account-level |
| Audit | Cloud Audit Logs | CloudTrail | Activity Log | Audit logs |

## Encryption Comparison

| Feature | **GCP** | **AWS** | **Azure** |
|---------|---------|---------|-----------|
| At-rest (default) | Google-managed keys | AWS-managed keys | Microsoft-managed |
| Customer-managed | Cloud KMS (CMEK) | KMS (CMK) | Key Vault |
| In-transit | TLS 1.3 (default) | TLS 1.2+ | TLS 1.2+ |
| Column-level | BQ column-level AEAD | Glue column encryption | Dynamic masking |
| Key rotation | Automatic | Configurable | Configurable |

## Secrets Management Comparison

| Feature | **Secret Manager** | **Secrets Manager** | **Key Vault** | **Databricks Secrets** |
|---------|-------------------|-------------------|---------------|----------------------|
| Cloud | GCP | AWS | Azure | Databricks |
| Versioning | Yes (auto) | Yes (auto) | Yes | Yes |
| Rotation | Manual / Cloud Function | Lambda rotation | Auto-rotation | Manual |
| Access control | IAM + Secret versions | IAM policies | RBAC + policies | ACLs (scopes) |
| Cost | $0.06/version/mo | $0.40/secret/mo | $0.03/operation | Included |
| SDK | `google.cloud.secretmanager` | `boto3` | `azure.keyvault` | `dbutils.secrets` |

## Network Security Comparison

| Feature | **GCP** | **AWS** | **Azure** |
|---------|---------|---------|-----------|
| VPC | Shared VPC | VPC + Transit Gateway | VNet + peering |
| Private access | Private Google Access | VPC Endpoints | Private Endpoints |
| Firewall | VPC firewall rules | Security Groups + NACLs | NSG + Azure Firewall |
| Service perimeter | VPC Service Controls | — | Private Link |
| DNS | Cloud DNS | Route 53 | Azure DNS |

## Detailed Reference

For comprehensive security comparisons, see:
- `archive/knowledge_base/COMPARISON/CROSS_CLOUD_COMPARISON.md` (Section 9: Security)
