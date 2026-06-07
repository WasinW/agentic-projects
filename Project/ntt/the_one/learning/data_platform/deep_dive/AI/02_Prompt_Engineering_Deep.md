# Prompt Engineering — Deep Dive

> CoT, ToT, ReAct, DSPy, structured outputs
> Prompt = code in 2026 — engineer it like code

---

## 1. ทำไม Prompt Engineering ยังสำคัญในปี 2026

### Common Misconception

"Frontier models are smart, just ask normally"

### Reality

- Better prompts = 20-40% accuracy improvement
- Same model, same data, different prompt = different outcomes
- Prompts are the **API** to LLM — design them carefully

### Hierarchy of Prompt Engineering

```
1. Basic prompting       (zero-shot)
2. Few-shot examples     (in-context learning)
3. Chain-of-Thought      (reasoning)
4. Self-consistency      (multiple runs + vote)
5. Tree-of-Thoughts      (branching exploration)
6. ReAct                 (reasoning + tools)
7. Reflection            (self-critique loop)
8. DSPy / programmatic   (auto-optimize)
```

---

## 2. Foundational Patterns

### Zero-Shot

```
Just ask:
"Translate 'Hello' to Thai."
→ "สวัสดี"
```

### Few-Shot (In-Context Learning)

```
Show examples in prompt:

"Translate English to Thai.

English: Hello
Thai: สวัสดี

English: Thank you
Thai: ขอบคุณ

English: Good morning
Thai: ?"
```

Powerful for:
- Novel formats
- Specific style
- Rare languages

### Instruction Following

```
"You are an expert data analyst.
Analyze this SQL query and identify potential issues.
Provide your response as a numbered list.

SQL: SELECT * FROM users WHERE age > 18;"
```

### Constraint Specification

```
"Summarize the following text in EXACTLY 3 bullet points.
Each bullet must start with • and contain max 15 words.
DO NOT include any preamble or explanation.

Text: ..."
```

---

## 3. Chain-of-Thought (CoT)

### Why CoT

LLMs are better at multi-step reasoning when they "think out loud"

### Without CoT
```
Q: A bag has 3 apples and 2 oranges. After eating 1 apple
   and buying 4 more oranges, how many fruits total?

A: 8  (sometimes wrong)
```

### With CoT
```
Q: ... [same question]

Think step by step:
A: Initial: 3 apples + 2 oranges = 5 fruits
   After eating 1 apple: 2 apples + 2 oranges = 4 fruits
   After buying 4 oranges: 2 apples + 6 oranges = 8 fruits
   
Answer: 8
```

### Trigger Phrases

```
"Let's think step by step"
"Walk through this carefully"
"Show your reasoning"
"Break this down"
```

### Few-Shot CoT

```
Q: Sara has 5 dolls. She gives 2 to her sister. How many left?
A: Sara starts with 5 dolls. She gives 2 away. 5 - 2 = 3.
   Answer: 3

Q: John has $20. He buys a $7 book. How much left?
A: ?
```

### Auto-CoT

Don't hand-craft CoT examples — let model generate them:
```
"Let's think step by step:" + model continues
```

---

## 4. Self-Consistency

### Idea

Run CoT multiple times with high temperature → take majority vote

```python
def self_consistency(prompt, n=10, temperature=0.7):
    responses = [
        llm(prompt, temperature=temperature)
        for _ in range(n)
    ]
    answers = [extract_answer(r) for r in responses]
    return Counter(answers).most_common(1)[0][0]
```

### When to Use

- Math/reasoning problems
- Decision tasks with discrete answers
- When accuracy matters more than cost (5-10x cost)

---

## 5. Tree of Thoughts (ToT)

### Idea

Instead of linear CoT, **branch** at decision points

```
                Problem
                  |
        [Generate 3 approaches]
        /        |        \
      A         B          C
      |         |          |
   Evaluate  Evaluate   Evaluate
      |         |          |
   [Best: B]
   Continue B...
```

### Pseudocode

```python
def tree_of_thoughts(problem, depth=3, breadth=3):
    def expand(state):
        # Generate breadth options
        options = llm(f"Given {state}, propose {breadth} next steps")
        return parse(options)
    
    def evaluate(state):
        score = llm(f"Rate this state 1-10: {state}")
        return parse_score(score)
    
    def search(state, d):
        if d == 0:
            return state
        options = expand(state)
        scored = [(o, evaluate(o)) for o in options]
        best = max(scored, key=lambda x: x[1])[0]
        return search(best, d-1)
    
    return search(problem, depth)
```

