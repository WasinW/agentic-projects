# Data Platform Capabilities — Deep Dive

> เอกสารต่อจาก `Data_Platform_Capabilities_Reference.md`
> ขยายเจาะลึกแต่ละ capability — implementation, tools, patterns, code

---

## 1. Data Catalog — Deep Dive

### What Catalog Solves

Without catalog:
- "ตารางนี้มีอยู่มั้ย?"
- "ใครเป็นเจ้าของ?"
- "Column นี้หมายถึงอะไร?"
- "ใช้ข้อมูลนี้ได้มั้ย? PII?"
- "Data ล่าสุดเมื่อไหร่?"

ทุกคำถามตอบใช้เวลา 30 นาที ค้นเอกสาร ถามคน

With catalog: 30 วินาที — Google-search-like

### Catalog Architecture

```
┌──────────────────────────────────────────────────────┐
│              ACTIVE METADATA LAYER                   │
│  • Auto-discovery from sources                       │
│  • Real-time updates                                 │
│  • AI-powered (semantic search, auto-tag)            │
└─────────────────────┬────────────────────────────────┘
                      │ scrapes / receives events
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
┌────────────┐ ┌────────────┐ ┌────────────┐
│ Data       │ │ Pipelines  │ │ BI Tools   │
│ Warehouses │ │ (Airflow,  │ │ (Looker,   │
│ Lakes      │ │  dbt)      │ │  Tableau)  │
└────────────┘ └────────────┘ └────────────┘
```

### Catalog Information Model

ทุก data asset ต้องมี:

```yaml
asset:
  id: warehouse.silver.customers
  type: table
  format: iceberg
  
  # Identity
  name: customers
  domain: customer
  description: "Cleansed customer master data"
  tags: ["pii", "core_entity", "tier1"]
  
  # Ownership
  owner_team: customer_data_team
  owner_individual: jane.doe@company.com
  steward: customer_steward@company.com
  
  # Schema
  columns:
    - name: customer_id
      type: string
      description: "Unique customer ID"
      pii: false
      key: true
    - name: phone
      type: string
      description: "Customer phone"
      pii: true
      pii_classification: contact_info
      masking: hash
  
  # Quality + freshness
  freshness:
    sla: 1_hour
    last_updated: 2026-05-04T10:00:00Z
  quality:
    last_check: 2026-05-04T11:00:00Z
    score: 98%
    issues: []
  
  # Lineage
  upstream_assets:
    - raw.bronze.customer_events
    - reference.country_codes
  downstream_assets:
    - mart.gold.customer_360
    - feature_store.customer_features_v3
  
  # Usage
  popularity:
    queries_per_day: 1500
    unique_users_30d: 45
  
  # Compliance
  classification: confidential
  retention: 7_years
  region: thailand
```

### Catalog Tools 2026

#### DataHub (LinkedIn OSS)
**Pros**: Most extensible, large community, supports almost everything
**Cons**: Complex setup, requires Kafka

```yaml
# datahub_recipe.yaml
source:
  type: bigquery
  config:
    project_id: my-project
    include_table_lineage: true
    profiling:
      enabled: true

sink:
  type: datahub-rest
  config:
    server: 'http://datahub:8080'
```

#### OpenMetadata
**Pros**: Modern UI, schema-first, easier setup than DataHub
**Cons**: Newer, smaller ecosystem

#### Dataplex (GCP)
**Pros**: Native GCP integration, auto-discover BQ + GCS + Dataflow
**Cons**: GCP only

#### Unity Catalog (Databricks → OSS 2024+)
**Pros**: Multi-format (Iceberg, Delta), multi-cloud, native to Databricks
**Cons**: Complex permissions model

#### Atlan
**Pros**: Best UX, governance focus, good for non-technical users
**Cons**: Commercial, expensive

### Auto-Discovery Patterns

#### Pattern 1: Pull-Based Crawler
```python
# Run on schedule
def crawl_bigquery():
    for dataset in client.list_datasets():
        for table in client.list_tables(dataset):
            metadata = extract_metadata(table)
            datahub.emit(metadata)
```

