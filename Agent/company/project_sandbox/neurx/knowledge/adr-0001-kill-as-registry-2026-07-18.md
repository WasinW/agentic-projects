# 0001. Kill NeurX as a standalone agent registry; merge trust/provenance IP into Regent

- Status: Accepted
- Date: 2026-07-18
- Deciders: Sin (Wasin) + portfolio-review-20260718 (portfolio-vc · chief-architect · market-skeptic lenses)
- Tags: strategy, kill-decision, agent-registry, trust, positioning
- Supersedes: the "four-pillar agent infrastructure" framing in `CLAUDE.md` / `INDEX.md` / master §B1

## Context

NeurX was the Track B "npm of agents" bet: a neutral agent (A2A) registry with four pillars
— **Registry** (publish/discover/version), **Interop** (MCP/A2A), **Runtime** (serverless host of
LangGraph/CrewAI), **Observability** (trace/replay). After ~1 year the artifact ledger is
**0 code, 0 schemas, 0 prototypes** — ~200 lines of prose in two places, one landscape note, and one
skill (`agent-registry-patterns`). The forces that make this a KILL, not a park:

1. **The neutral-registry window is closing from above.** The Linux Foundation **AAIF** (Agents &
   Agentic AI Foundation — OpenAI, Anthropic, Google, Microsoft, AWS, Block) is consolidating the
   registry layer under a foundation. A neutral third party does not get to own a layer this strategic
   once the hyperscalers agree to share it.
2. **A2A v1.2 absorbed the last defensible wedge into the spec.** The one pillar that was genuinely
   defensible was **trust** (signed cards, provenance, rug-pull defense). A2A v1.2 now ships **signed
   AgentCards** natively — the protocol is pulling card-signing/trust into itself. Building a product on
   "we sign the cards" competes with the spec, not on top of it.
3. **Distribution is already owned by hyperscaler marketplaces.** Microsoft Marketplace (4,000+ agents,
   3% fee), Gemini Enterprise, an AWS agent category, AgentExchange; and the dev registry layer is dense
   — official MCP Registry, Smithery (430K devs/mo), Solo.io shipping an enterprise Agent Registry
   (Jul 2026). There is no empty shelf.
4. **Two-sided cold-start is unwinnable solo, part-time, unfunded.** A registry needs publishers and
   consumers simultaneously; bootstrapping both against foundation gravity is a full-time, funded effort.
   Even the winners monetize poorly (npm survived by acquisition; Docker Hub dragged a decade).
5. **The customer-zero logic was wrong.** Lumora does not need a *registry*; it needs internal
   orchestration + policy/guardrails/audit. That makes Lumora the customer-zero of **Regent**, not NeurX.
6. **Trust overlaps ~80% with Regent.** Signed provenance, rug-pull/behavior-change detection, and
   cross-vendor confused-deputy defense are the same primitives as Regent's audit-trail + policy work.
   NeurX and Regent were one system pretending to be two projects, splitting the same scarce evening hours.

Owner reality: full-time Senior DE at AIA (started 2026-07-01), 6–10 hrs/week of side capacity this
quarter. A "parked" registry is a proven liability in this system — SentientNet consumed narrative and
planning cycles for a year at 0 LOC. A dead-but-soft-parked project keeps re-inviting build sessions.

## Options considered

- **Kill as standalone registry; merge trust/provenance IP into Regent (chosen)** —
  Ends the two-sided cold-start bet permanently; consolidates the one surviving pillar (trust) where it
  already lives 80% (Regent). Cost: formally closes a vision Sin liked. Upside: one Track B project instead
  of two competing for the same hours; a hard record that stops the idea haunting future sessions.
- **Soft park the registry ("gated behind Lumora revenue")** — rejected. The landscape that killed it
  (AAIF + A2A v1.2 signed cards + Solo.io shipping) will not reopen for a solo builder, so "parked" here
  means "an unmaintained, decaying plan that re-triggers build talk." A dead thing stated clearly is
  cheaper than a dead thing left ambiguous.
- **Narrow to a trust-only product (sign/verify AgentCards as a service)** — rejected as a *NeurX* product,
  because A2A v1.2 is native-signing the cards. Kept only as an optional throwaway probe (see Consequences),
  and only as *Regent* IP if it survives.
- **Keep Runtime + Observability pillars, defer them** — rejected. Each is a company-scale undertaking
  (Runtime alone is Bedrock-AgentCore-class). Cut permanently, not deferred; unbounded scope is why nothing
  was ever built.

## Decision

