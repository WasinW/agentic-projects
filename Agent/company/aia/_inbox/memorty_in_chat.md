โอเค ลุยตามลำดับ — 3 → 1 → 2 → 4 (export) เน้น **post-Gold layer** เท่านั้น

---

# 3️⃣ Tool Comparisons (เลือกอันไหนดี?)

## 🔍 Vector Database

| Tool | Best for | Pricing | Pros | Cons |
|---|---|---|---|---|
| **pgvector** ⭐ | Start here, hybrid SQL+vector | Free (Postgres) | Same DB, ACID, JOIN-able, mature | <1M vectors performance limit |
| **Qdrant** | Production self-host | Free OSS / $25+ cloud | Fast, Rust-based, good filtering | Need separate infra |
| **Pinecone** | Managed, no ops | $70+/mo serverless | Zero ops, fast | Lock-in, pricey at scale |
| **Weaviate** | Multi-modal + GraphQL | Free OSS / $25+ | Good for image+text | More complex |
| **Chroma** | Local dev | Free | Easiest start | Not production-grade |
| **Milvus** | Massive scale (10M+) | Free OSS | Enterprise-ready | Heavy ops |
| **BigQuery Vector** | If already on GCP | Pay per query | No new infra | Slower than dedicated |
| **MongoDB Atlas Vector** | Already use Mongo | $9+/mo | Same DB | Newer feature |

### ⭐ Recommendation for Sin:
```
Lab/Practice:        pgvector (Supabase or local Postgres)
Production small:    pgvector + Supabase ($25/mo)
Production scale:    Qdrant Cloud or pgvector with replicas
Skip:                Pinecone (lock-in), Chroma (not prod)
```

**Why pgvector wins for Sin:**
- Already know SQL (DE background)
- Can JOIN with structured data (`users` + `embeddings`)
- One database to operate
- Free tier ดี
- Scale to ~1-10M vectors fine

---

## 🤖 Agent / Orchestration Framework

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

### ⭐ Recommendation for Sin:
```
RAG-only project:     LlamaIndex or LangChain
Agentic workflows:    LangGraph ⭐
Multi-agent:          LangGraph (graph-based)
Production:           LangGraph + LangSmith
Maximum control:      Anthropic SDK + Pydantic AI
```

**Why LangGraph for Sin:**
- DE background → likes structured workflows (DAG-like)
- Stateful agents → can pause/resume (like Airflow for AI)
- LangSmith integration → observability built-in
- Same patterns as Beam/Dataflow (graph mental model)

---

## 📊 Eval Frameworks

| Tool | Best for | Pros | Cons |
|---|---|---|---|
| **RAGAS** ⭐ | RAG-specific evals | Standard metrics, easy | RAG-focused only |
| **DeepEval** | General LLM evals | Pytest-like, comprehensive | Newer |
| **LangSmith** | Production tracing + evals | Best UI, LangChain integration | $$ at scale |
| **Phoenix (Arize)** | Open source observability | Free, full-featured | Self-host |
| **Helicone** | LLM cost + latency | Simple, cheap | Less eval-focused |
| **Langfuse** | OSS LangSmith alternative | Self-host, full features | Less polished UI |
| **Custom (PyTest + LLM judge)** | Specific needs | Full control | Build everything |

### ⭐ Recommendation for Sin:
```
RAG accuracy:        RAGAS
Production traces:   LangSmith (if budget) or Langfuse (OSS)
General evals:       DeepEval
Cost monitoring:     Helicone (cheap, focused)
```

---

## 🧠 Embedding Models

| Model | Use case | Cost | Languages |
|---|---|---|---|
| **text-embedding-3-small** (OpenAI) | General English | $0.02/1M tokens | English-focused |
| **text-embedding-3-large** (OpenAI) | High accuracy | $0.13/1M tokens | English-focused |
| **voyage-3** ⭐ | Best quality general | $0.06/1M | English |
| **cohere-embed-multilingual-v3** ⭐ | Thai + global | $0.10/1M | 100+ langs incl Thai |
| **multilingual-e5-large** | Self-host | Free | 100+ langs |
| **BGE-M3** | Open source SOTA | Free (self-host) | Multilingual |
| **Vertex AI text-embedding** | GCP-native | $0.025/1M | Multilingual |

