# neurx — KB Index

> **STATUS: KILLED-as-registry 2026-07-18.** Killed as a standalone agent registry; trust/provenance IP
> merged into **Regent** (`../regent-ai/`). Runtime + Observability cut permanently. Decision:
> [`knowledge/adr-0001-kill-as-registry-2026-07-18.md`](knowledge/adr-0001-kill-as-registry-2026-07-18.md).
> KILL, not park — no un-kill as a registry; a future trust product is a NEW underwrite. Sections below are FROZEN.

Project-scoped knowledge base for **NeurX** — Agent Infrastructure & Registry.
Track B (AI ecosystem vision). The base layer: where agents live + discover each other.

- Code + docs: `~/Documents/Projects/Project/project_sandbox/neurx/`
- Master context: `…/projects-knowledge-base/01-projects-master-knowledge.md` §B1.

## Layout
```
neurx/
├── CLAUDE.md     ← how to work in this project
├── INDEX.md      ← this file
├── memory/       ← durable project facts
├── knowledge/    ← protocol notes, competitor map, positioning
└── skills/       ← project skill pointers (live in ~/.claude/skills)
```

## Status
**KILLED-as-registry 2026-07-18** (was: vision/architecture stage). See ADR-0001. Neutral-registry window
closed by AAIF/Linux Foundation consolidation + A2A v1.2 signed AgentCards (absorbed the trust wedge) +
hyperscaler marketplaces; two-sided cold-start unwinnable solo/part-time. Trust/provenance IP → Regent.
Runtime + Observability cut permanently. Lumora = Regent's customer-zero (not NeurX's).

## Agents — all COMMON (consulted from `roles/`, none owned by this project)
Lead: ai-architect, platform-architect, ai-engineer.
Support: solution-architect, software-engineer, business-analyst, investment-consultant, devops-engineer, enterprise-architect, security-engineer.

## Skills
- **Specific** (core IP, → `skills/`): `agent-registry-patterns` ✅ created (mirrored to ~/.claude/skills).
- **Common** (in `~/.claude/skills`, reusable, to create): `agent-protocol-design`, `mcp-integration`.

## Knowledge to capture
MCP + A2A protocol landscape · agent registry/versioning patterns · observability
(LangSmith and why it's LangChain-only) · competitor map (HF, Replicate, Together,
Fireworks, OpenRouter) · the 3 angles (global DX / Thai-SEA PDPA-default / vertical) ·
position in stack: NeurX (infra) ← Regent (governance) ← SentientNet (sovereignty).
