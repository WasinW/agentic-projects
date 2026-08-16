---
title: AIA Session — Complete Context Export
date: 2026-08-16
purpose: >
  Complete context handover to VS Code agents on Sin's machine.
  Contains: memory files, session recap, full-text of uploaded context docs,
  new deliverables, current state, and pending actions.
scope: AIA workstreams only (Cost Dashboard + Kafka Monitoring + Pipeline)
delivery_style: copy-paste ready — Sin will feed to local agents
---

# AIA Session — Complete Context Export

> **สำหรับ:** Sin — เอาไปให้ agent ในเครื่องช่วยงาน
> **วันที่ export:** 2026-08-16
> **Session type:** Web (Claude.ai)
> **Continuation of:** Multi-session engagement over ~1.5 months

---

## 📖 Table of Contents

1. [Memory Files (Persistent Context)](#part-1-memory-files-persistent-context)
2. [Session Recap & Timeline](#part-2-session-recap--timeline)
3. [Full Context Files (Copy-Paste)](#part-3-full-context-files-copy-paste)
   - [3.1: solution-artifact-factory-20260714-2040.md](#31-solution-artifact-factory-20260714-2040md)
   - [3.2: context-20260715-vscode-uc-share-pivot.md](#32-context-20260715-vscode-uc-share-pivotmd)
   - [3.3: Sin's Current Grafana Alert YAML](#33-sins-current-grafana-alert-yaml)
   - [3.4: HTML File (Deferred)](#34-html-file-deferred)
4. [New Deliverables Produced This Session](#part-4-new-deliverables-produced-this-session)
5. [Current State & Pending Actions](#part-5-current-state--pending-actions)
6. [Full File Inventory](#part-6-full-file-inventory)

---

# PART 1: Memory Files (Persistent Context)

## 1.1 Profile

**File:** `/profile.md`

```
name: profile
description: Who Sin is — role, employer, background
sources: [backfill]

- Name: Sin
- Senior Data Engineer at AIA Thailand
- Joined AIA Thailand on 2026-07-01
- Works across three workstreams at AIA:
  1. Kafka/Strimzi/Debezium producer pipeline on AKS
  2. Azure Databricks compute layer driven by a config Framework DB (prd_frmwrk_db)
  3. Cost Dashboard PoC on Databricks
- AIA operates an air-gapped environment — can only share screenshots, not paste code directly
- Previously a Data Engineer at The1 (Central Group Thailand), working primarily on GCP
- Has worked across GCP, AWS, and Azure cloud stacks
- Background in Scala/Spark (Delta Lake, Redshift, AWS-to-GCP data migration)
- Long-running interest in agentic AI and a Founder/IC career track
```

## 1.2 Cost Dashboard PoC Area

**File:** `/areas/cost-dashboard-poc.md`

```
name: cost-dashboard-poc
description: Azure Cost Monitoring Dashboard PoC on Databricks at AIA — current focus
aliases: [cost-dashboard, cost-monitoring-dashboard]

- Azure Cost Monitoring Dashboard PoC on Databricks — current primary focus at AIA
- Navigating the Option D+ architecture: granting UC access and row filters on coredata,
  exporting a .lvdash.json dashboard template for departmental admin import,
  and publishing with Individual Data Permissions
- Individual Data Permissions publishing is non-negotiable to preserve RLS
- Hard constraint: Sin's team cannot create or deploy objects in departmental workspaces in any form
- บูม owns the existing cost pipeline
- Unresolved: az login SSL/Zscaler TLS issue, pending a combined master-ca.crt bundle
- Azure CLI TLS certificate failures are caused by Zscaler proxy interception in AIA's
  corporate environment — a recurring theme
- Earlier explored Azure architecture context before the PoC consumed focus:
  SageMaker equivalents on Azure (Azure ML, Databricks ML) and general data platform architecture

⚠️ NOTE: This memory is stale. Updated understanding (from this session):
- Sarunya paused this workstream (พับไปก่อน)
- Solution has evolved from D+ → Artifact Factory (see PART 3.1)
- Empirical test proved D+ fails at "table not found" cross-workspace
- Sarunya later opened UC share (2026-07-15) → D+ conditional revival pending network verify
```

## 1.3 People

**File:** `/people/boom.md`
```
name: boom
description: Colleague at AIA who owns the existing cost pipeline

- บูม — owns the existing cost pipeline at AIA
- Still opaque what exactly his pipeline does; Sin has not fully understood yet
```

**File:** `/people/sarunya.md`
```
name: sarunya
description: Senior DE colleague at AIA

- พี่ Sarunya — senior Data Engineer on Sin's team at AIA, with an SA-like guidance role
- Made key decisions:
  - 2026-07-13: Paused cost dashboard Genie AI workstream
  - 2026-07-15: Opened UC share (partial R5 relaxation) → D+ conditional revival
  - Owns the security policy interpretation
```

## 1.4 Recent Work

**File:** `/topics/recent-work.md`

```
name: recent-work
description: Work-adjacent activity and explorations that aren't standalone projects

- Set up Outlook folder organization with rules for managing Kafka/Debezium/AKS notification volume
- Explored setting up private investment companies in Thailand and Singapore for long-term wealth
  accumulation and regulatory hedging — worked through Thai corporate tax mechanics,
  Singapore capital gains exemption nuances, CRS transparency, and a four-phase personal roadmap
- At The1 (Central Group), built and maintained production-grade Apache Beam/Dataflow pipelines
  for real-time and batch member data processing
- The1 systems: MS Member/MS Personas pipelines processing tens of millions of records,
  Kafka consumer pipelines for loyalty tier events writing to GCS via Iceberg format,
  a config-driven dataflow_common framework packaged as a wheel and Docker image for Composer/Dataflow deployment,
  and CDC streaming pipelines writing to BigLake Iceberg tables via Storage Write API
- The1 work: Terraform-managed BigQuery infrastructure, GitLab CI/CD, Cloud Composer (Airflow) DAG
  orchestration, cross-cloud S3 write patterns
- The1 work: data governance architecture (Dataplex, Unity Catalog, Gravitino comparisons),
  GCP Professional Data Engineer exam prep content, Dataform pipelines
- At The1 worked with GCP infra: Apache Beam/Dataflow, BigQuery, Bigtable, Pub/Sub,
  Cloud Composer, Kafka, Terraform
```

---

# PART 2: Session Recap & Timeline

## 2.1 Multi-Session Context (Prior to This Session)

**Compact summary from previous mobile sessions (2026-07-13 to 2026-07-15):**

### Cost Dashboard Journey

**Constraints (11 total, evolved over time):**
- R1: gold table + pipeline in coredata DEV, stays there
- R2: client users access from departmental PROD only
- R3: client not members of coredata workspace
- R4: Sin cannot deploy anything to departmental workspace (SP push = VIOLATES)
- R5: PROD can't read DEV data + cannot move data across env
- R5b: **client browser cannot open DEV workspace URL** ⭐ new constraint
- R6-R10: per-team row isolation, chargeback, monthly, multiple teams, automated
- Sarunya update 2026-07-15: UC table share NOW ALLOWED (R5 halved)

### Design Evolution

```
Timeline of solution attempts:

D+ (v1) [2026-07-13]
├── UC GRANT + row filter + dashboard export/import
├── Died from empirical test: DEV→UAT export failed "table not found"
└── Was based on wrong assumption C11 (PROD reading DEV allowed)

Artifact Factory [2026-07-14] ⭐ canonical
├── 2 tiers:
│   ├── Tier 0: Native AI/BI Dashboard per team + subscription with Excel/CSV
│   │           (2026-04-16 game-changer feature, zero-code, ~$5-20/yr)
│   └── Tier 1: Custom Lakeflow Job for_each team → self-contained interactive HTML
│               + Excel (~$20/mo, 5-8 person-days)
└── "Data rendered and sent to person" = allowed
    "Data landing in PROD system" = forbidden

D+ Conditional Revival [2026-07-15]
├── Sarunya opened UC share
├── Pending network gate verification
└── Test needed: SELECT count(*) from PROD workspace → coredata table
```

### Key Corrections Made in Previous Sessions

- ❌ "SQL warehouse compute affinity forces WS membership" (WRONG per Databricks docs)
- ❌ "UC GRANT requires adding to workspace" (WRONG — metastore-level privilege)
- ❌ "Feature 3 vs Feature 4 security difference" (SAME when Mode B used)
- ❌ Gemini's ".lvdash.json contains cache" (FALSIFIED via docs)
- ❌ Clean Rooms suggestion (wrong tool, $7,500/mo, delivers tables not dashboards)
- ❌ "table not found" ≠ "network blocked" (different layers)
- ❌ Databricks features cannot bypass NETWORK-layer enforcement (they're IDENTITY-layer)

### Kafka Monitoring Current State (from previous sessions)

```
Stack: Prometheus scrape → Grafana → Alertmanager → Email
Existing alerts: 2 (heartbeat + instant, both monitor strimzi_reconciliations_failed_total)
Namespace: nsp-th-u-kafka (UAT)
Datasource UID: PBFA97CFB590B2093
Folder: kafka-clsuter-alert-rule (has typo, kept for compat)
Receiver: test_wasin (still test channel)
No PROD alerts yet
Only monitors KafkaConnect kind
```

## 2.2 This Session Timeline (2026-08-15 to 2026-08-16)

**Session started with compact summary loaded.**

### Turn 1: Absorb Compact Summary
- Loaded full context of prior work
- Established understanding of both workstreams

### Turn 2: Discussion about "AIA context in this session"
- Confirmed Sin's 3 workstreams:
  1. Cost Dashboard Genie AI (paused by Sarunya)
  2. Monitoring Kafka (main focus)
  3. Pipeline Implementation (AIA-style, coordination-heavy)

### Turn 3: Explanation of AIA's Pipeline Coordination Style
- Sin explained "SMR" release cycle (still to explain in detail)
- Coordination model: source owner + DP team + IT helpdesk + vendor team
- Sin's role at AIA = architect + coordinator (vendor writes code, unlike The1)

### Turn 4-5: Kafka Monitoring Focus Set
- Sin requested pivot to Kafka monitoring topic
- Baseline noted for reference

### Turn 6: Sin Pasted Current Grafana YAML
- 2 alert rules (heartbeat + instant)
- Sin requested 3 things:
  1. Review current alerts
  2. Best practice for health checks (what to check, alert vs heartbeat)
  3. Explain architecture — why some queries work and some don't (strimzi_* vs kafka_*)

### Turn 7: Comprehensive Response Delivered
- Reviewed existing alerts (found real bugs + one WRONG bug call on my part)
- Explained 8-layer monitoring model (K8s, Strimzi, Broker, Topic, Connect, Debezium, Consumer, SLO)
- Explained architecture: JMX Exporter enable requirement, why kubectl vs Prometheus see different things

### Turn 8: Sin's Correction — Heartbeat is INTENTIONAL Design
- I falsely called `condition >= 0 + for 4h` a bug
- Sin corrected: this IS the heartbeat pattern (deadman's switch — silence = broken)
- I acknowledged and corrected my analysis

### Turn 9: Sin Requested Enhanced Queries in Same 2 Rules
- Constraint: use only Strimzi metrics that Sin has (no JMX/Kafka Exporter yet)
- Enhance heartbeat to show more status meaningfully
- Add alerts within existing framework
- Explain what each rule checks and why

### Turn 10: 9 Rules Designed Using Only Strimzi Metrics
- 1 Enhanced Heartbeat (H1) — multi-query cluster snapshot
- 8 Alert Rules (A1-A8):
  - A1: Reconcile failed (any kind, expanded from Sin's KafkaConnect-only)
  - A2: Operator DOWN (critical)
  - A3: Resource count dropped (accidental delete detection)
  - A4: Reconcile P99 slow (operator overloaded)
  - A5: Paused resource lingering
  - A6: Lock storm (contention)
  - A7: Operator alive but no reconciliation (deadlock detection)
  - A8: KafkaConnector NOT_READY (verify metric exists first)

### Turn 11: Sin Requested Deliverable Files (No Code Deploy)
- Sin: "code deploy กระทบคนอื่น ขอ setup UI ง่ายๆก่อน"
- Created 2 files:
  - `strimzi_alerts.yaml` — Full YAML with inline comments (1,052 lines)
  - `strimzi_alerts_setup_manual.md` — Step-by-step UI walkthrough (1,117 lines)
- Both delivered via present_files

### Turn 12: This Export Request
- Sin: "session นี้มี memory history เกี่ยวกับ aia อะไรยังไงบ้าง export ออกมาหน่อย"
- Sin: "รวมถึง context ที่ผม update ไปอย่างละเอียดด้วยนะ copy paste มาเลยก็ได้"

## 2.3 Key Decisions Made This Session

1. ✅ **Kafka monitoring is now primary focus** (Cost Dashboard paused by Sarunya)
2. ✅ **9 alert rules designed** using Strimzi metrics only (no exporter dependencies)
3. ✅ **UI setup approach adopted** (no code deploy to avoid impact on other teams)
4. ✅ **Deliverables produced** ready for Sin to click through in Grafana

## 2.4 Corrections Made This Session

| # | Original Error | Corrected By |
|---|---|---|
| 1 | Called Sin's heartbeat `>= 0` a "bug" | Sin's pushback — it's intentional deadman's switch |
| 2 | Would have missed JMX exporter deployment requirement in first draft | Verified via web search before responding |

---

# PART 3: Full Context Files (Copy-Paste)

## 3.1 solution-artifact-factory-20260714-2040.md

**Status:** ⭐ CANONICAL solution (supersedes solution-20260713-2342.md + solution-lakeview-details-20260713-2342.md)
**Source:** Uploaded by Sin 2026-07-14

**Full file contents below:**

---

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

---

## 3.2 context-20260715-vscode-uc-share-pivot.md

**Status:** ⭐ LATEST context (D+ resurrection with UC share)
**Source:** Uploaded by Sin 2026-07-15
**Impact:** Pivot after Sarunya opened UC share partially

**Full file contents below:**

---

# AIA Cost Dashboard — Context Export (VS Code session, 2026-07-15)

> **สำหรับ:** สิน — เอาไปอัปเดต web chat
> **หัวข้อหลักของ session นี้:** พี่ Sarunya ยอมให้ **share table ผ่าน UC ได้** → **D+ ฟื้นจากตาย (แบบมีเงื่อนไข)** + verify ว่า UC cross-workspace ติด network layer ไหนกันแน่
> **ไฟล์ที่เกี่ยวข้อง:** `solutions-catalog-20260714-2040.md` · `solutions-compare-matrix-20260714-2040.md` · `solution-artifact-factory-20260714-2040.md` · `requirements-and-concerns-20260714.md`

---

## 🔑 THE BIG PIVOT (สำคัญสุดของวันนี้)

**พี่ Sarunya update (2026-07-15):**
> **"เปิด shared table ผ่าน UC ได้ — แต่ห้ามเข้า workspace dev เรา"**

→ R5 เดิม (*"จะไม่เปิด shared แม้อยู่ใน UC เดียวกัน"*) **ถูกยกเลิก**
→ R5 ถูกผ่าครึ่ง:

| | เดิม (R5) | ใหม่ (2026-07-15) |
|---|---|---|
| share table ผ่าน UC | ❌ ห้าม | ✅ **ได้แล้ว** |
| เข้า workspace DEV | ❌ ห้าม | ✅ ยังห้าม (= R3 เดิม) |

**ข้อมูลเพิ่มจากสิน:**
- "share ผ่าน UC" = **UC GRANT (metastore เดียวกัน)** — คุ้นๆ ว่าอย่างนั้น *(แต่ยังไม่ทิ้ง Delta Sharing/OpenSharing — ขอ re-check)*
- metastore เดียวกันมั้ย = เหมือนข้อบน (ยังไม่ยืนยัน 100%)
- catalog OPEN/ISOLATED = **ไม่แน่ใจ ต้องดู**
- network path (PROD compute → DEV storage) เปิดมั้ย = **"ไม่น่าเปิด น่าจะแค่ชั้น governance"** ⭐

---

## 🧟 D+ / D17 ฟื้นจากตาย — และดีกว่า email artifact ทุกทาง

**architecture:**
```
coredata DEV                              departmental PROD
┌──────────────┐                      ┌────────────────────────┐
│ gold.cost_wide│◄──── shared via UC ──│ dashboard ของเขา        │
│ + ROW FILTER  │      (GRANT SELECT)  │   (import .lvdash.json)  │
│ 💾 data ที่ DEV │◄─ compute PROD อ่าน ─│ 💰 warehouse ของเขา      │
└──────────────┘                      │ 👤 เปิด workspace ตัวเอง  │
                                       │    — ไม่แตะ DEV เลย       │
                                       └────────────────────────┘
```

**"ห้ามเข้า DEV" ตอบโจทย์ด้วย UC GRANT พอดี:**
> **UC GRANT = สิทธิ์บน data ไม่ใช่ membership ของ workspace** — table โผล่ใน Catalog Explorer *ของเขา*, query ด้วย warehouse *ของเขา*, ไม่มีใครเข้า DEV

**สิ่งที่ได้กลับคืน:**
| | email artifact | **D+ (ฟื้น)** |
|---|---|---|
| K3 เห็นใน workspace ตัวเอง | ❌ | ✅ |
| K6 client จ่าย compute | ❌ เราจ่าย | ✅ เขาจ่าย |
| live / refreshable | ❌ static | ✅ live |
| interactive | ⚠️ Excel | ✅ dashboard เต็ม |
| R5b browser เข้า DEV | ติด | ✅ **ไม่ติดแล้ว** (เปิด workspace ตัวเอง) |

---

## ⚠️ VERIFY จาก Azure Databricks docs — UC cross-workspace ติด network ไหน

**คำถาม:** governance บอก "share ได้" แต่ตอน query จริง compute อ่าน storage ข้าม network ได้มั้ย?

### 🎯 VERDICT: **NO — UC GRANT (metastore เดียวกัน) ไม่พอ ถ้า network path ปิด**

> *"Cloud storage URLs must be accessible through firewall and network controls."*
> — [UC credential vending, Requirements](https://learn.microsoft.com/en-us/azure/databricks/external-access/credential-vending)

**กลไก (confirmed จาก docs):**
```
PROD warehouse รัน SELECT
   ↓ UC vend short-lived credential ให้ compute
   ↓ compute plane ของ PROD ── อ่านไฟล์ตรงๆ ──► ADLS storage ของ DEV
                                    ▲             (ไม่ผ่าน control plane)
                          ถ้า storage firewall ไม่ให้ PROD subnet → 403 / connectivity error
```

**⇒ grant = "necessary but not sufficient" · network reachability = gate ที่ 2 แยกกันคนละชั้น**

### ข้อเท็จจริงที่ verify มา (มี citation):
1. **UC = credential vending** → consumer compute (PROD) อ่าน ADLS ของ DEV **โดยตรง** data ไม่ผ่าน control plane
2. **compute ของ PROD เป็นตัวต่อ storage** ไม่ใช่ compute ของ DEV (metastore แชร์ / compute ไม่แชร์)
3. **ถ้า firewall ปิด → error 403 ไม่ใช่ widget ว่างเงียบๆ** *(แก้ที่เคยเข้าใจผิด: ว่างเปล่า = row filter คืน 0 แถว คนละเรื่องกับ network)*
4. **row filter ทำงานข้าม workspace ได้** (metastore เดียวกัน — Databricks compute บังคับใช้ตอน query) ✅
5. **serverless ก็ต้องเปิด** ผ่าน NSP service tag `AzureDatabricksServerless.<region>` หรือ NCC private endpoint (⏰ deadline 2026-06-09 ผ่านแล้ว — subnet-ID allowlist ต้องย้ายไป NSP)
6. **classic VNet-injected** ต้องมี private endpoint / VNet rule / peering + firewall rule
7. **Delta Sharing/OpenSharing = requirement เดียวกัน** (recipient อ่าน provider storage ตรงๆ) + **row filter/column mask ไม่เดินทางผ่าน share**
8. **ไม่มี UC mode ไหนที่ proxy data ผ่าน control plane** เพื่อเลี่ยง network requirement (ยกเว้น Lakehouse Federation ซึ่งเป็น data path คนละแบบ = JDBC ไป foreign engine ไม่ใช่เคสนี้)

### 🆕 governance gate อีกตัว (เช็คก่อน firewall เพราะเร็วกว่า):
**external-location / storage-credential "workspace binding"** — ถ้า bind ไว้เฉพาะ DEV → PROD/UAT อ่านไม่ได้**แม้ network เปิด + grant ครบ** (เช็คแท็บ Workspaces บน storage credential)

---

## 🔑 network ask เปลี่ยนไป — และดีขึ้น

เดิม §6 เขียนว่า *"เปิด browser → DEV workspace"* (ขอแปลกๆ)
**แต่ D+ variant นี้ user เปิด workspace ตัวเอง — ไม่แตะ DEV (ไม่ติด R5b)**
→ ข้อขอจริงคือ:

> **"เปิด private endpoint / firewall rule จาก PROD compute plane → DEV storage account"**

= **pattern มาตรฐานของ Azure** ที่ UC cross-workspace ออกแบบมาให้ทำอยู่แล้ว → **เถียงกับ infra ง่ายกว่าเยอะ**

**network path ที่ต้องเปิด 1 ใน:**
| PROD compute | เปิดอะไร (ที่ DEV ADLS) |
|---|---|
| Classic (VNet-injected) | private endpoint จาก PROD VNet · หรือ VNet/subnet rule บน storage firewall · หรือ peering + rule |
| Serverless | associate DEV storage กับ NSP + allow `AzureDatabricksServerless.<region>` · หรือ private endpoint จาก NCC ของ PROD |
| ทั้งคู่ | region เดียวกัน + ถ้า public access ปิด → เปิด "Allow Azure trusted services" |

---

## 🧪 PoC PLAN (สิน จะลองเอง)

**ข้อจำกัด:** สินรัน `dbutils.fs.ls` ที่ departmental ไม่ได้ (ไม่มีสิทธิ์/มองไม่เห็น compute ทุก env)
**ทางออก:** ทดสอบที่ **coredata UAT** (สินมีสิทธิ์เต็ม) → ตัดตัวแปร "user ไม่มีสิทธิ์" ออก

**⚠️ UAT พิสูจน์อะไร / ไม่พิสูจน์อะไร:**
- ✅ UAT ผ่าน → กลไก share + row filter + dashboard import **ทำงาน** (governance ครบ)
- ❌ **ไม่ได้พิสูจน์ network ของ departmental PROD** (UAT↔DEV ต่อ network ง่ายกว่า PROD↔DEV)
- ⇒ UAT ผ่าน = เหลือตัวแปรเดียวสำหรับ PROD = network path → เอาไปคุย infra

### วิธี "แชร์ให้ไปขึ้นที่ปลายทาง" — แยก 2 กลไก:

**1️⃣ TABLE → UC GRANT ให้ principal (ไม่ใช่ให้ workspace)**
> metastore เดียวกัน + catalog OPEN → ชื่อ catalog โผล่ใน Catalog Explorer ทุก workspace อยู่แล้ว · grant = เพื่อให้ *query ได้*
```sql
-- รันใน coredata DEV
GRANT USE CATALOG  ON CATALOG  <cat>                  TO `<your-user-or-group>`;
GRANT USE SCHEMA   ON SCHEMA   <cat>.cost             TO `<your-user-or-group>`;
GRANT SELECT       ON TABLE    <cat>.cost.cost_wide   TO `<your-user-or-group>`;
GRANT EXECUTE      ON FUNCTION <cat>.cost.fn_cost_rls TO `<your-user-or-group>`;  -- ⚠️ ลืมบ่อยสุด
```

**2️⃣ DASHBOARD → ไม่ auto ขึ้น (เป็น workspace object)** มี 2 ทาง ทดสอบคนละเรื่อง:
| ทาง | ทำยังไง | ทดสอบอะไร |
|---|---|---|
| A. Publish + share URL | publish ที่ DEV → share account user → เปิด URL | 🚨 URL ชี้ DEV → เทส browser→DEV (R5b) **ไม่ใช่ D+** |
| **B. Export → Import** ⭐ | export `.lvdash.json` → import เข้าปลายทาง → repoint warehouse → เปิด | ✅ **D+ จริง** |
→ **PoC ใช้ทาง B** (ทาง A จะหลอก เพราะใน UAT เปิด DEV URL ได้อยู่แล้ว)

### 🧪 test ที่เด็ดขาดสุด — ไม่ต้องใช้ dashboard ด้วยซ้ำ:
```sql
-- รันใน SQL editor / notebook ของ coredata UAT
SELECT * FROM <cat>.cost.cost_wide LIMIT 10;
```
**decision tree:**
```
เห็นแถว (filter ตัดถูก)      → ✅ governance + network + RLS ครบ → D+ ทำงาน (ในขอบเขต coredata)
403 / connectivity error    → ❌ ติด NETWORK → ตัวที่ต้องเปิด (เอาไปคุย infra)
ว่างเปล่า 0 แถว              → ⚠️ row filter คืน false — ทุกอย่างทำงาน แค่ filter logic
table/catalog not found     → ⚠️ คนละ metastore / catalog ISOLATED (ยัง bind UAT) / grant ไม่ครบ
```

### ลำดับที่แนะนำ:
1. **เช็ค metastore** (30 วิ): `SELECT current_metastore();` รันทั้ง DEV + UAT → **ต้องได้ค่าเดียวกัน** (ต่าง = คนละ metastore → Delta Sharing → row filter ไม่ผ่าน share)
2. **GRANT 4 บรรทัด** ให้ user ตัวเอง (ที่ DEV)
3. **รัน `SELECT ... LIMIT 10` ที่ UAT** → อ่าน decision tree
4. ผ่าน → **export/import dashboard เข้า UAT** (ทาง B) → widget ขึ้นมั้ย
5. ได้ผล → เขียน D+ resurrection doc + network ask

### caveat 2 ข้อ (grant แล้วยังอ่านไม่ได้ทั้งที่ควรได้):
- **catalog ISOLATED** → `databricks catalogs update <cat> --isolation-mode OPEN` (หรือ add binding READ_ONLY)
- **storage-credential/external-location bind เฉพาะ DEV** → เช็คแท็บ Workspaces (governance ไม่ใช่ network เช็คเร็ว)

---

## 🔄 REPOSITION (สถานะล่าสุด)

```
email artifact (PDF + Excel)  →  ✅ ship สัปดาห์นี้ = INTERIM ระหว่างรอ network
D+ (UC share + dashboard ฝั่ง PROD)  →  🎯 TARGET — ปลดล็อกทันทีถ้าเปิด storage network path
```
**pipeline + gold table + row filter ที่ทำไว้ = ใช้ต่อได้ทั้งหมด ไม่มีอะไรเสียเปล่า**

---

## 📝 corrections จาก session นี้ (แก้ความเข้าใจเดิม)
1. ~~"D+ ตายแล้ว"~~ → **D+ conditional — ฟื้นถ้า network path เปิด** (Sarunya ยอม share UC แล้ว)
2. ~~"UC share ติด network เสมอ"~~ → **ติดเฉพาะถ้า storage firewall ปิด — เป็น layer ที่เปิดได้ด้วย private endpoint/firewall rule มาตรฐาน**
3. **row filter ทำงานข้าม workspace ได้** (metastore เดียวกัน) — ยืนยันแล้ว
4. **firewall block = error 403 ไม่ใช่ widget ว่าง** — widget ว่าง = row filter คืน 0 แถว (คนละสาเหตุ)
5. network ask เปลี่ยนจาก "browser→DEV" เป็น **"PROD compute→DEV storage (private endpoint/firewall)"** — standard Azure pattern

## ❓ ยังค้าง (ต้องได้คำตอบ)
- metastore เดียวกันจริงมั้ย (Q ข้อ 1-2 รวมกัน)
- catalog OPEN/ISOLATED
- storage network path เปิดมั้ย (PoC จะตอบ)
- Delta Sharing option (Sarunya re-check)
- external-location workspace binding

---

## 3.3 Sin's Current Grafana Alert YAML

**Status:** What Sin has deployed in Grafana today
**Env:** UAT only
**Namespace:** nsp-th-u-kafka
**Datasource UID:** PBFA97CFB590B2093
**Folder:** kafka-clsuter-alert-rule (has typo, kept for compat)
**Receiver:** test_wasin (still test channel)

**Full YAML (copy from what Sin pasted):**

```yaml
apiVersion: 1
groups:
  - orgId: 1
    name: kafka-cluster-alert-heartbeat
    folder: kafka-clsuter-alert-rule
    interval: 1h
    rules:
      - uid: afv0s7g9f3ugwf
        title: strimzi-reconciled-heartbeat-uat
        condition: C
        data:
          - refId: A
            relativeTimeRange:
              from: 3600
              to: 0
            datasourceUid: PBFA97CFB590B2093
            model:
              editorMode: code
              expr: sum(increase(strimzi_reconciliations_failed_total{kind="KafkaConnect", namespace="nsp-th-u-kafka"}[10m]) or vector(0))
              instant: true
              intervalMs: 1000
              legendFormat: __auto
              maxDataPoints: 43200
              range: false
              refId: A
          - refId: B
            relativeTimeRange:
              from: 86400
              to: 0
            datasourceUid: PBFA97CFB590B2093
            model:
              datasource:
                type: prometheus
                uid: PBFA97CFB590B2093
              editorMode: code
              expr: sum(increase(strimzi_reconciliations_failed_total{kind="KafkaConnect", namespace="nsp-th-u-kafka"}[24h]) or vector(0))
              instant: true
              intervalMs: 1000
              legendFormat: __auto
              maxDataPoints: 43200
              range: false
              refId: B
          - refId: C
            datasourceUid: __expr__
            model:
              conditions:
                - evaluator:
                    params:
                      - 0
                    type: gte
                  operator:
                    type: and
                  query:
                    params: []
                  reducer:
                    params: []
                    type: avg
                  type: query
              datasource:
                name: Expression
                type: __expr__
                uid: __expr__
              expression: A
              intervalMs: 1000
              maxDataPoints: 43200
              refId: C
              type: threshold
        noDataState: NoData
        execErrState: Error
        for: 4h
        annotations:
          description: |-
            รายงานสถานะ Kafka Connect (UAT) ประจําชั่วโมง:

            - จํานวน KafkaConnect resources ที่ทํางานอยู่: {{ $values.A }}
            - จํานวน reconciliation ที่ failed ใน 24 ชม.ล่าสุด: {{ $values.B }}

            สถานะ: {{ if eq ($values.B).Value 0.0 }}ปกติ ไม่พบ failure{{ else }}พบ failure เกิดขึ้น กรุณาตรวจสอบ{{ end }}
          summary: '[Heartbeat] Kafka Connect UAT status (resources = {{ $values.A }}, failed in last 24h = {{ $values.B }})'
        labels:
          component: kafka-connect
          env: uat
          severity: info
          team: data-platform
        isPaused: false
        notification_settings:
          receiver: test_wasin
          repeat_interval: 4h

  - orgId: 1
    name: kafka-cluster-alert-instant
    folder: kafka-clsuter-alert-rule
    interval: 5m
    rules:
      - uid: ffu1jjdx0ffggc
        title: strimzi-reconciled-failed-alert-uat
        condition: C
        data:
          - refId: A
            relativeTimeRange:
              from: 604800
              to: 0
            datasourceUid: PBFA97CFB590B2093
            model:
              editorMode: code
              expr: sum(increase(strimzi_reconciliations_failed_total{kind="KafkaConnect", namespace="nsp-th-u-kafka"}[10m]))
              instant: true
              intervalMs: 1000
              legendFormat: __auto
              maxDataPoints: 43200
              range: false
              refId: A
          - refId: B
            relativeTimeRange:
              from: 3600
              to: 0
            datasourceUid: PBFA97CFB590B2093
            model:
              datasource:
                type: prometheus
                uid: PBFA97CFB590B2093
              editorMode: code
              expr: sum(strimzi_resources{kind="KafkaConnect", namespace="nsp-th-u-kafka"})
              instant: true
              intervalMs: 300000
              legendFormat: __auto
              maxDataPoints: 43200
              range: false
              refId: B
          - refId: C
            datasourceUid: __expr__
            model:
              conditions:
                - evaluator:
                    params:
                      - 0
                    type: gt
                  operator:
                    type: and
                  query:
                    params: []
                  reducer:
                    params: []
                    type: avg
                  type: query
              datasource:
                name: Expression
                type: __expr__
                uid: __expr__
              expression: A
              intervalMs: 1000
              maxDataPoints: 43200
              refId: C
              type: threshold
        noDataState: OK
        execErrState: Error
        annotations:
          description: |-
            รายงานสถานะ Kafka Connect (UAT) ประจําชั่วโมง:

            - จํานวน KafkaConnect resources ที่ทํางานอยู่: {{ $values.A }}
            - จํานวน reconciliation ที่ failed ใน 24 ชม.ล่าสุด: {{ $values.B }}

            สถานะ: {{ if eq ($values.B).Value 0.0 }}ปกติ ไม่พบ failure{{ else }}พบ failure เกิดขึ้น กรุณาตรวจสอบ{{ end }}
          runbook_url: None
          summary: '[Heartbeat] Kafka Connect UAT - Resources: {{ $values.A }}, Failed (24h): {{ $values.B }}'
        labels:
          component: kafka-connect
          env: uat
          severity: critical
          team: data-platform
        isPaused: false
        notification_settings:
          receiver: test_wasin
          repeat_interval: 15m
```

**Known issues with existing setup (from analysis this session):**

1. **Description mislabels A/B in both rules** — says A=resources but A is actually failed count
2. **runbook_url: "None"** (literal string) — will render "None" link in email
3. **receiver: test_wasin** — still test channel, not proper DL
4. **Scope narrow** — only monitors `kind="KafkaConnect"`, ignores Kafka/KafkaTopic/KafkaUser/KafkaConnector
5. **UAT only** — no PROD equivalent yet

**NOT a bug (was called out incorrectly by Claude, corrected by Sin):**
- Heartbeat `condition: gte 0` + `for: 4h` = intentional deadman's switch pattern
  - Always fires by design → confirms monitoring is alive
  - Silence = broken monitoring/network/prometheus

---

## 3.4 HTML File (Deferred)

**Filename:** `Databricks_Governance___Deploy_vs_Job_Decision___Flow.html`
**Size:** ~167 KB
**Uploaded:** 2026-07-21
**Status:** Sin said "ขอแปะไว้ก่อนนะ เดี๋ยวมาเล่า" (parked for later explanation)

**What we know:**
- Title suggests: Governance × Deploy vs Job × Decision Flow
- Likely visual diagram/decision tree about deployment governance
- Related to Cost Dashboard or general Databricks governance

**Sin has not yet explained content — treat as pending context.**

**File location:** `/mnt/user-data/uploads/Databricks_Governance___Deploy_vs_Job_Decision___Flow.html`

---

# PART 4: New Deliverables Produced This Session

## 4.1 strimzi_alerts.yaml (1,052 lines)

**Full path:** Delivered to Sin via present_files
**Purpose:** Complete Grafana alert rules YAML — 1 heartbeat + 8 alert rules
**Metrics used:** Strimzi Cluster Operator only (no JMX/Kafka Exporter required)

**Structure:**
```
Group 1: kafka-cluster-alert-heartbeat (interval 1h)
  └── H1: strimzi-cluster-heartbeat-uat
        (9 queries A-I + threshold J, noData=Alerting deadman)

Group 2: kafka-cluster-alert-instant (interval 5m)
  ├── A1: strimzi-reconcile-fail-any-kind-uat        [CRITICAL, 5m for/15m repeat]
  ├── A2: strimzi-cluster-operator-down-uat          [CRITICAL, 2m for/15m repeat]
  ├── A3: strimzi-resource-count-dropped-uat         [WARNING, 10m for/1h repeat]
  ├── A4: strimzi-reconcile-duration-p99-slow-uat    [WARNING, 15m for/1h repeat]
  ├── A5: strimzi-resource-paused-uat                [INFO, 30m for/6h repeat]
  ├── A6: strimzi-reconcile-locked-storm-uat         [WARNING, 15m for/1h repeat]
  ├── A7: strimzi-no-reconcile-happening-uat         [WARNING, 30m for/30m repeat]
  └── A8: strimzi-kafkaconnector-not-ready-uat       [CRITICAL, 10m for/15m repeat]
```

**Config notes:**
- datasourceUid: PBFA97CFB590B2093 (Sin's Prometheus)
- namespace: nsp-th-u-kafka (UAT — duplicate for PROD)
- receiver: test_wasin (change to real DL before production)
- folder: kafka-clsuter-alert-rule (keep Sin's existing typo for compat)

## 4.2 strimzi_alerts_setup_manual.md (1,117 lines)

**Full path:** Delivered to Sin via present_files
**Purpose:** Step-by-step Grafana UI walkthrough (no code deploy)
**Reason:** Sin can't deploy code without impacting other teams

**Sections:**
- Section 1: Prep Work (verify datasource UID, contact point, folder, metrics)
- Section 2: Create Heartbeat Rule H1 (9 queries walkthrough)
- Section 3: Create Alert Rules A1-A8 (with copy-paste PromQL each)
- Section 4: Verification & Testing (Preview, force-fire test)
- Section 5: Troubleshooting (6 common problems + fixes)
- Post-Setup Checklist
- Ongoing Maintenance (PROD promotion, adding exporters)

**Time estimate:** 1-1.5 hours total
- Prep: 15 min
- Heartbeat: 20 min
- 8 alerts: 5-10 min each = 40-80 min
- Testing: 10-15 min

---

# PART 5: Current State & Pending Actions

## 5.1 Cost Dashboard Workstream (PAUSED)

**Status:** พี่ Sarunya พับไปก่อน (paused)
**Latest design state:** Artifact Factory (canonical) + D+ conditional revival

**Pending if resumed:**
- Run diagnostic queries from departmental workspace to test C11:
  ```sql
  SELECT current_metastore();  -- run in DEV + UAT + departmental
  SHOW CATALOGS;
  SELECT count(*) FROM <cat>.cost.cost_wide LIMIT 10;
  ```
- Decision tree based on result:
  - Success → D+ works, proceed
  - Permission denied → GRANT missing (fixable)
  - Table/catalog not found → workspace binding or different metastore
  - 403/timeout → network path blocked (need §6 policy ask)

**Fallback options if D+ blocked:**
- Artifact Factory Tier 0 (native email subscription) — ship immediately
- Artifact Factory Tier 1 (custom HTML) — full automation

## 5.2 Kafka Monitoring Workstream (ACTIVE FOCUS)

**Status:** Design complete, awaiting Sin's UI setup

**Immediate next actions:**
1. Sin verifies metrics exist in Prometheus (via Explore):
   ```promql
   strimzi_reconciliations_failed_total{namespace="nsp-th-u-kafka"}
   strimzi_reconciliations_successful_total{namespace="nsp-th-u-kafka"}
   strimzi_reconciliations_total{namespace="nsp-th-u-kafka"}
   strimzi_reconciliations_duration_seconds_bucket{namespace="nsp-th-u-kafka"}
   strimzi_reconciliations_locked_total{namespace="nsp-th-u-kafka"}
   strimzi_resources{namespace="nsp-th-u-kafka"}
   strimzi_resources_paused{namespace="nsp-th-u-kafka"}
   strimzi_resource_state{namespace="nsp-th-u-kafka"}  # skip A8 if absent
   up{namespace="nsp-th-u-kafka"}
   ```

2. Sin creates 9 rules via Grafana UI following the manual (1-1.5 hr)

3. Fix existing 2 alerts:
   - Description mislabel A/B
   - receiver test_wasin → real DL
   - runbook_url "None" → real URL or remove

**Phase 2 (next month):**
- Deploy Kafka Exporter (consumer lag = most business-critical missing metric)
- Deploy JMX Exporter on brokers (partition health, under-replicated)
- Deploy kube-state-metrics (pod restart, PVC usage)

**Phase 3 (production promotion):**
- Duplicate all 9 rules for PROD namespace
- Change env label uat → prod
- Change receiver to production on-call DL
- Add Alertmanager routing per severity

## 5.3 Pipeline Implementation Workstream (BACKGROUND)

**Status:** Ongoing coordination-heavy work, no active session focus

**Sin's role:**
- Design + coordinate (vendor writes code)
- SMR release cycle (Sin will explain later)
- Fan-out coordination for each new ingestion:
  1. Source owner + Source team lead approval
  2. Data Platform team approval
  3. IT helpdesk (infra provisioning + permissions on both mount hops)
  4. Vendor team implementation

**Standard flow example (mount path setup):**
```
VM source → SA fileshare → VM DP landing zone
     ↑            ↑                ↑
   Source     IT helpdesk    IT helpdesk
   owner      + permissions  + permissions
   approval   (hop 1)        (hop 2)
```

**Pending:**
- Sin to explain SMR cycle in detail
- Understand บูม's pipeline (still opaque)
- Template/checklist for ingestion request flow

## 5.4 Infrastructure Background Items

**Az login Zscaler certificate issue:**
- Recurring theme across sessions
- Need combined master-ca.crt bundle (root + intermediates + certifi bundle)
- Blocks ARM API access from Sin's machine
- Not blocking current Kafka monitoring work

---

# PART 6: Full File Inventory

## 6.1 Files in /mnt/user-data/uploads/ (Sin's uploads across sessions)

**Text/Markdown documents:**
```
aia-cost-dashboard-sharing-solution_20260712.md    (early cost dashboard)
aia-kafka-event-processing-GUIDE-export.md         (early Kafka work)
aia-kafka-mobile-session-export-20260702.md        (Kafka mobile session)
aia-new-job.md                                     (onboarding notes)
context-20260713-2342.md                          (VS Code — D+ era, SUPERSEDED)
context-20260715-vscode-uc-share-pivot.md          ⭐ LATEST
context_20260702.md                                (early context)
context_20260712.md                                (mid-cycle context)
de-streaming-architecture-and-ai-survey_20260702.md
producer-ingestion-survey_20260702.md
solution-20260713-2342.md                         (VS Code — D+ era, SUPERSEDED)
solution-artifact-factory-20260714-2040.md         ⭐ CANONICAL
solution-lakeview-details-20260713-2342.md         (SUPERSEDED)
strimzi_config_20260702.md                         (Strimzi config)
strimzi_ex_20260702.md                             (Strimzi examples)
```

**Other files:**
```
Databricks_Governance___Deploy_vs_Job_Decision___Flow.html  (Sin will explain later)
[Various screenshots and photos from Sin's phone]
```

## 6.2 Files Produced in /mnt/user-data/outputs/ (Sin's exports)

**Session exports:**
```
aia-cost-monitoring-session-export.md            (earlier session archive)
aia-kafka-mobile-session-export.md               (earlier session archive)
chat_hist_20260713_01.md                         (S01 mobile morning, 14 turns)
chat_hist_20260713_02.md                         (S02 mobile mid-day, 13 turns)
chat_hist_20260714_web.md                        (S03 post VS Code + empirical test)
chat_hist_20260715_web.md                        (S04 post Artifact Factory + network research)
feature_MlAiDashboard_vs_ADBApp.md               (Feature 3 vs 4 deep-dive)
session_context_export.md                        (older archive)
```

**Reference docs (from earlier sessions):**
```
databricks_streaming_patterns.md
de_ai_ops_guide.md
de_ml_ai_complete_reference.md
```

**⭐ NEW THIS SESSION:**
```
strimzi_alerts.yaml                              (complete Grafana alert YAML)
strimzi_alerts_setup_manual.md                   (Grafana UI setup manual)
aia_full_context_export.md                       (THIS FILE)
```

---

# 📌 Quick Reference for VS Code Agents

**If agent needs to help Sin with:**

- **Kafka alerts setup** → Read `strimzi_alerts.yaml` + `strimzi_alerts_setup_manual.md`
- **Cost dashboard design** → Read `solution-artifact-factory-20260714-2040.md` (canonical)
- **Cost dashboard D+ revival** → Read `context-20260715-vscode-uc-share-pivot.md`
- **General AIA context** → Read Section 1 (memory) + Section 5 (current state)
- **Sarunya communication** → Section 8 of artifact factory doc has script template

**Do NOT reference (superseded):**
- solution-20260713-2342.md (D+ v1 dead)
- solution-lakeview-details-20260713-2342.md (D+ details dead)
- context-20260713-2342.md (early state)

**Ethical notes for agents:**
- Sin pushes back on inaccuracy — welcome corrections
- AIA operates air-gapped — screenshots only, no code paste from AIA
- Never assume network works — verify with real test
- Distinguish governance layer (grants/bindings) vs network layer (firewall/PE)
- Sin's role is coordination-heavy at AIA, not hands-on coding like at The1

---

*End of AIA Full Context Export*

*Generated: 2026-08-16*
*By: Claude (this session)*
*For: Sin's local VS Code agents*
