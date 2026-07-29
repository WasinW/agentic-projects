# Agent Fundamentals

## Agent คือ while loop ที่มี LLM เป็นตัวเลือก branch
```python
while not done:
    resp = llm(messages, tools=tool_schemas)
    if resp.tool_calls:
        messages += [execute(tc) for tc in resp.tool_calls]
    else:
        done = True
```
ทุกอย่างที่เหลือคือ engineering รอบ loop นี้

## messages[] คือของที่ framework ซ่อนไว้
ชั้นที่ทุก product ปิดไว้คือระหว่าง "โมเดลพ่นข้อความ" กับ "tool ถูกเรียก":
1. tool schema ถูก serialize เข้า prompt ยังไง
2. output ถูก parse กลับเป็น tool call ยังไง
3. `messages[]` หน้าตายังไงในแต่ละรอบ
4. context ถูกตัด/ประกอบยังไงเมื่อเต็ม

**history ทั้งก้อนถูกส่งซ้ำทุกรอบ** — นี่คือคำตอบว่าทำไม token บานตอนใช้ agent
วิธีเห็นด้วยตา: เขียน loop เองแล้ว print(messages) ทุกรอบ ครั้งเดียวเข้าใจหมด

## Tool design คืองานจริงของ agent engineer
คุณภาพ agent ≈ คุณภาพ tool ไม่ใช่ prompt
- tool น้อยแต่ scope ชัด ชนะ tool เยอะละเอียดยิบ
- คืน error เป็นข้อความที่โมเดลอ่านรู้เรื่อง เพื่อให้มันแก้เอง
- description คือ prompt เขียนให้เหมือนสอนพนักงานใหม่
- schema ใช้ JSON Schema

## Workflow vs Agent
| Pattern | คือ |
|---|---|
| Prompt chaining | ต่อกันเป็นทอด ผลอันหนึ่งเข้าอีกอัน |
| Routing | จำแนกก่อน แล้วส่งเข้าสายที่เหมาะ |
| Parallelization | ยิงพร้อมกันแล้วรวมผล / โหวต |
| Orchestrator-workers | ตัวหลักแตกงาน ตัวย่อยทำ |
| Evaluator-optimizer | ตัวหนึ่งทำ ตัวหนึ่งวิจารณ์ วนจนผ่าน |

5 อันนี้คือ **workflow** — path ถูกกำหนดโดยเรา
**Agent** จริงๆ คือตัวที่เลือก path เองแบบ dynamic

**Consensus: production ส่วนใหญ่ควรเป็น workflow ไม่ใช่ agent**
เพราะ debug ได้ ทำนายค่าใช้จ่ายได้ และ error ไม่ทบต้น

## Context engineering
ศัพท์ที่มาแทน prompt engineering — งานคือบริหารพื้นที่ context ไม่ใช่แต่งประโยค
- **compaction** — สรุปทับ history เมื่อยาว
- **sub-agent isolation** — แตก context ออกไปไม่ให้เปื้อนตัวหลัก
- **external memory** — เขียนลงไฟล์แล้วอ่านกลับ แทนแบกไว้ใน context
- **just-in-time retrieval** — ดึงเมื่อต้องใช้ ไม่ preload

## MCP
Protocol มาตรฐานให้ tool/context เสียบข้าม client ได้
แก้ปัญหา N×M (tool N ตัว × client M ตัว = เขียน integration N×M รอบ)

## Failure modes ที่ต้องเรียกชื่อถูก
- **context rot / lost in the middle** — ยัดเยอะจนโมเดลเบลอ attention เสื่อมก่อน context เต็ม
- **error compounding** — step ละ 95% ทำ 20 step เหลือ 36%
- **prompt injection ผ่าน tool result** — ข้อมูลที่ดึงมามีคำสั่งแฝง
- **infinite loop** — แก้ด้วย max steps
- **cost blowup** — แก้ด้วย budget cap

## วัฒนธรรมที่แข็งขึ้นเรื่อยๆ
- ไม่มี tracing ถือว่ายังไม่ได้ทำ (LangSmith / Langfuse / Braintrust)
- approval gate สำหรับ tool ที่มี side effect
- ไม่มี eval set = ยังตอบไม่ได้ว่าดีขึ้นจริงไหม

## ข้อจำกัด 3 อย่างที่ derive practice ที่เหลือได้เกือบหมด
1. Context จำกัด และ attention เสื่อมก่อนเต็ม — ยัดเยอะไม่ได้แปลว่าดี
2. LLM เป็น stochastic → error ทบต้น
3. Token = เงิน + เวลา + RAM
