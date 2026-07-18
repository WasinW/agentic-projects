# Streaming + Batch Join Research: Sales-Collector Public/Analytics Layer

> **Date**: 2026-03-17
> **Context**: sales-collector streaming Dataflow pipeline (Python, Beam 2.71.0) needs to JOIN streaming refined data with 5 large batch tables (~15M rows each) to produce a public/analytics layer in BQ.
> **Throughput**: 10K-100K messages/sec
> **Batch tables**: ~15M rows x ~10 columns each, 5 tables, updated periodically (BQ DTS from AWS)

---

## Table of Contents

1. [Existing Research Summary](#1-existing-research-summary)
2. [Memory Estimation](#2-memory-estimation)
3. [Option Evaluation](#3-option-evaluation)
   - [A. Side Input from BQ](#a-side-input-from-bq)
   - [B. In-memory Cache (MasterCache pattern)](#b-in-memory-cache-mastercache-pattern)
   - [C. Bigtable as Lookup](#c-bigtable-as-lookup)
   - [D. Redis/Memorystore as Lookup](#d-redismemorystore-as-lookup)
   - [E. Separate Batch Pipeline (Staging + BQ/Spark JOIN)](#e-separate-batch-pipeline-staging--bqspark-join)
   - [F. BQ Scheduled Queries / Views](#f-bq-scheduled-queries--views)
   - [G. Beam Enrichment Transform](#g-beam-enrichment-transform)
   - [H. CoGroupByKey with Periodic BQ Reads](#h-cogroupbykey-with-periodic-bq-reads)
   - [I. Materialized Views in BQ](#i-materialized-views-in-bq)
   - [J. Hybrid: Streaming to Raw + BQ Post-processing](#j-hybrid-streaming-to-raw--bq-post-processing)
4. [Comparison Matrix](#4-comparison-matrix)
5. [Recommendation](#5-recommendation)
6. [Sources](#6-sources)

---

## 1. Existing Research Summary

The existing document (`BQ_LOOKUP_TECHNIQUES.md`) evaluated 7 techniques for the **current** sales_channel enrichment (small lookup tables, ~1K-10K rows):

| # | Technique | Verdict |
|---|-----------|---------|
| 1 | Side Input + PeriodicImpulse | Good for <1GB master data |
| 2 | Stateful DoFn + Timer Cache | Too complex for global master data |
| 3 | Per-element BQ Query | **Banned** -- $5,150/day at 1K events/sec |
| 4 | External Cache (BigTable/Redis) | Overkill for small data, best for >2GB |
| 5 | Beam Enrichment Transform | Requires BigTable/Feature Store |
| 6 | CoGroupByKey Join | Windowing complexity, stale bounded data |
| 7 | Shared In-process Cache (singleton) | **Recommended** for <500MB master data |

**Decision matrix from existing research:**
```
< 500MB  --> Shared Cache (Technique 7) -- CURRENT IMPLEMENTATION
500MB-2GB --> Side Input (Technique 1)
> 2GB    --> BigTable (Technique 4)
```

**Key gap**: The existing research assumed master data < 500MB. The new requirement is **~75M rows across 5 tables**, which is a fundamentally different scale.

---

## 2. Memory Estimation

### Per-row size estimate

Assuming 15M rows x 10 columns per table. Column types: mix of strings (avg 20 bytes), integers (8 bytes), dates (10 bytes).

```
Average row size (raw data):
  - 4 string columns x 20 bytes = 80 bytes
  - 4 integer columns x 8 bytes = 32 bytes
  - 2 date columns x 10 bytes   = 20 bytes
  - Row overhead (dict keys, Python object headers) ~= 3-5x raw data in Python
  = ~132 bytes raw x 4 (Python dict overhead) ~= 528 bytes/row

Conservative estimate: ~600 bytes/row in a Python dict
Aggressive estimate:   ~300 bytes/row with optimized storage (namedtuple, slots)
```

### Total memory requirements

| Scenario | Per Table | 5 Tables | Notes |
|----------|-----------|----------|-------|
| Python dict (typical) | ~9 GB | ~45 GB | dict of dicts, standard Python objects |
| Optimized (slots/namedtuple) | ~4.5 GB | ~22.5 GB | Reduced Python object overhead |
| Compressed (msgpack/pickle in memory) | ~2 GB | ~10 GB | Requires deserialization per lookup |
| Raw data only (no Python overhead) | ~2 GB | ~10 GB | Theoretical minimum, not achievable in Python |

### Verdict on in-memory feasibility

- **Dataflow worker default memory**: 4 GB (n1-standard-1) to 16 GB (n1-standard-4)
- **Dataflow Vertical Autoscaling max**: 16 GiB per worker (default limit)
- **Side input**: Replicated to EVERY worker -- multiply by worker count
- **Singleton cache**: One copy per worker process

**45 GB in a Python dict will NOT fit in any standard Dataflow worker.** Even with n1-highmem-16 (104 GB), each worker holding 45 GB leaves little for pipeline processing. This rules out in-memory approaches for the full dataset.

---

## 3. Option Evaluation

### A. Side Input from BQ

**How it works**: PeriodicImpulse reads all 5 tables from BQ periodically, materializes as side inputs distributed to all workers.

| Criterion | Assessment |
|-----------|------------|
| **Memory** | ~45 GB per worker (replicated to ALL workers) -- **IMPOSSIBLE** |
| **Latency** | Minutes to re-read + distribute 75M rows |
| **Freshness** | Configurable (hourly, etc.) |
| **Complexity** | Medium |
| **Cost** | BQ scan: 5 tables x ~2GB x 24/day x N workers = moderate |
| **Reliability** | OOM guaranteed at this scale |
| **Throughput** | N/A -- won't work |

**Side input cache**: `--max_cache_memory_usage_mb` defaults to 100 MB (SDK 2.52+). Even if increased, 45 GB per worker is not viable.

**Verdict: ELIMINATED** -- 75M rows far exceeds side input capacity. Beam documentation recommends side inputs "fit into worker's memory." Google's OOM troubleshooting guide confirms large side inputs are a primary OOM cause.

---

### B. In-memory Cache (MasterCache Pattern)

**How it works**: Current pattern -- singleton dict in each worker process, refreshed from BQ periodically.

| Criterion | Assessment |
|-----------|------------|
| **Memory** | ~45 GB per worker process -- **IMPOSSIBLE** on standard machines |
| **Latency** | Zero (in-process dict lookup) |
| **Freshness** | Configurable refresh interval |
| **Complexity** | Low (already implemented for small tables) |
| **Cost** | BQ scan only |
| **Reliability** | OOM guaranteed; refresh of 75M rows takes minutes, blocks pipeline |
| **Throughput** | Excellent IF it fit in memory |

**Could it work with high-memory machines?**
- n1-highmem-16 (104 GB): 45 GB cache + pipeline overhead -- theoretically possible but extremely wasteful
- Cost: ~$0.83/hr per worker x N workers = very expensive just for memory
- Refresh time: Reading 75M rows from BQ into Python dict takes 10-30 minutes
- During refresh: pipeline stalls or uses stale data

**Verdict: ELIMINATED** for 75M rows. The current MasterCache works because data is <10K rows. Scaling to 75M is a 7,500x increase that breaks this pattern.

---

### C. Bigtable as Lookup

**How it works**: Batch job syncs BQ tables to Bigtable. Streaming pipeline does per-element key-value lookup.

| Criterion | Assessment |
|-----------|------------|
| **Memory** | Low (external storage, no in-memory requirement) |
| **Latency** | <10ms per lookup (single row read) |
| **Freshness** | Depends on sync job frequency (hourly, daily) |
| **Complexity** | High (new infra: Bigtable instance, sync job, schema design) |
| **Cost** | ~$470-940/month (see breakdown below) |
| **Reliability** | Very high (managed service, auto-replication) |
| **Throughput** | 10K+ reads/sec per node, scales linearly |

**Cost breakdown:**
```
Bigtable nodes: 1 node (handles ~10K reads/sec) = $0.65/hr = $468/month
  - At 100K msg/sec with 5 lookups each = 500K reads/sec -> need ~50 nodes = $23,400/month !!
  - BUT: batch lookups or pre-joining can reduce this dramatically
Storage: 75M rows x ~150 bytes (compact) = ~11 GB = ~$2.50/month (SSD)
Sync job: Cloud Function/Dataflow batch = ~$5-20/month
```

**Critical insight on throughput math:**
- 100K msg/sec x 5 table lookups = 500K Bigtable reads/sec
- Each Bigtable node handles ~10K reads/sec
- Needs ~50 nodes at peak = **$23,400/month** -- extremely expensive at high throughput
- At 10K msg/sec: 50K reads/sec -> ~5 nodes = ~$2,340/month

**Optimization: Batch reads with Beam Enrichment Transform** can batch up to 10,000 rows per request, but Bigtable batch reads are still limited by node throughput.

**Verdict: VIABLE but EXPENSIVE at high throughput.** Best if throughput is consistently <10K msg/sec or if lookups can be batched/deduplicated before hitting Bigtable.

---

### D. Redis / Memorystore as Lookup

**How it works**: Batch job syncs BQ tables to Redis. Streaming pipeline does per-element key-value lookup.

| Criterion | Assessment |
|-----------|------------|
| **Memory** | Redis server: ~15-25 GB for 75M rows (compact keys+values) |
| **Latency** | <1ms per lookup |
| **Freshness** | Depends on sync job frequency |
| **Complexity** | High (new infra: Memorystore, sync job, key design) |
| **Cost** | ~$300-600/month (see breakdown) |
| **Reliability** | High (managed, but single-region; Standard tier has replicas) |
| **Throughput** | 200K+ reads/sec per instance |

**Cost breakdown:**
```
Memorystore for Redis:
  - 75M rows x ~200 bytes (key + hash fields) = ~15 GB
  - With Redis overhead (~1.5x) = ~22 GB
  - Standard tier (HA): $0.049/GB/hr in us-central1
  - 25 GB x $0.049/hr = $1.225/hr = $882/month
  - Basic tier (no HA): $0.016/GB/hr = $288/month

Memorystore for Redis Cluster (better for high throughput):
  - Can handle 200K+ reads/sec per shard
  - 100K msg/sec x 5 lookups = 500K reads/sec -> ~3 shards
  - Pricing varies but typically $400-800/month for this size

Sync job: Cloud Function/Dataflow batch = ~$5-20/month
```

**Advantages over Bigtable:**
- Sub-millisecond latency vs <10ms
- Significantly cheaper at high throughput (fewer "nodes" needed)
- Redis handles 200K reads/sec per instance vs Bigtable's 10K per node
- Redis Cluster can handle 500K+ reads/sec across shards

**Disadvantages:**
- Data must fit in memory (22 GB is fine, but limits growth)
- Less durable than Bigtable (memory-based)
- Need careful key design for 5 different tables
- VPC peering required for Memorystore

**Verdict: VIABLE and more cost-effective than Bigtable for this use case.** Redis's throughput-per-dollar is much better. However, adds significant infra complexity.

---

### E. Separate Batch Pipeline (Staging + BQ/Spark JOIN)

**How it works**: Streaming pipeline writes to BQ staging/raw tables only. A separate batch job (BQ scheduled query, Dataflow batch, or Spark) reads staging + batch tables, performs the JOIN, writes to analytics layer.

```
STREAMING: Kafka -> Dataflow -> BQ refined tables (receipt, sku, tender) [EXISTING]
                                       |
BATCH:     BQ Scheduled Query (every N minutes/hours)
              SELECT r.*, b1.*, b2.*, b3.*, b4.*, b5.*
              FROM refined.receipt r
              LEFT JOIN batch_table_1 b1 ON r.key1 = b1.key1
              LEFT JOIN batch_table_2 b2 ON r.key2 = b2.key2
              ...
              -> analytics.enriched_receipt
```

| Criterion | Assessment |
|-----------|------------|
| **Memory** | Zero additional (BQ handles it) |
| **Latency** | Minutes to hours (batch interval) |
| **Freshness** | Batch interval (5min to 1hr typical) |
| **Complexity** | **LOW** -- SQL query + scheduler |
| **Cost** | BQ query cost only (~$5-30/month depending on data volume) |
| **Reliability** | Very high (BQ is battle-tested for JOINs) |
| **Throughput** | Not a concern (decoupled from streaming) |

**BQ cost estimate:**
```
Refined tables: ~1 day of streaming at 100K msg/sec
  = ~8.6B rows/day x ~200 bytes = ~1.7 TB/day ingested

Scheduled query scans:
  - Use partitioned tables + incremental logic (WHERE ingestedDate = CURRENT_DATE)
  - Scan ~1.7 TB refined + 5 x 2 GB batch tables = ~11.7 TB/day
  - At on-demand: $6.25/TB = ~$73/day = ~$2,190/month

  WITH OPTIMIZATION (flat-rate / editions):
  - BQ Enterprise edition: ~$0.04/slot-hour
  - JOIN of partitioned tables: ~100 slots for minutes = ~$5-10/day

  WITH INCREMENTAL (process only new rows):
  - Process only rows since last run (e.g., every 15 min)
  - Scan ~100 GB/run + batch tables = ~$0.75/run x 96 runs/day = ~$72/day
```

**Key advantages:**
1. **No changes to streaming pipeline** -- streaming stays fast and simple
2. **BQ handles the heavy lifting** -- optimized for large JOINs, no memory concerns
3. **Familiar tooling** -- SQL, scheduled queries, monitoring via BQ UI
4. **Easiest to implement and maintain**
5. **Naturally handles batch table updates** -- next query run picks up changes
6. **Can use BQ's partition pruning** and clustering for efficient scans

**Key disadvantages:**
1. **Latency** -- not real-time; minimum practical interval ~5-15 minutes
2. **BQ cost** can be significant at high volumes without flat-rate pricing
3. **Two systems to monitor** (streaming pipeline + scheduled queries)

**Verdict: STRONGLY VIABLE.** If analytics layer latency of 5-60 minutes is acceptable, this is the simplest and most cost-effective approach. Let BQ do what BQ does best -- large JOINs.

---

### F. BQ Scheduled Queries / Views

**How it works**: Create BQ views or scheduled queries that JOIN refined tables with batch tables. Analytics consumers query the view.

**Sub-option F1: Regular View (no materialization)**
```sql
CREATE VIEW analytics.enriched_receipt AS
SELECT r.*, b1.col1, b2.col2, ...
FROM refined.receipt r
LEFT JOIN batch_table_1 b1 ON r.key1 = b1.key1
LEFT JOIN batch_table_2 b2 ON r.key2 = b2.key2
...
```

| Criterion | Assessment |
|-----------|------------|
| **Memory** | Zero |
| **Latency** | Zero (query-time JOIN) |
| **Freshness** | Real-time (always latest data) |
| **Complexity** | **Trivial** -- single CREATE VIEW statement |
| **Cost** | Per-query scan cost (expensive if queried frequently) |
| **Reliability** | Very high |
| **Throughput** | N/A (query-time) |

**Problem**: Every downstream query rescans all data + performs JOINs. If many dashboards hit this view frequently, cost explodes.

**Sub-option F2: Scheduled Query (materialized output)**
Same as Option E. Scheduled query runs periodically, writes to a physical table.

**Verdict: F1 (view) is too expensive for frequent queries. F2 is equivalent to Option E.**

---

### G. Beam Enrichment Transform (BigQueryEnrichmentHandler)

**How it works**: Use Beam's built-in `Enrichment` transform with `BigQueryEnrichmentHandler` (available since Beam 2.57.0).

```python
from apache_beam.transforms.enrichment import Enrichment
from apache_beam.transforms.enrichment_handlers.bigquery import BigQueryEnrichmentHandler

handler = BigQueryEnrichmentHandler(
    project="my-project",
    table_name="project.dataset.batch_table_1",
    row_restriction_template="key = '{}'",
    fields=["lookup_key"],
    min_batch_size=100,
    max_batch_size=10000,
)

enriched = events | Enrichment(handler)
```

| Criterion | Assessment |
|-----------|------------|
| **Memory** | Low (no in-memory cache) |
| **Latency** | 100ms-1s per batch (BQ Storage API read) |
| **Freshness** | Real-time (queries BQ directly) |
| **Complexity** | Medium (Beam-native, but 5 chained enrichments) |
| **Cost** | BQ query cost per batch -- could be high |
| **Reliability** | Medium (BQ throttling, quotas) |
| **Throughput** | Limited by BQ API throughput |

**Critical analysis:**
- `max_batch_size=10000` means batches of up to 10K elements per BQ request
- At 100K msg/sec: 10 BQ requests/sec x 5 tables = 50 BQ requests/sec
- Each request scans the batch table with a WHERE clause
- BQ concurrent query limit: 100 (default) -- could hit quota with 50 req/sec
- **BQ Storage Read API** might be used internally, but per-batch queries still hit BQ quotas
- No built-in caching (unlike Bigtable handler which can use Redis cache)

**Cost estimate:**
```
At 100K msg/sec, batched at 10K:
  10 batches/sec x 5 tables x 86400 sec = 4.32M queries/day
  Each query scans ~1 row from indexed table: 10MB minimum charge
  4.32M x 10MB = 43.2 TB/day = $270/day = $8,100/month !!

  With BQ flat-rate: more predictable but still heavy slot usage
```

**Verdict: PROBLEMATIC at high throughput.** The BigQueryEnrichmentHandler issues per-batch queries to BQ, which hits quotas and incurs per-query minimum charges. Better suited for low-throughput pipelines or when combined with Bigtable handler instead.

---

### H. CoGroupByKey with Periodic BQ Reads

**How it works**: Periodically read batch tables into PCollections, window them, and CoGroupByKey with streaming data.

```python
# Periodic batch read
batch_data = (
    p
    | PeriodicImpulse(fire_interval=3600)
    | beam.FlatMap(lambda _: read_from_bq("batch_table"))
    | beam.Map(lambda r: (r["key"], r))
    | beam.WindowInto(FixedWindows(3600))
)

# Streaming
events = (
    kafka
    | beam.Map(lambda e: (e["key"], e))
    | beam.WindowInto(FixedWindows(3600))
)

# Join
joined = (
    {"events": events, "batch": batch_data}
    | beam.CoGroupByKey()
    | beam.FlatMap(merge_fn)
)
```

| Criterion | Assessment |
|-----------|------------|
| **Memory** | High -- 75M rows must be held in shuffle/state |
| **Latency** | Window-aligned (e.g., hourly windows) |
| **Freshness** | Per-window refresh |
| **Complexity** | **Very High** -- windowing alignment, watermark management, hot keys |
| **Cost** | BQ scan per refresh + Dataflow shuffle cost for 75M rows |
| **Reliability** | Low -- watermark issues, OOM on hot keys, complex debugging |
| **Throughput** | Limited by shuffle capacity |

**Problems:**
1. CoGroupByKey with 75M rows on one side = massive shuffle
2. Window alignment between bounded (batch) and unbounded (streaming) is fragile
3. Hot keys cause OOM on individual workers
4. Watermark management is extremely tricky
5. Debugging failures is painful

**Verdict: ELIMINATED** -- Too complex, too fragile, and too resource-intensive for this scale.

---

### I. Materialized Views in BQ

**How it works**: Create materialized views that pre-compute the JOIN. BQ auto-refreshes when base tables change.

```sql
CREATE MATERIALIZED VIEW analytics.enriched_receipt AS
SELECT r.*, b1.col1, b2.col2
FROM refined.receipt r
LEFT JOIN batch_table_1 b1 ON r.key = b1.key
LEFT JOIN batch_table_2 b2 ON r.key2 = b2.key2
```

| Criterion | Assessment |
|-----------|------------|
| **Memory** | Zero (BQ-managed) |
| **Latency** | Auto-refresh (minutes after base table change) |
| **Freshness** | Near-real-time for streaming base tables |
| **Complexity** | **Very Low** -- single DDL statement |
| **Cost** | Storage cost + maintenance cost (auto-refresh) |
| **Reliability** | High (BQ-managed) |
| **Throughput** | N/A (BQ handles internally) |

**Limitations of BQ Materialized Views:**
1. **JOIN restrictions**: Materialized views support JOINs but with limitations:
   - Only inner and left outer joins
   - Star schema only (one fact table, multiple dimension tables)
   - Dimension tables must be < 50 GB each (check current limit)
   - Incremental refresh only works for appended rows, not updates
2. **Refresh behavior**: Auto-refresh may lag; manual refresh adds cost
3. **5-table JOIN**: Might hit complexity limits for materialized views
4. **Streaming base table**: Materialized views work with streaming buffer, but refresh frequency may be limited
5. **Cost**: BQ charges for materialized view storage + maintenance queries

**Verdict: POTENTIALLY VIABLE if BQ materialized view limitations are acceptable.** The star-schema requirement (one fact + multiple dimension tables) matches our use case. Need to verify current limits on number of JOINs and dimension table sizes.

---

### J. Hybrid: Streaming to Raw + BQ Post-processing

**How it works**: Combines the strengths of streaming (low latency for raw/refined) with batch (BQ for heavy JOINs).

```
Architecture:

STREAMING (existing, no change):
  Kafka -> Dataflow -> Iceberg source tables
                    -> BQ refined tables (receipt, sku, tender)

POST-PROCESSING (new, simple):
  Option J1: BQ Scheduled Query (every 15 min)
    -> Incremental JOIN: new refined rows + 5 batch tables
    -> Write to analytics.enriched_* tables

  Option J2: BQ Materialized View
    -> Auto-refresh JOIN
    -> analytics.enriched_* view

  Option J3: Dataflow Batch (daily/hourly)
    -> Full JOIN with Dataflow batch pipeline
    -> Write to analytics.enriched_* tables
```

| Criterion | Assessment |
|-----------|------------|
| **Memory** | Zero additional on streaming side |
| **Latency** | 15 min (J1), near-real-time (J2), hourly (J3) |
| **Freshness** | Good for analytics use case |
| **Complexity** | Low (J1/J2) to Medium (J3) |
| **Cost** | $50-200/month with proper optimization |
| **Reliability** | Very high (decoupled failure domains) |
| **Throughput** | Not constrained (decoupled from streaming) |

**Why this is the best approach for THIS use case:**

1. **Streaming pipeline stays fast**: No enrichment overhead, no memory pressure, no external service dependencies
2. **JOIN is decoupled**: BQ scheduled query or materialized view handles the heavy JOIN
3. **Batch tables update independently**: Next query run automatically picks up changes
4. **Easiest to operate**: SQL-based, BQ monitoring, no new infra
5. **Cost-effective**: BQ is optimized for large JOINs; no need for Bigtable/Redis
6. **Incremental processing**: Only JOIN new rows since last run, using partition pruning

**Implementation sketch (J1 - Scheduled Query):**
```sql
-- Run every 15 minutes
-- Process only rows since last run using partition filter
MERGE INTO analytics.enriched_receipt t
USING (
  SELECT
    r.*,
    b1.dim1_col1, b1.dim1_col2,
    b2.dim2_col1, b2.dim2_col2,
    b3.dim3_col1,
    b4.dim4_col1,
    b5.dim5_col1
  FROM refined.receipt r
  LEFT JOIN batch_dataset.dim_table_1 b1 ON r.join_key_1 = b1.key
  LEFT JOIN batch_dataset.dim_table_2 b2 ON r.join_key_2 = b2.key
  LEFT JOIN batch_dataset.dim_table_3 b3 ON r.join_key_3 = b3.key
  LEFT JOIN batch_dataset.dim_table_4 b4 ON r.join_key_4 = b4.key
  LEFT JOIN batch_dataset.dim_table_5 b5 ON r.join_key_5 = b5.key
  WHERE r.ingestedDate >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 20 MINUTE)
) s
ON t.receipt_id = s.receipt_id
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...
```

**Verdict: RECOMMENDED.** This is the pragmatic, production-proven approach for enriching streaming data with large batch/dimension tables.

---

## 4. Comparison Matrix

| Option | Memory Impact | Latency | Freshness | Complexity | Monthly Cost | Throughput | Viable? |
|--------|-------------|---------|-----------|------------|-------------|------------|---------|
| **A. Side Input** | ~45 GB/worker | Minutes | Hourly | Medium | ~$30 BQ | N/A | NO (OOM) |
| **B. MasterCache** | ~45 GB/worker | 0ms | Hourly | Low | ~$5 BQ | Excellent | NO (OOM) |
| **C. Bigtable** | Low | <10ms | Hourly | High | $2K-23K | High | YES (expensive) |
| **D. Redis** | Low (server-side) | <1ms | Hourly | High | $300-900 | Very high | YES |
| **E. Batch Pipeline** | Zero | 15-60min | Batch | Low | $50-200 BQ | Decoupled | **YES** |
| **F. BQ Views** | Zero | Query-time | Real-time | Trivial | Per-query | N/A | PARTIAL |
| **G. Beam Enrichment** | Low | 100ms-1s | Real-time | Medium | $2K-8K BQ | Limited | MARGINAL |
| **H. CoGroupByKey** | High (shuffle) | Window | Window | Very High | High | Limited | NO |
| **I. Materialized View** | Zero | Auto | Near-RT | Very Low | $30-100 | N/A | MAYBE |
| **J. Hybrid (BQ post)** | Zero | 15min | Good | Low | $50-200 | Decoupled | **YES** |

---

## 5. Recommendation

### Ranked Top 3

#### Rank 1: Option J/E -- Hybrid: Streaming Raw + BQ Scheduled Query JOIN

**The clear winner for this use case.**

**Pros:**
- Zero impact on streaming pipeline performance and reliability
- BQ natively handles JOINs of any size -- 75M rows is trivial for BQ
- Simplest to implement: SQL + Cloud Scheduler, no new infra
- Cheapest to operate: ~$50-200/month with incremental processing
- Easiest to maintain: SQL-based, standard BQ monitoring
- Naturally handles batch table updates
- Partition pruning makes incremental JOINs very efficient
- Battle-tested pattern (used by most data platforms)

**Cons:**
- Not real-time: minimum ~5-15 minute latency
- Need to handle late-arriving data (re-process window)
- Two systems to monitor (streaming + scheduled queries)

**When to choose**: Analytics/reporting layer that tolerates 15+ minute latency (which is almost always the case for analytics dashboards built on top of batch dimension tables).

**Implementation effort**: 1-2 days (SQL + scheduler setup)

---

#### Rank 2: Option I -- BQ Materialized Views

**Best if near-real-time freshness is needed with zero operational overhead.**

**Pros:**
- Zero operational overhead -- BQ auto-refreshes
- Near-real-time freshness (auto-refresh on base table change)
- Single DDL statement to create
- Query cost savings vs regular views (pre-computed)
- Star schema pattern matches our use case (1 fact + 5 dimensions)

**Cons:**
- JOIN restrictions (check if 5-way LEFT JOIN is supported in materialized views)
- Dimension table size limits may apply
- Less control over refresh timing
- Incremental maintenance may not work if batch tables are overwritten (not appended)
- Cost can be unpredictable with large base tables

**When to choose**: If materialized view limitations are acceptable AND you need sub-minute freshness.

**Implementation effort**: 0.5-1 day (DDL + testing)

**Action item**: Verify BQ materialized view supports 5-way LEFT JOIN with dimension tables of 15M rows each. Check current limits at: https://cloud.google.com/bigquery/docs/materialized-views-intro

---

#### Rank 3: Option D -- Redis/Memorystore (if real-time is truly required)

**Best if sub-second enrichment latency is a hard requirement.**

**Pros:**
- Sub-millisecond lookup latency
- High throughput (200K+ reads/sec)
- More cost-effective than Bigtable for this scale
- Well-understood technology

**Cons:**
- Adds significant infrastructure: Memorystore instance, VPC peering, sync job
- ~$300-900/month ongoing cost
- Sync job complexity (BQ -> Redis for 5 tables, handle failures, ensure consistency)
- Data size limited by memory (~22 GB, manageable but limits growth)
- New failure modes (Redis down, sync failures, stale data)

**When to choose**: Only if analytics consumers truly need sub-second freshness from the enriched data. In practice, if the batch dimension tables themselves update only periodically (DTS from AWS), sub-second enrichment is pointless -- the dimension data is already hours/days old.

**Implementation effort**: 1-2 weeks (infra setup, sync job, pipeline integration, testing)

---

### Decision Framework

```
Q1: Does the analytics layer need real-time (<1 sec) freshness?
  |
  |--> YES: How fresh are the batch dimension tables themselves?
  |     |
  |     |--> Updated hourly or less --> Redis adds no value, use Option J (scheduled query)
  |     |--> Updated in real-time --> Option D (Redis) -- but verify this claim
  |
  |--> NO (15 min is OK): Option J (BQ Scheduled Query) -- simplest, cheapest
  |
  |--> NO (1-5 min is OK): Option I (Materialized View) -- if limits allow
```

### Final Recommendation

**Start with Option J (BQ Scheduled Query).** It is the simplest, cheapest, and most maintainable approach. The batch dimension tables are DTS-synced from AWS (inherently batch), so real-time enrichment adds no value -- the dimension data is already stale by definition.

If later requirements demand tighter latency, upgrade to materialized views (Option I) or Redis (Option D). The streaming pipeline does NOT need to change for any of these options -- only the post-processing layer changes.

---

## 6. Sources

### Web Sources
- [Enrich streaming data | Cloud Dataflow Documentation](https://docs.cloud.google.com/dataflow/docs/guides/enrichment)
- [Enrich streaming data in Bigtable with Dataflow | Google Cloud Blog](https://cloud.google.com/blog/products/data-analytics/enrich-streaming-data-in-bigtable-with-dataflow)
- [Use Apache Beam and BigQuery to enrich data | Dataflow ML](https://docs.cloud.google.com/dataflow/docs/notebooks/bigquery_enrichment_transform)
- [Use Apache Beam and Bigtable to enrich data | Dataflow ML](https://cloud.google.com/dataflow/docs/notebooks/bigtable_enrichment_transform)
- [Enrichment with Bigtable - Apache Beam](https://beam.apache.org/documentation/transforms/python/elementwise/enrichment-bigtable/)
- [Troubleshoot Dataflow out of memory errors | Google Cloud](https://docs.cloud.google.com/dataflow/docs/guides/troubleshoot-oom)
- [Vertical Autoscaling | Cloud Dataflow](https://docs.cloud.google.com/dataflow/docs/vertical-autoscaling)
- [Bigtable pricing | Google Cloud](https://cloud.google.com/bigtable/pricing)
- [Memorystore for Redis pricing | Google Cloud](https://cloud.google.com/memorystore/docs/redis/pricing)
- [Introduction to materialized views | BigQuery](https://cloud.google.com/bigquery/docs/materialized-views-intro)
- [Side input patterns - Apache Beam](https://beam.apache.org/documentation/patterns/side-inputs/)
- [Scaling a streaming workload on Apache Beam, 1 million events per second](https://beam.apache.org/blog/scaling-streaming-workload/)
- [Apache Beam: Stateful Streaming with Lookup Table | Medium](https://medium.com/@dmitry.turchenkov/apache-beam-stateful-streaming-with-lookup-table-980201a64422)
- [Streaming Data Joins: Real-Time Data Enrichment | DZone](https://dzone.com/articles/streaming-data-joins-a-deep-dive-into-real-time-da)
- [Lambda Architecture on GCP](https://oneuptime.com/blog/post/2026-02-17-how-to-implement-a-lambda-architecture-on-gcp-combining-batch-and-streaming-layers/view)

### Internal References
- `the1-re-data-platform/doc/dataflow/BQ_LOOKUP_TECHNIQUES.md` -- Existing research (7 techniques for small lookup tables)
