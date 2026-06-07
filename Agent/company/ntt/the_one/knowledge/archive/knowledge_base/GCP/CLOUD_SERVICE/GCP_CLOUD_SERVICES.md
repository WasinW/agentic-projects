# GCP Cloud Services for Data Engineering

> Comprehensive knowledge base covering GCP's cloud services for data processing,
> orchestration, messaging, integration, governance, security, and CI/CD.
>
> **Version**: 2.0 | **Last Updated**: 2026-03-05 | **Maintainer**: Data Platform Team

---

## Table of Contents

1. [Data Processing](#1-data-processing)
2. [Orchestration](#2-orchestration)
3. [Messaging and Streaming](#3-messaging-and-streaming)
4. [Data Integration](#4-data-integration)
5. [Data Governance](#5-data-governance)
6. [Security and Identity](#6-security-and-identity)
7. [CI/CD and DevOps](#7-cicd-and-devops)
8. [References](#8-references)

---

## 1. Data Processing

### 1.1 Dataflow (Managed Apache Beam)

Dataflow is Google Cloud's fully managed, serverless service for stream and batch
data processing, built on top of the Apache Beam programming model.

#### Architecture

```
+-------------------------------------------------------------------+
|                        Dataflow Service                           |
|                                                                   |
|  +--------------------+    +----------------------------------+  |
|  |   Beam SDK          |    |   Dataflow Runner               |  |
|  |   (Python/Java/Go)  |    |                                |  |
|  |                    |    |   - Worker Management           |  |
|  |   - Pipeline Graph |    |   - Autoscaling                |  |
|  |   - Transforms     |--->|   - Shuffle Service            |  |
|  |   - IOs            |    |   - Streaming Engine           |  |
|  |   - Windowing      |    |   - Fault Tolerance            |  |
|  +--------------------+    +----------------------------------+  |
|                                                                   |
|  Sources: Kafka, Pub/Sub, GCS, BQ, JDBC, Iceberg                |
|  Sinks:   BQ, GCS, Iceberg, Pub/Sub, Bigtable, Spanner          |
+-------------------------------------------------------------------+
```

**Core concepts**:

- **Pipeline**: The top-level container for a data processing job
- **PCollection**: A distributed dataset (bounded for batch, unbounded for streaming)
- **PTransform**: A data processing operation (Map, GroupByKey, CoGroupByKey, etc.)
- **IO Connectors**: Source/sink connectors for reading/writing external systems
- **Windowing**: Time-based grouping for streaming data (fixed, sliding, session)
- **Watermarks**: Track event-time completeness in streaming pipelines
- **Triggers**: Control when windowed results are emitted

**Programming model**: Apache Beam provides a unified API for both batch and streaming:

```python
import apache_beam as beam

with beam.Pipeline(options=pipeline_options) as p:
    (
        p
        | "ReadFromKafka" >> ReadFromKafka(consumer_config=kafka_config, topics=["events"])
        | "ParseJSON" >> beam.Map(parse_json)
        | "FilterValid" >> beam.Filter(is_valid)
        | "WindowInto" >> beam.WindowInto(beam.window.FixedWindows(60))
        | "WriteToIceberg" >> managed.Write(iceberg_config)
    )
```

#### Dataflow Pricing

| Resource | Batch | Streaming |
|----------|-------|-----------|
| vCPU | ~$0.056/vCPU-hr | ~$0.069/vCPU-hr |
| Memory | ~$0.003557/GB-hr | ~$0.003557/GB-hr |
| Streaming Engine | N/A | ~$0.089/CU-hr |
| Dataflow Shuffle | ~$0.011/GB | N/A |
| Persistent Disk (HDD) | ~$0.000054/GB-hr | ~$0.000054/GB-hr |
| Persistent Disk (SSD) | ~$0.000298/GB-hr | ~$0.000298/GB-hr |
| **FlexRS discount** | **~40% off vCPU and memory** | N/A |

**Committed Use Discounts**: 20% (1-year), 40% (3-year)

#### Batch vs Streaming

| Aspect | Batch | Streaming |
|--------|-------|-----------|
| Data source | Bounded (files, tables) | Unbounded (Kafka, Pub/Sub) |
| Execution | Finite; pipeline completes | Continuous; runs indefinitely |
| Autoscaling | Standard or FlexRS | Dynamic, throughput-based |
| Shuffle | Dataflow Shuffle service | Streaming Engine |
| Cost | Lower (FlexRS available) | Higher (always-on) |
| Latency | Minutes to hours | Seconds to minutes |
| Windowing | Not typically needed | Essential for grouping |
| Exactly-once | Built-in | Built-in (or at-least-once mode) |
| Use case | ETL, backfill, scheduled jobs | Real-time ingestion, CDC |

#### FlexRS (Flexible Resource Scheduling)

FlexRS reduces batch Dataflow costs by up to 40% by using a combination of
preemptible VMs and flexible scheduling:

- **How it works**: Dataflow delays job start by up to 6 hours to find cheaper resources
- **Best for**: Batch jobs that are not time-sensitive (overnight ETL, backfills)
- **Not for**: Streaming pipelines or time-critical batch jobs
- **Savings**: ~40% on vCPU and memory costs

```python
# Enable FlexRS in pipeline options
pipeline_options = PipelineOptions([
    "--runner=DataflowRunner",
    "--flexrs_goal=COST_OPTIMIZED",  # or SPEED_OPTIMIZED
    "--region=asia-southeast1",
])
```

#### Worker Configuration

**Default worker configurations**:

| Config | Batch | Streaming |
|--------|-------|-----------|
| vCPUs per worker | 1 | 4 |
| Memory per worker | 3.75 GB | 15 GB |
| Disk (with Shuffle/SE) | 25 GB | 30 GB |
| Disk (without Shuffle/SE) | 250 GB | 400 GB |
| Max workers (default) | 1,000 | 100 |

**Tuning parameters**:

```python
pipeline_options = PipelineOptions([
    "--runner=DataflowRunner",
    "--machine_type=n1-standard-4",        # Worker machine type
    "--num_workers=2",                      # Initial workers
    "--max_num_workers=20",                 # Max autoscale
    "--autoscaling_algorithm=THROUGHPUT_BASED",
    "--disk_size_gb=50",                    # Worker disk
    "--worker_disk_type=compute.googleapis.com/projects//zones//diskTypes/pd-ssd",
    "--use_public_ips=false",               # Private networking
    "--network=vpc-name",
    "--subnetwork=regions/region/subnetworks/subnet",
    "--service_account_email=sa@project.iam.gserviceaccount.com",
    "--staging_location=gs://bucket/staging",
    "--temp_location=gs://bucket/temp",
])
```

#### Key Features (2025-2026)

- **Managed I/O connectors**: Simplified source/sink configuration via YAML/config
- **IcebergIO managed.Write**: Direct Iceberg writes via BLMS REST Catalog
- **Parallel pipeline updates**: Update streaming jobs without downtime
- **Resource-based billing**: Streaming Engine billed per Compute Unit (CU)
- **At-least-once streaming mode**: Lower cost, trades off exactly-once guarantee
- **Committed Use Discounts**: 20% (1-year), 40% (3-year) commitment savings
- **Flex Templates**: Containerized pipeline deployment via Docker + container spec
- **Prime workers**: Enhanced worker VMs with better networking and storage

#### Flex Templates

Flex Templates are the recommended way to deploy Dataflow pipelines. They package
the pipeline code in a Docker container and deploy via a container spec.

```
+------------------+    +------------------+    +------------------+
| Pipeline Code    |    | Docker Image     |    | Container Spec   |
| (Python/Java)    |--->| (in GAR)         |--->| (in GCS)         |
|                  |    |                  |    |                  |
| beam pipeline    |    | FROM python:3.11 |    | {                |
| + dependencies   |    | COPY . /app      |    |   "image": "...",|
|                  |    | ENTRYPOINT ...   |    |   "sdkInfo": {}  |
+------------------+    +------------------+    | }                |
                                                +------------------+
                                                       |
                                                       v
                                                +------------------+
                                                | Dataflow Job     |
                                                | (workers)        |
                                                +------------------+
```

**Deployment flow** (used in the loyalty data platform):
1. GitLab CI builds Docker image and pushes to GAR
2. `prepare_dataflow_spec.sh` generates the container spec JSON
3. `deploy_dataflow.sh` launches/updates the Dataflow job
4. For streaming: cancel existing job, then launch new one
5. For batch: launch as new job (scheduled via Cloud Scheduler)

### 1.2 Dataproc (Managed Spark/Hadoop)

Dataproc is Google Cloud's managed service for running Apache Spark, Apache Hadoop,
Apache Flink, and other open-source frameworks.

#### Deployment Options

| Option | Management | Pricing | Idle Cost | Best For |
|--------|-----------|---------|-----------|----------|
| **On Compute Engine** | Managed cluster | $0.010/vCPU-hr + VM costs | Yes (cluster stays running) | Full control, persistent clusters |
| **Serverless** | No cluster to manage | DCU-based (per compute unit) | No (pay only when running) | Intermittent/bursty workloads |
| **On GKE** | Kubernetes-based | $0.010/vCPU-hr + GKE costs | Shared with GKE cluster | Multi-tenant, container-native |

#### Supported Engines

- **Apache Spark**: Batch and streaming (Structured Streaming)
- **Apache Hive**: SQL-based data warehousing on Hadoop
- **Apache Pig**: Data flow scripting (legacy)
- **Presto/Trino**: Interactive SQL queries
- **Apache Flink**: Stream processing
- **Jupyter/Zeppelin**: Interactive notebooks

#### Dataproc Pricing

**On Compute Engine**:
- Dataproc premium: $0.010/vCPU/hour (on top of VM costs)
- VM costs: Standard Compute Engine pricing
- Persistent disk: Standard GCE disk pricing
- Preemptible workers: ~80% discount on VM costs (but can be reclaimed)

**Serverless (Spark)**:
- Dataproc Compute Units (DCU): ~$0.06/DCU-hr
- Shuffle storage: ~$0.0035/GB-hr
- No idle costs -- pay only for job execution time

**Key features**:
- **Autoscaling**: Automatic cluster scaling based on YARN metrics
- **Initialization actions**: Custom scripts to install software at cluster creation
- **Component Gateway**: Web UIs (Spark UI, YARN, etc.) via secure proxy
- **Optional components**: Hive Metastore, Ranger, Jupyter, Zeppelin
- **Spot VMs**: Use spot/preemptible VMs for secondary workers (80% cheaper)
- **Image versioning**: Choose Spark/Hadoop versions via image version
- **Personal cluster auth**: Per-user Kerberos authentication
- **GPU support**: Attach NVIDIA GPUs for Spark ML workloads

### 1.3 Dataflow vs Dataproc Comparison

| Aspect | Dataflow | Dataproc |
|--------|----------|----------|
| **Engine** | Apache Beam | Apache Spark/Hadoop/Flink |
| **Management** | Fully serverless | Managed cluster (or Serverless Spark) |
| **Streaming** | Native, excellent windowing and state | Spark Structured Streaming |
| **Batch** | Good | Excellent (mature Spark ecosystem) |
| **Autoscaling** | Automatic, dynamic, fine-grained | Configurable, YARN-based, less dynamic |
| **Pricing** | Per resource consumed (no idle cost) | Per VM hour + Dataproc premium |
| **Idle costs** | None (serverless) | Yes (cluster mode), No (serverless) |
| **ML/AI** | Limited (no GPU support) | Spark MLlib, GPU support |
| **Migration** | Requires Beam SDK (new pipelines) | Lift-and-shift Spark/Hadoop code |
| **Interactive** | No (pipeline-only) | Notebooks, Spark Shell, Presto |
| **Iceberg** | IcebergIO (managed.Write) | Native Spark Iceberg connector |
| **Kafka** | KafkaIO (Beam connector) | Spark Kafka connector |
| **SQL** | Beam SQL (limited) | Spark SQL (full, mature) |
| **Ecosystem** | Beam IOs, limited 3rd-party | Full Spark/Hadoop ecosystem |
| **Exactly-once** | Built-in (streaming) | Requires checkpointing setup |
| **Deployment** | Flex Template (Docker) | Submit job to cluster |

#### When to Choose Dataflow

- New pipelines from scratch (no existing Spark code)
- Unified batch + streaming with the same codebase
- Minimal operational overhead (fully serverless)
- Complex windowing and event-time processing
- Kafka/Pub/Sub to BigQuery/Iceberg patterns
- CDC with Storage Write API integration
- You want zero idle costs

#### When to Choose Dataproc

- Existing Spark/Hadoop workloads (lift-and-shift)
- Interactive exploration (notebooks, Spark Shell)
- GPU-accelerated ML training (Spark MLlib)
- Complex Spark SQL queries and transformations
- Need the full Spark ecosystem (Delta Lake, MLlib, GraphX)
- Short-lived batch jobs with Serverless Spark (no cluster management)
- Multi-framework needs (Spark + Hive + Presto on same cluster)

#### Decision Matrix

| Scenario | Recommendation |
|----------|---------------|
| Real-time Kafka to BigQuery | Dataflow |
| Nightly batch ETL (new code) | Dataflow (with FlexRS) |
| Nightly batch ETL (existing Spark) | Dataproc (Serverless Spark) |
| Ad-hoc data exploration | Dataproc (with notebooks) |
| ML training with GPUs | Dataproc |
| Streaming with complex windowing | Dataflow |
| Iceberg writes from streaming | Dataflow (managed.Write) |
| Iceberg table maintenance | Dataproc (Spark) or PyIceberg |
| Mixed workloads (ETL + ML + SQL) | Dataproc |
| Event-driven microservices | Dataflow |

---

## 2. Orchestration

### 2.1 Cloud Composer (Managed Airflow)

Cloud Composer is Google Cloud's fully managed workflow orchestration service built
on Apache Airflow.

#### Versions

| Version | Status | Airflow Version | Pricing Model | Notes |
|---------|--------|-----------------|---------------|-------|
| Composer 1 | **End of Life: Sep 15, 2026** | Airflow 1.x/2.x | Per environment resources | Migrate to Composer 2/3 |
| Composer 2 | Active (>2.1.0 unaffected) | Airflow 2.x | Per environment + compute | Most widely deployed |
| Composer 3 | Latest | Airflow 2.x / 3.1 | DCU-based (consumption) | Recommended for new projects |

#### Architecture

```
+-----------------------------------------------------------+
|                   Cloud Composer                          |
|                                                           |
|  +------------------+   +-----------------------------+  |
|  | Airflow Webserver |   | Airflow Scheduler          |  |
|  | (UI + REST API)  |   | - DAG parsing              |  |
|  |                  |   | - Task scheduling          |  |
|  |                  |   | - Dependency resolution    |  |
|  +------------------+   +-----------------------------+  |
|                                                           |
|  +------------------+   +-----------------------------+  |
|  | Cloud SQL        |   | GKE Cluster (Workers)      |  |
|  | (Metadata DB)    |   | - Task execution           |  |
|  |                  |   | - Autoscaling (Composer 2+) |  |
|  +------------------+   +-----------------------------+  |
|                                                           |
|  +------------------+                                     |
|  | GCS (DAG bucket) |                                     |
|  | - DAG files      |                                     |
|  | - Plugins        |                                     |
|  | - Data           |                                     |
|  +------------------+                                     |
+-----------------------------------------------------------+
```

#### Pricing

**Composer 3 (DCU-based)**:
- Consumption-based: Data Compute Units (DCUs)
- Infrastructure SKU: Small, Medium, Large tiers (covers Cloud SQL, task queue, proxies)
- Pay for what you use -- no idle environment costs for task execution

**Composer 2**:
- Environment infrastructure: Per-hour charges for webserver, scheduler, database
- Worker compute: Per vCPU-hr and GB-hr
- DAG storage: Standard GCS pricing
- Typical cost: $300-$1,500/month for a small-medium environment

#### Key Features (2025-2026)

- **Apache Airflow 3.1 support**: Cloud Composer is the first hyperscaler to support
  Airflow 3.1 (announced 2025)
- **DAG versioning**: Auditable rollbacks for DAG changes
- **Scheduler-managed backfills**: Built-in backfill support without manual intervention
- **Task Execution API and SDK**: Programmatic task management
- **React-based modern UI**: Improved dashboard experience
- **Private IP**: Environments with no public IP (VPC-native)
- **CICD integration**: GitLab/GitHub sync for DAG deployment
- **Workload Identity**: Secure GKE-based authentication

#### Airflow 3.1 Highlights

- **Trigger-based scheduling**: More flexible than traditional cron
- **Dataset-aware scheduling**: DAGs triggered by upstream dataset changes
- **Improved task execution**: Better parallelism and resource management
- **Enhanced security**: Fine-grained RBAC, audit logging
- **Modern UI**: React-based (replacing Flask-based UI)

#### Example DAG for Data Pipeline

```python
from airflow import DAG
from airflow.providers.google.cloud.operators.dataflow import (
    DataflowStartFlexTemplateOperator,
)
from airflow.providers.google.cloud.operators.bigquery import BigQueryCheckOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "data-platform",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2026, 1, 1),
}

with DAG(
    dag_id="loyalty_tiers_collector",
    schedule_interval="0 18 * * *",  # 1AM BKK = 6PM UTC
    default_args=default_args,
    catchup=False,
    tags=["loyalty", "batch"],
) as dag:

    run_tiers_collector = DataflowStartFlexTemplateOperator(
        task_id="run_tiers_collector",
        project_id="project-id",
        location="asia-southeast1",
        body={
            "launchParameter": {
                "containerSpecGcsPath": "gs://bucket/templates/tiers-collector.json",
                "jobName": "tiers-collector",
                "environment": {
                    "maxWorkers": 10,
                    "tempLocation": "gs://bucket/temp",
                },
                "parameters": {
                    "config_file": "gs://bucket/config/prod.yaml",
                },
            }
        },
        wait_until_finished=True,
    )

    check_bq_output = BigQueryCheckOperator(
        task_id="check_bq_output",
        sql="""
            SELECT COUNT(*) > 0
            FROM `project.loyalty_refined.tiers`
            WHERE ingested_date = CURRENT_DATE()
        """,
        use_legacy_sql=False,
    )

    run_tiers_collector >> check_bq_output
```

### 2.2 Cloud Scheduler

Cloud Scheduler is a fully managed enterprise-grade cron job scheduler for GCP.

#### Overview

- **Purpose**: Trigger HTTP endpoints, Pub/Sub topics, or App Engine handlers on a schedule
- **Pricing**: $0.10/job/month (first 3 jobs free per project)
- **Reliability**: 99.99% SLA
- **Time zones**: Full IANA timezone support (e.g., `Asia/Bangkok`)

#### Use Cases in the Data Platform

```
Cloud Scheduler (1AM BKK daily)
    |
    +---> Pub/Sub topic "trigger-tiers-collector"
    |         |
    |         +---> Cloud Function / Composer DAG / direct Dataflow launch
    |
    +---> Pub/Sub topic "trigger-members-tiers-history"
              |
              +---> Cloud Function / Composer DAG / direct Dataflow launch
```

**Configuration example**:

```bash
# Create a Cloud Scheduler job that triggers a Pub/Sub topic daily at 1AM BKK
gcloud scheduler jobs create pubsub tiers-collector-daily \
    --schedule="0 1 * * *" \
    --time-zone="Asia/Bangkok" \
    --topic="trigger-tiers-collector" \
    --message-body='{"job": "tiers-collector", "env": "prod"}' \
    --location="asia-southeast1"
```

**Terraform example**:

```hcl
resource "google_cloud_scheduler_job" "tiers_collector" {
  name             = "tiers-collector-daily"
  description      = "Trigger tiers collector daily at 1AM BKK"
  schedule         = "0 1 * * *"
  time_zone        = "Asia/Bangkok"
  attempt_deadline = "320s"

  pubsub_target {
    topic_name = google_pubsub_topic.trigger_tiers.id
    data       = base64encode("{\"job\": \"tiers-collector\", \"env\": \"prod\"}")
  }
}
```

#### Limitations

- Maximum 500 jobs per project (can request increase)
- Minimum schedule interval: 1 minute
- Maximum message body: 256 KB (Pub/Sub target)
- No job chaining or dependencies (use Composer for complex workflows)
- No built-in retry with backoff (retries are simple count-based)

---

## 3. Messaging and Streaming

### 3.1 Pub/Sub

Pub/Sub is Google Cloud's fully managed, serverless messaging service for
event-driven architectures and streaming analytics.

#### Architecture

```
+-----------+     +----------+     +-------------+
| Publisher  |---->| Pub/Sub  |---->| Subscriber  |
|           |     |  Topic   |     |             |
| (App,     |     |          |     | (Dataflow,  |
|  Dataflow,|     | Messages |     |  Cloud Run, |
|  Cloud    |     | stored   |     |  GKE, etc.) |
|  Function)|     | durably  |     |             |
+-----------+     +----------+     +-------------+
```

#### Key Features

- **At-least-once delivery**: Every message delivered to every subscription at least once
- **Ordering keys**: Messages with the same ordering key delivered in order
- **Exactly-once processing**: With Dataflow connector (deduplication at consumer)
- **Dead letter topics**: Automatic routing of undeliverable messages
- **Message filtering**: Server-side attribute-based filtering
- **Schema validation**: Enforce Avro/Protobuf/JSON schemas on publish
- **Retention**: Up to 31 days message retention (default 7 days)
- **Seek**: Replay messages from a timestamp or snapshot
- **User-Defined Functions (UDFs)**: Transform messages in-flight
- **Low-latency watermarks**: For streaming analytics

#### Pricing

| Component | Price | Free Tier |
|-----------|-------|-----------|
| Message delivery | $40/TiB | First 10 GiB/month |
| Retained acknowledged messages | $0.27/GiB/month | -- |
| Snapshot message backlog | $0.27/GiB/month | -- |
| Seek (topic backlog) | $0.0035/GiB read | -- |

#### Pub/Sub with Dataflow

```python
import apache_beam as beam
from apache_beam.io import ReadFromPubSub, WriteToBigQuery

with beam.Pipeline(options=pipeline_options) as p:
    (
        p
        | "ReadPubSub" >> ReadFromPubSub(
            subscription="projects/proj/subscriptions/events-sub"
        )
        | "ParseJSON" >> beam.Map(parse_json_message)
        | "WriteBQ" >> WriteToBigQuery(
            table="project:dataset.table",
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            method=beam.io.WriteToBigQuery.Method.STORAGE_WRITE_API,
        )
    )
```

#### Pub/Sub Lite (Deprecated)

- **Status**: End of Life -- March 18, 2026
- Budget-friendly alternative with zonal (not regional) availability
- Lower cost but lower durability guarantees
- **Recommendation**: Migrate to standard Pub/Sub before EOL

### 3.2 Managed Service for Apache Kafka (MSKA)

Google Cloud's fully managed Apache Kafka service, providing the full Kafka
experience without managing infrastructure.

#### Key Features

- **Fully managed Kafka clusters**: No broker management
- **Kafka Connect**: Managed connectors for data integration
- **VPC Service Controls**: Network isolation and security
- **Mutual TLS (mTLS)**: End-to-end encryption
- **Kafka ACLs**: Fine-grained topic-level authorization
- **Exactly-once semantics**: Via Kafka's idempotent producers and transactions
- **Schema Registry**: Avro, Protobuf, JSON Schema support
- **Kafka Streams**: Stream processing library
- **Offset-based replay**: Precise message replay by offset
- **Cross-region replication**: Via MirrorMaker 2

#### Kafka with Dataflow (KafkaIO)

```python
from apache_beam.io.kafka import ReadFromKafka

# Read from Kafka using Beam KafkaIO
messages = (
    pipeline
    | "ReadKafka" >> ReadFromKafka(
        consumer_config={
            "bootstrap.servers": kafka_bootstrap_servers,
            "group.id": "loyalty-members-collector",
            "auto.offset.reset": "earliest",
            "security.protocol": "SASL_SSL",
            "sasl.mechanism": "PLAIN",
            "sasl.jaas.config": jaas_config,
        },
        topics=["member-events"],
        with_metadata=True,
    )
)
```

#### Pricing

- Per broker-hour (varies by broker type and size)
- Per partition (additional charge above base partitions)
- Per GB storage (retained data)
- Networking: Standard GCP egress rates
- Kafka Connect: Per connector-hour

### 3.3 Pub/Sub vs Kafka Comparison

| Feature | Pub/Sub | Kafka (MSKA / Confluent) |
|---------|---------|--------------------------|
| **Management** | Fully serverless | Managed cluster |
| **Ordering** | Per ordering key | Per partition |
| **Delivery** | At-least-once | At-least-once (configurable exactly-once) |
| **Replay** | Seek to timestamp | Offset-based replay (precise) |
| **Retention** | Up to 31 days | Configurable (unlimited with tiered storage) |
| **Schema** | Pub/Sub schemas (Avro/Protobuf/JSON) | Schema Registry (Avro/Protobuf/JSON) |
| **Multi-cloud** | GCP only | Any cloud (Confluent, MSK, MSKA) |
| **Pricing** | Per message volume ($40/TiB) | Per broker/partition/storage |
| **Latency** | ~100ms | ~10ms |
| **Throughput** | Very high (auto-scaled) | Very high (depends on broker count) |
| **Ecosystem** | GCP native integrations | Kafka Connect, Streams, ksqlDB |
| **Consumer groups** | Subscription model | Consumer group model |
| **Partitioning** | Automatic (serverless) | Manual partition management |
| **Dead letters** | Built-in DLT | Requires custom implementation |
| **Exactly-once** | With Dataflow connector | Native (idempotent producer + transactions) |
| **Best for** | GCP-native, event-driven | Multi-cloud, complex streaming, low-latency |

#### When to Choose Pub/Sub

- Purely GCP-native architecture
- Event-driven microservices with simple pub/sub patterns
- You want zero operational overhead (serverless)
- Message volume is variable (pay-per-message)
- Built-in GCP integrations (Dataflow, Cloud Functions, Cloud Run)

#### When to Choose Kafka

- Multi-cloud or hybrid-cloud architecture
- Need low-latency messaging (~10ms vs ~100ms)
- Complex stream processing (Kafka Streams, ksqlDB)
- Need precise offset-based replay
- Existing Kafka expertise and tooling
- Need Kafka Connect ecosystem (hundreds of connectors)
- The loyalty data platform uses Kafka (AWS MSK) as the message source

---

## 4. Data Integration

### 4.1 Dataform (SQL-Based Transformations)

Dataform is GCP's native dbt alternative, fully integrated into BigQuery as
**BigQuery Dataform**. It provides SQL-first data transformation with dependency
management, testing, and version control.

#### Architecture

```
+----------------------------------------------------------+
|                    BigQuery Dataform                      |
|                                                          |
|  +-------------------+    +---------------------------+  |
|  | Repository (Git)  |    | Compilation               |  |
|  |                   |    |                           |  |
|  | - definitions/    |--->| - Resolve refs            |  |
|  |   (SQLX files)    |    | - Apply JS templating     |  |
|  | - includes/       |    | - Build dependency graph  |  |
|  |   (JS functions)  |    | - Generate SQL            |  |
|  | - dataform.json   |    |                           |  |
|  +-------------------+    +---------------------------+  |
|                                     |                    |
|                                     v                    |
|                           +------------------+           |
|                           | Execution        |           |
|                           |                  |           |
|                           | - Run SQL in BQ  |           |
|                           | - Run assertions |           |
|                           | - Track lineage  |           |
|                           +------------------+           |
+----------------------------------------------------------+
```

#### Key Characteristics

- **SQL-first**: Write transformations in SQL with JavaScript templating
- **Fully managed**: No infrastructure to run -- executes directly in BigQuery
- **No licensing cost**: Pay only for BigQuery compute (no Dataform license fee)
- **Git integration**: Built-in repository management or connect to GitHub/GitLab
- **Dependency management**: `${ref("schema", "table")}` syntax for automatic DAG
- **Data testing**: Assertions for data quality validation
- **Incremental processing**: Support for incremental table builds
- **Documentation**: Inline documentation with schema descriptions
- **Environment management**: Development, staging, production environments

#### SQLX File Example

```sql
-- definitions/loyalty/member_tier_summary.sqlx
config {
    type: "table",
    schema: "loyalty_public",
    description: "Summary of member tiers with latest status",
    assertions: {
        nonNull: ["member_id", "tier_code"],
        uniqueKey: ["member_id"]
    },
    bigquery: {
        partitionBy: "DATE(last_updated)",
        clusterBy: ["program_code"]
    }
}

SELECT
    mt.member_id,
    mt.tier_code,
    mt.program_code,
    mt.start_date,
    mt.end_date,
    CURRENT_TIMESTAMP() AS last_updated,
    COUNT(te.event_id) AS total_tier_changes
FROM ${ref("loyalty_refined", "member_tier")} mt
LEFT JOIN ${ref("loyalty_refined", "tier_events_upgraded")} te
    ON mt.member_id = te.member_id
GROUP BY 1, 2, 3, 4, 5
```

#### Scheduling Options

- **Cloud Composer** (Airflow): Most flexible, recommended for complex workflows
- **BigQuery Studio data pipelines**: Built-in scheduling (simpler)
- **Google Cloud Workflows**: Serverless orchestration
- **Third-party orchestrators**: Dagster, Prefect, etc.

### 4.2 Dataform vs dbt Comparison

| Aspect | Dataform | dbt |
|--------|----------|-----|
| **Templating** | JavaScript + SQL (SQLX) | Jinja + SQL |
| **Platform** | BigQuery only | Multi-warehouse (BQ, Snowflake, Redshift, Databricks) |
| **Cost** | Free (pay BQ compute only) | Open-source free; dbt Cloud from $100+/month |
| **Management** | Fully managed (GCP service) | Self-hosted or dbt Cloud |
| **Lock-in** | GCP/BigQuery only | Portable across warehouses |
| **Community** | Smaller but growing | Very large, mature ecosystem |
| **Packages/Hub** | Limited (JS-based) | dbt Hub (1000+ packages) |
| **Incremental** | Supported | Supported (more mature) |
| **Testing** | Assertions (built-in) | Tests + data tests (extensive) |
| **Documentation** | Built-in (BQ-integrated) | Built-in (dbt docs site) |
| **CI/CD** | Git-native | Git-native + dbt Cloud CI |
| **IDE** | BigQuery Studio (web) | dbt Cloud IDE or VS Code |
| **Freshness checks** | Limited | Source freshness monitoring |
| **Snapshots (SCD)** | Not natively supported | Built-in SCD Type 2 |
| **Macros** | JavaScript functions | Jinja macros |
| **Semantic layer** | No | dbt Semantic Layer (MetricFlow) |
| **Learning curve** | Lower (simpler SQLX) | Higher (Jinja templating) |

#### When to Choose Dataform

- Fully committed to GCP/BigQuery
- Want zero additional licensing cost
- Simpler transformation needs
- Team prefers JavaScript over Jinja
- Want native BigQuery console integration

#### When to Choose dbt

- Multi-cloud or multi-warehouse strategy
- Need dbt Hub packages (pre-built models)
- Complex transformation logic (Jinja macros)
- Need SCD Type 2 snapshots
- Want portable skills across employers
- Large team with dbt expertise

### 4.3 Data Transfer Service

BigQuery Data Transfer Service automates data movement into BigQuery from various
sources.

#### Supported Sources

| Source Type | Sources |
|------------|---------|
| SaaS | Google Ads, Campaign Manager, YouTube, Google Play |
| Cloud storage | Amazon S3 to BigQuery |
| Cross-region | BigQuery dataset replication |
| Databases | Teradata, Amazon Redshift (migration) |

#### Key Features

- Scheduled transfers (hourly, daily, custom)
- Automatic schema detection
- Incremental data loading
- Backfill support for historical data
- Email notifications on failure

#### Pricing

- Free for most SaaS transfers (pay only for BQ storage/queries)
- S3 transfers: Standard data transfer pricing
- Cross-region: Standard cross-region pricing

### 4.4 Application Integration

Google Cloud Application Integration provides a no-code/low-code integration
platform for connecting enterprise systems.

- **Cloud Tasks**: Managed task queues for asynchronous processing
- **Cloud Workflows**: Serverless workflow orchestration (YAML-based)
- **Eventarc**: Event routing from 130+ Google Cloud sources
- **API Gateway**: Managed API proxying and management
- **Apigee**: Full API management platform (enterprise)

---

## 5. Data Governance

### 5.1 Dataplex Universal Catalog

Dataplex Universal Catalog is GCP's unified data governance and management platform.
It replaces the deprecated Data Catalog (discontinued January 30, 2026).

#### Core Capabilities

```
+--------------------------------------------------------------+
|                 Dataplex Universal Catalog                    |
|                                                              |
|  +------------------+  +-------------------+                 |
|  | Auto-discovery   |  | Data Quality      |                |
|  | - BigQuery       |  | - Column profiling |                |
|  | - Cloud SQL      |  | - Quality rules   |                |
|  | - Spanner        |  | - Scheduled checks |                |
|  | - Vertex AI      |  +-------------------+                |
|  | - Pub/Sub        |                                        |
|  | - Dataform       |  +-------------------+                |
|  | - Dataproc       |  | Data Lineage      |                |
|  |   Metastore      |  | - Source tracking  |                |
|  +------------------+  | - Impact analysis  |                |
|                        +-------------------+                |
|  +------------------+                                        |
|  | Semantic Search  |  +-------------------+                |
|  | - AI-powered     |  | Data Products     |                |
|  | - Natural lang.  |  | - Curated packages |                |
|  +------------------+  | - Documentation   |                |
|                        | - Access policies  |                |
|                        +-------------------+                |
+--------------------------------------------------------------+
```

#### Feature Details

**Metadata Cataloging**:
- Auto-discovers metadata from BigQuery, Cloud SQL, Spanner, Vertex AI, Pub/Sub,
  Dataform, and Dataproc Metastore
- Business and technical metadata management
- Custom metadata via aspects (replacement for deprecated Tag Templates)
- Schema documentation and descriptions

**Data Quality**:
- Column-level profiling (statistics, distributions, patterns)
- Rule-based data quality checks (null percentage, uniqueness, range)
- Scheduled quality scans with alerting
- Quality scores and dashboards

**Data Lineage**:
- Automatic lineage tracking for BigQuery, Dataflow, Dataproc, Dataform
- Column-level lineage (not just table-level)
- Impact analysis: see downstream effects of schema changes
- Visual lineage explorer in BigQuery console

**Data Profiling**:
- Automatic statistics for each column (min, max, mean, null count, distinct count)
- Pattern detection for string columns
- Distribution analysis
- Outlier detection

**Semantic Search**:
- AI-powered search across all metadata
- Natural language queries ("find all tables with member_id")
- Relevance ranking based on usage patterns

**Data Products** (2025-2026):
- Package data assets as self-service products
- Include documentation, quality metrics, SLAs
- Publish to Analytics Hub for sharing
- Access request workflows

#### Important Timeline

| Event | Date | Action Required |
|-------|------|-----------------|
| Data Catalog deprecated | January 30, 2026 | Migrate to Dataplex Universal Catalog |
| Tag Templates deprecated | February 2026 | Migrate to Dataplex aspects |
| BigLake support in Dataplex | 2025 | Direct integration available |
| Data Products GA | 2025 | New feature |

#### Dataplex Terraform Example

```hcl
resource "google_dataplex_lake" "loyalty_lake" {
  location = "asia-southeast1"
  name     = "loyalty-data-lake"
  project  = var.project_id

  labels = {
    team = "data-platform"
    env  = "prod"
  }
}

resource "google_dataplex_zone" "source_zone" {
  discovery_spec {
    enabled = true
  }

  lake     = google_dataplex_lake.loyalty_lake.name
  location = "asia-southeast1"
  name     = "source-zone"
  project  = var.project_id
  type     = "RAW"

  resource_spec {
    location_type = "SINGLE_REGION"
  }
}
```

### 5.2 Analytics Hub

Analytics Hub is GCP's data exchange platform for secure data sharing between
organizations.

#### Key Features

- **Publisher-subscriber model**: Data providers publish; consumers subscribe
- **Linked datasets**: Subscribers get read access without data copying
- **No data movement**: Data stays in the publisher's project
- **Fine-grained access**: Row/column-level security on shared data
- **Monetization**: Sell data products via Google Cloud Marketplace
- **Cross-organization sharing**: Share across GCP organizations
- **Audit trail**: Track who accesses shared data

#### Use Cases

- Share curated datasets with partner organizations
- Create internal data marketplaces
- Monetize anonymized/aggregated datasets
- Enable self-service data discovery for analysts

#### Pricing

- Free to publish listings
- Subscribers pay for their own BigQuery queries on linked datasets
- No data transfer charges (data is not copied)

---

## 6. Security and Identity

### 6.1 Secret Manager

Secret Manager is GCP's service for storing, managing, and accessing sensitive
configuration data (API keys, passwords, certificates, connection strings).

#### Key Features

- **Centralized storage**: Single location for all secrets
- **Versioning**: Multiple versions of each secret, with rollback capability
- **Automatic rotation**: Integration with Cloud Functions for rotation
- **IAM-based access**: Fine-grained access control per secret
- **Audit logging**: Cloud Audit Logs for every access
- **Regional and global replication**: Choose replication policy
- **Encryption**: Automatic encryption at rest (Google-managed or CMEK)

#### Usage in the Data Platform

```python
from google.cloud import secretmanager

def get_secret(project_id: str, secret_id: str, version: str = "latest") -> str:
    """Retrieve a secret from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Example: Get Kafka credentials
kafka_creds = get_secret("project-id", "kafkaCredentials")
api_creds = get_secret("project-id", "apiCredentials")
```

**Secret naming convention** (loyalty data platform):
- `kafkaCredentials` -- Kafka bootstrap servers, SASL credentials
- `apiCredentials` -- The1 API keys and endpoints

#### Pricing

| Component | Price | Free Tier |
|-----------|-------|-----------|
| Active secret versions | $0.06/version/month | 6 versions |
| Access operations | $0.03 per 10,000 | 10,000 ops/month |
| Rotation notifications | Free (via Pub/Sub) | -- |

#### Terraform Example

```hcl
resource "google_secret_manager_secret" "kafka_creds" {
  secret_id = "kafkaCredentials"
  project   = var.project_id

  replication {
    user_managed {
      replicas {
        location = "asia-southeast1"
      }
    }
  }
}

resource "google_secret_manager_secret_iam_member" "sa_access" {
  secret_id = google_secret_manager_secret.kafka_creds.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.dataflow_sa_email}"
}
```

### 6.2 Service Accounts and IAM

#### Service Account Strategy

The data platform uses per-collector service accounts following the principle of
least privilege:

```
+----------------------------------------------------------+
|              IAM Architecture                            |
|                                                          |
|  members-collector-sa@project.iam.gserviceaccount.com    |
|    +-- roles/bigquery.dataEditor (refined dataset)       |
|    +-- roles/biglake.admin (BLMS catalog)                |
|    +-- roles/storage.objectAdmin (source GCS bucket)     |
|    +-- roles/secretmanager.secretAccessor (secrets)      |
|    +-- roles/dataflow.worker                             |
|                                                          |
|  tiers-collector-sa@project.iam.gserviceaccount.com      |
|    +-- roles/bigquery.dataEditor (refined dataset)       |
|    +-- roles/biglake.admin (BLMS catalog)                |
|    +-- roles/storage.objectAdmin (source GCS bucket)     |
|    +-- roles/dataflow.worker                             |
|                                                          |
|  m-t-h-collector-sa@project.iam.gserviceaccount.com      |
|    +-- roles/bigquery.dataEditor (refined dataset)       |
|    +-- roles/biglake.admin (BLMS catalog)                |
|    +-- roles/storage.objectAdmin (source GCS bucket)     |
|    +-- roles/dataflow.worker                             |
+----------------------------------------------------------+
```

#### Key IAM Concepts

| Concept | Description |
|---------|-------------|
| **Principal** | Who (user, service account, group) |
| **Role** | What permissions (predefined or custom) |
| **Resource** | Where the role is granted (project, dataset, bucket) |
| **Policy** | Binding of principal + role on a resource |
| **Condition** | Optional condition (time-based, attribute-based) |

#### Common Roles for Data Engineering

| Role | Description | Typical Usage |
|------|-------------|---------------|
| `roles/bigquery.dataEditor` | Read/write tables in a dataset | Dataflow writing to BQ |
| `roles/bigquery.dataViewer` | Read tables in a dataset | Dataform reading refined |
| `roles/bigquery.jobUser` | Create and run BQ jobs | Service accounts running queries |
| `roles/biglake.admin` | Full BLMS catalog access | Dataflow writing to Iceberg |
| `roles/biglake.viewer` | Read BLMS catalog metadata | Query engines reading Iceberg |
| `roles/storage.objectAdmin` | Full GCS object access | Dataflow writing Parquet files |
| `roles/storage.objectViewer` | Read GCS objects | Reading Iceberg data files |
| `roles/dataflow.worker` | Dataflow worker permissions | Service accounts for workers |
| `roles/dataflow.admin` | Create/manage Dataflow jobs | CI/CD deploying pipelines |
| `roles/secretmanager.secretAccessor` | Read secrets | Dataflow reading credentials |
| `roles/composer.admin` | Manage Composer environments | DevOps managing Airflow |

#### Best Practices

1. **One SA per collector**: Isolate permissions per pipeline
2. **Dataset-level grants**: Grant BQ access at dataset level, not project
3. **Bucket-level grants**: Grant GCS access per bucket, not project-wide
4. **No editor/owner roles**: Use specific roles instead of broad `roles/editor`
5. **Service account impersonation**: Use short-lived tokens instead of keys
6. **Workload Identity**: For GKE-based workloads (Composer workers)
7. **Audit logging**: Enable data access audit logs for sensitive datasets
8. **Terraform**: Manage all IAM bindings as code

### 6.3 VPC Service Controls

VPC Service Controls (VPC-SC) create security perimeters around GCP resources to
prevent data exfiltration and unauthorized access.

#### Key Concepts

```
+----------------------------------------------------------+
|                VPC Service Perimeter                      |
|                                                          |
|  +------------+  +------------+  +-----------------+     |
|  | BigQuery   |  | GCS        |  | Secret Manager  |     |
|  | datasets   |  | buckets    |  | secrets         |     |
|  +------------+  +------------+  +-----------------+     |
|                                                          |
|  +------------+  +------------+                          |
|  | Dataflow   |  | Pub/Sub    |                          |
|  | jobs       |  | topics     |                          |
|  +------------+  +------------+                          |
|                                                          |
|  Access only from:                                       |
|  - Authorized VPC networks                               |
|  - Authorized service accounts                           |
|  - Authorized IP ranges                                  |
+----------------------------------------------------------+
```

#### Features

- **Access levels**: Define who can cross the perimeter (IP, device, identity)
- **Ingress/Egress rules**: Fine-grained rules for specific APIs and projects
- **Dry run mode**: Test perimeter before enforcement
- **Bridge perimeters**: Allow communication between perimeters
- **Supported services**: BigQuery, GCS, Pub/Sub, Dataflow, Secret Manager,
  Artifact Registry, Cloud SQL, Spanner, and 50+ more

#### Use Cases in Data Platform

- Prevent BigQuery data from being exported to unauthorized projects
- Restrict GCS bucket access to specific VPC networks
- Ensure Dataflow jobs can only access resources within the perimeter
- Block Secret Manager access from outside corporate network

---

## 7. CI/CD and DevOps

### 7.1 Artifact Registry (GAR)

Artifact Registry is GCP's managed service for storing, managing, and securing
build artifacts and dependencies.

#### Supported Formats

| Format | Use Case |
|--------|----------|
| Docker | Container images for Dataflow Flex Templates, Cloud Run |
| Maven | Java libraries and Beam pipeline JARs |
| npm | JavaScript/TypeScript packages |
| Python (PyPI) | Python packages and Beam pipeline wheels |
| Go | Go modules |
| Apt/Yum | Linux packages |
| Helm | Kubernetes Helm charts |

#### Key Features

- **Vulnerability scanning**: Automatic CVE scanning with Container Analysis
- **IAM-based access**: Fine-grained repository-level permissions
- **Regional and multi-regional**: Choose repository location
- **Cleanup policies**: Automatic deletion of old/unused images
- **Remote repositories**: Proxy and cache upstream registries (Docker Hub, PyPI)
- **Virtual repositories**: Aggregate multiple repositories under one endpoint
- **Immutable tags**: Prevent overwriting of tagged images

#### Usage in the Data Platform

Each collector has its own GAR repository:

```
GAR Repositories:
  asia-southeast1-docker.pkg.dev/project/
    +-- members-collector/     # Docker images for members Dataflow job
    +-- tiers-collector/       # Docker images for tiers Dataflow job
    +-- m-t-h-collector/       # Docker images for m-t-h Dataflow job
    +-- purchases-collector/   # Docker images for purchases Dataflow job
```

**Image naming convention**:
```
asia-southeast1-docker.pkg.dev/{project}/{collector}/{image}:{tag}
```

**Destinations in GitLab CI** (per collector):
- STG: `asia-southeast1-docker.pkg.dev/stg-project/collector/image:$CI_COMMIT_SHORT_SHA`
- PROD: `asia-southeast1-docker.pkg.dev/prod-project/collector/image:$CI_COMMIT_SHORT_SHA`

#### Pricing

| Component | Price | Free Tier |
|-----------|-------|-----------|
| Storage | $0.10/GB/month | 500 MB |
| Vulnerability scanning | $0.26/image scanned | 50 images/month |
| Egress | Standard GCP networking | -- |

#### Terraform Example

```hcl
resource "google_artifact_registry_repository" "members_collector" {
  location      = "asia-southeast1"
  repository_id = "members-collector"
  format        = "DOCKER"
  project       = var.project_id

  cleanup_policies {
    id     = "keep-recent"
    action = "KEEP"
    most_recent_versions {
      keep_count = 10
    }
  }

  cleanup_policies {
    id     = "delete-old"
    action = "DELETE"
    condition {
      older_than = "2592000s"  # 30 days
    }
  }
}
```

### 7.2 Cloud Build

Cloud Build is GCP's serverless CI/CD platform for building, testing, and deploying
applications.

#### Key Features

- **Serverless**: No build servers to manage
- **Build triggers**: Automatically build on Git push/PR
- **Custom build steps**: Use any Docker image as a build step
- **Parallel steps**: Run independent steps concurrently
- **Build pools**: Private worker pools for VPC-connected builds
- **Approval gates**: Manual approval before deployment (Enterprise)
- **Build artifacts**: Automatic push to GAR

#### Build Configuration

```yaml
# cloudbuild.yaml
steps:
  # Step 1: Run tests
  - name: 'python:3.11'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install -r requirements.txt
        pytest tests/ -v

  # Step 2: Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO}/${_IMAGE}:${SHORT_SHA}'
      - '.'

  # Step 3: Push to GAR
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO}/${_IMAGE}:${SHORT_SHA}'

images:
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO}/${_IMAGE}:${SHORT_SHA}'

options:
  machineType: 'E2_HIGHCPU_8'

substitutions:
  _REGION: 'asia-southeast1'
  _REPO: 'members-collector'
  _IMAGE: 'dataflow'
```

#### Pricing

| Component | Price | Free Tier |
|-----------|-------|-----------|
| Build minutes (default pool) | $0.003/build-minute | 120 min/day |
| Build minutes (E2 medium) | $0.006/build-minute | -- |
| Build minutes (E2 high CPU) | $0.012/build-minute | -- |
| Private pool | Per vCPU-hr | -- |

### 7.3 Integration with GitLab CI

The loyalty data platform uses GitLab CI as the primary CI/CD system, integrating
with GCP services for deployment.

#### Typical Pipeline Architecture

```
GitLab CI Pipeline
    |
    +-- build (all environments)
    |   +-- Unit tests (pytest)
    |   +-- Linting (ruff, mypy)
    |   +-- Security scans (sonar, gitleaks, trivy)
    |   +-- Docker build + push to GAR
    |
    +-- deploy-tables:stg
    |   +-- Create/alter BQ tables (deploy.py)
    |
    +-- deploy:stg
    |   +-- Prepare Dataflow config (prepare_dataflow_config.sh)
    |   +-- Prepare Dataflow spec (prepare_dataflow_spec.sh)
    |   +-- Deploy Dataflow job (deploy_dataflow.sh)
    |
    +-- deploy-tables:prod
    |   +-- Create/alter BQ tables (deploy.py)
    |
    +-- deploy:prod
        +-- Cancel existing job (streaming) / N/A (batch)
        +-- Prepare Dataflow config
        +-- Prepare Dataflow spec
        +-- Deploy Dataflow job
```

#### GitLab CI Configuration Example

```yaml
# .gitlab-ci.yml (simplified)
stages:
  - build
  - deploy-tables
  - deploy

variables:
  REGION: asia-southeast1
  PYTHON_VERSION: "3.11"

# Shared extends for security scanning
.common-sonar-scan:
  # ... sonar scanning configuration ...

.common-gitleaks:
  # ... gitleaks scanning configuration ...

.common-trivy:
  # ... trivy vulnerability scanning ...

# Build stage: Docker image with 4 destinations (STG + PROD)
create-image:
  stage: build
  script:
    - docker build -t ${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA} .
    - docker push ${STG_REGISTRY}/${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA}
    # PROD destinations (commented during testing):
    # - docker push ${PROD_REGISTRY}/${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA}

# Deploy tables: Create/alter BigQuery tables
deploy-tables:stg:
  stage: deploy-tables
  script:
    - python deploy.py --env stg --config config/stg.yaml
  environment: stg

deploy-tables:prod:
  stage: deploy-tables
  script:
    - python deploy.py --env prod --config config/prod.yaml
  environment: prod

# Deploy: Launch Dataflow jobs
deploy:stg:
  stage: deploy
  script:
    - ./scripts/prepare_dataflow_config.sh stg
    - ./scripts/prepare_dataflow_spec.sh stg
    - ./scripts/deploy_dataflow.sh stg
  environment: stg

deploy:prod:
  stage: deploy
  script:
    # For streaming (members-collector): cancel existing job first
    # For batch (tiers, m-t-h): just deploy
    - ./scripts/prepare_dataflow_config.sh prod
    - ./scripts/prepare_dataflow_spec.sh prod
    - ./scripts/deploy_dataflow.sh prod
  environment: prod
```

#### GitLab CI to GCP Authentication

```yaml
# Authentication via Workload Identity Federation (recommended)
.gcp-auth:
  id_tokens:
    GCP_ID_TOKEN:
      aud: https://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}
  before_script:
    - gcloud auth login --cred-file=${GOOGLE_APPLICATION_CREDENTIALS}
    - gcloud config set project ${PROJECT_ID}

# Or via Service Account Key (legacy, less secure)
.gcp-auth-key:
  before_script:
    - echo ${GCP_SA_KEY} | base64 -d > /tmp/sa-key.json
    - gcloud auth activate-service-account --key-file=/tmp/sa-key.json
    - gcloud config set project ${PROJECT_ID}
```

#### Key Scripts in the Data Platform

| Script | Purpose |
|--------|---------|
| `scripts/prepare_dataflow_config.sh` | Generate pipeline configuration from templates |
| `scripts/prepare_dataflow_spec.sh` | Generate Flex Template container spec JSON |
| `scripts/deploy_dataflow.sh` | Launch or update Dataflow job via gcloud |
| `deploy.py` | Create/alter BigQuery tables (native BQ only) |

#### Deployment Differences by Collector Type

| Aspect | Streaming (members-collector) | Batch (tiers, m-t-h) |
|--------|-------------------------------|----------------------|
| Job lifecycle | Long-running, cancel + relaunch | Short-lived, launch per run |
| Deploy strategy | Cancel existing, then deploy new | Deploy as new job |
| Trigger | Continuous (Kafka consumer) | Cloud Scheduler (1AM BKK) |
| Autoscaling | Dynamic (throughput-based) | Standard (batch autoscaling) |
| FlexRS | Not applicable | Applicable (40% savings) |
| Idle cost | Yes (always-on workers) | No (runs only during execution) |
| Update method | Cancel + new job | N/A (each run is independent) |
| `process_date` | Not needed | Yesterday's date (m-t-h) |

#### Container Spec Template

```json
{
  "image": "asia-southeast1-docker.pkg.dev/project/collector/image:tag",
  "sdkInfo": {
    "language": "PYTHON"
  },
  "defaultEnvironment": {
    "additionalExperiments": [],
    "additionalUserLabels": {
      "team": "data-platform",
      "collector": "members-collector"
    }
  },
  "metadata": {
    "name": "members-collector",
    "description": "Loyalty members collector pipeline"
  }
}
```

---

## 8. References

### Official Google Cloud Documentation

#### Data Processing

- [Dataflow Documentation](https://cloud.google.com/dataflow/docs)
- [Dataflow Pricing](https://cloud.google.com/dataflow/pricing)
- [Dataflow Release Notes](https://cloud.google.com/dataflow/docs/release-notes)
- [Dataflow Flex Templates](https://cloud.google.com/dataflow/docs/guides/templates/using-flex-templates)
- [Dataflow FlexRS](https://cloud.google.com/dataflow/docs/guides/flexrs)
- [Dataflow Streaming Engine](https://cloud.google.com/dataflow/docs/guides/deploying-a-pipeline#streaming-engine)
- [Dataflow Worker Configuration](https://cloud.google.com/dataflow/docs/guides/deploying-a-pipeline)
- [Dataproc Documentation](https://cloud.google.com/dataproc/docs)
- [Dataproc Pricing](https://cloud.google.com/dataproc/pricing)
- [Dataproc Serverless](https://cloud.google.com/dataproc-serverless/docs)

#### Orchestration

- [Cloud Composer Documentation](https://cloud.google.com/composer/docs)
- [Cloud Composer Pricing](https://cloud.google.com/composer/pricing)
- [Cloud Composer + Airflow 3.1 Announcement](https://cloud.google.com/blog/products/data-analytics/cloud-composer-supports-apache-airflow-31)
- [Cloud Composer Versions](https://cloud.google.com/composer/docs/concepts/versioning/composer-versions)
- [Cloud Composer 1 End of Life](https://cloud.google.com/composer/docs/composer-1/end-of-life)
- [Cloud Scheduler Documentation](https://cloud.google.com/scheduler/docs)
- [Cloud Scheduler Pricing](https://cloud.google.com/scheduler/pricing)

#### Messaging

- [Pub/Sub Documentation](https://cloud.google.com/pubsub/docs)
- [Pub/Sub Pricing](https://cloud.google.com/pubsub/pricing)
- [Pub/Sub + Dataflow Integration](https://cloud.google.com/dataflow/docs/concepts/streaming-with-cloud-pubsub)
- [Pub/Sub Lite End of Life](https://cloud.google.com/pubsub/docs/choosing-pubsub-or-lite)
- [Managed Kafka on GCP](https://cloud.google.com/managed-kafka/docs)
- [Migrate Kafka to Pub/Sub](https://cloud.google.com/pubsub/docs/migrating-from-kafka-to-pubsub)

#### Data Integration

- [Dataform Documentation](https://cloud.google.com/dataform/docs)
- [Dataform SQLX Reference](https://cloud.google.com/dataform/docs/reference/dataform-core-reference)
- [Dataform vs dbt Comparison](https://cloud.google.com/dataform/docs/compare-dataform-dbt)
- [Data Transfer Service](https://cloud.google.com/bigquery/docs/dts-introduction)

#### Data Governance

- [Dataplex Universal Catalog](https://cloud.google.com/dataplex/docs/introduction)
- [Dataplex Data Quality](https://cloud.google.com/dataplex/docs/data-quality-overview)
- [Dataplex Data Lineage](https://cloud.google.com/dataplex/docs/data-lineage)
- [Dataplex Data Products](https://cloud.google.com/blog/products/data-analytics/introducing-data-products-in-dataplex-universal-catalog)
- [Data Catalog Deprecation](https://cloud.google.com/data-catalog/docs/release-notes)
- [Analytics Hub](https://cloud.google.com/analytics-hub/docs)

#### Security

- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Secret Manager Pricing](https://cloud.google.com/secret-manager/pricing)
- [IAM Documentation](https://cloud.google.com/iam/docs)
- [Service Accounts Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)
- [VPC Service Controls](https://cloud.google.com/vpc-service-controls/docs)
- [Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)

#### CI/CD and DevOps

- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [Artifact Registry Pricing](https://cloud.google.com/artifact-registry/pricing)
- [Artifact Registry Cleanup Policies](https://cloud.google.com/artifact-registry/docs/repositories/cleanup-policy)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Cloud Build Pricing](https://cloud.google.com/build/pricing)

### Apache Beam

- [Apache Beam Documentation](https://beam.apache.org/documentation/)
- [Beam Python SDK](https://beam.apache.org/documentation/sdks/python/)
- [Beam KafkaIO](https://beam.apache.org/documentation/io/built-in/kafka/)
- [Beam BigQueryIO](https://beam.apache.org/documentation/io/built-in/google-bigquery/)
- [Beam IcebergIO (managed.Write)](https://beam.apache.org/documentation/io/built-in/iceberg/)
- [Beam Windowing](https://beam.apache.org/documentation/programming-guide/#windowing)
- [Beam Triggers](https://beam.apache.org/documentation/programming-guide/#triggers)

### Third-Party Analysis

- [Dataflow vs Dataproc (OneUptime)](https://oneuptime.com/blog/post/2026-02-17-how-to-choose-between-dataflow-and-dataproc-for-batch-data-processing-on-gcp/view)
- [Dataflow vs Dataproc (Medium)](https://medium.com/google-cloud/dataflow-vs-dataproc-1b722bfda9)
- [Dataflow Cost Optimization (DoiT)](https://www.doit.com/blog/dataflow-cost-optimization-for-streaming-and-batch-workloads/)
- [Dataflow Cost Guide (Sedai)](https://sedai.io/blog/google-dataflow-costs-pricing-guide)
- [Cloud Composer 3 Guide (CloudZone)](https://www.cloudzone.io/blog/google-cloud-composer-guide)
- [dbt vs Dataform (The Data Letter)](https://www.thedataletter.com/p/dbt-vs-dataform-which-should-you)
- [dbt vs Dataform (Devoteam)](https://www.devoteam.com/expert-view/dbt-vs-dataform-picking-the-right-data-transformation-tool/)
- [Dataform vs dbt (Valiotti)](https://valiotti.com/blog/dataform-vs-dbt-review/)
- [Dataform vs dbt (Masthead)](https://mastheadata.com/blog/dbt-vs-dataform)
- [2025 Streaming Momentum (Google Cloud Blog)](https://cloud.google.com/blog/products/data-analytics/2025-data-integration-and-streaming-momentum)
- [Dataplex Guide (Medium)](https://medium.com/@anurag.vinit/data-governance-with-gcp-dataplex-universal-catalog-e1e06a1245ac)

### GitLab CI

- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [GitLab CI with GCP](https://docs.gitlab.com/ee/ci/cloud_deployment/google_cloud.html)
- [GitLab Workload Identity Federation](https://docs.gitlab.com/ee/ci/cloud_services/google_cloud/)

---

> **Document Version**: 2.0 | **Last Updated**: 2026-03-05
