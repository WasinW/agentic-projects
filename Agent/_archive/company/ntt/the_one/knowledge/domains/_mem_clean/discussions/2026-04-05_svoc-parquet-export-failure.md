# Discussion: customer-svoc-interim WriteParquet Failure + BQ-to-Parquet Export Strategy

**Date**: 2026-04-05
**Status**: open
**Initiated by**: architect-cloud + domain-insight
**Participants**: architect-cloud, domain-insight

---

## Context

Dataflow job `customer-svoc-interim-202603-b04d5ec0` (PROD, project `the1-insight-prod`) **FAILED after 8 hr 50 min 59 sec**.

**Error:**
```
Workflow failed. Causes: S08:WriteParquet/Write/WriteImpl/GroupByKey/Read+WriteParquet/Write/WriteImpl/WriteBundles failed.
The job failed because a work item has failed 4 times.
Root cause: Timed out waiting for an update from the worker.
Workers: customer-svoc-interim-202-04020824-fj70-harness-{pkgq,sttd,nlnn}
```

The same BQ-to-Parquet pattern is planned for `backward-compatible-collector` (BQ -> GCS Parquet -> S3). Need a reliable approach for both.

---

## Findings

### architect-cloud says:

#### 1. Root Cause Analysis: Why WriteParquet Failed

**The pipeline code** (`builder.py`) is straightforward:

```python
# Step 1: BQ read (export method, default)
rows = p | "ReadBQ" >> beam.io.ReadFromBigQuery(query=export_sql, use_standard_sql=True, project=config.project)

# Step 2: Cast to string
stringified = rows | "CastToString" >> beam.Map(lambda row: {k: str(v) if v is not None else None for k, v in row.items()})

# Step 3: Write Parquet with fixed num_shards=15
_ = stringified | "WriteParquet" >> beam.io.WriteToParquet(
    file_path_prefix=output_path, schema=parquet_schema,
    num_shards=config.num_export_files,  # 15
    file_name_suffix=".parquet",
)
```

**The killer: `num_shards=15` + `GroupByKey`**

Looking at Apache Beam's `WriteImpl._expand_bounded()` (iobase.py line 1170-1215):

```python
# When num_shards >= 1 (our case: 15):
keyed_pcoll = pcoll | core.ParDo(_RoundRobinKeyFn(), count=min_shards)  # key 0-14
keyed_pcoll
    | core.WindowInto(window.GlobalWindows())
    | core.GroupByKey()              # <-- THIS IS THE PROBLEM
    | 'WriteBundles' >> core.ParDo(_WriteKeyedBundleDoFn(self.sink), ...)
```

When `num_shards=15`, Beam:
1. Assigns each record a round-robin key (0 through 14)
2. **GroupByKey collects ALL records for each key into memory** before writing
3. Each of 15 keys holds `total_rows / 15` records

**Data size estimation:**
- Source table: `refined.full_customer_svoc_ingt` -- 300 columns, all STRING
- The1 member base: likely 20-40 million members
- Average row size: 300 columns x ~20 bytes average = ~6 KB per row
- Total data: ~30M rows x 6 KB = **~180 GB raw data**
- Per shard (15 shards): ~12 GB of dict objects in memory per key

**Why workers timed out:**
- `GroupByKey` for key N has to buffer **~2M rows x 300 columns** as Python dicts
- Python dict overhead: each row is ~300 string objects + dict overhead = ~20-50 KB per row in Python heap
- Per-shard memory: 2M rows x 30 KB = **~60 GB Python heap per shard** (!!!)
- Workers (likely n1-standard-4, 15 GB RAM) get OOM'd silently
- Dataflow retries 4 times on different workers, all fail -> "Timed out waiting for update"

**Additionally:**
- `_RowDictionariesToArrowTable` buffers rows into `record_batch_size=1000` batches and `row_group_buffer_size=64 MB`
- But this happens BEFORE the GroupByKey, as a DoFn producing Arrow tables
- The GroupByKey then collects those Arrow tables per shard key
- 64 MB buffer x many batches per shard = massive memory

