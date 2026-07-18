# BigQuery Best Practices

## Partitioning Strategies

### Partition Types

| Type | Use Case | Granularity | Limit |
|------|----------|-------------|-------|
| Time-unit (TIMESTAMP/DATE/DATETIME) | Time-series data, event logs | HOUR, DAY, MONTH, YEAR | 10,000 partitions |
| Integer range | ID-based sharding, versioned data | Custom range + interval | 10,000 partitions |
| Ingestion time (`_PARTITIONTIME`) | Unknown partition column at write time | HOUR, DAY, MONTH, YEAR | 10,000 partitions |

### Choosing Partition Granularity
- **DAY (default):** Best for most workloads. Queries typically filter by date.
- **HOUR:** Use only when queries routinely filter by hour AND daily partitions exceed 10 GB each.
- **MONTH/YEAR:** Use for slowly growing tables or when DAY creates too many small partitions.
- **Target: >= 10 GB per partition** for optimal performance. Many small partitions increase metadata overhead.

### Partition Pruning
- Always filter on the partition column in `WHERE` clauses. Without it, BigQuery scans all partitions.
- Use `_PARTITIONTIME` pseudo-column for ingestion-time partitioned tables.
- Partition pruning applies before query execution -- it determines which partitions to read.
- Avoid expressions on partition columns that prevent pruning: `WHERE DATE(timestamp_col) = '2025-01-01'` may not prune if the table is partitioned on `timestamp_col` directly. Use `WHERE timestamp_col BETWEEN '2025-01-01' AND '2025-01-01 23:59:59'`.

## Clustering Best Practices

### Column Selection
- Cluster on columns most frequently used in `WHERE`, `JOIN`, `GROUP BY`, and `ORDER BY`.
- Up to 4 clustering columns per table.
- Column order matters: put the most-filtered column first.
- Best for high-cardinality columns (user_id, timestamp) where partitioning alone is insufficient.

### When to Use Clustering vs Partitioning
- **Partitioning:** When queries always filter on a single time/integer column.
- **Clustering:** When queries filter on multiple columns, or need finer granularity than partitioning allows.
- **Both:** Partition on date, cluster on frequently-filtered columns within each partition. This is the recommended approach for most tables.
- Unpartitioned tables > 64 MB and partitions > 64 MB benefit from clustering.

### Auto-Clustering
BigQuery automatically re-clusters data in the background at no cost. No manual maintenance needed. New data written to a clustered table is organized in temporary storage and periodically merged.

## Storage Write API vs Legacy Streaming Inserts

| Feature | Storage Write API | Legacy Streaming (`insertAll`) |
|---------|------------------|-------------------------------|
| Throughput | Higher (Protobuf binary) | Lower (JSON-based) |
| Cost | Lower per-byte | Higher per-byte |
| Exactly-once | Yes (committed streams) | No (best-effort dedup) |
| CDC support | Yes (`_CHANGE_TYPE`) | No |
| Schema validation | Protobuf at write time | JSON at insert time |
| Recommended | Yes (all new pipelines) | Legacy only |

### Write API Modes
- **Default stream:** Highest throughput, at-least-once. Use for CDC and high-volume ingestion.
- **Committed stream:** Exactly-once with offset tracking. Use when duplicates are unacceptable.
- **Buffered stream:** Write then commit on demand. Use for micro-batch patterns.
- **Pending stream:** Atomic multi-stream commits. Use for batch-like guarantees in streaming.

## CDC Patterns (Change Data Capture)

### Setup Requirements
```sql
CREATE TABLE my_dataset.my_table (
  id INT64 PRIMARY KEY NOT ENFORCED,
  name STRING,
  updated_at TIMESTAMP
)
OPTIONS (max_staleness = INTERVAL 15 MINUTE);
```

### Key Configuration
- **Primary key:** Required, up to 16 columns. NOT ENFORCED (BigQuery does not validate uniqueness).
- **`_CHANGE_TYPE`:** Pseudocolumn accepting `UPSERT` or `DELETE`.
- **`_CHANGE_SEQUENCE_NUMBER`:** Optional pseudocolumn for custom ordering (hex string format).
- **`max_staleness`:** Controls how often background merge applies changes. Formula:
  ```
  max_staleness = 2 * P95(background_apply_duration) + 7 minutes
  ```
- **DELETE retention:** 2-day window for out-of-order deletes.

### CDC Limitations
- No DML (DELETE, UPDATE, MERGE) allowed on CDC-enabled tables.
- No wildcard table queries or search indexes.
- Cannot use Storage Read API.
- Maximum 2,000 top-level columns.
- Primary keys cannot be modified after CDC operations begin.

### Cost Management
- Use `BACKGROUND` or `BACKGROUND_CHANGE_DATA_CAPTURE` reservation assignment for dedicated compute.
- Avoid excessively low `max_staleness` (increases merge frequency and cost).
- Monitor `upsert_stream_apply_watermark` via `INFORMATION_SCHEMA.TABLES`.

