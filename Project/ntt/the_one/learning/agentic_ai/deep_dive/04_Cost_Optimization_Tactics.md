# Deep Dive 04 — Cost Optimization Tactics

> ลด LLM cost 70-90% โดยไม่เสีย quality
> Tactic จริง + ตัวเลขจริง + code

---

## 1. The Cost Equation

```
Cost = Σ_calls (in_tokens × $in/MTok + out_tokens × $out/MTok)
              × calls_per_user_request
              × user_requests_per_day
```

ทุก lever ลดได้ → ลด cost

---

## 2. ตารางเก็บค่า — เริ่มจากรู้ว่าจ่ายอะไร

ก่อนปรับ — track ก่อน:

```python
class Cost:
    def __init__(self):
        self.calls = []
    
    def record(self, model, in_tok, out_tok):
        in_price, out_price = PRICES[model]
        cost = (in_tok * in_price + out_tok * out_price) / 1_000_000
        self.calls.append({
            "model": model,
            "in_tok": in_tok,
            "out_tok": out_tok,
            "cost_usd": cost,
            "ts": time.time(),
        })
    
    def summary(self):
        df = pd.DataFrame(self.calls)
        return df.groupby("model").agg({
            "in_tok": "sum",
            "out_tok": "sum",
            "cost_usd": ["sum", "mean", "max"]
        })
```

หรือใช้ Langfuse — ทำให้แล้ว

**Pareto observation**: 80% cost มักมาจาก 20% ของ workflow steps → focus ที่นั่น

---

## 3. Tactic 1: Model Routing — Save 60-80%

### หลักการ

ไม่ใช่ทุก step ต้อง Sonnet — งานง่ายใช้ Haiku, งานยากใช้ Sonnet

### Levels

```
Level 1: Hard-coded routing
   if step == "extract": haiku
   if step == "plan": sonnet
   if step == "synthesize": sonnet

Level 2: Classifier-based
   complexity = embed_classifier(input)
   model = haiku if complexity < 0.5 else sonnet

Level 3: Cascade (escalation)
   try haiku
   if confidence < threshold: retry with sonnet
```

### Cascade implementation

```python
async def cascade(prompt, schemas=None):
    # Try cheap first
    cheap = await haiku.invoke(prompt, tools=schemas)
    if has_high_confidence(cheap):
        return cheap
    
    # Escalate
    return await sonnet.invoke(prompt, tools=schemas)

def has_high_confidence(response):
    # Heuristics:
    # - response.stop_reason == "end_turn" (not max_tokens)
    # - no "I don't know" markers
    # - structured output passes validation
    return validate(response)
```

### ตัวอย่างจริง

```
Before: Sonnet สำหรับทุก step
  - 10 steps × 5K in × $3/MTok = $0.15
  - 10 steps × 1K out × $15/MTok = $0.15
  - Total: $0.30/request

After: Haiku 80% + Sonnet 20%
  - 8 Haiku × 5K in × $1/MTok = $0.04
  - 2 Sonnet × 5K in × $3/MTok = $0.03
  - Out: similar pattern → ~$0.05
  - Total: $0.12/request

Saving: 60%
```

### Provider routing

| Tier | Provider | Cost |
|---|---|---|
| Premium | Anthropic Sonnet/Opus | $3-75 |
| Mid-cheap | OpenAI mini, Gemini Flash | $0.10-1 |
| Cheap | DeepSeek, Llama 3.3 (Groq) | $0.30-1 |
| Free | Gemini Flash free tier, Cerebras free | $0 |
| Local | Ollama | $0 (electricity) |

**OpenRouter** ทำให้ test ทุก tier ผ่าน API เดียว

---

## 4. Tactic 2: Prompt Caching — Save 50-90% on Repeated Context

### Anthropic prompt cache

