# OpenLineage — Deep Dive

> Open standard for data lineage events ใน Spark, Beam, dbt, Airflow
> วิธีให้ pipeline emit lineage โดยอัตโนมัติ

---

## 1. ทำไมต้องมี Open Standard

### ปัญหา: ก่อน OpenLineage

แต่ละ tool emit lineage รูปแบบของตัวเอง:
- Spark → Atlas format
- Airflow → custom XCom
- dbt → manifest.json
- Tools incompatible

ผลลัพธ์: catalog ใหม่ต้อง integrate กับทุก tool

### OpenLineage Solution

> "Standard event format ที่ทุก tool emit ได้ และ catalog ทุกตัว consume ได้"

```
Spark → OpenLineage event → DataHub
Airflow → OpenLineage event → Marquez
dbt → OpenLineage event → OpenMetadata
       (same format)        (same format)
```

LF AI & Data Foundation graduated project (2024+)

---

## 2. Core Concepts

### 3 Entities

```
RUN     = a single execution (run_id = UUID)
JOB     = the recipe being executed (namespace + name)
DATASET = data being read or written (namespace + name)
```

### Event Lifecycle

```
START   → run begins
RUNNING → optional progress updates
COMPLETE → success
FAIL    → error
ABORT   → cancelled
```

### Event Structure

```json
{
  "eventType": "COMPLETE",
  "eventTime": "2026-05-04T10:00:00Z",
  
  "run": {
    "runId": "550e8400-e29b-41d4-a716-446655440000",
    "facets": {...}
  },
  
  "job": {
    "namespace": "production",
    "name": "customer_etl",
    "facets": {...}
  },
  
  "inputs": [
    {
      "namespace": "bigquery",
      "name": "raw.bronze.customers",
      "facets": {...}
    }
  ],
  
  "outputs": [
    {
      "namespace": "bigquery",
      "name": "warehouse.silver.customers",
      "facets": {...}
    }
  ]
}
```

### Namespace Convention

```
bigquery               → BigQuery datasets
postgres://hostname    → Postgres
s3://bucket            → S3 paths
kafka://broker         → Kafka topics
```

---

## 3. Facets — The Power of OpenLineage

### What are Facets

Facets = **modular metadata** attached to Run/Job/Dataset

Each facet = self-contained piece of metadata
- Can omit if not available
- Can extend with custom facets

### Standard Run Facets

```json
"run": {
  "runId": "uuid",
  "facets": {
    "parent": {
      "run": {"runId": "parent-uuid"},
      "job": {"namespace": "...", "name": "parent_job"}
    },
    "errorMessage": {
      "message": "Connection timeout",
      "stackTrace": "..."
    },
    "nominalTime": {
      "nominalStartTime": "2026-05-04T00:00:00Z",
      "nominalEndTime": "2026-05-05T00:00:00Z"
    }
  }
}
```

### Standard Job Facets

```json
"job": {
  "namespace": "...",
  "name": "...",
  "facets": {
    "documentation": {
      "description": "Daily customer ETL"
    },
    "ownership": {
      "owners": [
        {"name": "data-team", "type": "TEAM"}
      ]
    },
    "sourceCode": {
      "language": "python",
      "source": "..."
    },
    "sourceCodeLocation": {
      "type": "git",
      "url": "https://github.com/...",
      "version": "abc123"
    },
    "sql": {
      "query": "SELECT * FROM orders WHERE ..."
    }
  }
}
```

### Standard Dataset Facets

```json
"inputs": [{
  "namespace": "bigquery",
  "name": "raw.orders",
  "facets": {
    "schema": {
      "fields": [
        {"name": "order_id", "type": "string"},
        {"name": "amount", "type": "decimal"}
      ]
    },
    "dataSource": {
      "name": "bigquery",
      "uri": "bigquery://my-project"
    },
    "version": {
      "datasetVersion": "snapshot-1234567890"
    },
    "lifecycleStateChange": {
      "lifecycleStateChange": "CREATE"
    }
  }
}]
```

### Column-Level Lineage Facet (most important!)

