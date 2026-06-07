# Engineering Practices — Stack Comparison (Data Engineering Perspective)

> **เอกสารนี้เปรียบเทียบ CloudRun vs Dataflow จากมุม Data Engineering**
> ไม่ใช่จากมุม App Development — เพราะงาน data pipeline ≠ งาน API service

---

## ปัญหาของ Comparison เดิม

Comparison เดิมวัดจาก **App Development metrics**:
- Modularity Score, Write Code Score → วัดความง่ายในการเขียน code
- Unit Runtime, Integration Runtime → วัดความเร็ว test
- Pipeline stages, Total Runtime → วัดความเร็ว CI/CD
- Dependencies count → วัด attack surface

**สิ่งที่ขาดหายไปทั้งหมด = สิ่งที่สำคัญที่สุดสำหรับ data**:
- Data correctness (data ถูกต้องไหม?)
- Data completeness (data ครบไหม?)
- Data freshness (data ทันเวลาไหม?)
- Operational resilience (deploy แล้ว data หายไหม?)
- Scale capability (รับ data ขนาดใหญ่ได้ไหม?)

> **ถ้าวัดช่างซ่อมรถด้วย KPI ของเชฟ — ช่างย่อมแพ้เสมอ**
> Dataflow ไม่ได้แย่ — มันแค่ถูกวัดด้วย metrics ที่ไม่ใช่ของมัน

---

## 1. Stack Comparison — Data Engineering Metrics

### 1.1 Data Correctness & Reliability

| Metric | Dataflow / Python | CloudRun / Python | CloudRun / TypeScript | EKS / Kotlin |
|--------|:-:|:-:|:-:|:-:|
| **Exactly-once delivery** | ✅ Built-in (Beam) | ❌ None | ❌ None | ❌ None |
| **Exactly-once score** | **5** | **0** | **0** | **0** |
| **CDC UPSERT support** | ✅ BQ Storage Write API | ⚠️ Manual DML | ⚠️ Manual DML | ⚠️ Manual DML |
| **CDC DELETE support** | ✅ mutation_type: DELETE | ❌ Must build | ❌ Must build | ❌ Must build |
| **CDC score** | **5** | **1** | **1** | **1** |
| **Deduplication** | ✅ Beam.Distinct() + per-bundle | ❌ DB-level only | ❌ DB-level only | ❌ DB-level only |
| **Dedup score** | **5** | **1** | **1** | **1** |
| **Data loss on deploy** | ✅ Drain (0 loss) | ❌ Kill (data lost) | ❌ Kill (data lost) | ⚠️ Rolling (partial) |
| **Deploy safety score** | **5** | **0** | **0** | **3** |
| **Idempotent writes** | ✅ Primary key + atomic bundle | ❌ Must build | ❌ Must build | ❌ Must build |
| **Idempotency score** | **5** | **1** | **1** | **1** |
| **TOTAL CORRECTNESS** | **5.0** | **0.6** | **0.6** | **1.2** |

### 1.2 Streaming Capability

| Metric | Dataflow / Python | CloudRun / Python | CloudRun / TypeScript | EKS / Kotlin |
|--------|:-:|:-:|:-:|:-:|
| **Kafka streaming** | ✅ ReadFromKafka (cross-lang) | ⚠️ kafka-python (manual) | ⚠️ kafkajs (manual) | ⚠️ Spring Kafka |
| **Kafka score** | **5** | **2** | **2** | **3** |
| **Windowing** | ✅ FixedWindows + triggers | ❌ None | ❌ None | ❌ None |
| **Window score** | **5** | **0** | **0** | **0** |
| **Watermarks** | ✅ Event time tracking | ❌ None | ❌ None | ❌ None |
| **Watermark score** | **5** | **0** | **0** | **0** |
| **Backpressure** | ✅ Automatic source throttle | ❌ None (OOM risk) | ❌ None (OOM risk) | ⚠️ Manual |
| **Backpressure score** | **5** | **0** | **0** | **2** |
| **Late data handling** | ✅ Configurable | ❌ None | ❌ None | ❌ None |
| **Late data score** | **5** | **0** | **0** | **0** |
| **TOTAL STREAMING** | **5.0** | **0.4** | **0.4** | **1.0** |

### 1.3 Data Processing Scale

