# 07 — Case Study: E-commerce Builder Agent

> เอาทุกอย่างจาก 01-06 มาประกอบ — สร้าง multi-agent system ที่รับ requirement → สร้างเว็บขายของจริง
> Use case จากไอเดียของคุณ — แต่ทำเป็นจริงได้

---

## 0. Recap ไอเดียเดิม

ของคุณ:
> "Assistant รับ req → วิเคราะห์ → design architecture/system → ส่งให้ AI experts → AI implement (model เบาๆ) → มี coordinator + vector DB"

**Pattern**: Hierarchical + Orchestrator-Workers + Evaluator-Optimizer (composite)

ก่อนเริ่ม — มี "การปรับ" จากไอเดียเดิม:
1. **อย่าให้ agent build app ตั้งแต่ requirement → production code ในรอบเดียว** — fail rate สูงมาก
   เปลี่ยนเป็น: agent ออกแบบ + scaffold project → human (หรือ coding agent อื่น) ปรับแต่ง
2. **ใช้ "spec-first" workflow** — ทุก phase produce **artifact** (markdown/yaml/code stub) ไม่ใช่แค่ chat
3. **Human-in-the-loop หลัง phase สำคัญ** — Architecture review, schema review, before code gen
4. **Token budget ชัดเจน** — ไม่งั้น cost ระเบิด

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  USER: "อยากสร้างเว็บขายเสื้อผ้าออนไลน์ + admin + payment"     │
└────────────────────────────┬────────────────────────────────┘
                             ▼
        ┌─────────────────────────────────────────┐
        │          COORDINATOR AGENT              │
        │   (Sonnet 4.6 — planning, dispatch)     │
        │                                         │
        │   - Manages phases                      │
        │   - Tracks artifacts                    │
        │   - Handles HITL approval               │
        └──────────────────┬──────────────────────┘
                           │
        ╔══════════════════╪══════════════════╗
        ║       PHASE 1: ANALYSIS             ║
        ╠═════════════════════════════════════╣
        ║   Analyst Agent (Sonnet)            ║
        ║   - Clarifying questions            ║
        ║   - Scope definition                ║
        ║   - Tech constraints                ║
        ║   → produces: requirements.md       ║
        ║                                     ║
        ║   [HUMAN APPROVE]                   ║
        ╚═════════════════════════════════════╝
                           │
        ╔══════════════════╪══════════════════╗
        ║      PHASE 2: ARCHITECTURE          ║
        ╠═════════════════════════════════════╣
        ║   Architect Agent (Sonnet)          ║
        ║   - System decomposition            ║
        ║   - Tech stack selection            ║
        ║   - Service boundaries              ║
        ║   → produces: architecture.md       ║
        ║              + diagrams.mmd         ║
        ║                                     ║
        ║   [HUMAN APPROVE]                   ║
        ╚═════════════════════════════════════╝
                           │
        ╔══════════════════╪══════════════════╗
        ║   PHASE 3: DETAIL DESIGN (parallel) ║
        ╠═════════════════════════════════════╣
        ║   ┌─────┐  ┌─────┐  ┌─────┐  ┌────┐ ║
        ║   │ DBA │  │BE   │  │FE   │  │OPS │ ║
        ║   └──┬──┘  └──┬──┘  └──┬──┘  └─┬──┘ ║
        ║      │ Haiku  │ Haiku  │ Haiku │Haiku║
        ║      ▼        ▼        ▼       ▼    ║
        ║   schema.sql api.yaml ui.spec dock  ║
        ║                                     ║
        ║   ↓ Reviewer (Sonnet) merges        ║
        ╚═════════════════════════════════════╝
                           │
        ╔══════════════════╪══════════════════╗
        ║      PHASE 4: SCAFFOLDING           ║
        ╠═════════════════════════════════════╣
        ║   Implementer Agents (DeepSeek/Llama)║
        ║   - Generate boilerplate            ║
        ║   - Wire endpoints                  ║
        ║   - Set up auth                     ║
        ║   → produces: project files (git)   ║
        ╚═════════════════════════════════════╝
                           │
                           ▼
                  ┌──────────────┐
                  │ Final output │
                  └──────────────┘

┌─────────────────────────────────────────────────────────────┐
│  SHARED MEMORY                                              │
│  - workspace/<project_id>/  (file-based artifacts, git)     │
│  - Qdrant: chunks of artifacts (semantic search)            │
│  - Postgres: phase state, agent logs                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  GLOBAL KB                                                  │
│  - Architecture patterns                                    │
│  - DB schema templates                                      │
│  - Common API designs                                       │
│  - Past project lessons                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Phase Design — รายละเอียด

