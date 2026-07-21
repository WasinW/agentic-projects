# Management & Deployment Options — Databricks Governance + Monitoring

> **สิ่งที่ doc นี้ตอบ (ความสับสนตั้งต้นของ Sin):**
> 1. แต่ละข้อใน checklist ควร manage/deploy ด้วยอะไร — Terraform (IaC), shell, DAB, หรือ scheduler job?
> 2. "การสร้าง SA/SP มันเป็น TF มั้ย? งานของ infra team รึเปล่า? เราทำได้แค่ grant?"
> 3. "Jenkins deploy vs scheduler job (อ่าน CSV → recreate RBAC diff)" — อันไหนถูก?
>
> คู่กับ **[governance-monitoring-web-ui-manual.md](governance-monitoring-web-ui-manual.md)** (Doc 1 = ทำมือ) และ code ที่ `../deploy/`
> Verified against Databricks/Azure docs (July 2026). Generic — ไม่มี AIA identifier.

---

## TL;DR — คำตอบ 3 ข้อ

1. **ไม่มี tool เดียวครอบทุก layer** — เลือกตาม **churn (ความถี่ที่เปลี่ยน) × blast radius**. Structural low-churn → **Terraform**. Workload artifact → **DAB**. High-churn data-access (RLS) → **scheduler reconciliation job**. Shell = escape hatch เท่านั้น
2. **สร้าง SA/SP/network = TF ของ infra team ไม่ใช่ของคุณ.** คุณอยู่ฝั่ง **UC securable** (grant/entitlement/permission). เส้นแบ่งอยู่ที่ **Databricks Access Connector** — infra สร้าง แล้วส่ง resource ID ให้คุณ wire เข้า UC
3. **Jenkins vs scheduler job = ไม่ใช่ either/or** — Jenkins deploy *ตัว low-churn config + โค้ด job*, ส่วน reconcile RBAC รายวันรันเป็น *scheduled job*. ไอเดีย "อ่าน CSV → recreate diff" ของคุณ **ถูกแล้ว** สำหรับ 1.4

---

## 1. Decision framework: layer → churn → modality → owner

| Layer | Churn | Blast | **Modality** | Owner | Code |
|---|---|---|---|---|---|
| 1.1 Identity (users) | constant | low | **SCIM** จาก Entra | IdP/infra | — |
| 1.1 Group shells | low | low | TF `databricks_group` (optional) | you/infra | `terraform/l1_identity.tf` |
| **1.2 Entitlement** | low | **high** | **Terraform** (PR-gated) | you | `terraform/l2_entitlements.tf` |
| 1.3 Object ACL | moderate | med | **DAB** (asset+ACL) · TF สำหรับ warehouse | you | `terraform/l3_permissions.tf` |
| **1.4 Data grant + RLS** | **high** | **high** | structural→TF · per-team→**reconciliation JOB** | you | `terraform/l4_grants.tf`, `jobs/` |
| 2.1 Dashboards ×2 | build-once | low | **DAB** + SQL | you | `dashboards/` |
| SA/SP/network | — | — | **infra team's TF** | **infra** | — |

**หลักคิด:** churn สูง + data-shaped → job/data-driven. churn ต่ำ + declarative + ต้อง review/drift-detect → IaC. blast สูง (security boundary) → ต้อง PR-gate เสมอ (แม้ churn ต่ำ)

---

## 2. 3 กลไก deploy — เทียบตรงๆ

| เกณฑ์ | (a) Terraform | (b) shell + CLI/REST | (c) DAB (Asset Bundles) |
|---|---|---|---|
| Idempotency | ● plan/apply | ○ ต้องเขียน check-then-set เอง | ● declarative |
| Drift detection | ● `terraform plan` = ดีสุด | ○ ไม่มี | ◐ อ่อนกว่า TF (ไม่มี field-level diff) |
| State | ● explicit (คุณคุมเอง = ภาระด้วย) | ● ไม่มี (ไม่มีอะไรพัง = ไม่มี record) | ◐ Databricks จัดการให้ |
| Secrets | ◐ token อาจตกใน state → treat state sensitive | ● env var ล้วน | ● profile/scope ref |
| Review/approval | ● PR เห็น plan diff จริง | ○ bash diff ≠ ผลลัพธ์ | ◐ `bundle validate` |
| Rollback | ◐ revert .tf + apply | ○ เขียน inverse เอง | ◐ redeploy git SHA เก่า |
| Learning curve | ◐ HCL+state (กลาง-สูง) | ● เริ่มง่าย / ○ ทำให้ robust ยาก | ● YAML (DE-friendly) |
| ครอบคลุม governance | ● ครบ (grant/entitlement/permission/warehouse) | ● ครบผ่าน REST แต่ไม่มี guardrail | ◐ job/dashboard/pipeline/schema/volume — **ไม่มี** entitlement/table-grant/row-filter |

