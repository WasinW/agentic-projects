"""ค่า config ทั้งหมดอยู่ที่เดียว - แก้ตรงนี้ที่เดียวพอ"""
from pathlib import Path

# --- KB ที่จะ index — สลับ KB_ROOT ระหว่าง 2 อันนี้ ---
#   LAB_KB  = kb/ ของ lab เอง (4 ไฟล์ ชุดเล็ก ทดลองไว รู้ ground truth)
#   REAL_KB = ต้นไม้ Agent/ จริง (READ-ONLY; chunker filter กัน agent.md/_prefix/agentic_lab)
LAB_KB    = Path(__file__).resolve().parents[2] / "kb"
REAL_KB   = Path.home() / "Documents" / "Projects" / "Agent"
KB_ROOT   = REAL_KB            # option (ก): index ต้นไม้จริง (อ่านอย่างเดียว)
INDEX_DIR = Path(__file__).parent / "index"

# --- Models (local ล้วน) ---
# e5-small = multilingual, เบา (~470MB) รันไว เหมาะกับเครื่อง local/โมเดลเล็ก
# กับดัก: ตระกูล e5 ต้องเติม prefix "query:" / "passage:" เสมอ -> จัดการใน embeddings.py
# ถ้าอยากคุณภาพ retrieval สูงขึ้น + hybrid ในตัว ค่อยสลับเป็น "BAAI/bge-m3"
EMBED_MODEL = "intfloat/multilingual-e5-small"
CHAT_MODEL  = "qwen3:4b"          # หรือตัวที่คุณ pull ไว้ใน ollama
OLLAMA_URL  = "http://localhost:11434"

# --- Retrieval knobs (ตัวที่ต้องจูนจริง) ---
MAX_CHARS   = 600   # ขนาด child chunk
CANDIDATES  = 50    # ดึงกว้างก่อน (stage 1)
TOP_K       = 5     # ส่งเข้าโมเดลจริงกี่ก้อน (stage 2)
RRF_K       = 60    # ค่ามาตรฐานของ Reciprocal Rank Fusion

# --- Agent guardrails ---
MAX_STEPS   = 6     # กัน infinite loop
NUM_CTX     = 8192
