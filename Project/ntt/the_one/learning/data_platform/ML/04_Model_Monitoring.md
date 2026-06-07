# Model Monitoring — Deep Dive

> ทำไม model พังเงียบๆ ใน production และวิธีตรวจจับ
> สำคัญสุด: model degrades silently — ไม่มี error log แต่ business loss สะสม

---

## 1. ทำไม Model Monitoring ต่างจาก Application Monitoring

### Application Monitoring (DevOps)
ตรวจ:
- Service uptime
- Error rate
- Latency
- Resource usage

**Failure mode**: เห็นชัดเจน — 500 error, timeout, OOM

### Model Monitoring (MLOps)
ตรวจ:
- Prediction accuracy
- Data distribution shifts
- Concept relationships
- Fairness across groups

**Failure mode**: ข้อมูลเงียบ — model ยังตอบ 200 OK แต่คำตอบผิดมากขึ้นเรื่อยๆ

### ตัวอย่างที่เกิดในธุรกิจจริง

| Industry | Silent Failure | Cost |
|---|---|---|
| Banking | fraud model approve transactions ที่ปกติจะ block | Million $ loss |
| E-commerce | recommendation model แนะนำสินค้าหมด stock | Conversion drop 15% |
| Healthcare | diagnosis model bias against demographic | Lawsuit + reputation |
| Logistics | demand forecast off → over/understock | Inventory cost spike |

**Model พังเงียบๆ คือ silent killer ของ ML Platform**

---

## 2. Types of Drift — แยกให้ชัด

### 2.1 Data Drift (Input Drift) — เปลี่ยนที่ INPUT

**คำจำกัดความ**: input feature distributions เปลี่ยนจากตอน train

**ตัวอย่าง**:
- Train data: customer age มี mean 35
- Production: customer age มี mean 50 (older population now)

**Detection method**: เปรียบเทียบ distribution training vs production
- KS test (Kolmogorov-Smirnov) — for continuous
- Chi-square test — for categorical
- PSI (Population Stability Index) — robust, easy to interpret
- KL Divergence — information-theoretic

### 2.2 Concept Drift — เปลี่ยนที่ INPUT→OUTPUT relationship

**คำจำกัดความ**: ความสัมพันธ์ระหว่าง input กับ output เปลี่ยน

**ตัวอย่าง**:
- Train: "high income → low fraud risk"
- After COVID: "high income → high fraud risk" (because new fraud patterns)

**Detection method**: ต้องมี ground truth labels
- Performance monitoring (accuracy drop)
- Predicted vs actual distribution comparison

### 2.3 Label Drift (Prior Drift) — เปลี่ยนที่ OUTPUT distribution

**คำจำกัดความ**: prevalence ของ label เปลี่ยน

**ตัวอย่าง**:
- Train: 1% fraud rate
- Production: 5% fraud rate (fraud wave)

**Detection**: ดู class distribution over time

### 2.4 Feature Drift vs Model Drift — แยกคำให้ชัด

| คำ | หมายถึง |
|---|---|
| **Data Drift** | Input distribution change |
| **Concept Drift** | Input-output relationship change |
| **Model Drift** | Model performance degrades (combined effect) |
| **Label Drift** | Output distribution change |
| **Training-Serving Skew** | Bug — features computed differently |

**Insight**: Skew ≠ Drift
- Skew = your fault (code bug)
- Drift = world changed

---

## 3. The 5 Pillars + ML Specific (Comprehensive Map)

ที่เอามาจาก Monte Carlo + Evidently AI + ML community ปี 2026:

### Layer 1: Data Health (input side)
| Pillar | Method | Alert threshold |
|---|---|---|
| Schema | column count, types, names | Any change |
| Completeness | null % per column | > 5% increase |
| Uniqueness | unique count for keys | drop > 10% |
| Range | min/max bounds | outside trained range |
| Distribution | PSI, KL, KS test | PSI > 0.2 |

