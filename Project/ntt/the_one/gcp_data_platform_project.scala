// ===============================
// PROJECT STRUCTURE
// ===============================
/*
gcp-data-platform/
├── backend-service/
│   ├── src/main/scala/
│   │   └── com/dataplatform/
│   │       ├── core/
│   │       │   ├── DatabaseConnector.scala
│   │       │   ├── SecretManager.scala
│   │       │   ├── FileProcessor.scala
│   │       │   ├── IcebergManager.scala
│   │       │   └── ValidationEngine.scala
│   │       ├── ingestion/
│   │       │   ├── BatchIngestion.scala
│   │       │   ├── CDCProcessor.scala
│   │       │   └── FileIngestion.scala
│   │       ├── transformation/
│   │       │   ├── DataTransformer.scala
│   │       │   └── DataQuality.scala
│   │       ├── monitoring/
│   │       │   ├── AuditLogger.scala
│   │       │   ├── LineageTracker.scala
│   │       │   └── MetricsCollector.scala
│   │       └── config/
│   │           └── ConfigManager.scala
│   ├── src/main/resources/
│   │   └── application.conf
│   └── build.sbt
├── data-pipelines/
│   ├── ingestion/
│   │   ├── oracle-ingestion.scala
│   │   ├── postgres-ingestion.scala
│   │   ├── file-ingestion.scala
│   │   └── kafka-ingestion.scala
│   ├── transformation/
│   │   ├── raw-to-structured.scala
│   │   ├── structured-to-refined.scala
│   │   └── refined-to-analysis.scala
│   └── validation/
│       └── data-quality-check.scala
├── dataflow-templates/
│   ├── cdc-realtime-processor/
│   └── file-streaming-processor/
├── dataform-pipelines/
│   ├── real-time-analytics/
│   └── materialized-views/
├── deployment/
│   ├── terraform/
│   ├── scripts/
│   └── configs/
├── monitoring/
│   ├── dashboards/
│   └── alerts/
└── docs/
    ├── deployment-guide.md
    ├── pipeline-guide.md
    └── troubleshooting.md
*/

// ===============================
// BACKEND SERVICE CORE
// ===============================

// File: backend-service/src/main/scala/com/dataplatform/core/SecretManager.scala
package com.dataplatform.core

import com.google.cloud.secretmanager.v1.{SecretManagerServiceClient, SecretVersionName}
import scala.util.{Try, Success, Failure}

case class DatabaseCredentials(
  url: String,
  username: String,
  password: String,
  driver: String
)

object SecretManager {
  
  def getSecret(projectId: String, secretId: String, versionId: String = "latest"): String = {
    val client = SecretManagerServiceClient.create()
    
    try {
      val secretVersionName = SecretVersionName.of(projectId, secretId, versionId)
      val response = client.accessSecretVersion(secretVersionName)
      val secretValue = response.getPayload.getData.toStringUtf8
      
      client.close()
      secretValue
    } catch {
      case e: Exception =>
        client.close()
        throw new RuntimeException(s"Failed to get secret $secretId: ${e.getMessage}", e)
    }
  }
  
  def getDatabaseCredentials(projectId: String, secretId: String): DatabaseCredentials = {
    val secretJson = getSecret(projectId, secretId)
    parseJsonCredentials(secretJson)
  }
  
  private def parseJsonCredentials(jsonString: String): DatabaseCredentials = {
    // Simple JSON parsing - in production use circe or play-json
    val lines = jsonString.split("\n").map(_.trim).filter(_.nonEmpty)
    
    var url = ""
    var username = ""
    var password = ""
    var driver = ""
    
    lines.foreach { line =>
      if (line.contains("\"url\"")) {
        url = extractJsonValue(line)
      } else if (line.contains("\"username\"")) {
        username = extractJsonValue(line)
      } else if (line.contains("\"password\"")) {
        password = extractJsonValue(line)
      } else if (line.contains("\"driver\"")) {
        driver = extractJsonValue(line)
      }
    }
    
    DatabaseCredentials(url, username, password, driver)
  }
  
  private def extractJsonValue(line: String): String = {
    val parts = line.split(":")
    if (parts.length >= 2) {
      parts(1).trim.replaceAll("[\",]", "")
    } else ""
  }
}

// File: backend-service/src/main/scala/com/dataplatform/core/DatabaseConnector.scala
package com.dataplatform.core

import org.apache.spark.sql.{DataFrame, SparkSession}
import java.util.Properties

class DatabaseConnector(spark: SparkSession) {
  
  def connectAndQuery(
    projectId: String,
    secretId: String,
    query: String,
    fetchSize: Int = 10000
  ): DataFrame = {
    
    val credentials = SecretManager.getDatabaseCredentials(projectId, secretId)
    
    val connectionProperties = new Properties()
    connectionProperties.put("user", credentials.username)
    connectionProperties.put("password", credentials.password)
    connectionProperties.put("driver", credentials.driver)
    connectionProperties.put("fetchsize", fetchSize.toString)
    
    // For Oracle specific optimizations
    if (credentials.driver.contains("oracle")) {
      connectionProperties.put("oracle.jdbc.timezoneAsRegion", "false")
      connectionProperties.put("oracle.net.disableOob", "true")
    }
    
    spark.read
      .jdbc(credentials.url, s"($query) as subquery", connectionProperties)
  }
  
  def connectAndQueryTable(
    projectId: String,
    secretId: String,
    tableName: String,
    conditions: Option[String] = None,
    partitionColumn: Option[String] = None,
    lowerBound: Option[String] = None,
    upperBound: Option[String] = None,
    numPartitions: Int = 4
  ): DataFrame = {
    
    val credentials = SecretManager.getDatabaseCredentials(projectId, secretId)
    
    val connectionProperties = new Properties()
    connectionProperties.put("user", credentials.username)
    connectionProperties.put("password", credentials.password)
    connectionProperties.put("driver", credentials.driver)
    
    val finalTableName = conditions match {
      case Some(cond) => s"(SELECT * FROM $tableName WHERE $cond) as filtered_table"
      case None => tableName
    }
    
    partitionColumn match {
      case Some(partCol) if lowerBound.isDefined && upperBound.isDefined =>
        spark.read
          .jdbc(
            url = credentials.url,
            table = finalTableName,
            columnName = partCol,
            lowerBound = lowerBound.get.toLong,
            upperBound = upperBound.get.toLong,
            numPartitions = numPartitions,
            connectionProperties = connectionProperties
          )
      case _ =>
        spark.read
          .jdbc(credentials.url, finalTableName, connectionProperties)
    }
  }
  
