# AI Engineer — Comprehensive Knowledge

> Deep reference for the ai-engineer subagent.
> Production GenAI / LLM / Agent implementation.

---

## 1. Foundations

### What an AI Engineer does

Builds + operates **GenAI applications** in production: chatbots, RAG systems, agents, content generation, document AI. The 2023+ specialization that grew out of ML engineering as LLMs became dominant.

### AI Engineer vs ML Engineer

| | ML Engineer | AI Engineer |
|---|---|---|
| Focus | Train + serve custom models | Build apps using foundation models |
| Data | Tabular, training sets | Documents, prompts, eval sets |
| Stack | scikit-learn, XGBoost, PyTorch | LangChain, LlamaIndex, vLLM, vector DBs |
| Output | Predictions, scores | Generated content, actions |
| Eval | accuracy, AUC | faithfulness, helpfulness, safety |

In practice the roles overlap. Org structure varies.

### The core building blocks

1. **Foundation models** — Claude, GPT, Gemini (API or self-hosted)
2. **Prompts** — engineered, versioned, evaluated
3. **Retrieval** — vector + keyword search over your data
4. **Tools** — functions LLMs can call
5. **Memory** — what persists across turns/sessions
6. **Guardrails** — safety, schema, policy
7. **Observability** — tracing, eval, monitoring

---

## 2. Mental Models / Decision Frameworks

### The default architecture (start here)

```
User → API gateway → Input guardrails → RAG (hybrid) → LLM → Output guardrails → Response
                                                ↓
                                          Trace + log
```

For 80% of GenAI apps, this is enough. Don't over-engineer until you have evidence.

### Pattern fit decision

```
Need creative generation?         → LLM with light prompt
Need factual answers from docs?   → RAG
Need consistent output style?     → fine-tune small model
Need multi-step + tool use?       → Agent
Need to act on the world?         → Agent with restricted tools + HITL
```

### Latency tiers

| Tier | Budget | Pattern |
|---|---|---|
| Interactive (<2s TTFT) | Streaming, cached, small model | Streaming response, model routing |
| Sync (2-10s) | RAG, single LLM call | Mainstream pattern |
| Async (10s+) | Multi-step agents, batch | Background job, status polling |

### Model selection

For a new project:
- Anthropic Claude — best reasoning, agentic, long context
- OpenAI GPT — best general, broad ecosystem
- Google Gemini — best multimodal, longest context
- Open models (Llama, Qwen) — self-host for privacy/cost

Don't over-commit early. Build abstractions to swap.

### RAG quality lever

Roughly, the cost of improving RAG quality:

```
EASY:
  - Better chunking (semantic, not naive)
  - Hybrid retrieval (vector + BM25)
  - Reranker (Cohere, BGE)
  - Better embedding model (voyage, Cohere, bge)

MEDIUM:
  - Query rewriting
  - HyDE (hypothetical answer embedding)
  - Multi-query expansion
  - Contextual retrieval (Anthropic-style chunk context)

HARD:
  - GraphRAG (knowledge graph)
  - Routing across multiple retrievers
  - Domain-specific reranker
  - Fine-tuning the retriever
```

Start at EASY. Most projects never need HARD.

### Cost levers