### ⭐ Recommendation for Sin (Thai content):
```
Production Thai:      cohere multilingual-v3 ⭐
Self-host budget:     multilingual-e5-large
GCP-only:             Vertex AI text-embedding
English-only:         voyage-3
```

---

## 🛠️ Other Critical Tools

### Prompt Management
- **LangSmith** ⭐ (paid, best UX)
- **Langfuse** (OSS alternative)
- **Promptfoo** (testing-focused)
- **Git** (versioning prompts as files works fine for solo)

### Feature Store (skip if not doing ML)
- **Feast** ⭐ (OSS, lightweight)
- **Tecton** (managed, enterprise)
- **Vertex AI Feature Store** (GCP-native)

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

# 1️⃣ Design 1 Project End-to-End: **Thai RAG Q&A**

## 🎯 Project: "Lumora KB" — Thai Knowledge Base RAG

**Theme:** Sin's first hands-on practice project + portfolio piece + ใช้ได้กับงาน The1 ในอนาคต

### Use Case
- **User:** Sin himself (Stage 1) → expand to team (Stage 2)
- **JTBD:** Ask questions about Thai content (docs, articles, transcripts) in natural language and get cited answers
- **Why this:** Thai language support is rare, useful skill, portfolio-friendly

### Success Metrics
- Accuracy: 85%+ on hand-curated 50-question eval set
- Latency: <3 seconds end-to-end
- Cost: <$0.05 per query
- Citation: 100% of answers cite source

---

## 🏗️ Architecture (Post-Gold Only)

```
                  ┌─────────────────────────┐
                  │   Gold-Layer Documents  │
                  │   (already cleaned)     │
                  └────────────┬────────────┘
                               ↓
                  ┌─────────────────────────┐
                  │   💎 DIAMOND LAYER       │
                  │   Chunk + Embed Pipeline │
                  └────────────┬────────────┘
                               ↓
              ┌────────────────┴────────────────┐
              ↓                                  ↓
    ┌──────────────────┐                ┌────────────────┐
    │  Vector Store    │                │  Metadata Store│
    │  (pgvector)      │                │  (Postgres)    │
    │  - embedding     │                │  - doc info    │
    │  - chunk text    │                │  - tags        │
    └────────┬─────────┘                └────────┬───────┘
             └────────────────┬─────────────────┘
                              ↓
                  ┌─────────────────────────┐
                  │   🤖 AGENT LAYER         │
                  │   RAG Pipeline           │
                  │   1. Query rewrite       │
                  │   2. Hybrid retrieval    │
                  │   3. Rerank             │
                  │   4. LLM generate        │
                  │   5. Cite sources        │
                  └────────────┬────────────┘
                               ↓
                  ┌─────────────────────────┐
                  │   📊 APPLICATION         │
                  │   FastAPI + Streamlit    │
                  └────────────┬────────────┘
                               ↓
                  ┌─────────────────────────┐
                  │   🔄 FEEDBACK LOOP       │
                  │   - Query logs          │
                  │   - Thumbs up/down       │
                  │   - Latency metrics      │
                  │   → back to eval set     │
                  └─────────────────────────┘
```

---

## 📋 Step-by-Step Build Plan (6 weeks)

### **Week 1: Foundation Setup**

**Goal:** Working dev environment

```bash
# Project structure
lumora-kb/
├── docker-compose.yml
├── pyproject.toml
├── src/
│   ├── ingestion/      # Chunking + embedding
│   ├── retrieval/      # Vector + BM25
│   ├── rag/            # LangGraph workflow
│   ├── api/            # FastAPI
│   └── eval/           # Eval suite
├── data/
│   ├── raw/            # Gold docs
│   └── eval/           # Eval questions
├── notebooks/          # Exploration
├── tests/              # pytest
└── infra/              # Terraform (later)
```

