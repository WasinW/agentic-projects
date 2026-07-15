---
title: Chat History — AIA Cost Dashboard Session (Web)
date: 2026-07-15
session: continuation from chat_hist_20260714_web.md
participant: สิน (วศิน) — Senior DE @ AIA
purpose: >
  Post-empirical-test session covering:
  1. Artifact Factory solution adoption (from VS Code doc)
  2. Confirmation that email-artifact = only remaining option
  3. Deep research verifying no network-layer bypass exists
canonical_solution: Artifact Factory (Tier 0 + Tier 1)
key_file_referenced: solution-artifact-factory-20260714-2040.md
---

# Chat History — 2026-07-15 (Web Session Continuation)

## Executive Summary

**Status: Design has converged.**

After empirical test (previous session) proved D+ fails cross-workspace, and after VS Code session produced the **Artifact Factory** canonical solution, this session:

1. **Absorbed the Artifact Factory design** (from `solution-artifact-factory-20260714-2040.md`)
2. **Confirmed "email-artifact = only remaining option"** with Sin
3. **Deep researched Sin's residual doubts** about whether ANY Databricks feature can bypass the network wall
4. **Verified with official docs**: No feature bypasses. Only network-layer exception (§6) or file-based egress work.

**Key finding:** All Databricks sharing/access features are **identity-layer**. Network policy operates **below** identity layer. Therefore, no identity-layer trick can bypass network enforcement. This is architectural, not a Databricks limitation.

---

## Turn 41: Rename Acknowledgment

