# MCP + Vector DB — Design + Implementation Guide

> Detailed plan to add semantic knowledge search to the agent system via MCP + Qdrant.
> Goal: implementable end-to-end in one session by following this doc.

---

## 0. TL;DR

**What we're building**:
A local **MCP server** that exposes a `search_knowledge(query)` tool to all Claude sessions on this machine. Behind it: a **Qdrant vector DB** indexed with semantic chunks of every markdown file under `~/Documents/Projects/Agent/`.

**Why**:
- Subagents currently read whole knowledge.md files (~30 KB each) to answer. Wasteful.
- Semantic search returns only the **relevant chunks** → 80%+ context savings, faster, cheaper.
- Cross-file linking happens automatically via embeddings.

**Stack** (chosen for: simple, free, local, robust):

| Component | Choice | Why |
|---|---|---|
| Vector DB | **Qdrant** (Docker) | Best self-hosted UX, Rust performance, mature filters |
| Embedding | **bge-large-en-v1.5** | OSS, free, strong benchmarks, 1024-dim |
| MCP server | **Python FastMCP** | Official Anthropic SDK, fastest to write |
| Chunking | Header + size hybrid | Respects markdown structure |
| Reindex trigger | Manual script + git pre-commit (later) | Simple to start |

**Cost**: $0 in API fees. Disk: ~50–200 MB for Qdrant + ~2 GB for embedding model.

---

## 0.5 Implementation notes — deviations from this doc (Phase 1 built 2026-05-31)

Three things in the original steps below are out of date / platform-specific. The build works; these are the corrections actually applied:

1. **Python deps must be pinned on Intel macOS (x86_64).** PyTorch's last x86_64 macOS wheel is **2.2.2**, which forces `numpy<2` and `transformers<5`. Unpinned `sentence-transformers>=3.0.0` pulls torch≥2.4 + numpy 2.x and the whole stack fails to import. `requirements.txt` is pinned to: `torch==2.2.2`, `numpy<2`, `transformers==4.44.2`, `sentence-transformers==3.0.1`. (On Apple Silicon you can use latest.) Used `python3.11` + `uv` for the venv.

2. **MCP server registration is NOT via `settings.json`.** Claude Code v2.1.50 rejects an `mcpServers` key in `~/.claude/settings.json` (schema validation fails). Register via CLI instead — writes to `~/.claude.json`:
   ```bash
   claude mcp add agent-knowledge -s user -e PYTHONUNBUFFERED=1 -- \
     /Users/wasin/Documents/Projects/Agent/_infra/.venv/bin/python \
     /Users/wasin/Documents/Projects/Agent/_infra/mcp_server.py
   ```
   (`-s user` = available in all projects.) Still requires a VS Code restart to load. Step 3.6 below is obsolete; ignore the JSON snippet.

3. **qdrant-client ≥1.14 API changes** broke the original `mcp_server.py`. Two fixes applied:
   - `client.search(query_vector=…)` → **`client.query_points(query=…, …).points`**
   - `CollectionInfo.vectors_count` was removed → use `getattr(info, "vectors_count", None)`.

   The `mcp_server.py` in `_infra/` already has these fixes; the code in Step 3.5 below is the original (pre-fix) version.

---

## 1. Mental Model

