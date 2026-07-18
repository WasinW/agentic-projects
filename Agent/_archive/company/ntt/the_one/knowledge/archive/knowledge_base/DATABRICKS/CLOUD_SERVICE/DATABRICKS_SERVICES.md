# Databricks Services & Ecosystem - Comprehensive Knowledge Base

> **Last Updated**: 2026-03-05
> **Scope**: Data processing, orchestration, ingestion, ML/AI, data sharing, security, developer experience

---

## Table of Contents

1. [Data Processing](#1-data-processing)
2. [Orchestration and Workflows](#2-orchestration-and-workflows)
3. [Data Ingestion](#3-data-ingestion)
4. [ML and AI](#4-ml-and-ai)
5. [Data Sharing](#5-data-sharing)
6. [Security](#6-security)
7. [Developer Experience](#7-developer-experience)
8. [Sources](#8-sources)

---

## 1. Data Processing

### 1.1 Apache Spark Optimizations on Databricks

Databricks runs an **optimized distribution of Apache Spark** called **Databricks Runtime** (DBR), which includes proprietary and open-source enhancements over vanilla Spark.

#### 1.1.1 Photon Engine

**Photon** is Databricks' proprietary vectorized query engine written in C++ that replaces the JVM-based Spark SQL execution layer for supported operations:

```
Standard Spark Execution:          Photon Execution:
+-------------------+              +-------------------+
| Spark SQL Plan    |              | Spark SQL Plan    |
+--------+----------+              +--------+----------+
         |                                  |
         v                                  v
+-------------------+              +-------------------+
| JVM (Scala/Java)  |              | Photon (C++)       |
| Row-by-row exec   |              | Vectorized/SIMD    |
| GC pauses         |              | No GC overhead     |
| Object overhead   |              | Columnar batches   |
+-------------------+              +-------------------+
         |                                  |
         v                                  v
   1x baseline                     2-8x faster (typical)
```

**Key Photon characteristics**:
- **Columnar vectorized execution**: Processes data in batches of column vectors (typically 1024-4096 rows at a time) using CPU SIMD instructions
- **Native C++ implementation**: Eliminates JVM garbage collection pauses, object header overhead, and Java serialization costs
- **Transparent fallback**: Operations not yet supported by Photon fall back to the JVM Spark engine. No code changes required.
- **Supported operations**: Scans, filters, projections, aggregations, joins (hash join, sort-merge join, broadcast join), window functions, string operations, type casts
- **Not yet supported**: Some UDFs, certain complex types, Python UDFs (still run in JVM/Python)
- **Performance**: 2-8x speedup for SQL/DataFrame workloads; up to 10x for scan-heavy analytics. TPC-DS benchmarks show Photon-enabled clusters completing in 40-60% of the time compared to standard Spark.
- **Cost trade-off**: Photon clusters consume a higher DBU rate (~$0.55 vs $0.40 for All-Purpose, ~$0.20 vs $0.15 for Jobs). Net cost benefit depends on whether speedup outweighs the rate premium.
- **Availability**: Enabled by default on SQL Warehouses. Optional on All-Purpose and Jobs clusters (select "Photon" runtime in cluster configuration).

#### 1.1.2 Adaptive Query Execution (AQE)

**AQE** re-optimizes query plans at runtime based on actual data statistics collected during execution (after shuffle and broadcast exchanges). This addresses the fundamental problem that static query planning has inaccurate cardinality estimates.

**Four key AQE optimizations**:

| Optimization                          | What It Does                                                   | When It Helps                        |
|---------------------------------------|----------------------------------------------------------------|--------------------------------------|
| **Dynamic join strategy switching**   | Converts sort-merge join to broadcast hash join at runtime when one side is small | When optimizer overestimates table size |
| **Dynamic partition coalescing**      | Merges small post-shuffle partitions into larger ones          | After skewed shuffles or over-partitioning |
| **Dynamic skew join handling**        | Splits skewed partitions across multiple tasks                | When data has key skew (hot keys)    |
| **Empty relation propagation**        | Short-circuits execution when a relation is detected as empty | When filters eliminate all rows early |

**Configuration** (enabled by default on Databricks):
```python
# AQE is enabled by default on DBR 7.3+
# Key tuning parameters:
spark.conf.set("spark.sql.adaptive.enabled", "true")  # default: true
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.localShuffleReader.enabled", "true")

# Skew detection threshold
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256mb")

# Coalesce target size
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "64mb")
```

**Performance impact**: Databricks internal benchmarks show a median 1.38x speedup with AQE alone, and 2.87x speedup when AQE is combined with Photon.

#### 1.1.3 Cost-Based Optimizer (CBO)

The CBO uses **table and column statistics** to make optimal decisions about:
- Join ordering (which tables to join first)
- Join strategy (broadcast vs. sort-merge vs. shuffle hash)
- Aggregation strategy (hash vs. sort)
- Filter push-down ordering

```sql
-- Collect statistics for CBO
ANALYZE TABLE my_table COMPUTE STATISTICS;
ANALYZE TABLE my_table COMPUTE STATISTICS FOR COLUMNS col1, col2, col3;

-- Verify statistics are available
DESCRIBE EXTENDED my_table;

-- Check query plan to see CBO decisions
EXPLAIN COST SELECT * FROM fact_table f JOIN dim_table d ON f.key = d.key;
```

**Statistics collected**:
- Table-level: row count, size in bytes
- Column-level: distinct count, null count, min, max, average length, histogram (equi-height)

**Best practice**: Run `ANALYZE TABLE` after major data loads or schema changes. Without statistics, the CBO falls back to heuristic-based optimization (less accurate).

#### 1.1.4 Dynamic File Pruning (DFP)

**Dynamic File Pruning** eliminates irrelevant data files at runtime based on join predicates, especially effective for **star-schema** queries:

```
Without DFP:                         With DFP:
Fact table: 1000 files               Fact table: 50 files (pruned!)
  |                                     |
  +-- Read ALL files                    +-- Read only files matching
  |                                     |   join keys from dimension
  v                                     v
JOIN with dimension                   JOIN with dimension
(filter: region='US')                 (filter applied BEFORE fact scan)
```

**How it works**:
1. Execute the dimension-side filter first (e.g., `WHERE region = 'US'`)
2. Collect the resulting join keys (e.g., `region_id IN (1, 2, 3)`)
3. Use these keys to prune fact table files based on Delta min/max statistics
4. Only read fact table files that could contain matching rows

**Best for**: Star-schema joins where a small dimension table filters a large fact table. DFP can skip 80-95% of fact table files in typical scenarios.

**Requirements**: Delta table with column statistics (enabled by default). Works automatically -- no configuration needed.

#### 1.1.5 Predictive I/O

**Predictive I/O** is a Databricks-specific optimization available on Pro and Serverless SQL Warehouses:

- **Intelligent prefetching**: Predicts which data files and column chunks will be needed based on query patterns and historical access
- **Caching**: Automatically caches frequently accessed data on local SSDs
- **Read optimization**: Reorders I/O operations to minimize latency and maximize throughput
- **Delta-aware**: Understands Delta table structure to prefetch transaction log entries and optimize checkpoint reads

**Availability**: SQL Pro and SQL Serverless warehouses only (not available on Classic or All-Purpose clusters).

### 1.2 Structured Streaming

Databricks provides enhanced **Apache Spark Structured Streaming** for real-time and near-real-time data processing.

#### 1.2.1 Processing Modes

| Mode              | Latency          | How It Works                                           | Use Case                          |
|-------------------|------------------|--------------------------------------------------------|-----------------------------------|
| **Micro-batch**   | ~100ms-seconds   | Processes data in small batches at a configurable trigger interval | Most streaming workloads   |
| **Continuous**    | ~1-5ms           | Processes each record as it arrives (experimental in OSS Spark) | Ultra-low latency         |
| **Trigger.AvailableNow** | Batch-like | Processes all available data, then stops                | Incremental batch processing      |
| **Trigger.Once**  | Batch-like       | Processes exactly one micro-batch, then stops           | Scheduled incremental loads       |

**Micro-batch** (default, most common):
```python
# Micro-batch streaming query
query = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker:9092")
    .option("subscribe", "events")
    .load()
    .writeStream
    .format("delta")
    .option("checkpointLocation", "/checkpoints/events")
    .trigger(processingTime="10 seconds")  # micro-batch every 10s
    .toTable("bronze.events")
)
```

**Continuous mode** (5ms latency, Databricks-enhanced):
```python
# Real-time mode (Databricks-specific, DBR 16+)
query = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker:9092")
    .option("subscribe", "events")
    .load()
    .writeStream
    .format("delta")
    .option("checkpointLocation", "/checkpoints/events")
    .trigger(continuous="5 milliseconds")
    .toTable("bronze.events")
)
```

**Trigger.AvailableNow** (batch-style streaming):
```python
# Process all available data, then stop (great for scheduled jobs)
query = (
    spark.readStream
    .format("delta")
    .table("bronze.events")
    .writeStream
    .format("delta")
    .option("checkpointLocation", "/checkpoints/silver_events")
    .trigger(availableNow=True)
    .toTable("silver.events")
)
# Query processes all pending data, maintains checkpoint, then terminates
```

#### 1.2.2 Structured Streaming + Delta Lake Integration

Delta Lake is the **recommended sink** for Structured Streaming on Databricks:

| Feature                          | Description                                                    |
|----------------------------------|----------------------------------------------------------------|
| **Exactly-once semantics**       | Delta's ACID guarantees prevent duplicate writes on retry       |
| **Schema enforcement**           | Rejects writes that do not match the table schema               |
| **Automatic compaction**         | `autoOptimize.autoCompact` merges small streaming files         |
| **Optimize write**               | `optimizeWrite` coalesces output files during streaming writes  |
| **Merge (upsert) on stream**     | `foreachBatch` + `MERGE INTO` for streaming upserts             |
| **Change Data Feed**             | Stream consumers can read only changes from a Delta table       |
| **Idempotent restart**           | Checkpoint-based recovery ensures no data loss or duplication   |

**Streaming upsert pattern** (very common):
```python
def upsert_to_delta(batch_df, batch_id):
    target = DeltaTable.forName(spark, "silver.users")
    target.alias("t").merge(
        batch_df.alias("s"),
        "t.user_id = s.user_id"
    ).whenMatchedUpdateAll() \
     .whenNotMatchedInsertAll() \
     .execute()

query = (
    spark.readStream
    .format("kafka")
    .option("subscribe", "user_updates")
    .load()
    .writeStream
    .foreachBatch(upsert_to_delta)
    .option("checkpointLocation", "/checkpoints/user_upsert")
    .trigger(processingTime="30 seconds")
    .start()
)
```

#### 1.2.3 Streaming Metrics and Monitoring

```python
# Access streaming query progress
query.lastProgress  # Latest micro-batch metrics
query.recentProgress  # Recent history

# Key metrics in StreamingQueryProgress:
# - inputRowsPerSecond: rate of incoming data
# - processedRowsPerSecond: rate of processing
# - batchDuration: time per micro-batch
# - triggerExecution: breakdown of processing time
# - watermark: current event-time watermark
```

**Monitoring options**:
- **Spark UI**: Structured Streaming tab shows running queries
- **StreamingQueryListener**: Programmatic listener for custom monitoring
- **Databricks SQL Dashboard**: Query system tables for streaming metrics
- **Ganglia/CloudWatch/Azure Monitor**: Infrastructure-level monitoring

### 1.3 Databricks Runtime Versions

Databricks Runtime (DBR) is the set of software (Spark, Delta Lake, libraries) that runs on clusters.

#### 1.3.1 Current Versions (as of early 2026)

| Runtime Version   | Spark Version | Delta Lake | Python | Status           | Key Changes                                |
|-------------------|---------------|------------|--------|------------------|--------------------------------------------|
| **DBR 16.4 LTS**  | 3.5.x         | 3.3.x      | 3.11   | GA (LTS)         | Zstd default compression, Scala 2.12/2.13  |
| **DBR 15.4 LTS**  | 3.5.x         | 3.2.x      | 3.11   | GA (LTS)         | Liquid clustering GA, UniForm improvements  |
| **DBR 14.3 LTS**  | 3.5.x         | 3.1.x      | 3.10   | GA (LTS)         | Deletion vectors default, Photon improvements|
| **DBR 13.3 LTS**  | 3.4.x         | 2.4.x      | 3.10   | GA (LTS, EOL approaching) | Liquid clustering preview, DV support |

**LTS (Long-Term Support)**: Supported for ~2-3 years with critical bug fixes and security patches. Production workloads should always use LTS versions.

**Non-LTS versions** (e.g., DBR 15.0, 15.1, 15.2, 15.3): Short-lived, for early access to new features. Not recommended for production.

#### 1.3.2 Runtime Variants

| Variant                  | Suffix         | Includes                                              |
|--------------------------|----------------|-------------------------------------------------------|
| **Standard**             | (none)         | Spark, Delta Lake, Python, R, Scala                   |
| **ML**                   | `-ml`          | + TensorFlow, PyTorch, scikit-learn, MLflow, Hugging Face |
| **Photon**               | (cluster config) | Standard + Photon engine enabled                    |
| **GPU**                  | `-gpu`         | ML + NVIDIA CUDA, cuDF, RAPIDS                        |
| **Genomics**             | `-hls`         | Standard + bioinformatics libraries                   |

**Example cluster configuration**:
```json
{
  "spark_version": "16.4.x-scala2.12",     // Standard LTS
  "spark_version": "16.4.x-ml-scala2.12",  // ML Runtime
  "spark_version": "16.4.x-gpu-ml-scala2.12", // GPU ML Runtime
  "runtime_engine": "PHOTON"                // Enable Photon
}
```

#### 1.3.3 Key Changes Across Versions

| Version   | Notable Changes                                                              |
|-----------|------------------------------------------------------------------------------|
| DBR 17.x  | Spark 4.x (upcoming), Scala 2.13 only, ANSI mode default, variant type      |
| DBR 16.x  | Zstd compression default, Scala 2.12+2.13 dual images, history sharing default |
| DBR 15.x  | Liquid clustering GA, UniForm Iceberg GA, enhanced Photon coverage           |
| DBR 14.x  | Deletion vectors default, column mapping name mode default, Photon improvements |
| DBR 13.x  | Liquid clustering preview, DV support, Unity Catalog mandatory for new workspaces |

### 1.4 GPU Support and ML Runtime

Databricks provides first-class GPU support for machine learning and deep learning workloads:

**GPU cluster types**:
- **Single-node GPU**: For development and small model training
- **Multi-node GPU**: Distributed training with Horovod, PyTorch DDP, DeepSpeed
- **GPU SQL**: Photon does NOT use GPU; SQL workloads use CPU-optimized Photon

**Supported GPU instances**:

| Cloud | GPU Instance Types                     | GPU                | Use Case                    |
|-------|----------------------------------------|--------------------|-----------------------------|
| AWS   | p3.2xlarge, p3.8xlarge, p4d.24xlarge   | V100, A100          | Training, fine-tuning       |
| AWS   | g5.xlarge - g5.48xlarge                | A10G                | Inference, light training   |
| Azure | NC6s_v3, NC24s_v3, ND96asr_v4         | V100, A100          | Training, fine-tuning       |
| GCP   | n1-standard-4 + T4/A100               | T4, A100, H100      | Training, inference         |

**ML Runtime includes**:
- **TensorFlow**: With GPU acceleration (CUDA, cuDNN)
- **PyTorch**: With GPU acceleration and distributed training
- **Hugging Face Transformers**: Pre-installed for NLP/LLM workloads
- **RAPIDS (cuDF, cuML)**: GPU-accelerated Pandas and scikit-learn
- **Horovod**: Distributed deep learning training
- **MLflow**: Experiment tracking and model registry

---

## 2. Orchestration and Workflows

### 2.1 Lakeflow Jobs (Databricks Workflows)

**Databricks Workflows** (recently rebranded as part of **Lakeflow**) is the native orchestration service for scheduling and managing data pipelines, ML training, and operational tasks.

```
+--------------------------------------------------+
|                  Lakeflow Jobs                      |
|                                                    |
|  Task 1: Ingest     Task 2: Transform    Task 3:  |
|  (Notebook)    -->  (Python script) -->  (SQL)     |
|       |                  |                  |      |
|       v                  v                  v      |
|  +--------+        +----------+       +---------+  |
|  | Bronze |        | Silver   |       | Gold    |  |
|  +--------+        +----------+       +---------+  |
|                                                    |
|  Task 4: Train Model    Task 5: Deploy             |
|  (Python, GPU cluster)  (Model Serving)            |
+--------------------------------------------------+
```

**Key features**:

| Feature                    | Description                                                        |
|----------------------------|--------------------------------------------------------------------|
| **DAG orchestration**      | Define task dependencies as a directed acyclic graph               |
| **Multiple task types**    | Notebooks, Python scripts, JARs, SQL, DLT pipelines, dbt, Spark Submit |
| **Parameterization**       | Pass parameters between tasks via task values                       |
| **Conditional execution**  | Run tasks based on conditions (if/else logic)                       |
| **Error handling**         | Retry policies, timeout settings, failure notifications             |
| **Multi-cluster**          | Each task can run on a different cluster (different size/config)    |
| **Scheduling**             | Cron-based schedules, file arrival triggers, continuous             |
| **Monitoring**             | Run history, task-level metrics, alerts, Gantt chart visualization  |
| **Repair runs**            | Re-run only failed tasks without re-running successful ones         |
| **Git integration**        | Tasks can reference notebooks/code from Git repos                   |

**Job definition example (JSON)**:
```json
{
  "name": "daily_etl_pipeline",
  "schedule": {
    "quartz_cron_expression": "0 0 2 * * ?",
    "timezone_id": "Asia/Bangkok"
  },
  "tasks": [
    {
      "task_key": "ingest_raw",
      "notebook_task": {
        "notebook_path": "/Repos/team/etl/01_ingest"
      },
      "job_cluster_key": "etl_cluster",
      "timeout_seconds": 3600,
      "max_retries": 2
    },
    {
      "task_key": "transform_silver",
      "depends_on": [{"task_key": "ingest_raw"}],
      "python_wheel_task": {
        "package_name": "my_transforms",
        "entry_point": "run_silver"
      },
      "job_cluster_key": "etl_cluster"
    },
    {
      "task_key": "aggregate_gold",
      "depends_on": [{"task_key": "transform_silver"}],
      "sql_task": {
        "query": {"query_id": "abc123"},
        "warehouse_id": "def456"
      }
    }
  ],
  "job_clusters": [
    {
      "job_cluster_key": "etl_cluster",
      "new_cluster": {
        "spark_version": "16.4.x-scala2.12",
        "node_type_id": "m5.xlarge",
        "num_workers": 4,
        "runtime_engine": "PHOTON"
      }
    }
  ]
}
```

### 2.2 Task Types and Orchestration

**Supported task types**:

| Task Type          | Description                                              | Compute                        |
|--------------------|----------------------------------------------------------|--------------------------------|
| **Notebook**       | Run a Databricks notebook (Python, Scala, SQL, R)        | Job cluster or all-purpose     |
| **Python script**  | Run a Python file from workspace or repos                | Job cluster or all-purpose     |
| **Python wheel**   | Run a packaged Python wheel                              | Job cluster or all-purpose     |
| **JAR**            | Run a Spark JAR (Scala/Java)                             | Job cluster or all-purpose     |
| **Spark Submit**   | Submit arbitrary Spark applications                      | Job cluster                    |
| **SQL**            | Run SQL queries or dashboards                            | SQL Warehouse                  |
| **DLT pipeline**   | Trigger a Delta Live Tables pipeline                     | DLT-managed cluster            |
| **dbt**            | Run dbt models                                           | SQL Warehouse                  |
| **If/Else**        | Conditional branching based on task values                | N/A (control flow)             |
| **For Each**       | Loop over a collection, running sub-tasks for each item  | Varies per sub-task            |
| **Run Job**        | Trigger another Databricks job                            | Inherits target job's compute  |

**Task values** (inter-task communication):
```python
# In task A: set a value
dbutils.jobs.taskValues.set(key="row_count", value=42000)

# In task B (depends on A): read the value
count = dbutils.jobs.taskValues.get(taskKey="task_a", key="row_count")
if count > 0:
    # process...
```

### 2.3 Job Clusters vs All-Purpose Clusters

| Aspect                    | Job Cluster                          | All-Purpose Cluster                  |
|---------------------------|--------------------------------------|--------------------------------------|
| **Purpose**               | Automated, scheduled workloads       | Interactive development, exploration |
| **Lifecycle**             | Created at job start, terminated at end | Long-running, manually managed    |
| **DBU rate (Premium)**    | $0.15/DBU (standard)                | $0.55/DBU (standard)                |
| **Cost efficiency**       | Excellent (pay only for job duration)| Poor (pays for idle time too)        |
| **Startup time**          | 3-8 minutes (unless cluster pool)    | Already running (if pre-started)     |
| **Collaboration**         | No (single job execution)            | Yes (shared notebooks)               |
| **Cluster pools**         | Supported (faster startup)           | Supported                            |
| **Best for**              | Production ETL, ML training, scheduled jobs | Development, debugging, ad-hoc analysis |

**Best practice**: Always use **Job Clusters** for production workloads. The 73% DBU savings ($0.15 vs $0.55) is significant at scale. Use All-Purpose clusters only for interactive development.

### 2.4 Integration with Apache Airflow

Databricks integrates with Apache Airflow through the official **Databricks Airflow Provider**:

```python
# pip install apache-airflow-providers-databricks

from airflow import DAG
from airflow.providers.databricks.operators.databricks import (
    DatabricksRunNowOperator,
    DatabricksSubmitRunOperator,
)
from datetime import datetime

with DAG("databricks_etl", start_date=datetime(2026, 1, 1), schedule="0 2 * * *") as dag:

    # Option 1: Trigger an existing Databricks job
    trigger_etl = DatabricksRunNowOperator(
        task_id="trigger_etl_job",
        databricks_conn_id="databricks_default",
        job_id=12345,
        notebook_params={"date": "{{ ds }}"},
    )

    # Option 2: Submit a one-time run
    submit_training = DatabricksSubmitRunOperator(
        task_id="submit_ml_training",
        databricks_conn_id="databricks_default",
        new_cluster={
            "spark_version": "16.4.x-ml-scala2.12",
            "node_type_id": "p3.2xlarge",
            "num_workers": 2,
        },
        notebook_task={
            "notebook_path": "/Repos/ml/train_model",
            "base_parameters": {"experiment_id": "42"},
        },
    )

    trigger_etl >> submit_training
```

**Airflow operators available**:

| Operator                         | Description                                          |
|----------------------------------|------------------------------------------------------|
| `DatabricksRunNowOperator`       | Trigger existing Databricks job by job_id             |
| `DatabricksSubmitRunOperator`    | Submit one-time run with inline cluster/task config   |
| `DatabricksNotebookOperator`     | Run a specific notebook with parameters               |
| `DatabricksSqlOperator`          | Execute SQL against a SQL Warehouse                   |
| `DatabricksTaskOperator`         | Run a specific task within a multi-task job            |

**When to use Airflow vs Databricks Workflows**:

| Scenario                                    | Recommended Orchestrator        |
|---------------------------------------------|---------------------------------|
| Pure Databricks workloads                   | Databricks Workflows            |
| Mixed (Databricks + non-Databricks tasks)   | Airflow with Databricks provider|
| Existing Airflow investment                  | Airflow                         |
| Complex conditional logic, sensors           | Airflow                         |
| Simple DAG, fast setup                       | Databricks Workflows            |
| Need managed orchestration (no infra)        | Databricks Workflows            |

---

## 3. Data Ingestion

### 3.1 Lakeflow Connect (Managed Ingestion)

**Lakeflow Connect** (formerly known as Ingestion Pipelines) is Databricks' managed, no-code/low-code service for ingesting data from SaaS applications and databases directly into the lakehouse.

```
+-------------------+         +-------------------+        +-------------+
| Source Systems     |  CDC/   | Lakeflow Connect   | Delta  | Lakehouse   |
| - Salesforce       | API --> | (managed by        | --->   | - Bronze    |
| - HubSpot          |         |  Databricks)       |        | - Silver    |
| - PostgreSQL       |         +-------------------+        +-------------+
| - MySQL            |         | Auto-schema detect |
| - SQL Server       |         | Incremental sync   |
| - Oracle           |         | Error handling     |
| - MongoDB          |         | Monitoring         |
+-------------------+         +-------------------+
```

**Supported sources** (as of early 2026):

| Category         | Sources                                                           |
|------------------|-------------------------------------------------------------------|
| **Databases**    | PostgreSQL, MySQL, SQL Server, Oracle, MongoDB, Amazon RDS        |
| **SaaS Apps**    | Salesforce, HubSpot, Google Analytics, Workday, SAP, ServiceNow   |
| **Data Warehouses** | Snowflake, BigQuery, Redshift                                  |
| **Cloud Storage** | S3, ADLS, GCS (via Auto Loader -- see below)                    |

**Key features**:
- **Schema inference**: Automatically detects source schema and creates target tables
- **Incremental sync**: CDC-based replication for databases (Debezium-based)
- **Full refresh fallback**: Option to do full table reloads when CDC is not available
- **Error handling**: Dead-letter tables for failed records
- **Monitoring**: Built-in pipeline health dashboards
- **Unity Catalog integration**: Target tables automatically registered in Unity Catalog

### 3.2 Auto Loader (Incremental File Ingestion)

**Auto Loader** (`cloudFiles`) is Databricks' recommended approach for incrementally ingesting new files from cloud storage:

```python
# Auto Loader: Ingest new JSON files as they arrive in S3/ADLS/GCS
df = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "/checkpoints/orders/schema")
    .option("cloudFiles.inferColumnTypes", "true")
    .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
    .load("/data/landing/orders/")
)

# Write to Delta Bronze table
df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/checkpoints/orders/") \
    .option("mergeSchema", "true") \
    .trigger(availableNow=True) \
    .toTable("bronze.orders")
```

**How Auto Loader discovers new files**:

| Mode                | How It Works                                       | Latency      | Cost                  |
|---------------------|----------------------------------------------------|--------------|-----------------------|
| **Directory listing** | Periodically lists the directory and diffs against checkpoint | Seconds-minutes | Low (API calls)   |
| **File notification** | Cloud event notifications (S3 SQS, ADLS EventGrid, GCS Pub/Sub) | Sub-second  | Minimal (event-based) |

**File notification setup** (recommended for high-volume):
```python
df = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "parquet")
    .option("cloudFiles.useNotifications", "true")  # Use cloud events
    .option("cloudFiles.schemaLocation", "/checkpoints/schema/")
    .load("s3://my-bucket/incoming/")
)
```

**Auto Loader advantages over manual file listing**:
- **Exactly-once**: Checkpoint tracks which files have been processed; no duplicates on restart
- **Schema evolution**: Detect and handle new columns automatically (`schemaEvolutionMode`)
- **Rescue column**: Unknown/malformed fields go to `_rescued_data` column instead of failing
- **Scalable**: Handles millions of files per directory via file notification mode
- **Cost-effective**: Avoids expensive LIST operations on cloud storage

**Supported file formats**: JSON, CSV, Parquet, Avro, ORC, text, binary, XML

### 3.3 COPY INTO

**COPY INTO** is a SQL command for idempotent, incremental file ingestion (simpler alternative to Auto Loader for batch workloads):

```sql
-- Ingest new Parquet files from S3 into a Delta table
COPY INTO bronze.events
FROM 's3://my-bucket/events/'
FILEFORMAT = PARQUET
FORMAT_OPTIONS ('mergeSchema' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true');

-- Ingest CSV with options
COPY INTO bronze.users
FROM 's3://my-bucket/users/'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true', 'delimiter' = ',')
COPY_OPTIONS ('mergeSchema' = 'true');

-- Idempotent: running again skips already-processed files
COPY INTO bronze.events
FROM 's3://my-bucket/events/'
FILEFORMAT = PARQUET;
-- ^ This is safe to run repeatedly; already-loaded files are skipped
```

**COPY INTO vs Auto Loader**:

| Feature                  | COPY INTO                      | Auto Loader                      |
|--------------------------|--------------------------------|----------------------------------|
| **API**                  | SQL command                    | Structured Streaming (Python/Scala) |
| **Trigger**              | Manual / scheduled             | Continuous streaming or triggered |
| **File discovery**       | Directory listing (every run)  | Checkpointed + file notifications |
| **Schema evolution**     | `mergeSchema` option           | Automatic schema inference + evolution |
| **Scalability**          | Millions of files (slower listing) | Billions of files (notification mode) |
| **Exactly-once**         | Yes (idempotent by file path)  | Yes (checkpoint-based)            |
| **Best for**             | Scheduled batch ingestion      | Continuous or high-volume ingestion |

**Recommendation**: Use **Auto Loader** for production streaming/incremental workloads. Use **COPY INTO** for simple batch ingestion or when SQL-only interface is preferred.

### 3.4 Kafka Integration (Structured Streaming)

Databricks provides first-class Kafka integration via Spark Structured Streaming:

```python
# Read from Kafka
kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker1:9092,broker2:9092")
    .option("subscribe", "orders,events")              # Multiple topics
    .option("startingOffsets", "earliest")              # or "latest"
    .option("kafka.security.protocol", "SASL_SSL")
    .option("kafka.sasl.mechanism", "PLAIN")
    .option("kafka.sasl.jaas.config",
            'org.apache.kafka.common.security.plain.PlainLoginModule required '
            'username="user" password="pass";')
    .option("maxOffsetsPerTrigger", 100000)             # Rate limit
    .option("minPartitions", 10)                        # Parallelism
    .load()
)

# Kafka DataFrame schema:
# key (binary), value (binary), topic (string), partition (int),
# offset (long), timestamp (timestamp), timestampType (int)

# Parse JSON values
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, DoubleType

schema = StructType() \
    .add("order_id", StringType()) \
    .add("amount", DoubleType()) \
    .add("timestamp", StringType())

parsed_df = (
    kafka_df
    .select(
        col("key").cast("string").alias("kafka_key"),
        from_json(col("value").cast("string"), schema).alias("data"),
        col("topic"),
        col("partition"),
        col("offset"),
        col("timestamp").alias("kafka_timestamp")
    )
    .select("kafka_key", "data.*", "topic", "partition", "offset", "kafka_timestamp")
)

# Write to Delta with upsert
def upsert_orders(batch_df, batch_id):
    from delta.tables import DeltaTable
    target = DeltaTable.forName(spark, "silver.orders")
    target.alias("t").merge(
        batch_df.alias("s"), "t.order_id = s.order_id"
    ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

parsed_df.writeStream \
    .foreachBatch(upsert_orders) \
    .option("checkpointLocation", "/checkpoints/orders_upsert") \
    .trigger(processingTime="30 seconds") \
    .start()
```

**Kafka + Databricks best practices**:
- Use `maxOffsetsPerTrigger` to control micro-batch size and prevent OOM
- Use `minPartitions` to increase parallelism beyond Kafka partition count
- Store Kafka credentials in **Databricks Secrets** (not in code)
- Use **Avro** or **Protobuf** for schema-aware Kafka topics with Schema Registry
- Enable `failOnDataLoss=false` in development (set to `true` in production to catch offset gaps)
- Use `Trigger.AvailableNow` for batch-style Kafka processing (process all pending, then stop)

**Schema Registry integration**:
```python
from pyspark.sql.avro.functions import from_avro
from confluent_kafka.schema_registry import SchemaRegistryClient

# Read Avro-encoded Kafka messages with Schema Registry
schema_registry_client = SchemaRegistryClient({"url": "https://schema-registry:8081"})
avro_schema = schema_registry_client.get_latest_version("orders-value").schema.schema_str

decoded_df = kafka_df.select(
    from_avro(col("value"), avro_schema).alias("data")
).select("data.*")
```

---

## 4. ML and AI

### 4.1 MLflow 3 (Model Tracking, Registry, Deployment)

**MLflow** is an open-source ML lifecycle platform, deeply integrated into Databricks. MLflow 3 (latest major version) includes:

```
+------------------------------------------------------------------+
|                        MLflow 3 on Databricks                       |
|                                                                    |
|  +------------+   +-----------+   +----------+   +-------------+  |
|  | Tracking   |   | Registry  |   | Projects |   | Deployments |  |
|  | (experiments|   | (model    |   | (reprod. |   | (serving    |  |
|  |  & runs)   |   |  versions |   |  envs)   |   |  endpoints) |  |
|  +-----+------+   +-----+-----+   +----+-----+   +------+------+  |
|        |               |              |                 |          |
|        +-------+-------+------+-------+---------+-------+          |
|                |                                                    |
|                v                                                    |
|        Unity Catalog                                                |
|        (centralized model governance)                               |
+------------------------------------------------------------------+
```

#### MLflow Tracking

```python
import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Set experiment
mlflow.set_experiment("/Users/team/churn_prediction")

# Auto-logging (captures parameters, metrics, model automatically)
mlflow.sklearn.autolog()

with mlflow.start_run(run_name="rf_baseline") as run:
    # Train model
    model = RandomForestClassifier(n_estimators=100, max_depth=10)
    model.fit(X_train, y_train)

    # Manual metric logging
    y_pred = model.predict(X_test)
    mlflow.log_metric("accuracy", accuracy_score(y_test, y_pred))
    mlflow.log_metric("f1", f1_score(y_test, y_pred))

    # Log artifacts
    mlflow.log_artifact("feature_importance.png")

    # Log model
    mlflow.sklearn.log_model(model, "model",
        registered_model_name="churn_predictor")

    print(f"Run ID: {run.info.run_id}")
```

#### MLflow Model Registry (Unity Catalog)

```python
import mlflow

# Register model in Unity Catalog
mlflow.set_registry_uri("databricks-uc")

# Register a new model version
model_uri = f"runs:/{run_id}/model"
mv = mlflow.register_model(model_uri, "production.ml.churn_predictor")

# Promote model version with aliases
from mlflow import MlflowClient
client = MlflowClient()
client.set_registered_model_alias("production.ml.churn_predictor", "champion", mv.version)

# Load model by alias for serving
model = mlflow.pyfunc.load_model("models:/production.ml.churn_predictor@champion")
predictions = model.predict(new_data)
```

**Model Registry features**:
- **Versioning**: Track multiple model versions with lineage to training data and code
- **Aliases**: Label versions (e.g., "champion", "challenger") for deployment references
- **Tags**: Metadata tags for organization and filtering
- **Approval workflows**: Transition stages with comments and approvals
- **Unity Catalog governance**: Same access controls, lineage, and audit logging as data tables

#### MLflow 3 New Features

| Feature                    | Description                                                       |
|----------------------------|-------------------------------------------------------------------|
| **LoggedModel**            | First-class model entity linking runs, artifacts, and versions    |
| **Tracing**                | Distributed tracing for ML inference pipelines and LLM chains     |
| **GenAI metrics**          | Built-in evaluation metrics for LLMs (relevance, toxicity, etc.) |
| **Deployments API**        | Unified API for deploying to Databricks Model Serving, SageMaker, etc. |
| **Prompt Engineering UI**  | Interactive prompt testing and comparison                         |

### 4.2 Mosaic AI (Agent Bricks, Vector Search, AI Gateway, Model Serving)

**Mosaic AI** (formerly MosaicML, acquired by Databricks in 2023) is the umbrella for Databricks' AI platform services:

#### 4.2.1 Mosaic AI Model Serving

Serves ML models and LLMs as REST API endpoints:

```python
# Deploy a model from Unity Catalog
import requests

# Create serving endpoint
endpoint_config = {
    "name": "churn-predictor",
    "config": {
        "served_entities": [{
            "entity_name": "production.ml.churn_predictor",
            "entity_version": "3",
            "workload_size": "Small",
            "scale_to_zero_enabled": True,
        }]
    }
}

# Query the endpoint
response = requests.post(
    "https://<workspace>.cloud.databricks.com/serving-endpoints/churn-predictor/invocations",
    headers={"Authorization": f"Bearer {token}"},
    json={"dataframe_records": [{"feature1": 1.0, "feature2": "A"}]}
)
predictions = response.json()
```

**Serving endpoint types**:

| Type                     | Use Case                                      | Scaling              |
|--------------------------|-----------------------------------------------|----------------------|
| **Custom model**         | MLflow models (sklearn, PyTorch, TensorFlow)  | Auto-scale, scale-to-zero |
| **Foundation model**     | Hosted LLMs (DBRX, Llama, Mixtral)            | Provisioned throughput |
| **External model**       | Proxy to OpenAI, Anthropic, Google, etc.       | Pass-through         |
| **Feature serving**      | Low-latency feature lookups                    | Auto-scale           |

#### 4.2.2 Vector Search

Managed vector database for similarity search, powering RAG (Retrieval-Augmented Generation) applications:

```python
from databricks.vector_search.client import VectorSearchClient

# Create a vector search index on a Delta table
vsc = VectorSearchClient()

index = vsc.create_delta_sync_index(
    endpoint_name="vector-search-endpoint",
    index_name="production.ml.document_index",
    source_table_name="production.ml.documents",
    primary_key="doc_id",
    embedding_source_column="content",           # Auto-embed using Databricks model
    embedding_model_endpoint_name="databricks-bge-large-en",
    pipeline_type="TRIGGERED"                    # Sync on trigger
)

# Query the index
results = index.similarity_search(
    query_text="How to configure Kafka?",
    columns=["doc_id", "content", "title"],
    num_results=5
)
```

**Vector Search features**:
- **Delta Sync**: Automatically sync embeddings from Delta table (incremental updates)
- **Managed embeddings**: Databricks can generate embeddings using hosted models
- **Self-managed embeddings**: Bring your own precomputed embedding vectors
- **Filtering**: Hybrid search combining vector similarity with metadata filters
- **Multi-index**: Multiple indexes on different embedding columns
- **Unity Catalog governed**: Access control on vector indexes

#### 4.2.3 AI Gateway

Centralized gateway for managing access to multiple LLM providers:

```python
# AI Gateway route configuration
{
    "name": "llm-gateway",
    "routes": [
        {
            "name": "openai-gpt4",
            "route_type": "llm/v1/chat",
            "model": {
                "name": "gpt-4",
                "provider": "openai"
            }
        },
        {
            "name": "anthropic-claude",
            "route_type": "llm/v1/chat",
            "model": {
                "name": "claude-3-opus",
                "provider": "anthropic"
            }
        },
        {
            "name": "databricks-dbrx",
            "route_type": "llm/v1/chat",
            "model": {
                "name": "databricks-dbrx-instruct",
                "provider": "databricks"
            }
        }
    ]
}
```

**AI Gateway capabilities**:
- **Unified API**: Single endpoint to access multiple LLM providers
- **Rate limiting**: Per-user and per-route rate limits
- **Cost tracking**: Token usage and cost logging per route/user
- **Guardrails**: Input/output content filtering, PII detection
- **Fallback**: Automatic failover between providers
- **Audit logging**: All LLM requests logged for compliance

#### 4.2.4 Mosaic AI Agent Framework

Framework for building compound AI systems (agents that use tools, retrieval, and reasoning):

```python
from databricks.agents import Agent, ChatAgent

# Define a RAG agent
class MyRAGAgent(ChatAgent):
    def __init__(self):
        self.vector_index = VectorSearchClient().get_index("production.ml.docs_index")
        self.llm = get_model_serving_client("databricks-dbrx-instruct")

    def chat(self, messages):
        # Retrieve relevant documents
        query = messages[-1]["content"]
        docs = self.vector_index.similarity_search(query_text=query, num_results=5)

        # Generate response with context
        context = "\n".join([d["content"] for d in docs["result"]["data_array"]])
        prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
        return self.llm.predict(prompt)

# Deploy agent as a serving endpoint
mlflow.pyfunc.log_model("agent", python_model=MyRAGAgent())
```

### 4.3 Feature Store

Databricks Feature Store (now integrated into Unity Catalog) provides centralized feature management:

```python
from databricks.feature_engineering import FeatureEngineeringClient

fe = FeatureEngineeringClient()

# Create feature table
fe.create_table(
    name="production.features.user_features",
    primary_keys=["user_id"],
    timestamp_keys=["timestamp"],
    df=user_features_df,
    description="User behavioral features for ML models"
)

# Write features
fe.write_table(
    name="production.features.user_features",
    df=new_features_df,
    mode="merge"  # upsert by primary key
)

# Create training set with point-in-time lookup
from databricks.feature_engineering import FeatureLookup

training_set = fe.create_training_set(
    df=labels_df,  # DataFrame with user_id, timestamp, label
    feature_lookups=[
        FeatureLookup(
            table_name="production.features.user_features",
            lookup_key="user_id",
            timestamp_lookup_key="timestamp"  # point-in-time correct
        )
    ],
    label="churn"
)

training_df = training_set.load_df()
```

**Feature Store capabilities**:
- **Point-in-time lookups**: Prevent data leakage by fetching features as of the label timestamp
- **Online serving**: Publish features to low-latency online store for real-time inference
- **Lineage**: Track which models use which features (Unity Catalog integration)
- **Monitoring**: Feature drift detection and data quality checks
- **Batch and streaming**: Write features from batch jobs or streaming pipelines

### 4.4 Model Serving Endpoints

Detailed model serving architecture:

```
Client Request
      |
      v
+------------------+
| Load Balancer     |
| (HTTPS endpoint) |
+--------+---------+
         |
         v
+------------------+     +------------------+
| Serving Instance  |     | Serving Instance  |
| (Container)       | ... | (Container)       |
| - MLflow model    |     | - MLflow model    |
| - Dependencies    |     | - Dependencies    |
+------------------+     +------------------+
         |
         v
+------------------+
| Model Artifacts   |
| (Unity Catalog)   |
+------------------+
```

**Endpoint configuration options**:

| Setting                  | Options                                     | Description                           |
|--------------------------|---------------------------------------------|---------------------------------------|
| **Workload size**        | Small, Medium, Large                        | CPU/memory allocation per instance    |
| **Scale-to-zero**        | Enabled / Disabled                          | Reduce cost when no traffic           |
| **Compute type**         | CPU, GPU                                    | GPU for deep learning models          |
| **Traffic routing**      | Percentage-based split between versions     | Canary/blue-green deployments         |
| **Environment**          | Custom container, requirements.txt          | Dependency management                 |

---

## 5. Data Sharing

### 5.1 Delta Sharing (Open Protocol)

**Delta Sharing** is an open protocol for secure, cross-platform data sharing, without requiring the recipient to use Databricks:

```
Data Provider (Databricks)           Data Recipient (any platform)
+---------------------------+        +---------------------------+
| Unity Catalog              |  HTTP  | Pandas, Spark, Power BI   |
| - Share object             | -----> | Tableau, Trino, Flink     |
| - Tables, views, notebooks|        | Databricks, Snowflake     |
| - Access control           |        |                           |
+---------------------------+        +---------------------------+
        |                                      |
        v                                      v
+---------------------------+        +---------------------------+
| Delta Lake on             |        | Reads Parquet directly    |
| S3 / ADLS / GCS           |        | (pre-signed URLs)        |
+---------------------------+        +---------------------------+
```

**How Delta Sharing works**:
1. **Provider** creates a **Share** in Unity Catalog containing tables/views/notebooks
2. **Provider** creates **Recipients** with authentication tokens or open sharing
3. **Recipient** uses a Delta Sharing client (Python, Spark, REST) to discover and read shared data
4. Data is accessed via **pre-signed URLs** directly from the provider's cloud storage
5. **No data copying**: Recipients read data in-place from the provider's storage

**Provider setup (Databricks)**:
```sql
-- Create a share
CREATE SHARE customer_analytics;

-- Add tables to the share
ALTER SHARE customer_analytics ADD TABLE production.sales.orders;
ALTER SHARE customer_analytics ADD TABLE production.sales.customers
  WITH HISTORY;  -- Enable time travel for recipient

-- Create a recipient
CREATE RECIPIENT acme_corp;
-- Returns an activation link with a bearer token

-- Grant share to recipient
GRANT SELECT ON SHARE customer_analytics TO RECIPIENT acme_corp;
```

**Recipient access (Python, no Databricks needed)**:
```python
import delta_sharing

# Read shared table using profile file (contains token)
profile = delta_sharing.SharingProfile.read("config.share")

# List available shares
shares = delta_sharing.list_shares(profile)

# Read a shared table as Pandas DataFrame
df = delta_sharing.load_as_pandas(
    f"{profile}#customer_analytics.production.sales.orders"
)

# Read as Spark DataFrame
spark_df = delta_sharing.load_as_spark(
    f"{profile}#customer_analytics.production.sales.orders"
)
```

### 5.2 Cross-Platform Sharing

Delta Sharing recipients can consume data using various tools:

| Platform / Tool    | Integration                                              |
|--------------------|----------------------------------------------------------|
| **Pandas**         | `delta_sharing.load_as_pandas()` -- direct, no Spark needed |
| **Apache Spark**   | `delta_sharing.load_as_spark()` -- distributed processing |
| **Power BI**       | Delta Sharing connector (certified)                       |
| **Tableau**        | Delta Sharing connector (certified)                       |
| **Databricks**     | Native Unity Catalog integration (no token needed)        |
| **Snowflake**      | Delta Sharing integration (GA)                            |
| **Google BigQuery** | Via BigLake external tables                              |
| **Trino/Presto**   | Delta Sharing connector                                   |
| **Apache Flink**   | Delta Sharing connector                                   |
| **R**              | `delta_sharing` R package                                 |
| **Rust/Go/Java**   | REST API client libraries                                |

**Delta Sharing vs traditional data sharing**:

| Approach                  | Data Copy? | Real-time? | Open? | Governance?           |
|---------------------------|------------|------------|-------|-----------------------|
| File export (CSV/Parquet) | Yes        | No         | Yes   | Manual                |
| Database replication      | Yes        | Near-RT    | No    | Source DB controls     |
| API endpoint              | No         | Yes        | Varies| API-level auth         |
| Delta Sharing             | No         | Near-RT    | Yes   | Unity Catalog (full)   |
| Snowflake Data Sharing    | No         | Near-RT    | No    | Snowflake-only         |

### 5.3 Marketplace

**Databricks Marketplace** is a platform for discovering and sharing data products, ML models, and notebooks:

**For data providers**:
- List free or commercial data products
- Share Delta tables, feature tables, ML models, notebooks
- Analytics on data product usage
- Revenue sharing for commercial listings

**For data consumers**:
- Browse and discover data products by category
- One-click installation into your Databricks workspace
- Data products appear as Unity Catalog assets (governed, audited)
- Providers include: financial data vendors, weather services, geospatial data providers, public datasets

**Marketplace categories**: Financial data, healthcare, geospatial, weather, ESG, public sector, retail, telecommunications

---

## 6. Security

### 6.1 Unity Catalog Access Control

Unity Catalog provides the primary security layer for all data assets (detailed in DATA_PLATFORM doc Section 5.2). Key security features:

- **Centralized permissions**: Single permission model across all workspaces
- **Fine-grained access**: Table, column, and row-level controls
- **Dynamic masking**: Column masks applied at query time based on user identity
- **Row filters**: Row-level security based on user attributes
- **Audit logging**: All data access events logged to `system.access.audit`

### 6.2 Credential Passthrough and Secure Access

**Methods for authenticating to external data**:

| Method                          | Description                                             | Best For                    |
|---------------------------------|---------------------------------------------------------|-----------------------------|
| **Unity Catalog credentials**   | Managed storage credentials registered in UC            | Standard external data access |
| **Instance profiles (AWS)**     | IAM role attached to cluster EC2 instances              | AWS-native access           |
| **Service principal (Azure)**   | Azure AD service principal credentials                  | Azure-native access         |
| **Credential passthrough**      | User's identity flows through to storage                | Per-user access control     |
| **Databricks Secrets**          | Encrypted key-value store for credentials               | API keys, passwords         |

**Databricks Secrets**:
```python
# Create a secret scope
# (via CLI or API, not from notebook)
# databricks secrets create-scope --scope my-scope

# Store a secret
# databricks secrets put --scope my-scope --key db-password

# Access secret in notebook
password = dbutils.secrets.get(scope="my-scope", key="db-password")
# Value is redacted in notebook output: [REDACTED]
```

**Secret scope types**:
- **Databricks-backed**: Encrypted and stored within Databricks (default)
- **Azure Key Vault-backed**: Backed by Azure Key Vault (Azure only)
- **AWS Secrets Manager-backed**: Via integration (requires setup)

### 6.3 Private Connectivity

Private networking prevents data from traversing the public internet:

| Cloud | Service                        | How It Works                                          |
|-------|--------------------------------|-------------------------------------------------------|
| AWS   | **AWS PrivateLink**            | VPC endpoint to Databricks control plane + workspace  |
| Azure | **Azure Private Link**         | Private endpoint to Databricks workspace              |
| GCP   | **Private Service Connect**    | PSC endpoint to Databricks GKE-based workspace        |

**Network architecture** (AWS example):
```
Your VPC                              Databricks Control Plane
+---------------------------+        +---------------------------+
| Private Subnet             |  AWS   | Databricks AWS Account    |
| - Cluster nodes            | <----> | - Workspace API            |
| - No public IPs            | PLink  | - Cluster management       |
| - Security groups          |        | - Unity Catalog            |
+---------------------------+        +---------------------------+
         |                                      |
         v                                      v
+---------------------------+        +---------------------------+
| Your S3 / Data Sources     |        | Databricks-managed S3     |
| (VPC endpoint / PLink)    |        | (DBR artifacts, logs)     |
+---------------------------+        +---------------------------+
```

**Network security options**:

| Feature                          | Description                                                |
|----------------------------------|------------------------------------------------------------|
| **IP access lists**              | Restrict workspace access to specific IP ranges             |
| **VPC peering / VNet injection** | Cluster nodes run in your VPC/VNet                          |
| **PrivateLink (front-end)**      | Users access workspace UI/API via private endpoint          |
| **PrivateLink (back-end)**       | Cluster-to-control-plane communication via private endpoint |
| **No public IP (NPIP)**          | Cluster nodes have no public IP addresses                   |
| **Customer-managed keys (CMK)**  | Encrypt Databricks-managed resources with your KMS key      |

### 6.4 Encryption

| Encryption Type               | Default                    | Customer-Managed Option          |
|-------------------------------|----------------------------|----------------------------------|
| **Data at rest (storage)**    | Cloud provider default encryption (SSE-S3, ADLS encryption, GCS encryption) | CMK via AWS KMS, Azure Key Vault, GCP Cloud KMS |
| **Data at rest (workspace)**  | Databricks-managed encryption | CMK for notebooks, secrets, DBFS |
| **Data in transit**           | TLS 1.2+ for all communications | N/A (always encrypted)        |
| **Cluster <-> storage**       | TLS 1.2+                   | N/A (always encrypted)           |
| **Cluster <-> control plane** | TLS 1.2+                   | N/A (always encrypted)           |
| **Inter-node communication**  | TLS 1.2+ (optional on some runtimes) | Enable via cluster config  |

**Customer-managed keys for workspace services** (enhanced security):
```
# AWS: Configure CMK for managed services
# Encrypts: notebooks, secrets, queries, query history
aws kms create-key --description "Databricks workspace CMK"

# Configure in Databricks account API
PUT /api/2.0/accounts/{account_id}/customer-managed-keys
{
  "aws_key_info": {
    "key_arn": "arn:aws:kms:us-east-1:123456789:key/abc-123",
    "key_alias": "databricks-workspace-cmk"
  },
  "use_cases": ["MANAGED_SERVICES", "STORAGE"]
}
```

### 6.5 Compliance and Certifications

| Standard / Certification | Status        |
|--------------------------|---------------|
| SOC 2 Type II            | Certified     |
| ISO 27001                | Certified     |
| ISO 27017                | Certified     |
| ISO 27018                | Certified     |
| HIPAA                    | BAA available |
| FedRAMP High (AWS)       | Authorized    |
| FedRAMP High (Azure)     | Authorized    |
| GDPR                     | Compliant     |
| PCI DSS                  | Level 1       |
| HITRUST CSF              | Certified     |
| CSA STAR                 | Certified     |

---

## 7. Developer Experience

### 7.1 Notebooks (Collaborative)

Databricks notebooks are the primary interactive development environment:

**Key features**:

| Feature                     | Description                                                     |
|-----------------------------|-----------------------------------------------------------------|
| **Multi-language**          | Python, SQL, Scala, R in the same notebook (`%python`, `%sql`)  |
| **Real-time collaboration** | Multiple users editing simultaneously (Google Docs-style)       |
| **Version history**         | Built-in version control with diff view                         |
| **Git integration**         | Sync notebooks with Git repos (GitHub, GitLab, Bitbucket, Azure DevOps) |
| **Widgets**                 | Interactive input widgets for parameterized notebooks            |
| **Dashboard views**         | Convert notebook cells into dashboards                           |
| **Variable explorer**       | Inspect DataFrame schemas, preview data                         |
| **Auto-complete**           | Code completion for PySpark, SQL, Unity Catalog objects           |
| **Magic commands**          | `%run` (include), `%sh` (shell), `%fs` (DBFS), `%md` (markdown) |
| **Visualization**           | Built-in charts (bar, line, scatter, map, pivot) from query results |

**Notebook parameterization with widgets**:
```python
# Create widgets
dbutils.widgets.text("start_date", "2026-01-01", "Start Date")
dbutils.widgets.dropdown("environment", "stg", ["dev", "stg", "prod"])

# Access widget values
start_date = dbutils.widgets.get("start_date")
env = dbutils.widgets.get("environment")

# Use in queries
df = spark.sql(f"SELECT * FROM {env}.sales.orders WHERE date >= '{start_date}'")
```

**Notebook vs IDE development**:

| Aspect            | Databricks Notebook          | External IDE (VS Code, etc.) |
|-------------------|------------------------------|------------------------------|
| Cluster access    | Direct (attached cluster)    | Via Connect / remote SSH     |
| Collaboration     | Real-time, in-browser        | Git-based, async             |
| Debugging         | Cell-by-cell, limited debugger | Full debugger, breakpoints |
| Version control   | Built-in + Git sync          | Native Git                   |
| Testing           | Manual cell execution        | pytest, unittest integration |
| Code organization | Flat cells                   | Packages, modules, imports   |
| Best for          | Exploration, prototyping     | Production code, libraries   |

### 7.2 Databricks CLI

The Databricks CLI provides command-line access to all Databricks APIs:

```bash
# Installation
pip install databricks-cli
# Or newer version:
pip install databricks-sdk

# Authentication
databricks configure --token
# Enter: Host URL + Personal Access Token

# Workspace operations
databricks workspace list /Users/team/
databricks workspace export /Users/team/notebook.py --format SOURCE
databricks workspace import /Users/team/notebook.py --language PYTHON

# Cluster operations
databricks clusters list
databricks clusters create --json '{"cluster_name": "my-cluster", ...}'
databricks clusters start --cluster-id abc-123

# Job operations
databricks jobs list
databricks jobs run-now --job-id 12345
databricks runs get --run-id 67890

# Secrets
databricks secrets create-scope --scope my-scope
databricks secrets put --scope my-scope --key api-key --string-value "sk-..."
databricks secrets list --scope my-scope

# Unity Catalog
databricks unity-catalog tables list --catalog-name prod --schema-name sales
databricks unity-catalog grants list --securable-type TABLE --full-name prod.sales.orders

# SQL
databricks sql warehouses list
databricks sql queries execute --warehouse-id xyz --statement "SELECT count(*) FROM prod.sales.orders"
```

### 7.3 VS Code Extension (Databricks Extension for VS Code)

The official VS Code extension provides a local IDE experience with Databricks cluster integration:

**Features**:

| Feature                          | Description                                                |
|----------------------------------|------------------------------------------------------------|
| **Cluster connectivity**         | Attach to remote Databricks cluster from VS Code           |
| **Notebook support**             | Open, edit, and run `.py` notebooks locally                |
| **Sync to workspace**            | Auto-sync local files to Databricks workspace              |
| **Run on cluster**               | Execute local Python files on the remote cluster           |
| **Interactive REPL**             | PySpark interactive console connected to cluster           |
| **IntelliSense**                 | Auto-complete for PySpark, dbutils, Unity Catalog          |
| **Debugging**                    | Set breakpoints and debug Spark code (single-node)         |
| **Git integration**              | Use VS Code's native Git alongside Databricks Repos        |
| **Browse workspace**             | Explore clusters, jobs, notebooks from VS Code sidebar     |

**Setup**:
1. Install "Databricks" extension from VS Code Marketplace
2. Configure workspace URL and authentication (PAT or OAuth)
3. Select a cluster to attach to
4. Write code locally, execute on remote cluster

**Databricks Connect** (alternative for IDE integration):
```python
# pip install databricks-connect

from databricks.connect import DatabricksSession

spark = DatabricksSession.builder \
    .host("https://workspace.cloud.databricks.com") \
    .token("dapiXXXXXXX") \
    .clusterId("0123-456789-abcdefgh") \
    .getOrCreate()

# Use spark session as if running on the cluster
df = spark.read.table("production.sales.orders")
df.show()
```

### 7.4 Terraform Provider

The **Databricks Terraform Provider** enables infrastructure-as-code for all Databricks resources:

```hcl
# provider configuration
terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.50.0"
    }
  }
}

provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
}

# Create a Unity Catalog
resource "databricks_catalog" "production" {
  name    = "production"
  comment = "Production data catalog"
}

resource "databricks_schema" "sales" {
  catalog_name = databricks_catalog.production.name
  name         = "sales"
  comment      = "Sales domain schema"
}

# Create a SQL Warehouse
resource "databricks_sql_endpoint" "analytics" {
  name             = "analytics-warehouse"
  cluster_size     = "Medium"
  max_num_clusters = 3
  auto_stop_mins   = 15

  tags {
    custom_tags {
      key   = "team"
      value = "analytics"
    }
  }
}

# Create a Job
resource "databricks_job" "daily_etl" {
  name = "daily_etl_pipeline"

  schedule {
    quartz_cron_expression = "0 0 2 * * ?"
    timezone_id            = "Asia/Bangkok"
  }

  task {
    task_key = "ingest"
    notebook_task {
      notebook_path = "/Repos/team/etl/01_ingest"
    }
    new_cluster {
      spark_version = "16.4.x-scala2.12"
      node_type_id  = "m5.xlarge"
      num_workers   = 4
    }
  }

  task {
    task_key = "transform"
    depends_on {
      task_key = "ingest"
    }
    notebook_task {
      notebook_path = "/Repos/team/etl/02_transform"
    }
    job_cluster_key = "shared_etl"
  }

  email_notifications {
    on_failure = ["team@company.com"]
  }
}

# Create a cluster policy
resource "databricks_cluster_policy" "cost_control" {
  name = "cost-controlled-clusters"
  definition = jsonencode({
    "node_type_id" : {
      "type" : "allowlist",
      "values" : ["m5.xlarge", "m5.2xlarge"],
      "defaultValue" : "m5.xlarge"
    },
    "autotermination_minutes" : {
      "type" : "range",
      "minValue" : 10,
      "maxValue" : 60,
      "defaultValue" : 15
    },
    "custom_tags.team" : {
      "type" : "fixed",
      "value" : var.team_name
    }
  })
}

# Create a secret scope and secret
resource "databricks_secret_scope" "app_secrets" {
  name = "app-secrets"
}

resource "databricks_secret" "db_password" {
  scope        = databricks_secret_scope.app_secrets.name
  key          = "db-password"
  string_value = var.db_password
}

# Grant permissions
resource "databricks_grants" "sales_grants" {
  schema = "${databricks_catalog.production.name}.${databricks_schema.sales.name}"

  grant {
    principal  = "analysts@company.com"
    privileges = ["SELECT", "USAGE"]
  }

  grant {
    principal  = "data_engineers@company.com"
    privileges = ["ALL_PRIVILEGES"]
  }
}
```

**Terraform provider resource coverage** (key resources):

| Resource Category      | Terraform Resources                                              |
|------------------------|------------------------------------------------------------------|
| **Workspace**          | `databricks_workspace`, `databricks_workspace_conf`              |
| **Clusters**           | `databricks_cluster`, `databricks_cluster_policy`, `databricks_instance_pool` |
| **Jobs**               | `databricks_job`, `databricks_pipeline` (DLT)                    |
| **SQL**                | `databricks_sql_endpoint`, `databricks_sql_query`, `databricks_sql_dashboard` |
| **Unity Catalog**      | `databricks_catalog`, `databricks_schema`, `databricks_table`, `databricks_grants` |
| **Security**           | `databricks_secret_scope`, `databricks_secret`, `databricks_permissions` |
| **Networking**         | `databricks_mws_networks`, `databricks_mws_private_access_settings` |
| **Storage**            | `databricks_storage_credential`, `databricks_external_location`  |
| **Model Serving**      | `databricks_model_serving`                                       |

### 7.5 Asset Bundles (CI/CD)

**Databricks Asset Bundles** (DABs) is the recommended approach for CI/CD with Databricks, replacing legacy dbx and databricks-cli workflows:

```yaml
# databricks.yml (bundle configuration)
bundle:
  name: my_etl_project

workspace:
  host: https://workspace.cloud.databricks.com

variables:
  catalog:
    default: dev

targets:
  dev:
    mode: development
    workspace:
      root_path: /Users/${workspace.current_user.userName}/.bundle/${bundle.name}/dev
    variables:
      catalog: dev

  staging:
    workspace:
      root_path: /Shared/.bundle/${bundle.name}/staging
      host: https://staging-workspace.cloud.databricks.com
    variables:
      catalog: staging

  production:
    mode: production
    workspace:
      root_path: /Shared/.bundle/${bundle.name}/production
      host: https://prod-workspace.cloud.databricks.com
    variables:
      catalog: production
    run_as:
      service_principal_name: "production-sp"

resources:
  jobs:
    daily_etl:
      name: "daily_etl_${bundle.target}"
      schedule:
        quartz_cron_expression: "0 0 2 * * ?"
        timezone_id: "Asia/Bangkok"
      tasks:
        - task_key: ingest
          notebook_task:
            notebook_path: ./src/01_ingest.py
          new_cluster:
            spark_version: "16.4.x-scala2.12"
            node_type_id: m5.xlarge
            num_workers: 4

  pipelines:
    dlt_pipeline:
      name: "dlt_pipeline_${bundle.target}"
      target: "${var.catalog}.silver"
      libraries:
        - notebook:
            path: ./src/dlt_pipeline.py
```

**CLI commands for Asset Bundles**:
```bash
# Initialize a new bundle from template
databricks bundle init

# Validate bundle configuration
databricks bundle validate

# Deploy to target environment
databricks bundle deploy --target staging

# Run a specific job
databricks bundle run daily_etl --target staging

# Destroy deployed resources
databricks bundle destroy --target dev
```

**CI/CD pipeline example** (GitHub Actions):
```yaml
# .github/workflows/deploy.yml
name: Deploy Databricks Bundle

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: databricks/setup-cli@main
      - run: databricks bundle validate --target staging

  deploy-staging:
    needs: validate
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - uses: databricks/setup-cli@main
      - run: databricks bundle deploy --target staging
        env:
          DATABRICKS_TOKEN: ${{ secrets.STAGING_TOKEN }}
          DATABRICKS_HOST: ${{ secrets.STAGING_HOST }}

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: databricks/setup-cli@main
      - run: databricks bundle deploy --target production
        env:
          DATABRICKS_TOKEN: ${{ secrets.PROD_TOKEN }}
          DATABRICKS_HOST: ${{ secrets.PROD_HOST }}
```

**Asset Bundles vs other CI/CD approaches**:

| Approach              | Status            | Description                                    |
|-----------------------|-------------------|------------------------------------------------|
| **Asset Bundles**     | Recommended (GA)  | Declarative YAML, multi-environment, built-in   |
| **Terraform**         | Supported         | Infrastructure-as-code for all Databricks resources |
| **dbx (legacy)**      | Deprecated        | Python-based project management (replaced by DABs) |
| **REST API**          | Always available  | Direct API calls for maximum flexibility        |
| **databricks-sdk**    | Supported         | Python SDK wrapping REST APIs                   |

---

## 8. Sources

### Official Databricks Documentation
- [What is Photon?](https://docs.databricks.com/aws/en/compute/photon)
- [What is Photon? (Azure)](https://learn.microsoft.com/en-us/azure/databricks/compute/photon)
- [Adaptive Query Execution](https://docs.databricks.com/en/optimizations/aqe.html)
- [Adaptive Query Execution in Structured Streaming](https://www.databricks.com/blog/adaptive-query-execution-structured-streaming)
- [Speeding Up Spark SQL with AQE](https://www.databricks.com/blog/2020/05/29/adaptive-query-execution-speeding-up-spark-sql-at-runtime.html)
- [Best Practices for Performance Efficiency](https://docs.databricks.com/aws/en/lakehouse-architecture/performance-efficiency/best-practices)
- [Structured Streaming Programming Guide](https://docs.databricks.com/aws/en/structured-streaming/)
- [Real-time Mode in Structured Streaming](https://docs.databricks.com/aws/en/structured-streaming/real-time)
- [Auto Loader](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/)
- [COPY INTO](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/)
- [Kafka Structured Streaming](https://docs.databricks.com/aws/en/connect/streaming/kafka.html)
- [Databricks Runtime Release Notes](https://docs.databricks.com/aws/en/release-notes/runtime/)
- [Databricks Runtime 16.4 LTS](https://docs.databricks.com/aws/en/release-notes/runtime/16.4lts)
- [Databricks Runtime Versions and Compatibility](https://docs.databricks.com/aws/en/release-notes/runtime/)
- [Databricks Runtime 101 (ChaosGenius)](https://www.chaosgenius.io/blog/databricks-runtime/)
- [Databricks Runtime Overview (Flexera)](https://www.flexera.com/blog/finops/databricks-runtime/)
- [Databricks Jobs / Workflows](https://docs.databricks.com/aws/en/workflows/)
- [Lakeflow Jobs](https://docs.databricks.com/aws/en/jobs/)
- [Apache Airflow Provider for Databricks](https://airflow.apache.org/docs/apache-airflow-providers-databricks/stable/index.html)
- [Databricks SQL Warehouses](https://docs.databricks.com/aws/en/compute/sql-warehouse/)
- [Lakeflow Connect](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/)
- [MLflow on Databricks](https://docs.databricks.com/aws/en/mlflow/)
- [MLflow 3.0 Release](https://mlflow.org/blog/mlflow-3-release)
- [Mosaic AI Model Serving](https://docs.databricks.com/aws/en/machine-learning/model-serving/)
- [Mosaic AI Vector Search](https://docs.databricks.com/aws/en/generative-ai/vector-search.html)
- [Mosaic AI Gateway](https://docs.databricks.com/aws/en/generative-ai/external-models/ai-gateway.html)
- [Mosaic AI Agent Framework](https://docs.databricks.com/aws/en/generative-ai/agent-framework/)
- [Feature Store / Feature Engineering](https://docs.databricks.com/aws/en/machine-learning/feature-store/)
- [Delta Sharing](https://docs.databricks.com/aws/en/data-sharing/)
- [Delta Sharing Protocol](https://github.com/delta-io/delta-sharing)
- [Databricks Marketplace](https://docs.databricks.com/aws/en/marketplace/)
- [Unity Catalog Access Control](https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/)
- [Row Filters and Column Masks](https://docs.databricks.com/aws/en/data-governance/unity-catalog/row-filters-column-masks.html)
- [Databricks Secrets](https://docs.databricks.com/aws/en/security/secrets/)
- [Private Connectivity](https://docs.databricks.com/aws/en/security/network/classic/privatelink.html)
- [Encryption at Rest](https://docs.databricks.com/aws/en/security/keys/)
- [Customer-Managed Keys](https://docs.databricks.com/aws/en/security/keys/customer-managed-keys.html)
- [Compliance Standards](https://www.databricks.com/trust/compliance)
- [Databricks Notebooks](https://docs.databricks.com/aws/en/notebooks/)
- [Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/)
- [VS Code Extension](https://docs.databricks.com/aws/en/dev-tools/vscode-ext/)
- [Databricks Connect](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/)
- [Databricks Terraform Provider](https://docs.databricks.com/aws/en/dev-tools/terraform/)
- [Databricks Asset Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/)
- [Databricks SDK for Python](https://docs.databricks.com/aws/en/dev-tools/sdk-python.html)

### Open Source Projects
- [MLflow GitHub Repository](https://github.com/mlflow/mlflow)
- [Delta Sharing GitHub Repository](https://github.com/delta-io/delta-sharing)
- [Databricks Terraform Provider GitHub](https://github.com/databricks/terraform-provider-databricks)
- [Databricks CLI GitHub](https://github.com/databricks/cli)
- [Databricks SDK for Python](https://github.com/databricks/databricks-sdk-py)
- [Unity Catalog OSS](https://github.com/unitycatalog/unitycatalog)

### Third-Party Guides and Analysis
- [Databricks Photon Performance Optimization Guide (B EYE)](https://b-eye.com/blog/databricks-photon-performance-optimization-guide/)
- [How to Optimize Databricks Performance 2025 (e6data)](https://www.e6data.com/query-and-cost-optimization-hub/databricks-performance-optimization-complete-query-tuning-guide-2025)
- [Databricks Workflows vs Apache Airflow](https://www.astronomer.io/blog/databricks-vs-apache-airflow/)
- [Databricks Auto Loader Best Practices](https://www.databricks.com/blog/2022/06/28/auto-loader-enhanced-with-schema-evolution-rescue-and-more.html)
- [MLflow 3 What's New](https://mlflow.org/blog/mlflow-3-release)
- [Databricks Asset Bundles Guide (Medium)](https://medium.com/@nishchal.siddharth/databricks-asset-bundles-a-comprehensive-guide-to-ci-cd-for-databricks-e67f5476b8ee)
- [Databricks Terraform Provider Documentation (Registry)](https://registry.terraform.io/providers/databricks/databricks/latest/docs)
- [Databricks VS Code Extension Guide](https://marketplace.visualstudio.com/items?itemName=databricks.databricks)
- [Databricks Cost Optimization Guide (CloudForecast)](https://www.cloudforecast.io/guides/databricks-pricing-costs-guide/)
- [Databricks Security Best Practices (Databricks)](https://docs.databricks.com/aws/en/security/best-practices.html)

### Academic and Technical Papers
- [Photon: A Fast Query Engine for Lakehouse Systems (SIGMOD 2022)](https://people.eecs.berkeley.edu/~matei/papers/2022/sigmod_photon.pdf)
- [Adaptive and Robust Query Execution for Lakehouses (CMU)](https://www.cs.cmu.edu/~15721-f24/papers/AQP_in_Lakehouse.pdf)
- [Delta Sharing: An Open Protocol for Cross-Platform Data Sharing (VLDB 2024)](https://www.vldb.org/pvldb/vol18/p5197-puttaswamy.pdf)
- [Structured Streaming: A Declarative API for Real-Time Applications (SIGMOD 2018)](https://cs.stanford.edu/~matei/papers/2018/sigmod_structured_streaming.pdf)
