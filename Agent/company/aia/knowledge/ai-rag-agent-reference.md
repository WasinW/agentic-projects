# AI / RAG / Agent Reference

> SECONDARY reference — Sin's broader interest, **not** the AIA day job. RAG, agents, embeddings, vector DBs, eval, LLMOps tool comparisons + the Lumora KB portfolio project. Consolidated and deduplicated from the two overlapping tool-comparison docs. Read when doing AI-adjacent work; the day-job material is in the other two docs.

Original framing was The1/GCP (Thai content, BigQuery, Vertex). Cross-cloud notes added for AWS/Databricks where relevant.

---

## 1. Tool comparisons (choose the right tool)

### 1.1 Vector database

| Tool | Best for | Pricing | Pros | Cons |
|---|---|---|---|---|
| **pgvector** ⭐ | Start here; hybrid SQL+vector | Free (Postgres) | Same DB, ACID, JOIN-able, mature | <1M-vector perf limit |
| Qdrant | Production self-host | Free OSS / $25+ | Fast (Rust), good filtering | Separate infra |
| Pinecone | Managed, no ops | $70+/mo | Zero ops, fast | Lock-in, pricey at scale |
| Weaviate | Multimodal + GraphQL | Free OSS / $25+ | Good image+text | More complex |
| Chroma | Local dev only | Free | Easiest start | Not production-grade |
| Milvus | Massive scale (10M+) | Free OSS | Enterprise-ready | Heavy ops |
| OpenSearch k-NN | **AWS-native** | AWS pricing | Already in AWS estate | Tuning needed |
| Databricks Vector Search | **Databricks-native** | DBU-based | Sits on Delta, Unity-governed | Platform-bound |
| BigQuery / Mongo Atlas Vector | If already there | Pay/query | No new infra | Slower than dedicated |

**Pick:** lab/learn → pgvector; production small → pgvector (Supabase); production scale → Qdrant. **In the AIA estate the native choices are OpenSearch k-NN or Databricks Vector Search** (governed by Unity Catalog, no extra infra). Skip Pinecone (lock-in), Chroma (not prod).

### 1.2 Agent / orchestration framework

| Tool | Best for | Pros | Cons |
|---|---|---|---|
| **LangGraph** ⭐ | Production agents, complex flows | Stateful, debuggable, LangSmith integration | LangChain dependency |
| LangChain | Quick RAG prototypes | Huge ecosystem | Abstraction overhead, breaking changes |
| LlamaIndex | RAG-focused | Best RAG primitives | Less agent-focused |
| CrewAI | Multi-agent | Simple multi-agent | Less mature, opinionated |
| AutoGen | MS-backed multi-agent | Research-grade | Less production-ready |
| Pydantic AI | Type-safe agents | Clean, typed | New (2025), small community |
| Anthropic SDK direct | Max control | No abstraction | More code |
| Vercel AI SDK | Frontend AI | Easy streaming | JS only |

**Pick:** RAG-only → LlamaIndex/LangChain; agentic/multi-agent/production → LangGraph (+ LangSmith). A DE will find LangGraph's stateful-DAG model familiar (pause/resume like Airflow; graph mental model like Beam/Dataflow).

### 1.3 Eval frameworks

| Tool | Best for | Pros | Cons |
|---|---|---|---|
| **RAGAS** ⭐ | RAG-specific evals | Standard metrics, easy | RAG-only |
| DeepEval | General LLM evals | Pytest-like, comprehensive | Newer |
| LangSmith | Production tracing + evals | Best UI, LangChain-integrated | $$ at scale |
| Phoenix (Arize) | OSS observability | Free, full-featured | Self-host |
| Helicone | LLM cost + latency | Simple, cheap | Less eval-focused |
| Langfuse | OSS LangSmith alt | Self-host, full features | Less polished UI |
| Custom (pytest + LLM judge) | Specific needs | Full control | Build it all |

