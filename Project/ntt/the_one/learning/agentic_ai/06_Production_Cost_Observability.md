# 06 — Production, Cost, Observability

> Ship agent ขึ้น production จริง — ลด cost, มี monitoring, จับ failure ได้
> ใช้ของฟรี/open-source เกือบทั้งหมด

---

## 1. Cost Model — เข้าใจก่อนถึงจะลดได้

### 1.1 ที่มาของ cost

```
Total cost = Σ (input tokens × $in + output tokens × $out)
                  ×  (calls per request)
                  ×  (requests per day)
```

ใน agent loop จะมี **compound** — 1 user request = 5-20 LLM calls

### 1.2 ตารางราคาคร่าวๆ (2026)

| Model | $/MTok in | $/MTok out | Ratio |
|---|---|---|---|
| **Claude Opus 4.7** | $15 | $75 | premium |
| **Claude Sonnet 4.6** | $3 | $15 | mid |
| **Claude Haiku 4.5** | $1 | $5 | cheap |
| **GPT-5** | $1.25 | $10 | mid |
| **GPT-5 mini** | $0.25 | $2 | cheap |
| **Gemini 2.5 Pro** | $1.25 | $10 | mid |
| **Gemini 2.5 Flash** | $0.30 | $2.50 | cheap |
| **Gemini 2.5 Flash-Lite** | $0.10 | $0.40 | very cheap |
| **DeepSeek V3** (API) | $0.27 | $1.10 | very cheap |
| **Llama 3.3 70B (Groq)** | $0.59 | $0.79 | cheap (fast!) |
| **Cerebras Llama 70B** | free tier | free tier | free (rate limited) |
| **Self-host (Ollama)** | $0 | $0 | electricity only |

### 1.3 ตัวอย่าง agent cost

**Research agent ใช้ Sonnet เต็ม ไม่ optimize**:
- 10 sub-tasks × (5K input + 1K output) tokens = 50K in + 10K out × Sonnet
- = $0.15 + $0.15 = **$0.30 per query**
- × 10K query/day = **$3,000/day** 😱

**Same agent + optimization (routing + cache)**:
- Sonnet (orchestrator only) + Haiku (sub-agents) + 70% cache hit
- = ~$0.03 per query
- × 10K = **$300/day** = ลด 90%

> ดู [deep_dive/04 Cost Optimization](deep_dive/04_Cost_Optimization_Tactics.md) สำหรับ tactic เต็ม

---

## 2. Optimization Tactics — Big 5

### 2.1 Model Routing — งานง่ายใช้ model ถูก

```
                    Input
                      │
                      ▼
              ┌──────────────────┐
              │  Classifier      │  (cheap LLM หรือ embedding)
              └────────┬─────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │ Simple  │   │ Medium  │   │ Complex │
   │ Haiku   │   │ Sonnet  │   │  Opus   │
   └─────────┘   └─────────┘   └─────────┘
```

**Implementation**:
```python
def route(query):
    complexity = embed_classifier(query)
    if complexity < 0.3:
        return haiku.invoke(query)
    elif complexity < 0.7:
        return sonnet.invoke(query)
    else:
        return opus.invoke(query)
```

หรือใช้ **OpenRouter** + auto-routing:
```python
# OpenRouter: 1 API key, 100+ models, auto-fallback
client.chat.completions.create(
    model="openrouter/auto",  # automatic model selection
    messages=[...]
)
```

### 2.2 Prompt Caching — Cache prompt prefix

Anthropic / Gemini / OpenAI ทุกตัวรองรับ prompt cache แล้ว

```python
# Anthropic — cache prefix prompt
client.messages.create(
    model="claude-sonnet-4-6",
    system=[
        {
            "type": "text",
            "text": LONG_SYSTEM_PROMPT,  # 5000 tokens
            "cache_control": {"type": "ephemeral"}  # cache 5 min
        }
    ],
    messages=[...]
)
# First call: pay full
# Next calls within 5 min: pay 10% for cached portion
```

