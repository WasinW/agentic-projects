# 05 — Per-Collector Migration Assessment

ประเมินทีละ collector ที่ CTO ขอ migrate. แต่ละตัว: complexity, what we'd lose, migration cost, Cloud Run viability

## Summary table

| Collector | Tech ปัจจุบัน | CDC needed? | Iceberg? | Windowing? | Migrate viable? | Effort | Recommendation |
|---|---|---|---|---|---|---|---|
| **purchases-collector** (loyalty) | Beam streaming | ✓ (UPSERT) | ✓ | ✗ | ⚠ ทำได้ แต่ลด correctness | 8-10 wk | **เก็บ Beam** |
| **members-collector** (loyalty) | Beam streaming, Schema A/B/C unwrap, CDC DELETE 3-layer | ✓ (UPSERT+DELETE) | ✓ | ✗ | ✗ ไม่ปลอดภัย | 12-16 wk + risk | **เก็บ Beam (critical)** |
| **tiers-collector** (loyalty) | Beam batch (1AM cron) | ✓ (UPSERT) | ✓ | ✗ | ⚠ Cloud Run cron + custom | 6-8 wk | **เก็บ Beam (รัน batch ก็ใช้ Beam ได้)** |
| **members-tiers-history-collector** (loyalty) | Beam batch | ✓ | ✓ | ✗ | ⚠ คล้าย tiers | 6-8 wk | **เก็บ Beam** |
| **coupons-collector** (loyalty, planned) | Not yet built | TBD | TBD | TBD | TBD | TBD | **เริ่มด้วย Beam (consistency)** |
| **customer-profile-collector V4** (insight) | Beam streaming | ✓ | ⚠ external | ✗ | ⚠ ทำได้ (ลด correctness) | 8-10 wk | **negotiable** |
| **customer-profile-pipeline V3** (insight) | Beam streaming + windowed S3 + Iceberg merge + Consent SQL | ✓ | ✓ | ✓ (FixedWindows 5min) | ✗ ซับซ้อนมาก | 14-18 wk | **เก็บ Beam (critical complexity)** |
| **last-purchases-collector** (insight) | Beam streaming Pub/Sub→BQ CDC | ✓ | ✗ | ✗ | ✓ ทำได้ (simple CDC) | 4-6 wk | **negotiable** |
| **customer-svoc-collector** (insight) | Cloud Run (FastAPI) แล้ว | ✗ | ✗ | ✗ | N/A (already Cloud Run) | 0 | **คงเดิม** |
| **customer-svoc-interim** (insight) | Beam batch | ✗ | ✗ | ✗ | ✓ Cloud Run cron OK | 2-3 wk | **negotiable (cheap migrate)** |

**Translation**: 6 จาก 10 collectors **ควรเก็บ Beam ไว้** หรือเสี่ยงเสีย correctness. 3 collectors negotiable. 1 already Cloud Run

## Detailed per-collector

### 1. members-collector (loyalty) — DO NOT MIGRATE

**ปัจจุบัน:**
- Kafka streaming, 3 schemas (A/B/C) ที่ต้อง unwrap differently
- CDC writes ไปทั้ง Iceberg refined + BQ refined (UPSERT)
- **CDC DELETE with 3-layer safety** (saved in MEMORY.md):
  - Layer 1: tier_code from Kafka message
  - Layer 2: API check — ถ้า tier ไม่อยู่ใน API response แล้ว → candidate for delete
  - Layer 3: BQ confirm — query BQ ถ้า tier เคยมี → ออก DELETE row mutation
- Tier maintenance dedup (`beam.Distinct()` GroupByKey-based, ข้าม-bundle dedup)
- CDC upsert via primary_key=tierMaintenanceId on BQ table
- 17 new tests, 5 file changes, 2-3 weeks careful design

**Cloud Run version ต้องการ:**
- WAL/journal สำหรับ atomic Kafka offset + BQ write + Iceberg write — 3-4 weeks
- External dedup state (BT) สำหรับ tier_maintenance — 1 week
- DELETE coordination logic ใน distributed setting — 4-6 weeks (critical correctness)
- Schema B/C unwrap — 1 week (port code)
- Tests + integration — 2-3 weeks

