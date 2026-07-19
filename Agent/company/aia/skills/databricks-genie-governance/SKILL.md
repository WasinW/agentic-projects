---
name: databricks-genie-governance
description: >-
  Genie AI on Azure Databricks + governing business-user access, budget, and cost.
  Use when asked about: Genie One / Genie Agent / Genie Code (what they are, sharing, GA state),
  letting business users use ONLY Genie/AI-BI with no ability to create jobs/clusters/notebooks,
  Consumer access entitlement, the entitlement-additivity trap + the users-group entitlement
  migration, "user should reach only Genie One", Genie is not a security boundary (UC is),
  Databricks Budgets (what can BLOCK vs only ALERT), serverless budget/usage policies, Genie
  pay-as-you-go LLM DBUs + the 150 free-tier, monitoring Genie cost from system.billing.usage,
  why system.billing does not match the Azure Portal, or capping per-team Databricks spend.
---

# Databricks — Genie AI + Business-User Governance (access · budget · cost)

> Grounded in verified official docs (Microsoft Learn / Databricks), 2026-07-18.
> Field-context: AIA departmental workspace — business users consume shared dashboards + Genie,
> must be locked to Genie-only, isolated per team, and capped per team.
> Generic / public-doc knowledge — placeholders only, no client internals.
> Companion: `databricks-uc-governance-sharing` (RLS / sharing) · `databricks-cost-optimization`.

The one-line mental model:

> **Three INDEPENDENT gates, three different mechanisms.**
> **Entitlement** = which *surface* (Genie-only, no jobs) · **UC grant** = which *data* (row-level) · **Budget** = how much *spend*.
> Confusing them is why "lock business users to Genie" feels hard. Solve each gate separately.

---

## 0. Terminology (the 2026 renames — old names are dead)

| Old | Current | Note |
|---|---|---|
| Genie Space | **Genie Agent** | curated NL-to-SQL agent over ≤ selected UC tables |
| Databricks One | **Genie One** | the account-level entry surface a consumer lands in |
| — | **Genie Code** | the third Genie surface |

All three surfaces (**Genie One / Genie Agent / Genie Code**) report to billing as **one product**
`billing_origin_product = 'GENIE'` and share **one** resource tag `databricks-product: genie`.
Distinguish them via `usage_metadata.genie.surface`, not by separate products.

---

## GATE 1 — Entitlement: "Genie/AI-BI only, no jobs"

### 1.1 There are exactly three access entitlements

