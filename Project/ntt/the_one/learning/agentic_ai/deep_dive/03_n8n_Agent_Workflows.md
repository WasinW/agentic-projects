# Deep Dive 03 — n8n Agent Workflows

> สร้าง agent flow แบบ low-code ใน n8n + เมื่อไหร่เหมาะ / ไม่เหมาะ
> รวม pattern จริงและ limitation

---

## 1. n8n คืออะไร (Refresher)

- Open source workflow automation (Apache 2.0 + Sustainable Use License)
- Visual editor (drag-drop nodes)
- 400+ integrations (Slack, Gmail, GSheet, DB, ฯลฯ)
- AI nodes built-in (LangChain.js wrapped)
- Self-host ได้ ฟรี (Community Edition)

ต่างจาก pure no-code: รองรับ Code node (JS/Python) — เขียน custom logic ได้

---

## 2. n8n AI Nodes ที่ต้องรู้

### 2.1 AI Agent (Tools Agent)

Core node สำหรับ agent — รับ:
- Chat Model (sub-node)
- Tools (sub-node ↔ multiple)
- Memory (optional sub-node)
- Output Parser (optional)

```
   ┌──────────────────────────────────────┐
   │            AI Agent                  │
   │  ┌────────────┐                      │
   │  │ Chat Model │  ← Anthropic/OpenAI/Ollama
   │  └────────────┘                      │
   │  ┌────────────┐ ┌────────────┐       │
   │  │ Tool 1     │ │ Tool 2     │ ...   │
   │  └────────────┘ └────────────┘       │
   │  ┌────────────┐                      │
   │  │ Memory     │                      │
   │  └────────────┘                      │
   └──────────────────────────────────────┘
```

### 2.2 Common AI Nodes

| Node | ทำอะไร |
|---|---|
| **AI Agent** | Tool-using agent (ReAct) |
| **Basic LLM Chain** | Single LLM call |
| **Question and Answer Chain** | RAG basic |
| **Summarization Chain** | สรุป |
| **Information Extractor** | Extract structured data |
| **Text Classifier** | Classify text |

### 2.3 Tool Nodes (สำหรับ Agent)

| Tool | ทำอะไร |
|---|---|
| **HTTP Request Tool** | call REST API ใดๆ |
| **Code Tool** | run JS/Python |
| **Workflow Tool** | call sub-workflow |
| **Calculator Tool** | math |
| **Wikipedia Tool** | search wiki |
| **Vector Store Tool** | RAG over vector store |
| **MCP Client Tool** | use MCP server (recently added) |

### 2.4 Memory Nodes

| Memory | ทำอะไร |
|---|---|
| **Window Buffer Memory** | last N messages (in-process) |
| **Postgres Chat Memory** | persistent in Postgres |
| **Redis Chat Memory** | Redis-backed |
| **MongoDB Chat Memory** | Mongo-backed |

### 2.5 Vector Store Nodes

- **Qdrant Vector Store** ✅ (แนะนำ)
- **Pinecone**
- **Supabase Vector Store**
- **PGVector**
- **In-Memory Vector Store** (dev only)

---

## 3. Pattern 1: Simple Chatbot with RAG

```
┌────────────┐    ┌────────────┐    ┌────────────┐
│ Webhook    │───▶│ AI Agent   │───▶│ Respond    │
│ (chat input│    │            │    │ (chat reply│
└────────────┘    └─────┬──────┘    └────────────┘
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
  ┌─────────┐    ┌────────────┐   ┌─────────────┐
  │ Claude  │    │ Qdrant     │   │ Postgres    │
  │ Sonnet  │    │ Vector     │   │ Chat Memory │
  └─────────┘    │ Store Tool │   └─────────────┘
                 └────────────┘
```

**Setup**:
1. Create webhook trigger (or chat trigger)
2. Add AI Agent node
3. Connect Anthropic Chat Model (sub)
4. Add Qdrant Vector Store Tool (sub)
5. Add Postgres Chat Memory (sub)
6. Respond to webhook

**Use case**: customer support chatbot, internal Q&A

---

## 4. Pattern 2: Multi-Source Research Agent

