# Data Platform Knowledge Base

> **Master Index** | **Created**: 2026-03-05 | **Maintainer**: Data Platform Team

## Overview

Comprehensive knowledge base covering data platform, data warehouse, and lakehouse solutions across 4 major cloud/platform providers. Designed as a consulting reference for enterprise data architecture decisions.

---

## Directory Structure

```
knowledge_base/
├── README.md                          ← You are here (Master Index)
│
├── GCP/
│   ├── DATA_PLATFORM/
│   │   └── GCP_DATA_PLATFORM.md       BigQuery, BigLake, Iceberg, Lakehouse Architecture
│   └── CLOUD_SERVICE/
│       └── GCP_CLOUD_SERVICES.md      Dataflow, Dataproc, Composer, Pub/Sub, Dataform, Dataplex
│
├── AWS/
│   ├── DATA_PLATFORM/
│   │   └── AWS_DATA_PLATFORM.md       Redshift, Lake Formation, S3 Tables, Iceberg, Glue, EMR
│   └── CLOUD_SERVICE/
│       └── AWS_CLOUD_SERVICES.md      Kinesis, MSK, MWAA, Step Functions, DataZone, DMS
│
├── AZURE/
│   ├── DATA_PLATFORM/
│   │   └── AZURE_DATA_PLATFORM.md     Synapse, Fabric, OneLake, Delta Lake, Azure Databricks
│   └── CLOUD_SERVICE/
│       └── AZURE_CLOUD_SERVICES.md    ADF, Event Hubs, Stream Analytics, Purview, Power BI
│
├── DATABRICKS/
│   ├── DATA_PLATFORM/
│   │   └── DATABRICKS_DATA_PLATFORM.md  Lakehouse, Delta Lake, UniForm, Unity Catalog, DLT
│   └── CLOUD_SERVICE/
│       └── DATABRICKS_SERVICES.md     Spark, Streaming, MLflow, Mosaic AI, Delta Sharing
│
└── COMPARISON/
    ├── CROSS_CLOUD_COMPARISON.md      Side-by-side comparison tables across all platforms
    └── ARCHITECTURE_DECISION_GUIDE.md Platform selection framework + The1 reference architecture
```

---

## Quick Navigation by Topic

### Data Warehouse