### Phase 1: Analysis

**Agent**: Analyst (Claude Sonnet 4.6)

**Input**: User's free-form request

**Goal**: ตอบให้ได้ครบ:
- ใครเป็น user หลัก? (B2C / B2B / both)
- Scope: catalog + cart + payment + admin? + อะไรอีก?
- Scale คาดหวัง? (100 user, 10K user, 1M user)
- Constraints: budget, timeline, mandatory tech
- Out of scope?

**Tools**:
- `ask_user(question)` — clarifying question
- `search_global_kb(query)` — ดู past project ที่คล้าย
- `write_artifact(path, content)`

**Anti-pattern**: ถามคำถามเป็น 100 ข้อ → user เบื่อ
**Pattern ที่ใช้**: ถาม batch ละ 3-5 คำถาม + ระบุ default ให้ตอบเร็ว

**Output artifact**: `workspace/<project>/requirements.md`
```markdown
# Project: Online Clothing Store

## Users
- Primary: B2C end customers (Thailand)
- Secondary: Admin (1-3 staff)

## Scope (MVP)
- [x] Product catalog (300+ SKU, multi-image)
- [x] Cart + checkout
- [x] Payment: PromptPay + Credit card (Omise/Stripe)
- [x] Admin: product CRUD, order management
- [x] Auth: email + Google
- [ ] Reviews (post-MVP)
- [ ] Recommendation (post-MVP)

## Scale
- Year 1: 5K MAU, 200 orders/day peak

## Constraints
- Budget: ~$50/mo infra
- Timeline: MVP in 8 weeks
- Tech: prefer TypeScript stack

## Out of scope
- Mobile app
- Multi-vendor
```

**HITL**: User review → approve / request changes

---

### Phase 2: Architecture

**Agent**: Architect (Claude Sonnet 4.6)

**Input**: `requirements.md`

**Goal**: ออกแบบระบบในระดับ component
- Service boundaries
- Tech stack เลือก
- Data flow
- Deployment topology
- Security boundaries

**Tools**:
- `read_artifact(path)`
- `search_global_kb(query)` — หา pattern เก่า
- `write_artifact(path, content)`
- `draw_mermaid(spec)` — generate diagram

**Output artifacts**:
- `architecture.md` — narrative
- `diagrams/system.mmd` — Mermaid diagram
- `diagrams/data_flow.mmd`
- `tech_stack.md` — เลือก lib/framework + เหตุผล

ตัวอย่าง output (excerpt):
```markdown
# Architecture: Online Clothing Store

## Components
1. **Frontend** (Next.js 15 — SSR for SEO)
2. **Backend API** (Next.js API routes — keep simple)
3. **Database** (Postgres on Supabase free tier)
4. **Storage** (Supabase Storage for images)
5. **Search** (Postgres FTS — no need for ES at this scale)
6. **Payment** (Omise — Thai-friendly, PromptPay support)
7. **Email** (Resend — free tier)
8. **Hosting** (Vercel free tier — monitor usage)

## Why this stack
- Single Next.js codebase — small team velocity
- Supabase = managed Postgres + auth + storage in 1 → ลด complexity
- All components free tier ที่ scale 5K MAU พอ

## Future re-architect
- 50K+ MAU → split BE → Fastify API
- Move images → Cloudflare R2
```

**HITL**: User approve

---

### Phase 3: Detailed Design (Parallel Specialists)

**Agents** (parallel, แต่ละตัวมี scope แคบ):

#### 3a. Database Designer (Haiku 4.5)
**Tools**: `read_artifact`, `write_artifact`, `validate_sql`, `search_kb("schema_pattern")`
**Output**: `db/schema.sql`, `db/migrations/`, `db/erd.mmd`

#### 3b. Backend Designer (Haiku 4.5)
**Tools**: `read_artifact`, `write_artifact`, `search_kb("api_pattern")`
**Output**: `api/openapi.yaml`, `api/auth.md`

#### 3c. Frontend Designer (Haiku 4.5)
**Tools**: `read_artifact`, `write_artifact`, `search_kb("ui_pattern")`
**Output**: `ui/page_specs.md`, `ui/component_tree.md`

