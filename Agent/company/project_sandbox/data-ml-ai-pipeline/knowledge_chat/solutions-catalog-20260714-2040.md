# AIA Cost Dashboard — Solutions Catalogue (ทุก option + design + architecture)

> **วันที่:** 2026-07-14 20:40 · **คู่กับ:** `solutions-compare-matrix-20260714-2040.md` (ตารางเทียบ requirement + เหตุผลที่ตก)
> **Requirement:** ดู `requirements-and-concerns-20260714.md` — R1-R10 / K1-K6 / S1-S7 / Q1-Q8
> **จุดประสงค์:** *validate & verify* — บันทึก **ทุก** option ที่มีอยู่จริงบน Azure Databricks (GA / Preview / Beta ณ 2026-07) **พร้อม architecture** เพื่อให้เห็นว่า *ทำไม* แต่ละอันถึงผ่านหรือตก — ไม่ใช่แค่บอกว่าตก
> **Policy:** ไม่มี code/data จริงของ AIA — generic template ทั้งหมด
> **Scope:** **Power BI ตัดออก** (ยืนยัน 2026-07-14) — แต่ยังบันทึกไว้ใน catalogue เพื่อความครบถ้วน

---

## 0. ⚠️ 3 เรื่องที่ต้องแก้ก่อน — ของเดิมเราเข้าใจผิด

### (a) ชื่อเปลี่ยนหมดในปี 2026 — เอกสารเก่ากว่า มิ.ย. 2026 ใช้ชื่อตายแล้ว
| ชื่อเก่า | ชื่อปัจจุบัน | เมื่อไหร่ |
|---|---|---|
| Genie **Space** | **Genie Agent** | 2026-07-08 |
| **Databricks One** | **Genie One** | เม.ย. 2026 |
| **Delta Sharing** | **OpenSharing** | 2026-06-10 |
| Vector Search | **AI Search** | 2026-06-01 |
| Lakeview | **AI/BI Dashboard** | 2024 |
| DLT | Lakeflow / Spark Declarative Pipelines | 2025 |
| Legacy SQL Dashboard | ☠️ **RETIRED 2026-01-12** | — |