### Layer 2: Prediction Health (output side)
| Pillar | Method | Alert threshold |
|---|---|---|
| Prediction distribution | histogram comparison | KS p < 0.05 |
| Prediction confidence | average confidence over time | drop > 10% |
| Class imbalance | predicted class % | shift > 20% |

### Layer 3: Performance Health (with labels)
| Metric | When to use |
|---|---|
| Accuracy | balanced classes |
| Precision/Recall/F1 | imbalanced classes |
| AUC-ROC | binary classification, ranking |
| MAE/RMSE | regression |
| MAP@K, NDCG@K | ranking, recommendation |

### Layer 4: Operational Health
| Metric | Threshold |
|---|---|
| Latency p50, p95, p99 | < SLA |
| Throughput (QPS) | > min QPS |
| Error rate | < 0.1% |
| GPU utilization | 60-90% |

### Layer 5: Business Health
| Metric | Threshold |
|---|---|
| Conversion rate (model-served) | > baseline |
| Revenue per request | trending up |
| User engagement | within range |

### Layer 6: Fairness & Bias
| Metric | Description |
|---|---|
| Demographic Parity | similar prediction rate across groups |
| Equal Opportunity | similar TPR across groups |
| Predictive Parity | similar PPV across groups |

---

## 4. PSI (Population Stability Index) — Deep Dive

PSI เป็น metric ยอดนิยมเพราะ interpret ง่าย

### Formula

```
PSI = Σ (P_actual - P_expected) × ln(P_actual / P_expected)

For each bin:
  P_expected = % of training data in bin
  P_actual   = % of production data in bin
```

### Implementation

```python
import numpy as np

def calculate_psi(expected, actual, bins=10):
    """
    expected: training data distribution
    actual:   production data distribution
    """
    # Define bin edges from expected
    edges = np.percentile(expected, np.linspace(0, 100, bins + 1))
    
    expected_pct = np.histogram(expected, edges)[0] / len(expected)
    actual_pct = np.histogram(actual, edges)[0] / len(actual)
    
    # Avoid log(0)
    expected_pct = np.where(expected_pct == 0, 0.0001, expected_pct)
    actual_pct = np.where(actual_pct == 0, 0.0001, actual_pct)
    
    psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return psi
```

### Interpretation

| PSI | Meaning | Action |
|---|---|---|
| < 0.1 | Stable | None |
| 0.1 – 0.2 | Slight shift | Investigate |
| 0.2 – 0.25 | Moderate shift | Plan retrain |
| > 0.25 | Significant shift | Retrain ASAP |

---

## 5. KL Divergence + KS Test

### KL Divergence (continuous)

วัดว่า P "ห่าง" จาก Q เท่าไหร่ (asymmetric)

```python
from scipy.stats import entropy

def kl_divergence(p_hist, q_hist):
    return entropy(p_hist, q_hist)
```

**Interpretation**: 0 = identical, ∞ = totally different
- ใช้ดี เมื่อข้อมูลเป็น probability distribution

### Kolmogorov-Smirnov (KS) Test

วัด max difference ระหว่าง 2 cumulative distributions

```python
from scipy.stats import ks_2samp

def ks_drift_test(reference, current, alpha=0.05):
    statistic, p_value = ks_2samp(reference, current)
    drift = p_value < alpha
    return drift, statistic, p_value
```

**Pros**: non-parametric, no distribution assumption
**Cons**: sensitive to large samples (false positives)

---

## 6. Performance Monitoring (with Labels)

### Challenge: Label Latency

ปัญหา: ground truth labels มา **ช้า** หลังจาก prediction

```
Time:  T0 ─── prediction ─── T1 ─── label arrives ─── T7 days later
                                    ↑ this delay = label latency
```

**Strategies**:

### Strategy 1: Delayed Performance Tracking
```
For each prediction at time T:
  1. Log prediction
  2. Wait for label (could be days/weeks)
  3. Compute performance retroactively
  4. Update rolling window metrics
```

