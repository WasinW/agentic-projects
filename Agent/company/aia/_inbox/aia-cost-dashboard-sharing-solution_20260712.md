# AIA Cost-Dashboard Sharing Solution + Session Notes (2026-07-12) — ⚠️ SUPERSEDED

> **⚠️ SUPERSEDED by `aia-cost-dashboard-solution-VERIFIED_20260713.md`.** This doc's §4 (“Two realizations”) and §5 Step 2 are WRONG: (a) publish-mode names are **“Share data permissions” (default, dangerous)** vs **“Individual data permissions”** — not “embed/don’t embed”; (b) the row filter must use **`is_account_group_member()`**, not `is_member()`; (c) it MISSES the hard blocker — a **workspace-bound catalog** makes account users see **empty widgets**; (d) it wrongly implied compute/warehouse access forces workspace membership — in fact **“compute access is always granted by the publisher’s credentials”**, so viewers need no warehouse permission. Read the VERIFIED doc instead. Kept for history only.

> **For:** สิน (วศิน) — Senior DE @ AIA. Portable export (paste into web chat / read on mobile). Covers: (1) AIA data-platform architecture recap, (2) the cost-dashboard task, (3) the **shared-dashboard solution** (UC RLS + AI/BI Dashboard publish), (4) **step-by-step how-to**, (5) what to verify before presenting to พี่ Sarunya.
> **Policy:** air-gapped AIA machine — screenshots only, no code export FROM AIA; the SQL below is generic template สิน adapts. Keep AIA-actual separate from generic surveys.

---

## 1. AIA Data Platform architecture (confirmed, org diagram 2026-07-12)
```
SOURCES (RDBMS + files + external)
  ├─ Qlik (CDC) ────────┐        ← CDC = Qlik Replicate + Debezium (two tools)
  ├─ Debezium ──► Kafka  │  EVENT PROCESSING: AKS Strimzi Kafka + Connect + Grafana + Jenkins + ACR  ← Sin (producer)
  └─ Edge Node SFTP/AutoSys + ADF Link Service (files)
        │  orchestrate: ADF + Integration Runtime
        ▼
  COMPUTATION: Azure Databricks — Real-time cluster + Batch cluster       ← Sin's NEW focus
        driven by Azure SQL MI "Framework DB" (prd_frmwrk_db) = config-driven (SCB-RDT-like)
        │  ABFSS
        ▼
  DATALAKE (ADLS Gen2): RAW → Persist → Staging (staging/adam/data mart/HSM)
        ▼
  DATABASE: ODS (Azure SQL MI, app+regulator users) + Synapse Dedicated SQL pool
        (EDW, New QS, Departmental DM=Data Mart, UC=<user/team, NOT Unity Catalog>, DGO=Data Governance Office)
        ▼
  SERVING: ESB/API → apps · PowerBI · SSMS   |   GOVERNANCE: Purview + Data 360
  ANALYTIC: Databricks DS Lab + Departmental/Common/Amplify WS (client users, mlflow)
```
Key: **Departmental WS = workspaces where CLIENT users log in** (different from the DP internal WS). Some WS have **Unity Catalog** enabled. DR design exists.

