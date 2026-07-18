# Strimzi / Kafka / Debezium — Example YAMLs

> **Generic public Strimzi/Debezium reference — NOT AIA code.** Strimzi ~0.49.1, CRD `kafka.strimzi.io/v1beta2`, Debezium **1.9.7.Final** (1.9.x keys). Every value is a placeholder (`<host>`, `my-cluster`, `SCHEMA.TABLE`).

Each block is a **complete, simple** starting template — not over-engineered. Inline `#` comments explain non-obvious lines. See the "minimal vs production" note at the end for what you can drop in a dev cluster.

---

## 1. `Kafka` — ZooKeeper-based (legacy style; still valid on 0.35–0.45)

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: my-cluster                      # cluster name; prefixes generated Services/Secrets/pods
spec:
  kafka:
    version: 3.7.0                       # Kafka version deployed (must be supported by this operator)
    replicas: 3                          # 3 brokers = tolerate 1 loss with RF=3
    listeners:
      - name: plain                      # in-cluster plaintext (dev)
        port: 9092
        type: internal                   # ClusterIP, reachable only inside K8s
        tls: false
      - name: tls                        # in-cluster TLS + mutual-TLS auth
        port: 9093
        type: internal
        tls: true
        authentication:
          type: tls                      # clients present a cert (issued via KafkaUser)
    config:
      # RF/ISR of Kafka's own internal topics — must be <= replicas at creation time
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3      # RF for new topics
      min.insync.replicas: 2             # with acks=all, need 2 in-sync for a successful write
      auto.create.topics.enable: "false" # prefer explicit KafkaTopic CRs
    storage:
      type: persistent-claim             # PVC-backed (survives pod restarts); 'ephemeral' = test only
      size: 100Gi
      class: <storage-class>             # e.g. an SSD storage class; omit to use cluster default
      deleteClaim: false                 # keep the PVC if the cluster is deleted (safety)
  zookeeper:
    replicas: 3                          # ZK ensemble (odd number for quorum)
    storage:
      type: persistent-claim
      size: 50Gi
      deleteClaim: false
  entityOperator:
    topicOperator: {}                    # enable KafkaTopic reconciliation ({} = defaults)
    userOperator: {}                     # enable KafkaUser reconciliation
```

---

## 2. `Kafka` + `KafkaNodePool` — KRaft (modern; no ZooKeeper)

Two objects. The `Kafka` CR carries cluster-wide config; the `KafkaNodePool`(s) carry node roles/replicas/storage. Requires the node-pools + KRaft annotations.

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaNodePool
metadata:
  name: controller                       # a pool of KRaft controllers
  labels:
    strimzi.io/cluster: my-cluster       # binds this pool to the Kafka CR below
spec:
  replicas: 3                            # 3 controllers = quorum
  roles:
    - controller                         # controller-only nodes (metadata quorum)
  storage:
    type: persistent-claim
    size: 20Gi                           # controllers store metadata log only (small)
    deleteClaim: false
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaNodePool
metadata:
  name: broker
  labels:
    strimzi.io/cluster: my-cluster
spec:
  replicas: 3
  roles:
    - broker                             # data-serving brokers
  storage:
    type: persistent-claim
    size: 100Gi
    deleteClaim: false
---
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: my-cluster
  annotations:
    strimzi.io/node-pools: enabled       # tell operator that nodes come from KafkaNodePool CRs
    strimzi.io/kraft: enabled            # run in KRaft mode (no ZooKeeper); 'migration' during a ZK->KRaft move
spec:
  kafka:
    version: 3.7.0
    metadataVersion: 3.7-IV2             # KRaft metadata version; bump AFTER a version upgrade
    # NOTE: no 'replicas' / 'storage' here — the node pools own those in KRaft
    listeners:
      - name: tls
        port: 9093
        type: internal
        tls: true
        authentication:
          type: tls
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
  # NOTE: no 'zookeeper:' block in KRaft mode
  entityOperator:
    topicOperator: {}
    userOperator: {}
```

---

