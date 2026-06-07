# Real-Time Architecture — Deep Dive

> Flink, Materialize, RisingWave, streaming SQL, exactly-once
> ของจริงในระดับ enterprise ที่ The-1 / banking ใช้

---

## 1. ทำไม Real-Time มาแรงปี 2026

### Business Drivers

```
- Customer expects instant gratification (Uber, Grab)
- Fraud detection: milliseconds matter
- Real-time personalization: in-session
- IoT: continuous streams
- AI/ML: online features for inference
```

### Tech Drivers

```
- Streaming engines mature (Flink, Beam, Spark Streaming)
- Streaming databases emerging (RisingWave, Materialize)
- Cloud streaming infrastructure cheap (Pub/Sub, Kinesis)
- Iceberg + streaming compatibility
- Cost: real-time + batch unified pipelines now possible
```

---

## 2. The Real-Time Spectrum

### Latency Tiers

```
< 1ms    → Memory caches, in-process
1-10ms   → Online feature stores, HTTP calls
10-100ms → Stream processing (Kafka → Flink → output)
100ms-1s → Materialized views, near-real-time
1s-1min  → Micro-batch (Spark Structured Streaming)
1-5min   → Mini-batch
5-60min  → "Real-time" by some definitions
1hr+     → Batch
```

### Reality Check

> "Real-time" จริงๆ คืออะไร — ถามใหม่:
> 
> - **What's the latency budget?** (specific SLA)
> - **What happens if late?** (cost of lateness)
> - **Acceptable rate of late events?**

80% ของ "real-time" ที่ business ขอ = 5-15 minutes พอ

---

## 3. Streaming Architecture Patterns

### Pattern 1: Lambda (legacy)

```
                ┌─── BATCH (Spark daily) ───────┐
Events ─────────┤                                 ├─→ Serving
                └─── STREAMING (Flink) ──────────┘
                
Two pipelines, two codebases
```

**Pros**: Each pipeline optimized for its purpose
**Cons**: 2x maintenance, logic divergence

### Pattern 2: Kappa (modern default)

```
              ┌──── STREAMING (Flink) ────┐
Events ───────┤                             ├─→ Serving
              └──── Reprocess via replay ──┘

Single codebase
```

**Pros**: Single source of truth, simpler
**Cons**: Streaming engine must handle backfill

### Pattern 3: Unified Batch+Stream (2026)

```
Same SQL/code:
   - Run on bounded data → batch mode
   - Run on unbounded data → stream mode

Tools: Flink SQL, Beam, Spark Structured Streaming, RisingWave
```

**Pros**: Best of both
**Cons**: Need engine that supports

### Pattern 4: Streaming Database as Sink

```
[Source] → [Stream processor] → [Streaming DB] → [Apps query]

Streaming DB = always-fresh materialized views
Apps see "current state" without complex pipeline
```

Examples:
- Kafka → Flink → RisingWave
- Kafka → Flink → Materialize
- DB CDC → RisingWave directly

---

## 4. Apache Flink Deep

### Why Flink Wins for Complex Streaming

- True streaming (event-by-event, not micro-batch)
- Stateful operators (TB-scale state)
- Exactly-once guarantees (with proper sinks)
- Event time + watermarks (built-in)
- CEP (Complex Event Processing)
- SQL + DataStream + Table APIs

### Flink Architecture

```
┌─────────────────────────────────────────┐
│  JobManager (coordinator)                │
│  - Schedules tasks                       │
│  - Checkpointing coordinator             │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │ Task   │ │ Task   │ │ Task   │
   │Manager1│ │Manager2│ │Manager3│
   └────────┘ └────────┘ └────────┘
   (workers, run subtasks in parallel)
```

### Stateful Processing

