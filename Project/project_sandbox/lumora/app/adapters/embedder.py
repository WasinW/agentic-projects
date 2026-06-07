"""Embedder seam. MockEmbedder is the default — deterministic 1024-dim vectors
seeded by a text hash, so the pipeline embeds with NO model download / no GPU / $0.

Bge M3Embedder is a stub behind EMBEDDER=bge-m3 (needs sentence-transformers, which
is NOT installed by default — keeps the image tiny). Same 1024-dim output.
"""
from __future__ import annotations

import hashlib
import math

from app.core.settings import get_settings


class MockEmbedder:
    """Deterministic fake embedding. Same text -> same vector. Unit-norm-ish."""
    name = "mock"

    def __init__(self, dim: int = 1024):
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        # seed a tiny PRNG from the text hash -> reproducible pseudo-random vector
        h = hashlib.sha256(text.encode("utf-8")).digest()
        seed = int.from_bytes(h[:8], "big")
        vec = []
        x = seed or 1
        for _ in range(self.dim):
            x = (1103515245 * x + 12345) & 0x7FFFFFFF   # LCG
            vec.append((x / 0x7FFFFFFF) * 2 - 1)         # -> [-1, 1]
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


class Bge_M3Embedder:
    """Real bge-m3 embedder (1024-dim, Thai-friendly — decision #3).
    STUB: requires `sentence-transformers`, intentionally not a default dep.
    """
    name = "bge-m3"

    def __init__(self, dim: int = 1024):
        self.dim = dim
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer  # type: ignore
            self._model = SentenceTransformer("BAAI/bge-m3")
        return self._model

    def embed(self, text: str) -> list[float]:
        model = self._load()
        return model.encode(text, normalize_embeddings=True).tolist()


def get_embedder():
    s = get_settings()
    if s.embedder == "bge-m3":
        return Bge_M3Embedder(s.embedding_dim)
    return MockEmbedder(s.embedding_dim)
