# agentic_lab

Sandbox สำหรับ PoC งานสาย agentic / RAG — แยกจากงานหลัก เพิ่ม project ใหม่ได้เรื่อยๆ
จุดประสงค์: **เห็นกลไก backend ที่ปกติ framework ซ่อนไว้** (retrieval, agent loop, messages[])
ด้วยการเขียนเองทั้งเส้น แล้ววัดเทียบกับ agentic-retrieval (grep) baseline

## Structure
```
agentic_lab/
├── kb/                 <- knowledge ที่กลั่นแล้ว = วัตถุดิบ RAG ตัวจริง (index แค่โฟลเดอร์นี้)
│   ├── rag-fundamentals.md
│   ├── agent-fundamentals.md
│   ├── model-file-formats.md
│   └── local-stack-decisions.md
├── transcripts/        <- บทสนทนาดิบ + ref links เก็บอ้างอิง ไม่ index
│   ├── 2026-07-29-rag-agent-crashcourse.md
│   └── ref-links.md
└── projects/           <- PoC แต่ละตัว แยก venv แยก config
    └── local-rag-agent/
        ├── config.py       <- knob ทั้งหมดอยู่ที่เดียว
        ├── chunker.py      <- STEP 1: .md -> chunks (structure-aware + parent-child)
        ├── embeddings.py   <- STEP 3: text -> vector (e5 prefix trap อยู่ที่นี่)
        ├── indexer.py      <- STEP 2-3: chunks -> vectors.npy + chunks.jsonl
        ├── retriever.py    <- STEP 4: hybrid (dense + BM25) รวมด้วย RRF
        ├── tools.py        <- STEP 5: tool layer (search_kb) ที่ agent เรียก
        ├── agent.py        <- STEP 6: agent loop ที่ print(messages) ทุกรอบ
        └── requirements.txt
```

## kb/ กับ transcripts/ ต่างกันตรงไหน — สำคัญ
**transcript ดิบเป็นวัตถุดิบ RAG ที่แย่** เพราะ:
- มีบทสนทนาที่ไม่ใช่สาระปนเยอะ chunk จะเจือจาง
- ข้อมูลซ้ำหลายรอบ retrieval จะคืนก้อนซ้ำๆ กินที่ top-k
- มีข้อสรุปที่ถูกตีกลับแล้วปนอยู่ → โมเดลอาจดึงของที่ผิดมาตอบ

`kb/` คือฉบับที่กลั่นแล้ว จัด heading ให้ตัด chunk ได้สวย ตัดของซ้ำและของที่ถูกล้มแล้วออก
**index แค่ `kb/` เท่านั้น** ส่วน `transcripts/` เก็บไว้ให้คนอ่านย้อน

## เริ่มใช้
```bash
cd projects/local-rag-agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen3:4b          # หรือ nutboy02/Agents-A1-4B-Fable-Preview (tool-calling)

python chunker.py             # ดูว่า kb/ ถูกตัดยังไง (ยังไม่โหลดโมเดล = เร็ว)
python indexer.py             # โหลด e5-small (~470MB ครั้งแรก) -> สร้าง index/
python agent.py "hybrid search กับ RRF ต่างกันยังไง"
```
`config.KB_ROOT` ชี้มาที่ `kb/` ของ lab อยู่แล้ว — ทดลองได้เลยโดยไม่แตะ KB จริง
พอมั่นใจค่อยสลับไปชี้ KB ตัวจริง (`Path.home()/Documents/Projects/Agent`)

## ลำดับอ่าน code (เห็นภาพเร็วสุด)
1. `agent.py::run` แล้วดู `show_messages` — เห็นว่า **history ส่งซ้ำทุกรอบ** ตาตัวเอง
2. `retriever.py::search` — 8 บรรทัดที่แทน vector DB ทั้งก้อน (matmul + RRF)
3. `chunker.py::build_chunks` — contextual retrieval + parent-child อยู่ตรง `embed_text`
4. `embeddings.py` — จุดเดียวที่ 'เข้าใจภาษา' + กับดัก e5 prefix

## เพิ่ม project ใหม่
1. `projects/<ชื่อ>/` แยก venv แยก config
2. บทเรียนที่ได้ → เขียนเป็น note ใน `kb/` (heading ชัด ไม่ต้องยาว)
3. KB โตขึ้น → PoC ตัวต่อไปเริ่มจากจุดที่สูงกว่าเดิม

## Backlog
- [ ] reranker (cross-encoder) — stage 3 ที่ให้ผลเยอะสุด
- [ ] incremental re-index (ตอนนี้ rebuild ทั้งก้อน)
- [ ] golden set จริง 30-50 ข้อ แล้ววัด grep baseline vs dense vs hybrid
- [ ] tracing (LangSmith / Langfuse / print-based ก่อนก็ได้)
- [ ] approval gate สำหรับ tool ที่มี side effect (ตอนนี้ search_kb read-only)
```
