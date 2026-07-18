---
name: risk-management
description: Reference for trade risk discipline in a decision-support engine — position sizing from fixed-fractional risk, stop placement at structure/ATR invalidation, R:R and expectancy, leverage caps, no-counter-trend / stand-aside rules, short-squeeze caution. Use when defining stops/targets/sizing or a plan block, or reviewing whether a trade plan is survivable. Trigger on "position size", "stop loss / invalidation", "risk reward", "leverage", "how much to risk".
---

# risk-management

Turns a directional bias into a **survivable** trade plan. The first job of risk
management is to stay solvent through being wrong repeatedly — sizing and stops
come before targets. This skill is reference + checklist, not a predictor.

> Decision-support only — not investment advice.

## When to use

- Defining `plan` fields (entry/stop/targets/sizing) or invalidation levels.
- Reviewing whether a proposed trade is survivable (sizing vs account, R:R).
- Setting leverage / max-risk rules in engine config.
- NOT for indicator math (use `crypto-ta-math`) or signal weighting (signal spec).

## Core rules (locked defaults — make them config)

1. **Fixed-fractional risk per trade.** Risk a constant % of equity (default
   **1%**, aggressive cap **2%**). Never size by "conviction feeling".
2. **Stop = invalidation, not a round number.** The stop sits where the *thesis is
   wrong* (beyond a swing high/low + ATR buffer), not at an arbitrary % move.
3. **Position size is derived, never chosen:**
   ```
   risk_$       = equity × risk_pct
   stop_dist    = |entry − stop|
   position_qty = risk_$ / stop_dist
   notional     = position_qty × entry
   leverage     = notional / equity        # must be ≤ max_leverage
   ```
   If the required leverage exceeds the cap, the trade is **too big — reduce, don't
   widen the stop to fit.**
4. **R:R floor.** Skip trades with reward:risk below **1.5–2.0R**. `R = (target −
   entry)/(entry − stop)`. A high win-rate doesn't save a negative-expectancy book.
5. **No counter-trend trades** in the base engine (down-regime longs / up-regime
   shorts → stand-aside). Knife-catching is the #1 retail killer.
6. **Low conviction → stand-aside.** When confluence margin is thin or
   `confidence < floor`, the correct position size is **zero**.

## Stop / invalidation placement

- **Short:** stop above the most recent confirmed swing high + `atr_mult × ATR`
  (default 0.5). Confirm flips on **weekly close** above — avoids intrabar
  stop-hunt wicks.
- **Long:** stop below recent swing low − buffer; weekly-close confirmation below.
- **ATR floor:** if the structural stop is closer than `min_atr_dist × ATR`
  (default 1.0), widen to that — a too-tight stop guarantees noise-outs.
- **Volatility scaling:** in an expansion regime, widen buffers (×1.3) and *reduce
  size* (wider stop → smaller qty for the same risk_$).

## Expectancy (why a strategy is +EV)

```
E = (win_rate × avg_win) − (loss_rate × avg_loss)        # in R units
```
Positive expectancy needs either a win-rate edge or an R-multiple edge. Targets
should be set so avg_win ≥ ~2R; let winners run to the next structural level, cut
losers at invalidation. Track realized R per trade to validate the book.

## Crypto-specific caution

- **Short squeezes** spike hardest when everything is oversold and crowded-short —
  keep leverage low on shorts into oversold; size for the squeeze, not the thesis.
- **Funding / liquidation** on perps: leverage that survives a normal pullback can
  still liquidate on a wick. Size off the *liquidation distance*, not the stop.
- **Macro/flow regime** can override technicals (ETF flow, Fed) — when macro is the
  driver, haircut confidence and size down; technicals are subordinate.
- **24/7 market:** gaps are rare but weekend liquidity is thin — expect wider noise.

## Plan-review checklist

- [ ] Risk per trade ≤ configured % of equity?
- [ ] Stop at a real invalidation level (structure + ATR), not a round number?
- [ ] Position size *derived* from risk_$ / stop_dist (not chosen)?
- [ ] Implied leverage ≤ cap? Survives a wick to liquidation?
- [ ] R:R ≥ floor (≥1.5–2.0R)?
- [ ] With the trend (or explicitly stand-aside)?
- [ ] Conviction/confidence above floor (else size = 0)?
- [ ] Short into oversold? → extra squeeze haircut.
