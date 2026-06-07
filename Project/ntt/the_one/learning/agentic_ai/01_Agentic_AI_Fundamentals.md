# 01 — Agentic AI Fundamentals

> เข้าใจ "agent" จริงๆ คืออะไร, ต่างจาก workflow / chatbot ยังไง, เมื่อไหร่ควรใช้
> ก่อนเขียน code อะไร — ต้องเข้าใจอันนี้ก่อน ไม่งั้น over-engineer แน่ๆ

---

## 1. Agent vs Chatbot vs Workflow

นี่คือสิ่งที่คนสับสนมากสุด เพราะหลายคนเรียก "agent" หมดทุกอย่างที่มี LLM

### นิยามที่ใช้ใน 2026 (ตาม Anthropic / OpenAI)

```
┌─────────────────────────────────────────────────────────────┐
│                     LLM SYSTEMS                              │
├─────────────────────┬───────────────────────────────────────┤
│   WORKFLOWS         │           AGENTS                      │
│  (deterministic)    │       (autonomous)                    │
├─────────────────────┼───────────────────────────────────────┤
│ - Path กำหนดไว้ก่อน │ - LLM ตัดสินใจ next step เอง          │
│ - Predictable      │ - Open-ended                          │
│ - Cheap            │ - Expensive                           │
│ - Reliable         │ - Compound failures                   │
└─────────────────────┴───────────────────────────────────────┘
```

**Workflow** = LLM ที่ถูก orchestrate ผ่าน code ที่กำหนดไว้
- เช่น "extract entity → classify → save to DB" — เราเขียน flow ไว้แล้ว
- LLM ทำงาน 1 step ต่อรอบ ไม่ได้ตัดสินใจว่าจะไปไหนต่อ

**Agent** = ระบบที่ใช้ LLM **ตัดสินใจเองว่าทำอะไรต่อ** ในแต่ละ step
- มี loop: think → act → observe → think → ...
- ไม่รู้ล่วงหน้าว่าจะใช้ tool กี่ครั้ง

**Chatbot** = LLM ที่ตอบกลับ user — อาจเป็น workflow หรือ agent ก็ได้
- "Pure chatbot" คือ LLM call ครั้งเดียวต่อ message — **ไม่ใช่ agent**

### ตัวอย่างเปรียบเทียบ

| Use Case | ประเภท | เหตุผล |
|---|---|---|
| Customer FAQ bot (RAG → ตอบ) | Workflow | flow ตายตัว: search → answer |
| Email classifier (LLM → label) | Workflow | 1 step |
| Research assistant ค้นข้อมูลตอบ | **Agent** | ไม่รู้ต้อง search กี่รอบ |
| Code agent แก้ bug ใน repo | **Agent** | อ่านไฟล์ → แก้ → run test → ลูป |
| Invoice OCR → กรอก ERP | Workflow | flow ตายตัว |
| "Plan vacation to Tokyo" | **Agent** | ต้อง search หลายอย่าง → reason → book |

### กฎแม่บท (Anthropic's "Building Effective Agents", 2024)

> **Start with a workflow. Add agency only when needed.**

เพราะ agent มี cost / latency / failure mode สูงกว่า workflow มาก ถ้างานคุณ deterministic ใช้ workflow ดีกว่า

---

## 2. Anatomy of an Agent

Agent ทุกตัวประกอบด้วย 4 ส่วน ไม่ว่าจะ framework ไหน:

```
                  ┌──────────────────────┐
                  │       GOAL           │
                  │  (สิ่งที่ user อยากได้) │
                  └──────────┬───────────┘
                             ▼
   ┌────────────────────────────────────────────────┐
   │                  THE LOOP                      │
   │                                                │
   │  ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐  │
   │  │ Plan │───▶│ Act  │───▶│Observe│──▶│Think │  │
   │  └──────┘    └──────┘    └──────┘    └───┬──┘  │
   │      ▲                                    │     │
   │      └────────────────────────────────────┘     │
   └────────────────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌───────────┐  ┌───────────┐  ┌───────────┐
       │   BRAIN   │  │   TOOLS   │  │  MEMORY   │
       │   (LLM)   │  │ (actions) │  │ (state)   │
       └───────────┘  └───────────┘  └───────────┘
```

### 2.1 Brain (LLM)

