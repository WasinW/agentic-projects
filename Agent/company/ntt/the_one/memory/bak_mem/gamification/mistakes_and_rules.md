# Critical Mistakes & Rules — MUST READ EVERY SESSION

## Rules (ห้ามละเมิด)

### Rule #1: อ่าน code จริงก่อนพูด อย่าเดา
- ห้ามสรุป path, config, behavior โดยไม่ได้อ่านไฟล์จริง
- ถ้าไม่แน่ใจ → อ่านก่อน → แล้วค่อยตอบ
- อย่าพูดว่า "น่าจะ" หรือ "คิดว่า" — ต้อง verify ก่อน

### Rule #2: อย่าวนแก้ไปแก้มา
- คิดให้ดีก่อนแก้ ไม่ใช่แก้แล้ว revert แล้วแก้ใหม่
- ถ้าไม่แน่ใจ → ถามก่อน → อย่าแก้ code ทันที
- ทุกครั้งที่แก้ต้องมั่นใจว่าเข้าใจ root cause จริงๆ

### Rule #3: สั้น กระชับ ลงมือทำ
- ห้ามอธิบายยาว 3 หน้าก่อนแก้
- User ต้องการ action ไม่ใช่ lecture
- แก้เสร็จแล้วค่อยอธิบายสั้นๆ

### Rule #4: จำ correction ที่ user บอก — จดทันทีเมื่อถูกแก้
- ถ้า user แก้ไขข้อมูลที่ผิด → จดใน memory ทันที
- ห้ามทำผิดซ้ำหลังจาก user แก้แล้ว

### Rule #5: แก้ปัญหาเฉพาะหน้าก่อน
- ถ้า production พัง → ให้วิธี fix ทันที (manual command) ก่อน
- อย่าแก้แค่ CI ที่ต้องรอ deploy — user ต้องการ fix NOW

### Rule #6: ดูให้ชัดว่าอยู่ที่ path ไหน
- **Correct path**: `loyalty/loyalty_paralel/loyalty-data/` (BLMS REST, deployed code)
- **Wrong path**: `loyalty/loyalty-data/` (Hadoop, old code — อย่าแตะ)
- ตรวจ path ทุกครั้งก่อนอ่านไฟล์

### Rule #7: ต้องรัน validation หลังแก้ code ทุกครั้ง (MANDATORY)
- **ทุกครั้ง** ที่แก้โค้ดเสร็จ ต้องรัน **ครบทั้ง 5** ก่อนบอก user ว่าเสร็จ:
  1. `uv sync` — sync dependencies
  2. `ruff check .` + `ruff format .` — lint + format
  3. `mypy src tests` — type check
  4. `pytest` — run all tests
  5. `pre-commit run --all-files` — pre-commit hooks
- ห้ามข้าม ห้ามลืม ห้ามรัน partial
- ถ้า venv มีปัญหา (hdfs, VIRTUAL_ENV) → ใช้ `.venv/bin/ruff`, `.venv/bin/mypy`, `.venv/bin/pytest` ตรง
- (CI YAML ไม่ต้องรัน Python tools แต่ pre-commit อาจ check YAML)

---

## Mistakes Log (2026-02-19): BLMS Stale Entry Fix

### Mistake 1: อ่าน code ผิด directory
- ❌ อ่าน `loyalty/loyalty-data/` (Hadoop) → เสีย context ทั้ง session แรก
- ✅ ต้องอ่าน `loyalty/loyalty_paralel/loyalty-data/` (BLMS REST)
- **เหตุ**: ไม่ตรวจ path ก่อนอ่าน

### Mistake 2: บอก messaging path ผิด
- ❌ พูดว่า messaging data อยู่ที่ `gs://bucket/source/messages/`
- ✅ จริงๆ อยู่ที่ `gs://bucket/messages/` (flat, ไม่มี source/)
- **เหตุ**: ไม่ได้อ่าน `get_table_location()` ทั้งๆ ที่ return `gs://{catalog_name}/{table_name}`

### Mistake 3: บอกว่า table_properties.location ไม่ work
- ❌ สรุปว่า IcebergIO default ไป namespace path เสมอ
- ✅ `table_properties.location` OVERRIDE ได้ — messaging พิสูจน์แล้ว
- **เหตุ**: เชื่อ comment ใน deploy.py แทนที่จะ verify จาก working code (messaging)

### Mistake 4: เพิ่ม --enable-biglake-catalog แล้ว revert
- เพิ่ม flag → user ถามว่าจะลบ refined table มั้ย → วิเคราะห์ใหม่ → revert ทั้ง 6 จุด
- **เหตุ**: ไม่เข้าใจ root cause จริงก่อนแก้

### Mistake 5: แก้ deploy.py function ที่เป็น dead code
- แก้ `register_table_in_biglake_catalog` ให้ drop+re-register
- function ไม่เคยถูกเรียก (ไม่มี `--enable-biglake-catalog` flag)
- **เหตุ**: แก้โดยไม่คิดว่า function ถูกเรียกเมื่อไหร่

