# Feature Engineering — Deep Dive

> Windowing, encoding, embeddings, target encoding, generation
> "Better features > better algorithm" — true 80% of the time

---

## 1. Why Feature Engineering Matters

### The Truth in 2026

Even with foundation models, for tabular ML:
- **90%** of model improvement = feature engineering
- **10%** = algorithm tuning

LLMs change this for unstructured data, but tabular still feature-driven

### Categories of Features

```
Raw features:           directly from source (age, amount)
Derived features:       computed (age_squared, log_amount)
Aggregated features:    over window (avg_amount_30d)
Interaction features:   combine (age × income)
Encoded features:       categorical → numeric
Embedded features:      learned representations
External features:      enrichment (weather, holidays)
```

---

## 2. Numerical Feature Transformations

### Scaling

```python
# Standardization (z-score)
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
# Result: mean=0, std=1

# Min-Max
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))

# Robust (handles outliers)
from sklearn.preprocessing import RobustScaler
scaler = RobustScaler()
# Uses median + IQR
```

**When to use which**:
- Z-score: most ML algorithms expect this
- Min-Max: neural networks, when you know range
- Robust: data with outliers
- **No scaling needed**: tree-based models (XGBoost, LightGBM)

### Distribution Transformations

```python
# Log transform (for skewed data)
df['log_amount'] = np.log1p(df['amount'])  # log(1+x), handles 0

# Box-Cox (auto-detect best power)
from scipy.stats import boxcox
df['amount_bc'], lambda_ = boxcox(df['amount'] + 1)

# Yeo-Johnson (handles negatives)
from sklearn.preprocessing import PowerTransformer
pt = PowerTransformer(method='yeo-johnson')
df['amount_yj'] = pt.fit_transform(df[['amount']])

# Quantile (uniform/normal output)
from sklearn.preprocessing import QuantileTransformer
qt = QuantileTransformer(output_distribution='normal')
df['amount_q'] = qt.fit_transform(df[['amount']])
```

### Binning

```python
# Equal-width
df['age_bin'] = pd.cut(df['age'], bins=[0, 18, 30, 50, 100],
                       labels=['kid', 'young', 'adult', 'senior'])

# Equal-frequency (quantile)
df['amount_bin'] = pd.qcut(df['amount'], q=4, labels=['low', 'mid_low', 'mid_high', 'high'])

# Custom domain bins
df['risk_bucket'] = pd.cut(df['credit_score'],
    bins=[0, 580, 670, 740, 800, 850],
    labels=['poor', 'fair', 'good', 'very_good', 'excellent'])
```

**When to use binning**:
- Linear models (capture non-linear via bins)
- Robustness to outliers
- Match business logic (credit score buckets)

### Creating New Numerical Features

```python
# Ratios
df['debt_to_income'] = df['debt'] / df['income']

# Differences
df['account_age_days'] = (df['today'] - df['account_open_date']).dt.days

# Powers / interactions
df['age_squared'] = df['age'] ** 2
df['age_x_income'] = df['age'] * df['income']

# Rolling statistics
df['amount_rolling_avg_7d'] = df.groupby('user_id')['amount'].transform(
    lambda x: x.rolling(7, min_periods=1).mean()
)
```

---

## 3. Categorical Encoding

### Low Cardinality (< 100 unique values)

#### One-Hot Encoding
```python
pd.get_dummies(df['country'])  # creates N columns

# Or sklearn
from sklearn.preprocessing import OneHotEncoder
ohe = OneHotEncoder(handle_unknown='ignore')
encoded = ohe.fit_transform(df[['country']])
```
**Pros**: simple, no ordering implied
**Cons**: explosion if many categories

