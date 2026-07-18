# Streaming Enrichment with Large Lookup Tables: Deep Dive

**Context**: Real-time streaming enrichment with 75M rows total (5 tables x 15M rows each), throughput 10K-100K msg/sec.

**Date**: 2026-03-17

---

## Table of Contents

1. [Approach 1: Redis / Memorystore](#approach-1-redis--memorystore)
2. [Approach 2: No Additional Instance](#approach-2-no-additional-instance)
   - [2a. High-Memory Workers + Arrow/Polars](#2a-high-memory-workers--arrowpolars)
   - [2b. Sharded/Partitioned In-Memory Cache](#2b-shardedpartitioned-in-memory-cache)
   - [2c. Memory-Mapped Files (mmap)](#2c-memory-mapped-files-mmap)
   - [2d. GCS Parquet Lookup](#2d-gcs-parquet-lookup)
   - [2e. SQLite on Local Disk](#2e-sqlite-on-local-disk)
   - [2f. DuckDB In-Process](#2f-duckdb-in-process)
   - [2g. Beam Shared Class + Slowly Changing Lookup Cache](#2g-beam-shared-class--slowly-changing-lookup-cache)
   - [2h. Other Creative Approaches](#2h-other-creative-approaches)
3. [Comparison Matrix](#comparison-matrix)
4. [Recommendation](#recommendation)

---

## Approach 1: Redis / Memorystore

### 1.1 Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                     SYNC PATH (Batch)                        │
│                                                              │
│  BigQuery ──► Cloud Function / Dataflow Batch ──► Redis      │
│  (5 tables)   (scheduled: hourly or daily)    (Memorystore)  │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                     STREAMING PATH                           │
│                                                              │
│  Kafka ──► Dataflow Streaming ──┬──► Redis Lookup (5 keys)   │
│            (10K-100K msg/sec)   │                            │
│                                 └──► Enriched Output ──► BQ  │
│                                                              │
│  Dataflow workers connect via VPC Peering to Memorystore     │
└──────────────────────────────────────────────────────────────┘
```

### 1.2 Key Design for 5 Tables

Each of the 5 lookup tables has a different join key. Use **namespace prefixes** to avoid collisions:

| Table | Join Key | Redis Key Pattern | Example |
|-------|----------|-------------------|---------|
| `customers` | `customer_id` | `cust:{customer_id}` | `cust:ABC123` |
| `products` | `product_id` | `prod:{product_id}` | `prod:SKU-9876` |
| `stores` | `store_id` | `store:{store_id}` | `store:BKK-001` |
| `promotions` | `promo_code` | `promo:{promo_code}` | `promo:SUMMER2026` |
| `categories` | `category_id` | `cat:{category_id}` | `cat:ELEC-TV` |

**Composite keys** (if a table has multi-column key):
```
# Use colon-separated composite keys
"cust:{customer_id}:{tier_code}" -> value
# Or hash the composite key
"cust:" + hashlib.md5(f"{customer_id}:{tier_code}".encode()).hexdigest()[:16]
```

### 1.3 Redis Data Structures: Hash vs String vs Sorted Sets

#### Option A: String (one key per lookup row)

```
SET "cust:ABC123" '{"name":"John","tier":"Gold","region":"BKK"}'
GET "cust:ABC123"
```

**Memory per key**: ~100-120 bytes overhead + key length + value length.
For 75M keys with avg 50-byte key + 200-byte value: **~26 GB**.

Pros: Simplest model, O(1) GET, supports MGET for batch.
Cons: Highest memory overhead (per-key dict entry ~56 bytes + SDS headers).

#### Option B: Hash (group rows into hash buckets)

```
# Bucket by first 4 chars of key → max ~65K buckets, ~230 entries each
HSET "cust:bucket:ABC1" "ABC123" '{"name":"John","tier":"Gold"}'
HGET "cust:bucket:ABC1" "ABC123"
```

**Memory optimization trick**: If each hash has < `hash-max-ziplist-entries` (default 128) fields and each field < `hash-max-ziplist-value` (default 64 bytes), Redis stores as **ziplist** — contiguous memory, ~10x less overhead.

For 75M rows with 128-entry buckets:
- 75M / 128 = ~586K hash keys
- Each ziplist: ~128 * (field_len + value_len) bytes, compactly packed
- **Estimated: ~15-18 GB** (vs ~26 GB for strings)

Cons: Cannot use MGET across buckets; bucketing logic adds complexity; value size must be < 64 bytes for ziplist (or increase `hash-max-ziplist-value`).

#### Option C: Sorted Sets

Not applicable here — sorted sets are for range queries and ranking. Our use case is point lookups.

#### Recommendation: **String keys with MGET batching**

For this use case (pure key-value lookup, 5 different key patterns, high throughput), plain strings with MGET pipelining is the best balance of simplicity and performance. The memory overhead vs hash buckets is ~50% more, but the operational simplicity is worth it.

### 1.4 Redis Pipelining and Batching

Redis pipelining sends multiple commands without waiting for individual responses, dramatically reducing network round-trips.

```python
import redis

class RedisLookupDoFn(beam.DoFn):
    """Batch lookup with Redis pipelining."""

    BATCH_SIZE = 500  # Optimal: 100-1000 keys per pipeline

    def setup(self):
        self._pool = redis.ConnectionPool(
            host=self._host, port=6379,
            max_connections=20,
            socket_connect_timeout=5,
            socket_timeout=2,
            retry_on_timeout=True,
            decode_responses=True,
        )
        self._client = redis.Redis(connection_pool=self._pool)

    def process(self, batch_of_elements):
        # Collect keys needed for this batch
        keys_by_table = defaultdict(list)
        for elem in batch_of_elements:
            keys_by_table['cust'].append(f"cust:{elem['customer_id']}")
            keys_by_table['prod'].append(f"prod:{elem['product_id']}")
            keys_by_table['store'].append(f"store:{elem['store_id']}")
            # ... other tables

        # Single pipeline for ALL lookups across ALL tables
        pipe = self._client.pipeline(transaction=False)
        all_keys = []
        for table_keys in keys_by_table.values():
            for key in table_keys:
                pipe.get(key)
                all_keys.append(key)

        results = pipe.execute()  # One round-trip for everything
        lookup_map = dict(zip(all_keys, results))

        for elem in batch_of_elements:
            cust_data = json.loads(lookup_map.get(f"cust:{elem['customer_id']}", '{}'))
            prod_data = json.loads(lookup_map.get(f"prod:{elem['product_id']}", '{}'))
            # ... merge and yield
            yield {**elem, **cust_data, **prod_data}

    def teardown(self):
        self._pool.disconnect()
```

**Performance characteristics**:
- Without pipelining: ~50K ops/sec per connection (limited by RTT)
- With pipelining (batch 500): ~500K-1M ops/sec per connection
- With MGET (batch 500): similar, slightly more efficient wire protocol
- **For 100K msg/sec with 5 lookups each = 500K lookups/sec**: achievable with 1-2 connections per worker, 3-5 workers

### 1.5 Memory Optimization

#### Compression (msgpack vs JSON)

```python
import msgpack

# JSON: {"name":"John Doe","tier":"Gold","region":"Bangkok","points":15000}
# = 63 bytes

# msgpack of same data:
data = {"name": "John Doe", "tier": "Gold", "region": "Bangkok", "points": 15000}
packed = msgpack.packb(data)  # = ~45 bytes (30% smaller)

# For 75M rows: saves ~1.35 GB
```

#### Key compression

```python
# Instead of: "cust:ABC-123-DEF-456-GHI"  (24 bytes)
# Use:        "c:ABC123DEF456GHI"          (18 bytes, strip separators + short prefix)
# Or hash:    "c:" + base62(crc32(key))    (fixed ~10 bytes)
# Savings at 75M keys: ~750 MB

# WARNING: hash-based key compression risks collisions.
# CRC32 has ~1% collision rate at 75M keys. Use at least 64-bit hash.
```

#### Value field pruning

Store only the fields actually needed for enrichment, not the entire row.

```python
# Full row: 500 bytes avg
# Pruned to 5 enrichment fields: 100 bytes avg
# Savings: 75M * 400 bytes = 30 GB saved
```

#### Memory estimate (optimized)

| Component | Calculation | Size |
|-----------|------------|------|
| Key overhead | 75M * 56 bytes (Redis dict entry) | 4.2 GB |
| Key strings | 75M * 15 bytes avg | 1.1 GB |
| Values (msgpack, pruned) | 75M * 80 bytes avg | 6.0 GB |
| Redis internal overhead | ~15% | 1.7 GB |
| **Total** | | **~13 GB** |

With full JSON values (no pruning): **~22-26 GB**.

### 1.6 Sync Job Design

#### Option A: Full Refresh (Recommended for simplicity)

```
Cloud Scheduler (every 1 hour)
    └─► Cloud Function
         ├─ Query BQ: SELECT key_col, val_col FROM table
         ├─ Write to Redis with pipeline (batches of 10K)
         └─ Set TTL on old keys (or use key versioning)
```

**Key versioning pattern** to avoid stale data during refresh:
```python
# Write new data with version prefix
version = int(time.time())
pipe = redis.pipeline()
for row in bq_results:
    pipe.set(f"v{version}:cust:{row['id']}", msgpack.packb(row))
pipe.execute()

# Atomically swap version pointer
redis.set("cust:current_version", version)

# Cleanup old versions (async)
old_version = redis.get("cust:prev_version")
# ... delete old keys with SCAN + UNLINK
```

#### Option B: Incremental (CDC-based)

```
BQ Change History / Audit Logs
    └─► Pub/Sub
         └─► Cloud Function (or small Dataflow job)
              └─► Redis SET for changed keys only
```

Pros: Lower BQ scan cost, lower Redis write load.
Cons: Complex; must handle deletes; risk of drift.

#### Option C: Dataflow Batch Job

```python
# Dataflow batch pipeline (scheduled via Cloud Scheduler)
with beam.Pipeline(options=options) as p:
    for table_name, key_col, value_cols in TABLES:
        (p
         | f'Read_{table_name}' >> beam.io.ReadFromBigQuery(
             query=f'SELECT {key_col}, {",".join(value_cols)} FROM {table_name}')
         | f'WriteRedis_{table_name}' >> beam.ParDo(
             WriteToRedisDoFn(prefix=TABLE_PREFIX[table_name]))
        )
```

Pros: Handles all 5 tables in one job; familiar infra.
Cons: Dataflow startup time (~3-5 min); overkill for simple key-value writes.

**Recommendation**: Cloud Function for tables < 50M rows (fits in memory). Dataflow Batch for larger or if you need exactly-once guarantees.

### 1.7 Failure Modes

| Failure | Impact | Mitigation |
|---------|--------|------------|
| **Redis down** | All lookups fail → pipeline backpressure/stall | HA Standard tier (auto-failover in ~30s); circuit breaker in DoFn; fallback to cached stale data or pass-through without enrichment |
| **Sync failure** | Stale lookup data | Monitoring alert on sync job; TTL on keys (e.g., 4h) so data auto-expires if not refreshed; dead-letter missed refreshes |
| **Stale data** | Enriched with old values | Acceptable if refresh is hourly; add `_enriched_at` timestamp to output for observability |
| **Connection pool exhaustion** | Timeouts in DoFn | Size pool correctly (20-50 per worker); use `max_connections` with `BlockingConnectionPool` |
| **OOM on Redis** | Eviction or crash | Set `maxmemory-policy allkeys-lru`; monitor with `INFO memory`; alert at 80% capacity |
| **Network partition (VPC)** | Intermittent timeouts | Retry with exponential backoff; `socket_timeout=2` + `retry_on_timeout=True` |

### 1.8 VPC Peering with Dataflow

Memorystore requires **VPC peering** (or Private Service Connect). Dataflow workers must be in the same VPC or peered VPC.

```bash
# Dataflow pipeline launch flags
--network=projects/PROJECT/global/networks/VPC_NAME
--subnetwork=regions/REGION/subnetworks/SUBNET_NAME
--no_use_public_ips  # Required for private IP access to Memorystore
```

**Key constraints**:
- Memorystore IP range must not overlap with Dataflow subnet
- Peering routes must be exported/imported
- Firewall rule: allow ingress on port 6379 from Dataflow subnet CIDR
- If using Shared VPC, service project needs proper IAM

### 1.9 Complete DoFn Code Skeleton

```python
import json
import logging
from collections import defaultdict
from typing import Any, Dict, Iterator, List, Optional, Tuple

import apache_beam as beam
import msgpack
import redis

logger = logging.getLogger(__name__)


class BatchedRedisLookupDoFn(beam.DoFn):
    """
    Enriches streaming elements by looking up 5 tables in Redis.
    Uses pipelining for high throughput.

    Usage in pipeline:
        elements
        | beam.BatchElements(min_batch_size=100, max_batch_size=500)
        | beam.ParDo(BatchedRedisLookupDoFn(
            host="10.0.0.3",
            port=6379,
            table_configs=[
                TableLookupConfig("cust", "customer_id", ["name", "tier", "region"]),
                TableLookupConfig("prod", "product_id", ["name", "category"]),
                TableLookupConfig("store", "store_id", ["name", "city"]),
                TableLookupConfig("promo", "promo_code", ["discount_pct"]),
                TableLookupConfig("cat", "category_id", ["parent_category"]),
            ]
          ))
    """

    def __init__(
        self,
        host: str,
        port: int = 6379,
        table_configs: Optional[List] = None,
        max_connections: int = 20,
        socket_timeout: float = 2.0,
        use_msgpack: bool = True,
    ):
        self._host = host
        self._port = port
        self._table_configs = table_configs or []
        self._max_connections = max_connections
        self._socket_timeout = socket_timeout
        self._use_msgpack = use_msgpack
        # These are initialized in setup()
        self._pool = None
        self._client = None
        self._miss_counter = None
        self._hit_counter = None
        self._error_counter = None

    def setup(self):
        """Initialize Redis connection pool (once per worker lifetime)."""
        self._pool = redis.ConnectionPool(
            host=self._host,
            port=self._port,
            max_connections=self._max_connections,
            socket_connect_timeout=5,
            socket_timeout=self._socket_timeout,
            retry_on_timeout=True,
            decode_responses=not self._use_msgpack,
            health_check_interval=30,
        )
        self._client = redis.Redis(connection_pool=self._pool)
        # Verify connectivity
        self._client.ping()

        # Beam counters for monitoring
        self._hit_counter = beam.metrics.Metrics.counter(
            "redis_lookup", "cache_hit"
        )
        self._miss_counter = beam.metrics.Metrics.counter(
            "redis_lookup", "cache_miss"
        )
        self._error_counter = beam.metrics.Metrics.counter(
            "redis_lookup", "errors"
        )

    def process(
        self, batch: List[Dict[str, Any]]
    ) -> Iterator[Dict[str, Any]]:
        """Process a batch of elements with pipelined Redis lookups."""
        if not batch:
            return

        # 1. Collect all keys needed across all tables
        keys_order: List[Tuple[str, str, int]] = []  # (prefix, key, elem_idx)
        for idx, elem in enumerate(batch):
            for cfg in self._table_configs:
                join_value = elem.get(cfg.join_field)
                if join_value is not None:
                    redis_key = f"{cfg.prefix}:{join_value}"
                    keys_order.append((cfg.prefix, redis_key, idx))

        if not keys_order:
            yield from batch
            return

        # 2. Execute pipelined MGET
        try:
            pipe = self._client.pipeline(transaction=False)
            for _, redis_key, _ in keys_order:
                pipe.get(redis_key)
            results = pipe.execute()
        except redis.RedisError as e:
            logger.error(f"Redis pipeline error: {e}")
            self._error_counter.inc(len(batch))
            # Fallback: yield elements without enrichment
            yield from batch
            return

        # 3. Build per-element enrichment map
        enrichments: Dict[int, Dict[str, Any]] = defaultdict(dict)
        for (prefix, redis_key, elem_idx), value in zip(keys_order, results):
            if value is not None:
                self._hit_counter.inc()
                if self._use_msgpack:
                    decoded = msgpack.unpackb(value, raw=False)
                else:
                    decoded = json.loads(value)
                # Namespace enrichment fields to avoid collisions
                for k, v in decoded.items():
                    enrichments[elem_idx][f"{prefix}_{k}"] = v
            else:
                self._miss_counter.inc()

        # 4. Yield enriched elements
        for idx, elem in enumerate(batch):
            if idx in enrichments:
                yield {**elem, **enrichments[idx]}
            else:
                yield elem

    def teardown(self):
        """Clean up Redis connections."""
        if self._pool:
            self._pool.disconnect()


class TableLookupConfig:
    """Configuration for a single lookup table."""
    def __init__(self, prefix: str, join_field: str, value_fields: list):
        self.prefix = prefix
        self.join_field = join_field
        self.value_fields = value_fields


# Pipeline usage:
# (
#     messages
#     | "BatchForRedis" >> beam.BatchElements(
#         min_batch_size=100, max_batch_size=500
#     )
#     | "RedisEnrich" >> beam.ParDo(
#         BatchedRedisLookupDoFn(host="10.0.0.3", table_configs=[...])
#     )
# )
```

### 1.10 Cost Analysis

#### Memorystore for Redis (Standard Tier, HA)

Pricing (asia-southeast1, approximate):
- **Basic tier**: ~$0.049/GB/hour
- **Standard tier (HA)**: ~$0.098/GB/hour (2x for replica)

| Scenario | Memory Needed | Instance | Monthly Cost |
|----------|--------------|----------|-------------|
| Pruned + msgpack (13 GB) | 16 GB instance | Standard HA | 16 * $0.098 * 730 = **~$1,145/mo** |
| Full JSON (26 GB) | 32 GB instance | Standard HA | 32 * $0.098 * 730 = **~$2,290/mo** |
| With headroom (26 GB + buffer) | 52 GB instance | Standard HA | 52 * $0.098 * 730 = **~$3,722/mo** |

#### Memorystore for Redis Cluster

For larger scale or higher throughput:
- Node-based pricing (shard-based)
- Each shard: 13 GB (highmem) or 6.5 GB
- 75M keys at 13 GB optimized: ~2-3 shards needed
- **Approx $800-1,500/mo** for cluster mode (depends on node type)

Cluster advantages:
- Linear throughput scaling (add shards)
- 0-downtime scaling
- Multi-slot pipeline support

#### Dataflow Worker Cost (for the streaming pipeline itself)

| Throughput | Workers (n1-standard-4) | Worker Cost/mo | Redis Cost/mo | **Total/mo** |
|-----------|------------------------|----------------|---------------|-------------|
| 10K msg/sec | 2 workers | ~$390 | $1,145 | **~$1,535** |
| 50K msg/sec | 5 workers | ~$975 | $1,145 | **~$2,120** |
| 100K msg/sec | 10 workers | ~$1,950 | $1,145 | **~$3,095** |

Note: Redis cost is fixed regardless of throughput (same dataset). Worker cost scales with throughput.

### 1.11 Memorystore for Redis vs Redis Cluster

| Aspect | Memorystore (Standard) | Memorystore (Cluster) |
|--------|----------------------|---------------------|
| Max memory | 300 GB | 5+ TB |
| Throughput | Single-threaded (100K+ ops/sec) | Multi-shard (millions ops/sec) |
| HA | Primary + replica (auto-failover) | Per-shard replicas |
| Scaling | Vertical only (resize = downtime) | Add/remove shards online |
| Cost for 16 GB | ~$1,145/mo | ~$800-1,200/mo |
| Complexity | Simple (single endpoint) | Multi-slot (client must handle) |
| For 75M rows | Sufficient if optimized | Overkill unless >500K ops/sec |

**Recommendation**: Standard tier (16-32 GB) is sufficient for 75M rows at 100K msg/sec. Cluster only needed if throughput exceeds ~300K lookups/sec sustained.

---

## Approach 2: No Additional Instance

### 2a. High-Memory Workers + Arrow/Polars

#### Memory Calculation

Python dict memory per row (measured):
```python
import sys
# A dict with 5 string fields:
row = {"id": "ABC123", "name": "John Doe", "tier": "Gold", "region": "BKK", "points": "15000"}
sys.getsizeof(row)  # 232 bytes (dict overhead)
# + string objects: ~50 bytes each * 5 keys + 5 values = ~500 bytes
# Total: ~600-700 bytes per row

# 75M rows * 650 bytes = ~48.8 GB  ← Does NOT fit in n1-highmem-8 (52 GB)
# Would need n1-highmem-16 (104 GB) with ~50% headroom
```

PyArrow Table memory per row:
```python
import pyarrow as pa

# Arrow stores columnar data with zero per-row overhead
# Each column: array header (~64 bytes) + data
# String column (15M values, avg 10 chars): ~150 MB
# Int column (15M values): ~60 MB
# 5 columns per table: ~450 MB per 15M-row table
# 5 tables: ~2.25 GB total!

# But: lookup requires an index structure
# dict index on string key: 15M * 80 bytes = ~1.2 GB per table
# 5 tables: ~6 GB for indices
# Total: ~8-9 GB ← Fits in n1-highmem-4 (26 GB)!
```

Polars DataFrame:
```python
import polars as pl

# Similar to Arrow (Polars uses Arrow internally)
# 15M rows, 5 columns: ~500 MB per table
# 5 tables: ~2.5 GB
# With hash index for lookup: ~8-10 GB total
```

#### How to Do Key Lookup on Arrow Table

Arrow tables don't have native hash indexes. You need a separate index structure:

```python
import pyarrow as pa
import pyarrow.compute as pc
import numpy as np
from typing import Optional, Dict, Any

class ArrowLookupTable:
    """Efficient key-value lookup using Arrow table + Python dict index."""

    def __init__(self, table: pa.Table, key_column: str):
        self.table = table
        self.key_column = key_column
        # Build hash index: key -> row_index
        key_array = table.column(key_column).to_pylist()
        self._index: Dict[str, int] = {k: i for i, k in enumerate(key_array)}

    def lookup(self, key: str) -> Optional[Dict[str, Any]]:
        """O(1) lookup by key."""
        idx = self._index.get(key)
        if idx is None:
            return None
        # Extract single row (columnar access)
        return {
            col: self.table.column(col)[idx].as_py()
            for col in self.table.column_names
            if col != self.key_column
        }

    def lookup_batch(self, keys: list) -> list:
        """Batch lookup — more efficient for Arrow."""
        indices = [self._index.get(k) for k in keys]
        valid_mask = [i is not None for i in indices]
        valid_indices = [i for i in indices if i is not None]

        if not valid_indices:
            return [None] * len(keys)

        # Take rows by index (vectorized)
        subset = self.table.take(valid_indices)
        results = subset.to_pylist()

        # Map back to original order
        output = []
        result_iter = iter(results)
        for is_valid in valid_mask:
            if is_valid:
                output.append(next(result_iter))
            else:
                output.append(None)
        return output


class ArrowLookupDoFn(beam.DoFn):
    """DoFn that loads Arrow tables into memory on setup."""

    def __init__(self, gcs_paths: Dict[str, str], key_columns: Dict[str, str]):
        """
        gcs_paths: {"customers": "gs://bucket/customers.parquet", ...}
        key_columns: {"customers": "customer_id", ...}
        """
        self._gcs_paths = gcs_paths
        self._key_columns = key_columns
        self._lookups: Dict[str, ArrowLookupTable] = {}

    def setup(self):
        """Load all lookup tables once per worker."""
        import pyarrow.parquet as pq
        from pyarrow import fs

        gcs = fs.GcsFileSystem()
        for name, path in self._gcs_paths.items():
            # Read Parquet from GCS directly into Arrow
            table = pq.read_table(
                path.replace("gs://", ""),
                filesystem=gcs,
            )
            self._lookups[name] = ArrowLookupTable(
                table, self._key_columns[name]
            )
            logging.info(
                f"Loaded {name}: {table.num_rows} rows, "
                f"{table.nbytes / 1e6:.1f} MB"
            )

    def process(self, element):
        enriched = dict(element)
        for name, lookup in self._lookups.items():
            join_key = self._key_columns[name]
            key_value = element.get(join_key)
            if key_value:
                result = lookup.lookup(key_value)
                if result:
                    for k, v in result.items():
                        enriched[f"{name}_{k}"] = v
        yield enriched
```

#### Can 75M rows fit?

| Storage | Arrow Data | Dict Index | Total | Fits in... |
|---------|-----------|-----------|-------|-----------|
| 75M rows, 5 cols each | ~2.5 GB | ~6.5 GB | **~9 GB** | n1-highmem-2 (13 GB) |
| 75M rows, 10 cols each | ~5 GB | ~6.5 GB | **~11.5 GB** | n1-highmem-4 (26 GB) |
| 75M rows, 20 cols each | ~10 GB | ~6.5 GB | **~16.5 GB** | n1-highmem-4 (26 GB) |

**Yes, 75M rows easily fits in Arrow + dict index on a single n1-highmem-4 worker.**

The catch: **every worker** needs a full copy. With autoscaling, 5 workers = 5 copies = 5x memory cost. But the actual data is only ~9 GB, so even 10 workers with n1-highmem-4 is manageable.

#### Worker Cost

| Workers | Machine | RAM | Monthly Cost |
|---------|---------|-----|-------------|
| 3 x n1-highmem-4 | 4 vCPU, 26 GB | 78 GB total | ~$660/mo |
| 5 x n1-highmem-4 | 4 vCPU, 26 GB | 130 GB total | ~$1,100/mo |
| 10 x n1-highmem-4 | 4 vCPU, 26 GB | 260 GB total | ~$2,200/mo |

Cheaper than Redis at lower throughputs, comparable at high throughputs.

#### Refresh Mechanism

```python
# Use Beam's Shared class for periodic refresh
from apache_beam.utils.shared import Shared

class RefreshableArrowLookupDoFn(beam.DoFn):
    REFRESH_INTERVAL_SEC = 3600  # 1 hour

    def __init__(self, gcs_paths, key_columns):
        self._gcs_paths = gcs_paths
        self._key_columns = key_columns
        self._shared_handle = Shared()
        self._lookups = None
        self._current_tag = None

    def _compute_tag(self):
        t = time.time()
        return t - (t % self.REFRESH_INTERVAL_SEC)

    def _load_all(self):
        import pyarrow.parquet as pq
        from pyarrow import fs
        gcs = fs.GcsFileSystem()

        class WeakRefDict(dict):
            pass

        lookups = {}
        for name, path in self._gcs_paths.items():
            table = pq.read_table(path.replace("gs://", ""), filesystem=gcs)
            lookups[name] = ArrowLookupTable(table, self._key_columns[name])

        result = WeakRefDict(lookups)
        result['_tag'] = self._compute_tag()
        return result

    def setup(self):
        self._current_tag = self._compute_tag()
        self._lookups = self._shared_handle.acquire(
            self._load_all, tag=self._current_tag
        )

    def start_bundle(self):
        new_tag = self._compute_tag()
        if new_tag != self._current_tag:
            self._current_tag = new_tag
            self._lookups = self._shared_handle.acquire(
                self._load_all, tag=new_tag
            )

    def process(self, element):
        enriched = dict(element)
        for name, lookup in self._lookups.items():
            if name.startswith('_'):
                continue
            join_key = self._key_columns[name]
            key_value = element.get(join_key)
            if key_value:
                result = lookup.lookup(key_value)
                if result:
                    for k, v in result.items():
                        enriched[f"{name}_{k}"] = v
        yield enriched
```

### 2b. Sharded/Partitioned In-Memory Cache

#### Concept

Instead of every worker holding all 75M rows, each worker holds only a partition:

```
75M rows / 10 workers = 7.5M rows per worker (~1 GB each)
```

Route elements to the correct worker by their join key using `KeyBy + GroupByKey`:

```python
# Pseudocode
elements
| "KeyBy" >> beam.Map(lambda x: (hash(x['customer_id']) % NUM_SHARDS, x))
| "GroupByKey" >> beam.GroupByKey()  # Routes to same worker by key
| "Lookup" >> beam.ParDo(ShardedLookupDoFn())
```

#### Is This Feasible in Beam?

**Partially, with major caveats:**

1. **Beam does not guarantee worker affinity.** `GroupByKey` ensures same-key elements go to the same *task*, but tasks can move between workers. The lookup data must be loaded per-task, not per-worker.

2. **Stateful DoFn approach**: Use `@beam.DoFn.StateParam` with `BagState` to store lookup data. But BagState is backed by the runner's state backend (for Dataflow Streaming, this is Streaming Engine's persistent state), not RAM. Reading from state has latency.

3. **Sticky worker routing (Dataflow-specific)**: Dataflow tends to keep the same key range on the same worker, but this is an implementation detail, not a guarantee.

4. **Workaround**: Use the `Shared` class per shard. Each worker loads only its shard's data at startup. But this requires knowing the shard assignment at pipeline construction time, which Beam's dynamic work rebalancing breaks.

```python
class ShardedLookupDoFn(beam.DoFn):
    """
    Each worker loads only its shard of the lookup table.
    CAVEAT: Shard assignment must be stable (no dynamic rebalancing).
    """

    NUM_SHARDS = 10

    def __init__(self, gcs_path_template: str):
        # e.g., "gs://bucket/lookup/shard_{shard_id}.parquet"
        self._gcs_path_template = gcs_path_template
        self._shard_data = {}

    def process(self, element, shard_id=beam.DoFn.KeyParam):
        if shard_id not in self._shard_data:
            # Lazy-load this shard
            path = self._gcs_path_template.format(shard_id=shard_id)
            table = pq.read_table(path)
            self._shard_data[shard_id] = ArrowLookupTable(table, "key")

        result = self._shard_data[shard_id].lookup(element['key'])
        yield {**element, **(result or {})}
```

**Verdict**: Theoretically possible but fragile. Beam's dynamic work rebalancing and lack of worker affinity guarantees make this unreliable. If a worker is replaced, the shard must be re-loaded. Not recommended for production unless you can tolerate cold-start delays.

### 2c. Memory-Mapped Files (mmap)

#### Concept

Write lookup data as Arrow IPC files. Workers memory-map them, reading without loading into Python heap.

```python
import pyarrow as pa
import pyarrow.ipc as ipc
import mmap

# Write phase (offline):
table = pa.table({"key": keys, "val1": vals1, "val2": vals2})
with pa.OSFile("/tmp/lookup.arrow", "wb") as f:
    writer = ipc.new_file(f, table.schema)
    writer.write_table(table)
    writer.close()

# Read phase (on Dataflow worker):
source = pa.memory_map("/tmp/lookup.arrow", "r")
reader = ipc.open_file(source)
table = reader.read_all()  # Memory-mapped, NOT loaded into heap
```

#### How It Works on Dataflow Workers

1. **Worker startup**: Download Arrow IPC file from GCS to local disk (`/tmp/` or configured disk)
2. **mmap the file**: `pa.memory_map()` maps the file into virtual address space
3. **OS page cache**: Only pages actually accessed are loaded into RAM
4. **Benefit**: If you access 10% of keys, only ~10% of the file is in physical RAM

**Problem**: For key-value lookup, you need a hash index. Arrow IPC files don't have one. You'd need to:
- Build the index in memory (same as approach 2a, negating mmap benefit)
- Or do sequential scan (O(n) per lookup — way too slow)
- Or pre-sort the file and do binary search (O(log n) — possible but complex)

```python
# Binary search on sorted Arrow file
import bisect

class MmapArrowLookup:
    def __init__(self, file_path: str, key_column: str):
        source = pa.memory_map(file_path, "r")
        reader = ipc.open_file(source)
        self.table = reader.read_all()
        # Keys must be pre-sorted
        self.keys = self.table.column(key_column).to_pylist()
        # This to_pylist() defeats the purpose of mmap :(

    def lookup(self, key):
        idx = bisect.bisect_left(self.keys, key)
        if idx < len(self.keys) and self.keys[idx] == key:
            return {col: self.table.column(col)[idx].as_py()
                    for col in self.table.column_names}
        return None
```

**Verdict**: mmap is beneficial when you access a small fraction of the data. For enrichment where every key might be accessed, you end up loading most pages anyway. The need for an index structure negates the mmap advantage. **Not recommended** for this use case.

### 2d. GCS Parquet Lookup

#### Concept

Store lookup tables as partitioned Parquet on GCS. Workers read only needed partitions.

```
gs://bucket/lookups/customers/
  ├── partition=0/data.parquet    # keys where hash(key) % 100 == 0
  ├── partition=1/data.parquet
  ├── ...
  └── partition=99/data.parquet
```

```python
import pyarrow.parquet as pq
from pyarrow import fs

class GCSParquetLookupDoFn(beam.DoFn):
    def __init__(self, base_path: str, num_partitions: int = 100):
        self._base_path = base_path
        self._num_partitions = num_partitions
        self._gcs = None
        self._cache = {}  # LRU cache of loaded partitions

    def setup(self):
        self._gcs = fs.GcsFileSystem()

    def _get_partition(self, key: str) -> int:
        return hash(key) % self._num_partitions

    def process(self, element):
        key = element['customer_id']
        part_id = self._get_partition(key)

        if part_id not in self._cache:
            # Read partition from GCS
            path = f"{self._base_path}/partition={part_id}/data.parquet"
            table = pq.read_table(path, filesystem=self._gcs)
            # Build index for this partition
            keys = table.column("customer_id").to_pylist()
            self._cache[part_id] = {
                k: i for i, k in enumerate(keys)
            }, table

        index, table = self._cache[part_id]
        idx = index.get(key)
        if idx is not None:
            row = {col: table.column(col)[idx].as_py()
                   for col in table.column_names}
            yield {**element, **row}
        else:
            yield element
```

#### Performance Analysis

| Metric | Value |
|--------|-------|
| GCS read latency | ~50-100ms per file (first read) |
| Partition size (75M/100) | 750K rows ≈ 30-50 MB |
| Cache hit ratio | High (same partitions accessed repeatedly) |
| Throughput | **Limited by GCS latency on cache miss** |
| At 100K msg/sec | Need all 100 partitions cached within seconds |

**Problem**: At startup, every worker needs to load partitions on-demand. The first few minutes will have high latency (50-100ms per element on cache miss). Once all partitions are cached, performance is similar to approach 2a.

**Verdict**: This is essentially a lazy-loading version of approach 2a. After warm-up, all data ends up in memory anyway. The partitioning adds complexity without real benefit. Better to load everything upfront (2a).

### 2e. SQLite on Local Disk

#### Concept

Download lookup data as SQLite DB to worker's local SSD. Indexed queries provide O(1) lookup without consuming Python heap.

```python
import sqlite3
import tempfile
import os
from google.cloud import storage

class SQLiteLookupDoFn(beam.DoFn):
    """
    Download pre-built SQLite DB from GCS to local SSD.
    Indexed lookups: ~100K-500K queries/sec per worker.
    Memory: Only SQLite engine (~2 MB) + page cache (~50-100 MB configurable).
    """

    REFRESH_INTERVAL = 3600  # 1 hour

    def __init__(
        self,
        gcs_bucket: str,
        gcs_path: str,  # e.g., "lookups/enrichment.db"
        table_configs: list,  # [(table_name, key_col, join_field), ...]
    ):
        self._gcs_bucket = gcs_bucket
        self._gcs_path = gcs_path
        self._table_configs = table_configs
        self._conn = None
        self._db_path = None
        self._last_refresh = 0

    def setup(self):
        self._download_and_connect()

    def _download_and_connect(self):
        """Download SQLite DB from GCS to local disk."""
        # Close existing connection
        if self._conn:
            self._conn.close()

        # Download to temp file
        self._db_path = os.path.join(tempfile.gettempdir(), "lookup.db")
        client = storage.Client()
        bucket = client.bucket(self._gcs_bucket)
        blob = bucket.blob(self._gcs_path)
        blob.download_to_filename(self._db_path)

        # Connect with optimized settings
        self._conn = sqlite3.connect(self._db_path)
        self._conn.execute("PRAGMA journal_mode=OFF")     # Read-only, no journal
        self._conn.execute("PRAGMA synchronous=OFF")       # No fsync needed
        self._conn.execute("PRAGMA cache_size=-102400")    # 100 MB page cache
        self._conn.execute("PRAGMA mmap_size=1073741824")  # 1 GB mmap
        self._conn.execute("PRAGMA temp_store=MEMORY")
        self._conn.row_factory = sqlite3.Row

        self._last_refresh = time.time()
        logging.info(f"Loaded SQLite DB: {os.path.getsize(self._db_path) / 1e6:.1f} MB")

    def start_bundle(self):
        """Check if refresh is needed."""
        if time.time() - self._last_refresh > self.REFRESH_INTERVAL:
            self._download_and_connect()

    def process(self, element):
        enriched = dict(element)

        for table_name, key_col, join_field in self._table_configs:
            key_value = element.get(join_field)
            if key_value is None:
                continue

            cursor = self._conn.execute(
                f"SELECT * FROM {table_name} WHERE {key_col} = ?",
                (key_value,)
            )
            row = cursor.fetchone()
            if row:
                for col in row.keys():
                    if col != key_col:
                        enriched[f"{table_name}_{col}"] = row[col]

        yield enriched

    def teardown(self):
        if self._conn:
            self._conn.close()
        if self._db_path and os.path.exists(self._db_path):
            os.remove(self._db_path)
```

#### Pre-building the SQLite DB (offline job)

```python
# Run as Cloud Function or Dataflow batch job
import sqlite3
from google.cloud import bigquery, storage

def build_lookup_db():
    bq_client = bigquery.Client()
    db_path = "/tmp/enrichment.db"
    conn = sqlite3.connect(db_path)

    tables = [
        ("customers", "SELECT customer_id, name, tier, region FROM customers", "customer_id"),
        ("products", "SELECT product_id, name, category FROM products", "product_id"),
        ("stores", "SELECT store_id, name, city FROM stores", "store_id"),
        ("promotions", "SELECT promo_code, discount_pct FROM promotions", "promo_code"),
        ("categories", "SELECT category_id, parent_category FROM categories", "category_id"),
    ]

    for table_name, query, key_col in tables:
        rows = bq_client.query(query).result()
        # Create table
        first_row = True
        for row in rows:
            if first_row:
                cols = list(row.keys())
                col_defs = ", ".join(f"{c} TEXT" for c in cols)
                conn.execute(f"CREATE TABLE {table_name} ({col_defs})")
                first_row = False
            placeholders = ", ".join("?" * len(cols))
            conn.execute(
                f"INSERT INTO {table_name} VALUES ({placeholders})",
                [row[c] for c in cols]
            )

        # Create index on key column
        conn.execute(f"CREATE INDEX idx_{table_name}_{key_col} ON {table_name}({key_col})")
        conn.commit()

    conn.execute("ANALYZE")  # Update query planner statistics
    conn.execute("VACUUM")   # Compact the database
    conn.close()

    # Upload to GCS
    client = storage.Client()
    bucket = client.bucket("my-bucket")
    blob = bucket.blob("lookups/enrichment.db")
    blob.upload_from_filename(db_path)
```

#### Performance Analysis

| Metric | Value |
|--------|-------|
| SQLite indexed lookup | ~100K-500K queries/sec (SSD) |
| DB file size (75M rows, 5 cols each) | ~3-5 GB |
| Download time (GCS → local) | ~10-20 sec (SSD, same region) |
| Memory usage | ~2 MB engine + ~100 MB page cache |
| Python heap impact | **Negligible** |
| Startup latency | ~15-25 sec (download + open) |

**Key advantages**:
- **Minimal memory**: ~100 MB vs ~9 GB for Arrow+dict
- **Standard SQL**: Easy to debug and test
- **Robust**: SQLite is battle-tested with billions of deployments
- **Refresh**: Just re-download the file

**Key disadvantages**:
- **Single-threaded**: SQLite uses a single-writer model. OK for reads.
- **Local disk dependency**: Dataflow Streaming Engine uses small boot disks (30 GB default). A 5 GB SQLite DB fits, but barely.
- **Disk I/O latency**: Even SSD has ~100us latency vs ~100ns for RAM

### 2f. DuckDB In-Process

#### Concept

Similar to SQLite but columnar — better compression, vectorized execution.

```python
import duckdb
import tempfile
import os

class DuckDBLookupDoFn(beam.DoFn):
    """
    DuckDB in-process for enrichment lookups.
    Can read Parquet directly from GCS.
    """

    REFRESH_INTERVAL = 3600

    def __init__(self, gcs_parquet_paths: dict, key_columns: dict):
        """
        gcs_parquet_paths: {"customers": "gs://bucket/customers/*.parquet"}
        key_columns: {"customers": "customer_id"}
        """
        self._gcs_paths = gcs_parquet_paths
        self._key_columns = key_columns
        self._conn = None
        self._last_refresh = 0

    def setup(self):
        self._init_duckdb()

    def _init_duckdb(self):
        if self._conn:
            self._conn.close()

        self._conn = duckdb.connect(":memory:")
        # Or persistent: duckdb.connect("/tmp/lookup.duckdb")

        # Install and load GCS extension
        self._conn.execute("INSTALL httpfs; LOAD httpfs;")
        self._conn.execute("SET s3_region='asia-southeast1';")
        # GCS uses S3-compatible API in DuckDB

        for name, path in self._gcs_paths.items():
            # Load Parquet into DuckDB table (in-memory)
            self._conn.execute(f"""
                CREATE OR REPLACE TABLE {name} AS
                SELECT * FROM read_parquet('{path}')
            """)
            # Create index (DuckDB supports ART indexes)
            key_col = self._key_columns[name]
            self._conn.execute(f"""
                CREATE INDEX idx_{name} ON {name}({key_col})
            """)

            count = self._conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            logging.info(f"Loaded {name}: {count} rows")

        self._last_refresh = time.time()

    def start_bundle(self):
        if time.time() - self._last_refresh > self.REFRESH_INTERVAL:
            self._init_duckdb()

    def process(self, element):
        enriched = dict(element)

        for name in self._gcs_paths:
            key_col = self._key_columns[name]
            key_value = element.get(key_col)
            if key_value is None:
                continue

            result = self._conn.execute(
                f"SELECT * FROM {name} WHERE {key_col} = ?",
                [key_value]
            ).fetchone()

            if result:
                columns = self._conn.execute(
                    f"SELECT column_name FROM information_schema.columns WHERE table_name = '{name}'"
                ).fetchall()
                col_names = [c[0] for c in columns]
                for col_name, value in zip(col_names, result):
                    if col_name != key_col:
                        enriched[f"{name}_{col_name}"] = value

        yield enriched

    def teardown(self):
        if self._conn:
            self._conn.close()
```

#### DuckDB vs SQLite

| Aspect | SQLite | DuckDB |
|--------|--------|--------|
| Storage model | Row-oriented | Columnar |
| Compression | None (WAL mode) | Lightweight compression |
| 75M rows, 5 cols | ~4 GB on disk | ~2 GB on disk |
| In-memory 75M rows | N/A (file-based) | ~3-5 GB |
| Point lookup speed | ~200K-500K/sec (indexed) | ~100K-300K/sec (ART index) |
| GCS direct read | No (must download) | Yes (httpfs extension) |
| Python integration | stdlib (sqlite3) | pip install duckdb |
| Maturity | 25+ years | ~5 years |

**DuckDB advantage**: Can read Parquet directly from GCS without downloading. Better compression. Native Arrow interop.

**DuckDB disadvantage**: For point lookups specifically, SQLite is faster. DuckDB's ART index is good but optimized more for range scans. Also, loading 75M rows into DuckDB in-memory uses more RAM than Arrow.

### 2g. Beam Shared Class + Slowly Changing Lookup Cache

This is the **official Beam pattern** for this exact problem, documented at:
- https://beam.apache.org/documentation/patterns/shared-class/
- https://beam.apache.org/documentation/patterns/side-inputs/

#### Architecture

```
                    ┌─────────────────────────────┐
                    │    Beam Shared Object        │
                    │  (weak ref, shared across    │
                    │   all DoFn instances on       │
                    │   same worker)                │
                    │                              │
                    │  ┌─────────────────────┐     │
                    │  │  WeakRefDict         │     │
                    │  │  { key -> value }    │     │
                    │  │  for each table      │     │
                    │  └─────────────────────┘     │
                    │                              │
                    │  Tag: floor(time / interval) │
                    │  Reload when tag changes     │
                    └───────────────┬──────────────┘
                                    │
                        ┌───────────┤
                        ▼           ▼
                    DoFn-1      DoFn-2      (same worker)
                    process()   process()
                    ▲               ▲
                    │               │
            ┌───────┘               └───────┐
            │                               │
        element-1                       element-2
```

#### Complete Implementation

```python
import logging
import time
from typing import Any, Dict, Iterator, List, Optional

import apache_beam as beam
from apache_beam.utils.shared import Shared

logger = logging.getLogger(__name__)


class WeakRefDict(dict):
    """Dict subclass that supports weak references (required by Shared)."""
    pass


class SharedLookupCacheDoFn(beam.DoFn):
    """
    Slowly Changing Lookup Cache pattern using Beam's Shared class.

    - Loads lookup data from BQ/GCS into a dict shared across all DoFn
      instances on the same worker
    - Refreshes periodically based on tag (time-based)
    - Memory-efficient: single copy per worker (not per DoFn instance)
    """

    def __init__(
        self,
        bq_queries: Dict[str, str],
        key_columns: Dict[str, str],
        refresh_interval_sec: int = 3600,
    ):
        """
        bq_queries: {"customers": "SELECT * FROM project.dataset.customers", ...}
        key_columns: {"customers": "customer_id", ...}
        refresh_interval_sec: How often to reload data (default: 1 hour)
        """
        self._bq_queries = bq_queries
        self._key_columns = key_columns
        self._refresh_interval = refresh_interval_sec
        self._shared_handle = Shared()
        self._lookups = None
        self._current_tag = None

    def _compute_tag(self) -> float:
        """Compute time-based tag. Same tag = same cache."""
        t = time.time()
        return t - (t % self._refresh_interval)

    def _load_all_tables(self) -> WeakRefDict:
        """Load all lookup tables from BigQuery. Called on cache miss."""
        from google.cloud import bigquery

        bq_client = bigquery.Client()
        lookups = WeakRefDict()

        for table_name, query in self._bq_queries.items():
            key_col = self._key_columns[table_name]
            table_dict = {}

            for row in bq_client.query(query).result():
                key = row[key_col]
                table_dict[key] = dict(row)

            lookups[table_name] = table_dict
            logger.info(
                f"Loaded {table_name}: {len(table_dict)} rows"
            )

        lookups["_loaded_at"] = time.time()
        lookups["_tag"] = self._compute_tag()
        return lookups

    def setup(self):
        """Initialize cache on worker startup."""
        self._current_tag = self._compute_tag()
        self._lookups = self._shared_handle.acquire(
            self._load_all_tables, tag=self._current_tag
        )

    def start_bundle(self):
        """Check if cache needs refresh at bundle boundary."""
        new_tag = self._compute_tag()
        if new_tag != self._current_tag:
            logger.info(
                f"Cache tag changed: {self._current_tag} -> {new_tag}, refreshing"
            )
            self._current_tag = new_tag
            self._lookups = self._shared_handle.acquire(
                self._load_all_tables, tag=new_tag
            )

    def process(self, element: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Enrich element with lookup data from all tables."""
        enriched = dict(element)

        for table_name, key_col in self._key_columns.items():
            key_value = element.get(key_col)
            if key_value is None:
                continue

            table_dict = self._lookups.get(table_name, {})
            row = table_dict.get(key_value)
            if row:
                for col, val in row.items():
                    if col != key_col:
                        enriched[f"{table_name}_{col}"] = val

        yield enriched
```

#### Memory Impact

Using plain Python dicts: **~48 GB for 75M rows** (too much for most workers).

**Optimization**: Combine Shared class with Arrow storage:

```python
def _load_all_tables(self) -> WeakRefDict:
    """Load as Arrow tables with dict index — shared across DoFn instances."""
    import pyarrow.parquet as pq
    from pyarrow import fs

    gcs = fs.GcsFileSystem()
    lookups = WeakRefDict()

    for table_name, path in self._gcs_paths.items():
        table = pq.read_table(path.replace("gs://", ""), filesystem=gcs)
        key_col = self._key_columns[table_name]
        keys = table.column(key_col).to_pylist()
        index = {k: i for i, k in enumerate(keys)}
        lookups[table_name] = (table, index)

    lookups["_tag"] = self._compute_tag()
    return lookups
```

This gives ~9 GB per worker (Arrow data + dict index), shared across all DoFn instances via `Shared`.

### 2h. Other Creative Approaches

#### h1. Beam's Built-in Enrichment Transform (v2.54+)

Apache Beam 2.54+ includes a native `Enrichment` transform with built-in support for BigTable, BigQuery, Redis, and more.

```python
from apache_beam.transforms.enrichment import Enrichment
from apache_beam.transforms.enrichment_handlers.bigquery import BigQueryEnrichmentHandler

# BigQuery-backed enrichment with automatic batching
handler = BigQueryEnrichmentHandler(
    project="my-project",
    dataset="my_dataset",
    table_name="customers",
    row_restriction_template="customer_id = '{customer_id}'",
    fields=["customer_id"],
    column_names=["name", "tier", "region"],
    min_batch_size=100,
    max_batch_size=1000,
)

enriched = (
    elements
    | "EnrichCustomers" >> Enrichment(handler)
        .with_redis_cache("redis-host", 6379, 3600)
)
```

**Pros**: Official Beam API; built-in batching, throttling, retry; Redis cache built-in.
**Cons**: Issues a BQ query per batch (not free); Redis cache is optional addition (back to approach 1).

#### h2. Stateful DoFn with MapState

Use Beam's `MapState` to store lookup data per-key in the runner's state backend:

```python
class StatefulEnrichDoFn(beam.DoFn):
    LOOKUP_STATE = beam.transforms.userstate.ReadModifyWriteStateSpec(
        'lookup', beam.coders.FastPrimitivesCoder()
    )

    def process(
        self,
        element,
        lookup_state=beam.DoFn.StateParam(LOOKUP_STATE),
    ):
        cached = lookup_state.read()
        if cached is None:
            # Load from external source
            cached = fetch_from_bq(element['key'])
            lookup_state.write(cached)

        yield {**element, **cached}
```

**Pros**: Runner manages state storage and persistence.
**Cons**: State per unique key — 75M state entries is expensive on Dataflow (state is in Streaming Engine, not RAM). Read latency is higher than in-memory. Not suitable for large lookup tables.

#### h3. Precomputed Enrichment (Materialize Before Streaming)

Instead of enriching in the streaming pipeline, precompute enriched views in BQ:

```sql
-- Scheduled query (hourly) that materializes enriched data
CREATE OR REPLACE TABLE enriched_sales AS
SELECT s.*, c.name, c.tier, p.category, st.city
FROM raw_sales s
LEFT JOIN customers c ON s.customer_id = c.customer_id
LEFT JOIN products p ON s.product_id = p.product_id
LEFT JOIN stores st ON s.store_id = st.store_id;
```

Then the streaming pipeline just writes raw data, and enrichment happens in batch.

**Pros**: No enrichment complexity in streaming; BQ handles joins efficiently.
**Cons**: Not real-time; latency = batch interval (1 hour); downstream consumers see raw data until batch runs.

#### h4. BQ Streaming + Materialized Views

Write raw data to BQ via streaming insert, then use materialized views for enriched data:

```sql
CREATE MATERIALIZED VIEW enriched_sales_mv AS
SELECT s.*, c.name, c.tier
FROM raw_sales_stream s
JOIN customers c ON s.customer_id = c.customer_id;
```

**Pros**: Zero streaming enrichment code; BQ auto-refreshes materialized views.
**Cons**: Materialized view refresh is not instant (minutes); limited JOIN support in materialized views; cost of continuous queries.

---

## Comparison Matrix

| Approach | Memory/Worker | Lookup Latency | Throughput | Startup Time | Refresh | Complexity | Monthly Cost (50K msg/sec) |
|----------|-------------|----------------|-----------|-------------|---------|-----------|---------------------------|
| **Redis (1)** | ~0 (external) | ~1-2ms (network) | 500K+ ops/sec | Instant (after sync) | Sync job | Medium | ~$2,120 (Redis + workers) |
| **Arrow+dict (2a)** | ~9 GB | ~0.1us (RAM) | Millions/sec | ~30-60s (load data) | Shared class | Low | ~$1,100 (highmem workers) |
| **Sharded cache (2b)** | ~1 GB/shard | ~0.1us (RAM) | Millions/sec | Complex | Complex | High | ~$800 |
| **mmap (2c)** | ~100 MB active | ~1-10us (page fault) | Variable | ~20s (download) | Re-download | Medium | ~$800 |
| **GCS Parquet (2d)** | ~9 GB (after cache) | ~50ms (miss), ~0.1us (hit) | Varies | Slow (lazy) | Re-read | Medium | ~$800 |
| **SQLite (2e)** | ~100 MB cache | ~2-10us (SSD) | 100K-500K/sec | ~20s (download) | Re-download | Low | ~$800 |
| **DuckDB (2f)** | ~5 GB | ~5-20us | 100K-300K/sec | ~60s (load + index) | Reload | Medium | ~$1,000 |
| **Beam Shared+Arrow (2g)** | ~9 GB (shared) | ~0.1us (RAM) | Millions/sec | ~30-60s (load) | Built-in | Low | ~$1,100 |
| **Beam Enrichment (2h1)** | ~0 (+ Redis cache) | ~1-5ms (BQ) | Batch-limited | Instant | Automatic | Low | ~$2,500 (BQ + Redis + workers) |
| **SQLite+Shared (2e+2g)** | ~100 MB | ~2-10us | 100K-500K/sec | ~20s | Shared tag | Low | ~$800 |

### Scoring (1-5, higher = better)

| Approach | Performance | Memory | Simplicity | Reliability | Cost | **Total** |
|----------|-----------|--------|-----------|------------|------|----------|
| **Redis (1)** | 4 | 5 | 3 | 4 | 2 | **18** |
| **Arrow+dict (2a/2g)** | 5 | 3 | 4 | 4 | 4 | **20** |
| **SQLite (2e)** | 4 | 5 | 4 | 4 | 5 | **22** |
| **DuckDB (2f)** | 3 | 3 | 3 | 3 | 4 | **16** |
| **Sharded (2b)** | 5 | 5 | 1 | 2 | 5 | **18** |
| **GCS Parquet (2d)** | 2 | 3 | 3 | 3 | 5 | **16** |
| **mmap (2c)** | 2 | 4 | 2 | 3 | 5 | **16** |

---

## Recommendation

### Tier 1 (Recommended)

#### Best Overall: Arrow + Dict Index + Beam Shared Class (2a + 2g)

**Why**: Fastest lookups (sub-microsecond), simple code, well-understood Beam pattern, moderate memory (~9 GB shared per worker). No external dependencies. Periodic refresh via Shared tag mechanism.

**When to use**: If workers can have 26+ GB RAM (n1-highmem-4).

```
Pipeline:
  Kafka → Parse → BatchElements → ArrowLookupDoFn (Shared) → Write to BQ

Refresh:
  Beam Shared class auto-refreshes hourly via tag mechanism.
  Data source: Parquet files on GCS (written by scheduled BQ export).
```

#### Runner-up: SQLite on Local Disk (2e)

**Why**: Minimal memory footprint (~100 MB), excellent throughput (100K-500K lookups/sec), battle-tested technology. Works even with standard worker sizes. Easy to reason about.

**When to use**: If you want minimal memory usage, or if lookup data exceeds what fits comfortably in worker RAM.

### Tier 2 (Good Alternative)

#### Redis / Memorystore (1)

**Why**: Proven at scale, decoupled from pipeline workers, supports independent scaling. Best choice if you need sub-millisecond lookups shared across multiple services (not just Dataflow).

**When to use**: If multiple services need the same enrichment data, or if data changes frequently (< 5 min refresh needed).

### Tier 3 (Avoid)

- **Sharded cache (2b)**: Beam's dynamic work rebalancing breaks the sharding assumption.
- **mmap (2c)**: Need for hash index negates mmap benefit.
- **GCS Parquet (2d)**: Just a slower version of loading everything into memory.
- **DuckDB (2f)**: More complex than SQLite, slower at point lookups, less mature.
- **Beam Enrichment Transform with BQ (2h1)**: BQ query per batch is expensive and slow.

### Decision Flowchart

```
75M rows, 5 tables, 10K-100K msg/sec
│
├── Can workers have 26+ GB RAM?
│   ├── YES → Arrow + Dict Index + Beam Shared (2a+2g) ★
│   └── NO  → SQLite on Local Disk (2e) ★
│
├── Need < 5 min refresh or shared across services?
│   └── YES → Redis / Memorystore (1)
│
└── Budget is top priority?
    └── YES → SQLite (2e) — cheapest option
```

---

## References

- [Apache Beam Side Input Patterns](https://beam.apache.org/documentation/patterns/side-inputs/)
- [Apache Beam Shared Class (Cache) Pattern](https://beam.apache.org/documentation/patterns/shared-class/)
- [Apache Beam Enrichment Transform](https://beam.apache.org/documentation/transforms/python/elementwise/enrichment/)
- [Google Cloud Slowly Updating Side Inputs Pattern](https://cloud.google.com/architecture/e-commerce/patterns/slow-updating-side-inputs)
- [Cribl: Disk-Based Lookups for Enrichment at Scale](https://cribl.io/blog/go-big-or-go-home-enrichment-at-scale-with-disk-based-lookups/)
- [Redis Memory Optimization](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/memory-optimization/)
- [Memorystore for Redis Pricing](https://cloud.google.com/memorystore/docs/redis/pricing)
- [Memorystore for Redis Cluster Pricing](https://cloud.google.com/memorystore/cluster/pricing)
- [Google Memorystore Redis Pricing Guide (DragonflyDB)](https://www.dragonflydb.io/guides/google-cloud-redis-pricing)
- [SQLite Performance Tuning (Hacker News)](https://news.ycombinator.com/item?id=35547819)
- [SQLite Optimizations for Ultra High-Performance](https://www.powersync.com/blog/sqlite-optimizations-for-ultra-high-performance)
- [PyArrow Table Documentation](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html)
- [Arrow C++ Hash Join Improvements](https://arrow.apache.org/blog/2025/07/18/recent-improvements-to-hash-join/)
- [Beam Slowly Changing Lookup Cache Example (GitHub)](https://github.com/Kenji-H/beam-examples/tree/master/slowly-changing-lookup-cache)
- [Beam Side Input Lookup with Cache (Gist)](https://gist.github.com/jaketf/5a3820b91552aa4fb24aaa95388fb5c7)
- [Configure Dataflow Worker VMs](https://cloud.google.com/dataflow/docs/guides/configure-worker-vm)
