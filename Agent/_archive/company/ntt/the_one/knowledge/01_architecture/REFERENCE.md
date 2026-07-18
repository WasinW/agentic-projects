# Architecture Reference — Cross-Cloud Patterns

> Reference material for cross-cloud architecture comparison. For The1 project-specific patterns, see INSTRUCTIONS.md.

## Platform Positioning (2026)

| Platform | Strategic Direction | Primary Format | Strengths |
|----------|-------------------|----------------|-----------|
| **GCP** | Iceberg-native lakehouse via BigLake | Apache Iceberg | Serverless, simplicity, cost-efficient |
| **AWS** | Iceberg-first via S3 Tables | Apache Iceberg | Breadth, flexibility, mature ecosystem |
| **Azure** | Delta-native via Fabric/OneLake | Delta Lake | Microsoft integration, Power BI, enterprise |
| **Databricks** | Delta + Iceberg interop via UniForm | Delta Lake | Multi-cloud, ML/AI, open governance |

## Architecture Pattern Comparison

| Pattern | Best For | Platforms | Trade-offs |
|---------|----------|-----------|------------|
| **Medallion (Bronze/Silver/Gold)** | Progressive data refinement | All platforms | Simple to understand; can lead to excessive copies |
| **Lambda (batch + stream)** | Mixed workloads with different SLAs | GCP (Dataflow), AWS (Kinesis + Glue) | Complex to maintain; two code paths |
| **Kappa (stream-only)** | Pure streaming with replay | GCP (Dataflow), Databricks (Structured Streaming) | Simpler; requires good replay capability |
| **Data Mesh** | Large organizations with domain teams | All platforms (Unity Catalog, Dataplex) | Organizational overhead; governance challenge |

## Decision Tree: When to Use What

```
Need real-time analytics?
├─ Yes → Streaming pipeline (Dataflow/Flink/Structured Streaming)
│   ├─ Kafka source? → Dataflow with ReadFromKafka (our choice)
│   └─ Pub/Sub source? → Dataflow with ReadFromPubSub
└─ No → Batch pipeline
    ├─ SQL-only transform? → Dataform / dbt / Spark SQL
    └─ Complex logic? → Dataflow batch / Spark / Glue

Need open table format?
├─ GCP → Iceberg via BigLake BLMS REST Catalog
├─ AWS → Iceberg via S3 Tables or Glue
├─ Azure → Delta Lake via Fabric
└─ Multi-cloud → Delta UniForm or Iceberg directly

Need CDC?
├─ BQ Storage Write API (our choice) → use_cdc_writes=True
├─ Delta Lake → Change Data Feed
└─ Iceberg → Row-level deletes (v2 spec)
```

## The1 Architecture Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Cloud | GCP | Existing investment, BigQuery strength |
| Processing | Apache Beam on Dataflow | Unified batch+streaming, Java Kafka connector |
| Source layer | Apache Iceberg on GCS | Open format, schema evolution, time-travel |
| Catalog | BigLake Metastore (BLMS REST) | Native GCP integration, vended-credentials |
| Warehouse | BigQuery | Serverless, Storage Write API, CDC support |
| Streaming | Confluent Kafka | Existing platform, SASL/SSL, Schema Registry |
| IaC | Terraform | Multi-team, workspace isolation |
| CI/CD | GitLab CI + Kaniko | Existing GitLab, container builds |

## Detailed Reference

For comprehensive cross-cloud comparisons, see:
- `archive/knowledge_base/COMPARISON/CROSS_CLOUD_COMPARISON.md`
- `archive/knowledge_base/COMPARISON/ARCHITECTURE_DECISION_GUIDE.md`
