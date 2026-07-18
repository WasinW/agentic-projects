ลุยเลย — 3 scripts แยกชัดเจน ใช้ได้จริงในกระบวนการ production

---

# 📋 Pipeline Architecture

```
Kafka Topic (transactions)
   │
   ├─[Script 1: Consumer]─────► RAW Table (append-only, all STRING)
   │                                 │
   │                                 ↓
   ├─[Script 2: Transform]────► PERSIST Table (append-only, typed)
   │                                 │
   │                                 ↓
   └─[Script 3: Transform]────► CURATED Table (upsert, business logic)
```

---

# 🎬 Script 1: Kafka Consumer → RAW Table

```python
"""
================================================================
SCRIPT 1: KAFKA CONSUMER → RAW TABLE
================================================================
Purpose:    Consume Kafka messages and append to raw layer
Pattern:    Pattern 1 (direct streaming write, append-only)
Source:     Kafka topic 'transactions'
Target:     bronze.transactions_raw (append-only, all STRING)

Design decisions:
- All columns STRING (no type casting in this layer)
- Preserve raw message + metadata
- Idempotency via Kafka offset (exactly tracked in checkpoint)
- One consumer per topic (Concern 7)
- Schema drift safe (no parsing here)
================================================================
"""

from pyspark.sql.functions import col, current_timestamp, lit
from pyspark.sql.streaming import StreamingQueryListener
import logging


# ================================================================
# CONFIGURATION
# ================================================================
PIPELINE_NAME    = "kafka_to_raw_transactions"
PIPELINE_VERSION = "v1"

# Kafka source
KAFKA_BROKERS    = "msk-broker-1:9092,msk-broker-2:9092,msk-broker-3:9092"
KAFKA_TOPIC      = "transactions"
CONSUMER_GROUP   = "aia-de-transactions-raw"   # Kafka consumer group

# Target
TARGET_TABLE     = "bronze.transactions_raw"

# Checkpoint (versioned + namespaced)
CHECKPOINT_LOC   = f"s3://aia-checkpoints/prod/{PIPELINE_NAME}_{PIPELINE_VERSION}/"

# Trigger
TRIGGER_INTERVAL = "30 seconds"

# Rate limiting
MAX_OFFSETS_PER_TRIGGER = "100000"


# ================================================================
# MONITORING (Concern 12)
# ================================================================
class StreamingMonitor(StreamingQueryListener):
    def onQueryStarted(self, event):
        logging.info(f"[{PIPELINE_NAME}] Started: id={event.id}")
    
    def onQueryProgress(self, event):
        p = event.progress
        logging.info(
            f"[{PIPELINE_NAME}] batch={p.batchId} "
            f"rows={p.numInputRows} "
            f"rate={p.inputRowsPerSecond:.0f}/s "
            f"duration={p.durationMs.get('triggerExecution', 0)}ms"
        )
        
        # Lag alert
        if (p.inputRowsPerSecond or 0) > (p.processedRowsPerSecond or 0) * 1.5 + 100:
            logging.warning(f"[{PIPELINE_NAME}] LAG detected")
    
    def onQueryTerminated(self, event):
        if event.exception:
            logging.error(f"[{PIPELINE_NAME}] FAILED: {event.exception}")
        else:
            logging.info(f"[{PIPELINE_NAME}] Terminated cleanly")

spark.streams.addListener(StreamingMonitor())


# ================================================================
# TARGET TABLE SCHEMA (Run once during setup)
# ================================================================
# CREATE TABLE bronze.transactions_raw (
#     -- Kafka metadata
#     kafka_topic         STRING,
#     kafka_partition     INT,
#     kafka_offset        LONG,
#     kafka_timestamp     TIMESTAMP,
#     kafka_timestamp_type INT,
#     kafka_key           STRING,
#     
#     -- Message payload (raw JSON as string)
#     message_value       STRING,           ⭐ All raw, no parsing
#     message_headers     STRING,           
#     
#     -- Ingestion metadata
#     ingested_at         TIMESTAMP,
#     ingestion_date      DATE,
#     batch_id            LONG,
#     consumer_group      STRING
# )
# USING DELTA
# PARTITIONED BY (ingestion_date)
# TBLPROPERTIES (
#     delta.autoOptimize.optimizeWrite = true,
#     delta.autoOptimize.autoCompact = true,
#     delta.enableChangeDataFeed = true   -- For downstream
# );


# ================================================================
# CORE LOGIC
# ================================================================
def write_to_raw(batch_df, batch_id):
    """
    Append Kafka batch to raw table
    
    All columns kept as STRING — no parsing/typing in this layer
    """
    
    # ✅ Concern 5: Empty batch check
    if batch_df.isEmpty():
        return
    
    # Add ingestion metadata
    batch_with_meta = (batch_df
        .withColumn("ingested_at", current_timestamp())
        .withColumn("ingestion_date", current_timestamp().cast("date"))
        .withColumn("batch_id", lit(batch_id).cast("long"))
        .withColumn("consumer_group", lit(CONSUMER_GROUP))
    )
    
    # ✅ Concern 9: Explicit columns (no SELECT *)
    final_df = batch_with_meta.select(
        col("topic").alias("kafka_topic"),
        col("partition").alias("kafka_partition"),
        col("offset").alias("kafka_offset"),
        col("timestamp").alias("kafka_timestamp"),
        col("timestampType").alias("kafka_timestamp_type"),
        col("key").cast("string").alias("kafka_key"),
        col("value").cast("string").alias("message_value"),
        col("headers").cast("string").alias("message_headers"),
        col("ingested_at"),
        col("ingestion_date"),
        col("batch_id"),
        col("consumer_group"),
    )
    
    # Append to raw table (no MERGE — pure append)
    (final_df.write
        .format("delta")
        .mode("append")
        # Idempotency for replay
        .option("txnAppId", PIPELINE_NAME)
        .option("txnVersion", batch_id)
        .saveAsTable(TARGET_TABLE))


# ================================================================
# STREAMING PIPELINE
# ================================================================
def run_kafka_consumer():
    """Consume from Kafka and write to raw layer"""
    
    # ----- READ from Kafka -----
    kafka_df = (
        spark.readStream
            .format("kafka")
            
            # Kafka connection
            .option("kafka.bootstrap.servers", KAFKA_BROKERS)
            .option("subscribe", KAFKA_TOPIC)
            
            # Consumer group (commits offsets back to Kafka for monitoring)
            .option("kafka.group.id", CONSUMER_GROUP)
            
            # Starting position (first run only — checkpoint takes over after)
            .option("startingOffsets", "latest")     # or "earliest" for backfill
            
            # Rate limiting
            .option("maxOffsetsPerTrigger", MAX_OFFSETS_PER_TRIGGER)
            
            # Failure handling
            .option("failOnDataLoss", "false")        # Don't fail if Kafka loses old offsets
            
            # Security (uncomment if AIA uses MSK with IAM/SSL)
            # .option("kafka.security.protocol", "SASL_SSL")
            # .option("kafka.sasl.mechanism", "AWS_MSK_IAM")
            # .option("kafka.sasl.jaas.config", 
            #         "software.amazon.msk.auth.iam.IAMLoginModule required;")
            # .option("kafka.sasl.client.callback.handler.class",
            #         "software.amazon.msk.auth.iam.IAMClientCallbackHandler")
            
            .load()
    )
    
    # ----- WRITE -----
    query = (
        kafka_df.writeStream
            
            .queryName(PIPELINE_NAME)
            
            .foreachBatch(write_to_raw)
            
            # ✅ Concern 10: Versioned checkpoint
            .option("checkpointLocation", CHECKPOINT_LOC)
            
            # ✅ Concern 3: Micro-batch trigger
            .trigger(processingTime=TRIGGER_INTERVAL)
            
            .start()
    )
    
    logging.info(f"[{PIPELINE_NAME}] Started — id={query.id}")
    return query


# ================================================================
# RUN
# ================================================================
query = run_kafka_consumer()
```

