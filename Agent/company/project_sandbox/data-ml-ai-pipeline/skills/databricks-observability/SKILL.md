---
name: databricks-observability
description: >-
  Operational + data-quality observability on Azure Databricks from system tables + Lakehouse
  Monitoring. Use when asked about: monitoring job/pipeline health (success/failure/duration/SLA),
  cluster & SQL-warehouse health, who queried a table (audit), query-history cost/perf, dashboard or
  Genie availability, alerting (SQL Alerts / job notifications / webhooks to Azure Monitor), the
  operational system tables (system.lakeflow.*, system.compute, system.access.audit,
  system.query.history), data-quality / freshness / drift monitoring on the gold layer (Lakehouse
  Monitoring / data profiling, pipeline expectations), or building a pipeline/quality/status
  observability dashboard. Peer to databricks-cost-optimization (shares system.billing, different question).
---

# Databricks — Observability (operational health + data quality)

> Grounded in verified official docs (Microsoft Learn / Databricks), 2026-07-18.
> Peer to `databricks-cost-optimization`: they share `system.billing` but answer different questions —
> **cost = "who spent what" · observability = "is it healthy / did it run / who touched it / is the data good".**
> Kafka/AKS broker health is out of scope → `kafka-strimzi-cdc`. Generic / public-doc knowledge.

The one-line mental model:

> **Two faces of observability: OPERATIONAL (did the pipeline run, is compute healthy, who queried) from
> SYSTEM TABLES, and DATA-QUALITY (is the gold table fresh/complete/undrifted) from LAKEHOUSE MONITORING.**
> A dashboard/Genie is only as trustworthy as both. In a strict insurer, the observability layer *is* the audit layer.

---

## 1. The operational system-tables map (beyond billing)

All account-level, UC-governed. **Updated throughout the day — no real-time / latency SLA** (not for sub-minute paging). Must be enabled by an account admin; reader needs `SELECT`. ⚠ Several are **Public Preview** (query.history, access.audit, serving, some lakeflow/compute tables) — schemas can still change.

| System table | Answers |
|---|---|
| **`system.lakeflow.jobs`** / `job_tasks` | job + task definitions (inventory, ownership) |
| **`system.lakeflow.job_run_timeline`** | every run: `result_state` (SUCCEEDED/FAILED/…), start/end, trigger → **success/failure/duration/SLA trends** |
| **`system.lakeflow.job_task_run_timeline`** | task-level runs → which task failed, retries |
| **`system.compute.clusters`** / `node_timeline` | cluster config + per-node CPU/mem utilization → over/under-provisioning |
| **`system.compute.warehouses`** / `warehouse_events` | SQL-warehouse config + scaling/start/stop events |
| **`system.query.history`** *(Public Preview)* | every SQL query: duration, rows, spill, warehouse, user → **cost-per-query, slow queries, queue** |
| **`system.access.audit`** *(Public Preview)* | **who did what** — logins, queries, grants, dashboard/Genie access → the compliance table |
| **`system.access.table_lineage` / `column_lineage`** | upstream/downstream of the gold table |
| **`system.serving.served_entities` / `.endpoint_usage`** *(Preview)* | model-serving endpoint inventory + usage (schema, not one table; enable usage on the endpoint) |
| **`system.data_quality_monitoring.table_results`** | freshness/completeness anomaly-detection results (see §6) |

> `system.billing.usage` (cost) joins to these by `usage_metadata.job_id / cluster_id / warehouse_id` —
> that's how you put a **dollar** on a slow job or a heavy dashboard warehouse. (See `databricks-cost-optimization`.)

---

## 2. Job / pipeline health + SLA

