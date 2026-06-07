# SPEC — Signal & Trading-Logic Engine (Step 1 Deterministic)

> Authored by business/investment role, 2026-06-07. Conforms to the LOCKED §6
> contract + contract-locks in doc/02 and the project ADRs.
> **Scope:** deterministic signal computation → confluence scoring → bias →
> playbook selection → invalidation. Produces the code-owned fields of §6
> (`regime`, `levels`, `signals[]`, `confluence_score`, deterministic seed of
> `bias` / `plan.playbook`). Elliott, summaries, plan prose = LLM layer (§6 here).

---

## 0. Conventions & config principle

- **Every number below is a tunable default** from a single config file. Code
  reads config; no magic numbers inline. Spec values = v1 defaults.
- TFs v1: `1h`, `4h`, `1d`. 1w/1m later — config-driven.
- A **signal** = `{ name, value, vote, weight }`. `vote ∈ {long, short, neutral}`.
  `value` = raw/descriptive reading (number or label), carried for transparency.
- **Macro caveat surfaces in 3 places**: (a) a `confidence` haircut after
  confluence; (b) auto-injected `caveats[]` entry; (c) playbook downgrade to
  `stand-aside` when confluence is weak. See §3.4 and §4.

---

## 1. signals[] — the deterministic set

Computed per TF where noted. Each signal emits exactly one vote. If inputs are
insufficient (not enough bars), the signal is **ABSENT** (omitted from
`signals[]`, not voted neutral) so the confluence denominator self-adjusts.

### 1.1 `rsi_<tf>` — momentum / exhaustion (secondary)
- Wilder RSI(14) on closes, per TF. Inputs: ≥ `rsi_period + 100` bars.
- Vote (config `rsi`):
  - RSI ≥ `overbought` (70) → **short**
  - RSI ≤ `oversold` (30) → **neutral** (NOT long)
  - else → **neutral**
- **oversold ≠ long:** in a downtrend oversold persists; long here = knife-catch.
  Matches §6 sample (`rsi_1d 28 → neutral`). Divergence-long is v2, gated behind
  structure confirmation. Do NOT implement naive oversold→long.
- value: integer RSI.

### 1.2 `ma_stack` — trend backbone (PRIMARY)
- Ordering of price vs MA20/50/100, on anchor TF (default `1d`, config
  `ma_stack.anchor_tf`). Type EMA (config), periods `[20,50,100]`.
- Vote:
  - `close > MA20 > MA50 > MA100` → **long** (`"bullish"`)
  - `close < MA20 < MA50 < MA100` → **short** (`"bearish"`)
  - else → **neutral** (`"mixed"`)
- Anchor-TF only to avoid triple-counting trend across TFs.

### 1.3 `structure_<tf>` — swing structure HH-HL / LH-LL (PRIMARY)
- Confirmed swing highs/lows → trend structure, per TF.
- Swing detection: fractal pivot, `pivot_lookback` bars each side (default 3);
  use last `swing_count` confirmed pivots (default 4).
- Vote:
  - HH AND HL → **long** (`"HH/HL"`)
  - LH AND LL → **short** (`"LH/LL"`)
  - mixed / insufficient → **neutral** (`"mixed"`)
- Single highest-weighted signal type (see §2).

### 1.4 `candle_pattern_<tf>` — reversal/continuation (secondary)
- Pattern on last closed bar of TF (default `1d`, config `candle.tf`).
- Set: bullish/bearish engulfing, hammer, shooting star, doji(neutral). Each
  requires **context filter**: within `candle.context_atr` × ATR of nearest swing
  (default 0.5) — mid-range pattern = noise.
- Vote: bullish engulfing/hammer at support → **long**; bearish engulfing/
  shooting star at resistance → **short**; doji / no-context / none → **neutral**.
- value: pattern name or `"none"`. Lowest deterministic weight.

### 1.5 `vol_regime` — ATR volatility regime (RECOMMENDED ADD)
- ATR(14) vs rolling median (`vol_regime.lookback`, default 100), anchor `1d`.
- **Does NOT vote directionally — always `neutral`, weight 0**, excluded from the
  confluence denominator. value:
  - ATR ≥ `expansion_mult`×median (1.5) → `"expansion"`
  - ATR ≤ `contraction_mult`×median (0.7) → `"contraction"`
  - else → `"normal"`
