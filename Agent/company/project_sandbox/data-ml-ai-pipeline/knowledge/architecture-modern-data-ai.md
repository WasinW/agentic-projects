# Modern Data + AI Architecture

> PRIMARY reference. The "what goes where" map: how data engineering evolved, the extended medallion layering, the data-type taxonomy, and how the four Ops disciplines converge. Framed for an AWS + Databricks + Delta shop.

---

## 1. Evolution of Data Engineering (context, not trivia)

| Era | Years | Defining tech | DE role |
|---|---|---|---|
| 1. Hadoop/Spark | 2010–2015 | HDFS, Hive, MapReduce, Spark; Teradata/Oracle DW | "Data plumber" — move A→B |
| 2. Cloud DW | 2016–2020 | Redshift/BigQuery/Snowflake, dbt, Airflow; "Modern Data Stack" | Analytics Engineer emerges |
| 3. Lakehouse + Streaming | 2021–2023 | Delta/Iceberg/Hudi, Kafka+Flink, Medallion, Data Mesh | Platform Engineer |
| 4. AI-Native | 2024–now | Vector DBs mainstream, RAG standard, LLM tooling, agents in workflows | DE + AI hybrid |
| 5. Autonomous | 2026+ | Self-healing pipelines, agent-driven ops, NL interfaces | AI Platform Architect |

**Why the three pipelines (Data / ML / AI) converged onto one platform team:** LLMs need retrieval (= DE work); agents' tools are data APIs; production AI needs the same orchestration/retries/monitoring; shared compute+storage+observability; one source of truth for data, features, and embeddings.

For an AIA DE this means: the Bronze→Gold lakehouse you own is also the substrate any future ML/feature/AI work sits on. Build it clean and the AI layers are additive, not a rewrite.

---

## 2. The Extended Medallion

Classic medallion stops at Gold. The AI-native extension adds two analytical layers (Platinum, Diamond) plus an operational Agent-State layer and a feedback loop.

```
Bronze ──► Silver ──► Gold ──► Platinum ──► Diamond
(Raw)     (Clean)   (Business) (Features)  (AI-Ready)
                                  │            │
                          ┌───────┴────────────┴────────┐
                          ▼        ▼          ▼          ▼
                     [ML Models][Vector  ][Agent     ][Application
                               [Store    ][State      ][Layer]
                          └────────┬───────┴───────────┘
                                   ▼
                          [Observability + Feedback Loop]
                                   └──── feeds back to Bronze ───►
```

Naming note: the raw pipeline scripts in this repo use **Raw / Persist / Curated** as the physical table tiers, which map to **Bronze / Silver / Gold**. Treat them as synonyms — see `streaming-batch-patterns.md`.

### Layer definitions

| Layer | Purpose | Key properties | Typical tools (AWS/Databricks) |
|---|---|---|---|
| **Bronze (Raw)** | Direct copy from source | Immutable, append-only, original schema preserved, audit trail | Delta append, S3, Auto Loader / MSK |
| **Silver (Clean)** | Validated + conformed | Deduplicated, schema-normalized, DQ-passed, joinable | Delta, schema enforcement, DLQ |
| **Gold (Business)** | Business-ready | Aggregated, denormalized, KPI-ready, query-optimized | Delta, Z-order/cluster, partitioned |
| **Platinum (Features)** — *new* | Pre-computed ML features | Point-in-time correct, online+offline serving | Databricks Feature Store (Feast/Tecton elsewhere) |
| **Diamond (AI-Ready)** — *new* | Embeddings + multimodal + KG | Chunked, tagged, embedded for retrieval | Databricks Vector Search; pgvector/Qdrant/OpenSearch |
| **Agent-State** — *new* | Agent memory + logs | Short-term (conversation), long-term (prefs), tool logs, checkpoints | Redis/DynamoDB, Postgres, LangGraph checkpointer |
| **Application** | Serving | REST/gRPC, ML endpoints, RAG/agent endpoints | FastAPI, SageMaker/Bedrock endpoints, Modal |
| **Observability + Feedback** | Close the loop | User signals, traces, errors/latency/cost → back to Bronze | CloudWatch/Datadog/Grafana; Phoenix/Langfuse for AI |

For AIA today the work is concentrated in **Bronze → Silver → Gold** on Delta. Platinum/Diamond/Agent-State are where the role grows; they are listed so the lakehouse is designed not to block them.

