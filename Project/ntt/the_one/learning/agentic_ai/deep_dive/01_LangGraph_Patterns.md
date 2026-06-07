# Deep Dive 01 — LangGraph Patterns

> State machine สำหรับ agent — checkpointing, HITL, branching, parallel
> รู้ pattern แล้วใช้ LangGraph ได้จริงๆ

---

## 1. ทำไม LangGraph (อีกที)

ก่อน LangGraph คนใช้ `AgentExecutor` ของ LangChain — ปัญหา:
- ไม่เห็น state internal
- Loop ไหนพังไม่รู้
- Resume ไม่ได้
- HITL ลำบาก

**LangGraph mental model**: graph + state
- **Nodes**: function ที่รับ state → return updated state
- **Edges**: direction (conditional หรือ fixed)
- **State**: TypedDict ที่ flow ทั่ว graph

---

## 2. Core Concepts

### 2.1 State

```python
from typing import TypedDict, Annotated
from operator import add

class State(TypedDict):
    messages: Annotated[list, add]  # `add` = append, default = replace
    counter: int
    plan: list[str]
```

**Reducer** (`Annotated[list, add]`): เวลา multiple node update field เดียวกัน — รวมยังไง
- `add` for list → append
- `operator.or_` for set → union
- Default → replace

### 2.2 Nodes

Node = function รับ state คืน partial state update

```python
def planner(state: State) -> dict:
    plan = llm.invoke(state["messages"])
    return {"plan": plan.split("\n")}  # only update "plan"
```

### 2.3 Edges

```python
g = StateGraph(State)
g.add_node("planner", planner)
g.add_node("executor", executor)

# Fixed edge
g.set_entry_point("planner")
g.add_edge("planner", "executor")

# Conditional
g.add_conditional_edges(
    "executor",
    lambda s: "done" if not s["plan"] else "executor",  # router function
    {"done": END, "executor": "executor"}
)
```

### 2.4 Compile

```python
app = g.compile()

# Sync
result = app.invoke({"messages": [...], "counter": 0, "plan": []})

# Stream
for chunk in app.stream({"messages": [...]}):
    print(chunk)
```

---

## 3. Pattern 1: Linear Pipeline

```
Start → A → B → C → End
```

```python
g = StateGraph(State)
g.add_node("a", node_a)
g.add_node("b", node_b)
g.add_node("c", node_c)

g.set_entry_point("a")
g.add_edge("a", "b")
g.add_edge("b", "c")
g.add_edge("c", END)
```

ใช้: workflow ที่ step ตายตัว

---

## 4. Pattern 2: ReAct Loop

```
        ┌─────────┐
   ┌───▶│  agent  │
   │    └────┬────┘
   │         │
   │   ┌─────┴──────┐
   │   │ has tool?  │
   │   └─────┬──────┘
   │       Y │ N
   │         │ ▼
   │      ┌──▼────┐  END
   └──────│ tools │
          └───────┘
```

```python
from langgraph.prebuilt import ToolNode

def agent_node(state):
    msg = llm_with_tools.invoke(state["messages"])
    return {"messages": [msg]}

def should_continue(state):
    last = state["messages"][-1]
    return "tools" if last.tool_calls else END

g = StateGraph(State)
g.add_node("agent", agent_node)
g.add_node("tools", ToolNode(tools))

g.set_entry_point("agent")
g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
g.add_edge("tools", "agent")
```

ใช้: ReAct, tool-using agent

---

## 5. Pattern 3: Parallel Branches

```
            ┌─▶ B1 ─┐
   A ───────┼─▶ B2 ─┼─▶ Aggregator
            └─▶ B3 ─┘
```

LangGraph 0.2+ รองรับ parallel ผ่าน multiple `add_edge` จาก node เดียวกัน + reducer

```python
class State(TypedDict):
    messages: list
    branch_results: Annotated[list, add]  # collect from parallel branches

def branch_a(s): return {"branch_results": [llm("aspect A: " + s["topic"])]}
def branch_b(s): return {"branch_results": [llm("aspect B: " + s["topic"])]}
def branch_c(s): return {"branch_results": [llm("aspect C: " + s["topic"])]}

def aggregator(s):
    summary = llm("Synthesize: " + str(s["branch_results"]))
    return {"messages": [summary]}

g.add_node("branch_a", branch_a)
g.add_node("branch_b", branch_b)
g.add_node("branch_c", branch_c)
g.add_node("aggregator", aggregator)

g.set_entry_point("branch_a")  # หรือใช้ Router node ที่ fanout
# fanout
g.add_edge(START, "branch_a")
g.add_edge(START, "branch_b")
g.add_edge(START, "branch_c")
# fan-in
g.add_edge("branch_a", "aggregator")
g.add_edge("branch_b", "aggregator")
g.add_edge("branch_c", "aggregator")
g.add_edge("aggregator", END)
```

