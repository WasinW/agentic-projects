# 05 - Health Check DAGs (Airflow)

> Programmable cross-system health checks every 15 minutes

## Architecture

```
Cloud Composer (every 15 min)
  → Task 1: Check Dataflow streaming jobs (status, lag)
  → Task 2: Check batch job freshness (last success)
  → Task 3: Check BQ row counts (data freshness)
  → Task 4: Check Pub/Sub backlog
  → Alert if anomalies detected
```

## DAG Example

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from google.cloud import monitoring_v3, bigquery

PROJECT_ID = "the1-insight-prod"
REGION = "asia-southeast1"

STREAMING_JOBS = {
    "customer-profile-v3-streaming": {
        "max_system_lag_seconds": 300,
        "max_watermark_age_seconds": 600,
    },
}

def check_streaming_jobs(**context):
    from googleapiclient.discovery import build
    dataflow = build("dataflow", "v1b3")
    alerts = []

    for job_name, thresholds in STREAMING_JOBS.items():
        result = dataflow.projects().locations().jobs().list(
            projectId=PROJECT_ID, location=REGION, filter="ACTIVE",
        ).execute()

        matching = [j for j in result.get("jobs", [])
                    if job_name in j.get("name", "")]

        if not matching:
            alerts.append(f"CRITICAL: No active job for {job_name}")
            continue

        job = matching[0]
        if job.get("currentState") != "JOB_STATE_RUNNING":
            alerts.append(f"WARNING: {job_name} state={job['currentState']}")

    if alerts:
        raise Exception(f"{len(alerts)} issues: {alerts}")

def check_bq_freshness(**context):
    client = bigquery.Client(project=PROJECT_ID)
    alerts = []

    checks = {
        "insight.ms_personas": {
            "field": "etlLoadTimestamp",
            "max_hours": 2,
        },
    }

    for table_ref, cfg in checks.items():
        query = f"""
        SELECT MAX({cfg['field']}) as latest
        FROM `{PROJECT_ID}.{table_ref}`
        WHERE {cfg['field']} >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
        """
        result = list(client.query(query).result())
        if not result or result[0].latest is None:
            alerts.append(f"CRITICAL: {table_ref} no data in 24h")

    if alerts:
        raise Exception(f"{len(alerts)} issues: {alerts}")

def check_pubsub_backlog(**context):
    from google.cloud import pubsub_v1
    subscriber = pubsub_v1.SubscriberClient()
    alerts = []

    subs = {
        f"projects/{PROJECT_ID}/subscriptions/ms-personas-datapipeline-dataflow-subscription": {
            "max_unacked": 10000,
        },
    }

    for sub_path, cfg in subs.items():
        # Use monitoring API for backlog
        # (Pub/Sub API doesn't expose backlog count directly)
        pass  # Implement via Cloud Monitoring API

    if alerts:
        raise Exception(f"{len(alerts)} issues: {alerts}")

def send_slack_alert(**context):
    # Collect failures from upstream tasks
    import requests
    ti = context["ti"]
    # Send to Slack webhook
    pass

with DAG(
    "pipeline_health_check",
    default_args={
        "owner": "data-team",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    },
    schedule_interval="*/15 * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["monitoring"],
) as dag:

    t1 = PythonOperator(
        task_id="check_streaming",
        python_callable=check_streaming_jobs,
    )
    t2 = PythonOperator(
        task_id="check_bq_freshness",
        python_callable=check_bq_freshness,
    )
    t3 = PythonOperator(
        task_id="check_pubsub",
        python_callable=check_pubsub_backlog,
    )
    alert = PythonOperator(
        task_id="send_alert",
        python_callable=send_slack_alert,
        trigger_rule="one_failed",
    )

    [t1, t2, t3] >> alert
```

## Pros / Cons

| Pros | Cons |
|------|------|
| Full programmability | Requires Composer infra |
| Can correlate across systems | Schedule-based (not real-time) |
| Business logic checks (row counts) | DAG itself can fail |
| Custom Slack/email formatting | |

## Applicability

| Pipeline Type | Applicable | What to Check |
|--------------|:--:|------------|
| Dataflow Streaming | YES | Job status, lag, worker count |
| Dataflow Batch | YES | Last success time, duration |
| Cloud Run Batch | YES | Last execution status |
| Dataform | YES | Last invocation status |
