# Cloud Run & Cloud Scheduler Patterns

## Cloud Run for Batch Data Pipelines

### Cloud Run Jobs vs Services

| Feature | Cloud Run Jobs | Cloud Run Services |
|---------|---------------|-------------------|
| Trigger | Manual, Scheduler, Workflows | HTTP request |
| Execution | Run-to-completion | Request-response |
| Max duration | 168 hours (7 days) | 60 minutes (default), up to 1 hour |
| Scale-to-zero | Always (no cost when idle) | Yes, with cold start |
| Parallelism | Configurable task count | Auto-scaled by request concurrency |
| Use case | Batch ETL, data loading, backfills | API endpoints, webhooks, streaming triggers |

### Cloud Run vs Dataflow for Batch

| Aspect | Cloud Run | Dataflow |
|--------|-----------|----------|
| Cost at idle | Zero | Minimum 1 worker (streaming) / Zero (batch) |
| Startup time | Seconds | 3-7 minutes (Flex Template) |
| Auto-parallelism | Manual (task count) | Automatic (autoscaling) |
| Shuffle/state | None (stateless) | Service-based shuffle, state API |
| Max data volume | GB scale | TB scale |
| Beam integration | No (custom code) | Native |
| Monitoring | Basic logs/metrics | Dataflow UI, job metrics, insights |

**Choose Cloud Run when:**
- Simple API-to-BQ or file-processing pipelines (no complex transforms).
- Startup latency matters (seconds vs minutes).
- Cost sensitivity for small/medium datasets (< 10 GB).
- No need for Beam's windowing, state, or shuffle.

**Choose Dataflow when:**
- Complex transformations, joins, or aggregations.
- Large data volumes requiring distributed processing.
- Streaming pipelines with windowing and exactly-once.
- Need for Beam's IcebergIO, BigQueryIO, or KafkaIO.

### Cloud Run Job Architecture for Data Pipelines
```
Cloud Scheduler (cron)
    |
    v
Cloud Run Job (batch)
    |
    ├── Task 0: Process partition 2025-01-01
    ├── Task 1: Process partition 2025-01-02
    ├── Task 2: Process partition 2025-01-03
    └── ...
    |
    v
BigQuery / GCS / Iceberg
```

## Cloud Scheduler Integration Patterns

### Pattern 1: Direct Cloud Run Job Execution
```bash
# Create a Cloud Scheduler job that triggers a Cloud Run job
gcloud scheduler jobs create http tiers-collector-daily \
    --location=asia-southeast1 \
    --schedule="0 18 * * *" \
    --time-zone="UTC" \
    --uri="https://asia-southeast1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/my-project/jobs/tiers-collector:run" \
    --http-method=POST \
    --oauth-service-account-email=sa-scheduler@my-project.iam.gserviceaccount.com
```

### Pattern 2: Cloud Run Service as Trigger
```bash
# Scheduler -> Cloud Run Service -> Launches Dataflow Job
gcloud scheduler jobs create http launch-members-batch \
    --location=asia-southeast1 \
    --schedule="0 18 * * *" \
    --time-zone="UTC" \
    --uri="https://my-service-abc-as.a.run.app/trigger-pipeline" \
    --http-method=POST \
    --body='{"job_type": "initial_data", "date": "yesterday"}' \
    --oidc-service-account-email=sa-scheduler@my-project.iam.gserviceaccount.com \
    --oidc-token-audience="https://my-service-abc-as.a.run.app" \
    --attempt-deadline=320s
```

### Pattern 3: Scheduler -> Pub/Sub -> Cloud Run
For decoupled, retryable execution:
```
Scheduler --publish--> Pub/Sub Topic --push subscription--> Cloud Run Service
```
Benefits: Pub/Sub handles retries, dead-lettering, and message persistence independent of scheduler.

### Authentication Setup

**OIDC Token (for Cloud Run Services):**
```bash
# 1. Create service account
gcloud iam service-accounts create sa-scheduler \
    --display-name="Cloud Scheduler SA"

# 2. Grant invoker role
gcloud run services add-iam-policy-binding my-service \
    --member=serviceAccount:sa-scheduler@my-project.iam.gserviceaccount.com \
    --role=roles/run.invoker

# 3. Create scheduler with OIDC token
gcloud scheduler jobs create http my-job \
    --oidc-service-account-email=sa-scheduler@my-project.iam.gserviceaccount.com \
    --oidc-token-audience="https://my-service-url"
```

