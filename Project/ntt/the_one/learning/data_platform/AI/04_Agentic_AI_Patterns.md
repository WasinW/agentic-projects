# Agentic AI — Patterns & Production

> Multi-step LLM systems ที่วางแผนเอง ใช้เครื่องมือ และทำงานเสร็จ
> Frontier ของ AI Platform ปี 2026

---

## 1. Agent คืออะไร — แยกจาก RAG ให้ชัด

### RAG vs Agent

| Aspect | RAG | Agent |
|---|---|---|
| Input | 1 query | 1 task / goal |
| Output | 1 response | sequence of actions + final answer |
| Steps | Single LLM call | Multiple LLM calls + tool calls |
| Decision-making | None | Yes (plan + reflect) |
| State | Stateless | Stateful (memory) |
| Tools | Just retrieval | Many (search, API, code, browse) |
| Reliability | High | Lower (compound failures) |
| Cost | Low | High (multiple calls) |

### Agent Definition (2026)

> An **AI Agent** is a system that uses an LLM to decide what to do next, given a goal, while interacting with tools, memory, and possibly other agents.

### Anatomy of an Agent

```
┌────────────────────────────────────────────────┐
│                   GOAL                         │
│      "Book me a flight to Tokyo next week"     │
└──────────────────────┬─────────────────────────┘
                       ▼
┌────────────────────────────────────────────────┐
│                LLM (Brain)                     │
│    Plan + Reason + Decide                      │
└─────────┬────────────────────────────┬─────────┘
          │                            │
          ▼                            ▼
┌──────────────────┐          ┌──────────────────┐
│      TOOLS       │          │     MEMORY       │
│  • Web search    │          │  • Short-term    │
│  • API calls     │          │    (this convo)  │
│  • Database query│          │  • Long-term     │
│  • Code execute  │          │    (history)     │
└──────────────────┘          └──────────────────┘
```

---

## 2. Agent Patterns — 5 Common Patterns

### Pattern 1: ReAct (Reason + Act)

The classic pattern (Yao et al., 2022):

```
Loop:
  1. Thought: "I need to find flights to Tokyo"
  2. Action: search_flights(dest="Tokyo", date="next week")
  3. Observation: [list of flights]
  4. Thought: "I should compare prices"
  5. Action: ...
  6. ...
  Final Answer: "Here's the best option..."
```

```python
# Pseudocode
def react_agent(goal, tools, max_iterations=10):
    history = []
    for _ in range(max_iterations):
        prompt = build_prompt(goal, history, available_tools=tools)
        response = llm(prompt)
        
        thought = parse_thought(response)
        if "Final Answer:" in response:
            return parse_final_answer(response)
        
        action_name, args = parse_action(response)
        observation = tools[action_name](**args)
        
        history.append((thought, action_name, args, observation))
    
    return "Max iterations reached"
```

### Pattern 2: Plan-and-Execute

วางแผนทั้งหมดก่อน แล้วค่อย execute:

```
Step 1: Plan
  LLM: "To book a flight, I need to:
        1. Search flights
        2. Filter by budget
        3. Pick best
        4. Book selected"

Step 2: Execute each step
  Run plan items sequentially or in parallel
  
Step 3: Re-plan if needed
  If step fails, generate new plan
```

**Pros**: more efficient (fewer LLM calls than ReAct)
**Cons**: less adaptive

### Pattern 3: Reflexion

Agent reflects on its work:

```
1. Attempt task
2. Self-evaluate: "Was the answer good?"
3. If not, identify what went wrong
4. Retry with improved approach
5. Loop until satisfactory
```

### Pattern 4: Multi-Agent Collaboration

```
                    ┌─────────────────┐
                    │   ORCHESTRATOR  │
                    │     AGENT       │
                    └─────┬───────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   ┌─────────┐      ┌─────────┐      ┌─────────┐
   │Researcher│     │ Writer  │      │ Reviewer│
   │  Agent   │     │ Agent   │      │  Agent  │
   └─────────┘      └─────────┘      └─────────┘
```

Each agent has:
- Specific role
- Specific tools
- Specific personality

### Pattern 5: Hierarchical Agent

