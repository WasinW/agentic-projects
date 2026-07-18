# BigQuery CDC + MERGE DML Compatibility Research

> **Date**: 2026-03-18
> **Status**: RESEARCH COMPLETE
> **Verdict**: MERGE DML on CDC tables is **NOT SUPPORTED** by BigQuery. Must use alternatives.

---

## TL;DR

**BigQuery CDC-enabled tables explicitly prohibit mutating DML statements (MERGE, UPDATE, DELETE).** This is a hard architectural constraint, not a concurrency issue. If you need to enrich data in a CDC table, you must use one of the alternative patterns described below.

---

## 1. The Hard Constraint: CDC Tables Cannot Run MERGE

### What Google Documentation Says

From the [BigQuery CDC documentation](https://docs.cloud.google.com/bigquery/docs/change-data-capture), the **Limitations** section explicitly states that CDC-enabled tables **do not support**:

- **Mutating DML statements** such as `DELETE`, `UPDATE`, and `MERGE`
- Wildcard table queries
- Search indexes
- During runtime merge jobs: table copy, clone, snapshot, Storage Read API, `requirePartitionFilter`

### Why This Matters for Our Use Case

Our tables use:
- Storage Write API in CDC mode (`_CHANGE_TYPE` = UPSERT/DELETE)
- `max_staleness` set to 5 minutes
- Primary Key (NOT ENFORCED)

**All data modifications on a CDC table MUST flow through the Storage Write API using `_CHANGE_TYPE`.** There is no way to run a `MERGE` statement against these tables, period.

### What Happens If You Try

BigQuery will reject the DML statement with an error. The table is flagged as CDC-enabled while the Storage Write API is actively streaming row modifications to it.

---

## 2. CDC Internals: How It Actually Works

### Change Buffer Architecture

```
Storage Write API (CDC) ──> Change Buffer (unapplied rows)
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
            Background Apply Job              Runtime Merge Job
            (within max_staleness)         (query outside window)
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                              Base Table
```

### Background Apply Jobs
- Run at intervals defined by `max_staleness`
- Executed by `bigquery-adminbot@system.gserviceaccount.com`
- Use `BACKGROUND` or `BACKGROUND_CHANGE_DATA_CAPTURE` reservation assignment types
- Apply accumulated UPSERT/DELETE operations from the change buffer to the base table
- Tracked by `upsert_stream_apply_watermark` timestamp

### Runtime Merge Jobs
- Triggered when a query runs **outside** the `max_staleness` window
- BigQuery applies all pending row modifications on-the-fly during query execution
- More expensive and slower than background apply jobs
- Use `QUERY` reservation assignment type

### max_staleness Behavior
- `max_staleness = '0:5:0' HOUR TO SECOND` (5 min): data can be up to 5 min stale when queried
- `max_staleness = 0`: every query triggers runtime merge (expensive)
- Higher values = fewer background jobs = lower cost, but staler reads

### _CHANGE_SEQUENCE_NUMBER
- Optional STRING field in hexadecimal format (e.g., `'18F2EBB6480'`)
- Up to 4 sections separated by `/`
- BigQuery retains the record with the **higher** sequence number regardless of insertion order
- Critical for pipelines without guaranteed ordering (like Apache Beam)

---

## 3. Why MERGE Would Conflict Even If It Were Allowed

Even hypothetically, running MERGE on a CDC table would create race conditions:

### Race Condition Scenario
```
T1: CDC UPSERT row A (version 1) → enters change buffer
T2: MERGE enriches row A with lookup data → writes directly to base table
T3: Background apply job runs → applies version 1 from change buffer
    → OVERWRITES T2's enrichment (lost update!)
T4: CDC UPSERT row A (version 2) → enters change buffer
T5: Background apply → applies version 2, no enrichment
```

### The Fundamental Problem
CDC's change buffer is **append-only with sequence ordering**. DML writes to the base table directly. When the change buffer is flushed, it would overwrite DML changes because it uses primary-key-based UPSERT semantics with sequence numbers.

---

## 4. BigQuery DML Concurrency Model (for NON-CDC tables)

For reference, here's how DML concurrency works on **regular** (non-CDC) tables:

### Concurrency Limits
| Operation | Concurrent | Queue Size |
|-----------|-----------|------------|
| Mutating DML (UPDATE/DELETE/MERGE) | 2 | 20 |
| INSERT DML | 1,500 (first batch), then 10 | 100 |

### Conflict Detection
- Conflicts occur when concurrent mutating statements **touch the same partition**
- BigQuery retries failed statements up to 3 times automatically
- MERGE that **only inserts** rows does NOT conflict with other DML
- MERGE that updates/deletes rows CAN conflict with concurrent mutating DML

### Storage Write API + DML (non-CDC)
- Rows written via Storage Write API **can** be modified by DML within 30 minutes
- This applies to **non-CDC** Storage Write API usage (no `_CHANGE_TYPE`)
- Legacy `tabledata.insertAll` rows in streaming buffer CANNOT be modified by DML

---

## 5. Alternatives for Enriching CDC Table Data

### Option A: BQ View with JOIN (RECOMMENDED - Simplest)

```sql
CREATE OR REPLACE VIEW `project.dataset.enriched_member_tier` AS
SELECT
  t.*,
  l.tier_name,
  l.tier_benefits,
  l.tier_level
FROM `project.dataset.member_tier` t
LEFT JOIN `project.dataset.tier_lookup` l
  ON t.tierCode = l.tierCode;
```

**Pros:**
- Zero writes, zero conflicts
- Always up-to-date (reads from CDC table + lookup at query time)
- No additional cost beyond query compute
- Works with CDC tables (read-only operation)

**Cons:**
- JOIN cost on every query
- Not materialized (can't be indexed separately)
- Consumers must query the view, not the base table

### Option B: Separate Enriched Table via Scheduled Query

```sql
-- Runs every 5 minutes via Cloud Scheduler / Scheduled Query
CREATE OR REPLACE TABLE `project.dataset.enriched_member_tier`
PARTITION BY ingestedTHDate
AS
SELECT
  t.*,
  l.tier_name,
  l.tier_benefits
FROM `project.dataset.member_tier` t
LEFT JOIN `project.dataset.tier_lookup` l
  ON t.tierCode = l.tierCode;
```

**Pros:**
- Enriched table is a regular table (supports DML, indexes, etc.)
- Pre-computed JOIN (fast reads)
- Decoupled from CDC pipeline

**Cons:**
- Data staleness (up to 5 min from CDC + scheduled query interval)
- Full table rebuild each time (or incremental with watermark)
- Additional storage + compute cost

### Option C: Enrich in Dataflow BEFORE Writing to BQ (RECOMMENDED - Best)

```python
# In Dataflow pipeline, enrich before CDC write
enriched = (
    raw_events
    | 'EnrichWithLookup' >> beam.ParDo(EnrichWithLookupDoFn(lookup_side_input))
    | 'WriteToBQ' >> BigQueryIO.write(method='STORAGE_WRITE_API', ...)
)
```

**Pros:**
- Data arrives enriched, no post-processing needed
- Single write path, no race conditions
- Works with CDC tables (enrichment happens before write)
- Lookup can be side input, BQ read, or API call

**Cons:**
- Increases Dataflow pipeline complexity
- Lookup data must be available at processing time
- Side inputs may become stale (need periodic refresh)

### Option D: Write Enrichment as CDC UPSERT via Storage Write API

Instead of MERGE, send enriched rows back through the Storage Write API with `_CHANGE_TYPE = UPSERT`:

```python
# Separate "enrichment" pipeline
rows_to_enrich = bq_client.query("SELECT * FROM member_tier WHERE needs_enrichment")
for row in rows_to_enrich:
    enriched = enrich(row, lookup_data)
    storage_write_api.append_rows(
        enriched,
        _CHANGE_TYPE='UPSERT',
        _CHANGE_SEQUENCE_NUMBER=new_sequence_number  # Must be higher!
    )
```

**Pros:**
- Uses the same CDC mechanism (no DML needed)
- Respects `_CHANGE_SEQUENCE_NUMBER` ordering
- Works with CDC tables natively

**Cons:**
- Must ensure `_CHANGE_SEQUENCE_NUMBER` is higher than the original write
- Risk of overwriting newer CDC updates if sequence management is wrong
- More complex than view-based approach
- Essentially doubles write volume

### Option E: Materialized View (LIMITED SUPPORT)

```sql
CREATE MATERIALIZED VIEW `project.dataset.mv_enriched_member_tier`
OPTIONS (max_staleness = INTERVAL '10' MINUTE)
AS
SELECT t.*, l.tier_name
FROM `project.dataset.member_tier` t
JOIN `project.dataset.tier_lookup` l ON t.tierCode = l.tierCode;
```

**Limitations:**
- Any deletion in CDC base table triggers **full refresh** of materialized view
- No support for window functions (ROW_NUMBER, etc.)
- JOINs cause full refresh instead of incremental updates when right-side table changes
- Limited to 20 materialized views per base table per dataset

### Option F: Continuous Query (NOT VIABLE)

BigQuery continuous queries:
- Do NOT support JOINs (stateful operations)
- Do NOT support CDC upsert data processing
- Only support stateless transformations and ML functions

**Not suitable for enrichment with lookup tables.**

### Option B2: PeriodicImpulse → Separate Enriched Table (Best for sales-collector)

Variant ของ Option B — ใช้ Dataflow `PeriodicImpulse` เป็น trigger แทน Cloud Scheduler:

```python
# In sales-collector pipeline (main.py)
ENRICHMENT_SQL = """
INSERT INTO `{project}.public.sales_receipt_full`
SELECT
  r.*,
  lb.branch_name,
  lp.product_category,
  lm.member_segment,
  lt.tender_desc,
  lc.channel_name
FROM `{project}.refined.sales_receipt` r
LEFT JOIN `{project}.refined.lookup_branch` lb
  ON r.partner_code = lb.partner_code AND r.branch_code = lb.branch_code
LEFT JOIN `{project}.refined.lookup_product` lp
  ON r.partner_code = lp.partner_code
LEFT JOIN `{project}.refined.lookup_member` lm
  ON r.member_id = lm.member_id
LEFT JOIN `{project}.refined.lookup_tender` lt
  ON r.payment_type = lt.tender_type
LEFT JOIN `{project}.refined.lookup_channel` lc
  ON r.transaction_channel_id = lc.channel_id
WHERE r.transaction_date >= DATETIME_SUB(CURRENT_DATETIME("Asia/Bangkok"), INTERVAL 10 MINUTE)
"""

def _run_enrichment_query(timestamp_element, project):
    from google.cloud import bigquery
    client = bigquery.Client(project=project)
    job = client.query(ENRICHMENT_SQL.format(project=project))
    job.result()
    logging.info("Enrichment done: %s rows", job.num_dml_affected_rows)

# Add as branch in existing pipeline
_ = (
    p
    | "EnrichTrigger" >> PeriodicImpulse(fire_interval=300)
    | "RunEnrichment" >> beam.Map(_run_enrichment_query, project=project)
)
```

**Table architecture:**
```
refined.sales_receipt         ← CDC streaming (Kafka fields only)
refined.sales_sku             ← CDC streaming
refined.sales_tender          ← CDC streaming
  ↓ (PeriodicImpulse trigger every 5 min)
public.sales_receipt_full     ← non-CDC table (enriched, JOINed with 5 lookups)
public.sales_sku_full         ← non-CDC table
public.sales_tender_full      ← non-CDC table
```

**Pros:**
- Control flow ที่ Dataflow ที่เดียว (ไม่ต้อง Cloud Scheduler)
- `public.*` tables เป็น non-CDC → MERGE/INSERT/UPDATE ได้หมด
- BQ engine ทำ JOIN (ไม่ load data เข้า pipeline memory)
- Pipeline ตาย = enrichment หยุด (ถูกต้อง — ไม่มี data ใหม่ให้ enrich)
- Consumer อ่านจาก `public.*` ได้เร็ว (pre-computed)

**Cons:**
- Storage cost เพิ่ม (duplicate data ใน public tables)
- Latency 5-10 นาที (CDC max_staleness 5 min + enrichment interval 5 min)
- ต้อง manage 2 ชุด tables (refined + public)

**Cost estimate:**
```
BQ INSERT query (every 5 min, partition pruning):
  ~500 MB scan × 12/hr × 24hr = ~144 GB/day
  On-demand: 144 GB × $6.25/TB = ~$0.90/day = ~$27/month
Storage: ~3 tables × ~50 GB = ~$3/month
Total: ~$30/month
```

**Key considerations:**
- `public.*` ใช้ partition by `transaction_date` + clustering เดียวกัน
- INSERT OVERWRITE partition สำหรับ incremental (ไม่ต้อง full table rebuild)
- หรือใช้ MERGE on `public.*` (non-CDC → MERGE ได้) สำหรับ dedup

---

## Notes: Sales-Collector Specific Context

### Current Source Table Architecture
Source Iceberg table เก็บ **full Kafka message** ใน column เดียว:
```
source.sales_created:
  - data          (STRING)  ← ทั้ง JSON: {eventId, source, eventName, timestamp, payload: {...}}
  - ingested_date (INT64)   ← YYYYMMDD Bangkok time
  - ingested_at   (STRING)  ← ISO timestamp
```

### Data Volume
- 10K-100K messages/sec
- ~15M rows × 10 cols per lookup table × 5 tables = 75M lookup rows

### Current Enrichment (Small Tables)
MasterCache (BQ → Python dict, ~1K-10K rows) works for sales_channel 6-level priority chain.
This is for **large table** enrichment (15M+ rows) that cannot fit in memory.

### Recommended Approach for Sales-Collector

```
Streaming pipeline (existing):
  Kafka → Iceberg source (raw) → refined CDC tables (extracted fields + small enrichment)

Enrichment branch (new, in same pipeline):
  PeriodicImpulse (5 min) → BQ query → public non-CDC tables (refined + large table JOINs)

Consumers read from:
  public.sales_receipt_full (enriched, fast, non-CDC, supports DML)
```

---

## 6. Recommendation Matrix

| Criteria | View (A) | Separate Table (B) | Dataflow Enrich (C) | CDC UPSERT (D) |
|----------|----------|-------------------|---------------------|-----------------|
| Complexity | Low | Medium | Medium-High | High |
| Data freshness | Real-time | Periodic | Real-time | Near-real-time |
| Read performance | Medium | High | High | High |
| Write conflicts | None | None | None | Sequence risk |
| Additional cost | Query-time | Storage + compute | Dataflow compute | Write volume |
| Works with CDC | Yes | Yes | Yes | Yes |

### Our Recommendation

**For the loyalty data platform:**

1. **Best overall**: **Option C** (Enrich in Dataflow) -- if enrichment data is available at processing time. This is what Google recommends for CDC + ETL workloads.

2. **Simplest to implement now**: **Option A** (BQ View) -- zero code changes to the pipeline, just create a view. Consumers query the view instead of the base table.

3. **Best for heavy read workloads**: **Option B** (Separate enriched table) -- pre-computed, fast reads, but adds scheduled query management.

---

## 7. Summary of Key Facts

| Question | Answer |
|----------|--------|
| Can you run MERGE on a CDC table? | **NO** -- explicitly prohibited |
| Can you run UPDATE on a CDC table? | **NO** |
| Can you run DELETE on a CDC table? | **NO** (must use `_CHANGE_TYPE = DELETE` via Storage Write API) |
| Does CDC lock the table? | No locks -- uses change buffer + background apply |
| How many concurrent DML on non-CDC? | 2 concurrent + 20 queued (mutating DML) |
| Does max_staleness affect DML? | N/A -- DML is prohibited on CDC tables |
| Can Storage Write API rows be modified by DML? | Yes, on NON-CDC tables within 30 min |
| Materialized views on CDC tables? | Limited -- deletions trigger full refresh |
| Continuous queries on CDC? | Not supported |

---

## Sources

- [BigQuery CDC Documentation](https://docs.cloud.google.com/bigquery/docs/change-data-capture)
- [BigQuery DML Documentation](https://docs.cloud.google.com/bigquery/docs/data-manipulation-language)
- [BigQuery Storage Write API Documentation](https://docs.cloud.google.com/bigquery/docs/write-api)
- [BigQuery CDC Blog Post](https://cloud.google.com/blog/products/data-analytics/bigquery-gains-change-data-capture-functionality)
- [Using BigQuery CDC in Dataflow](https://cloud.google.com/blog/products/data-analytics/using-bigquerys-new-cdc-capability-in-dataflow/)
- [BigQuery DML Without Limits](https://cloud.google.com/blog/products/data-analytics/dml-without-limits-now-in-bigquery)
- [BigQuery Quotas and Limits](https://docs.cloud.google.com/bigquery/quotas)
- [BigQuery Continuous Queries](https://docs.cloud.google.com/bigquery/docs/continuous-queries-introduction)
- [BigQuery Materialized Views](https://docs.cloud.google.com/bigquery/docs/materialized-views-use)
- [BigQuery CDC with PubSub Workaround](https://medium.com/google-cloud/bigquery-cdc-with-pubsub-overcoming-limitations-ceae431acfec)
- [BigQuery Storage Write API Best Practices](https://docs.cloud.google.com/bigquery/docs/write-api-best-practices)
- [Datastream CDC Best Practices](https://docs.cloud.google.com/datastream/docs/best-practices-cdc-existing-table)
