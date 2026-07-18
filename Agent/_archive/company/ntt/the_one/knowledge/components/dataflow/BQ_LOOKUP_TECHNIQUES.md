# BigQuery Lookup / Enrichment Techniques for Beam Streaming Pipelines

> **Context**: Streaming pipeline (sales-collector) อ่าน Kafka → ต้อง enrich data โดย lookup จาก BQ master/reference tables (~5 tables, batch-updated) → เติม calculated columns ก่อนเขียน BQ refined
>
> **Platform**: Apache Beam 2.70+ on Google Cloud Dataflow (Streaming)

---

## สรุปเปรียบเทียบ (Quick Comparison)

| Technique | Freshness | BQ Cost | Memory | Complexity | Best For |
|-----------|-----------|---------|--------|------------|----------|
| 1. Side Input + PeriodicImpulse | นาที-ชม. | ต่ำ (periodic full scan) | สูง (ทุก worker) | กลาง | **Master data < 1GB** |
| 2. Stateful DoFn + Timer Cache | นาที-ชม. | ต่ำ | กลาง (per-key) | สูง | Keyed lookup, large data |
| 3. Per-element BQ Query | Real-time | **สูงมาก** | ต่ำ | ต่ำ | Rare lookups only |
| 4. BigTable/Redis Cache | วินาที | ต่ำ (BQ→cache batch) | ต่ำ (external) | สูง (infra) | High-throughput, low-latency |
| 5. Beam Enrichment Transform | วินาที-นาที | ขึ้นกับ handler | ต่ำ-กลาง | กลาง | Bigtable/Vertex AI |
| 6. CoGroupByKey Join | Window-based | กลาง | สูง | กลาง | Two streaming sources |
| 7. Shared in-process Cache (singleton) | นาที-ชม. | ต่ำ | กลาง (1 copy/worker) | กลาง | **Simple, practical** |

---

## Technique 1: Side Input with PeriodicImpulse

### How it works

```
PeriodicImpulse(every 1hr)
    → ReadAllFromBigQuery(master_table)
    → AsDict() / AsList()
    → side_input ──────────────────┐
                                   ▼
Kafka → Parse → DoFn(element, side=master_dict) → enriched → BQ
```

### Architecture

Beam จะ re-read BQ ทุกๆ interval → update side input → workers ใช้ version ล่าสุด
Side input ถูก materialize บน disk/memory ของ **ทุก worker**

### Code Skeleton

```python
from apache_beam.transforms.periodicsequence import PeriodicImpulse

# Refresh master data every hour
refresh = (
    p
    | "Trigger" >> PeriodicImpulse(
        fire_interval=3600,  # seconds
        apply_windowing=True,
    )
    | "ReadMaster" >> beam.FlatMap(
        lambda _: beam.io.ReadFromBigQuery(
            query="SELECT key, val FROM `project.dataset.master`",
            use_standard_sql=True,
        )
    )
    | "ToDict" >> beam.CombineGlobally(
        beam.combiners.ToDictCombineFn("key", "val")
    ).as_singleton_view()
)

# Main pipeline uses side input
enriched = (
    kafka_events
    | "Enrich" >> beam.ParDo(EnrichDoFn(), master=beam.pvalue.AsSingleton(refresh))
)
```

### Pros
- **Beam-native** — ไม่ต้องเพิ่ม infra
- **Automatic refresh** — PeriodicImpulse จัดการ timing
- **Consistent snapshot** — ทุก element ใน window เห็น data ชุดเดียวกัน

### Cons
- **Memory**: Side input ถูก copy ไปทุก worker → ถ้า master data ใหญ่ (>1GB) จะ OOM
- **Refresh latency**: ต้องรอ read + distribute ใหม่ทั้ง set
- **Watermark blocking**: Side input ที่ยังไม่พร้อมอาจ block main pipeline watermark
- **PeriodicImpulse + ReadFromBigQuery**: ใน streaming mode, `ReadFromBigQuery` ใน FlatMap ต้องระวัง — อาจต้องใช้ `ReadAllFromBigQuery` แทน
- **5 tables × full scan** ทุกชั่วโมง → BQ cost เพิ่ม (แต่ถ้า master data เล็กก็ถูก)

### BQ Cost
- **Per refresh**: scan ทั้ง table × 5 tables × 24 ครั้ง/วัน
- ถ้า master tables รวม 100MB → ~$0.01/วัน (ถูกมาก)
- ถ้า master tables รวม 10GB → ~$1.20/วัน