ผลกระทบจริง:
- System prompt 5K tokens
- Without cache: $3/MTok × 5K = $0.015 per call
- With cache hit: $0.30/MTok × 5K = $0.0015 per call (ลด 90%)
- ถ้า call 100 ครั้ง/นาที → ประหยัด $1.35/min × 60 = **$80+/hour**

**ใส่ที่ไหน**: system prompt, tool definitions, RAG context ที่ใช้ซ้ำ

### 2.3 Context Compression — บีบ context

#### A. Summarize old turns
หลัง conversation 20+ turns → summarize เก่ากลายเป็น 1 paragraph

#### B. Drop irrelevant messages
ใช้ embedding similarity → keep messages relevant to current query

#### C. Tool result truncation
Tool ส่ง output 5000 tokens → keep top 500 tokens ที่ relevant

```python
def truncate_tool_result(result, query, max_tokens=500):
    chunks = chunk(result, 100)
    scored = [(c, similarity(c, query)) for c in chunks]
    top = sorted(scored, key=lambda x: -x[1])[:5]
    return "\n".join(c for c, _ in top)
```

### 2.4 Semantic Cache (Cache เชิงความหมาย)

```
User Q1: "Refund policy?"     → LLM call → answer A1, save (embed(Q1), A1)
User Q2: "How to refund?"     → embed → match Q1 → return A1 (no LLM call!)
```

Tools:
- **GPTCache** (OSS) — semantic cache wrapper
- **Helicone Cache**
- **Langfuse Prompt Cache**
- DIY: Redis + embedding similarity

Cache hit rate ที่ดี = 30-60% สำหรับ FAQ-style → ลด cost ตามนั้น

### 2.5 Batch API

OpenAI / Anthropic มี batch API — submit batch job → รับผล 24 ชม. → ลด 50%

**ใช้เมื่อ**: งาน async ที่ไม่ต้อง realtime (data labeling, doc processing, eval)

---

## 3. Free / Cheap Stack — งบ $0-50/เดือน

### 3.1 Free Tier ที่ดีจริง (2026)

| Provider | Free Limit | Note |
|---|---|---|
| **Gemini API** | 1500 RPD Gemini 2.5 Flash | ดีสุด สำหรับ generic |
| **Groq** | 30 RPM, 14400 RPD Llama 3.3 70B | เร็วมาก! 1000+ tok/s |
| **Cerebras** | rate limited | speed 2000+ tok/s |
| **Together.ai** | $1 free credit | ลอง ได้ |
| **Hyperbolic** | $1 free credit | DeepSeek, Llama |
| **OpenRouter** | varies | aggregator |
| **Hugging Face Inference** | rate limited | OSS models |
| **Cloudflare Workers AI** | 10K req/day free | edge inference |

### 3.2 Stack ฟรี 100%

```
LLM:        Gemini 2.5 Flash (cloud) + Ollama Llama 3.2 (local)
Embedding:  Ollama nomic-embed-text
Vector DB:  Qdrant (Docker)
Orchestr:   LangGraph (OSS)
Memory:     SQLite + Qdrant
Observab:   Langfuse (Docker)
Eval:       Promptfoo (CLI)
Browser:    Playwright (local)
Search:     DuckDuckGo (free, scrape)

Total monthly cost: $0 (electricity ~ $5)
```

### 3.3 Stack เล็กน้อย $20-50/เดือน

```
LLM:        Claude Haiku (90%) + Sonnet (10% for hard tasks)
Embedding:  Voyage-3 ($0.06/MTok) — สำหรับ thai
Vector DB:  Qdrant Cloud free tier (1GB free) หรือ self-host
Orchestr:   LangGraph
Search:     Tavily free tier 1000/mo
Observab:   Langfuse Cloud free tier
Hosting:    Railway/Fly.io ($5/mo)

Monthly cost: ~$30-50
```

---

## 4. Observability — ทำไมต้องมีและทำยังไง

### 4.1 ทำไม

