# 00 — Overview & Consumption Model

> **อ่านไฟล์นี้ก่อนไฟล์อื่นทุกครั้ง** — มันคือแผนที่ของทั้ง repo และอธิบาย "กลไกการ share" ที่เป็นหัวใจของความสับสน

---

## 1. `common-data` คืออะไร

Monorepo เดียวที่เก็บ **ของกลาง** ให้ทุก data project ใช้ร่วมกัน เพื่อไม่ให้แต่ละ repo เขียนซ้ำ
มันไม่ deploy เป็น service — มันคือ **ของให้ดึงไปใช้** (a) ตอน CI compile (b) ตอน job runtime (c) ตอน `uv sync` (d) ตอน `terraform init`

Repo: `git@gitlab.com:The1central/The1/the1-data/common-data.git`
GCP project ของ common-data เอง: `the1-common-data-{stg|prod}`

---

## 2. โครงสร้าง repo ทั้งหมด (ตาม part)

```
common-data/
│
├── common-python-dataflow/         ← PART 3 : Python module สำหรับ Beam/Dataflow collector
│   ├── pyproject.toml               package name: common-data-python-dataflow
│   ├── Dockerfile / Dockerfile.base base image ของ Dataflow flex template
│   ├── dataflow-base-image.gitlab-ci.yml
│   ├── config/base.yaml
│   └── src/common/beam/
│       ├── adapters/input/          kafka_reader/ , bigquery/
│       ├── adapters/output/         bigquery/ , bigtable_writer/ , gcs/(iceberg)
│       └── testing/                 containers.py , fakes.py , fixtures.py
│
├── common-python-cloudrun/         ← PART 4 : Python module สำหรับ Cloud Run collector
│   ├── pyproject.toml               package name: common-data-python-cloudrun
│   └── src/common_cloudrun/
│       ├── adapters/input/kafka/    , adapters/output/{api_source,gcs_iceberg,pubsub,sftp_source}/
│       ├── application/             batch_pipeline.py , streaming_pipeline.py , transforms
│       ├── infrastructure/          builders.py , settings.py , gcp_auth.py , secret_manager.py , gcp_logging.py
│       ├── ports.py , data_types.py
│
├── pipeline/                       ← PART 5 : GitLab CI templates (job logic)
│   ├── common.gitlab-ci.yml          LEGACY  — รวม job เก่าทั้งก้อน (consumer เก่ายัง include อยู่)
│   ├── common-base.gitlab-ci.yml     LEGACY
│   ├── dataflow.gitlab-ci.yml        LEGACY
│   ├── terraform.gitlab-ci.yml       LEGACY
│   ├── v2/                           CURRENT — แยกเป็น layer
│   │   ├── base.gitlab-ci.yml          Layer 1: rules, GCP auth, image build, uv cache
│   │   ├── terraform.gitlab-ci.yml     Layer 2: terraform plan/apply
│   │   ├── scan.gitlab-ci.yml          Layer 2: gitleaks / trivy / sonar / DefectDojo
│   │   ├── bigquery.gitlab-ci.yml      .common-deploy-schemas  ← fetch deploy_schemas.py
│   │   ├── dataflow.gitlab-ci.yml      Layer 3: build / deploy / rollback (Dataflow)
│   │   ├── cloudrun.gitlab-ci.yml      Layer 3: deploy / redeploy / rollback (Cloud Run)
│   │   ├── dataform.gitlab-ci.yml      Layer 4: dataform build/test/deploy/assertion
│   │   └── example-service.gitlab-ci.yml   ตัวอย่างวิธีเขียน .gitlab-ci.yml ของ service
│   └── v3/                           NEXT — รุ่นถัดไป ยังไม่มี consumer ใช้จริง
│
├── templates/                      ← PART 5 : GitLab CI *Components* (หน้าตา interface)
│   ├── service-pipeline/template.yml          component หลัก (dataflow|cloudrun)
│   ├── service-pipeline-dataflow/template.yml sub-component (job เฉพาะ Dataflow)
│   ├── service-pipeline-cloudrun/template.yml sub-component (job เฉพาะ Cloud Run)
│   ├── service-pipeline-dataform/template.yml component สำหรับ Dataform pipeline
│   └── service-pipeline-terraform/template.yml component สำหรับ Terraform-only
│
├── scripts/                        ← PART 6 : Deploy scripts (ถูก fetch ตอน runtime)
│   ├── bigquery/deploy_schemas.py    สร้าง/อัปเดต BQ table จาก JSON schema
│   ├── dataflow/deploy_dataflow.sh   launch Dataflow flex template (update/drain logic)
│   ├── dataflow/prepare_dataflow_config.sh  merge base.yaml + env.yaml → base64
│   ├── dataflow/prepare_dataflow_spec.sh    render container_spec.json + อัป GCS
│   ├── dataform/deploy_dataform.sh   orchestrate Dataform deploy cycle
│   └── dataform/dataform_api.py      Dataform REST API helper (stdlib-only)
│
├── infrastructure/                 ← PART 1 : Terraform
│   ├── common/GCP/                   artifact-registry.tf → สร้าง repo "base-images"
│   │   └── base-image/dataflow-flex/ Dockerfile ของ shared base image
│   └── common-python-dataflow/       artifact-registry สำหรับ dataflow-python312-base
│
├── .gitlab-ci.yml                  CI ของ common-data เอง (build/test/release ของ 2 module)
├── README.md / SETUP.md
```