### When to Use
- Master data < 1GB รวม
- Freshness ระดับ ชม. พอ
- ไม่อยากเพิ่ม external infra

---

## Technique 2: Stateful DoFn with Timer-based Refresh

### How it works

```
Kafka → KeyBy(lookup_key) → StatefulDoFn ──→ enriched → BQ
                                │
                                ├─ State: cached_master_data (per key)
                                └─ Timer: refresh every N minutes
                                     → query BQ for this key
                                     → update state
```

### Code Skeleton

```python
class EnrichWithCacheDoFn(beam.DoFn):
    CACHE = beam.transforms.userstate.BagStateSpec("cache", beam.coders.PickleCoder())
    TIMER = beam.transforms.userstate.TimerSpec("refresh", beam.TimeDomain.PROCESSING_TIME)

    def process(
        self,
        element,
        cache=beam.DoFn.StateParam(CACHE),
        timer=beam.DoFn.TimerParam(TIMER),
    ):
        cached = list(cache.read())
        if not cached:
            # First element — trigger immediate refresh
            timer.set(Timestamp.now())

        # Lookup from cache
        master_data = cached[0] if cached else {}
        enriched = {**element, **master_data.get(element["key"], {})}
        yield enriched

    @beam.transforms.userstate.on_timer(TIMER)
    def refresh(self, cache=beam.DoFn.StateParam(CACHE)):
        # Query BQ for fresh data
        from google.cloud import bigquery
        client = bigquery.Client()
        rows = client.query("SELECT ...").result()
        cache.clear()
        cache.add({row["key"]: dict(row) for row in rows})

        # Re-arm timer for next refresh
        self.TIMER.set(Timestamp.now() + Duration(seconds=3600))
```

### Pros
- **Memory efficient**: Cache per key (ไม่ต้อง load ทั้ง table)
- **Fine-grained refresh**: แต่ละ key refresh อิสระ
- **No side input bottleneck**: ไม่ block watermark

### Cons
- **Complexity สูง**: State + Timer management ยาก debug
- **BQ queries มาก**: ถ้า key cardinality สูง → query BQ ถี่มาก
- **Dataflow state backend**: State ใหญ่ → slow checkpoint
- **Key distribution**: Hot key → state ใหญ่ใน 1 worker
- **ไม่เหมาะกับ master data**: ถ้า master data เหมือนกันทุก key → เสียเปล่าที่ cache per key

### BQ Cost
- ขึ้นกับ key cardinality × refresh rate
- 1M unique keys × refresh ทุกชม. = **1M queries/ชม.** → แพงมาก!
- เหมาะเฉพาะ low-cardinality keys

### When to Use
- Lookup data ที่ขึ้นกับ key (ไม่ใช่ global master)
- Key cardinality ต่ำ (<1000 unique keys)
- ต้องการ per-key freshness control

---

## Technique 3: Per-element BQ Query

### How it works

```
Kafka → Parse → DoFn(query BQ per element) → enriched → BQ
```

### Code Skeleton

```python
class LookupDoFn(beam.DoFn):
    def setup(self):
        from google.cloud import bigquery
        self._client = bigquery.Client()

    def process(self, element):
        key = element["partner_code"]
        row = next(self._client.query(
            f"SELECT * FROM `master` WHERE code = '{key}' LIMIT 1"
        ).result(), None)
        if row:
            element.update(dict(row))
        yield element
```

### Pros
- **Simple** — เข้าใจง่าย
- **Always fresh** — ได้ data ล่าสุดเสมอ
- **No memory** — ไม่ต้อง cache

### Cons
- **BQ Cost สูงมาก**: ทุก element = 1 BQ query → **minimum 10MB charge ต่อ query**
- **Latency**: BQ query ~1-5 วินาที/ครั้ง → throughput ต่ำมาก
- **Quota**: BQ concurrent query limit (default 100)
- **ไม่ scale**: 1000 events/sec = 1000 BQ queries/sec → จะ hit quota + ค่าใช้จ่ายมหาศาล

### BQ Cost
- **10MB minimum per query** × 1000 events/sec × 86400 sec/day = **864TB scanned/day** (billed)
- **ห้ามใช้ใน production streaming**

