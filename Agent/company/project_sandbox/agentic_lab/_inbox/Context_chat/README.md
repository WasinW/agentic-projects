# agentic_lab

Sandbox สำหรับ PoC งานสาย agentic / RAG — แยกจากงานหลัก เพิ่ม project ใหม่ได้เรื่อยๆ

## Structure
```
agentic_lab/
├── kb/                 <- knowledge ที่กลั่นแล้ว = วัตถุดิบ RAG ตัวจริง
│   ├── rag-fundamentals.md
│   ├── agent-fundamentals.md
│   ├── model-file-formats.md
│   └── local-stack-decisions.md
├── transcripts/        <- บทสนทนาดิบ เก็บไว้อ้างอิง ไม่ควร index
│   └── 2026-07-29-rag-agent-crashcourse.md
└── projects/           <- PoC แต่ละตัว แยก venv แยก config
    └── local-rag-agent/
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
pip install -r requirements.txt
ollama pull qwen3:4b

python chunker.py     # ดูว่า kb/ ถูกตัดยังไง (ยังไม่โหลดโมเดล)
python indexer.py
python agent.py "hybrid search กับ RRF ต่างกันยังไง"
```
`config.KB_ROOT` ชี้มาที่ `kb/` ของ lab อยู่แล้ว — ทดลองได้เลยโดยไม่แตะ KB จริง
พอมั่นใจค่อยสลับไปชี้ KB ตัวจริง

## เพิ่ม project ใหม่
1. `projects/<ชื่อ>/` แยก venv แยก config
2. บทเรียนที่ได้ → เขียนเป็น note ใน `kb/` (heading ชัด ไม่ต้องยาว)
3. KB โตขึ้น → PoC ตัวต่อไปเริ่มจากจุดที่สูงกว่าเดิม

## Backlog
- [ ] reranker (cross-encoder) — stage 3 ที่ให้ผลเยอะสุด
- [ ] incremental re-index (ตอนนี้ rebuild ทั้งก้อน)
- [ ] golden set จริง 30-50 ข้อ แล้ววัด grep baseline vs dense vs hybrid
- [ ] tracing
- [ ] pythainlp เพื่อให้ BM25 ฝั่งไทยทำงาน
