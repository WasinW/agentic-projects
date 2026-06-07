# Streaming Patterns — Deep Dive

> Watermarking, exactly-once, stateful processing, Kappa, CEP
> ที่แยก streaming engineer มืออาชีพออกจาก batch engineer

---

## 1. Streaming Fundamentals — แตกต่างจาก Batch อย่างไร

### Batch Mental Model

```
"Read all data → process → write all output"
- Bounded data
- One-shot
- High latency, predictable
```

### Streaming Mental Model

```
"Data is unbounded, infinite event stream
 Process events as they arrive
 Always running"
- Unbounded data
- Continuous
- Low latency, but complex
```

### Why Streaming is Hard

| Problem | Description |
|---|---|
| **Out-of-order events** | Network delay → events arrive in wrong order |
| **Late data** | Events from yesterday arrive today |
| **Exactly-once** | Process each event exactly once despite failures |
| **State management** | Aggregations need state across events |
| **Backpressure** | Source produces faster than sink can consume |
| **Schema evolution** | Schema changes mid-stream |
| **Replay** | How to recompute history |

---

## 2. Time Semantics — Critical Concept

### 3 Times in Streaming

```
Event Time:      เวลาที่เหตุการณ์เกิดจริง (in event payload)
Ingestion Time:  เวลาที่ event เข้า system
Processing Time: เวลาที่ engine handle event
```

### Why Different Times Matter

```
Event happens:     12:00:00 (event_time)
                    ↓ network delay
Arrives at Kafka:  12:00:30 (ingestion_time)
                    ↓ queue delay
Processed:         12:00:45 (processing_time)
```

If you aggregate by **processing_time**: you'll group based on when system saw it (wrong)
If you aggregate by **event_time**: correct semantically (but harder)

### Best Practice

> **Always use event_time for business logic**

ตัวอย่างที่ผิด:
```python
# Bad: window by processing_time
events.groupBy(window(current_timestamp(), "5 minutes")).count()
# Late events go to wrong window!
```

ถูก:
```python
# Good: window by event_time
events.groupBy(window(col("event_time"), "5 minutes")).count()
```

---

## 3. Watermarks — Heart of Streaming

### What is Watermark

> "All events with timestamp < W have arrived. Safe to compute results for windows ≤ W"

```
Stream:  [09:00] [09:15] [09:10] [09:20] [09:25] [09:14] ...
                         ↑ out of order
Watermark advances: max(event_times) - allowed_lateness
```

### Configuration Example (Spark)

```python
events_with_watermark = events \
    .withWatermark("event_time", "10 minutes")
    # Tolerate up to 10 min late events

windowed_counts = events_with_watermark \
    .groupBy(
        window("event_time", "5 minutes"),
        "country"
    ) \
    .count()
```

### How Watermark Drives Output

```
Time: 09:00 ─── 09:05 ─── 09:10 ─── 09:15 ─── 09:20

Window [09:00-09:05]:
  Events arrive
  Watermark < 09:05 → window not closed yet
  At watermark = 09:15 (09:05 + 10 min lateness):
     Window closes, emit final count
     Late events (event_time < 09:05 arriving after watermark 09:15) → DROPPED
```

### Trade-off

```
Long watermark (high lateness tolerance):
  ✅ Captures late events
  ❌ High latency to output (must wait)
  ❌ More state (kept longer)

Short watermark:
  ✅ Low latency
  ❌ Drops late events
```

### Late Data Handling Strategies

#### Strategy 1: Drop (default)
Events older than watermark → discarded
- Simple, low memory
- Some events lost

#### Strategy 2: Side output (Flink)
Late events go to separate stream
```python
late_events = events.getSideOutput(late_data_tag)
late_events.writeAsText("late_data.log")
```

#### Strategy 3: Update earlier results (allowed lateness)
- Re-fire window with new event included
- More complex sink semantics needed

---

## 4. Windowing — Group Events by Time

### 4 Window Types

