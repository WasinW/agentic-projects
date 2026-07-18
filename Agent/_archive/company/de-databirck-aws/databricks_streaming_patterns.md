# 🌊 Databricks Streaming Patterns: Complete Production Reference

> **For:** Sin (Data Engineer @ AIA / Databricks on AWS)
> **Scope:** Delta-to-Delta streaming patterns ใน Databricks (NO external ingest patterns)
> **Sources:** Databricks docs (AWS/Azure), Apache Spark docs, verified
> **Date:** December 2026
> **Status:** Production reference, multi-pattern composition guide

---

## 📑 Table of Contents

1. [Why Multiple Patterns Matter](#1-why-multiple-patterns-matter)
2. [Streaming Fundamentals](#2-streaming-fundamentals)
3. [The 7 Delta-to-Delta Patterns](#3-the-7-delta-to-delta-patterns)
4. [The "Running Aggregation" Problem](#4-the-running-aggregation-problem)
5. [Concerns Matrix (Per Pattern)](#5-concerns-matrix)
6. [Pattern Selection Decision Tree](#6-pattern-selection-decision-tree)
7. [Pattern Combinations (Real Production)](#7-pattern-combinations)
8. [Trigger Modes Deep Dive](#8-trigger-modes-deep-dive)
9. [Checkpoint Mechanics](#9-checkpoint-mechanics)
10. [Production Code Templates](#10-production-code-templates)

---

# 1. Why Multiple Patterns Matter

```
Single pattern thinking:                Reality:
─────────────────────                   ────────
"Use Pattern X for everything"   →    Different patterns for different scenarios
                                       Often COMBINE patterns in single pipeline
                                       
Example real pipeline:
  Bronze (Pattern 1: streaming read)
    ↓
  Silver (Pattern 6: DLT apply_changes for SCD)
    ↓
  Gold (Pattern 3: foreachBatch + MERGE for running totals)
    ↓
  Aggregations (Pattern 2: complete mode for small bounded sums)
```

**Key insight:** หนึ่ง pipeline = หลาย patterns

---

# 2. Streaming Fundamentals

## 2.1 Streaming Source Mechanics

```
ทุก streaming source แบ่งเป็น:

INPUT TRACKING (left side)
  ├── ตำแหน่งล่าสุดที่ process (checkpoint)
  ├── อ่านเฉพาะ NEW data
  └── filter/transform new data only

INPUT MODES (right side)
  ├── append: only new rows
  ├── update: rows that changed in this batch  
  └── complete: all rows in result
```

## 2.2 Key Concepts

| Term | Meaning |
|---|---|
| **Micro-batch** | Streaming = continuous batches at trigger intervals |
| **Checkpoint** | Source offsets + state + commits stored on storage |
| **Watermark** | "How late can data be?" — bounds state |
| **State store** | Memory/RocksDB store for stateful ops |
| **Trigger** | When/how often to run next batch |

## 2.3 Streaming != Always-On

Most production "streaming" = scheduled `availableNow` runs (not 24/7 cluster)

```
True streaming (24/7):       Cluster always running, sub-second to minutes latency
Scheduled streaming:          availableNow trigger, run hourly/daily, exit
```

Cost vs latency tradeoff — most pipelines OK with scheduled

---

# 3. The 7 Delta-to-Delta Patterns

## Pattern 1: **Direct Streaming Read** (Append-only Source)

### Mechanics
```python
events = spark.readStream.table("bronze.events")

(events
    .filter("event_type IN ('CLICK', 'VIEW')")
    .writeStream
    .format("delta")
    .option("checkpointLocation", "/ckpt/silver_events/")
    .trigger(availableNow=True)
    .toTable("silver.events"))
```

### When Source Must Be Append-Only
If source has updates/deletes → stream FAILS unless using:
- `.option("skipChangeCommits", "true")` — ignore non-appends (newer)
- `.option("ignoreChanges", "true")` — older, less safe
- Pattern 4 (CDF) — capture changes

### Pros / Cons
✅ Simplest pattern
✅ Filter/transform any way
✅ Low overhead
❌ Source must be append-only (or use skipChangeCommits)
❌ No upsert capability (target is append too)

### Use For
- Event streams
- Log processing
- Audit trails
- Bronze → Silver transformations on events

---

## Pattern 2: **Streaming Aggregation + Complete Mode**

### Mechanics
```python
(spark.readStream.table("transactions")
    .groupBy("account_id")
    .agg(sum("amount").alias("balance"))
    .writeStream
    .outputMode("complete")          # ⭐ REPLACES entire target
    .option("checkpointLocation", "/ckpt/")
    .toTable("gold.balance"))
```

### How it Works (Internal)
```
Spark maintains STATE STORE:
  {acc_1: balance=100, acc_2: balance=50, ...}

New event arrives: (acc_1, +10)
  State updated: {acc_1: balance=110, acc_2: balance=50, ...}

Output mode "complete":
  → Replace entire gold.balance table with current state
```

### Pros / Cons
✅ Simple declarative aggregation
✅ Spark handles state automatically
✅ Auto-recovery via checkpoint
❌ State grows with unique keys (memory pressure)
❌ Complete mode = rewrites entire target every batch
❌ Doesn't scale for unbounded keys (millions of accounts)

### Filter? Yes
```python
.filter("transaction_type = 'CREDIT'")  # ✅ Safe to add/remove
```

### Use For
- **Small bounded aggregations** (< 100K keys)
- Counters, KPIs
- Top-N rankings
- Dashboard backing tables

### ⚠️ NOT for Large Aggregations
ถ้า target table > 1M rows → ใช้ Pattern 3 แทน

---

## Pattern 3: **foreachBatch + MERGE** ⭐ Most Flexible

### Mechanics
```python
from delta.tables import DeltaTable

def merge_to_gold(batch_df, batch_id):
    """Custom logic per micro-batch"""
    if batch_df.isEmpty():
        return                          # Handle empty batches
    
    batch_df.persist()                  # Cache for multiple actions
    
    # Partition pruning hint
    affected_keys = [r.account_id for r in 
        batch_df.select("account_id").distinct().collect()]
    
    target = DeltaTable.forName(spark, "gold.balance")
    
    (target.alias("t")
        .merge(
            batch_df.alias("s"),
            f"""t.account_id = s.account_id 
                AND t.account_id IN ({','.join(map(repr, affected_keys))})"""
        )
        .whenMatchedUpdate(set={
            "balance": "t.balance + s.amount"    # ⭐ การบวกอยู่ที่นี่
        })
        .whenNotMatchedInsert(values={
            "account_id": "s.account_id",
            "balance": "s.amount"
        })
        .execute())
    
    batch_df.unpersist()

(spark.readStream.table("bronze.transactions")
    .writeStream
    .foreachBatch(merge_to_gold)
    .option("checkpointLocation", "/ckpt/")
    .option("txnAppId", "balance_pipeline")     # Idempotency
    .trigger(processingTime="1 minute")
    .start())
```

### Pros / Cons
✅ Maximum flexibility
✅ Custom MERGE logic (upsert, arithmetic)
✅ Multi-table writes possible
✅ Production standard for unbounded keys
✅ Scales well with partitioning
❌ At-least-once (not exactly-once) — use batchId for idempotency
❌ Doesn't work with continuous mode
❌ Need persist/unpersist if multiple actions
❌ Performance tuning manual

### Idempotency Setup
```python
.option("txnAppId", "my_pipeline")
.option("txnVersion", batch_id)
# Same batchId on replay = skip duplicate write
```

### Use For
- **Production upserts** on large tables
- Running totals/balances
- SCD updates (manual)
- CDC processing
- Custom multi-table writes

---

## Pattern 4: **Delta Change Data Feed (CDF)**

### Setup
```sql
-- Enable CDF on source table
ALTER TABLE silver.policies 
SET TBLPROPERTIES (delta.enableChangeDataFeed = true);
```

### Read Changes
```python
changes = (spark.readStream
    .format("delta")
    .option("readChangeFeed", "true")
    .option("startingVersion", 100)         # Optional start point
    .table("silver.policies"))
```

### Output Schema
Each row gets extra columns:
- `_change_type`: insert | update_preimage | update_postimage | delete
- `_commit_version`: Delta version
- `_commit_timestamp`: commit time

### Pros / Cons
✅ Captures inserts, updates, deletes
✅ Native to Delta (no extra system)
✅ Downstream can react to specific change types
❌ CDF data has retention limits (cleaned by VACUUM)
❌ Storage overhead on source
❌ Need to enable BEFORE need changes

### Use For
- Source has updates (dimensions, master data)
- Downstream needs to know WHAT changed
- Audit / replication

---

## Pattern 5: **skipChangeCommits / ignoreChanges**

### When Source Has Updates But Don't Care About Changes

```python
# Newer, recommended
(spark.readStream
    .option("skipChangeCommits", "true")    # Skip non-append commits
    .table("silver.policies"))

# Older
(spark.readStream
    .option("ignoreChanges", "true")        # Process whole files even on changes
    .table("silver.policies"))
```

### Difference
| Option | Behavior |
|---|---|
| skipChangeCommits | Skip entire commit if has updates/deletes (clean) |
| ignoreChanges | Reprocess files even if only some rows changed (duplicates downstream) |

### Pros / Cons
✅ Allows streaming from updateable source
✅ skipChangeCommits is cleanest
❌ Lose data if all commits have changes
❌ Limited to scenarios where missing updates OK

### Use For
- Scenarios where missing some updates acceptable
- Append-mostly tables with occasional cleanup

---

## Pattern 6: **DLT `apply_changes`** (Declarative SCD)

### Mechanics
```python
import dlt

# Define target streaming table
dlt.create_streaming_table("silver_policy_current")

# Apply CDC changes declaratively
dlt.apply_changes(
    target="silver_policy_current",
    source="bronze_policy_cdc_events",
    keys=["policy_id"],
    sequence_by="cdc_timestamp",
    apply_as_deletes="operation = 'DELETE'",
    except_column_list=["operation", "cdc_timestamp"],
    stored_as_scd_type=1                    # 1 = current state | 2 = history
)
```

### What It Does Internally
- Reads source as stream
- Handles ordering by sequence_by
- Performs MERGE to target
- Manages SCD logic
- = wraps Pattern 3 + 4 declaratively

### Pros / Cons
✅ Most declarative
✅ SCD Type 1 OR Type 2 built-in
✅ Handles late events via sequence_by
✅ DLT manages everything
❌ Locked into DLT (can't use outside)
❌ Less control than foreachBatch
❌ Premium DLT cost

### Use For
- Dimension tables (customer, product, policy)
- Source has CDC events
- Want declarative SCD
- Using DLT for pipeline anyway

---

## Pattern 7: **DLT Materialized View**

### Mechanics
```python
@dlt.table  # Materialized view — auto-refresh
def gold_balance_summary():
    return (spark.read.table("silver.transactions")
            .groupBy("account_id")
            .agg(sum("amount").alias("balance")))
```

### How DLT Decides Refresh Strategy
- If incremental possible (simple aggs) → incremental
- If complex (windows, multi-source) → full recompute
- DLT engine decides

### Pros / Cons
✅ Most declarative
✅ DLT auto-optimizes
✅ Built-in lineage
✅ Quality checks integrated
❌ Black-box refresh logic
❌ Sometimes full recompute (expensive)
❌ DLT-only

### Use For
- Gold aggregations
- BI-facing tables
- Where you trust DLT to optimize

---

# 4. The "Running Aggregation" Problem

## Scenario
```
9:00  — Gold table: account_1 balance = 100
10:00 — Bronze receives transaction: account_1, +10
        Gold table should become: account_1 balance = 110

Question: WHERE/HOW does 100+10=110 happen?
```

## 3 Mechanisms (Different Patterns Solve Differently)

### Mechanism A: Pattern 2 (Streaming Aggregation + Complete Mode)
```
Inside Spark's State Store:
  9:00:  {account_1: 100}
  Event: +10 arrives
  10:00: {account_1: 110}    ← STATE STORE updates
  
Output mode "complete":
  → Spark REPLACES entire gold.balance table with new state
  → "110" written to disk
```

**ที่บวกเกิดที่:** Spark in-memory/RocksDB state store
**Cost:** Rewrites entire target each batch
**Scale:** Bounded keys only

### Mechanism B: Pattern 3 (foreachBatch + MERGE)
```
Gold table on disk: account_1 = 100
Bronze: +10 transaction arrives
       
foreachBatch executes:
  MERGE INTO gold.balance t
  USING batch s
  ON t.account_id = s.account_id
  WHEN MATCHED THEN 
    UPDATE SET balance = t.balance + s.amount
                         ^^^^^^^^^   ^^^^^^^^
                         Read 100   Add 10 → 110

Gold table on disk: account_1 = 110
```

**ที่บวกเกิดที่:** MERGE SQL statement, by Delta engine
**Cost:** Only affected partitions/files
**Scale:** Unlimited keys (Sin's case ✓)

### Mechanism C: Pattern 7 (DLT Materialized View)
```
DLT engine decides:
  - Incremental refresh? Add delta to existing
  - Full recompute? Rebuild from source
  
DLT abstracts the decision
```

**ที่บวกเกิดที่:** DLT engine's optimizer
**Cost:** Depends on refresh strategy
**Scale:** Depends on aggregation complexity

## Decision: เลือก Mechanism ไหน?

| Need | Use |
|---|---|
| Small bounded keys (< 100K), simple agg | Mechanism A (Pattern 2) |
| Large keys, custom logic, performance | **Mechanism B (Pattern 3)** ⭐ |
| Don't want to write code, OK with DLT | Mechanism C (Pattern 7) |

---

# 5. Concerns Matrix (Per Pattern)

| Pattern | Top Concern | Mitigation |
|---|---|---|
| 1: Direct Stream | Source must be append-only | Use skipChangeCommits or CDF |
| 2: Complete Mode | Rewrites entire target | Only for small target tables |
| 3: foreachBatch+MERGE | At-least-once only | Use txnAppId + batchId |
| 3: foreachBatch+MERGE | Multiple actions reload state | persist/unpersist |
| 3: foreachBatch+MERGE | MERGE may scan many files | Partition + cluster + key filter |
| 4: CDF | CDF data has retention | Tune `delta.changeDataFeed.retentionDuration` |
| 4: CDF | Storage overhead | Worth it for change-aware downstream |
| 5: skipChangeCommits | Loses data on update commits | Only OK if updates ignorable |
| 6: DLT apply_changes | Lock-in to DLT | Plan migration carefully |
| 7: DLT MV | Black-box refresh logic | Monitor refresh strategy |

## Universal Concerns (All Patterns)

### Checkpoint Corruption
```
Symptoms: Pipeline fails on restart
Mitigation: 
  - Backup checkpoint periodically
  - Document checkpoint location per pipeline
  - Never reuse checkpoint across pipelines
```

### Schema Evolution
```
What requires fresh checkpoint:
  - Input source type/count
  - Output sink type
  - Stateful operation schema (groupBy keys)
  - State schema

What's safe:
  - Add/remove filters
  - Change UDF logic (in mapGroupsWithState)
  - Change trigger interval
  - Change rate limits
```

### Small Files Problem
```
Symptoms: Slow queries, S3 list operations cost
Mitigation:
  - delta.autoOptimize.optimizeWrite = true
  - delta.autoOptimize.autoCompact = true
  - Scheduled OPTIMIZE
  - Liquid Clustering
```

### Backpressure
```
Symptoms: Source piles up, latency grows
Mitigation:
  - maxBytesPerTrigger / maxFilesPerTrigger
  - Scale up cluster
  - Increase trigger interval
  - Switch to availableNow + scheduled
```

---

# 6. Pattern Selection Decision Tree

```
START: Need to stream Delta → Delta
   │
   ├── Source is append-only?
   │   │
   │   ├── YES → Need aggregation?
   │   │         │
   │   │         ├── YES → Target small (< 100K rows)?
   │   │         │         ├── YES → Pattern 2 (Complete mode)
   │   │         │         └── NO  → Pattern 3 (foreachBatch+MERGE)
   │   │         │
   │   │         └── NO → Pattern 1 (Direct stream read)
   │   │
   │   └── NO (has updates/deletes)
   │       │
   │       ├── Need to know what changed?
   │       │   ├── YES → Pattern 4 (CDF)
   │       │   └── NO  → Pattern 5 (skipChangeCommits)
   │       │
   │       └── Need SCD-style update on target?
   │           ├── Using DLT? → Pattern 6 (apply_changes)
   │           └── Not DLT?  → Pattern 4 (CDF) + Pattern 3 (foreachBatch)
   │
   └── Aggregation in DLT?
       └── → Pattern 7 (Materialized View)
```

---

# 7. Pattern Combinations (Real Production)

## Production Pattern: "Customer Balance Pipeline"

Real pipeline combines **multiple patterns**:

```
Bronze (Pattern 1): Stream-read raw transactions
   │
   ↓
Silver Append (Pattern 1 + 3): 
   - Stream-read bronze
   - foreachBatch: validate + write to history
   - Same code writes to TWO targets:
     a) silver.transactions_history (append-only)
     b) silver.transactions_validated (append, partition by date)
   │
   ↓
Silver Current Balance (Pattern 3 - main mechanic):
   - Stream-read from silver.transactions_validated
   - foreachBatch + MERGE: 
     UPDATE gold.balance SET balance = balance + amount
   - Liquid clustering on account_id for pruning
   │
   ↓
Gold Customer Dim (Pattern 6 - SCD):
   - Stream-read from bronze.customer_cdc (CDF enabled)
   - dlt.apply_changes with SCD Type 2
   - Tracks history of customer changes
   │
   ↓
Gold Daily Summary (Pattern 2 - bounded agg):
   - Stream-read from gold.balance + gold.customer_dim
   - groupBy(region) — only ~50 regions = bounded
   - Complete mode to small summary table
```

## Pattern Mapping for Insurance Pipelines (AIA-style)

| Pipeline | Patterns Used |
|---|---|
| **Policy CDC ingestion** | Pattern 4 (CDF) + Pattern 6 (apply_changes SCD2) |
| **Claims streaming** | Pattern 1 (append) + Pattern 3 (MERGE to current) |
| **Customer 360** | Pattern 4 (CDF from multi sources) + Pattern 3 (custom merge) |
| **Account balance** | Pattern 3 (foreachBatch + MERGE with addition) |
| **Fraud detection** | Pattern 1 (append) + Real-time Mode + Pattern 3 (alert table) |
| **Reserve calculation** | Pattern 7 (DLT MV) for aggregations |
| **Regulatory reports** | Pattern 2 (complete mode for bounded KPIs) |

---

# 8. Trigger Modes Deep Dive

## All 4 Trigger Modes

### 1. Default (no trigger specified)
```python
.writeStream  # no .trigger()
```
- **Interval:** 500ms (default micro-batch)
- **Behavior:** As fast as previous batch completes
- **Use:** Don't use in production (uncontrolled)

### 2. processingTime
```python
.trigger(processingTime="30 seconds")
```
- **Interval:** Fixed time (e.g., 30s, 1m, 5m)
- **Behavior:** Run every X time, even if no data
- **Use:** True streaming with controlled latency

### 3. availableNow ⭐ Recommended for Most Cases
```python
.trigger(availableNow=True)
```
- **Behavior:** Process ALL available data as multiple micro-batches, then STOP
- **Use:** Scheduled near-realtime (run hourly via Workflow)

**This is the killer pattern:**
```
Databricks Workflow scheduled hourly:
  9:00 AM:
    Job starts
    Stream runs with availableNow
    Processes all new data since 8:00 AM checkpoint
    Stream terminates
    Cluster shuts down
    
  10:00 AM:
    Job starts again
    Picks up from where 9:00 left off
    Processes new data
    Terminates
```

**Pros:**
- No idle cluster cost
- Same streaming code (incremental, checkpoint)
- Easy to run on schedule

### 4. realTime (Newest, Databricks 2024+)
```python
.trigger(realTime=True)
```
- **Behavior:** True sub-second streaming (not micro-batch)
- **Latency:** <1 second (often ~300ms)
- **Use:** Sub-second fraud detection, real-time alerts
- **Cost:** Higher than micro-batch

## Trigger vs Streaming Mode Reality

```
"Streaming" doesn't always mean "always on"

Most production "streaming" pipelines = scheduled batch with streaming code
  ├── Why: Cheaper (no idle cluster)
  ├── How: availableNow + Workflow scheduler  
  └── Benefit: Same code works for true streaming if needed later
```

---

# 9. Checkpoint Mechanics

## Where Streaming "Knows" Position

```
/path/to/checkpoint/
├── offsets/                    ← Source offsets per batch
│   ├── 0                       (batch 0: started at version X)
│   ├── 1                       (batch 1: from version X to Y)
│   └── 2                       (batch 2: from version Y to Z)
├── commits/                    ← Successfully committed batches
│   ├── 0
│   └── 1                       (batch 2 not committed = retry)
├── sources/                    ← Per-source metadata
│   └── 0/
│       └── (RocksDB for Auto Loader)
├── state/                      ← Stateful op data
│   └── 0/
│       ├── _metadata
│       └── 0.delta             (RocksDB checkpoint)
└── metadata                    ← Query identity (id, run_id)
```

## How Each Source Tracks Position

### Delta Source
```
Tracks: Last processed Delta table version
On restart: Read offsets/<latest>, find version
Query Delta log: "Any versions after that?"
Process: Only new files since that version
```

### Kafka Source
```
Tracks: (topic, partition, offset) per source
On restart: Resume from last committed offset per partition
```

### Auto Loader (S3)
```
Tracks: RocksDB of all files seen
On restart: List S3 path, exclude files already in RocksDB
```

## Checkpoint Rules

### Same checkpoint = same query
- Identity of stream
- Don't reuse checkpoint across pipelines
- Move stream code → must use same checkpoint location

### Cannot change without fresh checkpoint:
- Number/type of input sources
- Subscribed Kafka topics / Auto Loader paths
- Stateful operation schema (groupBy keys, aggregates)
- Output sink type
- State schema

### Safe to change:
- Filters (add/remove)
- Rate limits (maxFilesPerTrigger, etc.)
- Trigger intervals
- UDF logic
- Code refactoring (if logic equivalent)

## Recovery Scenarios

### Scenario 1: Job crashes mid-batch
```
Last committed: batch 5
Crashed during: batch 6 (no commit)
On restart:
  - Read offsets/6 (knows where batch 6 was)
  - Re-process batch 6
  - Idempotency (txnAppId/batchId) prevents duplicate writes
```

### Scenario 2: Cluster terminates (availableNow)
```
Job completes normally
Checkpoint state preserved
Next run: pick up from last successful batch
```

### Scenario 3: Checkpoint corruption
```
Symptoms: Mysterious failures on restart
Recovery:
  Option A: Restore from backup checkpoint
  Option B: Delete checkpoint + reprocess (if idempotent)
  Option C: New checkpoint + manual catch-up
```

---

# 10. Production Code Templates

## Template 1: Bronze → Silver (Append Stream)

```python
def bronze_to_silver():
    """Pattern 1: Direct streaming read for append-only"""
    
    # Read from bronze
    df = (spark.readStream
        .table("bronze.events")
        .filter("event_type IN ('CLICK', 'VIEW', 'PURCHASE')")  # Safe filter
        .filter("event_timestamp >= '2026-01-01'"))             # Safe filter
    
    # Validate + enrich
    validated = (df
        .withColumn("event_date", to_date("event_timestamp"))
        .withColumn("ingestion_ts", current_timestamp()))
    
    # Write
    (validated.writeStream
        .format("delta")
        .partitionBy("event_date")
        .option("checkpointLocation", "/ckpt/silver_events/")
        .trigger(availableNow=True)
        .toTable("silver.events"))
```

## Template 2: Bronze → Gold (foreachBatch + MERGE with Running Total)

```python
from delta.tables import DeltaTable
from pyspark.sql.functions import col

def transactions_to_balance():
    """Pattern 3: foreachBatch + MERGE for running balance"""
    
    def merge_to_balance(batch_df, batch_id):
        """Update balance for each affected account"""
        if batch_df.isEmpty():
            return
        
        batch_df.persist()  # Cache for multiple operations
        
        # Aggregate batch first (multiple txns per account in same batch)
        batch_agg = (batch_df
            .groupBy("account_id")
            .agg(sum("amount").alias("delta_amount")))
        
        # Get affected accounts for pruning hint
        affected = [r.account_id for r in 
            batch_agg.select("account_id").collect()]
        
        # MERGE with arithmetic
        target = DeltaTable.forName(spark, "gold.balance")
        
        partition_filter = f"t.account_id IN ({','.join(map(repr, affected))})"
        
        (target.alias("t")
            .merge(
                batch_agg.alias("s"),
                f"t.account_id = s.account_id AND {partition_filter}"
            )
            .whenMatchedUpdate(set={
                "balance": "t.balance + s.delta_amount",
                "last_updated": "current_timestamp()"
            })
            .whenNotMatchedInsert(values={
                "account_id": "s.account_id",
                "balance": "s.delta_amount",
                "last_updated": "current_timestamp()"
            })
            .execute())
        
        batch_df.unpersist()
    
    # Stream
    (spark.readStream
        .table("silver.transactions")
        .writeStream
        .foreachBatch(merge_to_balance)
        .option("checkpointLocation", "/ckpt/balance/")
        .option("txnAppId", "balance_pipeline")     # Idempotency
        .trigger(availableNow=True)                  # Scheduled
        .start())
```

## Template 3: SCD Type 2 with DLT apply_changes

```python
import dlt

# Create target streaming table
dlt.create_streaming_table(
    "silver.policy_history",
    comment="Policy dimension with full history"
)

# Apply CDC changes from bronze
dlt.apply_changes(
    target="silver.policy_history",
    source="bronze.policy_cdc",
    keys=["policy_id"],
    sequence_by="cdc_timestamp",
    apply_as_deletes="operation = 'DELETE'",
    except_column_list=["operation", "cdc_timestamp", "_metadata"],
    stored_as_scd_type=2,                          # ⭐ History tracked
    track_history_column_list=["status", "premium", "coverage"]
)
```

## Template 4: Bounded Aggregation (Complete Mode)

```python
def daily_summary():
    """Pattern 2: Complete mode for bounded aggregation"""
    
    summary = (spark.readStream
        .table("silver.transactions")
        .filter("amount > 0")
        .withColumn("txn_date", to_date("transaction_time"))
        .groupBy("txn_date", "region")              # ~50 regions × 365 = 18K rows MAX
        .agg(
            sum("amount").alias("total_amount"),
            count("*").alias("txn_count")))
    
    (summary.writeStream
        .outputMode("complete")
        .option("checkpointLocation", "/ckpt/daily_summary/")
        .trigger(processingTime="5 minutes")
        .toTable("gold.daily_summary"))
```

## Template 5: Combined Patterns Pipeline

```python
# === BRONZE → SILVER (Pattern 1) ===
def claims_bronze_to_silver():
    df = (spark.readStream
        .table("bronze.claims_cdc")
        .filter("operation IN ('INSERT', 'UPDATE', 'DELETE')"))
    
    (df.writeStream
        .partitionBy("claim_date")
        .option("checkpointLocation", "/ckpt/silver_claims/")
        .trigger(availableNow=True)
        .toTable("silver.claims_history"))

# === SILVER → SILVER CURRENT (Pattern 6 - DLT SCD1) ===
@dlt.create_streaming_table("silver.claims_current")
def claims_current():
    dlt.apply_changes(
        target="silver.claims_current",
        source="silver.claims_history",
        keys=["claim_id"],
        sequence_by="cdc_timestamp",
        apply_as_deletes="operation = 'DELETE'",
        stored_as_scd_type=1)

# === SILVER CURRENT → GOLD AGGREGATES (Pattern 3 - MERGE) ===
def claims_to_aggregates():
    def merge_aggregates(batch_df, batch_id):
        if batch_df.isEmpty():
            return
        
        agg = (batch_df
            .groupBy("policy_id")
            .agg(
                count("*").alias("delta_count"),
                sum("amount").alias("delta_amount")))
        
        # MERGE with addition
        target = DeltaTable.forName(spark, "gold.policy_claim_summary")
        (target.alias("t")
            .merge(agg.alias("s"), "t.policy_id = s.policy_id")
            .whenMatchedUpdate(set={
                "total_claims": "t.total_claims + s.delta_count",
                "total_amount": "t.total_amount + s.delta_amount"
            })
            .whenNotMatchedInsert(values={
                "policy_id": "s.policy_id",
                "total_claims": "s.delta_count",
                "total_amount": "s.delta_amount"
            })
            .execute())
    
    (spark.readStream
        .format("delta")
        .option("readChangeFeed", "true")            # Pattern 4 - CDF source
        .table("silver.claims_current")
        .filter("_change_type IN ('insert', 'update_postimage')")
        .writeStream
        .foreachBatch(merge_aggregates)
        .option("checkpointLocation", "/ckpt/gold_summary/")
        .trigger(availableNow=True)
        .start())

# === GOLD → BOUNDED KPI (Pattern 2 - Complete Mode) ===
def kpi_summary():
    (spark.readStream
        .table("gold.policy_claim_summary")
        .groupBy("product_line")                    # bounded ~10 lines
        .agg(
            sum("total_amount").alias("total_payout"),
            sum("total_claims").alias("claim_count"))
        .writeStream
        .outputMode("complete")
        .option("checkpointLocation", "/ckpt/kpi/")
        .trigger(processingTime="10 minutes")
        .toTable("gold.kpi_by_product"))
```

---

# 🎯 Summary: Pattern Selection Cheat Sheet

| Scenario | Pattern(s) | Note |
|---|---|---|
| Append events → silver | 1 | Filter safe |
| Append events → multiple sinks | 1 + 3 | foreachBatch for multi-write |
| Small aggregation (< 100K keys) | 2 | Complete mode OK |
| Large aggregation / running total | **3** ⭐ | MERGE with arithmetic |
| CDC source dimension → SCD1 | 4 + 3 OR 6 | DLT if available |
| CDC source dimension → SCD2 | 4 + 3 OR 6 | DLT apply_changes type=2 |
| Updateable source, ignore changes | 5 | skipChangeCommits |
| Multi-step DLT aggregations | 7 | DLT MV |

## Common Production Combination

```
Bronze (raw) ─Pattern 1─→ Silver History (append)
                              │
                              ↓ Pattern 4 (CDF) + Pattern 3 (MERGE)
                        Silver Current (latest state)
                              │
                              ↓ Pattern 3 (MERGE with arithmetic)
                        Gold Aggregates (running totals)
                              │
                              ↓ Pattern 2 (Complete Mode)
                        Gold KPIs (small bounded)
```

---

# 🚨 Critical Gotchas Summary

1. **Streaming source ไม่ scan whole table** — ใช้ checkpoint ทุก source
2. **Pattern 2 ปัญหาคือ WRITE side** (complete = rewrite target)
3. **Pattern 3 ใช้ at-least-once** — ต้อง txnAppId/batchId for idempotency
4. **foreachBatch ไม่ work กับ continuous mode**
5. **เปลี่ยน trigger interval safe** แต่เปลี่ยน source/sink/state ต้อง fresh checkpoint
6. **MERGE pruning critical** — ใส่ partition/cluster filter
7. **availableNow + Workflow** = best cost/latency balance
8. **CDF retention limited** — VACUUM ลบได้
9. **Same checkpoint = same query identity** — ห้าม reuse
10. **Empty batches เกิดได้** — handle ใน foreachBatch

---

**Document version:** v1
**Sources:** Databricks docs (AWS), Apache Spark docs, verified
**For:** AIA DE on Databricks AWS — production reference

