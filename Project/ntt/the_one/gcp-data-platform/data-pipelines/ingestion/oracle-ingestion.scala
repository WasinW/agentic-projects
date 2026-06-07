package com.dataplatform.pipelines.ingestion

import org.apache.spark.sql.SparkSession
import com.dataplatform.core._
import com.dataplatform.monitoring._
import java.time.Instant
import java.util.UUID

object OracleIngestion {
  
  def main(args: Array[String]): Unit = {
    
    val spark = SparkSession.builder()
      .appName("Oracle-Ingestion")
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
    val dbConnector = new DatabaseConnector(spark)
    val icebergManager = new IcebergManager(spark)
    val validationEngine = new ValidationEngine(spark)
    val auditLogger = new AuditLogger(spark, projectId)
    val lineageTracker = new LineageTracker(spark, projectId)
    
    try {
      // Parse arguments
      val sourceTable = getArgValue(args, "--source-table", "customers")
      val targetTable = getArgValue(args, "--target-table", "raw.oracle_customers")
      val secretId = getArgValue(args, "--secret-id", "oracle-db-credentials")
      val partitionDate = getArgValue(args, "--partition-date", "")
      
      auditLogger.logJobStart(jobId, "Oracle-Ingestion", targetTable, "FULL_LOAD")
      
      // Build query with partition condition
      val baseQuery = s"SELECT * FROM $sourceTable"
      val query = if (partitionDate.nonEmpty) {
        s"$baseQuery WHERE DATE(created_date) = '$partitionDate'"
      } else {
        baseQuery
      }
      
      println(s"Executing query: $query")
      
      // Extract data from Oracle
      val oracleData = dbConnector.connectAndQuery(
        projectId = projectId,
        secretId = secretId,
        query = query
      )
      
      val recordCount = oracleData.count()
      println(s"Extracted $recordCount records from Oracle")
      
      // Validate data
      val validationRules = validationEngine.getStandardValidationRules
      val validationResults = validationEngine.validateData(oracleData, validationRules, sourceTable)
      
      validationResults.foreach { result =>
        println(s"Validation: ${result.ruleName} - ${if (result.passed) "PASSED" else "FAILED"}: ${result.message}")
      }
      
      // Check if any critical validations failed
      val criticalFailures = validationResults.filter(r => !r.passed && r.severity == "ERROR")
      if (criticalFailures.nonEmpty) {
        throw new RuntimeException(s"Critical validation failures: ${criticalFailures.map(_.message).mkString("; ")}")
      }
      
      // Add metadata and standardize
      val processedData = oracleData
        .withColumn("_ingestion_timestamp", current_timestamp())
        .withColumn("_source_system", lit("oracle"))
        .withColumn("_source_table", lit(sourceTable))
        .withColumn("_partition_date", 
          if (partitionDate.nonEmpty) lit(partitionDate) else current_date())
      
      // Write to Iceberg raw zone
      icebergManager.writeToIceberg(
        df = processedData,
        tableName = targetTable,
        writeMode = "append",
        partitionCols = Seq("_partition_date")
      )
      
      // Track lineage
      lineageTracker.trackTableLineage(
        sourceTable = s"oracle.$sourceTable",
        targetTable = targetTable,
        transformation = "full_load_ingestion",
        jobId = jobId
      )
      
      auditLogger.logJobCompletion(
        jobId = jobId,
        jobName = "Oracle-Ingestion",
        tableName = targetTable,
        operation = "FULL_LOAD",
        recordsProcessed = recordCount,
        startTime = startTime,
        status = "COMPLETED"
      )
      
      println(s"Successfully ingested $recordCount records to $targetTable")
      
    } catch {
      case e: Exception =>
        auditLogger.logJobCompletion(
          jobId = jobId,
          jobName = "Oracle-Ingestion",
          tableName = args.find(_.startsWith("--target-table")).map(_.split("=", 2)(1)).getOrElse("unknown"),
          operation = "FULL_LOAD",
          recordsProcessed = 0,
          startTime = startTime,
          status = "FAILED",
          errorMessage = Some(e.getMessage)
        )
        
        println(s"Job failed: ${e.getMessage}")
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