**Pro**: Don't need source-side changes
**Con**: Periodic, not real-time

#### Pattern 2: Event-Driven (Push)
```
Pipeline emits OpenLineage event
   ↓
Lineage events go to Kafka
   ↓
Catalog consumes events
   ↓
Real-time updates
```

**Pro**: Real-time, accurate
**Con**: Need pipeline instrumentation

### Search & Discovery UX

ที่ดีต้องมี:
- **Free-text search** (semantic, not keyword)
- **Filters**: domain, owner, tags, freshness
- **Preview**: sample rows, schema
- **Lineage view**: where it comes from / goes to
- **Usage stats**: who uses it, how often
- **Trust signals**: quality score, last refresh

---

## 2. Data Lineage — Deep Dive

### Levels of Lineage Granularity

#### Level 1: Dataset-Level
```
raw.events → silver.cleaned → gold.aggregated → dashboard.metrics
```
- Easiest to implement
- Useful for impact analysis

#### Level 2: Column-Level (Important!)
```
silver.users.email_hash ← FROM raw.users.email (transformation: sha256)
gold.metrics.dau ← FROM silver.events.user_id (transformation: COUNT DISTINCT)
```
- Critical for compliance (PII tracking)
- Better impact analysis

#### Level 3: Cell-Level (Rare)
- Track per-row provenance
- Used in highly regulated (banking, healthcare)
- Expensive, complex

### OpenLineage Standard

มาตรฐานเปิดที่ใช้กันใน 2026 — รองรับ Spark, Beam, dbt, Airflow

```python
# Example: emit lineage event from custom pipeline
from openlineage.client import OpenLineageClient
from openlineage.client.event_v2 import RunEvent, Run, Job, Dataset

client = OpenLineageClient.from_environment()

client.emit(RunEvent(
    eventTime=now_iso(),
    eventType="START",
    run=Run(runId=run_uuid),
    job=Job(namespace="my-platform", name="customer_etl"),
    inputs=[
        Dataset(namespace="bigquery", name="raw.customer_events")
    ],
    outputs=[
        Dataset(namespace="bigquery", name="silver.customers")
    ],
    facets={
        "schema": SchemaDatasetFacet(...),
        "columnLineage": ColumnLineageDatasetFacet(...)
    }
))
```

### Column-Level Lineage Implementation

```python
# Capture transformation logic per column
column_lineage = {
    "outputs": {
        "silver.customers": {
            "fields": {
                "customer_id": {
                    "inputFields": [
                        {"namespace": "bq", "name": "raw.events.user_id"}
                    ],
                    "transformationDescription": "direct copy"
                },
                "email_hash": {
                    "inputFields": [
                        {"namespace": "bq", "name": "raw.events.email"}
                    ],
                    "transformationDescription": "sha256(email)"
                }
            }
        }
    }
}
```

### Spark Auto-Lineage (OpenLineage Spark)

```python
# Just add the integration JAR
spark = SparkSession.builder \
    .config("spark.jars.packages", "io.openlineage:openlineage-spark:1.20.0") \
    .config("spark.extraListeners", "io.openlineage.spark.agent.OpenLineageSparkListener") \
    .config("spark.openlineage.transport.type", "http") \
    .config("spark.openlineage.transport.url", "http://datahub:8080") \
    .getOrCreate()

# Now every Spark SQL/DataFrame operation auto-emits lineage
df = spark.read.table("raw.customers")
df_clean = df.filter("status = 'active'")
df_clean.write.table("silver.customers")
# → OpenLineage event emitted automatically
```

### dbt Lineage (Built-in)

dbt has native lineage:
```sql
-- models/silver/customers.sql
{{ config(materialized='table') }}

WITH source AS (
    SELECT * FROM {{ ref('raw_customers') }}  -- dbt knows the lineage
)
SELECT
    user_id AS customer_id,
    sha2(email, 256) AS email_hash,
    -- dbt parses this and knows column lineage
    AVG(amount) OVER (PARTITION BY user_id) AS avg_amount
FROM source
```

