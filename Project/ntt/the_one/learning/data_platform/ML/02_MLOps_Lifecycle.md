# MLOps Lifecycle — Deep Dive

> เจาะลึก lifecycle ของ ML system ตั้งแต่ data → production → continuous improvement
> โฟกัสที่ Traditional ML — สำหรับ LLM ดู `../AI/03_LLMOps_and_Evaluation.md`

---

## 1. The MLOps Lifecycle — 8 Phases

ML model มี lifecycle ที่ซับซ้อนกว่า application ทั่วไป เพราะ **มี 3 artifact** ต้องจัดการ: code, data, และ model

### ภาพรวม Lifecycle

```
1. SCOPING          — กำหนด business problem + success metric
        ↓
2. DATA              — collect, validate, version
        ↓
3. FEATURE ENGINEER  — create + register features
        ↓
4. EXPERIMENT        — train, evaluate, compare
        ↓
5. PACKAGE           — containerize, register
        ↓
6. DEPLOY            — batch / online / streaming
        ↓
7. MONITOR           — performance, drift, cost
        ↓
8. CONTINUOUS TRAIN  — retrain on schedule / drift
        ↓
       (loop back to step 4)
```

### Phase 1: Scoping (Business Discovery)

**Output**: Problem definition document

ต้องตอบ:
- **Business KPI** ที่ต้องการขยับ (เช่น "ลด fraud loss 30%")
- **ML Metric** ที่ proxy KPI (เช่น "AUC > 0.92, Recall@1% > 0.6")
- **Cost of error** — false positive vs false negative ราคา?
- **Decision threshold** — ใครคน vs ระบบ?
- **Data availability** — มีข้อมูล + label พอมั้ย?
- **Feasibility** — model นี้เคยมีคนทำสำเร็จมั้ย?

**Anti-pattern**: Skip phase นี้ → train model ไม่รู้เพื่ออะไร

### Phase 2: Data (Data Acquisition + Validation)

**Output**: Versioned + validated dataset

Activities:
- **Source identification** — data มาจากไหน, owner ใคร
- **Schema validation** — ใช้ Great Expectations / dbt tests
- **Data versioning** — DVC, Iceberg snapshots, lakeFS
- **Train/Val/Test split** — by time (NOT random) สำหรับ time-series
- **PII handling** — masking, tokenization

**Critical**: ใช้ Iceberg snapshot ID เป็น "data version" — ตามรอยได้ที่ชัด

```python
# Example: snapshot-based versioning
training_data = spark.read.format("iceberg") \
    .option("snapshot-id", "1234567890") \  # immutable
    .load("warehouse.transactions")
```

### Phase 3: Feature Engineering

**Output**: Registered features ใน Feature Store

Activities:
- **Feature definition** (declarative YAML)
- **Feature implementation** (pipeline code)
- **Feature validation** (range, distribution)
- **Feature documentation** (purpose, owner)

```yaml
# feature_definition.yaml
feature_view: customer_features_v3
entity: customer_id
features:
  - name: avg_purchase_7d
    type: float
    source: silver.customer_purchases
    aggregation: avg(amount)
    window: 7d
    materialization: daily_batch
    online_freshness: 1h
```

### Phase 4: Experiment & Train

**Output**: Trained model + metrics + artifacts

ทุก experiment ต้อง log:
- **Run metadata**: code SHA, data snapshot, env hash
- **Hyperparameters**: ทั้งหมดที่กำหนด
- **Metrics**: training metric + validation metric
- **Artifacts**: model file, plots, confusion matrix
- **Resources**: GPU type, training duration, $ cost

```python
# MLflow tracking pattern
import mlflow

with mlflow.start_run() as run:
    # Auto-log code SHA
    mlflow.set_tag("git_sha", get_current_sha())
    mlflow.set_tag("data_snapshot", "1234567890")
    
    # Train
    mlflow.log_params(params)
    model.fit(X_train, y_train)
    
    # Evaluate
    metrics = evaluate(model, X_val, y_val)
    mlflow.log_metrics(metrics)
    
    # Save artifacts
    mlflow.sklearn.log_model(model, "model")
    mlflow.log_artifact("feature_importance.png")
```

**Best practices ปี 2026**:
- ใช้ **autolog** เมื่อทำได้ (MLflow autolog framework)
- ใช้ **Tags** ไม่ใช่ params สำหรับ metadata (e.g., `model_type=xgboost`)
- เก็บ **input examples** ใน model signature

