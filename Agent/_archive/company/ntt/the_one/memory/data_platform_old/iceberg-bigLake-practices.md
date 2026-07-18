# Apache Iceberg & BigLake Best Practices

## Iceberg Table Design: Partitioning

### Hidden Partitioning
Iceberg uses hidden partitioning -- users write queries against logical columns, and Iceberg automatically maps to physical partition layout. No need for synthetic partition columns (unlike Hive where `WHERE event_date = '2025-01-01'` requires a separate `event_date` partition column).

### Partition Transforms

| Transform | Input | Output | Use Case |
|-----------|-------|--------|----------|
| `year(ts)` | Timestamp | Integer year | Multi-year tables with yearly queries |
| `month(ts)` | Timestamp | Integer year-month | Monthly aggregations |
| `day(ts)` | Timestamp | Integer date | Daily ingestion (most common) |
| `hour(ts)` | Timestamp | Integer date-hour | High-volume streaming |
| `bucket(N, col)` | Any | Hash mod N | Even distribution by ID |
| `truncate(L, col)` | String/Integer | Prefix of length L | Range-based access patterns |
| `identity(col)` | Any | Same value | Low-cardinality categorical columns |

### Choosing Partition Strategy
- **Target: 100 MB - 1 GB per partition** for optimal read performance.
- **Day partitioning** is the best default for time-series data. Only use hour if daily partitions exceed 1 GB.
- **Bucket partitioning** for ID-based access patterns. Choose bucket count based on: `total_data_size / target_partition_size`.
- **Avoid over-partitioning.** Too many small files (< 8 MB each) degrade read performance.
- Combine transforms: `day(timestamp)` + `bucket(16, member_id)` for both time-range and point lookups.

### Partition Evolution
Iceberg supports changing partition layout without rewriting data:
```sql
ALTER TABLE my_table ADD PARTITION FIELD day(event_timestamp);
ALTER TABLE my_table DROP PARTITION FIELD month(event_timestamp);
```
- Old data retains its original partition layout. New data uses the new layout.
- Queries automatically handle mixed partition layouts transparently.
- No data migration needed -- this is a metadata-only operation.

## Sorting (Sort Order)

### Sort Order Configuration
```sql
ALTER TABLE my_table WRITE ORDERED BY category, event_timestamp;
```

### Best Practices
- Sort by columns used in `WHERE` clauses after partition pruning.
- Put low-cardinality columns first (improves min/max statistics for file pruning).
- Sort order is per-write. Old data retains its original sort order.
- Sorting is optional -- engines can write unsorted when sorting cost is prohibitive.
- Combine with Parquet column statistics: sorted data yields tighter min/max ranges per row group, enabling more effective data skipping.

## Schema Evolution

### Supported Operations (Metadata-Only, No Data Rewrite)

| Operation | Safety | Notes |
|-----------|--------|-------|
| Add column | Safe | Existing data returns NULL for new column |
| Drop column | Safe | Column data preserved in files but hidden |
| Rename column | Safe | Uses internal field IDs, not names |
| Reorder columns | Safe | Metadata-only change |
| Widen type (int -> long) | Safe | Compatible type promotion |
| Make required -> optional | Safe | Relaxing nullability |

