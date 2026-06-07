# 04 — Cost Arithmetic: Naive vs Full TCO

CTO's argument is "by size × event count" — looks favorable for Cloud Run. เอกสารนี้ break down ตัวเลขจริง พร้อม assumption ที่ verify ได้

## Pricing references (asia-southeast1, 2026)

| Service | Unit | Price |
|---|---|---|
| Cloud Run | per vCPU-second | $0.0000240 |
| Cloud Run | per GiB-second | $0.0000025 |
| Cloud Run | per request | $0.0000004 |
| Pub/Sub | per million msgs (delivered) | $40 (egress) |
| Pub/Sub | storage retention (after 7d) | $0.27/GiB-month |
| BigQuery streaming insert (legacy `tabledata.insertAll`) | per GiB | $0.05 (legacy streaming) |
| BigQuery Storage Write API | per GiB | $0.025 |
| BigQuery storage (active) | per GiB-month | $0.020 |
| Bigtable (single node) | per node-hour | $0.65 |
| Bigtable IO | per ops/sec sustained | included with node |
| Dataflow worker (n1-standard-2) | per vCPU-hour | $0.06 + streaming engine ~20% premium |
| Dataflow shuffle | per GiB shuffled | $0.011 |
| GCS Standard | per GB-month | $0.020 |
| GCS Class A operation (write/finalize) | per 1000 ops | $0.005 |
| GCS Class B operation (read/list) | per 1000 ops | $0.0004 |

**Source**: Google Cloud public pricing pages, asia-southeast1, 2026

## Scenario 1: SIMPLE pipeline ที่ low scale (1M events/day, 1KB/event)

Use case: รับ event Pub/Sub → transform เล็ก ๆ → append BQ raw table

### Cloud Run pattern
```
Pub/Sub topic → Cloud Run subscriber → BQ Storage Write API
```

**Cost calculation:**
- Pub/Sub delivery: 1M × 30 = 30M msgs × $40/M = **$1.20/mo**
- Cloud Run: 1M × 30 = 30M requests × $0.0000004 = $12/mo (request fee)
  - Compute: ~5ms × 0.5 vCPU × 0.5 GiB → 30M × 0.005s × ($0.0000240 × 0.5 + $0.0000025 × 0.5) = ~$1.91/mo
  - **= $13.91/mo**
- BQ Storage Write: 1M × 30 × 1KB = 0.9 GiB × $0.025 = **$0.0225/mo (negligible)**
- BQ storage: 0.9 GiB × 0.020 = **$0.02/mo**

**Total: ~$15.15/mo**

### Dataflow pattern
```
Pub/Sub topic → Dataflow streaming job → BQ Storage Write API
```

**Cost calculation:**
- Dataflow worker: 1 × n1-standard-2 (2 vCPU) × 730h × $0.06 × 1.2 (premium) = **$105/mo**
- Streaming engine: included in premium
- Shuffle: minimal (1 hop pipeline) ~$1/mo
- BQ Storage Write: same $0.025/mo
- BQ storage: same $0.02/mo

**Total: ~$106/mo**

### Verdict at SCENARIO 1 (1M events/day)
**Cloud Run: $15/mo. Dataflow: $106/mo.**

🏆 **Cloud Run ถูกกว่า 7×** ที่ scale นี้.

**ผมยอมรับ: ที่ low scale + simple pipeline, Cloud Run ถูกกว่า**

## Scenario 2: CDC/Iceberg pipeline ที่ medium scale (10M events/day, 1KB/event)

Use case: Kafka → CDC processing (with dedup) → BQ refined + Iceberg

### Cloud Run pattern (3-hop)
```
Kafka consumer (Cloud Run service A) →
  Pub/Sub topic shuffle (ordering_key=user_id) →
    Cloud Run service B (CDC dedup, BT state) →
      Pub/Sub topic to-bq + topic to-iceberg →
        Cloud Run service C-bq (Storage Write API CDC) +
        Cloud Run service D-iceberg (single-committer)
```

**Cost calculation:**
- Pub/Sub: 3 hops × 10M × 30 = 900M msgs × $40/M = **$36/mo**
- Cloud Run × 4 services × min_instances=1 always-on:
  - Each: 730h × 1 vCPU × 0.5 GiB × ($0.0000240 + $0.0000025 × 0.5) = ~$67/mo
  - 4 services × $67 = **$268/mo**
- Bigtable for state: 1 node × $0.65 × 730h = **$475/mo** (ใหญ่สุด!)
- BQ Storage Write CDC: 10M × 30 × 1KB = 9 GiB × $0.025 = **$0.225/mo**
- GCS staging for Iceberg: 9 GiB × $0.020 + write ops 30M × $0.005/1000 = **$150/mo** (ops fee dominant)