**ข้อจำกัด DAB ที่ชี้ขาด (verified):** DAB ทำ **entitlement ไม่ได้, account group ไม่ได้, table-level grant ไม่ได้, row-filter/mask ไม่ได้** → DAB เป็น governance layer ไม่ได้. DAB เก่งเรื่อง **job/pipeline/dashboard** (ครอบ asset + ACL ของมันในตัว)

**Per-primitive:**
- Entitlement → **TF** (DAB ทำไม่ได้ + เป็น security boundary)
- Grant structural (catalog/schema USE) → **TF `databricks_grant`** (granular)
- Grant table/row per-team (churn สูง) → **reconciliation job** (ไม่ใช่ CI)
- Warehouse → **TF** (size/auto-stop = cost governance)
- Job/pipeline/dashboard → **DAB**
- Row filter/mask logic → SQL DDL (TF ไม่มี resource ตรงๆ)

---

## 3. ⚠️ กฎเหล็ก: TF ต้องไม่ตีกับ reconciliation job

- TF จัดการ grant **เฉพาะ `databricks_grant` (granular, per-principal)** ที่ **catalog/schema เท่านั้น**
- **ห้ามใช้ `databricks_grants` (authoritative)** บน securable ที่ **ลูกของมัน** ถูก job แตะ — เพราะ authoritative จะ **overwrite grant ทั้งหมด** ทุกครั้งที่ apply แล้วลบ table-level grant ที่ job สร้างทิ้ง
- job ทำงานที่ **level ต่างกัน** (table/row) กับ **principal ต่างกัน** → namespace ไม่ทับ = ไม่ตีกัน
- **Row filter แยกส่วน:** logic ของ function (`CREATE FUNCTION`) = low-churn → TF/CI; *data ที่ function อ่าน* (team ไหนเห็น row ไหน) = high-churn → control table ของ job. อย่าฝัง membership เป็น literal ใน function

---

## 4. ⭐ 1.4 ลงลึก: reconciliation job (ไอเดีย "อ่าน CSV → recreate diff" ของคุณ)

**Pattern (governance-as-data):** Delta control table เก็บ *desired state* (per-group grant + RLS) → job รายวันอ่าน → อ่าน *actual* → diff → apply **เฉพาะ delta**. Idempotent, drift-correcting, auditable. โค้ดเต็ม: `../deploy/jobs/rls_reconcile.py` + `access_control_ddl.sql`

**ทำไมเหมาะกับ 1.4 (ไม่เอา TF):** TF เขียน mapping-table-driven RLS ไม่ได้, ไม่ครอบ DDL binding, และ reconcile drift เฉพาะตอน apply ครั้งถัดไป — job รายวันจับ out-of-band drift + apply เฉพาะที่ต่าง

**อ่าน actual state ยังไง (2026, verified):**
- object grants → `information_schema.table_privileges / schema_privileges / catalog_privileges / routine_privileges`
- row filter/mask → `information_schema.row_filters / column_masks` (view มีจริง; **column name ยังไม่ verified → `DESCRIBE` ก่อน hardcode**)
- ABAC policy → `SHOW POLICIES ON ...` (ไม่มี `information_schema.policies` confirmed)
- ⚠️⚠️ **`information_schema` ถูก filter ตาม caller** — แม้มี MANAGE ก็เห็นแค่ grant ตัวเอง → **SP ที่รัน job ต้อง OWN securable** (หรือเป็น metastore admin) ไม่งั้นอ่าน actual ไม่ครบ แล้วจะ re-GRANT ซ้ำมั่ว. fallback = `SHOW GRANTS ON <securable>` รันในฐานะ owner
- ⚠️ **`system.access.*` ไม่มี snapshot ของ current grant** — `system.access.audit` เป็น event log (ใช้ทำ audit trail + จับ drift) ไม่ใช่ current state