Agent debug **ยากมาก**:
- Multi-step → ผิดที่ step ไหน?
- LLM non-deterministic → reproduce ยาก
- Tool failure → silent
- Cost spike → ใครเรียก loop infinite?

**Without observability** = ไม่รู้ว่าระบบทำงานยังไง

### 4.2 สิ่งที่ต้อง track

```
Per request:
  - Total latency
  - Total cost
  - All LLM calls (input, output, model, tokens, latency)
  - All tool calls (name, args, result, latency, error)
  - Final outcome (success/fail/incomplete)

Aggregated:
  - p50 / p95 / p99 latency
  - Cost per user, per day
  - Error rate by step
  - Tool usage frequency
  - Most expensive queries
```

### 4.3 Tools

#### Langfuse (แนะนำ — OSS + cloud free tier)

```bash
# Self-host
git clone https://github.com/langfuse/langfuse
cd langfuse
docker compose up -d
```

```python
from langfuse.openai import openai
# or
from langfuse.anthropic import anthropic

# All calls auto-traced
response = openai.chat.completions.create(...)
```

หรือ explicit:
```python
from langfuse import Langfuse
lf = Langfuse()

trace = lf.trace(name="research-agent", user_id="alice")
gen = trace.generation(name="planner",
                       model="claude-sonnet-4-6",
                       input=messages,
                       output=response,
                       usage={"prompt_tokens": 100, "completion_tokens": 50})
```

UI: see traces, costs, latency, errors per session

#### LangSmith (LangChain ecosystem)
- Tightly integrated กับ LangChain/LangGraph
- Cloud-only, มี free tier
- Excellent UI
- ราคา: $39+/mo for production

#### Helicone (OSS)
- Proxy-based — ไม่ต้องแก้ code
- Cost tracking + caching
- Free tier 10K req/mo

#### Phoenix (Arize)
- OSS observability
- เน้น eval + drift

#### OpenTelemetry + Tempo/Jaeger
- ถ้า team มี tracing infra อยู่แล้ว
- Generic — ไม่ LLM-specific แต่ flexible

### 4.4 Recommendation

- **เริ่ม**: Langfuse self-host (Docker) — ฟรี ครบ
- **Production**: ถ้าใช้ LangGraph → LangSmith / ถ้าทั่วไป → Langfuse Cloud

---

## 5. Eval — ประเมินว่า Agent ทำงานดีจริง

### 5.1 ทำไม Eval สำคัญ

LLM update → behavior เปลี่ยน → ระบบที่เคยใช้ได้พังเงียบๆ
ต้องมี eval suite ที่รันก่อน deploy ทุกครั้ง

### 5.2 ประเภท Eval

#### A. Reference-based
มี ground truth → เทียบ
- BLEU, ROUGE (text similarity) — เก่าแล้ว
- Exact match (classification, extraction)
- Custom rule-based

#### B. LLM-as-a-Judge
ใช้ LLM ตัวอื่น judge output

```python
def llm_judge(query, output, criteria):
    judgement = strong_llm(f"""
    Query: {query}
    Output: {output}
    Criteria: {criteria}
    Score 1-5 และอธิบาย
    """)
    return parse(judgement)
```

⚠️ Bias: judge อาจชอบ style ตัวเอง — ใช้ judge ที่ต่าง model จาก generator

#### C. Human eval
Gold standard — แต่แพง / ช้า
ใช้สำหรับ: ground truth สร้าง dataset, regression check

#### D. Trajectory eval (สำหรับ agent)
ไม่ใช่แค่ output สุดท้าย — eval ทั้ง trajectory:
- Agent ใช้ tool ถูกต้องมั้ย?
- Step count สมเหตุสมผลมั้ย?
- Cost reasonable มั้ย?

### 5.3 Tools

| Tool | Note |
|---|---|
| **Promptfoo** (OSS) | YAML config, CI-friendly |
| **DeepEval** (OSS) | Python, pytest-style |
| **Ragas** (OSS) | RAG-specific metrics |
| **TruLens** (OSS) | LLM eval + observability |
| **Langfuse Datasets + Evals** | end-to-end |
| **Inspect** (UK AI Safety) | research-grade |