**Total: ~$929/mo**

### Dataflow pattern
```
Kafka → Dataflow streaming (with dedup, Iceberg, BQ CDC) → outputs
```

**Cost calculation:**
- Dataflow worker: 1-2 × n1-standard-2 × 730h × $0.06 × 1.2 = $105-210/mo
- Streaming engine: included
- Shuffle: 9 GiB × $0.011 = **$0.10/mo**
- BQ Storage Write CDC: same $0.225/mo
- GCS for Iceberg (managed, batched): 9 GiB × $0.020 + ~12 commits/hr × 730h × few ops = **$5/mo**
- BLMS REST: included in BQ

**Total: ~$210/mo**

### Verdict at SCENARIO 2 (10M events/day, CDC + Iceberg)
**Cloud Run: $929/mo. Dataflow: $210/mo.**

🏆 **Dataflow ถูกกว่า 4.4×** — และ correctness ของ CDC ก็ดีกว่า

## Scenario 3: HIGH scale streaming (100M events/day, multi-collector)

Use case: 5 collectors × 20M events/day each = 100M events/day combined

### Cloud Run pattern
- ใช้ 5 sets of services × 4 services each = 20 Cloud Run services
- Pub/Sub hops: 3 × 5 collectors = 15 topics
- ขยาย Bigtable เป็น 3 nodes for IOPS
- Cost (estimate):
  - Pub/Sub: 100M × 3 hops × 30 = 9B msgs × $40/M = **$360/mo**
  - Cloud Run: 20 services × min 1 + autoscale to ~3-5 average = ~30 instance-equivalent × 730h × 1 vCPU × 0.5 GiB = **$2,000/mo**
  - Bigtable: 3 nodes × $0.65 × 730h = **$1,425/mo**
  - BQ + GCS: ~$200/mo
  - Reconciliation jobs: 5 × 1 cron Cloud Run × small = **$30/mo**

**Total: ~$4,015/mo**

### Dataflow pattern
- 5 Dataflow streaming jobs
- Each autoscale 1-3 workers × n1-standard-2 = ~2 worker average × 5 jobs = 10 workers
- Cost:
  - Dataflow: 10 × n1-standard-2 × 730h × $0.06 × 1.2 = **$525/mo**
  - Shuffle: 5 × 18 GiB × $0.011 = **$1/mo**
  - BQ + GCS Iceberg: ~$50/mo
  - BLMS REST: included

**Total: ~$576/mo**

### Verdict at SCENARIO 3 (100M events/day, 5 collectors)
**Cloud Run: $4,015/mo. Dataflow: $576/mo.**

🏆 **Dataflow ถูกกว่า 7×** — gap widens with scale and pipeline count

## Scenario 4: Backfill 30 days from cold storage

Same data set 100M events/day × 30 days = 3B events

### Cloud Run pattern (re-publish via Pub/Sub)
- Pub/Sub: 3B × $40/M = **$120 (one-time)**
- Cloud Run: 3B × 5ms × 1 vCPU = 15M vCPU-sec × $0.000024 = **$360 (one-time)**
- BT state writes: similar cost
- **Wall-clock time: ~35 days at sustained Cloud Run throughput**

### Dataflow batch pattern
- Read source bounded (Iceberg / BQ): no message fee
- Workers autoscale 50 × n1-standard-4 × 4 hours = **$48 (one-time)**
- Shuffle: 3B × 1KB / 1024 = 2.7 TiB × $0.011 = **$30 (one-time)**
- BQ writes: same cost
- **Wall-clock time: ~4-6 hours**

### Verdict at SCENARIO 4 (backfill 30 days)
**Cloud Run: $480 + 35 days. Dataflow: $78 + 4 hours.**

🏆 **Dataflow 6× cheaper + 200× faster** — backfill is unworkable in Cloud Run pattern

## Scenario 5: TCO over 3 years × 8 collectors

Combined estimate based on scenarios above + engineering effort

### Cloud Run pattern
| Item | Cost |
|---|---|
| Cloud infra Year 1 (avg 50M evt/day combined, all 8 collectors) | $3,500/mo × 12 = **$42K** |
| Cloud infra Year 2 (scale up to 80M/day) | $5,500/mo × 12 = **$66K** |
| Cloud infra Year 3 (100M+/day) | $8,000/mo × 12 = **$96K** |
| Engineering migration (8 collectors × 8-12 weeks × $5K/wk) | **$320K-$480K** |
| Custom CDC/Iceberg library development (1-time) | **$80K-$120K** |
| Reconciliation pipelines (8 × $10K each) | **$80K** |
| Maintenance overhead Year 2-3 (each pipeline unique) | **$60K/yr × 2 = $120K** |
| Incident response (3-4 incidents/yr × $5K each × 3 yr) | **$45K-$60K** |
| **3-year TCO** | **$853K - $1.06M** |