### When to Use
- **ไม่แนะนำ** สำหรับ streaming pipeline
- Batch pipeline ที่ elements น้อย (<100/run) อาจพอได้

---

## Technique 4: External Cache (BigTable / Redis / Memorystore)

### How it works

```
[Batch Job / Cloud Function]                    [Streaming Pipeline]
BQ master tables ──(scheduled)──→ BigTable      Kafka → Parse → DoFn(lookup BigTable) → enriched → BQ
                                  / Redis
                                  / Memorystore
```

### Code Skeleton (BigTable)

```python
# Batch: BQ → BigTable (Cloud Function, ทุก 1 ชม.)
def sync_master_to_bigtable():
    bq = bigquery.Client()
    bt = bigtable.Client().instance("my-instance").table("master")
    for row in bq.query("SELECT * FROM master").result():
        bt.mutate_rows([...])

# Streaming: Lookup from BigTable
class BigtableLookupDoFn(beam.DoFn):
    def setup(self):
        self._table = bigtable.Client().instance("my-instance").table("master")

    def process(self, element):
        row = self._table.read_row(element["key"].encode())
        if row:
            element["master_val"] = row.cells["cf"]["val"][0].value.decode()
        yield element
```

### Pros
- **Low latency**: BigTable <10ms, Redis <1ms
- **High throughput**: ไม่มี query limit แบบ BQ
- **Scalable**: BigTable/Redis designed สำหรับ high-QPS
- **Decouple refresh**: Batch job sync BQ→Cache แยกจาก pipeline

### Cons
- **เพิ่ม infra**: ต้อง provision + manage BigTable/Redis
- **Cost เพิ่ม**: BigTable ~$0.65/node/hr (min 1 node), Redis Memorystore ~$0.049/GB/hr
- **Data sync complexity**: ต้องมี job sync BQ→cache + handle failures
- **Eventual consistency**: Cache อาจ stale ระหว่าง sync

### BQ Cost
- **ต่ำ**: BQ scan เฉพาะตอน sync (batch, scheduled)
- BigTable/Redis cost แทน

### When to Use
- **High throughput** (>1000 events/sec) + ต้องการ low latency
- Master data ใหญ่ (>1GB) — ไม่ fit ใน memory
- มี budget สำหรับ additional infra
- ต้องการ <10ms lookup latency

---

## Technique 5: Beam Enrichment Transform (2.54+)

### How it works

```
Kafka → Parse → beam.Enrichment(handler=BigTableHandler(...)) → enriched → BQ
```

Beam built-in enrichment — currently supports BigTable handler + Vertex AI Feature Store

### Code Skeleton

```python
from apache_beam.transforms.enrichment import Enrichment
from apache_beam.transforms.enrichment_handlers.bigtable import BigTableEnrichmentHandler

handler = BigTableEnrichmentHandler(
    project_id="my-project",
    instance_id="my-instance",
    table_id="master",
    row_key="partner_code",
)

enriched = (
    kafka_events
    | "Enrich" >> Enrichment(handler).with_timeout(10)
)
```

### Pros
- **Beam-native API**: Clean, declarative
- **Built-in handlers**: BigTable, Vertex AI Feature Store
- **Custom handler**: สร้าง handler เองได้ (extend `EnrichmentSourceHandler`)
- **Batching**: Handler สามารถ batch requests

### Cons
- **ต้องมี BigTable/Feature Store**: ยังไม่มี native BQ handler
- **Custom BQ handler**: ต้อง implement เอง (query BQ ใน handler) → กลับไปปัญหา per-element query
- **Relatively new**: API อาจเปลี่ยน

### When to Use
- มี BigTable/Feature Store อยู่แล้ว
- ต้องการ clean API

---

## Technique 6: CoGroupByKey Join

### How it works

```
Kafka events (keyed) ───┐
                        ├─ CoGroupByKey ──→ enriched → BQ
BQ master (keyed) ──────┘
```

### Code Skeleton

```python
events = kafka_pcoll | "KeyEvents" >> beam.Map(lambda x: (x["partner_code"], x))
master = (
    p
    | "ReadMaster" >> beam.io.ReadFromBigQuery(query="SELECT * FROM master")
    | "KeyMaster" >> beam.Map(lambda x: (x["code"], x))
)

joined = (
    {"events": events, "master": master}
    | beam.CoGroupByKey()
    | beam.FlatMap(merge_results)
)
```

