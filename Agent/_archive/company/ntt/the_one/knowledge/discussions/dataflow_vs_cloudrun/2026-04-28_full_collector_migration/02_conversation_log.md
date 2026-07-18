# 02 — Conversation Log (User ↔ AI Architect)

Capture conversation chronologically — เพื่อให้เห็นว่า argument ค่อย ๆ refine ยังไง

User = data architect ของทีม data
AI = architect-side advocate (this assistant)

## Round 1 — Verify CDC claim from code

### User asks
> เค้ากลับมารื้อฟื้นอีก ว่าอยากใช้ Cloud Run เพราะถูกกว่า และสามารถทำ incremental CDC ลง BQ ได้ แต่ผมคุ้น ๆ ว่าไอท่าที่เค้าทำ มันไม่ใช่ในมุมที่ data pipeline ควรทำ
>
> Compute นี่ทำที่ไหน? เป็น micro-batch หรือ realtime? แล้วมัน write CDC ลง BQ จริงไหม? หรือแค่ write BT แล้วเอา view BQ ครอบ?

### AI verdict (verified จาก code)

จาก grep ทั้ง insight repo + อ่าน code/TF/SQL จริง:

**`Compute` = `computePersonaTraitUseCase` ใน Collector** (Node.js Cloud Run) — function ที่ run ใน `runInBackground` ต่อ event. **Per-event realtime in-process function** ไม่ใช่ micro-batch

**ไม่ใช่ CDC.** Code ใช้:
- `BigQueryClient.ts:43-50`: `dataset(...).table(...).insert([row])` = legacy `tabledata.insertAll` streaming insert (append-only)
- Persona เขียน BigTable ตรงผ่าน `btTable.mutate()` ที่ `save.service.ts:30-72` — BigTable คือ source of truth
- Pub/Sub UPSERT message ไป `personas-collector` topic
- Pub/Sub→BQ direct subscription (`enable_exactly_once_delivery=false`) ที่ `infrastructure/personas/api/pub-sub.tf:31-60` → append `personas_changelogs` table
- VIEW `insight.personas` (ที่ `personas/api/sql/personas-dataflow.sql:19-40`):
  ```sql
  CREATE OR REPLACE VIEW insight.personas AS
  SELECT *, ROW_NUMBER() OVER (PARTITION BY personaId ORDER BY timestamp DESC) AS rn
  FROM insight.personas_changelogs WHERE rn=1
  ```

**Verdict:** ตรงตามที่ user สงสัย — write BT (source of truth) + append changelog ที่ BQ + VIEW ROW_NUMBER ครอบ. **ไม่ใช่ CDC** ในนิยาม engineering (no `_CHANGE_TYPE`, no `MERGE`, no `primary_key`, no `max_staleness`, no Storage Write API CDC mode)

---

## Round 2 — User asks for "must-be-Dataflow" arguments

### User asks
> มีข้อโต้แย้งอะไรไหม แบบ เหตุผลที่ must be Dataflow/Dataproc คือ mindset เค้าอยากจะใช้ Cloud Run ทุกอัน

### AI's first attempt (data architect framing)

**Frame**: "Cloud Run for everything" = category error — เอาวิธีคิด API engineering มาใช้กับ data engineering. สอง discipline ต่างกัน

**Argument list (8 ข้อหลัก)**:
1. Data correctness ≠ API correctness — exactly-once vs eventual consistency
2. "Small transform" คือ trap — ทุก transform จะค่อย ๆ ขึ้นความซับซ้อน
3. Stateful processing เป็น primitive ที่ Cloud Run stateless ทำไม่ได้
4. Time semantics (event time, watermark) — Cloud Run ไม่รู้จัก
5. Schema = contract — Cloud Run pattern ใช้ Pub/Sub→BQ direct → schema drift silently
6. Replay/backfill — Cloud Run ทำไม่ได้แบบ deterministic
7. Lineage/observability ต่างกัน — "200 OK" ไม่ได้แปลว่าข้อมูลถูก
8. Economics flip ที่ scale — Cloud Run แพงกว่าที่ sustained streaming

**Closing principle**: "Beam exists เพราะ streaming/batch มี properties ที่ HTTP service framework + DB client ทำให้ไม่ได้"

---

## Round 3 — User pushes back: arguments are "soft"