### Phase 5: Package & Register

**Output**: Production-ready model artifact ใน Registry

Activities:
- **Package model** with serving code (BentoML, MLflow Models)
- **Containerize** (Docker image with deps)
- **Register** in Model Registry with version
- **Sign artifacts** (for supply chain security)

```python
# Register pattern
mlflow.register_model(
    model_uri=f"runs:/{run.info.run_id}/model",
    name="fraud_detector",
    tags={
        "owner": "risk_team",
        "approver_required": "true",
        "pii_used": "false"
    }
)
```

### Phase 6: Deploy

**Output**: Model serving in production

3 deployment patterns ที่ใช้ปี 2026:

#### 6.1 Shadow Deployment
```
Production traffic → Old Model → response to user
                  └→ New Model → log only (no impact)
```
ใช้สำหรับ test model ใหม่กับ real traffic โดยไม่กระทบ user

#### 6.2 Canary Deployment
```
1% traffic  → New Model  (monitor closely)
99% traffic → Old Model
   ↓ if metrics OK
10% → New, 90% → Old
   ↓
50% / 50%
   ↓
100% New, 0% Old
```

#### 6.3 A/B Testing
```
Cohort A (random split) → Model V1
Cohort B (random split) → Model V2
   ↓ measure business metrics for X days
Statistical test → pick winner
```

### Phase 7: Monitor

ดู `04_Model_Monitoring.md` สำหรับ deep dive

หลักๆ ต้องตรวจ:
- **Performance**: accuracy/precision/recall/AUC over time
- **Data drift**: input distribution shift (PSI > 0.2 = alert)
- **Concept drift**: relationship change (need labels)
- **Operational**: latency, throughput, error rate
- **Business KPI**: conversion rate, fraud loss, etc.

### Phase 8: Continuous Training (CT)

**Trigger**:
- **Schedule-based**: weekly/daily retrain
- **Performance-based**: accuracy drop > X% → retrain
- **Drift-based**: PSI > threshold → retrain
- **Data-based**: N new labeled samples → retrain
- **Manual**: data scientist judgment call

**CT Pipeline**:
```
[Trigger] 
   ↓
[Validate new data] (schema, distribution)
   ↓
[Train new model version]
   ↓
[Evaluate vs current production]
   ↓
[Approval gate] (auto if metrics improve, manual if degrade)
   ↓
[Shadow / Canary deploy]
   ↓
[Monitor for X days]
   ↓
[Promote to full production]
```

---

## 2. CI/CD/CT for ML — เทียบกับ DevOps

### CI (Continuous Integration)

ทุก commit รัน:
- **Lint & format** (black, ruff)
- **Unit tests** (model logic + data utils)
- **Data validation tests** (Great Expectations)
- **Smoke training** (1% data, fast)
- **Code review** (mandatory)

```yaml
# .github/workflows/ci.yml example
name: ML CI
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt
      - run: pytest tests/unit/
      - run: great_expectations checkpoint run smoke
      - run: python scripts/smoke_train.py --sample 0.01
```

### CD (Continuous Deployment)

เมื่อ merge to main:
- **Build container** with model serving code
- **Push to registry** (Artifact Registry)
- **Deploy to staging** (auto)
- **Run integration tests** (real endpoint)
- **Promote to canary** (5% traffic)
- **Auto-promote to production** ถ้า metrics OK

### CT (Continuous Training)

**Different from DevOps** — pipeline ที่ผลิต model ใหม่:
- **Trigger types** (schedule, drift, performance)
- **Training environment** (GPU pool, distributed)
- **Auto-validation** vs production model
- **Approval workflow** (auto if improved, manual otherwise)

---

## 3. Pipeline Patterns ปี 2026

### Pattern A: Kubeflow Pipelines (Vertex AI Pipelines)

```python
@dsl.pipeline(name="fraud-training")
def training_pipeline(
    data_snapshot: str,
    feature_view: str,
):
    # Step 1: Validate data
    validate_op = validate_data(snapshot=data_snapshot)
    
    # Step 2: Get features
    features_op = get_features(
        feature_view=feature_view,
        entity_df=validate_op.outputs["entity_df"]
    )
    
    # Step 3: Train
    train_op = train_model(features=features_op.output)
    
    # Step 4: Evaluate
    eval_op = evaluate_model(
        model=train_op.outputs["model"],
        test_data=features_op.outputs["test_data"]
    )
    
    # Step 5: Conditional deploy
    with dsl.If(eval_op.outputs["auc"] >= 0.92):
        deploy_op = deploy_model(model=train_op.outputs["model"])
```

