# AutoML — Deep Dive

> Automated ML — model selection + tuning + feature engineering
> When AutoML helps, when it hurts, what's mature ปี 2026

---

## 1. AutoML Spectrum

### What "AutoML" Means (varies)

```
LEVEL 1: Hyperparameter tuning automation
  → Optuna, Hyperopt, Vertex Vizier
  
LEVEL 2: Algorithm selection
  → Try XGBoost vs LightGBM vs RF, pick best
  
LEVEL 3: Feature engineering automation
  → Featuretools, AutoFeat
  
LEVEL 4: End-to-end (data → model)
  → AutoGluon, H2O AutoML, Vertex AI AutoML
  
LEVEL 5: Architecture search (neural)
  → NAS (Neural Architecture Search)
  → AutoKeras
  
LEVEL 6: AI-driven (LLM as engineer)
  → "Build me a churn model" → LLM generates pipeline
  → Emerging in 2026
```

---

## 2. When AutoML Helps

### Good Use Cases

✅ **Quick prototyping** — get baseline in hours
✅ **Standard tabular** — well-understood problem types
✅ **Limited DS team** — domain experts use AutoML
✅ **Hyperparameter tuning** — always automate this
✅ **Benchmarking** — compare against AutoML baseline

### Bad Use Cases

❌ **Custom domain** — needs domain knowledge
❌ **Strict latency budget** — AutoML often picks ensembles (slow)
❌ **Need interpretability** — black box ensembles
❌ **Unique data structure** — graph, time series with rare patterns
❌ **Production-critical** — manual tuning > black box for last 5%
❌ **Strict compliance** — auditors want explainable choices

---

## 3. AutoML Tools (2026)

### AutoGluon (recommended general-purpose)

```python
from autogluon.tabular import TabularDataset, TabularPredictor

train_data = TabularDataset('train.csv')

predictor = TabularPredictor(
    label='target',
    eval_metric='roc_auc'
).fit(
    train_data,
    presets='best_quality',  # quality vs speed
    time_limit=3600,  # 1 hour
)

# Predict
predictions = predictor.predict(test_data)
proba = predictor.predict_proba(test_data)

# Inspect
print(predictor.leaderboard())
predictor.feature_importance(test_data)
```

**Pros**:
- AWS-backed, OSS
- Good defaults (60-80% of optimal manual)
- Handles categorical natively
- Stacking + bagging built-in

**Cons**:
- Final model often big (ensemble)
- Less control

### H2O AutoML

```python
import h2o
from h2o.automl import H2OAutoML

h2o.init()
train = h2o.import_file('train.csv')

aml = H2OAutoML(
    max_models=20,
    max_runtime_secs=3600,
    seed=42
)
aml.train(x=feature_cols, y='target', training_frame=train)

# Leaderboard
print(aml.leaderboard.head())

# Best model
best = aml.leader
predictions = best.predict(test)
```

### Vertex AI AutoML (managed, GCP)

```python
from google.cloud import aiplatform

aiplatform.init(project='my-project')

# AutoML Tables
job = aiplatform.AutoMLTabularTrainingJob(
    display_name='churn_automl',
    optimization_prediction_type='classification',
    optimization_objective='maximize-au-roc'
)

dataset = aiplatform.TabularDataset.create(
    display_name='churn_data',
    bq_source='bq://project.dataset.train_table'
)

model = job.run(
    dataset=dataset,
    target_column='churned',
    budget_milli_node_hours=8000,  # 8 hours
    model_display_name='churn_v1'
)

# Deploy
endpoint = model.deploy(machine_type='n1-standard-4')
```

**Pros**:
- Fully managed
- Easy productionization
- Integration with BigQuery

**Cons**:
- Expensive
- Vendor lock-in
- Black-box (less inspectable)

### FLAML (Microsoft, fast)

```python
from flaml import AutoML

automl = AutoML()
automl.fit(
    X_train, y_train,
    task='classification',
    metric='roc_auc',
    time_budget=60,  # 1 minute!
    estimator_list=['lgbm', 'xgboost', 'rf'],
)

best_model = automl.model
```

