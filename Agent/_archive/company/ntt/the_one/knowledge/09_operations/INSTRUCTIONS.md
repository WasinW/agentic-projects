# Operations Instructions

> AI: Read this file when troubleshooting pipelines, restarting jobs, running initial data loads, or monitoring.

## Quick Reference

```bash
# Check Dataflow job status
gcloud dataflow jobs list --project "the1-loyalty-data-<env>" --region asia-southeast1

# Drain streaming job (graceful)
gcloud dataflow jobs drain <JOB_ID> --project "the1-loyalty-data-<env>" --region asia-southeast1

# Cancel streaming job (immediate)
gcloud dataflow jobs cancel <JOB_ID> --project "the1-loyalty-data-<env>" --region asia-southeast1

# Check BQ data freshness
bq query --project_id="the1-loyalty-data-<env>" --use_legacy_sql=false \
  "SELECT MAX(ingestedTHDate) FROM refined.member_tier"

# Check Iceberg metadata
gsutil cat "gs://<bucket>/<table>/metadata/version-hint.text"
```

---

## 1. Troubleshooting

### OOM (Out of Memory)

**Symptoms:** Workers crash with OOM, job restarts repeatedly.

**Log filter:**
```
resource.type="dataflow_step"
resource.labels.job_id="<JOB_ID>"
textPayload=~"OutOfMemoryError|MemoryError|OOM"
```

**Solutions:**
1. Increase `--max-workers` in deploy job
2. Use larger machine type: `--worker-machine-type n1-highmem-4`
3. Reduce `iceberg.batch_size` in config
4. Reduce `kafka.window_size_seconds`
5. For large loads: use `job_type=initial_data` (batch mode, 50 workers)

### Schema Mismatch (ClassCastException)

**Symptoms:** `ClassCastException: String cannot be cast to Long` in IcebergIO.

**Root cause:** Iceberg metadata doesn't match pipeline output. Usually from:
- Using `create_table` instead of `register_table` (field IDs mismatch)
- Manual metadata creation with wrong types

**Solutions:**
1. Verify JSON schema definitions match code models
2. Ensure partition field type matches (INT64 for Iceberg)
3. Re-run deploy.py with `register_table`
4. If data is corrupt: delete metadata + re-run deploy.py

### Kafka Consumer Lag

**Symptoms:** Growing backlog, data arriving late in BQ.

**Solutions:**
1. Increase `--max-workers`
2. Check Dataflow step metrics for bottleneck DoFns
3. Verify network connectivity (Dataflow workers → Kafka via Shared VPC)
4. Check Kafka topic throughput (producer flooding?)

### BigQuery Write Failures

**Symptoms:** Data in Iceberg but not in BQ refined tables.

**Solutions:**
1. Check BQ Storage Write API errors in Dataflow logs
2. Verify `Timestamp` usage (MUST use `apache_beam.utils.timestamp.Timestamp`, NOT `datetime.datetime`)
3. Check Bangkok timezone offset (+7h) on all timestamps
4. Verify BQ table schema matches pipeline output schema
5. For CDC: ensure `PRIMARY KEY ... NOT ENFORCED` exists on target table

### Pipeline Fails to Start

**Symptoms:** Job stays QUEUED or goes to FAILED immediately.

| Cause | Fix |
|-------|-----|
| Quota exceeded | Request GCP quota increase |
| Invalid image | Verify GAR image exists (check digest) |
| Permission denied | Check SA has required IAM roles |
| Network error | Verify Shared VPC subnet accessible |
| Invalid config | Check base64-encoded config decodes correctly |

### Stale Iceberg Entries (BLMS)

**Symptoms:** IcebergIO fails with "stale entry" or "table not found" from BLMS.

**Solutions:**
1. Re-register table: `python3 deploy.py "<project>" "<env>" --table=<name>`
2. Delete stale metadata: `gsutil -m rm -r "gs://<bucket>/<table>/metadata/"` then re-run deploy.py

---

## 2. Pipeline Operations

### Redeploying a Streaming Pipeline

```
1. Push code / trigger GitLab CI
2. CI builds + tests + creates image
3. CI finds running Dataflow job
4. CI drains/cancels existing job
5. CI launches new Flex Template
6. New job resumes from last committed Kafka offset
```

### Manually Managing Dataflow Jobs

```bash
# List running jobs
gcloud dataflow jobs list \
  --project "the1-loyalty-data-<env>" \
  --region "asia-southeast1" \
  --filter="name=members-collector AND state=Running"

# Drain (graceful — processes in-flight, 10 min timeout)
gcloud dataflow jobs drain <JOB_ID> \
  --project "the1-loyalty-data-<env>" \
  --region "asia-southeast1"

# Cancel (immediate — drops in-flight messages)
gcloud dataflow jobs cancel <JOB_ID> \
  --project "the1-loyalty-data-<env>" \
  --region "asia-southeast1"
```

### Running Initial Data Load