#### 3d. DevOps Designer (Haiku 4.5)
**Tools**: `read_artifact`, `write_artifact`, `search_kb("deploy_pattern")`
**Output**: `deploy/dockerfile`, `deploy/docker-compose.yml`, `deploy/runbook.md`

**ทำไม parallel ได้**: แต่ละ specialist มี scope ต่างกัน — depend on architecture.md ร่วมกันเท่านั้น

**Reviewer Agent** (Sonnet) → รัน หลัง parallel เสร็จ
- Cross-check: schema match กับ API spec มั้ย? UI page need API ที่ไม่มีมั้ย?
- Output: `review.md` + flag inconsistency

ถ้ามี inconsistency → loop กลับให้ specialist แก้ (Evaluator-Optimizer pattern)

---

### Phase 4: Scaffolding

**Agents**: Implementers (DeepSeek V3 / Llama 3.3 — cheap, code-focused)

แต่ละตัวรับ:
- Spec file เฉพาะ (เช่น `api/openapi.yaml` + `db/schema.sql`)
- Template (boilerplate Next.js + Prisma)

**Goal**: scaffold codebase — **ไม่ใช่ implement business logic เต็ม**
- Migrations
- API route stubs (mock response แต่ structure ถูก)
- React components (skeleton)
- Docker setup

**Tools**: `read_artifact`, `read_template`, `write_code_file`, `run_tests` (ถ้ามี)

**Output**: Git repo with structure + boilerplate

**Why ใช้ cheap model**: code generation ส่วน boilerplate ไม่ต้องใช้ Sonnet — Llama 3.3 70B ฟรีบน Groq + เร็ว 1000+ tok/s

---

## 3. Coordinator Agent — รายละเอียด

### Responsibilities
1. Phase progression — รู้ว่าตอนนี้อยู่ phase ไหน
2. Spawn agent ที่เหมาะ
3. Track artifacts
4. Handle HITL pause
5. Budget enforcement
6. Error recovery / replan

### State (LangGraph)

```python
from typing import TypedDict, Literal

class ProjectState(TypedDict):
    project_id: str
    phase: Literal["analysis", "architecture", "design", "scaffold", "done"]
    requirements: str | None
    architecture: str | None
    designs: dict  # {"db": ..., "api": ..., "ui": ..., "ops": ...}
    code_repo_path: str | None
    issues: list[str]
    budget_used_usd: float
    budget_max_usd: float
    awaiting_human: bool
    human_feedback: str | None
```

### Graph

```python
from langgraph.graph import StateGraph, END

g = StateGraph(ProjectState)

g.add_node("analyst", run_analyst)
g.add_node("await_approve_req", interrupt_node)  # HITL
g.add_node("architect", run_architect)
g.add_node("await_approve_arch", interrupt_node)
g.add_node("designers_parallel", run_designers_parallel)
g.add_node("reviewer", run_reviewer)
g.add_node("scaffold", run_scaffold)

g.set_entry_point("analyst")
g.add_edge("analyst", "await_approve_req")
g.add_conditional_edges("await_approve_req",
    lambda s: "architect" if not s["human_feedback"] else "analyst",
    {"architect": "architect", "analyst": "analyst"})

g.add_edge("architect", "await_approve_arch")
g.add_conditional_edges("await_approve_arch",
    lambda s: "designers_parallel" if not s["human_feedback"] else "architect",
    {"designers_parallel": "designers_parallel", "architect": "architect"})

g.add_edge("designers_parallel", "reviewer")
g.add_conditional_edges("reviewer",
    lambda s: "scaffold" if not s["issues"] else "designers_parallel",
    {"scaffold": "scaffold", "designers_parallel": "designers_parallel"})

g.add_edge("scaffold", END)

app = g.compile(
    checkpointer=PostgresSaver.from_conn_string("..."),
    interrupt_before=["await_approve_req", "await_approve_arch"],
)
```

> รายละเอียด LangGraph อยู่ใน [deep_dive/01](deep_dive/01_LangGraph_Patterns.md)

---

## 4. Tech Stack ที่แนะนำ — Free / Cheap

