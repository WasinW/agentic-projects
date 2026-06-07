# Liquidity Pools & Liquidity Analysis — FVG, Breaker Blocks, OTE Zones

> **Axis 1 — Trading Strategies | Module 03 — Order Flow & Liquidity**
> Document: 02_liquidity_concepts.md
> Version: 2.0 | Last Updated: 2026-04-12
> Classification: Core Knowledge Base — Multi-Agent AI Trading System

---

## Table of Contents

1. [Introduction to Liquidity in Trading](#1-introduction-to-liquidity-in-trading)
2. [Buy-Side Liquidity (BSL)](#2-buy-side-liquidity-bsl)
3. [Sell-Side Liquidity (SSL)](#3-sell-side-liquidity-ssl)
4. [Liquidity Voids — Price Inefficiencies](#4-liquidity-voids--price-inefficiencies)
5. [Fair Value Gaps (FVG)](#5-fair-value-gaps-fvg)
6. [Consequent Encroachment of FVG](#6-consequent-encroachment-of-fvg)
7. [Breaker Blocks](#7-breaker-blocks)
8. [Mitigation Blocks](#8-mitigation-blocks)
9. [Optimal Trade Entry (OTE) Zones](#9-optimal-trade-entry-ote-zones)
10. [Mathematical Framework for Identifying Liquidity Zones](#10-mathematical-framework-for-identifying-liquidity-zones)
11. [Algorithm for Detecting FVGs Programmatically](#11-algorithm-for-detecting-fvgs-programmatically)
12. [Core Logic — Entry/Exit](#12-core-logic--entryexit)
13. [Technical Specifications](#13-technical-specifications)
14. [Risk Parameters](#14-risk-parameters)
15. [Execution Flow — Pseudocode](#15-execution-flow--pseudocode)
16. [References](#16-references)

---

## 1. Introduction to Liquidity in Trading

### 1.1 What is Liquidity in the Context of Price Action?

In the context of ICT (Inner Circle Trader) methodology and institutional trading, **liquidity** refers to clusters of stop-loss orders and pending orders that rest at predictable price levels. These clusters represent real money that institutions can target to fill their own large positions.

**Key Insight**: Institutional traders need large amounts of liquidity (counterparty volume) to enter and exit positions. They cannot simply place market orders without significant slippage. Therefore, they actively seek out and target areas where retail stop losses cluster.

### 1.2 The Liquidity Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE LIQUIDITY CYCLE                            │
│                                                                 │
│  1. SETUP         2. SWEEP           3. REVERSAL    4. TARGET   │
│                                                                 │
│  Price creates    Price moves to      Price reverses  Price     │
│  obvious highs/   sweep the stops     sharply after   targets   │
│  lows where       clustered at        collecting      opposing  │
│  retail places    these levels         liquidity      liquidity │
│  stops                                                          │
│                                                                 │
│  ──── High ─────  ──── Sweep ────  ──── ─────  ──── Target ─── │
│       │                 ╱╲              │              │        │
│       │            ╱╲  ╱  ╲             │              │        │
│  ╱╲   │       ╱╲ ╱  ╲╱    ╲       ╱╲   │         ╱╲   │        │
│ ╱  ╲  │  ╱╲ ╱  ╲         ╲ ╱╲ ╱  ╲  │    ╱╲ ╱  ╲  │        │
│╱    ╲╱╲╱╱  ╲╱              ╲╱  ╲╱    ╲ │ ╱╱  ╲╱    ╲ │        │
│                                      ╲│╱             ╲│        │
│                                       ╲               ╲        │
│  Retail: "I'll    Retail: "I got     Smart Money:     SM exits  │
│  put my SL       stopped out!"       "Filled at      into      │
│  above high"                         their SLs"      liquidity │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Types of Liquidity

| Type | Location | Composition | Institutional Use |
|------|----------|-------------|-------------------|
| **Buy-Side Liquidity (BSL)** | Above swing highs, above equal highs | Sell stops (short traders), buy stop entries | Institutions sell INTO buy stops to fill shorts |
| **Sell-Side Liquidity (SSL)** | Below swing lows, below equal lows | Buy stops (long traders), sell stop entries | Institutions buy INTO sell stops to fill longs |
| **Internal Liquidity** | Within price ranges (FVGs, imbalances) | Limit orders, mean-reversion traders | Price rebalances to fill |
| **External Liquidity** | Beyond range extremes | Stop losses beyond obvious levels | Sweep targets for accumulation/distribution |

### 1.4 Liquidity as a Magnet

Price is drawn to liquidity like a magnet because:

1. **Institutional necessity**: Large orders REQUIRE counterparty volume to fill
2. **Market maker incentive**: Market makers are incentivized to find and trigger stops
3. **Self-fulfilling**: Everyone knows where stops are, creating consensus targets
4. **Order flow mechanics**: Triggered stops create additional momentum (cascading)

---

## 2. Buy-Side Liquidity (BSL)

### 2.1 Definition

Buy-Side Liquidity (BSL) consists of **buy stop orders** resting ABOVE the current market price. These exist because:

- Short sellers place their stop losses above recent highs
- Breakout traders have buy-stop entries above resistance
- Traders with pending orders to go long "on breakout"

### 2.2 Where BSL Accumulates

```
BSL FORMATION LOCATIONS:
════════════════════════

Location 1: Above Swing Highs
─────────────────────────────
         BSL ████████████  (sell stops from shorts + buy stop entries)
         ───────────── Swing High
    ╱╲
   ╱  ╲    ╱╲
  ╱    ╲  ╱  ╲
 ╱      ╲╱    ╲

Location 2: Above Equal Highs (Double/Triple Tops)
──────────────────────────────────────────────────
         BSL ████████████████████  (EXTRA liquidity — very obvious level)
         ─────────────────────── Equal Highs (very strong BSL)
    ╱╲        ╱╲       ╱╲
   ╱  ╲      ╱  ╲     ╱  ╲
  ╱    ╲    ╱    ╲   ╱    ╲
 ╱      ╲  ╱      ╲ ╱      ╲
╱        ╲╱        ╲╱        ╲

Location 3: Above Trendline (Descending)
────────────────────────────────────────
    BSL scattered along and above trendline
    ╲─────────────────────
     ╲      BSL ████
      ╲
       ╲    BSL ████
        ╲
         ╲  BSL ████

Location 4: Above Previous Day/Week/Month High
──────────────────────────────────────────────
    BSL ████████████████  (time-based liquidity pool)
    ─── PDH / PWH / PMH ───
```

### 2.3 BSL Grading System

Not all BSL is equal. Grade BSL by its expected magnitude:

| Grade | Condition | Expected Liquidity | Example |
|-------|-----------|-------------------|---------|
| **A+ (Premium)** | Multiple equal highs on HTF + swing high alignment | Extreme | Weekly equal highs with monthly swing high |
| **A (Strong)** | Equal highs OR significant swing high on HTF | High | Daily double top, weekly swing high |
| **B (Moderate)** | Single swing high on MTF | Moderate | 4H swing high, daily swing high |
| **C (Weak)** | Single swing high on LTF only | Low | 15M/1H swing high |

### 2.4 BSL Detection Algorithm

```python
def detect_buy_side_liquidity(candles: List[Candle], config: dict) -> List[LiquidityPool]:
    """
    Detect buy-side liquidity pools above current price.
    
    Identifies:
    1. Swing highs
    2. Equal highs (within tolerance)
    3. HTF key levels (PDH, PWH, PMH)
    """
    pools = []
    lookback = config.get('swing_lookback', 5)
    equal_high_tolerance = config.get('equal_high_tolerance_pct', 0.05)
    
    # 1. Find all swing highs
    swing_highs = []
    for i in range(lookback, len(candles) - lookback):
        is_swing = all(
            candles[i].high > candles[i-j].high and
            candles[i].high > candles[i+j].high
            for j in range(1, lookback + 1)
        )
        if is_swing:
            swing_highs.append({
                'price': candles[i].high,
                'index': i,
                'timestamp': candles[i].timestamp
            })
    
    # 2. Detect equal highs (BSL clusters)
    equal_high_groups = []
    used = set()
    
    for i, sh1 in enumerate(swing_highs):
        if i in used:
            continue
        group = [sh1]
        for j, sh2 in enumerate(swing_highs[i+1:], i+1):
            if j in used:
                continue
            pct_diff = abs(sh1['price'] - sh2['price']) / sh1['price'] * 100
            if pct_diff <= equal_high_tolerance:
                group.append(sh2)
                used.add(j)
        
        if len(group) >= 2:
            equal_high_groups.append(group)
            used.add(i)
    
    # 3. Create liquidity pools
    for group in equal_high_groups:
        avg_price = np.mean([sh['price'] for sh in group])
        pools.append(LiquidityPool(
            type='BSL',
            price=avg_price,
            grade='A' if len(group) >= 3 else 'A' if len(group) == 2 else 'B',
            touch_count=len(group),
            formation='EQUAL_HIGHS',
            first_formed=group[0]['timestamp'],
            last_touched=group[-1]['timestamp'],
            strength=min(len(group) * 0.3 + 0.4, 1.0)
        ))
    
    # 4. Add remaining single swing highs
    for i, sh in enumerate(swing_highs):
        if i not in used:
            pools.append(LiquidityPool(
                type='BSL',
                price=sh['price'],
                grade='B',
                touch_count=1,
                formation='SWING_HIGH',
                first_formed=sh['timestamp'],
                last_touched=sh['timestamp'],
                strength=0.4
            ))
    
    # 5. Sort by strength (strongest first)
    pools.sort(key=lambda p: p.strength, reverse=True)
    
    return pools
```

### 2.5 Trading BSL

**Scenario A: Trading the Sweep (Reversal)**
- Wait for price to sweep BSL
- Look for rejection (bearish candle, delta divergence, absorption on ask)
- Enter SHORT after sweep confirmation
- Stop loss: Above the sweep high
- Target: Next SSL below

**Scenario B: Trading the Run (Continuation)**
- If BSL is swept and price HOLDS above → the sweep becomes a breakout
- Enter LONG on retest of the swept level
- Stop loss: Below the retested level
- Target: Next BSL above

---

## 3. Sell-Side Liquidity (SSL)

### 3.1 Definition

Sell-Side Liquidity (SSL) consists of **sell stop orders** resting BELOW the current market price. These exist because:

- Long traders place their stop losses below recent lows
- Breakout traders have sell-stop entries below support
- Traders with pending short orders "on breakdown"

### 3.2 Where SSL Accumulates

```
SSL FORMATION LOCATIONS:
════════════════════════

Location 1: Below Swing Lows
────────────────────────────
 ╲      ╱╲    ╱
  ╲    ╱  ╲  ╱
   ╲  ╱    ╲╱
    ╲╱
         ───────────── Swing Low
         SSL ████████████  (buy stops from longs + sell stop entries)

Location 2: Below Equal Lows (Double/Triple Bottoms)
─────────────────────────────────────────────────────
╲        ╱╲        ╱╲        ╱
 ╲      ╱  ╲      ╱  ╲      ╱
  ╲    ╱    ╲    ╱    ╲    ╱
   ╲  ╱      ╲  ╱      ╲  ╱
    ╲╱        ╲╱        ╲╱
         ─────────────────────── Equal Lows (very strong SSL)
         SSL ████████████████████  (EXTREME liquidity)

Location 3: Below Ascending Trendline
──────────────────────────────────────
             ╱───────────────────
            ╱
      SSL ████  ╱
          ╱
    SSL ████  ╱
        ╱
  SSL ████

Location 4: Below Previous Day/Week/Month Low
─────────────────────────────────────────────
    ─── PDL / PWL / PML ───
    SSL ████████████████  (time-based liquidity pool)
```

### 3.3 SSL Grading System

| Grade | Condition | Expected Liquidity | Trading Significance |
|-------|-----------|-------------------|---------------------|
| **A+ (Premium)** | Multiple equal lows on HTF + swing low alignment | Extreme | High probability sweep target |
| **A (Strong)** | Equal lows OR significant swing low on HTF | High | Primary target for institutional longs |
| **B (Moderate)** | Single swing low on MTF | Moderate | Secondary target |
| **C (Weak)** | Single swing low on LTF only | Low | Minor target, may not hold |

### 3.4 SSL Detection Algorithm

```python
def detect_sell_side_liquidity(candles: List[Candle], config: dict) -> List[LiquidityPool]:
    """
    Detect sell-side liquidity pools below current price.
    Mirror logic of BSL detection but for lows.
    """
    pools = []
    lookback = config.get('swing_lookback', 5)
    equal_low_tolerance = config.get('equal_low_tolerance_pct', 0.05)
    
    # 1. Find all swing lows
    swing_lows = []
    for i in range(lookback, len(candles) - lookback):
        is_swing = all(
            candles[i].low < candles[i-j].low and
            candles[i].low < candles[i+j].low
            for j in range(1, lookback + 1)
        )
        if is_swing:
            swing_lows.append({
                'price': candles[i].low,
                'index': i,
                'timestamp': candles[i].timestamp
            })
    
    # 2. Detect equal lows (SSL clusters)
    equal_low_groups = []
    used = set()
    
    for i, sl1 in enumerate(swing_lows):
        if i in used:
            continue
        group = [sl1]
        for j, sl2 in enumerate(swing_lows[i+1:], i+1):
            if j in used:
                continue
            pct_diff = abs(sl1['price'] - sl2['price']) / sl1['price'] * 100
            if pct_diff <= equal_low_tolerance:
                group.append(sl2)
                used.add(j)
        
        if len(group) >= 2:
            equal_low_groups.append(group)
            used.add(i)
    
    # 3. Create liquidity pools
    for group in equal_low_groups:
        avg_price = np.mean([sl['price'] for sl in group])
        pools.append(LiquidityPool(
            type='SSL',
            price=avg_price,
            grade='A+' if len(group) >= 3 else 'A',
            touch_count=len(group),
            formation='EQUAL_LOWS',
            first_formed=group[0]['timestamp'],
            last_touched=group[-1]['timestamp'],
            strength=min(len(group) * 0.3 + 0.4, 1.0)
        ))
    
    # 4. Add remaining single swing lows
    for i, sl in enumerate(swing_lows):
        if i not in used:
            pools.append(LiquidityPool(
                type='SSL',
                price=sl['price'],
                grade='B',
                touch_count=1,
                formation='SWING_LOW',
                first_formed=sl['timestamp'],
                last_touched=sl['timestamp'],
                strength=0.4
            ))
    
    pools.sort(key=lambda p: p.strength, reverse=True)
    return pools
```

---

## 4. Liquidity Voids — Price Inefficiencies

### 4.1 Definition

A **Liquidity Void** (also called a "volume void" or "price vacuum") is a price range that was traversed very rapidly with minimal trading volume, creating a zone of inefficiency that price tends to revisit later to "fill" or "rebalance."

### 4.2 Why Liquidity Voids Form

```
FORMATION OF A LIQUIDITY VOID:
══════════════════════════════

Normal Price Action:                   Liquidity Void Formation:
(Balanced, efficient)                  (Displacement, inefficient)

Price moves gradually                  Price jumps rapidly through
through each level with                levels with minimal volume
volume at every price                  traded at intermediate prices

│████████│ 1.1060                      │██│ 1.1060
│████████│ 1.1058                      │  │ 1.1058  ← VOID
│████████│ 1.1056                      │  │ 1.1056  ← VOID
│████████│ 1.1054                      │  │ 1.1054  ← VOID
│████████│ 1.1052                      │  │ 1.1052  ← VOID
│████████│ 1.1050                      │██│ 1.1050
│████████│ 1.1048                      │████████│ 1.1048

Left: Volume at each level             Right: Gap in volume
      = balanced                              = inefficiency
      = less likely to revisit                = likely to revisit
```

### 4.3 Characteristics of Liquidity Voids

| Characteristic | Description |
|---------------|-------------|
| **Volume** | Very low volume within the void range |
| **Speed** | Price traversed the range in 1-3 candles |
| **Candle bodies** | Large body candles with small wicks |
| **Volume delta** | Extreme one-directional delta |
| **Post-formation** | Price typically returns to fill 50-100% of the void |
| **Timeframe relevance** | HTF voids more significant than LTF voids |

### 4.4 Detecting Liquidity Voids

```python
def detect_liquidity_voids(candles: List[Candle], config: dict) -> List[LiquidityVoid]:
    """
    Detect liquidity voids (rapid price displacement with minimal volume).
    """
    voids = []
    min_body_ratio = config.get('min_body_ratio', 0.7)  # Body must be >70% of candle range
    min_displacement_atr = config.get('min_displacement_atr', 2.0)  # Min 2 ATR move
    volume_ratio_threshold = config.get('volume_void_ratio', 0.3)  # Volume < 30% of average
    
    # Calculate ATR for context
    atr = calculate_atr(candles, period=14)
    avg_volume = np.mean([c.volume for c in candles[-50:]])
    
    for i in range(1, len(candles)):
        candle = candles[i]
        prev_candle = candles[i-1]
        
        # Check for displacement candle
        body = abs(candle.close - candle.open)
        range_size = candle.high - candle.low
        
        if range_size == 0:
            continue
        
        body_ratio = body / range_size
        displacement_size = range_size / atr[i]
        
        # Criteria for void formation
        is_displacement = (
            body_ratio >= min_body_ratio and
            displacement_size >= min_displacement_atr
        )
        
        if is_displacement:
            # Determine direction
            if candle.close > candle.open:  # Bullish displacement
                void_low = max(prev_candle.high, candle.open)
                void_high = candle.close
                direction = 'BULLISH'
            else:  # Bearish displacement
                void_high = min(prev_candle.low, candle.open)
                void_low = candle.close
                direction = 'BEARISH'
            
            if void_high > void_low:
                voids.append(LiquidityVoid(
                    high=void_high,
                    low=void_low,
                    direction=direction,
                    timestamp=candle.timestamp,
                    candle_index=i,
                    displacement_size=displacement_size,
                    filled_pct=0.0,
                    status='UNFILLED'
                ))
    
    return voids
```

### 4.5 Trading Liquidity Voids

**Entry Logic:**
- After a bearish void forms → expect price to retrace UP into the void
- Enter SHORT when price enters the void (50% level or CE of associated FVG)
- After a bullish void forms → expect price to retrace DOWN into the void
- Enter LONG when price enters the void (50% level or CE of associated FVG)

**Important**: Voids in the direction of the higher timeframe trend are MORE likely to be respected (partial fill then continuation) rather than fully filled.

---

## 5. Fair Value Gaps (FVG)

### 5.1 Definition

A **Fair Value Gap (FVG)** is a three-candle pattern where the middle candle's body creates a gap between the wicks of the first and third candles. This gap represents a price inefficiency where one side (buyers or sellers) had overwhelming dominance.

### 5.2 FVG Formation Rules

**Bullish FVG (BFVG):**
```
Candle 1 (C1): Any candle
Candle 2 (C2): Strong bullish candle (displacement)
Candle 3 (C3): Any candle

CONDITION: C3.low > C1.high
FVG ZONE: From C1.high (bottom) to C3.low (top)

Visual:
              ┌────┐
              │ C3 │
              │    │
              └──┬─┘
   FVG ZONE → │████│ ← Gap between C1.high and C3.low
              ┌──┴─┐
              │    │
              │ C2 │  ← Displacement candle
              │    │
              └──┬─┘
              ┌──┴─┐
              │ C1 │
              │    │
              └────┘
```

**Bearish FVG (SFVG):**
```
Candle 1 (C1): Any candle
Candle 2 (C2): Strong bearish candle (displacement)
Candle 3 (C3): Any candle

CONDITION: C3.high < C1.low
FVG ZONE: From C3.high (bottom) to C1.low (top)

Visual:
              ┌────┐
              │ C1 │
              │    │
              └──┬─┘
              ┌──┴─┐
              │    │
              │ C2 │  ← Displacement candle
              │    │
              └──┬─┘
   FVG ZONE → │████│ ← Gap between C3.high and C1.low
              ┌──┴─┐
              │ C3 │
              │    │
              └────┘
```

### 5.3 FVG Classification

| Type | Criteria | Quality | Trading Priority |
|------|----------|---------|-----------------|
| **Premium Bullish FVG** | Forms in premium zone (above 50% of range) during pullback | Highest | First priority for longs |
| **Discount Bullish FVG** | Forms in discount zone (below 50% of range) | High | Primary long target |
| **Premium Bearish FVG** | Forms in premium zone | High | Primary short target |
| **Discount Bearish FVG** | Forms in discount zone during pullback | Highest | First priority for shorts |
| **Balanced FVG** | Very small gap, already partially filled | Low | Lower priority |

### 5.4 FVG with Volume Confirmation

An FVG is STRONGER when accompanied by:

$$\text{FVG Strength} = \alpha \cdot \frac{V_{C2}}{V_{avg}} + \beta \cdot \frac{|\Delta_{C2}|}{\Delta_{avg}} + \gamma \cdot \frac{\text{gap\_size}}{\text{ATR}}$$

Where:
- $V_{C2}$ = Volume of the displacement candle (C2)
- $V_{avg}$ = Average volume over lookback period
- $\Delta_{C2}$ = Delta of C2 (should be strongly directional)
- $\Delta_{avg}$ = Average absolute delta
- gap_size = Size of the FVG in price
- ATR = Average True Range
- $\alpha = 0.35, \beta = 0.35, \gamma = 0.30$ (default weights)

### 5.5 FVG Trading Rules

**Entry at FVG (Mean Reversion):**

```
BULLISH FVG ENTRY:
1. Price retraces back DOWN into the FVG zone
2. Entry: At 50% of FVG (Consequent Encroachment) or at FVG bottom
3. Stop Loss: Below the FVG bottom (C1.high)
4. Take Profit: Equal to the displacement move, or next BSL

BEARISH FVG ENTRY:
1. Price retraces back UP into the FVG zone
2. Entry: At 50% of FVG (Consequent Encroachment) or at FVG top
3. Stop Loss: Above the FVG top (C1.low)
4. Take Profit: Equal to the displacement move, or next SSL
```

### 5.6 FVG Invalidation

An FVG is **invalidated** when:
- Price closes THROUGH the FVG completely (not just wicks through it)
- Specifically: a candle CLOSES beyond the far edge of the FVG

```
BULLISH FVG INVALIDATION:
─────────────────────────
  FVG top: 1.1060 (C3.low)
  FVG bottom: 1.1050 (C1.high)
  
  INVALID if: Any candle CLOSES below 1.1050
  STILL VALID if: Wick goes below 1.1050 but closes above it
  
  Note: A wick below that reverses is actually a STRONGER signal
  (it swept the stops below the FVG and then held = accumulation)
```

---

## 6. Consequent Encroachment of FVG

### 6.1 Definition

**Consequent Encroachment (CE)** is the 50% level (midpoint) of a Fair Value Gap. ICT methodology identifies this as the most probable point where price will react within an FVG.

### 6.2 Calculation

$$\text{CE}_{bullish} = \frac{C1_{high} + C3_{low}}{2} = \frac{\text{FVG bottom} + \text{FVG top}}{2}$$

$$\text{CE}_{bearish} = \frac{C1_{low} + C3_{high}}{2} = \frac{\text{FVG top} + \text{FVG bottom}}{2}$$

### 6.3 Why CE Matters

```
FVG with CE Level:
══════════════════

    FVG Top:    1.1060 ─────────────  ← Maximum expected retracement
                                          (if price goes here, FVG may fail)
    
    CE:         1.1055 ─ ─ ─ ─ ─ ─ ─  ← 50% level = OPTIMAL ENTRY
                                          Highest probability reaction point
    
    FVG Bottom: 1.1050 ─────────────  ← Minimum expected retracement
                                          (aggressive entries here)
                                          SL goes below this level

Three Entry Styles:
┌────────────────┬──────────────┬──────────────┬────────────────┐
│ Style          │ Entry Level  │ Hit Rate     │ R:R            │
├────────────────┼──────────────┼──────────────┼────────────────┤
│ Conservative   │ FVG Bottom   │ ~80%         │ Lower (wider SL)│
│ Moderate       │ CE (50%)     │ ~65%         │ Medium          │
│ Aggressive     │ FVG Top      │ ~45%         │ Higher (tight SL)│
└────────────────┴──────────────┴──────────────┴────────────────┘
```

### 6.4 CE with OTE Alignment

When the CE of an FVG aligns with the 62-79% Fibonacci retracement (OTE zone), the probability of a reaction increases significantly:

$$P(\text{reaction}) = P(\text{FVG}) \times P(\text{OTE}) \times \text{confluence\_multiplier}$$

In practice, if CE falls within the 62-79% Fib zone, treat it as a **premium setup**.

---

## 7. Breaker Blocks

### 7.1 Definition

A **Breaker Block** is a failed Order Block. When an Order Block (the last candle before a move) is violated and price closes through it, the OPPOSITE side of that candle becomes a Breaker Block — a high-probability reaction zone.

### 7.2 Formation Logic

```
BULLISH BREAKER BLOCK FORMATION:
═════════════════════════════════

Step 1: Bearish Order Block forms (last up-close candle before a down move)
        ┌─────┐
        │  OB │  ← Bearish Order Block (last bullish candle before selloff)
        │ (Up)│
        └──┬──┘
           │
           ╲
            ╲
             ╲  Price drops

Step 2: Price rallies back and CLOSES THROUGH the OB → OB FAILS
        ┌─────┐
        │  OB │ ← BROKEN (price closed above it)
        │XXXXX│
        └──┬──┘
           │╱────── Price breaks above
          ╱│
         ╱

Step 3: The BOTTOM of the broken OB becomes a BULLISH BREAKER BLOCK
        
        ──────────── Former OB high (less important)
        
        ══════════════ BULLISH BREAKER BLOCK (former OB low) ← TRADE THIS
        
        When price returns to this level → LONG entry
```

```
BEARISH BREAKER BLOCK FORMATION:
═════════════════════════════════

Step 1: Bullish Order Block forms (last down-close candle before a rally)
             ╱
            ╱
           ╱
        ┌──┴──┐
        │  OB │  ← Bullish Order Block (last bearish candle before rally)
        │(Down)│
        └─────┘

Step 2: Price drops back and CLOSES THROUGH the OB → OB FAILS
          ╲│
           ╲
        ┌──┬──┐
        │  OB │ ← BROKEN (price closed below it)
        │XXXXX│
        └─────┘

Step 3: The TOP of the broken OB becomes a BEARISH BREAKER BLOCK
        
        ══════════════ BEARISH BREAKER BLOCK (former OB high) ← TRADE THIS
        
        ──────────── Former OB low (less important)
        
        When price returns to this level → SHORT entry
```

### 7.3 Why Breaker Blocks Work

1. **Trapped traders**: Traders who entered on the original OB are now underwater. Their stop losses create liquidity.
2. **Failed support/resistance**: A broken S/R level often becomes the opposite. Breaker = S/R flip.
3. **Institutional re-entry**: Institutions who caused the original break often re-enter at the broken level.
4. **Self-fulfilling**: Experienced traders recognize the pattern and add confluence.

### 7.4 Breaker Block Detection Algorithm

```python
def detect_breaker_blocks(candles: List[Candle], 
                          order_blocks: List[OrderBlock]) -> List[BreakerBlock]:
    """
    Detect breaker blocks from failed order blocks.
    
    Logic: An OB becomes a breaker when price closes through it.
    """
    breakers = []
    
    for ob in order_blocks:
        if ob.status != 'ACTIVE':
            continue
        
        # Check if any subsequent candle CLOSES through the OB
        for i in range(ob.candle_index + 1, len(candles)):
            candle = candles[i]
            
            if ob.type == 'BEARISH_OB':
                # Bearish OB broken upward → becomes BULLISH BREAKER
                if candle.close > ob.high:
                    breakers.append(BreakerBlock(
                        type='BULLISH_BREAKER',
                        price_level=ob.low,  # Bottom of broken OB
                        range_high=ob.high,
                        range_low=ob.low,
                        formed_timestamp=candle.timestamp,
                        formed_index=i,
                        original_ob=ob,
                        status='ACTIVE',
                        strength=calculate_breaker_strength(ob, candle, candles)
                    ))
                    ob.status = 'BROKEN'
                    break
            
            elif ob.type == 'BULLISH_OB':
                # Bullish OB broken downward → becomes BEARISH BREAKER
                if candle.close < ob.low:
                    breakers.append(BreakerBlock(
                        type='BEARISH_BREAKER',
                        price_level=ob.high,  # Top of broken OB
                        range_high=ob.high,
                        range_low=ob.low,
                        formed_timestamp=candle.timestamp,
                        formed_index=i,
                        original_ob=ob,
                        status='ACTIVE',
                        strength=calculate_breaker_strength(ob, candle, candles)
                    ))
                    ob.status = 'BROKEN'
                    break
    
    return breakers


def calculate_breaker_strength(ob: OrderBlock, break_candle: Candle, 
                                candles: List[Candle]) -> float:
    """
    Calculate the strength/quality of a breaker block.
    
    Factors:
    1. How aggressively the OB was broken (displacement quality)
    2. Volume on the break candle
    3. Whether the break took liquidity (stop hunt before break)
    4. Timeframe relevance
    """
    # Displacement quality
    body = abs(break_candle.close - break_candle.open)
    range_size = break_candle.high - break_candle.low
    body_ratio = body / range_size if range_size > 0 else 0
    
    # Volume confirmation
    avg_vol = np.mean([c.volume for c in candles[-20:]])
    vol_ratio = min(break_candle.volume / avg_vol, 3.0) / 3.0
    
    # Combine
    strength = 0.5 * body_ratio + 0.3 * vol_ratio + 0.2 * ob.strength
    
    return min(strength, 1.0)
```

### 7.5 Trading Breaker Blocks

| Entry Type | Condition | Stop Loss | Target |
|-----------|-----------|-----------|--------|
| Bullish Breaker | Price retraces to breaker low | Below breaker low (1-2 ATR) | Previous swing high or next BSL |
| Bearish Breaker | Price retraces to breaker high | Above breaker high (1-2 ATR) | Previous swing low or next SSL |
| Aggressive | Enter at breaker level with limit | Tight stop (50% of breaker range) | 3-5R target |
| Conservative | Wait for LTF confirmation at breaker | Below/above LTF swing | 2-3R target |

---

## 8. Mitigation Blocks

### 8.1 Definition

A **Mitigation Block** is the origin of a move that created an Order Block which was later mitigated (returned to). It represents the zone where institutions originally placed orders, and where they may seek to add to their position or manage it.

### 8.2 Distinction from Order Blocks

| Feature | Order Block | Mitigation Block |
|---------|------------|-----------------|
| **Formation** | Last opposing candle before a move | The move's origin point |
| **First touch** | Primary reaction expected | May have been touched once already |
| **Purpose** | Initial accumulation/distribution | Position management, addition |
| **Strength after touch** | Weakened (may become breaker) | Can still hold on second touch |
| **ICT hierarchy** | Higher priority on first test | Used when OB already tested |

### 8.3 Identification

```
MITIGATION BLOCK IDENTIFICATION:
═════════════════════════════════

1. Price makes a significant move from Point A to Point B
2. The move creates an Order Block at Point A
3. Price retraces to the OB at Point A → OB "mitigated" (touched)
4. After mitigation, price moves again from Point A in the same direction
5. The low of the retracement that mitigated the OB = MITIGATION BLOCK

              Point B
              ╱╲
             ╱  ╲
            ╱    ╲
           ╱      ╲   Retracement
  Point A ╱        ╲  ╱╲  ← Returns to OB
  (OB)  ─╱──────────╲╱──╲─── ← MITIGATION BLOCK (low of retracement)
                          ╲
                           ╲  Continuation
                            ╲

The Mitigation Block is the exact low point of the retracement
that came back to test the original Order Block.
```

### 8.4 Trading Mitigation Blocks

Entry after the second test:
- First test of OB = standard OB trade
- If price returns again (second test), enter at the Mitigation Block level
- This represents the institution's second entry point
- Often combined with FVG/OTE for precision

---

## 9. Optimal Trade Entry (OTE) Zones

### 9.1 Definition

The **Optimal Trade Entry (OTE)** zone is the 62%-79% Fibonacci retracement level of a significant price swing. ICT methodology identifies this as the highest-probability zone for institutional re-entry during a retracement.

### 9.2 OTE Calculation

For a bullish OTE (buying a retracement in an uptrend):

$$\text{OTE}_{bottom} = \text{Swing High} - 0.79 \times (\text{Swing High} - \text{Swing Low})$$
$$\text{OTE}_{top} = \text{Swing High} - 0.62 \times (\text{Swing High} - \text{Swing Low})$$

For a bearish OTE (selling a retracement in a downtrend):

$$\text{OTE}_{top} = \text{Swing Low} + 0.79 \times (\text{Swing High} - \text{Swing Low})$$
$$\text{OTE}_{bottom} = \text{Swing Low} + 0.62 \times (\text{Swing High} - \text{Swing Low})$$

### 9.3 OTE Visual

```
BULLISH OTE (Buying the pullback):
═══════════════════════════════════

    Swing High ─── 1.1100 ──── 0% Fib
         │
         │    ──── 1.1076 ──── 23.6% Fib
         │
         │    ──── 1.1062 ──── 38.2% Fib (start of discount)
         │
         │    ──── 1.1050 ──── 50% Fib (equilibrium)
         │
         │    ════ 1.1038 ════ 62% Fib  ┐
         │    ║                  ║      │  OTE ZONE
         │    ║   OPTIMAL TRADE  ║      │  (62% - 79%)
         │    ║   ENTRY ZONE     ║      │
         │    ════ 1.1021 ════ 79% Fib  ┘  ← BEST ENTRY
         │
         │    ──── 1.1000 ──── 100% Fib (swing low)
         │
    Swing Low ─── 1.1000
    
    Entry: Limit buy at 1.1021-1.1038
    Stop Loss: Below Swing Low (1.1000) or below 79% (1.1021)
    Target: Above Swing High (1.1100) or next BSL
```

### 9.4 OTE with Confluence

The OTE zone becomes a **premium setup** when it aligns with:

| Confluence Factor | Description | Strength Multiplier |
|-------------------|-------------|-------------------|
| FVG within OTE | A Fair Value Gap exists within the OTE zone | 1.5x |
| Order Block at OTE | An OB sits at the OTE level | 1.4x |
| Breaker at OTE | A Breaker Block coincides with OTE | 1.3x |
| HTF S/D zone at OTE | Higher timeframe supply/demand at OTE | 1.5x |
| Volume node at OTE | High volume node from volume profile | 1.2x |
| Psychological level at OTE | Round number within OTE | 1.1x |

### 9.5 OTE Detection Algorithm

```python
def find_ote_zones(candles: List[Candle], config: dict) -> List[OTEZone]:
    """
    Find Optimal Trade Entry zones based on significant swings.
    """
    ote_zones = []
    swing_lookback = config.get('swing_lookback', 10)
    min_swing_size_atr = config.get('min_swing_size_atr', 2.0)
    
    atr = calculate_atr(candles, period=14)
    
    # Find significant swing highs and lows
    swings = find_significant_swings(candles, swing_lookback, min_swing_size_atr, atr)
    
    for i in range(1, len(swings)):
        prev_swing = swings[i-1]
        curr_swing = swings[i]
        
        swing_range = abs(curr_swing['price'] - prev_swing['price'])
        
        # Skip tiny swings
        if swing_range < min_swing_size_atr * atr[curr_swing['index']]:
            continue
        
        if prev_swing['type'] == 'LOW' and curr_swing['type'] == 'HIGH':
            # Bullish swing → Bullish OTE (buy the pullback)
            ote_top = curr_swing['price'] - 0.62 * swing_range
            ote_bottom = curr_swing['price'] - 0.79 * swing_range
            
            ote_zones.append(OTEZone(
                type='BULLISH_OTE',
                zone_high=ote_top,
                zone_low=ote_bottom,
                swing_high=curr_swing['price'],
                swing_low=prev_swing['price'],
                swing_range=swing_range,
                formed_timestamp=curr_swing['timestamp'],
                ce_level=(ote_top + ote_bottom) / 2,
                status='ACTIVE'
            ))
        
        elif prev_swing['type'] == 'HIGH' and curr_swing['type'] == 'LOW':
            # Bearish swing → Bearish OTE (sell the pullback)
            ote_bottom = curr_swing['price'] + 0.62 * swing_range
            ote_top = curr_swing['price'] + 0.79 * swing_range
            
            ote_zones.append(OTEZone(
                type='BEARISH_OTE',
                zone_high=ote_top,
                zone_low=ote_bottom,
                swing_high=prev_swing['price'],
                swing_low=curr_swing['price'],
                swing_range=swing_range,
                formed_timestamp=curr_swing['timestamp'],
                ce_level=(ote_top + ote_bottom) / 2,
                status='ACTIVE'
            ))
    
    return ote_zones
```

---

## 10. Mathematical Framework for Identifying Liquidity Zones

### 10.1 Liquidity Density Function

Define the liquidity density at price $P$ as:

$$L(P) = \sum_{i=1}^{N} w_i \cdot K\left(\frac{P - P_i}{h}\right)$$

Where:
- $P_i$ = Price of swing high/low $i$
- $w_i$ = Weight based on significance (timeframe, touch count, recency)
- $K$ = Kernel function (Gaussian: $K(x) = \frac{1}{\sqrt{2\pi}} e^{-x^2/2}$)
- $h$ = Bandwidth (controls smoothing)

This produces a smooth "liquidity profile" showing where stop orders are likely concentrated.

### 10.2 Liquidity Attractiveness Score

The probability that price targets a specific liquidity pool:

$$A(pool) = \frac{L(pool) \cdot D(pool)^{-\beta} \cdot T(pool)^{\gamma}}{\sum_{j} L(j) \cdot D(j)^{-\beta} \cdot T(j)^{\gamma}}$$

Where:
- $L(pool)$ = Estimated liquidity at the pool
- $D(pool)$ = Distance from current price to the pool
- $T(pool)$ = Time since the pool was last "touched"
- $\beta > 0$ = Distance decay parameter (closer pools more likely)
- $\gamma > 0$ = Staleness growth parameter (older, untested pools more attractive)

### 10.3 FVG Probability of Fill

Based on empirical data, the probability that an FVG will be filled (price returns to it):

$$P(\text{fill} | \text{FVG}) = 1 - e^{-\lambda \cdot t}$$

Where:
- $\lambda$ = Fill rate parameter (estimated from historical data, typically 0.02-0.05 per candle)
- $t$ = Number of candles since FVG formation

This means:
- After 20 candles: ~33-63% fill probability
- After 50 candles: ~63-92% fill probability
- After 100 candles: ~86-99% fill probability

**Most FVGs eventually get filled** — the question is WHEN and whether the trend direction determines if they provide a trading opportunity.

### 10.4 Multi-Factor Liquidity Model

Combining all liquidity concepts into a unified scoring model:

$$S_{liquidity}(P, t) = w_1 \cdot \text{BSL}(P) + w_2 \cdot \text{SSL}(P) + w_3 \cdot \text{FVG}(P, t) + w_4 \cdot \text{Breaker}(P) + w_5 \cdot \text{OTE}(P)$$

Where each component is normalized to [0, 1] and weights sum to 1.

**Default Weights:**

| Component | Weight | Rationale |
|-----------|--------|-----------|
| BSL/SSL | 0.30 | External liquidity is the primary draw |
| FVG | 0.25 | Internal liquidity (rebalancing) |
| Order Block / Breaker | 0.20 | Institutional S/D zones |
| OTE | 0.15 | Fibonacci confluence |
| Volume Profile | 0.10 | Market-generated information |

---

## 11. Algorithm for Detecting FVGs Programmatically

### 11.1 Complete FVG Detection Engine

```python
from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum
import numpy as np

class FVGType(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"

class FVGStatus(Enum):
    ACTIVE = "ACTIVE"          # Not yet tested
    PARTIALLY_FILLED = "PARTIALLY_FILLED"  # Price entered but didn't close through
    FILLED = "FILLED"          # Fully filled (CE reached)
    INVALIDATED = "INVALIDATED"  # Price closed through entirely

@dataclass
class FairValueGap:
    type: FVGType
    top: float                 # Upper boundary of FVG
    bottom: float              # Lower boundary of FVG
    ce_level: float            # Consequent Encroachment (50% level)
    candle1_index: int
    candle2_index: int         # Displacement candle
    candle3_index: int
    timestamp: float
    timeframe: str
    gap_size: float            # In price units
    gap_size_pct: float        # As percentage of price
    displacement_volume: float  # Volume of C2
    displacement_delta: float   # Delta of C2
    strength: float            # Quality score [0, 1]
    status: FVGStatus
    fill_percentage: float     # How much has been filled [0, 1]
    
    @property
    def is_tradeable(self) -> bool:
        return self.status in (FVGStatus.ACTIVE, FVGStatus.PARTIALLY_FILLED)


class FVGDetector:
    """
    Comprehensive Fair Value Gap detection and tracking engine.
    
    Features:
    - Detects bullish and bearish FVGs
    - Tracks fill status over time
    - Calculates strength/quality scores
    - Identifies confluences with other concepts
    - Provides entry/exit levels
    """
    
    def __init__(self, config: dict):
        self.min_gap_atr_ratio = config.get('min_gap_atr_ratio', 0.5)
        self.volume_weight = config.get('fvg_volume_weight', 0.35)
        self.delta_weight = config.get('fvg_delta_weight', 0.35)
        self.size_weight = config.get('fvg_size_weight', 0.30)
        self.max_active_fvgs = config.get('max_active_fvgs', 50)
        self.timeframe = config.get('timeframe', '1H')
        
        self.active_fvgs: List[FairValueGap] = []
        self.filled_fvgs: List[FairValueGap] = []
    
    def scan(self, candles: List['Candle']) -> List[FairValueGap]:
        """
        Scan candle data for all FVGs.
        
        Args:
            candles: List of OHLCV candle data
            
        Returns:
            List of detected Fair Value Gaps
        """
        if len(candles) < 3:
            return []
        
        fvgs = []
        atr = self._calculate_atr(candles, period=14)
        avg_volume = np.mean([c.volume for c in candles[-50:]]) if len(candles) >= 50 else np.mean([c.volume for c in candles])
        avg_delta = np.mean([abs(c.delta) for c in candles[-50:]]) if hasattr(candles[0], 'delta') else 1.0
        
        for i in range(2, len(candles)):
            c1 = candles[i-2]  # First candle
            c2 = candles[i-1]  # Displacement candle (middle)
            c3 = candles[i]    # Third candle
            
            current_atr = atr[i] if i < len(atr) else atr[-1]
            
            # CHECK FOR BULLISH FVG
            # Condition: C3's low is ABOVE C1's high
            if c3.low > c1.high:
                gap_size = c3.low - c1.high
                
                # Minimum size filter
                if gap_size >= current_atr * self.min_gap_atr_ratio:
                    # Calculate strength
                    strength = self._calc_fvg_strength(
                        c2=c2,
                        gap_size=gap_size,
                        atr=current_atr,
                        avg_volume=avg_volume,
                        avg_delta=avg_delta,
                        direction='BULLISH'
                    )
                    
                    fvg = FairValueGap(
                        type=FVGType.BULLISH,
                        top=c3.low,
                        bottom=c1.high,
                        ce_level=(c3.low + c1.high) / 2,
                        candle1_index=i-2,
                        candle2_index=i-1,
                        candle3_index=i,
                        timestamp=c3.timestamp,
                        timeframe=self.timeframe,
                        gap_size=gap_size,
                        gap_size_pct=(gap_size / c2.close) * 100,
                        displacement_volume=c2.volume,
                        displacement_delta=getattr(c2, 'delta', 0),
                        strength=strength,
                        status=FVGStatus.ACTIVE,
                        fill_percentage=0.0
                    )
                    fvgs.append(fvg)
            
            # CHECK FOR BEARISH FVG
            # Condition: C3's high is BELOW C1's low
            if c3.high < c1.low:
                gap_size = c1.low - c3.high
                
                # Minimum size filter
                if gap_size >= current_atr * self.min_gap_atr_ratio:
                    # Calculate strength
                    strength = self._calc_fvg_strength(
                        c2=c2,
                        gap_size=gap_size,
                        atr=current_atr,
                        avg_volume=avg_volume,
                        avg_delta=avg_delta,
                        direction='BEARISH'
                    )
                    
                    fvg = FairValueGap(
                        type=FVGType.BEARISH,
                        top=c1.low,
                        bottom=c3.high,
                        ce_level=(c1.low + c3.high) / 2,
                        candle1_index=i-2,
                        candle2_index=i-1,
                        candle3_index=i,
                        timestamp=c3.timestamp,
                        timeframe=self.timeframe,
                        gap_size=gap_size,
                        gap_size_pct=(gap_size / c2.close) * 100,
                        displacement_volume=c2.volume,
                        displacement_delta=getattr(c2, 'delta', 0),
                        strength=strength,
                        status=FVGStatus.ACTIVE,
                        fill_percentage=0.0
                    )
                    fvgs.append(fvg)
        
        self.active_fvgs.extend(fvgs)
        self._prune_active_fvgs()
        
        return fvgs
    
    def update(self, candle: 'Candle'):
        """
        Update FVG statuses based on new price action.
        Called for each new candle to track fill status.
        """
        for fvg in self.active_fvgs[:]:  # Copy list to allow removal during iteration
            if fvg.type == FVGType.BULLISH:
                self._update_bullish_fvg(fvg, candle)
            else:
                self._update_bearish_fvg(fvg, candle)
    
    def _update_bullish_fvg(self, fvg: FairValueGap, candle: 'Candle'):
        """Update a bullish FVG based on new candle data."""
        # Check if price has entered the FVG
        if candle.low <= fvg.top:
            # Price has entered the FVG from above (retracing down)
            if candle.low <= fvg.bottom:
                # Price went through entire FVG
                if candle.close < fvg.bottom:
                    # CLOSED below FVG → INVALIDATED
                    fvg.status = FVGStatus.INVALIDATED
                    fvg.fill_percentage = 1.0
                    self.active_fvgs.remove(fvg)
                    self.filled_fvgs.append(fvg)
                else:
                    # Wick below but closed inside/above → FILLED but valid
                    fvg.status = FVGStatus.FILLED
                    fvg.fill_percentage = 1.0
            elif candle.low <= fvg.ce_level:
                # Reached CE level → partially filled (significant)
                fvg.status = FVGStatus.PARTIALLY_FILLED
                fill = (fvg.top - candle.low) / fvg.gap_size
                fvg.fill_percentage = max(fvg.fill_percentage, fill)
            else:
                # Entered FVG but didn't reach CE
                fvg.status = FVGStatus.PARTIALLY_FILLED
                fill = (fvg.top - candle.low) / fvg.gap_size
                fvg.fill_percentage = max(fvg.fill_percentage, fill)
    
    def _update_bearish_fvg(self, fvg: FairValueGap, candle: 'Candle'):
        """Update a bearish FVG based on new candle data."""
        # Check if price has entered the FVG
        if candle.high >= fvg.bottom:
            # Price has entered the FVG from below (retracing up)
            if candle.high >= fvg.top:
                # Price went through entire FVG
                if candle.close > fvg.top:
                    # CLOSED above FVG → INVALIDATED
                    fvg.status = FVGStatus.INVALIDATED
                    fvg.fill_percentage = 1.0
                    self.active_fvgs.remove(fvg)
                    self.filled_fvgs.append(fvg)
                else:
                    # Wick above but closed inside/below → FILLED but valid
                    fvg.status = FVGStatus.FILLED
                    fvg.fill_percentage = 1.0
            elif candle.high >= fvg.ce_level:
                # Reached CE level
                fvg.status = FVGStatus.PARTIALLY_FILLED
                fill = (candle.high - fvg.bottom) / fvg.gap_size
                fvg.fill_percentage = max(fvg.fill_percentage, fill)
            else:
                # Entered but didn't reach CE
                fvg.status = FVGStatus.PARTIALLY_FILLED
                fill = (candle.high - fvg.bottom) / fvg.gap_size
                fvg.fill_percentage = max(fvg.fill_percentage, fill)
    
    def _calc_fvg_strength(self, c2, gap_size, atr, avg_volume, 
                           avg_delta, direction) -> float:
        """
        Calculate FVG quality/strength score.
        
        Factors:
        1. Volume of displacement candle (higher = stronger)
        2. Delta alignment (should match direction)
        3. Gap size relative to ATR (larger = stronger)
        """
        # Volume score
        vol_ratio = c2.volume / avg_volume if avg_volume > 0 else 1.0
        vol_score = min(vol_ratio / 3.0, 1.0)  # Cap at 3x average
        
        # Delta score
        delta = getattr(c2, 'delta', 0)
        if avg_delta > 0:
            delta_ratio = delta / avg_delta
            if direction == 'BULLISH':
                delta_score = min(max(delta_ratio, 0) / 3.0, 1.0)
            else:
                delta_score = min(max(-delta_ratio, 0) / 3.0, 1.0)
        else:
            delta_score = 0.5  # Neutral if no delta data
        
        # Size score
        size_ratio = gap_size / atr if atr > 0 else 1.0
        size_score = min(size_ratio / 3.0, 1.0)  # Cap at 3 ATR
        
        # Weighted combination
        strength = (
            self.volume_weight * vol_score +
            self.delta_weight * delta_score +
            self.size_weight * size_score
        )
        
        return round(strength, 4)
    
    def _calculate_atr(self, candles: List['Candle'], period: int = 14) -> np.ndarray:
        """Calculate Average True Range."""
        if len(candles) < 2:
            return np.array([0.0])
        
        trs = []
        for i in range(1, len(candles)):
            tr = max(
                candles[i].high - candles[i].low,
                abs(candles[i].high - candles[i-1].close),
                abs(candles[i].low - candles[i-1].close)
            )
            trs.append(tr)
        
        trs = np.array([trs[0]] + trs)  # Pad first value
        
        # EMA-based ATR
        atr = np.zeros(len(trs))
        atr[0] = trs[0]
        alpha = 2 / (period + 1)
        
        for i in range(1, len(trs)):
            atr[i] = alpha * trs[i] + (1 - alpha) * atr[i-1]
        
        return atr
    
    def _prune_active_fvgs(self):
        """Keep only the most recent/strongest FVGs to prevent memory bloat."""
        if len(self.active_fvgs) > self.max_active_fvgs:
            # Sort by strength and keep top N
            self.active_fvgs.sort(key=lambda f: f.strength, reverse=True)
            removed = self.active_fvgs[self.max_active_fvgs:]
            self.active_fvgs = self.active_fvgs[:self.max_active_fvgs]
            self.filled_fvgs.extend(removed)
    
    # === Public API ===
    
    def get_active_bullish_fvgs(self, current_price: float) -> List[FairValueGap]:
        """Get active bullish FVGs below current price (tradeable for longs)."""
        return [
            fvg for fvg in self.active_fvgs
            if fvg.type == FVGType.BULLISH 
            and fvg.is_tradeable 
            and fvg.top <= current_price
        ]
    
    def get_active_bearish_fvgs(self, current_price: float) -> List[FairValueGap]:
        """Get active bearish FVGs above current price (tradeable for shorts)."""
        return [
            fvg for fvg in self.active_fvgs
            if fvg.type == FVGType.BEARISH 
            and fvg.is_tradeable 
            and fvg.bottom >= current_price
        ]
    
    def get_nearest_fvg(self, current_price: float, direction: str) -> Optional[FairValueGap]:
        """Get the nearest tradeable FVG in the specified direction."""
        if direction == 'LONG':
            fvgs = self.get_active_bullish_fvgs(current_price)
            if fvgs:
                return min(fvgs, key=lambda f: current_price - f.ce_level)
        elif direction == 'SHORT':
            fvgs = self.get_active_bearish_fvgs(current_price)
            if fvgs:
                return min(fvgs, key=lambda f: f.ce_level - current_price)
        return None
```

### 11.2 FVG Visualization Data

```python
def generate_fvg_visualization_data(fvgs: List[FairValueGap], 
                                     candles: List['Candle']) -> dict:
    """Generate data structure for charting FVGs."""
    viz_data = {
        'rectangles': [],
        'lines': [],
        'labels': []
    }
    
    for fvg in fvgs:
        # Color based on type and status
        if fvg.type == FVGType.BULLISH:
            color = '#00FF0040' if fvg.is_tradeable else '#00FF0015'
        else:
            color = '#FF000040' if fvg.is_tradeable else '#FF000015'
        
        # FVG rectangle
        viz_data['rectangles'].append({
            'x_start': fvg.timestamp,
            'x_end': candles[-1].timestamp,  # Extend to current
            'y_top': fvg.top,
            'y_bottom': fvg.bottom,
            'color': color,
            'border_color': color.replace('40', 'FF'),
            'label': f"{'B' if fvg.type == FVGType.BULLISH else 'S'}FVG ({fvg.strength:.0%})"
        })
        
        # CE line
        viz_data['lines'].append({
            'x_start': fvg.timestamp,
            'x_end': candles[-1].timestamp,
            'y': fvg.ce_level,
            'style': 'dashed',
            'color': '#FFD700',
            'label': 'CE'
        })
    
    return viz_data
```

---

## 12. Core Logic — Entry/Exit

### 12.1 Complete Liquidity-Based Entry Framework

```python
class LiquidityTrader:
    """
    Trading logic based on liquidity concepts.
    Integrates FVG, BSL/SSL, Breaker Blocks, and OTE.
    """
    
    def __init__(self, config):
        self.fvg_detector = FVGDetector(config)
        self.liquidity_mapper = LiquidityMapper(config)
        self.breaker_detector = BreakerDetector(config)
        self.ote_finder = OTEFinder(config)
        self.min_confluence = config.get('min_confluence_score', 0.6)
    
    def evaluate_long_entry(self, candles, current_price, htf_bias='BULLISH'):
        """
        Evaluate potential long entry using liquidity concepts.
        
        Requirements for LONG:
        1. HTF bias is bullish (or neutral with strong signal)
        2. Price is at or approaching a liquidity concept level
        3. Sufficient confluence (multiple concepts aligning)
        4. Order flow confirmation (from Module 01)
        """
        if htf_bias == 'BEARISH':
            return None  # Do not take longs against HTF bias
        
        signals = []
        
        # Check 1: Is price at a Bullish FVG?
        bullish_fvgs = self.fvg_detector.get_active_bullish_fvgs(current_price)
        for fvg in bullish_fvgs:
            distance_to_ce = abs(current_price - fvg.ce_level)
            if distance_to_ce / fvg.gap_size < 0.3:  # Within 30% of CE
                signals.append({
                    'concept': 'FVG',
                    'level': fvg.ce_level,
                    'strength': fvg.strength,
                    'weight': 0.30
                })
        
        # Check 2: Is price at an OTE zone?
        ote_zones = self.ote_finder.find_ote_zones(candles)
        for ote in ote_zones:
            if ote.type == 'BULLISH_OTE' and ote.zone_low <= current_price <= ote.zone_high:
                signals.append({
                    'concept': 'OTE',
                    'level': ote.ce_level,
                    'strength': 0.7,
                    'weight': 0.25
                })
        
        # Check 3: Is price at a Bullish Breaker?
        breakers = self.breaker_detector.get_active_breakers('BULLISH')
        for breaker in breakers:
            if abs(current_price - breaker.price_level) / current_price < 0.001:
                signals.append({
                    'concept': 'BREAKER',
                    'level': breaker.price_level,
                    'strength': breaker.strength,
                    'weight': 0.25
                })
        
        # Check 4: Has SSL been swept recently? (Liquidity taken → reversal expected)
        recent_sweep = self.liquidity_mapper.check_recent_ssl_sweep(candles[-5:])
        if recent_sweep:
            signals.append({
                'concept': 'SSL_SWEEP',
                'level': recent_sweep['price'],
                'strength': recent_sweep['strength'],
                'weight': 0.20
            })
        
        # Calculate confluence score
        if not signals:
            return None
        
        confluence_score = sum(s['strength'] * s['weight'] for s in signals)
        
        if confluence_score >= self.min_confluence:
            # Determine optimal entry level
            entry_level = np.mean([s['level'] for s in signals])
            
            # Determine stop loss (below all concept levels)
            sl_level = min(s['level'] for s in signals) - self._calc_sl_buffer(candles)
            
            # Determine take profit (next BSL or opposing liquidity)
            tp_level = self._find_long_target(current_price, candles)
            
            return {
                'direction': 'LONG',
                'entry': entry_level,
                'stop_loss': sl_level,
                'take_profit': tp_level,
                'confluence_score': confluence_score,
                'signals': signals,
                'risk_reward': (tp_level - entry_level) / (entry_level - sl_level)
            }
        
        return None
```

### 12.2 Entry/Exit Summary Table

| Setup | Entry | Stop Loss | TP1 | TP2 | Min R:R |
|-------|-------|-----------|-----|-----|---------|
| FVG Long | At CE or FVG bottom | Below FVG (1 ATR buffer) | Previous swing high | Next BSL | 2:1 |
| FVG Short | At CE or FVG top | Above FVG (1 ATR buffer) | Previous swing low | Next SSL | 2:1 |
| OTE Long | Within 62-79% zone | Below swing low | Swing high | -27% extension | 3:1 |
| OTE Short | Within 62-79% zone | Above swing high | Swing low | -27% extension | 3:1 |
| Breaker Long | At breaker level | Below breaker range | Previous high | Next BSL | 2.5:1 |
| Breaker Short | At breaker level | Above breaker range | Previous low | Next SSL | 2.5:1 |
| SSL Sweep Long | After sweep confirmation | Below sweep low | Previous high | Opposing liquidity | 3:1 |
| BSL Sweep Short | After sweep confirmation | Above sweep high | Previous low | Opposing liquidity | 3:1 |

---

## 13. Technical Specifications

### 13.1 Detection Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `swing_lookback` | 5 | [3, 20] | Candles to confirm swing H/L |
| `equal_high_tolerance_pct` | 0.05 | [0.01, 0.20] | % tolerance for equal highs |
| `equal_low_tolerance_pct` | 0.05 | [0.01, 0.20] | % tolerance for equal lows |
| `min_gap_atr_ratio` | 0.5 | [0.2, 2.0] | Min FVG size relative to ATR |
| `fvg_volume_weight` | 0.35 | [0.1, 0.5] | Weight for volume in FVG strength |
| `min_confluence_score` | 0.6 | [0.4, 0.9] | Min score for trade entry |
| `ote_fib_high` | 0.79 | [0.75, 0.85] | Upper OTE boundary |
| `ote_fib_low` | 0.62 | [0.55, 0.65] | Lower OTE boundary |
| `breaker_min_strength` | 0.5 | [0.3, 0.8] | Min breaker quality |
| `max_active_fvgs` | 50 | [20, 200] | Max FVGs tracked simultaneously |

### 13.2 Timeframe Hierarchy

| Timeframe | Use | FVG Relevance | Liquidity Pool Significance |
|-----------|-----|---------------|---------------------------|
| Monthly | Directional bias | Major FVGs (hold for weeks) | Premium pools |
| Weekly | Swing direction | Strong FVGs (hold for days) | High significance |
| Daily | Entry direction | Moderate FVGs (hold for hours) | Medium significance |
| 4H | Entry timing | Short-term FVGs | Standard |
| 1H | Precision entry | Quick FVGs (intraday) | Lower |
| 15M | Scalp entries | Micro FVGs | Lowest |

---

## 14. Risk Parameters

### 14.1 Risk Per Trade by Setup Quality

| Confluence Score | Risk % | Position Size Multiplier |
|-----------------|--------|-------------------------|
| 0.9+ (Premium) | 2.0% | 1.5x |
| 0.7-0.9 (Strong) | 1.5% | 1.0x |
| 0.6-0.7 (Moderate) | 1.0% | 0.75x |
| <0.6 (Weak) | NO TRADE | 0x |

### 14.2 Stop Loss Rules

1. **FVG trades**: SL below/above the FVG edge + 0.5 ATR buffer
2. **OTE trades**: SL below/above the swing that defines the OTE
3. **Breaker trades**: SL beyond the breaker range + 1 ATR buffer
4. **Sweep trades**: SL beyond the sweep extreme + spread buffer

### 14.3 Take Profit Scaling

```
Position Management:
- TP1 (33% of position): 1:1 R:R → Move SL to breakeven
- TP2 (33% of position): 2:1 R:R → Trail stop
- TP3 (34% of position): Let run to liquidity target with trailing stop
```

---

## 15. Execution Flow — Pseudocode

```python
async def liquidity_trading_loop(config, data_feed, executor):
    """
    Main loop for liquidity-based trading strategy.
    """
    # Initialize
    fvg_detector = FVGDetector(config)
    liquidity_mapper = LiquidityMapper(config)
    breaker_detector = BreakerDetector(config)
    ote_finder = OTEFinder(config)
    risk_mgr = RiskManager(config)
    
    # Multi-timeframe candle stores
    candle_stores = {
        '1D': CandleStore('1D'),
        '4H': CandleStore('4H'),
        '1H': CandleStore('1H'),
        '15M': CandleStore('15M'),
    }
    
    async for tick in data_feed:
        # Update candle stores
        for tf, store in candle_stores.items():
            new_candle = store.update(tick)
            if new_candle:
                # Run detectors on new candle
                fvg_detector.scan(store.candles)
                fvg_detector.update(new_candle)
        
        current_price = tick.price
        
        # 1. DETERMINE HTF BIAS (Daily)
        htf_bias = determine_bias(candle_stores['1D'].candles)
        
        # 2. MAP LIQUIDITY (4H)
        bsl_pools = liquidity_mapper.detect_bsl(candle_stores['4H'].candles)
        ssl_pools = liquidity_mapper.detect_ssl(candle_stores['4H'].candles)
        
        # 3. IDENTIFY ENTRY CONCEPTS (1H)
        active_fvgs = fvg_detector.active_fvgs
        active_breakers = breaker_detector.get_active_breakers()
        ote_zones = ote_finder.find_ote_zones(candle_stores['1H'].candles)
        
        # 4. CHECK IF PRICE IS AT A CONCEPT LEVEL (15M for precision)
        if htf_bias == 'BULLISH':
            entry = evaluate_long_entry(
                current_price, active_fvgs, ote_zones, 
                active_breakers, ssl_pools, candle_stores['15M'].candles
            )
        elif htf_bias == 'BEARISH':
            entry = evaluate_short_entry(
                current_price, active_fvgs, ote_zones,
                active_breakers, bsl_pools, candle_stores['15M'].candles
            )
        else:
            entry = None
        
        # 5. EXECUTE IF VALID
        if entry and entry['risk_reward'] >= config['min_rr']:
            if risk_mgr.can_open_position():
                size = risk_mgr.calculate_size(
                    entry=entry['entry'],
                    stop=entry['stop_loss']
                )
                await executor.submit_order(
                    side='BUY' if entry['direction'] == 'LONG' else 'SELL',
                    size=size,
                    entry_price=entry['entry'],
                    stop_loss=entry['stop_loss'],
                    take_profit=entry['take_profit'],
                    metadata=entry
                )
```

---

## 16. References

### Academic & Theoretical

1. **Kyle, A. S.** (1985). "Continuous Auctions and Insider Trading." *Econometrica*. — Informed trading and liquidity.

2. **O'Hara, M.** (1995). *Market Microstructure Theory*. Blackwell. — How liquidity is provided and consumed.

3. **Glosten, L. R., & Milgrom, P. R.** (1985). "Bid, Ask and Transaction Prices in a Specialist Market." *JFE*. — Adverse selection and liquidity.

4. **Amihud, Y.** (2002). "Illiquidity and Stock Returns: Cross-Section and Time-Series Effects." *Journal of Financial Markets*. — Illiquidity premium.

5. **Easley, D., & O'Hara, M.** (1987). "Price, Trade Size, and Information in Securities Markets." *JFE*. — Information content of trades.

6. **Bouchaud, J. P., et al.** (2009). "How Markets Slowly Digest Changes in Supply and Demand." — Price impact and liquidity.

### ICT Methodology & Practitioner

7. **ICT (Inner Circle Trader)** — Complete body of work on:
   - Buy-side and sell-side liquidity
   - Fair Value Gaps
   - Optimal Trade Entry
   - Breaker Blocks
   - Mitigation Blocks
   - Consequent Encroachment
   - Kill Zones and institutional timing

8. **Smart Money Concepts (SMC)** — Community-developed extensions of ICT concepts applied to crypto and modern markets.

9. **Wyckoff, R. D.** (1931). *The Richard D. Wyckoff Method of Trading and Investing in Stocks*. — Original institutional accumulation/distribution framework.

10. **Dalton, J. F.** (1993). *Mind Over Markets*. — Auction Market Theory and value area concepts.

### Data & Tools

11. **TradingView** — Pine Script documentation for FVG and liquidity detection.
12. **ATAS Platform** — Order flow and footprint chart documentation.
13. **Exocharts** — Crypto-specific liquidity and FVG visualization tools.

---

> **Previous Document**: [01_order_book_analysis.md](./01_order_book_analysis.md) — Level 2 data and order book analysis
> **Next Document**: [03_hft_stop_hunting.md](./03_hft_stop_hunting.md) — HFT algorithms and institutional stop hunting mechanics
