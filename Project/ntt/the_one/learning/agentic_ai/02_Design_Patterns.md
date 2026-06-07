# 02 — Agentic AI Design Patterns

> 11 patterns ที่คุณต้องรู้ — แบ่งเป็น Workflow patterns (deterministic) และ Agent patterns (autonomous)
> เลือก pattern ผิด = over-engineer / unreliable

---

## 0. ภาพรวม Patterns

อ้างอิง Anthropic's "Building Effective Agents" (2024) + ประสบการณ์จริง 2025-2026:

```
┌──────────────────────────────────────────────────────────────┐
│                    WORKFLOW PATTERNS                         │
│                  (deterministic, predictable)                │
├──────────────────────────────────────────────────────────────┤
│  1. Prompt Chaining         (sequential)                     │
│  2. Routing                 (classify → branch)              │
│  3. Parallelization         (sectioning + voting)            │
│  4. Orchestrator-Workers    (manager delegates)              │
│  5. Evaluator-Optimizer     (write → critique → rewrite)     │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                     AGENT PATTERNS                           │
│                  (autonomous, dynamic)                       │
├──────────────────────────────────────────────────────────────┤
│  6. ReAct                   (Thought→Act→Obs loop)           │
│  7. Plan-and-Execute        (plan once, execute, replan)     │
│  8. Reflexion               (try → reflect → retry)          │
│  9. Tree-of-Thoughts        (search over reasoning paths)    │
│ 10. Multi-Agent             (specialists + coordinator)      │
│ 11. Hierarchical Agent      (manager → worker → sub-worker)  │
└──────────────────────────────────────────────────────────────┘
```

---

## Part A — Workflow Patterns

### Pattern 1: Prompt Chaining

**Idea**: แตก task ใหญ่เป็น sub-tasks ที่ต่อเนื่องกัน

```
Input ──▶ LLM 1 ──▶ Output 1 ──▶ LLM 2 ──▶ Output 2 ──▶ LLM 3 ──▶ Final
                       │
                       ▼
                  [Validate?]  ← guardrail ระหว่างทาง
```

**ตัวอย่าง**: เขียน blog post
1. LLM 1: Outline
2. LLM 2: Draft from outline
3. LLM 3: Polish + add SEO

**Code**:
```python
def write_blog(topic):
    outline = llm(f"Create outline for blog about: {topic}")
    if not validate_outline(outline):
        return None
    draft = llm(f"Write draft from outline: {outline}")
    polished = llm(f"Polish + SEO: {draft}")
    return polished
```

**ใช้เมื่อ**: task แตกเป็น step ชัดเจนได้, ต้องการ checkpoint ระหว่างทาง
**Trade-off**: latency เพิ่ม (3 LLM calls แทน 1) แต่คุณภาพดีขึ้น และ debug ง่าย

---

### Pattern 2: Routing

**Idea**: LLM 1 ตัวคอย classify input → ส่งไป handler ที่เหมาะ

```
                ┌──────────────────┐
                │  Router LLM      │
                │  (classifier)    │
                └────────┬─────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   ┌─────────┐      ┌─────────┐      ┌─────────┐
   │ Refund  │      │Technical│      │ Billing │
   │ Handler │      │ Handler │      │ Handler │
   │ (cheap) │      │ (heavy) │      │(medium) │
   └─────────┘      └─────────┘      └─────────┘
```

**ใช้เมื่อ**: input มีหลาย "ประเภท" และแต่ละประเภทใช้ prompt/model ต่างกัน

**ตัวอย่าง**: Customer support
- Simple FAQ → Haiku + RAG
- Complex bug → Sonnet + tools
- Refund → escalate to human

**Code**:
```python
def support_router(message):
    category = llm_classifier(message)  # tiny model
    
    if category == "faq":
        return faq_handler(message)  # cheap
    elif category == "bug":
        return bug_handler(message)  # heavy
    elif category == "refund":
        return escalate_to_human(message)
```

**Trade-off**:
- ✅ ประหยัด — งานง่ายไม่ใช้ model แพง
- ❌ Router ผิด → routed ไปผิด handler → คำตอบแย่
- ⚠️ ต้อง eval router accuracy