**Kill NeurX as a standalone agent registry.** Do not build the four pillars. Runtime and Observability are
cut **permanently** (not deferred). The **trust / provenance IP** — signed-card verification, provenance
graph, rug-pull / behavior-change detection, cross-vendor confused-deputy defense — **merges into Regent**
(the single Track B "Agent Trust & Governance" project) where it overlaps ~80% with the policy + audit-trail
work already scoped there. The `agent-registry-patterns` skill is retained as a *design-reference artifact
only* (map of registry mechanics), not as a product roadmap.

### The four open positioning questions — answered now, so they stop reopening

These were copied across three files for a year without a decision. Decided here, on record:

1. **Open-core + paid hosting vs closed SaaS?** → **Open-source tooling posture.** Anything that survives
   (e.g. a card-verify probe) ships as open-source tooling / a CLI, never a hosted closed-SaaS registry.
   There is no hosting business to defend against the foundation.
2. **Global DX vs Thai/SEA-first vs vertical?** → **Global DX first**, *if it were ever revived* — the
   registry problem is a global developer-experience problem, not a PDPA-locality one. (The Thai/SEA-first
   angle belongs to Regent's compliance play, not to a registry.)
3. **Does Lumora count as customer-zero?** → **No. Lumora is Regent's customer-zero, not NeurX's.** Lumora
   needs internal orchestration + policy/guardrails/audit, which is Regent's surface. If Lumora ever needs
   agent infra, build it as **Lumora-internal plumbing**, never as a platform extracted from one customer.
4. **Compete with Smithery on hosting, or sit above it?** → **Sit above the official registries (Smithery,
   official MCP Registry) at the agent/trust layer — never compete on server hosting.** And per this ADR,
   even that "sit above" layer is being absorbed by AAIF + A2A v1.2, so the answer is moot for a standalone
   product; it survives only as the trust primitives folded into Regent.

## Consequences

- **Positive**
  - Track B collapses from two vision projects to one (Regent), ending the evening-hours cannibalization.
  - The surviving, defensible primitive (trust/provenance) lands where it has 80% overlap and a real
    customer-zero (Lumora → Regent), instead of stranded under a registry that can't cold-start.
  - The four open questions are closed on record; future sessions can't relitigate NeurX positioning.
  - Removes a "motion-feeling without information-gain" scaffold from the portfolio (per market-contact rule).

- **Negative / cost**
  - Formally ends a vision the owner was attached to; no neutral-registry optionality remains.
  - The `01-agent-registry-and-interop.md` landscape note is now FROZEN and must be treated as stale.
  - Any future trust product does **not** inherit this thesis — it is a fresh underwrite (see below).

- **Follow-ups**
  - Update `CLAUDE.md`, `INDEX.md`, and `README.md` status → **KILLED-as-registry 2026-07-18**, pointing to
    Regent + this ADR. (done in this change.)
  - Stamp `knowledge/01-agent-registry-and-interop.md` **FROZEN 2026-07-18 — assume stale; re-scan before
    trusting any positioning.** (done in this change.)
  - Merge trust/provenance IP into Regent's KB (`regent-ai/knowledge/`) — owned by the Regent workstream,
    **not touched by this ADR** (separate owner). This ADR is the hand-off record.
  - Optional throwaway probe (only if the itch is real, ≤1 weekend, zero infra): a CLI
    `neurx-card validate|sign|verify` over A2A cards. If nobody cares, the trust thesis is killed cheaply
    too. Any survivor becomes **Regent** IP, not a revived NeurX.

## Un-kill condition

**Essentially none as a registry.** This is a KILL, not a park — there is no revenue gate or landscape
event that reopens "NeurX the neutral agent registry." A future *trust / provenance* product is permitted,
but only as a **brand-new underwrite from a fresh landscape scan** (AAIF state, A2A spec version, whether
the foundations left a trust gap open) — carrying **none** of NeurX's inherited positioning, scope, or
customer-zero assumptions. If that ever happens, it is Regent IP by default, and it starts at a new ADR,
not a resurrection of this one.

## Related
- `../../projects-knowledge-base/portfolio-review-20260718.md` §3.4 (verdict source) and §5 item 2 (KILL-vs-park ruling).
- `../../regent-ai/` — the merged Track B "Agent Trust & Governance" project (trust/provenance IP lands here).
- `knowledge/01-agent-registry-and-interop.md` — FROZEN landscape note (2026-07-18).
- `../../projects-knowledge-base/01-projects-master-knowledge.md` §B1 (superseded framing).