```
                 ┌──────────────────────────────────┐
                 │  Subagent (Claude)               │
                 │  "I need info on DLQ replay"     │
                 └────────────┬─────────────────────┘
                              │ MCP tool call
                              │ search_knowledge(query="DLQ replay policies",
                              │                  role_filter="data-ops", top_k=5)
                              ▼
                 ┌──────────────────────────────────┐
                 │  MCP Server (Python, local)      │
                 │  • Receives tool calls            │
                 │  • Embeds query (bge-large)       │
                 │  • Searches Qdrant                │
                 │  • Returns top-k chunks + meta    │
                 └────────────┬─────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
       ┌────────────┐  ┌────────────┐  ┌────────────┐
       │  Qdrant    │  │ Embedding  │  │ Filesystem │
       │  (Docker)  │  │ model      │  │ canonical  │
       │  port 6333 │  │ in-process │  │ Agent/*.md │
       │  REST/gRPC │  │            │  │            │
       └────────────┘  └────────────┘  └────────────┘
                              ▲
                              │ (separate process — runs on demand)
                 ┌────────────┴─────────────────────┐
                 │  Embedding pipeline (Python)     │
                 │  • Walks Agent/**.md             │
                 │  • Chunks by markdown headers     │
                 │  • Embeds + upserts to Qdrant     │
                 │  • Run manually or by git hook    │
                 └──────────────────────────────────┘
```

**Read path**: subagent → MCP server → Qdrant search → return chunks.
**Write path**: separate script reindexes when files change.

---

## 2. Directory Layout (what we'll create)

```
~/Documents/Projects/Agent/_infra/
├── docker-compose.yml          # Qdrant service
├── qdrant_storage/             # Qdrant data (gitignored)
├── requirements.txt            # Python deps
├── embed_knowledge.py          # Indexing script
├── mcp_server.py               # MCP server
├── reindex.sh                  # Convenience wrapper
└── README.md                   # Local run instructions
```

The `_infra/` prefix keeps it out of normal knowledge browsing.

---

## 3. Phase 1 — Step-by-Step Implementation

### Step 3.1 — Install Docker (if not installed)

```bash
# Check
docker --version

# If missing on macOS:
brew install --cask docker
# Then open Docker Desktop once
```

### Step 3.2 — Create `_infra/` and start Qdrant

```bash
mkdir -p ~/Documents/Projects/Agent/_infra/qdrant_storage
cd ~/Documents/Projects/Agent/_infra
```

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: agent-qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"  # REST
      - "6334:6334"  # gRPC
    volumes:
      - ./qdrant_storage:/qdrant/storage
    environment:
      QDRANT__SERVICE__GRPC_PORT: 6334
      QDRANT__LOG_LEVEL: INFO
```

Start it:

```bash
docker compose up -d
# Verify
curl http://localhost:6333/healthz
# Expect: ok
```

Web UI for debugging: <http://localhost:6333/dashboard>

### Step 3.3 — Python environment

```bash
cd ~/Documents/Projects/Agent/_infra
python3 -m venv .venv
source .venv/bin/activate
```

Create `requirements.txt`:

```text
qdrant-client>=1.12.0
sentence-transformers>=3.0.0
mcp>=1.0.0
python-frontmatter>=1.1.0
watchfiles>=0.24.0
```

Install:

```bash
pip install -r requirements.txt
```

The first run of `sentence-transformers` will download `bge-large-en-v1.5` (~1.3 GB) — one-time.

### Step 3.4 — Embedding pipeline (`embed_knowledge.py`)

```python
#!/usr/bin/env python3
"""Index agent knowledge files into Qdrant.

Run manually:   python embed_knowledge.py
Or with arg:    python embed_knowledge.py --reset    (wipe collection first)
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

ROOT = Path.home() / "Documents/Projects/Agent"
COLLECTION = "agent_knowledge"
EMBED_MODEL = "BAAI/bge-large-en-v1.5"
VECTOR_DIM = 1024
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# Folders to skip
SKIP_DIRS = {".git", "node_modules", "_infra", "qdrant_storage"}
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
        # roles/technical/architect/data-architect/knowledge.md
        if len(parts) >= 4:
            meta["role"] = parts[3]
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
    args = parser.parse_args()

    print(f"loading embedding model {EMBED_MODEL}...")
    model = SentenceTransformer(EMBED_MODEL)

    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    ensure_collection(client, args.reset)

    total_chunks = 0
    total_files = 0
    for md in sorted(ROOT.rglob("*.md")):
        # Skip if any parent is in SKIP_DIRS
        if any(part in SKIP_DIRS for part in md.relative_to(ROOT).parts):
            continue
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
```

Run it:

```bash
python embed_knowledge.py --reset
```

First run downloads the embedding model (~1.3 GB). Then indexes — expect a couple of minutes for ~200 files.

### Step 3.5 — MCP server (`mcp_server.py`)

```python
#!/usr/bin/env python3
"""MCP server exposing semantic search over the agent knowledge base.

