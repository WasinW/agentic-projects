<!-- Mirror of knowledge_chat/strimzi_config_20260702.md — keep in sync. -->

# Strimzi / Kafka / Debezium — Field Glossary

> **Generic public Strimzi/Debezium reference — NOT AIA code.** Version-correct for **Strimzi ~0.49.1** (also valid for 0.35/0.38/0.45 except where noted), CRD apiVersion **`kafka.strimzi.io/v1beta2`**, and **Debezium 1.9.7.Final** (1.9.x config keys). All values are placeholders.
>
> Scope note: ZooKeeper is **legacy** and removed in the newest Strimzi. KRaft is configured via **`KafkaNodePool`**. Both are covered below.

---

## 0. Two different layers of "fields"

There are two distinct things people call "CRD fields":

1. **The CRD *envelope*** — the Kubernetes `CustomResourceDefinition` object that *registers* `Kafka` as a kind. Its fields (`versions[].name`, `served`, `schema`, etc.) describe the *API itself*. You rarely edit these; the Strimzi operator ships them. Covered in §1.
2. **The `Kafka` custom resource *spec*** — what *you* write to declare a cluster (`spec.kafka.replicas`, etc.). Covered in §2 onward.

Don't confuse them: `served: true` in §1 is a property of the *API version*, not of your Kafka cluster.

---

## 1. `Kafka` CRD envelope (the `CustomResourceDefinition` object)

These live under `spec.versions[]` and `spec.names` of the `CustomResourceDefinition` named `kafkas.kafka.strimzi.io`. They describe the CRD, not your cluster.

| Field | Meaning | Example / type | Required? |
|---|---|---|---|
| `spec.versions[].name` | API version string this entry defines | `v1beta2` (string) | required |
| `spec.versions[].served` | Whether the API server serves/accepts this version | `true` (bool) | required |
| `spec.versions[].storage` | Whether objects are **persisted** in etcd at this version (exactly one version must be `true`) | `true` (bool) | required |
| `spec.versions[].deprecated` | Marks an API version as deprecated | `false` (bool) | optional |
| `spec.versions[].deprecationWarning` | Custom warning shown by kubectl when the deprecated version is used | `"v1beta1 is deprecated..."` (string) | optional |
| `spec.versions[].subresources` | Enables `/status` (and `/scale`) subresources so the operator writes `status` separately from `spec` | `{ status: {} }` (object) | optional |
| `spec.versions[].additionalPrinterColumns` | Extra columns shown by `kubectl get kafka` (e.g. Desired Replicas, Ready, Metadata State) | list of `{name,type,jsonPath}` | optional |
| `spec.versions[].schema.openAPIV3Schema` | The OpenAPI v3 structural schema used to **validate** every `Kafka` CR (this is where every field below is actually defined/typed) | large object | required |
| `spec.scope` | `Namespaced` vs `Cluster` | `Namespaced` (string) | required |
| `spec.names.{kind,plural,singular,shortNames,categories}` | How the kind is named/queried | `kind: Kafka`, `plural: kafkas`, `shortNames: [k]` | required (kind/plural) |

> Practical: `kubectl get crd kafkas.kafka.strimzi.io -o yaml` shows all of the above. `served`/`storage` matter during a Strimzi upgrade that changes API versions.

---

## 2. `Kafka` → `spec.kafka.*` (the broker config — the part you tune most)