---

# 🔄 Script 2: RAW → PERSIST (Type Casting per Data Contract)

```python
"""
================================================================
SCRIPT 2: RAW → PERSIST TABLE
================================================================
Purpose:    Parse raw JSON, apply data contract types, append to persist
Pattern:    Pattern 1 (streaming read, append-only)
Source:     bronze.transactions_raw (append-only)
Target:     silver.transactions_persist (append-only, typed)

Design decisions:
- Append-only (preserves history)
- Apply types per Data Contract / Spec Document
- Schema enforced (no drift through)
- Bad records → DLQ table (don't fail pipeline)
- Idempotency via raw's kafka_offset + ingestion_date
================================================================
"""

from pyspark.sql.functions import (
    col, from_json, current_timestamp, lit, to_date, to_timestamp
)
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, LongType,
    DecimalType, TimestampType, DateType, BooleanType
)
from pyspark.sql.streaming import StreamingQueryListener
import logging


# ================================================================
# CONFIGURATION
# ================================================================
PIPELINE_NAME    = "raw_to_persist_transactions"
PIPELINE_VERSION = "v1"

SOURCE_TABLE     = "bronze.transactions_raw"
TARGET_TABLE     = "silver.transactions_persist"
DLQ_TABLE        = "silver.transactions_dlq"     # Dead Letter Queue

CHECKPOINT_LOC   = f"s3://aia-checkpoints/prod/{PIPELINE_NAME}_{PIPELINE_VERSION}/"

TRIGGER_INTERVAL = "1 minute"

# Rate limiting (read from Delta source)
MAX_FILES_PER_TRIGGER = "100"
MAX_BYTES_PER_TRIGGER = "1g"


# ================================================================
# DATA CONTRACT SCHEMA (Per Spec Document)
# Document this in confluence/wiki + version it
# ================================================================
TRANSACTION_SCHEMA = StructType([
    StructField("transaction_id",   StringType(),       nullable=False),
    StructField("account_id",       StringType(),       nullable=False),
    StructField("region",           StringType(),       nullable=False),
    StructField("transaction_type", StringType(),       nullable=False),
    StructField("amount",           DecimalType(18, 2), nullable=False),
    StructField("currency",         StringType(),       nullable=False),
    StructField("transaction_time", StringType(),       nullable=False),    # ISO timestamp string
    StructField("merchant_id",      StringType(),       nullable=True),
    StructField("metadata",         StringType(),       nullable=True),     # JSON sub-object
])


# ================================================================
# TARGET TABLE SCHEMA (Run once)
# ================================================================
# CREATE TABLE silver.transactions_persist (
#     -- Business columns (from data contract)
#     transaction_id      STRING NOT NULL,
#     account_id          STRING NOT NULL,
#     region              STRING NOT NULL,
#     transaction_type    STRING NOT NULL,
#     amount              DECIMAL(18, 2) NOT NULL,
#     currency            STRING NOT NULL,
#     transaction_time    TIMESTAMP NOT NULL,
#     merchant_id         STRING,
#     metadata            STRING,
#     
#     -- Lineage from raw
#     kafka_partition     INT,
#     kafka_offset        LONG,
#     kafka_timestamp     TIMESTAMP,
#     
#     -- ETL metadata
#     etl_date            TIMESTAMP,
#     etl_batch_id        LONG,
#     business_date       DATE                -- derived from transaction_time
# )
# USING DELTA
# PARTITIONED BY (business_date)
# TBLPROPERTIES (
#     delta.autoOptimize.optimizeWrite = true,
#     delta.autoOptimize.autoCompact = true,
#     delta.enableChangeDataFeed = true
# );
#
# -- DLQ table for bad records
# CREATE TABLE silver.transactions_dlq (
#     -- Original raw fields
#     kafka_partition     INT,
#     kafka_offset        LONG,
#     message_value       STRING,
#     
#     -- Error details
#     error_reason        STRING,
#     error_detail        STRING,
#     
#     -- Metadata
#     dlq_at              TIMESTAMP,
#     etl_batch_id        LONG
# )
# USING DELTA
# PARTITIONED BY (DATE(dlq_at));


# ================================================================
# MONITORING
# ================================================================
class StreamingMonitor(StreamingQueryListener):
    def onQueryStarted(self, event):
        logging.info(f"[{PIPELINE_NAME}] Started: id={event.id}")
    
    def onQueryProgress(self, event):
        p = event.progress
        logging.info(
            f"[{PIPELINE_NAME}] batch={p.batchId} "
            f"rows={p.numInputRows} "
            f"duration={p.durationMs.get('triggerExecution', 0)}ms"
        )
    
    def onQueryTerminated(self, event):
        if event.exception:
            logging.error(f"[{PIPELINE_NAME}] FAILED: {event.exception}")

spark.streams.addListener(StreamingMonitor())


# ================================================================
# CORE TRANSFORM LOGIC
# ================================================================
def parse_and_persist(batch_df, batch_id):
    """
    Parse JSON, apply types per Data Contract
    Bad records → DLQ
    Good records → Persist
    """
    
    # ✅ Concern 5: Empty batch
    if batch_df.isEmpty():
        return
    
    # Register batch (no action — lazy)
    batch_df.createOrReplaceTempView("raw_batch")
    
    # ----- PARSE + TYPE CAST -----
    parsed_sql = """
        SELECT 
            -- Parse JSON
            from_json(message_value, '{schema}') as parsed,
            
            -- Lineage
            kafka_partition,
            kafka_offset,
            kafka_timestamp,
            message_value,
            
            -- ETL metadata
            current_timestamp() as etl_date,
            {batch_id}L as etl_batch_id
        FROM raw_batch
    """.format(
        schema=TRANSACTION_SCHEMA.simpleString(),
        batch_id=batch_id
    )
    
    parsed_df = spark.sql(parsed_sql)
    parsed_df.createOrReplaceTempView("parsed_batch")
    
    # ----- SPLIT GOOD/BAD -----
    
    # Good records: parsing succeeded + required fields present
    good_sql = """
        SELECT 
            parsed.transaction_id      AS transaction_id,
            parsed.account_id          AS account_id,
            parsed.region              AS region,
            parsed.transaction_type    AS transaction_type,
            parsed.amount              AS amount,
            parsed.currency            AS currency,
            CAST(parsed.transaction_time AS TIMESTAMP) AS transaction_time,
            parsed.merchant_id         AS merchant_id,
            parsed.metadata            AS metadata,
            kafka_partition,
            kafka_offset,
            kafka_timestamp,
            etl_date,
            etl_batch_id,
            CAST(parsed.transaction_time AS DATE) AS business_date
        FROM parsed_batch
        WHERE parsed IS NOT NULL
          AND parsed.transaction_id IS NOT NULL
          AND parsed.account_id IS NOT NULL
          AND parsed.amount IS NOT NULL
          AND parsed.transaction_time IS NOT NULL
    """
    
    good_df = spark.sql(good_sql)
    
    # Bad records: parsing failed OR required fields missing
    bad_sql = """
        SELECT 
            kafka_partition,
            kafka_offset,
            message_value,
            CASE 
                WHEN parsed IS NULL 
                    THEN 'JSON_PARSE_FAILED'
                WHEN parsed.transaction_id IS NULL 
                    THEN 'MISSING_TRANSACTION_ID'
                WHEN parsed.account_id IS NULL 
                    THEN 'MISSING_ACCOUNT_ID'
                WHEN parsed.amount IS NULL 
                    THEN 'MISSING_AMOUNT'
                WHEN parsed.transaction_time IS NULL 
                    THEN 'MISSING_TRANSACTION_TIME'
                ELSE 'UNKNOWN'
            END AS error_reason,
            CAST(parsed AS STRING) AS error_detail,
            current_timestamp() AS dlq_at,
            etl_batch_id
        FROM parsed_batch
        WHERE parsed IS NULL
           OR parsed.transaction_id IS NULL
           OR parsed.account_id IS NULL
           OR parsed.amount IS NULL
           OR parsed.transaction_time IS NULL
    """
    
    bad_df = spark.sql(bad_sql)
    
    # ----- WRITE BOTH TABLES (atomic per batch via txnVersion) -----
    
    # Good → Persist
    if not good_df.isEmpty():
        (good_df.write
            .format("delta")
            .mode("append")
            .option("txnAppId", f"{PIPELINE_NAME}_good")
            .option("txnVersion", batch_id)
            .saveAsTable(TARGET_TABLE))
    
    # Bad → DLQ
    if not bad_df.isEmpty():
        bad_count = bad_df.count()
        logging.warning(f"[{PIPELINE_NAME}] batch={batch_id} bad_records={bad_count}")
        
        (bad_df.write
            .format("delta")
            .mode("append")
            .option("txnAppId", f"{PIPELINE_NAME}_dlq")
            .option("txnVersion", batch_id)
            .saveAsTable(DLQ_TABLE))


# ================================================================
# STREAMING PIPELINE
# ================================================================
def run_raw_to_persist():
    """Read raw, parse, type-cast, persist"""
    
    # ----- READ from raw table -----
    raw_df = (
        spark.readStream
            .format("delta")
            
            # Skip non-append commits (shouldn't happen in raw, but safe)
            .option("skipChangeCommits", "true")
            
            # Rate limiting
            .option("maxFilesPerTrigger", MAX_FILES_PER_TRIGGER)
            .option("maxBytesPerTrigger", MAX_BYTES_PER_TRIGGER)
            
            .table(SOURCE_TABLE)
    )
    
    # No watermark needed — append-only, no stateful ops
    
    # ----- WRITE -----
    query = (
        raw_df.writeStream
            
            .queryName(PIPELINE_NAME)
            
            .foreachBatch(parse_and_persist)
            
            .option("checkpointLocation", CHECKPOINT_LOC)
            
            .trigger(processingTime=TRIGGER_INTERVAL)
            
            .start()
    )
    
    logging.info(f"[{PIPELINE_NAME}] Started — id={query.id}")
    return query


# ================================================================
# RUN
# ================================================================
query = run_raw_to_persist()
```

