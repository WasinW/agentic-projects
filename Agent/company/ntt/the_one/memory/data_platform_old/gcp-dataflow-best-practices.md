# GCP Dataflow Best Practices

## Streaming vs Batch Trade-offs

| Aspect | Streaming | Batch |
|--------|-----------|-------|
| Latency | Sub-second to minutes | Minutes to hours |
| Cost model | Resource-based (Streaming Engine CUs) | Per-job (FlexRS discounts available) |
| Autoscaling | Continuous, tunable via utilization hint | Default on, disable for short jobs |
| Error handling | Retries indefinitely (risk of stuck pipeline) | 4 retries then fail |
| State | Persistent per-key state in Streaming Engine | Shuffle-based, ephemeral |
| Update model | In-place update or drain | Re-run from scratch |

**When to choose streaming:** Real-time CDC, event-driven triggers, SLA < 5 minutes.
**When to choose batch:** Daily/hourly aggregations, backfills, cost-sensitive workloads.

**At-least-once mode:** If your pipeline tolerates duplicates (e.g., writing to an idempotent sink like BigQuery CDC with primary keys), enable at-least-once mode for streaming. This significantly reduces cost compared to exactly-once mode by avoiding the overhead of deduplication checkpointing.

## Autoscaling Best Practices

### Horizontal Autoscaling
- Set `numWorkers` for initial worker count to avoid cold-start redistribution overhead.
- Set `maxNumWorkers` to cap cost. For streaming, a good starting point is 2-3x your steady-state worker count.
- Tune the **autoscaling utilization hint** (0.0-1.0): higher values (e.g., 0.8) favor cost savings; lower values (e.g., 0.4) favor low latency.
- For streaming with Streaming Engine, autoscaling settings can be updated in-flight without stopping the job.
- Disable autoscaling for short-running batch jobs (< 10 minutes) where scaling overhead exceeds benefit.

### Vertical Autoscaling (Dataflow Prime)
- Dynamically scales worker memory from 6-16 GiB (standard) or 12-26 GiB (GPU).
- **Streaming:** Enabled by default with Dataflow Prime. Continuously adjusts memory.
- **Batch:** Disabled by default. Scales up only after 4 OOM errors. Enable with:
  ```
  --experiments=enable_batch_vmr
  --experiments=enable_vertical_memory_autoscaling
  ```
- Only memory scales vertically; CPU count remains fixed.
- Horizontal autoscaling pauses for 10 minutes during/after vertical scaling events.

### Machine Type Selection
- Start with `n1-standard-2` or `n2-standard-2` for general workloads.
- Use `n2-highmem-*` for memory-intensive transforms (large GroupByKey, side inputs).
- Use `n2-highcpu-*` for CPU-bound transforms (serialization, compression).
- Avoid oversized machines -- right-size based on experiment results.

## Streaming Pipeline Design Patterns

### Windowing Strategy
- **Fixed windows:** Use for regular aggregation intervals (e.g., 1-minute metrics).
- **Session windows:** Use for user-activity grouping with gap duration.
- **Sliding windows:** Use for moving averages (e.g., 5-min window, 1-min slide). Note: elements are duplicated across overlapping windows.
- **Global window + triggers:** Use for streaming pipelines that write per-element without aggregation.

### Triggers and Watermarks
- Default trigger fires at watermark (end of window). Add early firings for partial results:
  ```python
  AfterWatermark(early=AfterProcessingTime(delay=60))
  ```
- Set `allowed_lateness` to handle late data without dropping it.
- Use `AccumulationMode.ACCUMULATING` when downstream consumers can handle retractions; `DISCARDING` when each pane is independent.

### Watermark Management
- Watermark advances based on the oldest unprocessed element. A single stuck element blocks the entire watermark.
- Monitor watermark lag in Dataflow UI. Sustained lag > 5 minutes indicates a processing bottleneck.
- For Kafka sources, watermark is driven by consumer offset progress.

## Memory Management and OOM Prevention

1. **Run small experiments first.** If a test job uses nearly all available memory, expect OOM at scale.
2. **Enable Vertical Autoscaling** (Dataflow Prime) for automatic memory adjustment.
3. **Avoid per-element logging.** Use sampling or counters instead. Excessive logging causes memory pressure from log buffers.
4. **Limit side input size.** Side inputs are loaded into memory on each worker. For large lookups, use `ReadFromBigQuery` as a side input with `AsDict` pattern, or split into multiple smaller side inputs.
5. **Control GroupByKey fanout.** Hot keys cause memory spikes. Use `CombinePerKey` where possible, or add a `Reshuffle` before heavy transforms.
6. **Set timeouts for expensive DoFns.** One slow element can block a bundle and accumulate memory.
7. **Pre-package dependencies** in custom containers to avoid runtime pip installs that consume memory.

