# AI Architect — Comprehensive Knowledge

> Deep reference for the ai-architect subagent.

---

## 1. Foundations

### What an AI Architect does

Designs **systems that use machine learning and/or LLMs in production**. Bridges data architecture, software engineering, and ML/AI research.

- Picks the right pattern: predictive ML vs GenAI vs hybrid
- Chooses foundation models or trains custom models
- Designs the data + feature + serving + monitoring stack
- Plans for safety, evaluation, cost, latency
- Maps the system to compliance (especially with emerging AI regulations)

### Not the same as

- **Data Architect** — owns the data layer; AI architect consumes it
- **ML Engineer** — implements; AI architect designs
- **Data Scientist** — researches model approaches; AI architect productionizes them
- **MLOps Engineer** — operates trained models; AI architect designs the lifecycle

### The 2026 reality

The AI architect role exploded with LLMs. Today's AI architect must be conversant in:
- Classical ML (XGBoost, scikit-learn, deep learning)
- Foundation models (Claude, GPT, Gemini, open models)
- RAG architecture (retrieval + generation)
- Agent patterns (tool use, multi-agent, computer use)
- Evaluation + safety + guardrails
- MLOps and LLMOps differences

---

## 2. Mental Models / Decision Frameworks

### The fundamental decision: ML vs GenAI vs Hybrid

| Pattern | When |
|---|---|
| **Classical ML** | Tabular data, structured prediction, fraud, ranking, forecasting |
| **GenAI (LLM)** | Unstructured input/output, language tasks, content generation, summarization |
| **Hybrid** | Use LLM for understanding + classical ML for ranking/scoring |
| **Use existing API** | Don't reinvent commodity tasks (translation, transcription) |

A common mistake: applying LLMs to problems where XGBoost works better + cheaper + faster.

### RAG vs Fine-tune vs Both (for LLMs)

| Approach | Best for |
|---|---|
| **RAG** | Dynamic knowledge, factual grounding, fast updates, citing sources |
| **Fine-tune** | Specific output format, smaller model with same quality, latency/cost-critical |
| **Both** | Combine domain-specific writing + dynamic retrieval |
| **Prompt only** | Quick experiments, simple tasks |

Default: start with RAG. Only fine-tune if RAG hits a clear ceiling on style or you need a smaller model in production.

### Compound AI Systems (Berkeley NLP group, 2024)

The frontier of GenAI is **systems**, not single LLM calls. A compound AI system has:
- Multiple LLM calls
- Retrieval components
- Tool use
- Routing logic
- Verification / guardrails
- Memory + state

Designing compound systems is the AI architect's main job today.

### The 3 latency tiers

| Tier | Budget | Pattern |
|---|---|---|
| **Interactive** (<1s) | Must be fast | Cached embeddings, small models, streaming |
| **Synchronous** (1-10s) | OK to think | Full RAG, mid-size LLM, single agent step |
| **Async** (10s-hours) | Long-running | Multi-step agents, batch inference, background jobs |

Many AI systems mix tiers. Be clear about which is which.

### Build vs Use API for foundation models

