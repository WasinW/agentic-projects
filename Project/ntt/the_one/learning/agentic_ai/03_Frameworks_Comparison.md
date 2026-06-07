# 03 — Frameworks Comparison

> เลือก framework ที่เหมาะกับงาน — code-first vs low-code, control vs convenience
> ตัวที่อยู่ในวงการจริงปี 2026

---

## 0. Big Picture

```
                   AGENTIC AI FRAMEWORKS
                          │
         ┌────────────────┴───────────────┐
         │                                │
    CODE-FIRST                       LOW-CODE / NO-CODE
         │                                │
   ┌─────┼─────┬──────┬──────┐       ┌────┼────┬─────┬─────┐
   ▼     ▼     ▼      ▼      ▼       ▼    ▼    ▼     ▼     ▼
LangGraph LangChain  CrewAI AutoGen Pydantic  n8n  Flowise Dify Langflow
                              ↓        AI                        │
                         (deprecated  Claude Agent SDK            │
                          for new     OpenAI Agents SDK         (open source
                          projects)                              UI builder)
```

ก่อนจะเลือก — ตอบคำถามนี้:

| คำถาม | ผลกระทบ |
|---|---|
| ทีมเขียน code ได้มั้ย? | ถ้าไม่ → low-code |
| Production-grade? | ใช่ → LangGraph / Pydantic AI / SDK ของ vendor |
| Multi-agent? | ใช่ → CrewAI / AutoGen / LangGraph |
| Need state machine? | ใช่ → LangGraph |
| Quick prototype? | low-code (n8n, Flowise) หรือ CrewAI |
| งบ = 0 self-host? | n8n (community) / Flowise / Dify ฟรี |

---

## 1. Code-First Frameworks

### 1.1 LangGraph (LangChain ecosystem)

**Approach**: State graph — explicit state machine

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class State(TypedDict):
    messages: list
    plan: list
    results: dict
    next_action: str

def planner(state: State) -> State:
    plan = llm.invoke(f"Plan for: {state['messages'][-1]}")
    return {"plan": parse_plan(plan), "next_action": "execute"}

def executor(state: State) -> State:
    step = state["plan"].pop(0)
    result = run_tool(step)
    state["results"][step.id] = result
    state["next_action"] = "execute" if state["plan"] else "synthesize"
    return state

def synthesize(state: State) -> State:
    answer = llm.invoke(f"Synthesize: {state['results']}")
    return {"messages": state["messages"] + [answer], "next_action": "end"}

g = StateGraph(State)
g.add_node("planner", planner)
g.add_node("executor", executor)
g.add_node("synthesize", synthesize)

g.set_entry_point("planner")
g.add_conditional_edges("executor",
    lambda s: s["next_action"],
    {"execute": "executor", "synthesize": "synthesize"})
g.add_edge("synthesize", END)

app = g.compile(checkpointer=MemorySaver())
```

**Pros**:
- ✅ Explicit state — debug ง่าย, audit trail ครบ
- ✅ Built-in checkpointing — pause/resume/time-travel
- ✅ Human-in-the-loop รองรับดี
- ✅ Production proven (Uber, LinkedIn ใช้)

**Cons**:
- ❌ Verbose
- ❌ Learning curve
- ❌ ไม่เหมาะ quick prototype

**ใช้เมื่อ**: production agent, complex workflow, ต้องการ control ทุก state transition

---

### 1.2 LangChain (Legacy)

> **2026 status**: ใช้น้อยลงในงานใหม่ — community แนะนำ LangGraph แทน
> 
> LangChain ยังมีประโยชน์เป็น **utility library** — chains, output parsers, integrations 200+ providers

**ห้ามทำ**: เริ่ม project ใหม่ด้วย `langchain.agents.AgentExecutor` — ตัวนี้ deprecated

---

### 1.3 CrewAI

**Approach**: Role-based (DSL-style)

```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Senior Researcher",
    goal="Find latest info on {topic}",
    backstory="Expert in tech research...",
    tools=[search_tool],
    llm=ChatOpenAI(model="gpt-4o-mini"),
)

writer = Agent(
    role="Tech Writer",
    goal="Write engaging blog posts",
    backstory="10+ years writing about AI",
    tools=[],
    llm=ChatAnthropic(model="claude-haiku-4-5-20251001"),
)