**Stack:**
- Docker Compose with Postgres+pgvector
- Python 3.12 with uv (modern package manager)
- Just one LLM API (Claude or Gemini)
- Cohere for embeddings

**Tasks:**
1. ✅ Set up Docker Compose (Postgres + pgvector)
2. ✅ Initialize Python project
3. ✅ Test connection to Claude API
4. ✅ Test Cohere embedding
5. ✅ Load 10 sample Thai docs

### **Week 2: Ingestion Pipeline**

**Goal:** Documents → searchable vectors

**Components:**
```python
# src/ingestion/pipeline.py
class IngestionPipeline:
    def __init__(self):
        self.chunker = SemanticChunker(chunk_size=500, overlap=50)
        self.embedder = CohereEmbedder(model="embed-multilingual-v3.0")
        self.store = PgVectorStore()
    
    def ingest(self, doc: Document):
        # 1. Extract metadata
        # 2. Chunk semantically
        # 3. Embed each chunk
        # 4. Store both in pgvector + Postgres
```

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
    embedding VECTOR(1024),  -- Cohere v3 dim
    chunk_index INT,
    token_count INT
);

CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops);
```

**Tasks:**
1. Implement chunker (semantic-aware, Thai-friendly)
2. Implement embedder (batch processing)
3. Implement storage (pgvector + metadata)
4. Test end-to-end with 100 docs
5. Measure: ingestion speed, cost

### **Week 3: Retrieval Pipeline**

**Goal:** Question → relevant chunks

**Components:**
```python
# src/retrieval/hybrid.py
class HybridRetriever:
    def retrieve(self, query: str, k: int = 10):
        # 1. Vector search (semantic)
        vector_results = self.pgvector_search(query, k=20)
        
        # 2. BM25 search (keyword)
        bm25_results = self.bm25_search(query, k=20)
        
        # 3. Combine + rerank
        combined = self.reciprocal_rank_fusion(vector_results, bm25_results)
        
        # 4. Cohere rerank
        reranked = self.rerank(query, combined, top_k=k)
        
        return reranked
```

**Tasks:**
1. Vector search query
2. BM25 implementation (Postgres full-text or RAGfusion)
3. Reciprocal Rank Fusion
4. Cohere rerank integration
5. Eval retrieval quality (recall@5, MRR)

### **Week 4: RAG Workflow (LangGraph)**

**Goal:** Question → cited answer

```python
# src/rag/workflow.py
from langgraph.graph import StateGraph, END

class RAGState(TypedDict):
    question: str
    rewritten_query: str
    chunks: list[Chunk]
    answer: str
    citations: list[str]

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
1. Implement query rewriter
2. Implement relevance grader
3. Implement answer generator (Claude with Thai prompt)
4. Implement citation checker
5. End-to-end test

### **Week 5: API + UI**

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
# Simple Streamlit UI for testing
import streamlit as st

st.title("Lumora KB")
question = st.text_input("ถามอะไรก็ได้:")
if question:
    response = requests.post("http://localhost:8000/ask", json={"question": question})
    st.write(response.json()["answer"])
    for cite in response.json()["citations"]:
        st.caption(f"📎 {cite}")
```

**Tasks:**
1. FastAPI server
2. Streamlit UI
3. Logging (Phoenix or simple Postgres logs)
4. Docker compose for full stack
5. README + setup guide

### **Week 6: Eval + Production Polish**

**Goal:** Measure quality, ship to "production"

**Eval suite:**
```python
# src/eval/ragas_eval.py
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)

# 50 hand-curated Thai Q&A pairs
eval_set = load_eval_data("data/eval/thai_qa_v1.csv")

