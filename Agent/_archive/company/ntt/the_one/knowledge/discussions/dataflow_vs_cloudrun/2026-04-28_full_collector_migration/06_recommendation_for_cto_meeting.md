# 06 — Recommendation for CTO Meeting (Playbook)

Position to take + meeting flow + verbal scripts

## 🎯 Position สรุป (เปิดด้วย this)

> **"ทีม data ไม่ได้ refuse Cloud Run. เราใช้ Cloud Run อยู่แล้วใน customer-svoc-collector + insight collector pattern. คำถามที่ debate คือ scope: ที่ workload ระดับ CDC + Iceberg + windowed streaming, Cloud Run pattern จะ TCO ต่ำกว่าจริงเมื่อ rebuild ทุก capability ที่ Beam มีให้ มาเอง?**
>
> **คำตอบจาก code + cost arithmetic ของผม: ที่ scope The1 (8-12 collectors, 100M+ events/day combined), Dataflow pattern 3-year TCO ~$200K, Cloud Run pattern ~$1M. Gap ~$800K. ตัวเลขนี้ขอ challenge ผิดจุดไหน?"**

นี่คือ frame ที่:
- ไม่ defensive ไม่ดื้อ
- ยอมรับ Cloud Run มี place
- ใช้ TCO numbers (CTO เข้าใจ)
- ขอให้ CTO แสดงสิ่งที่ผิด (shifts burden)

## 🎬 Meeting Flow

### Stage 1: Concede + Anchor (5 min)

> **เปิด:** "ขอ concede 2 ข้อก่อน:
> 1. **Cloud Run ทำได้** ทุก data pipeline ที่เรามีถ้ายอม custom + add services + sacrifice properties บางอย่าง
> 2. **ที่ low scale + simple pipeline (< 5M events/day, append-only), Cloud Run ถูกกว่า** Dataflow จาก direct cloud cost
>
> ที่ทีมเรา push back **ไม่ใช่** เรื่อง 'Cloud Run can't do it'. เป็นเรื่อง:
> - ที่ scope งานเรา (8-12 collectors, sustained streaming, CDC, Iceberg), economics ของ Cloud Run pattern เอียงไม่เอื้อ
> - existing Beam investment ที่ใช้งานได้ + correctness สูง — ราคา throw away สูง
> - operational sprawl ที่ Cloud Run pattern ก่อ — เห็นแล้วใน insight ปัจจุบัน (8 services + 8 topics for 1 event flow)"

**Why this works:** CTO มาประชุมคาดเจอ defensive arguments ("Beam ดีกว่า!"). Conceding upfront = disarm และเปลี่ยน frame ทันที

### Stage 2: TCO Numbers (10 min)

> "เอาตัวเลข cost ที่ผม model มา challenge ดู — ดูจาก [04_cost_arithmetic.md](04_cost_arithmetic.md):
>
> | Scenario | Cloud Run | Dataflow | Winner |
> |---|---|---|---|
> | 1M events/day, simple append | $15/mo | $106/mo | Cloud Run 7× |
> | 10M events/day + CDC + Iceberg | $929/mo | $210/mo | Dataflow 4.4× |
> | 100M events/day, 5 collectors | $4,015/mo | $576/mo | Dataflow 7× |
> | Backfill 30 days | $480 + 35 days | $78 + 4 hr | Dataflow 6× cost, 200× speed |
> | **3-year TCO 8 collectors** | **$1.0M** | **$0.2M** | **Dataflow 5×** |
>
> ตัวเลขใช้ public pricing + reasonable assumptions. ขอ ask 3 อย่าง:
> 1. Pricing assumption ไหนผิด?
> 2. Workload pattern assumption ไหนผิด? (size, event count, hops, state IO)
> 3. Engineering effort assumption ไหนผิด? (8-12 weeks/collector × 8 collectors)
>
> ถ้า CTO ตอบมา → revise math. ถ้าไม่ตอบมา → number stands"

**Why this works:** Numbers force specificity. CTO เก่งจริงจะ challenge specific assumption — ที่ไหนเก่งจริงผม revise ได้. ที่ไหนไม่ challenge = number stands

### Stage 3: Per-Collector Assessment (10 min)

