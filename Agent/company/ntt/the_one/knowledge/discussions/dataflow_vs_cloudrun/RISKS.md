# Enterprise Data Operations Risk Assessment: CloudRun vs Dataflow

> **Purpose**: วิเคราะห์ความเสี่ยงทาง technical ที่จะเกิดขึ้นจริงใน production เมื่อใช้ CloudRun ทำงาน data pipeline แทน Dataflow
> พร้อม technical proof ว่าปัญหาเกิดขึ้นได้อย่างไร และ investigate/recover ยากแค่ไหน

---

## Executive Summary

CloudRun ถูกออกแบบมาสำหรับ **stateless HTTP services** (API, web app)
Dataflow ถูกออกแบบมาสำหรับ **stateful data processing** (streaming, batch, ETL)

ทั้งสอง service มีจุดแข็งคนละด้าน — ปัญหาเกิดเมื่อนำ CloudRun มาทำงานที่ต้องการ data processing guarantees ที่มันไม่มี primitives ให้ ส่งผลให้ต้อง build เองทั้งหมดตั้งแต่ต้น ซึ่งเท่ากับ reinvent Dataflow ใน CloudRun

---

## Risk 1: In-Flight Data Loss During Deployment (CRITICAL)

### ปัญหา — Technical Mechanism

เมื่อ deploy version ใหม่ สิ่งที่เกิดขึ้นในแต่ละ platform:

#### CloudRun: Container Replacement

```
Timeline (CloudRun Kafka consumer deployment):
────────────────────────────────────────────────────────────
t=0     New revision deployed
t=0     Old container receives SIGTERM
t=0-10s Grace period (default 10 seconds, max 3600s)
t=10s   Container forcefully killed (SIGKILL)
────────────────────────────────────────────────────────────

ปัญหา: ระหว่าง t=0 ถึง t=10s มี messages ที่อยู่ใน 3 สถานะ:
```

**สถานะ 1: Messages ที่ consumed แล้วแต่ยัง process ไม่จบ**
```
Kafka partition offset:  [100] [101] [102] [103] [104] [105]
Consumer position:                                      ^ (offset 105)
Actually processed:               ^ (stuck at 102, waiting API response)

ถ้า auto-commit = true (default ของ kafka-python):
  → Offset 105 ถูก commit แล้ว
  → Container ถูก kill
  → Messages 102-104 = LOST PERMANENTLY
  → Consumer ใหม่เริ่มจาก 106 → ไม่มีทางรู้ว่า 102-104 หายไป

ถ้า auto-commit = false (manual commit):
  → Offset ยังอยู่ที่ 101 (commit ล่าสุด)
  → Container ถูก kill
  → Consumer ใหม่เริ่มจาก 102 → messages ถูก reprocess
  → แต่ 102 อาจ write ไป BQ ไปแล้วครึ่งหนึ่ง → DUPLICATE DATA
```

**สถานะ 2: Iceberg write buffer ที่ยัง flush ไม่จบ**
```
Iceberg managed.Write buffers data for 300 seconds (triggering_frequency)
ถ้า container ถูก kill ระหว่าง buffer:
  → Data files ถูกเขียนลง GCS แล้วบางส่วน
  → แต่ Iceberg snapshot commit ยังไม่เกิด
  → ผลลัพธ์: orphan data files ใน GCS (ใช้ storage แต่ query ไม่เห็น)
  → Data ใน buffer = LOST (ต้อง replay จาก Kafka)
```

**สถานะ 3: CDC DELETE operation ทำไปครึ่งเดียว**
```
CDC DELETE flow ของ members-collector:
1. ✅ Kafka message received (tier removed)
2. ✅ API called → tier not found (confirmed delete)
3. ✅ BQ queried → programCode found
4. ❌ Container killed ก่อน BQ Storage Write API CDC DELETE commit

ผลลัพธ์: data ใน BQ ยังคงมี tier เก่าอยู่ → stale data
แต่ Kafka offset อาจ commit ไปแล้ว → ไม่ replay อีก → permanent stale
```

#### Dataflow: Drain Mechanism

```
Timeline (Dataflow streaming job drain):
────────────────────────────────────────────────────────────
t=0      gcloud dataflow jobs drain "$JOB_ID"
t=0      Dataflow STOPS reading new messages from Kafka
t=0-5m   In-flight messages continue processing normally
         - API calls complete
         - CDC operations complete
         - Windows close naturally
t=5m     IcebergIO flushes remaining buffer → atomic snapshot commit
t=5-10m  BQ Storage Write API flushes → rows committed
t=10m    Kafka offsets committed (only for fully processed messages)
t=10m    Job enters DRAINED state
t=10m    New job starts → picks up from last committed offset
────────────────────────────────────────────────────────────

ผลลัพธ์: 0 messages lost, 0 duplicates, 0 orphan files
```

### Data Loss: ทำไมหา investigate ยาก