```json
"outputs": [{
  "namespace": "bigquery",
  "name": "warehouse.silver.customers",
  "facets": {
    "columnLineage": {
      "fields": {
        "customer_id": {
          "inputFields": [
            {
              "namespace": "bigquery",
              "name": "raw.bronze.customers",
              "field": "user_id"
            }
          ],
          "transformationDescription": "direct_copy",
          "transformationType": "IDENTITY"
        },
        "email_hash": {
          "inputFields": [
            {
              "namespace": "bigquery",
              "name": "raw.bronze.customers",
              "field": "email"
            }
          ],
          "transformationDescription": "sha256(email)",
          "transformationType": "MASKED"
        },
        "lifetime_value": {
          "inputFields": [
            {"namespace": "bigquery", "name": "raw.orders", "field": "amount"}
          ],
          "transformationDescription": "SUM(amount) GROUP BY user_id",
          "transformationType": "AGGREGATION"
        }
      }
    }
  }
}]
```

### Custom Facets

```json
"facets": {
  "customCompliance_my_org": {
    "_producer": "https://github.com/my-org/dq-tracker",
    "_schemaURL": "https://my-org.com/schemas/compliance.json",
    "pii_check_passed": true,
    "compliance_team": "security",
    "audit_id": "AUD-2026-001"
  }
}
```

Naming convention: `customX_<orgName>` to avoid collision

---

## 4. Spark Integration (Auto-Lineage)

### Setup

```python
spark = SparkSession.builder \
    .config("spark.jars.packages",
            "io.openlineage:openlineage-spark_2.12:1.30.0") \
    .config("spark.extraListeners",
            "io.openlineage.spark.agent.OpenLineageSparkListener") \
    .config("spark.openlineage.transport.type", "http") \
    .config("spark.openlineage.transport.url",
            "http://marquez:5000/api/v1/lineage") \
    .config("spark.openlineage.namespace", "spark-prod") \
    .config("spark.openlineage.parentJobName", "customer_etl") \
    .config("spark.openlineage.parentRunId",
            "550e8400-e29b-41d4-a716-446655440000") \
    .getOrCreate()
```

### What you get for free

Spark events emitted automatically for:
- DataFrame reads/writes (Iceberg, Parquet, Delta)
- SQL queries
- Streaming queries

```python
# This automatically emits OpenLineage events
df = spark.read.table("raw.bronze.customers")
df_clean = df.filter("status = 'active'")
df_clean.write.saveAsTable("warehouse.silver.customers")

# Events: START → COMPLETE
# Inputs: raw.bronze.customers
# Outputs: warehouse.silver.customers
# Column lineage: which output cols come from which input cols
```

### Column-Level Lineage

Spark integration extracts column lineage from logical plan:

```python
# Spark sees:
spark.sql("""
    CREATE TABLE warehouse.silver.customers AS
    SELECT
        user_id AS customer_id,
        sha2(email, 256) AS email_hash,
        AVG(amount) OVER (PARTITION BY user_id) AS avg_amount
    FROM raw.bronze.customers
    JOIN raw.orders USING (user_id)
""")

# OpenLineage facet auto-generated:
# customer_id ← raw.bronze.customers.user_id
# email_hash ← sha256(raw.bronze.customers.email)
# avg_amount ← AVG over raw.orders.amount partitioned by user_id
```

---

## 5. Airflow Integration

### Setup

```bash
pip install openlineage-airflow
```

### Configuration

```bash
# .env or airflow.cfg
export OPENLINEAGE_URL=http://marquez:5000
export OPENLINEAGE_NAMESPACE=airflow-prod
```

### Auto-instrumented Operators

These operators emit lineage automatically:
- `BigQueryOperator`
- `PostgresOperator`
- `SparkSubmitOperator` (if Spark integration enabled)
- `BashOperator` (if SQL detected)

### Manual Lineage in Custom Operator

```python
from openlineage.airflow import OpenLineageAdapter, Dataset

class CustomETLOperator(BaseOperator):
    def execute(self, context):
        # Your ETL logic
        ...
        
        # Manually emit lineage
        adapter = OpenLineageAdapter()
        adapter.emit_lineage_event(
            run_id=context["run_id"],
            inputs=[Dataset(namespace="postgres://db", name="public.orders")],
            outputs=[Dataset(namespace="s3://bucket", name="silver/orders.parquet")]
        )
```

