# Long Context LLMs — Deep Dive

> Attention sink, RoPE scaling, needle-in-haystack, context rot
> Realities of using 1M+ token contexts ปี 2026

---

## 1. Context Window Evolution

### Timeline

```
2020: GPT-3       → 2K tokens
2022: GPT-3.5     → 4K
2023: GPT-4       → 8K → 32K
2023: Claude 2    → 100K (revolutionary!)
2024: Claude 3    → 200K
2024: Gemini 1.5  → 1M / 2M
2025: Gemini 2    → 2M
2026: Various     → 1-10M (varies by model)
```

### What Long Context Enables

- Whole books in single prompt
- Complete codebase understanding
- Long video analysis
- Cross-document reasoning
- Less RAG (sometimes)

---

## 2. The Reality: Long Context ≠ Effective Long Context

### Key Insight (2024-2026 research)

> "Models claim X tokens but **effective** context is much shorter"

### Findings

```
Claude Sonnet 4 (1M claimed):
  Effective: ~256K-500K tokens before quality drops
  
Gemini 1.5 Pro (2M claimed):
  Effective: ~500K-1M (better than most)
  
GPT-4 Turbo (128K):
  Effective: ~32K-64K before degradation
```

### "Lost in the Middle" Problem

Models tend to remember:
- Information at the **beginning** (high attention)
- Information at the **end** (recency)
- Forget the **middle**

```
User puts answer in middle of 100K context:
   Begin    Middle (target)    End
   [info1]  [ANSWER]           [info3]
                ↑ often missed
```

---

## 3. Needle in a Haystack (NIAH) Tests

### Standard NIAH

Insert a "needle" (specific fact) at varying positions in long context, ask model to retrieve

```
"In a 100K-token document of Wikipedia text,
I've inserted: 'The secret password is BLUEFISH'
What is the secret password?"
```

### Frontier Model Results (2026)

| Model | NIAH 1M Single | Multi-Needle | RULER 256K |
|---|---|---|---|
| Gemini 3 Deep Think | 99% | 89% | >80% |
| Claude Opus 4.7 | 95%+ | 75% | ~70% |
| GPT-5 | 90%+ | 70% | ~65% |
| Llama 4 (open) | 80% | 50% | <50% |

### Critical Finding

**Passing NIAH ≠ understanding long context**

Models can do "find this exact string" but fail at:
- Reasoning across multiple long-range items
- Aggregating information
- Following complex instructions over long context

### RULER Benchmark (more comprehensive)

Tests:
- Single-needle retrieval (easy)
- Multi-needle (harder)
- Multi-key (harder)
- Common words (much harder)
- Variable tracking
- Aggregation
- QA

Most models fail middle/hard tests above 64K-128K

---

## 4. Why Long Context is Hard

### Architectural Challenges

#### Quadratic Attention
```
Attention complexity: O(n²)
n=1K tokens:  1M operations
n=100K:        10B operations  (10000x)
n=1M:          1T operations   (1Mx)
```

→ Naive transformers can't scale

### Solutions Used in 2026

#### Sparse Attention
```
Don't attend to everything
- Sliding window (local)
- Strided patterns
- Specific tokens (sink, summary)
```

#### Linear Attention
```
Reformulate to O(n) instead of O(n²)
Used in: some open models
Trade-off: quality
```

#### Mixture of Experts (MoE)
```
Each token → only some experts
Reduces effective parameters touched
Used in: GPT-4, Mixtral, Llama 4
```

#### Ring Attention / Tree Attention
```
Distribute attention across GPUs
Used in: Gemini 1.5 architecture
```

---

## 5. RoPE Scaling (for Open Models)

### What RoPE Is

Rotary Positional Embeddings — encode position via rotation in vector space

Default: trained on N tokens (e.g., 8K)
Beyond N: position encodings break

### Problem

Train on 8K → use at 32K = quality crashes

### Solutions

#### Linear Scaling
```python
# Scale rotation frequencies linearly
rope_scaling = {"type": "linear", "factor": 4.0}
# Stretches 8K → 32K
# Quality OK at 16K, degrades after
```

#### NTK-Aware Scaling
```python
# Better than linear
rope_scaling = {"type": "ntk", "factor": 4.0}
# Maintains quality better at extended context
```

#### YaRN (best for open models)
```python
rope_scaling = {"type": "yarn", "factor": 4.0}
# Best non-fine-tuned scaling
# Still benefits from continued pre-training
```

### Continued Pre-training

For best long-context: fine-tune on long sequences