```
Manager Agent
   ↓ delegates
Worker Agent 1 (specialist A)
   ↓ may delegate further
Sub-worker A1
```

---

## 3. Frameworks Comparison (2026)

### LangGraph (LangChain ecosystem)

**Approach**: Graph-based, explicit state machine

```python
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    messages: list
    next_step: str

workflow = StateGraph(AgentState)

workflow.add_node("planner", plan_node)
workflow.add_node("researcher", research_node)
workflow.add_node("writer", write_node)
workflow.add_node("reviewer", review_node)

# Define edges
workflow.set_entry_point("planner")
workflow.add_edge("planner", "researcher")
workflow.add_conditional_edges(
    "researcher",
    lambda state: state["next_step"],
    {
        "needs_more_research": "researcher",
        "ready_to_write": "writer"
    }
)
workflow.add_edge("writer", "reviewer")
workflow.add_conditional_edges(
    "reviewer",
    lambda state: "approved" if state["approved"] else "writer",
    {"approved": END, "writer": "writer"}
)

app = workflow.compile()
```

**Pros**:
- Explicit state, debuggable
- Built-in checkpointing (time-travel)
- Production-grade (audit trails)
- Conditional logic clear

**Cons**:
- Verbose
- Learning curve

**Best for**: Production agents, complex workflows

### CrewAI

**Approach**: Role-based teams (DSL-style)

```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Senior Researcher",
    goal="Find latest info on {topic}",
    backstory="Expert at web research...",
    tools=[search_tool, scrape_tool],
)

writer = Agent(
    role="Tech Writer",
    goal="Write engaging articles",
    backstory="Award-winning writer...",
    tools=[],
)

research_task = Task(
    description="Research {topic}",
    agent=researcher,
)

write_task = Task(
    description="Write article based on research",
    agent=writer,
    context=[research_task],
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    verbose=True,
)

result = crew.kickoff(inputs={"topic": "AI in 2026"})
```

**Pros**:
- Easy to start (low learning curve)
- Built-in memory (short + long term)
- Role-based mental model
- 20+ pre-built tools

**Cons**:
- Less flexible than LangGraph
- Production audit harder

**Best for**: Quick prototypes, content generation, business workflows

### AutoGen (Microsoft)

**Approach**: Conversational agents

```python
from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent(
    name="assistant",
    llm_config={"model": "gpt-4o"},
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "coding"},
)

user_proxy.initiate_chat(
    assistant,
    message="Plot Tesla stock price for the last year"
)
# Agents converse, write code, execute, iterate
```

**Pros**:
- Strong code execution
- Conversational paradigm
- Multi-agent natural

**Cons**:
- Tools manual (no pre-built)
- Less production-ready

**Best for**: Code generation, data analysis tasks

### Claude Code SDK / OpenAI Agents SDK

**Approach**: Provider-native agent frameworks (2024-2025+)

```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    tools=[
        {
            "name": "search_flights",
            "description": "Search for flights",
            "input_schema": {...}
        },
        {
            "name": "book_flight",
            "description": "Book a specific flight",
            "input_schema": {...}
        }
    ],
    messages=[{"role": "user", "content": "Book me to Tokyo"}]
)

# Handle tool use
if response.stop_reason == "tool_use":
    tool_call = response.content[0]
    result = execute_tool(tool_call.name, tool_call.input)
    # Continue conversation with result
```

**Pros**:
- Provider-optimized
- Best tool use quality
- Computer use capabilities

**Cons**:
- Locked to provider

### Comparison Summary (2026)

| Framework | Maturity | Production-ready | Learning Curve | Tool Ecosystem |
|---|---|---|---|---|
| LangGraph | High | ✅ Best | Medium | 100+ via LangChain |
| CrewAI | Medium-High | Good | Low | 20+ pre-built |
| AutoGen | Medium | OK | Medium | Manual |
| Claude Code SDK | New | Growing | Low | Native + MCP |

**ปี 2026 trend**: LangGraph แซง CrewAI ใน enterprise เพราะ production features

---

## 4. Tool Use — How LLMs Call Functions

### Anatomy of a Tool