research_task = Task(
    description="Research {topic} thoroughly",
    expected_output="Markdown report with sources",
    agent=researcher,
)
write_task = Task(
    description="Write blog post from research",
    expected_output="800-word blog post",
    agent=writer,
    context=[research_task],
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process="sequential",  # หรือ "hierarchical"
    verbose=True,
)
result = crew.kickoff(inputs={"topic": "AI in 2026"})
```

**Pros**:
- ✅ Easy mental model (role/goal/backstory)
- ✅ Built-in memory (short + long term)
- ✅ Sequential และ hierarchical process
- ✅ Quick prototype สวย

**Cons**:
- ❌ Production audit ยากกว่า LangGraph
- ❌ Less flexible (DSL บังคับ structure)
- ⚠️ Hierarchical mode ใช้ manager agent ภายในที่ control ยาก

**ใช้เมื่อ**: business workflow, content generation, prototype

---

### 1.4 AutoGen (Microsoft)

**Approach**: Conversational multi-agent

```python
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

planner = AssistantAgent(name="Planner", system_message="You plan tasks")
coder = AssistantAgent(name="Coder", system_message="You write code")
reviewer = AssistantAgent(name="Reviewer", system_message="You review code")

user_proxy = UserProxyAgent(
    name="User",
    code_execution_config={"work_dir": "out"},
    human_input_mode="NEVER",
)

groupchat = GroupChat(
    agents=[user_proxy, planner, coder, reviewer],
    messages=[],
    max_round=12,
)
manager = GroupChatManager(groupchat=groupchat)
user_proxy.initiate_chat(manager, message="Build a Flask todo app")
```

**Pros**:
- ✅ Multi-agent คุยกัน natural ที่สุด
- ✅ Code execution sandbox มาให้
- ✅ Microsoft-backed, active development
- ✅ AutoGen v0.4+ ใช้ event-driven (ดีกว่ารุ่นเก่า)

**Cons**:
- ❌ Tools manual (ไม่มี library tool เยอะ)
- ❌ "Group chat" อาจ token explode
- ⚠️ Production deployment ต้อง self-build observability

**ใช้เมื่อ**: code generation, multi-agent debate, research prototypes

---

### 1.5 Pydantic AI

**Approach**: Type-safe, lightweight (เหมือน FastAPI สำหรับ agent)

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class WeatherResult(BaseModel):
    temperature_c: float
    condition: str

agent = Agent(
    "claude-sonnet-4-6",
    result_type=WeatherResult,
    system_prompt="You are a weather assistant.",
)

@agent.tool
async def get_weather(ctx, location: str) -> str:
    # call API
    return "..."

result = await agent.run("Weather in Tokyo")
print(result.data.temperature_c)  # type-safe!
```

**Pros**:
- ✅ Type safety — return type ถูก validate
- ✅ Lightweight, dependency น้อย
- ✅ Async-native
- ✅ Maintained โดย Pydantic team (trustworthy)

**Cons**:
- ❌ ใหม่กว่า ecosystem เล็กกว่า
- ❌ Multi-agent ต้องประกอบเอง

**ใช้เมื่อ**: ต้องการ structured output, FastAPI-style codebase, type safety

---

### 1.6 Vendor SDKs

#### Claude Agent SDK (Anthropic)
- เหมาะกับ Claude API users
- มี `computer_use`, `code_execution`, `web_search` tools built-in
- File operations, bash tools — ทำ coding agent ได้เลย
- ใช้กับ Claude models ดีที่สุด

#### OpenAI Agents SDK
- เหมาะกับ OpenAI users
- มี handoffs, guardrails, tracing built-in
- รองรับ multi-agent pattern ออกแบบมาดี
- เปิดตัวต้นปี 2025 — production-ready

#### Google ADK (Agent Development Kit)
- สำหรับ Gemini models
- Integrate กับ Vertex AI / Google Cloud
- รองรับ ADK, A2A protocol

**ใช้เมื่อ**: ทีมล็อกกับ vendor ใดเฉพาะ → ใช้ SDK ของเขาเป็น first-class

---

## 2. Low-Code / No-Code Platforms

### 2.1 n8n

**Approach**: Visual workflow builder (drag & drop)

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Webhook     │─────▶│ AI Agent     │─────▶│ Send Email   │
│  Trigger     │      │ (LangChain)  │      │              │
└──────────────┘      └──────┬───────┘      └──────────────┘
                             │
                  ┌──────────┼──────────┐
                  ▼          ▼          ▼
            ┌────────┐ ┌────────┐ ┌──────────┐
            │ Tool 1 │ │ Tool 2 │ │ Memory   │
            │(HTTP)  │ │(Code)  │ │(Postgres)│
            └────────┘ └────────┘ └──────────┘
