# Azure Data Platform: Synapse, Fabric & Lakehouse

> **Version**: 2.0 | **Created**: 2026-03-05 | **Maintainer**: Data Platform Team

## Table of Contents

1. [Azure Synapse Analytics](#1-azure-synapse-analytics)
2. [Microsoft Fabric](#2-microsoft-fabric)
3. [DirectLake Deep Dive](#3-directlake-deep-dive)
4. [Data Lake / Lakehouse](#4-data-lake--lakehouse)
5. [Delta Lake Operations](#5-delta-lake-operations)
6. [Apache Iceberg on Azure](#6-apache-iceberg-on-azure)
7. [Azure Databricks on Azure](#7-azure-databricks-on-azure)
8. [Limitations and Known Issues](#8-limitations-and-known-issues)
9. [Cost Summary](#9-cost-summary)
10. [References](#10-references)

---

## 1. Azure Synapse Analytics

### 1.1 Architecture

Synapse Analytics combines multiple analytics runtimes under one roof:

```
┌───────────────────────────────────────────────────────────────────────┐
│                    Azure Synapse Analytics                            │
│                                                                       │
│  ┌──────────────────┐  ┌────────────────┐  ┌───────────────────────┐ │
│  │ Dedicated SQL    │  │ Serverless SQL │  │ Apache Spark Pool     │ │
│  │ Pool (MPP)       │  │ Pool           │  │                       │ │
│  │                  │  │                │  │ Spark 3.4 Runtime     │ │
│  │ T-SQL (full DML) │  │ OPENROWSET    │  │ PySpark / Scala / R   │ │
│  │ DWU-based        │  │ CETAS          │  │ SparkML, Delta Lake   │ │
│  │ Distributions    │  │ Per-TB scan    │  │ Notebooks + Jobs      │ │
│  │ Materialized     │  │ CSV/Parquet/   │  │ vCore-based pricing   │ │
│  │ Views, Indexes   │  │ JSON/Delta     │  │                       │ │
│  └────────┬─────────┘  └───────┬────────┘  └───────────┬───────────┘ │
│           │                    │                        │             │
│           └────────────────────┼────────────────────────┘             │
│                                │                                      │
│                  ┌─────────────▼──────────────┐                      │
│                  │       ADLS Gen2            │                      │
│                  │   (Unified Data Lake)      │                      │
│                  │   Parquet / Delta / CSV    │                      │
│                  └────────────────────────────┘                      │
│                                                                       │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────────────────┐ │
│  │ Synapse      │  │ Synapse Link  │  │ Synapse Studio            │ │
│  │ Pipelines    │  │ (HTAP)        │  │ (Unified workspace)       │ │
│  │ (ADF-based)  │  │ Cosmos DB     │  │ SQL + Spark + Pipelines   │ │
│  │ 90+ sources  │  │ SQL Server    │  │ Monitor + Manage          │ │
│  └──────────────┘  └───────────────┘  └────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────┘
```

### 1.2 Dedicated SQL Pool (MPP)

#### Architecture Details

The Dedicated SQL Pool uses a Massively Parallel Processing (MPP) architecture:

```
┌─────────────────────────────┐
│       Control Node          │
│  (Query optimizer, GMS)     │
│  T-SQL parsing, planning    │
└──────────┬──────────────────┘
           │ Distribute queries
    ┌──────┼──────┐
    ▼      ▼      ▼
┌──────┐┌──────┐┌──────┐
│Comp 1││Comp 2││Comp N│  ← Compute Nodes
│      ││      ││      │    (1-60 per DWU level)
│ D1 D2││ D1 D2││ D1 D2│  ← Distributions (60 total)
└──────┘└──────┘└──────┘
    │      │      │
    ▼      ▼      ▼
  Azure Storage (data files)
```

**60 Distributions**: Data is always split into 60 distributions regardless of compute nodes.

#### Distribution Types

```sql
-- HASH distribution: Best for large fact tables (joins/aggregations)
CREATE TABLE dbo.FactSales
WITH (
    DISTRIBUTION = HASH(CustomerKey),
    CLUSTERED COLUMNSTORE INDEX
)
AS SELECT * FROM staging.Sales;

-- ROUND_ROBIN distribution: Best for staging/temp tables (even spread)
CREATE TABLE dbo.StagingOrders
WITH (
    DISTRIBUTION = ROUND_ROBIN,
    HEAP
)
AS SELECT * FROM external_source.Orders;

-- REPLICATE distribution: Best for small dimension tables (<2GB)
CREATE TABLE dbo.DimProduct
WITH (
    DISTRIBUTION = REPLICATE,
    CLUSTERED COLUMNSTORE INDEX
)
AS SELECT * FROM staging.Products;
```

**Distribution selection guide:**

| Table Size | Join Pattern | Recommendation |
|-----------|-------------|----------------|
| < 2 GB | Frequently joined | REPLICATE |
| < 2 GB | Not joined | ROUND_ROBIN |
| > 2 GB | No clear join key | ROUND_ROBIN |
| > 2 GB | Known join/group key | HASH(key) |

#### DWU (Data Warehouse Unit) Sizing

| DWU Level | Compute Nodes | Distributions/Node | Memory/Node | Max Concurrent Queries | Approximate $/hr |
|-----------|--------------|--------------------|-----------|-----------------------|-------------------|
| DW100c | 1 | 60 | 60 GB | 4 | ~$1.20 |
| DW200c | 1 | 60 | 60 GB | 8 | ~$2.40 |
| DW500c | 1 | 60 | 60 GB | 20 | ~$6.00 |
| DW1000c | 2 | 30 | 60 GB | 32 | ~$12.00 |
| DW2000c | 4 | 15 | 60 GB | 32 | ~$24.00 |
| DW5000c | 10 | 6 | 60 GB | 32 | ~$60.00 |
| DW10000c | 20 | 3 | 60 GB | 32 | ~$120.00 |
| DW30000c | 60 | 1 | 60 GB | 128 | ~$360.00 |

**Pause/Resume**: Dedicated pools can be paused to stop billing (compute only; storage always billed).

```bash
# Pause a SQL pool
az synapse sql pool pause \
  --name mySqlPool \
  --workspace-name myWorkspace \
  --resource-group myRG

# Resume a SQL pool
az synapse sql pool resume \
  --name mySqlPool \
  --workspace-name myWorkspace \
  --resource-group myRG

# Scale up/down
az synapse sql pool update \
  --name mySqlPool \
  --workspace-name myWorkspace \
  --resource-group myRG \
  --performance-level DW1000c
```

#### Materialized Views

```sql
-- Create a materialized view for common aggregation
CREATE MATERIALIZED VIEW dbo.MV_DailySalesSummary
WITH (DISTRIBUTION = HASH(StoreKey))
AS
SELECT
    StoreKey,
    CAST(SaleDate AS DATE) AS SaleDate,
    SUM(SalesAmount) AS TotalSales,
    COUNT_BIG(*) AS RowCount
FROM dbo.FactSales
GROUP BY StoreKey, CAST(SaleDate AS DATE);

-- Check refresh status
SELECT
    name,
    is_expanded,
    has_unchecked_data  -- TRUE = needs refresh
FROM sys.pdw_materialized_view_mappings AS mv
JOIN sys.objects AS o ON mv.object_id = o.object_id;

-- Refresh manually (auto-refresh happens at query time if data is stale)
ALTER MATERIALIZED VIEW dbo.MV_DailySalesSummary REBUILD;
```

#### Row-Level Security (RLS) and Column-Level Security (CLS)

```sql
-- Row-Level Security: Sales reps see only their data
CREATE SCHEMA Security;

CREATE FUNCTION Security.fn_SalesFilter(@SalesRep AS NVARCHAR(128))
RETURNS TABLE
WITH SCHEMABINDING
AS RETURN
    SELECT 1 AS result
    WHERE @SalesRep = USER_NAME()
       OR USER_NAME() = 'DataAdmin';

CREATE SECURITY POLICY SalesFilter
ADD FILTER PREDICATE Security.fn_SalesFilter(SalesRepName)
ON dbo.FactSales
WITH (STATE = ON);

-- Column-Level Security: Grant access to specific columns only
GRANT SELECT ON dbo.Customers
    (CustomerName, Email, City, Country)
    TO [AnalystRole];
-- Sensitive columns (SSN, Phone) excluded
```

#### System DMVs for Monitoring

```sql
-- Active and recent queries
SELECT
    request_id,
    status,
    submit_time,
    start_time,
    total_elapsed_time / 1000.0 AS elapsed_sec,
    resource_class,
    command
FROM sys.dm_pdw_exec_requests
WHERE status NOT IN ('Completed', 'Failed', 'Cancelled')
ORDER BY submit_time DESC;

-- Data movement operations (shuffles)
SELECT
    request_id,
    type AS movement_type,
    status,
    start_time,
    total_elapsed_time / 1000.0 AS elapsed_sec,
    bytes_processed / (1024*1024.0) AS mb_processed
FROM sys.dm_pdw_dms_workers
WHERE request_id = 'QID12345'
ORDER BY start_time;

-- Distribution skew detection
SELECT
    tb.name AS table_name,
    nps.row_count,
    CAST(nps.reserved_page_count * 8.0 / 1024 AS DECIMAL(10,2)) AS size_mb
FROM sys.tables AS tb
INNER JOIN sys.pdw_table_mappings AS mp ON tb.object_id = mp.object_id
INNER JOIN sys.pdw_nodes_tables AS nt ON mp.physical_name = nt.name
INNER JOIN sys.dm_pdw_nodes_db_partition_stats AS nps
    ON nt.object_id = nps.object_id AND nt.pdw_node_id = nps.pdw_node_id
WHERE tb.name = 'FactSales'
ORDER BY nps.row_count DESC;

-- Concurrency and resource usage
SELECT
    resource_class,
    COUNT(*) AS active_queries,
    SUM(total_elapsed_time) / 1000.0 AS total_elapsed_sec
FROM sys.dm_pdw_exec_requests
WHERE status = 'Running'
GROUP BY resource_class;
```

### 1.3 Serverless SQL Pool

On-demand query engine over files in ADLS Gen2 — no provisioned resources.

#### OPENROWSET

```sql
-- Query Parquet files directly
SELECT TOP 100 *
FROM OPENROWSET(
    BULK 'https://myaccount.dfs.core.windows.net/raw/events/year=2026/month=03/*.parquet',
    FORMAT = 'PARQUET'
) AS events;

-- Query CSV with explicit schema
SELECT *
FROM OPENROWSET(
    BULK 'https://myaccount.dfs.core.windows.net/raw/customers/*.csv',
    FORMAT = 'CSV',
    PARSER_VERSION = '2.0',
    HEADER_ROW = TRUE,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n'
) WITH (
    CustomerID INT,
    CustomerName VARCHAR(100),
    Email VARCHAR(200),
    CreatedDate DATE
) AS customers;

-- Query Delta Lake tables
SELECT *
FROM OPENROWSET(
    BULK 'https://myaccount.dfs.core.windows.net/delta/members/',
    FORMAT = 'DELTA'
) AS members
WHERE ingestedDate >= '2026-03-01';

-- Query JSON files with nested extraction
SELECT
    JSON_VALUE(doc, '$.eventId') AS event_id,
    JSON_VALUE(doc, '$.payload.memberCode') AS member_code,
    JSON_VALUE(doc, '$.timestamp') AS event_time
FROM OPENROWSET(
    BULK 'https://myaccount.dfs.core.windows.net/raw/events/*.json',
    FORMAT = 'CSV',
    FIELDTERMINATOR = '0x0b',
    FIELDQUOTE = '0x0b',
    ROWTERMINATOR = '0x0a'
) WITH (doc NVARCHAR(MAX)) AS events;
```

#### CETAS (CREATE EXTERNAL TABLE AS SELECT)

```sql
-- Materialize query results as Parquet in data lake
CREATE EXTERNAL TABLE dbo.CleanedMembers
WITH (
    LOCATION = 'refined/members/',
    DATA_SOURCE = MyDataLake,
    FILE_FORMAT = ParquetFormat
)
AS
SELECT
    memberCode,
    firstName,
    lastName,
    CAST(createdAt AS DATE) AS createdDate,
    tierCode
FROM OPENROWSET(
    BULK 'https://myaccount.dfs.core.windows.net/raw/members/*.parquet',
    FORMAT = 'PARQUET'
) AS raw
WHERE memberCode IS NOT NULL;
```

**Serverless pricing**: ~$5 per TB of data scanned. Optimization tips:
- Use Parquet/Delta (columnar) instead of CSV/JSON
- Partition data by commonly filtered columns
- Use column projection (SELECT specific columns, not *)
- Pre-filter with WHERE clauses on partition columns

### 1.4 Synapse Link (HTAP)

Real-time analytics on operational data without traditional ETL:

```
┌──────────────────┐     Automatic Sync     ┌──────────────────────┐
│ Cosmos DB        │ ─────────────────────▶  │ Synapse Analytics    │
│ (Transactional)  │     (No ETL code)       │ (Analytical Store)   │
│                  │                          │                      │
│ • MongoDB API    │  < 2 min latency         │ • Serverless SQL     │
│ • SQL API        │  Column store            │ • Spark Pool         │
│ • Gremlin API    │  No RU impact            │ • Full analytics     │
└──────────────────┘                          └──────────────────────┘
```

**Supported Sources:**

| Source | Sync Method | Latency | Notes |
|--------|-----------|---------|-------|
| **Cosmos DB** | Automatic analytical store | ~2 min | No RU impact, column format |
| **SQL Server 2022** | CDC-based | ~minutes | On-premises or Azure VM |
| **Dataverse** | Automatic | ~minutes | Power Platform / Dynamics 365 |

```sql
-- Query Cosmos DB via Synapse Link (Serverless SQL)
SELECT TOP 100
    c.id,
    c.memberCode,
    c.tierCode,
    c._ts AS lastModified
FROM OPENROWSET(
    'CosmosDB',
    'Account=mycosmosdb;Database=loyalty;Collection=members',
    members
) AS c
WHERE c.tierCode = 'GOLD';
```

### 1.5 Current Status: Investment Shifting to Fabric

**Retiring/Retired Components:**
- Synapse Data Explorer pools — **retired Oct 2025**
- Apache Spark 2.4 runtime — **retired**
- Apache Spark 3.1 runtime — **retired**
- Mapping Data Flows — migrating to Fabric Dataflow Gen2
- Synapse Link for SQL — migrating to Fabric Mirroring
- New features go to Fabric, not Synapse

**Still Active (no retirement date):**
- Dedicated SQL Pool (mature, many enterprise deployments)
- Serverless SQL Pool
- Synapse Pipelines (identical engine to ADF)
- Synapse Link for Cosmos DB

---

## 2. Microsoft Fabric

### 2.1 OneLake Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Microsoft Fabric                                │
│                                                                        │
│  ┌───────────┐ ┌────────────┐ ┌──────────────┐ ┌───────────────────┐  │
│  │ Lakehouse │ │ Warehouse  │ │ Real-Time    │ │ Power BI          │  │
│  │           │ │            │ │ Intelligence │ │ (DirectLake)      │  │
│  │ Spark     │ │ T-SQL      │ │              │ │                   │  │
│  │ + Delta   │ │ + Delta    │ │ Eventstream  │ │ No-import BI      │  │
│  │ Notebooks │ │ Cross-DB   │ │ KQL Database │ │ Paginated Reports │  │
│  │ Jobs      │ │ Queries    │ │ Dashboards   │ │ Copilot           │  │
│  └─────┬─────┘ └─────┬──────┘ └──────┬───────┘ └────────┬──────────┘  │
│        │             │               │                   │             │
│  ┌─────┴─────┐ ┌─────┴──────┐ ┌─────┴───────┐ ┌───────┴───────────┐ │
│  │ Data      │ │ Data       │ │ Data        │ │ Data Activator    │ │
│  │ Factory   │ │ Science    │ │ Engineering │ │ (Alerts/Actions)  │ │
│  │ Pipelines │ │ Spark ML   │ │ Spark Jobs  │ │ No-code triggers  │ │
│  │ Dataflow  │ │ MLflow     │ │ Notebooks   │ │                   │ │
│  │ Gen2      │ │ Models     │ │ Lakehouses  │ │                   │ │
│  └─────┬─────┘ └─────┬──────┘ └──────┬──────┘ └────────┬──────────┘ │
│        │             │               │                   │            │
│        └─────────────┼───────────────┼───────────────────┘            │
│                      │                                                │
│              ┌───────▼────────────────────────────────┐               │
│              │              OneLake                    │               │
│              │                                        │               │
│              │  • Single data lake for entire org     │               │
│              │  • Delta Lake as native format         │               │
│              │  • ADLS Gen2 protocol underneath       │               │
│              │  • Shortcuts to external storage       │               │
│              │  • Mirroring from external DBs         │               │
│              │  • ABFS / OneLake API / REST access    │               │
│              │  • Transparent Iceberg serving          │               │
│              └────────────────────────────────────────┘               │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Fabric Experiences in Detail

| Experience | Engine | API | Best For |
|-----------|--------|-----|----------|
| **Data Factory** | ADF Gen2 engine | Pipelines + Dataflow Gen2 | ETL/orchestration, 150+ connectors |
| **Data Engineering** | Spark (Fabric Runtime) | Notebooks, Spark Job Definitions | Heavy ETL, Delta Lake operations |
| **Data Science** | Spark + MLflow | Notebooks, Experiments, Models | ML model training and deployment |
| **Lakehouse** | Spark + SQL Analytics | Tables (Delta) + Files (unmanaged) | Data engineering storage layer |
| **Warehouse** | T-SQL (distributed) | T-SQL endpoint, stored procedures | SQL-heavy analytics, reporting |
| **Real-Time Intelligence** | Kusto (KQL) | Eventstream, KQL Database | Streaming analytics, IoT, logs |
| **Power BI** | DirectLake / Import / DQ | Semantic models, Reports, Dashboards | Business intelligence |
| **Data Activator** | Event-driven triggers | Rules, Alerts | Automated responses to data changes |

### 2.3 OneLake Shortcuts and Mirroring

#### Shortcuts

Shortcuts create virtual references to external data without copying:

```
┌─────────────────────────────┐
│         OneLake             │
│                             │
│  ┌───────────────────────┐  │
│  │ My Lakehouse          │  │
│  │                       │  │
│  │  /Tables/             │  │
│  │    sales (Delta)      │  │  ← Managed table
│  │                       │  │
│  │  /Files/              │  │
│  │    reports/           │  │  ← Managed files
│  │                       │  │
│  │  /Shortcuts/          │  │
│  │    ↗ adls_raw/        │──│──▶ ADLS Gen2 container
│  │    ↗ s3_events/       │──│──▶ AWS S3 bucket
│  │    ↗ gcs_exports/     │──│──▶ GCS bucket
│  │    ↗ other_lakehouse/ │──│──▶ Another Fabric Lakehouse
│  └───────────────────────┘  │
└─────────────────────────────┘
```

**Supported shortcut targets:**
- ADLS Gen2 (same or cross-tenant)
- Amazon S3 (cross-cloud)
- Google Cloud Storage (cross-cloud)
- Other Fabric Lakehouses/Warehouses (within tenant)
- Dataverse (Power Platform)

```python
# Python: Create a shortcut via REST API
import requests

url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items/{lakehouse_id}/shortcuts"
headers = {"Authorization": f"Bearer {token}"}

payload = {
    "path": "Files/external_data",
    "name": "aws_events",
    "target": {
        "amazonS3": {
            "location": "https://my-bucket.s3.us-east-1.amazonaws.com",
            "subpath": "/events/2026/",
            "connectionId": connection_id
        }
    }
}

response = requests.post(url, json=payload, headers=headers)
```

#### Mirroring

Mirroring replicates data from external databases into OneLake in near-real-time:

| Source | Sync Type | Latency | Notes |
|--------|----------|---------|-------|
| Azure SQL Database | CDC | ~seconds | Near-real-time |
| Azure Cosmos DB | Change Feed | ~seconds | NoSQL documents |
| Snowflake | Snapshot + incremental | ~minutes | Read-only replica |
| Azure SQL MI | CDC | ~seconds | Managed instance |
| Azure Databricks | Unity Catalog | ~minutes | Delta tables |
| PostgreSQL | CDC | ~seconds | Azure or on-prem |
| MySQL | CDC | ~seconds | Azure Database for MySQL |

**Mirrored data** lands as Delta tables in OneLake — queryable immediately by all Fabric engines.

### 2.4 Fabric Lakehouse vs Warehouse

| Feature | Lakehouse | Warehouse |
|---------|-----------|-----------|
| **Engine** | Spark + SQL analytics endpoint | T-SQL distributed engine |
| **Primary API** | PySpark/Scala notebooks | T-SQL queries |
| **File types** | Delta tables + raw files | Delta tables only |
| **Schema management** | Schema-on-read (Spark) | Schema-on-write (T-SQL) |
| **Stored procedures** | No | Yes |
| **Views** | SQL views via endpoint | T-SQL views |
| **Cross-database** | Via shortcuts | Cross-warehouse queries |
| **DML** | Spark (MERGE, UPDATE, DELETE) | T-SQL (full DML) |
| **Best for** | Data engineering, ML | SQL analytics, reporting |

```sql
-- Fabric Warehouse: Standard T-SQL operations
CREATE TABLE dbo.Members (
    memberCode VARCHAR(50) NOT NULL,
    firstName NVARCHAR(100),
    lastName NVARCHAR(100),
    tierCode VARCHAR(20),
    ingestedDate DATE
);

-- INSERT INTO
INSERT INTO dbo.Members (memberCode, firstName, lastName, tierCode, ingestedDate)
VALUES ('M001', 'John', 'Doe', 'GOLD', '2026-03-01');

-- MERGE (Fabric supports this)
MERGE INTO dbo.Members AS target
USING staging.NewMembers AS source
ON target.memberCode = source.memberCode
WHEN MATCHED THEN
    UPDATE SET
        tierCode = source.tierCode,
        ingestedDate = source.ingestedDate
WHEN NOT MATCHED THEN
    INSERT (memberCode, firstName, lastName, tierCode, ingestedDate)
    VALUES (source.memberCode, source.firstName, source.lastName,
            source.tierCode, source.ingestedDate);

-- Note: Some T-SQL features NOT supported in Fabric Warehouse:
-- • CREATE INDEX (clustered columnstore is automatic)
-- • IDENTITY columns (use GUID or sequence workaround)
-- • Triggers
-- • Cursors (use set-based operations)
-- • Linked servers
-- • Some window function variants
```

### 2.5 Real-Time Intelligence

Fabric's real-time analytics experience, powered by Kusto/KQL engine:

```
┌────────────────────────────────────────────────────────────────┐
│                   Real-Time Intelligence                       │
│                                                                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐ │
│  │ Eventstream  │───▶│ KQL Database │───▶│ Real-Time        │ │
│  │              │    │              │    │ Dashboard         │ │
│  │ Sources:     │    │ • KQL tables │    │ • Auto-refresh    │ │
│  │ • Event Hubs │    │ • Functions  │    │ • Anomaly detect  │ │
│  │ • Kafka      │    │ • Policies   │    │ • Alerts          │ │
│  │ • Custom App │    │              │    │                   │ │
│  │ • IoT Hub    │    │              │    │                   │ │
│  └──────────────┘    └──────────────┘    └──────────────────┘ │
│                                                                │
│  Eventstream also routes to:                                   │
│  • Lakehouse (Delta tables)                                    │
│  • Warehouse (T-SQL)                                           │
│  • Custom endpoints                                            │
└────────────────────────────────────────────────────────────────┘
```

```kql
// KQL: Query streaming data
StormEvents
| where StartTime between (datetime(2026-01-01) .. datetime(2026-03-01))
| summarize EventCount = count(), TotalDamage = sum(DamageCrops + DamageProperty)
    by State
| top 10 by TotalDamage desc
| render columnchart

// KQL: Time-series anomaly detection
MemberActivity
| make-series RequestCount = count() on Timestamp step 1h
| extend anomalies = series_decompose_anomalies(RequestCount)
| mv-expand Timestamp, RequestCount, anomalies
| where anomalies > 0
```

### 2.6 Dataflow Gen2

Visual, low-code data transformation (Power Query based):

| Feature | Dataflow Gen1 (ADF) | Dataflow Gen2 (Fabric) |
|---------|--------------------|-----------------------|
| **Engine** | Power Query (M) | Power Query (M) + Spark |
| **Scale** | Limited | Spark-backed for large data |
| **Destinations** | Azure only | OneLake + external |
| **Staging** | No lakehouse staging | Auto-staging to lakehouse |
| **Fast Copy** | No | Yes (native connectors) |
| **Refresh** | Scheduled | Scheduled + pipeline trigger |

### 2.7 Capacity Units (CU) Pricing and Management

#### CU SKU Table

| SKU | CUs | Approximate $/month | Power BI Equiv | Spark vCores | SQL CU Limit | Max Memory |
|-----|-----|---------------------|----------------|-------------|-------------|------------|
| F2 | 2 | ~$263 | — | 4 | 2 | 3 GB |
| F4 | 4 | ~$526 | — | 8 | 4 | 6 GB |
| F8 | 8 | ~$1,051 | — | 16 | 8 | 12 GB |
| F16 | 16 | ~$2,102 | — | 32 | 16 | 24 GB |
| F32 | 32 | ~$4,205 | — | 64 | 32 | 48 GB |
| F64 | 64 | ~$8,409 | P1 | 128 | 64 | 96 GB |
| F128 | 128 | ~$16,819 | P2 | 256 | 128 | 192 GB |
| F256 | 256 | ~$33,638 | P3 | 512 | 256 | 384 GB |
| F512 | 512 | ~$67,276 | P4 | 1024 | 512 | 768 GB |
| F1024 | 1024 | ~$134,552 | P5 | 2048 | 1024 | 1536 GB |

#### CU Consumption Model

**Shared capacity** — all workloads compete for the same CU pool:

```
Total CU Budget (per 30-second window)
├── Spark Jobs:          CU consumed based on vCores × time
├── SQL Warehouse:       CU consumed based on query complexity
├── Power BI:            CU consumed based on DirectLake/DQ load
├── Real-Time Intel:     CU consumed based on KQL queries + ingestion
├── Data Factory:        CU consumed based on activity type
└── Dataflow Gen2:       CU consumed based on Power Query + Spark
```

#### CU Smoothing and Throttling

| Behavior | Description |
|----------|-------------|
| **Smoothing** | Short bursts averaged over 5-minute windows |
| **Background throttling** | Low-priority jobs delayed when >100% CU |
| **Interactive throttling** | Queries rejected when CU overcommitted |
| **Autoscale (Preview)** | Temporary burst above SKU limit with extra cost |

```
CU Usage Over Time:
                    Throttle Zone
100% ─────────────────────────── ── ── ── ── ── ──
     │    ╱╲       ╱╲
     │   ╱  ╲     ╱  ╲    ╱╲
     │  ╱    ╲   ╱    ╲  ╱  ╲     Smoothing averages
50%  │ ╱      ╲ ╱      ╲╱    ╲    these peaks
     │╱        ╲              ╲
0%   └──────────────────────────────── Time
     │  5min  │  5min  │  5min  │
```

**Best practice**: Separate workspaces per team/workload for CU isolation and attribution.

### 2.8 Fabric Git Integration and CI/CD

```
┌──────────────────┐     ┌──────────────┐     ┌────────────────┐
│ Fabric Workspace │◄───▶│ Azure DevOps │◄───▶│ GitHub         │
│                  │ Git │ (Repos)      │     │                │
│ • Notebooks      │     │              │     │ • Actions CI   │
│ • Pipelines      │     │ • Branches   │     │ • PRs          │
│ • Semantic Models│     │ • PRs        │     │ • Code Review  │
│ • Reports        │     │ • Pipelines  │     │                │
└──────────────────┘     └──────────────┘     └────────────────┘
```

**Supported Git items:**
- Notebooks (PySpark, SQL, R)
- Data Pipelines
- Semantic Models (Power BI)
- Reports (Power BI)
- Spark Job Definitions
- Lakehouses (metadata only)
- Warehouses (SQL scripts)

**Limitations:**
- Not all item types support Git (some must be deployed manually)
- No native Terraform provider for Fabric items
- Deployment pipelines (Dev → Test → Prod) are Fabric-specific
- DirectLake semantic models have deployment rule gaps

```yaml
# Azure DevOps Pipeline for Fabric (using REST APIs)
trigger:
  branches:
    include:
      - main

stages:
  - stage: DeployToFabric
    jobs:
      - job: UpdateNotebooks
        steps:
          - task: AzureCLI@2
            inputs:
              azureSubscription: 'FabricConnection'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                TOKEN=$(az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv)

                # Update notebook definition
                curl -X PATCH \
                  "https://api.fabric.microsoft.com/v1/workspaces/${WORKSPACE_ID}/notebooks/${NOTEBOOK_ID}/updateDefinition" \
                  -H "Authorization: Bearer $TOKEN" \
                  -H "Content-Type: application/json" \
                  -d @notebook_definition.json
```

### 2.9 Fabric REST APIs

```python
# Python: Fabric REST API examples
import requests

BASE_URL = "https://api.fabric.microsoft.com/v1"

def get_headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# List workspaces
def list_workspaces(token):
    resp = requests.get(f"{BASE_URL}/workspaces", headers=get_headers(token))
    return resp.json()["value"]

# List items in a workspace
def list_items(token, workspace_id, item_type=None):
    url = f"{BASE_URL}/workspaces/{workspace_id}/items"
    if item_type:
        url += f"?type={item_type}"
    resp = requests.get(url, headers=get_headers(token))
    return resp.json()["value"]

# Run a notebook
def run_notebook(token, workspace_id, notebook_id, parameters=None):
    url = f"{BASE_URL}/workspaces/{workspace_id}/items/{notebook_id}/jobs/instances?jobType=RunNotebook"
    payload = {}
    if parameters:
        payload["executionData"] = {"parameters": parameters}
    resp = requests.post(url, json=payload, headers=get_headers(token))
    return resp.headers.get("Location")  # Poll this URL for job status

# Trigger pipeline
def run_pipeline(token, workspace_id, pipeline_id):
    url = f"{BASE_URL}/workspaces/{workspace_id}/items/{pipeline_id}/jobs/instances?jobType=Pipeline"
    resp = requests.post(url, headers=get_headers(token))
    return resp.headers.get("Location")
```

---

## 3. DirectLake Deep Dive

### 3.1 Architecture

DirectLake is a hybrid data access mode exclusive to Fabric:

```
┌────────────────────────────────────────────────────────────────────┐
│                      Power BI Report                               │
│                                                                    │
│  DAX Query → Semantic Model (VertiPaq engine)                      │
│                    │                                               │
│          ┌─────────▼──────────┐                                    │
│          │ DirectLake Mode    │                                    │
│          │                    │                                    │
│          │ Step 1: Check if   │                                    │
│          │ column in memory   │──── Yes ──▶ Read from memory      │
│          │                    │            (Import-like speed)     │
│          │ Step 2: If not,    │                                    │
│          │ "frame" from       │──── Load column from Parquet      │
│          │ OneLake Parquet    │     into VertiPaq columnar store   │
│          │                    │                                    │
│          │ Step 3: If too     │                                    │
│          │ large, fallback    │──── Fallback to DirectQuery        │
│          │ to DirectQuery     │     (slower, query at source)      │
│          └────────────────────┘                                    │
│                    │                                               │
│          ┌─────────▼──────────┐                                    │
│          │ OneLake            │                                    │
│          │ (Delta/Parquet)    │                                    │
│          │ V-Order optimized  │                                    │
│          └────────────────────┘                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 3.2 DirectLake vs Import vs DirectQuery

| Aspect | Import | DirectQuery | DirectLake |
|--------|--------|-------------|------------|
| **Data copy** | Full copy in memory | No copy (live query) | No copy (on-demand framing) |
| **Data freshness** | Scheduled refresh | Real-time | Near-real-time (auto) |
| **Query speed** | Fastest | Slowest | Fast (near Import) |
| **Memory usage** | Full dataset in RAM | None | Partial (framed columns) |
| **Data limit** | By capacity RAM | Source limits | Guardrails per SKU |
| **Refresh needed** | Yes (scheduled) | No | No (transparent) |
| **Multi-source** | Yes | Yes | OneLake only |

### 3.3 DirectLake Guardrails (per Fabric SKU)

When guardrails are exceeded, DirectLake falls back to DirectQuery:

| Guardrail | F2 | F8 | F64 (P1) | F128 (P2) | F256 (P3) | F512 (P4) |
|-----------|-----|-----|----------|-----------|-----------|-----------|
| **Max rows per table** | 300M | 300M | 1.5B | 3B | 6B | 12B |
| **Max model size on disk** | 10 GB | 10 GB | 25 GB | 50 GB | 100 GB | 200 GB |
| **Max columns per table** | 250 | 250 | 500 | 500 | 1,000 | 1,000 |
| **Max tables per model** | N/A | N/A | N/A | N/A | N/A | N/A |
| **Max Parquet groups/table** | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 |

**Fallback behavior**: When a guardrail is hit, the affected query falls back to DirectQuery mode (live query against the SQL Endpoint). This is slower but transparent to the user.

### 3.4 V-Order Optimization

V-Order is a Fabric-specific write-time optimization for Parquet files:

```python
# PySpark: Enable V-Order when writing Delta tables
spark.conf.set("spark.sql.parquet.vorder.enabled", "true")

# Write V-Order optimized Delta table
df.write.format("delta") \
    .mode("overwrite") \
    .option("vorder", "true") \
    .save("Tables/optimized_members")
```

**What V-Order does:**
- Applies special sorting and encoding to Parquet row groups
- Optimizes for VertiPaq columnstore reading (Power BI engine)
- Reduces DirectLake framing time by ~50-80%
- Makes Parquet files ~10-15% larger but dramatically faster for BI queries
- Only benefits DirectLake mode — no impact on Spark or SQL queries

### 3.5 Framing

Framing is the process of loading Parquet column segments into VertiPaq memory:

```
Frame Request Flow:
1. DAX query references column "Revenue"
2. VertiPaq checks: is "Revenue" already framed?
   a. YES → Read from memory (fast path)
   b. NO → Initiate framing:
      i.   Read Parquet file from OneLake
      ii.  Decode and compress into VertiPaq format
      iii. Store in memory cache
      iv.  Execute DAX query
3. Framed columns stay in memory until evicted (LRU policy)
```

**Framing optimization tips:**
- Use V-Order for faster framing
- Keep row group sizes between 100K-1M rows
- OPTIMIZE tables to reduce small files
- Minimize column count (only include needed columns)
- Pre-aggregate where possible

---

## 4. Data Lake / Lakehouse

### 4.1 ADLS Gen2 (Azure Data Lake Storage)

ADLS Gen2 = Azure Blob Storage + Hierarchical Namespace (HNS):

```
ADLS Gen2 Architecture:
┌──────────────────────────────────┐
│ Storage Account (HNS enabled)   │
│                                  │
│  ┌───────────────────────────┐  │
│  │ Container: "bronze"       │  │
│  │   /raw/events/2026/03/    │  │
│  │   /raw/members/           │  │
│  │   /raw/transactions/      │  │
│  └───────────────────────────┘  │
│                                  │
│  ┌───────────────────────────┐  │
│  │ Container: "silver"       │  │
│  │   /delta/member_tier/     │  │  ← Delta table (_delta_log/)
│  │   /delta/tiers/           │  │
│  └───────────────────────────┘  │
│                                  │
│  ┌───────────────────────────┐  │
│  │ Container: "gold"         │  │
│  │   /aggregated/daily_kpi/  │  │
│  │   /exports/               │  │
│  └───────────────────────────┘  │
│                                  │
│  Access: ABFS driver            │
│  abfss://container@account.dfs  │
│  .core.windows.net/path         │
└──────────────────────────────────┘
```

#### Storage Tiers

| Tier | Storage $/GB/mo | Read $/10K ops | Write $/10K ops | Min Retention | Rehydration |
|------|----------------|----------------|-----------------|---------------|-------------|
| **Hot** | $0.018 | $0.004 | $0.050 | None | Instant |
| **Cool** | $0.010 | $0.010 | $0.100 | 30 days | Instant |
| **Cold** | $0.0045 | $0.010 | $0.180 | 90 days | Instant |
| **Archive** | $0.002 | $5.00 | $0.100 | 180 days | Hours (rehydrate) |

#### Lifecycle Management

```json
{
  "rules": [
    {
      "name": "MoveToCoolAfter30Days",
      "type": "Lifecycle",
      "definition": {
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["bronze/raw/"]
        },
        "actions": {
          "baseBlob": {
            "tierToCool": { "daysAfterModificationGreaterThan": 30 },
            "tierToCold": { "daysAfterModificationGreaterThan": 90 },
            "tierToArchive": { "daysAfterModificationGreaterThan": 365 },
            "delete": { "daysAfterModificationGreaterThan": 730 }
          },
          "snapshot": {
            "delete": { "daysAfterCreationGreaterThan": 90 }
          }
        }
      }
    }
  ]
}
```

#### POSIX ACLs

```bash
# Set ACL on directory (recursive)
az storage fs access set-recursive \
  --acl "user:data-engineering-sp:rwx,group:data-readers:r-x,other::---" \
  --path "silver/delta/" \
  --file-system "datalake" \
  --account-name mystorageaccount

# Get current ACL
az storage fs access show \
  --path "silver/delta/member_tier/" \
  --file-system "datalake" \
  --account-name mystorageaccount

# Set default ACL (inherited by new files)
az storage fs access set \
  --acl "default:user:data-engineering-sp:rwx,default:group:data-readers:r-x" \
  --path "silver/delta/" \
  --file-system "datalake" \
  --account-name mystorageaccount
```

**ACL vs RBAC:**

| Feature | RBAC | POSIX ACL |
|---------|------|-----------|
| **Scope** | Account/container level | Directory/file level |
| **Granularity** | Coarse (Reader/Contributor) | Fine (rwx per user/group) |
| **Inheritance** | No | Default ACL propagates |
| **Use case** | Admin access, service roles | Data-level multi-tenant |
| **Management** | Azure Portal / CLI | CLI / SDK |

#### Private Endpoints

```bash
# Create private endpoint for ADLS Gen2
az network private-endpoint create \
  --name pe-datalake \
  --resource-group myRG \
  --vnet-name myVnet \
  --subnet private-endpoint-subnet \
  --private-connection-resource-id $(az storage account show \
    --name mystorageaccount --query id -o tsv) \
  --group-ids dfs \
  --connection-name pe-datalake-conn

# Create private DNS zone
az network private-dns zone create \
  --resource-group myRG \
  --name "privatelink.dfs.core.windows.net"
```

#### AzCopy for Data Transfer

```bash
# Copy from local to ADLS Gen2
azcopy copy './local-data/*' \
  'https://mystorageaccount.dfs.core.windows.net/bronze/raw/events/' \
  --recursive

# Sync between ADLS containers
azcopy sync \
  'https://source.dfs.core.windows.net/bronze/' \
  'https://dest.dfs.core.windows.net/bronze/' \
  --recursive --delete-destination=true

# Copy between storage accounts with SAS token
azcopy copy \
  'https://source.blob.core.windows.net/data/*?sv=2023-01-03&ss=b&srt=co&sp=r&se=...' \
  'https://dest.dfs.core.windows.net/imported/' \
  --recursive
```

### 4.2 OneLake vs ADLS Gen2

| Feature | OneLake | ADLS Gen2 |
|---------|---------|-----------|
| **Protocol** | ABFS + OneLake API | ABFS + REST |
| **Format** | Delta Lake (enforced for tables) | Any format |
| **Governance** | Fabric workspace security | RBAC + POSIX ACL |
| **Multi-engine** | All Fabric engines | Any ABFS-compatible |
| **Shortcuts** | Yes (cross-cloud) | No (manual mount) |
| **Storage cost** | ~$0.023/GB/mo | ~$0.018/GB/mo (Hot) |
| **Data residency** | Fabric capacity region | Storage account region |
| **Lifecycle tiers** | No (Hot only) | Hot/Cool/Cold/Archive |
| **Lock-in** | Medium (OneLake APIs) | Low (standard ABFS) |

**Key insight**: OneLake uses ADLS Gen2 under the hood but adds governance, shortcuts, and Fabric integration. Storage is ~28% more expensive but includes features.

---

## 5. Delta Lake Operations

### 5.1 Delta Lake on Azure

Delta Lake is the native table format for both Microsoft Fabric and Azure Databricks:

```
Delta Table Structure:
my_table/
├── _delta_log/
│   ├── 00000000000000000000.json    ← Initial commit
│   ├── 00000000000000000001.json    ← Second commit
│   ├── 00000000000000000002.json    ← Third commit
│   ├── 00000000000000000010.checkpoint.parquet  ← Checkpoint (every 10)
│   └── _last_checkpoint                ← Pointer to latest checkpoint
├── part-00000-xxxx.parquet          ← Data files
├── part-00001-xxxx.parquet
└── part-00002-xxxx.parquet
```

### 5.2 Delta Operations in Spark (Fabric/Databricks)

```python
# Create Delta table
from delta.tables import DeltaTable
from pyspark.sql.functions import col, current_timestamp, lit

# Write DataFrame as Delta
df.write.format("delta") \
    .mode("overwrite") \
    .partitionBy("ingestedDate") \
    .option("overwriteSchema", "true") \
    .saveAsTable("lakehouse.member_tier")

# MERGE (Upsert)
target = DeltaTable.forName(spark, "lakehouse.member_tier")
target.alias("t") \
    .merge(
        source_df.alias("s"),
        "t.memberCode = s.memberCode AND t.tierCode = s.tierCode"
    ) \
    .whenMatchedUpdate(set={
        "tierName": "s.tierName",
        "pointBalance": "s.pointBalance",
        "updatedAt": current_timestamp()
    }) \
    .whenNotMatchedInsertAll() \
    .execute()

# DELETE
target.delete(condition="tierCode = 'EXPIRED' AND ingestedDate < '2025-01-01'")

# UPDATE
target.update(
    condition="tierCode = 'SILVER' AND pointBalance > 10000",
    set={"tierCode": lit("GOLD")}
)
```

### 5.3 Delta Operations in T-SQL (Fabric Warehouse)

```sql
-- MERGE in Fabric Warehouse T-SQL
MERGE INTO dbo.member_tier AS target
USING staging.new_members AS source
ON target.memberCode = source.memberCode
   AND target.tierCode = source.tierCode
WHEN MATCHED THEN
    UPDATE SET
        tierName = source.tierName,
        pointBalance = source.pointBalance,
        updatedAt = GETUTCDATE()
WHEN NOT MATCHED BY TARGET THEN
    INSERT (memberCode, tierCode, tierName, pointBalance, ingestedDate, updatedAt)
    VALUES (source.memberCode, source.tierCode, source.tierName,
            source.pointBalance, source.ingestedDate, GETUTCDATE())
WHEN NOT MATCHED BY SOURCE AND target.ingestedDate < '2025-01-01' THEN
    DELETE;
```

### 5.4 Time Travel

```python
# Spark: Read older version
df_v5 = spark.read.format("delta") \
    .option("versionAsOf", 5) \
    .load("Tables/member_tier")

# Read by timestamp
df_yesterday = spark.read.format("delta") \
    .option("timestampAsOf", "2026-03-04 00:00:00") \
    .load("Tables/member_tier")

# View history
from delta.tables import DeltaTable
dt = DeltaTable.forPath(spark, "Tables/member_tier")
dt.history().show(truncate=False)

# Restore to previous version
dt.restoreToVersion(5)
# or
dt.restoreToTimestamp("2026-03-04 00:00:00")
```

```sql
-- T-SQL (Synapse Serverless): Time travel on Delta
SELECT * FROM OPENROWSET(
    BULK 'https://account.dfs.core.windows.net/silver/member_tier/',
    FORMAT = 'DELTA'
) AS members
OPTION (DELTA_TIMESTAMP = '2026-03-04T00:00:00Z');
```

### 5.5 OPTIMIZE and VACUUM

```python
# OPTIMIZE: Compact small files (bin-packing)
from delta.tables import DeltaTable

dt = DeltaTable.forName(spark, "lakehouse.member_tier")

# Basic optimize (compact all files)
dt.optimize().executeCompaction()

# Optimize with Z-ORDER for query patterns
dt.optimize().executeZOrderBy("memberCode", "tierCode")

# VACUUM: Remove old files beyond retention
# Default retention: 7 days (168 hours)
dt.vacuum(retentionHours=168)

# Dangerous: Remove files older than 0 hours
# spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
# dt.vacuum(0)  # DO NOT do this in production!
```

```sql
-- SQL: OPTIMIZE and VACUUM
OPTIMIZE member_tier;
OPTIMIZE member_tier ZORDER BY (memberCode, tierCode);

VACUUM member_tier RETAIN 168 HOURS;
```

### 5.6 Liquid Clustering (Databricks / Fabric Preview)

Replaces traditional Hive-style partitioning with dynamic clustering:

```python
# Create table with liquid clustering
spark.sql("""
    CREATE TABLE member_tier (
        memberCode STRING,
        tierCode STRING,
        tierName STRING,
        pointBalance BIGINT,
        ingestedDate DATE
    )
    USING DELTA
    CLUSTER BY (memberCode, tierCode)
""")

# Change clustering columns (no rewrite needed)
spark.sql("ALTER TABLE member_tier CLUSTER BY (ingestedDate, tierCode)")

# OPTIMIZE triggers clustering
spark.sql("OPTIMIZE member_tier")
```

**Liquid Clustering vs Partitioning:**

| Feature | Hive-Style Partitioning | Liquid Clustering |
|---------|------------------------|-------------------|
| **Column changes** | Requires table rewrite | ALTER TABLE (instant) |
| **High cardinality** | Too many small files | Handles well |
| **Low cardinality** | Works well | Also works well |
| **Data skew** | Manual management | Automatic rebalancing |
| **File size** | Varies per partition | Optimized uniformly |
| **Maintenance** | Manual partition management | Just run OPTIMIZE |

### 5.7 Deletion Vectors

Efficient deletes without rewriting entire Parquet files:

```python
# Enable deletion vectors
spark.sql("""
    ALTER TABLE member_tier
    SET TBLPROPERTIES ('delta.enableDeletionVectors' = true)
""")

# Now DELETEs and UPDATEs create deletion vectors instead of rewriting files
# The deletion vector marks specific rows as "deleted" in a side file
# OPTIMIZE later compacts and applies deletion vectors physically
```

```
Without Deletion Vectors:              With Deletion Vectors:
DELETE WHERE id=5                       DELETE WHERE id=5

data-00001.parquet (1GB) ← rewrite     data-00001.parquet (1GB) ← unchanged
data-00002.parquet (1GB) ← rewrite     data-00002.parquet (1GB) ← unchanged
                                        deletion-vector.bin     ← tiny file
Time: minutes                           Time: seconds
```

### 5.8 Change Data Feed (CDF)

```python
# Enable Change Data Feed
spark.sql("""
    ALTER TABLE member_tier
    SET TBLPROPERTIES ('delta.enableChangeDataFeed' = true)
""")

# Read changes between versions
changes = spark.read.format("delta") \
    .option("readChangeData", "true") \
    .option("startingVersion", 10) \
    .option("endingVersion", 15) \
    .table("member_tier")

# Change columns added automatically:
# _change_type: insert, update_preimage, update_postimage, delete
# _commit_version: version number
# _commit_timestamp: timestamp

changes.select("memberCode", "tierCode", "_change_type", "_commit_version").show()

# Filter only inserts and updates
new_and_updated = changes.filter(
    col("_change_type").isin("insert", "update_postimage")
)
```

---

## 6. Apache Iceberg on Azure

### 6.1 OneLake Transparent Iceberg Serving

Microsoft's approach: Delta tables in OneLake are served as Iceberg to external engines:

```
┌──────────────────────────────────────────────────────────────┐
│                        OneLake                                │
│                                                               │
│  ┌─────────────────────────────┐                             │
│  │ Delta Table (native)       │                             │
│  │ _delta_log/ + parquet      │                             │
│  └──────────────┬──────────────┘                             │
│                 │                                             │
│           ┌─────▼─────────────┐                              │
│           │ Iceberg Serving   │ ← Transparent conversion    │
│           │ Layer             │                              │
│           │                   │                              │
│           │ Generates:        │                              │
│           │ • metadata.json   │                              │
│           │ • manifest lists  │                              │
│           │ • manifests       │                              │
│           │ (on-the-fly)      │                              │
│           └───────┬───────────┘                              │
│                   │                                           │
│          ┌────────▼──────────────────────────┐               │
│          │ Iceberg REST Catalog Interface    │               │
│          │ (OneLake Table APIs - Preview)    │               │
│          └────────┬──────────────────────────┘               │
│                   │                                           │
└───────────────────┼───────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   Apache Spark  Apache Flink   Trino/DuckDB
   (external)    (external)     (external)
```

### 6.2 How to Access OneLake Tables as Iceberg

```python
# PySpark: Read OneLake Delta table as Iceberg (external engine)
spark = SparkSession.builder \
    .config("spark.sql.catalog.onelake", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.onelake.type", "rest") \
    .config("spark.sql.catalog.onelake.uri",
            "https://onelake.dfs.fabric.microsoft.com/v1") \
    .config("spark.sql.catalog.onelake.credential", "bearer-token") \
    .config("spark.sql.catalog.onelake.token", access_token) \
    .getOrCreate()

# Read table through Iceberg catalog
df = spark.table("onelake.workspace_name.lakehouse_name.member_tier")
```

### 6.3 Limitations of Iceberg Serving

| Limitation | Impact | Mitigation |
|-----------|--------|------------|
| Not true native Iceberg | Metadata generated on-the-fly | Accept latency overhead |
| Read-only from external | Cannot write Iceberg back to OneLake | Write via Fabric Spark/SQL |
| Preview status (Table APIs) | Breaking changes possible | Pin API versions |
| Conversion latency | Minutes delay for metadata generation | Not suitable for real-time |
| Schema mapping gaps | Complex types may not map perfectly | Test thoroughly |
| No partition evolution | Delta doesn't support Iceberg hidden partitions | Use Hive-style or liquid clustering |

### 6.4 Azure Databricks Native Iceberg

On Azure Databricks, you can use native Iceberg with Unity Catalog:

```python
# Databricks on Azure: Write native Iceberg via UniForm
spark.sql("""
    CREATE TABLE unity_catalog.schema.events
    USING DELTA
    TBLPROPERTIES (
        'delta.universalFormat.enabledFormats' = 'iceberg',
        'delta.enableIcebergCompatV2' = 'true'
    )
    AS SELECT * FROM raw_events
""")

# The table is now readable as both Delta AND Iceberg
# External engines can access via Iceberg REST Catalog (Unity Catalog)
```

---

## 7. Azure Databricks on Azure

### 7.1 Overview

Azure Databricks = Databricks platform running in Azure tenant with deep Azure integration:

```
┌──────────────────────────────────────────────────────────────────┐
│                    Azure Databricks                               │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                  Databricks Control Plane                  │  │
│  │  Unity Catalog, Workspace, Clusters, Jobs, SQL Warehouses │  │
│  └────────────────────────────────┬───────────────────────────┘  │
│                                   │                               │
│  ┌────────────────────────────────▼───────────────────────────┐  │
│  │              Azure Data Plane (Customer VNet)              │  │
│  │                                                            │  │
│  │  ┌──────────────┐  ┌────────────┐  ┌───────────────────┐  │  │
│  │  │ Spark Clusters│  │ SQL        │  │ Delta Live Tables │  │  │
│  │  │ (Azure VMs)  │  │ Warehouses │  │ (ETL Pipelines)   │  │  │
│  │  │              │  │ (Photon)   │  │                   │  │  │
│  │  │ Jobs/All-    │  │ Serverless │  │ Expectations      │  │  │
│  │  │ Purpose/Pool │  │ + Classic  │  │ Auto-scaling      │  │  │
│  │  └──────┬───────┘  └─────┬──────┘  └──────┬────────────┘  │  │
│  │         │                │                 │               │  │
│  │         └────────────────┼─────────────────┘               │  │
│  │                          │                                 │  │
│  │              ┌───────────▼───────────┐                     │  │
│  │              │   ADLS Gen2 / ABFS   │                     │  │
│  │              │   (Customer Storage)  │                     │  │
│  │              └───────────────────────┘                     │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Azure-Specific Integrations:                                     │
│  • Azure Key Vault backed secret scope                           │
│  • Azure AD / Entra ID authentication                            │
│  • VNet injection (data plane in customer VNet)                  │
│  • Private Link (no public IP)                                   │
│  • Azure Monitor / Log Analytics integration                     │
│  • SCIM provisioning from Azure AD                               │
└──────────────────────────────────────────────────────────────────┘
```

### 7.2 Pricing on Azure

DBU pricing is 10-20% higher on Azure compared to AWS:

| Workload | DBU Rate ($/DBU-hr) | Notes |
|----------|---------------------|-------|
| **Jobs Compute** | ~$0.10-0.20 | Batch ETL, scheduled jobs |
| **Jobs Compute (Photon)** | ~$0.15-0.30 | Photon-accelerated |
| **SQL Compute (Classic)** | ~$0.22 | SQL Warehouses |
| **SQL Compute (Serverless)** | ~$0.70 | Auto-scaling SQL |
| **All-Purpose Compute** | ~$0.40-0.55 | Interactive/development |
| **DLT (Core)** | ~$0.20 | Delta Live Tables core |
| **DLT (Pro)** | ~$0.25 | + Expectations |
| **DLT (Advanced)** | ~$0.36 | + Change Data Capture |
| **Model Serving** | ~$0.07 | ML inference |

**Total cost = DBU charges (Databricks) + Azure VM charges (Microsoft)**

Example: 10-node cluster with D16s_v3 VMs:
- Azure VM: 10 × $0.768/hr = $7.68/hr
- Databricks DBU: 10 × 8 DBU × $0.15/DBU-hr = $12.00/hr
- **Total: $19.68/hr**

### 7.3 Azure-Specific Integrations

```python
# Azure Key Vault backed secrets
dbutils.secrets.get(scope="azure-keyvault", key="storage-account-key")

# Access ADLS Gen2 with service principal
spark.conf.set(
    "fs.azure.account.auth.type.mystorageaccount.dfs.core.windows.net",
    "OAuth"
)
spark.conf.set(
    "fs.azure.account.oauth.provider.type.mystorageaccount.dfs.core.windows.net",
    "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider"
)
spark.conf.set(
    "fs.azure.account.oauth2.client.id.mystorageaccount.dfs.core.windows.net",
    dbutils.secrets.get("azure-keyvault", "sp-client-id")
)
spark.conf.set(
    "fs.azure.account.oauth2.client.secret.mystorageaccount.dfs.core.windows.net",
    dbutils.secrets.get("azure-keyvault", "sp-client-secret")
)
spark.conf.set(
    "fs.azure.account.oauth2.client.endpoint.mystorageaccount.dfs.core.windows.net",
    "https://login.microsoftonline.com/<tenant-id>/oauth2/token"
)

# Read from ADLS Gen2
df = spark.read.format("delta").load(
    "abfss://silver@mystorageaccount.dfs.core.windows.net/member_tier/"
)
```

### 7.4 When to Use Databricks vs Fabric on Azure

| Dimension | Azure Databricks | Microsoft Fabric |
|-----------|-----------------|-----------------|
| **Team skills** | Python/Scala engineers, data scientists | Business analysts, SQL developers |
| **ML/AI** | Advanced (MLflow, feature engineering, Mosaic AI) | Basic (AutoML, Copilot) |
| **Multi-cloud** | Yes (AWS, Azure, GCP) | Azure only |
| **BI** | SQL Warehouses + Tableau/Looker/Power BI | DirectLake Power BI (integrated) |
| **ETL complexity** | Complex Spark pipelines, DLT | Simple-medium Dataflow Gen2 |
| **Streaming** | Spark Structured Streaming (advanced) | Eventstream (simpler) |
| **Governance** | Unity Catalog (open, multi-cloud) | Purview + Fabric security |
| **Vendor lock-in** | Lower (open formats, multi-cloud) | Higher (OneLake, Fabric APIs) |
| **Maturity** | Very mature (10+ years) | Evolving (GA Nov 2023) |
| **Cost at scale** | Higher DBU cost but predictable | CU sharing can be cheaper |
| **M365 integration** | None | Deep (Teams, SharePoint, Excel) |
| **Power BI** | Requires separate capacity | Included in F64+ |
| **Data sharing** | Delta Sharing (open protocol) | OneLake shortcuts |

**Recommendation:**
- Use **Fabric** if: Power BI is primary BI tool, team is SQL-focused, Microsoft shop
- Use **Databricks** if: ML-heavy, multi-cloud needed, complex Spark ETL, open format priority
- Use **both** if: Databricks for engineering/ML → OneLake shortcut → Fabric for Power BI

---

## 8. Limitations and Known Issues

### 8.1 Fabric Maturity Gaps (as of March 2026)

| Issue | Severity | Impact | Workaround |
|-------|----------|--------|------------|
| T-SQL incomplete | **High** | No CREATE INDEX, IDENTITY, triggers, cursors, some window functions | Refactor to supported syntax or keep in Synapse |
| OneLake row-level security (Preview) | **High** | Cannot enforce fine-grained access | Define RLS at Power BI semantic model level |
| CI/CD gaps | **Medium** | DirectLake deployment rules greyed out, limited Git support | PowerShell + REST API scripts |
| SSIS packages | **Medium** | Cannot run natively in Fabric | Keep in Azure Data Factory SSIS IR |
| Mapping Data Flows | **Medium** | Not available in Fabric | Use Dataflow Gen2 or ADF |
| Fewer connectors than ADF | **Medium** | Some enterprise sources not supported | Use ADF for unsupported, load to OneLake |
| CU attribution | **Medium** | Hard to track which workload consumes CU | Workspace separation per team |
| No archive tier in OneLake | **Medium** | Cannot lifecycle old data to cheaper storage | Keep archive data in raw ADLS Gen2 |
| Cross-workspace queries | **Low** | Limited cross-workspace joins in Warehouse | Use shortcuts or centralized lakehouse |
| Spark session startup | **Low** | 30-60s cold start for Spark sessions | Use starter pools or warm pools |

### 8.2 Synapse Retirement Concerns

| Component | Status | Risk | Migration Target |
|-----------|--------|------|-----------------|
| Data Explorer pools | **Retired** Oct 2025 | Complete | Real-Time Intelligence (Fabric) |
| Spark 2.4/3.1 runtimes | **Retired** | Complete | Fabric Spark or Databricks |
| Mapping Data Flows | **Migrating** | Medium | Dataflow Gen2 (Fabric) |
| Synapse Link for SQL | **Migrating** | Medium | Fabric Mirroring |
| Dedicated SQL Pool | **Active** (no date) | Low-Medium | Fabric Warehouse |
| Serverless SQL Pool | **Active** (no date) | Low | Fabric Lakehouse SQL endpoint |
| Synapse Pipelines | **Active** (= ADF) | Low | Data Factory (identical engine) |

### 8.3 Cost Complexity

| Platform | Billing Dimensions | Predictability | Complexity |
|----------|-------------------|---------------|-----------|
| **Synapse** | DWU-hrs + per-TB + vCore-hrs + activity runs + storage + egress | Low | Very High |
| **Fabric** | CU-hrs + OneLake storage + egress | Medium | Medium |
| **Databricks** | DBU-hrs + VM-hrs + storage + egress + Premium features | Medium | High |

**Hidden cost traps:**

| Trap | Impact | Mitigation |
|------|--------|------------|
| OneLake storage is ~28% more expensive than ADLS Gen2 | $0.023 vs $0.018/GB/mo | Keep large cold data in raw ADLS Gen2 |
| Fabric CU throttling on under-provisioned capacity | Queries rejected, jobs delayed | Right-size CU or enable autoscale |
| Synapse serverless SQL on large unpartitioned data | Scans entire dataset (per-TB billing) | Partition by date, use columnar format |
| Cross-region egress | $0.05-0.12/GB | Co-locate compute and storage |
| Databricks all-purpose clusters left running | $20+/hr for idle clusters | Use auto-terminate (10-30 min) |
| Power BI import refresh consuming CUs | Unexpected CU consumption | Use DirectLake instead of Import |
| Spark session idle time | CUs consumed while notebook idle | Configure idle timeout (5-15 min) |

### 8.4 Lock-in Assessment

| Platform | Lock-In Level | Portable Aspects | Proprietary Aspects |
|----------|-------------|-----------------|---------------------|
| **Synapse Dedicated SQL** | Medium-High | T-SQL syntax, SQL Server skills | MPP distribution, DWU scaling, system DMVs |
| **Synapse Serverless** | Low | Standard T-SQL, open formats | OPENROWSET/CETAS syntax |
| **Fabric OneLake** | Medium | Delta Lake format (open), ABFS protocol | OneLake APIs, shortcuts, mirroring |
| **Fabric DirectLake** | **High** | None | Fabric-exclusive feature |
| **Fabric Warehouse** | Medium | T-SQL (mostly standard) | Fabric-specific limitations |
| **Fabric Real-Time Intelligence** | Medium | KQL syntax | Eventstream, integrations |
| **Databricks on Azure** | Low-Medium | Spark, Delta, MLflow, SQL | Unity Catalog (becoming standard), DBU pricing |

---

## 9. Cost Summary

### 9.1 Compute Cost Comparison

| Component | Synapse | Fabric | Databricks |
|-----------|---------|--------|------------|
| **Entry** | DW100c: ~$1,100/mo | F2: ~$263/mo | Jobs 2-node: ~$500/mo |
| **Medium** | DW1000c: ~$11,000/mo | F64: ~$8,400/mo | Jobs 10-node: ~$5,000/mo |
| **Large** | DW5000c: ~$55,000/mo | F256: ~$33,600/mo | Jobs 50-node: ~$50,000/mo |
| **Serverless SQL** | ~$5/TB scanned | Included in CU | SQL Serverless: ~$0.70/DBU |

### 9.2 Storage Cost Comparison

| Storage | Cost $/GB/mo | Notes |
|---------|-------------|-------|
| ADLS Gen2 (Hot) | $0.018 | Used by Synapse, Databricks |
| ADLS Gen2 (Cool) | $0.010 | 30-day minimum |
| ADLS Gen2 (Cold) | $0.0045 | 90-day minimum |
| ADLS Gen2 (Archive) | $0.002 | Rehydration required |
| OneLake | ~$0.023 | Fabric only, Hot tier only |

### 9.3 BI Cost Comparison

| Component | Price | Notes |
|-----------|-------|-------|
| Power BI Pro | $10/user/mo | Basic sharing and collaboration |
| Power BI Premium Per User (PPU) | $20/user/mo | Full premium features per user |
| Power BI Premium (P1) | ~$5,000/mo | Equivalent to Fabric F64 |
| Fabric F64 (includes Power BI) | ~$8,400/mo | Power BI Premium P1 included |
| Fabric F2 | ~$263/mo | Limited Power BI (no DirectLake full features) |

### 9.4 Reserved Instance Savings

| Platform | 1-Year RI | 3-Year RI | Notes |
|----------|----------|----------|-------|
| Synapse Dedicated SQL | ~37% | ~65% | DWU commitment |
| Fabric CU | ~20-25% | ~35-40% | CU commitment |
| Databricks DBCU | ~20% | ~37% | Commit units |
| Azure VMs (for Databricks) | ~30-40% | ~55-65% | VM reservation separate |

### 9.5 Scenario-Based Cost Estimates

#### Small Team (5 users, 500 GB, 50 queries/day)

| Component | Synapse | Fabric | Databricks |
|-----------|---------|--------|------------|
| Compute | $1,100/mo (DW100c) | $263/mo (F2) | $500/mo (Jobs) |
| Storage | $9/mo | $12/mo | $9/mo |
| BI | $50/mo (5×Pro) | Included (limited) | $50/mo (external) |
| **Total** | **~$1,160/mo** | **~$275/mo** | **~$560/mo** |

#### Medium Enterprise (30 users, 10 TB, 500 queries/day)

| Component | Synapse | Fabric | Databricks |
|-----------|---------|--------|------------|
| Compute | $11,000/mo (DW1000c) | $8,400/mo (F64) | $5,000/mo |
| Storage | $180/mo | $230/mo | $180/mo |
| BI | $300/mo (30×Pro) | Included (P1 equiv) | $300/mo |
| ETL | $500/mo (Pipelines) | Included in CU | $2,000/mo |
| **Total** | **~$12,000/mo** | **~$8,630/mo** | **~$7,480/mo** |

#### Large Enterprise (100+ users, 100 TB+, streaming + batch)

| Component | Synapse | Fabric | Databricks |
|-----------|---------|--------|------------|
| Compute | $55,000/mo | $33,600/mo (F256) | $50,000/mo |
| Storage | $1,800/mo | $2,300/mo | $1,800/mo |
| BI | $1,000/mo | Included | $1,000/mo |
| Streaming | $2,000/mo | Included in CU | $5,000/mo |
| **Total** | **~$60,000/mo** | **~$36,000/mo** | **~$58,000/mo** |
| **With RI** | **~$38,000/mo** | **~$27,000/mo** | **~$42,000/mo** |

---

## 10. References

### Official Microsoft Documentation

**Synapse Analytics:**
- [Synapse SQL Architecture](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/overview-architecture)
- [Synapse Dedicated SQL Pool](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql-data-warehouse/sql-data-warehouse-overview-what-is)
- [Synapse Serverless SQL](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/on-demand-workspace-overview)
- [Synapse Pricing](https://azure.microsoft.com/en-us/pricing/details/synapse-analytics/)
- [Synapse Link Overview](https://learn.microsoft.com/en-us/azure/cosmos-db/synapse-link)
- [Distribution Design](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql-data-warehouse/sql-data-warehouse-tables-distribute)
- [Materialized Views](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql-data-warehouse/performance-tuning-materialized-views)
- [Row-Level Security](https://learn.microsoft.com/en-us/sql/relational-databases/security/row-level-security)
- [OPENROWSET in Synapse](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/develop-openrowset)
- [CETAS in Synapse](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/develop-tables-cetas)

**Microsoft Fabric:**
- [Fabric Overview](https://learn.microsoft.com/en-us/fabric/fundamentals/microsoft-fabric-overview)
- [OneLake Overview](https://learn.microsoft.com/en-us/fabric/onelake/onelake-overview)
- [OneLake Shortcuts](https://learn.microsoft.com/en-us/fabric/onelake/onelake-shortcuts)
- [Fabric Mirroring](https://learn.microsoft.com/en-us/fabric/database/mirrored-database/overview)
- [Fabric Lakehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview)
- [Fabric Warehouse](https://learn.microsoft.com/en-us/fabric/data-warehouse/data-warehousing)
- [Real-Time Intelligence](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/overview)
- [Eventstream](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/overview)
- [Fabric Pricing](https://azure.microsoft.com/en-us/pricing/details/microsoft-fabric/)
- [Fabric Licenses and Capacity](https://learn.microsoft.com/en-us/fabric/enterprise/licenses)
- [Fabric REST APIs](https://learn.microsoft.com/en-us/rest/api/fabric/core/items)
- [Fabric Git Integration](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration)

**DirectLake:**
- [DirectLake Overview](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-overview)
- [DirectLake Guardrails](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-fixed-identity)
- [V-Order Optimization](https://learn.microsoft.com/en-us/fabric/data-engineering/delta-optimization-and-v-order)
- [Direct Lake vs Import — SQLBI](https://www.sqlbi.com/blog/marco/2025/05/13/direct-lake-vs-import-vs-direct-lakeimport-fabric-semantic-models-may-2025/)

**Storage:**
- [ADLS Gen2 Introduction](https://learn.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-introduction)
- [ADLS Gen2 Pricing](https://azure.microsoft.com/en-in/pricing/details/storage/data-lake/)
- [ADLS ACLs](https://learn.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-access-control)
- [Lifecycle Management](https://learn.microsoft.com/en-us/azure/storage/blobs/lifecycle-management-overview)
- [Private Endpoints](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints)

**Delta Lake:**
- [Delta Lake on Azure](https://learn.microsoft.com/en-us/azure/databricks/delta/)
- [Delta Lake MERGE](https://learn.microsoft.com/en-us/azure/databricks/delta/merge)
- [Delta Lake OPTIMIZE](https://learn.microsoft.com/en-us/azure/databricks/delta/optimize)
- [Liquid Clustering](https://learn.microsoft.com/en-us/azure/databricks/delta/clustering)
- [Deletion Vectors](https://learn.microsoft.com/en-us/azure/databricks/delta/deletion-vectors)
- [Change Data Feed](https://learn.microsoft.com/en-us/azure/databricks/delta/delta-change-data-feed)

**Iceberg on Azure:**
- [OneLake Iceberg Tables](https://learn.microsoft.com/en-us/fabric/onelake/onelake-iceberg-tables)
- [OneLake Table APIs (Preview)](https://learn.microsoft.com/en-us/fabric/onelake/onelake-table-api)
- [Fabric Blog — Delta to Iceberg](https://blog.fabric.microsoft.com/en-us/blog/new-in-onelake-access-your-delta-lake-tables-as-iceberg-automatically/)

**Azure Databricks:**
- [Azure Databricks Overview](https://learn.microsoft.com/en-us/azure/databricks/introduction/index)
- [Azure Databricks Pricing](https://azure.microsoft.com/en-us/pricing/details/databricks/)
- [VNet Injection](https://learn.microsoft.com/en-us/azure/databricks/administration-guide/cloud-configurations/azure/vnet-inject)
- [Unity Catalog on Azure](https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/)

### Third-Party Analysis
- [Synapse vs Fabric — ChaosGenius](https://www.chaosgenius.io/blog/azure-synapse-vs-fabric/)
- [Synapse vs Fabric — Flexera](https://www.flexera.com/blog/finops/azure-synapse-vs-fabric/)
- [Fabric vs Synapse — Atlan](https://atlan.com/microsoft-fabric-vs-azure-synapse/)
- [Databricks vs Fabric — Flexera](https://www.flexera.com/blog/finops/microsoft-fabric-vs-databricks/)
- [Databricks vs Fabric — ChaosGenius](https://www.chaosgenius.io/blog/microsoft-fabric-vs-databricks/)
- [OneLake Hidden Costs — Medium](https://medium.com/@hellodatainthedark/onelakes-hidden-costs-why-it-s-more-expensive-than-adls-gen2-85ece7f04258)
- [Fabric CU Consumption Guide — Data Mozart](https://data-mozart.com/fabric-capacity-units-explained/)
- [Fabric Architecture Best Practices — SQLServerCentral](https://www.sqlservercentral.com/articles/microsoft-fabric-architecture-best-practices)

---

> **Document Version**: 2.0 | **Last Updated**: 2026-03-05
