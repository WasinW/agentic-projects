# 02 — Part 2: Dataform

> ของกลางสำหรับ deploy Dataform pipeline — script (`deploy_dataform.sh`, `dataform_api.py`),
> CI templates (`pipeline/v2/dataform.gitlab-ci.yml`) และ CI component (`service-pipeline-dataform`)

---

## 1. ขอบเขต

collector หลายตัวมีโฟลเดอร์ `dataform/` (definitions SQL ของ public/refined layer) common-data ให้ **เครื่องมือ deploy
Dataform ที่เหมือนกันทุก repo** — repo ของ data domain **ไม่ต้องเขียน logic deploy เอง**

ของ Dataform ใน common-data มี 3 ชิ้น:

| ชิ้น | path | หน้าที่ |
|------|------|--------|
| `deploy_dataform.sh` | `scripts/dataform/deploy_dataform.sh` | orchestrate ทั้ง deploy cycle (clean → push → compile → validate → commit → invoke → poll) |
| `dataform_api.py` | `scripts/dataform/dataform_api.py` | Dataform v1beta1 REST API helper — stdlib ล้วน ไม่มี pip dep |
| CI templates | `pipeline/v2/dataform.gitlab-ci.yml` + `templates/service-pipeline-dataform/template.yml` | job ของ pipeline (build/test/deploy/assertion/approve) |

---

## 2. `dataform_api.py` — REST API helper

Python stdlib ล้วน (urllib, json, ssl, subprocess) — ไม่ต้อง `pip install` อะไร (รันใน image `google/cloud-sdk` ได้เลย)
ใช้ token จาก `gcloud auth print-access-token`

**14 subcommand:**

| Command | ทำอะไร |
|---------|--------|
| `deploy` | push ทุกไฟล์ใน `source_dir/` เข้า Dataform workspace (ข้าม `*_test.sqlx`) — patch `workflow_settings.yaml` ด้วย `--vars` / `--default-project` ได้ |
| `deploy-tag` | push ไฟล์จาก **git tag** ที่ระบุ (`git show <tag>:<file>`) — สำหรับ version-pinned prod deploy |
| `clean` | ลบ directory ใน workspace (scoped per entity) |
| `sync` | ลบ "ghost file" — ไฟล์ที่อยู่บน workspace แต่ไม่มีใน local แล้ว |
| `delete-file` | ลบไฟล์เฉพาะ |
| `commit` | `commitWorkspaceChanges` + `push` → ดัน workspace branch ขึ้น default branch |
| `compile` / `compile-git` | สร้าง compilation result จาก workspace / git commitish |
| `release` / `trigger` | สร้าง/อัปเดต Release Config + promote compilation result |
| `invoke` | สร้าง workflow invocation (scoped ด้วย `--tags`) |
| `poll` | เช็ค state ของ invocation |
| `query-actions` | ดึงรายละเอียด action ที่ FAILED |
| `validate-sql` | **BigQuery dry-run** ทุก compiled SQL — ก่อน invoke จริง |

มี retry/backoff สำหรับ HTTP 409/429/5xx และ throttle 0.2s/req (กัน quota "File access requests per minute")

---

## 3. `deploy_dataform.sh` — orchestration

รับ flag: `--entity <name>` `--validate-only` `--assertions-only` `--full-refresh` `--vars` `--release-config` `--tags`
อ่าน config จาก env var (`GCP_PROJECT_ID`, `WORKSPACE_ENV`, `DATAFORM_REPO`, `DATAFORM_SOURCE_DIR`, `DATAFORM_SA` …)

**ลำดับการทำงาน:**
```
Step 1a  clean    — ลบ definitions/{public,refined}/<entity> + definitions/tests จาก workspace
Step 1   sync     — ลบ ghost file ใน entity ของตัวเอง
Step 1b  deploy   — push ไฟล์ (จาก HEAD หรือจาก release tag ถ้ามี)
Step 3   compile  — สร้าง compilation result
Step 3b  validate-sql — BigQuery dry-run ทุก SQL  ← ถ้า fail หยุดก่อน ไม่แตะ prod
   (--validate-only จบตรงนี้)
Step 2   commit   — commit workspace → push ขึ้น default branch
Step 2b  trigger  — warmup release config (ถ้ามี)
Step 4   invoke   — สั่ง run workflow (scoped ด้วย tag = entity)
Step 5   poll     — รอจน SUCCEEDED / FAILED (timeout default 600s)
```
มี **rollback trap** — ถ้า fail หลัง push แล้ว จะ clean entity ออกจาก workspace ให้ ไม่ให้ไฟล์เสียค้าง

**Release mechanism (version-pinned deploy):** ลำดับความสำคัญ
1. env `DATAFORM_TAG` (override จาก CI)
2. `release.json` ของ entity (`<source_dir>/release.json`)
→ ถ้าเจอ tag จะ push definition จาก git tag นั้นแทน HEAD

---

## 4. consumer ใช้ Dataform ของ common-data อย่างไร

### 4.1 แบบ v2 component (`loyalty-data` — แนะนำ)

```yaml
include:
  - component: "$CI_SERVER_FQDN/The1central/The1/the1-data/common-data/service-pipeline-dataform@main"
    inputs:
      svc_name: "members-dataform"
      entity: "members"
      dataform_repo: "members-dataform"
      dataform_source_dir: "members-collector/dataform"
      gcp_project_id: "the1-loyalty-data"
      dataform_sa: "t1-members-collector@${GCP_PROJECT_ID}-${WORKSPACE_ENV}.iam.gserviceaccount.com"
      schemas_path: "infrastructure/members-collector/schemas"
```
component นี้ (`templates/service-pipeline-dataform/template.yml`) สร้าง **6 job ต่อ entity**:
```
build → unit-test → deploy:stg → assertion:stg → approve:prod(manual) → deploy:prod
```
และ component ก็ `include` `pipeline/v2/{base,dataform}.gitlab-ci.yml` ต่อ

