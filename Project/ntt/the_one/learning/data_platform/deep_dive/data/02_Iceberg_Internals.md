# Apache Iceberg — Internals Deep Dive

> Snapshot, manifest, metadata tree, time travel, hidden partitioning
> Why Iceberg "ate the lakehouse" ปี 2024-2026

---

## 1. ทำไม Iceberg ครองตลาด

### Pain Points ของ Hive Tables (predecessor)

1. **Directory listing**: query ต้อง list S3/GCS = ช้า + costly
2. **No atomic operations**: rename = copy → not atomic
3. **No time travel**: ไม่มี snapshot history
4. **Schema evolution painful**: rename column = full rewrite
5. **Partition by directory**: rigid, hard to change
6. **No row-level deletes**: must rewrite whole file

### Iceberg Solutions

1. ✅ **Metadata-driven**: ไม่ list directories, ใช้ manifest tree
2. ✅ **Atomic snapshot commits**: optimistic concurrency
3. ✅ **Time travel**: every commit = new snapshot
4. ✅ **In-place schema evolution**: by ID, not by position
5. ✅ **Hidden partitioning**: partition transforms (e.g., `days(ts)`)
6. ✅ **Row-level operations**: delete files (positional/equality)

---

## 2. Iceberg Architecture — 5 Layers

```
┌─────────────────────────────────────────────────────┐
│  LAYER 1: CATALOG                                   │
│  Maps: table_name → current metadata file path      │
│  (REST Catalog, Hive Metastore, AWS Glue, etc.)     │
└────────────────────────┬────────────────────────────┘
                         │ points to
                         ▼
┌─────────────────────────────────────────────────────┐
│  LAYER 2: METADATA FILE (v2.metadata.json)          │
│  • table_uuid, location, schema                     │
│  • partition specs (versioned)                      │
│  • snapshots list (history)                         │
│  • current_snapshot_id                              │
└────────────────────────┬────────────────────────────┘
                         │ snapshot points to
                         ▼
┌─────────────────────────────────────────────────────┐
│  LAYER 3: MANIFEST LIST (snap-XXX.avro)             │
│  Lists all manifest files for this snapshot         │
│  • partition summaries (min/max per partition)      │
│  • allows manifest pruning                          │
└────────────────────────┬────────────────────────────┘
                         │ lists
                         ▼
┌─────────────────────────────────────────────────────┐
│  LAYER 4: MANIFEST FILE (XXX.avro)                  │
│  Lists data files                                    │
│  • file path • partition values • column stats      │
│  • allows file pruning                              │
└────────────────────────┬────────────────────────────┘
                         │ lists
                         ▼
┌─────────────────────────────────────────────────────┐
│  LAYER 5: DATA FILES (Parquet/ORC/Avro)             │
│  Actual data                                         │
└─────────────────────────────────────────────────────┘
```

### Visual: File Layout on Storage

```
s3://warehouse/orders/
├── metadata/
│   ├── v1.metadata.json
│   ├── v2.metadata.json     ← current
│   ├── snap-1234.avro       ← snapshot 1's manifest list
│   ├── snap-5678.avro       ← snapshot 2's manifest list
│   ├── manifest-abc.avro
│   ├── manifest-def.avro
│   └── ...
└── data/
    ├── 00001-0-xxx.parquet
    ├── 00002-0-yyy.parquet
    └── ...
```

---

## 3. Snapshot Mechanism

### What is a Snapshot

Snapshot = **immutable view** ของ table ณ เวลาหนึ่ง

```json
{
  "snapshot_id": 1234567890,
  "parent_snapshot_id": 9876543210,
  "timestamp_ms": 1714780800000,
  "operation": "append",
  "manifest_list": "s3://.../snap-1234.avro",
  "summary": {
    "added-data-files": "5",
    "added-records": "10000",
    "added-files-size": "100MB"
  }
}
```

### Snapshot Operations

| Operation | What |
|---|---|
| `append` | New data added |
| `overwrite` | Replace partition / table |
| `delete` | Rows deleted |
| `replace` | Compact / rewrite |

### Time Travel

```sql
-- By snapshot ID
SELECT * FROM orders FOR VERSION AS OF 1234567890

-- By timestamp
SELECT * FROM orders FOR TIMESTAMP AS OF '2026-05-01 10:00:00'

-- Spark
spark.read.format("iceberg")
    .option("snapshot-id", "1234567890")
    .load("warehouse.orders")
```

### Why Time Travel Matters

1. **Reproducible ML training**: pin to snapshot
2. **Audit**: see exact data at any point
3. **Rollback**: revert bad write
4. **Debug**: compare snapshots

---

## 4. Manifest Files — The Pruning Magic

### Why Manifest Lists Speed Up Queries