**Pros**: 
- Very fast (CFO algorithm)
- Lightweight

**Cons**:
- Less features
- Smaller ecosystem

### AutoKeras (Neural Architecture Search)

```python
import autokeras as ak

# For tabular
clf = ak.StructuredDataClassifier(max_trials=10, overwrite=True)
clf.fit(X_train, y_train, epochs=50)

# For image
clf = ak.ImageClassifier(max_trials=5, overwrite=True)
clf.fit(images, labels, epochs=20)
```

**Pros**: 
- DL focus
- Architecture discovery

**Cons**:
- Slow (NAS expensive)
- Often beaten by pre-trained transfer learning

---

## 4. AutoML Internals

### How AutoGluon Works

```
1. Data preprocessing
   - Auto-detect column types
   - Missing value imputation
   - Categorical encoding
   - Date feature extraction
   
2. Train multiple models (in parallel where possible)
   - LightGBM
   - XGBoost
   - CatBoost
   - Random Forest
   - Extra Trees
   - Neural Network (MLP)
   - K-NN
   
3. Hyperparameter tuning per model
   - Bayesian optimization
   - Stop bad trials early
   
4. Stacking (multi-level ensemble)
   - Level 1: base models predict
   - Level 2: meta-model on predictions
   - Bagging: train multiple seeds
   
5. Model selection
   - Pick best by validation metric
   - Or weighted ensemble of top-K
```

### Bayesian Optimization (under the hood)

```
Round 1: Try random hyperparameters
  Get score → record (params, score)

Round 2+: 
  Build surrogate model: f(params) → expected score
  Find params that maximize "Expected Improvement"
  Try those params
  Update surrogate

Continue until budget exhausted
```

---

## 5. AutoML Workflow (Pragmatic)

### Phase 1: Quick Baseline

```python
# 5-minute baseline
from autogluon.tabular import TabularPredictor

predictor = TabularPredictor(label='target').fit(
    train_data,
    presets='medium_quality',
    time_limit=300
)
print(f"Baseline AUC: {predictor.evaluate(test_data)['roc_auc']}")
```

### Phase 2: Investigate Findings

```python
# What features matter?
importance = predictor.feature_importance(test_data)

# Which models are best?
print(predictor.leaderboard())

# What hyperparameters did it pick?
print(predictor.info())
```

### Phase 3: Manual Improvements

Based on findings:
- Add domain features (target encoding, interactions)
- Fix data quality issues
- Try specific model with more tuning

### Phase 4: Compare Manual vs AutoML

```python
manual_score = my_xgboost.score(test)
automl_score = predictor.evaluate(test_data)['roc_auc']

if abs(manual_score - automl_score) < 0.005:
    # AutoML is fine — use it
    deploy(predictor)
else:
    # Manual gives meaningfully better
    deploy(my_xgboost)
```

---

## 6. Hyperparameter Tuning (always automate this)

### Optuna — Best General Choice

```python
import optuna

def objective(trial):
    params = {
        'max_depth': trial.suggest_int('max_depth', 3, 12),
        'learning_rate': trial.suggest_float('lr', 1e-3, 0.3, log=True),
        'n_estimators': trial.suggest_int('n_est', 100, 2000),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('cs', 0.6, 1.0),
        'reg_alpha': trial.suggest_float('alpha', 1e-8, 10, log=True),
        'reg_lambda': trial.suggest_float('lambda', 1e-8, 10, log=True),
    }
    
    model = XGBClassifier(**params, early_stopping_rounds=50)
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    return roc_auc_score(y_val, model.predict_proba(X_val)[:, 1])

study = optuna.create_study(
    direction='maximize',
    pruner=optuna.pruners.MedianPruner(n_warmup_steps=10),
)
study.optimize(objective, n_trials=200, n_jobs=4, timeout=3600)

print(study.best_params)
print(study.best_value)
```

### Pruning (kill bad trials early)