| Metric | Dataflow / Python | CloudRun / Python | CloudRun / TypeScript | EKS / Kotlin |
|--------|:-:|:-:|:-:|:-:|
| **Max throughput** | 10K+ records/sec (autoscale) | ~100 records/req | ~100 records/req | ~1K records/sec |
| **Throughput score** | **5** | **1** | **1** | **3** |
| **Parallel BQ read** | ✅ ReadFromBigQuery (Storage API) | ❌ REST API only | ❌ REST API only | ⚠️ JDBC |
| **BQ read score** | **5** | **1** | **1** | **2** |
| **Iceberg write** | ✅ managed.Write (Java SDK) | ❌ PyIceberg (limited) | ❌ No TS library | ❌ Kotlin limited |
| **Iceberg score** | **5** | **2** | **0** | **1** |
| **Fan-out (1→N tables)** | ✅ PCollection branching | ❌ Sequential writes | ❌ Sequential writes | ⚠️ Manual threads |
| **Fan-out score** | **5** | **1** | **1** | **2** |
| **Initial data load (M records)** | ✅ Parallel workers | ❌ Single container (timeout) | ❌ Single container (timeout) | ⚠️ Limited |
| **Init load score** | **5** | **1** | **1** | **2** |
| **TOTAL SCALE** | **5.0** | **1.2** | **0.8** | **2.0** |

### 1.4 Operational Resilience

| Metric | Dataflow / Python | CloudRun / Python | CloudRun / TypeScript | EKS / Kotlin |
|--------|:-:|:-:|:-:|:-:|
| **Graceful shutdown** | ✅ Drain + flush | ❌ SIGTERM only | ❌ SIGTERM only | ⚠️ Graceful pod shutdown |
| **Shutdown score** | **5** | **1** | **1** | **3** |
| **In-place update** | ✅ --update flag | ❌ Redeploy = restart | ❌ Redeploy = restart | ⚠️ Rolling update |
| **Update score** | **5** | **0** | **0** | **3** |
| **State recovery** | ✅ Kafka offset preserved | ❌ Manual replay | ❌ Manual replay | ⚠️ Consumer group |
| **Recovery score** | **5** | **1** | **1** | **3** |
| **Pipeline-level metrics** | ✅ Beam Metrics aggregated | ❌ Per-container only | ❌ Per-container only | ⚠️ Custom metrics |
| **Metrics score** | **5** | **1** | **1** | **3** |
| **Autoscale workers** | ✅ 0→N workers (data-driven) | ⚠️ 0→N instances (request-driven) | ⚠️ 0→N instances | ✅ HPA |
| **Autoscale score** | **5** | **2** | **2** | **4** |
| **TOTAL OPERATIONS** | **5.0** | **1.0** | **1.0** | **3.2** |

### 1.5 Data Governance

| Metric | Dataflow / Python | CloudRun / Python | CloudRun / TypeScript | EKS / Kotlin |
|--------|:-:|:-:|:-:|:-:|
| **Schema enforcement** | ✅ RowTypeConstraint (compile time) | ⚠️ Runtime only | ⚠️ Runtime only | ⚠️ Runtime only |
| **Schema score** | **5** | **2** | **2** | **2** |
| **Lineage tracking** | ✅ Dataplex auto-capture (Dataflow) | ❌ Not captured | ❌ Not captured | ❌ Not captured |
| **Lineage score** | **5** | **0** | **0** | **0** |
| **DLQ (Dead Letter Queue)** | ✅ TaggedOutput → separate PCollection | ❌ Must build | ❌ Must build | ❌ Must build |
| **DLQ score** | **5** | **1** | **1** | **1** |
| **TOTAL GOVERNANCE** | **5.0** | **1.0** | **1.0** | **1.0** |

---

## 2. Overall Comparison (All Perspectives)

| Category | Weight | Dataflow | CloudRun/Py | CloudRun/TS | EKS/Kotlin |
|----------|--------|:--------:|:-----------:|:-----------:|:----------:|
| **Data Correctness** | 30% | **5.0** | 0.6 | 0.6 | 1.2 |
| **Streaming** | 20% | **5.0** | 0.4 | 0.4 | 1.0 |
| **Scale** | 15% | **5.0** | 1.2 | 0.8 | 2.0 |
| **Operations** | 15% | **5.0** | 1.0 | 1.0 | 3.2 |
| **Governance** | 10% | **5.0** | 1.0 | 1.0 | 1.0 |
| Developer Experience | 5% | 2.5 | **5.0** | **5.0** | 4.3 |
| CI/CD Speed | 5% | 2.0 | **5.0** | **5.0** | 4.6 |
| **WEIGHTED TOTAL** | 100% | **4.85** | **0.97** | **0.89** | **1.73** |

