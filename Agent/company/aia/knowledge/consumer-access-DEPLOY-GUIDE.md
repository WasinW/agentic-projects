# Consumer Access — Deploy Guide (จับมือทำ, สำหรับ environment ที่มีอยู่แล้ว)

> **สำหรับ:** สิน — เอาไป setup + อธิบายทีม + deploy จริง บน departmental workspace ที่**มีอยู่แล้ว**
> **คู่กับ:** `consumer-access-user-manual.md` (ฉบับ reference เต็ม + doc URL ทุกจุด) · `databricks-genie-governance` (skill)
> **สถานะ verify:** UI click-path + entitlement name = verified กับ Microsoft Learn สด (2026-07-18). `[C]`=confirmed-doc · `[I]`=inference · ⚠️=ยัง confirm label ใน tenant
> **หลักคิด:** environment คุณมีของเยอะแล้ว — guide นี้บอกว่า **อันไหน reuse ได้ อันไหนต้องทำจริง**

---

## PART 0 — อ่านก่อน: 5 เรื่องที่คนเข้าใจผิดบ่อยสุด

### ❶ "migrate workspace" = กด toggle setting ตัวเดียว — **ไม่ใช่สร้าง Databricks ใหม่**
```
❌ ไม่ใช่:  สร้าง workspace ใหม่ / ย้าย data / rebuild อะไรเลย
✅ ใช่:     flip switch ตัวเดียว บน workspace เดิม
```
มันเปลี่ยนแค่ **"พฤติกรรมการแจก entitlement"** ของ workspace เดิม:
| | `users` group แถมสิทธิ์อัตโนมัติ? | ผลกับ Consumer access |
|---|---|---|
| **ก่อน migrate** | แถม Workspace + SQL access ให้ทุกคน | Consumer access inherit สิทธิ์ author → **บล็อก job ไม่อยู่** 🚨 |
| **หลัง migrate** | ไม่แถมอะไร | เลือก entitlement เองทีละ group ได้สะอาด ✅ |

- **ทำที่ไหน:** Settings → **Advanced** → Access control → *"New behavior: Choose entitlements when adding principals to workspaces"* → **Manage** → Use new behavior → Save
- **ใครทำ:** **workspace admin** ของ departmental workspace (ถ้าไม่ใช่คุณ → ให้เขากด)
- **ทำครั้งเดียว** มีผลทั้ง workspace

### ❷ ไม่ต้องสร้าง account group ใหม่ ถ้ามีอยู่แล้ว
- group ทีมคุณเป็น **account group** (sync จาก Entra) อยู่แล้ว → **ใช้เลย ข้าม step สร้าง group**
- เช็ค: `SELECT is_account_group_member('ชื่อ-group-เดิม');` → `true` = account group จริง ใช้ได้
- ⚠️ เงื่อนไขเดียว: group เดิม**ต้องไม่มี entitlement อื่นติดอยู่** (additivity — ถ้ามี SQL/Workspace access ปน Consumer จะพัง)

### ❸ warehouse ใช้ตัวเดิม/ตัวเดียวร่วมกันได้
- **RLS (เห็น row ทีมไหน) คุมที่ UC (step 4) ไม่ใช่ที่ warehouse** → share warehouse ข้อมูลไม่ปน
- Genie แค่ต้องมี warehouse "สักตัว" ที่ group มี **CAN USE**
- **1 warehouse/ทีม เป็น optional** — ทำเฉพาะถ้าอยาก (ก) chargeback ต่อทีม (ข) คุม cost/auto-stop ต่อทีม
- → มี serverless warehouse อยู่แล้ว + ไม่ซีเรียส per-team chargeback = **ใช้ตัวเดิมร่วมกันได้เลย**

### ❹ step "UC grant" = อันเดียวกับ Topic 1 ที่คุยกันแต่แรก
grant ให้ group เห็น table + row filter เห็นเฉพาะ row ทีมตัวเอง — **mechanic เดียวกับ dashboard sharing เป๊ะ**

