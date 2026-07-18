# NTT / The-1 — KB Gap Analysis (2026-06-28)

> สำรวจ docs งานจริงใน `realproject/` ทุกโดเมน เทียบกับ KB ที่มี → ชี้ช่องที่ขาด/ผิด/ควรเพิ่ม
> วิธี: fan-out 7 agents (data-architect / de-engineer ×4 / devops / de-engineer-small) อ่านแบบ read-only
> สถานะ: **gap analysis เท่านั้น — ยังไม่เขียน/แก้ KB**

---

## TIER 0 — ของในคลังที่ "ผิด/ล้าสมัย" (แก้ก่อน เพราะ agent จะอ้างผิด)

| # | โดเมน | ปัญหา | ไฟล์ที่ต้องแก้ |
|---|---|---|---|
| 0.1 | sale | `domains/sales-data/` บอก "BQ writes commented out / per-topic Flatten" แต่จริงๆ BQ writes = active CDC UPSERT, รวม topic เดียว. Beam 2.70→2.71, column ชื่อเก่า (receipt_no…), trigger 300 vs 60s | `domains/sales-data/DATA_PIPELINE.md`, README — ใช้ `_mem_clean/sales/` เป็น source of truth |
| 0.2 | loyalty-mart | KB บอก "scaffold done, views TBD / definitions empty" แต่จริงๆ มาร์ท `point_earned` + `point_redemption` สร้างเสร็จแล้ว + มี init backfill | `domains/_mem_clean/loyalty-mart/knowledge_base.md` (§1 status, scope earn→earn+redeem) |
| 0.3 | shared | CLAUDE.md + `00_overview/platform_blueprint.md` เขียนว่า framework = "YAML + 25-step registry" — **ผิดรุ่น**. จริงๆ คือ ports-and-adapters + builder-dict registries | `CLAUDE.md`, `platform_blueprint.md` (บรรทัด 250/411/437/631) |
| 0.4 | insight | version drift (KB ว่า V3.2.0 vs source 3.0.0); S3 sink เขียนว่า "realtime" แต่จริงเป็น GCS buffer + hourly compact; events_consents note stale | `domains/insight/README.md`, `_mem_clean/insight/knowledge_base.md` |

## TIER 1 — โครงสร้างหายทั้งหมวด / โดเมนหายทั้งโดเมน

| # | สิ่งที่ขาด | ไป KB ไหน | source |
|---|---|---|---|
| 1.1 | **`02_ingestion/` หายทั้งหมวด** (Kafka collector, API batch, PostgreSQL CDC, init/backfill, schema A/B/C) | new `02_ingestion/` | `the1-re-data-platform/doc/02_ingestion/{INSTRUCTIONS,REFERENCE}.md` |
| 1.2 | **`05_serving/` หายทั้งหมวด** (Dataform views, public/consumer layer, BI) | new `05_serving/` | `the1-re-data-platform/doc/05_serving/{INSTRUCTIONS,REFERENCE}.md` |
| 1.3 | **foundry / svoc-transferor = โดเมนงานจริงทั้งโดเมน ไม่มีใน KB เลย** (Customer-360 SVOC + product-merchant mart) | new `domains/_mem_clean/foundry/knowledge_base.md` + CONTEXT_MAP | `realproject/foundry/foundry/infrastructure/svoc-transferor/` |
| 1.4 | **central IaC repo `the1-terraform-gcp`** เห็นแค่ฝั่ง consumer — module library (~32), org policy, hub-spoke network, **VPC-SC perimeter** ไม่มี | `data_platform_ref/architecture/` + `10_security/` | `terraform/the1-terraform-gcp/{organization,landingzone,modules,projects/monorepo}` |

## TIER 2 — Artifact reusable ข้ามโดเมน (มูลค่าสูง เอาไปใช้ซ้ำได้)

