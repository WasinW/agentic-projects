# Pure Dataflow Enrichment Research: Large Lookup Tables Without External Infrastructure

> **Date**: 2026-03-18
> **Context**: Streaming Dataflow pipeline (Python, Beam 2.71.0) on GCP
> **Input**: Kafka, 10K-100K messages/sec
> **Lookup**: 5 batch tables, each ~15M rows x ~10 columns = ~75M rows total
> **Constraint**: NO external instances (no Redis, no Bigtable, no extra infrastructure)
> **Current pattern**: `MasterCache` (BQ -> Python dict) for small tables (~1K-10K rows)
> **Related docs**: `BQ_LOOKUP_TECHNIQUES.md`, `STREAMING_BATCH_JOIN_RESEARCH.md`

---

## Table of Contents

1. [Memory Estimation: The Foundation](#1-memory-estimation-the-foundation)
2. [Option 1: Side Inputs at Scale](#2-option-1-side-inputs-at-scale)
3. [Option 2: Beam Enrichment Transform (BigQueryEnrichmentHandler)](#3-option-2-beam-enrichment-transform)
4. [Option 3: CoGroupByKey with Periodic BQ Reads](#4-option-3-cogroupbykey-with-periodic-bq-reads)
5. [Option 4: MasterCache Scaled Up (Current Pattern)](#5-option-4-mastercache-scaled-up)
6. [Option 5: beam.utils.shared.Shared Class Pattern](#6-option-5-beamutilssharedshared-class-pattern)
7. [Option 6: DuckDB/SQLite as Worker-Local Lookup](#7-option-6-duckdbsqlite-as-worker-local-lookup)
8. [Option 7: Bloom Filter Pre-Filter + Selective Lookup](#8-option-7-bloom-filter-pre-filter--selective-lookup)
9. [Option 8: GCS Parquet/Avro Lookup on Worker Startup](#9-option-8-gcs-parquetavro-lookup-on-worker-startup)
10. [Option 9: Sharded/Partitioned In-Memory Lookup](#10-option-9-shardedpartitioned-in-memory-lookup)
11. [Option 10: Two-Stage Pipeline (Streaming Raw + BQ Post-JOIN)](#11-option-10-two-stage-pipeline)
12. [Cost Comparison Matrix](#12-cost-comparison-matrix)
13. [Detailed Cost Analysis: Pure Dataflow vs External Services](#13-detailed-cost-analysis)
14. [Final Recommendation](#14-final-recommendation)
15. [Sources](#15-sources)

---

## 1. Memory Estimation: The Foundation

Before evaluating any option, we must understand the memory requirements. This drives every architectural decision.

### 1.1 Python Dict Memory Model (CPython 3.11+)

A Python dict entry consists of three 8-byte pointers (64-bit): key pointer, value pointer, hash value = 24 bytes per entry in the hash table. The hash table is kept at most 2/3 full, so effective overhead is ~36 bytes/entry for the table structure alone. Keys and values are separate Python objects with their own overhead.

**Per-object overhead in CPython:**
```
str object:  49 bytes (empty) + 1 byte per ASCII char
             → avg 20-char string key = ~69 bytes
int object:  28 bytes (small int, no interning for large values)
dict object: 64 bytes (empty) + hash table entries
```

### 1.2 Estimating a Single Lookup Row

Assume a typical row: 10 columns, mix of types.
```
Row as dict[str, Any]:
  Outer dict structure for 10 entries:
    - Hash table: 10 entries * 36 bytes (2/3 load) = 360 bytes
    - 10 key strings (col names, avg 15 chars): 10 * 64 bytes = 640 bytes
    - 10 values:
      - 4 strings (avg 20 chars): 4 * 69 bytes = 276 bytes
      - 4 ints: 4 * 28 bytes = 112 bytes
      - 2 dates (as str "2026-01-15"): 2 * 59 bytes = 118 bytes
    - Dict object overhead: 64 bytes
  Total per row dict: ~1,570 bytes

Outer lookup dict (key -> row):
  - Key string (composite, avg 30 chars): ~79 bytes
  - Pointer entries: 36 bytes
  Total outer overhead per entry: ~115 bytes

Grand total per row: ~1,685 bytes ≈ 1.7 KB
```

### 1.3 Total Memory Requirements

| Scenario | Per Table (15M rows) | 5 Tables | Notes |
|----------|---------------------|----------|-------|
| **Python dict (realistic)** | **~25 GB** | **~125 GB** | dict-of-dicts, full Python objects |
| **Optimized (shared keys via __slots__)** | ~12 GB | ~60 GB | NamedTuple or slotted class values |
| **Compact (msgpack values, str keys)** | ~5 GB | ~25 GB | Serialized values, deserialize on lookup |
| **Raw data (theoretical min)** | ~2 GB | ~10 GB | Just the data bytes, no Python overhead |

**Key insight**: Python's object overhead is 3-5x the raw data size. A 15M-row table that is 2 GB in BQ becomes 12-25 GB in a Python dict.

### 1.4 Dataflow Worker Memory Constraints

| Machine Type | vCPUs | Memory | Monthly Cost (streaming, us-central1) |
|-------------|-------|--------|--------------------------------------|
| n1-standard-4 | 4 | 15 GB | ~$350 (Dataflow streaming pricing) |
| n1-standard-8 | 8 | 30 GB | ~$700 |
| n1-highmem-4 | 4 | 26 GB | ~$430 |
| n1-highmem-8 | 8 | 52 GB | ~$860 |
| n1-highmem-16 | 16 | 104 GB | ~$1,720 |
| n2-highmem-16 | 16 | 128 GB | ~$1,900 |

**Dataflow streaming pricing (us-central1):**
- vCPU: $0.069/hr
- Memory: $0.003557/GB/hr
- With Streaming Engine: vCPU $0.069/hr, Memory $0.003557/GB/hr, Streaming Engine data $0.018/GB

**Python SDK threading model**: 1 process, 12 threads per vCPU by default. Side inputs and caches are shared across all threads in the process -- so ONE copy per worker process (not per thread).

### 1.5 The Fundamental Problem

```
125 GB (5 tables as Python dicts) >> 104 GB (n1-highmem-16, largest practical worker)

Even 1 table at 25 GB:
  - Doesn't fit in n1-standard-4 (15 GB total, ~8 GB available after OS + JVM + SDK)
  - Barely fits in n1-highmem-4 (26 GB total, ~18 GB available)
  - Fits in n1-highmem-8 (52 GB total, ~40 GB available) but leaves little for pipeline

All 5 tables (125 GB): IMPOSSIBLE in any single worker's memory as Python dicts
```

This fundamental constraint eliminates any approach that loads all 5 tables as Python dicts into worker memory. We need either:
- **Reduce what's loaded** (pre-filter, shard, compress)
- **Don't load into memory** (external lookup, GCS-based, BQ post-process)
- **Reduce Python overhead** (columnar/compact storage like DuckDB/SQLite)

---

## 2. Option 1: Side Inputs at Scale

### How Side Inputs Work in Dataflow

Side inputs allow passing additional data to a DoFn alongside the main PCollection. In Dataflow:

1. **Streaming Engine enabled** (default since ~2023): Side inputs stored outside worker memory with an **80 MB size limit**.
2. **Streaming Engine disabled**: Side inputs are materialized in worker memory. Python SDK: one copy per SDK process. Memory grows linearly with vCPUs.
3. **Side input views**: `AsDict`, `AsList`, `AsMultiMap`, `AsIterable`, `AsSingleton`.

### Side Input Distribution

```
With Streaming Engine:
  - Side inputs stored in Streaming Engine backend
  - Workers access via RPC, cached locally up to max_cache_memory_usage_mb
  - HARD LIMIT: 80 MB per side input
  - Cache default: 100 MB total (SDK 2.52+)

Without Streaming Engine:
  - Side input fully materialized in each worker's memory
  - One copy per Python SDK process (not per thread)
  - No hard size limit, but bounded by worker RAM
```

### The `max_cache_memory_usage_mb` Parameter

```python
# Pipeline options (SDK 2.52.0+)
--max_cache_memory_usage_mb=500  # default 100 MB for SDK 2.52-2.54, 0 for others
```

This controls the local side input cache size when using Streaming Engine. Even if you increase it to 500 MB or 1 GB, 75M rows as Python dicts (~125 GB) is impossible.

### Slowly Changing Side Input Pattern

The standard Beam pattern for refreshing side inputs:

```python
from apache_beam.transforms.periodicsequence import PeriodicImpulse

# Refresh lookup table every hour
side_input = (
    p
    | "Impulse" >> PeriodicImpulse(
        fire_interval=3600,  # seconds
        apply_windowing=True,
    )
    | "ReadBQ" >> beam.FlatMap(
        lambda _: ReadAllFromBigQuery(
            query="SELECT key, col1, col2 FROM `project.dataset.lookup_table`",
            use_standard_sql=True,
        )
    )
    | "Window" >> beam.WindowInto(
        beam.transforms.window.GlobalWindows(),
        trigger=beam.transforms.trigger.Repeatedly(
            beam.transforms.trigger.AfterProcessingTime(0)
        ),
        accumulation_mode=beam.transforms.trigger.AccumulationMode.DISCARDING,
    )
    | "Latest" >> beam.combiners.Latest.globally()
    | "AsDict" >> beam.pvalue.AsSingleton()  # or AsDict, AsMultiMap
)

# Use in main pipeline
enriched = (
    events
    | "Enrich" >> beam.ParDo(EnrichDoFn(), lookup=side_input)
)
```

### Side Input View Types for Lookups

| View Type | Use Case | Memory | Lookup Speed |
|-----------|----------|--------|-------------|
| `AsDict` | Key-value lookup | Full dict in memory | O(1) |
| `AsMultiMap` | One-to-many key lookup | Full map in memory | O(1) + iterate |
| `AsSingleton` | Single value (e.g., whole dict) | Full object in memory | O(1) |
| `AsIterable` | Streaming iteration | Lazy, lower memory | O(n) scan |
| `AsList` | Random access by index | Full list in memory | O(1) by index |

For key-value lookups, `AsDict` or `AsMultiMap` are correct. But they require materializing the entire dataset.

### Indexed Side Inputs (Dataflow-specific optimization)

Dataflow (batch mode) supports "indexed side inputs" where the runner doesn't load all values into memory -- it only loads values matching the requested key. This is an important optimization for `AsMultiMap` views.

**However**: This optimization applies to **Dataflow batch** runner. In **streaming** mode with Streaming Engine, the 80 MB limit applies regardless.

### Feasibility Assessment

```
15M rows x 1.7 KB/row = ~25 GB per table

Streaming Engine: 80 MB limit → CAN LOAD 0.003% of one table → IMPOSSIBLE
No Streaming Engine: 25 GB per table → need n1-highmem-8+ per worker → EXTREMELY EXPENSIVE

Side input refresh for 15M rows:
  - BQ read time: 15M rows via ReadFromBigQuery ≈ 5-15 minutes
  - Transfer + materialize: additional 5-10 minutes
  - Total: 10-25 minutes per refresh, during which watermark may be blocked
```

### Verdict: ELIMINATED

**Side inputs are designed for data that "fits in worker memory" (Beam docs).** At 15M rows per table:
- Streaming Engine: blocked by 80 MB hard limit
- Without Streaming Engine: requires 25+ GB per table per worker, 125+ GB for all 5
- Refresh latency: 10-25 minutes for full reload
- Watermark blocking during refresh causes pipeline stalling

**Practical side input limit**: ~100K-1M rows (depending on row size) to stay under 1 GB.

---

## 3. Option 2: Beam Enrichment Transform (BigQueryEnrichmentHandler)

### What It Is

The `Enrichment` transform (Beam 2.54.0+) provides a built-in way to enrich streaming data from external sources. The `BigQueryEnrichmentHandler` (Beam 2.57.0+) specifically enables BQ-based lookups.

### API (Beam 2.71.0)

```python
from apache_beam.transforms.enrichment import Enrichment
from apache_beam.transforms.enrichment_handlers.bigquery import BigQueryEnrichmentHandler

handler = BigQueryEnrichmentHandler(
    project="my-project",
    table_name="project.dataset.lookup_table",
    row_restriction_template="partner_code = '{}'",
    fields=["partner_code"],
    column_names=["partner_code", "partner_name", "region"],  # optional, default *
    min_batch_size=100,
    max_batch_size=10_000,
)

enriched = (
    events
    | "Enrich" >> Enrichment(
        source_handler=handler,
        join_fn=my_join_fn,      # default: cross_join
        timeout=30,              # seconds
    )
)
```

### How It Works Internally

1. Elements are batched via `beam.BatchElements` (min/max batch size).
2. For each batch, the handler constructs a BQ query with `row_restriction_template` and the batch of keys.
3. Results are joined back to original elements via `join_fn`.
4. Built-in retry with exponential backoff and client-side adaptive throttling.

### Batching Behavior

```
At 100K msg/sec, with max_batch_size=10,000:
  → 10 batches/sec per enrichment
  → 5 enrichments (5 tables) = 50 BQ requests/sec
  → 4,320,000 BQ requests/day
```

### Caching Options

| Cache Type | Available? | Details |
|-----------|-----------|---------|
| **Redis** | Yes | `enrichment.with_redis_cache(host, port, time_to_live=3600)` |
| **In-memory** | No built-in | No `with_memory_cache()` method exists |
| **Custom** | Possible | Would require custom EnrichmentSourceHandler |

**Critical limitation**: The only built-in cache is Redis, which violates the "no external instances" constraint. There is no in-memory/local caching option built into the Enrichment transform.

### Cost Analysis (Without Caching)

```
BQ query cost with batching:
  - Each request scans the table with WHERE clause
  - BQ minimum charge: 10 MB per query
  - 50 requests/sec * 86,400 sec/day = 4,320,000 queries/day
  - 4,320,000 * 10 MB = 43,200,000 MB = ~43 TB/day scanned
  - At $6.25/TB = $270/day = $8,100/month

BQ quota concerns:
  - Default concurrent query limit: 100
  - 50 req/sec is feasible but leaves little headroom
  - At 100K msg/sec, could spike higher with worker scaling
```

### Custom Handler with In-Memory Cache (Hybrid)

You could write a custom handler that maintains a local cache:

```python
class CachedBQEnrichmentHandler(EnrichmentSourceHandler):
    """Custom handler with worker-local in-memory cache."""

    def __init__(self, table_config, cache_ttl_sec=3600):
        self._table_config = table_config
        self._cache_ttl = cache_ttl_sec
        self._cache = {}
        self._cache_loaded_at = 0

    def __call__(self, request, *args, **kwargs):
        self._maybe_refresh_cache()
        key = self._extract_key(request)
        cached = self._cache.get(key)
        if cached:
            return beam.Row(**{**request._asdict(), **cached})
        return request  # miss: return unenriched

    def _maybe_refresh_cache(self):
        if time.time() - self._cache_loaded_at > self._cache_ttl:
            # Load full table into local dict
            client = bigquery.Client()
            self._cache = {
                row["key"]: dict(row)
                for row in client.query(f"SELECT * FROM `{self._table}`").result()
            }
            self._cache_loaded_at = time.time()
```

But this is essentially the MasterCache pattern wrapped in an Enrichment handler -- same memory constraints apply.

### Verdict: PROBLEMATIC (without caching) / EQUIVALENT TO MASTERCACHE (with custom cache)

**Without caching**: $8,100/month BQ cost at 100K msg/sec + quota risk. Not viable.
**With Redis cache**: Viable but violates "no external instances" constraint.
**With custom in-memory cache**: Same as MasterCache pattern -- memory limited.

---

## 4. Option 3: CoGroupByKey with Periodic BQ Reads

### How It Works

Read batch tables periodically into PCollections, window both sides, and join via CoGroupByKey.

```python
# Periodic batch read (every hour)
batch_data = (
    p
    | "Impulse" >> PeriodicImpulse(fire_interval=3600)
    | "ReadBQ" >> beam.FlatMap(lambda _: read_all_from_bq("lookup_table"))
    | "Key" >> beam.Map(lambda r: (r["lookup_key"], r))
    | "Window" >> beam.WindowInto(beam.window.GlobalWindows())
)

# Streaming events
events = (
    kafka
    | "KeyEvents" >> beam.Map(lambda e: (e["lookup_key"], e))
    | "WindowEvents" >> beam.WindowInto(beam.window.GlobalWindows())
)

# Join
joined = (
    {"events": events, "batch": batch_data}
    | beam.CoGroupByKey()
    | beam.FlatMap(merge_fn)
)
```

### Problems at Scale

1. **Shuffle volume**: 75M rows must be shuffled through Dataflow's shuffle service every refresh cycle. At ~150 bytes/row (serialized), that's ~11 GB per shuffle per table, ~55 GB total.

2. **Window alignment**: Matching unbounded (streaming) with "refreshed bounded" data in GlobalWindows requires careful trigger management. Late-arriving events may miss the latest batch data.

3. **Hot keys**: If join keys are skewed (common partner_code values), CoGroupByKey concentrates all data for that key on one worker -- causing OOM.

4. **Watermark complexity**: The batch side's watermark must be managed to avoid blocking the streaming side. This is notoriously difficult.

5. **State accumulation**: In GlobalWindows, previous batch data accumulates unless explicitly cleared. 75M rows per refresh cycle = growing state.

### Cost

```
Dataflow shuffle: ~55 GB per refresh x 24 refreshes/day = ~1.3 TB/day
Shuffle pricing: included in Streaming Engine pricing ($0.018/GB processed)
  = ~$24/day = ~$720/month just for shuffle

BQ read: 5 tables x ~2 GB x 24/day = ~240 GB/day
  = ~$1.50/day = ~$45/month

Total: ~$765/month + significant worker memory for processing
```

### Verdict: ELIMINATED

Too complex, too fragile, too expensive. CoGroupByKey is designed for joining two streaming sources or two bounded sources -- not for a streaming source + periodically-refreshed bounded source at 75M rows.

---

## 5. Option 4: MasterCache Scaled Up (Current Pattern)

### Current Implementation

The existing `MasterCache` in `sales-collector/src/domain/bq_lookup_cache.py`:
- Singleton per worker process
- Thread-safe (double-checked locking with `threading.Lock`)
- BQ client created per refresh
- Atomic swap of `_data` dict on refresh
- Configurable refresh interval (default 3600s)

### Can It Scale to 15M Rows Per Table?

**Memory**: As calculated in Section 1, 15M rows as Python dict ≈ 25 GB per table. For 5 tables: ~125 GB. This does NOT fit in any practical Dataflow worker.

**Refresh time**: Reading 15M rows from BQ via `client.query().result()`:
```
BQ query execution: ~30-60 seconds for SELECT * FROM 15M-row table
Result iteration in Python: 15M rows x ~0.1ms/row = ~25 minutes
  (Python BQ client iterates rows one-by-one, creates Row objects)
Total: ~26-30 minutes per table, ~2.5 hours for 5 tables

During refresh: other threads use stale data (safe due to atomic swap)
After refresh: new data visible to all threads
```

**Thread safety during refresh**: The current pattern is safe -- `_data` is swapped atomically (Python GIL protects reference assignment). Other threads continue using the old dict during refresh.

### Optimizations to Consider

**A. Column pruning**: Only SELECT needed columns (e.g., key + 3 value columns instead of 10).
```
Reduction: 10 cols → 4 cols ≈ 60% less data
15M rows x 4 cols x ~100 bytes = ~6 GB per table (from 25 GB)
5 tables = ~30 GB (from 125 GB)
Still too large for most workers.
```

**B. Row pruning (WHERE clause)**: If you can filter by a partition or active rows:
```
15M rows → 5M active rows = 67% reduction
5M x 1.7 KB = ~8.5 GB per table
5 tables = ~42 GB -- fits in n1-highmem-16 (104 GB, ~70 GB available)
```

**C. Value compression (msgpack/pickle)**: Store values as serialized bytes, deserialize on lookup.
```
15M rows, values stored as msgpack bytes (~150 bytes/row):
  Key (str ~80 bytes) + value (bytes ~150 bytes) + dict overhead (36 bytes) = ~266 bytes/row
  15M x 266 bytes = ~4 GB per table
  5 tables = ~20 GB -- fits in n1-highmem-8 (52 GB, ~35 GB available)

Trade-off: ~1-5 microseconds deserialization per lookup (msgpack.unpackb)
At 100K msg/sec x 5 lookups: 500K deserializations/sec ≈ 2.5 seconds of CPU/sec
  → Would need ~3 vCPUs just for deserialization overhead
```

### Verdict: PARTIALLY VIABLE (with aggressive optimization)

Scaling MasterCache to 15M rows/table requires:
- Column and row pruning to reduce data volume
- Possibly value compression (at CPU cost)
- n1-highmem-8 or larger workers (~$860/month per worker)
- 25-30 minute refresh time per table (blocking one thread)

**Viable only if** total lookup data can be reduced to ~20-30 GB through pruning/filtering.

---

## 6. Option 5: `beam.utils.shared.Shared` Class Pattern

### What It Is

Apache Beam provides `apache_beam.utils.shared.Shared` -- a utility for sharing a single object instance across all DoFn instances in the same worker process. It uses weak references for memory management and supports tag-based cache invalidation for periodic refresh.

### How It Differs from MasterCache

| Aspect | MasterCache (current) | Shared class |
|--------|----------------------|--------------|
| Lifecycle | Module-level singleton | Beam-managed weak reference |
| Memory | Strong reference, never GC'd | Weak reference, can be GC'd if no DoFn holds it |
| Refresh | Timer-based (`time.monotonic()`) | Tag-based (`acquire(fn, tag)`) |
| Thread safety | Manual (Lock) | Beam-managed |
| Multi-DoFn sharing | Via module import | Via shared handle |
| Testability | Hard to mock | Easier (inject handle) |

### Code Example

```python
import time
import apache_beam as beam
from apache_beam.utils.shared import Shared
from google.cloud import bigquery

class WeakRefDict(dict):
    """Wrapper to allow weak references to a dict."""
    pass

class EnrichWithSharedCache(beam.DoFn):
    def __init__(self, table_id, key_columns, refresh_interval_sec=3600):
        self._table_id = table_id
        self._key_columns = key_columns
        self._refresh_interval = refresh_interval_sec
        self._shared_handle = Shared()
        self._current_tag = None

    def _get_tag(self):
        """Returns a new tag every refresh_interval seconds."""
        return str(int(time.time() / self._refresh_interval))

    def _load_cache(self):
        """Load lookup table from BQ into a WeakRefDict."""
        client = bigquery.Client()
        cache = WeakRefDict()
        for row in client.query(f"SELECT * FROM `{self._table_id}`").result():
            key = "::".join(str(row[c]) for c in self._key_columns)
            cache[key] = dict(row)
        cache["__tag__"] = self._get_tag()
        return cache

    def start_bundle(self):
        """Check if cache needs refresh at bundle start."""
        new_tag = self._get_tag()
        if new_tag != self._current_tag:
            self._cache = self._shared_handle.acquire(self._load_cache, new_tag)
            self._current_tag = new_tag
        else:
            self._cache = self._shared_handle.acquire(self._load_cache)

    def process(self, element):
        key = "::".join(str(element.get(c, "")) for c in self._key_columns)
        lookup_result = self._cache.get(key)
        if lookup_result:
            element.update(lookup_result)
        yield element
```

### Advantages Over MasterCache

1. **Beam-managed lifecycle**: The Shared object handles thread safety internally.
2. **Memory cleanup**: Weak references allow GC when no DoFn holds the cache (useful during scaling down).
3. **Tag-based invalidation**: Clean refresh mechanism aligned with Beam's processing model.
4. **Better testability**: Inject shared handle in tests.

### Same Memory Constraint

The Shared class is an API improvement, not a memory improvement. The data still needs to fit in worker memory. The same 25 GB/table calculation applies.

### Verdict: BETTER API, SAME MEMORY PROBLEM

Use Shared instead of MasterCache for cleaner code, but it doesn't solve the fundamental memory problem for 15M-row tables.

---

## 7. Option 6: DuckDB/SQLite as Worker-Local Lookup

### The Idea

Instead of loading 75M rows into a Python dict (125 GB), load them into an in-process database (DuckDB or SQLite) that uses disk-backed storage with memory-mapped I/O. This dramatically reduces memory usage while maintaining fast lookups.

### DuckDB Approach

```python
import duckdb
import apache_beam as beam
from apache_beam.utils.shared import Shared
from google.cloud import bigquery, storage

class DuckDBLookup:
    """Worker-local DuckDB instance for large lookup tables."""

    def __init__(self, gcs_paths: dict[str, str], refresh_interval: int = 3600):
        self._gcs_paths = gcs_paths  # {"table_name": "gs://bucket/table.parquet"}
        self._refresh_interval = refresh_interval
        self._conn = None
        self._loaded_at = 0

    def setup(self):
        """Create in-memory DuckDB instance and load from GCS Parquet."""
        self._conn = duckdb.connect()  # in-memory, but can also use temp file
        self._conn.execute("INSTALL httpfs; LOAD httpfs;")
        self._conn.execute("SET s3_region='us-central1';")  # for GCS
        self._load_tables()

    def _load_tables(self):
        for name, path in self._gcs_paths.items():
            self._conn.execute(f"""
                CREATE OR REPLACE TABLE {name} AS
                SELECT * FROM read_parquet('{path}')
            """)
            count = self._conn.execute(f"SELECT count(*) FROM {name}").fetchone()[0]
            logging.info(f"DuckDB: loaded {name} with {count:,} rows")
        self._loaded_at = time.time()

    def lookup(self, table: str, key_col: str, key_val: str) -> dict | None:
        result = self._conn.execute(
            f"SELECT * FROM {table} WHERE {key_col} = ?", [key_val]
        ).fetchone()
        if result:
            cols = [desc[0] for desc in self._conn.description]
            return dict(zip(cols, result))
        return None

    def needs_refresh(self):
        return time.time() - self._loaded_at > self._refresh_interval


class EnrichWithDuckDB(beam.DoFn):
    def __init__(self, gcs_parquet_paths, key_columns_map):
        self._gcs_paths = gcs_parquet_paths
        self._key_columns_map = key_columns_map
        self._db = None

    def setup(self):
        self._db = DuckDBLookup(self._gcs_paths)
        self._db.setup()

    def process(self, element):
        for table, key_cols in self._key_columns_map.items():
            key_val = "::".join(str(element.get(c, "")) for c in key_cols)
            result = self._db.lookup(table, key_cols[0], key_val)
            if result:
                element.update(result)
        yield element
```

### Memory Usage: DuckDB vs Python Dict

```
DuckDB in-memory mode:
  - Uses columnar storage internally (Arrow-compatible)
  - 15M rows x 10 cols ≈ 2-4 GB per table (columnar, compressed)
  - 5 tables ≈ 10-20 GB
  - vs Python dict: 125 GB

DuckDB disk-backed mode (temp file):
  - Data spills to local SSD
  - Memory buffer configurable (e.g., 2 GB)
  - Lookup latency: ~0.1-1ms for indexed lookup (vs ~0.001ms for dict)
  - 5 tables fit on any worker's local disk
```

### SQLite Alternative

```python
import sqlite3
import tempfile

class SQLiteLookup:
    """Worker-local SQLite for disk-backed lookup."""

    def __init__(self, refresh_interval=3600):
        self._refresh_interval = refresh_interval
        self._db_path = None
        self._conn = None

    def setup(self):
        self._db_path = tempfile.mktemp(suffix=".db")
        self._conn = sqlite3.connect(self._db_path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA cache_size=-50000")  # 50MB page cache
        self._load_from_bq()

    def _load_from_bq(self):
        client = bigquery.Client()
        # Create table + index
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS lookup (
                key TEXT PRIMARY KEY,
                col1 TEXT, col2 TEXT, col3 INTEGER, ...
            )
        """)
        # Bulk insert
        rows = client.query("SELECT * FROM `project.dataset.table`").result()
        self._conn.executemany(
            "INSERT OR REPLACE INTO lookup VALUES (?, ?, ?, ?, ...)",
            [(row["key"], row["col1"], ...) for row in rows]
        )
        self._conn.commit()

    def lookup(self, key):
        cur = self._conn.execute("SELECT * FROM lookup WHERE key = ?", (key,))
        row = cur.fetchone()
        if row:
            return dict(zip([d[0] for d in cur.description], row))
        return None
```

### SQLite Memory Usage

```
SQLite disk-backed:
  - Page cache configurable (e.g., 50 MB)
  - Data on local SSD: 15M rows ≈ 2-3 GB per table file
  - Index: ~500 MB per table (B-tree on primary key)
  - Total disk: ~15-20 GB for 5 tables
  - Total memory: ~250 MB (page caches)
  - Lookup latency: ~0.05-0.5ms (indexed B-tree lookup)
```

### Comparison: DuckDB vs SQLite vs Python Dict

| Metric | Python Dict | DuckDB (in-mem) | DuckDB (disk) | SQLite (disk) |
|--------|------------|-----------------|---------------|---------------|
| **Memory (5 tables)** | ~125 GB | ~10-20 GB | ~2-5 GB | ~250 MB |
| **Disk** | 0 | 0 | ~15-20 GB | ~15-20 GB |
| **Lookup latency** | ~1 us | ~50 us | ~100-500 us | ~50-500 us |
| **Load time (15M rows)** | ~25 min (BQ) | ~3-5 min (Parquet) | ~3-5 min | ~10-15 min (BQ) |
| **Refresh** | Atomic swap | Reload | Reload | Reload |
| **Thread safety** | Manual lock | DuckDB handles | DuckDB handles | WAL mode OK |
| **Dependency** | None (stdlib) | duckdb package | duckdb package | sqlite3 (stdlib) |

### Practical Concerns

1. **DuckDB on Dataflow**: DuckDB is a C++ library with Python bindings. Must be included in the Docker container image. Works fine with custom containers.

2. **SQLite on Dataflow**: Built into Python stdlib. No extra dependencies.

3. **Concurrent access**: DuckDB and SQLite both handle concurrent reads from multiple threads. SQLite in WAL mode allows concurrent reads during writes.

4. **Refresh strategy**: During refresh, either serve stale data (double-buffering) or block briefly while swapping.

5. **GCS Parquet read**: DuckDB can read Parquet directly from GCS via httpfs extension. Avoids the slow BQ python client iteration.

### Verdict: HIGHLY VIABLE (especially SQLite for simplicity, DuckDB for performance)

This is the most promising "pure Dataflow" approach for truly large lookup tables. Memory footprint drops from 125 GB to 250 MB-20 GB depending on configuration.

**Best for**: When lookup tables are genuinely 15M+ rows and must be queryable at the worker level.

---

## 8. Option 7: Bloom Filter Pre-Filter + Selective Lookup

### The Idea

Most streaming events may only need lookups from a small subset of the lookup table. Use a Bloom filter (compact probabilistic data structure) as a first-pass filter:

1. Build Bloom filter from lookup table keys (compact: ~1-2 bytes per key)
2. For each streaming event, check Bloom filter first
3. If "probably exists" -> do the full lookup (from BQ, GCS, or local DB)
4. If "definitely not exists" -> skip lookup entirely

### Memory for Bloom Filter

```
15M keys, 1% false positive rate:
  - Optimal bits per key: -ln(0.01) / (ln(2))^2 ≈ 9.6 bits
  - Total: 15M * 9.6 bits = 144 Mbit = 18 MB per table
  - 5 tables = 90 MB total
  - Fits easily in any worker's memory
```

### Code Example

```python
from pybloom_live import ScalableBloomFilter
# or: from bitarray import bitarray + mmh3 for custom implementation

class BloomFilterPreFilter(beam.DoFn):
    def __init__(self, bloom_gcs_path, fallback_lookup):
        self._bloom_path = bloom_gcs_path
        self._fallback = fallback_lookup
        self._bloom = None

    def setup(self):
        # Load serialized bloom filter from GCS (~18 MB)
        from google.cloud import storage
        bucket = storage.Client().bucket("my-bucket")
        blob = bucket.blob(self._bloom_path)
        self._bloom = pickle.loads(blob.download_as_bytes())

    def process(self, element):
        key = element["lookup_key"]
        if key in self._bloom:  # O(1), may have false positive
            # Full lookup needed
            result = self._fallback.lookup(key)  # BQ, GCS, or local DB
            if result:
                element.update(result)
        # else: definitely not in lookup table, skip
        yield element
```

### When This Helps

- If only 5-10% of streaming events match a lookup key -> 90-95% skip the expensive lookup
- Combined with DuckDB/SQLite: Bloom filter eliminates 90% of DB lookups
- Combined with Enrichment transform: reduces BQ queries by 90%

### When This Doesn't Help

- If most events (>80%) match a lookup key -> Bloom filter is overhead with little benefit
- If all 5 lookups are needed for every event -> no filtering possible

### Verdict: USEFUL AS AN OPTIMIZATION LAYER

Not a standalone solution, but valuable when combined with DuckDB/SQLite or Enrichment transform. Reduces lookup load by the miss rate percentage.

---

## 9. Option 8: GCS Parquet/Avro Lookup on Worker Startup

### The Idea

Pre-export lookup tables as Parquet files on GCS. Each worker downloads and loads them during `setup()`.

```
Batch job (daily): BQ lookup tables → Parquet on GCS
Worker startup: Download Parquet from GCS → load into DuckDB/pandas/dict
Runtime: Lookup from local loaded data
```

### Benefits Over Direct BQ Reads

```
BQ Python client: 15M rows ≈ 25-30 minutes (row-by-row iteration)
Parquet via GCS:   15M rows ≈ 2-5 minutes (columnar bulk read)
  - Parquet file size: ~500 MB - 1 GB per table (compressed)
  - GCS download speed: ~500 MB/s within same region
  - Download time: ~2 seconds per table
  - Parse time: ~1-3 minutes (pyarrow/duckdb)
```

### Implementation

```python
import pyarrow.parquet as pq
from google.cloud import storage

class GCSParquetLookup:
    """Load Parquet files from GCS into worker-local storage."""

    def __init__(self, gcs_paths: dict[str, str]):
        self._gcs_paths = gcs_paths
        self._data: dict[str, dict[str, dict]] = {}

    def setup(self):
        for table_name, gcs_path in self._gcs_paths.items():
            # Read Parquet directly (pyarrow handles GCS natively)
            table = pq.read_table(gcs_path)
            # Convert to lookup dict (still has memory issue for large tables)
            df = table.to_pandas()
            self._data[table_name] = df.set_index("key").to_dict("index")

    def lookup(self, table_name, key):
        return self._data.get(table_name, {}).get(key)
```

**For large tables, combine with DuckDB**:

```python
def setup(self):
    self._conn = duckdb.connect()
    for table_name, gcs_path in self._gcs_paths.items():
        # DuckDB reads Parquet directly from GCS, creates indexed table
        self._conn.execute(f"""
            CREATE TABLE {table_name} AS
            SELECT * FROM read_parquet('{gcs_path}')
        """)
        self._conn.execute(f"CREATE INDEX idx_{table_name} ON {table_name}(key)")
```

### Verdict: VIABLE (best combined with DuckDB/SQLite)

GCS Parquet is the optimal **data transport** mechanism. Combine with DuckDB/SQLite for the **storage/lookup** layer. This is the best pure-Dataflow approach for the data loading step.

---

## 10. Option 9: Sharded/Partitioned In-Memory Lookup

### The Idea

If lookup tables can be partitioned by key (e.g., by partner_code or region), each worker only loads its partition. This reduces per-worker memory proportionally to the number of workers.

```
Full table: 15M rows, 25 GB
10 workers, each loads 1/10: 1.5M rows, 2.5 GB per worker
```

### Implementation Pattern

```python
# Shard streaming events by key
events_by_shard = (
    events
    | "ShardKey" >> beam.Map(lambda e: (hash(e["partner_code"]) % NUM_SHARDS, e))
    | "GroupByShard" >> beam.GroupByKey()
)

# Each worker loads only matching shard's lookup data
class ShardedEnrichDoFn(beam.DoFn):
    def __init__(self, num_shards):
        self._num_shards = num_shards
        self._shard_id = None
        self._cache = {}

    def process(self, element):
        shard_id, events = element
        if shard_id != self._shard_id:
            self._load_shard(shard_id)

        for event in events:
            key = event["partner_code"]
            lookup = self._cache.get(key)
            if lookup:
                event.update(lookup)
            yield event

    def _load_shard(self, shard_id):
        client = bigquery.Client()
        self._cache = {}
        for row in client.query(
            f"SELECT * FROM `table` WHERE MOD(FARM_FINGERPRINT(key), {self._num_shards}) = {shard_id}"
        ).result():
            self._cache[row["key"]] = dict(row)
        self._shard_id = shard_id
```

### Problems

1. **Dataflow doesn't guarantee shard-to-worker affinity**: A worker may process elements from any shard, requiring loading different shards.
2. **GroupByKey introduces latency**: Elements are buffered until the window closes.
3. **Key skew**: If partner distribution is uneven, some shards are much larger than others.
4. **Complexity**: Managing shard assignment and cache loading is error-prone.

### Better Alternative: Key-Based Routing via Beam

```python
# Use Reshuffle to ensure key affinity
keyed_events = events | beam.Map(lambda e: (e["partner_code"], e))

# Stateful DoFn with per-key cache
class StatefulLookupDoFn(beam.DoFn):
    CACHE = beam.transforms.userstate.ReadModifyWriteStateSpec("cache", beam.coders.PickleCoder())

    def process(self, element, cache=beam.DoFn.StateParam(CACHE)):
        key, event = element
        cached = cache.read()
        if cached is None:
            # Load just this key's data from BQ/GCS
            cached = self._lookup_single_key(key)
            cache.write(cached)
        event.update(cached)
        yield event
```

**Problem**: 15M unique keys = 15M state entries per table. Dataflow state backend handles this, but checkpoint size grows large, and per-key BQ lookups are expensive ($5,150/day as calculated in BQ_LOOKUP_TECHNIQUES.md).

### Verdict: PARTIALLY VIABLE (with careful implementation)

Sharding can reduce per-worker memory if implemented correctly. The main challenge is Dataflow's lack of worker-shard affinity guarantees. Best combined with DuckDB/SQLite where each worker loads the full dataset but queries efficiently.

---

## 11. Option 10: Two-Stage Pipeline (Streaming Raw + BQ Post-JOIN)

### The Idea

Don't enrich in the streaming pipeline at all. Write raw/refined data to BQ, then use BQ scheduled queries or materialized views to perform the JOIN.

```
Stage 1 (Streaming, no change):
  Kafka → Dataflow → BQ refined tables (as-is, fast, no enrichment overhead)

Stage 2 (Batch, new):
  BQ Scheduled Query (every 15 min):
    SELECT r.*, l1.*, l2.*, l3.*, l4.*, l5.*
    FROM refined.receipt r
    LEFT JOIN lookup_1 l1 ON r.key1 = l1.key
    LEFT JOIN lookup_2 l2 ON r.key2 = l2.key
    LEFT JOIN lookup_3 l3 ON r.key3 = l3.key
    LEFT JOIN lookup_4 l4 ON r.key4 = l4.key
    LEFT JOIN lookup_5 l5 ON r.key5 = l5.key
    WHERE r.ingestedDate >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 20 MINUTE)
  → analytics.enriched_table
```

### Why This Works

- **BQ handles 75M row JOINs trivially**: BQ's distributed query engine is specifically designed for this.
- **No memory constraints**: Nothing loads into worker memory.
- **No pipeline changes**: Streaming pipeline stays fast and simple.
- **BQ cost is low**: Incremental scans with partition pruning.

### Cost Estimate

```
Incremental scheduled query (every 15 min):
  - Scan new refined rows: ~100 GB/run (15 min of 100K msg/sec)
  - Scan 5 lookup tables: 5 x 2 GB = 10 GB/run
  - Total per run: ~110 GB
  - 96 runs/day: 96 x 110 GB = ~10.6 TB/day
  - On-demand pricing: 10.6 TB x $6.25/TB = ~$66/day = ~$2,000/month

With BQ Editions (flat-rate):
  - Enterprise edition: $0.04/slot-hr
  - ~100 slots for 2-3 minutes per run
  - 100 slots x 0.05 hr x $0.04 x 96 runs = ~$19/day = ~$580/month

With incremental MERGE (process only new rows, insert to partitioned table):
  - Scan only new partition: ~10-20 GB/run
  - 96 runs/day: ~1-2 TB/day = $6-12/day = $180-360/month
```

### Materialized View Alternative

```sql
CREATE MATERIALIZED VIEW analytics.enriched_receipt
PARTITION BY DATE(ingestedDate)
CLUSTER BY partner_code
AS
SELECT r.*, l1.partner_name, l2.branch_name, ...
FROM refined.receipt r
LEFT JOIN lookup_1 l1 ON r.partner_code = l1.partner_code
LEFT JOIN lookup_2 l2 ON r.key2 = l2.key
...
```

BQ materialized views support:
- Star schema JOINs (1 fact + multiple dimension tables) -- matches our case
- Auto-refresh when base tables change
- Incremental maintenance for append-only fact tables
- Dimension tables must be < 100 GB each (our 15M-row tables are ~2 GB each)

### Verdict: STRONGLY RECOMMENDED

This is the simplest, cheapest, and most robust approach. BQ is purpose-built for large JOINs. The streaming pipeline stays unmodified and fast. The only trade-off is 15-minute latency for the enriched view.

---

## 12. Cost Comparison Matrix

Monthly cost for 4 workers processing 50K-100K msg/sec:

| Option | Worker Type | Worker Cost | BQ/Other Cost | Total Monthly | Memory Risk |
|--------|-----------|-------------|---------------|---------------|-------------|
| **1. Side Input** | n1-highmem-16 | $6,880 | $45 BQ reads | $6,925 | OOM likely |
| **2. Enrichment (no cache)** | n1-standard-4 | $1,400 | $8,100 BQ queries | $9,500 | Low |
| **3. CoGroupByKey** | n1-highmem-8 | $3,440 | $765 shuffle+BQ | $4,205 | High |
| **4. MasterCache (optimized)** | n1-highmem-8 | $3,440 | $45 BQ reads | $3,485 | Medium |
| **5. Shared class** | n1-highmem-8 | $3,440 | $45 BQ reads | $3,485 | Medium |
| **6. DuckDB/SQLite** | n1-standard-4 | $1,400 | $10 GCS reads | $1,410 | **Low** |
| **7. Bloom + DuckDB** | n1-standard-4 | $1,400 | $10 GCS reads | $1,410 | **Low** |
| **8. GCS Parquet + DuckDB** | n1-standard-4 | $1,400 | $10 GCS reads | $1,410 | **Low** |
| **9. Sharded in-memory** | n1-highmem-4 | $1,720 | $45 BQ reads | $1,765 | Medium |
| **10. BQ Post-JOIN** | n1-standard-4 | $1,400 | $180-580 BQ | $1,580-1,980 | **None** |

### For reference: External service costs (what we're avoiding)

| Service | Monthly Cost | Notes |
|---------|-------------|-------|
| Redis Memorystore (25 GB) | $882 (Standard) / $288 (Basic) | + VPC peering + sync job |
| Bigtable (1 node) | $468 | Only handles ~10K reads/sec |
| Bigtable (50 nodes, 100K msg/sec) | $23,400 | For 500K reads/sec at peak |

---

## 13. Detailed Cost Analysis: Pure Dataflow vs External Services

### Scenario: 4 workers, 50K msg/sec average, 5 lookup tables x 15M rows

#### Option A: Bigger Dataflow Workers (DuckDB approach)

```
Workers: 4 x n1-standard-4 (15 GB RAM, DuckDB uses <2 GB + local SSD)
  vCPU: 4 workers x 4 vCPU x $0.069/hr = $1.104/hr
  Memory: 4 workers x 15 GB x $0.003557/GB/hr = $0.213/hr
  Streaming Engine: ~$0.018/GB processed (variable)
  Total workers: ~$1.32/hr = ~$950/month

GCS storage for Parquet: 5 tables x 1 GB = 5 GB = ~$0.10/month
GCS reads: negligible
BQ export (daily): free (export to GCS is free)

Total: ~$960/month
```

#### Option B: Standard Workers + Redis Memorystore

```
Workers: 4 x n1-standard-4 (unchanged)
  Total workers: ~$950/month

Redis Memorystore (Standard, 25 GB):
  $0.049/GB/hr x 25 GB = $1.225/hr = $882/month

Sync job (Cloud Function, hourly):
  ~$10/month

Total: ~$1,842/month
```

#### Option C: Standard Workers + Bigtable (1 node)

```
Workers: 4 x n1-standard-4 (unchanged)
  Total workers: ~$950/month

Bigtable:
  1 node: $0.65/hr = $468/month
  Storage (75M rows): ~$3/month

But at 50K msg/sec x 5 lookups = 250K reads/sec:
  Need ~25 nodes: 25 x $468 = $11,700/month !!

Total: ~$12,650/month (with adequate throughput)
```

### Summary

```
DuckDB on Dataflow:   ~$960/month   (cheapest, zero extra infra)
BQ Post-JOIN:         ~$1,580/month (simplest, zero pipeline change)
Redis:                ~$1,842/month (adds infra + ops complexity)
Bigtable (adequate):  ~$12,650/month (dramatically more expensive)
```

---

## Option 11: CDC UPSERT 2 รอบ (Streaming + Post-JOIN UPSERT back)

### Concept

แทนที่จะ enrich ใน pipeline → **UPSERT 2 ครั้ง**:

```
รอบ 1 (Streaming, real-time):
  Kafka → extract fields → UPSERT ลง refined (เฉพาะ fields จาก Kafka)

รอบ 2 (Periodic, ทุก 1-5 นาที):
  อ่าน refined (recent rows) → JOIN กับ 5 lookup tables → UPSERT ทับ refined (เติม enriched fields)
```

### Trigger: Dataflow Windowing vs Dataform?

#### Option A: Dataflow PeriodicImpulse (windowing trigger)

```python
# เพิ่ม branch ใน pipeline เดิม
trigger = (
    p
    | "Trigger" >> PeriodicImpulse(fire_interval=60)  # ทุก 1 นาที
    | "ReadRecent" >> beam.FlatMap(read_recent_from_bq, project=project)
    | "JoinLookups" >> beam.FlatMap(join_with_lookups, lookups=side_lookups)
    | "UpsertBack" >> WriteToBigQuery("refined.sales_receipt", method="CDC")
)
```

**ข้อดี**: อยู่ใน pipeline เดียว, ไม่ต้อง manage service เพิ่ม
**ข้อเสีย**:
- Pipeline อ่าน + เขียน table เดียวกัน (circular dependency risk)
- PeriodicImpulse trigger อยู่ใน streaming pipeline = ถ้า pipeline ตาย enrichment ก็หยุด
- JOIN logic อยู่ใน Python = ช้ากว่า BQ native JOIN
- ต้อง maintain lookup data ใน pipeline (กลับมาปัญหา memory เดิม)
- Pipeline complexity เพิ่มขึ้นมาก

#### Option B: Dataform (Recommended)

```sql
-- dataform: definitions/refined/enrich_sales_receipt.sqlx
config {
  type: "operations",
  hasOutput: false,
  tags: ["sales_enrichment"]
}

MERGE INTO `${ref("sales_receipt")}` AS target
USING (
  SELECT
    r.*,
    lb.branch_name,
    lp.product_category,
    lm.member_segment,
    lt.tender_desc,
    lc.channel_name
  FROM `${ref("sales_receipt")}` r
  LEFT JOIN `${ref("lookup_branch")}` lb
    ON r.partner_code = lb.partner_code AND r.branch_code = lb.branch_code
  LEFT JOIN `${ref("lookup_product")}` lp
    ON r.partner_code = lp.partner_code AND r.sku = lp.sku
  LEFT JOIN `${ref("lookup_member")}` lm
    ON r.member_id = lm.member_id
  LEFT JOIN `${ref("lookup_tender")}` lt
    ON r.payment_type = lt.tender_type
  LEFT JOIN `${ref("lookup_channel")}` lc
    ON r.transaction_channel_id = lc.channel_id
  WHERE r.transaction_date >= DATETIME_SUB(CURRENT_DATETIME("Asia/Bangkok"), INTERVAL 10 MINUTE)
    AND r.branch_name IS NULL  -- only enrich rows that haven't been enriched yet
) AS source
ON target.receipt_number = source.receipt_number
  AND target.partner_code = source.partner_code
  AND target.branch_code = source.branch_code
  AND target.sale_type_code = source.sale_type_code
  AND target.transaction_date = source.transaction_date
  AND target.display_receipt_number = source.display_receipt_number
WHEN MATCHED THEN UPDATE SET
  target.branch_name = source.branch_name,
  target.product_category = source.product_category,
  target.member_segment = source.member_segment,
  target.tender_desc = source.tender_desc,
  target.channel_name = source.channel_name
```

Scheduled via Cloud Scheduler → Dataform API:
```bash
# ทุก 5 นาที
*/5 * * * * dataform run --tag=sales_enrichment
```

**ข้อดี**:
- **Separation of concerns**: streaming pipeline ทำแค่ raw extract, Dataform ทำ enrichment
- **BQ native JOIN**: 75M-row JOIN ทำใน BQ engine = เร็ว, ไม่ต้อง load data เข้า memory
- **Idempotent**: MERGE + `WHERE branch_name IS NULL` = enrich เฉพาะ rows ที่ยังไม่ enriched
- **No extra infrastructure**: Dataform = serverless, ไม่มี instance
- **Version controlled**: SQL อยู่ใน git
- **Dependency management**: Dataform จัดการ dependency ระหว่าง tables ได้
- **Already in codebase**: coupons-collector ใช้ Dataform อยู่แล้ว

**ข้อเสีย**:
- Latency 1-5 นาที (ไม่ใช่ real-time ทันที)
- ต้อง setup Dataform workspace + Cloud Scheduler

### Cost

```
BQ MERGE query (every 5 min):
  Scan: ~recent 5 min data (~1 MB) + 5 lookup tables (~2 GB each)
  = ~10 GB per query × 12/hour × 24 hours = ~2.88 TB/day
  On-demand: 2.88 TB × $6.25/TB = ~$18/day = ~$540/month

  With partitioning + clustering optimization:
  Scan per query: ~500 MB (partition pruning on transaction_date)
  = ~144 GB/day × $6.25/TB = ~$0.90/day = ~$27/month

  With flat-rate slots (shared): effectively $0 marginal

Dataform: FREE (included in BQ)
Cloud Scheduler: $0.10/job/month = negligible
```

### Option B2: Dataflow PeriodicImpulse → BQ MERGE (Recommended)

ใช้ Dataflow เป็น **trigger only** — JOIN ทำใน BQ engine ไม่ load data เข้า memory:

```python
# เพิ่ม branch ใน pipeline เดิม (main.py)
ENRICHMENT_MERGE_SQL = """
MERGE INTO `{project}.refined.sales_receipt` AS target
USING (
  SELECT
    r.*,
    lb.branch_name,
    lp.product_category,
    lm.member_segment
  FROM `{project}.refined.sales_receipt` r
  LEFT JOIN `{project}.refined.lookup_branch` lb
    ON r.partner_code = lb.partner_code AND r.branch_code = lb.branch_code
  LEFT JOIN `{project}.refined.lookup_product` lp
    ON r.partner_code = lp.partner_code
  LEFT JOIN `{project}.refined.lookup_member` lm
    ON r.member_id = lm.member_id
  WHERE r.transaction_date >= DATETIME_SUB(CURRENT_DATETIME("Asia/Bangkok"), INTERVAL 10 MINUTE)
    AND r.branch_name IS NULL  -- only un-enriched rows
) AS source
ON target.receipt_number = source.receipt_number
  AND target.partner_code = source.partner_code
  AND target.branch_code = source.branch_code
  AND target.sale_type_code = source.sale_type_code
  AND target.transaction_date = source.transaction_date
  AND target.display_receipt_number = source.display_receipt_number
WHEN MATCHED THEN UPDATE SET
  target.branch_name = source.branch_name,
  target.product_category = source.product_category,
  target.member_segment = source.member_segment
"""

def _run_bq_enrichment(timestamp_element, project):
    """Fire BQ MERGE — Dataflow is just the trigger, BQ does the heavy lifting."""
    from google.cloud import bigquery
    client = bigquery.Client(project=project)
    job = client.query(ENRICHMENT_MERGE_SQL.format(project=project))
    job.result()  # wait for completion
    logging.info("Enrichment MERGE completed: %s rows affected", job.num_dml_affected_rows)

# In pipeline construction (alongside existing branches)
_ = (
    p
    | "EnrichTrigger" >> PeriodicImpulse(fire_interval=300)  # ทุก 5 นาที
    | "RunBqMerge" >> beam.Map(_run_bq_enrichment, project=project)
)
```

**ข้อดี**:

- **Control flow ที่ Dataflow ที่เดียว** — ไม่ต้อง manage Cloud Scheduler / Dataform แยก
- **BQ engine ทำ JOIN** — 75M rows สบาย, ไม่ load data เข้า pipeline memory
- **Pipeline lifecycle เดียวกัน** — pipeline ตาย = enrichment หยุดด้วย (ถูกต้อง เพราะถ้า streaming หยุด ก็ไม่มี data ใหม่ให้ enrich)
- **Pattern คุ้นเคย** — เหมือน `PeriodicImpulse` → BQ metadata refresh ที่ loyalty members-collector ใช้อยู่
- **ไม่ต้อง infra เพิ่ม** — ไม่มี Redis, Bigtable, Cloud Scheduler, Dataform workspace
- **SQL อยู่ใน codebase** — version controlled, review ได้ใน MR
- **Idempotent** — `WHERE branch_name IS NULL` = enrich เฉพาะ rows ที่ยังไม่ enriched
- **Config-driven** — `fire_interval` ปรับได้จาก YAML

**ข้อเสีย vs Cloud Scheduler + Dataform**:

- Pipeline restart = enrichment gap (แต่ catch up ได้เพราะ `INTERVAL 10 MINUTE` window)
- PeriodicImpulse fire ไม่ precise เท่า cron (±seconds, ไม่เป็นปัญหา)
- ถ้า BQ MERGE ช้า (>5 min) อาจ overlap กับ trigger ถัดไป — แก้ได้ด้วย lock/flag
- SQL อยู่ใน Python string แทน `.sqlx` file — อ่านยากกว่านิดหน่อย (แก้ได้โดยแยกเป็น `.sql` file แล้ว load)
- Dataform มี dependency management + lineage ที่ดีกว่า — แต่สำหรับ single MERGE query ไม่จำเป็น

**เมื่อไหร่ควรย้ายไป Dataform แทน**:

- เมื่อ enrichment SQL เพิ่มเป็น >3-5 queries ที่มี dependency กัน
- เมื่อต้องการ lineage tracking / data quality checks
- เมื่อทีมอื่นต้อง maintain enrichment SQL ด้วย

### Verdict: RECOMMENDED

**Option B2 (PeriodicImpulse → BQ MERGE)** เป็น sweet spot ที่ดีที่สุดสำหรับ sales-collector:

1. **ง่ายกว่า** Dataform — ไม่ต้อง setup workspace, scheduler แยก
2. **ดีกว่า** Dataflow windowing (Option A) — ไม่ load data เข้า memory, ใช้ BQ engine
3. **ถูกกว่า** Redis/Bigtable — ไม่มี instance cost
4. **Control flow ที่เดียว** — DevOps ดูแลแค่ Dataflow pipeline
5. **Scale ได้ในอนาคต** — ถ้า complex ขึ้น ค่อยย้ายไป Dataform

Cost เท่ากับ Option B (Dataform) = ~$27-540/mo ขึ้นกับ partition optimization

---

## 14. Final Recommendation

### Ranked by "Pure Dataflow, No Extra Infrastructure" Preference

#### Rank 1: BQ Post-JOIN (Option 10) -- IF 15-minute latency is acceptable

**The pragmatic winner.**

- Zero changes to streaming pipeline
- Zero extra memory on workers
- Zero extra infrastructure
- BQ handles 75M-row JOINs natively and efficiently
- ~$180-580/month BQ cost (with optimization)
- Implementation: 1 SQL scheduled query + Cloud Scheduler

**Choose this if**: Analytics/reporting layer tolerates 15+ minute latency (almost always true when batch dimension tables are themselves updated daily/hourly).

#### Rank 2: DuckDB/SQLite Worker-Local Lookup (Options 6/8) -- IF real-time enrichment is required

**The best pure-Dataflow approach for real-time enrichment.**

- Worker memory: <2 GB (SQLite with page cache) or <20 GB (DuckDB in-memory)
- Lookup latency: <1ms per lookup
- No external services
- Standard n1-standard-4 workers sufficient
- ~$960/month total

**Implementation plan:**
1. Daily batch job: Export lookup tables from BQ to GCS as Parquet
2. Worker `setup()`: Load Parquet into DuckDB (or import into SQLite)
3. `process()`: Local lookup, sub-millisecond latency
4. Refresh: Tag-based via `Shared` class, or recreate DB every N hours

**SQLite (recommended for simplicity)**:
- Built into Python stdlib (no extra dependency)
- Disk-backed with configurable page cache
- WAL mode for concurrent reads
- Well-understood, battle-tested

**DuckDB (recommended for performance)**:
- Columnar storage, better compression
- Direct GCS Parquet reading
- Faster bulk loads
- ~50 us lookup vs ~200 us for SQLite (both are sub-ms)

#### Rank 3: Optimized MasterCache / Shared Class (Options 4/5) -- IF data can be aggressively pruned

**Only viable if total lookup data can be reduced to <20-30 GB.**

Pruning strategies:
1. Column pruning: SELECT only needed columns (40-60% reduction)
2. Row pruning: WHERE active = true or recent_only (50-80% reduction)
3. Value compression: msgpack serialized values (70-80% reduction, at CPU cost)

If all three: 125 GB -> ~5-10 GB -> fits in n1-standard-8 (30 GB RAM)

**Choose this if**: Lookup tables have many unused columns/rows and can be pruned to <5 GB total.

#### Rank 4: Bloom Filter + DuckDB (Option 7) -- Optimization on top of Rank 2

Add a 90 MB Bloom filter layer on top of DuckDB/SQLite to skip ~90% of lookups for keys that don't exist in the lookup table. Only worthwhile if miss rate is >50%.

### Decision Tree

```
Q: Is 15-minute enrichment latency acceptable?
├── YES → Option 10: BQ Post-JOIN (simplest, cheapest)
└── NO → Q: Can lookup data be pruned to <20 GB total?
    ├── YES → Option 4/5: Optimized MasterCache/Shared (simplest code)
    └── NO → Option 6/8: DuckDB/SQLite on worker (best pure-Dataflow for large data)
        └── Optional: Add Bloom filter if miss rate >50%
```

### What NOT to Do

1. **Side inputs for 15M+ rows**: Hard 80 MB limit with Streaming Engine; OOM without it.
2. **CoGroupByKey for this**: Too complex, too fragile, too expensive.
3. **BigQueryEnrichmentHandler without caching**: $8K/month BQ cost at high throughput.
4. **Per-element BQ queries**: $5,150/day (from BQ_LOOKUP_TECHNIQUES.md). Absolutely not.
5. **Bigtable for high-throughput lookups**: $12K+/month for adequate node count.

---

## 15. Sources

### Apache Beam Official Documentation
- [Side Input Patterns](https://beam.apache.org/documentation/patterns/side-inputs/)
- [Cache Data Using a Shared Object](https://beam.apache.org/documentation/patterns/shared-class/)
- [Enrichment Transform](https://beam.apache.org/documentation/transforms/python/elementwise/enrichment/)
- [BigQueryEnrichmentHandler API](https://beam.apache.org/releases/pydoc/2.63.0/apache_beam.transforms.enrichment_handlers.bigquery.html)
- [Enrichment Class API (2.71.0)](https://beam.apache.org/releases/pydoc/current/apache_beam.transforms.enrichment.html)
- [Beam Python Streaming](https://beam.apache.org/documentation/sdks/python-streaming/)
- [Beam Programming Guide](https://beam.apache.org/documentation/programming-guide/)
- [beam.utils.shared.py source](https://github.com/apache/beam/blob/master/sdks/python/apache_beam/utils/shared.py)

### Google Cloud Documentation
- [Enrich Streaming Data (Dataflow)](https://docs.cloud.google.com/dataflow/docs/guides/enrichment)
- [Troubleshoot Dataflow OOM Errors](https://docs.cloud.google.com/dataflow/docs/guides/troubleshoot-oom)
- [Dataflow Vertical Autoscaling](https://docs.cloud.google.com/dataflow/docs/vertical-autoscaling)
- [Dataflow Pricing](https://cloud.google.com/dataflow/pricing)
- [Dataflow Pipeline Options](https://cloud.google.com/dataflow/docs/reference/pipeline-options)
- [BigQuery Materialized Views](https://cloud.google.com/bigquery/docs/materialized-views-intro)

### Community Resources
- [Beginners Guide to Caching in Apache Beam Dataflow (DEV.to)](https://dev.to/morz/beginners-guide-to-caching-inside-an-apache-beam-dataflow-streaming-pipeline-using-python-47hi)
- [Cache Data on Apache Beam Using Shared Object (Jaehyeon Kim)](https://jaehyeon.me/blog/2024-08-22-cache-using-shared-object/)
- [Apache Beam Stateful Streaming with Lookup Table (Medium)](https://medium.com/@dmitry.turchenkov/apache-beam-stateful-streaming-with-lookup-table-980201a64422)
- [Apache Beam Stateful Streaming with BigQuery Side Input (Medium)](https://medium.com/@dmitry.turchenkov/apache-beam-stateful-streaming-with-bigquery-side-input-b63d5f34e3fd)
- [Scaling a Streaming Workload on Apache Beam, 1M events/sec](https://beam.apache.org/blog/scaling-streaming-workload/)
- [Building a Bloom Filter in Google Dataflow (GitHub Gist)](https://gist.github.com/jewer/86c6d11c8391abc2da4c190cea13a9e1)

### Memory and Performance
- [Python Dict Memory Usage (Reuven Lerner)](https://lerner.co.il/2019/05/12/python-dicts-and-memory-usage/)
- [Dictionary Space Usage (U of Toronto)](https://utcc.utoronto.ca/~cks/space/blog/python/DictionarySpaceUsage)
- [Python Dict Memory Scaling (LabEx)](https://labex.io/tutorials/python-how-to-understand-python-dict-memory-scaling-450842)
- [DuckDB Memory Management](https://duckdb.org/2024/07/09/memory-management)
- [DuckDB Arrow Zero-Copy Integration](https://duckdb.org/2021/12/03/duck-arrow)

### Pricing
- [GCP Compute Engine Pricing (economize.cloud)](https://www.economize.cloud/resources/gcp/pricing/compute-engine/n1-standard-4/)
- [Google Cloud Dataflow Pricing (Tekpon)](https://tekpon.com/software/google-cloud-dataflow/pricing/)

### Internal References
- `the1-re-data-platform/doc/dataflow/BQ_LOOKUP_TECHNIQUES.md` -- 7 techniques for small tables
- `the1-re-data-platform/doc/dataflow/STREAMING_BATCH_JOIN_RESEARCH.md` -- Full 10-option evaluation
- `sale/sales-data/sales-collector/src/domain/bq_lookup_cache.py` -- Current MasterCache implementation
- `sale/sales-data/sales-collector/src/application/pipeline/enrich_dofns.py` -- Current EnrichDoFn
