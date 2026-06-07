# LLMOps & Evaluation — Deep Dive

> ทำให้ LLM application ใช้งานได้จริงระดับ production
> Prompt management, evaluation, guardrails, observability

---

## 1. ทำไม LLMOps ต่างจาก MLOps

### MLOps deals with...
- Model artifacts (`.pkl`, `.pt`)
- Training pipelines
- Numerical metrics (accuracy, AUC)
- Versioned models

### LLMOps deals with...
- **Prompts** (text strings) ← new artifact
- **System prompts** + few-shot examples
- **Embedding models + LLMs + retrievers** (compound system)
- **Subjective quality** (helpfulness, faithfulness)
- **Token-based cost** (not compute hours)
- **Hallucination, jailbreaks, bias** (new failure modes)
- **Prompts can change behavior dramatically** without code change

### LLMOps Stack Components

```
┌──────────────────────────────────────────────────┐
│           PROMPT MANAGEMENT                      │
│  Versioning • Templates • A/B testing            │
├──────────────────────────────────────────────────┤
│           EVALUATION FRAMEWORK                   │
│  Offline eval • Online eval • LLM-as-Judge       │
├──────────────────────────────────────────────────┤
│           GUARDRAILS                             │
│  Input validation • Output filtering • Policy    │
├──────────────────────────────────────────────────┤
│           OBSERVABILITY                          │
│  Tracing • Token tracking • Quality monitoring   │
├──────────────────────────────────────────────────┤
│           INFRASTRUCTURE                         │
│  API gateway • Caching • Routing • Fallback      │
└──────────────────────────────────────────────────┘
```

---

## 2. Prompt Management — The New Code

### Why Prompts Need Engineering Discipline

**Anti-pattern**:
```python
# In application code
response = llm(f"Summarize this: {document}")
# Hardcoded, unversioned, untested
```

**Production pattern**:
```python
# Centralized, versioned, evaluated
prompt = prompt_registry.get("summarizer", version="2.4.1")
response = llm(prompt.format(document=document))
```

### Prompt as Versioned Artifact

```yaml
# prompts/summarizer.yaml
name: summarizer
version: 2.4.1
owner: content_team
purpose: Summarize long documents into 3 bullets

system: |
  You are a precise summarizer. Output exactly 3 bullets.
  Each bullet starts with • and is one sentence.
  Be factual; no embellishment.

user_template: |
  Document:
  {document}
  
  Summary:

parameters:
  temperature: 0.3
  max_tokens: 300
  model: claude-sonnet-4-6

eval_criteria:
  - faithfulness: > 0.9
  - format_compliance: > 0.95
  - avg_length: 50-100 tokens

test_cases:
  - input: "test_doc_1.txt"
    expected_includes: ["key fact A", "key fact B"]
  - input: "test_doc_2.txt"
    expected_format: "exactly 3 bullets"
```

### Prompt Management Tools 2026

| Tool | Strength |
|---|---|
| **Langfuse Prompts** | Open source, integrated tracing |
| **PromptLayer** | Commercial, mature |
| **Helicone** | Lightweight, OSS |
| **Weights & Biases Prompts** | Integrated with experiment tracking |
| **Self-built (Git + YAML)** | Free, full control |

### Prompt Versioning Strategy

```
prompts/
├── summarizer/
│   ├── v1_0_0.yaml      # initial
│   ├── v1_1_0.yaml      # added length constraint
│   ├── v2_0_0.yaml      # changed system prompt structure (breaking)
│   └── v2_4_1.yaml      # current production
```

**Semantic versioning for prompts**:
- **Major** (v2.x): Breaking change in output format
- **Minor** (vX.4.x): New behavior, backward-compatible
- **Patch** (vX.X.1): Bug fix, typo, minor wording

### Prompt A/B Testing

```python
def get_prompt_variant(user_id: str, prompt_name: str) -> str:
    # Bucket users into variants
    variant = hash_to_variant(user_id, prompt_name)
    
    if variant == "control":
        return prompt_registry.get(prompt_name, version="2.3.0")
    elif variant == "treatment":
        return prompt_registry.get(prompt_name, version="2.4.0")
    
# Track outcomes per variant
log_prompt_usage(user_id, variant, outcome=user_thumbs_up)
```

