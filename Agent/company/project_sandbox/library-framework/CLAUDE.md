# CLAUDE.md — library-framework (KB context)

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
- Channel Count Formula: `MIN(S,A) ≤ N ≤ S×A` (S=subject breadth, A=audience segments).
- OPEN: separate product or pure internal IP for Lumora? Ask before assuming.

## Agent routing (reuse from ~/.claude/agents, don't create)
**Common core:** solution-architect (system design) · software-engineer (build) ·
business-analyst (requirements/stories) · investment-consultant (productize-or-not case).
**Specific:** content-strategist (taxonomy = content strategy) · ai-engineer
(the agent/workflow that *runs* the framework) · ux-designer (framework usability) ·
platform-architect (only if productized as a licensable platform).

## Skills
Reuse Lumora's: `lumora-combo-recommend`, `lumora-content-batch` (these already
operationalize C×T×M). To create: `content-taxonomy` (axis definitions + validation),
`agent-workflow-design`. All live in `~/.claude/skills`.

## Conventions
- Keep framework definitions tool-agnostic; Lumora-specific bindings stay in Lumora KB.
- Any change to an axis/formula = note it here and in the master doc.