> "Migration scope = 'all collectors'. ผมแยก collectors เป็น 3 tiers based on complexity:
>
> **Tier A — Keep Beam (6 collectors)**: members-collector, customer-profile-pipeline V3, tiers-collector, m-t-h-collector, purchases-collector, coupons-collector
>   - เหตุผล: CDC DELETE 3-layer safety, windowed S3+Iceberg merge, code reuse, other team's
>   - Migration cost: $640-860K
>   - Migration risk: high (correctness)
>
> **Tier B — Negotiable (2 collectors)**: customer-profile-collector V4, last-purchases-collector
>   - เหตุผล: simpler CDC, possible migrate ถ้า scope clear
>
> **Tier C — Already done or easy (2 collectors)**: customer-svoc-collector (done), customer-svoc-interim (cheap migrate)
>
> Challenge: ขอให้ CTO design Cloud Run version ของ **members-collector CDC DELETE 3-layer safety** ก่อนที่เราตกลง migrate ตัวอื่น. ถ้า design ออกมาแล้ว effort + correctness OK → ผมจะ believe migration plan"

**Why this works:** บังคับ CTO ทำ design ของ collector ที่ยากที่สุดก่อน. ถ้า design = เห็น sprawl. ถ้าไม่ design = ยอมรับว่า "yes, all collectors" คือ overcommit

### Stage 4: Counter-proposal (5 min)

> **เสนอแทน 'all collectors migrate':**
>
> **Tiered Strategy:**
> 1. **Keep Tier A on Beam** — proven, deployed, working
> 2. **POC Tier B/C on Cloud Run** — pick 1 collector (last-purchases-collector recommended), 3-month POC
> 3. **Measure** — cost, incidents, latency, dev velocity
> 4. **Decide based on data** — ไม่ extrapolate, ไม่ big-bang
>
> ถ้า POC พบ Cloud Run ดีกว่าจริง 30%+ → consider expand Tier B
> ถ้า POC พบ tied หรือ worse → stop migration
>
> **Investment**: 1 collector × 8 weeks = $40K POC budget. Result-driven decision — ไม่ใช่ ideology-driven"

**Why this works:** Counter-proposal นี้ CTO ปฏิเสธยาก เพราะ:
- ใจกว้าง (ทำ POC จริง)
- Risk-managed (1 collector ก่อน)
- Decision-rule-based (ตัดสินจาก measurement)
- Limited budget (POC ไม่ใช่ multi-million migration)

### Stage 5: Specific Demands (5 min)

ก่อน end meeting ขอ commitments ชัด ๆ:

