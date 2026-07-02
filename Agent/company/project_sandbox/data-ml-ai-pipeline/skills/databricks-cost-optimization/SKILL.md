---
name: databricks-cost-optimization
description: STARTER (refine after AIA requirements). The Databricks cost-reduction / re-platform playbook — compute model (job vs all-purpose vs serverless), Photon, cluster right-sizing + autoscaling, what actually drives DBUs, small-file compaction (OPTIMIZE / Z-ORDER / liquid clustering), idle-streaming cost, spot/fleet, system-tables cost observability, and the batch-vs-streaming cost trade-off. Use when asked to cut Databricks/DBU spend, plan a migration to lower cost, size a cluster, diagnose a suddenly-expensive job, or decide streaming vs scheduled batch. Pairs with `spark-tune` (faster jobs = fewer DBUs) — this skill owns the spend/platform levers, spark-tune owns in-job execution.
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
-- Top DBU spend by job over 30 days (system.billing.usage)
SELECT u.usage_metadata.job_id,
       SUM(u.usage_quantity)                       AS dbus,
       SUM(u.usage_quantity * lp.pricing.default)  AS approx_usd
FROM   system.billing.usage u
JOIN   system.billing.list_prices lp
       ON u.sku_name = lp.sku_name AND u.usage_end_time BETWEEN lp.price_start_time
                                        AND COALESCE(lp.price_end_time, current_timestamp())
WHERE  u.usage_date >= current_date() - INTERVAL 30 DAYS
GROUP  BY 1 ORDER BY dbus DESC LIMIT 25;
```

Also: `system.compute.clusters` (config), `system.compute.node_timeline` (utilization → over-provisioning).
**Rule: optimize the top 5 cost drivers, ignore the long tail.**

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

## Test plan / validation
1. **Baseline + attribute** — 30-day spend by job/cluster from system tables before any change.
2. **A/B a change** — e.g. Photon on/off, job vs all-purpose: compare DBU + wall-clock on identical input.
3. **Correctness gate** — assert row counts / DQ unchanged after compaction or trigger-mode change.
4. **Regression watch** — alert on per-job DBU/run rising > X% (cost observability dashboard).

## See also
- `spark-tune` — make each run faster (fewer DBUs); complementary, not overlapping.
- `databricks-streaming-pattern` — trigger modes feeding §5.
- Escalate strategic storage/platform calls (lakehouse layout, UC migration) to `data-architect`.
