# regent-ai — KB Index

> **STATUS: PARKED as product 2026-07-18** — now a practice + dogfood, not a product build.
> Decision: [`knowledge/adr-0001-park-as-product-2026-07-18.md`](knowledge/adr-0001-park-as-product-2026-07-18.md).
> This is the **single Track B project** ("Agent Trust & Governance"): NeurX (killed) folded
> its trust/provenance IP in here; SentientNet (parked) donated its sovereign-deployment angle.

Project-scoped knowledge base for **Regent AI** — Agent Governance & Trust Layer.
Track B (AI ecosystem vision). The policy/audit layer over NeurX.

- Code + docs: `~/Documents/Projects/Project/project_sandbox/regent-ai/`
- Master context: `…/projects-knowledge-base/01-projects-master-knowledge.md` §B2.

## Layout
```
regent-ai/
├── CLAUDE.md     ← how to work in this project
├── INDEX.md      ← this file
├── memory/       ← durable project facts
├── knowledge/    ← regulation notes, policy/audit patterns
└── skills/       ← project skill pointers (live in ~/.claude/skills)
```

## Status
**PARKED as product (2026-07-18)** → practice + dogfood. Old "model explainability + AI
ethics" vision deprecated. NeurX killed-as-registry and merged in; SentientNet parked, its
sovereign-deployment angle donated here. No product build until merged Track B has ≥1
external user AND Lumora Phase-1 revenue (ADR-0001).

## Knowledge files
- [`adr-0001-park-as-product-2026-07-18.md`](knowledge/adr-0001-park-as-product-2026-07-18.md) — park decision, dogfood, Cedar/OPA substrate, build gate.
- [`01-agent-governance-landscape.md`](knowledge/01-agent-governance-landscape.md) — landscape (Art.12 over-claim corrected); rots fast, re-scan before trusting.
- [`trust-provenance-from-neurx.md`](knowledge/trust-provenance-from-neurx.md) — trust/provenance IP inherited from NeurX.
- [`sovereign-deployment-angle.md`](knowledge/sovereign-deployment-angle.md) — sovereign-deployment feature inherited from SentientNet.

## Agents — all COMMON (consulted from `roles/`, none owned by this project)
Lead: governance-consultant, security-engineer.
Support: ai-architect, ai-engineer, solution-architect, software-engineer, business-analyst, investment-consultant.

## Skills
- **Specific** (core IP, → `skills/`): `agent-policy-engine`, `audit-trail-design` ✅ created (mirrored to ~/.claude/skills).
- **Common** (in `~/.claude/skills`, reusable): `ai-regulation-knowledge` (to create); `dpia-assessment` (exists).

## Knowledge to capture
EU AI Act · Thailand AI draft + PDPA · Singapore AI Verify · audit-trail / provenance
graph design · declarative policy-engine patterns · HITL checkpoint thresholds ·
the 3 angles (compliance-first SaaS / Thai-SEA-first / open-source policy engine).