  def writeToDatabase(
    df: DataFrame,
    projectId: String,
    secretId: String,
    tableName: String,
    mode: String = "append"
  ): Unit = {
    
    val credentials = SecretManager.getDatabaseCredentials(projectId, secretId)
    
    val connectionProperties = new Properties()
    connectionProperties.put("user", credentials.username)
    connectionProperties.put("password", credentials.password)
    connectionProperties.put("driver", credentials.driver)
    
    df.write
      .mode(mode)
      .jdbc(credentials.url, tableName, connectionProperties)
  }
}

// File: backend-service/src/main/scala/com/dataplatform/core/FileProcessor.scala
package com.dataplatform.core

import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.types._
import org.apache.spark.sql.functions._

class FileProcessor(spark: SparkSession) {
  
  def processExcelFile(
    filePath: String,
    sheetName: Option[String] = None,
    header: Boolean = true
  ): DataFrame = {
    
    val reader = spark.read
      .format("com.crealytics.spark.excel")
      .option("header", header.toString)
      .option("inferSchema", "true")
      .option("treatEmptyValuesAsNulls", "true")
    
    sheetName match {
      case Some(sheet) => reader.option("dataAddress", s"'$sheet'!A1").load(filePath)
      case None => reader.load(filePath)
    }
  }
  
  def processCSVFile(
    filePath: String,
    delimiter: String = ",",
    header: Boolean = true,
    schema: Option[StructType] = None
  ): DataFrame = {
    
    val reader = spark.read
      .option("header", header.toString)
      .option("delimiter", delimiter)
      .option("multiline", "true")
      .option("escape", "\"")
      .option("timestampFormat", "yyyy-MM-dd HH:mm:ss")
      .option("dateFormat", "yyyy-MM-dd")
    
    schema match {
      case Some(s) => reader.schema(s).csv(filePath)
      case None => reader.option("inferSchema", "true").csv(filePath)
    }
  }
  
  def processJSONFile(
    filePath: String,
    multiLine: Boolean = false,
    schema: Option[StructType] = None
  ): DataFrame = {
    
    val reader = spark.read
      .option("multiline", multiLine.toString)
      .option("timestampFormat", "yyyy-MM-dd HH:mm:ss")
    
    schema match {
      case Some(s) => reader.schema(s).json(filePath)
      case None => reader.json(filePath)
    }
  }
  
  def processTextFile(
    filePath: String,
    delimiter: String = "\t"
  ): DataFrame = {
    
    spark.read
      .option("delimiter", delimiter)
      .option("header", "false")
      .csv(filePath)
  }
  
  def standardizeDataFrame(
    df: DataFrame,
    addMetadata: Boolean = true
  ): DataFrame = {
    
    var result = df
    
    // Add standard metadata columns
    if (addMetadata) {
      result = result
        .withColumn("_ingestion_timestamp", current_timestamp())
        .withColumn("_source_file", input_file_name())
        .withColumn("_processing_date", current_date())
    }
    
    // Standardize column names
    val standardizedColumns = result.columns.map { col =>
      val newName = col.toLowerCase
        .replaceAll("[\\s-]+", "_")
        .replaceAll("[^a-z0-9_]", "")
      result.col(col).alias(newName)
    }
    
    result.select(standardizedColumns: _*)
  }
}

// File: backend-service/src/main/scala/com/dataplatform/core/IcebergManager.scala
package com.dataplatform.core

import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._

class IcebergManager(spark: SparkSession) {
  
  def writeToIceberg(
    df: DataFrame,
    tableName: String,
    writeMode: String = "append",
    partitionCols: Seq[String] = Seq.empty,
    mergeCondition: Option[String] = None
  ): Unit = {
    
    val writer = df.write
      .format("iceberg")
      .mode(writeMode)
    
    // Add partitioning if specified
    if (partitionCols.nonEmpty) {
      writer.partitionBy(partitionCols: _*)
    }
    
    writeMode.toLowerCase match {
      case "merge" if mergeCondition.isDefined =>
        // Use merge operation for upserts
        df.writeTo(tableName)
          .using("iceberg")
          .createOrReplace()
      case _ =>
        writer.saveAsTable(tableName)
    }
  }
  
  def readFromIceberg(
    tableName: String,
    snapshotId: Option[Long] = None,
    asOfTimestamp: Option[String] = None
  ): DataFrame = {
    
    val reader = spark.read.format("iceberg")
    
    // Time travel capabilities
    snapshotId.foreach(id => reader.option("snapshot-id", id.toString))
    asOfTimestamp.foreach(ts => reader.option("as-of-timestamp", ts))
    
    reader.table(tableName)
  }
  
  def createIcebergTable(
    tableName: String,
    df: DataFrame,
    partitionCols: Seq[String] = Seq.empty,
    tableProperties: Map[String, String] = Map.empty
  ): Unit = {
    
    var ddl = s"CREATE TABLE IF NOT EXISTS $tableName ("
    
    // Add column definitions
    val columnDefs = df.schema.fields.map { field =>
      s"${field.name} ${field.dataType.sql}"
    }.mkString(", ")
    
    ddl += columnDefs + ")"
    
    // Add partitioning
    if (partitionCols.nonEmpty) {
      val partitionSpec = partitionCols.mkString(", ")
      ddl += s" PARTITIONED BY ($partitionSpec)"
    }
    
    // Add table properties
    if (tableProperties.nonEmpty) {
      val props = tableProperties.map { case (k, v) => s"'$k'='$v'" }.mkString(", ")
      ddl += s" TBLPROPERTIES ($props)"
    }
    
    spark.sql(ddl)
  }
  
  def optimizeIcebergTable(tableName: String): Unit = {
    // Compact small files
    spark.sql(s"CALL iceberg.system.rewrite_data_files('$tableName')")
    
    // Update table statistics
    spark.sql(s"ANALYZE TABLE $tableName COMPUTE STATISTICS FOR ALL COLUMNS")
  }
}