### User pushback
> ใช้เหตุผลแบบขอไปทีแบบนี้ไม่ได้นะ เพราะคนที่เถียงคือ CTO
>
> 1. "Small transform" — เค้าจะบอกว่าไม่เห็นเป็นไร ใน dataflow collector อื่น ๆ ก็ไม่เห็นแก้ปัญหาตรงนี้, แก้ที่ semantic ได้เพราะตรงนั้นใช้ dataform
> 2. "Schema = contract" — เค้าก็จะหาทางแก้ได้, เพราะ Pub/Sub มี versioning สำหรับ schemas
> 3. ข้ออื่น ๆ จะเจอ "ก็ custom สิ"
>
> มันยังไม่ใช่ use case ที่แสดงความต่างชัดเจนระหว่าง Cloud Run กับ Dataflow
>
> ถ้าเข้าประชุม "เครื่องมืออย่าง Beam มีอยู่เพราะ streaming มี properties ที่ HTTP ทำไม่ได้" จะโดนสวนกลับ "แน่ใจหรอ มันทำได้นะ"
>
> เค้าอยากเห็นข้อจำกัดชัด ๆ ที่เถียงไม่ออก

### AI's second attempt — 5 Hard Limits (architectural primitives)

**Reframe**: "shift จาก feature comparison เป็น distributed systems primitives"

**5 Hard Limits:**
1. **Shuffle** (key-based redistribution across workers) — Cloud Run instances ไม่ communicate กัน
2. **Backpressure** — Cloud Run + Pub/Sub push ไม่สามารถบอก source ให้ช้าลง
3. **Atomic commit across multiple sinks** (BQ + Iceberg + Kafka offset) — exactly-once across heterogeneous systems
4. **Iceberg/Lakehouse atomic snapshot** — single coordinator commits required
5. **Watermark across distributed workers** — global state ของ event-time progress

**Concrete scenarios** (5 ตัวอย่าง pin CTO):
- Hot key (1 user 10K events/sec)
- Out-of-order events (mobile retry 10 min late)
- Backfill 30 days (35 วัน to replay if Cloud Run, 2-3 hr if Beam)
- Streaming join 2 sources with broadcast tier table
- Iceberg write 50 instances simultaneously

**Closing**: "คุณกำลังบอกว่าทีมจะมาเขียน infrastructure software แข่งกับ Google's data infra team. คุณเซ็นใจในเรื่องนี้ได้ไหม?"

---

## Round 4 — User pushes back AGAIN: "you'd rebuild Beam" is too soft

### User pushback (sharp)
> "ใช่ ทำได้. คำถามคือ คุณอยาก build worse version of Dataflow หรือใช้ Dataflow?" — แบบนี้ไม่ใช่เหตุผลที่ดี เดี๋ยวก็โดนสวนกลับอีก
>
> และจาก 5 Hard Limits ที่คุณบอก คิดว่าถ้าใช้ solution คล้าย ๆ ใน collector ตอนนี้ทำได้ไหม? ลองคิดว่าถ้าต้องเพียงกับคนดื้อจะใช้ Cloud Run อะ ต่อให้อ้อมหลาย service ต่อกับ Pub/Sub sub เพิ่ม เค้าก็ทำได้ไง
>
> คุณลองคิดดูว่ามันทำได้หรือเปล่า

### AI's HONEST re-evaluation

**ยอมรับ**: ผมแพ้ใน argument เชิง possibility. ทุก hard limit ที่บอกไป Cloud Run ทำได้จริงถ้ายอมเพิ่ม service + complexity:

| Limit | Cloud Run solution | Architectural? |
|---|---|---|
| Shuffle | Pub/Sub ordering key + BT state | ✓ Works (with cost/latency penalty) |
| Backpressure | streaming pull subscription | ✓ Works (collector ปัจจุบันก็ทำ) |
| Atomic commit | CDC chain pattern (eventual consistency between stages) | ✓ Works (Netflix/Pinterest pattern) |
| Iceberg snapshot | single-committer service (max_instances=1) | ✓ Works (throughput cap) |
| Watermark | processing-time windows + reconciliation | ✓ Works (lose event-time correctness) |

**Shift frame**: จาก "possibility" → **"engineering cost reality + economics at scale"**

**Walk-through ของ "shuffle aggregation" pattern in Cloud Run**:
- 4 services + 1 Pub/Sub topic + 4 DLQ + 1 BT table + 2 cron jobs + 5 monitoring dashboards
- ~3,000-5,000 LoC
- vs Beam: 30 LoC, 1 pipeline

