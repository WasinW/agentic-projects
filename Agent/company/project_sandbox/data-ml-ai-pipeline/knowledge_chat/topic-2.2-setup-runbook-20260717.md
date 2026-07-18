# Topic 2.2 — Setup Runbook: business-user lockdown (Consumer access + Genie + budget)

> **วันที่:** 2026-07-17 · คู่กับ `topic-2.2-consumer-access-genie-budget-20260717.md` (เหตุผล + citation)
> **เป้าหมาย:** business user ต่อทีม ใช้ได้แค่ Genie/AI-BI · สร้าง job ไม่ได้ · เห็นเฉพาะ row ของทีมตัวเอง · budget capped
> **ทำทีละทีม** (ตัวอย่าง `claims`) — ทำซ้ำต่อทีมโดยเปลี่ยนชื่อ
> **Placeholder:** `<cat>` catalog · `<ws>` departmental workspace · `<wh_id>` serverless SQL warehouse

---

## ⚠️ STEP 0 — Prerequisite ที่ห้ามข้าม (ไม่งั้น lockdown พังเงียบ)

**ตรวจก่อน:** workspace นี้ migrate entitlement behaviour แล้วหรือยัง?
- Account console → workspace → Settings → ดูว่า `users` system group ยังมี entitlement (Workspace access / SQL access) อยู่มั้ย
- **ถ้ายังมี → ยังไม่ migrate → Consumer access ยัง inherit สิทธิ์ author → ยังไม่ปลอดภัย**

**ถ้ายังไม่ migrate → migrate เลย (opt-in อย่ารอ 2026-09-14):**
```
pre-work ก่อนกด migrate:
  □ repoint SCIM / Terraform automation → account group (ไม่ใช่ system group)
     (หลัง migrate เขียน entitlement ของ system group จะ fail)
  □ เลิก nest users/admins group
  □ ตั้ง SCIM ให้เก็บ users-clone-<TIMESTAMP> (ไม่งั้นคน inherit อยู่จะหลุด access)
migrate:
  □ Account console → workspace → opt-in entitlement migration
หลัง migrate:
  □ audit users-clone-<TIMESTAMP> — มันได้สิทธิ์กว้างเดิมมา
  □ ยืนยัน biz-consumers-* NOT member ของ clone group
```

---

## STEP 1 — Account group (Entra → SCIM)

```
□ สร้าง account-level group: biz-consumers-claims
   (sync จาก Entra ID ผ่าน SCIM / Automatic Identity Management)
□ ยืนยันเป็น ACCOUNT group ไม่ใช่ workspace-local
   ทดสอบ: SELECT is_account_group_member('biz-consumers-claims');  -- ต้องได้ true สำหรับ member
□ อย่าใช้ CREATE GROUP ใน SQL (สร้าง workspace-local group — ใช้ไม่ได้)
```

---

## STEP 2 — Grant Consumer access **เท่านั้น** (additivity!)

```
□ Workspace <ws> → Settings → Identity and access → Groups → biz-consumers-claims → Manage
□ ✅ Consumer access          (workspace-consume)
□ ❌ Workspace access          (workspace-access)          ← ห้ามให้ (นี่คือตัวเปิด Jobs)
□ ❌ Databricks SQL access     (databricks-sql-access)     ← ห้ามให้ (นี่คือตัวเปิด SQL editor/author)
□ ❌ Allow unrestricted cluster creation  (allow-cluster-create)
□ ❌ Allow pool creation                  (allow-instance-pool-create)
```
> 🚨 **entitlement เดียวเท่านั้น** — เพิ่มตัวที่ 2 = consumer experience หาย + สร้าง job ได้

**Terraform equivalent:**
```hcl
resource "databricks_entitlements" "biz_consumers_claims" {
  group_id                   = databricks_group.biz_consumers_claims.id
  workspace_consume          = true
  # ทุกตัวอื่น = false (default) — อย่า set true
}
```

---

## STEP 3 — Compute: 1 serverless SQL warehouse ต่อทีม

```
□ สร้าง serverless SQL warehouse: wh-claims  (Genie ต้องมี warehouse รันถึงจะตอบ)
□ tag: team = claims                          (→ ลง system.billing.usage.custom_tags → chargeback)
□ Auto stop: 5-10 นาที                         (cap warehouse cost ที่ต้นทาง — budget block ไม่ได้)
□ Scaling: max cluster count จำกัด (เช่น 1-2)   (cap ceiling)
□ Permission: biz-consumers-claims = CAN USE   (❌ ไม่ใช่ CAN MANAGE — ไม่งั้นเห็น/แก้ warehouse ได้)
```

---

## STEP 4 — UC grant = รั้วจริง (Genie ไม่ใช่ security boundary)

