---
name: databricks-cost-optimization
description: STARTER (refine after AIA requirements). The Databricks cost-reduction / re-platform playbook — compute model (job vs all-purpose vs serverless), Photon, cluster right-sizing + autoscaling, what actually drives DBUs, small-file compaction (OPTIMIZE / Z-ORDER / liquid clustering), idle-streaming cost, spot/fleet, system-tables cost observability, and the batch-vs-streaming cost trade-off. Also covers the SERVING layer: Databricks Apps 24/7 billing (no scale-to-zero) + start/stop jobs, serverless SQL warehouse auto-stop, dashboard result-cache, and the "who pays" trap (publisher's warehouse funds every viewer's query). Use when asked to cut Databricks/DBU spend, plan a migration to lower cost, size a cluster, diagnose a suddenly-expensive job, decide streaming vs scheduled batch, or price a dashboard vs a Databricks App. Pairs with `spark-tune` (faster jobs = fewer DBUs) — this skill owns the spend/platform levers, spark-tune owns in-job execution.
---

# databricks-cost-optimization

> **STARTER scaffold — refine after AIA requirements.** Directly serves AIA's likely
> maintenance → re-platform / cost-cut goal. Numbers below are *directional* — confirm against
> AIA's actual system tables + pricing tier before committing to savings claims.

The spend playbook. Sister skill **`spark-tune`** makes a job *faster* (fewer DBUs per run);
this one decides *what runs where, how big, and whether it should run at all*.

## When to use

- "Our Databricks/AWS bill jumped" / "cut DBU spend" / "build the cost case for re-platform".
- Sizing or right-sizing a cluster; choosing job vs all-purpose vs serverless.
- Diagnosing a job that got slow + expensive; deciding streaming vs scheduled batch.

## 0. First — measure, don't guess (system tables)

Cost attribution lives in Unity Catalog **system tables**. Always start here.

```sql
-- Top DBU spend by job over 30 days (system.billing.usage). Point-in-time price join.
SELECT u.usage_metadata.job_id,
       SUM(u.usage_quantity)                                    AS dbus,
       SUM(u.usage_quantity * lp.pricing.effective_list.default) AS list_usd  -- effective_list, not default
FROM   system.billing.usage u
JOIN   system.billing.list_prices lp
       ON u.sku_name = lp.sku_name AND u.cloud = lp.cloud
      AND u.usage_start_time >= lp.price_start_time
      AND (lp.price_end_time IS NULL OR u.usage_start_time < lp.price_end_time)
WHERE  u.usage_date >= current_date() - INTERVAL 30 DAYS
GROUP  BY 1 ORDER BY dbus DESC LIMIT 25;
```

Also: `system.compute.clusters` (config), `system.compute.node_timeline` (utilization → over-provisioning).
**Rule: optimize the top 5 cost drivers, ignore the long tail.**

### 0.1 `system.billing` ≠ Azure Portal Cost Management — reconcile, don't panic

They measure **different things** and are *supposed* to differ. This trips up every "why doesn't my cost query match the portal?" investigation.