| # | สิ่งที่ขาด | ไป KB ไหน | source |
|---|---|---|---|
| 2.1 | **งานวิจัย lookup 75M แถว / 5 ตาราง** เทียบ 18 วิธี (SQLite/Arrow/DuckDB/mmap/Memorystore…) + cost + decision flow. KB ไม่มี lookup >500MB เลย | `components/dataflow/LARGE_LOOKUP_ENRICHMENT_75M.md` | `sale/doc/STREAMING_ENRICHMENT_DEEP_DIVE.md` + `STREAMING_BATCH_JOIN_RESEARCH.md` |
| 2.2 | **schema-strategy pattern** (`IcebergSchemaStrategy`/`RawJsonSchemaStrategy`) — สิ่งที่ DE เขียนบ่อยสุดต่อ service | `common_repo/04` | `common/common-data/common-python-cloudrun/README.md` + `…/iceberg_schema_strategy.py` |
| 2.3 | **Beam test harness** (testcontainers emulator: bq 9050 / bigtable 8086 / gcs 4443) — ของที่ copy ใช้บ่อยสุด แต่ไม่มี doc | `common_repo/03` | `common-python-dataflow/src/common/beam/testing/` |
| 2.4 | **BigQuery DTS S3→BQ pattern** (runtime partition `{run_time\|"%Y%m"}`, monthly schedule, Redshift-DTS-disabled-private-IP) — ใช้ทั้ง foundry + catalog | `shared/common_patterns.md` | `foundry/.../svoc-transferor/dts.tf` |
| 2.5 | **ports/data-model contracts** (SourcePort/SinkPort/TransformPort signatures + DataContainer/Records) — คือ extension interface จริง (แก้ความเข้าใจ 0.3) | `common_repo/07-cloudrun-ports.md` | `common-python-cloudrun/src/common_cloudrun/{ports,data_types}.py` |
| 2.6 | **Iceberg/BigLake best-practices** distilled (hidden partitioning, 100MB–1GB, schema/partition/sort evolution) | `03_storage/` | `the1-re-data-platform/agent/data-platform/iceberg-bigLake-practices.md` |
| 2.7 | **Dataplex declarative DQ framework** (completeness/uniqueness/validity/freshness + YAML) | `06_governance/` | `agent/data-platform/data-governance-framework.md` |

## TIER 3 — Incident / postmortem layer (บทเรียน production จริง)

| # | สิ่งที่ขาด | source |
|---|---|---|
| 3.1 | **SDK harness crash → ข้อมูลหาย 7 วันบน PROD** (GIL + blocking S3 sink + GroupByKey buffer → gRPC timeout; fix = GCS buffer + hourly compact) | `insight/doc/issue/SDK_HARNESS_CRASH_S3_WRITE.md` |
| 3.2 | **S3 export watermark lag** (PeriodicImpulse ค้างเพราะ blocking 3GB copy; fix 300→3600s) | `insight/doc/s3_export_lag_analysis.md` |
| 3.3 | **events_consents table-type recovery** (external_iceberg ≠ Storage Write API; type flips ทำ data orphan บน PROD) | `insight/HOTFIX_EVENTS_CONSENTS_20260128.md` |
| 3.4 | **mart dedup/inflation findings** (F1 init-override bug, F4 +51% earn inflation, UNNEST explosion) | `loyalty-mart/doc/profile_scripts/MART_DUP_FINDINGS.md` |
| 3.5 | **hexagonal trade-offs + Wasin's reservation** (CLAUDE.md สั่งให้ document — ตอนนี้ KB เขียน hexagonal เป็น fact แต่ไม่มีข้อเสีย/DI-ทำครึ่งๆ) | `insight/ARCHITECTURE.md §1.2-3.2` + `discussions/2026-04-05_insight-collector-refactor-audit.md:314-368` |

## TIER 4 — เพิ่มความลึก / ของเฉพาะโดเมน (ทำทีหลังได้)

- loyalty: AWS→GCP column mapping (earn 67-col / redeem 117-col), points business rules (topic_source/reason_code/AYCAB), tier_maintenance "filter-not-CDC" dedup, DLQ pattern detail, backfill idempotency pattern
- sale: ops runbook, CDC-PK/column-rename migration risk playbook, Phase-2 deferred member/product resolution
- shared: cloudrun adapters ใหม่ (SFTP + GCS file sink), ApiEnrichmentTransform merge strategies, streaming tune knobs (retry/flush/poll)
- terraform: module catalog, network topology, log-sink, state backend split, dataform impersonation
- for_me_only: promote AWS 7-part + Azure deep-dive เข้า `knowledge_base_legacy/` (depth หาย ~2.6k บรรทัดตอน synthesis)

---

## หมายเหตุสำคัญ
- **อย่า ingest:** `doc/archive/`, `doc/data_platform/`, `agent/bak_mem/`, `loyalty/backup/`, `*_bk/`, `sales-data_bk2/` — เป็น duplicate เก่าที่ KB ดูดไปแล้ว/ตั้งใจ superseded
- message / gamification / partner / catalog — KB `_mem_clean/` ครบและ current แล้ว (source README เป็น boilerplate) → **ไม่มี gap**
- **SCB:** ไม่มี docs ให้กลั่นเลย — ต้องสัมภาษณ์ Wasin แยก (ไม่ใช่รอบนี้)
