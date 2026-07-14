# AIA Cost-Dashboard Sharing — VERIFIED Solution (2026-07-13)

> **Supersedes `aia-cost-dashboard-sharing-solution_20260712.md`** (its publish-mode names, `is_member`, and missing workspace-bound-catalog blocker were wrong). Verified against official Microsoft Learn / Databricks docs, 2026-07-13. Presentation-grade — for สิน to take to พี่ Sarunya.

---

## 0. Executive answer
**Build an AI/BI Dashboard in the IT/DEV workspace on the UC gold table → publish with "Individual data permissions" → share to the clients' ACCOUNT-level groups → put a UC row filter on the table.** Clients open a URL, sign in with Entra SSO as **account users**: they never enter the IT workspace, are never workspace members, and **need no CAN USE on your SQL warehouse**. Row-level security applies per viewer.

**The blocker Sin feared ("SQL Warehouse compute affinity forces workspace membership") is FALSE:**
> "**Individual data permission:** Viewers run queries using their own credentials… **Workspace membership is not required.** … **Compute access is always granted by the publisher's credentials.**"
> — [Share a dashboard, Azure Databricks](https://learn.microsoft.com/en-us/azure/databricks/dashboards/share/share)

**data identity = viewer · compute identity = publisher.** IT pays the DBUs; the client sees only their rows; the client never touches the IT workspace.

---

## 1. The three sub-questions

### 1.1 What to build
An **AI/BI Dashboard (Lakeview)** in the IT/DEV workspace on `catalog.gold.cost_wide`, attached to a **serverless SQL warehouse** (auto-stop 5-10 min). Deploy via DAB + Jenkins.

### 1.2 How the target workspace's users SEE it
**Neither a Dashboard nor an App appears inside the client's workspace UI — both are URL-only.** The mechanism:
1. **Identity tier = the ACCOUNT, not the workspace.** An **account user** = an Entra principal registered in the Databricks *account*. A **workspace user** = an account user additionally *assigned to a workspace* with an entitlement. Your clients are already account users (they log into their Departmental workspaces).
2. **Publish** the dashboard → creates a view-only published version addressable by URL.
3. **Share** it to their **account-level group** (`client-claims`) with CAN VIEW, or "anyone in my account can view".
4. They open the link → Entra SSO → they get a **view-only render: no sidebar, no workspace nav, no draft, no other objects**.
5. **Compute:** runs on **your** warehouse using the **publisher's** credentials — viewer needs no warehouse permission, no workspace entitlement, **no license**.

**The only thing that appears INSIDE the client's Catalog Explorer is a UC table share** (Option D below) — not a dashboard, not an app.

### 1.3 Row-level access
**One UC row filter on the gold table, defined once, enforced everywhere** (dashboard, notebook, Power BI, their warehouse).

⚠️ **Must key off ACCOUNT groups** — viewers are not members of the IT workspace, so workspace-local groups will not resolve:
```sql
-- ✅ is_account_group_member()   ❌ is_member()  ← silently returns FALSE for your whole audience
CREATE OR REPLACE FUNCTION cost_platform.gold.team_row_filter(team_tag STRING)
RETURN is_account_group_member('de-team')                                   -- IT/FinOps bypass
    OR is_account_group_member(concat('client-', lower(team_tag)));

ALTER TABLE cost_platform.gold.cost_wide
  SET ROW FILTER cost_platform.gold.team_row_filter ON (tag_team);

GRANT USE CATALOG ON CATALOG cost_platform          TO `client-claims`;
GRANT USE SCHEMA  ON SCHEMA  cost_platform.gold      TO `client-claims`;
GRANT SELECT      ON TABLE   cost_platform.gold.cost_wide TO `client-claims`;
GRANT EXECUTE     ON FUNCTION cost_platform.gold.team_row_filter TO `client-claims`;  -- ⚠️ most-forgotten
```
**Recommended for chargeback:** drive the filter from a **mapping table** (`team_tag → account_group`) instead of a naming convention — decouples Azure tag hygiene from Entra group names; adding a team = insert a row, no DDL. (Later, at scale: **ABAC row-filter policies**, GA 2025.)

Prereqs: table must be in a **UC catalog** (`hive_metastore` cannot do RLS) and the catalog must **not be workspace-bound** (§4).

---

## 2. Verified claims (corrections to what we believed)
| Claim | Verdict |
|---|---|
| Published dashboard accessible **regardless of originating-workspace access** | **TRUE** ([AI/BI admin](https://learn.microsoft.com/en-us/azure/databricks/ai-bi/admin)) |
| Viewer must be an **account user** (no workspace assignment / entitlement / license) | **TRUE** |
| Publish-mode names "embed / don't embed credentials" | **RENAMED** → **"Share data permissions" (DEFAULT)** vs **"Individual data permissions"**. API flag still `embed_credentials: true/false`. **The default is the dangerous one.** |
| Shared mode → RLS evaluated as the **publisher** (all viewers see publisher's rows) | **TRUE — the #1 field failure.** Databricks staff: use "Don't embed credentials" for viewer-based access control |
| Individual mode preserves per-viewer UC RLS | **TRUE per 2 official pages** — ⚠️ **but the AI/BI admin capability table contradicts it** (shows RLS ✗ for account-member access). **→ MUST be empirically tested in AIA's tenant. This test is the decision.** |
| Viewer needs CAN USE on the SQL warehouse | **FALSE** — compute always uses publisher's credentials |
| Which warehouse runs it | **Publisher's, in the IT/DEV workspace → IT pays the DBUs** (chargeback irony — name it to Sarunya) |
| **Workspace-bound catalog** → account users see no data | **TRUE — HARD BLOCKER.** "Dashboard widgets that query workspace-bound securables **do not display data for account users**." An auto-created **default workspace catalog is bound by default** — very plausible trap in a DEV workspace |
| IP access lists apply to account users too | **TRUE** ("regardless of whether they are assigned to a workspace") |
| Databricks **Apps** shareable to account users | **CONTESTED — docs conflict**; plus "**if PrivateLink is enabled… access is blocked** for users on the public endpoint" |
| Apps **User Authorization** applies UC RLS | **TRUE but PUBLIC PREVIEW**; a token-forwarding bug **silently falls back to the app's service principal (full data)** |
| Apps bill **24/7, no scale-to-zero** | **TRUE.** Medium = 0.5 DBU/hr, Large = 1 DBU/hr (Interactive Serverless). Stopped = $0; start/stop jobs ≈ 76% saving |
| Monthly email subscription native w/ PDF | **TRUE** (any cron; PDF + CSV/Excel ≤100k rows; attachments ≤9 MB; ≤100 subscribers) |
| ⚠️ **Subscription gotcha** | "**Account users can only be added as subscribers as a notification destination. There is no Subscribe button for account users.**" A destination is a *static email target*, not an identity → **the PDF is NOT guaranteed RLS-filtered per recipient.** **→ Never email an all-teams PDF to account users. Send link-only, or use per-team dashboards.** |
| **Automatic identity management** | **GA** (default for accounts created after 2025-08-01). Sharing to an Entra group **auto-adds users to the ACCOUNT on first login — not to the workspace.** Exactly the mechanism we want |
| **Genie** as an option | **DEAD** — "can only be granted to **workspace users**" |
| Entitlement-model change | Rolling out 2026-06-15; **auto-enabled 2026-07-27; enforced 2026-09-14** — coordinate with Departmental WS admins |

---

## 3. Options vs requirements
R1 table stays DEV · R2 dashboard w/ table · R4 **no IT-WS access** · R6 tag RLS chargeback · R7 monthly notify · R8 multi-team

| | Option | R1 | R2 | R4 | R6 | R7 | R8 | Cost/mo (5 teams, ~100 users, light) | Effort | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| **A** | **AI/BI Dashboard, Individual data permissions, share to account groups + UC row filter** | ✓ | ✓ | ✓ | ✓ | ✓ (link-only) | ✓ | **$84-114** (SQL serverless 2X-S, ~30h) | Low (1-2 d) | ⭐ **RECOMMEND** — gated on the RLS test |
| **B** | **One dashboard PER TEAM, Shared data permissions**, dataset pre-filtered to that team | ✓ | ✓ | ✓ (docs unanimous) | ✓ (by construction) | ✓ **incl. safe per-team PDF** | ✓ | ~same (shared cache = cheaper) | Low-Med (script via Lakeview API/DAB) | **FALLBACK — zero doc ambiguity; the ONLY clean way to email per-team PDFs** |
| **C** | Databricks App + User Authorization | ✓ | ✓ | ⚠️ contested + PrivateLink risk | ✓ | ✗ (build it) | ✓ | **$256-347 24/7**, or ~$80-105 w/ start-stop — **PLUS the warehouse cost on top** | High | Only if a *written policy* forbids dashboards. Costs 2-4×, does less, is Preview |
| **D** | **UC GRANT only** — clients query the table from **their own** Departmental warehouse (RLS applies), import a `.lvdash.json` you hand them | ✓ | ✗ | ✓✓ | ✓ | ✗ | ✓ | **$0 to IT** — **their** warehouse pays = **real chargeback** | Low for you | ⭐ **COMPANION to A** — solves "why is IT paying?" |
| **E** | Delta Sharing | ✓ | ✗ | ✓ | ~ | ✗ | ✓ | client-side | Med | **Unnecessary** — same metastore verified |
| **F** | **Per-team monthly PDF/Excel job** | ✓ | ✓ | ✓✓ | ✓ | ✓✓ | ✓ | **$14-19** | Lowest | **BACKSTOP** if "share" really means "report" |
| **G** | Power BI on UC via client's warehouse | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | client's | Med | Politically strong (AIA has PBI); needs them to be workspace users in **their own** WS (they are); lowest lock-in |
| H | Genie | — | — | ✗ | — | — | — | — | — | **Dead** (workspace users only) |
| I | Embedding for external users | ✓ | ✓ | ✓ | ~ | ✗ | ✓ | + hosting | High | Public Preview; overkill |
| J | Lakehouse Federation | — | — | — | — | — | — | — | — | **Wrong tool** (queries external DBs *into* Databricks) |

**Cost note (Azure, verify SEA $/DBU):** SQL Serverless 2X-S = **4 DBU/hr**; Apps Medium = **0.5 DBU/hr**. The App costs **2-4× total** because you pay App compute **plus** the warehouse — and buys a *Preview* auth mode instead of a *GA* one.

---

## 4. "AI/BI Dashboard is not secure" — technical verdict
**FALSE as stated — but it points at a real footgun.**

**The legitimate kernel:** the **default** publish mode ("Share data permissions") uses the **publisher's** credentials, so **UC row filters are evaluated as the publisher and every viewer sees the full result set.** If anyone at AIA once published on defaults and "RLS didn't work", that is exactly what they saw. It is the most common AI/BI misconfiguration in the field.

**What is false:** no anonymous access exists (account identity + Entra SSO required; no public link) · IP access lists apply to account users too · with Individual permissions the query hits UC **as the viewer**, enforced by the **same UC engine, same code path** as any notebook/App query · dashboard events are in `system.access.audit` · viewers get **no workspace surface at all**.

**Head-to-head:**
| | AI/BI Dashboard (Individual) | Databricks App (User Auth) |
|---|---|---|
| Identity vs UC | Viewer | Viewer |
| RLS / masks | Yes (UC) | Yes (UC) |
| Auth | Entra SSO, no anonymous | Entra SSO, no anonymous |
| Maturity | **GA** | **Public Preview** |
| Custom code in the trust path | **None** | **Yes** — must forward `x-forwarded-access-token`; a bug silently queries as the **service principal (full data)** |
| Ways to misconfigure into a leak | **1** (wrong publish mode) | **≥4** (wrong auth mode, token not forwarded, over-broad scopes, SP over-granted) |
| PrivateLink | Works | **Documented risk of blocked access** |

**Conclusion:** an AI/BI dashboard published with **Individual data permissions**, on a **UC-row-filtered** table, behind **Entra SSO + IP access lists**, is **at least as secure as — and has a smaller misconfiguration surface than — a Databricks App with user authorization**, and it is **GA rather than Preview**.

**Questions to test policy vs misconception (ask neutrally):**
1. Is there a **written** AIA policy naming AI/BI dashboards? (ask for the policy ID)
2. Which specific risk — anonymous access / cross-team leakage / data egress / authentication? (each has a named control)
3. Was there a prior incident? If yes → **which publish mode?** (near-certainly the default → a config bug, not a product flaw)
4. Would it be satisfied by: viewer's own Entra identity + UC row filters + SSO-only + IP-restricted + downloads disabled + full audit?
5. Is a Databricks App approved? Note its user-auth mode is **Public Preview** — a policy that bans a GA feature and permits a Preview one is self-inconsistent.

---

## 5. Pre-flight checklist (verify in AIA's tenant BEFORE presenting)
| # | Check | How | If it fails |
|---|---|---|---|
| 1 | Same UC metastore | ✅ **already VERIFIED** | — |
| 2 | **Catalog isolation mode = `OPEN`** (not workspace-bound) | `databricks workspace-bindings get-bindings catalog <cat>` · or Catalog Explorer → catalog → **Workspaces** tab | **Account users see EMPTY widgets.** Fix: `databricks catalogs update <cat> --isolation-mode OPEN`. ⚠️ auto-created **default workspace catalog is bound by default** |
| 3 | ⭐ **THE TEST:** account user + Individual permissions + row filter → sees only their rows | one real/test client identity (in a client account group, **NOT** an IT-WS member) → publish Individual → share → they open the link. Confirm: loads · rows filtered · no sidebar | Docs contradict here → **this test decides.** If it fails → **Option B** |
| 4 | Client groups are **ACCOUNT-level** (not workspace-local) | Account console → User management → Groups | workspace-local groups **won't resolve** for account users |
| 5 | Automatic identity management / SCIM covers clients | Account console → User provisioning | admin must register identities/groups first |
| 6 | IP access lists / front-end PrivateLink | Admin settings → Security | account users must be on the approved network |
| 7 | SSO enforced (not OTP fallback) | Account console → SSO | OTP is a weaker story to security |
| 8 | Email notification destinations exist | Workspace admin → Notification destinations | you can't create them — need admin |
| 9 | Serverless SQL warehouse + auto-stop 5-10 min | SQL warehouses | cost blowout otherwise |
| 10 | Downloads decision (SQL results download) | Settings → Security | turning off = cheap concession that buys goodwill |
| 11 | **Publish mode = Individual (NOT the default)** | Publish dialog / `embed_credentials: false` in DAB | **the default is the leak** |
| 12 | Table is in a **UC catalog** (not `hive_metastore`) | `SHOW CATALOGS` | RLS impossible in hive_metastore → migrate (CTAS/deep clone/UCX) |

---

## 6. Questions for Sarunya (in this order)
1. **"Share" = live dashboard, or monthly report?** (decides A/B vs F — bring both, priced)
2. **Who pays the compute?** A published dashboard means **the IT warehouse pays for client queries** — ironic for a chargeback tool. IT absorbs it, or clients query from their own warehouse (Option D) so **their** DBUs are charged?
3. Can an admin add the client Entra groups as **ACCOUNT-level** groups? (no workspace assignment needed)
4. **Is the catalog workspace-bound?** (if yes → account users see nothing)
5. **Confirm "no IT-workspace access" means "not a member of the IT workspace"** — NOT "must not receive any data originating from the IT workspace". The second kills A, B **and** C; only Delta Sharing / reports survive.
6. Who claims "AI/BI is not secure", and is it **written** policy? (offer the §4 control set as formal mitigation)
7. Can you get **one test client identity** for the §5-item-3 test?
8. Is front-end **PrivateLink** enabled?
9. Do Departmental users already have Consumer/DBSQL entitlement in **their own** WS? (opens D and G at zero identity cost)
10. Monthly notification: **Teams or email**? (needs a workspace admin to configure — request early)

---

## 7. Recommendation
- **Primary: Option A** — AI/BI Dashboard + **Individual data permissions** + share to **account groups** + **mapping-table-driven UC row filter** + **link-only** monthly notification.
- **Fallback: Option B** — per-team dashboards with Shared data permissions (zero doc ambiguity; the only safe way to email per-team PDFs). Trivial at 5 teams; scriptable.
- **Companion: Option D** — also `GRANT SELECT` to client account groups → self-service in **their** workspace, **their** warehouse pays = real chargeback. Free. Hand them the `.lvdash.json`.
- **Backstop: Option F** — per-team monthly PDF job (~$15/mo, 1 day) if "share" means "report".
- **Do NOT build:** Databricks App (2-4× cost, Preview auth, contested account-user access, PrivateLink risk) · Genie (structurally blocked) · Delta Sharing (unnecessary) · Lakehouse Federation (wrong tool).

## 8. Watch-outs
- **The default publish mode is the security bug** — encode `embed_credentials: false` in DAB; never trust the UI default.
- **Never email an all-teams PDF to account users** (not per-identity RLS-filtered; no self-subscribe button). Link-only or Option B.
- **`is_member()` silently returns FALSE for your entire audience** — use `is_account_group_member()`.
- **Workspace-bound catalog = silent empty widgets**, with no error pointing at the cause.
- Caps: attachments ≤9 MB · ≤100 subscribers · table visuals ≤100k rows.
- **Entitlement model change: auto 2026-07-27 / enforced 2026-09-14.**
- **Lock-in:** the gold table is portable Delta; the row filter is a UC SQL UDF (rewritable); the **dashboard + account-user sharing model is Databricks-proprietary**. Say it out loud. Option G (Power BI on UC) is the low-lock-in path if that matters.

*Sources: Microsoft Learn — [Share a dashboard](https://learn.microsoft.com/en-us/azure/databricks/dashboards/share/share) · [AI/BI admin](https://learn.microsoft.com/en-us/azure/databricks/ai-bi/admin) · [Entitlements](https://learn.microsoft.com/en-us/azure/databricks/security/auth/entitlements) · [Schedules & subscriptions](https://learn.microsoft.com/en-us/azure/databricks/dashboards/share/schedule-subscribe) · [Workspace-catalog binding](https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/access-control/workspace-catalog-binding) · [Automatic identity management](https://learn.microsoft.com/en-us/azure/databricks/admin/users-groups/automatic-identity-management/) · [Databricks Apps auth](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/auth) · [Compute size](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/compute-size) · [Serverless DBU by SKU](https://learn.microsoft.com/en-us/azure/databricks/resources/pricing) · Databricks Community (RLS-not-working; Apps cost -76%).*