```python
# Cache write: full price + 25% surcharge
# Cache read: 10% of input price (90% off)

response = client.messages.create(
    model="claude-sonnet-4-6",
    system=[
        {
            "type": "text",
            "text": HUGE_SYSTEM_PROMPT_5K_TOKENS,
            "cache_control": {"type": "ephemeral"},  # 5 min TTL
        }
    ],
    messages=[
        {"role": "user", "content": current_query}
    ],
)
```

### TTL options
- `"ephemeral"` = 5 min (default, free)
- `"ephemeral", "ttl": "1h"` = 1 hour (extra cost)

### Where to cache

```
1. System prompt (always)
2. Tool definitions (often)
3. Long doc context for RAG (if same docs reused)
4. Few-shot examples (always)
5. Episodic memory summary (if pattern repeats)
```

### Cache breakpoints

ใส่ `cache_control` ที่จุด → ทุกอย่าง **ก่อน** จุดนั้น cached

```python
messages=[
    {"role": "user", "content": [
        {"type": "text", "text": LONG_CONTEXT, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": variable_query},  # not cached
    ]}
]
```

### ตัวอย่างจริง

```
Without cache:
  System: 5K tokens × $3/MTok = $0.015 per call
  × 100 calls/min = $1.50/min = $90/hour

With cache (5 min TTL):
  First call: full + 25% = $0.019
  Next ~99 calls within 5 min: $0.0015 each
  Total: $0.165 / 5 min = $1.98/hour

Saving: ~98%
```

### Gemini implicit cache
Gemini 2.5 มี implicit cache — automatic ถ้า prompt ซ้ำ
- Cost ~25% off
- ไม่ต้อง code อะไร

### OpenAI prompt cache
OpenAI มี automatic cache for prompts > 1024 tokens — 50% off cached portion

---

## 5. Tactic 3: Semantic Cache — Save on Similar Queries

### Concept

```
"Refund policy?" → embed → call LLM → save (vec_q1, answer_a1)
"How to refund?" → embed → similar to vec_q1 → return answer_a1 (no LLM!)
```

### Implementation (DIY)

```python
import redis
import json
import numpy as np

class SemanticCache:
    def __init__(self, threshold=0.92):
        self.r = redis.Redis()
        self.threshold = threshold
    
    def get(self, query: str):
        q_emb = embed(query)
        # iterate cached entries (or use vector DB for scale)
        for key in self.r.scan_iter("cache:*"):
            entry = json.loads(self.r.get(key))
            sim = cosine(q_emb, entry["emb"])
            if sim > self.threshold:
                return entry["answer"]
        return None
    
    def set(self, query: str, answer: str):
        q_emb = embed(query)
        key = f"cache:{hash(query)}"
        self.r.setex(key, 3600, json.dumps({
            "query": query,
            "emb": q_emb,
            "answer": answer,
        }))
        return key

# Usage
cache = SemanticCache()

def answer(query):
    cached = cache.get(query)
    if cached:
        return cached
    
    answer = llm(query)
    cache.set(query, answer)
    return answer
```

### ใช้ Qdrant แทน Redis (สำหรับ scale)

```python
def get(query):
    results = qdrant.search(
        collection_name="cache",
        query_vector=embed(query),
        limit=1,
        score_threshold=0.92,
    )
    return results[0].payload["answer"] if results else None
```

### Pre-built tools
- **GPTCache** — open source, multi-backend
- **Helicone Cache** — drop-in proxy
- **Langfuse Prompt Cache**

### Hit rate ที่ดี

- FAQ chatbot: 40-70% hit rate
- General assistant: 10-20%
- Personalized agent: 5%

ตั้ง threshold สูงมาก (0.95+) ตอนเริ่ม → ค่อยลด

⚠️ **Risk**: cache return wrong answer ถ้า threshold ต่ำ → eval ก่อน production

---

## 6. Tactic 4: Context Compression — Save on Long Convos

### Problem
Multi-turn conversation → ทุก call ส่ง history ทั้งหมด → token compound

### Solutions

#### A. Summarize old turns