```python
# After base model trained 8K
# Continue training on 32K-128K sequences
# Adapts attention patterns
```

---

## 6. Attention Sink Phenomenon

### What is Attention Sink

In long contexts, attention concentrates on:
- BOS (beginning) token
- Last few tokens
- A few "anchor" tokens

Mid-context tokens become "invisible"

### Why Happens

Softmax attention always sums to 1
Long context → most tokens get tiny attention
Few tokens absorb most attention (sinks)

### Symptoms

```
Context: [BOS][...100K of text...][user query]
          ↑                          ↑
       attention                  attention
       
Middle tokens get ~0 attention
"Effective" context shrinks
```

### Fixes (model-side)

#### StreamingLLM
- Keep BOS + recent window
- Drop middle, retain sinks
- Used for endless conversation

#### Attention Sink Training
- Explicitly train to use sinks
- Better stability at length

---

## 7. Long Context Best Practices

### Pattern 1: Put Important Stuff at Beginning AND End

```
Bad layout:
  [system prompt][1000 docs][user question]
                              ↑ might miss docs

Good layout:
  [system prompt + key instructions]
  [1000 docs]
  [user question + RESTATE key instructions]
```

### Pattern 2: Explicit Structure

```
"Below is information across 5 sections.
You will be asked questions about each.

<section_1>
[content]
</section_1>

<section_2>
[content]
</section_2>
...

When answering, FIRST identify which section the question relates to."
```

### Pattern 3: Multi-Step over Long Context

```
Step 1: Summarize each chunk (parallel)
Step 2: Combine summaries
Step 3: Answer using combined summary

Better than: dump all into one prompt
```

### Pattern 4: Chunk-then-Verify

```
1. Split context into chunks
2. For each chunk, ask: "Does this answer query?"
3. If yes → use that chunk
4. Verify with full context if needed
```

### Pattern 5: Always Test, Never Trust

Don't assume model "understood" 100K context
Verify with:
- Specific factual questions
- Cross-reference questions
- Quote-supporting answers

---

## 8. Long Context vs RAG — The Decision

### When Long Context Wins

✅ Information needs to be considered jointly
   - "Compare these 5 contracts"
   
✅ Document is < context window
   - Single book, single codebase

✅ Need cross-references in same prompt
   - Multi-hop reasoning across documents

### When RAG Wins

✅ Information dynamically updated
   - Knowledge base changes daily
   
✅ Many documents (more than fits)
   - 10,000 documents

✅ Cost matters
   - Long context = expensive per query

✅ Need citations / sources
   - RAG provides explicit attribution

### Hybrid: Best of Both

```
1. RAG retrieves top-50 candidates
2. Rerank to top-10
3. Send to long-context model (10 docs × 5K = 50K)
4. Model has context to reason across all 10
```

---

## 9. Cost Implications

### Per Query Cost (Sonnet pricing as example)

```
Input: $3 / 1M tokens

10K context:    $0.03 per query
100K context:   $0.30 per query
1M context:     $3.00 per query

10K queries/day at 1M context = $30K/day = $900K/month
```

### Caching Helps Massively

```python
# Anthropic prompt caching
# 90% off cached input tokens
# Cache TTL: 5 minutes

response = client.messages.create(
    model="claude-sonnet-4-6",
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": LONG_DOC,  # 1M tokens
                "cache_control": {"type": "ephemeral"}
            },
            {
                "type": "text",
                "text": USER_QUERY  # variable
            }
        ]
    }]
)

# First call: $3
# Subsequent calls within 5 min: $0.30 (90% off cached)
```

### Optimization Patterns

1. **Cache long context** (system prompts, RAG context)
2. **Trim aggressively** (only what model needs)
3. **Use long context strategically** (high-value queries only)
4. **Distill to shorter** (summarize first, then query)

---

## 10. Code with Long Context

### Code Repository Analysis

```python
# Cline-like pattern
import anthropic

client = anthropic.Anthropic()

# Concat entire repo
repo_content = ""
for file in walk_repo("./my_project"):
    repo_content += f"\n\n--- {file.path} ---\n{file.content}"

# Query
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": f"""Codebase:
{repo_content}

Task: Find all places where authentication is checked.
Return file paths + line numbers."""
    }]
)
```

### Limitations

- Repo > 1M tokens = doesn't fit
- Cost: $3+ per query at 1M
- Quality varies on big repos

### Better: Hybrid

```python
# 1. Index repo with embeddings
# 2. Query → retrieve relevant files
# 3. Send only relevant files to long-context model
```

---

