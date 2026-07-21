# Governance + Monitoring — Web UI User Manual (จับมือทำผ่านหน้าเว็บ)

> **สิ่งที่ doc นี้ตอบ:** "ถ้าจะทำแต่ละข้อใน checklist ผ่านหน้า UI (ไม่ deploy อะไร) กดตรงไหนบ้าง"
> เรียงตาม **priority: 1.2 → 1.4 → 2.1 (2 dashboard)** ก่อน แล้วค่อยตามด้วยข้อที่เหลือ
> คู่กับ **[governance-management-deployment-options.md](governance-management-deployment-options.md)** (Doc 2 = ถ้าจะ automate/deploy ใช้อะไร) และ code ที่ `../deploy/`
> Generic — ไม่มี AIA identifier, ตัด `<...>`/`${...}` = placeholder ใส่ค่าจริงตอนทำ

## Checklist ที่ manual นี้ครอบคลุม

```
1. Access Management
   1.1 Identity        — User, Consumer Group
   1.2 Entitlement ⭐   — Platform layer (Service)          ← priority
   1.3 Permission      — Object & Asset (Objects)
   1.4 Data/Grant ⭐    — Row-level access                   ← priority
2. Monitoring
   2.1 Cost ⭐          — (a) ADB per-team all-service  (b) Genie AI   ← priority (2 dashboards)
   2.2 Observability   — Infra tag / Job pipeline tag / Data Quality
```

**กติกา 3 ข้อที่ต้องจำ (ผิดแล้วพัง เงียบๆ):**
1. RLS ใช้ **account group** เท่านั้น (ไม่ใช่ workspace-local group) และในโค้ดใช้ `is_account_group_member()` — `is_member()` จะคืน FALSE เงียบๆ กับ account user
2. Consumer access (1.2) จะล็อกได้ต่อเมื่อ `workspace-consume` เป็น entitlement **ตัวเดียว** — entitlement เป็น additive
3. Dashboard published (2.1) ต้อง publish แบบ **Individual data permissions** ไม่งั้น viewer ทุกคนเห็นทุก row

---

# ⭐ 1.2 Entitlement (Consumer access lockdown) — ทำก่อน

> รายละเอียดเต็ม + STEP 0 migration อยู่ที่ [consumer-access-user-manual.md](consumer-access-user-manual.md) และ [consumer-access-DEPLOY-GUIDE.md](consumer-access-DEPLOY-GUIDE.md). ตรงนี้เป็น quick click-path.

**เป้าหมาย:** business user เข้าได้แค่ Genie/AI-BI ตั้ง job ไม่ได้

### STEP 0 (สำคัญ — ทำก่อนเสมอ): เช็ค entitlement migration
1. **Account console** (`accounts.azuredatabricks.net`) → **Settings** → **Feature enablement / Advanced**
2. หา **entitlement/access-control migration** — ถ้ายังไม่เปิด: consumer จะ inherit สิทธิ์จาก system group `users` (Workspace + SQL access) → **lockdown พังเงียบ**
3. Timeline: opt-in เปิดได้เลย · auto-enable **2026-07-27** · enforced **2026-09-14**
4. ⚠️ Migration = toggle setting ของ workspace **ไม่ใช่** สร้าง Databricks ใหม่ และมันแตะ workspace ที่คุณอาจไม่ได้เป็นเจ้าของ → ประสานกับ admin ของ consumer workspace

### STEP 1: สร้าง/หา account group
- **Account console** → **User management** → **Groups** → กลุ่มควรมาจาก Entra (SCIM sync) ชื่อแนว `consumer-<team>`
- ถ้ายังไม่มี → **ขอ IdP/infra team สร้างใน Entra** (ปกติ DE สร้าง account group เองไม่ได้ — ดู Doc 2 ownership)