### 5.4 ตัวอย่าง Promptfoo

```yaml
# promptfooconfig.yaml
prompts:
  - "Answer concisely: {{question}}"

providers:
  - openai:gpt-5-mini
  - anthropic:claude-haiku-4-5
  - ollama:llama3.3

tests:
  - vars:
      question: "Capital of Thailand"
    assert:
      - type: contains
        value: Bangkok
      - type: cost
        threshold: 0.001
      - type: llm-rubric
        value: "Answer is accurate and concise"
```

```bash
promptfoo eval
promptfoo view  # web UI
```

---

## 6. Production Patterns

### 6.1 Idempotency

Agent อาจ retry → ห้ามซ้ำ side-effect

```python
@idempotent(key="invoice_{customer_id}_{order_id}")
def create_invoice(customer_id, order_id):
    ...
```

### 6.2 Circuit Breaker

ถ้า LLM provider ล่ม → fallback model
```python
try:
    return primary_llm(prompt)
except (RateLimitError, ServiceUnavailable):
    return fallback_llm(prompt)
```

### 6.3 Rate Limiting

ทุก agent ควรมี:
- Max LLM calls per request
- Max tool calls per request
- Max wall-clock time
- Max total cost (in $)

```python
class Budget:
    def __init__(self, max_cost_usd=1.0, max_steps=20):
        self.cost = 0
        self.steps = 0
        self.max_cost = max_cost_usd
        self.max_steps = max_steps
    
    def check(self):
        if self.cost > self.max_cost:
            raise BudgetExceeded(f"Spent ${self.cost}")
        if self.steps > self.max_steps:
            raise BudgetExceeded("Too many steps")
```

### 6.4 Human-in-the-Loop (HITL)

สำหรับ critical action — ต้องให้คน approve

```python
# LangGraph supports interrupts
graph.compile(
    checkpointer=...,
    interrupt_before=["execute_payment"]  # pause here
)
# UI shows pending action → human approves → resume
```

### 6.5 Graceful Degradation

ถ้า tool fail → fall back ไป tool อื่น / answer with warning

### 6.6 Async + Streaming

Agent loop ยาว → user ต้องเห็น progress

```python
async for event in agent.astream(input):
    if event.type == "tool_start":
        yield f"🔧 Using {event.tool_name}..."
    elif event.type == "thinking":
        yield event.text
```

---

## 7. Deployment Options

### 7.1 Options ตาม Cost

| Option | Cost/mo | Best for |
|---|---|---|
| **Railway** | $5+ | Simple Docker deploy |
| **Fly.io** | $5+ | Edge, persistent volumes |
| **Render** | $7+ | Web services, free tier มี |
| **GCP Cloud Run** | pay-per-use | Serverless, scale-to-zero |
| **AWS Lambda + API GW** | pay-per-use | If already on AWS |
| **Self-host VPS** | $5-20 | Hetzner / Contabo |
| **K8s** | $50+ | Multi-service, scale |

**For prototype**: Railway / Fly.io / Render
**For production lite**: Cloud Run / VPS
**For scale**: K8s

### 7.2 Architecture Pattern (production)

```
┌────────────────────────────────────────────────┐
│   API Gateway / Load Balancer                  │
└────────┬───────────────────────────────────────┘
         │
         ▼
┌────────────────┐    ┌────────────────┐
│  Agent Service │ ◀▶ │  Job Queue     │ (long tasks → async)
│  (FastAPI)     │    │  (Redis/SQS)   │
└──┬─────────────┘    └────────────────┘
   │
   ├─▶ LLM (Anthropic/OpenAI/local)
   ├─▶ Vector DB (Qdrant)
   ├─▶ Memory DB (Postgres)
   ├─▶ Tools (MCP servers)
   └─▶ Observability (Langfuse)
```

### 7.3 Docker Compose minimal stack