results = evaluate(
    dataset=eval_set,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
)
```

**Tasks:**
1. Build eval set (50 Q&A)
2. Run RAGAS metrics
3. Identify weak spots
4. Iterate on chunking/retrieval/prompt
5. Deploy to Modal or Cloud Run
6. Set up monitoring dashboard

---

## 💰 Cost Estimate (1 month operation)

| Item | Cost |
|---|---|
| Supabase (Postgres + pgvector) | $25/mo |
| Cohere embedding (10K queries) | $5/mo |
| Claude API (1K queries/day) | $30/mo |
| Modal hosting | $10/mo |
| **Total** | **~$70/mo** |

---

## 🎯 Skills Sin จะได้จากโปรเจ็คนี้

✅ pgvector hands-on
✅ Chunking strategies (semantic, recursive)
✅ Embedding models (Cohere multilingual)
✅ Hybrid retrieval (vector + BM25)
✅ Reranking (Cohere)
✅ LangGraph (stateful agent workflows)
✅ RAGAS evaluation
✅ FastAPI + Streamlit
✅ Docker Compose multi-service
✅ Production patterns (logging, monitoring)

→ พร้อมสมัครงาน DE+AI ระดับ senior ใน Thailand

---

# 2️⃣ AIOps / LLMOps Deep Dive

นี่คือสาย operations ใหม่สุด — ของหายาก ตำราน้อย ลองอธิบายให้เห็นภาพ

## 🎯 What is LLMOps? (vs MLOps)

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

**Convergence:** Modern AI Ops = MLOps + LLMOps + Agent Ops

---

## 🔄 LLMOps Lifecycle

```
1. EXPERIMENTATION
   ├── Prompt engineering
   ├── Model selection
   ├── Embedding selection
   ├── Chunking strategy
   └── Eval baseline
        ↓
2. EVALUATION
   ├── Offline eval (golden set)
   ├── Quality metrics (faithfulness, etc.)
   ├── Cost analysis
   ├── Latency analysis
   └── Safety checks
        ↓
3. DEPLOYMENT
   ├── Prompt versioning (git or LangSmith)
   ├── Canary deploys
   ├── Feature flags
   ├── A/B testing
   └── Rollback plans
        ↓
4. MONITORING
   ├── Token usage + cost
   ├── Latency (p50, p95, p99)
   ├── Error rates
   ├── User feedback
   ├── Quality drift
   └── Safety incidents
        ↓
5. CONTINUOUS IMPROVEMENT
   ├── Failure analysis
   ├── Eval set expansion
   ├── Prompt iteration
   ├── Model upgrades
   └── Retraining (if fine-tuning)
        ↓
   [back to 1]
```

---

## 🎨 Key LLMOps Patterns

### Pattern 1: **Prompt Versioning + Git Flow**

```
prompts/
├── rag_system_v1.txt    (deployed to prod)
├── rag_system_v2.txt    (testing in staging)
└── changelog.md

# Deploy via env variable
PROMPT_VERSION=v2  → load rag_system_v2.txt
```

Or use LangSmith/Langfuse:
```python
from langsmith import Client
prompt = client.pull_prompt("rag-system:v2")
```

### Pattern 2: **Continuous Eval (CI/CD)**

```yaml
# .github/workflows/eval.yml
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

### Pattern 3: **Semantic Caching**

```python
# Cache responses by query embedding similarity
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

### Pattern 4: **Model Routing (Cheap → Expensive)**

```python
def route_query(q: str):
    if is_simple(q):
        return claude_haiku(q)        # $0.001
    elif is_complex(q):
        return claude_sonnet(q)        # $0.015
    else:
        return claude_opus(q)          # $0.075
```

### Pattern 5: **Guardrails (Safety + Quality)**

```python
class Guardrails:
    def pre_process(self, query):
        # Block PII
        # Block prompt injection
        # Block off-topic
        
    def post_process(self, response):
        # Check hallucination
        # Check toxicity
        # Verify citations