**Pick:** RAG accuracy → RAGAS; production traces → LangSmith (budget) / Langfuse (OSS); general → DeepEval; cost → Helicone.

### 1.4 Embedding models

| Model | Use case | Cost | Languages |
|---|---|---|---|
| text-embedding-3-small (OpenAI) | General English | $0.02/1M | English-focused |
| text-embedding-3-large (OpenAI) | High accuracy | $0.13/1M | English-focused |
| **voyage-3** ⭐ | Best general quality | $0.06/1M | English |
| voyage-code-3 | Code | $0.18/1M | Code |
| **cohere-embed-multilingual-v3** ⭐ | Thai + global | $0.10/1M | 100+ incl Thai |
| multilingual-e5-large | Self-host | Free | 100+ |
| BGE-M3 | OSS SOTA | Free (self-host) | Multilingual |
| Amazon Titan / Bedrock embeddings | AWS-native | Bedrock pricing | Multilingual |

**Pick (Thai):** Cohere multilingual-v3 for production, multilingual-e5-large/BGE-M3 to self-host. On AWS, Bedrock (Titan / hosted Cohere) keeps it in-estate.

### 1.5 Other tools (quick picks)

- **Prompt mgmt:** LangSmith ⭐ / Langfuse (OSS) / Promptfoo (testing) / Git (fine for solo).
- **Feature store:** Feast ⭐ (OSS) / Tecton / Databricks Feature Store (native at AIA) / SageMaker Feature Store.
- **Orchestration:** Prefect / Dagster / **Airflow** (AIA standard) / Temporal (durable, agent-friendly).
- **Model serving:** Modal ⭐ (serverless) / BentoML / vLLM / SageMaker Endpoints / Bedrock.

---

## 2. RAG essentials

**Why RAG:** LLM knowledge cutoff + no private data + hallucination without grounding; cheaper than fine-tuning; updatable by changing data. Flow: query → embed → vector search top-k → stuff into prompt → generate with citations.

### Chunking

| Strategy | When |
|---|---|
| Fixed-size (N tokens + overlap) | Simple text |
| Semantic (meaning boundaries) | Most use cases |
| Recursive (separator hierarchy) | Mixed content |
| Document-aware (sections/headers) | Technical docs |
| Sentence-window (embed sentence, retrieve neighbors) | Precise retrieval |
| Hierarchical (multi-size) | Long docs |
| Agentic (LLM picks boundaries) | Highest quality, costly |

Defaults: 200–800 tokens (sweet spot ~400–500), 10–20% overlap, preserve sentence boundaries, attach metadata (source, section, title).

### Retrieval

- **Dense (vector):** semantic, misses exact keywords.
- **Sparse (BM25):** exact match, misses synonyms.
- **Hybrid ⭐:** vector + BM25 → Reciprocal Rank Fusion → top-k. Almost always beats either alone.
- **Rerank:** retrieve top-50 → cross-encoder rerank to top-10 (Cohere/BGE/Voyage Rerank).
- **Pre-filter:** date, source, **access permissions (security)**, tags.

### Advanced patterns (when basic RAG underperforms)

Query rewriting (resolve pronouns, expand, decompose); HyDE (embed a hypothetical answer); Self-RAG (LLM decides when to retrieve + self-critiques); Corrective RAG (grade chunks → web-search fallback); Graph RAG (KG for relationships); Multi-vector (summary + chunks + questions per doc); ColBERT (per-token late interaction).

### Long-context vs RAG

RAG wins: KB >100K tokens, multi-user (cache embeddings), need citations, cost-sensitive, frequently updated. Long-context wins: need full-doc context, doc <100K tokens, one-shot, cost not primary. Hybrid: RAG to find chunks, long-context to analyze.

### RAG eval metrics

- **Retrieval:** Recall@k, MRR, NDCG, Hit Rate.
- **Generation:** Faithfulness (grounded), Answer Relevancy, Context Precision, Context Recall, Citation Accuracy, Hallucination Rate.
- **Tools:** RAGAS (standard), DeepEval, TruLens, Phoenix (production).