Run by Claude Code (configured in ~/.claude/settings.json) — not started manually
in production. To test manually: python mcp_server.py (then it waits on stdio).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

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

    results = client.search(
        collection_name=COLLECTION,
        query_vector=query_vec,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True,
    )

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
        "vectors_count": info.vectors_count,
        "status": str(info.status),
    }


if __name__ == "__main__":
    mcp.run()
```

### Step 3.6 — Register MCP server with Claude Code

Edit `~/.claude/settings.json` — add the `mcpServers` section. Full path to your venv's Python:

```jsonc
{
  "permissions": { ... },
  "mcpServers": {
    "agent-knowledge": {
      "command": "/Users/wasin/Documents/Projects/Agent/_infra/.venv/bin/python",
      "args": [
        "/Users/wasin/Documents/Projects/Agent/_infra/mcp_server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**Restart Claude Code** (close + reopen VS Code window) to pick up the MCP server.

### Step 3.7 — Update subagents to use the MCP tool

The MCP tool will appear to subagents as `mcp__agent-knowledge__search_knowledge`.

Update each subagent's frontmatter `tools` list. Example for `~/.claude/agents/architect/data-architect.md`:

```markdown
---
name: data-architect
description: ...
tools: Read, Glob, Grep, WebSearch, WebFetch, mcp__agent-knowledge__search_knowledge, mcp__agent-knowledge__list_files
model: inherit
---

You are a **Data Architect** consultant. Senior, opinionated, but humble about trade-offs.

## How you work

1. **First, search semantically**: call `mcp__agent-knowledge__search_knowledge(query="...", role_filter="data-architect", top_k=5)` to retrieve the most relevant chunks of your knowledge base.
2. **If you need full context** of a chunk's source file (the `file` field returned), use Read on `~/Documents/Projects/Agent/<file>`.
3. **For project-specific (The-1) questions**, also try `company_filter="ntt"` to include project context.
4. Sketch architecture in ASCII when useful; cite trade-offs explicitly.
... [rest of system prompt unchanged]
```

To update all 18 subagents in one pass, ask Claude in the next session.

### Step 3.8 — Convenience scripts

`_infra/reindex.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate
python embed_knowledge.py "$@"
```

```bash
chmod +x reindex.sh
```

`_infra/.gitignore`:

```text
.venv/
qdrant_storage/
__pycache__/
*.pyc
```

`_infra/README.md` — short local-run cheatsheet (Claude will write this in the new session).

---

## 4. Testing — Verify Everything Works

### 4.1 Qdrant healthy

```bash
curl http://localhost:6333/healthz       # → ok
curl http://localhost:6333/collections   # → JSON listing
```

### 4.2 Index populated

```bash
cd ~/Documents/Projects/Agent/_infra
source .venv/bin/activate
python -c "
from qdrant_client import QdrantClient
c = QdrantClient(host='localhost', port=6333)
info = c.get_collection('agent_knowledge')
print(f'points: {info.points_count}')
"
# Expect: ~1000-3000 points (varies by chunk size)
```

### 4.3 Manual search works

```bash
python -c "
from mcp_server import search_knowledge
results = search_knowledge('how to handle DLQ replay', top_k=3)
for r in results:
    print(f\"{r['score']:.3f}  {r['file']}\")
    print(f\"    {r['content'][:200]}...\")
    print()
"
```

### 4.4 Claude sees the MCP server

In the new Claude session, ask:

```
List the MCP tools available to you, and what arguments they take.
```

Claude should mention `mcp__agent-knowledge__search_knowledge`, `list_files`, `collection_stats`.

### 4.5 Subagent uses it end-to-end

```
Get the data architect's take on Iceberg merge-on-read vs copy-on-write trade-offs.
```

The spawned data-architect subagent should call `search_knowledge` and reference results from `roles/technical/architect/data-architect/knowledge.md` and possibly `roles/technical/engineer/de-engineer/knowledge.md`.

---

## 5. Maintenance + Re-indexing

### When to re-index

- After significant updates to any `knowledge.md`
- After running KNOWLEDGE_CHECKLIST Prompt A/B/C (which append content)
- After adding/renaming files

### Manual

```bash
~/Documents/Projects/Agent/_infra/reindex.sh
```

`upsert` semantics mean unchanged chunks are no-ops; only changed chunks update. Full reindex takes ~1-2 minutes.

### Force full reset

```bash
~/Documents/Projects/Agent/_infra/reindex.sh --reset
```

### Optional: automated re-index on git commit

If you put `Agent/` under git, add `.git/hooks/pre-commit` (or use husky):

```bash
#!/usr/bin/env bash
# Re-index if any *.md changed
if git diff --cached --name-only | grep -qE '\.md$'; then
  echo "Re-indexing knowledge base..."
  ~/Documents/Projects/Agent/_infra/reindex.sh
fi
```

### Watch mode (optional, future)

`embed_knowledge.py` can be extended with `watchfiles` to re-embed on save. Not in MVP.

---

## 6. Phase 2 + 3 (after MVP works)

### Phase 2 — Hybrid Search + Quality

- **Add BM25 sparse retrieval** (Qdrant supports it natively) → better on exact terms (names, IDs, acronyms).
- **Reciprocal Rank Fusion (RRF)** to combine dense + sparse.
- **Reranking** with `bge-reranker-large` or Cohere Rerank API on top-50 → top-5.
- **Query expansion** (LLM rewrites query before search).

Cost: still local + free if using bge-reranker.

### Phase 3 — Memory + Multi-modal

- **Conversation memory** — index past Claude conversations into the same collection (separate namespace).
- **Knowledge graph overlay** — extract entities + relationships from knowledge.md, store edges in a graph DB (Neo4j / Memgraph).
- **Multi-modal** — index diagram screenshots with CLIP embeddings if Agent/ accumulates images.

These are 1-2 week projects each. Don't pursue until Phase 1 is stable.

---

## 7. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Cannot connect to Qdrant` | Container not running | `docker compose up -d` in `_infra/` |
| MCP server doesn't appear in Claude | Settings not loaded | Restart VS Code window; check `~/.claude/settings.json` syntax |
| Embeddings very slow | First-time model download | One-time cost (~2 minutes for 1.3 GB) |
| `RuntimeError: no module named 'mcp'` | Wrong Python | Use the venv path in settings.json |
| Search returns empty | Collection not populated | Run `embed_knowledge.py --reset` |
| Search returns wrong role | Filter not applied | Subagent must pass `role_filter` arg |
| Container OOMs | Qdrant memory limits | Add `mem_limit: 2g` to docker-compose |
| File diff: chunks remain after deletion | Upsert doesn't delete | Run `--reset` periodically |

### Logs

```bash
docker logs agent-qdrant -f                              # Qdrant logs
tail -f ~/Library/Logs/Claude/mcp-server-agent-knowledge.log  # MCP server logs (Claude Code captures)
```

---

## 8. Cost + Resource Footprint

| Resource | Amount |
|---|---|
| Docker container (Qdrant) | ~150-300 MB RAM idle, ~500 MB-2 GB under load |
| Embedding model (bge-large) | ~1.3 GB disk, ~2 GB RAM when loaded |
| Qdrant storage | ~100-300 MB for ~3000 chunks |
| MCP server process | ~2 GB RAM (model loaded), ~100 MB CPU spike per query |
| API costs | $0 (everything local) |

Total: ~4 GB RAM headroom needed, ~5 GB disk.

---

## 9. Why these choices (FAQ)

**Why Qdrant over Chroma / Weaviate / pgvector?**
- Chroma: embedded, but limited filter performance + dev-only ergonomics.
- Weaviate: heavier, more features than needed.
- pgvector: great if you have Postgres; overkill to add one.
- Qdrant: best balance of speed (Rust), features (filters, hybrid), ops (single Docker container), and active community.

**Why bge-large over OpenAI embeddings?**
- Free, runs locally, no API key juggling.
- 2026 OSS benchmarks (MTEB): bge-large is competitive with closed APIs on retrieval.
- If you later want managed: switch to `voyage-3` or OpenAI `text-embedding-3-large` — only the script changes; collection schema stays the same (re-embed required).

**Why FastMCP (Python) over TypeScript SDK?**
- FastMCP is now the official Python SDK, much less boilerplate than TS.
- Embedding ecosystem is Python-native; staying in one language is simpler.

**Why not just use Anthropic's filesystem MCP server?**
- It provides file listing + reading, not semantic search.
- We need the embedding pipeline anyway.

**Will this scale to 10k+ files?**
- Yes. Qdrant handles millions of vectors. The embedding pipeline gets slow (~10s of minutes) but is rarely re-run from scratch.

---

## 10. Migration story: subagent update

Currently each subagent file (`~/.claude/agents/*/*.md`) instructs:

```
Read `~/Documents/Projects/Agent/roles/technical/architect/<role>/knowledge.md`
```

After MCP is live, swap to:

```
Call mcp__agent-knowledge__search_knowledge(query="...", role_filter="<role>") first.
Only Read full files if the search results aren't enough.
```

A pre-built migration prompt (run this in the new session after MCP is verified working):

```
Update all 18 subagent files under ~/.claude/agents/ to use the MCP knowledge search
as the primary discovery mechanism, keeping Read as a fallback.

For each file:
1. Add to the `tools:` frontmatter line: mcp__agent-knowledge__search_knowledge, mcp__agent-knowledge__list_files
2. Replace the "Read knowledge.md" instruction with:
   - First call mcp__agent-knowledge__search_knowledge(query="...", role_filter="<this-agent-id>", top_k=5)
   - If results insufficient, Read the file paths returned

Report which files changed and any frontmatter parse errors.
```

---

## 11. Bootstrap prompt for the new session

Paste this as your first message in the new session (after opening VS Code at `~/Documents/Projects/`):

```
Read SESSION_HANDOFF.md and MCP_VECTOR_DB_DESIGN.md.

Then implement Phase 1 of the MCP + Vector DB design, step by step:
1. Step 3.1-3.3: Docker + Qdrant + Python env
2. Step 3.4: embedding pipeline (run and verify the index populates)
3. Step 3.5-3.6: MCP server + settings.json config
4. Step 3.7: update ONE subagent (data-architect) as a test
5. Step 4: run the verification tests

Stop after each major step and report status before continuing.
Don't update all 18 subagents until I confirm the data-architect test works end-to-end.
```

---

## 12. References

- **Qdrant docs** — <https://qdrant.tech/documentation/>
- **FastMCP (Anthropic Python SDK)** — <https://github.com/modelcontextprotocol/python-sdk>
- **MCP specification** — <https://spec.modelcontextprotocol.io/>
- **bge-large-en-v1.5** — <https://huggingface.co/BAAI/bge-large-en-v1.5>
- **sentence-transformers** — <https://www.sbert.net/>
- **MTEB benchmarks** — <https://huggingface.co/spaces/mteb/leaderboard>

---

*Implement Phase 1 first. Don't reach for Phase 2-3 until Phase 1 has been used in real sessions for at least a week.*