```python
def search_database(query: str, table: str, limit: int = 10) -> list[dict]:
    """Search internal database for records.
    
    Args:
        query: Search keywords
        table: Table to search (orders, customers, products)
        limit: Max results
        
    Returns:
        List of matching records
    """
    # Implementation
    return db.search(query, table, limit)
```

### Tool Definition (JSON Schema)

```python
tool_definition = {
    "name": "search_database",
    "description": "Search internal database for records",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search keywords"
            },
            "table": {
                "type": "string",
                "enum": ["orders", "customers", "products"],
                "description": "Table to search"
            },
            "limit": {
                "type": "integer",
                "default": 10,
                "description": "Max results"
            }
        },
        "required": ["query", "table"]
    }
}
```

### Tool Use Loop

```python
def agent_loop(user_query, tools):
    messages = [{"role": "user", "content": user_query}]
    
    while True:
        response = llm.create(
            messages=messages,
            tools=[tool_def for tool_def in tools.values()]
        )
        
        # Check if LLM wants to use tool
        if response.stop_reason == "tool_use":
            tool_use = response.tool_use
            tool_result = tools[tool_use.name](**tool_use.input)
            
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": str(tool_result)
                }]
            })
            continue  # LLM may use another tool
        
        # Final response
        return response.content[0].text
```

### Tool Design Principles

#### Principle 1: Atomic & Composable
❌ `do_everything(complex_input)` — one big tool
✅ `search()` + `filter()` + `format()` — composable

#### Principle 2: Clear Names + Descriptions
```python
# Bad
def func1(s: str) -> str: ...

# Good
def lookup_customer_by_email(email: str) -> Customer:
    """Find customer by email address.
    
    Returns customer profile with name, status, last_login.
    Returns None if not found.
    """
```

#### Principle 3: Strong Typing
```python
# Bad
def search(query) -> dict: ...

# Good
def search(query: str, max_results: int = 10) -> list[SearchResult]:
    ...
```

#### Principle 4: Idempotent (when possible)
```python
# Read tools = idempotent
def get_customer(id: str) -> Customer

# Write tools = NOT idempotent (handle carefully)
def create_order(...) -> OrderId  # may create duplicates
def create_order(idempotency_key: str, ...) -> OrderId  # safe
```

#### Principle 5: Observable
- Log all tool calls
- Track success/failure rates
- Measure latency
- Cost tracking

---

## 5. Memory Management

### Why Agents Need Memory

```
Without memory:
  User: "What's my favorite color?"
  Agent: "I don't know."
  User: (later) "Tell me my favorite color"
  Agent: "I still don't know."
  
With memory:
  User: "My favorite color is blue"
  → Agent stores: {"user_pref": {"fav_color": "blue"}}
  User: (later) "What's my favorite color?"
  Agent: "Blue."
```

### Memory Types

#### 1. Short-Term (Conversational)
- Current conversation history
- Within context window
- Stored in messages array

```python
messages = [
    {"role": "user", "content": "I love Tokyo"},
    {"role": "assistant", "content": "Great choice!"},
    {"role": "user", "content": "Recommend hotels there"}  # uses context
]
```

#### 2. Long-Term (Persistent)
- Across sessions
- Stored in database
- Retrieved as relevant

```python
# At conversation end, extract + store
extract_facts(conversation) → {
    "user_preferences": {"likes_tokyo": true},
    "last_trip": "2026-04-15",
    "budget_pref": "mid-range"
}
store_in_db(user_id, facts)

# Next conversation, retrieve
facts = load_from_db(user_id)
system_prompt = build_with_facts(facts)
```

#### 3. Episodic Memory
- Specific past events
- "Last week we discussed X"

```python
episodic_db.add({
    "user_id": "u123",
    "session_id": "s456",
    "summary": "Discussed budget travel to Tokyo",
    "key_facts": ["budget: $2000", "dates: April"],
    "timestamp": "2026-04-15"
})
```

#### 4. Semantic Memory
- General knowledge about user/world
- Vector store + retrieval

```python
# When discussing finance
relevant_memories = vector_search(
    query="user financial situation",
    namespace=f"user_{user_id}"
)
```

### Memory Implementation Patterns

#### Pattern A: Context Window Management

