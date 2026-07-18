# Trust & Provenance IP — inherited from NeurX

> **Origin:** NeurX was KILLED as a standalone agent registry (2026-07-18). Its one
> defensible pillar — **trust/provenance** — overlaps ~80% with Regent, so it is folded
> in here. This file is the merged home; do not re-open NeurX to act on it.
> Registry mechanics (publish/version/discover) are dead — kept out on purpose.
> Source: NeurX `knowledge/01-agent-registry-and-interop.md` §2 + `skills/agent-registry-patterns`.

## Why this belongs in Regent

Each hyperscaler verifies trust only inside its own walled garden. The open, defensible
problem is **cross-vendor trust + provenance** — exactly Regent's one remaining open pillar
(multi-agent provenance across vendors over A2A). NeurX framed it as "who do you trust to
publish an agent"; Regent reframes it as "who is accountable when N agents — some
cross-vendor — collaborate and one fails." Same primitives, better wedge.

## The trust primitives Regent inherits

- **Signed Agent Cards + provenance.** Verify who published/built an agent and that its
  declared card is authentic (signature over the A2A Agent Card). Provenance = who
  published, build origin, chain of custody. This is the identity anchor every audit
  record and handoff trust gate hangs off.
- **Rug-pull defense.** Detect when a registered/known agent **changes behavior after it
  was trusted** (the MCP lesson applied to agents). Pin versions; **re-attest on change**;
  alert on drift from the attested capability set. In Regent this becomes a runtime policy
  input, not a registry gate.
- **Confused-deputy / capability-spoofing checks across vendors.** An agent must not be
  able to borrow another's authority or claim capabilities it can't back. Verify the
  caller's identity + granted scope at every A2A handoff, not just at registration.
- **Capability attestation.** An agent asserts what it can do; the trust layer checks the
  assertion is backed (reachable endpoint, signed card, matching declared capabilities)
  before another agent is allowed to delegate to it.

## How each maps onto Regent's pillars

| NeurX trust primitive | Regent home | Concrete use |
|---|---|---|
| Signed Agent Card + provenance | Audit / provenance graph | node identity in the provenance graph; every audit record links to a signed identity |
| Rug-pull / re-attest on change | Policy engine (runtime input) | policy denies handoff to an agent whose attestation drifted |
| Confused-deputy / capability-spoofing | Policy engine — **A2A handoff trust gates** | verify caller identity + scope at the delegation boundary |
| Capability attestation | HITL + handoff gates | escalate to human when a delegate can't attest to a required capability |

## What is explicitly NOT inherited (stays dead with NeurX)

- Publish flow, namespace/ownership, semver + protocol-revision compatibility ranges,
  capability-based **discovery/search + ranking**, curation tiers. These are *registry*
  mechanics — dead. Regent is not a registry. If a future trust product ever needs a
  directory, that is a **new underwrite**, not a resurrection of NeurX.

## Note on substrate

Signing/verification uses standard crypto + identity (do not invent). The A2A handoff
trust gates and cross-vendor provenance are where Regent's novelty lives — see
`adr-0001-park-as-product-2026-07-18.md` (build on Cedar/OPA, novelty above the substrate).

## Consult
security-engineer (signing, key mgmt, confused-deputy), ai-architect (A2A task lifecycle),
governance-consultant (what "trusted provenance" must satisfy for an auditor).
