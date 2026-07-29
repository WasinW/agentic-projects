"""ค่า config ทั้งหมดอยู่ที่เดียว - แก้ตรงนี้ที่เดียวพอ"""
from pathlib import Path

# --- KB ของคุณ ---
# ชี้มาที่ kb/ ของ lab เอง -> index ได้ทันทีโดยไม่ต้องแตะ KB จริง
KB_ROOT   = Path(__file__).resolve().parents[2] / "kb"
# ของจริงค่อยสลับเป็น: Path.home() / "Documents" / "Projects" / "Agent"
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