**Tip**: ใช้ embedding-based classifier ก่อน LLM classifier ได้ — ถูกกว่า + เร็วกว่า

---

### Pattern 3: Parallelization

แบ่งเป็น 2 sub-pattern:

#### 3a. Sectioning — งานแยกเป็นชิ้น independent

```
Input
  │
  ├──▶ LLM (aspect 1) ─┐
  ├──▶ LLM (aspect 2) ─┼──▶ Aggregator ──▶ Output
  └──▶ LLM (aspect 3) ─┘
```

**ตัวอย่าง**: Code review
- LLM 1: ตรวจ security
- LLM 2: ตรวจ performance
- LLM 3: ตรวจ style
- Aggregator รวมผล

#### 3b. Voting — รัน prompt เดียวกันหลายครั้ง

```
Input
  │
  ├──▶ LLM ─┐
  ├──▶ LLM ─┼──▶ Majority Vote ──▶ Output
  └──▶ LLM ─┘
```

**ใช้เมื่อ**: งานที่ LLM ตอบไม่ stable — เช่น classify content moderation, generate code with bug

**Trade-off**:
- ✅ Latency คงที่ (parallel)
- ✅ คุณภาพสูงกว่า single call
- ❌ Cost × N (N LLM calls)

---

### Pattern 4: Orchestrator-Workers

**นี่คือ pattern หลักที่ user ของเราอยากทำ — ใส่ใจอันนี้!**

```
                      ┌────────────────┐
                      │  ORCHESTRATOR  │
                      │  (decides what │
                      │   to delegate) │
                      └────┬───────────┘
                           │ dynamically
                           │ spawns workers
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
  ┌──────────┐      ┌──────────┐      ┌──────────┐
  │ Worker 1 │      │ Worker 2 │      │ Worker 3 │
  │(Architect│      │ (DB      │      │(Frontend │
  │ design)  │      │ design)  │      │ design)  │
  └──────────┘      └──────────┘      └──────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                  ┌────────────────┐
                  │  Aggregator    │
                  │  (merge & ship)│
                  └────────────────┘
```

**ต่างจาก parallelization ตรงไหน**: ใน parallelization เรา**กำหนดเอง**ว่ามี aspect อะไรบ้าง — ใน orchestrator-workers, **LLM ตัดสินใจ**ว่าต้องสร้าง worker กี่ตัวและทำอะไร

**ตัวอย่าง**: Search agent
- Orchestrator: รับคำถาม → ตัดสินใจว่าต้อง search 3 ประเด็น
- Worker 1: search ประเด็น A
- Worker 2: search ประเด็น B
- Worker 3: search ประเด็น C
- Orchestrator: รวมผล + เขียน summary

**Code skeleton**:
```python
def orchestrator_workers(task):
    plan = orchestrator_llm(f"""
    Task: {task}
    Break this into independent sub-tasks.
    Output JSON: [{{"id": 1, "task": "..."}}, ...]
    """)
    sub_tasks = json.loads(plan)
    
    # Run workers in parallel
    with ThreadPoolExecutor() as ex:
        results = list(ex.map(
            lambda st: worker_llm(st["task"]), 
            sub_tasks
        ))
    
    final = orchestrator_llm(f"Synthesize: {results}")
    return final
```

**ใช้เมื่อ**:
- ไม่รู้ล่วงหน้าว่าต้องแตกงานยังไง
- Worker แต่ละตัวเป็น expert คนละด้าน
- ต้องการ parallel execution

**Trade-off**:
- ✅ Flexible — orchestrator ตัดสินใจ runtime
- ❌ Cost สูง (orchestrator + N workers + aggregator)
- ⚠️ Worker output ต้อง structured (ไม่งั้น aggregator งง)

> **ไอเดียของคุณ** (ส่ง spec ไปให้ AI experts) = pattern นี้ตรงๆ จะลงรายละเอียดใน [07 Case Study](07_Case_Study_Ecommerce_Builder.md)

---

### Pattern 5: Evaluator-Optimizer

**Idea**: LLM เขียน → LLM อีกตัวประเมิน → ปรับปรุง → loop

