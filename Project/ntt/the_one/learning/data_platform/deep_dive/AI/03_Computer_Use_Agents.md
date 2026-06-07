# Computer Use & Browser Agents — Deep Dive

> Anthropic Claude Computer Use, OpenAI Operator, browser automation
> Frontier of autonomous AI ปี 2026

---

## 1. What is Computer Use

> "AI agent that controls computer/browser like a human — clicks, types, scrolls, reads screen"

### Two Paradigms

#### Computer Use (Anthropic)
- Controls **entire desktop**
- Can use any app (browser, IDE, terminal, native apps)
- Looks at screenshots, controls mouse + keyboard

#### Browser Use / Operator (OpenAI, others)
- Controls **browser only**
- Uses DOM + screenshots
- More targeted to web automation

### Why Important Now (2026)

- Frontier capability — only Anthropic, OpenAI, Google
- Unlocks 100s of automation use cases
- Market growing 200%+ YoY
- Replacing manual back-office work

---

## 2. How Computer Use Works

### Anthropic Claude Computer Use Architecture

```
1. User: "Book me a flight to Tokyo"
        ↓
2. Claude takes screenshot
        ↓
3. Claude analyzes screen (vision)
   "I see the desktop. I'll open browser."
        ↓
4. Claude calls tool: 
   computer.action(action="key", text="cmd+space")
        ↓
5. Tool executes on real machine
        ↓
6. Take new screenshot
        ↓
7. Claude: "Spotlight open. Type 'chrome'"
   computer.action(action="type", text="chrome")
        ↓
[Loop until task complete]
```

### Tool API (Anthropic)

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    tools=[
        {
            "type": "computer_20241022",
            "name": "computer",
            "display_width_px": 1920,
            "display_height_px": 1080,
            "display_number": 1
        },
        {
            "type": "text_editor_20241022",
            "name": "str_replace_editor"
        },
        {
            "type": "bash_20241022",
            "name": "bash"
        }
    ],
    messages=[{
        "role": "user",
        "content": "Open Chrome and search for AI news"
    }],
    betas=["computer-use-2024-10-22"]
)
```

### Computer Tool Actions

```
key             - press key (cmd+t, esc)
type            - type text
mouse_move      - move cursor to x,y
left_click      - click at current position
left_click_drag - drag from start to end
right_click
middle_click
double_click
screenshot      - capture screen
cursor_position - get current x,y
```

---

## 3. Browser Use Architecture

### OpenAI Operator (Browser-Focused)

```
Limited to web browser:
  ✓ Web tasks (search, forms, shopping)
  ✗ Desktop apps
  ✗ Terminal commands
```

### Browser Use Library (OSS)

```python
from browser_use import Agent
from langchain_openai import ChatOpenAI

agent = Agent(
    task="Find the cheapest flight from BKK to NRT next week",
    llm=ChatOpenAI(model="gpt-4o"),
)

result = await agent.run()
```

### Architecture

```
User task
    ↓
[Browser Agent]
   ├─ Vision: read screenshots
   ├─ DOM access: find elements
   ├─ Action: click, type, scroll
   └─ Memory: remember progress
    ↓
[Real Browser (Playwright)]
    ↓
[Web pages]
```

---

## 4. Playwright + LLM (Custom Build)

### Architecture

```python
from playwright.async_api import async_playwright
import anthropic

