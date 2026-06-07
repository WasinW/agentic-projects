# AI Platform — GenAI / LLM / Agentic AI Overview

> ครอบคลุม Generative AI, Large Language Models, RAG, Agentic AI
> แยกจาก Traditional ML — ดู `../ML/` แทน
> Last update: 2026-05

---

## 0. AI Platform vs ML Platform — แยกให้ชัด

### ความแตกต่างหลัก

| Aspect | ML Platform (Traditional) | AI Platform (GenAI/LLM) |
|---|---|---|
| **Model type** | Custom-trained per use case | Foundation models (pre-trained) |
| **Build approach** | Train from scratch on your data | Use API + fine-tune + augment |
| **Output type** | Numbers (predictions, scores) | Generated content (text, image, code) |
| **Evaluation** | Accuracy, AUC, RMSE | Quality, faithfulness, helpfulness |
| **Data needed** | Labeled training data | Reference docs, prompts, examples |
| **Failure mode** | Wrong prediction | Hallucination, jailbreak, bias |
| **Cost driver** | GPU training time | API calls, token count |
| **Latency** | 10-100ms typical | 1-10 seconds typical |

### When to use which

```
Numerical prediction (fraud, churn, demand) → ML Platform
  └─ Tabular data, structured features

Content generation (chatbot, summarization, code) → AI Platform
  └─ Unstructured input, natural language output

Classification of text/image → Hybrid (use LLM for embedding + classical classifier)
```

---

## 1. AI Platform Capabilities Map (8 Groups)

### Group AI-1: Foundation Model Management

| # | Capability | What |
|---|---|---|
| AI-1 | **Model Catalog** | tracking available LLMs (GPT, Claude, Gemini, Llama) |
| AI-2 | **Model Routing** | choose right model per query (cost vs quality) |
| AI-3 | **Fine-tuning Platform** | LoRA, QLoRA, full fine-tune |
| AI-4 | **Model Hosting** | API gateway / local serving (vLLM, TGI) |
| AI-5 | **Model Switching** | A/B test, fallback, version pinning |

### Group AI-2: Prompt Engineering & Management

| # | Capability | What |
|---|---|---|
| AI-6 | **Prompt Templates** | parameterized prompts |
| AI-7 | **Prompt Versioning** | Git-tracked, with eval metrics |
| AI-8 | **Prompt Library** | shared prompts across teams |
| AI-9 | **Prompt Testing** | regression suite per prompt |
| AI-10 | **Prompt Optimization** | iterative improvement (DSPy, GEPA) |

### Group AI-3: RAG Infrastructure

| # | Capability | What |
|---|---|---|
| AI-11 | **Document Ingestion** | parse, chunk, embed |
| AI-12 | **Vector Database** | similarity search |
| AI-13 | **Hybrid Search** | vector + BM25 + metadata filters |
| AI-14 | **Reranking** | cross-encoder rerank top-K |
| AI-15 | **Context Compression** | fit in context window |
| AI-16 | **Multi-modal RAG** | text + image + table |

### Group AI-4: Agentic AI

| # | Capability | What |
|---|---|---|
| AI-17 | **Agent Orchestration** | multi-step workflows |
| AI-18 | **Tool Use Framework** | LLM calls functions/APIs |
| AI-19 | **Multi-Agent Coordination** | agents collaborate |
| AI-20 | **Memory Management** | short + long term memory |
| AI-21 | **Planning & Reasoning** | ReAct, Chain-of-thought |
| AI-22 | **Human-in-the-loop** | approval gates |

### Group AI-5: Evaluation & Quality

| # | Capability | What |
|---|---|---|
| AI-23 | **LLM-as-Judge** | LLM evaluates LLM output |
| AI-24 | **RAG Evaluation** | RAGAS metrics |
| AI-25 | **Regression Testing** | golden test set |
| AI-26 | **Adversarial Testing** | red teaming |
| AI-27 | **Human Evaluation** | annotator workflow |

### Group AI-6: Safety & Guardrails

