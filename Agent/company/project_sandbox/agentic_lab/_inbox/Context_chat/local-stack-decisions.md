# Local Stack — ข้อจำกัดและการตัดสินใจ

## ข้อจำกัดที่ตั้งไว้
100% local, ประหยัด token, ใช้โมเดลเล็ก, ไม่มี server
KB ปัจจุบันเป็น markdown ล้วน agent อ่านไฟล์ตรง

## ยิ่งโมเดลเล็ก ยิ่งต้องทำ RAG (กลับด้านกับที่คนคิด)
Agentic retrieval **ผลักภาระการค้นหาไปให้โมเดล** — ต้องอ่าน description ทั้งหมด
ตัดสินใจว่าเปิดไฟล์ไหน อาจ grep หลายรอบ แล้วค่อยตอบ
นั่นคือความสามารถของโมเดลใหญ่ 4B ทำไม่ได้
multi-step tool routing คือสิ่งแรกที่พังเมื่อย่อโมเดล

RAG ย้าย retrieval ออกมาอยู่นอกโมเดล เหลืองานเดียวคือ "อ่าน context นี้แล้วตอบ"
ซึ่ง 4B ทำได้ดี

## Token math
```
Agentic:  descriptions 2k + grep 1k + file read 3k
          x 3 รอบ (history ส่งซ้ำทุกรอบ)      ~= 15-20k tokens
RAG:      5 chunks 2k + prompt 300            ~= 2.5k tokens รอบเดียว
```
~7 เท่า และบน local นี่คือ RAM กับเวลาจริง

## เลือกโมเดล
- **Embedding: bge-m3** — ต้องเป็น multilingual เพราะ KB มีภาษาไทย
  ห้ามใช้ embedder ภาษาอังกฤษล้วน. bge-m3 ให้ dense + sparse ในตัวเดียว ทำ hybrid ได้ฟรี
  ถ้าอยากเบากว่า: `intfloat/multilingual-e5-small`
- **Generation: Ollama** โมเดล 4B ที่ fine-tune มาทาง tool-calling
- Embed ครั้งเดียวตอน index ไม่ใช่ทุก query — cost อยู่ที่ ingest ไม่ใช่ runtime

## กับดักภาษาไทย
BM25 ต้องการ tokenizer เพราะไทยไม่มีเว้นวรรค
ไม่มี `pythainlp` → ไทยจะถูกรวบเป็นก้อนเดียว → BM25 ฝั่งไทยแทบไม่ทำงาน

## md-only setup ปัจจุบันคืออะไร
คือ agentic / lexical retrieval:
1. โหลด description ของ skill ทั้งหมดเข้า context
2. LLM อ่านแล้วตัดสินใจเองว่าเปิดไฟล์ไหน — **ตัว retriever คือ LLM เอง**
3. ใช้ grep / glob / read เป็น retrieval operator

ข้อดี: precision สูงมาก ไม่ต้องมี infra
พังเมื่อ: ไฟล์เยอะจน description ยัดไม่หมด / ต้องหาด้วยความหมาย /
ต้องการ latency ต่ำ / โมเดลเล็กเกินจะ route เอง

## ข้อสรุปเชิงปฏิบัติ
ที่ scale หลักร้อยไฟล์ agentic retrieval ยังให้ผลดีกว่า
สร้าง RAG เพื่อ **เรียนกลไก** และเพื่อรองรับโมเดลเล็ก แล้ววัดเทียบกับ grep baseline
ด้วย golden set จะได้เห็นด้วยตัวเลขว่าอันไหนชนะตรงไหน