## 11. Long Context Use Cases

### 1. Legal Document Analysis
```
Contract: 200 pages
Queries: 50+ across the contract
Long context = consistent understanding
```

### 2. Medical Records Review
```
Patient history: years of records
Need cross-temporal patterns
RAG would lose connections
```

### 3. Codebase Q&A
```
"How does feature X work?"
Need to follow function calls across files
Long context > RAG for code
```

### 4. Book Summarization
```
Whole novel → consistent character/plot tracking
Cannot do well with chunked summary
```

### 5. Multi-Document Synthesis
```
"Compare findings across 10 papers"
Need to reason across all simultaneously
```

### 6. Long Conversation History
```
Customer support chat history
Personalization across years
```

---

## 12. Context Rot

### Phenomenon (Chroma research, 2024)

Quality degrades non-linearly with context length, even within "supported" window:

```
Tokens     Quality (relative)
8K         100%
32K        95%
128K       80%
500K       60%
1M         40%
```

### Causes

- Attention dilution
- Position encoding edge effects
- Training data distribution
- Lost-in-middle bias

### Implications

- Don't max out context "because you can"
- Effective context << theoretical
- Test your specific use case

---

## 13. Future Directions (2026+)

### Hybrid Approaches Winning

```
Pure long context: declining
Pure RAG: limited
Hybrid (RAG + long-context model): future

Best 2026 systems:
- Smart retrieval (find relevant)
- Long context (reason across retrieved)
- Memory systems (persistent state)
```

### Trends

#### 1. Inference-Time Scaling
- Beyond just bigger context
- Reasoning steps, planning
- Compute at inference

#### 2. Memory Augmentation
- Persistent state across sessions
- Less reliance on stuffing context

#### 3. Compression Models
- Compress context to summaries
- Use compressed in inference
- E.g., LongRoPE, LongAlign

#### 4. Specialized Long-Context Models
- Some models optimized for long retrieval
- Others for long reasoning
- Pick by use case

---

## 14. Cheat Sheet

### Q: "Use long context หรือ RAG ดี?"
> "Long context: คุณจะ reason ข้าม documents ทั้งหมดพร้อมกัน
> RAG: หา specific info จาก large knowledge base
> Hybrid (best 2026): RAG retrieves → long-context model reasons"

### Q: "1M context ใช้ได้จริงมั้ย?"
> "Effective context << claimed
> Gemini 2.5 Pro: ~500K-1M effective (best)
> Claude Opus 4.7: ~256K-500K effective
> ส่วนใหญ่: degradation noticeable above 64-128K"

### Q: "ป้องกัน 'lost in middle' ยังไง?"
> "1. Put important info at beginning AND end
> 2. Use clear structure (XML tags, headers)
> 3. Restate query/instructions at end
> 4. Multi-step (summarize → answer)
> 5. Test specific use case"

### Q: "Cost long context จัดการยังไง?"
> "Prompt caching (90% off cached portion)
> Trim aggressively
> Use long context only for high-value queries
> Distill long → short for repeated queries"

### Q: "RoPE scaling ทำงานยังไง?"
> "Modify rotary positional embeddings เพื่อ extend context
> YaRN: best non-fine-tuned (open models)
> NTK-aware: middle ground
> Linear: simplest, most quality loss
> Best: continued pre-training on long sequences"

---

## Sources

- [LLMTest_NeedleInAHaystack GitHub](https://github.com/gkamradt/LLMTest_NeedleInAHaystack)
- [Long-Context Retrieval 2026: Needle-in-Haystack Test](https://www.digitalapplied.com/blog/long-context-retrieval-needle-in-haystack-2026)
- [Long Context LLMs Python: RoPE Scaling Laws](https://johal.in/long-context-llms-python-rope-scaling-laws-in-llama-cpp-2026/)
- [The Needle In a Haystack Test - Arize AI](https://arize.com/blog-course/the-needle-in-a-haystack-test-evaluating-the-performance-of-llm-rag-systems/)
- [Hidden in the Haystack: Smaller Needles are More Difficult](https://openreview.net/forum?id=PlH3YDvGhF)
- [LLM Context Window Management and Long-Context Strategies 2026](https://zylos.ai/research/2026-01-19-llm-context-management)
- [Context Rot: How Increasing Input Tokens Impacts LLM Performance - Chroma](https://research.trychroma.com/context-rot)
- [The Role of Long Context in LLMs for RAG](https://medium.com/@miteigi/the-role-of-long-context-in-llms-for-rag-a-comprehensive-review-499d73367e89)