---

## 3. Agents (condensed)

Agent = LLM that **plans → uses tools → observes → adapts** (vs a workflow's fixed steps).

**Anthropic "Building Effective Agents" patterns:** Prompt Chaining; Routing; Parallelization; Orchestrator-Workers; Evaluator-Optimizer; full autonomous Agent loop. **Default to the simplest pattern that works** — most tasks are workflows, not agents.

**Tool design:** single responsibility, clear I/O schema, descriptive name+docstring, idempotent, error-handled, logged. 5–10 tools max (more → confusion). Vague docs → wrong tool picked.

**Memory:** short-term (conversation/state), long-term (prefs/facts → vector/Postgres/KG), episodic (logged interactions), procedural (stored prompts/code).

**Planning:** ReAct (thought→action→observation loop), Plan-and-Execute, Tree of Thoughts, Reflection.

**Multi-agent** (hierarchical / sequential / debate / voting / network) only when tasks need specialization or parallelism — single agent is better for simple tasks and tight cost/latency budgets. Frameworks: LangGraph (graph), CrewAI (roles), AutoGen (conversation).

**Guardrails:** pre-process (block PII, prompt injection, off-topic) + post-process (hallucination, toxicity, citation verify). Tools: Guardrails AI, NeMo Guardrails, Lakera, LLM Guard. Cap iterations to avoid infinite loops; add human-in-the-loop approval for high-stakes actions.

---

## 4. LLMOps (vs MLOps) + production patterns

| MLOps | LLMOps |
|---|---|
| Train custom models | Use API models |
| Feature stores | Prompts + RAG context |
| Track experiments | Track prompt versions + evals |
| Model versioning | Prompt + model + chain versioning |
| Drift detection | Hallucination + relevance monitoring |
| Cost: GPU training | Cost: tokens + retrieval |
| Latency: ms | Latency: seconds |
| Deterministic | Stochastic |

**Lifecycle:** Experiment → Evaluate (golden set, cost, latency, safety) → Deploy (prompt versioning, canary, flags, A/B, rollback) → Monitor (cost, latency p50/95/99, errors, feedback, quality drift, safety) → Continuous improvement → loop.

**Key patterns:**
- **Prompt versioning:** `prompts/*_v{n}.txt` + `PROMPT_VERSION` env, or LangSmith `client.pull_prompt("rag-system:v2")`.
- **Continuous eval gate (CI):** run RAGAS on PR; fail if `faithfulness < 0.85`.
- **Semantic caching:** match on query-embedding similarity (threshold ~0.95) → 30–70% LLM cost saving.
- **Model routing:** simple→Haiku, mid→Sonnet, hard→Opus → 40–60% saving.
- **Batch API:** 50% discount where latency allows. Combined caching+routing+batch can hit 80%+ savings.
- **Eval-driven development:** write the eval before the feature.

**Production metrics:** Quality (faithfulness, relevancy, precision/recall, hallucination, citation); Cost (tokens/query, cost/query, cache-hit rate, model mix); Latency (TTFT, TTLT, retrieval latency, p50/95/99); Safety (injection attempts, toxicity, PII leakage, off-topic blocked); Business (👍/👎, resolution rate, containment rate).

**Tool cheatsheet:** trace → LangSmith/Phoenix; prompt versioning → LangSmith/Langfuse; eval → RAGAS+DeepEval; cost → Helicone/Langfuse; cache → Redis+custom; safety → Guardrails AI; load test → Locust; drift → Phoenix.

---

## 5. Portfolio project — Lumora KB (Thai RAG)

A 6-week hands-on RAG build (Sin's portfolio piece, ~$70/mo). Architecture is **post-Gold only** — it consumes already-clean Gold docs, so it slots onto the lakehouse from the other docs.

```
Gold docs → Diamond layer (chunk + embed) → [pgvector + Postgres metadata]
          → Agent layer (LangGraph): rewrite → hybrid retrieve → rerank → generate → cite
          → FastAPI + Streamlit → feedback loop (logs, 👍/👎, eval)
```

**Stack:** Postgres+pgvector · Cohere multilingual-v3 · Claude Sonnet · LangGraph · RAGAS · FastAPI · Streamlit · Docker Compose · LangSmith/Langfuse.
**Success metrics:** ≥85% accuracy on a 50-Q eval set, <3s latency, <$0.05/query, 100% answers cite a source.

**6-week plan:** W1 foundation (compose + APIs) → W2 ingestion (chunk/embed/store) → W3 retrieval (vector+BM25+RRF+rerank) → W4 LangGraph workflow (rewrite/grade/generate/cite) → W5 API+UI+logging → W6 eval (RAGAS) + deploy (Modal/Cloud Run).

LangGraph workflow skeleton:

```python
class RAGState(TypedDict):
    question: str; rewritten_query: str; chunks: list; answer: str; citations: list

def build_rag_graph():
    g = StateGraph(RAGState)
    for name, fn in [("rewrite_query", rewrite_query), ("retrieve", hybrid_retrieve),
                     ("grade_relevance", grade_chunks), ("generate", generate_answer),
                     ("verify_citations", check_citations)]:
        g.add_node(name, fn)
    g.set_entry_point("rewrite_query")
    g.add_edge("rewrite_query", "retrieve")
    g.add_edge("retrieve", "grade_relevance")
    g.add_conditional_edges("grade_relevance", decide_to_generate,
        {"sufficient": "generate", "insufficient": "rewrite_query"})
    g.add_edge("generate", "verify_citations")
    g.add_edge("verify_citations", END)
    return g.compile()
```

Core SQL schema (pgvector): `documents` (doc_id, title, source, content_hash UNIQUE, metadata JSONB) + `chunks` (chunk_id, doc_id FK, content, `embedding VECTOR(1024)`, chunk_index, token_count) with `ivfflat (embedding vector_cosine_ops)` + `gin(to_tsvector('simple', content))` for BM25; plus `query_logs` and `eval_runs` for observability. Hybrid retrieval = pgvector cosine + Postgres full-text → RRF → Cohere rerank.

---

## 6. Common pitfalls (carry these forward)

**RAG:** bad chunking (test 200/500/800, measure recall) · wrong-language embedding (use multilingual) · vector-only (use hybrid+rerank) · no eval (build 50+ Q&A early) · over-engineering (start simple) · ignoring citations (verify in workflow).
**Agent:** too many tools (≤10, clear docs) · no observability (LangSmith/Phoenix from day 1) · infinite loops (max-iteration caps) · no human-in-the-loop for high-stakes.
**Production:** no cost monitoring (daily alerts, budgets) · no caching · no prompt versioning · no drift monitoring (continuous eval on prod samples) · no safety guardrails.

---

## 7. Curated resources

- **Docs:** LangChain, LangGraph, RAGAS, pgvector, Cohere, Anthropic API; Phoenix, Langfuse, Helicone, Modal.
- **Learn:** DeepLearning.AI short courses (RAG/agents/eval); Anthropic "Building Effective Agents"; Maven LLM courses (Hamel Husain, Eugene Yan).
- **Read:** Eugene Yan, Hamel Husain, Chip Huyen, Lilian Weng, Simon Willison, Latent Space.
- **Books:** "AI Engineering" (Chip Huyen, 2025); "Designing ML Systems" (Huyen); "Designing Data-Intensive Applications" (Kleppmann); "Fundamentals of Data Engineering" (Reis & Housley).
- **Papers:** original RAG; "Lost in the Middle"; Self-RAG; Corrective RAG; HyDE; ReAct; Tree of Thoughts; Reflexion; RAGAS.