```bash
dbt docs generate
dbt docs serve  # auto-generated lineage UI
```

---

## 3. Data Contracts — Deep Dive

### What Contract Looks Like

```yaml
# contracts/orders_v2.yaml
domain: commerce
entity: order
schema_version: 2.0.0
contract_type: producer-consumer

producers:
  - service: order-service
    team: commerce_team

consumers:
  - dataset: warehouse.silver.orders
    team: data_team
  - service: fraud_detection_service
    team: risk_team

schema:
  format: avro  # or protobuf, json_schema
  fields:
    - name: order_id
      type: string
      required: true
      pii: false
      description: "Unique order identifier"
    - name: customer_id
      type: string
      required: true
      pii: false
    - name: amount
      type: decimal(10,2)
      required: true
      validation:
        min: 0
        max: 1000000
    - name: customer_phone
      type: string
      required: true
      pii: true
      masking: hash_sha256
    - name: items
      type: array<object>
      required: true

sla:
  freshness: "5 minutes"
  completeness: 99.9%
  schema_compatibility: "BACKWARD"

breaking_changes:
  policy: major_version_bump
  deprecation_period: 30_days

quality_rules:
  - rule: amount > 0
  - rule: customer_id IS NOT NULL
  - rule: order_id is unique
```

### Schema Format Comparison

| Format | Pros | Cons | When to use |
|---|---|---|---|
| **Avro** | Best schema evolution, compact | Less human-readable | Kafka, Hadoop, batch |
| **Protobuf** | Fastest, smallest | Limited evolution flexibility | gRPC, real-time |
| **JSON Schema** | Most readable, ubiquitous | Verbose, slower | REST APIs, docs |

**Recommendation**: Avro for streams + warehouse, JSON Schema for APIs

### Contract Enforcement Patterns

#### Pattern 1: Schema Registry (Kafka)

```
Producer:
  1. Define schema in registry
  2. Producer registers schema
  3. Schema validated against compatibility rules
  4. If breaking change → deployment fails
  5. If compatible → publish allowed

Consumer:
  1. Read from registry
  2. Consume with schema
  3. If producer breaks → consumer fails fast
```

```python
# Confluent Schema Registry example
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

schema_str = open("orders_v2.avsc").read()
sr_client = SchemaRegistryClient({"url": "http://schema-registry:8081"})

# Producer registers + validates compatibility
serializer = AvroSerializer(
    schema_registry_client=sr_client,
    schema_str=schema_str,
)
# If schema breaks compatibility, this throws
```

#### Pattern 2: CI Gate (datacontract-cli)

```bash
# In CI/CD pipeline
datacontract test contracts/orders_v2.yaml
# Validates: schema, quality rules, SLA

datacontract diff contracts/orders_v1.yaml contracts/orders_v2.yaml
# Detects breaking changes

# Gate: don't merge if breaking
```

```yaml
# .github/workflows/contract-check.yml
- name: Validate contracts
  run: |
    datacontract test contracts/*.yaml --strict
- name: Detect breaking changes
  run: |
    datacontract diff origin/main HEAD --fail-on-breaking
```

#### Pattern 3: Application-Side Validation

```python
# In producer service
from pydantic import BaseModel, validator

class OrderEvent(BaseModel):
    order_id: str
    customer_id: str
    amount: Decimal
    
    @validator("amount")
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("amount must be positive")
        return v

# In CI: test that real events match contract
def test_order_matches_contract():
    sample_event = generate_sample()
    OrderEvent.parse_obj(sample_event)  # raises if invalid
```

### Schema Evolution Rules

#### BACKWARD Compatibility (most common)
- New schema can read old data
- Allowed: add optional field, remove field
- Forbidden: add required field, change type