## 3. `KafkaTopic`

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: my-topic                         # also the Kafka topic name unless spec.topicName overrides
  labels:
    strimzi.io/cluster: my-cluster       # which Kafka cluster owns this topic
spec:
  partitions: 12                         # parallelism unit; can grow, cannot shrink
  replicas: 3                            # replication factor (<= broker count)
  config:
    retention.ms: "604800000"            # 7 days; values are STRINGS here
    cleanup.policy: delete               # 'compact' to keep latest-per-key (e.g. CDC key topics)
    segment.bytes: "1073741824"          # 1 GiB segments
    min.insync.replicas: "2"
```

---

## 4. `KafkaUser` (mTLS or SCRAM, with ACLs)

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaUser
metadata:
  name: app-consumer
  labels:
    strimzi.io/cluster: my-cluster       # must match the cluster; User Operator creates a Secret named after this user
spec:
  authentication:
    type: scram-sha-512                  # password auth; 'tls' = mutual-TLS cert instead
  authorization:
    type: simple                         # built-in ACL authorizer
    acls:
      - resource:
          type: topic
          name: "myserver."              # prefix stem
          patternType: prefix            # 'literal' = exact name
        operations: [Read, Describe]     # consumer needs Read + Describe
      - resource:
          type: group
          name: app-consumer-group
        operations: [Read]               # consumer group membership
  # quotas:                              # optional throttling
  #   consumerByteRate: 10485760         # 10 MB/s
```
> Result: a Kafka principal + a K8s Secret (`app-consumer`) holding the SCRAM password (or cert for `tls`). The client mounts that Secret to authenticate.

---

## 5. `KafkaConnect` — runtime with a Debezium image from a registry

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnect
metadata:
  name: my-connect
  annotations:
    strimzi.io/use-connector-resources: "true"   # REQUIRED so KafkaConnector CRs drive this runtime
spec:
  version: 3.7.0                                  # must match the Kafka/Connect in the image
  replicas: 2                                     # stateless worker pods (a Deployment)
  bootstrapServers: my-cluster-kafka-bootstrap:9093  # the TLS listener of the Kafka CR above
  image: <registry>/kafka-connect-debezium:0.49.1-kafka-3.7.0-dbz1.9.7  # image already has Debezium 1.9.7 plugins baked in
  tls:
    trustedCertificates:                          # trust the cluster CA to talk to brokers over TLS
      - secretName: my-cluster-cluster-ca-cert    # auto-created by Strimzi
        certificate: ca.crt
  authentication:
    type: tls                                     # worker authenticates to brokers via mTLS
    certificateAndKey:
      secretName: my-connect-user                 # a KafkaUser(type: tls) issued for the Connect cluster
      certificate: user.crt
      key: user.key
  config:
    group.id: my-connect-cluster                  # unique per Connect cluster
    config.storage.topic: my-connect-configs      # internal state topics (auto-created)
    offset.storage.topic: my-connect-offsets      # <-- CDC resume offsets live here
    status.storage.topic: my-connect-status
    config.storage.replication.factor: 3          # keep >1 in prod or you lose connector state on broker loss
    offset.storage.replication.factor: 3
    status.storage.replication.factor: 3
