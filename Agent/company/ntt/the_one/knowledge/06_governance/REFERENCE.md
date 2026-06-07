# Governance Reference — Cross-Cloud Comparison

> Cross-cloud comparison of data governance platforms.

## Governance Platform Comparison

| Feature | **GCP Dataplex** | **AWS Lake Formation** | **Azure Purview** | **Databricks Unity Catalog** |
|---------|-----------------|----------------------|------------------|---------------------------|
| Scope | Data mesh governance | Lake + warehouse | Enterprise-wide | Multi-cloud lakehouse |
| Catalog | Dataplex Universal Catalog | Glue Data Catalog | Purview Data Map | Unity Catalog |
| Access control | IAM + column-level | Cell-level, tag-based | RBAC + ABAC | GRANTS (SQL-style) |
| Data quality | Auto data quality scans | Glue Data Quality | Purview DQ rules | Lakehouse monitoring |
| Lineage | Auto-capture (BQ, Dataflow) | Limited (Glue jobs) | Auto-capture + custom | Unity Catalog lineage |
| Profiling | Auto data profiling | Manual (Glue profiling) | Auto classification | Table statistics |
| Discovery | Search, browse, tags | Glue Catalog search | Purview search + glossary | Unity Catalog search |
| Sharing | Analytics Hub | Lake Formation + RAM | Purview Data Share | Delta Sharing |
| Format support | BQ, Iceberg, external | Iceberg, Hudi, Parquet | Delta, Parquet | Delta, Iceberg (UniForm) |

## Data Quality Comparison

| Feature | **Dataplex** | **Great Expectations** | **dbt Tests** | **Monte Carlo** |
|---------|------------|----------------------|--------------|----------------|
| Type | Managed service | Open-source library | Built-in framework | SaaS platform |
| Setup | No-code rules | Code-based expectations | SQL assertions | Agent-based |
| Scheduling | Built-in | External (Airflow) | dbt Cloud scheduler | Continuous |
| Alerting | Cloud Monitoring | Custom | dbt Cloud | Built-in |
| Cost | Pay-per-scan | Free (self-managed) | dbt Cloud license | SaaS pricing |
| Best for | GCP-native, BQ tables | Multi-cloud, custom rules | SQL warehouse | Enterprise observability |

## Access Control Patterns

| Pattern | Description | Platforms |
|---------|-------------|-----------|
| **Row-level security** | Filter rows by user attribute | BQ (row-level access), Redshift, Synapse |
| **Column-level security** | Mask/restrict column access | BQ (column-level), Lake Formation, Unity Catalog |
| **Tag-based (ABAC)** | Access by data classification tags | Lake Formation, Purview |
| **RBAC** | Role-based access | All platforms |
| **Data masking** | Dynamic data masking | BQ (data masking), Synapse, Databricks |

## Detailed Reference

For comprehensive comparison, see:
- `archive/knowledge_base/COMPARISON/CROSS_CLOUD_COMPARISON.md` (Section 7: Governance)
- `archive/knowledge_base/GCP/CLOUD_SERVICE/GCP_CLOUD_SERVICES.md` (Dataplex)
- `archive/knowledge_base/AWS/CLOUD_SERVICE/AWS_CLOUD_SERVICES.md` (Lake Formation)