```python
def maybe_summarize(messages, threshold=20):
    if len(messages) < threshold:
        return messages
    
    old, recent = messages[:-10], messages[-10:]
    summary = llm.invoke(f"""
    Summarize this conversation in 200 words, preserving key facts and decisions:
    {old}
    """)
    return [{"role": "system", "content": f"Earlier: {summary}"}] + recent
```

#### B. Sliding window
เก็บแค่ last N — บาง context ก็พอ

```python
messages = messages[-20:]  # last 20
```

#### C. Selective retention (relevance-based)

```python
def filter_relevant(messages, query):
    q_emb = embed(query)
    scored = [(m, cosine(embed(m.content), q_emb)) for m in messages]
    return sorted(scored, key=lambda x: -x[1])[:10]
```

#### D. Tool result truncation

```python
def truncate_tool_result(result, query, max_tokens=500):
    if count_tokens(result) <= max_tokens:
        return result
    
    chunks = split_by_paragraph(result)
    scored = sorted(chunks, key=lambda c: -relevance(c, query))
    
    out = []
    total = 0
    for c in scored:
        ct = count_tokens(c)
        if total + ct > max_tokens:
            break
        out.append(c)
        total += ct
    return "\n\n".join(out)
```

### LLMLingua (research-grade compression)

```python
# Microsoft LLMLingua — compress prompts 5-10x
from llmlingua import PromptCompressor
pc = PromptCompressor()
compressed = pc.compress_prompt(
    long_context, 
    target_token=2000,
)
```

### ผลกระทบจริง

```
Conversation ที่ 30 turns × 200 token avg = 6000 token context
  - Sonnet: 6000 × $3/MTok = $0.018 per call
  - 30 calls = $0.54

With summary at turn 10/20:
  Avg context: ~ 2000 tokens
  Cost: $0.18

Saving: 67%
```

---

## 7. Tactic 5: Batch API — Save 50% (Async OK)

### OpenAI Batch API
```python
batch = client.batches.create(
    input_file_id="file-...",
    endpoint="/v1/chat/completions",
    completion_window="24h",
)
# Wait up to 24h → 50% discount
```

### Anthropic Message Batches
```python
batch = client.messages.batches.create(
    requests=[
        {"custom_id": "req-1", "params": {...}},
        {"custom_id": "req-2", "params": {...}},
        ...
    ]
)
# 24h window, 50% off
```

### ใช้เมื่อไหร่
- Data labeling (label 100K rows)
- Document processing
- Eval suite
- Backtesting / what-if

### ห้ามใช้เมื่อ
- Realtime (chat, search)

---

## 8. Tactic 6: Truncate Output

### Problem
LLM ตอบยาวเกิน — out token แพงกว่า in 5-10x

### Solutions

#### A. Set max_tokens
```python
response = llm.invoke(prompt, max_tokens=200)  # cap
```

#### B. Prompt for brevity
```
"Answer in 1 sentence only."
"Output JSON, no explanation."
```

#### C. Structured output
```python
from pydantic import BaseModel

class Answer(BaseModel):
    label: Literal["positive", "negative", "neutral"]
    confidence: float

response = llm.invoke(prompt, response_model=Answer)
# 3 tokens output instead of 30
```

### ผลกระทบ

```
Sentiment classifier:
  Free-form: avg 80 tokens out × $15/MTok = $0.0012 per call
  Structured (JSON): 15 tokens × $15 = $0.000225

× 1M classifications:
  Free-form: $1200
  Structured: $225
  Saving: 81%
```

---

## 9. Tactic 7: Smaller Embeddings + Quantization

### Concept
Embed dim ต่ำกว่า + quantized → DB เล็กลง + search เร็วขึ้น (ลด infra cost)

### Matryoshka embeddings (Voyage, OpenAI v3)

```python
# OpenAI text-embedding-3-large dim 3072 → ตัดเหลือ 1024
emb = openai.embeddings.create(
    model="text-embedding-3-large",
    input=text,
    dimensions=1024,  # truncate
)
```

ลด dim 3x → DB 3x เล็กลง, search 2-3x เร็ว, quality ลดน้อย (~3%)

