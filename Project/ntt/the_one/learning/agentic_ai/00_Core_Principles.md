# 00 — Core Principles (แกนหลัก)

> "ถ้าจำได้แค่ไฟล์เดียว จำไฟล์นี้"
> 15 หลักที่ extract มาจากทุกไฟล์ — เป็น compass เวลาคุณตัดสินใจ

---

## ทำไมต้องอ่าน

ทั้งชุดเอกสาร 11 ไฟล์ → 240KB → เนื้อหาเยอะ
แต่จริงๆ มันถูก derive มาจาก **หลักไม่กี่ข้อ**
ไฟล์นี้คือ "หลัก" พวกนั้น

ตอนคุณเจอสถานการณ์ใหม่ → ดูที่หลัก → ตัดสินใจได้
ถ้าทำตามแค่ pattern หรือ tool — เจอ case ใหม่ก็จะหลง

---

## Big Idea: Agent คือ "ระบบ" ไม่ใช่ "model"

```
LLM ดี ≠ agent ดี
agent ดี = ระบบที่ออกแบบดี + LLM พอดี
```

LLM เป็นแค่ 1 ใน 4 ส่วน (Brain, Tools, Memory, Loop)
ความฉลาดของระบบมาจาก **architecture** ไม่ใช่ตัว model

---

# Part A — Design Principles (หลักออกแบบ)

## P1: Workflow before Agent

**กฎ**: เริ่มที่ workflow (deterministic) เสมอ — เปลี่ยนเป็น agent เมื่อจำเป็นเท่านั้น

**เพราะ**: agent มี cost / latency / failure mode สูงกว่า workflow มาก ถ้า task deterministic — workflow คือคำตอบ

**Apply เมื่อ**:
- ออกแบบใหม่ → เริ่ม workflow → ดูว่าพอมั้ย → upgrade ถ้าไม่พอ
- เจอคนแนะ "ใช้ agent" → ถามกลับ "ทำไมไม่ workflow?"

→ [01 §3](01_Agentic_AI_Fundamentals.md), [02 §0](02_Design_Patterns.md)

---

## P2: Tool > Model > Prompt

**สัดส่วนคุณภาพ agent**:
- 60% — Tool design
- 30% — Memory / context
- 10% — Choice of LLM

**เพราะ**: LLM ฉลาดถึงไหนก็ทำได้แค่ tool ที่มันเรียกได้ ส่วน prompt ส่งผลแค่ marginal

**Apply เมื่อ**:
- Agent ตอบไม่ดี → first check **tool design**, ไม่ใช่เปลี่ยน model
- งบจำกัด → ลงทุนเวลา/code กับ tool, ใช้ model ราคาเบา

→ [04 ทั้งหมด](04_Tools_and_Selection.md)

---

## P3: Constrain > Freedom

**กฎ**: agent ที่ "ฉลาด" คือ agent ที่ **ถูกบังคับให้ฉลาด** — ไม่ใช่ปล่อยฟรี

**เพราะ**: 
- LLM ปล่อยฟรี → drift, hallucinate, infinite loop
- State machine + constrained tool list → output stable

**Apply เมื่อ**:
- ใช้ LangGraph แทน open-ended ReAct
- จำกัด ≤ 10 tools per agent
- Max steps + budget cap

→ [01 §7 MM4](01_Agentic_AI_Fundamentals.md), [deep_dive/01](deep_dive/01_LangGraph_Patterns.md)

---

## P4: Failure Compounds

**คณิต**: 90% accuracy ต่อ step × 10 steps = 35% end-to-end

**เพราะ**: ทุก step มีโอกาสพัง — ยิ่ง agent ยาว ยิ่งสะสม

**Apply เมื่อ**:
- ทุก phase ต้องมี **checkpoint / verify**
- HITL ที่จุดสำคัญ
- Reviewer agent หลัง multi-step
- ลด step count ให้น้อยที่สุด

→ [01 §7 MM3](01_Agentic_AI_Fundamentals.md), [02 Anti-pattern AP3](02_Design_Patterns.md)

---

## P5: Compose Patterns, Don't Reinvent

**กฎ**: 11 patterns ที่อยู่ใน [02](02_Design_Patterns.md) ครอบคลุม 95% case — combine ได้

**ตัวอย่าง compose**:
- E-commerce builder (07) = Hierarchical + Orchestrator-Workers + Eval-Optimizer
- Coding agent = ReAct + Reflexion
- Research agent = Orchestrator-Workers + Sectioning

**Apply เมื่อ**:
- ก่อนสร้าง pattern ใหม่ → check 11 patterns ก่อน
- Compose ดีกว่า invent จาก scratch

→ [02 ทั้งหมด](02_Design_Patterns.md)

---

# Part B — Decision Principles (หลักตัดสินใจ)

## P6: Match Tool to Problem (ไม่ใช่ปัญหากับ tool)

**กฎ**: เริ่มจาก problem → เลือก pattern → เลือก framework → เลือก LLM