```
Orchestration:  LangGraph (Python)  [free, OSS]
LLMs:
  - Coordinator/Analyst/Architect:  Claude Sonnet 4.6  ($3/$15)
  - Specialists (DBA/BE/FE/OPS):    Claude Haiku 4.5   ($1/$5)
  - Implementers:                   DeepSeek V3 หรือ
                                    Llama 3.3 70B (Groq free)  [free!]
  - Reviewer:                       Claude Sonnet 4.6 (consistency check)

Memory:
  - Vector DB:    Qdrant (Docker)            [free]
  - State store:  Postgres (LangGraph cp)    [free, Supabase]
  - Embedding:    Voyage-3 หรือ bge-m3       [paid cheap / free local]

Tools:
  - search_kb:        Qdrant query
  - write_artifact:   filesystem (workspace/)
  - read_artifact:    filesystem
  - draw_mermaid:     local mermaid CLI
  - validate_sql:     pglast (Python, OSS)
  - validate_openapi: openapi-spec-validator
  - run_tests:        E2B sandbox (free dev tier)

Observability:
  - Langfuse self-host (Docker)               [free]

Hosting:
  - Phase 1 (dev):  Local Docker Compose
  - Phase 2 (beta): Railway $5/mo + managed Postgres
  - Phase 3 (prod): Cloud Run + managed services
```

### ค่าใช้จ่ายประมาณการ (per project)

```
Phase 1 (Analysis):       Sonnet ~10K in + 3K out  ≈ $0.08
Phase 2 (Architecture):   Sonnet ~30K in + 10K out ≈ $0.24
Phase 3 (Designers ×4):   Haiku  ~80K in + 20K out ≈ $0.18
Phase 3 (Review):         Sonnet ~50K in + 5K out  ≈ $0.23
Phase 4 (Scaffold ×4):    Llama (Groq free)        = $0.00
Embedding + Qdrant:                                = $0.00
─────────────────────────────────────────────────────────
Total per project:                                 ≈ $0.73
```

ถ้า cache prompts (system + global KB) → ลดอีก 60% เหลือ ~$0.30/project

---

## 5. Implementation Skeleton

### 5.1 Project structure

```
ecommerce-builder/
├── docker-compose.yml
├── .env
├── pyproject.toml
├── src/
│   ├── coordinator/
│   │   ├── graph.py           # LangGraph definition
│   │   └── state.py
│   ├── agents/
│   │   ├── analyst.py
│   │   ├── architect.py
│   │   ├── designers/
│   │   │   ├── dba.py
│   │   │   ├── backend.py
│   │   │   ├── frontend.py
│   │   │   └── devops.py
│   │   ├── reviewer.py
│   │   └── implementers/
│   │       └── scaffold.py
│   ├── tools/
│   │   ├── filesystem.py      # read_artifact, write_artifact
│   │   ├── kb.py              # search_global_kb
│   │   ├── validate.py        # validate_sql, validate_openapi
│   │   └── mermaid.py
│   ├── memory/
│   │   ├── vector_store.py    # Qdrant client
│   │   └── workspace.py       # File-based artifact mgmt
│   ├── llm/
│   │   ├── factory.py         # Model routing
│   │   └── budget.py
│   └── api.py                 # FastAPI entry point
├── workspaces/                # Per-project artifacts
│   └── <project_id>/
│       ├── requirements.md
│       ├── architecture.md
│       └── ...
├── kb/                        # Global KB (seeds)
│   ├── patterns/
│   └── examples/
└── tests/
    └── eval/                  # Promptfoo configs
```

### 5.2 Coordinator skeleton

```python
# src/coordinator/graph.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from src.coordinator.state import ProjectState
from src.agents import analyst, architect, designers, reviewer, scaffold

def build_graph(checkpointer):
    g = StateGraph(ProjectState)
    
    g.add_node("analyst", analyst.run)
    g.add_node("architect", architect.run)
    g.add_node("designers", designers.run_parallel)
    g.add_node("reviewer", reviewer.run)
    g.add_node("scaffold", scaffold.run)
    
    g.set_entry_point("analyst")
    g.add_edge("analyst", "architect")
    g.add_edge("architect", "designers")
    g.add_edge("designers", "reviewer")
    g.add_conditional_edges(
        "reviewer",
        lambda s: "scaffold" if not s["issues"] else "designers",
        {"scaffold": "scaffold", "designers": "designers"},
    )
    g.add_edge("scaffold", END)
    
    return g.compile(
        checkpointer=checkpointer,
        interrupt_before=["architect", "designers"],  # HITL
    )
```

### 5.3 Specialist agent (เช่น DBA)