### Mistake 6: ไม่แก้ production ทันที
- เพิ่ม cleanup step ใน CI → ต้องรอ deploy ถึงจะ fix
- ❌ ควรให้ manual command ให้ user run เอง fix production เดี๋ยวนี้เลย
- **เหตุ**: focus on CI changes แทน immediate fix

### Mistake 7: อธิบายยาวเกินไป
- เขียน analysis หลายหน้า, ตาราง, option 3 ตัว ก่อนแก้ code
- user ต้องการ action ไม่ใช่ lecture

---

## Root Cause ที่ถูกต้อง (VERIFIED)
- Stale BLMS entry จาก pipeline run เก่า (ก่อนมี table_properties.location)
- BLMS entry ชี้ไป `gs://bucket/source/tiers/metadata/00001-xxx.metadata.json` (namespace path)
- IcebergIO LOAD table เดิมแทน auto-create ใหม่
- Fix: ลบ stale BLMS entry → IcebergIO auto-create ด้วย table_properties.location ที่ถูกต้อง

---

## Key Facts (VERIFIED — ห้ามเดาอีก)

### IcebergIO + BLMS Behavior
- `table_properties.location` ใช้ได้แค่ตอน **CREATE** table ใหม่
- ถ้า table มีอยู่แล้วใน BLMS → IcebergIO **LOAD** เดิม ไม่ดู table_properties.location
- Messaging ไม่มี stale entry → auto-create ทุกครั้ง → ใช้ location override → data ที่ flat path

### Path Pattern (VERIFIED)
- Messaging: `gs://the1-messaging-data-source-{env}/messages/` (flat, NO source/)
- Loyalty: `gs://the1-loyalty-data-source-{env}/tiers/` (flat, NO source/) ← ควรจะเป็นแบบนี้
- Stale entry ชี้ไป: `gs://the1-loyalty-data-source-{env}/source/tiers/` ← ผิด!

### deploy.py กับ IcebergIO คนละ catalog
- deploy.py → SqlCatalog (local SQLite) → สร้าง v1.metadata.json บน GCS
- IcebergIO → BLMS REST Catalog → สร้าง 00000-uuid.metadata.json บน GCS
- คนละระบบ ไม่ conflict กัน
- deploy.py ไม่แตะ BLMS (ยกเว้นมี --enable-biglake-catalog ซึ่งเราไม่ใช้)

### Messaging vs Loyalty — writer config เหมือนกัน
- ทั้งคู่ใช้ `get_table_location()` = `gs://{catalog_name}/{table_name}` (flat)
- ทั้งคู่ใช้ BLMS REST Catalog + GoogleAuthManager + vended-credentials
- ทั้งคู่ namespace = "source"
- ข้อแตกต่างเดียว: loyalty มี stale BLMS entry, messaging ไม่มี

---

### Mistake 8: CI cleanup ทำไม่ได้ — SA IAC ไม่มี Service Usage Consumer
- ❌ Uncomment cleanup step ใน .gitlab-ci.yml ทั้ง 3 collectors
- ✅ SA ใน GitLab CI คือ SA IAC ไม่มี role Service Usage Consumer → BLMS REST API ใช้ไม่ได้
- ✅ BLMS cleanup ต้องทำใน Dataflow (workload SA มี role ที่ถูกต้อง)
- Reverted CI changes, added comments อธิบายว่าทำไมทำไม่ได้

### Mistake 9: load_table() ≠ table ไม่มี
- ❌ `load_table()` fail → สรุปว่า "not in BLMS" → ไม่ drop
- ✅ BLMS entry มีอยู่ (เห็นจาก `list_tables()`) แต่ metadata file บน GCS หาย → `load_table()` พัง
- ✅ ต้องใช้ `list_tables()` เช็คก่อนว่า entry มีจริงมั้ย ถ้ามีแต่ `load_table()` พัง = broken entry → ต้อง drop

---

## Mistakes Log (2026-02-22): Sales-Collector Managed Transform Debug

### Mistake 10: สมมติฐานผิด — "2 managed.Write ทำให้พัง"
- ❌ คิดว่า pipeline มี 2 `managed.Write(managed.ICEBERG)` ทำให้ Dataflow upgrade error
- ✅ members-collector มี **4 managed.Write** ใน pipeline เดียว ทำงานได้ปกติ
- **เหตุ**: ไม่ได้ตรวจ members-collector ก่อนสรุป

### Mistake 11: เพิ่ม partition_fields โดยไม่จำเป็น
- ❌ เพิ่ม `"partition_fields": ["etlLoadTime"]` เพราะเห็นว่า messaging มี
- ✅ members-collector + purchases-collector ไม่มี partition_fields ก็ทำงานได้
- **เหตุ**: copy จาก messaging โดยไม่ตรวจ collector อื่นที่ทำงานได้