**OAuth Token (for Google APIs like Cloud Run Jobs API):**
```bash
gcloud scheduler jobs create http my-job \
    --oauth-service-account-email=sa-scheduler@my-project.iam.gserviceaccount.com
```

### Cron Schedule Examples
```
0 18 * * *       # 6 PM UTC daily (1 AM BKK = UTC+7)
0 18 * * 1-5     # Weekdays only
*/15 * * * *     # Every 15 minutes
0 0 1 * *        # First day of each month at midnight
0 18 * * * 2025  # Specific year
```

### Retry Configuration
```bash
gcloud scheduler jobs create http my-job \
    --attempt-deadline=600s \    # Max time per attempt
    --retry-config-max-retry-duration=3600s \  # Total retry window
    --retry-config-min-backoff-duration=30s \
    --retry-config-max-backoff-duration=600s \
    --retry-config-max-doublings=5 \
    --retry-config-retry-count=3
```

### Terraform Example
```hcl
resource "google_cloud_scheduler_job" "tiers_collector" {
  name             = "tiers-collector-daily"
  region           = "asia-southeast1"
  schedule         = "0 18 * * *"  # 1 AM BKK
  time_zone        = "UTC"
  attempt_deadline = "600s"

  retry_config {
    retry_count          = 3
    min_backoff_duration = "30s"
    max_backoff_duration = "600s"
    max_doublings        = 3
  }

  http_target {
    http_method = "POST"
    uri         = "https://${google_cloud_run_v2_service.tiers.uri}/run"

    oidc_token {
      service_account_email = google_service_account.scheduler.email
      audience              = google_cloud_run_v2_service.tiers.uri
    }
  }
}
```

## Scale-to-Zero Cost Optimization

### How Scale-to-Zero Works
- Cloud Run services scale to zero instances when no traffic arrives.
- Cloud Run jobs have zero cost between executions.
- No minimum instance charge (unlike Dataflow streaming which maintains at least 1 worker).

### Cost Comparison (Daily Batch Pipeline)

| Component | Cloud Run Job | Dataflow Batch |
|-----------|--------------|----------------|
| Compute | Pay only during execution | Pay during execution + startup overhead |
| Startup | ~1-3 seconds | ~3-7 minutes (Flex Template) |
| Idle cost | $0 | $0 (batch) |
| Minimum billing | 100ms per task | 10 min per worker |

### Optimization Strategies
1. **Keep container images small.** Smaller images = faster cold starts. Use multi-stage Docker builds.
2. **Set minimum instances = 0** (default for jobs, configurable for services).
3. **Pre-warm with minimum instances = 1** only for latency-sensitive services (adds ongoing cost).
4. **Use generation 2 execution environment** for faster startup and better CPU performance.
5. **Avoid large dependency installations at startup.** Bake all dependencies into the container image.

## Health Checks and Graceful Shutdown

### Startup Health Check (Services)
```yaml
# Cloud Run service.yaml
spec:
  template:
    spec:
      containers:
        - image: my-image
          startupProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 0
            periodSeconds: 10
            timeoutSeconds: 1
            failureThreshold: 3
```

### Liveness Health Check (Jobs)
```yaml
# Cloud Run job with health check
spec:
  template:
    spec:
      containers:
        - image: my-image
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            periodSeconds: 30
            timeoutSeconds: 1
```
Timeout cannot exceed `periodSeconds`. Default timeout is 1 second.

### Graceful Shutdown
Cloud Run sends `SIGTERM` before terminating a container. Handle it to flush buffers and close connections.

```python
import signal
import sys

def handle_sigterm(signum, frame):
    print("SIGTERM received, flushing buffers...")
    flush_pending_writes()
    close_connections()
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)
```

**Termination grace period:**
- Services: 10 seconds after SIGTERM (configurable up to 3600s).
- Jobs: Configurable via task timeout.

