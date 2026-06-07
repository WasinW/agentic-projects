# 10 — Local Agent Blueprint

> **One prescriptive design** สำหรับ "ทำ agent บน laptop + Docker stack + ฟรี/ถูก"
> ไม่มีตัวเลือก — มีแค่คำตอบเดียว ที่ผ่านการคิดให้แล้ว
> ตั้งใจว่า: clone → docker compose up → คุยกับ agent ใน 30 นาที

---

## ใครควรอ่านไฟล์นี้

- ✅ คุณอยากเริ่ม build agent **ตอนนี้** บน laptop
- ✅ ไม่อยาก compare 5 frameworks อีกแล้ว — แค่อยาก start
- ✅ ใช้ Docker เป็น
- ✅ เขียน Python ได้

ถ้ายังไม่เคยอ่าน [01](01_Agentic_AI_Fundamentals.md), [02](02_Design_Patterns.md) — แนะนำอ่านก่อน
ถ้าจะ shop framework ต่างๆ → [03](03_Frameworks_Comparison.md)
ไฟล์นี้จะ **ไม่อธิบายซ้ำ** ทำไมเลือกแต่ละอย่าง — บอกแค่ "เลือกอันนี้"

---

## 1. Final Architecture (ไม่ต้องคิดต่อ)

```
┌─────────────────────────────────────────────────────────────┐
│  YOUR LAPTOP / VPS                                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  agent (FastAPI + LangGraph)        :8000              │  │
│  │  - HTTP + chat endpoint                                │  │
│  │  - LangGraph state machine                             │  │
│  │  - Tool registry (in-process + MCP)                    │  │
│  └────────┬──────────────────┬──────────┬──────────┬─────┘  │
│           │                  │          │          │        │
│           ▼                  ▼          ▼          ▼        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────┐  ┌────────┐   │
│  │  qdrant      │  │  postgres    │  │redis │  │langfuse│   │
│  │  :6333       │  │  :5432       │  │ :6379│  │ :3000  │   │
│  │  (vector)    │  │ (state +     │  │(cache│  │(traces)│   │
│  │              │  │  langfuse +  │  │ +msg)│  │        │   │
│  │              │  │  app data)   │  │      │  │        │   │
│  └──────────────┘  └──────────────┘  └──────┘  └────────┘   │
│           ▲                                                  │
│           │ embed                                            │
│  ┌────────┴───────┐                                          │
│  │  ollama        │  :11434                                  │
│  │  (embed +      │  - nomic-embed-text                      │
│  │   small LLM)   │  - llama3.3:3b (fallback)                │
│  └────────────────┘                                          │
│                                                              │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   │ (cloud LLM call when needed)
                   ▼
            ┌──────────────┐
            │  Anthropic   │  Sonnet (planner)
            │  (or Gemini) │  Haiku (workers)
            └──────────────┘
```

### Components — ทำหน้าที่อะไร

| Component | Role | Why this one |
|---|---|---|
| **agent** (your code) | FastAPI + LangGraph orchestrator | 1 service, easy to debug |
| **qdrant** | Vector DB (Docker) | Production-ready, hybrid search, easy ops |
| **postgres** | App state + Langfuse + LangGraph checkpoint | 1 DB serves 3 purposes — less infra |
| **redis** | Cache (semantic, prompt) + queue | Fast, well-known |
| **ollama** | Local embedding + fallback LLM | No API key needed for embed |
| **langfuse** | Observability (traces, cost, evals) | OSS, drop-in via SDK |
| **Anthropic/Gemini** | "Smart" LLM for planning | Cloud — cheap APIs ดีกว่า self-host 70B |

---

## 2. Stack Decision Log (ถ้าสงสัย "ทำไมไม่ใช่ X")