- Feeds: ATR-multiple invalidation width (§5), range-fade vs trend-follow split
  (§4), LLM sizing note. Include in `signals[]` for transparency, weight 0.

### 1.6 `price_vs_ma_dist` — overextension (RECOMMENDED ADD, secondary)
- `dist_atr = (close − MA20) / ATR(14)`, anchor `1d`.
- Vote (config `price_dist`):
  - `dist_atr ≥ +stretch` (+2.5) → **short** (overextended above)
  - `dist_atr ≤ −stretch` (−2.5) → **neutral** (not long — knife-catch)
  - else → **neutral**
- Asymmetry intentional, matches §8 macro-down regime: fade froth, don't buy
  capitulation blindly.

**Roster v1:** `rsi_1h`, `rsi_4h`, `rsi_1d`, `ma_stack`, `structure_1h`,
`structure_4h`, `structure_1d`, `candle_pattern_1d`, `vol_regime` (w=0),
`price_vs_ma_dist`. Elliott absent in v1.

---

## 2. Weights (defaults — tunable, sum-normalized)

Weights are relative; confluence normalizes by sum of PRESENT weights.

| signal | weight | rationale |
|---|---|---|
| `structure_1d` | 0.22 | Higher-TF swing structure = truest trend read. |
| `structure_4h` | 0.16 | Tactical structure; confirms/leads 1d. |
| `structure_1h` | 0.06 | Noisy entry-timing read; light. |
| `ma_stack` | 0.20 | Trend backbone; low false-signal rate. |
| `price_vs_ma_dist` | 0.08 | Overextension guardrail. |
| `rsi_1d` | 0.09 | Momentum/exhaustion; higher TF more weight. |
| `rsi_4h` | 0.06 | Secondary momentum. |
| `rsi_1h` | 0.03 | Lowest-trust momentum. |
| `candle_pattern_1d` | 0.10 | Reversal trigger but noisy. |
| `vol_regime` | 0.00 | Context only; excluded from denominator. |
| *`elliott_1d` (v2)* | *0.05* | Lowest trust, supporting view (§6). |

Primary block (structure+MA+dist) ≈ 0.72 → satisfies §5. Levels are not a voting
signal; they enter via invalidation (§5) + playbook entry zones (§4).
Engine sum-normalizes over PRESENT signals at runtime — never hardcode normalized.

---

## 3. Confluence scoring

### 3.1 Locked formula
```
score[vote] = Σ(weight_i where signal_i.vote == vote) / Σ(weight_j of present, counted signals)
```
Denominator = present, counted signals only (`vol_regime` w0 + absent signals
excluded). `neutral` is its own bucket. Three scores sum to 1.0.

### 3.2 bias derivation
- `bias.direction = argmax(score)`.
- `margin = max_score − second_highest`.
- `conviction`: margin<0.15→low; 0.15–0.35→medium; >0.35→high.
- `timeframe_alignment`: per-TF read from `structure_<tf>` votes (1h/4h/1d).

### 3.3 Worked example (§8 down-regime)
Votes: structure_1d/4h short, structure_1h neutral, ma_stack short,
price_vs_ma_dist neutral, rsi_1d/4h/1h neutral, candle_pattern_1d neutral.
Denominator = 1.00 (vol_regime excluded, elliott absent).
- short = 0.22+0.16+0.20 = 0.58; neutral = 0.42; long = 0.00.
- `confluence_score = {long:0.00, short:0.58, neutral:0.42}`.
- argmax → **short**; margin 0.16 → **medium**; alignment `{1h:neutral,4h:short,1d:short}`.

