# NeurX

> **STATUS: KILLED-as-registry 2026-07-18.** Not an active project. See the formal decision:
> `~/Documents/Projects/Agent/company/project_sandbox/neurx/knowledge/adr-0001-kill-as-registry-2026-07-18.md`.

## Why killed (5 lines)

1. AAIF / Linux Foundation is consolidating the agent-registry layer — a neutral third party won't own it.
2. A2A v1.2 ships signed AgentCards natively, absorbing the one defensible wedge (trust) into the spec.
3. Hyperscaler marketplaces (Microsoft, Gemini, AWS) + dense dev registries (Smithery, official MCP) own distribution.
4. Two-sided registry cold-start is unwinnable solo, part-time, unfunded against foundation gravity.
5. The surviving primitive is trust/provenance — it overlaps ~80% with **Regent**, so it merged there. Lumora = Regent's customer-zero, not NeurX's. KILL, not park: any future trust product is a NEW underwrite.

> Agent Infrastructure & Registry — the "npm of agents": registry, interop (MCP/A2A),
> serverless runtime, observability. Track B (AI ecosystem vision). The base layer.
> **[FROZEN historical context below — do not act on it.]**

- **KB / agent context**: `~/Documents/Projects/Agent/company/project_sandbox/neurx/`
- **Master portfolio doc**: `../projects-knowledge-base/01-projects-master-knowledge.md` (§B1)
- **Mode**: architect + product-strategist, agentic-era. **Agent-centric, NOT model-centric.**

## Reality check
Old "AI model marketplace" vision is dead (HF/Replicate/OpenRouter own it).
Gated behind Lumora Phase-1 revenue. Clarify the wedge before building.

## Layout
```
neurx/
└── doc/    ← architecture, positioning, protocol notes
```