```java
public class CountByUser extends KeyedProcessFunction<String, Event, Tally> {
    // State: count per user
    private ValueState<Long> countState;
    
    @Override
    public void open(Configuration params) {
        countState = getRuntimeContext().getState(
            new ValueStateDescriptor<>("count", Long.class, 0L)
        );
    }
    
    @Override
    public void processElement(Event event, Context ctx, Collector<Tally> out) throws Exception {
        Long count = countState.value();
        count++;
        countState.update(count);
        out.collect(new Tally(event.getUserId(), count));
    }
}
```

### Watermarks

```java
WatermarkStrategy<Event> strategy = WatermarkStrategy
    .<Event>forBoundedOutOfOrderness(Duration.ofMinutes(5))
    .withTimestampAssigner((event, ts) -> event.getEventTime());

DataStream<Event> stream = source.assignTimestampsAndWatermarks(strategy);
```

### Windowing

```java
stream
    .keyBy(Event::getUserId)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .aggregate(new CountAggregator());
```

### Flink SQL (most teams use this in 2026)

```sql
CREATE TABLE clicks (
    user_id STRING,
    event_time TIMESTAMP(3),
    url STRING,
    WATERMARK FOR event_time AS event_time - INTERVAL '5' MINUTE
) WITH (
    'connector' = 'kafka',
    'topic' = 'clicks',
    'properties.bootstrap.servers' = 'kafka:9092',
    'format' = 'json'
);

SELECT 
    user_id,
    TUMBLE_START(event_time, INTERVAL '5' MINUTE) AS window_start,
    COUNT(*) AS click_count
FROM clicks
GROUP BY 
    user_id,
    TUMBLE(event_time, INTERVAL '5' MINUTE);
```

### Exactly-Once Sinks

```sql
-- Kafka transactional sink
CREATE TABLE alert_topic (
    user_id STRING,
    alert_type STRING,
    detected_at TIMESTAMP(3)
) WITH (
    'connector' = 'kafka',
    'topic' = 'alerts',
    'sink.delivery-guarantee' = 'exactly-once',
    'sink.transactional-id-prefix' = 'alert-job-'
);

-- Iceberg (atomic snapshot writes)
CREATE TABLE silver_clicks (...) WITH (
    'connector' = 'iceberg',
    'catalog-name' = 'warehouse',
    ...
);
```

---

## 5. Streaming Databases (2026)

### Why Streaming Databases

```
Traditional approach:
  Kafka → Flink (compute) → Postgres (serve)
  3 systems to manage
  Latency between layers

Streaming DB:
  Kafka → RisingWave (compute + serve)
  1 system, queries "current state"
  Materialized views auto-updating
```

### RisingWave

#### Setup
```bash
docker run -p 4566:4566 risingwavelabs/risingwave:latest
```

#### Pseudo-Postgres SQL
```sql
-- Create source from Kafka
CREATE SOURCE click_source (
    user_id VARCHAR,
    url VARCHAR,
    event_time TIMESTAMPTZ
) WITH (
    connector = 'kafka',
    topic = 'clicks',
    properties.bootstrap.server = 'kafka:9092'
) FORMAT PLAIN ENCODE JSON;

-- Materialized view (auto-updates!)
CREATE MATERIALIZED VIEW user_click_count AS
SELECT 
    user_id,
    COUNT(*) AS total_clicks,
    MAX(event_time) AS last_click
FROM click_source
GROUP BY user_id;

-- Query as if Postgres
SELECT * FROM user_click_count WHERE user_id = '12345';
-- Returns latest count, sub-second latency
```

#### Built-in CDC Connectors (no Debezium needed!)

```sql
-- Direct from Postgres CDC
CREATE SOURCE pg_orders WITH (
    connector = 'postgres-cdc',
    hostname = 'pg-host',
    port = '5432',
    username = 'admin',
    password = '...',
    database.name = 'shop',
    table.name = 'orders'
);

-- Direct from MySQL, MongoDB, SQL Server too
```