---

## 3. LLM Evaluation Framework

### The Eval Pyramid

```
        ┌──────────────────┐
        │  Production      │  Online: real users
        │  monitoring      │  (continuous)
        ├──────────────────┤
        │  E2E eval        │  Manual: human review
        │  (humans)        │  (sampled, expensive)
        ├──────────────────┤
        │  Regression      │  Automated: golden set
        │  test suite      │  (every change)
        ├──────────────────┤
        │  Unit tests      │  Per component
        │  (per module)    │  (every commit)
        └──────────────────┘
```

### Evaluation Types

#### Type 1: Reference-Based (Have Ground Truth)
- Compare output to known correct answer
- Metrics: BLEU, ROUGE, exact match, semantic similarity
- **Use when**: closed-form questions, translations, summarization with reference

#### Type 2: Reference-Free (No Ground Truth)
- Score output on dimensions without comparing to ground truth
- Metrics: faithfulness, fluency, relevance (LLM-as-judge)
- **Use when**: open-ended generation, chatbot

#### Type 3: Pairwise Comparison
- Show 2 outputs, ask which better
- Get win rate
- **Use when**: comparing 2 prompt versions or 2 models

### Common LLM Metrics

| Metric | What | How |
|---|---|---|
| **Faithfulness** | Output grounded in context | LLM judge |
| **Answer Relevance** | Addresses the question | LLM judge |
| **Helpfulness** | Solves user's problem | Human or LLM judge |
| **Completeness** | All parts of question answered | LLM judge |
| **Format Compliance** | Output matches schema | Regex / parser |
| **Toxicity** | Harmful content | Classifier (Detoxify, Perspective) |
| **Bias** | Unfair across groups | Statistical tests |
| **Coherence** | Logically consistent | LLM judge |
| **Conciseness** | Not verbose | Token count + LLM judge |

---

## 4. LLM-as-Judge — Deep Dive

### Why LLM-as-Judge

- Human evaluation: ~$5-50 per sample, slow
- Classical metrics (BLEU): poor correlation with human
- LLM judge: $0.01-0.10 per sample, fast, **80% agreement with humans**

### LLM-as-Judge Patterns

#### Pattern A: Direct Scoring (1-5 scale)
```python
def judge_faithfulness(answer, context):
    prompt = f"""Rate the faithfulness of the answer (1-5):
1: Completely fabricated, not in context
2: Mostly fabricated, slight grounding
3: Mixed - some grounded, some fabricated
4: Mostly grounded, minor unsupported claims
5: Fully grounded in context

Context: {context}
Answer: {answer}

Score (just the number):"""
    
    return int(llm(prompt))
```

#### Pattern B: Pairwise Comparison
```python
def judge_pairwise(query, answer_a, answer_b):
    prompt = f"""Compare two answers to the query.

Query: {query}
Answer A: {answer_a}
Answer B: {answer_b}

Which is better? Output: A, B, or TIE.
Reasoning first, then verdict."""
    
    return parse(llm(prompt))
```

#### Pattern C: Multi-Criteria
```python
def judge_multi(answer, query, context):
    prompt = f"""Evaluate the answer on 3 dimensions:

1. Faithfulness (0-1): grounded in context?
2. Relevance (0-1): addresses the query?
3. Helpfulness (0-1): solves user's need?

Query: {query}
Context: {context}
Answer: {answer}

Output JSON: {{"faithfulness": x, "relevance": y, "helpfulness": z, "reasoning": "..."}}"""
    
    return json.loads(llm(prompt))
```

#### Pattern D: G-Eval (Best Practice)

Chain-of-thought + structured rubric:

```python
G_EVAL_PROMPT = """You will be given a {task} and a response.

Evaluation Criteria:
{criteria}

Evaluation Steps:
1. Read the input carefully.
2. Read the response carefully.
3. Compare against criteria.
4. Score 1-5 based on:
   1: Strongly fails criterion
   3: Partially meets
   5: Fully meets

Now evaluate:
Input: {input}
Response: {response}

Reasoning (think step-by-step):
[your reasoning]

Final Score (1-5):
[just the number]"""
```

