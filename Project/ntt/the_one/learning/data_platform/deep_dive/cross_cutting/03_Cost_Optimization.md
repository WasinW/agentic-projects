# Cost Optimization — Deep Dive

> Storage, compute, query, ML/AI cost tactics
> ทำให้ data platform ไม่กลายเป็น cost center

---

## 1. Cost Mental Model

### Layers of Cost

```
1. STORAGE        ($/GB/month)
2. COMPUTE        ($/CPU-hour or $/slot-hour)
3. NETWORK        ($/GB egress, especially cross-region)
4. QUERIES        ($/TB scanned)
5. METADATA       (catalog, lineage tools)
6. PEOPLE         (DE/DS time)
7. OPPORTUNITY    (slow query = lost work time)
```

### The 80/20 of Data Cost

```
ปกติแล้วใน enterprise:
  20% of queries → 80% of cost
  20% of tables → 80% of storage
  20% of pipelines → 80% of compute
  
Strategy: optimize the 20% first, ignore long tail
```

---

## 2. Storage Cost Optimization

### Storage Tier Pricing (cloud, 2026)

| Tier | $/GB/month | Use case |
|---|---|---|
| Hot (S3 Standard, GCS Standard) | $0.020-0.025 | Frequent access |
| Warm (S3 IA, GCS Nearline) | $0.010-0.015 | Monthly access |
| Cold (S3 Glacier, GCS Coldline) | $0.004-0.005 | Yearly access |
| Archive (S3 Deep Archive) | $0.001 | Rarely access |

### Tactic 1: Lifecycle Policies

```python
# GCS lifecycle
{
  "rule": [
    {
      "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
      "condition": {"age": 30}
    },
    {
      "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
      "condition": {"age": 365}
    },
    {
      "action": {"type": "Delete"},
      "condition": {"age": 2555}  # 7 years
    }
  ]
}
```

**Saving**: 70-90% on rarely-accessed data

### Tactic 2: Compression + Format

```
Raw text:                100 GB
JSON:                    100 GB (basically same as text)
Parquet (Snappy):         15 GB  (6.7x compression)
Parquet (ZSTD):           10 GB (10x compression)
Iceberg + Parquet (ZSTD): 10 GB + small metadata
```

```python
# Spark write
df.write.format("parquet") \
    .option("compression", "zstd") \
    .save(path)
```

### Tactic 3: Partition + Cluster

```sql
-- Bad: full scans
CREATE TABLE events (...) PARTITIONED BY (event_date)

-- Better: partition + cluster
CREATE TABLE events (...)
  PARTITIONED BY (event_date)
  CLUSTERED BY (user_id) INTO 100 BUCKETS;

-- Iceberg hidden partitioning
CREATE TABLE events (
    user_id, event_time, ...
) PARTITIONED BY (days(event_time));
-- Auto-skip irrelevant partitions
```

### Tactic 4: Delete What You Don't Need

```sql
-- Find unused tables
SELECT 
    table_name,
    last_query_time,
    storage_size_gb,
    storage_size_gb * 0.02 AS monthly_cost
FROM `region-us`.INFORMATION_SCHEMA.TABLE_USAGE
WHERE last_query_time < TIMESTAMP_SUB(CURRENT_TIMESTAMP, INTERVAL 90 DAY)
ORDER BY storage_size_gb DESC;

-- Found 50 unused tables totaling 5 TB
-- Delete = $100/month savings
```

### Tactic 5: Iceberg Snapshot Cleanup

```sql
-- Iceberg snapshots accumulate
-- Old data still stored even after delete

CALL system.expire_snapshots(
    table => 'warehouse.orders',
    older_than => TIMESTAMP '2026-04-01',  -- 90 days
    retain_last => 5
);

CALL system.remove_orphan_files('warehouse.orders');

-- Can free 30-50% of storage
```

### Tactic 6: Don't Replicate Everything

```
❌ Bad: Bronze + Silver + Gold all kept forever
✅ Good: 
  Bronze: raw, kept 7 days (or per regulation)
  Silver: cleansed, kept 90 days hot, then cold
  Gold: aggregated, kept indefinitely (small)
  
Save 60-80% on Bronze costs
```

---

## 3. Compute Cost Optimization

### Spark / Compute Best Practices

#### Tactic 1: Right-Size Cluster

