# Streaming-to-Streaming Join / Enrichment Techniques for Beam Pipelines

> **Context**: Streaming pipeline ต้อง enrich data จากอีก source ที่เป็น **streaming เหมือนกัน** (ไม่ใช่ batch/reference table) — เช่น join 2 Kafka topics, หรือ consume topic เดียวกันแล้วแยก logic
>
> **Platform**: Apache Beam 2.70+ on Google Cloud Dataflow (Streaming)
>
> **ต่างจาก BQ Lookup doc อย่างไร**: BQ Lookup doc เป็นเรื่อง batch reference table (เปลี่ยนไม่บ่อย) ส่วน doc นี้เป็นเรื่อง **ทั้ง 2 ฝั่งเป็น streaming** — data มาเรื่อยๆ ไม่มี "snapshot"

---

## สรุปเปรียบเทียบ (Quick Comparison)

| Technique | Join Type | Latency | Completeness | Complexity | Best For |
|-----------|-----------|---------|--------------|------------|----------|
| 1. CoGroupByKey (Windowed) | Inner/Outer | Window-dependent | ภายใน window | กลาง | 2 streams, matched rate |
| 2. Same-topic / Multi-topic in 1 Pipeline | Tag + Group | ต่ำ (same pipeline) | ภายใน window | กลาง | Related events, same pipeline |
| 3. Stateful DoFn (Stream-updating Cache) | Left join | ต่ำ (in-state) | Eventual | สูง | Slowly-changing dim from stream |
| 4. Shared Cache fed by Side Pipeline | Left join | นาที | Eventual | กลาง | Dim stream + fact stream |
| 5. Materialized View (Stream → Store → Lookup) | Left join | วินาที-นาที | Eventual | สูง (infra) | High-volume dim stream |
| 6. Flatten + GroupByKey (Tagged Union) | Inner/Outer | Window-dependent | ภายใน window | ต่ำ-กลาง | Simple, same key space |
| 7. Temporal Join (Event-time Sorted) | Point-in-time | Window-dependent | Best-effort | สูง | Accurate historical join |

---

## Technique 1: CoGroupByKey on Windowed Streams

### How it works

```
Kafka Topic A ──→ Key(id) ──→ Window(Fixed/Sliding) ──┐
                                                        ├─ CoGroupByKey ──→ merge ──→ BQ
Kafka Topic B ──→ Key(id) ──→ Window(Fixed/Sliding) ──┘
```

ทั้ง 2 streams ถูก window ด้วย window เดียวกัน แล้ว join ด้วย key

### Code Skeleton

```python
import apache_beam as beam
from apache_beam import window

# Both streams windowed identically
stream_a = (
    p
    | "ReadA" >> ReadFromKafka(topic="orders")
    | "ParseA" >> beam.Map(parse_order)
    | "KeyA" >> beam.Map(lambda x: (x["order_id"], x))
    | "WindowA" >> beam.WindowInto(window.FixedWindows(300))  # 5 min
)

stream_b = (
    p
    | "ReadB" >> ReadFromKafka(topic="payments")
    | "ParseB" >> beam.Map(parse_payment)
    | "KeyB" >> beam.Map(lambda x: (x["order_id"], x))
    | "WindowB" >> beam.WindowInto(window.FixedWindows(300))
)

joined = (
    {"orders": stream_a, "payments": stream_b}
    | "Join" >> beam.CoGroupByKey()
    | "Merge" >> beam.FlatMap(merge_order_payment)
)

def merge_order_payment(element):
    key, groups = element
    orders = list(groups["orders"])
    payments = list(groups["payments"])
    if orders and payments:
        yield {**orders[0], "payment_status": payments[0].get("status")}
    elif orders:
        yield {**orders[0], "payment_status": None}  # left join
```

