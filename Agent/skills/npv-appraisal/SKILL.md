---
name: npv-appraisal
description: Appraise whether an initiative is worth funding — compute NPV / IRR / payback (+ discounted payback), stress-test the 2-3 assumptions that swing it, compare against opportunity cost, and return a fund / stage-gate / don't verdict with kill criteria and a recommended funding shape. Use when deciding to fund (or kill) a project, build, hire, or platform investment.
---

# npv-appraisal

Runs a financial appraisal of an initiative and returns a defensible **fund / stage-gate / don't** verdict — with the math shown, the assumptions exposed, the sensitivity that could flip it, and the kill criteria. Treats optimistic benefits with suspicion.

## When to use

- Deciding whether to fund a project, platform, build-vs-buy, hire, or migration.
- Comparing competing initiatives for a limited budget.
- Someone asks "is this worth it?" / "what's the ROI?" — answer with the appraisal, not a gut call.

## Inputs (ASK for any that are missing BEFORE appraising)

- **Costs** — capex + opex, **fully-loaded** (people, cloud, licenses, run-cost, ramp). Phased over time.
- **Benefits + assumptions** — revenue uplift / cost saved / risk avoided, and the explicit assumptions behind each.
- **Time horizon** — appraisal window in years.
- **Discount rate** — the hurdle rate / WACC. **ASK if unknown** — don't silently assume.

## Steps

1. **Load investment + finance knowledge:**
   `mcp__agent-knowledge__search_knowledge(query="NPV IRR payback discounted cash flow hurdle rate sensitivity opportunity cost capital allocation", role_filter="investment-consultant", top_k=5)`
   and `mcp__agent-knowledge__search_knowledge(query="discount rate WACC cost benefit fully-loaded cost assumptions", role_filter="finance-consultant", top_k=5)`.
   Fallback if MCP is down: read those roles' `knowledge.md`.
2. **Confirm inputs** — if costs, benefits, horizon, or discount rate are missing/vague, ASK first.
3. **Build the cash-flow table** — net cash flow per period (benefits − costs), fully-loaded.
4. **Compute** — **NPV** (at the discount rate), **IRR**, simple **payback**, and **discounted payback**. Show the math and the table.
5. **Sensitivity / stress test** — identify the **2-3 assumptions that swing the verdict** (adoption %, benefit realization, ramp time, run-cost) and show NPV under pessimistic/base/optimistic.
6. **Opportunity cost** — compare vs the next-best use of the same capital/headcount and the do-nothing baseline.
7. **Verdict** — **fund** / **stage-gate** (fund a pilot to retire the key uncertainty) / **don't** — with the **kill criteria** and the **funding shape** (full / staged / pilot).
8. **Offer to record** as an ADR or business case for the decision trail.

## Guardrails / Notes

- **Don't trust optimistic benefits** — haircut soft/uplift benefits; demand the assumption behind every number.
- **Sunk cost is irrelevant** — only forward cash flows count; ignore what's already spent.
- **Flag garbage-in assumptions** — if a swing assumption is unsupported, say the verdict is unreliable until validated; that itself argues for a stage-gate.
- Show NPV in money and IRR vs the hurdle rate together — IRR alone misleads on scale.
- Be explicit about confidence and which inputs are confirmed vs assumed.