### Data-type taxonomy (what the platform must carry)

- **Structured:** relational, time-series, geospatial, graph.
- **Semi-structured:** JSON/NoSQL, events/logs, XML.
- **Unstructured (growing emphasis):** text (docs, emails, chat), images, audio, video, PDFs, code.
- **Derived:** embeddings, ML features, predictions, generated content, agent memory.

In insurance specifically the unstructured tier (policy PDFs, claims notes, call transcripts) is exactly what later feeds the Diamond/RAG layer — capturing it cleanly in Bronze pays off twice.

---

## 3. The 4-Ops Convergence

```
DevOps + DataOps + MLOps + AIOps = "Modern Data + AI Ops"
```

| Discipline | Owns | Tools |
|---|---|---|
| **DevOps** (foundation) | IaC, CI/CD, containers, base observability | Terraform/CDK, GitHub Actions, Datadog/CloudWatch |
| **DataOps** | Pipeline orchestration, DQ monitoring, lineage, schema evolution | Airflow, dbt, Soda/Great Expectations, Monte Carlo |
| **MLOps** | Experiment tracking, model registry, feature store, serving, drift, A/B, retraining | MLflow, Databricks ML, SageMaker |
| **AIOps / LLMOps** *(newest)* | Prompt mgmt, token-cost tracking, LLM/RAG eval, agent observability, hallucination + safety | LangSmith, Phoenix, Helicone, Langfuse |

Goal of convergence: one observability plane (e.g. Datadog/Grafana + an AI tracer) carrying traces from agents → data → infra. For AIA, DataOps (Airflow + DQ + lineage) is the immediate concern; the rest is the growth path.

---

## 4. Governance layers (reference)

- **Catalog & discovery:** Unity Catalog (Databricks-native), DataHub/OpenMetadata; business glossary; domain ownership.
- **Lineage:** Unity Catalog lineage, OpenLineage/Marquez, dbt lineage; cross-system.
- **Access control:** RBAC/ABAC, row-level security, column masking (PII) — material for insurance/PII.
- **Quality:** Great Expectations / Soda; Monte Carlo / Bigeye for observability.
- **Privacy & compliance:** PDPA/GDPR mapping, PII detection, retention policies, audit logs.
- **AI governance (new):** model-card registry, prompt registry, eval history, bias/fairness + hallucination tracking, agent tool-usage audit.

PII handling and compliance are the domain of the governance consultant — escalate strategic decisions there; this doc only flags where they attach to the architecture.

---

## 5. Testing pyramid (data + AI)

```
        Production Monitoring (continuous eval)
              UAT (real users)
           SIT (integration)
        Unit tests (per component)
```

| Layer | Tests | Tools |
|---|---|---|
| Code | Unit, integration | pytest |
| Data | Schema, range, freshness | Great Expectations, dbt tests |
| Model | Accuracy, drift, fairness | MLflow eval, Deepchecks |
| RAG | Retrieval recall, faithfulness | RAGAS |
| Agent | Task completion, tool use | LangSmith evals |
| API | Functional, load, security | Postman, Locust |
| E2E | User journeys | Playwright |

AI-specific gates worth carrying into CI: golden datasets (held-out, must pass), adversarial/prompt-injection, bias/demographic parity, cost ceiling per run, p95 latency threshold.

---

## 6. Enterprise stack quick-map (AWS-first, since AIA)

| Concern | AWS | Databricks (multi-cloud) |
|---|---|---|
| Storage / lake | S3 | Delta Lake on S3 |
| Warehouse / SQL | Redshift / Athena | Databricks SQL |
| Batch compute | Glue, EMR | Spark on Databricks |
| Streaming | MSK (Kafka), Kinesis | Structured Streaming, Auto Loader |
| Orchestration | MWAA (managed Airflow) | Databricks Workflows + Airflow |
| ML platform | SageMaker | Databricks ML / MLflow |
| Feature store | SageMaker Feature Store | Databricks Feature Store |
| Vector | OpenSearch k-NN | Databricks Vector Search |
| LLM | Bedrock | Mosaic AI / external APIs |
| Governance | Lake Formation | Unity Catalog |

Most AIA pipeline work lands in: **S3 + Delta + Structured Streaming/Auto Loader + MWAA/Workflows + Unity Catalog**, with SageMaker/Bedrock as the ML/AI extension surface.
