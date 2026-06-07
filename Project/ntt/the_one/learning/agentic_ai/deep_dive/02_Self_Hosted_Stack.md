# Deep Dive 02 — Self-Hosted Stack

> Docker Compose ครบ stack: Ollama + Qdrant + Postgres + Langfuse + n8n + LangGraph
> รันบน laptop ($0) หรือ VPS ($5-20/mo)

---

## 1. Big Picture

```
┌──────────────────────────────────────────────────────────────┐
│                     YOUR APP / AGENT                         │
│              (LangGraph / Python / Node)                     │
└─────┬────────────┬────────────┬────────────┬────────────────┘
      │            │            │            │
      ▼            ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  Ollama  │ │  Qdrant  │ │ Postgres │ │ Langfuse │
│ (LLM)    │ │ (Vector) │ │ (State)  │ │ (Observ) │
│ :11434   │ │ :6333    │ │ :5432    │ │ :3000    │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
                   ▲                        ▲
      ┌────────────┘                        │
      │                                     │
┌─────────┐                          ┌──────────┐
│  n8n    │                          │  Redis   │
│ (autom) │                          │ (queue)  │
│ :5678   │                          │ :6379    │
└─────────┘                          └──────────┘
```

ทุกตัว free + open source

---

## 2. Hardware ที่ต้องการ

### Minimal (laptop dev)
- 16GB RAM (8GB dedicated to Docker)
- 50GB free disk
- Modern CPU
- ⚠️ Ollama big model จะช้าถ้าไม่มี GPU

### Recommended (small VPS)
- 32GB RAM
- 200GB SSD
- 8 vCPU
- ตัวอย่าง: Hetzner CPX31 (~ €15/mo) หรือ Contabo VPS L (~ $13/mo)

### Production (with GPU for local LLM)
- 64GB RAM
- 500GB SSD
- 1× RTX 3090 / 4090 (24GB VRAM)
- Hetzner GEX44 (~ €185/mo) หรือ self-hosted

---

## 3. Docker Compose ทั้งระบบ

### 3.1 Setup

```bash
mkdir agent-stack && cd agent-stack
mkdir -p data/{qdrant,postgres,ollama,langfuse,n8n,redis}
touch .env docker-compose.yml
```

### 3.2 `.env`

```bash
# Postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme
POSTGRES_DB=app

# Langfuse
LANGFUSE_DB_NAME=langfuse
LANGFUSE_SECRET=$(openssl rand -hex 32)
NEXTAUTH_SECRET=$(openssl rand -hex 32)
SALT=$(openssl rand -hex 32)
NEXTAUTH_URL=http://localhost:3000

# n8n
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=changeme
N8N_HOST=localhost
N8N_PORT=5678
N8N_PROTOCOL=http

# Your LLM API keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
GROQ_API_KEY=gsk_...
```

### 3.3 `docker-compose.yml`

```yaml
version: "3.9"

x-restart: &restart
  restart: unless-stopped

services:
  # ============================================
  # LLM (local)
  # ============================================
  ollama:
    <<: *restart
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes:
      - ./data/ollama:/root/.ollama
    # ถ้ามี GPU NVIDIA:
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]

  # ============================================
  # Vector DB
  # ============================================
  qdrant:
    <<: *restart
    image: qdrant/qdrant:latest
    ports: ["6333:6333", "6334:6334"]
    volumes:
      - ./data/qdrant:/qdrant/storage

  # ============================================
  # Postgres (shared by Langfuse, app state, n8n)
  # ============================================
  postgres:
    <<: *restart
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
      - ./init/postgres-init.sql:/docker-entrypoint-initdb.d/init.sql
    ports: ["5432:5432"]

  # ============================================
  # Cache / Queue
  # ============================================
  redis:
    <<: *restart
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes:
      - ./data/redis:/data

  # ============================================
  # Observability
  # ============================================
  langfuse-clickhouse:
    <<: *restart
    image: clickhouse/clickhouse-server:24
    volumes:
      - ./data/langfuse-ch:/var/lib/clickhouse
    environment:
      CLICKHOUSE_DB: default
      CLICKHOUSE_USER: clickhouse
      CLICKHOUSE_PASSWORD: clickhouse

  langfuse:
    <<: *restart
    image: langfuse/langfuse:3
    depends_on: [postgres, redis, langfuse-clickhouse]
    ports: ["3000:3000"]
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${LANGFUSE_DB_NAME}
      NEXTAUTH_URL: ${NEXTAUTH_URL}
      NEXTAUTH_SECRET: ${NEXTAUTH_SECRET}
      SALT: ${SALT}
      ENCRYPTION_KEY: ${LANGFUSE_SECRET}
      CLICKHOUSE_URL: http://langfuse-clickhouse:8123
      CLICKHOUSE_USER: clickhouse
      CLICKHOUSE_PASSWORD: clickhouse
      REDIS_HOST: redis
      REDIS_PORT: 6379
      TELEMETRY_ENABLED: "false"

  # ============================================
  # Workflow / automation
  # ============================================
  n8n:
    <<: *restart
    image: n8nio/n8n:latest
    ports: ["5678:5678"]
    environment:
      N8N_BASIC_AUTH_ACTIVE: "true"
      N8N_BASIC_AUTH_USER: ${N8N_BASIC_AUTH_USER}
      N8N_BASIC_AUTH_PASSWORD: ${N8N_BASIC_AUTH_PASSWORD}
      DB_TYPE: postgresdb
      DB_POSTGRESDB_HOST: postgres
      DB_POSTGRESDB_DATABASE: n8n
      DB_POSTGRESDB_USER: ${POSTGRES_USER}
      DB_POSTGRESDB_PASSWORD: ${POSTGRES_PASSWORD}
      N8N_HOST: ${N8N_HOST}
      N8N_PORT: ${N8N_PORT}
      N8N_PROTOCOL: ${N8N_PROTOCOL}
    volumes:
      - ./data/n8n:/home/node/.n8n
    depends_on: [postgres]

  # ============================================
  # Your agent service
  # ============================================
  agent:
    <<: *restart
    build: ./agent
    ports: ["8000:8000"]
    env_file: .env
    environment:
      OLLAMA_BASE_URL: http://ollama:11434
      QDRANT_URL: http://qdrant:6333
      POSTGRES_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://redis:6379
      LANGFUSE_HOST: http://langfuse:3000
      LANGFUSE_PUBLIC_KEY: ${LANGFUSE_PUBLIC_KEY}
      LANGFUSE_SECRET_KEY: ${LANGFUSE_SECRET_KEY}
    depends_on: [ollama, qdrant, postgres, redis, langfuse]
```