| Choice | Alternatives ที่ตัดออก | Reason ตัด |
|---|---|---|
| LangGraph | CrewAI, AutoGen, n8n | Production state machine; case study (07) ใช้ pattern นี้ |
| Qdrant | Chroma, Weaviate, pgvector | Dev-prod single tool; hybrid built-in |
| Postgres (1 DB) | แยก DB per service | KISS — laptop pool of 1 |
| Anthropic + Ollama hybrid | All-Anthropic, all-local | Embed local (free) + Sonnet for hard tasks (cheap) |
| Langfuse | LangSmith, custom | OSS = data ไม่ออก laptop |
| FastAPI | Flask, raw Python | Async + auto-docs |

**ห้ามถามต่อ**: ถ้าใช้ blueprint นี้ + ติดอย่างเดียว → fix ปัญหา ไม่เปลี่ยน stack

---

## 3. Repo Layout

```
my-agent/
├── docker-compose.yml         # full stack
├── .env.example
├── Makefile                   # short commands
├── pyproject.toml             # uv-managed
│
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI entry
│   ├── api/
│   │   ├── chat.py            # POST /chat
│   │   ├── runs.py            # GET /runs/<id>, resume
│   │   └── health.py
│   │
│   ├── agents/
│   │   ├── coordinator.py     # LangGraph compiled
│   │   ├── nodes/
│   │   │   ├── analyst.py
│   │   │   ├── architect.py
│   │   │   ├── designer.py
│   │   │   └── reviewer.py
│   │   └── state.py           # TypedDict
│   │
│   ├── tools/
│   │   ├── kb.py              # search_kb (Qdrant)
│   │   ├── files.py           # read/write workspace
│   │   ├── http.py            # generic HTTP
│   │   └── registry.py        # tool registry + schemas
│   │
│   ├── memory/
│   │   ├── qdrant_client.py
│   │   ├── postgres.py        # async pool
│   │   └── workspace.py       # file artifacts
│   │
│   ├── llm/
│   │   ├── factory.py         # routing: Sonnet vs Haiku vs Ollama
│   │   ├── budget.py          # cost cap
│   │   └── cache.py           # semantic cache
│   │
│   └── observability/
│       └── langfuse.py        # init + handlers
│
├── kb_seed/                   # initial vector DB content
│   └── patterns/
│       └── arch_patterns.md
│
├── workspaces/                # per-run artifacts (git-ignored)
│   └── .gitkeep
│
├── scripts/
│   ├── bootstrap.sh           # init DB, pull models
│   ├── seed_kb.py             # populate Qdrant from kb_seed/
│   └── eval.py                # run promptfoo
│
└── tests/
    ├── test_agents.py
    └── eval/
        └── promptfoo.yaml
```

---

## 4. docker-compose.yml (ทั้งระบบ)

```yaml
# docker-compose.yml
services:
  agent:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    environment:
      QDRANT_URL: http://qdrant:6333
      POSTGRES_URL: postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/agent
      OLLAMA_URL: http://ollama:11434
      REDIS_URL: redis://redis:6379
      LANGFUSE_HOST: http://langfuse:3000
    depends_on: [qdrant, postgres, redis, ollama, langfuse]
    volumes:
      - ./workspaces:/app/workspaces
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333"]
    volumes: ["qdrant_data:/qdrant/storage"]
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: agent
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/postgres-init.sql:/docker-entrypoint-initdb.d/init.sql
    ports: ["5432:5432"]
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes: ["redis_data:/data"]
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes: ["ollama_data:/root/.ollama"]
    # ถ้ามี GPU NVIDIA, uncomment:
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - {driver: nvidia, count: 1, capabilities: [gpu]}
    restart: unless-stopped

  langfuse:
    image: langfuse/langfuse:3
    ports: ["3000:3000"]
    depends_on: [postgres]
    environment:
      DATABASE_URL: postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/langfuse
      NEXTAUTH_URL: http://localhost:3000
      NEXTAUTH_SECRET: ${LANGFUSE_SECRET}
      SALT: ${LANGFUSE_SALT}
      ENCRYPTION_KEY: ${LANGFUSE_ENCRYPTION_KEY}
      TELEMETRY_ENABLED: "false"
    restart: unless-stopped

volumes:
  qdrant_data:
  postgres_data:
  redis_data:
  ollama_data:
```

