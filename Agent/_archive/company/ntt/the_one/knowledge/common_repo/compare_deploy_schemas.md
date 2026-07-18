# Compare — BQ Table Deploy Scripts (`deploy_schemas.py` vs per-collector `deploy.py`)

> เปรียบเทียบ script ที่ใช้ deploy BigQuery table ของทุก repo — flowchart + feature matrix
> เพื่อตอบว่า **ตัวไหน feature ครบกว่า / รองรับ use case ได้เยอะกว่า** ก่อนตัดสินใจ consolidate
>
> สร้างจากการอ่าน source ทั้ง 8 ไฟล์เต็ม ๆ + verify · วันที่ 2026-05-18 · **discussion only — ยังไม่แก้อะไร**

---

## 1. มีกี่ตัว / อยู่ที่ไหน

หา script deploy BQ table ทั้งระบบ เจอ **8 ไฟล์ — แต่จริง ๆ มี 6 ตัวที่ต่างกัน** (3 ไฟล์เหมือนกันเป๊ะ):

| # | Script | Path | บรรทัด | หมายเหตุ |
|---|--------|------|--------|----------|
| A | **`deploy_schemas.py`** (common) | `common-data/scripts/bigquery/deploy_schemas.py` | 1080 | **ตัวอ้างอิง — unified** |
| A | `deploy_schemas.py` (loyalty) | `loyalty-data/scripts/deploy_schemas.py` | 1080 | **byte-identical** กับ A (md5 `94fb28f0…`) |
| A | `deploy_schemas.py` (catalog) | `catalog-data/scripts/deploy_schemas.py` | 1080 | **byte-identical** กับ A |
| B | `deploy.py` (partner) | `partner-data/infrastructure/master-collector/schemas/deploy.py` | 1942 | per-collector, Iceberg-heavy |
| C | `deploy.py` (messaging) | `messaging-data/infrastructure/messages-collector/schemas/deploy.py` | 1739 | per-collector, Iceberg-heavy |
| D | `deploy.py` (sales) | `sales-data/infrastructure/sales-collector/schemas/deploy.py` | 724 | per-collector, native-only |
| E | `deploy.py` (gamification) | `gamification-data/infrastructure/account-missions-collector/schemas/deploy.py` | 662 | per-collector, native-only |
| F | `deploy.py` (foundry) | `foundry/infrastructure/svoc-transferor/schemas/deploy.py` | 156 | per-collector, native+view, minimal |

> **A = unified** (`common-data` + 2 copy ที่ loyalty/catalog) — อันนี้คือ "ตัว common"
> **B–F = per-collector fork** — แต่ละ collector มี `deploy.py` ของตัวเองคนละแบบ

---

## 2. ภาพใหญ่ — script มี 2 "generation"

ก่อนดู flowchart ต้องเข้าใจว่า script 2 ตระกูลนี้เกิดคนละยุค:

### Gen 1 — per-collector `deploy.py` (B–F)
- script ต้นฉบับที่แต่ละ collector copy-ดัดแปลงกันเอง
- **partner/messaging (B,C)** = ตระกูลเก่าสุด — มี **PyIceberg + Java iceberg-tools + dummy-data + Iceberg metadata generation** เพราะสมัยนั้น "source Iceberg table ต้องสร้างเอง"
- **sales/gamification (D,E)** = ตัด Iceberg ออก เหลือ native-only
- **foundry (F)** = minimal สุด เอาแค่ native + view
- อ่าน JSON จาก **directory ของตัวเองเท่านั้น** (`os.listdir(script_dir)`)

### Gen 2 — unified `deploy_schemas.py` (A)
- รวม `deploy.py` ทุก collector เป็น script เดียว (docstring เขียน *"Consolidated from per-collector deploy.py files"*)
- **ตัด PyIceberg/dummy-data/Java tools ทิ้งทั้งหมด** — เพราะสถาปัตยกรรมเปลี่ยน: **source Iceberg table ถูกสร้างอัตโนมัติโดย Dataflow `managed.Write` ผ่าน BLMS REST แล้ว** ไม่ต้องให้ deploy script สร้าง Iceberg metadata เองอีก
- เพิ่มของใหม่: **safe type widening, view, CTAS, external hive-partitioned, description reconcile, `--schemas-dir`**
- รับ `--schemas-dir <PATH>` → deploy schema ของ collector ไหนก็ได้ (ไม่ผูกกับ directory ตัวเอง)