| | API (Anthropic, OpenAI, Google) | Self-hosted (Llama, Qwen, DeepSeek) |
|---|---|---|
| Quality (today's best) | ★★★★★ | ★★★★ |
| Cost (low volume) | Cheap | Expensive (infra) |
| Cost (high volume) | Expensive (per-token) | Cheap (amortized) |
| Latency | Network-bound | LAN-bound |
| Privacy | Vendor sees it | Stays in your cloud |
| Customization | Limited | Full |
| Ops burden | None | High |

Default 2026: API for production unless privacy or cost forces self-host.

### Multi-model routing

Most production GenAI systems route between models:
```
Easy query   → small / cheap model (Haiku, GPT-5-nano)
Hard query   → flagship model (Opus, GPT-5)
Specialized  → fine-tuned model
Fallback     → secondary provider for resilience
```

Saves 60-80% cost with minor quality impact.

### Cost levers

1. **Model selection** — biggest lever
2. **Caching** — prompt caching, response caching, semantic cache
3. **Prompt size** — concise system + RAG retrieval not data-dump
4. **Routing** — cheap for cheap queries
5. **Self-hosting** — for high volume, predictable load
6. **Distillation** — train small model from big model's outputs

### Evaluation must be designed-in

You can't bolt on evaluation later. Plan for:
- Golden set (10-1000 hand-curated examples)
- Automated metrics (RAGAS, custom)
- LLM-as-judge (cheaper than human, less reliable than human)
- Production sampling + human review
- A/B testing infrastructure
- Drift / regression detection

---

## 3. Standard Practices

### Reference architecture: Production RAG

```
User query
   ↓
[Input guardrails — injection, PII, off-topic]
   ↓
[Query rewriting / routing — small model]
   ↓
[Hybrid retrieval]
   ├─ Vector search (embeddings)
   ├─ Keyword search (BM25)
   └─ Metadata filter
   ↓
[Reranking — cross-encoder]
   ↓
[Context assembly + token budget]
   ↓
[LLM generation — main model]
   ↓
[Output guardrails — toxicity, hallucination, schema]
   ↓
[Trace + log]
   ↓
Response
```

Each box is a design decision. Get them right at design time; debugging later is expensive.

### Reference architecture: Compound AI Agent

```
User request
   ↓
[Planner LLM — decompose into steps]
   ↓
[Loop: while not done]
   ├─ [Reasoning step]
   ├─ [Tool selection]
   ├─ [Tool execution]
   └─ [Memory update]
   ↓
[Verifier / critic — quality check]
   ↓
[Output guardrails]
   ↓
Response
```

Cap iterations. Add human-in-the-loop for critical decisions. Trace every step.

### Reference architecture: Classical ML serving

```
Online features (low-latency store)
   ↓
[Request: feature lookup + transform]
   ↓
[Model inference — TFServing / Triton / Vertex / SageMaker]
   ↓
[Post-processing + business rules]
   ↓
Response
   ↓
[Log to feature store + monitoring]
```

### MLOps lifecycle (classical ML)

```
Data → Feature pipeline → Training pipeline → Registry → Serving → Monitoring → Retraining
```

Each transition is a contract. Tools: MLflow, Vertex AI Pipelines, SageMaker Pipelines, Airflow + custom.

### LLMOps lifecycle (GenAI)

```
Prompts (versioned) → Evaluation suite → Deployment → Monitoring → Iteration
```

Different from MLOps because the "model" is largely outsourced (foundation model). The IP is in: prompts, RAG content, eval set, guardrails, orchestration.

### Eval framework selection

| Type | When | Tools |
|---|---|---|
| Reference-based | Have ground truth | RAGAS, exact match, BLEU/ROUGE |
| Reference-free | Open-ended | LLM-as-judge, human eval |
| Behavioral | Critical safety | Adversarial test suite, red-teaming |

Production-grade GenAI needs all three.

### Guardrails layers

```
Input:
- Prompt injection detection
- PII / sensitive data detection
- Topic / policy classifier
- Rate limiting

Output:
- Toxicity classifier
- Hallucination check (vs retrieved context)
- Schema validation
- Sensitive data leak detection
```

Tools: NeMo Guardrails, Llama Guard, Anthropic safety filters, custom classifiers.

### Vector DB selection

| | Pinecone | Weaviate | Qdrant | Milvus | pgvector |
|---|---|---|---|---|---|
| Managed | ✓ | optional | optional | optional | (in Postgres) |
| OSS | ✗ | ✓ | ✓ | ✓ | ✓ |
| Hybrid search | ✓ | ✓ | ✓ | ✓ | partial |
| Scale (B+ vectors) | ✓ | ★★ | ★★ | ★★★ | limited |
| Default for greenfield | Quick start | Most flexible | Most efficient | Largest scale | If you have PG |

### Memory patterns for agents

- **Short-term** — within session, often just context window
- **Conversational** — summarize past turns into a running summary
- **Long-term** — vector store + retrieval at start of each session
- **Episodic** — store specific interactions for recall
- **Semantic** — extracted facts about the user / domain

Most production agents use short-term + summarized conversational. Long-term is expensive but unlocks personalization.

### Multi-agent patterns

| Pattern | When |
|---|---|
| **Sequential** (pipeline) | Linear steps, clear handoffs |
| **Hierarchical** (manager → workers) | Complex tasks, decomposition |
| **Debate / critic** | Quality matters more than speed |
| **Specialist swarm** | Diverse tools, parallel exploration |

Frameworks: LangGraph (most flexible), CrewAI (role-based), AutoGen (conversation-based).

---

## 4. Tools Landscape (2026)

### Foundation models (closed)
- **Claude (Anthropic)** — strong reasoning, agentic, long context
- **GPT-5 family (OpenAI)** — flagship for general
- **Gemini 2.5 (Google)** — multimodal, long context (2M)
- **Mistral Large 3** — French / EU option

### Foundation models (open)
- **Llama 4 / 5** — Meta
- **Qwen 3 / DeepSeek V3** — Chinese frontier
- **Mistral / Mixtral** — open weights with permissive license

### Inference serving (self-host)
- **vLLM** — default for GPU production
- **SGLang** — fast-emerging competitor
- **TGI** (Hugging Face) — maintenance mode now
- **Ollama** — dev / single-user
- **llama.cpp** — edge / CPU

### Embeddings
- **OpenAI text-embedding-3 family**
- **Cohere embed v3**
- **Voyage AI** — strong open benchmarks
- **bge-large** — best open
- **nomic-embed-text** — open

### Vector DB
- See table above

### RAG frameworks
- **LangChain / LangGraph** — most popular, broad
- **LlamaIndex** — RAG-focused
- **Haystack** — production-oriented
- **DSPy** — programmatic prompt engineering

### Evaluation
- **RAGAS** — RAG-specific metrics
- **DeepEval** — broader LLM eval
- **TruLens** — tracing + eval
- **Langfuse / Helicone / Arize Phoenix** — observability + eval

### MLOps (classical ML)
- **MLflow** — most adopted experiment tracking + registry
- **Vertex AI / SageMaker / Azure ML** — managed
- **Kubeflow** — K8s-native
- **Weights & Biases** — premium experiment tracking
- **Feast / Tecton** — feature stores

### Agents
- **LangGraph** — graph-based flexibility
- **CrewAI** — role-based teams
- **AutoGen** — conversational agents
- **Anthropic Claude SDK with tool use** — direct API
- **smolagents** (Hugging Face) — minimal

### Safety / Guardrails
- **NeMo Guardrails** — NVIDIA, programmable
- **Llama Guard** — Meta classifier
- **Lakera Guard** — commercial
- **Custom classifiers** for domain-specific policies

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| LLM for everything | Expensive, slow, sometimes worse than XGBoost | Pattern fit: ML for prediction, LLM for language |
| Fine-tune as default | Slow iteration, hard to update | RAG first; fine-tune only if needed |
| Hand-tuned prompts in production code | No versioning, can't A/B test | Prompt management system |
| No eval | Quality regression invisible | Eval suite from day one |
| One model for all queries | Overpay for simple queries | Multi-model routing |
| Prompt-and-pray for safety | Real-world failures + liability | Layered guardrails + monitoring |
| Naive RAG (chunk + cosine) | Underperforms hybrid + rerank | Hybrid retrieval + rerank + structured chunking |
| Agent for everything | Compound failures, slow, expensive | Use agents only when sequential single-step doesn't work |
| Ignoring cost | Bill shock | Cost monitoring per use case + budgets |
| Ignoring drift | Quality degrades silently | Continuous evaluation + monitoring |

---

## 6. Advanced / Expert Topics

### Long-context strategies

Modern models support 100K-2M tokens. Trade-offs:
- **Pros**: less RAG complexity, full document in context
- **Cons**: expensive per call, attention degrades on long context ("lost in the middle"), latency

When to use long context vs RAG:
- Document size predictable + small (<200K tokens) → long context
- Large corpus, dynamic → RAG
- Hybrid: RAG to narrow to relevant docs, then long context

### Speculative decoding + caching

Server-side techniques to speed LLM inference:
- **Speculative decoding** — small model proposes, big verifies
- **Prompt caching** — Anthropic, OpenAI offer 50-90% off cached prompts
- **KV cache reuse** — within session

### Fine-tuning techniques

| Method | When |
|---|---|
| **Full fine-tune** | Significant data, big team | rare for most |
| **LoRA / QLoRA** | Most common; parameter-efficient | default |
| **DoRA** | Newer, better than LoRA in some cases |
| **Prompt tuning** | Few-shot extreme | niche |
| **DPO / RLHF** | Alignment, preference | important but complex |
| **ORPO** | Combine SFT + preference in one step | emerging |

### RAG advanced patterns

- **Query expansion** — generate multiple queries from one
- **HyDE** (hypothetical document embeddings) — embed what answer would look like
- **Contextual retrieval** (Anthropic) — generate context summary per chunk
- **Multi-vector** — multiple embeddings per chunk (different facets)
- **GraphRAG** (Microsoft) — knowledge graph + LLM

### Agent reliability

Agents compound failures: 5 steps × 95% reliability = 77% overall.
- Verify state after each action
- Checkpoint progress
- Limit iterations
- Human-in-loop for critical actions
- Comprehensive tracing

### Multi-modal architecture

When you need text + image + audio + video:
- **Vision-Language Models (VLMs)** — Claude vision, GPT-5, Gemini handle multiple modalities
- **Specialized embeddings** for cross-modal search (CLIP)
- **Whisper / Gemini for speech** to text
- **Diffusion models** for image generation
- Storage + retrieval gets more complex

### AI safety + alignment (production concerns)

- **Adversarial inputs** — prompt injection, jailbreaks
- **Output filtering** — toxicity, PII, off-topic
- **Hallucination** — model confidently wrong (RAG helps; doesn't solve)
- **Bias** — model reflects training data biases
- **Privacy** — data leakage from model, prompts

### LLMOps cost optimization deep

- Smart routing saves 60-80%
- Prompt caching 50-90% on cached portion
- Output limits (`max_tokens`) — cap accidental long completions
- Streaming improves perceived latency
- Embedding cache: same text → reuse forever
- Self-host above ~10M tokens/day

### Compliance for AI systems

Emerging regulations (EU AI Act, US executive orders, sector-specific):
- **Model cards** — document training data, performance, limitations
- **Use case classification** — high-risk requires more controls
- **Audit logs** — full traceability
- **Right to explanation** — for high-impact decisions
- **Bias auditing**

---

## 7. References

### Books
- **Designing Machine Learning Systems** — Chip Huyen (MLOps focus)
- **Designing Data-Intensive Applications** — Kleppmann (underlying systems)
- **Hands-On Large Language Models** — Alammar, Grootendorst (recent)
- **AI Engineering** — Chip Huyen (2024, GenAI focus)

### Papers / posts (must-read)
- **Compound AI Systems** — Berkeley NLP, 2024
- **RAGAS paper** — Es et al.
- **Lost in the Middle** — Liu et al. (long context limitations)
- **Constitutional AI** — Anthropic
- **The Bitter Lesson** — Sutton (classic; still relevant)

### Standards / specs
- **OpenAI / Anthropic API docs** — patterns referenced industry-wide
- **MCP (Model Context Protocol)** — Anthropic standard for tool use
- **OpenTelemetry GenAI semantic conventions** — for tracing

### Communities
- **Latent Space Podcast / Substack** — frontier discussions
- **AI Engineer summit / community** — practical patterns
- **HuggingFace community** — open models, datasets
- **ICML / NeurIPS / ICLR papers** — research

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Data Architect | "What's the shape of training + inference data?" |
| Solution Architect | "How does AI fit in the larger system?" |
| Platform Architect | "What AI capabilities should the platform provide?" |
| ML Engineer | "Here's the design — what's the implementation plan?" |
| AI Engineer | "Hands-on production implementation" |
| Governance | "Model cards, bias audits, AI Act compliance" |
| Product | "What can/can't we promise users?" |

---

*AI architecture in 2026 = compound systems thinking. The single-LLM-call era is over for production systems.*
