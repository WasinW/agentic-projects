# CLAUDE.md — regent-ai (KB context)

Project-scoped agent context for **Regent AI** — Agent Governance & Trust Layer.
Architect + product-strategist lens, reframed for the agentic era. Track B (vision).
NOT model explainability/ethics — that space is crowded and the vision is dead.

## What to read first
1. `…/projects-knowledge-base/01-projects-master-knowledge.md` §B2 — source of truth.
2. Reframing §4 + stack diagram: Regent = governance layer *on top of* NeurX.
3. [INDEX.md](INDEX.md) — this project's KB map.

## Mental model (don't violate)
- The unsolved problem is **agent autonomy & liability**, not model explainability.
- Four pillars: **Audit Trail** (decision→reason→tools, replay) · **Policy Engine**
  (declarative guardrails: spend caps, domain limits, approval thresholds) ·
  **Multi-Agent Compliance** (provenance graph: who's responsible when 5 agents fail) ·
  **HITL Checkpoints** (approval at risk thresholds).
- Market pull = EU AI Act in force, US EOs, Singapore AI Verify, Thailand drafting.
- OPEN: generic vs vertical (finance/health) · SaaS vs open-core · separate product vs NeurX layer.

## Agent routing (reuse from ~/.claude/agents, don't create)
**Common core:** solution-architect · software-engineer · business-analyst · investment-consultant.
**Specific:** governance-consultant (PDPA, EU AI Act, BoT/SEC, model governance) ·
security-engineer (policy enforcement, audit, guardrails, zero-trust) ·
ai-architect (safety + evaluation infrastructure) · ai-engineer (guardrails —
NeMo / Llama Guard, eval — RAGAS/DeepEval).

## Skills
Reuse: `dpia-assessment` (already exists — PDPA/GDPR DPIA). To create:
`agent-policy-engine`, `audit-trail-design`, `ai-regulation-knowledge` (PDPA + EU AI Act).

## Conventions
- Compliance claims must cite the actual regulation; don't hand-wave "best practice".
- Distinguish Regent (policy/audit) from NeurX (host) clearly in every design.