**G-Eval** improves correlation with human judgment from 0.51 → 0.66 on summarization

### LLM Judge Pitfalls

| Pitfall | Mitigation |
|---|---|
| **Position bias** | Show options A/B and B/A, average |
| **Verbosity bias** | Penalize length explicitly |
| **Self-preference** | Use different model for judge than tested |
| **Calibration drift** | Anchor with known examples |
| **Cost** | Sample, don't judge every output |

---

## 5. Evaluation Frameworks Comparison

### RAGAS — Specialized for RAG

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness, 
    answer_relevancy,
    context_precision,
    context_recall
)

result = evaluate(
    dataset=test_data,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
)
```

**Pros**: focused on RAG, ready metrics
**Cons**: only RAG, prescriptive

### DeepEval — Comprehensive

```python
from deepeval import evaluate
from deepeval.metrics import (
    GEval, 
    HallucinationMetric,
    AnswerRelevancyMetric,
    ToxicityMetric
)

correctness = GEval(
    name="Correctness",
    criteria="Is the answer factually correct?",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
)

evaluate(test_cases, [correctness, HallucinationMetric()])
```

**Pros**: pytest integration, custom metrics, rich
**Cons**: more setup

### Promptfoo — CLI-First

```yaml
# promptfooconfig.yaml
prompts:
  - "Summarize: {{text}}"
  - file://prompts/summarizer_v2.txt

providers:
  - openai:gpt-4o
  - anthropic:claude-sonnet-4-6

tests:
  - vars:
      text: "Long document..."
    assert:
      - type: contains
        value: "key fact"
      - type: llm-rubric
        value: "Concise and accurate"
```

```bash
promptfoo eval
```

**Pros**: simple CLI, good for prompt comparison
**Cons**: less flexible than Python frameworks

### TruLens — Observability + Eval

```python
from trulens_eval import Tru, TruLlama
from trulens_eval.feedback import Feedback

tru = Tru()

# Wrap your RAG app
recorder = TruLlama(
    rag_app,
    feedbacks=[
        Feedback.groundedness,
        Feedback.context_relevance,
        Feedback.answer_relevance,
    ]
)

with recorder as recording:
    response = rag_app.query("...")

# Dashboard at localhost:8501
```

**Pros**: dashboard, good for ongoing monitoring
**Cons**: heavier setup

---

## 6. Building an Eval Dataset

### Approach 1: Manual Curation

```yaml
# eval_set/qa_pairs.yaml
test_cases:
  - id: "policy_001"
    question: "How many vacation days do I get?"
    expected_answer_contains: ["15 days", "annual", "after probation"]
    expected_sources: ["hr_policy.pdf"]
    difficulty: "easy"
    
  - id: "policy_002"
    question: "Compare leave policies between full-time and contract"
    expected_answer_contains: ["full-time: 15 days", "contract: pro-rated"]
    difficulty: "medium"
    type: "comparative"
```

**Process**:
1. Domain experts write 50-200 Q+A
2. Mark difficulty: easy/medium/hard
3. Tag categories
4. Update quarterly

### Approach 2: Synthetic Generation

```python
from ragas.testset.generator import TestsetGenerator

generator = TestsetGenerator.from_langchain(
    generator_llm=llm,
    critic_llm=llm,
    embeddings=embeddings,
)

testset = generator.generate_with_langchain_docs(
    documents=your_docs,
    test_size=100,
    distributions={
        "simple": 0.5,
        "reasoning": 0.25,
        "multi_context": 0.25
    }
)
```

### Approach 3: From Production Logs

```sql
-- Mine production for diverse queries
SELECT 
    user_query,
    COUNT(*) as frequency,
    AVG(user_satisfaction) as avg_satisfaction
FROM llm_traces
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY user_query
HAVING COUNT(*) > 5
ORDER BY frequency DESC
LIMIT 100;
```

---

## 7. Guardrails — AI Safety in Production

### Why Guardrails Matter

Without guardrails:
- Prompt injection attacks
- PII leakage
- Inappropriate content
- Off-topic responses
- Hallucinations causing legal/financial harm

### Guardrails Architecture

```
┌──────────────────────────────────────────────┐
│            User Input                        │
└─────────────────────┬────────────────────────┘
                      ▼
