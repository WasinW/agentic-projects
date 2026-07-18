# ML Ops — Comprehensive Knowledge

> Deep reference for the ml-ops subagent.
> Operating ML models in production: deployment, monitoring, drift response, retraining.

---

## 1. Foundations

### What MLOps does

Operates ML models reliably in production. Owns: deployment, monitoring, drift detection, retraining triggers, on-call for ML systems.

### MLOps vs ML Engineer vs DevOps

- **ML Engineer** — implements training + serving
- **MLOps** — operates after deployment
- **DevOps** — general infrastructure

In small teams, one person. In large teams, specialization. Modern trend: MLOps embedded with ML Engineers.

### Why MLOps is different from DevOps

DevOps handles code. MLOps handles code + data + models — three sources of change.

A model can silently degrade with no code change (data drift). DevOps practices don't catch this.

### The model lifecycle

```
Train → Register → Validate → Deploy → Monitor → Retrain → Repeat
```

MLOps owns Deploy + Monitor + Retrain trigger.

---

## 2. Mental Models / Decision Frameworks

### Silent degradation is the primary failure mode

Code crashes loudly. Models degrade silently:
- Wrong answers, but they look right
- Performance drops on a subgroup before overall
- Drift creeps in over weeks

Monitoring catches what code can't.

### Drift taxonomy

- **Feature drift** — input distribution changes (more young users now)
- **Concept drift** — input-output relationship changes (recession changes spending patterns)
- **Label drift** — target distribution changes (fraud rates spike)
- **Performance drift** — accuracy drops on labeled data
- **Training-serving skew** — features computed differently in prod (a bug)

Different causes → different monitoring → different responses.

### Deployment patterns + risk

| Pattern | Risk | When |
|---|---|---|
| **Blue/green** | Low | Quick rollback needed |
| **Canary** (5 → 50 → 100%) | Lower | Standard for model upgrades |
| **Shadow** | Lowest | New model, untested |
| **A/B** | Statistical rigor | Compare for biz impact |
| **Multi-armed bandit** | Continuous opt | Many variants competing |

Default for major model change: **shadow → canary → full**.

### Rollback strategy

