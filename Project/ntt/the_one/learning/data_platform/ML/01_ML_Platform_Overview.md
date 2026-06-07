# ML Platform — Capability Overview & Mental Model

> ครอบคลุม Traditional ML (regression, classification, ranking, forecasting, recommender)
> ไม่รวม GenAI/LLM — ดู `../AI/` แทน
> Last update: 2026-05

---

## 0. ML Platform คืออะไร — แยกจาก Data Platform ยังไง

### ความสับสนที่พบบ่อย

หลายคนคิดว่า ML Platform = **"ฝั่งที่ Data Scientist train model"** — ผิดครับ

**ML Platform** คือชั้นที่อยู่ **บน** Data Platform เพื่อทำ 4 อย่าง:
1. ผลิต model (training)
2. เก็บ + version model (registry)
3. รัน model ใน production (serving)
4. monitor model ตลอดอายุการใช้งาน (observability)

**Data Platform** = "ผลิตและจัดการข้อมูล"
**ML Platform** = "ผลิตและจัดการ model + features"

### แสดงความสัมพันธ์เป็นแผนภาพ

```
┌──────────────────────────────────────────────────────────┐
│                  AI / GENAI PLATFORM                     │
│   (LLM, RAG, Agents — see AI/ folder)                    │
└───────────────────────┬──────────────────────────────────┘
                        ▲ uses features + embeddings
┌──────────────────────────────────────────────────────────┐
│                   ML PLATFORM                            │
│   ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │
│   │Feature  │  │ Training │  │  Model   │  │ Serving │  │
│   │ Store   │  │ Pipeline │  │ Registry │  │ Layer   │  │
│   └─────────┘  └──────────┘  └──────────┘  └─────────┘  │
│   ┌──────────────────────────────────────────────────┐  │
│   │     MLOps (CI/CD/CT, Monitoring, Lineage)        │  │
│   └──────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────────────────────────┘
                        ▲ pulls data, writes features
┌──────────────────────────────────────────────────────────┐
│                   DATA PLATFORM                          │
│   (Lakehouse, Streaming, Catalog, Governance)            │
└──────────────────────────────────────────────────────────┘
```

---

## 1. Mental Model — 6 Component Groups

ML Platform ปี 2026 แบ่งได้เป็น **6 หมวด** (24 capabilities ครอบคลุม)

### Group 1: Feature Engineering & Storage

| # | Capability | What |
|---|---|---|
| ML-1 | **Offline Feature Store** | features สำหรับ training (bulk read) — เก็บใน Iceberg/BQ |
| ML-2 | **Online Feature Store** | features สำหรับ inference — low-latency lookup (Bigtable, Redis) |
| ML-3 | **Feature Definition / Registry** | declarative feature spec (YAML) ใน Git |
| ML-4 | **Feature Versioning** | track เวอร์ชันของ feature logic |
| ML-5 | **Feature Lineage** | track ข้อมูล source ของ feature |
| ML-6 | **Point-in-Time Correctness** | ป้องกัน data leakage ตอน training |

### Group 2: Training & Experimentation

| # | Capability | What |
|---|---|---|
| ML-7 | **Experiment Tracking** | log runs, metrics, params (MLflow, W&B) |
| ML-8 | **Hyperparameter Tuning** | grid/Bayesian/random search (Optuna, Vizier) |
| ML-9 | **Distributed Training** | multi-GPU/multi-node (Horovod, Ray, PyTorch DDP) |
| ML-10 | **Reproducibility** | snapshot ของ data + code + env + seed |
| ML-11 | **Notebook / IDE Environment** | shared workspace (Vertex Workbench, Databricks) |

### Group 3: Model Registry & Versioning

| # | Capability | What |
|---|---|---|
| ML-12 | **Model Registry** | central store พร้อม metadata, stages |
| ML-13 | **Model Versioning** | semantic version + immutable artifacts |
| ML-14 | **Model Aliases** | `@champion`, `@challenger`, environment-bound |
| ML-15 | **Model Lineage** | trace model → training run → data → feature |

### Group 4: Deployment & Serving

| # | Capability | What |
|---|---|---|
| ML-16 | **Batch Inference** | scheduled scoring (nightly cohort) |
| ML-17 | **Online Inference (REST/gRPC)** | sync request-response, ms-latency |
| ML-18 | **Streaming Inference** | embedded ใน stream processor (Beam, Flink) |
| ML-19 | **Edge / On-device** | optimized model สำหรับ mobile/IoT |
| ML-20 | **A/B Testing / Canary** | route traffic เปรียบเทียบ model versions |

### Group 5: Monitoring & Observability