### Parent-Child Run Linking

```
Airflow DAG:
  └─ run_id = airflow_run_xyz
       │
       ├─ Task 1 (Spark job)
       │   └─ child_run_id = spark_run_abc (parent: airflow_run_xyz)
       │
       └─ Task 2 (dbt)
           └─ child_run_id = dbt_run_def (parent: airflow_run_xyz)
```

Marquez UI shows full DAG hierarchy

---

## 6. dbt Integration

### Setup

```bash
pip install openlineage-dbt
```

### Run dbt with OpenLineage

```bash
# Wrapper command
dbt-ol run

# Or set env
OPENLINEAGE_URL=http://marquez:5000 dbt run
```

### What you get

For each model run:
```
START event:
  job: project_name.model_name
  inputs: refs/sources from manifest.json

COMPLETE event:
  outputs: this model
  facets:
    - SQL query
    - column lineage (extracted from compiled SQL)
```

### dbt-OpenLineage Architecture

```
dbt run
   ↓
manifest.json (parsed model dependencies)
   ↓
run_results.json (status, timing)
   ↓
openlineage-dbt extracts → emit events
```

---

## 7. Custom Pipeline Integration

### Python Client

```python
from openlineage.client import OpenLineageClient
from openlineage.client.event_v2 import (
    RunEvent, RunState, Run, Job, Dataset
)
from openlineage.client.facet_v2 import (
    sql_job, schema_dataset, column_lineage_dataset
)
from datetime import datetime
import uuid

client = OpenLineageClient.from_environment()

run_id = str(uuid.uuid4())

# START event
client.emit(RunEvent(
    eventType=RunState.START,
    eventTime=datetime.utcnow().isoformat() + "Z",
    run=Run(runId=run_id),
    job=Job(namespace="my-platform", name="custom_pipeline"),
    inputs=[
        Dataset(namespace="bigquery", name="raw.events"),
    ],
    outputs=[],
    producer="my-platform/v1.0"
))

try:
    # Your pipeline logic
    process_data()
    
    # COMPLETE event with rich facets
    client.emit(RunEvent(
        eventType=RunState.COMPLETE,
        eventTime=datetime.utcnow().isoformat() + "Z",
        run=Run(runId=run_id),
        job=Job(
            namespace="my-platform",
            name="custom_pipeline",
            facets={
                "sql": sql_job.SQLJobFacet(query="SELECT ...")
            }
        ),
        inputs=[
            Dataset(
                namespace="bigquery",
                name="raw.events",
                facets={
                    "schema": schema_dataset.SchemaDatasetFacet(
                        fields=[
                            schema_dataset.SchemaDatasetFacetFields(
                                name="event_id", type="string"
                            )
                        ]
                    )
                }
            )
        ],
        outputs=[
            Dataset(
                namespace="bigquery",
                name="warehouse.events_clean",
                facets={
                    "columnLineage": column_lineage_dataset.ColumnLineageDatasetFacet(
                        fields={
                            "event_id": column_lineage_dataset.Fields(
                                inputFields=[
                                    column_lineage_dataset.InputField(
                                        namespace="bigquery",
                                        name="raw.events",
                                        field="event_id"
                                    )
                                ],
                                transformationDescription="direct copy",
                                transformationType="IDENTITY"
                            )
                        }
                    )
                }
            )
        ],
        producer="my-platform/v1.0"
    ))
except Exception as e:
    client.emit(RunEvent(
        eventType=RunState.FAIL,
        eventTime=datetime.utcnow().isoformat() + "Z",
        run=Run(runId=run_id),
        job=Job(namespace="my-platform", name="custom_pipeline"),
        inputs=[],
        outputs=[],
        producer="my-platform/v1.0"
    ))
```

### Decorator Pattern (Reusable)