## 2. Cost-Dashboard task
- **Goal:** Databricks dashboard for Azure cost per service/RG, tags per team → chargeback.
- **Team:** พี่ Sarunya (senior/SA guidance) · บูม (owns existing cost pipeline, REMOVES tags) · Sin (helps, **retains tags** = differentiator).
- **Ingest (settled):** Azure **Cost Management Export → ADLS (Parquet) → Databricks** (avoids the auth wall: device-code blocked by conditional access AADSTS530033; Export runs on Azure's own identity). Types: ActualCost / AmortizedCost / PriceSheet / FOCUS.
- **Pipeline (5-layer):** bronze(raw) → persist(typed + **tags as `MAP<STRING,STRING>`**) → prep → summary(FULL OUTER JOIN actual+amortized + LEFT JOIN pricesheet on meter_id) → gold(views incl. `cost_wide` tags→cols, `chargeback`). Dev = temp views/`WITH`; prod = `INSERT OVERWRITE PARTITION(usage_date)`.
- **Dashboard:** Databricks **AI/BI Dashboard** (Lakeview), NOT Power BI. Deploy via DAB + Jenkins.

## 3. Sarunya's requirements (the sharing problem)
1. AIA policy: no data cross-env EXCEPT cost from Portal. 2. Cost from Portal covers all env. 3. Dashboard shows all-env cost (even though pipeline runs in DEV). 4. Tag per team → chargeback. 5. Dashboard lives on **IT workspace** (Sin's team). 6. **Client teams have NO access to the IT workspace.** 7. Find a **way to share**. 8. **Notify users monthly.** + Sarunya thinks Databricks has "some feature" for shared dashboard (= AI/BI Dashboard sharing — it exists).

---

## 4. THE SOLUTION (recommended architecture)
**One gold table with Unity Catalog Row-Level Security → one AI/BI Dashboard → publish + share to each client's account-group; each client sees only their own rows; no IT-workspace access needed.**

```
[Data Platform WS — IT/internal]
  cost pipeline → gold.cost_wide
        │  ① UC ROW FILTER (per team) applied ONCE on the table (central, not re-done per WS)
        ▼
  AI/BI Dashboard "Cost Overview" (built on gold.cost_wide, runs on a SQL Warehouse)
        │  ② PUBLISH — "do NOT embed credentials"  →  RLS applies per viewer
        │  ③ SHARE (CAN VIEW) to client account-groups
        ▼
[Client @ departmental WS] opens dashboard link → runs as THEIR identity → RLS → sees only own rows
        ✓ viewing a shared dashboard ≠ accessing the IT workspace (satisfies req #6)
```

**Two realizations (depends on metastore topology):**
| | when | compute paid by |
|---|---|---|
| **A. Publish AI/BI dashboard (no embedded creds) + UC RLS** | DP WS & departmental WS share the **same UC metastore** | the dashboard's SQL Warehouse (IT, or route to departmental) |
| **B. UC cross-workspace table GRANT** — client queries `gold.cost_wide` from their own WS (RLS applies), builds/views own dashboard | same metastore, client is technical | client's departmental warehouse |
| **Delta Sharing** | **different** metastore/account | client's compute |

**Critical facts:**
- **RLS lives ONCE on the table** (UC row filter). Define it in DP; enforced everywhere the table is queried. Do NOT re-implement per departmental WS.
- **Publish "do NOT embed credentials"** — else all viewers see the same data (no per-client filtering).
- **The whole thing hinges on: is departmental WS under the SAME UC metastore as DP?** → verify first (Step 0).

---

## 5. STEP-BY-STEP HOW-TO

### Step 0 — Verify prerequisites (do this FIRST; it decides A vs Delta Sharing)
1. **Same metastore?** Run in BOTH the DP-batch WS and a departmental WS, compare the returned ID:
   ```sql
   SELECT current_metastore();
   ```
   - same ID → path A/B. different → Delta Sharing.
   - alt: **Account console (`accounts.azuredatabricks.net`) → Data → Metastores** → see which workspaces are assigned; or in departmental WS `SHOW CATALOGS` → if you see DP's `gold`/`cost_platform` catalog, it's shared.
2. **UC enabled** on both workspaces (Catalog Explorer shows a metastore).
3. **Client account-groups exist** (e.g. `client-underwriting`, `client-claims`) — from the departmental WS user groups. If not, ask admin to create/confirm.
4. **Pick the SQL Warehouse** the published dashboard runs on + decide **who pays** (IT serverless warehouse = simplest; or departmental = chargeback).
5. **Verify the nuance:** confirm that a user with CAN VIEW on a published dashboard can view it **without** being a member of the IT workspace (dashboard ACL ≠ workspace membership). ← ask a Databricks admin or test with one client identity before presenting.

### Step 1 — Gold table + Row-Level Security (in DP, Unity Catalog)
```sql
-- 1a. row-filter function: IT sees all; each client sees only their team's rows
CREATE OR REPLACE FUNCTION cost_platform.gold.cost_row_filter(team_tag STRING)
RETURN
    is_account_group_member('cost-admins')                    -- IT/FinOps see everything
    OR is_account_group_member(concat('client-', lower(team_tag)));  -- client sees own team

-- 1b. apply it to the gold table on the team column
ALTER TABLE cost_platform.gold.cost_wide
    SET ROW FILTER cost_platform.gold.cost_row_filter ON (tag_team);
--   (optional column mask for sensitive cols: ALTER TABLE ... ALTER COLUMN x SET MASK ...)

-- 1c. grant each client group read access (RLS auto-limits their rows)
GRANT USE CATALOG ON CATALOG cost_platform            TO `client-underwriting`;
GRANT USE SCHEMA  ON SCHEMA  cost_platform.gold        TO `client-underwriting`;
GRANT SELECT      ON TABLE   cost_platform.gold.cost_wide TO `client-underwriting`;
-- repeat GRANT per client group
```
> If team→group mapping is complex, drive `cost_row_filter` from a small mapping table instead of a name convention.

### Step 2 — Build + publish the AI/BI Dashboard (in DP)
1. **Create** an AI/BI Dashboard on `cost_platform.gold.cost_wide`, attached to the chosen SQL Warehouse. Build the pages (KPI tiles → trend → breakdowns → chargeback).
2. **Publish** → in the publish dialog choose **"Don't embed credentials"** (so each viewer's identity drives UC RLS).
3. **Share** → add each **client account-group** with **CAN VIEW**.

### Step 3 — Deliver + monthly notify
- **Databricks Job** (schedule: 1st of month) → task that emails/Teams the **dashboard link** (+ optional per-team PDF/Excel snapshot) to team leads. (Teams webhook / SMTP / SharePoint.)
- Chargeback: expose `gold_chargeback` (per cost_center/owner/month) on a dashboard page and/or hand to Finance.

### Alt Step (different metastore) — Delta Sharing
```sql
CREATE SHARE cost_share;
ALTER SHARE cost_share ADD TABLE cost_platform.gold.cost_wide;   -- RLS on the object still applies
CREATE RECIPIENT departmental_recipient;
GRANT SELECT ON SHARE cost_share TO RECIPIENT departmental_recipient;
```
Client mounts the share in their metastore and builds/views their dashboard; each recipient limited by the filter.

---

## 6. What to verify before presenting to Sarunya
1. **Metastore same?** (Step 0.1) — the make-or-break.
2. **View-shared-dashboard ≠ IT-workspace access?** (Step 0.5) — the requirement-#6 crux.
3. **Publish without embedded creds + cross-workspace RLS** behaves as described (test with one client identity).
4. **Compute/who-pays** decision (IT warehouse vs departmental) — ties to chargeback.
5. **"Dashboard/share" meaning to Sarunya:** live interactive (this solution) vs monthly static report (fallback Option C). If she wants report-only → Databricks Job → per-team PDF/Excel → email (no sharing infra). Prepare both as proposals.

## 7. Open questions (from Sarunya / to clarify)
- Dashboard: all-env vs prod-only? IT workspace identity? chargeback flow (Sin→Finance vs self-service)?
- Departmental Synapse schemas: EDW / New QS (Sin to explain later) · **DM = Data Mart** (confirmed) · **UC = a user/team label, NOT Unity Catalog** (Sin forgets exact) · **DGO = Data Governance Office**.
- Which departmental WS have UC enabled + share the DP metastore?

## 8. Today's decisions / state
- Confirmed full AIA architecture; Sin's scope = **producer (Kafka) + ADB compute (new) + cost-dashboard PoC**.
- Sharing solution = **UC RLS on one gold table + AI/BI Dashboard publish (no embedded creds) + share to client groups**, gated on **same-metastore** verification.
- Next: verify Step 0 (metastore + nuance) → build proposal for Sarunya (this doc is the draft).

*Generic Databricks/UC templates — not AIA code. Verify against AIA's actual metastore/permissions before applying.*
