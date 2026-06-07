# ML Algorithm Families — Deep Dive

> Tabular (XGBoost), Deep Learning, Time Series, Anomaly, Clustering
> Pick the right algorithm for the right problem

---

## 1. Algorithm Selection Framework

### First Question: What's the Problem Shape?

```
Predicting:
  Number → Regression
  Category (2 classes) → Binary Classification
  Category (N classes) → Multi-class Classification
  Ranking/Order → Ranking
  Sequence → Sequence Models
  
Discovering:
  Groups → Clustering
  Outliers → Anomaly Detection
  Patterns → Pattern Mining
  
Generating:
  Content → Generative Models (mostly DL)
```

### Second Question: Data Type?

```
Tabular (rows of features):
  Default: XGBoost / LightGBM
  Linear: Logistic / Linear Regression
  Small data: SVM, Random Forest

Time Series:
  Classical: ARIMA, Prophet
  ML: XGBoost with lag features
  DL: LSTM, Transformers, TFT

Text:
  Classical: TF-IDF + Logistic
  Modern: BERT/Transformers
  Or: LLM with embeddings (see AI/)

Image:
  Default: CNN (ResNet, EfficientNet)
  Modern: Vision Transformers (ViT)
  Or: Pre-trained models + fine-tune

Graph:
  Graph Neural Networks (GNN)
  Or: feature engineering + tabular ML

Audio:
  Mel spectrogram + CNN
  Or: Wav2Vec, Whisper
```

---

## 2. Tabular ML — XGBoost & Friends

### Why Gradient Boosting Dominates Tabular

In 2026, gradient boosting still wins ~80% of tabular Kaggle competitions

**Why**:
- Handles mixed feature types (numeric + categorical)
- No need for normalization
- Robust to outliers
- Captures non-linear + interactions
- Handles missing values natively
- Fast inference

### XGBoost / LightGBM / CatBoost — Comparison

| | XGBoost | LightGBM | CatBoost |
|---|---|---|---|
| Speed | Good | **Fastest** | Good |
| Accuracy | High | High | High |
| Categorical | Manual encoding | Limited native | **Best native** |
| Missing | ✅ | ✅ | ✅ |
| Memory | Higher | **Lower** | Higher |
| GPU | ✅ | ✅ | ✅ |
| Default tuning | OK | OK | **Best** |

**Recommendation**:
- Start with **LightGBM** (fastest)
- Switch to **CatBoost** if many categorical features
- **XGBoost** if you need broader ecosystem support

### XGBoost Algorithm (intuition)

```
1. Start with a single leaf prediction (mean of target)
2. Compute residuals: actual - predicted
3. Train a small tree to predict residuals
4. Update prediction: previous + learning_rate × tree_prediction
5. Repeat 1000+ times
6. Final prediction = sum of all trees
```

### Hyperparameters that Matter

```python
import xgboost as xgb

model = xgb.XGBClassifier(
    # Tree structure
    max_depth=6,           # 4-10 typical (deeper = overfit)
    min_child_weight=1,    # higher = regularization
    
    # Boosting
    n_estimators=1000,     # number of trees
    learning_rate=0.05,    # 0.01-0.3, lower = more trees
    
    # Sampling (regularization)
    subsample=0.8,         # row sampling per tree
    colsample_bytree=0.8,  # feature sampling per tree
    
    # Regularization
    reg_alpha=0,           # L1
    reg_lambda=1,          # L2
    
    # Imbalanced data
    scale_pos_weight=1,    # neg_count / pos_count for binary
    
    # Speed
    tree_method='hist',    # 'hist' or 'gpu_hist'
    n_jobs=-1
)

# Critical: early stopping
model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    early_stopping_rounds=50,  # stop if no improvement
)
```

### Production Considerations