> **ประเด็นสำคัญ:** B,C ตัวใหญ่ (1942/1739 บรรทัด) **ไม่ได้แปลว่า feature เยอะกว่า** — บรรทัดส่วนใหญ่คือ
> โค้ด PyIceberg/dummy-data ที่ **ตกยุคไปแล้ว** (managed.Write สร้าง Iceberg ให้เอง) → เป็น dead weight

---

## 3. Flowchart

### 3.1 — A: `deploy_schemas.py` (common / unified)

```
main(argv)
 │  รับ:  <PROJECT_ID> <ENV> --schemas-dir <PATH> [--force] [--table N] [--dataset D]
 ▼
สแกน *.json ใน --schemas-dir
 │  • ข้ามไฟล์ที่ขึ้นต้น "(unuse)"
 │  • ข้ามไฟล์ว่าง (empty → skip)
 │  • แทน ${env} ด้วย ENV
 │  • filter ตาม --table / --dataset
 ▼
for each table definition → deploy_table()
 │
 ├─ create_status == "drop" ─────────▶ drop table แล้วจบ
 │
 ├─ table_type == "view" ────────────▶ CREATE OR REPLACE VIEW (แทน {project_id}) จบ
 │
 ├─ table ยังไม่มี ──────────────────▶ generate_create_sql() → execute
 │     (native / native CTAS / iceberg / external_iceberg / external-hive)
 │
 └─ table มีอยู่แล้ว → compare_schemas(current vs definition)
        │
        ├─ NO_CHANGE  → reconcile (PK / max_staleness / description) → skip
        │
        ├─ ADDITIVE   → ALTER TABLE ADD COLUMN → reconcile
        │
        ├─ WIDENABLE  → ALTER COLUMN SET DATA TYPE   ★ มีเฉพาะตัวนี้
        │               (INT64→FLOAT64/NUMERIC, NUMERIC→BIGNUMERIC, FLOAT64→BIGNUMERIC)
        │               + เพิ่ม column ใหม่ถ้ามี → reconcile
        │
        └─ BREAKING
              ├─ native  → backup (bq cp) → drop → recreate → restore (column ร่วม) → drop backup
              └─ iceberg/external → drop → recreate (ข้อมูลปลอดภัยใน GCS)
```
- **เรียก BQ ด้วย:** `bq` CLI subprocess
- **Iceberg:** สร้างด้วย **SQL DDL** (`CREATE TABLE ... WITH CONNECTION ... OPTIONS(table_format='ICEBERG')`) — **ไม่มี** PyIceberg/dummy-data/Java

### 3.2 — D,E: `deploy.py` (sales / gamification — native-only)

```
main(argv)   รับ: <PROJECT_ID> <ENV> [--force] [--table] [--dataset]
 ▼
สแกน *.json ใน "directory ของ script เอง"   (ไม่มี --schemas-dir / ไม่ข้าม (unuse) / ไม่ skip empty)
 │  แทน ${env} · filter --table/--dataset
 ▼
for each definition → deploy_table()
 ├─ create_status == "drop" ──▶ drop จบ
 ├─ table ยังไม่มี ───────────▶ generate_create_sql() (native เท่านั้น) → execute
 └─ table มีอยู่ → compare_schemas()
        ├─ NO_CHANGE → reconcile (PK, max_staleness) → skip
        ├─ ADDITIVE  → ALTER ADD COLUMN → reconcile
        └─ BREAKING  → backup → drop → recreate → restore → drop backup
                       (sales: restore รองรับ column_mapping เปลี่ยนชื่อ column)
```
- ไม่มี WIDENABLE · ไม่มี view · ไม่มี Iceberg · ไม่มี CTAS
- sales: PK reconcile **เต็ม** (add/drop/change + ปลด max_staleness ชั่วคราวตอน drop PK สำหรับ CDC)
- gamification: PK reconcile **อ่อน** (add อย่างเดียว, mismatch แค่ warn) แต่ partition field-type detection ดีกว่า

