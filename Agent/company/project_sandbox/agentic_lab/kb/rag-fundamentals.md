# RAG Fundamentals

## RAG คืออะไรจริงๆ
RAG ไม่ใช่ความสามารถพิเศษของโมเดล มันคือ **string concatenation ที่มี search นำหน้า**
LLM ไม่เคยเห็น vector store เลย มันเห็นแค่ string ที่เราต่อแล้วยัดเข้า prompt
เพราะฉะนั้น retrieval ที่ดี = คำตอบที่ดี. 90% ของ RAG ที่ห่วยคือ retrieval ห่วย ไม่ใช่ LLM ห่วย

## Embedding และ cosine similarity
Embedding model คือ function: text → array ของ float (เช่น 1024 มิติ)
โมเดลถูก train ให้ข้อความที่ความหมายใกล้กันชี้ไปทางเดียวกันในปริภูมิ
วัดด้วย cosine similarity = dot product ของเวกเตอร์ที่ normalize แล้ว ได้ -1 ถึง 1
นี่คือจุดเดียวในระบบทั้งหมดที่ "เข้าใจภาษา" ที่เหลือคือ engineering ธรรมดา

## Chunking
1 chunk = 1 เวกเตอร์ = ความหมาย 1 ก้อน
ถ้า embed เอกสารทั้งไฟล์เป็นเวกเตอร์เดียว ความหมายจะถูกเฉลี่ยจนไม่ตรงคำถามไหนเลย
(semantic dilution)

**Structure-aware > fixed-size** — สำหรับ markdown ให้ตัดตาม heading
เพราะคนเขียนขีดเส้นแบ่งความหมายไว้ให้แล้ว

**Parent-child (small-to-big)** — embed chunk เล็กเพื่อความแม่น
แต่ตอน return ส่ง parent ก้อนใหญ่ให้โมเดล เพราะ precision กับ context เป็นคนละความต้องการ

**Contextual retrieval** — เติม heading path หรือสรุประดับเอกสารไว้หัว chunk ก่อน embed
แก้ปัญหา chunk ที่อ่านเดี่ยวๆ แล้วไม่รู้ว่าพูดถึงอะไร

## Hybrid search และ RRF
Dense พลาด exact term (ชื่อ table, error code, config key)
BM25 พลาด paraphrase ("job ล่ม" vs "SDK harness OOM")
→ ใช้คู่กันเป็น default ของวงการไปแล้ว

รวมผลด้วย **RRF (Reciprocal Rank Fusion)** ไม่ใช่บวก score
เพราะ score ของสองระบบคนละสเกล เทียบกันไม่ได้ → รวมที่ **อันดับ** แทน
score = sum(1 / (k + rank)) โดย k = 60 เป็นค่ามาตรฐาน

## Two-stage retrieval และ reranker
ดึงกว้าง 50-100 → rerank → เอา 5

**Bi-encoder** (embedding ปกติ) embed query กับ doc แยกกัน เร็วเพราะ precompute ได้
แต่สองฝั่งไม่เคยเห็นกัน
**Cross-encoder** (reranker) อ่านคู่ query+doc พร้อมกัน แม่นกว่าเยอะแต่ precompute ไม่ได้
→ เลยใช้เป็น stage 2 เท่านั้น
Pattern นี้มาจากวงการ Information Retrieval ก่อนยุค LLM สิบปี

## Metadata filtering
ต้องกรองก่อน similarity เพราะ semantic similarity แสดง
"เฉพาะปี 2025" หรือ "เฉพาะ repo นี้" ไม่ได้

## Storage เลือกตาม scale
- < 10k chunks: ไฟล์เปล่าๆ `.npy` + `.jsonl` ค้นด้วย matmul ครั้งเดียว (~5ms)
- 10k-100k: SQLite + sqlite-vec หรือ LanceDB (embedded ไม่มี server)
- > 1M / multi-user: ค่อยคุยเรื่อง Qdrant / Milvus

HNSW (graph ที่ hop หาเพื่อนบ้านได้ ~log time, approximate ไม่ใช่ exact)
เริ่มคุ้มที่ ~100k chunks ขึ้นไป ต่ำกว่านั้น brute force ชนะเพราะไม่ต้องดูแลอะไรเลย
**การลง vector database ตั้งแต่แรกคือจุดที่คนโดนหลอกให้ over-engineer มากที่สุด**

## Evaluation
ไม่มี eval set = ปรับจูนแบบเดา

**Golden set** 30-100 คู่ (คำถาม, chunk/ไฟล์ที่ควรเจอ)
วัดสองชั้นเสมอ ห้ามรวมกัน ไม่งั้น debug ไม่ได้:
- Retrieval: recall@k, MRR, context precision, context recall
- Generation: faithfulness, answer relevancy

**LLM-as-judge** ใช้ได้แต่ระวัง position bias และแนวโน้มชอบคำตอบยาว

## วิวัฒนาการ 3 ขั้นที่คนใช้อ้างอิงกัน
- **Naive RAG**: chunk → embed → top-k → ยัด. ทุกคนเริ่มตรงนี้ ทุกคนพบว่ามันห่วย
- **Advanced RAG**: เติม pre-retrieval (query rewriting, HyDE, decomposition)
  + post-retrieval (rerank, compression)
- **Agentic RAG**: retrieval เป็น tool ที่ agent เรียกเองได้หลายรอบ ตรวจผลตัวเองได้

## Debate ที่ยังไม่จบ: long context vs RAG
Long context + agentic search กินพื้นที่ naive RAG ไปเยอะสำหรับ corpus เล็ก-กลาง
หลายคนยืนยันว่า "ให้ agent grep เอา" ชนะ vector RAG ที่ scale หลักพันไฟล์
เพราะ retrieval ที่โมเดลตัดสินใจเองมี precision สูงกว่าและไม่ต้องดูแล index

สรุป: การใช้ md + agentic retrieval ไม่ใช่ของล้าหลัง มันคือฝั่งหนึ่งของ debate
แค่ต้องอธิบายได้ว่าเลือกเพราะอะไรและมันพังตอนไหน
