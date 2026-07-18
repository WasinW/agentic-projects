# Processing Reference — Engine Comparison

> Cross-cloud comparison of data processing engines.

## Processing Engine Comparison

| Feature | **Apache Beam/Dataflow** | **Apache Spark** | **AWS Glue** | **Flink** | **dbt/Dataform** |
|---------|------------------------|-----------------|-------------|-----------|-----------------|
| Model | Unified batch+stream | Micro-batch + Structured Streaming | Spark-based ETL | True streaming | SQL transforms |
| Language | Python, Java, Go | Python, Scala, Java, SQL | Python, Scala | Java, Scala, Python, SQL | SQL + Jinja |
| Managed | Dataflow (GCP) | Databricks, EMR, Dataproc | AWS Glue | Amazon KDA, Confluent | Dataform (GCP), dbt Cloud |
| Streaming | Native (watermarks, triggers) | Structured Streaming | Glue Streaming | Native (event time) | N/A (batch only) |
| Windowing | Fixed, sliding, session, global | Tumbling, sliding | Same as Spark | Tumbling, sliding, session | N/A |
| State | Stateful DoFns | MapState, checkpointing | Same as Spark | Keyed state, timers | N/A |
| Exactly-once | Yes (with supported sinks) | Yes (idempotent sinks) | Yes | Yes (checkpointing) | N/A |
| Cross-language | Yes (Java + Python via xlang) | Limited | No | No | N/A |
| Auto-scaling | Dataflow Autoscaling | Databricks Auto-scale | Glue Auto-scaling | Reactive scaling | N/A |

## When to Use What

| Scenario | Best Choice | Why |
|----------|------------|-----|
| Kafka → Iceberg + BQ (streaming) | **Beam/Dataflow** | Unified model, Java IcebergIO, GCP-native |
| Large batch ETL | **Spark/Dataproc** | Mature, fast shuffle, wide ecosystem |
| SQL transforms on warehouse | **Dataform/dbt** | Simple, version-controlled, incremental |
| Complex event processing | **Flink** | True event-time, low latency, rich state |
| Simple ETL without code | **AWS Glue** | Visual editor, Glue Catalog integration |
| ML pipeline | **Spark/Databricks** | MLlib, MLflow, GPU support |

## Beam vs Spark Feature Matrix

| Feature | Apache Beam | Apache Spark |
|---------|------------|-------------|
| Batch | Yes | Yes (native) |
| Streaming | Yes (native watermarks) | Structured Streaming (micro-batch) |
| Kafka connector | Java cross-language | Native Spark connector |
| Iceberg connector | Java IcebergIO (managed.Write) | SparkCatalog + IcebergSink |
| BQ connector | WriteToBigQuery (Storage Write API) | Spark BigQuery connector |
| CDC writes | BQ Storage Write API (use_cdc_writes) | Delta Lake Change Data Feed |
| DoFn pattern | ParDo(DoFn) | map/flatMap/mapPartitions |
| Windowing | Rich (fixed, sliding, session, custom) | Tumbling, sliding |
| Runner portability | Dataflow, Spark, Flink, Direct | Spark only |
| Python SDK maturity | Good (some cross-lang gaps) | Excellent (PySpark) |

## The1 Processing Choices

| Decision | Choice | Why |
|----------|--------|-----|
| Engine | Apache Beam on Dataflow | Unified batch+streaming, Java Kafka connector |
| Runner | DataflowRunner | GCP-native, auto-scaling, managed |
| Kafka connector | ReadFromKafka (Java cross-language) | Schema Registry support, Avro decoding |
| Transform pattern | DoFn chain (Extract → Decode → Transform → Write) | Explicit, testable, observable |
| CDC | BQ Storage Write API | Native CDC support, primary key dedup |

## Detailed Reference

For comprehensive comparison, see:
- `archive/knowledge_base/COMPARISON/CROSS_CLOUD_COMPARISON.md` (Section 4: Processing)
- `archive/knowledge_base/GCP/CLOUD_SERVICE/GCP_CLOUD_SERVICES.md` (Dataflow)
- `archive/knowledge_base/DATABRICKS/CLOUD_SERVICE/DATABRICKS_SERVICES.md` (Spark)
