# Feature Store — Deep Dive

> ทำไมต้องมี, ทำงานยังไง, build vs buy, point-in-time joins, training-serving skew
> สำคัญที่สุดเรื่องเดียวที่ทำให้ ML platform แตกต่างจาก notebook+model.pkl

---

## 1. ทำไมต้องมี Feature Store

### Pain Point จริงที่เกิดในองค์กร (ก่อนมี FS)

| Pain | สาเหตุ |
|---|---|
| **Training-Serving Skew** | features ใน training pipeline ≠ features ใน serving (คนละ code path) |
| **Feature Reinvention** | ทุก data scientist เขียน feature `avg_purchase_7d` ใหม่ ตามใจ |
| **Data Leakage** | ใช้ "future information" ที่จริงไม่มีในตอน inference |
| **Slow Iteration** | data scientist รอ DE สร้าง feature pipeline ใหม่ทุกครั้ง |
| **Inconsistent Logic** | feature เดียวกันใน 5 model ใช้ logic ต่างกัน |

### What Feature Store Solves

**คำจำกัดความ**: 
> ระบบกลางที่ define + compute + serve features ทั้ง batch และ online โดยใช้ definition เดียวกัน

**3 ปัญหาหลักที่แก้**:
1. **Training-Serving Skew** — ใช้ definition เดียวกันทั้ง 2 side
2. **Point-in-Time Correctness** — ป้องกัน data leakage
3. **Feature Reusability** — ทีมอื่นใช้ซ้ำได้

---

## 2. Architecture ของ Feature Store

### Components หลัก

```
┌─────────────────────────────────────────────────────────────┐
│                  FEATURE REGISTRY                           │
│           (declarative YAML / Python definitions)           │
│      "what features exist, how to compute, owner"           │
└───────────────────┬─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌───────────────────┐   ┌───────────────────┐
│  OFFLINE STORE    │   │  ONLINE STORE     │
│                   │   │                   │
│  • Iceberg/BQ     │   │  • Bigtable/Redis │
│  • Bulk read      │   │  • ms-latency     │
│  • Time-travel    │   │  • Latest values  │
│  • Used in        │   │  • Used in        │
│    TRAINING       │   │    SERVING        │
└───────────────────┘   └───────────────────┘
        ▲                       ▲
        │                       │
┌───────────────────────────────────────────┐
│          COMPUTE ENGINE                   │
│   • Materialization jobs (Spark/Beam/dbt) │
│   • Sync offline → online                 │
└───────────────────────────────────────────┘
```

### 3 Compute Patterns

#### Pattern A: Batch-Only Features
```
Source DB → daily ETL → Iceberg (offline) → sync to Bigtable (online)
```
- **Use case**: avg_purchase_30d, customer_segment, lifetime_value
- **Freshness**: T+1 acceptable
- **Tools**: dbt, Spark, Beam batch

#### Pattern B: Streaming Features
```
Kafka events → Beam/Flink stateful → Bigtable (online)
                                  ↓
                            Iceberg (offline backfill)
```
- **Use case**: purchases_last_5_min, active_session_count
- **Freshness**: seconds
- **Challenge**: ensure offline = online

#### Pattern C: On-Demand Features
```
At inference time → compute from request data → no storage
```
- **Use case**: distance(user_location, store_location), age_at_event
- **Computed during serving** (no FS storage)
- **Pattern**: Feast supports `OnDemandFeatureView`

---

## 3. Point-in-Time Joins — แก่นของ FS

นี่คือ **หัวใจ** ที่ FS แก้ปัญหา data leakage

### ปัญหา Data Leakage แบบ subtle

ลองคิดว่ากำลัง train fraud model:

**Naive approach** (❌ leak future):
```sql
-- ใช้ "ค่าเฉลี่ย 30 วัน" ของลูกค้า ณ ปัจจุบัน
SELECT 
  txn_id, txn_time, amount,
  (SELECT AVG(amount) FROM txns WHERE customer_id = t.customer_id) AS avg_30d,
  is_fraud
FROM txns t
```

**ปัญหา**: avg_30d รวม transaction ที่เกิด **หลัง** event เป้าหมาย → leak future

### Point-in-Time Correct Pattern