```python
# Save with feature names + version
model.save_model("model.json")
import json
metadata = {
    "feature_names": list(X_train.columns),
    "feature_dtypes": str(X_train.dtypes),
    "training_date": "2026-05-04",
    "training_metric": "auc=0.92"
}
json.dump(metadata, open("model_meta.json", "w"))

# Load + predict
model = xgb.XGBClassifier()
model.load_model("model.json")
preds = model.predict_proba(X_new)[:, 1]
```

---

## 3. Deep Learning Tabular (when to bother)

### Truth: DL Rarely Beats GBM on Tabular

For ~10K rows: GBM dominates
For >1M rows + complex interactions: DL competitive

### Models that work for tabular DL

#### TabNet (Google, 2019)
Attention-based, interpretable feature selection

#### FT-Transformer (Yandex)
Transformer for tabular, performs well on large datasets

#### NODE (Yandex)
Neural oblivious decision ensembles

#### Tabular Transformer (2024+)
Variants leveraging foundation model pretraining

### When to use DL Tabular

- Very large dataset (>10M rows)
- Need to combine with images/text in same model
- Transfer learning from related tabular task

### Avoid DL Tabular when

- < 100K rows
- Simple tabular problem
- Need fast inference + training
- Need interpretability (use GBM + SHAP instead)

---

## 4. Time Series Forecasting

### Classical Methods (still relevant)

#### ARIMA / SARIMA
```python
from statsmodels.tsa.arima.model import ARIMA

model = ARIMA(series, order=(p, d, q))  # (AR, differencing, MA)
fit = model.fit()
forecast = fit.forecast(steps=30)
```
- Good for: stationary data, clear seasonality
- Limited: doesn't use external regressors easily

#### Prophet (Facebook)
```python
from prophet import Prophet

model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    seasonality_mode='multiplicative'
)
model.add_country_holidays(country_name='TH')
model.add_regressor('promo_active')
model.fit(df)  # df has 'ds' (date) + 'y' (value)

forecast = model.predict(future_df)
```
- Good for: business series with seasonality + holidays
- Easy to use, handles missing data

### ML Approach: XGBoost on Time Features

```python
def create_features(df):
    df['hour'] = df.timestamp.dt.hour
    df['dayofweek'] = df.timestamp.dt.dayofweek
    df['month'] = df.timestamp.dt.month
    df['lag_1'] = df.value.shift(1)
    df['lag_7'] = df.value.shift(7)
    df['rolling_mean_7'] = df.value.shift(1).rolling(7).mean()
    df['rolling_std_30'] = df.value.shift(1).rolling(30).std()
    return df

# Train XGBoost on these features
model = xgb.XGBRegressor()
model.fit(features, target)
```

**Best practice**: Always use lagged features, NOT current value (avoid leakage)

### Modern Deep Learning for Time Series

#### LSTM / GRU
```python
# PyTorch
class LSTMForecaster(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])  # last timestep output
```

#### Temporal Fusion Transformer (TFT)
- SOTA for many time series tasks
- Combines RNN + Transformer
- Interpretable attention

#### Foundation Time Series Models (2024+)
- **Chronos** (Amazon, 2024)
- **TimesFM** (Google, 2024)
- **Moirai** (Salesforce, 2024)
- Pretrained on diverse time series → zero-shot forecast
- 2026 reality: works for general patterns, custom domain still benefits from training

### Choosing

```
< 5 time series, business data:
  → Prophet (easy, handles seasonality + holidays)

Many time series (1000+), need accuracy:
  → XGBoost with lag features

Complex multivariate, long horizon:
  → TFT or transformer

Quick zero-shot baseline:
  → Foundation models (Chronos, TimesFM)
```

---

## 5. Anomaly Detection

### When to use which

| Algorithm | Use case |
|---|---|
| **Z-score / IQR** | Univariate, simple thresholds |
| **Isolation Forest** | Tabular, fast, unsupervised |
| **One-class SVM** | Small dataset, complex boundary |
| **Autoencoder** | High-dim, deep features |
| **Statistical tests (CUSUM, EWMA)** | Time series drift |
| **Prophet** | Time series with seasonality |
| **LOF (Local Outlier Factor)** | Density-based clusters |

