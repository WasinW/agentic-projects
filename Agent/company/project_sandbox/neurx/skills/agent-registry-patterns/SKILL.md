---
name: agent-registry-patterns
description: Design patterns for an AGENT registry (NeurX) — publish flow, Agent Card schema + validation, semver/compatibility across A2A protocol revisions, capability-based discovery + ranking, anti-spam curation, and trust (signed cards, provenance, rug-pull defense). Use when designing how agents get published, versioned, discovered, or trusted in NeurX. NOT for MCP-server registries (those are commodity) — this is the agent layer above. Trigger on "agent registry", "publish an agent", "Agent Card", "agent versioning/discovery", "registry trust/curation".
---

# agent-registry-patterns

NeurX-specific design reference. Common interop background (MCP vs A2A, Agent Cards,
the registry landscape) lives in the ai-architect/ai-engineer roles KB +
`neurx/knowledge/01-agent-registry-and-interop.md` — consult those first. This skill =
the *how to design the registry mechanics* part.

## When to use
Designing or reviewing any of NeurX's registry pillars: publish, version, discover, trust.

## Position (don't rebuild commodity)
The MCP-*server* registry is taken (official MCP registry ~9k+, Smithery 7k+, mcp.so).
NeurX's wedge = the *agent* (A2A) layer: register/version/rate whole agents (Agent Cards), not tools.

## The four mechanics
1. **Publish**
   - Validate the Agent Card (capabilities, endpoint, auth schema) against the A2A spec.
   - Namespace + ownership (who owns `@scope/agent`); capability attestation.
   - Reject cards that over-claim or lack a reachable endpoint.
2. **Version**
   - Semver for agents; declare the **A2A protocol revision range** each version supports.
   - Compatibility metadata so a consumer can pick a version that speaks its protocol.
   - Deprecation policy + migration notes (mirror the official MCP registry's "no breaking changes" stance).
3. **Discover + rank**
   - Search by **capability**, not just name. Trust/rating signals feed ranking.
   - Curation tiers (verified vs community) — LobeHub's 56k uncurated shows the failure mode.
4. **Trust**
   - **Signed Agent Cards** + provenance (who published, build origin).
   - **Rug-pull defense**: detect when a registered agent changes behavior after approval (the MCP lesson, applied to agents). Pin versions; re-attest on change.
   - Confused-deputy / capability-spoofing checks across vendors.

## Design checklist
- [ ] Agent Card schema + validator defined
- [ ] Namespace + ownership model
- [ ] Semver + protocol-revision compatibility
- [ ] Capability-based search + ranking signals
- [ ] Curation tiers (verified/community)
- [ ] Signed cards + provenance + rug-pull detection
- [ ] Deprecation + migration policy

## Consult
ai-architect (interop trade-offs), platform-architect (registry as platform: namespaces, multi-tenancy, golden paths), security-engineer (signing, trust).