| Field | Meaning | Example / type | Required? |
|---|---|---|---|
| `version` | Kafka broker/protocol version the operator deploys | `3.7.0` (string) | optional (defaults per operator) |
| `metadataVersion` | KRaft **metadata** version (`inter.broker.protocol` analogue for KRaft). Bump *after* broker `version` upgrade. | `3.7-IV2` (string) | optional (KRaft only) |
| `replicas` | Number of broker nodes (ignored when using `KafkaNodePool`, which owns replicas) | `3` (int) | required (non-nodepool) |
| `image` | Override the broker container image | `<registry>/kafka:0.49.1-kafka-3.7.0` | optional |
| `listeners` | List of ways clients reach the brokers (see sub-table) | list | **required** |
| `config` | Passthrough of Apache Kafka broker settings (see sub-table) | map | optional |
| `storage` | Broker data storage (see sub-table) | object | required (non-nodepool) |
| `authorization` | Authorization plugin (see sub-table) | object | optional |
| `rack` | Rack-awareness for replica spread; `topologyKey` maps to a node label (e.g. AZ) | `{ topologyKey: topology.kubernetes.io/zone }` | optional |
| `brokerRackInitImage` | Image for the init container that resolves the node's rack label | `<registry>/operator:0.49.1` | optional |
| `livenessProbe` / `readinessProbe` | Probe tuning | `{ initialDelaySeconds: 15, timeoutSeconds: 5 }` | optional |
| `jvmOptions` | JVM heap/flags: `-Xms`, `-Xmx`, `-XX`, `gcLoggingEnabled`, `javaSystemProperties` | `{ -Xms: 4g, -Xmx: 4g }` | optional |
| `jmxOptions` | Expose JMX; optionally password-auth it | `{ authentication: { type: password } }` | optional |
| `resources` | K8s CPU/memory requests & limits | `{ requests: {cpu: "1", memory: 4Gi}, limits: {...} }` | optional (recommended) |
| `metricsConfig` | Prometheus JMX exporter config (via ConfigMap ref) | `{ type: jmxPrometheusExporter, valueFrom: {...} }` | optional |
| `logging` | Log level config: `inline` or `external` (ConfigMap) | `{ type: inline, loggers: {"kafka.root.logger.level": INFO} }` | optional |
| `template` | Customize generated K8s objects (see §2.7) | object | optional |
| `tieredStorage` | Enable Kafka tiered storage (remote log tier); `type: custom` + `remoteStorageManager` | object | optional (newer) |
| `quotas` | Client quotas plugin: `type: kafka` (built-in) or `strimzi` (Strimzi quotas plugin with `producerByteRate`, `consumerByteRate`, `requestPercentage`, `controllerMutationRate`) | object | optional |

### 2.1 `listeners[]` sub-fields

| Field | Meaning | Example / type | Required? |
|---|---|---|---|
| `name` | Listener name (lowercase alnum, ≤11 chars); part of the generated port/service names | `tls`, `plain`, `external` | required |
| `port` | Listener port (≥9092; must be unique) | `9093` (int) | required |
| `type` | How it's exposed (see values below) | `internal` | required |
| `tls` | Encrypt this listener with TLS | `true` (bool) | required |
| `authentication` | Client auth mechanism (see values below) | `{ type: tls }` | optional (no auth if omitted) |
| `configuration` | Listener-specific extras: `bootstrap`/`brokers` overrides, `brokerCertChainAndKey` (custom cert), `useServiceDnsDomain`, `advertisedHost/Port` | object | optional |

**`type` values:** `internal` (ClusterIP, in-cluster) · `cluster-ip` (per-broker ClusterIP, TCP) · `nodeport` · `loadbalancer` · `route` (OpenShift) · `ingress` (needs host config + TLS/SNI).

**`authentication.type` values:** `tls` (mTLS) · `scram-sha-512` · `oauth` · `custom`.

### 2.2 `config` — common broker settings (Apache Kafka keys, passed through)

| Key | Meaning | Example | Notes |
|---|---|---|---|
| `default.replication.factor` | Default RF for auto-created topics | `3` | set ≥3 in prod |
| `min.insync.replicas` | Min in-sync replicas for `acks=all` writes | `2` | pairs with RF=3 |
| `offsets.topic.replication.factor` | RF of `__consumer_offsets` | `3` | must be ≤ broker count at creation |
| `transaction.state.log.replication.factor` | RF of `__transaction_state` | `3` | for exactly-once/txns |
| `transaction.state.log.min.isr` | Min ISR for the txn log | `2` | |
| `log.retention.hours` (or `.ms` / `.bytes`) | How long/large data is kept before deletion | `168` (7d) | `.ms` wins if both set |
| `log.segment.bytes` | Log segment file size | `1073741824` | affects retention granularity |
| `auto.create.topics.enable` | Auto-create topics on first produce | `false` | prefer `false` + `KafkaTopic` CRs |
| `num.partitions` | Default partitions for auto-created topics | `3` | |