### Strategy 2: Proxy Metrics (when labels are slow)
- **User feedback** (clicks, conversions)
- **Implicit signals** (no return = correct)
- **Business KPIs** (revenue, retention)

### Strategy 3: Confidence-Based Monitoring
```
If model is "confident" → likely correct
If model is "uncertain" → likely wrong
Track confidence distribution over time
```

---

## 7. Drift Detection Methods Comparison

| Method | When to use | Pros | Cons |
|---|---|---|---|
| **PSI** | Continuous + categorical | Easy interpret | Bin-dependent |
| **KS Test** | Continuous only | Non-parametric | Sensitive to sample size |
| **Chi-Square** | Categorical only | Standard test | Need enough samples per cell |
| **Wasserstein** | Continuous distributions | Symmetric, geometric meaning | Compute heavy |
| **MMD** | Multi-dimensional | Feature interactions | Complex, slow |
| **Adversarial Validation** | High-dim, complex | Catch subtle drift | Overkill for simple cases |

---

## 8. Monitoring Architecture

### Reference Architecture

```
[Production Inference]
        │
        ▼
[Log Predictions + Inputs]
        │
        ▼
┌──────────────────────────┐
│   PREDICTION STORE       │
│   (Iceberg / BQ)         │
│  • input features        │
│  • prediction + score    │
│  • model version         │
│  • request_id            │
│  • timestamp             │
└──────────────────────────┘
        │
        ├──────────────────────┐
        ▼                      ▼
┌──────────────────┐  ┌──────────────────┐
│  Drift Detector  │  │  Label Joiner    │
│  (scheduled)     │  │  (when labels    │
│  • PSI per      │  │   arrive)        │
│    feature       │  │  • Compute       │
│  • Distribution  │  │    metrics       │
│    comparison    │  │  • Performance   │
└──────────────────┘  │    over time     │
        │             └──────────────────┘
        │                      │
        └──────────┬───────────┘
                   ▼
          ┌──────────────────┐
          │  Metrics Store   │
          │  (TSDB)          │
          └──────────────────┘
                   │
                   ▼
          ┌──────────────────┐
          │  Alerting        │
          │  (PagerDuty)     │
          └──────────────────┘
                   │
                   ▼
          ┌──────────────────┐
          │  Dashboard       │
          │  (Grafana)       │
          └──────────────────┘
```

### Schema for Prediction Logs

```sql
CREATE TABLE prediction_logs (
    request_id STRING,
    model_name STRING,
    model_version STRING,
    timestamp TIMESTAMP,
    
    -- Inputs (for drift detection)
    features STRUCT<...>,  -- raw features used
    feature_view_version STRING,
    
    -- Output
    prediction DOUBLE,
    confidence DOUBLE,
    predicted_class STRING,
    
    -- Metadata
    latency_ms INT,
    error STRING,
    
    -- Joined later
    actual_label STRING,
    label_arrival_time TIMESTAMP,
    business_outcome STRUCT<...>
)
PARTITION BY DATE(timestamp);
```

---

## 9. Implementation: Evidently AI

### Setup

```python
from evidently import Report
from evidently.metric_preset import (
    DataDriftPreset,
    DataQualityPreset,
    ClassificationPreset,
    RegressionPreset,
)
```

### Drift Detection

```python
# Reference = training data
# Current = recent production data
report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=train_df, current_data=prod_df)
report.save_html("drift_report.html")

# Programmatic check
result = report.as_dict()
drift_detected = result["metrics"][0]["result"]["dataset_drift"]
if drift_detected:
    alert("Drift detected!")
```

### Performance Tracking

```python
report = Report(metrics=[ClassificationPreset()])
report.run(
    reference_data=val_df,    # baseline performance
    current_data=prod_df,     # current performance
    column_mapping=ColumnMapping(
        target="actual",
        prediction="predicted",
    )
)
```

### Custom Tests

