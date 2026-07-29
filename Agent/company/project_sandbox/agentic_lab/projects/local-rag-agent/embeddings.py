"""
STEP 3: text -> vector  (จุดเดียวในระบบที่ 'เข้าใจภาษา' จริง)

กับดักเฉพาะ e5 ที่คนลืมกันบ่อยที่สุด:
  ตระกูล intfloat/e5 ถูก train มาให้ 'ถามด้วย prefix ต่างกัน'
    - เอกสารตอน index -> เติม "passage: " นำหน้า
    - query ตอนค้น    -> เติม "query: "   นำหน้า
  ลืมเติม = retrieval คุณภาพตกฮวบ (นี่คือ 'RAG ห่วยเพราะ retrieval ห่วย' คลาสสิก)
  (bge-m3 ไม่ต้องเติม prefix -> ถ้าสลับ EMBED_MODEL เป็น bge-m3 ให้ตั้ง PREFIX = "")

normalize_embeddings=True -> ได้ unit vector
  => dot product = cosine similarity  (retriever ถึงคูณ matmul ตรงๆ ได้เลย)
"""
from functools import lru_cache

import numpy as np

from config import EMBED_MODEL

# e5 ต้องมี prefix; ตระกูลอื่น (bge-m3 ฯลฯ) ตั้งเป็น "" ได้
_NEEDS_PREFIX = "e5" in EMBED_MODEL.lower()
_Q_PREFIX = "query: "   if _NEEDS_PREFIX else ""
_P_PREFIX = "passage: " if _NEEDS_PREFIX else ""


@lru_cache(maxsize=1)
def _model():
    # import ในนี้เพื่อไม่ให้ chunker.py (ที่ไม่ต้องโหลดโมเดล) ช้าไปด้วย
    from sentence_transformers import SentenceTransformer
    print(f"[embeddings] loading {EMBED_MODEL} (ครั้งแรกดาวน์โหลด ~470MB)...")
    return SentenceTransformer(EMBED_MODEL)


def _encode(texts, prefix):
    vecs = _model().encode(
        [f"{prefix}{t}" for t in texts],
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return vecs.astype("float32")


def embed_passages(texts):
    """ใช้ตอน index เอกสาร (indexer.py)"""
    return _encode(texts, _P_PREFIX)


def embed_query(texts):
    """ใช้ตอนค้น (retriever.py / tools.py) — คืน shape (n, dim) ให้ [0] ได้"""
    return _encode(texts, _Q_PREFIX)
