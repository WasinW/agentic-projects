# Kafka Consumer Instance Sharing Analysis in Apache Beam / Dataflow

> Date: 2026-04-04
> Context: coupons-collector pipeline มี 5 ReadFromKafka transforms (created, used, expired, revoked, reinstated)
> Problem: `coupons_created` มี data lag 1hr+ ในขณะที่ topic อื่นแค่ 2-4 min
> Question: ReadFromKafka หลายตัวใน pipeline เดียวกัน share consumer instance กันมั้ย?

---

## 1. คำตอบ: แต่ละ ReadFromKafka สร้าง Consumer แยกกัน

**ไม่ share instance** — แต่ละ ReadFromKafka transform สร้าง Kafka consumer ของตัวเองอย่างอิสระ

```python
# 2 transforms นี้ = 2 consumer instances แยกกัน
created = p | "ReadCreated" >> ReadFromKafka(topics=["created"], ...)
used = p | "ReadUsed" >> ReadFromKafka(topics=["used"], ...)
```

### หลักฐานจาก Source Code

**Java KafkaIO** (`ReadFromKafkaDoFn.java`):
- แต่ละ SDF restriction (= topic-partition) สร้าง `KafkaConsumer` ผ่าน `ConsumerFactoryFn` แยกกัน
- Consumer lifecycle: restriction start → create consumer → poll → checkpoint → resume → create new consumer
- ไม่มี mechanism ให้ share consumer ข้าม transforms

**Python ReadFromKafka** (`kafka.py`):
- เป็น `ExternalTransform` wrapper → ส่ง config ไป Java expansion service
- แต่ละ ReadFromKafka = separate expansion request = separate sub-graph
- Expansion service ไม่มี concept "merge consumers from different transforms"