```
       ┌─────────────┐
  ┌───▶│  Generator  │
  │    └─────┬───────┘
  │          │ output
  │          ▼
  │    ┌─────────────┐
  │    │  Evaluator  │ ──── if PASS ──▶ DONE
  │    └─────┬───────┘
  │          │ feedback
  └──────────┘
```

**ใช้เมื่อ**: มี evaluation criteria ชัดเจน + iterative improvement ดีขึ้นจริง

**ตัวอย่าง**: เขียน code
- Generator: เขียน function
- Evaluator: รัน test + ตรวจ style
- ถ้าไม่ผ่าน → feedback → generator แก้

**Code**:
```python
def generate_with_eval(spec, max_iter=5):
    output = generator_llm(spec)
    for i in range(max_iter):
        verdict, feedback = evaluator_llm(spec, output)
        if verdict == "PASS":
            return output
        output = generator_llm(spec, prev=output, feedback=feedback)
    return output  # หรือ raise
```

**Trade-off**:
- ✅ คุณภาพสูง (กรณีที่ eval ทำได้ดี)
- ❌ Cost × N iterations
- ⚠️ Evaluator คือคอขวด — ถ้า evaluator ผิด ทุกอย่างผิด

**Tip**: ใช้ stronger model เป็น evaluator, cheaper model เป็น generator

---

## Part B — Agent Patterns

### Pattern 6: ReAct (Reason + Act)

**Origin**: Yao et al., 2022 — pattern ดั้งเดิม

```
Loop:
  Thought:    "I need to find population of Tokyo"
  Action:     search("population of Tokyo")
  Observation: "13.96 million"
  Thought:    "Now multiply by 2"
  Action:     calculator("13.96 * 2")
  Observation: "27.92"
  Thought:    "I have the answer"
  Final Answer: "27.92 million"
```

**Format prompt** (ตัวอย่างเก่า, ก่อน function calling):
```
You can use these tools: search, calculator
Use this format:
Thought: ...
Action: <tool>(<args>)
Observation: <result>
... (loop)
Final Answer: <answer>
```

**ปัจจุบัน (2026)**: LLM ทุกตัวรองรับ "tool use" / "function calling" → ไม่ต้อง parse text แล้ว

**Code** (ดูที่ 01 §6 มีตัวอย่างเต็ม)

**ใช้เมื่อ**: ต้องการ flexibility สูง, งาน open-ended
**Trade-off**:
- ✅ Simple, มี library รองรับเยอะ
- ❌ Agent อาจ "หลง" — loop ไม่จบ
- ⚠️ Token เยอะ (ทุก iter ส่ง history ทั้งหมด)

---

### Pattern 7: Plan-and-Execute

**Idea**: วางแผนทีเดียวก่อน → execute → ถ้าพังให้ replan

```
       ┌──────────────┐
       │   PLANNER    │  วางแผน step ทั้งหมด
       └──────┬───────┘
              ▼
       Plan: [s1, s2, s3, s4]
              │
              ▼
       ┌──────────────┐
   ┌──▶│   EXECUTOR   │  ทำทีละ step
   │   └──────┬───────┘
   │          │ if fail
   │          ▼
   │   ┌──────────────┐
   └───│   REPLANNER  │  ปรับแผน
       └──────────────┘
```

**ต่างจาก ReAct ตรงไหน**: ReAct คิดทีละ step — Plan-and-Execute คิดทั้งหมดก่อน

**ใช้เมื่อ**:
- Task ที่ structure ค่อนข้างชัด (รู้คร่าวๆ ว่าต้องทำอะไรบ้าง)
- ต้องการ parallelize step ที่ independent
- Token efficiency สำคัญ (planner คิดครั้งเดียว)

**Code skeleton**:
```python
def plan_and_execute(goal):
    plan = planner_llm(goal)  # JSON list of steps
    results = {}
    for step in plan:
        try:
            results[step.id] = execute(step, context=results)
        except Exception as e:
            plan = replanner_llm(goal, plan, results, error=e)
            # restart loop with new plan
    return synthesize(goal, results)
```

**Trade-off**:
- ✅ Token efficient
- ✅ Parallel execution ของ independent steps
- ❌ Plan ผิดตั้งแต่ต้น → ต้อง replan = waste
- ⚠️ ไม่ adaptive เท่า ReAct