```yaml
# docker-compose.yml
services:
  agent:
    build: .
    env_file: .env
    ports: ["8000:8000"]
    depends_on: [qdrant, langfuse, redis]
  
  qdrant:
    image: qdrant/qdrant
    ports: ["6333:6333"]
    volumes: ["./qdrant_data:/qdrant/storage"]
  
  redis:
    image: redis:7
    
  postgres:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: changeme
    volumes: ["./pg_data:/var/lib/postgresql/data"]
  
  langfuse:
    image: langfuse/langfuse:latest
    ports: ["3000:3000"]
    depends_on: [postgres]
    environment:
      DATABASE_URL: postgres://postgres:changeme@postgres:5432/langfuse
```

> ดู [deep_dive/02 Self-Hosted Stack](deep_dive/02_Self_Hosted_Stack.md) สำหรับ stack ครบ

---

## 8. Security in Production

### 8.1 LLM-specific risks

| Risk | Mitigation |
|---|---|
| **Prompt injection** | Sanitize input + tool output, system prompt firewall |
| **Data exfiltration** | Restrict tool access, audit log |
| **Cost bomb** | Budget limits, rate limit, alerts |
| **Tool misuse** | RBAC, sandbox, allowlist |
| **PII leakage** | Redact before LLM call |

### 8.2 LLM Firewall / Guardrails

Tools:
- **Lakera Guard** (paid)
- **Llama Guard** (Meta, OSS)
- **NeMo Guardrails** (NVIDIA, OSS)
- **Guardrails AI** (OSS)

### 8.3 PII Handling

```python
import presidio_analyzer  # OSS

def redact_pii(text):
    results = analyzer.analyze(text=text, language="en")
    for r in results:
        text = text.replace(text[r.start:r.end], f"[{r.entity_type}]")
    return text

# ก่อนส่ง LLM
safe_input = redact_pii(user_input)
```

---

## 9. Checklist ก่อน Ship

- [ ] Observability ติดแล้ว (Langfuse / LangSmith)
- [ ] Eval suite รันผ่าน (Promptfoo / DeepEval)
- [ ] Budget limit (cost + steps) ทุก request
- [ ] Rate limit per user
- [ ] Idempotency keys for side-effect tools
- [ ] Fallback model ตั้งแล้ว
- [ ] HITL สำหรับ critical action
- [ ] PII redaction
- [ ] Audit log ของ tool call
- [ ] Backup memory/DB
- [ ] Alert on cost spike / error rate spike
- [ ] Document runbook (เมื่อ X เกิดทำ Y)

---

## 10. Real-world Numbers จาก Anthropic Research Agent

จาก paper/blog "How we built our multi-agent research system":
- Sonnet orchestrator + Haiku sub-agents
- Average 4-7 sub-agents per query
- p50 latency: 30-60 seconds
- p50 cost: $0.05-0.20 per query
- 90% queries solved on first try
- Token reduction 90% via summarization before merge

ใช้เป็น benchmark — ถ้าระบบคุณแย่กว่านี้มาก → revisit architecture

---

## สรุป

- Cost: model routing + cache + compress = ลด 70-90%
- Free stack จริงๆ ทำได้: Gemini Flash + Ollama + Qdrant + Langfuse
- **Observability ตั้งแต่ day 1** — ไม่งั้น debug ไม่ได้
- Eval suite ป้องกัน regression
- Budget cap, fallback, HITL, audit ทุก production agent
- Docker Compose stack รัน $5-20/mo ได้

**ต่อไป** → [07 Case Study: E-commerce Builder](07_Case_Study_Ecommerce_Builder.md) — เอาทุกอย่างมาประกอบเป็น use case ของคุณจริง

---

## References

- [Langfuse](https://langfuse.com/) — observability
- [Promptfoo](https://www.promptfoo.dev/) — eval
- [Anthropic prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [OpenRouter](https://openrouter.ai/) — model aggregator
- Anthropic, "How we built our multi-agent research system" (2025)