**Why 9 hours:**
- `ReadFromBigQuery` default method = **EXPORT** (BQ -> temp Avro/JSON on GCS -> workers read from GCS)
- For 180 GB of data, the export + read takes significant time
- Workers slowly process then OOM during the final GroupByKey+WriteBundles stage

#### 2. Beam WriteToParquet Architecture Issue

The fundamental problem: **`WriteToParquet` with `num_shards > 0` forces a GroupByKey that materializes all data for each shard in memory.** This is a well-known issue with Beam's file-based sink pattern for large datasets.

With `num_shards=0` (unset), Beam uses a different path:
```python
# num_shards=0 path:
pcoll | 'WriteBundles' >> core.ParDo(_WriteBundleDoFn(self.sink), ...)
      | 'Pair' >> core.Map(lambda x: (None, x))
      | core.GroupByKey()   # <-- GBK is only on WRITE RESULTS (file handles), not data
      | 'Extract' >> core.FlatMap(lambda x: x[1])
```
With `num_shards=0`, data is written per-bundle (streaming fashion) and only the file handles are grouped. **This does NOT OOM.** But you lose control over file count.

#### 3. The backward-compatible-collector Has the Same Pattern

```python
# backward-compatible-collector/src/application/pipeline/builder.py
(
    p
    | "ReadFromBQ" >> ReadFromBigQuery(query=query, use_standard_sql=True)
    | "WriteParquet" >> beam.io.WriteToParquet(
        file_path_prefix=f"{gcs_output}part",
        file_name_suffix=".parquet",
        num_shards=num_shards,    # default 15 from config
        codec=compression,        # snappy
    )
)
```

**Same vulnerability.** If the BQ tables grow large enough, this will also OOM.

For loyalty tables (member_tier, member_tier_maintenance, member_tier_history), the daily slices are likely small (thousands to low millions), so it may work now. But it is fragile by design.

---

### domain-insight says:

#### Why This is Over-Engineered

The entire purpose of `customer-svoc-interim` is: **read from BQ, write to GCS as Parquet.** That's it. No transformation, no join, no aggregation. Just format conversion + file placement.

Using Dataflow for this is like using a forklift to move a sandwich. BQ has a built-in `EXPORT DATA` command that does exactly this, running inside BQ's own engine with no external workers to OOM.

#### Data Profile

- `full_customer_svoc_ingt`: DTS landing table from AWS S3. All 300 columns are STRING.
- Updated monthly (par_month partitioned).
- Likely 20-40M rows per month based on The1 member base.
- The SQL does `SELECT col AS col` for all 300 columns (1:1 rename, currently identity).

#### backward-compatible-collector Profile

- `refined.member_tier`: daily partition, CDC table. Small-medium per day (depends on tier changes).
- `refined.member_tier_maintenance`: daily partition. Small-medium per day.
- `refined.member_tier_history`: daily partition by `etl_created_date`. Larger (full snapshot-like).
- After Parquet on GCS, files are transferred to S3 via boto3 multipart upload.

---

## Options Considered

### Option A: BQ EXPORT DATA (Recommended for SVOC)

**No Dataflow needed.** Run a single SQL command:

```sql
EXPORT DATA OPTIONS(
  uri = 'gs://the1-insight-prod-data-pipeline-data-staging/export/svoc/202603/svoc-*.parquet',
  format = 'PARQUET',
  overwrite = true,
  compression = 'SNAPPY'
) AS
SELECT
    member_number, life_stage, share_card_flag, ...
FROM `the1-insight-prod.refined.full_customer_svoc_ingt`
```

**Pros:**
- Zero infrastructure (no Dataflow workers, no containers, no OOM)
- BQ engine handles parallelism internally -- tested for petabyte-scale
- Typically completes in minutes for ~180 GB (vs. 9 hours that still failed)
- File size ~256 MB each by default (BQ controls output splitting automatically)
- Snappy/gzip/zstd compression supported natively
- Can be triggered from Airflow via `BigQueryInsertJobOperator` or `bq query` CLI
- Cost: only BQ query cost (same as reading the table), no Dataflow cost