| Investigation | Dataflow | CloudRun |
|---------------|----------|----------|
| **รู้ว่า data หายไหม?** | ✅ Drain log บอกจำนวน records flushed | ❌ ไม่รู้ — ไม่มี accounting ระหว่าง shutdown |
| **รู้ว่าหายกี่ records?** | ✅ ไม่มี (0 loss) | ❌ ไม่สามารถคำนวณได้ — ต้อง compare Kafka offset กับ BQ row count |
| **Kafka offset vs actual** | ✅ Offset = processed | ❌ Offset อาจ ahead of actual processed → gap ที่มองไม่เห็น |
| **หาจุดที่หายได้ไหม?** | ✅ N/A | ❌ ต้อง join Kafka timestamps กับ BQ ingestion timestamps → ยาก ใช้เวลา |
| **Recovery** | ✅ ไม่ต้อง | ❌ ต้อง reset Kafka offset + replay → risk ซ้ำทั้ง partition |

**ตัวอย่าง scenario จริง:**
```
สมมติ deploy ครั้งหนึ่ง CloudRun kill container ระหว่าง process:
- Lost: 47 messages (member tier updates)
- 47 members มี tier data ไม่ update ใน BQ
- BI report แสดงว่ามี Gold members 10,247 คน แต่จริงๆ มี 10,294 คน
- ไม่มีใครรู้จนกว่า business ตรวจพบ (อาจเป็นสัปดาห์หรือเดือน)
- Investigation: ต้อง compare Kafka topic messages กับ BQ rows ทีละ record
- Recovery: reset Kafka consumer offset → replay ทั้ง partition → risk duplicate
- เวลา investigate + fix: 1-3 วัน per incident
```

### "0 Downtime" vs "Drain Downtime" — ข้อเท็จจริง

argument ที่ว่า "CloudRun มี 0 downtime แต่ Dataflow มี downtime ต้อง drain":

| มุมมอง | CloudRun "0 downtime" | Dataflow "drain downtime" |
|---------|----------------------|--------------------------|
| **HTTP service** | ✅ ถูกต้อง — new container พร้อมรับ request ทันที | N/A |
| **Kafka consumer** | ❌ **ไม่จริง** — consumer group rebalance ใช้เวลา 30-60 วินาที | ✅ Drain 5-15 นาที |
| **Data processing** | ❌ **ไม่จริง** — in-flight data lost ระหว่าง container swap | ✅ In-flight data processed จนจบ |
| **จาก perspective ของ data** | ❌ **มี downtime + data loss** | ✅ **มี downtime แต่ 0 data loss** |

```
CloudRun "0 downtime" deploy:
├── HTTP requests: ✅ 0 downtime (ใช่จริง)
├── Kafka consumption: ❌ 30-60s rebalance gap
├── In-flight data: ❌ LOST (ไม่ถูก process)
└── ข้อสรุป: 0 downtime สำหรับ HTTP ≠ 0 downtime สำหรับ data

Dataflow "drain" deploy:
├── New data intake: ⏸ Paused 5-15 min (drain period)
├── In-flight data: ✅ Fully processed before shutdown
├── Data loss: ✅ 0 records lost
└── ข้อสรุป: มี processing delay แต่ 0 data loss
```

**คำถามสำคัญ: ในงาน data — อะไรสำคัญกว่ากัน?**
- Deploy เร็ว 15 นาที แต่ data อาจหาย?
- หรือ Deploy ช้า 15 นาที แต่ data ไม่หายเลย?