### Pros
- **Beam-native** — ใช้ Beam join API ถูกต้อง, well-understood
- **Distributed** — GroupByKey จัดการ shuffle efficiently
- **Deterministic** — ภายใน window เดียวกัน, join ผลลัพธ์เดียวกันเสมอ
- **Flexible join type** — inner, left, right, full outer ได้หมด

### Cons
- **Window alignment จำเป็น** — ถ้า event จาก 2 streams มาคนละ window → miss join
- **Late data** — event ที่มาหลัง window close จะ drop (ต้องตั้ง `allowed_lateness`)
- **Unmatched rate** — ถ้า stream A มา 1000 events/sec แต่ B มา 1 event/min → window ใหญ่ = memory สูง
- **Shuffle cost** — GroupByKey = shuffle ข้าม workers → network I/O
- **Hot key** — key distribution skewed → worker memory spike

### When to Use
- **2 streams ที่มา rate ใกล้เคียงกัน** (เช่น order + payment, ทั้งคู่ realtime)
- **Join key ชัดเจน** (order_id, transaction_id)
- **ยอมรับ window-level completeness** (ไม่ต้อง exact point-in-time)

---

## Technique 2: Same-topic / Multi-topic Consumer in 1 Pipeline

### How it works

```
กรณี A: Topic เดียว หลาย event types
Kafka Topic "events" ──→ Parse ──→ Route by event_type ──┬─ "order" ──→ Key ──┐
                                                          │                     ├─ CoGroupByKey
                                                          └─ "payment" ──→ Key ─┘

กรณี B: หลาย Topics ใน pipeline เดียว
Kafka Topic "orders"   ──→ Parse ──→ Tag("order") ──┬─ Flatten ──→ Key ──→ GroupByKey
Kafka Topic "payments" ──→ Parse ──→ Tag("payment") ─┘
```

**Core idea**: อ่านหลาย sources ใน pipeline เดียว → route/tag → join ภายใน

### Code Skeleton (Same topic, different event types)

```python
# Single topic with mixed events
all_events = (
    p
    | "Read" >> ReadFromKafka(topic="sales_events")
    | "Parse" >> beam.Map(parse_event)
    | "Window" >> beam.WindowInto(window.FixedWindows(300))
)

# Route by event type
orders = (
    all_events
    | "FilterOrders" >> beam.Filter(lambda x: x["event_type"] == "order_created")
    | "KeyOrders" >> beam.Map(lambda x: (x["order_id"], x))
)

payments = (
    all_events
    | "FilterPayments" >> beam.Filter(lambda x: x["event_type"] == "payment_received")
    | "KeyPayments" >> beam.Map(lambda x: (x["order_id"], x))
)

joined = (
    {"orders": orders, "payments": payments}
    | "Join" >> beam.CoGroupByKey()
    | "Merge" >> beam.FlatMap(merge_results)
)
```

### Code Skeleton (Multi-topic, tagged union)

```python
# Read from multiple topics
orders = (
    p
    | "ReadOrders" >> ReadFromKafka(topic="orders")
    | "ParseOrders" >> beam.Map(lambda x: ("order", parse_order(x)))
)

payments = (
    p
    | "ReadPayments" >> ReadFromKafka(topic="payments")
    | "ParsePayments" >> beam.Map(lambda x: ("payment", parse_payment(x)))
)

# Tag + Flatten + GroupByKey
all_tagged = (
    (orders, payments)
    | "Flatten" >> beam.Flatten()
    | "KeyByJoinKey" >> beam.Map(lambda x: (x[1]["order_id"], x))
    | "Window" >> beam.WindowInto(window.FixedWindows(300))
    | "Group" >> beam.GroupByKey()
    | "Merge" >> beam.FlatMap(merge_tagged_events)
)

def merge_tagged_events(element):
    key, tagged_list = element
    orders = [v for tag, v in tagged_list if tag == "order"]
    payments = [v for tag, v in tagged_list if tag == "payment"]
    for order in orders:
        payment = payments[0] if payments else {}
        yield {**order, "payment_amount": payment.get("amount")}
```

