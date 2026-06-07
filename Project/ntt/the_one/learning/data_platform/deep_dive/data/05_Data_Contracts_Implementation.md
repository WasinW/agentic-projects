# Data Contracts — Implementation Deep Dive

> Schema Registry, CI gates, evolution rules, real-world enforcement
> ทำให้ shift-left governance ใช้งานได้จริง

---

## 1. Data Contract Mental Model

### Contract = "API for Data"

เหมือน API contract แต่สำหรับ data:
- Producer commits to schema + SLA
- Consumer relies on it
- Breaking change = breaking version

### Without Contract (typical pain)

```
App team: "We renamed `phone_number` to `phone` to be cleaner"
Data team: (next day) "Why is fact_orders missing phone? 50 dashboards broken"
```

### With Contract

```
App team commits PR with renamed column
  ↓
CI runs contract validation
  ↓
"BREAKING CHANGE detected: phone_number removed"
  ↓
PR blocked
  ↓
App team must:
  1. Bump version (v2)
  2. Notify consumers
  3. Coordinate migration
```

---

## 2. Contract Components

### Required Fields

```yaml
contract:
  # Identity
  name: order_events
  version: 2.1.0
  
  # Ownership
  producer:
    team: order_team
    contact: orders@company.com
    repo: github.com/company/order-service
  
  consumers:
    - team: data_team
      use_case: warehouse_ingestion
    - team: ml_team
      use_case: fraud_model_training
  
  # Schema
  schema:
    format: avro       # or protobuf, json_schema
    location: s3://schemas/order_events/v2.1.0.avsc
  
  # SLA
  freshness:
    target: 5_minutes
    critical: 30_minutes
  completeness:
    null_pct_max:
      order_id: 0
      amount: 0
      customer_email: 0.5
  uniqueness:
    columns: [order_id]
  
  # Evolution
  compatibility: BACKWARD
  deprecation_policy:
    notice_period_days: 30
    parallel_run: true
```

### Quality Rules

```yaml
quality_rules:
  - name: amount_positive
    expression: "amount > 0"
    severity: error
  - name: status_in_enum
    expression: "status IN ('pending', 'paid', 'cancelled')"
    severity: error
  - name: customer_email_format
    expression: "customer_email LIKE '%@%.%'"
    severity: warn
```

---

## 3. Schema Format Deep Dive

### Avro

```json
{
  "type": "record",
  "name": "OrderEvent",
  "namespace": "com.company.orders",
  "fields": [
    {"name": "order_id", "type": "string"},
    {"name": "amount", "type": {"type": "decimal", "precision": 10, "scale": 2}},
    {"name": "status", "type": {
      "type": "enum",
      "name": "Status",
      "symbols": ["PENDING", "PAID", "CANCELLED"]
    }},
    {"name": "customer_email", "type": ["null", "string"], "default": null},
    {"name": "metadata", "type": {"type": "map", "values": "string"}}
  ]
}
```

**Pros**: 
- Best schema evolution support
- Compact binary encoding
- Strong typed (decimal, logical types)
- Self-describing (schema in file or via registry)

**Cons**:
- Less readable
- Slower than Protobuf for hot paths

### Protobuf

```protobuf
syntax = "proto3";

package com.company.orders;

message OrderEvent {
  string order_id = 1;
  double amount = 2;        // protobuf has limited decimal
  Status status = 3;
  optional string customer_email = 4;
  map<string, string> metadata = 5;
}

enum Status {
  STATUS_UNSPECIFIED = 0;
  STATUS_PENDING = 1;
  STATUS_PAID = 2;
  STATUS_CANCELLED = 3;
}
```

**Pros**:
- Fastest serialization
- Smallest payload
- Good evolution (with field numbers)
- Used heavily in gRPC

**Cons**:
- Limited decimal types
- Field numbers require discipline
- More boilerplate

### JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft-07/schema",
  "title": "OrderEvent",
  "type": "object",
  "required": ["order_id", "amount", "status"],
  "properties": {
    "order_id": {"type": "string"},
    "amount": {"type": "number", "minimum": 0},
    "status": {"type": "string", "enum": ["pending", "paid", "cancelled"]},
    "customer_email": {"type": ["string", "null"], "format": "email"},
    "metadata": {"type": "object", "additionalProperties": {"type": "string"}}
  }
}
```

**Pros**:
- Most readable
- Native to REST APIs
- Rich validation (regex, format, min/max)

**Cons**:
- Verbose
- Slower
- No native binary format
- Weaker evolution rules

### Decision Matrix

| Use case | Format |
|---|---|
| Kafka events | **Avro** (best evolution) |
| gRPC microservices | **Protobuf** |
| REST API | **JSON Schema** |
| Iceberg tables | **Avro/Parquet** |
| Internal data files | **Avro** |
| Public APIs | **JSON Schema/OpenAPI** |

---

## 4. Schema Compatibility Rules

### BACKWARD (most common)

> "New schema can read old data"

**Allowed**:
- Add field with default
- Remove field (consumer drops)
- Add enum value (with care)

**Forbidden**:
- Add required field (no default)
- Change type
- Rename field
- Remove enum value

```
Old: {id: 1, name: "Alice"}
New schema reads: {id: 1, name: "Alice", email: null}  ✅
```

### FORWARD

> "Old schema can read new data"

**Allowed**:
- Remove field
- Add field WITH default

**Forbidden**:
- Add required field
- Rename
- Change type

```
New: {id: 1, name: "Alice", phone: "+66"}
Old schema reads: {id: 1, name: "Alice"}  ✅ (drops phone)
```

### FULL

Both BACKWARD and FORWARD

**Allowed**:
- Add OPTIONAL field with default
- Remove OPTIONAL field

**Forbidden**: most other changes

### NONE

No compatibility check (avoid in production)

### Recommendation by Use Case

| Use case | Compatibility |
|---|---|
| Kafka producer-consumer | **BACKWARD** (consumers upgrade first) |
| Long-lived events | **FULL** (both directions) |
| API responses | **BACKWARD** |
| Internal data ETL | **BACKWARD** |

---

## 5. Schema Registry Implementation

### Confluent Schema Registry (Kafka)

```python
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

# Connect
sr_client = SchemaRegistryClient({"url": "http://schema-registry:8081"})

# Register schema
schema_str = open("order_event.avsc").read()
schema_id = sr_client.register_schema(
    subject_name="order_events-value",
    schema=Schema(schema_str, schema_type="AVRO")
)

# Producer with schema validation
serializer = AvroSerializer(
    schema_registry_client=sr_client,
    schema_str=schema_str,
)

producer = SerializingProducer({
    'bootstrap.servers': 'localhost:9092',
    'value.serializer': serializer
})

# This auto-validates schema
producer.produce(topic='order_events', value={
    "order_id": "123",
    "amount": 99.99,
    "status": "PENDING"
})
```

### Set Compatibility Mode

```bash
# Set compatibility for subject
curl -X PUT http://schema-registry:8081/config/order_events-value \
  -H "Content-Type: application/json" \
  -d '{"compatibility": "BACKWARD"}'
```

```bash
# Register new version (will be checked against compatibility)
curl -X POST http://schema-registry:8081/subjects/order_events-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schemaType": "AVRO", "schema": "..."}'

# If incompatible: 409 Conflict
```

### Multi-Cloud Schema Registries

| Service | Provider |
|---|---|
| Confluent Schema Registry | Confluent (Kafka) |
| AWS Glue Schema Registry | AWS |
| GCP Pub/Sub Schemas | GCP |
| Apicurio Registry | OSS, multi-format |
| Buf Schema Registry | OSS, Protobuf focus |

---

## 6. Data Contract CLI

### Install

```bash
pip install datacontract-cli
```

### Define Contract

```yaml
# datacontract.yaml
dataContractSpecification: 0.9.3
id: orders
info:
  title: Orders Contract
  version: 2.0.0
  owner: order_team
  contact:
    email: orders@company.com

terms:
  usage: "Order events for warehouse ingestion"
  limitations: "Not for real-time inventory"
  billing: "internal"

models:
  orders:
    type: table
    fields:
      order_id:
        type: string
        required: true
        primary: true
        unique: true
      customer_id:
        type: string
        required: true
      amount:
        type: decimal
        required: true
        precision: 10
        scale: 2
      status:
        type: text
        required: true
        enum: [pending, paid, cancelled]
      customer_email:
        type: string
        pii: true
        classification: confidential
      created_at:
        type: timestamp
        required: true

quality:
  - type: sql
    description: "Amount must be positive"
    query: |
      SELECT COUNT(*) FROM orders WHERE amount <= 0
    mustBe: 0
  - type: sql
    description: "Order IDs unique"
    query: |
      SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM orders
    mustBe: 0

servicelevels:
  availability:
    description: "99.9% uptime"
    percentage: "99.9%"
  retention:
    description: "Keep 7 years"
    period: P7Y
  freshness:
    description: "Updated within 5 minutes"
    threshold: 5m
```

### Validate

```bash
# Lint contract
datacontract lint datacontract.yaml

# Run quality checks against actual data
datacontract test datacontract.yaml \
    --server bigquery \
    --options project=my-project,dataset=warehouse

# Compare 2 versions for breaking changes
datacontract diff old_contract.yaml new_contract.yaml
```

### Generate Schemas

```bash
# Avro from contract
datacontract export --format avro datacontract.yaml > schema.avsc

# Protobuf
datacontract export --format protobuf datacontract.yaml > schema.proto