---

## 3. กลไกการ share 4 แบบ (หัวใจ)

ของใน common-data ไปถึง repo อื่นได้ด้วย **4 ช่องทาง** ที่ไม่เหมือนกันเลย เข้าใจ 4 อันนี้ = เข้าใจทั้ง repo

### กลไก A — GitLab CI `include` / `component`
**ใช้กับ:** Part 5 (CI templates)
ตอน GitLab compile pipeline ของ consumer มันจะดึง YAML จาก common-data มาประกอบ
```yaml
# แบบ component (v2)
include:
  - component: "$CI_SERVER_FQDN/The1central/The1/the1-data/common-data/service-pipeline@main"
    inputs: { svc_name: "members-collector", service_type: "dataflow", ... }
# แบบ project-file (legacy + v2 base)
include:
  - project: "The1central/The1/the1-data/common-data"
    ref: main
    file: "pipeline/v2/base.gitlab-ci.yml"
```
- **Pin ที่:** `@main` / `@0.1.0` (component) หรือ `ref:` (project-file)
- **เกิดผลเมื่อ:** ทุกครั้งที่ pipeline ของ consumer ถูก trigger (ดึง YAML สดตาม ref)
- ถ้า ref = `main` → แก้ common-data แล้วมีผล **รอบ pipeline ถัดไปทันที**

### กลไก B — Runtime fetch (curl / git clone) ตอน job ทำงาน
**ใช้กับ:** Part 6 (scripts) — `deploy_schemas.py`, `deploy_dataflow.sh`, `deploy_dataform.sh`, `dataform_api.py`
job ใน CI template ไม่ได้ "มี" script เอง — มัน **ดาวน์โหลด script สด ๆ จาก common-data ตอน job รัน**
```bash
# ตัวอย่างจริงจาก pipeline/v2/bigquery.gitlab-ci.yml (.common-deploy-schemas)
curl -sf \
  "$CI_SERVER_URL/api/v4/projects/The1central%2FThe1%2Fthe1-data%2Fcommon-data/repository/files/scripts%2Fbigquery%2Fdeploy_schemas.py/raw?ref=${COMMON_DATA_SCHEMAS_REF}" \
  -H "JOB-TOKEN: $CI_JOB_TOKEN" -o /tmp/deploy_schemas.py
python3 /tmp/deploy_schemas.py ...
```
- **Pin ที่:** ตัวแปร env — `COMMON_DATA_SCHEMAS_REF` (deploy_schemas.py), `COMPONENT_VERSION` (dataflow scripts), `COMMON_DATA_REF` (dataform scripts) — **ทุกตัว default = `main`**
- **เกิดผลเมื่อ:** ทุกครั้งที่ job รัน → ดึงเวอร์ชันล่าสุดของ ref เสมอ
- ต้องการ: common-data → Settings → CI/CD → **Job token allowlist** ต้องอนุญาต consumer project