```
> Alternative to a prebuilt `image`: use `spec.build` with `plugins[]` to let Strimzi assemble the image from Debezium artifacts. Prebuilt image is simpler and more reproducible for CI.

---

## 6. `KafkaConnector` — Debezium **Oracle** (1.9.x keys)

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnector
metadata:
  name: oracle-source
  labels:
    strimzi.io/cluster: my-connect               # MUST match the KafkaConnect runtime name
spec:
  class: io.debezium.connector.oracle.OracleConnector
  tasksMax: 1                                     # Oracle Debezium = single log reader (always 1)
  config:
    # --- source connection ---
    database.hostname: <host>
    database.port: "1521"
    database.user: <cdc_user>
    database.password: "${secrets:my-ns/oracle-secret:password}"  # from a mounted Secret, never inline
    database.dbname: <CDB_or_SID>
    database.pdb.name: <PDB>                       # only for multitenant CDB/PDB; drop otherwise
    database.connection.adapter: logminer         # 1.9 default; 'xstream' is the licensed alternative
    # --- logical name -> topic prefix ---
    database.server.name: myserver                # 1.9 KEY (2.x renamed to topic.prefix); topics = myserver.<schema>.<table>
    # --- schema history (DDL log) ---
    database.history.kafka.bootstrap.servers: my-cluster-kafka-bootstrap:9092  # 1.9 KEY (2.x: schema.history.internal.kafka.bootstrap.servers)
    database.history.kafka.topic: schema-history.myserver                       # 1.9 KEY (2.x: schema.history.internal.kafka.topic); MUST persist
    # --- scope ---
    table.include.list: SCHEMA.TABLE_A,SCHEMA.TABLE_B   # the field you edit most; schema-qualified, exact case
    snapshot.mode: initial                         # snapshot then stream; 'schema_only' skips the data snapshot
    # --- serialization (pick one; JSON shown for simplicity) ---
    key.converter: org.apache.kafka.connect.json.JsonConverter
    value.converter: org.apache.kafka.connect.json.JsonConverter
    # --- optional: flatten Debezium envelope into a plain row ---
    transforms: unwrap
    transforms.unwrap.type: io.debezium.transforms.ExtractNewRecordState
```
> DBA prereqs: archivelog ON + supplemental logging (db + per captured table) + LogMiner privileges for `<cdc_user>`.

---

## 7. `KafkaConnector` — Debezium **SQL Server** (1.9.x keys)

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnector
metadata:
  name: sqlserver-source
  labels:
    strimzi.io/cluster: my-connect
spec:
  class: io.debezium.connector.sqlserver.SqlServerConnector
  tasksMax: 1
  config:
    database.hostname: <host>
    database.port: "1433"
    database.user: <cdc_user>
    database.password: "${secrets:my-ns/mssql-secret:password}"
    database.names: <DB1>,<DB2>                    # 1.9 supports multiple DBs (older single-db used database.dbname)
    database.server.name: myserver                 # 1.9 KEY (2.x: topic.prefix)
    database.history.kafka.bootstrap.servers: my-cluster-kafka-bootstrap:9092  # 1.9 KEY (2.x: schema.history.internal.*)
    database.history.kafka.topic: schema-history.myserver                       # 1.9 KEY
    table.include.list: dbo.TABLE_A,dbo.TABLE_B
    snapshot.mode: initial
    key.converter: org.apache.kafka.connect.json.JsonConverter
    value.converter: org.apache.kafka.connect.json.JsonConverter
    transforms: unwrap
    transforms.unwrap.type: io.debezium.transforms.ExtractNewRecordState
```
> DB prereqs: SQL Server Agent running; CDC enabled at DB (`sys.sp_cdc_enable_db`) and per table (`sys.sp_cdc_enable_table`).

---

## Minimal vs production — what you can omit for a dev cluster

| Area | Dev (minimal) | Production (add back) |
|---|---|---|
| Brokers | `replicas: 1` | `replicas: 3` across AZs (`rack` + podAntiAffinity) |
| RF / ISR | `default.replication.factor: 1`, `min.insync.replicas: 1`, internal-topic RF `1` | RF `3`, `min.insync.replicas: 2`, internal + Connect topic RF `3` |
| Storage | `type: ephemeral` (no PVC) | `persistent-claim` with a class + `deleteClaim: false` |
| Listeners / auth | one `internal` `plain` listener, no `authentication` | TLS listener + `authentication` + `KafkaUser` ACLs |
| Secrets | inline placeholder | `${secrets:...}` via `externalConfiguration` / mounted Secret |
| Resources / probes / PDB / metrics | omit (defaults) | set `resources`, `podDisruptionBudget`, `metricsConfig`, `kafkaExporter` |
| Connect | `replicas: 1` | `replicas: >=2`, TLS+auth to brokers |
| KRaft controllers | one combined `[broker, controller]` pool | separate `controller` (3) + `broker` (>=3) pools |

Keep the same **field names and structure** in dev; only shrink counts/sizes and drop the hardening blocks. That way promotion to prod is additive, not a rewrite.