### Mistake 12: เพิ่ม --additional-experiments โดยไม่มีหลักฐาน
- ❌ เพิ่ม `--additional-experiments "use_pipeline_version_for_managed_transforms=..."` ใน deploy_dataflow.sh
- ✅ messaging/members/purchases ไม่มี experiment flag นี้ ก็ทำงานได้ปกติ
- **เหตุ**: เชื่อ Beam GitHub issue #36340 workaround ที่ไม่เคยถูก confirm

### Mistake 13: ไม่อ่าน log ให้ละเอียด — ข้าม artifact staging error
- ❌ มุ่งแก้ pipeline code (schema, partition, experiment) โดยไม่ดู error จริงใน Dataflow log
- ✅ Error จริง: `INTERNAL: Failed to close the writer for the artifact` = GCS staging permission issue
- ✅ ไม่เกี่ยวกับ code เลย — เป็นปัญหา infra (ขาด staging/temp location)
- **เหตุ**: ไม่ขอ log จาก user ตั้งแต่แรก

### Mistake 14: pre-commit แก้ไฟล์ transactions-collector (2026-02-23)
- ❌ `pre-commit run --all-files` → ruff format แก้ trailing whitespace ใน `transactions-collector/src/domain/pipeline_config.py`
- ✅ transactions-collector ไม่ใช่ของเรา — **ต้อง revert ทุกครั้ง** หลังรัน pre-commit
- ✅ `git checkout -- transactions-collector/` หลัง pre-commit เสมอ
- **เหตุ**: pre-commit scope ครอบคลุม monorepo ทั้งหมด ไม่จำกัดแค่ collector ของเรา

### Root Cause ที่ถูกต้อง (VERIFIED 2026-02-22)
**ปัญหา:** sales-collector deploy ไม่มี `--staging-location` + `--temp-location`
- Dataflow managed transform ต้อง stage Java jars (เช่น `avro.jar`) ไปยัง GCS
- ถ้าไม่กำหนด → ใช้ default bucket `gs://dataflow-staging-{region}-{project_number}/`
- SA ไม่มีสิทธิ์เขียน default bucket → `Failed to close the writer for the artifact`
- loyalty collectors (members/tiers/m-t-h) กำหนด staging/temp location ไว้ → ทำงานได้

**Fix:** เพิ่ม `--staging-location` + `--temp-location` ใน:
- `scripts/deploy_dataflow.sh` — รับ args + ส่งให้ `gcloud dataflow flex-template run`
- `.gitlab-ci.yml` deploy:stg — `gs://the1-sales-data-source-stg/dataflow/staging`
- `.gitlab-ci.yml` deploy:prod — `gs://the1-sales-data-source-prod/dataflow/staging`
- ใช้ source bucket เพราะ SA มี `objectAdmin` จาก terraform

---

## Mistakes Log (2026-03-09): Sales-Collector CDC Write Fix

### Mistake 15: Timestamp strftime มี Z suffix → BQ DATETIME reject
- **Bug**: `_WrapCdcRowDoFn` ใช้ `strftime("%Y-%m-%dT%H:%M:%SZ")` — Z suffix = timezone indicator
- **BQ DATETIME** = timezone-naive → ไม่รับ Z → Storage Write API reject ทุก row
- **BQ TIMESTAMP** = timezone-aware → รับ Z ได้ (ทำไม members-collector ทำงานได้)
- **Masked by**: Beam 2.70.0 bug ใน `TableRowToStorageApiProto.java:593` — `_change_type` pseudo-column ไม่อยู่ใน `SchemaInformation` → crash ตอน parse response → เห็นแค่ `Schema field not found: _change_type` (69,356 errors) mask error จริงหมด
- **Fix**: ลบ Z → `strftime("%Y-%m-%dT%H:%M:%S")`
- **Root cause**: Members-collector ใช้ TIMESTAMP columns (Z valid), sales ใช้ DATETIME columns (Z invalid) — code เดียวกัน แต่ schema ต่างกัน
- **Lesson**: เมื่อ cross-language CDC (Python→Java) + BQ Storage Write API, format ของ string value ต้องตรงกับ BQ column type: DATETIME ห้ามมี timezone, TIMESTAMP ต้องมี/ไม่มีก็ได้
- **Also applies to**: insight/customer-profile-pipeline (same pattern)

---

## Changes Made (2026-02-19 session) — Final State

| File | Change | Status |
|------|--------|--------|
| `tiers-collector/src/main.py` | `_cleanup_all_blms_entries()` — hardcode drop ทุก table, call site commented out | READY (uncomment to run) |
| `members-collector/src/main.py` | Removed `_cleanup_stale_blms_entries()` + call site | CLEAN |
| `members-tiers-history-collector/src/main.py` | Removed `_cleanup_stale_blms_entry()` + call site | CLEAN |
| `scripts/cleanup_blms_tables.py` | Manual utility script | KEPT |
| `docs/iceberg/BLMS_STALE_ENTRY_FIX.md` | Full documentation | ACTIVE |
| `memory/mistakes_and_rules.md` | This file | ACTIVE |
