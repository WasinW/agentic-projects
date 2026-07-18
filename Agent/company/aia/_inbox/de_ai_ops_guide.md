# 🎯 DE + AI/RAG/Agent: Complete Operational Guide

> **For:** Sin (Data Engineer @ The1 / Central Group Thailand)
> **Scope:** Post-Gold layer (ML, AI, RAG, Agent) — ignore Bronze→Gold for now
> **Purpose:** Hands-on roadmap for transitioning from pure DE → DE+AI hybrid role
> **Last updated:** Dec 2026

---

## 📑 Table of Contents

1. Tool Comparisons (Choose The Right Tool)
2. Project Design: Lumora KB (Thai RAG end-to-end)
3. LLMOps Deep Dive (Operations Patterns)
4. Skills Roadmap
5. Appendix: Schema, Code Snippets, Resources

---

# 1. 🔍 TOOL COMPARISONS

## 1.1 Vector Database

| Tool | Best for | Pricing | Pros | Cons |
|---|---|---|---|---|
| **pgvector** ⭐ | Start here, hybrid SQL+vector | Free (Postgres) | Same DB, ACID, JOIN-able, mature | <1M vectors performance limit |
| **Qdrant** | Production self-host | Free OSS / $25+ cloud | Fast, Rust-based, good filtering | Need separate infra |
| **Pinecone** | Managed, no ops | $70+/mo serverless | Zero ops, fast | Lock-in, pricey at scale |
| **Weaviate** | Multi-modal + GraphQL | Free OSS / $25+ | Good for image+text | More complex |
| **Chroma** | Local dev only | Free | Easiest start | Not production-grade |
| **Milvus** | Massive scale (10M+) | Free OSS | Enterprise-ready | Heavy ops |
| **BigQuery Vector** | If already on GCP | Pay per query | No new infra | Slower than dedicated |
| **MongoDB Atlas Vector** | Already use Mongo | $9+/mo | Same DB | Newer feature |

### ⭐ Recommendation: pgvector for Sin
- DE background → already know SQL
- Can JOIN with structured data
- One database to operate
- Free tier
- Scales to ~1-10M vectors

---

## 1.2 Agent / Orchestration Framework

| Tool | Best for | Pros | Cons |
|---|---|---|---|
| **LangGraph** ⭐ | Production agents, complex flows | Stateful, debuggable, LangSmith integration | LangChain ecosystem dependency |
| **LangChain** | Quick RAG prototypes | Massive ecosystem | Abstraction overhead, breaking changes |
| **LlamaIndex** | RAG-focused | Best RAG primitives | Less agent-focused |
| **CrewAI** | Multi-agent collab | Simple multi-agent | Less mature, opinionated |
| **AutoGen** | Microsoft-backed | Research-grade, multi-agent | Less production-ready |
| **Pydantic AI** | Type-safe agents | Clean API, type-safe | New (2025), smaller community |
| **Anthropic SDK direct** | Maximum control | No abstraction | More code |
| **Vercel AI SDK** | Frontend AI | Easy streaming | JS only |

### ⭐ Recommendation: LangGraph
- DE background → likes structured workflows (DAG-like)
- Stateful agents = can pause/resume (like Airflow)
- LangSmith integration = observability built-in
- Same patterns as Beam/Dataflow

---

## 1.3 Eval Frameworks

| Tool | Best for | Pros | Cons |
|---|---|---|---|
| **RAGAS** ⭐ | RAG-specific evals | Standard metrics, easy | RAG-focused only |
| **DeepEval** | General LLM evals | Pytest-like, comprehensive | Newer |
| **LangSmith** | Production tracing + evals | Best UI, LangChain integration | $$ at scale |
| **Phoenix (Arize)** | OSS observability | Free, full-featured | Self-host |
| **Helicone** | LLM cost + latency | Simple, cheap | Less eval-focused |
| **Langfuse** | OSS LangSmith alt | Self-host, full features | Less polished UI |
| **Custom (PyTest + LLM judge)** | Specific needs | Full control | Build everything |

### ⭐ Recommendation:
- RAG accuracy: **RAGAS**
- Production traces: **LangSmith** (if budget) / **Langfuse** (OSS)
- General evals: **DeepEval**

---

## 1.4 Embedding Models

