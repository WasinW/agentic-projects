# Recommender Systems & Reinforcement Learning — Deep Dive

> Two-tower, sequence models, RL for recommendations
> Production-grade rec systems ปี 2026

---

## 1. Recommender System Overview

### Stages of a Production Rec System

```
1. CANDIDATE GENERATION (millions → thousands)
   "Find candidates user might like"
   Methods: Collaborative filtering, content-based, embeddings

2. RANKING (thousands → tens)
   "Score each candidate precisely"
   Methods: GBDT, deep learning, two-tower

3. RE-RANKING (tens → final ordering)
   "Apply business rules, diversity, freshness"
   Methods: rules + ML mix

4. POST-PROCESSING
   "Promotion, ad insertion, deduplication"
```

### Why Multi-Stage

- Latency: cannot rank millions
- Cost: complex ranking expensive per item
- Different objectives: recall vs precision

---

## 2. Collaborative Filtering

### Matrix Factorization

```
Rating matrix:        Decompose into:
   item1 item2 item3      User factors (M×K)
u1   5     ?    3         × Item factors (K×N)
u2   ?     4    ?    →    
u3   2     5    ?         

Predict missing ratings = U × I^T
```

### ALS (Alternating Least Squares)

```python
from pyspark.ml.recommendation import ALS

als = ALS(
    rank=10,                # K dimensions
    maxIter=10,
    regParam=0.1,
    userCol="user_id",
    itemCol="item_id",
    ratingCol="rating",
    coldStartStrategy="drop"
)
model = als.fit(df)

# Predict
predictions = model.transform(test_df)

# Top-N for user
user_recs = model.recommendForAllUsers(10)
```

### Pros & Cons

✅ No item features needed
✅ Captures latent preferences
❌ Cold start (new user, new item)
❌ No interpretability
❌ Computational: scaling to 100M items hard

### When to Use

- Have explicit ratings or strong implicit signals
- Items don't change rapidly
- Need baseline recommender quickly

---

## 3. Content-Based Filtering

### Idea

Recommend items similar to those user liked

```
User profile = avg(features of items they liked)
For each candidate item:
  Score = similarity(user_profile, item_features)
Top-N by score
```

### Implementation

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Item features (text)
tfidf = TfidfVectorizer()
item_features = tfidf.fit_transform(items['description'])

# User profile
user_likes = ratings[ratings.user_id == user_id]
liked_features = item_features[user_likes.item_id]
user_profile = liked_features.mean(axis=0)

# Score all items
scores = cosine_similarity(user_profile, item_features)
top_n = scores.argsort()[-10:]
```

### Pros & Cons

✅ Handles cold-start items (new items with features)
✅ Interpretable (features known)
❌ Cannot recommend novel item types
❌ Limited diversity (always similar)

---

## 4. Two-Tower Models (modern, scalable)

### Architecture

```
USER FEATURES                ITEM FEATURES
(age, history, etc.)         (category, price, etc.)
       │                            │
       ▼                            ▼
   USER TOWER                  ITEM TOWER
   (Neural net)                (Neural net)
       │                            │
       ▼                            ▼
   USER EMBEDDING              ITEM EMBEDDING
   (e.g., 64-dim)              (e.g., 64-dim)
       │                            │
       └────────── DOT PRODUCT ─────┘
                       │
                  SIMILARITY SCORE
```

### Why Two-Tower

- **Train**: predict (user, item) → 1 if interacted
- **Serve**: pre-compute item embeddings, only compute user at inference
- **Retrieve**: ANN search → fast top-K

```python
# PyTorch sketch
class TwoTowerModel(nn.Module):
    def __init__(self, num_user_features, num_item_features, embed_dim=64):
        super().__init__()
        self.user_tower = nn.Sequential(
            nn.Linear(num_user_features, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, embed_dim)
        )
        self.item_tower = nn.Sequential(...)  # similar
    
    def forward(self, user_feats, item_feats):
        user_emb = self.user_tower(user_feats)
        item_emb = self.item_tower(item_feats)
        return (user_emb * item_emb).sum(dim=1)
```

### Negative Sampling

Critical for training:
- In-batch negatives (other items in batch as negatives)
- Random negatives (random sample)
- Hard negatives (hard examples - looked at but didn't click)

### Inference Pipeline

```
1. Pre-compute item embeddings (batch, daily refresh)
2. Index in vector DB (Pinecone, FAISS)
3. At request:
   user_emb = user_tower(user_features)  # ~10ms
   top_K = vector_db.search(user_emb)    # ~5ms
   return top_K
