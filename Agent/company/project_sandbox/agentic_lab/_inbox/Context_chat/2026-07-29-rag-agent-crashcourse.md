---
date: 2026-07-29
topic: RAG และ agent — จาก concept ถึง implementation
form: raw transcript
note: |
  code block ขนาดใหญ่ถูกตัดออกและชี้ไปที่ projects/local-rag-agent/ แทน
  เพื่อไม่ให้ซ้ำซ้อน — ตัวเต็มอยู่ในไฟล์จริง
---

# Transcript: RAG & Agent Crash Course

## Turn 1 — ตั้งคำถาม

**Sin:** สอนการเขียน RAG และการทำ agent หน่อย รู้สึกว่าตกรถเรียนรู้หลายขบวนมาก
เข้าไปในกลุ่ม Facebook ของ Hermes agent Thailand คนใช้และสร้าง agent กันเยอะมาก
อยากรู้ทุก technical ในการ analyst, design, implement — มีไฟล์หลายแบบที่ไม่รู้ว่าทำงานยังไง
(แนบลิงก์: Unsloth fine-tuning guide, Ollama Agents-A1-4B-Fable-Preview, openquok, alibaba/open-code-review)

**Claude:** ให้ภาพรวม 4 ส่วน — RAG เป็น pipeline สองเส้น (indexing/query),
agent เป็น while loop, ตารางไฟล์ (safetensors/gguf/Modelfile/LoRA/jsonl),
และเส้นทางเรียน 4 ขั้น. แยก 3 แกนให้ชัด:
รู้ข้อมูลใหม่ → RAG / ทำงานได้ → agent+tools / เปลี่ยนพฤติกรรม → fine-tune

## Turn 2 — ตีกลับเรื่อง analogy

**Sin:** ตอนนี้ในเครื่องมีแค่ md ใช้แต่ agent เรียก skill หรือ knowledge ที่มีแต่ md
ไม่ได้ทำ RAG แบบนี้ อีกอย่าง ยำ RAG กับ data pipeline รวมกันระวังจะสับสนกว่าเดิม
เข้าใจว่าเป็นแนวๆ pipeline เหมือนกัน แต่การทำงานทำยังไง สอนตั้งแต่ข้อ 1

**Claude:** รับว่า analogy บอกแค่รูปทรงไม่บอกกลไก แล้วทิ้งมัน. อธิบายว่า
md-only setup คือ agentic/lexical retrieval อยู่แล้ว (LLM เป็น retriever, grep เป็น operator)
แล้วสอนกลไก: embedding → cosine → chunking → query time 5 บรรทัด
**จุดสำคัญ: LLM ไม่เคยเห็น vector store มันเห็นแค่ string ที่เราต่อให้**

## Turn 3 — ข้อจำกัด local

**Sin:** ถ้าจะใช้ on local 100% แบบประหยัด token และใช้ model ต่ำ
ควรใช้ process embed > search และต้อง design แบบมี vector database ด้วยหรือเปล่า
ตอนนี้ใช้ AI อย่างเดียวช่วยงานหมด มีอะไรก็ยัด md ให้ agent
ทำให้ไม่เห็นการทำงาน backend ของ agent เลยใช่มั้ย

**Claude:** ใช่ แต่เหตุผลกลับด้าน — **ยิ่งโมเดลเล็กยิ่งต้องทำ RAG**
เพราะ agentic retrieval ผลักภาระการค้นหาไปให้โมเดล ซึ่ง 4B ทำไม่ได้
token math ≈ 7 เท่า. แต่ **ไม่ต้องมี vector database** — brute force matmul พอถึง ~100k chunks
ส่วนคำถามที่สอง: abstraction ไม่เคยรั่วให้เห็น สิ่งที่ถูกซ่อนคือชั้นระหว่าง
"โมเดลพ่นข้อความ" กับ "tool ถูกเรียก" — แคบกว่าที่คิด แค่ 100 บรรทัดที่ยังไม่ได้เขียน

## Turn 4 — ขอ common practice

**Sin:** อยากรู้ก่อนว่าคนอื่นรู้อะไร ทำยังไง ทำไม design แบบนั้น
ไม่ต้องตาม ref ผม อยากเห็นเผื่อตามเค้าทัน รู้แบบไม่เหมือนใครก็ดี
แต่ควรเข้าใจ common practice ด้วยเวลาคุย จะได้เข้าใจตรงกัน เพื่อโตตาม career

**Claude:** map สนามให้ — convention เกิดจากข้อจำกัด 3 อย่าง
(context จำกัด / error ทบต้น / token = เงิน+เวลา+RAM)
ฝั่ง RAG: Naive→Advanced→Agentic, hybrid+RRF, two-stage rerank,
small-to-big, contextual retrieval, metadata filter, golden set
ฝั่ง agent: workflow vs agent (5 patterns), tool design, context engineering, MCP, failure modes
ปิดท้ายด้วย 4 ประโยคที่พูดได้แล้วคนถือว่าอยู่ในวง

## Turn 5 — ขอจับมือทำ

**Sin:** ยังไม่ค่อยเข้าใจ สอนแบบจับมือทำเลยได้มั้ย
architecture เป็นไง diagram เป็นไง code เป็นไง structure มีอะไรบ้าง

**Claude:** สร้าง project `local-rag-agent` 459 บรรทัด รันได้จริง
→ ตัวเต็มอยู่ที่ `projects/local-rag-agent/`
ชี้ 3 จุดที่ต้องอ่าน: `chunker.build_chunks` (contextual retrieval + parent-child),
`retriever.search` (8 บรรทัดที่แทน vector DB ทั้งก้อน), `agent.run` (loop ที่ print messages ทุกรอบ)

## Turn 6 — export

**Sin:** ขอ export history chat ทั้งหมด จะเอาไปทำต่อใน agent ในเครื่อง
ตอนนี้มีแค่ agent md llm แต่จะมีอีกอันที่ทำเป็น RAG
เผื่อทำเป็น project sandbox ชื่อ agentic_lab ไว้ทำ PoC ต่อยอดขนานกับหลายๆ งาน

**Claude:** สร้าง `agentic_lab/` พร้อม kb ที่กลั่นแล้ว + transcript นี้ + project เดิม
พร้อมเตือนว่า transcript ดิบเป็นวัตถุดิบ RAG ที่แย่ ต้องใช้ kb/ แทน
