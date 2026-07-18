---
name: databricks-streaming-pattern
description: STARTER (refine after AIA requirements). Spark Structured Streaming on Databricks + Delta — choosing Auto Loader vs Kafka source, checkpoint namespacing, trigger modes (availableNow vs processingTime), watermark + stateful ops, and idempotent / exactly-once writes to Delta via foreachBatch + MERGE. Use when building or reviewing a streaming/micro-batch pipeline on Databricks, debugging duplicate or lost records, deciding a trigger mode, designing checkpoints, or handling schema evolution + a DLQ. For raw Spark job tuning (shuffle, skew, AQE, partition sizing) defer to the existing `spark-tune` skill — this one owns the streaming + Delta-write correctness layer, not executor tuning.
---

# databricks-streaming-pattern

> **STARTER scaffold — refine after AIA requirements are gathered.** Code is grounded in
> Wasin's production streaming templates (`knowledge_chat/streaming_template.py`,
> `example_scripts.md`), reframed for Databricks + Delta + Unity Catalog. No AIA-internal
> specifics are assumed.

Owns the **correctness layer** of streaming on Databricks: source choice, trigger, state,
and exactly-once writes. For executor/shuffle/AQE tuning, use **`spark-tune`** (do not
duplicate it here).

## When to use

- Building or reviewing a Structured Streaming pipeline on Databricks (Kafka/MSK or files → Delta).
- Symptoms: duplicate rows, lost rows after restart, stuck/growing state, checkpoint errors,
  "stream won't resume", unbounded cost on an idle stream.
- Deciding: Auto Loader vs Kafka, `availableNow` vs `processingTime`, append vs MERGE.

## 1. Source choice — Auto Loader vs Kafka

| Use **Auto Loader** (`cloudFiles`) | Use **Kafka / MSK** |
|---|---|
| Source is files landing in S3 (vendor drops, exports, CDC files) | Source is an event log / true stream |
| Want cheap file discovery (SQS/SNS notifications, not LIST) | Need low end-to-end latency, replay by offset |
| Schema inference + `schemaEvolutionMode` built in | You control producers + schema registry |

```python
# Auto Loader — incremental file ingest, notification mode (avoids costly S3 LIST)
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.useNotifications", "true")        # SQS/SNS, not directory listing
      .option("cloudFiles.schemaLocation", SCHEMA_LOC)      # tracks schema across runs
      .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
      .load(SOURCE_PATH))
```

```python
# Kafka / MSK source — see example_scripts.md Script 1 for the full IAM-auth block
df = (spark.readStream.format("kafka")
      .option("kafka.bootstrap.servers", KAFKA_BROKERS)
      .option("subscribe", TOPIC)
      .option("startingOffsets", "latest")                  # "earliest" only for first backfill
      .option("maxOffsetsPerTrigger", "100000")             # rate limit — prevents huge first batch
      .option("failOnDataLoss", "false")                    # MSK retention can expire old offsets
      .load())
# AIA likely uses MSK with IAM auth — add kafka.sasl.* SASL_SSL / AWS_MSK_IAM block. STARTER: confirm.
```

## 2. Checkpoint discipline (the #1 source of bugs)

- **One checkpoint per (query, target). Never share.** A shared checkpoint silently corrupts offsets.
- **Namespace + version it.** Bump the version suffix on any incompatible change (schema, source, stateful logic) so the new run starts clean instead of failing to deserialize old state.

```python
CHECKPOINT_LOC = f"s3://<bucket>/checkpoints/{ENV}/{PIPELINE_NAME}_{PIPELINE_VERSION}/"
# Changing stateful ops or the source format? -> bump PIPELINE_VERSION, don't reuse the old dir.
```

## 3. Trigger mode — pick deliberately (cost lever)

| Mode | Use when | Cost note |
|---|---|---|
| `availableNow=True` | **Batch-style** "process everything waiting, then stop" | Cluster spins down after — cheapest for periodic ingest. Prefer this over a 24/7 stream when latency SLA allows. |
| `processingTime="30 seconds"` | True low-latency micro-batch | Cluster runs continuously — the expensive default; justify the SLA. |
| `continuous` | Sub-second (rare) | Limited sinks, no foreachBatch MERGE — usually **not** what you want. |

```python
.trigger(availableNow=True)            # incremental batch — spins down when caught up
# .trigger(processingTime="30 seconds")  # continuous micro-batch — only if latency SLA requires
```