### Quantization

```python
# Qdrant supports binary, scalar, product quantization
client.update_collection(
    collection_name="docs",
    quantization_config=ScalarQuantization(
        scalar=ScalarQuantizationConfig(
            type=ScalarType.INT8,
            quantile=0.99,
            always_ram=True,
        )
    )
)
```

ลด memory 4x (float32 → int8), recall ลดเล็กน้อย

---

## 10. Tactic 8: Smaller / Local Models for Sub-tasks

### Routing tree

```
Coordinator (Sonnet)
   │
   ├─ Classify intent (Haiku)
   ├─ Extract entities (Haiku or Llama via Groq free)
   ├─ Embed (local nomic-embed)
   ├─ Format output (small Llama)
   └─ Translate to Thai (Gemini Flash)
```

ทุก non-reasoning step → cheap or free

### Specialization
Fine-tune small model สำหรับ specific task (extract, classify) → Llama 3B beats GPT-5 บนงานนั้น (และฟรี)

Tools:
- **Unsloth** — fast LoRA fine-tuning
- **Together fine-tuning**
- **Hugging Face AutoTrain**

---

## 11. Tactic 9: Eliminate LLM Calls

ที่ดีที่สุดคือ — ไม่ call LLM เลย

### Skip when:
- Input matches regex/rule
- Confidence-based routing
- Already-classified content

```python
def classify(text):
    # Try cheap rule first
    if any(kw in text.lower() for kw in URGENT_KEYWORDS):
        return "urgent"
    
    # Then embedding classifier
    emb = embed(text)
    label, conf = embedding_clf.predict(emb)
    if conf > 0.8:
        return label
    
    # Fall back to LLM
    return llm_classify(text)
```

### ตัวอย่าง: Email triage
- 60% emails → rule (regex match keywords)
- 30% → embedding classifier
- 10% → LLM
- vs 100% LLM = save 90% cost

---

## 12. Tactic 10: Concurrent / Parallel Reduction

### Problem
Some agents call LLM serially แต่ task อย่าง parallel ได้

### Solution
Run tools/agents in parallel → wall clock เร็ว = same cost แต่ user happy

```python
# Sequential: 10s × 3 = 30s
result_a = await agent_a()
result_b = await agent_b()
result_c = await agent_c()

# Parallel: 10s
result_a, result_b, result_c = await asyncio.gather(
    agent_a(), agent_b(), agent_c()
)
```

ไม่ลด cost โดยตรง แต่ลด **perceived cost** + อาจเปิดทางใช้ smaller model (เพราะมี budget time)

---

## 13. Tactic 11: Fine-Tuned Tiny Models (Replace LLM Calls)

### When worth it

Volume ที่ break-even:
- Fine-tune cost: $20-200 (one-time)
- Inference cost saving: depends on volume

ถ้า task เดิมใช้ LLM 1M ครั้ง × $0.001 = $1000
→ fine-tune Llama 3B + self-host = $200 + $50/mo
→ break-even หลังเดือนแรก

### What to fine-tune
- Classification (sentiment, intent, category)
- Entity extraction (NER)
- Summarization (specific style)
- Code completion (specific lang/framework)

