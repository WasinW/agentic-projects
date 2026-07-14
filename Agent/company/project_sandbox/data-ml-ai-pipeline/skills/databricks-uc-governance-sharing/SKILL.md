---
name: databricks-uc-governance-sharing
description: >-
  Unity Catalog governance + cross-workspace data-product sharing on Databricks (Azure).
  Use when asked about: UC identity model (Entra ID → account users vs workspace users), account
  groups vs workspace-local groups, row-level security / row filters / column masks,
  is_account_group_member(), GRANT EXECUTE on a filter function, workspace-catalog binding /
  isolation mode, "user sees empty dashboard widgets with no error", hive_metastore → UC migration,
  sharing a dashboard or table with a team whose workspace you do NOT control, AI/BI Dashboard
  publish modes ("Share data permissions" vs "Individual data permissions" / embed_credentials),
  dashboard subscriptions/PDF to external teams, Delta Sharing vs UC GRANT, Genie access,
  or verifying which metastore/catalog a workspace uses.
---

# Databricks Unity Catalog — Governance + Cross-Workspace Sharing

> Grounded in verified official docs (Microsoft Learn / Databricks), 2026-07-13.
> Field-tested against a real cross-workspace chargeback-dashboard problem
> (`knowledge_chat/aia-cost-dashboard-solution-VERIFIED_20260713.md`).
> Everything here is **generic / public-doc knowledge** — placeholders only, no client internals.

The one-line mental model:

> **Identity lives in the ACCOUNT. Data lives in the METASTORE. Compute lives in a WORKSPACE.**
> Most "why can't they see it?" bugs are someone confusing those three tiers.

---

## 1. Identity model — three tiers, do not blur them

```
Entra ID (Azure AD)
   │  SCIM sync  OR  Automatic identity management (GA; default for accounts created after 2025-08-01)
   ▼
Databricks ACCOUNT            ← account users + ACCOUNT GROUPS  (the governance tier)
   │  assign + entitlement
   ▼
WORKSPACE                     ← workspace users (members, with entitlements)
```

| Term | What it is | Can they… |
|---|---|---|
| **Account user** | An Entra principal registered in the Databricks *account*. Not assigned to your workspace. | Open a **published dashboard URL**. Be a member of an **account group** that a GRANT resolves. **Cannot** open your workspace UI, notebooks, Genie. |
| **Workspace user** | An account user *additionally assigned* to a workspace + given an entitlement. | Everything the entitlement allows inside *that* workspace. |
| **Consumer access** | The lightweight "view published dashboards" surface. | View-only render: no sidebar, no nav, no drafts, no other objects. |

**Account groups are ACCOUNT-tier.** A `GRANT ... TO \`grp\`` issued from **workspace A** resolves that
same group when the principal queries from **workspace B** — because the grant is stored in the
**metastore**, and the group is stored in the **account**. This is the whole trick behind cross-workspace sharing.

- **Workspace-local groups are legacy — avoid them.** They do not resolve for account users, and
  they do not travel across workspaces. Create groups in the **account console**, then assign to
  workspaces if (and only if) workspace membership is actually needed.
- **Automatic identity management (GA):** sharing to an Entra group **auto-adds those users to the
  ACCOUNT on first login** — *not to the workspace*. Exactly the mechanism you want for consumers.
- **Entitlement-model change:** rolling out 2026-06-15 → **auto-enabled 2026-07-27 → enforced
  2026-09-14**. Coordinate with the workspace admins who own the consumers' workspaces.

---

## 2. Access = TWO orthogonal dimensions. You need BOTH.

This is the single most common modelling error: people think access is one three-level ladder
(catalog → schema → table). It is not. It is **two independent axes**, and passing one does not help you with the other.

| Axis | Question it answers | Mechanism |
|---|---|---|
| **A. Object privileges** | *Can you touch the object at all?* | `USE CATALOG`, `USE SCHEMA`, `SELECT`, **`EXECUTE` on the row-filter function** |
| **B. Data filtering** | *Which rows/columns do you get back?* | **Row filter** (UDF bound to the table), **column mask** |

