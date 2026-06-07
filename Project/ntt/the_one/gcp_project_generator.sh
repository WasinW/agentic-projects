    val spark = SparkSession.builder()
      .appName("Custom-Ingestion")
      .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
      .getOrCreate()
    
    // Initialize backend services
    val dbConnector = new DatabaseConnector(spark)
    val icebergManager = new IcebergManager(spark)
    val validationEngine = new ValidationEngine(spark)
    val auditLogger = new AuditLogger(spark, projectId)
    val lineageTracker = new LineageTracker(spark, projectId)
    
    // Your custom logic here
    try {
      // Extract data
      val data = dbConnector.connectAndQuery(projectId, secretId, query)
      
      // Validate data
      val validationResults = validationEngine.validateData(data, rules, tableName)
      
      // Transform if needed
      val processedData = data.withColumn("_custom_field", lit("value"))
      
      // Write to Iceberg
      icebergManager.writeToIceberg(processedData, targetTable, "append")
      
      // Track lineage
      lineageTracker.trackTableLineage(sourceTable, targetTable, "custom_ingestion", jobId)
      
    } catch {
      case e: Exception =>
        // Handle errors and log
        auditLogger.logJobCompletion(jobId, "Custom-Ingestion", targetTable, 
          "INGESTION", 0, startTime, "FAILED", Some(e.getMessage))
        throw e
    }
  }
}
```

2. **Add to build.sbt (if needed)**
3. **Create deployment script**
4. **Add to orchestration workflows**

### Custom Validation Rules

```scala
val customValidationRules = Seq(
  ValidationRule("business_rule_1", "Amount must be positive", "amount > 0"),
  ValidationRule("referential_integrity", "Customer must exist", 
    "customer_id IN (SELECT customer_id FROM dim_customers)"),
  ValidationRule("data_freshness", "Data must be recent", 
    "ingestion_date >= CURRENT_DATE - INTERVAL 1 DAY")
)
```

### Custom Transformations

```scala
val transformedData = inputData
  // Business-specific transformations
  .withColumn("customer_tier", 
    when(col("total_purchases") > 10000, "Platinum")
    .when(col("total_purchases") > 5000, "Gold")
    .when(col("total_purchases") > 1000, "Silver")
    .otherwise("Bronze"))
  
  // Geographic enrichment
  .withColumn("region", 
    when(col("state").isin("CA", "OR", "WA"), "West Coast")
    .when(col("state").isin("NY", "MA", "CT"), "East Coast")
    .otherwise("Other"))
  
  // Date calculations
  .withColumn("days_since_last_purchase", 
    datediff(current_date(), col("last_purchase_date")))
```

## Configuration Management

### Environment-Specific Configurations

Create environment-specific configuration files:

**development.conf**
```hocon
dataplatform {
  project-id = "dev-project"
  gcs-bucket = "dev-bucket"
  validation.quality-threshold = 0.6  # Lower threshold for dev
}
```

**production.conf**
```hocon
dataplatform {
  project-id = "prod-project"
  gcs-bucket = "prod-bucket"
  validation.quality-threshold = 0.9  # Higher threshold for prod
}
```

### Dynamic Configuration

```scala
// Load configuration from external source
val configManager = new ConfigManager(spark, projectId)
val qualityThreshold = configManager.getValidationQualityThreshold
val maxErrorRate = configManager.getMaxErrorRate
```

## Error Handling Best Practices

### 1. Retry Logic
```scala
def executeWithRetry[T](operation: () => T, maxRetries: Int = 3): T = {
  var attempt = 0
  var lastException: Exception = null
  
  while (attempt < maxRetries) {
    try {
      return operation()
    } catch {
      case e: Exception =>
        lastException = e
        attempt += 1
        if (attempt < maxRetries) {
          val delay = math.pow(2, attempt).toInt * 1000 // Exponential backoff
          Thread.sleep(delay)
          println(s"Retry attempt $attempt after ${delay}ms delay")
        }
    }
  }
  throw lastException
}
```

### 2. Dead Letter Queue Pattern
```scala
// Separate valid and invalid records
val (validRecords, invalidRecords) = try {
  val validated = data.filter(validationCondition)
  val invalid = data.filter(!validationCondition)
  (validated, invalid)
} catch {
  case e: Exception =>
    // If validation fails completely, send all to DLQ
    (spark.emptyDataFrame, data)
}

// Process valid records
if (validRecords.count() > 0) {
  icebergManager.writeToIceberg(validRecords, targetTable)
}

// Send invalid records to dead letter table
if (invalidRecords.count() > 0) {
  icebergManager.writeToIceberg(invalidRecords, s"${targetTable}_dlq")
}
```

### 3. Circuit Breaker Pattern
```scala
class CircuitBreaker(failureThreshold: Int, timeout: Long) {
  private var failureCount = 0
  private var lastFailureTime = 0L
  private var state: String = "CLOSED" // CLOSED, OPEN, HALF_OPEN
  
  def execute[T](operation: () => T): T = {
    state match {
      case "OPEN" =>
        if (System.currentTimeMillis() - lastFailureTime > timeout) {
          state = "HALF_OPEN"
          execute(operation)
        } else {
          throw new RuntimeException("Circuit breaker is OPEN")
        }
      case "HALF_OPEN" =>
        try {
          val result = operation()
          state = "CLOSED"
          failureCount = 0
          result
        } catch {
          case e: Exception =>
            state = "OPEN"
            lastFailureTime = System.currentTimeMillis()
            throw e
        }
      case "CLOSED" =>
        try {
          operation()
        } catch {
          case e: Exception =>
            failureCount += 1
            if (failureCount >= failureThreshold) {
              state = "OPEN"
              lastFailureTime = System.currentTimeMillis()
            }
            throw e
        }
    }
  }
}
```

## Performance Optimization

### 1. Spark Configuration Tuning
```bash
# For large datasets
--properties="spark.executor.memory=14g,spark.driver.memory=4g,spark.executor.cores=4,spark.sql.adaptive.enabled=true,spark.sql.adaptive.coalescePartitions.enabled=true,spark.sql.adaptive.skewJoin.enabled=true"

# For streaming jobs
--properties="spark.streaming.backpressure.enabled=true,spark.streaming.receiver.maxRate=1000,spark.streaming.kafka.maxRatePerPartition=1000"
```

### 2. Partitioning Strategy
```scala
// Partition by date for time-series data
icebergManager.writeToIceberg(df, tableName, "append", Seq("partition_date"))

// Partition by high-cardinality column
icebergManager.writeToIceberg(df, tableName, "append", Seq("customer_id"))

// Multi-level partitioning
icebergManager.writeToIceberg(df, tableName, "append", Seq("year", "month", "day"))
```

### 3. Caching Strategy
```scala
// Cache frequently accessed DataFrames
val customerDim = spark.read.table("dim_customers").cache()

// Unpersist when no longer needed
customerDim.unpersist()
```

## Testing Pipelines

### 1. Unit Tests
```scala
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers
import org.apache.spark.sql.test.SharedSparkSession

class DataTransformationTest extends AnyFlatSpec with Matchers with SharedSparkSession {
  
  "Data transformation" should "handle null values correctly" in {
    import spark.implicits._
    
    val inputData = Seq(
      ("John", "Doe", null),
      ("Jane", null, "jane@example.com"),
      (null, "Smith", "smith@example.com")
    ).toDF("first_name", "last_name", "email")
    
    val result = transformData(inputData)
    
    result.filter(col("full_name").isNull).count() shouldBe 1
    result.filter(col("is_valid_email")).count() shouldBe 2
  }
}
```

### 2. Integration Tests
```scala
class PipelineIntegrationTest extends AnyFlatSpec with Matchers {
  
  "End-to-end pipeline" should "process data correctly" in {
    // Setup test data
    val testData = createTestData()
    
    // Run pipeline
    val result = runPipeline(testData)
    
    // Verify results
    result.count() should be > 0
    result.filter(col("_data_quality_score") >= 0.8).count() should be > (result.count() * 0.8)
  }
}
```

## Monitoring and Alerting

### Custom Metrics
```scala
// Custom metric collection
case class PipelineMetrics(
  recordsProcessed: Long,
  qualityScore: Double,
  processingTimeMs: Long,
  errorsCount: Long
)

class MetricsCollector(spark: SparkSession, projectId: String) {
  def recordMetric(metric: PipelineMetrics, jobName: String): Unit = {
    // Send to Cloud Monitoring
    // Store in BigQuery
    // Send to external systems
  }
}
```

### Custom Alerts
```yaml
# Custom alert for pipeline SLA breach
- displayName: "Pipeline SLA Breach"
  conditions:
  - conditionThreshold:
      filter: 'resource.type="dataproc_cluster" AND textPayload:"processing_time_ms"'
      comparison: "COMPARISON_GT"
      thresholdValue: 3600000  # 1 hour in ms
      duration: "300s"
```

## Best Practices

### 1. Code Organization
- Keep pipeline logic modular and reusable
- Use the provided backend services for common operations
- Implement proper error handling and logging
- Write comprehensive tests

### 2. Data Quality
- Implement validation at every stage
- Use the ValidationEngine for consistent quality checks
- Monitor quality trends over time
- Set up alerts for quality degradation

### 3. Performance
- Choose appropriate partitioning strategies
- Use Iceberg's features (time travel, schema evolution)
- Monitor resource usage and optimize accordingly
- Use caching judiciously

### 4. Security
- Never hardcode credentials in pipeline code
- Use Secret Manager for sensitive configuration
- Implement proper access controls
- Audit data access and modifications

### 5. Monitoring
- Use the built-in audit logging
- Track data lineage for all transformations
- Set up meaningful alerts
- Monitor pipeline SLAs

## Orchestration

### Daily Pipeline Example
```bash
#!/bin/bash
# Daily pipeline orchestration

# Run ingestion jobs in parallel
./run-oracle-ingestion.sh &
./run-postgres-ingestion.sh &
wait

# Run transformations sequentially
./run-raw-to-structured.sh
./run-structured-to-refined.sh
./run-refined-to-analysis.sh

# Run quality checks
./run-quality-checks.sh

# Generate reports
./generate-daily-reports.sh
```

### Using Cloud Composer (Airflow)
```python
from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-platform',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'daily_data_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
)

# Define pipeline tasks
oracle_ingestion = DataprocSubmitJobOperator(
    task_id='oracle_ingestion',
    job=oracle_job_config,
    dag=dag
)

transform_raw_to_structured = DataprocSubmitJobOperator(
    task_id='raw_to_structured',
    job=transform_job_config,
    dag=dag
)

# Set dependencies
oracle_ingestion >> transform_raw_to_structured
```
EOF

# README file
cat > README.md << 'EOF'
# GCP Data Platform

A comprehensive, production-ready data platform solution for Google Cloud Platform that provides scalable data ingestion, transformation, and analytics capabilities with built-in monitoring, data quality, and lineage tracking.

## 🏗️ Architecture Overview

```
Data Sources → Ingestion → Raw Zone → Transformation → Structured → Refined → Analysis
     ↓              ↓           ↓            ↓             ↓          ↓         ↓
   Oracle         Dataproc     GCS       Dataproc      Iceberg    BigQuery   ML/BI
   PostgreSQL     Dataflow   Iceberg      BigQuery      Format      SQL      Tools
   Files/APIs     Pub/Sub    Tables       Streaming     ACID       Analytics Reports
```

## ✨ Key Features

- **🔄 Multi-source Ingestion**: Oracle, PostgreSQL, MySQL, files, APIs, streaming data
- **⚡ Real-time Processing**: Change Data Capture (CDC) with near real-time processing
- **🛡️ Data Quality**: Built-in validation, monitoring, and quality scoring
- **📊 Flexible Pipelines**: Support for batch and streaming processing
- **🏔️ Modern Data Lake**: Apache Iceberg integration with ACID transactions
- **📈 Comprehensive Monitoring**: Audit logs, lineage tracking, and alerting
- **🔧 Infrastructure as Code**: Terraform deployment support
- **🧪 Built-in Testing**: Unit and integration test frameworks

## 🚀 Quick Start

### Prerequisites
- GCP Project with billing enabled
- `gcloud` CLI installed and configured
- `sbt` installed for Scala builds
- `terraform` installed (optional)

### 1. Clone and Setup
```bash
git clone <repository>
cd gcp-data-platform

# Set environment variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GCS_BUCKET="your-unique-bucket-name"
export DATAPROC_REGION="us-central1"
```

### 2. Quick Deployment
```bash
# Deploy everything with one command
./deployment/scripts/build-and-deploy.sh

# Configure database credentials
./deployment/scripts/setup-secrets.sh

