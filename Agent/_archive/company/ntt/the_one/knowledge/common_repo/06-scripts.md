# 06 — Part 6: Scripts (รวม `deploy_schemas.py`)

> `scripts/` ใน common-data — deploy script ที่ถูก **fetch ตอน runtime** โดย CI ของ repo อื่น
> ไฟล์นี้ตอบคำถามตรง ๆ ว่า **"ถ้าผมจะแก้ `scripts/bigquery/deploy_schemas.py` ต้องทำยังไง / ใครโดนผลกระทบ"**

---

## 1. มีอะไรใน `scripts/`

```
scripts/
├── bigquery/
│   └── deploy_schemas.py          สร้าง/อัปเดต BigQuery table จาก JSON schema (smart change detection)
├── dataflow/
│   ├── deploy_dataflow.sh         launch Dataflow flex template (update/drain/probe)
│   ├── prepare_dataflow_config.sh merge base.yaml + <env>.yaml → base64
│   └── prepare_dataflow_spec.sh   render container_spec.json (${IMAGE_FULL}) → อัป GCS
└── dataform/
    ├── deploy_dataform.sh         orchestrate Dataform deploy (ดู 02-dataform.md)
    └── dataform_api.py            Dataform REST API helper (ดู 02-dataform.md)
```

ของ Dataform อธิบายแล้วใน [02-dataform.md](02-dataform.md) — ไฟล์นี้โฟกัส **BigQuery + Dataflow scripts**

---

## 2. `deploy_schemas.py` — BigQuery Table Deployer

### 2.1 มันทำอะไร

script เดียว (~1080 บรรทัด, stdlib + เรียก `bq` CLI) สร้าง/อัปเดต BigQuery table จากไฟล์ JSON schema
docstring เขียนว่า *"Consolidated from per-collector deploy.py files into a single script"* — คือเอา `deploy.py`
ของแต่ละ collector มารวมเป็นตัวเดียว

**รองรับ table type:** `native`, `iceberg`, `external_iceberg`, `external` (Hive-partitioned), `view`

**CLI:**
```bash
python deploy_schemas.py <PROJECT_ID> <ENV> --schemas-dir <PATH> [--force] [--table NAME] [--dataset NAME]
# ตัวอย่าง
python deploy_schemas.py the1-loyalty-data-stg stg --schemas-dir infrastructure/members-collector/schemas
```
- อ่านทุกไฟล์ `*.json` ใน `--schemas-dir` (ข้ามไฟล์ที่ขึ้นต้น `(unuse)`)
- แต่ละ JSON ระบุ `dataset_id` ของตัวเอง → deploy ข้าม dataset ได้ในรอบเดียว
- แทนค่า `${env}` ใน JSON ด้วย ENV ที่ส่งมา

### 2.2 Smart change detection — หัวใจของ script

เทียบ schema ที่อยู่ใน BQ จริง vs JSON definition แล้วจัดเป็น 4 ระดับ:

| ChangeType | เงื่อนไข | สิ่งที่ทำ |
|------------|----------|-----------|
| `NO_CHANGE` | เหมือนเดิม | skip (แต่ยัง reconcile PK / max_staleness / description) |
| `ADDITIVE` | เพิ่ม column ใหม่อย่างเดียว | `ALTER TABLE ADD COLUMN` |
| `WIDENABLE` | เปลี่ยน type แบบปลอดภัย (INT64→FLOAT64, NUMERIC→BIGNUMERIC ฯลฯ) | `ALTER COLUMN SET DATA TYPE` |
| `BREAKING` | ลบ column / เปลี่ยน type อันตราย / เปลี่ยน mode / เปลี่ยน partition/cluster | native → **backup + drop + recreate + restore**; iceberg/external → drop + recreate (data ปลอดภัยใน GCS) |

reconcile เพิ่ม (เมื่อ table มีอยู่แล้ว): primary key (`ADD PRIMARY KEY ... NOT ENFORCED`), `max_staleness`, table/column description

> หมายเหตุความปลอดภัย: ระดับ BREAKING ของ native table จะ `bq cp` สำรอง แล้ว drop/recreate/restore อัตโนมัติ —
> ทำงานกับ `bq` CLI จริง การรัน script นี้ใน prod = แตะ table จริง ให้ระวัง

### 2.3 input — JSON schema file หน้าตาเป็นไง

JSON แต่ละไฟล์ = 1 table อยู่ใน `<consumer-repo>/infrastructure/<collector>/schemas/` มี field เช่น
`table_id`, `dataset_id`, `table_type`, `schema[]` (fields), `partitioning`, `clustering`, `primary_key`,
`max_staleness`, `biglake_config`/`external_config`, `create_status` (`create`|`drop`), `description`, `labels`

→ **schema เป็นของ consumer repo** ตัว script เป็นของ common-data

---

## 3. ⭐ deploy_schemas.py ถูกนำไปใช้ยังไง — คำตอบของคำถามหลัก

**`deploy_schemas.py` มีต้นฉบับที่เดียว: `common-data/scripts/bigquery/deploy_schemas.py`**
แต่ "การไปถึง consumer" มี **2 เส้นทาง** ขึ้นกับว่า repo นั้นอยู่ CI รุ่นไหน:

### เส้นทาง A — repo ที่ใช้ v2 component (ปัจจุบัน = loyalty-data) → **fetch สด ๆ จาก common-data**

job `.common-deploy-schemas` ใน `pipeline/v2/bigquery.gitlab-ci.yml`:
```yaml
.common-deploy-schemas:
  image: google/cloud-sdk:slim
  variables:
    COMMON_DATA_SCHEMAS_REF: "main"          # ← ref ที่จะดึง
  before_script:
    - !reference [.common-gcp-prepare, script]
    - |
      curl -sf \
        "$CI_SERVER_URL/api/v4/projects/The1central%2FThe1%2Fthe1-data%2Fcommon-data/repository/files/scripts%2Fbigquery%2Fdeploy_schemas.py/raw?ref=${COMMON_DATA_SCHEMAS_REF}" \
        -H "JOB-TOKEN: $CI_JOB_TOKEN" -o /tmp/deploy_schemas.py
  script:
    - python3 /tmp/deploy_schemas.py "$GCP_PROJECT_ID-$WORKSPACE_ENV" "$WORKSPACE_ENV" --schemas-dir "$CI_PROJECT_DIR/$SCHEMAS_PATH"
```
- ตอน job รัน มัน **`curl` ดาวน์โหลด `deploy_schemas.py` สดจาก common-data** (GitLab Repository Files API) ลง `/tmp/`
- component `service-pipeline` เอา job นี้ไปทำเป็น `deploy-schema:stg` / `deploy-schema:prod` (มี `$SCHEMAS_PATH` จาก input `schemas_path`)
- **Pin ที่:** ตัวแปร `COMMON_DATA_SCHEMAS_REF` — **default = `main`**

→ **ผลคือ: loyalty-data ดึง `deploy_schemas.py` เวอร์ชันล่าสุดของ branch `main` ทุกครั้งที่ deploy-schema job รัน**

### เส้นทาง B — repo legacy (sales, catalog, gamification, messaging, partner, foundry) → **มี copy ของตัวเอง**

repo เหล่านี้มีไฟล์ `deploy_schemas.py` (หรือ `deploy.py`) **ก๊อปไว้ในเครื่อง** ที่
`<repo>/scripts/deploy_schemas.py` หรือ `<repo>/infrastructure/<collector>/schemas/deploy.py`
แล้ว CI ของมันเรียก copy ในเครื่องตรง ๆ เช่น:
```yaml
script:
  - python3 "$CI_PROJECT_DIR/scripts/deploy_schemas.py" "$GCP_PROJECT_ID-$STG_ENV" "$STG_ENV" ...
```
→ copy เหล่านี้เป็น **fork** — อาจเก่ากว่า / ต่างจากต้นฉบับใน common-data

> หมายเหตุ: loyalty-data ก็ยังมีไฟล์ `scripts/deploy_schemas.py` ค้างอยู่ในเครื่องเช่นกัน แต่ job ที่มาจาก
> v2 component (`deploy-schema:stg/prod`) ใช้ตัวที่ `curl` มาจาก common-data — ไฟล์ในเครื่องของ loyalty-data
> จึงเป็นของตกค้าง (legacy leftover) ไม่ใช่ตัวที่ component รัน

---

## 4. ⭐ "ถ้าผมจะแก้ `deploy_schemas.py` ต้องทำยังไง" — คู่มือ

### ขั้นที่ 1 — แก้ที่ต้นฉบับ
แก้ไฟล์ `common-data/scripts/bigquery/deploy_schemas.py` ที่เดียว (อย่าไปแก้ copy ในเครื่องของ repo อื่น)

### ขั้นที่ 2 — เข้าใจว่าใครจะโดน และเมื่อไหร่

| Consumer | กลไก | โดนผลกระทบไหม / เมื่อไหร่ |
|----------|------|--------------------------|
| **loyalty-data** (v2 component) | curl fetch `ref=main` | **โดนทันที** — deploy-schema job รอบถัดไปดึงเวอร์ชันใหม่ |
| **sales / catalog / gamification / messaging / partner / foundry** (legacy) | copy ในเครื่อง | **ไม่โดน** — จนกว่าจะ copy ไฟล์ใหม่ไปทับเอง |

→ การแก้ `deploy_schemas.py` แล้ว merge เข้า `main` = **เปลี่ยนพฤติกรรมการ deploy BQ table ของ loyalty-data ทันที**
ในขณะที่ repo legacy ไม่ขยับเลย → ระบบจะ "ไม่เท่ากัน" ชั่วคราว

### ขั้นที่ 3 — ทดสอบก่อน merge เข้า main
เพราะ default ref = `main` แก้พลาด = loyalty-data deploy พัง เลือกวิธีใดวิธีหนึ่ง:
- **(แนะนำ) ทดสอบบน branch:** push แก้ไขขึ้น branch ของ common-data (เช่น `fix/deploy-schemas-x`)
  → ตั้ง `COMMON_DATA_SCHEMAS_REF: "fix/deploy-schemas-x"` ชั่วคราวใน CI ของ consumer ที่จะทดสอบ → รัน pipeline → ค่อย merge