**Cons:**
- Cannot control exact file count (BQ decides based on data size, typically 1 file per ~256 MB)
- File naming: `svoc-000000000000.parquet`, `svoc-000000000001.parquet`, ... (predictable pattern)
- No custom row_group_size control (BQ uses its own defaults)
- Schema is derived from query output (not custom pyarrow schema), but since all columns are STRING this is fine

**How to trigger:**
```bash
# From Airflow, Cloud Scheduler, or CI:
bq query --use_legacy_sql=false --project_id=the1-insight-prod \
  "EXPORT DATA OPTIONS(
    uri='gs://bucket/export/svoc/202603/svoc-*.parquet',
    format='PARQUET', overwrite=true, compression='SNAPPY'
  ) AS SELECT ... FROM \`the1-insight-prod.refined.full_customer_svoc_ingt\`"
```

Or via Python:
```python
from google.cloud import bigquery

client = bigquery.Client(project="the1-insight-prod")
sql = """
EXPORT DATA OPTIONS(
  uri = 'gs://the1-insight-prod-data-pipeline-data-staging/export/svoc/202603/svoc-*.parquet',
  format = 'PARQUET',
  overwrite = true,
  compression = 'SNAPPY'
) AS
SELECT member_number, life_stage, ...
FROM `the1-insight-prod.refined.full_customer_svoc_ingt`
"""
job = client.query(sql)
job.result()  # Wait for completion
print(f"Export complete: {job.total_bytes_processed} bytes processed")
```

---

### Option B: Fix the Dataflow Pipeline (If Dataflow is Required)

If there's a hard requirement to keep Dataflow (e.g., organizational policy, existing Airflow DAG integration), these changes would fix it:

**Fix 1: Remove `num_shards` (let Beam decide)**
```python
# builder.py - CHANGED
_ = (
    stringified
    | "WriteParquet" >> beam.io.WriteToParquet(
        file_path_prefix=output_path,
        schema=parquet_schema,
        # num_shards REMOVED -- Beam writes per-bundle, no GroupByKey on data
        file_name_suffix=".parquet",
        row_group_buffer_size=64 * 1024 * 1024,  # 64 MB row groups
        record_batch_size=10000,  # larger batches for efficiency
    )
)
```

**Why:** With `num_shards=0`, the Write transform uses per-bundle writes (no GroupByKey on the actual data). This eliminates the OOM.

