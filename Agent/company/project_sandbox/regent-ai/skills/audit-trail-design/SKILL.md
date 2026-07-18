---
name: audit-trail-design
description: Design a tamper-evident audit trail + provenance graph for autonomous/multi-agent systems (Regent AI) — signed, hash-chained append-only logs (a defensible EU AI Act Art.12/15 log-integrity interpretation, NOT a literal mandate), per-action records linking agent↔user↔policy, and a provenance graph to reconstruct who-asked-what-of-whom when multiple (incl. cross-vendor A2A) agents collaborate. Use when designing how agent behavior is logged for audit, replay, or compliance. Trigger on "audit trail", "tamper-evident logging", "provenance", "agent replay", "who did what", "EU AI Act Article 12".
---

# audit-trail-design

Regent-specific reference for the **audit/provenance** pillar. Background:
`regent-ai/knowledge/01-agent-governance-landscape.md`. Regulation depth (EU AI Act,
PDPA, retention) is in governance-consultant — consult it; this is the agent-replay design.

## When to use
Designing how every agent action is recorded so it can be audited, replayed, and proven compliant.

## Log integrity — a defensible interpretation, cite it precisely
**Do not over-claim the regulation.** EU AI Act **Art. 12 (record-keeping)** requires
high-risk AI to *automatically record events (logs) over the system's lifetime* and support
post-market monitoring; **Art. 19** requires those logs be **retained**. Neither article
literally names "hash-chaining", "signing", or "tamper-evident". The integrity requirement
is read in *together with* **Art. 15 (accuracy, robustness & cybersecurity)** — resilience
against unauthorised alteration of the system's use/outputs/performance.

So the honest claim is: **logs must exist + be retained (Art. 12/19) and be
integrity-protected (Art. 15); hash-chaining + signing is a strong, buyer-credible
engineering interpretation to satisfy that — NOT a literal textual mandate.** Never tell a
compliance buyer "a plain DB is illegal under Art. 12" — it's an over-claim that costs
credibility. Recommended design:
- **Append-only** + **hash-chained** records (each entry hashes the previous → any edit breaks the chain).
- **Signed** entries (cryptographic signature on write).
- Optionally anchor periodic chain digests externally for stronger non-repudiation.

## What each record must link
Every agent action (request → decision → tool call → output) logs the triple:
**agent ↔ user (on whose behalf) ↔ policy that permitted it** (from `agent-policy-engine`).
Plus: inputs, tool + args, result, timestamp, A2A task id (if cross-agent), risk tier, HITL approval ref (if any).

## Provenance graph (multi-agent)
When N agents collaborate — including cross-vendor over A2A — a flat log isn't enough. Build a **graph**: nodes = agents/tasks, edges = delegations ("agent X asked Y to do Z"). On failure you must answer *who is responsible* and reconstruct the full chain. Tie node ids to A2A task lifecycle states (submitted→working→completed/failed).

## Compliance mapping
Design the schema to map to **SOC 2 Type II, GDPR/PDPA, SOX, HIPAA** from day one — auditors want the linkage agent→action→authorization, retained per policy.

## Checklist
- [ ] Append-only + hash-chained store
- [ ] Signed entries
- [ ] Per-action agent↔user↔policy linkage
- [ ] A2A task id + provenance graph for multi-agent
- [ ] Replay capability (reconstruct a run end-to-end)
- [ ] Retention + compliance mappings (SOC2/PDPA/GDPR/SOX/HIPAA)
- [ ] HITL approval references captured

## Consult
governance-consultant (Art.12, retention, PDPA), security-engineer (signing, hash-chain, key mgmt), ai-architect (replay infra).