### Pros
- **ลด Kafka consumer**: 1 consumer group สำหรับ topic เดียว → ลด connection overhead
- **Event ordering**: Events จาก topic เดียวกัน (same partition) มาตามลำดับ
- **No external dependency**: ทุกอย่างอยู่ใน pipeline เดียว
- **Co-located processing**: Events ที่ related มาใน worker เดียวกัน (ถ้า same partition key)

### Cons
- **Topic coupling**: Pipeline ผูกกับ topic structure → เปลี่ยน schema ยาก
- **Resource sharing**: Pipeline ใหญ่ขึ้น → autoscaling ถูก balance ยากขึ้น
- **Mixed throughput**: ถ้า 1 event type มา 10x อีกตัว → ไม่ balance
- **Failure blast radius**: Pipeline crash = ทุก consumer หยุดหมด
- **Window ต้อง match**: ถ้า 2 event types มา timing ต่างกันมาก → join miss

### When to Use
- **Events ที่ related กันสูง** อยู่ใน topic เดียว (เช่น order lifecycle events)
- **ต้องการ simplify infrastructure** (1 pipeline แทน 2)
- **Event rate ใกล้เคียงกัน**
- **Same team owns both topics**

---

## Technique 3: Stateful DoFn (Stream-updating Cache)

### How it works

```
Dim Stream (เช่น branch updates) ──→ Stateful DoFn ──→ update state
                                          │
Fact Stream (เช่น sales events)   ──→ ────┘──→ lookup state ──→ enriched
```

เหมือน Technique 2 ใน BQ Lookup doc แต่แทนที่ state จะมาจาก BQ timer refresh, state อัพเดตจาก stream อีกตัวโดยตรง

### Code Skeleton

```python
class StreamEnrichDoFn(beam.DoFn):
    """
    Two types of elements arrive (tagged):
    - ("dim", key, dim_data)   → update cache state
    - ("fact", key, fact_data) → lookup from cache, enrich, emit
    """
    CACHE = beam.transforms.userstate.BagStateSpec("cache", beam.coders.PickleCoder())

    def process(self, element, cache=beam.DoFn.StateParam(CACHE)):
        tag, key, data = element

        if tag == "dim":
            # Update cache with latest dim value
            cache.clear()
            cache.add(data)
            return  # Don't emit dim records

        # tag == "fact" — lookup from cache
        cached_list = list(cache.read())
        dim_data = cached_list[0] if cached_list else {}
        yield {**data, **dim_data}


# Usage: merge 2 streams with tags
dim_stream = (
    p
    | "ReadDim" >> ReadFromKafka(topic="branch_updates")
    | "ParseDim" >> beam.Map(parse_branch)
    | "TagDim" >> beam.Map(lambda x: (x["branch_code"], ("dim", x["branch_code"], x)))
)

fact_stream = (
    p
    | "ReadFact" >> ReadFromKafka(topic="sales")
    | "ParseFact" >> beam.Map(parse_sale)
    | "TagFact" >> beam.Map(lambda x: (x["branch_code"], ("fact", x["branch_code"], x)))
)

enriched = (
    (dim_stream, fact_stream)
    | "Flatten" >> beam.Flatten()
    | "Enrich" >> beam.ParDo(StreamEnrichDoFn())
)
```

### Pros
- **Near-realtime enrichment**: Dim updates ถูก apply ทันทีที่มา (ไม่ต้องรอ window close)
- **No external store**: State อยู่ใน Dataflow (managed by runner)
- **Efficient for slowly-changing dims**: เก็บแค่ latest value per key
- **No BQ cost**: ไม่ต้อง query BQ เลย

### Cons
- **State management complexity**: Debug ยาก, state size monitoring จำเป็น
- **Ordering dependency**: ถ้า fact มาก่อน dim → cache ว่าง → enrichment miss (cold start)
- **State backend pressure**: Key cardinality สูง → state ใหญ่ → slow checkpoint
- **Same key requirement**: fact + dim ต้อง key เดียวกัน (Beam routes by key)
- **No global state**: State เป็น per-key → ไม่ share ข้าม key (ถ้า dim เป็น global lookup → ไม่เหมาะ)
- **Dataflow-specific**: State behavior ต่างกันใน runners อื่น

