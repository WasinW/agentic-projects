---
name: crypto-ta-math
description: Reference for the exact math behind technical-analysis indicators used in a trading engine — Wilder RSI/ATR (RMA), SMA/EMA, MA-stack classification, fractal pivots, HH-HL/LH-LL swing structure, support/resistance clustering, volatility regime. Use when implementing, verifying, or debugging TA indicator computation so values match TradingView. Trigger on "compute RSI/ATR", "why doesn't my indicator match TradingView", "pivot/swing detection", "S/R levels".
---

# crypto-ta-math

The precise, TradingView-compatible formulas for deterministic TA features. The
goal is **reproducibility**: the engine's numbers must equal what the user sees on
the chart. When in doubt, match `ta.*` semantics from Pine v6.

## When to use

- Implementing/verifying indicator math in a trading engine (RSI, ATR, MA, pivots, structure, S/R).
- A computed indicator disagrees with TradingView and you need the canonical definition.
- Designing golden-value unit tests for indicators.
- NOT for trade signals/weights (that's the signal spec) or risk sizing (use `risk-management`).

## The one gotcha: Wilder smoothing (RMA), not EMA/SMA

RSI and ATR use **Wilder's RMA**, seeded by an SMA, then a recursive smoothing.
`ewm(span=…)` (standard EMA) gives *close but wrong* values. Pine's `ta.rsi`/
`ta.atr` use RMA. Implement RMA explicitly:

```
RMA[period-1] = mean(x[0:period])                 # SMA seed
RMA[i]        = (RMA[i-1]*(period-1) + x[i]) / period
```

`ta.ema` ≡ `ewm(span=period, adjust=False)` with α = 2/(period+1). `ta.sma` ≡
simple rolling mean. Use these only for MAs, never for RSI/ATR.

## Formulas

### RSI (Wilder, period 14)
```
delta = close.diff().fillna(0)          # first bar: no prior close -> 0
gain  = max(delta, 0);  loss = max(-delta, 0)
avg_gain = RMA(gain, period);  avg_loss = RMA(loss, period)
RS  = avg_gain / avg_loss
RSI = 100 - 100/(1+RS)
```
Edge cases: `avg_loss==0` → RSI 100; `avg_gain==avg_loss==0` → 50. Need ≥ `period+~100`
bars for the seed to settle (early values drift vs TV until enough history).

### ATR (Wilder, period 14)
```
TR  = max(high-low, |high-prev_close|, |low-prev_close|)   # TR[0]=high-low
ATR = RMA(TR, period)
```

### MA stack (trend backbone)
Compute MA20/50/100 (EMA default). Classify the last bar:
- `close > MA20 > MA50 > MA100` → **bullish**
- `close < MA20 < MA50 < MA100` → **bearish**
- otherwise → **mixed**
Use a single anchor TF (e.g. 1d) — don't recompute trend on every TF or you
triple-count it (structure already carries the multi-TF read).

### Fractal pivots
A bar `i` is a **pivot high** if `high[i]` is the strict max over `[i-L, i+L]`
(L = lookback, default 3–5); symmetric for pivot lows. The last `L` bars are
**unconfirmed** (future bars could exceed) — never treat them as pivots.

### Swing structure (HH-HL / LH-LL)
From the last N confirmed pivots, compare the two most recent highs and two most
recent lows:
- higher-high AND higher-low → **HH/HL** (uptrend → long)
- lower-high AND lower-low → **LH/LL** (downtrend → short)
- anything else → **mixed**

### Support / Resistance
Pool = confirmed pivots (+ optional MA values as dynamic S/R). **Cluster** levels
within `cluster_atr_mult × ATR` (merge to mean) so you don't emit ten levels that
are really one zone. Split around current close, return **nearest-first**:
support = levels below price (highest first), resistance = above (lowest first).

### Volatility regime
`ATR_now` vs rolling median of ATR over `lookback` (≈100):
- `≥ 1.5 × median` → expansion · `≤ 0.7 × median` → contraction · else normal.
Use to widen invalidation buffers and gate range vs trend playbooks (it does not
vote directionally).

### Price overextension
`dist_atr = (close − MA20) / ATR`. Beyond ±2.5 ATR = stretched. Treat
overextension *above* as fade-risk; overextension *below* is **not** an auto-long
(oversold persists in downtrends — knife-catch guard).

## Verification discipline

- **Golden tests with hand-computed values** for RMA/RSI/ATR on tiny series
  (e.g. RSI period-2 on `[10,11,10,11]` → 71.4286 at the last bar).
- Bounds: RSI ∈ [0,100]; ATR ≥ 0; monotonic-up series → RSI 100.
- Cross-check the last value against TradingView on the same symbol/TF/period;
  small early-history drift is expected, late values should match closely.
- Always drop the **unclosed** candle before computing — an in-progress bar makes
  every indicator flicker.
