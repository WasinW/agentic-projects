# GCP Data Platform: Data Warehouse & Lakehouse

> Comprehensive knowledge base covering BigQuery, BigLake, Apache Iceberg on GCP,
> and the Lakehouse architecture pattern used in the loyalty/messaging/sales data platform.
>
> **Version**: 2.0 | **Last Updated**: 2026-03-05 | **Maintainer**: Data Platform Team

---

## Table of Contents

1. [BigQuery as Data Warehouse](#1-bigquery-as-data-warehouse)
2. [BigLake Lakehouse](#2-biglake-lakehouse)
3. [Data Lake on GCP](#3-data-lake-on-gcp)
4. [Lakehouse Architecture Pattern on GCP](#4-lakehouse-architecture-pattern-on-gcp)
5. [Limitations and Known Issues](#5-limitations-and-known-issues)
6. [Cost Summary Table](#6-cost-summary-table)
7. [References](#7-references)

---

## 1. BigQuery as Data Warehouse

### 1.1 Architecture Overview

BigQuery is a serverless, highly scalable, multi-cloud data warehouse designed for
business agility. Its architecture is built on four core Google technologies that
separate compute from storage and enable massive parallelism.

#### The Four Pillars

```
+-------------------------------------------------------------+
|                     BigQuery Service                        |
|                                                             |
|  +----------+  +----------+  +----------+  +------------+  |
|  |  Dremel  |  | Colossus |  |   Borg   |  |  Jupiter   |  |
|  | (Compute)|  | (Storage)|  | (Cluster)|  | (Network)  |  |
|  +----------+  +----------+  +----------+  +------------+  |
|                                                             |
|  +---------------------------------------------------------+|
|  |              Capacitor (Column Format)                  ||
|  +---------------------------------------------------------+|
+-------------------------------------------------------------+
```

#### Dremel (Compute Engine)

Dremel is BigQuery's execution engine, named after the original Google research paper
(2010). It uses a multi-level serving tree architecture to execute queries:

- **Root Server**: Receives the SQL query, parses it, and creates a query execution plan.
- **Intermediate Nodes (Mixers)**: Aggregate partial results from leaf nodes.
- **Leaf Nodes (Slots)**: Execute the actual computation on data partitions in parallel.

A single query can leverage thousands of leaf nodes simultaneously. Each "slot" is a
unit of computational capacity -- roughly equivalent to half a virtual CPU with a portion
of RAM. The tree structure enables BigQuery to scan petabytes of data in seconds.

Key characteristics:
- Column-oriented processing (reads only the columns needed)
- In-memory shuffle for JOINs and aggregations
- Dynamic query planning with adaptive re-partitioning
- Supports Standard SQL (ANSI:2011 compliant)

#### Colossus (Distributed Storage)

Colossus is Google's next-generation distributed file system (successor to GFS).
BigQuery stores all data on Colossus in a proprietary columnar format called Capacitor.

Key characteristics:
- Automatic replication (erasure coding + replicas) for durability
- Transparent compression per column (dictionary, run-length, delta encoding)
- Data stored in Capacitor format -- optimized for nested/repeated fields
- Storage is completely decoupled from compute -- data persists independently
- Automatic storage optimization (e.g., compaction, re-encoding)
- Supports both managed storage and external data references

#### Borg (Cluster Management)

Borg is Google's cluster management system (precursor to Kubernetes). In BigQuery's
context, Borg handles:

- Allocating compute resources (slots) to queries
- Scheduling and prioritizing workloads across thousands of machines
- Managing fault tolerance -- automatically restarting failed tasks
- Multi-tenant isolation between different customers' workloads
- Bin-packing to maximize resource utilization across Google's fleet

Borg ensures that BigQuery can serve thousands of concurrent users without any single
customer needing to manage infrastructure.

#### Jupiter (Network Fabric)

Jupiter is Google's petabit-scale datacenter network that enables BigQuery's
storage-compute separation:

- Provides 1 Petabit/sec bisection bandwidth within a datacenter
- Enables Dremel (compute) to read from Colossus (storage) at enormous throughput
- Supports the in-memory shuffle for distributed JOINs
- Makes storage-compute separation practical with negligible latency overhead
- Critical for enabling the "serverless" experience -- data does not need to be
  co-located with compute

#### Capacitor (Columnar Format)

Though not one of the four "pillars," Capacitor is BigQuery's proprietary columnar
storage format:

- Stores data column-by-column (not row-by-row)
- Each column independently compressed with optimal encoding
- Supports complex nested types (STRUCT, ARRAY) natively via Dremel encoding
- Automatic statistics collection (min/max/count per column segment)
- Enables partition pruning and column pruning at the storage layer

### 1.2 Editions

BigQuery offers three editions, each targeting different organizational needs. All
editions use the same underlying architecture.

| Feature | Standard | Enterprise | Enterprise Plus |
|---|---|---|---|
| **Target Use Case** | Cost-sensitive, smaller workloads | General enterprise | Mission-critical, advanced |
| **Pricing Model** | On-demand + Autoscaler | On-demand + Autoscaler + Commitments | On-demand + Autoscaler + Commitments |
| **Slot Pricing** (on-demand) | $0.04/slot-hour | $0.06/slot-hour | $0.10/slot-hour |
| **1-year commitment** | N/A | ~20% discount | ~20% discount |
| **3-year commitment** | N/A | ~40% discount | ~40% discount |
| **Monthly SLO** | 99.9% | 99.99% | 99.99% |
| **Max Reservations** | 10 (max 1,600 slots) | 200 (no cap) | 200 (no cap) |
| **Storage** | Same across all editions | Same across all editions | Same across all editions |
| **BI Engine** | No | Yes (up to 250 GB) | Yes (up to 250 GB) |
| **Materialized Views** | Query only | Create + auto-refresh | Create + auto-refresh |
| **CMEK** | No | Yes | Yes |
| **Column-level Security** | No | Yes | Yes |
| **Row-level Security** | No | Yes | Yes |
| **Dynamic Data Masking** | No | Yes | Yes |
| **Multi-region Failover** | No | No | Yes |
| **Time Travel** | 2 days | 7 days (configurable) | 7 days (configurable) |
| **Fail-safe Period** | 0 days | 7 days | 7 days |
| **Streaming (Storage Write API)** | Yes | Yes | Yes |
| **CDC (UPSERT/DELETE)** | Yes | Yes | Yes |
| **BigQuery ML** | No | Yes | Yes |
| **BigQuery Omni** | No | Yes | Yes |
| **Continuous Queries** | No | Yes | Yes |
| **Search Index Acceleration** | No | Yes | Yes |
| **Cross-region Replication** | No | No | Yes |
| **Managed Disaster Recovery** | No | No | Yes |

**On-Demand Pricing** (alternative to editions):
- $6.25 per TB of data processed
- First 1 TiB per month free
- Best for sporadic/ad-hoc workloads
- New projects since September 2025: 200 TiB daily query quota by default

**Recommendation for data platform projects**: Enterprise edition is the sweet spot
for most production workloads. Enterprise Plus is justified only when cross-region
replication or multi-region failover is required.

### 1.3 Storage Options

BigQuery supports four storage paradigms, each with different trade-offs:

#### Native (Managed) Storage

Data is stored directly in BigQuery's Capacitor format on Colossus.

- **Best for**: Frequently queried data, low-latency requirements
- **Performance**: Fastest query performance (optimized columnar format)
- **Cost**: $0.02/GB/month (active), $0.01/GB/month (long-term after 90 days)
- **Features**: Full DML, streaming inserts, CDC, partitioning, clustering, time travel
- **Limitation**: Data is locked into BigQuery format

```sql
-- Create a native BigQuery table
CREATE TABLE `project.dataset.my_table` (
    id STRING NOT NULL,
    name STRING,
    created_at TIMESTAMP,
    amount NUMERIC
)
PARTITION BY DATE(created_at)
CLUSTER BY id;
```

#### External Tables

Query data directly in GCS, Drive, Cloud SQL, or Bigtable without loading it.

- **Best for**: Infrequent queries, data exploration, ELT staging
- **Performance**: Slower (no Capacitor optimization, no caching)
- **Cost**: No storage cost in BQ (pay only for GCS storage + query bytes scanned)
- **Features**: Limited DML, no clustering, no streaming
- **Limitation**: Performance penalty, no BigQuery-managed optimization

```sql
-- Create an external table pointing to Parquet files in GCS
CREATE EXTERNAL TABLE `project.dataset.external_events`
WITH PARTITION COLUMNS
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://bucket/events/*.parquet'],
    hive_partition_uri_prefix = 'gs://bucket/events/'
);
```

#### BigLake Tables

Enhanced external tables with fine-grained access control and metadata caching.

- **Best for**: Governed data lake access, multi-engine scenarios
- **Performance**: Better than raw external (metadata caching, column pruning)
- **Cost**: External storage + BigLake API charges
- **Features**: Column-level security, row-level security, credential vending
- **Limitation**: Still reads from external storage (GCS/S3/ABFS)

```sql
-- Create a BigLake table with a connection
CREATE EXTERNAL TABLE `project.dataset.biglake_events`
WITH CONNECTION `project.region.connection_id`
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://bucket/events/*.parquet'],
    metadata_cache_mode = 'AUTOMATIC'
);
```

#### BigLake Managed (Iceberg) Tables

Apache Iceberg tables managed by BigQuery through BigLake Metastore.

- **Best for**: Open lakehouse pattern, multi-engine access (Spark + BQ)
- **Performance**: Good (Iceberg metadata pruning + Parquet columnar)
- **Cost**: GCS storage + BigLake API charges
- **Features**: ACID transactions, time travel, schema evolution, open format
- **Limitation**: Some BQ features unavailable (e.g., clustering, streaming inserts)
- **Maturity**: GA but still evolving; some operations have quirks

```sql
-- Create a BigLake Managed (Iceberg) table
CREATE TABLE `project.dataset.iceberg_events`
(
    event_id STRING,
    event_name STRING,
    payload JSON,
    ingested_date DATE
)
CLUSTER BY event_id
WITH CONNECTION `project.region.connection_id`
OPTIONS (
    table_format = 'ICEBERG',
    file_format = 'PARQUET',
    storage_uri = 'gs://bucket/iceberg/events/'
);
```

#### Storage Options Comparison

| Aspect | Native | External | BigLake | BigLake Iceberg |
|---|---|---|---|---|
| Format | Capacitor | Parquet/ORC/Avro/CSV/JSON | Parquet/ORC/Avro | Iceberg (Parquet) |
| Location | Colossus | GCS/S3/ABFS | GCS/S3/ABFS | GCS |
| Query Speed | Fastest | Slowest | Medium | Medium-Fast |
| DML Support | Full | Limited | Limited | Full (via BQ SQL) |
| Streaming | Yes (Storage Write API) | No | No | No |
| CDC | Yes | No | No | Limited |
| Partitioning | Yes | Hive-style | Hive-style | Iceberg native |
| Clustering | Yes | No | No | Sort order |
| Column Security | Enterprise+ | No | Yes | Yes |
| Time Travel | 2-7 days | No | No | Yes (Iceberg snapshots) |
| Multi-engine | No | Yes | Yes | Yes |
| Cost (storage) | $0.02/GB | GCS rates | GCS rates | GCS rates |

### 1.4 Partitioning and Clustering

Partitioning and clustering are BigQuery's primary mechanisms for reducing query cost
and improving performance by limiting the amount of data scanned.

#### Partitioning

Partitioning divides a table into segments based on a column value. BigQuery supports:

1. **Time-unit partitioning** (HOUR, DAY, MONTH, YEAR)
2. **Integer-range partitioning** (by integer column with start/end/interval)
3. **Ingestion-time partitioning** (`_PARTITIONTIME` pseudo-column)

```sql
-- DAY partitioning (most common)
CREATE TABLE `project.dataset.events`
(
    event_id STRING,
    event_time TIMESTAMP,
    data STRING
)
PARTITION BY DATE(event_time);

-- HOUR partitioning (for high-volume streaming)
CREATE TABLE `project.dataset.streaming_events`
(
    event_id STRING,
    event_time TIMESTAMP,
    data STRING
)
PARTITION BY TIMESTAMP_TRUNC(event_time, HOUR);

-- Integer-range partitioning
CREATE TABLE `project.dataset.orders`
(
    order_id INT64,
    customer_id INT64,
    amount NUMERIC
)
PARTITION BY RANGE_BUCKET(customer_id, GENERATE_ARRAY(0, 1000000, 1000));
```

**Partition limits and behavior**:
- Maximum 4,000 partitions per partitioned table (was 10,000 in older docs, 4,000 is current)
- Maximum 10,000 partitions modified per DML statement
- Partition pruning occurs when the partition column is used in `WHERE`
- Queries without partition filters scan ALL partitions (can require partition filter)
- `NULL` values go into a special `__NULL__` partition
- Values outside the range go into a `__UNPARTITIONED__` partition

**Best practices**:
- Use `DATE` or `TIMESTAMP` columns that appear frequently in `WHERE` clauses
- Choose partition granularity based on data volume:
  - `DAY`: Most common, good for 1-100 GB/day
  - `HOUR`: High-volume streaming (100+ GB/day)
  - `MONTH`/`YEAR`: Smaller datasets or long-retention analytical queries
- Enable `require_partition_filter` to prevent full-table scans
- Aim for at least 1 GB per partition; avoid too many small partitions
- Use BigQuery's built-in partition recommender for suggestions

#### Clustering

Clustering sorts data within each partition by up to 4 columns, enabling even more
granular pruning.

```sql
-- Clustering on top of partitioning
CREATE TABLE `project.dataset.events`
(
    event_id STRING,
    member_id STRING,
    event_type STRING,
    event_time TIMESTAMP,
    program_code STRING
)
PARTITION BY DATE(event_time)
CLUSTER BY member_id, event_type, program_code;
```

**How clustering works**:
- Data is sorted and organized into blocks by clustering columns (left to right priority)
- BigQuery maintains min/max statistics for each block
- Query predicates on clustering columns enable block pruning
- BigQuery automatically re-clusters in the background (free of charge)

**Clustering limits**:
- Up to 4 clustering columns per table
- Column order matters (first column has strongest pruning effect)
- Works with STRING, INT64, NUMERIC, BIGNUMERIC, DATE, TIMESTAMP, DATETIME, BOOL, GEOGRAPHY
- NOT supported with: BYTES, ARRAY, STRUCT, JSON, FLOAT64
- Benefits tables/partitions larger than 64 MB

**Best practices**:
- Place the most frequently filtered column first
- High-cardinality columns benefit more from clustering
- Combine with partitioning: partition by date, cluster by ID/type
- Clustering is especially effective for tables > 1 GB
- Re-clustering is automatic and free -- no maintenance needed
- Combined partitioning + clustering can reduce scanned data by 10-100x

#### Partitioning vs Clustering Decision Matrix

| Scenario | Recommendation |
|---|---|
| Filter by date/time range | Partition by time column |
| Filter by high-cardinality column (e.g., user_id) | Cluster by that column |
| Filter by both time and category | Partition by time, cluster by category |
| Table < 1 GB | Neither (overhead exceeds benefit) |
| Need strict cost control per query | Partition (provides hard boundaries) |
| Need to filter by multiple columns | Partition by time + cluster by up to 4 columns |
| Streaming data with CDC | Partition by ingestion time or event time |

### 1.5 CDC via Storage Write API

BigQuery's Change Data Capture (CDC) capability enables real-time UPSERT and DELETE
operations through the Storage Write API. This is critical for maintaining synchronized
replicas of operational databases.

#### How CDC Works

```
+------------+     Storage Write API      +-----------------+
|  Source     |  -----------------------> |  BigQuery Table  |
|  (Kafka/   |   UPSERT/DELETE rows       |  (CDC-enabled)   |
|   DB/API)  |   with _CHANGE_TYPE        |                  |
+------------+                            +-----------------+
                                                |
                                          Automatic merge
                                          into base table
```

**Requirements for CDC tables**:
1. Table must have a **primary key** (`NOT ENFORCED`)
2. Writes must use the **Storage Write API** (default committed stream)
3. Each row must include a `_CHANGE_TYPE` column with value `UPSERT` or `DELETE`
4. Must use protobuf format

```sql
-- Create a CDC-enabled table
CREATE TABLE `project.dataset.member_tier` (
    member_id STRING NOT NULL,
    tier_code STRING,
    program_code STRING,
    start_date DATE,
    end_date DATE,
    ingested_date DATE,
    PRIMARY KEY (member_id) NOT ENFORCED
)
PARTITION BY ingested_date
CLUSTER BY member_id;
```

#### UPSERT Behavior

- If a row with the same primary key exists, it is **replaced** (full row replacement)
- If no matching row exists, the row is **inserted**
- Multiple UPSERTs for the same key in a single write batch: last one wins
- The `_CHANGE_TYPE` column value must be `"UPSERT"`

#### DELETE Behavior

- If a row with the matching primary key exists, it is **deleted**
- If no matching row exists, the DELETE is a no-op (no error)
- The `_CHANGE_TYPE` column value must be `"DELETE"`
- Only the primary key columns need to be populated (other columns can be NULL)

#### Exactly-Once Semantics

The Storage Write API supports exactly-once delivery:
- **Committed mode** (default stream): At-least-once delivery, free
- **Buffered mode**: Exactly-once with explicit flush, $0.025/GB (first 2 TB/month free)
- For CDC with Dataflow, committed mode is typically sufficient because the CDC
  merge process handles deduplication via primary key

#### Mutation Type in Apache Beam

When using Apache Beam's BigQuery IO with the Storage Write API:

```python
from apache_beam.io.gcp.bigquery import StorageWriteSink

# In row mapper, set _CHANGE_TYPE
def to_bq_row(element):
    mutation_type = "DELETE" if element.get("_is_delete") else "UPSERT"
    row = {
        "member_id": element["memberId"],
        "tier_code": element.get("tierCode"),
        "program_code": element.get("programCode"),
        "_CHANGE_TYPE": mutation_type,
    }
    return row
```

#### CDC Best Practices

1. **Primary key selection**: Choose columns that uniquely identify a row in the source
2. **Avoid composite keys** if possible -- single-column keys perform better
3. **Batch writes**: Group multiple changes before writing to reduce API calls
4. **Ordering**: Within a batch, ensure correct ordering for same-key operations
5. **max_staleness**: For read-heavy workloads, set `max_staleness` to allow reading
   from the change buffer without immediate merge (reduces read cost)

```sql
-- Set max_staleness to allow reading slightly stale data (reduces merge frequency)
ALTER TABLE `project.dataset.member_tier`
SET OPTIONS (max_staleness = INTERVAL 15 MINUTE);
```

6. **Monitor merge lag**: CDC tables have a background merge process. Under heavy write
   load, the merge can fall behind. Monitor via `INFORMATION_SCHEMA.TABLE_STORAGE`.

#### CDC Limitations

- Primary keys are `NOT ENFORCED` -- BigQuery does not validate uniqueness
- No support for partial updates (must send full row for UPSERT)
- DELETE requires knowing the primary key value
- CDC is not supported on external or BigLake Iceberg tables (native only)
- `max_staleness` affects read consistency -- stale reads are possible
- Merge frequency is not configurable (managed by BigQuery)
- Maximum 4 primary key columns

#### Legacy Streaming Inserts (tabledata.insertAll)

- $0.010 per 200 MB ($0.05/GB)
- At-least-once delivery (possible duplicates)
- No CDC support
- Google recommends migrating to Storage Write API
- Max 50,000 rows per request

### 1.6 Materialized Views, BI Engine, and BQML

#### Materialized Views

Materialized views precompute and cache query results, automatically maintained by
BigQuery as base tables change.

```sql
-- Create a materialized view
CREATE MATERIALIZED VIEW `project.dataset.daily_member_counts`
AS
SELECT
    DATE(event_time) AS event_date,
    program_code,
    COUNT(DISTINCT member_id) AS unique_members,
    COUNT(*) AS total_events
FROM `project.dataset.events`
GROUP BY event_date, program_code;
```

**Key features**:
- Automatic refresh when base tables change (configurable interval)
- Smart rewriting: queries against base tables automatically use materialized views
- Incremental maintenance for supported aggregations
- Zero maintenance cost -- refresh is free (you only pay for storage)
- Supports: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `COUNT DISTINCT` (approximate), `HLL_COUNT`
- Supported over BigLake metadata-cached tables

**Limitations**:
- Requires Enterprise edition to create (Standard can query but not create)
- No JOINs in Standard edition (Enterprise+ required)
- Limited to aggregations (no window functions, subqueries, UDFs)
- Cannot reference other materialized views
- Maximum 20 materialized views per base table

#### BI Engine

BI Engine is an in-memory analysis service that accelerates BigQuery queries by caching
data in RAM.

- **Capacity**: Reserve 1 GB to 250 GB of RAM per project
- **Acceleration**: Sub-second query responses for cached data
- **Integration**: Works transparently with Looker, Looker Studio, Connected Sheets,
  and third-party BI tools
- **Pricing**: $0.0416/GB/hour of reserved capacity
- **Use case**: Interactive dashboards with sub-second response times
- **Cost reduction**: Can reduce dashboard query costs by up to 80%
- **No code changes needed**: Transparent acceleration

#### BigQuery ML (BQML)

Train and deploy machine learning models directly in BigQuery using SQL.

```sql
-- Train a classification model
CREATE OR REPLACE MODEL `project.dataset.churn_model`
OPTIONS (
    model_type = 'LOGISTIC_REG',
    input_label_cols = ['churned'],
    max_iterations = 20
) AS
SELECT
    member_id,
    total_purchases,
    days_since_last_purchase,
    tier_code,
    churned
FROM `project.dataset.member_features`;

-- Make predictions
SELECT *
FROM ML.PREDICT(
    MODEL `project.dataset.churn_model`,
    (SELECT * FROM `project.dataset.new_members`)
);
```

**Supported models by category**:

| Category | Models |
|---|---|
| Regression | Linear, Boosted Trees, AutoML DNN, Wide & Deep |
| Classification | Logistic, Boosted Trees, AutoML Tables |
| Clustering | K-Means |
| Time Series | ARIMA, ARIMA+ |
| Recommendation | Matrix Factorization |
| Deep Learning | DNN, TensorFlow imported |
| NLP/GenAI | Vertex AI models, Gemma |

Requires Enterprise edition or higher.

### 1.7 Pricing Model

BigQuery pricing has two main dimensions: **compute** (query processing) and
**storage** (data at rest).

#### Compute Pricing

**On-Demand Pricing** (pay-per-query):
- $6.25 per TB of data scanned (first 1 TB/month free)
- No upfront commitment
- Maximum 2,000 concurrent slots per project (can request increase)
- Good for: sporadic or unpredictable query patterns
- New projects since September 2025: 200 TiB daily query quota by default

**Capacity Pricing** (slot-based):

| Commitment | Standard | Enterprise | Enterprise Plus |
|---|---|---|---|
| Autoscaler (per slot-hour) | $0.04 | $0.06 | $0.10 |
| 1-year | N/A | ~$0.048 | ~$0.080 |
| 3-year | N/A | ~$0.036 | ~$0.060 |

- Buy "slots" (units of compute capacity)
- Predictable costs, suitable for steady workloads
- Autoscaler can add slots dynamically up to a configurable cap
- Baseline slots are always available; autoscaler slots are best-effort

**Recommendation**: For projects with consistent daily pipelines (like loyalty data),
capacity pricing with a baseline reservation + autoscaler cap provides cost
predictability while handling burst workloads.

#### Storage Pricing

| Storage Type | Active (< 90 days) | Long-term (>= 90 days) |
|---|---|---|
| Logical (uncompressed) | $0.02/GB/month | $0.01/GB/month |
| Physical (compressed) | $0.04/GB/month | $0.02/GB/month |

- **Logical pricing** (default): Based on uncompressed data size
- **Physical pricing** (opt-in per dataset): Based on actual compressed bytes
  (typically 3-5x smaller than logical, but includes time travel and fail-safe bytes)
- Long-term pricing kicks in automatically after 90 days of no modifications to a
  partition (not the table, but individual partitions)

#### Streaming Pricing

- **Storage Write API (committed)**: Free
- **Storage Write API (buffered)**: $0.025/GB (first 2 TB/month free)
- **Legacy streaming inserts** (`insertAll`): $0.010 per 200 MB (deprecated, avoid)

### 1.8 Key Quotas and Limitations

| Quota / Limit | Value | Notes |
|---|---|---|
| Max columns per table | 10,000 | Includes nested fields |
| Max row size | 100 MB | Serialized row size |
| Concurrent DML per table | 20 PENDING | DML statements |
| DML (UPDATE/DELETE/MERGE) | Unlimited | Previously 20/day, now unlimited |
| Max concurrent queries (on-demand) | 100 | Per project, can request increase |
| Max query size | 12 MB | Unresolved query text |
| Max result size | 10 GB (compressed) | For destination table queries |
| Max tables per dataset | Unlimited | No hard limit |
| Max datasets per project | Unlimited | No hard limit |
| Max partitions per table | 4,000 | For partitioned tables |
| Max partitions modified per DML | 10,000 | Per DML statement |
| Max clustering columns | 4 | Per table |
| Max primary key columns | 4 | For CDC tables |
| Nested record levels | 15 | Maximum nesting depth |
| Time travel window | 2-7 days | Depends on edition |
| Max Storage Write API throughput | 3 GB/s | Per project, per region |
| Max Storage Write API connections | 10,000 | Per project |
| Storage Write API free tier | 2 TB/month | Committed mode |
| Query timeout | 6 hours | Maximum query execution time |
| Max scheduled queries | 20,000 | Per project |
| Max views referenced in query | 500 | Nested view depth |
| Max UDF per query | 50 | User-defined functions |
| Max export size | 1 GB per file | Use wildcard for larger exports |
| Max LOAD jobs per table per day | 1,500 | Load jobs |
| Max LOAD jobs per project per day | 100,000 | Project-wide limit |
| Max LOAD job size | 15 TB | Per load job |
| Max row per request (legacy) | 50,000 | Legacy streaming inserts |
| On-demand daily quota | 200 TiB | New projects, Sep 2025+ |

---

## 2. BigLake Lakehouse

### 2.1 BigLake Architecture and Capabilities

BigLake is Google Cloud's unified storage engine that extends BigQuery's governance
and performance capabilities to data stored in open formats on GCS, Amazon S3, and
Azure Blob Storage.

```
                  +---------------------------+
                  |      BigQuery Engine       |
                  |   (SQL, ML, BI Engine)     |
                  +-----------+---------------+
                              |
                  +-----------v---------------+
                  |        BigLake API         |
                  |  +-----------------------+ |
                  |  | Credential Vending    | |
                  |  | Metadata Caching      | |
                  |  | Column/Row Security   | |
                  |  | Performance Accel.    | |
                  |  +-----------------------+ |
                  +-----------+---------------+
                              |
          +-------------------+-------------------+
          |                   |                   |
    +-----v----+       +-----v----+       +------v-----+
    |   GCS    |       |    S3    |       | Azure Blob |
    | (Parquet |       | (Parquet |       | (Parquet   |
    |  Iceberg |       |  Delta)  |       |  Iceberg)  |
    |  ORC)    |       |          |       |            |
    +----------+       +----------+       +------------+
```

**Core capabilities**:

1. **Unified governance**: Apply BigQuery column-level and row-level security
   policies to data in any storage location
2. **Performance acceleration**: Metadata caching, column pruning, and predicate
   pushdown for external data
3. **Multi-format support**: Parquet, ORC, Avro, CSV, JSON, Iceberg, Delta Lake
4. **Multi-cloud access**: Query data across GCS, S3, and Azure Blob without copying
5. **Open format preservation**: Data remains in open formats, no lock-in
6. **Automatic data tiering**: Cost optimization across storage classes

### 2.2 BigLake Metastore (BLMS) -- Iceberg REST Catalog

BigLake Metastore is a serverless, GCP-native metastore that implements the
**Apache Iceberg REST Catalog** specification. It replaces the need for a separate
Hive Metastore or custom catalog service.

#### Key Features

- **REST Catalog API**: Fully compatible with Apache Iceberg REST Catalog spec (GA)
- **Serverless**: No infrastructure to manage
- **Credential Vending**: Provides short-lived credentials to compute engines
- **Multi-engine**: Works with BigQuery, Dataflow, Spark, Flink, Trino
- **ACID Transactions**: Through Iceberg's optimistic concurrency
- **Namespace Management**: Hierarchical organization (catalog.namespace.table)
- **Iceberg 1.9+ compatible**: Works with modern Iceberg clients

#### BLMS Hierarchy

```
BigLake Catalog (per project + region)
  +-- Namespace (= BigQuery dataset)
       +-- Table (= Iceberg table on GCS)
            |-- metadata/
            |   |-- v1.metadata.json
            |   |-- v2.metadata.json
            |   +-- snap-*.avro (manifests)
            +-- data/
                |-- part-00000.parquet
                |-- part-00001.parquet
                +-- ...
```

#### BLMS REST API Operations

| Category | Operations |
|---|---|
| Table | create, list, load, update, drop |
| Namespace | create, list, drop |
| Config | resolve prefix, overrides |

#### Using BLMS with Apache Beam (Dataflow)

This is the primary write path used in the loyalty data platform:

```python
from apache_beam.io.managed import Write

# BLMS REST Catalog configuration
catalog_config = {
    "type": "rest",
    "uri": "https://biglake.googleapis.com/iceberg/v1beta",
    "warehouse": f"projects/{project}/locations/{region}/catalogs/{catalog}",
    "credential": "GCPCredential",
    "oauth2-server-uri": "https://oauth2.googleapis.com/token",
    "rest.sigv4-enabled": "true",
    "rest.access-delegation": "vended-credentials",
}

# Write to Iceberg via BLMS
result = (
    pipeline
    | "WriteToIceberg" >> Write(
        Write.to("iceberg")
        .withCatalogConfig(catalog_config)
        .toTable(f"{namespace}.{table_name}")
        .withTableProperties({
            "location": f"gs://{bucket}/{prefix}/{table_name}",
            "format-version": "2",
            "write.parquet.compression-codec": "snappy",
        })
    )
)
```

#### BLMS API Operations via curl

```bash
# List catalogs
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://biglake.googleapis.com/v1/projects/{project}/locations/{region}/catalogs"

# List namespaces in a catalog
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://biglake.googleapis.com/v1/projects/{project}/locations/{region}/catalogs/{catalog}/databases"

# List tables in a namespace
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://biglake.googleapis.com/v1/projects/{project}/locations/{region}/catalogs/{catalog}/databases/{namespace}/tables"
```

#### BLMS Terraform Configuration

BigLake catalogs and related IAM can be provisioned via Terraform:

```hcl
# Create a BigLake catalog
resource "google_biglake_catalog" "main" {
  name     = "loyalty_catalog"
  location = "asia-southeast1"
  project  = var.project_id
}

# Grant service account access to the catalog
resource "google_biglake_catalog_iam_member" "sa_access" {
  catalog  = google_biglake_catalog.main.name
  location = google_biglake_catalog.main.location
  project  = var.project_id
  role     = "roles/biglake.admin"
  member   = "serviceAccount:${var.service_account_email}"
}
```

### 2.3 Credential Vending and Access Delegation

Credential vending is a security mechanism where BLMS provides short-lived,
scoped credentials to compute engines for accessing data files on GCS/S3.

```
+----------+   1. Request table    +-------+
| Dataflow | ------------------->  | BLMS  |
| (Beam)   |                       |       |
|          | <-------------------  |       |
|          |  2. Table metadata    |       |
|          |     + vended creds    |       |
|          |                       +-------+
|          |
|          |  3. Read/Write data
|          |     using vended creds
|          | ------------------->  +-------+
|          |                       |  GCS  |
+----------+                       +-------+
```

**How it works**:
1. Compute engine (e.g., Dataflow) authenticates to BLMS with its service account
2. BLMS validates permissions and returns table metadata + short-lived GCS credentials
3. Compute engine uses the vended credentials to read/write data files directly
4. Credentials are scoped to specific GCS paths (least privilege)

**Configuration** (in catalog config):
```python
{
    "rest.access-delegation": "vended-credentials",
    "credential": "GCPCredential",
}
```

**Benefits**:
- No need to grant broad GCS access to compute service accounts
- Credentials are scoped and time-limited (typically 1 hour)
- Centralized access control through BLMS/BigLake policies
- Audit trail for all data access

**IAM requirements for credential vending**:
- The BLMS connection's service account needs `roles/storage.objectAdmin` on the GCS bucket
- The Dataflow service account needs `roles/biglake.viewer` on the catalog
- The connection must be configured with `rest.access-delegation: vended-credentials`

### 2.4 Multi-Cloud Support (BigQuery Omni)

BigLake enables querying data across cloud providers without copying:

**Cross-cloud query via BigQuery Omni**:
- Query S3 data from BigQuery using a connection to AWS
- Query Azure Blob data from BigQuery using a connection to Azure
- Data stays in its original location
- Compute runs in the cloud where the data resides
- Cross-cloud joins supported

**Supported regions for BigQuery Omni**:
- AWS: us-east-1, eu-west-1, and more
- Azure: eastus2, and more

**Requirements**: Enterprise edition or higher

```sql
-- Create an external table over S3 data
CREATE EXTERNAL TABLE `project.dataset.s3_events`
WITH CONNECTION `project.aws-region.aws_connection`
OPTIONS (
    format = 'PARQUET',
    uris = ['s3://bucket/events/*.parquet']
);

-- Query S3 data from BigQuery
SELECT event_type, COUNT(*)
FROM `project.dataset.s3_events`
WHERE event_date = '2026-01-15'
GROUP BY event_type;
```

### 2.5 Open Table Format Support

BigLake supports multiple open table formats with varying levels of maturity:

| Feature | Apache Iceberg | Delta Lake | Apache Hudi |
|---|---|---|---|
| Support Level | GA (native) | GA (since 2025) | Limited (read-only) |
| Write from BQ | Yes (DML) | Yes (DML) | No |
| Read from BQ | Yes | Yes | Yes |
| BLMS Integration | Yes (REST Catalog) | Unity Catalog bridge | No |
| Dataflow Write | Yes (managed.Write) | No | No |
| Spark Integration | Full | Full | Full |
| Time Travel | Yes | Yes | Yes |
| Schema Evolution | Full | Full | Full |
| Partition Evolution | Yes (Iceberg v2) | No | No |
| ACID Guarantees | Full | Full | Full |
| REST Catalog | Standard (Iceberg REST spec) | Unity Catalog | No standard |
| Interoperability | Best (multi-engine) | Good (UniForm) | Limited |
| Community Momentum | Highest (2024-2026, de facto standard) | Strong (Databricks) | Declining |

**GCP's strategic direction**: Iceberg is the preferred open table format on GCP.
BigLake Metastore is built around the Iceberg REST Catalog spec, and most GCP services
(Dataflow, Dataproc, BigQuery) have first-class Iceberg support.

---

## 3. Data Lake on GCP

### 3.1 GCS as Foundation

Google Cloud Storage (GCS) serves as the foundational storage layer for data lakes
on GCP. It provides durable, highly available object storage with multiple storage
classes for cost optimization.

#### Storage Classes

| Storage Class | Min Duration | Access Frequency | Price (US multi-region) | Use Case |
|---|---|---|---|---|
| Standard | None | Frequent | $0.020-0.026/GB/month | Active data, hot tier |
| Nearline | 30 days | Monthly | $0.010-0.020/GB/month | Backups, accessed monthly |
| Coldline | 90 days | Quarterly | $0.004-0.014/GB/month | Disaster recovery, rare access |
| Archive | 365 days | Annual | $0.0022-0.005/GB/month | Regulatory compliance, archives |

**Important**: All storage classes have the same first-byte latency (typically
milliseconds). The difference is purely in storage cost vs. retrieval/operation cost.
Prices vary by region -- always verify at official pricing pages.

#### Retrieval and Operation Costs

| Operation | Standard | Nearline | Coldline | Archive |
|---|---|---|---|---|
| Class A (create, list) per 10K ops | $0.05 | $0.10 | $0.10 | $0.50 |
| Class B (read, get) per 10K ops | $0.004 | $0.01 | $0.05 | $0.50 |
| Retrieval per GB | Free | $0.01 | $0.02 | $0.05 |

#### Key Features

- Strong consistency (read-after-write)
- Object lifecycle management
- Autoclass (automatic storage class optimization)
- CMEK/CSEK encryption
- VPC Service Controls

#### GCS for Data Lakes -- Best Practices

1. **Bucket layout**: Use a hierarchical path structure:
   ```
   gs://project-data-lake/
   |-- source/           # Raw data from ingestion
   |   |-- member_info/
   |   |   |-- data/     # Parquet files
   |   |   +-- metadata/ # Iceberg metadata
   |   +-- tier_events/
   |-- refined/          # Transformed data (optional on GCS)
   +-- archive/          # Historical snapshots
   ```

2. **Lifecycle rules**: Automatically transition or delete objects:
   ```json
   {
     "lifecycle": {
       "rule": [
         {
           "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
           "condition": {"age": 90, "matchesPrefix": ["source/"]}
         },
         {
           "action": {"type": "Delete"},
           "condition": {"age": 365, "matchesPrefix": ["source/temp/"]}
         }
       ]
     }
   }
   ```

3. **Versioning**: Enable for critical data to protect against accidental deletion
4. **Uniform bucket-level access**: Use IAM instead of ACLs for simpler security
5. **Regional vs multi-region**: Use regional for lower cost and data locality;
   multi-region for high availability
6. **Naming conventions**: Use lowercase, hyphens, no periods (for SSL compatibility)

#### GCS Terraform Example

```hcl
resource "google_storage_bucket" "data_lake" {
  name          = "loyalty-source-data"
  location      = "ASIA-SOUTHEAST1"
  storage_class = "STANDARD"

  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }
}
```

### 3.2 Apache Iceberg on GCP

Apache Iceberg is an open table format designed for huge analytic datasets. On GCP,
Iceberg tables are stored as Parquet files on GCS with metadata managed by BLMS.

#### Core Iceberg Concepts

```
+---------------------------------------------+
|              Iceberg Table                   |
|                                             |
|  Catalog (BLMS)                             |
|    +-- Current metadata pointer             |
|         +-- v3.metadata.json                |
|              |-- Schema (columns, types)    |
|              |-- Partition Spec             |
|              |-- Sort Order                 |
|              |-- Snapshot s3                |
|              |    +-- Manifest List         |
|              |         |-- Manifest 1       |
|              |         |    |-- file1.parq  |
|              |         |    +-- file2.parq  |
|              |         +-- Manifest 2       |
|              |              +-- file3.parq  |
|              +-- Snapshot s2 (previous)     |
|                   +-- ...                   |
+---------------------------------------------+
```

**Metadata hierarchy explained**:

1. **Catalog** (BLMS): Stores the pointer to the current metadata file for each table
2. **Metadata file** (v{n}.metadata.json): Contains schema, partition spec, sort order,
   and references to snapshots
3. **Snapshot**: A complete point-in-time view of the table. Each snapshot references
   a manifest list
4. **Manifest List** (snap-{id}.avro): Lists all manifest files for this snapshot,
   with partition-level statistics for pruning
5. **Manifest** (manifest-{id}.avro): Lists data files with per-file statistics
   (row count, min/max per column, null count)
6. **Data Files** (*.parquet): The actual data in Parquet columnar format

**Key Iceberg features on GCP**:

1. **ACID Transactions**: Optimistic concurrency via atomic metadata swap
   - Writers create new metadata + data files, then atomically update the catalog pointer
   - Conflicts detected by metadata version comparison; retry on conflict

2. **Time Travel**: Query data as of a specific snapshot or timestamp
   ```sql
   -- BigQuery time travel (for BigLake Iceberg tables)
   SELECT * FROM `project.dataset.events`
   FOR SYSTEM_TIME AS OF TIMESTAMP '2026-01-15 10:00:00 UTC';
   ```

3. **Schema Evolution**: Add, drop, rename, or reorder columns without rewriting data
   - Column identity tracked by field IDs (not names)
   - Rename is metadata-only (zero cost)
   - Type promotion supported (e.g., INT to LONG, FLOAT to DOUBLE)

4. **Partition Evolution**: Change partition strategy without rewriting existing data
   - Old data keeps old partition layout
   - New data uses new partition layout
   - Query engine handles both transparently

5. **Hidden Partitioning**: Partition transforms applied at write time, not exposed in schema
   - `days(timestamp)`, `hours(timestamp)`, `months(timestamp)`, `years(timestamp)`
   - `bucket(N, column)`, `truncate(L, column)`
   - Users query naturally (`WHERE timestamp > '2026-01-01'`), engine handles pruning

6. **Row-level Deletes** (v2): Equality and position delete files for efficient updates

#### Iceberg Format Versions

| Feature | v1 | v2 |
|---|---|---|
| Schema evolution | Yes | Yes |
| Partition evolution | No | Yes |
| Row-level deletes | No | Yes (equality + position deletes) |
| Sort order | No | Yes |
| Default delete mode | Copy-on-write | Merge-on-read |
| Recommended for new tables | No | Yes |

**The loyalty data platform uses Iceberg v2** (`"format-version": "2"` in table properties).

### 3.3 Iceberg vs Delta Lake vs Hudi

| Feature | Apache Iceberg | Delta Lake | Apache Hudi |
|---|---|---|---|
| **Creator** | Netflix (2018, ASF 2020) | Databricks (2019, Linux Foundation 2024) | Uber (2019, ASF 2020) |
| **File Format** | Parquet (default), ORC, Avro | Parquet only | Parquet (default), ORC |
| **Metadata** | JSON + Avro manifests | JSON transaction log (_delta_log/) | Timeline + metadata files |
| **Schema Evolution** | Full (field ID-based) | Add/rename (column name-based) | Full |
| **Partition Evolution** | Yes (unique feature) | Limited | Limited |
| **Hidden Partitioning** | Yes | No (user-managed) | No |
| **Time Travel** | Yes (snapshot-based) | Yes (version-based) | Yes (timeline-based) |
| **Merge-on-Read** | Iceberg v2 (equality/position deletes) | Deletion vectors (v2.4+) | Native (CoW + MoR) |
| **Copy-on-Write** | Yes | Yes | Yes |
| **Concurrency** | Optimistic (metadata swap) | Optimistic (log commit) | Optimistic (timeline) |
| **Row-level Ops** | Equality/Position deletes | Deletion vectors | Built-in (primary key) |
| **CDC Strength** | Good | Good | Excellent |
| **Catalog Support** | REST, Hive, AWS Glue, BLMS, Nessie | Unity, Hive, AWS Glue | Hive |
| **GCP Integration** | Best (BLMS, BQ, Dataflow native) | Good (BQ support GA since 2025) | Limited (read-only) |
| **Spark Support** | Full | Full | Full |
| **Flink Support** | Full | Limited | Full |
| **Trino/Presto** | Full | Full | Full |
| **Community** | Rapidly growing, multi-vendor | Large (Databricks ecosystem) | Declining |
| **Governance** | Apache Software Foundation | Linux Foundation | Apache Software Foundation |
| **Industry Momentum** | Highest (de facto standard) | Strong (Databricks) | Declining |

**When to choose Iceberg on GCP**:
- You are building on GCP and want native BLMS + BigQuery integration
- You need partition evolution (change partitioning without rewrite)
- You want multi-engine access (Beam, Spark, Flink, BigQuery, Trino)
- You need hidden partitioning (simpler queries, automatic pruning)

**When Delta Lake might be better**:
- You are heavily invested in Databricks or Spark
- You need mature streaming support (Structured Streaming)
- You want Unity Catalog for governance

**When Hudi might be better**:
- You need record-level indexing and fast upserts
- You have real-time CDC pipeline patterns
- You are on AWS (better Hudi support than GCP)

### 3.4 Data Lifecycle Management

Effective data lifecycle management on GCP involves coordinating GCS lifecycle rules,
Iceberg table maintenance, and BigQuery partition expiration.

#### Iceberg Table Maintenance

```python
# Example: Iceberg maintenance tasks (via PyIceberg or Spark)

# 1. Expire old snapshots (free up storage)
table.expire_snapshots().expire_older_than(
    datetime.now() - timedelta(days=7)
).commit()

# 2. Remove orphan files (cleanup failed writes)
table.remove_orphan_files(
    older_than=datetime.now() - timedelta(days=3)
)

# 3. Rewrite data files (compaction)
table.rewrite_data_files(
    target_file_size_bytes=256 * 1024 * 1024,  # 256 MB
    min_input_files=5
)

# 4. Rewrite manifests (optimize metadata)
table.rewrite_manifests()
```

**Why table maintenance matters**:
- **Snapshot expiry**: Without it, metadata grows unbounded, slowing queries
- **Orphan file cleanup**: Failed writes leave data files not referenced by any snapshot
- **Compaction**: Many small files degrade read performance (the "small files problem")
- **Manifest rewriting**: Reduces manifest scan time for query planning

**Maintenance scheduling**:
- Snapshot expiry: Daily (retain 7 days)
- Orphan file cleanup: Weekly
- Compaction: Daily or when average file size < 64 MB
- Manifest rewriting: Monthly or when manifest count > 100

#### BigQuery Partition Expiration

```sql
-- Set partition expiration on a BigQuery table
ALTER TABLE `project.dataset.events`
SET OPTIONS (
    partition_expiration_days = 365
);
```

#### Lifecycle Strategy by Data Tier

| Tier | Retention | Storage Class | Maintenance |
|---|---|---|---|
| Source (Iceberg) | 90 days snapshots, 365 days data | Standard then Nearline | Weekly compaction, daily snapshot expiry |
| Refined (BigQuery) | 365 days partitions | Native (auto long-term) | Partition expiration, backup rotation |
| Semantic (BQ views) | N/A (views are definitions) | N/A | Schema version management |
| Archive | 7 years | Coldline then Archive | Lifecycle rules for deletion |

---

## 4. Lakehouse Architecture Pattern on GCP

### 4.1 Overview

The loyalty/messaging/sales data platform implements a modern lakehouse architecture
that combines the flexibility of a data lake (open formats, multi-engine access) with
the performance and governance of a data warehouse (BigQuery).

```
+---------------------------------------------------------------------+
|                     Lakehouse Architecture                          |
|                                                                     |
|  +----------------+   +------------------+   +------------------+  |
|  |  Source Layer   |   |  Refined Layer   |   |  Semantic Layer  |  |
|  |  (Iceberg/GCS) |-->|  (BigQuery)      |-->|  (BQ Views)      |  |
|  |                |   |                  |   |                  |  |
|  |  Open format   |   |  Optimized       |   |  Business logic  |  |
|  |  Multi-engine  |   |  Governed        |   |  Public API      |  |
|  |  ACID writes   |   |  CDC-enabled     |   |  Dataform-managed|  |
|  +----------------+   +------------------+   +------------------+  |
|                                                                     |
|  Write: Dataflow -> managed.Write -> BLMS REST -> GCS (Iceberg)    |
|  Read:  BigQuery <- BigLake external table <- GCS (Iceberg)        |
|  Refine: Dataflow -> Storage Write API -> BigQuery (native)        |
|  Serve:  BI tools <- BigQuery views (Dataform) <- refined tables   |
+---------------------------------------------------------------------+
```

### 4.2 Three-Layer Mapping

| Layer | Technology | Write Method | Partition | Format |
|---|---|---|---|---|
| Source | Iceberg on GCS | IcebergIO (managed.Write) via BLMS REST | Varies | Parquet |
| Refined | BigQuery native | Storage Write API (CDC or APPEND) | ingestedTHDate (DATE) or etlLoadTime (HOUR) | Capacitor |
| Public | BigQuery views | Dataform CREATE OR REPLACE VIEW | N/A | N/A |

### 4.3 Source Layer: Iceberg on GCS via BLMS

The source layer captures raw or lightly transformed data from upstream systems
(Kafka, APIs, batch files) and stores it in Apache Iceberg format on GCS.

**Characteristics**:
- **Format**: Apache Iceberg v2 (Parquet data files)
- **Catalog**: BigLake Metastore (BLMS REST Catalog)
- **Writer**: Apache Beam `managed.Write` via Dataflow
- **Partitioning**: By date (e.g., `ingestedTHDate` for members, `etlLoadTime` for events)
- **Schema**: Matches upstream source with minimal transformation
- **Purpose**: Durable, replayable, open-format landing zone

**Write path**:
```
Kafka/API -> Dataflow (Beam) -> managed.Write -> BLMS REST Catalog -> GCS (Parquet)
```

**Why Iceberg for source layer**:
1. ACID writes prevent partial/corrupt data
2. Schema evolution handles upstream changes without pipeline restart
3. Time travel enables debugging and reprocessing
4. Open format allows multi-engine access (Spark for ad-hoc, BQ for analytics)
5. Partition evolution future-proofs against changing access patterns

**Example table structure on GCS**:
```
gs://loyalty-source-bucket/
  +-- member_info/
       |-- metadata/
       |   |-- v1.metadata.json
       |   |-- v2.metadata.json
       |   +-- snap-12345.avro
       +-- data/
           |-- ingestedTHDate=20260301/
           |   |-- 00000-0-abc.parquet
           |   +-- 00001-0-def.parquet
           +-- ingestedTHDate=20260302/
               +-- 00000-0-ghi.parquet
```

### 4.4 Refined Layer: BigQuery Native Tables

The refined layer contains cleansed, transformed, and business-ready data in BigQuery
native format.

**Characteristics**:
- **Format**: BigQuery native (Capacitor)
- **Writer**: Dataflow via Storage Write API (with CDC for UPSERT/DELETE)
- **Partitioning**: By date (DAY partition on `ingestedTHDate` or `etlLoadTime`)
- **CDC**: Primary key-based UPSERT/DELETE for dimensional tables (e.g., `member_tier`)
- **Purpose**: Optimized for analytical queries, dashboards, and ML

**Write path** (from Dataflow):
```
Dataflow (Beam) -> BigQuery Storage Write API -> BigQuery native table
```

**Transformations applied**:
- Field extraction and type casting
- Business logic application (e.g., tier matching, date conversion)
- Deduplication (via Beam `Distinct()` or CDC primary keys)
- CDC DELETE for stale records (e.g., removed tier memberships)

**Example refined tables**:
```sql
-- member_tier: CDC-enabled with UPSERT/DELETE
CREATE TABLE `loyalty_refined.member_tier` (
    member_id STRING NOT NULL,
    tier_code STRING,
    program_code STRING,
    start_date DATE,
    end_date DATE,
    ingested_date DATE,
    PRIMARY KEY (member_id) NOT ENFORCED
)
PARTITION BY ingested_date
CLUSTER BY member_id;

-- member_tier_maintenance: CDC-enabled with UPSERT
CREATE TABLE `loyalty_refined.member_tier_maintenance` (
    tierMaintenanceId STRING NOT NULL,
    member_id STRING,
    tier_code STRING,
    maintenance_date DATE,
    ingested_date DATE,
    PRIMARY KEY (tierMaintenanceId) NOT ENFORCED
)
PARTITION BY ingested_date;
```

### 4.5 Semantic/Public Layer: Dataform Views

The semantic layer (also called the "public" layer) exposes curated views managed
by Dataform (GCP's dbt alternative).

**Characteristics**:
- **Format**: BigQuery views (no data duplication)
- **Manager**: Dataform (SQL-based transformations with dependency management)
- **Purpose**: Business-facing API for BI tools, reports, and downstream consumers
- **Security**: Column-level and row-level security applied at view level

**Example Dataform view**:
```sql
-- definitions/loyalty/member_summary.sqlx
config {
    type: "view",
    schema: "loyalty_public",
    description: "Member summary view for BI consumption"
}

SELECT
    mt.member_id,
    mt.tier_code,
    mt.program_code,
    mt.start_date AS tier_start_date,
    COUNT(te.event_id) AS tier_change_count,
    MAX(te.event_time) AS last_tier_change
FROM ${ref("loyalty_refined", "member_tier")} mt
LEFT JOIN ${ref("loyalty_refined", "tier_events")} te
    ON mt.member_id = te.member_id
GROUP BY 1, 2, 3, 4
```

### 4.6 How This Maps to Loyalty/Messaging/Sales Projects

```
+---------------------------------------------------------------------+
|                    Data Platform Projects                            |
|                                                                     |
|  LOYALTY (our scope: 2.1.1)                                        |
|  +---------------------+  +-----------------+                      |
|  | members-collector   |  | tiers-collector  |                     |
|  | (Kafka streaming)   |  | (batch 1AM BKK) |                     |
|  | -> member_info      |  | -> tiers         |                     |
|  | -> member_tier (CDC)|  |                  |                     |
|  | -> tier_events      |  |                  |                     |
|  | -> tier_maintenance |  |                  |                     |
|  +---------------------+  +-----------------+                      |
|  +---------------------+                                            |
|  | members-tiers-      |                                            |
|  | history-collector   |                                            |
|  | (batch 1AM BKK)     |                                            |
|  | -> members_tiers_   |                                            |
|  |    history           |                                            |
|  +---------------------+                                            |
|                                                                     |
|  MESSAGING (reference: purchases-collector)                         |
|  +---------------------+                                            |
|  | purchases-collector | <-- Reference pattern (identical arch)     |
|  | (Kafka streaming)   |                                            |
|  | -> purchases        |                                            |
|  +---------------------+                                            |
|                                                                     |
|  TRANSACTION (other team)                                           |
|  +---------------------+                                            |
|  | transaction/        | <-- Coordinate for shared resources       |
|  | collectors          |     (datasets, terraform, IAM)            |
|  +---------------------+                                            |
|                                                                     |
|  ALL projects share:                                                |
|  - Source: Iceberg on GCS via BLMS REST Catalog                     |
|  - Refined: BigQuery native tables (Storage Write API + CDC)       |
|  - Semantic: Dataform views (managed separately)                   |
|  - Compute: Dataflow (Apache Beam)                                 |
|  - CI/CD: GitLab CI -> GAR -> Dataflow FlexTemplate                |
+---------------------------------------------------------------------+
```

**Data flow per project**:
```
Loyalty:  Kafka (AWS) -> Dataflow -> Iceberg (GCS) + BQ (refined) -> Dataform (public)
Message:  Kafka (AWS) -> Dataflow -> Iceberg (GCS) + BQ (refined) -> Dataform (public)
Sales:    Pub/Sub     -> Dataflow -> Iceberg (GCS) + BQ (refined) -> Dataform (public)
```

**Shared infrastructure**:
- BigLake Metastore catalog: shared across all collectors in a region
- Per-collector GCS buckets: isolated storage for each collector
- Per-collector Artifact Registry repos: isolated container images
- Per-collector IAM: each collector's service account has access to its own
  source + refined datasets only
- Common Terraform: `common/GCP/biglake-metastore.tf` for shared catalog setup

### 4.7 Data Flow End-to-End Example

The following illustrates the complete data flow for the members-collector (streaming):

```
1. INGEST
   Kafka topic: "member-events"
     |
     v
   Dataflow (members-collector)
   - KafkaIO.read()
   - attach_event_name() [Schema A/B/C handling]
   - Parse JSON, extract fields

2. SOURCE WRITE (Iceberg)
   Beam managed.Write -> BLMS REST Catalog -> GCS
     |
     v
   gs://loyalty-members-source/member_info/data/ingestedTHDate=20260305/*.parquet

3. API ENRICHMENT
   member_id -> The1 API -> full member tier data
     |
     v
   Enriched member tier records (with CDC DELETE detection)

4. REFINED WRITE (BigQuery)
   Beam BigQueryIO (Storage Write API) -> BQ native tables
     |
     v
   loyalty_refined.member_tier      (CDC UPSERT/DELETE)
   loyalty_refined.member_tier_maintenance (CDC UPSERT)
   loyalty_refined.tier_events_*    (append-only)

5. SEMANTIC LAYER
   Dataform views (scheduled refresh)
     |
     v
   loyalty_public.member_summary    (joined view)
   loyalty_public.tier_changes      (event view)

6. CONSUMPTION
   Looker Studio / Connected Sheets / downstream systems
```

---

## 5. Limitations and Known Issues

### 5.1 BigQuery Quotas and Limits

#### Query Limits

| Limit | Value | Impact |
|---|---|---|
| Max concurrent on-demand queries | 100 per project | Can cause queuing during peak hours |
| Query timeout | 6 hours | Long-running ETL must be chunked |
| Max query size | 12 MB | Complex generated SQL may exceed |
| Max result rows (interactive) | Unlimited (with dest table) | Must write to table for large results |
| Max UDF per query | 50 | Complex transformation chains |
| Max wildcard tables | 1,000 | Log table patterns |

#### DML Limits

| Limit | Value | Impact |
|---|---|---|
| Concurrent DML per table | 20 PENDING | Queue limit per table |
| DML (UPDATE/DELETE/MERGE) per day | Unlimited | Previously limited, now removed |
| Partitions modified per DML | 10,000 | Large backfill operations |
| Max UPDATE/DELETE target rows | None (but cost) | Full table scan cost |

**Important note on DML vs Storage Write API**: The DML limits above apply to SQL DML
statements (INSERT, UPDATE, DELETE, MERGE). They do NOT apply to the Storage Write API,
which is what the loyalty data platform uses. Storage Write API has its own limits
(throughput-based, not statement-count-based), making it much more suitable for
high-frequency writes.

#### Streaming Limits (Storage Write API)

| Limit | Value | Impact |
|---|---|---|
| Throughput per project per region | 3 GB/s | Shared across all tables |
| Concurrent connections | 10,000 per project | Each Dataflow worker = 1+ connections |
| Row size | 10 MB | Large payloads need splitting |
| Pending stream bytes | 10 TB per project | Buffered mode accumulation |
| Committed stream bytes per table/day | Unlimited | No cap for CDC |

#### Storage Limits

| Limit | Value | Impact |
|---|---|---|
| Columns per table | 10,000 | Including nested STRUCT fields |
| Nesting depth | 15 levels | Deeply nested JSON structures |
| Max row size | 100 MB | Serialized protocol buffer size |
| Max table size | No limit | Cost is the practical limit |

### 5.2 BLMS Maturity Concerns

BigLake Metastore, while GA, has known gaps compared to mature metastores like
Hive Metastore or AWS Glue Data Catalog:

| Issue | Severity | Workaround |
|---|---|---|
| PyIceberg missing `defaults` field in BLMS response | Medium | Patch or use Spark/Beam managed.Write instead |
| Cannot create/modify Iceberg tables via BigQuery DDL/DML | High | Use Spark, REST API, or Beam managed.Write |
| No `ALTER TABLE ... RENAME TO` for BLMS tables | Low | Drop and recreate |
| Query performance slower than native BQ tables | Medium | Use metadata caching |
| `list_namespaces()`/`list_tables()` return errors | Low | Handle exceptions in client code |
| Credential vending setup complexity | Medium | Careful IAM configuration |
| No built-in table maintenance | Medium | Implement via Spark/PyIceberg externally |
| No branching/tagging (Iceberg v2 feature) | Low | Feature not yet supported |
| Single catalog per project+region | Low | Design namespace hierarchy carefully |
| Regional availability limitations | Medium | Verify region support before deployment |

**Workarounds used in the loyalty data platform**:
- Source Iceberg tables are auto-created by `managed.Write` (no PyIceberg dependency)
- Iceberg code removed from `deploy.py` (was causing PyIceberg issues)
- BQ table creation uses native BigQuery API (not BLMS)
- Table maintenance planned but not yet implemented

### 5.3 Cost Optimization Strategies

#### Query Cost Optimization (7 tips)

1. **Avoid `SELECT *`** -- specify only needed columns (single biggest cost mistake)
2. **Apply `WHERE` filters early** -- leverage partitioning and clustering
3. **Use `--dry-run`** to estimate cost before execution
4. **Leverage query caching** (24h free, automatic)
5. **Use materialized views** for repetitive aggregations (free refresh)
6. **Partition + cluster all large tables** -- can reduce scanned data by 10-100x
7. **Denormalize data** -- storage is cheap, compute (JOINs) is expensive

#### Storage Cost Optimization (5 tips)

1. **Set table/partition expiration** for temporary and old data
2. **Leverage long-term pricing** -- 50% discount automatically after 90 days
3. **Use GCS lifecycle policies** for Iceberg source data
4. **Remove unused tables/datasets** regularly
5. **Use columnar formats** (Parquet, ORC) for external data

#### Pricing Model Optimization (5 tips)

1. **On-demand** for <50K queries/month or sporadic workloads
2. **Capacity-based (slots)** for >50K queries/month or steady workloads
3. **Flex slots** (autoscaler) for burst capacity on top of baseline
4. **3-year commitments** for ~40% discount on steady-state workloads
5. **FlexRS** for batch Dataflow jobs (up to 40% cheaper)

#### Infrastructure Cost Optimization (3 tips)

1. **Use physical storage billing** (3-5x cheaper for compressed data)
   ```sql
   ALTER SCHEMA `project.dataset`
   SET OPTIONS (storage_billing_model = 'PHYSICAL');
   ```

2. **Enable `require_partition_filter`** to prevent accidental full scans
   ```sql
   ALTER TABLE `project.dataset.events`
   SET OPTIONS (require_partition_filter = TRUE);
   ```

3. **Monitor with INFORMATION_SCHEMA**
   ```sql
   -- Find most expensive queries in the last 7 days
   SELECT
       user_email,
       job_id,
       ROUND(total_bytes_processed / POW(2, 40), 2) AS tb_processed,
       ROUND(total_bytes_processed / POW(2, 40) * 6.25, 2) AS estimated_cost_usd,
       query
   FROM `region-us`.INFORMATION_SCHEMA.JOBS
   WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
   ORDER BY total_bytes_processed DESC
   LIMIT 20;
   ```

### 5.4 Lock-in Considerations and Mitigation

| Concern | Lock-in Risk | Mitigation |
|---|---|---|
| BigQuery SQL | Low-Medium | Standard SQL (ANSI:2011); use standard where possible |
| BigQuery Storage | High | Data in Capacitor format; store raw in Iceberg/Parquet on GCS |
| BLMS Catalog | Medium | Iceberg REST Catalog spec is standard; data is open format |
| Iceberg data files | Low | Open Parquet format; readable by any engine |
| Dataflow (Beam) | Low | Apache Beam is multi-runner (Flink, Spark, Direct) |
| GCS | Low | Standard object storage; easy to replicate to S3/Azure |
| IAM/Security | High | GCP-specific; must redesign for other clouds |
| Dataform | Medium | SQL-based; migrating to dbt is straightforward |
| BQML models | Medium | Use Vertex AI or portable frameworks instead |
| BI Engine | Low | Keep BI layer thin; transparent optimization |
| Data egress charges | Medium | Plan data locality carefully |
| Terraform | Low | Multi-cloud; same patterns work elsewhere |

**Best strategy**: Store data in Iceberg/Parquet on GCS for portability, use BigQuery
for analytics, avoid deep BQML dependency.

**Exit strategy** (if moving off GCP):
1. Source data (Iceberg/Parquet on GCS) -- copy to S3/ABFS, point new catalog at it
2. Beam pipelines -- change runner from Dataflow to Flink/Spark
3. Refined data -- export from BQ to Parquet, load into new warehouse
4. Dataform views -- rewrite as dbt models (similar SQL)
5. IAM/Security -- redesign for new cloud provider

---

## 6. Cost Summary Table

### BigQuery Costs

| Component | Pricing | Free Tier |
|---|---|---|
| On-demand queries | $6.25/TB scanned | 1 TiB/month |
| Standard slots (autoscaler) | $0.04/slot-hour | -- |
| Enterprise slots (autoscaler) | $0.06/slot-hour | -- |
| Enterprise Plus slots (autoscaler) | $0.10/slot-hour | -- |
| Enterprise 1-year commitment | ~20% discount | -- |
| Enterprise 3-year commitment | ~40% discount | -- |
| Active storage (logical) | $0.02/GB/month | 10 GB |
| Long-term storage (logical) | $0.01/GB/month | -- |
| Active storage (physical) | $0.04/GB/month | 10 GB |
| Long-term storage (physical) | $0.02/GB/month | -- |
| Storage Write API (committed) | Free | -- |
| Storage Write API (buffered) | $0.025/GB | 2 TB/month |
| Legacy streaming inserts | $0.010/200 MB | -- |
| BI Engine reservation | $0.0416/GB/hour | -- |
| BigQuery ML | Varies by model type | 10 GB data/month |
| Data extraction | $0.011/GB | 10 GB/month |

### GCS Costs

| Component | Standard | Nearline | Coldline | Archive |
|---|---|---|---|---|
| Storage per GB/month | $0.020-0.026 | $0.010-0.020 | $0.004-0.014 | $0.0022-0.005 |
| Class A ops per 10K | $0.05 | $0.10 | $0.10 | $0.50 |
| Class B ops per 10K | $0.004 | $0.01 | $0.05 | $0.50 |
| Retrieval per GB | Free | $0.01 | $0.02 | $0.05 |
| Egress (intra-region) | Free | Free | Free | Free |
| Egress (inter-region) | $0.01/GB | $0.01/GB | $0.01/GB | $0.01/GB |

> Prices vary by region. Always verify at official pricing pages.

### Other Related Costs

| Service | Pricing | Free Tier |
|---|---|---|
| BigLake API | Included with BigQuery | -- |
| BLMS (Metastore) | Included with BigLake | -- |
| Dataflow (compute) | Per vCPU-hr, GB-hr, PD GB-hr | -- (see CLOUD_SERVICES doc) |
| Secret Manager | $0.06/10K access operations | 6 active versions |
| Cloud Logging | $0.50/GB ingested | 50 GB/month |
| Cloud Monitoring | Free for GCP metrics | First 150 MB API calls |

### Estimated Monthly Cost Scenarios

| Scenario | Description | Storage | Compute | Total Estimate |
|---|---|---|---|---|
| **Small** | 10 GB data, 100 queries | ~$0.20 | Free tier | ~$0.20 |
| **Medium** | 1 TB data, 10K queries, 10 TB scanned | ~$20 | ~$62.50 | ~$82.50 |
| **Large** | 100 TB data, 50K queries, 500 TB scanned | ~$1,500 | ~$3,125 | ~$4,625 |
| **Enterprise** | 1 PB data, 100-slot reservation | ~$15,000 | ~$4,400/mo (1-yr) | ~$19,400 |
| **Loyalty project** | 50 GB source, 20 GB refined, streaming | ~$5 | ~$200 (Dataflow) | ~$205 |

---

## 7. References

### Official Google Cloud Documentation

- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [BigQuery Architecture -- Under the Hood](https://cloud.google.com/blog/products/bigquery/bigquery-under-the-hood)
- [BigQuery Editions](https://cloud.google.com/bigquery/docs/editions-intro)
- [BigQuery Pricing](https://cloud.google.com/bigquery/pricing)
- [BigQuery Quotas and Limits](https://cloud.google.com/bigquery/quotas)
- [BigQuery Partitioned Tables](https://cloud.google.com/bigquery/docs/partitioned-tables)
- [BigQuery Clustered Tables](https://cloud.google.com/bigquery/docs/clustered-tables)
- [BigQuery CDC with Storage Write API](https://cloud.google.com/bigquery/docs/change-data-capture)
- [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
- [BigQuery Storage Write API Quotas](https://cloud.google.com/bigquery/quotas#write-api-limits)
- [BigQuery Materialized Views](https://cloud.google.com/bigquery/docs/materialized-views-intro)
- [BigQuery BI Engine](https://cloud.google.com/bigquery/docs/bi-engine-intro)
- [BigQuery ML](https://cloud.google.com/bigquery/docs/bqml-introduction)
- [BigQuery INFORMATION_SCHEMA](https://cloud.google.com/bigquery/docs/information-schema-intro)
- [DML Without Limits (Sep 2025)](https://cloud.google.com/blog/products/data-analytics/dml-without-limits-now-in-bigquery)
- [BigQuery September 2025 Default Changes](https://medium.com/@paul.brabban/bigquery-safer-by-default-from-september-2025-5fd9da0d78f0)
- [BigLake Documentation](https://cloud.google.com/biglake/docs)
- [BigLake Metastore](https://cloud.google.com/biglake/docs/about-blms)
- [BLMS REST Catalog](https://cloud.google.com/biglake/docs/blms-rest-catalog)
- [BigLake Managed Tables](https://cloud.google.com/bigquery/docs/manage-open-source-metadata)
- [BigLake Credential Vending](https://cloud.google.com/biglake/docs/credential-vending)
- [BigQuery Omni](https://cloud.google.com/bigquery/docs/omni-introduction)
- [GCS Storage Classes](https://cloud.google.com/storage/docs/storage-classes)
- [GCS Lifecycle Management](https://cloud.google.com/storage/docs/lifecycle)
- [GCS Pricing](https://cloud.google.com/storage/pricing)
- [Dataform Documentation](https://cloud.google.com/dataform/docs)
- [Dataform vs dbt](https://cloud.google.com/dataform/docs/compare-dataform-dbt)

### Apache Iceberg

- [Apache Iceberg Official Site](https://iceberg.apache.org/)
- [Iceberg Spec (Table Format)](https://iceberg.apache.org/spec/)
- [Iceberg REST Catalog Spec](https://iceberg.apache.org/docs/latest/rest-catalog/)
- [Iceberg Format v2 Spec](https://iceberg.apache.org/spec/#format-version-2)
- [PyIceberg Documentation](https://py.iceberg.apache.org/)
- [Iceberg on GCP Guide](https://cloud.google.com/bigquery/docs/iceberg-tables)
- [PyIceberg BLMS Issue (GitHub #2122)](https://github.com/apache/iceberg-python/issues/2122)

### Apache Beam / Dataflow

- [Beam IcebergIO (managed.Write)](https://beam.apache.org/documentation/io/built-in/iceberg/)
- [Beam BigQueryIO](https://beam.apache.org/documentation/io/built-in/google-bigquery/)
- [Dataflow Documentation](https://cloud.google.com/dataflow/docs)
- [Dataflow Pricing](https://cloud.google.com/dataflow/pricing)

### Research Papers and Blog Posts

- [Dremel: Interactive Analysis of Web-Scale Datasets (Google, 2010)](https://research.google/pubs/pub36632/)
- [Dremel: A Decade of Interactive SQL Analysis at Web Scale (2020)](https://research.google/pubs/pub49143/)
- [Jupiter Rising: A Decade of Clos Topologies at Google](https://research.google/pubs/pub43837/)
- [Large-scale cluster management at Google with Borg](https://research.google/pubs/pub43438/)
- [Colossus: The next generation of GFS](https://cloud.google.com/blog/products/storage-data-transfer/a-peek-behind-colossus-googles-file-system)
- [BigLake Research Paper (Google Research)](https://research.google/pubs/biglake-bigquerys-evolution-toward-a-multi-cloud-lakehouse/)

### Open Table Format Comparisons

- [Iceberg vs Delta Lake vs Hudi (Dremio)](https://www.dremio.com/blog/comparison-of-data-lake-table-formats-iceberg-hudi-and-delta-lake/)
- [Apache Iceberg: The Definitive Guide (O'Reilly)](https://www.oreilly.com/library/view/apache-iceberg-the/9781098148614/)
- [Delta Lake Documentation](https://docs.delta.io/latest/)
- [Apache Hudi Documentation](https://hudi.apache.org/docs/overview)
- [Open Table Formats Guide (DEV Community)](https://dev.to/alexmercedcoder/the-ultimate-guide-to-open-table-formats-iceberg-delta-lake-hudi-paimon-and-ducklake-dnk)
- [GCP & Iceberg Deep Dive (Substack)](https://juhache.substack.com/p/gcp-and-iceberg)
- [Apache Iceberg in BigQuery (Atlan)](https://atlan.com/know/iceberg/apache-iceberg-bigquery/)

### Third-Party Pricing Analysis

- [BigQuery Pricing Guide 2026 (Airbyte)](https://airbyte.com/data-engineering-resources/bigquery-pricing)
- [BigQuery Editions (DoiT)](https://www.doit.com/blog/bigquery-editions-and-what-you-need-to-know/)
- [BigQuery Editions (Masthead)](https://mastheadata.com/blog/pricing-editions)
- [BigQuery Architecture (Panoply)](https://panoply.io/data-warehouse-guide/bigquery-architecture/)
- [BigQuery Cost Optimization (e6data)](https://www.e6data.com/query-and-cost-optimization-hub/how-to-optimize-bigquery-costs)
- [Reduce BigQuery Costs (dbt Labs)](https://www.getdbt.com/blog/reduce-bigquery-costs)
- [GCS Pricing Guide (CloudZero)](https://www.cloudzero.com/blog/gcp-storage-pricing/)

### Terraform

- [Google Cloud Terraform Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [BigQuery Terraform Resources](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_table)
- [BigLake Terraform Resources](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/biglake_catalog)

---

> **Document Version**: 2.0 | **Last Updated**: 2026-03-05