### Pros
- **Beam-native** join
- **No external infra**
- **Efficient for large joins**: GroupByKey is distributed

### Cons
- **Streaming complexity**: BQ side เป็น bounded, Kafka เป็น unbounded → windowing ยุ่ง
- **Master data stale**: BQ อ่านครั้งเดียวตอน start (bounded read)
- **Hot keys**: Key skew → OOM
- **Window alignment**: ต้อง window both sides ให้ตรงกัน

### When to Use
- Master data ไม่เปลี่ยนบ่อย (อ่านครั้งเดียวพอ)
- Join key distribution สม่ำเสมอ

---

## Technique 7: Shared In-process Cache (Singleton Pattern) ⭐ RECOMMENDED

### How it works

```
Kafka → Parse → DoFn(lookup from shared_cache) → enriched → BQ
                     │
                     └─ shared_cache (module-level / class-level singleton)
                          ├─ dict[key, master_data]
                          ├─ last_refresh_time
                          └─ auto-refresh every N minutes (on access)
```

**Key insight**: ใน Dataflow, worker process หนึ่งรัน **หลาย DoFn instances** ใน **thread เดียวกัน** (หรือ process เดียวกัน) — สามารถ share in-process cache ผ่าน module-level variable ได้

### Code Skeleton

```python
import threading
import time
from google.cloud import bigquery

class _MasterCache:
    """Thread-safe in-process cache for BQ master data."""

    def __init__(self, refresh_interval_sec: int = 3600):
        self._lock = threading.Lock()
        self._data: dict[str, dict] = {}
        self._last_refresh: float = 0
        self._refresh_interval = refresh_interval_sec

    def get(self, key: str) -> dict | None:
        self._maybe_refresh()
        return self._data.get(key)

    def get_all(self) -> dict[str, dict]:
        self._maybe_refresh()
        return self._data

    def _maybe_refresh(self) -> None:
        now = time.monotonic()
        if now - self._last_refresh < self._refresh_interval:
            return
        with self._lock:
            # Double-check after acquiring lock
            if now - self._last_refresh < self._refresh_interval:
                return
            self._do_refresh()
            self._last_refresh = time.monotonic()

    def _do_refresh(self) -> None:
        client = bigquery.Client()
        new_data: dict[str, dict] = {}

        # Query all 5 master tables
        queries = {
            "partner": "SELECT code, name, ... FROM `project.dataset.partner_master`",
            "branch":  "SELECT code, name, ... FROM `project.dataset.branch_master`",
            # ... more tables
        }
        for table_key, query in queries.items():
            for row in client.query(query).result():
                key = row["code"]
                if key not in new_data:
                    new_data[key] = {}
                new_data[key][table_key] = dict(row)

        self._data = new_data  # Atomic swap


# Module-level singleton — shared across all DoFn instances in same worker
_master_cache = _MasterCache(refresh_interval_sec=3600)


class EnrichDoFn(beam.DoFn):
    """Enrich elements using shared in-process cache."""

    def process(self, element):
        master = _master_cache.get(element["partner_code"])
        if master:
            element["partner_name"] = master.get("partner", {}).get("name")
            element["branch_name"] = master.get("branch", {}).get("name")
            # ... more enrichments
        yield element
```

### สำหรับ sales-collector: Integration Pattern

```python
# In builder.py — ไม่ต้องเพิ่ม pipeline branch
# Cache ถูก trigger ตอน first access ใน DoFn

enriched_receipt = (
    receipt_rows
    | "EnrichReceipt" >> beam.ParDo(EnrichDoFn())
)

# Cache refresh เกิดขึ้นอัตโนมัติเมื่อ interval หมด
# ทุก worker refresh อิสระ (ไม่ sync กัน แต่ OK สำหรับ master data)
```

### Pros
- **Simple**: ไม่ต้อง pipeline branch, ไม่ต้อง side input, ไม่ต้อง external infra
- **Memory efficient**: 1 copy per worker process (ไม่ใช่ per DoFn instance)
- **Lazy refresh**: Query BQ เฉพาะเมื่อ cache expired
- **No watermark blocking**: ไม่กระทบ watermark (ต่างจาก side input)
- **Thread-safe**: Lock-based double-check pattern
- **Cost ต่ำ**: BQ scan = N workers × N tables × 24 refresh/day

