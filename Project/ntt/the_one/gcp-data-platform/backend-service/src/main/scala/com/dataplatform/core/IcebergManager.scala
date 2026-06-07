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