```python
# src/agents/designers/dba.py
from anthropic import Anthropic
from src.tools import filesystem, kb, validate
from src.llm.factory import get_model

DBA_SYSTEM_PROMPT = """
You are a Senior Database Architect specialized in Postgres.
Your task: design schema given requirements + architecture.

Output:
1. SQL schema (CREATE TABLE statements)
2. Migrations folder structure
3. ERD as Mermaid diagram

Constraints:
- Use UUID primary keys
- Include audit columns (created_at, updated_at)
- Foreign keys with proper CASCADE/RESTRICT
- Indexes for common query patterns

Always write artifacts via write_artifact tool.
"""

TOOLS = [
    filesystem.read_artifact_schema(),
    filesystem.write_artifact_schema(),
    kb.search_kb_schema(),
    validate.validate_sql_schema(),
]

def run(state):
    client = get_model("haiku-4-5", with_cache=True)
    
    requirements = filesystem.read(f"workspaces/{state['project_id']}/requirements.md")
    architecture = filesystem.read(f"workspaces/{state['project_id']}/architecture.md")
    
    messages = [
        {"role": "user", "content": f"""
        Requirements:\n{requirements}\n\n
        Architecture:\n{architecture}\n\n
        Design the database schema and write to db/schema.sql.
        """}
    ]
    
    # Agent loop with budget cap
    for _ in range(10):
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            system=DBA_SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
            max_tokens=2048,
        )
        if resp.stop_reason == "end_turn":
            break
        # ... handle tool calls
    
    return {**state, "designs": {**state["designs"], "db": "db/schema.sql"}}
```

### 5.4 Parallel designers

```python
# src/agents/designers/__init__.py
from concurrent.futures import ThreadPoolExecutor
from . import dba, backend, frontend, devops

def run_parallel(state):
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {
            "db": ex.submit(dba.run, state),
            "api": ex.submit(backend.run, state),
            "ui": ex.submit(frontend.run, state),
            "ops": ex.submit(devops.run, state),
        }
        results = {k: f.result() for k, f in futures.items()}
    
    # merge designs into state
    designs = {}
    for k, partial_state in results.items():
        designs[k] = partial_state["designs"][k]
    return {**state, "designs": designs}
```

---

## 6. Failure Modes & Mitigations

### FM1: Analyst ถามคำถามไม่จบ
**Mitigation**: cap rounds (≤ 3) + force commit

### FM2: Architect แนะ tech ไม่ถูกกับ scale
**Mitigation**: Constrain ใน system prompt + require justification

### FM3: Specialists ออกแบบไม่ตรงกัน (schema vs API)
**Mitigation**: Reviewer pass — loop fix
**+ Defensive**: ส่ง spec ของ specialist อื่นเข้าเป็น context (ไม่ใช่แค่ architecture)

### FM4: Implementer แต่ง code มี bug
**Mitigation**: 
- ใช้ Llama เฉพาะ scaffolding
- Real implementation ทิ้งให้ human / coding agent อื่น
- Generate test stubs ด้วย (ให้ human รัน)

### FM5: Cost ระเบิด
**Mitigation**: 
- Budget per project ($2 hard cap)
- Alert ที่ 50%, 75%, 90%
- Auto-halt ที่ 100%

### FM6: HITL ไม่กลับมา
**Mitigation**: Timeout 24 ชม. → notify user → archive

### FM7: Vector DB returns junk
**Mitigation**: 
- Reranker layer
- Quality threshold (similarity ≥ 0.7)
- Specialist เลือกใช้/ทิ้งได้

---

## 7. Roadmap — สร้างจริงยังไง

### Week 1: Foundations
- [ ] Set up Docker Compose: Qdrant + Postgres + Langfuse
- [ ] LangGraph hello world (1 node, 1 LLM call)
- [ ] Anthropic + OpenRouter API keys
- [ ] Basic tools: `read_artifact`, `write_artifact`

### Week 2: Single agent
- [ ] Analyst agent (single phase)
- [ ] HITL interrupt (user approve via API)
- [ ] Promptfoo eval (3-5 sample requirements)

### Week 3: Add Architect + Reviewer
- [ ] Architect with Mermaid generation
- [ ] Reviewer (cross-check artifacts)
- [ ] Loop on issues

### Week 4: Specialists in parallel
- [ ] DBA, Backend, Frontend, DevOps
- [ ] ThreadPoolExecutor parallel
- [ ] Merge artifacts

### Week 5: Implementer + scaffold
- [ ] Llama 3.3 via Groq for scaffolding
- [ ] Template system
- [ ] Git output

### Week 6: Memory & KB
- [ ] Embed past projects → Qdrant
- [ ] Pattern KB seed (5-10 patterns)
- [ ] Specialist queries KB

