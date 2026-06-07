# RAG Architecture — Deep Dive

> Retrieval-Augmented Generation: เทคนิคที่ครองตลาด enterprise GenAI ปี 2026
> 73% of RAG failures = retrieval failure, ไม่ใช่ generation failure

---

## 1. ทำไม RAG สำคัญที่สุดในโลก enterprise GenAI

### LLM เปล่าๆ มีปัญหาอะไร

1. **Knowledge cutoff** — ไม่รู้ข้อมูลใหม่
2. **Hallucination** — แต่งคำตอบที่ดูน่าเชื่อ
3. **No private data** — ไม่รู้ข้อมูลภายในบริษัท
4. **No traceability** — บอกไม่ได้ว่าเอามาจากไหน
5. **Can't update** — fine-tune ใหม่ทุกครั้ง = แพง

### RAG แก้ทั้ง 5 ข้อ

```
User question
    ↓
Retrieve relevant documents (private + fresh data)
    ↓
Inject into LLM context
    ↓
LLM generates answer with citations
    ↓
Response (grounded + traceable)
```

**Key insight**: LLM ไม่ต้อง "รู้" — แค่ "อ่านเก่ง"

---

## 2. RAG Architecture Layers — แบ่งให้ชัด

```
┌─────────────────────────────────────────────────────────┐
│              INGESTION PIPELINE (offline)               │
│  Source docs → Parse → Chunk → Embed → Index            │
└─────────────────────────────────────────────────────────┘
                            ↓
                   ┌─────────────────┐
                   │  VECTOR DB +    │
                   │  KEYWORD INDEX  │
                   └─────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              RETRIEVAL PIPELINE (online)                │
│  Query → Embed → Hybrid search → Rerank → Top-K         │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              GENERATION PIPELINE (online)               │
│  Top-K + Query → Build prompt → LLM → Parse → Cite      │
└─────────────────────────────────────────────────────────┘
                            ↓
                       Response
```

---

## 3. Stage 1: Document Ingestion

### Step 1.1: Document Loading

ไม่ใช่ทุกเอกสารเป็น PDF — ต้องจัดการ:
- PDF (text-based + scanned)
- Word/Google Docs
- HTML / Markdown
- PPT / Slides
- Spreadsheets (CSV, Excel)
- Images (with OCR)
- Audio/Video (with transcription)

### Tools 2026

| Tool | Strength |
|---|---|
| **Unstructured.io** | All-in-one, handles 25+ formats |
| **LlamaParse** | LLM-based parsing, great for complex PDFs |
| **Azure Document Intelligence** | Forms, tables |
| **Apache Tika** | Open source, traditional |
| **Docling** | IBM, fast, structured output |

### Anti-pattern

❌ Use simple PDF text extraction → loses tables, structure
✅ Use document-aware parser → preserves headings, tables, code blocks

---

### Step 1.2: Chunking — Most Critical

**Insight 2026**: 73% of RAG failures = retrieval failures = chunking failures

#### Chunking Strategies

##### Strategy A: Fixed-Size Chunking (baseline)
```python
def fixed_size_chunk(text, size=512, overlap=50):
    chunks = []
    for i in range(0, len(text), size - overlap):
        chunks.append(text[i:i+size])
    return chunks
```
**Pros**: simple, predictable
**Cons**: cuts mid-sentence, loses context

##### Strategy B: Sentence-Aware Splitting
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""]
)
```
**Pros**: respects sentence boundaries
**Cons**: doesn't understand semantic meaning

##### Strategy C: Semantic Chunking
```python
# Detect topic boundaries by embedding similarity
def semantic_chunk(sentences, threshold=0.7):
    embeddings = embed(sentences)
    chunks = [[sentences[0]]]
    for i in range(1, len(sentences)):
        sim = cosine(embeddings[i-1], embeddings[i])
        if sim < threshold:
            chunks.append([])
        chunks[-1].append(sentences[i])
    return ["".join(c) for c in chunks]
```
**Pros**: chunks = topics
**Cons**: slow (need embedding for each sentence)

##### Strategy D: Document-Aware Chunking
```python
# Use document structure (markdown headers, HTML tags)
def markdown_chunk(text):
    sections = split_by_headers(text)  # H1, H2, H3
    chunks = []
    for section in sections:
        if len(section) > 1000:
            chunks.extend(recursive_split(section, 500))
        else:
            chunks.append(section)
    # Preserve heading context in metadata
    return chunks