### Cons
- **Not Beam-native**: Bypass Beam's data model (ไม่มี exactly-once guarantee สำหรับ cache)
- **Per-worker refresh**: แต่ละ worker refresh เวลาต่างกัน → short inconsistency window
- **Memory**: ต้อง fit ใน memory ของ 1 worker (แต่ดีกว่า side input ที่ copy ทุก worker)
- **Not unit-test friendly**: Module-level singleton ยาก mock → ต้อง inject

### BQ Cost
- `N workers × 5 tables × 24 refresh/day` (ถ้า refresh ทุกชม.)
- 4 workers × 5 tables × 24 = 480 queries/day × 10MB min = ~$0.02/day
- **ถูกที่สุดในทุก technique** (ยกเว้น CoGroupByKey ที่อ่านครั้งเดียว)

### When to Use
- **Master data ขนาดเล็ก-กลาง** (< 500MB รวม 5 tables)
- **Freshness ระดับ ชม. พอ**
- **ไม่อยากเพิ่ม complexity** (ไม่ต้อง BigTable, ไม่ต้อง pipeline branch)
- **Production-proven**: หลาย Dataflow pipeline ใช้ pattern นี้

---

## Recommendation สำหรับ Sales-Collector

### สถานการณ์
- Master/reference data 5 tables (batch-updated, เปลี่ยนไม่บ่อย)
- Streaming pipeline (Kafka → Dataflow)
- ต้องการ balance cost vs freshness vs complexity

### แนะนำ: **Technique 7 (Shared In-process Cache)** เป็นตัวเลือกแรก

**เหตุผล:**
1. **Simplest** — ไม่ต้องเพิ่ม pipeline branch, side input, หรือ external infra
2. **Cost ต่ำสุด** — BQ scan minimal
3. **Practical** — Production-proven pattern
4. **ไม่ block watermark** — ต่างจาก Side Input
5. **เหมาะกับ master data** — เปลี่ยนไม่บ่อย, freshness ระดับ ชม. OK

### Alternative: **Technique 1 (Side Input + PeriodicImpulse)** ถ้าต้องการ Beam-native

**เหตุผล:**
1. **Beam-native** — ใช้ Beam API ถูกต้อง, testable
2. **Consistent snapshot** — ทุก element เห็น data version เดียวกัน
3. **แต่** — watermark blocking + memory per worker + complexity มากกว่า

### ไม่แนะนำ
- **Technique 3 (Per-element)** — BQ cost มหาศาล, ห้ามใช้ streaming
- **Technique 4 (BigTable/Redis)** — Overkill สำหรับ master data ขนาดเล็ก
- **Technique 2 (Stateful DoFn)** — Complexity สูงเกินไป สำหรับ global master data

### Decision Matrix

```
ถ้า master data รวม < 500MB  → Technique 7 (Shared Cache)
ถ้า master data รวม 500MB-2GB → Technique 1 (Side Input)
ถ้า master data รวม > 2GB    → Technique 4 (BigTable)
ถ้าต้องการ < 1 sec latency   → Technique 4 (BigTable/Redis)
```

---

## Appendix: Side Input vs Shared Cache — Deep Comparison

| Aspect | Side Input | Shared Cache |
|--------|-----------|--------------|
| Beam-native | ✅ Yes | ❌ Bypass Beam model |
| Watermark impact | ⚠️ Can block | ✅ No impact |
| Memory per worker | High (full copy) | Medium (1 copy) |
| Refresh mechanism | PeriodicImpulse PTransform | Timer-based in DoFn |
| Consistency | Strong (same version) | Eventual (per-worker) |
| Testability | ✅ Easy (mock side input) | ⚠️ Need DI pattern |
| Complexity | Medium | Low |
| Failure handling | Beam manages retry | Must handle manually |

---

## Appendix: Cost Calculator

```
BQ On-Demand pricing: $6.25 per TB scanned (as of 2025)
Minimum per query: 10MB

Formula:
  daily_cost = (num_workers × num_tables × refreshes_per_day × table_size_bytes)
               / (1024^4) × 6.25

Example (Technique 7):
  4 workers × 5 tables × 24/day × 50MB each
  = 24,000 MB/day = 23.4 GB/day
  = $0.14/day = ~$4.30/month

Example (Technique 3 — per element, DON'T DO THIS):
  1000 events/sec × 86400 sec × 10MB min
  = 864,000,000 MB/day = 824 TB/day
  = $5,150/day 💀
```