### Isolation Forest (most common)

```python
from sklearn.ensemble import IsolationForest

model = IsolationForest(
    n_estimators=100,
    contamination=0.01,  # expected anomaly fraction
    random_state=42
)
model.fit(X_train)

# Score: -1 = anomaly, 1 = normal
predictions = model.predict(X_new)

# Anomaly score (lower = more anomalous)
scores = model.decision_function(X_new)
```

**How it works**: random partitioning trees — anomalies isolated quickly

### Autoencoder for Anomaly

```python
# Train autoencoder on NORMAL data only
# Anomalies have high reconstruction error
class Autoencoder(nn.Module):
    def __init__(self, input_dim, encoding_dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, encoding_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(encoding_dim, 64),
            nn.ReLU(),
            nn.Linear(64, input_dim)
        )
    
    def forward(self, x):
        encoded = self.encoder(x)
        return self.decoder(encoded)

# Train on normal data
# At inference: high MSE = anomaly
def detect_anomaly(model, x, threshold):
    reconstructed = model(x)
    error = ((reconstructed - x) ** 2).mean(dim=1)
    return error > threshold
```

---

## 6. Clustering

### K-Means
```python
from sklearn.cluster import KMeans

model = KMeans(n_clusters=5, n_init=10, random_state=42)
model.fit(X)
labels = model.predict(X)
```
- Simple, fast
- Need to specify K
- Assumes spherical clusters

### DBSCAN (density-based)
```python
from sklearn.cluster import DBSCAN

model = DBSCAN(eps=0.5, min_samples=5)
labels = model.fit_predict(X)
# label = -1 means noise/outlier
```
- No need to specify K
- Finds arbitrary shapes
- Robust to outliers
- Sensitive to eps parameter

### HDBSCAN (better DBSCAN)
```python
import hdbscan

model = hdbscan.HDBSCAN(min_cluster_size=10)
labels = model.fit_predict(X)
```
- Auto-selects density threshold
- Hierarchical
- Good for varied cluster densities

### Choosing K

#### Elbow Method
```python
from sklearn.cluster import KMeans
inertias = []
for k in range(1, 20):
    kmeans = KMeans(n_clusters=k).fit(X)
    inertias.append(kmeans.inertia_)
# Plot, find "elbow"
```

#### Silhouette Score
```python
from sklearn.metrics import silhouette_score

scores = []
for k in range(2, 20):
    labels = KMeans(n_clusters=k).fit_predict(X)
    scores.append(silhouette_score(X, labels))
# Higher = better separation
```

---

## 7. Recommender Systems (overview, deep dive in 04)

### 3 Main Approaches

#### Collaborative Filtering
"Users who liked X also liked Y"
- Matrix factorization (SVD, ALS)
- Doesn't need item features

#### Content-Based
"Recommend similar items based on features"
- TF-IDF on item descriptions
- Embeddings + cosine similarity

#### Hybrid
- Combine both
- Most production systems use this

#### Modern: Deep Learning Recommenders
- Neural Collaborative Filtering
- Two-Tower models
- Sequence models (BERT4Rec, SASRec)

---

## 8. Reinforcement Learning (for ML, not LLM)

### When to Use RL

- Sequential decisions matter
- Delayed reward
- Environment can be simulated

### Use Cases
- Recommendation (long-term engagement)
- Ad bidding (auction dynamics)
- Inventory management
- Trading
- Robotics

### Avoid RL when
- Have labeled data (use supervised)
- One-shot decision (use classification)
- Cannot simulate environment safely

(Deep dive in `04_Recommender_RL.md`)

---

## 9. Model Selection by Problem Size

### Small Data (< 1000 rows)
```
Prefer simple models:
  Linear/Logistic Regression
  Random Forest
  Naive Bayes

Avoid: deep learning, complex GBM
Risk: overfitting
Strategy: heavy cross-validation, regularization
```