```

**Pros**:
- ✅ ฟรี (community edition self-host) / pricing $20/mo cloud
- ✅ 400+ integrations (Slack, Gmail, Google Sheets, ฯลฯ)
- ✅ มี "AI Agent" node เป็น first-class (LangChain.js inside)
- ✅ Webhook + cron + manual trigger
- ✅ ดีมากสำหรับ glue งาน automation
- ✅ Self-host ได้ ง่ายมาก (1 docker run)

**Cons**:
- ❌ Multi-agent ออกแบบยาก (มี sub-workflow แต่ debug ยาก)
- ❌ Version control ผ่าน git ทำได้แต่ไม่ smooth
- ❌ Custom logic ซับซ้อน → ยังต้องเขียน code (Code node)
- ⚠️ Workflow ใหญ่ขึ้นเร็ว — visual messy

**ใช้เมื่อ**:
- Glue งาน automation (Slack → AI → Notion)
- Single-agent workflow ไม่ซับซ้อนมาก
- ทีมมี non-developer ที่ต้อง build เอง

> รายละเอียด n8n agent flows อยู่ที่ [deep_dive/03](deep_dive/03_n8n_Agent_Workflows.md)

---

### 2.2 Flowise

**Approach**: LangChain.js wrapped in visual builder

**Pros**:
- ✅ Open source, free
- ✅ LangChain features → expose ใน UI
- ✅ Multi-agent ผ่าน "Agentflow"
- ✅ Self-host ง่าย

**Cons**:
- ❌ Production stability น้อยกว่า n8n
- ❌ Community เล็กกว่า

**ใช้เมื่อ**: prototype RAG / agent UI สำหรับ demo / non-technical users

---

### 2.3 Dify

**Approach**: AI app platform (LLM ops + agent + workflow + RAG ใน 1 platform)

**Pros**:
- ✅ All-in-one: chatbot UI + RAG + agent + analytics
- ✅ Open source (มี cloud version ด้วย)
- ✅ Built-in observability + cost tracking
- ✅ Workflow editor + agent mode

**Cons**:
- ❌ Opinionated — ออกนอก paradigm ยาก
- ❌ ไม่เหมาะ embed agent ใน app ที่ซับซ้อน

**ใช้เมื่อ**: build AI chatbot product แบบ standalone, internal tools

---

### 2.4 Langflow

**Approach**: คล้าย Flowise — LangChain visual

ความแตกต่างหลัก: Backed by Datastax, integration กับ Astra DB ดี

**ใช้เมื่อ**: ใช้ DataStax/Astra DB อยู่แล้ว

---

## 3. Comparison Matrix

| Framework | Type | Multi-agent | State mgmt | Production | Free? | Learning curve |
|---|---|---|---|---|---|---|
| **LangGraph** | Code | ✅ Excellent | ✅ Explicit | ✅ Yes | ✅ OSS | High |
| **CrewAI** | Code | ✅ Good | 🟡 Hidden | 🟡 OK | ✅ OSS | Low |
| **AutoGen** | Code | ✅ Excellent | 🟡 Convo | 🟡 OK | ✅ OSS | Medium |
| **Pydantic AI** | Code | 🟡 Manual | ✅ Type-safe | ✅ Yes | ✅ OSS | Low |
| **Claude Agent SDK** | Code | 🟡 Manual | ✅ Yes | ✅ Yes | 🟡 API cost | Low |
| **OpenAI Agents SDK** | Code | ✅ Excellent | ✅ Yes | ✅ Yes | 🟡 API cost | Low |
| **n8n** | Visual | 🟡 Limited | 🟡 Per node | ✅ Yes | ✅ OSS (CE) | Low |
| **Flowise** | Visual | ✅ Good | 🟡 Limited | 🟡 Beta | ✅ OSS | Low |
| **Dify** | Visual | ✅ Good | ✅ Built-in | ✅ Yes | ✅ OSS | Low |

---

## 4. Decision Matrix — ฉันควรใช้อะไร?

```
                   ทีมเขียน code ได้มั้ย?
                            │
            ┌───────────────┴───────────────┐
            │ NO                            │ YES
            ▼                               ▼
    ┌──────────────┐                ต้องการ multi-agent?
    │  LOW-CODE    │                        │
    └───────┬──────┘                ┌───────┴───────┐
            │                       │NO             │YES
   มี tool list ของ                 ▼               ▼
   workflow มาก?            ต้องการ state explicit?  │
            │                       │               │
   ┌────────┴────┐            ┌─────┴─────┐         │
   │YES         │NO            │YES         │NO     │
   ▼            ▼              ▼           ▼        ▼
  n8n      Dify/Flowise    LangGraph  Pydantic   ต้อง state explicit?
                                       AI            │
                                                ┌────┴────┐
                                                │YES       │NO
                                                ▼          ▼
                                            LangGraph   CrewAI หรือ AutoGen
                                                        ขึ้นกับ paradigm