LLM ที่ทำหน้าที่:
- **Plan** — แตกงานเป็น sub-tasks
- **Reason** — คิดว่าจะทำอะไรต่อ
- **Decide** — เลือก tool / argument
- **Synthesize** — รวมผลลัพธ์เป็นคำตอบ

**ตัวเลือก** (2026):
- **Frontier**: Claude Opus 4.7, GPT-5, Gemini 2.5 Pro — เก่งสุด แต่แพง
- **Mid**: Claude Sonnet 4.6, GPT-5 mini, Gemini 2.5 Flash — sweet spot
- **Cheap**: Haiku 4.5, Gemini 2.5 Flash-Lite, Llama 3.3 70B (Groq) — เร็ว ถูก
- **Local**: Qwen 2.5 / Llama 3.3 / DeepSeek (Ollama) — ฟรี แต่กิน RAM

> ใน Agent ดีๆ คุณจะใช้ **หลายตัว** ไม่ใช่ตัวเดียว — เรื่องนี้อยู่ที่ 06

### 2.2 Tools (Actions)

อะไรที่ agent ทำได้บ้าง — เช่น:
- `search_web(query)`
- `read_file(path)`
- `run_python(code)`
- `query_database(sql)`
- `send_email(to, subject, body)`
- `call_other_agent(agent_name, task)`

**กฎทอง**: tool คือสิ่งที่ทำให้ agent มีพลังจริง — ไม่มี tool = agent ใช้แต่ความรู้ที่ฝัง LLM = ChatGPT ธรรมดา

> รายละเอียดการออกแบบ tool อยู่ที่ 04

### 2.3 Memory (State)

แบ่งเป็น 3 ระดับ:

```
┌────────────────────────────────────────────────────┐
│  WORKING MEMORY (in-context)                       │
│  - ข้อความใน conversation ปัจจุบัน                  │
│  - Scratchpad ของ agent                            │
│  - หายไปเมื่อจบ task                                │
└────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────┐
│  EPISODIC MEMORY (per-session, persistent)         │
│  - Log ของ session ก่อนๆ                           │
│  - "ครั้งก่อน user ขอ X เราทำ Y แล้วเขาชอบ"          │
└────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────┐
│  SEMANTIC MEMORY (knowledge base)                  │
│  - Vector DB / Knowledge graph                     │
│  - "Domain facts" "user preferences" "company SOP" │
└────────────────────────────────────────────────────┘
```

> รายละเอียดอยู่ที่ 05

### 2.4 The Loop

นี่คือสิ่งที่แยก agent จาก workflow:

```python
# Pseudocode — minimal agent loop
def agent(goal, tools, llm, max_steps=20):
    history = []
    for step in range(max_steps):
        # 1. Brain decides
        decision = llm.decide(goal, history, tools)
        
        # 2. Done?
        if decision.is_final_answer:
            return decision.answer
        
        # 3. Act
        tool_name = decision.tool
        args = decision.args
        result = tools[tool_name](**args)
        
        # 4. Observe → next iteration
        history.append({"action": decision, "result": result})
    
    raise Exception("Max steps reached")
```

ทั้งหมดของ agent system ที่ซับซ้อน → ก็คือ loop นี้นั่นแหละ มาเสริมด้วย:
- Multi-agent (loop ซ้อน loop)
- Memory (อ่าน/เขียน external state)
- Reflection (loop วิเคราะห์ตัวเอง)

---

## 3. เมื่อไหร่ควรใช้ Agent (และเมื่อไหร่ห้ามใช้)

### ✅ ควรใช้ agent เมื่อ

1. **งาน open-ended** — ไม่รู้จะมีกี่ step
   - "Research บริษัทคู่แข่งแล้วสรุปเป็น report"
   - "Debug bug นี้ใน codebase"

2. **ต้อง reasoning หลายชั้น**
   - "ถ้าเดือนนี้ขายดี ให้สั่งสต๊อกเพิ่ม 30%; ถ้าไม่ดีให้วิเคราะห์ว่าทำไม"

3. **มี tool หลายตัว** ที่ต้องเลือกใช้
   - Customer support agent ที่อาจ search KB / refund / escalate

4. **Iteration จำเป็น** — ทำผิดต้องลองใหม่
   - Code agent: write → test → fix → test

### ❌ อย่าใช้ agent เมื่อ