### STEP 2: ตั้ง entitlement ให้เป็น Consumer access ตัวเดียว
1. **Account console** → **User management** → **Groups** → เลือก `consumer-<team>` → **Entitlements**
2. ✅ ติ๊ก **Consumer access** (`workspace-consume`)
3. ❌ **เอาออกให้หมด**: Workspace access, Databricks SQL access, Allow cluster creation
4. ตรวจว่า inherited จาก `users` ไม่หลุดเข้ามา (นี่คือเหตุผลที่ต้องทำ STEP 0)

> **Profile B (power team ที่ต้องใช้ SQL):** ไม่ใช่ "เพิ่ม SQL access" — มันคือ **SWAP** = `databricks-sql-access` ✅ / `workspace-consume` ❌ (Terraform reject ถ้าใส่คู่กัน)

### STEP 3: assign group เข้า workspace
- **Workspace admin settings** → **Permissions / Identity and access** → **Groups** → **Add** `consumer-<team>`

### STEP 4: Genie budget (คุมค่า LLM)
1. **Account console** → **Usage / Budgets** → **Create budget**
2. Filter ที่ **Genie / Unity AI Gateway (LLM)** → set per-user threshold → **Block usage** (Genie LLM block ได้จริง)
3. ⚠️ warehouse/classic compute = **alert only** (block ไม่ได้) → คุมที่ warehouse config (auto-stop + max clusters) แทน
4. per-user override ตั้ง target เป็น **group** ได้ = คุม per-group ใน budget เดียว

---

# ⭐ 1.4 Data / Grant — Row-Level access — ทำเป็นอันดับ 2

**เป้าหมาย:** แต่ละ team เห็นเฉพาะ row ของตัวเอง (บน cost view / gold table)

### แนวคิด: ทำผ่าน SQL Editor เป็นหลัก (grant + row filter เป็น SQL DDL, ไม่มีปุ่ม UI ให้ bind row filter)

### STEP 1: สร้าง mapping table (ครั้งเดียว) — SQL Editor
```sql
CREATE TABLE IF NOT EXISTS <gov_catalog>.control.team_access_map (team_tag STRING, account_group STRING);
INSERT INTO <gov_catalog>.control.team_access_map VALUES ('alpha','consumer-alpha');
```

### STEP 2: สร้าง row-filter UDF (ครั้งเดียว)
```sql
CREATE OR REPLACE FUNCTION <catalog>.<gold>.fn_team_rls(team_tag STRING)
RETURN is_account_group_member('<platform-group>')
    OR EXISTS (SELECT 1 FROM <gov_catalog>.control.team_access_map m
               WHERE m.team_tag = team_tag AND is_account_group_member(m.account_group));
```

### STEP 3: grant + bind (ต่อ 1 team — **grant 4 อันต้องมาคู่กัน** นี่คือกับดักที่ลืมบ่อย)
```sql
GRANT USE CATALOG ON CATALOG <catalog>                         TO `consumer-alpha`;
GRANT USE SCHEMA  ON SCHEMA  <catalog>.<gold>                  TO `consumer-alpha`;
GRANT SELECT      ON TABLE   <catalog>.<gold>.cost_by_team     TO `consumer-alpha`;
GRANT EXECUTE     ON FUNCTION <catalog>.<gold>.fn_team_rls     TO `consumer-alpha`;  -- ← ลืมบ่อยสุด
ALTER TABLE <catalog>.<gold>.cost_by_team SET ROW FILTER <catalog>.<gold>.fn_team_rls ON (team_tag);
```

### STEP 4: verify (สำคัญ — RLS-for-bare-account-user เป็นเรื่อง contested ต้องทดสอบจริง)
- **SQL Editor** → **Run as** (ถ้ามี) หรือให้ user จริง 1 คน query → ต้องเห็นเฉพาะ row ตัวเอง
- ตรวจ binding: `DESCRIBE TABLE EXTENDED <catalog>.<gold>.cost_by_team;` (จะเห็น row filter ที่ผูก)