---

### Pattern 8: Reflexion (Self-Critique)

**Idea**: หลังทำ task → reflect → improve

```
Attempt 1: ทำ task → output 1
        ↓
Reflect: "What went wrong? What to improve?"
        ↓
Attempt 2: ทำใหม่ ด้วย insight จาก reflection → output 2
        ↓ (loop until satisfied)
```

ต่างจาก Evaluator-Optimizer ตรงที่ reflection ทำโดย agent เดียวกัน (self-critique) — ไม่ใช่ critic แยก

**ตัวอย่าง**: Math problem
- Attempt 1: คำนวณ → ได้คำตอบ
- Reflect: "ลองตรวจคำตอบโดยแทนค่ากลับ" → พบว่าผิด
- Attempt 2: หาทางใหม่

**Code**:
```python
def reflexion(task, max_iter=3):
    attempt = llm(f"Solve: {task}")
    for i in range(max_iter):
        reflection = llm(f"""
            Task: {task}
            Your attempt: {attempt}
            Critique: Is this correct? What should improve?
        """)
        if "correct" in reflection.lower():
            return attempt
        attempt = llm(f"""
            Task: {task}
            Previous: {attempt}
            Reflection: {reflection}
            Try again:
        """)
    return attempt
```

**Trade-off**:
- ✅ คุณภาพดีขึ้นมาก สำหรับ reasoning task
- ❌ Cost × 2-3
- ⚠️ Self-critique ไม่ honest เสมอ — บางที LLM ยืนยันคำตอบผิดของตัวเอง

---

### Pattern 9: Tree-of-Thoughts (ToT)

**Idea**: แทนที่จะคิด linear (ReAct) — คิดเป็น tree, search หาเส้นทางที่ดีที่สุด

```
                    Goal
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    Branch A     Branch B     Branch C
    (rate: 0.6)  (rate: 0.9)  (rate: 0.3)
        │            │            │
       ...      ┌────┼────┐      ✗ pruned
                ▼    ▼    ▼
              B1   B2   B3
            (0.5)(0.95)(0.4)
                 ✓ best
```

**ใช้เมื่อ**: Reasoning task ที่มีทางเลือกหลายเส้นทาง (puzzle, math, planning)

**Trade-off**:
- ✅ คุณภาพสูงสำหรับ complex reasoning
- ❌ Cost × O(branching × depth)
- ⚠️ Production ใช้น้อย — overhead เยอะ ใช้เฉพาะ research

> ในงาน production จริง ToT ใช้น้อย — ใช้ Reflexion / multi-agent voting แทน

---

### Pattern 10: Multi-Agent Collaboration

**Idea**: หลาย agent ที่แต่ละตัวมี role ชัด ทำงานร่วมกัน

```
                  ┌─────────────────┐
                  │   COORDINATOR   │
                  │      AGENT      │
                  └────────┬────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
  ┌──────────┐       ┌──────────┐       ┌──────────┐
  │Researcher│       │  Writer  │       │ Reviewer │
  │  Agent   │◀────▶ │  Agent   │ ◀───▶ │  Agent   │
  └──────────┘       └──────────┘       └──────────┘
       ↑                                       │
       └───── feedback if reject ──────────────┘
```

**ต่างจาก Orchestrator-Workers ตรงไหน**:
- Orchestrator-Workers: workers ไม่คุยกัน, รับคำสั่งจาก orchestrator เท่านั้น
- Multi-Agent: agents คุยกันได้, มี dialog

**Pattern ของ communication**:

#### A. Sequential
```
Researcher ──▶ Writer ──▶ Reviewer ──▶ Done
```

#### B. Group Chat (AutoGen style)
```
[Coordinator]: Topic = AI in healthcare
[Researcher]: Found 3 papers on...
[Writer]: Drafting based on papers...
[Reviewer]: Section 2 needs more depth
[Writer]: Updating...
```

#### C. Hierarchical (next pattern)

**ใช้เมื่อ**:
- งานต้องการ specialist หลายด้าน
- การ collaboration / debate ทำให้ output ดีขึ้น

**Trade-off**:
- ✅ คุณภาพ + flexibility
- ❌ Cost สูงมาก (agents × turns)
- ⚠️ Coordination overhead — ออกแบบ communication protocol ให้ดี