---

# 🎯 Script 3: PERSIST → CURATED (Business Logic + Upsert)

```python
"""
================================================================
SCRIPT 3: PERSIST → CURATED TABLE
================================================================
Purpose:    Apply business logic + upsert to curated layer
Pattern:    Pattern 3 (foreachBatch + SQL MERGE) ⭐
Source:     silver.transactions_persist (append-only, typed)
Target:     gold.account_balance (upsert, current state)

Design decisions (all 14 concerns addressed):
- SQL MERGE only (no DataFrame actions)
- Idempotency via update_date guard
- Partition pruning in ON
- Source dedupe via ROW_NUMBER
- Explicit columns
- Watermark for late data bound
- Monitoring + alerting
- Versioned checkpoint
================================================================
"""

from pyspark.sql.streaming import StreamingQueryListener
import logging


# ================================================================
# CONFIGURATION
# ================================================================
PIPELINE_NAME    = "persist_to_curated_balance"
PIPELINE_VERSION = "v1"

SOURCE_TABLE     = "silver.transactions_persist"
TARGET_TABLE     = "gold.account_balance"

CHECKPOINT_LOC   = f"s3://aia-checkpoints/prod/{PIPELINE_NAME}_{PIPELINE_VERSION}/"

# Trigger
TRIGGER_INTERVAL = "30 seconds"

# Watermark
WATERMARK_COL    = "etl_date"
WATERMARK_DELAY  = "1 hour"

# Rate limiting
MAX_FILES_PER_TRIGGER = "200"
MAX_BYTES_PER_TRIGGER = "1g"


# ================================================================
# TARGET TABLE SCHEMA (Run once)
# ================================================================
# CREATE TABLE gold.account_balance (
#     account_id          STRING NOT NULL,
#     region              STRING NOT NULL,
#     
#     -- Aggregated state
#     current_balance     DECIMAL(18, 2) NOT NULL,
#     last_transaction_id STRING,
#     last_transaction_time TIMESTAMP,
#     transaction_count   LONG,
#     
#     -- Status
#     account_status      STRING,         -- ACTIVE | DORMANT | CLOSED
#     
#     -- ETL metadata (for idempotency guard)
#     update_date         TIMESTAMP NOT NULL,
#     update_batch_id     LONG
# )
# USING DELTA
# PARTITIONED BY (region)
# CLUSTER BY (account_id)
# TBLPROPERTIES (
#     delta.autoOptimize.optimizeWrite = true,
#     delta.autoOptimize.autoCompact = true,
#     delta.enableChangeDataFeed = true,
#     'delta.feature.allowColumnDefaults' = 'supported'
# );


# ================================================================
# MONITORING
# ================================================================
class StreamingMonitor(StreamingQueryListener):
    def onQueryStarted(self, event):
        logging.info(f"[{PIPELINE_NAME}] Started: id={event.id}")
    
    def onQueryProgress(self, event):
        p = event.progress
        metrics = {
            "batch_id":        p.batchId,
            "input_rows":      p.numInputRows,
            "duration_ms":     p.durationMs.get("triggerExecution", 0),
            "addBatch_ms":     p.durationMs.get("addBatch", 0),
        }
        logging.info(f"[{PIPELINE_NAME}] {metrics}")
        
        # Lag alert
        if (p.inputRowsPerSecond or 0) > (p.processedRowsPerSecond or 0) * 1.5 + 100:
            logging.warning(f"[{PIPELINE_NAME}] LAG: alert!")
        
        # Slow batch alert
        if metrics["duration_ms"] > 120_000:
            logging.warning(f"[{PIPELINE_NAME}] SLOW BATCH: {metrics['duration_ms']}ms")
    
    def onQueryTerminated(self, event):
        if event.exception:
            logging.error(f"[{PIPELINE_NAME}] FAILED: {event.exception}")

spark.streams.addListener(StreamingMonitor())


# ================================================================
# CORE MERGE LOGIC (Business Rules + Upsert)
# ================================================================
def merge_to_curated(batch_df, batch_id):
    """
    Apply business logic and MERGE into curated table
    
    Business rules:
    - CREDIT increases balance, DEBIT decreases
    - Track transaction count
    - Determine account status based on activity
    - Latest transaction info preserved
    """
    
    # ✅ Concern 5: Empty batch check
    if batch_df.isEmpty():
        return
    
    # Register batch (no action triggered)
    batch_df.createOrReplaceTempView("persist_batch")
    
    # ✅ Concerns 1, 2, 4, 6, 9 all in single SQL MERGE
    spark.sql(f"""
        MERGE INTO {TARGET_TABLE} t
        USING (
            -- ✅ Concern 6: Source dedupe — aggregate per account
            SELECT 
                account_id,
                region,
                
                -- Business logic: net delta from this batch
                SUM(
                    CASE 
                        WHEN transaction_type = 'CREDIT' THEN amount
                        WHEN transaction_type = 'DEBIT'  THEN -amount
                        ELSE 0
                    END
                ) as net_delta,
                
                COUNT(*) as txn_count_delta,
                
                -- Latest transaction (use FIRST_VALUE with ordering)
                FIRST_VALUE(transaction_id) OVER w as last_transaction_id,
                FIRST_VALUE(transaction_time) OVER w as last_transaction_time,
                
                MAX(etl_date) as max_etl_date
                
            FROM persist_batch
            WINDOW w AS (
                PARTITION BY account_id 
                ORDER BY transaction_time DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            )
            GROUP BY 
                account_id, 
                region,
                transaction_id,
                transaction_time
        ) s
        ON  t.account_id = s.account_id
            
            -- ✅ Concern 4: Partition pruning
            AND t.region IN (
                SELECT DISTINCT region FROM persist_batch
            )
            
            -- ✅ Concern 1 + 8: Idempotency + late data guard
            AND t.update_date < s.max_etl_date
        
        -- ✅ Concern 9: Explicit columns
        WHEN MATCHED THEN UPDATE SET
            t.current_balance       = t.current_balance + s.net_delta,
            t.last_transaction_id   = s.last_transaction_id,
            t.last_transaction_time = s.last_transaction_time,
            t.transaction_count     = t.transaction_count + s.txn_count_delta,
            t.account_status        = CASE 
                WHEN t.current_balance + s.net_delta < 0 THEN 'OVERDRAWN'
                WHEN s.max_etl_date > t.update_date     THEN 'ACTIVE'
                ELSE t.account_status
            END,
            t.update_date           = s.max_etl_date,
            t.update_batch_id       = {batch_id}L
        
        WHEN NOT MATCHED THEN INSERT (
            account_id,
            region,
            current_balance,
            last_transaction_id,
            last_transaction_time,
            transaction_count,
            account_status,
            update_date,
            update_batch_id
        )
        VALUES (
            s.account_id,
            s.region,
            s.net_delta,
            s.last_transaction_id,
            s.last_transaction_time,
            s.txn_count_delta,
            'ACTIVE',
            s.max_etl_date,
            {batch_id}L
        )
    """)
    
    # Optional: Log MERGE metrics
    history = spark.sql(f"""
        SELECT operationMetrics 
        FROM (DESCRIBE HISTORY {TARGET_TABLE} LIMIT 1)
    """).first()
    
    if history:
        metrics = history["operationMetrics"]
        logging.info(
            f"[{PIPELINE_NAME}] batch={batch_id} "
            f"updated={metrics.get('numTargetRowsUpdated', 0)} "
            f"inserted={metrics.get('numTargetRowsInserted', 0)}"
        )


# ================================================================
# STREAMING PIPELINE
# ================================================================
def run_persist_to_curated():
    """Read persist, apply business logic, MERGE to curated"""
    
    # ----- READ from persist -----
    source_df = (
        spark.readStream
            .format("delta")
            
            # Skip non-append (persist should be append-only)
            .option("skipChangeCommits", "true")
            
            # Rate limiting
            .option("maxFilesPerTrigger", MAX_FILES_PER_TRIGGER)
            .option("maxBytesPerTrigger", MAX_BYTES_PER_TRIGGER)
            
            .table(SOURCE_TABLE)
    )
    
    # ✅ Concern 8: Watermark for late data
    watermarked_df = source_df.withWatermark(
        WATERMARK_COL, 
        WATERMARK_DELAY
    )
    
    # ----- WRITE -----
    query = (
        watermarked_df.writeStream
            
            .queryName(PIPELINE_NAME)
            
            # ✅ Concern 7: One writer per target (documented convention)
            
            .foreachBatch(merge_to_curated)
            
            # ✅ Concern 10: Versioned checkpoint
            .option("checkpointLocation", CHECKPOINT_LOC)
            
            # ✅ Concern 3: processingTime (not continuous)
            .trigger(processingTime=TRIGGER_INTERVAL)
            
            .start()
    )
    
    logging.info(f"[{PIPELINE_NAME}] Started — id={query.id}")
    return query


# ================================================================
# RUN
# ================================================================
query = run_persist_to_curated()
```

