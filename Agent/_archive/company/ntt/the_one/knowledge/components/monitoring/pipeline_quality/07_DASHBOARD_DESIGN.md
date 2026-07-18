# 07 - Dashboard Design

> What to visualize and how to organize dashboards

## Dashboard Hierarchy

```
Level 1: Overview (all pipelines at a glance)
  → Job status scorecards, system lag, error rate

Level 2: Per-Pipeline (deep dive)
  → customer-profile: lag, watermark, throughput, workers
  → loyalty collectors: last run, duration, element count

Level 3: Infrastructure
  → Worker count, vCPU, memory, GCS usage, BQ slots
```

## Overview Dashboard — Key Widgets

### Scorecards (top row)
- Pipeline status: GREEN (running, lag < 5min) / RED (crashed or lag > 10min)
- Current system lag
- Current watermark age
- Active worker count

### Time-series Charts
1. **System lag + watermark age** (dual Y-axis) with threshold lines (300s, 600s)
2. **Throughput** (elements/sec) per pipeline
3. **Worker count** over time with autoscaling events
4. **Error rate** (log-based metrics: SDK crash, CDC failures)

### Error Panel
- Recent ERROR logs (embedded Logs Panel widget)
- DLQ record count trend

## Streaming Dashboard (customer-profile)

| Widget | Metric | Purpose |
|--------|--------|---------|
| System lag gauge | `system_lag` | Is pipeline keeping up? |
| Watermark age | `data_watermark_age` | How fresh is data? |
| Throughput | `element_count` rate | Processing speed |
| Backlog | `per_stage/backlog_bytes` | How much is queued? |
| Worker count | `current_num_workers` | Autoscaling behavior |
| CDC failed rows | Log-based metric | Write errors |
| SDK crash count | Log-based metric | Worker crashes |
| Pub/Sub backlog | `pubsub.googleapis.com/subscription/num_undelivered_messages` | Source backlog |

## Batch Dashboard (tiers, m-t-h)

| Widget | Metric | Purpose |
|--------|--------|---------|
| Last run status | Job state scorecard | Did it succeed? |
| Duration trend | `elapsed_time` per run | Getting slower? |
| Elements processed | `element_count` per run | Expected volume? |
| BQ table freshness | Custom query | Latest partition date |

## Terraform

```hcl
resource "google_monitoring_dashboard" "pipeline_overview" {
  dashboard_json = file("${path.module}/dashboards/pipeline_overview.json")
}
```

Dashboard JSON uses `mosaicLayout` with `xyChart`, `scorecard`, `text`, and `logsPanel` widgets.

## Key Design Principles

1. **Glanceable**: Overview shows health in < 5 seconds
2. **Drillable**: Click pipeline → deep dive dashboard
3. **Actionable**: Every widget links to relevant log filter
4. **Threshold lines**: Visual boundary between normal and abnormal
5. **Time range**: Default 6 hours, with 1hr/1day/1week options

## Effort

1-2 days per dashboard, 3-4 days total for all 3 levels
