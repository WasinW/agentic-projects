# Discussion: BQ to Parquet Export Best Practices -- No Dup, Cost Control, Fixed File Count

**Date**: 2026-04-05
**Status**: open
**Initiated by**: architect-solution
**Participants**: architect-solution, architect-cloud, architect-data

---

## Context

Two production pipelines need BQ -> GCS Parquet export:

| Pipeline | Frequency | Data Size | Columns | Current State |
|----------|-----------|-----------|---------|---------------|
| customer-svoc-interim | Monthly | ~180 GB/month | 280 (all STRING) | **FAILED** -- OOM after 9 hrs |
| backward-compatible-collector | Daily | Variable (small-medium) | Variable per table | At risk -- same `num_shards` pattern |

**Core problem**: Dataflow + `WriteToParquet(num_shards=15)` triggers `GroupByKey` that buffers all data per shard in memory. For 180 GB / 15 shards = 12 GB raw per shard, ~60 GB Python heap per shard. Workers OOM.

**Requirements**:
1. No duplicate data (exactly-once output)
2. Cost control (no redundant BQ scans on retry/re-run)
3. Controllable file count (10-20 files preferred)
4. Reliable for both large (180 GB) and small (daily slices) datasets

**Related discussion**: `2026-04-05_svoc-parquet-export-failure.md` (root cause analysis + initial options)

---

## Findings

### architect-solution says:

#### 1. Beam/Dataflow Best Practices for BQ Read

**ReadFromBigQuery has 3 methods:**

| Method | How It Works | Cost | Best For |
|--------|-------------|------|----------|
| `EXPORT` (default) | BQ exports to temp Avro/JSON on GCS, workers read from GCS | BQ export: **FREE**. GCS temp storage: minimal. Worker compute: Dataflow pricing. | Large tables, cost-sensitive |
| `DIRECT_READ` | Streams rows via BQ Storage Read API | **$1.10/TB** read. No temp files. | Medium tables needing speed |
| `STORAGE_READ_API` | Same as DIRECT_READ (alias in newer SDK) | Same as DIRECT_READ | Same |

**Key insight**: The EXPORT method is free for BQ reads (export is not charged), but slow (~30+ min for 180 GB export step alone). DIRECT_READ is faster but costs $1.10/TB. Neither affects the write-side OOM.

**Dedup guarantee in Batch mode:**
- Beam batch mode provides **exactly-once processing** for deterministic sources
- `ReadFromBigQuery` in batch mode creates a snapshot of the query result -- the source is frozen at query time
- Within a single pipeline run, no duplicates from retry/bundle restart (Beam replays from the same snapshot)
- **Cross-run risk**: If pipeline fails and re-runs, the snapshot is different (table may have changed). Mitigation: use `FOR SYSTEM_TIME AS OF` or temp table.

#### 2. Deduplication Strategies (3 Layers)

**Layer 1: Read-side dedup (snapshot isolation)**

```sql
-- Option A: BQ time-travel snapshot (free, up to 7 days)
SELECT * FROM `project.dataset.table`
FOR SYSTEM_TIME AS OF TIMESTAMP('2026-04-05T00:00:00Z')

-- Option B: Temp table pattern
-- Query once -> temp table (TTL 24h) -> read from temp table on retry
CREATE OR REPLACE TABLE `project.dataset._temp_export_20260405`
OPTIONS(expiration_timestamp=TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR))
AS SELECT * FROM `project.dataset.source_table`;
```

**Why this matters**: If pipeline fails at write step and re-runs, the re-read hits the same snapshot. No cost for re-query (temp table) or guaranteed consistent data (time-travel).

**Layer 2: Write-side dedup (idempotent output)**

| Strategy | How | Guarantee |
|----------|-----|-----------|
| Deterministic file names | `shard-00000-of-00015.parquet` | Overwrite = replace, no extra files |
| Atomic directory swap | Write to `tmp/` -> verify -> rename to `final/` | All-or-nothing |
| `EXPORT DATA ... overwrite=true` | BQ native | Atomic by design |
| GCS versioning OFF + overwrite | Default GCS behavior | Latest write wins |

