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