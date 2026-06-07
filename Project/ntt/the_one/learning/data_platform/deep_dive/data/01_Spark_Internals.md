# Apache Spark — Internals Deep Dive

> Catalyst, Tungsten, AQE, Shuffle, Memory Management
> สิ่งที่ทำให้ Spark performance ดีหรือพัง — รู้แล้ว tune ได้ตรงจุด

---

## 1. Spark Execution Model — Big Picture

### Layers of Spark

```
┌─────────────────────────────────────────────────────────┐
│   USER CODE (DataFrame/SQL/Dataset API)                 │
└──────────────────────┬──────────────────────────────────┘
                       │ → Logical Plan
┌──────────────────────▼──────────────────────────────────┐
│   CATALYST OPTIMIZER (logical → physical)               │
│   • Analyzer • Logical Optimizer • Physical Planner     │
└──────────────────────┬──────────────────────────────────┘
                       │ → Physical Plan (RDD DAG)
┌──────────────────────▼──────────────────────────────────┐
│   TUNGSTEN EXECUTION ENGINE                             │
│   • Off-heap memory • Code gen • Vectorization          │
└──────────────────────┬──────────────────────────────────┘
                       │ → Execution
┌──────────────────────▼──────────────────────────────────┐
│   ADAPTIVE QUERY EXECUTION (runtime adjust)             │
│   • Dynamic partition coalesce • Skew handling • Joins  │
└─────────────────────────────────────────────────────────┘
```

### Job → Stage → Task

```
1 Job (= 1 action like .count())
   ↓ split by shuffles
N Stages
   ↓ each partition = 1 task
M Tasks (executed in parallel on executors)
```

**กฎสำคัญ**:
- Stage boundary = shuffle (wide dependency)
- Task = 1 partition × 1 stage
- Executor cores = max parallel tasks

---

## 2. Catalyst Optimizer — How Spark "Thinks"

### 4 Phases

```
SQL/DataFrame
    ↓
Phase 1: ANALYZER
    • Resolve column names
    • Validate types
    • Bind to catalog
    ↓ Resolved Logical Plan
Phase 2: LOGICAL OPTIMIZER
    • Predicate pushdown
    • Constant folding
    • Column pruning
    • Reorder joins
    ↓ Optimized Logical Plan
Phase 3: PHYSICAL PLANNER
    • Choose physical operators
    • Cost-based join selection
    ↓ Physical Plan
Phase 4: CODE GENERATION (Tungsten)
    • Whole-stage codegen
    • Compile to JVM bytecode
    ↓ RDD execution
```

### Logical Optimizer — Key Rules

#### Rule 1: Predicate Pushdown
```sql
-- Before optimization
SELECT * FROM (
    SELECT * FROM events
) t WHERE event_date = '2026-05-01'

-- After optimization (filter pushed down to source)
SELECT * FROM events WHERE event_date = '2026-05-01'
-- Reads only matching partitions, not all data
```

#### Rule 2: Column Pruning
```sql
-- Before
SELECT name FROM (SELECT * FROM users)

-- After (only read 'name' from Parquet)
SELECT name FROM users
```

#### Rule 3: Constant Folding
```sql
-- Before
SELECT * FROM events WHERE year = 2025 + 1

-- After
SELECT * FROM events WHERE year = 2026
```

#### Rule 4: Join Reorder (CBO)
```sql
-- Bad order: large × large × small = huge intermediate
A(1B rows) JOIN B(1B rows) JOIN C(1K rows)

-- CBO reorders to:
A JOIN C JOIN B  -- small first reduces intermediate size
```

### Inspect Catalyst plan

```python
df = spark.sql("...complex query...")

# See all 4 plans
df.explain(extended=True)

# Just final
df.explain()

# Cost-based plan (with statistics)
df.explain("cost")
```

### Plan output meaning

