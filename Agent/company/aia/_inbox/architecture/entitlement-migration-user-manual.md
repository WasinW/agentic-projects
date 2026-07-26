# Entitlement Migration — User Manual (จับมือทำ)

> เรื่อง: การเปิดโหมด "default entitlement ใหม่" ของ `users` system group บน Azure Databricks
> (ที่ทำให้ Consumer-access lockdown ทำงานจริง). **verified 2026-07-26** กับ MS Learn
> `system-group-entitlements-migration`. 🔒 private KB. คู่กับ `grafana-alert-user-manual.md`.

---

## 0. เข้าใจภาพรวมก่อน (อ่าน 1 นาที — กัน confuse)

### มันมี "toggle ตัวเดียว" — ไม่ใช่หลาย step
มี setting ตัวเดียวที่ระดับ workspace ("Choose entitlements when adding principals"). "migrate", "auto",
"enforced" = **สถานะ/วิธีที่ toggle ตัวเดียวกันนี้ถูกเปิด** ไม่ใช่คนละงาน:

| คำ | คืออะไร |
|---|---|
| **opt-in / migrate** | **คุณกด toggle เอง** (ได้ตั้งแต่ 2026-06-15) |
| **auto-enable (2026-07-27)** | **Databricks กด toggle ตัวเดียวกันให้** ถ้าคุณยังไม่กด |
| **enforced (2026-09-14)** | toggle ล็อคเปิดถาวร (revert ไม่ได้แล้ว) |

→ **opt-in = auto = "กด toggle เดียวกัน" ต่างแค่ใครกด. ผลลัพธ์เหมือนกันเป๊ะ**

### toggle นี้ (ไม่ว่าใครกด) ทำ 2 อย่างอัตโนมัติ
1. **user/group ที่ add ใหม่ "หลัง" กด → default = none** (ต้อง grant สิทธิ์ให้เอง = ที่เราต้องการ)
2. **ของเดิม (มีก่อนกด) → ย้ายไป `users-clone-<TS>` ที่เก็บสิทธิ์เก่าไว้** → **ไม่พัง ไม่มีใครเสีย access**

### ⭐ แยกให้ชัด: "กด toggle" ≠ "งาน clean สิทธิ์"
- **กด toggle** = แค่เปิดโหมด (คำว่า migrate/auto หมายถึงอันนี้)
- **clean ของเก่า + grant ของใหม่** = **งานคนละอัน** (audit / entitlement work = Access Mgmt layer 1.2) —
  ทำต่อจากนั้น, ทำเป็น **code ได้** (ไม่ต้องนั่งกดมือ)
> (ก่อนหน้านี้เอกสารเรียก 2 อันนี้ปนกันจนงง — จำแค่ "กด toggle = เปิดโหมด" กับ "clean = งานต่างหาก")

---

## 1. ต้องแคร์ deadline มั้ย? → **ไม่ต้อง**
- toggle จะ **auto-flip เองวันที่ 27 ก.ค.** (คุณ "พลาด" ไม่ได้ มันเกิดแน่)
- **14 ก.ย.** แค่ทำให้ **revert ไม่ได้** (ซึ่งเราก็ไม่อยาก revert อยู่แล้ว)
- **งาน clean ของเก่า = ไม่มี hard deadline** แต่ต้องทำ ไม่งั้น lockdown ไม่เป็นจริง

---

## 2. คุณมี 2 ทางเลือก (ผลเหมือนกัน — เลือกตามสะดวก)

| | A) opt-in เอง (กดก่อน 27 ก.ค.) | B) ปล่อย auto (27 ก.ค.) |
|---|---|---|
| ใครกด toggle | คุณ | Databricks |
| คุมชื่อ clone group + timing | ได้ | ไม่ได้ (auto-timestamp) |
| ของใหม่ default none | ✅ | ✅ |
| ของเก่า preserve (ไม่พัง) | ✅ | ✅ |
| **ต้อง clean ของเก่าเอง** | ✅ (เชิงรุก) | ✅ (เชิงรับ) |

→ **ทั้ง 2 ทาง สุดท้ายต้อง clean ของเก่าเองเหมือนกัน** (toggle ไม่ล้างส่วนเกินให้). แนะนำ A ถ้าอยากคุม

---

## PART A — (ถ้าเลือก opt-in เอง) กด toggle

> ต้องเป็น **workspace admin**. ถ้าปล่อย auto ข้าม PART นี้ไปได้เลย