**Layer 3: Post-write verification**

```python
# After write completes:
# 1. Count files
files = gcs_client.list_blobs(bucket, prefix="export/svoc/202604/")
assert len(files) == expected_file_count

# 2. Count rows
total_rows = sum(pq.read_metadata(f).num_rows for f in files)
assert total_rows == source_row_count

# 3. Spot-check schema
schema = pq.read_schema(files[0])
assert set(schema.names) == expected_columns
```

#### 3. Cost Analysis Deep Dive

**Per-run cost for 180 GB SVOC export:**

| Approach | BQ Read Cost | Compute Cost | GCS Storage | Total | On Retry |
|----------|-------------|--------------|-------------|-------|----------|
| EXPORT DATA | $0.00 (export free) | $0.00 | ~$0.004 | **~$0.004** | Same |
| BQ query + EXPORT DATA | $1.125 (query) | $0.00 | ~$0.004 | **~$1.13** | Query re-runs = $1.125 more |
| BQ query + temp table + EXPORT DATA from temp | $1.125 (first) | $0.00 | ~$0.008 | **~$1.13** | Retry from temp = FREE |
| Dataflow EXPORT method | $0.00 (BQ export) | ~$8-20 (workers) | ~$0.004 | **~$8-20** | Full re-run |
| Dataflow DIRECT_READ | $0.198 (Storage API) | ~$8-20 | $0.00 | **~$8-20** | API re-read = $0.198 more |
| Cloud Run + BQ Storage API | $1.125 (query) + $0.198 (read) | ~$0.02 | ~$0.004 | **~$1.35** | Re-run = $1.35 |
| Cloud Run + temp table + Storage API | $1.125 (first query) | ~$0.02 | ~$0.008 | **~$1.16** | Retry from temp = $0.22 |

**Pricing reference (2026 GCP):**
- BQ on-demand query: $6.25/TB scanned
- BQ Storage Read API: $1.10/TB read
- BQ EXPORT DATA: FREE (no query charge, no export charge)
- BQ EXPORT DATA with SELECT transform: $6.25/TB query charge
- GCS storage: $0.020/GB/month (standard)
- Dataflow batch: $0.056/vCPU-hr + $0.003557/GB-hr
- Cloud Run: $0.00002400/vCPU-second + $0.00000250/GiB-second

**Critical cost distinction for EXPORT DATA:**

```sql
-- FREE: Direct table export (no query charge)
EXPORT DATA OPTIONS(...) AS
SELECT * FROM `project.dataset.table`

-- $6.25/TB: Export with transformation/filter (counts as query)
EXPORT DATA OPTIONS(...) AS
SELECT col1, col2, UPPER(col3) FROM `project.dataset.table`
WHERE date > '2026-01-01'
```

If the SVOC export uses `SELECT *` without transformation, it is truly free. If it renames columns (`SELECT col AS alias`), it may incur query cost. **Verify with dry-run.**

#### 4. Temp Table Pattern (Best Practice for Retry Safety)

```python
from google.cloud import bigquery

client = bigquery.Client(project="the1-insight-prod")

# Step 1: Create temp table (one-time cost)
temp_table_id = f"the1-insight-prod._temp.svoc_export_{run_date}"
job_config = bigquery.QueryJobConfig(
    destination=temp_table_id,
    write_disposition="WRITE_TRUNCATE",
)
# Add TTL
client.query(
    f"""CREATE OR REPLACE TABLE `{temp_table_id}`
    OPTIONS(expiration_timestamp=TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR))
    AS SELECT * FROM `the1-insight-prod.refined.full_customer_svoc_ingt`""",
).result()

# Step 2: Export from temp table (free, retryable)
client.query(f"""
    EXPORT DATA OPTIONS(
        uri='gs://bucket/export/svoc/{run_date}/*.parquet',
        format='PARQUET', overwrite=true, compression='SNAPPY'
    ) AS SELECT * FROM `{temp_table_id}`
""").result()

# Step 3: Verify
# ...count files, count rows, check schema...
```

