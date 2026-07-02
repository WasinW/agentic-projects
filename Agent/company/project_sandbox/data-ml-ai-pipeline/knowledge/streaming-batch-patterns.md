# Streaming & Batch Patterns (Spark / Databricks)

> PRIMARY reference — the load-bearing doc for AIA. Spark Structured Streaming + batch patterns on Delta Lake, grounded in the real Kafka(MSK) → Raw → Persist → Curated pipeline. Covers the write patterns, the 14 streaming concerns, checkpoint/trigger/watermark/idempotency discipline, DLQ, monitoring, and deployment on Databricks Workflows + Airflow.

Layer naming: **Raw = Bronze, Persist = Silver, Curated = Gold.** The scripts use Raw/Persist/Curated as physical table tiers.

---

## 1. The three pipeline stages

```
Kafka topic (MSK)
   │
   ├─[1: Consumer]──► RAW   (bronze, append-only, ALL STRING, no parsing)
   │                   │
   ├─[2: Transform]──► PERSIST (silver, append-only, TYPED per data contract; bad rows → DLQ)
   │                   │
   └─[3: Transform]──► CURATED (gold, UPSERT via MERGE, business logic, current state)
```

| Aspect | 1: Kafka→Raw | 2: Raw→Persist | 3: Persist→Curated |
|---|---|---|---|
| Pattern | Append-only write | Append-only write | foreachBatch + MERGE |
| Source | Kafka topic | Delta (raw) | Delta (persist) |
| Target | Delta append | Delta append + DLQ | Delta upsert |
| Schema | all STRING | typed per contract | business-ready |
| Transform | metadata only | parse + type-cast | business logic + agg |
| Idempotency | Kafka offset (checkpoint) | kafka_offset preserved | `update_date` guard |
| Error handling | trust Kafka | DLQ table | business validation |
| Trigger | 30 s | 1 min | 30 s |
| Watermark | no | no | yes (1 h) |
| Stateful | no | no | implicit via MERGE |

Design principle running through all three: **push typing and business logic downstream, keep Bronze dumb and replayable.** Schema drift can't break a layer that doesn't parse.

---

## 2. The 14 streaming concerns (the checklist)

The scripts annotate "Concern N" inline but never list them in one place. Consolidated:

| # | Concern | Rule |
|---|---|---|
| 1 | **Idempotency** | Every batch safe to re-run. Use a guard (`t.update_date < s.etl_date`) on MERGE and/or Delta `txnAppId`+`txnVersion` on append. |
| 2 | **MERGE only in foreachBatch** | Do the upsert as a single SQL `MERGE`; avoid DataFrame actions (`.count()`, `.collect()`) that trigger extra jobs inside the batch. |
| 3 | **Trigger discipline** | Use `processingTime` micro-batch (or `availableNow` for backfill). Avoid `continuous` (immature) unless truly needed. |
| 4 | **Partition pruning in ON** | MERGE `ON` clause must constrain the target partition column (e.g. `t.region IN (SELECT DISTINCT region FROM source_batch)`) or it full-scans the target. |
| 5 | **Empty-batch check** | `if batch_df.isEmpty(): return` — skip no-op batches, avoid empty writes/commits. |
| 6 | **Source dedupe** | Dedupe within the batch before MERGE (`ROW_NUMBER() OVER (PARTITION BY key ORDER BY etl_date DESC) = 1`). MERGE errors on duplicate source keys. |
| 7 | **One writer per target** | Exactly one streaming query writes to a given table. Need another writer → separate pipeline from a different source. Prevents checkpoint/commit conflicts. |
| 8 | **Watermark for late data** | Required for stateful ops (windowed agg, stream-stream join). For stateless it documents late-data tolerance. |
| 9 | **Explicit columns** | No `SELECT *`, no `INSERT *`. List columns — schema-change safety + cost. |
| 10 | **Checkpoint discipline** | Versioned + namespaced path: `s3://aia-checkpoints/prod/{pipeline}_{version}/`. Bump version on schema change; never share a checkpoint across pipelines. |
| 11 | **Schema enforcement** | Parse against an explicit contract schema; route failures to DLQ rather than failing the stream. |
| 12 | **Monitoring** | `StreamingQueryListener` per query: log batchId/rows/rate/duration; alert on lag + slow batch. |
| 13 | **Rate limiting** | Bound batch size: `maxOffsetsPerTrigger` (Kafka), `maxFilesPerTrigger` / `maxBytesPerTrigger` (Delta). Prevents one giant catch-up batch. |
| 14 | **Late-data / replay handling** | Combined with #1 and #8: idempotency guard + watermark make replays and out-of-order arrivals safe. |