| # | Capability | What |
|---|---|---|
| AI-28 | **Input Guardrails** | prompt injection, PII detection |
| AI-29 | **Output Guardrails** | toxicity, hallucination, policy |
| AI-30 | **Content Moderation** | unsafe content blocking |
| AI-31 | **Topic Restriction** | stay on-topic |
| AI-32 | **Jailbreak Detection** | adversarial prompts |

### Group AI-7: Observability & Monitoring

| # | Capability | What |
|---|---|---|
| AI-33 | **Trace Logging** | full request → response chain |
| AI-34 | **Token Usage Tracking** | per request, per user |
| AI-35 | **Latency Monitoring** | TTFT, TPS, total |
| AI-36 | **Quality Drift** | output quality over time |
| AI-37 | **Cost per Query** | $$ per inference |
| AI-38 | **User Feedback Loop** | thumbs up/down, RLHF data |

### Group AI-8: LLMOps Infrastructure

| # | Capability | What |
|---|---|---|
| AI-39 | **API Gateway** | auth, rate limit, routing |
| AI-40 | **Caching Layer** | semantic cache, prompt cache |
| AI-41 | **Fallback Chain** | model A → B → C if fail |
| AI-42 | **Streaming Response** | chunked output |
| AI-43 | **Batch Processing** | offline bulk inference |

---

## 2. Reference Architecture — End-to-End AI Platform