### A.1 Pre-work ก่อนกด (สำคัญ — ห้ามลืม)
1. **repoint SCIM / Terraform / scripts → target "account group" ไม่ใช่ "system group"**
   - หลังกด: เขียน entitlement ลง `users`/`admins` จะ **FAIL** → เช็ค `dtp_framework_aiath` (`api_assign_permission`), TF, SCIM
2. **un-nest**: ถ้า `users`/`admins` ถูก nest เป็น member ของ group อื่น → เอาออก
3. **SCIM preserve clone group**: ถ้า SCIM ลบ group ที่ไม่รู้จัก → แก้ให้เก็บ `users-clone-<TS>` (ถ้าโดนลบ = user เสีย entitlement)

### A.2 กด toggle (UI)
1. **workspace** → **Settings** → tab **Advanced** → **Access control**
2. **"New behavior: Choose entitlements when adding principals to workspaces"** → **Manage**
3. เลือก **Use new behavior** → **ตั้งชื่อ clone group** → **Save**

---

## PART B — Clean ของเก่า + grant ของใหม่ (ต้องทำ "ทั้ง 2 case")

### B.1 Audit + prune ของเก่า (ตัวที่ "ปิด lockdown จริง")
เช็ค/แก้ 4 อย่าง:
- [ ] `users` group = **ไม่มี entitlement**
- [ ] `admins` group = มีครบ (ปกติ)
- [ ] ⭐ **`biz-consumers-*` (consumer group) ต้อง NOT อยู่ใน `users-clone-<TS>`** — ถ้าเจอ = **เอาออก** (ไม่งั้นยังมี Workspace+SQL ติดอยู่ = lockdown รั่ว)
- [ ] consumer แต่ละกลุ่มมี entitlement เดียว = **`workspace-consume`**

### B.2 Grant ของใหม่ (default none → เปิดเท่าที่จำเป็น)
- group ที่ add หลังกด toggle เริ่มที่ศูนย์ → เปิดสิทธิ์ตามตาราง Concept ข้างล่าง

---

## Concept — นี่คือ Access Mgmt layer 1.2 (โมเดล "default none → grant explicit" ของคุณ)

**กด toggle = ครั้งเดียว. การกำหนดสิทธิ์ต่อ group = งาน ongoing ทำเป็น code**
(TF `databricks_entitlements` / reconcile — วางไว้ที่ `deploy/terraform/l2_entitlements.tf`):

| Group (account group) | เปิด entitlement ให้ | หมายเหตุ |
|---|---|---|
| `users` (system) | **none** | หลังกด toggle = default ศูนย์จริง (เปลี่ยนไม่ได้) |
| `admins` (system) | all | ปกติ |
| `consumer-<team>` | **workspace-consume เท่านั้น** | business user → Genie/AI-BI only, ตั้ง job ไม่ได้ |
| `power-<team>` | databricks-sql-access | ทีมใช้ SQL (เป็น **SWAP** กับ consume ไม่ใช่เพิ่ม) |
| `de-<team>` | workspace-access (+ cluster-create) | data engineer |

→ pattern = **least privilege** (ทุก group เริ่มศูนย์ เปิดเท่าที่จำเป็น). toggle ทำให้ "ศูนย์" เป็น default จริง;
เปิดสิทธิ์ต่อ group = automate ผ่าน TF/reconcile ได้

---

## Rollback (ถ้ามีอะไรพัง)
- **opt out ได้ถึง 2026-09-14** — `users-clone-<TS>` ยังอยู่ (เก็บ/จัดการ/ลบเองได้)
- หลัง **2026-09-14** = enforced ถาวร, opt-out หาย (revert ไม่ได้)

---

## สรุป action (ย่อ)
1. **ไม่ต้องแคร์ deadline** — toggle auto-flip 27 ก.ค. เอง; 14 ก.ย. แค่ห้าม revert
2. **เลือก**: กด toggle เอง (opt-in, คุมได้) หรือปล่อย auto — ผลเหมือนกัน
3. **Pre-work** (ถ้า opt-in): เช็ค SCIM/TF/`dtp_framework_aiath` เขียน entitlement ลง **account group** ไม่ใช่ system group
4. **Clean ของเก่า** (ทั้ง 2 case): `biz-consumers-*` ออกจาก clone group + consumer เหลือ `workspace-consume`
5. **Grant ของใหม่**: default none → เปิดตามตาราง (ทำเป็น code = layer 1.2)
