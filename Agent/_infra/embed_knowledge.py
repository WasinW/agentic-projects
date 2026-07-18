#!/usr/bin/env python3
"""Index agent knowledge files into Qdrant.

Run via wrapper:  _infra/reindex.sh [--reset | --files A.md B.md]
Auto-invoked by the git pre-commit hook (_infra/hooks/pre-commit) for staged Agent/**/*.md.
Health check: _infra/doctor.sh (SessionStart hook).

Exclusion rule: any path part starting with "_" is machine-excluded (_archive, _inbox,
_template, _infra, _reviews) plus the names in SKIP_DIRS.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)
from sentence_transformers import SentenceTransformer

ROOT = Path.home() / "Documents/Projects/Agent"
COLLECTION = "agent_knowledge"
EMBED_MODEL = "BAAI/bge-large-en-v1.5"
VECTOR_DIM = 1024
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# Folders to skip (any "_"-prefixed path part is also skipped — see is_skipped)
SKIP_DIRS = {".git", "node_modules", "qdrant_storage", "archive", "knowledge_base_legacy", "memory", "bak_mem"}


def is_skipped(parts: tuple[str, ...]) -> bool:
    """Machine-exclusion rule: named skip dirs + any _-prefixed dir/file."""
    return any(part in SKIP_DIRS or part.startswith("_") for part in parts)
# Heuristic: chunks shouldn't exceed this many chars
MAX_CHUNK_CHARS = 1500
CHUNK_OVERLAP = 200


def stable_id(file_rel: str, chunk_index: int) -> int:
    """Generate a stable 64-bit int ID from file path + chunk index."""
    h = hashlib.md5(f"{file_rel}:{chunk_index}".encode()).hexdigest()
    # Qdrant point IDs are uint64
    return int(h[:16], 16)


def chunk_markdown(text: str) -> list[str]:
    """Chunk markdown by H2/H3 boundaries, then split long sections by chars."""
    # Split at headings to keep semantic units together
    sections = re.split(r"\n(?=##\s)", text)
    chunks: list[str] = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        if len(section) <= MAX_CHUNK_CHARS:
            chunks.append(section)
        else:
            # Sub-chunk with overlap
            stride = MAX_CHUNK_CHARS - CHUNK_OVERLAP
            for start in range(0, len(section), stride):
                piece = section[start : start + MAX_CHUNK_CHARS].strip()
                if piece:
                    chunks.append(piece)
    return chunks


def extract_metadata(rel_path: str) -> dict[str, str | None]:
    """Derive category + role/company from path."""
    parts = rel_path.split("/")
    meta: dict[str, str | None] = {"category": "general", "role": None, "company": None, "subproject": None}
    if len(parts) >= 1 and parts[0] == "roles":
        meta["category"] = "role"
        # role = the directory that contains the file. Works for both depths:
        #   roles/technical/architect/data-architect/knowledge.md -> "data-architect"
        #   roles/business/business-analyst/knowledge.md          -> "business-analyst"
        if len(parts) >= 3:
            meta["role"] = parts[-2]
    elif len(parts) >= 1 and parts[0] == "company":
        meta["category"] = "company"
        # company/ntt/the_one/knowledge/...
        if len(parts) >= 3:
            meta["company"] = parts[1]
            meta["subproject"] = parts[2]
    elif len(parts) >= 1 and parts[0] == "pipelines":
        meta["category"] = "pipeline"
    return meta


def index_file(client: QdrantClient, model: SentenceTransformer, path: Path) -> int:
    rel = str(path.relative_to(ROOT))
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError) as e:
        print(f"  skip {rel}: {e}")
        return 0

    chunks = chunk_markdown(content)
    if not chunks:
        return 0

    embeddings = model.encode(chunks, show_progress_bar=False, normalize_embeddings=True)
    meta = extract_metadata(rel)

    # Make per-file re-embedding idempotent: drop this file's old chunks first.
    # (Chunk boundaries shift when content changes, so stable_id mapping changes —
    # without this, stale chunks for the file would linger after an incremental update.)
    client.delete(
        collection_name=COLLECTION,
        points_selector=Filter(must=[FieldCondition(key="file", match=MatchValue(value=rel))]),
    )

    points = [
        PointStruct(
            id=stable_id(rel, i),
            vector=emb.tolist(),
            payload={
                "file": rel,
                "chunk_index": i,
                "content": chunk,
                **meta,
            },
        )
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
    ]

    client.upsert(collection_name=COLLECTION, points=points)
    return len(chunks)


def ensure_collection(client: QdrantClient, reset: bool) -> None:
    if reset and client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)
        print(f"deleted existing collection '{COLLECTION}'")
    if not client.collection_exists(COLLECTION):
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
        )
        print(f"created collection '{COLLECTION}'")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Wipe collection before indexing")
    parser.add_argument(
        "--files",
        nargs="*",
        help="Only (re-)embed these specific .md files (incremental). Paths may be "
        "absolute or relative to the Agent root. Used by the git pre-commit hook.",
    )
    args = parser.parse_args()

    # Build the work list: incremental (--files) or full walk
    if args.files:
        targets = []
        for raw in args.files:
            p = Path(raw)
            p = p if p.is_absolute() else (ROOT / raw)
            try:
                rel_parts = p.resolve().relative_to(ROOT).parts
            except ValueError:
                print(f"  skip (outside Agent root): {raw}")
                continue
            if is_skipped(rel_parts) or p.suffix != ".md":
                continue
            if p.exists():
                targets.append(p)
    else:
        targets = [
            md
            for md in sorted(ROOT.rglob("*.md"))
            if not is_skipped(md.relative_to(ROOT).parts)
        ]

    if not targets:
        print("nothing to index.")
        return 0

    print(f"loading embedding model {EMBED_MODEL}...")
    model = SentenceTransformer(EMBED_MODEL)

    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    ensure_collection(client, args.reset)

    total_chunks = 0
    total_files = 0
    for md in targets:
        n = index_file(client, model, md)
        if n:
            total_files += 1
            total_chunks += n
            print(f"  {n:>3} chunks  {md.relative_to(ROOT)}")

    print(f"\nIndexed {total_files} files / {total_chunks} chunks.")
    info = client.get_collection(COLLECTION)
    print(f"Collection size: {info.points_count} points.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