`scripts/postgres-init.sql`:
```sql
CREATE DATABASE langfuse;
\c agent
CREATE EXTENSION IF NOT EXISTS vector;
```

`.env.example`:
```bash
# Postgres
POSTGRES_PASSWORD=changeme

# LLM APIs
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...

# Langfuse (generate via: openssl rand -hex 32)
LANGFUSE_SECRET=
LANGFUSE_SALT=
LANGFUSE_ENCRYPTION_KEY=
LANGFUSE_PUBLIC_KEY=     # set after first Langfuse setup
LANGFUSE_SECRET_KEY=     # set after first Langfuse setup

# Budget
MAX_COST_PER_REQUEST_USD=0.50
MAX_STEPS_PER_AGENT=15
```

---

## 5. Python Project Setup

`pyproject.toml`:
```toml
[project]
name = "my-agent"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
    "langgraph>=0.2",
    "langchain-anthropic>=0.2",
    "langchain-google-genai>=2",
    "anthropic>=0.40",
    "qdrant-client>=1.12",
    "asyncpg>=0.30",
    "redis>=5",
    "httpx>=0.27",
    "pydantic>=2",
    "pydantic-settings>=2",
    "langfuse>=2.50",
    "python-dotenv>=1",
]

[tool.uv]
package = false

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

`Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock* ./
RUN uv pip install --system --no-cache .
COPY app/ ./app/
COPY scripts/ ./scripts/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`Makefile`:
```makefile
.PHONY: up down logs bootstrap seed shell test eval

up:
	docker compose up -d
	@echo "Stack starting at:"
	@echo "  Agent:    http://localhost:8000"
	@echo "  Langfuse: http://localhost:3000"
	@echo "  Qdrant:   http://localhost:6333/dashboard"

down:
	docker compose down

logs:
	docker compose logs -f agent

bootstrap:
	docker compose exec ollama ollama pull nomic-embed-text
	docker compose exec ollama ollama pull llama3.2:3b
	docker compose exec agent python scripts/seed_kb.py
	@echo "Bootstrap complete. Open http://localhost:3000 to set up Langfuse."

seed:
	docker compose exec agent python scripts/seed_kb.py

shell:
	docker compose exec agent bash

test:
	docker compose exec agent pytest tests/

eval:
	docker compose exec agent python scripts/eval.py
```

---

## 6. Code Skeleton — เพียงพอที่จะรันได้

### 6.1 `app/main.py`

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import chat, runs, health
from app.memory.postgres import init_pool
from app.memory.qdrant_client import init_qdrant
from app.observability.langfuse import init_langfuse

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool()
    init_qdrant()
    init_langfuse()
    yield

app = FastAPI(title="my-agent", lifespan=lifespan)
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(runs.router)
```

### 6.2 `app/agents/state.py`

```python
from typing import TypedDict, Annotated, Literal
from operator import add
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    run_id: str
    messages: Annotated[list, add_messages]
    plan: list[str]
    completed: Annotated[list[str], add]
    artifacts: dict[str, str]   # logical_name → file path
    issues: Annotated[list[str], add]
    cost_used_usd: float
    next_action: Literal["analyze", "architect", "design", "review", "done"]
```

### 6.3 `app/agents/coordinator.py`

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.agents.state import AgentState
from app.agents.nodes import analyst, architect, designer, reviewer
import os

async def build_graph():
    g = StateGraph(AgentState)
    g.add_node("analyst", analyst.run)
    g.add_node("architect", architect.run)
    g.add_node("designer", designer.run)
    g.add_node("reviewer", reviewer.run)

    g.add_edge(START, "analyst")
    g.add_edge("analyst", "architect")
    g.add_edge("architect", "designer")
    g.add_edge("designer", "reviewer")
    g.add_conditional_edges(
        "reviewer",
        lambda s: "done" if not s["issues"] else "designer",
        {"done": END, "designer": "designer"},
    )

    saver = AsyncPostgresSaver.from_conn_string(os.environ["POSTGRES_URL"])
    return g.compile(
        checkpointer=saver,
        interrupt_before=["architect"],  # HITL gate
    )
```