```
Common over-provisioning:
  Job needs 4 cores, 16 GB
  Cluster: 16 cores, 128 GB (4x oversized)

Auto-scaling:
  Min: 2 workers
  Max: 50 workers
  Scale based on queue depth
```

#### Tactic 2: Spot/Preemptible Instances

```
On-demand: $0.50/hour
Spot:      $0.15/hour (70% off)

Trade-off:
  - Can be reclaimed any time
  - For batch: usually fine (retry)
  - For streaming: risky (use mixed)
```

```python
# Databricks
{
  "min_workers": 2,
  "max_workers": 20,
  "aws_attributes": {
    "availability": "SPOT_WITH_FALLBACK",
    "first_on_demand": 1,  # 1 on-demand for stability
    "spot_bid_price_percent": 100
  }
}
```

#### Tactic 3: Use Larger Machines (sometimes)

```
Counterintuitive but: 
  100 workers × small = lots of communication overhead
  10 workers × large = less overhead, sometimes faster
  
Find sweet spot empirically
```

#### Tactic 4: Cache Smartly

```python
# Bad: cache then ignore
df = expensive_compute()
df.cache()
df.write.save(...)  # use once, never cache benefit

# Good: cache when used multiple times
df = expensive_compute()
df.cache()
result1 = df.filter("...").count()
result2 = df.groupBy("...").agg(...)
df.unpersist()  # release when done
```

#### Tactic 5: Avoid Re-Reading

```python
# Bad: read same file 3 times
df1 = spark.read.parquet(path).filter("a")
df2 = spark.read.parquet(path).filter("b")  # re-read!
df3 = spark.read.parquet(path).filter("c")  # re-read!

# Good: read once
df = spark.read.parquet(path).cache()
df1 = df.filter("a")
df2 = df.filter("b")
df3 = df.filter("c")
```

---

## 4. BigQuery Cost Optimization

### Pricing Models

```
On-Demand: $5/TB scanned
Capacity (slots): $X/slot/month (predictable)
```

### When On-Demand
- Low/variable usage
- < 1TB/day scans
- Different query patterns

### When Capacity
- Predictable load
- > 5TB/day scans
- Need to control max spend

### Tactic 1: Partition + Cluster

```sql
CREATE TABLE events
PARTITION BY DATE(event_time)
CLUSTER BY user_id, country
AS SELECT * FROM source_data;

-- Query: scans 1 partition + cluster pruning
SELECT * FROM events
WHERE DATE(event_time) = '2026-05-01'
  AND user_id IN ('123', '456');
-- Scans: ~10 MB instead of 1 TB
-- Cost: $0.0001 instead of $5
```

### Tactic 2: Materialized Views

```sql
-- Frequent expensive query
CREATE MATERIALIZED VIEW hourly_revenue AS
SELECT 
    DATE_TRUNC(event_time, HOUR) AS hour,
    SUM(amount) AS revenue
FROM events
GROUP BY 1;

-- BQ auto-incrementally updates
-- Queries hit MV (small) not raw (huge)
```

### Tactic 3: Query Optimization

```sql
-- Bad: SELECT *
SELECT * FROM huge_table WHERE date = '2026-05-01';
-- Scans all columns

-- Good: only what you need
SELECT id, amount FROM huge_table WHERE date = '2026-05-01';
-- Scans only 2 columns
```

### Tactic 4: Avoid Wildcards in WHERE

```sql
-- Bad: function on partition column
WHERE EXTRACT(YEAR FROM event_time) = 2026
-- BQ can't prune

-- Good: direct comparison
WHERE event_time >= '2026-01-01' AND event_time < '2027-01-01'
-- Pruning works
```

### Tactic 5: Limit on Big Queries

```sql
-- In dev, always:
SELECT * FROM huge_table WHERE ... LIMIT 100;
-- Saves money on accidental full scans
```

### Tactic 6: BigLake Iceberg + BQ External

```
Heavy compute on Dataflow → Iceberg (cheap storage)
BQ as external table over Iceberg
Light queries scan Iceberg metadata + small data
Cost: minimal BQ compute
```

---

## 5. ML / AI Cost Optimization

### Training Cost

#### Tactic 1: Spot/Preemptible for Training