```python
class ConversationMemory:
    def __init__(self, max_tokens=8000):
        self.messages = []
        self.max_tokens = max_tokens
    
    def add(self, message):
        self.messages.append(message)
        self.compress_if_needed()
    
    def compress_if_needed(self):
        if self.token_count() > self.max_tokens:
            # Summarize older messages
            older = self.messages[:-10]
            recent = self.messages[-10:]
            summary = llm(f"Summarize: {older}")
            self.messages = [{"role": "system", "content": f"Previous: {summary}"}] + recent
```

#### Pattern B: Vector Memory

```python
class SemanticMemory:
    def __init__(self):
        self.vector_store = ChromaClient()
    
    def remember(self, user_id, fact):
        embedding = embed(fact)
        self.vector_store.add(
            user_id=user_id,
            text=fact,
            embedding=embedding,
            timestamp=now()
        )
    
    def recall(self, user_id, query, top_k=5):
        query_emb = embed(query)
        results = self.vector_store.search(
            namespace=user_id,
            embedding=query_emb,
            top_k=top_k
        )
        return [r.text for r in results]
```

#### Pattern C: LangGraph Checkpointing

```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver(connection_string="...")

app = workflow.compile(checkpointer=checkpointer)

# Run with thread_id
config = {"configurable": {"thread_id": "user_123_session_456"}}
result = app.invoke({"messages": [...]}, config)

# Resume later — full state restored
result = app.invoke({"messages": [new_message]}, config)
```

---

## 6. Production Concerns

### 6.1 Reliability — Compound Failure

ปัญหา: Agent มีหลาย step → ถ้า each step มี 95% reliability:
- 5 steps: 0.95^5 = 77%
- 10 steps: 0.95^10 = 60%
- 20 steps: 0.95^20 = 36%

**กฎเหล็ก**: น้อย step = ดีกว่า

### Strategies for Reliability

#### Strategy 1: Limit Iterations
```python
agent = create_agent(max_iterations=8)  # hard limit
```

#### Strategy 2: Validation at Each Step
```python
def validate_step(action, args, expected_schema):
    if not matches_schema(args, expected_schema):
        return "Invalid arguments"
    if action not in allowed_actions:
        return "Unknown action"
    return None
```

#### Strategy 3: Checkpointing + Recovery
```python
# Save state every step
# On failure, resume from checkpoint, not restart
```

#### Strategy 4: Human Approval Gates
```python
def execute_critical(action, args):
    if action.is_destructive:
        approval = request_human_approval(action, args)
        if not approval:
            return "Cancelled"
    return execute(action, args)
```

#### Strategy 5: Fallback to Simpler Pattern
```python
try:
    result = complex_agent.run(query)
except ComplexFailureError:
    result = simple_rag.run(query)  # fallback
```

### 6.2 Cost Control

Agent calls = O(steps × tokens × model)

```
Simple chatbot: ~$0.01 per conversation
Agent (5 steps): ~$0.10 per conversation  
Multi-agent (3 agents × 5 steps): ~$0.50 per conversation
```

**Optimization**:
1. **Cheap models for tool selection** (router agent uses Haiku)
2. **Expensive only for complex reasoning** (final answer uses Opus)
3. **Cache tool results** (same query → same result)
4. **Short max_tokens** per intermediate step
5. **Early stopping** when confident

### 6.3 Observability

```python
@trace
def agent_run(goal):
    with tracer.start_as_current_span("agent_execution") as span:
        span.set_attribute("goal", goal)
        span.set_attribute("agent_version", "v2.4")
        
        for step in plan(goal):
            with tracer.start_as_current_span(f"step_{step.name}") as step_span:
                step_span.set_attribute("tool", step.tool)
                result = step.execute()
                step_span.set_attribute("result_size", len(str(result)))
        
        return final_answer
```

Each agent run logs:
- Goal + final answer
- Number of steps
- Tools used (and how often)
- Tokens consumed (per step + total)
- Latency (per step + total)
- Cost
- Errors / retries

### 6.4 Safety

