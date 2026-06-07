# `common-data` Repository — Architecture & Solution Documentation

> เอกสารชุดนี้อธิบาย repo **`common-data`** (`gitlab.com/The1central/The1/the1-data/common-data`)
> ว่ามันคืออะไร มีอะไรบ้าง และ **ถูกนำไปใช้ (consume) โดย repo อื่น ๆ ได้อย่างไร**
>
> เขียนจากการอ่าน source จริงทั้ง repo + verify กับ consumer repo ทุกตัว
> วันที่: 2026-05-17 · common-data HEAD: `ec991a9`

---

## ทำไมต้องมีเอกสารชุดนี้

`common-data` ไม่ใช่ "service" — มันคือ **monorepo ของ shared building blocks** ที่ทุก data project
(loyalty-data, sales-data, catalog-data, gamification-data, messaging-data, partner-data, foundry ...)
ดึงไปใช้ ปัญหาคือ "ของที่ share" มันถูก share ด้วย **กลไกที่ต่างกัน 4 แบบ** และแต่ละแบบมี
**วิธี pin version ที่ต่างกัน** — ทำให้สับสนว่า "ถ้าแก้ไฟล์ X ใน common-data แล้ว ใครจะโดนผลกระทบบ้าง / เมื่อไหร่"

เอกสารชุดนี้ตอบคำถามนั้นแบบแยกเป็น part.

---

## ภาพรวม 30 วินาที

`common-data` แบ่งของที่ share ออกเป็น 6 part:

| # | Part | อยู่ที่ | กลไกการ share | Version pin |
|---|------|--------|----------------|-------------|
| 1 | **TF Infrastructure** | `infrastructure/` | Terraform git module + shared base-image | git ref ของ module / image tag |
| 2 | **Dataform** | `scripts/dataform/` + `pipeline/v2/dataform*` + `templates/service-pipeline-dataform/` | CI component + runtime `git clone` | `@ref` ของ component / `COMMON_DATA_REF` |
| 3 | **Dataflow common module** | `common-python-dataflow/` | Python git dependency (uv) | `tag` ใน `pyproject.toml` + `uv.lock` |
| 4 | **Cloud Run common module** | `common-python-cloudrun/` | Python git dependency (uv) | `tag` ใน `pyproject.toml` + `uv.lock` |
| 5 | **GitLab CI** | `pipeline/` + `templates/` | CI `include:` (component / project-file) | `@ref` ของ component / `ref:` ของ include |
| 6 | **Scripts** (deploy_schemas.py ฯลฯ) | `scripts/` | runtime fetch (curl GitLab API / git clone) | `COMMON_DATA_SCHEMAS_REF` / `COMPONENT_VERSION` (default `main`) |

> **กฎทอง 1 ข้อที่ต้องจำ:** ของที่ถูก share มี 2 โหมดใหญ่ —
> **(A) pin ด้วย version** (Python module, CI component tag) → consumer จะไม่โดนผลกระทบจนกว่าจะ bump เอง
> **(B) ดึงสด ๆ ที่ runtime จาก `main`** (scripts ส่วนใหญ่, component ที่ตั้ง `@main`) → consumer โดนผลกระทบ **ทันที** ใน pipeline รอบถัดไป

---

## โครงสร้างเอกสาร

อ่านตามลำดับนี้ครั้งแรก:

| ลำดับ | ไฟล์ | เนื้อหา |
|------|------|--------|
| 0 | [00-overview-and-consumption-model.md](00-overview-and-consumption-model.md) | **อ่านก่อน** — โครงสร้าง repo ทั้งหมด + กลไกการ share 4 แบบ + version-pinning matrix ของ consumer ทุกตัว |
| 1 | [01-tf-infrastructure.md](01-tf-infrastructure.md) | Part 1 — `infrastructure/` + shared dataflow base-image |
| 2 | [02-dataform.md](02-dataform.md) | Part 2 — Dataform: `deploy_dataform.sh`, `dataform_api.py`, component |
| 3 | [03-dataflow-module.md](03-dataflow-module.md) | Part 3 — `common-python-dataflow` (Beam adapters) |
| 4 | [04-cloudrun-module.md](04-cloudrun-module.md) | Part 4 — `common-python-cloudrun` (Cloud Run framework) |
| 5 | [05-gitlab-ci.md](05-gitlab-ci.md) | Part 5 — `pipeline/` + `templates/` (v2 / v3 / legacy) |
| 6 | [06-scripts.md](06-scripts.md) | Part 6 — `scripts/` — รวม **`deploy_schemas.py`** + คู่มือ "ถ้าจะแก้ ต้องทำยังไง" |

---

## คำถามที่เอกสารนี้ตอบให้ได้

- ถ้าผมแก้ `scripts/bigquery/deploy_schemas.py` → repo ไหนโดนผลกระทบ และเมื่อไหร่? → [06-scripts.md](06-scripts.md)
- consumer แต่ละ repo ดึง common-data ด้วยกลไกอะไร / version ไหน? → [00-overview](00-overview-and-consumption-model.md) (matrix)
- CI component `service-pipeline@main` ทำงานยังไง มี job อะไรบ้าง? → [05-gitlab-ci.md](05-gitlab-ci.md)
- module Python ที่ collector import เข้ามา มาจากไหน pin version ยังไง? → [03](03-dataflow-module.md) / [04](04-cloudrun-module.md)
- base image ของ Dataflow มาจากไหน ใครใช้บ้าง? → [01-tf-infrastructure.md](01-tf-infrastructure.md)

---

## ⚠️ Scope & ความถูกต้อง

- เอกสารนี้สร้างจาก snapshot ของ repo ณ วันที่ระบุด้านบน — ถ้า common-data ถูกแก้หลังจากนั้น ให้ verify กับ code จริงอีกครั้ง
- consumer repo บางตัวยังอยู่บน **CI รุ่นเก่า (legacy)** และบางตัวอยู่บน **v2** — เอกสารระบุไว้ชัดในแต่ละ part
- ทุกอย่างที่เขียน อ้างอิง path จริง — เปิดไฟล์ตามได้เลย
