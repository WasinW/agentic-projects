# Operations Reference — Observability & Cost Patterns

> Cross-cloud comparison of observability, monitoring, and cost optimization.

## Observability Comparison

| Feature | **GCP** | **AWS** | **Azure** | **Databricks** |
|---------|---------|---------|-----------|---------------|
| Logging | Cloud Logging | CloudWatch Logs | Monitor Logs | Spark UI logs |
| Metrics | Cloud Monitoring | CloudWatch Metrics | Monitor Metrics | Ganglia, custom |
| Tracing | Cloud Trace | X-Ray | App Insights | OpenTelemetry |
| Dashboards | Cloud Monitoring, Looker | CloudWatch Dashboards | Azure Dashboards | Databricks SQL |
| Alerting | Cloud Monitoring policies | CloudWatch Alarms | Monitor Alerts | SQL alerts |
| Log export | Log sinks → BQ/GCS | Firehose → S3 | Diagnostic settings | Delta table export |

## Cost Optimization Strategies

| Strategy | GCP (Dataflow) | AWS (Glue/EMR) | Databricks |
|----------|---------------|----------------|------------|
| **Right-sizing** | `--max-workers`, machine type | Glue DPU, EMR instance type | Cluster size, Photon |
| **Spot/preemptible** | FlexRS (preemptible VMs) | Spot instances | Spot instances |
| **Auto-scaling** | `THROUGHPUT_BASED` | Glue auto-scaling | Autoscale clusters |
| **Reserved capacity** | Flex Slots (BQ) | Reserved instances | Committed DBUs |
| **Storage tiering** | Nearline/Coldline (GCS) | S3 Intelligent-Tiering | Azure Cool/Archive |
| **Query optimization** | Partitioning + clustering | Iceberg partitioning | Z-ORDER, OPTIMIZE |

## Dataflow Cost Factors

| Factor | Impact | Optimization |
|--------|--------|-------------|
| Worker count | Linear cost increase | Use `--max-workers=1` for low-volume |
| Machine type | 2-4x cost difference | `n1-standard-2` for streaming, `n1-highmem-4` for init |
| Streaming vs batch | Streaming = continuous cost | Batch when real-time not needed |
| Shuffle mode | Network cost | Use `SHUFFLE_MODE_SERVICE` |
| Region | Price varies by region | `asia-southeast1` (our region) |

## Detailed Reference

For comprehensive cost comparisons, see:
- `archive/knowledge_base/COMPARISON/CROSS_CLOUD_COMPARISON.md` (Section 11: Pricing)