#### FORWARD Compatibility
- Old schema can read new data
- Allowed: remove field, add field with default
- Forbidden: rename field

#### FULL Compatibility (strictest)
- Both BACKWARD and FORWARD
- Allowed: add optional with default
- Forbidden: most changes

### Breaking Change Process

```
1. Producer wants to change schema (breaking)
   ↓
2. Open RFC / proposal
   ↓
3. Notify all consumers (>= 30 days)
   ↓
4. Bump major version (v2 → v3)
   ↓
5. Run v2 + v3 in parallel (deprecation period)
   ↓
6. Track consumer migration
   ↓
7. When all consumers migrated → retire v2
```

---

## 4. Data Quality — Deep Dive

### The 6 Dimensions Revisited

#### 1. Accuracy
```python
# Reference data check
def check_accuracy():
    for record in transactions:
        # Cross-check with golden source
        if record.customer_phone != golden_source.get(record.customer_id).phone:
            raise AccuracyError()
```

#### 2. Completeness
```python
# Null check + record count
expectations = [
    {"column": "customer_id", "null_pct_max": 0},
    {"column": "amount", "null_pct_max": 0.5},
    {"row_count_min": 1000, "row_count_max": 1000000},
]
```

#### 3. Consistency
```python
# Cross-table check
def check_consistency():
    customer_count_table_a = query("SELECT COUNT(*) FROM table_a")
    customer_count_table_b = query("SELECT COUNT(*) FROM table_b")
    assert abs(a - b) < tolerance
```

#### 4. Timeliness
```python
# Freshness check
def check_freshness():
    last_record = query("SELECT MAX(event_time) FROM events")
    age = now() - last_record
    assert age < timedelta(minutes=10)
```

#### 5. Uniqueness
```python
# Duplicate check
def check_uniqueness():
    dups = query("""
        SELECT order_id, COUNT(*) c
        FROM orders
        GROUP BY order_id
        HAVING c > 1
    """)
    assert len(dups) == 0
```

#### 6. Validity
```python
# Format / range check
def check_validity():
    # Phone format
    assert all(re.match(r"^\+\d{10,15}$", p) for p in phones)
    # Amount range
    assert all(0 <= a <= 1000000 for a in amounts)
```

### Tools Comparison

#### dbt Tests
```sql
-- models/orders.sql
{{ config(materialized='table') }}
SELECT ...
```

```yaml
# models/schema.yml
models:
  - name: orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: amount
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1000000
```

**Pros**: in-line with transformation, simple
**Cons**: limited to schema-level checks

#### Great Expectations (GE)

```python
import great_expectations as gx

context = gx.get_context()

batch = context.get_batch(
    datasource_name="my_source",
    table_name="orders"
)

batch.expect_column_values_to_not_be_null("order_id")
batch.expect_column_values_to_be_unique("order_id")
batch.expect_column_values_to_be_between("amount", 0, 1000000)
batch.expect_column_value_lengths_to_be_between("phone", 10, 15)

result = batch.validate()
```

**Pros**: rich expectations library, profiling
**Cons**: heavier setup

#### Soda

```yaml
# checks.yml
checks for orders:
  - missing_count(order_id) = 0
  - duplicate_count(order_id) = 0
  - invalid_count(amount) = 0:
      valid min: 0
      valid max: 1000000
  - row_count > 1000
  - freshness(event_time) < 10m
  - schema:
      fail:
        when required column missing: [order_id, amount]
```

```bash
soda scan -d production checks.yml
```

**Pros**: declarative, hybrid testing + observability
**Cons**: SaaS or self-host trade-off

### Quality Architecture: Pre-load vs Post-load

#### Pre-load (Validation Gate)
```
Source → Validation → If pass: Load
                    → If fail: DLQ + alert
```
- Catches issues before pollution
- Pipeline blocks until fixed
- Higher reliability

#### Post-load (Detection)
```
Source → Load → Run quality checks
              → If fail: alert (data already in DW)
```
- Faster pipeline
- Issues found later
- Need rollback strategy