| Model | Use case | Cost | Languages |
|---|---|---|---|
| text-embedding-3-small (OpenAI) | General English | $0.02/1M tokens | English-focused |
| text-embedding-3-large (OpenAI) | High accuracy | $0.13/1M tokens | English-focused |
| **voyage-3** ⭐ | Best quality general | $0.06/1M | English |
| **cohere-embed-multilingual-v3** ⭐ | Thai + global | $0.10/1M | 100+ langs incl Thai |
| multilingual-e5-large | Self-host | Free | 100+ langs |
| BGE-M3 | OSS SOTA | Free (self-host) | Multilingual |
| Vertex AI text-embedding | GCP-native | $0.025/1M | Multilingual |

### ⭐ Recommendation for Sin (Thai content):
**Cohere multilingual-v3** for production, **multilingual-e5-large** for self-host

---

## 1.5 Other Critical Tools

### Prompt Management
- **LangSmith** ⭐ (paid, best UX)
- **Langfuse** (OSS alternative)
- **Promptfoo** (testing-focused)
- **Git** (versioning prompts as files — works fine for solo)

### Workflow Orchestration
- **Prefect** ⭐ (modern, Python-native)
- **Dagster** (asset-based, great for data+AI)
- **Airflow** (still standard at enterprise)
- **Temporal** (durable workflows, good for agents)

### Model Serving
- **Modal** ⭐ (serverless, pay per second)
- **BentoML** (model packaging)
- **Vertex AI Endpoints** (GCP managed)
- **vLLM** (high-performance LLM serving)

---

# 2. 🚀 PROJECT: LUMORA KB (Thai RAG End-to-End)

## 2.1 Use Case

- **User:** Sin (Stage 1) → team (Stage 2)
- **JTBD:** Ask Thai content in natural language, get cited answers
- **Why:** Thai support is rare, useful skill, portfolio-friendly

## 2.2 Success Metrics

- **Accuracy:** 85%+ on 50-question eval set
- **Latency:** <3s end-to-end
- **Cost:** <$0.05 per query
- **Citation:** 100% of answers cite source

## 2.3 Architecture (Post-Gold Only)

```
┌─────────────────────────┐
│   Gold Documents        │
│   (already cleaned)     │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│   💎 DIAMOND LAYER       │
│   Chunk + Embed         │
└────────────┬────────────┘
             ↓
   ┌─────────┴─────────┐
   ↓                   ↓
[Vector Store]   [Metadata Store]
(pgvector)       (Postgres)
   ↓                   ↓
   └─────────┬─────────┘
             ↓
┌─────────────────────────┐
│   🤖 AGENT LAYER        │
│   1. Query rewrite      │
│   2. Hybrid retrieval   │
│   3. Rerank             │
│   4. LLM generate       │
│   5. Cite sources       │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│   📊 APPLICATION         │
│   FastAPI + Streamlit   │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│   🔄 FEEDBACK LOOP       │
│   Logs + thumbs + eval  │
└─────────────────────────┘
```

## 2.4 Project Structure

```
lumora-kb/
├── docker-compose.yml
├── pyproject.toml
├── src/
│   ├── ingestion/      # Chunking + embedding
│   ├── retrieval/      # Vector + BM25 + rerank
│   ├── rag/            # LangGraph workflow
│   ├── api/            # FastAPI
│   └── eval/           # RAGAS eval suite
├── data/
│   ├── raw/            # Gold docs
│   └── eval/           # Eval Q&A
├── notebooks/          # Exploration
├── tests/              # pytest
└── infra/              # Terraform (later)
```

## 2.5 Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Database | Postgres + pgvector | One DB, SQL skills |
| Embedding | Cohere multilingual-v3 | Best for Thai |
| LLM | Claude Sonnet 4.5 | Quality, Thai support |
| Orchestration | LangGraph | Stateful workflows |
| Eval | RAGAS | Standard RAG metrics |
| API | FastAPI | Fast, async, typed |
| UI | Streamlit | Quick prototyping |
| Containerization | Docker Compose | Easy local dev |
| Observability | LangSmith or Langfuse | Trace + metrics |

## 2.6 6-Week Build Plan

### Week 1: Foundation Setup

**Goal:** Working dev environment

**Tasks:**
1. Docker Compose with Postgres + pgvector
2. Initialize Python project (uv)
3. Test Claude API connection
4. Test Cohere embedding
5. Load 10 sample Thai docs

### Week 2: Ingestion Pipeline

**Goal:** Documents → searchable vectors