> **หมายเหตุ**: Weight กำหนดตาม priority ของ enterprise data platform
> - Data correctness = สำคัญสุด (ผิดแล้วกระทบ business + compliance)
> - Developer experience = สำคัญน้อยสุด (ทำครั้งเดียว, data ต้องถูกต้องทุกวัน)

---

## 3. Comparison เดิม vs ใหม่

| Metric ที่เดิมวัด | Dataflow | CloudRun | ทำไม metric นี้ misleading สำหรับ data |
|-------------------|:--------:|:--------:|---------------------------------------|
| Modularity: 1.9 vs 5.0 | 1.9 | **5.0** | Beam pipeline = declarative DAG — ไม่ต้อง modular แบบ app (แต่ code จริงก็ใช้ hexagonal อยู่แล้ว) |
| Write Code: 3.2 vs 5.0 | 3.2 | **5.0** | Beam DoFn ต้อง boilerplate — แลกกับ exactly-once + parallelism ฟรี |
| Unit Test: 1s vs 1s | 1 | 1 | เท่ากัน — ไม่ใช่ differentiator |
| Integration Test: 1000s vs 1s | 1000 | **1** | Dataflow integration test = **test pipeline จริง** (Beam TestPipeline) — CloudRun test = **test HTTP endpoint** (ไม่ได้ test data processing) |
| Pipeline Runtime: 40m vs 10m | 40 | **10** | Dataflow build ช้ากว่าเพราะ bundle Beam SDK + Flex Template — **build ช้า 30 นาที vs data หาย 100% ทุก deploy** |
| Deploy downtime: 15m vs 0m | 15 | **0** | Dataflow 15m = **drain** (process in-flight data) — CloudRun 0m = **kill** (data lost) — **0 downtime ≠ 0 data loss** |
| Dependencies: 686 vs 218 | 686 | **218** | Beam SDK = Google-maintained framework — จำนวน deps ไม่ = security risk (เหมือน Spring Boot มี deps เยอะแต่ไม่อันตราย) |

### สิ่งที่เดิมไม่วัด (แต่สำคัญที่สุด)

| Metric ที่ไม่ได้วัด | Dataflow | CloudRun | Impact |
|---------------------|:--------:|:--------:|--------|
| Data loss on deploy | **0%** | **100% of in-flight** | ข้อมูลลูกค้าหาย ทุกครั้งที่ deploy |
| Exactly-once guarantee | **Yes** | **No** | ข้อมูลซ้ำ/หาย ใน production |
| Streaming capability | **Native** | **None** | ไม่สามารถทำ real-time ได้จริง |
| CDC support | **Native** | **None** | ข้อมูลเก่าค้าง ลบไม่ได้ |
| Iceberg write | **Managed** | **Manual** | 6-12 weeks rewrite |
| Backpressure | **Automatic** | **None** | OOM crash ตอน traffic spike |
| Pipeline lineage | **Auto-capture** | **None** | Dataplex ไม่เห็น CloudRun |

---

## 4. Detailed Scoring Breakdown — Data Engineering Aspects

### 4.1 Data Correctness

| Aspect | Metric | Description | Dataflow | score | CloudRun/Py | score | CloudRun/TS | score | EKS/Kotlin | score |
|--------|--------|-------------|----------|-------|-------------|-------|-------------|-------|------------|-------|
| | Exactly-once semantics | Messages processed exactly once | Built-in | **5** | None | **0** | None | **0** | None | **0** |
| | CDC UPSERT | Atomic row-level updates | BQ Storage Write API | **5** | Manual DML | **1** | Manual DML | **1** | Manual DML | **1** |
| | CDC DELETE | Row-level deletes with safety | 3-layer safety | **5** | Must build from scratch | **0** | Must build from scratch | **0** | Must build from scratch | **0** |
| | Deduplication (windowed) | Remove duplicates across time windows | Beam.Distinct() | **5** | No windowing | **0** | No windowing | **0** | No windowing | **0** |
| | Deduplication (per-bundle) | Remove duplicates within batch | DoFn start_bundle | **5** | Must implement | **2** | Must implement | **2** | Must implement | **2** |
| | Idempotent writes | Safe retry without duplicates | Bundle atomicity | **5** | Must implement | **1** | Must implement | **1** | Must implement | **1** |
| | Data loss on deploy | Data preserved during deployment | Drain → flush → commit | **5** | Kill container | **0** | Kill container | **0** | Rolling update | **3** |
| | **Total Score** | | | **5.0** | | **0.6** | | **0.6** | | **1.0** |