### Cold Start Problem

```
Timeline:
t0: Pipeline starts
t1: Fact event (branch_code=A) arrives → cache empty → enrich fails (no dim data)
t2: Dim event (branch_code=A) arrives → cache updated
t3: Fact event (branch_code=A) arrives → cache hit → enrich success ✅
```

**Mitigation options:**
1. Buffer facts จน dim มา (complex, may cause backpressure)
2. ใช้ initial side input จาก BQ แล้วค่อย switch to stream update
3. ยอมรับ miss ช่วง cold start → downstream handle nulls

### When to Use
- **Dim source เป็น stream** (CDC feed, Kafka dim topic)
- **Dim changes ไม่บ่อย** (slowly changing dimension)
- **Key cardinality ต่ำ-กลาง** (< 100K unique keys)
- **Fact-to-dim delay ยอมรับได้** (dim มาก่อน fact ส่วนใหญ่)

---

## Technique 4: Shared Cache fed by Side Pipeline (Background Refresh from Stream)

### How it works

```
Dim Stream (Kafka) ──→ Side Pipeline ──→ update shared cache (singleton)
                                              │
Fact Stream (Kafka) ──→ Main Pipeline ──→ DoFn(lookup cache) ──→ enriched ──→ BQ
```

คล้าย Technique 7 (Singleton Cache) จาก BQ Lookup doc แต่แทนที่จะ refresh จาก BQ, ใช้อีก pipeline branch consume dim stream แล้วอัพเดต cache โดยตรง

### Code Skeleton

```python
import threading
from typing import Any

class _StreamFedCache:
    """Singleton cache updated from stream, read by main pipeline."""

    _instance: "_StreamFedCache | None" = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._data: dict[str, dict[str, Any]] = {}
        self._data_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "_StreamFedCache":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def update(self, key: str, value: dict[str, Any]) -> None:
        with self._data_lock:
            self._data[key] = value

    def lookup(self, key: str) -> dict[str, Any] | None:
        return self._data.get(key)  # dict read is atomic in CPython


class UpdateCacheDoFn(beam.DoFn):
    """Consumes dim stream → updates shared cache."""
    def process(self, element: dict[str, Any]) -> None:
        cache = _StreamFedCache.get_instance()
        key = element["branch_code"]
        cache.update(key, element)
        # No yield — this branch is sink-only (cache updater)


class EnrichFromCacheDoFn(beam.DoFn):
    """Main stream reads from shared cache."""
    def process(self, element: dict[str, Any]):
        cache = _StreamFedCache.get_instance()
        dim = cache.lookup(element["branch_code"])
        if dim:
            element["branch_name"] = dim.get("branch_name")
        yield element


# Pipeline
dim_branch = (
    p
    | "ReadDim" >> ReadFromKafka(topic="branch_updates")
    | "ParseDim" >> beam.Map(parse_branch)
    | "UpdateCache" >> beam.ParDo(UpdateCacheDoFn())  # sink branch
)

enriched = (
    p
    | "ReadFact" >> ReadFromKafka(topic="sales")
    | "ParseFact" >> beam.Map(parse_sale)
    | "Enrich" >> beam.ParDo(EnrichFromCacheDoFn())
    | "Write" >> WriteToBQ()
)
```

### Pros
- **Near-realtime** — Dim updates propagate ภายใน milliseconds (same worker)
- **No windowing needed** — cache ใช้ latest value, ไม่ต้อง align windows
- **No BQ cost** — dim data มาจาก stream โดยตรง
- **Simple enrichment DoFn** — main pipeline ไม่ต้อง KeyBy
- **Familiar pattern** — ถ้าใช้ Singleton Cache จาก batch อยู่แล้ว, แค่เปลี่ยน refresh source