### When to Use

- Complex planning (game, math, logic)
- When CoT not enough
- Have compute budget

### Cost: 5-20x more LLM calls

---

## 6. ReAct (Reasoning + Acting)

### Pattern

```
Thought: I need to find X
Action: search("X query")
Observation: [results]
Thought: Now I need Y
Action: lookup("Y")
Observation: [result]
Thought: I have enough info
Final Answer: ...
```

### Implementation

```python
def react_agent(question, tools, max_iterations=10):
    history = ""
    for _ in range(max_iterations):
        prompt = f"""You have these tools: {list(tools.keys())}

Question: {question}

{history}

Output Thought, Action (or Final Answer):"""
        
        response = llm(prompt)
        
        if "Final Answer:" in response:
            return response.split("Final Answer:")[1].strip()
        
        thought = parse_thought(response)
        action_name, args = parse_action(response)
        
        observation = tools[action_name](**args)
        
        history += f"\nThought: {thought}\nAction: {action_name}({args})\nObservation: {observation}"
    
    return "Max iterations reached"
```

### Used in
- LangChain agents
- Most agent frameworks
- Hugging Face Transformers Agents

(More in Agentic AI doc)

---

## 7. Reflection / Self-Critique

### Pattern

```
1. Generate initial answer
2. Critique own answer
3. Refine based on critique
4. Optionally repeat
```

### Implementation

```python
def reflection_pattern(question, max_rounds=3):
    answer = llm(f"Q: {question}\nA:")
    
    for _ in range(max_rounds):
        critique = llm(f"""Review this answer for accuracy and completeness:

Question: {question}
Answer: {answer}

Critique:""")
        
        if "no issues" in critique.lower():
            break
        
        answer = llm(f"""Original Q: {question}
Original A: {answer}
Critique: {critique}

Improved Answer:""")
    
    return answer
```

### Variations

- **Reflexion**: agent reflects on past tasks, learns
- **Self-Refine**: iterative improvement
- **Self-Verify**: check own work

### When to Use

- Important answers (accuracy critical)
- Code generation
- Long-form writing
- Research tasks

### Cost: 2-3x calls

---

## 8. Structured Outputs

### Why Structured

- Easier to parse
- Type safety
- Composable in pipelines

### Method 1: JSON Mode (provider feature)

```python
# OpenAI
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "..."}],
    response_format={"type": "json_object"}
)

# Anthropic Claude (via prefilling)
response = client.messages.create(
    model="claude-sonnet-4-6",
    messages=[
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "{"}  # prefill
    ]
)
```

### Method 2: Function Calling / Tool Use

```python
# Define tool with schema
tools = [{
    "type": "function",
    "function": {
        "name": "extract_invoice",
        "parameters": {
            "type": "object",
            "properties": {
                "invoice_number": {"type": "string"},
                "total": {"type": "number"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "price": {"type": "number"}
                        }
                    }
                }
            },
            "required": ["invoice_number", "total", "items"]
        }
    }
}]

# Force LLM to call this
response = llm(prompt, tools=tools, tool_choice={"name": "extract_invoice"})
data = json.loads(response.tool_calls[0].arguments)
```

### Method 3: Constrained Generation

```python
# Outlines library — guarantees valid JSON
from outlines import models, generate

model = models.transformers("microsoft/phi-3-mini")
generator = generate.json(model, schema=PydanticModel)
result = generator(prompt)
```

### Method 4: Pydantic + Instructor

```python
from pydantic import BaseModel
import instructor
from openai import OpenAI

client = instructor.patch(OpenAI())

class Invoice(BaseModel):
    invoice_number: str
    total: float
    items: list[Item]

invoice = client.chat.completions.create(
    model="gpt-4o",
    response_model=Invoice,  # auto-validates
    messages=[{"role": "user", "content": "Extract from: ..."}]
)
```

---

## 9. Prompt Templates & Versioning

### Template Pattern

```python
TEMPLATE = """You are a {role}.

Task: {task}

Context:
{context}

Constraints:
{constraints}

Output Format:
{output_format}

Input:
{input_text}"""

prompt = TEMPLATE.format(
    role="customer support agent",
    task="Answer the user's question",
    context="\n".join([doc.text for doc in retrieved_docs]),
    constraints="- Use only context\n- Be concise\n- Cite sources",
    output_format="JSON with answer + sources",
    input_text=user_query
)
```