### ❺ 🚨 "อย่าใช้ Share data permissions" คนละเรื่องกับ UC grant (Databricks ตั้งชื่อชนกันเอง)
```
UC grant (step 4)        = "แชร์ TABLE" → คุมว่าเห็น ROW ไหน       (สิทธิ์ระดับ data)
"Share data permissions" = โหมด PUBLISH dashboard → query รันในนามใคร  (คนละ setting!)
```
| โหมด publish dashboard | query รันในนาม | ผล |
|---|---|---|
| **"Share data permissions"** (default) | publisher (คุณ) | RLS เป็นคุณ → **ทุกคนเห็นทุกแถว** 🚨 |
| **"Individual data permissions"** | ผู้ชม | RLS ต่อคน → เห็นเฉพาะทีมตัวเอง ✅ |
→ ใช้เฉพาะถ้ามี **dashboard** · ทีมที่ใช้แค่ Genie One = ข้ามได้

---

## PART 1 — สรุป: environment เดิม เหลือทำอะไรจริงๆ

```
① migrate (toggle บน ws เดิม)          ← ต้องทำ · ครั้งเดียว · workspace admin
② assign entitlement ให้ group เดิม      ← ต้องทำ · Consumer access เดียว (reuse group ได้)
③ ให้ group CAN USE warehouse (ตัวเดิม)  ← reuse ได้ ถ้ามี serverless warehouse
④ UC grant + row filter (= Topic 1)     ← ต้องทำ (ถ้ายังไม่ได้ grant)
⑤ publish dashboard โหมด Individual     ← เฉพาะถ้ามี dashboard
⑥ Genie budget (คุมปริมาณ)              ← ต้องทำ ถ้าอยากคุม Genie spend
```
> **ของที่ "ต้องทำจริง" = ① migrate · ② entitlement · ④ grant · ⑥ budget** · ที่เหลือ reuse

---

## PART 2 — HAND-HOLDING STEP-BY-STEP (คลิกตามได้เลย)

> ทำทีละทีม ตัวอย่าง `<team>=claims`. **ทำ STEP 0 ให้เสร็จก่อนเสมอ.**

### ▶ STEP 0 — migrate workspace (workspace admin, ครั้งเดียวทั้ง ws) `[C]`
```
1. คลิกชื่อ user มุมขวาบน → Settings
2. แท็บ Advanced
3. หาหัวข้อ Access control →
   "New behavior: Choose entitlements when adding principals to workspaces"
   (สถานะจะขึ้น "Legacy behavior (action might be needed)")
4. คลิก Manage
5. ใน dialog → Behavior for this workspace → เลือก "Use new behavior"
6. Clone group name → ใช้ default users-clone-<TIMESTAMP> ได้
7. Save
```
**⚠️ pre-work ก่อนกด (สำคัญ) `[C]`:**
- repoint SCIM/Terraform → เขียน **account group** (หลัง migrate เขียน system group จะ fail)
- ตั้ง SCIM ให้ **เก็บ** clone group (ไม่งั้นคนที่ inherit ผ่าน clone หลุด access)

**หลัง migrate — audit (จุดที่คนพลาด) `[C]`:**
```
Settings → Identity and access → Groups → Manage → เปิด users-clone-<TS>
□ ยืนยัน: users = ไม่มี entitlement · admins = ครบ · clone = สิทธิ์กว้างเดิม
□ 🚨 ยืนยัน group ทีม (biz-consumers-*) NOT เป็นสมาชิก clone group
   (ถ้า group ถูก assign เข้า ws ก่อน migrate มันจะหลุดเข้า clone = ได้สิทธิ์ author กลับมา
    → assign group "หลัง" migrate หรือลบออกจาก clone ทันที)
```

### ▶ STEP 1 — group (reuse ถ้ามี) `[C]`
```
มี account group ทีมอยู่แล้ว?
  ✅ มี  → เช็ค SELECT is_account_group_member('<group>'); = true → ข้ามไป STEP 2
  ❌ ไม่มี → Account Console → User management → Groups → Add group (sync Entra/SCIM)
           อย่าใช้ CREATE GROUP ใน SQL (ได้ workspace-local group ใช้ข้าม ws ไม่ได้)
```