### 3.4 `init/postgres-init.sql`

```sql
-- Create separate DBs for different services
CREATE DATABASE langfuse;
CREATE DATABASE n8n;
CREATE DATABASE app;

-- Enable pgvector for app DB
\c app
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3.5 Boot

```bash
docker compose up -d
docker compose ps  # ดู status

# Pull Ollama models
docker compose exec ollama ollama pull llama3.3
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec ollama ollama pull qwen2.5:7b
```

### 3.6 First-time setup

1. **Langfuse**: เปิด `http://localhost:3000` → create org → create project → get API keys → ใส่ `.env`
2. **n8n**: `http://localhost:5678` → login → create workflows
3. **Qdrant**: `http://localhost:6333/dashboard`

---

## 4. Ollama — Local LLM Setup

### 4.1 Models ที่แนะนำ

| Use case | Model | RAM | Note |
|---|---|---|---|
| General | `llama3.3` (70B) | 40GB | best OSS quality |
| Lightweight | `llama3.2:3b` | 4GB | fast on laptop |
| Code | `qwen2.5-coder:7b` | 8GB | code-focused |
| Embedding | `nomic-embed-text` | 1GB | 768 dim, English |
| Multilingual emb | `bge-m3` | 2GB | 1024 dim, ไทย ดี |
| Vision | `llava:13b` | 13GB | image understanding |

```bash
ollama pull llama3.3
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text
ollama pull bge-m3

ollama list  # ดูที่มี
```

### 4.2 Quick test

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.3",
  "prompt": "Say hi in Thai"
}'
```

### 4.3 OpenAI-compatible API

Ollama expose endpoint แบบ OpenAI:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # ignored
)

resp = client.chat.completions.create(
    model="llama3.3",
    messages=[{"role": "user", "content": "Hello"}],
)
```

ใช้กับ LangChain/LangGraph ได้เลย:
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(base_url="http://localhost:11434/v1", model="llama3.3", api_key="ollama")
```

### 4.4 Tool use (function calling) ที่ Ollama

Ollama รองรับ tool use ผ่าน Llama 3.1+, Qwen 2.5+:

```python
client.chat.completions.create(
    model="llama3.3",
    messages=[...],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "...",
            "parameters": {...}
        }
    }],
)
```

### 4.5 GPU acceleration

```bash
# Verify GPU
docker compose exec ollama ollama run llama3.3 "hi"
# Check log → "using GPU" message

# nvidia-smi inside container
docker compose exec ollama nvidia-smi
```

ถ้าไม่มี GPU → CPU inference ก็ได้ แต่ช้า (5-15 tok/s vs 50-100+ on GPU)

---

## 5. Alternative: vLLM (production-grade local)

ถ้ามี GPU จริงจังและจะ scale → **vLLM** ดีกว่า Ollama:
- Higher throughput (batching)
- OpenAI-compatible API
- Production tuning options

```yaml
# docker-compose.override.yml
services:
  vllm:
    image: vllm/vllm-openai:latest
    ports: ["8001:8000"]
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    command: --model meta-llama/Llama-3.3-70B-Instruct --max-model-len 8192
    volumes:
      - ~/.cache/huggingface:/root/.cache/huggingface