```
┌─────────────────────────────────────────────────────────────────┐
│                       USER INTERFACES                           │
│   Chat UI │ API Clients │ Internal Apps │ Voice / Mobile        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    API GATEWAY LAYER                            │
│  • Authentication  • Rate limiting  • Routing  • Caching        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                  ORCHESTRATION LAYER                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │     INPUT GUARDRAILS                                       │ │
│  │  PII detect • Prompt injection • Topic check               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                     │
│  ┌────────────────────────▼───────────────────────────────────┐ │
│  │     AGENT / WORKFLOW ENGINE                                │ │
│  │  LangGraph / LlamaIndex / Custom                           │ │
│  │  • Plan  • Tool selection  • Multi-step  • Memory          │ │
│  └────────────────────────┬───────────────────────────────────┘ │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                   │
│         ▼                 ▼                 ▼                   │
│  ┌──────────┐    ┌──────────────┐    ┌──────────┐              │
│  │   RAG    │    │   TOOLS /    │    │  MEMORY  │              │
│  │  ENGINE  │    │   FUNCTIONS  │    │  STORE   │              │
│  └──────────┘    └──────────────┘    └──────────┘              │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │     LLM ROUTER                                             │ │
│  │  Pick model by task (cost vs quality vs speed)             │ │
│  └────────────────────────┬───────────────────────────────────┘ │
│                           │                                     │
│  ┌────────────────────────▼───────────────────────────────────┐ │
│  │     OUTPUT GUARDRAILS                                      │ │
│  │  Toxicity • Hallucination • Schema • Policy                │ │
│  └────────────────────────┬───────────────────────────────────┘ │
└────────────────────────────┼────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                  FOUNDATION MODELS                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ OpenAI   │  │ Anthropic│  │ Google   │  │ Self-host│         │
│  │ GPT-x    │  │ Claude   │  │ Gemini   │  │ Llama/Qwen│        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              KNOWLEDGE & DATA LAYER                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Vector   │  │ Document │  │ Knowledge│  │ Structured│        │
│  │ DB       │  │ Store    │  │ Graph    │  │ Data (BQ) │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              OBSERVABILITY LAYER                                │
│  Traces (Langfuse) │ Metrics │ Quality eval │ Cost tracking     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. The 5 Patterns of GenAI Application

### Pattern 1: Pure Prompting (Zero-shot / Few-shot)
```
User query → System prompt + Query → LLM → Response
```
- **Use case**: simple chatbots, summarization, translation
- **No external data needed**
- **Cheapest, fastest to build**
- **Limitation**: stuck at training cutoff

### Pattern 2: RAG (Retrieval-Augmented Generation)
```
User query → Retrieve relevant docs → Inject as context → LLM → Response
```
- **Use case**: enterprise QA, support bot, documentation search
- **Mainstay of enterprise AI**
- **Solves**: factual grounding, current info, private data
- **Deep dive**: ดู `02_RAG_Architecture.md`

### Pattern 3: Fine-tuning
```
Base LLM + Domain data → Fine-tuned LLM → Deploy
```
- **Use case**: domain-specific style, niche knowledge, smaller models
- **2026 reality**: PEFT (LoRA, QLoRA) มาแทน full fine-tune ส่วนใหญ่
- **When**: RAG ไม่พอ + มี data > 1000 examples + need consistent style

### Pattern 4: Agentic AI
```
User query → Agent plans → Calls tools → Iterates → Response
```
- **Use case**: complex tasks needing multi-step reasoning + actions
- **Deep dive**: ดู `04_Agentic_AI_Patterns.md`

### Pattern 5: Hybrid / Compound Systems
```
Combination of all above
e.g., Agent uses RAG, then fine-tuned model for output formatting
```
- **2026 reality**: most production systems are compound, not pure

---

## 4. AI Platform Maturity Model

### Level 1 — Experimental
- Engineers call OpenAI API directly
- Prompts hard-coded in app
- No evaluation
- No monitoring

### Level 2 — Productionized
- Centralized prompt management
- Version control prompts
- Basic guardrails (PII, toxicity)
- Cost tracking per app

### Level 3 — Enterprise-Ready ← **target ปี 2026**
- Multi-model routing
- RAG infrastructure (vector DB, reranking)
- Comprehensive evaluation (RAGAS, custom)
- Observability (Langfuse, Datadog)
- Fine-tuning capability

### Level 4 — Agentic & Adaptive
- Agent orchestration
- Self-improving (continual evaluation + retraining)
- Multi-modal
- Production-grade safety + audit

### Level 5 — AI-Native Operations
- Agents handling autonomous workflows
- Continuous learning loops
- AI debugging AI

**Most enterprises ปี 2026 อยู่ Level 2-3, leaders เริ่ม Level 4**

---

## 5. Key Architectural Decisions

### Decision 1: Self-host vs API

| Factor | API (OpenAI/Anthropic) | Self-host (Llama/Qwen) |
|---|---|---|
| Speed to start | Days | Months |
| Quality | Best (GPT-5, Claude Opus 4.7) | Lower for general |
| Cost (low volume) | Cheaper | Expensive (GPU 24/7) |
| Cost (high volume) | Expensive | Cheaper |
| Data privacy | Trust vendor | Full control |
| Compliance | Limited control | Full control |
| Customization | Fine-tune limited | Any way |
| Latency | Network + queue | LAN + GPU |

**กฎ**: เริ่ม API → switch เมื่อ volume justify

### Decision 2: Single Model vs Router

```
Single Model:
  Simpler, predictable cost
  But: overpay for simple queries
       underperform on complex ones

Multi-Model Router:
  Cheap for simple (Haiku/GPT-4o-mini)
  Powerful for complex (Opus/GPT-5)
  Saves 50-70% cost typically
```

**ตัวอย่าง routing**:
```python
def route(query: str, user_tier: str) -> str:
    if classify_complexity(query) == "simple":
        return "claude-haiku-4-5"  # $0.80/1M tokens
    elif user_tier == "premium":
        return "claude-opus-4-7"    # $15/1M tokens
    else:
        return "claude-sonnet-4-6"  # $3/1M tokens
```

### Decision 3: RAG vs Fine-tune vs Both

```
Q1: Is information dynamic? (changes often)
  Yes → RAG (always fresh)
  No  → Q2

Q2: Is response style critical? (specific tone, format)
  Yes → Fine-tune
  No  → Q3

Q3: How much domain knowledge?
  Lots of facts → RAG
  Reasoning style → Fine-tune
  Both → Combined approach