### ▶ STEP 2 — assign entitlement `[C]`
```
Settings → Identity and access → ข้าง Groups คลิก Manage → เลือก group → toggle:

  Profile A — "Genie One only" (business user ทั่วไป):
     ✅ Consumer access
     ❌ Databricks SQL access · ❌ Workspace access
     ❌ Allow unrestricted cluster creation · ❌ Allow pool creation

  Profile B — "power team" (analyst ที่ต้อง author เอง แต่ยังห้าม job):
     ❌ Consumer access          ← ปิด (อยู่คู่ SQL access ไม่ได้ + จะโดน override)
     ✅ Databricks SQL access    ← ตัวนี้ให้ author dashboard/query
     ❌ Workspace access         ← ห้าม! (นี่คือตัวเปิด Jobs — เส้นห้ามข้าม)
     ❌ cluster/pool creation
```
> ⚠️ **Profile B = "สลับ" ไม่ใช่ "เพิ่ม"** — `workspace-consume` ใช้คู่ `databricks-sql-access` ไม่ได้ (Terraform reject + จะ override) `[C]`
> `[C]` ถ้า toggle **เทากดไม่ได้** = inherit จาก group อื่น/clone → แก้ที่ต้นทาง (สัญญาณ STEP 0 ยังไม่เรียบร้อย)

### ▶ STEP 3 — warehouse (reuse ตัวเดิมได้) `[C/I]`
```
มี serverless SQL warehouse อยู่แล้ว?
  ✅ ใช้ตัวเดิม → แค่ให้สิทธิ์: เปิด warehouse → Permissions → เพิ่ม group = CAN USE (ไม่ใช่ CAN MANAGE)
  ❌ สร้างใหม่ (ถ้าอยาก per-team): SQL → SQL Warehouses → Create → Type: Serverless
       · Auto stop 5-10 นาที · scaling จำกัด (max 1-2) · Advanced→Tags: team=claims
       · Permissions: group = CAN USE
```
> `[C]` consumer access user **มองไม่เห็น warehouse/Query History อยู่แล้ว** — CAN USE แค่ให้ Genie/BI รันเบื้องหลัง

### ▶ STEP 4 — UC grant = รั้วจริง (= Topic 1) `[C]`
```sql
GRANT USE CATALOG  ON CATALOG  <cat>                    TO `biz-consumers-claims`;
GRANT USE SCHEMA   ON SCHEMA   <cat>.gold               TO `biz-consumers-claims`;
GRANT SELECT       ON TABLE    <cat>.gold.cost_by_team  TO `biz-consumers-claims`;
GRANT EXECUTE      ON FUNCTION <cat>.gold.fn_team_rls   TO `biz-consumers-claims`;  -- ⭐ ห้ามลืม
-- row filter ใช้ is_account_group_member('client-claims') ไม่ใช่ is_member()
-- ❌ อย่า grant ทั้ง catalog/schema อื่น — Genie จะ reach ได้หมด (Genie ไม่ใช่รั้ว, UC คือรั้ว)
```

### ▶ STEP 5 — dashboard publish (เฉพาะถ้ามี dashboard) `[C]`
```
บน dashboard → Share → เพิ่ม group → Can view
ตอน Publish → เลือก ✅ "Individual data permissions"  (❌ ไม่ใช่ "Share data permissions" default)
```

### ▶ STEP 6 — Genie budget = คุมปริมาณ Genie ต่อทีม `[C]`
```
Account Console (accounts.azuredatabricks.net) → Usage → Budgets → Create budget
  · Name: genie-claims
  · Workspaces: <ws>
  · Resource types: Unity AI Gateway          ← ต้องเลือกตัวนี้
  · Resource tags → Key: databricks-product  Value: genie   (ใส่ tag นี้ตัวเดียว!)
  · Shared threshold: $5,000 → ☑ Send alert
  · Per-user threshold: $30 → ☑ Block usage    ← hard cap ต่อคน (Genie เท่านั้นที่ block ได้)
  · Per-user override: บางทีม/คน $200          ← "ได้มากกว่าแต่คุมได้"
  · Create
```
> resolution: ใน budget เดียว group permissive สุดชนะ · ข้าม budget restrictive สุดชนะ → "ให้มากกว่า" = ใช้ **override** ใน budget เดียวกัน
> ⚠️ warehouse/classic **block ไม่ได้** (alert only) → cap ที่ auto-stop + scaling (STEP 3)

