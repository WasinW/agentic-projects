# Cross-Cloud Data Platform Comparison

> **Version**: 2.0 | **Created**: 2026-03-05 | **Maintainer**: Data Platform Team

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Data Warehouse Comparison](#2-data-warehouse-comparison)
3. [Lakehouse Comparison](#3-lakehouse-comparison)
4. [Data Processing Comparison](#4-data-processing-comparison)
5. [Orchestration Comparison](#5-orchestration-comparison)
6. [Streaming/Messaging Comparison](#6-streamingmessaging-comparison)
7. [Governance Comparison](#7-governance-comparison)
8. [Open Table Format Support](#8-open-table-format-support)
9. [Security Comparison](#9-security-comparison)
10. [Infrastructure as Code](#10-infrastructure-as-code)
11. [Pricing Comparison](#11-pricing-comparison)
12. [Lock-in Assessment](#12-lock-in-assessment)
13. [Known Issues per Platform](#13-known-issues-per-platform)
14. [Feature Gap Matrix](#14-feature-gap-matrix)
15. [References](#15-references)

---

## 1. Executive Summary

### Platform Strengths

| Platform | One-Line Summary | Sweet Spot |
|----------|-----------------|-----------|
| **GCP** | Best serverless warehouse (BigQuery) + strongest Iceberg-native lakehouse (BigLake/BLMS) | Serverless analytics, Beam streaming, Iceberg-first |
| **AWS** | Broadest service catalog + most mature ecosystem + strategic Iceberg bet (S3 Tables) | Maximum flexibility, Kafka-heavy, Spark workloads |
| **Azure** | Deep Microsoft integration (Fabric/Power BI/M365) + strongest enterprise SQL heritage | Microsoft shops, Power BI-centric, SQL Server migration |
| **Databricks** | Best open lakehouse (Delta/UniForm) + only true multi-cloud + best ML platform | Multi-cloud, ML/AI-first, complex Spark ETL |

### Quick Recommendation Matrix

| Use Case | Primary Recommendation | Secondary Option |
|----------|----------------------|-----------------|
| Serverless SQL analytics | **GCP (BigQuery)** | AWS (Redshift Serverless) |
| Complex streaming + batch | **GCP (Dataflow)** | Databricks (Structured Streaming) |
| Multi-cloud strategy | **Databricks** | (no close second) |
| Microsoft enterprise shop | **Azure (Fabric)** | Azure Databricks |
| Maximum flexibility / choice | **AWS** | GCP |
| ML/AI-first team | **Databricks** | GCP (Vertex AI + BQ ML) |
| Cost-sensitive, simple queries | **GCP (BigQuery on-demand)** | AWS (Athena) |
| Existing Spark workloads | **Databricks** | AWS (EMR) |
| Power BI-centric BI | **Azure (Fabric DirectLake)** | Azure Databricks |
| Open format commitment | **Databricks** | GCP (Iceberg/BLMS) |
| Real-time CDC pipelines | **GCP (Dataflow + BQ CDC)** | Databricks (DLT + CDF) |
| Data mesh / self-serve | **Databricks (Unity Catalog)** | GCP (Dataplex) |
| Legacy DW migration | **AWS (Redshift)** or **Azure (Synapse)** | GCP (BigQuery Migration) |
| IoT / edge analytics | **Azure (IoT Hub + Fabric)** | AWS (IoT Core + Kinesis) |

---

## 2. Data Warehouse Comparison

| Feature | BigQuery (GCP) | Redshift (AWS) | Synapse/Fabric (Azure) | Databricks SQL |
|---------|---------------|----------------|------------------------|----------------|
| **Architecture** | Dremel (serverless MPP) | MPP (leader + compute) | MPP (dedicated) / CU (Fabric) | Photon (vectorized Spark) |
| **Serverless** | Full (native) | Serverless option (RPU) | Serverless SQL pool / Fabric | Serverless warehouses |
| **Concurrency** | 100+ queries/project (slots) | 5-50 WLM queues + concurrency scaling | Varies by DWU/CU | Auto-scaling endpoints |
| **Max data** | Petabytes+ (no limit) | Petabytes (RA3 managed storage) | Petabytes | Petabytes |
| **Storage format** | Capacitor (internal) + Iceberg (external) | Columnar (internal) + Iceberg (S3 Tables) | Delta Lake (Fabric) | Delta Lake |
| **CDC** | Storage Write API (UPSERT/DELETE) | Streaming ingestion + MV refresh | Synapse Link / Fabric Mirroring | Delta Change Data Feed |
| **ML integration** | BQML (SQL-based, in-engine) | Redshift ML (→ SageMaker) | Limited in Fabric | MLflow, Mosaic AI, Feature Store |
| **Free tier** | 1 TB/month queries, 10 GB storage | 2-month trial (750 DC-hours) | $200 credits (30 days) | Community Edition (14-day) |
| **Pricing model** | Per TB scanned or flat-rate slots | Per node-hr or RPU-hr (Serverless) | DWU-hr (Synapse) or CU (Fabric) | DBU + cloud VM |
| **Open format** | Iceberg (BigLake) | Iceberg (S3 Tables, Spectrum) | Delta (OneLake) | Delta + UniForm (Iceberg) |
| **Multi-cloud query** | BigQuery Omni (limited GA) | No | No | Yes (native multi-cloud) |
| **Semi-structured** | JSON, STRUCT, ARRAY (native) | SUPER type (PartiQL) | JSON functions (T-SQL) | JSON, variant type |
| **Materialized views** | Auto-refresh | Manual/auto-refresh | Yes (Synapse Dedicated) | Yes (via DLT or manual) |
| **Result cache** | Automatic (free) | Automatic | Automatic | Automatic |
| **Data sharing** | Analytics Hub | Data Sharing (cross-account) | OneLake shortcuts / Data Share | Delta Sharing (open protocol) |

### Warehouse Performance Characteristics

| Workload | Best Platform | Why |
|----------|-------------|-----|
| **Ad-hoc SQL (100s of queries/day)** | BigQuery (on-demand) | Pay per query, no cluster management |
| **Sustained BI dashboards** | BigQuery (slots) or Redshift (RA3) | Predictable cost, cached results |
| **Complex multi-table joins** | Redshift (RA3) or Databricks SQL | MPP distribution optimization |
| **Concurrent mixed workloads** | Databricks SQL | Auto-scaling endpoints |
| **Real-time inserts + queries** | BigQuery (Storage Write API) | Sub-second append, immediate query |
| **Large-scale aggregations** | BigQuery or Databricks (Photon) | Columnar scan efficiency |

---

## 3. Lakehouse Comparison

| Feature | BigLake+Iceberg (GCP) | S3+Iceberg (AWS) | OneLake+Delta (Azure) | Delta Lake (Databricks) |
|---------|----------------------|-------------------|----------------------|------------------------|
| **Native format** | Iceberg | Iceberg | Delta Lake | Delta Lake |
| **Catalog** | BLMS REST Catalog | Glue Catalog (Iceberg REST) | OneLake | Unity Catalog (Iceberg REST) |
| **ACID** | Yes (Iceberg) | Yes (Iceberg) | Yes (Delta) | Yes (Delta) |
| **Time travel** | Yes (snapshot) | Yes (snapshot) | Yes (version) | Yes (version) |
| **Schema evolution** | Add/rename/drop columns | Add/rename/drop columns | Add/merge/overwrite schema | Add/merge/overwrite schema |
| **Partition evolution** | Hidden partitions (Iceberg) | Hidden partitions (Iceberg) | Hive-style only | Liquid Clustering (replaces partitioning) |
| **Multi-engine** | BigQuery, Spark, Flink, Trino | Athena, Redshift, EMR, Glue, Trino | Fabric, Synapse, Databricks | Spark, Flink, Trino, DuckDB, Presto |
| **Governance** | Dataplex + BigLake ACL | Lake Formation (row/column/cell/tag) | Purview + Fabric security | Unity Catalog (ABAC, row filters, masks) |
| **Cross-format** | Iceberg native (no conversion) | Iceberg native (no conversion) | Delta → Iceberg (transparent serving) | Delta → Iceberg (UniForm metadata) |
| **Compaction** | Auto (BigQuery managed) | Manual (Spark/Athena OPTIMIZE) | Manual (OPTIMIZE) | Auto (Predictive Optimization) |
| **Maturity** | Newer (BLMS GA 2024) | Mature (S3 Tables GA 2025) | New (Fabric GA Nov 2023) | Most mature (Delta Lake since 2019) |
| **Deletion vectors** | N/A (Iceberg uses position deletes) | N/A (Iceberg v2 equality deletes) | Yes (Delta) | Yes (Delta) |
| **Z-Order/clustering** | Clustering (BQ), partition transform (Iceberg) | Z-Order via Spark | Z-Order via Spark, Liquid Clustering | Z-Order, Liquid Clustering |

### Table Format Feature Comparison (Iceberg vs Delta)

| Feature | Apache Iceberg | Delta Lake |
|---------|---------------|------------|
| **Creator** | Netflix → Apache | Databricks → Linux Foundation |
| **Spec version** | v2 (position/equality deletes) | 3.x (deletion vectors, liquid clustering) |
| **Metadata** | manifest list → manifests → data | transaction log (JSON + Parquet checkpoint) |
| **Partition evolution** | Yes (hidden, no rewrite) | No (Liquid Clustering instead) |
| **Schema evolution** | Full (add/rename/drop/reorder) | Add/merge (rename via column mapping) |
| **MERGE performance** | Copy-on-write or merge-on-read | Deletion vectors (fast MoR) |
| **Multi-engine** | Excellent (Spark, Flink, Trino, Presto, DuckDB, Impala) | Good (Spark, Flink, Trino, DuckDB) |
| **Cloud-native catalogs** | BLMS (GCP), Glue (AWS), Unity (DB) | Unity (DB), OneLake (Azure) |
| **Interop** | Native in GCP/AWS | UniForm generates Iceberg metadata |
| **Industry direction** | Growing (GCP, AWS, Snowflake, Confluent bet) | Strong (Databricks, Azure, Spark ecosystem) |
| **Convergence** | Delta-Iceberg compatibility improving | UniForm v2 makes Delta readable as Iceberg |

---

## 4. Data Processing Comparison

| Feature | Dataflow (GCP) | Glue (AWS) | EMR (AWS) | Data Factory (Azure) | Spark (Databricks) |
|---------|---------------|-----------|-----------|---------------------|-------------------|
| **Engine** | Apache Beam | Apache Spark | Apache Spark | ADF + Spark (Mapping DF) | Apache Spark |
| **Serverless** | Yes (fully) | Yes | Serverless option | ADF: Yes, Spark: No | Serverless option |
| **Streaming** | Excellent (Beam) | Structured Streaming | Structured Streaming | Stream Analytics | Structured Streaming |
| **Batch** | Good | Excellent | Excellent | Good (Copy, Data Flow) | Excellent |
| **Auto-scaling** | Automatic (horizontal) | Auto (DPU) | Configurable | ADF: auto | Auto-scaling clusters |
| **Unified batch+stream** | Yes (Beam model) | Via Structured Streaming | Via Structured Streaming | Separate services | Via DLT or SS |
| **Iceberg write** | IcebergIO (managed.Write) | Spark native | Spark native | N/A (Delta native) | Delta + UniForm |
| **Pricing** | vCPU + memory/hr | DPU-hr ($0.44) | Instance-hr + spot | Activity runs + compute | DBU + VM |
| **Learning curve** | High (Beam SDK) | Medium (Spark + Glue API) | Medium (Spark) | Low (visual) | Medium (Spark) |
| **Cost at scale** | Medium | Lower (Spot friendly) | Lowest (Spot + Reserved) | Medium | Higher |
| **Talent pool** | Smallest (Beam niche) | Large (Spark) | Large (Spark) | Large (SQL/visual) | Large (Spark) |

### Processing Engine Decision Guide

```
Is unified batch + streaming critical?
├── YES → Do you have Beam expertise?
│   ├── YES → GCP Dataflow
│   └── NO → Databricks DLT or Spark Structured Streaming
└── NO (batch OR streaming separately)
    ├── Batch ETL:
    │   ├── Simple transforms → ADF (Azure) or Glue (AWS)
    │   ├── Complex Spark → Databricks or EMR
    │   └── SQL-based → dbt/Dataform on warehouse
    └── Streaming:
        ├── SQL on streams → Azure Stream Analytics
        ├── Complex event processing → Dataflow (Beam) or Flink
        └── Micro-batch OK → Spark Structured Streaming
```

---

## 5. Orchestration Comparison

| Feature | Cloud Composer (GCP) | MWAA (AWS) | Data Factory (Azure) | Lakeflow Jobs (Databricks) |
|---------|---------------------|-----------|---------------------|---------------------------|
| **Engine** | Apache Airflow 2.x / 3.x | Apache Airflow 2.x | Proprietary | Proprietary |
| **Serverless** | Composer 3 (DCU-based) | No (managed env) | Yes | Yes |
| **DAG authoring** | Python (Airflow) | Python (Airflow) | JSON/YAML (visual) | Python/YAML (visual) |
| **Pricing** | ~$400-2,000+/mo | ~$360-1,400+/mo | Per activity run | Included in DBU |
| **Visual designer** | Airflow UI (graph) | Airflow UI (graph) | Yes (drag-and-drop) | Yes (DAG view) |
| **Integration** | GCP services (native operators) | AWS services (native operators) | Azure + M365 + 150 connectors | Databricks ecosystem |
| **Lock-in** | Low (Airflow portable) | Low (Airflow portable) | High (ADF-specific JSON) | High (Databricks-specific) |
| **Monitoring** | Airflow UI + Cloud Monitoring | Airflow UI + CloudWatch | ADF Monitor + Azure Monitor | Lakeflow Monitor |
| **Git integration** | Yes (DAGs in GCS/repo) | Yes (DAGs in S3/repo) | Azure DevOps, GitHub | Repos, Git folders |
| **Max concurrent tasks** | Depends on env size | Depends on env size | ~80 per pipeline | Depends on cluster |
| **Retry/alerting** | Airflow native | Airflow native | Built-in | Built-in |
| **Cross-cloud** | Via Airflow operators | Via Airflow operators | Limited | Native (multi-cloud) |

### Orchestration Decision Flowchart

```
Do you need Airflow specifically?
├── YES → Which cloud?
│   ├── GCP → Cloud Composer (Composer 3 for serverless)
│   ├── AWS → MWAA
│   └── Azure → Self-managed or ADF (different paradigm)
└── NO
    ├── Visual/low-code → Azure Data Factory
    ├── Databricks-centric → Lakeflow Jobs (Workflows)
    ├── Simple scheduling → Cloud Scheduler (GCP) / EventBridge (AWS)
    └── Step-based workflows → AWS Step Functions
```

---

## 6. Streaming/Messaging Comparison

| Feature | Pub/Sub (GCP) | Kinesis (AWS) | MSK (AWS) | Event Hubs (Azure) | Confluent Cloud |
|---------|-------------|-------------|-----------|-------------------|-----------------|
| **Type** | Serverless messaging | Managed streaming | Managed Kafka | Kafka-compatible streaming | Managed Kafka |
| **Protocol** | gRPC, REST | REST, KCL | Kafka native | AMQP, Kafka, HTTPS | Kafka native |
| **Latency** | ~100ms | ~200ms | ~10ms | ~ms | ~10ms |
| **Ordering** | Per ordering key | Per shard | Per partition | Per partition | Per partition |
| **Throughput** | Unlimited (auto) | Per shard (1 MB/s in) | Per broker | Per TU/PU | Per CKU |
| **Retention** | 31 days (default, configurable) | 1-365 days | Unlimited (tiered storage) | 1-90 days | Infinite (tiered) |
| **Replay** | Seek to timestamp | Trim horizon / timestamp | Offset / timestamp | Offset / timestamp | Offset / timestamp |
| **Schema** | Pub/Sub schemas | Glue Schema Registry | Glue Schema Registry | Event Hubs Schema Registry | Confluent Schema Registry |
| **Serverless** | Yes (fully) | Yes | Serverless option | Standard (TU-based) | Yes (basic/standard) |
| **Multi-cloud** | No | No | No | No | Yes |
| **Exactly-once** | With Dataflow | KCL dedup | Kafka transactions | Consumer managed | Kafka transactions |
| **Dead letter** | Dead-letter topic | Lambda DLQ | Topic-based | Storage-based | Topic-based |
| **Cost model** | Per message + storage | Per shard-hr + data | Per broker-hr + storage | Per TU-hr + data | Per CKU-hr + data |

### When to Use What

| Scenario | Best Choice | Why |
|----------|-----------|-----|
| GCP-native, serverless | Pub/Sub | Zero-ops, auto-scaling |
| Existing Kafka ecosystem | MSK or Confluent | Protocol compatibility |
| Azure + Kafka clients | Event Hubs (Kafka endpoint) | Kafka protocol, Azure integration |
| Multi-cloud Kafka | Confluent Cloud | Same platform on any cloud |
| Simple event routing | Event Grid (Azure) or EventBridge (AWS) | Serverless, low-code |
| High-throughput CDC | MSK or Confluent | Kafka Connect ecosystem |
| IoT telemetry | Pub/Sub (GCP) or Kinesis (AWS) | Managed, auto-scale |

---

## 7. Governance Comparison

| Feature | Dataplex (GCP) | Lake Formation (AWS) | Purview (Azure) | Unity Catalog (Databricks) |
|---------|---------------|---------------------|-----------------|---------------------------|
| **Focus** | Quality + discovery + zones | Fine-grained access control | Governance + compliance + lineage | Unified governance + sharing |
| **Access control** | IAM + BigLake ACL | Row/column/cell security + LF-Tags | Sensitivity labels + RBAC | ABAC + row filters + column masks |
| **Lineage** | Yes (visual, from Dataflow/BQ) | No (DataZone for discovery) | Yes (visual, from ADF/Synapse) | Yes (automated, column-level) |
| **Classification** | Auto (DLP API + profiling) | Manual (or Macie integration) | Auto (200+ classifiers, sensitivity) | Auto (tags + profiling) |
| **Multi-cloud** | No | No | Yes (scan S3, GCS, Snowflake) | Yes (native multi-cloud) |
| **Catalog** | Dataplex Universal Catalog | Glue Data Catalog | Purview Data Map + Catalog | Unity Catalog |
| **Cost** | Free + BQ compute | Free | Capacity-based (~$0.413/CU/hr) | Included in Premium tier |
| **Open standard** | No (GCP-specific) | Hive Metastore compatible | No (Purview-specific) | Iceberg REST Catalog |
| **Data quality** | Auto-quality rules (profiling) | Glue Data Quality (DQDL) | Purview Data Quality (Preview) | Expectations (DLT), Lakehouse Monitoring |
| **Data products** | Dataplex data products | DataZone business catalog | Purview business glossary | Unity Catalog + Delta Sharing |
| **Business glossary** | Dataplex business glossary | DataZone glossary | Purview business glossary | Unity Catalog tags |

---

## 8. Open Table Format Support

| Feature | GCP | AWS | Azure | Databricks |
|---------|-----|-----|-------|------------|
| **Iceberg** | Native (BigLake BLMS REST) | Native (S3 Tables, Glue REST) | Via OneLake Iceberg serving | Via UniForm (Delta → Iceberg) |
| **Delta Lake** | BigLake (read), Dataproc (read/write) | Glue, EMR, Athena (read) | Native (OneLake, Fabric) | Native (primary format) |
| **Hudi** | Dataproc (limited) | EMR, Glue 4.0+ | Limited | Limited |
| **Catalog standard** | Iceberg REST Catalog (BLMS) | Iceberg REST (Glue) | OneLake APIs (proprietary) | Iceberg REST (Unity Catalog) |
| **Interop approach** | Iceberg-first | Iceberg-first | Delta-first + Iceberg serving | Delta-first + UniForm |
| **Cross-format** | Iceberg ↔ Delta via XTable | Iceberg ↔ Delta via XTable | Delta → Iceberg (transparent) | Delta → Iceberg (UniForm v2) |

### Industry Direction

```
                    Format Adoption Trajectory (2024-2026)

Adoption    ▲
            │   ╱── Iceberg ──────────────── Converging
            │  ╱    (GCP, AWS, Snowflake,    with Delta
            │ ╱      Confluent)
            │╱
            │ ╲
            │  ╲── Delta ────────────────── UniForm provides
            │   ╲   (Databricks, Azure,      Iceberg interop
            │    ╲   Spark ecosystem)
            │
            │     ╲── Hudi ─────────── Declining adoption
            │      ╲
            └──────────────────────────────────▶ Time
              2024    2025    2026    2027
```

**Key trends:**
- Iceberg and Delta are converging via UniForm and XTable
- Hudi adoption declining — most new projects choose Iceberg or Delta
- GCP and AWS bet on Iceberg natively; Azure and Databricks bet on Delta with Iceberg interop
- Iceberg REST Catalog becoming de facto standard for catalog interoperability
- Unity Catalog and BLMS both implement Iceberg REST Catalog spec

---

## 9. Security Comparison

| Feature | GCP | AWS | Azure | Databricks |
|---------|-----|-----|-------|------------|
| **Identity** | Google IAM + Workforce Identity | IAM + SSO + Organizations | Entra ID (Azure AD) | SCIM + SSO (via cloud IdP) |
| **Secrets** | Secret Manager | Secrets Manager | Key Vault | Secret scopes (backed by cloud) |
| **Encryption at rest** | Default (GMEK), CMEK, CSEK | Default (SSE-S3), KMS, CloudHSM | Default (Microsoft-managed), CMK | Inherits cloud encryption |
| **Encryption in transit** | TLS 1.2+ (default) | TLS 1.2+ | TLS 1.2+ | TLS 1.2+ |
| **Network isolation** | VPC, Private Google Access, VPC-SC | VPC, PrivateLink, VPC Endpoints | VNet, Private Endpoints, Service Endpoints | VNet injection, Private Link |
| **Row/column security** | BigLake ACL, BQ row/column | Lake Formation (row/column/cell) | Purview sensitivity + RLS | Unity Catalog (row filters, column masks) |
| **Audit logging** | Cloud Audit Logs | CloudTrail | Azure Monitor + Diagnostic Logs | Unity Catalog audit logs |
| **Compliance** | SOC 1/2/3, ISO, FedRAMP, HIPAA | SOC 1/2/3, ISO, FedRAMP, HIPAA, GovCloud | SOC 1/2/3, ISO, FedRAMP, HIPAA, Government | SOC 2, ISO, HIPAA (via cloud) |
| **Data residency** | Regional/multi-regional | Regional | Regional | Inherits cloud region |

---

## 10. Infrastructure as Code

| Feature | GCP | AWS | Azure | Databricks |
|---------|-----|-----|-------|------------|
| **Terraform** | google provider (mature) | aws provider (most mature) | azurerm provider (mature) | databricks provider (mature) |
| **Native IaC** | Deployment Manager (legacy) | CloudFormation, CDK | ARM Templates, Bicep | Terraform + REST APIs |
| **Pulumi** | Yes | Yes | Yes | Yes |
| **CLI** | gcloud | aws cli | az cli | databricks cli |
| **SDK** | Python, Java, Go, Node.js | Python (boto3), Java, Go, .NET | Python, Java, .NET, Go | Python, Java, Go |
| **GitOps** | Config Connector (K8s) | Controllers for K8s | Azure Arc | Repos + Git folders |
| **State management** | GCS backend | S3 backend | Azure Storage backend | Via cloud backend |

### Terraform Provider Comparison

```hcl
# GCP: Create BigQuery dataset + table
resource "google_bigquery_dataset" "refined" {
  dataset_id = "refined"
  location   = "asia-southeast1"
}

# AWS: Create Glue database + S3 bucket
resource "aws_glue_catalog_database" "refined" {
  name = "refined"
}

# Azure: Create Synapse workspace
resource "azurerm_synapse_workspace" "analytics" {
  name                = "syn-analytics"
  resource_group_name = azurerm_resource_group.rg.name
  location            = "southeastasia"
}

# Databricks: Create Unity Catalog schema
resource "databricks_schema" "refined" {
  catalog_name = databricks_catalog.main.name
  name         = "refined"
}
```

---

## 11. Pricing Comparison

### 11.1 Small Team (10 users, 1 TB, ~100 queries/day)

| Component | GCP | AWS | Azure | Databricks |
|-----------|-----|-----|-------|------------|
| **Storage** | ~$20/mo (GCS Standard) | ~$24/mo (S3 Standard) | ~$18/mo (ADLS Hot) | ~$20/mo (cloud storage) |
| **Compute** | ~$0-200/mo (BQ on-demand) | ~$250/mo (Redshift Serverless) | ~$263/mo (Fabric F2) | ~$300/mo (SQL Warehouse) |
| **Orchestration** | ~$0 (Cloud Scheduler) | ~$0 (EventBridge) | ~$5/mo (ADF) | ~$0 (included) |
| **Streaming** | ~$50/mo (Pub/Sub) | ~$50/mo (Kinesis) | ~$50/mo (Event Hubs Basic) | ~$100/mo (SS cluster) |
| **BI** | ~$0 (Looker Studio free) | ~$0 (QuickSight free tier) | ~$100/mo (10×Pro) | ~$100/mo (external BI) |
| **Total** | **~$70-270/mo** | **~$325-450/mo** | **~$436-536/mo** | **~$520-620/mo** |
| **Notes** | BQ free tier covers most queries | No free tier for Serverless | Fabric F2 is minimum viable | SQL Warehouse auto-suspend helps |

### 11.2 Medium Enterprise (50 users, 50 TB, ~1,000 queries/day)

| Component | GCP | AWS | Azure | Databricks |
|-----------|-----|-----|-------|------------|
| **Storage** | ~$1,000/mo | ~$1,200/mo | ~$900/mo | ~$1,000/mo |
| **Compute** | ~$3-5K/mo (slots) | ~$3-6K/mo (RA3/Serverless) | ~$8,400/mo (Fabric F64) | ~$4-8K/mo (SQL+Jobs) |
| **ETL** | ~$1-2K/mo (Dataflow) | ~$1.5-3K/mo (Glue) | Included in Fabric CU | ~$2-4K/mo (Jobs clusters) |
| **Streaming** | ~$500-1K/mo (Pub/Sub+Dataflow) | ~$500-1.5K/mo (MSK) | Included in Fabric CU | ~$1-2K/mo (SS) |
| **Governance** | ~$0 (Dataplex free) | ~$0 (Lake Formation free) | ~$500/mo (Purview) | Included in Premium |
| **BI** | ~$300/mo (Looker) | ~$500/mo (QuickSight) | Included (Power BI in F64) | ~$500/mo (external BI) |
| **Total** | **~$6-9K/mo** | **~$7-12K/mo** | **~$10-12K/mo** | **~$9-16K/mo** |

### 11.3 Large Enterprise (200+ users, 500 TB+, streaming + batch)

| Component | GCP | AWS | Azure | Databricks |
|-----------|-----|-----|-------|------------|
| **Total** | **~$35-65K/mo** | **~$47-88K/mo** | **~$34-73K/mo** | **~$50-100K/mo** |
| **With RI/CUD** | **~$25-45K/mo** | **~$30-55K/mo** | **~$25-50K/mo** | **~$35-65K/mo** |
| **Notes** | Best cost at scale (flat-rate slots) | Most flexible, most complex billing | Fabric CU discounts at scale | Highest compute, unified platform |

### 11.4 Cost Optimization Levers

| Optimization | GCP | AWS | Azure | Databricks |
|-------------|-----|-----|-------|------------|
| **Reserved pricing** | 1yr CUD: ~30%, 3yr: ~50% (slots) | 1yr RI: ~37%, 3yr: ~65% | 1yr: ~20-25%, 3yr: ~35-40% | DBCU: ~20-37% |
| **Spot/preemptible** | Preemptible VMs (Dataproc) | Spot Instances (EMR/EKS) | Spot VMs (Databricks) | Spot workers (Jobs clusters) |
| **Auto-pause** | BQ (no idle cost) | Redshift Serverless | Fabric capacity pause/resume | SQL Warehouse auto-stop |
| **Tiered storage** | GCS (Standard→Nearline→Coldline→Archive) | S3 (Standard→IA→Glacier) | ADLS (Hot→Cool→Cold→Archive) | Cloud storage tiers |
| **Query optimization** | Partitioning + clustering | Sort keys + dist keys | Partition + distribution | Liquid clustering + Z-Order |

---

## 12. Lock-in Assessment

| Dimension | GCP | AWS | Azure | Databricks |
|-----------|-----|-----|-------|------------|
| **Data portability** | Medium-High (Iceberg on GCS) | High (Iceberg on S3) | Medium (Delta on ADLS) | High (Delta+Iceberg on any cloud) |
| **Code portability** | Medium (Beam open but niche) | Medium (Spark portable, services not) | Low (T-SQL gaps, ADF proprietary) | High (Spark, SQL standard) |
| **Skill portability** | Medium (BQ SQL partially standard) | Medium-High (Spark, SQL broadly used) | Medium (SQL Server skills transfer) | High (Spark, Python, SQL universal) |
| **Migration out** | Medium (BQ → Iceberg export) | Medium (many services to replace) | Medium-High (Fabric ecosystem) | Low-Medium (data is open format) |
| **Vendor dependency** | High (BQ proprietary), Low (Iceberg layer) | Medium (many proprietary services) | High (Fabric + Power BI ecosystem) | Medium (operational dependency) |
| **Multi-cloud** | No (Omni very limited) | No | No | Yes (native, same API) |

### Lock-in Risk Matrix

```
Lock-in Risk:    LOW ←──────────────────────────────────→ HIGH

Data Format:     [Iceberg/Delta on cloud storage]  ←→  [Proprietary format]
                 Databricks, GCP, AWS                   (none currently)

Compute Engine:  [Standard Spark/SQL]              ←→  [Proprietary engine]
                 Databricks, EMR                        BigQuery, Fabric, ADF

Catalog:         [Iceberg REST Catalog]            ←→  [Proprietary catalog]
                 Databricks UC, GCP BLMS, Glue REST     OneLake, ADF metadata

BI Layer:        [Open BI tools]                   ←→  [Vendor-specific BI]
                 Tableau, Looker, custom                DirectLake (Fabric-only)

Orchestration:   [Apache Airflow]                  ←→  [Proprietary workflow]
                 Composer, MWAA                         ADF, Lakeflow Jobs
```

### Verdict

1. **Lowest lock-in**: Databricks (multi-cloud, open formats, open compute, open catalog)
2. **Moderate**: AWS (broad open-source support but many proprietary services to integrate)
3. **Moderate-high**: GCP (BigQuery is proprietary but Iceberg layer mitigates)
4. **Highest risk**: Azure (Fabric is new proprietary stack, deep ecosystem tie-in, Delta-only native)

---

## 13. Known Issues per Platform

### GCP

| Issue | Severity | Impact |
|-------|----------|--------|
| BLMS REST Catalog maturity | Medium | PyIceberg compatibility issues, some operations unsupported |
| BigQuery SQL proprietary extensions | Medium | GoogleSQL differs from ANSI SQL in some areas |
| Smaller ecosystem and community | Low | Fewer third-party integrations, smaller talent pool |
| Apache Beam talent scarcity | Medium | Harder to hire Beam developers than Spark |
| Dataform limited to BigQuery | Low | Cannot use Dataform for non-BQ transformations |
| Cloud Composer cost | Medium | Expensive for simple scheduling needs |

### AWS

| Issue | Severity | Impact |
|-------|----------|--------|
| **Service fragmentation** | **High** | Too many overlapping services — biggest concern |
| Decision fatigue | High | EMR vs Glue vs Athena vs Redshift — when to use which? |
| Cost unpredictability | Medium | Multiple billing models across 10+ data services |
| Redshift Python UDF deprecation | Medium | June 2026 deadline, requires migration to Lambda UDF |
| S3 Tables (Iceberg) still new | Low | GA but ecosystem integration still growing |
| Lake Formation complexity | Medium | Fine-grained security setup is complex |

### Azure

| Issue | Severity | Impact |
|-------|----------|--------|
| **Fabric maturity gaps** | **High** | T-SQL incomplete, security preview, CI/CD gaps |
| Synapse retirement uncertainty | Medium | Component-by-component retirement hard to track |
| Delta-only native format | Medium | Iceberg is serving layer, not native |
| Cost complexity | Medium | Multi-dimensional billing (CU, DWU, activities, storage) |
| OneLake storage premium | Low | ~28% more expensive than raw ADLS Gen2 |
| Fewer connectors than ADF | Medium | Some enterprise sources not supported in Fabric |

### Databricks

| Issue | Severity | Impact |
|-------|----------|--------|
| **Cost at scale** | **High** | Consistently most expensive option across all tiers |
| DBU pricing complexity | Medium | Different rates per workload type, hard to predict |
| Operational lock-in | Medium | Unity Catalog, Workflows, Model Serving create dependency |
| Learning curve | Medium | Non-Spark teams need significant ramp-up |
| Overkill for simple analytics | Low | Over-engineered for simple SQL dashboard use cases |

---

## 14. Feature Gap Matrix

Shows which platform is **best** (B), **good** (G), **adequate** (A), or **missing/weak** (W):

| Feature | GCP | AWS | Azure | Databricks |
|---------|-----|-----|-------|------------|
| **Serverless SQL** | **B** | G | A | G |
| **Managed Kafka** | W | **B** | G | A |
| **Managed Airflow** | G | G | W | W |
| **Visual ETL** | A | G | **B** | A |
| **ML platform** | G | G | A | **B** |
| **BI integration** | A | A | **B** | A |
| **Multi-cloud** | W | W | W | **B** |
| **Data governance** | G | G | G | **B** |
| **Iceberg support** | **B** | **B** | A | G |
| **Delta support** | A | A | **B** | **B** |
| **Streaming** | **B** | G | G | G |
| **Cost efficiency** | **B** | G | G | A |
| **Enterprise compliance** | G | **B** | **B** | G |
| **Open source** | G | G | A | **B** |
| **Ecosystem size** | A | **B** | G | G |

---

## 15. References

### Platform-Specific Documentation
- [GCP Data Platform](../GCP/DATA_PLATFORM/GCP_DATA_PLATFORM.md) | [GCP Cloud Services](../GCP/CLOUD_SERVICE/GCP_CLOUD_SERVICES.md)
- [AWS Data Platform](../AWS/DATA_PLATFORM/AWS_DATA_PLATFORM.md) | [AWS Cloud Services](../AWS/CLOUD_SERVICE/AWS_CLOUD_SERVICES.md)
- [Azure Data Platform](../AZURE/DATA_PLATFORM/AZURE_DATA_PLATFORM.md) | [Azure Cloud Services](../AZURE/CLOUD_SERVICE/AZURE_CLOUD_SERVICES.md)
- [Databricks Data Platform](../DATABRICKS/DATA_PLATFORM/DATABRICKS_DATA_PLATFORM.md) | [Databricks Services](../DATABRICKS/CLOUD_SERVICE/DATABRICKS_SERVICES.md)

### Cross-Platform Analysis
- [Top Data Warehouse Platforms Compared — godatawarehouse.com](https://godatawarehouse.com/top-data-warehouse-platforms-compared-costs-use-cases/)
- [Databricks Competitors — Label Your Data](https://labelyourdata.com/articles/databricks-competitors)
- [BigQuery Competitors — Improvado](https://improvado.io/blog/bigquery-competitors)
- [Cloud Data Warehouse Comparison — Mastech Digital](https://www.mastechdigital.com/blogs/cloud-data-warehouse-comparison)
- [How Cloud Data Warehouses Bill You — ClickHouse](https://clickhouse.com/blog/how-cloud-data-warehouses-bill-you)
- [2025-2026 Lakehouse Ecosystem Guide — DEV Community](https://dev.to/alexmercedcoder/the-2025-2026-ultimate-guide-to-the-data-lakehouse-and-the-data-lakehouse-ecosystem-dig)
- [Data Warehouse TCO — MotherDuck](https://motherduck.com/learn-more/data-warehouse-tco/)
- [Iceberg vs Delta vs Hudi — Dremio](https://www.dremio.com/blog/apache-iceberg-vs-delta-lake-vs-apache-hudi/)
- [Table Format Comparison — Onehouse](https://www.onehouse.ai/blog/apache-hudi-vs-delta-lake-vs-apache-iceberg-lakehouse-feature-comparison)
- [Cloud Cost Comparison — InfoWorld](https://www.infoworld.com/article/3684254/comparing-cloud-data-warehouse-costs.html)

---

> **Document Version**: 2.0 | **Last Updated**: 2026-03-05
