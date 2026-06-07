# 02 - Cloud Logging + Log-based Metrics

> Detect specific errors (SDK crash, OOM, API failures) from worker logs

## Key Log Filters

### SDK Harness Crash (exact issue we experienced)
```
resource.type="dataflow_step"
AND (textPayload=~"SDK harness" OR textPayload=~"harness disconnected"
     OR textPayload=~"gRPC.*timeout" OR textPayload=~"DEADLINE_EXCEEDED")
```

### Worker Unhealthy
```
resource.type="dataflow_step"
AND (textPayload=~"Worker pool.*unhealthy"
     OR textPayload=~"Expected.*SDK Harnesses.*but only")
```

### OOM
```
resource.type="dataflow_step"
AND (textPayload=~"OutOfMemoryError" OR textPayload=~"Memory limit exceeded")
```

### CDC Write Failures
```
resource.type="dataflow_step"
AND textPayload=~"FAILED ROW"
AND severity>=ERROR
```

### Dataform Failure
```
resource.type="dataform.googleapis.com/Repository"
AND jsonPayload.terminalState="FAILED"
```

### Cloud Run Job Failure
```
resource.type="cloud_run_job"
AND severity>=ERROR
```

## Create Log-based Metrics

### gcloud CLI
```bash
# SDK harness crashes
gcloud logging metrics create dataflow_sdk_harness_crash \
  --description="Count of SDK harness crash events" \
  --log-filter='
    resource.type="dataflow_step"
    AND (textPayload=~"SDK harness" OR textPayload=~"harness disconnected")'

# CDC write failures
gcloud logging metrics create dataflow_cdc_failed_rows \
  --description="Count of CDC write failures" \
  --log-filter='
    resource.type="dataflow_step"
    AND textPayload=~"FAILED ROW"
    AND severity>=ERROR'
```

### Terraform
```hcl
resource "google_logging_metric" "sdk_harness_crash" {
  name   = "dataflow_sdk_harness_crash"
  filter = <<-EOT
    resource.type="dataflow_step"
    AND (textPayload=~"SDK harness" OR textPayload=~"harness disconnected")
  EOT
  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    unit         = "1"
  }
}

# Alert on the log-based metric
resource "google_monitoring_alert_policy" "sdk_crash_alert" {
  display_name = "SDK Harness Crash Detected"
  combiner     = "OR"

  conditions {
    display_name = "SDK harness crash count > 0"
    condition_threshold {
      filter          = <<-EOT
        resource.type = "dataflow_step"
        AND metric.type = "logging.googleapis.com/user/dataflow_sdk_harness_crash"
      EOT
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "0s"
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.pagerduty.id]

  documentation {
    content   = "SDK harness crash detected. Likely gRPC ping timeout. Check worker logs."
    mime_type = "text/markdown"
  }
}
```

## Log Router Sink (Archive to BQ for Analysis)

```hcl
resource "google_logging_project_sink" "dataflow_errors_to_bq" {
  name        = "dataflow-errors-to-bigquery"
  destination = "bigquery.googleapis.com/projects/${var.project_id}/datasets/pipeline_logs"
  filter      = "resource.type=\"dataflow_step\" AND severity>=ERROR"
  unique_writer_identity = true
  bigquery_options { use_partitioned_tables = true }
}
```

## Pros / Cons

| Pros | Cons |
|------|------|
| Catches errors built-in metrics miss | Regex-based — can break if log format changes |
| Works for ALL pipeline types | Log ingestion costs can grow |
| No additional infra | 1-5 min delay (not instant) |

## Applicability

| Pipeline Type | Applicable |
|--------------|:--:|
| Dataflow Streaming | YES |
| Dataflow Batch | YES |
| Cloud Run Batch | YES |
| Dataform | YES |