# Run sample pipeline
./deployment/scripts/run-sample-ingestion.sh
```

### 3. Alternative: Terraform Deployment
```bash
./deployment/scripts/deploy-with-terraform.sh
```

## 📁 Project Structure

```
gcp-data-platform/
├── backend-service/              # Core platform services (Scala)
│   ├── src/main/scala/com/dataplatform/
│   │   ├── core/                # Database, file processing, Iceberg, validation
│   │   ├── ingestion/           # Ingestion pipeline templates
│   │   ├── transformation/      # Transformation pipeline templates
│   │   ├── monitoring/          # Audit logging and lineage tracking
│   │   └── config/              # Configuration management
│   └── build.sbt                # Build configuration
├── data-pipelines/               # Pipeline implementations
│   ├── ingestion/               # Oracle, PostgreSQL, file, CDC pipelines
│   ├── transformation/          # Raw→Structured→Refined→Analysis
│   └── validation/              # Data quality check pipelines
├── dataflow-templates/           # Real-time processing templates
├── dataform-pipelines/           # SQL-based transformations
├── deployment/                   # Infrastructure and deployment
│   ├── terraform/               # Terraform configurations
│   └── scripts/                 # Deployment and utility scripts
├── monitoring/                   # Dashboards and alerting
└── docs/                        # Documentation
```

## 🔧 Backend Service Components

### Core Services
- **DatabaseConnector**: Connect to Oracle, PostgreSQL, MySQL with Secret Manager integration
- **FileProcessor**: Process Excel, CSV, JSON, text files with standardization
- **IcebergManager**: Manage Iceberg tables with optimization and time travel
- **ValidationEngine**: Configurable data quality rules and validation
- **AuditLogger**: Comprehensive job and operation audit logging
- **LineageTracker**: Table, column, and row-level lineage tracking

### Example Usage
```scala
// Initialize services
val dbConnector = new DatabaseConnector(spark)
val icebergManager = new IcebergManager(spark)
val validationEngine = new ValidationEngine(spark)

// Extract data with automatic secret management
val data = dbConnector.connectAndQuery(projectId, "oracle-credentials", "SELECT * FROM customers")

// Validate data quality
val validationResults = validationEngine.validateData(data, validationRules, "customers")

// Write to Iceberg with partitioning
icebergManager.writeToIceberg(data, "raw.customers", "append", Seq("partition_date"))
```

## 🔄 Pipeline Types

### Ingestion Pipelines
- **Full Load**: Complete table extraction with date partitioning
- **Incremental**: Delta/CDC-based updates with watermarking
- **File-based**: Scheduled file processing with format detection
- **Streaming**: Real-time data ingestion via Pub/Sub

### Transformation Pipelines
- **Raw → Structured**: Data cleansing, standardization, and quality scoring
- **Structured → Refined**: Business logic application and enrichment
- **Refined → Analysis**: Aggregations and analytics preparation

### Example Pipeline Execution
```bash
# Oracle ingestion
gcloud dataproc jobs submit spark \
    --cluster=data-platform-cluster \
    --class=com.dataplatform.pipelines.ingestion.OracleIngestion \
    --jars=gs://bucket/jars/data-platform-backend-assembly-1.0.0.jar \
    -- --source-table=customers --target-table=raw.oracle_customers

# Data transformation
gcloud dataproc jobs submit spark \
    --cluster=data-platform-cluster \
    --class=com.dataplatform.pipelines.transformation.RawToStructured \
    --jars=gs://bucket/jars/data-platform-backend-assembly-1.0.0.jar \
    -- --source-table=raw.oracle_customers --target-table=structured.customers
```

## 📊 Monitoring and Operations

### Built-in Monitoring
- **Audit Logging**: All pipeline executions logged to BigQuery
- **Data Lineage**: Automatic tracking of data transformations
- **Quality Metrics**: Data quality scores and trend analysis
- **Performance Monitoring**: Job execution times and resource usage

### Dashboards and Alerts
- **Cloud Monitoring**: Native GCP monitoring integration
- **Custom Dashboards**: Pipeline health and data quality metrics
- **Automated Alerts**: Job failures and quality degradation notifications

### Example Monitoring Queries
```sql
-- Pipeline success rate
SELECT 
  DATE(start_time) as date,
  job_name,
  COUNTIF(status = 'COMPLETED') / COUNT(*) * 100 as success_rate
FROM `project.monitoring.audit_logs`
WHERE start_time >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY 1, 2

-- Data quality trends
SELECT 
  DATE(check_timestamp) as date,
  table_name,
  AVG(quality_score) as avg_quality_score
FROM `project.monitoring.data_quality_results`
WHERE check_timestamp >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY 1, 2
ORDER BY 1 DESC, 2
```

## 🔒 Security Features

- **Secret Manager Integration**: Secure credential management
- **IAM-based Access Control**: Fine-grained permissions
- **Data Encryption**: At-rest and in-transit encryption
- **Audit Trail**: Complete audit trail of all operations
- **Network Security**: VPC and firewall configuration

## 🧪 Testing

### Unit Tests
```scala
import org.scalatest.flatspec.AnyFlatSpec
import org.apache.spark.sql.test.SharedSparkSession

class ValidationEngineTest extends AnyFlatSpec with SharedSparkSession {
  "ValidationEngine" should "validate data correctly" in {
    val rules = Seq(ValidationRule("not_null", "ID should not be null", "id IS NOT NULL"))
    val results = validationEngine.validateData(testData, rules, "test_table")
    assert(results.head.passed)
  }
}
```

### Integration Tests
```bash
# Run full pipeline test
./deployment/scripts/run-sample-ingestion.sh

# Verify results in BigQuery
bq query "SELECT COUNT(*) FROM \`project.structured.customers\`"
```

## 📚 Documentation

- **[Deployment Guide](docs/deployment-guide.md)**: Complete deployment instructions
- **[Pipeline Guide](docs/pipeline-guide.md)**: Pipeline development and best practices
- **[API Documentation](docs/api-docs.md)**: Backend service API reference
- **[Troubleshooting](docs/troubleshooting.md)**: Common issues and solutions

## 🔧 Configuration

### Environment Variables
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GCS_BUCKET="your-bucket-name"
export DATAPROC_REGION="us-central1"
```

### Application Configuration
```hocon
dataplatform {
  project-id = ${GOOGLE_CLOUD_PROJECT}
  gcs-bucket = ${GCS_BUCKET}
  
  validation {
    quality-threshold = 0.8
    max-error-rate = 0.1
  }
  
  iceberg {
    warehouse = "gs://"${dataplatform.gcs-bucket}"/iceberg-warehouse"
  }
}
```

## 🚀 Advanced Features

### Time Travel with Iceberg
```scala
// Read historical data
val historicalData = icebergManager.readFromIceberg(
  tableName = "structured.customers",
  asOfTimestamp = Some("2024-01-01 00:00:00")
)
```

### Streaming CDC Processing
```scala
// Real-time change data capture
val cdcStream = spark.readStream
  .format("pubsub")
  .option("subscription", "cdc-subscription")
  .load()
```

### Data Quality Scoring
```scala
// Automatic quality scoring
val qualityScore = df.select(
  avg(when(col("email").rlike("@"), 1).otherwise(0)) * 0.3 +
  avg(when(col("phone").isNotNull, 1).otherwise(0)) * 0.3 +
  avg(when(col("name").isNotNull, 1).otherwise(0)) * 0.4
).collect()(0)(0).asInstanceOf[Double]
```

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy Data Platform
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup sbt
      uses: olafurpg/setup-scala@v10
    - name: Build and Deploy
      run: ./deployment/scripts/build-and-deploy.sh
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For issues and questions:
1. Check the [troubleshooting guide](docs/troubleshooting.md)
2. Review GCP Dataproc logs
3. Monitor BigQuery audit tables
4. Create an issue in the repository

## 🎯 Roadmap

- [ ] Apache Airflow integration for workflow orchestration
- [ ] Delta Lake support as alternative to Iceberg
- [ ] Machine learning pipeline templates
- [ ] Real-time dashboards with Looker integration
- [ ] Data catalog integration with Apache Atlas
- [ ] Cost optimization recommendations

---

**Built with ❤️ for the data engineering community**
EOF

echo ""
echo "🎉 GCP Data Platform project structure created successfully!"
echo ""
echo "📁 Project created in: $(pwd)/$PROJECT_NAME"
echo ""
echo "🚀 Next steps:"
echo "1. cd $PROJECT_NAME"
echo "2. Set environment variables:"
echo "   export GOOGLE_CLOUD_PROJECT='your-project-id'"
echo "   export GCS_BUCKET='your-bucket-name'"
echo "3. Run deployment: ./deployment/scripts/build-and-deploy.sh"
echo "4. Configure secrets: ./deployment/scripts/setup-secrets.sh"
echo "5. Test pipeline: ./deployment/scripts/run-sample-ingestion.sh"
echo ""
echo "📚 Documentation:"
echo "- Deployment Guide: docs/deployment-guide.md"
echo "- Pipeline Guide: docs/pipeline-guide.md"
echo "- README: README.md"
echo ""
echo "Happy data engineering! 🎯"
      name = "metadata"
      type = "JSON"
      mode = "NULLABLE"
    }
  ])
  
  labels = {
    env        = "data-platform"
    managed-by = "terraform"
  }
}

resource "google_bigquery_table" "data_lineage" {
  dataset_id = google_bigquery_dataset.monitoring.dataset_id
  table_id   = "data_lineage"
  
  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }
  
  clustering = ["source_table", "target_table"]
  
  schema = jsonencode([
    {
      name = "source_table"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "target_table"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "transformation"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "columns"
      type = "STRING"
      mode = "REPEATED"
    },
    {
      name = "timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "job_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "level"
      type = "STRING"
      mode = "REQUIRED"
    }
  ])
  
  labels = {
    env        = "data-platform"
    managed-by = "terraform"
  }
}

resource "google_bigquery_table" "data_quality_results" {
  dataset_id = google_bigquery_dataset.monitoring.dataset_id
  table_id   = "data_quality_results"
  
  time_partitioning {
    type  = "DAY"
    field = "check_timestamp"
  }
  
  clustering = ["table_name", "rule_name"]
  
  schema = jsonencode([
    {
      name = "job_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "table_name"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "rule_name"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "passed"
      type = "BOOLEAN"
      mode = "REQUIRED"
    },
    {
      name = "failed_records"
      type = "INTEGER"
      mode = "REQUIRED"
    },
    {
      name = "total_records"
      type = "INTEGER"
      mode = "REQUIRED"
    },
    {
      name = "severity"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "message"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "quality_score"
      type = "FLOAT"
      mode = "REQUIRED"
    },
    {
      name = "check_timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    }
  ])
  
  labels = {
    env        = "data-platform"
    managed-by = "terraform"
  }
}
EOF

# Dataproc resources
cat > deployment/terraform/dataproc.tf << 'EOF'
# Dataproc cluster
resource "google_dataproc_cluster" "data_platform_cluster" {
  name   = var.cluster_name
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
        "spark:spark.sql.adaptive.enabled"                    = "true"
        "spark:spark.sql.adaptive.coalescePartitions.enabled" = "true"
      }
    }

    gce_cluster_config {
      zone = "${var.region}-a"
      service_account_scopes = [
        "https://www.googleapis.com/auth/cloud-platform"
      ]
      
      tags = ["dataproc-cluster", "data-platform"]
    }

    initialization_action {
      script = "gs://goog-dataproc-initialization-actions-${var.region}/conda/bootstrap-conda.sh"
    }
  }
  
  labels = {
    env        = "data-platform"
    managed-by = "terraform"
  }
}

# Dataproc autoscaling policy
resource "google_dataproc_autoscaling_policy" "data_platform_autoscaling" {
  policy_id = "data-platform-autoscaling"
  location  = var.region

  worker_config {
    max_instances = 10
    min_instances = 2
    weight        = 1
  }

  secondary_worker_config {
    max_instances = 20
    min_instances = 0
    weight        = 1
  }

  basic_algorithm {
    cooldown_period = "2m"
    yarn_config {
      graceful_decommission_timeout = "5m"
      scale_up_factor               = 0.05
      scale_down_factor             = 1.0
    }
  }
}
EOF

# Secret Manager resources
cat > deployment/terraform/secrets.tf << 'EOF'
# Oracle database credentials secret
resource "google_secret_manager_secret" "oracle_db_credentials" {
  secret_id = "oracle-db-credentials"
  
  replication {
    automatic = true
  }
  
  labels = {
    env        = "data-platform"
    managed-by = "terraform"
  }
}

# PostgreSQL database credentials secret
resource "google_secret_manager_secret" "postgres_db_credentials" {
  secret_id = "postgres-db-credentials"
  
  replication {
    automatic = true
  }
  
  labels = {
    env        = "data-platform"
    managed-by = "terraform"
  }
}

# MySQL database credentials secret
resource "google_secret_manager_secret" "mysql_db_credentials" {
  secret_id = "mysql-db-credentials"
  
  replication {
    automatic = true
  }
  
  labels = {
    env        = "data-platform"
    managed-by = "terraform"
  }
}
EOF

# IAM resources
cat > deployment/terraform/iam.tf << 'EOF'
# IAM roles for Dataproc service account
resource "google_project_iam_member" "dataproc_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${data.google_compute_default_service_account.default.email}"
}

resource "google_project_iam_member" "dataproc_bq_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${data.google_compute_default_service_account.default.email}"
}

resource "google_project_iam_member" "dataproc_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${data.google_compute_default_service_account.default.email}"
}

resource "google_project_iam_member" "dataproc_storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${data.google_compute_default_service_account.default.email}"
}

resource "google_project_iam_member" "dataproc_dataflow_admin" {
  project = var.project_id
  role    = "roles/dataflow.admin"
  member  = "serviceAccount:${data.google_compute_default_service_account.default.email}"
}

resource "google_project_iam_member" "dataproc_pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${data.google_compute_default_service_account.default.email}"
}
EOF