**Tip จาก Anthropic (multi-agent research system, 2025)**:
- ใช้ Sonnet เป็น orchestrator (planning เก่ง)
- ใช้ Haiku เป็น sub-agent (parallel + cheap)
- ลด token 90%+ ด้วยการ summarize ก่อนส่งกลับ orchestrator

---

### Pattern 11: Hierarchical Agent

**Idea**: Manager → Worker → Sub-worker (recursive)

```
        ┌─────────────────┐
        │   CEO Agent     │  วาง vision
        └────────┬────────┘
                 │
     ┌───────────┼───────────┐
     ▼           ▼           ▼
  ┌──────┐   ┌──────┐   ┌──────┐
  │ CTO  │   │ CMO  │   │ CFO  │
  └──┬───┘   └──┬───┘   └──┬───┘
     │          │          │
  ┌──┴──┐    ┌──┴──┐    ┌──┴──┐
  │ Dev │    │SEO  │    │Acct │
  │Agent│    │Agent│    │Agent│
  └─────┘    └─────┘    └─────┘
```

**ใช้เมื่อ**:
- Task ซับซ้อนมาก แต่ละ layer เห็น abstraction ต่างกัน
- ต้องการแยก concerns ตามระดับ (strategic / tactical / operational)

**Code skeleton** (recursive):
```python
class Agent:
    def __init__(self, role, sub_agents=None):
        self.role = role
        self.sub_agents = sub_agents or []
    
    def execute(self, task):
        if not self.sub_agents:
            return llm(self.role, task)  # leaf
        
        plan = llm(f"As {self.role}, decompose: {task}")
        results = []
        for sub_task, sub_agent_role in plan:
            sub = next(a for a in self.sub_agents if a.role == sub_agent_role)
            results.append(sub.execute(sub_task))
        return synthesize(results)
```

**Trade-off**:
- ✅ Scale ได้สูง — เพิ่ม layer ได้
- ❌ Latency สะสม (manager wait for workers wait for sub-workers...)
- ❌ Cost มหาศาล
- ⚠️ Communication path ยาว → information loss

---

## Part C — เลือก Pattern ยังไง

### Decision Flowchart

```
                    คุณมี task อะไร?
                            │
            ┌───────────────┴───────────────┐
            │                               │
      Deterministic?                  Open-ended?
            │                               │
            ▼                               ▼
      WORKFLOW patterns              AGENT patterns
            │                               │
   ┌────────┼────────┐             ┌────────┼────────┐
   │        │        │             │        │        │
Single   Branch    Many         Linear   Iterate  Multi-
 step     by      parts         tools    /reflect  role
   │     type      │              │        │        │
   ▼     │         ▼              ▼        ▼        ▼
1-shot   ▼      Sectioning      ReAct  Reflexion  Multi-
 LLM   Routing  /Voting          │     /Eval-Opt   agent
                                 ▼
                         (ถ้ารู้ plan ก่อน)
                          Plan-and-Execute
```

### Cheatsheet (จำได้ก็พอ)

| ถ้า... | ใช้ pattern... |
|---|---|
| เขียน blog 3 step | Prompt Chaining |
| Customer support 5 ประเภท | Routing |
| ตรวจ code review หลายมุม | Sectioning |
| Content moderation ที่ต้องแม่น | Voting |
| Research ที่ไม่รู้ต้องค้นกี่อย่าง | Orchestrator-Workers |
| เขียน code ที่ต้อง pass test | Evaluator-Optimizer |
| Search agent ทั่วไป | ReAct |
| Pipeline ที่รู้ structure คร่าวๆ | Plan-and-Execute |
| Math / reasoning task | Reflexion |
| ทีม specialist (engineer + designer + PM) | Multi-Agent |
| Org-scale agent | Hierarchical |

---

## Part D — Anti-patterns (อย่าทำ)

### ❌ AP1: "Agent ทุกอย่าง"
```
ผิด: ใช้ ReAct loop ทำทุก task แม้ task เป็น linear
ถูก: ดู spectrum (01 §4) — เลือกระดับน้อยที่สุดที่งานต้องการ
```