### Cons
- **Per-worker cache** — แต่ละ worker เห็น dim events คนละชุด (Kafka partition assignment)
  - **Critical issue**: ถ้า dim topic มี 4 partitions, worker A อาจเห็นแค่ partition 0,1 → cache ไม่ครบ
  - **Mitigation**: Dim topic ต้องมี partition count ≥ worker count, หรือ broadcast all to all workers
- **Not Beam-native** — Bypass Beam's data model
- **Cold start** — Cache ว่างตอน start → miss enrichment ช่วงแรก
- **Memory** — ต้อง fit ใน memory per worker
- **No exactly-once** — Dim events อาจ process ซ้ำหรือ miss (at-least-once from Kafka)

### Worker-Partition Problem (สำคัญ!)

```
Dim topic: 2 partitions
Workers: 4

Kafka consumer assignment:
  Worker 0 → partition 0 (branch_code A, B)
  Worker 1 → partition 1 (branch_code C, D)
  Worker 2 → (no partition assigned for dim topic)
  Worker 3 → (no partition assigned for dim topic)

Result:
  Worker 2 processes sale with branch_code=A → cache miss! ❌
```

**Solutions:**
1. **Broadcast**: Dim stream → BQ/GCS → ทุก worker reload (กลับไปเหมือน batch)
2. **Publish dim to all partitions**: Producer ส่ง dim event ทุก partition (fan-out)
3. **Use Stateful DoFn instead** (Technique 3): KeyBy ensures same key goes to same worker

### When to Use
- **Dim stream volume ต่ำ** + **ทุก worker ได้รับ dim data ครบ** (broadcast possible)
- **Dim data เป็น global** (ไม่ key-specific) เช่น config updates, feature flags
- **พร้อมยอมรับ eventual consistency ระหว่าง workers**

---

## Technique 5: Materialized View (Stream → External Store → Lookup)

### How it works

```
Pipeline A (Dim):
Kafka dim topic ──→ Parse ──→ Write to BigTable/Redis/Firestore

Pipeline B (Fact + Enrichment):
Kafka fact topic ──→ Parse ──→ DoFn(lookup BigTable/Redis) ──→ enriched ──→ BQ
```

หรือ:
```
Pipeline A (Dim):
Kafka dim topic ──→ Parse ──→ Write to BQ (streaming insert)

Pipeline B (Fact + Enrichment):
Kafka fact topic ──→ Parse ──→ DoFn(read from BQ/cache) ──→ enriched ──→ BQ
```

แยก 2 pipelines — dim pipeline เขียน external store, fact pipeline อ่าน store สำหรับ enrichment

### Code Skeleton (BigTable as materialized view)

```python
# Pipeline A: Materialize dim stream to BigTable
class WriteDimToBigtableDoFn(beam.DoFn):
    def setup(self):
        from google.cloud import bigtable
        self._table = bigtable.Client(project="my-project") \
            .instance("my-instance").table("branch_dim")

    def process(self, element):
        row_key = element["branch_code"].encode()
        row = self._table.direct_row(row_key)
        row.set_cell("cf", "branch_name", element["branch_name"].encode())
        row.set_cell("cf", "region", element["region"].encode())
        row.commit()

# Pipeline B: Lookup from BigTable
class LookupBigtableDoFn(beam.DoFn):
    def setup(self):
        from google.cloud import bigtable
        self._table = bigtable.Client(project="my-project") \
            .instance("my-instance").table("branch_dim")

    def process(self, element):
        row = self._table.read_row(element["branch_code"].encode())
        if row:
            element["branch_name"] = row.cells["cf"]["branch_name"][0].value.decode()
        yield element
```

### Pros
- **Decoupled pipelines** — dim + fact pipeline scale อิสระ
- **Strong consistency** — BigTable/Redis read-after-write
- **Any number of consumers** — หลาย fact pipelines อ่าน store เดียวกัน
- **Scalable** — BigTable handles millions QPS
- **No cold start** — Store มี data ก่อน fact pipeline start (ถ้า dim pipeline รันก่อน)

