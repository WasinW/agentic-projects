# Option D+ — Tech Stack · Architecture · Flow · UI Manual · Deployment (2026-07-13, 23:42)

> ## ☠️ DEAD — 2026-07-14
> **Option D+ ตายแล้ว** — dashboard ที่ import ไปฝั่ง departmental PROD จะ **live query กลับมาที่ table ใน coredata DEV** แต่ **PROD วิ่งมา DEV ไม่ได้** (network) และ **จะไม่เปิด shared แม้อยู่ใน UC เดียวกัน** → `.lvdash.json` ที่ import ไปจะ **"table not found" เสมอ** (มันพก query text + widget config เท่านั้น **ไม่เคยพก data**)
> 👉 **อ่าน `solution-artifact-factory-20260714-2040.md` แทน**
> เก็บไฟล์นี้ไว้เพราะ **§ trap runbook + publish-mode + `is_account_group_member()` ยัง valid** และจะได้ใช้ทันทีถ้า policy §6 ผ่าน

> **~~The winner.~~** The only option satisfying all 11 constraints. Everything here is **GA on Azure Databricks** (no Preview dependency). Companions: `context-20260713-2342.md` · `solution-20260713-2342.md`.
> **One-line summary:** *Grant the data (with a row filter). Hand over the dashboard as a file. They import it into **their** workspace, publish it with **Individual data permissions**, run it on **their** warehouse.*
> **Names are placeholders** — no AIA identifiers here. Adapt locally.

---

# 1. TECH STACK — exactly which Databricks features are used

## 1.1 Unity Catalog (the governance layer — this is what makes row-level work)
| Feature | Role | Status |
|---|---|---|
| **UC Privileges (`GRANT`)** | `USE CATALOG` / `USE SCHEMA` / `SELECT` / **`EXECUTE`** → let the client's account groups read the gold table | GA |
| **UC Row Filter** (`ALTER TABLE … SET ROW FILTER` + `is_account_group_member()`) | each team sees only its own rows | GA |
| ↳ *or* **ABAC Policies** (tag-driven, catalog/schema-level) | the modern, scalable alternative — **Databricks now recommends ABAC over per-table row filters** | GA (2025) |
| **Workspace-Catalog Binding** | let the departmental workspace *reach* the catalog (`OPEN`, or add it `BINDING_TYPE_READ_ONLY`) | GA |
| **Account Groups** (Entra → Databricks account via **Automatic Identity Management** / SCIM) | the identity that the row filter evaluates | GA (AIM default for accounts created after 2025-08-01) |

## 1.2 AI/BI Dashboard (= **Lakeview** — the same product; API path is still `/api/2.0/lakeview/…`)
| Feature | Role | Status |
|---|---|---|
| **AI/BI Dashboard** | the dashboard itself (**not** the retired "Databricks SQL Dashboard") | GA |
| **Dashboard Export / Import** (`.lvdash.json`, Workspace API or UI) | **the mechanism that satisfies C4 + C6** — Sin exports, *they* import | GA |
| **Publish → "Individual data permissions"** (`embed_credentials: false`) | queries run as the **viewer** → the UC row filter fires per user 🚨 | GA |
| **Dashboard permissions (Share)** | `CAN VIEW` to each team's group | GA |
| **Scheduled subscriptions** | monthly PDF/Excel to email / Teams (C8) | GA |

## 1.3 Compute
| Feature | Role |
|---|---|
| **Serverless SQL Warehouse** — **in the departmental workspace** | runs the dashboard's queries → **the client pays the DBUs** (C7 = real chargeback). Auto-stop 5–10 min. |

## 1.4 Optional add-ons
| Feature | Why | Status |
|---|---|---|
| **Genie One** (`https://<workspace>/one`) | the clean business-user UI — makes the dashboard feel like a *product*, not a file. **Probably the "new feature" the stakeholder is asking about.** Needs workspace membership + **Consumer access**. | GA |
| **Genie Agent** (ex-Genie Space) | natural-language cost questions; **UC row filters still enforced per user** | GA (⚠️ PAYG LLM DBUs since 2026-07-08) |
| **DAB / Git folders** | CI/CD for the dashboard file | DAB GA · **Git-folder dashboards = Public Preview** |

