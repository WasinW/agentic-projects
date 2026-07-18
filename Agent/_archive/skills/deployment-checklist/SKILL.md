---
name: deployment-checklist
description: Run pre-deployment readiness for an ML model going to production — offline validation gates, training-serving skew, rollout pattern, rollback, monitoring, registry/versioning, and an approval gate — ending in a go/no-go verdict plus the gaps to close. Use before promoting a model (batch, online, or streaming) to prod, or revisiting a stalled promotion.
---

# deployment-checklist

Walks an ML model through a concrete production-readiness checklist and returns a **go / no-go** plus the precise gaps blocking go. Covers the candidate-vs-current comparison and the serving mode's specific risks — not a generic checklist.

## When to use

- Promoting a trained model (or retrain) to production for the first time or as a refresh.
- A promotion is stalled and you need to know exactly what's missing.
- Someone asks "is this model ready to ship?" — answer with the checklist result, not a vibe.

## Inputs (ASK for any that are missing BEFORE assessing)

- **Model + use case** — what it predicts, the business decision it drives, the cost of a wrong prediction.
- **Serving mode** — batch / online (request-response) / streaming, and the latency + throughput SLA.
- **Current vs candidate** — is there an incumbent model? candidate's offline metrics vs the threshold + the incumbent.
- **Label timing** — are ground-truth labels immediate, delayed, or proxy-only?

## Steps

1. **Load ml-ops knowledge:**
   `mcp__agent-knowledge__search_knowledge(query="ML model production deployment readiness rollout shadow canary rollback monitoring drift training-serving skew", role_filter="ml-ops", top_k=5)`.
   Fallback if MCP is down: read that role's `knowledge.md`.
2. **Offline validation gates** — metrics vs threshold AND vs incumbent; **slice/segment** performance (not just aggregate); **fairness** across protected/key segments; data-quality + leakage check.
3. **Training-serving skew** — same features, same transforms, same source at serve time; check feature-store parity and point-in-time correctness.
4. **Rollout pattern** — pick + define: **shadow** (log, no serve) → **canary** (small %) → **champion-challenger / A-B** → **full**. State the promotion criteria per stage.
5. **Rollback plan** — one-command revert to incumbent, the trigger thresholds, and who pulls the lever.
6. **Monitoring wired** — operational (latency/error/throughput) + **drift** (input + prediction) + **performance with delayed labels** (proxy metrics until labels land) + **business KPI**. Confirm alerts route to an owner.
7. **Registry / versioning** — model + data + code + config versioned and reproducible; lineage from candidate back to training run.
8. **Approval gate** — required sign-off (model owner / risk / governance) recorded.
9. **Verdict** — **GO** or **NO-GO**, with the ranked gaps and what closes each.

## Guardrails / Notes

- Aggregate metric passing while a **key slice regresses** is a no-go — always check slices.
- Don't ship without a **rollback** and without **delayed-label** monitoring when labels lag — you'd be blind.
- Shadow/canary first for anything customer-facing or high-cost-of-error; don't jump to full.
- Be explicit about which gates are confirmed vs assumed; a "GO" on assumptions is a soft no-go.
- For regulated decisions, the fairness + governance sign-off is a hard gate, not optional.