```python
# Vertex AI
job = aiplatform.CustomTrainingJob(
    machine_type='a2-highgpu-1g',
    accelerator_type='NVIDIA_A100',
    accelerator_count=1,
    boot_disk_type='pd-ssd',
    use_spot_vm=True,  # 60-80% off
)
```

#### Tactic 2: Mixed Precision (bf16/fp16)

```python
# Automatic mixed precision
trainer = Trainer(
    args=TrainingArguments(
        bf16=True,  # 2x speed, half memory
        ...
    )
)
```

#### Tactic 3: Gradient Accumulation

```
Want batch_size=64 but GPU only fits 8
Solution: gradient_accumulation_steps=8
Same effective batch, lower memory
```

#### Tactic 4: PEFT (LoRA/QLoRA)

```
Full fine-tune 70B: $20K
QLoRA fine-tune 70B: $1K (95% quality)
Use QLoRA whenever possible
```

#### Tactic 5: Resume from Checkpoint

```
Training crashed at epoch 5/10?
Resume from checkpoint, don't restart
Save 50% compute
```

### Inference Cost

#### Tactic 1: Smart Routing

```python
def route(query):
    if simple(query):
        return "haiku"  # $0.80/1M tokens
    elif medium(query):
        return "sonnet"  # $3/1M
    else:
        return "opus"   # $15/1M

# Saves 60-80% with proper routing
```

#### Tactic 2: Quantization

```
fp16 70B: 4× A100 ($25/hour)
AWQ-4bit 70B: 1× A100 ($6/hour)
Cost: 4x reduction
Quality: ~3% loss
```

#### Tactic 3: Caching

```
Anthropic prompt caching: 90% off cached input
OpenAI: similar feature

Cacheable:
- System prompts
- Long context (RAG retrieved chunks)
- Document context

Save 50-90% for chatbots with consistent system
```

#### Tactic 4: Batch Processing

```
Real-time API: $3/1M tokens
Batch API (24hr SLA): $1.50/1M (50% off)

Use batch for:
- Offline scoring
- Bulk analysis
- Non-urgent generation
```

#### Tactic 5: Output Limits

```python
# Cap max tokens
response = llm.generate(
    prompt,
    max_tokens=500  # cap output
)

# vs unbounded: model might write 4K tokens
```

#### Tactic 6: Smaller Models When Possible

```
GPT-5 ($2.50/$10) for everything
vs
GPT-5 nano ($0.05/$0.40) for 90% of queries
+ GPT-5 ($2.50/$10) for hard ones

50x cost savings on routine queries
```

#### Tactic 7: Fine-Tune Smaller Model

```
Use GPT-5 ($10/1M output) — too expensive at scale
Fine-tune Llama 3 8B on your task quality
Self-host with vLLM ($0.50/1M effective)

20x cheaper at scale (>10M tokens/day)
```

---

## 6. FinOps Practices

### Tagging Strategy (mandatory)

ทุก resource ต้องมี:
```
team: "fraud_team"
project: "fraud_v2"
environment: "production"
cost_center: "CC-1234"
owner: "jane.doe@company.com"
purpose: "ml_training"
ttl: "permanent" or "30_days"
```

Without tags → can't attribute → can't optimize

### Cost Visibility Dashboard

```
PER TEAM:
- Total spend
- Top 10 expensive resources
- Trend (vs last month)
- Anomaly detection

PER PROJECT:
- Same as above
- Per-job cost breakdown

PER USER:
- Top spenders
- Their queries

EFFICIENCY:
- Cost per outcome (per dashboard, per model)
- Cost per query
```

### Tools

- **Vendor-native**: AWS Cost Explorer, GCP Cost, Azure Cost Mgmt
- **Multi-cloud**: Cloudability, Apptio
- **Database-specific**: SELECT (BQ), Finout (DBX/SF), Bluesky (SF)
- **Open source**: OpenCost (K8s), KubeCost

### Review Cadence

```
Daily:
- Anomaly alerts (spend spike > 30%)
- Failed job re-run cost

Weekly:
- Top 10 expensive items review
- Wasted resources (idle, oversized)

Monthly:
- Trend review with leaders
- Optimization initiatives
- Tag compliance audit

Quarterly:
- Reserve capacity decisions
- Architecture cost review
- ROI of optimizations
```

---

## 7. Hidden Costs