```
**Pros**: preserves logical structure
**Cons**: requires structured docs

##### Strategy E: Late Chunking (2024+)
```
1. Embed entire document at once (with long-context model)
2. Then split tokens into chunks
3. Average pooling per chunk = chunk embedding

Benefit: each chunk has full document context baked in
```

#### Chunk Size Guidelines

| Size | Use case |
|---|---|
| 100-256 tokens | Code snippets, exact lookups |
| 256-512 tokens | General Q&A, FAQ |
| 512-1024 tokens | Complex docs, technical |
| 1024-2048 tokens | Long-form content |
| Late chunking | Best for any size |

**กฎ**: chunk ใหญ่ = context มากขึ้น แต่ noise มากขึ้น
        chunk เล็ก = precision สูง แต่ context ขาด

#### Metadata to Preserve

ทุก chunk ต้องมี metadata:
```python
chunk = {
    "text": "...",
    "embedding": [...],
    "metadata": {
        "doc_id": "policy_2026.pdf",
        "doc_title": "HR Policy 2026",
        "section": "Vacation Policy",
        "section_number": "3.2",
        "page": 15,
        "source_url": "https://...",
        "doc_type": "policy",
        "department": "HR",
        "language": "th",
        "last_updated": "2026-04-15",
        "access_level": "all_employees"
    }
}
```

---

### Step 1.3: Embedding

#### What is Embedding

ตัวเลข vector ที่แทน "ความหมาย" ของข้อความ
- Vector dim ปกติ 768-3072
- คำว่า "หมา" และ "สุนัข" → vectors ใกล้กัน

#### Embedding Models (2026 Leaders)

| Model | Provider | Dim | Strength |
|---|---|---|---|
| **voyage-3** | Voyage AI | 1024 | Best on MTEB benchmark |
| **text-embedding-3-large** | OpenAI | 3072 | General purpose |
| **Cohere embed-v4** | Cohere | 1024 | Multilingual |
| **gte-large-v1.5** | Open source | 1024 | Free self-host |
| **bge-m3** | Open source | 1024 | Multilingual, multi-functional |
| **voyage-code-3** | Voyage AI | 1024 | Code-specific |
| **multilingual-e5-large** | Open source | 1024 | Multilingual |

#### Domain-Specific Considerations

- **Code**: voyage-code-3, bge-code
- **Multilingual**: bge-m3, multilingual-e5
- **Long documents**: jina-embeddings-v3 (8192 tokens)
- **Cost-sensitive**: text-embedding-3-small (1536 dim, cheap)

#### Embedding Pipeline (production pattern)

```python
class EmbeddingPipeline:
    def __init__(self):
        self.model = VoyageEmbedder("voyage-3")
        self.batch_size = 100
    
    def process(self, chunks: list[Chunk]) -> list[Chunk]:
        # Batch for efficiency
        for batch in chunked(chunks, self.batch_size):
            texts = [c.text for c in batch]
            embeddings = self.model.embed(texts)
            for chunk, emb in zip(batch, embeddings):
                chunk.embedding = emb
        return chunks
```

#### Re-embedding Strategy

เมื่อเปลี่ยน embedding model ต้อง re-embed ทุก chunk
- กลยุทธ์ A: full re-embed (downtime, cost)
- กลยุทธ์ B: dual indexing (run both models in parallel, switch when ready)
- กลยุทธ์ C: gradual migration (re-embed by priority)

---

### Step 1.4: Indexing

Index data ลงใน:
1. **Vector index** (semantic search)
2. **Keyword index** (BM25 lexical search)
3. **Metadata index** (structured filters)

#### Vector Index Algorithms

| Algorithm | Trade-off |
|---|---|
| **HNSW** (Hierarchical Navigable Small World) | Best balance, default choice |
| **IVF** (Inverted File Index) | Faster build, less memory |
| **PQ** (Product Quantization) | Compression, smaller storage |
| **Flat** (brute force) | Exact, slow, only for small data |

#### HNSW Parameters

```
M: number of connections per node (8-64, default 16)
  Higher M = better recall but more memory
  
ef_construction: build-time search depth (200-800)
  Higher = better index but slower build
  
ef_search: query-time search depth (50-500)
  Higher = better recall but slower query
```

---

## 4. Stage 2: Retrieval Pipeline

### Architecture: Hybrid + Rerank

```
       Query
         │
    ┌────┴────┐
    ▼         ▼