```sql
-- Axis A — all four. USE CATALOG/USE SCHEMA are not inherited from SELECT.
GRANT USE CATALOG ON CATALOG  <catalog>                          TO `client-<team>`;
GRANT USE SCHEMA  ON SCHEMA   <catalog>.<schema>                 TO `client-<team>`;
GRANT SELECT      ON TABLE    <catalog>.<schema>.<table>         TO `client-<team>`;
GRANT EXECUTE     ON FUNCTION <catalog>.<schema>.<filter_fn>     TO `client-<team>`;  -- <<< THE MOST FORGOTTEN ONE
```

> **Symptom of the missing `GRANT EXECUTE`:** the user has `SELECT`, the row filter exists, and the
> query **fails or returns nothing** — because they cannot execute the filter UDF that guards the table.
> Add the function grant to the same script that adds the table grant. Always. Same commit.

---

## 3. Row-Level Security (row filters) + column masks

### 3.1 The function + the binding

```sql
-- The filter function returns a BOOLEAN: TRUE = this row is visible to the caller.
CREATE OR REPLACE FUNCTION <catalog>.<schema>.team_row_filter(team_tag STRING)
RETURN is_account_group_member('<platform-team>')                        -- platform/FinOps bypass
    OR is_account_group_member(concat('client-', lower(team_tag)));      -- naming-convention variant

ALTER TABLE <catalog>.<schema>.<table>
  SET ROW FILTER <catalog>.<schema>.team_row_filter ON (<filter_col>);   -- bind to the column(s) passed in
```

### 3.2 `is_account_group_member()` — NOT `is_member()`

| Function | Resolves against | Behaviour for an account user (not a workspace member) |
|---|---|---|
| `is_member('g')` | **workspace-local** group | **Silently returns FALSE** — no error. Your entire consumer audience sees zero rows (or, in a shared-credential dashboard, the wrong rows). |
| **`is_account_group_member('g')`** | **account** group | Correct. **Use this.** |

`is_member()` failing *silently* is what makes this a multi-hour debug. If RLS "works for me but
returns nothing for them", check this line first.

### 3.3 Three ways to drive the filter

| Approach | How | Verdict |
|---|---|---|
| **Naming convention** | `concat('client-', lower(team_tag))` — group name derived from the data value | Fine for a PoC. Brittle: couples source-system tag hygiene (typos, renames, casing) to Entra group names. |
| **Mapping table** ⭐ | Filter function joins a `team_tag → account_group` mapping table | **Recommended.** Decouples tag hygiene from identity. Onboarding a team = **INSERT a row**, no DDL, no redeploy. Auditable. |
| **ABAC row-filter policies** | Attribute-based policies at catalog/schema level (GA 2025) | Best at scale — one policy governs many tables instead of one binding per table. Adopt when the table count grows past what you want to hand-bind. |

```sql
-- Mapping-table-driven (recommended)
CREATE TABLE <catalog>.<schema>.team_access_map (team_tag STRING, account_group STRING);

CREATE OR REPLACE FUNCTION <catalog>.<schema>.team_row_filter(team_tag STRING)
RETURN is_account_group_member('<platform-team>')
    OR EXISTS (
         SELECT 1 FROM <catalog>.<schema>.team_access_map m
         WHERE m.team_tag = team_tag
           AND is_account_group_member(m.account_group)
       );
```

### 3.4 Column masks

```sql
CREATE OR REPLACE FUNCTION <catalog>.<schema>.mask_pii(v STRING)
RETURN CASE WHEN is_account_group_member('<pii-readers>') THEN v ELSE '***' END;

ALTER TABLE <catalog>.<schema>.<table>
  ALTER COLUMN <col> SET MASK <catalog>.<schema>.mask_pii;
```

Same `GRANT EXECUTE` requirement applies to mask functions.

### 3.5 Prereqs (both are hard gates)
1. Table is in a **UC catalog** — `hive_metastore` cannot do this at all (§5).
2. The catalog is **not workspace-bound** for the consumers (§4).

---

## 4. Workspace-catalog binding — the silent killer

A catalog has an **isolation mode**:

| Isolation mode | Meaning |
|---|---|
| `OPEN` | Any workspace in the metastore can access it (subject to privileges). |
| `ISOLATED` (workspace-bound) | Only the explicitly bound workspaces can access it. |

> **The trap:** *"Dashboard widgets that query workspace-bound securables **do not display data for
> account users**."* — no error, no permission-denied, just **empty widgets**. And the
> **auto-created default workspace catalog is ISOLATED (bound) by default**, which is exactly the
> catalog a fresh DEV workspace hands you.

**Check it:**
```bash
databricks workspace-bindings get-bindings catalog <catalog>
# UI: Catalog Explorer → <catalog> → "Workspaces" tab
```
**Fix it:**
```bash
databricks catalogs update <catalog> --isolation-mode OPEN
# or keep ISOLATED and explicitly bind the consumer workspaces:
databricks workspace-bindings update-bindings catalog <catalog> --json '{"add":[{"workspace_id":<id>,"binding_type":"BINDING_TYPE_READ_ONLY"}]}'
```

If you see "user is in the group, GRANTs are correct, RLS looks right, and they still see nothing" —
**check the isolation mode before anything else.**

---

## 5. `hive_metastore` cannot do this

| Capability | `hive_metastore` | Unity Catalog |
|---|---|---|
| Row filters / column masks | ❌ | ✅ |
| `is_account_group_member()` | ❌ (function does not exist) | ✅ |
| Cross-workspace grants | ❌ (metastore is workspace-local) | ✅ |
| Lineage / `system.access.audit` | ❌ | ✅ |

`DESCRIBE CATALOG hive_metastore` returns essentially only name/comment/owner — a useful quick tell.
Migration paths, cheapest first:

| Path | When |
|---|---|
| **CTAS into UC** ⭐ | History not needed. Simplest, and lets you fix the schema on the way in. |
| **Deep clone** | You need the Delta history / time travel preserved. |
| **External table** | Files must stay where they are (points UC at the existing location). |
| **UCX (Databricks Labs)** | Bulk migration of many tables/assets; generates the assessment + migration plan. |

**MAP-typed columns:** they survive UC fine, but a row filter/mask cannot be bound *inside* a MAP.
If you need RLS on something that lives in a map (e.g. Azure resource **tags** kept as
`MAP<STRING,STRING>`), **promote it to a top-level column** in gold (`tag_team STRING`) and bind the
filter to that. Keep the MAP for the long tail; project the governed keys out.

---

## 6. Sharing a data product with workspaces you do NOT control — decision tree

The framing question: **what actually shows up on the consumer's screen?**

> **The only artifact that ever appears inside a consumer's own workspace is a shared TABLE**
> (in *their* Catalog Explorer). A dashboard is a **URL**. An App is a **URL**. Neither ever
> materialises in their workspace UI.

```
Do they need to see it inside THEIR OWN workspace / their own BI tool?
├── YES → (b) UC table GRANT to their account group  [+ hand them a .lvdash.json to import]
│         → THEIR warehouse runs the query → THEY pay → real chargeback
└── NO, a link is fine
    ├── One curated view, per-viewer RLS  → (a) Published AI/BI Dashboard + share to account group  ⭐ default
    ├── Zero doc-ambiguity / need per-team PDF → per-team dashboards, one per group
    ├── Different METASTORE or a different ORG → (d) Delta Sharing
    └── "Share" actually means "a report in my inbox" → (e) scheduled per-team report job
```

| # | Option | Appears in their WS? | Who pays compute | RLS | Verdict |
|---|---|---|---|---|---|
| **a** | **Published AI/BI Dashboard + account-group share** | No (URL only) | **Publisher** | Per-viewer *if* published with Individual data permissions (§7) | ⭐ Default. Viewer needs **NO warehouse permission** and **NO workspace membership**. |
| **b** | **UC table GRANT** to their account group | **Yes — Catalog Explorer** | **Consumer's own warehouse** | Yes (UC, everywhere) | ⭐ Companion to (a). The only real **chargeback** answer. Free to you. |
| **c** | Export/import `.lvdash.json` | Yes (as *their* dashboard) | Consumer | Yes (via UC on the table) | Template hand-off. Pairs with (b). They own the copy → drift is on them. |
| **d** | **Delta Sharing** | Yes (as a share) | Consumer | Coarser (share-level) | **Only** for a **different metastore** or an **external org**. Same metastore → unnecessary complexity. |
| **e** | Scheduled per-team report (PDF/Excel job) | No (email) | You (a tiny job) | By construction (query filtered per team) | Cheapest backstop when "share" means "report". |
| — | **Genie** | — | — | — | **BLOCKED.** *"can only be granted to workspace users."* Account users cannot use it. Do not propose it. |