Use this as a PR review checklist for any streaming job.

---

## 3. Script 1 — Kafka(MSK) → Raw (append-only, all STRING)

Pattern: direct streaming write, no parsing. Idempotency from Kafka offsets tracked in the checkpoint.

```python
PIPELINE_NAME    = "kafka_to_raw_transactions"
PIPELINE_VERSION = "v1"
KAFKA_BROKERS    = "msk-broker-1:9092,msk-broker-2:9092,msk-broker-3:9092"
KAFKA_TOPIC      = "transactions"
CONSUMER_GROUP   = "aia-de-transactions-raw"
TARGET_TABLE     = "bronze.transactions_raw"
CHECKPOINT_LOC   = f"s3://aia-checkpoints/prod/{PIPELINE_NAME}_{PIPELINE_VERSION}/"
TRIGGER_INTERVAL = "30 seconds"
MAX_OFFSETS_PER_TRIGGER = "100000"

def write_to_raw(batch_df, batch_id):
    if batch_df.isEmpty():                                  # Concern 5
        return
    final_df = (batch_df
        .withColumn("ingested_at", current_timestamp())
        .withColumn("ingestion_date", current_timestamp().cast("date"))
        .withColumn("batch_id", lit(batch_id).cast("long"))
        .withColumn("consumer_group", lit(CONSUMER_GROUP))
        .select(                                            # Concern 9: explicit cols
            col("topic").alias("kafka_topic"),
            col("partition").alias("kafka_partition"),
            col("offset").alias("kafka_offset"),
            col("timestamp").alias("kafka_timestamp"),
            col("timestampType").alias("kafka_timestamp_type"),
            col("key").cast("string").alias("kafka_key"),
            col("value").cast("string").alias("message_value"),   # raw JSON, no parse
            col("headers").cast("string").alias("message_headers"),
            "ingested_at", "ingestion_date", "batch_id", "consumer_group",
        ))
    (final_df.write.format("delta").mode("append")
        .option("txnAppId", PIPELINE_NAME)                  # Concern 1: idempotent append
        .option("txnVersion", batch_id)
        .saveAsTable(TARGET_TABLE))

def run_kafka_consumer():
    kafka_df = (spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BROKERS)
        .option("subscribe", KAFKA_TOPIC)
        .option("kafka.group.id", CONSUMER_GROUP)
        .option("startingOffsets", "latest")                # "earliest" for backfill
        .option("maxOffsetsPerTrigger", MAX_OFFSETS_PER_TRIGGER)   # Concern 13
        .option("failOnDataLoss", "false")
        # MSK IAM auth (uncomment for AIA MSK):
        # .option("kafka.security.protocol", "SASL_SSL")
        # .option("kafka.sasl.mechanism", "AWS_MSK_IAM")
        # .option("kafka.sasl.jaas.config",
        #         "software.amazon.msk.auth.iam.IAMLoginModule required;")
        # .option("kafka.sasl.client.callback.handler.class",
        #         "software.amazon.msk.auth.iam.IAMClientCallbackHandler")
        .load())
    return (kafka_df.writeStream
        .queryName(PIPELINE_NAME)
        .foreachBatch(write_to_raw)
        .option("checkpointLocation", CHECKPOINT_LOC)       # Concern 10
        .trigger(processingTime=TRIGGER_INTERVAL)           # Concern 3
        .start())
```

Target table DDL (run once):

```sql
CREATE TABLE bronze.transactions_raw (
    kafka_topic STRING, kafka_partition INT, kafka_offset LONG,
    kafka_timestamp TIMESTAMP, kafka_timestamp_type INT, kafka_key STRING,
    message_value STRING,          -- all raw, no parsing
    message_headers STRING,
    ingested_at TIMESTAMP, ingestion_date DATE, batch_id LONG, consumer_group STRING
) USING DELTA
PARTITIONED BY (ingestion_date)
TBLPROPERTIES (
    delta.autoOptimize.optimizeWrite = true,
    delta.autoOptimize.autoCompact   = true,
    delta.enableChangeDataFeed       = true     -- lets Script 2 read as a stream
);
```

**Databricks note:** the same shape works for file sources via **Auto Loader** (`cloudFiles`) instead of Kafka — swap `.format("kafka")` for `.format("cloudFiles")` with `cloudFiles.format`/`schemaLocation`; the append + checkpoint + idempotency discipline is identical.

---