```

### Decision 4: Vector DB Choice

(detailed comparison ในตาราง — see `02_RAG_Architecture.md`)

```
Self-host + small (<10M vectors): Qdrant or pgvector
Self-host + large: Milvus or Vespa
Managed + small-mid: Pinecone
Managed + GCP-native: Vertex Vector Search
Need hybrid + filters: Weaviate or Qdrant
```

---

## 6. Cost Models — เข้าใจการจ่าย

### Token-Based Pricing (API)

```
Input tokens × $price_in + Output tokens × $price_out
```

ตัวอย่างปี 2026:
| Model | Input $/1M | Output $/1M | Use case |
|---|---|---|---|
| GPT-5 nano | $0.05 | $0.40 | high volume, simple |
| Claude Haiku 4.5 | $0.80 | $4.00 | balanced |
| GPT-5 | $2.50 | $10.00 | quality general |
| Claude Sonnet 4.6 | $3.00 | $15.00 | reasoning |
| Claude Opus 4.7 | $15.00 | $75.00 | complex tasks |

### Cost per Conversation

```
Avg conv = 5 turns × (200 tokens in + 300 tokens out)
        = 1000 in + 1500 out per conv
        
With Sonnet: (1000 × $3 + 1500 × $15) / 1M
           = $0.003 + $0.0225
           = ~$0.025 per conversation
```

### Cost Optimization Levers

1. **Prompt caching** (50-90% savings on repeated context)
2. **Smart routing** (use cheap model for simple)
3. **Output limits** (cap max_tokens)
4. **Batch processing** (50% discount)
5. **Self-host for high volume** (>10M tokens/day)
6. **Embedding cache** (reuse embeddings)

---

## 7. Common AI Use Cases & Architecture

### Use Case 1: Internal Knowledge Base (RAG)

```
Confluence/SharePoint → Ingestion → Vector DB
User question → Retrieve → LLM → Answer with sources
```

**Stack**:
- LlamaIndex/LangChain
- Pinecone/Vertex Vector Search
- GPT-4o or Claude Sonnet
- Langfuse for tracing

### Use Case 2: Customer Support Bot

```
User message → Intent classifier → Branch:
  - FAQ: RAG over knowledge base
  - Action: Tool use (lookup order, refund)
  - Escalate: Human handoff
```

**Stack**:
- LangGraph for orchestration
- RAG for FAQ
- Tools for backend actions
- Guardrails for sensitive topics

### Use Case 3: Document Analysis (Banking)

```
Upload PDF → Parse + chunk → Embed
Query → Hybrid search → Rerank → LLM extract
Output: structured JSON with citations
```

**Stack**:
- Unstructured.io for parsing
- Cohere rerank
- Claude (longer context for documents)
- Schema validation on output

### Use Case 4: Code Assistant

```
Developer query → Repo retrieval → Code context → LLM → Suggestion
```

**Stack**:
- Code-specific embeddings (e.g., voyage-code)
- Code-trained LLM (Claude, GPT)
- Tree-sitter for code parsing

### Use Case 5: Multi-step Agent (Travel Planner)

```
User: "Plan trip to Tokyo for 5 days, $2000 budget"
  ↓
Agent plans:
  1. Search flights (tool)
  2. Search hotels (tool)
  3. Build itinerary
  4. Calculate budget
  5. Present options