### 3.3 — B,C: `deploy.py` (partner / messaging — Iceberg-heavy)

```
main(argv)   รับ: <PROJECT_ID> <ENV> [--force] [--table] [--dataset]
 ▼
สแกน *.json ใน directory ตัวเอง · แทน ${env} · filter
 ▼
for each definition → deploy_table()
 ├─ create_status == "drop" ──▶ drop BQ table + ลบ GCS path (iceberg) จบ
 ├─ (partner) rename_from ────▶ rename table เก่า → ชื่อใหม่ ก่อน
 ├─ table ยังไม่มี
 │     ├─ native ───────────▶ CREATE TABLE
 │     └─ external_iceberg ─▶ เลือก Java/Python สร้าง Iceberg metadata
 │                            → ถ้ายังไม่มีข้อมูล: สร้าง dummy data (PyIceberg)
 │                            → CREATE EXTERNAL TABLE → ลบ dummy data
 └─ table มีอยู่ → compare_schemas()
        ├─ NO_CHANGE → skip   (ไม่ reconcile PK/staleness/description)
        ├─ ADDITIVE
        │    ├─ native ──────▶ ALTER ADD COLUMN
        │    └─ iceberg ─────▶ evolve Iceberg schema (PyIceberg) → drop+recreate BQ
        └─ BREAKING
             ├─ native ──────▶ backup → drop → recreate → restore → drop backup
             └─ iceberg ─────▶ เช็คมีข้อมูลไหม → evolve schema / สร้าง dummy
                                → drop+recreate BQ external table
```
- มี PyIceberg + Java iceberg-tools + dummy-data + Iceberg metadata V2 generation
- partner เพิ่ม: partitioned-Iceberg manifest generation (ใช้ `fastavro`), `rename_from`
- **ไม่ reconcile** PK / max_staleness / description เลย
- ไม่มี WIDENABLE · ไม่มี view · ไม่มี CTAS

### 3.4 — F: `deploy.py` (foundry — minimal)

```
main(argv)   รับ: <PROJECT_ID> <ENV>   (ไม่มี flag เลย)
 ▼
สแกน *.json ใน directory ตัวเอง · แทน ${env} + ${project_id}
 ▼
for each definition → deploy()
 ├─ table_type == "view"  ──▶ CREATE OR REPLACE VIEW ... SELECT * FROM <source>
 └─ อื่น ๆ (native)        ──▶ ถ้ายังไม่มี: CREATE TABLE IF NOT EXISTS ;  ถ้ามีแล้ว: skip
```
- **ไม่มี change detection / migration / reconcile เลย** — idempotent ล้วน
- มี view (CREATE OR REPLACE) เป็นจุดเด่นเดียว

---

## 4. Feature Comparison Matrix