class BrowserAgent:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.browser = None
        self.page = None
    
    async def setup(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch()
        self.page = await self.browser.new_page()
    
    async def screenshot(self):
        return await self.page.screenshot()
    
    async def get_dom(self):
        # Simplified DOM with element IDs
        return await self.page.evaluate("""() => {
            const elements = document.querySelectorAll('*');
            return Array.from(elements).map((el, i) => ({
                id: i,
                tag: el.tagName,
                text: el.innerText?.slice(0, 100),
                visible: el.offsetParent !== null,
            }));
        }""")
    
    async def click(self, element_id):
        await self.page.click(f'[data-agent-id="{element_id}"]')
    
    async def execute_task(self, task):
        for step in range(20):
            screenshot = await self.screenshot()
            dom = await self.get_dom()
            
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Task: {task}\n\nDOM: {dom}"},
                        {"type": "image", "source": {"type": "base64", "data": screenshot}}
                    ]
                }],
                tools=[
                    {"name": "click", "input_schema": {...}},
                    {"name": "type", "input_schema": {...}},
                    {"name": "scroll", "input_schema": {...}},
                    {"name": "done", "input_schema": {...}}
                ]
            )
            
            tool_call = parse_tool_call(response)
            if tool_call.name == "done":
                return tool_call.result
            
            await self.execute_action(tool_call)
```

---

## 5. Real Use Cases (2026)

### Use Case 1: Form Filling at Scale

```
Task: Fill 100 government forms with customer data

Traditional: 100 hours of human work
Agent: 2 hours of LLM work + supervision

Process:
1. Read CRM database
2. For each customer:
   - Open gov website
   - Fill form fields
   - Submit
   - Save confirmation
3. Report errors
```

### Use Case 2: Web Research & Reporting

```
Task: "Research top 10 competitors of Company X"

Agent:
1. Google search
2. Visit company websites
3. Extract: product, pricing, founding year, etc.
4. Compile spreadsheet
5. Send report

Time: 30 min (vs 4 hours human)
```

### Use Case 3: QA Testing

```
Task: "Test the checkout flow on staging"

Agent:
1. Navigate to product
2. Add to cart
3. Try various payment methods
4. Check error handling
5. Verify confirmation email
6. Report bugs found

vs. manual QA: 10x faster
```

### Use Case 4: Customer Support

```
Task: Help user reset password (when chatbot fails)

Agent:
1. Look up user account
2. Initiate password reset
3. Verify identity
4. Update internal notes
5. Email user
```

### Use Case 5: Data Migration

```
Task: Migrate data from legacy app to new system

Agent:
1. Export from old (UI-only legacy system)
2. Transform format
3. Import to new
4. Verify rows match
```

---

## 6. Reliability Challenges

### Problem 1: UI Changes Break Agent

```
Today: button at coords (500, 300)
Tomorrow: site redesign, button at (700, 250)
Agent: clicks wrong place
```

**Mitigation**:
- Use semantic targeting (by text, role) not coords
- Re-screenshot before each action
- Verify outcome after action

### Problem 2: Loading & Async

```
Agent clicks "Submit"
Page still loading...
Agent thinks task done
Actually error appeared after load
```

**Mitigation**:
- Wait for page idle (Playwright)
- Verify expected state after action
- Retry on uncertainty

### Problem 3: Multi-Step Failures

```
Step 1: ✓ login
Step 2: ✓ navigate
Step 3: ✗ wrong button
Step 4: agent now in unexpected state
```

**Mitigation**:
- Checkpoint progress
- Validate state at each step
- Error recovery patterns

### Problem 4: Authentication

```
Site requires CAPTCHA / 2FA
Agent can't solve
```

**Mitigation**:
- Pre-authenticate session
- Hand off to human for CAPTCHA
- Use cookie auth (skip 2FA)

---

## 7. Safety & Authority

### Critical: Don't Give Agent Unlimited Power

```
✅ ALLOWED:
  - Read files
  - Search web
  - Fill forms
  - Click harmless buttons

⚠️ REQUIRES APPROVAL:
  - Submit purchases
  - Send emails
  - Modify shared state
  - Delete files

❌ NEVER ALLOW:
  - Transfer money externally
  - Delete production data
  - Access secrets
  - Bypass security
```

### Implementation: Authority Levels

```python
class ActionAuthority:
    READ_ONLY = ["read", "search", "view", "scroll"]
    USER_AUTHORIZED = ["fill_form", "click_button", "send_email"]
    APPROVAL_REQUIRED = ["purchase", "delete", "modify_settings"]
    BLOCKED = ["transfer_money", "access_keys", "system_command"]
    
    def check(self, action, context):
        if action.type in self.BLOCKED:
            raise BlockedAction()
        if action.type in self.APPROVAL_REQUIRED:
            return self.request_human_approval(action)
        if action.type in self.USER_AUTHORIZED:
            return self.check_consent(action, context)
        return True