**Best practice**: pre-load critical checks (schema), post-load comprehensive checks (statistical)

### Data Quality Monitoring Architecture

```
┌──────────────────────────────────────────────────┐
│              QUALITY ENGINE                      │
│  • Schedule checks (per dataset)                 │
│  • Run via Spark/dbt                             │
│  • Output structured results                     │
└─────────────────────┬────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────┐
│              METRICS STORE                       │
│  Quality scores per dataset over time            │
└─────────────────────┬────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────┐
│              ALERTING                            │
│  • Threshold breach → PagerDuty                  │
│  • Trend degradation → Email                     │
└──────────────────────────────────────────────────┘
```

---

## 5. Audit Logging — Deep Dive

### What to Log

#### Layer 1: Access Audit
- Who queried what dataset
- Who downloaded file
- Who changed permission

#### Layer 2: Change Audit
- Who deployed pipeline
- Who modified schema
- Who promoted model

#### Layer 3: Data Modification Audit
- Who inserted/updated/deleted rows (in operational DB)
- Who reprocessed historical data
- Who manually corrected data

### Cloud Audit Logs (GCP example)

```sql
-- Query Cloud Audit Logs
SELECT
    timestamp,
    protopayload_auditlog.authenticationInfo.principalEmail AS user,
    protopayload_auditlog.serviceName AS service,
    protopayload_auditlog.methodName AS action,
    protopayload_auditlog.resourceName AS resource
FROM `my-project.audit_logs.cloudaudit_googleapis_com_data_access`
WHERE timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP, INTERVAL 7 DAY)
  AND protopayload_auditlog.serviceName = 'bigquery.googleapis.com'
ORDER BY timestamp DESC
```

### Application-Level Audit

```python
class AuditLogger:
    def __init__(self):
        self.client = AuditLogClient()
    
    def log_data_access(self, user, dataset, action, query):
        self.client.emit({
            "timestamp": now(),
            "user_id": user.id,
            "user_email": user.email,
            "dataset": dataset,
            "action": action,  # READ, WRITE, DELETE
            "query": redact_pii(query),
            "result_count": result.count,
            "duration_ms": result.duration,
            "ip_address": user.ip,
        })
```

### Audit Best Practices

1. **Immutable logs** — write-only, no modification
2. **Centralized** — single source for audit
3. **Retention** — keep 7+ years for banking
4. **Encryption** — at rest + in transit
5. **Separate access** — auditors only, not engineers
6. **Monitoring** — alert on suspicious patterns
7. **Tamper detection** — hash chain logs

---

## 6. Cost Observability (FinOps for Data) — Deep Dive

### Why Data FinOps

Data platform spending grows uncontrolled because:
- BigQuery slot/on-demand pricing complex
- Snowflake credit consumption opaque
- Databricks DBU pricing variable
- Engineers don't see cost in real-time

### Cost Visibility Hierarchy

```
LEVEL 1: Total spend per month
LEVEL 2: Spend per project / environment
LEVEL 3: Spend per team / cost center
LEVEL 4: Spend per pipeline / job
LEVEL 5: Spend per query / row processed
LEVEL 6: Cost per business outcome
```

### Implementation: BigQuery Cost Tracking

```sql
-- Information schema gives query-level cost
SELECT
    user_email,
    project_id,
    query,
    creation_time,
    total_bytes_processed,
    total_bytes_processed * 5 / POW(10, 12) AS cost_usd,  -- $5/TB
    total_slot_ms,
    cache_hit
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY)
  AND job_type = "QUERY"
ORDER BY total_bytes_processed DESC
LIMIT 100
```

### Mandatory Tagging Strategy

ทุก resource ต้องมี:
```
team: "fraud_team"
project: "fraud_v2"
environment: "production"
cost_center: "CC-1234"
owner: "jane.doe@company.com"
purpose: "ml_training"
```

### Tools 2026

