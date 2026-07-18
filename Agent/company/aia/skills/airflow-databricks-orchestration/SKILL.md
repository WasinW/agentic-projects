---
name: airflow-databricks-orchestration
description: STARTER (refine after AIA requirements). Patterns for Airflow (MWAA) orchestrating Databricks jobs — DatabricksSubmitRunOperator vs DatabricksRunNowOperator, reusing a shared job cluster across tasks, idempotent + retriable tasks, dependency wiring, backfill via catchup + data_interval, sensors/deferrable operators, secrets/connections, and dev→staging→prod env promotion. Use when building or reviewing an Airflow DAG that triggers Databricks, designing retries/backfill/idempotency, choosing which Databricks operator, or wiring secrets + per-env config. Carries Wasin's config-driven, dependency-checked orchestration discipline onto Airflow+Databricks.
---

# airflow-databricks-orchestration

> **STARTER scaffold — refine after AIA requirements.** Assumes AWS-managed Airflow (MWAA) +
> Databricks; no AIA-internal DAGs assumed. Encodes Wasin's existing config-driven /
> dependency-check orchestration habits onto this stack.

## When to use

- Building/reviewing an Airflow DAG that triggers Databricks jobs.
- Designing retries, backfill, idempotency, or env promotion for orchestrated pipelines.
- Choosing `SubmitRun` vs `RunNow`; sharing a job cluster across tasks; wiring secrets.

## 1. Operator choice — RunNow vs SubmitRun

| `DatabricksRunNowOperator` | `DatabricksSubmitRunOperator` |
|---|---|
| Triggers a **job defined in Databricks** (job_id) | Defines the run **inline from Airflow** (notebook/JAR/cluster spec) |
| Job owns cluster + config (deploy via Terraform/Asset Bundles) | Airflow owns the spec |
| **Preferred** — clean separation, Databricks UI shows lineage, config in one place | Use for ad-hoc / dynamic specs only |

```python
from airflow.providers.databricks.operators.databricks import (
    DatabricksRunNowOperator, DatabricksSubmitRunOperator)

run_silver = DatabricksRunNowOperator(
    task_id="raw_to_persist",
    databricks_conn_id="databricks_default",     # connection, not inline token (see §6)
    job_id="{{ var.value.silver_job_id }}",      # per-env via Airflow Variable
    jar_params=[],
    notebook_params={"data_interval": "{{ ds }}"},  # pass the logical date down -> idempotency
    retries=2, retry_delay=__import__("datetime").timedelta(minutes=5),
)
```

## 2. Reuse one job cluster across tasks (cost)

Spinning a fresh cluster per task is slow + wasteful. Define a **multi-task Databricks Job** with a
shared job cluster (via Asset Bundles/Terraform) and trigger it once with `RunNow` — or, if
orchestrating task-by-task from Airflow, share a cluster with `SubmitRun` + `existing_cluster_id` /
a job-cluster `job_cluster_key`. Avoid all-purpose clusters from Airflow (see `databricks-cost-optimization` §1).

## 3. Idempotent + retriable tasks (non-negotiable)

- **Pass the data interval down**, never `now()`. The task must produce the same output for the same
  `{{ ds }}` / `{{ data_interval_start }}` no matter when it runs (enables safe retry + backfill).
- Databricks side does the dedupe: `txnAppId`/`txnVersion` for appends, `MERGE` with an
  `update_date <` guard for upserts (see `databricks-streaming-pattern` §5).
- `RunNow`'s `idempotency_token` (deterministic from dag_run) prevents a retry double-submitting a run.
- Set `retries` + exponential `retry_delay`; reserve alerting for final failure, not transient retries.

## 4. Dependencies, catchup + backfill

```python
import pendulum
from airflow import DAG
with DAG(
    dag_id="aia_streaming_batch_ingest",         # STARTER name
    schedule="0 * * * *",                         # hourly availableNow batch (cost-aware, see §below)
    start_date=pendulum.datetime(2026, 1, 1, tz="Asia/Bangkok"),
    catchup=False,                                # True ONLY for a deliberate, rate-limited backfill
    max_active_runs=1,                            # serialize -> no overlapping writes to same target
    default_args={"owner": "data-eng", "depends_on_past": False},
    tags=["aia", "starter", "databricks"],
) as dag:
    bronze >> silver >> gold                       # explicit lineage = dependency-check discipline
```

- **Backfill:** flip `catchup=True` with a bounded window + `max_active_runs` to avoid a thundering
  herd of clusters; rely on §3 idempotency so re-runs are safe.
- Cross-DAG/dataset deps: prefer **Airflow Datasets** (data-aware scheduling) over brittle
  `ExternalTaskSensor` where possible.

## 5. Sensors — prefer deferrable

For "wait for upstream file/partition", use **deferrable operators / sensors** (async, free up
worker slots) over classic poke-mode sensors that pin a worker. Databricks provider run-state is
already async-friendly — `deferrable=True` on the operator releases the slot while the job runs.

## 6. Secrets + connections

- Databricks auth via an **Airflow Connection** (`databricks_default`) backed by MWAA's Secrets
  Manager backend — never a token literal in DAG code.
- Job-level secrets (Kafka/MSK creds, S3) live in **Databricks secret scopes** backed by Secrets
  Manager, referenced as `{{secrets/scope/key}}` in the job — not passed through Airflow.
- PII / regulated-data handling → escalate to `governance-consultant` (PDPA / OIC for insurance).

## 7. Env promotion (dev → staging → prod)

- DAG code identical across envs; **all env-specific values via Airflow Variables / per-env config**
  (job_ids, paths, schedules) — the config-driven principle. No literals in DAG bodies.
- Promote DAGs through Git → S3 (MWAA picks up); promote Databricks jobs via **Asset Bundles**
  (`databricks bundle deploy -t prod`) so Airflow only references a `job_id` per env.

## Test plan
1. **DAG integrity** — `pytest` import check (no cycles, valid schedule, all tasks reachable).
2. **Idempotency** — run the same `{{ ds }}` twice; assert identical Databricks output (counts/DQ).
3. **Retry** — inject a transient failure; assert auto-retry succeeds with no duplicate data.
4. **Backfill** — run a 3-day catchup on staging; assert `max_active_runs` honored + correct results.
5. **Secrets** — assert no token/credential literal in any DAG file (CI grep gate).

## See also
- `databricks-streaming-pattern` — `availableNow` jobs this DAG schedules; idempotent writes.
- `databricks-cost-optimization` — job-cluster reuse, batch-vs-streaming scheduling.
- `spark-tune` — when a triggered job itself is slow.
- Escalate prod SLA/on-call + incident runbooks to `data-ops`.
