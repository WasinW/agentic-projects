# Delivering a Dashboard Cross-Workspace via Unity Catalog Share

**Pattern for:** a central DEV team exposing a governed table (and a dashboard
built on it) to a *different* workspace's users, who query it from **their own**
workspace and warehouse — never entering the provider's workspace. The client's
warehouse pays for the compute (real chargeback).

> Distilled from the AIA cost-dashboard cross-workspace pivot
> (Sarunya lifted the "no UC share" constraint on 2026-07-15; network facts
> verified against Azure Databricks docs). Source transcripts:
> `knowledge_chat/context-20260715-vscode-uc-share-pivot.md`,
> `knowledge_chat/aia-cost-dashboard-solution-VERIFIED_20260713.md`. Several
> tenant facts are still open — see "Open — resolved by the PoC".
>
> Sibling approach (publisher pays, no client workspace at all):
> [databricks-dashboard-account-sharing-rls.md](databricks-dashboard-account-sharing-rls.md).

## The core lesson

**A `GRANT` is necessary but not sufficient for cross-workspace access.** Unity
Catalog governance (the grant) and network reachability are **two separate
gates** on different layers. Sharing works only when *all* of these hold:

1. **Same metastore** — provider and consumer workspaces share one UC metastore.
   (Different metastore ⇒ you need Delta Sharing, and **row filters / column
   masks do not travel through a share**.)
2. **Grant on the securables** — `USE CATALOG` + `USE SCHEMA` + `SELECT` on the
   table + `EXECUTE` on any row-filter function (the last is the most-forgotten).
3. **Catalog not workspace-bound** — isolation mode `OPEN`, or a `READ_ONLY`
   binding to the consumer workspace. An ISOLATED catalog bound only to DEV is
   invisible elsewhere even with grants.
4. **External-location / storage-credential not workspace-bound** — a governance
   gate separate from the catalog; if bound only to DEV, other workspaces can't
   read even with network open + grants. Check the securable's **Workspaces** tab.
5. **Network path open** — this is the gate people forget. See below.

## Why network is a second gate (credential vending)

UC does **credential vending**: when the consumer's warehouse runs `SELECT`, UC
hands its compute a short-lived credential and **the consumer compute plane reads
the provider's ADLS storage directly** — the data does not proxy through the
control plane. So the consumer's compute subnet must be able to reach the
provider's storage account:

```
consumer warehouse runs SELECT
   → UC vends short-lived credential to that compute
   → consumer compute plane ── reads files directly ──► provider ADLS
                                  (bypasses control plane)
   if storage firewall denies the consumer subnet → error 403
```

> "Cloud storage URLs must be accessible through firewall and network controls."
> — [UC credential vending, Requirements](https://learn.microsoft.com/en-us/azure/databricks/external-access/credential-vending)

**No UC mode proxies data through the control plane to dodge this** (Lakehouse
Federation is the only "no direct storage" path, but that's JDBC to a foreign
engine — a different data path, not this case).

The network ask is a **standard Azure pattern** (open a path from consumer compute
to provider storage), which is easier to justify to infra than any workspace-login
exception:

| Consumer compute | Open (on the provider's ADLS) |
|---|---|
| Classic (VNet-injected) | private endpoint from consumer VNet · or VNet/subnet rule on storage firewall · or peering + rule |
| Serverless | associate provider storage with an NSP + allow `AzureDatabricksServerless.<region>` · or private endpoint from the consumer's NCC |
| Either | same region · if public access is off, enable "Allow Azure trusted services" |

(Serverless subnet-ID allowlists were retired 2026-06-09 → must move to NSP.)

## Two failure modes people conflate

- **403 / connectivity error** = the **network** gate is closed (firewall). Not a
  data problem.
- **Empty result, 0 rows, no error** = the **row filter** returned false for this
  principal. Governance and network are fine; it's filter logic.

Keeping these apart is what makes cross-workspace debugging fast.

## Delivering the dashboard itself

The table travels via the grant; **a dashboard is a workspace object and does not
auto-appear** in the consumer workspace. Two mechanisms — they test different things:

| Way | How | What it actually proves |
|---|---|---|
| Publish + share URL | publish in DEV → share to account user → open URL | ⚠️ the URL points at DEV → this tests "browser reaches DEV", **not** the client-side pattern |
| **Export → Import** ✅ | export `.lvdash.json` → import into the consumer workspace → repoint to their warehouse → open | the real cross-workspace pattern — client's own workspace + warehouse |

Row filters still enforce per-viewer because the metastore is shared and Databricks
compute applies them at query time — confirmed to work cross-workspace.

## Verifying it (the decisive test needs no dashboard)

Run in the consumer workspace's SQL editor after granting:

```sql
SELECT * FROM <cat>.cost.cost_wide LIMIT 10;
```

| Result | Meaning |
|---|---|
| rows, correctly filtered | governance + network + RLS all work ✅ |
| 403 / connectivity error | network gate closed → open the storage path |
| empty, 0 rows | row filter returned false — everything works, check filter logic |
| table/catalog not found | different metastore, or catalog ISOLATED, or grant incomplete |

Fast pre-checks: `SELECT current_metastore();` in both workspaces must match; then
the four grants; then the `SELECT`. Test in an environment where you hold full
rights (e.g. a UAT that shares the metastore) to isolate the "user lacks
permission" variable — but note a UAT pass does **not** prove the *production*
consumer's network path, which is usually the last variable to clear.

## Open — resolved by the PoC (do not present as settled)

- Same metastore, provider vs consumer? (`current_metastore()` on both)
- Catalog isolation: `OPEN` or `ISOLATED`?
- Is the production consumer's compute→storage network path actually open?
- External-location / storage-credential workspace binding scoped to DEV only?
- Delta Sharing as a fallback if metastores differ (loses row-filter travel).

## Where this sits

The pipeline, gold table, and row filter are reusable regardless of delivery. A
per-team email report (PDF/Excel) **already ships as the interim** while the
network path is negotiated; the UC-share + client-side dashboard is the **target**
that unlocks the moment storage networking is opened. As of writing the decisive
PoC (the `SELECT ... LIMIT 10` from the consumer workspace) has **not been run**,
so the network gate remains unproven — treat every "Open" item above as live.