[Vector]   [BM25/Keyword]
 search     search
    │         │
    ▼         ▼
 Top-50    Top-50
    └────┬────┘
         ▼
    [Fusion (RRF)]
         ▼
    Top-50 candidates
         ▼
    [Reranker (cross-encoder)]
         ▼
    Top-5 final
         ▼
    Pass to LLM
```

### Step 2.1: Query Embedding

```python
def embed_query(query: str, model="voyage-3") -> list[float]:
    # Some models have query-specific instructions
    enhanced = f"Represent this query for retrieval: {query}"
    return embed(enhanced)
```

**Pro tip**: Query rewriting can improve retrieval
- HyDE (Hypothetical Document Embedding): LLM generates hypothetical answer, embed that
- Multi-query: LLM generates variations of query, retrieve all
- Step-back: ask broader question first

### Step 2.2: Vector Search

```python
results = vector_db.search(
    vector=query_embedding,
    top_k=50,
    filter={"doc_type": "policy", "language": "th"},
    include_metadata=True
)
```

### Step 2.3: BM25 / Keyword Search

```python
# BM25 still undefeated for exact match
keyword_results = keyword_index.search(
    query=query,
    top_k=50,
    filter={...}
)
```

**Why BM25 still matters**:
- Product codes (XJ-9572)
- Legal terms ("Section 5(a)(ii)")
- Names (James Wilson)
- Acronyms (CRM, ETL)

### Step 2.4: Hybrid Fusion (RRF)

Reciprocal Rank Fusion combines rankings:
```python
def rrf(rankings: list[list[Document]], k=60) -> list[Document]:
    scores = defaultdict(float)
    for ranking in rankings:
        for rank, doc in enumerate(ranking):
            scores[doc.id] += 1 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: -x[1])
```

### Step 2.5: Reranking (Most Important Quality Lever)

**ผลลัพธ์**: rerank ช่วยเพิ่ม quality 15-30% บน RAGAS metrics

#### Cross-Encoder vs Bi-Encoder

```
Bi-Encoder (embedding):
  Encode query → vector_q
  Encode each doc → vector_d (precomputed)
  Score = cosine(vector_q, vector_d)
  Fast but loses interaction
  
Cross-Encoder (reranker):
  Concatenate (query, doc) → BERT → score
  Slow but captures fine-grained interaction
  Use only for top-K rerank
```

#### Reranker Models 2026

| Model | Type |
|---|---|
| **Cohere Rerank 3** | Commercial API, best quality |
| **BAAI/bge-reranker-v2-m3** | Open source, multilingual |
| **Jina Reranker v2** | Open source |
| **Voyage Rerank** | Commercial API |

#### Implementation

```python
from cohere import Client

co = Client()

def rerank(query: str, docs: list[Document], top_k=5):
    response = co.rerank(
        query=query,
        documents=[d.text for d in docs],
        top_n=top_k,
        model="rerank-english-v3.0"
    )
    
    # Reorder by relevance score
    return [docs[r.index] for r in response.results]
```

---

## 5. Stage 3: Generation

### Step 3.1: Prompt Construction

```python
SYSTEM_PROMPT = """You are a helpful HR assistant. 
Answer questions using ONLY the provided context.
If the answer isn't in the context, say "I don't know based on the documents I have."
Always cite sources using [doc_id, page] format.
"""

def build_prompt(query, contexts):
    context_str = "\n\n".join([
        f"[Source: {c.metadata['doc_id']}, page {c.metadata['page']}]\n{c.text}"
        for c in contexts
    ])
    
    return f"""Context:
{context_str}

Question: {query}

Answer (with citations):"""
```

### Step 3.2: Context Window Management

ปัญหา: LLM context limited, ต้องเลือก
- เก่า: GPT-3.5 = 4K, GPT-4 = 8K
- ใหม่: Claude = 200K, Gemini = 2M

แต่: "needle in haystack" — long context ลดคุณภาพ

**Strategy**: ส่งแค่ top-3-5 chunks ที่ rerank แล้ว ไม่ใช่ทั้งหมด

### Step 3.3: Citation Generation

```python
# Approach A: Inline citations
"Based on the document [policy.pdf, p.5], vacation is..."

# Approach B: Structured output
{
  "answer": "Vacation is 15 days...",
  "citations": [
    {"doc": "policy.pdf", "page": 5, "snippet": "..."}
  ]
}