| Tool | Specialty |
|---|---|
| **SELECT** (DoiT) | BigQuery deep optimization |
| **Finout** | Multi-cloud, Databricks/Snowflake |
| **Revefi** | Autonomous AI optimization |
| **Bluesky** | Snowflake cost optimization |
| **Cloudability** (Apptio) | Enterprise FinOps |

### Cost Optimization Patterns

#### Pattern 1: Partition + Cluster
```sql
-- Without: scans entire 1TB table = $5
SELECT * FROM events WHERE event_date = '2026-05-01'

-- With partition + cluster: scans 5GB = $0.025
CREATE TABLE events
PARTITION BY DATE(event_date)
CLUSTER BY customer_id
AS ...
```

#### Pattern 2: Materialize Aggregates
```sql
-- Instead of querying raw 100x
-- Materialize hourly summary once
CREATE MATERIALIZED VIEW orders_hourly AS
SELECT date_trunc(event_time, hour) AS hour, COUNT(*) AS c
FROM orders
GROUP BY 1
```

#### Pattern 3: Slot Reservation (predictable workload)
```
On-demand: $5/TB scanned (variable)
Slot reservation: $X/slot/month (fixed)

If your scan cost > $X/month → reserve
Use Auto-scaling for spikes
```

#### Pattern 4: Avoid Anti-Patterns
- `SELECT *` when only need few columns
- `ORDER BY` without LIMIT
- Cross-region queries
- Cartesian joins
- Large UNNEST in WHERE

---

## 7. DataOps Practices — Deep Dive

### CI/CD for Data

#### Pipeline as Code
```python
# pipelines/customer_etl.py
@dag(schedule="@daily", start_date=datetime(2026,1,1))
def customer_etl():
    extract = ExtractTask(source="postgres.customers")
    transform = TransformTask(sql="cleaning.sql")
    load = LoadTask(target="iceberg.silver.customers")
    validate = ValidateTask(checkpoint="customer_quality")
    
    extract >> transform >> load >> validate
```

#### CI Pipeline
```yaml
# .github/workflows/data-ci.yml
on: [pull_request]

jobs:
  test:
    steps:
      - uses: actions/checkout@v3
      
      - name: Lint SQL
        run: sqlfluff lint models/
      
      - name: dbt parse + compile
        run: dbt deps && dbt parse
      
      - name: dbt test (sample)
        run: dbt test --select tag:critical
      
      - name: Schema diff (breaking change?)
        run: dbt-schema-diff origin/main HEAD
        # Fail if breaking change
      
      - name: Unit tests
        run: pytest tests/unit/
      
      - name: Cost estimate
        run: |
          python scripts/estimate_cost.py models/
          # Fail if > $50/run
```

#### CD Pipeline
```yaml
on:
  push:
    branches: [main]

jobs:
  deploy:
    steps:
      - name: Build image
        run: docker build -t pipeline:${{ github.sha }} .
      
      - name: Deploy to staging
        run: terraform apply -target=staging
      
      - name: Run integration tests
        run: pytest tests/integration/ --env=staging
      
      - name: Deploy to production
        run: terraform apply -target=production
        if: success()
      
      - name: Notify
        run: slack-notify "Deployed pipeline:${{ github.sha }}"
```

### Environment Management

```
DEV:
  - Each engineer's branch
  - Sample data (1% of prod)
  - Cheap compute
  - Fast iteration

STAGING:
  - Mirrors production schema
  - Full data (refreshed weekly from prod)
  - Used for integration tests
  - Pre-prod validation

PROD:
  - Real data
  - SLA guarantees
  - Full monitoring
  - Approved deploys only
```

### Backfill Strategy

```python
# Idempotent backfill pattern
def backfill_pipeline(start_date, end_date):
    for date in date_range(start_date, end_date):
        # Each date is independent
        # Re-run safe (idempotent)
        with transaction():
            delete_existing(date)  # clean slate
            run_pipeline(date)
            validate(date)
```