## 4. Script 2 — Raw → Persist (typed per data contract, DLQ for bad rows)

Reads Bronze as a Delta stream, parses against an explicit contract schema, splits good/bad, writes good → Persist and bad → DLQ. Never fails the stream on bad data (Concern 11).

```python
SOURCE_TABLE = "bronze.transactions_raw"
TARGET_TABLE = "silver.transactions_persist"
DLQ_TABLE    = "silver.transactions_dlq"

# Data contract — document + version in the wiki
TRANSACTION_SCHEMA = StructType([
    StructField("transaction_id",   StringType(),       False),
    StructField("account_id",       StringType(),       False),
    StructField("region",           StringType(),       False),
    StructField("transaction_type", StringType(),       False),
    StructField("amount",           DecimalType(18, 2), False),
    StructField("currency",         StringType(),       False),
    StructField("transaction_time", StringType(),       False),   # ISO string, cast later
    StructField("merchant_id",      StringType(),       True),
    StructField("metadata",         StringType(),       True),
])

def parse_and_persist(batch_df, batch_id):
    if batch_df.isEmpty():
        return
    batch_df.createOrReplaceTempView("raw_batch")
    spark.sql(f"""
        SELECT from_json(message_value, '{TRANSACTION_SCHEMA.simpleString()}') AS parsed,
               kafka_partition, kafka_offset, kafka_timestamp, message_value,
               current_timestamp() AS etl_date, {batch_id}L AS etl_batch_id
        FROM raw_batch
    """).createOrReplaceTempView("parsed_batch")

    good_df = spark.sql("""
        SELECT parsed.transaction_id, parsed.account_id, parsed.region,
               parsed.transaction_type, parsed.amount, parsed.currency,
               CAST(parsed.transaction_time AS TIMESTAMP) AS transaction_time,
               parsed.merchant_id, parsed.metadata,
               kafka_partition, kafka_offset, kafka_timestamp,
               etl_date, etl_batch_id,
               CAST(parsed.transaction_time AS DATE) AS business_date
        FROM parsed_batch
        WHERE parsed IS NOT NULL AND parsed.transaction_id IS NOT NULL
          AND parsed.account_id IS NOT NULL AND parsed.amount IS NOT NULL
          AND parsed.transaction_time IS NOT NULL
    """)
    bad_df = spark.sql("""
        SELECT kafka_partition, kafka_offset, message_value,
               CASE WHEN parsed IS NULL THEN 'JSON_PARSE_FAILED'
                    WHEN parsed.transaction_id IS NULL THEN 'MISSING_TRANSACTION_ID'
                    WHEN parsed.account_id IS NULL THEN 'MISSING_ACCOUNT_ID'
                    WHEN parsed.amount IS NULL THEN 'MISSING_AMOUNT'
                    WHEN parsed.transaction_time IS NULL THEN 'MISSING_TRANSACTION_TIME'
                    ELSE 'UNKNOWN' END AS error_reason,
               CAST(parsed AS STRING) AS error_detail,
               current_timestamp() AS dlq_at, etl_batch_id
        FROM parsed_batch
        WHERE parsed IS NULL OR parsed.transaction_id IS NULL
           OR parsed.account_id IS NULL OR parsed.amount IS NULL
           OR parsed.transaction_time IS NULL
    """)

    if not good_df.isEmpty():
        (good_df.write.format("delta").mode("append")
            .option("txnAppId", f"{PIPELINE_NAME}_good").option("txnVersion", batch_id)
            .saveAsTable(TARGET_TABLE))
    if not bad_df.isEmpty():
        (bad_df.write.format("delta").mode("append")
            .option("txnAppId", f"{PIPELINE_NAME}_dlq").option("txnVersion", batch_id)
            .saveAsTable(DLQ_TABLE))

source = (spark.readStream.format("delta")
    .option("skipChangeCommits", "true")      # raw is append-only; ignore any non-append
    .option("maxFilesPerTrigger", "100").option("maxBytesPerTrigger", "1g")   # Concern 13
    .table(SOURCE_TABLE))
# No watermark — append-only, no stateful ops
```

DLQ table is reprocessed on a separate daily Airflow/Workflows job (fix → re-insert). Persist is partitioned by `business_date`.

---

## 5. Script 3 — Persist → Curated (business logic + idempotent MERGE)

Pattern 3: `foreachBatch` + SQL `MERGE`. This is where all 14 concerns land. Watermark bounds late data.

