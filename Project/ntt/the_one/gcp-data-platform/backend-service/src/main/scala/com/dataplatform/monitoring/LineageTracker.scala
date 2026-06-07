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