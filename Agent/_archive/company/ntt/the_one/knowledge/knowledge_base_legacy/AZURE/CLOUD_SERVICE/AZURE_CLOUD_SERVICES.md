# Azure Cloud Services for Data Engineering

> **Version**: 2.0 | **Created**: 2026-03-05 | **Maintainer**: Data Platform Team

## Table of Contents

1. [Data Processing & ETL](#1-data-processing--etl)
2. [Streaming & Messaging](#2-streaming--messaging)
3. [Data Governance](#3-data-governance)
4. [Power BI Integration](#4-power-bi-integration)
5. [Security](#5-security)
6. [Infrastructure as Code](#6-infrastructure-as-code)
7. [CI/CD](#7-cicd)
8. [References](#8-references)

---

## 1. Data Processing & ETL

### 1.1 Azure Data Factory (ADF)

Cloud-scale ETL and orchestration service with 150+ built-in connectors:

```
┌──────────────────────────────────────────────────────────────┐
│                   Azure Data Factory                          │
│                                                               │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Pipelines      │  │ Data Flows   │  │ Integration      │ │
│  │                │  │              │  │ Runtime          │ │
│  │ • Activities   │  │ • Mapping    │  │                  │ │
│  │ • Control flow │  │   (visual    │  │ • Azure IR       │ │
│  │ • Parameters   │  │    Spark)    │  │   (cloud)        │ │
│  │ • Variables    │  │ • Wrangling  │  │ • Self-hosted IR │ │
│  │ • Triggers     │  │   (Power     │  │   (on-prem)      │ │
│  │                │  │    Query)    │  │ • SSIS IR         │ │
│  └────────┬───────┘  └──────┬───────┘  └──────────────────┘ │
│           │                 │                                 │
│  ┌────────▼─────────────────▼──────────────────────────────┐ │
│  │                     Activities                           │ │
│  │                                                          │ │
│  │  Copy  │ Data Flow │ Notebook │ Stored Proc │ Web       │ │
│  │  HDInsight │ Databricks │ SQL │ Custom │ Lookup         │ │
│  │  Until │ ForEach │ If │ Switch │ Wait │ Execute Pipeline│ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

#### Pipeline Example (ARM JSON)

```json
{
  "name": "IngestMembersToLake",
  "properties": {
    "activities": [
      {
        "name": "CopyFromSQL",
        "type": "Copy",
        "inputs": [{ "referenceName": "SqlSource", "type": "DatasetReference" }],
        "outputs": [{ "referenceName": "AdlsSink", "type": "DatasetReference" }],
        "typeProperties": {
          "source": {
            "type": "AzureSqlSource",
            "sqlReaderQuery": "SELECT * FROM members WHERE modified_date > @{pipeline().parameters.watermark}"
          },
          "sink": {
            "type": "ParquetSink",
            "storeSettings": {
              "type": "AzureBlobFSWriteSettings"
            },
            "formatSettings": {
              "type": "ParquetWriteSettings",
              "maxRowsPerFile": 1000000
            }
          },
          "enableStaging": false
        }
      },
      {
        "name": "RunDatabricksNotebook",
        "type": "DatabricksNotebook",
        "dependsOn": [
          { "activity": "CopyFromSQL", "dependencyConditions": ["Succeeded"] }
        ],
        "typeProperties": {
          "notebookPath": "/ETL/transform_members",
          "baseParameters": {
            "source_path": "abfss://bronze@storage.dfs.core.windows.net/members/",
            "target_path": "abfss://silver@storage.dfs.core.windows.net/members/"
          }
        }
      }
    ],
    "parameters": {
      "watermark": { "type": "string", "defaultValue": "1900-01-01" }
    }
  }
}
```

#### Pricing

| Component | Price | Notes |
|-----------|-------|-------|
| **Pipeline activities** | $1.00/1,000 runs (Cloud IR) | $0.50/1,000 (Self-hosted IR) |
| **Data movement** | $0.25/DIU-hr | DIU = Data Integration Unit |
| **Mapping Data Flow** | ~$0.268/vCore-hr (General Purpose) | ~$0.354/vCore-hr (Memory Optimized) |
| **SSIS IR** | ~$0.84/node-hr (Standard) | Enterprise: ~$2.37/node-hr |
| **Pipeline orchestration** | $1.00/1,000 activity runs | Control activities half price |

#### ADF vs Fabric Data Factory

| Feature | ADF (Standalone) | Fabric Data Factory |
|---------|-----------------|---------------------|
| **Pipelines** | Full featured | Full featured (same engine) |
| **Mapping Data Flows** | Yes | No (use Dataflow Gen2) |
| **SSIS IR** | Yes | No |
| **Connectors** | 150+ | ~100+ (growing) |
| **Pricing** | Per activity/DIU | Included in Fabric CU |
| **Self-hosted IR** | Yes | Yes |
| **Git integration** | Azure DevOps, GitHub | Fabric Git (limited) |
| **Monitoring** | ADF Monitor + Azure Monitor | Fabric Monitoring Hub |

### 1.2 Azure Stream Analytics

Real-time SQL queries on streaming data:

```sql
-- Tumbling window: Count events per 5-minute window
SELECT
    memberCode,
    COUNT(*) AS eventCount,
    System.Timestamp() AS windowEnd
INTO [output-eventhub]
FROM [input-eventhub]
GROUP BY
    memberCode,
    TumblingWindow(minute, 5)

-- Hopping window: Running average over 10 min, output every 5 min
SELECT
    tierCode,
    AVG(pointBalance) AS avgPoints,
    COUNT(*) AS memberCount,
    System.Timestamp() AS windowEnd
INTO [output-sql]
FROM [input-eventhub]
GROUP BY
    tierCode,
    HoppingWindow(minute, 10, 5)

-- Session window: Group events within 10 min of inactivity
SELECT
    sessionId,
    COUNT(*) AS clickCount,
    MIN(EventEnqueuedUtcTime) AS sessionStart,
    MAX(EventEnqueuedUtcTime) AS sessionEnd,
    DATEDIFF(second, MIN(EventEnqueuedUtcTime), MAX(EventEnqueuedUtcTime)) AS durationSec
INTO [output-blob]
FROM [input-eventhub]
GROUP BY
    sessionId,
    SessionWindow(minute, 10)

-- Reference data join (static lookup)
SELECT
    e.memberCode,
    e.eventType,
    r.memberName,
    r.tierCode
INTO [output-powerbi]
FROM [input-eventhub] e
JOIN [ref-members] r ON e.memberCode = r.memberCode
```

**Pricing:** ~$0.11/Streaming Unit (SU)/hour. Minimum 1 SU, auto-scale up to 192 SU.

```bash
# Create Stream Analytics job
az stream-analytics job create \
  --name loyaltyStreamJob \
  --resource-group myRG \
  --location southeastasia \
  --sku Standard \
  --transformation-streaming-units 6

# Start job
az stream-analytics job start \
  --name loyaltyStreamJob \
  --resource-group myRG \
  --output-start-mode JobStartTime
```

### 1.3 Azure HDInsight

Managed open-source analytics service (Hadoop ecosystem):

| Cluster Type | Engine | Best For | Status |
|-------------|--------|----------|--------|
| **Spark** | Apache Spark 3.x | ETL, ML, interactive | Active (being superseded by Databricks) |
| **Hadoop** | MapReduce, Hive, Pig | Legacy batch | Legacy |
| **HBase** | Apache HBase | NoSQL wide-column | Niche |
| **Kafka** | Apache Kafka | Message streaming | Active (but MSK/Event Hubs preferred) |
| **Interactive Query** | Hive LLAP | Interactive SQL | Active |

**Pricing:** VM-based (D-series, E-series) + HDInsight surcharge (~30% markup).

**Recommendation:** For new projects, use Databricks (Spark), Event Hubs (Kafka), or Fabric instead.

### 1.4 Azure Functions for Data

Serverless event-driven compute for lightweight data processing:

```python
# Azure Function: Process Event Hub messages
import azure.functions as func
import json
import logging
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()

@app.event_hub_message_trigger(
    arg_name="events",
    event_hub_name="member-events",
    connection="EventHubConnection",
    cardinality=func.Cardinality.MANY
)
@app.blob_output(
    arg_name="outputblob",
    path="processed/members/{datetime:yyyy}/{datetime:MM}/{datetime:dd}/batch.json",
    connection="StorageConnection"
)
def process_member_events(events: list[func.EventHubEvent], outputblob: func.Out[str]):
    """Process batch of Event Hub messages and write to blob storage."""
    processed = []
    for event in events:
        body = json.loads(event.get_body().decode("utf-8"))
        processed.append({
            "memberCode": body.get("memberCode"),
            "eventType": body.get("eventType"),
            "timestamp": event.enqueued_time.isoformat(),
            "partition": event.partition_key
        })
        logging.info(f"Processed event for member {body.get('memberCode')}")

    outputblob.set(json.dumps(processed))


@app.timer_trigger(
    schedule="0 0 1 * * *",  # 1 AM daily
    arg_name="timer"
)
def daily_data_quality_check(timer: func.TimerRequest):
    """Daily data quality check on landing zone."""
    if timer.past_due:
        logging.warning("Timer is past due!")

    blob_client = BlobServiceClient.from_connection_string(
        os.environ["StorageConnection"]
    )
    container = blob_client.get_container_client("bronze")

    # Check if today's data landed
    today = datetime.now().strftime("%Y/%m/%d")
    blobs = list(container.list_blobs(name_starts_with=f"raw/members/{today}"))

    if not blobs:
        logging.error(f"No data found for {today}!")
        # Send alert via Logic App or SendGrid
```

**Pricing:**

| Plan | Compute | Free Grant | Price |
|------|---------|-----------|-------|
| **Consumption** | Serverless | 1M executions + 400K GB-s/month | $0.20/million exec + $0.000016/GB-s |
| **Premium** | Pre-warmed | None | ~$0.173/vCPU-hr |
| **Dedicated** | App Service | None | App Service pricing |
| **Flex Consumption** | Serverless + VNet | 100K executions | $0.20/million exec |

### 1.5 Azure Logic Apps

Visual workflow orchestration (low-code/no-code):

```json
{
  "definition": {
    "triggers": {
      "When_a_blob_is_added": {
        "type": "ApiConnection",
        "inputs": {
          "host": { "connection": { "name": "@parameters('$connections')['azureblob']['connectionId']" } },
          "method": "get",
          "path": "/datasets/default/triggers/batch/onupdatedfile",
          "queries": { "folderId": "/bronze/raw/members/" }
        },
        "recurrence": { "frequency": "Minute", "interval": 5 }
      }
    },
    "actions": {
      "Parse_CSV": {
        "type": "ParseCsv",
        "inputs": { "content": "@triggerBody()" }
      },
      "For_each_row": {
        "type": "Foreach",
        "foreach": "@body('Parse_CSV')",
        "actions": {
          "Validate_and_Insert": {
            "type": "ApiConnection",
            "inputs": {
              "host": { "connection": { "name": "@parameters('$connections')['sql']['connectionId']" } },
              "method": "post",
              "path": "/datasets/default/tables/staging.members/items",
              "body": "@item()"
            }
          }
        }
      },
      "Send_completion_email": {
        "type": "ApiConnection",
        "runAfter": { "For_each_row": ["Succeeded"] },
        "inputs": {
          "host": { "connection": { "name": "@parameters('$connections')['office365']['connectionId']" } },
          "method": "post",
          "path": "/v2/Mail",
          "body": {
            "To": "data-team@company.com",
            "Subject": "Members data ingested",
            "Body": "Processed @{length(body('Parse_CSV'))} records"
          }
        }
      }
    }
  }
}
```

---

## 2. Streaming & Messaging

### 2.1 Azure Event Hubs

Big data streaming platform with Kafka compatibility:

```
┌───────────────────────────────────────────────────────────────┐
│                    Azure Event Hubs                            │
│                                                               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ Part 0  │  │ Part 1  │  │ Part 2  │  │ Part N  │        │
│  │         │  │         │  │         │  │         │        │
│  │ offset  │  │ offset  │  │ offset  │  │ offset  │        │
│  │ 0..100  │  │ 0..80   │  │ 0..120  │  │ 0..95   │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │               │
│       └────────────┼────────────┼────────────┘               │
│                    │                                          │
│  ┌─────────────────▼──────────────────────────────────────┐  │
│  │              Consumer Groups                            │  │
│  │                                                         │  │
│  │  $Default     │  analytics  │  archival                 │  │
│  │  (real-time)  │  (batch)    │  (cold storage)           │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  Features:                                                    │
│  • Kafka protocol compatible (kafka:// endpoint)             │
│  • Capture to ADLS Gen2 / Blob (Avro format)                │
│  • Schema Registry (Avro schemas)                            │
│  • Geo-disaster recovery (active-passive)                    │
│  • Auto-inflate (auto-scale TUs)                             │
│  • Private endpoints                                         │
└───────────────────────────────────────────────────────────────┘
```

#### Python Producer/Consumer

```python
# Producer: Send events to Event Hub
from azure.eventhub import EventHubProducerClient, EventData
import json

connection_str = "Endpoint=sb://mynamespace.servicebus.windows.net/;..."
eventhub_name = "member-events"

producer = EventHubProducerClient.from_connection_string(
    conn_str=connection_str,
    eventhub_name=eventhub_name
)

with producer:
    event_data_batch = producer.create_batch()
    for member in members_list:
        event = EventData(json.dumps({
            "memberCode": member["code"],
            "eventType": "TIER_CHANGE",
            "tierCode": member["tier"],
            "timestamp": datetime.utcnow().isoformat()
        }))
        event.properties = {"source": "loyalty-api"}
        event_data_batch.add(event)
    producer.send_batch(event_data_batch)


# Consumer: Read events from Event Hub
from azure.eventhub import EventHubConsumerClient

def on_event(partition_context, event):
    body = json.loads(event.body_as_str())
    print(f"Partition {partition_context.partition_id}: {body['memberCode']}")
    partition_context.update_checkpoint(event)

consumer = EventHubConsumerClient.from_connection_string(
    conn_str=connection_str,
    consumer_group="analytics",
    eventhub_name=eventhub_name
)

with consumer:
    consumer.receive(
        on_event=on_event,
        starting_position="-1"  # From beginning
    )
```

#### Kafka Compatibility

```python
# Use Kafka client with Event Hubs (no code changes needed)
from confluent_kafka import Producer

kafka_conf = {
    "bootstrap.servers": "mynamespace.servicebus.windows.net:9093",
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": "$ConnectionString",
    "sasl.password": "Endpoint=sb://mynamespace.servicebus.windows.net/;SharedAccessKeyName=...",
}

producer = Producer(kafka_conf)
producer.produce("member-events", key="M001", value=json.dumps({"tier": "GOLD"}))
producer.flush()
```

#### Event Hubs Capture

```bash
# Enable capture to ADLS Gen2
az eventhubs eventhub update \
  --name member-events \
  --namespace-name mynamespace \
  --resource-group myRG \
  --enable-capture true \
  --capture-interval 300 \
  --capture-size-limit 314572800 \
  --destination-name EventHubArchive.AzureBlockBlob \
  --storage-account mystorageaccount \
  --blob-container capture \
  --archive-name-format "{Namespace}/{EventHub}/{PartitionId}/{Year}/{Month}/{Day}/{Hour}/{Minute}/{Second}"
```

#### Pricing

| Tier | Throughput | Features | Price |
|------|-----------|----------|-------|
| **Basic** | 1 MB/s in, 2 MB/s out per TU | 1 consumer group, 1 day retention | ~$0.015/hr/TU |
| **Standard** | Same per TU | 20 consumer groups, 7 day retention, Capture | ~$0.03/hr/TU |
| **Premium** | Per PU (dedicated resources) | Dynamic partitions, 90 day retention, large messages (1MB+), Geo-DR | ~$1.23/hr/PU |
| **Dedicated** | 1 CU = 20 PU equiv | Full tenant isolation, 90 day retention | ~$6.85/hr/CU |

### 2.2 Azure Service Bus

Enterprise message broker for reliable application integration:

```python
# Service Bus: Send message with session and dedup
from azure.servicebus import ServiceBusClient, ServiceBusMessage

conn_str = "Endpoint=sb://myservicebus.servicebus.windows.net/;..."

with ServiceBusClient.from_connection_string(conn_str) as client:
    # Queue: Point-to-point messaging
    with client.get_queue_sender("order-processing") as sender:
        message = ServiceBusMessage(
            body=json.dumps({"orderId": "ORD-001", "amount": 1500.00}),
            session_id="customer-123",           # FIFO within session
            message_id="msg-unique-001",         # Dedup key
            subject="NEW_ORDER",                 # Routing label
            time_to_live=timedelta(hours=24),     # Message expires
            application_properties={
                "priority": "high",
                "region": "SEA"
            }
        )
        sender.send_messages(message)

    # Topic: Pub/sub with subscriptions
    with client.get_topic_sender("member-events") as sender:
        msg = ServiceBusMessage(
            body=json.dumps({"memberCode": "M001", "event": "UPGRADE"}),
            application_properties={"tierCode": "GOLD"}
        )
        sender.send_messages(msg)

    # Subscription with filter (SQL rule)
    # Only receives messages where tierCode = 'GOLD'
    with client.get_subscription_receiver(
        "member-events", "gold-subscribers"
    ) as receiver:
        for msg in receiver.receive_messages(max_wait_time=30):
            print(f"Gold event: {msg}")
            receiver.complete_message(msg)
```

**Key Features:**

| Feature | Description |
|---------|-------------|
| **Sessions** | FIFO guarantee within session |
| **Dead-lettering** | Poison messages auto-moved to DLQ |
| **Duplicate detection** | Based on message_id (configurable window) |
| **Transactions** | Atomic send/complete across queues |
| **Auto-forwarding** | Chain queues/topics together |
| **Scheduled delivery** | Send now, deliver later |
| **Message deferral** | Skip message, process later by sequence number |

### 2.3 Azure Event Grid

Serverless event routing service:

```python
# Event Grid: React to blob storage events
from azure.eventgrid import EventGridPublisherClient, EventGridEvent
from azure.identity import DefaultAzureCredential

# Custom event publishing
credential = DefaultAzureCredential()
client = EventGridPublisherClient(
    "https://mytopic.southeastasia-1.eventgrid.azure.net/api/events",
    credential
)

event = EventGridEvent(
    data={"memberCode": "M001", "newTier": "PLATINUM"},
    subject="loyalty/members/tier-change",
    event_type="Loyalty.TierChanged",
    data_version="1.0"
)
client.send([event])
```

**Event sources:** Blob Storage, Resource Groups, IoT Hub, Container Registry, Service Bus, Event Hubs, Custom Topics, Azure AD, Key Vault, App Configuration.

**Event handlers:** Functions, Logic Apps, Event Hubs, Service Bus, Storage Queues, Webhooks, Power Automate.

### 2.4 Streaming Comparison

| Feature | Event Hubs | Service Bus | Event Grid | Stream Analytics |
|---------|-----------|-------------|------------|------------------|
| **Type** | Big data streaming | Enterprise messaging | Event routing | Stream processing |
| **Protocol** | AMQP, Kafka, HTTPS | AMQP, SBMP | HTTP/CloudEvents | N/A (engine) |
| **Ordering** | Per partition | Per session | No guarantee | Per partition |
| **Throughput** | Millions/sec | Thousands/sec | Millions/sec | Depends on SU |
| **Latency** | ~ms | ~ms | ~ms | ~seconds |
| **Message size** | 1 MB (standard), 1 MB+ (Premium) | 256 KB - 100 MB | 1 MB | N/A |
| **Retention** | 1-90 days | 14 days (unlimited with Premium) | 24 hours retry | N/A |
| **Best for** | Telemetry, analytics, CDC streams | Business transactions, commands | Reactive automation | Real-time SQL on streams |
| **Dedup** | No (consumer responsibility) | Yes (message_id) | No | Temporal dedup |
| **DLQ** | No native | Yes (built-in) | Yes (storage account) | Error output |

---

## 3. Data Governance

### 3.1 Microsoft Purview

Unified governance, risk, and compliance platform:

```
┌────────────────────────────────────────────────────────────────┐
│                     Microsoft Purview                          │
│                                                                │
│  ┌────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ Data Map       │  │ Data Catalog     │  │ Data Estate   │ │
│  │                │  │                  │  │ Insights      │ │
│  │ • Scan sources │  │ • Search & browse│  │ • Analytics   │ │
│  │ • Auto-classify│  │ • Business       │  │ • Sensitivity │ │
│  │ • Lineage      │  │   glossary       │  │   reports     │ │
│  │ • Collections  │  │ • Annotations    │  │ • Usage stats │ │
│  └───────┬────────┘  └────────┬─────────┘  └───────────────┘ │
│          │                    │                                │
│  ┌───────▼────────────────────▼──────────────────────────────┐│
│  │              Supported Sources                             ││
│  │                                                            ││
│  │  Azure SQL │ ADLS Gen2 │ Synapse │ Cosmos DB │ Fabric     ││
│  │  Power BI  │ Databricks│ AWS S3  │ GCS      │ Snowflake  ││
│  │  Oracle    │ SAP       │ Teradata│ Hive     │ SQL Server ││
│  └────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────┘
```

```bash
# Register a data source for scanning
az purview account create \
  --name myPurviewAccount \
  --resource-group myRG \
  --location southeastasia

# CLI or REST API for registering sources
# Typically done via Purview Studio UI or REST API
curl -X PUT \
  "https://myPurviewAccount.purview.azure.com/scan/datasources/adls-bronze" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "AdlsGen2",
    "properties": {
      "endpoint": "https://mystorageaccount.dfs.core.windows.net/",
      "resourceGroup": "myRG",
      "subscriptionId": "sub-id",
      "collection": { "referenceName": "data-engineering", "type": "CollectionReference" }
    }
  }'
```

**Key Features:**

| Feature | Description |
|---------|-------------|
| **Auto-classification** | 200+ built-in classifiers (PII, financial, healthcare) |
| **Sensitivity labels** | M365 labels applied to data assets |
| **Data lineage** | Visual lineage from ADF, Synapse, Databricks |
| **Business glossary** | Define and manage business terms |
| **Collections** | Organize assets with access control |
| **Multi-cloud scanning** | Scan AWS S3, GCS, Snowflake, Databricks |
| **M365 integration** | Labels flow to SharePoint, Teams, OneDrive |

**Pricing:** Based on Data Map capacity units (~$0.413/capacity unit/hr) + scanning volume.

### 3.2 Azure Data Share

Share data across organizations without copying:

| Mode | How It Works | Latency | Supported Sources |
|------|-------------|---------|-------------------|
| **Snapshot** | Full or incremental copy to recipient | Minutes-hours | ADLS Gen2, Blob, SQL, Synapse, Data Explorer |
| **In-place** | Direct access (no copy) | Real-time | Data Explorer, Synapse SQL |

```bash
# Create a data share
az datashare create \
  --account-name myDataShareAccount \
  --name MemberDataShare \
  --resource-group myRG \
  --share-kind CopyBased \
  --description "Monthly member tier aggregates"

# Add a dataset to share
az datashare dataset create \
  --account-name myDataShareAccount \
  --share-name MemberDataShare \
  --name AggregatedTiers \
  --resource-group myRG \
  --kind BlobFolder \
  --container-name gold \
  --prefix "aggregated/tiers/"
```

### 3.3 Purview vs Dataplex vs Lake Formation vs Unity Catalog

| Feature | Microsoft Purview | GCP Dataplex | AWS Lake Formation | Unity Catalog |
|---------|------------------|-------------|-------------------|---------------|
| **Focus** | Governance + compliance | Quality + discovery | Access control | Unified governance |
| **Multi-cloud** | Yes (scan S3, GCS) | GCP only | AWS only | Yes (native) |
| **Lineage** | Yes (visual) | Yes | No (DataZone) | Yes (column-level) |
| **Classification** | Auto (200+ classifiers) | Auto (profiling) | Manual | Auto + custom |
| **Access control** | Via Azure RBAC + sensitivity | IAM + row/column | Row/column/cell/tag | ABAC + row filters |
| **M365 integration** | Deep | None | None | None |
| **Open standard** | No | No | Hive-compatible | Iceberg REST |
| **Cost** | Capacity-based | Free + BQ compute | Free | Included in Premium |
| **Maturity** | Mature (rebranded) | Medium | Mature | Mature |

---

## 4. Power BI Integration

### 4.1 Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                    Power BI Architecture                           │
│                                                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────────┐    │
│  │ Power BI     │    │ Power BI     │    │ Power BI          │    │
│  │ Desktop      │    │ Service      │    │ Mobile            │    │
│  │ (Author)     │    │ (Publish)    │    │ (Consume)         │    │
│  └──────┬───────┘    └──────┬───────┘    └───────────────────┘    │
│         │                   │                                      │
│         └───────────┬───────┘                                      │
│                     │                                              │
│         ┌───────────▼───────────────────────┐                     │
│         │       Semantic Model              │                     │
│         │  (VertiPaq / Analysis Services)   │                     │
│         │                                   │                     │
│         │  Data access mode:                │                     │
│         │  ┌─────────┬───────────┬────────┐ │                     │
│         │  │ Import  │DirectQuery│Direct  │ │                     │
│         │  │         │          │Lake    │ │                     │
│         │  └────┬────┴─────┬────┴───┬────┘ │                     │
│         └───────┼──────────┼────────┼───────┘                     │
│                 │          │        │                               │
│         ┌───────▼──┐ ┌────▼────┐ ┌─▼────────┐                    │
│         │ Scheduled│ │ Live    │ │ OneLake  │                    │
│         │ refresh  │ │ query   │ │ Parquet  │                    │
│         │ (copy)   │ │ (source)│ │ (frame)  │                    │
│         └──────────┘ └─────────┘ └──────────┘                    │
└────────────────────────────────────────────────────────────────────┘
```

### 4.2 Data Access Modes

| Mode | Data Location | Refresh | Performance | Data Limit | Use Case |
|------|-------------|---------|-------------|-----------|----------|
| **Import** | In-memory (VertiPaq) | Scheduled (8x/day Pro, 48x/day Premium) | Fastest | ~1 GB (Pro), 100 GB+ (Premium) | Small-medium, dashboards |
| **DirectQuery** | Source database | Real-time | Slowest | Source limits | Real-time requirements |
| **DirectLake** | OneLake (Parquet/Delta) | Automatic (transparent) | Fast (near Import) | Guardrails per SKU | Fabric lakehouse |
| **Composite** | Mix of Import + DQ | Hybrid | Varies | Mix | Hot/cold data pattern |

### 4.3 DirectLake Deep Dive

See [AZURE_DATA_PLATFORM.md Section 3](../DATA_PLATFORM/AZURE_DATA_PLATFORM.md#3-directlake-deep-dive) for full DirectLake architecture, guardrails, V-Order, and framing details.

**Key points for data engineers:**
- Write data as Delta tables in OneLake with V-Order enabled
- Keep row groups between 100K-1M rows
- Run `OPTIMIZE` regularly to compact small files
- Monitor framing fallback to DirectQuery in Fabric Monitoring Hub
- DirectLake requires Fabric F64+ for full guardrail limits

### 4.4 Power BI REST API

```python
# Power BI REST API: Trigger dataset refresh
import requests

# Get access token
token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
token_response = requests.post(token_url, data={
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret,
    "scope": "https://analysis.windows.net/powerbi/api/.default"
})
access_token = token_response.json()["access_token"]

headers = {"Authorization": f"Bearer {access_token}"}

# Trigger refresh
refresh_url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
requests.post(refresh_url, headers=headers, json={
    "notifyOption": "MailOnFailure",
    "retryCount": 3
})

# Get refresh history
history = requests.get(refresh_url, headers=headers).json()
for refresh in history["value"][:5]:
    print(f"Status: {refresh['status']}, Start: {refresh['startTime']}")

# Get dataset info
dataset_url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}"
dataset_info = requests.get(dataset_url, headers=headers).json()
print(f"Dataset: {dataset_info['name']}, Mode: {dataset_info.get('defaultMode')}")
```

### 4.5 Power BI Licensing

| License | Price | Features |
|---------|-------|----------|
| **Power BI Free** | $0 | Personal analytics, no sharing |
| **Power BI Pro** | $10/user/mo | Share reports, 8 refreshes/day, 1 GB model |
| **Power BI Premium Per User (PPU)** | $20/user/mo | 48 refreshes/day, 100 GB model, paginated reports, AI |
| **Power BI Premium P1** | ~$5,000/mo | Capacity-based, embed, XMLA endpoint |
| **Fabric F64** | ~$8,400/mo | P1 equivalent + all Fabric workloads |

---

## 5. Security

### 5.1 Azure Key Vault

```python
# Python: Interact with Key Vault
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(
    vault_url="https://mykeyvault.vault.azure.net/",
    credential=credential
)

# Create/update secret
client.set_secret("kafka-connection-string", "Endpoint=sb://...")

# Get secret
secret = client.get_secret("kafka-connection-string")
print(f"Secret value: {secret.value}")

# List secrets
for secret_properties in client.list_properties_of_secrets():
    print(f"  {secret_properties.name}: enabled={secret_properties.enabled}")

# Soft-delete recovery
deleted = client.begin_delete_secret("old-secret")
deleted.wait()
# Recover within retention period:
client.begin_recover_deleted_secret("old-secret").wait()
```

```bash
# CLI: Key Vault operations
# Create vault with soft-delete and purge protection
az keyvault create \
  --name mykeyvault \
  --resource-group myRG \
  --location southeastasia \
  --enable-soft-delete true \
  --soft-delete-retention-days 90 \
  --enable-purge-protection true

# Grant access via RBAC
az role assignment create \
  --role "Key Vault Secrets Officer" \
  --assignee data-engineering-sp \
  --scope /subscriptions/{sub}/resourceGroups/myRG/providers/Microsoft.KeyVault/vaults/mykeyvault

# Enable private endpoint
az network private-endpoint create \
  --name pe-keyvault \
  --resource-group myRG \
  --vnet-name myVnet \
  --subnet private-endpoints \
  --private-connection-resource-id $(az keyvault show --name mykeyvault --query id -o tsv) \
  --group-ids vault \
  --connection-name pe-keyvault-conn
```

**Pricing:**

| Tier | Operations | HSM Keys | Secrets |
|------|-----------|----------|---------|
| **Standard** | $0.03/10K operations | N/A | $0.03/10K |
| **Premium** | $0.03/10K operations | $1/key/mo + $0.03/10K | $0.03/10K |

### 5.2 Managed Identity

Zero-credential access to Azure services:

```python
# Python: Use managed identity (no credentials in code)
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# DefaultAzureCredential automatically uses:
# 1. Managed Identity (in Azure)
# 2. Azure CLI credential (local dev)
# 3. Environment variables
# 4. VS Code credential
credential = DefaultAzureCredential()

# Access storage without connection strings
blob_client = BlobServiceClient(
    account_url="https://mystorageaccount.blob.core.windows.net",
    credential=credential
)
```

```bash
# Assign managed identity to resources
# System-assigned (tied to resource lifecycle)
az webapp identity assign --name myApp --resource-group myRG

# User-assigned (independent lifecycle, shared across resources)
az identity create --name data-pipeline-identity --resource-group myRG

az vm identity assign \
  --name myVM \
  --resource-group myRG \
  --identities data-pipeline-identity

# Grant storage access to managed identity
az role assignment create \
  --role "Storage Blob Data Contributor" \
  --assignee $(az identity show --name data-pipeline-identity --resource-group myRG --query principalId -o tsv) \
  --scope /subscriptions/{sub}/resourceGroups/myRG/providers/Microsoft.Storage/storageAccounts/mystorageaccount
```

**Best practices:**
- Use **user-assigned** managed identity for data pipelines (survives resource recreation)
- Use **system-assigned** for single-purpose resources
- Never store credentials in code or config files
- Use Key Vault references in ADF/Fabric for non-Azure sources

### 5.3 Private Endpoints

Private connectivity to Azure PaaS services:

| Service | Private Endpoint Group | DNS Zone |
|---------|----------------------|----------|
| **Storage (blob)** | blob | privatelink.blob.core.windows.net |
| **Storage (dfs)** | dfs | privatelink.dfs.core.windows.net |
| **SQL Database** | sqlServer | privatelink.database.windows.net |
| **Synapse SQL** | Sql | privatelink.sql.azuresynapse.net |
| **Synapse Dev** | Dev | privatelink.dev.azuresynapse.net |
| **Event Hubs** | namespace | privatelink.servicebus.windows.net |
| **Key Vault** | vault | privatelink.vaultcore.azure.net |
| **Databricks** | databricks_ui_api | privatelink.azuredatabricks.net |
| **Cosmos DB** | Sql | privatelink.documents.azure.com |
| **Purview** | account | privatelink.purview.azure.com |

**Pricing:** ~$0.01/hr per private endpoint + $0.01/GB data processed.

### 5.4 Azure AD / Entra ID

```bash
# Create service principal for data pipeline
az ad sp create-for-rbac \
  --name "data-pipeline-sp" \
  --role "Storage Blob Data Contributor" \
  --scopes /subscriptions/{sub}/resourceGroups/myRG

# Conditional Access: Require MFA for admin access
# (Typically configured via Azure Portal or Graph API)

# RBAC: Custom role for data engineers
az role definition create --role-definition '{
  "Name": "Data Engineer",
  "Description": "Custom role for data engineering team",
  "Actions": [
    "Microsoft.Storage/storageAccounts/blobServices/containers/read",
    "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/*",
    "Microsoft.Synapse/workspaces/read",
    "Microsoft.Synapse/workspaces/sqlPools/*",
    "Microsoft.Synapse/workspaces/sparkPools/*",
    "Microsoft.DataFactory/factories/read",
    "Microsoft.DataFactory/factories/pipelines/*"
  ],
  "NotActions": [
    "Microsoft.Storage/storageAccounts/delete",
    "Microsoft.Synapse/workspaces/delete"
  ],
  "AssignableScopes": ["/subscriptions/{sub}/resourceGroups/myRG"]
}'
```

### 5.5 Network Security

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure VNet Architecture                    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    VNet (10.0.0.0/16)               │    │
│  │                                                      │    │
│  │  ┌──────────────┐  ┌───────────────┐  ┌──────────┐ │    │
│  │  │ Compute      │  │ Private       │  │ Gateway  │ │    │
│  │  │ Subnet       │  │ Endpoints     │  │ Subnet   │ │    │
│  │  │ 10.0.1.0/24  │  │ 10.0.2.0/24  │  │ 10.0.3.0 │ │    │
│  │  │              │  │              │  │  /24      │ │    │
│  │  │ • Databricks │  │ • Storage    │  │ • VPN GW │ │    │
│  │  │ • VMs        │  │ • Key Vault  │  │ • ExpressRoute│ │
│  │  │ • AKS        │  │ • SQL        │  │          │ │    │
│  │  │              │  │ • Event Hub  │  │          │ │    │
│  │  └──────────────┘  └───────────────┘  └──────────┘ │    │
│  │                                                      │    │
│  │  NSG Rules:                                         │    │
│  │  • Allow outbound to Azure services (service tags)  │    │
│  │  • Deny all inbound from internet                   │    │
│  │  • Allow internal subnet communication              │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────┐           │
│  │           Service Endpoints                   │           │
│  │  Storage, SQL, Key Vault, Event Hubs,        │           │
│  │  Cosmos DB, Service Bus                       │           │
│  └──────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Infrastructure as Code

### 6.1 Terraform (AzureRM Provider)

```hcl
# Terraform: Data platform infrastructure
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90"
    }
  }
}

provider "azurerm" {
  features {}
}

# Resource Group
resource "azurerm_resource_group" "data_platform" {
  name     = "rg-data-platform-sea"
  location = "southeastasia"
}

# ADLS Gen2 Storage
resource "azurerm_storage_account" "datalake" {
  name                     = "stdatalakesea"
  resource_group_name      = azurerm_resource_group.data_platform.name
  location                 = azurerm_resource_group.data_platform.location
  account_tier             = "Standard"
  account_replication_type = "ZRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true  # Hierarchical namespace for ADLS Gen2

  blob_properties {
    delete_retention_policy {
      days = 30
    }
    container_delete_retention_policy {
      days = 30
    }
  }

  tags = {
    environment = "production"
    team        = "data-engineering"
  }
}

# ADLS Gen2 containers (bronze/silver/gold)
resource "azurerm_storage_data_lake_gen2_filesystem" "bronze" {
  name               = "bronze"
  storage_account_id = azurerm_storage_account.datalake.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "silver" {
  name               = "silver"
  storage_account_id = azurerm_storage_account.datalake.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "gold" {
  name               = "gold"
  storage_account_id = azurerm_storage_account.datalake.id
}

# Event Hubs Namespace
resource "azurerm_eventhub_namespace" "streaming" {
  name                = "ehns-loyalty-sea"
  location            = azurerm_resource_group.data_platform.location
  resource_group_name = azurerm_resource_group.data_platform.name
  sku                 = "Standard"
  capacity            = 2

  auto_inflate_enabled     = true
  maximum_throughput_units = 10
}

resource "azurerm_eventhub" "member_events" {
  name                = "member-events"
  namespace_name      = azurerm_eventhub_namespace.streaming.name
  resource_group_name = azurerm_resource_group.data_platform.name
  partition_count     = 8
  message_retention   = 7

  capture_description {
    enabled             = true
    encoding            = "Avro"
    interval_in_seconds = 300
    size_limit_in_bytes = 314572800

    destination {
      name                = "EventHubArchive.AzureBlockBlob"
      archive_name_format = "{Namespace}/{EventHub}/{PartitionId}/{Year}/{Month}/{Day}/{Hour}/{Minute}/{Second}"
      blob_container_name = "capture"
      storage_account_id  = azurerm_storage_account.datalake.id
    }
  }
}

# Key Vault
resource "azurerm_key_vault" "secrets" {
  name                       = "kv-data-platform-sea"
  location                   = azurerm_resource_group.data_platform.location
  resource_group_name        = azurerm_resource_group.data_platform.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 90
  purge_protection_enabled   = true
  enable_rbac_authorization  = true
}

# Azure Data Factory
resource "azurerm_data_factory" "etl" {
  name                = "adf-data-platform-sea"
  location            = azurerm_resource_group.data_platform.location
  resource_group_name = azurerm_resource_group.data_platform.name

  identity {
    type = "SystemAssigned"
  }

  github_configuration {
    account_name    = "myorg"
    branch_name     = "main"
    git_url         = "https://github.com"
    repository_name = "data-factory-pipelines"
    root_folder     = "/adf/"
  }
}

# Synapse Analytics Workspace
resource "azurerm_synapse_workspace" "analytics" {
  name                                 = "syn-analytics-sea"
  resource_group_name                  = azurerm_resource_group.data_platform.name
  location                             = azurerm_resource_group.data_platform.location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.silver.id
  sql_administrator_login              = "sqladmin"
  sql_administrator_login_password     = data.azurerm_key_vault_secret.sql_password.value

  identity {
    type = "SystemAssigned"
  }

  managed_virtual_network_enabled = true
}

# Databricks Workspace
resource "azurerm_databricks_workspace" "engineering" {
  name                        = "dbw-engineering-sea"
  resource_group_name         = azurerm_resource_group.data_platform.name
  location                    = azurerm_resource_group.data_platform.location
  sku                         = "premium"
  managed_resource_group_name = "rg-dbw-managed-sea"

  custom_parameters {
    no_public_ip        = true
    virtual_network_id  = azurerm_virtual_network.data_platform.id
    private_subnet_name = azurerm_subnet.dbw_private.name
    public_subnet_name  = azurerm_subnet.dbw_public.name
  }
}

# IAM: Grant ADF access to storage
resource "azurerm_role_assignment" "adf_storage" {
  scope                = azurerm_storage_account.datalake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_data_factory.etl.identity[0].principal_id
}

data "azurerm_client_config" "current" {}
```

### 6.2 Bicep (ARM Template DSL)

```bicep
// Bicep: Data Lake infrastructure
@description('Location for all resources')
param location string = resourceGroup().location

@description('Environment name')
@allowed(['dev', 'stg', 'prod'])
param environment string

// ADLS Gen2 Storage Account
resource dataLake 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'st${environment}datalake${uniqueString(resourceGroup().id)}'
  location: location
  sku: { name: 'Standard_ZRS' }
  kind: 'StorageV2'
  properties: {
    isHnsEnabled: true
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    accessTier: 'Hot'
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
  }
}

// Containers
resource bronzeContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${dataLake.name}/default/bronze'
}

resource silverContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${dataLake.name}/default/silver'
}

resource goldContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${dataLake.name}/default/gold'
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'kv-${environment}-data-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    sku: { family: 'A', name: 'standard' }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
  }
}

// Event Hub Namespace
resource eventHubNamespace 'Microsoft.EventHub/namespaces@2024-01-01' = {
  name: 'ehns-${environment}-loyalty'
  location: location
  sku: { name: 'Standard', tier: 'Standard', capacity: 2 }
  properties: {
    isAutoInflateEnabled: true
    maximumThroughputUnits: 10
  }
}

resource memberEventsHub 'Microsoft.EventHub/namespaces/eventhubs@2024-01-01' = {
  parent: eventHubNamespace
  name: 'member-events'
  properties: {
    partitionCount: 8
    messageRetentionInDays: 7
    captureDescription: {
      enabled: true
      encoding: 'Avro'
      intervalInSeconds: 300
      sizeLimitInBytes: 314572800
      destination: {
        name: 'EventHubArchive.AzureBlockBlob'
        properties: {
          storageAccountResourceId: dataLake.id
          blobContainer: 'capture'
          archiveNameFormat: '{Namespace}/{EventHub}/{PartitionId}/{Year}/{Month}/{Day}/{Hour}/{Minute}/{Second}'
        }
      }
    }
  }
}

output storageAccountName string = dataLake.name
output keyVaultName string = keyVault.name
output eventHubNamespaceName string = eventHubNamespace.name
```

---

## 7. CI/CD

### 7.1 Azure DevOps Pipelines

```yaml
# azure-pipelines.yml: Deploy data platform
trigger:
  branches:
    include:
      - main
  paths:
    include:
      - src/pipelines/**
      - infrastructure/**

variables:
  - group: data-platform-vars
  - name: azureServiceConnection
    value: 'AzureServiceConnection'

stages:
  - stage: Validate
    jobs:
      - job: LintAndTest
        pool:
          vmImage: 'ubuntu-latest'
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.12'

          - script: |
              pip install -r requirements-dev.txt
              ruff check src/
              mypy src/
              pytest tests/ --cov=src --cov-report=xml
            displayName: 'Lint, type-check, and test'

          - task: PublishTestResults@2
            inputs:
              testResultsFiles: 'junit-results.xml'

          - task: PublishCodeCoverageResults@2
            inputs:
              codeCoverageTool: 'Cobertura'
              summaryFileLocation: 'coverage.xml'

  - stage: DeployInfra
    dependsOn: Validate
    condition: succeeded()
    jobs:
      - job: Terraform
        pool:
          vmImage: 'ubuntu-latest'
        steps:
          - task: TerraformInstaller@1
            inputs:
              terraformVersion: 'latest'

          - task: TerraformTaskV4@4
            displayName: 'Terraform Init'
            inputs:
              provider: 'azurerm'
              command: 'init'
              workingDirectory: 'infrastructure/'
              backendServiceArm: '$(azureServiceConnection)'
              backendAzureRmResourceGroupName: 'rg-terraform-state'
              backendAzureRmStorageAccountName: 'stterraformstate'
              backendAzureRmContainerName: 'tfstate'
              backendAzureRmKey: 'data-platform.tfstate'

          - task: TerraformTaskV4@4
            displayName: 'Terraform Plan'
            inputs:
              provider: 'azurerm'
              command: 'plan'
              workingDirectory: 'infrastructure/'
              environmentServiceNameAzureRM: '$(azureServiceConnection)'
              commandOptions: '-out=tfplan'

          - task: TerraformTaskV4@4
            displayName: 'Terraform Apply'
            inputs:
              provider: 'azurerm'
              command: 'apply'
              workingDirectory: 'infrastructure/'
              environmentServiceNameAzureRM: '$(azureServiceConnection)'
              commandOptions: 'tfplan'

  - stage: DeployPipelines
    dependsOn: DeployInfra
    jobs:
      - job: DeployADF
        pool:
          vmImage: 'ubuntu-latest'
        steps:
          - task: AzureResourceManagerTemplateDeployment@3
            displayName: 'Deploy ADF ARM template'
            inputs:
              azureResourceManagerConnection: '$(azureServiceConnection)'
              subscriptionId: '$(subscriptionId)'
              resourceGroupName: 'rg-data-platform-sea'
              location: 'southeastasia'
              templateLocation: 'Linked artifact'
              csmFile: 'adf/ARMTemplateForFactory.json'
              csmParametersFile: 'adf/ARMTemplateParametersForFactory.json'

      - job: DeployDatabricks
        pool:
          vmImage: 'ubuntu-latest'
        steps:
          - script: |
              pip install databricks-cli
              databricks workspace import_dir \
                --overwrite \
                src/notebooks/ /ETL/
            displayName: 'Deploy Databricks notebooks'
            env:
              DATABRICKS_HOST: $(databricksHost)
              DATABRICKS_TOKEN: $(databricksToken)
```

### 7.2 GitHub Actions for Azure

```yaml
# .github/workflows/deploy-data-platform.yml
name: Deploy Data Platform

on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'infrastructure/**'

permissions:
  id-token: write   # Required for OIDC
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: |
          pip install -r requirements-dev.txt
          ruff check src/
          pytest tests/ -v

  deploy-infra:
    needs: test
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      # OIDC authentication (no secrets stored)
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - uses: hashicorp/setup-terraform@v3
      - run: |
          cd infrastructure
          terraform init \
            -backend-config="resource_group_name=rg-terraform-state" \
            -backend-config="storage_account_name=stterraformstate" \
            -backend-config="container_name=tfstate" \
            -backend-config="key=data-platform.tfstate"
          terraform plan -out=tfplan
          terraform apply tfplan

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      # Build and push to Azure Container Registry
      - run: |
          az acr login --name myacr
          docker build -t myacr.azurecr.io/data-pipeline:${{ github.sha }} .
          docker push myacr.azurecr.io/data-pipeline:${{ github.sha }}
```

### 7.3 Azure Container Registry (ACR)

```bash
# Create ACR
az acr create \
  --name myacr \
  --resource-group myRG \
  --sku Premium \
  --admin-enabled false

# Enable geo-replication
az acr replication create \
  --registry myacr \
  --location westeurope

# Image vulnerability scanning (Defender for Containers)
az security assessment list \
  --assessed-resource-id /subscriptions/{sub}/resourceGroups/myRG/providers/Microsoft.ContainerRegistry/registries/myacr

# Lifecycle policy (auto-cleanup old images)
az acr config retention update \
  --registry myacr \
  --status enabled \
  --days 30 \
  --type UntaggedManifests
```

**Pricing:**

| SKU | Storage | Build Minutes | Webhooks | Geo-Replication | Price |
|-----|---------|-------------|----------|-----------------|-------|
| **Basic** | 10 GB | 0 | 2 | No | ~$5/mo |
| **Standard** | 100 GB | 0 | 10 | No | ~$20/mo |
| **Premium** | 500 GB | 0 | 500 | Yes | ~$50/mo |

---

## 8. References

### Official Microsoft Documentation

**Data Processing:**
- [Azure Data Factory](https://learn.microsoft.com/en-us/azure/data-factory/introduction)
- [ADF Pricing](https://azure.microsoft.com/en-us/pricing/details/data-factory/)
- [ADF ARM Templates](https://learn.microsoft.com/en-us/azure/data-factory/continuous-integration-delivery)
- [Azure Stream Analytics](https://learn.microsoft.com/en-us/azure/stream-analytics/stream-analytics-introduction)
- [Stream Analytics Query Language](https://learn.microsoft.com/en-us/stream-analytics-query/stream-analytics-query-language-reference)
- [Azure Functions Python](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Azure Logic Apps](https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-overview)
- [Azure HDInsight](https://learn.microsoft.com/en-us/azure/hdinsight/hdinsight-overview)

**Streaming & Messaging:**
- [Event Hubs Overview](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-about)
- [Event Hubs for Apache Kafka](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-for-kafka-ecosystem-overview)
- [Event Hubs Capture](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-capture-overview)
- [Event Hubs Pricing](https://azure.microsoft.com/en-us/pricing/details/event-hubs/)
- [Service Bus Overview](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-messaging-overview)
- [Service Bus Python](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-python-how-to-use-queues)
- [Event Grid Overview](https://learn.microsoft.com/en-us/azure/event-grid/overview)

**Governance:**
- [Microsoft Purview](https://learn.microsoft.com/en-us/purview/purview)
- [Purview Data Map](https://learn.microsoft.com/en-us/purview/concept-elastic-data-map)
- [Azure Data Share](https://learn.microsoft.com/en-us/azure/data-share/overview)

**Security:**
- [Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/overview)
- [Key Vault Python SDK](https://learn.microsoft.com/en-us/azure/key-vault/secrets/quick-create-python)
- [Managed Identity](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview)
- [Private Endpoints](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview)
- [Azure AD / Entra ID](https://learn.microsoft.com/en-us/entra/fundamentals/whatis)
- [Azure RBAC](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview)

**Power BI:**
- [Power BI REST API](https://learn.microsoft.com/en-us/rest/api/power-bi/)
- [DirectLake Overview](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-overview)
- [Power BI Licensing](https://learn.microsoft.com/en-us/power-bi/fundamentals/service-features-license-type)
- [Power BI Pricing](https://powerbi.microsoft.com/en-us/pricing/)

**Infrastructure as Code:**
- [Terraform AzureRM Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Bicep Documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/overview)
- [Azure DevOps Pipelines](https://learn.microsoft.com/en-us/azure/devops/pipelines/)
- [GitHub Actions for Azure](https://learn.microsoft.com/en-us/azure/developer/github/github-actions)
- [Azure Container Registry](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-intro)

### Third-Party
- [ADF vs Fabric Data Factory — Data Mozart](https://data-mozart.com/azure-data-factory-vs-fabric-data-factory/)
- [Event Hubs vs Kafka — Confluent](https://www.confluent.io/blog/azure-event-hubs-kafka-vs-confluent/)
- [Purview vs Databricks Unity Catalog — Atlan](https://atlan.com/microsoft-purview-vs-databricks-unity-catalog/)

---

> **Document Version**: 2.0 | **Last Updated**: 2026-03-05