```

---

## 5. Sequence Models (Behavior-Aware)

### Why Sequential

User behavior changes over time — sequential models capture this

### Examples

#### GRU4Rec (Recurrent)
```
User session: [item1, item2, item3, ...]
Predict: next item likely to be?

GRU/LSTM processes sequence
Final state → recommendation
```

#### SASRec (Self-Attention)

```
Use Transformer to model sequences
Better than RNN at capturing long-range
```

#### BERT4Rec

```
Like BERT but for items
Mask random items in sequence
Predict masked items
Bidirectional context
```

### Modern: Transformer Recommenders

```python
class SequentialRecommender(nn.Module):
    def __init__(self, num_items, embed_dim, num_heads, num_layers):
        super().__init__()
        self.item_embedding = nn.Embedding(num_items + 1, embed_dim)
        self.position_embedding = nn.Embedding(max_seq_len, embed_dim)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
    
    def forward(self, item_seq):
        item_emb = self.item_embedding(item_seq)
        pos = torch.arange(item_seq.size(1)).unsqueeze(0)
        pos_emb = self.position_embedding(pos)
        
        x = item_emb + pos_emb
        x = self.transformer(x)
        # Use last position for next-item prediction
        return x[:, -1, :] @ self.item_embedding.weight.t()
```

---

## 6. Ranking Models (Stage 2)

### Pointwise: Predict relevance score

```python
# Each (user, item) → score independently
# Train with: target = clicked / converted / liked

model = XGBClassifier()
model.fit(user_item_features, clicks)

# At serve: score each candidate
scores = model.predict_proba(candidate_features)[:, 1]
top_K = candidates[np.argsort(scores)[-10:]]
```

### Pairwise: Learn relative ordering

```python
# Train on (user, item_better, item_worse) triples
# Loss: model(item_better) > model(item_worse)

# LightGBM ranker
import lightgbm as lgb

train_data = lgb.Dataset(
    X, y,
    group=group_sizes  # number of items per query/user
)
params = {'objective': 'lambdarank', 'metric': 'ndcg'}
model = lgb.train(params, train_data, num_boost_round=100)
```

### Listwise: Optimize whole list

```python
# Optimize NDCG / MAP directly
# Tools: TF-Ranking, LambdaMART
```

### Multi-Objective Ranking

Real systems balance multiple objectives:
- Click probability
- Watch time
- Engagement
- Diversity
- Fairness

```python
# Weighted combination
final_score = (
    w_click * p_click +
    w_engagement * p_engagement +
    w_diversity * diversity_score +
    w_freshness * recency_score
)
```

---

## 7. Cold Start Problem

### Cold User
```
New user, no history → cannot recommend

Solutions:
- Onboarding survey ("which genres?")
- Popular items globally
- Content-based using demographics
- Implicit signal (browser, device)
- Bootstrap from similar users
```

### Cold Item
```
New item, no interactions → cannot retrieve

Solutions:
- Content-based (use item features)
- Promote in random sampling
- Use item embedding from features (not from interactions)
- Two-tower model with item features in tower
```

### Hybrid Approach (production)

```python
def get_recommendations(user_id):
    user_history = get_history(user_id)
    
    if len(user_history) < 5:
        # Cold user
        return popular_items() + demographic_recs(user_id)
    elif len(user_history) < 20:
        # Warm user
        return content_based_recs(user_id) + cf_recs(user_id)
    else:
        # Established user
        return two_tower_recs(user_id) + sequential_recs(user_id)
```

---

## 8. Evaluation Metrics

### Offline Metrics

#### Precision@K / Recall@K
```python
def precision_at_k(actual, predicted, k):
    pred_k = predicted[:k]
    relevant = set(actual) & set(pred_k)
    return len(relevant) / k

def recall_at_k(actual, predicted, k):
    pred_k = predicted[:k]
    relevant = set(actual) & set(pred_k)
    return len(relevant) / len(actual)
```

#### MAP (Mean Average Precision)
```python
def average_precision(actual, predicted):
    score = 0.0
    num_hits = 0.0
    for i, p in enumerate(predicted):
        if p in actual:
            num_hits += 1
            score += num_hits / (i + 1)
    return score / len(actual)
