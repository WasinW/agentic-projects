# 🧠 DE + ML + AI Complete Reference

> **For:** Sin (Data Engineer @ The1 / Central Group Thailand)
> **Purpose:** Comprehensive knowledge base for transitioning from pure DE → DE+AI hybrid role
> **Scope:** Everything we discussed + extensive additional knowledge
> **Date:** December 2026
> **Status:** Reference document for VS Code session continuation

---

## 📑 Table of Contents

1. [The Evolution of Data Engineering](#1-the-evolution-of-data-engineering)
2. [Modern Data + AI Architecture](#2-modern-data--ai-architecture)
3. [RAG Deep Dive](#3-rag-deep-dive)
4. [Agent Systems](#4-agent-systems)
5. [MLOps Fundamentals](#5-mlops-fundamentals)
6. [LLMOps / AIOps](#6-llmops--aiops)
7. [Production Patterns & Use Cases](#7-production-patterns--use-cases)
8. [Tool Landscape (Comprehensive)](#8-tool-landscape)
9. [Infrastructure: Local + Cloud](#9-infrastructure-local--cloud)
10. [CI/CD, Governance, Testing, Ops](#10-cicd-governance-testing-ops)
11. [Practical Project: Lumora KB](#11-practical-project-lumora-kb)
12. [Skills Roadmap](#12-skills-roadmap)
13. [Sin-Specific Context](#13-sin-specific-context)
14. [Common Pitfalls](#14-common-pitfalls)
15. [Resources](#15-resources)

---

# 1. The Evolution of Data Engineering

## 1.1 Era Timeline

```
Era 1 (2010-2015): Hadoop/Spark
─────────────────────────────────
- Batch ETL
- Hadoop ecosystem (HDFS, Hive, MapReduce)
- Spark for faster processing
- Data warehouses (Teradata, Oracle)
- Role: "Data plumber" — move data A → B

Era 2 (2016-2020): Cloud Data Warehouses
─────────────────────────────────
- BigQuery, Snowflake, Redshift dominate
- dbt for SQL-based transformations
- Airflow for orchestration
- "Modern Data Stack" emerges
- Role: "Analytics Engineer" emerges

Era 3 (2021-2023): Lakehouse + Streaming
─────────────────────────────────
- Iceberg, Delta Lake, Hudi
- Kafka + Flink streaming
- Medallion Architecture (Bronze/Silver/Gold)
- Data Mesh / Data Fabric concepts
- Role: Platform Engineer focus

Era 4 (2024-NOW): AI-Native Data Engineering
─────────────────────────────────
- Vector databases mainstream
- RAG = standard production pattern
- LLM-powered data tooling
- Agents in data workflows
- DE convergence with ML/AI
- Role: DE + AI hybrid

Era 5 (2026+): Autonomous Data Platforms
─────────────────────────────────
- Self-healing pipelines
- Agent-driven data ops
- Natural language interfaces standard
- Multi-modal data as first-class
- Role: AI Platform Architect
```

## 1.2 Convergence of 3 Pipelines

```
Traditional (Separate Teams):
─────────────────────────────
Data Pipeline      ←─ Data Engineers
ML Pipeline        ←─ ML Engineers  
AI/Agent Pipeline  ←─ AI Engineers / Research

Modern (Convergent):
─────────────────────
[All 3 pipelines] ──► Single platform team
                      Hybrid roles (DE+ML+AI)
                      Shared infrastructure
                      Unified observability
```

**Why convergent?**
1. **LLMs need data** → RAG requires retrieval = DE work
2. **Agents need tools** → Tools are data APIs
3. **Production AI needs pipelines** → Orchestration, retries, monitoring
4. **Shared infrastructure** → Same compute, storage, observability
5. **Single source of truth** → Data, features, embeddings together

## 1.3 The New DE Role Spectrum

```
Pure DE ←─────────────────────────────► AI Engineer
   │
   ├─ DE (Classic)        — Pipelines, warehouses
   ├─ DE + ML             — + Feature stores, model serving
   ├─ DE + AI (RAG)       — + Vector, RAG patterns
   ├─ DE + Agent          — + Tool design, agent workflows
   ├─ AI Platform Eng     — + Eval frameworks, prompt mgmt
   └─ AI Engineer         — Mostly model/agent work
```

**Sin's target:** DE + AI (RAG) → DE + Agent over 6-12 months

---

# 2. Modern Data + AI Architecture

## 2.1 Beyond Medallion: Extended Architecture

```
Traditional Medallion (2020-2024):
─────────────────────────────────
Bronze (Raw) → Silver (Clean) → Gold (Business) → BI/Dashboard

AI-Native Extended (2025-2026):
─────────────────────────────────
Bronze → Silver → Gold → Platinum → Diamond
                              ↓         ↓
                          (Features) (AI-Ready)
                              ↓         ↓
                   ┌──────────┴─────────┴───────────┐
                   ↓          ↓         ↓           ↓
              [ML Models] [Vector  ] [Agent    ] [Application
                         [Store    ] [State    ] [Layer]
                              ↓         ↓           ↓
                              └─────────┴───────────┘
                                       ↓
                              [Observability Loop]
                                       ↓
                              ─── feeds back to Bronze ─→
```

## 2.2 Layer Definitions

### Bronze Layer — Raw
- Direct copy from source
- Immutable, append-only
- Original schema preserved
- Audit trail

### Silver Layer — Cleaned
- Validated, deduplicated
- Schema normalized
- Quality checks passed
- Joinable across sources

### Gold Layer — Business
- Aggregated, denormalized
- Business logic applied
- KPI-ready
- Optimized for query

### 🥇 Platinum Layer — Features (NEW)
- Pre-computed features for ML
- Point-in-time correct
- Online + offline serving
- **Tools:** Feast, Tecton, Databricks Feature Store, Vertex AI Feature Store

### 💎 Diamond Layer — AI-Ready (NEW)
- Vector embeddings of business entities
- Multi-modal data normalized
- Knowledge graphs
- Chunked + tagged for retrieval
- **Tools:** pgvector, Pinecone, Weaviate, Qdrant, BQ Vector Search

### 🤖 Agent State Layer (NEW)
- Short-term memory (conversation)
- Long-term memory (user preferences)
- Tool execution logs
- Agent checkpoints
- **Tools:** Redis, MongoDB, LangGraph Checkpointer, Postgres

### 📊 Application Layer
- REST/GraphQL/gRPC APIs
- ML serving endpoints
- RAG endpoints
- Agent endpoints
- **Tools:** FastAPI, Modal, BentoML, Hono, Cloud Run

### 🔄 Observability + Feedback Loop
- User signals (thumbs, clicks, dwell time)
- Agent traces (tool calls, reasoning)
- Error logs, latency, cost
- → flows back to Bronze for retraining
- **Tools:** LangSmith, Phoenix, Langfuse, Datadog

## 2.3 Data Types in AI-Native Architecture

```
Structured Data:
├─ Relational (SQL tables)
├─ Time-series
├─ Geospatial
└─ Graph

Semi-Structured:
├─ JSON/NoSQL
├─ Events/Logs
└─ XML

Unstructured (NEW emphasis):
├─ Text (docs, emails, chat)
├─ Images
├─ Audio
├─ Video
├─ PDFs
└─ Code

Derived:
├─ Embeddings (vectors)
├─ Features (ML-ready)
├─ Predictions
├─ Generated content
└─ Agent memory
```

---

# 3. RAG Deep Dive

## 3.1 RAG Fundamentals

**Why RAG?**
- LLMs have knowledge cutoff
- Can't access private data
- Hallucination without grounding
- Cost: cheaper than fine-tuning
- Updatable: just change data

**Core flow:**
```
1. Query → embed → search vector store → retrieve top-k chunks
2. Stuff chunks into LLM prompt → generate answer with citations
```

## 3.2 Chunking Strategies

| Strategy | Description | Best for |
|---|---|---|
| **Fixed-size** | N tokens with overlap | Simple text |
| **Semantic** | Break at meaning boundaries | Most use cases |
| **Recursive** | Split by separator hierarchy (paragraph→sentence) | Mixed content |
| **Document-aware** | Respect doc structure (sections, headers) | Technical docs |
| **Sliding window** | Overlap-heavy for context | Code, dense text |
| **Sentence-window** | Embed sentence, retrieve neighbors | Precise retrieval |
| **Hierarchical** | Multiple chunk sizes | Long documents |
| **Agentic chunking** | LLM decides boundaries | Highest quality, costly |

**Best practices:**
- Chunk size: 200-800 tokens (sweet spot 400-500)
- Overlap: 10-20% of chunk size
- Preserve sentence boundaries
- Include metadata (source, section, doc title)

## 3.3 Embedding Models

| Model | Dim | Cost | Best for |
|---|---|---|---|
| text-embedding-3-small | 1536 | $0.02/1M | English, fast |
| text-embedding-3-large | 3072 | $0.13/1M | English, high quality |
| voyage-3 | 1024 | $0.06/1M | English, best quality |
| voyage-code-3 | 1024 | $0.18/1M | Code |
| cohere-embed-multilingual-v3 | 1024 | $0.10/1M | **Thai + 100 langs** |
| multilingual-e5-large | 1024 | Free (self-host) | Multilingual budget |
| BGE-M3 | 1024 | Free (self-host) | Open source SOTA |
| Vertex AI text-embedding | 768 | $0.025/1M | GCP-native |

**For Thai content:** Cohere multilingual-v3 or self-host BGE-M3

## 3.4 Retrieval Strategies

### 3.4.1 Vector Search (Dense)
- Cosine similarity, dot product, L2 distance
- Captures semantic meaning
- Misses exact keywords sometimes

### 3.4.2 BM25 Search (Sparse/Keyword)
- TF-IDF based
- Exact match excellent
- Misses synonyms

### 3.4.3 Hybrid Search ⭐
```
Vector(semantic) + BM25(keyword) → Reciprocal Rank Fusion → top-k
```

Almost always better than either alone.

### 3.4.4 Reranking
- Initial retrieval gets top-50
- Cross-encoder reranks to top-10
- Cohere Rerank, BGE Reranker, Voyage Rerank

### 3.4.5 Filtering Pre-Retrieval
- Date range
- Source type
- Access permissions (security)
- Tags/categories

## 3.5 Advanced RAG Patterns

### Query Rewriting
- Resolve pronouns ("his" → "John's")
- Expand abbreviations
- Generate variations for retrieval
- Multi-step decomposition

### HyDE (Hypothetical Document Embeddings)
```
Query → LLM generates "ideal answer" → Embed answer → Search
```
- Often better than embedding query directly
- Works for sparse/specialized domains

### Self-RAG
- LLM decides whether to retrieve
- Retrieves multiple times if needed
- Self-critiques retrieved chunks
- Often higher quality

### Corrective RAG (CRAG)
```
Retrieve → Grade chunks → 
  ├── Sufficient: Generate
  ├── Insufficient: Web search
  └── Mixed: Decompose + retry
```

### Graph RAG
- Build knowledge graph from docs
- Query graph for relationships
- Combine with vector for semantic
- Excellent for connected reasoning

### Multi-Vector Retrieval
- One doc → multiple embeddings (summary + chunks + questions)
- Retrieve based on best match
- Higher accuracy, more storage

### ColBERT (Late Interaction)
- Per-token embeddings
- Higher quality, more compute
- Good for nuanced retrieval

## 3.6 Long-Context vs RAG

```
Long-context wins when:
- Need full document context
- Document <100K tokens
- One-shot tasks
- Cost not primary concern

RAG wins when:
- Knowledge base >100K tokens
- Multi-user (cache embeddings)
- Need citations
- Cost-sensitive
- Need to update knowledge

Hybrid: Use both
- RAG to find relevant chunks
- Long-context for deep analysis
```

## 3.7 Multimodal RAG

### Modalities:
- Text + images (e.g., document with diagrams)
- Text + tables (e.g., financial reports)
- Text + code
- Video (frames + transcript)
- Audio (transcript + embeddings)

### Approaches:
1. **Single multimodal model** (CLIP, GPT-4V) — embed all in same space
2. **Multi-vector** — separate text/image embeddings, retrieve both
3. **Caption-based** — caption images, embed captions

### Tools:
- CLIP / OpenCLIP
- LLaVA / Llama 3 Vision
- Claude 3 (vision)
- Gemini Pro Vision

## 3.8 RAG Evaluation

### Retrieval Metrics:
- **Recall@k** — % relevant chunks in top-k
- **MRR** (Mean Reciprocal Rank)
- **NDCG** (Normalized Discounted Cumulative Gain)
- **Hit Rate** — % queries with at least 1 relevant chunk

### Generation Metrics:
- **Faithfulness** — answer grounded in context
- **Answer Relevancy** — addresses question
- **Context Precision** — retrieved chunks relevant
- **Context Recall** — important info retrieved
- **Citation Accuracy** — citations support claim
- **Hallucination Rate** — % fabricated info

### Tools:
- **RAGAS** — standard library
- **DeepEval** — comprehensive
- **TruLens** — multi-metric
- **Phoenix** — production observability

---

# 4. Agent Systems

## 4.1 Agent Fundamentals

**Definition:** Agent = LLM that can:
1. **Plan** — decompose task into steps
2. **Use tools** — call functions/APIs
3. **Observe** — see results
4. **Adapt** — adjust based on feedback

**vs Workflow:**
- Workflow: predefined steps
- Agent: dynamic, decides next step

## 4.2 Anthropic's "Building Effective Agents" Patterns

### Pattern 1: Prompt Chaining
```
Input → LLM₁ → Output₁ → LLM₂ → Output₂ → Final
```
Linear sequence, each step builds on previous.

### Pattern 2: Routing
```
Input → Router → 
  ├── Route A → Specialist A
  ├── Route B → Specialist B
  └── Route C → Specialist C
```
Classify, then dispatch.

### Pattern 3: Parallelization
```
Input → ┌── LLM₁ → Output₁
        ├── LLM₂ → Output₂
        └── LLM₃ → Output₃
              ↓
            Aggregator → Final
```
Run in parallel, aggregate.

### Pattern 4: Orchestrator-Workers
```
Orchestrator (LLM) decides → 
  ├── Spawn Worker₁ (task A)
  ├── Spawn Worker₂ (task B)
  └── Spawn Worker₃ (task C)
        ↓
     Synthesize results
```
Dynamic task decomposition.

### Pattern 5: Evaluator-Optimizer
```
Generate (LLM) → Evaluate (LLM) → 
  ├── Pass: return
  └── Fail: Optimize → retry
```
Iterative improvement loop.

### Pattern 6: Agent (full autonomous)
```
While not done:
  Plan → Use Tool → Observe → Adapt
```
Open-ended, multi-step, dynamic.

## 4.3 Tool Design

**Good tools have:**
- Single responsibility
- Clear input/output schema
- Descriptive name + docstring
- Idempotent when possible
- Error handling
- Logging

**Tool categories:**
- **Data tools** — query DB, search docs, lookup
- **Action tools** — send email, create ticket, update record
- **Computation tools** — calculator, code interpreter
- **Information tools** — web search, weather, news
- **Meta tools** — ask user, delegate to other agent

**Tool examples (for Sin's use case):**
```python
@tool
def search_products(query: str, category: Optional[str] = None) -> list[Product]:
    """Search products by natural language query."""
    
@tool
def get_trending_items(platform: str, top_n: int = 10) -> list[Product]:
    """Get trending products from a platform."""
    
@tool
def generate_content(product_id: str, style: str) -> Content:
    """Generate marketing content for a product in given style."""
```

## 4.4 Memory Systems

### Short-term (working) memory:
- Conversation history
- Current task state
- Recent observations
- **Implementation:** LangGraph state, in-memory dict

### Long-term memory:
- User preferences
- Learned facts
- Past successful workflows
- **Implementation:** Vector store, Postgres, knowledge graph

### Episodic memory:
- Specific past interactions
- Lessons learned
- **Implementation:** Logged + indexed

### Procedural memory:
- How to do tasks
- Tool usage patterns
- **Implementation:** Stored prompts, code

## 4.5 Planning Approaches

### ReAct (Reasoning + Acting)
```
Thought: I need to find the user's order
Action: search_orders(user_id="123")
Observation: Found 3 orders
Thought: Need to check the latest
Action: get_order_details(order_id="456")
...
```

### Plan-and-Execute
```
1. Generate full plan upfront
2. Execute steps sequentially
3. Replan if blocked
```

### Tree of Thoughts
- Explore multiple reasoning paths
- Evaluate at each branch
- Pick best path
- More compute, higher quality

### Reflection
- Generate
- Self-critique
- Improve
- Loop

## 4.6 Multi-Agent Systems

### Patterns:
- **Hierarchical** — Manager → Workers
- **Sequential** — Pipeline of specialists
- **Debate** — Multiple agents argue
- **Voting** — Multiple agents propose, vote
- **Network** — Free communication

### Frameworks:
- **CrewAI** — Role-based teams
- **AutoGen** — Conversation patterns
- **LangGraph** — Graph-based
- **MetaGPT** — Software dev focused

### When to use multi-agent:
✅ Complex tasks needing specialization
✅ Need diverse perspectives
✅ Parallel processing helps
❌ Simple tasks (single agent better)
❌ Strict cost/latency budgets

## 4.7 Agent Frameworks Comparison

| Framework | Strength | Weakness | Use when |
|---|---|---|---|
| **LangGraph** ⭐ | Stateful, debuggable, production-ready | LangChain dependency | Production agents |
| LangChain | Massive ecosystem | Abstraction overhead | Quick prototypes |
| LlamaIndex | RAG-focused | Less agent-focused | RAG-heavy apps |
| CrewAI | Multi-agent easy | Less mature | Multi-agent teams |
| AutoGen | Microsoft-backed | Research-grade | Research |
| Pydantic AI | Type-safe | New (2025) | Type-heavy projects |
| Anthropic SDK | Max control | More code | Simple, controlled |
| Vercel AI SDK | Frontend AI | JS only | Web apps |

---

# 5. MLOps Fundamentals

## 5.1 ML Lifecycle

```
1. Problem Definition → metric, baseline
2. Data Collection → labeling, augmentation
3. Feature Engineering → feature store
4. Model Training → experiments
5. Evaluation → offline metrics
6. Deployment → A/B test, canary
7. Monitoring → drift, performance
8. Retraining → feedback loop
```

## 5.2 Experiment Tracking

**What to track:**
- Code version (git commit)
- Data version (DVC, lakeFS)
- Hyperparameters
- Metrics
- Artifacts (model files)
- Environment (Docker, requirements)

**Tools:**
- **MLflow** — open source standard
- **Weights & Biases** — best UI
- **Comet** — feature-rich
- **Neptune** — collaborative
- **Vertex AI Experiments** — GCP

## 5.3 Feature Stores

**Why?**
- Reuse features across models
- Training-serving consistency
- Point-in-time correctness
- Online + offline serving

**Architecture:**
```
Data sources → Feature Pipeline → 
  ├── Offline store (BigQuery, Snowflake) — training
  └── Online store (Redis, DynamoDB) — serving
       ↓
   Both serve features by entity ID + timestamp
```

**Tools:**
- **Feast** ⭐ (open source, lightweight)
- **Tecton** (managed, enterprise)
- **Vertex AI Feature Store** (GCP)
- **Databricks Feature Store**

## 5.4 Model Serving

### Batch inference:
- Predict for all users overnight
- Store predictions in DB
- Simple, cheap
- Latency: high

### Real-time online:
- Predict on request
- REST/gRPC endpoint
- Latency: ms
- Tools: TorchServe, TF Serving, Triton, BentoML, Modal

### Streaming inference:
- React to events
- Kafka consumer + model
- Latency: sub-second
- Tools: Flink, Spark Streaming

### Edge inference:
- On-device
- ONNX, TFLite, CoreML
- No network needed
- Privacy-preserving

## 5.5 Drift Detection

**Types of drift:**

### Data Drift
- Input distribution changes
- E.g., user demographics shift
- Detection: PSI, KL divergence, KS test

### Concept Drift
- Input → output relationship changes
- E.g., what users like changes
- Detection: prediction accuracy decline

### Label Drift
- Label distribution changes
- E.g., more fraud now
- Detection: class balance monitoring

### Tools:
- **Evidently AI** — open source
- **Arize** — production
- **Fiddler** — enterprise
- **WhyLabs** — privacy-focused

## 5.6 Model Governance

- Model registry (version, lineage)
- Model card (intended use, limitations)
- Bias/fairness audit
- Regulatory compliance (EU AI Act, etc.)
- Decision logging
- Right to explanation

---

# 6. LLMOps / AIOps

## 6.1 LLMOps vs MLOps

```
MLOps:                          LLMOps:
- Train models                  - Use API models
- Feature stores                - Prompts + RAG context
- Track experiments             - Track prompt versions
- Model versioning              - Prompt + model + chain versioning
- Drift detection               - Hallucination + relevance monitoring
- Cost: GPU training            - Cost: tokens + retrieval
- Latency: ms                   - Latency: seconds
- Deterministic                 - Stochastic
```

## 6.2 LLMOps Lifecycle

```
EXPERIMENTATION
├── Prompt engineering
├── Model selection (Claude/GPT/Gemini)
├── Embedding selection
├── Chunking strategy
└── Eval baseline
        ↓
EVALUATION
├── Offline eval (golden set)
├── Quality metrics
├── Cost analysis
├── Latency analysis
└── Safety checks
        ↓
DEPLOYMENT
├── Prompt versioning
├── Canary deploys
├── Feature flags
├── A/B testing
└── Rollback plans
        ↓
MONITORING
├── Token usage + cost
├── Latency (p50, p95, p99)
├── Error rates
├── User feedback
├── Quality drift
└── Safety incidents
        ↓
CONTINUOUS IMPROVEMENT
├── Failure analysis
├── Eval set expansion
├── Prompt iteration
└── Model upgrades
        ↓
   [loop back]
```

## 6.3 Key Patterns

### Prompt Versioning
```
prompts/
├── rag_system_v1.txt    (prod)
├── rag_system_v2.txt    (staging)
└── changelog.md

# Deploy via env
PROMPT_VERSION=v2
```

### Continuous Eval (CI/CD)
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

### Semantic Caching
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

### Model Routing
```python
def route_query(q: str):
    if is_simple(q):
        return claude_haiku(q)          # cheap
    elif is_complex(q):
        return claude_sonnet(q)         # mid
    else:
        return claude_opus(q)           # premium
```

### Guardrails
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

Tools: Guardrails AI, NeMo Guardrails, Lakera, LLM Guard

### Observability Stack
```
Application
   ↓
Tracer (LangSmith / Langfuse / Phoenix)
   ↓
Metrics + Logs + Traces
   ↓
Alerts (Slack, PagerDuty)
   ↓
Dashboards (Grafana)
```

### Eval-Driven Development
```
1. Write eval BEFORE feature
2. Implement feature
3. Run eval — must pass threshold
4. Deploy
5. Monitor → expand eval set
```

## 6.4 Cost Optimization

### Token-level:
- Shorter system prompts
- Strip unnecessary context
- Compress conversation history
- Truncate long inputs

### Model-level:
- Use smaller models when possible
- Model routing (cheap → expensive)
- Fine-tune smaller for specific tasks

### Caching:
- Exact match cache (Redis)
- Semantic cache (vector similarity)
- Response caching with TTL
- Prefix caching (Claude/OpenAI native)

### Retrieval:
- Embed once, retrieve many
- Smaller chunks where possible
- Cache embeddings

### Batch processing:
- Async batch where latency allows
- OpenAI/Anthropic batch API (50% discount)

### Real-world savings:
- Caching: 30-70% reduction
- Model routing: 40-60% reduction
- Batch API: 50% reduction
- Combined: can hit 80%+ savings

## 6.5 Production Metrics

### Quality:
- Faithfulness, Answer Relevancy
- Context Precision, Context Recall
- Hallucination Rate
- Citation Accuracy

### Cost:
- Tokens per query (in/out)
- Cost per query
- Cache hit rate
- Model distribution

### Latency:
- TTFT (Time To First Token)
- TTLT (Time To Last Token)
- Retrieval latency
- p50/p95/p99

### Safety:
- Prompt injection attempts
- Toxicity scores
- PII leakage
- Off-topic blocked

### Business:
- User satisfaction (👍/👎)
- Resolution rate
- Containment rate (% not escalated)

## 6.6 Hallucination Mitigation

### Prevention:
- Strong system prompt ("only answer from context")
- Citation requirements
- Temperature low (0-0.3)
- Constitutional AI patterns

### Detection:
- LLM-as-judge: "Is this grounded in context?"
- Citation verification
- Cross-check with another model
- Fact-checking against knowledge base

### Response:
- Reject if hallucinated
- Show confidence score
- Cite sources
- "I don't know" is OK

---

# 7. Production Patterns & Use Cases

## 7.1 RAG Patterns

### Pattern 1: Internal Knowledge Base
- HR docs, policies, processes
- Slack/Teams bot interface
- Citation required
- Department-level access control

### Pattern 2: Customer Support
- Product docs + ticket history
- Multi-channel (chat, email, voice)
- Escalation to human
- Sentiment monitoring

### Pattern 3: Sales Enablement
- Product info + competitor intel
- CRM integration
- Personalized to deal stage
- Talking points generation

### Pattern 4: Legal/Compliance
- Contract analysis
- Regulation lookup
- Audit trails (every query logged)
- Strict source verification

### Pattern 5: Research Assistant
- Multi-document synthesis
- Citation graphs
- Long-context capability
- Comparison across sources

### Pattern 6: Code Assistant
- Code repositories
- API documentation
- Code-specific embeddings
- IDE integration

## 7.2 Agent Patterns

### Pattern 1: Conversational Analytics
- User: "Show me Q3 revenue by region"
- Agent: parses → SQL → BQ → chart
- Tools: schema lookup, SQL gen, chart gen
- Used at: Cube, ThoughtSpot, Hex

### Pattern 2: Data Pipeline Copilot
- "Why did pipeline X fail?"
- Agent: query logs → check lineage → suggest fix
- Tools: log search, lineage API, runbook lookup

### Pattern 3: Marketing Campaign Generator
- "Create campaign for product X targeting Y"
- Agent: research → generate copy → suggest channels → set budget
- Tools: market research, copy gen, A/B test setup

### Pattern 4: Customer 360 Agent
- "Tell me about customer C"
- Agent: aggregates CRM + behavior + support
- Tools: multi-source query, summarization

### Pattern 5: Content Production
- "Make video script for trend X"
- Agent: trend research → script → storyboard → voice
- Tools: trend API, script gen, image gen, voice gen

### Pattern 6: Onboarding Assistant
- New employee questions
- Agent: HR docs + tools + escalation
- Personalized to role

## 7.3 Document Processing Patterns

### Pattern 1: Intelligent ETL
- PDFs → OCR → LLM extract → structure → DB
- Validation per field
- Confidence scoring
- Human review for low-confidence

### Pattern 2: Multi-modal Extraction
- Invoices: text + tables + logos
- Receipts: items + prices + totals
- Forms: structured fields
- Tools: Gemini, Claude (vision), GPT-4V

### Pattern 3: Document Classification
- Type detection
- Routing based on type
- Tagging for retrieval

## 7.4 Real-time AI Patterns

### Pattern 1: Streaming Recommendations
- User behavior → realtime features → model → recommendation
- Latency: <100ms
- Stack: Kafka + Flink + online feature store + model server

### Pattern 2: Fraud Detection
- Transaction → enrichment → score → decision
- Latency: <50ms
- Stack: streaming features + low-latency model + decision engine

### Pattern 3: Live Personalization
- Page request → user context → ranking
- Latency: <200ms
- Stack: vector lookup + reranking

---

# 8. Tool Landscape

## 8.1 Comprehensive Stack

### Storage / Data Lake:
- **Cloud:** S3, GCS, R2, Azure Blob
- **Lakehouse:** Delta Lake, Iceberg, Hudi
- **Lakehouse platforms:** Databricks, Snowflake, BigQuery, Fabric

### Compute:
- **Batch:** Spark, Dataflow, Athena, BigQuery
- **Streaming:** Flink, Spark Streaming, Beam
- **Serverless:** AWS Lambda, Cloud Run, Modal
- **Container:** K8s, ECS

### Orchestration:
- **Airflow** — standard, mature
- **Prefect** — modern, Python-native
- **Dagster** — asset-based
- **Temporal** — durable, agent-friendly
- **GitHub Actions** — for simple CI tasks

### Transformation:
- **dbt** — SQL-first, standard
- **SQLMesh** — modern dbt alternative
- **dataform** — GCP-native dbt
- **Python** — flexible

### Quality:
- **dbt tests** — SQL tests
- **great_expectations** — flexible
- **Soda** — cloud + OSS
- **Monte Carlo** — data observability
- **Bigeye** — automated monitoring

### Catalog / Governance:
- **DataHub** — open source
- **Unity Catalog** — Databricks
- **Dataplex** — GCP
- **Atlan** — enterprise
- **OpenMetadata** — OSS

### Vector Database:
- **pgvector** ⭐ — start here
- **Qdrant** — production self-host
- **Pinecone** — managed
- **Weaviate** — multimodal
- **Chroma** — local dev
- **Milvus** — massive scale

### Embedding:
- **OpenAI** — text-embedding-3
- **Cohere** ⭐ — multilingual
- **Voyage** — quality leader
- **Vertex AI** — GCP-native
- **BGE-M3** — open source

### LLM:
- **Anthropic Claude** — quality, safety
- **OpenAI GPT** — ecosystem
- **Google Gemini** — multimodal
- **Meta Llama** — open source
- **Mistral** — efficient
- **Groq** — fast inference

### Agent Framework:
- **LangGraph** ⭐ — stateful
- **LangChain** — ecosystem
- **LlamaIndex** — RAG
- **CrewAI** — multi-agent
- **Pydantic AI** — type-safe

### Eval:
- **RAGAS** ⭐ — RAG
- **DeepEval** — general
- **TruLens** — multi-metric
- **LangSmith** — production
- **Phoenix** — open source

### Observability:
- **LangSmith** — LangChain ecosystem
- **Langfuse** — open source LangSmith
- **Phoenix** — Arize OSS
- **Helicone** — cost focused
- **W&B** — ML tracking

### Feature Store:
- **Feast** ⭐ — OSS
- **Tecton** — managed
- **Vertex AI** — GCP
- **Databricks** — DB-integrated

### Model Serving:
- **Modal** ⭐ — serverless
- **BentoML** — packaging
- **Vertex AI Endpoints** — GCP
- **Sagemaker** — AWS
- **vLLM** — LLM-specific

### Prompt Management:
- **LangSmith**
- **Langfuse**
- **Promptfoo** — testing
- **PromptLayer**

### CI/CD:
- **GitHub Actions** — standard
- **GitLab CI** — self-host friendly
- **ArgoCD** — K8s GitOps
- **Dagster Cloud** — data CI

### IaC:
- **Terraform** ⭐ — standard
- **Pulumi** — code-based
- **CDK** — AWS/GCP
- **OpenTofu** — Terraform fork

---

# 9. Infrastructure: Local + Cloud

## 9.1 Local Stack (Free, $0)

| Layer | Tool | Purpose |
|---|---|---|
| Storage | MinIO | S3-compatible local |
| Compute | Docker + Python | Containerized dev |
| Orchestration | Prefect / Dagster local | Pipeline dev |
| Warehouse | DuckDB / Postgres | SQL local |
| Vector | pgvector / Chroma | Vector local |
| ML tracking | MLflow | Experiment local |
| Feature store | Feast (file) | Feature local |
| LLM | Ollama (Llama, Mistral) | Local inference |
| Embedding | sentence-transformers | Local embed |
| Agent | LangGraph | Local agents |
| API | FastAPI / Hono | Local API |
| Observability | Phoenix | Local traces |

**Cost: $0**
**Use case: Learn fundamentals, experiment safely**

## 9.2 Low-Cost Cloud ($30-150/mo)

| Layer | Tool | Cost |
|---|---|---|
| Storage | Cloudflare R2 | $0.015/GB |
| Compute | Modal / Fly.io | $5-30/mo |
| Orchestration | GitHub Actions | Free tier |
| Warehouse | Supabase Postgres | $25/mo |
| Vector | Supabase pgvector | Included |
| LLM | Claude API | Pay per token |
| Embedding | Cohere API | Pay per token |
| Observability | LangSmith / Langfuse | Free tier |

**Cost: $30-150/mo for moderate use**
**Use case: Production-ready apps, low budget**

## 9.3 Enterprise Cloud

### GCP Stack (Sin's familiar):
- BigQuery (warehouse)
- Vertex AI (ML platform)
- Dataflow (Beam)
- Cloud Composer (Airflow)
- Cloud Run (containers)
- Dataplex (governance)
- BigQuery Vector Search
- Vertex AI Feature Store

### AWS Stack:
- Redshift (warehouse)
- Sagemaker (ML)
- Glue (ETL)
- MSK (Kafka)
- Lambda
- Lake Formation
- Bedrock (LLM)
- OpenSearch (vector)

### Azure Stack:
- Synapse Analytics
- Fabric (lakehouse)
- Data Factory
- AKS
- Cognitive Services
- Azure AI Search (vector)
- Foundry

### Databricks (multi-cloud):
- Delta Lake
- Unity Catalog
- Mosaic AI
- Vector Search
- Feature Store

## 9.4 Recommended Stage Progression

```
Stage 1: Pure Local (Month 1-2)
─────────────────────────────────
Docker compose with:
  - Postgres + pgvector
  - MinIO  
  - Ollama
  - Prefect
  - FastAPI
  - Streamlit
Cost: $0
Use case: Learn fundamentals

Stage 2: Hybrid (Month 3-4)
───────────────────────────
Local infra + cloud APIs:
  - Local Postgres + pgvector
  - Claude API / OpenRouter
  - GitHub Actions CI
  - Modal (heavy compute)
Cost: $10-30/mo
Use case: Build first real RAG

Stage 3: Cloud-Native (Month 5+)
────────────────────────────────
Full cloud:
  - Supabase
  - Cloudflare Workers + Modal
  - Claude API
  - LangSmith
Cost: $50-150/mo
Use case: Production apps
```

---

# 10. CI/CD, Governance, Testing, Ops

## 10.1 CI/CD for AI/Data

### Pipeline stages:
```
Code commit
   ↓
Lint (ruff, mypy)
   ↓
Unit tests (pytest)
   ↓
Data tests (great_expectations, dbt)
   ↓
Model eval (if model changed)
   ↓
Security scan (snyk, trivy)
   ↓
Build (Docker, wheels)
   ↓
Deploy (Terraform → Cloud Run/K8s)
   ↓
Smoke tests
   ↓
Promote: dev → sit → uat → prod
```

### AI-specific CI/CD:
- **Prompt versioning** — git-tracked
- **Model versioning** — semantic + A/B
- **Embedding versioning** — reindex if changed
- **Eval gates** — auto-block bad models
- **Cost gates** — flag if cost explodes

## 10.2 Governance Layers

```
Catalog & Discovery
├─ DataHub / Unity / Dataplex
├─ Business glossary
└─ Domain ownership

Lineage
├─ OpenLineage / Marquez
├─ dbt lineage
└─ Cross-system lineage

Access Control
├─ RBAC / ABAC
├─ Row-level security
└─ Column masking (PII)

Quality
├─ Soda / great_expectations
└─ Monte Carlo / Bigeye

Privacy & Compliance
├─ PDPA / GDPR mapping
├─ PII detection
├─ Retention policies
└─ Audit logs

AI Governance (NEW)
├─ Model card registry
├─ Prompt registry
├─ Eval history
├─ Bias/fairness monitoring
├─ Hallucination tracking
└─ Tool usage audit (agents)
```

## 10.3 Testing Pyramid

```
                ┌───────────────────┐
                │  Production       │
                │  Monitoring       │
                │  (Continuous Eval)│
                └─────────┬─────────┘
                          │
              ┌───────────┴───────────┐
              │   UAT (Real Users)    │
              └───────────┬───────────┘
                          │
          ┌───────────────┴───────────────┐
          │   SIT (Integration)            │
          └───────────────┬───────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │   Unit Tests (Per Component)       │
        └───────────────────────────────────┘
```

### Per layer:

| Layer | Tests | Tools |
|---|---|---|
| Code | Unit, integration | pytest |
| Data | Schema, range, freshness | great_expectations, dbt |
| Model | Accuracy, drift, fairness | MLflow eval, DeepChecks |
| RAG | Retrieval recall, faithfulness | RAGAS |
| Agent | Task completion, tool use | LangSmith evals |
| API | Functional, load, security | Postman, Locust |
| E2E | User journeys | Playwright |

### AI-specific tests:
- **Golden datasets** — held-out, must pass
- **Adversarial** — prompt injection
- **Bias** — demographic parity
- **Cost** — must complete under $X
- **Latency** — p95 < threshold

## 10.4 The 4 Ops Convergence

```
DevOps + DataOps + MLOps + AIOps = "Modern Data+AI Ops"
```

### DevOps (Foundation)
- IaC (Terraform)
- CI/CD pipelines
- Container orchestration
- Observability (logs, metrics, traces)
- Tools: GitHub Actions, Terraform, Datadog

### DataOps (Data-Specific)
- Pipeline orchestration (Airflow/Prefect)
- Data quality monitoring
- Data lineage
- Schema evolution
- Tools: Airflow, dbt, Soda, Monte Carlo

### MLOps (ML-Specific)
- Experiment tracking
- Model registry
- Feature store
- Model serving
- Drift monitoring
- A/B testing
- Retraining pipelines
- Tools: MLflow, Kubeflow, Vertex AI, Sagemaker

### AIOps / LLMOps (AI-Specific) ⭐ NEW
- Prompt management
- Token cost tracking
- LLM evaluation
- RAG performance
- Agent observability
- Hallucination detection
- Safety monitoring
- Tools: LangSmith, Phoenix, Helicone, Langfuse

### Convergent observability:
```
Single platform for all:
  Datadog / Grafana + Phoenix
  = traces from agents to data to infra
```

---

# 11. Practical Project: Lumora KB

## 11.1 Project Definition

**Name:** Lumora KB — Thai Knowledge Base RAG
**Goal:** Hands-on AI+DE practice + portfolio piece
**Duration:** 6 weeks
**Cost:** ~$70/mo

## 11.2 Use Case

- **User:** Sin (Stage 1), team (Stage 2)
- **JTBD:** Ask Thai content questions, get cited answers
- **Success:** 85%+ accuracy, <3s latency, <$0.05/query

## 11.3 Architecture

```
Gold Documents (already cleaned)
        ↓
💎 Diamond Layer (Chunk + Embed)
        ↓
┌───────┴────────┐
↓                ↓
Vector Store     Metadata Store
(pgvector)       (Postgres)
        ↓
🤖 Agent Layer (LangGraph)
1. Query rewrite
2. Hybrid retrieval (vector + BM25)
3. Rerank (Cohere)
4. LLM generate (Claude)
5. Citation check
        ↓
📊 API (FastAPI) + UI (Streamlit)
        ↓
🔄 Observability (LangSmith/Phoenix)
```

## 11.4 Tech Stack

| Layer | Tool |
|---|---|
| Database | Postgres + pgvector |
| Embedding | Cohere multilingual-v3 |
| LLM | Claude Sonnet 4.5 |
| Orchestration | LangGraph |
| Eval | RAGAS |
| API | FastAPI |
| UI | Streamlit |
| Container | Docker Compose |
| Observability | LangSmith or Langfuse |

## 11.5 Project Structure

```
lumora-kb/
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── README.md
│
├── src/
│   ├── ingestion/
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   ├── loader.py
│   │   └── pipeline.py
│   │
│   ├── retrieval/
│   │   ├── vector.py
│   │   ├── bm25.py
│   │   ├── hybrid.py
│   │   └── rerank.py
│   │
│   ├── rag/
│   │   ├── state.py
│   │   ├── nodes/
│   │   │   ├── rewriter.py
│   │   │   ├── grader.py
│   │   │   ├── generator.py
│   │   │   └── citer.py
│   │   └── workflow.py
│   │
│   ├── api/
│   │   ├── main.py
│   │   ├── routes.py
│   │   └── schemas.py
│   │
│   ├── eval/
│   │   ├── ragas_eval.py
│   │   ├── golden_set.py
│   │   └── load_test.py
│   │
│   └── utils/
│       ├── db.py
│       ├── llm.py
│       └── logger.py
│
├── data/
│   ├── raw/
│   └── eval/
│       └── thai_qa_v1.csv
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
    └── terraform/
```

## 11.6 docker-compose.yml

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

## 11.7 SQL Schema

```sql
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
    embedding VECTOR(1024),  -- Cohere v3 dim
    chunk_index INT NOT NULL,
    token_count INT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chunks_embedding 
  ON chunks USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

CREATE INDEX idx_chunks_content_fts 
  ON chunks USING gin(to_tsvector('simple', content));

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
    user_feedback SMALLINT,
    created_at TIMESTAMP DEFAULT NOW()
);

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

## 11.8 6-Week Plan

### Week 1: Foundation
- Docker Compose with Postgres + pgvector
- Python project setup (uv)
- Test Claude API + Cohere
- Load 10 sample Thai docs

### Week 2: Ingestion
- Semantic chunker
- Batch embedder
- Storage (pgvector + metadata)
- Test with 100 docs

### Week 3: Retrieval
- Vector search
- BM25
- Hybrid (RRF)
- Cohere rerank
- Eval recall@5

### Week 4: RAG Workflow (LangGraph)
- Query rewriter
- Relevance grader
- Answer generator
- Citation checker
- E2E test

### Week 5: API + UI
- FastAPI
- Streamlit
- Logging
- Docker compose
- README

### Week 6: Eval + Polish
- Build 50 Q&A eval set
- Run RAGAS
- Iterate
- Deploy (Modal)
- Monitoring

## 11.9 Sample Code: LangGraph Workflow

```python
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

class RAGState(TypedDict):
    question: str
    rewritten_query: str
    chunks: list
    answer: str
    citations: list

def rewrite_query(state):
    """Use LLM to clarify ambiguous queries"""
    # ... call Claude to rewrite
    return {"rewritten_query": rewritten}

def hybrid_retrieve(state):
    """Vector + BM25 + rerank"""
    # ... retrieve chunks
    return {"chunks": chunks}

def grade_chunks(state):
    """LLM judges chunk relevance"""
    # ... if relevant: proceed, else: re-retrieve
    return {"chunks": filtered}

def generate_answer(state):
    """Generate answer from chunks"""
    # ... Claude with Thai prompt
    return {"answer": answer, "citations": citations}

def check_citations(state):
    """Verify each citation supports claim"""
    # ... LLM-as-judge for citation
    return {"answer": verified, "citations": verified_cites}

def decide_to_generate(state):
    return "sufficient" if len(state["chunks"]) >= 3 else "insufficient"

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

## 11.10 Cost Breakdown

| Item | Monthly |
|---|---|
| Supabase | $25 |
| Cohere embedding (10K queries) | $5 |
| Claude API (1K queries/day) | $30 |
| Modal hosting | $10 |
| **Total** | **~$70** |

---

# 12. Skills Roadmap

## 12.1 Phase 1: Foundation (Month 1-2)

### Goals:
- pgvector hands-on
- LangChain/LangGraph basics
- Build first RAG project
- MLflow basics

### Concrete tasks:
- [ ] Set up local Docker stack
- [ ] Embed 1000 Thai docs in pgvector
- [ ] Build basic RAG with LangChain
- [ ] Add LangGraph state management
- [ ] Track experiments with MLflow
- [ ] Run first RAGAS eval

### Deliverable:
Lumora KB v1 with working RAG

## 12.2 Phase 2: Production Patterns (Month 3-4)

### Goals:
- Advanced eval (RAGAS deep)
- Prompt management
- Feature store basics
- Modern orchestration

### Concrete tasks:
- [ ] Build 100-question eval set
- [ ] Implement RAGAS in CI/CD
- [ ] Set up LangSmith/Langfuse
- [ ] Migrate prompts to versioned storage
- [ ] Build Feast feature store on Postgres
- [ ] Add Prefect orchestration

### Deliverable:
Lumora KB v2 production-ready

## 12.3 Phase 3: Advanced (Month 5-6)

### Goals:
- Agent design (LangGraph multi-step)
- Multimodal RAG
- AI governance basics

### Concrete tasks:
- [ ] Build multi-step agent (research → write → review)
- [ ] Add image understanding (Claude vision)
- [ ] Implement Guardrails
- [ ] Add model routing (cheap → expensive)
- [ ] Set up semantic caching
- [ ] Document model cards

### Deliverable:
Lumora Agent v1 (multi-modal, guarded)

## 12.4 Phase 4: Specialist (Month 7+)

### Goals:
- Cost optimization
- Multi-tenant systems
- Advanced eval (A/B)
- Production AI Ops

### Concrete tasks:
- [ ] Implement comprehensive caching strategy
- [ ] Multi-tenant data isolation
- [ ] Build A/B testing framework
- [ ] Set up full observability dashboard
- [ ] Cost optimization audit
- [ ] Performance benchmarking

### Deliverable:
Production-grade AI platform

## 12.5 Portfolio Project Order

1. **Lumora KB** — Thai RAG (Month 1-2) ⭐ START
2. **NL→SQL Agent** — BigQuery natural language (Month 2-3)
3. **Document AI** — Thai PDF processing (Month 3-4)
4. **Multi-agent workflow** — research + writer + reviewer (Month 4-5)
5. **Production multi-tenant** — full prod system (Month 5-6)

Each project should:
- Have public GitHub repo
- README with architecture
- Documented decisions
- Eval results
- Cost analysis

---

# 13. Sin-Specific Context

## 13.1 Sin's Current State

**Background:**
- DE at The1 / Central Group Thailand
- Stack: Apache Beam/Dataflow, BigQuery, Bigtable, Pub/Sub, Cloud Composer
- Cross-cloud: AWS → GCP migration
- Multi-year GCP experience
- Building "dataflow_common" framework

**Strengths:**
- Strong DE foundation
- Architectural thinking
- Python expertise
- SQL proficiency
- Cloud infrastructure (GCP heavy)
- Streaming + batch experience

**Gaps to close:**
- Vector databases (pgvector)
- Embedding models (Cohere, OpenAI)
- LangChain/LangGraph
- RAG patterns
- Eval frameworks (RAGAS)
- LLMOps (LangSmith, prompt mgmt)
- Modern web stack (Node.js/FastAPI/Hono — for serving)

## 13.2 Sin's Target State (6-12 months)

**Role:** DE + AI Hybrid (Senior level)
**Capabilities:**
- Design and build RAG systems
- Architect multi-agent workflows
- Implement LLMOps practices
- Build evaluation frameworks
- Multi-modal AI applications
- Cost-optimized AI systems

**Validation:**
- Lumora KB portfolio piece
- Successful job applications (senior DE+AI roles)
- Confident interview discussions on AI topics

## 13.3 The1 AI Use Cases (Day-Job Practice)

Sin can practice AI skills via The1 work:

### Use Case 1: NL→SQL on BigQuery
- User: business analysts
- Need: ask questions in Thai/English
- Skills: RAG (schema retrieval), agent (SQL gen), eval

### Use Case 2: Customer 360 AI Agent
- User: marketing team
- Need: holistic view of any customer
- Skills: multi-source RAG, summarization

### Use Case 3: Campaign Recommendation
- User: marketing automation
- Need: ML-driven personalized campaigns
- Skills: features + models + LLM personalization

### Use Case 4: Internal Data Assistant
- User: all employees
- Need: Slack bot for data questions
- Skills: RAG over docs + lineage queries

### Use Case 5: Voice of Customer
- User: product team
- Need: extract insights from reviews
- Skills: classification, summarization, sentiment

### Use Case 6: AI-Powered Data Quality
- User: data team
- Need: anomaly detection + RCA
- Skills: agent over logs + lineage

## 13.4 Lumora Project Tie-In

Lumora project provides AI skills practice naturally:

- **Data Service** → DE + data ingestion + vector store
- **AI Agent** → LangGraph workflows
- **Content production** → multimodal LLM
- **Marketing service** → API + scheduling
- **Performance tracking** → observability + evals

= Lumora is Sin's hands-on AI portfolio AND business

## 13.5 Career Path Strategy

```
Year 1 (Now): DE at The1 + Build skills
  ├── Day job: Push for AI use cases at The1
  ├── Personal: Build Lumora KB (Phase 1)
  ├── Cert: GCP Professional DE (in progress)
  └── Network: AI engineering community

Year 2: DE + AI hybrid role
  ├── Internal promotion OR
  ├── External senior DE+AI role
  ├── Salary increase 30-50%
  └── Lumora Phase 1 → 2 transition

Year 3+: Specialist or Founder
  ├── Founder track: Lumora full-time
  ├── OR: Staff Engineer / Architect role
  └── Income: 300K-700K THB+/month
```

---

# 14. Common Pitfalls

## 14.1 RAG Pitfalls

❌ **Bad chunking** — too big = unfocused, too small = lose context
✅ **Solution:** Test multiple sizes (200, 500, 800), measure recall

❌ **Wrong embedding for language** — English model on Thai = bad
✅ **Solution:** Use multilingual (Cohere v3, BGE-M3)

❌ **Vector search only** — misses exact keywords
✅ **Solution:** Hybrid (vector + BM25 + rerank)

❌ **No eval** — can't improve what you don't measure
✅ **Solution:** Build eval set early (50+ Q&A), automate

❌ **Over-engineering** — too many features, complex graphs
✅ **Solution:** Start simple, iterate based on eval

❌ **Ignoring citations** — hallucinations slip through
✅ **Solution:** Citation verification in workflow

## 14.2 Agent Pitfalls

❌ **Too many tools** — agent confused, low quality
✅ **Solution:** 5-10 tools max, very clear descriptions

❌ **Vague tool docs** — agent picks wrong tool
✅ **Solution:** Clear input/output schemas, examples

❌ **No observability** — can't debug failures
✅ **Solution:** LangSmith/Phoenix from day 1

❌ **Infinite loops** — agent retries forever
✅ **Solution:** Max iteration limits, escape conditions

❌ **No human-in-the-loop** — autonomous = risky
✅ **Solution:** Approval gates for high-stakes actions

## 14.3 Production Pitfalls

❌ **No cost monitoring** — bill explodes
✅ **Solution:** Daily cost alerts, query budgets

❌ **No caching** — paying for same answers
✅ **Solution:** Semantic + exact match cache

❌ **No prompt versioning** — can't roll back bad changes
✅ **Solution:** Git or LangSmith versioning

❌ **No drift monitoring** — quality silently degrades
✅ **Solution:** Continuous eval on production samples

❌ **No safety guardrails** — prompt injection succeeds
✅ **Solution:** Input/output filtering

## 14.4 Career Pitfalls

❌ **Tutorial hell** — learning forever, building nothing
✅ **Solution:** One project end-to-end > 10 tutorials

❌ **Tool obsession** — switching frameworks weekly
✅ **Solution:** Pick LangGraph + pgvector, ship

❌ **No portfolio** — can't prove skills
✅ **Solution:** Public GitHub repos with READMEs

❌ **Solo learning** — slow, missing context
✅ **Solution:** Join Discord/community, attend meetups

---

# 15. Resources

## 15.1 Documentation

### Core:
- LangChain: https://python.langchain.com
- LangGraph: https://langchain-ai.github.io/langgraph/
- RAGAS: https://docs.ragas.io
- pgvector: https://github.com/pgvector/pgvector
- Cohere: https://docs.cohere.com
- Anthropic API: https://docs.anthropic.com

### Frameworks:
- LlamaIndex: https://docs.llamaindex.ai
- CrewAI: https://docs.crewai.com
- Pydantic AI: https://ai.pydantic.dev

### Eval/Observability:
- LangSmith: https://docs.smith.langchain.com
- Langfuse: https://langfuse.com/docs
- Phoenix: https://docs.arize.com/phoenix
- Helicone: https://docs.helicone.ai

### Vector DBs:
- Qdrant: https://qdrant.tech/documentation
- Pinecone: https://docs.pinecone.io
- Weaviate: https://weaviate.io/developers

## 15.2 Courses

### Free:
- DeepLearning.AI short courses (RAG, agents, eval)
- Anthropic's "Building Effective Agents"
- Hugging Face NLP course
- Full Stack Deep Learning
- Made with ML

### Paid:
- Maven LLM courses (Hamel Husain, Eugene Yan)
- Coursera ML/DL specialization
- DataCamp tracks

## 15.3 Blogs / Newsletters

### Must-follow:
- Eugene Yan (applied LLM): eugeneyan.com
- Hamel Husain: hamel.dev
- Chip Huyen: huyenchip.com
- Lilian Weng (OpenAI): lilianweng.github.io
- Simon Willison: simonwillison.net
- Sebastian Raschka: sebastianraschka.com
- Latent Space (Swyx): latent.space

### Newsletters:
- The Batch (Andrew Ng)
- TLDR AI
- AI Engineer's Pack
- The Sequence
- Last Week in AI

## 15.4 Communities

- LangChain Discord
- LlamaIndex Discord
- AI Engineer Slack
- /r/LocalLLaMA (Reddit)
- /r/MachineLearning
- /r/dataengineering
- Thai DE community (Facebook)
- AI Engineer Foundation
- HackerNews

## 15.5 Conferences

### AI/ML:
- AI Engineer Summit (Swyx)
- MLOps World
- NeurIPS / ICLR / ICML
- The Data + AI Summit (Databricks)

### Data Engineering:
- Data Council
- Reinforce
- Subsurface (Dremio)
- Coalesce (dbt)

## 15.6 Books

### Foundational:
- "Designing Data-Intensive Applications" — Kleppmann
- "Fundamentals of Data Engineering" — Reis & Housley
- "The Data Warehouse Toolkit" — Kimball

### ML/AI:
- "Hands-On Machine Learning" — Géron
- "Designing Machine Learning Systems" — Chip Huyen
- "Building LLM-Powered Applications" — Valentina Alto

### Modern:
- "AI Engineering" — Chip Huyen (2025)
- "RAG-Driven Generative AI" — Denis Rothman

## 15.7 GitHub Repos to Study

- LangChain templates
- LlamaIndex examples
- Anthropic cookbook
- OpenAI cookbook
- Google Gemini cookbook
- pgvector examples
- LangGraph examples

## 15.8 Papers Worth Reading

### RAG:
- "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (original)
- "Lost in the Middle: How Language Models Use Long Contexts"
- "Self-RAG: Learning to Retrieve, Generate, and Critique"
- "Corrective Retrieval Augmented Generation"
- "HyDE: Precise Zero-Shot Dense Retrieval"

### Agents:
- "ReAct: Synergizing Reasoning and Acting in Language Models"
- "Tree of Thoughts"
- "Reflexion: Language Agents with Verbal Reinforcement Learning"
- Anthropic's "Building Effective Agents" essay

### Eval:
- "RAGAS: Automated Evaluation of RAG"
- "Holistic Evaluation of Language Models (HELM)"

---

# 🎯 Final Notes for Sin

## Priority Skills (in order)

1. **pgvector + Postgres** — fundamentals
2. **LangChain → LangGraph** — orchestration
3. **RAGAS** — evaluation
4. **FastAPI / Cloud Run** — serving
5. **LangSmith / Langfuse** — observability
6. **Cohere multilingual** — Thai embedding
7. **Claude API** — production LLM
8. **Modal / Cloudflare Workers** — deploy
9. **Prompt engineering** — quality
10. **Agent design** — advanced

## First Month Action Plan

**Week 1:** Set up Lumora KB local stack
**Week 2:** Ingest 100 Thai docs, basic RAG working
**Week 3:** Add hybrid retrieval + rerank
**Week 4:** LangGraph workflow + eval set

By end of Month 1: Working portfolio piece + understanding of full stack

## Career Conversion Strategy

```
Use Lumora KB as:
  - Portfolio piece (GitHub public)
  - Interview talking points
  - LinkedIn content (write about it)
  - Internal advocacy (show The1 team)
  
After 3 months:
  - Start applying to DE+AI roles
  - Speaking at meetups
  - Open source contributions
  
After 6 months:
  - Senior DE+AI role offers expected
  - 30-50% salary increase target
  - Choice: stay at The1 (with raise) or move
```

## Mindset

✅ **Build > Read** — code over tutorials
✅ **Ship > Perfect** — done > nothing
✅ **Eval-driven** — measure everything
✅ **Iterate** — v1 then v2 then v3
✅ **Public** — share work, build network

---

**Document version:** v1
**Token count:** ~30,000
**Last updated:** December 2026
**Maintained by:** Sin + Claude (Anthropic)

---