```
== Parsed Logical Plan ==          # Step 1: just parsed
'Filter ('amount > 100)
+- 'UnresolvedRelation `orders`

== Analyzed Logical Plan ==        # Step 2: types resolved
Filter (amount#5 > 100)
+- SubqueryAlias orders
   +- Relation[id#3, amount#5]

== Optimized Logical Plan ==       # Step 3: rules applied
Filter (amount#5 > 100)
+- Relation[id#3, amount#5]
                                    # column 'name' pruned!
== Physical Plan ==                # Step 4: ready to execute
*(1) Filter (amount#5 > 100)
+- *(1) FileScan parquet [id#3,amount#5]
        PushedFilters: [GreaterThan(amount,100)]
                                    # filter pushed to Parquet!
```

**Note**: `*(1)` = whole-stage codegen group 1

---

## 3. Tungsten — How Spark Actually Runs Fast

### Problem ที่ Tungsten แก้

JVM problems:
- **Object overhead**: Java object = header + padding (~16 bytes overhead even for small data)
- **GC pressure**: short-lived objects → GC pauses
- **Cache miss**: scattered objects → poor CPU cache utilization
- **Boxing**: primitives → boxed objects

### 3 ส่วนของ Tungsten

#### Part 1: Off-Heap Memory Management

```
JVM Heap (slow GC):     [obj1][obj2][obj3]...
                         ↓ Tungsten replaces with
Off-Heap (manual mgmt):  [raw bytes...]
```

- ใช้ `sun.misc.Unsafe` API
- Spark manage memory เอง ไม่ผ่าน GC
- Configurable: `spark.memory.offHeap.enabled=true`

#### Part 2: Cache-Aware Computation

```python
# Internal: BinaryFormat (sorted by cache lines)
# Numbers stored contiguously → CPU prefetch works
# Arrays of structs → struct of arrays
```

#### Part 3: Whole-Stage Code Generation

**Without codegen** (interpret):
```
For each row:
  Call filter operator (virtual call)
    Call expression evaluator (virtual call)
      Compare amount > 100
  Call project operator (virtual call)
  ...
```
50% time = virtual call overhead

**With codegen** (compile to bytecode):
```java
// Spark generates this Java code at runtime, compiles, runs
while (row_iter.hasNext()) {
    InternalRow row = row_iter.next();
    long amount = row.getLong(5);
    if (amount > 100) {
        // emit row directly, no virtual calls
        result.append(row);
    }
}
```

10x speedup typical for simple filter-project queries

### Verify codegen working

```python
df.explain()
# Look for *(N) prefix = codegen group
# Operators in same * group = fused into one function

# Output example:
# *(1) Project [id, amount]
# +- *(1) Filter amount > 100
# +- *(1) FileScan
# Same *(1) = fused = fast
```

---

## 4. Adaptive Query Execution (AQE) — Runtime Smart

### What AQE Does

Catalyst optimizes BEFORE seeing data → uses statistics
AQE optimizes DURING execution → uses real runtime stats

### 3 Main Features

#### Feature 1: Dynamic Partition Coalesce

**Problem**: After shuffle, partitions become uneven
- Some partitions: 100 KB (too small, overhead)
- Some partitions: 500 MB (just right)
- Some partitions: 5 GB (skew, slow)

**AQE solution**: merge small partitions automatically
```
Before AQE:  [100KB] [200KB] [500MB] [100KB] [50KB]
After AQE:   [400KB merged]   [500MB] [50KB]
```

```python
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "128MB")
```

#### Feature 2: Skew Join Handling

**Problem**: Sort-merge join with skewed key
```
Key 'user_42' = 100M rows (other keys avg 1K)
1 task takes 1 hour, others take 1 second
```

**AQE solution**: detect + split skewed partitions
```
Skewed partition for key 'user_42'
   → split into 10 sub-partitions
   → replicate other side accordingly
   → 10 tasks in parallel instead of 1
```

```python
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
```

#### Feature 3: Dynamic Join Selection

**Problem**: At plan time, don't know join build size
- Plan as sort-merge (safe but slow)
- After scan, realize one side is small

**AQE solution**: switch to broadcast join
```
Plan time:    SortMergeJoin (default)
After scan:   "Side B is only 50MB → switch to BroadcastHashJoin"
```

10-100x speedup when applicable

### Enable everything (Spark 3.0+)

```python
spark.conf.set("spark.sql.adaptive.enabled", "true")  # default Spark 3.2+
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.localShuffleReader.enabled", "true")
```

---

## 5. Shuffle — The Bottleneck

