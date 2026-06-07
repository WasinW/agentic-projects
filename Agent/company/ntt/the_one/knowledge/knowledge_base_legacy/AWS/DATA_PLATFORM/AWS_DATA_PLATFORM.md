# AWS Data Platform: Redshift, Lake Formation & Lakehouse

> Comprehensive knowledge base covering Amazon Redshift, AWS Lake Formation,
> Apache Iceberg on AWS, S3 Tables, Athena, Glue, EMR, and the Lakehouse
> architecture pattern on AWS.
>
> **Version**: 2.0 | **Last Updated**: 2026-03-05 | **Maintainer**: Data Platform Team

---

## Table of Contents

1. [Amazon Redshift (Data Warehouse)](#1-amazon-redshift)
2. [Data Lake / Lakehouse on AWS](#2-data-lake--lakehouse-on-aws)
3. [Query Engines](#3-query-engines)
4. [AWS Glue](#4-aws-glue)
5. [Amazon EMR](#5-amazon-emr)
6. [SageMaker Lakehouse / Unified Studio](#6-sagemaker-lakehouse--unified-studio)
7. [Limitations and Known Issues](#7-limitations-and-known-issues)
8. [Cost Summary](#8-cost-summary)
9. [References](#9-references)

---

## 1. Amazon Redshift

### 1.1 Architecture Overview

Amazon Redshift is a fully managed, petabyte-scale data warehouse service built on
Massively Parallel Processing (MPP) architecture. It is optimized for online analytical
processing (OLAP) workloads and uses columnar storage, data compression, and zone maps
to reduce I/O needed for queries.

#### Cluster Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Amazon Redshift Cluster                         │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     Leader Node                               │   │
│  │  - SQL parsing, query planning, optimization                  │   │
│  │  - Compiles and distributes code to compute nodes             │   │
│  │  - Aggregates intermediate results from compute nodes         │   │
│  │  - Returns final results to client                            │   │
│  └───────────────────────┬──────────────────────────────────────┘   │
│                          │                                          │
│          ┌───────────────┼───────────────┐                          │
│          │               │               │                          │
│  ┌───────▼──────┐ ┌─────▼──────┐ ┌──────▼───────┐                  │
│  │ Compute      │ │ Compute    │ │ Compute      │                  │
│  │ Node 1       │ │ Node 2     │ │ Node N       │                  │
│  │              │ │            │ │              │                  │
│  │ ┌──────────┐ │ │ ┌────────┐ │ │ ┌──────────┐ │                  │
│  │ │ Slice 1  │ │ │ │ Slice 1│ │ │ │ Slice 1  │ │                  │
│  │ │ (CPU+Mem │ │ │ │        │ │ │ │          │ │                  │
│  │ │  +Disk)  │ │ │ │        │ │ │ │          │ │                  │
│  │ ├──────────┤ │ │ ├────────┤ │ │ ├──────────┤ │                  │
│  │ │ Slice 2  │ │ │ │ Slice 2│ │ │ │ Slice 2  │ │                  │
│  │ └──────────┘ │ │ └────────┘ │ │ └──────────┘ │                  │
│  └──────────────┘ └────────────┘ └──────────────┘                  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │            Redshift Managed Storage (RMS / S3)                │   │
│  │  - RA3 nodes: data persisted in S3, local SSD as cache        │   │
│  │  - Scale storage independently from compute                    │   │
│  │  - Automatic tiering: hot data on SSD, warm/cold on S3        │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

**Leader Node** responsibilities:
- Receives SQL from client applications (JDBC/ODBC)
- Parses, optimizes, and generates the query execution plan
- Compiles code and distributes it to compute nodes
- Handles metadata operations (DDL) and result aggregation
- For single-node clusters, the leader node also serves as the compute node

**Compute Nodes** are partitioned into **slices**:
- Each slice is allocated a portion of the node's memory and disk space
- A slice processes its assigned portion of the workload in parallel
- The number of slices per node depends on the node type (e.g., ra3.xlplus = 2 slices)
- Data is distributed across slices according to the table's distribution style

#### Node Types (2025-2026)

| Node Type | vCPU | Memory | Managed Storage | Slices/Node | Price/hr (On-Demand) | Use Case |
|-----------|------|--------|-----------------|-------------|---------------------|----------|
| ra3.xlplus | 4 | 32 GB | 32 TB | 2 | ~$1.086 | Dev/test, small workloads |
| ra3.4xlarge | 12 | 96 GB | 128 TB | 4 | ~$3.26 | General production |
| ra3.16xlarge | 48 | 384 GB | 128 TB | 16 | ~$13.04 | Large-scale production |
| dc2.large | 2 | 15 GB | 160 GB SSD | 2 | ~$0.25 | Small, SSD-only (legacy) |
| dc2.8xlarge | 32 | 244 GB | 2.56 TB SSD | 16 | ~$4.80 | SSD-only, high performance |

**RA3 vs DC2**: RA3 nodes decouple storage and compute using Redshift Managed Storage
(RMS) backed by S3. Local SSD serves as a high-performance cache. DC2 nodes store data
locally on SSD only — no managed storage separation. AWS recommends RA3 for all new
clusters.

### 1.2 Data Distribution Styles

When you create a table, you choose a distribution style that determines how rows are
distributed across compute node slices. The right distribution minimizes data movement
during JOINs and aggregations.

#### Distribution Style Options

| Style | How It Works | Best For |
|-------|-------------|----------|
| **AUTO** | Redshift auto-selects based on table size (starts ALL → KEY → EVEN) | Default; most tables |
| **KEY** | Rows with same key value go to same slice | Large fact tables joined on a specific column |
| **ALL** | Full copy of table on every node | Small dimension tables (< ~200K rows) |
| **EVEN** | Round-robin across all slices | Tables not joined with other tables |

```sql
-- KEY distribution on customer_id (collocate with fact table)
CREATE TABLE orders (
    order_id       BIGINT IDENTITY(1,1),
    customer_id    BIGINT NOT NULL,
    order_date     DATE NOT NULL,
    total_amount   DECIMAL(12,2),
    status         VARCHAR(20)
)
DISTKEY(customer_id)
SORTKEY(order_date);

-- ALL distribution for small dimension table
CREATE TABLE product_categories (
    category_id    INT PRIMARY KEY,
    category_name  VARCHAR(100),
    parent_id      INT
)
DISTSTYLE ALL;

-- EVEN distribution (no joins expected)
CREATE TABLE audit_logs (
    log_id         BIGINT IDENTITY(1,1),
    event_time     TIMESTAMP DEFAULT GETDATE(),
    event_type     VARCHAR(50),
    details        VARCHAR(4000)
)
DISTSTYLE EVEN
SORTKEY(event_time);

-- AUTO distribution (recommended default)
CREATE TABLE user_sessions (
    session_id     VARCHAR(64),
    user_id        BIGINT,
    start_time     TIMESTAMP,
    end_time       TIMESTAMP,
    page_views     INT
)
DISTSTYLE AUTO;
```

#### Checking Distribution Style

```sql
-- View distribution style for all tables
SELECT "schema", "table", diststyle, sortkey1
FROM svv_table_info
WHERE "schema" = 'public'
ORDER BY "table";

-- Check data skew across slices
SELECT slice, COUNT(*) AS row_count
FROM stv_blocklist
WHERE tbl = (SELECT oid FROM pg_class WHERE relname = 'orders')
GROUP BY slice
ORDER BY slice;
```

### 1.3 Sort Keys

Sort keys determine the physical ordering of data on disk. They enable zone map
effectiveness — Redshift maintains min/max metadata per 1MB block and can skip
blocks that don't match the query filter.

| Sort Key Type | Behavior | Best For |
|---------------|----------|----------|
| **Compound** | Data sorted by columns in defined order (prefix matters) | Range-restricted queries, date-based filtering |
| **Interleaved** | Equal weight to each column in the sort key | Ad-hoc queries with varying filter columns |
| **Auto** | Redshift automatically manages sort order | Default; most tables |

```sql
-- Compound sort key (most common)
-- Queries filtering on order_date benefit most
-- Queries on order_date + status also benefit
-- Queries on status alone get NO benefit (prefix rule)
CREATE TABLE sales (
    sale_id        BIGINT,
    order_date     DATE,
    status         VARCHAR(10),
    amount         DECIMAL(12,2)
)
COMPOUND SORTKEY(order_date, status);

-- Interleaved sort key (multi-column ad-hoc)
-- Equal benefit for queries on ANY column
-- BUT: VACUUM REINDEX is expensive
CREATE TABLE events (
    event_id       BIGINT,
    event_type     VARCHAR(50),
    region         VARCHAR(20),
    event_date     DATE
)
INTERLEAVED SORTKEY(event_type, region, event_date);

-- Auto sort key (let Redshift decide)
CREATE TABLE metrics (
    metric_id      BIGINT,
    metric_name    VARCHAR(100),
    value          DOUBLE PRECISION,
    recorded_at    TIMESTAMP
)
SORTKEY AUTO;
```

**Best practices:**
- Use compound sort keys for time-series data (most common pattern)
- Avoid interleaved sort keys unless you have genuinely unpredictable query patterns
  (they make VACUUM significantly more expensive)
- Auto sort key is the safest default

### 1.4 Workload Management (WLM)

WLM controls how queries are routed to queues and how resources are allocated.

#### Automatic WLM (Recommended)

```sql
-- Check current WLM configuration
SELECT * FROM stv_wlm_configuration;

-- With automatic WLM, Redshift manages:
-- - Queue assignment
-- - Memory allocation
-- - Concurrency (up to auto-scaled max)
-- - Query priority

-- Create a query monitoring rule
CREATE QUERY MONITORING RULE long_running_query
    WHEN query_execution_time > 300  -- 5 minutes
    THEN LOG;

-- Set query priority for a user group
ALTER USER analytics_team SET QUERY_GROUP TO 'high_priority';
```

#### Manual WLM Configuration

Manual WLM allows fine-grained control but requires ongoing tuning:

```json
// Parameter group WLM JSON configuration
[
  {
    "query_group": ["etl_jobs"],
    "query_group_wild_card": 0,
    "user_group": ["etl_user"],
    "user_group_wild_card": 0,
    "concurrency_scaling": "auto",
    "memory_percent_to_use": 50,
    "max_execution_time": 7200000,
    "query_concurrency": 5
  },
  {
    "query_group": ["dashboard"],
    "memory_percent_to_use": 30,
    "query_concurrency": 15
  },
  {
    "query_group": [],
    "memory_percent_to_use": 20,
    "query_concurrency": 5
  }
]
```

#### Concurrency Scaling

When query load exceeds the configured concurrency, Redshift can automatically add
transient clusters to handle the burst:

- Enabled per WLM queue
- Each cluster gets 1 hour free per day per main cluster (accrues when not in use)
- Beyond free credits: billed at on-demand rate per second
- Supports read queries and write queries (INSERT, DELETE, UPDATE, COPY, UNLOAD)

### 1.5 Redshift Serverless

Redshift Serverless eliminates cluster management entirely — no provisioning, scaling,
or maintenance required.

#### Key Concepts

```
┌─────────────────────────────────────────────────┐
│             Redshift Serverless                  │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │  Namespace (logical container)            │   │
│  │  - Databases, schemas, tables, users      │   │
│  │  - Encryption settings                    │   │
│  │  - IAM roles                              │   │
│  └──────────────┬───────────────────────────┘   │
│                 │                                │
│  ┌──────────────▼───────────────────────────┐   │
│  │  Workgroup (compute)                      │   │
│  │  - Base RPU capacity (min 8)              │   │
│  │  - Max RPU capacity ceiling               │   │
│  │  - Auto-pause and auto-resume             │   │
│  │  - VPC, security group, subnet config     │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  Multiple workgroups → 1 namespace (shared data) │
│  1 workgroup → 1 namespace only                  │
└─────────────────────────────────────────────────┘
```

**RPU (Redshift Processing Unit):**
- 1 RPU = unit of compute capacity
- Minimum: 8 RPU (reduced from 32 in late 2024)
- Maximum: 512 RPU
- Billed per second, only when queries are running
- Price: ~$0.375/RPU-hour

#### Serverless vs Provisioned Comparison

| Feature | Serverless | Provisioned |
|---------|------------|-------------|
| **Management** | Zero cluster management | You manage cluster config |
| **Scaling** | Auto-scales RPU (8-512) | Manual resize or elastic resize |
| **Pricing** | Per RPU-second (~$0.375/RPU-hr) | Per node-hour |
| **Minimum** | 8 RPU | 1 node |
| **Idle cost** | None (auto-pause after idle) | Yes (24/7 unless paused manually) |
| **Concurrency** | Auto-scales | WLM config + concurrency scaling |
| **Maintenance** | Automatic, transparent | Weekly maintenance windows |
| **Snapshots** | Included | Included (manual + automated) |
| **Reserved pricing** | 1yr: ~20%, 3yr: ~45% off | 1yr: ~25%, 3yr: ~75% off |
| **Best for** | Variable/unpredictable workloads | Steady, predictable workloads |
| **Data sharing** | Yes | Yes (RA3 required, encrypted) |
| **Zero-ETL** | Yes | Yes (RA3 required) |

```sql
-- Example: Configure serverless workgroup via AWS CLI
-- aws redshift-serverless create-workgroup \
--   --workgroup-name "analytics-wg" \
--   --namespace-name "analytics-ns" \
--   --base-capacity 32 \
--   --max-capacity 128 \
--   --config-parameters "max_query_execution_time=3600"

-- Check serverless usage
SELECT * FROM sys_serverless_usage
ORDER BY start_time DESC
LIMIT 20;

-- Monitor RPU consumption
SELECT
    DATE_TRUNC('hour', start_time) AS hour,
    AVG(compute_capacity) AS avg_rpu,
    MAX(compute_capacity) AS max_rpu,
    SUM(data_storage) AS total_storage_mb
FROM sys_serverless_usage
WHERE start_time > DATEADD(day, -7, GETDATE())
GROUP BY 1
ORDER BY 1;
```

### 1.6 Key Features Deep Dive

#### Materialized Views with Auto-Refresh

```sql
-- Create a materialized view with auto-refresh
CREATE MATERIALIZED VIEW mv_daily_sales
AUTO REFRESH YES
AS
SELECT
    DATE_TRUNC('day', order_date) AS sale_date,
    product_category,
    COUNT(*) AS order_count,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS avg_order_value
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY 1, 2;

-- Query the materialized view
SELECT * FROM mv_daily_sales
WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY total_revenue DESC;

-- Manual refresh
REFRESH MATERIALIZED VIEW mv_daily_sales;

-- Check refresh status
SELECT mv_name, state, autorewrite, autorefresh
FROM stv_mv_info;
```

#### SUPER Data Type (Semi-Structured Data)

Redshift's SUPER type stores semi-structured data (JSON) natively with
PartiQL query support:

```sql
-- Create table with SUPER column
CREATE TABLE customer_events (
    event_id       BIGINT IDENTITY(1,1),
    event_time     TIMESTAMP DEFAULT GETDATE(),
    customer_id    BIGINT,
    event_data     SUPER   -- stores JSON natively
);

-- Insert JSON data
INSERT INTO customer_events (customer_id, event_data)
VALUES (
    12345,
    JSON_PARSE('{"action": "purchase", "items": [{"sku": "A1", "qty": 2, "price": 29.99}, {"sku": "B2", "qty": 1, "price": 49.99}], "metadata": {"source": "mobile", "version": "3.1"}}')
);

-- Query nested SUPER data using PartiQL dot notation
SELECT
    customer_id,
    event_data.action AS action,
    event_data.metadata.source AS source,
    event_data.items[0].sku AS first_item_sku,
    event_data.items[0].price AS first_item_price
FROM customer_events
WHERE event_data.action = 'purchase';

-- Unnest arrays
SELECT
    ce.customer_id,
    item.sku,
    item.qty,
    item.price
FROM customer_events ce, ce.event_data.items AS item
WHERE ce.event_data.action = 'purchase';

-- Aggregate across semi-structured data
SELECT
    event_data.metadata.source::VARCHAR AS source,
    COUNT(*) AS event_count,
    SUM(item.price * item.qty) AS total_value
FROM customer_events ce, ce.event_data.items AS item
GROUP BY 1;
```

#### Streaming Ingestion (Kinesis / MSK)

Streaming ingestion allows near real-time data landing in Redshift via
materialized views over Kinesis Data Streams or Amazon MSK (Kafka).

```sql
-- Step 1: Create external schema for Kinesis stream
CREATE EXTERNAL SCHEMA kinesis_schema
FROM KINESIS
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftStreamRole';

-- Step 2: Create materialized view with auto-refresh
CREATE MATERIALIZED VIEW mv_clickstream
AUTO REFRESH YES
AS
SELECT
    approximate_arrival_timestamp,
    partition_key,
    shard_id,
    sequence_number,
    refresh_time,
    JSON_PARSE(kinesis_data) AS payload
FROM kinesis_schema."clickstream-events"
WHERE is_utf8(kinesis_data)
  AND is_valid_json(from_varbyte(kinesis_data, 'utf-8'));

-- Step 3: Query the streaming data
SELECT
    DATE_TRUNC('minute', approximate_arrival_timestamp) AS minute,
    payload.page::VARCHAR AS page,
    COUNT(*) AS click_count
FROM mv_clickstream
WHERE approximate_arrival_timestamp > GETDATE() - INTERVAL '1 hour'
GROUP BY 1, 2
ORDER BY 1 DESC, 3 DESC;

-- For MSK (Kafka) streaming ingestion:
CREATE EXTERNAL SCHEMA kafka_schema
FROM MSK
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftMSKRole'
AUTHENTICATION IAM
CLUSTER_ARN 'arn:aws:kafka:us-east-1:123456789012:cluster/my-cluster/abc123';

CREATE MATERIALIZED VIEW mv_kafka_events
AUTO REFRESH YES
AS
SELECT
    kafka_timestamp,
    kafka_key,
    kafka_partition,
    kafka_offset,
    kafka_headers,
    JSON_PARSE(kafka_value) AS payload
FROM kafka_schema."loyalty-events"
WHERE is_utf8(kafka_value)
  AND is_valid_json(from_varbyte(kafka_value, 'utf-8'));
```

#### Data Sharing

```sql
-- PRODUCER cluster: Create a datashare
CREATE DATASHARE sales_share SET PUBLICACCESSIBLE FALSE;

-- Add schema and tables to the datashare
ALTER DATASHARE sales_share ADD SCHEMA public;
ALTER DATASHARE sales_share ADD TABLE public.orders;
ALTER DATASHARE sales_share ADD TABLE public.customers;
ALTER DATASHARE sales_share ADD ALL TABLES IN SCHEMA analytics;

-- Grant access to consumer namespace
GRANT USAGE ON DATASHARE sales_share
TO NAMESPACE 'a1b2c3d4-5678-90ab-cdef-EXAMPLE11111';

-- CONSUMER cluster: Create database from datashare
CREATE DATABASE sales_db FROM DATASHARE sales_share
OF NAMESPACE 'f1e2d3c4-5678-90ab-cdef-EXAMPLE22222';

-- Query shared data (read-only)
SELECT * FROM sales_db.public.orders
WHERE order_date >= '2026-01-01';
```

#### Zero-ETL Integrations

Zero-ETL enables near real-time replication from operational databases to Redshift
without building ETL pipelines.

```
┌──────────────────┐     Zero-ETL     ┌──────────────────┐
│ Aurora MySQL      │ ──────────────▶ │                  │
│ Aurora PostgreSQL │                  │  Amazon Redshift │
│ RDS MySQL        │     (auto CDC)   │  (Serverless or  │
│ DynamoDB          │ ──────────────▶ │   RA3 cluster)   │
└──────────────────┘                  └──────────────────┘
```

**Requirements:**
- Redshift: Serverless or RA3 node type, encrypted (provisioned)
- Case sensitivity: must be enabled on Redshift
- Aurora/RDS: binlog enabled (MySQL) or logical replication (PostgreSQL)
- DynamoDB: Point-in-Time Recovery (PITR) enabled

**Latency:**
- Aurora MySQL: < 15 seconds (p50) for 1M+ transactions/minute
- Aurora PostgreSQL: similar performance
- DynamoDB: 15-30 minute incremental exports

```sql
-- After Zero-ETL integration is configured via console/CLI:

-- Check integration status
SELECT integration_id, source_arn, target_database,
       status, error_message
FROM svv_integration;

-- Query replicated data directly
SELECT * FROM aurora_schema.customers
WHERE last_updated > DATEADD(hour, -1, GETDATE());

-- Create local materialized views for performance
CREATE MATERIALIZED VIEW mv_active_customers
AUTO REFRESH YES
AS
SELECT customer_id, name, email, tier, last_purchase_date
FROM aurora_schema.customers
WHERE status = 'active';
```

#### Redshift ML

```sql
-- Create a churn prediction model using SageMaker Autopilot
CREATE MODEL customer_churn_model
FROM (
    SELECT
        tenure_months,
        monthly_spend,
        support_tickets,
        login_frequency,
        churned  -- target column (0 or 1)
    FROM customer_features
    WHERE sample_date < '2026-01-01'
)
TARGET churned
FUNCTION predict_churn
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftMLRole'
SETTINGS (
    S3_BUCKET 'my-redshift-ml-bucket',
    MAX_RUNTIME 3600
);

-- Check model status
SHOW MODEL customer_churn_model;

-- Use the model for predictions
SELECT
    customer_id,
    name,
    predict_churn(tenure_months, monthly_spend, support_tickets, login_frequency) AS churn_prediction,
    predict_churn_prob(tenure_months, monthly_spend, support_tickets, login_frequency) AS churn_probability
FROM customer_features
WHERE predict_churn(tenure_months, monthly_spend, support_tickets, login_frequency) = 1
ORDER BY churn_probability DESC
LIMIT 100;
```

#### AQUA (Advanced Query Accelerator)

AQUA pushes computation down to the storage layer, reducing data movement between
storage and compute:

- Available on ra3.16xlarge and ra3.4xlarge nodes
- Accelerates queries with LIKE, SIMILAR TO, date functions, and aggregations
- Uses custom FPGA-based hardware in the storage layer
- No code changes required — transparent acceleration
- Automatically enabled on supported node types

### 1.7 Redshift Spectrum

Query data directly in S3 without loading into Redshift, using the same SQL dialect.

```sql
-- Create external schema referencing Glue Catalog
CREATE EXTERNAL SCHEMA spectrum_schema
FROM DATA CATALOG
DATABASE 'my_lake_db'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftSpectrumRole'
CREATE EXTERNAL DATABASE IF NOT EXISTS;

-- Create external table for Parquet data in S3
CREATE EXTERNAL TABLE spectrum_schema.raw_events (
    event_id       VARCHAR(64),
    event_type     VARCHAR(50),
    user_id        BIGINT,
    event_data     VARCHAR(65535),
    event_time     TIMESTAMP
)
PARTITIONED BY (event_date DATE)
STORED AS PARQUET
LOCATION 's3://my-data-lake/raw/events/';

-- Add partitions
ALTER TABLE spectrum_schema.raw_events
ADD PARTITION (event_date='2026-03-01')
LOCATION 's3://my-data-lake/raw/events/event_date=2026-03-01/';

-- Or use MSCK to discover partitions automatically
-- (requires Hive-compatible partition directory structure)

-- Join S3 data with local Redshift tables
SELECT
    e.event_type,
    c.customer_name,
    c.tier,
    COUNT(*) AS event_count
FROM spectrum_schema.raw_events e
JOIN public.customers c ON e.user_id = c.customer_id
WHERE e.event_date >= '2026-03-01'
GROUP BY 1, 2, 3
ORDER BY event_count DESC;
```

**Pricing:** $5 per TB of data scanned from S3 (same as Athena).
Partition pruning and columnar formats (Parquet, ORC) dramatically reduce scan costs.

### 1.8 System Tables and Monitoring

```sql
-- Query execution history (last 7 days)
SELECT
    query,
    SUBSTRING(querytxt, 1, 100) AS query_text,
    starttime,
    endtime,
    DATEDIFF(second, starttime, endtime) AS duration_sec,
    aborted
FROM stl_query
WHERE starttime > DATEADD(day, -1, GETDATE())
  AND userid > 1  -- exclude system queries
ORDER BY duration_sec DESC
LIMIT 20;

-- Table storage usage
SELECT
    "schema",
    "table",
    size AS size_mb,
    pct_used,
    empty AS empty_blocks,
    unsorted,
    stats_off,
    tbl_rows,
    skew_rows
FROM svv_table_info
WHERE "schema" = 'public'
ORDER BY size DESC;

-- Disk space per node
SELECT
    owner AS node,
    used,
    capacity,
    ROUND(used::FLOAT / capacity * 100, 2) AS pct_used
FROM stv_partitions
WHERE type = 0
ORDER BY node;

-- WLM queue wait times
SELECT
    service_class,
    num_queued_queries,
    avg_queue_time / 1000000 AS avg_wait_sec,
    max_queue_time / 1000000 AS max_wait_sec
FROM stl_wlm_query
WHERE starttime > DATEADD(hour, -1, GETDATE())
GROUP BY service_class
ORDER BY avg_wait_sec DESC;

-- Lock contention
SELECT
    l.table_id,
    t.name AS table_name,
    l.lock_owner_pid,
    l.lock_status,
    l.lock_mode
FROM stv_locks l
JOIN stv_tbl_perm t ON l.table_id = t.id
WHERE l.lock_status = 'Waiting';

-- COPY command performance
SELECT
    query,
    SUBSTRING(filename, 1, 60) AS filename,
    lines_scanned,
    bytes_scanned / 1024 / 1024 AS mb_scanned,
    DATEDIFF(second, starttime, endtime) AS duration_sec
FROM stl_load_commits
WHERE starttime > DATEADD(day, -1, GETDATE())
ORDER BY duration_sec DESC;
```

### 1.9 Key Limitations

| Category | Limitation | Workaround |
|----------|-----------|------------|
| Concurrency | Default 5-50 WLM slots | Enable concurrency scaling |
| Maintenance | Weekly windows (provisioned) | Use Serverless |
| Column limit | 1,600 columns per table | Denormalize or use SUPER type |
| Python UDF | **End of support June 2026** | Migrate to Lambda UDFs |
| Serverless min | 8 RPU minimum | Use auto-pause for cost control |
| Data sharing | Requires encrypted clusters (RA3) | Enable encryption at creation |
| Streaming | MV refresh needed (not true real-time) | Use auto-refresh YES |
| VARCHAR max | 65,535 bytes | Use SUPER for large JSON |
| Result cache | 15-minute TTL | Materialized views for longer persistence |
| Cross-region | Not natively supported in Serverless | Use data sharing + provisioned |

---

## 2. Data Lake / Lakehouse on AWS

### 2.1 S3 as Data Lake Storage

Amazon S3 is the foundational storage layer for data lakes on AWS. It provides
virtually unlimited scale, 11 nines (99.999999999%) durability, and deep integration
with every AWS analytics service.

#### Storage Classes

| Class | Storage/GB/mo | Retrieval/GB | Min Duration | Min Object Size | Use Case |
|-------|--------------|-------------|--------------|-----------------|----------|
| Standard | ~$0.023 | Free | None | None | Frequently accessed data |
| Intelligent-Tiering | ~$0.023 | Free | None | 128 KB | Unknown/changing access patterns |
| Standard-IA | ~$0.0125 | $0.01 | 30 days | 128 KB | Infrequent access |
| One Zone-IA | ~$0.01 | $0.01 | 30 days | 128 KB | Re-creatable data |
| Glacier Instant | ~$0.004 | $0.03 | 90 days | 128 KB | Archive with ms retrieval |
| Glacier Flexible | ~$0.0036 | $0.01-$30 | 90 days | 40 KB | Archive (mins-hours retrieval) |
| Glacier Deep Archive | ~$0.00099 | $0.02-$30 | 180 days | 40 KB | Long-term compliance archive |

#### S3 Lifecycle Policy Example

```json
{
  "Rules": [
    {
      "ID": "DataLakeLifecycle",
      "Status": "Enabled",
      "Filter": { "Prefix": "data-lake/" },
      "Transitions": [
        {
          "Days": 90,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 365,
          "StorageClass": "GLACIER_IR"
        },
        {
          "Days": 730,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ]
    },
    {
      "ID": "CleanupOldVersions",
      "Status": "Enabled",
      "Filter": { "Prefix": "" },
      "NoncurrentVersionTransitions": [
        {
          "NoncurrentDays": 30,
          "StorageClass": "STANDARD_IA"
        }
      ],
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 90
      }
    }
  ]
}
```

#### S3 Bucket Policy for Data Lake

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowRedshiftSpectrumAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/RedshiftSpectrumRole"
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-data-lake",
        "arn:aws:s3:::my-data-lake/*"
      ]
    },
    {
      "Sid": "DenyUnencryptedTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": "arn:aws:s3:::my-data-lake/*",
      "Condition": {
        "Bool": { "aws:SecureTransport": "false" }
      }
    }
  ]
}
```

### 2.2 AWS Lake Formation

Lake Formation provides centralized security and governance for data lakes,
simplifying fine-grained access control across all analytics services.

#### Architecture

```
┌─────────────────────────────────────────────────────┐
│                AWS Lake Formation                    │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  Permissions Engine                             │  │
│  │  - Table/Column/Row/Cell-level permissions      │  │
│  │  - LF-Tags (attribute-based access control)     │  │
│  │  - Cross-account sharing                        │  │
│  │  - Data filters (SQL predicates)                │  │
│  └──────────────────────┬─────────────────────────┘  │
│                         │                             │
│  ┌──────────────────────▼─────────────────────────┐  │
│  │  Glue Data Catalog (metadata)                   │  │
│  │  - Databases, tables, partitions                │  │
│  │  - Iceberg REST Catalog API                     │  │
│  │  - Schema versioning                            │  │
│  └──────────────────────┬─────────────────────────┘  │
│                         │                             │
│  ┌──────────────────────▼─────────────────────────┐  │
│  │  Governed Access                                │  │
│  │  Athena / Redshift / EMR / Glue ETL             │  │
│  │  (all query through Lake Formation permissions)  │  │
│  └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

#### LF-Tag Based Access Control

```bash
# Create LF-Tags
aws lakeformation create-lf-tag \
  --tag-key "classification" \
  --tag-values '["public", "internal", "confidential", "restricted"]'

aws lakeformation create-lf-tag \
  --tag-key "domain" \
  --tag-values '["sales", "marketing", "finance", "hr"]'

# Assign tags to a table
aws lakeformation add-lf-tags-to-resource \
  --resource '{"Table": {"DatabaseName": "analytics_db", "Name": "customer_orders"}}' \
  --lf-tags '[{"TagKey": "classification", "TagValues": ["internal"]}, {"TagKey": "domain", "TagValues": ["sales"]}]'

# Grant permissions using tags
aws lakeformation grant-permissions \
  --principal '{"DataLakePrincipalIdentifier": "arn:aws:iam::123456789012:role/AnalystRole"}' \
  --resource '{"LFTagPolicy": {"ResourceType": "TABLE", "Expression": [{"TagKey": "classification", "TagValues": ["public", "internal"]}, {"TagKey": "domain", "TagValues": ["sales"]}]}}' \
  --permissions '["SELECT"]'
```

#### Column-Level and Row-Level Security

```bash
# Grant access to specific columns only
aws lakeformation grant-permissions \
  --principal '{"DataLakePrincipalIdentifier": "arn:aws:iam::123456789012:role/MarketingRole"}' \
  --resource '{"TableWithColumns": {"DatabaseName": "analytics_db", "Name": "customers", "ColumnNames": ["customer_id", "name", "city", "state"]}}' \
  --permissions '["SELECT"]'

# Create a data filter for row-level security
aws lakeformation create-data-cells-filter \
  --table-data '{
    "TableCatalogId": "123456789012",
    "DatabaseName": "analytics_db",
    "TableName": "orders",
    "Name": "us_orders_only",
    "RowFilter": {"FilterExpression": "country = '\''US'\''"},
    "ColumnNames": ["order_id", "customer_id", "order_date", "amount", "country"]
  }'
```

### 2.3 Apache Iceberg on AWS (Strategic Direction)

AWS has made **Iceberg its strategic table format** for the lakehouse layer. Multiple
services now provide first-class Iceberg support.

#### S3 Tables

S3 Tables provide managed Iceberg tables directly in S3 with automatic table
maintenance (compaction, snapshot management, orphan file cleanup).

```
┌──────────────────────────────────────────┐
│              S3 Tables                    │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │  Table Bucket                      │  │
│  │  (S3 bucket with table semantics)  │  │
│  │                                    │  │
│  │  ┌────────────┐ ┌──────────────┐  │  │
│  │  │ Namespace  │ │ Namespace    │  │  │
│  │  │ ┌────────┐ │ │ ┌──────────┐│  │  │
│  │  │ │Table A │ │ │ │ Table C  ││  │  │
│  │  │ ├────────┤ │ │ └──────────┘│  │  │
│  │  │ │Table B │ │ │             │  │  │
│  │  │ └────────┘ │ │             │  │  │
│  │  └────────────┘ └──────────────┘  │  │
│  │                                    │  │
│  │  Auto-compaction: ✓                │  │
│  │  Snapshot management: ✓            │  │
│  │  Orphan file cleanup: ✓            │  │
│  │  Iceberg REST Catalog: ✓           │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

```bash
# Create a table bucket
aws s3tables create-table-bucket \
  --name my-lakehouse-bucket \
  --region us-east-1

# Create a namespace
aws s3tables create-namespace \
  --table-bucket-arn arn:aws:s3tables:us-east-1:123456789012:bucket/my-lakehouse-bucket \
  --namespace sales

# Create a table
aws s3tables create-table \
  --table-bucket-arn arn:aws:s3tables:us-east-1:123456789012:bucket/my-lakehouse-bucket \
  --namespace sales \
  --name orders \
  --format ICEBERG
```

#### Glue Catalog Iceberg REST API

The Glue Data Catalog now exposes a standard Iceberg REST Catalog endpoint,
enabling any Iceberg-compatible engine to access tables.

```python
# PySpark with Glue Catalog Iceberg REST API
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("IcebergOnAWS") \
    .config("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog") \
    .config("spark.sql.catalog.glue_catalog.warehouse", "s3://my-data-lake/iceberg/") \
    .config("spark.sql.catalog.glue_catalog.io-impl", "org.apache.iceberg.aws.s3.S3FileIO") \
    .getOrCreate()

# Create Iceberg table
spark.sql("""
    CREATE TABLE glue_catalog.analytics.events (
        event_id STRING,
        event_type STRING,
        user_id BIGINT,
        event_data STRING,
        event_time TIMESTAMP
    )
    USING iceberg
    PARTITIONED BY (days(event_time))
    TBLPROPERTIES (
        'write.format.default' = 'parquet',
        'write.parquet.compression-codec' = 'zstd',
        'write.metadata.compression-codec' = 'gzip'
    )
""")

# Insert data
spark.sql("""
    INSERT INTO glue_catalog.analytics.events
    VALUES
        ('e1', 'click', 100, '{"page": "/home"}', TIMESTAMP '2026-03-01 10:00:00'),
        ('e2', 'purchase', 101, '{"item": "shoes"}', TIMESTAMP '2026-03-01 11:00:00')
""")

# Time travel query
spark.sql("""
    SELECT * FROM glue_catalog.analytics.events
    VERSION AS OF 1
""").show()

# Read snapshot history
spark.sql("""
    SELECT * FROM glue_catalog.analytics.events.snapshots
""").show()
```

#### Table Optimization

```sql
-- In Athena: Optimize Iceberg table (bin-pack compaction)
OPTIMIZE analytics.events REWRITE DATA
USING BIN_PACK
WHERE event_time >= TIMESTAMP '2026-03-01';

-- Expire old snapshots (keep last 3 days)
ALTER TABLE analytics.events
SET TBLPROPERTIES (
    'history.expire.max-snapshot-age-ms' = '259200000',
    'history.expire.min-snapshots-to-keep' = '5'
);

-- Vacuum orphan files
-- (managed automatically by S3 Tables; manual with Spark for Glue-managed tables)
```

```python
# PySpark: Table optimization with sort compaction
from pyspark.sql import SparkSession

# Bin-pack compaction
spark.sql("""
    CALL glue_catalog.system.rewrite_data_files(
        table => 'analytics.events',
        strategy => 'binpack',
        options => map(
            'target-file-size-bytes', '134217728',
            'min-file-size-bytes', '67108864',
            'max-file-size-bytes', '201326592'
        )
    )
""")

# Sort compaction (Z-Order)
spark.sql("""
    CALL glue_catalog.system.rewrite_data_files(
        table => 'analytics.events',
        strategy => 'sort',
        sort_order => 'zorder(user_id, event_type)'
    )
""")

# Expire snapshots
spark.sql("""
    CALL glue_catalog.system.expire_snapshots(
        table => 'analytics.events',
        older_than => TIMESTAMP '2026-03-01 00:00:00',
        retain_last => 5
    )
""")

# Remove orphan files
spark.sql("""
    CALL glue_catalog.system.remove_orphan_files(
        table => 'analytics.events',
        older_than => TIMESTAMP '2026-02-28 00:00:00'
    )
""")
```

### 2.4 SageMaker Lakehouse / Unified Studio

AWS's vision for unified analytics (consolidating as of 2025-2026):

```
┌─────────────────────────────────────────────────────┐
│           SageMaker Lakehouse / Unified Studio        │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │  SageMaker Catalog (unified metadata)            │ │
│  │  - Replaces fragmented Glue + Lake Formation     │ │
│  │  - Single entry point for discovery              │ │
│  └─────────────────────┬───────────────────────────┘ │
│                        │                              │
│  ┌─────────────┬───────┼───────┬──────────────────┐  │
│  │ S3 Tables   │ Glue  │       │ Redshift         │  │
│  │ (managed    │ Cat.  │       │ (query engine)   │  │
│  │  Iceberg)   │       │       │                  │  │
│  └─────────────┘       │       └──────────────────┘  │
│                        │                              │
│  ┌─────────────────────▼───────────────────────────┐ │
│  │  Lake Formation (unified governance)             │ │
│  │  - FGAC across S3 Tables + Glue + Redshift       │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

**Current state (2025-2026):**
- SageMaker Unified Studio combines data, ML, and AI workflows
- Integrates S3 Tables, Glue Catalog, Lake Formation, Redshift
- Still consolidating — expect feature convergence through 2026
- Not yet a full replacement for individual services

---

## 3. Query Engines

### 3.1 Amazon Athena

Serverless SQL query engine based on Trino (Engine v3), querying data directly in S3.

#### Athena Engine Versions

| Version | Engine | Key Features |
|---------|--------|-------------|
| v2 | Presto | Original engine, stable |
| v3 | Trino | Current default, better performance, more functions |

#### Iceberg Operations in Athena

```sql
-- Create Iceberg table
CREATE TABLE analytics.events (
    event_id    STRING,
    event_type  STRING,
    user_id     BIGINT,
    payload     STRING,
    event_time  TIMESTAMP
)
PARTITIONED BY (DATE(event_time))
LOCATION 's3://my-data-lake/iceberg/events/'
TBLPROPERTIES (
    'table_type' = 'ICEBERG',
    'format' = 'PARQUET',
    'write_compression' = 'ZSTD'
);

-- INSERT
INSERT INTO analytics.events
VALUES ('e1', 'click', 100, '{}', TIMESTAMP '2026-03-01 10:00:00');

-- UPDATE (Iceberg tables only)
UPDATE analytics.events
SET event_type = 'page_view'
WHERE event_id = 'e1';

-- DELETE (Iceberg tables only)
DELETE FROM analytics.events
WHERE event_time < TIMESTAMP '2025-01-01';

-- MERGE (upsert)
MERGE INTO analytics.events AS target
USING staging.new_events AS source
ON target.event_id = source.event_id
WHEN MATCHED THEN
    UPDATE SET event_type = source.event_type, payload = source.payload
WHEN NOT MATCHED THEN
    INSERT (event_id, event_type, user_id, payload, event_time)
    VALUES (source.event_id, source.event_type, source.user_id, source.payload, source.event_time);

-- Time travel
SELECT * FROM analytics.events FOR TIMESTAMP AS OF TIMESTAMP '2026-03-01 00:00:00';
SELECT * FROM analytics.events FOR VERSION AS OF 12345;

-- OPTIMIZE (bin-pack compaction)
OPTIMIZE analytics.events REWRITE DATA USING BIN_PACK;

-- VACUUM (remove old snapshots and orphan files)
VACUUM analytics.events;
```

#### Federated Queries

```sql
-- Query DynamoDB from Athena
SELECT * FROM "lambda:dynamodb_connector".default.users
WHERE partition_key = 'user_123';

-- Query RDS/Aurora from Athena
SELECT * FROM "lambda:rds_connector".my_database.orders
WHERE order_date > DATE '2026-01-01';

-- Join S3 data with DynamoDB data
SELECT
    s3_events.event_type,
    dynamo_users.user_name,
    COUNT(*) AS event_count
FROM analytics.events AS s3_events
JOIN "lambda:dynamodb_connector".default.users AS dynamo_users
    ON s3_events.user_id = dynamo_users.user_id
GROUP BY 1, 2;
```

#### Workgroups and Cost Controls

```bash
# Create a workgroup with cost limits
aws athena create-work-group \
  --name "analytics-team" \
  --configuration '{
    "ResultConfiguration": {
      "OutputLocation": "s3://my-athena-results/analytics/"
    },
    "EnforceWorkGroupConfiguration": true,
    "BytesScannedCutoffPerQuery": 10737418240,
    "RequesterPaysEnabled": false
  }' \
  --description "Analytics team workgroup with 10GB scan limit per query"
```

#### Performance Tuning

```sql
-- Partition projection (avoid MSCK REPAIR for large partition sets)
CREATE EXTERNAL TABLE events_projected (
    event_id  STRING,
    event_data STRING
)
PARTITIONED BY (
    event_date STRING,
    region STRING
)
STORED AS PARQUET
LOCATION 's3://my-data-lake/events/'
TBLPROPERTIES (
    'projection.enabled' = 'true',
    'projection.event_date.type' = 'date',
    'projection.event_date.range' = '2024-01-01,NOW',
    'projection.event_date.format' = 'yyyy-MM-dd',
    'projection.event_date.interval' = '1',
    'projection.event_date.interval.unit' = 'DAYS',
    'projection.region.type' = 'enum',
    'projection.region.values' = 'us-east-1,us-west-2,eu-west-1,ap-southeast-1',
    'storage.location.template' = 's3://my-data-lake/events/event_date=${event_date}/region=${region}/'
);
```

### 3.2 Comparison: Athena vs Spectrum vs Redshift Serverless

| Feature | Athena | Redshift Spectrum | Redshift Serverless |
|---------|--------|-------------------|---------------------|
| **Engine** | Trino (v3) | Redshift MPP | Redshift MPP |
| **Pricing** | $5/TB scanned | $5/TB scanned | $0.375/RPU-hr |
| **Cluster needed** | No | Yes (Redshift) | No (auto-managed) |
| **DML** | INSERT/UPDATE/DELETE (Iceberg) | Via Redshift | Full DML |
| **Performance** | Good (simple queries) | Better (Redshift optimizer) | Best (full MPP) |
| **Concurrency** | 25 DML / 20 DDL | Redshift WLM | Auto-scaling RPU |
| **Joins** | S3 + federated sources | S3 + Redshift local | All Redshift + S3 |
| **Best for** | Ad-hoc S3 queries | Extending existing Redshift | Full warehouse workload |
| **Iceberg support** | Full (read + write) | Read only | Read + write |
| **Use with dbt** | Via connector | Via Redshift adapter | Via Redshift adapter |

**Decision guide:**
1. **Athena** — ad-hoc exploration, data science queries, rare usage
2. **Spectrum** — already have Redshift, want to extend to S3
3. **Serverless** — need full warehouse capabilities, variable workload

---

## 4. AWS Glue

### 4.1 Glue ETL Deep Dive

AWS Glue is a serverless Spark-based ETL engine with integrated data catalog.

#### Glue Versions and Capabilities

| Version | Spark | Python | Key Features |
|---------|-------|--------|-------------|
| Glue 3.0 | 3.1.1 | 3.7 | Delta Lake preview |
| Glue 4.0 | 3.3.0 | 3.10 | Iceberg/Hudi/Delta GA, Ray support |
| Glue 5.0 | 3.5.x | 3.10 | Lake Formation FGAC on Iceberg/Delta/Hudi |
| Glue 5.1 | 3.5.6 | 3.10 | Iceberg v3, materialized views |

#### DynamicFrame vs DataFrame

```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
job.init(args['JOB_NAME'], args)

# DynamicFrame: Glue-native, handles schema inconsistencies
dynamic_frame = glueContext.create_dynamic_frame.from_catalog(
    database="raw_db",
    table_name="clickstream",
    transformation_ctx="source"
)

# Resolve choice types (DynamicFrame feature)
resolved = dynamic_frame.resolveChoice(
    choice="make_cols",
    specs=[("price", "cast:double")]
)

# Convert to DataFrame for complex transformations
df = resolved.toDF()
df_filtered = df.filter(df.event_type == "purchase") \
    .select("user_id", "product_id", "price", "event_time")

# Convert back to DynamicFrame
output_dynamic_frame = DynamicFrame.fromDF(df_filtered, glueContext, "output")

# Write to Iceberg table
glueContext.write_dynamic_frame.from_options(
    frame=output_dynamic_frame,
    connection_type="s3",
    format="iceberg",
    connection_options={
        "path": "s3://my-data-lake/iceberg/purchases/",
        "catalog": "glue_catalog",
        "database": "analytics",
        "table": "purchases"
    },
    transformation_ctx="iceberg_sink"
)

job.commit()
```

#### Glue with Iceberg (PySpark)

```python
# Glue 5.0+ with Iceberg support
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .config("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog") \
    .config("spark.sql.catalog.glue_catalog.warehouse", "s3://my-data-lake/iceberg/") \
    .config("spark.sql.catalog.glue_catalog.io-impl", "org.apache.iceberg.aws.s3.S3FileIO") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .getOrCreate()

# Read from Iceberg table
df = spark.read.format("iceberg").load("glue_catalog.analytics.events")

# Write with MERGE (upsert)
spark.sql("""
    MERGE INTO glue_catalog.analytics.events AS target
    USING updates AS source
    ON target.event_id = source.event_id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""")
```

#### Job Bookmarks

Job bookmarks track processed data to enable incremental processing:

```python
# Enable bookmarks in job parameters: --job-bookmark-option job-bookmark-enable

# Read only new data since last run
dynamic_frame = glueContext.create_dynamic_frame.from_catalog(
    database="raw_db",
    table_name="events",
    transformation_ctx="bookmark_source",  # Key: transformation_ctx enables bookmarks
    additional_options={
        "jobBookmarkKeys": ["event_time"],
        "jobBookmarkKeysSortOrder": "asc"
    }
)
```

#### Glue Crawlers

```bash
# Create a crawler for S3 data
aws glue create-crawler \
  --name "events-crawler" \
  --role "arn:aws:iam::123456789012:role/GlueCrawlerRole" \
  --database-name "raw_db" \
  --targets '{
    "S3Targets": [
      {
        "Path": "s3://my-data-lake/raw/events/",
        "Exclusions": ["**.tmp", "**_SUCCESS"]
      }
    ]
  }' \
  --schema-change-policy '{
    "UpdateBehavior": "UPDATE_IN_DATABASE",
    "DeleteBehavior": "LOG"
  }' \
  --recrawl-policy '{"RecrawlBehavior": "CRAWL_NEW_FOLDERS_ONLY"}'

# Run the crawler
aws glue start-crawler --name "events-crawler"
```

### 4.2 Glue Data Catalog

The Glue Data Catalog is the centralized metadata repository for all data assets on AWS.

```
┌──────────────────────────────────────────────┐
│            Glue Data Catalog                  │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │  Hive Metastore Compatible           │    │
│  │  - Databases, tables, partitions     │    │
│  │  - Schema versioning                 │    │
│  │  - Compatible with EMR, Athena,      │    │
│  │    Redshift Spectrum                  │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │  Iceberg REST Catalog API            │    │
│  │  - Standard Iceberg REST endpoint    │    │
│  │  - Works with Spark, Flink, Trino,   │    │
│  │    DuckDB, PyIceberg                  │    │
│  │  - Catalog federation                │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  Pricing:                                    │
│  - First 1M objects free                     │
│  - $1.00 per 100K objects above free tier    │
│  - First 1M requests free                    │
│  - $1.00 per 1M requests above free tier     │
└──────────────────────────────────────────────┘
```

### 4.3 Glue vs EMR Comparison

| Feature | Glue ETL | EMR on EC2 | EMR Serverless |
|---------|----------|------------|----------------|
| **Management** | Fully serverless | Semi-managed | Serverless |
| **Engine** | Spark, Python, Ray | Spark, Hive, Presto, Flink, HBase | Spark, Hive |
| **Startup time** | ~1 min | 5-15 min | ~1 min |
| **Pricing** | $0.44/DPU-hr | EC2 + ~15-25% EMR surcharge | vCPU+mem per second |
| **Cost at scale** | Higher per-unit | Lowest (Spot + Reserved) | Medium |
| **Spot support** | N/A (serverless) | Yes (60-90% savings) | Yes (Graviton) |
| **Customization** | Limited libraries | Full control | Moderate |
| **Catalogs** | Glue Catalog native | Glue/Hive/Iceberg | Glue/Hive/Iceberg |
| **Interactive** | No (jobs only) | Yes (notebooks, Zeppelin) | No |
| **Best for** | Simple-medium ETL | Complex, cost-sensitive | Bursty Spark jobs |

---

## 5. Amazon EMR

### 5.1 Deployment Options

#### EMR on EC2

Traditional managed Hadoop/Spark clusters:

```bash
# Create an EMR cluster with Spark and Iceberg
aws emr create-cluster \
  --name "analytics-cluster" \
  --release-label emr-7.0.0 \
  --applications Name=Spark Name=Hive Name=JupyterEnterpriseGateway \
  --instance-groups '[
    {"InstanceGroupType":"MASTER","InstanceType":"m5.2xlarge","InstanceCount":1},
    {"InstanceGroupType":"CORE","InstanceType":"r5.2xlarge","InstanceCount":4},
    {"InstanceGroupType":"TASK","InstanceType":"r5.2xlarge","InstanceCount":4,"BidPrice":"OnDemandPrice","Market":"SPOT"}
  ]' \
  --configurations '[
    {
      "Classification": "spark-defaults",
      "Properties": {
        "spark.sql.catalog.glue_catalog": "org.apache.iceberg.spark.SparkCatalog",
        "spark.sql.catalog.glue_catalog.catalog-impl": "org.apache.iceberg.aws.glue.GlueCatalog",
        "spark.sql.catalog.glue_catalog.warehouse": "s3://my-data-lake/iceberg/",
        "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
      }
    },
    {
      "Classification": "iceberg-defaults",
      "Properties": {
        "iceberg.enabled": "true"
      }
    }
  ]' \
  --ec2-attributes KeyName=my-key,SubnetId=subnet-abc123 \
  --service-role EMR_DefaultRole \
  --ec2-instance-profile EMR_EC2_DefaultRole \
  --log-uri s3://my-emr-logs/
```

#### EMR Serverless

```bash
# Create an EMR Serverless application
aws emr-serverless create-application \
  --name "spark-analytics" \
  --type "SPARK" \
  --release-label "emr-7.0.0" \
  --initial-capacity '{
    "DRIVER": {
      "workerCount": 1,
      "workerConfiguration": {
        "cpu": "4 vCPU",
        "memory": "16 GB"
      }
    },
    "EXECUTOR": {
      "workerCount": 10,
      "workerConfiguration": {
        "cpu": "4 vCPU",
        "memory": "16 GB"
      }
    }
  }' \
  --maximum-capacity '{
    "cpu": "200 vCPU",
    "memory": "600 GB",
    "disk": "2000 GB"
  }' \
  --auto-stop-configuration '{"enabled": true, "idleTimeoutMinutes": 15}'

# Submit a job
aws emr-serverless start-job-run \
  --application-id "app-abc123" \
  --execution-role-arn "arn:aws:iam::123456789012:role/EMRServerlessRole" \
  --job-driver '{
    "sparkSubmit": {
      "entryPoint": "s3://my-scripts/etl_job.py",
      "sparkSubmitParameters": "--conf spark.sql.catalog.glue_catalog=org.apache.iceberg.spark.SparkCatalog --conf spark.sql.catalog.glue_catalog.catalog-impl=org.apache.iceberg.aws.glue.GlueCatalog --conf spark.sql.catalog.glue_catalog.warehouse=s3://my-data-lake/iceberg/"
    }
  }'
```

#### EMR on EKS

```bash
# Register a virtual cluster
aws emr-containers create-virtual-cluster \
  --name "analytics-vc" \
  --container-provider '{
    "id": "my-eks-cluster",
    "type": "EKS",
    "info": {
      "eksInfo": {
        "namespace": "emr-spark"
      }
    }
  }'
```

### 5.2 Deployment Comparison

| Feature | EMR on EC2 | EMR Serverless | EMR on EKS |
|---------|-----------|----------------|------------|
| **Management** | Managed cluster | No cluster | Kubernetes |
| **Idle cost** | Yes (cluster runs 24/7) | No (auto-stop) | Shared K8s cluster |
| **Startup** | 5-15 min | ~1 min | ~1 min |
| **Spot instances** | Yes (60-90% savings) | Graviton support | K8s spot nodes |
| **Engines** | Spark, Hive, Presto, Flink, HBase | Spark, Hive | Spark |
| **Interactive** | Yes (notebooks, SSH) | No | No |
| **Best for** | Full control, multi-engine | Bursty jobs, cost control | Multi-tenant K8s platform |

### 5.3 Pricing

**EMR on EC2 (example: r5.2xlarge):**
- EC2: $0.504/hr (On-Demand), ~$0.15/hr (Spot)
- EMR surcharge: ~25% of EC2 price
- Total On-Demand: ~$0.63/hr per node
- Total with Spot: ~$0.19/hr per node (70% savings)

**EMR Serverless:**
- vCPU: $0.052624/hr
- Memory: $0.0057785/GB-hr
- Storage: $0.000111/GB-hr
- Billed per second, 1-min minimum

**Cost optimization strategies:**
1. Use Spot instances for TASK nodes (tolerant of interruption)
2. Right-size instances based on workload profiling
3. Use auto-scaling policies based on YARN metrics
4. Use instance fleets for diversified Spot capacity
5. Consider Graviton instances (up to 30% better price-performance)

### 5.4 Supported Frameworks

| Framework | EMR on EC2 | EMR Serverless | EMR on EKS |
|-----------|-----------|----------------|------------|
| Spark | Yes (3.5.x) | Yes | Yes |
| Hive | Yes (3.x) | Yes | No |
| Presto/Trino | Yes | Yes | No |
| Flink | Yes (1.18+) | Preview | No |
| HBase | Yes | No | No |
| Iceberg | Yes (native) | Yes | Yes |
| Delta Lake | Yes | Yes | Yes |

---

## 6. SageMaker Lakehouse / Unified Studio

### 6.1 Vision and Current State

AWS is converging its data and AI services under SageMaker Unified Studio:

**What it unifies:**
- S3 Tables (managed Iceberg)
- Glue Data Catalog (metadata)
- Lake Formation (governance)
- Redshift (query engine)
- SageMaker (ML/AI)

**Current state (2025-2026):**
- Still in active consolidation phase
- S3 Tables + Glue Iceberg REST integration is production-ready
- Unified Studio is GA but features are still maturing
- Individual services remain fully supported
- Expect continued feature convergence through 2026-2027

**Recommendation:** Use individual services (Glue + Lake Formation + Redshift + S3 Tables)
for production workloads today. Monitor Unified Studio for future consolidation.

---

## 7. Limitations and Known Issues

### 7.1 Service Fragmentation (Critical Issue)

AWS's biggest data platform concern — too many overlapping services create decision
fatigue and integration complexity.

```
Query engines:    Athena, Redshift Spectrum, Redshift Serverless, EMR (Presto/Spark SQL)
ETL:              Glue ETL, EMR, Lambda + S3, Redshift stored procedures
Governance:       Glue Catalog, Lake Formation, DataZone, SageMaker Catalog
Streaming:        Kinesis Data Streams, MSK, Kinesis Firehose
Orchestration:    MWAA (Airflow), Step Functions, EventBridge
```

**Impact:**
- Decision fatigue for new teams
- Integration complexity across services
- Cost unpredictability from multiple billing models
- Skill fragmentation — hard to be expert in all services

### 7.2 Redshift Limitations

| Category | Limitation | Severity |
|----------|-----------|----------|
| Concurrency | 5-50 WLM slots default | Medium |
| Maintenance | Weekly windows (provisioned) | Low |
| Columns | 1,600 per table max | Medium |
| Python UDF | **Deprecated June 2026** → Lambda UDFs | High |
| Serverless min | 8 RPU minimum | Low |
| Streaming | Manual MV refresh (not true real-time) | Medium |
| VARCHAR max | 65,535 bytes | Low |
| Spectrum | $5/TB scanned (no discount) | Medium |
| Cross-AZ | Data transfer costs between AZs | Low |

### 7.3 Athena Limitations

| Category | Limitation | Severity |
|----------|-----------|----------|
| Query timeout | 30 min default (max 240 min) | Medium |
| Concurrent queries | 25 DML / 20 DDL | Medium |
| Query string | 256 KB max | Low |
| Min billing | 10 MB per query | Low |
| Partitions | 10M per table | Low |
| UPDATE/DELETE | Iceberg tables only | Medium |
| Federated | High latency for cross-source joins | Medium |

### 7.4 Glue Limitations

| Category | Limitation | Severity |
|----------|-----------|----------|
| DPU cost | $0.44/DPU-hr (expensive at scale) | High |
| Customization | Limited library install options | Medium |
| Debugging | Limited debugging compared to EMR notebooks | Medium |
| DynamicFrame | Quirky API, harder than native PySpark | Low |
| Crawlers | Can be slow and create unwanted tables | Medium |

### 7.5 Lock-in Assessment

| Service | Lock-in Risk | Mitigation |
|---------|-------------|------------|
| **Redshift** | High | Use standard SQL; avoid distribution/sort key dependency |
| **Athena** | Low-Medium | Trino/Presto compatible; standard SQL |
| **S3** | Low | Standard object storage, open formats |
| **S3 Tables** | Low-Medium | Iceberg format; API is AWS-specific |
| **Glue Catalog** | Medium | Hive-compatible + Iceberg REST API is standard |
| **Lake Formation** | High | No direct equivalent elsewhere |
| **EMR** | Low | Open-source Spark/Flink/Presto |
| **Glue ETL** | Medium | Use standard PySpark; avoid DynamicFrame-only patterns |
| **Zero-ETL** | High | AWS-proprietary; consider Debezium/Airbyte as alternative |
| **Kinesis** | Medium | Use MSK (Kafka) for portability |

---

## 8. Cost Summary

### 8.1 Service-Level Pricing

| Service | Pricing Model | Low Usage | Medium Usage | High Usage |
|---------|--------------|-----------|-------------|------------|
| **Redshift Provisioned** (ra3.xlplus) | Per node-hour | ~$782/mo (1 node) | ~$3,128/mo (4 nodes) | ~$12,512/mo (16 nodes) |
| **Redshift Serverless** | Per RPU-second | ~$50/mo | ~$500/mo | ~$5,000+/mo |
| **Redshift Managed Storage** | Per GB-month | ~$24/mo (1 TB) | ~$240/mo (10 TB) | ~$2,400/mo (100 TB) |
| **Athena** | $5/TB scanned | ~$5/mo | ~$50/mo | ~$500/mo |
| **Glue ETL** | $0.44/DPU-hr | ~$32/mo | ~$316/mo | ~$9,504/mo |
| **Glue Catalog** | Per object + request | FREE (<1M) | ~$10/mo | ~$100/mo |
| **EMR on EC2** (r5.2xlarge) | Instance + surcharge | ~$454/mo (1 node) | ~$1,814/mo (4 nodes) | ~$7,257/mo (16 nodes) |
| **EMR Serverless** | vCPU+memory/hr | ~$50/mo | ~$500/mo | ~$5,000+/mo |
| **S3 Standard** | Per GB-month | ~$23/mo (1 TB) | ~$230/mo (10 TB) | ~$2,300/mo (100 TB) |
| **Lake Formation** | FREE | FREE | FREE | FREE |

### 8.2 Scenario-Based Costs

#### Small Team (10 users, 1 TB, ~100 queries/day)

| Component | Approach A: Athena | Approach B: Serverless | Approach C: Provisioned |
|-----------|-------------------|----------------------|----------------------|
| Query engine | ~$50/mo | ~$200/mo | ~$782/mo |
| Storage (S3) | ~$23/mo | ~$23/mo | ~$24/mo (RMS) |
| Catalog | FREE | FREE | FREE |
| ETL (Glue) | ~$30/mo | ~$30/mo | ~$30/mo |
| **Total** | **~$103/mo** | **~$253/mo** | **~$836/mo** |
| **Best for** | Ad-hoc, cost-sensitive | Variable workloads | Predictable, dashboard-heavy |

#### Medium Enterprise (50 users, 50 TB, ~1,000 queries/day)

| Component | Cost Range |
|-----------|-----------|
| Redshift (provisioned, 4 RA3 nodes) | ~$3,100-9,400/mo |
| S3 storage (raw + processed) | ~$1,150/mo |
| Glue ETL | ~$500-2,000/mo |
| Streaming (MSK/Kinesis) | ~$500-1,500/mo |
| Lake Formation + Catalog | ~$10/mo |
| **Total** | **~$5,300-14,000/mo** |

### 8.3 Cost Optimization Strategies

1. **Redshift Reserved Instances**: 1-year (25% off), 3-year (75% off) for provisioned
2. **Serverless Reservations**: 1-year (20% off), 3-year (45% off)
3. **EMR Spot instances**: 60-90% savings on task nodes
4. **Athena**: Use columnar formats (Parquet/ORC) + partitioning to reduce scan
5. **S3 lifecycle policies**: Auto-tier data to cheaper storage classes
6. **Glue**: Use auto-scaling, right-size DPUs, enable job bookmarks
7. **Data compression**: ZSTD for Parquet files (30-50% smaller than Snappy)

---

## 9. References

### Official AWS Documentation
- [Amazon Redshift Architecture](https://docs.aws.amazon.com/redshift/latest/dg/c_high_level_system_architecture.html)
- [Redshift Distribution Styles](https://docs.aws.amazon.com/redshift/latest/dg/c_choosing_dist_sort.html)
- [Redshift Sort Keys](https://docs.aws.amazon.com/redshift/latest/dg/t_Sorting_data.html)
- [Redshift WLM](https://docs.aws.amazon.com/redshift/latest/dg/cm-c-implementing-workload-management.html)
- [Redshift Serverless](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-billing.html)
- [Redshift Pricing](https://aws.amazon.com/redshift/pricing/)
- [Redshift Quotas and Limits](https://docs.aws.amazon.com/redshift/latest/mgmt/amazon-redshift-limits.html)
- [Redshift Streaming Ingestion](https://docs.aws.amazon.com/redshift/latest/dg/materialized-view-streaming-ingestion.html)
- [Redshift ML](https://aws.amazon.com/redshift/features/redshift-ml/)
- [Redshift Zero-ETL](https://docs.aws.amazon.com/redshift/latest/mgmt/zero-etl-using.html)
- [Redshift Data Sharing](https://docs.aws.amazon.com/redshift/latest/dg/datashare-overview.html)
- [Redshift SUPER Data Type](https://docs.aws.amazon.com/redshift/latest/dg/r_SUPER_type.html)
- [Redshift AQUA](https://docs.aws.amazon.com/redshift/latest/mgmt/managing-cluster-aqua.html)
- [Redshift Concurrency Scaling](https://docs.aws.amazon.com/redshift/latest/dg/concurrency-scaling.html)
- [Redshift Python UDF End of Support](https://aws.amazon.com/blogs/big-data/amazon-redshift-python-user-defined-functions-will-reach-end-of-support-after-june-30-2026/)
- [S3 Storage Classes](https://aws.amazon.com/s3/storage-classes/)
- [Lake Formation](https://docs.aws.amazon.com/lake-formation/latest/dg/what-is-lake-formation.html)
- [Lake Formation LF-Tags](https://docs.aws.amazon.com/lake-formation/latest/dg/tag-based-access-control.html)
- [S3 Tables](https://aws.amazon.com/s3/features/tables/)
- [Glue Iceberg REST Catalog](https://docs.aws.amazon.com/glue/latest/dg/connect-glu-iceberg-rest.html)
- [Glue Documentation](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)
- [Glue Pricing](https://aws.amazon.com/glue/pricing/)
- [Glue Job Bookmarks](https://docs.aws.amazon.com/glue/latest/dg/monitor-continuations.html)
- [Glue Crawlers](https://docs.aws.amazon.com/glue/latest/dg/add-crawler.html)
- [Athena Documentation](https://docs.aws.amazon.com/athena/latest/ug/what-is.html)
- [Athena Pricing](https://aws.amazon.com/athena/pricing/)
- [Athena Quotas](https://docs.aws.amazon.com/athena/latest/ug/service-limits.html)
- [Athena Partition Projection](https://docs.aws.amazon.com/athena/latest/ug/partition-projection.html)
- [Athena Iceberg](https://docs.aws.amazon.com/athena/latest/ug/querying-iceberg.html)
- [EMR Documentation](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-what-is-emr.html)
- [EMR Pricing](https://aws.amazon.com/emr/pricing/)
- [EMR Serverless](https://aws.amazon.com/emr/serverless/)
- [EMR on EKS](https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/emr-eks.html)
- [SageMaker Lakehouse](https://docs.aws.amazon.com/sagemaker-lakehouse-architecture/latest/userguide/s3-tables-integration.html)

### Third-Party Analysis
- [Redshift Pricing Guide — CloudChipr](https://cloudchipr.com/blog/amazon-redshift-pricing)
- [Redshift Pricing Guide — RudderStack](https://www.rudderstack.com/blog/amazon-redshift-pricing/)
- [Redshift Architecture — Medium](https://medium.com/@KuldeepsinhVaghela/amazon-redshift-architecture-explained-leader-node-compute-nodes-and-performance-tuning-197ec98c6e7a)
- [Glue Pricing Breakdown — CloudChipr](https://cloudchipr.com/blog/aws-glue-pricing)
- [EMR Pricing Guide — CloudChipr](https://cloudchipr.com/blog/aws-emr)
- [AWS Analytics re:Invent 2025](https://aws.amazon.com/blogs/big-data/aws-analytics-at-reinvent-2025-unifying-data-ai-and-governance-at-scale/)
- [2025-2026 Lakehouse Ecosystem Guide — DEV Community](https://dev.to/alexmercedcoder/the-2025-2026-ultimate-guide-to-the-data-lakehouse-and-the-data-lakehouse-ecosystem-dig)

---

> **Document Version**: 2.0 | **Last Updated**: 2026-03-05
