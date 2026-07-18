# Loyalty Session Export Summary
**Exported: 2026-04-05**
**Session scope**: loyalty domain — members-collector, tiers-collector, members-tiers-history-collector, coupons-collector, backward-compatible-collector

---

## Session Owner & Role
- **User**: Wasin — Data Engineer / Tech Lead ดูแล loyalty data platform
- **Working style**: สั้น กระชับ ลงมือทำ, verify ก่อนตอบ, ห้ามเดา
- **Language**: Thai + English mixed (technical terms in English)

## Project Overview
- **GCP Project**: `the1-loyalty-data` (stg/prod)
- **Repo**: GitLab monorepo — loyalty domain อยู่ใน `loyalty/loyalty_paralel/`
- **Stack**: Python 3.12, Apache Beam, Dataflow, Iceberg (BLMS REST), BigQuery, Kafka, UV

## Architecture
```
STREAMING: Kafka → members-collector (job_type=normal) → Iceberg → BQ
BATCH:     Cloud Scheduler (1AM BKK) → tiers-collector → API → Iceberg → BQ
           Cloud Scheduler (1AM BKK) → members-tiers-history → PostgreSQL → Iceberg → BQ
INIT:      GitLab CI (TRIGGER_INIT_DATA_LOAD=1) → job_type=initial_data → Iceberg → BQ
NEW:       backward-compatible-collector → BQ → Parquet → GCS → S3 (config-driven batch export)
```

## Collectors Managed (5)
| Collector | Mode | Source | Sink | Status |
|-----------|------|--------|------|--------|
| members-collector | Streaming | Kafka | Iceberg + BQ | STG deployed, waiting for messages |
| tiers-collector | Batch | REST API | Iceberg + BQ | Active |
| members-tiers-history | Batch | PostgreSQL | Iceberg + BQ | Active |
| coupons-collector | Streaming | Kafka | Iceberg + BQ | Schema changes in progress |
| backward-compatible | Batch | BigQuery | S3 (via GCS) | Scaffolded, needs STG test |

## Key Technical Decisions Made
1. **Iceberg via BLMS REST Catalog** (not Hadoop) — identical to messaging-collector
2. **CDC DELETE for member_tier** — 3-layer safety (tierCode, API check, BQ confirm)
3. **Schema A/B/C handling** — members-collector handles 3 Kafka message formats
4. **etlLoadTime → ingestedTHDate** — members-collector source/refined rename
5. **deploy.py cleanup** — removed Iceberg code (managed.Write auto-creates)
6. **Option B write ACTIVE, BQ table creation DISABLED** — waiting for terraform dataset
7. **Bangkok timezone +7** — all refined timestamps use BKK time
8. **Common migration** — KafkaReaderAdapter from common-data-python-dataflow (DI pattern)
9. **Source Iceberg 3-column schema** — data (str), ingested_date (int), ingested_at (int)

## Completed Work (Major Items)
- D-H IcebergIO Refactor (BlmsCatalogConfig + ManagedIcebergWriteConfig)
- Option B Migration code (partially cleaned)
- GitLab CI prod jobs (all 3 collectors)
- Schema B/C nested payload fix
- CDC DELETE for member_tier
- Tier maintenance dedup + CDC upsert
- etlLoadTime → ingestedTHDate rename
- Kafka config + Secret structure migration
- deploy.py cleanup (2290→370 lines)
- Sonar scan fixes (members 24 issues, m-t-h 7 issues)
- Coupons REPEATED RECORD schema
- Backward-compatible-collector full scaffold
- partition_fields alignment
- Common library migration (KafkaReaderAdapter)
- BLMS schema evolution (4 tables to 3-column)
- Dataform views (coupons)

## Pending Work
- Members-collector STG verification (waiting for Kafka messages)
- Coupons event_name conflict (Kafka vs API race)
- Coupons CVE (pyasn1, libc6)
- Coupons ingested_at: str→int alignment
- M-T-H rerun safety (DELETE WHERE + INSERT)
- 3 collectors partition/datetime changes (plan exists)
- Tiers-collector sonar scan
- Backward-compatible-collector STG testing
- Secret key migration (tiers, m-t-h) — if DevOps changes
- Kafka schema: eligibleTierCode migration
- Init data migration (DTS S3→BQ blocked on AWS perm)

## Memory Files Exported (14 files)
| File | Description |
|------|-------------|
| MEMORY.md | Main index (338 lines) |
| loyalty_knowledge_base.md | Complete KB — all collectors, infra, schemas, patterns |
| mistakes_and_rules.md | Critical rules + mistakes log (MUST READ) |
| catalog_products_knowledge_base.md | Catalog/products-collector KB |
| insight_knowledge_base.md | Insight domain KB |
| sales_knowledge_base.md | Sales domain KB |
| sales_pipeline_knowledge_base.md | Sales pipeline specifics |
| sales_schema_migration.md | Schema migration notes |
| sales_schema_migration_done.md | Migration completion summary |
| sales_deploy_fix.md | deploy.py INTERVAL fix |
| sales_initial_data.md | Initial data setup |
| kafka_schema_changes.md | New Kafka schema (eligibleTierCode) |
| feedback_verify_before_answer.md | Verification guidelines |
| dofns_comparison.md | DoFn comparison (members vs messaging) |

## Key Rules for Any Agent Working on Loyalty
1. **No git commands** (no branch, add, commit, push)
2. **Must run after code changes**: uv sync, ruff, mypy, pytest, pre-commit
3. **Correct path**: `loyalty/loyalty_paralel/loyalty-data/` (NOT `loyalty/loyalty-data/`)
4. **purchases-collector** = reference/read-only
5. **member-tiers** = DEPRECATED
6. **transaction/** = NOT ours
7. **pre-commit** modifies transactions-collector → must revert after
8. **Bangkok timezone +7** for ALL refined timestamps