## Schema Evolution

### Safe Operations (No Data Rewrite)
- `ADD COLUMN` -- new nullable column, appended to schema.
- `ALTER COLUMN SET OPTIONS` -- change description or policy tags.
- `ALTER COLUMN SET DEFAULT` -- set default value for new inserts.

### Require Caution
- `ALTER COLUMN DROP NOT NULL` -- relaxing constraints is safe.
- Column type widening: `INT64` to `NUMERIC`, `FLOAT64` to `BIGNUMERIC`.
- Nested field additions in RECORD/STRUCT types.

### Not Supported (Requires Table Recreate)
- Rename columns (use `ALTER TABLE RENAME COLUMN` -- creates alias only in some cases).
- Remove columns (`ALTER TABLE DROP COLUMN` supported but check dependencies).
- Change partition column or clustering columns after creation.

## Cost Optimization

### Compute Pricing (BigQuery Editions)

| Edition | Use Case | Features |
|---------|----------|----------|
| Standard | Dev/test, ad-hoc | Basic compute |
| Enterprise | Production | ML, security, governance |
| Enterprise Plus | Mission-critical | Advanced security, multi-region |

- **On-demand:** Pay per TB scanned. Good for sporadic, unpredictable workloads.
- **Capacity (slots):** Pay for reserved compute. Good for sustained, predictable workloads.
- Set reservation **baseline = 0** for fully on-demand with autoscaling cap.
- Buy 1-year or 3-year commitments for 20-40% discount on sustained workloads.
- Use `BACKGROUND` reservation type for CDC merge jobs to separate from interactive queries.

### Storage Optimization
- Tables/partitions unmodified for 90 days automatically get 50% storage discount (long-term pricing).
- Set dataset/table/partition expiration to auto-delete stale data.
- Use `INFORMATION_SCHEMA.TABLE_STORAGE` to monitor consumption.
- Pre-aggregate transactional data and expire raw rows.

## Query Optimization

### General Rules
1. **Never `SELECT *`** in production queries. Specify only needed columns.
2. **Filter on partition and clustering columns** first.
3. **Pre-aggregate before JOIN:** `GROUP BY` before joining reduces shuffle.
4. **Largest table first in JOINs** for optimal broadcast join planning.
5. **Use `INT64` for join keys** over `STRING` (faster comparison).
6. **Declare primary/foreign keys** (NOT ENFORCED) to help the optimizer.

### Anti-Patterns to Avoid
- Self-joins that square output rows. Use window functions instead.
- Repeated CTE evaluation. Materialize to temp tables for reuse.
- Single-row DML. Batch operations for efficiency.
- `ORDER BY` without `LIMIT` on large result sets.
- Cross joins without pre-aggregation.

### Materialized Views
- Automatically maintained by BigQuery on base table changes.
- Queries are automatically rewritten to use materialized views when beneficial.
- Best for aggregations on large tables that are queried frequently.
- Support partition alignment with base tables.

## BigQuery Iceberg Tables (External Catalog)

### Managed Iceberg Tables (BigLake)
- Created natively in BigQuery with `table_format = 'ICEBERG'`.
- Data stored in customer-owned GCS bucket in Parquet format.
- Automatic storage optimization: adaptive file sizing, auto-clustering, garbage collection.
- Schema evolution supported (add, drop, rename columns).
- Iceberg V2 snapshot export with automatic refresh on mutations.
- Queryable from external engines (Spark, Flink, Trino) via exported snapshots.

### External Catalog Tables (BLMS REST)
- Tables managed in BigLake Metastore REST catalog.
- Queried from BigQuery using four-part naming: `project.catalog.namespace.table`.
- Credential vending for fine-grained GCS access control.
- Read-only from BigQuery (mutations via external engines).
- Useful for multi-engine lakehouse architectures.

### When to Use Each
- **Managed Iceberg:** Full BigQuery DML + external engine read access needed.
- **External Catalog (BLMS):** Multi-engine write access needed, BigQuery reads only.
- **Standard BigQuery:** No external engine access needed, maximum BigQuery feature set.

---

*Sources: [Partitioned Tables](https://docs.cloud.google.com/bigquery/docs/partitioned-tables), [Clustered Tables](https://docs.cloud.google.com/bigquery/docs/clustered-tables), [Storage Optimization](https://docs.cloud.google.com/bigquery/docs/best-practices-storage), [Compute Optimization](https://docs.cloud.google.com/bigquery/docs/best-practices-performance-compute), [CDC](https://docs.cloud.google.com/bigquery/docs/change-data-capture), [Iceberg Tables](https://docs.cloud.google.com/bigquery/docs/iceberg-tables), [BigQuery Editions](https://docs.cloud.google.com/bigquery/docs/editions-intro)*