### แก้ตอน onboard team ใหม่ (routine): เพิ่มแค่ 1 แถวใน map — ไม่ต้องแตะ DDL
```sql
INSERT INTO <gov_catalog>.control.team_access_map VALUES ('beta','consumer-beta');
GRANT SELECT ON TABLE <catalog>.<gold>.cost_by_team TO `consumer-beta`;
GRANT EXECUTE ON FUNCTION <catalog>.<gold>.fn_team_rls TO `consumer-beta`;
```
> ทำซ้ำๆ แบบนี้บ่อย = churn สูง → **Doc 2 แนะนำให้ย้ายเป็น reconciliation job** (`../deploy/jobs/rls_reconcile.py`) ที่อ่าน control table แล้ว apply ให้เอง แต่ทำมือผ่าน SQL Editor ก็ได้ถ้ายังน้อย

---

# ⭐ 2.1 Cost Monitoring — 2 dashboards — ทำเป็นอันดับ 3

> SQL พร้อมใช้อยู่ที่ `../deploy/dashboards/` — ตรงนี้คือวิธีเอาขึ้นหน้า UI

### STEP 1: สร้าง view (ครั้งเดียว) — SQL Editor
- รัน `../deploy/dashboards/cost_views.sql` (แทน `${...}` ก่อน) — ได้ `v_billing_priced_rls` + `v_genie_priced_rls`

### STEP 2: สร้าง dashboard — AI/BI (Lakeview)
1. Sidebar → **Dashboards** → **Create dashboard**
2. แท็บ **Data** → **Create from SQL** → วาง query จาก `dashboard_a_departmental.sql` (ทีละ visual)
3. แท็บ **Canvas** → **Add visualization** → เลือกชนิดตาม layout comment ท้ายไฟล์ (Counter/Line/Bar/Table)
4. **Filters** → Add → date range (`:date_start`/`:date_end`), service field-filter
5. ทำซ้ำสำหรับ Dashboard B (Genie) จาก `dashboard_b_genie.sql`

### STEP 3: per-team RLS (แต่ละ team เห็นเฉพาะของตัวเอง) — publish mode คือหัวใจ
1. มุมขวาบน → **Publish**
2. เลือก **Individual data permissions** (embed credentials = **OFF**)
   - ⚠️ อย่าเลือก default "Share data permissions" (embed = ON) → viewer ทุกคนรันเป็น publisher = เห็นทุก team (leak)
3. RLS จะ evaluate ตาม identity ของ **คนดู** ผ่าน secure view → เพิ่ม team = insert 1 แถวใน `team_access_map`

### STEP 4: refresh + who-pays
- **Schedule** → ตั้ง cron (daily/6-hourly พอ — system table lag ไม่กี่ชม.) → warehouse serverless auto-stop ≤10 นาที
- ⚠️ dashboard published รันบน warehouse **ของ publisher** → platform จ่ายค่าให้ทุก team เปิดดู → ถ้าอยาก chargeback จริง: `GRANT SELECT ON v_*_priced_rls TO consumer-<team>` แล้วส่ง `.lvdash.json` ให้เขา import ไปดูจาก warehouse ตัวเอง

### ⚠️ verify ก่อนเชื่อตัวเลข Genie (flag จาก research)
- `SELECT DISTINCT billing_origin_product FROM system.billing.usage;` — ยืนยันว่ามี `'GENIE'` จริง (ยัง under-documented; ถ้าไม่มีอาจอยู่ใต้ `AI_GATEWAY`)
- `SELECT usage_metadata.genie.* ...` — ยืนยัน field `surface` มีจริงก่อนใช้ visual B3

---

# 1.1 Identity — User / Consumer Group (ทำตามได้เมื่อจำเป็น)

**เป้าหมาย:** ให้ user + group มาถึง Databricks