#### Vector Support (2026)
```sql
-- Embedding column
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR,
    embedding VECTOR(1536)
);

-- Vector similarity in MV
CREATE MATERIALIZED VIEW similar_products AS
SELECT *, 
    embedding <=> (SELECT embedding FROM products WHERE id = $1) AS distance
FROM products
ORDER BY distance
LIMIT 10;
```

### Materialize

#### Different from RisingWave

```
RisingWave: Apache 2.0, Postgres-compatible
Materialize: BSL (not fully open), wire-Postgres-compatible
```

#### Setup
```bash
# Cloud or self-host
materialize cloud signup
```

#### SQL
```sql
-- Source
CREATE SOURCE clicks FROM KAFKA BROKER 'kafka:9092' TOPIC 'clicks'
    FORMAT BYTES;

-- Auto-incremental MV
CREATE MATERIALIZED VIEW user_metrics AS
SELECT 
    user_id,
    COUNT(*) AS clicks,
    AVG(amount) AS avg_amount
FROM (
    SELECT 
        cast(payload::jsonb -> 'user_id' as text) AS user_id,
        cast(payload::jsonb -> 'amount' as numeric) AS amount
    FROM clicks
)
GROUP BY user_id;

-- Subscribe to changes (real-time)
SUBSCRIBE TO user_metrics;
```

### RisingWave vs Materialize

| | RisingWave | Materialize |
|---|---|---|
| License | Apache 2.0 | BSL |
| CDC sources | ✅ Built-in (PG, MySQL, Mongo, SQL Server) | PG only native |
| Kafka | ✅ | ✅ |
| Vector / AI | ✅ Built-in | ❌ |
| Performance | Good | Good |
| Maturity | Newer | More mature |

**2026 trend**: RisingWave gaining due to multi-source CDC + AI features

---

## 6. CDC (Change Data Capture)

### Why CDC

Without CDC: Pull every N minutes (lag, expensive)
With CDC: Stream every change (real-time, cheap)

### CDC Tools

#### Debezium (most common)
```yaml
# Connector config
{
  "name": "orders-cdc",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.dbname": "shop",
    "database.server.name": "shop_server",
    "table.include.list": "public.orders",
    "plugin.name": "pgoutput"
  }
}
```

→ Reads PG WAL (Write-Ahead Log) → Kafka events

#### Native (less infra)
- RisingWave CDC (no Debezium needed)
- Flink CDC (Apache 2.0 alternative)

### Snapshot + Stream Pattern

```
1. Initial snapshot: read full table
2. Switch to streaming: read WAL changes
3. Forever: append new changes

Result: real-time replica with full history
```

### Schema Evolution Challenges

```
Table column added → CDC needs to handle
- Debezium: requires schema registry update
- Some tools: silent failure
- Use Schema Registry + compatibility rules
```

---

## 7. Production Patterns

### Pattern 1: CDC → Stream → Iceberg + Online FS

```
[Source DB]
    ↓ Debezium CDC
[Kafka]
    ↓ Flink (transform)
    ├──→ [Iceberg Bronze] (offline, batch reads)
    ├──→ [Iceberg Silver]  (cleansed)
    └──→ [Bigtable/Redis] (online lookup)
```

**Use case**: Real-time fraud, real-time CRM, online ML features

### Pattern 2: Pub/Sub → Beam → Multiple Sinks

```
[App events]
    ↓ Pub/Sub
[Dataflow (Beam)]
    ├─→ [BigQuery] (analytics)
    ├─→ [Bigtable] (lookup)
    └─→ [GCS Iceberg] (archival)
```

### Pattern 3: Streaming MV for Apps

```
[Multiple sources]
    ↓
[RisingWave]
    ├── Materialized View 1 (user metrics)
    ├── Materialized View 2 (product trends)
    └── Materialized View 3 (real-time KPI)
       ↑
   [Frontend queries MVs directly]
```

### Pattern 4: Streaming SQL on Iceberg

