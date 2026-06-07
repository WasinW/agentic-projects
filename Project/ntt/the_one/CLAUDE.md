# Workspace — NTT / The-1

This is the **workspace** (code + active docs). For agent knowledge + role-based discussions, look at:

→ `~/Documents/Projects/Agent/company/ntt/the_one/` (project context + knowledge)
→ `~/Documents/Projects/Agent/INDEX.md` (top-level directory)
→ `~/.claude/CLAUDE.md` (global instructions)

## Layout (suggested)

```
~/Documents/Projects/Project/ntt/the_one/
├── code/        ← clone repos / active code
└── docs/        ← active design docs, drafts, exports
```

## When starting work

1. Note that legacy workspace is at `~/Documents/ntt_project/the_one/` — do not modify unless explicitly migrating.
2. For project conventions (Beam framework, hexagonal pattern, no-BQ-writes, etc.), see [Agent/company/ntt/the_one/CLAUDE.md](../../../Agent/company/ntt/the_one/CLAUDE.md).
3. For role-based input, spawn subagents (`data-architect`, `de-engineer`, `gcp-expert`, etc.).