- หรือรัน local: `python3 deploy_schemas.py the1-xxx-data-stg stg --schemas-dir <path> --table <one-table>` ชี้ stg ก่อน
- ใช้ `--table` / `--dataset` จำกัดขอบเขตตอนทดสอบ

### ขั้นที่ 4 — ถ้าอยากให้ deploy ของ production reproducible (pin version)
default `main` = ดึงสดทุกครั้ง (เสี่ยง) — ถ้าต้องการ pin:
- ตั้ง `COMMON_DATA_SCHEMAS_REF` เป็น **git tag** ของ common-data แทน `main` ในตัวแปร CI ของ consumer
- แล้วเวลาจะอัป ค่อย bump tag — เหมือนที่ component `component_version` แนะนำ ("dev → main, prod → tag")

### ขั้นที่ 5 — sync repo legacy (ถ้าต้องการให้เท่ากัน)
ถ้าการแก้นี้สำคัญและอยากให้ legacy repo ได้ด้วย ตัวเลือก:
- **ระยะสั้น:** copy `deploy_schemas.py` ไปทับ `<repo>/scripts/deploy_schemas.py` ของแต่ละ legacy repo (ทำ 6 รอบ)
- **ระยะยาว (แนะนำ):** migrate legacy repo ขึ้น v2 component → ทุก repo fetch จาก common-data ที่เดียว ไม่ต้อง copy อีก

> ⚠️ ทั้งหมดนี้คือ "การวางแผน" — ยังไม่ต้องลงมือแก้ จนกว่าจะ scope งานจริงชัด

---

## 5. Dataflow scripts — กลไกเดียวกัน

`deploy_dataflow.sh`, `prepare_dataflow_config.sh`, `prepare_dataflow_spec.sh` — ทำงานแบบเดียวกับ deploy_schemas.py:

| Script | หน้าที่ |
|--------|--------|
| `prepare_dataflow_config.sh` | `yq` merge `config/base.yaml` + `config/<env>.yaml` → base64 (ส่งเข้า pipeline ผ่าน `--dataflow_config`) |
| `prepare_dataflow_spec.sh` | `sed` แทน `${IMAGE_FULL}` ใน `container_spec.json` → อัปขึ้น GCS |
| `deploy_dataflow.sh` | launch flex template — pre-flight compat check (image + config hash) → `--update` ถ้าได้ ไม่ได้ก็ drain+fresh → probe (รอ RUNNING + workers ready + ไม่มี ERROR log) |

**v2:** job `.common-dataflow-deploy` / `.common-dataflow-rollback` ใน `pipeline/v2/dataflow.gitlab-ci.yml`
fetch 3 script นี้ผ่าน anchor `_fetch_common_scripts` (curl GitLab API, `ref = COMPONENT_VERSION` default `main`)
**legacy:** repo มี copy เองที่ `<repo>/scripts/`

`deploy_dataflow.sh` แก้ปัญหายาก ๆ ให้แล้ว: ตรวจ graph-incompatible (managed transform upgrade fail) แล้ว fallback drain+fresh,
detect benign GKE log noise, รอ worker startup จริง — ของพวกนี้ถ้า collector เขียนเองจะพลาดง่าย

---

## 6. ตารางสรุป — กลไก B (runtime fetch) ทั้งหมด

| Script | fetch โดย (v2) | ตัวแปร ref | default |
|--------|----------------|------------|---------|
| `scripts/bigquery/deploy_schemas.py` | `.common-deploy-schemas` (curl API) | `COMMON_DATA_SCHEMAS_REF` | `main` |
| `scripts/dataflow/*.sh` | `_fetch_common_scripts` (curl API) | `COMPONENT_VERSION` | `main` |
| `scripts/dataform/deploy_dataform.sh` + `dataform_api.py` | `.dataform-fetch-common-scripts` (git clone) | `COMMON_DATA_REF` | `main` |

ทั้ง 3 ต้องการ: common-data → Settings → CI/CD → **Job token allowlist** อนุญาต consumer project

---

## 7. ข้อสังเกต / ความเสี่ยงของ part นี้

- **default ref = `main` ทุกตัว** → ทุกการ merge เข้า main มีผลกับ v2 consumer ทันที ไม่มี staging buffer
- **legacy repo ถือ fork** — `deploy_schemas.py` / `deploy_dataflow.sh` มีหลายก๊อปปี้ทั่ว 6 repo อาจ drift ห่างจากต้นฉบับ
- ยังไม่มีการ pin tag สำหรับ production — `COMMON_DATA_SCHEMAS_REF` / `COMPONENT_VERSION` ตั้ง `main` หมด
- `deploy_schemas.py` รัน `bq` CLI ตรง — BREAKING change บน native table จะ backup/drop/recreate/restore เอง
  (มี backup `bq cp` ก่อน แต่ก็ควรรู้ว่า prod table จะถูกแตะจริง)

---

กลับไป: [README (index)](README.md) · [00 — Overview](00-overview-and-consumption-model.md)