```bash
# Backfill via CLI
dbt run --vars '{start_date: 2026-01-01, end_date: 2026-04-30}' \
        --target prod_backfill \
        --threads 8
```

### Idempotency Patterns

#### Pattern 1: MERGE (upsert)
```sql
MERGE INTO silver.customers AS target
USING staging.customers AS source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...
```

#### Pattern 2: Delete + Insert
```sql
DELETE FROM silver.customers WHERE event_date = ?;
INSERT INTO silver.customers SELECT ... WHERE event_date = ?;
```

#### Pattern 3: Iceberg Snapshot Replace
```python
# Iceberg supports atomic snapshot replace
df.write.format("iceberg") \
    .option("write.distribution-mode", "hash") \
    .mode("overwrite") \
    .option("overwrite-mode", "dynamic") \
    .partitionBy("event_date") \
    .saveAsTable("silver.customers")
```

---

## 8. Self-Service Platform — Deep Dive

### What "Self-Service" Means

Domain teams ทำงานได้เองโดยไม่ต้องผ่าน Data Engineering กลาง:
- Onboard new data source (1 day, not 2 weeks)
- Create new pipeline (1 hour, not 1 week)
- Query data (immediate, not request)
- Build dashboard (no DE involvement)

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  PORTAL UI                              │
│  • Form to define pipeline (no code)                    │
│  • Browse data catalog                                  │
│  • Self-service permissions request                     │
│  • View own usage + cost                                │
└─────────────────────┬───────────────────────────────────┘
                      │ generates configs
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  CONFIG STORE                           │
│  YAML configs in Git (GitOps)                           │
└─────────────────────┬───────────────────────────────────┘
                      │ triggers
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  PLATFORM ENGINE                        │
│  • Reads config                                         │
│  • Generates pipeline (Beam/Spark)                      │
│  • Deploys to runtime                                   │
│  • Auto-monitoring                                      │
└─────────────────────────────────────────────────────────┘
```

### Template Pattern (Pipeline-as-Form)

```yaml
# What user fills in (simple)
name: marketing_email_clicks
team: marketing
source:
  type: s3
  path: s3://marketing/email_clicks/
  format: json
target:
  table: silver.marketing.email_clicks
schedule: daily
```

```python
# Platform engine generates the full Beam pipeline
def generate_pipeline_from_config(config):
    return f"""
    ReadFromS3({config.source.path})
        | ParseJSON()
        | ValidateSchema()
        | StandardEnrich()
        | WriteToIceberg({config.target.table})
    """
```

### Permission Self-Service

```yaml
# permission_request.yaml
requester: jane.doe@company.com
team: marketing
requesting:
  asset: warehouse.silver.customers
  level: read
  columns: ["customer_id", "email_hash"]  # not all
  duration: 30_days
business_justification: "Build email campaign segmentation"
```

```python
# Auto-approval if:
def auto_approve(request):
    if request.team in asset.allowed_teams:
        return True
    if request.level == "read" and request.columns_only_non_pii:
        return True
    return False  # → human review
```

---

## 9. Implementation Patterns สำหรับ Cross-Cutting

### Pattern A: Library Approach (สำหรับ small teams)

```python
# platform_lib/__init__.py
from .observability import emit_metric, emit_audit
from .governance import register_dataset, emit_lineage
from .quality import run_check
from .cost import attribute_cost
```

```python
# in user pipeline
from platform_lib import emit_metric, register_dataset

@register_dataset(name="orders_silver", owner="commerce")
def transform():
    df = read_source()
    emit_metric("rows_read", len(df))
    return df
```

### Pattern B: Decorator/Hooks (สำหรับ medium teams)

```python
@platform_pipeline(
    name="customer_etl",
    sla="1h",
    pii_handling="auto_mask",
    cost_attribution="commerce"
)
def my_pipeline():
    # Platform handles audit + lineage + cost + quality automatically
    return data_logic()
```

### Pattern C: Sidecar Services (สำหรับ large teams)

```
Each pipeline emits standard events
   ↓