# Pub/Sub resources
cat > deployment/terraform/pubsub.tf << 'EOF'
# Pub/Sub topic for CDC events
resource "google_pubsub_topic" "cdc_events" {
  name = "cdc-events"
  
  labels = {
    env        = "data-platform"
    managed-by = "terraform"
  }
}

# Subscription for CDC processing
resource "google_pubsub_subscription" "cdc_processor" {
  name  = "cdc-changes"
  topic = google_pubsub_topic.cdc_events.name

  message_retention_duration = "604800s"  # 7 days
  retain_acked_messages      = false
  ack_deadline_seconds       = 20

  expiration_policy {
    ttl = "2678400s"  # 31 days
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.cdc_events_dlq.id
    max_delivery_attempts = 5
  }
  
  labels = {
    env        = "data-platform"
    managed-by = "terraform"
  }
}

# Dead letter queue for failed CDC messages
resource "google_pubsub_topic" "cdc_events_dlq" {
  name = "cdc-events-dlq"
  
  labels = {
    env        = "data-platform"
    managed-by = "terraform"
  }
}

# Subscription for monitoring dead letter queue
resource "google_pubsub_subscription" "cdc_dlq_monitor" {
  name  = "cdc-dlq-monitor"
  topic = google_pubsub_topic.cdc_events_dlq.name

  message_retention_duration = "604800s"
  
  labels = {
    env        = "data-platform"
    managed-by = "terraform"
  }
}
EOF

# Outputs
cat > deployment/terraform/outputs.tf << 'EOF'
output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "bucket_name" {
  description = "GCS bucket name for data platform"
  value       = google_storage_bucket.data_platform_bucket.name
}

output "bucket_url" {
  description = "GCS bucket URL"
  value       = google_storage_bucket.data_platform_bucket.url
}

output "dataproc_cluster_name" {
  description = "Dataproc cluster name"
  value       = google_dataproc_cluster.data_platform_cluster.name
}

output "dataproc_cluster_region" {
  description = "Dataproc cluster region"
  value       = google_dataproc_cluster.data_platform_cluster.region
}

output "bigquery_datasets" {
  description = "BigQuery datasets created"
  value = {
    raw        = google_bigquery_dataset.raw.dataset_id
    structured = google_bigquery_dataset.structured.dataset_id
    refined    = google_bigquery_dataset.refined.dataset_id
    analysis   = google_bigquery_dataset.analysis.dataset_id
    monitoring = google_bigquery_dataset.monitoring.dataset_id
  }
}

output "pubsub_topics" {
  description = "Pub/Sub topics created"
  value = {
    cdc_events     = google_pubsub_topic.cdc_events.name
    cdc_events_dlq = google_pubsub_topic.cdc_events_dlq.name
  }
}

output "secrets" {
  description = "Secret Manager secrets created"
  value = {
    oracle_credentials   = google_secret_manager_secret.oracle_db_credentials.secret_id
    postgres_credentials = google_secret_manager_secret.postgres_db_credentials.secret_id
    mysql_credentials    = google_secret_manager_secret.mysql_db_credentials.secret_id
  }
}

output "next_steps" {
  description = "Next steps to complete setup"
  value = <<EOT
Data Platform Infrastructure Created Successfully!

Next Steps:
1. Configure database credentials:
   ./deployment/scripts/setup-secrets.sh

2. Upload application JARs:
   ./deployment/scripts/build-and-deploy.sh

3. Run sample pipeline:
   ./deployment/scripts/run-sample-ingestion.sh

4. Monitor in GCP Console:
   - Dataproc: https://console.cloud.google.com/dataproc/clusters?project=${var.project_id}
   - BigQuery: https://console.cloud.google.com/bigquery?project=${var.project_id}
   - Storage: https://console.cloud.google.com/storage/browser/${google_storage_bucket.data_platform_bucket.name}
EOT
}
EOF

echo "Terraform files created successfully!"

# ===============================
# CREATE MONITORING FILES
# ===============================

echo "Creating monitoring and documentation files..."

# Dashboard configuration
cat > monitoring/dashboards/data-platform-dashboard.yaml << 'EOF'
displayName: "GCP Data Platform Monitoring"
mosaicLayout:
  tiles:
  - width: 6
    height: 4
    widget:
      title: "Pipeline Job Success Rate"
      scorecard:
        timeSeriesQuery:
          timeSeriesFilter:
            filter: 'resource.type="dataproc_cluster" AND textPayload:"Successfully"'
            aggregation:
              alignmentPeriod: "300s"
              perSeriesAligner: "ALIGN_RATE"
              crossSeriesReducer: "REDUCE_MEAN"
        sparkChartView:
          sparkChartType: "SPARK_LINE"
  
  - width: 6
    height: 4
    widget:
      title: "Records Processed Over Time"
      xyChart:
        dataSets:
        - timeSeriesQuery:
            timeSeriesFilter:
              filter: 'resource.type="bigquery_table" AND resource.labels.table_id="audit_logs"'
              aggregation:
                alignmentPeriod: "300s"
                perSeriesAligner: "ALIGN_RATE"
        timeshiftDuration: "0s"
        yAxis:
          label: "Records per Second"
          scale: "LINEAR"
  
  - width: 6
    height: 4
    widget:
      title: "Data Quality Scores"
      xyChart:
        dataSets:
        - timeSeriesQuery:
            timeSeriesFilter:
              filter: 'resource.type="bigquery_table" AND resource.labels.table_id="data_quality_results"'
              aggregation:
                alignmentPeriod: "3600s"
                perSeriesAligner: "ALIGN_MEAN"
                groupByFields: ["resource.labels.table_name"]
        yAxis:
          label: "Quality Score"
          scale: "LINEAR"
  
  - width: 6
    height: 4
    widget:
      title: "Failed Jobs"
      xyChart:
        dataSets:
        - timeSeriesQuery:
            timeSeriesFilter:
              filter: 'resource.type="dataproc_cluster" AND (textPayload:"failed" OR textPayload:"error")'
              aggregation:
                alignmentPeriod: "300s"
                perSeriesAligner: "ALIGN_RATE"
        yAxis:
          label: "Failed Jobs per Minute"
          scale: "LINEAR"
  
  - width: 12
    height: 4
    widget:
      title: "Storage Usage by Zone"
      xyChart:
        dataSets:
        - timeSeriesQuery:
            timeSeriesFilter:
              filter: 'resource.type="gcs_bucket"'
              aggregation:
                alignmentPeriod: "3600s"
                perSeriesAligner: "ALIGN_MEAN"
                groupByFields: ["resource.labels.bucket_name"]
        yAxis:
          label: "Storage (GB)"
          scale: "LINEAR"
EOF

# Alert policies
cat > monitoring/alerts/data-pipeline-alerts.yaml << 'EOF'
# Job Failure Alert
- displayName: "Data Pipeline Job Failures"
  documentation:
    content: "Alert when data pipeline jobs fail"
  conditions:
  - displayName: "Job failure rate"
    conditionThreshold:
      filter: 'resource.type="dataproc_cluster" AND (textPayload:"failed" OR textPayload:"FAILED")'
      comparison: "COMPARISON_GT"
      thresholdValue: 0
      duration: "300s"
      aggregations:
      - alignmentPeriod: "300s"
        perSeriesAligner: "ALIGN_RATE"
  alertStrategy:
    autoClose: "1800s"
  notificationChannels: []
  enabled: true

# Data Quality Alert
- displayName: "Data Quality Degradation"
  documentation:
    content: "Alert when data quality scores drop below threshold"
  conditions:
  - displayName: "Quality score below threshold"
    conditionThreshold:
      filter: 'resource.type="bigquery_table" AND resource.labels.table_id="data_quality_results"'
      comparison: "COMPARISON_LT"
      thresholdValue: 0.8
      duration: "300s"
      aggregations:
      - alignmentPeriod: "300s"
        perSeriesAligner: "ALIGN_MEAN"
        groupByFields: ["resource.labels.table_name"]
  alertStrategy:
    autoClose: "3600s"
  notificationChannels: []
  enabled: true

# High Storage Usage Alert
- displayName: "High Storage Usage"
  documentation:
    content: "Alert when GCS storage usage is high"
  conditions:
  - displayName: "Storage usage threshold"
    conditionThreshold:
      filter: 'resource.type="gcs_bucket"'
      comparison: "COMPARISON_GT"
      thresholdValue: 1000000000000  # 1TB in bytes
      duration: "900s"
      aggregations:
      - alignmentPeriod: "900s"
        perSeriesAligner: "ALIGN_MEAN"
  alertStrategy:
    autoClose: "3600s"
  notificationChannels: []
  enabled: true
EOF

# ===============================
# CREATE DOCUMENTATION
# ===============================

# Deployment guide
cat > docs/deployment-guide.md << 'EOF'
# GCP Data Platform Deployment Guide

## Prerequisites

### 1. GCP Project Setup
- GCP Project with billing enabled
- Required APIs enabled (handled automatically by deployment scripts)
- Appropriate IAM permissions for the deployment user

### 2. Tools Installation

#### Install Google Cloud CLI
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### Install sbt (for Scala builds)
```bash
# Ubuntu/Debian
echo "deb https://repo.scala-sbt.org/scalasbt/debian all main" | sudo tee /etc/apt/sources.list.d/sbt.list
curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | sudo apt-key add
sudo apt-get update
sudo apt-get install sbt

# macOS
brew install sbt
```

#### Install Maven (for Dataflow templates)
```bash
# Ubuntu/Debian
sudo apt-get install maven

# macOS
brew install maven
```

#### Install Terraform (optional)
```bash
# Ubuntu/Debian
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# macOS
brew install terraform
```

## Deployment Options

### Option 1: Quick Deployment (Recommended)