```

### Sandboxing

```
Run agent in:
  ✓ Isolated VM (no access to host)
  ✓ Limited network (whitelist domains)
  ✓ Read-only file system (where possible)
  ✓ Disposable session (delete after task)
```

```python
# Anthropic Computer Use suggested setup
# Run in Docker container with:
docker run \
    --memory=2g \
    --cpus=2 \
    --network=limited \
    --read-only \
    --tmpfs /tmp \
    computer-use-image
```

---

## 8. Cost Economics

### Cost per Task

```
Average task: 10-30 LLM calls + 10-30 screenshots
Each call: 1500-5000 tokens (image-heavy)

Per task estimate:
  Simple form fill: $0.10 - $0.50
  Complex research: $1 - $5
  Long workflow: $5 - $20
```

### Optimization

```python
# Reduce screenshot resolution
display_width=1280, display_height=720  # vs 1920x1080
# Tokens reduced by ~40%

# Use cheaper model for routing
router = "haiku"  # $0.80 / 1M tokens
worker = "sonnet"  # $3 / 1M tokens

# Cache when possible
prompt_caching=True  # 90% off cached system prompt
```

### When NOT Cost-Effective

```
Task: Fill 1 form per minute
Cost: $0.50/task × 60/hr = $30/hour
vs human: $20-30/hour

→ humans cheaper for high volume!

Computer Use better for:
- High value tasks
- 24/7 availability needed
- Unique varied tasks
```

---

## 9. Browser Automation Frameworks (2026)

### Playwright + Stagehand
```
Stagehand: AI layer on top of Playwright
Better than raw Playwright for automation
```

### browser-use (OSS)
```
LangChain-based
Vision + DOM hybrid
Quick to set up
```

### Selenium IDE + LLM
```
Legacy + modern
Less elegant but ubiquitous
```

### Anthropic Computer Use SDK
```
Direct from Anthropic
Best Claude integration
```

### OpenAI Operator API
```
Browser-focused
Native to OpenAI ecosystem
```

---

## 10. Production Deployment Patterns

### Pattern A: Async Job Queue

```
User submits task
    ↓
Queue (Redis/Celery)
    ↓
Worker pool (each = browser instance)
    ↓
Agent executes
    ↓
Result stored in DB
    ↓
User notified
```

### Pattern B: Real-Time Conversation

```
User chats with agent
   ↓
Agent decides if needs computer use
   ↓
"Let me find that for you..." (executes)
   ↓
Returns result inline
```

### Pattern C: Batch Processing

```
Schedule: nightly run
List: 1000 records to process
Distribute: 10 workers × 100 records
Each worker: browser + agent
```

### Infrastructure

```
Browser instances: containerized (Selenium Grid, Browserless)
LLM access: API-based (cheap to scale)
Persistence: track progress, recover on failure
Monitoring: per-task latency, success rate, cost
```

---

## 11. Evaluation

### Benchmarks

#### WebArena (academic)
- 812 web tasks
- E-commerce, forums, GitLab, etc.
- Realistic websites

#### VisualWebArena
- Visual + interactive tasks
- More challenging

#### OSWorld
- Desktop tasks (not just web)
- 369 real-world tasks
- For Computer Use evaluation

#### Mind2Web
- Cross-domain web tasks
- Diverse benchmark

### Custom Eval

```python
test_tasks = [
    {
        "task": "Find the contact email on homepage",
        "verify": lambda result: '@' in result and '.com' in result,
        "max_steps": 5,
        "max_cost": 1.0
    },
    {
        "task": "Search for 'AI news' and return top 3 titles",
        "verify": lambda result: len(result) >= 3,
        "max_steps": 10,
    },
]