```

Tools: Guardrails AI, NeMo Guardrails, Lakera

### Pattern 6: **Observability Stack**

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

### Pattern 7: **Eval-Driven Development**

```
1. Write eval BEFORE feature
2. Implement feature
3. Run eval — must pass threshold
4. Deploy
5. Monitor production → expand eval set
```

---

## 📊 Production LLMOps Metrics

### Quality Metrics:
- **Faithfulness** — answer grounded in retrieved context
- **Answer Relevancy** — answer addresses the question
- **Context Precision** — retrieved chunks relevant
- **Context Recall** — important info retrieved
- **Hallucination Rate** — % of responses with fabricated info
- **Citation Accuracy** — % citations actually support claim

### Cost Metrics:
- **Tokens per query** (input + output)
- **Cost per query**
- **Cache hit rate**
- **Model distribution** (% Haiku vs Sonnet vs Opus)

### Latency Metrics:
- **TTFT** (Time To First Token)
- **TTLT** (Time To Last Token)
- **Retrieval latency**
- **Total p50/p95/p99**

### Safety Metrics:
- **Prompt injection attempts**
- **Toxicity scores**
- **PII leakage incidents**
- **Off-topic queries blocked**

### Business Metrics:
- **User satisfaction** (thumbs up/down ratio)
- **Resolution rate** (% queries solved)
- **Containment rate** (% not escalated to human)

---

## 🛠️ Tool Stack Cheatsheet

| Need | Best Tool | Why |
|---|---|---|
| **Trace agent calls** | LangSmith / Phoenix | See entire chain |
| **Prompt versioning** | LangSmith / Langfuse | Diff + rollback |
| **Eval** | RAGAS + DeepEval | Standard metrics |
| **Cost tracking** | Helicone / Langfuse | Per-query cost |
| **Caching** | Redis + custom logic | Semantic cache |
| **Safety** | Guardrails AI | Pre/post filters |
| **Load test** | Locust + custom | LLM-specific |
| **Drift detection** | Phoenix | Distribution shifts |

---

# 4️⃣ Export ทั้งหมดเป็น MD File## ✅ ครบทุกอย่างที่ถามแล้ว

**975 บรรทัด** — สาระสำคัญในไฟล์:

### 📚 5 Sections:

**1. Tool Comparisons** — เลือก stack
- Vector DB: pgvector ⭐
- Agent framework: LangGraph ⭐
- Eval: RAGAS ⭐
- Embedding: Cohere multilingual-v3 (Thai) ⭐
- + Workflow orchestration, model serving, prompt mgmt

**2. Lumora KB Project** — Thai RAG end-to-end
- 6-week build plan รายสัปดาห์
- Architecture diagram (post-Gold only)
- Tech stack + cost ($70/mo)
- Skills outcomes ที่จะได้

**3. LLMOps Deep Dive** — operations patterns
- MLOps vs LLMOps comparison
- 5-stage lifecycle
- 7 production patterns (prompt versioning, semantic cache, model routing, guardrails, etc.)
- Metrics ครบทุกมุม (quality, cost, latency, safety, business)

**4. Skills Roadmap** — 4 phases 7 เดือน
- Portfolio project order: Lumora KB → NL→SQL → Doc AI → Agent → Production

**5. Appendix** — ของจริงสำหรับ build
- Project structure ครบทุก folder
- docker-compose.yml พร้อมใช้
- Init SQL schema (documents, chunks, query_logs, eval_runs)
- .env template
- Resources + courses + communities

---

## 🎯 Quick Win: เริ่มต้น Week 1 เลยได้

```bash
# Steps พื้นฐาน
mkdir lumora-kb && cd lumora-kb
# Copy structure จาก Section 5.1
# Copy docker-compose.yml จาก Section 5.2
# Copy init.sql จาก Section 5.3
docker compose up -d
# ลอง connect Postgres, ลอง pgvector extension
```

---

อยากให้ผม:
1. **เจาะลึก Week 1 implementation** — ใส่ code จริงสำหรับ Week 1 setup?
2. **Design eval set** — ตัวอย่าง 50 Thai Q&A questions?
3. **Compare กับ The1's GCP stack** — map ไปสู่ Dataplex/Vertex AI/BigQuery?
4. **อีก project** — NL→SQL หรือ Document AI design?
5. **End session** — เก็บ context ทั้งหมด?