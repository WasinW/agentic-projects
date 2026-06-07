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