### 4.2 Operational Resilience

| Aspect | Metric | Description | Dataflow | score | CloudRun/Py | score | CloudRun/TS | score | EKS/Kotlin | score |
|--------|--------|-------------|----------|-------|-------------|-------|-------------|-------|------------|-------|
| | Graceful drain | Process in-flight before shutdown | gcloud drain | **5** | SIGTERM (10s) | **1** | SIGTERM (10s) | **1** | preStop hook | **3** |
| | In-place update | Update without restarting | --update flag | **5** | Redeploy = restart | **0** | Redeploy = restart | **0** | Rolling update | **3** |
| | State recovery | Resume from failure | Kafka offset + window state | **5** | Must replay manually | **1** | Must replay manually | **1** | Consumer group | **3** |
| | Metrics aggregation | Cross-worker metric visibility | Beam Metrics API | **5** | Per-container only | **1** | Per-container only | **1** | Custom | **3** |
| | Autoscaling (data-driven) | Scale based on data volume | Worker pool autoscale | **5** | Request-based scale | **2** | Request-based scale | **2** | HPA | **4** |
| | Worker startup monitoring | Know when pipeline is healthy | CurrentVcpuCount metric | **5** | Container health check | **3** | Container health check | **3** | Pod ready | **4** |
| | Incompatible update detection | Smart fallback on failure | Graph compatibility check | **5** | None | **0** | None | **0** | None | **0** |
| | **Total Score** | | | **5.0** | | **1.1** | | **1.1** | | **2.9** |

### 4.3 Enterprise Data Operations

| Aspect | Metric | Description | Dataflow | score | CloudRun/Py | score | CloudRun/TS | score | EKS/Kotlin | score |
|--------|--------|-------------|----------|-------|-------------|-------|-------------|-------|------------|-------|
| | Initial data load (millions) | Bulk load large dataset | Parallel ReadFromBQ | **5** | Single container timeout | **1** | Single container timeout | **1** | JDBC limited | **2** |
| | Schema evolution | Handle schema changes safely | Iceberg REST catalog | **5** | Manual migration | **1** | Manual migration | **1** | Manual | **1** |
| | Partition management | Auto-create data partitions | managed.Write auto-partition | **5** | Manual | **1** | Manual | **1** | Manual | **1** |
| | Cross-language transforms | Use Java + Python together | Beam cross-lang SDK | **5** | Single language | **0** | Single language | **0** | Single language | **0** |
| | GCP service integration | Dataplex lineage, BQ native | Full integration | **5** | No Dataplex lineage | **1** | No Dataplex lineage | **1** | No GCP native | **1** |
| | Managed Iceberg writes | Atomic Iceberg commits with batching | managed.Write (300s trigger) | **5** | PyIceberg (no batching) | **2** | No TS library | **0** | Limited | **1** |
| | **Total Score** | | | **5.0** | | **1.0** | | **0.7** | | **1.0** |

---

## 5. Cost Comparison (Production Estimate)

### Scenario: Loyalty Data Pipeline (3 collectors, streaming + batch)