### Pattern B: Metaflow (Netflix)

```python
class FraudFlow(FlowSpec):
    
    @step
    def start(self):
        self.data = read_iceberg("transactions", snapshot=self.snapshot_id)
        self.next(self.train)
    
    @resources(cpu=8, memory=16000, gpu=1)
    @step
    def train(self):
        self.model = train(self.data)
        self.next(self.evaluate)
    
    @step
    def evaluate(self):
        self.metrics = evaluate(self.model, self.data)
        if self.metrics["auc"] >= 0.92:
            self.next(self.deploy)
        else:
            self.next(self.end)
    
    @step
    def deploy(self):
        register_model(self.model)
        self.next(self.end)
```

### Pattern C: Airflow + Custom (legacy / banking)

```python
# Airflow DAG
with DAG("fraud_training", schedule="0 2 * * *") as dag:
    validate = SparkSubmitOperator(...)
    train = KubernetesPodOperator(image="fraud-trainer:latest", ...)
    evaluate = PythonOperator(...)
    branch = BranchPythonOperator(...)
    deploy = MLflowDeployOperator(...)
```

---

## 4. Experiment Tracking — Beyond MLflow

### Anti-patterns ที่พบบ่อย

❌ **Spreadsheet tracking** — ลืม update, ไม่มี versioning
❌ **Notebook + email** — ไม่ reproducible
❌ **Print to console** — log หาย
❌ **Save to S3 manual** — ไม่ structured

### Required tags ทุก experiment

```python
mlflow.set_tags({
    "git_sha": get_git_sha(),
    "git_branch": get_branch(),
    "data_snapshot": snapshot_id,
    "feature_view_version": "v3",
    "trainer_version": "2.4.1",
    "purpose": "hyperparam_search",  # or "production_candidate"
    "owner": "@username",
    "environment": "training-gpu-pool-1"
})
```

### What to log

| Type | Example | Tool method |
|---|---|---|
| Hyperparams | `lr=0.01`, `depth=6` | `log_params()` |
| Metrics | `auc=0.92` over epochs | `log_metric(step=epoch)` |
| Artifacts | model, feature importance | `log_artifact()` |
| Tags | metadata, environment | `set_tags()` |
| Inputs | sample data examples | `log_input()` |
| Models | with signature | `log_model()` |

---

## 5. Model Registry Patterns

### Workflow: From Run → Production

```
1. Training run produces model artifact
        ↓
2. mlflow.register_model() → version 1 created (stage: None)
        ↓
3. Evaluate vs current production
        ↓
4. If metrics improve: 
   - Tag as `@candidate`
   - Trigger approval workflow
        ↓
5. Approver reviews:
   - Model card
   - Evaluation report
   - Fairness audit
        ↓
6. Promote to staging (`@staging` alias)
        ↓
7. Deploy to staging environment
        ↓
8. Run integration + load tests
        ↓
9. Canary in production (5% traffic)
        ↓
10. Monitor 7 days
        ↓
11. If stable: promote to `@production` (replaces previous)
        ↓
12. Old version → `@archived`
```

### Naming + Aliasing Best Practice

**ห้าม**: `fraud_model_v2`, `fraud_model_2026_01_15` (versioning ใน name)
**ทำ**: `fraud_detector` (product name) + version (auto) + alias (env)

```
Model: fraud_detector
  Version 1 → archived
  Version 2 → archived
  ...
  Version 41 → @champion (current production)
  Version 42 → @candidate (under review)
```

### Rollback strategy

❌ ห้าม serve `@production` alias — ขึ้นกับ infra config
✅ Serve specific version (`fraud_detector:41`)
✅ Rollback = update infra config to previous version

---

## 6. Deployment Architectures

### 6.1 Online Inference (Real-time API)

```
[Client] → [API Gateway] → [Model Server] → [Online Feature Store]
                                ↓
                          [Response]
```

**Components**:
- **API Gateway**: auth, rate limit, routing (Kong, Apigee)
- **Model Server**: BentoML / Seldon / Vertex Endpoint / Triton
- **Feature Lookup**: Bigtable / Redis / DynamoDB
- **Caching**: Redis for repeated requests

**Latency budget** (typical):
```
Total: 100ms
├─ Network: 20ms
├─ Auth + routing: 5ms
├─ Feature lookup: 30ms
├─ Model inference: 30ms
├─ Post-processing: 10ms
└─ Response serialize: 5ms
```