## 1.5 NOT used
❌ Databricks Apps (can't deploy into their workspace; 24/7 billing; 2-4× cost) · ❌ Delta Sharing/OpenSharing (same metastore; can't share row-filtered tables) · ❌ Legacy SQL Dashboard (retired) · ❌ Dashboard embedding (that *is* the "anyone with the link" fear) · ❌ Lakehouse Federation.

---

# 2. ARCHITECTURE

```
┌──────────────────── DATABRICKS ACCOUNT (identity tier) ────────────────────┐
│  Entra ID ──(Automatic Identity Management / SCIM)──▶ ACCOUNT GROUPS:       │
│      cost-platform-admins · client-team-a · client-team-b · client-team-c   │
│  ⚠ Account groups resolve in ANY workspace on the metastore.                │
│  ⚠ A GRANT to them creates ZERO workspace membership.                       │
└───────────────────────────────┬────────────────────────────────────────────┘
                                │
┌──────────────── UNITY CATALOG METASTORE (data tier — shared) ───────────────┐
│  catalog: finops                                                            │
│    schema: cost                                                             │
│      TABLE  cost_gold  (usage_date, service_name, resource_group,           │
│                         tag_team ◀── top-level col, NOT inside the MAP,     │
│                         tags MAP<STRING,STRING>, amortized_cost, …)         │
│      FUNCTION fn_cost_rls(team)  ── ROW FILTER ON (tag_team)                │
│      TABLE  team_access_map (team_tag, account_group, user_email)  [opt]    │
│                                                                             │
│  workspace binding:  coredata = READ_WRITE  |  departmental = READ_ONLY  ①  │
│  grants ②: USE CATALOG + USE SCHEMA + SELECT + EXECUTE → client-team-*      │
└──────────┬──────────────────────────────────────────────┬───────────────────┘
           │                                              │
┌──────────┴─── WORKSPACE: coredata (DEV / IT) ───┐   ┌───┴── WORKSPACE: departmental (PROD / CLIENT) ──┐
│                                                 │   │                                                 │
│  Cost Mgmt Export → ADLS → pipeline (Sin)       │   │  ③ Catalog Explorer ▶ finops.cost.cost_gold      │
│     bronze→persist→prep→summary→GOLD            │   │        ← the table APPEARS here                  │
│  Sin authors the dashboard here, then EXPORTS   │   │                                                 │
│     ⤵  cost_dashboard.lvdash.json  ────────────────▶│  ④ Dashboards ▶ "Cloud Cost"                     │
│                                                 │   │        imported by THEIR admin (one time)        │
│  ✗ CLIENTS NEVER ENTER THIS WORKSPACE           │   │        published: INDIVIDUAL data permissions 🚨 │
│  ✗ Sin never deploys into departmental          │   │        runs on THEIR serverless SQL warehouse    │
│                                                 │   │        ⇒ THEY PAY  ⇒ real chargeback             │
│                                                 │   │        CAN VIEW → client-team-a / -b / -c        │
│                                                 │   │  ⑤ Genie One (/one) = clean business-user view   │
└─────────────────────────────────────────────────┘   └─────────────────────────────────────────────────┘

① catalog→workspace BINDING   (metastore admin / catalog owner)   ← NOT workspace membership
② UC GRANT to ACCOUNT GROUPS  (catalog owner = Sin)               ← NOT workspace membership
③ a TABLE is the ONLY Databricks object that materialises inside someone else's workspace
④ the DASHBOARD is a FILE handed over — not a deployment (this is how C4 is satisfied)
⑤ optional consumption skin
```

