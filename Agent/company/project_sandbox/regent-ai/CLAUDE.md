# CLAUDE.md — regent-ai (KB context)

> **STATUS: PARKED as product 2026-07-18.** Regent is now a **practice + dogfood**, not a
> product build — see [`knowledge/adr-0001-park-as-product-2026-07-18.md`](knowledge/adr-0001-park-as-product-2026-07-18.md).
> Convert to (a) **career capital at AIA** (agent governance in a regulated insurer) and
> (b) a **weekend dogfood** = PreToolUse policy hook + hash-chained JSONL audit on Sin's own
> Claude Code agent fleet. **Build on Cedar/OPA — never invent a policy DSL** (novelty lives
> above: HITL thresholds, spend caps first-class, A2A handoff trust gates, cross-vendor
> provenance). **No product build** until the merged Track B project ("Agent Trust &
> Governance", NeurX folded in) has **≥1 external user AND Lumora Phase-1 revenue**.
> This is now the single Track B project; trust/provenance folded in from NeurX (killed),
> sovereign-deployment angle folded in from SentientNet (parked). Cap: ~4 hrs/month.

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

## Agents to consult — all COMMON (live in `roles/` + `~/.claude/agents`, shared by every project)
Lead: governance-consultant (PDPA, EU AI Act, BoT/SEC, model governance) ·
security-engineer (policy enforcement, audit, guardrails, zero-trust).
Support: ai-architect (safety + eval infra) · ai-engineer (guardrails — NeMo/Llama Guard,
eval — RAGAS/DeepEval) · solution-architect · software-engineer · business-analyst · investment-consultant.
> NOT this project's agents — shared consulting layer. Don't copy them here.

## This project's own assets (SPECIFIC — live in this folder)
- **Specific skills** (core IP) → `skills/`: `agent-policy-engine`, `audit-trail-design`
  (the policy engine + provenance/audit IS Regent's product).
- **Common skills** (in `~/.claude/skills`, reusable): `ai-regulation-knowledge`
  (PDPA + EU AI Act — to create); `dpia-assessment` (already exists).
- **Knowledge** → `knowledge/`: regulation notes, policy/audit patterns, HITL thresholds.

## Conventions
- Compliance claims must cite the actual regulation; don't hand-wave "best practice".
- Distinguish Regent (policy/audit) from NeurX (host) clearly in every design.