```

แต่ต้องการ GPU ที่ VRAM ใหญ่พอ (24GB+ for 70B in fp16, less for quantized)

---

## 6. Qdrant — Practical Usage

### 6.1 Basic Python client

```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
)

client = QdrantClient(url="http://localhost:6333")

# Create collection
client.recreate_collection(
    collection_name="docs",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
)

# Index
def index_doc(text, doc_id, metadata):
    embedding = embed(text)  # via Ollama
    client.upsert(
        collection_name="docs",
        points=[PointStruct(id=doc_id, vector=embedding, payload={
            "text": text,
            **metadata,
        })]
    )

# Search with filter
results = client.search(
    collection_name="docs",
    query_vector=embed(query),
    query_filter=Filter(must=[
        FieldCondition(key="dept", match=MatchValue(value="engineering"))
    ]),
    limit=5,
)
```

### 6.2 Hybrid (dense + sparse)

```python
from qdrant_client.models import SparseVectorParams, NamedVector, NamedSparseVector

client.recreate_collection(
    collection_name="docs",
    vectors_config={
        "dense": VectorParams(size=768, distance=Distance.COSINE),
    },
    sparse_vectors_config={
        "sparse": SparseVectorParams()
    }
)

# Need sparse encoder e.g. BM25 / SPLADE
# ดู Qdrant docs สำหรับ FastEmbed integration
```

### 6.3 Snapshots (backup)

```bash
# Create snapshot
curl -X POST http://localhost:6333/collections/docs/snapshots

# List
curl http://localhost:6333/collections/docs/snapshots

# Download (then save somewhere safe)
curl -o backup.snapshot http://localhost:6333/collections/docs/snapshots/<name>
```

---

## 7. LangGraph + Local Stack

### 7.1 Wire ทุกตัวใน 1 agent

```python
# agent/main.py
import os
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_openai import ChatOpenAI
from langfuse.callback import CallbackHandler

# LLM via Ollama
ollama_llm = ChatOpenAI(
    base_url=os.environ["OLLAMA_BASE_URL"] + "/v1",
    api_key="ollama",
    model="llama3.3",
)

# Or premium
from langchain_anthropic import ChatAnthropic
claude = ChatAnthropic(model="claude-haiku-4-5-20251001")

# Observability
langfuse_handler = CallbackHandler(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    host=os.environ["LANGFUSE_HOST"],
)

# Vector DB
from qdrant_client import QdrantClient
qdrant = QdrantClient(url=os.environ["QDRANT_URL"])

# State checkpoint
saver = PostgresSaver.from_conn_string(os.environ["POSTGRES_URL"])

# Graph
def search_kb(state):
    results = qdrant.search(
        collection_name="docs",
        query_vector=embed(state["query"]),
        limit=5,
    )
    return {"docs": [r.payload["text"] for r in results]}

def answer(state):
    resp = claude.invoke(f"Q: {state['query']}\nDocs: {state['docs']}")
    return {"answer": resp.content}

g = StateGraph(...)  # standard
g.add_node("search", search_kb)
g.add_node("answer", answer)
# ...

app = g.compile(checkpointer=saver)

# Run with tracing
result = app.invoke(
    {"query": "..."},
    config={"callbacks": [langfuse_handler], "configurable": {"thread_id": "session-1"}},
)
```

### 7.2 Dockerfile สำหรับ agent

```dockerfile
# agent/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir uv && uv pip install --system -e .
COPY . .
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 8. Embedding via Ollama (saving cost)

```python
import requests

def embed(text: str) -> list[float]:
    r = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text},
        timeout=10,
    )
    return r.json()["embedding"]

# Batch
def embed_batch(texts: list[str]) -> list[list[float]]:
    return [embed(t) for t in texts]
```

หรือใช้ FastEmbed (faster, runs in-process):
```python
from fastembed import TextEmbedding
model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
embeddings = list(model.embed(["hello", "world"]))
```

---

## 9. Production Deployment

### 9.1 Reverse proxy (Caddy)

```yaml
services:
  caddy:
    image: caddy:2
    ports: ["80:80", "443:443"]
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - ./caddy_data:/data
```

`Caddyfile`:
```
agent.yourdomain.com {
    reverse_proxy agent:8000
}
n8n.yourdomain.com {
    reverse_proxy n8n:5678
    basic_auth {
        admin <hash>
    }
}
langfuse.yourdomain.com {
    reverse_proxy langfuse:3000
}
```

Caddy auto-provisions Let's Encrypt SSL — ฟรี