```python
SOURCE_TABLE  = "silver.transactions_persist"
TARGET_TABLE  = "gold.account_balance"
WATERMARK_COL, WATERMARK_DELAY = "etl_date", "1 hour"

def merge_to_curated(batch_df, batch_id):
    if batch_df.isEmpty():                     # Concern 5
        return
    batch_df.createOrReplaceTempView("persist_batch")
    spark.sql(f"""
        MERGE INTO {TARGET_TABLE} t
        USING (
            SELECT account_id, region,                                  -- Concern 6: dedupe/agg
                   SUM(CASE WHEN transaction_type='CREDIT' THEN amount
                            WHEN transaction_type='DEBIT'  THEN -amount
                            ELSE 0 END) AS net_delta,
                   COUNT(*) AS txn_count_delta,
                   FIRST_VALUE(transaction_id)   OVER w AS last_transaction_id,
                   FIRST_VALUE(transaction_time) OVER w AS last_transaction_time,
                   MAX(etl_date) AS max_etl_date
            FROM persist_batch
            WINDOW w AS (PARTITION BY account_id ORDER BY transaction_time DESC
                         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
            GROUP BY account_id, region, transaction_id, transaction_time
        ) s
        ON  t.account_id = s.account_id
            AND t.region IN (SELECT DISTINCT region FROM persist_batch)   -- Concern 4: prune
            AND t.update_date < s.max_etl_date                            -- Concern 1+8: guard
        WHEN MATCHED THEN UPDATE SET                                      -- Concern 9: explicit
            t.current_balance       = t.current_balance + s.net_delta,
            t.last_transaction_id   = s.last_transaction_id,
            t.last_transaction_time = s.last_transaction_time,
            t.transaction_count     = t.transaction_count + s.txn_count_delta,
            t.account_status        = CASE
                WHEN t.current_balance + s.net_delta < 0 THEN 'OVERDRAWN'
                WHEN s.max_etl_date > t.update_date      THEN 'ACTIVE'
                ELSE t.account_status END,
            t.update_date     = s.max_etl_date,
            t.update_batch_id = {batch_id}L
        WHEN NOT MATCHED THEN INSERT
            (account_id, region, current_balance, last_transaction_id,
             last_transaction_time, transaction_count, account_status,
             update_date, update_batch_id)
            VALUES (s.account_id, s.region, s.net_delta, s.last_transaction_id,
                    s.last_transaction_time, s.txn_count_delta, 'ACTIVE',
                    s.max_etl_date, {batch_id}L)
    """)

source = (spark.readStream.format("delta")
    .option("skipChangeCommits", "true")
    .option("maxFilesPerTrigger", "200").option("maxBytesPerTrigger", "1g")
    .table(SOURCE_TABLE))
watermarked = source.withWatermark(WATERMARK_COL, WATERMARK_DELAY)        # Concern 8
query = (watermarked.writeStream
    .queryName(PIPELINE_NAME)
    .foreachBatch(merge_to_curated)                                       # Concern 7: sole writer
    .option("checkpointLocation", CHECKPOINT_LOC)                         # Concern 10
    .trigger(processingTime="30 seconds")                                 # Concern 3
    .start())
```

Curated DDL highlights: `PARTITIONED BY (region) CLUSTER BY (account_id)`, autoOptimize on, CDF on. The `update_date` column is the idempotency guard — never drop it.

> ⚠️ **Correctness flag (from the raw notes):** the MERGE source aggregates with `GROUP BY account_id, region, transaction_id, transaction_time` *and* uses `SUM(...) net_delta`. Grouping by `transaction_id` makes each group a single transaction, so `net_delta` and `txn_count_delta` are per-transaction, not per-account — yet the `MERGE ON` is only `account_id`, which will error if a batch has multiple transactions for one account (duplicate source keys). To get true per-account net delta, group by `account_id, region` only and pick the latest transaction via a window. Validate/fix before using in production. The simpler `streaming_template.py` (single MERGE, `ROW_NUMBER()=1` dedupe per key) is the cleaner reference for the pattern.

---

## 6. Streaming discipline — the rules distilled

**Checkpoint:** `s3://aia-checkpoints/prod/{pipeline}_{version}/`. One per query. Bump `{version}` on any schema/state change (a new version = fresh checkpoint = controlled reprocess). Never point two queries at the same checkpoint.

**Trigger:** `processingTime="30s"/"1min"` for steady streaming; `availableNow=True` for backfills/scheduled catch-up (processes all available data then stops — ideal for an Airflow-triggered batch run over a streaming source). Avoid `continuous`.