- Always version-pin in production (don't serve `@production`)
- Rollback = config change to previous version
- Test rollback in staging before launching
- Decide pre-commit: what triggers rollback?

### Retraining trigger logic

```
Time-based (every N days/weeks) — baseline
Performance-based — when accuracy drops > threshold
Drift-based — when input distribution shifts
Data-based — when N new labeled samples accumulate
Manual — analyst override

Choose one + manual override.
```

### Champion-Challenger

- Champion: current production
- Challenger: candidate to replace
- Run in parallel, compare
- Promote challenger if it wins on defined metric

Useful pattern for continuous model improvement.

### Performance monitoring with delayed labels

Ground truth often delayed:
- Fraud: labels weeks later
- Churn: months later
- Conversion: minutes-hours

Strategies:
- Proxy metrics (user feedback signals)
- Confidence-based monitoring (drop in model confidence)
- Distribution checks (output predictions changing)
- Backfilled performance reports

---

## 3. Standard Practices

### Monitoring layers

**Operational**
- Latency (p50, p95, p99)
- Throughput
- Errors
- Resource use

**Data**
- Input feature distributions (vs training)
- Missing values, null rates
- Out-of-range values

**Model**
- Prediction distribution
- Confidence
- Class balance
- Top features used (SHAP)

**Performance**
- Accuracy / AUC / F1 (when labels available)
- Slice metrics (per cohort)
- Calibration

**Business**
- Conversion, revenue, retention
- Final source of truth for value

### Drift metrics

- **PSI (Population Stability Index)** — most common
  - <0.1: stable
  - 0.1-0.2: slight shift, monitor
  - 0.2+: significant, investigate
- **KL divergence** — information-theoretic
- **Wasserstein distance** — distribution distance
- **KS test** — non-parametric

PSI is most widely used in industry; easy to interpret.

### Feature monitoring

Per feature in production:
- Distribution stats (mean, std, quantiles)
- Missing rate
- Drift score vs baseline
- Correlation with target (when labels available)

Alert when drift exceeds threshold or missing rate spikes.

### Model registry hygiene

- Every prod model: version pinned, owner, training data snapshot
- Lifecycle stages: dev → staging → prod → archived
- Approval gate before prod promotion
- Audit log of stage transitions

### Production readiness checklist

Before launching a model:
- [ ] Eval on holdout meets SLA
- [ ] Fairness audit passed
- [ ] Latency benchmark
- [ ] Load test
- [ ] Failure mode analysis
- [ ] Rollback procedure
- [ ] Monitoring + alerting setup
- [ ] Runbook
- [ ] Owner + on-call
- [ ] Documentation (model card)

### Continuous Training (CT) pipeline

```
Trigger →
  Validate input data quality →
  Generate features →
  Train new candidate →
  Evaluate vs current prod →
  Approval gate (auto if metric improves, else manual) →
  Shadow deploy →
  Canary →
  Full →
  Monitor → Repeat
```

### Feature store hygiene (ops side)

- Monitor feature freshness
- Detect schema changes
- Track online/offline sync lag
- Alert on missing features at inference

### LLM-specific ops

For GenAI / LLM systems:
- Latency monitoring (TTFT, tokens/sec)
- Token cost tracking per request
- Quality metrics (RAGAS, LLM-judge)
- Hallucination rate
- Guardrail trip rate
- Cost optimization (caching, routing)

---

## 4. Tools Landscape (2026)

### MLOps platforms
- **MLflow** — tracking + registry standard
- **Vertex AI / SageMaker / Azure ML / Databricks ML** — managed
- **Kubeflow** — K8s-native
- **Weights & Biases** — premium tracking
- **Neptune / Comet** — alternatives

### Model serving
- **Triton** — NVIDIA, multi-framework
- **TensorFlow Serving / TorchServe**
- **Seldon / KServe** — K8s-native
- **BentoML**
- **vLLM** — LLM-specific

### Model monitoring
- **Evidently** — OSS
- **WhyLabs** — commercial
- **Arize AI / Fiddler** — commercial
- **Vertex AI Model Monitoring** — GCP
- **SageMaker Model Monitor** — AWS

### Feature stores
- **Feast** — OSS
- **Tecton** — commercial
- **Cloud-native** (Vertex / SageMaker / Databricks)

### LLM observability
- **Langfuse** — OSS
- **LangSmith** — commercial
- **Helicone**
- **Arize Phoenix**

### Pipeline orchestration
- **Airflow / Dagster / Prefect**
- **Kubeflow Pipelines**
- **Vertex AI Pipelines / SageMaker Pipelines**
- **Metaflow** (Netflix OSS)

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| No monitoring | Silent degradation | Monitor multiple layers |
| Only one metric | Misses important shifts | Multi-metric + slice |
| Drift alerts to email blackhole | Ignored | Routing + escalation |
| No rollback procedure | Long MTTR | Pre-tested rollback |
| Manual retrain only | Slow response to drift | Trigger-based |
| Direct prod deploy | Risky | Shadow → canary → full |
| Pickle in S3, no registry | Lost provenance | Model registry |
| Same eval metric in dev + prod | Real-world differs | Production-realistic eval |
| No model card | Can't explain decisions | Mandatory model cards |
| Train-test leakage | Optimistic eval | Strict separation |
| Skipping fairness | Discrimination risk | Audit + slice metrics |
| No labels in prod | Can't measure performance | Active labeling process |

---

## 6. Advanced / Expert Topics

### CI/CD/CT (Continuous Training)

Three loops:
- **CI**: code changes → run tests
- **CD**: code passes → deploy
- **CT**: new data + drift → retrain → deploy

Level 2 MLOps (Google) = all three automated.

### Shadow deployment

New model receives all prod traffic, but predictions logged only (not served).
- Compare outputs to current model
- Eval on real distribution
- Find issues before exposing users
- Pre-launch verification

Best for: major model changes.

### Multi-armed bandit serving

Continuously explore multiple model variants + reward winners:
- Thompson sampling, UCB, contextual bandits
- Bridges A/B test + production
- Useful for personalization, ranking

Complex. Use when justified by clear continuous improvement need.

### Federated learning

Train without centralizing data:
- Edge devices contribute model updates
- Privacy-preserving (data stays local)
- Common in healthcare, mobile

Operational complexity is high; only when privacy mandates it.

### Online learning

Model updates per event:
- River, Vowpal Wabbit
- Useful for highly dynamic environments
- Risk: catastrophic forgetting

Rare in practice; usually unjustified vs frequent batch retrain.

### Model serving optimizations

- Quantization (fp32 → fp16 → int8)
- Distillation (small model from big)
- Batching (group requests)
- Caching (idempotent inputs)
- ONNX runtime for cross-framework

### A/B test infrastructure

For models:
- Bucketing (consistent user assignment)
- Holdout group (control)
- Pre-registration of metrics
- Statistical test framework
- Avoid peeking

### Cost optimization

- Right-size inference instances
- GPU sharing (Triton, MIG)
- Auto-scaling (with cold-start mitigation)
- Quantization for cheaper inference
- LLM: smart routing (cheap for cheap queries)

---

## 7. References

### Books
- **Designing Machine Learning Systems** — Chip Huyen
- **Reliable Machine Learning** — Chen, Tay
- **Machine Learning Engineering for Production (MLOps)** — DeepLearning.AI specialization

### Frameworks
- **Google's MLOps Levels** (0, 1, 2) — well-known framework
- **MLflow Model Lifecycle**
- **CRISP-DM** (older but still useful)

### Communities
- **MLOps Community** (Slack, podcast, conferences)
- **DBT + MLOps overlap** community

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| ML Engineer | "Model degraded — debug + retrain plan" |
| AI Architect | "Long-term reliability + cost" |
| Data Engineer | "Feature pipeline failed" |
| Data Ops | "Shared infra, capacity" |
| Product | "Quality vs latency vs cost trade-offs" |
| Governance | "Model cards, audit trail, bias" |

---

*MLOps = SRE + statistics + ML knowledge. Silent failures are the enemy.*