> **Cost tie-in:** the single biggest streaming cost mistake is a 24/7 `processingTime` stream
> where `availableNow` on a schedule (e.g. every 5–15 min via Airflow/Workflows) would meet the SLA.
> See `databricks-cost-optimization` → "streaming idle cost".

## 4. Watermark + stateful ops

Required for windowed aggregation, stream-stream joins, and dedup-with-state — bounds state growth so it doesn't grow forever (and blow up cost/latency).

```python
df = df.withWatermark("event_time", "1 hour")   # drop/state-evict events later than 1h
# Stateless append/MERGE doesn't strictly need it, but declare it to document late-data tolerance.
```

## 5. Idempotent / exactly-once writes to Delta

Two patterns — match to the target semantics.

**(a) Append-only → `txnAppId` + `txnVersion`** (Delta dedupes on replay; from `example_scripts.md` Script 1/2):

```python
def write_append(batch_df, batch_id):
    if batch_df.isEmpty():
        return
    (batch_df.write.format("delta").mode("append")
        .option("txnAppId", PIPELINE_NAME)      # idempotency key: same (appId, version)
        .option("txnVersion", batch_id)         # -> Delta skips the duplicate commit on replay
        .saveAsTable(TARGET_TABLE))
```

**(b) Upsert → `foreachBatch` + SQL `MERGE`** (current-state tables; from `streaming_template.py`):

```python
def merge_to_target(batch_df, batch_id):
    if batch_df.isEmpty():                                   # empty-batch guard
        return
    batch_df.createOrReplaceTempView("src")
    spark.sql(f"""
        MERGE INTO {TARGET_TABLE} t
        USING (
            SELECT * FROM (                                  -- source dedupe: latest per key
                SELECT *, ROW_NUMBER() OVER (
                    PARTITION BY account_id ORDER BY etl_date DESC) rn
                FROM src
            ) WHERE rn = 1
        ) s
        ON  t.account_id = s.account_id
            AND t.region IN (SELECT DISTINCT region FROM src) -- partition pruning in ON
            AND t.update_date < s.etl_date                    -- idempotency + late-data guard
        WHEN MATCHED THEN UPDATE SET t.balance = s.balance, t.update_date = s.etl_date
        WHEN NOT MATCHED THEN INSERT (account_id, region, balance, update_date)
                            VALUES (s.account_id, s.region, s.balance, s.etl_date)
    """)   -- explicit columns, never SELECT */INSERT *
```

**Rules baked in** (the 14 concerns from the source templates): empty-batch guard, source dedupe,
partition pruning in `ON`, `update_date <` idempotency guard, explicit columns, one writer per
target table.

> `foreachBatch` MERGE gives **idempotent upsert**, not literal exactly-once. The `update_date <`
> guard is what makes a re-run safe — without it a replayed batch double-applies.

## 6. Schema evolution + DLQ

- **Bronze** = all-STRING, no parsing — drift-proof landing zone.
- **Silver** = parse against a **versioned data-contract schema**; route bad records to a DLQ table
  (don't fail the stream). See `example_scripts.md` Script 2 for the good/bad split + DLQ pattern.
- Delta write-side: `.option("mergeSchema", "true")` only for additive, reviewed changes — never blindly.

## 7. Monitoring

Attach a `StreamingQueryListener` (full impl in `streaming_template.py`): emit `batchId`,
`numInputRows`, input vs processed rate, `triggerExecution` ms → CloudWatch/Datadog; alert on
lag (input rate > process rate) and rising batch duration. In Databricks **Jobs**, don't call
`awaitTermination()` — the Jobs service owns lifecycle.

## Test plan

1. **Idempotency / replay** — delete checkpoint, re-run a fixed input batch, assert target row
   counts identical (the core safety property).
2. **DLQ** — feed malformed records, assert they land in DLQ and the stream stays up.
3. **Restart** — kill mid-batch, restart, assert no dup / no loss.
4. **Schema evolution** — add a column upstream, assert Auto Loader/contract handles it as designed.
5. **State bound** — windowed job: assert state size plateaus under load (watermark working).

## See also
- `spark-tune` — executor/shuffle/skew/AQE tuning (do not re-implement here).
- `databricks-cost-optimization` — trigger-mode + idle-stream cost.
- `airflow-databricks-orchestration` — scheduling `availableNow` runs.
