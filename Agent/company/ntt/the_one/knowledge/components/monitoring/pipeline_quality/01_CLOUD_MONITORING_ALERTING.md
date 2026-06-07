# 01 - Cloud Monitoring + Alerting (GCP Native)

> Real-time alerting on Dataflow metrics — would have caught SDK crash within 5 minutes

## Key Dataflow Metrics

| Metric | Type | Description | Pipeline |
|--------|------|-------------|----------|
| `system_lag` | GAUGE (sec) | Max duration item awaiting processing | Streaming |
| `data_watermark_age` | GAUGE (sec) | Age of most recent fully-processed item | Streaming |
| `current_num_workers` | GAUGE | Current worker count | Both |
| `is_active` | GAUGE | 1 if running | Both |
| `failed` | GAUGE | 1 if failed | Both |
| `per_stage/backlog_bytes` | GAUGE | Unprocessed bytes | Streaming |

> **MQL is deprecated (July 2025).** Use PromQL or `condition_threshold`.

## Alert 1: System Lag > 5 Minutes (would catch SDK crash)

```hcl
resource "google_monitoring_alert_policy" "dataflow_system_lag" {
  display_name = "Dataflow System Lag > 300s"
  combiner     = "OR"

  conditions {
    display_name = "System lag exceeds 5 minutes"
    condition_threshold {
      filter          = <<-EOT
        resource.type = "dataflow_job"
        AND metric.type = "dataflow.googleapis.com/job/system_lag"
      EOT
      comparison      = "COMPARISON_GT"
      threshold_value = 300
      duration        = "300s"
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MAX"
      }
      trigger { count = 1 }
    }
  }

  notification_channels = [google_monitoring_notification_channel.slack.id]

  documentation {
    content   = "System lag exceeded 300s. Check: (1) Worker health, (2) SDK harness logs, (3) Autoscaling"
    mime_type = "text/markdown"
  }
}
```

## Alert 2: Data Watermark Age > 10 Minutes

```hcl
resource "google_monitoring_alert_policy" "dataflow_watermark_age" {
  display_name = "Dataflow Data Freshness > 10min"
  combiner     = "OR"

  conditions {
    display_name = "Data watermark age exceeds 10 minutes"
    condition_threshold {
      filter          = <<-EOT
        resource.type = "dataflow_job"
        AND metric.type = "dataflow.googleapis.com/job/data_watermark_age"
      EOT
      comparison      = "COMPARISON_GT"
      threshold_value = 600
      duration        = "600s"
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MAX"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.slack.id]
}
```

## Alert 3: Job Failed

```hcl
resource "google_monitoring_alert_policy" "dataflow_job_failed" {
  display_name = "Dataflow Job Failed"
  combiner     = "OR"

  conditions {
    display_name = "Job failure detected"
    condition_threshold {
      filter          = <<-EOT
        resource.type = "dataflow_job"
        AND metric.type = "dataflow.googleapis.com/job/failed"
      EOT
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "0s"
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MAX"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.pagerduty.id]
}
```

## Alert 4: Autoscaling at Max Workers

```hcl
resource "google_monitoring_alert_policy" "dataflow_max_workers" {
  display_name = "Dataflow Workers at Max"
  combiner     = "OR"

  conditions {
    display_name = "Worker count at maximum for 10+ min"
    condition_threshold {
      filter          = <<-EOT
        resource.type = "dataflow_job"
        AND metric.type = "dataflow.googleapis.com/job/current_num_vcpus"
      EOT
      comparison      = "COMPARISON_GT"
      threshold_value = 16
      duration        = "600s"
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MAX"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.slack.id]
}
```

## Notification Channels

```hcl
resource "google_monitoring_notification_channel" "slack" {
  display_name = "Pipeline Alerts - Slack"
  type         = "slack"
  labels       = { channel_name = "#pipeline-alerts" }
  sensitive_labels { auth_token = var.slack_auth_token }
}

resource "google_monitoring_notification_channel" "email" {
  display_name = "Pipeline Alerts - Email"
  type         = "email"
  labels       = { email_address = "data-team@company.com" }
}
```

## Pros / Cons

| Pros | Cons |
|------|------|
| Native GCP — no setup | Cannot monitor external systems (Kafka) |
| Real-time (1-5 min) | Limited expression vs custom code |
| Terraform-manageable | Free tier limited (500 MB metrics) |
| Free for basic alerts | |

## Applicability

| Pipeline Type | Applicable | Key Metrics |
|--------------|:--:|------------|
| Dataflow Streaming | PRIMARY | system_lag, watermark_age, backlog |
| Dataflow Batch | YES | failed, elapsed_time, element_count |
| Cloud Run Batch | Partial | Via `run.googleapis.com/` metrics |
| Dataform | NO | Use log-based metrics instead |

## References

- https://cloud.google.com/dataflow/docs/guides/using-cloud-monitoring
- https://cloud.google.com/monitoring/alerts/terraform
- https://docs.cloud.google.com/monitoring/promql/promql-in-alerting
