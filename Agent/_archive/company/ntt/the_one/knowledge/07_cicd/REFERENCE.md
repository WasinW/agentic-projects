# CI/CD Reference — Cross-Cloud Patterns

> Cross-cloud comparison of CI/CD and deployment patterns for data pipelines.

## CI/CD Tool Comparison

| Feature | **GitLab CI** | **GitHub Actions** | **Cloud Build** | **CodePipeline** | **Azure DevOps** |
|---------|-------------|-------------------|----------------|-----------------|-----------------|
| Runner | Self-hosted + SaaS | GitHub-hosted + self | Cloud Build workers | CodeBuild | Azure agents |
| Container build | Kaniko, Docker | Docker, Buildx | Cloud Build native | CodeBuild Docker | Azure Docker |
| IaC integration | terraform CLI | terraform CLI | Cloud Deploy | CDK, CloudFormation | ARM, Bicep |
| Secret mgmt | CI variables | GitHub Secrets | Secret Manager | Secrets Manager | Key Vault |
| Parallel jobs | stages + DAG | jobs matrix | build steps | stages | stages |
| Artifact storage | GitLab Packages | GitHub Packages | Artifact Registry | ECR, S3 | Azure Artifacts |

## Dataflow Deployment Patterns

| Pattern | Description | When to Use |
|---------|-------------|-------------|
| **Flex Template** | Docker image → Dataflow launcher | All collectors (our choice) |
| **Classic Template** | Staged template on GCS | Legacy pipelines |
| **Direct launch** | `gcloud dataflow run` | Ad-hoc/debugging |
| **Update in-place** | `--update` flag on running job | Schema-compatible changes only |
| **Drain + relaunch** | Drain existing → launch new | Breaking changes (streaming) |

## Container Registry Comparison

| Feature | **Artifact Registry** | **ECR** | **ACR** | **Docker Hub** |
|---------|---------------------|---------|---------|---------------|
| Cloud | GCP | AWS | Azure | Multi-cloud |
| Vulnerability scan | On-push | On-push (Inspector) | Defender | Snyk integration |
| Multi-arch | Yes | Yes | Yes | Yes |
| Cost | $0.10/GB/mo | $0.10/GB/mo | $0.10/GB/mo | Free (public) |

## Detailed Reference

For comprehensive comparison, see:
- `archive/knowledge_base/COMPARISON/CROSS_CLOUD_COMPARISON.md` (Section 10: IaC)