### Context:
Previous turn Sin requested rename from `chat_hist_20260713_03.md` → `chat_hist_20260714_web.md` (Sin's naming convention: `_web` suffix distinguishes mobile chat from VS Code `_2342` timestamps).

### Sin's Message:
> "ไม่เป็นไรผมแก้แล้วแค่บอกไว้ก่อน"

= "Never mind, I fixed it myself, just letting you know."

### Response:
Acknowledged. Asked whether to continue with any topic or end for the day.

---

## Turn 42: Artifact Factory Solution Uploaded

### Sin's Message:
> "update เพิ่มครับ"

Sin uploaded: `solution-artifact-factory-20260714-2040.md`

### Content Absorbed:

**File supersedes:**
- `solution-20260713-2342.md` (C11 wrong, D+ dead)
- `solution-lakeview-details-20260713-2342.md`

**Key principle from Sin:**
> data ที่ถูก render แล้วส่งถึง "คน" = อนุญาต  
> สิ่งที่ห้าม = data ลงไปอยู่ใน "ระบบ" ฝั่ง PROD

**Reasoning chain:**
```
dashboard ทุกตัวต้อง query data ถึงจะทำงาน
   → data อยู่ DEV
      → PROD วิ่งมาอ่านไม่ได้ (R5)
      → browser ก็เปิด DEV ไม่ได้ (R5b) ⭐ NEW constraint
      → เอา dashboard ไป PROD ก็ไม่ได้ (R1/R4)
         ⇒ ❌ ไม่มี live-query solution ใดๆ อยู่รอด
         ⇒ ✅ เหลือทางเดียว: ARTIFACT ที่ render ใน DEV แล้วส่งถึงคน
```

**Design shift:**
```
Old: Dashboard sharing platform → live query cross-env
New: 🏭 Artifact Factory → render in DEV → send to "person"
```

**Solution — 2 Tiers:**

**Tier 0 (Native, zero-code, ship this week):**
```
1 AI/BI Dashboard per team (dataset ฝัง WHERE tag_team = 'TEAM_A')
├── Schedule (monthly, cron)
├── ☑ Include PDF (pages)
├── ☑ Include data (Excel/CSV) ⭐ 2026-04-16 new feature
└── Subscriber = Email notification destination (DL)

Cost: ~$5-20/year
```

**Tier 1 (Custom, ~1 month):**
```
Lakeflow Job (monthly)
├── T0: resolve_run — pin Delta version + read ops.team_recipient_map
├── T1-Tn: for_each team → render HTML/PDF/XLSX
├── T-verify: 6 assertions gate
├── T-deliver: Logic App / Graph / SMTP
└── T-ledger: audit log

Cost: ~$20/month
```

**Killed features (documented explicitly):**
```
❌ Live dashboard in their WS (R5b browser blocked)
❌ .lvdash.json import (empirical test failed)
❌ Table share cross-env (R5 blocked)
❌ External embedding (iframe → DEV = R5b)
❌ Genie scheduled tasks (subscriber must be Genie user in DEV → R3)
❌ Databricks Apps (R4 deploy blocked)
❌ Clean Rooms (wrong tool + $7,500/mo)
❌ SP push automation (R4)
```

**🆕 Critical New Feature Identified:**

2026-04-16 update to AI/BI Dashboard subscription:
- Can attach CSV/TSV/Excel (up to 100k rows) with PDF
- Previously PDF only (2016-2026 stable)
- Enables Tier 0 shipping without any code

**Isolation Model Change:**
```
Old: UC row filter (with embed_credentials trap)
New: By-construction (1 dashboard per team = physically separate)
    → No RLS trap
    → No credentials mode confusion
    → No silent leaks
```

**Policy Ask §6 (endgame):**
> "ขอเปิดให้ browser ของ user (เฉพาะ Entra group `finops-cost-viewers`) เข้าถึง host ของ DEV Databricks workspace ได้ — HTTPS 443, front-end, read-only"

**Roadmap:**
| When | What | Effort | Result |
|---|---|---|---|
| This week | Tier 0 native subscriptions | 1 day, 0 lines | Ship immediately |
| This month | Artifact Factory | 5-8 person-days | Full automation |
| Parallel | M365 admin asks + Graph API outbound | — | Unlock SharePoint |
| Endgame | §6 policy ask | 1 doc | Live URL back in 2 days |

### My Response:

Acknowledged as canonical solution. Explicitly listed my earlier mobile session errors that this replaces:
- SQL warehouse workspace affinity claim (WRONG)
- Feature 3 vs Feature 4 security emphasis (WRONG — same when Mode B)
- SP proxy suggestions (violate C4/R4)

Noted the 2026-04-16 feature update as game-changer.

Highlighted trap avoidance:
- 9MB attachment cap
- 100k rows Excel silent truncation
- Unsubscribe = DL fallout
- SDK Schedule field limitations

---

## Turn 43: Confirmation of Direction

### Sin's Question:
> "ตกลง อันนี้เหลือ option export sent mail แทนแล้วมั้ยนะ"

### Response:

Confirmed: Yes — deliverable = render + send file to person. All other options dead from R5b.

**Only 2 tiers remaining:**
```
Tier 0: Native email subscription (this week)
Tier 1: Custom Artifact Factory (this month)
```

**All alternatives explicitly dead:**
- Live dashboard in their WS (R5b)
- .lvdash.json import (empirical proven)
- Table share cross-env (R5)
- External embedding (R5b)
- Genie scheduled tasks (R3)
- Databricks Apps (R4)
- Clean Rooms (overkill + wrong tool)
- SP push automation (R4)

**Channel ranking:**
```
Ship now:    Email attachment (approved, fragile isolation)
Aim month 2: SharePoint page per team (ACL isolation, revocable, audit)
Backup:      SharePoint/OneDrive link
Endgame:     Live link (requires §6 policy)
```

**Noted:** Sin had this insight from the very beginning (earlier turn: "ทำเป็น physical เลย คือ user ดู dashboard ของตัวเองที่ไม่ต้องมาแตะ data เลย") — I only accepted it after full circle.

---

## Turn 44: Deep Research Request — Can ANYTHING Bypass Network?

### Sin's Question:
> "อยากให้ช่วย deep research หน่อยว่าถ้าติดปัญหาเรื่อง network การจะพยายามข้ามโดยใช้วิธีอื่นมันไม่ได้จริงๆ รึป่าว เช่นการ shared uc หรือ การต้องสร้าง services principles ที่ prod แล้วส่ง credentials ให้ dev ไรงี้ หรือ แค่แชร์ dashboard ที่ dev ให้ user groups ที่ env prod ไรงี้ พวกนี้มันข้าม network ได้มั้ยนะ"

### Research Performed:

Three targeted web searches:
1. "Databricks Unity Catalog cross-workspace network requirements data plane VNet"
2. "Delta Sharing OpenSharing network requirements recipient reads storage direct"
3. "Databricks service principal cross-workspace token secret scope security policy"
4. "Databricks AI/BI dashboard cross-workspace share account users browser access"

### Key Documentation Findings

**1. Fundamental Architecture — Control Plane vs Data Plane:**

Microsoft Learn (VNet injection docs):
> "The outbound rule to the AzureDatabricks service tag (ports 443, 3306, 8443–8451) serves the following purposes:
> 443: for Azure Databricks infrastructure, cloud data sources, and library repositories
> 8443: for internal calls from the Azure Databricks compute plane to the Azure Databricks control plane API"

**Implication:** Compute plane connects to both control plane AND storage directly. If storage is in different VNet with policy blocking → dead at network layer, before any Databricks feature logic executes.

**2. Serverless Compute — Same Enforcement:**

Databricks Platform SME blog (Karthik Subbarao):
> "Therefore, to securely access your storage from the serverless compute plane, you need to create an NCC and either allowlist the network identifiers on your storage account, for intra-region storage storage access, or create a private endpoint."

**Implication:** Even serverless (Databricks-managed) compute needs storage allowlisted. NCC controls it. Same wall.

**3. OpenSharing — Direct Storage Access:**

Databricks official docs:
> "When you share eligible Delta tables using Databricks-to-Open sharing, Databricks returns the table's cloud storage location alongside temporary cloud credentials (cloud tokens) that recipients can use to read data directly from cloud storage."

Setup docs:
> "A cloud storage configuration that allows network access from the recipient."

**Implication:** OpenSharing = provider gives storage location + temp token. Recipient reads directly. Network config from recipient to provider's storage = prerequisite.

**4. Dashboard Cross-Workspace Sharing — Compute Stays with Publisher:**

Microsoft Learn:
> "Compute access is always granted by the publisher's credentials."

Interesting nuance: Even with Individual Data Permissions, compute (SQL Warehouse) is publisher's. So data plane doesn't cross env.

**BUT:**
> "Registered members of your Databricks account without workspace access can be granted access to a view-only copy of a dashboard."

Users see dashboard by opening its URL. URL points to publisher's workspace. Client's browser must reach DEV workspace URL.

**Implication:** Even though data plane doesn't cross env, HTTP request from viewer's browser → DEV workspace URL crosses env. R5b blocks this.

**5. Cross-Env Token Storage — Explicitly Forbidden (AIA):**

From Sin's context doc (confirmed 2026-07-13):
> "ทีม Cybersecurity/Infra ไม่อนุญาตให้สร้าง Secret Scope ที่ฝั่ง Dev เพื่อเก็บ Token ของฝั่ง Prod ข้ามสภาพแวดล้อม"

**Implication:** Even if SP-based scheme worked technically, AIA policy explicitly forbids the credential storage pattern.

### Verdict Table

| Scenario | Layer | Blocked By | Bypass Possible? |
|---|---|---|---|
| UC GRANT (same metastore) | Identity | R5 (data plane cross-env) | ❌ No |
| OpenSharing (cross-metastore) | Identity | R5 (direct storage read) | ❌ No |
| SP + cross-env token | Identity + Security | R5 + explicit token policy | ❌ No |
| Dashboard share (Shared mode) | Identity | R5b (browser cross-env) | ❌ No |
| Dashboard share (Individual mode) | Identity | R5b (browser cross-env) | ❌ No |
| Private Link peering | **Network** | Requires approval | ⚠️ = §6 policy ask |
| Serverless compute + NCC | Identity | Storage allowlist | ❌ No |
| Databricks Apps | Identity | R5b (browser) | ❌ No |
| MV / Streaming Table | Compute | R5 (refresh needs source) | ❌ No |

### The Fundamental Truth

```
Databricks features architecture layers:

┌──────────────────────────────────┐
│  IDENTITY layer                   │ ← UC, SP, Dashboard sharing
│  (WHO can access?)                │   OpenSharing, Apps
└──────────────────────────────────┘
              │
              ▼ Feature logic runs HERE
┌──────────────────────────────────┐
│  NETWORK layer                    │ ← Firewall, NSG, VNet policy
│  (CAN this TCP connection happen?)│   Private endpoint, allowlist
└──────────────────────────────────┘
              │
              ▼ Enforced FIRST
              │  Before identity check
              │
              ▼
      Network says NO → Feature never gets to run
```

**Only 2 ways to actually bypass network:**

1. **Network-layer exception** (change the network policy)
   - Private Link peering
   - Firewall rule exception
   - IP allowlist
   - = §6 policy ask in Artifact Factory doc

2. **Sidestep entirely** (don't use Databricks for delivery)
   - Render artifact in DEV
   - Send via approved corporate channels (email, SharePoint)
   - = Artifact Factory approach

### Response Summary Delivered:

**TL;DR: All 3 scenarios blocked. Databricks features cannot bypass network policy — architecturally impossible.**

Explained control/data plane separation. Went through each scenario with citations. Confirmed:
- Artifact Factory = only viable design in constraint space
- §6 policy ask = only path to restore "live in their workspace" experience
- No technical shortcut exists

Sin's insight from the beginning was correct.

---

## Turn 45: This Export Request

### Sin's Message:
> "Export ของวันนี้มาหน่อย"

### Response:
This document.

---

## 🎯 Session-End State

### Design Convergence Complete

**Canonical solution: Artifact Factory** (from `solution-artifact-factory-20260714-2040.md`)

**No further Databricks-native alternatives to explore** — the constraint space has been exhaustively mapped:

```
Available network egress from DEV:
├── ✅ Email (control plane routed) → Tier 0
├── ✅ Graph API outbound (SharePoint) → Tier 1 enhancement
├── ✅ SMTP relay (if enabled) → Tier 1 backup
└── ❌ Direct data plane cross-env (blocked by policy)

Deliverable form:
├── ✅ Rendered artifact (PDF/HTML/Excel) → sent as file
├── ❌ Live dashboard in target workspace (R4 + R5b)
└── ❌ Cross-workspace table access (R5)

Automation:
├── ✅ Lakeflow Job for_each team (fully automated)
├── ✅ Native subscription (zero-code, this week)
└── ❌ Any Sin-initiated deploy to departmental
```

### Confirmed Path Forward

**Week 1 (Tier 0):**
- Build 1 AI/BI Dashboard per team in DEV
- Dataset with `WHERE tag_team = 'TEAM_A'` embedded
- Configure schedule + email destination
- ☑ Include PDF pages
- ☑ Include Excel data attachment (2026-04-16 feature)
- Deliver first monthly reports
- Cost: ~$5-20/year

**Month 1 (Tier 1):**
- Build Lakeflow Job with for_each pattern
- Custom HTML renderer (ECharts inline, offline-interactive)
- Excel with PivotTable/slicer
- Verify gate (6 assertions)
- Delivery via Logic App / Graph / SMTP
- Artifact ledger + audit log
- Mapping table (SCD2 approvable)
- Cost: ~$20/month

**Parallel:**
- Request M365 admin: HTML rendering on FinOps SharePoint site
- Request network: DEV → Graph API outbound
- Draft §6 policy ask document
- Present to Sarunya using script in Artifact Factory §8

**Endgame:**
- If §6 approved → restore dashboard-in-their-place in 2 days
- Same Tier 1 pipeline reusable
- No wasted work

### Open Questions Still Pending (from Artifact Factory doc §9)

| # | Question | Impact |
|---|---|---|
| Q1 | SMTP relay approved in DEV? | Effort of T3 |
| Q2 | DEV → Graph API outbound allowed? | SharePoint path unlocking |
| Q3 | "No data to PROD" = platform or environment? | If laptop/Outlook counts → email also violates |
| Q4 | Purview sensitivity labels on tenant? | DNF real vs theater |
| Q5 | Tag hygiene % coverage for tag_team | Chargeback credibility |
| Q6 | Number of teams (5 vs 30)? | Operational cost scales |
| Q7 | บูม's pipeline scope? | Duplicate work risk |

### Files Produced Today (2026-07-14 through 2026-07-15)

| File | Purpose |
|---|---|
| `chat_hist_20260713_01.md` | Mobile Session 01 (morning) |
| `chat_hist_20260713_02.md` | Mobile Session 02 (afternoon) |
| `chat_hist_20260714_web.md` | Mobile Session 03 (post VS Code + empirical test) |
| `chat_hist_20260715_web.md` | This file — post Artifact Factory adoption + network deep research |
| `feature_MlAiDashboard_vs_ADBApp.md` | Feature deep-dive reference |
| `context-20260713-2342.md` | VS Code — early context |
| `solution-20260713-2342.md` | VS Code — D+ era (SUPERSEDED) |
| `solution-lakeview-details-20260713-2342.md` | VS Code — D+ details (SUPERSEDED) |
| `solution-artifact-factory-20260714-2040.md` | ⭐ **CANONICAL SOLUTION** |

### Ethical Note

Multiple times during this multi-session engagement, I proposed solutions that:
1. Violated stated policies (R4/C4 via SP push)
2. Made unverified technical claims (compute affinity, feature security)
3. Failed to recognize the fundamental network layer distinction earlier

**Sin's contributions were essential:**
- Multiple pushbacks correcting me
- Empirical test that falsified D+ (invaluable data)
- Original intuition ("physical export") that ultimately proved correct
- Refusing to accept my SP proxy suggestions despite my repetition
- Bringing in VS Code agents' work for parallel verification
- Fact-checking Gemini's "cache" claim by testing

The correct solution — Artifact Factory — was ultimately produced by the VS Code session in parallel. This web session's contribution:
1. Empirical validation (D+ dead)
2. Fact-checking competing AI proposals (Gemini's cache claim)
3. Rejecting alternatives with evidence (Clean Rooms, SP push)
4. Deep verification that no network-layer bypass exists

**Key lesson for future sessions:**
- Network policy operates at a different layer than identity/permission features
- Feature-layer solutions cannot bypass network-layer enforcement
- When constraints appear to conflict, empirical testing settles debates faster than analysis
- Sin's intuition consistently ran ahead of my analysis

### Message Sin Can Use with Sarunya (from Artifact Factory §8)

> พี่ Sarunya ครับ — มีข่าวไม่ดี 1 ข้อ กับข่าวดี 2 ข้อครับ
>
> **ข่าวไม่ดี:** "dashboard ที่อยู่ใน workspace ของ client เอง" — ตอนนี้ **สร้างไม่ได้จริงๆ** ครับ ไม่ใช่เพราะ Databricks ทำไม่ได้ แต่เพราะ **policy ปิดทุกทางที่ data จะเดินออกจาก DEV**: copy ไม่ได้ · share ไม่ได้ · PROD วิ่งมาอ่าน DEV ไม่ได้ · **browser ของ client เองก็เปิด URL ของ DEV ไม่ได้** ทางเดียวที่เหลือคือ **ไฟล์ที่ render ใน DEV แล้วส่งถึง "คน"**
>
> **ข่าวดีที่ 1:** ผมจะทำ **"โรงงานผลิต report"** — Databricks Job รันเดือนละครั้ง fan-out ทีละทีม **แต่ละทีมเห็นเฉพาะ cost ของตัวเอง by construction** ส่งอัตโนมัติ ไฟล์ HTML **interactive ได้จริง** + Excel ให้ Finance
>
> อ้อ — และมี **feature ใหม่ Databricks (เม.ย. 2026)** ที่ช่วยเราพอดี: subscription แนบ **Excel/CSV** ได้แล้ว → ตั้ง native subscription **สัปดาห์นี้ zero code**
>
> **ข่าวดีที่ 2:** เหลือ **การขอ policy แค่ข้อเดียว** = *"browser ของ user (เฉพาะ group) เปิด DEV URL ได้ read-only"* — ไม่มี data ลง PROD ไม่มี copy
>
> ประเด็นสำหรับ security: **วันนี้เราส่ง cost data ทางอีเมล — forward ต่อได้ ถอนคืนไม่ได้** ส่วนวิธี link — **data ไม่ออกจาก DEV เลย** audit ได้ทุก query **policy ปัจจุบันบังคับให้เราใช้ช่องทางที่ปลอดภัยน้อยกว่า**

---

*End of Chat History — 2026-07-15 Web Session*

**Handover complete for VS Code agents.**  
**Ready for Tier 0 build to start.**
