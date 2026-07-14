# AIA Cost Dashboard — Solution: **Artifact Factory** (2026-07-14, 20:40)

> **สืบเนื่องจาก:** `requirements-and-concerns-20260714.md` (R1-R10 / K1-K6 / S1-S7)
> **แทนที่:** `solution-20260713-2342.md` + `solution-lakeview-details-20260713-2342.md` — เอกสารสองอันนั้น **C11 ผิด** และ **Option D+ ตายแล้ว**
> **Scope:** ตัด **Power BI ออกทั้งหมด** (ยืนยัน 2026-07-14: *"ที่ AIA ตอนนี้เราจะไม่ไปแตะ power bi"*)
> **Policy:** ไม่มี code/data จริงของ AIA ในเอกสารนี้ — SQL/Python ทั้งหมดเป็น **generic template**

---

## 0. ทำไมโจทย์ถึงเปลี่ยน

ข้อจำกัดสุดท้าย (ยืนยันโดยสิน 2026-07-14):

| | |
|---|---|
| **R1** | gold table + pipeline อยู่ **coredata DEV** และอยู่ที่นั่นต่อไป (ไม่ promote ไป PROD) |
| **R2** | client user เข้าจาก **departmental PROD** เท่านั้น |
| **R3** | client ไม่เข้ามาเป็นสมาชิก coredata |
| **R4** | ทีมสิน **deploy อะไรลง departmental workspace ไม่ได้** (ไม่มี SP / API / bundle) |
| **R5** | **PROD วิ่งมาอ่าน DEV ไม่ได้** (network) **และห้ามย้าย data ข้าม env** — จะไม่เปิด shared แม้อยู่ใน UC เดียวกัน |
| **R5b** | **browser ของ client เปิด URL ของ DEV workspace ไม่ได้** ← ข้อนี้ฆ่า option ที่เหลือทั้งหมด |
| R6-R10 | per-team row isolation · chargeback · รายเดือน · หลายทีม · ต้อง automated |

### หลักการที่สินยืนยัน (สำคัญที่สุดในเอกสารนี้)
> **data ที่ถูก render แล้วส่งถึง "คน" = อนุญาต**
> **สิ่งที่ห้าม = data ลงไปอยู่ใน "ระบบ" ฝั่ง PROD**

### ผลที่ตามมาทางตรรกะ
```
dashboard ทุกตัวต้อง query data ถึงจะทำงาน
   → data อยู่ DEV
      → PROD วิ่งมาอ่านไม่ได้ (R5)
      → browser ก็เปิด DEV ไม่ได้ (R5b)
      → เอา dashboard ไป PROD ก็ไม่ได้ (R1/R4)
         ⇒ ❌ ไม่มี live-query solution ใดๆ อยู่รอด
         ⇒ ✅ เหลือทางเดียว: ARTIFACT ที่ render ใน DEV แล้วส่งถึงคน
```

**เราไม่ได้กำลังสร้าง dashboard platform — เรากำลังสร้าง "โรงงานผลิต artifact"**
โจทย์ทางวิศวกรรมย้ายจาก *sharing* → **isolation correctness + automation + auditability**
เพราะใน topology นี้ **อีเมลที่ส่งผิดคน = data breach** (ไม่ใช่ row filter ที่ลืมใส่)

---

## 1. ⭐ Feature ใหม่ที่เปลี่ยนคำตอบ

### 🆕 **2026-04-16 — Dashboard email subscription แนบ "ข้อมูล" ได้แล้ว**

