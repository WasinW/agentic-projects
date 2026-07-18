# CLAUDE.md — library-framework (KB context)

> **STATUS — FOLDED into LUMORA as internal IP (2026-07-18).**
> This is no longer a standalone project. The **canonical** framework file is
> `…/lumora/knowledge/01_creative_library.md` (Lumora v3). This directory is a
> **pointer only** — do not extend it; make framework changes in the Lumora canonical.
> **OPEN question resolved: internal IP** (not a separate product). Revisit as a
> standalone **only in 12 months, and only if ≥1 channel shows framework-attributable
> public growth**. If ever externalized, the route is **content-led authority
> (StoryBrand-style), NEVER a SaaS license.** See portfolio review §3.2.

Project-scoped agent context for the **Library Framework** — a generalizable
Content × Theme × Media taxonomy + production system. Lumora is its first
customer. Builder + product-strategist lens — NOT DE/pipeline, NOT a SaaS yet.

## What to read first
1. `…/projects-knowledge-base/01-projects-master-knowledge.md` §A2 — source of truth.
2. Lumora KB `…/lumora/knowledge/01_creative_library.md` — where the framework was born.
3. [INDEX.md](INDEX.md) — this project's KB map.

## Mental model (don't violate)
- The framework solves a *general* problem (diverse content at scale without
  homogenization), not just Lumora's. Treat Lumora as customer-zero, not as the product.
- Three post-level axes: **C** (content pillars C1-C10) × **T** (theme clusters) ×
  **M** (media formats M1-M12). Account-level fixed tags: Voice/Archetype, Persona,
  Niche Scope. Per-post optional: JTBD, HHH funnel stage.
- Channel Count Formula: `1 ≤ N ≤ S×A` (S=subject breadth, A=audience segments) — the V1/V2/V3 gates decide N; the old `MIN(S,A)` lower bound was pseudo-math (corrected 2026-07-18 in the Lumora canonical).
- ~~OPEN: separate product or pure internal IP?~~ **RESOLVED: internal IP** (see status banner above).

## Agents to consult — all COMMON (live in `roles/` + `~/.claude/agents`, shared by every project)
Lead: solution-architect · software-engineer · content-strategist (taxonomy = content strategy).
Support: business-analyst (requirements/stories) · investment-consultant (productize-or-not case) ·
ai-engineer (the agent/workflow that *runs* the framework) · ux-designer (usability) ·
platform-architect (only if productized as a license).
> These are NOT this project's agents — they're the shared consulting layer. Don't copy them here.

## This project's own assets (SPECIFIC — live in this folder)
- **Specific skill** (niche IP) → `skills/`: `content-taxonomy` (C×T×M axis defs + validation).
- **Reuse**: `lumora-combo-recommend`, `lumora-content-batch` (already operationalize C×T×M);
  `agent-workflow-design` (a COMMON skill in `~/.claude/skills`).
- **Knowledge** → `knowledge/`: axis defs, account-level tags, channel-count formula.

## Conventions
- Keep framework definitions tool-agnostic; Lumora-specific bindings stay in Lumora KB.
- Any change to an axis/formula = note it here and in the master doc.