```python
from evidently import TestSuite
from evidently.tests import (
    TestColumnDrift,
    TestNumberOfDriftedColumns,
    TestAccuracyScore,
)

suite = TestSuite(tests=[
    TestColumnDrift(column_name="amount"),
    TestNumberOfDriftedColumns(lt=3),  # less than 3 drifted
    TestAccuracyScore(gt=0.85),        # accuracy > 0.85
])
suite.run(reference_data=train, current_data=prod)
suite.save_html("test_report.html")
```

---

## 10. Vertex AI Model Monitoring (Managed)

```python
from google.cloud import aiplatform

# Setup monitoring on existing endpoint
endpoint = aiplatform.Endpoint("projects/.../endpoints/...")

monitoring_job = endpoint.create_model_monitoring_job(
    display_name="fraud-monitor",
    
    # Sample 10% of requests for monitoring
    log_sampling_strategy=SamplingStrategy(
        random_sample_config={"sample_rate": 0.1}
    ),
    
    # Compare against training data
    objective_config=ObjectiveConfig(
        training_dataset=DatasetGcsSource(
            gcs_uri="gs://my-bucket/train.csv"
        ),
        training_prediction_skew_detection_config=SkewConfig(
            skew_thresholds={
                "amount": 0.3,  # PSI threshold per feature
                "merchant_category": 0.2,
            },
        ),
    ),
    
    # Email when drift detected
    notification_channels=["projects/.../notificationChannels/123"],
)
```

---

## 11. Fairness & Bias Monitoring

### Why Fairness Matters

- Legal: GDPR, AI Act, banking regulations
- Reputational: Bias scandals destroy brands
- Ethical: ML reinforces existing inequalities if not monitored

### Common Metrics

#### Demographic Parity
```
P(prediction=1 | group=A) ≈ P(prediction=1 | group=B)
```
"Same approval rate across groups"

#### Equal Opportunity
```
P(prediction=1 | actual=1, group=A) ≈ P(prediction=1 | actual=1, group=B)
```
"Same true positive rate"

#### Predictive Parity
```
P(actual=1 | prediction=1, group=A) ≈ P(actual=1 | prediction=1, group=B)
```
"Same precision"

### Implementation

```python
from fairlearn.metrics import (
    demographic_parity_difference,
    equalized_odds_difference,
    selection_rate,
)

# Demographic parity
dpd = demographic_parity_difference(
    y_true, y_pred,
    sensitive_features=df["gender"]
)
print(f"Demographic Parity Difference: {dpd}")
# > 0.1 = significant disparity

# Per-group metrics
from fairlearn.metrics import MetricFrame
metric_frame = MetricFrame(
    metrics={
        "selection_rate": selection_rate,
        "accuracy": accuracy_score,
    },
    y_true=y_true,
    y_pred=y_pred,
    sensitive_features=df[["gender", "race"]],
)
print(metric_frame.by_group)
```

### Mitigation Strategies

1. **Pre-processing**: re-balance training data
2. **In-processing**: fair training algorithms
3. **Post-processing**: threshold adjustment per group
4. **Avoid**: removing sensitive feature alone (proxy variables remain)

---

## 12. Alerting Best Practices

### Alert Hierarchy

```
P0 — Page immediately (24/7)
  • Production model crash (0 throughput)
  • Critical accuracy drop (> 20%)
  • Security incident

P1 — Notify team (next business hour)
  • Drift threshold exceeded
  • Latency degradation
  • Fairness regression

P2 — Email digest (daily summary)
  • Minor drift (PSI 0.1-0.2)
  • Cost anomaly
  • Long tail latency
```

### Alert Fatigue — Anti-patterns

❌ Alert on every PSI > 0.1 (too noisy)
❌ Alert on every prediction outlier
❌ Same alert routes to same team always

### Alert Quality

✅ Each alert links to:
- Runbook
- Dashboard
- On-call documentation
- Suggested first action

---

## 13. Retraining Triggers

### When to Retrain

