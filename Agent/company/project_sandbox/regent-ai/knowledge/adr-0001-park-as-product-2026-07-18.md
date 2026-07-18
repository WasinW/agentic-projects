# ADR-0001 — Park Regent as a product; convert to career capital + a dogfood

- **Status:** Accepted
- **Date:** 2026-07-18
- **Deciders:** Sin (owner)
- **Context source:** portfolio-review-20260718.md §3.5, §2.3, Appendix #3
- **Supersedes framing in:** master §B2 ("compliance-first governance SaaS" as a near-term build)

## Context

Regent's thesis is right and early — the unsolved problem is **agent autonomy &
liability**, and the market is converging on the exact 3-part stack the KB describes
(policy engine → runtime enforcer → tamper-evident audit + provenance). But as a
*product* for a solo, part-time founder it is not viable on the current horizon:

- **Vendor-risk is a locked door, not a hard sell.** The buyers who actually need this
  (regulated enterprises facing EU AI Act enforcement from 2026-08-02) cannot procure
  from a solo, unaudited vendor — they require the vendor's own SOC 2, references, SLAs,
  vendor-risk review. No GTM effort clears that door for a one-person shop.
- **Commodity floor is already high.** Microsoft's free agent-governance OSS toolkit
  covers OWASP Agentic 10/10 with sub-ms policy eval. Identity incumbents (Entra Agent
  ID GA 2026-04, Okta for AI Agents, AgentCore Identity) own the enforcement point.
  Pillars 1–2 (policy + audit) are becoming **table stakes you compose, not build**.
- **The one open pillar** is multi-agent provenance **across vendors** (A2A) — narrow,
  and not enough to hang a company on for a solo.
- **Triple-stacked dependency** (Regent ← NeurX ← Lumora revenue) makes P(product) ≈ 0
  on any timeline Sin can act on. Regent is at 0 LOC while the window closes.

The angles that survive today are **customer-zero/internal** and **career capital at
AIA** (free, real, now). Standalone global product is not viable while the window closes.

## Decision

**Park Regent as a product.** Do not build a Regent product. Instead convert the
accumulated thesis + skills into two things that pay off immediately at ~0 cost:

### (a) Career capital at AIA — agent governance inside a regulated insurer
Redirect all compliance/governance depth to AIA now. AIA is a regulated insurer that
*will* face real agent-governance questions (audit, policy, HITL, PDPA/BoT/SEC). Position
Sin as the person who understands agent audit + policy enforcement in that context. Build
cost = 0; it monetizes as role/credibility today, not as a future SaaS.

### (b) Weekend dogfood on Sin's own Claude Code agent fleet
Build, on Sin's own agents, the smallest real version of Regent:
- **PreToolUse policy hook** = the runtime enforcement point. Claude Code's PreToolUse
  hook *is* the tool-call boundary the KB says incumbents are weak at. Enforce a
  permission matrix (agent × tool × scope), spend/rate caps, and HITL thresholds there.
- **Hash-chained JSONL audit** of every tool call on the fleet, with a `verify` command
  that walks the chain. This is real protection for Lumora's content agents *and* a live
  Regent demo, and it pressure-tests the two skills — turning notes into IP.

### Policy substrate — build on Cedar or OPA, NEVER invent a DSL
When (b) needs a policy language, **adopt Cedar (or OPA/Rego)** as the substrate. Do not
invent a policy DSL — that is the classic mistake, and both already dominate MCP/agent
authorization in 2026. **Regent's novelty lives strictly above the substrate:**
- **HITL approval thresholds** as first-class policy objects (risk tier → human gate).
- **Spend caps first-class** (per-agent / per-task budget as a native policy primitive).
- **A2A handoff trust gates** (trust-gated agent→agent delegation, incl. cross-vendor).
- **Cross-vendor provenance** (the one genuinely open pillar) — the provenance graph over
  A2A task lifecycles.

If Cedar/OPA can express a rule, use it; only the four items above justify new code.

### Product build gate (locked)
**No Regent product build** until BOTH hold:
1. The merged Track B project ("Agent Trust & Governance", NeurX folded in) has **≥1
   external user**, AND
2. **Lumora Phase-1 revenue** exists.

Until then Regent is a practice + a dogfood, capped at ~4 hrs/month (portfolio Priority 3).

## Consequences

- **Positive:** ~0 build cost; the dogfood gives real protection to Lumora agents and a
  demo simultaneously; AIA turns the KB into career capital *now*; skills get validated by
  use, not just written; no evening hours sunk into a product whose window is closing.
- **Negative / accepted:** Regent-as-a-company is deferred indefinitely (correct — the
  window is closing for solo greenfield anyway); the "governance SaaS" narrative in master
  §B2 must stop implying a near-term build.
- **When to revisit:** at the product-build gate above, and only after a **fresh landscape
  re-scan** (this KB rots in <13 months — see the Art.12 fix and the incumbent list above).
- **Thai AI Act = tracked option, not a build:** when the law lands, be first to publish a
  Thai-language mapping (content/consulting play, not SaaS).

## Related
- `01-agent-governance-landscape.md` — landscape (Art.12 over-claim corrected).
- `trust-provenance-from-neurx.md` — trust/provenance IP folded in from NeurX.
- `sovereign-deployment-angle.md` — sovereign-deployment feature folded in from SentientNet.
- `skills/agent-policy-engine`, `skills/audit-trail-design` — the two IP skills the dogfood validates.
