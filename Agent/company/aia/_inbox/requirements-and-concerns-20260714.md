# AIA Cost Dashboard — Requirements & Concerns (consolidated, 2026-07-14)

> ## 🔄 UPDATE 2026-07-15 — R5 SPLIT (the pivot)
> Sarunya: **"เปิด shared table ผ่าน UC ได้ — แต่ห้ามเข้า workspace dev เรา"** → the old blanket R5 was TWO things conflated. Split them:
> - **R5-sharing** *(LIFTED)* — UC table sharing IS now allowed. The old "no share even in one metastore" is dead.
> - **R5-network** *(STILL UNKNOWN — the make-or-break)* — does PROD's compute plane have a network path to read DEV's ADLS storage? A UC grant is governance-only; the consumer's compute reads the provider's storage **directly** → storage firewall/PE must admit it, else 403. Sin's read: "network น่าจะยังไม่เปิด แค่ governance." **PoC pending at coredata UAT.**
> - **R5b** *(browser → DEV)* is now MOOT for the target design: D+ users open **their own** workspace, not DEV.
> ⇒ **Option D+ is RESURRECTED as the target** (gets K3+K6 back); Artifact Factory = fallback if R5-network stays closed. See `context-20260715-vscode-uc-share-pivot.md`, `solution-d-plus-resurrection-20260718.md`, skill `databricks-uc-governance-sharing` §6b. Read everything below through this lens: many "DEAD" verdicts assumed R5-sharing was closed.

> **Purpose:** one authoritative list so everyone (Sin, Sarunya, the web chat, the VS Code agents) is looking at the same picture — **before** proposing any more solutions.
> **Status:** supersedes the constraint sets in `context-20260713-2342.md` / `solution-20260713-2342.md`. **C11 ("PROD may read the DEV catalog") was WRONG** — see R5.
> Names are placeholders. No AIA identifiers.

---

## 1. Context

| | |
|---|---|
| **Goal** | An Azure **cost-monitoring dashboard**: each client team sees its own cloud cost, tagged per team, for **chargeback**. |
| **Sin (วศิน)** | Senior DE. Builds the cost pipeline + gold table in **coredata DEV**. Proposes; does not decide. |
| **พี่ Sarunya** | Senior DE / SA. **Owns the requirements.** Believes Databricks should solve this natively. Several of her answers are still pending. |
| **บูม** | Owns the *existing* cost pipeline (drops tags). **Still opaque.** Sin's differentiator = **keeps the tags**. |
| **Ingest (settled)** | Azure Cost Management **Export → ADLS (Parquet) → Databricks**. 5 layers: bronze → persist (tags as `MAP`) → prep → summary → **gold**. |

---

## 2. Environment topology

| Workspace | Role | Notes |
|---|---|---|
| **coredata DEV** | Sin's team. **The cost pipeline + gold table live HERE.** | The dashboard is authored here. |
| **coredata PROD** | Exists — but **the pipeline/dashboard will NOT be promoted here.** | This closes the "prod-to-prod" path. |
| **departmental PROD** | **The client teams' workspace.** Contains **multiple teams**. | Where users actually work. |

**Network / sharing reality:** **coredata DEV is NOT shared with / reachable from departmental PROD.** *(This is the fact that kills every live-query design.)*

---

## 3. REQUIREMENTS (hard — the solution must satisfy all)

| # | Requirement | Source |
|---|---|---|
| **R1** | The cost **gold table stays in coredata DEV**. The pipeline is **not** promoted to coredata PROD or anywhere else. | AIA policy / Sin |
| **R2** | **Client users access from PROD only** (their departmental PROD workspace). They will not log into DEV. | Sin |
| **R3** | Clients must **NOT** become members of the coredata workspace. | Sarunya (strict) |
| **R4** | **Sin's team CANNOT create/deploy any object (dashboard, app, table) in the departmental workspace.** No service principal, no API deploy, no bundle deploy. *(Sin has pushed back on this twice — it is firm.)* | Sin / policy |
| **R5** | 🚨 **coredata DEV is NOT reachable from departmental PROD** (network policy — the environments are not shared). **⇒ No live cross-env query is possible, ever.** | Sin (2026-07-14) — **this replaces the old, wrong "C11 = PROD may read DEV"** |
| **R6** | **Row-level:** each team sees **only its own** cost rows. Multiple teams inside the departmental workspace. | Sarunya |
| **R7** | **Chargeback per team**, driven by the resource **tag**. | Sarunya |
| **R8** | **Monthly cadence** — users are notified/updated every month. | Sarunya |
| **R9** | **Multiple client teams** (not one). | Sarunya |
| **R10** | The delivery should be **automated** (the current manual PDF-by-email is not acceptable long-term). | Sin |

### 3.1 The logical consequence of R1 + R2 + R4 + R5 (this is the crux)
```
Any dashboard placed in PROD must query the gold table…
   …but the gold table is in DEV…
      …and PROD cannot reach DEV (R5)…
         …and we cannot put the dashboard in coredata PROD (R1)…
            …and users only come from PROD (R2)…
               ⇒ NO LIVE-QUERY SOLUTION CAN EXIST.
```
> **⇒ The artifact delivered to PROD must CARRY THE DATA WITH IT (static), or the DATA must first be physically placed somewhere PROD can read.**
> This single sentence defines the entire remaining solution space.