### 6.2 Batch Inference

```
[Scheduler (Airflow)] 
       ↓
[Read input data (Iceberg)]
       ↓
[Get features (Offline FS)]
       ↓
[Apply model (Spark/Beam)]
       ↓
[Write predictions (Iceberg)]
       ↓
[Sync to operational DB / Reverse ETL]
```

**Pattern**: ใช้ Spark broadcast model + UDF หรือ pandas_udf
```python
@pandas_udf("double")
def predict(*features: pd.Series) -> pd.Series:
    df = pd.concat(features, axis=1)
    return pd.Series(model.predict_proba(df)[:, 1])

result = data.withColumn("prediction", predict(*feature_cols))
```

### 6.3 Streaming Inference

```
[Kafka / PubSub] → [Beam / Flink] → [Model] → [Output topic]
                          ↓
                  [Online Feature Store lookup]
```

**Pattern**: Embed model ใน stream processor
```python
class PredictDoFn(beam.DoFn):
    def setup(self):
        self.model = load_model_from_registry("fraud_detector", alias="champion")
        self.fs_client = FeatureStoreClient()
    
    def process(self, event):
        features = self.fs_client.get_online_features(
            entity={"customer_id": event["customer_id"]},
            features=["avg_purchase_7d", "txn_count_1h"]
        )
        score = self.model.predict([features])[0]
        yield {**event, "fraud_score": score}
```

---

## 7. Infrastructure for ML Training

### Resource Patterns

| Workload | Resource | Cost optimization |
|---|---|---|
| Data prep | CPU + RAM | Spot instances |
| Training (small) | 1 GPU | On-demand T4 |
| Training (large) | Multi-GPU | Reserved A100 |
| Hyperparam search | Many CPUs/GPUs in parallel | Spot + preemptible |
| Inference (online) | CPU/GPU on autoscale | Reserved + autoscale buffer |
| Inference (batch) | CPU pool | Spot instances |

### Distributed Training Patterns

```
Data Parallel (most common):
   Same model on each GPU, different data shards
   
Model Parallel:
   Model split across GPUs (when model too big)
   
Pipeline Parallel:
   Layers split, GPUs work like assembly line
```

**Tools**: PyTorch DDP, Horovod, Ray Train, DeepSpeed

---

## 8. ML Pipeline Testing

### Test Pyramid for ML

```
        ┌─────────────────┐
        │ E2E Pipeline    │  (slow, expensive)
        │   tests         │
        ├─────────────────┤
        │ Integration     │  (medium)
        │   tests         │
        ├─────────────────┤
        │ Unit tests      │  (fast, cheap)
        │ + Data tests    │
        └─────────────────┘
```

### What to test

| Layer | Test type | Example |
|---|---|---|
| Data | Schema | "table has columns A, B, C" |
| Data | Distribution | "amount column is positive" |
| Feature | Correctness | "avg_7d on synthetic data = expected" |
| Feature | Skew | "offline computed = online served" |
| Model | Logic | "predict() returns shape (n, 2)" |
| Model | Performance | "AUC on holdout > 0.85" |
| Model | Invariance | "predict same with re-ordered features" |
| Pipeline | Smoke | "full pipeline runs on 1% data" |
| Pipeline | E2E | "full pipeline produces deployable model" |

### Specific tests for production safety

```python
def test_no_pii_in_features():
    features = get_features("v3")
    assert "phone_number" not in features
    assert "email" not in features

def test_predictions_in_range():
    preds = model.predict(test_X)
    assert (preds >= 0).all() and (preds <= 1).all()

def test_no_constant_predictions():
    preds = model.predict(diverse_test_X)
    assert preds.std() > 0.01  # not stuck

def test_fairness():
    for group in ["A", "B", "C"]:
        group_preds = model.predict(test_X[test_X.group == group])
        # check fairness metric
        assert demographic_parity(preds) < 0.1
```

---

## 9. Common Anti-Patterns ของ ML Pipeline

### ❌ Training-Serving Skew
**สาเหตุ**: feature คำนวณคนละทางใน training vs serving

**แก้**: ใช้ feature store ที่บังคับใช้ definition เดียวกัน

### ❌ Data Leakage
**สาเหตุ**: features ที่ใช้ "future information"

**แก้**: point-in-time joins (ดู Feature Store doc)

