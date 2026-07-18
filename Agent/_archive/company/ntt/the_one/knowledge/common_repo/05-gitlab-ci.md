# 05 — Part 5: GitLab CI

> CI/CD ที่ share — `pipeline/` (job logic) + `templates/` (component interface) — รุ่น legacy / v2 / v3

---

## 1. ขอบเขต

common-data ให้ **CI/CD pipeline กลาง** เพื่อให้ collector ทุกตัว build/scan/deploy แบบเดียวกัน โดยไม่ต้องเขียน
GitLab CI เองทั้งหมด ของแบ่งเป็น 2 ชั้น:

| ชั้น | path | คืออะไร |
|------|------|--------|
| **`templates/`** | `templates/service-pipeline*/template.yml` | **GitLab CI Component** — "หน้าตา/interface" ที่ consumer `include` มี `spec.inputs` |
| **`pipeline/`** | `pipeline/v2/*.yml`, `pipeline/common*.yml` | **job logic จริง** — hidden job (`.common-*`) ที่ component/consumer extend |

มี 3 รุ่นอยู่พร้อมกัน:

| รุ่น | path | สถานะ | ใครใช้ |
|-----|------|-------|--------|
| **legacy** | `pipeline/common.gitlab-ci.yml`, `common-base/`, `dataflow/`, `terraform/` | ยังใช้งาน | 6 repo (sales, catalog, gamification, messaging, partner, foundry) |
| **v2** | `pipeline/v2/` + `templates/` | **ปัจจุบัน** | loyalty-data |
| **v3** | `pipeline/v3/` | ยังไม่มี consumer | — |

---

## 2. v2 — สถาปัตยกรรมแบบ layer

`pipeline/v2/` แยกเป็น layer ตาม comment ในไฟล์:

```
Layer 1  base.gitlab-ci.yml      primitives: rules, GCP auth, Kaniko build, uv cache
Layer 2  terraform.gitlab-ci.yml terraform plan/apply
Layer 2  scan.gitlab-ci.yml      gitleaks / trivy / sonar / DefectDojo
Layer 2  bigquery.gitlab-ci.yml  .common-deploy-schemas (fetch deploy_schemas.py)
Layer 3  dataflow.gitlab-ci.yml  build/deploy/promote/rollback ของ Dataflow
Layer 3  cloudrun.gitlab-ci.yml  deploy/redeploy/rollback ของ Cloud Run
Layer 4  dataform.gitlab-ci.yml  build/test/deploy/assertion ของ Dataform
```

### Layer 1 `base.gitlab-ci.yml` — มีอะไรสำคัญ
- **Trigger rules** — `.rules_app_changes`, `.rules_stg_only`, `.rules_prod_only`, `.rules_infra_*`
  - แยก pipeline type: deploy / terraform / dataform ไม่ชนกัน (`.rules_block_non_*_triggers`)
  - push ที่แตะแค่ `<svc>/dataform/**` จะไม่ rebuild image collector
- **`.common-gcp-prepare`** — decode SA จาก `T1_PIPELINE_SA` (prod) / `T1_PIPELINE_NP_SA` (non-prod) → activate
- **`.common-build-image`** — Kaniko build push **ทั้ง stg + prod GAR ในรอบเดียว** (CloudRun pattern)
- **`.common-uv_base`** — image uv + cache `.venv` keyed ด้วย `uv.lock`

### Layer 3 `dataflow.gitlab-ci.yml` — จุดที่เกี่ยวกับ scripts
- `_fetch_common_scripts` — **fetch `deploy_dataflow.sh` / `prepare_dataflow_*.sh` จาก common-data ตอน runtime** (กลไก B) ref = `COMPONENT_VERSION`
- `.common-dataflow-build-image` — build push stg เท่านั้น (ใช้ NP SA เพราะ base image อยู่ `the1-common-data-stg`)
- `.common-dataflow-promote-image` — `crane copy` stg → prod
- `.common-dataflow-deploy` — merge config → render spec → launch → บันทึก deployed SHA ลง GCS
- `.common-dataflow-rollback` — deploy ภาพเก่าโดยไม่ rebuild (trigger `TRIGGER_ROLLBACK=1`)

