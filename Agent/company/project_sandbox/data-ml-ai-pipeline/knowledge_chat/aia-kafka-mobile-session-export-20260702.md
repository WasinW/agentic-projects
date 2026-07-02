# AIA Kafka/Strimzi Discussion — Mobile Session Export

> **For:** สิน (วศิน) — Senior Data Engineer at AIA (started 2026-07-01)
> **Session:** Mobile Claude chat, continuation from VS Code session
> **Purpose:** Portable brain-dump so VS Code chat can pick up where mobile left off
> **Context source:** Started from `aia-kafka-event-processing-GUIDE-export.md` uploaded from VS Code
> **Date:** 2026-07-02
> **Note:** All discussion was concept + architecture reasoning. NO AIA code was shared or requested (policy compliance).

---

## 📋 Session Overview

สินอัปโหลด onboarding doc จาก VS Code session ก่อนหน้า และคุยต่อบนมือถือขณะเดินทาง เนื้อหาที่คุยครอบคลุม:

1. **Confirm context understanding** — ผม (Claude) ยอมรับว่า mental model ก่อนหน้าผิด (AWS → จริงๆ Azure)
2. **Update Sin's context** — policy ห้าม export code, scope งาน 2 อัน, สิ่งที่ยัง confused
3. **Layer decomposition** — AKS vs K8s vs Strimzi vs Debezium (3 layers)
4. **Debezium location clarification** — อยู่บน Kafka Connect cluster (ไม่ใช่ Kafka broker cluster)
5. **Strimzi operators explained** — 4 operators + reconciliation loop concept

---

## 🎯 Context Corrections (สำคัญที่สุด)

### ผมยอมรับ mental model ผิดก่อนหน้านี้:

| ก่อน (ผิด) | จริง |
|---|---|
| Databricks บน AWS | **Azure Databricks** |
| MSK, Kinesis, MWAA | **Azure Databricks + AKS + ADF + ACR** |
| CI = GitHub Actions/CodePipeline | **Jenkins** |
| Git = GitHub | **Bitbucket** (org `aia-th`) |
| ชื่อ Sin | **วศิน** (เรียก สิน / ศิน / sin ก็ได้ ไม่มี 's) |
| Sin ทำ Databricks streaming | จริงๆ ดูแล **Producer side (Debezium CDC)** |

### Policy สำคัญที่ต้องเคารพ:

> **สินไม่สามารถ export code หรือ data จาก AIA** — traditional insurance company policy กลัวข้อมูลรั่ว + กลัวโดนฟ้อง เพราะ AI ไม่รับผิดชอบ ต้องมี user คุมอีกที
> 
> **ต่างจาก The1** ที่เป็น new platform เปิดได้บ้าง หรือโปรเจ็คส่วนตัว
> 
> **ผลต่อ Claude:** Reason from architecture + screenshots + describe ล้วนๆ ไม่ขอให้ paste code ไม่ generate ที่แอบอ้างว่าเป็น AIA code

### สิน's 2 goals (long-term):

1. **สร้าง Kafka cluster ต่อได้เอง** — ถ้ามี new source → set up ingestion (producer side) ได้จบ
2. **Refactor to make simpler** — ปรับ existing platform ให้ใช้ง่ายขึ้น
   - แต่ต้องเข้าใจ current setup ก่อน (จึงเริ่มจากคำถามเรื่อง AKS + Kafka cluster)

Consumer side (Databricks) = สินเก่งอยู่แล้ว ไม่ใช่โจทย์หลัก

---

## 🏗️ Discussion 1: AKS vs Kubernetes vs Strimzi vs Debezium

### The 3-Layer Model

ก่อนหน้านี้สินสับสน 4 คำนี้ พอมองเป็น 3 layer ก็เคลียร์:

```
┌────────────────────────────────────────────┐
│  Layer 1: INFRASTRUCTURE                    │
│  AKS = Azure Kubernetes Service              │  ← ตัว "เครื่อง"
│  (managed K8s cluster by Azure)              │
└──────────────────┬─────────────────────────┘
                   │ ทำงานด้วย
                   ▼
┌────────────────────────────────────────────┐
│  Layer 2: ORCHESTRATION                     │
│  Kubernetes + Strimzi operator               │  ← "ผู้จัดการ"
│  (K8s = generic; Strimzi = Kafka specialist)│
└──────────────────┬─────────────────────────┘
                   │ สร้าง+ดูแล
                   ▼
┌────────────────────────────────────────────┐
│  Layer 3: APPLICATION                       │
│  Kafka brokers + Kafka Connect + Debezium    │  ← "งานจริง"
└────────────────────────────────────────────┘
```

### Layer 1: AKS (Azure Kubernetes Service)

**คืออะไร:** Managed K8s cluster ของ Azure (VM pool + control plane สำเร็จรูป)

**Key points:**
- ไม่ใช่ code สินเขียน — infrastructure ที่มีอยู่แล้ว
- Azure จัดหาให้พร้อมใช้ (คล้าย managed Databricks workspace)
- สินได้ kubectl access → apply YAML เข้าไป

**Analogy:**
| Sin's world | AKS |
|---|---|
| Azure Databricks Workspace | AKS Cluster |
| Azure จัดหา Spark cluster ให้ | Azure จัดหา K8s cluster ให้ |
| สินแค่ submit notebook/job | สินแค่ apply YAML |

**Cloud equivalents:**
- AWS: **EKS** (Elastic Kubernetes Service)
- GCP: **GKE** (Google Kubernetes Engine)
- Azure: **AKS** ← AIA ใช้ตัวนี้

### Layer 2: Kubernetes (K8s)

**คืออะไร:** Container orchestrator — รัน containers และดูแลให้ยังอยู่

**Analogy สำคัญ:**
| Sin's world | K8s |
|---|---|
| Airflow orchestrates DAG tasks | K8s orchestrates containers |
| Task = 1 unit of work | Pod = 1 container instance |
| Airflow's scheduler restarts failed tasks | K8s restarts failed pods |
| DAG = declarative (YAML/Python) | K8s resources = declarative (YAML) |

**5 concepts ที่พอ:**

| Concept | คืออะไร | Analogy |
|---|---|---|
| **Pod** | 1 container instance | 1 Spark executor |
| **StatefulSet** | หลาย pods มี identity คงที่ (pod-0/1/2) | HDFS namenodes ที่ต้องมี identity ตายตัว |
| **Service** | Network endpoint ให้ pods คุยกัน | LB ที่ route ไป Kafka broker port 9092 |
| **PVC (Persistent Volume Claim)** | Storage แนบกับ pod (survives restart) | Delta table location on ADLS |
| **Namespace** | Isolation boundary | Databricks catalog/schema |

**Declarative vs Imperative (key mindset):**

```
Imperative (แบบเก่า):
  "รัน install.sh → สร้าง VM → install Kafka"
  → ถ้า VM ล่ม = พังทั้งระบบ

Declarative (K8s):
  YAML: "ฉันต้องการ Kafka broker 3 ตัว, storage 100GB, port 9092"
  → K8s: "OK รับทราบ" → make it happen → ดูแลให้อยู่ตลอด
  → ถ้า broker ล่ม → K8s สร้างใหม่ auto ตาม YAML
```

### Layer 3: Strimzi + Debezium

จะอธิบายละเอียดใน section ถัดไป

---

## 🎯 Discussion 2: Debezium อยู่บน Kafka Cluster ที่ AKS ป่ะ?

### สินถาม: "Debezium อยู่บน Kafka cluster ที่เราสร้างบน AKS ป่ะ"

### คำตอบ: ใช่บน AKS แต่ **ไม่ใช่บน Kafka cluster (broker cluster) โดยตรง**

### แยก 3 clusters บน AKS เดียว:

```
                    AKS (Azure Kubernetes Service)
                    ═════════════════════════════
                    
    ┌─────────────────┐   ┌──────────────────┐   ┌──────────────────┐
    │  Strimzi        │   │  Kafka Cluster   │   │  Kafka Connect   │
    │  Operator       │   │  (brokers)       │   │  Cluster         │
    │                 │   │                  │   │  (workers)       │
    │  (1 pod)        │   │  broker-0        │   │  connect-0       │
    │  Watch CRs +    │   │  broker-1        │   │  connect-1       │
    │  reconcile      │   │  broker-2        │   │                  │
    │                 │   │  (StatefulSet)   │   │  (Deployment)    │
    └────────┬────────┘   └────────┬─────────┘   └────────┬─────────┘
             │                     │                       │
             │ manages both        │                       │
             ├─────────────────────┴───────────────────────┘
             │
             │ inside Connect pods, Debezium plugins loaded:
             ▼
    ┌─────────────────────────────────────────────────────┐
    │  Debezium connectors (running as plugins in Connect) │
    │                                                       │
    │  ┌───────────────┐  ┌───────────────┐  ┌──────────┐ │
    │  │ cmic-oracle   │  │ bbl360-sql    │  │ autopay  │ │
    │  │ (Oracle CDC)  │  │ (SqlServer CDC)│  │ (Oracle) │ │
    │  └───────┬───────┘  └───────┬───────┘  └────┬─────┘ │
    │          │                  │                │       │
    └──────────┼──────────────────┼────────────────┼───────┘
               │                  │                │
               ▼                  ▼                ▼
          Oracle DB          SQL Server DB    Oracle DB
          (cmic)             (bbl360)         (autopay)
                                                                
    ทั้ง Kafka Connect → ส่ง events → Kafka Cluster brokers → topics
```

### 2 Clusters แยก (สำคัญ)

**Kafka Cluster (Broker Cluster)**
- Kind: `Kafka` (CRD)
- หน้าที่: เก็บ + ส่ง messages ในรูป topics
- Pods: kafka broker pods (StatefulSet — identity คงที่)
- Storage: PVC (Azure Disk) เก็บ log segments
- สร้างโดย: apply `Kafka` CR ใน `dtp_kafka_cluster` repo

**Kafka Connect Cluster**
- Kind: `KafkaConnect` (CRD)
- หน้าที่: runtime process โฮสต์ connectors (Debezium)
- Pods: connect worker pods (Deployment ปกติ)
- Image: custom image จาก ACR (Strimzi base + Debezium plugins + AIA custom jars)
- สร้างโดย: apply `KafkaConnect` CR น่าจะอยู่ที่ `dtp_kafka_connector/connect/`

**ทั้ง 2 คนละ pod-set กัน — แต่คุยกันผ่าน K8s internal network**

### Debezium อยู่ตรงไหนกันแน่?

**Debezium ไม่ใช่ container/pod แยก** — เป็น **plugin (JAR files) โหลดใน Kafka Connect image**

```
Kafka Connect Image (Docker image ใน ACR)
    │
    ├── Base image: Strimzi Kafka Connect runtime
    ├── + Debezium Oracle connector plugin (JAR)
    ├── + Debezium SQL Server connector plugin (JAR)
    ├── + Debezium PostgreSQL connector plugin (JAR)
    └── + Custom TimestampConsumer jar (AIA built)
    
    ↑ นี่คือที่ dtp_kafka_build_ci สร้าง image
```

**เมื่อ Kafka Connect pod start:**
1. โหลด base runtime
2. Scan `/plugins/` → เจอ Debezium JARs
3. Register connector classes (เช่น `io.debezium.connector.oracle.OracleConnector`)
4. Ready รับ `KafkaConnector` CRs

**เมื่อ apply `KafkaConnector` CR:**
- ระบุ `class: io.debezium.connector.oracle.OracleConnector`
- Strimzi + Connect runtime → instantiate connector instance
- Connector เริ่ม read Oracle log → publish to topic

### Component Type Comparison

| Component | Type | Pod? | Sin's Analogy |
|---|---|---|---|
| **AKS** | Infrastructure | (host all pods) | Azure Databricks workspace |
| **Strimzi operator** | Controller | 1 pod | DLT engine |
| **Kafka cluster** | Broker cluster | 3+ pods (StatefulSet) | HDFS namenode + datanodes |
| **Kafka Connect cluster** | Connector runtime | 2+ pods (Deployment) | Spark cluster |
| **Debezium** | Plugin (JAR) | ❌ ไม่มี pod แยก | Library ที่ import ใน Spark job |
| **KafkaConnector CR** | Config/spec | ❌ Just YAML | Spark job submission |

### ทำไม Kafka Connect ต้องแยก cluster จาก Kafka?

**Design principle:**
- **Kafka brokers** = high-throughput I/O, storage-heavy → StatefulSet + PVC
- **Kafka Connect workers** = CPU/memory-heavy processing, stateless → Deployment
- Scale ไม่เหมือนกัน → แยก cluster
- Restart independent → Connect ล่มไม่กระทบ broker
- Update image independent → upgrade Debezium plugin ไม่กระทบ Kafka data

**เหมือน Spark Driver แยกจาก HDFS Datanode** — คนละ concern

### Updated Mental Model:

```
เดิม:   AKS → Kafka cluster (มี Debezium อยู่ในนั้น) [WRONG]

ใหม่:   AKS
         ├── Strimzi operator (จัดการทุกอย่าง)
         ├── Kafka cluster (brokers เก็บ topics)
         └── Kafka Connect cluster (Debezium plugins วิ่งในนี้)
                └── connects to → Kafka cluster via network
```

---

## 🎯 Discussion 3: Strimzi คืออะไร + Operators มีอะไรบ้าง

### Strimzi คืออะไร (สั้นๆ)

**Open-source project เอา Kafka มารันบน Kubernetes ผ่าน operator pattern**

- Home: strimzi.io
- Governance: CNCF sandbox project
- Built by: Red Hat + community

### ทำไมต้องมี Strimzi?

**ก่อน Strimzi** → deploy Kafka บน K8s ต้องเขียน:
- StatefulSet YAML เอง (broker pods)
- PVC config (storage)
- Service (networking)
- Certs (TLS)
- Manage upgrades manually
- ZooKeeper/KRaft config
- = **1000+ บรรทัด YAML + shell scripts ต่อ cluster**

**หลัง Strimzi** → เขียน YAML แค่ ~20 บรรทัด:
```yaml
kind: Kafka
spec:
  kafka:
    replicas: 3
    storage: 100Gi
```
Strimzi จัดการที่เหลือหมด

### Operator Pattern (Foundation Concept)

**สำคัญที่ต้องเข้าใจก่อนจะเข้าใจ Strimzi operators**

```
Operator = โปรแกรม 1 ตัว ที่:
  1. รันอยู่ใน K8s cluster (เหมือน pod อื่นๆ)
  2. Watch K8s API ตลอดเวลา
     ("มี CR ประเภทที่ฉันดูแลเกิดขึ้นมั้ย?")
  3. เมื่อเห็น CR ใหม่ → อ่าน spec → สร้าง real resources ให้ตรง
  4. Watch state ต่อไปเรื่อยๆ → ถ้าจริงไม่ตรง spec → แก้ให้ตรง
  5. Loop ไปเรื่อยๆ ตลอดชีวิต
```

### Reconciliation Loop (หัวใจของ operator)

```
┌────────────────────────────────────────┐
│  Loop ทุก N วินาที (ปกติ 30s):        │
│                                        │
│  1. Observe:                           │
│     "Desired state คืออะไร?"          │
│     → อ่าน CR YAML                    │
│                                        │
│  2. Analyze:                           │
│     "Actual state คืออะไร?"           │
│     → check pods, services, PVCs       │
│                                        │
│  3. Act:                               │
│     Desired ≠ Actual?                  │
│     → create/update/delete resources   │
│                                        │
│  4. Report:                            │
│     Update CR status field             │
│                                        │
└────────────────────────────────────────┘
```

### Analogy ใกล้ตัวสิน:

**Databricks DLT engine ทำงานเหมือน operator:**

| DLT | K8s Operator |
|---|---|
| อ่าน `@dlt.table` decorators | อ่าน CR YAML |
| สร้าง Spark jobs | สร้าง pods |
| Monitor pipeline health | Monitor pod health |
| Auto-restart on failure | Auto-restart on failure |
| Update table properties → refresh | Update CR → reconcile |

**Airflow scheduler ก็คล้าย:**
- Scan DAGs directory → create task instances
- Operator scan CRs → create real resources

---

## 🔧 Strimzi's 4 Operators

```
┌──────────────────────────────────────────────────────────┐
│  Strimzi Operators (4 ตัว)                                │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌───────────────────┐                                   │
│  │ 1. Cluster        │  ← หัวหน้าใหญ่                     │
│  │    Operator       │     สร้าง/จัดการ Kafka clusters    │
│  └────────┬──────────┘                                   │
│           │ spawns +                                     │
│           │ manages                                      │
│           ▼                                              │
│  ┌───────────────────┐  ┌────────────────────┐          │
│  │ 2. Topic          │  │ 3. User            │          │
│  │    Operator       │  │    Operator        │          │
│  │  (topics)         │  │  (users + ACLs)    │          │
│  └───────────────────┘  └────────────────────┘          │
│                                                          │
│  ┌───────────────────┐                                   │
│  │ 4. Drain Cleaner  │  ← ตัวเสริม (optional)            │
│  │  (K8s eviction)   │                                   │
│  └───────────────────┘                                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 1️⃣ Cluster Operator (หัวหน้าใหญ่)

**หน้าที่:** สร้างและจัดการ Kafka clusters + Kafka Connect clusters + อื่นๆ

**CRs ที่ดูแล:**

| CR Kind | Creates |
|---|---|
| `Kafka` | Kafka cluster (brokers + storage) |
| `KafkaConnect` | Kafka Connect cluster (workers) |
| `KafkaMirrorMaker2` | Cross-cluster mirror |
| `KafkaBridge` | HTTP-to-Kafka bridge |
| `KafkaRebalance` | Cruise Control rebalance requests |

**สิ่งที่มันสร้าง เมื่อ apply `Kafka` CR:**

```
Cluster Operator สร้าง:
  ├── StatefulSet (Kafka broker pods)
  ├── Services (client + internal)
  ├── PVCs (Azure Disk)
  ├── ConfigMaps (Kafka config)
  ├── Secrets (TLS certs)
  ├── ZooKeeper StatefulSet (ถ้ายังไม่ KRaft)
  ├── Topic Operator deployment  ← spawn sub-operator
  ├── User Operator deployment   ← spawn sub-operator
  └── NetworkPolicy
```

**= 1 CR (~20 บรรทัด) → 30+ K8s resources จริง**

**Analogy:** เหมือน Airflow scheduler ที่สร้าง executors + workers + workflows ทั้งชุด

**AIA repo location:** `dtp_kafka_cluster/install/<version>/cluster-operator/`

### 2️⃣ Topic Operator (ผู้ดูแล topics)

**หน้าที่:** Sync ระหว่าง `KafkaTopic` CRs กับ topics จริงใน Kafka

**CR ที่ดูแล:**
```yaml
kind: KafkaTopic
metadata:
  name: transactions
  labels:
    strimzi.io/cluster: my-kafka-cluster
spec:
  partitions: 12
  replicas: 3
  config:
    retention.ms: 604800000
    cleanup.policy: delete
```

**ทำงานยังไง:**

```
สิน apply KafkaTopic YAML
    ↓
Topic Operator เห็น
    ↓
เช็ค: topic นี้มีอยู่ใน Kafka หรือยัง?
    ├── ไม่มี → create topic (ผ่าน Kafka Admin API)
    ├── มีแล้ว config ตรง → skip
    └── มีแล้วแต่ config ต่าง → alter topic
```

**2 Modes:**
- **Unidirectional (แนะนำ)** — YAML → Kafka only, source of truth = CR
- **Bidirectional (deprecated)** — 2-way sync, มี edge cases

**Strimzi 0.36+ default = Unidirectional**

**Analogy:** เหมือน dbt ที่ sync `.sql` files กับ tables ใน warehouse

**AIA repo location:** `dtp_kafka_cluster/install/<version>/topic-operator/`

### 3️⃣ User Operator (ผู้ดูแล users + ACLs)

**หน้าที่:** Sync `KafkaUser` CRs กับ users จริงใน Kafka + สร้าง K8s Secret ที่มี credentials

**CR ที่ดูแล:**
```yaml
kind: KafkaUser
metadata:
  name: databricks-consumer
  labels:
    strimzi.io/cluster: my-kafka-cluster
spec:
  authentication:
    type: scram-sha-512   # หรือ tls
  authorization:
    type: simple
    acls:
      - resource:
          type: topic
          name: transactions
        operations: [Read, Describe]
      - resource:
          type: group
          name: databricks-consumer-group
        operations: [Read]
```

**ทำงานยังไง:**
1. สร้าง Kafka user + ACLs (ผ่าน Kafka Admin API)
2. สร้าง K8s Secret ที่มี credentials (username + password/cert)
3. Consumer app (Databricks) mount Secret เพื่อ authenticate

**Analogy:** เหมือน AWS IAM (create user + generate access keys + attach policy)

**AIA repo location:** `dtp_kafka_cluster/install/<version>/user-operator/`

### 4️⃣ Drain Cleaner (Optional Helper)

**หน้าที่:** จัดการเมื่อ K8s ต้อง evict Kafka pods (เช่น node maintenance)

**ปัญหาที่แก้:**
```
Scenario:
  K8s admin ต้อง maintain node
  → K8s: "ขอ evict pods บน node นี้"
  → ถ้า Kafka broker ถูก evict แบบไม่ระวัง = data loss เสี่ยง

Drain Cleaner:
  → intercept eviction request
  → ให้ Strimzi rolling restart อย่างระวัง 
    (respect partition leaders)
  → migrate leadership ก่อน pod down
  → ป้องกัน data loss
```

**Implementation:** ไม่มี CR โดยตรง — เป็น **admission webhook** intercept K8s eviction API

**AIA repo location:** `dtp_kafka_cluster/install/<version>/drain-cleaner/`

---

## 📊 Operators Summary Table

| Operator | ดูแล CRs | จัดการอะไร | AIA repo location |
|---|---|---|---|
| **Cluster** | `Kafka`, `KafkaConnect`, `KafkaMirrorMaker2`, `KafkaBridge`, `KafkaRebalance` | สร้าง clusters, brokers, Connect workers | `install/<ver>/cluster-operator/` |
| **Topic** | `KafkaTopic` | Sync topics + configs | `install/<ver>/topic-operator/` |
| **User** | `KafkaUser` | Users + ACLs + credentials Secrets | `install/<ver>/user-operator/` |
| **Drain Cleaner** | (webhook) | Safe pod eviction | `install/<ver>/drain-cleaner/` |

### Analogy Recap:

```
Cluster Operator     ↔ Databricks admin (create workspaces/clusters)
Topic Operator       ↔ dbt (sync .sql files to warehouse tables)
User Operator        ↔ IAM (create users, generate keys, attach policies)
Drain Cleaner        ↔ Kubernetes drain hook (safe shutdown)
```

---

## 🚦 Complete Deployment Sequence (ลำดับทำงานทั้งหมด)

```
Time 0: Empty AKS cluster
        ↓
Time 1: apply install/<ver>/cluster-operator/
        → Cluster Operator pod running
        → CRDs registered (K8s รู้จัก kind: Kafka)
        ↓
Time 2: apply install/<ver>/topic-operator/, user-operator/, drain-cleaner/
        → All operators running (ยังไม่มีอะไรให้ดูแล)
        ↓
Time 3: apply Kafka CR (dtp_kafka_cluster/<Kafka.yaml>)
        → Cluster Operator เห็น → สร้าง Kafka brokers
        → Kafka cluster ready
        ↓
Time 4: apply KafkaTopic CRs
        → Topic Operator เห็น → สร้าง topics
        ↓
Time 5: apply KafkaUser CRs
        → User Operator เห็น → สร้าง users + Secrets
        ↓
Time 6: apply KafkaConnect CR (dtp_kafka_connector/connect/)
        → Cluster Operator เห็น → สร้าง Connect workers
        ↓
Time 7: apply KafkaConnector CRs (dtp_kafka_connector/connector-*)
        → Connect runtime เห็น → start Debezium connectors
        ↓
Time 8: Databricks consumes topics ← Sin's strength
```

**7 steps → complete platform at AIA**

---

## 📂 Repo → Layer Mapping (Consolidated)

```
┌──────────────────────────────────────────────────────────────┐
│  Repo 1: dtp_kafka_build_ci                                  │
│  Purpose: Build Docker images                                 │
│                                                               │
│  What it contains:                                            │
│    - Dockerfiles (custom Kafka Connect image)                │
│    - Jenkinsfiles สำหรับ build                                │
│    - "Images Release version" README                          │
│                                                               │
│  What Jenkins does:                                           │
│    docker build → docker push → ACR                           │
│                                                               │
│  ⚠️ NOTHING deploys to K8s from here                          │
│  ⚠️ Just an image factory                                     │
└──────────────────────────────────────────────────────────────┘
                          │
                          │ ACR image tags referenced ↓
                          ▼
┌──────────────────────────────────────────────────────────────┐
│  Repo 2: dtp_kafka_cluster                                   │
│  Purpose: Deploy Strimzi + Kafka cluster                      │
│                                                               │
│  What it contains:                                            │
│    - install/<version>/                                       │
│        ├── cluster-operator/  ← Strimzi operator itself      │
│        ├── topic-operator/    ← sub-operator                  │
│        ├── user-operator/     ← sub-operator                  │
│        └── drain-cleaner/                                     │
│    - Kafka cluster CR (kind: Kafka)                          │
│    - KafkaTopic CRs                                          │
│    - KafkaUser CRs                                           │
│    - cert/ (TLS certs)                                        │
│    - Grafana dashboards                                       │
│                                                               │
│  What Jenkins does:                                           │
│    kubectl/helm apply install/ → Strimzi operator running    │
│    kubectl apply Kafka CR → operator creates broker pods     │
└──────────────────────────────────────────────────────────────┘
                          │
                          │ Kafka runtime available ↓
                          ▼
┌──────────────────────────────────────────────────────────────┐
│  Repo 3: dtp_kafka_connector                                 │
│  Purpose: Deploy KafkaConnect + KafkaConnector CDCs           │
│                                                               │
│  What it contains:                                            │
│    - connect/                                                 │
│        └── KafkaConnect runtime CR (likely)                   │
│    - connector-{dev,uat,prod,dr}-main{,0.38,0.45,0.49.1}/    │
│        └── multiple YAMLs (one per source DB)                 │
│            each = kind: KafkaConnector                        │
│    - .jenkins/                                                │
│                                                               │
│  What Jenkins does:                                           │
│    kubectl apply KafkaConnect CR → runtime pods created      │
│    kubectl apply KafkaConnector CRs → Debezium starts        │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Insights ที่ได้จาก mobile session

### Insight 1: 3 Clusters แยกกันบน AKS
- **Strimzi operator cluster** (1 pod) — control plane
- **Kafka broker cluster** (StatefulSet) — data plane, storage
- **Kafka Connect cluster** (Deployment) — plugin runtime, stateless

### Insight 2: Debezium = Plugin ไม่ใช่ Cluster
- อยู่ในรูป JAR ที่โหลดตอน Connect pod start
- `KafkaConnector` CR = ตัว instantiate connector instance
- 1 YAML = 1 source system

### Insight 3: Reconciliation Loop = หัวใจ operator pattern
- Observe → Analyze → Act → Report → Loop
- ไม่มี "deploy script" ตัวใหญ่
- CR = "อยากให้เป็นแบบไหน"
- Operator = "ทำให้เป็นแบบนั้น + รักษาให้อยู่แบบนั้น"

### Insight 4: Strimzi ≠ Kafka distribution ใหม่
- ใช้ upstream Apache Kafka jar files
- Strimzi = K8s wrapper + operator + CRDs
- Kafka มาตรฐาน แต่ deploy ง่ายกว่า 100 เท่า

### Insight 5: สินไม่ต้อง touch Kafka jar files
- แค่เข้าใจ CRDs 5-6 อัน + K8s basics
- Debug ด้วย `kubectl` ไม่ใช่ trace code flow

---

## 🎯 Sin's Learning Priority (Next Steps)

### Phase 1: ทำความเข้าใจ layers ✅ DONE (จาก session นี้)
- AKS = infrastructure
- K8s = orchestrator
- Strimzi = Kafka operator
- Debezium = CDC plugin

### Phase 2: Hands-on กับ live cluster (สัปดาห์แรกที่ AIA)

Commands ที่จะใช้ (once ได้ kubectl access):

```bash
# ดู operators ที่รันอยู่
kubectl get deployment -n <namespace>
# → strimzi-cluster-operator, entity-operator (topic+user)

# ดู CRDs ที่ Strimzi register ไว้
kubectl get crds | grep strimzi
# → kafkas.kafka.strimzi.io, kafkatopics.kafka.strimzi.io, etc.

# ดู Kafka brokers
kubectl get statefulset -n <namespace>
kubectl get kafka -n <namespace>

# ดู Kafka Connect workers
kubectl get deployment -n <namespace> | grep connect
kubectl get kafkaconnect -n <namespace>

# ดู Debezium connectors (running instances)
kubectl get kafkaconnector -n <namespace>

# ดู Connect pod logs (เห็น Debezium plugins loaded)
kubectl logs <connect-pod-name> -n <namespace> | grep -i debezium

# ดู operator logs (debug)
kubectl logs -n <namespace> deployment/strimzi-cluster-operator

# Describe CR (เห็น current state vs desired)
kubectl describe kafka <name>
kubectl describe kafkaconnector <name>
```

### Phase 3: Follow existing patterns
- อ่าน 1-2 existing `KafkaConnector` YAMLs ใน Bitbucket (read-only, no export)
- เข้าใจ config fields ผ่าน architectural discussion
- Trace Jenkins pipeline ผ่าน Jenkins UI

### Phase 4: Add new source (Sin's goal #1)
- Clone pattern จาก existing connector
- Fill in new source DB config
- PR → review → Jenkins → deploy

### Phase 5: Refactor (Sin's goal #2)
- ต้องเข้าใจ full flow ก่อน
- 3-6 เดือนหลังทำงาน

---

## 💬 Sin's Open Questions (จาก mobile session + carry over)

### จาก doc เดิม (section 10) — ยังต้อง confirm กับทีม:
1. Real prod CD Jenkins jobs ต่อ repo คืออะไร?
2. Live Strimzi version ใน prod?
3. Deploy via `kubectl apply` หรือ `helm`? GitOps (ArgoCD/Flux)?
4. `Kafka` cluster CR structure — brokers, KRaft vs ZooKeeper, storage?
5. Promotion flow dev→uat→prod→dr?
6. sf360 migration = อะไร?
7. Databricks เป็น consumer เดียว หรือมี sink connectors ด้วย?
8. Schema Registry ใช้ (Avro/JSON, compatibility policy)?
9. First concrete task ของสิน?

### เพิ่มจาก mobile session:
10. kubectl read access ก่อน write access?
11. มี dev/sandbox cluster ให้ practice YAML?
12. `KafkaConnect` runtime CR อยู่ที่ `connect/` folder ใช่ไหม?

---

## 🎓 Topics ที่ยังไม่ได้เจาะลึกใน mobile session

Save for VS Code deep-dive:

1. **KafkaConnect runtime mechanics** — worker distribution, task rebalancing
2. **Debezium internals** — LogMiner, snapshot mode, offset tracking
3. **KafkaConnector YAML anatomy** — dissect field ทีละอัน สำหรับ Oracle + SQL Server
4. **CRD mechanics** — Strimzi extend K8s ยังไง
5. **kubectl cheat sheet** — 20 commands สำหรับ DE
6. **Operator pattern เชิงลึก** — reconciliation loop, event-driven, controller manager
7. **Strategy สร้าง Kafka cluster ใหม่** — checklist ครบชุด
8. **AIA-specific**: walk through repo structure จริง (ดู screenshots ที่มี)

---

## ⚠️ Reminder for VS Code Chat

**Policy สำคัญ:**
- ❌ ห้ามขอให้สิน paste AIA code
- ❌ ห้าม generate code อ้างว่าเป็น AIA
- ✅ Reason from architecture + screenshots ที่สิน describe
- ✅ ให้ self-check checklists
- ✅ Explain concepts ผ่าน analogy ที่สินคุ้น (Spark, Databricks, dbt, Airflow)

**สินยืนยัน:**
> "traditional insurance company กลัวข้อมูลรั่ว + กลัวโดนฟ้อง เพราะ AI ไม่รับผิดชอบ ต้องมี user คุมอีกที ต่างจาก The1 ที่เป็น new platform"

**สินแข็ง:**
- Azure Databricks + Structured Streaming (Consumer side — ไม่ใช่โจทย์หลัก)
- Spark/config-driven ETL framework
- DLT-like declarative thinking

**สิน weak (ต้อง focus):**
- Kubernetes basics
- Strimzi operators
- Debezium CDC
- Kafka Connect runtime
- Jenkins CD flow ที่ AIA
- ACR image lifecycle

**ชื่อ:** เรียก สิน / ศิน / sin ก็ได้ (ไม่ต้องมี 's — นั่นคือ possessive)

---

## 📋 Summary for VS Code Continuation

**Mobile session accomplished:**
- ✅ Corrected mental model (Azure not AWS)
- ✅ Explained AKS vs K8s vs Strimzi vs Debezium (3 layers)
- ✅ Clarified Debezium = plugin in Kafka Connect cluster (not on Kafka broker cluster)
- ✅ Explained Strimzi operator pattern + 4 operators
- ✅ Reconciliation loop concept
- ✅ Complete deployment sequence (7 steps)
- ✅ Repo-to-layer mapping
- ✅ Analogy bank (DLT, dbt, Airflow, IAM)

**Ready for VS Code deep dive:**
- Debezium internals (LogMiner, snapshot mode)
- KafkaConnect runtime mechanics
- kubectl hands-on cheat sheet
- Individual connector YAML anatomy
- Strategy for adding new source (Sin's goal #1)
- Path to refactoring (Sin's goal #2)

**Session ended:** สิน กลับถึงบ้าน จะต่อใน VS Code

---

**End of mobile session export — 2026-07-02**