1. **Set Environment Variables**
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GCS_BUCKET="your-unique-bucket-name"
export DATAPROC_REGION="us-central1"
```

2. **Run Automated Deployment**
```bash
# Make scripts executable
chmod +x deployment/scripts/*.sh

# Deploy infrastructure and applications
./deployment/scripts/build-and-deploy.sh
```

3. **Configure Database Credentials**
```bash
./deployment/scripts/setup-secrets.sh
```

4. **Test with Sample Pipeline**
```bash
./deployment/scripts/run-sample-ingestion.sh
```

### Option 2: Terraform Deployment

1. **Deploy Infrastructure with Terraform**
```bash
./deployment/scripts/deploy-with-terraform.sh
```

2. **Build and Deploy Applications**
```bash
./deployment/scripts/build-and-deploy.sh
```

## Manual Deployment Steps

If you prefer to deploy manually:

### 1. Enable APIs
```bash
gcloud services enable dataproc.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable dataflow.googleapis.com
gcloud services enable pubsub.googleapis.com
```

### 2. Create GCS Bucket
```bash
gsutil mb gs://$GCS_BUCKET
```

### 3. Build Backend Service
```bash
cd backend-service
sbt clean assembly
cd ..
```

### 4. Upload JARs and Scripts
```bash
gsutil cp backend-service/target/scala-2.12/data-platform-backend-assembly-1.0.0.jar gs://$GCS_BUCKET/jars/
gsutil -m cp -r data-pipelines/* gs://$GCS_BUCKET/scripts/
```

### 5. Create BigQuery Datasets
```bash
for dataset in raw structured refined analysis monitoring; do
    bq mk --dataset --location=US $GOOGLE_CLOUD_PROJECT:$dataset
done
```

### 6. Create Dataproc Cluster
```bash
gcloud dataproc clusters create data-platform-cluster \
    --region=$DATAPROC_REGION \
    --zone=${DATAPROC_REGION}-a \
    --master-machine-type=n1-standard-4 \
    --num-workers=2 \
    --worker-machine-type=n1-standard-4 \
    --image-version=2.1-debian11 \
    --enable-autoscaling \
    --max-workers=10 \
    --properties="spark:spark.serializer=org.apache.spark.serializer.KryoSerializer,spark:spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
```

## Configuration

### Database Credentials
Store database connection details in Secret Manager:

```json
{
  "url": "jdbc:oracle:thin:@host:port:sid",
  "username": "your_username",
  "password": "your_password",
  "driver": "oracle.jdbc.driver.OracleDriver"
}
```

### Application Configuration
Edit `backend-service/src/main/resources/application.conf`:

```hocon
dataplatform {
  project-id = ${GOOGLE_CLOUD_PROJECT}
  gcs-bucket = ${GCS_BUCKET}
  
  validation {
    quality-threshold = 0.8  # Adjust as needed
    max-error-rate = 0.1
  }
}
```

## Monitoring Setup

### 1. Create Monitoring Dashboard
```bash
gcloud monitoring dashboards create --config-from-file=monitoring/dashboards/data-platform-dashboard.yaml
```

### 2. Set up Alerting
```bash
# Configure notification channels first in GCP Console
# Then create alert policies
gcloud alpha monitoring policies create --policy-from-file=monitoring/alerts/data-pipeline-alerts.yaml
```

## Verification

### Check Infrastructure
```bash
# Verify cluster
gcloud dataproc clusters list --region=$DATAPROC_REGION

# Verify BigQuery datasets
bq ls

# Verify GCS bucket
gsutil ls gs://$GCS_BUCKET/
```

### Run Test Pipeline
```bash
./deployment/scripts/run-sample-ingestion.sh
```

### Monitor Jobs
- **Dataproc Console**: https://console.cloud.google.com/dataproc/jobs
- **BigQuery Console**: https://console.cloud.google.com/bigquery
- **Cloud Monitoring**: https://console.cloud.google.com/monitoring

## Troubleshooting

### Common Issues

#### 1. sbt Build Failures
```bash
# Clear cache and retry
sbt clean
rm -rf ~/.sbt ~/.ivy2
sbt assembly
```

#### 2. Permission Errors
```bash
# Check service account permissions
gcloud projects get-iam-policy $GOOGLE_CLOUD_PROJECT

# Grant required roles
PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_PROJECT --format="value(projectNumber)")
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

#### 3. Dataproc Job Failures
```bash
# Check job logs
gcloud dataproc jobs describe JOB_ID --region=$DATAPROC_REGION

# SSH to cluster for debugging
gcloud dataproc clusters describe data-platform-cluster --region=$DATAPROC_REGION
```

#### 4. Iceberg Table Issues
```bash
# Check Iceberg warehouse location
gsutil ls gs://$GCS_BUCKET/iceberg-warehouse/

# Verify Spark configuration
gcloud dataproc clusters describe data-platform-cluster --region=$DATAPROC_REGION --format="value(config.softwareConfig.properties)"
```

## Cleanup

### Remove Dataproc Cluster
```bash
gcloud dataproc clusters delete data-platform-cluster --region=$DATAPROC_REGION
```

### Remove with Terraform
```bash
cd deployment/terraform
terraform destroy -var="project_id=$GOOGLE_CLOUD_PROJECT" -var="bucket_name=$GCS_BUCKET"
```

### Manual Cleanup
```bash
# Delete BigQuery datasets
for dataset in raw structured refined analysis monitoring; do
    bq rm -r -f $GOOGLE_CLOUD_PROJECT:$dataset
done

# Delete GCS bucket
gsutil rm -r gs://$GCS_BUCKET

# Delete secrets
gcloud secrets delete oracle-db-credentials
gcloud secrets delete postgres-db-credentials
```
EOF

# Pipeline development guide
cat > docs/pipeline-guide.md << 'EOF'
# Pipeline Development Guide

## Pipeline Architecture

The GCP Data Platform follows a medallion architecture with four zones:

1. **Raw Zone**: Unprocessed data from sources
2. **Structured Zone**: Cleaned and standardized data
3. **Refined Zone**: Business logic applied and enriched data
4. **Analysis Zone**: Aggregated data for analytics and reporting

## Pipeline Types

### 1. Ingestion Pipelines

#### Full Load Ingestion
Used for complete table extracts, typically for dimension tables or initial loads.

**Example Usage:**
```bash
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

#### Incremental Ingestion
Used for extracting only changed or new records based on timestamps or change flags.

**Example Usage:**
```bash
gcloud dataproc jobs submit spark \
    --cluster=data-platform-cluster \
    --class=com.dataplatform.pipelines.ingestion.PostgresIngestion \
    -- \
    --source-table=orders \
    --target-table=raw.postgres_orders \
    --secret-id=postgres-db-credentials \
    --incremental-column=last_modified \
    --last-value=2024-01-01T00:00:00
```

#### Real-time CDC
Processes change data capture events from Pub/Sub in near real-time.

**Example Usage:**
```bash
gcloud dataproc jobs submit spark \
    --cluster=data-platform-cluster \
    --class=com.dataplatform.pipelines.ingestion.CDCProcessor \
    -- \
    --pubsub-subscription=cdc-changes \
    --target-table=raw.cdc_changes
```

### 2. Transformation Pipelines

#### Raw to Structured
Cleans, standardizes, and validates raw data.

**Key Operations:**
- Column name standardization
- Data type conversions
- Basic data cleansing
- Data quality scoring
- Null handling

#### Structured to Refined
Applies business logic and enriches data.

**Key Operations:**
- Business rule implementation
- Data enrichment from lookup tables
- Customer segmentation
- Derived column calculations
- Advanced validations

#### Refined to Analysis
Creates aggregations and metrics for analytics.

**Key Operations:**
- Data aggregation
- Metric calculations
- Dimensional modeling
- Time-series analysis

### 3. Data Quality Pipelines

Validates data quality at each zone with configurable rules.

**Example Usage:**
```bash
gcloud dataproc jobs submit spark \
    --cluster=data-platform-cluster \
    --class=com.dataplatform.pipelines.validation.DataQualityCheck \
    -- \
    --source-table=structured.customers \
    --zone=structured
```

## Custom Pipeline Development

### Creating a New Ingestion Pipeline

1. **Create Pipeline Class**
```scala
package com.dataplatform.pipelines.ingestion

import org.apache.spark.sql.SparkSession
import com.dataplatform.core._
import com.dataplatform.monitoring._

object CustomIngestion {
  def main(args: Array[String]): Unit = {
    #!/bin/bash

# GCP Data Platform Project Structure Generator
# This script creates the complete folder structure and files for the GCP Data Platform

set -e

PROJECT_NAME="gcp-data-platform"
BASE_DIR=$(pwd)

echo "=== Creating GCP Data Platform Project Structure ==="
echo "Project will be created in: $BASE_DIR/$PROJECT_NAME"

# Create main project directory
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

echo "Creating directory structure..."

# ===============================
# CREATE DIRECTORY STRUCTURE
# ===============================

# Backend Service
mkdir -p backend-service/src/main/scala/com/dataplatform/{core,ingestion,transformation,monitoring,config}
mkdir -p backend-service/src/main/resources
mkdir -p backend-service/src/test/scala

# Data Pipelines
mkdir -p data-pipelines/{ingestion,transformation,validation}

# Dataflow Templates
mkdir -p dataflow-templates/{cdc-realtime-processor,file-streaming-processor}
mkdir -p dataflow-templates/cdc-realtime-processor/src/main/java/com/dataplatform/dataflow

# Dataform Pipelines
mkdir -p dataform-pipelines/{real-time-analytics,materialized-views}
mkdir -p dataform-pipelines/real-time-analytics/definitions

# Deployment
mkdir -p deployment/{terraform,scripts,configs}

# Monitoring
mkdir -p monitoring/{dashboards,alerts}

# Documentation
mkdir -p docs

echo "Directory structure created successfully!"

# ===============================
# CREATE BACKEND SERVICE FILES
# ===============================

echo "Creating backend service files..."

# SecretManager.scala
cat > backend-service/src/main/scala/com/dataplatform/core/SecretManager.scala << 'EOF'
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
EOF

# DatabaseConnector.scala
cat > backend-service/src/main/scala/com/dataplatform/core/DatabaseConnector.scala << 'EOF'
package com.dataplatform.core

import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
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
EOF

# FileProcessor.scala
cat > backend-service/src/main/scala/com/dataplatform/core/FileProcessor.scala << 'EOF'
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
EOF

# IcebergManager.scala
cat > backend-service/src/main/scala/com/dataplatform/core/IcebergManager.scala << 'EOF'
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
EOF

# ValidationEngine.scala
cat > backend-service/src/main/scala/com/dataplatform/core/ValidationEngine.scala << 'EOF'
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
EOF

# AuditLogger.scala
cat > backend-service/src/main/scala/com/dataplatform/monitoring/AuditLogger.scala << 'EOF'
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
EOF

# LineageTracker.scala
cat > backend-service/src/main/scala/com/dataplatform/monitoring/LineageTracker.scala << 'EOF'
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
EOF

# ConfigManager.scala
cat > backend-service/src/main/scala/com/dataplatform/config/ConfigManager.scala << 'EOF'
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
  
  def getIcebergWarehouse: String = {
    config.getString("dataplatform.iceberg.warehouse")
      .replace("${dataplatform.gcs-bucket}", getGcsBucket)
  }
  
  def getValidationQualityThreshold: Double = {
    config.getDouble("dataplatform.validation.quality-threshold")
  }
  
  def getMaxErrorRate: Double = {
    config.getDouble("dataplatform.validation.max-error-rate")
  }
  
  def getAuditTable: String = {
    config.getString("dataplatform.monitoring.audit-table")
      .replace("${dataplatform.project-id}", getProjectId)
  }
  
  def getLineageTable: String = {
    config.getString("dataplatform.monitoring.lineage-table")
      .replace("${dataplatform.project-id}", getProjectId)
  }
}
EOF

# build.sbt
cat > backend-service/build.sbt << 'EOF'
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
      
      // Configuration
      "com.typesafe" % "config" % "1.4.2",
      
      // Testing
      "org.scalatest" %% "scalatest" % "3.2.15" % Test
    ),
    
    assembly / assemblyMergeStrategy := {
      case PathList("META-INF", xs @ _*) => MergeStrategy.discard
      case "application.conf" => MergeStrategy.concat
      case x => MergeStrategy.first
    }
  )
EOF

# application.conf
cat > backend-service/src/main/resources/application.conf << 'EOF'
dataplatform {
  project-id = ${?GOOGLE_CLOUD_PROJECT}
  gcs-bucket = ${?GCS_BUCKET}
  
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
  
  spark {
    serializer = "org.apache.spark.serializer.KryoSerializer"
    sql.extensions = "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
    sql.catalog.iceberg = "org.apache.iceberg.spark.SparkCatalog"
    sql.catalog.iceberg.type = "hadoop"
    sql.catalog.iceberg.warehouse = ${dataplatform.iceberg.warehouse}
  }
}
EOF

echo "Backend service files created successfully!"

# ===============================
# CREATE PIPELINE FILES
# ===============================

echo "Creating pipeline files..."

# Oracle Ingestion Pipeline
cat > data-pipelines/ingestion/oracle-ingestion.scala << 'EOF'
package com.dataplatform.pipelines.ingestion

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import com.dataplatform.core._
import com.dataplatform.monitoring._
import com.dataplatform.config.ConfigManager
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
      .getOrCreate()
    
    val configManager = new ConfigManager(spark, "")
    val projectId = configManager.getProjectId
    spark.conf.set("spark.sql.catalog.iceberg.warehouse", configManager.getIcebergWarehouse)
    
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
EOF

# PostgreSQL Ingestion Pipeline
cat > data-pipelines/ingestion/postgres-ingestion.scala << 'EOF'
package com.dataplatform.pipelines.ingestion

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import com.dataplatform.core._
import com.dataplatform.monitoring._
import com.dataplatform.config.ConfigManager
import java.time.Instant
import java.util.UUID

object PostgresIngestion {
  
  def main(args: Array[String]): Unit = {
    
    val spark = SparkSession.builder()
      .appName("Postgres-Ingestion")
      .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg.type", "hadoop")
      .getOrCreate()
    
    val configManager = new ConfigManager(spark, "")
    val projectId = configManager.getProjectId
    spark.conf.set("spark.sql.catalog.iceberg.warehouse", configManager.getIcebergWarehouse)
    
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
      val sourceTable = getArgValue(args, "--source-table", "users")
      val targetTable = getArgValue(args, "--target-table", "raw.postgres_users")
      val secretId = getArgValue(args, "--secret-id", "postgres-db-credentials")
      val incrementalColumn = getArgValue(args, "--incremental-column", "")
      val lastValue = getArgValue(args, "--last-value", "")
      
      auditLogger.logJobStart(jobId, "Postgres-Ingestion", targetTable, "INCREMENTAL_LOAD")
      
      // Build incremental query
      val baseQuery = s"SELECT * FROM $sourceTable"
      val query = if (incrementalColumn.nonEmpty && lastValue.nonEmpty) {
        s"$baseQuery WHERE $incrementalColumn > '$lastValue'"
      } else {
        baseQuery
      }
      
      println(s"Executing query: $query")
      
      // Extract data from PostgreSQL
      val postgresData = dbConnector.connectAndQuery(
        projectId = projectId,
        secretId = secretId,
        query = query
      )
      
      val recordCount = postgresData.count()
      println(s"Extracted $recordCount records from PostgreSQL")
      
      if (recordCount > 0) {
        // Add metadata
        val processedData = postgresData
          .withColumn("_ingestion_timestamp", current_timestamp())
          .withColumn("_source_system", lit("postgresql"))
          .withColumn("_source_table", lit(sourceTable))
          .withColumn("_partition_date", current_date())
        
        // Write to Iceberg raw zone
        icebergManager.writeToIceberg(
          df = processedData,
          tableName = targetTable,
          writeMode = "append",
          partitionCols = Seq("_partition_date")
        )
        
        // Track lineage
        lineageTracker.trackTableLineage(
          sourceTable = s"postgresql.$sourceTable",
          targetTable = targetTable,
          transformation = "incremental_load_ingestion",
          jobId = jobId
        )
        
        println(s"Successfully ingested $recordCount records to $targetTable")
      } else {
        println("No new records found for ingestion")
      }
      
      auditLogger.logJobCompletion(
        jobId = jobId,
        jobName = "Postgres-Ingestion",
        tableName = targetTable,
        operation = "INCREMENTAL_LOAD",
        recordsProcessed = recordCount,
        startTime = startTime,
        status = "COMPLETED"
      )
      
    } catch {
      case e: Exception =>
        auditLogger.logJobCompletion(
          jobId = jobId,
          jobName = "Postgres-Ingestion",
          tableName = args.find(_.startsWith("--target-table")).map(_.split("=", 2)(1)).getOrElse("unknown"),
          operation = "INCREMENTAL_LOAD",
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
EOF

# File Ingestion Pipeline
cat > data-pipelines/ingestion/file-ingestion.scala << 'EOF'
package com.dataplatform.pipelines.ingestion

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import com.dataplatform.core._
import com.dataplatform.monitoring._
import com.dataplatform.config.ConfigManager
import java.time.Instant
import java.util.UUID

object FileIngestion {
  
  def main(args: Array[String]): Unit = {
    
    val spark = SparkSession.builder()
      .appName("File-Ingestion")
      .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg.type", "hadoop")
      .getOrCreate()
    
    val configManager = new ConfigManager(spark, "")
    val projectId = configManager.getProjectId
    spark.conf.set("spark.sql.catalog.iceberg.warehouse", configManager.getIcebergWarehouse)
    
    val jobId = UUID.randomUUID().toString
    val startTime = Instant.now()
    
    // Initialize services
    val fileProcessor = new FileProcessor(spark)
    val icebergManager = new IcebergManager(spark)
    val validationEngine = new ValidationEngine(spark)
    val auditLogger = new AuditLogger(spark, projectId)
    val lineageTracker = new LineageTracker(spark, projectId)
    
    try {
      // Parse arguments
      val filePath = getArgValue(args, "--file-path", "")
      val fileType = getArgValue(args, "--file-type", "csv")
      val targetTable = getArgValue(args, "--target-table", "raw.file_data")
      val sheetName = getArgValue(args, "--sheet-name", "")
      val delimiter = getArgValue(args, "--delimiter", ",")
      
      if (filePath.isEmpty) {
        throw new IllegalArgumentException("--file-path is required")
      }
      
      auditLogger.logJobStart(jobId, "File-Ingestion", targetTable, "FILE_LOAD")
      
      println(s"Processing file: $filePath (type: $fileType)")
      
      // Process file based on type
      val fileData = fileType.toLowerCase match {
        case "csv" => 
          fileProcessor.processCSVFile(filePath, delimiter)
        case "excel" | "xlsx" => 
          val sheet = if (sheetName.nonEmpty) Some(sheetName) else None
          fileProcessor.processExcelFile(filePath, sheet)
        case "json" => 
          fileProcessor.processJSONFile(filePath)
        case "txt" | "text" => 
          fileProcessor.processTextFile(filePath, delimiter)
        case _ => 
          throw new IllegalArgumentException(s"Unsupported file type: $fileType")
      }
      
      val recordCount = fileData.count()
      println(s"Processed $recordCount records from file")
      
      // Standardize DataFrame
      val standardizedData = fileProcessor.standardizeDataFrame(fileData, addMetadata = true)
        .withColumn("_source_system", lit("file"))
        .withColumn("_file_type", lit(fileType))
        .withColumn("_partition_date", current_date())
      
      // Basic validation
      val validationRules = Seq(
        ValidationRule("non_empty_file", "File should contain records", "COUNT(*) > 0")
      )
      
      val validationResults = validationEngine.validateData(standardizedData, validationRules, "file_data")
      validationResults.foreach { result =>
        println(s"Validation: ${result.ruleName} - ${if (result.passed) "PASSED" else "FAILED"}: ${result.message}")
      }
      
      // Write to Iceberg raw zone
      icebergManager.writeToIceberg(
        df = standardizedData,
        tableName = targetTable,
        writeMode = "append",
        partitionCols = Seq("_partition_date")
      )
      
      // Track lineage
      lineageTracker.trackTableLineage(
        sourceTable = s"file.$filePath",
        targetTable = targetTable,
        transformation = "file_ingestion",
        jobId = jobId
      )
      
      auditLogger.logJobCompletion(
        jobId = jobId,
        jobName = "File-Ingestion",
        tableName = targetTable,
        operation = "FILE_LOAD",
        recordsProcessed = recordCount,
        startTime = startTime,
        status = "COMPLETED",
        metadata = Map(
          "file_path" -> filePath,
          "file_type" -> fileType
        )
      )
      
      println(s"Successfully ingested $recordCount records to $targetTable")
      
    } catch {
      case e: Exception =>
        auditLogger.logJobCompletion(
          jobId = jobId,
          jobName = "File-Ingestion",
          tableName = args.find(_.startsWith("--target-table")).map(_.split("=", 2)(1)).getOrElse("unknown"),
          operation = "FILE_LOAD",
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
EOF

# CDC Processor
cat > data-pipelines/ingestion/cdc-processor.scala << 'EOF'
package com.dataplatform.pipelines.ingestion

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.streaming.Trigger
import org.apache.spark.sql.types._
import com.dataplatform.core._
import com.dataplatform.monitoring._
import com.dataplatform.config.ConfigManager
import java.time.Instant
import java.util.UUID

object CDCProcessor {
  
  def main(args: Array[String]): Unit = {
    
    val spark = SparkSession.builder()
      .appName("CDC-Processor")
      .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg.type", "hadoop")
      .getOrCreate()
    
    val configManager = new ConfigManager(spark, "")
    val projectId = configManager.getProjectId
    spark.conf.set("spark.sql.catalog.iceberg.warehouse", configManager.getIcebergWarehouse)
    
    val jobId = UUID.randomUUID().toString
    
    // Initialize services
    val icebergManager = new IcebergManager(spark)
    val auditLogger = new AuditLogger(spark, projectId)
    val lineageTracker = new LineageTracker(spark, projectId)
    
    try {
      // Parse arguments
      val pubsubSubscription = getArgValue(args, "--pubsub-subscription", "cdc-changes")
      val targetTable = getArgValue(args, "--target-table", "raw.cdc_changes")
      val checkpointLocation = getArgValue(args, "--checkpoint-location", s"${configManager.getGcsBucket}/checkpoints/cdc-processor")
      
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
      
      // Write to Iceberg with streaming
      val query = processedCDC.writeStream
        .outputMode("append")
        .format("iceberg")
        .option("table", targetTable)
        .option("checkpointLocation", checkpointLocation)
        .trigger(Trigger.ProcessingTime("30 seconds"))
        .start()
      
      // Track streaming lineage
      lineageTracker.trackTableLineage(
        sourceTable = s"pubsub.$pubsubSubscription",
        targetTable = targetTable,
        transformation = "cdc_streaming_ingestion",
        jobId = jobId
      )
      
      println(s"CDC streaming started. Writing to $targetTable")
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
EOF

# Raw to Structured Transformation
cat > data-pipelines/transformation/raw-to-structured.scala << 'EOF'
package com.dataplatform.pipelines.transformation

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import com.dataplatform.core._
import com.dataplatform.monitoring._
import com.dataplatform.config.ConfigManager
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
      .getOrCreate()
    
    val configManager = new ConfigManager(spark, "")
    val projectId = configManager.getProjectId
    spark.conf.set("spark.sql.catalog.iceberg.warehouse", configManager.getIcebergWarehouse)
    
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
        // Standardize column names (convert to lowercase and snake_case)
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
        ValidationRule("quality_threshold", "Data quality score should be above threshold", s"_data_quality_score >= ${configManager.getValidationQualityThreshold}")
      )
      
      val validationResults = validationEngine.validateData(structuredData, structuredValidationRules, targetTable)
      
      validationResults.foreach { result =>
        println(s"Validation: ${result.ruleName} - ${if (result.passed) "PASSED" else "FAILED"}: ${result.message}")
      }
      
      // Filter out low quality records
      val qualityData = structuredData.filter(col("_data_quality_score") >= configManager.getValidationQualityThreshold)
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
          "data_quality_threshold" -> configManager.getValidationQualityThreshold.toString
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
EOF

# Structured to Refined Transformation
cat > data-pipelines/transformation/structured-to-refined.scala << 'EOF'
package com.dataplatform.pipelines.transformation

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import com.dataplatform.core._
import com.dataplatform.monitoring._
import com.dataplatform.config.ConfigManager
import java.time.Instant
import java.util.UUID

object StructuredToRefined {
  
  def main(args: Array[String]): Unit = {
    
    val spark = SparkSession.builder()
      .appName("Structured-To-Refined")
      .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg.type", "hadoop")
      .getOrCreate()
    
    val configManager = new ConfigManager(spark, "")
    val projectId = configManager.getProjectId
    spark.conf.set("spark.sql.catalog.iceberg.warehouse", configManager.getIcebergWarehouse)
    
    val jobId = UUID.randomUUID().toString
    val startTime = Instant.now()
    
    // Initialize services
    val icebergManager = new IcebergManager(spark)
    val validationEngine = new ValidationEngine(spark)
    val auditLogger = new AuditLogger(spark, projectId)
    val lineageTracker = new LineageTracker(spark, projectId)
    
    try {
      // Parse arguments
      val sourceTable = getArgValue(args, "--source-table", "structured.customers")
      val targetTable = getArgValue(args, "--target-table", "refined.customers_enriched")
      val processDate = getArgValue(args, "--process-date", "")
      
      auditLogger.logJobStart(jobId, "Structured-To-Refined", targetTable, "ENRICHMENT")
      
      // Read from structured zone
      var structuredData = icebergManager.readFromIceberg(sourceTable)
      
      // Filter by processing date if specified
      if (processDate.nonEmpty) {
        structuredData = structuredData.filter(col("_partition_date") === processDate)
      }
      
      val recordCount = structuredData.count()
      println(s"Processing $recordCount records from $sourceTable")
      
      // Business enrichment and calculations
      val refinedData = structuredData
        // Customer segmentation
        .withColumn("customer_segment", 
          when(col("is_recent_customer") && col("_data_quality_score") >= 0.8, "Premium")
          .when(col("is_recent_customer"), "Standard")
          .when(col("_data_quality_score") >= 0.8, "Legacy_High_Quality")
          .otherwise("Legacy_Standard")
        )
        
        // Geographic analysis from email domain
        .withColumn("is_business_email", 
          when(col("email_domain").isin("gmail.com", "yahoo.com", "hotmail.com", "outlook.com"), false)
          .otherwise(true)
        )
        
        // Customer lifecycle stage
        .withColumn("days_since_creation", datediff(current_date(), col("created_date")))
        .withColumn("lifecycle_stage",
          when(col("days_since_creation") <= 30, "New")
          .when(col("days_since_creation") <= 365, "Active")
          .when(col("days_since_creation") <= 1095, "Mature")
          .otherwise("Veteran")
        )
        
        // Contact preferences
        .withColumn("preferred_contact", 
          when(col("is_valid_email") && col("phone").isNotNull, "Both")
          .when(col("is_valid_email"), "Email")
          .when(col("phone").isNotNull, "Phone")
          .otherwise("None")
        )
        
        // Risk scoring
        .withColumn("data_completeness_score",
          (when(col("first_name").isNotNull, 0.2).otherwise(0) +
           when(col("last_name").isNotNull, 0.2).otherwise(0) +
           when(col("is_valid_email"), 0.3).otherwise(0) +
           when(col("phone").isNotNull && length(col("phone")) === 10, 0.3).otherwise(0))
        )
        
        // Add enrichment metadata
        .withColumn("_enrichment_timestamp", current_timestamp())
        .withColumn("_enrichment_version", lit("1.0"))
        
        // Select final refined columns
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
          col("customer_segment"),
          col("lifecycle_stage"),
          col("is_business_email"),
          col("preferred_contact"),
          col("data_completeness_score"),
          col("days_since_creation"),
          col("_source_system"),
          col("_ingestion_timestamp"),
          col("_processed_timestamp"),
          col("_enrichment_timestamp"),
          col("_enrichment_version"),
          col("_partition_date")
        )
      
      // Validate refined data
      val refinedValidationRules = Seq(
        ValidationRule("segment_valid", "Customer segment should be valid", 
          "customer_segment IN ('Premium', 'Standard', 'Legacy_High_Quality', 'Legacy_Standard')"),
        ValidationRule("lifecycle_valid", "Lifecycle stage should be valid", 
          "lifecycle_stage IN ('New', 'Active', 'Mature', 'Veteran')"),
        ValidationRule("completeness_range", "Data completeness score should be between 0 and 1", 
          "data_completeness_score >= 0 AND data_completeness_score <= 1")
      )
      
      val validationResults = validationEngine.validateData(refinedData, refinedValidationRules, targetTable)
      
      validationResults.foreach { result =>
        println(s"Validation: ${result.ruleName} - ${if (result.passed) "PASSED" else "FAILED"}: ${result.message}")
      }
      
      // Write to refined zone
      icebergManager.writeToIceberg(
        df = refinedData,
        tableName = targetTable,
        writeMode = "overwrite",
        partitionCols = Seq("_partition_date")
      )
      
      // Track lineage
      lineageTracker.trackColumnLineage(
        sourceTable = sourceTable,
        targetTable = targetTable,
        transformation = "structured_to_refined_enrichment",
        columns = Seq("customer_segment", "lifecycle_stage", "is_business_email", "preferred_contact", "data_completeness_score"),
        jobId = jobId
      )
      
      auditLogger.logJobCompletion(
        jobId = jobId,
        jobName = "Structured-To-Refined",
        tableName = targetTable,
        operation = "ENRICHMENT",
        recordsProcessed = recordCount,
        startTime = startTime,
        status = "COMPLETED"
      )
      
      println(s"Successfully enriched $recordCount records to $targetTable")
      
    } catch {
      case e: Exception =>
        auditLogger.logJobCompletion(
          jobId = jobId,
          jobName = "Structured-To-Refined",
          tableName = args.find(_.startsWith("--target-table")).map(_.split("=", 2)(1)).getOrElse("unknown"),
          operation = "ENRICHMENT",
          recordsProcessed = 0,
          startTime = startTime,
          status = "FAILED",
          errorMessage = Some(e.getMessage)
        )
        
        println(s"Enrichment failed: ${e.getMessage}")
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
EOF

# Refined to Analysis Transformation
cat > data-pipelines/transformation/refined-to-analysis.scala << 'EOF'
package com.dataplatform.pipelines.transformation

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import com.dataplatform.core._
import com.dataplatform.monitoring._
import com.dataplatform.config.ConfigManager
import java.time.Instant
import java.util.UUID

object RefinedToAnalysis {
  
  def main(args: Array[String]): Unit = {
    
    val spark = SparkSession.builder()
      .appName("Refined-To-Analysis")
      .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg.type", "hadoop")
      .getOrCreate()
    
    val configManager = new ConfigManager(spark, "")
    val projectId = configManager.getProjectId
    spark.conf.set("spark.sql.catalog.iceberg.warehouse", configManager.getIcebergWarehouse)
    
    val jobId = UUID.randomUUID().toString
    val startTime = Instant.now()
    
    // Initialize services
    val icebergManager = new IcebergManager(spark)
    val auditLogger = new AuditLogger(spark, projectId)
    val lineageTracker = new LineageTracker(spark, projectId)
    
    try {
      // Parse arguments
      val sourceTable = getArgValue(args, "--source-table", "refined.customers_enriched")
      val targetTable = getArgValue(args, "--target-table", "analysis.customer_analytics")
      val processDate = getArgValue(args, "--process-date", "")
      
      auditLogger.logJobStart(jobId, "Refined-To-Analysis", targetTable, "ANALYTICS")
      
      // Read from refined zone
      var refinedData = icebergManager.readFromIceberg(sourceTable)
      
      // Filter by processing date if specified
      if (processDate.nonEmpty) {
        refinedData = refinedData.filter(col("_partition_date") === processDate)
      }
      
      val recordCount = refinedData.count()
      println(s"Processing $recordCount records from $sourceTable")
      
      // Create analytics aggregations
      val analyticsData = refinedData
        .groupBy(
          col("customer_segment"),
          col("lifecycle_stage"),
          col("is_business_email"),
          col("preferred_contact"),
          col("_partition_date")
        )
        .agg(
          count("*").alias("customer_count"),
          avg("data_completeness_score").alias("avg_data_completeness"),
          min("created_date").alias("earliest_customer_date"),
          max("created_date").alias("latest_customer_date"),
          avg("days_since_creation").alias("avg_days_since_creation"),
          countDistinct("email_domain").alias("unique_email_domains")
        )
        .withColumn("_analytics_timestamp", current_timestamp())
        .withColumn("_analytics_version", lit("1.0"))
      
      // Write to analysis zone
      icebergManager.writeToIceberg(
        df = analyticsData,
        tableName = targetTable,
        writeMode = "overwrite",
        partitionCols = Seq("_partition_date")
      )
      
      // Track lineage
      lineageTracker.trackTableLineage(
        sourceTable = sourceTable,
        targetTable = targetTable,
        transformation = "refined_to_analysis_aggregation",
        jobId = jobId
      )
      
      val outputRecordCount = analyticsData.count()
      
      auditLogger.logJobCompletion(
        jobId = jobId,
        jobName = "Refined-To-Analysis",
        tableName = targetTable,
        operation = "ANALYTICS",
        recordsProcessed = outputRecordCount,
        startTime = startTime,
        status = "COMPLETED",
        metadata = Map(
          "input_records" -> recordCount.toString,
          "output_records" -> outputRecordCount.toString
        )
      )
      
      println(s"Successfully created $outputRecordCount analytics records in $targetTable from $recordCount input records")
      
    } catch {
      case e: Exception =>
        auditLogger.logJobCompletion(
          jobId = jobId,
          jobName = "Refined-To-Analysis",
          tableName = args.find(_.startsWith("--target-table")).map(_.split("=", 2)(1)).getOrElse("unknown"),
          operation = "ANALYTICS",
          recordsProcessed = 0,
          startTime = startTime,
          status = "FAILED",
          errorMessage = Some(e.getMessage)
        )
        
        println(s"Analytics transformation failed: ${e.getMessage}")
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
EOF

# Data Quality Check
cat > data-pipelines/validation/data-quality-check.scala << 'EOF'
package com.dataplatform.pipelines.validation

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import com.dataplatform.core._
import com.dataplatform.monitoring._
import com.dataplatform.config.ConfigManager
import java.time.Instant
import java.util.UUID

object DataQualityCheck {
  
  def main(args: Array[String]): Unit = {
    
    val spark = SparkSession.builder()
      .appName("Data-Quality-Check")
      .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
      .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
      .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
      .config("spark.sql.catalog.iceberg.type", "hadoop")
      .getOrCreate()
    
    val configManager = new ConfigManager(spark, "")
    val projectId = configManager.getProjectId
    spark.conf.set("spark.sql.catalog.iceberg.warehouse", configManager.getIcebergWarehouse)
    
    val jobId = UUID.randomUUID().toString
    val startTime = Instant.now()
    
    // Initialize services
    val icebergManager = new IcebergManager(spark)
    val validationEngine = new ValidationEngine(spark)
    val auditLogger = new AuditLogger(spark, projectId)
    
    try {
      // Parse arguments
      val sourceTable = getArgValue(args, "--source-table", "")
      val zone = getArgValue(args, "--zone", "structured") // raw, structured, refined, analysis
      
      if (sourceTable.isEmpty) {
        throw new IllegalArgumentException("--source-table is required")
      }
      
      auditLogger.logJobStart(jobId, "Data-Quality-Check", sourceTable, "VALIDATION")
      
      // Read data from specified table
      val data = icebergManager.readFromIceberg(sourceTable)
      val recordCount = data.count()
      
      println(s"Running data quality checks on $sourceTable with $recordCount records")
      
      // Define validation rules based on zone
      val validationRules = zone.toLowerCase match {
        case "raw" => getRawZoneValidationRules()
        case "structured" => getStructuredZoneValidationRules()
        case "refined" => getRefinedZoneValidationRules()
        case "analysis" => getAnalysisZoneValidationRules()
        case _ => validationEngine.getStandardValidationRules
      }
      
      // Run validations
      val validationResults = validationEngine.validateData(data, validationRules, sourceTable)
      
      // Report results
      println("\n=== Data Quality Check Results ===")
      validationResults.foreach { result =>
        val status = if (result.passed) "✓ PASSED" else "✗ FAILED"
        println(s"$status - ${result.ruleName}: ${result.message}")
      }
      
      // Calculate overall quality score
      val totalRules = validationResults.length
      val passedRules = validationResults.count(_.passed)
      val qualityScore = if (totalRules > 0) passedRules.toDouble / totalRules else 0.0
      
      println(f"\nOverall Quality Score: ${qualityScore * 100}%.1f%% ($passedRules/$totalRules rules passed)")
      
      // Store quality results
      storeQualityResults(spark, projectId, sourceTable, validationResults, qualityScore, jobId)
      
      // Determine job status
      val criticalFailures = validationResults.filter(r => !r.passed && r.severity == "ERROR")
      val status = if (criticalFailures.isEmpty) "COMPLETED" else "COMPLETED_WITH_WARNINGS"
      
      auditLogger.logJobCompletion(
        jobId = jobId,
        jobName = "Data-Quality-Check",
        tableName = sourceTable,
        operation = "VALIDATION",
        recordsProcessed = recordCount,
        startTime = startTime,
        status = status,
        metadata = Map(
          "quality_score" -> f"${qualityScore * 100}%.1f",
          "rules_passed" -> passedRules.toString,
          "total_rules" -> totalRules.toString,
          "critical_failures" -> criticalFailures.length.toString
        )
      )
      
      if (criticalFailures.nonEmpty) {
        println(s"\nWARNING: ${criticalFailures.length} critical validation(s) failed!")
        criticalFailures.foreach(f => println(s"  - ${f.message}"))
      }
      
    } catch {
      case e: Exception =>
        auditLogger.logJobCompletion(
          jobId = jobId,
          jobName = "Data-Quality-Check",
          tableName = args.find(_.startsWith("--source-table")).map(_.split("=", 2)(1)).getOrElse("unknown"),
          operation = "VALIDATION",
          recordsProcessed = 0,
          startTime = startTime,
          status = "FAILED",
          errorMessage = Some(e.getMessage)
        )
        
        println(s"Data quality check failed: ${e.getMessage}")
        e.printStackTrace()
        throw e
    } finally {
      spark.stop()
    }
  }
  
  private def getRawZoneValidationRules(): Seq[ValidationRule] = Seq(
    ValidationRule("data_exists", "Table should contain data", "COUNT(*) > 0"),
    ValidationRule("metadata_columns", "Should have ingestion metadata", "_ingestion_timestamp IS NOT NULL"),
    ValidationRule("source_system", "Should have source system info", "_source_system IS NOT NULL")
  )
  
  private def getStructuredZoneValidationRules(): Seq[ValidationRule] = Seq(
    ValidationRule("primary_key_exists", "Primary key should exist", "customer_id IS NOT NULL"),
    ValidationRule("no_duplicates", "No duplicate primary keys", "COUNT(*) = COUNT(DISTINCT customer_id)"),
    ValidationRule("processed_timestamp", "Should have processing timestamp", "_processed_timestamp IS NOT NULL"),
    ValidationRule("quality_score", "Should have data quality score", "_data_quality_score IS NOT NULL")
  )
  
  private def getRefinedZoneValidationRules(): Seq[ValidationRule] = Seq(
    ValidationRule("enrichment_complete", "Should have enrichment metadata", "_enrichment_timestamp IS NOT NULL"),
    ValidationRule("segment_valid", "Customer segment should be valid", 
      "customer_segment IN ('Premium', 'Standard', 'Legacy_High_Quality', 'Legacy_Standard')"),
    ValidationRule("lifecycle_valid", "Lifecycle stage should be valid", 
      "lifecycle_stage IN ('New', 'Active', 'Mature', 'Veteran')")
  )
  
  private def getAnalysisZoneValidationRules(): Seq[ValidationRule] = Seq(
    ValidationRule("aggregation_valid", "Should have valid aggregations", "customer_count > 0"),
    ValidationRule("analytics_timestamp", "Should have analytics timestamp", "_analytics_timestamp IS NOT NULL"),
    ValidationRule("completeness_range", "Average completeness should be valid", 
      "avg_data_completeness >= 0 AND avg_data_completeness <= 1")
  )
  
  private def storeQualityResults(
    spark: SparkSession,
    projectId: String,
    tableName: String,
    results: Seq[ValidationResult],
    qualityScore: Double,
    jobId: String
  ): Unit = {
    import spark.implicits._
    
    val qualityDF = results.map { result =>
      (
        jobId,
        tableName,
        result.ruleName,
        result.passed,
        result.failedRecords,
        result.totalRecords,
        result.severity,
        result.message,
        qualityScore,
        current_timestamp()
      )
    }.toDF(
      "job_id", "table_name", "rule_name", "passed", "failed_records", 
      "total_records", "severity", "message", "quality_score", "check_timestamp"
    )
    
    qualityDF.write
      .format("bigquery")
      .option("table", s"$projectId.monitoring.data_quality_results")
      .option("writeMethod", "direct")
      .mode("append")
      .save()
  }
  
  private def getArgValue(args: Array[String], key: String, default: String): String = {
    args.find(_.startsWith(s"$key="))
      .map(_.split("=", 2)(1))
      .getOrElse(default)
  }
}
EOF

echo "Pipeline files created successfully!"

# ===============================
# CREATE DATAFLOW TEMPLATES
# ===============================

echo "Creating Dataflow templates..."

# CDC Realtime Processor POM
cat > dataflow-templates/cdc-realtime-processor/pom.xml << 'EOF'
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
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
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
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
            <version>2.15.2</version>
        </dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>1.7.36</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>11</source>
                    <target>11</target>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-shade-plugin</artifactId>
                <version>3.4.1</version>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals>
                            <goal>shade</goal>
                        </goals>
                        <configuration>
                            <transformers>
                                <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                                    <mainClass>com.dataplatform.dataflow.CDCProcessor</mainClass>
                                </transformer>
                            </transformers>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
EOF

# CDC Processor Java
cat > dataflow-templates/cdc-realtime-processor/src/main/java/com/dataplatform/dataflow/CDCProcessor.java << 'EOF'
package com.dataplatform.dataflow;

import org.apache.beam.sdk.Pipeline;
import org.apache.beam.sdk.io.gcp.pubsub.PubsubIO;
import org.apache.beam.sdk.io.gcp.bigquery.BigQueryIO;
import org.apache.beam.sdk.options.*;
import org.apache.beam.sdk.transforms.*;
import org.apache.beam.sdk.values.PCollection;
import com.google.api.services.bigquery.model.TableRow;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;
import org.apache.beam.sdk.transforms.windowing.FixedWindows;
import org.apache.beam.sdk.transforms.windowing.Window;
import org.joda.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CDCProcessor {
    
    private static final Logger LOG = LoggerFactory.getLogger(CDCProcessor.class);
    
    public interface CDCProcessorOptions extends PipelineOptions {
        @Description("Pub/Sub subscription for CDC events")
        @Validation.Required
        String getSubscription();
        void setSubscription(String subscription);
        
        @Description("BigQuery table for output")
        @Validation.Required
        String getOutputTable();
        void setOutputTable(String outputTable);
        
        @Description("Window duration in minutes")
        @Default.Integer(1)
        Integer getWindowDuration();
        void setWindowDuration(Integer windowDuration);
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
            .apply("Apply Fixed Windows", 
                Window.<String>into(FixedWindows.of(Duration.standardMinutes(options.getWindowDuration()))))
            .apply("Parse and Transform CDC Events", 
                ParDo.of(new ParseCDCEvent()));
        
        transformedEvents.apply("Write to BigQuery",
            BigQueryIO.writeTableRows()
                .to(options.getOutputTable())
                .withWriteDisposition(BigQueryIO.Write.WriteDisposition.WRITE_APPEND)
                .withCreateDisposition(BigQueryIO.Write.CreateDisposition.CREATE_NEVER));
        
        pipeline.run();
    }
    
    static class ParseCDCEvent extends DoFn<String, TableRow> {
        private final ObjectMapper mapper = new ObjectMapper();
        
        @ProcessElement
        public void processElement(ProcessContext c) {
            try {
                String json = c.element();
                JsonNode node = mapper.readTree(json);
                
                TableRow row = new TableRow();
                
                // Extract CDC fields
                row.set("operation", node.get("operation").asText());
                row.set("table_name", node.get("table_name").asText());
                row.set("lsn", node.get("lsn").asText());
                row.set("timestamp", node.get("timestamp").asText());
                
                // Handle before/after data
                JsonNode beforeData = node.get("before");
                JsonNode afterData = node.get("after");
                
                if (beforeData != null && !beforeData.isNull()) {
                    row.set("before_data", beforeData.toString());
                }
                
                if (afterData != null && !afterData.isNull()) {
                    row.set("after_data", afterData.toString());
                }
                
                // Add processing metadata
                row.set("processing_timestamp", c.timestamp().toString());
                row.set("partition_date", c.timestamp().toString().substring(0, 10));
                
                c.output(row);
                
            } catch (Exception e) {
                LOG.error("Error parsing CDC event: {}", c.element(), e);
                // Optionally send to dead letter queue
            }
        }
    }
}
EOF

echo "Dataflow templates created successfully!"

# ===============================
# CREATE DATAFORM PIPELINES
# ===============================

echo "Creating Dataform pipelines..."

# Dataform config
cat > dataform-pipelines/real-time-analytics/dataform.json << 'EOF'
{
  "defaultSchema": "analysis",
  "assertionSchema": "dataform_assertions",
  "warehouse": "bigquery",
  "defaultLocation": "US"
}
EOF

# Customer metrics SQL
cat > dataform-pipelines/real-time-analytics/definitions/customer_metrics.sqlx << 'EOF'
config {
  type: "incremental",
  schema: "analysis",
  description: "Real-time customer metrics aggregation",
  bigquery: {
    partitionBy: "DATE(updated_at)",
    clusterBy: ["customer_segment", "lifecycle_stage"]
  }
}

SELECT
  customer_id,
  customer_segment,
  lifecycle_stage,
  COUNT(*) as transaction_count,
  SUM(amount) as total_amount,
  AVG(amount) as avg_amount,
  MAX(transaction_timestamp) as last_transaction_time,
  CURRENT_TIMESTAMP() as updated_at
FROM ${ref("structured", "transactions")}
WHERE transaction_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
GROUP BY customer_id, customer_segment, lifecycle_stage

${ when(incremental(), `WHERE updated_at > (SELECT MAX(updated_at) FROM ${self()})`) }
EOF

# Daily customer summary
cat > dataform-pipelines/real-time-analytics/definitions/daily_customer_summary.sqlx << 'EOF'
config {
  type: "table",
  schema: "analysis",
  description: "Daily customer activity summary",
  bigquery: {
    partitionBy: "summary_date",
    clusterBy: ["customer_segment"]
  }
}

SELECT
  DATE(c.created_date) as summary_date,
  c.customer_segment,
  c.lifecycle_stage,
  COUNT(DISTINCT c.customer_id) as unique_customers,
  COUNT(DISTINCT CASE WHEN c.is_valid_email THEN c.customer_id END) as customers_with_email,
  COUNT(DISTINCT CASE WHEN c.phone IS NOT NULL THEN c.customer_id END) as customers_with_phone,
  AVG(c.data_completeness_score) as avg_completeness_score,
  COUNT(DISTINCT c.email_domain) as unique_email_domains
FROM ${ref("refined", "customers_enriched")} c
GROUP BY 
  DATE(c.created_date),
  c.customer_segment,
  c.lifecycle_stage
ORDER BY summary_date DESC, customer_segment
EOF

# Data quality dashboard
cat > dataform-pipelines/real-time-analytics/definitions/data_quality_dashboard.sqlx << 'EOF'
config {
  type: "view",
  schema: "analysis",
  description: "Data quality metrics dashboard"
}

WITH quality_trends AS (
  SELECT
    DATE(check_timestamp) as check_date,
    table_name,
    AVG(quality_score) as avg_quality_score,
    COUNT(*) as total_checks,
    SUM(CASE WHEN passed THEN 1 ELSE 0 END) as passed_checks,
    SUM(CASE WHEN severity = 'ERROR' AND NOT passed THEN 1 ELSE 0 END) as error_count
  FROM ${ref("monitoring", "data_quality_results")}
  WHERE check_timestamp >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  GROUP BY DATE(check_timestamp), table_name
)

SELECT
  check_date,
  table_name,
  avg_quality_score,
  SAFE_DIVIDE(passed_checks, total_checks) * 100 as pass_rate_percent,
  error_count,
  CASE 
    WHEN avg_quality_score >= 0.9 THEN 'Excellent'
    WHEN avg_quality_score >= 0.8 THEN 'Good'
    WHEN avg_quality_score >= 0.7 THEN 'Fair'
    ELSE 'Poor'
  END as quality_rating
FROM quality_trends
ORDER BY check_date DESC, table_name
EOF

echo "Dataform pipelines created successfully!"

# ===============================
# CREATE DEPLOYMENT SCRIPTS
# ===============================

echo "Creating deployment scripts..."

# Main build and deploy script
cat > deployment/scripts/build-and-deploy.sh << 'EOF'
#!/bin/bash

set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}
BUCKET_NAME=${GCS_BUCKET:-"your-data-platform-bucket"}
REGION=${DATAPROC_REGION:-"us-central1"}
BACKEND_SERVICE_JAR="data-platform-backend-assembly-1.0.0.jar"

echo "=== GCP Data Platform Build and Deployment ==="
echo "Project ID: $PROJECT_ID"
echo "GCS Bucket: $BUCKET_NAME"
echo "Region: $REGION"

# Validate required environment variables
if [ -z "$PROJECT_ID" ] || [ -z "$BUCKET_NAME" ]; then
    echo "Error: GOOGLE_CLOUD_PROJECT and GCS_BUCKET environment variables are required"
    exit 1
fi

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "Error: No active gcloud authentication found. Please run 'gcloud auth login'"
    exit 1
fi

# Set the active project
gcloud config set project $PROJECT_ID

echo "Enabling required APIs..."
gcloud services enable dataproc.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable dataflow.googleapis.com
gcloud services enable pubsub.googleapis.com

# Create GCS bucket if it doesn't exist
if ! gsutil ls gs://$BUCKET_NAME > /dev/null 2>&1; then
    echo "Creating GCS bucket: $BUCKET_NAME"
    gsutil mb gs://$BUCKET_NAME
else
    echo "GCS bucket already exists: $BUCKET_NAME"
fi

# Build backend service JAR
echo "Building backend service..."
cd backend-service
if ! command -v sbt &> /dev/null; then
    echo "Error: sbt is not installed. Please install sbt first."
    exit 1
fi

sbt clean assembly
if [ $? -ne 0 ]; then
    echo "Error: Backend service build failed"
    exit 1
fi

echo "Backend service built successfully"
cd ..

# Upload JAR to GCS
echo "Uploading backend service JAR to GCS..."
gsutil cp backend-service/target/scala-2.12/$BACKEND_SERVICE_JAR gs://$BUCKET_NAME/jars/

# Upload pipeline scripts
echo "Uploading pipeline scripts..."
gsutil -m cp -r data-pipelines/* gs://$BUCKET_NAME/scripts/

# Build and upload Dataflow templates
echo "Building and uploading Dataflow templates..."
cd dataflow-templates/cdc-realtime-processor
if ! command -v mvn &> /dev/null; then
    echo "Warning: Maven not found. Skipping Dataflow template build."
else
    mvn clean package -DskipTests
    gsutil cp target/cdc-realtime-processor-1.0.0.jar gs://$BUCKET_NAME/dataflow-templates/
fi
cd ../..

# Upload Dataform pipelines
echo "Uploading Dataform pipelines..."
gsutil -m cp -r dataform-pipelines/* gs://$BUCKET_NAME/dataform-pipelines/

# Create BigQuery datasets
echo "Creating BigQuery datasets..."
for dataset in raw structured refined analysis monitoring; do
    if ! bq ls -d $PROJECT_ID:$dataset > /dev/null 2>&1; then
        echo "Creating dataset: $dataset"
        bq mk --dataset --location=US $PROJECT_ID:$dataset
    else
        echo "Dataset already exists: $dataset"
    fi
done

# Create monitoring tables
echo "Creating monitoring tables..."

# Audit logs table
bq query --use_legacy_sql=false --replace=true "
CREATE OR REPLACE TABLE \`$PROJECT_ID.monitoring.audit_logs\` (
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
CLUSTER BY job_name, status
"

# Data lineage table
bq query --use_legacy_sql=false --replace=true "
CREATE OR REPLACE TABLE \`$PROJECT_ID.monitoring.data_lineage\` (
  source_table STRING,
  target_table STRING,
  transformation STRING,
  columns ARRAY<STRING>,
  timestamp TIMESTAMP,
  job_id STRING,
  level STRING
)
PARTITION BY DATE(timestamp)
CLUSTER BY source_table, target_table
"

# Data quality results table
bq query --use_legacy_sql=false --replace=true "
CREATE OR REPLACE TABLE \`$PROJECT_ID.monitoring.data_quality_results\` (
  job_id STRING,
  table_name STRING,
  rule_name STRING,
  passed BOOLEAN,
  failed_records INT64,
  total_records INT64,
  severity STRING,
  message STRING,
  quality_score FLOAT64,
  check_timestamp TIMESTAMP
)
PARTITION BY DATE(check_timestamp)
CLUSTER BY table_name, rule_name
"

# Check if Dataproc cluster exists
if ! gcloud dataproc clusters describe data-platform-cluster --region=$REGION > /dev/null 2>&1; then
    echo "Creating Dataproc cluster..."
    gcloud dataproc clusters create data-platform-cluster \
        --region=$REGION \
        --zone=${REGION}-a \
        --master-machine-type=n1-standard-4 \
        --master-boot-disk-size=50GB \
        --num-workers=2 \
        --worker-machine-type=n1-standard-4 \
        --worker-boot-disk-size=50GB \
        --image-version=2.1-debian11 \
        --enable-autoscaling \
        --max-workers=10 \
        --initialization-actions=gs://goog-dataproc-initialization-actions-${REGION}/conda/bootstrap-conda.sh \
        --optional-components=ZEPPELIN \
        --enable-ip-alias \
        --metadata="enable-cloud-sql-hive-metastore=false" \
        --properties="spark:spark.serializer=org.apache.spark.serializer.KryoSerializer,spark:spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,spark:spark.sql.catalog.iceberg=org.apache.iceberg.spark.SparkCatalog,spark:spark.sql.catalog.iceberg.type=hadoop,spark:spark.sql.catalog.iceberg.warehouse=gs://$BUCKET_NAME/iceberg-warehouse"
else
    echo "Dataproc cluster already exists: data-platform-cluster"
fi

echo "Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Configure your database credentials in Secret Manager:"
echo "   ./deployment/scripts/setup-secrets.sh"
echo "2. Run sample ingestion job:"
echo "   ./deployment/scripts/run-sample-ingestion.sh"
echo "3. Monitor jobs in GCP Console:"
echo "   https://console.cloud.google.com/dataproc/jobs?project=$PROJECT_ID&region=$REGION"
EOF

# Setup secrets script
cat > deployment/scripts/setup-secrets.sh << 'EOF'
#!/bin/bash

set -e

PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}

echo "=== Setting up Secret Manager secrets ==="
echo "Project ID: $PROJECT_ID"

# Function to create or update secret
create_or_update_secret() {
    local secret_name=$1
    local secret_data=$2
    
    if gcloud secrets describe $secret_name --project=$PROJECT_ID > /dev/null 2>&1; then
        echo "Updating existing secret: $secret_name"
        echo "$secret_data" | gcloud secrets versions add $secret_name --data-file=-
    else
        echo "Creating new secret: $secret_name"
        echo "$secret_data" | gcloud secrets create $secret_name --data-file=-
    fi
}

# Oracle database credentials
echo "Setting up Oracle database credentials..."
read -p "Oracle host (e.g., your-oracle-host:1521:XE): " oracle_host
read -p "Oracle username: " oracle_username
read -s -p "Oracle password: " oracle_password
echo

oracle_credentials=$(cat << EOF
{
  "url": "jdbc:oracle:thin:@$oracle_host",
  "username": "$oracle_username",
  "password": "$oracle_password",
  "driver": "oracle.jdbc.driver.OracleDriver"
}
EOF
)

create_or_update_secret "oracle-db-credentials" "$oracle_credentials"

# PostgreSQL database credentials
echo "Setting up PostgreSQL database credentials..."
read -p "PostgreSQL host (e.g., your-postgres-host:5432/your_db): " postgres_host
read -p "PostgreSQL username: " postgres_username
read -s -p "PostgreSQL password: " postgres_password
echo

postgres_credentials=$(cat << EOF
{
  "url": "jdbc:postgresql://$postgres_host",
  "username": "$postgres_username",
  "password": "$postgres_password",
  "driver": "org.postgresql.Driver"
}
EOF
)

create_or_update_secret "postgres-db-credentials" "$postgres_credentials"

# Grant Secret Manager access to Dataproc service account
echo "Granting Secret Manager access to Dataproc service account..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/storage.objectAdmin"

echo "Secret setup completed successfully!"
echo "Secrets created:"
echo "- oracle-db-credentials"
echo "- postgres-db-credentials"
EOF

# Sample ingestion script
cat > deployment/scripts/run-sample-ingestion.sh << 'EOF'
#!/bin/bash

set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}
BUCKET_NAME=${GCS_BUCKET:-"your-data-platform-bucket"}
CLUSTER_NAME=${DATAPROC_CLUSTER:-"data-platform-cluster"}
REGION=${DATAPROC_REGION:-"us-central1"}

echo "=== Running Sample Data Pipeline ==="
echo "Project ID: $PROJECT_ID"
echo "Cluster: $CLUSTER_NAME"
echo "Region: $REGION"

# Check if cluster exists
if ! gcloud dataproc clusters describe $CLUSTER_NAME --region=$REGION > /dev/null 2>&1; then
    echo "Error: Dataproc cluster '$CLUSTER_NAME' not found in region '$REGION'"
    echo "Please run the deployment script first: ./deployment/scripts/build-and-deploy.sh"
    exit 1
fi

# Submit Oracle ingestion job
echo "Submitting Oracle ingestion job..."
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

# Wait a bit before submitting the next job
sleep 30

# Submit transformation job
echo "Submitting Raw to Structured transformation job..."
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

# Wait a bit before submitting the next job
sleep 30

# Submit enrichment job
echo "Submitting Structured to Refined enrichment job..."
gcloud dataproc jobs submit spark \
    --cluster=$CLUSTER_NAME \
    --region=$REGION \
    --class=com.dataplatform.pipelines.transformation.StructuredToRefined \
    --jars=gs://$BUCKET_NAME/jars/data-platform-backend-assembly-1.0.0.jar \
    --properties="spark.executor.memory=4g,spark.driver.memory=2g,spark.executor.cores=2" \
    -- \
    --source-table=structured.customers \
    --target-table=refined.customers_enriched \
    --process-date=$(date +%Y-%m-%d)

echo "Enrichment job submitted successfully!"

# Submit data quality check
echo "Submitting data quality check..."
gcloud dataproc jobs submit spark \
    --cluster=$CLUSTER_NAME \
    --region=$REGION \
    --class=com.dataplatform.pipelines.validation.DataQualityCheck \
    --jars=gs://$BUCKET_NAME/jars/data-platform-backend-assembly-1.0.0.jar \
    --properties="spark.executor.memory=2g,spark.driver.memory=1g,spark.executor.cores=1" \
    -- \
    --source-table=refined.customers_enriched \
    --zone=refined

echo "Data quality check submitted successfully!"

echo ""
echo "All sample jobs submitted successfully!"
echo ""
echo "Monitor job progress in the GCP Console:"
echo "https://console.cloud.google.com/dataproc/jobs?project=$PROJECT_ID&region=$REGION"
echo ""
echo "Check audit logs in BigQuery:"
echo "https://console.cloud.google.com/bigquery?project=$PROJECT_ID&ws=!1m5!1m4!4m3!1s$PROJECT_ID!2smonitoring!3saudit_logs"
EOF

# Pipeline orchestration script
cat > deployment/scripts/run-daily-pipeline.sh << 'EOF'
#!/bin/bash

set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}
BUCKET_NAME=${GCS_BUCKET:-"your-data-platform-bucket"}
CLUSTER_NAME=${DATAPROC_CLUSTER:-"data-platform-cluster"}
REGION=${DATAPROC_REGION:-"us-central1"}
PROCESS_DATE=${1:-$(date +%Y-%m-%d)}

echo "=== Running Daily Data Pipeline for $PROCESS_DATE ==="

# Function to submit job and wait for completion
submit_and_wait() {
    local job_class=$1
    local job_name=$2
    shift 2
    local job_args="$@"
    
    echo "Submitting $job_name..."
    local job_id=$(gcloud dataproc jobs submit spark \
        --cluster=$CLUSTER_NAME \
        --region=$REGION \
        --class=$job_class \
        --jars=gs://$BUCKET_NAME/jars/data-platform-backend-assembly-1.0.0.jar \
        --properties="spark.executor.memory=4g,spark.driver.memory=2g,spark.executor.cores=2" \
        --format="value(reference.jobId)" \
        -- $job_args)
    
    echo "Job submitted with ID: $job_id"
    
    # Wait for job completion
    while true; do
        local status=$(gcloud dataproc jobs describe $job_id --region=$REGION --format="value(status.state)")
        case $status in
            "DONE")
                echo "$job_name completed successfully"
                break
                ;;
            "ERROR"|"CANCELLED")
                echo "Error: $job_name failed with status: $status"
                exit 1
                ;;
            *)
                echo "Waiting for $job_name to complete... (current status: $status)"
                sleep 30
                ;;
        esac
    done
}

# Step 1: Oracle Ingestion
submit_and_wait \
    "com.dataplatform.pipelines.ingestion.OracleIngestion" \
    "Oracle Ingestion" \
    --source-table=customers \
    --target-table=raw.oracle_customers \
    --secret-id=oracle-db-credentials \
    --partition-date=$PROCESS_DATE

# Step 2: PostgreSQL Ingestion
submit_and_wait \
    "com.dataplatform.pipelines.ingestion.PostgresIngestion" \
    "PostgreSQL Ingestion" \
    --source-table=users \
    --target-table=raw.postgres_users \
    --secret-id=postgres-db-credentials

# Step 3: Raw to Structured Transformation
submit_and_wait \
    "com.dataplatform.pipelines.transformation.RawToStructured" \
    "Raw to Structured Transformation" \
    --source-table=raw.oracle_customers \
    --target-table=structured.customers \
    --process-date=$PROCESS_DATE

# Step 4: Structured to Refined Transformation
submit_and_wait \
    "com.dataplatform.pipelines.transformation.StructuredToRefined" \
    "Structured to Refined Transformation" \
    --source-table=structured.customers \
    --target-table=refined.customers_enriched \
    --process-date=$PROCESS_DATE

# Step 5: Refined to Analysis Transformation
submit_and_wait \
    "com.dataplatform.pipelines.transformation.RefinedToAnalysis" \
    "Refined to Analysis Transformation" \
    --source-table=refined.customers_enriched \
    --target-table=analysis.customer_analytics \
    --process-date=$PROCESS_DATE

# Step 6: Data Quality Checks
submit_and_wait \
    "com.dataplatform.pipelines.validation.DataQualityCheck" \
    "Data Quality Check - Structured" \
    --source-table=structured.customers \
    --zone=structured

submit_and_wait \
    "com.dataplatform.pipelines.validation.DataQualityCheck" \
    "Data Quality Check - Refined" \
    --source-table=refined.customers_enriched \
    --zone=refined

echo "Daily pipeline for $PROCESS_DATE completed successfully!"
EOF

# Terraform deployment script
cat > deployment/scripts/deploy-with-terraform.sh << 'EOF'
#!/bin/bash

set -e

PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}
BUCKET_NAME=${GCS_BUCKET:-"your-data-platform-bucket"}
REGION=${DATAPROC_REGION:-"us-central1"}

echo "=== Deploying GCP Data Platform with Terraform ==="
echo "Project ID: $PROJECT_ID"
echo "Bucket: $BUCKET_NAME"
echo "Region: $REGION"

cd deployment/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan \
    -var="project_id=$PROJECT_ID" \
    -var="bucket_name=$BUCKET_NAME" \
    -var="region=$REGION"

# Apply deployment
read -p "Do you want to proceed with the deployment? (y/N): " confirm
if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    terraform apply \
        -var="project_id=$PROJECT_ID" \
        -var="bucket_name=$BUCKET_NAME" \
        -var="region=$REGION" \
        -auto-approve
    
    echo "Terraform deployment completed successfully!"
else
    echo "Deployment cancelled."
fi

cd ../..
EOF

# Make scripts executable
chmod +x deployment/scripts/*.sh

echo "Deployment scripts created successfully!"

# ===============================
# CREATE TERRAFORM FILES
# ===============================

echo "Creating Terraform infrastructure files..."

# Main Terraform configuration
cat > deployment/terraform/main.tf << 'EOF'
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0"
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
  description = "GCS Bucket Name for data platform"
  type        = string
}

variable "cluster_name" {
  description = "Dataproc cluster name"
  type        = string
  default     = "data-platform-cluster"
}

# Data sources
data "google_compute_default_service_account" "default" {}

data "google_project" "project" {
  project_id = var.project_id
}
EOF

# GCS resources
cat > deployment/terraform/storage.tf << 'EOF'
# Main data platform bucket
resource "google_storage_bucket" "data_platform_bucket" {
  name          = var.bucket_name
  location      = "US"
  force_destroy = false
  
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
  
  lifecycle_rule {
    condition {
      age = 1095  # 3 years
    }
    action {
      type          = "SetStorageClass"
      storage_class = "ARCHIVE"
    }
  }
  
  versioning {
    enabled = true
  }
  
  uniform_bucket_level_access = true
  
  labels = {
    environment = "data-platform"
    managed-by  = "terraform"
  }
}

# Bucket folders
resource "google_storage_bucket_object" "folders" {
  for_each = toset([
    "jars/",
    "scripts/",
    "dataflow-templates/",
    "dataform-pipelines/",
    "iceberg-warehouse/",
    "checkpoints/",
    "temp/"
  ])
  
  bucket  = google_storage_bucket.data_platform_bucket.name
  name    = each.value
  content = " "  # Empty content to create folder
}
EOF

# BigQuery resources
cat > deployment/terraform/bigquery.tf << 'EOF'
# BigQuery datasets
resource "google_bigquery_dataset" "raw" {
  dataset_id    = "raw"
  friendly_name = "Raw Data Zone"
  description   = "Raw ingested data from various sources"
  location      = "US"
  
  labels = {
    env        = "data-platform"
    zone       = "raw"
    managed-by = "terraform"
  }
  
  access {
    role          = "OWNER"
    user_by_email = data.google_compute_default_service_account.default.email
  }
}

resource "google_bigquery_dataset" "structured" {
  dataset_id    = "structured"
  friendly_name = "Structured Data Zone"
  description   = "Cleaned and standardized data"
  location      = "US"
  
  labels = {
    env        = "data-platform"
    zone       = "structured"
    managed-by = "terraform"
  }
  
  access {
    role          = "OWNER"
    user_by_email = data.google_compute_default_service_account.default.email
  }
}

resource "google_bigquery_dataset" "refined" {
  dataset_id    = "refined"
  friendly_name = "Refined Data Zone"
  description   = "Business logic applied and enriched data"
  location      = "US"
  
  labels = {
    env        = "data-platform"
    zone       = "refined"
    managed-by = "terraform"
  }
  
  access {
    role          = "OWNER"
    user_by_email = data.google_compute_default_service_account.default.email
  }
}

resource "google_bigquery_dataset" "analysis" {
  dataset_id    = "analysis"
  friendly_name = "Analysis Data Zone"
  description   = "Analytics and aggregated data for reporting"
  location      = "US"
  
  labels = {
    env        = "data-platform"
    zone       = "analysis"
    managed-by = "terraform"
  }
  
  access {
    role          = "OWNER"
    user_by_email = data.google_compute_default_service_account.default.email
  }
}

resource "google_bigquery_dataset" "monitoring" {
  dataset_id    = "monitoring"
  friendly_name = "Monitoring and Audit"
  description   = "Platform monitoring, auditing and lineage data"
  location      = "US"
  
  labels = {
    env        = "data-platform"
    zone       = "monitoring"
    managed-by = "terraform"
  }
  
  access {
    role          = "OWNER"
    user_by_email = data.google_compute_default_service_account.default.email
  }
}

# Monitoring tables
resource "google_bigquery_table" "audit_logs" {
  dataset_id = google_bigquery_dataset.monitoring.dataset_id
  table_id   = "audit_logs"
  
  time_partitioning {
    type  = "DAY"
    field = "start_time"
  }
  
  clustering = ["job_name", "status"]
  
  schema = jsonencode([
    {
      name = "job_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "job_name"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "table_name"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "operation"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "records_processed"
      type = "INTEGER"
      mode = "REQUIRED"
    },
    {
      name = "start_time"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "end_time"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name