**Watermark:** mandatory for stateful ops (windowed agg, stream-stream join, `dropDuplicates` with time). For stateless MERGE it documents and bounds late-data tolerance and lets the guard reject stale updates.

**Idempotency:** two mechanisms — (a) Delta `txnAppId`+`txnVersion` on append writes makes a re-run a no-op; (b) `t.update_date < s.event_date` guard on MERGE rejects stale/duplicate updates. Use the matching one per pattern.

**Rate limiting:** always set — `maxOffsetsPerTrigger` (Kafka), `maxFilesPerTrigger`/`maxBytesPerTrigger` (Delta). Without it a restart after downtime creates one massive batch that blows memory/SLA.

**Source change handling:** reading a Delta source that only appends → `skipChangeCommits=true`. (Older `ignoreChanges` is messier — prefer `skipChangeCommits`.)

**No DataFrame actions inside foreachBatch** beyond the unavoidable `isEmpty()` check — do the work in one SQL statement. Each `.count()`/`.collect()` is an extra Spark job per micro-batch.

---

## 7. Monitoring — StreamingQueryListener

One listener per query; log progress, alert on lag and slow batches. Wire `send_to_*` to CloudWatch/Datadog and `alert_*` to PagerDuty/Slack.

```python
class StreamingMonitor(StreamingQueryListener):
    def onQueryStarted(self, e):
        logging.info(f"[{PIPELINE_NAME}] started id={e.id}")
    def onQueryProgress(self, e):
        p = e.progress
        m = {"batch_id": p.batchId, "input_rows": p.numInputRows,
             "input_rate": p.inputRowsPerSecond or 0,
             "process_rate": p.processedRowsPerSecond or 0,
             "trigger_ms": p.durationMs.get("triggerExecution", 0)}
        logging.info(f"[{PIPELINE_NAME}] {m}")
        if m["input_rate"] > m["process_rate"] * 1.5 + 100:        # lag
            logging.warning(f"[{PIPELINE_NAME}] LAG {m}")          # alert_pagerduty(...)
        if m["trigger_ms"] > 60_000:                               # slow batch
            logging.warning(f"[{PIPELINE_NAME}] SLOW {m['trigger_ms']}ms")
    def onQueryTerminated(self, e):
        if e.exception:
            logging.error(f"[{PIPELINE_NAME}] FAILED {e.exception}")   # alert critical
spark.streams.addListener(StreamingMonitor())
```

Also useful: after a MERGE, read `DESCRIBE HISTORY <table> LIMIT 1` → `operationMetrics` for `numTargetRowsUpdated` / `numTargetRowsInserted` to log write volumes.

---

## 8. Deployment (Databricks Workflows + Airflow/MWAA)

```
Job: Stream Layer (continuous)        Job: Maintenance (weekly)     Job: DLQ Reprocess (daily)
  ├─ Script 1  Kafka→Raw                OPTIMIZE + VACUUM             read DLQ → fix → re-insert
  ├─ Script 2  Raw→Persist              + ANALYZE
  └─ Script 3  Persist→Curated
```

- Each streaming script runs as a continuous task on a Databricks Workflow. **Do not** call `query.awaitTermination()` in a Databricks Job — the Jobs service owns the lifecycle (only use it for notebook testing).
- **Maintenance** (`OPTIMIZE`/`VACUUM`/`ANALYZE`) and **DLQ reprocess** run on schedules. At AIA these schedules are natural **Airflow/MWAA** DAGs that trigger Databricks Jobs (or run as Databricks scheduled Workflows) — keep orchestration in Airflow, keep the heavy Spark in Databricks.
- For pure-batch equivalents of the same logic, reuse Script 3's `merge_to_curated` body in a batch job and feed it a bounded read, or run the streaming job with `.trigger(availableNow=True)` on a schedule.

---

## 9. Test plan for any pipeline change

1. **Unit:** parse/transform functions on sample good + malformed records (assert good count, DLQ reasons).
2. **Idempotency:** run the same batch twice → target unchanged (guard / txnVersion working).
3. **DQ gates:** row counts, null checks on NOT-NULL contract fields, value ranges (Great Expectations / Soda) before promoting Persist→Curated.
4. **Replay:** point checkpoint to a fresh version, reprocess from `earliest`, compare aggregates to baseline.
5. **Late data:** inject an event older than the watermark → confirm it's bounded/rejected as expected.
6. **Schema drift:** add an unexpected field to source JSON → Raw unaffected, Persist routes to DLQ, no stream failure.
7. **Monitoring:** force a slow/large batch → confirm lag + slow-batch alerts fire.
