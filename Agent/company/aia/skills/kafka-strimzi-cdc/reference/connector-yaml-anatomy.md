# Connector & CR YAML anatomy (Strimzi + Debezium 1.9.x)

> Generic, version-correct templates สิน can adapt. **Not AIA code.** AIA runs **Debezium 1.9.7.Final** → these use **1.9.x keys** (2.x renamed several — flagged). Always confirm against the live cluster.

## 1. `KafkaConnector` — Debezium **Oracle** (e.g. `cmic`)
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnector
metadata:
  name: cmic-connector
  labels:
    strimzi.io/cluster: <the KafkaConnect runtime name>   # MUST match the KafkaConnect CR
spec:
  class: io.debezium.connector.oracle.OracleConnector
  tasksMax: 1                                             # Oracle Debezium = 1 task (single log reader)
  config:
    # --- source connection ---
    database.hostname: <host>
    database.port: "1521"
    database.user: <cdc_user>
    database.password: "${secrets:...}"                  # via K8s secret / KafkaUser, never inline
    database.dbname: <CDB_or_SID>
    database.pdb.name: <PDB>                              # only for CDB/PDB (multitenant)
    database.connection.adapter: logminer                # 1.9 default; XStream is the alt
    # --- logical name → topic prefix (1.9 key; 2.x renamed to topic.prefix) ---
    database.server.name: cmic                            # topics become cmic.<schema>.<table>
    # --- schema history (1.9 keys; 2.x = schema.history.internal.*) ---
    database.history.kafka.bootstrap.servers: <kafka-bootstrap>:9092
    database.history.kafka.topic: schema-history.cmic
    # --- scope ---
    table.include.list: SCHEMA.TABLE_A,SCHEMA.TABLE_B     # the most-edited field
    snapshot.mode: initial                               # initial | schema_only | ...
    # --- serialization ---
    key.converter: io.confluent.connect.avro.AvroConverter    # or org.apache.kafka.connect.json.JsonConverter
    value.converter: io.confluent.connect.avro.AvroConverter
    # (+ schema registry url if Avro — confirm Confluent vs Apicurio)
    # --- optional flatten (envelope → row) ---
    transforms: unwrap
    transforms.unwrap.type: io.debezium.transforms.ExtractNewRecordState
```
**Oracle source prereqs (DBA side):** archivelog mode ON; `ALTER DATABASE ADD SUPPLEMENTAL LOG DATA;` (+ per-table for `table.include.list`); LogMiner privileges for the CDC user. Without these Debezium can't read the redo log.

## 2. `KafkaConnector` — Debezium **SQL Server** (e.g. `bbl360sql`)
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnector
metadata:
  name: bbl360sql-connector
  labels:
    strimzi.io/cluster: <KafkaConnect name>
spec:
  class: io.debezium.connector.sqlserver.SqlServerConnector
  tasksMax: 1
  config:
    database.hostname: <host>
    database.port: "1433"
    database.user: <cdc_user>
    database.password: "${secrets:...}"
    database.names: <DB1>,<DB2>                          # 1.9 supports multi-db; older = database.dbname
    database.server.name: bbl360                          # → topic prefix (1.9 key)
    database.history.kafka.bootstrap.servers: <kafka-bootstrap>:9092
    database.history.kafka.topic: schema-history.bbl360
    table.include.list: dbo.TABLE_A,dbo.TABLE_B
    snapshot.mode: initial
    key.converter: io.confluent.connect.avro.AvroConverter
    value.converter: io.confluent.connect.avro.AvroConverter
    transforms: unwrap
    transforms.unwrap.type: io.debezium.transforms.ExtractNewRecordState
```
**SQL Server source prereqs:** SQL Server **Agent running**; CDC enabled at DB (`sys.sp_cdc_enable_db`) and per table (`sys.sp_cdc_enable_table`). Debezium reads the SQL Server CDC change tables.

## 3. `KafkaConnect` — the runtime that HOSTS the connectors (likely `connector/connect/`)
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnect
metadata:
  name: dtp-connect-cluster
  annotations:
    strimzi.io/use-connector-resources: "true"           # lets KafkaConnector CRs drive this runtime
spec:
  version: 2.8.0                                          # Kafka version (matches image)
  replicas: 2                                             # worker pods (Deployment, stateless)
  bootstrapServers: <kafka-bootstrap>:9093                # → the Kafka broker cluster
  image: <ACR>/strimzi-kafka-connect:0.49.1-kafka-2.8.0-vX  # custom image w/ Debezium plugins baked in
  config:
    group.id: dtp-connect
    config.storage.topic: connect-configs                # Connect's internal state topics
    offset.storage.topic: connect-offsets                # ← connector offsets live here
    status.storage.topic: connect-status
    config.storage.replication.factor: 3
    offset.storage.replication.factor: 3
    status.storage.replication.factor: 3
  tls: { trustedCertificates: [...] }                    # talk to brokers over TLS
```
Key idea: **one Connect cluster hosts many `KafkaConnector`s**. `strimzi.io/use-connector-resources: "true"` is what makes `KafkaConnector` CRs (repo 3) get picked up automatically.

## 4. `Kafka` — the broker cluster (the still-unseen CR, in `dtp_kafka_cluster`)
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata: { name: dtp-kafka-cluster }
spec:
  kafka:
    replicas: 3
    listeners:
      - { name: tls, port: 9093, type: internal, tls: true, authentication: { type: tls } }
    storage: { type: persistent-claim, size: 100Gi, class: managed-premium }   # Azure Disk PVC
    config: { offsets.topic.replication.factor: 3, default.replication.factor: 3, min.insync.replicas: 2 }
  zookeeper: { replicas: 3, storage: { type: persistent-claim, size: 50Gi } }   # OR KRaft (no zk) in newer
  entityOperator: { topicOperator: {}, userOperator: {} }                       # bundles topic+user operators
```
This is what to compare against once สิน screenshots the real one (replicas / storage / KRaft-vs-zk / listeners).

## 5. `KafkaTopic` and `KafkaUser`
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata: { name: cmic.schema.table_a, labels: { strimzi.io/cluster: dtp-kafka-cluster } }
spec: { partitions: 12, replicas: 3, config: { retention.ms: "604800000", cleanup.policy: delete } }
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaUser
metadata: { name: databricks-consumer, labels: { strimzi.io/cluster: dtp-kafka-cluster } }
spec:
  authentication: { type: scram-sha-512 }                # or tls
  authorization:
    type: simple
    acls:
      - { resource: { type: topic, name: "cmic.", patternType: prefix }, operations: [Read, Describe] }
      - { resource: { type: group, name: databricks-cg }, operations: [Read] }
```
The User Operator turns a `KafkaUser` into a Kafka user + a **K8s Secret** holding credentials, which the Databricks consumer mounts to authenticate.

## Field cheat-sheet (what changes when)
| You want to... | Change |
|---|---|
| capture more tables | `table.include.list` |
| rename topics | `transforms` / RegexRouter, or `database.server.name` prefix |
| avoid full re-snapshot | `snapshot.mode: schema_only` (only if history acceptable) |
| point at a different DB | `database.hostname/port/dbname/names` |
| change parallelism | `tasksMax` (note: Oracle stays 1) |
| flatten CDC envelope | `transforms.unwrap` (ExtractNewRecordState) |
| move to new cluster version | rebuild in `connector-*-main<newver>`, match Connect `image` tag |