> *"Email subscribers receive a PDF snapshot and **can optionally include tabular data from selected dashboard widgets as CSV, TSV, or Excel attachments**."*
> *"**Supported formats:** CSV, TSV, or Excel (Excel exports are limited to 100,000 rows). **Supported widgets:** Any widget with underlying query results, including table, pivot table, and visualization widgets."*
> — [Manage scheduled dashboard updates and subscriptions](https://learn.microsoft.com/en-us/azure/databricks/dashboards/share/schedule-subscribe)

**subscriber ไม่จำเป็นต้องเป็น Databricks user:**
> *"You can configure account users, **distribution lists**, and **external users (such as partners or clients)** as email notification destinations."*
> — [Manage notification destinations](https://learn.microsoft.com/en-us/azure/databricks/admin/workspace-settings/notification-destinations)

### 🔍 อันไหน "ใหม่" จริง อันไหนไม่ใช่ — (คำตอบคำถามข้อ 2)

| ชิ้นส่วน | ใหม่มั้ย? | เมื่อไหร่ | สถานะ |
|---|---|---|---|
| Dashboard scheduled **subscription** (ส่ง PDF อัตโนมัติ) | ❌ **ของเก่า** | GA มานานแล้ว | GA |
| **แนบ CSV / TSV / Excel มากับ subscription** | ✅ **ใหม่จริง** | **2026-04-16** | **GA** ← *นี่คือของที่เปลี่ยนเกม* |
| เลือกหน้า (page selection) ที่จะใส่ใน PDF | ✅ ใหม่ | 2026-04 | GA |
| Email notification destination รับ external user / DL | ❌ ของเก่า | — | GA |
| Custom visualizations (**Vega-Lite**) ใน AI/BI | ✅ ใหม่ | 2026-05 | 🟡 **Public Preview** |
| Dashboard relationships (multi-fact model) | ✅ ใหม่ | 2026-06→07 | 🟡 Public Preview |
| **Self-contained interactive HTML** | ❌ **ไม่ใช่ feature ของ Databricks เลย** | — | เป็นแค่ Python job เขียนไฟล์ (เทคนิคเก่าแก่, portable 100%) |
| Genie One **scheduled tasks** (prompt → email) | ✅ ใหม่ | 2026-04 | 🟡 Preview — ❌ **ใช้ไม่ได้: ผู้รับต้องเป็น Genie user ใน DEV → ตาย R3** |
| **External embedding** for external users | ✅ ใหม่ | 2026-04 | GA — ❌ **ใช้ไม่ได้: iframe ยัง load จาก DEV URL → browser เข้าไม่ถึง (R5b)** |
| Legacy SQL dashboard "email snapshot" | ☠️ | **retired 2026-01-12** | อย่าให้ใครอ้างถึง |

**สรุป:** ของใหม่ที่ *ใช้ได้จริง* มีชิ้นเดียว = **tabular attachment ใน subscription** ส่วน feature ใหม่ตัวหรูๆ (embedding, Genie scheduled) **ตายหมดเพราะ R5b** — ยืนยันอีกครั้งว่า **ไม่มี feature ใดของ Databricks อ้อม network policy ได้**

---

## 2. Solution ที่เสนอ — 2 ชั้น

### 🥉 ชั้น 0 — "Native, zero-code" (ship ได้สัปดาห์นี้)

```
1 AI/BI Dashboard ต่อ 1 ทีม   (dataset ฝัง  WHERE tag_team = 'TEAM_A'  ไว้ในตัว)
        ↓  Schedule (monthly, cron)
        ↓  Advanced settings → ☑ Include pages (PDF)  +  ☑ Include data (Excel/CSV)
        ↓  Subscriber = Email notification destination (DL ของทีมนั้น)
   📧 กล่องอีเมลของทีม:  PDF (ภาพรวม) + XLSX (pivot/filter เองได้)
```

**ทำไมมันผ่านทุกข้อ**
| ข้อ | ผ่านยังไง |
|---|---|
| R4 | ไม่ deploy อะไรลง departmental เลย — dashboard อยู่ DEV ล้วนๆ |
| R5 | ไม่มี data ลงระบบ PROD — egress เดียวคืออีเมลผ่าน Databricks control plane (ช่องทางที่ได้รับอนุญาตอยู่แล้ว) |
| **R6** | **isolation = by construction** — dashboard ทีม A มี row ทีม B **ไม่ได้ทางกายภาพ** เพราะเป็นคนละ query คนละไฟล์ |
| R10 | scheduler ของ Databricks รันเองตลอด |
| K-cost | ~2-10 DBU/เดือน → **~$5-20/ปี** |

**💡 ผลพลอยได้:** เมื่อ isolation เป็น by-construction แล้ว → **ไม่ต้องใช้ UC row filter เลย** → หลุดพ้นจากกับดัก `embed_credentials=true` (viewer query รันด้วย credential ของ publisher → row filter ถูก bypass เงียบๆ) ที่เคยเป็น trap อันดับ 1

**⚠️ กับดัก 5 ข้อที่ต้องรู้**
| # | กับดัก | ทางแก้ |
|---|---|---|
| 1 | **9 MB cap** (PDF + attachment รวมกัน) เกินแล้ว → **แนบแค่ PDF** + ข้อความ *"Open the dashboard to download full results"* ← **ซึ่ง client เปิดไม่ได้!** | aggregate ให้เล็ก: `resource_group × month` **ไม่ใช่** `resource × day` |
| 2 | **Excel = 100,000 rows** เกินแล้ว **ตัดเงียบ** | pre-aggregate + assert row count ก่อน |
| 3 | chart widget render ได้ max 10K rows / table widget 100K | ออกแบบ widget ตามนี้ |
| 4 | **Unsubscribe** — คนเดียวในDL กด → **ทั้ง DL หลุด** | เตือนทีมล่วงหน้า / ใช้ DL ที่คุมโดย IT |
| 5 | **attachment config ตั้งได้แค่ใน UI** — SDK `Schedule` มีแค่ `cron_schedule / warehouse_id / display_name / pause_status / etag` ไม่มี field attachment | ตั้งครั้งเดียวใน UI แล้วมันรันตลอด (schedule/subscription เองสร้างผ่าน API ได้) |

**ℹ️ security note ที่ดี:** PDF ถูกเขียนลง object storage ของ Databricks ชั่วคราว แล้ว **ลบทันทีหลังส่ง** (ไฟล์ที่ user กด download เองถึงจะค้าง ~60 วัน)

---

### 🥇 ชั้น 1 — **Self-contained Interactive HTML** (ของจริง, ~1 เดือน)

> **นี่คือคำตอบของ S4** — *"ถ้าได้เป็น json static dashboard ได้ ก็ยังดี อย่างน้อยให้ user import เอง"*
> `.lvdash.json` **ทำไม่ได้** (มันไม่พก data) — แต่ **HTML ทำได้**

```
Lakeflow Job (monthly)
 ├─ [T0] resolve_run   → pin Delta version V + อ่าน ops.team_recipient_map
 ├─ [T1] for_each team → render:  report_<team>_<YYYYMM>.html   (interactive, offline)
 │                                report_<team>_<YYYYMM>.pdf    (exec summary)
 │                                chargeback_<team>_<YYYYMM>.xlsx (Finance)
 │                       → เขียนลง UC Volume + INSERT ops.artifact_ledger
 ├─ [T2] VERIFY GATE  🚧  barrier — ห้ามส่งอะไรจนกว่าจะผ่านทุกข้อ
 ├─ [T3] for_each team → deliver (webhook → Logic App → O365 sendMail)
 └─ [T4] close_run     → audit + Teams summary
```

**คุณสมบัติ:** เปิดใน browser ธรรมดา **offline สนิท** — hover / filter / drill / cross-filter ได้จริง ไม่ต้องต่อ Databricks ไม่ต้องมี network

**⚠️ Zscaler:** ต้อง **vendor** chart library ลง UC Volume แล้ว inline เข้าไฟล์ — **ห้ามใช้ CDN เด็ดขาด** (Zscaler MITM → หน้าขาว)
| lib | ขนาด inline | เหมาะกับ |
|---|---|---|
| **ECharts** | **~1.1 MB** | ⭐ แนะนำ — คุ้มสุด |
| Plotly (`include_plotlyjs=True`) | ~3.5-5 MB | ถ้าคุ้นมือ |
| Chart.js | ~200 KB | กราฟง่ายๆ ไฟล์เล็กสุด |

**📮 การส่ง:** **Databricks แนบไฟล์อีเมลเองไม่ได้** (job notification ส่งได้แค่สถานะ run) → 3 ทาง เรียงตามความเหมาะกับ Zscaler:
1. ⭐ **webhook destination → Azure Logic App (ใน DEV subscription) → O365 `sendMail`** — data plane ไม่ต้อง egress เลย และ Logic App drop เข้า **SharePoint** ได้ฟรีๆ ด้วย
2. MS Graph `sendMail` จาก job (ต้อง app registration + `Mail.Send`) — ติด Zscaler จนกว่าจะแก้ CA bundle
3. `smtplib` → corporate SMTP relay — ง่ายสุด ถ้า relay reachable จาก DEV data plane

**🎁 portability:** ชั้น 1 เป็นแค่ Spark/pandas job ที่เขียนไฟล์ → **ยกไปที่ไหนก็ได้** (ต่างจากชั้น 0 ที่ lock-in กับ subscription/PDF engine ของ Databricks 100% — ไม่มี API surface เลย)

---

### 🥈 ชั้น 1b — Excel + PivotTable + Slicer
สาย **Finance / chargeback ชอบที่สุด** — เป็นเครื่องมือที่เขาใช้อยู่แล้ว interactive จริง generate จาก job ได้ด้วย `xlsxwriter`
👉 ทำควบไปกับชั้น 1 (ใช้ delivery pipeline เดียวกัน)

---

## 3. Governance — เมื่อ "ACL" กลายเป็นอีเมลแอดเดรส

| control | ทำยังไง | กันอะไร |
|---|---|---|
| **Generation-time filter** | `WHERE tag_team = :team` (parameterised) **ใน for_each task** — ห้าม filter ตอน deliver, ห้าม `df.filter(teams[i])` | data ข้ามทีมในไฟล์เดียว |
| **Manifest binding** | ฝัง `{run_id, team_tag, period, gold_version, sha256, recipients}` ในทุกไฟล์ | ไฟล์/ผู้รับสลับกันเงียบๆ |
| **Recipient snapshot** | T3 อ่านผู้รับ **จาก ledger row ที่เขียนตอน render** ไม่ใช่ query map ใหม่ | map ถูกแก้กลางรัน → ไฟล์ A ไปหาทีม B |
| **Verify gate (T2)** | เปิดไฟล์ที่ render แล้วจริงๆ มา assert: (a) team ในไฟล์มี **1 ค่า** เท่านั้น (b) ยอดตรงกับ gold (c) ไม่ว่าง (d) ผู้รับอยู่ใน Entra + domain allowlist (e) manifest == ledger == map (f) Σ ทุกทีม == ยอดรวม → **fail = abort ทั้ง run ห้ามส่งบางส่วน** | **ตัว breach เอง** |
| **Dry-run** | บังคับทุกครั้งที่แก้ map — render + verify + print To: list แต่ไม่ส่ง | map พังหลุดถึงกล่องจดหมาย |
| **Two-person rule** | `approved_by NOT NULL` · MERGE จาก YAML ที่ผ่าน Git review · คนรัน job ≠ คน approve | insider / เผลอ add ตัวเอง |
| **Shadow copy + immutable audit** | ทุกฉบับ Cc `finops-cost@` · `ops.delivery_audit` append-only | *"พิสูจน์ไม่ได้ว่าเดือน มี.ค. ส่งอะไรไปให้ใคร"* |
| **Anomaly tripwire** | alert เมื่อยอดทีมเคลื่อน >3σ / recipient set เปลี่ยน / จำนวนทีมเปลี่ยน | drift เงียบๆ |
| **Purview label** | Internal/Confidential + Do-Not-Forward (ถ้า tenant รองรับ) | forward มั่ว |

**เรื่อง forward — พูดตรงๆ:** ห้ามไม่ได้จริง Purview DNF แค่เพิ่มแรงเสียดทาน **แต่** data ชุดนี้คือ **ค่าใช้จ่าย Azure ราย resource — ไม่มี PII ไม่มี PHI ไม่มีข้อมูลผู้เอาประกัน** blast radius = ขายหน้าภายใน ไม่ใช่ regulatory event → **ความไม่สมมาตรนี้คือ lever ของข้อ 5**

### ตาราง mapping (single source of truth)
```sql
CREATE TABLE ops.team_recipient_map (
  team_tag         STRING NOT NULL,        -- ต้องตรงกับ gold.cost_wide.tag_team เป๊ะ
  display_name     STRING NOT NULL,
  recipients_to    ARRAY<STRING> NOT NULL,
  recipients_cc    ARRAY<STRING>,
  delivery_channel STRING NOT NULL,        -- 'EMAIL' | 'SHAREPOINT' | 'BOTH'
  formats          ARRAY<STRING> NOT NULL, -- ['HTML','PDF','XLSX']
  cost_centers     ARRAY<STRING>,
  active_from      DATE NOT NULL,
  active_to        DATE,                   -- NULL = current (SCD2 → audit ย้อนหลังได้)
  requested_by     STRING NOT NULL,
  approved_by      STRING NOT NULL,        -- ⚠️ NOT NULL — ไม่ approve ไม่ส่ง
  approved_at      TIMESTAMP NOT NULL,
  change_ticket    STRING
);
```
**เพิ่มทีมใหม่ = INSERT 1 row + 1 approval — ไม่ต้องแก้โค้ด**

---

## 4. ช่องทางส่ง — เทียบ

| | Email attachment | SharePoint/OneDrive link | **SharePoint page ฝัง HTML ต่อทีม** | Teams post | Network drive |
|---|---|---|---|---|---|
| อนุมัติแล้ววันนี้ | ✅ **ใช่** | ❓ | ❓ | ❓ | ~ |
| รู้สึกเหมือน "ที่ของฉัน" | ❌ | 🟡 | ✅ **ใกล้เคียงที่สุด** | ✅ | ❌ |
| interactive | ✅ (เปิด attachment ใน browser) | ✅ | ✅ | ❌ | ✅ |
| isolation ด้วย | address list (**เปราะ**) | **ACL บน folder** | **ACL บน site (แข็งสุด)** | channel membership | NTFS |
| **ถอนคืนได้** | ❌ | ✅ | ✅ | 🟡 | ✅ |
| audit การอ่าน | ❌ | ✅ | ✅ | 🟡 | ❌ |
| effort | 1-2 วัน | 3-5 วัน (Graph + consent) | 5-8 วัน + tenant setting | 1 วัน | อย่า |
| **สรุป** | **ship ตอนนี้** | ดีกว่า email ถ้าอนุมัติ | 🎯 **เป้าเดือนที่ 2** | notification เสริม | ❌ |

**SharePoint page = ตัวแทนที่ใกล้ "dashboard ใน workspace ตัวเอง" ที่สุดเท่าที่ policy อนุญาต** — และ isolation เลื่อนขั้นจาก *"พิมพ์ address ถูกมั้ย"* → *"ACL ถูกมั้ย"* ซึ่งเป็น control คนละชั้น **ถอนคืนได้ audit ได้** → เป็น **security upgrade** ไม่ใช่แค่ UX
⚠️ ติด 2 อย่าง: (1) SharePoint สมัยใหม่ **ไม่ render `.html` ในเบราว์เซอร์** โดย default (มันจะ download) ต้องเปิด custom script ที่ site collection — ขอ M365 admin (2) DEV ต้องยิง **Graph API ออกได้** (outbound เท่านั้น — เถียงง่ายกว่า inbound เยอะ)

---

## 5. 🚫 สิ่งที่ "เป็นไปไม่ได้" — พูดครั้งเดียวให้จบ

1. **ไม่มีวันมี dashboard live ใน workspace ของ client** — PROD วิ่งหา DEV ไม่ได้ + deploy ลง workspace เขาไม่ได้ + promote ไป coredata PROD ไม่ได้ → **ปิดทั้งตระกูล live-query** ไม่มี feature ไหน (ปัจจุบัน/Preview/roadmap) route รอบ network policy ได้
2. **ไม่มี Databricks object ใดไปโผล่ใน workspace เขาได้** — Dashboard / Genie Agent / App ล้วน workspace-scoped; object เดียวที่ข้าม workspace ได้คือ table/view ซึ่ง **R5 ห้าม**
3. **`.lvdash.json` ไม่มีวันพก data** — มันคือ query text + widget config เท่านั้น ไม่มี snapshot mode ไม่มี cache และ `embed_credentials=true` **ไม่ได้แปลว่าฝัง data** (แปลว่า query ของทุกคนรันด้วย credential ของ publisher — และจะ **ทำลาย row filter เงียบๆ**) → import ไปฝั่งเขา = **"table not found" เสมอ**
4. **UC row-level security ตกไปเลย** — isolation ต้องเป็น **by construction** (1 artifact / 1 ทีม) และเมื่อยอมรับแล้ว **มันกลายเป็นข้อดี**: ไฟล์นั้นมี row ทีมอื่นไม่ได้ทางกายภาพ
5. **ไม่มี PDF-export API** — PDF เกิดได้ 2 ทาง: ปุ่ม download ใน UI กับ subscription scheduler → **scheduler *คือ* automation** จะเขียน PDF pipeline เองบน AI/BI ไม่ได้
6. **Databricks แนบไฟล์อีเมล / เขียน SharePoint เองไม่ได้** — artifact ใดๆ นอกเหนือจาก PDF/CSV/Excel ของ subscription ต้องมี custom send step
7. **Interactive + offline + อยู่ใน workspace เขา = เซตว่าง** — เลือกได้ 2 จาก 3

---

## 6. 🔑 ข้อขอ policy — ข้อเดียว (ถ้าอยากได้ของจริง)

> **"ขอเปิดให้ browser ของ user (เฉพาะ Entra group `finops-cost-viewers`) เข้าถึง host ของ DEV Databricks workspace ได้ — HTTPS 443, front-end, read-only"**

**ไม่ใช่ data-movement exception · ไม่มี copy · ไม่มี share · ไม่มี object ลง PROD · PROD compute ไม่แตะ DEV** — มีแค่ **คนเปิดหน้าเว็บดู** แล้ว **UC row filter** คัดให้เห็นเฉพาะแถวของตัวเอง

| | วันนี้ (email artifact) | ถ้าอนุมัติ (link) |
|---|---|---|
| data ออกจาก DEV | **ใช่ — เป็นไฟล์ ถาวร** | **ไม่ — pixels เท่านั้น** |
| isolation บังคับด้วย | string ในช่อง To: | **UC row filter บน identity** |
| ถอนสิทธิ์ | **ไม่ได้** | ✅ ทันที |
| audit การอ่าน | **ไม่ได้** | ✅ ทุก query |
| forward ต่อ | ✅ (และมองไม่เห็น) | ❌ link ไร้ประโยชน์ถ้าไม่มีสิทธิ์ |
| network exposure ใหม่ | ไม่มี | 1 host, 443, 1 group, read-only |

> **policy ปัจจุบัน — เมื่อใช้กับ dataset ชุดนี้ — กำลังบังคับให้เราเลือกช่องทางที่ปลอดภัย *น้อยกว่า*** นี่คือประโยคที่ต้องพูดกับ security owner (เป็นลายลักษณ์อักษร พร้อมตารางข้างบน)

*(ข้อขอสำรอง ถ้า network exception ถูกปฏิเสธ: `GRANT SELECT` บน gold table ให้ account group ของ client แล้วเขา query จาก warehouse ตัวเองใต้ row filter — สะอาดกว่ามากในแง่ "ใน workspace เขา" แต่มันคือ PROD compute อ่าน DEV data ซึ่งคือสิ่งที่ policy ห้ามตรงๆ → คาดว่าโดนปฏิเสธ **ยิงข้อ browser ก่อน**)*

---

## 7. Roadmap

| เมื่อไหร่ | ทำอะไร | effort | ผลลัพธ์ |
|---|---|---|---|
| **สัปดาห์นี้** | AI/BI dashboard ต่อทีม + native subscription (PDF + **Excel**) → email destination | ~1 วัน, 0 บรรทัด | เลิก manual PDF ทันที · Sarunya เห็นความคืบหน้า · gold table ได้ผู้อ่านจริงมา validate |
| **เดือนนี้** | **Artifact Factory** — for_each job + mapping table + verify gate + HTML/PDF/XLSX + Logic App delivery + ledger | 5-8 คน-วัน · ~$20/เดือน | interactive จริง · automated เต็ม · audit ได้ · เพิ่มทีม = INSERT 1 row |
| **ขนานกัน** | ยิง 2 คำขอถูกๆ: (a) M365 admin เปิด HTML rendering บน FinOps site (b) network เปิด DEV → Graph API **outbound** | — | ปลดล็อก SharePoint page ต่อทีม = "ที่ของเขาเอง" |
| **ปลายทาง** | ยิงข้อขอ policy §6 | 1 เอกสาร | ถ้าอนุมัติ → กลับไปเป็น dashboard-in-their-place ได้ **ใน 2 วัน** (pipeline เดิมใช้ต่อได้หมด) |

---

## 8. 🗣️ สคริปต์คุยกับพี่ Sarunya

> พี่ Sarunya ครับ — มีข่าวไม่ดี 1 ข้อ กับข่าวดี 2 ข้อครับ
>
> **ข่าวไม่ดี:** "dashboard ที่อยู่ใน workspace ของ client เอง" — ตอนนี้ **สร้างไม่ได้จริงๆ** ครับ ไม่ใช่เพราะ Databricks ทำไม่ได้ (มันทำได้ และผม verify มาแล้วว่าวิธีที่ถูกคือ AI/BI Dashboard + UC row filter) แต่เพราะ **policy ปิดทุกทางที่ data จะเดินออกจาก DEV**: copy ไม่ได้ · share ไม่ได้ · PROD วิ่งมาอ่าน DEV ไม่ได้ · และ **browser ของ client เองก็เปิด URL ของ DEV ไม่ได้** ทางเดียวที่เหลือและได้รับอนุญาตจริง คือ **ไฟล์ที่ render ใน DEV แล้วส่งถึง "คน"** — ซึ่งก็คือสิ่งที่เราทำ manual อยู่ทุกวันนี้
>
> **ข่าวดีที่ 1 — ของที่พี่จะได้แทน:** ผมจะทำ **"โรงงานผลิต report"** ครับ — Databricks Job รันเดือนละครั้ง fan-out ทีละทีม ทีมละ 1 ไฟล์ **แต่ละทีมเห็นเฉพาะ cost ของตัวเอง by construction** (คนละ query คนละ task คนละไฟล์ — ปนกันไม่ได้ทางกายภาพ) ส่งอัตโนมัติ ไม่ต้องมีใครกดอะไร ไฟล์ HTML ที่ส่งไป **เปิดแล้ว interactive ได้จริง** (กราฟ กรอง drill-down) ไม่ใช่ PDF แบนๆ + มี **Excel** ให้ Finance เอาไปทำ chargeback ตรงๆ **เพิ่มทีมใหม่ = insert 1 row ไม่ต้องแก้โค้ด** และมี audit log ว่าเดือนไหนส่งอะไรให้ใคร
>
> อ้อ — และมี **feature ใหม่ของ Databricks (เม.ย. 2026)** ที่ช่วยเราพอดีครับ: subscription ตอนนี้แนบ **Excel/CSV** มากับ PDF ได้แล้ว แปลว่าแค่ตั้ง native subscription **สัปดาห์นี้เลย โดยไม่ต้องเขียนโค้ด** ทีมก็ได้ทั้ง PDF และไฟล์ที่ pivot เองได้
>
> **ข่าวดีที่ 2 — ทางกลับไปหาสิ่งที่พี่อยากได้จริงๆ:** เหลือ **การขอ policy แค่ข้อเดียว** ครับ: *"ขอให้ browser ของ user (เฉพาะ group ที่ระบุชื่อ) เปิด URL ของ DEV workspace ได้ แบบ read-only"* — **ไม่มี data ลง PROD ไม่มี copy ไม่มี share** มีแค่คนเปิดหน้าเว็บดู แล้ว UC row filter คัดให้เห็นเฉพาะแถวตัวเอง
>
> และประเด็นที่อยากให้พี่ใช้คุยกับ security: **วันนี้เราส่ง cost data ออกไปเป็นไฟล์ทางอีเมล — forward ต่อได้ ถอนคืนไม่ได้ ตรวจปลายทางไม่ได้** ส่วนวิธี link — **data ไม่ออกจาก DEV เลย** ตัดสิทธิ์เมื่อไหร่ก็ได้ audit ได้ทุก query **policy ปัจจุบันกำลังบังคับให้เราใช้ช่องทางที่ปลอดภัยน้อยกว่าครับ** — และ data ชุดนี้คือค่าใช้จ่าย Azure ไม่มี PII ไม่มี PHI

---

## 9. ❓ คำถามที่ยังต้องหาคำตอบ

| # | คำถาม | กระทบอะไร |
|---|---|---|
| Q1 | **SMTP relay** — DEV Databricks มี relay ภายในที่ approved แล้วมั้ย หรือต้องผ่าน Logic App / Power Automate? | effort ของ T3 (ไม่กระทบ design) |
| Q2 | **DEV ยิง Graph API ออกได้มั้ย?** | ประตูของ SharePoint path ทั้งหมด |
| Q3 | กฎ "ห้าม data ลง PROD" หมายถึง **platform** หรือ **environment**? ถ้านับ laptop + Outlook ของ client เป็น PROD ด้วย → **อีเมลก็ผิด policy** และแปลว่าไม่มีใคร enforce policy ตัวเอง — ซึ่งเป็น argument ที่แรงที่สุดของ §6 | ทั้งหมด |
| Q4 | Purview sensitivity label มีบน tenant นี้มั้ย? | DNF เป็นของจริงหรือละคร |
| Q5 | **tag hygiene** — `tag_team` ครอบคลุมกี่ %? ถ้า <95% ถังของ "untagged" จะเป็นปัญหา chargeback ที่ใหญ่กว่าเรื่อง delivery channel | ความน่าเชื่อถือทั้งระบบ |
| Q6 | จำนวนทีม — 5 หรือ 30? | ที่ 30 การ review recipient map กลายเป็นต้นทุน operational ตัวจริง และ policy exception เลิกเป็น nice-to-have |
| Q7 | บูม's pipeline ทำอะไรอยู่แน่? | เสี่ยงทำซ้ำ |

---

## 10. Scripts
👉 `scripts/cost-artifact-factory-20260714-2040/`
| ไฟล์ | ทำอะไร |
|---|---|
| `01_native_dashboard_subscriptions.py` | ชั้น 0 — generate dashboard ต่อทีมจาก template + สร้าง schedule/subscription ผ่าน SDK |
| `02_render_interactive_html.py` | ชั้น 1 — self-contained interactive HTML (ECharts inline, offline) |
| `03_render_excel_chargeback.py` | ชั้น 1b — Excel + PivotTable + slicer |
| `04_verify_and_deliver.py` | verify gate (6 assertions) + delivery (Logic App / Graph / SMTP) + ledger |
| `00_setup_tables.sql` | mapping table + artifact ledger + delivery audit |