```
Iceberg: streaming-write supported
Read with Flink/Spark Structured Streaming

[Source] → [Flink] → [Iceberg]
                       ↓
              [Spark batch + streaming reads]
              [Trino interactive queries]
```

---

## 8. Backfill in Streaming Systems

### The Hard Problem

```
You have a streaming pipeline running for 6 months
Need to:
- Add new feature
- Reprocess all historical data
- Update output

Issue: streaming engine designed for "now", not "past"
```

### Solutions

#### Option 1: Replay Source
```
Kafka with long retention (30+ days):
  Reset consumer offset to beginning
  Replay through pipeline
  Outputs auto-corrected
  
Issue: limited by Kafka retention
```

#### Option 2: Iceberg Source
```
Iceberg has snapshots = effectively unlimited "history"
Stream from oldest snapshot
Process all events
```

#### Option 3: Hybrid Backfill
```
Run batch job on historical data (Spark)
Output to same sink (Iceberg)
Streaming pipeline handles new data
Eventual consistency
```

#### Option 4: Dual Pipeline
```
Old streaming version: keep running
New version: process backfill data
Switch readers to new version
Sunset old
```

---

## 9. Latency vs Cost Trade-offs

### Latency Bands and Costs

```
< 1s latency:
  - Stream processor 24/7 (Flink, Dataflow)
  - In-memory state
  - Cost: HIGH (always-on compute)

1-15s latency:
  - Micro-batch (Spark Structured Streaming)
  - Acceptable for most "real-time"
  - Cost: MEDIUM

5-60min latency:
  - Mini-batch (Spark / Beam scheduled)
  - 80% of business needs
  - Cost: LOW

1hr+ latency:
  - Standard batch
  - Cost: LOWEST
```

### Tiered Approach (recommended)

```
Tier 1 (Hot, < 5 sec):  
  10% of data, 80% of business value
  Use streaming
  Accept high cost

Tier 2 (Warm, 5-60 min):
  30% of data, 15% of value
  Use micro-batch
  Medium cost

Tier 3 (Cold, T+1):
  60% of data, 5% of value
  Standard batch
  Low cost
```

---

## 10. Streaming Operations

### Key Metrics to Monitor

```
Throughput:
- Events/sec processed
- Bytes/sec
- Records lag (consumer behind producer)

Latency:
- End-to-end (event time → output time)
- Processing time (within engine)
- Watermark progression

State:
- State size (GB)
- Checkpoint duration
- Checkpoint failures

Resources:
- CPU, memory per task manager
- GC pauses
- Network I/O

Errors:
- Failed records
- DLQ count
- Checkpoint failures
- Restarts
```

### Failure Modes

#### Mode 1: Slow Source
```
Symptom: lag growing
Diagnosis: source production rate < consumption
Fix:
- Scale source
- Or accept lag
- Backpressure flows back
```

#### Mode 2: Slow Sink
```
Symptom: backpressure, memory pressure
Diagnosis: sink can't keep up with stream
Fix:
- Scale sink
- Async writes
- Buffering with bound
```

#### Mode 3: State Explosion
```
Symptom: memory full, OOM
Diagnosis: state grows unboundedly
Fix:
- TTL on state
- Watermark cleanup
- Smaller windows
```

#### Mode 4: Hot Keys
```
Symptom: one task slow, others idle
Diagnosis: data skew (one user/partition huge)
Fix:
- Salting (hash key + random)
- Pre-aggregation
- Partition strategy
```

#### Mode 5: Watermark Stuck
```
Symptom: no output despite events flowing
Diagnosis: idle source partitions blocking watermark
Fix:
- Idle timeout configuration
- Source heartbeat events
- Per-partition watermarks
```

---

## 11. Real-Time ML / AI Integration

### Online Feature Computation

```
Stream events
    ↓ Flink/Beam
Update online feature store (Bigtable/Redis)
    ↓
Inference service reads features
    ↓
Predictions in real-time
```

### Example: Real-Time Fraud Detection