```

**Stack**:
- LangGraph
- Tool definitions
- Memory for conversation context
- Cost tracking

---

## 8. Foundation Models Landscape (2026)

### Closed Source / API
| Model | Provider | Strength |
|---|---|---|
| Claude Opus 4.7 | Anthropic | Best reasoning, long context, coding |
| GPT-5 | OpenAI | General-purpose, multimodal |
| Gemini 2.5 Pro | Google | Long context (2M tokens), multimodal |
| Claude Sonnet 4.6 | Anthropic | Best price/performance |

### Open Source / Self-host
| Model | Strength |
|---|---|
| Llama 4 (Meta) | General-purpose, long context |
| Qwen 3 (Alibaba) | Strong reasoning, multilingual |
| DeepSeek V3 | Math/code, MoE efficient |
| Mistral Large 3 | EU-friendly, multilingual |

### Specialized
| Model | Use case |
|---|---|
| voyage-3 | Embeddings (best on benchmarks) |
| Cohere Rerank 3 | Reranking |
| Whisper v3 | Speech-to-text |
| Stable Diffusion 3 | Image generation |
| Suno V4 | Music |

---

## 9. AI Platform vs Existing Data Platform

### What stays the same
- **Storage**: Iceberg/Delta for documents to RAG
- **Streaming**: Kafka/PubSub for events
- **Governance**: PII detection still applies
- **Compute**: Spark/Beam for embedding pipelines

### What's new
- **Vector Database** (new component)
- **LLM API/Serving** (new component)
- **Prompt Management** (new artifact type)
- **Trace logging** (richer than ML logs)
- **Token-based cost** (different from compute)

### Integration pattern
```
Data Platform (Iceberg, BQ, Streaming)
        ↓
Embedding Pipeline (new — runs on existing compute)
        ↓
Vector DB (new layer)
        ↓
AI Platform (new layer)
        ↓
Application
```

**Insight**: AI Platform extends Data Platform — it doesn't replace it

---

## 10. Map กับ The-1 (ตัวอย่างของคุณ)

### Use cases ที่น่าจะเหมาะ
1. **Customer support bot** — RAG over FAQ + ticket history
2. **Member analytics summary** — auto-generate insights from data
3. **Campaign content generation** — personalized SMS/email
4. **Internal knowledge search** — search across docs

### ที่ The-1 ขาด (จากที่ research)
- ❌ Vector database (ไม่เห็นใน repo)
- ❌ Prompt management framework
- ❌ AI evaluation infrastructure
- ❌ Centralized LLM gateway

### Roadmap แนะนำ

**Phase 1 (3 months)**: AI Foundation
- Set up centralized LLM API gateway (cost tracking, routing)
- Pick vector DB (start with managed: Vertex Vector Search)
- Build first RAG use case (FAQ bot)

**Phase 2 (6 months)**: Production Hardening
- Add evaluation framework (RAGAS)
- Add observability (Langfuse)
- Add guardrails (NeMo Guardrails or custom)
- Cost optimization (caching, routing)

**Phase 3 (9-12 months)**: Agentic
- Multi-step agents
- Tool use for backend actions
- Customer-facing agent

---

## 11. Cheat Sheet

### Q: "AI Platform กับ ML Platform แตกต่างยังไง?"
> "ML Platform = train custom model on tabular data, predict numbers
> AI Platform = use foundation models, generate content, work with unstructured input
> Lifecycle ต่างกัน: ML focus on training pipeline, AI focus on prompt + retrieval + evaluation"

### Q: "ออกแบบ AI Platform ใหม่ เริ่มยังไง?"
> "8 capability groups: Foundation Model, Prompt Mgmt, RAG, Agentic, Evaluation, Safety, Observability, Infrastructure
> Maturity Level 2-3 คือเป้าหมายปี 2026
> Priority แรก: API Gateway + Prompt management + Vector DB + Tracing"

### Q: "ใช้ RAG หรือ Fine-tune?"
> "RAG: dynamic info, factual grounding, easy update
> Fine-tune: consistent style, niche reasoning, smaller faster model
> ส่วนใหญ่ enterprise ใช้ RAG ก่อน fine-tune ทีหลังเฉพาะที่จำเป็น"

---

## เอกสารต่อใน folder นี้

- [02_RAG_Architecture.md](02_RAG_Architecture.md) — chunking, retrieval, reranking deep
- [03_LLMOps_and_Evaluation.md](03_LLMOps_and_Evaluation.md) — prompt mgmt, eval, guardrails
- [04_Agentic_AI_Patterns.md](04_Agentic_AI_Patterns.md) — multi-agent, tool use, memory