```

---

## 5. Real-World Recipes

### Recipe 1: Internal Tool — Slack bot ตอบ KB
```
Stack: n8n + Anthropic + Qdrant
- Trigger: Slack message
- Step 1: Embed query
- Step 2: Search Qdrant
- Step 3: AI Agent node (RAG context)
- Step 4: Reply Slack
Cost: ~$5-20/mo (n8n self-host) + Anthropic per token
```

### Recipe 2: Research Agent (Anthropic-style)
```
Stack: LangGraph + Tavily/Exa + Claude
- Orchestrator (Sonnet)
- 3-5 parallel sub-agents (Haiku, each with limited tools)
- Aggregator (Sonnet)
Cost: $0.10-0.50 per query (heavy)
```

### Recipe 3: Coding Agent (cursor-like)
```
Stack: Claude Agent SDK + custom tools
- Tools: read_file, write_file, run_bash, git
- Loop with max_iterations
Cost: $0.50-5 per task (depends on repo size)
```

### Recipe 4: Customer Support
```
Stack: Dify + GPT-5-mini + FAQ vector store
- Chat UI built-in
- Routing: tier 1 (FAQ) → tier 2 (specialist) → escalate
- Analytics built-in
Cost: $20/mo Dify cloud + LLM
```

### Recipe 5: Multi-step Workflow ที่ user ของเราอยากทำ
```
Stack: LangGraph + Claude + Qdrant + Ollama (cheap model สำหรับ codegen)
- Coordinator (Claude Sonnet)
- Specialists (Claude Haiku + cached prompts)
- Implementers (DeepSeek/Llama via Ollama — ฟรี)
- Memory: Qdrant
Cost: $0.10-2 per project (mostly Sonnet calls)
```

---

## 6. Common Mistakes ที่ต้องระวัง

### ❌ "เลือก framework ก่อนเข้าใจปัญหา"
LangGraph > CrewAI โดย "rule" ไม่จริง — งานต่างกัน

### ❌ "ใช้ low-code → production scale"
n8n สำหรับ ≤ 100 workflow runs/day ดี — สเกล 10K+ ขอ go code

### ❌ "Multi-agent เพราะ cool"
2 agent ดีกว่า 5 agent ที่ confused

### ❌ "ไม่ใส่ observability ตั้งแต่ต้น"
Agent debug ยากมาก — ติด tracing ตั้งแต่ day 1 (Langfuse / LangSmith)

### ❌ "ลืม version control"
n8n / Flowise — workflow ต้อง export → commit ใน git ไม่งั้นหายเรียบ

---

## 7. Recommendation สำหรับคุณ

จาก use case ที่บอกมา (e-commerce builder agent + ราคาเบาๆ):

### Phase 1 (Prototype, week 1-2)
- **CrewAI** — เริ่ม role-based ง่าย
- **Free tier**: Gemini 2.5 Flash + Groq Llama 3.3
- **No vector DB ก่อน** — ใช้ in-memory dict

### Phase 2 (Refine, week 3-4)
- ย้าย → **LangGraph** เมื่อ flow ซับซ้อนขึ้น
- เพิ่ม **Qdrant** local (Docker)
- เพิ่ม **Langfuse** observability

### Phase 3 (Production, month 2+)
- LangGraph + checkpointing
- Hybrid model: Claude Sonnet สำหรับ planning, Haiku/Llama สำหรับ work
- Monitor cost/quality ใน Langfuse

ห้ามทำ:
- ❌ เริ่ม LangGraph เลย — verbose มาก จะท้อ
- ❌ AutoGen — token explode ง่าย คุมยาก
- ❌ n8n สำหรับ multi-agent ที่ซับซ้อน — ออกแบบยาก

---

## สรุป

- **Code-first**: LangGraph (production), CrewAI (prototype), Pydantic AI (type-safe)
- **Vendor SDKs**: ใช้ถ้าล็อก vendor — ลึกที่สุด
- **Low-code**: n8n (automation), Dify (chatbot), Flowise (RAG)
- **เลือกตาม**: ทีม / scale / control / state machine
- **เริ่มเล็ก** → ย้ายไป framework ที่ powerful ขึ้นเมื่อจำเป็น

**ต่อไป** → [04 Tools & Selection](04_Tools_and_Selection.md) — ออกแบบ tool ให้ agent ใช้ได้ดี

---

## References

- [LangGraph docs](https://langchain-ai.github.io/langgraph/)
- [CrewAI docs](https://docs.crewai.com/)
- [AutoGen docs](https://microsoft.github.io/autogen/)
- [Pydantic AI docs](https://ai.pydantic.dev/)
- [n8n AI nodes](https://n8n.io/integrations/categories/ai/)
- [Dify](https://dify.ai/)
