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