**The three facts the whole design rests on**
1. **Identity = account. Data = metastore. Compute = workspace.** Three separate tiers. A UC grant touches only the middle one.
2. **The publisher's identity and warehouse run the query.** ⇒ publish it *in their workspace, by their user* → their RLS, their bill.
3. **Only a table/view appears in another workspace's UI.** A dashboard/app is always workspace-local ⇒ to get it "inside their workspace", the object must be *created there* — by them, from a file we give them.

---

# 3. FLOW

## 3.1 Build-time (one-time setup)
```
Sin @ coredata                                   Departmental admin @ their WS
──────────────                                   ────────────────────────────
0. verify: same metastore ✓
   verify: their group is an ACCOUNT group ✓
   verify: catalog binding (OPEN or add READ_ONLY)
1. project tag_team out of the MAP → top-level col
2. CREATE FUNCTION fn_cost_rls(...)
3. ALTER TABLE ... SET ROW FILTER
4. GRANT USE CATALOG/SCHEMA/SELECT/EXECUTE
   → client-team-* (ACCOUNT groups)
5. build the AI/BI dashboard
6. Export → cost_dashboard.lvdash.json ──────────▶ 7. Import dashboard from file
                                                  8. MOVE to /Workspace/Shared/FinOps/
                                                  9. point dataset at THEIR warehouse
                                                 10. Publish → INDIVIDUAL data permissions 🚨
                                                 11. Share → CAN VIEW to client-team-*
                                                 12. Warehouse Permissions → CAN USE
                                                 13. Schedule → monthly PDF (optional)
```

## 3.2 Run-time (what a client user experiences)
```
User (team A) opens THEIR departmental workspace
   └▶ Sidebar → Dashboards → "Cloud Cost"        (no link, no email — it's just there)
        └▶ query runs on THEIR serverless SQL warehouse, as THEIR identity
             └▶ UC row filter: is_account_group_member('client-team-a') → TRUE
                  └▶ returns ONLY team A's rows
                       └▶ DBUs billed to THEIR workspace ✅
User (team B) opens the SAME dashboard  →  sees ONLY team B's rows
```

## 3.3 Monthly cadence
`Dashboard → Schedule (monthly, 1st, 08:00) → Subscribers = each team's email/Teams destination → PDF`
⚠️ **Test with 2 users from 2 teams first.** If the PDF is not per-viewer filtered, fall back to **one schedule per team** with only that team's distribution list.

---

# 4. SQL — the complete data-side setup (run in coredata)

```sql
-- ═══ STEP 0 · PREREQ: tag_team must be a TOP-LEVEL column ═══
-- A row filter CANNOT bind to a key inside a MAP<STRING,STRING>.
-- Project the governed key out; keep the MAP for the long tail.
CREATE OR REPLACE TABLE finops.cost.cost_gold AS
SELECT
    usage_date, subscription_id, resource_group, resource_id,
    service_name, meter_id,
    lower(tags['team'])        AS tag_team,        -- ⭐ governed key → top-level
    tags['environment']        AS tag_environment,
    tags['costcenter']         AS tag_cost_center,
    tags                       AS tags,            -- keep the MAP
    amortized_cost, actual_cost, currency
FROM finops.cost.summary_cost_with_tags;

-- ═══ STEP 1 · ROW FILTER FUNCTION ═══
-- ⚠️ is_account_group_member()  — NEVER is_member() (that is workspace-local and
--    silently returns FALSE for your entire audience → 0 rows, no error).
-- ⚠️ The parameter type MUST match the column type exactly, and run with
--    spark.sql.ansi.enabled = true — a type mismatch can silently return ALL rows.
CREATE OR REPLACE FUNCTION finops.cost.fn_cost_rls(team_tag STRING)
RETURN
    is_account_group_member('cost-platform-admins')                    -- IT/FinOps: see all
    OR is_account_group_member(concat('client-team-', lower(team_tag))); -- each team: own rows

-- ═══ STEP 2 · ATTACH THE FILTER ═══
ALTER TABLE finops.cost.cost_gold
    SET ROW FILTER finops.cost.fn_cost_rls ON (tag_team);

-- ═══ STEP 3 · GRANTS (repeat per team group — use ACCOUNT groups) ═══
GRANT USE CATALOG  ON CATALOG  finops                    TO `client-team-a`;
GRANT USE SCHEMA   ON SCHEMA   finops.cost                TO `client-team-a`;
GRANT SELECT       ON TABLE    finops.cost.cost_gold      TO `client-team-a`;
GRANT EXECUTE      ON FUNCTION finops.cost.fn_cost_rls    TO `client-team-a`;  -- ⚠️ MOST-FORGOTTEN
-- …repeat for client-team-b, client-team-c

-- ═══ STEP 4 · VERIFY ═══
SHOW GRANTS ON TABLE finops.cost.cost_gold;
-- and have a REAL team user run, in the departmental workspace:
--   SELECT current_user(), is_account_group_member('client-team-a');   -- must be TRUE
--   SELECT count(*) FROM finops.cost.cost_gold;                        -- must be ONLY their rows
```