### What is Shuffle

Wide dependency = data must redistribute across partitions

```
Stage 1 (no shuffle):     [P1][P2][P3][P4]
                           ↓ groupBy('country')
                          shuffle (network!)
Stage 2 (after shuffle):  [Thai][US][JP][...]
```

### Why Shuffle is Expensive

- **Disk I/O**: write shuffle files
- **Network I/O**: fetch from other executors
- **Serialization**: convert to/from bytes
- **Memory**: buffer + sort

Typical: shuffle = 60-80% of job time for analytical queries

### Shuffle Implementations

#### Sort-based Shuffle (default)
```
Map task: write sorted file per reducer
Reduce task: fetch + merge from all map tasks
```

#### Push-based Shuffle (Spark 3.2+)
```
Map task: push directly to reducer (don't wait)
Reduce task: receives pre-aggregated data
```
- Reduces small file problem
- Better with cloud storage

```python
spark.conf.set("spark.shuffle.push.enabled", "true")
```

### Optimization Patterns

#### Pattern 1: Avoid shuffle if possible
```python
# Bad
df.groupBy("user_id").agg(...)  # shuffle by user_id

# Better (if pre-partitioned by user_id)
df.repartition("user_id").groupBy("user_id").agg(...)  # no shuffle
```

#### Pattern 2: Broadcast small tables
```python
# Auto-broadcast if < threshold (default 10MB)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "100MB")

# Manual
from pyspark.sql.functions import broadcast
df_large.join(broadcast(df_small), "id")
```

#### Pattern 3: Repartition strategically
```python
# Before expensive operation, ensure good partitioning
df = df.repartition(200, "user_id")  # cluster by user_id
df.groupBy("user_id").count()  # local groupby = no shuffle
```

---

## 6. Memory Management

### Spark Memory Layout

```
┌─────────────────────────────────────────────────┐
│         JVM Heap                                │
│  ┌─────────────────────────────────────────┐    │
│  │ Reserved (300 MB) - system               │    │
│  ├─────────────────────────────────────────┤    │
│  │ User Memory (40%)                        │    │
│  │ - User data structures                   │    │
│  │ - Spark internal metadata                │    │
│  ├─────────────────────────────────────────┤    │
│  │ Spark Memory (60%)                       │    │
│  │  ┌──────────────────────────┐            │    │
│  │  │ Storage (cached blocks)  │            │    │
│  │  │ Execution (shuffle/join) │            │    │
│  │  │ Unified, can borrow      │            │    │
│  │  └──────────────────────────┘            │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

```python
# Settings
spark.executor.memory = 8g          # total
spark.memory.fraction = 0.6         # spark
spark.memory.storageFraction = 0.5  # within spark, storage
```

### Off-Heap (Tungsten)

```python
spark.conf.set("spark.memory.offHeap.enabled", "true")
spark.conf.set("spark.memory.offHeap.size", "4g")
# Allows execution > heap size
# No GC pressure
```

### Common OOM Causes

| Symptom | Cause | Fix |
|---|---|---|
| Driver OOM | `collect()` too much data | Use `take()`, write to file |
| Executor OOM during shuffle | Skewed partitions | Enable skew handling, repartition |
| Executor OOM during join | Build side too big | Don't broadcast, increase memory |
| Executor OOM gradually | Memory leak in UDF | Profile, use built-in functions |

---

## 7. Performance Tuning Checklist

### Configuration ที่ควรเปิด default

```python
spark = SparkSession.builder \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \
    .config("spark.sql.autoBroadcastJoinThreshold", "100MB") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.sql.files.maxPartitionBytes", "128MB") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.parquet.enableVectorizedReader", "true") \
    .config("spark.memory.offHeap.enabled", "true") \
    .config("spark.memory.offHeap.size", "4g") \
    .getOrCreate()