### Layer 2 `bigquery.gitlab-ci.yml` — `.common-deploy-schemas`
fetch `deploy_schemas.py` จาก common-data (กลไก B) แล้วรัน — รายละเอียดเต็มที่ [06-scripts.md](06-scripts.md)

---

## 3. v2 — CI Components (`templates/`)

Component คือ entry point ที่ consumer `include` มี `spec.inputs` ชัดเจน

### `service-pipeline` — component หลัก
ไฟล์ `templates/service-pipeline/template.yml` — ใช้กับ collector (dataflow หรือ cloudrun)
- รับ input ~20 ตัว — สำคัญ: `svc_name`, `service_type` (`dataflow`|`cloudrun`), `infra_path`, `gcp_project_id`,
  `gar_repository_name`, `docker_image_name`, `gcp_service_account`, `schemas_path`, `component_version`,
  `dataflow_base_image_default`, `config_bucket`, `max_workers`
- ภายในมัน `include` `pipeline/v2/{base,scan,terraform,cloudrun,dataflow,bigquery,dataform}.gitlab-ci.yml`
  **และ** include sub-component ตาม `service_type`:
  ```yaml
  - component: ".../service-pipeline-$[[ inputs.service_type ]]@$[[ inputs.component_version ]]"
  ```
  → load เฉพาะ `service-pipeline-dataflow` **หรือ** `service-pipeline-cloudrun` ตัวเดียว
- สร้าง job: `lint`, `test`, `scan-secrets`, `sonar-scan`, `scan-image`, `defectdojo-gate`,
  `infra:stg`, `deploy-schema:stg`, `approve:infra:prod`, `infra:prod`, `deploy-schema:prod`

### sub-component
| Component | job ที่เพิ่ม |
|-----------|-------------|
| `service-pipeline-dataflow` | `dataflow-build-image`, `dataflow:stg`, `dataflow:promote-image`, `approve:prod`, `dataflow:prod` |
| `service-pipeline-cloudrun` | `build-image`, `deploy:stg`, `redeploy:stg`, `approve:prod`, `deploy:prod`, `redeploy:prod`, `rollback` |
| `service-pipeline-dataform` | `build`, `unit-test`, `deploy:stg`, `assertion:stg`, `approve:prod`, `deploy:prod` (ต่อ entity) |
| `service-pipeline-terraform` | `terraform:apply:stg`, `terraform:apply:prod` (สำหรับ project ที่มีแต่ infra/dataform) |

### `component_version` — input สำคัญเรื่อง version
```yaml
component_version:
  default: "main"
  description: "version ของ sub-components + scripts. dev → pin branch เช่น main;
                production → pin tag (เช่น 0.1.0) เพื่อให้ pipeline reproducible"
```
ค่านี้ใช้ทั้ง 2 ที่: (1) `@<ref>` ของ sub-component (2) `COMPONENT_VERSION` ที่ `_fetch_common_scripts` ใช้ clone

---

## 4. consumer ใช้ CI อย่างไร

### v2 — `loyalty-data` (ตัวอย่างจริง)
root `.gitlab-ci.yml`:
```yaml
include:
  - project: "The1central/The1/the1-data/common-data"
    ref: main
    file: "pipeline/v2/base.gitlab-ci.yml"
  - project: "The1central/The1/the1-data/common-data"
    ref: main
    file: "pipeline/v2/terraform.gitlab-ci.yml"
```
แต่ละ collector `<collector>/.gitlab-ci.yml`:
```yaml
include:
  - component: "gitlab.com/The1central/The1/the1-data/common-data/service-pipeline@main"
    inputs:
      svc_name: "members-collector"
      service_type: "dataflow"
      infra_path: "infrastructure/members-collector"
      schemas_path: "infrastructure/members-collector/schemas"
      gcp_project_id: "the1-loyalty-data"
      gar_repository_name: "members-collector"
      docker_image_name: "members-collector"
      gcp_service_account: "t1-members-collector"
      domain_name: "the1-loyalty-data"
  - component: ".../service-pipeline-dataform@main"
    inputs: { ... }
```
ดูตัวอย่างเต็มที่ `pipeline/v2/example-service.gitlab-ci.yml`