```python
def objective_with_pruning(trial):
    params = {...}
    model = XGBClassifier(**params)
    
    for epoch in range(num_iterations):
        model.fit(X_train, y_train, partial=True)
        score = score_at_epoch(model, X_val, y_val)
        
        # Report intermediate value
        trial.report(score, epoch)
        
        # Prune if seems hopeless
        if trial.should_prune():
            raise optuna.TrialPruned()
    
    return final_score
```

### Multi-Objective Optimization

```python
# Optimize accuracy AND latency
def objective(trial):
    params = {...}
    model = train(params)
    accuracy = evaluate(model)
    latency = measure_latency(model)
    return accuracy, -latency  # maximize first, minimize second

study = optuna.create_study(directions=['maximize', 'minimize'])
study.optimize(objective, n_trials=100)

# Pareto front
pareto = study.best_trials  # multiple optimal trade-offs
```

### Distributed Tuning

```python
# Multiple machines coordinating
study = optuna.create_study(
    storage='postgresql://...',  # shared state
    study_name='production_tuning',
    load_if_exists=True
)
study.optimize(objective, n_trials=50)  # each worker contributes
```

---

## 7. Feature Generation Automation

### Featuretools (Deep Feature Synthesis)

```python
import featuretools as ft

# Define entities
es = ft.EntitySet(id='ecommerce')
es.add_dataframe(dataframe_name='customers', dataframe=customers, index='customer_id')
es.add_dataframe(dataframe_name='orders', dataframe=orders, index='order_id')
es.add_dataframe(dataframe_name='items', dataframe=items, index='item_id')

# Relationships
es.add_relationship('customers', 'customer_id', 'orders', 'customer_id')
es.add_relationship('orders', 'order_id', 'items', 'order_id')

# Auto-generate features
features, definitions = ft.dfs(
    entityset=es,
    target_dataframe_name='customers',
    agg_primitives=['sum', 'mean', 'std', 'count', 'max', 'min'],
    trans_primitives=['day', 'month', 'weekday', 'is_weekend'],
    max_depth=3,
)

# Result: hundreds of features auto-generated
# e.g., MEAN(orders.SUM(items.price))
```

### AutoFeat

```python
from autofeat import AutoFeatClassifier

clf = AutoFeatClassifier(
    feateng_steps=2,
    featsel_runs=5,
)
X_features = clf.fit_transform(X_train, y_train)
# Generated polynomial + non-linear features
```

---

## 8. AutoML for Specific Domains

### Time Series: AutoTS, NeuralForecast

```python
from neuralforecast import NeuralForecast
from neuralforecast.auto import AutoNHITS, AutoTFT

models = [
    AutoNHITS(h=horizon, num_samples=20),
    AutoTFT(h=horizon, num_samples=20),
]

nf = NeuralForecast(models=models, freq='D')
nf.fit(df=train_df)
forecast = nf.predict()
```

### NLP: Hugging Face AutoTrain

```bash
# CLI tool
autotrain llm \
    --train \
    --project_name my-llm-finetune \
    --model meta-llama/Llama-2-7b \
    --data_path ./data \
    --use_peft \
    --num_train_epochs 3
```

### Vision: AutoML for Computer Vision

```python
from autogluon.multimodal import MultiModalPredictor

predictor = MultiModalPredictor(
    label='label',
    problem_type='multiclass',
    eval_metric='accuracy',
).fit(
    train_data='./images_with_labels',
    time_limit=3600,
)
```

---

## 9. AutoML in Production

### Architectural Patterns

#### Pattern A: AutoML for Initial Model
```
1. Train AutoML model
2. Inspect what it does
3. Reimplement manually with controls
4. Deploy manual version (faster, more controlled)
```

#### Pattern B: AutoML as Continuous Retraining
```
Schedule:
  Weekly: AutoML on fresh data
  If new model meaningfully better: deploy
  Else: stick with current
```

#### Pattern C: AutoML in Self-Service Platform
```
Domain users upload data + label column
AutoML handles all complexity
User gets API endpoint
```

### Production Considerations

#### Latency
AutoML often picks ensembles → slow
Solutions:
- Constrain to single model (`presets='best_quality_no_ensembling'`)
- Distill ensemble → smaller model

#### Memory
Ensembles = N× memory
- Quantize
- Pick subset of models for ensemble