#### Tumbling Windows
```
Fixed size, non-overlapping
[----- 5min -----][----- 5min -----][----- 5min -----]
```
```python
groupBy(window("event_time", "5 minutes"))
```

#### Sliding Windows
```
Fixed size, overlapping (slide < size)
[----- 5min -----]
       [----- 5min -----]
              [----- 5min -----]
```
```python
groupBy(window("event_time", "5 minutes", "1 minute"))
# Size 5min, slide 1min
```

#### Session Windows
```
Variable size, gap-based
[event event event] [-30min gap-] [event event] 
   ↑ session 1                       ↑ session 2
```
```python
groupBy(session_window("event_time", "30 minutes"))
```

#### Global Windows (rare)
```
All events in one window — until manually triggered
Used in: complex CEP scenarios
```

### When to Use Which

| Use case | Window |
|---|---|
| 5-min metrics | Tumbling |
| Rolling 1-hour avg, updated every 1 min | Sliding |
| User session activity | Session |
| Detect pattern across all events | Global |

---

## 5. State Management

### Why State

Aggregations need to remember:
- Running counts per key
- Last seen timestamp
- Open sessions
- Joined state from another stream

### State Backends

#### Memory (default, fast)
```
Keep state in JVM heap
- Fast access
- Limited size
- Lost on crash (without checkpoint)
```

#### RocksDB (Flink default for production)
```
LSM-tree on local disk
- TB-scale state
- Persistent
- Slower than memory but durable
```

```java
// Flink
env.setStateBackend(new EmbeddedRocksDBStateBackend());
```

### State Operations

```python
# Spark Structured Streaming arbitrary state
def update_state(key, batch_iter, state):
    if state.exists:
        current = state.get
    else:
        current = {"count": 0, "sum": 0}
    
    for event in batch_iter:
        current["count"] += 1
        current["sum"] += event.amount
    
    state.update(current)
    state.setTimeoutDuration("1 hour")  # cleanup
    
    return [(key, current["count"], current["sum"])]

events.groupByKey().mapGroupsWithState(update_state)
```

### State Cleanup

State accumulates → must clean up:

#### Time-based TTL
```python
state.setTimeoutDuration("1 hour")
# State expires 1 hour after last update
```

#### Watermark-based
```python
state.setTimeoutTimestamp(watermark + 1.hour)
# State expires when watermark passes
```

#### Tombstoning
```python
if event.is_delete_signal:
    state.remove()
```

---

## 6. Exactly-Once Semantics

### What "Exactly-Once" Means

> "Despite any failures, each event affects output exactly once"

3 levels:
- **At-most-once**: events can be lost, never duplicated (rare use case)
- **At-least-once**: no loss, but duplicates possible (need dedup)
- **Exactly-once**: each event reflected exactly once

### How Flink Achieves Exactly-Once

#### Component 1: Checkpointing
```
Periodically (e.g. every 30s):
  1. Inject barrier into stream
  2. All operators snapshot state when barrier passes
  3. Save snapshot to durable storage (S3/HDFS)
  4. On failure: restore from latest checkpoint
```

#### Component 2: Two-Phase Commit (sink)
```
Phase 1: PRECOMMIT
  - Write data tentatively (in transaction)
  - Don't commit yet
  
Phase 2: COMMIT
  - Wait for checkpoint completion
  - On checkpoint complete: commit
  - On failure: abort transaction
```

#### Component 3: Replayable Source
```
Source must support seeking back (Kafka offset, file position)
On failure: rewind to last checkpointed offset
Replay events → re-process → end up with same state (deterministic)
```

### Sinks that Support Exactly-Once

| Sink | Exactly-once method |
|---|---|
| Kafka | Transactional producer |
| Iceberg | Atomic snapshot commit |
| File | Two-phase + atomic rename |
| JDBC | Idempotent upsert |
| Custom | Implement TwoPhaseCommitSinkFunction |