Without Iceberg (Hive style):
```
1. List all directories under /events/
2. List all files in each
3. Filter by partition column
4. Read file footers for stats
= 1000s of S3 calls for big tables
```

With Iceberg:
```
1. Read metadata.json (1 file)
2. Read manifest list (1 file)
   → has partition min/max per manifest → prune
3. Read selected manifests (few files)
   → has data file stats → prune more
4. Read selected data files
= 5-10 S3 calls regardless of table size
```

### Manifest List Structure

```
manifest_list (snap-1234.avro):
[
  {
    manifest_path: "manifest-abc.avro",
    partitions: [
      {field_id: 1, min: 2026-04-01, max: 2026-04-15}
    ],
    added_files_count: 100,
    deleted_files_count: 0
  },
  {
    manifest_path: "manifest-def.avro",
    partitions: [
      {field_id: 1, min: 2026-04-16, max: 2026-04-30}
    ],
    ...
  }
]
```

Query `WHERE date = '2026-04-20'` → skip manifest-abc entirely

### Manifest File Structure

```
manifest-def.avro:
[
  {
    data_file: "00001-0-xxx.parquet",
    partition: {date: 2026-04-20},
    record_count: 1000,
    column_stats: {
      amount: {min: 0.5, max: 999.99, null_count: 0}
    }
  },
  ...
]
```

Query `WHERE amount > 500` → use column stats → skip files with max ≤ 500

---

## 5. Hidden Partitioning — Game-Changing Feature

### Hive Way (broken)
```sql
CREATE TABLE events (
    id INT,
    event_time TIMESTAMP,
    event_date STRING  -- DUPLICATE: stored twice
) PARTITIONED BY (event_date)

-- User must remember
SELECT * FROM events WHERE event_date = '2026-05-01'
-- If they forget date: full scan!
```

### Iceberg Way (works)
```sql
CREATE TABLE events (
    id INT,
    event_time TIMESTAMP
) PARTITIONED BY (days(event_time))
-- No duplicate column!

-- User just queries naturally
SELECT * FROM events WHERE event_time > '2026-05-01'
-- Iceberg automatically maps to partition
```

### Available Transforms

| Transform | Example |
|---|---|
| `identity(col)` | Same as Hive |
| `bucket(N, col)` | Hash to N buckets |
| `truncate(L, col)` | First L chars/digits |
| `year(ts)` | Year only |
| `month(ts)` | Year-month |
| `day(ts)` | Date |
| `hour(ts)` | Hour |
| `void(col)` | Drop partition |

### Partition Evolution (Iceberg superpower)

```sql
-- Year 1: partition by month
ALTER TABLE events ADD PARTITION FIELD month(event_time)

-- Year 5: data grew, switch to day
ALTER TABLE events DROP PARTITION FIELD month(event_time)
ALTER TABLE events ADD PARTITION FIELD day(event_time)

-- Old data still works! (uses old partition spec)
-- New data uses new partition spec
-- Queries work transparently across both
```

Hive can't do this — Iceberg can because partition is in metadata, not directory

---

## 6. Schema Evolution

### How Iceberg Tracks Columns

By **ID, not name or position**:

```json
{
  "schema": {
    "fields": [
      {"id": 1, "name": "id", "type": "int"},
      {"id": 2, "name": "name", "type": "string"},
      {"id": 3, "name": "email", "type": "string"}
    ]
  }
}
```

### Allowed Operations (no rewrite needed)

```sql
-- Add column
ALTER TABLE orders ADD COLUMN status STRING

-- Drop column (just remove from metadata)
ALTER TABLE orders DROP COLUMN old_field

-- Rename
ALTER TABLE orders RENAME COLUMN email TO email_address
-- ID stays same, just name changes

-- Reorder
ALTER TABLE orders ALTER COLUMN status FIRST

-- Type promotion (safe widening)
ALTER TABLE orders ALTER COLUMN amount TYPE DOUBLE  -- from float
```

### Why this works

Reader code:
```
For each column requested:
  Look up by ID (not name!) in current schema
  Map to file's schema by ID
  Read column from Parquet
```

Old Parquet files don't have the new column → readers return NULL

---

## 7. Row-Level Operations (Merge-on-Read vs Copy-on-Write)

### Problem

Object stores (S3/GCS) don't support file modification — only create/delete

How to handle DELETE / UPDATE on rows in a 10GB Parquet file?

### Strategy 1: Copy-on-Write (CoW)

```sql
DELETE FROM orders WHERE status = 'cancelled'
-- Write entire new file without those rows
-- Mark old file as deleted in next snapshot
```

**Pros**: Reads fast (no merge needed)
**Cons**: Writes slow (rewrite whole file for 1 deleted row)
**Use case**: Read-heavy, low-update tables

