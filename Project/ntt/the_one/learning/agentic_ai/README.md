# Agentic AI — Learning Path

> ชุดเอกสารสอนทำ Agentic AI ตั้งแต่พื้นฐาน → ออกแบบระบบ → production
> เป้าหมาย: เข้าใจหลักการ + สร้างของจริงได้ + ใช้งบน้อย (free / self-host ได้)

---

## ทำไมต้องอ่านชุดนี้

ตอนคุณเริ่มสนใจ "AI agent" คุณจะเจอข้อมูลกระจัดกระจาย:

- บางคนบอก ใช้ LangChain
- บางคนบอก LangChain ห่วย ใช้ LangGraph
- บางคนเขียน CrewAI ในตัวอย่าง
- คนอื่นบอก ลาก n8n drag-drop เอา
- บางทีเห็น "MCP" "ReAct" "Plan-and-Execute" "Reflection" — งงไปหมด

**ปัญหาคือ**: ทุก tool/pattern มันถูกในบางบริบท แต่ไม่มีใครสอนให้คุณเลือก

ชุดนี้จะสอน **mental model** ก่อน แล้วค่อยลง tool ทีหลัง — คุณจะเลือกได้เองว่างานไหนใช้อะไร

---

## เหมาะกับใคร

- คนที่เคยเขียน code ได้ (Python / TypeScript / shell)
- เคยใช้ ChatGPT / Claude API บ้าง รู้ว่า "prompt" คืออะไร
- ยังไม่เคยทำ agent จริงจัง
- งบจำกัด — อยากได้ทางที่ฟรีหรือถูก

ถ้ายังไม่เคยลอง LLM API เลย แนะนำเปิด `learning/data_platform/AI/` อ่านก่อน 1-2 ไฟล์

---

## โครงสร้าง

### ⭐ Start Here

| ไฟล์ | สิ่งที่ได้ |
|---|---|
| **[00 Core Principles](00_Core_Principles.md)** | **แกนหลัก 15 ข้อ — compass สำหรับนำทางทั้งหมด** |

### Core Series (อ่านตามลำดับ)

| # | ไฟล์ | สิ่งที่ได้ |
|---|---|---|
| 01 | [Fundamentals](01_Agentic_AI_Fundamentals.md) | Agent คืออะไร, Workflow vs Agent, เมื่อไหร่ควรใช้ |
| 02 | [Design Patterns](02_Design_Patterns.md) | 10+ patterns และเลือก pattern ยังไง |
| 03 | [Frameworks Comparison](03_Frameworks_Comparison.md) | LangGraph / CrewAI / n8n / Dify — เลือกอะไร |
| 04 | [Tools & Selection](04_Tools_and_Selection.md) | ออกแบบ tool, MCP intro, web search, code exec |
| 05 | [Memory & Knowledge](05_Memory_and_Knowledge.md) | Vector DB (Qdrant/Chroma), self-host, embedding |
| 06 | [Production, Cost, Observability](06_Production_Cost_Observability.md) | Model routing, cache, monitor — ใช้ของฟรี |
| 07 | [Case Study: E-commerce Builder](07_Case_Study_Ecommerce_Builder.md) | ไอเดียของคุณ ออกแบบเป็นระบบจริง |
| 08 | [MCP Deep Dive](08_MCP_Deep_Dive.md) | Concept + protocol + เขียน MCP server เอง |
| 09 | [Agent Skills (SKILL.md)](09_Agent_Skills.md) | Anthropic's Skills standard — folder-based knowledge |
| **10** | **[Local Agent Blueprint](10_Local_Agent_Blueprint.md)** | **🎯 Prescriptive design — clone → docker compose up → chat ภายใน 30 นาที** |

### Deep Dive (อ่านเมื่ออยากลึก)

| ไฟล์ | เนื้อหา |
|---|---|
| [LangGraph Patterns](deep_dive/01_LangGraph_Patterns.md) | State machine, checkpoint, human-in-the-loop |
| [Self-Hosted Stack](deep_dive/02_Self_Hosted_Stack.md) | Ollama + Qdrant + n8n + Langfuse บน Docker Compose |
| [n8n Agent Workflows](deep_dive/03_n8n_Agent_Workflows.md) | สร้าง multi-agent flow แบบ low-code |
| [Cost Optimization](deep_dive/04_Cost_Optimization_Tactics.md) | Routing, caching, context compression — ลดบิล 70%+ |