# dbt model
datacontract export --format dbt datacontract.yaml > model.yml

# JSON Schema
datacontract export --format json-schema datacontract.yaml > schema.json
```

---

## 7. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/contract-check.yml
name: Data Contract Check

on:
  pull_request:
    paths:
      - 'contracts/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Install datacontract-cli
        run: pip install datacontract-cli
      
      - name: Lint contracts
        run: |
          for contract in contracts/*.yaml; do
            datacontract lint $contract
          done
      
      - name: Detect breaking changes
        run: |
          for contract in contracts/*.yaml; do
            git show origin/main:$contract > /tmp/old.yaml || continue
            datacontract diff /tmp/old.yaml $contract --fail-on-breaking
          done
      
      - name: Run quality checks (against staging data)
        run: |
          datacontract test contracts/orders.yaml \
              --server bigquery \
              --options project=staging,dataset=warehouse
        env:
          GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.STAGING_SA }}
      
      - name: Notify consumers (on breaking change request)
        if: contains(github.event.pull_request.labels.*.name, 'breaking-change')
        run: |
          # Read consumers from contract
          # Auto-create issues in their repos
          # Slack notification
          ...
```

### dbt Contracts Integration

```yaml
# models/marts/orders/orders.yml
models:
  - name: fct_orders
    config:
      contract:
        enforced: true
    columns:
      - name: order_id
        data_type: string
        constraints:
          - type: not_null
          - type: primary_key
      - name: amount
        data_type: numeric
        constraints:
          - type: not_null
          - type: check
            expression: "amount > 0"
```

```bash
dbt build  # ← contract enforced; build fails if schema doesn't match
```

---

## 8. Producer-Side Validation

### Pattern: Validate Before Publish

```python
from datacontract.validator import ContractValidator

validator = ContractValidator.from_file("contracts/orders.yaml")

def publish_order(order_event):
    # Validate against contract
    result = validator.validate(order_event)
    if not result.is_valid:
        raise ContractViolation(result.errors)
    
    # Publish to Kafka
    producer.produce(topic='orders', value=order_event)
```

### Pattern: Pydantic Models from Contract

```python
# Auto-generate pydantic from contract
# datacontract export --format python contracts/orders.yaml

from pydantic import BaseModel, Field, validator
from decimal import Decimal
from typing import Optional
from datetime import datetime

class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"

class Order(BaseModel):
    order_id: str
    customer_id: str
    amount: Decimal = Field(gt=0)  # > 0
    status: OrderStatus
    customer_email: Optional[str] = None
    created_at: datetime
    
    @validator('customer_email')
    def email_format(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email')
        return v

# In producer code
def publish_order(data: dict):
    order = Order.parse_obj(data)  # raises if invalid
    producer.produce('orders', order.json())
```

---

## 9. Consumer-Side Validation

### Pattern: Schema-First Consumer

```python
from confluent_kafka.schema_registry.avro import AvroDeserializer

deserializer = AvroDeserializer(sr_client)

consumer = DeserializingConsumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'data-warehouse',
    'value.deserializer': deserializer,
    'isolation.level': 'read_committed'
})

consumer.subscribe(['orders'])
while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    
    order = msg.value()  # auto-deserialized to dict matching schema
    process(order)
```

### Pattern: Quality Check Consumer

```python
# Sidecar consumer that validates quality
class QualityCheckConsumer:
    def __init__(self, contract_file):
        self.validator = ContractValidator.from_file(contract_file)
        self.metrics = MetricsClient()
    
    def consume(self, topic):
        for message in consume_kafka(topic):
            result = self.validator.validate(message)
            
            self.metrics.increment(f'contract.{topic}.total')
            if not result.is_valid:
                self.metrics.increment(f'contract.{topic}.invalid')
                
                if result.severity == 'error':
                    self.send_to_dlq(message, result.errors)
                else:
                    self.log_warning(message, result.warnings)
```

---

## 10. Breaking Change Process (Step-by-Step)

### Scenario: Need to rename `customer_email` → `email`

#### Phase 1: Plan
```yaml
# Increment major version
version: 3.0.0  # was 2.x.x
breaking_changes:
  - description: "Renamed customer_email to email"
    migration_guide: "https://wiki/migration-v3"
    deprecation_date: 2026-06-01
    removal_date: 2026-09-01
```

#### Phase 2: Add new field (forward-compatible)
```yaml
fields:
  - name: customer_email
    deprecated: true
    deprecation_message: "Use 'email' instead"
  - name: email
    type: string
    description: "Customer email"
```

Producer writes BOTH for transition period.

#### Phase 3: Notify consumers
```python
# Auto-script
for consumer in contract.consumers:
    create_github_issue(
        repo=consumer.repo,
        title="Migration: customer_email → email by 2026-09-01",
        body=migration_guide
    )
    slack_notify(consumer.team)
```