### กลไก C — Python git dependency (uv)
**ใช้กับ:** Part 3 + 4 (`common-python-dataflow`, `common-python-cloudrun`)
collector ใส่ common-data เป็น dependency ใน `pyproject.toml`:
```toml
[project]
dependencies = ["common-data-python-dataflow"]

[tool.uv.sources]
common-data-python-dataflow = {
  git = "ssh://git@gitlab.com/The1central/The1/the1-data/common-data.git",
  subdirectory = "common-python-dataflow",
  tag = "0.0.64"            # ← pin ที่นี่
}
```
- **Pin ที่:** `tag` (หรือ `rev`/`branch`) + ถูก lock ลง `uv.lock`
- **เกิดผลเมื่อ:** consumer แก้ tag เอง แล้วรัน `uv sync` / `uv lock` ใหม่ → **ไม่ใช่ของอัตโนมัติ**
- เป็นกลไกเดียวที่ "ปลอดภัยที่สุด" — แก้ common-data ไม่กระทบใครจนกว่าเขาจะ bump tag

### กลไก D — Terraform git module
**ใช้กับ:** Part 1 (infrastructure)
Terraform อ้าง module ด้วย git URL:
```hcl
module "base_images_repo" {
  source = "git::https://gitlab.com/The1central/platform/the1-terraform-gcp.git//modules/artifact-registry"
  ...
}
```
- **หมายเหตุสำคัญ:** module กลางจริง ๆ อยู่ที่ repo **`the1-terraform-gcp`** ไม่ใช่ `common-data`
  `common-data/infrastructure/` เป็น **ผู้ใช้** module นั้น ไม่ใช่ผู้ให้
- สิ่งที่ common-data "ให้" คนอื่นในเชิง infra จริง ๆ คือ **shared base image** (`the1-common-data-{env}/base-images`) ซึ่งถูก consume ด้วยการอ้าง image URL ไม่ใช่ terraform — ดู [01-tf-infrastructure.md](01-tf-infrastructure.md)

---

## 4. Consumption Matrix — ใครใช้อะไร version ไหน

> verify จาก `.gitlab-ci.yml` + `pyproject.toml` ของ consumer ทุกตัว (2026-05-17)

### 4.1 GitLab CI

| Consumer repo | รุ่น CI | include อะไร | ref |
|---------------|--------|--------------|-----|
| **loyalty-data** | **v2 (component)** | root: `pipeline/v2/base` + `pipeline/v2/terraform`; แต่ละ collector: `service-pipeline@main` + `service-pipeline-dataform@main` | `main` |
| sales-data | legacy | `pipeline/common.gitlab-ci.yml` | (default) |
| catalog-data | legacy | `pipeline/common.gitlab-ci.yml` | (default) |
| gamification-data | legacy | `pipeline/common.gitlab-ci.yml` (root) + collector CI เขียน job เองในเครื่อง | (default) |
| messaging-data | legacy | `pipeline/common.gitlab-ci.yml` (root) + collector CI เขียน job เองในเครื่อง | (default) |
| partner-data | legacy | `pipeline/common.gitlab-ci.yml` | (default) |
| foundry | legacy | `pipeline/common.gitlab-ci.yml` | (default) |

→ **มีแค่ `loyalty-data` ที่ migrate มา v2 component แล้ว** อีก 6 repo ยังเป็น legacy
→ ยังไม่มี repo ไหนใช้ `pipeline/v3/`

### 4.2 Python module (กลไก C)

| Consumer (package ภายใน) | module | tag |
|--------------------------|--------|-----|
| loyalty-data / members-collector | `common-data-python-dataflow` | `0.0.23` |
| catalog-data / products-collector | `common-data-python-dataflow` | `0.0.23` |
| sales-data / sales-collector | `common-data-python-dataflow` | `0.0.32` |
| gamification-data / account-missions-collector | `common-data-python-dataflow` `[iceberg,bigtable,kafka]` | `0.0.64` |
| messaging-data / messages-collector | `common-data-python-dataflow` `[iceberg,bigtable,kafka,pubsub]` | `0.0.64` |
| partner-data / master-collector | `common-data-python-cloudrun` `[iceberg,pubsub,gcs]` | `0.0.42` |

→ tag กระจัดกระจาย (`0.0.23` … `0.0.64`) เพราะแต่ละทีม bump ไม่พร้อมกัน — ดู [03](03-dataflow-module.md)/[04](04-cloudrun-module.md)
→ collector ที่เป็น batch บางตัว (tiers-collector, gamification master-collector) **ไม่ได้** depend module นี้

### 4.3 Scripts (กลไก B)