### Cons
- **Extra infrastructure** — ต้อง provision + manage BigTable/Redis
- **Cost** — BigTable ~$0.65/node/hr (min 1 node ≈ $470/month), Redis Memorystore ~$0.049/GB/hr
- **Latency gap** — Dim write → store → fact read ≈ milliseconds-seconds
- **Operational complexity** — 2 pipelines to monitor, store to maintain
- **Double write cost** — Dim data เขียน Kafka + store + อาจ BQ ด้วย

### Cost Comparison (External Stores)

| Store | Min Cost/month | Latency | Max QPS | Best For |
|-------|---------------|---------|---------|----------|
| BigTable | ~$470 (1 node) | <10ms | 10K+/node | High-throughput |
| Redis Memorystore | ~$35 (1GB) | <1ms | 100K+ | Low-latency |
| Firestore | Pay-per-use (~$0.06/100K reads) | 10-50ms | 10K | Low-volume |
| BQ (streaming buffer) | $0.05/GB insert + query cost | seconds | 100K rows/sec | Already using BQ |

### When to Use
- **High-volume dim stream** (ไม่ fit ใน memory)
- **Multiple consumers** need same dim data
- **Strong consistency** required
- **Budget for extra infra**
- **Operational team** พร้อม manage additional stores

---

## Technique 6: Flatten + GroupByKey (Tagged Union)

### How it works

```
Stream A ──→ Map(tag="A", key, data) ──┐
                                        ├─ Flatten ──→ Window ──→ GroupByKey ──→ merge ──→ BQ
Stream B ──→ Map(tag="B", key, data) ──┘
```

Simple variation ของ CoGroupByKey — ใช้ Flatten + GroupByKey + manual tag แทน

### Code Skeleton

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class TaggedEvent:
    tag: str       # "sale" or "branch"
    key: str       # join key (branch_code)
    data: dict[str, Any]

sales = (
    p
    | "ReadSales" >> ReadFromKafka(topic="sales")
    | "TagSales" >> beam.Map(
        lambda x: (x["branch_code"], TaggedEvent("sale", x["branch_code"], x))
    )
)

branches = (
    p
    | "ReadBranches" >> ReadFromKafka(topic="branch_updates")
    | "TagBranches" >> beam.Map(
        lambda x: (x["branch_code"], TaggedEvent("branch", x["branch_code"], x))
    )
)

joined = (
    (sales, branches)
    | "Flatten" >> beam.Flatten()
    | "Window" >> beam.WindowInto(window.FixedWindows(300))
    | "Group" >> beam.GroupByKey()
    | "Merge" >> beam.FlatMap(merge_tagged)
)

def merge_tagged(element):
    key, events = element
    sales_list = [e.data for e in events if e.tag == "sale"]
    branch_list = [e.data for e in events if e.tag == "branch"]
    branch_info = branch_list[0] if branch_list else {}
    for sale in sales_list:
        yield {**sale, "branch_name": branch_info.get("branch_name")}
```

### Pros
- **Simple** — ง่ายกว่า CoGroupByKey (ไม่ต้อง named inputs)
- **Flexible** — เพิ่ม stream ที่ 3, 4 ได้ง่าย (แค่เพิ่ม tag)
- **Standard Beam** — ใช้ Flatten + GroupByKey ซึ่งทุก runner support

### Cons
- **เหมือน CoGroupByKey** — window alignment, late data, hot key problems เหมือนกัน
- **Type safety ต่ำ** — TaggedEvent ต้อง manual tag checking
- **Verbose** — merge function ต้อง handle tag extraction เอง
- **Performance**: Flatten + GroupByKey ≈ CoGroupByKey (ไม่ได้ดีกว่า)

### When to Use
- **ง่ายกว่า CoGroupByKey** ในบาง use case (เช่น 3+ streams)
- **Team ไม่คุ้นกับ CoGroupByKey API** — Flatten + GBK เข้าใจง่ายกว่า

---

## Technique 7: Temporal Join (Event-time Sorted / Point-in-time)

### How it works

```
Fact Stream ──→ Window(Session/Fixed) ──→ Sort by event_time ──┐
                                                                 ├─ Temporal merge ──→ enriched