| # | Capability | What |
|---|---|---|
| ML-21 | **Performance Monitoring** | accuracy/precision/AUC over time |
| ML-22 | **Data Drift Detection** | input distribution shift (PSI, KL divergence) |
| ML-23 | **Concept Drift Detection** | input→output relationship shift |
| ML-24 | **Training-Serving Skew** | offline features ≠ online features |
| ML-25 | **Bias / Fairness** | model fair across demographic groups |
| ML-26 | **Explainability** | SHAP, LIME, counterfactuals |

### Group 6: MLOps / Governance

| # | Capability | What |
|---|---|---|
| ML-27 | **CI/CD/CT Pipeline** | automated test, deploy, retrain |
| ML-28 | **Model Cards / Documentation** | training data, intended use, limitations |
| ML-29 | **Model Approval Gates** | human review before production |
| ML-30 | **Compliance / Audit** | who deployed what, training data trail |
| ML-31 | **Cost Tracking** | $ per training run / inference |
| ML-32 | **Resource Optimization** | GPU scheduling, autoscaling |

---

## 2. The 3 Levels of ML Software (ปี 2026 framework)

ใช้ในวงการเพื่อบอก maturity ของ ML system:

### Level 0 — **Manual ML Process**
```
Data Scientist runs notebook → trains model → emails .pkl file → engineer deploys
```
- Manual training, manual deployment
- ไม่มี monitoring
- เหมาะกับ POC / research เท่านั้น

### Level 1 — **ML Pipeline Automation (CI/CT)**
```
Data → Auto-feature engineering → Auto-training → Validation → Auto-deploy → Monitor
```
- Automated retraining (CT = Continuous Training)
- Performance monitoring + alerting
- Pipeline ทดสอบ + integration test ก่อน deploy

### Level 2 — **CI/CD Pipeline Automation**
```
Code change → CI tests → Trigger training pipeline → Auto-deploy → Monitor → Auto-rollback
```
- ทุกอย่างใน Level 1
- + CI/CD ของ pipeline code เอง (ไม่ใช่แค่ model)
- + automated rollback เมื่อตรวจ degradation

**ปี 2026 enterprise มาตรฐาน = Level 1, leaders ใช้ Level 2**

---

## 3. ML Maturity Model (4 Stages)

ที่อ้างอิง: Microsoft + Google ML maturity framework (ปรับปี 2026)

### Stage 1 — **Initial / Reactive**
- ทุกอย่าง manual
- ไม่มี version control ของ data + model
- ปัญหาแก้แบบ ad-hoc
- **ปัญหาที่เจอ**: model พังใน production, ไม่รู้สาเหตุ, retrain เอง

### Stage 2 — **Repeatable**
- Notebook → ปรับเป็น script
- ใช้ Git สำหรับ code
- มี basic experiment tracking (MLflow)
- Manual deployment
- **ปัญหาที่เจอ**: time to deploy นาน, ไม่รู้ว่า model degrade

### Stage 3 — **Automated** (← เป้าหมาย enterprise)
- CI/CD pipeline
- Feature store
- Model registry + automated promotion
- Automated monitoring + alerting
- **คุณลักษณะ**: deploy ได้เร็ว, monitor 24/7, retrain ได้บ่อย

### Stage 4 — **Resilient / Adaptive**
- Auto-retraining triggered by drift
- Self-healing (auto-rollback, auto-scale)
- Continuous experimentation (always-on A/B)
- AI-driven optimization (AutoML, Auto-feature)
- **คุณลักษณะ**: ระบบจัดการตัวเองในกรณีปกติ ทีมโฟกัส innovation

---

## 4. Reference Architecture สำหรับ ML Platform

### Architecture Diagram (E2E)

```
                                                                     
┌────────────────────────────────────────────────────────────────┐
│                  DATA PLATFORM (existing)                      │
│         Iceberg (offline) + Streaming (CDC + Kafka)            │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│                    FEATURE PLATFORM                            │
│  ┌──────────────────┐         ┌──────────────────────┐         │
│  │ Feature Pipeline │ ──────► │ Offline Feature Store│         │
│  │ (Beam/Spark/dbt) │         │ (Iceberg/BQ)         │         │
│  └──────────────────┘         └──────────────────────┘         │
│             │                            │                     │
│             ▼                            ▼                     │
│  ┌──────────────────────────────────────────────┐              │
│  │   Online Feature Store (Bigtable/Redis)      │              │
│  │   ← synced from offline (eventual sync)      │              │
│  └──────────────────────────────────────────────┘              │
└────────────────────────────────────────────────────────────────┘
              │                            │
              ▼                            ▼
┌──────────────────────────┐    ┌──────────────────────────────┐
│   TRAINING PLATFORM      │    │   SERVING PLATFORM           │
│   ┌────────────────────┐ │    │   ┌────────────────────────┐ │
│   │ Vertex AI Pipelines│ │    │   │ Online Endpoint        │ │
│   │ (Kubeflow)         │ │    │   │ (Vertex / SageMaker)   │ │
│   └────────────────────┘ │    │   └────────────────────────┘ │
│   ┌────────────────────┐ │    │   ┌────────────────────────┐ │
│   │ MLflow Tracking    │ │    │   │ Batch Inference        │ │
│   │ + Experiments      │ │    │   │ (Spark / Beam)         │ │
│   └────────────────────┘ │    │   └────────────────────────┘ │
│   ┌────────────────────┐ │    │   ┌────────────────────────┐ │
│   │ Model Registry     │◄─────┼──►│ Streaming Inference    │ │
│   │ (MLflow/Vertex)    │ │    │   │ (Beam/Flink + Model)   │ │
│   └────────────────────┘ │    │   └────────────────────────┘ │
└──────────────────────────┘    └──────────────────────────────┘
                                              │
                                              ▼
                                  ┌──────────────────────────┐
                                  │   MONITORING LAYER       │
                                  │ • Performance metrics    │
                                  │ • Drift detection        │
                                  │ • Skew detection         │
                                  │ • Cost / latency         │
                                  └──────────────────────────┘
```

