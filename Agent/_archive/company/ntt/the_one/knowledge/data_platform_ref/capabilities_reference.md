# Data Platform Capabilities — Reference Map

> เอกสารชุดที่ 2 — ต่อจาก Modern_Data_AI_Platform_Blueprint.md
> เน้นตอบคำถาม: **"feature ที่ไม่ใช่ pipeline หลัก เรียกว่าอะไร มีอะไรบ้าง ใช้ทำอะไร"**
> Last update: 2026-05

---

## 0. ก่อนอื่น — feature พวกนี้เรียกว่าอะไรกันแน่?

ในวงการเรียกหลายชื่อ ทั้งหมดความหมายใกล้เคียงกัน:

| ชื่อที่เรียก | ที่มา | นัยที่เน้น |
|---|---|---|
| **Cross-cutting Concerns** | Software Engineering | feature ที่ตัดผ่านทุก module |
| **Undercurrents** | Joe Reis & Matt Housley (Fundamentals of Data Engineering, 2022) | สิ่งที่ "ไหลใต้" ทุก stage ของ DE Lifecycle |
| **Platform Capabilities** | Enterprise Architecture | ความสามารถที่แพลตฟอร์มต้องมี |
| **Non-Functional Requirements (NFRs)** | Solution Architecture | requirement ที่ไม่ใช่ business logic |
| **Operational Features** | DevOps / SRE | feature ที่จำเป็นสำหรับการ operate ระบบ |
| **DataOps Practices** | DataOps community | practices ที่ทำให้ data pipeline reliable |

**คำที่ผมแนะนำให้ใช้ในงานจริง**: 
- **"Platform Capability"** — เวลาคุยกับ business / executive
- **"Undercurrent"** — เวลาคุย architecture / interview (ทำให้ดูรู้กรอบ Joe Reis)
- **"Cross-cutting Concern"** — เวลา code review / design review

---

## 1. Mental Model — แกน 2 มิติ

### มิติที่ 1: Pipeline Stages (สิ่งที่ pipeline ทำตามลำดับเวลา)

```
Generation → Ingestion → Storage → Transformation → Serving
```

### มิติที่ 2: Cross-cutting Capabilities (สิ่งที่ทุก stage ต้องมี)

Joe Reis เรียกว่า **6 Undercurrents** — มาตรฐานที่ใช้กันในวงการ:

```
                    Generation  Ingestion  Storage  Transform  Serving
─────────────────────────────────────────────────────────────────────
Security              ✓           ✓          ✓        ✓          ✓
Data Management       ✓           ✓          ✓        ✓          ✓
DataOps               ✓           ✓          ✓        ✓          ✓
Data Architecture     ✓           ✓          ✓        ✓          ✓
Orchestration         -           ✓          ✓        ✓          ✓
Software Engineering  -           ✓          ✓        ✓          ✓
```

### Visual Mental Model

```
        ┌────────────────────────────────────────────────────┐
        │              CONSUMPTION LAYER                     │
        │  BI / ML / API / GenAI / Reverse ETL / Submission  │
        └────────────────────────────────────────────────────┘
                                 ▲
        ┌────────────────────────────────────────────────────┐
        │       PIPELINE STAGES (ที่คนเห็นบ่อยๆ)              │
        │   Generate → Ingest → Store → Transform → Serve    │
        └────────────────────────────────────────────────────┘
                                 ▲
        ┌────────────────────────────────────────────────────┐
        │   PLATFORM CAPABILITIES (Cross-cutting)            │
        │  ┌──────────┬──────────┬──────────┬──────────┐    │
        │  │ Security │  DQ &    │ Observ-  │  Gov &   │    │
        │  │          │  Quality │  ability │  Catalog │    │
        │  ├──────────┼──────────┼──────────┼──────────┤    │
        │  │ DataOps  │  Self-   │  FinOps  │  Lineage │    │
        │  │          │  Service │          │          │    │
        │  └──────────┴──────────┴──────────┴──────────┘    │
        └────────────────────────────────────────────────────┘
                                 ▲
        ┌────────────────────────────────────────────────────┐
        │              INFRASTRUCTURE LAYER                  │
        │  Storage / Compute / Network / Identity            │
        └────────────────────────────────────────────────────┘
```