### 3.4 Macro-flow confidence haircut (caveat surface #1)
```
confidence = max_score × macro_alignment_factor
```
`macro_regime` config enum: `{aligned:1.0, neutral:0.85, conflicting:0.65}`,
v1 default `neutral`. Always append caveat: `"technical subordinate to macro/ETF
flow — confidence haircut applied"` (surface #2).

---

## 4. Playbook → plan mapping (deterministic decision table)

Inputs: `regime.trend` (up|down|range from ma_stack + structure_1d),
`bias.direction`, `bias.conviction`, `vol_regime.value`. Output: `plan.playbook`
+ entry-zone source. (LLM writes prose/targets later.)

Trend: `up` if ma_stack bullish AND structure_1d long; `down` if bearish AND
short; else `range`.

| trend | direction | conviction | vol | → playbook | entry source |
|---|---|---|---|---|---|
| down | short | med/high | normal/exp | **sell-the-rip (trend-following)** | nearest resistance |
| down | short | low | any | **stand-aside / wait-pullback** | watch |
| up | long | med/high | normal/exp | **buy-the-dip (trend-following)** | nearest support |
| up | long | low | any | **stand-aside / wait-pullback** | none |
| range | any | any | contraction | **range-fade** | range edges |
| range | any | any | expansion | **stand-aside (breakout pending)** | await break |
| any | neutral | any | any | **stand-aside** | none |
| down | long | any | any | **stand-aside** (no counter-trend v1) | none |
| up | short | any | any | **stand-aside** | none |

Baked-in: no counter-trend trades v1; low conviction → stand-aside;
range+expansion → stand-aside; range+contraction → range-fade. Caveat surface #3:
`confidence < confidence_floor` (default 0.45) forces playbook → stand-aside.

---

## 5. Invalidation rules (`levels.invalidation`)

Deterministic `{price, rule}` by `bias.direction`. Config block `invalidation`.

### 5.1 Level inputs (feed `levels.support/resistance`)
- Swing levels: confirmed pivots (anchor `1d`). Highs→resistance, lows→support.
  Cluster within `cluster_atr` (0.5 ATR) into single levels.
- MA20/50/100 double as dynamic S/R, included in arrays.

### 5.2 Price + rule by direction
- **SHORT:** `price = recent swing_high(1d) + atr_mult×ATR(14,1d)` (mult 0.5);
  `rule = "weekly close above {price} flips bias"` (confirm = weekly_close).
- **LONG:** `price = recent swing_low(1d) − buffer`;
  `rule = "weekly close below {price} flips bias"`.
- **NEUTRAL/range:** range boundary opposite the fade entry;
  `rule = "close beyond range boundary {price} voids range thesis"`.

### 5.3 ATR-floor guard
If swing-invalidation distance < `min_atr_dist`×ATR (1.0), widen to that.
`vol_regime=expansion` → buffer × `expansion_widen` (1.3).

### 5.4 Consistency assertion
SHORT: price must be ABOVE current; LONG: BELOW. If violated, warn + downgrade
conviction one notch (signals conflicting).

---

## 6. Elliott Wave placement (v2 — supporting view)

When LLM adds elliott, integrate as a **single** voting signal `elliott_1d` (not
per-TF — prevents EW, lowest trust, from swamping via multiplicity).
- Weight default 0.05 — below every directional deterministic signal. Hard cap:
  `elliott.weight ≤ min(directional deterministic weights)`, enforced in config.
- Vote: `implied_direction` → long|short; if `confidence==low` OR primary/alt
  counts disagree on direction → **neutral**. (alt_count existing ≠ neutral; only
  directional disagreement forces neutral.)
- Effect: present → joins denominator; at 0.05 can only break ties / nudge
  conviction (~4.8% max swing), never flip a primary-decided argmax.
- Guard: if elliott contradicts `structure_1d`, don't suppress — let it lower the
  winning margin (possible conviction downgrade). Intended "caution," not veto.
- EW never sets `bias.direction` alone; excluded from playbook trend derivation.

---

## 7. Config defaults — single source

All §1–§6 defaults belong in `config/engine.yaml` (v1 keeps one config file).
Keys: `timeframes`, `weights{}`, `rsi{period,overbought,oversold}`,
`ma_stack{type,periods,anchor_tf}`, `structure{pivot_lookback,swing_count}`,
`candle{tf,context_atr,enabled[]}`, `vol_regime{lookback,expansion_mult,
contraction_mult}`, `price_dist{stretch}`, `invalidation{atr_mult,confirm,
min_atr_dist,expansion_widen,cluster_atr}`, `confluence{conviction_bands:
[0.15,0.35]}`, `macro_regime{aligned,neutral,conflicting,active}`,
`confidence_floor`, `elliott{weight,enabled}`.

---

## Open items (do not block v1)
1. **EMA vs SMA** for ma_stack — defaulted EMA; config flip.
2. **Weekly close** invalidation needs 1w candles ingested even though v1 trades
   1h/4h/1d — confirm 1w fetched for the invalidation rule (low cost).
3. **`macro_regime.active`** is the only manual input in an otherwise fully
   deterministic Step 1 — deliberate human override knob encoding §8. Automating
   via ETF-flow series = out of scope v1.