---

## 5. Cross-functional Requirements ของ ML Platform

ที่ enterprise มักลืม:

### 5.1 Reproducibility — เทรน model เดิมได้ไหม?

ต้องเก็บ:
- **Code version** (Git SHA)
- **Data snapshot** (Iceberg snapshot ID, dataset version)
- **Feature definitions** (feature store version)
- **Hyperparameters** (saved with run)
- **Environment** (Docker image hash, requirements.txt)
- **Random seeds** (numpy, torch, tf seeds)
- **Hardware** (CPU/GPU type for non-deterministic ops)

**กฎ**: ถ้าเทรน model 6 เดือนที่แล้วซ้ำได้ผลเหมือนเดิม = reproducible

### 5.2 Lineage — ตามรอย model ได้ไหม?

```
Training Run (run_id: abc123)
   ├─ Code: github.com/repo@a1b2c3
   ├─ Data: iceberg.transactions@snapshot=789
   ├─ Features: [user_avg_7d_v3, txn_count_1h_v2]
   ├─ Hyperparams: {lr: 0.01, depth: 6}
   ├─ Metrics: {auc: 0.92, precision: 0.85}
   ├─ Artifacts: model.pkl (sha256: ...)
   └─ Output: registered as fraud_model:42
```

ทุก link ต้องตามได้ทั้งสองทาง (forward + backward)

### 5.3 Governance — ใครรับผิดชอบ?

```
Model Card:
  name: fraud_detector
  owner: @risk_team
  approver: @model_review_board
  intended_use: "Score credit card transactions for fraud risk"
  out_of_scope: "Not for loan decisions, not for KYC"
  training_data: iceberg.fraud_labels@2026-04-01
  pii_used: ["card_hash", "amount", "merchant_category"]
  known_limitations:
    - "Lower recall on amounts > $10K"
    - "Performance degrades on new merchant types"
  fairness_audit: 2026-04-15 (passed)
  retrain_schedule: weekly
  drift_thresholds:
    psi: 0.2
    accuracy_drop: 5%
```

ทุก production model ต้องมี Model Card

---

## 6. Tech Stack Reference (2026)

### All-in-One Platforms
| Platform | Strength | When to use |
|---|---|---|
| **Vertex AI** (GCP) | Managed end-to-end, integrates BQ | GCP-native shop |
| **SageMaker** (AWS) | AWS-native, mature | AWS shop |
| **Databricks ML** | Unified data + ML, MLflow native | Already on Databricks |
| **Azure ML** | Azure-native | Azure shop |

### Open Source Stack (Composable)
| Layer | Tool | Note |
|---|---|---|
| Tracking | **MLflow** | de facto standard |
| Registry | **MLflow Registry** | with stages + aliases |
| Pipeline | **Kubeflow Pipelines** / **Metaflow** | K8s-native vs Netflix |
| Feature Store | **Feast** | OSS, point-in-time correct |
| Serving | **BentoML** / **Ray Serve** / **Seldon Core** | framework-agnostic |
| Monitoring | **Evidently** / **WhyLabs** | drift + performance |
| Hyperparam | **Optuna** | Bayesian, parallelizable |

### Specialized
| Tool | Purpose |
|---|---|
| **DVC** | data version control |
| **Great Expectations** | data validation for ML |
| **Fiddler / Arize** | model observability (commercial) |
| **Weights & Biases** | experiment tracking (better UX than MLflow) |

---

## 7. Map กับ The-1 / Banking ของคุณ

ที่ The-1 เคยทำ (จาก repo ที่สำรวจ):
- ✅ Data Platform (Beam config-driven) — solid foundation
- ❓ Feature Store — มี Bigtable แต่ไม่รู้ใช้แบบ feature store มั้ย
- ❌ Model Registry กลาง — น่าจะแยกตาม domain
- ❌ Centralized Training Platform — แต่ละโปรเจกต์ทำเอง
- ❌ Cross-domain Model Monitoring