### ❌ Random Train/Test Split for Time Series
**สาเหตุ**: ใช้ `train_test_split(random=True)` กับ time series data → leak future ไป past

**แก้**: split by time (e.g., train: <2026-01, val: 2026-01, test: 2026-02)

### ❌ Hyperparam Tuning on Test Set
**สาเหตุ**: ใช้ test set ตอน tune hyperparams → optimistic estimate

**แก้**: 3-way split (train/val/test) — tune บน val, evaluate บน test เดียว

### ❌ Model Drift Without Detection
**สาเหตุ**: deploy แล้วลืม

**แก้**: monitoring + alerting + automated retraining

### ❌ "model.pkl" in Git
**สาเหตุ**: large binaries → repo bloat

**แก้**: Model Registry + DVC

### ❌ Silent Schema Changes
**สาเหตุ**: data team เปลี่ยน column → model พัง

**แก้**: Data Contracts + schema validation in CI

---

## 10. Cost & Resource Optimization

### Training Cost
| Strategy | Saving |
|---|---|
| Spot/Preemptible GPUs | 60–80% |
| Right-size models | 30–50% |
| Distributed training (faster wall time) | 20–40% |
| Mixed precision (fp16) | 30% memory, 1.5x speed |
| Cache feature views | 50% (avoid recompute) |

### Inference Cost
| Strategy | Saving |
|---|---|
| Quantization (INT8) | 4x throughput, slight accuracy drop |
| Distillation (small model) | 5–10x cost |
| Dynamic batching | 2–3x throughput |
| Autoscaling on traffic | 30–60% (peak vs avg) |
| GPU sharing (multi-tenant) | 2–4x utilization |

### Monitoring Cost
| Strategy | Saving |
|---|---|
| Sample for drift (not 100%) | 90% |
| Aggregate metrics (not per-request) | 50–80% |
| Tiered alerting (don't page all) | reduce noise |

---

## 11. Reference Implementation: GCP

### Recommended Stack ปี 2026 บน GCP

```
TRAINING:
  Vertex AI Pipelines (KFP) — orchestration
  Vertex AI Training Jobs — distributed training
  Vertex AI Experiments — tracking
  Vertex Model Registry — registry

SERVING:
  Vertex Endpoints — online inference
  Cloud Run + BentoML — alternative serving
  Dataflow + Beam — streaming inference

FEATURES:
  Feast (OSS) on top of:
    Iceberg/BQ — offline FS
    Bigtable — online FS

MONITORING:
  Vertex Model Monitoring — built-in drift detection
  Evidently — open source supplement
  Cloud Monitoring — operational

GOVERNANCE:
  Dataplex — model + data catalog
  IAM + workload identity — access
  Cloud Audit Logs — audit trail
```

### ทางเลือกที่ Cost-conscious

```
Replace Vertex AI Endpoint → Cloud Run + BentoML (cheaper for low-traffic)
Replace Vertex Pipelines → Cloud Composer + Kubeflow (more flexible)
Use Iceberg + DuckDB local for fast experiments (no Vertex notebook needed)
```

---

## 12. Checklist: Production Readiness

ก่อนจะปล่อย model production ใหม่ ทุกตัวต้องผ่าน checklist นี้:

### Code & Pipeline
- [ ] Code in Git, peer-reviewed
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Pipeline reproducible (rerun gets same result)

### Data
- [ ] Data lineage documented
- [ ] Schema validated in CI
- [ ] No PII leakage to features
- [ ] Train/val/test split verified
- [ ] No data leakage detected

### Model
- [ ] Model card written
- [ ] Performance metrics > baseline
- [ ] Fairness audit passed
- [ ] Latency benchmark passed
- [ ] Memory usage acceptable

### Deployment
- [ ] Container builds successfully
- [ ] Health check endpoint works
- [ ] Logging configured
- [ ] Metrics exported
- [ ] Alerts configured

### Monitoring
- [ ] Performance dashboard exists
- [ ] Drift detection configured
- [ ] Alert routing setup
- [ ] On-call documented
- [ ] Runbook written

### Governance
- [ ] Approver signed off
- [ ] Compliance reviewed
- [ ] Rollback plan documented
- [ ] Incident response tested

---

## เอกสารต่อ

- [03_Feature_Store_Deep_Dive.md](03_Feature_Store_Deep_Dive.md)
- [04_Model_Monitoring.md](04_Model_Monitoring.md)
- [01_ML_Platform_Overview.md](01_ML_Platform_Overview.md) (ภาพรวม)