**Benefits:**
- Query cost paid once ($1.125 for 180 GB)
- EXPORT DATA from temp table is free (SELECT * = no transform)
- Retry/re-run reads same frozen snapshot at zero cost
- TTL auto-cleans temp table after 24 hours

---

### architect-cloud says:

#### 5. Exactly-Once Write Guarantees by Approach

| Approach | Write Atomicity | Failure Mode | Recovery | Duplicate Risk |
|----------|----------------|--------------|----------|----------------|
| **EXPORT DATA (overwrite=true)** | Atomic -- BQ writes all files or none | BQ handles retry internally | Re-run overwrites same path | **NONE** |
| **Beam WriteToParquet (num_shards=0)** | Per-bundle atomic (temp file -> rename) | Partial files possible on worker crash | Re-run creates new files alongside old | **MEDIUM** (orphan files from failed run) |
| **Beam WriteToParquet (num_shards=N)** | Same as above + GBK ensures all data per shard | Same + OOM risk | Same + OOM on retry | **MEDIUM** + OOM |
| **Cloud Run + PyArrow writers** | Application-managed | Partial files if process dies mid-write | Application must clean up + retry | **LOW** (with temp dir pattern) |

**Best pattern for Cloud Run + PyArrow (idempotent write):**

```python
import pyarrow.parquet as pq
from gcsfs import GCSFileSystem
import uuid

fs = GCSFileSystem()
run_id = f"{run_date}_{uuid.uuid4().hex[:8]}"
temp_dir = f"gs://bucket/export/_tmp/{run_id}/"
final_dir = f"gs://bucket/export/svoc/{run_date}/"

# Write to temp directory
writers = []
for i in range(num_files):
    path = f"{temp_dir}shard-{i:05d}-of-{num_files:05d}.parquet"
    writers.append(pq.ParquetWriter(path, schema=schema, compression='snappy',
                                     filesystem=fs))

# ... write data to writers ...

for w in writers:
    w.close()

# Verify temp directory
temp_files = fs.ls(temp_dir)
assert len(temp_files) == num_files
total_rows = sum(pq.read_metadata(f, filesystem=fs).num_rows for f in temp_files)
assert total_rows == expected_rows

# Atomic swap: delete final dir, copy temp -> final
if fs.exists(final_dir):
    fs.rm(final_dir, recursive=True)
for f in temp_files:
    fs.cp(f, final_dir + f.split("/")[-1])

# Cleanup temp
fs.rm(temp_dir, recursive=True)
```

**Note**: GCS does not have true atomic directory rename. The copy loop is not atomic. For strict atomicity, use a manifest file pattern:

```python
# Write manifest LAST (acts as commit marker)
manifest = {"files": file_list, "total_rows": total_rows, "checksum": sha256}
fs.write_text(f"{final_dir}_SUCCESS", json.dumps(manifest))

# Downstream reads: check _SUCCESS file exists before processing
```

#### 6. File Count Control -- The Complete Picture