| Trigger | Condition |
|---|---|
| **Schedule** | Weekly / monthly (time-based) |
| **Performance** | Accuracy drop > 5% |
| **Drift** | PSI > 0.25 on key features |
| **Data volume** | 100K new labeled samples |
| **Manual** | Business request |

### Retrain Decision Logic

```python
def should_retrain(model_id):
    metrics = get_recent_metrics(model_id)
    
    # Check 1: Performance degradation
    if metrics["accuracy_drop"] > 0.05:
        return True, "performance_degradation"
    
    # Check 2: Drift
    if metrics["max_psi"] > 0.25:
        return True, "drift_threshold"
    
    # Check 3: Time since last train
    days_since = days_since_last_training(model_id)
    if days_since > 30:
        return True, "scheduled"
    
    # Check 4: New data volume
    new_samples = count_new_labeled_samples(model_id)
    if new_samples > 100000:
        return True, "new_data"
    
    return False, "stable"
```

---

## 14. Runbook Template — When Drift Detected

```markdown
# Runbook: Model Drift Alert

## Step 1: Validate (5 min)
- [ ] Check alert source (Vertex / Evidently / custom)
- [ ] Reproduce in dashboard
- [ ] Check if data pipeline is healthy (upstream OK?)

## Step 2: Investigate (30 min)
- [ ] Which features drifted?
- [ ] When did drift start?
- [ ] Is performance degraded? (need labels)
- [ ] Is it data quality issue or true drift?

## Step 3: Decide (1 hour)
Decision tree:
  If data quality issue:
    → Fix upstream pipeline
    → Re-validate
  If true drift + performance OK:
    → Document, monitor closer
    → Consider retraining cadence
  If true drift + performance degraded:
    → Trigger emergency retrain
    → Or rollback to previous version

## Step 4: Action
- [ ] Document in incident log
- [ ] Update threshold if false alarm
- [ ] Schedule retrain if needed
- [ ] Notify stakeholders
```

---

## 15. Cost of Monitoring

### Monitoring Cost Components

| Component | Cost driver |
|---|---|
| Storage (prediction logs) | rows × retention |
| Compute (drift detection) | jobs × frequency |
| Query (dashboards) | analyst usage |
| Tools (Evidently, Vertex Monitoring) | flat or usage |

### Optimization

- Sample predictions (1-10% for drift detection)
- Aggregate metrics (don't keep per-request forever)
- Tier retention (raw 30 days, aggregated 1 year)
- Use existing infra (Iceberg + dbt > buy new tool)

---

## 16. Cheat Sheet

### Q: "Drift กับ Skew ต่างกันยังไง?"
> "Skew = bug — features คำนวณคนละทางใน training vs serving (your fault)
> Drift = world change — input distribution หรือ relationship เปลี่ยน (real)"

### Q: "ใช้ PSI หรือ KS test ดี?"
> "PSI: easy interpret, threshold ชัด (>0.2 = drift) — ใช้ใน production
> KS: statistical rigor, p-value — ใช้ใน research / detailed analysis"

### Q: "ตรวจ drift ได้ ก็ต้องตรวจ performance ด้วย?"
> "ใช่ — drift ≠ degradation — model อาจ robust ต่อ drift
> ถ้าไม่มี label, ใช้ proxy: confidence drift, prediction distribution, business metrics"

### Q: "ต้อง retrain ทุกครั้งที่ drift มั้ย?"
> "ไม่ — ขึ้นกับว่า performance degraded จริงหรือไม่
> ถ้า drift แต่ accuracy ยังโอเค = monitor แต่ไม่ต้อง retrain
> ถ้า drift + accuracy drop = retrain ทันที"

---

## เอกสารต่อ

- [01_ML_Platform_Overview.md](01_ML_Platform_Overview.md) — ภาพรวม
- [02_MLOps_Lifecycle.md](02_MLOps_Lifecycle.md) — pipeline patterns
- [03_Feature_Store_Deep_Dive.md](03_Feature_Store_Deep_Dive.md) — features ที่ป้อน model