Dim Stream ──→ Window(Session/Fixed) ──→ Sort by event_time  ──┘
```

**Goal**: Join fact event กับ dim version ที่ "มีผลอยู่ ณ เวลานั้น" (point-in-time correctness)

เช่น branch เปลี่ยนชื่อเวลา 14:00 → sale เวลา 13:59 ต้องได้ชื่อเก่า, sale เวลา 14:01 ได้ชื่อใหม่

### Code Skeleton

```python
class TemporalJoinDoFn(beam.DoFn):
    """
    Stateful DoFn that maintains sorted dim versions.
    For each fact event, finds the latest dim version <= fact.event_time.
    """
    DIM_STATE = beam.transforms.userstate.BagStateSpec("dims", beam.coders.PickleCoder())

    def process(self, element, dims=beam.DoFn.StateParam(DIM_STATE)):
        tag, data = element

        if tag == "dim":
            # Store dim version with its effective timestamp
            dims.add({"event_time": data["event_time"], "data": data})
            return

        # tag == "fact" — find latest dim version <= fact.event_time
        fact_time = data["event_time"]
        all_dims = sorted(list(dims.read()), key=lambda d: d["event_time"])

        # Binary search for latest dim <= fact_time
        applicable_dim = None
        for dim in all_dims:
            if dim["event_time"] <= fact_time:
                applicable_dim = dim["data"]
            else:
                break

        if applicable_dim:
            data["branch_name"] = applicable_dim.get("branch_name")
        yield data
```

### Pros
- **Point-in-time accuracy** — fact gets the correct dim version for its timestamp
- **Historical correctness** — important for audit trails, financial data
- **Handles late data** — dim version history ถูกเก็บไว้ → late fact ยัง match ได้

### Cons
- **Complexity สูงมาก** — State management + sorting + binary search
- **State growth** — ต้องเก็บ dim history ทั้งหมด (หรือ truncate old versions)
- **Memory** — State per key จะ grow unbounded ถ้าไม่มี cleanup
- **Ordering assumption** — ถ้า dim events มา out-of-order → sort ใน state อาจผิด
- **Performance** — Sort ทุกครั้งที่ fact มา → O(N) per fact event

### State Cleanup Strategy

```python
# ทุกๆ N minutes, ลบ dim versions เก่ากว่า retention period
CLEANUP_TIMER = beam.transforms.userstate.TimerSpec("cleanup", beam.TimeDomain.PROCESSING_TIME)

@beam.transforms.userstate.on_timer(CLEANUP_TIMER)
def cleanup(self, dims=beam.DoFn.StateParam(DIM_STATE)):
    cutoff = time.time() - RETENTION_SECONDS
    current_dims = list(dims.read())
    dims.clear()
    for dim in current_dims:
        if dim["event_time"] >= cutoff:
            dims.add(dim)
```

### When to Use
- **Compliance / Audit** ต้องการ point-in-time correctness
- **Slowly-changing dims** ที่เปลี่ยน infrequently แต่ต้อง track history
- **Financial data** ที่ต้อง match exact rate/price ณ เวลา transaction

---

## Recommendation: เลือกเทคนิคตาม Use Case

### Decision Tree

```
Q1: Dim source เป็น stream หรือ batch?
├─ Batch → ดู BQ_LOOKUP_TECHNIQUES.md
└─ Stream → Q2

Q2: ต้องการ point-in-time accuracy (dim version ณ เวลา fact)?
├─ Yes → Technique 7 (Temporal Join) — complex แต่ accurate
└─ No (latest dim OK) → Q3

