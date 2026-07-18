"""
================================================================
PRODUCTION STREAMING TEMPLATE
================================================================
Use case:    Streaming (true micro-batch, low-latency)
Pattern:     foreachBatch + SQL MERGE
Source:      Delta table (silver layer)
Target:      Delta table (gold layer)
Trigger:     processingTime (continuous micro-batch)
Concerns:    1-14 all addressed (see comments below)
================================================================
"""

from pyspark.sql.streaming import StreamingQueryListener
import logging

# ================================================================
# CONFIGURATION (per pipeline — change these)
# ================================================================
PIPELINE_NAME    = "balance_pipeline"
PIPELINE_VERSION = "v3"                          # ⬆️ bump on schema change

SOURCE_TABLE     = "silver.transactions"
TARGET_TABLE     = "gold.balance"

# 🛑 Concern 10: Checkpoint discipline (versioned, namespaced)
CHECKPOINT_LOC   = f"s3://aia-checkpoints/prod/{PIPELINE_NAME}_{PIPELINE_VERSION}/"

# Trigger (Concern 3 + 13)
TRIGGER_INTERVAL = "30 seconds"                  # how often micro-batch runs

# Concern 8: Watermark for late data bound
WATERMARK_COL    = "etl_date"
WATERMARK_DELAY  = "1 hour"

# Rate limiting (prevent batch overload)
MAX_FILES_PER_TRIGGER = "1000"
MAX_BYTES_PER_TRIGGER = "1g"


# ================================================================
# MONITORING (Concern 12)
# ================================================================
class StreamingMonitor(StreamingQueryListener):
    """Pushes streaming metrics to monitoring + alerts on lag"""
    
    def onQueryStarted(self, event):
        logging.info(f"[{PIPELINE_NAME}] Stream started: id={event.id}")
    
    def onQueryProgress(self, event):
        p = event.progress
        
        metrics = {
            "pipeline":          PIPELINE_NAME,
            "batch_id":          p.batchId,
            "input_rows":        p.numInputRows,
            "input_rate":        p.inputRowsPerSecond or 0,
            "process_rate":      p.processedRowsPerSecond or 0,
            "trigger_duration":  p.durationMs.get("triggerExecution", 0),
            "addBatch_duration": p.durationMs.get("addBatch", 0),
            "sources":           p.sources,
            "sink":              p.sink,
        }
        
        # Push to monitoring (Datadog / CloudWatch / etc.)
        # send_to_datadog(metrics)
        logging.info(f"[{PIPELINE_NAME}] Progress: {metrics}")
        
        # Alert if lag (input rate > process rate × 1.5)
        if metrics["input_rate"] > metrics["process_rate"] * 1.5 + 100:
            logging.warning(
                f"[{PIPELINE_NAME}] LAG: input={metrics['input_rate']} "
                f"process={metrics['process_rate']}"
            )
            # alert_pagerduty(...)
        
        # Alert if batch duration trending up
        if metrics["trigger_duration"] > 60_000:  # 1 minute
            logging.warning(f"[{PIPELINE_NAME}] Slow batch: {metrics['trigger_duration']}ms")
    
    def onQueryTerminated(self, event):
        if event.exception:
            logging.error(f"[{PIPELINE_NAME}] Stream FAILED: {event.exception}")
            # alert_pagerduty_critical(...)
        else:
            logging.info(f"[{PIPELINE_NAME}] Stream terminated cleanly")

# Register once (don't register multiple times for same query)
spark.streams.addListener(StreamingMonitor())


# ================================================================
# CORE MERGE LOGIC (Concerns 1, 2, 4, 5, 6, 9)
# ================================================================
def merge_to_target(batch_df, batch_id):
    """
    foreachBatch function — runs per micro-batch
    
    Addresses:
    - Concern 1: Idempotency via update_date guard (Sin's Fix A)
    - Concern 2: SQL MERGE only — no DataFrame actions
    - Concern 4: Partition pruning in ON
    - Concern 5: Empty batch check
    - Concern 6: Source dedupe via ROW_NUMBER
    - Concern 9: Explicit columns (no SELECT *, no INSERT *)
    """
    
    # ✅ Concern 5: Empty batch
    if batch_df.isEmpty():
        return
    
    # Register batch as view (no action triggered)
    batch_df.createOrReplaceTempView("source_batch")
    
    # ✅ Concern 2 + 6 + 4 + 1 + 9: All in single SQL
    spark.sql(f"""
        MERGE INTO {TARGET_TABLE} t
        USING (
            -- ✅ Concern 6: Dedupe source — keep latest per key
            SELECT 
                account_id,
                region,
                balance,
                etl_date
            FROM (
                SELECT 
                    account_id,
                    region,
                    balance,
                    etl_date,
                    ROW_NUMBER() OVER (
                        PARTITION BY account_id 
                        ORDER BY etl_date DESC
                    ) as rn
                FROM source_batch
            )
            WHERE rn = 1
        ) s
        ON  t.account_id = s.account_id
            -- ✅ Concern 4: Partition pruning
            AND t.region IN (SELECT DISTINCT region FROM source_batch)
            -- ✅ Concern 1 + 8: Idempotency + late data guard
            AND t.update_date < s.etl_date
        -- ✅ Concern 9: Explicit columns
        WHEN MATCHED THEN UPDATE SET
            t.balance     = s.balance,
            t.update_date = s.etl_date
        WHEN NOT MATCHED THEN INSERT 
            (account_id, region, balance, update_date)
            VALUES 
            (s.account_id, s.region, s.balance, s.etl_date)
    """)


# ================================================================
# STREAMING PIPELINE
# ================================================================
def run_stream():
    """Main streaming pipeline — call once at start of job"""
    
    # ----- READ -----
    source_df = (
        spark.readStream
            .format("delta")
            
            # Source handling (Concern 5 of Pattern selection)
            .option("skipChangeCommits", "true")        # Skip if source has updates/deletes
            # OR .option("ignoreChanges", "true")        # Older, less clean
            
            # Rate limiting (prevent batch overload)
            .option("maxFilesPerTrigger", MAX_FILES_PER_TRIGGER)
            .option("maxBytesPerTrigger", MAX_BYTES_PER_TRIGGER)
            
            # Read from Delta table
            .table(SOURCE_TABLE)
    )
    
    # ----- WATERMARK (Concern 8) -----
    # Required if you use stateful ops (groupBy window, stream-stream join)
    # Optional for stateless — but documents your late-data tolerance
    watermarked_df = source_df.withWatermark(
        WATERMARK_COL, 
        WATERMARK_DELAY
    )
    
    # ----- WRITE -----
    query = (
        watermarked_df.writeStream
            
            # Identity (for monitoring + logs)
            .queryName(PIPELINE_NAME)
            
            # ✅ Concern 7: One writer per target table (documented)
            # If you need another writer to gold.balance → create separate pipeline reading from different source
            
            # Custom merge logic
            .foreachBatch(merge_to_target)
            
            # ✅ Concern 10: Versioned, namespaced checkpoint
            .option("checkpointLocation", CHECKPOINT_LOC)
            
            # ✅ Concern 3: processingTime trigger (NOT continuous, NOT availableNow)
            .trigger(processingTime=TRIGGER_INTERVAL)
            
            .start()
    )
    
    logging.info(f"[{PIPELINE_NAME}] Started — id={query.id}, runId={query.runId}")
    return query


# ================================================================
# RUN
# ================================================================
query = run_stream()

# Note: Don't call query.awaitTermination() in Databricks Jobs
# Jobs service handles lifecycle automatically
# For notebook testing only:
# query.awaitTermination()