LangGraph จะ run branch_a/b/c parallel โดยอัตโนมัติเมื่อมาถึง START → multi-fanout

ใช้: sectioning, voting, parallel specialists

---

## 6. Pattern 4: Send (Dynamic Parallel)

ถ้าจำนวน branch ไม่รู้ล่วงหน้า → ใช้ `Send`

```python
from langgraph.constants import Send

def fan_out(state):
    return [Send("worker", {"task": t}) for t in state["tasks"]]

def worker(state):
    return {"results": [process(state["task"])]}

g.add_node("planner", planner_node)
g.add_node("worker", worker)
g.add_node("aggregator", aggregator)

g.add_conditional_edges("planner", fan_out, ["worker"])
g.add_edge("worker", "aggregator")
```

ใช้: orchestrator-workers ที่ task list dynamic (ตาม [02 §pattern 4](../02_Design_Patterns.md))

---

## 7. Pattern 5: Checkpointing (Resumable)

```python
from langgraph.checkpoint.postgres import PostgresSaver
# หรือ
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

with PostgresSaver.from_conn_string("postgresql://...") as checkpointer:
    app = g.compile(checkpointer=checkpointer)
    
    config = {"configurable": {"thread_id": "user-123"}}
    
    # First call
    app.invoke({"messages": [HumanMessage("hi")]}, config=config)
    
    # Crash...
    
    # Resume — picks up from last checkpoint
    app.invoke({"messages": [HumanMessage("continue")]}, config=config)
```

**Use case**: 
- Long-running agent (resume after crash)
- Multi-turn conversation (state across messages)
- Time-travel debugging (`get_state_history()`)

---

## 8. Pattern 6: Human-in-the-Loop

### 8a. Interrupt before/after node

```python
app = g.compile(
    checkpointer=checkpointer,
    interrupt_before=["execute_payment"],  # pause here
)

# Agent runs until interrupt
state = app.invoke({"messages": [...]}, config=config)

# Show pending action to user
print(app.get_state(config).next)  # "execute_payment"

# User reviews... approves
app.invoke(None, config=config)  # resume
```

### 8b. Update state from human

```python
# Human edits state
app.update_state(config, {"messages": [HumanMessage("Change amount to $50")]})
app.invoke(None, config=config)
```

### 8c. NodeInterrupt (dynamic)

```python
from langgraph.errors import NodeInterrupt

def review_node(state):
    if state["amount"] > 1000:
        raise NodeInterrupt(f"Amount ${state['amount']} requires approval")
    return state
```

---

## 9. Pattern 7: Subgraphs

แตก subagent เป็น subgraph

```python
# Subgraph
sub_g = StateGraph(SubState)
sub_g.add_node("research", research_node)
sub_g.add_node("write", write_node)
sub_g.set_entry_point("research")
sub_g.add_edge("research", "write")
sub_g.add_edge("write", END)
sub_app = sub_g.compile()

# Parent graph
parent_g = StateGraph(ParentState)
parent_g.add_node("planner", planner_node)
parent_g.add_node("subagent", sub_app)  # subgraph as node!
parent_g.add_node("review", review_node)
```

State translation:
```python
def to_sub_state(parent_s): return {"topic": parent_s["topic"]}
def from_sub_state(sub_s): return {"draft": sub_s["draft"]}
```

ใช้: hierarchical agent (จาก [02 pattern 11](../02_Design_Patterns.md))

---

## 10. Pattern 8: Multi-Agent Supervisor

```
              ┌──────────────┐
              │  Supervisor  │  decides next agent
              └──────┬───────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌────────┐  ┌────────┐  ┌────────┐
   │Agent A │  │Agent B │  │Agent C │
   └────────┘  └────────┘  └────────┘
        │            │            │
        └────────────┼────────────┘
                     │
                     ▼ (back to supervisor)
```