| Cost Factor | Dataflow | CloudRun | Notes |
|-------------|----------|----------|-------|
| **Streaming compute** (24/7) | ~$150/mo (1 worker n1-std-2) | ~$200/mo (min 1 instance + Kafka lib) | CloudRun ต้อง always-on สำหรับ Kafka |
| **Batch compute** (2 jobs/day) | ~$5/mo (1 worker × 5 min × 2) | ~$3/mo (on-demand) | Batch: CloudRun ถูกกว่าเล็กน้อย |
| **GCS operations** (Iceberg) | ~$2/mo (1 commit/5min) | ~$200/mo (1 commit/request) | CloudRun ไม่มี batching → 100x more commits |
| **BLMS API calls** | ~$1/mo (batched) | ~$50/mo (per-record) | No batching = more API calls |
| **Engineering effort** (build equivalent) | $0 (built-in) | **$200K-400K** (40-80 weeks × dev cost) | One-time cost to reinvent Dataflow features |
| **Incident cost** (data loss/corruption) | ~$0 (exactly-once) | **$?? per incident** | Each incident = investigation + replay + business impact |
| **TOTAL (monthly)** | **~$158/mo** | **~$453/mo + risk** | Before counting engineering effort |

---

## 6. "But CloudRun is simpler!" — Addressing Common Arguments

| Argument | Reality |
|----------|---------|
| "CloudRun code is simpler" | Simpler **to write** ≠ simpler **to operate**. Data pipeline complexity ไม่ได้อยู่ที่ code — อยู่ที่ data correctness, exactly-once, backpressure. CloudRun "ซ่อน" complexity ไว้ = ต้อง build เองภายหลัง |
| "CloudRun deploys faster" | Deploy เร็ว 30 นาที แต่ **data หายทุกครั้ง**. Dataflow drain 15 นาที = 0 data loss. ถ้า deploy สัปดาห์ละ 2 ครั้ง: 30 min saved vs data lost × 104 times/year |
| "CloudRun มี fewer dependencies" | Beam SDK = **Google-maintained framework** เหมือน Spring Boot. จำนวน deps ไม่ = risk. Beam SDK มี 686 deps เพราะมันรวม Kafka connector, Iceberg connector, BQ connector ไว้ในตัว — CloudRun ต้อง install ทีละตัวเอง |
| "CloudRun unit tests เร็วกว่า" | Integration test ของ Dataflow ช้าเพราะ **test data pipeline จริง** (Beam TestPipeline, windowing, triggers). CloudRun integration test เร็วเพราะ **ไม่ได้ test data processing** — test แค่ HTTP endpoint |
| "Modularity score ต่ำ" | Beam pipeline เป็น **declarative DAG** — ไม่ต้อง modular แบบ app. แต่ code จริงของเราก็ใช้ hexagonal architecture อยู่แล้ว (domain/ adapters/ application/) — modularity score 1.9 วัดจากอะไร? |
| "CloudRun scale ง่ายกว่า" | Scale **instances** ง่าย ≠ scale **data processing**. CloudRun scale = more HTTP handlers. Dataflow scale = more parallel data workers with backpressure. ใส่ Kafka stream ให้ CloudRun 10,000 msg/sec → OOM crash |
| "ทีมอื่นใช้ CloudRun ได้" | ทีมอื่นทำ **API service** (request-response). เราทำ **data pipeline** (streaming, batch, CDC). คนละงาน คนละ tool. ไม่มีใครใช้ CloudRun ทำ streaming Kafka consumer ใน production |

---

## 7. What Google Cloud Recommends

### Google Cloud Decision Tree (Official Documentation)

```
"Is your workload..."

Stateless HTTP/gRPC service?     → Cloud Run ✅
Event-driven function?           → Cloud Functions
Container-based microservice?    → Cloud Run / GKE
Stream processing?               → Dataflow ✅ (NOT Cloud Run)
Batch ETL?                       → Dataflow ✅ (NOT Cloud Run)
ML training?                     → Vertex AI
Data transformation (SQL)?       → Dataform ✅
Interactive analytics?           → BigQuery
```