┌──────────────────────────────────────────────┐
│         INPUT GUARDRAILS                     │
│  • PII Detection & Masking                   │
│  • Prompt Injection Detection                │
│  • Topic Restriction                         │
│  • Toxic Input Detection                     │
│  • Length Limits                             │
└─────────────────────┬────────────────────────┘
                      ▼
                   [LLM]
                      ▼
┌──────────────────────────────────────────────┐
│         OUTPUT GUARDRAILS                    │
│  • Toxicity Filtering                        │
│  • PII Leakage Detection                     │
│  • Hallucination Check                       │
│  • Schema Validation                         │
│  • Topic Compliance                          │
│  • Sentiment Check                           │
└─────────────────────┬────────────────────────┘
                      ▼
              Final response
```

### Guardrail Tools 2026

| Tool | Strength |
|---|---|
| **NeMo Guardrails** (NVIDIA) | Comprehensive, programmable (Colang) |
| **Llama Guard 3** (Meta) | LLM-based safety classifier |
| **Guardrails AI** | Pythonic, schema validation focus |
| **OpenAI Moderation API** | Simple, free, basic |
| **Lakera Guard** | Commercial, enterprise focus |
| **AWS Bedrock Guardrails** | AWS integrated |

### NeMo Guardrails Pattern

```yaml
# config.yml
models:
  - type: main
    engine: anthropic
    model: claude-sonnet-4-6

rails:
  input:
    flows:
      - check pii
      - check jailbreak
      - check off-topic
  
  output:
    flows:
      - check toxicity
      - check hallucination
      - self check facts

  dialog:
    user_intents:
      - request_help
      - off_topic
    
    flows:
      handle_off_topic:
        steps:
          - "I can only help with HR questions. Try asking about..."
```

### Custom Guardrail Pattern

```python
class GuardrailPipeline:
    def __init__(self):
        self.input_checks = [
            PIIDetector(),
            PromptInjectionClassifier(),
            ToxicityClassifier(),
        ]
        self.output_checks = [
            HallucinationDetector(),
            SchemaValidator(),
            ToxicityClassifier(),
        ]
    
    async def process(self, user_input: str, context: list) -> str:
        # Input validation
        for check in self.input_checks:
            result = await check.evaluate(user_input)
            if result.blocked:
                return self.fallback_response(result.reason)
        
        # Generate
        response = await self.llm.generate(user_input, context)
        
        # Output validation
        for check in self.output_checks:
            result = await check.evaluate(response, context=context)
            if result.blocked:
                response = self.safe_fallback(result.reason)
        
        return response
```

### Common Guardrail Implementations

#### PII Detection
```python
import re
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()

def detect_pii(text):
    results = analyzer.analyze(text=text, language="en")
    pii_types = [r.entity_type for r in results]
    return {
        "has_pii": len(results) > 0,
        "types": pii_types,
        "score": max([r.score for r in results], default=0)
    }
```

#### Prompt Injection Detection
```python
from transformers import pipeline

injection_classifier = pipeline(
    "text-classification",
    model="protectai/deberta-v3-base-prompt-injection-v2"
)

def detect_injection(text):
    result = injection_classifier(text)[0]
    return {
        "is_injection": result["label"] == "INJECTION",
        "score": result["score"]
    }
```

#### Hallucination Detection (RAG context)
```python
def detect_hallucination(answer: str, context: list[str]) -> bool:
    # Method 1: NLI (Natural Language Inference)
    # Each claim in answer should be entailed by context
    claims = extract_claims(answer)
    for claim in claims:
        if not any(entails(ctx, claim) for ctx in context):
            return True
    return False
    
    # Method 2: LLM-as-judge
    # prompt = f"Is the answer fully supported by context? Yes/No"
```

#### Topic Restriction
```python
ALLOWED_TOPICS = ["HR", "vacation", "policy", "benefits"]

def check_topic(query: str) -> bool:
    embeddings = embed(query)
    topic_embeddings = embed(ALLOWED_TOPICS)
    
    max_sim = max(cosine_sim(embeddings, t) for t in topic_embeddings)
    return max_sim > 0.5  # threshold