### Optional — mapping-table–driven filter (recommended for chargeback at scale)
Decouples Azure tag hygiene from Entra group names; onboarding a team = one `INSERT`, no DDL.
```sql
CREATE TABLE IF NOT EXISTS finops.cost.team_access_map (
    team_tag      STRING,   -- value in cost_gold.tag_team
    account_group STRING,   -- Databricks account group
    user_email    STRING    -- fallback path (Option A′) — include from day one
);
-- ⚠️ The mapping table itself must have NO row filter (a filtered table cannot be
--    referenced by another filter) and must be locked down + change-controlled.
```

### Optional — ABAC policy instead of a per-table row filter (Databricks-recommended)
Apply a tag-driven policy at catalog/schema level so every cost table inherits it — no per-table DDL. Requires DBR 16.4+/serverless.

---

# 5. USER MANUAL — step by step through the UI

## 🟦 PART A — Sin, in the **coredata** workspace

### A0 · Verify the prerequisites (do this FIRST — it decides everything)
1. **Same metastore?** In a coredata notebook:
   `spark.sql("SELECT current_metastore()").show(truncate=False)`
   Ask a departmental user to run the same. **IDs must match.** (`SELECT current_metastore()` does **not** work on a SQL warehouse — use a notebook, or `databricks metastores current`.)
2. ⭐ **Is their team group an ACCOUNT group?** Have a **real team user** run, **in departmental**:
   ```sql
   SELECT current_user(), is_account_group_member('client-team-a');
   ```
   * `true` → ✅ proceed.
   * `false` → their group is **workspace-local (legacy)** → it can't be granted UC data access **from anywhere**. **Escalate to the Databricks ACCOUNT admin** to create/sync account groups from Entra. *(This is NOT a coredata change and adds nobody to coredata.)*
   * You can also check the **Source** column: departmental **Admin settings → Identity and access → Groups** — must read **Account** or **External**, not *Workspace*.
3. **Is the catalog workspace-bound?**
   **Catalog Explorer → `finops` → Workspaces tab**
   * "**All workspaces have access**" ticked → `OPEN` → ✅ nothing to do.
   * Otherwise (`ISOLATED`) → **Assign to workspaces** → pick **departmental** → **Manage access level → Read-only**.
   * CLI: `databricks workspace-bindings get-bindings catalog finops`
   > 🔎 A binding lets that workspace's **compute** reach the catalog. It grants **no human anything** — `GRANT` + the row filter still gate every row.

### A1 · Prepare the data
Run the SQL in **§4** (steps 0–4).

