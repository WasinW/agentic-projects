# CLAUDE.md — neurx (KB context)

> **STATUS: KILLED-as-registry 2026-07-18.** NeurX is dead as a standalone agent registry.
> Trust/provenance IP merged into **Regent** (`../regent-ai/`, the single Track B "Agent Trust &
> Governance" project). Runtime + Observability pillars cut permanently. Formal decision:
> [`knowledge/adr-0001-kill-as-registry-2026-07-18.md`](knowledge/adr-0001-kill-as-registry-2026-07-18.md).
> This is a KILL, not a park — do not resume a build. A future trust product = a NEW underwrite (see ADR).
> Everything below is FROZEN historical context; do not act on it.

Project-scoped agent context for **NeurX** — Agent Infrastructure & Registry
(the "npm of agents"). Architect + product-strategist lens, reframed for the
agentic era. Track B (vision). NOT a model marketplace — that vision is dead.

## What to read first
1. `…/projects-knowledge-base/01-projects-master-knowledge.md` §B1 — source of truth.
2. Reframing principle §4: unit of AI = agent + workflow + context, NOT model.
3. [INDEX.md](INDEX.md) — this project's KB map.

## Mental model (don't violate)
- Agent-centric, not model-centric. HF/Replicate/Together/OpenRouter own models — stay out.
- Four pillars: Agent **Registry** (publish/discover/version) · **Interop** (MCP, A2A) ·
  **Runtime** (host LangGraph/CrewAI serverless) · **Observability** (trace/replay).
- Lumora = potential customer-zero; Library Framework workflows could ship here.
- OPEN: open-core+hosting vs closed SaaS · global vs Thai/SEA · solo vs raise. Ask, don't assume.

## Agents to consult — all COMMON (live in `roles/` + `~/.claude/agents`, shared by every project)
Lead: ai-architect (agentic platform arch) · platform-architect (platform-as-product:
registry, golden paths, multi-tenancy) · ai-engineer (MCP/A2A, agent runtime).
Support: solution-architect · software-engineer · business-analyst · investment-consultant ·
devops-engineer (serverless hosting) · enterprise-architect (positioning) ·
security-engineer (multi-tenant isolation).
> NOT this project's agents — shared consulting layer. Don't copy them here.

## This project's own assets (SPECIFIC — live in this folder)
- **Specific skill** (this project's core IP) → `skills/`: `agent-registry-patterns`
  (publish/discover/version — the registry IS NeurX's product).
- **Common skills** (in `~/.claude/skills`, reusable by any AI project, to create):
  `agent-protocol-design` (MCP/A2A), `mcp-integration`.
- **Knowledge** → `knowledge/`: protocol landscape, competitor map, positioning.

## Conventions
- This is architecture + positioning stage. Clarify the wedge before any build.
- Reality-check 2024 plans against 2026 (MCP/A2A maturity, LangSmith lock-in).