**Effort estimate**: 12-16 weeks senior data engineer

**Risk**: bug ใน 3-layer DELETE = wrong tier counts ใน BI = customer-facing impact (e.g., wrong "Gold member" count, wrong loyalty tier benefits)

**Decision**: **DO NOT MIGRATE.** Critical correctness + already deployed + working

### 2. customer-profile-pipeline V3 (insight) — DO NOT MIGRATE

**ปัจจุบัน (V3, Hexagonal architecture):**
- Pub/Sub → Bigtable enrichment (5 column families) → BQ CDC + S3 Parquet + Iceberg merge + DLQ
- **FixedWindows(5 min)** for S3 export with Bangkok TZ partition paths
- **Periodic MERGE every 300s** ms_personas → ms_personas_iceberg
- **PeriodicImpulse** for windowed periodic tasks
- **Consent SQL chain** (4 SQL submits + export to GCS + S3 copy hourly)
- RateLimitedLogger to prevent log quota exhaustion (real production fix from 140K throttle/24s)

**Cloud Run version ต้องการ:**
- 5-min windowed buffer + flush — 2-3 weeks (state management)
- Parquet write per window with partition paths — 1-2 weeks
- Iceberg merge (single committer) — 3-4 weeks
- Consent SQL chain via Cloud Scheduler + state — 2-3 weeks
- BQ CDC write logic — 2-3 weeks
- Rate-limited logging port — 0.5 week
- DLQ + retry pattern — 1 week
- Reconciliation jobs — 2 weeks
- Integration tests — 3-4 weeks

**Effort estimate**: 14-18 weeks senior data engineer

**Risk**: complexity ของ V3 มาจาก 5+ Sessions of debugging in production. Re-implement = re-learn all those bugs.

**Decision**: **DO NOT MIGRATE.** ที่ทีม insight pattern ปัจจุบันใช้ V3 (Beam) สำหรับ flow นี้อยู่แล้ว + critical complexity

### 3. tiers-collector + members-tiers-history-collector (loyalty) — KEEP BEAM

**ปัจจุบัน:**
- Beam batch (Cloud Scheduler 1AM BKK) → API call → Iceberg + BQ CDC
- ใช้ pattern เดียวกันกับ members-collector ใน reuse code

**Cloud Run version ทำได้:**
- Cloud Scheduler → Cloud Run cron job → API → BQ writes
- ไม่ต้อง streaming primitives
- Iceberg single-committer pattern OK ที่ batch scale

**แต่:**
- ทีม data ปัจจุบันมี proven pattern (Beam) สำหรับ tiers + history
- Reuse code กับ members-collector (shared domain models, BlmsCatalogConfig, ManagedIcebergWriteConfig)
- ถ้า migrate Beam→Cloud Run = forfeit code reuse + retraining + 6-8 weeks effort

**Effort estimate**: 6-8 weeks each

**Decision**: **KEEP BEAM.** ไม่มี gain จาก migration; ใช้ pattern เดียวกับ members-collector

### 4. purchases-collector (loyalty) — KEEP BEAM

**ปัจจุบัน:** reference/read-only สำหรับทีม data (owned by another team), Beam streaming pattern

**Decision**: **KEEP BEAM.** ไม่ใช่ของทีมเรา — coordinate with other team. Pattern พิสูจน์แล้ว

### 5. customer-profile-collector V4 (insight) — NEGOTIABLE

**ปัจจุบัน:**
- Beam streaming (V4 refactor with DI pattern)
- 128 MS member fields mapping
- Bigtable read + BQ CDC writes

**Cloud Run version ทำได้:**
- คล้าย V3 แต่ขนาดเล็กกว่า (no S3, no Consent SQL chain, no Iceberg merge)
- ถ้า skip CDC ที่แท้จริง — ใช้ append + view trick — easier (8 wk)
- ถ้า maintain CDC correctness — harder (10 wk)

**Decision**: **Negotiate.** ถ้า lose CDC correctness ก็ migrate ได้, แต่ scope ต้อง clear

### 6. last-purchases-collector (insight) — NEGOTIABLE