| Feature | A common `deploy_schemas.py` | B partner | C messaging | D sales | E gamification | F foundry |
|---------|:--:|:--:|:--:|:--:|:--:|:--:|
| **บรรทัด** | 1080 | 1942 | 1739 | 724 | 662 | 156 |
| **CLI `--schemas-dir`** (deploy collector ไหนก็ได้) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| CLI `--force / --table / --dataset` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Table type: native** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Table type: **view** | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Table type: **native CTAS** (`native_query`) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Table type: iceberg (DDL) | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Table type: external_iceberg | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Table type: **external GCS/Hive-partitioned** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Change detection** | ✅ 4 ระดับ | ✅ 3 | ✅ 3 | ✅ 3 | ✅ 3 | ❌ ไม่มี |
| ↳ **WIDENABLE** (safe type widening) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Breaking: backup→drop→recreate→restore (native) | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Breaking: restore + **column rename map** | ❌ | ❌ | ❌ | ✅ | ❌ | — |
| Reconcile: **primary key** | ⚠️ add-only | ❌ | ❌ | ✅ add/drop/change+CDC | ⚠️ add-only | ❌ |
| Reconcile: **max_staleness** | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ |
| Reconcile: **table/column description** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Partitioning DAY/MONTH/HOUR + cluster | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **INT64 YYYYMMDD partition** (`PARSE_DATE`) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Partition field-type detection (DATE vs TS) | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | — |
| JSON: ข้าม `(unuse)` files | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| JSON: skip empty file | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| JSON: `${env}` substitution | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| JSON: `${project_id}` substitution | ✅ (view) | ❌ | ❌ | ❌ | ❌ | ✅ |
| `create_status: drop` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| PyIceberg / dummy-data / Java iceberg-tools | ❌ *(ตั้งใจตัด)* | ✅ | ✅ | ❌ | ❌ | ❌ |
| `rename_from` (table rename) | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| เรียก BQ ผ่าน | `bq` CLI | `bq` CLI | `bq` CLI | `bq` CLI | `bq` CLI | `bq` CLI |
| เป็น single source of truth | ✅ | ❌ fork | ❌ fork | ❌ fork | ❌ fork | ❌ fork |

✅ = มี/ครบ · ⚠️ = มีแต่จำกัด · ❌ = ไม่มี

---

## 5. สรุป — ตัวไหน feature ครบกว่า (verify แล้ว)

### ✅ ยืนยัน: `deploy_schemas.py` (A — common) ครบที่สุดสำหรับสถาปัตยกรรมปัจจุบัน

A ชนะขาดใน feature ที่ deploy.py ตัวอื่น **ไม่มีเลยสักตัว**:
- **WIDENABLE** — เปลี่ยน type ปลอดภัยแบบ in-place (INT64→FLOAT64 ฯลฯ) ไม่ต้อง drop table
- **view** + **CTAS** (`native_query`) — มีแค่ A (foundry มี view อย่างเดียว ไม่มี CTAS)
- **external GCS/Hive-partitioned** table type
- **INT64 YYYYMMDD partitioning** — สำคัญมากกับ schema ของ platform นี้ (`ingestedTHDate` เป็น INT)
- **description reconcile** (table + column)
- ข้าม `(unuse)` file + skip empty file
- **`--schemas-dir`** — deploy schema ของ collector ไหนก็ได้ → เป็นเหตุผลที่มันถูกใช้เป็น common script
- เป็น single source of truth (B–F เป็น fork ต่างคนต่างดูแล)

### ⚠️ ข้อควรรู้ 2 ข้อ (ไม่ขัดข้อสรุป แต่ต้องเข้าใจ)

**(1) partner/messaging ใหญ่กว่า แต่ไม่ได้เก่งกว่า**
1942/1739 บรรทัดส่วนใหญ่ = โค้ด PyIceberg/Java/dummy-data ที่ **ตกยุค** — ปัจจุบัน source Iceberg table
ถูกสร้างอัตโนมัติโดย Dataflow `managed.Write` ผ่าน BLMS REST แล้ว deploy script ไม่ต้องสร้าง Iceberg metadata เอง
→ A จงใจตัดส่วนนี้ทิ้ง = ฟีเจอร์ที่ "หายไป" คือฟีเจอร์ของแนวทางที่เลิกใช้แล้ว ไม่ใช่ regression
(ยังต้อง confirm ว่า collector ที่ partner/messaging ดูแล ไม่มี table ที่ยังพึ่ง flow Iceberg-metadata เดิม — ดูข้อ 6)

**(2) จุดเดียวที่ A อ่อนกว่าของจริง = PK reconciliation ของ sales (D)**
- A: PK reconcile แบบ **add-only** — ถ้า PK ใน BQ ไม่ตรง definition แค่ warn "Manual intervention needed"
- D (sales): PK reconcile **เต็มวงจร** — add / drop / change ได้ และมี logic ปลด `max_staleness` ชั่วคราวก่อน drop PK (จำเป็นสำหรับ CDC table) แล้ว set กลับ
- → ถ้าจะ consolidate ทุก repo มาที่ A ควร **port PK-lifecycle logic ของ sales เข้า A ก่อน** ไม่งั้น sales จะเสีย capability
- (column-rename-map ตอน restore ของ sales ก็เป็น nice-to-have ที่ A ไม่มี — แต่ severity ต่ำกว่า)