> Strimzi **forbids** setting a handful of keys via `config` (it manages them): e.g. broker/node ids, `listeners`, `advertised.*`, `zookeeper.connect`, security/SSL keystore paths, `log.dirs`. Set those via the dedicated CR fields instead.

### 2.3 `storage`

| Field | Meaning | Example / type | Required? |
|---|---|---|---|
| `type` | `ephemeral` (emptyDir, test only) · `persistent-claim` (PVC) · `jbod` (list of persistent-claim volumes) | `persistent-claim` | required |
| `size` | Volume size (persistent-claim) | `100Gi` | required for persistent-claim |
| `class` | StorageClass name (e.g. Azure disk class) | `managed-premium` | optional |
| `deleteClaim` | Delete the PVC when the cluster/broker is removed | `false` (bool) | optional (default false) |
| `id` | Volume id (JBOD, per volume) | `0` (int) | required in JBOD |
| `overrides` | Per-broker storage class overrides (e.g. per-AZ class) | list | optional |

### 2.4 `authorization`

| Field | Meaning | Example / type |
|---|---|---|
| `type` | `simple` (built-in ACL authorizer) · `opa` (Open Policy Agent) · `keycloak` (OAuth/Keycloak) · `custom` | `simple` |
| `superUsers` | Principals bypassing ACLs | `[ "CN=admin", "user-x" ]` |
| `url` (opa/keycloak) | Policy/authz endpoint | `https://opa:8181/...` |
| `clientId`, `tokenEndpointUri` (keycloak) | Keycloak client wiring | strings |

### 2.7 `template` — customizing generated K8s objects

`template` lets you patch labels/annotations/spec of the objects Strimzi generates. Common sub-objects:

| Sub-object | Customizes | Notable fields |
|---|---|---|
| `statefulset` / `podSet` | The broker workload (StrimziPodSet in modern versions; StatefulSet historically) | `metadata.{labels,annotations}` |
| `pod` | Broker pods | `metadata`, `imagePullSecrets`, `securityContext`, `terminationGracePeriodSeconds`, `affinity` (`nodeAffinity`, `podAffinity`, `podAntiAffinity`), `tolerations`, `topologySpreadConstraints` |
| `bootstrapService` / `brokersService` | The generated Services | labels/annotations (e.g. cloud LB annotations) |
| `externalBootstrapRoute` / `perPodRoute` / `...Ingress` | OpenShift Routes / Ingresses for external listeners | host/annotations |
| `persistentVolumeClaim` | The PVCs | labels/annotations |
| `podDisruptionBudget` | PDB for rolling ops | `maxUnavailable` |
| `kafkaContainer` / `initContainer` | The broker & init containers | `env`, `securityContext`, `volumeMounts` |
| `serviceAccount` | The pod's ServiceAccount | labels/annotations |
| `clusterRoleBinding` | RBAC binding (e.g. for rack awareness) | labels/annotations |

> Use `podAntiAffinity` + `rack.topologyKey` to spread brokers across AZs; use `podDisruptionBudget.maxUnavailable` to control rolling updates.

---

## 3. `Kafka` spec siblings (peers of `spec.kafka`)