### Schema Evolution Rules
- Iceberg tracks columns by **field ID**, not by name. Renaming is safe.
- Adding a required column is NOT allowed (existing data can't satisfy the constraint).
- Type narrowing (long -> int) is NOT allowed.
- When dropping a column, the field ID is retired. Re-adding a column with the same name gets a new ID.

### Schema Evolution in Practice
```python
# Via PyIceberg
from pyiceberg.catalog import load_catalog

catalog = load_catalog("my_catalog")
table = catalog.load_table("namespace.table_name")

with table.update_schema() as update:
    update.add_column("new_field", StringType(), doc="Description")
    update.rename_column("old_name", "new_name")
```

## BigLake Metastore (BLMS) REST Catalog

### Architecture
```
                    BLMS REST Catalog
                    (Single Source of Truth)
                   /          |          \
                  /           |           \
           Apache Spark   Apache Beam    BigQuery
           (read/write)   (write)        (read)
                  \           |           /
                   \          |          /
                    Google Cloud Storage
                    (Parquet data files)
```

### Catalog Configuration

**REST Endpoint:** `https://biglake.googleapis.com/iceberg/v1/restcatalog`

**Authentication Options:**
1. **End-user credentials:** Users access with their own IAM identity. Simpler setup.
2. **Credential vending (recommended for production):** BLMS controls fine-grained GCS access. Users don't need direct bucket permissions.

**Required IAM Roles:**
- Admin: `roles/biglake.admin` + `roles/storage.admin`
- Read (vended): `roles/biglake.viewer`
- Write (vended): `roles/biglake.editor`
- BigQuery DML: `roles/bigquery.dataEditor` + `roles/storage.admin`

### Catalog Creation
```bash
gcloud beta biglake iceberg catalogs create my-catalog \
    --project my-project \
    --catalog-type gcs-bucket \
    --credential-mode credential-vending \
    --primary-location us-central1
```

### Client Configuration (Beam/Dataflow)
```python
catalog_properties = {
    "type": "rest",
    "uri": "https://biglake.googleapis.com/iceberg/v1/restcatalog",
    "warehouse": "gs://my-data-bucket",
    "rest.auth.type": "org.apache.iceberg.gcp.auth.GoogleAuthManager",
    "io-impl": "org.apache.iceberg.gcp.gcs.GCSFileIO",
    "header.X-Iceberg-Access-Delegation": "vended-credentials",
}
```

### Key Limitations
- Only Parquet file format supported.
- `metadata.json` limited to 1 MB.
- No row/column-level security on REST catalog tables.
- Cannot create BigQuery views over REST catalog tables.
- Nested namespaces with credential vending can inadvertently grant access to unintended resources.

## Iceberg + BigQuery Integration

### Three Integration Modes

| Mode | Write Engine | Read from BQ | BQ DML | Use Case |
|------|-------------|-------------|--------|----------|
| Managed Iceberg tables | BigQuery | Yes (native) | Yes | BQ-first, open format export |
| BLMS REST catalog | External (Spark/Beam) | Yes (federated) | Limited | Multi-engine lakehouse |
| External catalog tables | External | Yes (linked) | No | Legacy Hive/custom catalogs |

### Querying BLMS Tables from BigQuery
```sql
-- Four-part naming: project.catalog.namespace.table
SELECT * FROM `my-project.my-catalog.my-namespace.my-table`
WHERE ingestedTHDate = 20250101;
```

### Managed Iceberg Tables in BigQuery
```sql
CREATE TABLE my_dataset.my_table (
  id INT64,
  name STRING,
  event_time TIMESTAMP
)
WITH CONNECTION `my-project.us-central1.my-connection`
OPTIONS (
  file_format = 'PARQUET',
  table_format = 'ICEBERG'
);
```
Features: auto-clustering, garbage collection, V2 snapshot export, time travel, column-level security.

## Compaction and Maintenance

### Data File Compaction
Small files degrade read performance. Compact regularly for tables with streaming writes.

```sql
-- Spark procedure
CALL catalog.system.rewrite_data_files(
  table => 'namespace.table_name',
  options => map('target-file-size-bytes', '134217728')  -- 128 MB target
);
```

**When to compact:**
- Average file size < 32 MB.
- Number of data files per partition > 100.
- Query performance degradation observed.

**Target file size:** 128 MB - 512 MB. Smaller for frequently filtered tables, larger for scan-heavy tables.

### Snapshot Expiration
```sql
CALL catalog.system.expire_snapshots(
  table => 'namespace.table_name',
  older_than => TIMESTAMP '2025-01-01 00:00:00',
  retain_last => 5
);
```

**Schedule:** Daily or weekly. Retain at least the last 3-5 snapshots for time travel.
**Effect:** Removes snapshot metadata and data files no longer referenced by any active snapshot.

### Manifest Rewrite
```sql
CALL catalog.system.rewrite_manifests('namespace.table_name');
```
Optimizes manifest file organization for faster query planning. Run after heavy compaction.

### Orphan File Removal
```sql
CALL catalog.system.remove_orphan_files(
  table => 'namespace.table_name',
  older_than => TIMESTAMP '2025-01-01 00:00:00'
);
```
Removes data files in the table's location not referenced by any metadata. Run carefully -- ensure no concurrent writes.

### Metadata File Cleanup
```properties
# Auto-delete old metadata files after each commit
write.metadata.delete-after-commit.enabled=true
write.metadata.previous-versions-max=10
```

### Recommended Maintenance Schedule

| Operation | Frequency | Priority |
|-----------|-----------|----------|
| Snapshot expiration | Daily | Critical |
| Data file compaction | Daily (streaming) / Weekly (batch) | High |
| Orphan file removal | Weekly | Medium |
| Manifest rewrite | After compaction | Medium |
| Metadata cleanup | Automatic (configure once) | Low |

## Time Travel Queries

```sql
-- Read from a specific snapshot
SELECT * FROM my_table VERSION AS OF 123456789;

-- Read from a specific timestamp
SELECT * FROM my_table TIMESTAMP AS OF '2025-01-15 10:00:00';
```

**Retention:** Controlled by `history.expire.max-snapshot-age-ms` (default: 5 days). Adjust based on recovery SLA.
**Cost:** Time travel reads scan the same data volume as current reads. Older snapshots may reference un-compacted files.

## Managed vs Manual Iceberg Writes in Beam

### Managed Write (managed.Write)
```python
pcoll | managed.Write(config={
    "table": "catalog.namespace.table",
    "catalog_name": "my_catalog",
    "catalog_properties": {...},
})
```
- **Auto-creates table** if it doesn't exist (schema from Beam Row).
- **Auto-creates partitions** based on `partition_fields` config.
- Handles metadata commits automatically.
- Recommended for Dataflow pipelines.

### Manual Write (PyIceberg)
```python
table = catalog.load_table("namespace.table_name")
table.append(arrow_table)
```
- Full control over write parameters, compaction, and commit.
- Requires explicit table creation and schema management.
- Better for batch ETL scripts and maintenance operations.

### When to Use Each
- **managed.Write:** Streaming pipelines, Dataflow jobs, auto-schema management.
- **PyIceberg:** Batch scripts, maintenance operations, schema evolution, deploy-time table setup.
- **BigQuery DML:** When data is in BQ-managed Iceberg tables and you want SQL-based mutations.

---

*Sources: [Iceberg Partitioning](https://iceberg.apache.org/docs/latest/partitioning/), [Iceberg Schema Evolution](https://iceberg.apache.org/docs/latest/evolution/), [Iceberg Maintenance](https://iceberg.apache.org/docs/1.5.1/maintenance/), [BLMS REST Catalog](https://docs.cloud.google.com/biglake/docs/blms-rest-catalog), [BigQuery Iceberg Tables](https://docs.cloud.google.com/bigquery/docs/iceberg-tables), [BigLake Metastore Overview](https://docs.cloud.google.com/bigquery/docs/about-blms)*