### ❌ AP2: "More agents = better"
```
ผิด: เพิ่ม agent → "ทีม 10 คน" → ทุกคน LLM call แยก
ถูก: 2-3 agent ก็พอสำหรับ 90% ของ use case
```

### ❌ AP3: "Plan-and-Execute โดยไม่มี replan"
```
ผิด: planner ผิด → execute → fail → ไม่มี recovery
ถูก: เสมอมี replanner / fallback
```

### ❌ AP4: "ReAct ไม่จำกัด max_iter"
```
ผิด: while True: agent.step()  ← infinite loop / token bomb
ถูก: max_iter + budget cap (token limit) + circuit breaker
```

### ❌ AP5: "Multi-agent ไม่มี protocol"
```
ผิด: agents คุยกันแบบ free-form → token explode, drift
ถูก: structured messages (JSON), turn limits, role boundaries
```

### ❌ AP6: "Tool list ยาวเหยียด"
```
ผิด: agent มี 50 tools → confused, pick wrong tool
ถูก: ≤ 7-10 tools / agent; subagent ที่มี toolset เฉพาะ
```

---

## Part E — เลือก Pattern โดยใช้ Use Case ตัวอย่าง

### UC1: Chatbot ตอบคำถามจาก doc (RAG)
```
Pattern: Workflow (Prompt Chaining)
Flow: Query → embed → search → re-rank → LLM → answer
```
อย่าใช้ agent — overkill

### UC2: AI Recruiter อ่าน CV → match กับ JD
```
Pattern: Sectioning
Flow: parallel(skills_match, experience_match, culture_match) → aggregate
```

### UC3: Code review bot
```
Pattern: Sectioning + Evaluator-Optimizer
Flow: parallel(security_check, perf_check, style_check) 
      → aggregate
      → if issues: suggest fixes via Evaluator-Optimizer
```

### UC4: Research agent ("วิเคราะห์คู่แข่ง 5 บริษัท")
```
Pattern: Orchestrator-Workers
Flow: orchestrator แตกเป็น 5 sub-task (per company)
      → 5 workers ค้นข้อมูล parallel
      → orchestrator รวม + เขียน report
```

### UC5: Coding agent (เช่น Cursor/Claude Code)
```
Pattern: ReAct + Reflexion
Flow: read repo → plan → write → test → if fail: reflect → retry
```

### UC6: Build website end-to-end (ไอเดียของคุณ)
```
Pattern: Hierarchical + Orchestrator-Workers (composite)
Flow: 
  Coordinator (vision)
    → Analyst (decompose to subsystems)
    → Architect (design)
       → Specialists (DB, frontend, backend, devops) [parallel]
          → Implementers (cheap LLMs writing code)
    → Reviewer
```
จะลงรายละเอียดใน [07 Case Study](07_Case_Study_Ecommerce_Builder.md)

---

## สรุป

- 5 Workflow patterns + 6 Agent patterns — รู้ทั้งหมดแล้วใช้ตามงาน
- **ใช้ workflow ก่อน, agent ทีหลัง** — เสมอ
- Orchestrator-Workers = pattern ที่ใช้บ่อยสุดสำหรับ multi-step task
- Multi-agent / Hierarchical = ของจริงในงานใหญ่ แต่ cost สูงมาก
- Anti-pattern หลัก: ใช้ agent ทั้งที่ workflow พอ

**ต่อไป** → [03 Frameworks Comparison](03_Frameworks_Comparison.md) — เลือก framework ที่ใช่กับ pattern

---

## References

- Anthropic, ["Building Effective Agents"](https://www.anthropic.com/research/building-effective-agents) (2024) — pattern definitions
- Yao et al., ["ReAct"](https://arxiv.org/abs/2210.03629) (2022)
- Shinn et al., ["Reflexion"](https://arxiv.org/abs/2303.11366) (2023)
- Yao et al., ["Tree of Thoughts"](https://arxiv.org/abs/2305.10601) (2023)
- Wu et al., ["AutoGen"](https://arxiv.org/abs/2308.08155) (2023) — multi-agent
- Anthropic, ["How we built our multi-agent research system"](https://www.anthropic.com/engineering/built-multi-agent-research-system) (2025)