```sql
-- Failure + duration trend per job (last 30d) from the run timeline
SELECT j.name,
       COUNT(*)                                                        AS runs,
       SUM(CASE WHEN t.result_state = 'FAILED' THEN 1 ELSE 0 END)      AS failures,
       ROUND(AVG(t.period_end_time - t.period_start_time))             AS avg_secs,
       MAX(t.period_end_time)                                          AS last_run
FROM   system.lakeflow.job_run_timeline t
JOIN   system.lakeflow.jobs j ON t.job_id = j.job_id AND j.account_id = t.account_id
WHERE  t.period_start_time >= current_date() - INTERVAL 30 DAYS
GROUP  BY j.name
HAVING failures > 0 OR avg_secs > <sla_secs>
ORDER  BY failures DESC, avg_secs DESC;
```
- **SLA-miss detection:** flag jobs whose `last_run` is older than the expected cadence (didn't run), OR whose duration exceeded the SLA (ran slow). Both are incidents; the "didn't run" one is silent without this.
- **Lakeflow Jobs failure ≠ Declarative Pipeline (DLT) signal** — a DLT/Lakeflow **pipeline** surfaces quality/flow via its **event log**; `system.lakeflow.job_run_timeline` covers the **job** that triggers it. Watch both.
- Retries: `job_task_run_timeline` shows a task that failed-then-succeeded — a flaky task hides inside a "green" job.

---

## 3. SQL warehouse + dashboard/Genie availability

- **Warehouse health** from `system.query.history` + `system.compute.warehouse_events`: queued vs running, **spill** (memory pressure → upsize or optimize the query), auto-stop behaviour, cost-per-query.
- **Dashboard availability = warehouse availability.** A published dashboard is "down" when its refresh warehouse can't start or errors. Monitor the **specific refresh warehouse**; alert on failed scheduled refreshes.
- **Zero-view dashboards** (cost + hygiene): `system.access.audit` for dashboards with no views in 30d → unschedule (see `databricks-cost-optimization` §8.2).
- **Genie availability/usage:** Genie needs a running warehouse to answer; monitor that warehouse + Genie usage/feedback signals (ties to `databricks-genie-governance` — usage/cost via `billing_origin_product='GENIE'`).

---

## 4. Alerting — the native primitives + when to leave Databricks

| Primitive | Use for | Limit |
|---|---|---|
| **Databricks SQL Alerts** | threshold on a query result (e.g. failures > 0, freshness > Xh) → email/webhook | query-based; runs on a schedule, not event-driven |
| **Job notifications** | on-start/success/failure/duration-exceeded per job | job-scoped only |
| **Notification destinations** (Email / Slack / **Teams** / **Webhook** / PagerDuty) | fan-out the above | admin-created; snapshot destinations carry the "one render, one identity" caveat |
| **Webhook → Azure Monitor / Logic App / SIEM** | when you need paging, correlation, or compliance retention beyond Databricks | you build the receiver |

> **Latency reality:** system tables are *"updated throughout the day"* with **no real-time / latency SLA**
> → they are for **trend + audit + daily health**, not sub-minute paging. For real-time SLA breaches, emit
> from the job itself (job notifications) or push a metric to Azure Monitor; don't poll a system table expecting seconds.

---

## 5. Audit operations (the compliance face)

`system.access.audit` answers *"who queried the cost/PII table, when, from where"*:
```sql
SELECT event_time, user_identity.email, action_name,
       request_params.full_name_arg AS object, source_ip_address
FROM   system.access.audit
WHERE  action_name IN ('getTable','commandSubmit','generateTemporaryTableCredential')
  AND  request_params.full_name_arg LIKE '<cat>.gold.%'
  AND  event_date >= current_date() - INTERVAL 7 DAYS
ORDER  BY event_time DESC;
```
- Enable **verbose audit logs** for notebook/command-level actions.
- For compliance-grade retention, **deliver audit logs to a SIEM** (system tables have a retention limit → snapshot to your own Delta if you need long history).
- This is how you evidence "only Team A ever read Team A's cost rows" — the RLS design's proof.

---

## 6. Data-quality observability — two tools, two moments

Dashboards + Genie are only as good as the gold under them. **Three distinct capabilities, three moments** — don't fold them together:

| | **Pipeline expectations** | **Anomaly detection** *(new)* | **Data profiling** *(= former Lakehouse Monitoring)* |
|---|---|---|---|
| When | **at write time** (Lakeflow/DLT pipeline) | at rest, schema/catalog-level, one-click | at rest, per-table, scheduled |
| Mechanism | `EXPECT` rules → warn/drop/fail/quarantine | managed scan → `system.data_quality_monitoring.table_results` | UC monitor → profile + drift metric tables |
| Catches | bad rows entering | **freshness + completeness** | **drift / distribution shift / summary stats / inference** |

> **2026 naming (be precise):** **Lakehouse Monitoring was renamed *Data profiling***; it now sits **alongside a genuinely new *Anomaly detection* capability** under the **Data Quality Monitoring** umbrella. Freshness/completeness = Anomaly detection; drift/distribution = Data profiling. Don't attribute freshness to the profiling monitor.

- **Data-profiling monitor types:** snapshot · time-series · inference. Each emits a **profile metrics** + **drift metrics** table you can dashboard/alert on. *(verify the exact 3 names on the data-profiling subpage before relying on them.)*
- **SLAs on the gold that feeds the dashboard:** freshness (`max(load_ts)` age), completeness (row count vs expected), **custom business rules** (cost never negative; **tag-coverage % ≥ 95** — directly feeds chargeback credibility). Alert on breach via §4.
- **Cost caveat:** monitoring runs compute — schedule it (daily/hourly), don't over-profile every table.

---

## 7. Reference architecture — one observability dashboard

```
system.lakeflow.*   ─┐
system.compute.*     ├─► gold_ops views (job health, warehouse health, freshness, audit)
system.query.history ├─►      │
system.access.audit  ┘       ▼
Lakehouse Monitoring ───► drift/profile metric tables
                             │
                    AI/BI Observability Dashboard  +  SQL Alerts → Teams/webhook
                    (job SLA · warehouse queue · gold freshness · tag-coverage% · audit)
```
- Kafka/AKS broker + Strimzi health is a **separate** pane → `kafka-strimzi-cdc`; join the two dashboards at "did the CDC land in bronze" (freshness of the bronze table = the seam).
- Build it on a serverless SQL warehouse with auto-stop; refresh on a schedule (system tables lag anyway).

## 8. Gotchas
1. **System tables update throughout the day, no latency SLA** — trend/audit/daily health, not real-time paging.
2. **Must be enabled by an account admin** + `SELECT` granted — a real prerequisite in a locked shop.
3. **"Didn't run" is silent** — SLA monitoring must check for *missing* runs, not just failed ones.
4. **A green job can hide a flaky retried task** — check task-level timeline.
5. **Dashboard down = its refresh warehouse down** — monitor the warehouse, not just the dashboard object.
6. **Expectations ≠ Lakehouse Monitoring** — write-time vs at-rest; you usually want both.
7. **Retention limits** on system tables + monitor metrics → snapshot to Delta for long history / audit.
8. **Monitoring costs compute** — schedule; don't profile everything continuously.

## 9. Test plan
1. Force a job failure → confirm it shows in `job_run_timeline` and fires the alert.
2. Stall a table's freshness → confirm the freshness SLA alert fires.
3. Query the gold table as a test user → confirm the read appears in `system.access.audit` under their identity.
4. Drop tag-coverage below 95% on a sample → confirm the custom-metric alert catches it (chargeback guard).
5. Confirm the observability dashboard's own warehouse has auto-stop (don't let the monitor become the cost).

## See also
- `databricks-cost-optimization` — put a $ on a heavy job/warehouse (join billing by job_id/warehouse_id); §0.1 reconciliation.
- `databricks-genie-governance` — Genie usage/cost signals; Genie availability = its warehouse.
- `kafka-strimzi-cdc` — broker/Strimzi health (the other observability pane).
- Sources: [System tables reference](https://learn.microsoft.com/en-us/azure/databricks/admin/system-tables/) · [Jobs system tables](https://learn.microsoft.com/en-us/azure/databricks/admin/system-tables/jobs) · [Query history](https://learn.microsoft.com/en-us/azure/databricks/sql/user/queries/query-history) · [Data quality monitoring](https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/data-quality-monitoring/).