### legacy — 6 repo ที่เหลือ
root `.gitlab-ci.yml`:
```yaml
include:
  - project: "The1central/The1/the1-data/common-data"
    file: "pipeline/common.gitlab-ci.yml"
  - ".gitlab/ci/dataform-template.gitlab-ci.yml"   # template ของ repo เอง
  - "<collector>/.gitlab-ci.yml"                    # job เขียนเองในเครื่อง
```
legacy = include `pipeline/common.gitlab-ci.yml` ก้อนเดียว แล้วแต่ละ collector เขียน job เองเยอะ
(gamification/messaging แทบเขียน job เองหมด ใช้แค่ anchor บางตัวจาก common)

---

## 5. flow ของ pipeline (v2)

```
push main + แตะ <svc>/src         →  lint → test → scan → build-image → scan-image
                                       → dataflow:stg / deploy:stg
                                       → (approve:prod manual) → promote → dataflow:prod
push main + แตะ infra_path         →  infra:stg → (approve:infra:prod) → infra:prod
push main + แตะ schemas_path       →  deploy-schema:stg → (manual) deploy-schema:prod  + rebuild/redeploy
TRIGGER_TERRAFORM_APPLY_ALL=1      →  terraform เท่านั้น
TRIGGER_MANUAL_DEPLOY=1            →  app deploy เท่านั้น
TRIGGER_DATAFORM_DEPLOY_SVC=1      →  dataform เท่านั้น
TRIGGER_ROLLBACK=1 + ROLLBACK_SHA  →  rollback
```
prod ทุกเส้นมี **manual approval gate** (`approve:prod` / `approve:infra:prod`, `when: manual`, `allow_failure: false`)

---

## 6. v3 — รุ่นถัดไป

`pipeline/v3/` มีไฟล์ครบ (base, cloudrun, dataflow, dataform, terraform, scan, dataflow-base-image, example-service)
แต่ **ยังไม่มี consumer ตัวไหน include** — ถือว่าเป็น WIP/รุ่นทดลอง การเปลี่ยน v3 ตอนนี้ไม่กระทบ production
(เมื่อจะใช้จริงค่อย verify ความต่างจาก v2 อีกที)

---

## 7. variable ที่ต้องตั้งระดับ group/project

CI กลางต้องการ CI/CD variable เหล่านี้ (set ที่ GitLab group/project):
`T1_PIPELINE_SA` (file, base64 prod SA), `T1_PIPELINE_NP_SA` (file, base64 non-prod SA),
`T1_PIPELINE_PRD_SA` (dataform prod), `DEFECTDOJO_TOKEN`, `UV_IMAGE`, `RUNNER_TAG_STG/PROD`, `LBL_SELECT_OPTION`

**Prereq สำคัญ:** common-data → Settings → CI/CD → **Job token allowlist** ต้องอนุญาตทุก consumer project
(ไม่งั้น curl/clone fetch script ข้าม project จะ 401)

---

## 8. checklist — ถ้าจะแก้ CI ใน common-data

| แก้อะไร | ใครโดน | เมื่อไหร่ |
|---------|--------|----------|
| `pipeline/v2/*.yml` | loyalty-data + ทุก component (include `main`) | pipeline รอบถัดไป — ทันที |
| `templates/*/template.yml` | repo ที่ใช้ component นั้น `@main` | pipeline รอบถัดไป — ทันที |
| `pipeline/common.gitlab-ci.yml` (legacy) | 6 legacy repo | pipeline รอบถัดไป — ทันที |
| `pipeline/v3/*` | ไม่มีใคร | — |

ก่อนแก้:
1. ดูว่า anchor/job ที่จะแก้ ถูก extend จากที่ไหนบ้าง (`!reference`, `extends:`)
2. แก้ v2 และ legacy แยกกัน — เป็นคนละก้อน คนละ consumer
3. ถ้าเป็น breaking → consumer ควร pin `ref:`/`@tag` แทน `main` ก่อนค่อยปล่อย
4. ทดสอบกับ branch ของ common-data ได้: consumer ตั้ง `ref:` / `component_version` ชี้ branch นั้นชั่วคราว

---

ถัดไป: [06 — Scripts (deploy_schemas.py)](06-scripts.md)
