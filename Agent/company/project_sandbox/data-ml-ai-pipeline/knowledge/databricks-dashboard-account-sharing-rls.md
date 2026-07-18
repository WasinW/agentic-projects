# Sharing a Databricks AI/BI Dashboard to Teams Without Workspace Access

**Pattern for:** letting people who are *not* members of your workspace view a
governed dashboard, each seeing only their own rows, without buying them licenses
or workspace entitlements. The canonical case is a central IT/DE team exposing a
FinOps/cost dashboard to client business teams.

> Distilled from the AIA cost-dashboard solution (verified against Microsoft
> Learn / Databricks docs, 2026-07-13). Source transcript:
> `knowledge_chat/aia-cost-dashboard-solution-VERIFIED_20260713.md`. One claim
> remains tenant-dependent — see "The one test that decides".

## The pattern

Build an **AI/BI Dashboard (Lakeview)** in your own workspace on a **Unity
Catalog** gold table → **publish with "Individual data permissions"** → **share
to the viewers' account-level groups** → put a **UC row filter** on the table.

Viewers open a URL, sign in with Entra SSO as **account users**. They never enter
your workspace, are never workspace members, and need **no CAN USE on your SQL
warehouse**. The split that makes it work:

- **data identity = the viewer** → UC row filters/masks evaluate per viewer.
- **compute identity = the publisher** → your warehouse runs the query and pays
  the DBUs; the viewer needs no compute grant, no entitlement, no license.

This is GA, and has a *smaller* misconfiguration surface than a Databricks App
with user authorization (which is Public Preview and puts custom token-forwarding
code in the trust path). Prefer this over an App unless a written policy forbids
dashboards.

## Identity model (the concept people miss)

- **Account user** = an Entra principal registered in the Databricks *account*.
- **Workspace user** = an account user additionally assigned to a workspace with
  an entitlement.
- Sharing a published dashboard to an **account-level group** lets account users
  view it with **no workspace assignment**. With Automatic Identity Management
  (GA; default for accounts created after 2025-08-01) the first login
  auto-adds them to the *account*, not the workspace.
- Groups used in the row filter and the share **must be account-level**.
  Workspace-local groups silently do not resolve for this audience.

## Row-level security

One UC row filter on the gold table, defined once, enforced everywhere
(dashboard, notebook, Power BI, the viewer's own warehouse):

```sql
-- ✅ is_account_group_member()   ❌ is_member()  ← silently FALSE for account users
CREATE OR REPLACE FUNCTION cost_platform.gold.team_row_filter(team_tag STRING)
RETURN is_account_group_member('de-team')                        -- IT/FinOps bypass
    OR is_account_group_member(concat('client-', lower(team_tag)));

ALTER TABLE cost_platform.gold.cost_wide
  SET ROW FILTER cost_platform.gold.team_row_filter ON (tag_team);

GRANT USE CATALOG ON CATALOG cost_platform            TO `client-claims`;
GRANT USE SCHEMA  ON SCHEMA  cost_platform.gold        TO `client-claims`;
GRANT SELECT      ON TABLE   cost_platform.gold.cost_wide TO `client-claims`;
GRANT EXECUTE     ON FUNCTION cost_platform.gold.team_row_filter TO `client-claims`;  -- most-forgotten grant
```

For chargeback-style mappings, drive the filter from a **mapping table**
(`team_tag → account_group`) rather than a naming convention — adding a team
becomes an INSERT, not DDL. At scale, ABAC row-filter policies (GA 2025).

## Non-negotiable gotchas

Each of these fails **silently** — no error points at the cause:

1. **The default publish mode is the security bug.** "Share data permissions"
   (the default) runs as the *publisher*, so every viewer sees the publisher's
   full result set — RLS effectively off. Use **"Individual data permissions"**;
   pin `embed_credentials: false` in the DAB. Never trust the UI default.
2. **`is_member()` returns FALSE for the entire account-user audience.** Use
   `is_account_group_member()`.
3. **A workspace-bound catalog shows account users empty widgets.** An
   auto-created default workspace catalog is bound by default. Set isolation
   mode to `OPEN` (`databricks catalogs update <cat> --isolation-mode OPEN`).
4. **Never email an all-teams PDF to account users.** Subscriptions add account
   users only as static notification destinations (no per-identity RLS, no
   self-subscribe button) → the PDF is not filtered per recipient. Send
   link-only, or use one dashboard per team.
5. **The table must be in a UC catalog** — `hive_metastore` cannot do RLS.

## The one test that decides

Two official pages say Individual permissions preserve per-viewer UC RLS; the
AI/BI admin capability table contradicts them (shows RLS ✗ for account-member
access). **This must be tested empirically in the target tenant** and the result
is the go/no-go for this whole pattern:

> Take one real/test viewer identity that is in a client account group but **not**
> a member of your workspace → publish Individual → share → have them open the
> link. Confirm: it loads, rows are filtered to their team, and there is no
> workspace sidebar.

If it fails → fall back to **one dashboard per team** with Shared data
permissions and a dataset pre-filtered to that team (zero doc ambiguity, and the
only clean way to email per-team PDFs).

## Fallbacks & companions

- **Per-team dashboards (Shared mode)** — the unambiguous fallback; scriptable
  via the Lakeview API / DAB.
- **UC `GRANT` only** — also grant SELECT to client account groups so they query
  the table from *their own* workspace/warehouse: RLS still applies, **their**
  DBUs are charged (real chargeback), $0 to IT. A free companion to the pattern.
- **Per-team monthly PDF job** — backstop if "share" actually means "report".
- **Avoid:** Databricks App user-auth (2-4× cost, Preview, PrivateLink risk),
  Genie (workspace users only — structurally blocked), Delta Sharing (same
  metastore makes it unnecessary), Lakehouse Federation (wrong tool).

## Lock-in note

The gold table is portable Delta; the row filter is a rewritable UC SQL UDF; the
**dashboard + account-user sharing model is Databricks-proprietary**. If low
lock-in matters, Power BI on the UC table via the client's own warehouse is the
escape hatch.

*Related: [architecture-modern-data-ai.md](architecture-modern-data-ai.md) ·
[streaming-batch-patterns.md](streaming-batch-patterns.md)*