1. **งาน deterministic** — flow ชัดเจน
   - ❌ "Extract email → save to DB" → ใช้ workflow
   - ❌ "Translate text" → 1 LLM call

2. **Latency critical** — agent loop ช้าๆ
   - User ไม่รอ 30 วินาที สำหรับคำถามง่ายๆ

3. **Cost critical at scale**
   - ถ้า request 1M ครั้ง/วัน — agent loop จะแพงมาก
   - ใช้ workflow + cache

4. **Reliability critical** — failure ของ tool 1 ตัวอาจพังทั้ง chain
   - การชำระเงิน, การส่งของ — ต้อง deterministic

### Decision Tree

```
                    Task มาแล้ว
                         │
                         ▼
           ┌─────────────────────────┐
           │ มี flow ตายตัวมั้ย?       │
           └────────┬─────────┬──────┘
              YES   │         │   NO
                    ▼         ▼
              ┌─────────┐   ┌─────────────────┐
              │ WORKFLOW│   │ ต้องใช้ tools    │
              │ (chain) │   │ มากกว่า 1 ตัว?  │
              └─────────┘   └────┬───────┬────┘
                                 │       │
                            NO   │       │   YES
                                 ▼       ▼
                          ┌─────────┐  ┌──────┐
                          │1-shot   │  │AGENT │
                          │LLM call │  │      │
                          └─────────┘  └──────┘
```

---

## 4. Agentic Spectrum — ไม่ใช่ binary

จริงๆ "workflow vs agent" ไม่ใช่สวิตช์ on/off มันเป็น spectrum:

```
LESS AGENTIC ◄─────────────────────────────────────► MORE AGENTIC

[1] Single LLM call
        │
        ▼
[2] Chained LLMs (prompt 1 → prompt 2 → ...)
        │
        ▼
[3] LLM with tools (function calling)
        │
        ▼
[4] LLM with router (LLM ตัดสินใจ branch)
        │
        ▼
[5] Loop with tool use (ReAct)
        │
        ▼
[6] Plan-and-execute
        │
        ▼
[7] Multi-agent collaboration
        │
        ▼
[8] Self-modifying agent (เขียน code ตัวเองเพิ่ม tool)
```

ยิ่ง agentic มาก = ยิ่งทรงพลัง แต่ก็ยิ่ง:
- Cost สูง
- Latency สูง
- Failure mode เยอะ
- Debug ยาก

**กฎ**: ใช้ระดับน้อยที่สุดที่ทำงานได้

---

## 5. Common Misconceptions

### ❌ "Agent = ChatGPT ที่มี plugin"
ผิด — plugin คือ tool ที่ ChatGPT เลือกใช้ได้ การที่ ChatGPT เรียก plugin 1 รอบไม่ใช่ agent ตามนิยาม agent ต้องมี loop และตัดสินใจ multi-step

### ❌ "ใช้ agent = ฉลาดกว่าเดิม"
ผิด — agent loop ที่ออกแบบไม่ดี → reasoning ผิด → ผลลัพธ์แย่กว่า single LLM call เก่งๆ ด้วยซ้ำ

### ❌ "AutoGPT คือ future"
AutoGPT (2023) แสดงให้เห็นว่า agent autonomous ทำได้ แต่ปัจจุบัน (2026) production-grade agents = **constrained agents** ไม่ใช่ "ปล่อยให้คิดเอง 100%" — มี guardrails / state machine ชัดเจน

### ❌ "ใช้ framework = ดีกว่าเขียนเอง"
ใช้ framework ในงานที่เหมาะ — ถ้างานคุณ workflow ง่ายๆ เขียนเองด้วย Python loop + OpenAI SDK = clean กว่า, debug ง่ายกว่า, ไม่มี dependency hell

---

## 6. Tutorial: ReAct Agent ใน 30 บรรทัด

ก่อนไปทุก framework — เขียน agent ด้วยมือดูก่อน จะเข้าใจว่ามันทำงานยังไง:

```python
# pip install anthropic
import os, json
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# 1. Tools
def calculator(expression: str) -> str:
    return str(eval(expression))  # ⚠️ unsafe — เป็นแค่ตัวอย่าง

def search(query: str) -> str:
    # mock: real impl would call Tavily/SerpAPI
    return f"Search results for '{query}': [mock data]"

TOOLS = {
    "calculator": calculator,
    "search": search,
}

# 2. Tool schemas (Anthropic format)
TOOL_SCHEMAS = [
    {
        "name": "calculator",
        "description": "Evaluate a math expression",
        "input_schema": {"type": "object",
                         "properties": {"expression": {"type": "string"}},
                         "required": ["expression"]}
    },
    {
        "name": "search",
        "description": "Search the web",
        "input_schema": {"type": "object",
                         "properties": {"query": {"type": "string"}},
                         "required": ["query"]}
    },
]

# 3. Agent loop
def run_agent(goal: str, max_steps: int = 10):
    messages = [{"role": "user", "content": goal}]
    for step in range(max_steps):
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )
        # Final answer?
        if resp.stop_reason == "end_turn":
            return resp.content[0].text
        # Tool use
        messages.append({"role": "assistant", "content": resp.content})
        tool_results = []
        for block in resp.content:
            if block.type == "tool_use":
                result = TOOLS[block.name](**block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
        messages.append({"role": "user", "content": tool_results})
    return "Max steps reached"

print(run_agent("What is the population of Tokyo times 2?"))
```

**สิ่งที่เกิดขึ้น**:
1. Agent เห็น goal → คิดว่าต้อง search "population of Tokyo"
2. Tool result กลับมา → คิดว่าต้องคำนวณ × 2
3. ใช้ calculator → ได้ตัวเลข
4. Synthesize → ตอบ user

> นี่คือ ReAct pattern — เราจะลงรายละเอียดใน 02

**ลองรันดู** แล้วเปลี่ยน goal เป็นอย่างอื่น เพื่อดูว่า agent ตัดสินใจยังไง

---

## 7. Mental Models ที่ต้องจำ

### MM1: Agent = พนักงานใหม่
> Agent ก็เหมือนพนักงานใหม่ที่เก่งมาก แต่ไม่รู้บริบท
> - คุณต้องอธิบาย goal ให้ชัด (= prompt)
> - บอกว่าเขาทำอะไรได้บ้าง (= tools)
> - บอก SOP ของบริษัท (= system prompt + memory)
> - ตรวจงาน (= eval / human-in-the-loop)

### MM2: LLM ไม่ใช่ "ส่วนเดียว" ของ agent
> Agent ที่ทำงานดี ≠ LLM ที่เก่งที่สุด
> - 60% ของคุณภาพอยู่ที่ **tool design**
> - 30% อยู่ที่ **memory/context**
> - 10% อยู่ที่ LLM
> ⇒ ใช้เวลากับ tool / context มากกว่าหา model ใหม่

### MM3: Failure compounds
> ถ้า step ละ 90% accurate → 10 steps = 0.9¹⁰ = 35%
> ⇒ ยิ่ง agent ทำงานยาว ยิ่งต้อง verify / checkpoint

### MM4: Constrain > Freedom
> Agent ที่ "ฉลาด" คืออันที่ **ถูกบังคับให้ฉลาด** ไม่ใช่ปล่อยฟรี
> State machine + tool restriction ทำให้ผลลัพธ์ดีขึ้น มากกว่าเปิดให้ทำอะไรก็ได้

---

## สรุป

- **Agent** = LLM + Loop + Tools + Memory; LLM ตัดสินใจ next step เอง
- **Workflow** = LLM ที่ถูก orchestrate ผ่าน flow ตายตัว
- **เริ่มจาก workflow ก่อน เสมอ** — agent มี cost/risk
- 4 ส่วนของ agent: Brain (LLM), Tools, Memory, Loop
- ความฉลาดของ agent อยู่ที่ tool design + context มากกว่า LLM ตัวไหน
- Failure compounds — design ต้องมี checkpoint / verify

**ต่อไป** → [02 Design Patterns](02_Design_Patterns.md) ลงรายละเอียด pattern แต่ละแบบ

---

## References

- Anthropic, ["Building Effective Agents"](https://www.anthropic.com/research/building-effective-agents) (Dec 2024) — bible เริ่มต้น
- Yao et al., ["ReAct: Synergizing Reasoning and Acting in Language Models"](https://arxiv.org/abs/2210.03629) (2022)
- Anthropic, ["How we built our multi-agent research system"](https://www.anthropic.com/engineering/built-multi-agent-research-system) (2025)
- Lilian Weng, ["LLM Powered Autonomous Agents"](https://lilianweng.github.io/posts/2023-06-23-agent/) — overview ดี