### Week 7: Production hardening
- [ ] Budget cap, error recovery, retries
- [ ] Observability dashboard (Langfuse)
- [ ] Load test 10 concurrent projects

### Week 8: Polish
- [ ] Web UI (or CLI) for user
- [ ] Documentation
- [ ] Eval suite with regression check

---

## 8. ลด Scope ถ้าอยากลองเร็ว

ถ้า 8 สัปดาห์ใหญ่ — ลดเป็น MVP 1 สัปดาห์:

**Tiny MVP**:
- Single LangGraph: analyst → architect → 1 designer (เลือก DBA) → done
- Skip parallel, skip implementer
- ใช้ free Gemini 2.5 Flash เลย
- File-based memory (ไม่มี Qdrant)
- รัน CLI ไม่มี UI

**Cost**: $0 (Gemini free tier)
**Time**: 1 สัปดาห์ part-time

แล้วค่อย scale up ตาม roadmap

---

## 9. ทำไมไม่ใช้ AutoGen / CrewAI?

ลองคิดแล้ว — สำหรับ use case นี้:

**CrewAI**: 
- ✅ Easy mental model (role-based)
- ❌ HITL ยาก
- ❌ Parallel + checkpoint ไม่ smooth เท่า LangGraph
- 🟡 ดีถ้าทำ MVP เร็ว

**AutoGen**:
- ✅ Multi-agent debate ดี
- ❌ "Group chat" → token explode สำหรับ structured workflow
- ❌ Production trace ยาก
- 🟡 ไม่เหมาะ phase-based workflow

**LangGraph**:
- ✅ State + checkpoint + HITL พอดี
- ✅ Production-ready
- ❌ Verbose
- ✅ ตอบโจทย์นี้ดีสุด

ถ้าจะใช้ low-code: **n8n** ทำได้แต่ multi-agent ใน n8n ลำบาก — ดู [deep_dive/03](deep_dive/03_n8n_Agent_Workflows.md) สำหรับลิมิตเชิงลึก

---

## 10. คำถามเปิดที่ต้องคิดต่อ

1. **Code generation จริงเลยมั้ย?** — ตอนนี้ design ของเรา scaffold แค่ structure
   - Option A: เรียก Claude Code (CLI) ตอนจบ → coding agent จริง
   - Option B: stop ที่ scaffold + spec → human dev เขียน
   - Option C: ใช้ Aider / Cline / Cursor agent

2. **Update existing project?** — หลังจาก v1 ส่ง user → user ขอเพิ่ม feature → flow ยังไง
   - ต้องมี "diff mode" — agent อ่าน existing repo + spec ใหม่ → patch

3. **Multi-tenancy** — หลาย user ใช้พร้อมกัน
   - Project-level isolation in workspace + Qdrant collection per project

4. **Customer support / debugging** — agent fail แล้ว user ถาม "ทำไม"
   - Langfuse trace + summarizer agent → ตอบใน chat

---

## 11. สรุป — Cheat Sheet

```
PATTERN:   Hierarchical Orchestrator-Workers + Eval-Optimizer
PHASES:    Analysis → Architecture → Design (parallel) → Scaffold
HITL:      หลัง analysis + architecture
LLMS:      Sonnet (smart) + Haiku (specialist) + Llama (cheap impl)
MEMORY:    File workspace + Qdrant project KB + global KB
ORCHESTR:  LangGraph (state + checkpoint + HITL)
COST:      ~$0.30-1 per project (with caching)
TIME:      1 สัปดาห์ MVP, 8 สัปดาห์ production
RISK:      ลด scope → file-only output, ไม่ generate code จริง
```

---

## Next Steps

1. อ่าน [deep_dive/01 LangGraph Patterns](deep_dive/01_LangGraph_Patterns.md) — สำหรับ implementation detail
2. อ่าน [deep_dive/02 Self-Hosted Stack](deep_dive/02_Self_Hosted_Stack.md) — Docker compose ครบ
3. ลองทำ Tiny MVP (week 1-2) ก่อน — อย่าทำ full system ตั้งแต่แรก
4. Commit ทุก artifact ใน git — debug จาก history ได้

---

## References

- Anthropic, "How we built our multi-agent research system" (2025)
- LangGraph "Self-RAG" tutorial (parallel + reviewer pattern)
- "v0.dev" / "bolt.new" — production examples ของ AI builder agent
- Aider / Continue.dev — open source coding agent reference