---

## Roadmap แบบ 4 สัปดาห์ (ถ้ามีเวลาว่าง 1 ชม./วัน)

### Week 1 — เข้าใจของ
- Day 1-2: 01 Fundamentals → ทำตัวอย่าง ReAct เล็กๆ ด้วย OpenAI/Claude API
- Day 3-4: 02 Design Patterns → เปลี่ยน ReAct เป็น Plan-and-Execute
- Day 5-7: 03 Frameworks → ลอง LangGraph 1 flow + n8n 1 flow

### Week 2 — Tool & Memory
- Day 1-3: 04 Tools → สร้าง tool 3-4 อัน (web search, RAG, calculator, http)
- Day 4-7: 05 Memory → set up Qdrant local + RAG flow + episodic memory

### Week 3 — Multi-Agent
- Day 1-3: deep_dive/01 LangGraph Patterns → multi-agent graph
- Day 4-7: 07 Case Study → เริ่มประกอบ e-commerce builder จริง

### Week 4 — Production
- Day 1-3: 06 Production → ติด Langfuse + cache + cost dashboard
- Day 4-7: deep_dive/04 Cost Optimization → tune ให้ราคาเบา

---

## ก่อนเริ่ม — เครื่องมือที่ต้องเตรียม

**ขั้นต่ำสุด (ฟรีหมด)**:
- Docker Desktop
- Python 3.11+ (หรือ Node.js 20+)
- Git
- API key อย่างน้อย 1 อัน:
  - **Gemini** (free tier ใจดีสุด — 1500 req/day Gemini 2.5 Flash)
  - **Groq** (free tier เร็วมาก — Llama 3.3 70B / DeepSeek)
  - **Cerebras** (free tier — Llama models, เร็วระดับ inference 1000+ tok/s)
  - หรือ **Ollama** local (ฟรี ไม่ต้อง key — แต่กิน RAM)

**แนะนำเพิ่ม**:
- Claude API ($5 ครั้งแรก) — สำหรับงานที่ต้องการคุณภาพสูง
- OpenRouter — รวม model หลายเจ้าใน key เดียว

**ห้ามทำ**:
- เริ่มด้วยการจ่าย OpenAI API ตู้มเลย — เปลือง
- ลง LangChain แล้วงง — ไปอ่าน 03 ก่อน

---

## หลักการสอน (เพื่อให้คุณอ่านสนุก)

1. **ตัวอย่างก่อน → ทฤษฎีตาม** — ทุกหัวข้อจะมี code/diagram ก่อนอธิบาย
2. **ASCII diagram เยอะ** — เห็น flow ชัดกว่าอ่าน paragraph
3. **บอก trade-off ตรงไปตรงมา** — pattern ทุกอันมีจุดแข็ง/จุดอ่อน
4. **อ้างอิงของจริง** — ลิงก์ไป repo / paper / blog ที่ trusted
5. **ใช้ของฟรี/ถูกเป็นหลัก** — ทุกตัวอย่างรันได้ด้วย free tier หรือ self-host

---

## Quick Reference — ถ้ารีบ

| คำถาม | ไปที่ |
|---|---|
| "Agent ต่างจาก chatbot ยังไง?" | [01 §1](01_Agentic_AI_Fundamentals.md#1-agent-vs-chatbot-vs-workflow) |
| "ฉันควรใช้ LangGraph หรือ CrewAI?" | [03 §6](03_Frameworks_Comparison.md#6-decision-matrix) |
| "Vector DB ตัวไหนฟรี?" | [05 §3](05_Memory_and_Knowledge.md#3-vector-db-comparison) |
| "ลด cost ยังไง?" | [06 §4](06_Production_Cost_Observability.md) + [deep_dive/04](deep_dive/04_Cost_Optimization_Tactics.md) |
| "ทำเว็บขายของด้วย agent?" | [07 Case Study](07_Case_Study_Ecommerce_Builder.md) |
| "n8n ทำ agent ยังไง?" | [deep_dive/03](deep_dive/03_n8n_Agent_Workflows.md) |

---

## License & References

เนื้อหาเขียนเอง — อ้างอิง paper/blog ที่ระบุในแต่ละไฟล์
อนุญาตใช้ภายในส่วนตัว / ทีมงาน ไม่ต้องขอ