**Source**: [Choosing a compute option](https://cloud.google.com/docs/choosing-a-compute-option)

> Google เองก็ไม่แนะนำให้ใช้ CloudRun สำหรับ stream processing หรือ batch ETL

---

## 8. Evidence from Our Codebase

### Features Currently Using Dataflow-Specific Capabilities

| Feature | File | Dataflow Capability | CloudRun Alternative |
|---------|------|---------------------|---------------------|
| Kafka streaming | `builder.py:272` | ReadFromKafka (cross-lang Java) | kafka-python (no cross-lang, no windowing) |
| 60-second windows | `builder.py:304-310` | FixedWindows + AfterWatermark trigger | ❌ ต้อง implement เอง |
| Fan-out (1→4 tables) | `builder.py:365-450` | PCollection branching + ParDo | Sequential writes (4x slower) |
| CDC DELETE | `api_dofns.py:275-320` | 3-layer safety + BQ Storage Write | Manual DML DELETE (no safety) |
| Beam Metrics | `api_dofns.py:41-43` | Counters aggregated across workers | Per-container (no aggregation) |
| Iceberg managed write | `iceberg_sink.py:28-82` | managed.Write(ICEBERG) | PyIceberg (no buffering, no trigger) |
| BLMS REST catalog | `blms_catalog_config.py` | Vended credentials (auto OAuth) | Manual OAuth token exchange |
| Init data load (M rows) | `builder.py:521-654` | Parallel ReadFromBigQuery | REST API (timeout, no parallel) |
| Drain on deploy | `deploy_dataflow.sh:396` | gcloud dataflow drain | SIGTERM → data lost |
| Smart update | `deploy_dataflow.sh:372` | --update (graph compatible) | ❌ Always restart |
| Worker metrics | `deploy_dataflow.sh:258` | CurrentVcpuCount API | ❌ No equivalent |
| Per-bundle dedup | `api_dofns.py:186-203` | start_bundle() lifecycle | ❌ No bundle concept |
| Schema enforcement | `iceberg_writer.py:59` | RowTypeConstraint (compile time) | Runtime only |
| Buffered writes | `base.yaml:25-28` | triggering_frequency_secs: 300 | Per-request write (no buffer) |

> **14 features** ที่ใช้ Dataflow-specific capabilities — ทั้งหมดต้อง rewrite ถ้าย้ายไป CloudRun

---

## 9. Risk Ownership Statement

> **ถ้าตัดสินใจใช้ CloudRun สำหรับ data pipeline ผู้ตัดสินใจต้องรับผิดชอบ:**
>
> 1. **Data loss** ทุกครั้งที่ deploy (ไม่มี drain mechanism)
> 2. **Duplicate data** ใน production (ไม่มี exactly-once)
> 3. **OOM crashes** เมื่อ traffic spike (ไม่มี backpressure)
> 4. **CDC failures** — stale data ค้างใน BQ (ไม่มี native CDC)
> 5. **40-80 weeks engineering effort** เพื่อ reinvent สิ่งที่ Dataflow ให้ฟรี
> 6. **Compliance risk** — data ไม่ถูกต้อง ส่งผลกระทบต่อ business decisions
> 7. **No Dataplex lineage** — governance blind spot
>
> เหล่านี้ไม่ใช่ theoretical risks — เป็น **guaranteed outcomes** จากการใช้ tool ผิด use case

---

## References

### Google Cloud Official Documentation
- [Choosing a compute option](https://cloud.google.com/docs/choosing-a-compute-option) — Decision tree showing Dataflow for ETL/streaming
- [Dataflow: What is Dataflow](https://cloud.google.com/dataflow/docs/overview) — "Unified stream and batch data processing"
- [Cloud Run: What is Cloud Run](https://cloud.google.com/run/docs/overview/what-is-cloud-run) — "Stateless containers invoked via requests"
- [Dataflow exactly-once](https://cloud.google.com/dataflow/docs/concepts/exactly-once) — Built-in exactly-once guarantee
- [BQ Storage Write API CDC](https://cloud.google.com/bigquery/docs/change-data-capture) — CDC via Storage Write API (Dataflow integration)

### Apache Beam Documentation
- [Beam Programming Model](https://beam.apache.org/documentation/programming-guide/) — Windowing, triggers, watermarks
- [Beam Exactly-Once](https://beam.apache.org/documentation/runtime/model/) — Runner guarantees
- [Managed IcebergIO](https://beam.apache.org/documentation/io/built-in/iceberg/) — Cross-language Iceberg support

### Codebase Evidence
- `members-collector/src/application/pipeline/builder.py` — Streaming pipeline with windowing + fan-out
- `members-collector/src/application/pipeline/api_dofns.py` — CDC DELETE + Beam Metrics
- `members-collector/src/adapters/output/iceberg_sink.py` — Managed Iceberg Write
- `scripts/deploy_dataflow.sh` — Drain + update + smart fallback
- `members-collector/config/base.yaml` — Buffering + trigger configuration