**Safety guard (สำคัญสุด — อยู่ในโค้ดแล้ว):**
1. **dry-run เป็น default** — log plan แล้วออก ไม่ apply จนกว่า set `apply=true` (รัน dry-run ใน prod สักพักก่อน)
2. **max-revoke circuit breaker** — abort ถ้า plan จะ revoke > threshold หรือ > 20% ของ actual (กัน CSV push พลาดแล้ว mass-revoke)
3. **scope guard** — แตะเฉพาะ principal prefix ที่ manage (`consumer-*`) + catalog ที่ manage. ห้ามแตะ owner/admin/`system`/`hive_metastore`
4. validation (schema + enum + fqn parse + function exists + คู่ GRANT/ROW_FILTER ต้องมี EXECUTE)
5. audit write-back → `reconcile_audit` table
6. run-as SP least-privilege, ordering: grant ก่อน → bind RLS → revoke ท้าย

**Manual job ก็ได้:** ไม่จำเป็นต้อง schedule ทุกวันตั้งแต่แรก — รันเป็น **manual job** (กด Run เมื่อแก้ control table) ก็ pattern เดียวกัน. พอมั่นใจค่อยใส่ schedule

---

## 5. ⭐ ABAC vs per-table row filter (ตอบ "scale ยังไง")

| | Per-table row filter (`SET ROW FILTER`) | ABAC policy (`CREATE POLICY` + governed tag) |
|---|---|---|
| หน่วยคุม | 1 binding / table | 1 policy ที่ catalog/schema → auto ทุก table ที่ tag ตรง |
| onboard table ใหม่ | ต้อง `SET ROW FILTER` ใหม่ | **ใส่ tag** → policy คลุมเอง (0 DDL/table) |
| drift surface | โตเชิงเส้นตามจำนวน table | flat |
| compute floor | UC warehouse / DBR กว้าง | **DBR 16.4+ / serverless เท่านั้น** ⚠️ |
| maturity | GA นาน stable | **GA 2026-05-13** (~2 เดือน) |

**สรุป:** table เดียวต่อ domain (เช่น cost table เดียว) → **per-table row filter** ง่ายกว่า/เสี่ยงน้อยกว่า. หลาย table แชร์ tag/predicate เดียวกัน → **ABAC** ชนะ (onboard = ใส่ tag). **ทั้งคู่ delivery ผ่าน reconciliation job ตัวเดียวกันได้** — วันนี้ปล่อย `SET ROW FILTER`, พรุ่งนี้ `CREATE POLICY`. ⚠️ ABAC GA มี breaking change: view เหนือ table ที่มี ABAC จะ eval เป็น session user (ไม่ใช่ owner)

---

## 6. ⭐ Ownership boundary — ตอบ "SA/SP เป็น TF ของใคร"

> **กฎเดียวจบ:** ถ้าเป็น **Azure Resource Manager (ARM) object → TF ของ infra**. ถ้าเป็น **Unity Catalog securable → ของคุณ**. เส้นแบ่งอยู่ที่ **Databricks Access Connector**

**คุณ *ไม่* Terraform:** Storage Account, Service Principal/Managed Identity, private endpoint/network. คุณ **request** แล้ว **consume**

**Handoff chain (เส้นแบ่งหนา 1 บรรทัด):**
```
── INFRA (ARM) ─────────────────────────────
Storage Account (ADLS Gen2)         ← infra TF
   ▲ RBAC: Storage Blob Data Contributor → connector's MI
Databricks Access Connector          ← infra TF (ARM) — ส่ง resource ID ให้คุณ
════════════ HANDOFF LINE ═══════════════════
Storage Credential                   ← UC securable (metastore admin; ⚠️อาจ delegate ให้คุณ)
External Location                    ← UC securable
Catalog / Schema / Table             ← คุณ
GRANT SELECT ... TO consumer-<team>  ← คุณ
── DATABRICKS / คุณ (UC securable) ─────────
```