OpenLineage sidecar listens
   ↓
Catalog service consumes
Quality service consumes
Cost service consumes
Audit service consumes
   ↓
All services updated automatically
```

### Pattern D: Service Mesh (สำหรับ very large)

```
Pipelines call services via internal API
  ↓
Service mesh handles:
  - Auth + audit
  - Tracing + metrics
  - Rate limiting
  - Retry + circuit breaker
```

---

## 10. Implementation Decision Framework

### Question 1: Build vs Buy?

| Capability | Build (OSS) | Buy (Commercial) |
|---|---|---|
| Catalog | DataHub, OpenMetadata | Atlan, Collibra |
| Quality | dbt tests, GE | Soda, Monte Carlo |
| Lineage | OpenLineage spec | DataHub commercial, Atlan |
| Observability | Evidently | Monte Carlo, Bigeye |
| Cost | Custom + Iceberg metadata | SELECT, Finout |

**กฎ**:
- Small team (<10) → buy (managed time > money)
- Medium (10-50) → mix (build core, buy advanced)
- Large (50+) → build (control + custom)

### Question 2: Centralized vs Federated?

```
< 50 datasets → Centralized
50-500 → Hybrid (central platform, federated ownership)
500+ → Federated (mesh-style)
```

### Question 3: Open Source vs Cloud Native?

| Factor | Open Source | Cloud Native (e.g. Dataplex) |
|---|---|---|
| Lock-in | Low | High |
| Setup | High effort | Low |
| Cost | Self-host = compute | Pay per usage |
| Multi-cloud | ✅ | ❌ |

---

## 11. Maturity Implementation Roadmap

### Year 1: Foundation
**Quarter 1**:
- Set up catalog (DataHub or Dataplex)
- Auto-ingest metadata from BQ + Dataflow
- Define top 10 critical assets

**Quarter 2**:
- Implement dbt tests (Level 1 DQ)
- Add OpenLineage to pipelines
- Set up Cloud Audit Log review

**Quarter 3**:
- Add Soda or GE for advanced DQ
- Cost attribution mandatory tags
- DataDog or equivalent for ops monitoring

**Quarter 4**:
- Define top 5 Data Contracts
- Schema Registry for streams
- CI gate for breaking changes

### Year 2: Scale
- Self-service portal
- Federated governance
- Active metadata + AI assistance
- Multi-domain catalog

---

## 12. Cheat Sheet

### Q: "ทำไม Catalog สำคัญ?"
> "ลด time-to-find-data จาก 30 นาที → 30 วินาที
> เป็น 'Google search' ของ enterprise
> Active metadata + auto-discovery + lineage + quality = trust"

### Q: "Data Contract ใช้ format ไหน?"
> "Avro: streaming + warehouse (best evolution)
> Protobuf: real-time gRPC (fastest)
> JSON Schema: REST API (most readable)
> Most enterprise = Avro for events + JSON for APIs"

### Q: "วัด Data Quality ยังไง?"
> "6 dimensions: Accuracy, Completeness, Consistency, Timeliness, Uniqueness, Validity
> Tools: dbt tests (in-pipeline), GE/Soda (validation), Monte Carlo (observability)
> Critical: pre-load gates + post-load monitoring"

### Q: "OpenLineage คืออะไร?"
> "Open standard ของ data lineage event ใช้กันใน Spark, Beam, dbt, Airflow
> ส่ง event ที่บอกว่า 'job X อ่าน table A เขียน table B'
> Catalog tools (DataHub, Marquez) consume events เพื่อสร้าง lineage graph"

---

## เอกสารต่อ

- [Data_Platform_Capabilities_Reference.md](Data_Platform_Capabilities_Reference.md) — overview
- [Modern_Data_AI_Platform_Blueprint.md](Modern_Data_AI_Platform_Blueprint.md) — architecture decisions
- [ML/](ML/) — ML platform capabilities
- [AI/](AI/) — AI platform capabilities
- [References.md](References.md) — sources for all documents