### Strategy 2: Merge-on-Read (MoR) — Iceberg v2+

Two types of delete files:

#### Position Delete File
```
Lists: (data_file_path, row_position) to skip
- file_a.parquet, row 42
- file_a.parquet, row 100
```

#### Equality Delete File
```
Lists predicates: rows matching these are deleted
- order_id = 'xyz123'
- order_id = 'abc456'
```

**At read time**:
```
Read data file
  ↓
Apply position deletes (skip those rows)
  ↓
Apply equality deletes (filter matching)
  ↓
Return remaining rows
```

**Pros**: Writes fast (just append delete file)
**Cons**: Reads slower (merge work)
**Use case**: Write-heavy, streaming updates

### When to use which

```sql
ALTER TABLE orders SET TBLPROPERTIES (
    'write.delete.mode' = 'merge-on-read',
    'write.update.mode' = 'merge-on-read',
    'write.merge.mode' = 'copy-on-write'
)
```

---

## 8. Compaction & Maintenance

### Why Compact

Streaming writes create many small files:
```
Hour 1: file1.parquet (10 MB)
Hour 2: file2.parquet (10 MB)
...
Hour 24: 24 small files = inefficient reads
```

### Compaction Operations

#### Rewrite Data Files
```sql
-- Combine small files into larger ones
CALL system.rewrite_data_files('warehouse.orders')

-- With options
CALL system.rewrite_data_files(
    table => 'warehouse.orders',
    options => map(
        'min-input-files', '5',
        'target-file-size-bytes', '536870912'  -- 512 MB
    )
)
```

#### Rewrite Manifests (consolidate metadata)
```sql
CALL system.rewrite_manifests('warehouse.orders')
```

#### Expire Snapshots (cleanup history)
```sql
-- Keep last 7 days of snapshots
CALL system.expire_snapshots(
    table => 'warehouse.orders',
    older_than => TIMESTAMP '2026-04-27 00:00:00',
    retain_last => 5
)
```

#### Remove Orphan Files
```sql
-- Delete data files not referenced by any snapshot
CALL system.remove_orphan_files('warehouse.orders')
```

### Recommended Maintenance Schedule

```
Daily:
  - rewrite_manifests (fast, low impact)

Weekly:
  - rewrite_data_files (consolidate small files)

Monthly:
  - expire_snapshots (free storage)
  - remove_orphan_files (cleanup)
```

---

## 9. Iceberg Catalogs

### Catalog Types

| Catalog | Use case |
|---|---|
| **REST Catalog** | Modern, vendor-neutral, multi-engine |
| **Hive Metastore** | Legacy compatibility |
| **AWS Glue** | AWS native |
| **Nessie** | Git-like branches |
| **Polaris** | Snowflake's open catalog (2024+) |
| **Unity Catalog** | Databricks (now OSS) |
| **Project Tacit (Apache)** | New REST-based |

### REST Catalog Spec

```http
# List tables
GET /v1/{prefix}/namespaces/{namespace}/tables

# Get table
GET /v1/{prefix}/namespaces/{ns}/tables/{table}
Response: {metadata-location, metadata}

# Commit
POST /v1/{prefix}/namespaces/{ns}/tables/{table}
Body: {requirements: [...], updates: [...]}
```

ตัว engine (Spark, Trino, Flink) คุยกับ catalog ผ่าน REST → คลายปัญหา vendor lock-in

### Configure Spark with REST Catalog

```python
spark = SparkSession.builder \
    .config("spark.sql.catalog.warehouse", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.warehouse.type", "rest") \
    .config("spark.sql.catalog.warehouse.uri", "https://catalog.example.com") \
    .config("spark.sql.catalog.warehouse.token", "...") \
    .getOrCreate()
```

---

## 10. Iceberg Performance Tuning

### Read Optimization

#### 1. Enable Vectorized Reads
```sql
ALTER TABLE orders SET TBLPROPERTIES (
    'read.parquet.vectorization.enabled' = 'true',
    'read.parquet.vectorization.batch-size' = '5000'
)
```

#### 2. Bloom Filters for High-Cardinality Filters
```sql
ALTER TABLE orders SET TBLPROPERTIES (
    'write.parquet.bloom-filter-enabled.column.order_id' = 'true',
    'write.parquet.bloom-filter-fpp.column.order_id' = '0.01'
)
```

#### 3. Sort Order (Z-order or sort)
```sql
ALTER TABLE orders WRITE ORDERED BY (event_time, customer_id)
-- Future writes sorted; co-located data → less files scanned
```

### Write Optimization

#### Target File Size
```sql
ALTER TABLE orders SET TBLPROPERTIES (
    'write.target-file-size-bytes' = '536870912'  -- 512 MB
)
```