**RACI (ย่อ):**

| Resource | Infra | คุณ (DE) |
|---|---|---|
| Storage Account, SP/MI, network/PE | **R/A** | C (request + spec) |
| Access Connector | **R/A** | I (รับ resource ID) |
| Storage credential / external location | R/A (⚠️ อาจ delegate) | C/R |
| Catalog/schema/table | — | **R** |
| **Grant / entitlement / permission** | I | **R/A** |
| Warehouse (size/auto-stop) | I | **R** |
| Job / dashboard | I | **R** |
| Entra group | R/A (IdP) | C (request) |

**2 จุดต้อง confirm กับ org (ไม่ใช่ doc fact):**
1. คุณถือ `CREATE STORAGE CREDENTIAL` / `CREATE EXTERNAL LOCATION` เองมั้ย — insurer ส่วนใหญ่ **centralize** ไว้ที่ admin กลาง แล้ว delegate เฉพาะ external location. ถ้าเป็นงั้น คุณเริ่มที่ catalog
2. คุณสร้าง account group เองได้มั้ย — ปกติ **ไม่ได้** (ต้องเป็น account/workspace admin) → treat เป็น **IAM request** ไปที่ IdP team

**กับดัก network ที่ซ่อนอยู่:** GRANT เป็น control-plane decision — **ไม่เปิด network path**. เวลา consumer query, UC vend credential แล้ว **compute ของ consumer อ่าน ADLS ตรง** — ถ้า storage firewall/PE ไม่รับ compute plane นั้น = **403/timeout ทั้งที่ grant ถูก** → นั่นคือปัญหา **network** (วนกลับไปหา infra) ไม่ใช่ governance

---

## 7. Identity flow (SCIM)

```
Entra ID (source of truth)
   │  SCIM app  OR  Automatic identity management (default หลัง 2025-08-01, รองรับ nested group)
   ▼
Databricks ACCOUNT ── account users + ACCOUNT GROUPS   ← UC resolve ที่ชั้นนี้
   │  assign + entitlement
   ▼
WORKSPACE ── workspace users (+ entitlements)
```
- group เกิดที่ **Entra** → sync ลงมา. คุณ **consume** ไม่ mint
- ⚠️ อย่าใช้ workspace-local group กับ UC (resolve ข้าม workspace ไม่ได้, `is_account_group_member()` มองไม่เห็น)
- ⚠️ object ที่ sync จาก Entra: แก้ฝั่ง Databricks จะโดน reconcile ทิ้ง (Entra ชนะ). ถ้าย้าย workspace-level SCIM → account-level ต้อง **ปิด provisioner เดิม** ไม่งั้นตีกัน

---

## 8. สรุปว่าจะเริ่มยังไง (recommended path)

1. **ยืนยัน boundary กับ infra** — SA/SP/connector ใครทำ, คุณเริ่มที่ credential หรือ catalog (จุด confirm #1)
2. **1.2 Entitlement** — ทำมือผ่าน UI ก่อน (Doc 1) → พอ pattern นิ่ง ย้ายเป็น TF (`l2_entitlements.tf`) เข้า Jenkins
3. **1.4 RLS** — เริ่ม SQL Editor ทำมือ (Doc 1) → พอ team เยอะ/churn สูง ย้ายเป็น control table + `rls_reconcile.py` (dry-run ก่อน)
4. **2.1 Dashboards** — สร้าง UI → export `.lvdash.json` → commit → DAB deploy
5. **Jenkins** เข้ามาเมื่ออยาก PR-gate + multi-env — ไม่ต้องมีตั้งแต่วันแรก. ยังไม่มี TF ในโปรเจกต์ = เริ่มจาก manual/CLI ก่อนได้ (`shell/bootstrap_cli.sh`)

> **Bottom line:** เริ่มทำมือ (Doc 1) พิสูจน์ว่า work → automate ทีละ layer ตาม churn (Doc 2). ไม่ต้องกระโดดไป Jenkins/TF ทันที และ **ไม่ต้องแตะ Azure infra provisioning เลย** (นั่นงาน infra)
