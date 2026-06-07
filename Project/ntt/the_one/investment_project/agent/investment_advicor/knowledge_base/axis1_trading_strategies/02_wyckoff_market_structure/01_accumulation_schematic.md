# Wyckoff Accumulation Schematic — Complete Analysis

> **Module**: Axis 1 — Trading Strategies
> **Topic**: 02 — Wyckoff Method & Market Structure
> **File**: 01_accumulation_schematic.md
> **Version**: 1.0
> **Last Updated**: 2026-04-12
> **Author**: NTT Multi-Agent AI Trading System — Knowledge Base Team

---

## Table of Contents

1. [Introduction to Accumulation](#1-introduction-to-accumulation)
2. [Accumulation Schematic #1 — Standard](#2-accumulation-schematic-1--standard)
3. [Accumulation Schematic #2 — With Spring](#3-accumulation-schematic-2--with-spring)
4. [Detailed Phase Analysis](#4-detailed-phase-analysis)
5. [Volume Analysis at Each Phase](#5-volume-analysis-at-each-phase)
6. [Real-Time Identification](#6-real-time-identification)
7. [Mathematical Models](#7-mathematical-models)
8. [Accumulation vs Continued Downtrend](#8-accumulation-vs-continued-downtrend)
9. [Entry/Exit Logic](#9-entryexit-logic)
10. [Risk Parameters](#10-risk-parameters)
11. [Execution Flow](#11-execution-flow)
12. [Forex-Specific Accumulation](#12-forex-specific-accumulation)
13. [Crypto-Specific Accumulation](#13-crypto-specific-accumulation)
14. [Common Mistakes and Pitfalls](#14-common-mistakes-and-pitfalls)
15. [References](#15-references)

---

## 1. Introduction to Accumulation

### 1.1 Definition

Accumulation is the first phase of the Wyckoff market cycle. It represents a **sideways trading range** that forms at the bottom of a downtrend, during which the Composite Man (CM) — representing large institutional operators — systematically absorbs available supply (selling pressure) and builds a long position at favorable prices.

### 1.2 Purpose from CM's Perspective

The Composite Man must accumulate a large position **without** significantly moving price upward. To accomplish this, CM:

1. **Creates fear**: Uses selling climaxes and springs to generate panic selling among retail traders
2. **Absorbs supply**: Quietly buys the selling pressure at each test of support
3. **Tests supply**: Periodically allows price to fall to check if supply remains (if supply dries up, accumulation is near complete)
4. **Shakes out weak hands**: Springs below support to trigger stop losses and margin calls
5. **Confirms completion**: Allows a Sign of Strength (SOS) rally to break above resistance, confirming demand now overwhelms supply

### 1.3 Duration and Proportionality

Per Wyckoff's Law of Cause and Effect:

$$
\text{Expected Markup Move} \propto \text{Duration of Accumulation} \times \text{Width of Range}
$$

More precisely:

$$
T_{\text{markup}} \approx \beta \cdot \sqrt{T_{\text{accumulation}}}
$$

Where:
- $T_{\text{markup}}$ = expected duration of markup phase
- $T_{\text{accumulation}}$ = duration of accumulation phase (in bars)
- $\beta$ = asset-specific scaling constant (typically 2.0–5.0)

---

## 2. Accumulation Schematic #1 — Standard

### 2.1 ASCII Schematic

```
                    Accumulation Schematic #1 (Standard — No Spring)
                    
Price
  │
  │   ╲
  │    ╲  Prior Downtrend
  │     ╲
  │      ╲                         AR
  │    PS ╲                       ╱  ╲        SOS
  │    │   ╲                     ╱    ╲      ╱   ╲   
  │    ↓    ╲      ╱────────────╱──────╲────╱─────╲──── Creek (Resistance)
  │          ╲    ╱  ST(b)             ST           LPS  
  │           ╲  ╱     ╲              ╱ ╲         ╱  ╲
  │            ╲╱       ╲            ╱   ╲       ╱    ╲
  │    ────────SC────────╲──────────╱─────╲─────╱──────── Ice (Support)
  │                       ╲       ╱       ╲   ╱
  │                        ╲     ╱     Secondary Test
  │                         ╲   ╱      on higher low
  │                      ST in Phase B
  │
  │  Phase A  │    Phase B                │ Phase C│  Phase D   │Phase E
  │ (Stopping)│    (Building Cause)       │(Test)  │  (Trend)   │(Markup)
  │           │                           │        │            │
  └───────────┴───────────────────────────┴────────┴────────────┴──→ Time
  
  Volume:
  ████      ███      ██    █     ██   █    ████    ██    ████
  HIGH      HIGH    MED   LOW   MED  LOW   HIGH   LOW   HIGH
  (SC)     (ST/AR)        (test)           (SOS)  (LPS)  (BU)
```

### 2.2 Key Events in Schematic #1

| Event | Abbreviation | Phase | Position | Description |
|---|---|---|---|---|
| Preliminary Support | PS | A | Before SC | First significant buying after extended decline |
| Selling Climax | SC | A | Range bottom | Panic selling with extreme volume, wide spread, reversal |
| Automatic Rally | AR | A | Range top | Sharp bounce from SC, defines resistance |
| Secondary Test | ST | B | Near SC | Retest of SC low on lower volume |
| Sign of Strength | SOS | D | Above AR | Rally that breaks above trading range resistance |
| Last Point of Support | LPS | D | Above SC | Pullback after SOS on low volume |
| Back-Up | BU | E | Near AR | Final retest of broken resistance as support |

---

## 3. Accumulation Schematic #2 — With Spring

### 3.1 ASCII Schematic

```
                    Accumulation Schematic #2 (With Spring — Most Common)
                    
Price
  │
  │   ╲
  │    ╲  Prior Downtrend
  │     ╲
  │      ╲                         AR
  │    PS ╲                       ╱  ╲                    SOS
  │    │   ╲                     ╱    ╲     Test        ╱    ╲
  │    ↓    ╲      ╱────────────╱──────╲───╱──╲────────╱──────╲── Creek
  │          ╲    ╱  ST(b)             ST       ╲     ╱    LPS  ╲
  │           ╲  ╱     ╲              ╱ ╲        ╲   ╱     │     BU
  │            ╲╱       ╲            ╱   ╲        ╲ ╱      ↓     ╱
  │    ────────SC────────╲──────────╱─────╲────────╳───────────── Ice
  │                       ╲       ╱       ╲      ╱│╲
  │                        ╲     ╱         ╲    ╱ │ ╲
  │                         ╲   ╱           ╲  ╱  │  ← Test of Spring
  │                      ST in Phase B    Spring   │    (higher low)
  │                                    (shakeout)  │
  │                                                │
  │  Phase A  │    Phase B                │Phase C │  Phase D   │Phase E
  │ (Stopping)│    (Building Cause)       │(Test)  │  (Trend)   │(Markup)
  │           │                           │        │            │
  └───────────┴───────────────────────────┴────────┴────────────┴──→ Time
  
  Volume:
  ████      ███      ██    █     ██  ███  █     ████   ██    ████
  HIGH      HIGH    MED   LOW   MED  HIGH LOW   HIGH  LOW   HIGH
  (SC)     (ST/AR)        (test)   (Spring)(Test)(SOS) (LPS)  (BU)
```

### 3.2 Spring Classification

Springs are classified by the depth of penetration below support:

| Type | Penetration | Volume | Reversal Speed | Trading Value |
|---|---|---|---|---|
| **Spring #1** | Deep (> 3% below) | Very high | Slow | Low — may indicate continued weakness |
| **Spring #2** | Moderate (1–3% below) | Moderate-High | Moderate-Fast | Moderate — needs confirmation |
| **Spring #3** | Shallow (< 1% below) | Low-Moderate | Fast | High — best spring, CM testing with minimal effort |

$$
\text{Spring Quality Score} = \frac{1}{\text{Depth}^2} \times \frac{V_{\text{reversal\_bar}}}{V_{\text{breakdown\_bar}}} \times \text{Reversal Speed}
$$

Where:
- Depth = penetration below support as % of ATR
- Reversal Speed = number of bars to reclaim support (lower = better)

---

## 4. Detailed Phase Analysis

### 4.1 Phase A — Stopping the Downtrend

Phase A marks the end of the prior downtrend and the beginning of a sideways trading range. The purpose is to **halt the decline** and establish the first boundaries of the trading range.

#### 4.1.1 Preliminary Support (PS)

**Definition**: The first significant buying interest that appears after an extended decline. Price may temporarily stabilize, but this is NOT the final bottom.

**Characteristics:**

| Attribute | Description |
|---|---|
| **Price Action** | Wide-spread down bar that closes in the middle or upper portion |
| **Volume** | Notably increased from recent bars, but not extreme |
| **Context** | Occurs after extended downtrend; price has been falling for weeks/months |
| **Close Position** | Closes in middle-to-upper third of the bar range |
| **Significance** | Alerts that the downtrend may be nearing exhaustion |
| **Reliability** | Low alone — only meaningful when followed by SC |

**Mathematical Detection:**

$$
\text{PS\_detected} = \begin{cases}
\text{true} & \text{if } V(t) > \bar{V}_{20} \times 1.5 \text{ AND } \text{CPos}(t) > 0.4 \text{ AND trend} = \text{DOWN} \\
\text{false} & \text{otherwise}
\end{cases}
$$

Where Close Position:
$$
\text{CPos}(t) = \frac{C(t) - L(t)}{H(t) - L(t)}
$$

```python
def detect_preliminary_support(candles, i, avg_volume, atr, trend):
    """
    Detect Preliminary Support (PS) event.
    
    Parameters:
        candles: list of OHLCV candles
        i: current index
        avg_volume: 20-period average volume
        atr: current ATR value
        trend: current detected trend ('DOWN', 'UP', 'SIDEWAYS')
    
    Returns:
        dict or None
    """
    if trend != 'DOWN':
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    # PS conditions
    conditions = {
        'downtrend': trend == 'DOWN',
        'increased_volume': c['volume'] > avg_volume * 1.5,
        'not_extreme_volume': c['volume'] < avg_volume * 3.5,
        'wide_spread': spread > atr * 0.8,
        'close_not_at_low': close_position > 0.35,
        'prior_decline': candles[i]['close'] < candles[max(0, i-20)]['close'],
    }
    
    if all(conditions.values()):
        return {
            'event': 'PS',
            'phase': 'A',
            'index': i,
            'price': c['close'],
            'volume_ratio': c['volume'] / avg_volume,
            'close_position': close_position,
            'confidence': sum(conditions.values()) / len(conditions),
            'conditions': conditions
        }
    
    return None
```

#### 4.1.2 Selling Climax (SC)

**Definition**: The climactic selling event that establishes the lower boundary of the accumulation range. Characterized by extreme volume, wide price spread, and a close near or at the lows — followed by a reversal.

**Characteristics:**

| Attribute | Description |
|---|---|
| **Price Action** | Extreme wide-spread down bar, often with a long lower wick |
| **Volume** | Highest volume in the decline — often 3-5x average |
| **Close Position** | Initially at lows, but often rebounds to close in lower-middle |
| **Context** | Follows PS; represents capitulation and panic selling |
| **Reversal** | Sharp upward reversal follows (1-3 bars) |
| **Significance** | Defines the bottom of the trading range (Ice level) |
| **Reliability** | High when followed by AR within 1-5 bars |

**Mathematical Detection:**

$$
\text{SC\_detected} = \begin{cases}
\text{true} & \text{if } V(t) > \bar{V}_{20} \times 2.5 \\
& \text{AND } \text{Spread}(t) > ATR \times 1.5 \\
& \text{AND } P(t) < P(t-20) \\
& \text{AND } \text{PS\_exists\_within}(30 \text{ bars}) \\
\text{false} & \text{otherwise}
\end{cases}
$$

The Selling Climax Intensity Index:

$$
\text{SCI} = \frac{V(t)}{\bar{V}_{50}} \times \frac{\text{Spread}(t)}{ATR_{14}} \times (1 - \text{CPos}(t))
$$

Where higher SCI values indicate more intense selling climaxes. Typical ranges:
- SCI < 3.0: Weak climax — may not hold
- SCI 3.0–6.0: Moderate climax — likely to define range
- SCI > 6.0: Strong climax — high probability of accumulation range forming

```python
def detect_selling_climax(candles, i, avg_volume_20, avg_volume_50, atr, ps_event):
    """
    Detect Selling Climax (SC) event.
    """
    if ps_event is None:
        return None  # PS must precede SC
    
    if i - ps_event['index'] > 30:
        return None  # PS too far away
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    # Core SC conditions
    conditions = {
        'extreme_volume': c['volume'] > avg_volume_20 * 2.5,
        'wide_spread': spread > atr * 1.3,
        'bearish_context': c['low'] < min(cc['low'] for cc in candles[max(0,i-20):i]),
        'ps_exists': ps_event is not None and (i - ps_event['index']) <= 30,
    }
    
    # Reversal confirmation (check next 1-3 bars if available)
    reversal_detected = False
    if i + 1 < len(candles):
        next_bar = candles[i + 1]
        if next_bar['close'] > next_bar['open'] and next_bar['close'] > c['close']:
            reversal_detected = True
    conditions['reversal_hint'] = reversal_detected or close_position > 0.3
    
    # Calculate intensity
    sci = (c['volume'] / avg_volume_50) * (spread / atr) * (1 - close_position)
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'SC',
            'phase': 'A',
            'index': i,
            'price_low': c['low'],
            'price_close': c['close'],
            'volume_ratio': c['volume'] / avg_volume_20,
            'spread_ratio': spread / atr,
            'close_position': close_position,
            'sci': sci,
            'confidence': sum(conditions.values()) / len(conditions),
            'range_bottom': c['low'],  # Defines Ice level
            'conditions': conditions
        }
    
    return None
```

#### 4.1.3 Automatic Rally (AR)

**Definition**: The sharp, reflexive rally that immediately follows the Selling Climax. It represents the automatic reaction as short sellers cover and bargain hunters buy. The AR defines the upper boundary of the accumulation range (Creek level).

**Characteristics:**

| Attribute | Description |
|---|---|
| **Price Action** | Sharp rally with multiple bullish bars, retracing 50–100% of the SC drop |
| **Volume** | Moderate-to-high, decreasing from SC levels |
| **Duration** | Short — typically 3–10 bars |
| **Close Position** | Bars close consistently in upper half |
| **Significance** | Defines the top of the trading range (Creek/Resistance) |
| **Why it stops** | Supply re-enters the market from overhead selling pressure |

**Mathematical Detection:**

$$
\text{AR\_detected} = \begin{cases}
\text{true} & \text{if SC exists within 10 bars} \\
& \text{AND } \sum_{j=\text{SC}}^{t} \Delta P(j) > 0.5 \times |\text{SC decline}| \\
& \text{AND } \text{rally bars} \geq 3 \\
& \text{AND } V_{\text{avg,rally}} > \bar{V}_{20} \times 0.8 \\
\text{false} & \text{otherwise}
\end{cases}
$$

```python
def detect_automatic_rally(candles, i, sc_event, avg_volume, atr):
    """
    Detect Automatic Rally (AR) event.
    AR is detected at the peak of the rally following the SC.
    """
    if sc_event is None:
        return None
    
    sc_idx = sc_event['index']
    if i - sc_idx > 15 or i - sc_idx < 2:
        return None
    
    # Check if we're at a swing high after the SC
    if i + 1 >= len(candles):
        return None
    
    current_high = candles[i]['high']
    prev_high = candles[i-1]['high'] if i > 0 else 0
    next_close = candles[i+1]['close'] if i+1 < len(candles) else candles[i]['close']
    
    # AR is the first significant swing high after SC
    is_swing_high = (candles[i]['high'] >= max(c['high'] for c in candles[sc_idx:i+1]))
    price_reverting = next_close < candles[i]['close']
    
    # Rally magnitude
    sc_low = sc_event['price_low']
    rally_size = current_high - sc_low
    
    # Calculate retracement of the decline that led to SC
    pre_sc_high = max(c['high'] for c in candles[max(0, sc_idx-20):sc_idx])
    sc_decline = pre_sc_high - sc_low
    retracement = rally_size / sc_decline if sc_decline > 0 else 0
    
    conditions = {
        'follows_sc': (i - sc_idx) >= 2 and (i - sc_idx) <= 15,
        'is_swing_high': is_swing_high,
        'significant_rally': rally_size > atr * 1.5,
        'minimum_retracement': retracement >= 0.3,
        'price_starting_to_revert': price_reverting,
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'AR',
            'phase': 'A',
            'index': i,
            'price_high': current_high,
            'rally_size': rally_size,
            'retracement_pct': retracement,
            'confidence': sum(conditions.values()) / len(conditions),
            'range_top': current_high,  # Defines Creek level
            'conditions': conditions
        }
    
    return None
```

### 4.2 Phase B — Building the Cause

Phase B is the longest phase of accumulation. The purpose is for the Composite Man to **absorb the remaining supply** within the trading range. This phase builds the "cause" that will produce the subsequent "effect" (markup move).

#### 4.2.1 Secondary Test (ST)

**Definition**: A retest of the Selling Climax area on diminished volume and narrower spread, confirming that demand is overcoming supply at these levels.

**Characteristics:**

| Attribute | Description |
|---|---|
| **Price Action** | Declines toward or near SC low, but usually holds above it |
| **Volume** | Significantly lower than SC — this is the critical confirmation |
| **Spread** | Narrower than SC bars |
| **Close** | Should close above SC low |
| **Frequency** | May occur 2–4 times during Phase B |
| **Purpose** | Tests whether sellers are exhausted at the SC level |

**ST Quality Assessment:**

$$
\text{ST\_Quality} = \frac{V_{\text{SC}}}{V_{\text{ST}}} \times \frac{\text{Spread}_{\text{SC}}}{\text{Spread}_{\text{ST}}} \times \left(1 + \frac{P_{\text{ST\_low}} - P_{\text{SC\_low}}}{\text{ATR}}\right)
$$

Higher values indicate better quality ST (more supply absorbed):
- ST Quality < 1.5: Weak — supply still present
- ST Quality 1.5–3.0: Moderate — supply diminishing
- ST Quality > 3.0: Strong — supply nearly exhausted

```python
def detect_secondary_test(candles, i, sc_event, ar_event, avg_volume, atr):
    """
    Detect Secondary Test (ST) of the Selling Climax.
    """
    if sc_event is None or ar_event is None:
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    sc_low = sc_event['price_low']
    range_height = ar_event['price_high'] - sc_low
    
    # ST should be near SC low (within 15% of range from bottom)
    proximity_to_sc = (c['low'] - sc_low) / range_height if range_height > 0 else 1.0
    
    conditions = {
        'near_sc_level': abs(proximity_to_sc) < 0.15,
        'lower_volume': c['volume'] < sc_event['volume_ratio'] * avg_volume * 0.7,
        'narrower_spread': spread < sc_event['spread_ratio'] * atr * 0.8,
        'holds_above_sc': c['low'] >= sc_low - atr * 0.3,
        'after_ar': i > ar_event['index'],
        'bullish_close': close_position > 0.3,
    }
    
    # Calculate quality
    vol_ratio = (sc_event['volume_ratio'] * avg_volume) / c['volume'] if c['volume'] > 0 else 0
    spread_ratio = (sc_event['spread_ratio'] * atr) / spread if spread > 0 else 0
    level_bonus = 1 + max(0, (c['low'] - sc_low) / atr)
    quality = vol_ratio * spread_ratio * level_bonus
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'ST',
            'phase': 'B',
            'index': i,
            'price_low': c['low'],
            'quality': quality,
            'volume_vs_sc': c['volume'] / (sc_event['volume_ratio'] * avg_volume),
            'proximity_to_sc': proximity_to_sc,
            'confidence': sum(conditions.values()) / len(conditions),
            'interpretation': 'STRONG' if quality > 3.0 else 'MODERATE' if quality > 1.5 else 'WEAK',
            'conditions': conditions
        }
    
    return None
```

#### 4.2.2 Phase B Characteristics

During Phase B, price oscillates between support (SC area) and resistance (AR area). The critical observations:

```
Phase B — Supply Absorption Pattern
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Price   AR ─────────────────────────────────────────── Creek
         │  ╱╲      ╱╲         ╱╲        ╱╲  ╱╲
         │ ╱  ╲    ╱  ╲       ╱  ╲      ╱  ╲╱  ╲
         │╱    ╲  ╱    ╲     ╱    ╲    ╱         ╲
         │      ╲╱      ╲   ╱      ╲  ╱           ╲
        SC ──────────────╲─╱────────╲╱──────────── Ice
                          ╳
                   (possible test
                    below support)

Volume  ████  ██  ███  ██  █   ██  █  █   █  ██  █   ██
        HIGH      MED      LOW      LOW      LOW      LOW

         ← Supply being absorbed → ← Supply nearly exhausted →

Key Observations:
  1. Volume on tests of support DECREASES over time
  2. Volume on rallies may increase or stay constant
  3. Range may narrow toward the end (coiling)
  4. Each test of support finds less supply
  5. Each rally finds less resistance (supply weakening)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Phase B Duration Estimation:**

$$
T_B \approx 0.60 \times T_{\text{total\_accumulation}}
$$

Phase B typically represents 50–70% of the total accumulation duration.

### 4.3 Phase C — The Spring (Test)

Phase C is the **most critical phase** for trading. It contains the Spring event — the final shakeout that represents the Composite Man's last test of supply before initiating the markup.

#### 4.3.1 Spring (Shakeout)

**Definition**: A false breakdown below the support level (SC area) that quickly reverses. The CM intentionally pushes price below support to trigger retail stop losses and accumulate the resulting selling at below-value prices.

**Characteristics:**

| Attribute | Description |
|---|---|
| **Price Action** | Brief penetration below trading range support, followed by rapid reversal |
| **Volume** | Variable — Type 3 springs have low volume (ideal) |
| **Duration** | Quick — usually 1–3 bars below support before reclaiming |
| **Depth** | Should not exceed 2–3% below support (deeper = possible failure) |
| **Purpose** | Trigger stop losses, shake out weak holders, test remaining supply |
| **Significance** | Highest probability entry point in entire accumulation |

**Spring Type Classification (detailed):**

| Type | Depth (% of ATR) | Volume | Close | Reversal Bars | Trade Action |
|---|---|---|---|---|---|
| Type 3 (Best) | < 0.5 ATR below | Low to moderate | Closes above support | 1 bar | Aggressive buy |
| Type 2 (Good) | 0.5–1.5 ATR below | Moderate to high | Closes near/above support | 1–3 bars | Buy on test |
| Type 1 (Risky) | > 1.5 ATR below | Very high | Closes well below support | 3–5+ bars | Wait for test |

```python
def detect_spring(candles, i, range_support, range_resistance, avg_volume, atr, st_events):
    """
    Detect Spring (shakeout below support).
    """
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    # Must penetrate below support
    if c['low'] >= range_support:
        return None
    
    # Calculate penetration depth
    depth = range_support - c['low']
    depth_atr = depth / atr
    
    # Close must recover (at least partially)
    close_above_support = c['close'] >= range_support
    close_near_support = c['close'] >= range_support - atr * 0.2
    
    # Classify spring type
    if depth_atr < 0.5 and c['volume'] <= avg_volume * 1.3:
        spring_type = 3  # Best
        base_confidence = 0.9
    elif depth_atr < 1.5 and c['volume'] <= avg_volume * 2.0:
        spring_type = 2  # Good
        base_confidence = 0.7
    elif depth_atr < 3.0:
        spring_type = 1  # Risky
        base_confidence = 0.5
    else:
        return None  # Too deep — likely breakdown, not spring
    
    # Volume on spring vs prior ST events
    vol_decreasing_on_tests = True
    if len(st_events) >= 2:
        for j in range(1, len(st_events)):
            if st_events[j].get('volume_vs_sc', 1) >= st_events[j-1].get('volume_vs_sc', 0) * 1.1:
                vol_decreasing_on_tests = False
    
    conditions = {
        'penetrates_support': c['low'] < range_support,
        'limited_depth': depth_atr < 2.0,
        'recovers': close_above_support or close_near_support,
        'not_extreme_volume': c['volume'] < avg_volume * 3.0,
        'decreasing_supply': vol_decreasing_on_tests,
        'bullish_close': close_position > 0.4,
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'SPRING',
            'phase': 'C',
            'index': i,
            'spring_type': spring_type,
            'price_low': c['low'],
            'price_close': c['close'],
            'depth': depth,
            'depth_atr': depth_atr,
            'volume_ratio': c['volume'] / avg_volume,
            'close_above_support': close_above_support,
            'confidence': base_confidence * (sum(conditions.values()) / len(conditions)),
            'trade_action': {
                3: 'AGGRESSIVE_BUY',
                2: 'BUY_ON_TEST',
                1: 'WAIT_FOR_CONFIRMATION'
            }[spring_type],
            'stop_loss': c['low'] - atr * 0.5,
            'conditions': conditions
        }
    
    return None
```

#### 4.3.2 Test of the Spring

**Definition**: After the Spring, price may pull back toward the Spring low to **confirm** that supply has been exhausted. The Test should occur on even lower volume than the Spring and should hold above the Spring low.

**Characteristics:**

| Attribute | Description |
|---|---|
| **Price Action** | Pullback toward Spring low, but holds above it (higher low) |
| **Volume** | Must be lower than Spring volume — this is the confirmation |
| **Duration** | 3–10 bars after Spring |
| **Close** | Should close above support level |
| **Significance** | Confirms supply exhaustion — highest conviction entry point |

```python
def detect_test_of_spring(candles, i, spring_event, avg_volume, atr):
    """
    Detect the Test after a Spring event.
    This is the highest-confidence entry point.
    """
    if spring_event is None:
        return None
    
    # Must be within reasonable time after spring
    bars_since_spring = i - spring_event['index']
    if bars_since_spring < 2 or bars_since_spring > 15:
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    # Price must be near or slightly above spring low
    spring_low = spring_event['price_low']
    proximity = abs(c['low'] - spring_low) / atr
    
    conditions = {
        'near_spring_area': proximity < 1.5,
        'holds_above_spring_low': c['low'] > spring_low,
        'lower_volume': c['volume'] < spring_event['volume_ratio'] * avg_volume * 0.8,
        'bullish_close': close_position > 0.5,
        'narrower_spread': spread < atr * 1.0,
        'higher_low': c['low'] > spring_low,
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'TEST_OF_SPRING',
            'phase': 'C',
            'index': i,
            'price_low': c['low'],
            'price_close': c['close'],
            'distance_from_spring': c['low'] - spring_low,
            'volume_vs_spring': c['volume'] / (spring_event['volume_ratio'] * avg_volume),
            'confidence': 0.90 * (sum(conditions.values()) / len(conditions)),
            'trade_action': 'STRONG_BUY',
            'stop_loss': spring_low - atr * 0.3,
            'conditions': conditions
        }
    
    return None
```

### 4.4 Phase D — Markup Within the Range

Phase D confirms that demand has definitively overcome supply. The Sign of Strength (SOS) and Last Point of Support (LPS) events occur here.

#### 4.4.1 Sign of Strength (SOS)

**Definition**: A strong rally on increased volume and widening spread that breaks above the trading range resistance (Creek). This confirms the accumulation is complete and markup is beginning.

**Characteristics:**

| Attribute | Description |
|---|---|
| **Price Action** | Strong impulsive move upward, breaking above AR high/Creek resistance |
| **Volume** | Significantly increased — highest volume since SC |
| **Spread** | Wide bullish bars |
| **Close** | Consistently near highs of the bars |
| **Significance** | Confirms phase transition from Accumulation to Markup |
| **Breakout validation** | Price must close above Creek, not just wick above |

$$
\text{SOS\_Strength} = \frac{V_{\text{SOS}}}{\bar{V}_{20}} \times \frac{\text{Spread}_{\text{SOS}}}{ATR} \times \text{CPos}_{\text{SOS}} \times \frac{|\Delta P_{\text{SOS}}|}{\text{Range Height}}
$$

```python
def detect_sign_of_strength(candles, i, creek_level, avg_volume, atr, range_height):
    """
    Detect Sign of Strength (SOS) — breakout above Creek.
    """
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    # Must close above Creek resistance
    if c['close'] <= creek_level:
        return None
    
    # Check breakout quality
    breakout_distance = c['close'] - creek_level
    breakout_atr = breakout_distance / atr
    
    conditions = {
        'closes_above_creek': c['close'] > creek_level,
        'significant_breakout': breakout_atr > 0.3,
        'strong_volume': c['volume'] > avg_volume * 1.5,
        'wide_spread': spread > atr * 0.8,
        'bullish_close': close_position > 0.6,
        'body_mostly_above_creek': (c['open'] + c['close']) / 2 > creek_level,
    }
    
    # Calculate SOS strength
    strength = (c['volume'] / avg_volume) * (spread / atr) * close_position
    strength *= breakout_distance / range_height if range_height > 0 else 0
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'SOS',
            'phase': 'D',
            'index': i,
            'price_close': c['close'],
            'price_high': c['high'],
            'breakout_distance': breakout_distance,
            'strength': strength,
            'volume_ratio': c['volume'] / avg_volume,
            'confidence': sum(conditions.values()) / len(conditions),
            'interpretation': 'STRONG' if strength > 2.0 else 'MODERATE' if strength > 1.0 else 'WEAK',
            'conditions': conditions
        }
    
    return None
```

#### 4.4.2 Last Point of Support (LPS)

**Definition**: A pullback after the SOS that finds support at or above the Creek level (former resistance now acting as support). Volume should decrease during the pullback.

**Characteristics:**

| Attribute | Description |
|---|---|
| **Price Action** | Pullback toward Creek level; holds above or at Creek |
| **Volume** | Declining — significantly lower than SOS volume |
| **Spread** | Narrowing — bars getting smaller |
| **Close** | Should close above Creek level |
| **Significance** | Second-best entry point (after Test of Spring) for buyers who missed the Spring |
| **Stop Loss** | Below the Creek level |

```python
def detect_last_point_of_support(candles, i, sos_event, creek_level, avg_volume, atr):
    """
    Detect Last Point of Support (LPS) — pullback to Creek after SOS.
    """
    if sos_event is None:
        return None
    
    bars_since_sos = i - sos_event['index']
    if bars_since_sos < 2 or bars_since_sos > 20:
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    # Price should be pulling back toward Creek
    proximity_to_creek = abs(c['low'] - creek_level) / atr
    
    conditions = {
        'near_creek': proximity_to_creek < 1.0,
        'holds_above_creek': c['low'] >= creek_level - atr * 0.2,
        'declining_volume': c['volume'] < sos_event['volume_ratio'] * avg_volume * 0.6,
        'narrow_spread': spread < atr * 0.9,
        'bullish_close': close_position > 0.4,
        'pullback_from_sos': c['close'] < sos_event['price_high'],
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'LPS',
            'phase': 'D',
            'index': i,
            'price_low': c['low'],
            'price_close': c['close'],
            'distance_from_creek': c['low'] - creek_level,
            'volume_ratio': c['volume'] / avg_volume,
            'confidence': 0.80 * (sum(conditions.values()) / len(conditions)),
            'trade_action': 'BUY',
            'stop_loss': creek_level - atr * 0.5,
            'conditions': conditions
        }
    
    return None
```

### 4.5 Phase E — Markup Begins

#### 4.5.1 Back-Up to the Edge of the Creek (BU/LPS)

**Definition**: The final pullback after price has broken out of the accumulation range. Price pulls back to the Creek area one last time before the sustained markup begins.

| Attribute | Description |
|---|---|
| **Price Action** | Pullback to Creek area from above; may be the same as LPS |
| **Volume** | Low — supply is exhausted |
| **Significance** | Last opportunity to enter before sustained markup |
| **Risk** | If price falls back below Creek on high volume, accumulation may have failed |

```
Phase E — Markup Beginning
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                                          ╱
                                         ╱
                                        ╱  Markup continues
                                SOS    ╱
                               ╱  ╲   ╱
                              ╱    ╲ ╱
  Creek ─────────────────────╱──────╳─── BU (Back-Up)
                            ╱      LPS
  ════════════════════════╱════════════
                         ╱
        Accumulation    ╱
        Range          ╱
                      ╱
  ════════════════════════════════════
  
  Volume at BU: LOW (confirms supply exhaustion)
  Entry: Buy at BU with SL below Creek
  Target: Projected move from Cause measurement
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. Volume Analysis at Each Phase

### 5.1 Volume Signature Table

| Event | Expected Volume | vs 20-SMA | Spread | Close Position | Key Interpretation |
|---|---|---|---|---|---|
| PS | Increased | 1.5–2.5x | Wide | Mid-Upper | First demand appearance |
| SC | Extreme | 2.5–5.0x | Very Wide | Low-Mid | Capitulation selling, CM buying |
| AR | Moderate-High | 1.0–2.0x | Wide | Upper | Short covering + bottom fishing |
| ST | Decreased | 0.5–0.8x vs SC | Narrower | Above mid | Supply drying up |
| Phase B tests | Decreasing | 0.3–0.7x vs SC | Narrowing | Variable | Progressive absorption |
| Spring | Variable | 0.5–2.0x | Moderate | Recovers | Shakeout — supply tested |
| Test of Spring | Low | 0.3–0.6x | Narrow | Upper | Supply confirmed exhausted |
| SOS | High | 1.5–3.0x | Wide | Near high | Demand overwhelms supply |
| LPS | Low | 0.3–0.6x | Narrow | Above mid | No supply at higher levels |
| BU | Low | 0.3–0.5x | Narrow | Above mid | Final supply test |

### 5.2 Volume Trend During Accumulation

$$
V_{\text{tests}}(k) = V_{\text{SC}} \cdot e^{-\lambda k}
$$

Where:
- $V_{\text{tests}}(k)$ = volume at the $k$-th test of support
- $V_{\text{SC}}$ = volume at the Selling Climax
- $\lambda$ = decay rate (typically 0.3–0.6)

The exponential decay of volume on successive tests is one of the strongest confirmations of accumulation.

### 5.3 Volume Divergence Score

$$
\text{VDS}(t) = \frac{\sum_{i=1}^{n} [V_{\text{test},i} \cdot \mathbb{1}(P_{\text{test},i} \leq P_{\text{SC}} + \epsilon)]}{\sum_{i=1}^{n} [V_{\text{rally},i} \cdot \mathbb{1}(P_{\text{rally},i} \geq P_{\text{AR}} - \epsilon)]}
$$

Where:
- VDS < 0.5: Strong accumulation signal (declining volume on tests vs rallies)
- VDS 0.5–1.0: Moderate signal
- VDS > 1.0: Weak or no accumulation

---

## 6. Real-Time Identification

### 6.1 Progressive Phase Detection

In real-time trading, accumulation must be identified progressively as events unfold:

```
Real-Time Accumulation Detection State Machine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

State 0: WATCHING (no events detected)
  │
  ├── Detect PS → State 1: PS_DETECTED (10% confidence)
  │
State 1: PS_DETECTED
  │
  ├── Detect SC → State 2: SC_DETECTED (25% confidence)
  ├── Timeout (30 bars) → State 0: WATCHING
  │
State 2: SC_DETECTED
  │
  ├── Detect AR → State 3: RANGE_FORMING (40% confidence)
  ├── New low below SC → State 0: WATCHING (failed)
  │
State 3: RANGE_FORMING
  │
  ├── Detect ST with lower volume → State 4: PHASE_B (55% confidence)
  ├── Break below SC on high volume → State 0: WATCHING (failed)
  │
State 4: PHASE_B
  │
  ├── Multiple STs with decreasing vol → State 5: SUPPLY_ABSORBED (65% confidence)
  ├── Break below SC on high volume → State 0: WATCHING (failed)
  ├── Timeout (200+ bars) → Review for re-distribution
  │
State 5: SUPPLY_ABSORBED
  │
  ├── Detect Spring → State 6: SPRING_DETECTED (80% confidence)
  ├── Price breaks above Creek → State 7: SOS_DETECTED (70% confidence)
  │
State 6: SPRING_DETECTED
  │
  ├── Test of Spring (higher low, low vol) → State 8: CONFIRMED (90% confidence)
  ├── Price falls below Spring low → State 4: PHASE_B (reduced confidence)
  │
State 7: SOS_DETECTED
  │
  ├── LPS pullback to Creek → State 8: CONFIRMED (85% confidence)
  ├── Price falls back into range → State 4: PHASE_B (reduced confidence)
  │
State 8: CONFIRMED ACCUMULATION
  │
  ├── BU successful → State 9: MARKUP (95% confidence)
  ├── Price falls back below Creek on volume → State 4: PHASE_B (reassess)
  │
State 9: MARKUP_INITIATED
  └── Phase complete — transition to Markup tracking

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Real-Time Confidence Calculation

$$
C_{\text{accum}}(t) = \sum_{e \in E_{\text{detected}}} w_e \cdot q_e \cdot d_e(t)
$$

Where:
- $E_{\text{detected}}$ = set of detected Wyckoff events
- $w_e$ = weight of event $e$ (see table below)
- $q_e$ = quality score of event $e$ [0, 1]
- $d_e(t)$ = time decay factor: $d_e(t) = e^{-\mu(t - t_e)}$ where $\mu$ = decay rate

| Event | Weight ($w_e$) | Notes |
|---|---|---|
| PS | 0.05 | Very early, low weight |
| SC | 0.15 | Essential but needs confirmation |
| AR | 0.10 | Confirms range boundaries |
| ST (1st) | 0.10 | First confirmation of supply absorption |
| ST (subsequent) | 0.05 each | Additional confirmation |
| Spring | 0.25 | Highest weight — most significant event |
| Test of Spring | 0.15 | Confirms Spring validity |
| SOS | 0.10 | Breakout confirmation |
| LPS | 0.05 | Final entry confirmation |
| **Total possible** | **1.00** | |

---

## 7. Mathematical Models

### 7.1 Accumulation Range Parameters

Given the detected accumulation range:

$$
\text{Range} = [P_{\text{ice}}, P_{\text{creek}}]
$$

Where:
- $P_{\text{ice}} = P_{\text{SC\_low}} \pm \epsilon$ (support level)
- $P_{\text{creek}} = P_{\text{AR\_high}} \pm \epsilon$ (resistance level)
- $\epsilon$ = tolerance zone (typically 0.2 ATR)

**Range Height:**
$$
H_{\text{range}} = P_{\text{creek}} - P_{\text{ice}}
$$

**Range Duration (in bars):**
$$
T_{\text{range}} = t_{\text{SOS}} - t_{\text{PS}}
$$

### 7.2 Price Target Projection

**Method 1: Point-and-Figure Count (Modernized)**

$$
\text{Target}_{\text{up}} = P_{\text{ice}} + \left(\frac{T_{\text{range}}}{T_{\text{bar}}} \times H_{\text{range}} \times \alpha\right)
$$

Where:
- $T_{\text{bar}}$ = average bar duration
- $\alpha$ = scaling factor (typically 0.5–1.5, calibrated per asset)

**Method 2: ATR-Based Projection**

$$
\text{Target}_{\text{up}} = P_{\text{creek}} + k \cdot ATR \cdot \sqrt{\frac{T_{\text{range}}}{20}}
$$

Where $k$ is a multiplier:
- Conservative: $k = 2.0$
- Moderate: $k = 3.5$
- Aggressive: $k = 5.0$

**Method 3: Fibonacci Extension from Range**

$$
\text{Target}_{1.0} = P_{\text{creek}} + 1.0 \times H_{\text{range}}
$$
$$
\text{Target}_{1.618} = P_{\text{creek}} + 1.618 \times H_{\text{range}}
$$
$$
\text{Target}_{2.618} = P_{\text{creek}} + 2.618 \times H_{\text{range}}
$$

### 7.3 Spring Probability Model

The probability that a break below support is a Spring (vs. a genuine breakdown):

$$
P(\text{Spring} | \text{Break Below}) = \sigma\left(\beta_0 + \beta_1 x_V + \beta_2 x_D + \beta_3 x_T + \beta_4 x_S\right)
$$

Where $\sigma$ is the sigmoid function and:
- $x_V$ = normalized volume at the break (lower volume favors Spring)
- $x_D$ = depth of penetration (shallower favors Spring)
- $x_T$ = number of prior successful tests of support (more tests favor Spring)
- $x_S$ = slope of volume on successive tests (declining slope favors Spring)

Typical coefficients (to be calibrated):
- $\beta_0 = 0.5$, $\beta_1 = -0.8$ (lower vol = more likely Spring)
- $\beta_2 = -1.2$ (shallower = more likely Spring)
- $\beta_3 = 0.4$ (more prior tests = more likely Spring)
- $\beta_4 = -0.6$ (declining vol trend = more likely Spring)

### 7.4 Supply Exhaustion Index

Cumulative measure of supply absorption during accumulation:

$$
\text{SEI}(t) = \frac{\sum_{i=t_0}^{t} V_{\text{down}}(i) \cdot |\Delta P_{\text{down}}(i)|}{\sum_{i=t_0}^{t} V_{\text{up}}(i) \cdot |\Delta P_{\text{up}}(i)|}
$$

Where:
- $V_{\text{down}}(i)$ = volume on down bars, $V_{\text{up}}(i)$ = volume on up bars
- $\Delta P_{\text{down}}(i)$ = price change on down bars, $\Delta P_{\text{up}}(i)$ = price change on up bars
- $t_0$ = start of accumulation range

**Interpretation:**
- SEI > 2.0 at start (heavy supply) → SEI declining toward 1.0 → SEI < 0.5 near end (supply exhausted)
- The transition from SEI > 1.0 to SEI < 1.0 marks the critical turning point

---

## 8. Accumulation vs Continued Downtrend

### 8.1 Key Differentiators

One of the most critical skills is distinguishing genuine accumulation from a pause in a continuing downtrend (re-distribution).

| Feature | Accumulation | Re-Distribution (Continued Downtrend) |
|---|---|---|
| Volume on SC | Extreme (climactic) | Moderate (no capitulation) |
| Volume trend on tests | Decreasing | Flat or increasing |
| Spring behavior | Quick reversal, holds | Fails — price continues lower |
| Range duration | Proportional to prior decline | Often short, weak |
| Rallies within range | Strong, on increasing volume | Weak, on low volume |
| Close positions on tests | Above midpoint | Below midpoint |
| Higher lows forming | Yes, progressively | No — each test as deep or deeper |
| SOS quality | Strong breakout, high volume | Weak breakout, low volume (fails) |

### 8.2 Failure Detection Algorithm

```python
def detect_accumulation_failure(state, candle, avg_volume, atr):
    """
    Detect if the accumulation pattern is failing (actually re-distribution).
    
    Returns:
        dict with failure signal and new state, or None if no failure
    """
    failures = []
    
    # Failure 1: Price breaks below Spring low on high volume
    if state.spring_event and candle['low'] < state.spring_event['price_low']:
        if candle['volume'] > avg_volume * 1.5:
            failures.append({
                'type': 'SPRING_FAILURE',
                'severity': 'CRITICAL',
                'description': 'Price broke below Spring low on high volume',
                'action': 'EXIT_ALL_LONGS'
            })
    
    # Failure 2: SOS fails — price falls back below Creek on high volume
    if state.sos_event and candle['close'] < state.creek_level:
        if candle['volume'] > avg_volume * 1.2:
            failures.append({
                'type': 'SOS_FAILURE',
                'severity': 'HIGH',
                'description': 'SOS failed — price back below Creek with volume',
                'action': 'EXIT_OR_REDUCE'
            })
    
    # Failure 3: Volume increasing on successive tests (supply not being absorbed)
    if len(state.test_volumes) >= 3:
        vol_slope = np.polyfit(range(len(state.test_volumes)), state.test_volumes, 1)[0]
        if vol_slope > 0:
            failures.append({
                'type': 'INCREASING_SUPPLY',
                'severity': 'MEDIUM',
                'description': 'Volume increasing on tests — supply not being absorbed',
                'action': 'REDUCE_CONFIDENCE'
            })
    
    # Failure 4: Bearish closes on tests (closing at lows)
    if state.recent_tests:
        bearish_closes = sum(1 for t in state.recent_tests[-3:] if t['close_position'] < 0.3)
        if bearish_closes >= 2:
            failures.append({
                'type': 'BEARISH_TESTS',
                'severity': 'MEDIUM',
                'description': 'Tests showing bearish close positions',
                'action': 'REDUCE_CONFIDENCE'
            })
    
    # Failure 5: Time exceeded without progression
    if state.bars_in_phase > state.max_phase_duration:
        failures.append({
            'type': 'TIME_EXHAUSTION',
            'severity': 'LOW',
            'description': f'Phase duration exceeded {state.max_phase_duration} bars',
            'action': 'REASSESS'
        })
    
    return failures if failures else None
```

### 8.3 Scoring: Accumulation vs Re-Distribution

$$
P(\text{Accum}) = \frac{1}{1 + e^{-z}}
$$

Where:

$$
z = w_1 \cdot [\text{Vol declining on tests}] + w_2 \cdot [\text{Spring success}] + w_3 \cdot [\text{Higher lows}] + w_4 \cdot [\text{SOS strength}] - w_5 \cdot [\text{Failure signals}]
$$

Default weights: $w_1 = 2.0, w_2 = 3.0, w_3 = 1.5, w_4 = 2.5, w_5 = 4.0$

---

## 9. Entry/Exit Logic

### 9.1 Entry Points (Ranked by Quality)

#### Entry 1: Test of Spring (Highest Quality)

```python
def entry_test_of_spring(spring_event, test_event, atr, range_height):
    """
    Highest quality entry — after Spring is confirmed by Test.
    """
    entry_price = test_event['price_close']
    stop_loss = spring_event['price_low'] - atr * 0.3
    risk = entry_price - stop_loss
    
    # Targets based on range projection
    target_1 = entry_price + range_height * 1.0   # Conservative
    target_2 = entry_price + range_height * 1.618  # Moderate
    target_3 = entry_price + range_height * 2.618  # Aggressive
    
    return {
        'entry_type': 'TEST_OF_SPRING',
        'direction': 'LONG',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'risk': risk,
        'targets': [target_1, target_2, target_3],
        'risk_reward': [(t - entry_price) / risk for t in [target_1, target_2, target_3]],
        'position_size_pct': 2.0,  # Full risk allocation
        'confidence': 0.90,
        'max_risk_pct': 2.0,
    }
```

#### Entry 2: Spring (Direct Entry)

```python
def entry_spring_direct(spring_event, atr, range_height):
    """
    Aggressive entry directly on Spring bar.
    Best for Type 3 springs with quick reversal.
    """
    entry_price = spring_event['price_close']
    stop_loss = spring_event['price_low'] - atr * 0.5
    risk = entry_price - stop_loss
    
    return {
        'entry_type': 'SPRING_DIRECT',
        'direction': 'LONG',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'risk': risk,
        'targets': [
            entry_price + range_height * 0.8,
            entry_price + range_height * 1.5,
            entry_price + range_height * 2.5,
        ],
        'position_size_pct': 1.5,  # Reduced due to no test confirmation
        'confidence': 0.75,
        'max_risk_pct': 1.5,
        'note': 'Consider adding on successful Test'
    }
```

#### Entry 3: Last Point of Support (LPS)

```python
def entry_lps(lps_event, creek_level, atr, range_height):
    """
    Entry on pullback after SOS breakout.
    Good for traders who missed the Spring.
    """
    entry_price = lps_event['price_close']
    stop_loss = creek_level - atr * 0.5
    risk = entry_price - stop_loss
    
    return {
        'entry_type': 'LPS',
        'direction': 'LONG',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'risk': risk,
        'targets': [
            entry_price + range_height * 1.0,
            entry_price + range_height * 2.0,
            entry_price + range_height * 3.0,
        ],
        'position_size_pct': 1.5,
        'confidence': 0.80,
        'max_risk_pct': 1.5,
    }
```

#### Entry 4: Back-Up (BU)

```python
def entry_backup(bu_price, creek_level, atr, range_height):
    """
    Entry on final pullback to Creek from above.
    Latest entry with lowest risk but reduced R:R.
    """
    entry_price = bu_price
    stop_loss = creek_level - atr * 0.3
    risk = entry_price - stop_loss
    
    return {
        'entry_type': 'BACKUP',
        'direction': 'LONG',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'risk': risk,
        'targets': [
            entry_price + range_height * 0.8,
            entry_price + range_height * 1.618,
        ],
        'position_size_pct': 1.0,
        'confidence': 0.85,
        'max_risk_pct': 1.0,
    }
```

### 9.2 Position Scaling Strategy

```
Entry Scaling During Accumulation:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total planned position: 100%

Entry 1: Spring (Direct)         → 30% of total position
Entry 2: Test of Spring          → 30% of total position  (add-on)
Entry 3: LPS or BU               → 20% of total position  (add-on)
Entry 4: Pullback during Markup   → 20% of total position  (add-on)

Average Entry Price: Weighted average of all entries
Combined Stop Loss: Below Spring low (or below Creek for later entries)
Combined R:R: Should be >= 3:1 for the complete position

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 9.3 Exit Logic

```python
def accumulation_exit_logic(position, candle, market_state, atr):
    """
    Exit logic for positions entered during accumulation.
    """
    exit_signals = []
    
    # Hard stop loss
    if candle['low'] <= position['stop_loss']:
        exit_signals.append({
            'type': 'STOP_LOSS',
            'action': 'EXIT_ALL',
            'price': position['stop_loss'],
            'reason': 'Stop loss triggered'
        })
    
    # Target 1 — partial exit
    if candle['high'] >= position['targets'][0] and not position.get('t1_hit'):
        exit_signals.append({
            'type': 'TARGET_1',
            'action': 'EXIT_50PCT',
            'price': position['targets'][0],
            'reason': 'First target reached — take partial profits',
            'move_stop': 'BREAKEVEN'
        })
    
    # Target 2 — additional exit
    if candle['high'] >= position['targets'][1] and not position.get('t2_hit'):
        exit_signals.append({
            'type': 'TARGET_2',
            'action': 'EXIT_30PCT',
            'price': position['targets'][1],
            'reason': 'Second target reached',
            'move_stop': position['targets'][0]  # Trail to T1
        })
    
    # Target 3 — final exit
    if len(position['targets']) > 2 and candle['high'] >= position['targets'][2]:
        exit_signals.append({
            'type': 'TARGET_3',
            'action': 'EXIT_REMAINING',
            'price': position['targets'][2],
            'reason': 'Final target reached'
        })
    
    # Phase change — distribution detected
    if market_state.phase == 'DISTRIBUTION':
        exit_signals.append({
            'type': 'PHASE_CHANGE',
            'action': 'EXIT_ALL',
            'price': candle['close'],
            'reason': 'Distribution phase detected — exit longs'
        })
    
    # Trailing stop during markup
    if market_state.phase == 'MARKUP' and position.get('t1_hit'):
        trail_stop = candle['high'] - atr * 2.5
        if trail_stop > position['stop_loss']:
            exit_signals.append({
                'type': 'TRAIL_STOP_UPDATE',
                'action': 'UPDATE_STOP',
                'new_stop': trail_stop,
                'reason': 'Trailing stop tightened during markup'
            })
    
    return exit_signals
```

---

## 10. Risk Parameters

### 10.1 Risk Parameters by Entry Type

| Entry Type | Max Risk (% Account) | Typical SL (ATR) | Min R:R | Max Position | Confidence Threshold |
|---|---|---|---|---|---|
| Spring (Type 3) | 2.0% | 0.5–1.0 | 4:1 | 30% of planned | 0.80 |
| Spring (Type 2) | 1.5% | 1.0–1.5 | 3:1 | 25% of planned | 0.70 |
| Spring (Type 1) | 0.5% | 1.5–2.5 | 5:1 | 10% of planned | 0.60 |
| Test of Spring | 2.0% | 0.5–1.0 | 3:1 | 30% of planned | 0.85 |
| SOS Breakout | 1.5% | 1.5–2.0 | 2:1 | 20% of planned | 0.70 |
| LPS | 1.5% | 0.5–1.0 | 3:1 | 20% of planned | 0.75 |
| BU | 1.0% | 0.3–0.8 | 2:1 | 15% of planned | 0.80 |

### 10.2 Dynamic Risk Adjustment

$$
R_{\text{adjusted}} = R_{\text{base}} \times \min\left(1.0, \frac{C_{\text{accum}}}{C_{\text{threshold}}}\right) \times F_{\text{volatility}} \times F_{\text{correlation}}
$$

Where:
- $R_{\text{base}}$ = base risk percentage from table above
- $C_{\text{accum}}$ = accumulation confidence score
- $C_{\text{threshold}}$ = minimum confidence threshold (0.65)
- $F_{\text{volatility}}$ = volatility adjustment factor: $F_V = \frac{ATR_{\text{historical}}}{ATR_{\text{current}}}$ (reduce risk in high volatility)
- $F_{\text{correlation}}$ = correlation adjustment (reduce if correlated positions exist)

### 10.3 Maximum Drawdown Limits

| Timeframe | Max Drawdown | Action |
|---|---|---|
| Per trade | Based on SL | Automatic exit |
| Per day | 3% of account | Stop trading for the day |
| Per week | 5% of account | Reduce position sizes by 50% |
| Per month | 8% of account | Stop trading, review system |
| Total | 15% of account | Full system shutdown, manual review |

---

## 11. Execution Flow

### 11.1 Complete Accumulation Detection Algorithm

```python
class AccumulationDetector:
    """
    Complete state machine for detecting Wyckoff accumulation in real-time.
    """
    
    def __init__(self, config):
        self.config = config
        self.state = 'WATCHING'
        self.confidence = 0.0
        self.events = []
        self.range_support = None
        self.range_resistance = None
        self.phase_start_bar = None
        
    def update(self, candle, index, avg_volume, atr, trend):
        """
        Process a new candle and update accumulation detection state.
        
        Returns:
            dict: Current state, confidence, events, and any trade signals
        """
        result = {
            'state': self.state,
            'confidence': self.confidence,
            'new_events': [],
            'signals': [],
            'phase': None
        }
        
        if self.state == 'WATCHING':
            ps = detect_preliminary_support(
                self.candles, index, avg_volume, atr, trend
            )
            if ps:
                self.events.append(ps)
                self.state = 'PS_DETECTED'
                self.confidence = 0.10
                self.phase_start_bar = index
                result['new_events'].append(ps)
        
        elif self.state == 'PS_DETECTED':
            sc = detect_selling_climax(
                self.candles, index, avg_volume, avg_volume,
                atr, self._get_event('PS')
            )
            if sc:
                self.events.append(sc)
                self.state = 'SC_DETECTED'
                self.confidence = 0.25
                self.range_support = sc['range_bottom']
                result['new_events'].append(sc)
            elif index - self.phase_start_bar > 30:
                self._reset()
        
        elif self.state == 'SC_DETECTED':
            ar = detect_automatic_rally(
                self.candles, index, self._get_event('SC'),
                avg_volume, atr
            )
            if ar:
                self.events.append(ar)
                self.state = 'RANGE_FORMING'
                self.confidence = 0.40
                self.range_resistance = ar['range_top']
                result['new_events'].append(ar)
            elif candle['low'] < self.range_support - atr * 2:
                self._reset()  # New low far below SC — not accumulation
        
        elif self.state == 'RANGE_FORMING':
            st = detect_secondary_test(
                self.candles, index, self._get_event('SC'),
                self._get_event('AR'), avg_volume, atr
            )
            if st:
                self.events.append(st)
                self.state = 'PHASE_B'
                self.confidence = 0.55
                result['new_events'].append(st)
        
        elif self.state == 'PHASE_B':
            # Check for additional STs
            st = detect_secondary_test(
                self.candles, index, self._get_event('SC'),
                self._get_event('AR'), avg_volume, atr
            )
            if st:
                self.events.append(st)
                result['new_events'].append(st)
                # Update confidence based on quality
                if st['interpretation'] == 'STRONG':
                    self.confidence = min(0.70, self.confidence + 0.05)
            
            # Check for Spring
            spring = detect_spring(
                self.candles, index, self.range_support,
                self.range_resistance, avg_volume, atr,
                [e for e in self.events if e['event'] == 'ST']
            )
            if spring:
                self.events.append(spring)
                self.state = 'SPRING_DETECTED'
                self.confidence = 0.80
                result['new_events'].append(spring)
                
                # Generate trade signal for Type 3 Spring
                if spring['spring_type'] == 3:
                    result['signals'].append({
                        'action': 'BUY',
                        'type': 'SPRING_TYPE3',
                        'entry': candle['close'],
                        'stop_loss': spring['stop_loss'],
                        'confidence': spring['confidence']
                    })
            
            # Check for SOS without Spring
            sos = detect_sign_of_strength(
                self.candles, index, self.range_resistance,
                avg_volume, atr,
                self.range_resistance - self.range_support
            )
            if sos:
                self.events.append(sos)
                self.state = 'SOS_DETECTED'
                self.confidence = 0.70
                result['new_events'].append(sos)
        
        elif self.state == 'SPRING_DETECTED':
            # Look for Test of Spring
            test = detect_test_of_spring(
                self.candles, index, self._get_event('SPRING'),
                avg_volume, atr
            )
            if test:
                self.events.append(test)
                self.state = 'CONFIRMED'
                self.confidence = 0.90
                result['new_events'].append(test)
                result['signals'].append({
                    'action': 'BUY',
                    'type': 'TEST_OF_SPRING',
                    'entry': candle['close'],
                    'stop_loss': test['stop_loss'],
                    'confidence': test['confidence']
                })
            
            # Check for failure
            spring_low = self._get_event('SPRING')['price_low']
            if candle['close'] < spring_low and candle['volume'] > avg_volume * 1.5:
                self.state = 'PHASE_B'
                self.confidence = max(0.30, self.confidence - 0.30)
        
        elif self.state == 'SOS_DETECTED':
            # Look for LPS
            lps = detect_last_point_of_support(
                self.candles, index, self._get_event('SOS'),
                self.range_resistance, avg_volume, atr
            )
            if lps:
                self.events.append(lps)
                self.state = 'CONFIRMED'
                self.confidence = 0.85
                result['new_events'].append(lps)
                result['signals'].append({
                    'action': 'BUY',
                    'type': 'LPS',
                    'entry': candle['close'],
                    'stop_loss': lps['stop_loss'],
                    'confidence': lps['confidence']
                })
        
        elif self.state == 'CONFIRMED':
            # Accumulation confirmed — look for markup entry
            self.confidence = 0.90
            result['phase'] = 'ACCUMULATION_CONFIRMED'
        
        result['state'] = self.state
        result['confidence'] = self.confidence
        return result
    
    def _get_event(self, event_type):
        """Get the most recent event of a given type."""
        for e in reversed(self.events):
            if e['event'] == event_type:
                return e
        return None
    
    def _reset(self):
        """Reset to watching state."""
        self.state = 'WATCHING'
        self.confidence = 0.0
        self.events = []
        self.range_support = None
        self.range_resistance = None
        self.phase_start_bar = None
```

---

## 12. Forex-Specific Accumulation

### 12.1 Session-Based Accumulation Patterns

In Forex, accumulation frequently maps to session transitions:

| Pattern | Description | Frequency | Best Pairs |
|---|---|---|---|
| **Asian Range Accumulation** | Price consolidates in tight range during Asian session, Springs below Asian low at London open | Very common | EUR/USD, GBP/USD |
| **London Accumulation** | Early London session creates range, Spring at London–NY overlap | Common | EUR/USD, EUR/GBP |
| **Weekly Accumulation** | Monday–Tuesday range, Spring mid-week, SOS Thursday–Friday | Moderate | All majors |
| **News-Driven Accumulation** | Range forms before high-impact news, SC/Spring on news release | Moderate | Affected pairs |

### 12.2 Tick Volume Adjustments for Forex

Since Forex uses tick volume, adjustments are needed:

$$
V_{\text{adjusted}}(t) = V_{\text{tick}}(t) \times \frac{\text{Session\_Weight}(t)}{\text{Max\_Session\_Weight}}
$$

Session weights:
- Asian: 0.5
- London: 1.0
- London/NY overlap: 1.0
- NY afternoon: 0.7
- Late NY: 0.3

---

## 13. Crypto-Specific Accumulation

### 13.1 On-Chain Confirmation of Accumulation

| On-Chain Metric | Accumulation Signal | Confidence Boost |
|---|---|---|
| Exchange outflows > inflows | Coins moving to cold storage (long-term holding) | +10% |
| Whale addresses increasing balance | Large holders accumulating | +15% |
| Miner reserve increasing | Miners holding, not selling | +5% |
| Stablecoin reserves on exchanges increasing | Buying power accumulating | +10% |
| Funding rate deeply negative | Bearish sentiment (contrarian bullish) | +5% |
| Open interest declining | Leverage washing out | +5% |

### 13.2 Crypto Volume Filtering

```python
def filter_wash_trading(exchange_volumes, known_wash_pct):
    """
    Filter suspected wash trading volume from crypto exchanges.
    
    Parameters:
        exchange_volumes: dict of {exchange_name: volume}
        known_wash_pct: dict of {exchange_name: estimated_wash_pct}
    
    Returns:
        float: estimated real volume
    """
    real_volume = 0
    for exchange, volume in exchange_volumes.items():
        wash_pct = known_wash_pct.get(exchange, 0.0)
        real_volume += volume * (1 - wash_pct)
    
    return real_volume
```

### 13.3 Crypto Accumulation Timeframes

| Timeframe | Use | Notes |
|---|---|---|
| 1W | Macro accumulation (months-long) | Best for spot investing |
| 1D | Intermediate accumulation (weeks-long) | Swing trading |
| 4H | Short-term accumulation (days-long) | Active trading |
| 1H | Intraday accumulation | Scalp/day trading |
| 15M | Micro accumulation | Scalping with leverage |

---

## 14. Common Mistakes and Pitfalls

### 14.1 Mistakes to Avoid

| # | Mistake | Consequence | Solution |
|---|---|---|---|
| 1 | Entering on SC directly | SC is NOT the entry — it defines the range | Wait for Spring or SOS |
| 2 | Ignoring volume | Phase identification without volume is unreliable | Volume is non-negotiable |
| 3 | Forcing the pattern | Not every range is accumulation | Require all key events |
| 4 | Wrong timeframe | Accumulation on 5M may be noise on 4H | Always confirm on HTF |
| 5 | Ignoring failed springs | Type 1 springs that don't reverse can lead to breakdown | Use stop losses |
| 6 | Premature SOS identification | Not every rally above resistance is SOS | Require volume + spread confirmation |
| 7 | Over-leveraging Spring entries | Spring entries can still fail | Risk max 2% per trade |
| 8 | Ignoring broader context | Accumulation in a macro downtrend has lower success | Check HTF trend |

### 14.2 Pattern Quality Checklist

Before trading an accumulation pattern, verify:

```
Accumulation Quality Checklist:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ ] Prior downtrend exists (minimum 2x the range height)
[ ] Selling Climax has extreme volume (>= 2.5x average)
[ ] Automatic Rally defines clear resistance
[ ] Secondary Test(s) show declining volume
[ ] Range has been in place for minimum 20 bars
[ ] Volume on support tests is progressively decreasing
[ ] Spring or SOS event detected
[ ] If Spring: Test occurred with lower volume and higher low
[ ] If SOS: Volume expanded significantly on breakout
[ ] Higher timeframe trend is not strongly bearish
[ ] No conflicting signals from other analysis methods

Score: Count checked items / total items
Minimum score to trade: 7/11 (64%)
High confidence: 9+/11 (82%+)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 15. References

### 15.1 Primary Sources

1. Wyckoff, R.D. (1931). *The Richard D. Wyckoff Method of Trading and Investing in Stocks*. Wyckoff Associates.
2. Evans, R. (1969). *Wyckoff Course Notes — Accumulation and Distribution Schematics*. Stock Market Institute.
3. Pruden, H.O. (2007). *The Three Skills of Top Trading*. Wiley. — Chapter 4: "The Wyckoff Method of Market Analysis."

### 15.2 Modern Adaptations

4. Williams, T. (2005). *Master the Markets*. TradeGuider Systems. — VSA confirmation of accumulation events.
5. Weis, D.H. (2013). *Trades About to Happen*. Wiley. — Modern wave-volume approach to accumulation.
6. Schroeder, G. (2015). "Wyckoff Accumulation Schematics #1 and #2." *StockCharts.com Wyckoff Power Charting Series*.

### 15.3 Research Papers

7. Lo, A.W. & Wang, J. (2000). "Trading Volume: Definitions, Data Analysis, and Implications of Portfolio Theory." *Review of Financial Studies*, 13(2), 257–300.
8. Blume, L., Easley, D., & O'Hara, M. (1994). "Market Statistics and Technical Analysis: The Role of Volume." *Journal of Finance*, 49(1), 153–181.

---

> **Next Document**: `02_distribution_schematic.md` — Detailed Distribution Phase Analysis