### Versioning (Git-Tracked)

```yaml
# prompts/customer_support_v2.4.1.yaml
name: customer_support
version: 2.4.1
purpose: Answer customer questions from knowledge base

system: |
  You are a helpful support agent.
  Use ONLY the provided context.
  Cite sources using [doc_id].

user_template: |
  Context: {context}
  Question: {question}
  Answer:

parameters:
  temperature: 0.3
  max_tokens: 500
  model: claude-sonnet-4-6

evaluation:
  test_set: prompts/eval/customer_support_v2.4_tests.yaml
  metrics:
    faithfulness: ">= 0.9"
    answer_relevance: ">= 0.85"

changelog:
  v2.4.1: Fixed instruction about citation format
  v2.4.0: Added explicit "use only context" instruction
  v2.3.0: ...
```

### A/B Test Versions

```python
def get_prompt(user_id, name):
    variant = hash(user_id + name) % 100
    if variant < 50:
        return PromptRegistry.get(name, version="2.3.0")  # control
    else:
        return PromptRegistry.get(name, version="2.4.1")  # treatment

# Track outcomes per variant
log_outcome(user_id, version, user_satisfaction)
```

---

## 10. DSPy — Programmatic Prompts

### What DSPy Does

Instead of writing strings, write **declarative programs**

DSPy compiles your program → optimal prompts (auto-tuned)

### Signature (declare what you want)

```python
import dspy

class GenerateAnswer(dspy.Signature):
    """Answer questions based on context."""
    context = dspy.InputField(desc="relevant facts")
    question = dspy.InputField(desc="user question")
    answer = dspy.OutputField(desc="answer with citations")
```

### Module (declare strategy)

```python
class RAG(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=5)
        self.generate = dspy.ChainOfThought(GenerateAnswer)
    
    def forward(self, question):
        context = self.retrieve(question).passages
        prediction = self.generate(context=context, question=question)
        return prediction
```

### Compilation (auto-optimize)

```python
from dspy.teleprompt import BootstrapFewShot

# Define metric
def metric(example, pred, trace=None):
    return example.answer in pred.answer  # or LLM judge

# Auto-tune
teleprompter = BootstrapFewShot(metric=metric, max_bootstrapped_demos=4)
optimized_rag = teleprompter.compile(RAG(), trainset=examples)

# Now optimized_rag has auto-generated few-shot examples
# 10-40% quality improvement
```

### Compilers Available

- BootstrapFewShot: simple few-shot generation
- BootstrapFewShotWithRandomSearch: random search variants
- MIPROv2: Bayesian optimization (best, slowest)
- COPRO: optimize instructions

### When to Use DSPy

- Multi-stage LLM pipelines
- Need optimization beyond manual prompting
- Want maintainable code (vs prompt strings)

### Cons

- Learning curve
- Compile takes time
- Less control than manual prompting

---

## 11. Advanced Techniques

### Self-Ask
```
Decompose complex question into sub-questions:

Q: Who is the spouse of the person who wrote 1984?

Sub-Q1: Who wrote 1984?
A1: George Orwell
Sub-Q2: Who is George Orwell's spouse?
A2: Eileen O'Shaughnessy
Final: Eileen O'Shaughnessy
```

### Plan-and-Solve
```
First plan all steps, then execute:

Plan:
1. Identify the equation type
2. Apply formula
3. Solve

Execute:
Step 1: ...
```

### Maieutic Prompting (Socratic)
```
Verify each claim with sub-questions
Find contradictions, refine
Used for fact-checking
```

### Constitutional AI (CAI)
```
LLM critiques itself per principles:
1. Generate response
2. Check against principles
3. Revise if violates

Used in: Claude, helping with safety
```

### Iterative Refinement (Self-Refine)
```
Generate → Critique → Refine → Critique → Refine...
Stop when no improvement
```

---

## 12. Optimization Tips

### Be Specific

❌ "Write something about dogs"
✅ "Write a 3-paragraph blog post about training puppies for first-time dog owners. Tone: friendly, informative."

### Use Delimiters

```
Use clear delimiters for input vs instructions:

"""
Input:
{user_input}
"""

Now respond to the above.
```

### Chain of Density (for summarization)