### ▶ hardening (ปิดประตูหลัง) ⚠️
```
□ ปิด dashboard email subscriptions  (Settings → Notifications area)   [⚠️ verify label ใน tenant]
□ ปิด SQL results download           (Settings → Security area)        [⚠️ verify label ใน tenant]
□ เช็ค group ไม่มี PAT สิทธิ์สูง / ไม่มี SP ปน
```

---

## PART 3 — DEPLOYMENT GUIDELINE

### ลำดับ deploy (order สำคัญ)
| # | ทำ | ใคร | scope | reversible? |
|---|---|---|---|---|
| 1 | **STEP 0 migrate** (+ audit clone) | workspace admin | ทั้ง workspace | ⚠️ ยาก — plan ก่อน |
| 2 | **pilot 1 ทีมก่อน** (Profile A) | Sin + admin | 1 group | ง่าย (ถอน entitlement/grant ได้) |
| 3 | **verify pilot** (PART 4) | Sin | 1 test user | — |
| 4 | **replicate ทีมที่เหลือ** | Sin | ทีละ group | ง่าย |
| 5 | **budget + hardening** | account/workspace admin | workspace | ง่าย |

### หลัก deploy
- **migrate ก่อนเสมอ** (STEP 0) — ถ้าไม่ migrate lockdown ทั้งหมดพังเงียบ · migrate **ก่อน** assign group เข้า ws (กัน clone-group trap)
- **pilot 1 ทีม** (เช่น claims) ให้ผ่าน verify ก่อน แล้วค่อย replicate — อย่า roll ทุกทีมพร้อมกัน
- **timing:** entitlement migration บังคับ **2026-09-14** (auto 07-27) → ทำ STEP 0 ก่อนเส้นนี้ `[C]`
- **coordinate:** migration = workspace admin ทำ → ถ้า Sin ไม่ owner departmental ws → นัด admin
- **rollback:** entitlement/grant ถอนได้ต่อ group · แต่ **STEP 0 migrate ถอนยาก** (opt-out ได้จนถึง 09-14 เท่านั้น) → ทดสอบใน non-prod ws ก่อนถ้ามี
- **as-code (แนะนำ):** entitlement + grant เก็บใน Terraform/Git → repeatable ต่อทีม + audit trail (ตัวอย่าง TF ใน `consumer-access-user-manual.md`)

---

## PART 4 — VERIFY (login test ก่อนส่งมอบ)

### Profile A (Consumer only)
```
□ login test user → เด้งเข้า Genie One (ไม่ใช่ full workspace)
□ หา Create job / notebook / cluster → ไม่มี surface เลย
□ เปิด SQL editor → ไม่มีสิทธิ์
□ ถาม Genie เรื่อง cost ทีมตัวเอง → เห็นเฉพาะ row ทีมตัวเอง (RLS)
□ prompt Genie ให้ query table ทีมอื่น → empty/no access (UC เป็นรั้ว)
□ Genie budget: ใช้เกิน per-user threshold → โดน Block
```
### Profile B (SQL access)
```
□ login → เข้า DBSQL surface (ไม่ redirect Genie One)
□ author dashboard/SQL editor → ทำได้
□ Create job/notebook/cluster → ยังไม่มี surface  ← เส้นห้ามข้าม
```

---

## PART 5 — FLAGS (พูดกับทีมตรงๆ)
1. ⚠️ **2 label ยัง confirm ไม่ 100%:** `dashboard email subscriptions` + `SQL results download` (hardening) — เป็น setting จริงแต่ยังไม่ได้ fetch หน้านั้น → confirm ใน tenant ก่อน
2. `[C]` **Genie ≠ security boundary — UC คือรั้ว** → scope grant แคบ (STEP 4)
3. `[C]` **budget block ได้เฉพาะ Genie LLM** — warehouse/classic = alert only
4. `[C]` **additivity + migration = จุดพังเงียบสุด** → STEP 0 + audit clone group
5. `[I]` **free ~150 LLM DBU/user** เลขจาก pricing page ไม่ใช่ Learn → verify ตาม region · SP ไม่มี free tier
6. `[C]` **RLS สำหรับ bare account user = doc ขัดกัน → test** — แต่ moot (user เราถือ Consumer/SQL access อยู่แล้ว)

---
**Reference เต็ม + doc URL ทุกจุด:** `consumer-access-user-manual.md` · **skill:** `databricks-genie-governance`