### 6.4 `app/agents/nodes/analyst.py` (template — others follow)

```python
from app.llm.factory import get_llm
from app.tools.registry import tools_for
from app.agents.state import AgentState

SYSTEM = """You are an Analyst. Decompose the user's request into clear requirements.
Output a markdown checklist of:
- Users (primary, secondary)
- Scope (in / out)
- Constraints (budget, timeline)
- Success criteria
Save the result to workspaces/<run_id>/requirements.md via write_artifact."""

async def run(state: AgentState) -> dict:
    llm = get_llm(role="analyst")  # routes to Sonnet
    tools = tools_for("analyst")   # ask_user, read/write_artifact, search_kb
    
    response = await llm.bind_tools(tools).ainvoke(
        [{"role": "system", "content": SYSTEM}] + state["messages"]
    )
    return {
        "messages": [response],
        "completed": ["analysis"],
        "artifacts": {"requirements": f"workspaces/{state['run_id']}/requirements.md"},
        "next_action": "architect",
    }
```

### 6.5 `app/llm/factory.py`

```python
import os
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

# Role-based routing
def get_llm(role: str):
    routing = {
        "analyst":   ChatAnthropic(model="claude-sonnet-4-6", max_tokens=2000),
        "architect": ChatAnthropic(model="claude-sonnet-4-6", max_tokens=2000),
        "designer":  ChatAnthropic(model="claude-haiku-4-5-20251001", max_tokens=2000),
        "reviewer":  ChatAnthropic(model="claude-sonnet-4-6", max_tokens=1500),
        # cheap fallback for utility tasks
        "utility":   ChatOpenAI(
            base_url=f"{os.environ['OLLAMA_URL']}/v1",
            api_key="ollama",
            model="llama3.2:3b",
        ),
    }
    return routing[role]
```

### 6.6 `app/tools/kb.py`

```python
from qdrant_client import AsyncQdrantClient
from langchain_core.tools import tool
import httpx, os

_qdrant: AsyncQdrantClient | None = None

def _client():
    global _qdrant
    if not _qdrant:
        _qdrant = AsyncQdrantClient(url=os.environ["QDRANT_URL"])
    return _qdrant

async def _embed(text: str) -> list[float]:
    async with httpx.AsyncClient() as h:
        r = await h.post(
            f"{os.environ['OLLAMA_URL']}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text},
            timeout=15,
        )
        return r.json()["embedding"]

@tool
async def search_kb(query: str, top_k: int = 5) -> list[dict]:
    """Search the knowledge base for relevant patterns/docs.
    Use this when you need reference material on architecture patterns,
    common DB schemas, or past project examples.
    Returns list of {title, snippet, score}."""
    emb = await _embed(query)
    results = await _client().search(
        collection_name="patterns",
        query_vector=emb,
        limit=top_k,
    )
    return [
        {
            "title": r.payload.get("title", ""),
            "snippet": r.payload.get("text", "")[:500],
            "score": r.score,
        }
        for r in results
    ]
```

### 6.7 `app/api/chat.py`

```python
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from app.agents.coordinator import build_graph
import uuid

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None

@router.post("")
async def chat(req: ChatRequest):
    graph = await build_graph()
    thread_id = req.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    result = await graph.ainvoke(
        {"messages": [{"role": "user", "content": req.message}], "run_id": thread_id},
        config=config,
    )
    return {
        "thread_id": thread_id,
        "answer": result["messages"][-1].content,
        "artifacts": result.get("artifacts", {}),
    }
```

