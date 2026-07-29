"""
STEP 5: tool layer  <- สิ่งที่ agent เรียกได้ (ที่นี่มีตัวเดียว: search_kb)

โครงของ 'tool' หนึ่งตัว = 2 ส่วนที่ต้องคู่กันเสมอ:
  1. schema (JSON Schema)  -> serialize เข้า prompt ให้โมเดล 'รู้ว่ามี tool นี้'
                              โมเดลเห็นแค่ description นี้เท่านั้น = description คือ prompt
  2. ตัว execute จริง       -> รันเมื่อโมเดลสั่งเรียก แล้วคืน 'string' กลับเข้า messages[]

Tool design (kb/agent-fundamentals.md):
  - tool น้อยแต่ scope ชัด ชนะ tool เยอะละเอียดยิบ
  - คืน error เป็นข้อความที่โมเดลอ่านรู้เรื่อง เพื่อให้มันแก้เอง (ดู dispatch)
"""
from config import INDEX_DIR, TOP_K, CANDIDATES
from embeddings import embed_query
from retriever import Retriever, format_for_llm

# lazy: สร้าง retriever (โหลด vectors + BM25) ครั้งเดียวตอนถูกเรียกจริง
_retriever = None


def _get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever(INDEX_DIR, embed_query)
    return _retriever


def search_kb(query, mode="hybrid"):
    hits = _get_retriever().search(
        query, top_k=TOP_K, candidates=CANDIDATES, mode=mode)
    return format_for_llm(hits)


# --- schema ที่โมเดลเห็น (Ollama /api/chat รับรูปแบบ OpenAI tools) ---
TOOLS = [{
    "type": "function",
    "function": {
        "name": "search_kb",
        "description": (
            "ค้น knowledge base ของผู้ใช้ (RAG). "
            "เรียกเมื่อคำถามเกี่ยวกับ note / project / ความรู้ที่ผู้ใช้เก็บไว้. "
            "คืน chunk ที่เกี่ยวข้องพร้อมไฟล์ต้นทางให้ใช้ตอบ."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "คำค้นภาษาธรรมชาติ อธิบายสิ่งที่อยากรู้",
                },
                "mode": {
                    "type": "string",
                    "enum": ["hybrid", "dense", "bm25"],
                    "description": "วิธีค้น (default hybrid = dense + BM25 รวมด้วย RRF)",
                },
            },
            "required": ["query"],
        },
    },
}]

_DISPATCH = {"search_kb": search_kb}


def dispatch(name, args):
    """execute tool ตามชื่อ; คืน string เสมอ (แม้ error) เพื่อป้อนกลับเข้า messages[]"""
    fn = _DISPATCH.get(name)
    if fn is None:
        return f"(ไม่รู้จัก tool ชื่อ '{name}')"
    try:
        return fn(**args)
    except Exception as e:
        # คืน error เป็นข้อความ ให้โมเดลลองแก้ query เอง ดีกว่า throw ทิ้ง loop
        return f"(tool '{name}' error: {e})"