### 4.2 script ถูกดึงมาจากไหน — กลไก B (runtime fetch)

job ใน `pipeline/v2/dataform.gitlab-ci.yml` **ไม่ได้มี `deploy_dataform.sh` ในตัว** — มัน `git clone` common-data สด ๆ
ทุกครั้งที่ job รัน (anchor `.dataform-fetch-common-scripts`):
```bash
COMMON_DATA_REF="${COMMON_DATA_REF:-main}"
git clone --depth 1 --branch "$COMMON_DATA_REF" \
  "https://gitlab-ci-token:${CI_JOB_TOKEN}@gitlab.com/.../common-data.git" /tmp/common-data
export DATAFORM_SCRIPT="/tmp/common-data/scripts/dataform/deploy_dataform.sh"
```
comment ในไฟล์เขียนชัด: *"Consumers must NOT vendor their own copy; CI templates always run the script from this fetch."*
→ **v2 = ของ common-data ตัวเดียวเป็น single source of truth**

- **Pin:** `COMMON_DATA_REF` (default `main`)
- **Prereq:** common-data → Settings → CI/CD → Job token allowlist ต้องอนุญาต consumer project

### 4.3 แบบ legacy (6 repo ที่เหลือ)

repo legacy (sales, catalog, gamification, messaging, partner, foundry) มี **copy `deploy_dataform.sh` ของตัวเอง**
ที่ `<repo>/scripts/deploy_dataform.sh` และมี `.gitlab/ci/dataform-template.gitlab-ci.yml` ของตัวเอง
เรียก `bash scripts/deploy_dataform.sh --entity ...` จาก copy ในเครื่อง

> นี่คือ fork — แก้ common-data แล้ว repo legacy **ไม่โดน** จนกว่าจะ copy ไฟล์ไปทับเอง

---

## 5. job ใน `pipeline/v2/dataform.gitlab-ci.yml`

template (hidden job) ที่ component ใช้ extend:

| Template | stage | ทำอะไร |
|----------|-------|--------|
| `.common-dataform-build` | build | `deploy_dataform.sh --validate-only` (compile + dry-run, ไม่ invoke) |
| `.common-dataform-unit-test` | build | `dataform test` ผ่าน `@dataform/cli` (node:20) — isolate entity, skip ถ้าไม่มี `*_test.sqlx` |
| `.common-dataform-deploy-stg` | deploy-stg | deploy เต็ม + invoke + poll — `resource_group: $DATAFORM_REPO-$WORKSPACE_ENV` (mutex) |
| `.common-dataform-assertion-stg` | deploy-stg | `--assertions-only` (รัน assertion อย่างเดียว) |
| `.common-dataform-approve-prod` | deploy-prod | gate `when: manual` |
| `.common-dataform-deploy-prod` | deploy-prod | deploy prod (auth ด้วย prod SA) |

จุดสำคัญ:
- **mutex** `resource_group: $DATAFORM_REPO-$WORKSPACE_ENV` — deploy กับ assertion ของ repo เดียวกันไม่ชนกัน (กัน workspace state พัง)
- **unit-test** รันบน node image ใช้ `@dataform/cli@3.0.35` — ไม่ต้องแตะ GCP
- **approve:prod** เป็น manual gate บังคับคนกด

---

## 6. checklist — ถ้าจะแก้ของ Dataform ใน common-data

### แก้ `deploy_dataform.sh` หรือ `dataform_api.py`
1. แก้ที่ `common-data/scripts/dataform/`
2. ผลกระทบ:
   - repo **v2** (loyalty-data) → โดน **ทันที** รอบ pipeline ถัดไป (clone `main`)
   - repo **legacy** (6 ตัว) → **ไม่โดน** — ต้อง copy ไฟล์ใหม่ไปทับ `<repo>/scripts/deploy_dataform.sh` เอง
3. ถ้าเพิ่ม flag ใหม่ → เช็คว่า CI template/component ส่ง flag นั้นรึยัง (เช่น `--extra-clean-paths` มี input `dataform_extra_clean_paths`)
4. ทดสอบกับ entity จริงด้วย `--validate-only` ก่อน

### แก้ CI template/component ของ Dataform
- แก้ `pipeline/v2/dataform.gitlab-ci.yml` หรือ `templates/service-pipeline-dataform/template.yml`
- repo ที่ใช้ `service-pipeline-dataform@main` โดนทันที — ดู [05-gitlab-ci.md](05-gitlab-ci.md)

### อยากให้ deploy แบบ pin version
- ตั้ง env `COMMON_DATA_REF` เป็น tag (ไม่ใช่ `main`) ใน CI ของ consumer
- หรือใช้ input `dataform_tag` ของ component เพื่อ pin **definition files** จาก git tag

---

## 7. ข้อสังเกต

- v2 ออกแบบให้ "ห้าม vendor copy" แต่ตอนนี้ **6/7 repo ยัง vendor copy อยู่** (legacy) → script Dataform กระจาย 7 ก๊อปปี้ที่อาจไม่ตรงกัน
- การ migrate legacy → v2 component คือทางแก้ที่ทำให้ Dataform script เหลือ source เดียว

---

ถัดไป: [03 — Dataflow common module](03-dataflow-module.md)