> นี่คือ skeleton — ใช้รันได้ แล้ว iterate
> **อย่า** ขยายก่อนรันได้ — รันก่อน, ลองคุยก่อน, แล้วค่อยเพิ่ม

---

## 7. First Run (จาก zero ถึง chat ใน 30 นาที)

```bash
# 1. Clone หรือสร้าง folder ตามโครงในข้อ 3
mkdir my-agent && cd my-agent
# สร้างไฟล์ตาม layout (โดยเฉพาะ docker-compose.yml + Dockerfile + app/)

# 2. ตั้งค่า env
cp .env.example .env
# แก้ .env: ใส่ ANTHROPIC_API_KEY, สร้าง LANGFUSE_* ด้วย:
openssl rand -hex 32  # ใช้ 3 ครั้งสำหรับ SECRET, SALT, ENCRYPTION_KEY

# 3. ขึ้น stack
make up
# รอ 1-2 นาที → ตรวจ docker compose ps ว่าทุก service running

# 4. ตั้งค่า Langfuse (one-time)
# เปิด http://localhost:3000
# - Sign up (local account)
# - Create project "my-agent"
# - Copy public + secret keys → ใส่ใน .env
# - make down && make up   # restart with new env

# 5. Bootstrap (pull models, seed KB)
make bootstrap
# ครั้งแรกใช้เวลา 5-10 นาที (download nomic-embed + llama3.2:3b)

# 6. Test chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to build an online clothing store"}'

# 7. ดู trace
# เปิด http://localhost:3000 → traces tab → เห็น LLM calls, costs, latency
```

---

## 8. Day-2 Operations

### เพิ่ม agent role ใหม่

1. สร้าง `app/agents/nodes/<role>.py` ตาม template ของ analyst (§6.4)
2. ใส่ใน routing ของ `app/llm/factory.py`
3. Register ใน graph (`coordinator.py`):
   ```python
   g.add_node("<role>", new_role.run)
   g.add_edge("previous_node", "<role>")
   ```
4. Restart: `docker compose restart agent`

### เพิ่ม tool

1. สร้างใน `app/tools/<tool>.py` ใช้ `@tool` decorator
2. Register ใน `app/tools/registry.py`:
   ```python
   ROLE_TOOLS = {
       "analyst": [ask_user, read_artifact, write_artifact, search_kb],
       "architect": [..., draw_mermaid, search_kb],
       "designer": [...],
   }
   ```
3. Restart agent

### เพิ่ม document ใน KB

วาง markdown file ใน `kb_seed/patterns/` แล้ว:
```bash
make seed
```

### Debug agent ที่พัง

1. **Check Langfuse**: http://localhost:3000 → trace ของ run ที่ fail
2. **Check Postgres state**: 
   ```sql
   SELECT * FROM checkpoints WHERE thread_id = '<run_id>' ORDER BY created_at DESC LIMIT 10;
   ```
3. **Replay**: ใน LangGraph Studio (`langgraph dev`) → time travel จาก checkpoint
4. **Check logs**: `make logs`

### Resume after crash

LangGraph มี checkpoint built-in:
```python
# จาก thread_id เดิม → resume
result = await graph.ainvoke(None, config={"configurable": {"thread_id": "..."}})
```

### HITL approval

State machine มี `interrupt_before=["architect"]` → graph หยุดก่อน node นั้น
- Frontend show pending approval
- User approves → `graph.ainvoke(None, config=...)` ต่อ
- User changes → `graph.update_state(config, {"messages": [...]})` แล้ว invoke

---

## 9. Cost Per Run (estimated)

จาก case study (07) — apply blueprint นี้:

```
Per "build e-commerce" run:
  Analyst (Sonnet, ~10K in + 3K out)        ~ $0.08
  Architect (Sonnet, ~30K in + 10K out)     ~ $0.24
  4× Designer (Haiku, ~80K in + 20K out)    ~ $0.18
  Reviewer (Sonnet, ~50K in + 5K out)       ~ $0.23
  Embed (Ollama local)                      = $0.00
  ─────────────────────────────────────────
  Total                                     ~ $0.73
  
With prompt caching (system + KB):          ~ $0.30
With 50% semantic cache hit:                ~ $0.15
```