# Approach C: Source verification (recommended)
After generation:
  1. Extract claims from answer
  2. For each claim, find supporting chunk
  3. If no support, mark as "ungrounded"
```

---

## 6. Advanced RAG Patterns (2026)

### Pattern A: Query Decomposition

```
User: "Compare Tokyo and Bangkok climate, food, and cost"

Decompose into sub-queries:
  1. Tokyo climate
  2. Bangkok climate  
  3. Tokyo food
  4. Bangkok food
  5. Tokyo cost
  6. Bangkok cost

Run parallel retrieval for each
Aggregate context
LLM synthesizes
```

### Pattern B: Multi-Hop RAG

```
User: "Who is the CEO of the company that acquired Anthropic?"

Step 1: Retrieve "Who acquired Anthropic?"
  → Answer: Amazon (partial)
  
Step 2: Retrieve "Who is CEO of Amazon?"
  → Answer: Andy Jassy
  
Final: "Andy Jassy is the CEO of Amazon, which has invested heavily in Anthropic"
```

### Pattern C: Self-Querying

```
User: "Recent papers on transformers from 2025"

LLM extracts filters from query:
  topic = "transformers"
  year >= 2025
  type = "paper"

Apply structured filters + semantic search on topic
```

### Pattern D: HyDE (Hypothetical Document Embedding)

```
1. User query: "How to handle data drift?"
2. LLM generates hypothetical answer:
   "Data drift can be handled by..."
3. Embed hypothetical answer (not query)
4. Search with that embedding

Why: hypothetical answer is closer in vector space
to actual relevant docs than the query
```

### Pattern E: Contextual Retrieval (Anthropic 2024)

```
For each chunk during indexing:
  1. LLM generates "context blurb" (50-100 tokens)
     describing where chunk fits in document
  2. Prepend blurb to chunk before embedding
  3. Result: chunks have global context

Benefit: 49% reduction in retrieval failures
```

### Pattern F: GraphRAG (Microsoft)

```
1. Extract entities + relationships from docs → knowledge graph
2. For each query, traverse graph + retrieve text
3. Better for queries needing relationships

Use case: "How is X related to Y?" type questions
```

### Pattern G: Adaptive Retrieval

```
Query classifier decides:
  Simple factual → vanilla RAG
  Multi-faceted → query decomposition
  Comparative → graph traversal
  Numerical → SQL agent
```

---

## 7. Vector Database Selection

### Decision Matrix

| Need | Recommendation |
|---|---|
| Managed, easy start | **Pinecone** |
| GCP-native | **Vertex Vector Search** |
| Open source self-host, < 10M vectors | **Qdrant** |
| Open source self-host, > 100M vectors | **Milvus** or **Vespa** |
| Have Postgres already | **pgvector** |
| Best hybrid search | **Weaviate** or **Qdrant** |
| Embedded/on-device | **Chroma** |

### Performance Benchmark (2026 typical)

| DB | p99 Latency | QPS (single node) | Cost (10M vectors) |
|---|---|---|---|
| Qdrant | 2ms | 12,000 | $200/mo (self-host) |
| FAISS | 3ms | 15,000 | n/a (library) |
| Milvus | 5ms | 8,000 | $400/mo |
| Pinecone | 8ms | 5,000 | $700/mo (managed) |
| Weaviate | 10ms | 4,000 | $300/mo |

### Hybrid Search Support

| DB | Native Hybrid | Filtering |
|---|---|---|
| Weaviate | ✅ Excellent | ✅ |
| Qdrant | ✅ Good | ✅ Strong |
| Pinecone | ✅ Added 2024 | ✅ |
| Milvus | ✅ Good | ✅ |
| pgvector | Manual | ✅ via SQL |

---

## 8. RAG Evaluation Framework (RAGAS)

### Key Metrics

#### Retrieval Metrics
| Metric | What it measures |
|---|---|
| **Context Precision** | Are retrieved chunks relevant? |
| **Context Recall** | Did we retrieve all relevant chunks? |
| **Context Relevance** | Are chunks pertinent to query? |

#### Generation Metrics
| Metric | What it measures |
|---|---|
| **Faithfulness** | Answer grounded in context (no hallucination)? |
| **Answer Relevance** | Answer addresses the question? |
| **Answer Correctness** | Factually correct? (vs ground truth) |

### RAGAS Implementation

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from datasets import Dataset

eval_data = Dataset.from_dict({
    "question": [...],
    "answer": [...],          # generated by your RAG
    "contexts": [...],        # retrieved chunks
    "ground_truth": [...],    # known correct answer
})

result = evaluate(
    eval_data,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    ]
)

print(result)
# {faithfulness: 0.92, answer_relevancy: 0.88, ...}
```