---

## 4. CONCERNS (soft — strong preferences; trade-offs must be argued, not assumed)

### 4.1 พี่ Sarunya's concerns
| # | Concern | Detail / status |
|---|---|---|
| **K1** | **"AI/BI Dashboard is not secure"** | **NOT a written policy.** Her actual fear: *"if you export the link, anyone can access it."* → **Factually false** (no anonymous access; the viewer must be a registered Entra/Databricks identity **and** be explicitly granted). ⚠️ But the *legitimate kernel* is real: the **default publish mode ("Share data permissions")** runs queries as the **publisher** → row filters evaluate as the publisher → **every team sees every row**, silently. Also the setting **"Anyone in my account can view"** would genuinely do what she fears. |
| **K2** | **"It should be self-contained inside Databricks"** | She does not want a separate portal / external tool. ❓ **Ambiguous — must clarify:** does she mean *literally an object inside their workspace*, or *"no separate tool to remember"*? These lead to different solutions. |
| **K3** | **Users should open their own workspace and see their cost there** | Sin's read of what she really wants (she *said* "monthly report", but he believes she means in-workspace). ❓ **Needs confirming.** |
| **K4** | **Monthly notification to users** | She stated this explicitly. |
| **K5** | **Chargeback by team tag** | Formal — feeds Finance. |
| **K6** | **Who pays the compute** | *"Probably the client."* Not decided. |