Q3: Dim + Fact มาจาก topic เดียวกัน?
├─ Yes → Technique 2 (Same-topic, route by type) — simple
└─ No → Q4

Q4: Dim data เปลี่ยนบ่อยแค่ไหน?
├─ ไม่บ่อย (slowly changing, < 1/min) → Q5
└─ บ่อย (> 1/sec) → Q6

Q5: Dim data fit ใน memory? (< 500MB)
├─ Yes → Technique 4 (Shared Cache fed by Side Pipeline)
│        หรือ Technique 3 (Stateful DoFn) ถ้า key-specific
└─ No → Technique 5 (Materialized View — BigTable/Redis)

Q6: Rate ของ 2 streams ใกล้เคียงกัน?
├─ Yes → Technique 1 (CoGroupByKey) หรือ Technique 6 (Flatten+GBK)
└─ No → Technique 5 (Materialized View — decouple + scale independently)
```

### สำหรับ Sales-Collector: ถ้า reference table เปลี่ยนเป็น stream

**สถานการณ์ปัจจุบัน**: `sales_channel_branch` เป็น batch reference table → ใช้ Singleton Cache (BQ lookup)

**ถ้า `sales_channel_branch` เปลี่ยนเป็น stream (CDC feed)**:

| Option | Technique | Tradeoff |
|--------|-----------|----------|
| A | **Keep Singleton Cache + BQ** | ง่ายสุด — dim stream เขียน BQ, cache refresh ทุกชม. (current setup works) |
| B | **Shared Cache fed by stream** (Tech 4) | Realtime — แต่ต้องแก้ worker-partition problem |
| C | **Stateful DoFn** (Tech 3) | Accurate per-key — แต่ complex + cold start |
| D | **Materialized View** (Tech 5) | Scalable — แต่ต้องเพิ่ม infra (BigTable/Redis) |

**แนะนำ Option A** (keep current + let dim stream write BQ):
- ไม่ต้องแก้ code เลย — dim stream pipeline เขียน BQ, fact pipeline อ่าน BQ cache เหมือนเดิม
- Staleness ระดับ ชม. ยอมรับได้สำหรับ master data

---

## Appendix: Window Strategies สำหรับ Streaming Join

| Window Type | Duration | Use Case | Join Behavior |
|-------------|----------|----------|---------------|
| Fixed (Tumbling) | 5-60 min | Regular batches | Events ในช่วงเวลาเดียวกัน join |
| Sliding | Size=10min, Period=5min | Overlapping | Event อาจ join หลายครั้ง |
| Session | Gap=30min | User sessions | Events ที่มาต่อเนื่อง group ด้วยกัน |
| Global + Trigger | ∞ | Latest-wins | ทุก event อยู่ window เดียว (ต้อง trigger) |

### Window + Allowed Lateness

```python
beam.WindowInto(
    window.FixedWindows(300),            # 5-minute windows
    trigger=trigger.AfterWatermark(
        early=trigger.AfterProcessingTime(60),  # emit early results every 1 min
        late=trigger.AfterCount(1),              # emit on each late arrival
    ),
    accumulation_mode=trigger.AccumulationMode.ACCUMULATING,
    allowed_lateness=Duration(seconds=3600),  # accept late data up to 1 hr
)
```

---

## Appendix: Streaming Join Failure Modes

| Problem | Symptom | Solution |
|---------|---------|----------|
| Late data | Enrichment miss (null fields) | `allowed_lateness` + late trigger |
| Hot key | Worker OOM | Pre-split keys, add salt |
| Schema evolution | Deserialization error | Schema registry + backward compat |
| Rebalance | Temporary data loss | Checkpoint + replay from offset |
| Backpressure | One stream blocks other | Separate consumer groups / pipelines |
| Clock skew | Window misalignment | Use event time (not processing time) |
| Cold start | Cache empty at start | Seed from batch (BQ/GCS) first |