### ที่ควรเพิ่มก่อน (priority order)

**Priority 1**: Model Registry (MLflow) + Experiment Tracking
- ลงทุนน้อย, ได้ผลทันที
- หลีกเลี่ยง model.pkl ที่หาไม่เจอ

**Priority 2**: Feature Store ที่ทำ point-in-time joins ได้
- Feast on top of Iceberg + Bigtable
- ลด training-serving skew

**Priority 3**: Model Monitoring (Evidently)
- Drift detection + Performance tracking
- เริ่มจาก model สำคัญที่สุดก่อน

**Priority 4**: CI/CD/CT Pipeline
- Automated training trigger
- Approval gates ก่อน production

---

## 8. คำถามที่ใช้ตัดสินใจสำหรับโปรเจกต์ใหม่

### Q1. Latency requirement?
- < 100ms → Online inference + Online Feature Store + ผ่าน edge cache
- 100ms – 1s → Online inference + Online Feature Store
- 1s – 1min → Streaming inference
- 1hr+ → Batch inference

### Q2. Retrain frequency?
- < 1 hour → Online learning (rare, complex)
- Daily → Automated CT pipeline
- Weekly → Scheduled retrain
- Monthly+ → Manual retrain ok

### Q3. Model size + complexity?
- < 100 MB → ใช้ commodity serving (CPU)
- 100 MB – 10 GB → GPU serving
- > 10 GB → Distributed serving (model parallelism)

### Q4. Drift sensitivity?
- High (fraud, recommendation) → Real-time drift detection
- Medium (churn, LTV) → Daily drift report
- Low (forecasting) → Weekly drift check

---

## 9. คำที่สับสนบ่อย — แยกให้ชัด

| Term A | Term B | ต่างกันยังไง |
|---|---|---|
| MLOps | DevOps | MLOps มี data + model artifacts ที่ DevOps ไม่มี |
| Training Pipeline | Inference Pipeline | Training: data → model. Inference: model + new data → predictions |
| Model Registry | Model Store | Registry มี metadata + governance, Store แค่ artifacts |
| Online Feature Store | Online Inference | FS = lookup features ms. Inference = run model |
| Concept Drift | Data Drift | Concept: input→output relationship change. Data: input distribution change |
| Training-Serving Skew | Drift | Skew: train ≠ serve features (bug). Drift: world changed (real) |
| Champion / Challenger | A/B Test | Champion = current prod. Challenger = candidate. A/B = serve both |
| Batch Score | Online Score | Batch: scheduled bulk. Online: per-request |

---

## 10. สรุปสำหรับสัมภาษณ์ / ออกแบบ

### Cheat Sheet

```
ML Platform = Feature Platform + Training Platform + Serving Platform 
              + Monitoring + MLOps

6 หมวด, 32 capabilities
4 stages of maturity (Initial → Repeatable → Automated → Resilient)
3 levels of ML software (Manual → CI/CT → CI/CD/CT)
```

### Q: "ออกแบบ ML platform ใหม่ เริ่มยังไง?"

> "เริ่มจาก use case จริงก่อน — ต้องการ batch หรือ online? Latency เท่าไหร่? Retrain frequency?
> แล้ว map ลง 6 หมวด: Feature, Training, Registry, Serving, Monitoring, MLOps
> Priority แรกที่ลงทุนเสมอคือ Registry + Experiment Tracking — ลงทุนน้อย ได้ traceability ทันที
> Feature Store ลงทุนเฉพาะถ้ามี > 3 model ที่ใช้ feature ซ้ำกัน
> Model Monitoring สำคัญที่สุดเมื่อ scale — เพราะ silent degradation = สูญเงินจริง"

### Q: "ML Platform ของคุณอยู่ Stage ไหน?"

> "ตอนนี้ Stage 2 (Repeatable) — มี Git, MLflow, Docker แต่ deployment ยัง manual
> เป้าหมาย Stage 3 (Automated) ใน 6 เดือนข้างหน้า — เพิ่ม CT pipeline + automated monitoring
> Stage 4 (Resilient) ค่อยมาคิดเมื่อมี > 20 production models"

---

## เอกสารต่อใน folder นี้

- [02_MLOps_Lifecycle.md](02_MLOps_Lifecycle.md) — เจาะลึก CI/CD/CT pipeline, experiment tracking, deployment patterns
- [03_Feature_Store_Deep_Dive.md](03_Feature_Store_Deep_Dive.md) — Online/Offline sync, point-in-time joins, training-serving skew
- [04_Model_Monitoring.md](04_Model_Monitoring.md) — Drift detection methods, performance tracking, fairness