**สิ่งที่คุณคิดว่าเป็น "feature"** (audit log, DQ, validation, lineage, ฯลฯ) — มันคือ **Platform Capability layer** ที่ส่วนกลาง

---

## 2. The Complete Capability Map — 8 หมวด, 40+ Features

ผมจัดกลุ่มจาก practical ของวงการ + 6 Undercurrents ของ Joe Reis ให้ครบทุก feature ที่ enterprise ใช้กัน

### Group 1: Data Management & Governance

| # | Feature | ชื่ออื่นที่เรียก | What | Why |
|---|---|---|---|---|
| 1 | **Data Catalog** | Metadata Catalog | ทะเบียนข้อมูล search ได้ | คนหา dataset ไม่เจอ ทำงานซ้ำ |
| 2 | **Business Glossary** | Semantic Dictionary | นิยามคำธุรกิจ ("Active User") | ทุกคนใช้คำเดียวกันคนละนิยาม |
| 3 | **Data Lineage** | Lineage Graph | กราฟ source → consumer | impact analysis, debug |
| 4 | **Data Contracts** | Schema Contract | ข้อตกลง schema producer↔consumer | breaking change ที่ต้นทาง |
| 5 | **Data Stewardship** | Domain Ownership | คนรับผิดชอบ dataset | ใครคำตอบสุดท้ายเรื่องคุณภาพ |
| 6 | **Master Data Management (MDM)** | Golden Record | single source สำหรับ entity (Customer, Product) | duplicate / conflict resolution |
| 7 | **Reference Data** | Lookup / Code Master | ตาราง code มาตรฐาน (country code, currency) | consistent lookup ทุกระบบ |
| 8 | **Data Modeling** | Schema Design | star schema, data vault, dimensional modeling | structured analytics |

### Group 2: Data Quality & Validation

| # | Feature | What | Implementation Pattern | Tools |
|---|---|---|---|---|
| 9 | **Schema Validation** | Verify schema before ingest | JSON Schema / Avro / Protobuf | Confluent SR, Buf |
| 10 | **Data Quality Tests** | Run rules on data (null, range) | dbt tests, contract enforcement | dbt, Soda, GE |
| 11 | **Anomaly Detection** | ML detect unusual data | Statistical / ML-based | Monte Carlo, Anomalo |
| 12 | **Reconciliation** | Source vs target counts/sums match | Daily count match jobs | Custom + Soda |
| 13 | **Quarantine / DLQ** | Bad records → separate location | Dead-letter topic / DLQ table | Pub/Sub DLQ, Kafka DLQ |
| 14 | **Data Profiling** | Statistical summary of dataset | Auto-generate stats per column | dbt-profiler, GE |

#### 6 Data Quality Dimensions (มาตรฐาน DAMA + Industry)

```
1. ACCURACY      — ค่าตรงกับความจริง? (price ในระบบ = price ที่ขาย)
2. COMPLETENESS  — มีครบทุก record/field ที่ต้องการ?
3. CONSISTENCY   — ค่าเดียวกันในทุกระบบ?
4. TIMELINESS    — ข้อมูลทันต่อการใช้งาน?
5. UNIQUENESS    — ไม่มี duplicate?
6. VALIDITY      — รูปแบบถูกต้อง? (email format, phone digits)
```

**กฎการใช้งาน**: ไม่จำเป็นต้องวัดทุก dimension ทุก dataset — เลือกตาม business impact

### Group 3: Observability & Reliability

| # | Feature | What | Tools |
|---|---|---|---|
| 15 | **Pipeline Monitoring** | Job status, duration, throughput | Datadog, GCP Monitoring |
| 16 | **Data Observability** | 5 pillars (ดูถัดไป) | Monte Carlo, Bigeye, Acceldata |
| 17 | **Alerting** | Trigger on threshold/anomaly | PagerDuty, Slack |
| 18 | **SLA / SLO Tracking** | Measure delivery promise | Custom dashboards |
| 19 | **Audit Logging** | Who did what when | Cloud Audit Logs, GCP CAL |
| 20 | **Distributed Tracing** | Request flow across services | OpenTelemetry, Jaeger |
| 21 | **Cost / Usage Metrics** | Slot/DBU/credit usage | (FinOps section) |