#### Action Authorization
```python
class ActionAuthority:
    READ_ONLY = ["search", "lookup", "summarize"]
    USER_AUTHORIZED = ["send_email", "create_order"]
    ADMIN_ONLY = ["delete_account", "modify_pricing"]
    NEVER = ["transfer_funds_external"]  # AI cannot do this
    
    def can_execute(self, action, user_context):
        if action in self.NEVER:
            return False
        if action in self.READ_ONLY:
            return True
        if action in self.USER_AUTHORIZED:
            return user_context.has_permission(action)
        if action in self.ADMIN_ONLY:
            return user_context.is_admin
```

#### Guardrails on Agent Actions
```python
def safe_execute(action, args):
    # Pre-check
    if guardrails.input_check(action, args).blocked:
        return "Action blocked by policy"
    
    # Execute
    result = action.run(**args)
    
    # Post-check
    if guardrails.output_check(result).blocked:
        return "Result filtered by policy"
    
    return result
```

#### Sandboxed Code Execution
```python
def execute_code_safely(code: str):
    # Run in isolated container
    container = docker.run(
        image="python-sandbox:latest",
        command=["python", "-c", code],
        network="none",      # no internet
        memory_limit="512m",
        cpu_limit="1.0",
        timeout=30,
        read_only_root=True,
    )
    return container.output
```

---

## 7. Multi-Agent Architectures

### Architecture 1: Centralized Orchestrator

```
       User
        ↓
  [Orchestrator]
   ↓    ↓    ↓
  A1   A2   A3
```

- One agent decides who does what
- Easier to control
- Bottleneck at orchestrator

### Architecture 2: Decentralized

```
   User → A1 → A2 → A3 → User
              ↑
             A4 (when needed)
```

- Agents pass to each other
- More flexible
- Harder to predict behavior

### Architecture 3: Blackboard

```
   ┌───────────────────┐
   │   Shared State    │
   │   (Blackboard)    │
   └─────┬───┬───┬─────┘
         │   │   │
         A1  A2  A3
         (read+write)
```

- Agents communicate via shared state
- Good for collaborative tasks
- Used in CrewAI

### Architecture 4: Hierarchical

```
        Manager
       /   |   \
   Lead1 Lead2 Lead3
    /\    /\    /\
   W  W  W  W  W  W
```

- Multiple levels of delegation
- Scales to complex tasks
- Used in Microsoft Magentic-One

---

## 8. Real-World Agent Use Cases

### Use Case 1: Customer Support Triage

```
User: "I want to cancel my order"
        ↓
  [Triage Agent] → classify intent
        ↓
  [Order Lookup Agent] → find user's orders
        ↓
  [Cancellation Agent] → check eligibility, process
        ↓
  [Confirmation Agent] → send email, update DB
        ↓
  Final response to user
```

### Use Case 2: Code Generation

```
User: "Build a REST API for user management"
        ↓
  [Architect Agent] → design API spec
        ↓
  [Developer Agent] → write code
        ↓
  [Tester Agent] → write + run tests
        ↓
  [Reviewer Agent] → code review
        ↓
  Output: working code + tests
```

### Use Case 3: Data Analysis

```
User: "Analyze Q1 sales trends"
        ↓
  [Data Agent] → query database
        ↓
  [Analyst Agent] → identify trends
        ↓
  [Visualizer Agent] → create charts
        ↓
  [Writer Agent] → narrative report
        ↓
  Output: charts + report
```

### Use Case 4: Research Assistant

```
User: "Research competitors of company X"
        ↓
  [Searcher Agent] → web search + crawl
        ↓
  [Extractor Agent] → extract key facts
        ↓
  [Verifier Agent] → cross-check sources
        ↓
  [Summarizer Agent] → consolidate
        ↓
  Output: research brief with citations
```

---

## 9. Agent Evaluation

### Standard Benchmarks (2026)

| Benchmark | What |
|---|---|
| **SWE-bench** | Solve real GitHub issues |
| **WebArena** | Navigate web tasks |
| **AgentBench** | General agent capabilities |
| **GAIA** | Reasoning + tool use |
| **τ-bench** | Customer service scenarios |

### Custom Eval Pattern