> **Google Cloud Documentation** ([Dataflow Drain](https://cloud.google.com/dataflow/docs/guides/stopping-a-pipeline#drain)):
> "When you drain a pipeline, Dataflow immediately stops ingesting new data... and allows the pipeline to finish processing and writing any buffered data."
>
> ไม่มี equivalent mechanism ใน CloudRun — เพราะ CloudRun ไม่ได้ออกแบบมาสำหรับ stateful data processing

---

## Risk 2: No Exactly-Once Processing Guarantee (CRITICAL)

### ปัญหา — Technical Mechanism

**Exactly-once = แต่ละ Kafka message ถูก process และ write ได้ 1 ครั้งเท่านั้น**

ไม่ใช่แค่ "ดี" — มันเป็น **requirement** สำหรับ enterprise data:
- Loyalty points: duplicate → แต้มเกิน → financial loss
- Member tiers: duplicate → report ผิด → business decision ผิด
- CDC DELETE: duplicate → delete ซ้ำ → ถ้า re-insert มาระหว่างนั้น จะลบ data ที่ควรอยู่

#### ทำไม CloudRun ทำ exactly-once ไม่ได้

```
CloudRun Kafka consumer — 3 failure scenarios:

Scenario A: Process สำเร็จ แต่ commit offset fail
────────────────────────────────────────────────
1. Read message (offset 100)
2. Process message → write to BQ ✅
3. Commit offset → NETWORK ERROR ❌
4. Container restart → re-read offset 100
5. Process message AGAIN → write to BQ AGAIN
6. ผลลัพธ์: DUPLICATE record ใน BQ

Scenario B: Process fail ระหว่าง multi-step
────────────────────────────────────────────────
1. Read message (offset 100)
2. Write to Iceberg ✅
3. Write to BQ → TIMEOUT ❌
4. Container restart → re-read offset 100
5. Write to Iceberg AGAIN (duplicate in Iceberg)
6. Write to BQ ✅
7. ผลลัพธ์: Iceberg มี duplicate, BQ ถูกต้อง → DATA INCONSISTENCY

Scenario C: Partial fan-out success
────────────────────────────────────────────────
1. Read message (member tier change event)
2. Fan-out to 4 tables:
   - member_tier: ✅ written
   - tier_maintenance: ✅ written
   - tier_events_upgraded: ❌ FAIL (container killed)
   - tier_events_downgraded: ⏭️ not reached
3. Commit offset (auto-commit)
4. ผลลัพธ์: 2 of 4 tables updated → PARTIAL UPDATE → data inconsistency
```

#### Dataflow exactly-once mechanism

```
Dataflow Bundle Processing:
────────────────────────────────────────────────
1. Read N messages from Kafka → create BUNDLE
2. Process all messages in bundle
3. Write to ALL outputs (Iceberg + BQ × 4 tables) → TENTATIVE
4. If ALL writes succeed → COMMIT bundle (atomic)
5. If ANY write fails → RETRY entire bundle (rollback tentative writes)
6. After commit → advance Kafka offset

ผลลัพธ์:
- All-or-nothing: ทุก output ได้ data เหมือนกัน หรือ ไม่ได้เลย
- No partial writes: ไม่มี scenario ที่ 2 จาก 4 tables ได้ data
- Retry-safe: retry ไม่สร้าง duplicate เพราะ tentative writes ถูก rollback
```

> **Google Cloud Documentation** ([Dataflow Exactly-Once](https://cloud.google.com/dataflow/docs/concepts/exactly-once)):
> "Cloud Dataflow ensures that every record is processed exactly once... The system guarantees that side effects, such as writes to Cloud BigQuery, are not duplicated."

> **Apache Beam Documentation** ([Runner Semantics](https://beam.apache.org/documentation/runners/capability-matrix/)):
> Dataflow runner provides "Exactly-once" processing guarantee — CloudRun ไม่ใช่ Beam runner จึงไม่มี guarantee นี้

### Investigation Difficulty

| เรื่อง | Dataflow | CloudRun |
|--------|----------|----------|
| **ตรวจพบ duplicate** | ✅ ไม่เกิด (exactly-once) | ❌ ต้อง run SQL: `SELECT id, COUNT(*) ... HAVING COUNT(*) > 1` เป็นประจำ |
| **ตรวจพบ partial write** | ✅ ไม่เกิด (bundle atomicity) | ❌ ต้อง cross-check ทุก table ว่า row count ตรงกัน → complex query |
| **เวลาตรวจพบ** | ✅ Instant (ไม่เกิด) | ❌ อาจเป็นวัน/สัปดาห์ — จนกว่า BI report ผิดปกติ |
| **เวลา fix** | ✅ 0 | ❌ ต้อง identify duplicates → delete → verify → อาจ 2-8 ชั่วโมง/incident |
| **Root cause analysis** | ✅ N/A | ❌ ต้อง correlate container logs + Kafka offsets + BQ write timestamps → complex |

---

## Risk 3: No Backpressure — Silent Data Corruption Under Load (HIGH)

### ปัญหา — Technical Mechanism

**Backpressure = ความสามารถในการชะลอ source เมื่อ downstream ช้า**

```
Normal flow (100 msg/sec):
Kafka ──100/sec──→ [Process] ──100/sec──→ [Write to BQ]
                   ✅ ทัน                   ✅ ทัน

Campaign day (10,000 msg/sec):
────────────────────────────────────────────────

Dataflow (มี backpressure):
Kafka ──500/sec──→ [Process:API slow] ──500/sec──→ [Write]
       ^ slowed                   autoscale workers 1→5
       automatically              throughput increases
結果: ช้าลงเล็กน้อย แต่ 0 data loss

CloudRun (ไม่มี backpressure):
Kafka ──10K/sec──→ [Process:API slow] ──100/sec──→ [Write]
       ^ still fast                       ^ bottleneck
       consuming messages                 memory fills up
       into memory

t=0:    Buffer: 0 messages        Memory: 50MB
t=10s:  Buffer: 99,000 messages   Memory: 500MB
t=30s:  Buffer: 297,000 messages  Memory: 1.5GB
t=60s:  Container OOM killed      Memory: >2GB (limit)

ผลลัพธ์:
- 297,000 messages ใน memory buffer = LOST
- Container restart → Kafka rebalance (30-60s)
- Resume → แต่ traffic ยังสูง → OOM อีก → crash loop
```

### Recovery Difficulty

```
OOM crash loop scenario:
1. Container OOM → restart → 30s rebalance
2. Resume consuming → 10K msg/sec still coming
3. OOM again within 60s → restart
4. ซ้ำไปเรื่อยๆ จนกว่า traffic ลด
5. ระหว่างนั้น: Kafka consumer lag สะสม → data delay หลายชั่วโมง

Investigation:
- ❌ ไม่มี log บอกว่า messages ไหนหายไป (OOM = no graceful shutdown log)
- ❌ ต้อง compare Kafka high watermark vs consumer committed offset
- ❌ ถ้า auto-commit=true → offset committed แต่ data lost → invisible gap
- ❌ Recovery: ต้อง manually reset offset → replay → risk duplicates

Dataflow equivalent scenario:
- Autoscale workers 1→5 (automatic)
- If workers maxed out → backpressure slows Kafka read
- Data flows through slower but COMPLETELY
- 0 OOM, 0 data loss, 0 investigation needed
```

> **Google Cloud Documentation** ([Dataflow Autoscaling](https://cloud.google.com/dataflow/docs/horizontal-autoscaling)):
> "Horizontal autoscaling lets the Dataflow service automatically choose the appropriate number of worker instances... The Dataflow service automatically scales the number of workers based on the amount of work in a pipeline."

---

## Risk 4: No Streaming Primitives — Must Reinvent From Scratch (HIGH)

### ปัญหา — Technical Mechanism

Streaming data processing ต้องการ 4 primitives พื้นฐาน ที่ CloudRun ไม่มี:

#### 1. Windowing (การจัด group messages ตามเวลา)

```python
# สิ่งที่ Dataflow ทำให้อัตโนมัติ (code จริงจาก builder.py):
windowed = parsed | beam.WindowInto(
    FixedWindows(60),  # Group messages เป็น 60-second windows
    trigger=AfterWatermark(
        early=Repeatedly(AfterProcessingTime(60)),
    ),
    accumulation_mode=AccumulationMode.DISCARDING,
)

# ทำไมต้อง window?
# → Iceberg write: batch 1000s of records → 1 atomic commit (efficient)
# → ถ้าไม่มี window: ต้อง write ทีละ record → 1000x slower, 1000x more commits
```

CloudRun alternative: ต้อง build time-based batching เอง
```python
# ต้อง implement เอง:
class ManualWindowManager:
    def __init__(self):
        self.buffer = []
        self.window_start = time.time()

    def add(self, message):
        self.buffer.append(message)
        if time.time() - self.window_start >= 60:
            self.flush()  # But what if flush fails?
            # What about late data?
            # What about out-of-order events?
            # What about multi-partition coordination?
            # → ต้อง handle ทุก case เอง
```

#### 2. Watermarks (การ track ว่า data มาถึงครบแค่ไหน)

```
Watermark = "confidence ว่า data ก่อนเวลานี้มาถึงหมดแล้ว"

Dataflow: tracks watermark automatically across all workers
→ รู้ว่า "data ก่อน 14:00:00 มาครบแล้ว → safe to close window"
→ Late data (ก่อน 14:00:00 แต่มาถึงหลัง) → route to late data handler

CloudRun: ไม่มี concept → ไม่รู้ว่า data มาครบหรือยัง
→ Close window เมื่อไหร่? ไม่มีทางรู้
→ Late data? Process เหมือน data ปกติ → อาจอยู่ผิด partition
```

#### 3. Triggers (เมื่อไหร่ควร emit ผลลัพธ์จาก window)

```
Dataflow triggers (code จริง):
- AfterWatermark: emit เมื่อ watermark ผ่าน window end
- AfterProcessingTime(60): emit early results ทุก 60 วินาที
- DISCARDING: หลัง emit แล้ว clear buffer

CloudRun: emit เมื่อไหร่? → ต้องตัดสินใจเอง
- Timer-based? → ถ้า container restart ล่ะ?
- Count-based? → ถ้า messages มาไม่สม่ำเสมอล่ะ?
- Memory-based? → ถ้า OOM ก่อน trigger ล่ะ?
```

#### 4. Accumulation Mode (จัดการ window output อย่างไร)

```
DISCARDING (ใช้อยู่): emit แล้วทิ้ง → ไม่ duplicate
ACCUMULATING: emit แล้วเก็บ → emit ซ้ำ (สำหรับ correction)

CloudRun: ต้อง manage buffer lifecycle เอง
→ ถ้า emit แล้ว crash ก่อน clear buffer → duplicate on restart
→ ถ้า clear buffer แล้ว emit fail → data loss
→ ต้อง implement 2-phase commit pattern เอง
```

### Effort to Rebuild

| Primitive | Lines of Code (Estimate) | Edge Cases | Risk of Bugs |
|-----------|:------------------------:|:----------:|:------------:|
| Windowing | 500-1000 | Time zone, DST, leap seconds | High |
| Watermarks | 1000-2000 | Multi-partition, out-of-order, late data | Very High |
| Triggers | 500-1000 | Crash recovery, partial emit | High |
| Accumulation | 300-500 | 2-phase commit, crash between phases | Very High |
| **Total** | **2300-4500** | **ทุกข้อต้อง handle crash recovery** | **Very High** |

> ทั้ง 4 primitives นี้เป็น core ของ Apache Beam Windowing Model ที่ Google ใช้เวลาพัฒนามากกว่า 10 ปี (ตั้งแต่ Google Millwheel → Dataflow → Beam)

---

## Risk 5: Iceberg Writes Without Managed I/O — Complexity Explosion (HIGH)

### ปัญหา — Technical Mechanism

```
Dataflow Iceberg Write Path (ปัจจุบัน):
Python SDK ──→ Beam Expansion Service ──→ Java IcebergIO ──→ BLMS REST Catalog
                                          ↓
                                    managed.Write(ICEBERG)
                                    - Auto-create table
                                    - Auto-partition
                                    - Buffered writes (300s)
                                    - Atomic snapshot commits
                                    - Schema evolution
                                    - Vended credentials (GoogleAuthManager)

CloudRun Iceberg Write Path (ต้อง build):
Python code ──→ PyIceberg library ──→ BLMS REST Catalog (manual OAuth)
                ↓
          ต้อง implement เอง:
          - Table creation + partition spec
          - Manual batching (accumulate in memory → flush)
          - Atomic commit (begin snapshot → write files → commit)
          - Retry on failure (rollback partial writes)
          - Credential refresh (OAuth token expiry)
          - Schema evolution (ALTER TABLE manually)
          - Orphan file cleanup (failed writes leave GCS files)
```

### Why Cross-Language Matters

```
Iceberg managed.Write เป็น Java SDK transform ที่ถูกเรียกจาก Python:

Dataflow:
┌──────────────────────────────┐
│  Python SDK Harness           │  ← Python DoFns (transform, filter)
│  ↓ (Beam Row)                │
│  Java SDK Harness             │  ← IcebergIO (Java, managed by Beam)
│  ↓ (Iceberg DataFile)        │
│  GCS + BLMS REST Catalog     │  ← Storage layer
└──────────────────────────────┘
Dataflow runs BOTH harnesses in coordinated containers

CloudRun:
┌──────────────────────────────┐
│  Python container ONLY        │  ← Cannot run Java SDK Harness
│  ↓                           │
│  PyIceberg (pure Python)      │  ← Limited functionality
│  ↓                           │
│  GCS + BLMS REST Catalog     │
└──────────────────────────────┘
→ PyIceberg ไม่มี: buffered writes, triggering frequency, auto-create
→ ต้อง implement buffering + flush + atomic commit เอง
```

### Estimated Effort Per Collector

| Task | Effort | Risk |
|------|--------|------|
| Replace managed.Write → PyIceberg | 2 weeks | Credential vending ต่างกัน |
| Build batching layer (replace triggering_frequency) | 1 week | OOM if buffer too large |
| Build atomic commit logic | 1 week | Partial failure = orphan files |
| Build retry + rollback | 1 week | Race condition between workers |
| Build schema evolution | 0.5 weeks | Field ordering mismatch |
| Testing + edge cases | 1.5 weeks | Crash during commit = corrupted table |
| **Total per collector** | **7 weeks** | **× 3 collectors = 21 weeks** |

---

## Risk 6: CDC DELETE — Requires Guarantees That CloudRun Cannot Provide (HIGH)

### ปัญหา — Technical Mechanism

CDC DELETE ของ members-collector มี 3-layer safety ที่ต้องการ exactly-once:

```
CDC DELETE Flow (code จริงจาก api_dofns.py):

Layer 1: Kafka message มี tier_code
  → ถ้า tier_code = None → skip (ไม่ใช่ DELETE case)

Layer 2: API ไม่มี tier นี้สำหรับ member
  → Call API: GET /members/{id}/tiers
  → ถ้า tier_code อยู่ใน response → UPSERT (ไม่ใช่ DELETE)
  → ถ้า tier_code ไม่อยู่ → อาจจะ DELETE

Layer 3: BQ confirms tier existed
  → Query BQ: SELECT program_code FROM member_tier WHERE member_id=X AND code=Y
  → ถ้าพบ → emit _is_delete: True + program_code
  → ถ้าไม่พบ → skip (ไม่เคยมีใน BQ → ไม่ต้อง DELETE)

3-layer ทั้งหมดต้องทำงาน atomically ภายใน 1 bundle:
  → ถ้า Layer 2 pass แต่ Layer 3 fail → retry ENTIRE bundle
  → ถ้า Layer 3 pass แต่ write fail → retry ENTIRE bundle
  → Dataflow guarantees: ไม่มี partial execution ระหว่าง layers
```

#### CloudRun Failure Scenario

```
CloudRun (ไม่มี bundle atomicity):

1. Layer 1: ✅ tier_code = "GOLD"
2. Layer 2: ✅ API says tier removed → DELETE candidate
3. Layer 3: ✅ BQ confirms existed → emit DELETE
4. Write CDC DELETE to BQ: ✅ mutation_type: DELETE
5. Commit Kafka offset: ❌ NETWORK TIMEOUT
6. Container restart → re-read same message
7. Layer 1: ✅ tier_code = "GOLD"
8. Layer 2: ✅ API says tier removed (still)
9. Layer 3: ❌ BQ says NOT FOUND (because step 4 already deleted it!)
10. Skip → ดูเหมือน OK

แต่ถ้าระหว่าง step 6-9 member ได้ tier GOLD กลับมา (re-upgrade):
- Step 4 ลบ GOLD tier ไป
- Step 8: API says tier exists → UPSERT
- ผลลัพธ์ดูเหมือนถูก... แต่!
- ถ้า step 5 succeed + step 8 ไม่เกิด → DELETE ไป 2 ครั้ง (duplicate DELETE)

Edge case ซับซ้อนมาก → investigate ยากเพราะ:
- ไม่มี bundle boundary → ไม่รู้ว่า operation ไหนเป็นของ retry ไหน
- Log กระจายข้าม containers → correlate ยาก
- Timing-dependent bugs → reproduce ไม่ได้
```

> **BQ Storage Write API CDC Documentation** ([BigQuery CDC](https://cloud.google.com/bigquery/docs/change-data-capture)):
> "To use CDC... rows written to the table include a column that indicates the change type (upsert or delete)."
> Beam integration กับ BQ Storage Write API CDC ต้องการ exactly-once delivery guarantee ที่มีเฉพาะใน Dataflow runner

---

## Risk 7: Pipeline DAG → Manual Orchestration (MEDIUM)

### ปัญหา — Technical Mechanism

```
members-collector pipeline DAG (code จริง):

ReadFromKafka(topic1) ──┐
ReadFromKafka(topic2) ──┤
                        ├── Flatten ── Parse ── AttachEventName ── ExtractTriples
                        │
                ┌───────┴───────────────────────────────────┐
                │                                           │
        ExtractPairs                                 ExtractMemberIds
                │                                           │
        DeduplicatePairs                            DeduplicateMemberIds
                │                                           │
        FetchMemberTier (API)                       FetchTierMaintenance (API)
                │                                           │
        ┌───────┴───────┐                           Transform + Write
        │               │                           (Iceberg + BQ)
  ExtractPayload   ExtractTierEvents
        │               │
  Write(Iceberg+BQ) Write(Iceberg+BQ ×2)

Total: 2 inputs → shared processing → 4 output tables
All within 1 pipeline, 1 transaction, 1 drain operation
```

#### CloudRun: ต้องออกแบบ orchestration เอง

```
Option A: Single container ทำทุกอย่าง
  → Monolithic → hard to scale branches independently
  → ถ้า BQ write ของ table 3 ช้า → block ทั้ง pipeline

Option B: Multiple containers + message queue
  → Container 1: Kafka → parse → publish to PubSub
  → Container 2: PubSub → FetchMemberTier → write
  → Container 3: PubSub → FetchTierMaintenance → write
  → ปัญหา: 3 containers × retry × offset tracking = complexity
  → ปัญหา: PubSub costs + latency ระหว่าง containers

Option C: Single container + async
  → asyncio tasks for parallel branches
  → ปัญหา: OOM if too many concurrent tasks
  → ปัญหา: error handling across branches → partial failure
  → ปัญหา: no backpressure on individual branches
```

### Investigation Difficulty

| เรื่อง | Dataflow | CloudRun |
|--------|----------|----------|
| **ดู pipeline flow** | ✅ Dataflow UI แสดง DAG + throughput per step | ❌ ไม่มี — ต้อง trace logs manually |
| **หา bottleneck** | ✅ Per-transform metrics (Dataflow UI) | ❌ ต้อง instrument custom metrics ทุก step |
| **Debug partial failure** | ✅ Bundle retry → all-or-nothing | ❌ ต้อง trace ว่า branch ไหน fail → data inconsistency |
| **Replay specific branch** | ✅ ไม่ต้อง (bundle retry ทำให้) | ❌ ต้อง design replay mechanism per branch |

---

## Risk 8: Monitoring Blind Spots — Silent Data Issues (MEDIUM)

### ปัญหา — Technical Mechanism

Dataflow มี **data-aware metrics** ที่ CloudRun ไม่มี:

```
Dataflow Built-in Metrics (available in Dataflow UI + Cloud Monitoring):
────────────────────────────────────────────────
System Metrics:
- CurrentVcpuCount: จำนวน workers ที่กำลังทำงาน
- BacklogBytes: จำนวน unprocessed bytes ใน Kafka
- DataWatermark: watermark ปัจจุบัน (data completeness indicator)
- SystemLag: เวลาที่ data ใช้ในการ traverse pipeline

Per-Transform Metrics:
- Elements processed per second per transform
- Processing time per element per transform
- Error count per transform

Custom Beam Metrics (code จริงจาก api_dofns.py):
- extract_member.events_seen: จำนวน events ที่เข้ามา
- extract_member.events_extracted: จำนวนที่ extract สำเร็จ
- fetch_member_tier.deletes_emitted: จำนวน CDC DELETE
- dedup_pairs.duplicate_pairs: จำนวน duplicates ที่ถูกกรอง
→ ทั้งหมด aggregated across ALL workers → single dashboard

CloudRun Metrics (Cloud Monitoring):
────────────────────────────────────────────────
- Request count per container
- CPU/Memory per container
- Startup latency
→ ไม่มี: data throughput, processing lag, backlog, watermark
→ Custom metrics: per-container only, ไม่ aggregate across instances
```

### ตัวอย่าง: Silent Kafka Lag

```
Scenario: API downstream ช้าลง → Kafka lag สะสม

Dataflow:
- BacklogBytes metric เพิ่มขึ้น → alert fires within 5 min
- DataWatermark ช้าลง → visible in dashboard
- Action: เพิ่ม --max-workers หรือ investigate API

CloudRun:
- ❌ ไม่มี backlog metric
- ❌ Container ดูเหมือน healthy (HTTP 200, CPU normal)
- ❌ ไม่มีใครรู้ว่า Kafka lag สะสม 2 ชั่วโมงแล้ว
- ❌ Business รู้ตอน: "ทำไม member tier ใน report ไม่ update มา 3 ชั่วโมง?"
- Investigation: ต้อง manually check Kafka consumer lag → correlate with BQ freshness → ใช้เวลา 1-2 ชั่วโมง
```

---

## Risk 9: Cost Model — Efficiency at Scale (MEDIUM)

### ปัญหา — Technical Mechanism

```
Iceberg Write Cost Comparison:

Dataflow (batched writes):
- triggering_frequency_secs: 300 (5 minutes)
- 1 atomic commit per 5 min = 12 commits/hour
- Each commit: 1 GCS write (data) + 1 GCS write (metadata) + 1 REST API call
- Cost: 12 × 3 = 36 operations/hour

CloudRun (per-message writes — ถ้าไม่ build batching):
- 100 msg/sec × 3600 sec = 360,000 messages/hour
- 360,000 commits/hour (worst case, no batching)
- Each commit: 1 GCS write + 1 metadata + 1 REST API
- Cost: 360,000 × 3 = 1,080,000 operations/hour

Ratio: 1,080,000 / 36 = 30,000× more GCS operations
(ถ้า build batching ใน CloudRun: ลดลง แต่ต้อง handle OOM + crash recovery)

Iceberg Metadata Bloat:
- 12 commits/hour → 288 snapshots/day → manageable
- 360,000 commits/hour → 8.6M snapshots/day → metadata file ใหญ่มาก → query ช้า
- ต้อง run metadata compaction เป็นประจำ (extra operation)
```

```
Compute Cost Comparison (streaming, 24/7):

Dataflow:
- 1 worker n1-standard-2: $0.120/hr × 730 hr/mo = $87.60/mo
- Autoscale: ช่วง off-peak ลดเหลือ 1 worker
- ช่วง peak: scale to 3 workers = $0.360/hr (temporary)

CloudRun (always-on Kafka consumer):
- Min instances = 1 (ต้อง always-on สำหรับ Kafka)
- 1 vCPU + 2GB: $0.0864/hr + $0.009/hr = $0.0954/hr
- Monthly: $69.64/mo
- BUT: ต้องเพิ่ม logic สำหรับ batching, dedup, monitoring → CPU usage สูงขึ้น
- realistic: 2 vCPU + 4GB = $139.28/mo

ดูเหมือนใกล้เคียง — แต่:
- CloudRun ต้องเพิ่ม: PubSub (ถ้า multi-container), monitoring infra, dedup storage
- Dataflow: ทุกอย่าง included
```

---

## Risk 10: No Job Lifecycle Management (MEDIUM)

### ปัญหา — Technical Mechanism

```
Streaming job lifecycle ที่ Dataflow provide:

┌─────────┐  deploy   ┌─────────┐  update   ┌─────────┐
│ STOPPED │ ────────→ │ RUNNING │ ────────→ │ UPDATED │
└─────────┘           └─────────┘           └─────────┘
                          │                       │
                      drain │              ┌──────┘
                          ↓                ↓
                    ┌──────────┐    ┌─────────┐
                    │ DRAINING │ ──→│ DRAINED │
                    └──────────┘    └─────────┘

- RUNNING → UPDATED: in-place update (graph compatible changes)
  → Kafka state preserved, window state preserved
  → 0 downtime, 0 data loss

- RUNNING → DRAINING → DRAINED: graceful shutdown
  → Process all in-flight data
  → Flush all buffers
  → Commit all offsets
  → Then terminate

CloudRun lifecycle:
┌─────────┐  deploy   ┌─────────┐  new revision  ┌──────┐
│ STOPPED │ ────────→ │ RUNNING │ ──────────────→ │ KILLED│
└─────────┘           └─────────┘ (SIGTERM+10s)   └──────┘

- No drain, no update, no state preservation
- SIGTERM → 10 second grace period → SIGKILL
- Kafka consumer: must rejoin group → rebalance → 30-60s downtime
```

### Kafka Consumer Rebalance Impact

```
CloudRun container replacement:
t=0:    Container A receives SIGTERM
t=0:    Container B starts
t=0-3s: Container B health check
t=3s:   Container B joins consumer group
t=3-30s: Kafka consumer GROUP REBALANCE
         → All partitions reassigned
         → NO messages consumed during rebalance
         → If multiple consumers: ALL consumers pause
t=30-60s: Rebalance complete → resume consuming
t=60s+:  Catch up with accumulated lag

"0 downtime" สำหรับ HTTP — แต่สำหรับ Kafka consumer:
→ 30-60 seconds ไม่มี consumption
→ ทุกครั้งที่ deploy → 30-60s Kafka lag เพิ่ม
→ Deploy 5 ครั้ง/สัปดาห์ × 52 สัปดาห์ = 260 rebalance events/ปี
→ 260 × 45s avg = 11,700 seconds = ~3.25 ชั่วโมง/ปี ที่ data ไม่ถูก process
```

---

## Summary: Risk Matrix

| Risk | Severity | ความน่าจะเป็น | Investigation Difficulty | Recovery Difficulty |
|------|----------|---------------|------------------------|-------------------|
| In-flight data loss on deploy | **CRITICAL** | ทุกครั้งที่ deploy | **สูงมาก** — ต้อง compare offset vs BQ row-by-row | **สูง** — replay risk duplicate |
| No exactly-once | **CRITICAL** | ทุก retry/failure | **สูงมาก** — duplicates ซ่อนใน data จนกว่า BI ผิด | **สูง** — identify + delete duplicates |
| No backpressure | **HIGH** | ทุก traffic spike | **สูง** — OOM log ไม่บอกว่า data ไหนหาย | **สูง** — manual offset reset |
| No streaming primitives | **HIGH** | ตลอดเวลา | **N/A — ต้อง build** | **N/A — 2300-4500 lines of code** |
| No managed Iceberg write | **HIGH** | ตลอดเวลา | **N/A — ต้อง build** | **N/A — 21 weeks effort** |
| CDC impossible | **HIGH** | ตลอดเวลา | **สูงมาก** — timing-dependent bugs | **สูงมาก** — stale data + race conditions |
| No pipeline DAG | **MEDIUM** | ตลอดเวลา | **สูง** — ไม่มี DAG visualization | **ปานกลาง** — manual log tracing |
| Monitoring blind spots | **MEDIUM** | ตลอดเวลา | **สูง** — silent failures | **ปานกลาง** — build observability layer |
| Cost at scale | **MEDIUM** | เมื่อ scale | **ต่ำ** — cost visible in billing | **ปานกลาง** — optimize manually |
| No job lifecycle | **MEDIUM** | ทุกครั้งที่ deploy | **ปานกลาง** — rebalance visible in logs | **ต่ำ** — wait for rebalance |

### จุดสำคัญ: Investigation + Recovery

**ปัญหาที่ใหญ่ที่สุดไม่ใช่ว่า data จะหาย — แต่คือ:**
1. **ไม่รู้ว่าหาย** จนกว่า business report ผิด (อาจเป็นสัปดาห์ภายหลัง)
2. **หาไม่เจอว่าหายตรงไหน** เพราะไม่มี drain accounting, ไม่มี bundle boundary
3. **กู้คืนยาก** เพราะ replay Kafka = risk duplicate, manual offset reset = risk missing data
4. **เกิดซ้ำทุกครั้ง** ที่ deploy, traffic spike, หรือ downstream ช้า

Dataflow แก้ปัญหาเหล่านี้ด้วย guarantees ระดับ framework:
- Drain → 0 data loss on deploy
- Exactly-once → 0 duplicates
- Backpressure → 0 OOM data loss
- Bundle atomicity → 0 partial writes
- Built-in metrics → detect issues ภายในนาที ไม่ใช่สัปดาห์

---

## Conclusion

> ปัญหาหลักของการใช้ CloudRun สำหรับ data pipeline ไม่ใช่ว่า CloudRun แย่ — มันเป็น tool ที่ดีมากสำหรับ HTTP services
>
> ปัญหาคือ data pipeline ต้องการ guarantees ที่ CloudRun ไม่ได้ถูกออกแบบมาให้:
> - **Exactly-once processing** — Dataflow provides, CloudRun doesn't
> - **Graceful drain** — Dataflow provides, CloudRun doesn't
> - **Backpressure** — Dataflow provides, CloudRun doesn't
> - **Streaming primitives** — Dataflow provides, CloudRun doesn't
>
> "0 downtime" ของ CloudRun = 0 downtime สำหรับ **HTTP requests**
> ไม่ใช่ 0 downtime สำหรับ **data processing** — ตรงกันข้าม data จะ lost ทุกครั้งที่ deploy
>
> การ investigate ปัญหา data ที่เกิดจาก CloudRun ยากและใช้เวลามากเพราะ:
> - ไม่มี drain accounting → ไม่รู้ว่า data หายกี่ records
> - ไม่มี bundle boundary → ไม่รู้ว่า operation ไหนเป็นของ retry
> - ไม่มี pipeline metrics → silent failures จนกว่า business สังเกต
> - Cross-container log correlation → ใช้เวลา hours per incident

---

## References

### Google Cloud Official Documentation
- [Dataflow: Stopping a Pipeline (Drain)](https://cloud.google.com/dataflow/docs/guides/stopping-a-pipeline#drain) — "allows the pipeline to finish processing and writing any buffered data"
- [Dataflow: Exactly-Once Processing](https://cloud.google.com/dataflow/docs/concepts/exactly-once) — "guarantees that every record is processed exactly once"
- [Dataflow: Horizontal Autoscaling](https://cloud.google.com/dataflow/docs/horizontal-autoscaling) — "automatically choose the appropriate number of worker instances"
- [Dataflow: Updating a Pipeline](https://cloud.google.com/dataflow/docs/guides/updating-a-pipeline) — in-place update without data loss
- [Cloud Run: Container Lifecycle](https://cloud.google.com/run/docs/container-contract#lifecycle) — "SIGTERM signal... 10 seconds before sending a SIGKILL"
- [Cloud Run: What is Cloud Run](https://cloud.google.com/run/docs/overview/what-is-cloud-run) — "deploy and run stateless containers"
- [BigQuery: Change Data Capture](https://cloud.google.com/bigquery/docs/change-data-capture) — CDC via Storage Write API
- [Choosing a Compute Option](https://cloud.google.com/docs/choosing-a-compute-option) — decision tree

### Apache Beam Documentation
- [Beam Programming Guide: Windowing](https://beam.apache.org/documentation/programming-guide/#windowing) — event time windowing, watermarks, triggers
- [Beam Runner Capability Matrix](https://beam.apache.org/documentation/runners/capability-matrix/) — Dataflow = exactly-once
- [Beam IcebergIO](https://beam.apache.org/documentation/io/built-in/iceberg/) — managed Iceberg write (cross-language)

### Industry References
- Tyler Akidau, "The Dataflow Model" (VLDB 2015) — foundational paper on windowing + watermarks
- Tyler Akidau, "Streaming 101/102" (O'Reilly) — why exactly-once matters for streaming

### Codebase Evidence
- `members-collector/src/application/pipeline/builder.py` — windowing, fan-out, ReadFromKafka
- `members-collector/src/application/pipeline/api_dofns.py` — CDC DELETE, Beam Metrics, dedup
- `members-collector/src/adapters/output/iceberg_sink.py` — managed.Write(ICEBERG)
- `members-collector/config/base.yaml` — triggering_frequency, window_size, CDC config
- `scripts/deploy_dataflow.sh` — drain, update, worker monitoring