### Kafka Exactly-Once Pattern

```python
# Producer
producer = KafkaProducer(
    bootstrap_servers='...',
    enable_idempotence=True,           # dedupes within session
    transactional_id='unique-app-id',  # cross-session transactions
    acks='all'
)

# Consumer
consumer = KafkaConsumer(
    isolation_level='read_committed'   # only read committed transactions
)

# Process + produce in transaction
producer.init_transactions()
producer.begin_transaction()
try:
    for record in batch:
        producer.send('output_topic', process(record))
    producer.send_offsets_to_transaction(
        offsets={...},
        consumer_group_metadata=consumer.consumer_group_metadata()
    )
    producer.commit_transaction()
except:
    producer.abort_transaction()
```

---

## 7. Streaming Joins — Tricky

### Stream-to-Stream Join

```python
# Both sides are streams
clicks.join(
    impressions,
    expr("""
        clicks.user_id = impressions.user_id AND
        clicks.event_time BETWEEN impressions.event_time AND 
                                  impressions.event_time + interval 1 hour
    """)
)
```

**Challenges**:
- Need state on both sides
- Watermark on both sides
- State grows → must bound (window join)

### Stream-to-Static Join (lookup)

```python
# Stream + static dimension table
events.join(
    broadcast(dim_customers),
    "customer_id"
)
# Spark broadcasts dim_customers to all executors
# Update dim_customers manually (replay if changes)
```

### Stream-to-Slowly-Changing Join (Side Input)

```python
# Beam example
class EnrichWithCustomer(beam.DoFn):
    def process(self, event, customer_dict):
        customer = customer_dict[event['customer_id']]
        yield {**event, **customer}

result = (events
    | beam.ParDo(
        EnrichWithCustomer(),
        customer_dict=beam.pvalue.AsDict(customers_view)
    )
)
```

### Stream-to-Stream-with-Latest Join

```python
# Need: order events joined with latest customer profile at order time
# Pattern: keep customer state per customer_id, use it for order

class OrderEnricher(StatefulFunction):
    customer_state: ValueState[Customer]
    
    def process(self, event):
        if event.type == "customer_update":
            self.customer_state.update(event.customer)
        elif event.type == "order":
            customer = self.customer_state.value()
            emit({**event.order, "customer": customer})
```

---

## 8. Complex Event Processing (CEP)

### What is CEP

Detect **patterns** across events:
- "Login from country A, then login from country B within 5 min" (suspicious)
- "Click → Add to cart → Checkout abandoned" (funnel)
- "3 failed payments in a row" (fraud)

### Flink CEP Example

```java
Pattern<Event, ?> pattern = Pattern.<Event>begin("first")
    .where(e -> e.getType().equals("login"))
    .next("second")
    .where(e -> e.getType().equals("login"))
    .where((e, ctx) -> 
        !e.getCountry().equals(
            ctx.getEventsForPattern("first").iterator().next().getCountry()
        )
    )
    .within(Time.minutes(5));

// Apply
PatternStream<Event> matched = CEP.pattern(loginStream, pattern);
DataStream<Alert> alerts = matched.select(events -> new Alert(events));
```

### When CEP vs Custom Logic

| Use case | Tool |
|---|---|
| Simple aggregation | SQL/DataFrame |
| Pattern matching | CEP library |
| Complex stateful logic | Custom KeyedProcessFunction |
| Time-based correlation | CEP or windowed join |

### CEP Pitfall

CEP patterns at scale = state explosion
- Each pattern in progress = state
- Per-key, exploding combinations possible
- **Best practice**: scope patterns tightly, use TTL

---

## 9. Backpressure

### What is Backpressure

```
Source: produces 100K events/sec
Sink: writes 50K events/sec
        ↓
Buffer fills up → memory pressure → must slow source
```

### Detection

#### Flink
```
Web UI shows backpressure status per task:
  OK / LOW / HIGH
```