**The compute-affinity trap (name it out loud early):** with option (a), queries run on the
**publisher's** warehouse. **The team hosting the dashboard pays for every viewer's query.**
For a *cost/chargeback* dashboard that is deliciously ironic — and it is exactly why (b) exists.
Ship (a) **and** (b): the link for the casual viewer, the table grant for the team that wants to
build their own thing and pay their own DBUs.

---

## 7. AI/BI Dashboard publish modes — the #1 field failure

When you publish a dashboard you choose a credential mode. **The default is the dangerous one.**

| UI label | API | Query runs as | RLS outcome |
|---|---|---|---|
| **"Share data permissions"** (**DEFAULT**) | `embed_credentials: true` | The **publisher** | ❌ **Row filters are evaluated as the publisher → every viewer sees the publisher's full result set.** |
| **"Individual data permissions"** | `embed_credentials: false` | The **viewer** | ✅ Per-viewer UC RLS / masks. **Workspace membership is not required.** |

Two facts that surprise everyone, both true, and they are *not* contradictory:

> **data identity = the VIEWER · compute identity = the PUBLISHER.**
> The viewer's Entra identity is what UC evaluates; the publisher's credentials are what get the
> warehouse to run. So the viewer needs **no CAN USE on the warehouse** and **no workspace entitlement**.

**Encode the mode in the bundle. Never trust the UI default.**
```yaml
# databricks.yml (DAB)
resources:
  dashboards:
    cost_dashboard:
      display_name: <name>
      file_path: ./dashboards/<name>.lvdash.json
      warehouse_id: ${var.warehouse_id}
      embed_credentials: false      # <<< "Individual data permissions". The UI default (true) leaks every row.
```

If anyone in your org says *"we tried AI/BI and RLS didn't work / it's not secure"* — they almost
certainly published on the default. That is a **config bug, not a product flaw**. Ask them
*which publish mode*; the answer is the whole conversation.

> ⚠️ **One doc contradiction to test, not to assume:** two official pages say Individual mode
> preserves per-viewer RLS for account-member access; the AI/BI **admin capability table** shows RLS
> as unsupported for account-member access. **Empirically test in your own tenant** with one real
> consumer identity before you commit an architecture to it. If it fails → fall back to
> **one dashboard per team, published with Share data permissions, on a dataset pre-filtered to that
> team** (zero ambiguity, and the only clean way to email per-team PDFs).

---

## 8. Subscriptions / scheduled PDF — the account-user gotcha

> *"Account users can only be added as subscribers **as a notification destination**. There is
> **no Subscribe button** for account users."*

A **notification destination is a static email target, not an identity**. Therefore:

- **NEVER email an all-teams PDF to account users.** The render is **not** per-recipient
  RLS-filtered — you would blast every team's rows to every team. This is a data-leak class bug.
- Safe patterns: **link-only** notifications ("your dashboard was refreshed → <url>"), or
  **one dashboard per team** and one destination per team (filtering by construction).
- Caps to design around: attachments **≤ 9 MB** · **≤ 100 subscribers** · table visuals **≤ 100k rows** ·
  any cron schedule · PDF + CSV/Excel.

---

## 9. Verification cheat-sheet (run these BEFORE you design)