From [Manage entitlements](https://learn.microsoft.com/en-us/azure/databricks/security/auth/entitlements):

| Capability | **Consumer access**<br>`workspace-consume` | Databricks SQL access<br>`databricks-sql-access` | Workspace access<br>`workspace-access` |
|---|:--:|:--:|:--:|
| Read/run shared dashboards, Genie Agents, Apps | ✓ | ✓ | ✓ |
| Query SQL warehouses via BI tools | ✓ | ✓ | |
| Author dashboards / Genie / SQL editor | | ✓ | |
| **Notebooks, JOBS, pipelines, models** | | | ✓ |

Plus two compute entitlements (`allow-cluster-create`, `allow-instance-pool-create`) — not granted to non-admins by default.

> **Job authoring lives behind `workspace-access`.** Withhold it → there is no Jobs surface at all.

### 1.2 Consumer access is the answer — what it does / does not allow

[What is consumer access?](https://learn.microsoft.com/en-us/azure/databricks/ai-bi/consumers/):
> *"…gives users access to workspace-level **Genie One**. When users with consumer access sign in, they are directed to Genie One instead of the standard workspace… **Users with only consumer access cannot create new objects in the workspace.**"*

| ✅ CAN | ❌ CANNOT |
|---|---|
| use Genie One; ask questions | create **job / cluster / notebook / pipeline** |
| open dashboards/Genie/Apps shared to them | create/edit dashboards or Genie Agents |
| be granted **CAN USE** on a warehouse → use Power BI/Tableau | open SQL editor / run ad-hoc SQL |
| **RLS/CLS is enforced on their views** | view warehouses or Query History |

→ Answer to *"can a Consumer-access user create a job?"* = **No (doc-confirmed).** "Reaches only Genie One" is exactly the intended state.

### 1.3 🪤 THE TRAP — additivity + the users-group migration

> Entitlements are **additive**. Consumer access locks down **only if it is the user's SOLE entitlement.**

**Before the migration, the `users` system group grants Workspace access + SQL access by DEFAULT** → a
consumer **inherits authoring rights** and the lockdown **silently breaks** (they can create jobs).
The consumer doc says it: *"Until your workspace migrates… users with consumer access also inherit all entitlements granted to the `users` system group."*

**Migration timeline** ([Migrate workspace entitlement control](https://learn.microsoft.com/en-us/azure/databricks/security/auth/system-group-entitlements-migration)):
`2026-06-15 opt-in` → **`2026-07-27 auto-enable`** → **`2026-09-14 enforced`** (no opt-out).
After: `users` group has **no** entitlements; you pick entitlements per principal; old entitlements move to a `users-clone-<TS>` workspace-local group.

> **For a strict shop: migrate the workspace NOW (opt-in).** Otherwise Consumer access is not actually restrictive.
> Pre-work: repoint SCIM/Terraform to **account groups** (post-migration, writing system-group entitlements fails); preserve the clone group in SCIM (or members lose access); after migrating, **audit the clone group** and ensure `biz-consumers-*` is NOT a member of it.

### 1.4 Configure it — per team

```
0. PREREQUISITE: migrate the workspace entitlement behaviour (§1.3) — else Consumer access leaks.
1. account group  biz-consumers-<team>   (Entra → SCIM; must be an ACCOUNT group, not workspace-local)
2. grant Consumer access (workspace-consume) ONLY. Nothing else. (additivity!)
3. serverless SQL warehouse (admin-owned) → grant the group CAN USE (NOT CAN MANAGE) — Genie needs compute
4. UC: GRANT SELECT on just the team's gold view + EXECUTE on the row-filter fn  (GATE 2)
5. hardening: disable dashboard email subscriptions; disable SQL results download
6. budget (GATE 3)
```
```hcl
resource "databricks_entitlements" "biz_consumers_team" {
  group_id          = databricks_group.biz_consumers_team.id
  workspace_consume = true   # every other entitlement stays false (default)
}
```

### 1.5 Close the job-creation back-doors
- **primary:** no `workspace-access` → no DS&E objects; no `allow-cluster-create`.
- **dashboard schedule/subscription** (job-like): Settings → Notifications → disable **Enable dashboard email subscriptions**.
- **API/Terraform:** entitlements enforce server-side → Jobs API rejects the same as the UI. Ensure no elevated PAT / no SP shares the group.
- **Genie:** cannot create jobs; only lever is querying data, bounded by GATE 2.

---

## GATE 2 — UC grant: "see only your team's rows" (and Genie is NOT the fence)

> **Genie is not a security boundary — Unity Catalog is.**
> [Create and manage a Genie Agent](https://learn.microsoft.com/en-us/azure/databricks/genie/set-up): access is controlled by UC, and users *"can query other tables by prompting for joins or editing SQL directly."*

⇒ A consumer can prompt Genie to reach **any table they hold `SELECT` on** — the Genie Agent's
attached-table list is **not** a fence. So scope UC grants tightly:

```sql
GRANT USE CATALOG  ON CATALOG  <cat>                    TO `biz-consumers-<team>`;
GRANT USE SCHEMA   ON SCHEMA   <cat>.gold               TO `biz-consumers-<team>`;
GRANT SELECT       ON TABLE    <cat>.gold.cost_by_team  TO `biz-consumers-<team>`;
GRANT EXECUTE      ON FUNCTION <cat>.gold.fn_team_rls   TO `biz-consumers-<team>`;  -- row filter fn
-- row filter uses is_account_group_member('client-<team>')  — see databricks-uc-governance-sharing
```

**These users need Consumer access regardless** — Genie One and *seeing shared Genie Agents / Apps* require
it (a bare account user cannot see Genie Agents — **confirmed**). On **RLS specifically**: it is evaluated
against the viewer's identity via `is_account_group_member()` in Individual-data-permissions mode; whether
a *bare account user* (no entitlement) also gets RLS enforced is **contested across Databricks docs** (the
entitlements "Consumer access vs account users" table says ✓ for both; an AI/BI admin matrix says ✗) →
**test in-tenant, don't assert**. Moot for this workstream since these users hold Consumer access. The
confirmed, non-RLS reasons to require Consumer access: **Genie/App visibility** + **reading workspace-bound catalogs**.

---

## GATE 3 — Budget & cost control (know what can BLOCK vs only ALERT)

### 3.1 Databricks Budgets — the asymmetry that surprises everyone

[Create and monitor budgets](https://learn.microsoft.com/en-us/azure/databricks/admin/account-settings/budgets).
A budget = scope filter (workspace / resource type / tag) + ≤4 monthly thresholds + email alerts,
account-admin only, measured in **USD at list price**.

> **[C] "Per-user overrides and usage blocking is only available for Genie budgets."**

| Spend type | Can BLOCK? |
|---|---|
| **Genie budgets** (Resource type = Unity AI Gateway + tag `databricks-product: genie`) | ✅ **Yes** — per-user threshold + **"Block usage" (Genie budgets ONLY)**; near-real-time (not tied to slow system.billing). May overshoot slightly (in-flight requests). |
| **Other Unity AI Gateway LLM** (Pay-Per-Token model serving, `ai_query` batch) | ❌ **ALERT ONLY** — tracked, not blockable. |
| **Serverless SQL warehouse / classic compute** | ❌ **ALERT ONLY** — no enforcement. |

> **Precision:** the "Block usage" checkbox is annotated *"(For Genie budgets only)"* — it is **Genie**, a
> *subset* of Unity AI Gateway, that can be hard-blocked. Not all AI-Gateway spend.

⇒ You **cannot** hard-block warehouse DBUs via budgets. **Cap them at the compute config instead:**
one serverless SQL warehouse per team, short **auto-stop**, small **max scaling / cluster count**, a per-team **tag**.

### 3.2 Serverless usage policies (a.k.a. budget policies) — attribute, don't enforce ⚠ Public Preview
[Attribute usage with serverless usage policies](https://learn.microsoft.com/en-us/azure/databricks/admin/usage/budget-policies):
stamp custom tags on serverless usage → lands in `system.billing.usage.custom_tags`. **Attribution only, no cap.**
⚠ Covers serverless notebooks/jobs/pipelines/model-serving/Apps/Lakebase — **NOT serverless SQL warehouses and NOT Genie**, and not classic compute. → for warehouse attribution, **tag the warehouse itself**.

### 3.3 Genie LLM budget (the one thing you can truly enforce)
[Manage budgets and cost controls for Genie](https://learn.microsoft.com/en-us/azure/databricks/genie/budgets):
- Genie = pay-as-you-go **LLM DBUs since 2026-07-08**, above a **free monthly allowance**.
- Budget scope: **Resource type = Unity AI Gateway**, single tag `databricks-product: genie`.
- Set **shared threshold = ALERT** (pool) + **per-user threshold + "Block usage"** (hard cap, e.g. $30) + group overrides.
- Resolution: within one budget the **most permissive** group wins; across budgets the **most restrictive** wins.
- **Compute to run Genie's SQL is billed separately** and is NOT in the Genie budget.

---

## GATE 4 — Answer quality: is Genie's number CORRECT? (the trust gate)

Gates 1-3 make Genie *safe and affordable*. They do **nothing** for *accuracy*. For business users
self-serving cost/insurance numbers, a confidently-wrong Genie answer is worse than no Genie — and
"Genie is not a security boundary" does not mean "Genie is automatically right." Curating the space **is a DE deliverable.**

| Lever | What it does |
|---|---|
| **Metadata (the 80%)** | Column/table **comments**, clear names, **metric views / semantic layer**. *"Genie quality is 80% metadata quality."* Fix this before anything else. |
| **General instructions + SQL guidelines** | Natural-language steering attached to the Genie space (e.g. "fiscal year starts April"; "always filter `is_current=true`"). Different from table comments. |
| **Trusted assets** ⭐ | **Certified example SQL** + **parameterized UC SQL functions** as deterministic answers. For a regulated/exact metric, have Genie **call a function** instead of generating SQL → reproducible, auditable numbers. |
| **Benchmark / sample questions** | An eval set of known Q→A. Run it and **measure accuracy BEFORE exposing to a business group**; re-run after changes. |
| **Scope narrow** | Fewer, well-modeled **gold** tables beat many raw tables (also ties to GATE 2: a consumer can prompt joins to anything they can SELECT). Narrow space = higher accuracy. |
| **Feedback loop** | Capture 👍/👎, monitor usage, iterate instructions. Assign an **owner** for curation. |

> **The honest caveat to give the business:** Genie is **non-deterministic NL-to-SQL**. For a number that
> must be exact/auditable (chargeback totals, regulatory figures), back it with a **trusted SQL function**
> or a **certified dashboard** — do not present free-form Genie output as the system of record.

Docs: [Genie](https://learn.microsoft.com/en-us/azure/databricks/genie/) · [best practices](https://learn.microsoft.com/en-us/azure/databricks/genie/best-practices) · [trusted assets](https://learn.microsoft.com/en-us/azure/databricks/genie/trusted-assets).

---

## 4. Genie COST MONITORING — the correct formula (and the trap you will hit)

### 4.1 The free tier — mechanics that dictate the formula
[Manage budgets and cost controls for Genie](https://learn.microsoft.com/en-us/azure/databricks/genie/budgets):
- **Free monthly allowance ≈ 150 LLM DBU / identified user / month** (the *150* is a **pricing-page constant**, not in the billing reference docs — don't hardcode without a comment; verify per region).
- **Pooled per user across ALL surfaces** (One + Agents + Code): *"a user who spends \$2 in Genie One and \$10 in Genie Code has \$12 counted"*.
- **Identified users only — service principals get ZERO free tier** and are billed for all usage.
- **Resets on the 1st.** A budget **cannot** remove the free tier.

### 4.2 🚨 The trap: GROSS not net — apply a per-user free-tier floor for BILLED cost

> **`system.billing.usage` is GROSS for `GENIE`** — it records ALL Genie DBUs from the first DBU (incl. within the free tier). **Validated vs AIA tenant data (2026-07): many users with < 150 monthly Genie DBU still have rows** — which the "net" model forbids.

⇒ The official Databricks canonical query (`SUM(usage_quantity * effective_list)`, no free-tier term) = **GROSS list cost** — fine for *attribution*, but it **over-states the bill** by the free-tier credit. For the **BILLED** number (what the Portal reflects), apply the free tier per user: `GREATEST(0, user_monthly_genie_dbu − 150)` — 150 pooled per **identified** user; **SPs/agents (`run_as` = UUID, not email) get NO free tier → don't subtract.** Two more common errors: using `pricing.default` (use **`effective_list.default`**), and hardcoding a Genie `sku_name` (filter on `billing_origin_product='GENIE'` and **join** the SKU).

> ⚠ **Doc-silent:** gross-vs-net isn't stated in official docs. Earlier guidance said "net / don't subtract" (from the canonical query + a community dashboard) — **falsified by AIA data → treat as GROSS.** May vary by tenant/time; re-validate (under net, users < 150 DBU have no rows).

### 4.3 Canonical SQL — GROSS Genie list cost per user/month (for BILLED, apply the §4.2 per-user floor)
```sql
SELECT
  date_trunc('MONTH', u.usage_date)   AS usage_month,
  u.identity_metadata.run_as          AS user_identity,      -- billed principal
  u.usage_metadata.genie.surface      AS genie_surface,      -- One / Agents / Code (informational)
  SUM(u.usage_quantity)               AS gross_dbus,         -- GROSS — for BILLED apply the §4.2 per-user floor
  SUM(u.usage_quantity * lp.pricing.effective_list.default) AS list_cost_usd
FROM system.billing.usage u
JOIN system.billing.list_prices lp
  ON  u.cloud = lp.cloud
  AND u.sku_name = lp.sku_name                                -- JOIN it, don't hardcode
  AND u.usage_start_time >= lp.price_start_time
  AND (lp.price_end_time IS NULL OR u.usage_start_time < lp.price_end_time)  -- point-in-time price
WHERE u.billing_origin_product = 'GENIE'                      -- covers all three surfaces
  AND u.usage_unit = 'DBU'                                    -- bill on DBUs, not TOKEN/ANSWER meters
GROUP BY ALL
-- SUM() self-nets RETRACTION/RESTATEMENT corrections; never read raw rows.
```

### 4.4 Why it still won't match the Azure Portal exactly (irreducible)
`effective_list` is **list** price. The Azure invoice applies four adjustments downstream of the system table:
**negotiated/committed discount · currency (USD→billing currency, FX) · tax · timing** (UTC `usage_date` vs Azure billing cycle + few-hour refresh + late corrections).
→ For a to-the-cent number use the **Azure Cost Management Export** (the AIA cost pipeline already has it);
treat the system-table query as the per-user/per-surface **attribution** layer the export can't give you.
**Reconcile DBU-meter ↔ DBU-meter, never DBU ↔ total.** (For general — not Genie — cost, the biggest gap is classic-compute **VMs**, which are billed separately in the managed RG and never appear in `system.billing`; see `databricks-cost-optimization`.)

---

## 5. Gotchas
1. **Additivity silently defeats the lockdown** — any 2nd entitlement, or pre-migration `users`-group inheritance, turns a "consumer" into an author. Migrate + audit the clone group.
2. **Budgets block ONLY Genie/AI-Gateway LLM spend** — warehouse/classic = alert only → cap at compute config.
3. **`system.billing.usage` is GROSS (validated AIA 2026-07)** — `SUM(dbu×price)` is gross list (attribution); for BILLED cost apply a per-user floor `GREATEST(0, user_monthly_genie_dbu − 150)` (SPs/agents get no free tier). See §4.2. (Earlier "don't subtract 150 / net" was falsified by data.)
4. **Use `pricing.effective_list.default`**, not `pricing.default`; **join** `sku_name`, don't hardcode it.
5. **Genie is not a security boundary — UC is.** A consumer can prompt joins to any table they hold SELECT on → scope grants tightly.
6. **Service principals get no free Genie tier** and no free-tier exemption — billed for all usage.
7. **Budget policies (Preview) don't cover SQL warehouses or Genie** → tag the warehouse itself for attribution.
8. **CAN USE, not CAN MANAGE**, on the warehouse — else consumers can see/manage compute.
9. **Genie needs a running warehouse** to answer — provision one; the consumer can't create it.
10. **system.billing latency (few hours) + list price** → same-day / to-the-cent comparisons will look off; reconcile at month close against the Export.

---

## 6. Test plan
1. **Prereq:** workspace migrated? clone group audited (`biz-consumers-*` NOT a member)?
2. Login as a test consumer → lands in **Genie One** (not full workspace).
3. Try to create job / notebook / cluster → **no surface**. Open SQL editor → **no access**. See warehouses → **none**.
4. Ask Genie about the team's cost → **only that team's rows** (RLS). Prompt a join to another team's table → **empty / no access**.
5. Genie budget: exceed the per-user threshold → **blocked** (LLM). Warehouse: confirm alert fires (no block) and auto-stop caps it.
6. Cost query (§4.3): confirm no `- 150`; validate net-model (low users have no rows); reconcile DBU-meter vs Cost Management Export at month close.

## See also
- `databricks-uc-governance-sharing` → RLS, row filters, `is_account_group_member()`, publish modes, sharing decision tree.
- `databricks-cost-optimization` → system.billing vs Azure Portal (classic VM gap), warehouse auto-stop, "who pays" trap.
- `knowledge_chat/topic-2.1-*` , `topic-2.2-*` (2026-07-17) → the fully-cited AIA source material.
- Escalate: Entra/SCIM + PrivateLink plumbing → `azure-expert`; regulatory sign-off → `governance-consultant`.