### 4.2 Sin's concerns
| # | Concern |
|---|---|
| **S1** | **Cannot deploy anything into the departmental workspace** (R4) — has restated this three times; any proposal that needs it is dead on arrival. |
| **S2** | **Cannot promote the pipeline/dashboard to coredata PROD** (R1) — this closes the prod-to-prod path. |
| **S3** | The **only working option today is a manual PDF → email** — which is (a) PDF only, (b) **not automated**, (c) not what Sarunya pictures. |
| **S4** | **Minimum acceptable improvement:** a **static dashboard file (JSON or equivalent) that the user can import themselves** and that renders **without touching DEV data**. |
| **S5** | Tag handling: **keeps tags as a `MAP`** (บูม's pipeline drops them). For row-level, the team key **must be projected to a top-level column** (a row filter cannot bind inside a `MAP`). |
| **S6** | **`az login` / Databricks CLI still blocked by Zscaler TLS interception** → automation tooling is partly unavailable until the CA bundle is fixed. |
| **S7** | **บูม's existing pipeline is still opaque** → risk of duplicate/conflicting work. |

---

## 5. OPEN QUESTIONS that decide the whole solution space

> **These must be answered before any further design.** Each one opens or closes an entire family of solutions.

| # | Question | Why it matters |
|---|---|---|
| **Q1** 🔴 | **Is there ANY storage or channel that coredata DEV can WRITE to and departmental PROD can READ from?** (e.g. an ADLS container, a blob path, a shared storage account, SharePoint, a file drop, email) | **This is THE question.** If YES → we can *physically move* per-team data into PROD's reach → a real, refreshable dashboard becomes possible again. If NO → only file-delivery (PDF/HTML/Excel via email) survives. |
| **Q2** 🔴 | **Does R5 ("not shared / network policy") also forbid a *data export*, or only a *live connection*?** | "The environments are not networked" ≠ "no data may ever move". Cost data was already blessed to cross env (the Portal-export exception). Clarify with Sarunya/security. |
| **Q3** | **Is the departmental side willing/able to do ANYTHING once** — e.g. import a file, create an external table, run a notebook, set up a Git folder? (R4 says *Sin* can't deploy — but can *they* act?) | Determines whether the client can hold a live object at all. |
| **Q4** | **Can Sin's pipeline write per-team extracts into a catalog/schema that the DEPARTMENTAL side owns** (they grant the write, they own the grants)? | The "push model". Needs Q1/Q2 to be yes. |
| **Q5** | **K2/K3:** does "self-contained in Databricks" / "see it in their workspace" mean *literally an object in their workspace*, or *"one place, no extra portal"*? | Decides whether a static file in their workspace counts, or whether a PDF in email is acceptable. |
| **Q6** | **What is the acceptable freshness?** Monthly? Weekly? Daily? | A monthly static snapshot is a very different engineering problem from a live dashboard. |
| **Q7** | **Do the departmental teams have a Databricks SQL warehouse + Consumer entitlement**, and do they have any BI tool already (Power BI)? | Opens the "they build it, we feed it" family. |
| **Q8** | **Metastore topology:** are coredata DEV and departmental PROD on the **same** UC metastore? (Earlier stated "verified same"; the DEV→UAT test suggests the picture is murkier.) | Even if the network blocks live query, this affects any future data-sharing option. |

---

## 6. Status of every option considered so far

| Option | Status | Why |
|---|---|---|
| **D+** (grant table + export `.lvdash.json` → they import) | ❌ **DEAD** | The imported dashboard still issues a **live query against the DEV table**. PROD cannot reach DEV (R5). "table not found" — **always**, regardless of grants or bindings. |
| **A** (UC GRANT only — they query the table themselves) | ❌ **DEAD** | Same reason (R5). |
| **C** (publish in coredata, share the URL to account users) | ❌ **DEAD in spirit** | Technically the query would run on **coredata's** warehouse (so it *could* work) — **but** it fails K1 (her "link" fear), K3 (not in their workspace), and R5 makes the whole cross-env stance hostile. **Keep only as an emergency escape hatch, and only if Sarunya accepts a link.** |
| **E / E2** (Genie Agent) | ❌ **DEAD** | Genie queries live tables → same R5 wall. |
| **F** (Databricks App) | ❌ **DEAD** | Must be **deployed into a workspace** (violates R4) + queries live data (R5) + 2-4× cost + user-auth was Preview. |
| **O** (push model — write per-team data into a departmental-owned catalog) | ⚠️ **CONDITIONAL** | Requires **Q1/Q2/Q4** to be YES. If any storage/catalog exists that DEV can write and PROD can read, **this becomes the leading candidate.** |
| **G** (Delta Sharing / OpenSharing) | ❌ **DEAD** | Same metastore ⇒ not offerable; and providers **cannot share tables that have row filters or column masks**. |
| **Clean Rooms** | ❌ **REJECTED** | ~**$7,500/mo** (vs $10-50); delivers **tables, not dashboards**; per-notebook approval overhead; designed for **cross-organisation** privacy, not internal BI. |
| **N** (monthly per-team PDF via email) | ✅ **ONLY THING THAT WORKS TODAY** | But: **PDF only**, **not automated**, and not what Sarunya pictures. **This is the baseline to beat.** |
| **Static dashboard file with data embedded** | ❓ **Sin's minimum ask** | ⚠️ **`.lvdash.json` contains query syntax + widget settings ONLY — NO data, NO cache** (verified; Gemini's "cache embedded" claim was **false**). So a native Databricks dashboard **cannot** be made static. → *Any static-with-data artifact must come from outside the AI/BI dashboard product.* |

---

## 7. What a valid solution must now look like

Given R1 + R2 + R4 + R5, a solution must be **one of these two shapes**:

### Shape 1 — **Self-contained artifact** (data travels inside the file)
The client opens a file that already contains the numbers. No query, no network, no catalog.
Candidate media: **HTML (with embedded data + charts)** · **Excel (with data + PivotTables/charts)** · **PDF** · a notebook with embedded results · an image.
- ✅ Satisfies R1-R5 by construction.
- ⚠️ Fails K2/K3 if "in their workspace" is taken literally (unless the file is *placed in* their workspace — which needs Q3).
- ✅ Can be **automated** (a scheduled Databricks Job generates + delivers per-team files) — solving S3/R10.
- ⚠️ Row-level security becomes **"generate one file per team"** (isolation by construction), not UC RLS.

### Shape 2 — **Physically move the data into PROD's reach**, then they hold a live object
Sin's job writes per-team extracts to a location the departmental side can read; **they** turn it into a table/dashboard in their own workspace.
- ✅ Restores a genuinely live, in-workspace dashboard (K3), refreshable, and **they pay compute** (K6).
- 🔴 **Entirely dependent on Q1 / Q2 / Q4.** If no shared storage channel exists and none may be created, this shape does not exist.

> **⇒ The single highest-value next action is to answer Q1 and Q2.** Everything else follows from them.

---

## 8. Agreed facts (verified — do not re-litigate)
1. **`.lvdash.json` contains query syntax + widget settings only — no data, no cache, no snapshot.** (Gemini's claim was false.)
2. **`embed_credentials = true` ("Share data permissions") ≠ data embedded.** It only means all viewers' queries run as the **publisher** — the query still executes live at render time. **And it silently defeats row-level security** (every team would see every row).
3. **A dashboard/app is always workspace-scoped.** The only Databricks object that can appear inside another workspace is a **table/view** (and only if the metastore + bindings + network allow it — which R5 forbids here).
4. **Lakeview = AI/BI Dashboard** (same product; API still `/lakeview/`). Legacy "Databricks SQL Dashboard" is **retired**. Databricks One → **Genie One**; Genie Space → **Genie Agent**; Delta Sharing → **OpenSharing**.
5. **Genie requires workspace membership** — an account user without workspace membership cannot see a Genie Agent.
6. **Row filters use `is_account_group_member()`, never `is_member()`**, cannot bind inside a `MAP`, and cannot be applied to a `VIEW`.
7. ⚠️ **Entitlement behaviour change: auto-enabled 2026-07-27, enforced 2026-09-14** — the departmental admin must grant **Consumer access** explicitly.
8. **The DEV→UAT test failed with "table not found"** — a *catalog-resolution* error, not a network timeout. But given R5, the distinction is now moot: **the target (departmental PROD) cannot reach DEV either way.**

---

## 9. Next step
**Confirm this document is correct and complete** (Sin → Sarunya), then answer **Q1 + Q2** (and Q3). Only then design.