// File: backend-service/src/main/scala/com/dataplatform/core/ValidationEngine.scala
package com.dataplatform.core

import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

case class ValidationRule(
  name: String,
  description: String,
  expression: String,
  severity: String = "ERROR" // ERROR, WARNING, INFO
)

case class ValidationResult(
  ruleName: String,
  passed: Boolean,
  failedRecords: Long,
  totalRecords: Long,
  severity: String,
  message: String
)

class ValidationEngine(spark: SparkSession) {
  
  def validateData(
    df: DataFrame,
    rules: Seq[ValidationRule],
    tableName: String
  ): Seq[ValidationResult] = {
    
    val totalRecords = df.count()
    
    rules.map { rule =>
      try {
        // Apply validation rule
        val validDF = df.filter(rule.expression)
        val validRecords = validDF.count()
        val failedRecords = totalRecords - validRecords
        
        val passed = failedRecords == 0
        val message = if (passed) {
          s"Validation passed: ${rule.description}"
        } else {
          s"Validation failed: ${rule.description}. $failedRecords out of $totalRecords records failed."
        }
        
        ValidationResult(
          ruleName = rule.name,
          passed = passed,
          failedRecords = failedRecords,
          totalRecords = totalRecords,
          severity = rule.severity,
          message = message
        )
        
      } catch {
        case e: Exception =>
          ValidationResult(
            ruleName = rule.name,
            passed = false,
            failedRecords = totalRecords,
            totalRecords = totalRecords,
            severity = "ERROR",
            message = s"Validation rule execution failed: ${e.getMessage}"
          )
      }
    }
  }
  
  def validateSchema(df: DataFrame, expectedSchema: StructType): ValidationResult = {
    val actualSchema = df.schema
    
    val missingFields = expectedSchema.fields.filterNot { expectedField =>
      actualSchema.fields.exists(_.name == expectedField.name)
    }
    
    val extraFields = actualSchema.fields.filterNot { actualField =>
      expectedSchema.fields.exists(_.name == actualField.name)
    }
    
    val typeMismatches = expectedSchema.fields.filter { expectedField =>
      actualSchema.fields.find(_.name == expectedField.name) match {
        case Some(actualField) => actualField.dataType != expectedField.dataType
        case None => false
      }
    }
    
    val passed = missingFields.isEmpty && extraFields.isEmpty && typeMismatches.isEmpty
    
    val message = if (passed) {
      "Schema validation passed"
    } else {
      val issues = Seq(
        if (missingFields.nonEmpty) s"Missing fields: ${missingFields.map(_.name).mkString(", ")}" else "",
        if (extraFields.nonEmpty) s"Extra fields: ${extraFields.map(_.name).mkString(", ")}" else "",
        if (typeMismatches.nonEmpty) s"Type mismatches: ${typeMismatches.map(_.name).mkString(", ")}" else ""
      ).filter(_.nonEmpty)
      
      s"Schema validation failed: ${issues.mkString("; ")}"
    }
    
    ValidationResult(
      ruleName = "schema_validation",
      passed = passed,
      failedRecords = if (passed) 0 else df.count(),
      totalRecords = df.count(),
      severity = "ERROR",
      message = message
    )
  }
  
  def getStandardValidationRules: Seq[ValidationRule] = Seq(
    ValidationRule("not_null_id", "ID field should not be null", "id IS NOT NULL"),
    ValidationRule("positive_amounts", "Amount fields should be positive", "amount > 0"),
    ValidationRule("valid_dates", "Dates should be valid and not in future", "date_column <= current_date()"),
    ValidationRule("no_duplicates", "Records should not have duplicates", "COUNT(*) = COUNT(DISTINCT id)")
  )
}

// File: backend-service/src/main/scala/com/dataplatform/monitoring/AuditLogger.scala
package com.dataplatform.monitoring

import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import java.time.Instant

case class AuditLog(
  jobId: String,
  jobName: String,
  tableName: String,
  operation: String,
  recordsProcessed: Long,
  startTime: Instant,
  endTime: Instant,
  status: String,
  errorMessage: Option[String] = None,
  metadata: Map[String, String] = Map.empty
)

class AuditLogger(spark: SparkSession, projectId: String) {
  
  def logJobStart(
    jobId: String,
    jobName: String,
    tableName: String,
    operation: String,
    metadata: Map[String, String] = Map.empty
  ): Unit = {
    
    val auditLog = AuditLog(
      jobId = jobId,
      jobName = jobName,
      tableName = tableName,
      operation = operation,
      recordsProcessed = 0,
      startTime = Instant.now(),
      endTime = Instant.now(),
      status = "STARTED",
      metadata = metadata
    )
    
    writeAuditLog(auditLog)
  }
  
  def logJobCompletion(
    jobId: String,
    jobName: String,
    tableName: String,
    operation: String,
    recordsProcessed: Long,
    startTime: Instant,
    status: String = "COMPLETED",
    errorMessage: Option[String] = None,
    metadata: Map[String, String] = Map.empty
  ): Unit = {
    
    val auditLog = AuditLog(
      jobId = jobId,
      jobName = jobName,
      tableName = tableName,
      operation = operation,
      recordsProcessed = recordsProcessed,
      startTime = startTime,
      endTime = Instant.now(),
      status = status,
      errorMessage = errorMessage,
      metadata = metadata
    )
    
    writeAuditLog(auditLog)
  }
  
  private def writeAuditLog(auditLog: AuditLog): Unit = {
    import spark.implicits._
    
    val auditDF = Seq(auditLog).toDF()
    
    // Write to BigQuery audit table
    auditDF.write
      .format("bigquery")
      .option("table", s"$projectId.monitoring.audit_logs")
      .option("writeMethod", "direct")
      .mode("append")
      .save()
  }
  
  def getJobHistory(jobName: String, days: Int = 30): DataFrame = {
    spark.read
      .format("bigquery")
      .option("table", s"$projectId.monitoring.audit_logs")
      .load()
      .filter(
        col("job_name") === jobName &&
        col("start_time") >= date_sub(current_date(), days)
      )
      .orderBy(desc("start_time"))
  }
}

