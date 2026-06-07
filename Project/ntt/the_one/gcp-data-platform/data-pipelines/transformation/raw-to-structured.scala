package com.dataplatform.pipelines.transformation

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import com.dataplatform.core._
import com.dataplatform.monitoring._
import java.time.Instant
import java.util.UUID

object RawToStructured {
  
  def main(args: Array[String]): Unit = {
    
    val spark = SparkSession.builder()
      .appName("Raw-To-Structured")
      .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg.type", "hadoop")
      .config("spark.sql.catalog.iceberg.warehouse", "gs://your-bucket/iceberg-warehouse")
      .getOrCreate()
    
    val projectId = sys.env.getOrElse("GOOGLE_CLOUD_PROJECT", "your-project-id")
    val jobId = UUID.randomUUID().toString
    val startTime = Instant.now()
    
    // Initialize services
    val icebergManager = new IcebergManager(spark)
    val validationEngine = new ValidationEngine(spark)
    val auditLogger = new AuditLogger(spark, projectId)
    val lineageTracker = new LineageTracker(spark, projectId)
    
    try {
      // Parse arguments
      val sourceTable = getArgValue(args, "--source-table", "raw.oracle_customers")
      val targetTable = getArgValue(args, "--target-table", "structured.customers")
      val processDate = getArgValue(args, "--process-date", "")
      
      auditLogger.logJobStart(jobId, "Raw-To-Structured", targetTable, "TRANSFORMATION")
      
      // Read from raw zone
      var rawData = icebergManager.readFromIceberg(sourceTable)
      
      // Filter by processing date if specified
      if (processDate.nonEmpty) {
        rawData = rawData.filter(col("_partition_date") === processDate)
      }
      
      val recordCount = rawData.count()
      println(s"Processing $recordCount records from $sourceTable")
      
      // Data transformations
      val structuredData = rawData
        // Standardize column names
        .withColumnRenamed("CUSTOMER_ID", "customer_id")
        .withColumnRenamed("FIRST_NAME", "first_name")
        .withColumnRenamed("LAST_NAME", "last_name")
        .withColumnRenamed("EMAIL_ADDRESS", "email")
        .withColumnRenamed("PHONE_NUMBER", "phone")
        .withColumnRenamed("CREATED_DATE", "created_date")
        .withColumnRenamed("LAST_UPDATED", "last_updated")
        
        // Data type conversions
        .withColumn("customer_id", col("customer_id").cast(LongType))
        .withColumn("created_date", to_timestamp(col("created_date"), "yyyy-MM-dd HH:mm:ss"))
        .withColumn("last_updated", to_timestamp(col("last_updated"), "yyyy-MM-dd HH:mm:ss"))
        
        // Data cleansing
        .withColumn("first_name", trim(upper(col("first_name"))))
        .withColumn("last_name", trim(upper(col("last_name"))))
        .withColumn("email", trim(lower(col("email"))))
        .withColumn("phone", regexp_replace(col("phone"), "[^0-9]", ""))
        
        // Add derived columns
        .withColumn("full_name", concat_ws(" ", col("first_name"), col("last_name")))
        .withColumn("email_domain", split(col("email"), "@").getItem(1))
        .withColumn("phone_formatted", 
          when(length(col("phone")) === 10, 
            concat(lit("("), substring(col("phone"), 1, 3), lit(") "),
                   substring(col("phone"), 4, 3), lit("-"),
                   substring(col("phone"), 7, 4))
          ).otherwise(col("phone"))
        )
        
        // Add business flags
        .withColumn("is_valid_email", col("email").rlike("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"))
        .withColumn("is_recent_customer", 
          datediff(current_date(), col("created_date")) <= 365
        )
        
        // Add processing metadata
        .withColumn("_processed_timestamp", current_timestamp())
        .withColumn("_data_quality_score", 
          (when(col("is_valid_email"), 1).otherwise(0) +
           when(col("phone").isNotNull && length(col("phone")) === 10, 1).otherwise(0) +
           when(col("first_name").isNotNull && col("last_name").isNotNull, 1).otherwise(0)
          ) / 3.0
        )
        
        // Select final columns
        .select(
          col("customer_id"),
          col("first_name"),
          col("last_name"),
          col("full_name"),
          col("email"),
          col("email_domain"),
          col("phone"),
          col("phone_formatted"),
          col("created_date"),
          col("last_updated"),
          col("is_valid_email"),
          col("is_recent_customer"),
          col("_data_quality_score"),
          col("_source_system"),
          col("_source_table"),
          col("_ingestion_timestamp"),
          col("_processed_timestamp"),
          col("_partition_date")
        )
      
      // Validate structured data
      val structuredValidationRules = Seq(
        ValidationRule("unique_customer_id", "Customer ID should be unique", "COUNT(*) = COUNT(DISTINCT customer_id)"),
        ValidationRule("valid_customer_id", "Customer ID should not be null", "customer_id IS NOT NULL"),
        ValidationRule("valid_name", "First and last name should not be null", "first_name IS NOT NULL AND last_name IS NOT NULL"),
        ValidationRule("quality_threshold", "Data quality score should be above 0.5", "_data_quality_score >= 0.5")
      )
      
      val validationResults = validationEngine.validateData(structuredData, structuredValidationRules, targetTable)
      
      validationResults.foreach { result =>
        println(s"Validation: ${result.ruleName} - ${if (result.passed) "PASSED" else "FAILED"}: ${result.message}")
      }
      
      // Filter out low quality records
      val qualityData = structuredData.filter(col("_data_quality_score") >= 0.5)
      val finalRecordCount = qualityData.count()
      
      println(s"After quality filtering: $finalRecordCount records (${recordCount - finalRecordCount} records filtered out)")
      
      // Write to structured zone
      icebergManager.writeToIceberg(
        df = qualityData,
        tableName = targetTable,
        writeMode = "overwrite",
        partitionCols = Seq("_partition_date")
      )
      
      // Track column-level lineage
      lineageTracker.trackColumnLineage(
        sourceTable = sourceTable,
        targetTable = targetTable,
        transformation = "raw_to_structured",
        columns = Seq("customer_id", "first_name", "last_name", "email", "phone", "created_date"),
        jobId = jobId
      )
      
      auditLogger.logJobCompletion(
        jobId = jobId,
        jobName = "Raw-To-Structured",
        tableName = targetTable,
        operation = "TRANSFORMATION",
        recordsProcessed = finalRecordCount,
        startTime = startTime,
        status = "COMPLETED",
        metadata = Map(
          "source_records" -> recordCount.toString,
          "filtered_records" -> (recordCount - finalRecordCount).toString,
          "data_quality_threshold" -> "0.5"
        )
      )
      
      println(s"Successfully transformed $finalRecordCount records to $targetTable")
      
    } catch {
      case e: Exception =>
        auditLogger.logJobCompletion(
          jobId = jobId,
          jobName = "Raw-To-Structured",
          tableName = args.find(_.startsWith("--target-table")).map(_.split("=", 2)(1)).getOrElse("unknown"),
          operation = "TRANSFORMATION",
          recordsProcessed = 0,
          startTime = startTime,
          status = "FAILED",
          errorMessage = Some(e.getMessage)
        )
        
        println(s"Transformation failed: ${e.getMessage}")
        e.printStackTrace()
        throw e
    } finally {
      spark.stop()
    }
  }
  
  private def getArgValue(args: Array[String], key: String, default: String): String = {
    args.find(_.startsWith(s"$key="))
      .map(_.split("=", 2)(1))
      .getOrElse(default)
  }
}