# NeurX — Agent Registry & Interop (landscape + design notes)

> **FROZEN 2026-07-18 — assume stale; re-scan before trusting any positioning.**
> NeurX was KILLED as a standalone registry on 2026-07-18 (see `adr-0001-kill-as-registry-2026-07-18.md`).
> The landscape below rots fast: AAIF/Linux Foundation registry consolidation, A2A v1.2 signed AgentCards,
> and hyperscaler marketplaces have already moved past this snapshot. Trust/provenance IP merged into Regent.
> Do NOT plan a registry from this file; treat every "the lane is open" claim as false until re-verified.

> Project-specific knowledge. **Common** interop background (MCP vs A2A) lives in
> `roles/technical/architect/ai-architect` + `…/engineer/ai-engineer` — consult those
> first, don't duplicate. This file = the registry/product-specific depth.
> Researched 2026-06-27.

## 1. The 2026 reality NeurX is entering

The "agent npm" wedge is **already partly taken at the MCP-server layer** — but
fragmented, and nobody owns the *agent* (not server) registry cleanly:

| Registry | Position (Q2 2026) | Note |
|---|---|---|
| **Official MCP Registry** | backbone; ~9.4k verified servers, Anthropic/GitHub/Microsoft | committed to no breaking API changes — build against it |
| **Smithery** | "Docker Hub of MCP", 7k+ servers, 430k+ devs/mo, hosted runtime | closest to the full registry+hosting play |
| **mcp.so / PulseMCP** | large discovery catalogs | curation + ranking differ |
| **LobeHub** | 56k+ by raw count | community-driven, low curation |

**Implication for positioning**: the MCP-*server* registry is crowded and Anthropic-backed.
NeurX's defensible wedge is **one layer up** — the *agent* (A2A) registry: discover/version/rate
whole agents (Agent Cards), not just tools. That layer is still open.

## 2. What's genuinely NeurX-specific (not in common roles)

The common KB now covers MCP, A2A, Agent Cards, multi-agent orchestration. NeurX's own IP is the
**registry mechanics** — the part no role-level knowledge should carry:

- **Publish flow**: Agent Card schema validation, capability attestation, ownership/namespace.
- **Versioning**: semver for agents, compatibility ranges across A2A protocol revisions, deprecation.
- **Discovery + ranking**: search by capability, trust/rating signals, anti-spam/curation (LobeHub's 56k shows what no-curation looks like).
- **Trust**: signed Agent Cards, provenance, "rug pull" defense (a server/agent changing behavior post-approval — the MCP lesson, applied to agents).
- **Runtime + observability** (pillars 3-4): serverless hosting of LangGraph/CrewAI agents; trace/replay across A2A task lifecycles.

## 3. Open positioning questions (from master §B1)

- Open-core + paid hosting vs closed SaaS?
- Global DX play vs Thai/SEA-first (PDPA-default) vs vertical?
- Does Lumora count as customer-zero (it needs agent infra)?
- Compete with Smithery on hosting, or sit above it as the agent (not server) layer?

## 4. Agents to consult
ai-architect (interop/registry trade-offs) · platform-architect (registry as platform-as-product:
namespaces, golden paths, multi-tenancy) · ai-engineer (A2A/MCP build) · security-engineer
(signed cards, trust) · devops-engineer (serverless runtime) · enterprise-architect / investment-consultant (positioning + funding).

## Sources
- [Official MCP Registry](https://registry.modelcontextprotocol.io/)
- [Best MCP Registries 2026 — TrueFoundry](https://www.truefoundry.com/blog/best-mcp-registries)
- [AI Agent Marketplace Landscape 2026 — Agensi](https://www.agensi.io/learn/ai-agent-marketplace-landscape-2026)
- [Linux Foundation — A2A 150+ orgs, 1-year milestone](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year)