#### Reproducibility
```python
predictor.fit(..., random_seed=42)
# But: AutoML often inherently stochastic
# Fix: pin versions, save full pipeline
```

#### Versioning
```python
# Save full predictor (includes all preprocessing)
predictor.save('./model_v1')

# Load
predictor = TabularPredictor.load('./model_v1')
```

---

## 10. Limitations Real Talk

### Where AutoML Falls Short

#### 1. Domain Knowledge
```
Problem: Predict loan default
AutoML doesn't know:
  - 'days_since_late_payment' is highly predictive
  - 'income_to_debt_ratio' should be capped at 10
  - Macro economic features should be included

Manual: incorporates these → 5-10% better
```

#### 2. Data Leakage Detection
```
AutoML uses 'closed_at' feature
   → only filled for closed accounts
   → leaks target

Manual: would catch in EDA
AutoML: may not detect
```

#### 3. Custom Loss Functions
```
Standard AutoML: ROC-AUC, accuracy, MSE
Need: weighted asymmetric loss?
   AutoML often can't customize
```

#### 4. Feature Drift Awareness
```
AutoML picks best features at training time
But some features drift heavily
   → manual would prefer more stable features
```

#### 5. Multi-Objective
```
Optimize accuracy + latency + fairness?
Most AutoML single objective
```

---

## 11. AI-Driven AutoML (2026 emerging)

### LLM as Data Scientist

```python
# Example: AutoGen Agent
from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent(
    name="data_scientist",
    system_message="You are an expert ML engineer. Build models step by step.",
    llm_config={"model": "claude-sonnet-4-6"}
)

user = UserProxyAgent(
    name="user",
    code_execution_config={"work_dir": "."}
)

user.initiate_chat(
    assistant,
    message="Here's churn data. Build me a model. Optimize for AUC."
)

# Assistant writes code, executes, iterates
```

### Tools (2026)

- **OpenAI Code Interpreter**
- **Claude Code SDK**
- **Sketch (Python)**
- **PandasAI**

### Limits

- Hallucination (suggests wrong approach)
- No real domain knowledge
- Fragile to errors
- **Augment, don't replace** experienced DS

---

## 12. Cheat Sheet

### Q: "AutoML แทน Data Scientist ได้มั้ย?"
> "ไม่ — แทนได้บางส่วน
> AutoML ทำ standard tasks เร็ว แต่ DS ยังจำเป็นสำหรับ:
> - Problem framing
> - Feature engineering with domain knowledge
> - Data quality + leakage detection
> - Production decisions
> Best: AutoML + DS = 10x productive together"

### Q: "เริ่ม AutoML จากตัวไหน?"
> "AutoGluon (general, AWS-backed) — best default
> H2O — enterprise, mature
> Vertex AI / SageMaker AutoML — managed cloud
> FLAML — fast prototyping
> Optuna — always automate hyperparameter tuning"

### Q: "Production ใช้ AutoML ดีมั้ย?"
> "ใช้ได้ แต่:
> 1. Constrain ensemble size (latency)
> 2. Save full pipeline (preprocessing + model)
> 3. Monitor drift (AutoML model still drifts)
> 4. Have rollback to previous version
> 5. Document chosen model + features"

### Q: "Optuna vs AutoML?"
> "Optuna: tune ONE algorithm (XGBoost) deeply
> AutoML: try MANY algorithms shallowly
> Often combine: AutoML to pick algo → Optuna to tune"

---

## Sources

- [AutoGluon Documentation](https://auto.gluon.ai/)
- [H2O AutoML](https://docs.h2o.ai/h2o/latest-stable/h2o-docs/automl.html)
- [Vertex AI AutoML](https://cloud.google.com/vertex-ai/docs/training/automl-api)
- [Optuna Documentation](https://optuna.org/)
- [FLAML Documentation](https://microsoft.github.io/FLAML/)
- [AutoKeras](https://autokeras.com/)
- [Featuretools](https://featuretools.alteryx.com/)
- [NeuralForecast](https://nixtlaverse.nixtla.io/neuralforecast/)