```
                ┌────────────────┐
   Trigger ────▶│   AI Agent     │────▶ Output (email/slack)
                └───────┬────────┘
                        │ tools:
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
  ┌─────────┐    ┌────────────┐   ┌─────────────┐
  │ Tavily  │    │  HTTP Tool │   │ Workflow    │
  │ Search  │    │  (Wikipedia│   │ Tool        │
  │ HTTP    │    │   /Arxiv)  │   │ (sub-flow)  │
  └─────────┘    └────────────┘   └─────────────┘
```

**Tip**: Use **Workflow Tool** เป็น "sub-agent" — เปิดทาง multi-agent

---

## 5. Pattern 3: Multi-Agent (Workflow Tool Pattern)

n8n ไม่มี native multi-agent → ใช้ Workflow Tool เป็น proxy

```
[Coordinator Workflow]
       │
       ▼
   ┌──────────┐
   │ AI Agent │
   │ "Coord"  │
   └────┬─────┘
        │ tools:
        ├──▶ [Workflow Tool] → calls "Researcher Workflow"
        ├──▶ [Workflow Tool] → calls "Writer Workflow"
        └──▶ [Workflow Tool] → calls "Reviewer Workflow"

[Researcher Workflow]            [Writer Workflow]            [Reviewer Workflow]
      │                                 │                            │
      ▼                                 ▼                            ▼
  ┌──────────┐                   ┌──────────┐                ┌──────────┐
  │ AI Agent │                   │ AI Agent │                │ AI Agent │
  │"Research"│                   │ "Writer" │                │"Reviewer"│
  └──────────┘                   └──────────┘                └──────────┘
```

### How

1. สร้าง 3 sub-workflows: `researcher`, `writer`, `reviewer`
   - Each: trigger ด้วย "Execute Workflow Trigger" → AI Agent → return result
2. ใน main workflow: AI Agent มี 3 Workflow Tools ชี้ไป sub-workflows
3. Coordinator agent ตัดสินใจเรียก workflow ไหน

**ข้อจำกัด**:
- ❌ Sub-workflows คุยกันโดยตรงไม่ได้ (มี coordinator เป็นกลาง)
- ❌ Stateful debate (group chat) — ทำได้แต่ messy
- ⚠️ Trace cross-workflow ลำบาก — ต้อง pass thread_id เอง

---

## 6. Pattern 4: Approval Flow (HITL)

```
┌────────────┐    ┌─────────┐    ┌──────────┐    ┌──────────────┐
│  Trigger   │───▶│  AI     │───▶│ Approve  │───▶│ Execute (or  │
│            │    │ Agent   │    │ Wait     │    │ cancel)      │
└────────────┘    │ (plan)  │    │ (Slack)  │    └──────────────┘
                  └─────────┘    └──────────┘
                                       │
                                  Slack message:
                                  "Approve [✅] [❌]"
```

**Implementation**:
- AI Agent generates plan
- "Slack" node sends message with buttons
- "Wait for approval" node pauses workflow
- Buttons trigger callback → resume workflow

n8n มี node `Wait` + Slack interactive — ทำได้ตรงๆ

---

## 7. Pattern 5: Scheduled Agent

```
┌──────────┐    ┌────────────┐    ┌──────────┐
│ Schedule │───▶│  AI Agent  │───▶│ Action   │
│ (cron)   │    │            │    │          │
└──────────┘    └────────────┘    └──────────┘
```

**Use case**: 
- Daily report generator
- Weekly newsletter
- Hourly competitor monitoring

---

## 8. Code Node — Custom Logic

n8n ไม่มี node ทุกอย่าง — Code node เติมเต็ม

```javascript
// JavaScript (default)
const items = $input.all();
const result = items.map(item => {
    return {
        json: {
            ...item.json,
            processed: true,
            wordCount: item.json.text.split(' ').length,
        }
    };
});
return result;
```

```python
# Python
import json
texts = [item['json']['text'] for item in items]
output = []
for t in texts:
    output.append({'json': {'text': t, 'words': len(t.split())}})
return output
```

**Tip**: Code node ดี แต่ถ้าใช้เกิน 30% ของ workflow → ควร migrate ไป LangGraph

---

## 9. Embedding & Vector Store ใน n8n

### Setup Qdrant

1. Add credentials: Qdrant → URL `http://qdrant:6333` (if Docker network)
2. Add embeddings credential: choose provider (Ollama/OpenAI/etc)

### Index documents (one-off workflow)

```
[Read Files] → [Document Loader] → [Text Splitter] → [Embeddings] → [Qdrant Insert]
```

### Query (in agent)