| | `system.billing.usage × list_prices` | Azure Cost Management (Export → ADLS) |
|---|---|---|
| Answers | **"who used what DBU"** (attribution) | **"what we actually paid"** (money truth) |
| Contains | **DBU consumption only, at LIST price** | actual $ incl. **classic-compute VMs/disks/IPs**, discounts, tax |
| For classic compute | ❌ **VM/disk NOT here** (billed separately in the workspace's **managed resource group**) | ✅ VM meter *Virtual Machines* + DBU meter *Azure Databricks* |

- **Biggest gap = classic-compute VMs** (often **40–60%** of a cluster's true cost) — they live only on the Azure bill, never in `system.billing`. Serverless is closer (VM cost is bundled into the DBU price).
- **2nd gap = list vs actual:** `effective_list` is list price; your EA/MCA/DBCU-committed rate, FX, and tax are applied only at invoicing.
- **Reconcile DBU-meter ↔ DBU-meter, never DBU ↔ total.** Comparing the DBU query to the *whole* Databricks portal cost is the classic mistake.
- **To approach the portal total:** add classic VM$ from the Export (join by managed-RG / cluster tag) on top of the DBU$. Authoritative $ = the **Export**; use `system.billing` for per-job/team/tag attribution.
- **Genie LLM cost is a special case** — the 150 free DBU/user/month are pre-excluded from `system.billing`, so **do NOT subtract them**. See `databricks-genie-governance` §4.

## 1. Compute model — the biggest lever

| Model | Cost profile | Use for |
|---|---|---|
| **Job (ephemeral) clusters** | Cheapest DBU rate; spins down after run | All scheduled/production batch + `availableNow` streams. **Default.** |
| **All-purpose clusters** | Highest DBU rate; often left running idle | Interactive dev/notebooks **only**. The #1 silent money leak when shared/left on. |
| **Serverless (jobs/SQL/DLT)** | Per-second, no idle, fast start; higher per-DBU | Spiky/short/unpredictable workloads where idle waste > the premium. |

> **Migration win #1:** move scheduled work off all-purpose onto **job clusters**. Common
> 20–40% cut just from this. Quantify per-job from system tables first.

## 2. Photon

Vectorized engine. Bills more DBU/hr but often finishes faster → **net cheaper** on SQL/Delta-
heavy scans, MERGE, aggregations. **Benchmark per workload** (Python UDF-heavy jobs may not gain).
Decision = `photon_dbu_rate * photon_runtime` vs `normal_rate * normal_runtime`, not the hourly rate alone.

## 3. Right-sizing + autoscaling

- Size from **`node_timeline` utilization**, not guesswork. CPU/mem < ~40% sustained → downsize.
- Autoscaling: set a **realistic min** (over-high min = paying for idle) and a capped max.
- Streaming: autoscaling helps little (steady load) — size to steady-state, don't leave max high.
- Driver: only oversize when collecting/broadcasting a lot; otherwise a fat driver is waste.

## 4. Small files / layout — compaction (storage + scan cost)

Small files inflate scan time (DBUs) and S3 GET/LIST.

```sql
OPTIMIZE gold.account_balance;                              -- bin-pack small files
OPTIMIZE gold.account_balance ZORDER BY (account_id);       -- co-locate for filter/join
ALTER TABLE gold.account_balance CLUSTER BY (account_id);   -- liquid clustering (preferred, evolvable)
```

- Prefer **liquid clustering** over static partitioning + Z-ORDER on new tables — adapts without rewrite,
  avoids over-partitioning (a classic small-file generator).
- Enable `delta.autoOptimize.optimizeWrite` + `autoCompact` on streaming sinks (see source templates).
- Schedule `OPTIMIZE` + `VACUUM` as a **job-cluster** maintenance workflow (weekly), not on the hot path.
- `VACUUM` to reclaim S3; keep retention ≥ any time-travel/compliance need before shrinking it.

## 5. Streaming idle cost (often the single biggest waste)

A 24/7 `processingTime` stream bills a cluster around the clock even at near-zero input.

- If latency SLA allows minutes → switch to **`.trigger(availableNow=True)`** on a schedule
  (Airflow/Workflows every 5–15 min). Cluster spins down between runs.
- Consolidate many tiny streams onto one job/cluster instead of one cluster each.
- See `databricks-streaming-pattern` → "Trigger mode".

## 6. Spot / fleet

- Workers on **spot/fleet** with on-demand fallback → big cut for fault-tolerant batch (streaming
  checkpoints + Delta idempotency make interruptions safe to retry).
- Keep the **driver on-demand** (spot driver loss kills the whole job).
- Fleet instance pools reduce spot eviction churn + speed cluster start.

## 7. Batch-vs-streaming trade-off (the strategic question)

| | Real-time stream | Scheduled batch (`availableNow`) |
|---|---|---|
| Cost | High (always-on compute) | Low (spins down) |
| Justified when | Latency SLA is seconds/low-minutes (fraud, real-time bal.) | Hourly/daily freshness is fine |

> **Re-platform heuristic:** challenge every always-on stream. Many "streaming" pipelines exist
> for habit, not SLA — converting to scheduled `availableNow` batch is often the largest single
> saving in an insurance data platform. Confirm each SLA with the business before converting.

## 8. Serving layer: dashboards, SQL warehouses, and Databricks Apps

> Added 2026-07-13 from verified Azure Databricks docs. This is the **serving/consumption** side of the
> bill — invisible in a pipeline-only cost review, and the place where a "cheap little dashboard"
> quietly becomes the most expensive thing you own.

### 8.1 Databricks Apps bill 24/7 — there is NO scale-to-zero

| Fact | Detail |
|---|---|
| Billing | **Per hour while the app is RUNNING — 24/7.** It does not idle down. |
| Scale-to-zero | **Does not exist.** (Horizontal scaling is **Beta** and scales *out*, never to zero.) |
| Sizes | **Medium = 0.5 DBU/hr** (<= 2 vCPU / 6 GB) - **Large = 1 DBU/hr** |
| SKU | **Interactive Serverless** |
| Stopped | **$0.** Code + config are retained; restart takes **10-60 s**. |
| **Hidden second bill** | **An App still needs a SQL warehouse underneath it.** App compute **+** warehouse compute. |

> **Total cost of an App ~= 2-4x the equivalent AI/BI Dashboard** — because you pay App compute *on top of*
> the same warehouse the dashboard would have used alone. Before building an App, ask what it buys you
> that a dashboard does not. Often: nothing.

**The workaround — two scheduled Jobs (start / stop):** since *stopped = $0*, schedule the App to exist
only during business hours. **11h × 5d = 55h/week vs 168h ⇒ ~67% saving** (or ~76% with an 8h/day window).

```python
# Job "app-start" — cron 0 8 * * MON-FRI  |  Job "app-stop" — cron 0 19 * * MON-FRI
import os, requests
HOST   = os.environ["DATABRICKS_HOST"]          # https://adb-<id>.<n>.azuredatabricks.net
TOKEN  = dbutils.secrets.get("<scope>", "sp-token")
APP    = dbutils.widgets.get("app_name")
ACTION = dbutils.widgets.get("action")          # "start" | "stop"  <- one notebook, two jobs

r = requests.post(f"{HOST}/api/2.0/apps/{APP}/{ACTION}",
                  headers={"Authorization": f"Bearer {TOKEN}"}, timeout=60)
r.raise_for_status()                            # fail loud: a silent no-op start = a broken morning
print(ACTION, APP, r.json().get("compute_status", {}).get("state"))
```
Cost of the mechanism itself is ~0 (two tiny serverless jobs). Caveat: the first user before 8am gets a
cold app — shift the cron or accept it. **Never leave a PoC App running over a weekend.**

### 8.2 What actually keeps a dashboard cheap

- **Serverless SQL warehouse with auto-stop 5-10 min.** This is the whole game. A serverless warehouse
  bills per-second and dies between queries — as close to scale-to-zero as the serving layer gets.
  (An App cannot do this; a warehouse can. That asymmetry *is* the cost argument.)
- **Scheduled refresh -> shared result cache.** Refresh the dashboard on a schedule so viewers hit the
  **cached result** instead of each one triggering a fresh warehouse start + scan. N viewers, 1 query.
  This is also why *per-team* dashboards often cost the same or less than one shared one — caches are shared.
- Sizing anchor: SQL Serverless **2X-Small = 4 DBU/hr**. A light multi-team dashboard on a 2X-S with
  auto-stop lands in the low **$100s/mo**, not thousands. Verify $/DBU for your region + tier.
- Kill the long tail: dashboards nobody opens still refresh on schedule. Audit `system.access.audit`
  for dashboards with zero views in 30 days and unschedule them.

### 8.3 The "who pays" trap (matters most for a chargeback dashboard)

A **published** AI/BI Dashboard runs its queries on the **publisher's** warehouse, using the
**publisher's compute credentials** — even when the *data* identity is the viewer's.

> **=> The team that hosts the dashboard pays the DBUs for every viewer's query.**
> On a **cost/chargeback** dashboard this is perfectly ironic: the platform team funds everyone else's
> browsing of their own overspend. Say it out loud to the sponsor **before** you build it.

**The fix is a governance move, not a compute move:** also `GRANT SELECT` on the gold table to the
consumers' **account groups** so they query it from **their own** workspace + **their own** warehouse.
Their DBUs, their bill = **real chargeback**, and $0 marginal cost to you. Ship both: the published
dashboard for casual viewers, the table grant for teams that want to self-serve.
(Mechanics: `databricks-uc-governance-sharing`.)

### 8.4 Serving-layer cost ladder (cheapest -> dearest)

| Option | Order of magnitude | Notes |
|---|---|---|
| **Scheduled report job** (PDF/Excel, per team) | **~$15/mo** | Minutes of serverless job per month. The backstop when "share" means "report". |
| **UC table GRANT** (they query from their own warehouse) | **$0 to you** | Cost moves to the consumer = chargeback. |
| **AI/BI Dashboard** on serverless SQL w/ auto-stop | **~$100/mo** | The default. Publisher pays. |
| **Databricks App** + start/stop jobs | **~$100/mo + the warehouse** | Only if a *written policy* forbids dashboards. |
| **Databricks App** 24/7 | **~$300/mo + the warehouse** | The accidental default. Avoid. |

## 9. Tag governance & the chargeback operating model

Chargeback lives or dies on tags. If clusters/warehouses run untagged, `system.billing.usage.custom_tags`
is full of holes and the per-team query **silently under-attributes**. Enforce, don't hope.

### 9.1 Enforce tags at the source
| Compute | Enforce with |
|---|---|
| **Classic cluster / job** | **Cluster policy** with `custom_tags.<key>` set to `fixed` or `allowlist` → a cluster **cannot start untagged**. |
| **Serverless notebook/job/pipeline/model-serving/Apps/Lakebase** | **Serverless usage (budget) policy** → stamps tags on serverless usage (⚠ Public Preview). |
| **Serverless SQL warehouse + Genie** | ⚠ **NOT covered by usage policies** → **tag the warehouse object directly** (warehouse custom tags flow to `system.billing.usage`). |

> **The coverage gap to say out loud:** the business-user population (dashboards + Genie on serverless
> warehouses) is exactly the slice usage policies **don't** tag → their cost is attributed only if you tag
> the **warehouse**. One warehouse per team, tagged `team=<t>`, is the clean answer (also caps cost — §8.2).

### 9.2 Three tag surfaces — don't confuse them
| Surface | Where it shows | Use |
|---|---|---|
| **custom_tags** (compute-resource + serverless-policy) | `system.billing.usage.custom_tags` | DBU attribution per team |
| **Azure resource tags** (managed-RG VMs/disks) | Azure Cost Management Export | **classic VM** cost per team |
| **default tags** (Vendor:Databricks, etc.) | both | the mechanism that carries your tags to the managed RG |

Cluster custom tags **propagate to the managed-RG VMs/disks** — that's the join that bridges DBU
attribution (`system.billing`) to actual VM$ (the Export). Watch: propagation **delay**, and some resource
types reject some tags — validate one tagged cluster before trusting chargeback.

### 9.3 The showback → chargeback ladder
| Rung | What | Mechanism |
|---|---|---|
| **Showback** | report cost per team, no billing | `system.billing` + tags dashboard |
| **Soft chargeback** | allocate cost to teams (still central budget) | + Azure Export for actual $, VM allocated by tag/DBU-share |
| **Hard chargeback** | team pays its own bill | **consumer queries from THEIR own warehouse** (UC GRANT — `databricks-uc-governance-sharing` §6 option b) |

### 9.4 Minimum tag taxonomy (insurer) + the reconciliation join
Taxonomy: `cost_center · team · environment · workload · data_domain`. Flows into **both** the DBU query
(`custom_tags`) and the Azure invoice (managed-RG resource tags).
```sql
-- Bridge: DBU attribution (system.billing) ⟵join⟶ actual VM$ (Cost Mgmt Export), both by team tag
-- closes the loop §0.1 opens. Export must be ingested as a table (Topic 1 pipeline already does this).
SELECT COALESCE(b.team, x.team) AS team,
       b.dbu_list_usd, x.vm_actual_usd,
       b.dbu_list_usd + x.vm_actual_usd AS approx_total
FROM   ( /* system.billing DBU$ grouped by custom_tags['team'] */ ) b
FULL   OUTER JOIN ( /* Export VM$ grouped by managed-RG tag team */ ) x USING (team);
```

---

## Test plan / validation
1. **Baseline + attribute** — 30-day spend by job/cluster from system tables before any change.
2. **A/B a change** — e.g. Photon on/off, job vs all-purpose: compare DBU + wall-clock on identical input.
3. **Correctness gate** — assert row counts / DQ unchanged after compaction or trigger-mode change.
4. **Regression watch** — alert on per-job DBU/run rising > X% (cost observability dashboard).
5. **Serving layer** — every App is stopped or on a start/stop schedule; every SQL warehouse has
   auto-stop <= 10 min; no dashboard refreshes for zero viewers.

## See also
- `spark-tune` — make each run faster (fewer DBUs); complementary, not overlapping.
- `databricks-streaming-pattern` — trigger modes feeding §5.
- `databricks-uc-governance-sharing` — the sharing model behind §8.3 (who pays / account-group GRANT).
- `databricks-genie-governance` — Genie LLM cost + free-tier (don't subtract 150), Budgets (block only Genie), Consumer-access lockdown.
- Escalate strategic storage/platform calls (lakehouse layout, UC migration) to `data-architect`.