**Downside:** File count is unpredictable (could be 50+ files or just 5, depending on Dataflow's parallelism).

**Fix 2: If exact file count matters, use Reshuffle + FileIO**
```python
import apache_beam as beam
from apache_beam.io import fileio
import pyarrow as pa
import pyarrow.parquet as pq
import io

class WriteParquetFn(beam.DoFn):
    def __init__(self, schema):
        self.schema = schema

    def process(self, element):
        # element is (shard_key, iterable_of_rows)
        shard_key, rows = element
        rows_list = list(rows)
        if not rows_list:
            return

        # Build Arrow table from rows
        table = pa.Table.from_pylist(rows_list, schema=self.schema)

        # Write to in-memory buffer
        buf = io.BytesIO()
        pq.write_table(table, buf, compression='snappy',
                       row_group_size=1_000_000)
        yield buf.getvalue()

# In builder:
NUM_SHARDS = 15

rows = p | "ReadBQ" >> beam.io.ReadFromBigQuery(...)
keyed = rows | "Key" >> beam.Map(lambda row, n=NUM_SHARDS: (hash(str(row.get('member_number',''))) % n, row))
grouped = keyed | "GroupByShard" >> beam.GroupByKey()
# WARNING: This still has the same GBK problem!
```

**This does NOT help** -- any approach with GroupByKey on data has the same memory problem.

**Fix 3: Use `WriteToParquetBatched` (Beam 2.71+)**
```python
# The input must be pyarrow Tables, not dicts
# This avoids the per-row dict overhead but still has GBK with num_shards
```
Still has GBK issue with fixed shards.

**Fix 4: Increase worker memory + reduce shard count**
```yaml
# Dataflow launch options:
--machine_type=n2-highmem-16    # 128 GB RAM (vs ~15 GB default)
--num_shards=5                   # fewer shards = fewer GBK groups but larger each
--disk_size_gb=500               # more disk for spill
--number_of_worker_harness_threads=1  # reduce parallelism per worker to limit memory
```

**Cost:** n2-highmem-16 = ~$1.14/hr x 4 workers x 2 hrs = ~$9/run. Expensive for a simple export.

**Verdict on Fix options:**
- Fix 1 (remove num_shards) is the simplest and works, but loses file count control
- Fix 4 (bigger machines) works but is expensive and fragile (if data grows 2x, breaks again)
- **None of these are as good as Option A (EXPORT DATA)**

---

### Option C: BQ EXPORT DATA + Cloud Storage Transfer to S3 (For backward-compatible-collector)

For the backward-compatible-collector use case (BQ -> Parquet -> GCS -> S3):

**Step 1: EXPORT DATA** (same as Option A)
```sql
EXPORT DATA OPTIONS(
  uri = 'gs://the1-loyalty-data-prod-backward-compatible/export/member_tier/2026-04-04/*.parquet',
  format = 'PARQUET',
  overwrite = true,
  compression = 'SNAPPY'
) AS
SELECT * FROM `the1-loyalty-data-prod.refined.member_tier`
WHERE DATE(ingested_datetime) = '2026-04-04'
```

**Step 2: Transfer to S3** (keep existing boto3 approach or use STS)

The existing `s3_writer.py` in backward-compatible-collector already does GCS->local->S3 upload with multipart. This module can be reused standalone (as a Cloud Run job or Cloud Function) without Dataflow.

**Architecture:**
```
Cloud Scheduler / Airflow
  -> BQ EXPORT DATA (runs in BQ engine, ~minutes)
  -> Cloud Run Job: list GCS Parquet files -> boto3 upload to S3
```

---

### Option D: Cloud Run + PyArrow Direct (No Dataflow, No EXPORT DATA)

For full control over Parquet schema, row groups, compression, and file count:

```python
# cloud_run_export.py
from google.cloud import bigquery
import pyarrow as pa
import pyarrow.parquet as pq

client = bigquery.Client()
query = "SELECT * FROM `project.refined.member_tier` WHERE ..."

# Stream rows via BQ Storage Read API (arrow format -- very fast)
arrow_table = client.query(query).to_arrow()

# Write with full control
pq.write_table(
    arrow_table,
    "gs://bucket/path/output.parquet",
    compression='snappy',
    row_group_size=1_000_000,
    filesystem=gcsfs.GCSFileSystem(),
)
```

**Pros:** Full control over schema, partitioning, row groups, file count.
**Cons:** Single-machine memory limit (Cloud Run max 32 GB). For 180 GB SVOC, would need to paginate reads.

**Suitable for:** backward-compatible-collector tables (small daily slices), **NOT for SVOC** (too large).

---

### Option E: Spark / Dataproc (For Extreme Scale)

If data grows to terabytes or needs complex transformations:

```python
# PySpark
df = spark.read.format("bigquery").option("table", "project.refined.full_customer_svoc_ingt").load()
df.repartition(15).write.parquet("gs://bucket/export/svoc/202603/", mode="overwrite", compression="snappy")
```

**Pros:** Handles any scale, Spark is designed for large shuffles.
**Cons:** Requires Dataproc cluster, more complex infra, higher cost for simple export.

**Verdict:** Overkill. BQ EXPORT DATA is sufficient.

---

## Recommendation

### For customer-svoc-interim (280 cols, ~180 GB, monthly)

**Use Option A: BQ EXPORT DATA**

Reasoning:
1. The pipeline does ZERO transformation (just SELECT with aliases, then write Parquet)
2. BQ EXPORT DATA handles this in minutes, not hours
3. Zero infrastructure to maintain (no Docker, no Dataflow workers, no OOM risk)
4. Cost: ~$0.90 per run (BQ query cost for 180 GB at $5/TB) vs. $9+ for Dataflow
5. Can be triggered from existing Airflow DAG with a simple `BigQueryInsertJobOperator`

**Migration path:**
1. Replace Dataflow job with BQ `EXPORT DATA` SQL in Airflow DAG
2. Verify output Parquet files match expected schema (all STRING, same column names)
3. Decommission the Dataflow flex template + container image
4. Keep the codebase as reference / fallback

**If exact file count (15) is a hard requirement** from downstream consumers:
- EXPORT DATA does not support fixed file count
- Workaround: Export then merge files using `pyarrow.parquet.read_table()` + `write_table()` in a small Cloud Run post-step
- Or: Inform downstream that file count may vary (usually cleaner)

### For backward-compatible-collector (loyalty tables, daily, small-medium)

**Use Option A (EXPORT DATA) + existing S3 upload module:**

1. Replace Dataflow pipeline with BQ EXPORT DATA (per job config query)
2. Keep the `s3_writer.py` module as-is for GCS -> S3 transfer
3. Run as Cloud Run job: Step 1 (EXPORT) -> Step 2 (S3 upload)
4. Or keep as Airflow task: `BigQueryInsertJobOperator` -> `PythonOperator(upload_to_s3)`

**If Dataflow must be kept** (e.g., organizational mandate):
- Remove `num_shards` parameter (set to 0) to avoid the GroupByKey OOM
- This is a 1-line fix: delete `num_shards=num_shards` from `WriteToParquet` call
- Accepts variable file count as tradeoff
- For loyalty daily slices (small data), the current setup may work for now, but is fragile

### Summary Matrix

| Criteria                  | EXPORT DATA (A) | Dataflow fixed (B) | Cloud Run (D) | Spark (E) |
|---------------------------|-----------------|-------------------|---------------|-----------|
| SVOC 180 GB               | Best            | Works (no shards) | Too large     | Overkill  |
| Loyalty daily slices      | Best            | Works             | Works         | Overkill  |
| File count control        | No              | No (if no shards) | Yes           | Yes       |
| Infra complexity          | None            | High              | Low           | High      |
| Cost per run (SVOC)       | ~$0.90          | ~$9+              | ~$0.50        | ~$3+      |
| Time (SVOC)               | 2-10 min        | 1-2 hr            | N/A           | 15-30 min |
| OOM risk                  | None            | Low (no shards)   | Medium        | None      |

---

## Key Technical Details

### Why "Timed out waiting for an update from the worker" means OOM

Dataflow workers run a harness process that sends heartbeats to the service. When a worker runs out of memory:
1. The OS kernel triggers OOM killer, terminating the Python process
2. Or: Python enters a GC death spiral, consuming 100% CPU with no progress
3. Either way, the heartbeat stops
4. Dataflow service waits (default 10 min), then declares "timed out"
5. Retries on a new worker 4 times, same result each time

The error message path confirms this: `WriteParquet/Write/WriteImpl/GroupByKey/Read+WriteParquet/Write/WriteImpl/WriteBundles` -- the GroupByKey is accumulating data, then WriteBundles tries to materialize it.

### Why row_group_buffer_size does NOT help here

The `_RowDictionariesToArrowTable` DoFn (parquetio.py line 99-148) buffers rows into Arrow record batches of `record_batch_size=1000` rows and flushes when `row_group_buffer_size` (64 MB) is reached. **But this DoFn runs BEFORE the GroupByKey.** The output of this DoFn is Arrow tables. These Arrow tables then go into the GroupByKey which collects them per shard key. So the GBK still accumulates all data for a shard.

### ReadFromBigQuery Method

The pipeline uses default `ReadFromBigQuery` which defaults to the **EXPORT method** (BQ -> temp files on GCS -> workers read). This is:
- Slow for large tables (export step alone can take 30+ min for 180 GB)
- Creates temporary GCS files that need cleanup
- Alternative: `method=ReadFromBigQuery.Method.DIRECT_READ` uses BQ Storage Read API (faster, no temp files)

But switching to DIRECT_READ does not fix the WriteParquet OOM -- it only speeds up the read side.

---

## Decision (Human Approval)
- [ ] Approved
- [ ] Rejected -- Reason: ...
- [ ] Needs revision -- Feedback: ...

## Action Items
- [ ] **customer-svoc-interim**: Replace Dataflow pipeline with BQ EXPORT DATA -- assigned to: insight team
- [ ] **backward-compatible-collector**: Either (a) switch to EXPORT DATA, or (b) remove `num_shards` as quick fix -- assigned to: loyalty team
- [ ] Verify SVOC downstream consumers accept variable file count -- assigned to: domain-insight + insight team
- [ ] If backward-compatible-collector keeps Dataflow, add `--machine_type=n2-standard-4` and remove `num_shards` -- assigned to: architect-cloud

---

### architect-solution + architect-cloud: Fixed File Count Options

**Date**: 2026-04-05
**Question**: Can we write exactly 10-20 Parquet files without OOM?

#### Source Code Findings (Beam 2.69 iobase.py, parquetio.py, fileio.py)

**`num_shards >= 1` path (iobase.py WriteImpl._expand_bounded)**:
- `_RoundRobinKeyFn` assigns key 0..N-1 → `GlobalWindows()` → **GroupByKey()** → `_WriteKeyedBundleDoFn` writes per key.
- GBK materializes **ALL elements** for each key in memory. 180 GB / 15 keys = 12 GB raw per key, ~50-60 GB Python heap per key. Fatal on any standard machine.

**`num_shards = 0` path**: Data writes per-bundle via `_WriteBundleDoFn`. GBK only on write results (file handles), not data. No OOM. But file count = number of bundles (runner-decided, unpredictable).

**`_RowDictionariesToArrowTable`** runs BEFORE GroupByKey (converts dicts to Arrow tables in 64 MB row groups). The GBK then collects those Arrow tables per shard key -- so it buffers Arrow tables, not dicts, but still unbounded per key.

#### Option 1: WriteToParquet + num_shards + bigger machine

| Machine | RAM | Per-shard headroom (15 shards) | Verdict |
|---------|-----|-------------------------------|---------|
| n1-standard-4 | 15 GB | 0 (current, OOM) | Failed |
| n1-highmem-8 | 52 GB | ~50 GB total, 1 shard at a time might fit | Risky -- Dataflow may schedule multiple shards on same worker |
| n1-highmem-16 | 104 GB | Likely fits if 1-2 shards per worker | Probably works |
| n2-highmem-16 | 128 GB | Safe margin | Works |

**Problem**: Dataflow batch scheduler can place multiple GBK shards on the same worker. With 15 shards and 4 workers, each worker handles ~4 shards sequentially (not simultaneously), but Python GC pressure + Arrow buffer overhead makes this unpredictable.

**Cost**: n1-highmem-16 Dataflow batch ~$0.95/hr compute + Dataflow surcharges (~$0.056/vCPU-hr + $0.003557/GB-hr). For 16 vCPU + 104 GB + 2hr runtime + 4 workers: **~$15-20/run**. Compared to EXPORT DATA ~$0.90/run. 20x more expensive for the same result.

**Verdict**: Works but expensive and fragile. Data growth breaks it again.

#### Option 2: Reshuffle before WriteToParquet(num_shards=15)

`beam.Reshuffle()` inserts a random-key GBK that redistributes elements across workers and breaks fusion. **But it does NOT help here**: the WriteImpl's internal `_RoundRobinKeyFn → GroupByKey` still collects all elements per shard key into memory AFTER the Reshuffle. Reshuffle changes data distribution between stages but cannot change the behavior of a downstream GBK that groups by shard key.

**Verdict**: Does NOT solve OOM. The problem is WriteImpl's GBK, not data skew before it.

#### Option 3: beam.io.fileio.WriteToFiles with custom ParquetSink

Source code analysis of `fileio.py WriteToFiles.expand()`:

1. `_WriteUnshardedRecordsFn`: Opens 1 writer per destination. Spills to SPILLED_RECORDS when `len(writers) >= max_writers_per_bundle` (default 20).
2. Spilled records → `_AppendShardedDestination(shards=N)` → round-robin key → **GroupByKey** → `_WriteShardedRecordsFn`.

**For SVOC (single destination)**: Only 1 writer needed. `max_writers_per_bundle=20` is never exceeded. **Zero records spill**. All data flows through unsharded path = 1 file per bundle, file count = runner-decided. The `shards` param is irrelevant.

To force exact file count, you must set `max_writers_per_bundle=0` (force all records to spill). Then ALL data goes through GBK on shard keys -- **same OOM as WriteToParquet(num_shards=15)**.

**Verdict**: Does NOT solve the problem for single-destination. WriteToFiles is designed for multi-destination fan-out, not fixed file count.

#### Option 4: Custom sharding + per-shard write

```python
records | beam.Map(lambda x: (hash(x['member_number']) % 15, x))
        | beam.GroupByKey()  # same OOM -- all records for key N in memory
        | beam.FlatMap(write_shard_to_gcs)
```

Any approach using `GroupByKey` on the actual data hits the same wall. The GBK contract in Beam (especially Python SDK on Dataflow) materializes all values for a key in memory for GlobalWindows.

**Verdict**: Same OOM. GroupByKey on data is the fundamental blocker.

#### Option 5: Two-step (Dataflow unsharded → PyArrow merge)

**Step 1**: Dataflow `WriteToParquet(num_shards=0)` -- Beam auto-shards, no GBK on data, no OOM. Produces N files (maybe 50-200 depending on parallelism).
**Step 2**: Cloud Run job or Cloud Function reads N files, merges into 15 files via PyArrow.

```python
# Step 2: merge script (Cloud Run, ~8 GB RAM sufficient)
import pyarrow.parquet as pq
from gcsfs import GCSFileSystem

fs = GCSFileSystem()
files = fs.glob("gs://bucket/export/svoc/202603/part-*.parquet")
dataset = pq.ParquetDataset(files, filesystem=fs)
table = dataset.read()  # reads metadata only, lazy
# Split into 15 chunks and write
rows_per_file = len(table) // 15
for i in range(15):
    chunk = table.slice(i * rows_per_file, rows_per_file)
    pq.write_table(chunk, f"gs://bucket/final/svoc-{i:05d}.parquet",
                    filesystem=fs, compression='snappy')
```

**Problem**: `dataset.read()` loads entire 180 GB into memory. Need streaming approach:
```python
# Better: read + write in row-group-sized chunks per output file
# But this requires knowing total row count upfront to distribute evenly
```

**Verdict**: Feasible but adds complexity (2 pipelines + merge logic). The merge step itself needs careful chunked implementation to avoid OOM on the merge side.

#### Option 6: BQ EXPORT DATA → merge Parquet files

**Step 1**: `EXPORT DATA` → many files (~700 files at 256 MB each for 180 GB).
**Step 2**: PyArrow merge into 15 files.

Same merge challenge as Option 5 Step 2. But Step 1 is faster (minutes vs hours).

**Better merge approach using row-group streaming**:
```python
import pyarrow.parquet as pq

files = [...]  # 700 files from EXPORT DATA
files_per_output = len(files) // 15  # ~47 files per output

for i in range(15):
    batch = files[i * files_per_output : (i + 1) * files_per_output]
    writer = None
    for f in batch:
        t = pq.read_table(f, filesystem=fs)  # ~256 MB each, fits in memory
        if writer is None:
            writer = pq.ParquetWriter(f"output-{i:05d}.parquet", t.schema,
                                       compression='snappy', filesystem=fs)
        writer.write_table(t)  # writes as new row group
    writer.close()
```

**Memory**: Only 1 input file in memory at a time (~256 MB). Peak ~512 MB. Runs on Cloud Run with 1 GB RAM.

**Verdict**: BEST option if fixed file count is a hard requirement. Two simple steps, both reliable, low cost, low memory.

#### Option 7: Cloud Run + BQ Storage Read API + PyArrow streaming write

```python
from google.cloud import bigquery
import pyarrow.parquet as pq
from gcsfs import GCSFileSystem

client = bigquery.Client()
query = "SELECT * FROM `project.refined.full_customer_svoc_ingt`"
result = client.query(query)

# to_arrow_iterable() yields RecordBatch objects (streaming, not all-in-memory)
batches = result.to_arrow_iterable(bqstorage_client=bqstorage_client)

# Strategy: round-robin batches across 15 open ParquetWriters
fs = GCSFileSystem()
writers = [pq.ParquetWriter(f"gs://bucket/svoc-{i:05d}.parquet",
           schema=schema, compression='snappy', filesystem=fs) for i in range(15)]

for idx, batch in enumerate(batches):
    writers[idx % 15].write_batch(batch)  # each batch ~few MB

for w in writers:
    w.close()
```

**Memory**: ~15 open writers + 1 RecordBatch in flight. Each RecordBatch ~few MB. Peak memory ~200-500 MB. Could run on Cloud Run with 2 GB RAM.

**Processing time**: BQ Storage Read API reads at ~1-2 GB/s per stream. With multiple streams: 180 GB in ~5-10 min read time. Write bottlenecked by GCS upload: ~200 MB/s per writer = 180 GB / 200 MB/s / 15 writers ~ 1 min. Total: **~10-15 min**.

**Cloud Run cost**: 8 vCPU + 4 GB RAM x 15 min = ~$0.02. Plus BQ query cost ~$0.90. **Total ~$1/run**.

**Verdict**: Excellent. Full control over file count, streaming (no OOM), fast, cheap. Best single-step solution.

#### Answers to Specific Questions

**`num_shards=0` behavior**: Beam's `WriteImpl._expand_bounded` takes the `num_shards=0` path where data writes per-bundle (streaming). GBK only on write results. File count = number of bundles = runner-decided. On Dataflow batch, typically 1 file per worker thread that processes data. For 180 GB with 4 workers x 4 threads, expect ~16-64 files (variable).

**`max_num_shards` option**: Does not exist in Beam Python SDK. Only `num_shards` (exact count) or 0 (auto).

**Beam 2.71 changes to WriteToParquet**: `WriteToParquetBatched` accepts `pyarrow.Table` objects directly (skips dict-to-Arrow conversion). Still uses same `WriteImpl` with same GBK behavior for `num_shards >= 1`. Does not fix OOM.

#### Summary Matrix (all 7 options)

| # | Option | Exact file count? | OOM risk | Cost/run | Complexity | SVOC 180GB? |
|---|--------|-------------------|----------|----------|------------|-------------|
| 1 | num_shards + big machine | YES | MEDIUM (data growth) | ~$15-20 | Low | Fragile |
| 2 | Reshuffle + num_shards | YES | **HIGH (unchanged)** | Same as 1 | Low | NO |
| 3 | WriteToFiles + ParquetSink | NO (single dest) | Same as #1 if forced | Same | Medium | NO |
| 4 | Custom GBK + write | YES | **HIGH (same GBK)** | Same as 1 | Medium | NO |
| 5 | Dataflow unsharded → merge | YES (step 2) | LOW | ~$10 + $0.50 | High | Yes but slow |
| 6 | EXPORT DATA → merge | YES (step 2) | NONE | ~$0.90 + $0.10 | Medium | **YES** |
| 7 | Cloud Run + BQ Storage API | YES | NONE | ~$1 | Medium | **YES** |

#### Recommendation

**If fixed file count is a HARD requirement**: Option 7 (Cloud Run + BQ Storage Read API + PyArrow writers). Single step, streaming, no OOM, exact control, ~$1/run, ~15 min.

**If fixed file count is NICE-TO-HAVE**: Option A from earlier discussion (BQ EXPORT DATA). Zero infra, ~$0.90, ~5 min. Accept variable file count.

**If fixed file count is HARD + want simplest implementation**: Option 6 (EXPORT DATA + merge). Two steps but both trivial. Step 1 = SQL, Step 2 = 20-line Python script on Cloud Run.