#### Label Encoding
```python
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
df['country_id'] = le.fit_transform(df['country'])
```
**Use only**: tree-based models (where ordering doesn't imply meaning)

### High Cardinality (>100 unique values)

#### Target Encoding (Mean Encoding)
```python
# Encode by mean of target per category
target_map = df.groupby('city')['target'].mean()
df['city_encoded'] = df['city'].map(target_map)
```

**Critical: Avoid Leakage**
```python
# ❌ Bad: leakage
df['city_te'] = df.groupby('city')['target'].transform('mean')
# Uses target including current row!

# ✅ Good: out-of-fold
from sklearn.model_selection import KFold

def target_encode_oof(train, test, col, target):
    train_oof = pd.Series(index=train.index, dtype=float)
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    for train_idx, val_idx in kf.split(train):
        target_map = train.iloc[train_idx].groupby(col)[target].mean()
        train_oof.iloc[val_idx] = train.iloc[val_idx][col].map(target_map)
    
    # Test uses full train mean
    test_map = train.groupby(col)[target].mean()
    test_encoded = test[col].map(test_map)
    
    return train_oof, test_encoded
```

#### Frequency Encoding
```python
# Encode by how often category appears
freq_map = df['city'].value_counts(normalize=True)
df['city_freq'] = df['city'].map(freq_map)
```

#### Hash Encoding (high cardinality)
```python
import hashlib

def hash_encode(value, num_buckets=100):
    return int(hashlib.md5(str(value).encode()).hexdigest(), 16) % num_buckets

df['city_hash'] = df['city'].apply(lambda x: hash_encode(x, 100))
```
**Pros**: bounded dimensionality, no fitting
**Cons**: collisions

#### Embedding (learned)
```python
# Use neural network / categorical encoder
import torch.nn as nn

class CategoryEmbedder(nn.Module):
    def __init__(self, num_categories, embed_dim=8):
        super().__init__()
        self.embedding = nn.Embedding(num_categories, embed_dim)
    
    def forward(self, x):
        return self.embedding(x)
```

#### CatBoost Native
```python
# CatBoost handles categories natively (best for high cardinality)
from catboost import CatBoostClassifier

model = CatBoostClassifier(cat_features=['city', 'country', 'merchant'])
model.fit(X, y)
# CatBoost does ordered target encoding internally
```

---

## 4. Datetime Features

### Time Decomposition

```python
def add_datetime_features(df, col='timestamp'):
    df[f'{col}_year'] = df[col].dt.year
    df[f'{col}_month'] = df[col].dt.month
    df[f'{col}_day'] = df[col].dt.day
    df[f'{col}_dayofweek'] = df[col].dt.dayofweek
    df[f'{col}_hour'] = df[col].dt.hour
    df[f'{col}_quarter'] = df[col].dt.quarter
    df[f'{col}_is_weekend'] = df[col].dt.dayofweek >= 5
    df[f'{col}_is_month_start'] = df[col].dt.is_month_start
    df[f'{col}_is_month_end'] = df[col].dt.is_month_end
    df[f'{col}_dayofyear'] = df[col].dt.dayofyear
    return df
```

### Cyclic Encoding (for periodic time)

```python
# Hour of day is cyclic: 23 close to 0
# Linear encoding wrong: 23 - 0 = 23 (large)
# Cyclic encoding correct: same point on circle

df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)

# Day of year
df['day_sin'] = np.sin(2 * np.pi * df['dayofyear'] / 365)
df['day_cos'] = np.cos(2 * np.pi * df['dayofyear'] / 365)
```

### Time Since / Time Until

```python
df['days_since_signup'] = (df['event_time'] - df['signup_time']).dt.days
df['days_until_expiry'] = (df['expiry'] - df['today']).dt.days
df['seconds_since_last_event'] = df.groupby('user_id')['timestamp'].diff().dt.total_seconds()
```

### Holiday & Calendar Features

```python
import holidays

th_holidays = holidays.Thailand()
df['is_holiday'] = df['date'].apply(lambda x: x in th_holidays)
df['days_to_next_holiday'] = df['date'].apply(
    lambda x: min((d - x).days for d in th_holidays.keys() if d > x)
)
df['is_payday'] = df['date'].dt.day.isin([15, 30, 31])  # last/mid month
```

---

## 5. Window Features (Time Series)

### Lag Features

```python
# Same column, previous value(s)
df['amount_lag1'] = df.groupby('user_id')['amount'].shift(1)
df['amount_lag7'] = df.groupby('user_id')['amount'].shift(7)
df['amount_lag30'] = df.groupby('user_id')['amount'].shift(30)
```

### Rolling Statistics

```python
# Rolling mean (last N events, excluding current)
df['amount_avg_7d'] = (
    df.groupby('user_id')['amount']
    .shift(1)  # exclude current!
    .rolling(window=7, min_periods=1)
    .mean()
)

# Multiple stats
for window in [7, 30, 90]:
    grp = df.groupby('user_id')['amount'].shift(1).rolling(window, min_periods=1)
    df[f'amount_mean_{window}d'] = grp.mean()
    df[f'amount_std_{window}d'] = grp.std()
    df[f'amount_max_{window}d'] = grp.max()
    df[f'amount_min_{window}d'] = grp.min()
```

### Expanding Statistics (lifetime)

```python
df['amount_lifetime_avg'] = (
    df.groupby('user_id')['amount']
    .shift(1)
    .expanding()
    .mean()
)

df['transaction_count_to_date'] = (
    df.groupby('user_id').cumcount()
)
```

### Time-Based Aggregations (custom windows)

```python
# Last 30 days excluding last 7 days
def amount_30d_excluding_recent(df, user_id, current_time):
    user_data = df[df.user_id == user_id]
    window = user_data[
        (user_data.timestamp < current_time - pd.Timedelta(days=7)) &
        (user_data.timestamp >= current_time - pd.Timedelta(days=30))
    ]
    return window.amount.mean()

# Or use Beam/Spark windows for production
```

---

## 6. Aggregation Features

### Group-Level Statistics

```python
# Per user
user_stats = df.groupby('user_id').agg({
    'amount': ['mean', 'std', 'sum', 'min', 'max', 'count'],
    'category': lambda x: x.nunique(),  # diversity
    'timestamp': lambda x: (x.max() - x.min()).days,  # active period
})

user_stats.columns = ['_'.join(col) for col in user_stats.columns]
df = df.merge(user_stats, on='user_id', how='left')
```

### Cross-Group Features

```python
# Amount relative to user's average
df['amount_vs_user_avg'] = df['amount'] / df.groupby('user_id')['amount'].transform('mean')

# Amount percentile within user's history
df['amount_user_percentile'] = (
    df.groupby('user_id')['amount']
    .rank(pct=True)
)

# Amount vs category average
df['amount_vs_category_avg'] = (
    df['amount'] / df.groupby('category')['amount'].transform('mean')
)
```

---

## 7. Interaction Features

### Manual Interactions

```python
# Multiply
df['age_x_income'] = df['age'] * df['income']

# Divide (ratios)
df['debt_to_income'] = df['debt'] / df['income']

# Compare
df['amount_above_avg'] = (df['amount'] > df.groupby('user_id')['amount'].transform('mean')).astype(int)
```

### Polynomial Features

```python
from sklearn.preprocessing import PolynomialFeatures

# All combinations up to degree 2
poly = PolynomialFeatures(degree=2, interaction_only=False)
poly_features = poly.fit_transform(df[['age', 'income']])
# Generates: age, income, age², age×income, income²
```

### Feature Crosses (categorical)

```python
df['country_x_category'] = df['country'] + '_' + df['category']
# Then encode this combined column
```

### Tree Path Features

```python
# Use shallow tree to discover interactions
from sklearn.tree import DecisionTreeClassifier

tree = DecisionTreeClassifier(max_depth=4)
tree.fit(X, y)

# Each leaf = unique combination of conditions
df['tree_leaf'] = tree.apply(X)
# Use as categorical feature
```

---

## 8. Text Features

### Classical Bag-of-Words

```python
from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer(
    max_features=1000,
    ngram_range=(1, 2),  # unigrams + bigrams
    stop_words='english',
    min_df=5
)
X_text = tfidf.fit_transform(df['description'])
```

### Length Features

```python
df['desc_length'] = df['description'].str.len()
df['desc_word_count'] = df['description'].str.split().str.len()
df['desc_avg_word_length'] = df['desc_length'] / df['desc_word_count']
df['desc_unique_word_ratio'] = df['description'].apply(
    lambda x: len(set(x.split())) / len(x.split()) if x else 0
)
```

### Domain Features

```python
# Email features
df['email_domain'] = df['email'].str.split('@').str[1]
df['is_personal_email'] = df['email_domain'].isin(['gmail.com', 'yahoo.com', 'hotmail.com'])

# Phone features
df['phone_country'] = df['phone'].str[:3]
df['phone_length'] = df['phone'].str.len()
```

### Modern: Pre-trained Embeddings

```python
# Sentence transformers
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(df['description'].tolist())
# 384-dim vectors as features

# Use as features (with PCA if too many dims)
```

---

## 9. Image Features

### Pre-trained Embeddings

```python
import torch
from torchvision import models, transforms

# Use ResNet as feature extractor
resnet = models.resnet50(pretrained=True)
resnet.eval()
# Remove final layer
resnet = torch.nn.Sequential(*list(resnet.children())[:-1])

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

with torch.no_grad():
    features = resnet(transform(img).unsqueeze(0)).flatten()
# 2048-dim feature vector
```

### Modern: CLIP / DINOv2

```python
from transformers import CLIPModel, CLIPProcessor

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

inputs = processor(images=img, return_tensors="pt")
features = model.get_image_features(**inputs)
# 512-dim, more semantic than ResNet
```

---

## 10. Feature Selection

### Why Select

- Reduce overfitting
- Speed up training
- Better interpretability
- Lower production cost (less FS lookups)

### Statistical Methods

```python
# Variance threshold (drop near-constant)
from sklearn.feature_selection import VarianceThreshold
vt = VarianceThreshold(threshold=0.01)
X_selected = vt.fit_transform(X)

# Correlation threshold (drop highly correlated)
def remove_correlated(df, threshold=0.95):
    corr = df.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    to_drop = [col for col in upper.columns if any(upper[col] > threshold)]
    return df.drop(columns=to_drop)
```

### Model-Based Selection

```python
# Tree feature importance
model = XGBClassifier()
model.fit(X, y)
importances = pd.Series(model.feature_importances_, index=X.columns)
top_features = importances.nlargest(50).index

# Recursive Feature Elimination
from sklearn.feature_selection import RFE
rfe = RFE(estimator=LogisticRegression(), n_features_to_select=20)
rfe.fit(X, y)
selected = X.columns[rfe.support_]

# SHAP-based (more accurate)
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)
shap_importance = np.abs(shap_values).mean(axis=0)
```

### Boruta (relevant features only)

```python
from boruta import BorutaPy

forest = RandomForestClassifier(n_jobs=-1)
boruta = BorutaPy(forest, n_estimators='auto')
boruta.fit(X.values, y.values)

# Confirmed features
selected = X.columns[boruta.support_].tolist()
# Tentative features (might add)
tentative = X.columns[boruta.support_weak_].tolist()
```

---

## 11. Feature Generation Tools

### Featuretools (Deep Feature Synthesis)

```python
import featuretools as ft

# Define entity set
es = ft.EntitySet(id='customers')
es.add_dataframe(dataframe_name='customers', dataframe=customers_df, index='customer_id')
es.add_dataframe(dataframe_name='transactions', dataframe=trans_df, index='transaction_id')
es.add_relationship('customers', 'customer_id', 'transactions', 'customer_id')

# Generate features automatically
feature_matrix, feature_defs = ft.dfs(
    entityset=es,
    target_dataframe_name='customers',
    agg_primitives=['mean', 'sum', 'std', 'count'],
    trans_primitives=['day', 'month', 'weekday'],
    max_depth=2
)
```

### TSFresh (time series features)

```python
from tsfresh import extract_features

# Extracts ~700 time series features
features = extract_features(
    df,
    column_id='user_id',
    column_sort='timestamp',
    column_value='amount'
)
# Includes: mean, autocorrelation, FFT, peaks, etc.
```

---

## 12. Production Feature Pipeline

### Pattern: Feature Function Library

```python
# features/window.py
def avg_amount_window(df, user_id, current_time, window_days):
    """Compute avg amount in window before current_time.
    
    Args:
        df: full transactions
        user_id: target user
        current_time: cutoff (inclusive of past, exclusive of present)
        window_days: window size
    
    Returns:
        float, avg amount or NaN if no data
    """
    window_start = current_time - timedelta(days=window_days)
    window = df[
        (df.user_id == user_id) &
        (df.timestamp < current_time) &
        (df.timestamp >= window_start)
    ]
    return window.amount.mean()

# This same function used in:
# 1. Training (offline, point-in-time)
# 2. Serving (online, lookup from FS)
# 3. Backfill (re-run on history)
```

### Pattern: Feature Store Definition (Feast)

```python
@feature_view(
    entities=["user_id"],
    ttl=timedelta(days=30),
    source=transactions_source
)
def user_features(transactions):
    return transactions.groupby('user_id').agg(
        avg_amount_7d=("amount", "mean"),
        count_7d=("amount", "count"),
    )
```

### Pattern: Streaming Feature

```python
# Beam pipeline
from apache_beam import window

(events
    | 'Window' >> beam.WindowInto(window.SlidingWindows(size=300, period=60))
    | 'KeyByUser' >> beam.WithKeys(lambda e: e.user_id)
    | 'Sum' >> beam.combiners.Sum.PerKey()
    | 'WriteToBT' >> WriteToBigtable(table='user_features')
)
```

---

## 13. Pitfalls

### Pitfall 1: Target Leakage
```
❌ closed_at as feature for churn → only filled for churned
❌ ip_geolocation derived after fraud detection
✅ Only features available BEFORE prediction time
```

### Pitfall 2: Train-Serve Skew
```
❌ Training: pandas pd.qcut for binning
   Serving: different bin edges
   → silent skew

✅ Save bin edges with model, apply same in serving
```

### Pitfall 3: Forgetting Time Order
```
❌ Random shuffle for time series
✅ Time-based split, point-in-time joins
```

### Pitfall 4: Feature Explosion
```
❌ Generate 10000 features, hope model picks
   → overfits to noise

✅ Domain-driven generation + selection
```

### Pitfall 5: Hardcoded Magic Values
```
❌ df['high_value'] = df['amount'] > 10000  # arbitrary
✅ Use percentile or domain-driven threshold
```

### Pitfall 6: Not Handling Missing
```
Different missingness types:
- Missing Completely at Random (MCAR): drop or impute
- Missing at Random (MAR): impute by group
- Missing Not at Random (MNAR): missingness IS feature
   → df['amount_missing'] = df['amount'].isna()
```

---

## 14. Cheat Sheet

### Q: "ทำ feature engineering ที่ไหนก่อน?"
> "1. Domain knowledge (talk to business)
> 2. EDA — distributions, correlations, missingness
> 3. Feature ideas → quick prototype
> 4. Validate (no leakage, no skew)
> 5. Iterate"

### Q: "Tree models ต้อง encode categorical มั้ย?"
> "ต้อง — XGBoost รับเฉพาะ numeric
> Use: Label encoding (XGBoost), Target encoding (high cardinality), CatBoost native (best for many cats)
> ห้าม: One-hot encoding ใน XGBoost (overfits)"

### Q: "Window features ทำตอน training ทำยังไงไม่ leak?"
> "1. Sort by time
> 2. Use shift(1) ก่อน rolling — exclude current row
> 3. Group by entity (user_id)
> 4. Use feature store with point-in-time joins for production
> 5. Test: feature ที่ time T ใช้แค่ data < T เท่านั้น"

### Q: "Feature selection ทำตอนไหน?"
> "หลังจากสร้าง all features
> Step 1: drop near-constant + highly correlated (statistical)
> Step 2: model-based (tree importance, SHAP)
> Step 3: validate on holdout
> เริ่ม > 100 features → reduce to 30-50 = production-friendly"

---

## Sources

- [Featuretools Documentation](https://featuretools.alteryx.com/)
- [TSFresh Documentation](https://tsfresh.readthedocs.io/)
- [scikit-learn Feature Engineering](https://scikit-learn.org/stable/modules/preprocessing.html)
- [CatBoost Categorical Features](https://catboost.ai/en/docs/concepts/categorical-features)
- [Feature Engineering for Machine Learning](https://www.oreilly.com/library/view/feature-engineering-for/9781491953235/)
