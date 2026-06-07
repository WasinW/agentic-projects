# 05 — Memory & Knowledge

> Agent ที่ไม่จำได้ = ChatGPT — Memory คือสิ่งที่ทำให้ agent มี "อายุ" ยาว
> Vector DB, embedding, chunking, knowledge graph — เลือก stack ฟรีๆ ได้

---

## 1. 3 ชั้นของ Memory

```
┌──────────────────────────────────────────────────────┐
│  WORKING MEMORY                  (this conversation) │
│  - Messages, scratchpad, current task state          │
│  - LLM context window                                │
│  - หายเมื่อ session end                                │
└──────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────┐
│  EPISODIC MEMORY              (session history)      │
│  - "เมื่อวาน user ขอ X, เราตอบ Y"                      │
│  - Conversation log persisted                        │
│  - Storage: SQL / NoSQL / vector DB                  │
└──────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────┐
│  SEMANTIC MEMORY              (knowledge base)       │
│  - "Domain facts" "company SOP" "user preferences"   │
│  - Vector DB / Knowledge graph / SQL                 │
│  - Shared across users/sessions                      │
└──────────────────────────────────────────────────────┘
```

### Working Memory
- ใส่ใน context window (ทุก LLM call)
- จำกัดด้วย context size + cost
- Optimize: summarization, compression, sliding window

### Episodic Memory
- ใช้เมื่ออยากให้ agent จำ "ครั้งก่อน"
- ตัวอย่าง: customer support agent จำว่า user เคย refund อะไร
- Storage: เริ่มที่ SQLite/Postgres → ถ้า search ต้องการ semantic → vector DB

### Semantic Memory
- คือ "knowledge" ที่ agent ใช้อ้างอิง
- Pattern หลัก: RAG (Retrieval-Augmented Generation)
- Storage: vector DB (สำคัญสุด)

---

## 2. RAG Refresher (สั้นๆ)

```
INDEXING (offline):
  Documents → Chunk → Embed → Vector DB

QUERY (online):
  User Q → Embed → Search Vector DB → Top K chunks
                                          ↓
                       LLM(Q + chunks) → Answer
```

ถ้ายังไม่คุ้น RAG → กลับไปอ่าน `learning/data_platform/AI/02_RAG_Architecture.md`

ในที่นี้จะเน้น **agent + memory** — RAG เป็น primitive อย่างหนึ่ง

---

## 3. Vector DB Comparison

### 3.1 ตารางเปรียบเทียบ

| DB | Type | Free? | Best for | RAM/disk |
|---|---|---|---|---|
| **Qdrant** | Self-host | ✅ OSS | Production, hybrid search | Low-Medium |
| **Chroma** | Self-host / cloud | ✅ OSS | Prototype, local dev | Low |
| **Weaviate** | Self-host / cloud | ✅ OSS | GraphQL, modules | Medium |
| **Milvus** | Self-host / cloud | ✅ OSS | Scale (1B+ vectors) | High |
| **pgvector** | Postgres extension | ✅ OSS | ใช้ Postgres อยู่แล้ว | Medium |
| **LanceDB** | Embedded | ✅ OSS | Local-first, like SQLite for vectors | Low |
| **Pinecone** | Cloud only | 🟡 Free 100K vec | Hosted, easy | N/A |

### 3.2 แนะนำให้ใช้

**สำหรับ prototype / dev**: Chroma หรือ LanceDB
- รัน in-process, ไม่ต้อง server
- 5 บรรทัดเริ่ม

**สำหรับ production self-host**: **Qdrant** (อันดับ 1)
- Rust-based, performance ดี
- Hybrid search (dense + sparse) built-in
- Filtering powerful
- Docker container เดียว, deploy ง่าย

**สำหรับงาน Postgres-centric**: pgvector
- ไม่ต้อง infra แยก
- JOIN กับ relational data ได้

**สำหรับ scale 1B+**: Milvus
- ออกแบบมาให้ scale
- ติดตั้ง heavy (Pulsar, etcd, MinIO)

---

## 4. Setup Qdrant Local (5 นาที)

```bash
# 1. Run Qdrant via Docker
docker run -d --name qdrant \
    -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant

# 2. Python client
pip install qdrant-client
```

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(url="http://localhost:6333")

