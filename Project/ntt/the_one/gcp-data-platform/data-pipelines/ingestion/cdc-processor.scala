package com.dataplatform.pipelines.ingestion

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.streaming.Trigger
import com.dataplatform.core._
import com.dataplatform.monitoring._
import java.time.Instant
import java.util.UUID

object CDCProcessor {
  
  def main(args: Array[String]): Unit = {
    
    val spark = SparkSession.builder()
      .appName("CDC-Processor")
      .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
      .config("spark.sql.streaming.checkpointLocation", "gs://your-bucket/checkpoints/cdc-processor")
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg.type", "hadoop")
      .config("spark.sql.catalog.iceberg.warehouse", "gs://your-bucket/iceberg-warehouse")
      .getOrCreate()
    
    val projectId = sys.env.getOrElse("GOOGLE_CLOUD_PROJECT", "your-project-id")
    val jobId = UUID.randomUUID().toString
    
    // Initialize services
    val icebergManager = new IcebergManager(spark)
    val auditLogger = new AuditLogger(spark, projectId)
    val lineageTracker = new LineageTracker(spark, projectId)
    
    try {
      // Parse arguments
      val pubsubSubscription = getArgValue(args, "--pubsub-subscription", "cdc-changes")
      val targetTable = getArgValue(args, "--target-table", "raw.cdc_changes")
      
      auditLogger.logJobStart(jobId, "CDC-Processor", targetTable, "STREAMING_CDC")
      
      // Read from Pub/Sub
      val cdcStream = spark.readStream
        .format("pubsub")
        .option("subscription", s"projects/$projectId/subscriptions/$pubsubSubscription")
        .load()
      
      // Parse CDC messages
      val parsedCDC = cdcStream
        .select(
          from_json(col("data").cast("string"), getCDCSchema()).alias("cdc_data"),
          col("timestamp").alias("_pubsub_timestamp")
        )
        .select(
          col("cdc_data.*"),
          col("_pubsub_timestamp"),
          current_timestamp().alias("_processing_timestamp")
        )
      
      // Process CDC operations
      val processedCDC = parsedCDC
        .withColumn("_operation_type", col("operation")) // INSERT, UPDATE, DELETE
        .withColumn("_source_lsn", col("lsn")) // Log Sequence Number
        .withColumn("_partition_date", to_date(col("_processing_timestamp")))
      
      // Write to Iceberg with merge operations
      val query = processedCDC.writeStream
        .outputMode("append")
        .format("iceberg")
        .option("table", targetTable)
        .option("checkpointLocation", s"gs://your-bucket/checkpoints/cdc-processor/$targetTable")
        .trigger(Trigger.ProcessingTime("30 seconds"))
        .start()
      
      // Track streaming lineage
      lineageTracker.trackTableLineage(
        sourceTable = s"pubsub.$pubsubSubscription",
        targetTable = targetTable,
        transformation = "cdc_streaming_ingestion",
        jobId = jobId
      )
      
      query.awaitTermination()
      
    } catch {
      case e: Exception =>
        auditLogger.logJobCompletion(
          jobId = jobId,
          jobName = "CDC-Processor",
          tableName = args.find(_.startsWith("--target-table")).map(_.split("=", 2)(1)).getOrElse("unknown"),
          operation = "STREAMING_CDC",
          recordsProcessed = 0,
          startTime = Instant.now(),
          status = "FAILED",
          errorMessage = Some(e.getMessage)
        )
        
        println(s"CDC processing failed: ${e.getMessage}")
        e.printStackTrace()
        throw e
    }
  }
  
  private def getCDCSchema(): StructType = {
    StructType(Seq(
      StructField("operation", StringType, false),
      StructField("lsn", StringType, false),
      StructField("table_name", StringType, false),
      StructField("before", MapType(StringType, StringType), true),
      StructField("after", MapType(StringType, StringType), true),
      StructField("timestamp", TimestampType, false)
    ))
  }
  
  private def getArgValue(args: Array[String], key: String, default: String): String = {
    args.find(_.startsWith(s"$key="))
      .map(_.split("=", 2)(1))
      .getOrElse(default)
  }
}