**Schema:**
```sql
CREATE TABLE documents (
    doc_id UUID PRIMARY KEY,
    title TEXT,
    source TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chunks (
    chunk_id UUID PRIMARY KEY,
    doc_id UUID REFERENCES documents,
    content TEXT,
    embedding VECTOR(1024),
    chunk_index INT,
    token_count INT
);

CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX ON chunks USING gin(to_tsvector('simple', content));
```

**Component:**
```python
class IngestionPipeline:
    def __init__(self):
        self.chunker = SemanticChunker(chunk_size=500, overlap=50)
        self.embedder = CohereEmbedder(model="embed-multilingual-v3.0")
        self.store = PgVectorStore()
    
    def ingest(self, doc):
        # 1. Extract metadata
        # 2. Chunk semantically
        # 3. Embed each chunk (batch)
        # 4. Store both in pgvector + Postgres
```

**Tasks:**
1. Semantic chunker (Thai-friendly)
2. Batch embedder (cost-efficient)
3. Storage (pgvector + metadata)
4. Test with 100 docs
5. Measure: speed, cost

### Week 3: Retrieval Pipeline

**Goal:** Question → relevant chunks

**Component:**
```python
class HybridRetriever:
    def retrieve(self, query: str, k: int = 10):
        # 1. Vector search (semantic)
        vector_results = self.pgvector_search(query, k=20)
        
        # 2. BM25 search (keyword)
        bm25_results = self.bm25_search(query, k=20)
        
        # 3. Reciprocal Rank Fusion
        combined = self.rrf(vector_results, bm25_results)
        
        # 4. Cohere rerank
        reranked = self.rerank(query, combined, top_k=k)
        
        return reranked
```

**Tasks:**
1. Vector search query
2. BM25 (Postgres full-text)
3. Reciprocal Rank Fusion
4. Cohere rerank integration
5. Eval: recall@5, MRR

### Week 4: RAG Workflow (LangGraph)

**Goal:** Question → cited answer

```python
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

class RAGState(TypedDict):
    question: str
    rewritten_query: str
    chunks: list
    answer: str
    citations: list

def build_rag_graph():
    graph = StateGraph(RAGState)
    
    graph.add_node("rewrite_query", rewrite_query)
    graph.add_node("retrieve", hybrid_retrieve)
    graph.add_node("grade_relevance", grade_chunks)
    graph.add_node("generate", generate_answer)
    graph.add_node("verify_citations", check_citations)
    
    graph.set_entry_point("rewrite_query")
    graph.add_edge("rewrite_query", "retrieve")
    graph.add_edge("retrieve", "grade_relevance")
    graph.add_conditional_edges(
        "grade_relevance",
        decide_to_generate,
        {"sufficient": "generate", "insufficient": "rewrite_query"}
    )
    graph.add_edge("generate", "verify_citations")
    graph.add_edge("verify_citations", END)
    
    return graph.compile()
```

**Tasks:**
1. Query rewriter (handle pronouns, ambiguity)
2. Relevance grader (LLM-as-judge)
3. Answer generator (Claude w/ Thai prompt)
4. Citation checker
5. End-to-end test

### Week 5: API + UI

**Goal:** Make it usable

```python
# src/api/main.py
from fastapi import FastAPI
from src.rag.workflow import build_rag_graph

app = FastAPI()
rag_graph = build_rag_graph()

@app.post("/ask")
async def ask(question: str):
    result = await rag_graph.ainvoke({"question": question})
    return {
        "answer": result["answer"],
        "citations": result["citations"]
    }
```

```python
# Streamlit UI
import streamlit as st
import requests

st.title("Lumora KB")
question = st.text_input("ถามอะไรก็ได้:")
if question:
    response = requests.post(
        "http://localhost:8000/ask", 
        json={"question": question}
    )
    data = response.json()
    st.write(data["answer"])
    for cite in data["citations"]:
        st.caption(f"📎 {cite}")
```

**Tasks:**
1. FastAPI server
2. Streamlit UI
3. Logging (Postgres or Phoenix)
4. Docker compose full stack
5. README + setup guide

### Week 6: Eval + Production Polish

**Goal:** Measure quality, ship

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)

eval_set = load_eval_data("data/eval/thai_qa_v1.csv")

results = evaluate(
    dataset=eval_set,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall
    ]
)