# Create collection (one-time)
client.recreate_collection(
    collection_name="docs",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

# Insert
client.upsert(
    collection_name="docs",
    points=[
        PointStruct(id=1, vector=[0.1, 0.2, ...], payload={"text": "hello"}),
    ],
)

# Search
results = client.search(
    collection_name="docs",
    query_vector=[0.1, 0.2, ...],
    limit=5,
)
```

**Resource ใช้**: ~ 200MB RAM สำหรับ 100K vectors (1536-dim) — รันบน laptop ได้

---

## 5. Embedding Models (เลือกฟรี/ถูก)

### 5.1 Cloud (paid but quality)

| Model | Cost / 1M tokens | Dim | Quality (MTEB avg) |
|---|---|---|---|
| **OpenAI text-embedding-3-large** | $0.13 | 3072 | 64.6 |
| **OpenAI text-embedding-3-small** | $0.02 | 1536 | 62.3 |
| **Voyage voyage-3** | $0.06 | 1024 | 67+ |
| **Cohere embed-v4** | $0.12 | 1024 | 67+ |

### 5.2 Open-source (รันเองฟรี)

| Model | Size | Dim | MTEB | Note |
|---|---|---|---|---|
| **BAAI/bge-large-en-v1.5** | 1.3GB | 1024 | 64.2 | classic strong baseline |
| **BAAI/bge-m3** | 2.3GB | 1024 | 67+ | multilingual + long context |
| **sentence-transformers/all-MiniLM-L6-v2** | 80MB | 384 | 56.3 | tiny, fast |
| **mxbai-embed-large-v1** | 1.3GB | 1024 | 64.6 | strong, OSS |
| **nomic-embed-text-v1.5** | 550MB | 768 | 62.4 | long context (8k) |

### 5.3 Run embedding ผ่าน Ollama (ง่ายสุด)

```bash
ollama pull nomic-embed-text
```

```python
import requests

def embed(text: str) -> list[float]:
    r = requests.post("http://localhost:11434/api/embeddings", json={
        "model": "nomic-embed-text",
        "prompt": text,
    })
    return r.json()["embedding"]
```

หรือ Hugging Face Inference (free tier):
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("BAAI/bge-large-en-v1.5")
emb = model.encode("Hello world")
```

### 5.4 Multilingual (สำคัญสำหรับงานไทย)

ถ้าต้องการ embed ภาษาไทย:
- **bge-m3** — ดีที่สุดใน OSS
- **multilingual-e5-large** — fallback
- **Voyage voyage-multilingual-2** — paid แต่ดี

---

## 6. Chunking Strategy

ก่อน embed → ต้อง chunk text ให้พอดีกับ context

### 6.1 Strategies

#### A. Fixed-size (simplest)
```python
def fixed_chunk(text, size=500, overlap=50):
    return [text[i:i+size] for i in range(0, len(text), size-overlap)]
```
- ✅ Simple
- ❌ Cut คำกลาง / ความหมายแตก

#### B. Recursive (LangChain default)
แตกตาม separator hierarchy: `\n\n` → `\n` → `.` → ` `
- ✅ ฉลาดขึ้น
- ❌ ยังไม่ understand semantic

#### C. Semantic chunking
ใช้ embedding similarity → chunk ตรงที่ topic เปลี่ยน
- ✅ คุณภาพดีกว่า
- ❌ ช้ากว่า, complex

#### D. Document-aware
- Markdown: chunk ตาม heading
- Code: chunk ตาม function/class
- HTML: chunk ตาม section

#### E. Late chunking (2024+)
- Embed ทั้ง doc → pool ตาม chunk boundary
- ดีกว่ามาก context-wise
- ต้องใช้ embedding model ที่ context ยาว

### 6.2 ขนาด Chunk ที่แนะนำ

```
- Q&A retrieval:  256-512 tokens (precise)
- Summarization: 1024-2048 tokens (more context)
- Code search:   per function/class
- Long docs:     hierarchical (section → para → sentence)
```

### 6.3 Overlap

```
ปกติ overlap 10-20% ของ chunk size
chunk=512, overlap=50-100 ก็พอ
```

### 6.4 Metadata

ใส่ metadata กับ chunk เสมอ — agent ใช้ filter / cite ได้
```python
{
    "text": "...",
    "source": "policy_2024.pdf",
    "page": 12,
    "section": "Refund Policy",
    "date": "2024-06",
    "author": "Legal Dept",
}
```

---

## 7. Hybrid Search (Dense + Sparse)

Vector search อย่างเดียวไม่พอ — keyword matching สำคัญด้วย

```
Query: "annual report 2024"
Dense search: หา doc ที่ "พูดคล้ายๆ"
Sparse search (BM25): หา doc ที่มีคำว่า "annual report 2024" จริง
Hybrid: รวม 2 score
```

### Implementation

#### Option 1: Qdrant native hybrid
```python
client.query_points(
    collection_name="docs",
    prefetch=[
        Prefetch(query=dense_vec, using="dense", limit=20),
        Prefetch(query=sparse_vec, using="sparse", limit=20),
    ],
    query=FusionQuery(fusion=Fusion.RRF),  # reciprocal rank fusion
)
```

#### Option 2: Manual reranking
```python
dense = qdrant.search(...)
sparse = bm25.search(...)  # via rank_bm25 or Elasticsearch
combined = rrf_merge(dense, sparse)  # reciprocal rank fusion
final = reranker.rerank(query, combined)  # optional cross-encoder
```

### Reranker

หลัง retrieve → rerank ด้วย cross-encoder (precision สูงกว่า)

| Model | Free? | Note |
|---|---|---|
| **bge-reranker-v2-m3** | ✅ OSS | best OSS reranker |
| **Cohere Rerank v3** | $$ | strong |
| **Voyage rerank-2** | $$ | strong |

---

## 8. Episodic Memory — จำ Session

ถ้า agent ต้องจำ user ข้ามวัน:

### 8.1 Pattern: Conversation Summary
```python
def maybe_summarize(messages):
    if len(messages) > 20:
        summary = llm("Summarize this conversation: " + str(messages[:-10]))
        return [{"role": "system", "content": f"Earlier: {summary}"}] + messages[-10:]
    return messages
```

### 8.2 Pattern: Vector Memory
- Embed ทุก message (หรือทุก turn)
- เวลา query → retrieve relevant past messages
- ใส่ใน context

### 8.3 Pattern: Profile Extraction (Mem0-style)

```
ทุกครั้งหลัง conversation:
  LLM: "extract facts about user from this conversation"
       → ["user prefers Python", "user works at startup", ...]
  Save to user_profile collection
  
เวลา user มาใหม่:
  Load relevant profile facts → ใส่ system prompt
```

**Tools**: [Mem0](https://github.com/mem0ai/mem0) — open source memory layer

```python
from mem0 import MemoryClient

m = MemoryClient(api_key="...")
m.add("User likes Thai food", user_id="alice")
m.add("Allergic to peanuts", user_id="alice")

results = m.search("food preferences", user_id="alice")
```

### 8.4 Pattern: LangGraph Checkpointer

LangGraph มี checkpoint built-in → state ของ agent เก็บใน DB อัตโนมัติ

```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string("postgres://...")
app = graph.compile(checkpointer=checkpointer)

# Resume conversation
config = {"configurable": {"thread_id": "user_alice_session_1"}}
app.invoke({"messages": [...]}, config=config)
```

---

## 9. Knowledge Graph (Optional, Advanced)

Vector DB ดีสำหรับ "similar" — ไม่ดีสำหรับ "structured relation"

ตัวอย่าง: "ใครเป็น manager ของ alice ที่ทำงาน project X?"
- Vector: ตอบไม่ได้ — relation specific
- Graph: query ได้ตรงๆ

### Tools
- **Neo4j** — แม่บท graph DB
- **Memgraph** — Cypher-compatible, faster
- **Apache AGE** — Postgres extension
- **Kuzu** — embedded graph DB

### GraphRAG (Microsoft)
- Build knowledge graph จาก unstructured docs
- Query LLM ผ่าน graph + community summary
- ดีกว่า vanilla RAG ในงาน complex
- Cost สูงในการ index

แนะนำ: ใช้ vanilla RAG ก่อน, ขยับไป GraphRAG ถ้าต้องการ multi-hop reasoning

---

## 10. Memory Architecture สำหรับ Agent System ของคุณ

จาก use case ที่บอก (e-commerce builder + multi-agent + vector DB on Docker):

```
┌──────────────────────────────────────────────────────┐
│   USER REQUEST: "build e-commerce site"              │
└────────────────────┬─────────────────────────────────┘
                     ▼
        ┌──────────────────────────┐
        │  COORDINATOR AGENT       │
        └──────────┬───────────────┘
                   │ reads/writes
                   ▼
        ┌──────────────────────────────────────┐
        │  SHARED MEMORY (this project)        │
        ├──────────────────────────────────────┤
        │  workspace/                          │
        │   ├─ requirements.md                 │
        │   ├─ architecture.md                 │
        │   ├─ db_schema.sql                   │
        │   ├─ api_spec.yaml                   │
        │   └─ ...                             │
        │                                      │
        │  + Qdrant collection per project     │
        │   (chunks of all artifacts)          │
        └──────────────────────────────────────┘
                   ▲
                   │ specialists read context
        ┌──────────┴──────────┐
        ▼                     ▼
   ┌─────────┐           ┌─────────┐
   │Architect│           │ DBA     │
   └─────────┘           └─────────┘

┌──────────────────────────────────────────────────────┐
│   GLOBAL KNOWLEDGE (across all projects)             │
├──────────────────────────────────────────────────────┤
│  Qdrant collection: "patterns"                       │
│  - Architecture patterns                             │
│  - Common DB schemas                                 │
│  - API design patterns                               │
│  - Past project lessons                              │
└──────────────────────────────────────────────────────┘
```

### Levels:
1. **Working memory**: Each agent's context (transient)
2. **Shared project memory**: Files in `workspace/` — version control via git
3. **Project KB**: Qdrant collection — searchable artifacts of current project
4. **Global KB**: Qdrant collection — patterns / past projects

### Why this design?
- **File-based artifacts** — readable by humans, git-able, debuggable
- **Vector search on top** — agents query semantic
- **Separation per project** — isolation
- **Global KB** — learning across projects

---

## 11. Checklist — Memory ของ Agent

- [ ] Working memory: รู้ว่า context limit เท่าไหร่ + strategy เมื่อเกิน
- [ ] Episodic memory: เก็บ conversation history (DB?)
- [ ] Semantic memory: vector DB setup, embedding model เลือกแล้ว
- [ ] Chunking strategy ตาม doc type
- [ ] Metadata schema ครบ
- [ ] Hybrid search ถ้า keyword สำคัญ
- [ ] Reranker ถ้าต้องการ precision
- [ ] Memory write/read protocol ชัดเจน (ใครเขียนเมื่อไหร่)
- [ ] Privacy/ACL: user A เห็น memory user A เท่านั้น
- [ ] Backup/retention policy

---

## 12. Common Mistakes

### ❌ Embed ทุก doc ด้วย model เดียว
ภาษา / domain ต่าง → คุณภาพต่าง — ใช้ multilingual model ถ้ามีหลายภาษา

### ❌ Chunk ด้วย size ตายตัว ไม่สน document type
PDF / code / markdown ต้องคนละ strategy

### ❌ ไม่มี metadata
Filter ไม่ได้, cite ไม่ได้, debug ไม่ได้

### ❌ "Just embed everything"
ขยะเข้า → ขยะออก เลือก doc ที่จะ embed ก่อน

### ❌ ไม่มี reranker
Vector search อย่างเดียว recall สูงแต่ precision ต่ำ — reranker ช่วยมาก

### ❌ Memory infinite growth
ตั้ง retention policy: 30 วัน / 90 วัน + auto-summarize

---

## สรุป

- 3 ชั้น memory: working, episodic, semantic
- Vector DB ฟรี: **Qdrant** (production) / **Chroma** (prototype)
- Embedding ฟรี: **bge-m3** (multilingual) / **nomic-embed-text** (Ollama)
- Chunking: ขึ้นกับ doc type, มี overlap, มี metadata
- Hybrid search (dense + sparse) ดีกว่า dense only
- Reranker เพิ่ม precision คุ้มค่า
- Knowledge graph เมื่อต้องการ relation จริงๆ
- Memory architecture สำหรับ multi-agent: shared workspace + per-project KB + global KB

**ต่อไป** → [06 Production, Cost, Observability](06_Production_Cost_Observability.md)

---

## References

- [Qdrant docs](https://qdrant.tech/documentation/)
- [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard) — embedding benchmark
- [Mem0](https://github.com/mem0ai/mem0) — agent memory layer
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag)
- [LangChain RAG cookbook](https://python.langchain.com/docs/tutorials/rag/)