// File: backend-service/src/main/scala/com/dataplatform/monitoring/LineageTracker.scala
package com.dataplatform.monitoring

import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import java.time.Instant

case class DataLineage(
  sourceTable: String,
  targetTable: String,
  transformation: String,
  columns: Seq[String],
  timestamp: Instant,
  jobId: String,
  level: String // TABLE, COLUMN, ROW
)

class LineageTracker(spark: SparkSession, projectId: String) {
  
  def trackTableLineage(
    sourceTable: String,
    targetTable: String,
    transformation: String,
    jobId: String
  ): Unit = {
    
    val lineage = DataLineage(
      sourceTable = sourceTable,
      targetTable = targetTable,
      transformation = transformation,
      columns = Seq.empty,
      timestamp = Instant.now(),
      jobId = jobId,
      level = "TABLE"
    )
    
    writeLineage(lineage)
  }
  
  def trackColumnLineage(
    sourceTable: String,
    targetTable: String,
    transformation: String,
    columns: Seq[String],
    jobId: String
  ): Unit = {
    
    val lineage = DataLineage(
      sourceTable = sourceTable,
      targetTable = targetTable,
      transformation = transformation,
      columns = columns,
      timestamp = Instant.now(),
      jobId = jobId,
      level = "COLUMN"
    )
    
    writeLineage(lineage)
  }
  
  def trackRowLineage(
    sourceTable: String,
    targetTable: String,
    transformation: String,
    rowIdentifiers: Seq[String],
    jobId: String
  ): Unit = {
    
    val lineage = DataLineage(
      sourceTable = sourceTable,
      targetTable = targetTable,
      transformation = transformation,
      columns = rowIdentifiers,
      timestamp = Instant.now(),
      jobId = jobId,
      level = "ROW"
    )
    
    writeLineage(lineage)
  }
  
  private def writeLineage(lineage: DataLineage): Unit = {
    import spark.implicits._
    
    val lineageDF = Seq(lineage).toDF()
    
    // Write to BigQuery lineage table
    lineageDF.write
      .format("bigquery")
      .option("table", s"$projectId.monitoring.data_lineage")
      .option("writeMethod", "direct")
      .mode("append")
      .save()
  }
  
  def getLineageForTable(tableName: String): DataFrame = {
    spark.read
      .format("bigquery")
      .option("table", s"$projectId.monitoring.data_lineage")
      .load()
      .filter(
        col("source_table") === tableName || 
        col("target_table") === tableName
      )
      .orderBy(desc("timestamp"))
  }
}

// File: backend-service/build.sbt
ThisBuild / scalaVersion := "2.12.17"
ThisBuild / version := "1.0.0"

lazy val backendService = (project in file("."))
  .settings(
    name := "data-platform-backend",
    assembly / mainClass := Some("com.dataplatform.DataPlatformService"),
    libraryDependencies ++= Seq(
      // Spark dependencies
      "org.apache.spark" %% "spark-core" % "3.5.0" % "provided",
      "org.apache.spark" %% "spark-sql" % "3.5.0" % "provided",
      
      // Google Cloud dependencies
      "com.google.cloud" % "google-cloud-secretmanager" % "2.63.0",
      "com.google.cloud" % "google-cloud-storage" % "2.63.0",
      
      // Database drivers
      "com.oracle.database.jdbc" % "ojdbc8" % "21.9.0.0",
      "org.postgresql" % "postgresql" % "42.7.1",
      "mysql" % "mysql-connector-java" % "8.0.33",
      
      // Iceberg
      "org.apache.iceberg" % "iceberg-spark-runtime-3.5_2.12" % "1.4.3",
      
      // File formats
      "com.crealytics" %% "spark-excel" % "3.5.1_0.20.3",
      
      // BigQuery
      "com.google.cloud.spark" %% "spark-bigquery-with-dependencies" % "0.32.2",
      
      // Testing
      "org.scalatest" %% "scalatest" % "3.2.15" % Test
    ),
    
    assembly / assemblyMergeStrategy := {
      case PathList("META-INF", xs @ _*) => MergeStrategy.discard
      case "application.conf" => MergeStrategy.concat
      case x => MergeStrategy.first
    }
  )

// ===============================
// SAMPLE PIPELINE SCRIPTS
// ===============================

// File: data-pipelines/ingestion/oracle-ingestion.scala
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

// File: data-pipelines/ingestion/cdc-processor.scala
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

// File: data-pipelines/transformation/raw-to-structured.scala
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

// File: deployment/scripts/build-and-deploy.sh
#!/bin/bash

set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}
BUCKET_NAME=${GCS_BUCKET:-"your-data-platform-bucket"}
BACKEND_SERVICE_JAR="data-platform-backend-assembly-1.0.0.jar"

echo "=== GCP Data Platform Build and Deployment ==="
echo "Project ID: $PROJECT_ID"
echo "GCS Bucket: $BUCKET_NAME"

# Build backend service JAR
echo "Building backend service..."
cd backend-service
sbt clean assembly
echo "Backend service built successfully"

# Upload JAR to GCS
echo "Uploading backend service JAR to GCS..."
gsutil cp target/scala-2.12/$BACKEND_SERVICE_JAR gs://$BUCKET_NAME/jars/

