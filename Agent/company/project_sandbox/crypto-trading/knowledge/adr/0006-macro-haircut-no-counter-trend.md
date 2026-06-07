# 0006. Macro-flow confidence haircut + no-counter-trend / stand-aside

- Status: Accepted
- Date: 2026-06-07
- Deciders: Wasin + investment-consultant
- Tags: signals, risk, regime

## Context
doc/02 §5/§8: the current market is driven by macro / ETF flow more than
technicals. A purely technical bias would overstate confidence. Also, the #1
retail killer is counter-trend knife-catching and over-trading low-conviction setups.

## Decision
- **Macro haircut:** `confidence = max_score × macro_regime.factor`, where factor ∈
  {aligned 1.0, neutral 0.85, conflicting 0.65}. v1 default `neutral` (0.85). This
  is the single manual override knob in an otherwise deterministic Step 1; it
  encodes "technical subordinate to flow". A `caveats[]` entry is always emitted.
- **RSI oversold → neutral, never long** (and overextension-below → neutral):
  oversold persists in downtrends; no auto knife-catch.
- **No counter-trend trades / low-conviction → stand-aside** (decision table lives
  in the plan/LLM layer; the deterministic engine already refuses to vote long on
  oversold and haircuts thin-margin confidence).

## Consequences
- + Confidence reflects regime reality, not just chart geometry.
- + Encodes survivability bias into the engine, not just the human.
- − `macro_regime.active` is manual until an ETF-flow series automates it (future).
- Related: [0005](0005-confluence-formula-bias-derivation.md); skill `risk-management`.
