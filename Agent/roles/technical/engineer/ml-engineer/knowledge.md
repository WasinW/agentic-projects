# ML Engineer — Comprehensive Knowledge

> Deep reference for the ml-engineer subagent.

---

## 1. Foundations

### What an ML Engineer does

Productionizes **machine learning** models. Owns the full lifecycle from data → model → serving → monitoring → retraining.

- Implements + operates training pipelines
- Builds feature engineering pipelines
- Manages experiment tracking + model registry
- Deploys models (batch, online, streaming)
- Sets up monitoring + drift detection
- Implements retraining loops

### MLE vs Data Scientist vs AI Engineer

- **Data Scientist** — research-y; explores hypotheses, builds prototype models
- **ML Engineer** — productionizes; reliability, scale, latency
- **AI Engineer** — usually means GenAI / LLM applications (different stack)
- **MLOps Engineer** — operates ML systems in production (overlap with MLE)

In smaller teams, one person is all of these. In bigger teams, they specialize.

### MLE skill profile

- Strong software engineering (>50% of the job)
- Solid ML fundamentals (don't need PhD)
- Data engineering literacy
- Cloud infrastructure
- Statistics + distributions intuition

---

## 2. Mental Models / Decision Frameworks

### Build vs Buy / Use existing

For each model decision:
- **Foundation model API** — most ML tasks today have a foundation model that does it well enough
- **Custom model** — when foundation models can't, or volume/cost forces self-train
- **Open source pretrained** — fine-tune for your data
- **From scratch** — rare; only if novel problem with novel data

### The 4 model lifecycles

| Type | Update cadence | Pattern |
|---|---|---|
| **Static** | Rarely | Train once, deploy, forget (uncommon) |
| **Periodic** | Daily/weekly | Scheduled retrain pipeline |
| **Triggered** | On drift / performance | Monitor → trigger retrain |
| **Online** | Continuous | Online learning (rare in practice) |

Most production ML = Periodic. Triggered is the modern ideal but hard.

### Training-Serving Skew

The classic ML production bug: features computed differently at training vs serving.

Causes:
- Different code paths (training: Python; serving: Go service)
- Different data freshness (training: T-1; serving: now)
- Different aggregations / windows
- Different missing-value handling

Solutions:
- **Feature store** — single source of truth, same computation everywhere
- **Skew testing** — produce serving outputs at training time, compare
- **Shadow deployment** — run new model in parallel, compare outputs

### Feature engineering decisions

- **Where to compute** — offline (warehouse/lake) vs online (request time)
- **Storage** — feature store with online + offline sync
- **Freshness** — stale-but-cheap vs fresh-but-expensive
- **Point-in-time correctness** — avoid leakage in training data

### Inference patterns

| Pattern | Latency | Use |
|---|---|---|
| **Batch** | hours | Bulk scoring (overnight) |
| **Async** | seconds | Background scoring (queue) |
| **Online sync** | <100ms | User-facing API |
| **Streaming** | <1s | Per-event inference (fraud, ad serving) |
| **Edge** | <10ms | On-device (mobile, IoT) |

Most teams pick one or two. Don't build all.

### Model + data versioning

Every production model needs version of:
- Training code
- Training data snapshot
- Feature definitions
- Hyperparameters
- Random seed
- Environment (dependencies)
- Eval metrics

Without all of this, you can't reproduce. MLflow, Weights & Biases, custom solutions provide it.

### Model serving complexity ladder

```
1. Pickle file + scripts          (notebook era)
2. REST API in a container        (basic prod)
3. Model registry + auto-deploy   (CI/CD for models)
4. Multi-model serving            (model server)
5. Shadow / canary deployment     (safer rollouts)
6. Multi-armed bandit / A/B       (online optimization)
7. Personalized routing           (model per cohort)
```

Most teams should be at level 3-4. Higher levels only with clear ROI.

---

## 3. Standard Practices

### Reference architecture: Modern ML Platform

```
Data Sources
    ↓
[Feature Pipelines: Spark / dbt / streaming]
    ↓
[Feature Store: offline + online]
    ↓
[Training Pipeline: schedule or trigger]
    ├─ [Experiment tracking: MLflow / W&B]
    ├─ [Model artifacts → Registry]
    └─ [Evaluation suite]
    ↓
[Deployment]
    ├─ [Batch inference job]
    ├─ [Online API: Triton / TFServing / Vertex / SageMaker]
    └─ [Streaming embedded: Flink / Beam UDF]
    ↓
[Monitoring]
    ├─ [Performance metrics — labeled feedback]
    ├─ [Drift detection — input + output]
    ├─ [Latency / errors]
    └─ [Cost]
    ↓
[Retraining trigger]
```

### Feature store usage

- Offline (training): point-in-time joins for historical features
- Online (serving): low-latency lookup by entity key
- Both backed by same definition (no skew)

Tools:
- **Feast** (OSS) — most popular
- **Tecton** — commercial, mature
- **Vertex AI Feature Store / SageMaker Feature Store / Databricks Feature Store** — cloud-native
- **Custom** — many teams build their own

### Experiment tracking patterns

For every training run, log:
- Code version (git SHA)
- Data snapshot (Iceberg snapshot, dataset hash)
- Hyperparameters
- Hardware / compute spec
- Metrics (per epoch + final)
- Artifacts (model, plots, confusion matrix)
- Notes / tags

Tools: MLflow (de facto OSS), Weights & Biases (premium), Neptune, Comet.

### Hyperparameter tuning

| Method | When |
|---|---|
| **Grid search** | Small space, fast model |
| **Random search** | Better default than grid |
| **Bayesian optimization** | Expensive trials (Optuna, Hyperopt) |
| **Population-based** | Long training runs |
| **AutoML** | Bake-off across many configs (AutoGluon, etc.) |

Optuna is the modern default for most teams.

### Training pipeline patterns

```
Validate input → Sample / split → Train → Evaluate → Compare to baseline → Register if better
```

Always compare to current production. Never deploy a "worse" model unless deliberate (e.g., simpler / cheaper).

### Eval methodology

- **Hold-out test set** — never touch during dev
- **Cross-validation** — when data is small
- **Time-based split** — for temporal data (mandatory)
- **Stratified** — for imbalanced classes
- **Multi-metric** — don't optimize a single metric blindly
- **Slice metrics** — per cohort / segment / region

### Model deployment patterns

| Pattern | Use |
|---|---|
| **Blue/green** | Quick rollback, traffic switch |
| **Canary** | Gradual rollout (5% → 50% → 100%) |
| **Shadow** | Run new model parallel, log only |
| **A/B** | Compare new vs current with stats test |
| **Multi-armed bandit** | Continuous optimization across variants |

### Monitoring layers

1. **Operational** — uptime, latency, errors
2. **Data drift** — input distributions shift
3. **Concept drift** — input-output relationship shifts
4. **Performance** — accuracy on labeled feedback (delayed)
5. **Business** — revenue, conversion (slowest)

A model can degrade silently for weeks before performance drops are visible. Drift detection is your early warning.

### Retraining triggers

- **Schedule** — every N days/weeks
- **Drift** — PSI, KL-divergence on input distribution
- **Performance** — accuracy below threshold
- **Volume** — when new data accumulates
- **Manual** — analyst notices issue

Combine: schedule + drift + manual override.

---

## 4. Tools Landscape (2026)

### ML platforms (managed)
- **Vertex AI** (GCP) — strong end-to-end
- **SageMaker** (AWS) — mature, complex
- **Databricks ML** — best with Spark stack
- **Azure ML** — strong enterprise integration

### Experiment tracking + registry
- **MLflow** — open source standard
- **Weights & Biases** — best UX, paid
- **Neptune** — alternative to W&B
- **Comet** — alternative to W&B

### Pipeline orchestration
- **Kubeflow Pipelines** — K8s-native
- **Vertex AI Pipelines** — KFP managed on GCP
- **SageMaker Pipelines** — AWS-native
- **Airflow + custom** — flexible but DIY
- **Metaflow** (Netflix OSS) — Python-first
- **ZenML** — modular ML pipelines
- **Dagster** — data-asset model also fits ML

### Feature stores
- **Feast** — OSS, growing
- **Tecton** — commercial, mature
- **Vertex Feature Store / SageMaker Feature Store / Databricks**

### Model serving
- **NVIDIA Triton** — high-performance, multi-framework
- **TensorFlow Serving** — TF-focused
- **TorchServe** — PyTorch-focused
- **Seldon Core** — K8s-native
- **BentoML** — Python-friendly wrappers
- **KServe** — K8s-native
- **vLLM** — LLM inference

### Hyperparameter tuning
- **Optuna** — default OSS
- **Hyperopt** — older
- **Ray Tune** — distributed
- **Cloud-native** (Vizier, SageMaker HPO)

### Monitoring + drift
- **Evidently** — open source, strong
- **WhyLabs** — commercial
- **Arize / Fiddler** — commercial
- **Monte Carlo for ML** — extending DQ to ML

### Frameworks
- **scikit-learn** — classical ML
- **XGBoost / LightGBM / CatBoost** — tabular SOTA
- **PyTorch** — deep learning default
- **TensorFlow / Keras** — still common in production
- **HuggingFace Transformers** — NLP / LLM
- **JAX / Flax** — research, increasing

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Notebook → production | No tests, no versioning | Modularize; use pipelines |
| No baseline | Can't tell if model adds value | Always benchmark vs simple baseline |
| Single train/test split | Overfits to that split | Cross-validation or time-split |
| Test set leakage | Optimistic eval | Strict separation; never touch test set |
| No experiment tracking | Lost work, can't reproduce | MLflow from day 1 |
| Manual deployment | Slow, error-prone | CI/CD with model registry |
| Same model for all users | One-size-fits-none | Segment / personalize if data supports |
| No drift monitoring | Silent degradation | Drift detection always on |
| Random retraining | Wastes compute | Trigger-based |
| Ignoring training-serving skew | Production performs worse than eval | Feature store + skew testing |
| All-or-nothing rollout | High blast radius | Canary / shadow first |
| Optimizing a single metric | Misses real-world cost | Multi-metric + slice metrics |
| One giant model | Hard to update | Smaller models if business logic naturally splits |

---

## 6. Advanced / Expert Topics

### Feature store advanced

- **Point-in-time joins** — train without leakage
- **Online-offline consistency** — same definitions, sync mechanism
- **Feature freshness SLA** — per-feature
- **Feature monitoring** — drift per feature
- **Feature lineage** — what data → feature → model

### Feature store online-offline sync mechanisms

**What.** A feature store keeps two physical stores: an **offline** store (warehouse/lake — BigQuery, Snowflake, Iceberg/Delta) for point-in-time-correct training data, and an **online** store (low-latency KV — Redis, DynamoDB, Bigtable, Aerospike) for sub-10ms serving lookups by entity key. Both must serve the *same* feature definition or you get training-serving skew.

**Why it matters in prod.** The offline store optimizes for correctness (no future leakage via point-in-time joins); the online store optimizes for freshness + latency (latest value per entity). These goals conflict — sync is where skew silently creeps in.

**Sync patterns + when each:**

- **Batch materialization** — scheduled job reads offline → writes latest values online (`feast materialize`, Tecton scheduled materialization). Use for batch/daily features. Freshness bounded by job cadence.
- **Streaming ingestion / push** — features computed in Flink/Spark Structured Streaming and pushed straight to online (Feast **Push API**, Tecton stream features) with the same record also landing offline. Use for fresh signals (fraud, session, real-time aggregates) — seconds-fresh.
- **On-demand transforms** — computed at request time from raw request payload + fetched features. Use for features only knowable at inference (e.g. distance from request lat/long). The transform code must be shared offline+online or you create *on-demand skew*.
- **Dual-write vs CDC** — dual-write (job writes both stores) is simplest but risks the two diverging on partial failure; CDC (online store fed from a log/offline change stream) reduces duplication + staleness (Tecton uses CDC). Lean CDC/single-source-of-truth as scale grows.
- **TTLs** — online entries expire so stale features aren't served past their freshness SLA; offline retains full history.

**Anti-patterns (online-offline skew):** different aggregation windows or null handling between the two stores; materializing offline with `event_timestamp` but serving online with wall-clock now; on-demand transform reimplemented in the serving language. Always run skew tests (materialize offline → diff against online for the same entity/time).

**Tools (2025-2026):** **Feast** (OSS) — materialize + Push API, you bring the engines. **Tecton** — managed compute, CDC, streaming; **acquired by Databricks Aug 2025**, folding into Databricks Feature Store's Declarative Feature APIs (managed batch+streaming pipelines). **Vertex / SageMaker Feature Store** — cloud-native, managed sync. Iceberg/Delta increasingly the offline backbone.

Refs: [Feast Push source](https://docs.feast.dev/reference/data-sources/push) · [Online-Offline Feature Skew (Hopsworks)](https://www.hopsworks.ai/dictionary/online-offline-feature-skew)

### Online learning

When the world changes fast enough that batch retraining isn't fast enough:
- **Streaming SGD** — model updates per event
- **Concept-drift-aware** — algorithms detect drift, adapt
- **Bandit / RL** — explore + exploit

Rare in practice — usually unjustified complexity.

### Model compression

- **Quantization** — fp32 → fp16 → int8 → int4
- **Pruning** — remove low-importance weights
- **Distillation** — small model learns from big model
- **LoRA / adapters** — small fine-tunes layered on frozen base

Important for edge deployment + cost optimization.

### Distributed training

- **Data parallel** — same model, different shards (most common)
- **Model parallel** — model split across devices (very large models)
- **Pipeline parallel** — layers across devices, mini-batch pipeline
- **FSDP / DeepSpeed / Megatron** — frameworks

For LLMs / very large models. Most ML doesn't need this.

### A/B testing for models

- **Random user assignment** — gold standard
- **Geo-split** — when randomization hard
- **Time-split** — least reliable but easy
- **Multi-armed bandit** — for continuous optimization
- **Pre-registration** — avoid p-hacking

Statistical significance ≠ business significance. Compare to expected revenue impact.

### Causal inference vs predictive ML

Predictive: "Will this user churn?"
Causal: "Will this intervention reduce churn?"

Causal needs different methodology (uplift modeling, A/B tests, propensity scoring). Most teams confuse the two.

### Time-series specifics

- **Trend + seasonality + residual** — classical decomposition
- **Stationarity testing** — many models require it
- **Cross-validation** — must respect time order (no leak from future)
- **Modern**: Prophet, NeuralProphet, Temporal Fusion Transformers, Chronos (foundation model)

### Recommender systems

- **Collaborative filtering** — user-item interaction patterns
- **Content-based** — item features
- **Hybrid** — both
- **Two-tower** — user + item embeddings, dot product
- **Sequential** — RNN/Transformer for behavior sequences
- **Multi-armed bandit** for ranking

### Ranking systems

- **Pointwise** — predict relevance per item
- **Pairwise** — predict which of two is better
- **Listwise** — predict ranking directly
- **LambdaMART / XGBoost ranking** — common
- **Learning to rank** — academic foundation

### Fairness + bias

- **Disparate impact** — outcome rates by group
- **Equalized odds** — error rates by group
- **Counterfactual fairness** — would outcome change if group changed?

No single fairness metric is "right". Pick the relevant one for the use case.

---

## 7. References

### Books
- **Designing Machine Learning Systems** — Chip Huyen (production focus)
- **Machine Learning Engineering** — Burkov (practical)
- **Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow** — Géron
- **Reliable Machine Learning** — Chen, Tay (reliability + scale)

### Papers / posts
- **Hidden Technical Debt in ML Systems** — Sculley et al. (Google, 2015)
- **MLOps at Scale** — Google paper
- **Rules of ML** — Martin Zinkevich (Google)
- **Feature Stores for ML** — Tecton blog series

### Communities
- **MLOps Community** — Slack, podcast, conference
- **Papers With Code** — research
- **Towards Data Science** — practical writing
- **r/MachineLearning** (Reddit)

### Courses (still valuable)
- **fast.ai** — practical deep learning
- **Andrew Ng's ML courses** — foundations
- **Stanford CS231n, CS229** — fundamentals

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| AI Architect | "Here's the design — what's the implementation plan?" |
| Data Engineer | "Need this feature pipeline" |
| Data Scientist | "Productionize this experiment" |
| ML Ops | "Drift response + retraining strategy" |
| Software Engineer | "Integrate model API into product" |
| Product | "What's the model latency + accuracy trade-off?" |
| Governance | "Bias audit, model cards" |

---

*ML engineering = software engineering + statistics + data engineering. Be good at all three.*