For typical chat (single agent), expect $0.01-0.05 per turn

---

## 10. Resource Footprint (laptop)

```
qdrant:   ~ 100MB RAM (10K vectors)
postgres: ~ 100MB
redis:    ~ 50MB
ollama:   ~ 4GB RAM (llama3.2:3b loaded) + 1GB embed
langfuse: ~ 300MB
agent:    ~ 200MB
─────────────────────────────────
Total:    ~ 6GB RAM idle
          ~ 8-10GB peak (during inference)
```

→ ต้องการ laptop **16GB RAM ขั้นต่ำ**, แนะนำ 32GB
ถ้าน้อย → drop Ollama ตัว LLM (เก็บแค่ embed) + ใช้ cloud LLM 100%

---

## 11. Path to Production

### Stage 1: Local (this blueprint)
- รันบน laptop, dev work
- Cost: $0 stack + ~$5-30/mo APIs

### Stage 2: VPS (1 month after stable)
- Hetzner CPX31 (€15/mo) — same docker compose
- Add Caddy reverse proxy + SSL
- Backup script (Postgres + Qdrant snapshots) → S3/B2

```bash
# bootstrap on VPS
ssh root@vps
git clone <your-repo>
cd my-agent
docker compose up -d
# add Caddyfile for SSL
```

### Stage 3: Managed Services (when you outgrow VPS)
- Postgres → Supabase ($25/mo)
- Qdrant → Qdrant Cloud (free 1GB) or stay self-host
- Langfuse → Langfuse Cloud (free 50K events/mo)
- Agent → Cloud Run / Fly.io (~$10/mo)

### Stage 4: Scale (rare)
- LangGraph Cloud (managed)
- Multi-region
- Load balancer + multiple agent replicas

> 80% ของ projects หยุดที่ Stage 2 — พอใช้

---

## 12. ห้ามทำในช่วง Stage 1

- ❌ Add Kubernetes (overhead เกินค่า)
- ❌ Multi-region setup
- ❌ Microservices split (1 agent service ก่อน)
- ❌ Custom auth (use simple API key)
- ❌ Prometheus + Grafana (Langfuse เพียงพอ)
- ❌ More than 5 agent roles (เริ่ม 2-3 ก่อน)
- ❌ Sub-agent recursion (เริ่ม flat ก่อน)

ใส่เมื่อมี data ว่าจำเป็น — ไม่ใช่ "เพราะ best practice"

---

## 13. ห้ามลืม (production checklist)

