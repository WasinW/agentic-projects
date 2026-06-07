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