```python
from typing import Literal

class State(TypedDict):
    messages: list
    next: Literal["agent_a", "agent_b", "agent_c", "FINISH"]

def supervisor(state):
    decision = llm.invoke(f"""
    Conversation: {state['messages']}
    Next agent (a/b/c) or FINISH?
    """)
    return {"next": decision}

def route(state):
    return state["next"]

g.add_node("supervisor", supervisor)
g.add_node("agent_a", agent_a_node)
g.add_node("agent_b", agent_b_node)
g.add_node("agent_c", agent_c_node)

g.set_entry_point("supervisor")
g.add_conditional_edges("supervisor", route, {
    "agent_a": "agent_a",
    "agent_b": "agent_b",
    "agent_c": "agent_c",
    "FINISH": END,
})
g.add_edge("agent_a", "supervisor")
g.add_edge("agent_b", "supervisor")
g.add_edge("agent_c", "supervisor")
```

ใช้: tasks ที่ต้อง re-route หลายรอบ

---

## 11. Pattern 9: Self-RAG (Retrieve → Critique → Re-retrieve)

```
Question
    ▼
Retrieve
    ▼
Grade docs
    ├──▶ relevant ──▶ Generate ──▶ Grade hallucination ──▶ END
    └──▶ not relevant ──▶ Rewrite query ──▶ Retrieve (loop)
```

```python
def grade_docs(state):
    grades = [llm_grade(doc, state["question"]) for doc in state["docs"]]
    relevant = [d for d, g in zip(state["docs"], grades) if g == "yes"]
    if not relevant:
        return {"next": "rewrite"}
    return {"next": "generate", "docs": relevant}

def rewrite(state):
    new_q = llm.invoke(f"Rewrite for better retrieval: {state['question']}")
    return {"question": new_q}

def generate(state):
    answer = llm.invoke(f"Q: {state['question']} Docs: {state['docs']}")
    return {"answer": answer, "next": "check"}

def check_hallucination(state):
    grade = llm_grade_groundedness(state["answer"], state["docs"])
    return {"next": "END" if grade == "grounded" else "generate"}
```

---

## 12. State Patterns

### 12a. Messages (LangGraph idiom)

```python
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]  # smart merge
```

`add_messages` reducer:
- Append by default
- ถ้า message id ซ้ำ → replace (เพื่อ update ของเก่า)
- รองรับ delete: `RemoveMessage(id=...)`

### 12b. Multi-key state

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
    plan: list[str]
    completed_steps: Annotated[list[str], add]
    final_answer: str | None
```

แต่ละ node update เฉพาะ key ที่ตัวเอง concern

### 12c. Pydantic state

```python
from pydantic import BaseModel

class State(BaseModel):
    messages: list = []
    plan: list[str] = []
    
    def is_complete(self) -> bool:
        return len(self.plan) == 0
```

LangGraph รองรับ Pydantic v2 directly — type safety + methods

---

## 13. Streaming

LangGraph มี 5 stream modes:

```python
# 1. values — ทุก state update
for s in app.stream(input, stream_mode="values"):
    print(s)

# 2. updates — เฉพาะ delta จาก node
for s in app.stream(input, stream_mode="updates"):
    print(s)  # {"node_name": {"key": value}}

# 3. messages — token-level streaming
for msg, meta in app.stream(input, stream_mode="messages"):
    print(msg.content, end="")

# 4. debug — verbose
# 5. custom — your custom events
from langgraph.config import get_stream_writer
writer = get_stream_writer()
writer({"progress": 50})
```

---

## 14. Error Handling

### 14a. Retry per node

```python
from langgraph.utils.runnable import RunnableCallable

def my_node(state):
    ...

g.add_node("my_node", my_node, retry=RetryPolicy(max_attempts=3))
```

### 14b. Try/except in node

```python
def safe_node(state):
    try:
        return {"result": risky_operation()}
    except Exception as e:
        return {"result": None, "error": str(e), "next": "fallback"}
```

### 14c. Recursion limit

```python
app.invoke(input, config={"recursion_limit": 50})
```

Default = 25; ป้องกัน infinite loop

---

## 15. Testing

### 15a. Unit test node

```python
def test_planner():
    state = {"messages": [HumanMessage("plan trip")]}
    result = planner_node(state)
    assert "plan" in result
    assert len(result["plan"]) > 0
```

### 15b. Integration test graph

```python
def test_full_flow():
    app = build_graph()
    final = app.invoke({"messages": [HumanMessage("test")]})
    assert "answer" in final
```

### 15c. Mock LLM

```python
from unittest.mock import patch

@patch("src.llm.client.invoke")
def test_with_mock(mock_llm):
    mock_llm.return_value = AIMessage("mocked")
    ...
```

### 15d. Snapshot test for state

```python
config = {"configurable": {"thread_id": "test-1"}}
app.invoke({"messages": [HumanMessage("hi")]}, config=config)
snapshot = app.get_state(config)
assert snapshot.values["messages"][-1].content == "expected"
```

---

## 16. Time Travel & Debug

```python
# Replay from a specific checkpoint
history = list(app.get_state_history(config))
# history[0] = latest, [-1] = earliest