```bash
# Via GitLab CI (recommended):
# Set pipeline variables:
#   TRIGGER_INIT_DATA_LOAD = 1
#   SERVICE_NAME = members-collector
# Trigger pipeline manually

# What happens:
# - job_type=initial_data (batch mode)
# - MAX_WORKERS=50
# - Machine type: n1-highmem-4
# - Job name: members-collector-init-YYYYMMDD-HHMMSS
# - Self-terminating

# After init load completes:
# Run normal streaming deploy (unset TRIGGER_INIT_DATA_LOAD)
```

### Recovering from Failed Table Deployment

```bash
# 1. Check current state
bq show --project_id="the1-loyalty-data-<env>" "refined.<table>"
gsutil ls "gs://<bucket>/<table>/metadata/"

# 2. Re-run deploy.py (idempotent — uses CREATE IF NOT EXISTS)
cd infrastructure/<collector>/schemas
python3 deploy.py "the1-loyalty-data-<env>" "<env>"

# 3. Force recreate specific table
python3 deploy.py "the1-loyalty-data-<env>" "<env>" --table=<table_name> --force
```

---

## 3. Monitoring

### Cloud Logging Filters

```
# All logs from a specific job
resource.type="dataflow_step"
resource.labels.job_id="<JOB_ID>"

# Error logs only
resource.type="dataflow_step"
severity>=ERROR

# Pipeline-specific logs
resource.type="dataflow_step"
jsonPayload.message=~"members-collector"
```

### Dataflow Console Metrics

| Metric | What to Watch |
|--------|---------------|
| Throughput | Elements/sec (should be non-zero for streaming) |
| Backlog | Kafka consumer lag (should stay low) |
| System lag | Event creation → processing time |
| Workers | Current vs max-workers |
| Errors | Error count and messages |

### Data Freshness Queries

```sql
-- Latest data in refined layer
SELECT MAX(ingestedTHDate) as latest_load
FROM `the1-loyalty-data-{env}.refined.member_tier`;

-- Row counts per partition
SELECT ingestedTHDate, COUNT(*) as row_count
FROM `the1-loyalty-data-{env}.refined.member_tier`
GROUP BY ingestedTHDate
ORDER BY ingestedTHDate DESC
LIMIT 10;

-- Check etlLoadTime for tier events
SELECT DISTINCT etlLoadTime
FROM `the1-loyalty-data-{env}.refined.tier_events_upgraded`
ORDER BY etlLoadTime DESC
LIMIT 5;
```

### Alert Policies

| Alert | Condition | Threshold |
|-------|-----------|-----------|
| Dataflow job failure | Job state = FAILED | Immediate |
| Kafka consumer lag | Backlog > threshold | 5 minutes |
| No data written | Partition stale | 2h (streaming), 26h (batch) |
| Worker OOM | OOM in logs | Immediate |
| Pipeline error rate | Error rate > threshold | 5 minutes |

---

## 4. Configuration Management

### YAML Merge Pattern

```
base.yaml (shared defaults)
  + stg.yaml (STG overrides)
  + prod.yaml (PROD overrides)
  = merged → base64 → --dataflow_config parameter
```

### Environment-Specific Overrides

| Setting | base.yaml | stg.yaml | prod.yaml |
|---------|-----------|----------|-----------|
| Kafka brokers | (none) | STG brokers | PROD brokers |
| GCS bucket | (none) | STG bucket | PROD bucket |
| BQ project | (none) | `*-stg` | `*-prod` |
| Write mode | `append` | (inherit) | `cdc` (member_tier) |
| Log level | `ERROR` | (inherit) | (inherit) |
| Max workers | (none) | 1 | 1-2 |

### Configuration Change Procedure

1. Edit YAML in collector's `config/` directory
2. Commit and push → triggers GitLab CI
3. CI merges configs, base64-encodes, passes to Dataflow
4. Streaming: old job drained/cancelled → new job launched
5. Batch: next scheduled run uses updated config

---

## 5. Collector Quick Reference

| Collector | Type | Trigger | Max Workers (PROD) |
|-----------|------|---------|-------------------|
| members-collector | Streaming | Kafka events | 1 |
| tiers-collector | Batch | 1 AM BKK daily | 1 |
| members-tiers-history | Batch | 1 AM BKK daily | 1 |
| purchases-collector | Streaming | Kafka events | 2 |

---

## 6. DO / DON'T

| DO | DON'T |
|----|-------|
| Use `drain` for streaming jobs before redeploying | Use `cancel` (loses in-flight messages) |
| Check Dataflow logs before escalating | Assume pipeline is broken |
| Use `register_table` in deploy.py | Use `create_table` (breaks field IDs) |
| Verify Bangkok timezone on all timestamps | Assume UTC |
| Use `TRIGGER_INIT_DATA_LOAD=1` for large loads | Run init load as streaming job |
| Check network/IAM first for startup failures | Retry without investigating |
