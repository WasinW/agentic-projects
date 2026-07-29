"""
STEP 4: hybrid retrieval = dense + BM25 รวมด้วย RRF

ทำไมต้อง hybrid:
  dense พลาด exact term  (ชื่อ table, error code, config key)
  BM25  พลาด paraphrase  ("job ล่ม" vs "SDK harness OOM")

ทำไมรวมด้วย RRF ไม่ใช่บวก score:
  score ของสองระบบคนละสเกล เทียบกันไม่ได้ -> รวมที่ 'อันดับ' แทน
"""
import json
import math
import re
from collections import Counter, defaultdict

import numpy as np

# ---------- tokenizer ----------
try:
    from pythainlp.tokenize import word_tokenize as _th_tok

    def tokenize(t):
        return [w.strip().lower() for w in _th_tok(t, engine="newmm") if w.strip()]
except ImportError:
    # fallback: ไทยจะถูกรวบเป็นก้อนเดียว -> BM25 ไทยจะอ่อนลงมาก
    def tokenize(t):
        return re.findall(r"[a-zA-Z0-9_]+|[\u0E00-\u0E7F]+", t.lower())


# ---------- BM25 (เขียนเองประมาณ 30 บรรทัด) ----------
class BM25:
    def __init__(self, corpus_tokens, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.docs = corpus_tokens
        self.N = len(corpus_tokens)
        self.avgdl = sum(len(d) for d in corpus_tokens) / max(self.N, 1)
        self.tf = [Counter(d) for d in corpus_tokens]
        df = Counter()
        for d in corpus_tokens:
            df.update(set(d))
        # IDF: คำที่โผล่ทุก doc แทบไม่มีค่า / คำหายากมีค่าสูง
        self.idf = {w: math.log(1 + (self.N - n + 0.5) / (n + 0.5))
                    for w, n in df.items()}

    def scores(self, q_tokens):
        s = np.zeros(self.N, dtype="float32")
        for w in q_tokens:
            idf = self.idf.get(w)
            if idf is None:
                continue
            for i, tf in enumerate(self.tf):
                f = tf.get(w, 0)
                if f:
                    dl = len(self.docs[i])
                    s[i] += idf * f * (self.k1 + 1) / (
                        f + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
        return s


# ---------- RRF ----------
def rrf(rank_lists, k=60):
    """rank_lists = [[idx เรียงจากดีสุด], [...]]  -> [(idx, score)] เรียงแล้ว"""
    fused = defaultdict(float)
    for ranks in rank_lists:
        for rank, idx in enumerate(ranks):
            fused[idx] += 1.0 / (k + rank + 1)
    return sorted(fused.items(), key=lambda x: -x[1])


class Retriever:
    def __init__(self, index_dir, embed_fn):
        self.embed_fn = embed_fn
        self.vectors = np.load(index_dir / "vectors.npy")
        with open(index_dir / "chunks.jsonl", encoding="utf-8") as f:
            self.chunks = [json.loads(l) for l in f]
        self.bm25 = BM25([tokenize(c["embed_text"]) for c in self.chunks])

    def search(self, query, top_k=5, candidates=50, mode="hybrid"):
        # --- stage 1: ดึงกว้าง ---
        qv = self.embed_fn([query])[0]
        dense = self.vectors @ qv                    # normalize แล้ว = cosine
        d_rank = np.argsort(-dense)[:candidates].tolist()

        if mode == "dense":
            picked = d_rank[:top_k]
        elif mode == "bm25":
            picked = np.argsort(-self.bm25.scores(tokenize(query)))[:top_k].tolist()
        else:
            s_rank = np.argsort(-self.bm25.scores(tokenize(query)))[:candidates].tolist()
            picked = [i for i, _ in rrf([d_rank, s_rank])[:top_k]]

        # --- stage 2: child -> parent, กัน parent ซ้ำ ---
        out, seen = [], set()
        for i in picked:
            c = self.chunks[i]
            key = (c["file"], c["heading"])
            if key in seen:
                continue
            seen.add(key)
            out.append({"score": float(dense[i]), **c})
        return out


def format_for_llm(hits):
    """สิ่งที่โมเดลเห็นจริงๆ คือ 'string' อันนี้เท่านั้น - ไม่ใช่ vector"""
    parts = []
    for i, h in enumerate(hits, 1):
        parts.append(f"[{i}] source: {h['file']} | {h['heading']}\n{h['parent']}")
    return "\n\n---\n\n".join(parts) if parts else "(ไม่พบข้อมูลที่เกี่ยวข้อง)"