```sql
-- คำนวณ avg ตาม "snapshot ณ เวลานั้น"
SELECT 
  t.txn_id, t.txn_time, t.amount,
  AVG(prev.amount) AS avg_30d_before_event,
  t.is_fraud
FROM txns t
LEFT JOIN txns prev
  ON prev.customer_id = t.customer_id
  AND prev.txn_time BETWEEN t.txn_time - INTERVAL '30 days' AND t.txn_time - INTERVAL '1 second'
GROUP BY t.txn_id, t.txn_time, t.amount, t.is_fraud
```

**กฎเหล็ก**:
- Feature ณ event time T ต้องใช้ข้อมูลที่อยู่ **ก่อน** T เท่านั้น
- ห้ามใช้ feature value ปัจจุบันสำหรับ historical event

### Feast's Point-in-Time API

```python
# Feast does this automatically
training_df = store.get_historical_features(
    entity_df=entity_df,  # contains entity_id + event_timestamp
    features=[
        "customer_features:avg_purchase_30d",
        "customer_features:txn_count_7d",
    ]
).to_df()

# Feast guarantees: each row's features are computed
# AS OF that row's event_timestamp (no leakage)
```

---

## 4. Training-Serving Skew — How FS Eliminates It

### Without Feature Store (skew problem)

```
TRAINING SIDE:
  Spark batch job:
    SELECT customer_id, AVG(amount) OVER (LAST 7 DAYS) AS avg_7d
    FROM transactions
  → train model
  
SERVING SIDE:
  Online API:
    redis.get(f"customer:{cid}:avg_7d")  # ← computed how?
    # different code path, different windowing logic
    # different null handling
    # different join semantics
  → silent skew → model performs worse in prod than test
```

### With Feature Store (skew eliminated)

```python
# ONE definition (used by both training and serving)
@feature_view(
    entities=["customer_id"],
    ttl=timedelta(days=7),
    source=transactions_source,
)
def customer_features(transactions: DataFrame) -> DataFrame:
    return transactions.groupby("customer_id").agg(
        avg_7d=("amount", lambda x: x.tail(7).mean()),
        count_7d=("txn_id", "count"),
    )

# Training: Feast applies this to historical data with point-in-time
# Serving: Feast applies same logic + serves from online store
# RESULT: identical features, no skew
```

### Detection: Skew Monitoring

แม้ใช้ FS แล้ว ยังต้อง monitor:

```python
# Compute features both ways for sample
def detect_skew():
    sample_entities = sample_recent_predictions(n=1000)
    
    online_features = fs.get_online_features(sample_entities)
    offline_features = fs.get_historical_features(
        entity_df=sample_entities_with_timestamp
    )
    
    # Compare distributions
    for feature in feature_names:
        psi = population_stability_index(
            online_features[feature],
            offline_features[feature]
        )
        if psi > 0.1:
            alert(f"Skew detected on {feature}: PSI={psi}")
```

---

## 5. Feast Architecture (Open Source Reference)

### Components

```
┌──────────────────────────────────────────────────────────┐
│                   FEAST CLI / SDK                        │
│   feast apply / get_historical / get_online              │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│              REGISTRY (metadata DB)                      │
│  • Feature views, entities, sources                      │
│  • Stored in Postgres / GCS / S3                         │
└──────────────────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌────────┐    ┌────────┐    ┌────────┐
   │OFFLINE │    │MATERIA-│    │ ONLINE │
   │  STORE │    │ LIZE   │    │  STORE │
   │        │    │ JOB    │    │        │
   │ BQ /   │ ─► │ (Spark/│ ─► │Bigtable│
   │Iceberg │    │  Beam) │    │/Redis  │
   └────────┘    └────────┘    └────────┘
        ▲                           ▲
        │ get_historical            │ get_online
        │ (training)                │ (serving)
        │                           │
   ┌─────────────────────────────────────┐
   │       USER CODE (Training/Serving)  │
   └─────────────────────────────────────┘
```

### Feature Definition Example (Feast)