**Anti-pattern**: 
- "ใช้ LangGraph มา 6 เดือน — ใช้กับทุก project" ❌
- "Cool framework ใหม่ — เอามาลองงานจริง" ❌

**ลำดับที่ถูก**:
```
Problem → Pattern (จาก 02) → Framework (จาก 03) → LLM (จาก 06)
```

→ [03 §4 Decision Matrix](03_Frameworks_Comparison.md), [02 §C Cheatsheet](02_Design_Patterns.md)

---

## P7: Free First, Then Optimize

**ลำดับงบ**:
1. Gemini Free Tier + Ollama (laptop) → $0
2. Cheap APIs (Haiku/Flash) + Qdrant Docker → $5-30/mo
3. Sonnet/GPT-5 + managed services → $100+/mo

**กฎ**: เริ่ม tier 1 เสมอ — ขยับขึ้นเมื่อพิสูจน์ได้ว่าจำเป็น

**Apply เมื่อ**:
- Start project → ใช้ free tier ก่อน
- หลัง prototype → measure ว่าตรงไหน "ต้อง" ใช้ smart model
- Routing: Sonnet เฉพาะ planner, Haiku/Llama ทำงานหลัก

→ [06 §3](06_Production_Cost_Observability.md), [deep_dive/04](deep_dive/04_Cost_Optimization_Tactics.md)

---

## P8: Measure Before Optimize

**กฎ**: ลด cost / improve quality โดยไม่ measure = guessing

**Order**:
1. Trace ทุก request (Langfuse) → รู้ที่ไหนแพง/ช้า/พัง
2. Pareto: 80% cost จาก 20% steps → focus ที่นั่น
3. Optimize → measure อีกที

**Apply เมื่อ**:
- ตั้ง observability **day 1** ไม่ใช่ "ทำเสร็จก่อน"
- มี eval suite ก่อน optimize prompt
- ดู metric จริง ไม่ใช่ "feel"

→ [06 §4](06_Production_Cost_Observability.md), [deep_dive/04 §2](deep_dive/04_Cost_Optimization_Tactics.md)

---

# Part C — Operational Principles (หลักปฏิบัติ)

## P9: Budget or Die

**กฎ**: ทุก agent ต้องมี budget (cost + steps + time)

**เพราะ**: agent loop พังได้ → infinite tool call → ค่าใช้จ่ายระเบิด

**Minimum budget**:
- `max_cost_usd` per request
- `max_steps` per agent
- `max_wall_time_sec`
- Alert ที่ 50% / 75% / 90%

→ [06 §6.3](06_Production_Cost_Observability.md), [02 AP4](02_Design_Patterns.md)

---

## P10: Observability Day 1

**กฎ**: Langfuse / LangSmith ติดก่อน feature เสร็จ ไม่ใช่หลัง

**เพราะ**: agent debug ยากมาก — ไม่มี trace = ไม่รู้พังที่ไหน

**Minimum observability**:
- Per-request: latency, cost, all LLM calls, all tool calls
- Aggregate: p50/p95, error rate, cost per user

→ [06 §4](06_Production_Cost_Observability.md), [deep_dive/02](deep_dive/02_Self_Hosted_Stack.md)

---

## P11: Eval Stops Silent Regression

**กฎ**: ทุก deploy ต้องผ่าน eval suite

**เพราะ**: 
- LLM update → behavior เปลี่ยน → output เคยดี อาจพัง
- Prompt tweak → ทำให้ case 1 ดีขึ้น แต่ case 2 พัง
- ไม่มี eval = ไม่รู้

**Minimum**: Promptfoo + 10-20 representative cases + CI integration

→ [06 §5](06_Production_Cost_Observability.md)

---

## P12: HITL for Irreversible Actions

**กฎ**: action ที่ undo ไม่ได้ → ต้องให้คน approve

**ตัวอย่าง irreversible**:
- ส่ง email / DM
- Charge บัตร
- Delete data
- Deploy production

**Apply ผ่าน**: LangGraph `interrupt_before` หรือ n8n `Wait` node

→ [06 §6.4](06_Production_Cost_Observability.md), [deep_dive/01 §8](deep_dive/01_LangGraph_Patterns.md)

---

# Part D — Architecture Principles (หลักสถาปัตย์)

## P13: Memory in 3 Layers

```
WORKING (in-context)        — current convo, scratchpad
EPISODIC (per-session)      — past convos, history
SEMANTIC (shared knowledge) — domain facts, RAG
```

**กฎ**: รู้ว่าข้อมูลแต่ละชิ้นอยู่ชั้นไหน — อย่าเก็บ working ไว้ semantic หรือกลับกัน

**Apply เมื่อ**:
- Convo summary → Episodic (Postgres)
- Domain facts → Semantic (Qdrant)
- Current task state → Working (LangGraph state)

→ [05 ทั้งหมด](05_Memory_and_Knowledge.md)

---

## P14: State Explicit, Not Implicit

**กฎ**: state ต้องเห็นได้ debug ได้ checkpoint ได้