### Dataflow pattern (continuing current approach)
| Item | Cost |
|---|---|
| Cloud infra Year 1 | $1,000/mo × 12 = **$12K** |
| Cloud infra Year 2 | $1,500/mo × 12 = **$18K** |
| Cloud infra Year 3 | $2,000/mo × 12 = **$24K** |
| New collectors (5 × 2-3 weeks × $5K/wk) | **$50K-$75K** |
| Maintenance shared codebase | **$20K/yr × 3 = $60K** |
| Incident response (~0.5/yr × $5K × 3) | **$7.5K** |
| **3-year TCO** | **$172K - $197K** |

### Verdict TCO over 3 years
**Cloud Run pattern: ~$1M. Dataflow pattern: ~$200K.**

🏆 **Dataflow ~5× cheaper TCO** at this scope

## Caveats and assumptions

### ที่ Cloud Run ตัวเลขผมอาจ off
- ถ้า low scale + simple pipelines เท่านั้น (< 5M events/day, no CDC/Iceberg) → Cloud Run จะถูกกว่า ตามสมมุติ
- ถ้าใช้ shared Cloud Run service (multiple collectors share 1 service) → ลด min-instance cost
- ถ้าใช้ pull subscription แทน push (อาจลด some hops)

### ที่ Dataflow ตัวเลขผมอาจ off
- ถ้าใช้ Dataflow Prime (cost optimization) → อาจลดเพิ่ม 20-30%
- ถ้า workload spiky มาก → autoscale-down อาจไม่ทัน, ทำให้ utilization ต่ำ
- Streaming engine premium อาจ off-by 10-15%

### Assumptions ที่ใช้
- 1KB/event average size
- Pub/Sub egress cost only (intra-region free for ingress)
- Cloud Run min_instances=1 always-on (because streaming workload)
- Bigtable required for state (per-key dedup, lookup)
- 30-day BQ retention assumed
- Engineering rate $5K/wk = senior data engineer fully loaded

## ตัวเลขที่ใช้ใน CTO meeting

> "ที่ scale > 10M events/day per collector, Cloud Run pattern แพงกว่า Dataflow 4-7×.
> ที่ portfolio scope ของ The1 (8-12 collectors), 3-year TCO Cloud Run ~$1M, Dataflow ~$200K — gap ~$800K.
> ตัวเลขนี้ใช้ public pricing + reasonable assumptions. ขอ challenge ตัวเลขนี้ — ผิดจุดไหน?"

> "เห็นด้วยว่า Cloud Run ถูกกว่าที่ < 5M events/day per collector + simple pipeline. แต่ที่ workload ของเราจริง — multi-collector, CDC, Iceberg, sustained streaming — economics เอียง Dataflow ชัดเจน"

## Crossover point

Cost crossover ที่ traffic ใด: ~5-10M events/day per collector for simple pipeline. CDC/Iceberg pattern crossover ต่ำกว่านี้ (Dataflow ถูกกว่าทันทีจากคุณสมบัติ batched commits ที่ Beam มี)

**Decision rule (เสนอใช้):**
- Workload < 5M events/day + append-only → **Cloud Run OK**
- Workload > 10M events/day → **Dataflow**
- CDC + Iceberg + windowing → **Dataflow** (แพงกว่าตอนเริ่ม, ถูกในระยะยาว, correctness ดีกว่า)
- HTTP API + light ingestion → **Cloud Run** (ที่ทีม insight ทำอยู่แล้ว)

## Note about insight current pattern

ที่ insight ปัจจุบันใช้ Cloud Run pattern + Pub/Sub→BQ direct + ROW_NUMBER view, work อยู่ได้เพราะ:
- Volume ยังไม่สูงมาก (estimate < 20M events/day)
- ไม่ทำ true CDC (append-only + view) — accepted limitation
- ไม่ทำ Iceberg writes ตรง (ใช้ BQ Pub/Sub direct + ClickHouse via GCS)
- Operations team handle 8 services + 8 topics ได้ใน scope ปัจจุบัน

ถ้า scale 5×, Cloud Run cost จะกระโดด (Pub/Sub hops × 5 = $1,800/mo, services × 5 instances avg = $$$$)
