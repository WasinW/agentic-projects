Verification complete. The deliverable is unusually accurate — nearly every quote, date, API name, and UI path matches the live Microsoft Learn docs verbatim. I found **one runnable bug** (Profile B Terraform + framing) and **one precision overstatement** (budget-block scope), plus a minor naming note. Here is the corrected deliverable.

---

# Consumer Access — User Manual: per-team access control ใน departmental workspace

> **Deliverable 2** · Azure Databricks · UI-first runbook สำหรับสิน (setup + explain)
> **Verified against Microsoft Learn** (docs `ms.date` 2026-07-08 ถึง 2026-07-15, ดึงสด 2026-07-18) + **Databricks Terraform provider docs**. Passed adversarial review (3 corrections applied — ดู changelog ท้ายไฟล์). `[C]` = confirmed-from-docs · `[I]` = inference · ⚠️ Preview / doc-contested flagged inline.
> **Placeholders** (generic template — no AIA internals): `<ws>` departmental workspace · `<cat>` catalog · `<team>` เช่น `claims` · `<wh_id>` serverless SQL warehouse · `biz-consumers-<team>` account group (Profile A) · `biz-power-<team>` account group (Profile B).
> **Mental model:** 3 gate อิสระ 3 กลไก — **Entitlement** = เข้า *surface* ไหน · **UC grant** = เห็น *data* ไหน · **Budget** = ใช้ได้ *เท่าไหร่*. อย่าเอามาปนกัน.

---

## 1. THE TIER MODEL — entitlement → "ทีมนี้ทำอะไรได้"