### Building Eval Dataset

**Approach 1: Manual (highest quality)**
- 50-200 Q+A pairs from domain experts
- Time: weeks

**Approach 2: Synthetic (faster)**
- LLM generates Q+A from your docs
- RAGAS has `TestsetGenerator`
- Validate sample manually

**Approach 3: Hybrid**
- Synthetic for breadth
- Manual for critical paths

---

## 9. Cost Optimization

### Cost Drivers

```
Total cost = ingest_cost + storage_cost + retrieval_cost + generation_cost

Ingest:
  - Embedding API calls (one-time per chunk)
  
Storage:
  - Vector DB ($/GB/month)
  
Retrieval:
  - Query embeddings (per query)
  - Vector DB queries (per query)
  - Reranking (per query)
  
Generation:
  - LLM tokens (input + output)
```

### Optimization Strategies

#### 1. Caching
- **Embedding cache**: same text → reuse embedding (huge savings)
- **Query cache**: identical query → return same answer
- **Semantic cache**: similar query → return cached (use carefully)

#### 2. Smaller Embeddings
- text-embedding-3-small (1536 dim) vs large (3072 dim)
- Same model, smaller vectors = 2x cost saving
- Quality drop usually small

#### 3. Tiered Retrieval
```
Level 1: Cheap retrieval (BM25 only) → top 100
Level 2: Vector search rerank → top 20
Level 3: Cross-encoder rerank → top 5
```
Skip levels for simple queries

#### 4. Model Routing
- Simple queries → Haiku ($)
- Complex queries → Opus ($$$)
- Could save 60-80%

#### 5. Prompt Caching (Anthropic, OpenAI 2024+)
- System prompt + base context cached
- 90% discount on cached tokens
- Huge savings for chatbots with consistent system prompt

---

## 10. Common RAG Failure Modes

### Failure 1: Retrieval misses relevant docs
**Symptom**: LLM says "I don't know" but answer is in docs
**Causes**:
- Bad chunking (sentence cut mid-thought)
- Wrong embedding model for domain
- Query too different from doc language

**Fixes**:
- Better chunking strategy
- Domain-specific embeddings
- Query rewriting (HyDE)
- Hybrid search

### Failure 2: Hallucination despite RAG
**Symptom**: LLM makes up facts not in context
**Causes**:
- LLM trusts pre-training over context
- Bad system prompt

**Fixes**:
- Stronger system prompt: "ONLY use context"
- Faithfulness scoring
- Citation verification step
- Use Claude (less hallucinatory than GPT generally)

### Failure 3: Wrong context retrieved
**Symptom**: Answer is plausible but from wrong doc
**Causes**:
- No reranker
- Filter not applied (e.g., no department filter)
- Documents too similar

**Fixes**:
- Add reranker
- Stronger metadata filters
- Self-querying RAG

### Failure 4: Out-of-scope queries
**Symptom**: User asks unrelated, RAG returns random doc
**Causes**:
- No relevance threshold

**Fixes**:
- Set min similarity threshold
- Add "I don't have info on that" fallback
- Use rerank score < threshold → "no answer"

### Failure 5: Stale information
**Symptom**: Answers based on outdated docs
**Causes**:
- No document refresh policy
- No timestamp filter

**Fixes**:
- Re-ingest pipeline (delta updates)
- Timestamp metadata + filter
- Iceberg snapshot tracking for source

---

## 11. Production RAG Architecture (Reference Implementation)

### Stack ปี 2026