| Field | Meaning | Example / type | Required? |
|---|---|---|---|
| `zookeeper` | **Legacy** ZooKeeper ensemble config: `replicas`, `storage`, `resources`, `jvmOptions`, `template`, `logging`, `config`. **Omitted/removed in KRaft mode** and dropped entirely in the newest Strimzi. | `{ replicas: 3, storage: {...} }` | required (ZK mode) / absent (KRaft) |
| `entityOperator` | Deploys the Topic + User operators as a sidecar deployment | see below | optional (needed for `KafkaTopic`/`KafkaUser`) |
| `entityOperator.topicOperator` | Enables Topic Operator (watches `KafkaTopic`). `reconciliationIntervalSeconds`, `watchedNamespace`, `resources` | `{}` = defaults on | optional |
| `entityOperator.userOperator` | Enables User Operator (watches `KafkaUser`) | `{}` | optional |
| `clusterCa` | Cluster CA cert lifecycle (broker↔broker, operator↔broker) | see fields below | optional |
| `clientsCa` | Clients CA cert lifecycle (for `KafkaUser` mTLS certs) | see fields below | optional |
| `cruiseControl` | Deploy Cruise Control for rebalancing (`KafkaRebalance` CRs); `brokerCapacity`, `config`, `resources` | object | optional |
| `jmxTrans` | **Deprecated/removed** — old JMXTrans metrics exporter. Use `metricsConfig` (Prometheus) instead. | object | deprecated |
| `kafkaExporter` | Deploy Kafka Exporter (consumer-lag & topic/partition metrics for Prometheus/Grafana); `topicRegex`, `groupRegex`, `resources` | object | optional |
| `maintenanceTimeWindows` | Cron windows during which cert renewal / maintenance rolls are allowed | `[ "* * 8-10 * * ?" ]` (list of Quartz cron) | optional |

**`clusterCa` / `clientsCa` shared fields:**

| Field | Meaning | Example |
|---|---|---|
| `generateCertificateAuthority` | `true` = Strimzi self-manages the CA; `false` = you provide your own CA in a Secret | `true` (bool) |
| `validityDays` | CA cert validity | `365` (int) |
| `renewalDays` | Days before expiry to start renewal | `30` (int) |
| `certificateExpirationPolicy` | On renewal: `renew-certificate` vs `replace-key` | `renew-certificate` |

---

## 4. `Kafka` → `status.*` (operator-written, read-only)

You never set these; the operator reports them. Read via `kubectl get kafka <name> -o yaml`.

| Field | Meaning | Example / type |
|---|---|---|
| `conditions[]` | Standard K8s conditions (`Ready`, `Warning`, `NotReady`) with `type/status/reason/message/lastTransitionTime` | list |
| `observedGeneration` | The `metadata.generation` the operator last reconciled (lag = not yet reconciled) | `7` (int) |
| `listeners[]` | Resolved addresses per listener: `name`, `bootstrapServers`, `addresses[]`, `certificates` — this is where you read the actual bootstrap host:port | list |
| `kafkaNodePools[]` | Node pools associated with this cluster | list of `{name}` |
| `registeredNodeIds[]` | Node IDs currently registered in the cluster metadata | `[0,1,2]` |
| `clusterId` | Kafka cluster UUID | `abcd-...` (string) |
| `operatorLastSuccessfulVersion` | Strimzi operator version that last successfully reconciled | `0.49.1` |
| `kafkaVersion` | Running Kafka version | `3.7.0` |
| `kafkaMetadataVersion` | Active KRaft metadata version | `3.7-IV2` |
| `kafkaMetadataState` | Where the cluster sits on the ZooKeeper→KRaft journey (see states below) | `KRaft` |
| `autoRebalance` | Status of auto-rebalance (Cruise-Control-driven) on scale-up/down, incl. `state` and affected node pools | object |

### `kafkaMetadataState` — the KRaft migration states (in order)

| State | Meaning |
|---|---|
| `ZooKeeper` | Cluster runs on ZooKeeper (pre-migration / legacy). |
| `KRaftMigration` | KRaft controllers up; metadata + brokers being migrated. Some brokers KRaft, some still ZK. |
| `KRaftDualWriting` | Brokers + controllers connected to ZooKeeper; KRaft controllers also write metadata *to* ZooKeeper (dual write). |
| `KRaftPostMigration` | Brokers run KRaft and are disconnected from ZK; controllers still write to ZK but are ready to disconnect. **Last state where rollback is possible.** |
| `PreKRaft` | Controllers disconnected from ZK; ZooKeeper ready to be removed. |
| `KRaft` | Migration finalized — brokers + controllers fully KRaft; ZooKeeper gone. |

> Driven by the `strimzi.io/kraft` annotation on the `Kafka` CR: `migration` → advance to the rollback-safe point; `enabled` → finalize (no rollback after); `rollback`/`disabled` for reverting.

---