```python
from feast import Entity, FeatureView, Field
from feast.types import Float32, Int64
from datetime import timedelta

# 1. Define entity
customer = Entity(name="customer_id", join_keys=["customer_id"])

# 2. Define source (where data lives)
transactions_source = BigQuerySource(
    table="warehouse.silver.transactions",
    timestamp_field="event_time",
)

# 3. Define feature view
customer_stats = FeatureView(
    name="customer_stats",
    entities=[customer],
    ttl=timedelta(days=30),
    schema=[
        Field(name="avg_purchase_7d", dtype=Float32),
        Field(name="txn_count_24h", dtype=Int64),
    ],
    source=transactions_source,
    online=True,
)
```

### Get Features (Training)

```python
from feast import FeatureStore

store = FeatureStore(repo_path=".")

# Entity DF: which entities + when (event time)
entity_df = pd.DataFrame({
    "customer_id": [101, 102, 103],
    "event_timestamp": [
        "2026-04-01 10:00:00",
        "2026-04-01 11:00:00",
        "2026-04-01 12:00:00",
    ]
})

# Get features as of event_timestamp (point-in-time correct)
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "customer_stats:avg_purchase_7d",
        "customer_stats:txn_count_24h",
    ],
).to_df()
```

### Get Features (Serving)

```python
# Latest features for online prediction
online_features = store.get_online_features(
    features=[
        "customer_stats:avg_purchase_7d",
        "customer_stats:txn_count_24h",
    ],
    entity_rows=[{"customer_id": 101}]
).to_dict()
```

---

## 6. Feature Store Comparison (2026)

### Feast (OSS)

**Pros**:
- 100% open source
- Lightweight (Python)
- Pluggable backends (BQ/Snowflake offline, Redis/DynamoDB online)
- Best for self-hosted

**Cons**:
- ไม่ทำ feature transformation (ต้อง pre-compute เอง)
- ไม่มี UI catalog ในตัว
- Operational overhead self-host

### Tecton (Commercial → Acquired by Databricks 2025)

**Pros**:
- End-to-end (compute + serve + monitor)
- Real-time feature transformations
- Production SLAs
- After 2025 → ผูกกับ Databricks

**Cons**:
- ราคาแพง
- Vendor lock (post Databricks acquisition)

### Databricks Feature Store

**Pros**:
- Native Databricks integration
- Lineage built-in
- Unity Catalog integration

**Cons**:
- Lock-in to Databricks

### Vertex AI Feature Store (GCP)

**Pros**:
- Managed on GCP
- Online + offline served
- Integrates with Vertex pipelines

**Cons**:
- ราคาแพงกว่า self-host Feast
- ต้อง buy-in Vertex ecosystem

### Build vs Buy Decision

| ขนาด ML team | คำแนะนำ |
|---|---|
| 1–3 data scientists | ไม่ต้องมี FS — ใช้ dbt + simple lookup pattern |
| 4–10 | **Feast** + your existing data warehouse |
| 10–30 | Feast แบบ self-host หรือ Vertex/Databricks managed |
| 30+ | Custom build (Uber Michelangelo style) หรือ Tecton |

---

## 7. Feature Definition Best Practices

### Naming Convention

```
[entity]_[aggregation]_[window]_[unit]

Examples:
  customer_avg_purchase_7d
  customer_count_login_24h
  product_views_30d_count
```

### Versioning

```yaml
# Bad
customer_features:
  features:
    - avg_purchase  # which window? changes silently

# Good
customer_features_v3:
  features:
    - avg_purchase_7d_v2  # explicit window + version
    - avg_purchase_30d_v1
```

### Documentation Requirements

ทุก feature ต้องมี:
- **Owner** (team / individual)
- **Description** (business meaning)
- **Source** (where data comes from)
- **Logic** (how computed)
- **Freshness SLA** (how often updated)
- **Online / Offline only** flag
- **PII flag**

### Anti-patterns

❌ **Feature drift in definition**:
```python
# v1: window=7d
# v1.1 (silent change): window=14d  ← breaks downstream
```

✅ **Versioned changes**:
```python
# v1: window=7d (preserved for old models)
# v2: window=14d (new feature, new name)
```

---

## 8. Online Store Decisions

### Latency Requirements

| Use case | Required latency | Store choice |
|---|---|---|
| Display recommendations | < 100ms | Bigtable, DynamoDB, Redis |
| Real-time fraud | < 50ms | Redis, in-memory |
| Search ranking | < 30ms | Redis cluster |
| Personalization | < 200ms | Bigtable + cache |

### Cost Comparison (Online Stores)