**Why fixed file count matters (or doesn't):**

| Consumer | File Count Requirement | Reason |
|----------|----------------------|--------|
| S3 downstream (AWS) | Usually doesn't care | S3 prefix listing is cheap |
| Spark/EMR readers | Prefers files ~ number of executors | Parallelism optimization |
| Athena/Redshift Spectrum | Prefers 128 MB - 1 GB per file | Scan efficiency |
| Human inspection | Prefers fewer files | Convenience |
| SLA monitoring | Prefers deterministic count | Easy validation (expected N files) |

**If file count truly matters, available control per approach:**

| Approach | File Count Control | Mechanism |
|----------|-------------------|-----------|
| EXPORT DATA | No direct control | BQ decides (~256 MB/file). For 180 GB: ~700 files |
| EXPORT DATA + merge | YES | Post-process merge N->K files |
| Cloud Run + PyArrow streaming | YES | Open exactly K ParquetWriters |
| Dataflow num_shards=N | YES but OOM | GroupByKey on data |
| Dataflow num_shards=0 | No | Runner-decided, ~50-200 files |
| Dataflow 2-step + merge | YES | Write unsharded -> merge |
| Spark repartition(K) | YES | Shuffle-based, handles large data |

**EXPORT DATA file count estimation:**
- BQ targets ~256 MB per output file (compressed Parquet)
- 180 GB source / 3x Parquet compression / 256 MB = ~234 files (estimate, actual varies)
- For small daily tables (< 1 GB): typically 1-5 files

#### 7. Beam WriteToParquet Internals (Why num_shards Causes OOM)

**Source: iobase.py `WriteImpl._expand_bounded()` (Beam 2.69)**

```
num_shards >= 1 path:
  pcoll
    | _RoundRobinKeyFn(count=num_shards)    # key 0..N-1
    | GlobalWindows()
    | GroupByKey()                            # <-- MATERIALIZES ALL DATA PER KEY
    | _WriteKeyedBundleDoFn(sink)            # writes per key

num_shards == 0 path:
  pcoll
    | _WriteBundleDoFn(sink)                 # writes per-bundle (streaming, no GBK on data)
    | Map(lambda x: (None, x))
    | GroupByKey()                            # GBK only on WRITE RESULTS (file handles)
    | FlatMap(lambda x: x[1])                # extract file handles
```

**The GBK for num_shards >= 1 in GlobalWindows collects ALL elements for each key into an iterator that Beam materializes in memory.** This is the Python SDK behavior on Dataflow runner. The Java SDK has different spill behavior, but Python SDK does not spill to disk.

**WriteToParquetBatched (Beam 2.71+):** Accepts `pyarrow.Table` objects instead of dicts. Skips the `_RowDictionariesToArrowTable` conversion. **But still uses same WriteImpl with same GBK for num_shards >= 1.** Does not fix OOM.

**beam.io.fileio.WriteToFiles:** For single-destination writes (our case), data flows through unsharded path (1 writer per bundle). The `shards` parameter only affects spilled records. Since single-destination never exceeds `max_writers_per_bundle`, nothing spills. Result: same as num_shards=0 -- no file count control.

**Reshuffle before Write:** Does not help. Reshuffle inserts a random-key GBK that redistributes elements, but the Write's internal `_RoundRobinKeyFn -> GroupByKey` still collects all elements per shard key afterward. The two GBKs are independent.

**Conclusion: There is no way to get fixed file count in Beam Python SDK + Dataflow for large data without GBK on data (= OOM risk).**

#### 8. Staying with Dataflow -- Viable Patterns

If organizational policy requires Dataflow:

**Pattern A: num_shards=0 (accept variable file count)**
```python
# 1-line fix: remove num_shards
_ = rows | "WriteParquet" >> beam.io.WriteToParquet(
    file_path_prefix=output_path,
    schema=parquet_schema,
    # num_shards removed
    file_name_suffix=".parquet",
    codec="snappy",
)
```
- No OOM (no GBK on data)
- File count: runner-decided (~50-200 for 180 GB)
- If downstream can handle variable file count: done

**Pattern B: num_shards=0 -> post-merge**
```python
# Step 1: Dataflow writes variable files (no OOM)
# Step 2: Cloud Run merges into fixed count

# merge.py (runs after Dataflow completes)
import pyarrow.parquet as pq
from gcsfs import GCSFileSystem

fs = GCSFileSystem()
input_files = sorted(fs.glob("gs://bucket/tmp/svoc/*.parquet"))
num_output = 15

# Distribute input files evenly across output files
files_per_output = len(input_files) // num_output + 1

for i in range(num_output):
    batch = input_files[i * files_per_output : (i + 1) * files_per_output]
    if not batch:
        break
    writer = None
    for f in batch:
        table = pq.read_table(f, filesystem=fs)  # ~few hundred MB each
        if writer is None:
            writer = pq.ParquetWriter(
                f"gs://bucket/final/svoc/shard-{i:05d}-of-{num_output:05d}.parquet",
                table.schema, compression='snappy', filesystem=fs
            )
        writer.write_table(table)  # each input file becomes a row group
    if writer:
        writer.close()
```
- Memory: only 1 input file in RAM at a time (~few hundred MB)
- Cloud Run with 2 GB RAM is sufficient
- Adds orchestration complexity (2 steps)

**Pattern C: Use DIRECT_READ for speed (num_shards=0)**
```python
rows = p | "ReadBQ" >> beam.io.ReadFromBigQuery(
    query=export_sql,
    use_standard_sql=True,
    method=beam.io.ReadFromBigQuery.Method.DIRECT_READ,  # faster, $1.10/TB
    project=config.project,
)
# ... WriteToParquet(num_shards=0) ...
```
- Faster read (~5-10 min vs 30+ min for EXPORT method)
- Costs $0.198 for 180 GB (Storage Read API)
- Total: $0.198 + Dataflow compute (~$5-10) = ~$5-10/run
- Still no file count control

---

### architect-data says:

#### 9. Recommended Architecture Patterns (Final)

**Pattern 1: EXPORT DATA Direct (Simplest, cheapest)**

```
Cloud Scheduler / Airflow
  |
  v
BQ EXPORT DATA  -----> GCS Parquet files (variable count)
  |                         |
  v                         v
Verify (row count)    S3 Transfer (boto3/STS)
```

```sql
EXPORT DATA OPTIONS(
    uri = 'gs://bucket/export/{table}/{date}/*.parquet',
    format = 'PARQUET',
    overwrite = true,
    compression = 'SNAPPY'
) AS
SELECT * FROM `project.dataset.table`
WHERE partition_date = @date
```

| Attribute | Value |
|-----------|-------|
| File count control | No (BQ decides) |
| Dedup guarantee | Atomic (BQ manages) |
| Cost (180 GB) | $0.00 - $1.13 (depends on SELECT * vs transform) |
| Retry cost | Same (overwrite=true is idempotent) |
| Complexity | Minimal (1 SQL statement) |
| OOM risk | None (runs in BQ engine) |
| Time (180 GB) | 2-10 min |

**Best for**: SVOC (if variable file count acceptable), small-medium daily exports.

---

**Pattern 2: Temp Table + EXPORT DATA (Best cost on retry)**

```
Airflow / Cloud Run
  |
  v
BQ Query -> Temp Table (TTL 24h)  [cost: $6.25/TB, one-time]
  |
  v
EXPORT DATA FROM temp table       [cost: FREE, retryable]
  |
  v
GCS Parquet files -> Verify -> S3
```

```python
# Pseudo-code orchestration
def export_pipeline(table, date, gcs_path):
    temp_table = f"project._temp.export_{table}_{date}"
    
    # Step 1: Snapshot to temp (idempotent with WRITE_TRUNCATE)
    bq_client.query(f"""
        CREATE OR REPLACE TABLE `{temp_table}`
        OPTIONS(expiration_timestamp=TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR))
        AS SELECT * FROM `{table}` WHERE partition_date = '{date}'
    """).result()
    
    # Step 2: Export from temp (free, safe to retry)
    bq_client.query(f"""
        EXPORT DATA OPTIONS(
            uri='{gcs_path}/*.parquet',
            format='PARQUET', overwrite=true, compression='SNAPPY'
        ) AS SELECT * FROM `{temp_table}`
    """).result()
    
    # Step 3: Verify
    verify_export(gcs_path, expected_rows=get_row_count(temp_table))
```

| Attribute | Value |
|-----------|-------|
| File count control | No |
| Dedup guarantee | Snapshot isolation + atomic export |
| Cost (180 GB, first run) | $1.13 (query) + $0.00 (export) = $1.13 |
| Cost (retry) | $0.00 (export from existing temp table) |
| Complexity | Low (2 SQL statements) |
| OOM risk | None |

**Best for**: Large tables where retry cost matters, tables that change during export window.

---

**Pattern 3: Cloud Run + BQ Storage API + Streaming PyArrow (Full control)**

```
Cloud Scheduler
  |
  v
Cloud Run Job
  |-- BQ query -> temp table (snapshot)
  |-- BQ Storage Read API -> stream RecordBatches
  |-- Round-robin to K ParquetWriters
  |-- Close writers -> verify -> manifest
  |
  v
GCS: exactly K Parquet files
  |
  v
S3 Transfer
```

```python
# cloud_run_export.py
from google.cloud import bigquery, bigquery_storage
import pyarrow.parquet as pq
from gcsfs import GCSFileSystem
import json

NUM_FILES = 15
COMPRESSION = "snappy"

def run_export(source_table: str, output_prefix: str, date: str):
    bq_client = bigquery.Client()
    bqs_client = bigquery_storage.BigQueryReadClient()
    fs = GCSFileSystem()
    
    # Step 1: Query to get arrow stream
    query = f"SELECT * FROM `{source_table}` WHERE partition_date = '{date}'"
    job = bq_client.query(query)
    
    # Step 2: Stream as Arrow RecordBatches
    result = job.result()
    arrow_iterator = result.to_arrow_iterable(
        bqstorage_client=bqs_client,
        max_queue_size=2,  # limit prefetch to control memory
    )
    
    # Step 3: Open K writers
    temp_prefix = f"{output_prefix}/_tmp/"
    final_prefix = f"{output_prefix}/{date}/"
    schema = None
    writers = []
    total_rows = 0
    
    for idx, batch in enumerate(arrow_iterator):
        if schema is None:
            schema = batch.schema
            for i in range(NUM_FILES):
                path = f"{temp_prefix}shard-{i:05d}-of-{NUM_FILES:05d}.parquet"
                writers.append(pq.ParquetWriter(path, schema,
                               compression=COMPRESSION, filesystem=fs))
        
        # Round-robin batches across writers
        writers[idx % NUM_FILES].write_batch(batch)
        total_rows += batch.num_rows
    
    # Step 4: Close all writers
    for w in writers:
        w.close()
    
    # Step 5: Verify
    temp_files = sorted(fs.ls(temp_prefix))
    verified_rows = sum(
        pq.read_metadata(f"gs://{f}", filesystem=fs).num_rows
        for f in temp_files
    )
    assert verified_rows == total_rows, f"Row mismatch: {verified_rows} vs {total_rows}"
    assert len(temp_files) == NUM_FILES
    
    # Step 6: Move to final location
    if fs.exists(final_prefix):
        fs.rm(final_prefix, recursive=True)
    for f in temp_files:
        filename = f.split("/")[-1]
        fs.mv(f"gs://{f}", f"{final_prefix}{filename}")
    
    # Step 7: Write manifest
    manifest = {
        "total_rows": total_rows,
        "num_files": NUM_FILES,
        "compression": COMPRESSION,
        "source_table": source_table,
        "date": date,
    }
    with fs.open(f"{final_prefix}_SUCCESS", "w") as mf:
        json.dump(manifest, mf)
    
    return manifest
```

| Attribute | Value |
|-----------|-------|
| File count control | **YES** (exact) |
| Dedup guarantee | Temp dir + verify + atomic move |
| Cost (180 GB) | ~$1.35 (query + Storage API + Cloud Run compute) |
| Memory | ~200-500 MB peak (1 RecordBatch + K open writers) |
| Cloud Run config | 4-8 vCPU, 2-4 GB RAM, 60 min timeout |
| Time (180 GB) | ~10-15 min |
| Complexity | Medium (single Python script, ~100 lines) |

**Best for**: When exact file count is a hard requirement.

---

**Pattern 4: EXPORT DATA + Parquet Merge (Fixed count, simplest code)**

```
Step 1: EXPORT DATA -> gs://bucket/tmp/  (~N files, BQ decides)
Step 2: Cloud Run merge -> gs://bucket/final/  (exactly K files)
```

```python
# merge_parquet.py (Cloud Run job, ~30 lines)
import pyarrow.parquet as pq
from gcsfs import GCSFileSystem

def merge_parquet_files(input_prefix: str, output_prefix: str, num_output: int):
    fs = GCSFileSystem()
    input_files = sorted(fs.glob(f"{input_prefix}/*.parquet"))
    
    # Distribute input files evenly
    files_per_shard = max(1, len(input_files) // num_output)
    
    for i in range(num_output):
        start = i * files_per_shard
        end = start + files_per_shard if i < num_output - 1 else len(input_files)
        shard_files = input_files[start:end]
        
        if not shard_files:
            break
        
        output_path = f"{output_prefix}/shard-{i:05d}-of-{num_output:05d}.parquet"
        writer = None
        
        for f in shard_files:
            table = pq.read_table(f"gs://{f}", filesystem=fs)
            if writer is None:
                writer = pq.ParquetWriter(
                    output_path, table.schema,
                    compression="snappy", filesystem=fs,
                )
            writer.write_table(table)
        
        if writer:
            writer.close()
    
    # Cleanup input
    for f in input_files:
        fs.rm(f"gs://{f}")
```

| Attribute | Value |
|-----------|-------|
| File count control | **YES** (merge step) |
| Dedup guarantee | EXPORT DATA atomic + merge idempotent (overwrite) |
| Cost (180 GB) | ~$0.05 (export free + Cloud Run merge ~3-5 min) |
| Memory (merge) | ~256-512 MB peak (1 input file at a time) |
| Complexity | Low (export SQL + 30-line merge) |
| Time (180 GB) | ~5-10 min export + ~5 min merge |

**Best for**: Fixed file count with minimum cost and complexity.

---

#### 10. Approach Comparison Matrix

| # | Approach | Exact Files | No Dup | Cost (180 GB) | Cost (retry) | OOM Risk | Complexity | Time |
|---|---------|:-----------:|:------:|:-------------:|:------------:|:--------:|:----------:|:----:|
| 1 | **EXPORT DATA direct** | No | Atomic | **$0 - $1.13** | Same | None | **Minimal** | 2-10 min |
| 2 | **Temp table + EXPORT DATA** | No | Snapshot + atomic | $1.13 | **$0** | None | Low | 3-12 min |
| 3 | **Cloud Run + Storage API** | **Yes** | Temp dir + verify | $1.35 | $1.35 | None | Medium | 10-15 min |
| 4 | **EXPORT DATA + merge** | **Yes** | Atomic + idempotent | **$0.05** | $0.05 | None | **Low** | 10-15 min |
| 5 | Dataflow (num_shards=0) | No | Per-bundle atomic | $8-20 | $8-20 | None | Medium | 1-2 hr |
| 6 | Dataflow (num_shards=15) | Yes | Per-bundle atomic | $15-20 | $15-20 | **HIGH** | Medium | **FAILS** |
| 7 | Dataflow + merge | Yes | Per-bundle + merge | $10-22 | $10-22 | None | High | 1-2.5 hr |
| 8 | Spark/Dataproc | Yes | Checkpoint | $3-5 | $3-5 | None | High | 15-30 min |

#### 11. Specific Recommendations

**For customer-svoc-interim (280 cols, ~180 GB, monthly):**

| Priority | Pattern | Why |
|----------|---------|-----|
| 1st choice | **Pattern 4: EXPORT DATA + merge** | Fixed 15 files, ~$0.05/run, simplest, fastest |
| 2nd choice | Pattern 1: EXPORT DATA direct | If variable file count OK, ~$0/run |
| 3rd choice | Pattern 3: Cloud Run streaming | If need custom Parquet settings (row groups, etc.) |
| Avoid | Dataflow with num_shards | OOM proven, expensive even if fixed |

**For backward-compatible-collector (daily, small-medium):**

| Priority | Pattern | Why |
|----------|---------|-----|
| 1st choice | **Pattern 1: EXPORT DATA direct** | Daily slices are small, variable file count fine (1-5 files) |
| 2nd choice | Pattern 2: Temp table + EXPORT DATA | If retry safety critical |
| 3rd choice | Pattern 3: Cloud Run streaming | If exact file count matters for S3 consumer |
| Acceptable | Dataflow with num_shards=0 | Quick fix (remove num_shards), keeps existing infra |

#### 12. Migration Path

**Phase 1: Immediate fix (customer-svoc-interim)**
1. Replace Dataflow pipeline with EXPORT DATA SQL
2. Add merge step (Cloud Run or Airflow PythonOperator) if 15 files needed
3. Verify output matches current Parquet schema
4. Update Airflow DAG: `BigQueryInsertJobOperator` -> (optional) merge -> S3 transfer

**Phase 2: backward-compatible-collector**
1. Option A (quick): Remove `num_shards` from `WriteToParquet` -- 1-line fix
2. Option B (proper): Replace Dataflow with EXPORT DATA + existing S3 upload module
3. Test with each table (member_tier, member_tier_maintenance, member_tier_history)

**Phase 3: Common library**
```python
# Reusable export module for all BQ -> Parquet pipelines
class BQToParquetExporter:
    def __init__(self, project, gcs_bucket, num_files=None):
        ...
    
    def export(self, query, output_path, compression="snappy"):
        # Step 1: EXPORT DATA
        # Step 2: Merge (if num_files specified)
        # Step 3: Verify
        # Step 4: Write manifest
        ...
```

---

## Options Considered

1. **Option 1: EXPORT DATA direct** -- Pros: Zero cost, zero infra, atomic. Cons: No file count control.
2. **Option 2: Temp table + EXPORT DATA** -- Pros: Retry-safe, snapshot isolation. Cons: Initial query cost, no file count control.
3. **Option 3: Cloud Run + BQ Storage API streaming** -- Pros: Full control (files, schema, row groups). Cons: More code, higher cost.
4. **Option 4: EXPORT DATA + merge** -- Pros: Fixed files, minimal cost, simple. Cons: Two steps, slight latency.
5. **Option 5: Dataflow (fixed)** -- Pros: Keeps existing infra. Cons: Expensive, slow, fragile.
6. **Option 6: Spark/Dataproc** -- Pros: Handles any scale. Cons: Overkill, needs cluster management.

## Recommendation

**Primary: Pattern 4 (EXPORT DATA + Parquet merge) for SVOC.** Cheapest (~$0.05/run), simplest (SQL + 30 lines Python), fastest (~15 min), exact file count, zero OOM risk.

**Secondary: Pattern 1 (EXPORT DATA direct) for backward-compatible-collector.** Daily slices are small enough that variable file count (1-5 files) is acceptable. Zero infrastructure beyond a SQL statement.

**Fallback: Remove num_shards from existing Dataflow pipelines.** If organizational constraints require keeping Dataflow, this is a 1-line fix that eliminates OOM at the cost of variable file count.

**Do NOT**: Keep `num_shards=15` on Dataflow. This is a ticking time bomb that will OOM on any sufficiently large table.

## Decision (Human Approval)
- [ ] Approved
- [ ] Rejected -- Reason: ...
- [ ] Needs revision -- Feedback: ...

## Action Items
- [ ] **customer-svoc-interim**: Implement Pattern 4 (EXPORT DATA + merge) -- assigned to: insight team
- [ ] **backward-compatible-collector**: Implement Pattern 1 (EXPORT DATA direct) or remove num_shards as quick fix -- assigned to: loyalty team
- [ ] Verify SVOC downstream S3 consumers accept file naming change -- assigned to: domain-insight
- [ ] Verify EXPORT DATA `SELECT *` vs `SELECT col AS alias` cost with dry-run -- assigned to: architect-cloud
- [ ] Build common `BQToParquetExporter` module if pattern used by 3+ pipelines -- assigned to: architect-solution
