# 03 — Honest Evaluation: ทุกข้ออ้างของ CTO ทำได้/ไม่ได้

ในเอกสารนี้ **ยอมรับ openly** ว่า Cloud Run + Pub/Sub + creative architecture ทำเกือบทุกอย่างได้. แล้ว **identify เฉพาะ** จุดที่:
- ทำไม่ได้จริง ๆ (architectural impossible)
- ทำได้ แต่ tradeoff ใหญ่
- ทำได้ แต่ pattern ในตัว insight ปัจจุบันยังไม่ได้ทำ

## Capability Matrix (ทำได้/ไม่ได้)

| Capability | Cloud Run? | How (if yes) | Tradeoff |
|---|---|---|---|
| **HTTP API serving** | ✓ ใช่ | Cloud Run native | None — fits use case |
| **Per-event transform → BQ append** | ✓ ใช่ | Cloud Run + BQ client `insertAll` | None ที่ low scale, แพงที่สูง |
| **Per-event transform → BQ via Storage Write API (default stream)** | ✓ ใช่ | Cloud Run + Storage Write client | สามารถ append-only — Storage Write CDC mode ต้อง config + library support |
| **Pub/Sub direct subscription → BQ** | ✓ ใช่ | Pub/Sub `bigquery_config` subscription | append-only; UDF for transform; `enable_exactly_once_delivery=false` ใน insight ปัจจุบัน |
| **CDC UPSERT to BQ** | ⚠ บางส่วน | Storage Write API + `_CHANGE_TYPE` + table `primary_key NOT ENFORCED` | ต้อง implement state for dedup + ordering; **ไม่ work ดีโดยไม่มี bundle atomicity** |
| **CDC DELETE to BQ (true)** | ✗ ทำได้ยากมาก | Storage Write API + tombstone or DML DELETE | ใน insight ปัจจุบันยังไม่ทำ — ที่ loyalty/members-collector ทำได้เพราะ Beam bundle atomicity |
| **Iceberg writes (atomic snapshot)** | ⚠ ที่ low throughput | Single-committer Cloud Run + GCS staging + manual manifest commit | Throughput cap by 1 vCPU; **ทำเลย ๆ ที่ scale ไม่ได้** |
| **GroupByKey aggregation** | ⚠ จำกัด | Pub/Sub ordering key + BT state | Latency 100-1000× ของ Beam in-memory state |
| **Streaming join 2 sources** | ⚠ จำกัด | BT lookup + cache + reconciliation | Cost explosion ที่ high cardinality, ไม่มี side-input pattern |
| **Windowed aggregation (5 min)** | ⚠ จำกัด | Cloud Scheduler + flush BT state to BQ | processing-time only, ไม่มี watermarks |
| **Event-time correctness with late data** | ✗ ทำไม่ได้แบบ correctly | (workaround: reconcile job daily) | Late data goes to wrong window; metric drift |
| **Backpressure (Kafka source slowdown)** | ✓ ใช่ | Streaming pull subscription | Worker pool ต้อง coordinate manually |
| **Backfill 30 days from cold storage** | ✗ ใช้ไม่ได้แบบ practical | Re-publish all events through Pub/Sub | At 100M/day × 30d = 3B msgs × HTTP latency = ~35 days replay time vs Beam batch 2-3 hr |
| **Schema evolution (add column without downtime)** | ⚠ จำกัด | Pub/Sub schema versioning + deploy coordination | ไม่ atomic — readers/writers อาจ see different schemas mid-deploy |
| **Hot key handling** | ✗ ไม่มี automatic | Manual key splitting / sub-key fan-out | Beam มี automatic hot key detection |
| **Exactly-once across multiple sinks** | ✗ ทำไม่ได้แบบ true | Saga / 2PC / outbox | Eventual consistency only — ไม่ใช่ atomic |
| **Per-stage metrics + watermarks** | ⚠ ต้องสร้างเอง | Custom metrics + reconciliation | No DAG-aware observability |

## ✓ ที่ Cloud Run **ทำได้สบาย** (ไม่ต้องอ้างว่าใช้ Dataflow)

CTO ถูกใน 3 cases:

### 1. HTTP API serving + simple ingestion
audiences, personas/api, triggers, online-event-receiver, bigfiles-receiver — **Cloud Run เหมาะแล้ว**. ไม่ต้องเปลี่ยนเป็น Dataflow