| Store | $/GB/month | Latency | Best for |
|---|---|---|---|
| Redis (managed) | $50–100 | < 1ms | hot, small |
| DynamoDB | $0.25 + ops | 5–10ms | scalable, pay-per-use |
| Bigtable | $0.17 | 5–20ms | very large scale |
| pgvector | varies | 10–50ms | already have Postgres |
| Cassandra | $0.10 | 5–10ms | self-managed |

### Sync Strategies (Offline → Online)

#### Strategy A: Scheduled Batch Sync
```
Daily 2am: Spark job reads Iceberg → writes Bigtable
```
- **Pro**: simple, predictable
- **Con**: stale by up to 24h

#### Strategy B: CDC + Stream
```
Iceberg snapshot change → CDC event → Beam → Bigtable
```
- **Pro**: near real-time
- **Con**: complex, watermark issues

#### Strategy C: Dual Write
```
Stream processor writes both Bigtable (online) + Iceberg (offline) atomically
```
- **Pro**: lowest latency, single source of truth
- **Con**: requires transactional write across stores (hard)

---

## 9. Streaming Feature Engineering Patterns

### Pattern A: Tumbling Window
```
[--- 1min ---][--- 1min ---][--- 1min ---]
   count          count         count
```

### Pattern B: Sliding Window
```
[----- 5min -----]
       [----- 5min -----]
              [----- 5min -----]
   updates every 1min
```

### Pattern C: Session Window
```
events: x x x      x x          x
        |session1| |s2|         |s3|
        (gap > 30min = new session)
```

### Beam Pattern Example

```python
# Compute "purchases in last 5 min" as streaming feature
purchases = (p
    | "Read" >> beam.io.ReadFromPubSub(topic="purchases")
    | "Window" >> beam.WindowInto(
          window.SlidingWindows(size=300, period=60))  # 5min sliding, 1min slide
    | "ByCustomer" >> beam.GroupBy("customer_id")
    | "Count" >> beam.CombineValues(beam.combiners.CountCombineFn())
    | "WriteOnlineFS" >> beam.ParDo(WriteToBigtable())
)
```

---

## 10. Common Mistakes ที่พบในองค์กร

### Mistake 1: ใช้ Online Store เป็น Source of Truth
**ผิด**: เก็บ feature ใน Redis อย่างเดียว → train โดย dump Redis
**ถูก**: Offline (Iceberg) เป็น source of truth, Online เป็น mirror

### Mistake 2: Online ≠ Offline
**ผิด**: คน A เขียน online sync, คน B เขียน batch — logic ต่าง
**ถูก**: ใช้ Feature Store ที่บังคับ definition เดียว + monitor skew

### Mistake 3: ไม่มี TTL ใน Online Store
**ผิด**: Online store เก็บ value เก่าตลอดไป → memory เต็ม
**ถูก**: TTL ทุก feature (Feast `ttl=timedelta(days=30)`)

### Mistake 4: ไม่ Version Feature
**ผิด**: เปลี่ยน logic ของ `avg_7d` → ทุก model ที่ใช้พังพร้อมกัน
**ถูก**: feature ใหม่ = version ใหม่ (`avg_7d_v2`), retire เก่าเมื่อ migrate ครบ

### Mistake 5: Ignore Backfill Cost
**ผิด**: Add new feature → backfill historical = 1 ปี = $$$$
**ถูก**: คิด backfill cost ตอน design + จำกัด history

### Mistake 6: ลืม Test Skew
**ผิด**: ใช้ FS = ปลอดภัย — ไม่ตรวจ
**ถูก**: Schedule skew monitoring + alert

---

## 11. Reference Implementation: Feast บน GCP

### Setup

```bash
pip install feast[gcp,bigquery,redis]

feast init my_repo
cd my_repo
```

### feature_store.yaml

```yaml
project: my_repo
registry: gs://my-bucket/feast/registry.db
provider: gcp

offline_store:
  type: bigquery
  dataset: warehouse_features

online_store:
  type: bigtable
  project_id: my-project
  instance: feast-instance
```

### Feature Definitions (`features.py`)