#### 5 Pillars of Data Observability (Monte Carlo standard)

| Pillar | คำถามที่ตอบ | ตัวอย่าง alert |
|---|---|---|
| **Freshness** | ข้อมูลล่าสุดเมื่อไหร่? | "ตาราง orders ไม่มี data > 2 ชม." |
| **Volume** | จำนวน record ปกติหรือไม่? | "วันนี้ ingest แค่ 10K row จากปกติ 1M" |
| **Schema** | structure เปลี่ยนหรือไม่? | "Column phone หายจาก source A" |
| **Distribution** | ค่าอยู่ในช่วงคาดการณ์? | "average order value = -50 (เป็นลบ?)" |
| **Lineage** | ข้อมูลมาจากไหน? ใครใช้? | "Source X พัง = downstream 12 dashboards พัง" |

**Insight**: Pipeline Monitoring (#15) ตรวจ **ตัวระบบ** ส่วน Data Observability (#16) ตรวจ **ข้อมูล** — ต่างกัน, ต้องมีทั้งคู่

### Group 4: Security & Privacy

| # | Feature | What | Implementation |
|---|---|---|---|
| 22 | **Authentication** | Verify identity | OAuth, SAML, IAM |
| 23 | **Authorization (RBAC/ABAC)** | What can user do | Role-based / attribute-based |
| 24 | **Row-Level Security (RLS)** | กรอง row ตาม user | BQ Authorized Views, Unity Catalog |
| 25 | **Column-Level Security** | mask column ตาม role | BQ Policy Tags |
| 26 | **PII Detection** | scan + classify sensitive data | DLP API, Sensitive Data Protection |
| 27 | **Data Masking / Tokenization** | hash / replace ค่า PII | hash_sha256, format-preserving encryption |
| 28 | **Encryption at Rest** | encrypt files | KMS, CMEK |
| 29 | **Encryption in Transit** | TLS everywhere | Private Service Connect |
| 30 | **Secret Management** | API keys, passwords | Secret Manager, Vault |
| 31 | **Audit Trail** | log access + queries | BQ audit, CloudTrail |

### Group 5: DataOps / Pipeline Engineering

| # | Feature | What | Pattern |
|---|---|---|---|
| 32 | **Version Control** | Code + config in Git | mono-repo / multi-repo |
| 33 | **CI/CD for Data** | automated test + deploy | GitHub Actions, Cloud Build |
| 34 | **Pipeline Testing** | unit / integration / regression | pytest + Beam DirectRunner, dbt test |
| 35 | **Environment Management** | dev / staging / prod separation | Terraform workspaces |
| 36 | **Schema Migration** | evolve schema safely | Iceberg schema evolution, Liquibase |
| 37 | **Backfill / Replay** | rerun old data | Beam batch + watermark, dbt --full-refresh |
| 38 | **Idempotency** | run twice = same result | dedup keys, transactional writes |
| 39 | **Dependency Management** | DAG of jobs | Airflow, Dagster, Prefect |

### Group 6: FinOps / Cost Management

| # | Feature | What | Tools |
|---|---|---|---|
| 40 | **Cost Attribution** | tag every resource (team/product/env) | Mandatory labels |
| 41 | **Cost Observability** | dashboard ต่อ team/job/query | SELECT, Finout, Revefi |
| 42 | **Budget Alerts** | trigger when over X% budget | Cloud Billing alerts |
| 43 | **Resource Quotas** | hard limit per project | BQ slot reservation, K8s quota |
| 44 | **Workload Cost Analysis** | "query ไหนแพงสุด?" | Information schema queries |
| 45 | **Optimization Recommendations** | "ตารางนี้ควร partition" | Active Assist, Databricks Insights |

### Group 7: Self-Service & Productivity

| # | Feature | What | Why |
|---|---|---|---|
| 46 | **Pipeline Templates** | YAML/UI กรอกเสร็จได้ pipeline | onboard ภายใน 1 วัน |
| 47 | **Self-Service Portal** | Web UI สำหรับ domain teams | ลด ticket ถึง DE กลาง |
| 48 | **Data Discovery (Search)** | Google-like search ใน catalog | หา dataset ใน 30 วินาที |
| 49 | **Documentation Auto-gen** | docs จาก dbt / Iceberg metadata | ลด stale docs |
| 50 | **Notebook Environment** | shared Jupyter / Hex | exploration |

### Group 8: Outbound / Integration

| # | Feature | What | ตัวอย่างใช้ |
|---|---|---|---|
| 51 | **Submission / Outbound** | ส่งข้อมูลออก (เช่น regulator) | ส่งรายงาน BOT, IRS |
| 52 | **Reverse ETL** | warehouse → operational app | Sync customer score → Salesforce |
| 53 | **Data Sharing** | cross-org sharing | Snowflake Share, BQ Sharing |
| 54 | **API Layer** | expose data ผ่าน REST/GraphQL | Hasura, custom |
| 55 | **Pub/Sub Distribution** | broadcast events | Kafka topics, Pub/Sub |
| 56 | **File Drop** | export to SFTP/Email | regulatory, legacy partner |

---

## 3. Map กับสิ่งที่คุณเคยทำ (SCB Data-X / The-1)

### SCB Data-X — Framework ที่คุณเขียนมีอะไรเทียบกับ Capability Map?

```
fw_ingest_main      → covers: Schema Validation (#9), DLQ (#13), Audit Log (#19)
fw_transform_main   → covers: Data Quality Tests (#10), Idempotency (#38)
fw_validated_main   → covers: Reconciliation (#12), Data Profiling (#14)
fw_submission_main  → covers: Submission/Outbound (#51), File Drop (#56)
fw_outbound_main    → covers: Reverse ETL (#52), API Layer (#54)
```

**สิ่งที่ Data-X มีดี**: Group 5 (DataOps) + Group 8 (Outbound) ครบมาก เพราะ banking environment

**สิ่งที่ Data-X อาจขาด** (ขึ้นกับว่าได้แตะหรือเปล่า):
- ❓ Data Observability (5 pillars) — Pipeline monitoring มี แต่ data anomaly detection?
- ❓ Cost Attribution (FinOps) — รู้ cost ต่อ pipeline / business unit หรือเปล่า?
- ❓ Self-service portal — domain team ขอ pipeline ใหม่ ต้องผ่าน DE กลางอยู่ใช่หรือไม่?

### The-1 — มีอะไรในแต่ละหมวด

```
Beam config-driven framework  → Group 5 (DataOps), Group 7 (Self-service partial)
Iceberg + BigLake             → Group 1 (Catalog), Group 4 (Encryption)
Hexagonal in insight/         → Group 5 (Software Engineering principle)
DLQ for bad records           → Group 2 (#13)
Cloud Audit Log               → Group 3 (#19)
```

**ที่ The-1 ขาดเด่นๆ** (จากที่ research repo ของคุณ):
- ❌ Data Contracts (#4) — schema breaking change ยังจับที่ปลายน้ำ
- ❌ Active Metadata Catalog (#1) — ยังไม่มี DataHub/Dataplex จริงจัง
- ❌ Data Observability platform (#16) — มีแต่ pipeline monitoring
- ❌ Cost Observability per pipeline (#41)
- ❌ Self-Service Portal สำหรับ domain teams (#47)

---

## 4. Maturity Model — เริ่มจากไหนก่อน

ห้ามทำทุกหมวดพร้อมกัน — ทำตาม maturity:

### Level 1 — **Survival** (ใหม่/MVP)
ต้องมีก่อนเปิด production:
- ✅ Pipeline Monitoring (#15)
- ✅ Alerting (#17)
- ✅ Schema Validation (#9)
- ✅ Audit Logging (#19)
- ✅ Authentication / Authorization (#22, #23)
- ✅ Encryption at Rest + Transit (#28, #29)
- ✅ Version Control (#32)
- ✅ Basic CI/CD (#33)

> หาก 8 ข้อนี้ยังไม่ครบ ห้ามไป Level 2

### Level 2 — **Reliable** (Production stable)
- ✅ Data Quality Tests (#10)
- ✅ DLQ / Quarantine (#13)
- ✅ Pipeline Testing (#34)
- ✅ Environment Management (#35)
- ✅ Idempotency (#38)
- ✅ Backfill / Replay (#37)
- ✅ Secret Management (#30)
- ✅ Cost Attribution (#40, mandatory tags)

### Level 3 — **Trusted** (ลูกค้าเชื่อข้อมูล)
- ✅ Data Catalog (#1)
- ✅ Data Lineage (#3)
- ✅ Data Observability 5 pillars (#16)
- ✅ Anomaly Detection (#11)
- ✅ Reconciliation (#12)
- ✅ Cost Observability (#41)
- ✅ Budget Alerts (#42)
- ✅ Business Glossary (#2)

### Level 4 — **Self-Service** (Scale ทีม)
- ✅ Pipeline Templates (#46)
- ✅ Self-Service Portal (#47)
- ✅ Data Discovery (#48)
- ✅ Data Contracts (#4)
- ✅ Data Stewardship (#5)
- ✅ Documentation Auto-gen (#49)

### Level 5 — **Intelligent** (AI-driven Ops)
- ✅ Auto-anomaly response
- ✅ ML-based DQ rule generation
- ✅ Auto cost optimization
- ✅ AI-powered data discovery (text-to-SQL)
- ✅ Continuous schema evolution

**ปี 2026 องค์กรส่วนใหญ่อยู่ Level 2-3, Tech leaders อยู่ Level 4, ใหญ่ๆ บางที่เริ่ม Level 5**

---

## 5. Capability Map ของ ML/AI Platform (ต่อยอด)

ถ้า Data Platform เก่งครบ Level 3+ แล้ว ML Platform คือชั้นที่อยู่บน

### Group ML-1: Feature Engineering & Storage

| # | Feature | What |
|---|---|---|
| ML-1 | **Feature Store** | reusable features for training + serving |
| ML-2 | **Online Feature Store** | low-latency lookup (Bigtable, Redis) |
| ML-3 | **Offline Feature Store** | bulk read for training (Iceberg) |
| ML-4 | **Feature Versioning** | "feature v2 ใช้ logic ใหม่" |
| ML-5 | **Training/Serving Skew Detection** | offline vs online consistency |

### Group ML-2: Model Lifecycle

| # | Feature | What |
|---|---|---|
| ML-6 | **Experiment Tracking** | log runs, metrics, params (MLflow, W&B) |
| ML-7 | **Model Registry** | versioned model artifacts |
| ML-8 | **Model Deployment** | batch / streaming / online serving |
| ML-9 | **Model Versioning + Rollback** | A/B test, canary |
| ML-10 | **Reproducibility** | exact data + code + env |

### Group ML-3: Model Monitoring (เทียบเท่า Data Observability ฝั่ง ML)

| # | Feature | What |
|---|---|---|
| ML-11 | **Data Drift Detection** | input distribution เปลี่ยน |
| ML-12 | **Model Drift Detection** | output distribution เปลี่ยน |
| ML-13 | **Performance Monitoring** | accuracy/precision over time |
| ML-14 | **Bias / Fairness Monitoring** | model fair across groups |
| ML-15 | **Explainability** | SHAP, LIME, why predicted |

### Group ML-4: GenAI / RAG specific

| # | Feature | What |
|---|---|---|
| GA-1 | **Vector Database** | embedding search |
| GA-2 | **Embedding Pipeline** | text → vector |
| GA-3 | **Prompt Management** | versioned prompts, A/B test |
| GA-4 | **LLM Evaluation** | quality benchmark per release |
| GA-5 | **RAG Quality Tracking** | retrieval precision/recall |
| GA-6 | **Hallucination Detection** | output grounded in source? |
| GA-7 | **Conversation Logging** | log prompts + outputs (also for training) |

### Group ML-5: Operations

| # | Feature | What |
|---|---|---|
| ML-16 | **Auto-retraining** | scheduled / drift-triggered |
| ML-17 | **Feature/Model Lineage** | which model uses which feature |
| ML-18 | **Resource Optimization** | GPU/TPU scheduling |
| ML-19 | **Cost per Inference** | track inference $$ |
| ML-20 | **Compliance / Model Cards** | document training data + bias |

---

## 6. Tool Landscape — Map ต่อ Capability

ผมจัด tool ตามหมวด เพื่อให้คุณเห็นว่าตัวไหนทำหน้าที่ไหน (ปี 2026)

### Catalog + Lineage + Discovery
| Tool | OSS/Commercial | Strength |
|---|---|---|
| **Unity Catalog** | OSS (since 2024) | Native Databricks, multi-format |
| **Dataplex** | GCP | GCP native, integrates BQ + Dataflow |
| **DataHub** | OSS (LinkedIn) | extensible, large community |
| **OpenMetadata** | OSS | newer, modern UI |
| **Atlan** | Commercial | Best UX, governance focus |
| **Collibra** | Commercial | Enterprise / Banking |
| **Alation** | Commercial | Governance + glossary |

### Data Quality + Validation
| Tool | Strength |
|---|---|
| **dbt tests** | inline with transformation, simple |
| **Great Expectations** | rich validation framework |
| **Soda** | testing + observability hybrid |
| **dbt-expectations** | GE-style for dbt |

### Data Observability (5 pillars)
| Tool | Strength |
|---|---|
| **Monte Carlo** | Pioneer, comprehensive |
| **Bigeye** | Auto-thresholding |
| **Acceldata** | Compute + data monitoring |
| **Anomalo** | ML-based anomaly |
| **Datafold** | diff-based validation |

### Pipeline Orchestration
| Tool | Strength |
|---|---|
| **Airflow / Cloud Composer** | matured, plugin-rich |
| **Dagster** | software-defined assets, modern |
| **Prefect** | flexible, hybrid execution |
| **Argo Workflows** | K8s-native |
| **Mage** | developer-friendly |

### Data Contracts
| Tool | Strength |
|---|---|
| **dbt Contracts** | inline with dbt |
| **Confluent Schema Registry** | Kafka-native |
| **Buf** | Protobuf-first |
| **Atlan Data Contracts** | catalog-integrated |

### FinOps for Data
| Tool | Strength |
|---|---|
| **SELECT** | BigQuery focus |
| **Finout** | multi-cloud, Databricks/Snowflake |
| **Revefi** | autonomous AI optimization |
| **Cloudability** | enterprise FinOps |

### ML Platform
| Tool | Strength |
|---|---|
| **MLflow** | open standard, model registry |
| **Vertex AI** | GCP managed end-to-end |
| **SageMaker** | AWS managed |
| **Databricks ML** | unified with data |
| **Kubeflow** | K8s-native, complex |
| **Feast** | OSS feature store |
| **Tecton** | commercial feature platform |

---

## 7. Implementation Pattern ที่ใช้ได้จริง

### Pattern 1: **Cross-cutting Library** (สำหรับ Engine ของคุณ)

แทนที่จะเขียน audit logging ใน 100 pipeline → ทำเป็น library กลาง

```python
# platform_lib/observability.py
class PipelineObservability:
    def __init__(self, job_id: str, dataset: str):
        self.start_time = time.time()
        self.job_id = job_id
        self.dataset = dataset
        self.metrics = {}

    def emit_audit_event(self, event: str, metadata: dict):
        # write to centralized audit log
        ...

    def track_dq(self, dimension: str, value: float):
        # send to observability platform
        ...

    def __enter__(self):
        self.emit_audit_event("pipeline_start", {})
        return self

    def __exit__(self, *args):
        duration = time.time() - self.start_time
        self.emit_audit_event("pipeline_end", {"duration": duration, **self.metrics})
```

```python
# in user pipeline (transparent)
with PipelineObservability(job_id="xyz", dataset="orders") as obs:
    df = read_source(config)
    obs.track_dq("completeness", df.isnull().mean())
    write_sink(df, config)
```

**Insight**: เป็นวิธีให้ developer ไม่ต้องเขียน boilerplate ทุกครั้ง

### Pattern 2: **Hooks in Kernel** (สำหรับ Config-Driven Framework แบบ Data-X / The-1)

```yaml
# pipeline.yaml
pipeline:
  name: customer_360
  hooks:
    pre_run:
      - audit_log_start
      - schema_validation
    post_step:
      - dq_test
      - lineage_emit
    post_run:
      - audit_log_end
      - metrics_publish
      - cost_attribution
  steps:
    - read: { ... }
    - transform: { ... }
    - write: { ... }
```

Kernel จะอ่าน hooks แล้วฉีดเข้าก่อน/หลังแต่ละ step อัตโนมัติ — domain team ไม่ต้องคิด

### Pattern 3: **Sidecar Services** (สำหรับระบบใหญ่)

```
┌─────────────────┐
│   Pipeline      │
│   (Beam/Spark)  │
└────────┬────────┘
         │ emit events
         ▼
┌─────────────────────────────────────────────┐
│   Sidecar Services (กลาง)                   │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌──────┐ │
│  │ Audit  │ │  DQ    │ │Lineage │ │ Cost │ │
│  │ Logger │ │Engine  │ │Emitter │ │Track │ │
│  └────────┘ └────────┘ └────────┘ └──────┘ │
└─────────────────────────────────────────────┘
```

ทุก pipeline emit standard events (OpenLineage / OpenTelemetry) → sidecar services จัดการเอง

**Standards ปี 2026 ที่ใช้กัน**:
- **OpenLineage** — lineage events standard
- **OpenTelemetry** — tracing + metrics standard
- **Iceberg snapshot metadata** — table-level lineage built-in

---

## 8. คำตอบตรงกับคำถามของคุณ

### คำถาม: feature พวก audit log, DQ, validation, lineage, observability เรียกว่าอะไร?

**คำตอบสั้น**: เรียก **Platform Capabilities** (รวม) หรือเรียกตามชื่อกลุ่ม:
- audit log → **Audit Trail** ใน Security
- DQ + validation → **Data Quality** + **Schema Validation**
- lineage → **Data Lineage**
- pipeline quality → **Pipeline Observability**
- ทุกอย่างที่ track สถานะระบบ → **Observability**
- ทุกอย่างที่ track สถานะข้อมูล → **Data Observability** (ต่างกัน — pillar 5)
- submission → **Outbound / Data Distribution**

### คำถาม: ต้องมีอะไรบ้าง?

**คำตอบ**: ดู Maturity Model (ส่วน 4) — Level 1 ครบ 8 ข้อก่อน แล้วค่อยขยับ

### คำถาม: มี framework อะไรที่อ้างอิงได้?

**คำตอบ**: 4 frameworks มาตรฐาน
1. **Joe Reis & Matt Housley — 6 Undercurrents** (Fundamentals of Data Engineering)
2. **Monte Carlo — 5 Pillars of Data Observability**
3. **DAMA-DMBOK — 11 Knowledge Areas** (Data Management Association, ใช้กับ banking/government)
4. **DataOps Manifesto — 18 principles** (สำหรับ DataOps)

ใช้ Joe Reis เป็นหลัก เพราะทันสมัยและ practical สุด

---

## 9. Cheat Sheet ตอนสัมภาษณ์

### Q: "ออกแบบ data platform ใหม่ feature ที่ต้องมีคืออะไร?"

**คำตอบ structure**:
> "ผมแบ่งเป็น 2 มิติครับ — pipeline stages กับ cross-cutting capabilities ที่ Joe Reis เรียกว่า undercurrents"

(แล้วร่ายหมวด — Security, Data Management, DataOps, Architecture, Orchestration, Software Engineering)

> "ในแต่ละ undercurrent มี platform features ที่จำเป็น เช่น Data Quality มี 6 dimensions, Observability มี 5 pillars แบบ Monte Carlo"

> "ผมจัดลำดับใช้ตาม maturity level — Level 1 ต้อง pipeline monitoring + alerting + schema validation + audit log ก่อน ถึงค่อย Level 2 + 3 ขึ้นไป"

### Q: "Audit log กับ Data lineage ต่างกันยังไง?"

> "Audit log ตอบคำถาม **'ใครทำอะไรเมื่อไหร่'** — focus ที่ activity ส่วน Lineage ตอบคำถาม **'ข้อมูลมาจากไหน ไปไหน'** — focus ที่ data flow ทั้งสองอย่างต้องมี ใช้คนละโจทย์"

### Q: "Data Observability ต่างจาก Pipeline Monitoring ยังไง?"

> "Pipeline Monitoring ตรวจ **ตัวระบบ** — job pass/fail, latency, throughput Data Observability ตรวจ **เนื้อข้อมูล** — schema เปลี่ยน, volume drop, value distribution shift Pipeline pass แต่ data ผิดได้ — Monte Carlo เลยเสนอ 5 pillars"

---

## 10. Action Plan สำหรับคุณ

### ให้ตัวเองทำ Audit ของ The-1 / Data-X ก่อน

ใช้ template นี้:

```
Capability                    | The-1 status | Data-X status | Priority
─────────────────────────────────────────────────────────────────────
Pipeline Monitoring           | ✅ มี         | ✅ มี          | -
Alerting                      | ❓ partial    | ✅ มี          | -
Schema Validation             | ✅ มี         | ✅ มี          | -
Audit Logging                 | ✅ มี         | ✅ มี          | -
Authentication                | ✅ มี         | ✅ มี          | -
─────────────────────────────────────────────────────────────────────
Data Quality Tests            | ❓            | ✅ มี          | HIGH
DLQ / Quarantine              | ✅ มี         | ✅ มี          | -
Pipeline Testing              | ❓ partial    | ✅ มี          | HIGH
Cost Attribution              | ❓            | ❓             | MEDIUM
─────────────────────────────────────────────────────────────────────
Data Catalog                  | ❌            | ❓             | HIGH
Data Lineage                  | ❌            | ❓             | HIGH
Data Observability            | ❌            | ❓             | MEDIUM
Anomaly Detection             | ❌            | ❌             | LOW
─────────────────────────────────────────────────────────────────────
Pipeline Templates            | ✅ partial    | ✅ มี          | -
Self-Service Portal           | ❌            | ❓             | MEDIUM
Data Contracts                | ❌            | ❌             | HIGH
```

### กรอบการอ่านเพิ่มเติม (curated)

#### Books (ต้องมี 1 เล่ม)
1. **Fundamentals of Data Engineering** — Joe Reis & Matt Housley (O'Reilly 2022) — เล่มเดียวที่ทุกคนต้องอ่าน
2. **The DataOps Cookbook** — DataKitchen — DataOps practices
3. **Data Management at Scale** — Piethein Strengholt — Federated patterns

#### Online resources
- Monte Carlo blog — Data Observability
- Modern Data 101 (substack) — current trends
- Maxime Beauchemin's articles — Functional DE patterns
- Joe Reis's substack "Practical Data Modeling"

#### Standard documents
- **DAMA-DMBOK 2** — Data Management body of knowledge
- **DataOps Manifesto** — dataopsmanifesto.org
- **OpenLineage spec** — openlineage.io
- **Data Contract spec** — datacontract.com

---

## 11. สรุป — กรอบจำง่าย

ถ้าต้องตอบใน 30 วินาทีว่า "Data Platform feature คืออะไร" ใช้สูตรนี้:

```
2 มิติ
├─ Pipeline Stages (Generate → Ingest → Store → Transform → Serve)
└─ Cross-cutting Capabilities (= Joe Reis's 6 Undercurrents)

8 หมวดของ Capabilities
1. Data Management & Governance       (Catalog, Lineage, Contract, Glossary)
2. Data Quality & Validation          (DQ tests, Schema val, DLQ)
3. Observability & Reliability        (Monitoring, 5 pillars, Alerting, SLA)
4. Security & Privacy                 (RBAC, PII mask, Encrypt, Audit)
5. DataOps / Pipeline Engineering     (CI/CD, Testing, Backfill, Idempotency)
6. FinOps / Cost Management           (Tagging, Cost obs, Budget)
7. Self-Service & Productivity        (Templates, Portal, Discovery)
8. Outbound / Integration             (Submission, Reverse ETL, API)

5 Maturity Levels
Survival → Reliable → Trusted → Self-Service → Intelligent
```

ครั้งหน้าหลงทาง ดู section นี้ — ทุก feature ที่งงๆ จะ map เข้าหมวดใดหมวดหนึ่งใน 8 หมวดนี้แน่นอน

---

## เอกสารชุดอื่นที่เกี่ยวข้อง

- [Modern_Data_AI_Platform_Blueprint.md](Modern_Data_AI_Platform_Blueprint.md) — Architecture patterns + decision framework
- (ถัดไป) `Data_Platform_Implementation_Patterns.md` — concrete code patterns ของแต่ละ capability (ถ้าต้องการ)
- (ถัดไป) `ML_AI_Platform_Capabilities.md` — เจาะลึก ML/AI โดยเฉพาะ

— เอกสารนี้คือ reference ครับ ไม่ต้องอ่านรวดเดียว เปิดดูตอนสับสน
