# AWS Cloud Services for Data Engineering

> Comprehensive knowledge base covering streaming, orchestration, governance,
> data integration, security, and CI/CD services on AWS for data engineering.
>
> **Version**: 2.0 | **Last Updated**: 2026-03-05 | **Maintainer**: Data Platform Team

---

## Table of Contents

1. [Streaming & Messaging](#1-streaming--messaging)
2. [Orchestration](#2-orchestration)
3. [Data Governance](#3-data-governance)
4. [Data Integration](#4-data-integration)
5. [Security](#5-security)
6. [CI/CD](#6-cicd)
7. [References](#7-references)

---

## 1. Streaming & Messaging

### 1.1 Amazon Kinesis

Amazon Kinesis is a family of services for real-time data streaming and processing.

#### Kinesis Data Streams

Real-time data streaming with sub-second latency, ordered within shards.

```
┌───────────────────────────────────────────────────────────┐
│                  Kinesis Data Streams                      │
│                                                           │
│  Producers                    Shards                      │
│  ┌──────────┐   ┌──────┐    ┌──────────────────────────┐ │
│  │ App / SDK │──▶│Shard │    │ Shard = ordered sequence │ │
│  │ KPL       │   │  1   │    │ - 1 MB/s write           │ │
│  │ Agent     │   ├──────┤    │ - 2 MB/s read            │ │
│  │ Firehose  │   │Shard │    │ - Partition key routing   │ │
│  └──────────┘   │  2   │    │ - 24h-365d retention     │ │
│                  ├──────┤    └──────────────────────────┘ │
│                  │Shard │                                  │
│                  │  N   │    Consumers                     │
│                  └──┬───┘    ┌──────────────────────────┐ │
│                     │        │ KCL App, Lambda,          │ │
│                     └───────▶│ Firehose, Analytics,     │ │
│                              │ Redshift, EMR            │ │
│                              └──────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

**Capacity Modes:**

| Mode | Scaling | Pricing | Best For |
|------|---------|---------|----------|
| **On-Demand** | Auto (up to 200 MB/s write) | ~$0.08/GB in, ~$0.04/GB out | Variable/unpredictable traffic |
| **Provisioned** | Manual shard management | ~$0.015/shard-hr + $0.014/M PUT | Predictable, cost-sensitive |

**Enhanced Fan-Out:**

Standard consumers share the 2 MB/s per shard limit. Enhanced Fan-Out provides
a dedicated 2 MB/s per consumer per shard using HTTP/2 push:

```python
import boto3
import json

# Producer: Put records using KPL-like batching
kinesis = boto3.client('kinesis', region_name='us-east-1')

def put_events(stream_name: str, events: list[dict]) -> dict:
    records = [
        {
            'Data': json.dumps(event).encode('utf-8'),
            'PartitionKey': event['user_id']
        }
        for event in events
    ]
    return kinesis.put_records(
        StreamName=stream_name,
        Records=records
    )

# Consumer: Read with enhanced fan-out
def register_consumer(stream_arn: str, consumer_name: str) -> str:
    response = kinesis.register_stream_consumer(
        StreamARN=stream_arn,
        ConsumerName=consumer_name
    )
    return response['Consumer']['ConsumerARN']

# Subscribe to shard with enhanced fan-out (HTTP/2 push)
def subscribe_to_shard(consumer_arn: str, shard_id: str, starting_position: dict):
    response = kinesis.subscribe_to_shard(
        ConsumerARN=consumer_arn,
        ShardId=shard_id,
        StartingPosition=starting_position
    )
    for event in response['EventStream']:
        if 'SubscribeToShardEvent' in event:
            records = event['SubscribeToShardEvent']['Records']
            for record in records:
                data = json.loads(record['Data'])
                yield data
```

**Enhanced Fan-Out Pricing:**
- $0.015/consumer-shard-hr
- $0.013/GB data retrieved
- Up to 20 consumers per stream

#### Kinesis Data Firehose

Fully managed delivery stream to S3, Redshift, OpenSearch, Splunk, and HTTP endpoints.

```
┌────────────────────────────────────────────────────────────┐
│                  Kinesis Data Firehose                       │
│                                                             │
│  Sources              Transform            Destinations     │
│  ┌──────────┐        ┌──────────┐        ┌──────────────┐  │
│  │ Direct   │  ──▶   │ Lambda   │  ──▶   │ S3           │  │
│  │ PUT      │        │ Transform│        │ Redshift     │  │
│  │ Kinesis  │        │          │        │ OpenSearch   │  │
│  │ MSK      │        │ Format   │        │ Splunk       │  │
│  │ CloudWatch│       │ Convert  │        │ HTTP         │  │
│  └──────────┘        │ (Parquet │        │ Snowflake    │  │
│                       │  /ORC)  │        │ Iceberg      │  │
│                       └──────────┘        └──────────────┘  │
│                                                             │
│  Buffering: 1-15 min (time) or 1-128 MB (size)             │
│  Dynamic Partitioning: route to S3 prefixes by field        │
│  Format Conversion: JSON → Parquet/ORC (Glue Catalog)       │
└────────────────────────────────────────────────────────────┘
```

```bash
# Create a Firehose delivery stream with Parquet conversion and dynamic partitioning
aws firehose create-delivery-stream \
  --delivery-stream-name "events-to-s3" \
  --delivery-stream-type "DirectPut" \
  --extended-s3-destination-configuration '{
    "RoleARN": "arn:aws:iam::123456789012:role/FirehoseRole",
    "BucketARN": "arn:aws:s3:::my-data-lake",
    "Prefix": "events/year=!{partitionKeyFromQuery:year}/month=!{partitionKeyFromQuery:month}/day=!{partitionKeyFromQuery:day}/",
    "ErrorOutputPrefix": "errors/",
    "BufferingHints": {
      "SizeInMBs": 128,
      "IntervalInSeconds": 300
    },
    "CompressionType": "UNCOMPRESSED",
    "DataFormatConversionConfiguration": {
      "Enabled": true,
      "SchemaConfiguration": {
        "DatabaseName": "raw_db",
        "TableName": "events",
        "Region": "us-east-1",
        "RoleARN": "arn:aws:iam::123456789012:role/FirehoseGlueRole"
      },
      "InputFormatConfiguration": {
        "Deserializer": {
          "OpenXJsonSerDe": {}
        }
      },
      "OutputFormatConfiguration": {
        "Serializer": {
          "ParquetSerDe": {
            "Compression": "SNAPPY"
          }
        }
      }
    },
    "DynamicPartitioningConfiguration": {
      "Enabled": true
    },
    "ProcessingConfiguration": {
      "Enabled": true,
      "Processors": [
        {
          "Type": "MetadataExtraction",
          "Parameters": [
            {
              "ParameterName": "MetadataExtractionQuery",
              "ParameterValue": "{year: .event_time[:4], month: .event_time[5:7], day: .event_time[8:10]}"
            },
            {
              "ParameterName": "JsonParsingEngine",
              "ParameterValue": "JQ-1.6"
            }
          ]
        }
      ]
    }
  }'
```

**Firehose to Iceberg (2025+):**

Firehose now supports direct delivery to Apache Iceberg tables:

```bash
# Firehose to Iceberg table in Glue Catalog
aws firehose create-delivery-stream \
  --delivery-stream-name "events-to-iceberg" \
  --delivery-stream-type "DirectPut" \
  --iceberg-destination-configuration '{
    "RoleARN": "arn:aws:iam::123456789012:role/FirehoseRole",
    "CatalogConfiguration": {
      "CatalogARN": "arn:aws:glue:us-east-1:123456789012:catalog"
    },
    "DestinationTableConfigurationList": [
      {
        "DestinationDatabaseName": "analytics_db",
        "DestinationTableName": "events",
        "S3ErrorOutputPrefix": "errors/iceberg/"
      }
    ],
    "BufferingHints": {
      "SizeInMBs": 128,
      "IntervalInSeconds": 300
    },
    "S3Configuration": {
      "RoleARN": "arn:aws:iam::123456789012:role/FirehoseRole",
      "BucketARN": "arn:aws:s3:::my-data-lake"
    }
  }'
```

**Firehose Pricing:**

| Tier | Price/GB |
|------|---------|
| First 500 TB/month | $0.029 |
| Next 1.5 PB | $0.025 |
| Over 2 PB | $0.020 |
| Format conversion | +$0.018/GB |
| Dynamic partitioning | +$0.019/GB (JQ) |

### 1.2 Amazon MSK (Managed Streaming for Apache Kafka)

Fully managed Apache Kafka service — the most production-ready managed Kafka
offering on any cloud.

#### MSK Provisioned vs Serverless

| Feature | MSK Provisioned | MSK Serverless |
|---------|----------------|----------------|
| **Management** | You choose broker type/count | Fully managed |
| **Scaling** | Manual (add brokers) | Auto-scale |
| **Pricing** | Per broker-hr + storage | Per cluster-hr + partition-hr + data |
| **Kafka version** | 2.6-3.7+ | Latest |
| **Topics/partitions** | Up to 200K+ per cluster | Up to 120 partitions |
| **Retention** | Configurable (unlimited) | Configurable |
| **Multi-AZ** | 2-3 AZ | 3 AZ |
| **Tiered storage** | Yes (since 2024) | Yes |
| **Best for** | Large-scale, cost-sensitive | Small-medium, dev/test |

```bash
# Create MSK Provisioned cluster
aws kafka create-cluster-v2 \
  --cluster-name "analytics-kafka" \
  --provisioned '{
    "BrokerNodeGroupInfo": {
      "InstanceType": "kafka.m5.2xlarge",
      "ClientSubnets": ["subnet-aaa", "subnet-bbb", "subnet-ccc"],
      "StorageInfo": {
        "EbsStorageInfo": {
          "VolumeSize": 1000,
          "ProvisionedThroughput": {
            "Enabled": true,
            "VolumeThroughput": 250
          }
        }
      },
      "SecurityGroups": ["sg-abc123"]
    },
    "NumberOfBrokerNodes": 3,
    "KafkaVersion": "3.6.0",
    "ConfigurationInfo": {
      "Arn": "arn:aws:kafka:us-east-1:123456789012:configuration/my-config/xxx",
      "Revision": 1
    },
    "EncryptionInfo": {
      "EncryptionInTransit": {
        "ClientBroker": "TLS",
        "InCluster": true
      }
    },
    "EnhancedMonitoring": "PER_TOPIC_PER_PARTITION"
  }'
```

#### MSK Connect

Managed Kafka Connect for source/sink connectors:

```bash
# Create an S3 Sink connector
aws kafkaconnect create-connector \
  --connector-name "s3-sink" \
  --kafka-cluster '{
    "ApacheKafkaCluster": {
      "BootstrapServers": "b-1.cluster.xxx.kafka.us-east-1.amazonaws.com:9092",
      "Vpc": {
        "Subnets": ["subnet-aaa", "subnet-bbb"],
        "SecurityGroups": ["sg-abc123"]
      }
    }
  }' \
  --connector-configuration '{
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "tasks.max": "4",
    "topics": "events",
    "s3.region": "us-east-1",
    "s3.bucket.name": "my-data-lake",
    "flush.size": "100000",
    "storage.class": "io.confluent.connect.s3.storage.S3Storage",
    "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
    "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",
    "path.format": "year=YYYY/month=MM/day=dd/hour=HH",
    "partition.duration.ms": "3600000",
    "locale": "en-US",
    "timezone": "UTC"
  }' \
  --capacity '{
    "autoScaling": {
      "minWorkerCount": 1,
      "maxWorkerCount": 8,
      "scaleInPolicy": {"cpuUtilizationPercentage": 20},
      "scaleOutPolicy": {"cpuUtilizationPercentage": 80},
      "mcuCount": 2
    }
  }'
```

#### MSK Tiered Storage

Tiered storage (GA 2024) moves older log segments to S3 automatically:

- Enables near-infinite retention at S3 cost
- Only hot data stays on EBS (broker SSD)
- Transparent to consumers (no API changes)
- Reduces EBS storage costs by 50-80% for long retention

#### AWS Glue Schema Registry

```python
from aws_schema_registry import DataAndSchema, SchemaRegistryClient
from aws_schema_registry.avro import AvroSchema
import json

# Schema Registry for MSK/Kinesis
schema_registry = SchemaRegistryClient(
    endpoint='https://glue.us-east-1.amazonaws.com',
    region='us-east-1'
)

# Register an Avro schema
avro_schema = AvroSchema({
    "type": "record",
    "name": "UserEvent",
    "namespace": "com.example.events",
    "fields": [
        {"name": "event_id", "type": "string"},
        {"name": "user_id", "type": "long"},
        {"name": "event_type", "type": "string"},
        {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"},
        {"name": "payload", "type": ["null", "string"], "default": None}
    ]
})

schema_registry.register_schema(
    schema_name='UserEvent',
    schema_def=avro_schema,
    data_format='AVRO'
)
```

### 1.3 Amazon SQS / SNS

| Service | Type | Ordering | Throughput | Max Message | Pricing |
|---------|------|----------|-----------|-------------|---------|
| **SQS Standard** | Queue | Best-effort | Unlimited | 256 KB | ~$0.40/M requests |
| **SQS FIFO** | Queue | Strict FIFO | 3,000 msg/s (batch) | 256 KB | ~$0.50/M requests |
| **SNS Standard** | Pub/Sub | No | High | 256 KB | ~$0.50/M publishes |
| **SNS FIFO** | Pub/Sub | Strict FIFO | 300 msg/s | 256 KB | ~$0.50/M publishes |

**Fan-out pattern (SNS → SQS):**

```
                    ┌─────────┐
                    │  SNS    │
                    │  Topic  │
                    └────┬────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
    ┌──────▼──────┐ ┌───▼────┐ ┌─────▼──────┐
    │ SQS Queue   │ │ SQS    │ │ Lambda     │
    │ (analytics) │ │ (alert)│ │ (process)  │
    └─────────────┘ └────────┘ └────────────┘
```

### 1.4 Amazon EventBridge

Serverless event bus for application and AWS service events:

```python
import boto3
import json

events = boto3.client('events', region_name='us-east-1')

# Put custom event
events.put_events(
    Entries=[
        {
            'Source': 'data-platform.etl',
            'DetailType': 'ETL Job Completed',
            'Detail': json.dumps({
                'job_name': 'daily-aggregation',
                'status': 'SUCCESS',
                'records_processed': 1500000,
                'duration_seconds': 340
            }),
            'EventBusName': 'data-platform-bus'
        }
    ]
)

# Create an event rule (via CLI)
# aws events put-rule \
#   --name "etl-failure-alert" \
#   --event-bus-name "data-platform-bus" \
#   --event-pattern '{
#     "source": ["data-platform.etl"],
#     "detail-type": ["ETL Job Completed"],
#     "detail": {
#       "status": ["FAILED"]
#     }
#   }'
```

**EventBridge Scheduler** (cron/rate-based):

```bash
# Create a schedule for daily ETL trigger
aws scheduler create-schedule \
  --name "daily-etl-trigger" \
  --schedule-expression "cron(0 1 * * ? *)" \
  --schedule-expression-timezone "Asia/Bangkok" \
  --flexible-time-window '{"Mode": "OFF"}' \
  --target '{
    "Arn": "arn:aws:states:us-east-1:123456789012:stateMachine:daily-etl",
    "RoleArn": "arn:aws:iam::123456789012:role/SchedulerRole",
    "Input": "{\"date\": \"<aws.scheduler.execution-id>\"}"
  }'
```

### 1.5 Streaming Comparison

| Feature | Kinesis Data Streams | MSK (Kafka) | SQS | EventBridge |
|---------|---------------------|-------------|-----|-------------|
| **Type** | Data streaming | Event streaming | Message queue | Event bus |
| **Latency** | ~200ms | ~10ms | ~10ms | ~500ms |
| **Ordering** | Per shard | Per partition | FIFO only | No |
| **Replay** | Duration-based | Offset-based | No | Archive replay |
| **Throughput** | High | Very High | Moderate | High |
| **Multi-consumer** | Yes (enhanced fan-out) | Yes (consumer groups) | No | Yes (rules) |
| **Schema** | Optional | Glue Schema Registry | N/A | Schema discovery |
| **Multi-cloud** | No | MSK: No, Confluent: Yes | No | No |
| **Pricing** | Shard-hr + PUT | Broker-hr + storage | Per request | Per event |
| **Best for** | AWS-native streaming | Complex event architecture | Task queuing | Event routing |

**Decision flowchart:**

```text
Need data streaming?
├── Yes → Need Kafka compatibility?
│         ├── Yes → MSK
│         └── No → Need < 100ms latency?
│                   ├── Yes → MSK
│                   └── No → Kinesis Data Streams
└── No → Need message queuing?
          ├── Yes → Need FIFO?
          │         ├── Yes → SQS FIFO
          │         └── No → SQS Standard
          └── No → Event routing → EventBridge
```

---

## 2. Orchestration

### 2.1 Amazon MWAA (Managed Workflows for Apache Airflow)

Fully managed Apache Airflow for workflow orchestration.

#### Architecture

```
┌───────────────────────────────────────────────────────────┐
│                        MWAA                                │
│                                                            │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐ │
│  │ Web Server   │  │ Scheduler   │  │ Workers          │ │
│  │ (Airflow UI) │  │ (DAG parse  │  │ (Celery/K8s)     │ │
│  │              │  │  + schedule) │  │ Auto-scaling     │ │
│  └──────────────┘  └─────────────┘  │ 1-25 (per env)   │ │
│                                      └──────────────────┘ │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  S3 Bucket (DAGs, plugins, requirements.txt)         │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Aurora PostgreSQL (Metadb — managed, included)      │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

#### Environment Classes and Pricing

| Class | Scheduler | Workers | Metadb | Price/hr |
|-------|-----------|---------|--------|---------|
| **mw1.small** | 1 vCPU, 2 GB | 1 vCPU, 2 GB | Included | ~$0.49 |
| **mw1.medium** | 2 vCPU, 4 GB | 2 vCPU, 4 GB | Included | ~$0.95 |
| **mw1.large** | 4 vCPU, 8 GB | 4 vCPU, 8 GB | Included | ~$1.89 |
| **mw1.xlarge** | 8 vCPU, 16 GB | 8 vCPU, 16 GB | Included | ~$3.58 |
| **mw1.2xlarge** | 16 vCPU, 32 GB | 16 vCPU, 32 GB | Included | ~$7.16 |

Worker pricing: additional ~$0.055-0.22/worker-hr depending on class.

**Estimated monthly cost:** ~$360/mo (small) to ~$5,200/mo (2xlarge with max workers).

#### DAG Example

```python
# s3://my-mwaa-bucket/dags/daily_etl.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.operators.athena import AthenaOperator
from airflow.providers.amazon.aws.operators.redshift_sql import RedshiftSQLOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

default_args = {
    'owner': 'data-platform',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['data-team@example.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='daily_etl_pipeline',
    default_args=default_args,
    description='Daily ETL: S3 → Glue → Iceberg → Redshift',
    schedule_interval='0 1 * * *',  # 1 AM UTC daily
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['etl', 'daily', 'production'],
) as dag:

    # Wait for source data
    wait_for_data = S3KeySensor(
        task_id='wait_for_source_data',
        bucket_name='source-data-bucket',
        bucket_key='events/{{ ds }}/data.parquet',
        aws_conn_id='aws_default',
        timeout=3600,
        poke_interval=60,
    )

    # Run Glue ETL job
    glue_etl = GlueJobOperator(
        task_id='run_glue_etl',
        job_name='events-bronze-to-silver',
        region_name='us-east-1',
        script_args={
            '--JOB_NAME': 'events-bronze-to-silver',
            '--process_date': '{{ ds }}',
            '--source_path': 's3://source-data-bucket/events/{{ ds }}/',
            '--target_database': 'analytics_db',
            '--target_table': 'events_silver',
        },
        num_of_dpus=10,
        aws_conn_id='aws_default',
    )

    # Run Athena OPTIMIZE on Iceberg table
    optimize_iceberg = AthenaOperator(
        task_id='optimize_iceberg_table',
        query="OPTIMIZE analytics_db.events_silver REWRITE DATA USING BIN_PACK WHERE event_date = DATE '{{ ds }}'",
        database='analytics_db',
        output_location='s3://athena-results/optimize/',
        aws_conn_id='aws_default',
    )

    # Load to Redshift
    load_redshift = RedshiftSQLOperator(
        task_id='refresh_redshift_mv',
        redshift_conn_id='redshift_default',
        sql="REFRESH MATERIALIZED VIEW mv_daily_events;",
    )

    wait_for_data >> glue_etl >> optimize_iceberg >> load_redshift
```

#### Custom Plugins and Requirements

```text
# s3://my-mwaa-bucket/requirements/requirements.txt
apache-airflow-providers-amazon==9.0.0
apache-airflow-providers-slack==8.0.0
boto3>=1.34.0
pyarrow>=15.0.0
```

```python
# s3://my-mwaa-bucket/plugins/custom_operators/data_quality_operator.py
from airflow.models import BaseOperator
from airflow.providers.amazon.aws.hooks.athena import AthenaHook


class DataQualityCheckOperator(BaseOperator):
    """Run data quality checks using Athena queries."""

    def __init__(self, query: str, expected_result: int, database: str, **kwargs):
        super().__init__(**kwargs)
        self.query = query
        self.expected_result = expected_result
        self.database = database

    def execute(self, context):
        hook = AthenaHook(aws_conn_id='aws_default')
        query_execution_id = hook.run_query(
            query=self.query,
            query_context={'Database': self.database},
            result_configuration={'OutputLocation': 's3://athena-results/dq/'}
        )
        result = hook.get_query_results(query_execution_id)
        actual = int(result['ResultSet']['Rows'][1]['Data'][0]['VarCharValue'])

        if actual != self.expected_result:
            raise ValueError(f"Data quality check failed: expected {self.expected_result}, got {actual}")
        self.log.info(f"Data quality check passed: {actual} == {self.expected_result}")
```

### 2.2 AWS Step Functions

Serverless workflow orchestration using state machine definitions.

#### Standard vs Express

| Feature | Standard | Express |
|---------|----------|---------|
| **Max duration** | 1 year | 5 minutes |
| **Pricing** | $0.025/1,000 transitions | $0.00001667/GB-second |
| **Execution history** | Full (up to 25K events) | CloudWatch Logs only |
| **Exactly-once** | Yes | At-least-once |
| **Max start rate** | 2,000/sec | 100,000/sec |
| **Best for** | Long-running ETL, approvals | High-volume, short processing |

#### State Machine Example (Data Pipeline)

```json
{
  "Comment": "Data pipeline: S3 → Glue → Quality Check → Redshift",
  "StartAt": "RunGlueJob",
  "States": {
    "RunGlueJob": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "events-etl",
        "Arguments": {
          "--process_date.$": "$.process_date",
          "--JOB_NAME": "events-etl"
        }
      },
      "ResultPath": "$.glue_result",
      "Next": "DataQualityCheck",
      "Retry": [
        {
          "ErrorEquals": ["Glue.AWSGlueException"],
          "IntervalSeconds": 60,
          "MaxAttempts": 3,
          "BackoffRate": 2.0
        }
      ],
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "NotifyFailure",
          "ResultPath": "$.error"
        }
      ]
    },
    "DataQualityCheck": {
      "Type": "Task",
      "Resource": "arn:aws:states:::athena:startQueryExecution.sync",
      "Parameters": {
        "QueryString": "SELECT COUNT(*) FROM analytics_db.events_silver WHERE event_date = DATE '${process_date}' AND event_id IS NULL",
        "QueryExecutionContext": {
          "Database": "analytics_db"
        },
        "ResultConfiguration": {
          "OutputLocation": "s3://athena-results/step-functions/"
        }
      },
      "ResultPath": "$.quality_result",
      "Next": "EvaluateQuality"
    },
    "EvaluateQuality": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.quality_result.QueryExecution.Status.State",
          "StringEquals": "SUCCEEDED",
          "Next": "RefreshRedshift"
        }
      ],
      "Default": "NotifyFailure"
    },
    "RefreshRedshift": {
      "Type": "Task",
      "Resource": "arn:aws:states:::redshift-data:executeStatement.sync",
      "Parameters": {
        "ClusterIdentifier": "analytics-cluster",
        "Database": "analytics",
        "Sql": "REFRESH MATERIALIZED VIEW mv_daily_events;",
        "DbUser": "etl_user"
      },
      "Next": "NotifySuccess"
    },
    "NotifySuccess": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:etl-notifications",
        "Message": "Daily ETL pipeline completed successfully."
      },
      "End": true
    },
    "NotifyFailure": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:etl-alerts",
        "Message.$": "States.Format('ETL pipeline failed: {}', $.error.Cause)"
      },
      "End": true
    }
  }
}
```

#### Parallel Processing with Map State

```json
{
  "ProcessPartitions": {
    "Type": "Map",
    "ItemsPath": "$.partitions",
    "MaxConcurrency": 10,
    "Iterator": {
      "StartAt": "ProcessPartition",
      "States": {
        "ProcessPartition": {
          "Type": "Task",
          "Resource": "arn:aws:states:::glue:startJobRun.sync",
          "Parameters": {
            "JobName": "partition-processor",
            "Arguments": {
              "--partition.$": "$.partition_key"
            }
          },
          "End": true
        }
      }
    },
    "Next": "MergeResults"
  }
}
```

### 2.3 MWAA vs Step Functions

| Feature | MWAA (Airflow) | Step Functions |
|---------|---------------|----------------|
| **Model** | DAGs (Python code) | State machines (JSON/YAML) |
| **Best for** | Complex data ETL pipelines | Microservice orchestration, short workflows |
| **Learning curve** | Higher (Airflow knowledge) | Lower (visual designer + SDK) |
| **Cost** | ~$360-5,200/mo (always-on) | Pay per transition/GB-second |
| **Scheduling** | Built-in (cron, sensors) | EventBridge Scheduler |
| **Ecosystem** | 1,000+ Airflow operators | AWS SDK integrations |
| **Retry/error** | Airflow retry, callbacks | Built-in error handling, retry |
| **Human approval** | Custom sensor/webhook | Activity tasks (built-in) |
| **Monitoring** | Airflow UI + CloudWatch | Console + CloudWatch + X-Ray |
| **Vendor lock-in** | Low (Airflow = open source) | High (AWS-specific) |

---

## 3. Data Governance

### 3.1 AWS Lake Formation

(See [AWS_DATA_PLATFORM.md Section 2.2](../DATA_PLATFORM/AWS_DATA_PLATFORM.md#22-aws-lake-formation) for detailed coverage.)

Key capabilities:
- Fine-grained access control (row, column, cell, tag-based)
- LF-Tags for attribute-based access control
- Cross-account data sharing
- Data filters with SQL predicates
- Integration with Glue, Athena, EMR, Redshift
- **Free** (pay only for underlying services)

### 3.2 Amazon DataZone

Business data catalog and governance for self-service data access.

```
┌──────────────────────────────────────────────────────────┐
│                    Amazon DataZone                        │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Domains                                          │   │
│  │  ┌────────────────┐  ┌────────────────────────┐  │   │
│  │  │ Sales Domain   │  │ Marketing Domain       │  │   │
│  │  │                │  │                        │  │   │
│  │  │ Projects:      │  │ Projects:              │  │   │
│  │  │ - Analytics    │  │ - Campaign Analytics   │  │   │
│  │  │ - Reporting    │  │ - Customer 360         │  │   │
│  │  │                │  │                        │  │   │
│  │  │ Assets:        │  │ Assets:                │  │   │
│  │  │ - order_facts  │  │ - campaign_metrics     │  │   │
│  │  │ - revenue_kpi  │  │ - customer_segments    │  │   │
│  │  └────────────────┘  └────────────────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  Features:                                               │
│  - Semantic search + AI-powered discovery                │
│  - Request/approve subscription workflow                 │
│  - Business glossary                                     │
│  - Data quality rules                                    │
│  - Auto-generated documentation                          │
└──────────────────────────────────────────────────────────┘
```

### 3.3 Glue Data Catalog

(See [AWS_DATA_PLATFORM.md Section 4.2](../DATA_PLATFORM/AWS_DATA_PLATFORM.md#42-glue-data-catalog) for detailed coverage.)

### 3.4 Governance Comparison

| Feature | Lake Formation | DataZone | Glue Catalog |
|---------|---------------|----------|--------------|
| **Focus** | Security/governance | Business discovery | Technical metadata |
| **Access control** | Row/column/cell/tag | Subscription-based | IAM-based |
| **Discovery** | Limited | Rich (AI search, glossary) | Basic |
| **Lineage** | No (DataZone needed) | Yes (basic) | No |
| **Data quality** | No | Yes (rules, profiling) | No |
| **Cost** | Free | Per domain | Free tier + per object |
| **Best for** | Platform admins | Business users | Data engineers |

---

## 4. Data Integration

### 4.1 AWS DMS (Database Migration Service)

Managed database migration and continuous replication (CDC).

#### Migration Modes

```
┌──────────────────────────────────────────────────────────┐
│                    AWS DMS                                │
│                                                          │
│  Full Load            Full Load + CDC         CDC Only   │
│  ┌──────────┐        ┌──────────────┐     ┌──────────┐  │
│  │ One-time  │        │ Initial load │     │ Changes  │  │
│  │ migration │        │ + ongoing    │     │ only     │  │
│  │           │        │ replication  │     │ (ongoing)│  │
│  └──────────┘        └──────────────┘     └──────────┘  │
│                                                          │
│  Sources: Oracle, SQL Server, PostgreSQL, MySQL,         │
│           MongoDB, SAP, S3, Aurora, DynamoDB             │
│                                                          │
│  Targets: S3, Redshift, RDS, Aurora, DynamoDB,          │
│           OpenSearch, Kinesis, Kafka, Neptune             │
└──────────────────────────────────────────────────────────┘
```

```bash
# Create a DMS replication instance (serverless)
aws dms create-replication-config \
  --replication-config-identifier "mysql-to-s3" \
  --source-endpoint-arn "arn:aws:dms:us-east-1:123456789012:endpoint:source-mysql" \
  --target-endpoint-arn "arn:aws:dms:us-east-1:123456789012:endpoint:target-s3" \
  --compute-config '{
    "MinCapacityUnits": 1,
    "MaxCapacityUnits": 16,
    "MultiAZ": false,
    "ReplicationSubnetGroupId": "default"
  }' \
  --replication-type "full-load-and-cdc" \
  --table-mappings '{
    "rules": [
      {
        "rule-type": "selection",
        "rule-id": "1",
        "rule-name": "select-all-tables",
        "object-locator": {
          "schema-name": "production",
          "table-name": "%"
        },
        "rule-action": "include"
      },
      {
        "rule-type": "transformation",
        "rule-id": "2",
        "rule-name": "add-partition-column",
        "rule-target": "column",
        "object-locator": {
          "schema-name": "production",
          "table-name": "%"
        },
        "rule-action": "add-column",
        "value": "ingestion_date",
        "expression": "$TIMESTAMP",
        "data-type": {
          "type": "string",
          "length": 10
        }
      }
    ]
  }'
```

**DMS Pricing:**
- Serverless: ~$0.013/DMS Capacity Unit-hr (billed per second)
- On-demand instances: from ~$0.018/hr (dms.t3.micro) to ~$3.654/hr (dms.r5.24xlarge)
- Storage: $0.115/GB-month

### 4.2 AWS AppFlow

SaaS integration service with 60+ connectors:

```bash
# Create a flow: Salesforce → S3 (Parquet)
aws appflow create-flow \
  --flow-name "salesforce-opportunities" \
  --source-flow-config '{
    "connectorType": "Salesforce",
    "connectorProfileName": "my-sf-connection",
    "sourceConnectorProperties": {
      "Salesforce": {
        "object": "Opportunity",
        "enableDynamicFieldUpdate": true,
        "includeDeletedRecords": false
      }
    },
    "incrementalPullConfig": {
      "datetimeTypeFieldName": "LastModifiedDate"
    }
  }' \
  --destination-flow-config-list '[{
    "connectorType": "S3",
    "destinationConnectorProperties": {
      "S3": {
        "bucketName": "my-data-lake",
        "bucketPrefix": "salesforce/opportunities/",
        "s3OutputFormatConfig": {
          "fileType": "PARQUET",
          "aggregationConfig": {
            "aggregationType": "SingleFile"
          },
          "prefixConfig": {
            "prefixType": "PATH_AND_FILENAME",
            "prefixFormat": "DAY"
          }
        }
      }
    }
  }]' \
  --trigger-config '{
    "triggerType": "Scheduled",
    "triggerProperties": {
      "Scheduled": {
        "scheduleExpression": "rate(1hour)",
        "dataPullMode": "Incremental"
      }
    }
  }' \
  --tasks '[
    {
      "taskType": "Filter",
      "sourceFields": ["StageName"],
      "connectorOperator": {"Salesforce": "EQUAL_TO"},
      "taskProperties": {"VALUE": "Closed Won"}
    },
    {
      "taskType": "Map",
      "sourceFields": ["Id", "Name", "Amount", "CloseDate", "StageName"],
      "taskProperties": {"DESTINATION_DATA_TYPE": "string"}
    }
  ]'
```

**AppFlow Pricing:**
- $0.001 per flow run
- $0.02 per GB of data processed

### 4.3 AWS Data Exchange

- Find, subscribe, and use third-party data
- 3,500+ data products from 300+ providers
- Direct delivery to S3, Redshift, or Lake Formation
- Automatic revision notifications

### 4.4 AWS Transfer Family

Managed SFTP/FTPS/FTP/AS2 for file transfers to S3/EFS:

```bash
# Create an SFTP server
aws transfer create-server \
  --protocols "SFTP" \
  --identity-provider-type "SERVICE_MANAGED" \
  --endpoint-type "PUBLIC" \
  --tags '[{"Key": "project", "Value": "data-lake"}]'

# Create user with S3 home directory
aws transfer create-user \
  --server-id "s-abc123" \
  --user-name "data-partner" \
  --role "arn:aws:iam::123456789012:role/TransferRole" \
  --home-directory "/my-data-lake/incoming/partner-a" \
  --home-directory-type "LOGICAL" \
  --home-directory-mappings '[{"Entry": "/", "Target": "/my-data-lake/incoming/partner-a"}]'
```

---

## 5. Security

### 5.1 AWS Secrets Manager

```python
import boto3
import json

secrets_manager = boto3.client('secretsmanager', region_name='us-east-1')

# Create a secret
secrets_manager.create_secret(
    Name='data-platform/redshift/admin',
    Description='Redshift admin credentials',
    SecretString=json.dumps({
        'username': 'admin',
        'password': 'secure-password-here',
        'host': 'analytics-cluster.xxx.us-east-1.redshift.amazonaws.com',
        'port': 5439,
        'dbname': 'analytics'
    }),
    Tags=[
        {'Key': 'project', 'Value': 'data-platform'},
        {'Key': 'environment', 'Value': 'production'}
    ]
)

# Retrieve a secret
def get_secret(secret_name: str) -> dict:
    response = secrets_manager.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Enable automatic rotation (Lambda-based)
secrets_manager.rotate_secret(
    SecretId='data-platform/redshift/admin',
    RotationLambdaARN='arn:aws:lambda:us-east-1:123456789012:function:RotateRedshiftSecret',
    RotationRules={
        'AutomaticallyAfterDays': 30
    }
)
```

**Pricing:** $0.40/secret/month + $0.05/10,000 API calls

#### Rotation Lambda Example

```python
# Lambda function for automatic secret rotation
import boto3
import json
import string
import secrets as py_secrets


def lambda_handler(event, context):
    step = event['Step']
    secret_id = event['SecretId']
    token = event['ClientRequestToken']

    sm = boto3.client('secretsmanager')

    if step == 'createSecret':
        current = json.loads(sm.get_secret_value(SecretId=secret_id)['SecretString'])
        # Generate new password
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
        new_password = ''.join(py_secrets.choice(alphabet) for _ in range(32))
        current['password'] = new_password
        sm.put_secret_value(
            SecretId=secret_id,
            ClientRequestToken=token,
            SecretString=json.dumps(current),
            VersionStages=['AWSPENDING']
        )
    elif step == 'setSecret':
        pending = json.loads(
            sm.get_secret_value(SecretId=secret_id, VersionStage='AWSPENDING')['SecretString']
        )
        # Update password in the database
        update_database_password(pending)
    elif step == 'testSecret':
        pending = json.loads(
            sm.get_secret_value(SecretId=secret_id, VersionStage='AWSPENDING')['SecretString']
        )
        test_database_connection(pending)
    elif step == 'finishSecret':
        sm.update_secret_version_stage(
            SecretId=secret_id,
            VersionStage='AWSCURRENT',
            MoveToVersionId=token,
            RemoveFromVersionId=get_current_version(sm, secret_id)
        )
```

### 5.2 IAM Roles for Data Services

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "GlueETLPermissions",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-data-lake",
        "arn:aws:s3:::my-data-lake/*"
      ]
    },
    {
      "Sid": "GlueCatalogPermissions",
      "Effect": "Allow",
      "Action": [
        "glue:GetDatabase",
        "glue:GetTable",
        "glue:GetTableVersions",
        "glue:CreateTable",
        "glue:UpdateTable",
        "glue:BatchCreatePartition"
      ],
      "Resource": [
        "arn:aws:glue:us-east-1:123456789012:catalog",
        "arn:aws:glue:us-east-1:123456789012:database/*",
        "arn:aws:glue:us-east-1:123456789012:table/*"
      ]
    },
    {
      "Sid": "LakeFormationPermissions",
      "Effect": "Allow",
      "Action": [
        "lakeformation:GetDataAccess"
      ],
      "Resource": "*"
    }
  ]
}
```

#### Cross-Service Trust Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "glue.amazonaws.com",
          "lakeformation.amazonaws.com"
        ]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### 5.3 VPC Endpoints

| Type | Services | Cost | Data Path |
|------|----------|------|-----------|
| **Gateway** | S3, DynamoDB | **Free** | Route table entry |
| **Interface** | Glue, Kinesis, Secrets Manager, Redshift, etc. | ~$0.01/hr/AZ + $0.01/GB | PrivateLink (ENI) |

```bash
# Create S3 gateway endpoint (free)
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-abc123 \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-abc123

# Create Glue interface endpoint
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-abc123 \
  --vpc-endpoint-type Interface \
  --service-name com.amazonaws.us-east-1.glue \
  --subnet-ids subnet-aaa subnet-bbb \
  --security-group-ids sg-abc123 \
  --private-dns-enabled
```

### 5.4 KMS Encryption

```bash
# Create a CMK for data lake encryption
aws kms create-key \
  --description "Data lake encryption key" \
  --key-usage ENCRYPT_DECRYPT \
  --key-spec SYMMETRIC_DEFAULT \
  --tags '[{"TagKey": "project", "TagValue": "data-platform"}]'

# Enable automatic key rotation
aws kms enable-key-rotation \
  --key-id "arn:aws:kms:us-east-1:123456789012:key/my-key-id"

# Create alias
aws kms create-alias \
  --alias-name "alias/data-lake-key" \
  --target-key-id "arn:aws:kms:us-east-1:123456789012:key/my-key-id"
```

**KMS Pricing:**
- $1.00/key/month (CMK)
- $0.03/10,000 API calls
- AWS-managed keys: free for S3 SSE-S3

### 5.5 S3 Encryption Options

| Method | Key Management | Cost | Best For |
|--------|---------------|------|----------|
| SSE-S3 | AWS managed | Free | Default for all buckets |
| SSE-KMS | AWS KMS (CMK or AWS-managed) | $1/key + API calls | Audit trails, key rotation control |
| SSE-C | Customer provided | Free (you manage keys) | Full key control |
| CSE | Client-side encryption | Varies | End-to-end encryption |

---

## 6. CI/CD

### 6.1 AWS CodePipeline / CodeBuild

```yaml
# buildspec.yml for CodeBuild (data platform project)
version: 0.2

env:
  variables:
    PYTHON_VERSION: "3.12"
    AWS_REGION: "us-east-1"
  secrets-manager:
    REDSHIFT_PASSWORD: "data-platform/redshift/admin:password"

phases:
  install:
    runtime-versions:
      python: 3.12
    commands:
      - pip install -r requirements.txt
      - pip install pytest mypy ruff

  pre_build:
    commands:
      - echo "Running linting and type checking"
      - ruff check src/
      - mypy src/ --ignore-missing-imports

  build:
    commands:
      - echo "Running tests"
      - pytest tests/ -v --junitxml=reports/junit.xml
      - echo "Building deployment package"
      - python setup.py sdist

  post_build:
    commands:
      - echo "Uploading artifacts to S3"
      - aws s3 cp dist/*.tar.gz s3://deployment-artifacts/glue-jobs/

reports:
  test-reports:
    files:
      - reports/junit.xml
    file-format: JUNITXML

artifacts:
  files:
    - dist/*.tar.gz
    - deploy/*.yaml
  discard-paths: no
```

### 6.2 Amazon ECR

```bash
# Create repository
aws ecr create-repository \
  --repository-name "data-platform/etl-runner" \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=KMS

# Login, build, and push
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

docker build -t data-platform/etl-runner:latest .
docker tag data-platform/etl-runner:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/data-platform/etl-runner:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/data-platform/etl-runner:latest

# Lifecycle policy to keep only last 10 images
aws ecr put-lifecycle-policy \
  --repository-name "data-platform/etl-runner" \
  --lifecycle-policy-text '{
    "rules": [
      {
        "rulePriority": 1,
        "description": "Keep only last 10 images",
        "selection": {
          "tagStatus": "any",
          "countType": "imageCountMoreThan",
          "countNumber": 10
        },
        "action": {
          "type": "expire"
        }
      }
    ]
  }'
```

**ECR Pricing:**
- Private: $0.10/GB-month storage
- Public: 50 GB free, then $0.10/GB
- Data transfer: free to same-region services

### 6.3 AWS CDK (Infrastructure as Code)

```python
# cdk_stack.py — Data Lake infrastructure
from aws_cdk import (
    Stack, Duration, RemovalPolicy,
    aws_s3 as s3,
    aws_glue as glue,
    aws_iam as iam,
    aws_kms as kms,
    aws_lakeformation as lf,
    aws_redshiftserverless as redshift,
)
from constructs import Construct


class DataLakeStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Encryption key
        data_lake_key = kms.Key(self, "DataLakeKey",
            description="Encryption key for data lake",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Data lake bucket
        lake_bucket = s3.Bucket(self, "DataLakeBucket",
            bucket_name=f"data-lake-{self.account}-{self.region}",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=data_lake_key,
            versioned=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="ArchiveOldData",
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(90),
                        ),
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(365),
                        ),
                    ],
                )
            ],
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Glue database
        analytics_db = glue.CfnDatabase(self, "AnalyticsDB",
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name="analytics_db",
                description="Analytics database for data lake",
            ),
        )

        # Glue ETL role
        glue_role = iam.Role(self, "GlueETLRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSGlueServiceRole"
                )
            ],
        )
        lake_bucket.grant_read_write(glue_role)

        # Redshift Serverless
        rs_namespace = redshift.CfnNamespace(self, "RedshiftNamespace",
            namespace_name="analytics",
            admin_username="admin",
            admin_user_password="CHANGE-ME-USE-SECRETS",
            db_name="analytics",
            iam_roles=[glue_role.role_arn],
        )

        rs_workgroup = redshift.CfnWorkgroup(self, "RedshiftWorkgroup",
            workgroup_name="analytics-wg",
            namespace_name="analytics",
            base_capacity=32,
            max_capacity=128,
        )
        rs_workgroup.add_dependency(rs_namespace)
```

### 6.4 Terraform for AWS Data Services

```hcl
# main.tf — Data lake infrastructure with Terraform
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# S3 Data Lake Bucket
resource "aws_s3_bucket" "data_lake" {
  bucket = "data-lake-${data.aws_caller_identity.current.account_id}"
  tags = {
    Project     = "data-platform"
    Environment = "production"
  }
}

resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.data_lake.arn
    }
  }
}

# Glue Catalog Database
resource "aws_glue_catalog_database" "analytics" {
  name        = "analytics_db"
  description = "Analytics database"
}

# Glue ETL Job
resource "aws_glue_job" "events_etl" {
  name         = "events-bronze-to-silver"
  role_arn     = aws_iam_role.glue_etl.arn
  glue_version = "5.0"
  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.scripts.id}/glue/events_etl.py"
    python_version  = "3"
  }
  default_arguments = {
    "--job-bookmark-option"       = "job-bookmark-enable"
    "--TempDir"                   = "s3://${aws_s3_bucket.temp.id}/glue/"
    "--enable-metrics"            = "true"
    "--enable-continuous-cloudwatch-log" = "true"
  }
  max_retries       = 1
  timeout           = 60
  worker_type       = "G.1X"
  number_of_workers = 10
}

# Redshift Serverless
resource "aws_redshiftserverless_namespace" "analytics" {
  namespace_name = "analytics"
  db_name        = "analytics"
  admin_username = "admin"
  admin_user_password = var.redshift_admin_password
  iam_roles      = [aws_iam_role.redshift.arn]
}

resource "aws_redshiftserverless_workgroup" "analytics" {
  namespace_name = aws_redshiftserverless_namespace.analytics.namespace_name
  workgroup_name = "analytics-wg"
  base_capacity  = 32
  max_capacity   = 128
}

data "aws_caller_identity" "current" {}
```

### 6.5 GitLab CI Integration with OIDC

```yaml
# .gitlab-ci.yml — GitLab CI with AWS OIDC (no long-lived keys)
stages:
  - test
  - build
  - deploy-stg
  - deploy-prod

variables:
  AWS_DEFAULT_REGION: us-east-1
  ROLE_ARN_STG: arn:aws:iam::111111111111:role/GitLabCI-STG
  ROLE_ARN_PROD: arn:aws:iam::222222222222:role/GitLabCI-PROD

.aws-auth-stg:
  id_tokens:
    GITLAB_OIDC_TOKEN:
      aud: https://gitlab.example.com
  before_script:
    - >
      export $(printf "AWS_ACCESS_KEY_ID=%s AWS_SECRET_ACCESS_KEY=%s AWS_SESSION_TOKEN=%s"
      $(aws sts assume-role-with-web-identity
      --role-arn $ROLE_ARN_STG
      --role-session-name "gitlab-ci-${CI_PIPELINE_ID}"
      --web-identity-token $GITLAB_OIDC_TOKEN
      --query "Credentials.[AccessKeyId,SecretAccessKey,SessionToken]"
      --output text))

.aws-auth-prod:
  id_tokens:
    GITLAB_OIDC_TOKEN:
      aud: https://gitlab.example.com
  before_script:
    - >
      export $(printf "AWS_ACCESS_KEY_ID=%s AWS_SECRET_ACCESS_KEY=%s AWS_SESSION_TOKEN=%s"
      $(aws sts assume-role-with-web-identity
      --role-arn $ROLE_ARN_PROD
      --role-session-name "gitlab-ci-${CI_PIPELINE_ID}"
      --web-identity-token $GITLAB_OIDC_TOKEN
      --query "Credentials.[AccessKeyId,SecretAccessKey,SessionToken]"
      --output text))

test:
  stage: test
  image: python:3.12
  script:
    - pip install -r requirements.txt
    - ruff check src/
    - mypy src/
    - pytest tests/ -v

build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  extends: .aws-auth-stg
  script:
    - aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
    - docker build -t $ECR_REGISTRY/etl-runner:$CI_COMMIT_SHORT_SHA .
    - docker push $ECR_REGISTRY/etl-runner:$CI_COMMIT_SHORT_SHA

deploy-stg:
  stage: deploy-stg
  extends: .aws-auth-stg
  script:
    - cd infrastructure
    - terraform init
    - terraform plan -var-file=stg.tfvars -out=plan.out
    - terraform apply plan.out
  environment:
    name: staging

deploy-prod:
  stage: deploy-prod
  extends: .aws-auth-prod
  script:
    - cd infrastructure
    - terraform init
    - terraform plan -var-file=prod.tfvars -out=plan.out
    - terraform apply plan.out
  environment:
    name: production
  when: manual
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

---

## 7. References

### Official AWS Documentation

- [Kinesis Data Streams](https://docs.aws.amazon.com/streams/latest/dev/introduction.html)
- [Kinesis Data Streams Pricing](https://aws.amazon.com/kinesis/data-streams/pricing/)
- [Kinesis Enhanced Fan-Out](https://docs.aws.amazon.com/streams/latest/dev/enhanced-consumers.html)
- [Kinesis Data Firehose](https://docs.aws.amazon.com/firehose/latest/dev/what-is-this-service.html)
- [Firehose Pricing](https://aws.amazon.com/firehose/pricing/)
- [Firehose to Iceberg](https://docs.aws.amazon.com/firehose/latest/dev/apache-iceberg-destination.html)
- [Amazon MSK](https://docs.aws.amazon.com/msk/latest/developerguide/what-is-msk.html)
- [MSK Serverless](https://docs.aws.amazon.com/msk/latest/developerguide/serverless.html)
- [MSK Connect](https://docs.aws.amazon.com/msk/latest/developerguide/msk-connect.html)
- [MSK Tiered Storage](https://docs.aws.amazon.com/msk/latest/developerguide/msk-tiered-storage.html)
- [Glue Schema Registry](https://docs.aws.amazon.com/glue/latest/dg/schema-registry.html)
- [SQS Developer Guide](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
- [SNS Developer Guide](https://docs.aws.amazon.com/sns/latest/dg/welcome.html)
- [Amazon EventBridge](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html)
- [EventBridge Scheduler](https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html)
- [Amazon MWAA](https://docs.aws.amazon.com/mwaa/latest/userguide/what-is-mwaa.html)
- [MWAA Pricing](https://aws.amazon.com/managed-workflows-for-apache-airflow/pricing/)
- [AWS Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html)
- [Step Functions Pricing](https://aws.amazon.com/step-functions/pricing/)
- [AWS Lake Formation](https://docs.aws.amazon.com/lake-formation/latest/dg/what-is-lake-formation.html)
- [Amazon DataZone](https://docs.aws.amazon.com/datazone/latest/userguide/what-is-datazone.html)
- [AWS DMS](https://docs.aws.amazon.com/dms/latest/userguide/Welcome.html)
- [DMS Serverless](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Serverless.html)
- [AWS AppFlow](https://docs.aws.amazon.com/appflow/latest/userguide/what-is-appflow.html)
- [AWS Transfer Family](https://docs.aws.amazon.com/transfer/latest/userguide/what-is-aws-transfer-family.html)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
- [Secrets Manager Rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)
- [VPC Endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints.html)
- [AWS KMS](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html)
- [Amazon ECR](https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html)
- [AWS CodeBuild](https://docs.aws.amazon.com/codebuild/latest/userguide/welcome.html)
- [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/home.html)

### Third-Party Analysis

- [MSK vs Kinesis — Confluent](https://www.confluent.io/blog/kinesis-vs-kafka/)
- [MWAA vs Step Functions — AWS Blog](https://aws.amazon.com/blogs/architecture/orchestration-on-aws-choosing-between-aws-step-functions-and-amazon-mwaa/)
- [AWS Data Services Comparison — DEV Community](https://dev.to/alexmercedcoder/the-2025-2026-ultimate-guide-to-the-data-lakehouse-and-the-data-lakehouse-ecosystem-dig)

---

> **Document Version**: 2.0 | **Last Updated**: 2026-03-05