ใช้ **Qdrant Vector Store Tool** ใน AI Agent — agent retrieves automatically

---

## 10. n8n + MCP

n8n รองรับ MCP servers ผ่าน MCP Client Tool node (recently added)

**Setup**:
1. Add MCP Client Tool ใน AI Agent
2. Configure: command + args (เช่น `npx @modelcontextprotocol/server-filesystem /workspace`)
3. Agent เห็น tools ทั้งหมดที่ MCP server expose

**ผลกระทบ**: ทุก MCP server (1000+ ตัว) → plug เข้า n8n ได้เลย

---

## 11. n8n Limitations สำหรับ Agent

### ❌ ไม่เหมาะ

#### LL1: State machine ซับซ้อน
- LangGraph มี explicit state — n8n ไม่มี
- ใช้ "set" / "merge" node ปะติดปะต่อ → messy

#### LL2: Conditional loop ยาว
- n8n มี loop nodes (Loop Over Items, Split In Batches) แต่ control flow ที่ซับซ้อน → ต้องเขียน Code

#### LL3: Multi-agent ที่ต้อง share state
- Sub-workflows independent — pass state ผ่าน input/output
- ไม่มี shared "checkpoint" แบบ LangGraph

#### LL4: Production trace
- Built-in execution log แต่ search/filter ลำบาก
- ต้องส่ง webhook ไป external (Langfuse) เอง

#### LL5: Version control
- Workflows เก็บใน DB → export JSON ↔ git
- Diff JSON ไม่สวย

### ✅ เหมาะ

#### Good 1: Glue automation
- "Slack message → AI extract intent → call ERP API → reply"
- Single-agent flow ที่มี integration เยอะ

#### Good 2: Scheduled jobs
- Daily/weekly automation
- Easier กว่าเขียน cron + script

#### Good 3: Internal tools demo
- Stakeholder เห็น flow ได้ → review ง่าย
- Modify ไม่ต้อง dev

#### Good 4: Quick prototype
- 30 min ทำ working demo

---

## 12. Workflow ตัวอย่างจริง

### Example A: Slack Bot ตอบคำถาม KB

```
Trigger: Slack message (mention @bot)
   │
   ▼
AI Agent (Anthropic Haiku)
  - Tools: Qdrant Vector Store (KB), HTTP (Tavily search)
  - Memory: Postgres (per channel)
   │
   ▼
Slack Send Reply
```

**Cost**: $5-20/mo Haiku + free n8n self-host
**Time to build**: 1-2 hours

---

### Example B: Lead Triage

```
Trigger: Webhook (form submit)
   │
   ▼
Information Extractor (Gemini Flash)
   - Extracts: name, company, intent, urgency
   │
   ▼
Switch (route by urgency)
   ├── high → Slack #sales-urgent
   ├── medium → Add to CRM (HubSpot node)
   └── low → Email autoresponder
```

---

### Example C: Document Processor

```
Trigger: Drive new file
   │
   ▼
Read PDF → Text
   │
   ▼
AI Agent (Sonnet)
   - Tools: Code (parse), HTTP (validate against API)
   - Output Parser: structured JSON
   │
   ▼
Postgres Insert
```

---

### Example D: Daily Competitor Watch

```
Trigger: Cron (daily 9am)
   │
   ▼
HTTP (fetch competitor sites)
   │
   ▼
AI Agent (Haiku) — extract changes
   │
   ▼
Compare with last run (Postgres)
   │
   ▼
If changed → AI Agent (Sonnet) summarize → Email digest
```

---

## 13. Performance & Limits

- **Single execution**: default timeout 5 min (configurable)
- **Concurrent executions**: depends on `EXECUTIONS_PROCESS=main` vs `own`
- **DB**: Postgres recommended for production
- **Memory**: Workflow data ทั้งหมด in-memory → big payloads → OOM

### Scaling

```yaml
# docker-compose
services:
  n8n-worker:
    image: n8nio/n8n
    environment:
      EXECUTIONS_MODE: queue  # offload to workers
    deploy:
      replicas: 3
  
  redis:
    image: redis  # broker
```

---

## 14. n8n vs Code (LangGraph) — Decision

