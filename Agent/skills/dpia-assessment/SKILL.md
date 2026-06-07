---
name: dpia-assessment
description: Run a DPIA / PIA (Data Protection Impact Assessment) for a processing activity through a PDPA (Thailand) + GDPR lens — purpose & lawful basis, data flows incl. cross-border, necessity, risks to data subjects, mitigations, and a residual-risk verdict on whether a full DPIA is mandated. Use before standing up or changing a processing activity that touches personal data.
---

# dpia-assessment

Assesses a processing activity for privacy risk and produces a structured DPIA: what is being done, on what lawful basis, the risks to data subjects, the mitigations, and a clear verdict on whether a **full DPIA is required** and who must sign off. Thai PDPA first, GDPR as a parallel lens.

## When to use

- Standing up a new processing activity touching personal data, or materially changing one.
- New data sharing, a new vendor/processor, profiling, or any cross-border transfer.
- Someone asks "do we need a DPIA / PIA for this?" — answer with the assessment, not a yes/no.

## Inputs (ASK for any that are missing BEFORE assessing)

- **What data** — categories, including sensitive/special-category (health, religion, biometric, criminal).
- **Why** — the purpose(s) and the intended **lawful basis** (consent, contract, legitimate interest, legal obligation, vital interest).
- **Who** — data subjects, internal users, processors/sub-processors, recipients.
- **Where stored & retention** — systems, region, how long, deletion mechanism.
- **Sharing & cross-border** — who it's shared with, and any transfer outside Thailand/EEA + the safeguard.

## Steps

1. **Load governance knowledge:**
   `mcp__agent-knowledge__search_knowledge(query="DPIA PIA PDPA GDPR lawful basis cross-border transfer data subject risk", role_filter="governance-consultant", top_k=5)`.
   Fallback if MCP is down: read that role's `knowledge.md`.
2. **Confirm inputs** — if any above are unknown, ASK first. A DPIA on guessed flows is worthless.
3. **Purpose + lawful basis** — state each purpose and its lawful basis; flag consent that isn't freely given/specific, or legitimate-interest that needs a balancing test.
4. **Data inventory + flows** — map data → systems → recipients, including **cross-border** legs and their safeguard (adequacy, SCCs, consent, PDPA Sec. 28/29 basis).
5. **Necessity & proportionality** — is each data element needed for the purpose? Challenge over-collection and indefinite retention.
6. **Risks to data subjects** — likelihood × severity: re-identification, profiling harm, discrimination, breach exposure, function creep, loss of control.
7. **Mitigations** — data minimization, masking/pseudonymization, retention limits, access control, encryption, consent/notice, DSAR support.
8. **Residual-risk verdict** — after mitigations: Low / Medium / High. State whether a **full DPIA is required** and the sign-off needed (DPO / controller).

## Guardrails / Notes

- **Identify high-risk processing that MANDATES a DPIA** — large-scale sensitive data, systematic profiling with legal/significant effect, large-scale monitoring of public areas, new tech with high risk. Do not rubber-stamp.
- Flag **PDPA / BoT specifics** when relevant — Thai consent rules, sensitive-data Sec. 26, cross-border Sec. 28-29, and BoT data-governance expectations for financial data.
- Lawful basis is per-purpose — one activity can carry several; don't collapse them.
- Be explicit about confidence; mark each flow as confirmed vs assumed.
- A DPIA is living — note when re-assessment is triggered (new recipient, new purpose, new tech).