```yaml
test_cases:
  - id: "support_001"
    goal: "Cancel order ORD-12345"
    expected_outcome:
      tools_called:
        - lookup_order
        - cancel_order
        - send_confirmation
      max_steps: 5
      success_criteria:
        - order_status == "cancelled"
        - email_sent == true
    
  - id: "support_002"
    goal: "Get refund for damaged product"
    expected_outcome:
      tools_called: [lookup_order, file_complaint, escalate_to_human]
      should_escalate: true
```

### Metrics

| Metric | What |
|---|---|
| **Task Completion Rate** | % of tasks completed successfully |
| **Step Efficiency** | Steps used vs minimum needed |
| **Tool Use Accuracy** | Right tool for the job |
| **Cost per Task** | Tokens × $$ |
| **Latency per Task** | End-to-end time |
| **Safety Score** | No harmful/wrong actions |

---

## 10. Production Deployment Checklist

### Architecture
- [ ] Choose framework (LangGraph for production)
- [ ] Define state schema
- [ ] Define tool catalog
- [ ] Design memory strategy
- [ ] Plan for failures (max iterations, fallback)

### Reliability
- [ ] Test golden path
- [ ] Test failure modes (tool errors, LLM errors)
- [ ] Implement checkpointing
- [ ] Set max iterations
- [ ] Add validation per step

### Safety
- [ ] Define authority levels (read/write/never)
- [ ] Add input/output guardrails
- [ ] Sandbox code execution
- [ ] Approval gates for critical actions
- [ ] Audit logging mandatory

### Observability
- [ ] Trace every agent run
- [ ] Per-step latency + cost
- [ ] Tool usage frequency
- [ ] Error categorization
- [ ] Dashboard

### Cost
- [ ] Smart model routing (cheap for routing, expensive for reasoning)
- [ ] Tool result caching
- [ ] Token limits per step
- [ ] Cost alerts

### Eval
- [ ] Golden test set
- [ ] Regression tests pre-deploy
- [ ] Online quality monitoring
- [ ] User feedback collection

---

## 11. Future Trends (2026-2027)

### Trend 1: Computer Use
LLMs can control screen, mouse, keyboard
- Anthropic Claude Computer Use
- OpenAI Operator
- Use case: web automation

### Trend 2: Long-Horizon Agents
Multi-day tasks, persistent goals
- Agents that plan months ahead
- Self-improving over time

### Trend 3: Specialized Foundation Models for Agents
Models trained specifically for tool use
- Better than general LLMs at function calling
- Lower cost, higher reliability

### Trend 4: Agent Marketplaces
Pre-built agent skills you can subscribe to
- Like app stores for agents
- Composable agent ecosystem

### Trend 5: Multi-Modal Agents
Text + voice + image + video
- Already starting (Gemini, GPT-5)
- Will become standard

---

## 12. Cheat Sheet

### Q: "Agent กับ RAG ต่างกันยังไง?"
> "RAG: 1 query → retrieve → 1 response (stateless)
> Agent: goal → multi-step plan + tool calls + memory → final result (stateful)"

### Q: "เลือก framework ไหน?"
> "LangGraph: production, audit-friendly (recommended ปี 2026)
> CrewAI: prototype เร็ว, role-based
> AutoGen: code generation
> Native SDK (Anthropic/OpenAI): provider-optimized"

### Q: "ทำไม agent reliability ต่ำ?"
> "Compound failure — 5 step × 95% reliability = 77% overall
> Solution: limit iterations, validate per step, checkpointing, human-in-loop for critical"

### Q: "Memory แบบไหนดี?"
> "Short-term: messages array (within context)
> Long-term: extract facts → store in DB
> Semantic: vector store for related context
> Production: ใช้ทั้ง 3 แบบรวมกัน"

### Q: "Cost agent control ยังไง?"
> "Cheap model for routing/simple tasks (Haiku)
> Expensive for reasoning (Opus)
> Cache tool results
> Limit max_tokens per step
> Early stopping with confidence check"

---

## เอกสารที่เกี่ยวข้อง

- [01_AI_Platform_Overview.md](01_AI_Platform_Overview.md) — overall AI platform
- [02_RAG_Architecture.md](02_RAG_Architecture.md) — agents often use RAG as a tool
- [03_LLMOps_and_Evaluation.md](03_LLMOps_and_Evaluation.md) — operations + eval
- [../ML/](../ML/) — Traditional ML platform