```

---

## 8. Observability for LLM Apps

### What to Trace

```python
@trace
def llm_request(query, user_id):
    # Trace captures everything
    return rag_pipeline.run(query, user_id)
```

Each trace should log:
- **Request metadata**: user_id, session_id, timestamp
- **Input**: full query (with PII masking)
- **Pipeline steps**: each component's input/output
- **LLM details**: model, system prompt version, temperature, token counts
- **Retrieved context**: which docs/chunks (with scores)
- **Output**: full response
- **Latency breakdown**: per stage
- **Cost**: per request
- **Quality metrics**: post-hoc eval scores
- **User feedback**: thumbs up/down (when available)

### Tracing Tools

| Tool | Type |
|---|---|
| **Langfuse** | OSS, comprehensive, self-host |
| **Helicone** | OSS, simple integration |
| **LangSmith** | LangChain native, commercial |
| **Arize Phoenix** | OSS, ML/LLM combined |
| **Datadog LLM Observability** | Enterprise observability |
| **W&B Weave** | Experiment + production |

### Langfuse Integration Pattern

```python
from langfuse import Langfuse
from langfuse.decorators import observe

langfuse = Langfuse()

@observe(as_type="generation")
def generate(prompt, model):
    response = llm_client.complete(prompt, model=model)
    
    langfuse.update_current_observation(
        input=prompt,
        output=response,
        model=model,
        usage={
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
        }
    )
    return response

@observe()
def rag_query(user_query):
    # All sub-spans automatically tracked
    docs = retrieve(user_query)
    response = generate(build_prompt(user_query, docs), "claude-sonnet")
    return response
```

### Key Metrics to Dashboard

```
Volume metrics:
  - Requests per minute
  - Tokens per minute
  - Active users

Quality metrics:
  - Avg quality score (LLM judge)
  - User feedback (👍/👎 ratio)
  - Hallucination rate
  - Off-topic rate

Cost metrics:
  - $ per request
  - $ per user per day
  - Cache hit rate
  - Fallback rate

Performance metrics:
  - Time to First Token (TTFT)
  - Total response time
  - Tokens per second
  - p50/p95/p99 latency

Error metrics:
  - 4xx rate (bad input)
  - 5xx rate (provider issues)
  - Timeout rate
  - Guardrail trip rate
```

---

## 9. LLM Routing & Fallback

### Why Routing

- ไม่ใช่ทุก query ต้องการ Opus
- 80% ของ query สามารถใช้ Haiku ได้
- Saves 60-90% cost

### Routing Patterns

#### Pattern A: Rule-Based
```python
def route(query):
    if len(query) < 50:
        return "claude-haiku-4-5"  # cheap
    if "code" in query.lower():
        return "claude-sonnet-4-6"  # good for code
    if needs_deep_reasoning(query):
        return "claude-opus-4-7"  # best
    return "claude-sonnet-4-6"  # default
```

#### Pattern B: Classifier-Based
```python
classifier = LLMClassifier()  # small, fast model

def route(query):
    complexity = classifier.classify(query)  # simple/medium/complex
    return {
        "simple": "haiku",
        "medium": "sonnet",
        "complex": "opus"
    }[complexity]
```

#### Pattern C: Cost-Aware Cascade
```python
def cascading_query(query):
    # Try cheap first
    response = llm("haiku", query)
    confidence = self_score(response)
    
    if confidence > 0.8:
        return response
    
    # Escalate
    response = llm("sonnet", query)
    confidence = self_score(response)
    
    if confidence > 0.7:
        return response
    
    # Final attempt
    return llm("opus", query)
```

### Fallback Chains

```python
PROVIDERS = ["anthropic", "openai", "google"]

async def generate_with_fallback(prompt):
    for provider in PROVIDERS:
        try:
            return await call(provider, prompt, timeout=10)
        except (RateLimitError, ServerError, TimeoutError):
            continue  # try next
    raise AllProvidersFailedError()
```

### Caching Strategies

#### Exact Match Cache
```python
cache_key = hash(prompt + model + temperature)
if cached := cache.get(cache_key):
    return cached