print(results)
# {'faithfulness': 0.89, 'answer_relevancy': 0.92, ...}
```

**Tasks:**
1. Build eval set (50 Q&A)
2. Run RAGAS
3. Identify weak spots
4. Iterate
5. Deploy (Modal or Cloud Run)
6. Monitoring dashboard

## 2.7 Cost Estimate

| Item | Cost/mo |
|---|---|
| Supabase (Postgres + pgvector) | $25 |
| Cohere embedding (10K queries) | $5 |
| Claude API (1K queries/day) | $30 |
| Modal hosting | $10 |
| **Total** | **~$70** |

## 2.8 Skills Acquired

- pgvector hands-on
- Chunking strategies (semantic, recursive)
- Embedding models (Cohere multilingual)
- Hybrid retrieval (vector + BM25)
- Reranking (Cohere)
- LangGraph (stateful workflows)
- RAGAS evaluation
- FastAPI + Streamlit
- Docker Compose
- Production patterns

---

# 3. 🔧 LLMOPS DEEP DIVE

## 3.1 LLMOps vs MLOps

```
MLOps focuses on:                LLMOps focuses on:
─────────────────                ─────────────────
- Train custom models             - Use pre-trained models (API)
- Manage feature stores           - Manage prompts + RAG context
- Track experiments               - Track prompt versions + evals
- Model versioning                - Prompt + model + chain versioning
- Drift detection                 - Hallucination + relevance monitoring
- Cost: GPU training              - Cost: tokens + retrieval
- Latency: ms                     - Latency: seconds
- Deterministic                   - Stochastic (temperature)
```

**Modern AI Ops = MLOps + LLMOps + Agent Ops**

## 3.2 LLMOps Lifecycle

```
1. EXPERIMENTATION
   - Prompt engineering
   - Model selection
   - Embedding selection
   - Chunking strategy
   - Eval baseline
        ↓
2. EVALUATION
   - Offline eval (golden set)
   - Quality metrics
   - Cost analysis
   - Latency analysis
   - Safety checks
        ↓
3. DEPLOYMENT
   - Prompt versioning
   - Canary deploys
   - Feature flags
   - A/B testing
   - Rollback plans
        ↓
4. MONITORING
   - Token usage + cost
   - Latency (p50, p95, p99)
   - Error rates
   - User feedback
   - Quality drift
   - Safety incidents
        ↓
5. CONTINUOUS IMPROVEMENT
   - Failure analysis
   - Eval set expansion
   - Prompt iteration
   - Model upgrades
        ↓
   [back to 1]
```

## 3.3 Key Patterns

### Pattern 1: Prompt Versioning + Git Flow

```
prompts/
├── rag_system_v1.txt    (prod)
├── rag_system_v2.txt    (staging)
└── changelog.md

# Deploy via env
PROMPT_VERSION=v2  → load rag_system_v2.txt
```

Or LangSmith:
```python
from langsmith import Client
prompt = client.pull_prompt("rag-system:v2")
```

### Pattern 2: Continuous Eval (CI/CD)

```yaml
on: pull_request
jobs:
  rag_eval:
    steps:
      - run: pytest tests/
      - run: python eval/run_ragas.py
      - name: Quality gate
        run: |
          if faithfulness < 0.85; then exit 1; fi
```

### Pattern 3: Semantic Caching

```python
async def query_with_cache(q: str):
    q_emb = embed(q)
    cached = cache.search(q_emb, threshold=0.95)
    if cached:
        return cached
    
    result = await rag.invoke(q)
    cache.add(q_emb, result)
    return result
```

**Saves 30-70% on LLM costs**

### Pattern 4: Model Routing (Cheap → Expensive)

```python
def route_query(q: str):
    if is_simple(q):
        return claude_haiku(q)         # $0.001
    elif is_complex(q):
        return claude_sonnet(q)         # $0.015
    else:
        return claude_opus(q)           # $0.075
```

### Pattern 5: Guardrails (Safety + Quality)

```python
class Guardrails:
    def pre_process(self, query):
        # Block PII
        # Block prompt injection
        # Block off-topic
        return safe_query
    
    def post_process(self, response):
        # Check hallucination
        # Check toxicity
        # Verify citations
        return safe_response
```

Tools: Guardrails AI, NeMo Guardrails, Lakera

### Pattern 6: Observability Stack

```
Application
   ↓
LangSmith / Langfuse / Phoenix (trace)
   ↓
Metrics:
- Token usage
- Cost per query
- Latency breakdown
- Tool calls
- Errors
   ↓