```python
def with_lineage(namespace, job_name, inputs_fn, outputs_fn):
    def decorator(func):
        def wrapper(*args, **kwargs):
            run_id = str(uuid.uuid4())
            client = OpenLineageClient.from_environment()
            
            inputs = inputs_fn(*args, **kwargs)
            
            # START
            client.emit(RunEvent(
                eventType=RunState.START,
                run=Run(runId=run_id),
                job=Job(namespace=namespace, name=job_name),
                inputs=inputs,
                outputs=[],
                eventTime=datetime.utcnow().isoformat() + "Z",
                producer="..."
            ))
            
            try:
                result = func(*args, **kwargs)
                outputs = outputs_fn(result, *args, **kwargs)
                
                # COMPLETE
                client.emit(RunEvent(
                    eventType=RunState.COMPLETE,
                    run=Run(runId=run_id),
                    job=Job(namespace=namespace, name=job_name),
                    inputs=inputs,
                    outputs=outputs,
                    ...
                ))
                return result
            except Exception as e:
                # FAIL
                client.emit(...)
                raise
        return wrapper
    return decorator

# Usage
@with_lineage(
    namespace="my-app",
    job_name="customer_enrichment",
    inputs_fn=lambda config: [
        Dataset(namespace="bigquery", name=config.input_table)
    ],
    outputs_fn=lambda result, config: [
        Dataset(namespace="bigquery", name=config.output_table)
    ]
)
def enrich_customers(config):
    # Your logic
    return processed_data
```

---

## 8. Backend: Marquez

### What is Marquez

Reference implementation of OpenLineage backend
- Storage: PostgreSQL
- API: REST + GraphQL
- UI: lineage graph visualization

### Deploy

```bash
# Docker compose
docker-compose -f docker-compose.dev.yml up

# Access
# UI: http://localhost:3000
# API: http://localhost:5000
```

### Schema

```sql
-- Simplified
CREATE TABLE jobs (
    uuid UUID PRIMARY KEY,
    namespace TEXT,
    name TEXT
);

CREATE TABLE datasets (
    uuid UUID PRIMARY KEY,
    namespace TEXT,
    name TEXT
);

CREATE TABLE runs (
    uuid UUID PRIMARY KEY,
    job_uuid UUID,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    state TEXT
);

CREATE TABLE run_inputs (
    run_uuid UUID,
    dataset_uuid UUID
);

CREATE TABLE run_outputs (
    run_uuid UUID,
    dataset_uuid UUID
);

CREATE TABLE column_lineage (
    output_dataset_uuid UUID,
    output_field TEXT,
    input_dataset_uuid UUID,
    input_field TEXT,
    transformation TEXT
);
```

### Query Lineage

```graphql
# GraphQL
{
  lineage(
    nodeId: "dataset:bigquery:warehouse.silver.customers"
    depth: 5
  ) {
    nodes {
      type
      name
      facets
    }
    edges {
      source
      target
    }
  }
}
```

---

## 9. Other Backends

### DataHub

```yaml
# datahub config
source:
  type: openlineage
  config:
    endpoint: http://datahub:8080/openlineage/api/v1
```

DataHub consumes OpenLineage events natively → builds rich catalog

### OpenMetadata

```yaml
# OpenMetadata setup
ingest:
  - type: openlineage
    config:
      endpoint: http://openmetadata:8585
```

### Egeria

Open Metadata Repository — enterprise focused

### Custom Backend

Anyone can implement OpenLineage receiver — it's just a REST endpoint accepting events

---

## 10. Lineage Patterns

### Dataset-Level Lineage (Easy)

```
raw.events ────► silver.events ────► gold.metrics ────► dashboard
```

### Column-Level Lineage (Best Practice)

```
raw.events.user_id ────► silver.users.id
raw.events.email ────► silver.users.email_hash (sha256)
raw.events.amount ────► gold.metrics.revenue (SUM)
```

### Cross-System Lineage

```
postgres://db.orders ────► s3://bucket/orders.parquet ────► bigquery.warehouse.orders
                              (Airflow)                        (Spark)
```

OpenLineage works across systems because namespace/name are universal

### Streaming Lineage