```

### Top 10 anti-patterns

1. **Using collect() on large DataFrame** → OOM driver
2. **`select("*")`** → reads unused columns
3. **UDF when built-in exists** → no codegen
4. **Repartition before write without need** → unnecessary shuffle
5. **Cache without using cached data** → wastes memory
6. **`distinct()` followed by `count()`** → use `countDistinct()`
7. **Multiple `groupBy` chains** → single multi-agg
8. **Cartesian join unintentional** → set `spark.sql.crossJoin.enabled=false`
9. **Broadcasting large table** → fails or slow
10. **No partitioning on write** → file proliferation

### Read efficiency

```python
# Bad: scans all partitions
spark.read.parquet("s3://bucket/data/").filter("date='2026-05-01'")

# Good: partition discovery + pushdown
spark.read.parquet("s3://bucket/data/")  # auto-detect partitions
    .filter("date='2026-05-01'")  # pruned to one partition

# Best: partition + cluster
# Reads only specific files based on stats
```

---

## 8. Spark + Iceberg Specific

### Iceberg Optimizations on Spark

```python
# Reading Iceberg
df = spark.read.format("iceberg").load("warehouse.events")
    .filter("date = '2026-05-01'")
# Iceberg metadata pruning: only reads relevant manifests
# Partition pruning at metadata level

# Time travel
df = spark.read.format("iceberg") \
    .option("snapshot-id", "1234567890") \
    .load("warehouse.events")
```

### Hidden partitioning (Iceberg's killer feature)

```sql
-- Iceberg auto-partition by transformation
CREATE TABLE events (...)
PARTITIONED BY (days(event_time))

-- Query without thinking about partition column
SELECT * FROM events WHERE event_time > '2026-05-01'
-- Iceberg + Spark know this maps to days(event_time) partition
```

---

## 9. Debugging Slow Spark Jobs

### Step 1: Check Spark UI
- **Stages tab**: which stages took longest?
- **Tasks**: skew? (max time / avg time)
- **Shuffle**: how much shuffled?

### Step 2: Common Issues

| Symptom | Diagnosis | Fix |
|---|---|---|
| Few tasks > 80% of time | Skew | Enable AQE skew handling, salting |
| Lots of small tasks | Too many partitions | Coalesce, increase partition size |
| GC time > 10% | Memory pressure | More memory, off-heap |
| Spill to disk | Memory not enough | Repartition, more memory |
| Shuffle > 50% time | Bad join order/partition | Broadcast, repartition strategically |

### Step 3: Read explain plan

```python
df.explain("formatted")
```

Look for:
- `BroadcastHashJoin` good for small × large
- `SortMergeJoin` good for large × large
- `BroadcastNestedLoopJoin` BAD usually
- Number of shuffle exchanges
- Pushed filters / column pruning

---

## 10. Cheat Sheet

### Q: "Why is Spark slow?"
> "3 main reasons: bad shuffle (skew, too much), bad memory (OOM, GC), missing optimizations (no codegen, broadcast, AQE)
> Fix order: enable AQE → enable broadcast → fix skew → tune memory"

### Q: "Catalyst vs AQE?"
> "Catalyst = optimize BEFORE running (uses table statistics)
> AQE = optimize DURING running (uses runtime stats)
> Both run together, AQE adjusts what Catalyst couldn't predict"

### Q: "When does whole-stage codegen NOT happen?"
> "When operators can't be fused: Python UDFs (need PySpark serialization), unsupported expressions
> Verify with `*(N)` prefix in plan — if missing, codegen disabled for that op"

### Q: "Sort-merge vs Broadcast join?"
> "Broadcast: small × large (< 10-100MB), copy small to all executors, no shuffle
> Sort-merge: large × large, both sides shuffle by join key, sort, merge
> AQE auto-switches when possible"

---

## Sources

- [Apache Spark Performance Tuning: 7 Optimization Tips (2026)](https://www.flexera.com/blog/finops/spark-performance-tuning/)
- [Spark Catalyst Pipeline: A Deep Dive](https://www.unraveldata.com/resources/catalyst-analyst-a-deep-dive-into-sparks-optimizer/)
- [Adaptive Query Execution (AQE) in Apache Spark 4.0](https://medium.com/@goyalarchana17/adaptive-query-execution-aqe-in-apache-spark-4-0-revolutionizing-query-optimization-be107db67493)
- [Spark Tungsten Optimization](https://www.sparkcodehub.com/spark/performance/tungsten-optimization)
- [Spark working internals](https://anhcodes.dev/blog/tune-spark/)
