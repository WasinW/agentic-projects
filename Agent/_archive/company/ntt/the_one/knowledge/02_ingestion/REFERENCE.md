# Ingestion Reference — Streaming & Messaging Comparison

> Cross-cloud comparison of streaming and messaging services.

## Streaming Platform Comparison

| Feature | **Confluent Kafka** | **GCP Pub/Sub** | **AWS MSK/Kinesis** | **Azure Event Hubs** | **Databricks** |
|---------|-------------------|----------------|-------------------|---------------------|---------------|
| Model | Pull-based log | Push-based | Pull (MSK) / Push (Kinesis) | Pull-based (AMQP) | Auto Loader |
| Ordering | Per-partition | Per-key (ordering key) | Per-shard/partition | Per-partition | Per-file |
| Retention | Configurable (infinite) | 31 days max | 7 days (Kinesis) / unlimited (MSK) | 90 days max | N/A |
| Schema Registry | Confluent SR | No native SR | Glue Schema Registry | Azure SR | Unity Catalog |
| Exactly-once | Yes (idempotent producer) | No (at-least-once) | Yes (MSK) / No (Kinesis) | No | Yes (structured streaming) |
| Cross-language | Yes (librdkafka) | Yes (gRPC) | Yes | Yes | Spark-native |
| Managed | Confluent Cloud | Fully managed | MSK Serverless | Fully managed | Managed Spark |

## When to Use What

| Scenario | Recommendation |
|----------|---------------|
| High-throughput event streaming | Confluent Kafka or MSK |
| GCP-native pub/sub | Google Pub/Sub |
| Simple message queue | Pub/Sub or SQS |
| Log aggregation | Kafka + Kafka Connect |
| File-based ingestion | Databricks Auto Loader or GCS notifications |
| CDC from database | Debezium (Kafka Connect) or Datastream |

## Batch Ingestion Comparison

| Method | GCP | AWS | Azure | Databricks |
|--------|-----|-----|-------|------------|
| **API polling** | Dataflow (PeriodicImpulse) | Glue/Lambda | ADF REST connector | Spark batch |
| **Database extract** | Dataflow (ReadFromBigQuery) | Glue JDBC | ADF Copy Activity | Spark JDBC |
| **File landing** | GCS → Dataflow | S3 → Glue/Lambda | ADLS → ADF | Auto Loader |
| **CDC** | Datastream | DMS | Change Data Capture | Delta Live Tables |

## Detailed Reference

For comprehensive comparison, see:
- `archive/knowledge_base/COMPARISON/CROSS_CLOUD_COMPARISON.md` (Section 6: Streaming/Messaging)
- `archive/knowledge_base/GCP/CLOUD_SERVICE/GCP_CLOUD_SERVICES.md` (Section 3: Pub/Sub)
- `archive/knowledge_base/AWS/CLOUD_SERVICE/AWS_CLOUD_SERVICES.md` (Section 1: Kinesis/MSK)
