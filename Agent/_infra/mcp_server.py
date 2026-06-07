#!/usr/bin/env python3
"""MCP server exposing semantic search over the agent knowledge base.

Run by Claude Code (configured in ~/.claude/settings.json) — not started manually
in production. To test manually: python mcp_server.py (then it waits on stdio).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# The embedding model is already cached locally. Force offline so SentenceTransformer
# does not make a network call to HuggingFace on load — that call fails with an SSL
# cert error in some environments and breaks search_knowledge. Must be set before the
# sentence_transformers / huggingface_hub import below.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from mcp.server.fastmcp import FastMCP
from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue
from sentence_transformers import SentenceTransformer

# Configuration via env or defaults
COLLECTION = os.environ.get("MCP_COLLECTION", "agent_knowledge")
EMBED_MODEL = os.environ.get("MCP_EMBED_MODEL", "BAAI/bge-large-en-v1.5")
QDRANT_HOST = os.environ.get("MCP_QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.environ.get("MCP_QDRANT_PORT", "6333"))
AGENT_ROOT = Path(os.environ.get("MCP_AGENT_ROOT", Path.home() / "Documents/Projects/Agent"))

# Lazy-init globals (loaded on first call)
_client: QdrantClient | None = None
_model: SentenceTransformer | None = None


def _client_singleton() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return _client


def _model_singleton() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


mcp = FastMCP("agent-knowledge")


@mcp.tool()
def search_knowledge(
    query: str,
    top_k: int = 5,
    role_filter: str | None = None,
    company_filter: str | None = None,
    category_filter: str | None = None,
) -> list[dict[str, Any]]:
    """Semantic search over the agent knowledge base.

    Args:
        query: Natural-language question or topic.
        top_k: Number of top results to return (default 5, max 20).
        role_filter: Optional role to filter by, e.g. "data-architect", "ml-engineer".
        company_filter: Optional company name, e.g. "ntt".
        category_filter: Optional category — "role", "company", "pipeline", or "general".

    Returns:
        List of dicts with: file, content, score (cosine similarity), and metadata.
    """
    top_k = max(1, min(20, top_k))
    client = _client_singleton()
    model = _model_singleton()

    query_vec = model.encode(query, normalize_embeddings=True).tolist()

    conditions: list[FieldCondition] = []
    if role_filter:
        conditions.append(FieldCondition(key="role", match=MatchValue(value=role_filter)))
    if company_filter:
        conditions.append(FieldCondition(key="company", match=MatchValue(value=company_filter)))
    if category_filter:
        conditions.append(FieldCondition(key="category", match=MatchValue(value=category_filter)))

    query_filter = Filter(must=conditions) if conditions else None

    # qdrant-client >=1.14 removed .search(); use .query_points() and take .points
    results = client.query_points(
        collection_name=COLLECTION,
        query=query_vec,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True,
    ).points

    return [
        {
            "file": r.payload.get("file"),
            "content": r.payload.get("content"),
            "score": round(r.score, 4),
            "role": r.payload.get("role"),
            "company": r.payload.get("company"),
            "category": r.payload.get("category"),
        }
        for r in results
    ]


@mcp.tool()
def list_files(prefix: str | None = None) -> list[str]:
    """List all knowledge files known to the index, optionally filtered by path prefix.

    Args:
        prefix: e.g. "roles/technical/architect/" to filter by path prefix.

    Returns:
        Sorted list of file paths (relative to Agent root).
    """
    client = _client_singleton()
    # Scroll all unique file paths (cap at 5000 — enough for our scale)
    seen: set[str] = set()
    next_page = None
    while True:
        records, next_page = client.scroll(
            collection_name=COLLECTION,
            limit=500,
            offset=next_page,
            with_payload=["file"],
            with_vectors=False,
        )
        for rec in records:
            f = rec.payload.get("file")
            if f and (prefix is None or f.startswith(prefix)):
                seen.add(f)
        if next_page is None:
            break
    return sorted(seen)


@mcp.tool()
def collection_stats() -> dict[str, Any]:
    """Quick stats about the indexed collection (useful for diagnostics)."""
    client = _client_singleton()
    info = client.get_collection(COLLECTION)
    return {
        "name": COLLECTION,
        "points_count": info.points_count,
        # vectors_count was removed from CollectionInfo in qdrant-client >=1.14; guard it.
        "vectors_count": getattr(info, "vectors_count", None),
        "status": str(info.status),
    }


if __name__ == "__main__":
    mcp.run()
