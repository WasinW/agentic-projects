package com.dataplatform.config

import org.apache.spark.sql.SparkSession
import com.typesafe.config.{Config, ConfigFactory}

class ConfigManager(spark: SparkSession, projectId: String) {
  
  private val config: Config = ConfigFactory.load()
  
  def getProjectId: String = {
    sys.env.getOrElse("GOOGLE_CLOUD_PROJECT", 
      config.getString("dataplatform.project-id"))
  }
  
  def getGcsBucket: String = {
    sys.env.getOrElse("GCS_BUCKET", 
      config.getString("dataplatform.gcs-bucket"))
  }
}