### (b) 🔴 **ข้อเท็จจริงที่สำคัญที่สุดในโจทย์ทั้งหมด — และเราเคยเข้าใจผิด**
มันไม่ใช่เรื่อง *"shared vs individual data permissions"* — มันคือ **entitlement tier**
จาก [AI/BI administration guide](https://learn.microsoft.com/en-us/azure/databricks/ai-bi/admin/) capability matrix:

| ความสามารถ | **Account member** | **Consumer access** | **Databricks SQL access** |
|---|---|---|---|
| เปิด/รัน dashboard | ✓ | ✓ | ✓ |
| เปิด/รัน Genie Agent | ✓ | ✓ | ✓ |
| **บังคับใช้ row-/column-level security** | **✗** | **✓** | **✓** |
| query warehouse ผ่าน BI tool | ✗ | ✓ | ✓ |
| สร้าง/แก้ dashboard | ✗ | ✗ | ✓ |

> ## 🚨 **Account user เพียวๆ ไม่ได้ RLS บังคับใช้**
> ทุก design ที่บอกว่า *"share ให้ account user + UC row filter"* ยืนอยู่บน **✗ ที่ document ไว้ชัดเจน**
> ตัวปลดล็อกคือ **Consumer access entitlement** — ซึ่งเป็น **workspace entitlement** (view-only) และ **admin ฝั่งเขา grant เองได้**

### (c) 🔴 **Genie ไม่ได้ "ตาย" อย่างที่เราเคยเขียน**
[Create and manage a Genie Agent](https://learn.microsoft.com/en-us/azure/databricks/genie/set-up) เขียนชัด:
> *"You can also specify certain users or groups (**including all account users**) to share with…"*
> *"**To share with all account users:** Click Share → Select **All account users**"*

⚠️ **แต่** หน้า AI/BI admin ยังมีประโยคเก่า *"…can only be granted to workspace users"* → **เอกสารของ Microsoft ขัดกันเอง (ทั้งสองหน้าอัปเดต 2026-07-08)** → **ต้องเทสจริง อย่าเดา**
👉 skill `databricks-uc-governance-sharing` ที่เขียนว่า *"Genie BLOCKED — do not propose"* → **ต้องแก้**

*(หมายเหตุ: ในเคส AIA เรื่องนี้ **ไม่เปลี่ยนผลลัพธ์** — Genie ตายด้วย R5 อยู่ดี แต่ต้องบันทึกไว้ให้ถูก เพราะโปรเจกต์อื่นจะได้ไม่ใช้ข้อมูลผิด)*

---

## 1. 🧬 The Identity Tier Model — กระดูกสันหลังของทุก option

```
TIER 0  Anonymous / external        ไม่มี Databricks identity เลย
        └─ เข้าถึงได้ทาง: external embedding (SP-minted token)
           หรือ artifact ที่เรา generate แล้วส่งให้ (PDF / HTML / Excel / file)

TIER 1  Account user                Entra principal ที่ register ใน Databricks ACCOUNT
        └─ ✓ เปิด published dashboard + Genie Agent ผ่าน URL ได้
        └─ ✗ ไม่ได้ UC row-filter / column-mask บังคับใช้   ← 🚨 กับดักใหญ่
        └─ ✗ มองไม่เห็น workspace-bound securable (widget ว่างเปล่า เงียบๆ)
        └─ ✗ ต่อ warehouse / BI tool ไม่ได้

TIER 2  Consumer access entitlement  account user + assign เข้า workspace แบบ view-only
        └─ ✓ RLS/CLS บังคับใช้   ✓ BI tool ได้   ✗ สร้างอะไรไม่ได้
        └─ ⭐ นี่คือ tier ที่ design "share ข้าม workspace" เกือบทุกอันต้องการจริงๆ

TIER 3  Databricks SQL access        workspace member เต็มตัว สร้าง/แก้ได้
```

**ข้อจำกัด R3 ("client ต้องไม่เป็นสมาชิก coredata") = หัวใจของเกม**
⚠️ ระวังความแตกต่าง: **Tier 2 ใน workspace ของ*เขาเอง* = ฟรี ไม่ผิดอะไร (ส่วนใหญ่มีอยู่แล้ว)** · **Tier 2 ใน coredata = สิ่งที่ห้าม**

---

## 2. 🧱 กำแพง 4 ด้านของ AIA — ทุก option ต้องผ่านให้ครบ

```
        ┌─────────────────────────────────────────────────────────────┐
        │  R1  gold table + pipeline ต้องอยู่ coredata DEV เท่านั้น      │
        │  R2  client เข้าจาก departmental PROD เท่านั้น                │
        │  R3  client ไม่เป็นสมาชิก coredata                            │
        │  R4  เรา deploy อะไรลง departmental workspace ไม่ได้           │
        │  R5  🚨 PROD → DEV ไม่ถึงกัน (network) + ห้ามย้าย data ข้าม env │
        │  R5b 🚨 browser ของ client ก็เปิด URL ของ DEV ไม่ได้            │
        └─────────────────────────────────────────────────────────────┘
```

**ตัวกรอง 3 ชั้นที่ฆ่า option:**
```
❶ ต้องมี live path (browser หรือ compute) จาก PROD → DEV ไหม?   → R5 / R5b ฆ่า
❷ ต้องเอา data ไปวางในที่ที่ PROD อ่านได้ไหม?                     → R5 ฆ่า
❸ ต้อง deploy object ลง departmental workspace ไหม?             → R4 ฆ่า  (เว้นแต่ *เขา* ทำเอง)
```
**เหลือรอดได้ทางเดียว: ไม่ต้องทั้ง ❶ ❷ ❸ → ARTIFACT ที่ render ใน DEV แล้วส่งถึง "คน"**

---
---

# FAMILY A — AI/BI Dashboard (= Lakeview)

## A1. Published dashboard — **"Share data permissions"** (ค่า default)
**Status:** GA · share to all account users ผ่าน SDK/REST GA **2026-03-26**

publish dashboard → ได้ URL แบบ view-only · **credential ของ publisher ถูกฝัง** → query ของ *ทุกคน* รันในนามของ publisher

```
coredata DEV                                  departmental PROD user
┌──────────────────────────────┐
│ Dashboard (published)        │◄──── HTTPS ──── 🌐 browser (Entra SSO)
│   embed_credentials = TRUE   │                 identity: ACCOUNT USER (Tier 1)
│        │                     │
│        ▼                     │
│ SQL Warehouse (ของเรา) ───────┼──► query รันในนามของ **PUBLISHER**
│   💰 เราจ่าย DBU ทั้งหมด        │     RLS ประเมินในนามของ **PUBLISHER** 🚨
│        │                     │
│        ▼                     │
│ UC table  gold.cost_wide     │
└──────────────────────────────┘
object อยู่ DEV · compute อยู่ DEV · ไม่มีอะไรลง PROD
```
| | |
|---|---|
| **ต้องการ** | live browser path → DEV URL · viewer register ใน account · catalog ต้องไม่ workspace-bound |
| **จ่ายค่า compute** | **เรา** |
| **🚨 Gotcha** | **นี่คือรูรั่ว** — ทุกคนเห็น result set เต็มของ publisher · UC row filter ประเมินในนามของ*เรา* · **และนี่คือ default** |
| **AIA** | ❌ **ตาย R5b** (browser เข้า DEV ไม่ได้) + K1 (Sarunya กลัว link) |

---

## A2. Published dashboard — **"Individual data permissions"**
**Status:** GA · `embed_credentials = false`

```
coredata DEV                                  departmental PROD user
┌──────────────────────────────┐
│ Dashboard (published)        │◄──── HTTPS ──── 🌐 browser
│   embed_credentials = FALSE  │                 identity: VIEWER
│        │                     │
│        ▼                     │
│ SQL Warehouse (ของเรา) ───────┼──► compute identity: **PUBLISHER** (เราจ่าย)
│                              │     data identity:    **VIEWER**
│        ▼                     │     RLS ประเมินในนาม viewer — ✅ *ถ้าเป็น Tier 2+*
│ UC table + ROW FILTER        │
└──────────────────────────────┘
```
> *"Compute access is always granted by the publisher's credentials"* → viewer **ไม่ต้องมี `CAN USE`** บน warehouse ของเรา

| | |
|---|---|
| **ต้องการ** | viewer ต้องมี `SELECT` บน table + `USE CATALOG` + `USE SCHEMA` + **`GRANT EXECUTE` บน row-filter function** (grant ที่คนลืมบ่อยที่สุด) **และต้องเป็น Tier 2 ขึ้นไป RLS ถึงจะทำงาน** |
| **🚨 Gotcha** | **The Tier-1 trap** — account user เพียวๆ **ไม่ได้ RLS** (capability matrix ✗) · **workspace-bound catalog → widget ว่างเปล่า ไม่มี error** |
| **AIA** | ❌ **ตาย R5b** — และแม้ browser เข้าได้ ก็ยังติด Tier-1 trap ถ้า admin เขาไม่ให้ Consumer access |

---

## A3. ⭐ **หนึ่ง dashboard ต่อหนึ่งทีม** — dataset pre-filtered
**Status:** GA (ประกอบจาก GA primitive ล้วน — ไม่มี preview เลย)

**เลี่ยงคำถาม RLS ทั้งหมด** — N dashboard, แต่ละอันมี `WHERE tag_team = 'x'` ฝังใน dataset → credential ของ publisher จึง **ถูกต้องโดยโครงสร้าง**

```
coredata DEV
┌───────────────────────────────────────────────┐
│ dash_team_a  (WHERE tag_team='team_a')  ──┐   │
│ dash_team_b  (WHERE tag_team='team_b')  ──┤   │──► share ให้ account group
│ dash_team_c  (WHERE tag_team='team_c')  ──┘   │    ของทีมนั้น *เท่านั้น*
│        ทุกอัน embed_credentials = TRUE          │
│                   ▼                           │
│  SQL Warehouse (ของเรา)                        │
└───────────────────────────────────────────────┘
```
| | |
|---|---|
| **ต้องการ** | ไม่มีอะไรเกินจาก A1 — script ผ่าน Lakeview API / DAB |
| **✅ ข้อดี** | **ไม่พึ่ง RLS → ไม่พึ่ง entitlement tier เลย** · Tier 1 ก็พอ |
| **🚨 Gotcha** | N dashboard ต้อง sync (แก้ด้วย 1 template + loop) · **share-list กลายเป็น security boundary** · ไม่ scale เกิน ~20 ทีม |
| **AIA** | ⚠️ **ตัว dashboard เองตาย R5b** — **แต่** ⭐ **นี่คือรากฐานของ A5 (subscription)** ซึ่งเป็นทางรอด: มันคือ*เหตุผลเดียว*ที่ email PDF/Excel ต่อทีมได้อย่างปลอดภัย |

---

## A4. Dashboard **export / import** (`.lvdash.json`) — *เดิมชื่อ "Option D+"*
**Status:** GA

```
coredata DEV              (ไฟล์: email/git/Volume)        departmental PROD
┌──────────────┐                                     ┌───────────────────┐
│ dashboard    │──► .lvdash.json ──────────────────► │ dashboard (ของเขา)│
└──────────────┘                                     │        │          │
                                                     │        ▼          │
     UC table (ใน catalog ของ DEV) ◄─── live query ──│ warehouse ของเขา  │
                    ▲                                │ 💰 เขาจ่าย!        │
                    └─── 🚨 R5: PROD วิ่งมาไม่ถึง ─────└───────────────────┘
```
| | |
|---|---|
| **💰** | **เขาจ่าย** — **นี่เป็น option เดียวใน catalogue ที่ได้ chargeback จริง** (irony: dashboard เรื่อง cost แต่ IT จ่ายค่า query ให้ทุกคน) |
| **ต้องการ** | metastore เดียวกัน · `GRANT SELECT` · catalog isolation = `OPEN` · **และ PROD ต้องอ่าน DEV ได้** |
| **🚨 Gotcha** | **`.lvdash.json` มีแค่ query text + widget config — ไม่เคยมี data** → import ไปฝั่งเขา = **"table not found" เสมอ** |
| **AIA** | ☠️ **ตาย R5** — dashboard ที่ import ไปยังต้อง live query กลับมาที่ DEV **นี่คือสาเหตุที่ D+ ตาย** |

---

## A5. ⭐⭐ **Scheduled subscription** — PDF + CSV/TSV/**Excel** attachment
**Status:** GA · **🆕 tabular attachment เพิ่มมา เม.ย. 2026** · PDF page-selection เม.ย. 2026 · custom subject มี.ค. 2026

```
coredata DEV                                    departmental PROD user
┌────────────────────────────┐
│ Schedule (cron, monthly)   │
│   │                        │
│   ▼                        │
│ Warehouse render snapshot  │  รันในนามของ **SCHEDULE OWNER**
│   │                        │  (ไม่ใช่ per-recipient!)
│   ▼                        │
│ PDF / CSV / XLSX ──────────┼──── 📧 SMTP ───► 📥 inbox
└────────────────────────────┘                  identity: **ไม่มีเลย (Tier 0)**
                                                มันคือ email address ไม่ใช่ principal
```
| | |
|---|---|
| **✅ ต้องการฝั่ง viewer** | **ไม่มีอะไรเลย** — ไม่ต้องเป็น Databricks user ด้วยซ้ำ |
| | *"You can configure account users, **distribution lists**, and **external users (such as partners or clients)** as email notification destinations."* |
| **🚨 Gotcha ที่คมที่สุดใน catalogue** | **snapshot ถูก render ครั้งเดียว ในนาม identity เดียว — ไม่ได้ filter per-recipient** → ส่ง PDF รวมทุกทีมให้ mailing list ผสม = **data leak โดยโครงสร้าง** |
| | **⇒ ต้องส่งจาก per-team dashboard (A3) เท่านั้น — ห้ามมีข้อยกเว้น** |
| **caps** | attachment **≤ 9 MB** · subscriber ≤ 100 · Excel ≤ 100k rows · chart widget ≤ 10k rows · workspace admin ปิด subscription ทั้ง workspace ได้ด้วย toggle เดียว (sub เดิม pause เงียบๆ) |
| **AIA** | ✅✅ **ผ่านทุกข้อ** — ไม่ต้องมี live path, ไม่ต้อง deploy อะไรลง PROD, ไม่มี data ลงระบบ PROD, isolation by construction **= ชั้น 0 ของ solution** |

---

## A6. **External embedding** (สำหรับ external user)
**Status:** **GA — มี.ค. 2026 (Azure)** · `hideDatabricksLogo` มี.ค. 2026
เป็น **ทาง interactive ทางเดียวที่รองรับ Tier 0**

```
🌐 browser ของ user
     │ (1) login เข้า *แอปของเรา* (IdP ของเรา ไม่ใช่ Entra/Databricks)
     ▼
┌────────────────────────────┐
│ APP SERVER ของเรา          │──(2) client_credentials + SP secret ──►┐
│ ⚠️ ต้อง host เองที่ไหนสักที่ │◄─ OAuth token ───────────────────────┤
│    ← นี่คือตัวตัดสิน         │                                        │
│                            │──(3) GET /api/2.0/lakeview/dashboards/ │
│                            │      {id}/published/tokeninfo           │
│                            │      ?external_viewer_id=&external_value=│
│                            │◄─(4) user token แบบ scoped แคบ ────────┤
└────────┬───────────────────┘                            coredata DEV │
         │ (5) token → browser                       ┌─────────────────▼──┐
         ▼                                           │ Published dashboard│
   <DatabricksDashboard/>  ─────────────────────────►│ Warehouse (ของเรา) │
   render ในหน้าเว็บของเรา                             │ filter ด้วย        │
                                                     │ __aibi_external_value
                                                     └────────────────────┘
```
row filtering ทำโดย**เรา** ด้วยการ inject `__aibi_external_value` เข้า dataset SQL:
```sql
SELECT * FROM cost_wide WHERE tag_team = __aibi_external_value
```
| | |
|---|---|
| **ต้องการ** | ⚠️ **application server ที่เรา host เอง** ← ข้อนี้คือตัวตัดสิน · workspace admin ต้อง allowlist domain |
| **🚨 Gotcha** | **UC RLS ถูก bypass ทั้งหมด** → security ยุบเหลือ *"app server ผมส่ง external_value ถูกมั้ย"* = **เรา re-implement RLS ใน application code** (สำหรับลูกค้าประกันที่ regulated — ต้องพูดออกมาดังๆ) · `external_viewer_id` ลง audit log → **ห้ามมี PII** · rate limit 20 loads/sec · **download เปิด default** · **Ask Genie ใช้ไม่ได้ใน external embedding** |
| **AIA** | ❌ **ตาย R4/R5b** — ต้องมี app server ของเราที่ user PROD เข้าถึงได้ **และ** browser ยังต้องโหลด iframe จาก DEV URL |

---

## A7. **Basic embedding** (iframe ใน internal portal)
**Status:** GA
```
Internal portal (SharePoint / intranet)
   │  <iframe src="https://<DEV>.azuredatabricks.net/embed/dashboardsv3/<id>">
   ▼
coredata DEV ── Entra SSO ใน iframe ──► viewer ต้องเป็น account user (Tier 1+)
```
| | |
|---|---|
| **🚨 Gotcha** | **แทบไม่ได้อะไรเลยเมื่อเทียบกับส่ง hyperlink เฉยๆ** — มันแก้แค่ *chrome* ไม่ได้แก้ *identity* · SSO ใน iframe = แหล่งกำเนิด bug "ของผมใช้ได้นี่" (Safari ITP, strict cookie) |
| **AIA** | ❌ **ตาย R5b** — iframe ยังโหลดจาก DEV URL |

---

## A8. Dashboard peripherals (ตัวเสริม ไม่ใช่ solution เดี่ยว)
| Feature | Status | เกี่ยวมั้ย |
|---|---|---|
| **Custom Vega-Lite viz** | 🟡 Public Preview (มิ.ย. 2026) | presentation อย่างเดียว — ไม่กระทบ identity/compute |
| **Dashboard relationships** (multi-fact) | 🟡 Public Preview (ก.ค. 2026) | modelling อย่างเดียว |
| **Local metric views** | 🟡 Public Preview | modelling ใน dashboard ไม่ต้อง publish ขึ้น UC |
| **Publish ด้วย service principal credentials** | ✅ GA (เม.ย. 2026) | 💡 มีประโยชน์จริง — ตัด dashboard ออกจาก credential ของ*คน* → กัน "คน author ลาออก dashboard ตาย" |
| **Bookmarks / shared filter combos** | GA (มิ.ย. 2026) | cosmetic |
| **Import Power BI/Tableau → AI/BI (Genie Code)** | ✅ GA (ก.ค. 2026) | ทางเข้า ไม่ใช่ทางออก |
| ~~Legacy SQL dashboard~~ | ☠️ **RETIRED 2026-01-12** | **อย่าให้ใครอ้างถึง** |

---
---

# FAMILY B — Genie

## B9. **Genie Agent** share ให้ all account users
**Status:** GA · **🆕 pay-as-you-go pricing ตั้งแต่ 2026-07-08**

```
coredata DEV
┌────────────────────────────────────────┐
│ Genie Agent (≤ 30 UC tables)           │◄── 🌐 browser, Entra SSO
│   compute credential = ฝังของ AUTHOR    │    identity: account user / consumer
│        │                               │
│        ▼                               │
│ Pro / Serverless SQL Warehouse ────────┼──► compute identity: **AUTHOR** (เราจ่าย)
│   💰 เราจ่าย DBU + LLM DBU              │     data identity:    **END USER** ✓
│        │                               │
│        ▼                               │
│ UC tables + row filters ───────────────┼──► "คำถามเกี่ยวกับ data ที่เขาไม่มีสิทธิ์
└────────────────────────────────────────┘     จะได้ empty response"
```
| | |
|---|---|
| **ต้องการ** | UC tables (≤30) · Pro/serverless warehouse · account admin เปิด partner-powered AI ทั้ง account **และ** workspace · end user ต้องมี `SELECT` **และ Tier 2** |
| **🚨 Gotcha ใหญ่** | **Genie query table ที่เราไม่ได้ใส่ก็ได้** — *"users can query other tables by prompting for joins or editing SQL directly"* → **Genie Agent ไม่ใช่ security boundary · UC ต่างหากที่เป็น** |
| **💸 Gotcha 2** | **cost model เปลี่ยน 2026-07-08 → pay-as-you-go LLM DBU** (ฟรี 150 DBU/user/เดือน ≈ $10.50) — เอา NL interface แบบไม่จำกัดไปจ่อ dashboard เรื่อง cost นี่เป็นวิธีสร้าง cost ที่ตลกดี → **ตั้ง Budget** (GA 2026-07-06, block ได้) |
| **AIA** | ❌ **ตาย R5b** (browser เข้า DEV ไม่ได้) — *แต่ให้บันทึกว่า "Genie ตายเพราะ network ไม่ใช่เพราะ account-user ใช้ไม่ได้"* |

## B10. Genie iframe embedding — **GA มิ.ย. 2026** → ❌ เหมือน A7 (แก้ chrome ไม่แก้ identity) · **ไม่มี "Genie external embedding"** เทียบเท่า A6
## B11. **Genie Conversation API** — **GA เม.ย. 2026**
```
app ที่ไหนก็ได้ (รวมทั้งใน PROD) ──POST /api/2.0/genie/spaces/{id}/start-conversation
                                  Authorization: Bearer <token ของ principal ใน DEV>
                                  ▼
                            coredata DEV ──► Genie ──► warehouse ──► UC
```
> ⭐ **ข้อสังเกตสำคัญ:** *"ไม่มีกำแพง network หรือ API ระหว่าง workspace เลย — กำแพงคือ **การครอบครอง credential** ล้วนๆ"* — **ยกเว้นในเคส AIA ที่ network ถูกบล็อกจริง (R5)** → ❌ ตาย
## B12. **Genie One** (account-level) — **GA เม.ย. 2026**
```
                 ┌─────────────────────────────────┐
PROD user ──────►│  Genie One  (ACCOUNT level)     │ ← URL เดียว หน้า home เดียว
 (Consumer       │  cross-workspace search         │
  access)        │  ┌─────────┬─────────┬────────┐ │ object ยัง *อยู่* ที่ DEV;
                 │  │ dash    │ genie   │ app    │ │ Genie One เป็นแค่ launcher
                 │  └────┬────┴────┬────┴───┬────┘ │ ที่ federate
                 └───────┼─────────┼────────┼──────┘
                         ▼         ▼        ▼
                    object + warehouse ใน DEV (DEV จ่าย)
```
💡 **นี่คือคำตอบเชิง presentation ของ K3** *"ให้ user ใน PROD เจอของใน DEV โดยไม่ต้องเข้า workspace DEV"* — **แต่ยังต้องมี live path → ❌ ตาย R5b**

## B13. Genie peripherals
| Feature | Status | หมายเหตุ |
|---|---|---|
| **Genie One scheduled tasks** (NL task → email ผลลัพธ์ประจำ) | 🟡 Public Preview (เม.ย. 2026) | เป็นกลไก notify รายเดือนได้จริง — ❌ **แต่ผู้รับต้องเป็น Genie user ใน DEV → ตาย R3** |
| ⚠️ **Share Genie Agent ผ่าน OpenSharing** | 🔴 **Beta — 2026-06-17** | **ใหม่และตรงประเด็นมาก** — สร้าง **snapshot ณ จุดเวลาหนึ่ง** ของ data asset + instruction → ผู้รับ **mount แล้วได้ Genie Agent ของตัวเอง** ใน metastore ตัวเอง = **"ให้ Genie ที่เขาเป็นเจ้าของและจ่ายเอง"** ทางเดียว · snapshot ⇒ **ไม่ live** · ❌ **แต่ยังคือการย้าย data ข้าม env → ตาย R5** |
| Genie app for **Microsoft Teams** | 🔴 Beta (มิ.ย. 2026) | ถามข้อมูลใน Teams — delivery surface ที่ไม่ต้องใช้ browser |
| Genie app for **Slack** | 🟡 Public Preview (มิ.ย. 2026) | |
| **Genie documents** (ร่างเอกสารจาก conversation) | GA (พ.ค. 2026) | artifact path แบบ Tier-0 |
| Genie mobile | 🟡 Public Preview (พ.ค. 2026) | |
| ⚠️ **Ask Genie บน published dashboard** | ✅ **GA (ก.ค. 2026) — เปิด default!** | 🚨 **publish dashboard ปุ๊บ viewer ได้กล่องถาม NL ใส่ data เราทันที ไม่ว่าเราจะตั้งใจหรือไม่ — ต้อง audit** |

---
---

# FAMILY C — Databricks Apps

## C14. App — **system/app authorization** (service principal)
**Status:** GA · Git-backed deploy GA เม.ย. 2026
```
coredata DEV
┌──────────────────────────────────────┐
│ App (Streamlit/Dash/Flask/Node)      │◄─── 🌐 browser
│   dedicated SERVICE PRINCIPAL        │     viewer ต้องมี CAN USE บน app
│   (auto-provision, immutable)        │
│        │ DATABRICKS_CLIENT_ID/SECRET │
│        ▼                             │
│ SQL Warehouse ───────────────────────┼──► **ทุก query รันในนาม SP**
│        ▼                             │     🚨 ทุก viewer เห็น data เหมือนกันเป๊ะ
│ UC tables                            │
└──────────────────────────────────────┘
```
> *"All users who interact with the app share the same permissions defined for the service principal… it doesn't support user-level access control."*

**🚨 ไม่มี per-user isolation เลย** — ถ้าต้องการ row-level ต้องเขียนเอง → **app กลายเป็น security boundary**
**💸 Apps bill 24/7 ไม่มี scale-to-zero** (Medium 0.5 DBU/hr · Large 1 DBU/hr) **+ warehouse DBU อีกต่างหาก**
**AIA:** ❌ **ตาย R4** (ต้อง deploy) + **R5b** + cost 2-4×

## C15. App — **user authorization** (on-behalf-of token forwarding)
**Status:** ⚠️ **PUBLIC PREVIEW** (ยังอยู่ ณ ก.ค. 2026)
```
coredata DEV
┌───────────────────────────────────────────────────┐
│ App                                               │◄── 🌐 browser (user)
│  Databricks inject header:                        │
│    x-forwarded-access-token  ◄── token ของ USER   │
│                                                   │
│  โค้ดของเรา *ต้อง* อ่านมันเอง:                       │
│    tok = headers.get('x-forwarded-access-token')  │
│    sql.connect(..., access_token=tok)             │
│         │                                         │
│         ├── ถ้า forward ──► query ในนาม USER (RLS ✓)
│         └── ถ้า **ลืม** ──► query ในนาม **SP** = **DATA เต็ม** 🚨🚨
│              ↑ ไม่ error ไม่เตือน — leak ที่หน้าตาเหมือน app ทำงานปกติ
└───────────────────────────────────────────────────┘
```
**🚨 silent fallback = จุดตายของ option นี้** · user consent **ถอนคืนไม่ได้** · **ยัง Public Preview**
> 💬 ประโยคที่ใช้ได้จริงในห้องประชุม: *"policy ที่ห้าม dashboard ซึ่ง **GA** แต่อนุญาต app auth mode ที่เป็น **Preview** — มันขัดกันเองครับ"*

**AIA:** ❌ ตาย R4 + R5b + Preview

## C16. App เป็น **static file host** — GA
```
Job ใน DEV ──► render report.html ──► App serve เป็น static asset
                                       ไม่มี query path เลยตอน request
```
**❌ dominated** — bill 24/7 เพื่อ serve ไฟล์ ทั้งที่ **UC Volume / blob / SharePoint ทำได้ ~$0** (→ G28) · **และยังตาย R4/R5b อยู่ดี**

---
---

# FAMILY D — Sharing & Unity Catalog

## D17. ⭐ **UC cross-workspace GRANT** (metastore เดียวกัน)
**Status:** GA · **option ที่ถูกมองข้ามที่สุดใน catalogue**

ไม่ใช่ "feature การ share" ด้วยซ้ำ — มันคือข้อเท็จจริงว่า **1 UC metastore ครอบทุก workspace ใน region** → `GRANT SELECT` ให้ account group แล้ว table ก็ไปโผล่ใน Catalog Explorer ของ workspace B **ไม่มี object ไม่มี protocol ไม่มี copy**

```
        ┌──────────── UC metastore เดียว (ต่อ region) ────────────┐
        │                                                        │
coredata DEV                                     departmental PROD
┌──────────────┐                              ┌────────────────────┐
│ pipeline     │─write─► catalog.gold.cost_wide ◄──read──│ warehouse ของเขา│
│ compute เรา   │        + ROW FILTER          │ 💰 เขาจ่าย!         │
└──────────────┘        + COLUMN MASK          │ notebook ของเขา    │
                                               │ BI tool ของเขา     │
              GRANT SELECT TO `client-team-a`  └────────────────────┘
                                                (Tier 3 ใน workspace ตัวเอง — มีอยู่แล้ว)
                          ▲
              🚨 R5: network บล็อก + จะไม่เปิด shared แม้อยู่ใน UC เดียวกัน
```
| | |
|---|---|
| **✅ ข้อดีมหาศาล** | เขาเป็น **workspace user เต็มตัวใน workspace ตัวเอง** → **RLS/CLS ทำงาน native** ไม่มี entitlement ambiguity ไม่มี publish-mode footgun ไม่มี ✗ ใน capability matrix · **💰 เขาจ่าย DBU เอง = chargeback จริง** |
| **ต้องการ** | metastore + region เดียวกัน · isolation `OPEN` · `USE CATALOG` + `USE SCHEMA` + `SELECT` + **`EXECUTE` บน filter function** |
| **AIA** | ☠️ **ตาย R5** — PROD compute อ่าน DEV data ไม่ได้ (network) **และจะไม่เปิด shared แม้อยู่ใน UC เดียวกัน** · **นี่คือ option ที่เจ็บที่สุดที่ต้องทิ้ง** — ถ้า policy เปลี่ยน นี่คืออันแรกที่กลับมา |

## D18. **Workspace-catalog binding** — ไม่ใช่ option แต่เป็น **กับดักที่ต้องเคลียร์**
```
isolation mode:
  OPEN       ← default ของ catalog ที่สร้างเอง — ทุก WS ใน metastore เข้าถึงได้
  ISOLATED   ← เข้าถึงได้เฉพาะ WS ที่ bind ไว้  ⚠️
  READ_ONLY  ← bind แล้วอ่านได้ เขียนไม่ได้
```
🚨 **default workspace catalog ที่ระบบสร้างให้อัตโนมัติ = workspace-bound โดย default**
> *"Account users cannot access data from workspace-bound securables"*

**failure mode: dashboard โหลดขึ้น layout ขึ้น แต่ทุก widget ว่างเปล่า ไม่มี error ไม่มีข้อความบอกว่าเป็นเพราะ binding** ← **failure ที่ debug ยากที่สุดในโจทย์นี้**
`databricks workspace-bindings get-bindings catalog <cat>` → `databricks catalogs update <cat> --isolation-mode OPEN`

## D19. **OpenSharing** (เดิม Delta Sharing) — Databricks-to-Databricks
**Status:** GA · **เปลี่ยนชื่อ 2026-06-10** · 🆕 cross regulatory domain (PuP มิ.ย. 2026) · **SecureConnect** share จากหลัง firewall (PuP มิ.ย. 2026) · foreign Iceberg ใน share (PuP เม.ย. 2026)
```
Metastore 1 (เรา)                    Metastore 2 (เขา — คนละ metastore)
┌────────────────────┐              ┌──────────────────────┐
│ SHARE "cost_share" │─ D2D proto ─►│ CATALOG (mount, RO)  │
│  └ cost_wide       │  ไม่ copy data │        │             │
│  RECIPIENT = เขา   │  เขาอ่าน storage │        ▼             │
└────────────────────┘  ของเราด้วย    │  compute ของเขา 💰    │
        │               short-lived  └──────────────────────┘
        ▼               credential
   ADLS (ของเรา) ◄──────────────────
```
| **🚨 Gotcha ที่ฆ่า "ก็แค่ Delta Share สิ"** | **granularity = share ไม่ใช่ row** — **row filter / column mask ไม่เดินทางผ่าน share** → ถ้าต้อง per-team row ต้อง **materialize table (หรือ share) แยกต่อ 1 recipient** |
|---|---|
| **AIA** | ❌ **ตาย 2 ชั้น**: metastore เดียวกัน ⇒ offer ไม่ได้ (และถ้าคนละ metastore ก็ยัง **ตาย R5** เพราะเป็นการย้าย data ข้าม env) |

## D20. **OpenSharing — open protocol** (recipient ไม่ใช่ Databricks) — GA
recipient ใช้ pandas/Spark/Trino/BI tool ผ่าน credential file · **ไม่ต้องมี Databricks account เลย (Tier 0 จริง)**
🚨 **เรากำลังแจก bearer credential file** — rotation / revocation / blast radius เป็นความรับผิดชอบเรา
**AIA:** ❌ **ตาย R5** (ย้าย data ข้าม env)

## D21. **Clean Rooms** — GA
```
data ฝ่าย A ──┐
              ├──► Clean Room (Databricks-managed, isolated) ──► output แบบ aggregate
data ฝ่าย B ──┘      รันได้เฉพาะ notebook ที่ approve
```
**❌ REJECTED** — ~**$7,500/เดือน** (เทียบ $10-50) · ให้ **table ไม่ใช่ dashboard** · approve ทีละ notebook
> **Clean Rooms แก้ปัญหา "องค์กรสองฝ่ายไม่ไว้ใจกัน" — เอามาย้าย cost dashboard ระหว่างสองทีมในบริษัทเดียวกัน = เอาตู้เซฟธนาคารมาเก็บ Post-it** · บันทึกไว้ ปฏิเสธไป

## D22. **Lakehouse Federation** — *workspace B federate มาหา workspace A ได้มั้ย?*
**คำตอบ: ไม่ได้ — และควรรู้ว่าทำไม** Lakehouse Federation ให้ Databricks query ระบบ**ภายนอก** (PostgreSQL, Snowflake, Redshift, BigQuery, Iceberg…) **Databricks workspace ไม่ใช่ federatable source ของ Databricks workspace อีกตัว**
- metastore เดียวกัน → ไม่ต้อง federate (D17 ให้อยู่แล้ว)
- คนละ metastore → ใช้ OpenSharing (D19)

🆕 **ที่ใกล้เคียงและใช้ได้จริง:** **publish UC catalog → Microsoft Fabric เป็น read-only mirrored catalog (Public Preview, 2026-06-18)** → ดู H34

---
---

# FAMILY E — Governance primitives (modifier ไม่ใช่ delivery)

ไม่ได้ย้าย data ไปไหน — เป็นตัวกำหนดว่า **เมื่อ delivery mechanism ทำงานแล้ว viewer เห็นอะไร** บันทึกไว้เพราะเอกสารปฏิเสธที่ดีต้องแสดงว่าพิจารณาแล้ว

| primitive | status | พฤติกรรม |
|---|---|---|
| **UC row filters** | GA | SQL UDF คืน boolean · `SET ROW FILTER … ON (col)` · 🚨 **ต้องใช้ `is_account_group_member()` — `is_member()` คืน FALSE เงียบๆ ให้ทุกคนที่ไม่ใช่ workspace member = audience ทั้งหมดของเรา** · ต้อง `GRANT EXECUTE` บน function (grant ที่ลืมบ่อยที่สุด) · **bind ใน `MAP` ไม่ได้** · **ใช้กับ VIEW ไม่ได้** |
| **UC column masks** | GA | UDF ต่อ column · caveat เรื่อง identity เหมือนกัน |
| **ABAC policies** | ✅ **GA — 2026-04-28** *(ไม่ใช่ 2025 อย่างที่เราเคยเขียน)* | row filter + column mask ขับด้วย governed tag แปะที่ catalog/schema/table · 1 policy → พันตาราง · ⚠️ **breaking change ตอน GA:** view/function เหนือ table ที่มี ABAC ประเมินในนาม **session user** ไม่ใช่ owner · ต้อง DBR 16.4+ |
| **ABAC GRANT policies** | 🔴 Beta (มิ.ย. 2026) | grant สิทธิ์แบบ dynamic ตาม tag — ตอนนี้แค่ `EXECUTE` บน model · **นี่คือทิศทางที่ UC กำลังไป** |
| **Governed tags** | GA (2026-04-02) | รากฐานที่ ABAC ต้องใช้ |
| **Data Classification** | GA (2026-04-20) | agentic auto-tagging column ที่ sensitive → ป้อน ABAC |
| **Dynamic views** | GA (legacy) | `CASE WHEN is_account_group_member(...)` — pattern ก่อน ABAC |

> ## 🚨 ตัวที่ตัดสินทุกอย่าง
> **ไม่มีอันไหนทำงานเลยกับ Tier-1 account user** (capability matrix: RLS ✗)
> **governance ดีได้แค่เท่ากับ entitlement tier ที่เราส่งไปถึง**
> **และในเคส AIA — governance ทั้งหมดนี้ตกไป เพราะเราไม่มี live query เลย → isolation ต้องเป็น by construction**

---
---

# FAMILY F — Data movement (เอา data ไปวางในที่ที่ PROD อ่านได้)

> **⛔ ทั้ง family นี้ตายด้วย R5** — *"ห้ามย้าย data ข้าม env"* บันทึกไว้เพื่อความครบ และเผื่อ **Q1/Q2 ได้คำตอบว่า YES**

## F23. **Table copy / CTAS เข้า catalog ที่ B เป็นเจ้าของ** — GA
```
Job ใน DEV ──► CTAS ──► catalog_PROD.schema.table  (catalog เขา storage เขา)
                        filter ต่อทีมตอน write
```
🟢 ง่ายที่สุด · เขาจ่ายค่าอ่าน · ไม่ต้องใช้ RLS ถ้า filter ตอน write
🔴 data ซ้ำ · stale · lineage ขาด · N copy สำหรับ N ทีม · **AIA: ตาย R5**

## F24. **ADLS write + external table** — GA
```
Job ใน DEV ──► เขียน Delta/Parquet ลง ADLS container ──► PROD register EXTERNAL TABLE
```
🚨 **มี governance สองระบบเหนือไฟล์ชุดเดียว** (UC ใน DEV + UC ใน PROD) → ACL surface ย้ายไปที่ Azure RBAC → **นี่คือวิธี bypass UC โดยไม่ตั้งใจ** · **AIA: ตาย R5**

## F25. **Delta clone** — GA
- **DEEP CLONE** → copy จริง เหมือน F23
- **SHALLOW CLONE** → ⚠️ **เปราะมากข้าม workspace/catalog**: compute ของ B ต้องอ่าน *storage path* ของ A ได้ **และ `VACUUM` ใน A จะทำให้ clone ของ B พังเงียบๆ** → **อย่าใช้ shallow clone เป็นกลไก share** · **AIA: ตาย R5**

## F26. **Lakeflow / DLT pipeline promote ไป workspace B** — GA
```
DAB / Jenkins ──► deploy pipeline definition อันเดียวกันเข้า workspace B
                  B รัน · B จ่าย · B เป็นเจ้าของ output table
```
**AIA: ตาย R4** (เรา deploy ไม่ได้) — เว้นแต่ **เขา** deploy bundle เอง (→ Family I) · และ re-compute ใน B = pipeline ซ้ำ + cost ซ้ำ + drift

---
---

# FAMILY G — Artifacts & exports (Tier 0 — **ไม่ต้องมี Databricks identity เลย**)

> ## ⭐ **นี่คือ family เดียวที่รอดในเคส AIA**

## G27. **Notebook → HTML export พร้อม output** — GA
`GET /api/2.2/jobs/runs/export?run_id=&views_to_export=CODE|DASHBOARDS|ALL` → HTML ที่มี output render แล้ว
```
Job ใน DEV ──► notebook run ──► export_run ──► .html ──► email / SharePoint / Volume
                                               (ไม่ต้องมี identity ใดๆ ในการเปิด)
```
🚨 **HTML นี้ static และ unfiltered ทั้งหมด** — อะไรก็ตามที่ identity ของ job เห็น จะถูก bake เข้าไป → per-team = โอเค · export notebook รวมทุกทีมให้ audience ผสม = **หายนะ**
🟡 กราฟ render เป็นภาพนิ่ง · **ไฟล์บวมเร็ว** · มี notebook chrome + code ติดไปด้วย · **⚠️ ถ้าไม่ inline plot lib เอง อาจมี CDN ref ติดไป → Zscaler บล็อก**
**AIA: ✅ ใช้ได้** (แต่ **G29 ดีกว่าทุกทาง**)

## G28. **UC Volume เป็น file drop** — GA
```
Job ใน DEV ──► /Volumes/catalog/ops/reports/2026-07/team_a.xlsx
                        │
                        └── GRANT READ VOLUME TO `client-team-a`
                            → เห็นใน Catalog Explorer ของเขา · download ได้
```
🚨 **grant เป็นระดับ volume ไม่ใช่ระดับไฟล์** → **1 volume ต่อ 1 ทีม** ไม่งั้นแชร์หมดทุกอย่าง · ไม่มี RLS บนไฟล์
**AIA: ❌ ตาย R5** — Volume อยู่ใน UC ของ DEV ซึ่ง PROD เข้าไม่ถึง

## G29. ⭐⭐⭐ **Custom self-contained HTML / Excel จาก Job** — GA (แค่เขียนโค้ด)
```
Job ใน DEV ──► for_each team ──► pandas + ECharts(inline) / openpyxl
           ──► ไฟล์เดียวจบ (data ฝังในไฟล์)
           ──► 📧 email attachment / SharePoint / Volume / blob
                        │
                        └──► 👤 คนเปิดในเครื่องตัวเอง · offline · ไม่ต้องต่ออะไร
```
| | |
|---|---|
| **✅** | **control สูงสุด magic ต่ำสุด** · per-team filtering เป็นเรื่อง **explicit** · ~$15/เดือน · **ไม่ต้องมี Databricks identity ฝั่งปลายทาง** · **ไม่มี preview feature** · **ไม่มี doc ขัดแย้ง** · **portable 100%** (ย้ายออกจาก Databricks ได้ทั้งดุ้น) |
| **🔴** | เรากลายเป็นเจ้าของ report renderer · 🚨 **ต้อง vendor chart lib — ห้าม CDN** (Zscaler MITM → หน้าขาว) |
| **AIA** | ✅✅✅ **ผ่านทุกข้อ = ชั้น 1 ของ solution · และเป็นคำตอบตรงๆ ของ S4** *(`.lvdash.json` พก data ไม่ได้ แต่ HTML ทำได้)* |

## G30. **SQL Statement Execution API / result download** — GA
`POST /api/2.0/sql/statements` → `EXTERNAL_LINKS` disposition คืน pre-signed URL ไปยัง Arrow/JSON chunk
🚨 ถูกคุมด้วย workspace setting **`SQL results download`** — admin ปิดทั้ง workspace ได้ → **พังเงียบๆ** · pre-signed link หมดอายุ

## G31. ⭐ **Notification destinations** — Email / Slack / Teams / **Webhook** / PagerDuty — GA
```
Schedule/Alert ใน DEV ──► Notification Destination (⚠️ workspace ADMIN เท่านั้นที่สร้างได้)
                            ├─ Email      → PDF / CSV / XLSX attachment
                            ├─ Slack      → PNG ใน channel + link + PDF ใน thread
                            ├─ Teams      → PNG + link + PDF ใน thread
                            ├─ Webhook    → POST อะไรก็ได้ → **ระบบปลายทางของเราเอง** ⭐
                            └─ PagerDuty  → incident
```
> ⭐ **Webhook คือตัวหลับใน** — เป็น generic egress hook: ยิง POST ไป Azure Function / **Logic App** / service ของเราเอง แล้วเราก็**หลุดออกจาก delivery model ของ Databricks ทั้งหมด** แลกกับการต้องสร้าง receiver เอง
> **นี่คือกลไกที่ทำให้ G29 ส่งอีเมลได้ — เพราะ Databricks แนบไฟล์อีเมลเองไม่ได้**

⚠️ **เราสร้าง notification destination เองไม่ได้ — workspace admin ต้องสร้างให้** → **ขอตั้งแต่เนิ่นๆ ไม่งั้นกลายเป็น critical path**
⚠️ ทุก destination ที่พา snapshot ไปด้วย มีปัญหา identity แบบเดียวกับ A5 (render ครั้งเดียว identity เดียว ผู้รับหลายคน)

## G32. **Databricks SQL Alerts** — GA (default ใน compliance-security-profile workspace ตั้งแต่ 2026-07-09)
🆕 **SQL alert task ใน Lakeflow Jobs GA มิ.ย. 2026** → คืน evaluation state → task ถัดไป branch ได้
ไม่ใช่ dashboard แต่เป็นช่องทาง "push ตัวเลขไปหาเขา" ที่ **ไม่ต้องมี identity ฝั่งรับเลย** · **AIA: ✅ ใช้เสริมได้** (เช่น alert เมื่อ cost ทีมไหนพุ่ง >3σ)

---
---

# FAMILY H — Escape hatches & non-Databricks

## H33. ~~**Power BI บน warehouse ของ workspace B**~~ — **OUT OF SCOPE** (ยืนยัน 2026-07-14)
```
PROD user ──► Power BI ──► warehouse ของเขา (ใน PROD) ──► UC table ใน DEV + ROW FILTER
              (Entra SSO)   💰 เขาจ่าย                        ▲
                                                     🚨 R5 บล็อกตรงนี้
```
> บันทึกไว้เพื่อความครบ: ในทางเทคนิค **นี่คือ option ที่ lock-in ต่ำสุด · RLS ถูกต้อง native · เขาจ่ายเอง** และแข็งแรงทางการเมืองในองค์กร Microsoft
> ⚠️ **regression เม.ย. 2026:** Microsoft **ถอด BI compatibility mode** ออกจาก Power BI Databricks connector → **UC metric view ใช้ใน Power BI ไม่ได้แล้ว** (table/view ธรรมดายังโอเค)
> **AIA: ❌ ตาย 2 ชั้น — (1) นโยบายทีม ไม่แตะ PBI (2) ตาย R5 อยู่ดี**

## H34. **Publish UC catalog → Microsoft Fabric** (mirrored catalog) — 🟡 **Public Preview 2026-06-18**
```
UC catalog ใน DEV ──► publish เป็น read-only mirrored catalog ใน Microsoft Fabric
                      ──► Fabric user query ตรง (ไม่ต้องมี Databricks identity)
```
ใหม่จริง เกี่ยวจริง **ถ้า** consumer อยู่บน Fabric · Preview · read-only · governance คร่อม 2 product · **พฤติกรรมของ UC row filter ข้าม mirror ต้อง verify**
**AIA: ❌ ตาย R5** (data ยังต้องเดินทาง) + PBI/Fabric out of scope

## H35. **OneLake catalog federation** — GA 2026-06-17 — ทิศทาง**กลับกัน** (Databricks อ่าน OneLake) · ไม่ใช่ทางออกจาก DEV

## H36. **JDBC/ODBC จาก compute ของ B → warehouse ของ A** — GA **และมันทำงานได้จริง**
```
notebook/app ใน PROD ──JDBC──► https://<DEV>.azuredatabricks.net/sql/1.0/warehouses/<id>
                                Authorization: Bearer <token ที่ใช้ได้ใน DEV>
```
> ⚠️ **กำแพงคือการครอบครอง credential 100% ไม่ใช่ topology** — *ในกรณีทั่วไป*
> **นี่คือ option ที่คนส่วนใหญ่คิดว่าใช้ได้ แล้วมาค้นพบทีหลังว่ามันแปลว่า "ให้สิทธิ์ workspace A แก่เขาทางประตูหลัง"** → ปฏิเสธด้วยเหตุผลนี้ให้ชัด
> **AIA: ❌ ตาย 2 ชั้น — (1) ต้องมี entitlement ใน coredata = ผิด R3 (2) network บล็อกจริง = R5**

## H37. **Databricks Connect / Statement Execution API จาก B → A** — GA — วิเคราะห์เหมือน H36 · mitigate ด้วย **scoped PAT (GA เม.ย. 2026)** + **token auto-scoping (GA มิ.ย. 2026)** · **AIA: ❌ เหมือน H36**

## H38. **Partner Connect** — GA — เป็น onboarding wizard ไม่ใช่กลไก share ข้าม workspace · บันทึก ปฏิเสธ

## H39. **Serverless SQL warehouse egress / network policies** — GA · 🆕 block internet destination เฉพาะเจาะจง (PuP มิ.ย. 2026) — เป็น **control ไม่ใช่ delivery** · **แต่เกี่ยวกับเรา: มันคือสิ่งที่จะคุมว่า Job ของเรายิง Logic App / Graph API ออกได้มั้ย (Q2)**

## H40. **Lakebase** (managed Postgres / OLTP) — GA-ish · PG18 มิ.ย. 2026
```
Job ใน DEV ──► sync serving table เข้า Lakebase (Postgres)
                              │
                              └──► Postgres client อะไรก็ได้ — app, tool, ทีม B
                                   ต่อด้วย Postgres credential
                                   ✅ ไม่ต้องมี Databricks identity เลย (Tier 0)
```
🔴 **มันคือ database ตัวที่สอง** = copy ที่สอง + governance perimeter ที่สอง · **UC row filter ไม่ตามเข้าไปใน Postgres** → ต้อง re-implement access control ด้วย Postgres role · bill ต่อเนื่อง
**AIA: ❌ ตาย R5** (ย้าย data ข้าม env) — *แต่ถ้า Q1/Q2 = YES นี่เป็น escape hatch ที่น่าสนใจกว่าที่คิด*

## H41. **Lakehouse Real-Time (Lakehouse//RT)** — 🔴 **Beta 2026-06-30**
warehouse type ใหม่: อ่าน sub-second รองรับ *"hundreds to thousands of concurrent users"* · ไม่ใช่กลไก share **แต่**ถ้าวันหนึ่งต้อง serve audience ฝั่ง PROD จำนวนมากจาก warehouse ของเรา (A1/A2/A3) นี่คือ compute shape ที่ทำให้รอด · Beta — **ตีราคาก่อนเชื่อ**

## H42. ⚠️⭐ **Databricks Marketplace — private listing** — GA · **🆕 third-party app ติดตั้งเข้า workspace ตัวเองได้ตั้งแต่ 2026-06-16**
```
เรา (provider) ──► PRIVATE Marketplace listing (data product / notebook / app)
                    │
workspace B admin ──┴──► "Get access" → ของไปโผล่เป็น catalog / app **ใน workspace เขา**
                          ✅ เขา install · เขารัน · เขาจ่าย · **เราไม่เคย deploy อะไรลง B เลย**
```
> ## ⭐ **นี่คือคำตอบที่สะอาดที่สุดของข้อจำกัด "เรา deploy ลง workspace เขาไม่ได้ แต่เขาทำเองได้" — และแทบไม่มีใครเสนอ**
> Marketplace เป็น **pull model**: เรา publish, **เขา** install

🚨 **แต่:** เบื้องหลังคือ **OpenSharing** → caveat เรื่อง row-granularity ของ D19 ใช้ทั้งหมด **และมันคือการย้าย data ข้าม env**
**AIA: ❌ ตาย R5** — **แต่ถ้า Q1/Q2 ตอบว่า YES นี่คือ option อันดับ 1 ของ Shape 2** (ดู §7 ของ requirements doc) เพราะมันแก้ R4 ได้อย่างสง่างามที่สุด

---
---

# FAMILY I — 🔄 **"แล้ว admin ฝั่งเขาสร้างเองได้มั้ย?"**

> ข้อจำกัดมัน **asymmetric**: **เรา** deploy ลง departmental ไม่ได้ · **เขา** ทำได้
> ทุกอันใน family นี้ **พลิกโจทย์** — และ **ทุกอันตั้งอยู่บน D17 (UC GRANT)** ซึ่ง **ตาย R5**

| # | เขาสร้าง | เราให้ | 💰 | Status | AIA |
|---|---|---|---|---|---|
| I-a | import `.lvdash.json` ของเรา → dashboard ของเขา | JSON + `GRANT SELECT` | **เขา** | GA | ❌ R5 |
| I-b | AI/BI dashboard ของเขาเองบน table เรา | `GRANT SELECT` | **เขา** | GA | ❌ R5 |
| I-c | Genie Agent ของเขาเองบน table เรา | `GRANT SELECT` + example query | **เขา** | GA | ❌ R5 |
| I-d | mount Genie Agent snapshot ผ่าน OpenSharing | a share | **เขา** | 🔴 Beta (มิ.ย. 2026) | ❌ R5 |
| I-e | Databricks App ของเขาเอง (user-auth) | `GRANT SELECT` + source ใน git | **เขา** | App GA / auth 🟡 PuP | ❌ R5 |
| I-f | install private Marketplace listing ของเรา | the listing | **เขา** | GA | ❌ R5 |
| I-g | ~~Power BI report ของเขาเอง~~ | `GRANT SELECT` | **เขา** | GA | ❌ R5 + PBI out |
| I-h | deploy DAB ของเราเข้า workspace เขาเอง | bundle + README | **เขา** | GA | ❌ R5 |
| I-i | mount Delta Share เข้า metastore เขา | a share | **เขา** | GA | ❌ R5 |
| **I-j** ⭐ | **admin เขา grant Consumer access ให้ user เขา** แล้วเปิด published dashboard ของเราจาก DEV | **แค่ URL** | เรา (compute) | GA | ❌ **R5b** — browser เข้า DEV ไม่ได้ |

> ## 💡 I-j คือตัวหลับในของ family นี้
> สิ่งที่บล็อก per-viewer RLS บน published dashboard ของเรา คือ **Consumer access entitlement** — และ **admin ของ*เขา* grant มันได้ใน workspace ของ*เขา*เอง** เราไม่ต้อง deploy อะไรเลย เราแค่ต้องให้**เขาติ๊กช่องเดียว**
> Databricks ถึงกับทำ group-cloning migration (`Migrate workspace entitlement control`) มาเพื่อให้ Consumer access เป็น default ของ user ใหม่
> **⇒ ในโปรเจกต์อื่น: ขอสิ่งนี้ก่อน แล้วค่อยไปออกแบบอ้อมมัน**
> **⇒ ในเคส AIA: ตาย R5b อยู่ดี** เพราะต่อให้เขามี entitlement ครบ browser ก็ยังเปิด DEV ไม่ได้

---
---

# 3. ⚠️ Cross-cutting watch-outs (จำให้ขึ้นใจ — ใช้ได้ทุกโปรเจกต์)

1. 🚨 **`is_member()` vs `is_account_group_member()`** — `is_member()` resolve **workspace-local group** → สำหรับ audience ที่นิยามว่า *ไม่ได้อยู่ใน workspace เรา* มันคืน **FALSE ให้ทุกคน เงียบๆ** → **ทุก row filter ในโจทย์แนวนี้ต้องใช้ `is_account_group_member()`**
2. 🚨 **`GRANT EXECUTE` บน row-filter function** — grant `SELECT` แล้วลืมอันนี้ = query fail (หรือแย่กว่านั้น พฤติกรรมประหลาด) **grant ที่คนลืมบ่อยที่สุดใน UC**
3. 🚨 **workspace-bound catalog → widget ว่างเปล่า ไม่มี error** (D18) — **เช็ค `isolation-mode` ก่อน debug อย่างอื่นทั้งหมด**
4. 🚨 **publish mode default = อันที่ไม่ปลอดภัย** — `embed_credentials: true` = credential ของ publisher = ทุกคนเห็นทุกอย่าง → **pin `false` ใน DAB อย่าเชื่อ UI default**
5. 🚨 **snapshot ที่ส่งทาง email/Slack/Teams ถูก render ครั้งเดียว ในนาม identity เดียว — ไม่เคย filter per-recipient** → **per-team dashboard หรือ per-team job เท่านั้น ไม่มีข้อยกเว้น**
6. 🆕 **Ask Genie เปิด default บน published dashboard แล้ว** (GA ก.ค. 2026) → **เราอาจ ship NL query interface ใส่ data ตัวเองโดยไม่ได้ตัดสินใจ — ต้อง audit**
7. 💸 **Genie เป็น pay-as-you-go แล้ว** (2026-07-08) ฟรี 150 LLM DBU/user/เดือน → **ตั้ง Budget** (GA 2026-07-06 · block ได้)
8. ⏰ **Entitlement model เปลี่ยน: rollout 2026-06-15 → auto-enable 2026-07-27 → บังคับใช้ 2026-09-14** → design ที่พึ่ง entitlement behaviour **ต้อง re-validate** · **อีก 2 สัปดาห์**
9. **IP access list มีผลกับ account user ด้วย** — viewer ที่อยู่นอก VPN = fail สนิท ไม่ว่า tier ไหน
10. **ABAC GA มี breaking change** (view/function ประเมินในนาม session user) — ถ้าใช้ ABAC อยู่ เช็คว่า tenant ถูกติดต่อมั้ย และ grace period 3 เดือนจบเมื่อไหร่
11. 💸 **Apps ไม่มี scale-to-zero — bill 24/7** · start/stop job กู้คืนได้ ~76%
12. **Power BI ไม่รองรับ UC metric view แล้ว** (เม.ย. 2026)

---

# 4. 💰 Cost envelope (Azure — verify $/DBU ตาม region)

| component | rate | หมายเหตุ |
|---|---|---|
| SQL Serverless 2X-Small | **4 DBU/hr** (~$0.70/DBU) | auto-stop 5-10 นาที = สุขอนามัยพื้นฐาน |
| SQL Pro | ~$0.55/DBU **+ VM** | |
| SQL Classic | ~$0.22/DBU **+ VM** | |
| **Databricks Apps** | **Medium 0.5 · Large 1 DBU/hr — 24/7 ไม่มี scale-to-zero** | **บวก** warehouse ที่มัน query อีก |
| **Genie** | **pay-as-you-go LLM DBU** ฟรี 150/user/เดือน (~$10.50) | 🆕 2026-07-08 |
| Lakebase | ต่อเนื่อง + **snapshot storage คิดเงินแล้ว** (มิ.ย. 2026) | |

**ประมาณการ ~5 ทีม / ~100 light user:**
| | |
|---|---|
| Published dashboard บน serverless 2X-S (~30 wh-hr/เดือน) | **~$85-115/เดือน — เราจ่าย** |
| Databricks App (24/7) + warehouse | **~$256-347/เดือน** (หรือ ~$80-105 ถ้าทำ start/stop job) = **2-4× ของ dashboard เพื่อแลกกับ auth mode ที่ยัง Preview** |
| **⭐ Per-team artifact job (G29 / A5)** | **~$5-20/เดือน** |
| ~~UC GRANT (D17) / export-import (A4) / Power BI (H33)~~ | **$0 กับเรา — warehouse ของ consumer จ่าย** *(แต่ตาย R5)* |

---

# 5. 🔒 Lock-in & portability

| layer | portable? |
|---|---|
| gold table (Delta/Parquet ใน ADLS ของเรา) | ✅ **ใช่** — UniForm/Iceberg REST ทำให้อ่านได้หลาย engine |
| row filter (UC SQL UDF) | 🟡 ส่วนใหญ่ — เขียนใหม่ได้ แต่ semantics (`is_account_group_member`) เป็นของ UC |
| ABAC / governed tags / classification | ❌ **ไม่** — UC gravity ลึก **นี่คือจุดที่ center of mass ขององค์กรย้ายเข้าไป** |
| **account-user sharing model · published dashboard · Genie Agent · Apps** | ❌ **ไม่เลย — proprietary 100%** ไม่มีอะไรเทียบเท่าที่อื่น ไม่มี export path |
| External embedding | ❌ **ไม่** — `@databricks/aibi-client` + `/tokeninfo` เป็น protocol เฉพาะ |
| **⭐ G29 (custom HTML/Excel job)** | ✅✅ **portable เกือบสมบูรณ์** — เป็นแค่ Spark/pandas job ที่เขียนไฟล์ · Databricks-specific แค่ scheduler + Volume ซึ่งแทนที่ได้ง่าย |
| ~~Power BI on UC (H33) / OpenSharing open protocol (D20)~~ | 2 อันนี้ lock-in ต่ำสุดใน catalogue |

> **พูดกับลูกค้าให้ชัด: *data* portable · *กลไก sharing* ไม่ portable**
> **ในเคส AIA — เราถูกบังคับให้ไปอยู่ที่ G29 ซึ่งบังเอิญเป็นอันที่ portable ที่สุด นี่คือด้านดีของข้อจำกัด**

---

# 6. 🏁 สรุป — 3 อันที่รอด (จาก ~25 อัน)

| ชั้น | option | ทำไมรอด |
|---|---|---|
| **ชั้น 0** | **A3 + A5** — per-team dashboard + native subscription (PDF + **Excel**) | ไม่ต้อง live path · ไม่ deploy ลง PROD · ไม่มี data ลงระบบ PROD · isolation by construction · **0 บรรทัดโค้ด** |
| **ชั้น 1** ⭐ | **G29** — self-contained interactive HTML / Excel จาก Job (+ **G31 webhook → Logic App** สำหรับส่ง) | เหมือนบน + **interactive จริง** + **portable 100%** + ตอบ **S4** ตรงๆ |
| **เสริม** | **G32** — SQL Alert (cost ทีมไหนพุ่ง >3σ) | push ตัวเลขโดยไม่ต้องมี identity ฝั่งรับ |

**ทุกอันที่เหลือตายด้วย R5 / R5b / R4 — รายละเอียดทีละข้อ → `solutions-compare-matrix-20260714-2040.md`**