## Concurrency and Timeout Settings

### Cloud Run Jobs
```bash
gcloud run jobs create my-batch-job \
    --image=my-image \
    --tasks=10 \                    # Total tasks to run
    --max-retries=3 \               # Retries per failed task
    --parallelism=5 \               # Max concurrent tasks
    --task-timeout=3600s \          # 1 hour per task (max 168h)
    --memory=2Gi \
    --cpu=2
```

### Cloud Run Services
```bash
gcloud run deploy my-service \
    --image=my-image \
    --concurrency=80 \              # Requests per instance (default: 80)
    --max-instances=100 \
    --min-instances=0 \             # Scale to zero
    --timeout=300s \                # Request timeout (max 3600s)
    --memory=2Gi \
    --cpu=2
```

### Concurrency Guidelines
- **CPU-bound tasks:** Set `concurrency=1` to avoid contention.
- **I/O-bound tasks:** Higher concurrency (10-80) is efficient.
- **Data pipeline triggers:** `concurrency=1` to prevent overlapping pipeline launches.
- **Batch jobs:** Set `parallelism` based on downstream resource limits (e.g., API rate limits, BQ quota).

### Timeout Strategy
- Set task timeout to 2x expected execution time for safety margin.
- For long-running batch jobs, use Cloud Run Jobs (up to 7 days) instead of Services (max 1 hour).
- Set Cloud Scheduler `attempt-deadline` to slightly more than expected Cloud Run execution time.

## VPC Connector Patterns

### Direct VPC Egress (Recommended)
No connector needed. Cloud Run connects directly to VPC resources.

```bash
gcloud run jobs update my-job \
    --network=my-vpc \
    --subnet=my-subnet \
    --vpc-egress=private-ranges-only  # Only VPC traffic goes through VPC
```

### Subnet Sizing
- Each Cloud Run task consumes 1 IP for execution duration + 7 minutes after completion.
- Minimum: `/26` subnet (62 usable IPs).
- For 50 concurrent tasks: `/25` subnet (126 usable IPs) to handle overlap.
- Formula: `subnet_size >= max_concurrent_tasks * 1.5` (for IP reuse overlap).

### VPC Egress Modes
- **`private-ranges-only` (recommended):** Only RFC 1918 traffic routes through VPC. Internet traffic goes directly.
- **`all-traffic`:** All egress routes through VPC. Required for Cloud NAT or firewall rules on all traffic.

### Common VPC Use Cases for Data Pipelines
1. **Access private Kafka cluster** in VPC.
2. **Access Cloud SQL** via private IP.
3. **Access internal APIs** behind Internal Load Balancer.
4. **Enforce firewall rules** on outbound traffic.

### Terraform VPC Configuration
```hcl
resource "google_cloud_run_v2_job" "batch_pipeline" {
  name     = "my-batch-job"
  location = "asia-southeast1"

  template {
    template {
      containers {
        image = "asia-southeast1-docker.pkg.dev/my-project/my-repo/my-image:v1"
        resources {
          limits = {
            cpu    = "2"
            memory = "2Gi"
          }
        }
      }
      vpc_access {
        network_interfaces {
          network    = "my-vpc"
          subnetwork = "my-subnet"
        }
        egress = "PRIVATE_RANGES_ONLY"
      }
      timeout = "3600s"
    }
    task_count  = 1
    parallelism = 1
  }
}
```

---

*Sources: [Cloud Run Services](https://cloud.google.com/run), [Cloud Run Instance Autoscaling](https://cloud.google.com/run/docs/about-instance-autoscaling), [Triggering with Scheduler](https://docs.cloud.google.com/run/docs/triggering/using-scheduler), [Task Timeout](https://docs.cloud.google.com/run/docs/configuring/task-timeout), [Concurrency](https://docs.cloud.google.com/run/docs/about-concurrency), [Health Checks](https://docs.cloud.google.com/run/docs/configuring/healthchecks), [Direct VPC](https://docs.cloud.google.com/run/docs/configuring/vpc-direct-vpc), [Cloud Scheduler](https://docs.cloud.google.com/scheduler/docs)*
