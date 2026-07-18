# Serving Reference — BI & Analytics Comparison

> Cross-cloud comparison of serving, BI, and analytics patterns.

## BI Tool Integration

| Feature | **Looker** | **Power BI** | **Tableau** | **Metabase** |
|---------|-----------|-------------|------------|-------------|
| Best with | GCP (BigQuery) | Azure (Fabric) | Any (native connectors) | Self-hosted |
| Semantic model | LookML | DAX measures | Tableau data model | Questions/dashboards |
| Real-time | BigQuery streaming | DirectQuery | Live connection | Query-based |
| Embedding | Yes (iframes, SDK) | Yes (Power BI Embedded) | Yes (Tableau Embedded) | Yes (iframe) |
| Cost | Per-user license | Per-user or capacity | Per-user license | Free (OSS) |
| Governance | Looker Hub | Power BI governance | Tableau Server | Manual |

## Serving Patterns

| Pattern | Use Case | Technology |
|---------|----------|-----------|
| **Materialized Views** | Pre-computed aggregations | BigQuery, Redshift, Synapse |
| **Authorized Views** | Cross-project data sharing | BigQuery |
| **SQL Views** | Logical data transformations | All warehouses |
| **API Layer** | Application serving | Cloud Run, GKE, Lambda |
| **Caching** | Low-latency reads | Redis, Memcached, Bigtable |
| **OLAP Engine** | Interactive analytics | ClickHouse, Druid, Pinot |

## Detailed Reference

For comprehensive comparison, see:
- `archive/knowledge_base/COMPARISON/CROSS_CLOUD_COMPARISON.md` (BI sections)