### What NOT to fine-tune
- General reasoning (can't beat Sonnet)
- Open-ended chat
- Tool use (small models ยัง weak)

---

## 14. ตัวอย่างจริง — Reduce 90%

### Before: Naive Implementation

```
Customer support agent
- Sonnet for everything
- No cache
- Full conversation history
- Free-form output
- Tool result raw

Per request: ~$0.50
× 10K requests/day = $5000/day = $150K/mo 😱
```

### After: Optimized

```
1. Routing:
   - 60% FAQ → rule + embedding cache (no LLM): $0
   - 30% routine → Haiku + cache: $0.01
   - 10% complex → Sonnet + cache: $0.05

2. Prompt cache: system + tool defs (50% calls hit)
3. Semantic cache: 30% hit rate
4. Conversation summary at 15 turns
5. Tool result truncation
6. Structured output (max_tokens=500)

Per request avg:
   0.6 × $0 + 0.3 × $0.01 + 0.1 × $0.05 = $0.008

× 10K = $80/day = $2400/mo

Saving: 98%
```

---

## 15. Cost Budget Pattern

```python
class CostBudget:
    def __init__(self, max_usd=1.0):
        self.max = max_usd
        self.used = 0
        self.calls = []
    
    def charge(self, model, in_tok, out_tok):
        cost = compute_cost(model, in_tok, out_tok)
        self.used += cost
        self.calls.append(cost)
        if self.used > self.max:
            raise BudgetExceeded(f"Spent ${self.used:.4f} > ${self.max}")
    
    def remaining(self):
        return self.max - self.used

# Usage in agent
budget = CostBudget(max_usd=0.50)
agent.run(query, budget=budget)
```

ทุก agent ต้องมี budget — ไม่งั้น runaway loop = $$ bomb

---

## 16. Cost-Quality Tradeoff Matrix

ทุก optimization มี cost-quality tradeoff:

| Optimization | Cost saving | Quality risk | Easy to revert? |
|---|---|---|---|
| Prompt cache | 50-90% | None | Yes |
| Cheaper model | 60-80% | Medium | Yes |
| Semantic cache | 30-70% | Medium-high | Yes |
| Conversation summary | 50-80% | Low-medium | Yes |
| Output truncation | 20-50% | Low | Yes |
| Fine-tune | 70-95% | Medium | No (model trained) |
| Eliminate LLM call | 100% (per call) | Low if rule-based | Yes |

**Recommend order**:
1. Prompt cache (easy, no quality risk)
2. Eliminate where possible (rules)
3. Routing (easy, monitorable)
4. Semantic cache (with eval)
5. Compression
6. Output truncation
7. Fine-tune (last resort, big payoff)

---

## 17. Monitoring & Alerts

```python
# Daily cost spike alert
if daily_cost > 1.5 * weekly_avg:
    alert("Cost spike detected: ${} vs avg ${}")

# Per-user cost cap
if user_cost(user_id, last_24h) > USER_DAILY_CAP:
    block_user(user_id)

# Model drift in cost
if avg_tokens_per_call > baseline * 1.3:
    alert("Token bloat — check prompts/tools")
```

Tools:
- Langfuse: built-in cost tracking + alerts
- Helicone: cost dashboard
- Custom: Postgres + Grafana

---

## 18. Checklist

ก่อน optimize:
- [ ] Track cost per call (Langfuse / custom)
- [ ] Identify top 20% of cost contributors
- [ ] Set budget cap per user/request

Quick wins (do first):
- [ ] Prompt cache (system + tool defs)
- [ ] Routing (cheap → smart cascade)
- [ ] max_tokens cap
- [ ] Tool result truncation

Medium effort:
- [ ] Semantic cache (with eval suite)
- [ ] Conversation summary
- [ ] Structured output

Big payoff (advanced):
- [ ] Fine-tuned small model สำหรับ classification
- [ ] Local Ollama for embed + small LLM
- [ ] Eliminate LLM calls via rules

---

## 19. สรุป

- เริ่มที่ measure → identify hot spots
- Prompt cache + routing = 70-80% saving (low effort)
- Semantic cache = 30-70% (medium effort, eval needed)
- Compression + truncation = 30-50% incremental
- Fine-tune = 70-95% สำหรับ high-volume specific task
- Budget cap **ต้องมี** ทุก production agent

**End-to-end target**: $0.05-0.20 per complex agent request (vs $0.50-2 unoptimized)

---

## References

- [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [OpenAI Batch API](https://platform.openai.com/docs/guides/batch)
- [GPTCache](https://github.com/zilliztech/GPTCache)
- [LLMLingua](https://github.com/microsoft/LLMLingua)
- [Helicone caching](https://docs.helicone.ai/features/caching)
- [Voyage Matryoshka](https://blog.voyageai.com/) — dimension truncation