Alerts (Slack, PagerDuty)
```

### Pattern 7: Eval-Driven Development

```
1. Write eval BEFORE feature
2. Implement feature
3. Run eval — must pass threshold
4. Deploy
5. Monitor → expand eval set
```

## 3.4 Production Metrics

### Quality:
- **Faithfulness** — grounded in context
- **Answer Relevancy** — addresses question
- **Context Precision** — retrieved chunks relevant
- **Context Recall** — important info retrieved
- **Hallucination Rate** — % fabricated info
- **Citation Accuracy** — % citations support claim

### Cost:
- **Tokens per query** (input + output)
- **Cost per query**
- **Cache hit rate**
- **Model distribution**

### Latency:
- **TTFT** (Time To First Token)
- **TTLT** (Time To Last Token)
- **Retrieval latency**
- **p50/p95/p99**

### Safety:
- **Prompt injection attempts**
- **Toxicity scores**
- **PII leakage**
- **Off-topic blocked**

### Business:
- **User satisfaction** (👍/👎)
- **Resolution rate**
- **Containment rate**

## 3.5 Tool Stack Cheatsheet

| Need | Best Tool | Why |
|---|---|---|
| Trace agent calls | LangSmith / Phoenix | See entire chain |
| Prompt versioning | LangSmith / Langfuse | Diff + rollback |
| Eval | RAGAS + DeepEval | Standard metrics |
| Cost tracking | Helicone / Langfuse | Per-query cost |
| Caching | Redis + custom | Semantic cache |
| Safety | Guardrails AI | Pre/post filters |
| Load test | Locust + custom | LLM-specific |
| Drift detection | Phoenix | Distribution shifts |

---

# 4. 📈 SKILLS ROADMAP

## 4.1 Phase 1 (Month 1-2): Foundation

- [ ] pgvector hands-on (CRUD + queries)
- [ ] LangChain basics (chains, retrievers)
- [ ] Build 1 RAG project (Lumora KB)
- [ ] MLflow basics (experiment tracking)

## 4.2 Phase 2 (Month 3-4): Production Patterns

- [ ] Eval frameworks (RAGAS deep)
- [ ] Prompt management (LangSmith or Langfuse)
- [ ] Feature store basics (Feast)
- [ ] Modern orchestration (Prefect/Dagster)

## 4.3 Phase 3 (Month 5-6): Advanced

- [ ] Agent design (LangGraph multi-step)
- [ ] Multimodal RAG (image + text)
- [ ] AI governance basics
- [ ] LangGraph stateful workflows

## 4.4 Phase 4 (Month 7+): Specialist

- [ ] Cost optimization patterns (semantic cache, routing)
- [ ] Multi-tenant AI systems
- [ ] Advanced eval (golden sets, A/B)
- [ ] Production AI Ops

## 4.5 Portfolio Project Order

1. **Lumora KB** — Thai RAG (Month 1-2) ← START HERE
2. **NL→SQL** — BigQuery natural language (Month 2-3)
3. **Document AI** — Thai PDF processing (Month 3-4)
4. **Agentic workflow** — multi-step automation (Month 4-5)
5. **Production system** — full prod deploy (Month 5-6)

---

# 5. 📎 APPENDIX

## 5.1 Project Structure (Lumora KB)

```
lumora-kb/
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── README.md
│
├── src/
│   ├── __init__.py
│   │
│   ├── ingestion/
│   │   ├── chunker.py          # Semantic chunking
│   │   ├── embedder.py         # Cohere embedding
│   │   ├── loader.py           # Doc loading
│   │   └── pipeline.py         # Orchestration
│   │
│   ├── retrieval/
│   │   ├── vector.py           # pgvector search
│   │   ├── bm25.py             # Keyword search
│   │   ├── hybrid.py           # RRF combination
│   │   └── rerank.py           # Cohere rerank
│   │
│   ├── rag/
│   │   ├── state.py            # LangGraph state
│   │   ├── nodes/
│   │   │   ├── rewriter.py     # Query rewrite
│   │   │   ├── grader.py       # Relevance grade
│   │   │   ├── generator.py    # Answer gen
│   │   │   └── citer.py        # Citation check
│   │   └── workflow.py         # Graph compose
│   │
│   ├── api/
│   │   ├── main.py             # FastAPI app
│   │   ├── routes.py
│   │   └── schemas.py
│   │
│   ├── eval/
│   │   ├── ragas_eval.py       # RAGAS suite
│   │   ├── golden_set.py       # Manual evals
│   │   └── load_test.py        # Locust
│   │
│   └── utils/
│       ├── db.py               # DB connection
│       ├── llm.py              # Claude client
│       └── logger.py           # Structured logs
│
├── data/
│   ├── raw/                    # Gold docs
│   └── eval/
│       └── thai_qa_v1.csv      # 50 Q&A
│
├── notebooks/
│   ├── 01_explore_data.ipynb
│   ├── 02_chunking_strategies.ipynb
│   ├── 03_embedding_quality.ipynb
│   └── 04_eval_results.ipynb
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── eval/
│
├── ui/
│   └── streamlit_app.py
│
└── infra/
    ├── docker/
    │   ├── api.Dockerfile
    │   └── ui.Dockerfile
    └── terraform/              # Cloud deploy (Week 6+)