# Pick a past state
old_state = history[5]

# Resume from there with modification
new_config = old_state.config
app.update_state(new_config, {"messages": [HumanMessage("different input")]})
app.invoke(None, new_config)
# Creates a new branch from history[5]
```

---

## 17. Visualization

```python
from IPython.display import Image
Image(app.get_graph().draw_mermaid_png())

# Or text-based
print(app.get_graph().draw_ascii())
```

หรือ export Mermaid:
```python
print(app.get_graph().draw_mermaid())
# paste into mermaid.live
```

---

## 18. LangGraph Studio (UI debugger)

```bash
pip install langgraph-cli[inmem]
langgraph dev
```

เปิดเบราเซอร์ → เห็น graph + state ทุก step + edit + replay

ดีมากสำหรับ debug agent ที่ซับซ้อน

---

## 19. Pattern สำหรับ Case Study (จาก 07)

### Coordinator Graph (สำหรับ e-commerce builder)

```python
from langgraph.graph import StateGraph, END, START

class ProjectState(TypedDict):
    project_id: str
    requirements: str | None
    architecture: str | None
    designs: dict
    issues: Annotated[list[str], add]
    code_repo_path: str | None
    budget_used: float

def analyst(s): ...     # → requirements
def architect(s): ...   # → architecture
def dba(s): ...
def backend(s): ...
def frontend(s): ...
def devops(s): ...
def reviewer(s): ...
def scaffold(s): ...

g = StateGraph(ProjectState)

# Nodes
g.add_node("analyst", analyst)
g.add_node("architect", architect)
g.add_node("dba", dba)
g.add_node("backend", backend)
g.add_node("frontend", frontend)
g.add_node("devops", devops)
g.add_node("reviewer", reviewer)
g.add_node("scaffold", scaffold)

# Linear: analyst → architect
g.add_edge(START, "analyst")
g.add_edge("analyst", "architect")

# Fan-out from architect to 4 designers (parallel)
g.add_edge("architect", "dba")
g.add_edge("architect", "backend")
g.add_edge("architect", "frontend")
g.add_edge("architect", "devops")

# Fan-in to reviewer
g.add_edge("dba", "reviewer")
g.add_edge("backend", "reviewer")
g.add_edge("frontend", "reviewer")
g.add_edge("devops", "reviewer")

# Reviewer → scaffold or loop
g.add_conditional_edges(
    "reviewer",
    lambda s: "scaffold" if not s["issues"] else "fix",
    {"scaffold": "scaffold", "fix": "dba"},  # simplified loop
)

g.add_edge("scaffold", END)

app = g.compile(
    checkpointer=PostgresSaver(...),
    interrupt_before=["architect", "dba"],  # HITL
)
```

---

## 20. Common Mistakes

### ❌ Mutate state in node (don't return)
```python
# ❌
def bad(s):
    s["counter"] += 1  # mutation
    # no return

# ✅
def good(s):
    return {"counter": s["counter"] + 1}
```

### ❌ Heavy work outside checkpointer
Heavy IO หรือ external call ใน node → checkpoint บันทึกหลังเสร็จ → ถ้าพังกลางทาง state หาย

ทำให้ idempotent หรือ split เป็น sub-step

### ❌ State ใหญ่เกินไป
ทุก checkpoint บันทึก state ทั้งหมด → DB โต
แก้: เก็บ artifact เป็น file/blob, state ถือ ref เท่านั้น

### ❌ ไม่มี recursion_limit
Loop แล้ว loop ไปเรื่อย — ตั้ง limit เสมอ

---

## 21. Summary

- LangGraph = state machine สำหรับ agent
- 9 patterns ที่ครอบคลุม 95% case
- Checkpointing → resume + HITL + time travel
- Subgraphs → hierarchical
- Send → dynamic parallel
- Streaming → 5 modes
- Studio UI → debug
- เหมาะ production มากกว่า CrewAI/AutoGen สำหรับ workflow ที่ structured

**ต่อไป** → [02 Self-Hosted Stack](02_Self_Hosted_Stack.md) — เอา LangGraph ไปรันกับ Docker

---

## References

- [LangGraph docs](https://langchain-ai.github.io/langgraph/)
- [LangGraph tutorials](https://langchain-ai.github.io/langgraph/tutorials/)
- [LangChain academy](https://academy.langchain.com/) — free LangGraph course
