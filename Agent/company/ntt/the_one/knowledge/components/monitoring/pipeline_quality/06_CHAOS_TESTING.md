# 06 - Chaos Testing / Fault Injection

> ทำให้พังตั้งใจ → ดูว่า monitoring detect ได้ไหม

## STG ONLY — ห้ามทำใน PROD

## Scenario 1: SDK Harness Crash (gRPC Ping Timeout)

**Inject**:
```python
class SlowDoFn(beam.DoFn):
    def process(self, element):
        import time
        time.sleep(120)  # exceeds gRPC ping timeout (~60s)
        yield element
```

**Expected alerts**:
- Log-based metric: SDK harness crash count > 0
- Cloud Monitoring: system_lag > 300s
- Cloud Monitoring: workers at max (autoscaler keeps replacing crashed workers)

**Verify**: Alert fires within 5 minutes? Correct notification channel? Actionable content?

## Scenario 2: Watermark Stall

**Inject**: Pause Pub/Sub subscription (stop delivering messages)
```bash
# STG only
gcloud pubsub subscriptions update SUBSCRIPTION_NAME \
    --push-no-wrapper  # or detach temporarily
```

**Expected alerts**:
- data_watermark_age > threshold
- Backlog increasing

## Scenario 3: CDC Write Failure

**Inject**: Change BQ table schema to break CDC
```sql
-- STG only: rename required column
ALTER TABLE `stg.insight.ms_personas` RENAME COLUMN memberId TO memberId_old;
```

**Expected alerts**:
- Log-based metric: CDC failed rows > 0
- DLQ record count increasing
- LogFailedCDCRows throughput > 0

**Cleanup**: Rename column back

## Scenario 4: S3/GCS Write Failure

**Inject**: Revoke GCS write permission
```bash
# STG only
gcloud projects remove-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:SA@PROJECT.iam.gserviceaccount.com" \
    --role="roles/storage.objectCreator"
```

**Expected alerts**:
- system_lag spike
- Export step error logs

**Cleanup**: Re-grant permission immediately after test

## Scenario 5: API Endpoint Down

**Inject**: Point API base URL to `https://httpstat.us/503` in STG config

**Expected alerts**:
- API error rate log-based metric
- DLQ records from FetchDoFns

## Chaos Test Checklist

```
PRE-TEST:
[ ] STG environment ONLY
[ ] All monitoring/alerts configured and verified
[ ] Team notified of test window
[ ] Rollback plan documented and tested

DURING TEST:
[ ] Record exact timestamp of fault injection
[ ] Wait for alert (record latency)
[ ] Verify correct notification channel received alert
[ ] Verify alert content is actionable
[ ] Screenshot dashboard state

POST-TEST:
[ ] Remove fault / rollback
[ ] Verify pipeline recovers automatically
[ ] Verify alert auto-resolves when issue clears
[ ] Document results:
    - Alert latency: _____ seconds
    - False positives: _____
    - Gaps found: _____
    - Action items: _____
```

## Pros / Cons

| Pros | Cons |
|------|------|
| Proves monitoring actually works | Risk of accidental prod impact |
| Finds gaps before real incidents | Time-consuming to set up |
| Builds team confidence | No native GCP chaos tool for Dataflow |
| Creates runbooks | |

## Effort

2-3 days for all 5 scenarios including documentation