### A2 · Build the dashboard
1. Sidebar → **+ New → Dashboard**
2. **Data** tab → **Add dataset**:
   ```sql
   SELECT usage_date, service_name, resource_group, tag_team, tag_environment,
          SUM(amortized_cost) AS cost
   FROM finops.cost.cost_gold
   WHERE usage_date >= add_months(current_date(), -6)
   GROUP BY ALL
   ```
   → attach a SQL warehouse (coredata's, just for authoring).
   > 💡 **Do NOT add `WHERE tag_team = …`** — the UC row filter does that per viewer.
3. **Canvas** tab → build the pages:
   * Row 1 — **KPI counters**: MTD cost · vs last month · forecast
   * Row 2 — **Line**: daily cost trend (30–90 d) with a 7-day moving average
   * Row 3 — **Bar (sorted)**: top services · top resource groups
   * Row 4 — **Table**: top resources
   * (optional) a page per view: Overview / Trend / Chargeback / Detail
4. **Save.**

### A3 · Export the file
Top-right **⋮ (kebab)** → **File actions → Export** → downloads **`cost_dashboard.lvdash.json`**.
*(API equivalent: `GET /api/2.0/workspace/export?path=…&direct_download=true&format=AUTO`)*

### A4 · Hand over
Send the `.lvdash.json` to the departmental admin, together with the **written checklist** in §5-B. **Do not skip the written note about the publish mode** — it is the one step that, if missed, becomes a data leak.

---

## 🟩 PART B — the **departmental admin**, in **their** workspace (one time, ~15 min)

### B1 · Import
1. Sidebar → **Dashboards**
2. Click the **caret (˅)** next to **Create** → **Import dashboard from file**
3. Upload `cost_dashboard.lvdash.json`

### B2 · 🚨 Move it to a shared folder
The import lands in **the importer's personal folder** — nobody else can see it.
**Workspace** → find the dashboard → **⋮ → Move** → **`/Workspace/Shared/FinOps/`**

### B3 · 🚨 Point it at *your* warehouse
Open the dashboard → **Data** tab → select the dataset → change the **SQL warehouse** to **your own** (serverless, auto-stop ≤10 min).
*(If you skip this it still points at coredata's warehouse → it breaks, or IT gets billed.)*

### B4 · 🚨🚨 Publish — **"Individual data permissions"**
**Publish** (top-right) → choose **"Individual data permissions"**.
> ❌ **NEVER choose the default "Share data permissions".** That runs every viewer's query with the **publisher's** credentials → the row filter evaluates as the publisher → **every team sees every team's cost.** Silent. No error. This is the single most dangerous click in the whole build.

### B5 · Share
**Share** → add each team's **account group** → permission **CAN VIEW**.
> ❌ Do **not** use **"Anyone in my account can view"**.

### B6 · Warehouse permissions
**SQL Warehouses** → the warehouse → **Permissions** → each team group → **CAN USE**.
Also confirm the team users hold the **Databricks SQL / Consumer access** entitlement.
> ⚠️ **Entitlement change: auto-enabled 2026-07-27, enforced 2026-09-14** — the `users` system group loses entitlements. **Grant Consumer access explicitly**, or your users will lose access mid-rollout.

### B7 · Monthly schedule (optional)
**Schedule** → Monthly, 1st, 08:00 → **Subscribers** = each team's email / Teams destination → format **PDF**.

---

## ✅ PART C — Test before you call it done
| # | Test | Expected |
|---|---|---|
| 1 | A **team-A** user opens their workspace → **Dashboards** | "Cloud Cost" is listed (no link needed) |
| 2 | They open it | **Only team-A rows** |
| 3 | A **team-B** user opens the same dashboard | **Only team-B rows** |
| 4 | Neither user can reach the coredata workspace | ✅ (they were never added) |
| 5 | Billing | DBUs land on the **departmental** warehouse |
| 6 | Monthly schedule fires | each team's PDF contains **only their data** ← **test with 2 users / 2 teams** |
| 7 | Genie One (`/one`) — optional | dashboard shows in the clean business-user UI |

---

# 6. DEPLOYMENT — from manual to automated

## 6.1 Manual (PoC / first drop) — what §5 describes
Export → email the file → they import. **Zero infrastructure.** Best for the PoC.

## 6.2 Semi-automated — versioned file, manual import
Keep `cost_dashboard.lvdash.json` in **Bitbucket** (alongside the pipeline). Sin re-exports on change; the departmental admin re-imports.
⚠️ Re-exports can diff noisily — the `.lvdash.json` schema drifts across releases. Don't build a golden-file test on it.

## 6.3 Automated — **DAB + service principal** ⭐ (best long-term)
Ask the departmental admin for **one service principal** with **CAN MANAGE on one folder** — a far softer ask than adding a person to a workspace.

```yaml
# databricks.yml
bundle:
  name: cost-dashboard

variables:
  warehouse_id:
    description: The DEPARTMENTAL serverless SQL warehouse

targets:
  departmental:
    workspace:
      host: https://<departmental-workspace-url>
      root_path: /Workspace/Shared/FinOps
    variables:
      warehouse_id: <THEIR_WAREHOUSE_ID>          # ⚠️ NOT coredata's
    run_as:
      service_principal_name: sp-costdash

resources:
  dashboards:
    cost_dashboard:
      display_name: "Cloud Cost"
      file_path: ./src/cost_dashboard.lvdash.json
      warehouse_id: ${var.warehouse_id}
      embed_credentials: false                    # 🚨 = "Individual data permissions"
      permissions:
        - group_name: client-team-a
          level: CAN_VIEW
        - group_name: client-team-b
          level: CAN_VIEW
```
```bash
databricks bundle validate -t departmental
databricks bundle deploy   -t departmental        # run as sp-costdash
# regenerate the JSON after editing in the UI:
databricks bundle generate dashboard --resource cost_dashboard
```
**What the SP needs in the departmental workspace:** workspace member · **CAN MANAGE (or CAN EDIT) on `/Workspace/Shared/FinOps`** · **CAN USE** on their warehouse.
🚨 **Pin `embed_credentials: false` in the bundle** — never rely on the UI default.

## 6.4 CI/CD (Jenkins — matches AIA's existing Kafka platform pattern)
```groovy
pipeline {
  stages {
    stage('Validate') { steps { sh 'databricks bundle validate -t departmental' } }
    stage('Deploy')   {
      when { branch 'main' }
      input { message "Deploy cost dashboard to departmental?" }
      steps { sh 'databricks bundle deploy -t departmental' }
    }
  }
}
```

## 6.5 Git folders (alternative)
Databricks **Git folders** can materialise a `.lvdash.json` as a live dashboard in their workspace — they clone the repo, no deployment by Sin at all.
⚠️ **Public Preview**, and **switching branches is destructive** (dashboards get new IDs/URLs). Also, **Git folders do not track publish/schedule config** — that must come from DAB or the Lakeview API. Pin a branch if you use it.

---

# 7. RUNBOOK — the 12 things that will bite you

| # | Trap | Symptom | Fix |
|---|---|---|---|
| 1 | 🚨 **Published with "Share data permissions"** (the default) | **Every team sees every row.** Silent. No error. | Republish with **Individual data permissions** (`embed_credentials: false`). Pin it in DAB. |
| 2 | 🚨 **Catalog is `ISOLATED`** / bound only to coredata | Widgets render **empty**, no error | `databricks workspace-bindings get-bindings catalog <cat>` → add departmental as `BINDING_TYPE_READ_ONLY` (or set `--isolation-mode OPEN`) |
| 3 | **`is_member()` used instead of `is_account_group_member()`** | 0 rows for everyone | Use `is_account_group_member()` |
| 4 | **Group is workspace-local** | `is_account_group_member()` → FALSE | Account admin creates/syncs **account** groups from Entra. ⚠️ `CREATE GROUP` in SQL makes workspace-local groups — never use it |
| 5 | **Forgot `GRANT EXECUTE` on the filter function** | query fails / returns nothing | `GRANT EXECUTE ON FUNCTION … TO <group>` |
| 6 | **Imported dashboard sat in the importer's user folder** | nobody else can see it | Move to `/Workspace/Shared/…` |
| 7 | **`warehouse_id` never changed after import** | breaks, or **IT gets billed** | Re-point the dataset at *their* warehouse |
| 8 | **`tag_team` is inside the `MAP`** | can't attach the row filter | Project it to a top-level column |
| 9 | **UDF parameter type ≠ column type** | 🚨 can **silently return ALL rows** | Match types exactly; `spark.sql.ansi.enabled = true` |
| 10 | **DBR < 12.2** (or dedicated access mode without serverless) | "fails securely" → **returns no data** — looks like a bug, not a permission error | DBR ≥ 12.2; dedicated mode needs 15.4 LTS + serverless |
| 11 | **Monthly PDF blasts the same file to everyone** | cross-team leak | **Test with 2 users / 2 teams.** If not per-viewer → one schedule per team, that team's list only. (Caps: attachments ≤9 MB · ≤100 subscribers · table visuals ≤100k rows) |
| 12 | ⚠️ **Entitlement change: auto 2026-07-27 / enforced 2026-09-14** | viewers silently lose access | Departmental admin grants **Consumer access** explicitly per group |

**Also:** a **materialized view / streaming table** built on the filtered table by a privileged owner **bakes in unfiltered rows** — never allow one without its own filter. **Row filters cannot be applied to a VIEW** (per-team views are an *alternative* to RLS, not a complement). Row-filtered tables **cannot** be read via Iceberg-REST / UC REST, have **no time travel**, and **cannot be cloned**.

---

# 8. Cost
| Item | Rate (Azure — confirm your region/tier) | Realistic |
|---|---|---|
| **Serverless SQL Warehouse, 2X-Small** (their workspace) | ~4 DBU/hr while active; SQL Serverless ≈ $0.70–0.95/DBU | **~$10–50/mo** for a cost dashboard with light traffic + 1 monthly refresh + 10-min auto-stop |
| **Paid by** | **the client's workspace** ⇒ real chargeback ✅ | |
| Row filter / ABAC | no DBU charge; small query-plan cost (*"the engine always makes the secure choice"*) | negligible on a cost table |
| Genie Agent (optional) | PAYG LLM DBUs since 2026-07-08; 150 free/mo ≈ $10.50 | $0 → tens of $ |

---

# 9. Lock-in (say it out loud so it's a decision, not an accident)
The **data** is portable (Delta on ADLS). The **serving layer is not**: `.lvdash.json` is proprietary, AI/BI dashboards don't render outside Databricks, row filters/ABAC are UC-only, Genie is entirely proprietary. **The deliberate exit path:** the same UC table + row filter consumed by **Power BI over their own warehouse** — governance stays in UC, only the viz layer moves.

---

# 10. PoC checklist (what to actually do next)
- [ ] Have a real team user run `SELECT current_user(), is_account_group_member('<their-group>')` in departmental → **true?**
- [ ] `databricks workspace-bindings get-bindings catalog <cat>` → `OPEN`, or add departmental `READ_ONLY`
- [ ] Project `tag_team` to a top-level column
- [ ] Create the row filter + GRANTs (incl. **`GRANT EXECUTE`**)
- [ ] Have that user run `SELECT count(*) FROM <gold>` → **only their rows?**
- [ ] Build the dashboard in coredata → **Export** `.lvdash.json`
- [ ] Departmental admin: **Import → Move to Shared → repoint warehouse → Publish (Individual) → Share (named groups) → Warehouse CAN USE**
- [ ] Test with **2 users from 2 teams**
- [ ] Test the **monthly schedule** with those same 2 users
- [ ] Confirm DBUs land on **their** warehouse
- [ ] (optional) show them **Genie One** (`/one`)

*All facts verified against Microsoft Learn / Azure Databricks docs, 2026-07-13. Generic templates — no AIA identifiers.*