### Medium Data (1K - 100K)
```
Sweet spot for:
  XGBoost / LightGBM (tabular)
  Random Forest
  Logistic Regression with feature engineering
  
Some DL viable for: text, image with pre-trained
```

### Large Data (> 100K - 10M)
```
GBM still strong
DL becomes competitive
Distributed training optional
Consider: cost vs accuracy trade-off
```

### Very Large (> 10M)
```
Distributed training (Spark MLlib, Dask)
DL approaches work well
Foundation models + fine-tune
Streaming considerations
```

---

## 10. Imbalanced Data Handling

### Detection

```python
class_counts = y.value_counts()
imbalance_ratio = class_counts.max() / class_counts.min()
# > 10 = imbalanced
# > 100 = severe imbalance
```

### Strategies

#### Strategy 1: Class Weights
```python
# Automatically inverse-frequency weighted
model = XGBClassifier(
    scale_pos_weight=neg_count / pos_count
)
```

#### Strategy 2: Resampling
```python
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

# SMOTE: synthetic minority samples
smote = SMOTE(sampling_strategy=0.3)
X_res, y_res = smote.fit_resample(X, y)

# Combine: SMOTE then undersample majority
from imblearn.combine import SMOTETomek
sm = SMOTETomek()
X_res, y_res = sm.fit_resample(X, y)
```

#### Strategy 3: Different Threshold
```python
# Don't use 0.5 default
preds = model.predict_proba(X)[:, 1]
optimal_threshold = find_threshold_max_f1(preds, y_true)
classifications = preds > optimal_threshold
```

#### Strategy 4: Different Metric
```
Don't optimize accuracy on imbalanced data!

Use:
  - Precision-Recall AUC
  - F1 score
  - Recall at fixed precision
```

---

## 11. Hyperparameter Tuning

### Tools (2026)

#### Optuna (recommended)
```python
import optuna

def objective(trial):
    params = {
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'n_estimators': trial.suggest_int('n_estimators', 100, 2000),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
    }
    
    model = XGBClassifier(**params)
    score = cross_val_score(model, X, y, cv=5, scoring='roc_auc').mean()
    return score

study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=100, n_jobs=4)

print(study.best_params)
```

**Why Optuna**:
- Bayesian optimization (smarter than grid)
- Pruning (stop bad trials early)
- Distributed parallel
- Integration with MLflow

#### Other Tools
- Hyperopt (older, less features)
- Ray Tune (distributed at scale)
- Vertex AI Vizier (managed)
- Weights & Biases Sweeps

### Search Spaces

```python
# Grid search (exhaustive)
{'max_depth': [3, 5, 7]}

# Random search (better for high-dim)
trial.suggest_int('max_depth', 3, 10)

# Bayesian (smartest)
# Auto-managed by Optuna

# Log-scale (for learning rate, etc.)
trial.suggest_float('lr', 0.0001, 0.1, log=True)
```

---

## 12. Interpretation & Explainability

### SHAP (most popular)

```python
import shap

# Train model
model = XGBClassifier().fit(X_train, y_train)

# Compute SHAP values
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Global importance
shap.summary_plot(shap_values, X_test)

# Single prediction
shap.force_plot(
    explainer.expected_value,
    shap_values[0],
    X_test.iloc[0]
)
```

### LIME (local explanation)

```python
from lime.lime_tabular import LimeTabularExplainer

explainer = LimeTabularExplainer(
    X_train.values,
    feature_names=X_train.columns,
    mode='classification'
)

exp = explainer.explain_instance(
    X_test.iloc[0].values,
    model.predict_proba,
    num_features=10
)
exp.show_in_notebook()
```

### When to Use

| Need | Tool |
|---|---|
| Global feature importance | SHAP summary |
| Single prediction explanation | SHAP force / LIME |
| Counterfactual ("what if X changed") | DiCE |
| Model-agnostic | LIME, SHAP KernelExplainer |
| Tree models | SHAP TreeExplainer (fast) |
| Deep learning | SHAP DeepExplainer, integrated gradients |