| Topic | GCP | AWS | Azure | Databricks |
|-------|-----|-----|-------|------------|
| **Core warehouse** | [BigQuery](GCP/DATA_PLATFORM/GCP_DATA_PLATFORM.md#1-bigquery-core-data-warehouse) | [Redshift](AWS/DATA_PLATFORM/AWS_DATA_PLATFORM.md#1-amazon-redshift) | [Synapse/Fabric](AZURE/DATA_PLATFORM/AZURE_DATA_PLATFORM.md#1-azure-synapse-analytics) | [Databricks SQL](DATABRICKS/DATA_PLATFORM/DATABRICKS_DATA_PLATFORM.md#4-databricks-sql) |
| **CDC** | [Storage Write API](GCP/DATA_PLATFORM/GCP_DATA_PLATFORM.md#15-cdc-via-storage-write-api) | [Streaming Ingestion](AWS/DATA_PLATFORM/AWS_DATA_PLATFORM.md#14-key-features) | [Synapse Link](AZURE/DATA_PLATFORM/AZURE_DATA_PLATFORM.md#13-synapse-link-htap) | [Change Data Feed](DATABRICKS/DATA_PLATFORM/DATABRICKS_DATA_PLATFORM.md#22-key-features) |
| **Comparison** | [Warehouse Comparison](COMPARISON/CROSS_CLOUD_COMPARISON.md#2-data-warehouse-comparison) ||||

### Lakehouse & Open Formats

| Topic | GCP | AWS | Azure | Databricks |
|-------|-----|-----|-------|------------|
| **Lakehouse** | [BigLake](GCP/DATA_PLATFORM/GCP_DATA_PLATFORM.md#2-biglake-lakehouse) | [S3+Iceberg](AWS/DATA_PLATFORM/AWS_DATA_PLATFORM.md#2-data-lake--lakehouse-on-aws) | [OneLake](AZURE/DATA_PLATFORM/AZURE_DATA_PLATFORM.md#2-microsoft-fabric) | [Delta Lakehouse](DATABRICKS/DATA_PLATFORM/DATABRICKS_DATA_PLATFORM.md#1-lakehouse-architecture) |
| **Iceberg** | [BLMS REST Catalog](GCP/DATA_PLATFORM/GCP_DATA_PLATFORM.md#22-biglake-metastore-blms--iceberg-rest-catalog) | [S3 Tables + Glue](AWS/DATA_PLATFORM/AWS_DATA_PLATFORM.md#23-apache-iceberg-on-aws-strategic-direction) | [OneLake Serving](AZURE/DATA_PLATFORM/AZURE_DATA_PLATFORM.md#33-apache-iceberg-support) | [UniForm](DATABRICKS/DATA_PLATFORM/DATABRICKS_DATA_PLATFORM.md#3-delta-uniform-interoperability) |
| **Format comparison** | [Iceberg vs Delta vs Hudi](GCP/DATA_PLATFORM/GCP_DATA_PLATFORM.md#33-open-table-format-comparison) ||| [Delta vs Iceberg vs Hudi](DATABRICKS/DATA_PLATFORM/DATABRICKS_DATA_PLATFORM.md#23-delta-lake-vs-iceberg-vs-hudi) |

### Data Processing & Streaming

| Topic | GCP | AWS | Azure | Databricks |
|-------|-----|-----|-------|------------|
| **Processing** | [Dataflow](GCP/CLOUD_SERVICE/GCP_CLOUD_SERVICES.md#11-dataflow-managed-apache-beam) | [Glue/EMR](AWS/DATA_PLATFORM/AWS_DATA_PLATFORM.md#4-aws-glue) | [ADF](AZURE/CLOUD_SERVICE/AZURE_CLOUD_SERVICES.md#11-azure-data-factory-adf) | [Spark](DATABRICKS/CLOUD_SERVICE/DATABRICKS_SERVICES.md) |
| **Streaming** | [Pub/Sub](GCP/CLOUD_SERVICE/GCP_CLOUD_SERVICES.md#31-pubsub) | [Kinesis/MSK](AWS/CLOUD_SERVICE/AWS_CLOUD_SERVICES.md#1-streaming--messaging) | [Event Hubs](AZURE/CLOUD_SERVICE/AZURE_CLOUD_SERVICES.md#21-azure-event-hubs) | [Structured Streaming](DATABRICKS/CLOUD_SERVICE/DATABRICKS_SERVICES.md) |
| **Orchestration** | [Composer](GCP/CLOUD_SERVICE/GCP_CLOUD_SERVICES.md#21-cloud-composer-managed-airflow) | [MWAA](AWS/CLOUD_SERVICE/AWS_CLOUD_SERVICES.md#21-amazon-mwaa-managed-airflow) | [ADF](AZURE/CLOUD_SERVICE/AZURE_CLOUD_SERVICES.md#11-azure-data-factory-adf) | [Lakeflow Jobs](DATABRICKS/CLOUD_SERVICE/DATABRICKS_SERVICES.md) |

### Governance & Security

| Topic | GCP | AWS | Azure | Databricks |
|-------|-----|-----|-------|------------|
| **Governance** | [Dataplex](GCP/CLOUD_SERVICE/GCP_CLOUD_SERVICES.md#51-dataplex-universal-catalog) | [Lake Formation](AWS/CLOUD_SERVICE/AWS_CLOUD_SERVICES.md#31-aws-lake-formation) | [Purview](AZURE/CLOUD_SERVICE/AZURE_CLOUD_SERVICES.md#31-microsoft-purview) | [Unity Catalog](DATABRICKS/DATA_PLATFORM/DATABRICKS_DATA_PLATFORM.md#5-unity-catalog) |

### Decision Making

| Document | Description |
|----------|------------|
| [Cross-Cloud Comparison](COMPARISON/CROSS_CLOUD_COMPARISON.md) | Side-by-side tables: warehouse, lakehouse, processing, pricing, lock-in |
| [Architecture Decision Guide](COMPARISON/ARCHITECTURE_DECISION_GUIDE.md) | When to choose each platform, migration paths, The1 reference architecture |

---

## Key Insights Summary

### Platform Positioning (2026)

| Platform | Strategic Direction | Primary Format | Strengths |
|----------|-------------------|----------------|-----------|
| **GCP** | Iceberg-native lakehouse via BigLake | Apache Iceberg | Serverless, simplicity, cost-efficient |
| **AWS** | Iceberg-first via S3 Tables | Apache Iceberg | Breadth, flexibility, mature ecosystem |
| **Azure** | Delta-native via Fabric/OneLake | Delta Lake | Microsoft integration, Power BI, enterprise |
| **Databricks** | Delta + Iceberg interop via UniForm | Delta Lake | Multi-cloud, ML/AI, open governance |

### Industry Trends

1. **Open formats winning**: Iceberg and Delta converging; proprietary formats declining
2. **Lakehouse replacing warehouse+lake**: Single architecture for all analytics
3. **Serverless everywhere**: All platforms moving toward consumption-based pricing
4. **Governance is differentiator**: Unity Catalog, Dataplex, Lake Formation competing
5. **Multi-cloud is real but rare**: Most orgs are single-cloud; multi-cloud adds complexity
6. **AI/ML integration**: Every platform embedding ML capabilities into data platform

---

## How to Use This Knowledge Base

1. **New to a platform?** Start with the DATA_PLATFORM doc for that provider
2. **Comparing platforms?** Go to [COMPARISON/](COMPARISON/)
3. **Making a decision?** Use the [Architecture Decision Guide](COMPARISON/ARCHITECTURE_DECISION_GUIDE.md)
4. **Deep dive on a service?** Use the CLOUD_SERVICE docs
5. **Understanding our project?** See The1 reference in the Decision Guide
6. **Pricing questions?** Each DATA_PLATFORM doc has a cost summary section

---

> **Last Updated**: 2026-03-05