```
Generate 5 increasingly dense summaries:
1. Long, low density
2. Slightly shorter, higher density
3. ...
5. Short, high density

Output the densest one
```

### Show Format

❌ "Output as a list"
✅ "Output as a list:
   - Item 1
   - Item 2"

### Negative Examples

```
"Translate to formal Thai.

DO NOT use:
- Casual particles like 'นะ', 'อ่ะ'
- English loanwords if Thai exists
- Slang"
```

### Step-Back Prompting

```
Before answering specific question, ask broader principle:

Q: How does X work in this specific case?
Step-back Q: What are the general principles of X?
Then: Apply principles to specific case.
```

---

## 13. Provider-Specific Best Practices

### Anthropic Claude

```
- XML tags work great:
  <example>...</example>
  <instructions>...</instructions>

- "Think step by step inside <thinking> tags"
- Long context handles needle-in-haystack well
- System prompt is influential
```

### OpenAI GPT

```
- JSON mode reliable
- Function calling structured
- Use system role for persistent instruction
```

### Google Gemini

```
- Long context (2M tokens)
- Multimodal native
- Use system_instruction parameter
```

### General

- Lower temperature for factual (0.0-0.3)
- Higher temperature for creative (0.7-1.0)
- Use top_p instead of top_k
- max_tokens cap to control cost

---

## 14. Anti-Patterns

### ❌ Vague Instructions
```
"Write a good email"
→ what's "good"?
```

### ❌ No Examples
```
"Format as JSON"
→ which fields? what shape?
Better: provide example
```

### ❌ Buried Instructions
```
[long context]
[more context]
[finally instruction]

Better: instruction first, then context
```

### ❌ Overload
```
"Do X, Y, Z, A, B, C in one prompt"
→ model loses focus

Better: chain (X first, then Y based on result)
```

### ❌ Mix System and User
```
System: "You are X"
User: "Actually you're Y"

Confuses model. Use system properly.
```

### ❌ No Output Format
```
LLM responds with prose when you wanted structured
→ harder to parse, downstream breaks

Always: explicit format spec
```

---

## 15. Cheat Sheet

### Q: "เริ่ม prompt engineering จากไหน?"
> "1. Be specific (role + task + format)
> 2. Show examples (few-shot)
> 3. Add CoT for reasoning
> 4. Structure output (JSON/schema)
> 5. Iterate based on outputs
> 6. Version + test
> ขั้นตอนเดียวกับ writing code"

### Q: "CoT ใช้เมื่อไหร่?"
> "Multi-step reasoning, math, logic, analysis
> Add 'think step by step' หรือ explicit framework
> Cost: longer output, but accuracy +20-40%"

### Q: "Structured output ทำยังไง?"
> "1. Function calling (best — provider enforces)
> 2. JSON mode (provider features)
> 3. Pydantic + Instructor library
> 4. Constrained generation (Outlines)
> ห้าม: parse free-form text — fragile"

### Q: "DSPy ดีกว่า manual prompting มั้ย?"
> "Pipeline หลาย stage: ใช่ — DSPy ช่วยมาก
> Single prompt: manual ก็ได้
> DSPy ตามผล research = 10-40% improvement
> Trade-off: learning curve + compile time"

### Q: "Tree of Thoughts ดีกว่า CoT มั้ย?"
> "ใช่สำหรับ complex problems
> ToT ใช้ compute 5-20x มากกว่า
> Use ToT only when CoT ไม่พอ — math olympiad, complex planning"

---

## Sources

- [DSPy Framework](https://dspy.ai/)
- [Systematic LLM Prompt Engineering Using DSPy Optimization](https://towardsdatascience.com/systematic-llm-prompt-engineering-using-dspy-optimization/)
- [Advanced Prompt Engineering 2026](https://lushbinary.com/blog/advanced-prompt-engineering-techniques-developer-guide/)
- [Prompting with DSPy](https://www.digitalocean.com/community/tutorials/prompting-with-dspy)
- [DSPy GitHub](https://github.com/stanfordnlp/dspy)
- [What is DSPy? - IBM](https://www.ibm.com/think/topics/dspy)
- [Prompt Engineering 2026 Frameworks](https://pasqualepillitteri.it/en/news/1090/prompt-engineering-2026-frameworks-complete-guide)
- [Anthropic Prompting Guide](https://docs.anthropic.com/claude/docs/intro-to-prompting)
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