## 5. `KafkaNodePool` (KRaft — how you declare nodes in modern Strimzi)

A node pool is a group of Kafka nodes with a shared role/storage. Enabled by the `strimzi.io/node-pools: enabled` annotation on the `Kafka` CR; the pool is linked via `strimzi.io/cluster` label.

| Field | Meaning | Example / type | Required? |
|---|---|---|---|
| `metadata.labels."strimzi.io/cluster"` | Which `Kafka` CR this pool belongs to | `my-cluster` | required |
| `spec.roles` | Node roles: `controller`, `broker`, or both (combined nodes) | `[ broker, controller ]` or `[ broker ]` | required (KRaft) |
| `spec.replicas` | Number of nodes in this pool | `3` (int) | required |
| `spec.storage` | Same schema as `spec.kafka.storage` (`ephemeral` / `persistent-claim` / `jbod`) | `{ type: persistent-claim, size: 100Gi, class: ..., deleteClaim: false }` | required |
| `spec.resources` / `jvmOptions` / `template` | Per-pool overrides (else inherit cluster) | objects | optional |

> Typical prod split: a `controllers` pool (`roles: [controller]`, replicas 3) + a `brokers` pool (`roles: [broker]`, replicas ≥3). Dev often uses one pool with combined `[broker, controller]`.

---

## 6. `KafkaConnect` → `spec.*`

| Field | Meaning | Example / type | Required? |
|---|---|---|---|
| `version` | Kafka/Connect version (must match the image) | `3.7.0` | optional |
| `replicas` | Connect worker pods (stateless Deployment) | `3` | optional |
| `image` | Connect image — must contain the Debezium plugins if you build them in | `<registry>/connect:0.49.1-kafka-3.7.0-debezium1.9.7` | optional (if not using `build`) |
| `bootstrapServers` | Broker bootstrap the workers connect to | `my-cluster-kafka-bootstrap:9093` | **required** |
| `config` | Connect worker config (see keys below) | map | recommended |
| `tls` | TLS to brokers: `trustedCertificates[]` (secretName + certificate) | object | optional |
| `authentication` | Worker→broker auth: `type: tls` / `scram-sha-512` / `oauth`, with secret refs | object | optional |
| `build` | Let Strimzi build the Connect image: `output` (registry/image) + `plugins[]` (each `name` + `artifacts[]` of type `tgz`/`jar`/`zip`/`maven` with `url`/`sha512sum`) | object | optional (alt to prebuilt `image`) |
| `resources` / `jvmOptions` / `logging` / `metricsConfig` / `template` | Same semantics as broker equivalents | objects | optional |
| `externalConfiguration` | Mount Secrets/ConfigMaps as env/volumes (feeds `${secrets:...}` in connectors) | object | optional |

**`config` common keys:**

| Key | Meaning | Example |
|---|---|---|
| `group.id` | Connect cluster group id (unique per Connect cluster) | `connect-cluster` |
| `config.storage.topic` | Internal topic storing connector **configs** | `connect-cluster-configs` |
| `offset.storage.topic` | Internal topic storing source connector **offsets** (CDC resume position) | `connect-cluster-offsets` |
| `status.storage.topic` | Internal topic storing connector/task **status** | `connect-cluster-status` |
| `config.storage.replication.factor` | RF of the config topic | `3` |
| `offset.storage.replication.factor` | RF of the offset topic | `3` |
| `status.storage.replication.factor` | RF of the status topic | `3` |
| `key.converter` / `value.converter` | Default converters | `org.apache.kafka.connect.json.JsonConverter` |

**Annotation `strimzi.io/use-connector-resources: "true"`** (on `metadata.annotations`): tells this Connect cluster to be driven by `KafkaConnector` **CRs** instead of the REST API. Without it, your `KafkaConnector` CRs are ignored.

---

## 7. `KafkaConnector` → `spec.*`  (this is where Debezium lives)