```
Event: card transaction
    ↓
Flink computes features:
  - txn_count_1min
  - amount_vs_avg
  - geo_change_speed
    ↓
Write to online FS
    ↓
ML model (deployed inline) predicts
    ↓
If fraud_score > threshold:
  Block transaction
  Alert customer
```

### Real-Time RAG (emerging)

```
Documents updated continuously
    ↓
Re-embed changed documents
    ↓
Update vector DB
    ↓
RAG queries get fresh context

Tools:
- Pinecone has this
- Weaviate streaming updates
```

---

## 12. Choosing the Right Tool (2026)

### Decision Tree

```
Latency need?
  < 100ms, complex state → Flink
  Latency-tolerant, want SQL → Materialize/RisingWave
  Already using Spark → Spark Structured Streaming
  GCP-native, batch+stream → Dataflow (Beam)

State complexity?
  Simple aggregations → any
  Complex (CEP, sessions) → Flink
  Just MVs → RisingWave/Materialize

Scale?
  TB-scale state → Flink
  Smaller → RisingWave/Materialize
  Massive throughput → Flink/Dataflow

Team skill?
  Java/Scala expert → Flink
  SQL only → RisingWave/Materialize
  Python → Beam, Spark

Already using?
  Kafka → any (especially Kafka Streams for embedded)
  Postgres → Materialize/RisingWave (Postgres-compat)
  GCP → Dataflow + BigQuery
```

---

## 13. Cheat Sheet

### Q: "เลือก streaming engine ไหน?"
> "Flink: complex state, lowest latency, best for stateful
> Spark Structured Streaming: unified with batch, micro-batch
> Beam/Dataflow: GCP managed
> RisingWave: SQL-first, materialized views
> Materialize: similar to RW but BSL"

### Q: "RisingWave vs Flink?"
> "Flink: more flexible, more features, harder to use
> RisingWave: SQL-first, simpler ops, materialized views auto
> ใช้ Flink เมื่อต้อง custom logic, RisingWave สำหรับ SQL workflows"

### Q: "Lambda vs Kappa?"
> "Lambda (legacy): 2 codebases, divergence pain
> Kappa: streaming-only, replay for backfill
> 2026: Unified Batch+Stream (Flink, Beam) — same code both modes"

### Q: "CDC ใช้ตัวไหน?"
> "Debezium: standard, mature, requires Kafka Connect
> Flink CDC: Apache 2.0, integrated
> RisingWave native: simplest if using RisingWave
> Choice: depends on existing infra"

### Q: "Backfill streaming pipeline ยังไง?"
> "Hard problem — engineered approaches:
> 1. Long Kafka retention (30+ days) — replay from offset
> 2. Iceberg as source — read snapshot history
> 3. Batch backfill + streaming forward
> 4. Dual pipeline migration"

---

## Sources

- [Apache Flink Documentation](https://flink.apache.org/)
- [Flink CEP Guide - Kai Waehner](https://www.kai-waehner.de/blog/2026/04/14/complex-event-processing-cep-with-apache-flink-what-it-is-and-when-not-to-use-it/)
- [Understanding Apache Flink Event Time and Watermarks](https://www.decodable.co/blog/understanding-apache-flink-event-time-and-watermarks)
- [Materialize vs RisingWave Comparison](https://materialize.com/guides/materialize-vs-risingwave/)
- [Materialize Alternatives 2026 - RisingWave](https://risingwave.com/blog/materialize-alternatives-2026/)
- [Incremental Materialized Views Complete Guide 2026](https://risingwave.com/blog/incremental-materialized-views-complete-guide/)
- [Streaming Database Landscape 2026 - RisingWave](https://risingwave.com/blog/streaming-database-landscape-2026-complete-guide/)
- [RisingWave GitHub](https://github.com/risingwavelabs/risingwave)
- [Confluent Flink Documentation](https://docs.confluent.io/cloud/current/flink/concepts/timely-stream-processing.html)