**ปัจจุบัน:** Beam streaming, Pub/Sub→BQ CDC (simpler than members-collector)

**Cloud Run version:**
- Pub/Sub → Cloud Run subscriber → Storage Write API CDC mode (with primary_key handling)
- Effort: 4-6 weeks

**Decision**: **Negotiate.** Simple CDC ที่อาจ migrate ได้ แต่ test thoroughly

### 7. customer-svoc-collector (insight) — NO CHANGE

**ปัจจุบัน:** Cloud Run + FastAPI (on-demand BQ EXPORT + Parquet merge)

**Decision**: **เก็บเดิม.** ทำงานดี

### 8. customer-svoc-interim (insight) — CAN MIGRATE

**ปัจจุบัน:** Beam batch (BQ SQL → GCS Parquet)

**Cloud Run version:**
- Cloud Run cron + BQ EXPORT DATA → GCS
- ไม่ต้องการ Beam primitives
- Effort: 2-3 weeks

**Decision**: **Cheap migrate, OK to do.** ไม่ใช่ data pipeline ในแง่ streaming

## Strategic decisions

### "All or nothing" trap
ที่ CTO เสนอ "migrate all" — risk คือ:
- Pilot collectors ง่าย (svoc-interim, last-purchases) ก่อน
- "เห็นไหม ทำได้!" → กดดัน collectors ยาก (members-collector, customer-profile-pipeline V3)
- ใช้เวลา 2-3 ปี, มี bugs in production

### Counter-proposal: Tiered migration
แบ่งเป็น 3 tiers based on complexity + criticality:

**Tier A — Keep Beam (6 collectors):**
- members-collector (CDC DELETE, critical correctness)
- customer-profile-pipeline V3 (windowed + Iceberg merge + consent SQL)
- tiers-collector + members-tiers-history-collector (batch with Iceberg, code reuse)
- purchases-collector (other team's, working)
- coupons-collector (planned, start with Beam for consistency)

**Tier B — Negotiable (2 collectors):**
- customer-profile-collector V4 (decide based on CDC correctness requirement)
- last-purchases-collector (simple CDC, possible migrate)

**Tier C — Cheap migrate or already Cloud Run (2 collectors):**
- customer-svoc-interim (batch, easy migrate)
- customer-svoc-collector (already Cloud Run)

### Migration as "POC + measure" not "big bang"

ถ้า CTO ยืนยันต้อง migrate บาง collector — เสนอ:
1. Pick **ONE collector** ใน Tier B หรือ C (last-purchases-collector recommended — simple CDC)
2. POC for 3 months
3. Measure: cost, incidents, latency, dev velocity
4. **Reassess based on data** — ไม่ใช่ extrapolate มาตัดสินทั้งหมด

ถ้า POC พบ:
- ✓ Cost ลดจริง > 30%
- ✓ Incidents ไม่เพิ่ม
- ✓ Dev velocity OK
→ Consider migrate Tier B

ถ้า POC พบ:
- ✗ Cost ใกล้เคียง หรือเพิ่ม
- ✗ Incidents เพิ่ม
- ✗ Dev velocity ลด
→ **Stop migration, keep Beam for Tier A+B**

## Cost of "all-collector migration" + losing Beam infra

| Item | Cost |
|---|---|
| Engineering effort 8-12 weeks × 8 collectors × $5K/wk | **$320K-$480K** |
| Custom CDC library (1-time) | **$80K-$120K** |
| Custom Iceberg writer (1-time) | **$60K-$80K** |
| Reconciliation pipelines (per collector) | **$80K** |
| Testing + parallel run | **$60K** |
| Migration risk buffer (data loss/duplicate fix) | **$40K** |
| **Total migration cost** | **$640K-$860K** |
| Plus: forfeit existing Beam infra investment | **~$200K of past work** |
| Plus: ongoing higher cloud costs (per [04](04_cost_arithmetic.md)) | **$60-80K/yr × 3yr = $180-240K** |

**Total cost of "migrate everything": ~$1M-$1.3M over 3 years**

vs **Cost of "keep Beam pattern": ~$200K over 3 years**

**Net waste of migration: ~$800K-$1.1M over 3 years**

That's the number to put in front of CTO