### 2. Cloud Run + Pub/Sub direct → BQ append
ใช้ได้สำหรับ "raw event log" use case:
- รับ event
- transform เล็กน้อย
- append BQ table
- query downstream อ่าน raw

ตัวอย่าง: events_consents log ใน insight, online_event raw log

**ที่ low-medium scale (< 10M events/day) — pattern นี้ work ดี**. ไม่ต้องบังคับใช้ Dataflow

### 3. Per-event compute → write BigTable (insight collector pattern ปัจจุบัน)
- รับ event Pub/Sub
- enrichment per event (lookup BT)
- update persona BT
- publish UPSERT message Pub/Sub

นี่คือ **OLTP-style processing**, ไม่ใช่ data pipeline. **Cloud Run เหมาะแล้ว**

## ⚠ ที่ Cloud Run **ทำได้ แต่ tradeoff ใหญ่**

### Tradeoff 1: Storage Write API CDC mode
Cloud Run + Storage Write API library สามารถใช้ CDC mode ได้:
```python
# pseudocode
client.append_rows(WriteStream(stream_type=PENDING))
# include _CHANGE_TYPE = "UPSERT" | "DELETE" pseudo-column
```

**แต่:** ที่ scale + correctness ที่ true CDC ต้องการ:
- **Per-key dedup** ต้องการ external state (BT/Redis)
- **Ordering** ต้องการ Pub/Sub ordering keys หรือ external sequencer
- **Bundle atomicity** ที่ Beam มี — ใน Cloud Run ต้อง implement WAL/checkpoint
- **Retry semantics** — Storage Write API stream มี state, ถ้า Cloud Run instance restart จะต้อง resume stream หรือสร้างใหม่ (ทุก resume = potential dup)

**Effort estimate**: 2-4 เดือนของ senior data engineer สำหรับ build CDC library ที่ใช้ใน Cloud Run pattern — vs 0 effort ใน Dataflow (built-in)

### Tradeoff 2: Iceberg writes via single-committer
**Pattern**: 1 Cloud Run service `min_instances=1, max_instances=1` รับ events → buffer in-process → commit ทุก 5 นาที

**ทำได้สำหรับ throughput ต่ำ.** แต่:
- ถ้า instance crash mid-buffer → events ที่ buffer ไว้ lost
- เพื่อ avoid loss: persist buffer ไปที่ GCS staging ก่อน → instance restart resume → commit Iceberg manifest
- ที่ point นี้ คุณ build **deterministic checkpointing system** = ส่วนหนึ่งของ Beam runtime

**Effort estimate**: 2-3 เดือนสำหรับ build Iceberg writer service ที่ correctness OK + scalable + recoverable. vs 0 effort ใน Dataflow IcebergIO

### Tradeoff 3: Multi-stage CDC chain (eventual consistency)
แทน atomic commit ใช้ chain pattern:
```
Cloud Run #1 → Pub/Sub topic A → BQ direct → BQ table 1
                                     ↓
                                 BQ CDC stream → Pub/Sub topic B → Cloud Run #2 → Iceberg
```

**ทำได้.** แต่:
- BQ ↔ Iceberg อาจ diverge 5 นาที-1 ชั่วโมง (lag ของ CDC stream + Cloud Run scaling time)
- Reconciliation job daily เพื่อตรวจ divergence
- ถ้า Cloud Run #2 fail consistently → BQ ahead of Iceberg → analytics queries ผิดตามมา
- Replay จาก Iceberg ย้อน BQ = ไม่มี (CDC stream uni-directional)

**Effort estimate**: 1-2 เดือนต่อ pipeline สำหรับ design chain + reconciliation + monitoring + alerting

## ✗ ที่ Cloud Run **ทำไม่ได้** (architectural)

### 1. True exactly-once ระหว่าง multiple heterogeneous sinks
ไม่ใช่ technically impossible — เป็น economically/practically impossible

**ต้องการ:**
- Distributed transaction protocol (2PC) participants ใน BQ + Iceberg + Kafka
- BQ does not support 2PC participant API
- Iceberg supports atomic commit but only within itself
- Kafka offset commit is Kafka-only

**Workaround:** outbox pattern via single transactional store (Spanner/PG) → CDC streams. Adds Spanner cost + complexity

**Beam solution**: deterministic finalization (proprietary tech) — ไม่ public API, only Dataflow runtime มี

### 2. Atomic snapshot isolation ระหว่าง concurrent writers
Iceberg snapshot atomic = "1 committer per snapshot per trigger". Cloud Run autoscale = N concurrent committers = conflicts