```sql
-- Which metastore am I in?  (NOTE: fails on a SQL warehouse — run in a NOTEBOOK)
SELECT current_metastore();
```
```python
spark.sql("SELECT current_metastore()").show()          # notebook, all-purpose/serverless cluster
from databricks.sdk import WorkspaceClient
print(WorkspaceClient().metastores.current().metastore_id)
```
```bash
databricks metastores current                            # CLI
databricks workspace-bindings get-bindings catalog <cat> # isolation / bound workspaces
databricks catalogs update <cat> --isolation-mode OPEN   # unbind
databricks lakeview dashboards ...                       # CLI/API still says "lakeview" (= AI/BI Dashboard)
```
```sql
SHOW CATALOGS;                                -- see `system` + `samples` ⇒ UC is on. Only hive_metastore ⇒ no UC.
DESCRIBE CATALOG <cat>;                       -- Catalog Type: Regular | Delta Sharing | Foreign | System
SHOW GROUPS;                                  -- what resolves here
SELECT is_account_group_member('<group>');    -- ⭐ the definitive "will my filter fire?" test
SELECT current_user();
```

**Same-metastore check across two workspaces = the fork in the road:** same metastore ⇒ account
groups + GRANTs just work, Delta Sharing is unnecessary. Different metastore ⇒ Delta Sharing is the
*only* option. Verify it, don't assume it. (Different workspace IDs and different catalogs are
normal and fine — it is the **metastore** that matters.)

---

## 10. Gotchas (the list that saves the day)

1. **`is_member()` silently returns FALSE for account users** → use **`is_account_group_member()`**.
2. **Missing `GRANT EXECUTE` on the row-filter / mask function** → SELECT alone is not enough.
3. **Workspace-bound catalog ⇒ EMPTY widgets, no error.** Default workspace catalogs are bound by default.
4. **The default publish mode leaks everything** (`embed_credentials: true`). Pin `false` in DAB.
5. **Never email an all-teams PDF to account users** — notification destinations are not identities.
6. **Genie is workspace-users-only** — structurally dead for external consumers.
7. **`hive_metastore` = no RLS, no account-group functions.** Migrate first, design second.
8. **Workspace-local groups are legacy** and do not resolve across workspaces.
9. **Publisher pays the DBUs** for every viewer's query (see `databricks-cost-optimization`).
10. **IP access lists apply to account users too** — *"regardless of whether they are assigned to a
    workspace"*. Your consumers must be on an approved network / VPN.
11. **Front-end PrivateLink** can block users on the public endpoint (documented risk for Apps).
12. **Entitlement-model change: auto 2026-07-27, enforced 2026-09-14** — put it on the calendar.
13. **Lock-in honesty:** the gold table is portable Delta and the row filter is a rewritable SQL UDF,
    but the **published-dashboard + account-user sharing model is Databricks-proprietary**. If that
    matters, the low-lock-in path is: UC GRANT + the consumer's own BI tool (Power BI) on UC.

---

## Test plan / validation

1. **Pre-flight**: same metastore? · `SHOW CATALOGS` (UC, not hive)? · isolation mode `OPEN`? ·
   groups are **account-level**? · SSO enforced (not OTP fallback)? · IP lists / PrivateLink?
2. **Grant test**: as the platform group, `SELECT is_account_group_member('<client-group>')` → FALSE;
   as a consumer identity → TRUE.
3. ⭐ **The decisive test**: one real consumer identity that is **NOT** a member of your workspace,
   in a client account group → publish with **Individual data permissions** → share → they open the
   link. Assert: (a) it loads, (b) **only their rows**, (c) no sidebar / no workspace surface.
   *This single test decides the architecture.* If it fails → per-team dashboards.
4. **Negative test**: a user in **no** client group → zero rows (not an error, and not everything).
5. **Regression**: add a team via the **mapping table only** (INSERT, no DDL) → new group sees rows,
   existing groups unchanged.
6. **Audit**: confirm the viewer's queries land in `system.access.audit` under **their** identity.

## See also
- `databricks-cost-optimization` → §"who pays" trap, Apps 24/7 billing, warehouse auto-stop.
- `de-solution-architecture` → the reusable "share a data product across workspaces" pattern.
- `knowledge_chat/aia-cost-dashboard-solution-VERIFIED_20260713.md` → the fully-cited source.
- Escalate: catalog/metastore topology → `data-architect`; PII/regulatory sign-off → `governance-consultant`.