results = []
for test in test_tasks:
    agent = Agent(...)
    result = await agent.run(test["task"], max_steps=test["max_steps"])
    success = test["verify"](result)
    results.append(success)

print(f"Success rate: {sum(results) / len(results)}")
```

### Metrics

- **Task completion rate**: % succeed
- **Steps efficiency**: actual vs minimum
- **Cost per task**: $$
- **Time per task**: latency
- **Error recovery**: did it self-correct?

---

## 12. Limitations (2026)

### Current Frontier

✅ Working well:
- Form filling (simple)
- Web search + summarize
- Click through workflows
- Data extraction from web

⚠️ Working sometimes:
- Complex reasoning over UI
- CAPTCHA + 2FA
- Mobile apps
- Highly visual tasks

❌ Doesn't work:
- Tasks requiring deep domain knowledge
- Real-time interactive (games)
- Voice-only interfaces
- Highly novel UIs

### Reliability Numbers

```
Frontier models on WebArena (2026):
  Claude Computer Use: ~50-65% task success
  GPT-4 Operator: ~45-60%
  Gemini: ~40-55%

Far from human (~95%)
But getting better fast
```

---

## 13. Future Trends

### 2025-2026 Direction

1. **Multi-modal native**: better vision understanding
2. **Persistent memory**: agents remember user prefs
3. **Multi-agent coordination**: agents work together
4. **Agent marketplaces**: pre-built skills
5. **Native OS integration**: smarter than screenshot loop

### Beyond 2026

- **Voice + vision agents**: phone-call automation
- **AR/VR agents**: control 3D environments
- **Robotics integration**: physical world

---

## 14. Cheat Sheet

### Q: "Computer Use vs Browser Use?"
> "Computer Use (Anthropic): controls whole desktop, native apps + terminal
> Browser Use (Operator, browser-use): web only, simpler
> ส่วนใหญ่ start with browser → expand to computer when needed"

### Q: "เริ่ม build agent ยังไง?"
> "1. Pick framework: browser-use (easy), Anthropic Computer Use SDK (powerful)
> 2. Define task clearly + success criteria
> 3. Set max_iterations (avoid infinite loop)
> 4. Authority levels (block dangerous actions)
> 5. Run in sandbox
> 6. Monitor + iterate"

### Q: "ทำไม agent ทำงานไม่ค่อย reliable?"
> "Compound failures: 5 step × 90% reliability = 59% success
> Solutions:
> - Verify state after each action
> - Checkpoint progress
> - Limit iterations
> - Human-in-loop for critical
> - Better prompting + planning"

### Q: "Cost ของ Computer Use?"
> "$0.10 - $20 per task (varies)
> Image input expensive (~1500 tokens per screenshot)
> Optimize: lower resolution, cache prompts, smart routing"

### Q: "Production ready ปี 2026 มั้ย?"
> "Selectively yes:
> - Form filling, data extraction = production-ready
> - Complex multi-step workflows = need supervision
> - Critical decisions = always human-approved
> Frontier capability — leaders adopting, mainstream slower"

---

## Sources

- [Introducing Computer Use - Anthropic](https://www.anthropic.com/news/3-5-models-and-computer-use)
- [Anthropic Computer Use vs OpenAI CUA - WorkOS](https://workos.com/blog/anthropics-computer-use-versus-openais-computer-using-agent)
- [Computer Use Agents 2026: Claude vs OpenAI vs Gemini](https://www.digitalapplied.com/blog/computer-use-agents-2026-claude-openai-gemini-matrix)
- [AI Agents That Use Computers](https://www.programming-helper.com/tech/ai-agents-that-use-computers-hands-on-ai-2026)
- [Browser Automation AI Agents: Playwright vs Stagehand](https://www.digitalapplied.com/blog/browser-automation-ai-agents-playwright-stagehand-2026)
- [The Agentic Browser Landscape in 2026](https://nohacks.co/blog/agentic-browser-landscape-2026)
- [browser-use GitHub](https://github.com/browser-use/browser-use)