```

#### NDCG (Normalized Discounted Cumulative Gain)
```python
def dcg(scores):
    return sum(s / np.log2(i + 2) for i, s in enumerate(scores))

def ndcg(actual_scores, predicted_order):
    actual_scored = [actual_scores.get(item, 0) for item in predicted_order]
    ideal_scored = sorted(actual_scores.values(), reverse=True)
    return dcg(actual_scored) / dcg(ideal_scored)
```

#### Coverage
```
% of items ever recommended
% of users who got recommendations
```

#### Diversity
```
Pairwise dissimilarity within recommended list
```

### Online Metrics (A/B Testing)

- **CTR** (Click-Through Rate)
- **Conversion Rate**
- **Engagement** (watch time, likes)
- **Retention** (daily/weekly active)
- **Revenue per user**

**Critical**: offline ≠ online — always A/B test

---

## 9. Reinforcement Learning for Recommendations

### Why RL

Standard supervised learning: predict next click
RL: optimize **long-term value**

```
Standard: maximize P(click_now)
RL: maximize Σ rewards over time (engagement, retention)
```

### Use Cases

- **YouTube/Netflix recommendation**: optimize watch time
- **News feed**: long-term engagement vs clickbait trade-off
- **E-commerce**: lifetime value vs immediate purchase

### Multi-Armed Bandits (simpler than RL)

```
Each "arm" = item to recommend
Each pull = show item, observe reward (click/no click)
Goal: identify best arms while exploring

Algorithms:
- Epsilon-greedy: exploit best, explore with prob ε
- UCB (Upper Confidence Bound): explore uncertain
- Thompson Sampling: bayesian, sample from posterior
```

### Contextual Bandits

```python
# Each request has context (user features)
# Different best arm per context

class ContextualBandit:
    def __init__(self, n_arms, n_features):
        self.models = [LinearRegression() for _ in range(n_arms)]
    
    def select_arm(self, context, exploration=0.1):
        # Predict reward for each arm
        scores = [m.predict(context) for m in self.models]
        # Add exploration bonus (UCB style)
        scores = [s + exploration * uncertainty(m) for s, m in zip(scores, self.models)]
        return np.argmax(scores)
    
    def update(self, arm, context, reward):
        self.models[arm].partial_fit(context, reward)
```

### Full RL (Q-Learning, PPO)

```python
# State: user context + history
# Action: which item to recommend
# Reward: click + downstream engagement
# Policy: maps state → action

# Off-policy training with logged data
# Caution: distribution shift, biased logs
```

### Production RL Challenges

1. **Off-policy evaluation**: how to test without deploying?
2. **Bias in logs**: only see rewards for items shown
3. **Counterfactual**: would this user have liked something else?
4. **Safety**: bad action = lose users

### Practical Approach (2026)

Most production = **hybrid**:
- Supervised models for relevance score
- Bandits for explore/exploit
- RL for long-term reranking
- Heavy guardrails

---

## 10. Diversity & Filter Bubble

### Problem

Pure relevance ranking → echo chamber, boring feeds

### Diversification Strategies

#### MMR (Maximal Marginal Relevance)
```python
def mmr_select(candidates, k, lambda_=0.7):
    selected = []
    while len(selected) < k:
        scores = []
        for c in candidates:
            relevance = c.score
            similarity_to_selected = max(
                cosine_sim(c.embedding, s.embedding) for s in selected
            ) if selected else 0
            mmr_score = lambda_ * relevance - (1-lambda_) * similarity_to_selected
            scores.append(mmr_score)
        
        best_idx = np.argmax(scores)
        selected.append(candidates[best_idx])
        candidates.pop(best_idx)
    return selected
```

#### Topic Diversification
```python
# Ensure varied categories
def diverse_select(candidates, k, max_per_category=3):
    selected = []
    category_counts = defaultdict(int)
    
    for c in sorted(candidates, key=lambda x: -x.score):
        if category_counts[c.category] < max_per_category:
            selected.append(c)
            category_counts[c.category] += 1
            if len(selected) >= k:
                break
    return selected
```

#### Determinantal Point Process (DPP)
- Mathematically optimal diversity
- Used at Hulu, Spotify

---

## 11. Production Architecture

### Real-Time Recommendation API

```
[User request]
      ↓
[Online Feature Store] (user features, last-N items)
      ↓
[Candidate Generation]
  - Two-tower retrieval (vector DB)
  - Recent items
  - Trending
      ↓ (combines candidates)