```
INGESTION (offline batch + incremental):
  Source: SharePoint, Confluence, Drive
  Parse: Unstructured.io
  Chunk: LlamaIndex (semantic + recursive)
  Embed: voyage-3 (or text-embedding-3-large)
  Store: Iceberg (raw + chunks + metadata)
        + Pinecone/Qdrant (vectors)
        + Elasticsearch (BM25)

RETRIEVAL (online):
  Embed query: voyage-3
  Hybrid: Vector + BM25 (RRF fusion)
  Rerank: Cohere Rerank 3
  Filter: metadata (department, language, date)

GENERATION:
  LLM: Claude Sonnet 4.6 (default), Haiku for simple
  Prompt: Templated with citations
  Output: structured JSON with sources

OBSERVABILITY:
  Tracing: Langfuse
  Eval: RAGAS (offline) + custom (online)
  Cost: per-request token tracking

ORCHESTRATION:
  Framework: LlamaIndex or LangChain
  Server: FastAPI + Cloud Run
  
DATA PLATFORM:
  Document store: Iceberg on GCS
  Lineage: track source → chunk → answer
```

### Pseudo-code End-to-End

```python
class ProductionRAG:
    def __init__(self):
        self.embedder = VoyageEmbedder("voyage-3")
        self.vector_db = PineconeClient()
        self.bm25 = ElasticsearchClient()
        self.reranker = CohereReranker()
        self.llm = AnthropicClient()
        self.tracer = LangfuseTracer()
    
    @trace
    def query(self, user_query: str, user_id: str):
        # 1. Input guardrails
        if detect_pii(user_query):
            user_query = mask_pii(user_query)
        
        # 2. Query enhancement
        rewritten = self.llm.rewrite_query(user_query)
        
        # 3. Hybrid retrieval
        query_emb = self.embedder.embed(rewritten)
        
        vector_results = self.vector_db.search(
            vector=query_emb,
            top_k=50,
            filter={"access_level": user_access_level(user_id)}
        )
        bm25_results = self.bm25.search(rewritten, top_k=50)
        
        # 4. Fusion + Rerank
        fused = rrf_fusion([vector_results, bm25_results])
        reranked = self.reranker.rerank(rewritten, fused, top_k=5)
        
        # 5. Threshold check (no answer if low relevance)
        if max(r.score for r in reranked) < 0.3:
            return {"answer": "I don't have information on that.", "sources": []}
        
        # 6. Build prompt + generate
        prompt = build_prompt(user_query, reranked)
        response = self.llm.generate(
            prompt,
            system=SYSTEM_PROMPT,
            temperature=0
        )
        
        # 7. Output guardrails
        if detect_hallucination(response, reranked):
            response = "I'm not sure based on available info."
        
        # 8. Citation verification
        verified = verify_citations(response, reranked)
        
        # 9. Log + return
        self.tracer.log(user_query, reranked, response)
        return {
            "answer": response,
            "sources": [r.metadata for r in reranked],
            "confidence": verified.confidence
        }
```

---

## 12. Cheat Sheet

### Q: "RAG ทำงานยังไง?"
> "3 stage: ingest (parse, chunk, embed, index), retrieve (hybrid search + rerank), generate (build prompt + LLM)
> Key insight: 73% ของ RAG fail ที่ retrieval ไม่ใช่ generation"

### Q: "Chunk ขนาดไหนดี?"
> "ขึ้นกับ use case: 256-512 ทั่วไป, 100-256 สำหรับ exact lookup, 1024+ สำหรับ long-form
> สำคัญกว่าขนาด คือ semantic boundary — อย่าตัดกลางประโยค"

### Q: "ทำไม rerank สำคัญ?"
> "Bi-encoder (embedding) เร็วแต่ลึก่ดน้อย — Cross-encoder (rerank) อ่านทั้ง query+doc ลึกขึ้น
> rerank top-50 → top-5 ช่วยเพิ่ม quality 15-30% บน RAGAS"

### Q: "Vector DB ตัวไหน?"
> "เริ่ม: Pinecone (managed) หรือ Qdrant (self-host)
> GCP: Vertex Vector Search
> มี Postgres: pgvector
> Scale > 100M: Milvus หรือ Vespa"

### Q: "ป้องกัน hallucination ใน RAG ยังไง?"
> "1. System prompt บังคับ 'ONLY use context'
> 2. Faithfulness scoring (RAGAS)
> 3. Citation verification post-generation
> 4. Threshold relevance — ถ้า rerank < threshold = 'ไม่รู้'"

---

## เอกสารต่อ

- [03_LLMOps_and_Evaluation.md](03_LLMOps_and_Evaluation.md) — prompt mgmt, eval framework
- [04_Agentic_AI_Patterns.md](04_Agentic_AI_Patterns.md) — multi-step agents
- [01_AI_Platform_Overview.md](01_AI_Platform_Overview.md) — overall architecture
