"""
STEP 2-3: chunks -> embeddings -> เก็บลงไฟล์เปล่าๆ  (ไม่มี vector DB)

ที่ scale นี้ (< 10k chunks) ไฟล์ .npy + .jsonl ก็พอ:
  - vectors.npy  : เมทริกซ์ (n_chunks x dim) โหลดครั้งเดียว ค้นด้วย matmul ~5ms
  - chunks.jsonl : metadata + parent/child text  (1 บรรทัด = 1 chunk)
การลง Qdrant/Milvus ตั้งแต่แรกที่ scale นี้ = over-engineer (ดู kb/rag-fundamentals.md)

cost อยู่ที่ 'ตอน index' ไม่ใช่ตอน query -> embed ครั้งเดียวที่นี่ แล้ว reuse ตลอด
(ตอนนี้ rebuild ทั้งก้อนทุกครั้ง; incremental re-index อยู่ใน backlog)
"""
import json

import numpy as np

from config import KB_ROOT, INDEX_DIR, MAX_CHARS
from chunker import build_chunks
from embeddings import embed_passages


def main():
    chunks = build_chunks(KB_ROOT, MAX_CHARS)
    n_files = len({c["file"] for c in chunks})
    print(f"[indexer] {len(chunks)} chunks จาก {n_files} ไฟล์ ({KB_ROOT})")
    if not chunks:
        print("[indexer] ไม่พบ .md ใน KB_ROOT — เช็ค config.KB_ROOT ก่อน")
        return

    vectors = embed_passages([c["embed_text"] for c in chunks])
    print(f"[indexer] embedded -> {vectors.shape}")

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    np.save(INDEX_DIR / "vectors.npy", vectors)
    with open(INDEX_DIR / "chunks.jsonl", "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"[indexer] saved -> {INDEX_DIR}/  (vectors.npy + chunks.jsonl)")


if __name__ == "__main__":
    main()
