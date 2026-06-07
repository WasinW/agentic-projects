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