```
Kafka topic 'orders' ────► Flink job 'enrich_orders' ────► Iceberg 'orders_silver'
                                                       ────► Online Feature Store
```

Streaming jobs emit:
- START when job submitted
- RUNNING periodically (with metrics)
- COMPLETE on graceful stop

---

## 11. Integration ใน The-1 / Banking Context

### Recommendations

#### Phase 1: Auto-Instrumentation
- Spark jobs → openlineage-spark
- dbt → openlineage-dbt
- Airflow → openlineage-airflow

→ Get 80% lineage for free

#### Phase 2: Custom Pipelines
- Beam pipelines (custom emission via Python client)
- Cloud Run / Functions (decorator pattern)

→ Cover remaining 20%

#### Phase 3: Backend Choice
- Marquez (simple, free)
- DataHub (rich features, OSS)
- Dataplex (GCP managed, integrates BQ/Dataflow)

#### Phase 4: Custom Facets

```yaml
custom_facets:
  - banking_compliance:
      pdpa_classification: confidential
      bot_compliance_check: passed
      data_steward: compliance@bank.com
  - quality_score:
      score: 0.95
      checks_passed: 18
      checks_failed: 0
```

---

## 12. Limitations & Gotchas

### Limitation 1: Logic in External Systems
```
Pipeline reads from API, writes to BQ
OpenLineage knows: "no input dataset"
Workaround: emit custom dataset for API
```

### Limitation 2: Iceberg Streaming Writes
```
Spark Structured Streaming + Iceberg
Some integrations partial → may miss column lineage
Check: openlineage-spark version compatibility
```

### Limitation 3: Multi-Hop Logic in UDF
```
df.withColumn("score", complex_udf(col1, col2, col3))
OpenLineage may not extract: score depends on which input fields?
Workaround: prefer SQL/DataFrame ops over UDF when lineage matters
```

### Limitation 4: Cross-Cluster Lineage
```
Spark on cluster A writes to S3
Spark on cluster B reads from S3
Different clusters = different OpenLineage producers
Need backend to stitch (which Marquez does, by namespace+name match)
```

---

## 13. Cheat Sheet

### Q: "OpenLineage คืออะไร?"
> "Open standard event format สำหรับ data lineage
> Tools (Spark, Airflow, dbt) emit events → catalog (DataHub, Marquez) consume
> Avoid vendor lock-in, get column-level lineage for free"

### Q: "Spark + OpenLineage ทำงานยังไง?"
> "Add JAR + listener config → Spark auto-emits events ทุก read/write
> Column lineage extracted from Catalyst logical plan
> No code changes needed"

### Q: "Custom pipeline emit lineage ยังไง?"
> "ใช้ Python client (openlineage-python)
> Wrap pipeline ใน try-except, emit START + COMPLETE/FAIL
> Add facets: schema, column lineage, custom metadata
> หรือใช้ decorator pattern เพื่อ reuse"

### Q: "เลือก backend ไหน?"
> "Marquez: simple, official OL backend
> DataHub: enterprise catalog + OL native
> Dataplex: GCP managed (auto-discover + OL)
> เลือกตาม catalog strategy ขององค์กร"

---

## Sources

- [OpenLineage GitHub](https://github.com/OpenLineage/OpenLineage)
- [Getting Started | OpenLineage](https://openlineage.io/getting-started/)
- [OpenLineage Specification](https://github.com/OpenLineage/OpenLineage/blob/main/spec/OpenLineage.md)
- [Data Lineage with OpenLineage](https://medium.com/@manideepgrandhi02/data-lineage-with-openlineage-8cd095f9eb4e)
- [The OpenLineage Standard](https://apxml.com/courses/data-governance-quality-observability-production/chapter-4-data-lineage-metadata-management/openlineage-standard)
- [Column level lineage in Fabric Spark with OpenLineage](https://www.rakirahman.me/openlineage-to-delta/)
- [OpenLineage for a unified lineage view across structured and unstructured data](https://www.ibm.com/new/announcements/openlineage-for-a-unified-lineage-view-across-structured-and-unstructured-data-to-enable-explainable-ai)