### Ref:
- [KafkaIO.java](https://github.com/apache/beam/blob/master/sdks/java/io/kafka/src/main/java/org/apache/beam/sdk/io/kafka/KafkaIO.java)
- [ReadFromKafkaDoFn.java](https://github.com/apache/beam/blob/master/sdks/java/io/kafka/src/main/java/org/apache/beam/sdk/io/kafka/ReadFromKafkaDoFn.java)
- [Python kafka.py](https://github.com/apache/beam/blob/master/sdks/python/apache_beam/io/kafka.py)

---

## 2. SDF-Based Reader — Parallelism Per Partition

Modern Beam ใช้ **Splittable DoFn (SDF)** สำหรับ KafkaIO:

```
ReadFromKafka(topics=["created"])
  → SDF splits into:
    Restriction(topic="created", partition=0) → creates KafkaConsumer #1
    Restriction(topic="created", partition=1) → creates KafkaConsumer #2
    ...
```

- แต่ละ topic-partition = restriction แยก = consumer instance แยก
- Dataflow สามารถกระจาย restrictions ไปคนละ worker ได้
- 5 topics x 10 partitions = 50 restrictions = up to 50 independent consumers

### Ref:
- [Beam SDF Programming Guide](https://beam.apache.org/documentation/programming-guide/#splittable-dofns)

---

## 3. แล้วทำไม coupons_created ถึง lag?

### ไม่ใช่เพราะ shared consumer — แต่เป็นเพราะ:

### A. Shared Worker Resources (น่าจะเป็นสาเหตุหลัก)

- แม้ consumers จะแยกกัน แต่ทั้ง 5 transforms รันบน **worker pool เดียวกัน**
- `coupons_created` มี volume สูงกว่ามาก (120K elements vs 0 elements ของ topic อื่น)
- worker CPU/memory ถูก created กินเกือบหมด → topic อื่นได้ resources น้อย

### B. Downstream Backpressure (API Rate Limit)

- `api_delay_seconds: 0.14` = max ~7 calls/sec/thread
- `coupons_created` มี backlog 120K → ต้องใช้เวลา 120K / 14 TPS = ~2.4 ชม.
- Downstream ช้า → backpressure กลับไปที่ reader → lag สะสม

### C. Stage Fusion

- Dataflow **fuses** ReadFromKafka กับ downstream transforms (AttachEventName → BuildRawEvent → ...)
- ถ้า downstream ช้า → reader ถูก slow down ด้วย (backpressure ภายใน fused stage)
- **ไม่** fuse ข้าม sources — แต่ละ ReadFromKafka เริ่ม stage ของตัวเอง

### D. NOT caused by:

- Shared consumer instance (แยกกัน)
- Consumer group rebalancing (ถ้าใช้ assign mode)
- Cross-language overhead (minimal)

---

## 4. Consumer Group (`group.id`) — ต้องระวัง

### ถ้าหลาย ReadFromKafka ใช้ `group.id` เดียวกัน:

| Mode | ปัญหา |
|---|---|
| `subscribe()` (group-managed) | Kafka broker มอง consumers ทั้งหมดเป็น group เดียว → rebalance storm → partition assignment ผิด |
| `assign()` (explicit) | ไม่มีปัญหา assignment แต่ offset commits อาจปนกัน |

**Best practice**: ใช้ **unique `group.id` per ReadFromKafka transform** หรือ per topic

```python
ReadFromKafka(
    consumer_config={"group.id": "coupons-collector-created", ...},
    topics=["loyalty.coupons.created"],
)
ReadFromKafka(
    consumer_config={"group.id": "coupons-collector-used", ...},
    topics=["loyalty.coupons.used"],
)
```

### Ref:
- [Kafka Consumer Group Protocol](https://kafka.apache.org/documentation/#consumerconfigs_group.id)

---

## 5. Dataflow Streaming Engine

### Classic Streaming vs Streaming Engine:

| | Classic | Streaming Engine |
|---|---|---|
| Source management | Worker-side (compete for CPU) | **Backend-managed** (better isolation) |
| Resource isolation | Shared thread pool | Sources managed separately |
| Autoscaling | Aggregate-based | **Per-key/per-source** awareness |

**Streaming Engine ให้ isolation ดีกว่ามาก** — แนะนำ enable เสมอ

### Ref:
- [Dataflow Streaming Engine](https://cloud.google.com/dataflow/docs/streaming-engine)

---

## 6. Solutions — จัดลำดับความน่าสนใจ

### Solution A: รวมเป็น ReadFromKafka เดียว (แนะนำสำหรับ coupons)

```python
all_events = p | ReadFromKafka(
    topics=["created", "used", "expired", "revoked", "reinstated"],
    consumer_config={"group.id": "coupons-collector-all", ...},
)
# Route by topic in downstream DoFn
```

**Pros:**
- Dataflow จัดการ partition distribution ได้ดีกว่า (50 partitions ใน 1 source)
- ลด cross-language overhead (1 expansion vs 5)
- ลด consumer creation overhead

**Cons:**
- ต้อง route by topic ใน downstream
- 1 topic lag อาจกระทบ topic อื่น (แต่ Dataflow SDF จะ split/rebalance)

**เหมาะกับ coupons-collector** เพราะทุก topic ใช้ schema + flow เหมือนกัน

### Solution B: แยก Pipeline ต่อ topic (isolation สูงสุด)

```
Pipeline 1: ReadFromKafka("created") → Process → Write
Pipeline 2: ReadFromKafka("used") → Process → Write
```

**Pros:** Complete resource isolation, independent scaling
**Cons:** มาก pipeline, มาก cost (baseline cost per job), CI/CD ซับซ้อน

### Solution C: Fusion Break ด้วย Reshuffle

```python
created = p | ReadFromKafka(topics=["created"], ...)
created_safe = created | beam.Reshuffle()  # break fusion
```

**Pros:** ป้องกัน downstream backpressure กลับไปที่ reader
**Cons:** เพิ่ม shuffle step (latency cost)

### Solution D: เพิ่ม Workers

- `maxNumWorkers` เพิ่ม → มี resources มากขึ้นให้ทุก source
- แต่ต้องระวัง API TPS limit (14 TPS shared across workers)

### Solution E: Unique `group.id` per Transform (baseline)

ทำเสมอ ไม่ว่าจะเลือก solution ไหน

---

## 7. Known Issues (Apache Beam)

| Issue | Description |
|---|---|
| [BEAM-12908](https://issues.apache.org/jira/browse/BEAM-12908) | Cross-language KafkaIO performance — serialization overhead |
| [BEAM-10931](https://issues.apache.org/jira/browse/BEAM-10931) | Consumer caching — overhead จาก create/close consumer ทุก checkpoint |
| [BEAM-13653](https://issues.apache.org/jira/browse/BEAM-13653) | SDF reader latency กับ many partitions on single worker |
| Autoscaler | Dataflow autoscaler ใช้ aggregate metric — อาจไม่เห็น per-source starvation |

---

## 8. สรุป Decision Matrix สำหรับ coupons-collector

| Approach | Isolation | Performance | Complexity | Cost |
|---|---|---|---|---|
| **A. Single ReadFromKafka 5 topics** | Medium | **ดีที่สุด** (Dataflow optimize ให้) | **ต่ำสุด** | ต่ำสุด |
| B. 5 ReadFromKafka (ปัจจุบัน) | Medium | OK (แต่ lag ได้ถ้า volume ต่าง) | ต่ำ | ต่ำ |
| C. 5 Pipelines แยก | **สูงสุด** | ดี | สูง | สูง |
| D. Current + Reshuffle | Medium | ดีขึ้น (ลด backpressure) | ต่ำ | ต่ำ |

**แนะนำ: Solution A** — รวม 5 topics เป็น ReadFromKafka เดียว เพราะ:
- ทุก topic ใช้ schema เดียวกัน
- flow เหมือนกัน (consume → write source → merge → call API)
- Dataflow distribute partitions ได้ efficient กว่า
- ลด resource contention ระหว่าง source stages
