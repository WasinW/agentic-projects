# Smart Money Concepts (SMC) — Complete Trading Guide

## Document Metadata
| Field | Value |
|---|---|
| **Strategy ID** | SMC-001 |
| **Category** | Institutional Order Flow / Smart Money |
| **Asset Classes** | Forex, Crypto, Indices |
| **Timeframes** | M15 to Weekly (primary: H1–H4) |
| **Complexity** | Advanced |
| **AI Suitability** | High — rule-based structure identification |
| **Version** | 2.0 |
| **Last Updated** | 2026-04-12 |

---

## Table of Contents
1. [Introduction and Philosophy](#1-introduction-and-philosophy)
2. [Market Structure](#2-market-structure)
3. [Order Blocks (OB)](#3-order-blocks-ob)
4. [Breaker Blocks](#4-breaker-blocks)
5. [Mitigation Blocks](#5-mitigation-blocks)
6. [Institutional Order Flow Entry Drill (IOFED)](#6-institutional-order-flow-entry-drill-iofed)
7. [Premium and Discount Zones](#7-premium-and-discount-zones)
8. [Equilibrium](#8-equilibrium)
9. [Kill Zones](#9-kill-zones)
10. [Fair Value Gaps (FVG)](#10-fair-value-gaps-fvg)
11. [Liquidity Concepts](#11-liquidity-concepts)
12. [Entry Models](#12-entry-models)
13. [Mathematical Models](#13-mathematical-models)
14. [Risk Parameters](#14-risk-parameters)
15. [Complete Execution Flow](#15-complete-execution-flow)
16. [AI Implementation Notes](#16-ai-implementation-notes)
17. [References](#17-references)

---

## 1. Introduction and Philosophy

Smart Money Concepts (SMC) is a trading methodology built on the premise that financial markets are manipulated by large institutional participants — banks, hedge funds, and central banks — collectively referred to as "smart money." The framework reverses-engineers institutional behavior from price action alone, without reliance on traditional lagging indicators.

### 1.1 Core Thesis

Markets do not move randomly. Institutional participants require:
1. **Liquidity** to fill large orders without excessive slippage.
2. **Imbalance** (Fair Value Gaps) as evidence of aggressive institutional activity.
3. **Displacement** — sharp directional moves indicating smart money commitment.

### 1.2 Key Principles

- Price seeks liquidity before making real moves.
- Equal highs/lows are liquidity targets, not support/resistance.
- Institutional traders accumulate positions in ranges, distribute at extremes.
- The "true" move begins after retail traders have been stopped out.

### 1.3 Relationship to Other Frameworks

SMC synthesizes concepts from:
- **Wyckoff Method** — accumulation/distribution, composite operator
- **ICT (Inner Circle Trader)** methodology — order blocks, kill zones, optimal trade entry
- **Auction Market Theory** — fair value, imbalance

---

## 2. Market Structure

Market structure is the foundational layer of SMC analysis. It defines the directional bias that all subsequent decisions depend on.

### 2.1 Swing Points

A **swing high** is a candle high that is higher than the high of the candle immediately to its left AND the candle immediately to its right.

A **swing low** is a candle low that is lower than the low of the candle immediately to its left AND the candle immediately to its right.

For algorithmic purposes, a configurable lookback parameter `n` is used:

$$\text{SwingHigh}_i = \begin{cases} \text{True} & \text{if } H_i > \max(H_{i-n}, \ldots, H_{i-1}) \text{ and } H_i > \max(H_{i+1}, \ldots, H_{i+n}) \\ \text{False} & \text{otherwise} \end{cases}$$

$$\text{SwingLow}_i = \begin{cases} \text{True} & \text{if } L_i < \min(L_{i-n}, \ldots, L_{i-1}) \text{ and } L_i < \min(L_{i+1}, \ldots, L_{i+n}) \\ \text{False} & \text{otherwise} \end{cases}$$

Recommended `n` values:
| Timeframe | n (candles) |
|-----------|-------------|
| M5–M15 | 3–5 |
| H1 | 5–7 |
| H4 | 5–10 |
| Daily | 3–5 |

### 2.2 Bullish Market Structure (Uptrend)

- Price forms **Higher Highs (HH)** and **Higher Lows (HL)**.
- Each new swing high exceeds the previous swing high.
- Each new swing low holds above the previous swing low.

### 2.3 Bearish Market Structure (Downtrend)

- Price forms **Lower Lows (LL)** and **Lower Highs (LH)**.
- Each new swing low breaks below the previous swing low.
- Each new swing high fails to exceed the previous swing high.

### 2.4 Break of Structure (BOS)

A BOS confirms trend continuation:
- **Bullish BOS**: Price closes above a prior swing high.
- **Bearish BOS**: Price closes below a prior swing low.

Condition (Bullish):
$$\text{BullishBOS} = C_{\text{current}} > H_{\text{previous\_swing\_high}}$$

### 2.5 Change of Character (CHoCH)

A CHoCH signals a potential trend reversal:
- In an uptrend, price breaks below the most recent **Higher Low** → bearish CHoCH.
- In a downtrend, price breaks above the most recent **Lower High** → bullish CHoCH.

$$\text{BearishCHoCH} = C_{\text{current}} < L_{\text{most\_recent\_HL}} \quad \text{(in a bullish trend)}$$

### 2.6 Internal vs. External Structure

- **External Structure**: Higher-timeframe swing points (H4, Daily).
- **Internal Structure**: Lower-timeframe swing points (M15, H1) within the legs of external structure.

Internal structure breaks do not invalidate external structure. The AI agent should track both layers simultaneously.

---

## 3. Order Blocks (OB)

Order Blocks are the footprints of institutional order placement. They represent the last opposing candle (or candle cluster) before a strong displacement move.

### 3.1 Bullish Order Block

**Definition**: The last bearish candle (or series of consecutive bearish candles) before a strong bullish displacement move that creates a Break of Structure.

**Identification Algorithm**:
1. Identify a bullish BOS (price closes above a prior swing high).
2. Trace back to the impulse leg that caused the BOS.
3. Find the last bearish candle before that impulse leg began.
4. The range of that candle (open to low) defines the Bullish OB zone.

**Zone Definition**:
$$\text{BullishOB}_{\text{upper}} = O_{\text{last\_bearish\_candle}}$$
$$\text{BullishOB}_{\text{lower}} = L_{\text{last\_bearish\_candle}}$$

**Refined Zone** (for tighter entries):
$$\text{BullishOB}_{\text{refined\_upper}} = C_{\text{last\_bearish\_candle}}$$
$$\text{BullishOB}_{\text{refined\_lower}} = L_{\text{last\_bearish\_candle}}$$

### 3.2 Bearish Order Block

**Definition**: The last bullish candle (or series of consecutive bullish candles) before a strong bearish displacement move that creates a Break of Structure.

**Zone Definition**:
$$\text{BearishOB}_{\text{upper}} = H_{\text{last\_bullish\_candle}}$$
$$\text{BearishOB}_{\text{lower}} = O_{\text{last\_bullish\_candle}}$$

**Refined Zone**:
$$\text{BearishOB}_{\text{upper}} = H_{\text{last\_bullish\_candle}}$$
$$\text{BearishOB}_{\text{refined\_lower}} = C_{\text{last\_bullish\_candle}}$$

### 3.3 Order Block Validity Criteria

An OB is considered valid only if:

1. **Displacement exists**: The move away from the OB must be impulsive (large-bodied candles, minimal wicks).
   $$\text{Displacement Ratio} = \frac{|C - O|}{\text{ATR}(14)} \geq 1.5$$

2. **Imbalance (FVG) created**: The displacement should leave a Fair Value Gap.

3. **BOS occurs**: The impulse from the OB must break a prior swing point.

4. **Unmitigated**: Price has not yet returned to test the OB zone.

### 3.4 Order Block Strength Scoring

$$\text{OB\_Score} = w_1 \cdot S_{\text{displacement}} + w_2 \cdot S_{\text{FVG}} + w_3 \cdot S_{\text{freshness}} + w_4 \cdot S_{\text{HTF\_alignment}}$$

Where:
- $S_{\text{displacement}} = \min\left(\frac{|\text{displacement move}|}{2 \times \text{ATR}(14)}, 1.0\right)$
- $S_{\text{FVG}} \in \{0, 0.5, 1.0\}$ — no FVG, partial FVG, full FVG
- $S_{\text{freshness}} = e^{-\lambda \cdot t}$, where $t$ = candles since formation, $\lambda = 0.01$
- $S_{\text{HTF\_alignment}} \in \{0, 1\}$ — 1 if HTF trend agrees

Default weights: $w_1 = 0.35, w_2 = 0.25, w_3 = 0.20, w_4 = 0.20$

**Minimum threshold**: $\text{OB\_Score} \geq 0.60$ for trade consideration.

---

## 4. Breaker Blocks

A Breaker Block forms when a prior Order Block is **violated** (price trades through it) and then price reverses. The violated OB "flips" polarity.

### 4.1 Bullish Breaker Block

**Formation**:
1. A bearish Order Block is established (last bullish candle before a sell-off).
2. Price returns and breaks above the bearish OB entirely (violation).
3. The violated bearish OB now becomes a **Bullish Breaker Block**.
4. When price pulls back to this zone, it acts as support.

**Logic**:
$$\text{BullishBreaker} = \text{BearishOB}_{\text{violated}} \implies \text{zone flips to bullish support}$$

### 4.2 Bearish Breaker Block

**Formation**:
1. A bullish Order Block is established.
2. Price breaks below the bullish OB entirely (violation).
3. The violated bullish OB becomes a **Bearish Breaker Block**.
4. When price rallies to this zone, it acts as resistance.

### 4.3 Trading Rules

| Rule | Bullish Breaker | Bearish Breaker |
|------|----------------|-----------------|
| **Bias** | Long | Short |
| **Entry Zone** | OB high to OB low (now flipped) | OB low to OB high (now flipped) |
| **Confirmation** | LTF bullish CHoCH inside the zone | LTF bearish CHoCH inside the zone |
| **Stop Loss** | Below breaker low − buffer | Above breaker high + buffer |
| **Target** | Next HTF liquidity pool | Next HTF liquidity pool |

### 4.4 Breaker vs. Order Block Priority

When both an OB and a Breaker overlap, the **Breaker takes precedence** because it represents a structural shift (polarity change). The AI should assign higher confidence to Breaker entries when multiple confluences align.

---

## 5. Mitigation Blocks

### 5.1 Definition

A Mitigation Block is a zone where institutional participants return to "mitigate" (close or hedge) previously accumulated positions that are now in drawdown due to a structural shift.

### 5.2 Formation (Bearish Mitigation Block)

1. An uptrend is established; institutions are long.
2. A CHoCH occurs (bearish) — structure shifts.
3. Institutions need to close their losing long positions.
4. Price retraces up to the origin of the **last leg that failed** (the swing high that was the start of the bearish move).
5. This zone = Bearish Mitigation Block. Institutions sell here to exit longs, creating supply.

### 5.3 Formation (Bullish Mitigation Block)

1. A downtrend is established; institutions are short.
2. A CHoCH occurs (bullish).
3. Price retraces down to the origin of the last failed bearish leg.
4. This zone = Bullish Mitigation Block. Institutions buy here to cover shorts, creating demand.

### 5.4 Key Difference from Order Blocks

| Feature | Order Block | Mitigation Block |
|---------|-------------|-----------------|
| **Purpose** | Initiate new positions | Close/hedge old positions |
| **Location** | Before impulse move | At the start of a failed structural leg |
| **Strength** | Generally stronger | Moderate — one-time use |
| **Retests** | Can hold multiple times | Usually respected only once |

---

## 6. Institutional Order Flow Entry Drill (IOFED)

IOFED is a systematic top-down entry process used to align macro context with precision entry.

### 6.1 The IOFED Process

**Step 1 — HTF Narrative (Daily/Weekly)**
- Determine HTF market structure (bullish/bearish).
- Identify HTF POI (Point of Interest): OB, Breaker, FVG, liquidity pool.
- Determine if price is in premium or discount.

**Step 2 — Intermediate Timeframe Confirmation (H4/H1)**
- Wait for price to reach the HTF POI.
- Look for an intermediate-timeframe CHoCH or BOS confirming the HTF bias.
- Identify intermediate OB/FVG within the HTF POI.

**Step 3 — LTF Entry (M15/M5)**
- Drill into LTF once the intermediate confirmation fires.
- Identify a LTF CHoCH or BOS in the direction of the HTF bias.
- Enter at the LTF OB or FVG formed after the LTF structural shift.

**Step 4 — Execution**
- Place limit order at the LTF entry zone.
- Stop loss below/above the LTF swing point that formed the CHoCH.
- Targets: intermediate swing point → HTF liquidity target.

### 6.2 IOFED Decision Matrix

```
HTF Bias:    BULLISH
├── Price in Discount Zone?  → YES → Proceed
│   └── H4 CHoCH Bullish?   → YES → Proceed
│       └── M15 CHoCH Bullish? → YES → ENTER LONG at M15 OB
│           ├── SL: Below M15 swing low
│           ├── TP1: H4 internal swing high
│           └── TP2: HTF external swing high / liquidity target
├── Price in Premium Zone?   → NO TRADE (wait for discount)
└── H4 CHoCH Bearish?       → NO TRADE (conflicting signal)
```

---

## 7. Premium and Discount Zones

### 7.1 Concept

Every price leg (swing low to swing high, or vice versa) can be divided into Premium and Discount zones using the 50% (equilibrium) level.

- **Premium Zone**: Above the 50% level (expensive). Ideal for sells.
- **Discount Zone**: Below the 50% level (cheap). Ideal for buys.

### 7.2 Calculation

For a bullish leg from swing low $L$ to swing high $H$:

$$\text{Equilibrium} = \frac{H + L}{2}$$

$$\text{Premium Zone} = \left[\frac{H + L}{2}, H\right]$$

$$\text{Discount Zone} = \left[L, \frac{H + L}{2}\right]$$

### 7.3 Fibonacci Overlay

Premium/Discount zones are further refined using Fibonacci retracements of the swing:

| Fibonacci Level | Zone | Significance |
|----------------|------|--------------|
| 0.0 (Swing High) | Extreme Premium | Maximum mean-reversion potential |
| 0.236 | Premium | Shallow pullback zone |
| 0.382 | Premium | Moderate pullback zone |
| 0.500 | Equilibrium | Fair value — neutral |
| 0.618 | Discount | **Optimal Trade Entry (OTE)** |
| 0.705 | Discount | Deep discount |
| 0.786 | Discount | Extreme discount |
| 1.0 (Swing Low) | Extreme Discount | Invalidation territory |

### 7.4 Trading Rules

- **Longs**: Only at discount levels (0.618–0.786 preferred = OTE zone).
- **Shorts**: Only at premium levels (0.236–0.382 preferred).
- Entries at equilibrium (0.5) are lower probability and should be avoided unless supported by strong confluences.

$$\text{OTE\_Zone} = \left[H - 0.786 \times (H - L), \; H - 0.618 \times (H - L)\right]$$

---

## 8. Equilibrium

### 8.1 Definition

Equilibrium represents the "fair price" of a given price range. Markets naturally oscillate around equilibrium, making it a critical reference point.

$$EQ = \frac{H_{\text{range}} + L_{\text{range}}}{2}$$

### 8.2 Equilibrium Applications

1. **Range Equilibrium**: The midpoint of a consolidation range. Price spends the most time near equilibrium (cf. Market Profile / POC).

2. **Swing Equilibrium**: The 50% retracement of any impulse leg. Used to divide premium/discount.

3. **FVG Equilibrium**: The midpoint of a Fair Value Gap. Often acts as a magnet for price.

$$EQ_{\text{FVG}} = \frac{H_{\text{FVG}} + L_{\text{FVG}}}{2}$$

4. **Order Block Equilibrium**: The 50% level of an Order Block. Refined entries target this level.

### 8.3 Equilibrium as Decision Boundary

The AI agent uses equilibrium as a binary filter:

```
IF price_position < equilibrium:
    bias = BULLISH (we are in discount)
    only_look_for = LONG entries
ELIF price_position > equilibrium:
    bias = BEARISH (we are in premium)
    only_look_for = SHORT entries
```

---

## 9. Kill Zones

Kill Zones are specific time windows during which institutional participants are most active, creating the highest-probability trading setups.

### 9.1 Forex Kill Zones (UTC)

| Kill Zone | Time (UTC) | Characteristics |
|-----------|-----------|-----------------|
| **Asian Session** | 00:00 – 06:00 | Range-bound; liquidity builds at session highs/lows |
| **London Open** | 07:00 – 10:00 | Highest volatility; smart money accumulation/distribution |
| **New York Open** | 12:00 – 15:00 | Second highest volatility; often reverses London move |
| **London Close** | 15:00 – 17:00 | Institutional position squaring; trend exhaustion |

### 9.2 Crypto Kill Zones (UTC)

Crypto markets operate 24/7, but volume clustering still creates effective kill zones:

| Kill Zone | Time (UTC) | Rationale |
|-----------|-----------|-----------|
| **Asian Crypto** | 00:00 – 04:00 | Chinese/Korean/Japanese retail and institutional |
| **European Crypto** | 07:00 – 10:00 | European institutional desks active |
| **US Crypto** | 13:00 – 16:00 | US institutional and retail peak |
| **US Evening** | 20:00 – 23:00 | US retail + Asian pre-market |

### 9.3 Kill Zone Trading Logic

1. **Pre-Kill Zone**: Identify the range formed during the quiet session (e.g., Asian range before London).
2. **Kill Zone Begins**: Watch for a sweep of the quiet session liquidity (stop hunt above/below the range).
3. **Reversal**: After the sweep, look for a CHoCH on M5/M15 indicating the real move.
4. **Entry**: Enter at the OB/FVG formed after the CHoCH.

### 9.4 Asian Range Sweep Model

$$\text{Asian High} = \max(H_i) \quad \text{for } i \in [00:00, 06:00] \text{ UTC}$$
$$\text{Asian Low} = \min(L_i) \quad \text{for } i \in [00:00, 06:00] \text{ UTC}$$

**Bullish Setup**: Price sweeps below the Asian Low during London Open, then reverses with CHoCH → Long.

**Bearish Setup**: Price sweeps above the Asian High during London Open, then reverses with CHoCH → Short.

---

## 10. Fair Value Gaps (FVG)

### 10.1 Definition

A Fair Value Gap is a three-candle formation where the wick of candle 1 does not overlap with the wick of candle 3, leaving an "unfilled" price range at candle 2. This represents aggressive institutional activity creating an imbalance.

### 10.2 Bullish FVG

$$\text{BullishFVG}: L_3 > H_1$$

Zone:
$$\text{FVG\_Upper} = L_3$$
$$\text{FVG\_Lower} = H_1$$

### 10.3 Bearish FVG

$$\text{BearishFVG}: H_3 < L_1$$

Zone:
$$\text{FVG\_Upper} = L_1$$
$$\text{FVG\_Lower} = H_3$$

### 10.4 FVG as Entry Zone

- Price tends to retrace into FVGs before continuing in the direction of the impulse.
- The **CE (Consequent Encroachment)** is the 50% level of the FVG — the most likely fill level.

$$CE = \frac{\text{FVG\_Upper} + \text{FVG\_Lower}}{2}$$

### 10.5 FVG Classification

| Type | Description | Significance |
|------|-------------|--------------|
| **Unmitigated FVG** | Price has not returned to the gap | High — pending fill |
| **Partially Mitigated** | Price filled to CE but not fully | Medium — may still attract |
| **Fully Mitigated** | Price closed through entire gap | Low — no longer relevant |
| **Inversion FVG** | FVG was fully mitigated and now acts as support/resistance | Medium-High — polarity flip |

---

## 11. Liquidity Concepts

### 11.1 Types of Liquidity

**Buy-Side Liquidity (BSL)**: Stop-loss orders of short sellers sitting above swing highs. Institutions target BSL by driving price up to fill sell orders.

**Sell-Side Liquidity (SSL)**: Stop-loss orders of long traders sitting below swing lows. Institutions target SSL by driving price down to fill buy orders.

### 11.2 Liquidity Pool Identification

```python
def identify_liquidity_pools(swing_points, price_data):
    bsl_pools = []
    ssl_pools = []
    
    for sp in swing_points:
        if sp.type == "swing_high":
            # Count how many times this level was tested
            touches = count_touches(price_data, sp.price, tolerance=ATR*0.1)
            if touches >= 2:
                bsl_pools.append({
                    "level": sp.price,
                    "strength": touches,
                    "type": "BSL"
                })
        elif sp.type == "swing_low":
            touches = count_touches(price_data, sp.price, tolerance=ATR*0.1)
            if touches >= 2:
                ssl_pools.append({
                    "level": sp.price,
                    "strength": touches,
                    "type": "SSL"
                })
    
    return bsl_pools, ssl_pools
```

### 11.3 Equal Highs / Equal Lows

Equal Highs (EQH) and Equal Lows (EQL) are the highest-probability liquidity targets because they represent obvious stop-loss clusters.

$$\text{EqualHighs}: |H_a - H_b| \leq \epsilon \quad \text{where } \epsilon = 0.1 \times \text{ATR}(14)$$

### 11.4 Liquidity Sweep (Stop Hunt)

A **liquidity sweep** occurs when price moves beyond a liquidity pool and then reverses. This is the hallmark of smart money engineering — creating the appearance of a breakout to trigger retail stops, then reversing.

Detection:
$$\text{Sweep} = \begin{cases} \text{Bullish Sweep (of SSL)} & \text{if } L_i < \text{SSL\_level} \text{ AND } C_i > \text{SSL\_level} \\ \text{Bearish Sweep (of BSL)} & \text{if } H_i > \text{BSL\_level} \text{ AND } C_i < \text{BSL\_level} \end{cases}$$

---

## 12. Entry Models

### 12.1 Risk Entry (Aggressive)

The Risk Entry model places a **limit order** directly at the identified Point of Interest (OB, Breaker, FVG) without waiting for lower-timeframe confirmation.

**Advantages**: Best possible entry price; lowest stop-loss distance.
**Disadvantages**: Higher failure rate; susceptible to stop hunts.

**Protocol**:
1. Identify HTF POI (e.g., H4 Bullish OB in discount).
2. Place a limit buy at the OB body midpoint (OB equilibrium) or FVG CE.
3. Stop loss: Below the OB low minus 1x ATR buffer on entry TF.
4. No LTF confirmation required.

$$\text{Entry}_{\text{risk}} = \frac{O_{\text{OB}} + L_{\text{OB}}}{2}$$

$$\text{SL}_{\text{risk}} = L_{\text{OB}} - k \times \text{ATR}(14)_{\text{entry\_TF}}$$

Where $k = 0.2$ to $0.5$ depending on volatility.

### 12.2 Confirmation Entry (Conservative)

The Confirmation Entry model requires a **lower-timeframe structural shift** (CHoCH) within the POI before entry.

**Advantages**: Higher win rate; confirms institutional participation.
**Disadvantages**: Worse entry price; wider stop loss; may miss fast moves.

**Protocol**:
1. Identify HTF POI.
2. Wait for price to enter the POI zone.
3. Drop to LTF (one to two timeframes lower).
4. Wait for LTF CHoCH in the direction of the HTF bias.
5. Enter at the LTF OB formed after the CHoCH.
6. Stop loss: Below/above the LTF swing that formed the CHoCH.

```
HTF_POI_reached = price_enters_zone(htf_ob)
IF HTF_POI_reached:
    ltf_choch = detect_choch(ltf_candles, direction=htf_bias)
    IF ltf_choch:
        ltf_ob = find_ob_after_choch(ltf_candles, ltf_choch)
        entry = ltf_ob.midpoint
        sl = ltf_choch.swing_extreme + buffer
        EXECUTE TRADE(entry, sl, targets)
```

### 12.3 Hybrid Entry

Combine both: place a risk entry at the HTF POI with 50% of position size, and add the remaining 50% on LTF confirmation. This balances opportunity capture with confirmation.

$$\text{Avg Entry}_{\text{hybrid}} = \frac{0.5 \times E_{\text{risk}} + 0.5 \times E_{\text{confirm}}}{1.0}$$

---

## 13. Mathematical Models

### 13.1 Order Block Displacement Index (OBDI)

Measures the strength of displacement from an Order Block:

$$\text{OBDI} = \frac{\sum_{i=1}^{n} |C_i - O_i|}{\sum_{i=1}^{n} (H_i - L_i)} \times \frac{\text{Range}_{\text{impulse}}}{\text{ATR}(14) \times n}$$

Where $n$ = number of candles in the impulse leg.

Interpretation:
- $\text{OBDI} > 1.5$: Strong displacement — high-quality OB.
- $1.0 < \text{OBDI} \leq 1.5$: Moderate displacement.
- $\text{OBDI} \leq 1.0$: Weak displacement — low-quality OB.

### 13.2 Liquidity-Weighted Bias Score (LWBS)

$$\text{LWBS} = \frac{\sum_{j} \text{BSL}_j \times d_j^{-1}}{\sum_{j} \text{BSL}_j \times d_j^{-1} + \sum_{k} \text{SSL}_k \times d_k^{-1}}$$

Where:
- $\text{BSL}_j$ = strength (touch count) of the $j$-th buy-side liquidity pool
- $\text{SSL}_k$ = strength of the $k$-th sell-side liquidity pool
- $d_j, d_k$ = distance from current price to the respective pool

Interpretation:
- $\text{LWBS} > 0.6$: Price is more likely to seek BSL → bullish bias.
- $\text{LWBS} < 0.4$: Price is more likely to seek SSL → bearish bias.

### 13.3 FVG Fill Probability Model

Based on empirical observation, the probability of an FVG being filled follows a time-decay model:

$$P(\text{fill} \mid t) = 1 - e^{-\alpha \cdot t}$$

Where:
- $t$ = number of candles since FVG formation
- $\alpha$ = asset-specific fill rate parameter

Typical $\alpha$ values:
| Asset | $\alpha$ (H1) |
|-------|---------------|
| EUR/USD | 0.015 |
| GBP/USD | 0.018 |
| BTC/USD | 0.012 |
| ETH/USD | 0.014 |

### 13.4 Multi-POI Confluence Score

When multiple SMC elements overlap, the entry quality increases:

$$\text{Confluence} = \sum_{i=1}^{N} w_i \cdot \mathbb{1}[\text{POI}_i \text{ present in zone}]$$

| POI Element | Weight ($w_i$) |
|-------------|---------------|
| HTF Order Block | 0.25 |
| FVG | 0.20 |
| OTE Zone (0.618–0.786) | 0.20 |
| Liquidity Sweep | 0.15 |
| Breaker Block | 0.10 |
| Kill Zone timing | 0.10 |

**Minimum confluence for trade**: $\text{Confluence} \geq 0.55$

---

## 14. Risk Parameters

### 14.1 Position Sizing

$$\text{Position Size} = \frac{\text{Account Balance} \times R\%}{|E - SL| \times \text{Pip Value}}$$

Where $R\% = 1\%$ per trade (max 2% for A+ setups with Confluence $\geq 0.80$).

### 14.2 Stop Loss Placement

| Entry Type | SL Placement | Buffer |
|-----------|-------------|--------|
| Risk Entry at OB | Below OB low (long) / Above OB high (short) | 0.2 × ATR |
| Confirmation Entry | Below LTF CHoCH swing | 0.1 × ATR |
| FVG Entry | Below the candle 1 wick that defines the FVG | 0.15 × ATR |

### 14.3 Take Profit Targets

| Target | Location | Partial Close |
|--------|----------|---------------|
| TP1 | Internal liquidity (nearest opposing swing) | 40% of position |
| TP2 | External liquidity (HTF swing high/low) | 30% of position |
| TP3 | Extended target (next HTF liquidity pool) | 20% of position |
| Trail | Trailing stop behind each new structural HL/LH | 10% of position |

### 14.4 Risk-Reward Requirements

| Setup Quality | Minimum R:R |
|--------------|-------------|
| A+ (Confluence ≥ 0.80) | 3:1 |
| A (Confluence 0.65–0.79) | 4:1 |
| B+ (Confluence 0.55–0.64) | 5:1 |
| Below B+ | No trade |

### 14.5 Daily Risk Limits

- Maximum daily risk: 3% of account.
- Maximum concurrent trades: 3.
- Maximum correlated exposure: 2% (e.g., two USD pairs count together).
- After 2 consecutive losses: pause for 1 kill zone session.
- After 3 consecutive losses: pause for 24 hours.

### 14.6 Drawdown Management

$$\text{If Drawdown} \geq 5\%: \text{reduce } R\% \text{ to } 0.5\%$$
$$\text{If Drawdown} \geq 8\%: \text{reduce } R\% \text{ to } 0.25\%$$
$$\text{If Drawdown} \geq 10\%: \text{halt trading, review strategy}$$

---

## 15. Complete Execution Flow

### 15.1 Main Loop Pseudocode

```python
def smc_main_loop():
    """
    Main execution loop for the SMC trading strategy.
    Runs continuously during active kill zones.
    """
    
    # ========================================
    # STEP 1: HIGHER TIMEFRAME ANALYSIS (Daily/Weekly)
    # ========================================
    htf_data = fetch_candles(timeframe="D1", count=120)
    
    # 1a. Determine HTF market structure
    htf_swings = identify_swing_points(htf_data, lookback=5)
    htf_structure = classify_structure(htf_swings)  # BULLISH / BEARISH / RANGING
    
    # 1b. Identify HTF POIs
    htf_obs = find_order_blocks(htf_data, htf_swings)
    htf_fvgs = find_fvgs(htf_data)
    htf_breakers = find_breaker_blocks(htf_data, htf_obs)
    htf_liquidity = identify_liquidity_pools(htf_swings, htf_data)
    
    # 1c. Determine premium/discount
    htf_eq = calculate_equilibrium(htf_swings)
    current_zone = "DISCOUNT" if current_price < htf_eq else "PREMIUM"
    
    # 1d. Filter: Only trade in the direction of HTF structure
    if htf_structure == "BULLISH" and current_zone != "DISCOUNT":
        return NO_TRADE("Bullish bias but price in premium — wait for discount")
    if htf_structure == "BEARISH" and current_zone != "PREMIUM":
        return NO_TRADE("Bearish bias but price in discount — wait for premium")
    
    # ========================================
    # STEP 2: INTERMEDIATE TIMEFRAME (H4/H1)
    # ========================================
    itf_data = fetch_candles(timeframe="H4", count=200)
    
    # 2a. Check if price is at an HTF POI
    htf_poi = find_nearest_poi(current_price, htf_obs + htf_fvgs + htf_breakers)
    if not price_in_zone(current_price, htf_poi):
        return WAIT("Price not at HTF POI yet")
    
    # 2b. Look for ITF structural confirmation
    itf_swings = identify_swing_points(itf_data, lookback=7)
    itf_choch = detect_choch(itf_swings, direction=htf_structure)
    itf_bos = detect_bos(itf_swings, direction=htf_structure)
    
    if not (itf_choch or itf_bos):
        return WAIT("No ITF confirmation at HTF POI")
    
    # 2c. Identify ITF POI for refined entry
    itf_obs = find_order_blocks(itf_data, itf_swings)
    itf_fvgs = find_fvgs(itf_data)
    
    # ========================================
    # STEP 3: LOWER TIMEFRAME ENTRY (M15/M5)
    # ========================================
    ltf_data = fetch_candles(timeframe="M15", count=200)
    
    # 3a. Wait for LTF structural shift
    ltf_swings = identify_swing_points(ltf_data, lookback=3)
    ltf_choch = detect_choch(ltf_swings, direction=htf_structure)
    
    if not ltf_choch:
        return WAIT("No LTF CHoCH — no entry trigger")
    
    # 3b. Find LTF entry zone
    ltf_ob = find_ob_after_choch(ltf_data, ltf_choch)
    ltf_fvg = find_fvg_after_choch(ltf_data, ltf_choch)
    entry_zone = ltf_ob if ltf_ob else ltf_fvg
    
    if not entry_zone:
        return WAIT("No valid LTF entry zone after CHoCH")
    
    # ========================================
    # STEP 4: CONFLUENCE SCORING
    # ========================================
    confluence = calculate_confluence(
        htf_ob=htf_poi.type == "OB",
        fvg_present=ltf_fvg is not None,
        ote_zone=is_in_ote(current_price, htf_swings),
        liquidity_swept=detect_sweep(ltf_data, htf_liquidity),
        breaker_present=htf_poi.type == "BREAKER",
        in_kill_zone=is_kill_zone(current_time)
    )
    
    if confluence < 0.55:
        return NO_TRADE(f"Confluence {confluence} below threshold 0.55")
    
    # ========================================
    # STEP 5: RISK MANAGEMENT
    # ========================================
    # 5a. Calculate entry, SL, TP
    entry_price = entry_zone.midpoint
    
    if htf_structure == "BULLISH":
        sl_price = entry_zone.low - ATR_BUFFER
        tp1 = nearest_internal_high(itf_swings)
        tp2 = nearest_external_high(htf_swings)
    else:
        sl_price = entry_zone.high + ATR_BUFFER
        tp1 = nearest_internal_low(itf_swings)
        tp2 = nearest_external_low(htf_swings)
    
    risk_reward = abs(tp1 - entry_price) / abs(entry_price - sl_price)
    
    min_rr = get_min_rr(confluence)
    if risk_reward < min_rr:
        return NO_TRADE(f"R:R {risk_reward:.1f} below minimum {min_rr}")
    
    # 5b. Position sizing
    risk_amount = account_balance * get_risk_percent(drawdown)
    position_size = risk_amount / abs(entry_price - sl_price)
    
    # 5c. Check daily limits
    if daily_risk_used + risk_amount > MAX_DAILY_RISK:
        return NO_TRADE("Daily risk limit reached")
    
    if open_trade_count >= MAX_CONCURRENT:
        return NO_TRADE("Max concurrent trades reached")
    
    # ========================================
    # STEP 6: EXECUTE
    # ========================================
    order = place_limit_order(
        direction="BUY" if htf_structure == "BULLISH" else "SELL",
        entry=entry_price,
        stop_loss=sl_price,
        take_profit_1=tp1,
        take_profit_2=tp2,
        size=position_size,
        expiry=next_kill_zone_end()
    )
    
    log_trade(order, confluence, htf_structure, entry_zone)
    
    return order
```

### 15.2 Trade Management Pseudocode

```python
def manage_open_trade(trade):
    """
    Active management of an open SMC trade.
    """
    ltf_data = fetch_candles(timeframe=trade.entry_tf, count=100)
    
    # Partial close at TP1
    if price_reached(trade.tp1) and not trade.tp1_hit:
        close_partial(trade, percent=40)
        move_sl_to_breakeven(trade)
        trade.tp1_hit = True
    
    # Partial close at TP2
    if price_reached(trade.tp2) and not trade.tp2_hit:
        close_partial(trade, percent=30)  # 30% of original = ~50% of remaining
        trail_sl_behind_structure(trade, ltf_data)
        trade.tp2_hit = True
    
    # Trailing stop on remaining position
    if trade.tp2_hit:
        new_swing = latest_swing_in_direction(ltf_data, trade.direction)
        if new_swing:
            new_sl = new_swing.price - ATR_BUFFER if trade.direction == "BUY" else new_swing.price + ATR_BUFFER
            if is_tighter(new_sl, trade.current_sl, trade.direction):
                update_sl(trade, new_sl)
    
    # Time-based exit: if trade hasn't hit TP1 within 2 kill zone sessions
    if trade.age_in_sessions >= 2 and not trade.tp1_hit:
        close_full(trade, reason="Time expiry — no momentum")
    
    # Structural invalidation
    structure = classify_structure(identify_swing_points(ltf_data))
    if structure_contradicts(structure, trade.direction):
        close_full(trade, reason="LTF structure invalidated")
```

---

## 16. AI Implementation Notes

### 16.1 Data Requirements

| Data Type | Minimum History | Update Frequency |
|-----------|----------------|-----------------|
| Weekly candles | 2 years | Every Monday |
| Daily candles | 6 months | Every day |
| H4 candles | 3 months | Every 4 hours |
| H1 candles | 1 month | Every hour |
| M15 candles | 2 weeks | Every 15 minutes |
| M5 candles | 1 week | Every 5 minutes |

### 16.2 Computation Priorities

1. **HTF structure**: Recompute on each new Daily candle close.
2. **HTF POIs**: Recompute on each new H4 candle close.
3. **Kill Zone check**: Evaluate every minute.
4. **LTF entry**: Evaluate every M5 candle close during active kill zones only.

### 16.3 State Management

The agent must maintain:
- Active HTF bias (BULLISH/BEARISH/RANGING)
- List of unmitigated OBs, FVGs, and Breakers per timeframe
- Liquidity pools with touch counts
- Current zone (PREMIUM/DISCOUNT) per relevant swing
- Open trades with management state

### 16.4 Backtesting Considerations

- SMC setups are relatively rare (5–15 trades per pair per month on H1 timeframe).
- Require a minimum of 200 trades for statistical significance.
- Track: win rate, average R:R, profit factor, max drawdown, Sharpe ratio.
- Expected performance benchmarks:
  - Win Rate: 45–55%
  - Average R:R: 3:1 to 5:1
  - Profit Factor: 1.5–2.5
  - Monthly Return: 3–8% (with 1% risk per trade)

---

## 17. References

### Academic and Institutional Research
1. Menkhoff, L., & Taylor, M. P. (2007). "The Obstinate Passion of Foreign Exchange Professionals: Technical Analysis." *Journal of Economic Literature*, 45(4), 936–972.
2. Osler, C. L. (2003). "Currency Orders and Exchange Rate Dynamics: An Explanation for the Predictive Success of Technical Analysis." *The Journal of Finance*, 58(5), 1791–1819.
3. Kavajecz, K. A., & Odders-White, E. R. (2004). "Technical Analysis and Liquidity Provision." *The Review of Financial Studies*, 17(4), 1043–1071.

### Books
4. Brooks, A. (2012). *Trading Price Action Trends*. Wiley.
5. Wyckoff, R. D. (1931). *The Richard D. Wyckoff Method of Trading and Investing in Stocks*. Wyckoff Associates.
6. Dalton, J. F. (1993). *Mind Over Markets*. McGraw-Hill.
7. Neill, H. B. (2001). *The Art of Contrary Thinking*. Caxton Press.

### Practitioner Sources
8. ICT (The Inner Circle Trader). "ICT Mentorship" lecture series (2016–2024). — Primary source for Order Blocks, Kill Zones, OTE, and IOFED concepts.
9. Michael J. Huddleston. "ICT Charter Price Delivery Algorithm" (2022). — Institutional order flow modeling.
10. SmartRisk. "Algorithmic Detection of Order Flow Imbalances in FX Markets" (2021). — FVG quantification.
11. Axia Futures. "Institutional Order Flow Analysis" (2020). — Volume-based OB validation.

### Data Sources
12. Forex Factory. Economic calendar for Kill Zone alignment with news events.
13. CME FedWatch Tool. Interest rate expectations for macro bias.
14. CoinGlass. Crypto liquidation data for liquidity pool mapping.
15. TradingView. Charting and backtesting platform.

---

*This document is part of the Multi-Agent AI Trading System knowledge base. It should be read in conjunction with the Wyckoff Market Structure guide (02_wyckoff_market_structure), Order Flow & Liquidity guide (03_order_flow_liquidity), and the Risk Management framework.*
