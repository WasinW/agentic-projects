# 01 — CTO's Proposal & Scope

## What's actually being proposed

CTO ของ insight-api owner team เสนอ **migrate ทุก collector ในโปรเจ็ค data** จาก current Beam/Dataflow pattern → Cloud Run pattern

### Pattern เปลี่ยน

**Current (data team's pattern, ใช้กับทุก collector):**
```
Kafka (source — cost ของ source อื่นไม่อยู่ใน scope)
  ↓
Dataflow Flex Template (per collector)
  ↓ Beam pipeline:
  ↓   - source connectors
  ↓   - DoFns (transform, dedup, join, enrichment)
  ↓   - sink: BQ Storage Write API CDC mode + IcebergIO via BLMS REST
  ↓
BQ refined table (per table) + Iceberg source table
```

**Proposed (CTO's pattern, ใช้กับทุก collector):**
```
Pub/Sub subscription (replace Kafka in some flows)
  ↓
Cloud Run service (per collector or shared)
  ↓ business logic:
  ↓   - validate / transform
  ↓   - identity resolution (BT)
  ↓   - persona enrichment
  ↓
BQ via หลายทาง:
  - BQ client library (legacy `tabledata.insertAll` / `dataset(...).table(...).insert([row])`)
  - Storage Write API (manual, default stream or pending stream)
  - Pub/Sub topic → BQ direct subscription (push to BQ)
  - Materialized view ครอบ append table (เพื่อ derive "current state")
```

### CTO's stated reasons

1. **"ถูกกว่า"** — direct cloud cost (Cloud Run + Pub/Sub + BQ Storage Write) คำนวณตาม `size × event_count` ดู cheaper
2. **"ง่ายกว่า"** — code = HTTP service, ทุก dev เขียนได้, ไม่ต้องเรียน Beam SDK
3. **"Flexible — custom ได้ทุกอย่าง"** — CDC, materialized view, Pub/Sub direct, batch via Cloud Scheduler — ทำได้ทั้งหมด
4. **"Already proven"** — insight-api ทำงานอยู่แล้วด้วย pattern นี้ (collector + persona-collector + ClickHouse pipeline)
5. **"Less infrastructure"** — ไม่ต้องการ Composer, Dataflow workers always-on, GAR repos สำหรับ Flex Templates

### Hidden assumptions ที่ CTO อาจไม่ได้ articulate

- Cloud Run pattern current ของ insight-api **ถือว่า work ดีพอแล้ว** → คนอื่นควรใช้ pattern เดียวกัน
- Cost calculation เป็น **per-component math** — Cloud Run vs Dataflow worker, Pub/Sub vs Kafka — แล้ว aggregate ตรง ๆ
- "Custom ทำได้" = ไม่นับ engineering effort เป็น cost
- Operational tax (8 services + 8 topics ของ insight ปัจจุบัน) ไม่ถูก count

## Scope = ทุก collector

ที่จะเปลี่ยนจริง ๆ (จาก code ที่อ่าน):

### Loyalty (loyalty/loyalty-data/) — Beam ทั้งหมด, ตอนนี้ deployed

| Collector | Current | Migration target ตามที่ proposed |
|---|---|---|
| **purchases-collector** | Beam streaming, Kafka → Iceberg + BQ CDC | Cloud Run + Pub/Sub→BQ direct? |
| **members-collector** | Beam streaming, Kafka (Schema A/B/C) → Iceberg + BQ CDC + DELETE support (3-layer safety) | Cloud Run — แต่ CDC DELETE ต้อง custom |
| **tiers-collector** | Beam batch, Cloud Scheduler 1AM → Iceberg + BQ CDC | Cloud Run cron + BQ writes |
| **members-tiers-history-collector** | Beam batch → Iceberg + BQ CDC | Cloud Run cron + BQ writes |
| **coupons-collector** | (planned) | Cloud Run + Pub/Sub→BQ |

### Insight (insight-api/data/) — Mixed, partly Beam already

| Collector | Current | Migration target |
|---|---|---|
| **customer-profile-collector** (V4) | Beam streaming | Cloud Run + Pub/Sub→BT→BQ |
| **customer-profile-pipeline** (V3) | Beam streaming, Pub/Sub→BT→BQ CDC + S3 Parquet windowed + Iceberg merge + Consent SQL | Cloud Run — แต่ windowing/merge/SQL chain ต้อง re-architect |
| **last-purchases-collector** | Beam streaming, Pub/Sub→BQ CDC | Cloud Run + Pub/Sub→BQ |
| **customer-svoc-collector** | Cloud Run already (FastAPI cron) | No change |
| **customer-svoc-interim** | Beam batch | Cloud Run cron job |

### Other domains (planned/future)

- messaging-collector — currently Kafka↔Pub/Sub bridge; pipeline TBD
- partner-data — TBD
- gamification-data — TBD
- catalog-products-collector — TBD (terraform setup KB exists)
- foundry-svoc-collector — TBD
- common/common-data/ — shared lib

## What's at stake

### Existing investment to forfeit

ถ้า migrate ทั้งหมดไป Cloud Run, **ทีมเรา throw away**:

1. **Beam Hexagonal Architecture refactor** — domain models (BlmsCatalogConfig + ManagedIcebergWriteConfig), iceberg_writer/iceberg_sink with frozen dataclasses (loyalty 3 collectors, ~498 tests pass)
2. **BLMS REST + IcebergIO + managed.Write** patterns — proven, traced from YAML→Settings→ConfigAdapter→IcebergSink (verified 2026-02-17)
3. **CDC DELETE 3-layer safety** (Schema B/C unwrap + tier_code Kafka→API→BQ check) — irreplaceable in Cloud Run without major eng effort
4. **Schema migration tooling** — register_table preserving field IDs + partition spec, deploy.py BQ table mgmt with backup/restore/schema compare
5. **GitLab CI patterns** — create-image with stg+prod multi-destinations, terraform:apply per env, deploy-tables, deploy:prod scripts (prepare_dataflow_config/spec, deploy_dataflow)
6. **Per-collector infrastructure** — buckets, GAR repos, biglake-metastore IAM (source + refined dataset access), container_spec.json templates
7. **Knowledge base + documentation** — `loyalty/docs/` + `loyalty_knowledge_base.md` + 10+ reference docs
8. **Team expertise** — Beam internals, Iceberg semantics, Dataflow tuning — months of accumulated learning

### What "successful migration" requires

| Phase | Scope | Estimated time |
|---|---|---|
| 1. Re-architect each collector | 8-12 collectors | 6-12 weeks/collector |
| 2. Build custom CDC (with DELETE) for Cloud Run | 1-time platform work | 3-6 months |
| 3. Build custom Iceberg writer for Cloud Run | 1-time platform work | 2-4 months |
| 4. Build state management (BT/Redis) per pipeline | per-collector | 1-2 weeks each |
| 5. Build reconciliation jobs | per-collector | 1 week each |
| 6. Migrate prod data + validate | per-collector | 2-4 weeks each |
| 7. Decommission Dataflow infra | end of migration | 1 week |
| **Total (8 collectors)** | | **~18-24 months × 1 senior engineer** |

vs continuing Beam pattern: **~2-3 weeks per new collector** (proven from purchases→members→tiers pattern)

## Scope creep risk

CTO's proposal frame คือ "all collectors" — แต่:
- **บาง collector simple** → migrate ง่าย (e.g., last-purchases-collector ที่เป็น Pub/Sub→BQ CDC)
- **บาง collector ซับซ้อน** → migrate ยากมาก (e.g., members-collector CDC DELETE, customer-profile-pipeline V3 windowed S3+Iceberg merge)

**Risk**: ถ้า accept proposal ทั้งหมด → ทีมจะ migrate "ตัวง่าย" ก่อน, แล้วอ้างว่า "เห็นไหม มันทำได้" → กดดัน migrate "ตัวยาก" → ตัวยากใช้เวลา 6-12 เดือน → 2-3 ปีไม่จบ → ทีม data ไม่มีเวลาทำ feature ใหม่

## Questions ที่ต้องเอาไปถาม CTO

1. **Phasing**: migrate ทั้งหมดในคราวเดียว หรือ pilot 1-2 collectors ก่อน?
2. **Capability parity**: CDC DELETE + Iceberg + windowing — Cloud Run version ทำได้ไหม? ใครจะ implement? Estimate?
3. **Cost calculation**: ตัวเลข cost สมมุติฐานคืออะไร? (event volume, hop count, state store IOPS, engineering effort)
4. **Sunk cost handling**: existing Beam infra ที่เรามี — เก็บไว้ใช้ต่อ? หรือ retire ทันที?
5. **Team skills**: data engineer ของเราคุ้น Beam — retraining cost? Hire app engineers? ทีมไหน own?
6. **Operational ownership**: ใคร on-call สำหรับ Cloud Run pipeline 8-12 services × N collectors?
7. **Migration risk**: data loss/duplicate ระหว่าง migrate — มี mitigation plan?