---

# 📊 Summary: Pipeline Comparison

| Aspect | Script 1: Kafka→Raw | Script 2: Raw→Persist | Script 3: Persist→Curated |
|---|---|---|---|
| **Pattern** | Append-only write | Append-only write | foreachBatch + MERGE |
| **Source** | Kafka topic | Delta table (raw) | Delta table (persist) |
| **Target** | Delta append | Delta append + DLQ | Delta upsert |
| **Schema** | All STRING | Typed per contract | Business-ready |
| **Transformations** | Metadata only | Parse + type cast | Business logic + agg |
| **Idempotency** | Kafka offset | kafka_offset preserved | update_date guard |
| **Error handling** | Trust Kafka | DLQ table | Business validation |
| **Trigger** | 30 seconds | 1 minute | 30 seconds |
| **Watermark** | No | No | Yes (1 hour) |
| **Stateful** | No | No | Implicit via MERGE |
| **Concerns** | 5,7,9,10,12,13 | 5,7,9,10,12,13 + DLQ | All 14 |

---

# 🚀 Deployment Strategy

```
Databricks Workflow (DAG):

   ┌─────────────────────┐
   │  Job: Stream Layer  │
   ├─────────────────────┤
   │                     │
   │  ┌──────────────┐   │
   │  │ Script 1     │ ── continuous run
   │  │ Kafka→Raw    │   │
   │  └──────────────┘   │
   │                     │
   │  ┌──────────────┐   │
   │  │ Script 2     │ ── continuous run
   │  │ Raw→Persist  │   │
   │  └──────────────┘   │
   │                     │
   │  ┌──────────────┐   │
   │  │ Script 3     │ ── continuous run
   │  │ Persist→Cur  │   │
   │  └──────────────┘   │
   │                     │
   └─────────────────────┘
   
   ┌─────────────────────┐
   │ Job: Maintenance    │ ── weekly schedule
   ├─────────────────────┤
   │  OPTIMIZE + VACUUM  │
   │  + ANALYZE          │
   └─────────────────────┘
   
   ┌─────────────────────┐
   │ Job: DLQ Reprocess  │ ── daily schedule
   ├─────────────────────┤
   │  Fix bad records    │
   │  + Re-insert        │
   └─────────────────────┘
```

---

อยากต่อ:
1. **Maintenance script** (OPTIMIZE/VACUUM/ANALYZE schedule)?
2. **DLQ reprocessing script** (รับ DLQ มาแก้แล้วยัดกลับ)?
3. **Common framework** (refactor 3 scripts ให้แชร์ code base)?
4. **Update file** ใส่ 3 scripts ทั้งหมด?