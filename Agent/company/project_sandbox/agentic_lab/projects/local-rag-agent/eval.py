"""
(ข) eval harness — วัด retrieval 4 โหมดด้วย golden set

ทำไมต้องวัด: "ไม่มี eval set = ปรับจูนแบบเดา" (kb/rag-fundamentals.md)
วัด 2 ค่า ห้ามรวมกัน:
  recall@k = จาก golden ทั้งหมด กี่สัดส่วนที่ chunk 'ถูก' ติด top-k
  MRR      = เฉลี่ย 1/อันดับของ chunk ถูกตัวแรก (ยิ่งสูง = ดันของถูกขึ้นบนสุด)

4 โหมด (ไล่จาก lexical -> semantic):
  grep   = keyword overlap  (จำลอง 'agent grep หา term') = baseline ของ md-only setup
  bm25   = lexical + IDF weighting
  dense  = semantic (embedding + cosine)
  hybrid = dense + bm25 รวมด้วย RRF

รันบน LAB_KB (4 ไฟล์ รู้ ground truth แน่นอน) -> ตัวเลขเชื่อถือได้
อยากวัดบนต้นไม้จริง: เขียน golden set ของตัวเองแล้วแก้ KB ด้านล่างเป็น REAL_KB
"""
import json
import pathlib

import numpy as np

from config import LAB_KB, MAX_CHARS, TOP_K, CANDIDATES
from chunker import build_chunks
from embeddings import embed_passages, embed_query
from retriever import BM25, rrf, tokenize

GOLDEN = pathlib.Path(__file__).parent / "golden.jsonl"
KB = LAB_KB          # <- เปลี่ยนเป็น REAL_KB ได้ถ้ามี golden set ของต้นไม้จริง


def load_golden():
    with open(GOLDEN, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def grep_scores(chunks, query):
    """lexical baseline: นับ query token ที่โผล่เป็น substring ใน chunk"""
    qtok = set(tokenize(query))
    s = np.zeros(len(chunks), dtype="float32")
    for i, c in enumerate(chunks):
        text = c["embed_text"].lower()
        s[i] = sum(1 for t in qtok if t in text)
    return s


def is_hit(chunk, gold):
    if not chunk["file"].endswith(gold["file"]):
        return False
    h = gold.get("heading", "")
    return h.lower() in chunk["heading"].lower() if h else True


def ranked(chunks, vectors, bm25, dense_cache, query, mode, k):
    if mode == "grep":
        return np.argsort(-grep_scores(chunks, query))[:k].tolist()
    if mode == "bm25":
        return np.argsort(-bm25.scores(tokenize(query)))[:k].tolist()
    dense = dense_cache[query]
    if mode == "dense":
        return np.argsort(-dense)[:k].tolist()
    # hybrid
    d = np.argsort(-dense)[:CANDIDATES].tolist()
    b = np.argsort(-bm25.scores(tokenize(query)))[:CANDIDATES].tolist()
    return [i for i, _ in rrf([d, b])[:k]]


def main():
    chunks = build_chunks(KB, MAX_CHARS)
    print(f"[eval] KB={KB.name}  chunks={len(chunks)}")
    vectors = embed_passages([c["embed_text"] for c in chunks])
    bm25 = BM25([tokenize(c["embed_text"]) for c in chunks])
    golden = load_golden()

    # embed ทุก query ครั้งเดียว (dense + hybrid ใช้ร่วมกัน)
    dense_cache = {g["q"]: vectors @ embed_query([g["q"]])[0] for g in golden}
    k = TOP_K

    print(f"[eval] golden={len(golden)}  metric @k={k}\n")
    print(f"{'mode':7} {'recall@k':>9} {'MRR':>7}")
    print("-" * 25)
    for mode in ["grep", "bm25", "dense", "hybrid"]:
        hits, rr = 0, 0.0
        for g in golden:
            idx = ranked(chunks, vectors, bm25, dense_cache, g["q"], mode, k)
            rank = next((r for r, i in enumerate(idx, 1) if is_hit(chunks[i], g)), None)
            if rank:
                hits += 1
                rr += 1.0 / rank
        print(f"{mode:7} {hits/len(golden):>9.2f} {rr/len(golden):>7.2f}")
    print("\nอ่านผล: exact-term (RRF/.gguf/MCP) -> grep/bm25 เด่น;",
          "paraphrase -> dense เด่น; hybrid ควรนิ่งสุด")


if __name__ == "__main__":
    main()