### ตารางคะแนนสรุป

| Script | ครบสำหรับ arch ปัจจุบัน | จุดแข็งเฉพาะตัว | สถานะ |
|--------|:--:|----------------|-------|
| **A common `deploy_schemas.py`** | **ดีที่สุด** | widening, view, CTAS, external-hive, description reconcile, `--schemas-dir` | ควรเป็นมาตรฐานกลาง |
| D sales `deploy.py` | ปานกลาง | **PK lifecycle เต็ม + CDC staleness coordination**, column-rename map | จุดเดียวที่เก่งกว่า A — ควร port เข้า A |
| B partner `deploy.py` | เกินจำเป็น | PyIceberg partitioned, `rename_from` | ใหญ่เพราะโค้ดตกยุค |
| C messaging `deploy.py` | เกินจำเป็น | PyIceberg + fallback metadata | ใหญ่เพราะโค้ดตกยุค |
| E gamification `deploy.py` | ปานกลาง-ต่ำ | partition field-type detection | subset ของ A |
| F foundry `deploy.py` | ต่ำสุด | view (idempotent) | minimal — A ครอบคลุมหมดแล้ว |

---

## 6. ข้อที่ต้อง verify ต่อ ก่อนตัดสินใจ consolidate (discuss)

1. **partner/messaging มี table ที่ยังต้องใช้ flow Iceberg-metadata เดิมไหม?**
   เช็ค JSON schema ของ master-collector (partner) + messages-collector ว่ามี `table_type: external_iceberg`
   ที่คาดหวังให้ deploy script สร้าง Iceberg metadata/dummy-data เองหรือเปล่า — ถ้ามี ต้องยืนยันว่า
   managed.Write ครอบคลุมแล้วจริง ก่อนทิ้ง flow เก่า
2. **PK-lifecycle ของ sales** — A ต้อง port logic นี้เข้าก่อน ถึงจะ migrate sales มา A ได้แบบไม่เสีย capability
3. **partition field-type detection** — A เทียบ gamification: ต้องเช็คว่า A จัดการ DATE column โดยไม่ครอบ `DATE()` เกินถูกต้องครบ (A มี branch แยก DATE/INT64/TIMESTAMP อยู่แล้ว — ดูเหมือนครบ แต่ verify กับ schema จริง)
4. **`rename_from`** ของ partner — ถ้ายังจำเป็น (มี table ที่ต้อง rename) อาจต้อง port เข้า A
5. JSON schema ของ B–F วาง field ตรงกับที่ A คาดหวังไหม (เช่น A อ่าน `partitioning.field`, `biglake_config`, `external_config` — ตรวจ key naming)

---

## 7. ข้อเสนอแนะเชิงทิศทาง (ยังไม่ลงมือ — รอ discuss)

- **A เป็น base ที่ถูกต้อง** สำหรับ consolidation — ไม่ต้องไปยึด deploy.py ตัวใหญ่
- ก่อน migrate: **port 1 อย่างเข้า A** = PK lifecycle ของ sales (add/drop/change + CDC staleness)
- ของที่ "หาย" จาก B/C (PyIceberg/dummy-data) **ไม่ต้อง port** — เป็นแนวทางที่เลิกใช้ เว้นแต่ข้อ 6.1 พบว่ายังจำเป็น
- consolidation = ให้ทุก repo เลิกถือ `deploy.py` ของตัวเอง แล้วใช้ `.common-deploy-schemas` (v2) ที่ fetch `deploy_schemas.py` จาก common-data — ดู [06-scripts.md](06-scripts.md)

---

กลับไป: [README (index)](README.md) · [06 — Scripts](06-scripts.md)