```

## 5.2 docker-compose.yml

```yaml
version: '3.9'

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: lumora
      POSTGRES_USER: lumora
      POSTGRES_PASSWORD: lumora_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infra/sql/init.sql:/docker-entrypoint-initdb.d/init.sql

  api:
    build:
      context: .
      dockerfile: infra/docker/api.Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://lumora:lumora_dev@postgres:5432/lumora
      - COHERE_API_KEY=${COHERE_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - postgres
    volumes:
      - ./src:/app/src

  ui:
    build:
      context: .
      dockerfile: infra/docker/ui.Dockerfile
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api

volumes:
  postgres_data:
```

## 5.3 Init SQL Schema

```sql
-- infra/sql/init.sql

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE documents (
    doc_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    content_hash TEXT UNIQUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chunks (
    chunk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id UUID REFERENCES documents(doc_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding VECTOR(1024),
    chunk_index INT NOT NULL,
    token_count INT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vector index
CREATE INDEX idx_chunks_embedding 
  ON chunks USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- Full-text index for BM25
CREATE INDEX idx_chunks_content_fts 
  ON chunks USING gin(to_tsvector('simple', content));

-- Query logs for observability
CREATE TABLE query_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    rewritten_query TEXT,
    retrieved_chunks UUID[],
    answer TEXT,
    citations TEXT[],
    latency_ms INT,
    tokens_input INT,
    tokens_output INT,
    cost_usd DECIMAL(10, 6),
    user_feedback SMALLINT,  -- -1, 0, 1
    created_at TIMESTAMP DEFAULT NOW()
);

-- Eval results
CREATE TABLE eval_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version TEXT NOT NULL,
    faithfulness DECIMAL(5, 4),
    answer_relevancy DECIMAL(5, 4),
    context_precision DECIMAL(5, 4),
    context_recall DECIMAL(5, 4),
    avg_latency_ms INT,
    avg_cost_usd DECIMAL(10, 6),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 5.4 Sample .env

```bash
# .env.example

# Database
DATABASE_URL=postgresql://lumora:lumora_dev@localhost:5432/lumora

# LLM APIs
ANTHROPIC_API_KEY=sk-ant-...
COHERE_API_KEY=...

# Optional: observability
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=lumora-kb

# App config
LOG_LEVEL=INFO
ENVIRONMENT=development
PROMPT_VERSION=v1
```

## 5.5 Resources

### Learning:
- LangChain docs: https://python.langchain.com
- LangGraph docs: https://langchain-ai.github.io/langgraph/
- RAGAS docs: https://docs.ragas.io
- pgvector docs: https://github.com/pgvector/pgvector

### Communities:
- LangChain Discord
- /r/LocalLLaMA (Reddit)
- AI Engineer Foundation
- Thai DE community on Facebook

### Courses:
- DeepLearning.AI short courses (RAG, agents)
- Maven LLM courses (Hamel Husain, Eugene Yan)
- Anthropic's "Building Effective Agents" essay

### Newsletters:
- Latent Space (Swyx)
- AI Engineer's Pack
- Eugene Yan's blog (applied LLM)

### Tools docs:
- LangSmith: https://docs.smith.langchain.com
- Phoenix: https://docs.arize.com/phoenix
- Langfuse: https://langfuse.com/docs
- Modal: https://modal.com/docs

---

# 🚀 Next Steps

1. ✅ Set up Docker Compose locally
2. ✅ Get Cohere + Anthropic API keys
3. ✅ Run Week 1 setup
4. ✅ Load 10 Thai docs
5. ✅ Build first chunking + embedding
6. ✅ Iterate weekly per the plan

**End goal:** Working Lumora KB in 6 weeks → portfolio piece + skills validated for AI+DE senior roles

---

**Document version:** v1
**For Sin's hands-on DE+AI transition**