### Egress (cross-region/cross-cloud)

```
GCP within region: free
GCP cross-region: $0.02/GB
GCP to internet: $0.12/GB
GCP to AWS: $0.12/GB

1 TB egress = $120
100 TB/month = $12,000

Mitigation:
- Process in same region as data
- Use VPC peering for cross-cloud
- Compress before transfer
```

### NAT Gateway

```
NAT charges per GB processed
Often unexpectedly high
Especially: API calls from K8s pods → external

Mitigation:
- VPC endpoints (private connections)
- Direct routes
- Inspect NAT data flow
```

### CloudWatch / Monitoring

```
Metrics + logs at scale = $$$
1B log lines/day = thousands $/month

Mitigation:
- Tier retention (hot 7d, cold 90d, archive 1yr)
- Sample logs (1% for high volume)
- Filter before logging (don't log /health)
```

### Idle Resources

```
- Database instances during off-hours
- Dev/staging environments not auto-stop
- Notebook instances forgotten
- Test clusters left running

Mitigation:
- Scheduled stop/start (weekends off)
- Auto-shutdown after idle (notebook 1hr)
- Tag dev/test for review
```

---

## 8. Architecture-Level Cost Patterns

### Pattern 1: Tiered Compute by SLA

```
Hot tier (real-time, expensive):
  Streaming engine 24/7
  10% of data, 80% of value

Warm tier (near-real-time):
  Micro-batch
  30% of data

Cold tier (batch):
  Daily/weekly
  60% of data, 5% of value
  
Wrong: real-time everything = 5-10x cost
```

### Pattern 2: Storage-Compute Separation

```
Tightly coupled (Snowflake legacy):
  Storage + compute together
  Pay for compute even when idle
  
Decoupled (Iceberg + any compute):
  Storage cheap (S3/GCS)
  Compute on-demand
  Spin up only when needed
```

### Pattern 3: Open Format → Choose Cheapest Compute

```
Iceberg as canonical storage
Read with:
  - Trino (cheap interactive)
  - Spark (heavy transform)
  - Flink (streaming)
  - Dataflow (managed)
  - DuckDB (local)

Choose engine by cost-performance for each workload
```

### Pattern 4: Serverless When Possible

```
Always-on cluster:    $2000/month (24/7)
Serverless query:     $200/month (only when used)

But: warm-up costs, cold-start latency
Use for: variable/low usage
Avoid for: constant high load
```

---

## 9. Cost-Aware Query Patterns

### Pattern 1: Pre-Aggregate

```sql
-- Wrong: query raw 1B rows every time
SELECT user_country, COUNT(*) FROM events GROUP BY 1;
-- Scans 100 GB, $0.50

-- Right: materialize once, query forever
CREATE TABLE country_stats AS
SELECT user_country, COUNT(*) FROM events GROUP BY 1;
-- Then query country_stats (small, cheap)
```

### Pattern 2: Sample for Exploration

```sql
-- Production query: full data
SELECT ... FROM events WHERE ...

-- Exploration: sample 1%
SELECT ... FROM events TABLESAMPLE SYSTEM (1 PERCENT) WHERE ...
-- 100x cheaper, still get insight
```

### Pattern 3: Push Filters Early

```sql
-- Bad: huge join, then filter
SELECT * FROM big_table_1 JOIN big_table_2 USING (id)
WHERE big_table_1.date = '2026-05-01';

-- Good: filter first, then join
WITH filtered_1 AS (
  SELECT * FROM big_table_1 WHERE date = '2026-05-01'
)
SELECT * FROM filtered_1 JOIN big_table_2 USING (id);
```

### Pattern 4: APPROXIMATE Functions

```sql
-- Exact: full scan
SELECT COUNT(DISTINCT user_id) FROM events;

-- Approximate: HyperLogLog, 5x faster
SELECT APPROX_COUNT_DISTINCT(user_id) FROM events;
-- Off by 1-2%, often acceptable
```

---

## 10. ML/AI Specific Cost Patterns

### LLM Cost Math (concrete)

