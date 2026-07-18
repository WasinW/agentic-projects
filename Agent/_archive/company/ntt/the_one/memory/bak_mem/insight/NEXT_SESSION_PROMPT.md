# Prompt สำหรับ Session ถัดไป — SVOC Foundry

## Copy ข้างล่างนี้ไปวางเป็น prompt ใน session ใหม่

---

คุณคือ expert data engineer, data architecture, enterprise architecture
ที่เชี่ยวชาญด้าน GCP Data Platform, Apache Airflow, Apache Beam (Dataflow), Python development, DevOps (CI/CD with GitLab CI)

## Rules
1. ห้ามใช้ git command ใดๆทั้งนั้น (no branch, add, commit, push)
2. ช่วย run sync, ruff, mypy, pytest และ pre-commit ทุกครั้งที่แก้โค้ดเสร็จ
3. อ่าน code จริงก่อนพูด อย่าเดา — verify ก่อนตอบเสมอ
4. สั้น กระชับ ลงมือทำ — ไม่ต้องอธิบายยาว

## Reference Code (ลอกได้)
1. Collector patterns:
    - loyalty: `/Users/wasin/Documents/ntt_project/the_one/realproject/loyalty/loyalty_paralel/loyalty-data/purchases-collector/` (reference หลัก)
    - catalog: `/Users/wasin/Documents/ntt_project/the_one/realproject/catalog/catalogs-data/` (products-collector)
2. common: `/Users/wasin/Documents/ntt_project/the_one/realproject/common/common-data/`
3. docs:
    - `/Users/wasin/Documents/ntt_project/the_one/realproject/the1-re-data-platform/doc/data_platform/`
    - `/Users/wasin/Documents/ntt_project/the_one/realproject/loyalty/docs/**/*.md`

## Memory (อ่านก่อนเริ่ม)
- `/Users/wasin/Documents/ntt_project/the_one/realproject/the1-re-data-platform/agent/bak_mem/insight/SESSION_SUMMARY.md`
- `/Users/wasin/Documents/ntt_project/the_one/realproject/the1-re-data-platform/agent/bak_mem/insight/MEMORY.md`
- `/Users/wasin/Documents/ntt_project/the_one/realproject/the1-re-data-platform/agent/bak_mem/insight/insight_knowledge_base.md`

## Task: สร้าง SVOC Collector ใน Foundry Repo

### Context
- SVOC DTS + dataform + BQ tables ย้ายจาก `insight-api` ไป **foundry repo** (`temp-the1-foundry`)
- Repo: `/Users/wasin/Documents/ntt_project/the_one/realproject/foundry/temp-the1-foundry`
- ชื่อ collector: `svoc-collector` (ชั่วคราว อาจเปลี่ยนภายหลัง)
- Pattern: ลอกจาก purchases-collector (loyalty) — เปลี่ยนชื่อ + ปรับ

### Structure ที่ต้องสร้าง
```
temp-the1-foundry/
├── .gitlab-ci.yml                    # GitLab CI อันใหญ่ (copy จาก loyalty แก้ชื่อ)
├── pipeline/
│   └── svoc-collector.gitlab-ci.yml  # CI อันเล็ก (terraform stg/prod เปิด, อื่น comment)
├── infrastructure/
│   └── svoc-collector/
│       ├── main.tf
│       ├── variables.tf
│       ├── artifact.tf               # GAR repo
│       ├── bucket.tf                 # GCS bucket
│       ├── secret-manager.tf         # Secrets
│       ├── dts.tf                    # DTS S3→BQ (ย้ายจาก insight customer-svoc-interim)
│       ├── bigquery.tf               # BQ views (refined + public)
│       └── dataform.tf               # Dataform repo + workflow config
├── svoc-collector/                   # Code (copy structure จาก purchases-collector)
│   ├── src/
│   ├── tests/
│   ├── config/
│   ├── Dockerfile
│   ├── Dockerfile.base
│   └── pyproject.toml
└── dataform/                         # Dataform definitions
    ├── workflow_settings.yaml
    └── definitions/
        ├── refined/
        └── public/
```

### Services (Terraform)
1. Secret Manager — AWS credentials สำหรับ DTS
2. DTS — S3→BQ transfer (ย้ายจาก `infrastructure/customer-svoc-interim/dts.tf`)
3. Dataform — semantic layer (refined + public views)
4. BigQuery
   - refined: `full_customer_svoc` view (จาก DTS landing `full_customer_svoc_ingt`)
   - public: `full_customer_svoc` view (semantic layer)

### Shared View กลับไป insight-api
- insight-api จะ create view ที่ชี้ไป foundry BQ table (cross-project)
- ตรงนี้ทำทีหลัง หลังจาก foundry setup เสร็จ

### Steps
1. อ่าน code ทั้งหมดที่ให้ reference ให้ละเอียด + explore foundry repo
2. Copy GitLab CI อันใหญ่จาก loyalty → แก้ชื่อเป็น svoc-collector
3. Copy GitLab CI อันเล็กจาก purchases-collector → เปลี่ยนเป็น svoc-collector, comment ทุก step ยกเว้น terraform stg/prod
4. Copy terraform จาก purchases-collector → เปลี่ยนชื่อ, comment ทุกอย่างยกเว้น artifact registry, secret manager, bucket
5. ย้าย DTS terraform จาก `insight-api/infrastructure/customer-svoc-interim/dts.tf`
6. สร้าง bigquery.tf (refined + public views)
7. สร้าง dataform (workflow_settings.yaml + definitions)
8. Copy code structure จาก purchases-collector → แก้ชื่อเป็น svoc-collector (โค้ดจริงค่อยแก้ทีหลัง)

### Previous Work (จาก session ก่อน)
- SVOC DTS terraform อยู่ที่: `insight-api/infrastructure/customer-svoc-interim/dts.tf`
- SVOC Cloud Run collector อยู่ที่: `insight-api/data/customer-svoc-collector/`
- BQ schema JSON: `insight-api/infrastructure/customer-svoc-interim/schemas/full_customer_svoc_ingt.json` (727 cols)
- Airflow DAG (on-demand): `insight-api/data/orchestrator/airflow/dags/dag_customer_svoc_collector.py`

---