มี **entitlement การเข้าถึงแค่ 3 ตัว** (assign ที่ **workspace level**, ต้อง Premium plan) + compute entitlement อีก 2 ตัว. `[C]` [Manage entitlements](https://learn.microsoft.com/en-us/azure/databricks/security/auth/entitlements)

| ทีมทำอะไรได้ | **Consumer access**<br>`workspace-consume` | **Databricks SQL access**<br>`databricks-sql-access` | **Workspace access**<br>`workspace-access` |
|---|:--:|:--:|:--:|
| ดู/รัน dashboard · Genie Agent · Apps ที่ share มา | ✓ | ✓ | ✓ |
| **เด้งเข้า Genie One** ตอนล็อกอิน (แทน full workspace) | ✓ *(เฉพาะเมื่อเป็น entitlement เดียว)* | — | — |
| query warehouse ผ่าน BI tool (Power BI/Tableau) | ✓ | ✓ | |
| **author** dashboard / Genie Agent / เปิด **SQL editor** / ad-hoc SQL | | ✓ | |
| **สร้าง notebook / JOB / pipeline / model** (DS&E object) | | | ✓ |
| ดู warehouse list / **Query History** | ❌ *(แม้ได้ permission แล้ว)* `[C]` | ✓ | ✓ |

**Compute entitlement (2 ตัว, non-admin ไม่ได้ default):** `[C]`
- **Allow unrestricted cluster creation** (`allow-cluster-create`)
- **Allow pool creation** (`allow-instance-pool-create`) ← label คือ "Allow pool creation" ไม่ใช่ "unrestricted pool"

**หลักตัดสิน tier ต่อทีม (สิน read ตารางนี้แล้วเลือก):**
- อยากให้ **"ใช้แค่ Genie/AI-BI, ตั้ง job ไม่ได้"** → **Consumer access อย่างเดียว**. `[C]` doc: *"When users with consumer access sign in, they are directed to Genie One instead of the standard workspace… Users with only consumer access cannot create new objects in the workspace."*
- อยากให้ทีมนั้น **author dashboard/query เองได้** แต่ยัง **ห้ามสร้าง job/cluster** → ให้ **Databricks SQL access** (ไม่ให้ Workspace access). ⚠️ **นี่คือการ "สลับ" tier ไม่ใช่ "เพิ่มทับ"** — `databricks-sql-access` อยู่คู่กับ `workspace-consume` **ไม่ได้** (ดู §2 Profile B + note ด้านล่าง). Job/cluster ยังบล็อกอยู่เพราะไม่มี `workspace-access`.
- **Job creation อยู่หลัง `workspace-access` เท่านั้น** → ไม่ให้ตัวนี้ = ไม่มี Jobs surface เลย. `[C]` *"Grants access to core workspace features such as notebooks, jobs, models, and pipelines."*

> 🔑 **หัวใจของ per-team control:** entitlement **additive** — Consumer access จะ restrictive จริง **ก็ต่อเมื่อเป็น entitlement เดียวของ user**. เพิ่มตัวที่ 2 (SQL/Workspace access) = *"overrides the simplified consumer experience"* `[C]` → **consumer/Genie-One experience หายทันที** (ผู้ใช้ไปโผล่ surface DBSQL/full แทน). นี่คือกับดักที่ทำ lockdown พังเงียบ (§5) — และคือเหตุผลว่าทำไม Profile B ไม่ใช่ "consumer + X" แต่เป็น "X แทน consumer".

---

## 2. TWO TEAM PROFILES — grade แต่ละทีมให้พอดี "ที่จำเป็น"

### Profile A — **"Genie One only" team** (ส่วนใหญ่จะเป็นแบบนี้)
Business user ทั่วไป: consume dashboard + ถาม Genie เรื่อง cost ทีมตัวเอง. **ห้าม** author, ห้าม job.

| ตั้งอะไร | ค่า |
|---|---|
| Entitlement | **Consumer access เท่านั้น** (`workspace-consume`) — ไม่ให้ตัวอื่นเลย |
| Warehouse | serverless SQL warehouse ต่อทีม, group = **CAN USE** |
| UC grant | SELECT เฉพาะ gold view ของทีม + EXECUTE row-filter fn |
| Genie budget | per-user threshold + **Block usage** (hard cap) |
| ผลลัพธ์ user เห็น | เด้งเข้า **Genie One**, ไม่มี Jobs/notebook/SQL-editor surface, เห็นเฉพาะ row ทีมตัวเอง |

### Profile B — **"Power" team** (ได้มากกว่า แต่ยัง controlled)
บางทีมอยาก **สร้าง dashboard / query เองได้** (เช่น analyst) — ให้ **Databricks SQL access** แต่ยังบล็อก job/cluster.

| ตั้งอะไร | ค่า | ทำไมยังคุมได้ |
|---|---|---|
| Entitlement | **Databricks SQL access** (`databricks-sql-access`) — **Consumer access ปิด** | SQL access เป็น superset ของ consume-capabilities (ยังเห็น/รัน dashboard·Genie Agent·App ที่ share ได้ `[C]`) **บวก** author DBSQL — ไม่แตะ `workspace-access` |
| ❌ ยังห้าม | Consumer access (อยู่คู่ SQL access ไม่ได้ + จะโดน override อยู่ดี) · Workspace access · Allow unrestricted cluster creation · Allow pool creation | **ไม่มี Jobs/notebook/pipeline/cluster surface เลย** `[C]` |
| Warehouse | warehouse ต่อทีม, **CAN USE** (ไม่ใช่ CAN MANAGE) — สร้าง/แก้ warehouse เองไม่ได้ |
| UC grant | SELECT เฉพาะ schema ที่ทีมนั้นควรเห็น (ยัง scope แคบ) |
| Genie budget | per-user threshold สูงกว่า (ผ่าน **override** ต่อ group) |

> ⚠️ **Profile B ไม่ได้ "เด้งเข้า Genie One"** — SQL-access user จะเข้า DBSQL surface (มี SQL editor / dashboard authoring). แต่ **สร้าง job/notebook/cluster ไม่ได้** เพราะนั่นอยู่หลัง `workspace-access` ล้วนๆ. เส้นที่ห้ามข้ามคือ **Workspace access** — ข้ามเมื่อไหร่ = ให้สิทธิ์สร้าง job ทันที. "Power" แปลว่า "author dashboard/query" ไม่ใช่ "author job".
>
> 🔧 **ทำไมต้อง "สลับ" ไม่ใช่ "เพิ่ม":** `workspace_consume` **ใช้ร่วมกับ `databricks_sql_access` (หรือ `workspace_access`) ไม่ได้** — Terraform provider reject ตรงๆ (*"Couldn't be used with `workspace_access` or `databricks_sql_access`"* `[C]`), และต่อให้ toggle ทั้งสองใน UI ได้, doc additivity ก็บอกว่า SQL access จะ **override** consumer experience อยู่ดี → consumer เป็น entitlement ที่ตายซาก. ดังนั้น Profile B = **SQL access แทน consumer**.

---

## 3. STEP-BY-STEP SETUP ต่อทีม (UI click-path)

> ทำทีละทีม (ตัวอย่าง `<team>=claims`). ทำซ้ำต่อทีมโดยเปลี่ยนชื่อ. **STEP 0 ต้องเสร็จก่อน — รายละเอียดใน §5.**

### ▶ STEP 0 — Prerequisite (ดู §5): workspace ต้อง **migrated** แล้ว
ถ้ายังไม่ migrate → Consumer access **ไม่ restrictive จริง** (inherit สิทธิ์ author จาก `users` group). **ทำ §5 ให้เสร็จก่อน** แล้วค่อยมา STEP 1. (Migration = **workspace admin** ทำ — สินอาจไม่ได้เป็นเจ้าของ → coordinate.)

### ▶ STEP 1 — สร้าง **account group** (Entra → SCIM)
```
□ สร้าง account-level group: biz-consumers-claims  (Profile A)  /  biz-power-claims (Profile B)
   (Account Console → User management → Groups → Add group — sync จาก Entra ID ผ่าน SCIM
    หรือ Automatic identity management)
□ ต้องเป็น ACCOUNT group ไม่ใช่ workspace-local
   ❌ อย่าใช้ CREATE GROUP ใน SQL (จะได้ workspace-local group — ใช้ข้ามไม่ได้, is_member ไม่ resolve)
```
**Verify (notebook):** `SELECT is_account_group_member('biz-consumers-claims');` → member ต้องได้ `true`.

### ▶ STEP 2 — assign entitlement `[C]` exact path
```
UI click-path (workspace admin):
□ คลิก username มุมขวาบน → Settings
□ แท็บ Identity and access
□ ข้าง Groups → คลิก Manage
□ เลือก group แล้ว toggle entitlement:

  ── Profile A (biz-consumers-claims): "Genie One only" ──
     ✅ Consumer access
     ❌ Databricks SQL access
     ❌ Workspace access
     ❌ Allow unrestricted cluster creation
     ❌ Allow pool creation

  ── Profile B (biz-power-claims): "author DBSQL, no jobs" ──
     ❌ Consumer access            ← ปิด (อยู่คู่ SQL access ไม่ได้ + จะโดน override)
     ✅ Databricks SQL access      ← ตัวนี้ให้ author dashboard/query
     ❌ Workspace access           ← ห้าม (นี่คือตัวเปิด Jobs/notebook/pipeline)
     ❌ Allow unrestricted cluster creation
     ❌ Allow pool creation
```
> `[C]` ถ้า toggle **ติ๊กแล้วเป็นสีเทากดไม่ได้** = entitlement inherit มาจาก group อื่น (เช่น clone group / `users` ก่อน migrate) → แก้ที่ group ต้นทาง ไม่ใช่ที่นี่. นี่คือสัญญาณ STEP 0 ยังไม่เรียบร้อย.

**Terraform equivalent (aside):** `[C]` `workspace_consume` ห้ามอยู่คู่ `workspace_access`/`databricks_sql_access` → แยกเป็น 2 resource คนละ group
```hcl
# Profile A — Genie One only
resource "databricks_entitlements" "biz_consumers_claims" {
  group_id          = databricks_group.biz_consumers_claims.id
  workspace_consume = true      # sole entitlement — ทุกตัวอื่น false (default). อย่า set true ตัวอื่น
}

# Profile B — power team (author DBSQL, no jobs)
resource "databricks_entitlements" "biz_power_claims" {
  group_id              = databricks_group.biz_power_claims.id
  databricks_sql_access = true  # consumer access ถูก DROP — provider ไม่ให้ set คู่กัน
  # workspace_access / allow_cluster_create / allow_instance_pool_create = false (default) → job/cluster ยังบล็อก
}
```

### ▶ STEP 3 — compute: 1 serverless SQL warehouse ต่อทีม (Genie ต้องมี warehouse ถึงตอบได้ `[C/I]`)
```
UI: SQL → SQL Warehouses → Create SQL warehouse
□ Name: wh-claims · Type: Serverless
□ Auto stop: 5–10 นาที             (cap ต้นทาง — budget block warehouse ไม่ได้, §4)
□ Cluster count / scaling: จำกัด (เช่น min 1 / max 1–2)   (cap ceiling)
□ Advanced → Tags: team = claims    (→ system.billing.usage.custom_tags → chargeback)
□ Permissions (ปุ่มขวาบนของ warehouse):
     biz-consumers-claims = CAN USE   ← ❌ ไม่ใช่ CAN MANAGE
```
> `[C]` consumer access user **มองไม่เห็น warehouse / Query History อยู่แล้ว** *"even if permissions on compute and data have been granted"* — CAN USE แค่ให้ Genie/BI รันได้เบื้องหลัง.

### ▶ STEP 4 — UC grant = **รั้วจริง** (Genie ไม่ใช่ security boundary)
```sql
-- ให้แคบที่สุด: user prompt Genie ให้ query table ไหนก็ได้ที่เขามี SELECT
-- ("users can query other tables by prompting for joins or editing SQL directly")
GRANT USE CATALOG  ON CATALOG  <cat>                       TO `biz-consumers-claims`;
GRANT USE SCHEMA   ON SCHEMA   <cat>.gold                  TO `biz-consumers-claims`;
GRANT SELECT       ON TABLE    <cat>.gold.cost_by_team     TO `biz-consumers-claims`;
GRANT EXECUTE      ON FUNCTION <cat>.gold.fn_team_rls      TO `biz-consumers-claims`;  -- ⭐ ห้ามลืม
-- ❌ อย่า grant ทั้ง catalog/schema อื่น — Genie จะ reach ได้หมด
```
> **จุดพลาดคลาสสิก:** มี `SELECT` + row filter แต่**ลืม `GRANT EXECUTE`** บน filter fn → query **fail / คืน 0 row เงียบๆ**. ใส่คู่กันเสมอ commit เดียวกัน.
> Row filter ต้องใช้ **`is_account_group_member('client-claims')`** ไม่ใช่ `is_member()` (ตัวหลัง return FALSE เงียบสำหรับ account user). รายละเอียด row-filter/mapping-table → `databricks-uc-governance-sharing` §3.

### ▶ STEP 5 — dashboard sharing (per-viewer RLS)
```
UI (บน dashboard ที่ publish): Share → เพิ่ม biz-consumers-claims → Can view
□ ตอน Publish เลือกโหมด credential:
     ✅ "Individual data permissions"   (embed_credentials: false) → query รันเป็น "ผู้ชม" → RLS ต่อคน fire
     ❌ "Share data permissions" (DEFAULT!) → query รันเป็น publisher → ทุกคนเห็น full set (data leak)
```
> ⚠️ **DEFAULT คือตัวอันตราย.** "we tried AI/BI and RLS didn't work" 99% = publish ผิดโหมด. Pin `embed_credentials: false` ใน DAB. รายละเอียด → `databricks-uc-governance-sharing` §7.

### ▶ STEP 6 — hardening (ปิดประตูหลัง)
```
□ ปิด dashboard email subscriptions   (schedule = job-like construct)
     Settings → Notifications area → toggle "dashboard email subscriptions" = off   [verify label in-tenant]
□ ปิด SQL results download             (กัน consumer export result set)
     Settings → Security area → "SQL results download" = off                          [verify label in-tenant]
□ ยืนยัน group ไม่มี PAT สิทธิ์สูง / ไม่มี service principal ปนใน group
     (entitlement enforce ที่ server-side → Jobs API โดน reject เหมือน UI)
```
> `[C-partial]` label สองอันบนสุดเป็น workspace admin setting จริง แต่ผมยังไม่ได้ fetch หน้า setting นั้นในรอบนี้ → **ยืนยัน label เป๊ะใน tenant** ก่อนอธิบายให้ทีม.

---

## 4. CONTROL GENIE USAGE/ปริมาณ ต่อ group — Genie budget

> นี่คือคำตอบของ **"ควบคุมปริมาณการใช้ Genie AI ต่อทีม"**. Genie = pay-as-you-go **LLM DBU ตั้งแต่ 2026-07-08 00:00 UTC** เกิน free allowance ต่อ user/เดือน. `[C]` [Genie budgets](https://learn.microsoft.com/en-us/azure/databricks/genie/budgets)

**สิ่งที่ block ได้จริง vs alert เฉยๆ** `[C]` [Budgets](https://learn.microsoft.com/en-us/azure/databricks/admin/account-settings/budgets):

| spend | block ได้? |
|---|---|
| **Genie LLM** — Unity AI Gateway budget ที่ scope ด้วย tag `databricks-product=genie` | ✅ **BLOCK** — checkbox **"Block usage"** annotated *"(For Genie budgets only)"* · near-real-time (ไม่ผูก system.billing ที่ช้า) |
| **Unity AI Gateway LLM อื่นที่ไม่ใช่ Genie** — Pay-Per-Token model serving, `ai_query` batch | ❌ **ALERT อย่างเดียว** `[C]` *"Per-user overrides and usage blocking is only available for Genie budgets"* |
| serverless SQL warehouse / classic compute | ❌ **ALERT อย่างเดียว** → cap ที่ compute config (STEP 3) |

> 🎯 **Precision ที่ต้องพูดให้ชัด:** "Block usage" = **Genie subset ของ Unity AI Gateway เท่านั้น** ไม่ใช่ AI-Gateway spend ทั้งหมด. spend ประเภทอื่น (PPT / `ai_query` batch / warehouse / classic) = track/alert ได้ แต่ **hard-block ไม่ได้** → ต้อง cap ที่ config ปลายทาง.

### สร้าง Genie budget — exact click-path `[C]`
```
□ Account Console (accounts.azuredatabricks.net) → sidebar: Usage
□ แท็บ Budgets → ปุ่ม "Create budget" (Genie doc) / "Add budget" (budgets doc) — label ต่างกันตามหน้า, ปุ่มเดียวกัน
□ Scope:
     • Name: genie-claims
     • Workspaces drop-down: เลือก <ws>   (ว่าง = ทั้ง account)
     • Resource types drop-down: Unity AI Gateway     ← ต้องเลือกตัวนี้
     • Resource tags → Select tags → Key: databricks-product   Values: genie
       ⚠️ ใส่ tag นี้ตัวเดียว — ใส่ tag อื่นเพิ่ม budget จะ "ไม่ track Genie เลย"
□ Shared thresholds (pool รวมทั้ง scope):
     • Add threshold → Monthly threshold: เช่น $5,000
     • When threshold exhausted: ☑ Send alert   (Databricks แนะนำติ๊กแค่ Send alert ที่ shared)
     • Email addresses: <distro>
□ Per-user thresholds (คุมต่อ user = ตัวคุมปริมาณจริง):
     • Add threshold → Monthly threshold: เช่น $30
     • When threshold exhausted: ☑ Block usage        ← hard cap ต่อ user
□ Per-user overrides (ให้บางทีม/บางคนได้มากกว่า แต่ยังคุม):
     • Add override → Users dropdown: เลือก biz-consumers-claims (หรือ user)
     • Monthly threshold: เช่น $200
□ Create
```

**Resolution rules** `[C]`: ใน budget เดียว → **most permissive** group ชนะ · ข้าม budget → **most restrictive** ชนะ. ⇒ อยากให้บางทีมได้มากกว่า = **override ใน budget เดียวกัน** (ไม่ใช่สร้าง budget แยกที่จะทำให้ restrictive สุดชนะ).

**Free tier — สิ่งที่ต้องพูดกับทีม** `[C]`:
- free = ต่อ **identified user เท่านั้น** (service principal **ไม่มี** free tier, ถูกคิดทุก DBU) · **reset วันที่ 1** · budget **เอา free ออกไม่ได้**.
- จำนวน free = **~150 LLM DBU/user/เดือน** `[I-flag]` — เลข 150 มาจาก **pricing page ไม่ใช่ Learn** (Genie budgets doc บอกแค่ *"see the pricing page"*) → **verify ตาม region** ก่อน quote.
- pooled ข้ามทุก surface (One + Agents + Code): user ใช้ $2 ใน Genie One + $10 ใน Genie Code = นับ $12 รวม.
- **compute ที่รัน Genie SQL บิลแยก** ไม่อยู่ใน Genie budget → คุมที่ warehouse (STEP 3).

**Warehouse budget (alert only):** สร้างอีก budget, Resource types = **All**, Resource tags = `team=claims` (warehouse tag) → threshold + email. Block ไม่ได้ → พึ่ง auto-stop + max scaling (STEP 3) เป็น cap จริง.

> ⚠️ **Preview coverage gap:** serverless **usage policies** (budget policies) tag ได้แค่ serverless notebook/job/pipeline/model-serving/Apps — **ไม่รวม serverless SQL warehouse และ Genie** → อย่าพึ่งมันคุม population นี้ → **tag ที่ warehouse เอง** (STEP 3).

---

## 5. ⚠️ STEP 0 — the prerequisite ที่ทำ lockdown พังเงียบ (additivity + migration)

### กับดัก
Entitlements **additive**. Consumer access lock ได้ **ก็ต่อเมื่อเป็น entitlement เดียว**. `[C]` *"users benefit from the consumer experience only if consumer access is their sole entitlement… Assigning additional workspace entitlements overrides the simplified consumer experience."*

**ปัญหาก่อน migrate:** `users` system group แถม **Workspace access + Databricks SQL access** ให้ทุกคน default → consumer **inherit สิทธิ์ author → สร้าง job ได้** ทั้งที่ตั้งใจบล็อก. `[C]` *"Until your workspace migrates… users with consumer access also inherit all entitlements granted to the users system group."*

### Timeline `[C]` [Migrate workspace entitlement control](https://learn.microsoft.com/en-us/azure/databricks/security/auth/system-group-entitlements-migration)
```
2026-06-15  opt-in ได้
2026-07-27  auto-enable (ถ้ายังไม่ opt-in/out) — ยัง opt-out ชั่วคราวได้จนถึง enforce
2026-09-14  enforce ทั้งหมด (ไม่มี opt-out)      ← อีก ~2 เดือน
```
หลัง migrate: `users` = **ไม่มี entitlement**, `admins` = ครบทุกตัว (ล็อกทั้งคู่) · เลือก entitlement ตอน add คนได้สะอาด · สิทธิ์เดิมย้ายไป workspace-local clone group **`users-clone-<TIMESTAMP>`**.

### 💡 คำแนะนำ (env ตึงแบบ AIA): **migrate เลย opt-in อย่ารอ 14 ก.ย.** `[I]`
ไม่งั้น Consumer access ไม่ restrictive จริง. **migration ทำโดย workspace admin** — สินอาจไม่ได้เป็นเจ้าของ **departmental workspace นี้ → ต้อง coordinate กับ workspace admin.**

### Pre-work ก่อนกด migrate `[C]`
```
□ repoint SCIM / Terraform / scripts → เขียน ACCOUNT group (ไม่ใช่ system group)
   (หลัง migrate: แก้ entitlement ของ system group จะ FAIL)
□ เลิก nest users/admins group (behavior ใหม่ห้าม nest)
□ ตั้ง SCIM ให้ PRESERVE clone group users-clone-<TS>
   (ถ้า SCIM ลบ group ที่ไม่รู้จัก → คน inherit ผ่าน clone จะหลุด access)
```

### Migrate — exact click-path `[C]` (workspace admin)
```
□ คลิก username มุมขวาบน → Settings
□ แท็บ Advanced
□ ใต้หัวข้อ Access control → หา
   "New behavior: Choose entitlements when adding principals to workspaces"
   สถานะจะขึ้น: "Legacy behavior (action might be needed)"
□ คลิก Manage
□ ใน dialog → Behavior for this workspace → เลือก "Use new behavior"
□ Clone group name → ตั้งชื่อ (หรือใช้ default users-clone-<TIMESTAMP>)
□ Save
```

### หลัง migrate — audit clone group `[C]` (จุดที่คนพลาด)
```
□ Settings → Identity and access → Groups → Manage → เปิด users-clone-<TS>
□ ยืนยัน: users = ไม่มี entitlement · admins = ครบ · clone = สิทธิ์กว้างเดิม
□ 🚨 ยืนยัน biz-consumers-* / biz-power-* NOT เป็นสมาชิก clone group
```
> **Sharp edge ที่ต้องระวัง** `[C]`: ตอน migrate, Databricks เอา *"principals directly assigned to the workspace… plus any account groups assigned to the workspace"* ใส่เข้า clone group อัตโนมัติ (เพื่อรักษา access เดิม). ⇒ **ถ้า `biz-consumers-<team>` ถูก assign เข้า workspace ก่อน migrate มันจะไปโผล่ใน clone group = ได้สิทธิ์ author (Workspace + SQL access) กลับมา.** ทางเลี่ยง: **assign consumer group หลัง migrate** หรือ **ลบออกจาก clone group ทันทีหลัง migrate**.

---

## 6. VERIFY checklist — login เป็น test user แต่ละ profile

### Profile A (Consumer-only) — ทำก่อนส่งมอบ
```
□ login test user ใน biz-consumers-claims → เด้งเข้า Genie One (ไม่ใช่ full workspace)
□ หา "Create job" / "Create notebook" / "Create cluster" → ไม่มี surface เลย
□ เปิด SQL editor → ไม่มีสิทธิ์
□ ดู warehouse list / Query History → มองไม่เห็น (แม้ได้ CAN USE)  [C]
□ ถาม Genie เรื่อง cost ทีมตัวเอง → เห็นเฉพาะ row ทีมตัวเอง (RLS)
□ prompt Genie ให้ join/query table ทีมอื่น → empty / no access (UC เป็นรั้ว ไม่ใช่ Genie)
□ Genie budget: spam จน > per-user threshold → โดน Block (เห็นข้อความ budget exhausted)
□ warehouse: ยืนยัน alert fires (ไม่ block) + auto-stop cap จริง
```

### Profile B (Databricks SQL access) — ต่างจาก A
```
□ login → เข้า DBSQL surface (ไม่ใช่ Genie One redirect)  ← คาดหวังต่างจาก A
□ author dashboard / เปิด SQL editor → ทำได้
□ "Create job" / "Create notebook" / cluster creation → ยังไม่มี surface  ← เส้นที่ห้ามข้าม
□ UC SELECT ยัง scope แคบ → query ได้เฉพาะ schema ที่ควรเห็น
```

---

## 7. Honest flags (พูดกับทีมตรงๆ)

1. **`[C]` แต่ doc-contested — RLS สำหรับ *bare account user* (ไม่มี entitlement):** ตาราง *"Consumer access vs account users"* ในหน้า entitlements แสดง *"View objects using row- and column-level security"* = ✓ ให้**ทั้ง** Consumer access และ bare account user; แต่ AI/BI admin matrix อีกหน้าบอก ✗ สำหรับ bare account user. **docs ขัดกัน → test ด้วย identity จริงใน tenant ก่อน commit.** — **แต่ moot สำหรับงานนี้** เพราะ user ของเราถือ Consumer access (Profile A) หรือ SQL access (Profile B) อยู่แล้ว (ซึ่ง RLS fire แน่นอน — ตารางให้ ✓ กับ Consumer access ชัดเจน). เหตุผล confirmed ที่ต้องใช้ Consumer access = **เห็น Genie Agent/App ได้** + **อ่าน workspace-bound catalog ได้** (bare account user ทำไม่ได้ทั้งคู่ `[C]`).
2. **Genie ≠ security boundary — UC คือรั้ว.** `[C]` consumer prompt Genie ให้ query table ไหนก็ได้ที่เขามี `SELECT` → **scope UC grant แคบ** คือด่านจริง ไม่ใช่ attached-table list ของ Genie space.
3. **Free ~150 LLM DBU = pooled ต่อ user ข้ามทุก surface**, เอาออกด้วย budget ไม่ได้, reset วันที่ 1, **service principal ไม่มี free tier**. เลข 150 มาจาก pricing page ไม่ใช่ Learn → verify ตาม region.
4. **Budget block ได้เฉพาะ Genie LLM (subset ของ Unity AI Gateway)** — AI-Gateway อื่น (PPT/`ai_query`) และ warehouse/classic = **alert only** → cap ที่ compute config (auto-stop + max scaling). **Block usage อาจเกิน threshold นิดหน่อย** (request in-flight ไม่ถูกตัด).
5. **Additivity + migration = จุดพังเงียบที่สุด.** entitlement ที่ 2 หรือ pre-migration inheritance เปลี่ยน consumer เป็น author. **migrate + audit clone group.** migration = workspace admin → **coordinate** (สินอาจไม่ owner).
6. **Lock-in note:** entitlement/Consumer-access/Genie-budget model นี้ **Databricks-proprietary**. gold table = portable Delta, row filter = rewritable SQL UDF (portable). ถ้าต้องการ low-lock-in path สำหรับ consumer: **UC GRANT + Power BI ของทีมเอง** บน UC (ทีม query จาก workspace ตัวเอง จ่าย compute เอง = chargeback จริง — ตรงกับ Topic 1 D+).

---

### Source docs (Microsoft Learn + Terraform provider, ดึงสด 2026-07-18)
- Entitlements + exact labels + API names + "Consumer access vs account users" table: https://learn.microsoft.com/en-us/azure/databricks/security/auth/entitlements
- Consumer access (Genie One redirect / cannot-create-objects / users-group inheritance): https://learn.microsoft.com/en-us/azure/databricks/ai-bi/consumers/
- Budgets (Block usage = Genie-only / resolution / Add-budget path): https://learn.microsoft.com/en-us/azure/databricks/admin/account-settings/budgets
- Genie budgets (free tier / 2026-07-08 / SP no free / pooled / resolution rules): https://learn.microsoft.com/en-us/azure/databricks/genie/budgets
- Entitlement migration (opt-in path / clone-group auto-add / timeline): https://learn.microsoft.com/en-us/azure/databricks/security/auth/system-group-entitlements-migration
- **Terraform `databricks_entitlements` (`workspace_consume` mutual-exclusivity):** https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/entitlements

**Companion skills (deep-dive):** `databricks-genie-governance` (GATE 1-4, cost SQL) · `databricks-uc-governance-sharing` (§3 row filter, §7 publish modes). **Escalate:** Entra/SCIM plumbing → `azure-expert`; regulatory sign-off → `governance-consultant`.

---
**Labels ที่ verify แล้วในรอบนี้ vs ยังต้อง confirm ใน tenant:**
- ✅ verified exact: entitlement toggles + API names (`workspace-consume`/`databricks-sql-access`/`workspace-access`/`allow-cluster-create`/`allow-instance-pool-create`), `Settings → Identity and access → Manage`, migration `Advanced → Access control → New behavior… → Manage → Use new behavior → Clone group name → Save`, budget `Usage → Budgets → Create/Add budget → Resource types (All / Unity AI Gateway) → Select tags (databricks-product / genie) → Block usage (Genie-only)`, TF `workspace_consume` mutual-exclusivity.
- ⚠️ ยัง confirm: label เป๊ะของ **dashboard email subscriptions** และ **SQL results download** (STEP 6) — เป็น setting จริงแต่ผมยังไม่ได้ fetch หน้านั้น → verify ก่อนอธิบายทีม.

---

## Reviewer changes

1. **[Runnable bug — FIXED] Profile B ไม่ใช่ "Consumer access + Databricks SQL access."** `workspace_consume` **ใช้ร่วมกับ `databricks_sql_access`/`workspace_access` ไม่ได้** — Databricks Terraform provider reject ตรงๆ (*"Couldn't be used with `workspace_access` or `databricks_sql_access`"*), และ Learn additivity doc ยืนยันว่า entitlement ที่ 2 **override** consumer experience อยู่ดี (consumer เป็น entitlement ที่ตายซาก). เดิมสั่ง "uncomment `databricks_sql_access = true`" ทับ `workspace_consume = true` → `terraform apply` **จะ fail**. แก้เป็น: Profile B = **Databricks SQL access อย่างเดียว** (drop Consumer access), แยก Terraform เป็นคนละ resource/group. Security ยังคุมได้เท่าเดิม (job ยังบล็อกเพราะไม่มี `workspace-access`) และไม่เสีย capability (SQL access เป็น superset ของ consume). แก้ที่ §1 หลักตัดสิน tier, §2 Profile B (ตาราง + note), §3 STEP 2 toggles, §3 Terraform aside, §6 Profile B header.

2. **[Precision overstatement — FIXED] §4 block table เดิม lump "Genie / Unity AI Gateway LLM = ✅ BLOCK."** ผิด scope — "Block usage" เป็น **Genie-only** (Unity AI Gateway budget ที่ scope ด้วย tag `databricks-product=genie` เท่านั้น). Unity AI Gateway LLM อื่น (Pay-Per-Token model serving, `ai_query` batch) = **alert only, block ไม่ได้** (doc: *"Per-user overrides and usage blocking is only available for Genie budgets"*). แยกเป็น 3 แถว + เพิ่ม precision note; ปรับ flag #4 ให้ตรง.

3. **[Naming note — added] "Genie One" ถูกต้องตาม Azure Learn ปัจจุบัน.** consumer doc (`ms.date` 2026-07-14) ระบุชัด *"directed to Genie One."* หมายเหตุ: Terraform provider doc ของ `workspace_consume` ยังเขียน "Databricks One" (ลิงก์ AWS, ตามหลัง rename) — ไม่ใช่ error ของ deliverable, เพิ่ม note กันสับสน.

**ยืนยันว่าถูกต้องอยู่แล้ว (ไม่แก้):** entitlement API names ทั้ง 5, Premium-plan requirement, Consumer-cannot-create-objects + cannot-see-warehouse/Query-History (doc-backed verbatim), additivity trap, migration timeline **2026-07-27 auto / 2026-09-14 enforced** (+ opt-in 2026-06-15), clone-group auto-add sharp edge, budget resolution rules (in-budget=most-permissive / cross-budget=most-restrictive), free-tier mechanics (SP no free / reset วันที่ 1 / pooled / budget เอาออกไม่ได้), 150-from-pricing-page hedge, compute-billed-separately, budget-policies-Preview-gap, publish-mode RLS (§5), `is_account_group_member` vs `is_member`, GRANT EXECUTE gotcha, RLS-tier-contested hedge (§7 #1), Genie-not-a-security-boundary (§7 #2), all UI click-paths (Identity-and-access / Advanced-Access-control / Usage-Budgets). ทั้งหมด match live docs.

Sources:
- [Manage entitlements — Azure Databricks](https://learn.microsoft.com/en-us/azure/databricks/security/auth/entitlements)
- [What is consumer access? — Azure Databricks](https://learn.microsoft.com/en-us/azure/databricks/ai-bi/consumers/)
- [Create and monitor budgets — Azure Databricks](https://learn.microsoft.com/en-us/azure/databricks/admin/account-settings/budgets)
- [Manage budgets and cost controls for Genie — Azure Databricks](https://learn.microsoft.com/en-us/azure/databricks/genie/budgets)
- [Migrate workspace entitlement control — Azure Databricks](https://learn.microsoft.com/en-us/azure/databricks/security/auth/system-group-entitlements-migration)
- [databricks_entitlements — Terraform Registry](https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/entitlements)