```python
from feast import Entity, FeatureView, Field, BigQuerySource
from feast.types import Float32, Int64
from datetime import timedelta

customer = Entity(name="customer_id", join_keys=["customer_id"])

txn_source = BigQuerySource(
    table="my-project.warehouse.silver_transactions",
    timestamp_field="event_time",
)

customer_stats_v3 = FeatureView(
    name="customer_stats_v3",
    entities=[customer],
    ttl=timedelta(days=30),
    schema=[
        Field(name="avg_purchase_7d", dtype=Float32),
        Field(name="txn_count_24h", dtype=Int64),
    ],
    source=txn_source,
    online=True,
    tags={"owner": "risk_team", "pii": "false"},
)
```

### Apply + Materialize

```bash
# Register
feast apply

# Materialize past 1 year to online store
feast materialize 2025-05-01T00:00:00 2026-05-01T00:00:00

# Or schedule incremental
feast materialize-incremental $(date -u +%Y-%m-%dT%H:%M:%S)
```

### Use in Training

```python
from feast import FeatureStore
import pandas as pd

store = FeatureStore(repo_path=".")

entity_df = pd.read_sql("""
    SELECT customer_id, event_time AS event_timestamp, is_fraud
    FROM warehouse.fraud_labels
    WHERE event_time BETWEEN '2026-01-01' AND '2026-04-30'
""", conn)

training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "customer_stats_v3:avg_purchase_7d",
        "customer_stats_v3:txn_count_24h",
    ],
).to_df()

# Now train
X = training_df[["avg_purchase_7d", "txn_count_24h"]]
y = training_df["is_fraud"]
model.fit(X, y)
```

### Use in Serving

```python
# In your prediction service
from feast import FeatureStore

store = FeatureStore(repo_path="gs://my-bucket/feast/")

def predict(customer_id: int):
    features = store.get_online_features(
        features=[
            "customer_stats_v3:avg_purchase_7d",
            "customer_stats_v3:txn_count_24h",
        ],
        entity_rows=[{"customer_id": customer_id}],
    ).to_dict()
    
    prediction = model.predict([[
        features["avg_purchase_7d"][0],
        features["txn_count_24h"][0],
    ]])[0]
    return prediction
```

---

## 12. Decision Tree: ต้องมี FS มั้ย?

```
Q1: มี ML model ใน production มากกว่า 3 ตัวมั้ย?
  No  → ไม่ต้องมี (ใช้ dbt + lookup pattern)
  Yes → Q2

Q2: model ใช้ feature ซ้ำกันมั้ย?
  No  → ยังไม่ต้องเร่ง
  Yes → Q3

Q3: ต้องการ online inference?
  No  → batch FS เพียงพอ (= ใช้ Iceberg + dbt + table)
  Yes → Q4

Q4: ต้องการ point-in-time correctness?
  No  → simple key-value cache เพียงพอ
  Yes → ต้องมี Feature Store จริงจัง (Feast)

Q5: ขนาด team / model count?
  Small (< 5 model) → Feast self-host
  Medium (5-20)     → Feast managed หรือ Vertex AI FS
  Large (20+)       → Custom build หรือ Tecton/Databricks FS
```

---

## 13. Cheat Sheet

### Q: "Feature Store แก้ปัญหาอะไร?"
> "3 ปัญหา: training-serving skew, point-in-time correctness, และ feature reusability ข้าม model"

### Q: "Online vs Offline FS ต่างกันยังไง?"
> "Offline เก็บใน data lake (Iceberg) สำหรับ training — bulk read + time travel
> Online เก็บใน key-value store (Bigtable/Redis) สำหรับ serving — ms-latency lookup
> ใช้ definition เดียวกัน sync จาก offline → online"

### Q: "Point-in-Time Join คืออะไร?"
> "การ join feature เข้ากับ event โดยใช้ feature value ที่ถูกต้อง 'as of' event time
> ป้องกัน data leakage ที่จะใช้ future information ตอน training"

### Q: "Build vs Buy?"
> "ขนาด < 5 model: ใช้ Feast OSS
> ขนาด 5-20: managed (Vertex/Databricks)
> ขนาด 20+: custom (เหมือน Uber Michelangelo)"

---

## เอกสารต่อ

- [04_Model_Monitoring.md](04_Model_Monitoring.md) — drift detection, performance tracking
- [02_MLOps_Lifecycle.md](02_MLOps_Lifecycle.md) — full lifecycle