## Shuffle Modes

### Service-based Shuffle (Recommended for Batch)
- Offloads shuffle to Google-managed infrastructure.
- Reduces worker disk and memory requirements.
- Enabled by default for batch pipelines.
- Eliminates need for large persistent disks on workers.

### Streaming Engine (Recommended for Streaming)
- Moves streaming state and shuffle to Google backend.
- Reduces worker resource consumption by up to 50%.
- Enables in-flight autoscaling updates.
- Enabled with `--enable_streaming_engine` (default in newer SDK versions).

## Flex Templates Best Practices

1. **Use custom container images** with all dependencies pre-installed. Avoid `FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE` -- it installs at launch time, slowing startup.
2. **Pin image tags** with dates or commit SHAs. Never use `:latest`.
3. **Base image strategy:** Copy Flex Template launcher binary from Google base image onto your custom image:
   ```dockerfile
   FROM my-custom-image:v1.2.3
   COPY --from=gcr.io/dataflow-templates-base/python311-template-launcher-base:latest /opt/google/dataflow/python_template_launcher /opt/google/dataflow/python_template_launcher
   ```
4. **Keep metadata file in source control** alongside pipeline code. Include it in the template spec during CI/CD build.
5. **Store template spec in GCS** with versioned paths: `gs://bucket/templates/v1.2.3/template.json`.
6. **Container spec JSON** should reference Artifact Registry (not Container Registry, which is deprecated).

## Cost Optimization

| Strategy | Savings | Applies to |
|----------|---------|------------|
| FlexRS (Flexible Resource Scheduling) | 40-60% | Non-urgent batch jobs |
| At-least-once streaming mode | 30-50% | Streaming with idempotent sinks |
| Streaming Engine | 20-40% | All streaming jobs |
| Right-sized machine types | 10-30% | All jobs |
| Service-based shuffle | 10-20% | Batch jobs (reduces disk) |
| Committed Use Discounts | 20-40% | Sustained streaming workloads |
| Region co-location | Variable | Cross-region data transfer |

**Additional tips:**
- Set `max_workflow_runtime_walltime_seconds` to kill runaway batch jobs.
- Consolidate small batch jobs into fewer, larger ones. Job startup overhead is fixed.
- Use `numberOfWorkerHarnessThreads` to tune parallelism per worker rather than adding workers.
- Monitor via Dataflow Insights for automatic recommendations.

## Monitoring and Alerting

### Key Metrics to Monitor
- **System lag** (streaming): Time between data event and processing. Alert at > 5 min.
- **Data freshness** (streaming): Time since last element was processed. Alert at > 10 min.
- **Watermark lag**: Oldest unprocessed element age. Alert at sustained > 5 min.
- **Worker CPU utilization**: Target 50-70% for headroom. Alert at > 90% sustained.
- **Worker memory utilization**: Alert at > 85%.
- **Backlog size** (bytes/elements): Growing backlog indicates under-provisioning.
- **Error rate**: Failed elements / total elements. Alert at > 1%.

### Monitoring Setup
- Use Cloud Monitoring dashboards with Dataflow job metrics.
- Set up alerting policies on `system_lag`, `data_freshness`, and `elapsed_time`.
- Enable Dataflow Insights for automated straggler detection and recommendations.
- Export job metrics to BigQuery for historical analysis and capacity planning.
- Use `speculative_execution` (`map_task_backup_mode=ON`) for batch jobs to mitigate stragglers.

---

*Sources: [Dataflow Cost Optimization](https://docs.cloud.google.com/dataflow/docs/optimize-costs), [Horizontal Autoscaling](https://cloud.google.com/dataflow/docs/horizontal-autoscaling), [Tune Autoscaling](https://docs.cloud.google.com/dataflow/docs/guides/tune-horizontal-autoscaling), [Vertical Autoscaling](https://docs.cloud.google.com/dataflow/docs/vertical-autoscaling), [Large Batch Pipelines](https://docs.cloud.google.com/dataflow/docs/guides/large-pipeline-best-practices), [Flex Templates](https://cloud.google.com/blog/topics/developers-practitioners/why-you-should-be-using-flex-templates-your-dataflow-deployments), [Custom Containers](https://docs.cloud.google.com/dataflow/docs/guides/build-container-image)*
