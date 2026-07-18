# Pipeline Quality Monitoring Solutions

> Date: 2026-03-27 | Context: SDK harness crash (gRPC ping timeout) ทำให้ data loss 7 วัน

## Background

Pipeline `customer-profile-v3-streaming` เจอ SDK harness crash จาก gRPC ping timeout
ไม่มีระบบ monitoring/alerting → ไม่รู้ว่าพังจนข้อมูลหายไป 7 วัน

## Solutions (แยกเป็นไฟล์)

| # | Solution | Detection Speed | Effort | Best For |
|---|----------|:-:|:-:|----------|
| 1 | [Cloud Monitoring + Alerting](01_CLOUD_MONITORING_ALERTING.md) | Real-time (1-5 min) | 2.5 days | Dataflow Streaming/Batch |
| 2 | [Cloud Logging + Log-based Metrics](02_CLOUD_LOGGING_METRICS.md) | 1-5 min | 1-2 days | All pipeline types |
| 3 | [Dead Letter Queue (DLQ)](03_DLQ_PATTERN.md) | Real-time | 3-5 days | Dataflow (Beam) |
| 4 | [ELK vs GCP Native](04_ELK_VS_GCP_NATIVE.md) | N/A (comparison) | - | Decision doc |
| 5 | [Health Check DAGs (Airflow)](05_HEALTH_CHECK_DAGS.md) | 15 min (schedule) | 2-3 days | Cross-system checks |
| 6 | [Chaos Testing](06_CHAOS_TESTING.md) | N/A (validation) | 2-3 days | Verify monitoring works |
| 7 | [Dashboard Design](07_DASHBOARD_DESIGN.md) | Visual | 2-3 days | All |

## Implementation Priority

### Phase 1: Quick Wins (Week 1) — 2.5 days
- Alert: system_lag > 300s
- Alert: data_watermark_age > 600s
- Alert: job failed
- Log-based metric: SDK harness crash
- Notification channel: Slack

### Phase 2: Foundation (Week 2) — 3 days
- Overview dashboard
- Log-based metrics: OOM, API errors
- Log Router sink to BQ
- Alert: autoscaling at max

### Phase 3: DLQ (Week 3-4) — 4 days
- DLQ BQ table
- TaggedOutput in critical DoFns
- DLQ row count alert

### Phase 4: Advanced (Month 2) — 10 days
- Per-pipeline dashboards
- Airflow health check DAG
- Chaos testing (all scenarios)

## Applicability Matrix

| Solution | Dataflow Streaming | Dataflow Batch | Cloud Run Batch | Dataform |
|----------|:--:|:--:|:--:|:--:|
| Cloud Monitoring Alerts | PRIMARY | YES | Partial | NO |
| Log-based Metrics | YES | YES | YES | YES |
| DLQ | YES | YES | Manual | NO |
| Health Check DAGs | YES | YES | YES | YES |
| Chaos Testing | YES | YES | Limited | NO |
| Dashboards | YES | YES | YES | YES |