```

#### Semantic Cache (use carefully!)
```python
# Find similar past queries
embedding = embed(query)
similar = vector_cache.search(embedding, top=1)

if similar[0].similarity > 0.95:
    return similar[0].response  # ⚠️ but may differ subtly
```

#### Prompt Caching (Provider-side)
```python
# Anthropic example
response = anthropic.messages.create(
    model="claude-sonnet-4-6",
    system=[
        {
            "type": "text",
            "text": LARGE_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}  # ← cached
        }
    ],
    messages=[{"role": "user", "content": query}]
)
# 90% discount on cached portion
```

---

## 10. Continuous Improvement Loop

```
Production traffic
       ↓
Trace logs (full request → response)
       ↓
Sample for human review (1-5%)
       ↓
Annotate quality + issues
       ↓
Identify patterns:
  - Frequent failure modes
  - Underperforming prompts
  - Missing context
       ↓
Improve:
  - Prompt updates → version bump
  - New examples in eval set
  - New guardrail rules
       ↓
A/B test changes
       ↓
Promote winners
       ↓
[loop]
```

---

## 11. Cost Management

### Cost Components

```
Per request cost = 
    embedding($) +
    vector_db_query($) +
    rerank($) +
    llm_input_tokens × $/1M_in +
    llm_output_tokens × $/1M_out
```

### Real-World Cost Example

Customer support bot, 10K conversations/day, 5 turns avg:
```
Per turn:
  - Embedding query: 100 tokens × $0.10/1M = negligible
  - Vector DB: $0.0001 per query
  - Rerank: $0.001 per query  
  - LLM: 1500 input + 300 output (Sonnet)
       = 1500 × $3/1M + 300 × $15/1M
       = $0.0045 + $0.0045
       = $0.009 per turn

Per conversation: 5 × $0.009 = $0.045
Per day: 10K × $0.045 = $450
Per month: $13,500

With smart routing (50% Haiku, 50% Sonnet):
  Avg per turn: $0.005
  Per month: $7,500 (44% savings)

With prompt caching (system prompt cached):
  Cached input cheap (10% of normal)
  Per turn: $0.003
  Per month: $4,500 (67% savings)
```

### Cost Optimization Checklist

- [ ] Smart routing (Haiku for simple)
- [ ] Prompt caching (90% off cached)
- [ ] Output limits (max_tokens)
- [ ] Embedding cache (reuse)
- [ ] Semantic cache (carefully)
- [ ] Tier retention of traces
- [ ] Use Batch API (50% discount)
- [ ] Self-host for high volume (>10M tokens/day)

---

## 12. Cheat Sheet

### Q: "ทำ LLM platform ใหม่ component ที่ต้องมีคืออะไร?"
> "5 layers: Prompt Mgmt, Eval, Guardrails, Observability, Infra
> เริ่มที่ Prompt versioning + Tracing + Basic guardrails ก่อน
> Eval framework + advanced guardrails ตามมาเมื่อ scale"

### Q: "วัด quality LLM ยังไง?"
> "Multi-layered: 
> 1. Unit tests per component
> 2. Regression suite (golden Q+A)
> 3. RAGAS หรือ DeepEval automated
> 4. LLM-as-judge for subjective
> 5. Human eval sampled
> 6. Online user feedback (thumbs up/down)"

### Q: "ทำไม guardrails สำคัญ?"
> "LLM ใน production มี attack surface ใหม่: prompt injection, jailbreak, PII leak, hallucination
> Guardrails เป็น defense layer ทั้ง input และ output
> ใช้ NeMo Guardrails หรือ Llama Guard + custom rules"

### Q: "Cost optimize LLM ยังไง?"
> "1. Smart routing (cheap model สำหรับ simple)
> 2. Prompt caching (90% off cached)
> 3. Embedding cache
> 4. Output limits
> 5. Batch API (50% off)
> 6. Self-host for very high volume"

---

## เอกสารต่อ

- [04_Agentic_AI_Patterns.md](04_Agentic_AI_Patterns.md) — multi-agent, tool use
- [02_RAG_Architecture.md](02_RAG_Architecture.md) — RAG deep dive
- [01_AI_Platform_Overview.md](01_AI_Platform_Overview.md) — overview