#### Phase 4: Track migration
```sql
-- Dashboard: which consumers still use deprecated field?
SELECT consumer_id, last_used_at
FROM data_access_logs
WHERE accessed_field = 'customer_email'
  AND last_used_at > NOW() - INTERVAL '7 days'
```

#### Phase 5: Remove (after deprecation period)
```yaml
# v4.0.0
fields:
  - name: email
    type: string
  # customer_email removed
```

---

## 11. Org-Level Contract Strategy

### Contract Repository

```
contracts/
├── domains/
│   ├── orders/
│   │   ├── order_events_v2.yaml
│   │   └── order_status_v1.yaml
│   ├── customers/
│   │   └── customer_master_v3.yaml
│   └── inventory/
│       └── stock_levels_v1.yaml
├── shared_types/
│   ├── address.yaml
│   ├── money.yaml
│   └── timestamp.yaml
├── policies/
│   ├── pii_classification.yaml
│   └── retention_rules.yaml
└── docs/
    ├── breaking_change_process.md
    ├── contract_template.yaml
    └── governance.md
```

### Approval Process

```
Author opens PR
    ↓
CI auto-checks: lint, breaking change detection
    ↓
Required reviewers (CODEOWNERS):
  - Producer team lead
  - Consumer team lead (if breaking)
  - Data steward (if PII)
    ↓
On merge: schema deployed to registry
```

### Catalog Integration

```python
# Auto-sync contracts → catalog
def sync_to_catalog():
    for contract in load_all_contracts():
        datahub.upsert_dataset(
            urn=f"urn:li:dataset:({contract.platform},{contract.name},PROD)",
            schema=contract.schema,
            ownership={"team": contract.producer.team},
            tags=contract.tags,
            sla=contract.servicelevels
        )
```

---

## 12. Anti-Patterns

### ❌ "Document is the Contract"
```
Confluence page with "agreed schema"
→ Nobody reads, nobody enforces
→ Just decoration
```

### ❌ Contract Written After Production
```
Build pipeline first, then write contract to "match"
→ Contract becomes documentation, not enforcement
```

### ❌ Validate Only at Consumer
```
Producer changes anything
→ Discovered at consumer (too late)
→ Pollution already in topic/table
```

### ❌ Breaking Changes Without Versioning
```
"Just update the schema"
→ Consumers break silently
```

### ❌ One Contract Per File for Tiny Changes
```
Every minor change = new file = explosion
→ Use version field within file
```

### ❌ No SLA in Contract
```
"customer_data" — but no freshness/availability promised
→ When data is late, who's responsible?
```

---

## 13. Cheat Sheet

### Q: "เริ่ม implement Data Contracts ยังไง?"
> "1. Pick 3-5 critical entities (orders, customers, transactions)
> 2. Write contracts in YAML, store in Git
> 3. Set up CI gate: lint + breaking change detection
> 4. Add Schema Registry for streams (Confluent SR)
> 5. Educate teams on process
> 6. Expand gradually — 12 contracts > 100 unenforced"

### Q: "Avro vs Protobuf vs JSON Schema?"
> "Avro: Kafka events, best schema evolution
> Protobuf: gRPC microservices, fastest
> JSON Schema: REST APIs, most readable
> Most enterprises = Avro for events + JSON Schema for APIs"

### Q: "BACKWARD vs FULL compatibility?"
> "BACKWARD = upgrade consumers first, then producer (most common)
> FULL = both can be upgraded any order (strictest)
> Use BACKWARD for streams, FULL for cross-team APIs with no migration coordination"

### Q: "เมื่อ Producer ไม่อยากใช้ contract?"
> "Argument: 'extra friction', 'slows us down'
> Counter: 1 broken downstream = 100x rework
> Strategy: start with mostly-passive contracts (warning), graduate to enforce
> Show value: 'last quarter we caught 5 breaking changes before prod'"

---

## Sources

- [Data Contracts Explained: Key Aspects, Tools, Setup in 2026](https://atlan.com/data-contracts/)
- [Data Contracts for Schema Registry on Confluent Platform](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html)
- [Data Contract CLI](http://cli.datacontract.com/)
- [datacontract-cli GitHub](https://github.com/datacontract/datacontract-cli)
- [dbt Data Contracts: Quick Primer](https://atlan.com/dbt-data-contracts/)
- [Avro vs Protobuf vs JSON Schema](https://www.conduktor.io/glossary/avro-vs-protobuf-vs-json-schema)
- [Schema Evolution in Apache Avro, Protobuf, and JSON Schema](https://www.javacodegeeks.com/2025/06/schema-evolution-in-apache-avro-protobuf-and-json-schema.html)
- [An Engineer's Guide to Data Contracts - Pt. 2](https://dataproducts.substack.com/p/an-engineers-guide-to-data-contracts-6df)