```sql
-- ให้แคบที่สุด — user prompt Genie query table ไหนก็ได้ที่เขามี SELECT
GRANT USE CATALOG  ON CATALOG  <cat>                       TO `biz-consumers-claims`;
GRANT USE SCHEMA   ON SCHEMA   <cat>.gold                  TO `biz-consumers-claims`;
GRANT SELECT       ON TABLE    <cat>.gold.cost_by_team     TO `biz-consumers-claims`;
GRANT EXECUTE      ON FUNCTION <cat>.gold.fn_team_rls      TO `biz-consumers-claims`;  -- ถ้ามี row filter

-- ❌ อย่า grant กว้าง (เช่น ทั้ง catalog / schema อื่น) — Genie จะ reach ได้หมด
```
> row filter ต้องใช้ `is_account_group_member('client-team-claims')` **ไม่ใช่ `is_member()`** · และ RLS บังคับใช้ก็ต่อเมื่อ user เป็น Consumer access ขึ้นไป (ซึ่ง STEP 2 ให้แล้ว)

---

## STEP 5 — Hardening (ปิดประตูหลัง)

```
□ Settings → Notifications → ปิด "Enable dashboard email subscriptions"
   (schedule = job-like construct — ปิด residual scheduling surface)
□ Settings → Security → ปิด "SQL results download"
   (กัน consumer export result set ออก)
□ ยืนยัน group ไม่มี PAT สิทธิ์สูง / ไม่มี service principal ปนใน group
   (entitlement enforce ที่ server-side → Jobs API ก็โดน reject เหมือน UI)
```

---

## STEP 6 — Budget

### 6a. Genie LLM budget — **enforce (block ได้)**
```
□ Account console → Budgets → Create
□ Resource type: Unity AI Gateway
□ Tag filter: databricks-product = genie   (tag เดียว ห้ามใส่ตัวอื่น)
□ Scope: workspace <ws> / group biz-consumers-claims
□ Shared threshold:  = ALERT (pool รวม)
□ Per-user threshold: เช่น $30/user + ☑ Block usage   ← hard cap
□ Group override: ถ้าบางคนต้องมากกว่า
```
> resolution: ใน budget เดียว group permissive สุดชนะ · ข้าม budget restrictive สุดชนะ
> ⚠️ Genie free 150 LLM DBU/user/เดือน เอาออกไม่ได้ · reset วันที่ 1 · SP ไม่มี free tier

### 6b. Warehouse budget — **alert อย่างเดียว (block ไม่ได้)**
```
□ Account console → Budgets → Create
□ Filter: warehouse tag team = claims
□ Threshold + email alert
□ (block ไม่ได้ → พึ่ง STEP 3: auto-stop + max scaling เป็นตัว cap จริง)
```

---

## STEP 7 — Verify (ทำก่อนส่งมอบ)

```
□ login เป็น test user ใน biz-consumers-claims → ต้องเด้งไป Genie One (ไม่ใช่ full workspace)
□ ลองกด "สร้าง job" / "สร้าง notebook" / "สร้าง cluster" → ต้องไม่มี surface / โดน block
□ เปิด SQL editor → ต้องไม่มีสิทธิ์
□ ถาม Genie เรื่อง cost ทีมตัวเอง → เห็นเฉพาะ row ทีมตัวเอง (RLS)
□ ลอง prompt Genie ให้ query table อื่นนอก grant → ต้อง "empty response" / no access
□ ดู warehouse list → ต้องมองไม่เห็น
□ (ถ้าเทสได้) Genie budget block → spam จน >$30 → ต้องโดนหยุด
```

---

## STEP 8 — Monitor (เชื่อม Topic 2.1)
```sql
-- Genie LLM ต่อ user
SELECT identity_metadata.run_as, usage_metadata.genie.surface, SUM(usage_quantity) AS dbus
FROM system.billing.usage
WHERE billing_origin_product = 'GENIE' AND usage_date >= :start
GROUP BY ALL ORDER BY dbus DESC;

-- warehouse cost ต่อทีม
SELECT custom_tags['team'] AS team, SUM(usage_quantity) AS dbus
FROM system.billing.usage
WHERE custom_tags['team'] IS NOT NULL AND usage_date >= :start
GROUP BY ALL;
```

---

## ✅ checklist สรุป (1 ทีม)
- [ ] STEP 0 workspace migrated + clone group audited
- [ ] STEP 1 account group + verify is_account_group_member
- [ ] STEP 2 Consumer access **only**
- [ ] STEP 3 serverless warehouse + tag + auto-stop + CAN USE
- [ ] STEP 4 UC SELECT แคบ + EXECUTE (ถ้ามี RLS)
- [ ] STEP 5 ปิด subscription + download
- [ ] STEP 6 Genie budget (block) + warehouse budget (alert)
- [ ] STEP 7 verify ทั้ง 7 ข้อ
- [ ] STEP 8 monitor query
