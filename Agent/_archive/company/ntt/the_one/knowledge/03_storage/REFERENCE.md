# Storage Reference — Warehouse, Lakehouse & Format Comparison

> Cross-cloud comparison of data warehouse, lakehouse, and open table formats.

## Data Warehouse Comparison

| Feature | **BigQuery** | **Redshift** | **Synapse/Fabric** | **Databricks SQL** |
|---------|------------|------------|-------------------|-------------------|
| Architecture | Serverless (Dremel) | Provisioned/Serverless | Dedicated/Serverless | Serverless Photon |
| Storage | Capacitor (columnar) | Managed storage | Delta Lake (OneLake) | Delta Lake |
| Pricing | On-demand or slots | Per-node or Serverless | DWU-based or Capacity | DBU-based |
| CDC | Storage Write API | Streaming ingestion | Synapse Link | Change Data Feed |
| Iceberg | BigLake external tables | Spectrum + Lake Formation | OneLake serving | UniForm |
| Concurrency | 2,000+ slots | WLM (up to 50) | Resource classes | Serverless auto |
| ML Integration | BQML | Redshift ML | Synapse ML | Mosaic AI |
| Geo | Multi-region native | RA3 cross-AZ | Geo-redundant | Multi-cloud |

## Lakehouse Comparison

| Feature | **GCP BigLake** | **AWS (S3 Tables)** | **Azure Fabric** | **Databricks** |
|---------|---------------|-------------------|-----------------|---------------|
| Format | Apache Iceberg | Apache Iceberg | Delta Lake | Delta Lake |
| Catalog | BLMS REST Catalog | Glue / Lake Formation | Unity Catalog | Unity Catalog |
| Governance | Dataplex | Lake Formation | Purview | Unity Catalog |
| Query Engine | BigQuery | Athena/Redshift/EMR | Spark/SQL endpoint | Photon/Spark |
| Compaction | Auto (managed.Write) | Auto (S3 Tables) | Auto (Optimize) | Auto (OPTIMIZE) |
| Time Travel | Iceberg snapshots | Iceberg snapshots | Delta versioning | Delta versioning |

## Open Table Format Comparison

| Feature | **Apache Iceberg** | **Delta Lake** | **Apache Hudi** |
|---------|-------------------|---------------|-----------------|
| Governance | ASF (Apache) | Linux Foundation | ASF (Apache) |
| Cloud adoption | GCP, AWS | Azure, Databricks | Limited |
| Schema evolution | Full (add/rename/reorder) | Add/rename columns | Add columns |
| Partition evolution | Yes (hidden partitions) | No (manual) | No |
| Row-level deletes | Copy-on-write + merge-on-read | Deletion vectors | Merge-on-read |
| Time travel | Snapshot-based | Version-based | Timeline-based |
| Interop | Native everywhere | UniForm (reads Iceberg) | Limited |
| Compaction | Rewrite data files | OPTIMIZE + Z-ORDER | Compaction service |
| Merge-on-read | Yes (v2 spec) | Yes (deletion vectors) | Yes (native) |

## Pricing Comparison (Approximate)

| Workload | GCP (BigQuery) | AWS (Redshift) | Databricks |
|----------|---------------|---------------|------------|
| **Small** (1TB, light queries) | $50-100/mo | $200-400/mo | $150-300/mo |
| **Medium** (10TB, moderate) | $500-1,500/mo | $1,000-3,000/mo | $800-2,000/mo |
| **Large** (100TB+, heavy) | $5,000-15,000/mo | $10,000-30,000/mo | $8,000-20,000/mo |
| **Storage** (per TB/mo) | $20 (active), $10 (long-term) | $24 (managed) | $23 (Delta) |

## The1 Storage Choices

| Decision | Choice | Why |
|----------|--------|-----|
| Source format | Apache Iceberg | Open format, schema evolution, partition evolution |
| Catalog | BLMS REST Catalog | GCP-native, vended-credentials, no key management |
| Warehouse | BigQuery | Serverless, Storage Write API, CDC support |
| Write method | managed.Write (Beam IcebergIO) | Cross-language Java connector, handles compaction |
| BQ write | Storage Write API | High throughput, CDC support, at-least-once |

## Detailed Reference

For comprehensive comparison, see:
- `archive/knowledge_base/COMPARISON/CROSS_CLOUD_COMPARISON.md` (Sections 2-3: Warehouse/Lakehouse)
- `archive/knowledge_base/GCP/DATA_PLATFORM/GCP_DATA_PLATFORM.md` (BigQuery, BigLake, Iceberg)
- `archive/knowledge_base/AWS/DATA_PLATFORM/AWS_DATA_PLATFORM.md` (Redshift, S3 Tables)
- `archive/knowledge_base/DATABRICKS/DATA_PLATFORM/DATABRICKS_DATA_PLATFORM.md` (Delta, UniForm)