[Ranking Model] (XGBoost / DNN)
      ↓
[Re-ranking]
  - Diversity
  - Business rules
  - Personalization weights
      ↓
[Response] ~50-200ms total
```

### Latency Budget Example

```
Total: 200ms
├─ Auth + parsing: 5ms
├─ Online FS lookup: 30ms
├─ Candidate retrieval: 30ms (vector search)
├─ Feature joining: 20ms
├─ Ranking model: 50ms (50 candidates × 1ms)
├─ Re-ranking: 30ms
└─ Response serialization: 35ms
```

### Update Frequency

```
Item embeddings: daily batch (Spark + two-tower)
User embeddings: at request time (real-time)
Item index: hourly (for new items)
Ranking model: weekly (retrain on fresh data)
Bandit weights: continuous (online updates)
```

---

## 12. Common Recommender Pitfalls

### Pitfall 1: Train-Serve Skew
```
Training: features as-of historical time
Serving: features at inference time
→ different distributions

Fix: Feature store with point-in-time joins
```

### Pitfall 2: Position Bias
```
Items shown at top get more clicks
   → model learns "top items are best"
   → not actually true!

Fix: 
- Inverse propensity scoring
- Position as feature (then zero at inference)
- Counterfactual reasoning
```

### Pitfall 3: Selection Bias
```
Only see rewards for items shown
→ never learn about unshown items

Fix:
- Exploration (bandit / random injection)
- Off-policy evaluation
```

### Pitfall 4: Popularity Bias
```
Popular items always recommended
→ less popular items never get chance
→ harder cold start

Fix:
- Diversification
- Re-rank with popularity penalty
- Long-tail boost
```

### Pitfall 5: Filter Bubble
```
Recommend only what user liked
→ user trapped in narrow content
→ engagement drops over time

Fix:
- Explicit diversity term
- Periodic injection of novel items
- Topic balance
```

---

## 13. Tools & Frameworks

| Tool | Use case |
|---|---|
| **Spark MLlib ALS** | Classic CF, large-scale |
| **TensorFlow Recommenders** | Two-tower, sequential |
| **PyTorch + custom** | Research, custom architectures |
| **LightFM** | Hybrid CF+content, simpler |
| **Implicit** | Implicit feedback ALS |
| **Surprise** | Quick prototyping |
| **Vespa** | Search + recommendation engine |
| **Pinecone/Qdrant** | Vector retrieval |

---

## 14. Cheat Sheet

### Q: "เริ่ม recommender system จากไหน?"
> "1. Baseline: popularity / co-occurrence
> 2. ALS หรือ matrix factorization
> 3. Two-tower with features (production scalable)
> 4. Add ranking model (XGBoost on user-item features)
> 5. Add diversity + business rules
> 6. A/B test, iterate"

### Q: "Two-tower vs end-to-end DNN?"
> "Two-tower: pre-compute item embeddings → fast retrieval
> End-to-end: more expressive but slower at serve
> ปี 2026 production = two-tower for retrieval + DNN/GBM for ranking"

### Q: "Cold start แก้ยังไง?"
> "Cold user: popular + demographic + onboarding survey
> Cold item: content-based features in two-tower
> Hybrid approach: switch strategy by data density"

### Q: "Bandit vs RL?"
> "Bandit: simpler, single-step decisions
> RL: long-term value, multi-step
> ส่วนใหญ่ start with bandit, RL only when long-term metric matters"

### Q: "Position bias แก้ยังไง?"
> "Inverse Propensity Scoring (IPS): weight by P(shown at position)
> Or: position as feature, zero at serve
> Or: explicit click models accounting for position"

---

## Sources

- [TensorFlow Recommenders](https://www.tensorflow.org/recommenders)
- [PyTorch Recommendation Systems](https://github.com/pytorch/torchrec)
- [BERT4Rec Paper](https://arxiv.org/abs/1904.06690)
- [SASRec Paper](https://arxiv.org/abs/1808.09781)
- [Two-Tower Models at Google](https://research.google/pubs/sampling-bias-corrected-neural-modeling-for-large-corpus-item-recommendations/)
- [Spotify Engineering Blog](https://engineering.atspotify.com/category/data-science-and-machine-learning/)
- [YouTube Recommendation Paper (Deep Neural Networks)](https://research.google/pubs/deep-neural-networks-for-youtube-recommendations/)