| Field | Meaning | Example / type | Required? |
|---|---|---|---|
| `metadata.labels."strimzi.io/cluster"` | Which `KafkaConnect` runtime hosts this connector | `my-connect` | **required** |
| `class` | Connector implementation class | `io.debezium.connector.oracle.OracleConnector` | required |
| `tasksMax` | Max tasks. **Debezium source connectors = 1** (single log reader). | `1` (int) | optional |
| `config` | Connector-specific settings (the Debezium keys — §7.1/§7.2) | map | required |
| `pause` | (Older field) pause the connector | `true` (bool) | optional |
| `state` | Preferred state: `running` / `paused` / `stopped` (`stopped` frees the task slot; newer, replaces `pause`) | `running` | optional |
| `autoRestart` | Auto-restart failed connector/tasks: `{ enabled: true, maxRestarts: N }` | object | optional |
| `transforms` | Single Message Transforms chain (comma-list of names + per-name `transforms.<n>.*`) | see §7.3 | optional |

### 7.1 Debezium **Oracle** 1.9.x config keys

| Key | Meaning | Example | Required? |
|---|---|---|---|
| `connector.class` | (= `spec.class`) | `io.debezium.connector.oracle.OracleConnector` | required |
| `database.hostname` | Oracle host | `<host>` | required |
| `database.port` | Listener port | `"1521"` | required |
| `database.user` | CDC user | `<cdc_user>` | required |
| `database.password` | Password (inject via secret, not inline) | `${secrets:ns/db-secret:password}` | required |
| `database.dbname` | CDB name or SID | `<CDB_or_SID>` | required |
| `database.pdb.name` | Pluggable DB name (multitenant/CDB only) | `<PDB>` | optional |
| `database.connection.adapter` | `logminer` (default in 1.9) or `xstream` | `logminer` | optional |
| **`database.server.name`** | **Logical name → topic prefix.** Topics become `<server-name>.<schema>.<table>`. **⚠ 1.9 key — renamed to `topic.prefix` in Debezium 2.x.** | `myserver` | required |
| **`database.history.kafka.bootstrap.servers`** | Broker(s) for the **schema history** topic. **⚠ 1.9 key — renamed to `schema.history.internal.kafka.bootstrap.servers` in 2.x.** | `my-cluster-kafka-bootstrap:9092` | required |
| **`database.history.kafka.topic`** | Name of the schema history topic (DDL log; must persist). **⚠ 1.9 key — `schema.history.internal.kafka.topic` in 2.x.** | `schema-history.myserver` | required |
| `table.include.list` | Schema-qualified tables to capture (most-edited field) | `SCHEMA.TABLE_A,SCHEMA.TABLE_B` | optional (else all) |
| `schema.include.list` | Restrict to schemas | `SCHEMA` | optional |
| `snapshot.mode` | `initial` (snapshot + stream) · `schema_only` (no data snapshot) · `never` · `initial_only` | `initial` | optional |

**Oracle DBA prereqs:** archivelog mode ON; supplemental logging (`ALTER DATABASE ADD SUPPLEMENTAL LOG DATA;` + per captured table); LogMiner privileges for the CDC user.

### 7.2 Debezium **SQL Server** 1.9.x config keys

| Key | Meaning | Example | Required? |
|---|---|---|---|
| `connector.class` | | `io.debezium.connector.sqlserver.SqlServerConnector` | required |
| `database.hostname` | SQL Server host | `<host>` | required |
| `database.port` | Port | `"1433"` | required |
| `database.user` / `database.password` | CDC credentials | `<cdc_user>` / `${secrets:...}` | required |
| `database.names` | DB(s) to capture — **1.9 supports multiple** (older single-db used `database.dbname`) | `<DB1>,<DB2>` | required |
| **`database.server.name`** | Logical name → topic prefix. **⚠ `topic.prefix` in 2.x.** | `myserver` | required |
| **`database.history.kafka.bootstrap.servers`** | Schema history brokers. **⚠ `schema.history.internal.*` in 2.x.** | `my-cluster-kafka-bootstrap:9092` | required |
| **`database.history.kafka.topic`** | Schema history topic. **⚠ `schema.history.internal.*` in 2.x.** | `schema-history.myserver` | required |
| `table.include.list` | Tables to capture | `dbo.TABLE_A,dbo.TABLE_B` | optional |
| `snapshot.mode` | `initial` · `schema_only` · `initial_only` | `initial` | optional |