# Upload pipeline scripts
echo "Uploading pipeline scripts..."
gsutil -m cp -r ../data-pipelines/* gs://$BUCKET_NAME/scripts/

# Upload Dataflow templates
echo "Uploading Dataflow templates..."
gsutil -m cp -r ../dataflow-templates/* gs://$BUCKET_NAME/dataflow-templates/

# Create BigQuery datasets
echo "Creating BigQuery datasets..."
bq mk --dataset --location=US $PROJECT_ID:raw
bq mk --dataset --location=US $PROJECT_ID:structured  
bq mk --dataset --location=US $PROJECT_ID:refined
bq mk --dataset --location=US $PROJECT_ID:analysis
bq mk --dataset --location=US $PROJECT_ID:monitoring

# Create monitoring tables
echo "Creating monitoring tables..."
bq query --use_legacy_sql=false "
CREATE TABLE IF NOT EXISTS \`$PROJECT_ID.monitoring.audit_logs\` (
  job_id STRING,
  job_name STRING,
  table_name STRING,
  operation STRING,
  records_processed INT64,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  status STRING,
  error_message STRING,
  metadata JSON
)
PARTITION BY DATE(start_time)
CLUSTER BY job_name, status"

bq query --use_legacy_sql=false "
CREATE TABLE IF NOT EXISTS \`$PROJECT_ID.monitoring.data_lineage\` (
  source_table STRING,
  target_table STRING,
  transformation STRING,
  columns ARRAY<STRING>,
  timestamp TIMESTAMP,
  job_id STRING,
  level STRING
)
PARTITION BY DATE(timestamp)
CLUSTER BY source_table, target_table"

# Create Dataproc cluster
echo "Creating Dataproc cluster..."
gcloud dataproc clusters create data-platform-cluster \
    --region=us-central1 \
    --zone=us-central1-a \
    --master-machine-type=n1-standard-4 \
    --master-boot-disk-size=50GB \
    --num-workers=2 \
    --worker-machine-type=n1-standard-4 \
    --worker-boot-disk-size=50GB \
    --image-version=2.1-debian11 \
    --enable-autoscaling \
    --max-workers=10 \
    --initialization-actions=gs://goog-dataproc-initialization-actions-us-central1/conda/bootstrap-conda.sh \
    --optional-components=ZEPPELIN \
    --enable-ip-alias \
    --metadata="enable-cloud-sql-hive-metastore=false" \
    --properties="spark:spark.serializer=org.apache.spark.serializer.KryoSerializer,spark:spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,spark:spark.sql.catalog.iceberg=org.apache.iceberg.spark.SparkCatalog,spark:spark.sql.catalog.iceberg.type=hadoop,spark:spark.sql.catalog.iceberg.warehouse=gs://$BUCKET_NAME/iceberg-warehouse"

echo "Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Configure your database credentials in Secret Manager"
echo "2. Update the configuration files with your specific settings"
echo "3. Run sample ingestion job: ./run-sample-ingestion.sh"

# File: deployment/scripts/run-sample-ingestion.sh
#!/bin/bash

set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}
BUCKET_NAME=${GCS_BUCKET:-"your-data-platform-bucket"}
CLUSTER_NAME=${DATAPROC_CLUSTER:-"data-platform-cluster"}
REGION=${DATAPROC_REGION:-"us-central1"}

echo "=== Running Sample Oracle Ingestion Job ==="

# Submit Oracle ingestion job
gcloud dataproc jobs submit spark \
    --cluster=$CLUSTER_NAME \
    --region=$REGION \
    --class=com.dataplatform.pipelines.ingestion.OracleIngestion \
    --jars=gs://$BUCKET_NAME/jars/data-platform-backend-assembly-1.0.0.jar \
    --properties="spark.executor.memory=4g,spark.driver.memory=2g,spark.executor.cores=2" \
    -- \
    --source-table=customers \
    --target-table=raw.oracle_customers \
    --secret-id=oracle-db-credentials \
    --partition-date=$(date +%Y-%m-%d)

echo "Oracle ingestion job submitted successfully!"

# Submit transformation job
echo "=== Running Raw to Structured Transformation ==="

gcloud dataproc jobs submit spark \
    --cluster=$CLUSTER_NAME \
    --region=$REGION \
    --class=com.dataplatform.pipelines.transformation.RawToStructured \
    --jars=gs://$BUCKET_NAME/jars/data-platform-backend-assembly-1.0.0.jar \
    --properties="spark.executor.memory=4g,spark.driver.memory=2g,spark.executor.cores=2" \
    -- \
    --source-table=raw.oracle_customers \
    --target-table=structured.customers \
    --process-date=$(date +%Y-%m-%d)

echo "Transformation job submitted successfully!"
echo ""
echo "Monitor job progress in the GCP Console:"
echo "https://console.cloud.google.com/dataproc/jobs?project=$PROJECT_ID&region=$REGION"

# File: docs/deployment-guide.md

# GCP Data Platform Deployment Guide

## Prerequisites

### 1. GCP Setup
- GCP Project with billing enabled
- Required APIs enabled:
  - Dataproc API
  - BigQuery API  
  - Cloud Storage API
  - Secret Manager API
  - Dataflow API

### 2. Tools Installation
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Install sbt
echo "deb https://repo.scala-sbt.org/scalasbt/debian all main" | sudo tee /etc/apt/sources.list.d/sbt.list
curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | sudo apt-key add
sudo apt-get update
sudo apt-get install sbt
```

### 3. Authentication
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default login
```

## Deployment Steps

### Step 1: Environment Setup
```bash
# Set environment variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GCS_BUCKET="your-data-platform-bucket"
export DATAPROC_REGION="us-central1"

# Create GCS bucket
gsutil mb gs://$GCS_BUCKET

# Enable required APIs
gcloud services enable dataproc.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable dataflow.googleapis.com
```

### Step 2: Secret Manager Setup
```bash
# Create database credentials secret
echo '{
  "url": "jdbc:oracle:thin:@your-oracle-host:1521:XE",
  "username": "your_username", 
  "password": "your_password",
  "driver": "oracle.jdbc.driver.OracleDriver"
}' | gcloud secrets create oracle-db-credentials --data-file=-

# Create PostgreSQL credentials
echo '{
  "url": "jdbc:postgresql://your-postgres-host:5432/your_db",
  "username": "your_username",
  "password": "your_password", 
  "driver": "org.postgresql.Driver"
}' | gcloud secrets create postgres-db-credentials --data-file=-
```

### Step 3: Build and Deploy
```bash
# Run automated deployment
chmod +x deployment/scripts/build-and-deploy.sh
./deployment/scripts/build-and-deploy.sh
```

### Step 4: Manual Verification
```bash
# Check if JAR was uploaded
gsutil ls gs://$GCS_BUCKET/jars/

# Check BigQuery datasets
bq ls

# Check Dataproc cluster
gcloud dataproc clusters list --region=$DATAPROC_REGION
```

### Step 5: Run Sample Pipeline
```bash
chmod +x deployment/scripts/run-sample-ingestion.sh
./deployment/scripts/run-sample-ingestion.sh
```

## Configuration Files

### application.conf
```hocon
dataplatform {
  project-id = ${GOOGLE_CLOUD_PROJECT}
  gcs-bucket = ${GCS_BUCKET}
  
  iceberg {
    warehouse = "gs://"${dataplatform.gcs-bucket}"/iceberg-warehouse"
    catalog-type = "hadoop"
  }
  
  monitoring {
    audit-table = ${dataplatform.project-id}".monitoring.audit_logs"
    lineage-table = ${dataplatform.project-id}".monitoring.data_lineage"
  }
  
  validation {
    quality-threshold = 0.5
    max-error-rate = 0.1
  }
}
```

## Troubleshooting

### Common Issues

#### 1. JAR Assembly Failures
```bash
# Clear sbt cache
sbt clean
rm -rf ~/.sbt
rm -rf ~/.ivy2

# Rebuild
sbt assembly
```

#### 2. Dataproc Job Failures
```bash
# Check logs
gcloud dataproc jobs describe JOB_ID --region=$DATAPROC_REGION

# SSH to cluster for debugging
gcloud dataproc clusters describe CLUSTER_NAME --region=$DATAPROC_REGION
```

#### 3. Secret Manager Access
```bash
# Grant Secret Manager access to Dataproc service account
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

#### 4. BigQuery Permissions
```bash
# Grant BigQuery access
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"
```

## Monitoring Setup

### Cloud Monitoring Dashboard
```bash
# Create custom dashboard
gcloud monitoring dashboards create --config-from-file=monitoring/dashboard-config.yaml
```

### Log-based Metrics
```bash
# Create log-based metrics for job monitoring
gcloud logging metrics create job_success_rate \
    --description="Success rate of data pipeline jobs" \
    --log-filter='resource.type="dataproc_cluster" AND textPayload:"Successfully"'
```

## Performance Tuning

### Dataproc Cluster Optimization
```bash
# For large workloads, use high-memory machines
gcloud dataproc clusters create large-cluster \
    --master-machine-type=n1-highmem-8 \
    --worker-machine-type=n1-highmem-8 \
    --num-workers=5 \
    --preemptible-workers=10
```

### Spark Configuration
```bash
# For memory-intensive jobs
--properties="spark.executor.memory=14g,spark.driver.memory=4g,spark.executor.cores=4,spark.sql.adaptive.enabled=true,spark.sql.adaptive.coalescePartitions.enabled=true"
```

# File: docs/pipeline-guide.md

# Pipeline Development Guide

## Pipeline Types

### 1. Ingestion Pipelines

#### Full Load Ingestion
```scala
// Usage example
gcloud dataproc jobs submit spark \
    --cluster=data-platform-cluster \
    --region=us-central1 \
    --class=com.dataplatform.pipelines.ingestion.OracleIngestion \
    --jars=gs://bucket/jars/data-platform-backend-assembly-1.0.0.jar \
    -- \
    --source-table=customers \
    --target-table=raw.oracle_customers \
    --secret-id=oracle-db-credentials \
    --partition-date=2024-01-01
```

#### CDC Streaming
```scala
// Real-time CDC processing
gcloud dataproc jobs submit spark \
    --cluster=data-platform-cluster \
    --region=us-central1 \
    --class=com.dataplatform.pipelines.ingestion.CDCProcessor \
    --jars=gs://bucket/jars/data-platform-backend-assembly-1.0.0.jar \
    -- \
    --pubsub-subscription=cdc-changes \
    --target-table=raw.cdc_changes
```

### 2. Transformation Pipelines

#### Zone-to-Zone Processing
```scala
// Raw → Structured
gcloud dataproc jobs submit spark \
    --cluster=data-platform-cluster \
    --class=com.dataplatform.pipelines.transformation.RawToStructured \
    -- \
    --source-table=raw.oracle_customers \
    --target-table=structured.customers

// Structured → Refined  
gcloud dataproc jobs submit spark \
    --cluster=data-platform-cluster \
    --class=com.dataplatform.pipelines.transformation.StructuredToRefined \
    -- \
    --source-table=structured.customers \
    --target-table=refined.customers_enriched
```

### 3. Custom Pipeline Development

#### Creating New Ingestion Pipeline
```scala
package com.dataplatform.pipelines.ingestion

import org.apache.spark.sql.SparkSession
import com.dataplatform.core._

object CustomIngestion {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Custom-Ingestion")
      .getOrCreate()
    
    // Initialize backend services
    val dbConnector = new DatabaseConnector(spark)
    val icebergManager = new IcebergManager(spark)
    val validationEngine = new ValidationEngine(spark)
    
    // Your custom logic here
    // Use backend services for common operations
  }
}
```

## Data Quality Framework

### Validation Rules
```scala
// Standard validation rules
val validationRules = Seq(
  ValidationRule("not_null_check", "Key fields should not be null", "id IS NOT NULL"),
  ValidationRule("date_range", "Dates should be within valid range", "created_date >= '2020-01-01'"),
  ValidationRule("email_format", "Email should be valid format", "email RLIKE '^[^@]+@[^@]+\\.[^@]+")
)

// Custom validation
val customRules = Seq(
  ValidationRule("business_rule", "Amount should be positive", "amount > 0"),
  ValidationRule("referential_integrity", "Customer must exist", "customer_id IN (SELECT id FROM customers)")
)
```

### Data Quality Monitoring
```scala
// Track data quality over time
val qualityMetrics = validationEngine.validateData(df, validationRules, tableName)
qualityMetrics.foreach { metric =>
  // Send to monitoring system
  MetricsCollector.recordQualityMetric(metric)
}
```

## Configuration Management

### Environment-specific Configs
```scala
// development.conf
dataplatform {
  project-id = "dev-project"
  gcs-bucket = "dev-bucket"
  validation.quality-threshold = 0.3
}

// production.conf  
dataplatform {
  project-id = "prod-project"
  gcs-bucket = "prod-bucket"
  validation.quality-threshold = 0.8
}
```

### Dynamic Configuration
```scala
// Load from Firestore
val configManager = new ConfigManager(spark, projectId)
val pipelineConfig = configManager.getPipelineConfig("customer-ingestion")
```

## Error Handling Best Practices

### Retry Logic
```scala
def executeWithRetry[T](operation: () => T, maxRetries: Int = 3): T = {
  var attempt = 0
  while (attempt < maxRetries) {
    try {
      return operation()
    } catch {
      case e: Exception =>
        attempt += 1
        if (attempt >= maxRetries) throw e
        Thread.sleep(1000 * attempt) // Exponential backoff
    }
  }
  throw new RuntimeException("Max retries exceeded")
}
```

### Dead Letter Queue
```scala
// Handle failed records
val (successRecords, failedRecords) = df.partition(validationCondition)

// Process successful records
icebergManager.writeToIceberg(successRecords, targetTable)

// Send failed records to dead letter table
icebergManager.writeToIceberg(failedRecords, s"${targetTable}_failed")
```

# File: monitoring/dashboard-config.yaml
displayName: "Data Platform Monitoring"
mosaicLayout:
  tiles:
  - width: 6
    height: 4
    widget:
      title: "Job Success Rate"
      scorecard:
        timeSeriesQuery:
          timeSeriesFilter:
            filter: 'resource.type="dataproc_cluster"'
            aggregation:
              alignmentPeriod: "300s"
              perSeriesAligner: "ALIGN_RATE"
  - width: 6
    height: 4
    widget:
      title: "Records Processed"
      xyChart:
        dataSets:
        - timeSeriesQuery:
            timeSeriesFilter:
              filter: 'metric.type="custom.googleapis.com/dataplatform/records_processed"'
        timeshiftDuration: "0s"
        yAxis:
          label: "Records"
          scale: "LINEAR"

# File: deployment/terraform/main.tf
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "bucket_name" {
  description = "GCS Bucket Name"
  type        = string
}

# GCS Bucket
resource "google_storage_bucket" "data_platform_bucket" {
  name     = var.bucket_name
  location = "US"
  
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
  
  versioning {
    enabled = true
  }
}

# BigQuery Datasets
resource "google_bigquery_dataset" "raw" {
  dataset_id = "raw"
  location   = "US"
  
  labels = {
    env = "data-platform"
  }
}

resource "google_bigquery_dataset" "structured" {
  dataset_id = "structured"
  location   = "US"
  
  labels = {
    env = "data-platform"
  }
}

resource "google_bigquery_dataset" "refined" {
  dataset_id = "refined"
  location   = "US"
  
  labels = {
    env = "data-platform"
  }
}

resource "google_bigquery_dataset" "analysis" {
  dataset_id = "analysis"
  location   = "US"
  
  labels = {
    env = "data-platform"
  }
}

resource "google_bigquery_dataset" "monitoring" {
  dataset_id = "monitoring"
  location   = "US"
  
  labels = {
    env = "data-platform"
  }
}

# Dataproc Cluster
resource "google_dataproc_cluster" "data_platform_cluster" {
  name   = "data-platform-cluster"
  region = var.region

  cluster_config {
    staging_bucket = google_storage_bucket.data_platform_bucket.name

    master_config {
      num_instances = 1
      machine_type  = "n1-standard-4"
      disk_config {
        boot_disk_type    = "pd-standard"
        boot_disk_size_gb = 50
      }
    }

    worker_config {
      num_instances = 2
      machine_type  = "n1-standard-4"
      disk_config {
        boot_disk_type    = "pd-standard"
        boot_disk_size_gb = 50
      }
    }

    preemptible_worker_config {
      num_instances = 2
    }

    software_config {
      image_version = "2.1-debian11"
      override_properties = {
        "spark:spark.serializer"                               = "org.apache.spark.serializer.KryoSerializer"
        "spark:spark.sql.extensions"                           = "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
        "spark:spark.sql.catalog.iceberg"                     = "org.apache.iceberg.spark.SparkCatalog"
        "spark:spark.sql.catalog.iceberg.type"                = "hadoop"
        "spark:spark.sql.catalog.iceberg.warehouse"           = "gs://${var.bucket_name}/iceberg-warehouse"
      }
    }

    gce_cluster_config {
      zone = "${var.region}-a"
      service_account_scopes = [
        "https://www.googleapis.com/auth/cloud-platform"
      ]
    }

    initialization_action {
      script = "gs://goog-dataproc-initialization-actions-${var.region}/conda/bootstrap-conda.sh"
    }
  }
}

# Secret for database credentials
resource "google_secret_manager_secret" "oracle_db_credentials" {
  secret_id = "oracle-db-credentials"
  
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret" "postgres_db_credentials" {
  secret_id = "postgres-db-credentials"
  
  replication {
    automatic = true
  }
}

# IAM permissions
resource "google_project_iam_member" "dataproc_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${data.google_compute_default_service_account.default.email}"
}

resource "google_project_iam_member" "dataproc_bq_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${data.google_compute_default_service_account.default.email}"
}

data "google_compute_default_service_account" "default" {}

# File: dataflow-templates/cdc-realtime-processor/pom.xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.dataplatform</groupId>
    <artifactId>cdc-realtime-processor</artifactId>
    <version>1.0.0</version>

    <properties>
        <beam.version>2.50.0</beam.version>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.apache.beam</groupId>
            <artifactId>beam-sdks-java-core</artifactId>
            <version>${beam.version}</version>
        </dependency>
        <dependency>
            <groupId>org.apache.beam</groupId>
            <artifactId>beam-runners-google-cloud-dataflow-java</artifactId>
            <version>${beam.version}</version>
        </dependency>
        <dependency>
            <groupId>org.apache.beam</groupId>
            <artifactId>beam-sdks-java-io-google-cloud-platform</artifactId>
            <version>${beam.version}</version>
        </dependency>
    </dependencies>
</project>

# File: dataflow-templates/cdc-realtime-processor/src/main/java/CDCProcessor.java
package com.dataplatform.dataflow;

import org.apache.beam.sdk.Pipeline;
import org.apache.beam.sdk.io.gcp.pubsub.PubsubIO;
import org.apache.beam.sdk.io.gcp.bigquery.BigQueryIO;
import org.apache.beam.sdk.options.*;
import org.apache.beam.sdk.transforms.*;
import org.apache.beam.sdk.values.PCollection;
import com.google.api.services.bigquery.model.TableRow;

public class CDCProcessor {
    
    public interface CDCProcessorOptions extends PipelineOptions {
        @Description("Pub/Sub subscription for CDC events")
        @Validation.Required
        String getSubscription();
        void setSubscription(String subscription);
        
        @Description("BigQuery table for output")
        @Validation.Required
        String getOutputTable();
        void setOutputTable(String outputTable);
    }
    
    public static void main(String[] args) {
        CDCProcessorOptions options = PipelineOptionsFactory.fromArgs(args)
            .withValidation()
            .as(CDCProcessorOptions.class);
            
        Pipeline pipeline = Pipeline.create(options);
        
        PCollection<String> cdcEvents = pipeline
            .apply("Read from Pub/Sub", 
                PubsubIO.readStrings().fromSubscription(options.getSubscription()));
        
        PCollection<TableRow> transformedEvents = cdcEvents
            .apply("Parse and Transform", ParDo.of(new ParseCDCEvent()));
        
        transformedEvents.apply("Write to BigQuery",
            BigQueryIO.writeTableRows()
                .to(options.getOutputTable())
                .withWriteDisposition(BigQueryIO.Write.WriteDisposition.WRITE_APPEND));
        
        pipeline.run();
    }
    
    static class ParseCDCEvent extends DoFn<String, TableRow> {
        @ProcessElement
        public void processElement(ProcessContext c) {
            String json = c.element();
            // Parse CDC JSON and create TableRow
            TableRow row = new TableRow();
            // Add parsing logic here
            c.output(row);
        }
    }
}

# File: dataform-pipelines/real-time-analytics/dataform.json
{
  "defaultSchema": "analysis",
  "assertionSchema": "dataform_assertions",
  "warehouse": "bigquery",
  "defaultLocation": "US"
}

# File: dataform-pipelines/real-time-analytics/definitions/customer_metrics.sqlx
config {
  type: "incremental",
  schema: "analysis",
  description: "Real-time customer metrics aggregation"
}

SELECT
  customer_id,
  COUNT(*) as transaction_count,
  SUM(amount) as total_amount,
  AVG(amount) as avg_amount,
  MAX(transaction_timestamp) as last_transaction_time,
  CURRENT_TIMESTAMP() as updated_at
FROM ${ref("structured", "transactions")}
WHERE transaction_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
GROUP BY customer_id

# File: README.md
# GCP Data Platform

A comprehensive data platform solution for GCP that provides scalable data ingestion, transformation, and analytics capabilities with built-in monitoring and data quality features.

## Architecture Overview

```
Data Sources → Ingestion → Raw Zone → Transformation → Structured → Refined → Analysis
     ↓              ↓           ↓            ↓             ↓          ↓         ↓
   Oracle         Dataproc     GCS       Dataproc      Iceberg    BigQuery   ML/BI
   PostgreSQL     Dataflow   Iceberg      BigQuery      Format      SQL      Tools
   Files/APIs     
```

## Key Features

- **Multi-source Ingestion**: Oracle, PostgreSQL, files, APIs, streaming data
- **Real-time CDC**: Change Data Capture with near real-time processing
- **Data Quality**: Built-in validation, monitoring, and lineage tracking
- **Flexible Pipelines**: Support for batch and streaming processing
- **Iceberg Integration**: Modern data lake format with ACID transactions
- **Comprehensive Monitoring**: Audit logs, lineage tracking, and alerting

## Quick Start

### 1. Prerequisites
- GCP Project with billing enabled
- gcloud CLI installed and configured
- sbt installed for Scala builds

### 2. Clone and Setup
```bash
git clone <repository>
cd gcp-data-platform

# Set environment variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GCS_BUCKET="your-bucket-name"
```

### 3. Deploy Infrastructure
```bash
# Option 1: Automated deployment
./deployment/scripts/build-and-deploy.sh

# Option 2: Terraform deployment
cd deployment/terraform
terraform init
terraform apply
```

### 4. Configure Secrets
```bash
# Create database credentials in Secret Manager
gcloud secrets create oracle-db-credentials --data-file=oracle-creds.json
```

### 5. Run Sample Pipeline
```bash
./deployment/scripts/run-sample-ingestion.sh
```

## Project Structure

```
gcp-data-platform/
├── backend-service/          # Core platform services
├── data-pipelines/           # Pipeline implementations
├── dataflow-templates/       # Real-time processing templates
├── dataform-pipelines/       # SQL-based transformations
├── deployment/               # Infrastructure and deployment scripts
├── monitoring/               # Dashboards and alerting
└── docs/                     # Documentation
```

## Backend Service Features

The backend service provides reusable components for:

- **Database Connectivity**: Oracle, PostgreSQL, MySQL with Secret Manager integration
- **File Processing**: Excel, CSV, JSON, text file ingestion
- **Iceberg Management**: Table creation, optimization, time travel
- **Data Validation**: Configurable quality rules and monitoring
- **Audit Logging**: Comprehensive job and data lineage tracking

## Pipeline Types

### Ingestion Pipelines
- **Full Load**: Complete table extraction with partitioning
- **Incremental**: Delta/CDC-based updates
- **File-based**: Scheduled file processing
- **Streaming**: Real-time data ingestion

### Transformation Pipelines  
- **Raw → Structured**: Data cleansing and standardization
- **Structured → Refined**: Business logic and enrichment
- **Refined → Analysis**: Aggregations and analytics preparation

## Monitoring and Operations

- **GCP Native Monitoring**: Cloud Monitoring integration
- **Custom Dashboards**: Pipeline and data quality metrics
- **Audit Logging**: BigQuery-based audit trail
- **Data Lineage**: Table, column, and row-level tracking
- **Alerting**: Job failure and data quality alerts

## Development Guide

See [docs/pipeline-guide.md](docs/pipeline-guide.md) for detailed development instructions.

## Deployment Guide

See [docs/deployment-guide.md](docs/deployment-guide.md) for complete deployment procedures.

## Support

For issues and questions:
1. Check [docs/troubleshooting.md](docs/troubleshooting.md)
2. Review GCP Dataproc logs
3. Monitor BigQuery audit tables

## License

Copyright 2024 - Data Platform Team