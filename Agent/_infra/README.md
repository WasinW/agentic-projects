# Agent Knowledge — MCP + Vector DB (local)

Semantic search over every markdown file under `~/Documents/Projects/Agent/`,
exposed to Claude Code sessions as MCP tools. Local, free, no API keys.

See the full design in `~/Documents/Projects/MCP_VECTOR_DB_DESIGN.md`.

## Stack

| Component | Choice |
|---|---|
| Vector DB | Qdrant (Docker, port 6333) |
| Embedding | `BAAI/bge-large-en-v1.5` (1024-dim, local) |
| MCP server | Python FastMCP |

## ⚠️ Platform note (this machine = Intel macOS / x86_64)

PyTorch's last x86_64 macOS wheel is **2.2.2**, which forces `numpy<2` and
`transformers<5`. `requirements.txt` is pinned accordingly — **do not bump torch**
on this machine or the stack breaks. (On Apple Silicon you could use latest.)

## First-time setup

```bash
cd ~/Documents/Projects/Agent/_infra

# 1. Start Qdrant
docker compose up -d
curl http://localhost:6333/healthz        # → ok

# 2. Python env (uv is fastest; plain venv also works)
uv venv --python 3.11 .venv
uv pip install -p .venv/bin/python -r requirements.txt

# 3. Build the index (first run downloads the ~1.3 GB embedding model)
./reindex.sh --reset
```

## Daily use

The MCP server is launched automatically by Claude Code (configured under
`mcpServers` in `~/.claude.json` — NOT settings.json). You don't start `mcp_server.py` by hand.

Tools exposed to Claude / subagents:

- `mcp__agent-knowledge__search_knowledge(query, top_k=5, role_filter=…, company_filter=…, category_filter=…)`
- `mcp__agent-knowledge__list_files(prefix=…)`
- `mcp__agent-knowledge__collection_stats()`

## Re-indexing

Re-run after editing any `knowledge.md` (e.g. after KNOWLEDGE_CHECKLIST Prompt A/B/C):

```bash
./reindex.sh            # upsert — only changed chunks update
./reindex.sh --reset    # wipe + full rebuild (use after deleting/renaming files)
```

`upsert` does not delete chunks for removed sections — run `--reset` periodically
to prune stale chunks.

## Manual checks

```bash
# Index populated?
.venv/bin/python -c "from qdrant_client import QdrantClient; \
print(QdrantClient(host='localhost',port=6333).get_collection('agent_knowledge').points_count)"

# Search works?
.venv/bin/python -c "from mcp_server import search_knowledge; \
[print(round(r['score'],3), r['file']) for r in search_knowledge('DLQ replay', top_k=3)]"
```

## Files

| File | Purpose |
|---|---|
| `docker-compose.yml` | Qdrant service |
| `requirements.txt` | Python deps (pinned for Intel macOS) |
| `embed_knowledge.py` | Indexing pipeline (chunk → embed → upsert) |
| `mcp_server.py` | MCP server (3 tools over Qdrant) |
| `reindex.sh` | Convenience wrapper around `embed_knowledge.py` |
| `qdrant_storage/` | Qdrant data (gitignored) |
| `.venv/` | Python venv (gitignored) |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Cannot connect to Qdrant` | `docker compose up -d` |
| MCP server not visible in Claude | Restart VS Code; check `mcpServers` in `~/.claude.json` |
| Search returns empty | `./reindex.sh --reset` |
| `no module named 'mcp'` | Use the venv python in the `~/.claude.json` mcpServers entry |

```bash
docker logs agent-qdrant -f                                       # Qdrant logs
tail -f ~/Library/Logs/Claude/mcp-server-agent-knowledge.log      # MCP server logs
```