**Anti-pattern**:
- Convo state ฝังใน message history → debug ยาก
- "Magic" wrapping (CrewAI hidden state) → audit ไม่ได้

**Pattern ที่ถูก**: 
- LangGraph TypedDict state — explicit
- File-based artifacts — git-trackable
- Observability traces — replayable

→ [deep_dive/01 §2](deep_dive/01_LangGraph_Patterns.md), [07 §3](07_Case_Study_Ecommerce_Builder.md)

---

## P15: Compose, Don't Monolith

**กฎ**: 
- 1 ใหญ่ agent ทำทุกอย่าง = brittle
- หลาย small agents ที่ specialty ชัด = robust

**ตัวอย่าง**:
- ❌ "AssistantAgent" ที่มี 30 tools ทำได้ทุกอย่าง
- ✅ Coordinator + 4 specialists + 4 implementers (case study 07)

**Why**:
- Specialty agent → focused prompt, ใช้ cheaper model ได้
- Failure isolation
- Composable: replace 1 agent โดยไม่กระทบตัวอื่น

→ [07 ทั้งหมด](07_Case_Study_Ecommerce_Builder.md), [02 §pattern 4](02_Design_Patterns.md)

---

# Part E — Anti-Principles (อย่าทำ)

## AP1: "AI Magic จะแก้ทุกอย่าง"
ผิด — agent ดีต้อง engineer ดีๆ ไม่ใช่ "ใส่ LLM ไป"

## AP2: "Multi-agent = better"
ผิด — 2 agents ดีกว่า 5 agents ที่ confused

## AP3: "ตอนนี้ฟรี เดี๋ยวค่อยคุม cost"
ผิด — cost ระเบิดเร็วมาก ตั้ง budget ตั้งแต่ day 1

## AP4: "เริ่มที่ frontier model"
ผิด — เริ่ม Haiku/Flash → upgrade ถ้าไม่พอ

## AP5: "Framework สวย → Project ดี"
ผิด — Framework เป็นเครื่องมือ Architecture เป็น "design"

## AP6: "ทำให้เสร็จก่อน → ค่อยใส่ trace"
ผิด — ไม่มี trace = debug ไม่ได้ = ทำไม่เสร็จ

## AP7: "agent autonomous เต็มที่"
ผิด — production = constrained agent + HITL ที่จุดสำคัญ

## AP8: "แก้ bug ด้วย prompt tweak"
ผิด — bug บ่อยอยู่ที่ tool / state / context, ไม่ใช่ prompt

---

# The "First Hour" Drill

ถ้าคุณเจอ task ใหม่ — ทำ drill นี้ในชั่วโมงแรก:

```
0-10 min: เขียน problem statement 1 paragraph
10-20 min: workflow ก่อน → ทำได้มั้ย? (P1)
20-30 min: เลือก pattern (P5, [02])
30-45 min: list tools ที่จำเป็น + describe ทุกตัว (P2)
45-60 min: เลือก framework + LLM (P6, P7)
```

หลังชั่วโมงแรก — มี skeleton design ที่ implement ต่อได้

---

# The "Decision Cheat Sheet"

| คำถาม | หลัก | ไป |
|---|---|---|
| Workflow หรือ agent? | P1 | [01 §3](01_Agentic_AI_Fundamentals.md) |
| Pattern ไหน? | P5 | [02 §C](02_Design_Patterns.md) |
| Framework ไหน? | P6 | [03 §4](03_Frameworks_Comparison.md) |
| LLM ไหน? | P7 | [06 §1.2](06_Production_Cost_Observability.md) |
| Output แย่ — แก้ที่ไหน? | P2 | tool design ก่อน |
| Cost สูง — ลดยังไง? | P8 | [deep_dive/04](deep_dive/04_Cost_Optimization_Tactics.md) |
| Production ready? | P9-P12 | [06 §9](06_Production_Cost_Observability.md) |
| Multi-agent ออกแบบยังไง? | P15 | [07](07_Case_Study_Ecommerce_Builder.md) |

---

# The "Mantra"

> Workflow first.
> Tool > Model > Prompt.
> Constrain > Freedom.
> Failure compounds — checkpoint.
> Free first, optimize next.
> Budget or die.
> Trace day 1.
> Eval before deploy.
> Compose, don't monolith.

อ่าน 9 บรรทัดนี้ก่อนเริ่มงานทุกครั้ง — 80% ของการตัดสินใจจะถูก

---

## ถ้าคุณยังจำได้แค่ 3 อย่าง

```
1. Start with workflow — agent เมื่อจำเป็น
2. Tool design = 60% ของคุณภาพ
3. Trace + budget + eval = ป้องกันระเบิด
```

ทุกอย่างใน 11 ไฟล์ที่เหลือ → derived จาก 3 ข้อนี้

---

## Next

- ใหม่ → [01 Fundamentals](01_Agentic_AI_Fundamentals.md)
- มี idea → [07 Case Study](07_Case_Study_Ecommerce_Builder.md)
- จะ optimize → [deep_dive/04](deep_dive/04_Cost_Optimization_Tactics.md)