| Criteria | n8n | LangGraph |
|---|---|---|
| Time to first workflow | 30 min | 4 hours |
| Complex state machine | ❌ | ✅ |
| HITL | ✅ via Wait | ✅ via interrupt |
| Multi-agent | 🟡 via sub-workflow | ✅ native |
| Trace/eval | 🟡 manual | ✅ rich |
| Version control | 🟡 JSON in git | ✅ Python |
| Non-dev maintains | ✅ | ❌ |
| 400+ integrations | ✅ | ❌ build yourself |
| Cost-control granular | 🟡 | ✅ |
| Test coverage | ❌ | ✅ |

### Hybrid pattern

ใช้ **ทั้งสอง** — แต่ละตัวที่มันเก่ง:

```
n8n: webhook receiver, integrations, scheduling
   │
   ▼
HTTP request → LangGraph service (Docker container)
   │
   ▼ (after agent processing)
n8n: response routing, notifications
```

n8n เป็น "API gateway + orchestrator", LangGraph เป็น "agent brain"

---

## 15. ทำ Case Study (จาก 07) ใน n8n ได้มั้ย?

ตอบ: ทำได้ **บางส่วน** แต่ไม่แนะนำ

**ถ้าจะทำใน n8n**:

```
Main Workflow (Coordinator):
   AI Agent (Sonnet)
     - Tool: Workflow → "Analyst Workflow"
     - Tool: Workflow → "Architect Workflow"
     - Tool: Workflow → "Designers Parallel Workflow"
        - calls 4 sub-workflows internally
     - Tool: Workflow → "Reviewer Workflow"
     - Tool: Workflow → "Scaffold Workflow"
   - Memory: Postgres (per project_id)
```

**ปัญหา**:
- HITL ใน multi-step ยาก (ต้อง wait nodes ซ้อนกัน)
- State sharing ระหว่าง sub-workflows = file system / Postgres → ไม่ atomic
- Cost monitoring per phase = ต้อง logging ส่งไป Langfuse เอง
- Reviewer loop กลับ → conditional ใน n8n หลายชั้น = tangled

**สรุป**: prototype ได้, production ใช้ LangGraph

---

## 16. Migration Path: n8n → Code

ถ้าเริ่มที่ n8n แล้วโตจน complex:

```
Step 1: เริ่ม n8n prototype
Step 2: identify "ส่วนที่ซับซ้อน" → ย้ายเป็น LangGraph service
Step 3: n8n เรียก LangGraph ผ่าน HTTP
Step 4: เมื่อ n8n เหลือแค่ glue → migrate full ถ้า cost-effective
```

ไม่ต้อง all-or-nothing

---

## 17. Tips & Tricks

### T1: Pin Node Output for testing
- Right-click node → "Pin Output"
- Workflow รันเร็วขึ้น (ไม่ call API ทุกครั้ง)

### T2: Set node สำหรับ debugging
- Add "Set" node กลาง flow → see data state

### T3: Error workflow
- Settings → "Error Workflow" → ทุก error trigger workflow นี้
- Send to Slack/PagerDuty

### T4: Webhook authentication
- Use "Header Auth" → require API key
- หรือ HMAC signature

### T5: Sub-workflow as reusable component
- Same logic ใช้หลายที่ → factor เป็น sub-workflow
- Version it carefully

### T6: Caching expensive AI calls
- Use Postgres node before AI Agent
- Hash input → check cache → skip AI ถ้า hit

---

## 18. Resources

- [n8n docs](https://docs.n8n.io/)
- [n8n AI](https://n8n.io/ai/)
- [Templates gallery](https://n8n.io/workflows/) — copy-paste ready
- [n8n + LangChain blog](https://blog.n8n.io/category/ai/) — official tutorials
- Community Discord — ตอบเร็ว

---

## 19. สรุป

- n8n = **automation platform with AI**, not pure agent platform
- ดีสำหรับ glue + scheduled + integration
- ไม่เหมาะสำหรับ multi-agent ที่ซับซ้อน, state machine, HITL หลายชั้น
- Pattern หลัก: Single AI Agent + tools / sub-workflows
- Hybrid กับ LangGraph = best of both worlds
- **Verdict for your case study**: prototype ได้ใน 1 วัน, production ใช้ LangGraph

---

## References

- [n8n Self-Host on Docker](https://docs.n8n.io/hosting/installation/docker/)
- [n8n AI Agent docs](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/)
- [Workflow Tool pattern](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolworkflow/)
- [Templates: AI workflows](https://n8n.io/workflows/categories/ai/)