**Cost arithmetic (100M events/day)**:
- Cloud Run pattern: ~$20,600/mo (mainly Pub/Sub hops)
- Dataflow pattern: ~$700-4,600/mo
- **Cloud Run is 5-30× more expensive** at this scale, **driven by Pub/Sub multi-hop**

**TCO over 5 pipelines × 3 years**:
- Cloud Run pattern: ~$3.7M
- Dataflow pattern: ~$210K

**Argument that won't get rolled**:
- Concede possibility upfront: "เห็นด้วยว่า Cloud Run ทำได้ — แต่เป็นเรื่อง economics + TCO"
- ถาม operational sprawl: "8 services + 8 topics for ONE event flow ตอนนี้, scope 5 use case = 40 services"
- ถาม cost numbers: "$20K vs $700/mo at 100M/day — challenge ตัวเลขผม ?"
- ขอ design doc: "ให้ design Cloud Run version ของ CDC + Iceberg + windowed pipeline"

---

## Round 5 — User clarifies the actual proposal scope

### User clarifies
> ที่เค้าจะเอามาแก้ คือทุก collector ในโปรเจ็ค data
>
> ปกติ kafka (source อื่น cost ไม่อยู่ในเจค) > dataflow per job > bq per table + storage write API
>
> มันจะเป็น pubsub subscription > cloudrun > bq + bq client/storage write api/pubsub topic (push and direct write to bq)
>
> โดยคิดเงิน by size + amount of event ไง เค้าจะมาเถียงได้อีก
>
> เพราะมันดูง่ายและถูกกว่า แต่ใน long term ไม่น่า work
>
> เพิ่มมาเป็นเอกสารอีกชุดในโฟลเดอร์ discussion เอาคำตอบของคุณแต่ละอันมาด้วย จะได้เห็นว่าคุยอะไรกัน

### AI response (this doc set)

**Important findings from clarification:**

1. **Scope = ALL collectors in project data** — ไม่ใช่แค่ insight. ยังรวม loyalty (purchases/members/tiers/m-t-h), customer-profile V3/V4, last-purchases, customer-svoc-interim — collectors ที่เรา invest มาแล้ว

2. **CTO's cost calc = "by size × event_count"** — partial truth ที่ดู favorable for Cloud Run ที่ low scale. Honest analysis ต้องรวม:
   - Multi-hop Pub/Sub
   - State store (BT/Redis) IOPS
   - Engineering effort
   - Reconciliation jobs
   - DLQ replay infra
   - Operational on-call burden
   - Migration cost (forfeit existing Beam infra)
   - Multi-toolchain tax

3. **"ดูง่าย/ถูก short-term, long-term ไม่ work"** — user's intuition ตรง. Long-term issues:
   - Operational sprawl (services × topics × subs explosion)
   - Cost crossover at scale
   - Data quality drift (no CDC = silent corruption)
   - Migration trap (custom code in N pipelines = rewrite pain)
   - Skill set divergence (data team vs app team)

**Action**: เอกสารชุดนี้ถูกสร้างขึ้นเพื่อ
- Capture honest technical position (ไม่ overplay limits)
- ให้ ammunition ที่ defensible against CTO pushback
- Document conversation thread เพื่อ continuity ครั้งหน้า

---

## Honest Position สรุป (สิ่งที่ AI architect ยึด)

> **"Cloud Run + Pub/Sub orchestration ทำ data pipeline ทุกประเภทได้ — แต่ที่ scale + portfolio ของ The1 (loyalty + insight + messaging combined > 100M events/day, 8-12 collectors) economics และ operational TCO เอียงไป Dataflow ชัดเจน."**
>
> **"คำถามที่ถูกต้องไม่ใช่ 'Cloud Run vs Dataflow' — คือ 'ที่ scope งานเรา, infrastructure pattern ไหน TCO ต่ำที่สุดในระยะ 3 ปี?'"**
>
> ถ้า CTO ตอบจาก "size × event count" → คำตอบนั้น **incomplete**. ครบจริงต้องรวม **engineering effort + ops + risk + sunk cost**

ดูตัวเลขเต็มที่ [04_cost_arithmetic.md](04_cost_arithmetic.md), evaluation ที่ [03_honest_evaluation.md](03_honest_evaluation.md), per-collector ที่ [05_per_collector_assessment.md](05_per_collector_assessment.md)
