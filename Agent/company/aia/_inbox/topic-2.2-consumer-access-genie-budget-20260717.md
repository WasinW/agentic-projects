# Topic 2.2 — Consumer access + Genie + budget ต่อทีม (business user lockdown)

> **วันที่:** 2026-07-17 · verify กับ Microsoft Learn (อัปเดต 2026-07-08 ถึง 2026-07-15) · [C]=confirmed docs · [I]=inference
> **requirement (verbatim):** *"consumer access — end goal อยากให้ business user ใช้เฉพาะ Genie AI/BI ได้ แต่ตั้ง job ไม่ได้ ถ้าเข้าได้แต่ Genie One ก็ไม่มีปัญหา"*
> **2 เรื่องซ้อน:** (A) คุมการใช้งาน/สิทธิ์ · (B) budget

---

## 🎯 คำตอบสั้น: **Consumer access ตอบโจทย์เป๊ะ — แต่ต้อง migrate workspace ก่อน ไม่งั้นพังเงียบๆ**

---

## PART A — Access control: "Genie/AI-BI only, no jobs"

### A1. entitlement model — มี 3 ตัวเท่านั้น [C]
[Manage entitlements](https://learn.microsoft.com/en-us/azure/databricks/security/auth/entitlements)

| ความสามารถ | **Consumer access**<br>`workspace-consume` | Databricks SQL access<br>`databricks-sql-access` | Workspace access<br>`workspace-access` |
|---|:--:|:--:|:--:|
| อ่าน/รัน dashboard, Genie Agent, Apps ที่ share มา | ✓ | ✓ | ✓ |
| query warehouse ผ่าน BI tool | ✓ | ✓ | |
| อ่าน/เขียน DBSQL object (author dashboard/Genie, SQL editor) | | ✓ | |
| อ่าน/เขียน DS&E object (**notebook, job, pipeline, model**) | | | ✓ |

> **[C] job authoring อยู่หลัง `workspace-access`** — *"Grants access to core workspace features such as notebooks, **jobs**, models, and pipelines"* → **ไม่ให้ตัวนี้ = ไม่มี Jobs UI เลย**
> compute entitlement แยกอีก 2: `allow-cluster-create`, `allow-instance-pool-create` — non-admin ไม่ได้ default

### A2. Consumer access ทำอะไรได้/ไม่ได้ [C]
[What is consumer access?](https://learn.microsoft.com/en-us/azure/databricks/ai-bi/consumers/) (อัปเดต 2026-07-14):
> *"Consumer access is a workspace entitlement that gives users access to workspace-level **Genie One**. When users with consumer access sign in, they are directed to **Genie One instead of the standard workspace**… **Users with only consumer access cannot create new objects in the workspace.**"*

| ✅ ทำได้ | ❌ ทำไม่ได้ |
|---|---|
| ใช้ Genie One | สร้าง **job / cluster / pipeline / notebook** |
| ดู/interact dashboard, Genie Agent, App ที่ share มา | สร้าง/แก้ dashboard, Genie Agent |
| ถามคำถามใน Genie | เปิด **SQL editor** / ad-hoc SQL |
| ได้ CAN USE warehouse → ใช้ Power BI/Tableau | ดู warehouse / Query History (แม้ grant permission แล้ว) |
| **RLS/CLS บังคับใช้บน view ของเขา** | สร้าง object ใดๆ ในworkspace |

> **⇒ "สร้าง job ได้มั้ย?" = ไม่ได้ (ยืนยันจาก docs)** — ไม่มี Jobs surface, ไม่มี cluster creation, ไม่มี SQL editor → **"เข้าได้แต่ Genie One" ตรงเป๊ะ**

### A3. 🚨 กับดักใหญ่ที่สุด — **additivity + entitlement migration**

> **[C] "entitlements are additive… users benefit from the consumer experience *only if consumer access is their SOLE entitlement*. Assigning additional workspace entitlements overrides the simplified consumer experience."**

**ปัญหา:** วันนี้ (ก่อน migrate) **`users` system group แถม Workspace access + SQL access ให้ทุกคน default**
→ consumer ที่ add แบบเก่า **inherit สิทธิ์ author มาด้วย → lockdown พังเงียบๆ** (business user สร้าง job ได้ ทั้งที่ตั้งใจจะบล็อก!)
> [C] consumer doc: *"Until your workspace migrates… users with consumer access also inherit all entitlements granted to the `users` system group."*

**[C] timeline การเปลี่ยน entitlement behaviour** ([Migrate workspace entitlement control](https://learn.microsoft.com/en-us/azure/databricks/security/auth/system-group-entitlements-migration)):
```
2026-06-15  opt-in ได้
2026-07-27  auto-enable (ถ้ายังไม่ opt-in/out)
2026-09-14  บังคับใช้ทั้งหมด (ไม่มี opt-out)   ← อีก ~2 เดือน
```
หลัง migrate: `users` group = **ไม่มี entitlement** · เลือก entitlement ตอน add คนได้สะอาด · สิทธิ์เดิมย้ายไป clone group `users-clone-<TIMESTAMP>`

> ## 💡 [I] คำแนะนำสำหรับ env ตึงๆ: **migrate workspace นี้เลย (opt-in) อย่ารอ 14 ก.ย.**
> ไม่งั้น Consumer access **ไม่ restrictive จริง** เพราะ `users`-group inheritance
> **pre-work ก่อน migrate [C]:** repoint SCIM/Terraform ไป **account group (ไม่ใช่ system group)** · เลิก nest `users`/`admins` · ตั้ง SCIM ให้ **เก็บ clone group** (ไม่งั้นคนหลุด access)
> **หลัง migrate:** audit clone group — มันได้สิทธิ์กว้างเดิมมา · `biz-consumers-*` **ต้องไม่เป็นสมาชิก clone group**

### A4. Genie 2 เรื่องที่ต้องรู้ [C]
1. **warehouse:** Genie ต้องมี warehouse รันอยู่ → admin เตรียม serverless SQL warehouse ให้ group **CAN USE** (ไม่ใช่ CAN MANAGE) → ใช้ได้แต่มองไม่เห็น/สร้างไม่ได้
2. **Genie ไม่ใช่ security boundary — UC ต่างหาก** → *"users can query other tables by prompting for joins or editing SQL directly"* → **scope UC SELECT ให้แคบ** เฉพาะ gold view ที่ publish · อย่าพึ่ง attached-table list ของ Genie เป็นรั้ว
3. **RLS บังคับใช้เฉพาะ Consumer access ขึ้นไป** (bare account user ไม่ได้) → เหตุผลที่ 2 ที่ต้องใช้ Consumer access ไม่ใช่แค่ account-share

### A5. ปิดประตูหลังสร้าง job [C]
| ประตู | ปิดยังไง |
|---|---|
| **primary** | ไม่ให้ `workspace-access` → ไม่มี DS&E object · ไม่ให้ `allow-cluster-create` |
| **dashboard schedule/subscription** (job-like) | Settings → Notifications → ปิด **Enable dashboard email subscriptions** |
| **API / Terraform** | entitlement enforce ที่ server-side → เรียก Jobs API ก็โดน reject เหมือน UI · เช็คว่า group ไม่มี PAT สิทธิ์สูง / ไม่มี SP ปนใน group |
| **Genie** | Genie สร้าง job ไม่ได้ · lever เดียว = query data (bound ด้วย UC SELECT) |
| **download (nicety)** | Settings → Security → ปิด **SQL results download** |

**✅ ยืนยัน "no jobs / Genie-only": ได้** — Consumer access **เป็น entitlement เดียว** + workspace **migrated แล้ว** + ปิด subscription = Genie One + ดู/รัน dashboard ที่ share + **พิสูจน์ได้ว่าไม่มี surface สร้าง job/cluster/author**

---

## PART B — Budget ต่อทีม

### B1. 🚨 Databricks Budgets — **block ได้เฉพาะ Genie/AI-Gateway · compute ทั่วไป alert อย่างเดียว** [C]
[Create and monitor budgets](https://learn.microsoft.com/en-us/azure/databricks/admin/account-settings/budgets) (อัปเดต 2026-07-14)
budget = scope filter (workspace / resource type / tag) + threshold ≤4 + email alert · account-admin only · วัดเป็น USD **list price**

> **[C] "Per-user overrides and usage blocking is only available for Genie budgets."**

| ประเภท | block ได้? |
|---|---|
| **general compute** (All resource types — serverless SQL warehouse, classic) | ❌ **ALERT อย่างเดียว** |
| **Genie / Unity AI Gateway** | ✅ **BLOCK ได้** — มี checkbox *"Block usage"* หยุด request เมื่อถึง threshold · near-real-time (ไม่ผูกกับ system.billing ที่ช้า) · ⚠️ อาจเกิน threshold นิดหน่อย (request in-flight) |

> ⚠️ **แก้ที่ผมเคยพูดผิด:** ผมเคยบอก "Budgets block ได้" แบบรวมๆ — **ผิด** · block ได้เฉพาะ **LLM/AI-Gateway spend (รวม Genie)** · warehouse/classic = alert เท่านั้น

### B2. Serverless usage policies (budget policies) — attribute ไม่ enforce · ⚠️ Preview [C]
[Attribute usage with serverless usage policies](https://learn.microsoft.com/en-us/azure/databricks/admin/usage/budget-policies) (อัปเดต 2026-07-10)
- แปะ **custom tag** บน serverless usage → tag ลง `system.billing.usage.custom_tags` → **attribution ล้วน ไม่มี cap**
- ⚠️ **coverage gap [C]:** ใช้กับ serverless **notebook, job, pipeline, model serving, Apps, Lakebase** — **ไม่รวม serverless SQL warehouse และ Genie** และ **ไม่แปะ tag บน classic compute**
- ⇒ **budget policy ไม่ tag warehouse ที่ business user ใช้จริง** → ต้อง **tag ที่ warehouse เอง** (warehouse custom tag → `system.billing.usage`) ([Use tags](https://learn.microsoft.com/en-us/azure/databricks/admin/account-settings/usage-detail-tags))

### B3. Genie / LLM cost [C]
[Manage budgets and cost controls for Genie](https://learn.microsoft.com/en-us/azure/databricks/genie/budgets) (อัปเดต 2026-07-14)
- **ตั้งแต่ 2026-07-08 00:00 UTC** Genie = **pay-as-you-go LLM DBU** เกิน free allowance ต่อ user/เดือน
- free = เฉพาะ **identified user ไม่ใช่ SP** · reset วันที่ 1 ของเดือน · budget **เอา free ออกไม่ได้**
- **free = 150 LLM DBU/user/เดือน (~$10.50 US-East list)** — [I-flag] เลข 150 มาจาก pricing page ไม่ใช่ Learn → verify ตาม region
- **cap ต่อ user/ทีม [C]:** budget · Resource type = **Unity AI Gateway** · tag `databricks-product: genie` เดียว · ตั้ง shared threshold (alert) + **per-user threshold (เช่น $30) + Block usage** + override ต่อ group ได้ → **alert ที่ shared, block ที่ per-user**
- **[C] resolution:** ใน budget เดียว group ที่ permissive สุดชนะ · ข้าม budget restrictive สุดชนะ · compute ที่รัน Genie SQL **บิลแยก ไม่อยู่ใน Genie budget**

### B4. ความจริงเรื่อง enforcement สำหรับ population นี้ [I]
| cost component | กลไก | enforce/attribute |
|---|---|---|
| **Genie LLM DBU** | Genie/Unity-AI-Gateway budget + per-user **Block usage** | ✅ **enforce (hard cap near-real-time)** |
| **serverless SQL warehouse** (dashboard + Genie query execution) | **warehouse-level custom tag** → system.billing · general budget = **alert only** | ⚠️ **attribute + alert (block ไม่ได้)** |
| serverless notebook/job/pipeline | budget policy tag (Preview) | attribute — แต่ consumer สร้างไม่ได้อยู่แล้ว (Part A) |

> **[I] warehouse cost block ที่ budget ไม่ได้ → cap ที่ compute config แทน:** 1 serverless SQL warehouse ต่อทีม · **auto-stop สั้น** · **max scaling/cluster count จำกัด** · **tag ต่อทีม** → cap ที่ต้นทาง

### B5. monitoring — เชื่อมกับ Topic 2.1 / Topic 1 [C]
`system.billing.usage` pane เดียว:
- Genie: filter `billing_origin_product = 'GENIE'` · group `identity_metadata.run_as`, `usage_metadata.genie.surface` · join `list_prices`
- warehouse/team: filter **warehouse tag** ใน `custom_tags`
- budget-policy tag (serverless notebook/job) ก็ลง `custom_tags`
→ **spine เดียวกับ Topic 2.1 + chargeback tag เดียวกับ Topic 1**

---

## ✅ Combined recommendation — setup ต่อทีม (เช่น Claims)

1. **migrate workspace เลย** (opt-in อย่ารอ 2026-09-14) — repoint SCIM/Terraform ไป account group · เก็บ clone group · audit clone group หลัง migrate ← **prerequisite ที่ทำให้ Consumer access restrictive จริง**
2. **account group** `biz-consumers-claims` (Entra→SCIM) → grant **Consumer access (`workspace-consume`) เท่านั้น** ไม่ให้ตัวอื่นเลย (additivity!)
3. **UC grant = รั้วจริง:** SELECT เฉพาะ gold schema/view ของทีมนี้ + USE CATALOG/SCHEMA เฉพาะที่ต้อง
4. **compute:** 1 serverless SQL warehouse ต่อทีม · group **CAN USE** · tag `team=claims` · auto-stop สั้น + max scaling จำกัด
5. **hardening:** ปิด dashboard email subscription · ปิด SQL results download
6. **Genie LLM budget (enforce):** budget · Unity AI Gateway + tag `databricks-product: genie` · scope ทีม · **per-user threshold + Block usage** ($30) + group override · shared threshold = alert
7. **warehouse budget (alert):** general budget filter `team=claims` warehouse tag → email alert (block ไม่ได้ → พึ่งข้อ 4)
8. **monitor:** dashboard `system.billing.usage` key ด้วย `team` tag + `billing_origin_product='GENIE'` per-user

## ⚠️ watch-outs
- **additivity ทำ lockdown พังเงียบ** — entitlement ที่ 2 (หรือ `users`-group inheritance ก่อน migrate) เปลี่ยน consumer เป็น author → **migrate + audit**
- **budget block ไม่ได้กับ general/serverless-SQL compute** — เฉพาะ Genie/AI-Gateway LLM → cap warehouse ที่ compute config
- **budget policy ≠ ครอบ warehouse** และเป็น Preview → อย่าพึ่งมันเป็น cost หลักของ population นี้ → ใช้ warehouse tag
- Genie **free 150 DBU เอาออกไม่ได้** · SP ไม่มี free tier + ไม่ยกเว้น billing
- budget วัด **list price** ไม่รวม discount → reconcile กับ rate card
- เลข **150 LLM DBU** จาก pricing page ไม่ใช่ Learn → verify ตาม region

## 🔗 เชื่อม workstream
- **Topic 1:** business user ที่ให้ Consumer access = คน consume dashboard/RLS ของ Topic 1 · warehouse tag = chargeback tag เดียวกัน
- **Topic 2.1:** monitor ใช้ `system.billing.usage` + custom_tags spine เดียวกัน
- **PoC Topic 1 (D+):** ผลว่า user เข้า departmental workspace ได้แค่ไหน → ผูกกับ Consumer access นี้โดยตรง