#### Kafka
```
Consumer lag = offset_latest - offset_consumed
Growing lag = backpressure
```

### Mitigation

#### Strategy 1: Scale up
- More parallelism in slow operator
- Larger sink

#### Strategy 2: Buffering
- Increase buffer size
- Spill to disk

#### Strategy 3: Throttle source
- Reduce source rate
- Drop low-priority events

#### Strategy 4: Async I/O
```java
// Don't block on slow API calls
AsyncDataStream.unorderedWait(
    inputStream,
    new AsyncHttpRequest(),
    1000, TimeUnit.MILLISECONDS,
    100  // max concurrent
);
```

---

## 10. Streaming SQL Patterns

### Tumbling Aggregation
```sql
-- Flink SQL
SELECT 
    TUMBLE_START(event_time, INTERVAL '5' MINUTE) AS window_start,
    country,
    COUNT(*) AS events
FROM events
GROUP BY 
    TUMBLE(event_time, INTERVAL '5' MINUTE),
    country
```

### Continuous Materialized View (Flink/RisingWave)
```sql
CREATE MATERIALIZED VIEW recent_orders AS
SELECT customer_id, COUNT(*) AS order_count, SUM(amount) AS gmv
FROM orders
WHERE event_time > NOW() - INTERVAL '1 hour'
GROUP BY customer_id;

-- Auto-updates as new orders arrive
```

### Pattern Matching (Flink SQL)
```sql
SELECT * FROM events
MATCH_RECOGNIZE (
    PARTITION BY user_id
    ORDER BY event_time
    MEASURES
        A.event_time AS login_time,
        B.event_time AS suspicious_time
    PATTERN (A B)
    DEFINE
        A AS A.event_type = 'login',
        B AS B.event_type = 'login' AND B.country <> A.country
              AND B.event_time < A.event_time + INTERVAL '5' MINUTE
)
```

---

## 11. Lambda vs Kappa Architecture

### Lambda (legacy, 2010s)

```
                ┌─── BATCH LAYER ─── (Spark daily)
Events ─────────┤                                       
                └─── SPEED LAYER ─── (Storm/Flink real-time)
                          ↓
                    Serving Layer
                  (combines both views)
```

**Pros**: 
- Batch reliable, stream fresh
- Catch late data via batch

**Cons**:
- 2 codebases (batch + stream) → maintenance hell
- Logic divergence over time

### Kappa (modern, 2018+)

```
              ┌─── STREAM LAYER ──── (Flink)
Events ───────┤        ↓
              │   Reprocess by replay
              └─── (same code on Kafka replay)
                        ↓
                  Serving Layer
```

**Pros**:
- Single codebase
- Replay = full reprocess
- Simpler

**Cons**:
- Streaming engine must handle large replays
- Requires durable + replayable source (Kafka long retention)

### 2026 Reality: Unified Batch+Stream

```
Same SQL code:
  Run on bounded data → "batch mode"
  Run on unbounded data → "streaming mode"

Tools:
  Flink: same SQL, configurable mode
  Beam: native unified
  Spark Structured Streaming: same DataFrame ops
```

**Industry direction**: forget Lambda/Kappa, use **unified processing**

---

## 12. Streaming Tools Comparison (2026)

| Tool | Strength | Weakness |
|---|---|---|
| **Flink** | Best stateful, lowest latency, true streaming | Steep learning curve |
| **Kafka Streams** | Embedded in app, simple deploy | JVM-only, less features |
| **Spark Structured Streaming** | Unified with batch, large ecosystem | Micro-batch (~100ms min) |
| **Beam (Dataflow)** | Portable across runners, GCP managed | Less stateful features than Flink |
| **RisingWave** | SQL-first streaming DB, Postgres-compat | New, smaller ecosystem |
| **Materialize** | True incremental MVs, Postgres wire | BSL license, less integrations |

### Decision Tree