1. **Documentation requirement**: "ก่อน migrate collector ใด ๆ, ขอ design doc ที่:
   - Cloud Run service inventory (จำนวน services, Pub/Sub topics, BT/state stores)
   - Capability parity check (CDC, Iceberg, windowing — what's preserved/lost)
   - Migration plan (parallel run, validation, rollback)
   - 12-month TCO projection"

2. **POC commitment**: "POC last-purchases-collector ใน 3 เดือน. Measure 5 KPIs (cost, incidents, p99 latency, throughput, dev cycle time). ตัดสินใจ Tier B based on data"

3. **No big-bang**: "ไม่ migrate Tier A (members-collector, customer-profile-pipeline V3) ก่อน POC + Tier B success"

4. **Sunk cost respect**: "Beam infra investment ใน loyalty 3 collectors + insight V4 — ไม่ retire จนกว่า Cloud Run version พิสูจน์ functional + cost parity"

## 🛡️ Defensive Plays (ถ้า CTO push back)

### CTO claim: "Cost calc ของแกทุน Pub/Sub hop เกิน. เราใช้ 1 hop ก็พอ"

**Reply:** "ใช่ — ที่ 1 hop pattern (Pub/Sub→Cloud Run→BQ direct), Cloud Run คุ้ม. แต่ pattern นั้น = append-only + lose CDC. แสดง code Cloud Run version ของ members-collector CDC DELETE ใน 1 hop ได้ไหม? ผมว่าทำไม่ได้ — ต้อง 3+ hops minimum"

### CTO claim: "Beam คือ over-engineering. Simple is better"

**Reply:** "เห็นด้วยกับ 'simple is better'. แต่ที่ data correctness needs of CDC + DELETE = simple ไม่พอ. ที่ insight ตอนนี้ใช้ append + view trick — work OK, แต่:
- ลบ persona ไม่ได้ (GDPR delete request = manual SQL)
- view scan cost growth (ROW_NUMBER scan whole table)
- duplicate rows from Pub/Sub at-least-once
- BT↔BQ drift potential
ที่ scale 5× ปัจจุบัน, pattern นี้จะแตก"

### CTO claim: "ทีม data เก่ง Beam — ไม่ต้องการเรียน Cloud Run"

**Reply:** "ทีม data ใช้ TypeScript Cloud Run ใน customer-svoc-collector แล้ว. ไม่ใช่ 'ไม่เก่ง'. คำถามคือ for streaming + CDC workload, tool ไหน TCO ต่ำกว่า. ผมเสนอ POC measure แทน argue"

### CTO claim: "Dataflow มี vendor lock-in. Cloud Run portable กว่า"

**Reply:** "Dataflow runner = Apache Beam SDK ที่ portable to Spark/Flink/Direct runner. Cloud Run + Pub/Sub + BQ direct = lock-in to GCP services. Lock-in argument cuts both ways"

### CTO claim: "Composer + Dataflow + GAR = infrastructure overhead"

**Reply:** "เห็นด้วยว่า Composer + Dataflow มี baseline cost. แต่:
- Composer: insight ปัจจุบันก็มี (data-pipeline/composer.tf)
- Dataflow GAR: ใช้ template-based deploy ไม่ overhead operationally
ที่ insight current pattern ก็มี: 8 Cloud Run services + 8 Pub/Sub topics + EventArc + BT + BQ + view layer + GCS + ClickHouse — sprawl ไม่ได้น้อยกว่า"

### CTO claim: "นี่คือ technical decision ของเค้า ทีม data ไม่มีสิทธิ์เถียง"

**Reply:** "Decision ของ CTO ต่อ tech direction — เคารพ. แต่ทีม data รับผิดชอบ correctness ของ data + on-call สำหรับ data incidents. ขอ alignment เพื่อ:
1. Decision-making process ที่ data team voice in (especially data correctness implications)
2. POC + measure ก่อน big-bang
3. Document trade-offs explicitly เพื่อ future reference (แทนที่จะ revisit ทุก 6 เดือน)"

## 📋 Materials to bring to meeting

1. **เอกสารชุดนี้** (6 docs ใน `dataflow_vs_cloudrun/2026-04-28_full_collector_migration/`)
2. **Cost spreadsheet** (paste ตาราง 04_cost_arithmetic.md ลง Sheets)
3. **Per-collector matrix** (paste 05_per_collector_assessment.md)
4. **insight architecture proof** ([insight/doc/insight-api/05_BQ_WRITE_SEMANTICS_PROOF.md](../../../../../insight/doc/insight-api/05_BQ_WRITE_SEMANTICS_PROOF.md)) — ที่พิสูจน์ว่า insight ตอนนี้ "ไม่ได้ทำ CDC จริง"
5. **loyalty members-collector code** สำหรับ show CDC DELETE 3-layer pattern (file references)

## 🎤 Closing Statement

ใช้นี้ปิด:

> "ทีม data **ไม่ได้** มาเถียงว่า Cloud Run ผิด. เราใช้ Cloud Run อยู่แล้ว. ที่เถียงคือ **scope + scale**.
>
> ที่ scope งาน CDC + Iceberg + windowed streaming + 100M events/day across 8-12 collectors, Beam/Dataflow มี TCO ต่ำกว่า ~5× ในช่วง 3 ปี + correctness ดีกว่า + risk ต่ำกว่า. ตัวเลขในเอกสาร, ขอ challenge.
>
> ที่เสนอ counter คือ **POC 1 collector 3 เดือน + measure-driven decision**. ไม่ใช่ big-bang migrate. ผ่าน metrics → expand. ไม่ผ่าน → keep Beam.
>
> Decision rule นี้เป็น engineering, ไม่ใช่ ideology. เห็นด้วยไหม?"

ถ้า CTO เห็นด้วย — POC win
ถ้า CTO ไม่เห็นด้วย — ขอ rationale ที่ specific (ไม่ใช่ "ผมตัดสินใจแล้ว")

## ❌ สิ่งที่ **ไม่ควรพูด** ในประชุม

- ❌ "Beam ดีกว่า" (vague, ego-trigger)
- ❌ "Cloud Run ทำไม่ได้" (false — ทำได้)
- ❌ "Dataflow คือ Google's recommendation" (appeal to authority)
- ❌ "ผม 10 ปี data engineer" (status arg, ทำให้ CTO จะหา way กลับมา)
- ❌ "ทีม Lyft/Spotify/Netflix ใช้ Beam" (irrelevant — context ต่างกัน)
- ❌ "พวกคุณไม่เข้าใจ data engineering" (insulting + escalates)

✅ สิ่งที่ควรพูด: **ตัวเลข + scope + risk + counter-proposal**