1. Smart routing (cheap model for cheap queries)
2. Prompt caching (Anthropic / OpenAI 50-90% off cached)
3. Limit max_tokens
4. Compress system prompt
5. Embed once, query forever (don't re-embed)
6. Self-host above ~10M tokens/day

---

## 3. Standard Practices

### Production RAG pipeline

#### Ingestion (offline)
```
Documents
  ↓
[Parsing — Unstructured, LlamaParse, Docling]
  ↓
[Chunking — semantic preferred, with overlap]
  ↓
[Embedding — voyage, Cohere, bge]
  ↓
[Index — vector DB + BM25 + metadata]
```

Best practices:
- Preserve metadata (source, page, date)
- Include chunk context (heading hierarchy)
- Chunk size 200-500 tokens with 10-20% overlap
- Skip boilerplate (footers, headers)
- Test on real queries before scaling

#### Retrieval (online)
```
Query
  ↓
[Optional query rewriting]
  ↓
[Hybrid retrieval — vector + BM25, parallel]
  ↓
[Rerank top-50 → top-5]
  ↓
[Context assembly — order matters; relevant first]
  ↓
[Prompt template]
  ↓
[LLM call — with streaming]
```

### Agent pattern (when needed)

```
Goal
  ↓
[Plan — LLM decomposes]
  ↓
[Loop with iteration limit]
  ├─ Reason → Choose tool
  ├─ Execute tool
  ├─ Observe → Update memory
  └─ Check done
  ↓
[Verify / critic]
  ↓
[Output]
```

Cap iterations. Add HITL for irreversible actions. Trace every step.

### Prompt management

- Prompts in source control (Git), not hardcoded
- Versioning + metadata
- A/B testing framework
- Tools: LangSmith, Langfuse, PromptLayer, Helicone

### Evaluation framework

Three levels:

**Offline eval** (golden set):
- 50-500 hand-curated test cases
- Run on every prompt/model change
- Metrics: faithfulness, relevance, correctness (RAGAS)

**Online eval** (production):
- Sample 1-10% of production traffic
- LLM-as-judge for quality
- User feedback (thumbs up/down)
- Drift detection

**Adversarial / red team**:
- Critical safety
- Quarterly + when policy changes

### Guardrails

Input:
- Prompt injection classifier (ProtectAI, Lakera)
- PII / sensitive data detection (Presidio, Lakera)
- Topic / policy classifier

Output:
- Toxicity (HuggingFace Detoxify)
- Hallucination check (vs retrieved context)
- Schema validation (Pydantic, Outlines)
- Sensitive data leakage

Tools: NeMo Guardrails, Llama Guard, Lakera Guard, custom.

### Streaming + UX

- Stream tokens as they generate (TTFT < 1s preferred)
- Show retrieval results inline ("Searching X documents...")
- Stop button + abort plumbing
- Loading states for long-running agent steps

### Observability

Every request:
- Trace ID
- Input + retrieved context + prompt + output
- Token counts (input + output)
- Latency breakdown (retrieval, LLM, post-processing)
- Cost
- User feedback (when available)
- Eval scores (sampled)

Tools: Langfuse (OSS), LangSmith, Helicone, Arize Phoenix, Datadog LLM Observability.

### Prompt injection mitigation

**What.** Prompt injection = untrusted text overrides your instructions. **Direct** (user types "ignore previous instructions") is the easy case; **indirect** is the real threat — malicious instructions hidden in a retrieved doc, a web page, an email, or a tool result that the model treats as authoritative. No single fix; you layer defenses and assume each one leaks.

**Why in prod.** Any agent with tools + untrusted input is exploitable: exfiltrate data via a crafted URL, trigger unauthorized tool calls, poison RAG answers. Anthropic's own red-team numbers (Sonnet 4.5) show the gradient — ~96% tool-use attacks blocked, ~92% MCP, but only ~78% for computer use. Treat model-level robustness as necessary but never sufficient.

**Patterns + when.**

- **Input guardrails** — classifier before the model. Llama PromptGuard 2 (DeBERTa-based, 86M / 22M, catches direct jailbreaks + injected inputs from user *and* tool outputs); Lakera Guard, ProtectAI. Cheap, run on every request.
- **Spotlighting / delimiting** — wrap untrusted content in explicit delimiters or encode it (datamarking) so the model knows "this is data, not instructions." Microsoft's spotlighting; simplest high-leverage win.
- **Dual-LLM pattern** (Simon Willison) — a privileged LLM never sees raw untrusted text; a quarantined LLM processes it and returns only structured, validated values. Strong against indirect injection.
- **Tool-call allowlists + structured outputs** — constrain which tools fire, validate args against a schema, require approval for irreversible/exfil-capable calls (anything that sends data outbound).
- **Defense for indirect injection via RAG/tool results** — scan retrieved chunks and tool outputs through the same classifier as user input; strip/escape instructions; provenance-tag context; least-privilege tool scopes so a poisoned doc can't reach a dangerous tool.
- **Output guardrails** — block data exfil patterns (suspicious URLs, encoded payloads) before they leave.

**Anti-patterns.** Relying on a system-prompt "do not obey injected instructions" line (trivially bypassed); trusting tool/RAG output as if it were your own instructions; giving an agent broad tool scopes "to be safe"; no human gate on outbound/destructive actions.

**Tools (2025-2026).** Meta **LlamaFirewall** (PromptGuard 2 + Agent Alignment Checks + CodeShield, open source), Llama Guard 4 (in/out moderation), Lakera Guard, NeMo Guardrails, Anthropic's real-time injection classifiers (auto-confirm gate on computer use).

Refs: [LlamaFirewall (Meta AI)](https://ai.meta.com/research/publications/llamafirewall-an-open-source-guardrail-system-for-building-secure-ai-agents/), [PromptGuard 2 model card](https://www.llama.com/docs/model-cards-and-prompt-formats/prompt-guard/).

---

## 4. Tools Landscape (2026)

### LLM APIs
- **Anthropic (Claude Opus, Sonnet, Haiku)** — strong reasoning
- **OpenAI (GPT-5 family)** — flagship
- **Google (Gemini 2.5)** — long context, multimodal
- **Amazon Bedrock** — multi-model unified API
- **Vertex AI** — GCP unified
- **Azure OpenAI** — enterprise OpenAI

### Self-hosted inference
- **vLLM** — default for GPU
- **SGLang** — emerging competitor
- **Ollama** — dev / single-user
- **llama.cpp** — edge / CPU
- **TGI** — maintenance mode now

### Embeddings
- **OpenAI text-embedding-3-large/small**
- **Cohere embed v3 English / Multilingual**
- **Voyage AI** — strong open benchmarks
- **bge-large-en-v1.5** — best open
- **nomic-embed-text** — open

### Vector DBs
- **Pinecone** — managed, fast start
- **Qdrant** — Rust, efficient, OSS
- **Weaviate** — flexible, OSS
- **Milvus** — large scale
- **pgvector** — if you have Postgres
- **Chroma** — local + simple

### Reranking
- **Cohere Rerank** — commercial, very good
- **bge-reranker-large** — best open
- **Jina Reranker** — alternative

### Frameworks
- **LangChain + LangGraph** — most popular
- **LlamaIndex** — RAG-focused
- **Haystack** — production-oriented
- **DSPy** — programmatic prompts
- **smolagents** (HF) — minimal
- **Pydantic AI** — Pydantic-flavored

### Evaluation
- **RAGAS** — RAG metrics
- **DeepEval** — broader
- **TruLens** — tracing + eval
- **promptfoo** — CLI prompt eval

### Observability
- **Langfuse** — OSS, comprehensive
- **LangSmith** — LangChain commercial
- **Arize Phoenix** — OSS
- **Helicone** — gateway + observability
- **OpenTelemetry GenAI semantic conventions** — emerging standard

### Guardrails
- **NeMo Guardrails** — NVIDIA, programmable
- **Llama Guard** — Meta
- **Lakera Guard** — commercial
- **Presidio** — Microsoft, PII detection

### Document parsing
- **Unstructured** — broad support
- **LlamaParse** — strong on PDFs
- **Docling** (IBM) — open + fast
- **Azure Document Intelligence** — forms

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Naive RAG (chunk + cosine + LLM) | Underperforms | Hybrid + rerank + structured chunking |
| Hardcoded prompts in app code | No versioning, A/B test | Prompt management system |
| No eval | Silent regression | Eval suite + production sampling |
| One model for all | Overpay | Multi-model routing |
| Long context everything | Cost + latency, lost in middle | RAG + targeted long-context |
| Agent for every task | Compound failures, slow, costly | Sequential single-step where possible |
| Embed system prompt every request | Expensive | Prompt caching |
| Trust LLM output | Hallucination, schema breaks | Validate + retry with feedback |
| Ignore drift | Quality slides | Continuous eval |
| Naive memory (full history) | Costs explode | Summarize / trim / vector retrieve |
| No tracing | Black box | Trace every call |
| Skip guardrails | Liability + safety | Layered guardrails |

---

## 6. Advanced / Expert Topics

### Advanced RAG

- **Contextual retrieval** (Anthropic) — generate context summary per chunk, embed both
- **Hybrid search** — RRF (reciprocal rank fusion)
- **Multi-vector** — embed chunk multiple ways (summary, hypothetical questions)
- **Self-querying** — LLM generates structured filter from natural query
- **GraphRAG** — knowledge graph for entity-rich domains
- **CRAG** (Corrective RAG) — verify retrievals, regenerate if poor

### Multi-modal RAG

- Embeddings for images (CLIP, voyage-multimodal)
- VLM for understanding (Claude vision, Gemini, GPT-5)
- Combined retrieval across modalities
- Image → text caption for retrieval

### Long context strategies

Models with 1M-2M context (Gemini, Claude Opus 4.5+):
- Send full document instead of RAG
- Trade-off: cost + latency + "lost in the middle"
- Hybrid: RAG to narrow → long context for reasoning

### Speculative decoding + prompt caching

Server-side:
- Speculative decoding — small model proposes
- Prompt caching — system prompt + RAG context cached

Anthropic prompt caching: 90% off cached portion. Massive cost saving for chatbots.

### Agent reliability patterns

- Plan → Execute → Verify
- Self-critique loops
- Tool result validation
- Memory checkpointing
- Maximum iteration limits
- Human approval gates for critical actions

### Multi-agent orchestration

| Pattern | When |
|---|---|
| Sequential | Linear handoff |
| Hierarchical | Manager + workers |
| Debate | Quality > speed |
| Specialist swarm | Diverse tools, parallel |

Frameworks: LangGraph (flexible), CrewAI (role-based), AutoGen (conversational).

### Fine-tuning techniques

| Method | When |
|---|---|
| **Full FT** | Rare, very specific |
| **LoRA / QLoRA** | Common, parameter-efficient |
| **DPO / ORPO** | Preference / alignment |
| **Prompt tuning** | Niche |
| **Distillation** | Big → small |

For most apps: API + RAG > fine-tune.

### Cost optimization deep

```
Per request:
  Input tokens × $in_rate + Output tokens × $out_rate

Levers:
  - Smart routing (Haiku for simple, Sonnet/Opus for complex)
  - Prompt caching (90% off cached)
  - Output limits (cap max_tokens)
  - Self-hosting (>10M tokens/day)
  - Distillation (fine-tune small from big)
  - Semantic cache (careful with correctness)
```

### Computer Use / Browser agents

Frontier capability:
- Anthropic Claude Computer Use
- OpenAI Operator
- browser-use, Playwright + LLM

Use cases:
- Form filling at scale
- QA testing
- Customer support escalation
- Data migration UI-only systems

Cost + reliability still emerging. Use carefully.

### Computer-use / browser agents (deep)

**What.** Agents that drive a real GUI/browser via screenshots + synthetic mouse/keyboard actions, for systems with no API. Three families: **Anthropic Computer Use** (the `computer_20250124` tool; desktop-level — terminal, files, any app; you supply the sandbox), **OpenAI Operator / CUA** (cloud-hosted virtual browser, web-only, safety-first), and **browser-use / Playwright + LLM** (open-source, DOM + accessibility tree, more deterministic than pure pixels).

**Why in prod.** Last-resort automation when no API exists: legacy/UI-only systems, form-filling at scale, end-to-end QA, data migration. Today it's still a frontier capability — useful for narrow, supervised flows, not unattended fleets.

**Patterns + when.**

- **Sandbox always** — Docker container + virtual display (Anthropic ships a reference impl) or an ephemeral cloud VM. Never point a computer-use agent at a host with real credentials or network access you can't revoke.
- **Guardrails** — injection classifiers on every screenshot (a malicious web page is indirect injection); allowlist domains/actions; human confirmation gate on irreversible or sensitive steps (Anthropic auto-steers to user-confirm when a screenshot looks like injection).
- **Reliability** — cap steps, add per-step verification/retries, checkpoint state, screenshot-diff to detect "stuck." Multi-step success is the weak point; both Operator and Computer Use still drop or misread steps, and Sonnet 4.5 only blocked ~78% of computer-use injection attacks vs ~96% for plain tool use.
- **When to use** — prefer API > MCP > browser-automation (Playwright) > pixel-level computer use, in that order. Reach for computer use only when nothing higher-level exists, and keep a human in the loop.

**Anti-patterns.** Unattended computer-use agents with live credentials; no sandbox; trusting on-screen text as instructions; using pixel control where an API or DOM selector would be far cheaper and more reliable.

**Tools (2025-2026).** Anthropic Computer Use (Claude Sonnet 4.5/4.6), OpenAI Operator/CUA, browser-use, Playwright, Browserbase (hosted browser infra), E2B (sandboxes).

Refs: [Anthropic computer use tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool), [Claude Sonnet 4.5 system card](https://www.anthropic.com/claude-sonnet-4-5-system-card).

### Model Context Protocol (MCP)

**What.** An open JSON-RPC standard (Anthropic, late 2024) that lets any LLM host discover and call external **tools** (actions), **resources** (read-only data), and **prompts** (reusable templates) over a stateful session — the "USB-C for AI tools," replacing N bespoke integrations with one protocol. Now the de facto standard, adopted across OpenAI, Google, and the major IDEs/agent frameworks.

**Architecture.**
- **Host** (Claude Desktop, IDE, your agent) runs one or more **clients**, each connected to a **server**.

- **Transports**: **stdio** for local servers (subprocess, lowest latency, default for dev) and **Streamable HTTP** (replaced the old HTTP+SSE) for remote/multi-client production servers, with OAuth 2.1.
- **Primitives**: tools (JSON-schema'd, can mutate), resources (safe reads), prompts. Current spec rev **2025-06-18** added structured tool output, **elicitation** (server asks the user for more info mid-call), resource links in results, OAuth Resource-Server classification, and RFC 8707 resource indicators.

**Why it matters.** Write a tool once, every MCP-aware host can use it. Decouples capability authors from app authors; turns "integrations" into a marketplace.

**Building / consuming.** Build with the official Python or TypeScript SDK (FastMCP-style: decorate functions as `@tool`/`@resource`); test with MCP Inspector; ship as stdio for local or Streamable HTTP for remote. Consuming = register the server in your host config; the model sees tool schemas automatically.

**Security.** Treat third-party MCP servers as untrusted code with network + data access. Risks: tool-description injection ("rug pull" — server changes a tool's behavior after approval), token theft (hence RFC 8707 audience-binding), over-broad scopes, confused-deputy. Pin/review servers, scope OAuth tightly, run injection classifiers on tool output, prefer least privilege.

**Tools (2025-2026).** modelcontextprotocol Python/TS SDKs, FastMCP, MCP Inspector, registries (Smithery, mcp.so), gateways for auth/observability.

Refs: [MCP spec 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/changelog), [MCP transports](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports).

### Semantic caching (correctness trade-offs)

**What.** Cache LLM responses keyed by **embedding similarity** of the query, not exact-string match: embed the incoming query, vector-search past queries, and if cosine similarity ≥ threshold, return the cached answer — skipping the LLM call. Big latency + cost win for FAQ-shaped traffic.

**Why in prod.** Repetitive query distributions (support, docs Q&A) get high hit rates; a hit costs an embedding lookup instead of a full generation. But unlike exact caching, semantic caching is **probabilistic** and can serve wrong answers — correctness is the whole game.

**Patterns + when.**

- **Threshold tuning** — the precision/recall dial. Typical 0.7-0.95; lower = more hits but more false hits, higher = safe but few hits. Tune per-domain against a labeled set, not by gut.
- **False-hit risk** — "How do I cancel?" vs "How do I *not* cancel?" embed close but need different answers; negations, entities, numbers, and time-sensitive queries are classic traps. A weak embedding model maps distinct queries together → confident wrong answers. Use a strong embedding model and a per-namespace threshold.
- **Staleness + invalidation** — cached answers go stale when source data changes. TTLs, version/namespace keys tied to your knowledge-base version, event-driven eviction on content updates. Never semantically cache personalized, auth-scoped, or fast-changing answers.
- **When to use** — high-volume, low-personalization, tolerant-of-approximation flows. Avoid for anything where a wrong-but-plausible answer is costly.

**Anti-patterns.** One global threshold across all query types; caching personalized/stateful responses; no staleness strategy; trusting hits without sampling for false-hit rate in eval.

**Tools (2025-2026).** **GPTCache** (Zilliz, OSS — pluggable embedders + Milvus/Faiss/Redis/Qdrant), **Redis LangCache / RedisVL SemanticCache** (managed embed+store+search in one API), LangChain `RedisSemanticCache`, Portkey/Helicone gateway-level semantic cache.

Refs: [Redis semantic caching guide](https://redis.io/blog/how-to-cache-semantic-search/), [GPTCache](https://github.com/zilliztech/GPTCache).

---

## 7. References

### Books
- **AI Engineering** — Chip Huyen (2024, GenAI focus)
- **Hands-On Large Language Models** — Alammar, Grootendorst
- **Building LLM Powered Applications** — Joseph

### Papers / posts
- **Compound AI Systems** — Berkeley, 2024
- **RAGAS paper** — Es et al.
- **Lost in the Middle** — Liu et al.
- **Contextual Retrieval** — Anthropic blog
- **Constitutional AI** — Anthropic

### Communities
- **AI Engineer Summit** — community + conference
- **Latent Space** (podcast + Substack)
- **HuggingFace community**

### Standards
- **MCP (Model Context Protocol)** — Anthropic standard
- **OpenTelemetry GenAI conventions**

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| AI Architect | Implementation of designed pattern |
| ML Engineer | Classical ML for ranking/scoring inside GenAI |
| Data Engineer | Knowledge base ingestion pipelines |
| Product | UX trade-offs (latency vs quality vs cost) |
| Governance | Safety, PII, model cards |
| Security | Prompt injection mitigation |

---

*GenAI engineering in 2026 = compound systems thinking + production engineering. The single-call era is over.*