---

## 13. Common Pitfalls

### Pitfall 1: Random Train/Test Split for Time Series
```python
# Bad: leaks future
X_train, X_test = train_test_split(X, random_state=42)

# Good: temporal split
train = df[df.date < '2026-04-01']
val = df[(df.date >= '2026-04-01') & (df.date < '2026-05-01')]
test = df[df.date >= '2026-05-01']
```

### Pitfall 2: Data Leakage from Future
```python
# Bad: using current value as feature
df['avg_30d'] = df.amount.rolling(30).mean()  # includes today

# Good: shift first
df['avg_30d'] = df.amount.shift(1).rolling(30).mean()  # only past
```

### Pitfall 3: Target Leakage
```
Feature 'closed_at' in churn prediction
  → only filled for churned customers!
  → model learns "if closed_at exists → churn"
  → useless in production
```

### Pitfall 4: Ignoring Imbalanced Classes
```python
# 99% class 0, 1% class 1
# Accuracy 99% by predicting all 0!
# Use ROC-AUC or PR-AUC
```

### Pitfall 5: Hyperparameter Tuning on Test Set
```
Bad:
  Tune on test → optimistic estimate
  Real performance worse

Good:
  Tune on validation
  Final eval on holdout test (touch once!)
```

### Pitfall 6: Forgetting Production Constraints
```
Model uses 100 features (90% from FS)
Production: only 50 features available in real-time
→ either reduce features or ensure FS sync
```

### Pitfall 7: Ignoring Latency Requirements
```
Train: optimal model 95% accuracy, 10s inference
Production needs: < 100ms

Solutions:
  Distillation (small model from big one)
  Quantization (int8 instead of float32)
  Pruning (remove unused weights)
  Simpler model (XGBoost with depth=4)
```

---

## 14. Cheat Sheet

### Q: "Default tabular ML algorithm คืออะไร?"
> "LightGBM (fastest) หรือ XGBoost (most ecosystem support)
> CatBoost ถ้ามี categorical features เยอะ
> เริ่มจาก default hyperparams + early stopping = baseline solid"

### Q: "DL ดีกว่า GBM สำหรับ tabular มั้ย?"
> "ส่วนใหญ่ NO — GBM ยัง win ~80% ของ Kaggle tabular
> DL competitive ต้อง > 1M rows + complex interactions
> ปี 2026: TabNet, FT-Transformer ดีขึ้น แต่ก็ยังไม่ default"

### Q: "Time series — ARIMA, Prophet, หรือ DL?"
> "5 series, business data: Prophet (easy)
> Many series + accuracy: XGBoost + lag features
> Foundation models (Chronos, TimesFM) สำหรับ zero-shot
> DL (TFT) สำหรับ complex multivariate"

### Q: "Imbalanced data ทำยังไง?"
> "1. ห้ามใช้ accuracy
> 2. ใช้ class_weight หรือ scale_pos_weight
> 3. SMOTE สำหรับ minority oversample
> 4. ปรับ threshold ไม่ใช่ 0.5 default
> 5. Optimize PR-AUC หรือ F1"

### Q: "Tune hyperparameters ยังไง?"
> "Optuna (Bayesian) > Random Search > Grid Search
> Use early stopping + pruning
> Search log-scale สำหรับ learning rate, regularization
> 100 trials > 10 trials, but diminishing returns after 200"

---

## Sources

- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [LightGBM Documentation](https://lightgbm.readthedocs.io/)
- [CatBoost Documentation](https://catboost.ai/docs)
- [Prophet Forecasting](https://facebook.github.io/prophet/)
- [Optuna Documentation](https://optuna.org/)
- [SHAP Documentation](https://shap.readthedocs.io/)
- [Kaggle Competition Solutions](https://www.kaggle.com/competitions)