- [ ] `MAX_COST_PER_REQUEST_USD` ใน `.env`
- [ ] `MAX_STEPS_PER_AGENT` cap
- [ ] Langfuse traces ทำงาน (เห็นใน UI)
- [ ] Promptfoo eval suite (อย่างน้อย 10 cases)
- [ ] Backup script + cron
- [ ] SSL (Caddy / Let's Encrypt) ที่ Stage 2
- [ ] HITL interrupt ก่อน irreversible actions
- [ ] PII redaction ก่อนส่ง LLM
- [ ] Tool result sanitization (anti-injection)
- [ ] Rate limit per user

---

## 14. ถ้าติด — Diagnostic

| อาการ | ตรวจ | แก้ |
|---|---|---|
| Container ไม่ขึ้น | `docker compose logs <svc>` | ดู error → fix env |
| Postgres password ผิด | logs ขึ้น auth fail | `docker compose down -v` แล้ว up ใหม่ |
| Ollama OOM | `docker logs ollama` | ใช้ smaller model หรือ disable Ollama LLM |
| Qdrant collection ไม่มี | search 404 | `make seed` |
| Langfuse trace ไม่ขึ้น | API key ใน .env | regen + restart |
| Agent loop ไม่จบ | Langfuse trace ยาว | ใส่ `max_steps` ใน budget |
| Cost พุ่ง | Langfuse cost dashboard | check prompt cache + routing |
| LangGraph state ไม่ persist | postgres connection | ตรวจ `POSTGRES_URL` |

---

## 15. Compose กับ MCP

ถ้ามี MCP server ที่ทีมใช้อยู่แล้ว (จาก [08](08_MCP_Deep_Dive.md)) — wrap เป็น tool:

```python
# app/tools/mcp_bridge.py
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.tools import StructuredTool
from contextlib import asynccontextmanager

@asynccontextmanager
async def mcp_session(command, args):
    params = StdioServerParameters(command=command, args=args)
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            yield session

# Wrap MCP tool as LangChain tool
def mcp_tool_to_lc(mcp_session, tool_def):
    async def call(**kwargs):
        result = await mcp_session.call_tool(tool_def.name, kwargs)
        return result.content[0].text
    return StructuredTool.from_function(
        coroutine=call,
        name=tool_def.name,
        description=tool_def.description,
        args_schema=...,  # build from tool_def.inputSchema
    )
```

→ MCP server ใหม่ทุกตัว = "lego" สำหรับ agent

---

## 16. Compose กับ Skills

ถ้าใช้ใน Claude Code dev — เขียน [Skills](09_Agent_Skills.md) สำหรับ pattern ที่ทำซ้ำ:

```
my-agent/.claude/skills/
├── add-agent-role/
│   └── SKILL.md          # how to add a new role
├── debug-agent/
│   └── SKILL.md          # debug workflow
└── deploy/
    └── SKILL.md          # deploy to VPS
```

Skill ทำให้ Claude Code ช่วย maintain agent service ได้สะดวกตลอด

---

## 17. Summary

```
ARCHITECTURE: agent (LangGraph) + qdrant + postgres + redis + ollama + langfuse  
LLM ROUTING:  Sonnet (planner), Haiku (workers), Ollama (embed + small)
DEPLOY:       1 docker-compose.yml, 6 services
DEV LOOP:     edit code → docker compose restart agent → test → check Langfuse
COST:         ~$0.30 per complex run (with caching)
SCALE PATH:   Local → VPS → Managed → (rare) full cloud
```

ถ้าทำตาม blueprint นี้ → **คุณจะมี agent ที่ใช้งานได้จริง within 1 day** + scalable up จากนั้น

---

## 18. ห้ามถามต่อ — ทำเลย

1. ✅ สร้าง folder structure
2. ✅ Copy `docker-compose.yml` + `Dockerfile` + `Makefile`
3. ✅ Copy code skeleton จาก §6
4. ✅ `cp .env.example .env` + ใส่ key
5. ✅ `make up` → wait → `make bootstrap`
6. ✅ ทดสอบ `curl /chat`
7. ✅ ดู trace ใน Langfuse
8. ✅ Iterate

ถ้าติด — diagnostic table (§14)
ถ้าเข้าใจ pattern ใน [02](02_Design_Patterns.md) แล้ว — เพิ่ม agent role ตาม §8

---

## References (ไฟล์อื่นใน series)

- Why this stack: [03 Frameworks](03_Frameworks_Comparison.md)
- LangGraph patterns: [deep_dive/01](deep_dive/01_LangGraph_Patterns.md)
- Self-hosted ลึก: [deep_dive/02](deep_dive/02_Self_Hosted_Stack.md)
- Cost ลด: [deep_dive/04](deep_dive/04_Cost_Optimization_Tactics.md)
- Tool design: [04](04_Tools_and_Selection.md)
- MCP integration: [08](08_MCP_Deep_Dive.md)
- Skills (dev workflow): [09](09_Agent_Skills.md)
- Case study (e-commerce): [07](07_Case_Study_Ecommerce_Builder.md)

ไฟล์นี้ = blueprint
ไฟล์อื่น = explanation / depth — อ่านเฉพาะถ้าสงสัย