### 9.2 Backups

```bash
# Daily Postgres dump
0 3 * * * docker compose exec -T postgres pg_dumpall -U postgres | gzip > /backups/pg-$(date +\%F).sql.gz

# Qdrant snapshots
0 4 * * * curl -X POST http://localhost:6333/collections/docs/snapshots
```

ส่งไป S3 / Backblaze B2 / Wasabi

### 9.3 Resource limits

```yaml
services:
  ollama:
    deploy:
      resources:
        limits:
          memory: 16G
        reservations:
          memory: 8G
```

### 9.4 Health checks

```yaml
services:
  qdrant:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 30s
      timeout: 5s
      retries: 3
```

---

## 10. Monitoring

### 10.1 Prometheus + Grafana

```yaml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports: ["3001:3000"]
```

Qdrant + Postgres + Langfuse exporters all available

### 10.2 Logs aggregation

```yaml
services:
  loki:
    image: grafana/loki
  promtail:
    image: grafana/promtail
    volumes:
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
```

---

## 11. Cost Estimates

### Self-host on Hetzner CPX31 (8 vCPU, 16GB, 240GB)
- ~ €15/mo = ~ $16/mo
- เพียงพอสำหรับ:
  - Qdrant 1M vectors
  - Postgres สำหรับ Langfuse + n8n + app
  - Llama 3.2 3B (CPU only — slow)
  - 100-1000 agent runs/day

### Self-host on Hetzner GEX44 (with GPU)
- ~ €185/mo = ~ $200/mo  
- เพียงพอสำหรับ:
  - Llama 3.3 70B local
  - 10K+ agent runs/day
  - Embedding local

### Compare to cloud
- Pinecone: $70+/mo (vector DB only)
- Anthropic API only: depends — แต่ 100K runs × Sonnet ≈ $300+/mo
- Self-host = save ~ 60-80% ที่ scale

---

## 12. Common Pitfalls

### Postgres ผิด password ตอนตั้ง
- DB folder ถูก initialize แล้วใช้ password เดิม → เปลี่ยน env ไม่ work
- แก้: `docker compose down -v` (ลบ volume) → start ใหม่

### Ollama OOM
- Model ใหญ่กว่า RAM → OOM kill
- แก้: ใช้ quantized version (`llama3.3:70b-instruct-q4_K_M`)

### Qdrant collection schema mismatch
- Embedding dim เปลี่ยน (768 → 1024) → upsert error
- แก้: recreate collection หรือ create แยก

### n8n webhook ไม่ถึง
- ใน Docker network → external URL ต่างจาก internal
- Set `WEBHOOK_URL` env var

### Langfuse trace ไม่ขึ้น
- API key สลับ public ↔ secret
- หรือ host URL ใส่ผิด (must be reachable from agent container)

---

## 13. Backup & Disaster Recovery

```bash
# 1. Full backup script
#!/bin/bash
TIMESTAMP=$(date +%F-%H%M)
mkdir -p /backups/$TIMESTAMP

# Postgres
docker compose exec -T postgres pg_dumpall -U postgres | gzip > /backups/$TIMESTAMP/pg.sql.gz

# Qdrant snapshots
for COL in docs patterns episodes; do
    curl -X POST http://localhost:6333/collections/$COL/snapshots
done
# รอแล้ว download
sleep 5
for COL in docs patterns episodes; do
    LATEST=$(curl -s http://localhost:6333/collections/$COL/snapshots | jq -r '.result | last | .name')
    curl -o /backups/$TIMESTAMP/${COL}.snapshot \
        http://localhost:6333/collections/$COL/snapshots/$LATEST
done

# Volume backup
tar czf /backups/$TIMESTAMP/n8n.tar.gz ./data/n8n
tar czf /backups/$TIMESTAMP/ollama.tar.gz ./data/ollama

# Sync to remote
rclone copy /backups/$TIMESTAMP remote:backups/
```

---

## 14. สรุป — สั่งใน 5 นาที

```bash
git clone https://github.com/<your-template>/agent-stack
cd agent-stack
cp .env.example .env
# edit .env

docker compose up -d
docker compose exec ollama ollama pull llama3.3
docker compose exec ollama ollama pull nomic-embed-text

# Open
echo "Langfuse: http://localhost:3000"
echo "n8n: http://localhost:5678"
echo "Qdrant: http://localhost:6333/dashboard"
echo "Agent: http://localhost:8000"
```

---

## References

- [Ollama docs](https://github.com/ollama/ollama)
- [Qdrant Docker setup](https://qdrant.tech/documentation/quickstart/)
- [Langfuse self-host](https://langfuse.com/docs/deployment/self-host)
- [n8n Docker](https://docs.n8n.io/hosting/installation/docker/)
- [Hetzner Cloud](https://www.hetzner.com/cloud)