**SQL Server prereqs:** SQL Server **Agent running**; CDC enabled at DB (`sys.sp_cdc_enable_db`) and per table (`sys.sp_cdc_enable_table`).

### 7.3 `transforms` (Single Message Transforms) — common with Debezium

| Key | Meaning | Example |
|---|---|---|
| `transforms` | Comma list of transform names (order matters) | `unwrap` |
| `transforms.<n>.type` | The SMT class | `io.debezium.transforms.ExtractNewRecordState` (flatten CDC envelope → row) |
| `transforms.<n>.*` | Per-transform options | `transforms.route.regex`, `...replacement` for `RegexRouter` |

---

## 8. `KafkaTopic` → `spec.*`

| Field | Meaning | Example / type | Required? |
|---|---|---|---|
| `metadata.labels."strimzi.io/cluster"` | Owning Kafka cluster | `my-cluster` | required |
| `spec.topicName` | Actual Kafka topic name (defaults to `metadata.name`; use when the topic name isn't a valid K8s name) | `my.topic.name` | optional |
| `spec.partitions` | Partition count (can increase, not decrease) | `12` (int) | optional (default 1) |
| `spec.replicas` | Replication factor | `3` (int) | optional (default from cluster) |
| `spec.config.retention.ms` | Retention time in ms | `"604800000"` (7d) | optional |
| `spec.config.cleanup.policy` | `delete` (time/size retention) or `compact` (keep latest per key) or `compact,delete` | `delete` | optional |
| `spec.config.segment.bytes` | Segment size | `"1073741824"` | optional |
| `spec.config.min.insync.replicas` | Per-topic min ISR | `"2"` | optional |

> Note: `config` values here are strings. Bidirectional vs unidirectional Topic Operator mode changed across Strimzi versions — in unidirectional mode the CR is source of truth.

---

## 9. `KafkaUser` → `spec.*`

| Field | Meaning | Example / type | Required? |
|---|---|---|---|
| `metadata.labels."strimzi.io/cluster"` | Owning Kafka cluster | `my-cluster` | required |
| `spec.authentication.type` | `tls` (mTLS cert) · `tls-external` · `scram-sha-512` (password) | `scram-sha-512` | required |
| `spec.authorization.type` | `simple` (ACL authorizer) | `simple` | optional |
| `spec.authorization.acls[]` | ACL rules (see below) | list | optional |
| `spec.quotas` | Per-user quotas: `producerByteRate`, `consumerByteRate`, `requestPercentage`, `controllerMutationRate` | `{ consumerByteRate: 1048576 }` | optional |

**`acls[]` sub-fields:**

| Field | Meaning | Example |
|---|---|---|
| `resource.type` | `topic` · `group` · `cluster` · `transactionalId` | `topic` |
| `resource.name` | Resource name (or prefix stem) | `myserver.` |
| `resource.patternType` | `literal` (exact) or `prefix` | `prefix` |
| `operations` | Allowed ops: `Read`, `Write`, `Describe`, `Create`, `Delete`, `Alter`, `DescribeConfigs`, `AlterConfigs`, `ClusterAction`, `IdempotentWrite`, `All` | `[ Read, Describe ]` |
| `host` | Restrict by client host | `*` |
| `type` | `allow` (default) or `deny` | `allow` |

> The User Operator materializes a `KafkaUser` into a Kafka principal **and** a K8s Secret holding the cert (mTLS) or password (SCRAM) that the client (e.g. a Databricks consumer) mounts to authenticate.

---

## Debezium 1.9.x → 2.x key renames (the ones that bite)

| Concept | **1.9.x (use these)** | 2.x (do NOT use on 1.9) |
|---|---|---|
| Topic prefix / logical name | `database.server.name` | `topic.prefix` |
| Schema history brokers | `database.history.kafka.bootstrap.servers` | `schema.history.internal.kafka.bootstrap.servers` |
| Schema history topic | `database.history.kafka.topic` | `schema.history.internal.kafka.topic` |

Since Debezium here is **1.9.7.Final**, always use the left column.