#### Distribution Mode
```python
# Spark write
df.write.format("iceberg")
    .option("write-distribution-mode", "hash")  # cluster by partition
    .mode("append")
    .saveAsTable("warehouse.orders")
```

Options:
- `none`: no shuffle (might create many small files)
- `hash`: cluster by partition (recommended)
- `range`: sort + cluster (best file sizes)

---

## 11. Iceberg vs Delta Lake vs Hudi (2026 reality)

| Feature | Iceberg | Delta Lake | Hudi |
|---|---|---|---|
| Origin | Netflix | Databricks | Uber |
| Open governance | ✅ Apache | Linux Foundation | ✅ Apache |
| Hidden partitioning | ✅ Best | ❌ | Partial |
| Time travel | ✅ | ✅ | ✅ |
| Schema evolution | ✅ Best | ✅ | ✅ |
| MoR support | ✅ | Limited | ✅ Original |
| Branches/tags | Beta | ❌ | ❌ |
| Multi-engine | ✅ Best | Improving | ✅ |
| GCP support | BigLake native | OK | OK |
| AWS support | Athena native | OK | OK |
| Streaming | Good | ✅ Best (Spark) | ✅ Best |

**2026 winner trend**: Iceberg leads in multi-engine + open governance
- BigLake on Iceberg
- AWS S3 Tables on Iceberg
- Snowflake Polaris on Iceberg
- Delta keeps Databricks shop

---

## 12. Common Iceberg Issues

### Issue 1: Small files proliferation
**Cause**: Streaming writes, no compaction
**Fix**: Schedule `rewrite_data_files` weekly

### Issue 2: Slow metadata scans
**Cause**: Too many manifests
**Fix**: `rewrite_manifests` daily

### Issue 3: Storage cost explosion
**Cause**: Snapshots accumulating, orphan files
**Fix**: Schedule `expire_snapshots` + `remove_orphan_files`

### Issue 4: Catalog conflicts
**Cause**: Multiple writers same table without lock
**Fix**: Use catalog with optimistic concurrency, retry logic

### Issue 5: Slow first read
**Cause**: REST catalog round-trip latency
**Fix**: Cache metadata client-side, use connection pooling

---

## 13. Cheat Sheet

### Q: "ทำไม Iceberg ชนะ Hive?"
> "Metadata-driven instead of directory listing — แค่อ่าน manifest tree (5-10 calls) แทนที่จะ list directories (1000s calls)
> Plus: hidden partitioning, schema evolution by ID, atomic snapshots, time travel"

### Q: "Iceberg vs Delta Lake?"
> "Iceberg: better hidden partitioning, multi-engine (Spark, Trino, Flink, Dataflow), open catalog
> Delta: better Databricks integration, stronger streaming pipeline
> 2026 trend: Iceberg leading in multi-cloud / multi-engine"

### Q: "Time travel ทำงานยังไง?"
> "ทุก commit = new snapshot ใน metadata.json
> Snapshot = immutable, points to manifest list
> Query 'AS OF snapshot_id' → engine ใช้ manifest list ของ snapshot นั้น
> Old data files ยังอยู่ จนกว่าจะ expire_snapshots"

### Q: "Hidden partitioning ดียังไง?"
> "User เขียน `WHERE event_time > X` ตามปกติ
> Iceberg แปลให้เอง = `days(event_time) > X` (partition column)
> User ไม่ต้อง maintain duplicate `event_date` column ที่อาจไม่ sync กับ event_time"

### Q: "MoR vs CoW?"
> "CoW: write whole file ใหม่ (slow write, fast read) — เหมาะ batch + read-heavy
> MoR: append delete file (fast write, slower read) — เหมาะ streaming + write-heavy
> เลือกได้ per-table ผ่าน TBLPROPERTIES"

---

## Sources

- [Apache Iceberg Spec](https://iceberg.apache.org/spec/)
- [Apache Iceberg Metadata Explained: Snapshots & Manifests](https://olake.io/blog/2025/10/03/iceberg-metadata/)
- [Understanding the Apache Iceberg Manifest List (Snapshot)](https://dev.to/alexmercedcoder/understanding-the-apache-iceberg-manifest-list-snapshot-507)
- [Apache Iceberg Metadata Tables: Querying the Internals](https://datalakehousehub.com/blog/2026-04-29-apache-iceberg-masterclass-11-metadata-tables/)
- [A Guide to Apache Iceberg Snapshots and Time Travel](https://www.e6data.com/blog/apache-iceberg-snapshots-time-travel)
- [How Iceberg works - Amazon EMR](https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-iceberg-how-it-works.html)
- [Iceberg Table Architecture: Metadata and Snapshots](https://www.conduktor.io/glossary/iceberg-table-architecture-metadata-and-snapshots)