| Script | legacy repo (6 ตัว) | v2 repo (loyalty-data) |
|--------|--------------------|-----------------------|
| `deploy_schemas.py` | มี **copy ของตัวเอง** ที่ `<repo>/scripts/deploy_schemas.py` | job `.common-deploy-schemas` **fetch จาก common-data** (`ref=COMMON_DATA_SCHEMAS_REF`, default `main`) |
| `deploy_dataflow.sh` | มี copy เอง ที่ `<repo>/scripts/` | fetch จาก common-data (`_fetch_common_scripts`, `ref=COMPONENT_VERSION`) |
| `deploy_dataform.sh` + `dataform_api.py` | มี copy เอง | `git clone` common-data ตอน runtime (`COMMON_DATA_REF`, default `main`) |

→ นี่คือจุดสำคัญที่สุดของเอกสารชุดนี้ — ดูรายละเอียดเต็มที่ [06-scripts.md](06-scripts.md)

### 4.4 Shared base image (Part 1)

| Consumer | อ้าง base image อย่างไร |
|----------|------------------------|
| gamification-data, messaging-data (collector CI) | hardcode `the1-common-data-stg/base-images/dataflow-flex-python312-java17:20260416` |
| loyalty-data (v2) | ผ่าน input `dataflow_base_image_default` ของ component (ค่า default ชี้ image เดียวกัน) |

---

## 5. "ถ้าผมแก้ของใน common-data แล้วใครโดน?" — สรุปสั้น

| แก้อะไร | ใครโดน | โดนเมื่อไหร่ |
|---------|--------|-------------|
| `scripts/bigquery/deploy_schemas.py` | repo ที่ใช้ v2 component (ตอนนี้ = loyalty-data) | pipeline รอบถัดไป (ref=main) — **ทันที** |
| `scripts/dataflow/*.sh` | repo ที่ใช้ v2 component | pipeline รอบถัดไป — ทันที |
| `scripts/dataform/*` | repo ที่ใช้ component `service-pipeline-dataform` หรือ v2 dataform | pipeline รอบถัดไป — ทันที |
| `pipeline/v2/*.yml` | repo ที่ include v2 (loyalty-data + ทุก component) | pipeline รอบถัดไป — ทันที |
| `pipeline/common.gitlab-ci.yml` (legacy) | 6 legacy repo | pipeline รอบถัดไป — ทันที |
| `common-python-dataflow/` หรือ `common-python-cloudrun/` | **ไม่มีใครโดนทันที** — จนกว่า consumer จะ bump `tag` แล้ว `uv sync` | เมื่อ consumer bump เอง |
| `templates/*/template.yml` (component interface) | repo ที่ใช้ component นั้นด้วย `@main` | pipeline รอบถัดไป — ทันที |

> สรุปง่าย ๆ: **ทุกอย่างที่ pin `@main` หรือ default ref = `main` → แก้แล้วมีผลทันที** (กลไก A, B)
> มีแค่ **Python module (กลไก C)** เท่านั้นที่ถูก pin ด้วย tag → ปลอดภัย แก้ได้โดยไม่กระทบใคร

ผลที่ตามมา: การแก้ของใน common-data ที่ pin `main` = **เปลี่ยนพฤติกรรม production ของหลาย repo พร้อมกัน**
→ ต้องคิดเรื่อง backward-compatibility เสมอ และควรพิจารณา pin เป็น tag สำหรับงาน production (ดูหัวข้อ "Release & Versioning" ในแต่ละ part)

---

## 6. common-data CI ของตัวเอง

`.gitlab-ci.yml` ที่ root ของ common-data ใช้ build/test/release ตัว module 2 ตัว + base image:
```yaml
include:
  - "pipeline/common.gitlab-ci.yml"
  - "common-python-dataflow/.gitlab-ci.yml"
  - "common-python-dataflow/dataflow-base-image.gitlab-ci.yml"
  - "common-python-cloudrun/.gitlab-ci.yml"
stages: [build, deploy-stg, deploy-prod]
```
→ release ของ module = git tag (เช่น `python-cloudrun-0.0.19`, `0.0.64`) — รายละเอียดที่ [03](03-dataflow-module.md)/[04](04-cloudrun-module.md)

---

ต่อไป: อ่าน part ที่สนใจได้เลย — [01 TF](01-tf-infrastructure.md) · [02 Dataform](02-dataform.md) · [03 Dataflow module](03-dataflow-module.md) · [04 Cloud Run module](04-cloudrun-module.md) · [05 GitLab CI](05-gitlab-ci.md) · [06 Scripts](06-scripts.md)