```
Need < 100ms latency + complex state?
  → Flink

Already on Spark + want SQL?
  → Spark Structured Streaming

GCP shop, managed, mid-latency?
  → Dataflow (Beam)

Want streaming SQL feel like Postgres?
  → RisingWave

Embedded in microservice?
  → Kafka Streams
```

---

## 13. Common Streaming Pitfalls

### Pitfall 1: Using Processing Time
**Symptom**: late events appear in wrong window
**Fix**: use event_time + watermark

### Pitfall 2: Unbounded State
**Symptom**: memory grows forever
**Fix**: TTL, watermark cleanup, time-bounded windows

### Pitfall 3: Wrong Watermark
**Symptom**: results too late OR drop too many late events
**Fix**: profile late event distribution, set 95th percentile

### Pitfall 4: Stream-to-Static Lookup Without Refresh
**Symptom**: stale dimension data in joins
**Fix**: refresh broadcast or use side input with updates

### Pitfall 5: Hot Keys
**Symptom**: one partition slow, others idle
**Fix**: salting + post-aggregation
```python
# Add random salt to key
events.map(lambda e: ((e.key, random.randint(0, 9)), e.value))
    .groupBy("salted_key")
    .agg(...)
    .groupBy("original_key")
    .agg(...)  # combine partial results
```

### Pitfall 6: Not Idempotent Sink
**Symptom**: duplicates after recovery
**Fix**: use exactly-once sink or idempotent upsert

### Pitfall 7: Schema Changes Mid-Stream
**Symptom**: pipeline crashes when source adds column
**Fix**: schema registry + gradual rollout

---

## 14. Cheat Sheet

### Q: "Watermark คืออะไร?"
> "Watermark = 'ฉันมั่นใจว่า events เก่ากว่า X arrived แล้ว'
> เป็นกลไกที่ตัดสินว่าเมื่อไหร่ window 'ปิด' = emit result
> Trade-off: ยาว = capture late events, สั้น = low latency"

### Q: "Exactly-once เป็นไปได้จริงมั้ย?"
> "ใช่ — Flink ทำได้ผ่าน checkpoint + 2-phase commit + replayable source
> ต้องการ sink ที่ support transactions (Kafka, Iceberg, JDBC)
> 'Effectively-once' is industry term — exactly-once สำหรับ output, internal duplicates อาจมี"

### Q: "Lambda vs Kappa ใช้ตัวไหน?"
> "ปี 2026 ส่วนใหญ่ Kappa หรือ Unified
> Lambda มีปัญหา 2 codebase = maintenance hell
> Modern engines (Flink, Spark, Beam) ทำ same code ทั้ง batch + stream
> ตัด Lambda ออกได้เกือบทุก use case"

### Q: "เลือก streaming engine ไหน?"
> "Flink: complex state, low latency, stateful processing — best
> Spark Structured Streaming: unified with batch, micro-batch OK
> Dataflow/Beam: GCP managed, portable
> RisingWave/Materialize: SQL-first, easy
> Kafka Streams: embedded in service"

---

## Sources

- [What is Apache Flink? Stateful Stream Processing](https://www.conduktor.io/glossary/what-is-apache-flink-stateful-stream-processing)
- [Understanding Apache Flink: Architecture, Event-Time Processing, and State Management](https://softwarefrontier.substack.com/p/understanding-apache-flink-architecture)
- [Complex Event Processing (CEP) with Apache Flink](https://www.kai-waehner.de/blog/2026/04/14/complex-event-processing-cep-with-apache-flink-what-it-is-and-when-not-to-use-it/)
- [Understanding Apache Flink Event Time and Watermarks](https://www.decodable.co/blog/understanding-apache-flink-event-time-and-watermarks)
- [How to Implement Flink Exactly-Once Processing](https://oneuptime.com/blog/post/2026-01-28-flink-exactly-once-processing/view)
- [Time and Watermarks in Confluent Cloud for Apache Flink](https://docs.confluent.io/cloud/current/flink/concepts/timely-stream-processing.html)
