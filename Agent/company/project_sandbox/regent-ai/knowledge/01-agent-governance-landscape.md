# Regent AI — Agent Governance Landscape (2026)

> **STATUS: PARKED as product 2026-07-18** — see `adr-0001-park-as-product-2026-07-18.md`.
> Regent is now a practice + dogfood (career capital at AIA + a PreToolUse policy hook +
> hash-chained JSONL audit on Sin's own agent fleet), not a product build. Trust/provenance
> folded in from NeurX (`trust-provenance-from-neurx.md`); sovereign-deployment angle folded
> in from SentientNet (`sovereign-deployment-angle.md`).
> **This landscape rots fast (<13 months) — re-scan before trusting any positioning claim.**
>
> Project-specific knowledge. **Common** regulation depth (EU AI Act risk tiers, GPAI
> obligations, PDPA, audit/lineage) lives in `roles/technical/consultant/governance-consultant`
> and guardrail tooling in `…/engineer/ai-engineer` + `…/security-engineer` — consult those.
> This file = the **agent-autonomy / liability** layer those don't cover. Researched 2026-06-27.

## 1. The gap Regent targets

Existing governance KB covers *model* compliance (AI Act, bias, model cards) and *content*
guardrails (input/output validation, PII, injection). The **unsolved** problem is one layer up:
**agent autonomy & liability** — what an autonomous agent is *allowed to do*, proven after the fact.

The 2026 stack converging in the market (validates Regent's four pillars):
- **Policy engine** — central repo of plans, permissions, contextual rules.
- **Runtime enforcer** — validates *every* request/tool-call against policy *before* execution (~200-300ms).
- **Audit + analytics** — captures all agent behavior; links agent ↔ user ↔ policy that permitted each action.

## 2. Where the market is (don't rebuild the table-stakes)

- **OpenAI Agents SDK**: strong on model input/output guardrails, **weak on tool-level governance**
  (which tool, by which agent, what permission) — that runtime+tool layer is the open space.
- **Guardrail vendors** (Galileo, Lakera, NeMo, Llama Guard): prompt/output safety, injection, PII.
- **OWASP Agentic Top 10** + **trust-gated handoffs**: emerging standard for multi-agent accountability.
- Regent's differentiation = **multi-agent provenance + declarative policy + HITL thresholds**, not yet-another output classifier.

## 3. Hard requirements that shape design

- **EU AI Act Art. 12 — record-keeping (log integrity):** Art. 12 requires high-risk AI
  systems to *automatically record events (logs) over their lifetime* and enable
  post-market monitoring (retention obligation in Art. 19). It does **not** literally name
  "hash-chaining", "signing", or "tamper-evident" as required techniques.
  **Hash-chained + signed append-only logs are a *defensible engineering interpretation*,
  not a literal mandate** — the tamper-evidence requirement is read into Art. 12 *together
  with Art. 15 (accuracy, robustness & cybersecurity)*, which requires resilience against
  unauthorised third parties altering the system's use, outputs or performance. So: logs
  must exist + be retained (Art. 12/19) and be integrity-protected (Art. 15); hash-chaining
  is *how we choose to satisfy that*, and it is a strong, buyer-credible interpretation —
  **not** "the regulation says a plain DB is illegal." Claiming the literal-mandate version
  to a compliance buyer loses credibility exactly where Regent needs it.
- **Provenance graph**: when 5 agents collaborate (incl. cross-vendor via A2A) and one fails, you must
  reconstruct *who asked what of whom*. Ties directly to the A2A task-lifecycle (see ai-architect KB).
- **HITL checkpoints**: approval gates at declared risk thresholds (spend caps, external-domain actions, irreversible ops).
- **Compliance mappings**: SOC 2 Type II, GDPR/PDPA, SOX, HIPAA — the audit schema should map to these from day one.

## 4. Open positioning (from master §B2)

Generic platform vs vertical (finance/health) · B2B SaaS vs open-core policy engine ·
separate product vs a governance layer *on* NeurX. Thai/SEA angle = PDPA + future Thai AI Act built-in.

## 5. Agents to consult
governance-consultant (regulation → controls, AI Act, PDPA) · security-engineer (enforcement,
hash-chained audit, zero-trust, OWASP Agentic) · ai-architect (safety/eval infra) ·
ai-engineer (guardrail impl — NeMo/Llama Guard, eval) · solution-architect · investment-consultant.

## Skills
`agent-policy-engine`, `audit-trail-design` **[specific → this project's `skills/`]** ·
`dpia-assessment` (common, exists).

## Sources
- [Tool-level governance guardrails — OpenAI Agents SDK issue #2515](https://github.com/openai/openai-agents-python/issues/2515)
- [AI Agent Governance Starts with Guardrails — Frontegg](https://frontegg.com/blog/ai-agent-governance-starts-with-guardrails)
- [AI agent governance tools compared, 2026 — DEV](https://dev.to/jagmarques/ai-agent-governance-tools-compared-2026-landscape-53hm)
- [awesome-ai-agent-governance](https://github.com/systempromptio/awesome-ai-agent-governance)