```
Customer support bot:
  10K conversations/day
  5 turns avg
  500 tokens in + 200 out per turn
  
Per conversation: 5 × (500 + 200) = 3500 tokens

Using Sonnet ($3 in / $15 out):
  Daily: 10K × (5 × $3 × 500/1M + 5 × $15 × 200/1M)
       = 10K × ($0.0075 + $0.015)
       = 10K × $0.0225
       = $225/day
  Monthly: $6,750

After caching system prompt (90% off):
  Daily: 10K × ($0.0008 + $0.015)
       = $158/day
  Monthly: $4,740 (30% savings)

After smart routing (50% Haiku):
  $$reduce by ~40% more
  Monthly: ~$2,800
```

### Self-Host Calculation

```
Same workload on self-hosted Llama 3 70B:
  Hardware: 4× A100 80GB
  Cloud rental: ~$25/hour × 24 × 30 = $18,000/month
  
Self-host worth it if API > $18K/month (10M+ tokens/day)
```

### Embedding Cost

```
Text embeddings: ~$0.10-0.20 / 1M tokens
1B documents × 500 tokens each = 500B tokens = $50-100K one-time

Optimization:
- Cache embeddings (reuse forever)
- Smaller embedding models if quality OK
- Self-host embedding (cheaper at scale)
```

---

## 11. Optimization Roadmap (3-month plan)

### Month 1: Visibility
- [ ] Mandatory tagging policy
- [ ] Cost dashboard per team
- [ ] Anomaly alerts (spend spikes)
- [ ] Top 10 expensive resources audit

### Month 2: Quick Wins
- [ ] Delete unused tables (>90d untouched)
- [ ] Lifecycle policies for cold data
- [ ] Right-size clusters
- [ ] Switch to spot/preemptible where safe
- [ ] Enable AQE, partition pruning

### Month 3: Architecture
- [ ] Migrate to open format (Iceberg)
- [ ] Tiered storage strategy
- [ ] Smart routing for LLM
- [ ] Implement caching
- [ ] Materialize hot queries

---

## 12. Cheat Sheet

### Q: "ทำให้ data platform ถูกลงยังไง?"
> "1. Visibility (tagging + dashboards)
> 2. Storage tiers (hot/warm/cold)
> 3. Right-size compute (auto-scale, spot)
> 4. Query optimization (partition, cluster)
> 5. Architecture (open format, decoupled)"

### Q: "BigQuery ค่าใช้จ่ายควบคุมยังไง?"
> "1. Partition + cluster everything
> 2. Materialized views for hot queries
> 3. Avoid SELECT * — only needed columns
> 4. Slot reservation if predictable
> 5. BigLake Iceberg for heavy data
> 6. APPROX functions when exactness not needed"

### Q: "LLM cost ลดยังไง?"
> "1. Smart routing (cheap model for simple)
> 2. Prompt caching (90% off cached)
> 3. Batch API (50% off)
> 4. Output limits (max_tokens)
> 5. Self-host (>10M tokens/day)
> 6. Fine-tune smaller model on task"

### Q: "Spot instance ใช้ตรงไหนได้บ้าง?"
> "Batch jobs: ✅ (retryable)
> ML training: ✅ (with checkpoints)
> Stateless inference: ✅ (with redundancy)
> Streaming: ⚠️ (mixed: some on-demand for stability)
> Stateful DB: ❌"

### Q: "Hidden costs ที่คนลืม?"
> "1. Egress (cross-region/cloud) — can be 50%+ of bill
> 2. NAT Gateway data processing
> 3. CloudWatch logs at scale
> 4. Idle resources (notebooks, dev clusters)
> 5. Snapshot retention (Iceberg, RDS)"

---

## Sources

- [BigQuery Cost Optimization Best Practices](https://cloud.google.com/bigquery/docs/best-practices-costs)
- [Databricks Cost Optimization Guide](https://docs.databricks.com/en/admin/account-settings/billable-usage-delivery.html)
- [FinOps Foundation](https://www.finops.org/)
- [Apache Spark Performance Tuning 2026](https://www.flexera.com/blog/finops/spark-performance-tuning/)
- [SELECT BigQuery Cost Optimization](https://www.morningstar.com/news/pr-newswire/20260416sf36330/select-announces-automated-bigquery-cost-optimization-early-access-program)
- [Databricks FinOps Genie](https://www.databricks.com/dataaisummit/session/databricks-finops-genie-cost-observability-meets-optimization-insights)
- [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [Iceberg Table Maintenance](https://iceberg.apache.org/docs/latest/maintenance/)