- **User (churn สูง — joiner/mover/leaver):** อย่าจัดการมือ → มาจาก **Entra ผ่าน SCIM** อัตโนมัติ. เช็คได้ที่ **Account console → User management → Users** (read-only เป็นหลัก)
- **Consumer/account group:** มาจาก Entra เช่นกัน. DE **สร้าง account group เองปกติไม่ได้** (ต้องเป็น account/workspace admin) → **ขอ IdP team สร้างใน Entra** แล้วมัน sync ลงมา
- **หน้า UI:** Account console → **User management** → **Groups** → เห็น group ที่ sync มา, กด group เพื่อดู members/entitlements
- ⚠️ อย่าสร้าง **workspace-local group** มาใช้กับ UC — มัน resolve ข้าม workspace ไม่ได้ และ `is_account_group_member()` มองไม่เห็น

---

# 1.3 Permission — Object & Asset ACL (ทำตามได้เมื่อจำเป็น)

**เป้าหมาย:** คุมสิทธิ์บน object (warehouse, dashboard, Genie space, job)

### SQL Warehouse
- **SQL** → **SQL Warehouses** → เลือก warehouse → **Permissions** → **Add** `consumer-<team>` = **CAN USE** (อย่าให้ CAN MANAGE — ไม่งั้นแก้ compute ได้)

### Dashboard
- เปิด dashboard → **Share** → เพิ่ม group → **Can view** (หรือ Can run/edit/manage)

### Genie space
- เปิด Genie space → **Share / Permissions** → เพิ่ม group → **Can run** / **Can view**
- ⚠️ จัดการผ่าน UI/REST — TF provider ยังไม่ confirm `genie_space_id`

### Job
- **Workflows** → เลือก job → **Permissions** → **Add** → CAN VIEW / CAN MANAGE RUN / IS OWNER
- (consumer access ปกติสร้าง job ไม่ได้อยู่แล้ว — ข้อนี้สำหรับ power team)

---

# 2.2 Observability — Infra / Job pipeline / Data Quality (deferred, ทำทีหลัง)

> ยัง deferred จนกว่า 1.2/1.4/2.1 เสร็จ — ใส่ไว้ให้ครบ checklist. detail เต็มอยู่ใน skill `databricks-observability`.

- **Infra tracking (tag):** ทุก compute (cluster/warehouse/job) ใส่ **tag** (team/CostCenter) ที่หน้า config → cost + usage แยกตาม tag ได้เอง. เช็คที่ `system.billing.usage.custom_tags`
- **Job pipeline tracking (tag):** ตั้ง tag ตอนสร้าง job/DLT → query health จาก `system.lakeflow.*` (job runs, task duration, failures)
- **Data Quality:** ใช้ **Lakehouse Monitoring** (Catalog → table → **Quality** tab → Create monitor) หรือ DLT expectations → metric table + dashboard
- **SQL Alert:** SQL → **Alerts** → New → ผูก query (เช่น job fail, cost spike) → notification

---

## สรุป priority + "ทำมือ vs automate"

| ข้อ | ทำมือผ่าน UI ได้ | ควร automate เมื่อ | ที่ Doc 2 แนะนำ |
|---|---|---|---|
| 1.2 Entitlement | ได้ (rarely change) | มีหลาย team / audit | **Terraform** |
| 1.4 RLS grant | ได้ (SQL Editor) | churn สูง (team เข้า-ออกบ่อย) | **reconciliation job** |
| 2.1 Dashboards | ได้ (สร้างครั้งเดียว) | อยาก version control | **DAB** |
| 1.1 Identity | read-only | เสมอ | **SCIM (IdP team)** |
| 1.3 ACL | ได้ | asset เยอะ | **DAB/TF** |

→ อ่านต่อ **Doc 2** ว่าทำไมแต่ละอันเลือก tool นั้น + ใครเป็นเจ้าของ (infra vs คุณ) + Jenkins กับ scheduler job ต่างกันยังไง