**ทำได้ก็ต่อเมื่อ:**
- max_instances=1 (= สูญเสียความ scaleable ของ Cloud Run)
- หรือ centralized commit coordinator service (= rebuilt Beam IcebergIO sink)

### 3. Deterministic backfill at scale
Beam batch read source: bounded read 30 วันของ Iceberg/BQ → run pipeline บน workers parallel → done ใน hours

Cloud Run: ไม่มี bounded source concept. ต้อง:
- Query source store เป็น chunks
- Re-publish events through Pub/Sub one-by-one
- Pub/Sub HTTP latency ~10ms per message
- 100M/day × 30 day = 3B messages = 3B × 10ms = **35 วัน to replay**

**Architectural reason**: HTTP services ทำงาน per-request. Beam workers ทำงาน on partitions in parallel. ที่ partition level, Beam process M events ใน 1 worker concurrently. Cloud Run HTTP endpoint = serial within request

### 4. Cross-key transactional state
"User A purchases coupon B → atomically debit user A balance + mark coupon B used"

**Beam:** state per key + side input — ไม่มี native cross-key tx (Beam ก็ไม่มี)
**Cloud Run + BT:** BT transactions are single-row only

**Honest:** **neither side has this**. Real solution = Spanner/PG. Off-topic for this debate

### 5. DAG-aware observability + lineage
- Beam: per-step row count, watermark tracking, backlog metrics, drain accounting
- Cloud Run: HTTP requests, CPU, memory — opaque to data flow

**ทำเองได้แต่:** custom OpenTelemetry traces + lineage system + reconciliation jobs = 2-4 months engineering. vs Dataflow free

## Summary: When CTO claims "Cloud Run can do everything"

**Honest reply:**

> "Cloud Run **can do most things** in data pipelines — yes. But for these 5 specific cases, doing them in Cloud Run requires:
> - 2-6 months engineering per case
> - Forfeit Beam's proven implementations
> - Higher operational complexity
> - Eventual consistency tradeoffs
>
> ที่ scope ของ The1 (8-12 collectors, 100M+ events/day combined), **economics flip**: cost of custom-building exceeds cost of using Dataflow.
>
> The proposal isn't 'Cloud Run can't do it'. It's 'should we?'"

## ที่ insight pattern ปัจจุบันยังไม่ได้ทำ (จากการ verify code)

ที่ CTO อาจอ้างว่า "เห็นไหม insight ทำงานอยู่แล้ว" — ดูจริงคือ insight pattern ปัจจุบัน:

| Capability | Insight ปัจจุบันมีไหม? | หลักฐาน |
|---|---|---|
| CDC (true) | ✗ ไม่มี | append-only `personas_changelogs` + ROW_NUMBER view ([insight/doc/insight-api/05](../../../../../insight/doc/insight-api/05_BQ_WRITE_SEMANTICS_PROOF.md)) |
| CDC DELETE | ✗ ไม่มี | ไม่มี tombstone column ใน schema; ลบ persona ไม่ได้แบบ workflow |
| Iceberg writes | ✗ ไม่ใช่ Iceberg แท้ | ที่อ้างว่า "managed-iceberg" type table — actual table type ของ events_consents เคยเปลี่ยน 3 ครั้ง (iceberg → external_iceberg → native) ([insight/HOTFIX_EVENTS_CONSENTS_20260128.md](../../../../../insight/HOTFIX_EVENTS_CONSENTS_20260128.md)) — เคยเดือนที่แล้วเปลี่ยนพังแล้วต้อง hotfix |
| Exactly-once | ✗ ไม่มี | `enable_exactly_once_delivery = false` ที่ pub-sub.tf:34 |
| Stateful streaming aggregation | ✗ ไม่มี | (ถ้ามี ทีม insight ต้องเขียนใหม่) |
| Windowed metrics with watermarks | ✗ ไม่มี | (ใช้ processing-time + reconciliation) |
| Backfill replay | ⚠ มีแบบ manual | re-publish events ผ่าน Pub/Sub (slow) |

**สิ่งที่ insight ทำงานอยู่ได้คือ:**
- Per-event enrichment + BT mutate (OLTP-style)
- Event ingestion → BQ append
- ClickHouse micro-batch (Pub/Sub → GCS → batch insert)

**สิ่งที่ insight pattern ทำไม่ได้** = สิ่งที่ loyalty/data plane ทำได้: true CDC, IcebergIO, exactly-once, windowed streaming, replay
