# Volume Spread Analysis (VSA) — Wyckoff Volume Integration

> **Module**: Axis 1 — Trading Strategies
> **Topic**: 02 — Wyckoff Method & Market Structure
> **File**: 04_wyckoff_volume_analysis.md
> **Version**: 1.0
> **Last Updated**: 2026-04-12
> **Author**: NTT Multi-Agent AI Trading System — Knowledge Base Team

---

## Table of Contents

1. [Introduction to Volume Spread Analysis](#1-introduction-to-volume-spread-analysis)
2. [VSA Principles](#2-vsa-principles)
3. [Key VSA Signals](#3-key-vsa-signals)
4. [Effort vs Result Analysis](#4-effort-vs-result-analysis)
5. [Volume at Support and Resistance](#5-volume-at-support-and-resistance)
6. [Integration with Wyckoff Phases](#6-integration-with-wyckoff-phases)
7. [Mathematical Models](#7-mathematical-models)
8. [Algorithmic Implementation](#8-algorithmic-implementation)
9. [Core Logic — Entry/Exit](#9-core-logic--entryexit)
10. [Risk Parameters](#10-risk-parameters)
11. [Execution Flow](#11-execution-flow)
12. [Forex and Crypto Adaptations](#12-forex-and-crypto-adaptations)
13. [References](#13-references)

---

## 1. Introduction to Volume Spread Analysis

### 1.1 Origin and History

Volume Spread Analysis (VSA) was developed by **Tom Williams** (1929–2011), a former syndicate trader who systematized Richard Wyckoff's tape-reading principles into a methodology that could be applied to modern bar charts. Williams published his findings in *Master the Markets* (1993, revised 2005) and built the TradeGuider software to automate VSA detection.

### 1.2 Core Philosophy

VSA operates on a single fundamental premise:

> **The market is driven by professional money (Smart Money/Composite Man). Professional activity is revealed through the relationship between VOLUME, SPREAD (range), and CLOSE POSITION on each bar.**

Key insight: Professionals leave "footprints" on the chart that cannot be hidden if you know how to read the volume-spread-close relationship.

### 1.3 The Three Components

| Component | Definition | What It Reveals |
|---|---|---|
| **Volume** | Number of shares/contracts/ticks traded | Effort (activity level) |
| **Spread** | High minus Low of the bar (range) | Result (price range achieved) |
| **Close Position** | Where the close falls within the bar range | Control (who won: buyers or sellers) |

$$
\text{Close Position} = \frac{C - L}{H - L} \in [0, 1]
$$

Where:
- 0.0 = close at low (sellers in control)
- 0.5 = close at midpoint (indecision)
- 1.0 = close at high (buyers in control)

### 1.4 The VSA Matrix

```
The VSA Analysis Matrix:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                    Volume LOW          Volume AVERAGE      Volume HIGH
                   ─────────────       ─────────────────   ──────────────────
Spread WIDE     │ Ease of Movement   │ Normal Activity   │ Climactic Action  │
Close HIGH      │ (Bullish — no      │ (Healthy demand)  │ (Absorption OR    │
                │  resistance)       │                   │  climax buying)   │
                ├────────────────────┼───────────────────┼───────────────────┤
Spread WIDE     │ Ease of Movement   │ Normal Activity   │ Climactic Action  │
Close LOW       │ (Bearish — no      │ (Healthy supply)  │ (Absorption OR    │
                │  support)          │                   │  climax selling)  │
                ├────────────────────┼───────────────────┼───────────────────┤
Spread NARROW   │ No Demand / No     │ Testing           │ Stopping Volume   │
Close HIGH      │ Supply (depends    │ (Professional     │ (Absorption —     │
                │ on context)        │  testing supply)  │  demand absorbing │
                │                    │                   │  supply)          │
                ├────────────────────┼───────────────────┼───────────────────┤
Spread NARROW   │ No Demand / No     │ Testing           │ Stopping Volume   │
Close LOW       │ Supply (depends    │ (Professional     │ (Absorption —     │
                │ on context)        │  testing demand)  │  supply absorbing │
                │                    │                   │  demand)          │
                └────────────────────┴───────────────────┴───────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 2. VSA Principles

### 2.1 Principle 1: Markets Move on Supply and Demand

Professional operators accumulate or distribute positions over time. Their activity creates specific volume-spread patterns that are readable.

### 2.2 Principle 2: Volume is Activity

Volume represents the level of professional interest in a price level:
- **High volume** = professionals are active (either buying OR selling — context determines which)
- **Low volume** = professionals are absent (market is vulnerable to the next professional action)

### 2.3 Principle 3: The Close Reveals Intent

The close position within the bar is the most important piece of information:
- **Close at high**: Buyers won control of that bar
- **Close at low**: Sellers won control of that bar
- **Close at mid**: Neither side has clear control

### 2.4 Principle 4: Context is King

The same volume-spread pattern means different things in different contexts:
- High volume with wide spread down on a rally = **distribution** (bearish)
- High volume with wide spread down after decline = **selling climax** (potentially bullish)
- Low volume narrow bar in uptrend = **no supply** (bullish continuation)
- Low volume narrow bar in downtrend = **no demand** (bearish continuation)

### 2.5 Principle 5: Weakness Appears on Up Bars, Strength Appears on Down Bars

This is counter-intuitive but critical:
- **Hidden weakness**: High volume, wide spread UP bar that closes OFF the high → supply entering
- **Hidden strength**: High volume, wide spread DOWN bar that closes OFF the low → demand entering

---

## 3. Key VSA Signals

### 3.1 No Demand

**Definition**: A bar that shows the absence of professional buying interest. The market cannot continue up without demand.

**Characteristics:**
- Spread: Narrow (below average)
- Volume: Below average (often below previous 2 bars)
- Close: At or below midpoint
- Context: Occurs during up-move or at resistance
- Bar type: Up bar (close > open) but weak

**Signal**: Bearish (in uptrend or at resistance)

$$
\text{No Demand} = \begin{cases}
\text{true} & \text{if } V < \bar{V} \times 0.7 \\
& \text{AND } \text{Spread} < \overline{\text{Spread}} \times 0.8 \\
& \text{AND } C > O \text{ (up bar)} \\
& \text{AND CPos} < 0.6 \\
& \text{AND context} = \text{UPTREND or RESISTANCE} \\
\text{false} & \text{otherwise}
\end{cases}
$$

```python
def detect_no_demand(candle, avg_volume, avg_spread, atr, context):
    """
    Detect No Demand bar.
    
    Context: should be at/near resistance or in an uptrend
    Signal meaning: buyers are not present — price vulnerable to decline
    """
    spread = candle['high'] - candle['low']
    close_pos = (candle['close'] - candle['low']) / spread if spread > 0 else 0.5
    is_up_bar = candle['close'] > candle['open']
    
    conditions = {
        'low_volume': candle['volume'] < avg_volume * 0.7,
        'narrow_spread': spread < avg_spread * 0.8,
        'is_up_bar': is_up_bar,
        'weak_close': close_pos < 0.6,
        'correct_context': context in ['UPTREND', 'AT_RESISTANCE', 'RALLY_IN_RANGE'],
    }
    
    # Additional confirmation: volume lower than previous 2 bars
    # (would need candle history for this)
    
    if all(conditions.values()):
        return {
            'signal': 'NO_DEMAND',
            'bias': 'BEARISH',
            'strength': (1 - candle['volume'] / avg_volume) * (1 - spread / avg_spread),
            'confidence': 0.70,
            'action': 'PREPARE_FOR_DECLINE',
            'close_position': close_pos,
        }
    return None
```

### 3.2 No Supply (No Selling Pressure)

**Definition**: A bar that shows the absence of professional selling interest. The market cannot continue down without supply.

**Characteristics:**
- Spread: Narrow (below average)
- Volume: Below average
- Close: At or above midpoint
- Context: Occurs during down-move or at support
- Bar type: Down bar (close < open) but holding

**Signal**: Bullish (in downtrend or at support)

$$
\text{No Supply} = \begin{cases}
\text{true} & \text{if } V < \bar{V} \times 0.7 \\
& \text{AND } \text{Spread} < \overline{\text{Spread}} \times 0.8 \\
& \text{AND } C < O \text{ (down bar)} \\
& \text{AND CPos} > 0.4 \\
& \text{AND context} = \text{DOWNTREND or SUPPORT} \\
\text{false} & \text{otherwise}
\end{cases}
$$

```python
def detect_no_supply(candle, avg_volume, avg_spread, atr, context):
    """
    Detect No Supply bar (no selling pressure).
    
    Context: should be at/near support or in a downtrend
    Signal meaning: sellers are absent — price vulnerable to rally
    """
    spread = candle['high'] - candle['low']
    close_pos = (candle['close'] - candle['low']) / spread if spread > 0 else 0.5
    is_down_bar = candle['close'] < candle['open']
    
    conditions = {
        'low_volume': candle['volume'] < avg_volume * 0.7,
        'narrow_spread': spread < avg_spread * 0.8,
        'is_down_bar': is_down_bar,
        'holding_close': close_pos > 0.4,
        'correct_context': context in ['DOWNTREND', 'AT_SUPPORT', 'DECLINE_IN_RANGE'],
    }
    
    if all(conditions.values()):
        return {
            'signal': 'NO_SUPPLY',
            'bias': 'BULLISH',
            'strength': (1 - candle['volume'] / avg_volume) * (1 - spread / avg_spread),
            'confidence': 0.70,
            'action': 'PREPARE_FOR_RALLY',
            'close_position': close_pos,
        }
    return None
```

### 3.3 Stopping Volume

**Definition**: High volume that appears after a sustained move, with the bar closing opposite to the prior trend direction or near the opposite extreme. Indicates that professionals are stepping in to halt the current move.

**Bullish Stopping Volume** (after decline):
- High volume on a down bar, but close near the high (demand absorbing supply)

**Bearish Stopping Volume** (after rally):
- High volume on an up bar, but close near the low (supply absorbing demand)

```python
def detect_stopping_volume(candle, avg_volume, avg_spread, atr, prior_trend, 
                           decline_length=0, rally_length=0):
    """
    Detect Stopping Volume — professional intervention to halt a move.
    """
    spread = candle['high'] - candle['low']
    close_pos = (candle['close'] - candle['low']) / spread if spread > 0 else 0.5
    
    # Bullish stopping volume (stops a decline)
    if prior_trend == 'DOWN' and decline_length >= 3:
        conditions = {
            'high_volume': candle['volume'] > avg_volume * 1.8,
            'wide_spread': spread > avg_spread * 1.0,
            'closes_off_low': close_pos > 0.4,
            'after_decline': decline_length >= 3,
        }
        
        if sum(conditions.values()) >= 3:
            return {
                'signal': 'STOPPING_VOLUME_BULLISH',
                'bias': 'BULLISH',
                'strength': (candle['volume'] / avg_volume) * close_pos,
                'confidence': 0.75,
                'action': 'POTENTIAL_BOTTOM',
                'note': 'Demand stepping in to absorb supply after decline'
            }
    
    # Bearish stopping volume (stops a rally)
    elif prior_trend == 'UP' and rally_length >= 3:
        conditions = {
            'high_volume': candle['volume'] > avg_volume * 1.8,
            'wide_spread': spread > avg_spread * 1.0,
            'closes_off_high': close_pos < 0.6,
            'after_rally': rally_length >= 3,
        }
        
        if sum(conditions.values()) >= 3:
            return {
                'signal': 'STOPPING_VOLUME_BEARISH',
                'bias': 'BEARISH',
                'strength': (candle['volume'] / avg_volume) * (1 - close_pos),
                'confidence': 0.75,
                'action': 'POTENTIAL_TOP',
                'note': 'Supply stepping in to absorb demand after rally'
            }
    
    return None
```

### 3.4 Climactic Volume

**Definition**: Extreme volume (typically > 3x average) combined with very wide spread, often marking a turning point or the exhaustion of a move.

| Type | Context | Volume | Spread | Close | Interpretation |
|---|---|---|---|---|---|
| **Selling Climax** | After decline | Very High (3-5x) | Very Wide | Near low (then reversal) | Capitulation — potential bottom |
| **Buying Climax** | After rally | Very High (3-5x) | Very Wide | Near high (then reversal) | Euphoria — potential top |
| **Climactic Shake** | At support | Very High | Wide | Recovers above open | Designed to shake out weak holders |
| **Climactic Trap** | At resistance | Very High | Wide | Falls below open | Designed to trap breakout buyers |

```python
def detect_climactic_volume(candle, prev_candles, avg_volume, avg_spread, atr, context):
    """
    Detect climactic volume events.
    """
    spread = candle['high'] - candle['low']
    close_pos = (candle['close'] - candle['low']) / spread if spread > 0 else 0.5
    vol_ratio = candle['volume'] / avg_volume
    spread_ratio = spread / avg_spread
    
    if vol_ratio < 2.5:
        return None  # Not climactic
    
    results = []
    
    # Selling Climax
    if context in ['DOWNTREND', 'AT_SUPPORT'] and candle['close'] < candle['open']:
        if close_pos > 0.3:  # Closes off the low (recovery)
            results.append({
                'signal': 'SELLING_CLIMAX',
                'bias': 'BULLISH',
                'strength': vol_ratio * spread_ratio * close_pos,
                'confidence': min(0.90, 0.6 + vol_ratio * 0.05),
                'note': 'Extreme selling exhaustion — potential bottom'
            })
    
    # Buying Climax
    if context in ['UPTREND', 'AT_RESISTANCE'] and candle['close'] > candle['open']:
        if close_pos < 0.7:  # Closes off the high
            results.append({
                'signal': 'BUYING_CLIMAX',
                'bias': 'BEARISH',
                'strength': vol_ratio * spread_ratio * (1 - close_pos),
                'confidence': min(0.90, 0.6 + vol_ratio * 0.05),
                'note': 'Extreme buying exhaustion — potential top'
            })
    
    # Climactic Shake (Spring-like)
    if context in ['AT_SUPPORT', 'IN_RANGE']:
        if candle['low'] < prev_candles[-1]['low'] and close_pos > 0.5:
            results.append({
                'signal': 'CLIMACTIC_SHAKE',
                'bias': 'BULLISH',
                'strength': vol_ratio * close_pos,
                'confidence': 0.80,
                'note': 'Shakeout with recovery — strong demand present'
            })
    
    # Climactic Trap
    if context in ['AT_RESISTANCE', 'IN_RANGE']:
        if candle['high'] > prev_candles[-1]['high'] and close_pos < 0.5:
            results.append({
                'signal': 'CLIMACTIC_TRAP',
                'bias': 'BEARISH',
                'strength': vol_ratio * (1 - close_pos),
                'confidence': 0.80,
                'note': 'Breakout trap with reversal — strong supply present'
            })
    
    return results[0] if results else None
```

### 3.5 Up-Thrust (Supply Entering on Up Bar)

**Definition**: An up bar with high volume that closes at or near its low — showing that despite buying effort, supply overwhelmed demand during the bar.

```python
def detect_upthrust(candle, avg_volume, avg_spread, context):
    """
    Detect Upthrust — hidden supply on an up bar.
    
    Bar opens low, moves high (wide spread), but closes near the low.
    High volume confirms professional selling into the rally.
    """
    spread = candle['high'] - candle['low']
    close_pos = (candle['close'] - candle['low']) / spread if spread > 0 else 0.5
    upper_wick = candle['high'] - max(candle['open'], candle['close'])
    upper_wick_pct = upper_wick / spread if spread > 0 else 0
    
    conditions = {
        'high_volume': candle['volume'] > avg_volume * 1.3,
        'wide_or_normal_spread': spread >= avg_spread * 0.8,
        'closes_near_low': close_pos < 0.35,
        'large_upper_wick': upper_wick_pct > 0.4,
        'bearish_context': context in ['UPTREND', 'AT_RESISTANCE', 'IN_DISTRIBUTION'],
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'signal': 'UPTHRUST',
            'bias': 'BEARISH',
            'strength': (candle['volume'] / avg_volume) * (1 - close_pos) * upper_wick_pct,
            'confidence': 0.78,
            'action': 'LOOK_TO_SHORT',
            'note': 'Supply overwhelmed demand — close at lows despite high volume up move'
        }
    return None
```

### 3.6 Test (Professional Testing for Supply/Demand)

**Definition**: A narrow-spread, low-volume bar that dips into (or rallies into) a prior area of activity to check if supply (or demand) remains.

**Test for Supply** (Bullish): Price dips to support area on low volume → no supply remains → bullish

**Test for Demand** (Bearish): Price rallies to resistance area on low volume → no demand remains → bearish

```python
def detect_test(candle, avg_volume, avg_spread, support_zone, resistance_zone, prior_climax):
    """
    Detect professional Test bars.
    """
    spread = candle['high'] - candle['low']
    close_pos = (candle['close'] - candle['low']) / spread if spread > 0 else 0.5
    
    # Test for supply (bullish test at support)
    if candle['low'] <= support_zone['upper']:
        conditions = {
            'low_volume': candle['volume'] < avg_volume * 0.7,
            'narrow_spread': spread < avg_spread * 0.8,
            'closes_above_mid': close_pos > 0.5,
            'in_support_zone': candle['low'] <= support_zone['upper'],
            'prior_climax_exists': prior_climax is not None and prior_climax['bias'] == 'BULLISH',
        }
        
        if sum(conditions.values()) >= 4:
            return {
                'signal': 'TEST_BULLISH',
                'bias': 'BULLISH',
                'strength': (1 - candle['volume'] / avg_volume) * close_pos,
                'confidence': 0.80,
                'action': 'BUY_SIGNAL',
                'note': 'Low volume test of support — supply exhausted, safe to rise'
            }
    
    # Test for demand (bearish test at resistance)
    if candle['high'] >= resistance_zone['lower']:
        conditions = {
            'low_volume': candle['volume'] < avg_volume * 0.7,
            'narrow_spread': spread < avg_spread * 0.8,
            'closes_below_mid': close_pos < 0.5,
            'in_resistance_zone': candle['high'] >= resistance_zone['lower'],
            'prior_climax_exists': prior_climax is not None and prior_climax['bias'] == 'BEARISH',
        }
        
        if sum(conditions.values()) >= 4:
            return {
                'signal': 'TEST_BEARISH',
                'bias': 'BEARISH',
                'strength': (1 - candle['volume'] / avg_volume) * (1 - close_pos),
                'confidence': 0.80,
                'action': 'SELL_SIGNAL',
                'note': 'Low volume test of resistance — demand exhausted, safe to fall'
            }
    
    return None
```

### 3.7 Complete VSA Signal Catalog

| Signal | Volume | Spread | Close | Context | Bias | Confidence |
|---|---|---|---|---|---|---|
| No Demand | Low | Narrow | Mid/Low (up bar) | Uptrend/Resistance | Bearish | 0.65–0.75 |
| No Supply | Low | Narrow | Mid/High (dn bar) | Downtrend/Support | Bullish | 0.65–0.75 |
| Stopping Vol (Bull) | High | Wide | Off low (dn bar) | After decline | Bullish | 0.70–0.80 |
| Stopping Vol (Bear) | High | Wide | Off high (up bar) | After rally | Bearish | 0.70–0.80 |
| Selling Climax | V. High | V. Wide | Recovers | After ext. decline | Bullish | 0.80–0.90 |
| Buying Climax | V. High | V. Wide | Falls back | After ext. rally | Bearish | 0.80–0.90 |
| Upthrust | High | Wide | Near low (up bar) | At resistance | Bearish | 0.75–0.85 |
| Reverse Upthrust | High | Wide | Near high (dn bar) | At support | Bullish | 0.75–0.85 |
| Test (Supply) | Low | Narrow | Off low | At support | Bullish | 0.75–0.85 |
| Test (Demand) | Low | Narrow | Off high | At resistance | Bearish | 0.75–0.85 |
| Absorption (Bull) | High | Narrow | Near high | At support | Bullish | 0.80–0.90 |
| Absorption (Bear) | High | Narrow | Near low | At resistance | Bearish | 0.80–0.90 |

---

## 4. Effort vs Result Analysis

### 4.1 The Effort-Result Principle

Wyckoff's Third Law (Effort vs Result) is the foundation of VSA:

> **Volume = Effort. Price change = Result. When effort and result diverge, a change is imminent.**

### 4.2 Mathematical Formulation

**Instantaneous Effort-Result Ratio:**

$$
ER(t) = \frac{|\Delta P(t)| / ATR(t)}{V(t) / \bar{V}(n)}
$$

Where:
- $|\Delta P(t)| = |C(t) - C(t-1)|$ = absolute price change
- $ATR(t)$ = current Average True Range
- $V(t)$ = current volume
- $\bar{V}(n)$ = n-period average volume

**Interpretation:**
- ER >> 1.0: High result relative to effort → **Ease of movement** (path of least resistance)
- ER ≈ 1.0: Normal relationship → **No signal**
- ER << 1.0: Low result relative to effort → **Absorption/Resistance** (opposing force present)

### 4.3 Cumulative Effort-Result Divergence

Over a window of $w$ bars:

$$
\text{CERD}(t, w) = \frac{\sum_{i=t-w+1}^{t} \text{Result}(i)}{\sum_{i=t-w+1}^{t} \text{Effort}(i)}
$$

Where:
$$
\text{Result}(i) = \frac{P(i) - P(i-1)}{ATR(i)}
$$
$$
\text{Effort}(i) = \frac{V(i)}{\bar{V}(n)} \times \text{sign}(\Delta P(i))
$$

**Directional CERD** (signed to show bullish/bearish bias):

$$
\text{CERD}_{\text{bull}}(t, w) = \frac{\sum_{i: \Delta P(i) > 0} V(i) \cdot \Delta P(i)}{\sum_{i: \Delta P(i) > 0} V(i)} - \frac{\sum_{i: \Delta P(i) < 0} V(i) \cdot |\Delta P(i)|}{\sum_{i: \Delta P(i) < 0} V(i)}
$$

### 4.4 Divergence Types

```
Effort-Result Divergence Classification:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type A: INCREASING EFFORT, DIMINISHING RESULT (Exhaustion)
────────────────────────────────────────────────────────────────────
  Volume:  ██  ███  ████  █████  ██████   ← Effort increasing
  Price:   +5  +4   +3    +2     +1       ← Result decreasing
  Signal:  EXHAUSTION — trend about to reverse

Type B: DECREASING EFFORT, INCREASING RESULT (Ease of Movement)
────────────────────────────────────────────────────────────────────
  Volume:  ██████  ████  ███  ██  █       ← Effort decreasing
  Price:   +2      +3    +4   +5  +6      ← Result increasing
  Signal:  PATH CLEAR — no opposition, trend accelerating

Type C: HIGH EFFORT, NO RESULT (Absorption)
────────────────────────────────────────────────────────────────────
  Volume:  █████  █████  █████  █████     ← Effort high and constant
  Price:   +1     0      -1     0         ← Result minimal
  Signal:  ABSORPTION — one side absorbing the other at this level

Type D: SPIKE EFFORT WITH REVERSAL (Climactic)
────────────────────────────────────────────────────────────────────
  Volume:  ██  ██  ███  █████████  ███    ← Sudden effort spike
  Price:   -3  -4  -5   -8(→+3)   +2     ← Result reverses
  Signal:  CLIMAX — extreme selling/buying exhausted, reversal imminent

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.5 Multi-Bar Effort-Result Analysis

```python
def multi_bar_effort_result(candles, start_idx, end_idx, atr_values, avg_volumes):
    """
    Analyze effort vs result over a range of bars.
    
    Returns divergence type and strength.
    """
    efforts = []
    results = []
    
    for i in range(start_idx, end_idx + 1):
        effort = candles[i]['volume'] / avg_volumes[i] if avg_volumes[i] > 0 else 1.0
        result = abs(candles[i]['close'] - candles[i-1]['close']) / atr_values[i] \
                 if i > 0 and atr_values[i] > 0 else 0.0
        
        efforts.append(effort)
        results.append(result)
    
    if len(efforts) < 3:
        return None
    
    # Calculate slopes
    x = np.arange(len(efforts))
    effort_slope = np.polyfit(x, efforts, 1)[0]
    result_slope = np.polyfit(x, results, 1)[0]
    
    # Total effort and result
    total_effort = sum(efforts)
    total_result = sum(results)
    er_ratio = total_result / total_effort if total_effort > 0 else 1.0
    
    # Net price direction
    net_price_change = candles[end_idx]['close'] - candles[start_idx]['close']
    direction = 'UP' if net_price_change > 0 else 'DOWN'
    
    # Classify divergence type
    if effort_slope > 0.1 and result_slope < -0.05:
        divergence_type = 'EXHAUSTION'
        bias = 'BEARISH' if direction == 'UP' else 'BULLISH'
        strength = abs(effort_slope) + abs(result_slope)
    elif effort_slope < -0.05 and result_slope > 0.1:
        divergence_type = 'EASE_OF_MOVEMENT'
        bias = 'BULLISH' if direction == 'UP' else 'BEARISH'
        strength = abs(result_slope) - abs(effort_slope)
    elif sum(e > 1.5 for e in efforts) > len(efforts) * 0.6 and er_ratio < 0.3:
        divergence_type = 'ABSORPTION'
        bias = 'BULLISH' if direction == 'DOWN' else 'BEARISH'
        strength = total_effort / (total_result + 0.01)
    elif max(efforts) > 3.0 and abs(net_price_change) < atr_values[end_idx] * 0.5:
        divergence_type = 'CLIMACTIC'
        bias = 'BULLISH' if direction == 'DOWN' else 'BEARISH'
        strength = max(efforts) * (1 - er_ratio)
    else:
        divergence_type = 'NORMAL'
        bias = 'NEUTRAL'
        strength = 0.0
    
    return {
        'divergence_type': divergence_type,
        'bias': bias,
        'strength': min(1.0, strength / 5.0),
        'er_ratio': er_ratio,
        'effort_slope': effort_slope,
        'result_slope': result_slope,
        'total_effort': total_effort,
        'total_result': total_result,
        'net_direction': direction,
        'bars_analyzed': end_idx - start_idx + 1,
    }
```

---

## 5. Volume at Support and Resistance

### 5.1 Volume Behavior at Key Levels

The behavior of volume when price approaches support or resistance reveals professional intent:

```
Volume at Support (Bullish scenario):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Approach #1 (Tests):
  Volume: ████  ███  ██  █  █    ← DECREASING on each test
  Price:  ────────────────────── Support level
  Result: Supply exhausted → BULLISH (no more sellers)

Approach #2 (Absorption):
  Volume: █  ██  ████  ████████  ← INCREASING at support
  Price:  ────────────────────── Support level
  Spread: ███  ██  █  ░         ← But spread NARROWING
  Result: Demand absorbing supply → BULLISH (buyers accumulating)

Approach #3 (Breakdown):
  Volume: █  ██  ███  █████  ██████  ← INCREASING through support
  Price:  ────────────────────────── Support level BREAKS
  Spread: █  ██  ███  ████  ████     ← Spread WIDENING
  Close:  All closing at LOWS
  Result: Supply overwhelming → BEARISH (genuine breakdown)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.2 Volume-Based Support/Resistance Strength

$$
\text{Level Strength} = \frac{\sum_{i=1}^{n} V_i \cdot W_{\text{proximity},i} \cdot W_{\text{reaction},i}}{n}
$$

Where:
- $V_i$ = volume at touch $i$
- $W_{\text{proximity},i}$ = $e^{-|P_{\text{touch}} - P_{\text{level}}| / ATR}$ (closer = more weight)
- $W_{\text{reaction},i}$ = size of reaction from the level (larger bounce = stronger level)

### 5.3 Volume Confirmation at Levels

```python
def volume_at_level_analysis(candles, level, level_type, lookback, avg_volume, atr):
    """
    Analyze volume behavior at a support/resistance level.
    
    Parameters:
        level: float, the price level to analyze
        level_type: 'SUPPORT' or 'RESISTANCE'
        lookback: number of bars to analyze
    
    Returns:
        dict with volume behavior and interpretation
    """
    touches = []
    zone_tolerance = atr * 0.3
    
    for i in range(max(0, len(candles) - lookback), len(candles)):
        c = candles[i]
        
        if level_type == 'SUPPORT':
            if abs(c['low'] - level) <= zone_tolerance:
                touches.append({
                    'index': i,
                    'volume': c['volume'],
                    'close_pos': (c['close'] - c['low']) / (c['high'] - c['low']) \
                                 if c['high'] != c['low'] else 0.5,
                    'spread': c['high'] - c['low'],
                    'held': c['close'] > level,
                })
        elif level_type == 'RESISTANCE':
            if abs(c['high'] - level) <= zone_tolerance:
                touches.append({
                    'index': i,
                    'volume': c['volume'],
                    'close_pos': (c['close'] - c['low']) / (c['high'] - c['low']) \
                                 if c['high'] != c['low'] else 0.5,
                    'spread': c['high'] - c['low'],
                    'held': c['close'] < level,
                })
    
    if len(touches) < 2:
        return {'insufficient_data': True}
    
    # Analyze volume trend on touches
    touch_volumes = [t['volume'] for t in touches]
    vol_slope = np.polyfit(range(len(touch_volumes)), touch_volumes, 1)[0]
    avg_touch_vol = np.mean(touch_volumes)
    
    # Analyze holding behavior
    held_pct = sum(1 for t in touches if t['held']) / len(touches)
    
    # Determine interpretation
    if level_type == 'SUPPORT':
        if vol_slope < 0 and held_pct > 0.7:
            interpretation = 'SUPPLY_EXHAUSTING'
            bias = 'BULLISH'
            confidence = 0.80
        elif vol_slope > 0 and held_pct > 0.5:
            interpretation = 'ABSORPTION'
            bias = 'BULLISH'
            confidence = 0.75
        elif vol_slope > 0 and held_pct < 0.4:
            interpretation = 'WEAKENING'
            bias = 'BEARISH'
            confidence = 0.70
        else:
            interpretation = 'NEUTRAL'
            bias = 'NEUTRAL'
            confidence = 0.50
    else:  # RESISTANCE
        if vol_slope < 0 and held_pct > 0.7:
            interpretation = 'DEMAND_EXHAUSTING'
            bias = 'BEARISH'
            confidence = 0.80
        elif vol_slope > 0 and held_pct > 0.5:
            interpretation = 'ABSORPTION'
            bias = 'BEARISH'
            confidence = 0.75
        elif vol_slope > 0 and held_pct < 0.4:
            interpretation = 'WEAKENING'
            bias = 'BULLISH'
            confidence = 0.70
        else:
            interpretation = 'NEUTRAL'
            bias = 'NEUTRAL'
            confidence = 0.50
    
    return {
        'level': level,
        'level_type': level_type,
        'touches': len(touches),
        'volume_slope': vol_slope,
        'avg_touch_volume': avg_touch_vol,
        'held_percentage': held_pct,
        'interpretation': interpretation,
        'bias': bias,
        'confidence': confidence,
    }
```

---

## 6. Integration with Wyckoff Phases

### 6.1 VSA Signals by Wyckoff Phase

| Wyckoff Phase | Expected VSA Signals | Significance |
|---|---|---|
| **Accumulation — Phase A** | Selling Climax, Stopping Volume | Confirms decline is halting |
| **Accumulation — Phase B** | No Supply bars, decreasing volume tests | Confirms supply absorption |
| **Accumulation — Phase C** | Test (supply) at Spring, low volume | Confirms supply exhausted |
| **Accumulation — Phase D** | Wide spread up bars on volume (SOS) | Confirms demand taking control |
| **Markup** | No Supply on pullbacks, ease of movement up | Confirms healthy uptrend |
| **Distribution — Phase A** | Buying Climax, Stopping Volume | Confirms rally exhausting |
| **Distribution — Phase B** | No Demand bars, Upthrusts | Confirms demand absorption |
| **Distribution — Phase C** | Test (demand) at UTAD, low volume | Confirms demand exhausted |
| **Distribution — Phase D** | Wide spread down bars on volume (SOW) | Confirms supply taking control |
| **Markdown** | No Demand on rallies, ease of movement down | Confirms healthy downtrend |

### 6.2 VSA Confirmation Scoring for Wyckoff Events

$$
C_{\text{VSA}} = \frac{\sum_{s \in S_{\text{expected}}} w_s \cdot \mathbb{1}(s \text{ detected})}{\sum_{s \in S_{\text{expected}}} w_s}
$$

Where $S_{\text{expected}}$ is the set of expected VSA signals for the current Wyckoff phase.

### 6.3 Phase-Specific VSA Detection

```python
class WyckoffVSAIntegrator:
    """
    Integrates VSA signals with Wyckoff phase analysis.
    """
    
    EXPECTED_SIGNALS = {
        'ACCUMULATION_A': ['SELLING_CLIMAX', 'STOPPING_VOLUME_BULLISH'],
        'ACCUMULATION_B': ['NO_SUPPLY', 'TEST_BULLISH', 'ABSORPTION_BULLISH'],
        'ACCUMULATION_C': ['TEST_BULLISH', 'NO_SUPPLY'],
        'ACCUMULATION_D': ['WIDE_SPREAD_UP_HIGH_VOL'],  # SOS
        'DISTRIBUTION_A': ['BUYING_CLIMAX', 'STOPPING_VOLUME_BEARISH'],
        'DISTRIBUTION_B': ['NO_DEMAND', 'UPTHRUST', 'ABSORPTION_BEARISH'],
        'DISTRIBUTION_C': ['TEST_BEARISH', 'NO_DEMAND'],
        'DISTRIBUTION_D': ['WIDE_SPREAD_DOWN_HIGH_VOL'],  # SOW
        'MARKUP': ['NO_SUPPLY', 'EASE_OF_MOVEMENT_UP'],
        'MARKDOWN': ['NO_DEMAND', 'EASE_OF_MOVEMENT_DOWN'],
    }
    
    def score_phase_confidence(self, current_phase, detected_signals, lookback_bars=20):
        """
        Score how well VSA signals confirm the hypothesized Wyckoff phase.
        """
        expected = self.EXPECTED_SIGNALS.get(current_phase, [])
        if not expected:
            return 0.5  # No expectation
        
        # Count matches
        matches = 0
        total_weight = 0
        
        for signal_type in expected:
            weight = 1.0
            total_weight += weight
            for detected in detected_signals[-lookback_bars:]:
                if detected['signal'] == signal_type or \
                   detected['signal'].startswith(signal_type.split('_')[0]):
                    matches += weight
                    break
        
        return matches / total_weight if total_weight > 0 else 0.5
    
    def get_conflicting_signals(self, current_phase, detected_signals):
        """
        Identify VSA signals that CONTRADICT the current phase hypothesis.
        """
        conflicts = []
        
        # Define contradictions
        contradictions = {
            'ACCUMULATION': ['BUYING_CLIMAX', 'NO_DEMAND', 'UPTHRUST'],
            'DISTRIBUTION': ['SELLING_CLIMAX', 'NO_SUPPLY', 'TEST_BULLISH'],
            'MARKUP': ['NO_DEMAND', 'UPTHRUST', 'STOPPING_VOLUME_BEARISH'],
            'MARKDOWN': ['NO_SUPPLY', 'TEST_BULLISH', 'STOPPING_VOLUME_BULLISH'],
        }
        
        phase_base = current_phase.split('_')[0] if '_' in current_phase else current_phase
        contradiction_list = contradictions.get(phase_base, [])
        
        for detected in detected_signals:
            if detected['signal'] in contradiction_list:
                conflicts.append(detected)
        
        return conflicts
```

---

## 7. Mathematical Models

### 7.1 Volume-Price Relationship Formulas

**Normalized Volume:**

$$
V_{\text{norm}}(t) = \frac{V(t) - \bar{V}(n)}{\sigma_V(n)}
$$

**Normalized Spread:**

$$
S_{\text{norm}}(t) = \frac{S(t) - \bar{S}(n)}{\sigma_S(n)}
$$

Where $S(t) = H(t) - L(t)$

**Volume-Spread Anomaly Score:**

$$
\text{VSA\_Score}(t) = V_{\text{norm}}(t) - S_{\text{norm}}(t) \times \text{sign}(\Delta P(t))
$$

Interpretation:
- Positive VSA_Score during up bar = buying pressure with narrow spread = absorption (bullish at support)
- Positive VSA_Score during down bar = selling pressure with narrow spread = absorption (bearish at resistance)
- Negative VSA_Score = normal relationship (high volume = wide spread)

### 7.2 Cumulative Volume Delta (CVD)

$$
\text{CVD}(t) = \sum_{i=1}^{t} V(i) \times \text{sign}(\Delta P(i))
$$

Or with close-position weighting:

$$
\text{CVD}_{\text{weighted}}(t) = \sum_{i=1}^{t} V(i) \times (2 \cdot \text{CPos}(i) - 1)
$$

**CVD Divergence from Price:**

$$
\text{Divergence}(t) = \text{corr}(P_{\text{window}}, \text{CVD}_{\text{window}}) < 0
$$

When price makes new highs but CVD is declining = **bearish divergence** (distribution).
When price makes new lows but CVD is rising = **bullish divergence** (accumulation).

### 7.3 Volume Momentum

**Rate of Volume Change:**

$$
\text{VRC}(t, n) = \frac{V(t) - V(t-n)}{V(t-n)} \times 100
$$

**Volume Moving Average Convergence/Divergence (VMACD):**

$$
\text{VMACD}(t) = EMA(V, 12)(t) - EMA(V, 26)(t)
$$

$$
\text{Signal}(t) = EMA(\text{VMACD}, 9)(t)
$$

### 7.4 Effort Index

$$
\text{EI}(t) = \frac{V(t)}{|C(t) - C(t-1)| + \epsilon}
$$

Where $\epsilon$ is a small constant to prevent division by zero.

High EI = lots of volume producing small price change = absorption/conflict
Low EI = small volume producing large price change = ease of movement

### 7.5 Supply-Demand Pressure Index

$$
\text{SDPI}(t, n) = \frac{\sum_{i=t-n+1}^{t} V(i) \cdot \text{CPos}(i) \cdot \frac{S(i)}{ATR(i)}}{\sum_{i=t-n+1}^{t} V(i) \cdot (1-\text{CPos}(i)) \cdot \frac{S(i)}{ATR(i)}}
$$

Where:
- SDPI > 1.0: Demand pressure dominant (bullish)
- SDPI = 1.0: Equilibrium
- SDPI < 1.0: Supply pressure dominant (bearish)

### 7.6 Weis Wave Volume

David Weis's wave volume aggregates volume by directional wave:

$$
\text{WaveVol}_{\text{up}}(k) = \sum_{i=t_{\text{start},k}}^{t_{\text{end},k}} V(i) \quad \text{for up-wave } k
$$

$$
\text{WaveVol}_{\text{down}}(k) = \sum_{i=t_{\text{start},k}}^{t_{\text{end},k}} V(i) \quad \text{for down-wave } k
$$

**Wave Volume Divergence:**

$$
\text{WVD} = \frac{\text{WaveVol}_{\text{up}}(k) - \text{WaveVol}_{\text{up}}(k-1)}{\text{WaveVol}_{\text{up}}(k-1)}
$$

If price makes HH but WaveVol_up decreasing → bearish divergence
If price makes LL but WaveVol_down decreasing → bullish divergence

```python
def calculate_weis_waves(candles, atr, min_wave_size=0.5):
    """
    Calculate Weis Wave volume — aggregate volume by directional waves.
    """
    waves = []
    current_wave = {
        'direction': None,
        'start_idx': 0,
        'end_idx': 0,
        'volume': 0,
        'price_start': candles[0]['close'],
        'price_end': candles[0]['close'],
        'price_high': candles[0]['high'],
        'price_low': candles[0]['low'],
    }
    
    for i in range(1, len(candles)):
        c = candles[i]
        price_change = c['close'] - candles[i-1]['close']
        
        new_direction = 'UP' if price_change >= 0 else 'DOWN'
        
        if current_wave['direction'] is None:
            current_wave['direction'] = new_direction
        
        # Check if wave direction changed
        if new_direction != current_wave['direction']:
            # Check if the reversal is significant enough
            wave_size = abs(current_wave['price_end'] - current_wave['price_start'])
            
            if wave_size >= min_wave_size * atr[i]:
                # Save completed wave
                waves.append(current_wave.copy())
                
                # Start new wave
                current_wave = {
                    'direction': new_direction,
                    'start_idx': i,
                    'end_idx': i,
                    'volume': c['volume'],
                    'price_start': candles[i-1]['close'],
                    'price_end': c['close'],
                    'price_high': c['high'],
                    'price_low': c['low'],
                }
            else:
                # Not significant enough — continue current wave (could be noise)
                current_wave['end_idx'] = i
                current_wave['volume'] += c['volume']
                current_wave['price_end'] = c['close']
                current_wave['price_high'] = max(current_wave['price_high'], c['high'])
                current_wave['price_low'] = min(current_wave['price_low'], c['low'])
        else:
            # Continue current wave
            current_wave['end_idx'] = i
            current_wave['volume'] += c['volume']
            current_wave['price_end'] = c['close']
            current_wave['price_high'] = max(current_wave['price_high'], c['high'])
            current_wave['price_low'] = min(current_wave['price_low'], c['low'])
    
    # Add final wave
    if current_wave['direction'] is not None:
        waves.append(current_wave)
    
    return waves


def detect_weis_wave_divergence(waves):
    """
    Detect divergences between price and Weis Wave volume.
    """
    divergences = []
    
    # Need at least 4 waves (2 up + 2 down minimum)
    up_waves = [w for w in waves if w['direction'] == 'UP']
    down_waves = [w for w in waves if w['direction'] == 'DOWN']
    
    # Bullish divergence: price LL but down-wave volume decreasing
    if len(down_waves) >= 2:
        for j in range(1, len(down_waves)):
            price_lower = down_waves[j]['price_low'] < down_waves[j-1]['price_low']
            vol_lower = down_waves[j]['volume'] < down_waves[j-1]['volume']
            
            if price_lower and vol_lower:
                divergences.append({
                    'type': 'BULLISH_WEIS_DIVERGENCE',
                    'wave_index': j,
                    'price_low_curr': down_waves[j]['price_low'],
                    'price_low_prev': down_waves[j-1]['price_low'],
                    'vol_curr': down_waves[j]['volume'],
                    'vol_prev': down_waves[j-1]['volume'],
                    'strength': down_waves[j-1]['volume'] / down_waves[j]['volume'],
                    'end_idx': down_waves[j]['end_idx'],
                })
    
    # Bearish divergence: price HH but up-wave volume decreasing
    if len(up_waves) >= 2:
        for j in range(1, len(up_waves)):
            price_higher = up_waves[j]['price_high'] > up_waves[j-1]['price_high']
            vol_lower = up_waves[j]['volume'] < up_waves[j-1]['volume']
            
            if price_higher and vol_lower:
                divergences.append({
                    'type': 'BEARISH_WEIS_DIVERGENCE',
                    'wave_index': j,
                    'price_high_curr': up_waves[j]['price_high'],
                    'price_high_prev': up_waves[j-1]['price_high'],
                    'vol_curr': up_waves[j]['volume'],
                    'vol_prev': up_waves[j-1]['volume'],
                    'strength': up_waves[j-1]['volume'] / up_waves[j]['volume'],
                    'end_idx': up_waves[j]['end_idx'],
                })
    
    return divergences
```

---

## 8. Algorithmic Implementation

### 8.1 Complete VSA Scanner

```python
class VSAScanner:
    """
    Complete Volume Spread Analysis scanner for real-time market analysis.
    Detects all major VSA signals and provides trading recommendations.
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.vol_period = self.config.get('volume_avg_period', 20)
        self.spread_period = self.config.get('spread_avg_period', 20)
        self.signal_history = []
        
    def scan(self, candle, candle_history, context):
        """
        Scan current candle for VSA signals.
        
        Parameters:
            candle: current OHLCV bar
            candle_history: list of recent candles (at least vol_period)
            context: dict with 'trend', 'at_support', 'at_resistance', 
                     'wyckoff_phase', etc.
        
        Returns:
            list of detected VSA signals
        """
        # Calculate averages
        recent = candle_history[-self.vol_period:]
        avg_volume = np.mean([c['volume'] for c in recent])
        avg_spread = np.mean([c['high'] - c['low'] for c in recent])
        atr = self._calculate_atr(candle_history)
        
        signals = []
        
        # 1. No Demand
        nd = detect_no_demand(candle, avg_volume, avg_spread, atr, 
                             context.get('trend', 'UNKNOWN'))
        if nd:
            signals.append(nd)
        
        # 2. No Supply
        ns = detect_no_supply(candle, avg_volume, avg_spread, atr,
                             context.get('trend', 'UNKNOWN'))
        if ns:
            signals.append(ns)
        
        # 3. Stopping Volume
        prior_trend = self._detect_micro_trend(candle_history[-10:])
        sv = detect_stopping_volume(candle, avg_volume, avg_spread, atr,
                                   prior_trend['direction'],
                                   prior_trend.get('length', 0),
                                   prior_trend.get('length', 0))
        if sv:
            signals.append(sv)
        
        # 4. Climactic Volume
        cv = detect_climactic_volume(candle, candle_history[-5:], 
                                    avg_volume, avg_spread, atr,
                                    context.get('trend', 'UNKNOWN'))
        if cv:
            signals.append(cv)
        
        # 5. Upthrust
        ut = detect_upthrust(candle, avg_volume, avg_spread,
                            context.get('trend', 'UNKNOWN'))
        if ut:
            signals.append(ut)
        
        # 6. Test
        support_zone = context.get('support_zone', {'upper': 0, 'lower': 0})
        resistance_zone = context.get('resistance_zone', {'upper': 999999, 'lower': 999999})
        prior_climax = self._get_last_climax()
        
        test = detect_test(candle, avg_volume, avg_spread,
                          support_zone, resistance_zone, prior_climax)
        if test:
            signals.append(test)
        
        # 7. Absorption detection
        abs_signal = self._detect_absorption(candle, avg_volume, avg_spread, atr, context)
        if abs_signal:
            signals.append(abs_signal)
        
        # Store signals
        for s in signals:
            s['timestamp'] = candle.get('timestamp')
            s['bar_index'] = len(candle_history)
            self.signal_history.append(s)
        
        return signals
    
    def _detect_absorption(self, candle, avg_volume, avg_spread, atr, context):
        """Detect volume absorption (high vol, narrow spread, holding)."""
        spread = candle['high'] - candle['low']
        close_pos = (candle['close'] - candle['low']) / spread if spread > 0 else 0.5
        
        if candle['volume'] > avg_volume * 1.8 and spread < avg_spread * 0.6:
            if close_pos > 0.6 and context.get('at_support'):
                return {
                    'signal': 'ABSORPTION_BULLISH',
                    'bias': 'BULLISH',
                    'strength': candle['volume'] / avg_volume * close_pos,
                    'confidence': 0.82,
                    'note': 'High volume absorbed at narrow spread near support — demand winning'
                }
            elif close_pos < 0.4 and context.get('at_resistance'):
                return {
                    'signal': 'ABSORPTION_BEARISH',
                    'bias': 'BEARISH',
                    'strength': candle['volume'] / avg_volume * (1 - close_pos),
                    'confidence': 0.82,
                    'note': 'High volume absorbed at narrow spread near resistance — supply winning'
                }
        return None
    
    def _calculate_atr(self, candles, period=14):
        """Calculate ATR."""
        if len(candles) < period + 1:
            return np.mean([c['high'] - c['low'] for c in candles])
        
        true_ranges = []
        for i in range(1, len(candles)):
            tr = max(
                candles[i]['high'] - candles[i]['low'],
                abs(candles[i]['high'] - candles[i-1]['close']),
                abs(candles[i]['low'] - candles[i-1]['close'])
            )
            true_ranges.append(tr)
        
        return np.mean(true_ranges[-period:])
    
    def _detect_micro_trend(self, recent_candles):
        """Detect the immediate micro-trend direction and length."""
        if len(recent_candles) < 3:
            return {'direction': 'UNKNOWN', 'length': 0}
        
        up_count = sum(1 for i in range(1, len(recent_candles)) 
                      if recent_candles[i]['close'] > recent_candles[i-1]['close'])
        down_count = len(recent_candles) - 1 - up_count
        
        if up_count > down_count + 1:
            return {'direction': 'UP', 'length': up_count}
        elif down_count > up_count + 1:
            return {'direction': 'DOWN', 'length': down_count}
        return {'direction': 'SIDEWAYS', 'length': 0}
    
    def _get_last_climax(self):
        """Get the most recent climactic signal."""
        for s in reversed(self.signal_history):
            if 'CLIMAX' in s.get('signal', '') or 'STOPPING' in s.get('signal', ''):
                return s
        return None
```

---

## 9. Core Logic — Entry/Exit

### 9.1 VSA-Based Entry Signals

| Signal Combination | Direction | Confidence | Entry Logic |
|---|---|---|---|
| Test (Bullish) + No Supply + at Support | LONG | 0.85 | Enter long at close of test bar |
| Stopping Volume (Bull) + Bullish reversal bar | LONG | 0.80 | Enter long on confirmation bar |
| Selling Climax + Spring (Wyckoff) | LONG | 0.90 | Enter long on spring reversal |
| Absorption (Bull) at key support | LONG | 0.80 | Enter long with tight stop |
| Test (Bearish) + No Demand + at Resistance | SHORT | 0.85 | Enter short at close of test bar |
| Stopping Volume (Bear) + Bearish reversal bar | SHORT | 0.80 | Enter short on confirmation bar |
| Buying Climax + UTAD (Wyckoff) | SHORT | 0.90 | Enter short on UTAD reversal |
| Upthrust + Absorption (Bear) at resistance | SHORT | 0.85 | Enter short at close of upthrust |

### 9.2 VSA Entry Algorithm

```python
def vsa_entry_logic(vsa_signals, wyckoff_phase, structure_state, candle, atr):
    """
    Generate trade entries based on VSA signals combined with context.
    """
    entries = []
    
    for signal in vsa_signals:
        entry = None
        
        # Bullish entries
        if signal['bias'] == 'BULLISH' and signal['confidence'] >= 0.70:
            # Check alignment with Wyckoff and Structure
            wyckoff_aligned = wyckoff_phase in ['ACCUMULATION', 'MARKUP', 'UNKNOWN']
            structure_aligned = structure_state in ['BULLISH', 'TRANSITIONING', 'UNKNOWN']
            
            if wyckoff_aligned or structure_aligned:
                confidence_boost = 0.0
                if wyckoff_aligned and structure_aligned:
                    confidence_boost = 0.15
                elif wyckoff_aligned or structure_aligned:
                    confidence_boost = 0.05
                
                entry = {
                    'direction': 'LONG',
                    'trigger': signal['signal'],
                    'entry_price': candle['close'],
                    'stop_loss': candle['low'] - atr * 0.5,
                    'target_1': candle['close'] + atr * 1.5,
                    'target_2': candle['close'] + atr * 3.0,
                    'confidence': min(0.95, signal['confidence'] + confidence_boost),
                    'risk_reward': (atr * 1.5) / (candle['close'] - candle['low'] + atr * 0.5),
                }
        
        # Bearish entries
        elif signal['bias'] == 'BEARISH' and signal['confidence'] >= 0.70:
            wyckoff_aligned = wyckoff_phase in ['DISTRIBUTION', 'MARKDOWN', 'UNKNOWN']
            structure_aligned = structure_state in ['BEARISH', 'TRANSITIONING', 'UNKNOWN']
            
            if wyckoff_aligned or structure_aligned:
                confidence_boost = 0.0
                if wyckoff_aligned and structure_aligned:
                    confidence_boost = 0.15
                elif wyckoff_aligned or structure_aligned:
                    confidence_boost = 0.05
                
                entry = {
                    'direction': 'SHORT',
                    'trigger': signal['signal'],
                    'entry_price': candle['close'],
                    'stop_loss': candle['high'] + atr * 0.5,
                    'target_1': candle['close'] - atr * 1.5,
                    'target_2': candle['close'] - atr * 3.0,
                    'confidence': min(0.95, signal['confidence'] + confidence_boost),
                    'risk_reward': (atr * 1.5) / (candle['high'] + atr * 0.5 - candle['close']),
                }
        
        if entry and entry['risk_reward'] >= 1.5:
            entries.append(entry)
    
    # Sort by confidence
    entries.sort(key=lambda x: x['confidence'], reverse=True)
    return entries
```

---

## 10. Risk Parameters

### 10.1 VSA Signal Risk Matrix

| VSA Signal | Risk per Trade | Stop Loss | Target 1 | Target 2 | Min R:R |
|---|---|---|---|---|---|
| Selling Climax + Test | 2.0% | Below SC low | 1.5 ATR | 3.0 ATR | 3:1 |
| No Supply at Support | 1.0% | Below support | 1.0 ATR | 2.0 ATR | 2:1 |
| Absorption (Bullish) | 1.5% | Below absorption zone | 1.5 ATR | 3.0 ATR | 2.5:1 |
| Stopping Volume | 1.5% | Below stopping bar low | 2.0 ATR | 4.0 ATR | 3:1 |
| Buying Climax + Test | 2.0% | Above BC high | 1.5 ATR | 3.0 ATR | 3:1 |
| No Demand at Resistance | 1.0% | Above resistance | 1.0 ATR | 2.0 ATR | 2:1 |
| Upthrust | 1.5% | Above upthrust high | 1.5 ATR | 3.0 ATR | 2.5:1 |

### 10.2 Position Sizing by VSA Confidence

$$
\text{Position Size} = \frac{\text{Account} \times R_{\text{max}} \times C_{\text{VSA}}}{|P_{\text{entry}} - P_{\text{SL}}|}
$$

Where:
- $R_{\text{max}}$ = maximum risk per trade (from table above)
- $C_{\text{VSA}}$ = VSA confidence score [0, 1]

---

## 11. Execution Flow

### 11.1 VSA Processing Pipeline

```
VSA Processing Pipeline:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: RAW DATA
  ├── OHLCV candle received
  ├── Calculate spread, close position, body
  └── Normalize against averages

Step 2: CLASSIFY CURRENT BAR
  ├── Volume classification (Low/Average/High/Extreme)
  ├── Spread classification (Narrow/Average/Wide/Very Wide)
  ├── Close position classification (Low/Mid/High)
  └── Body-to-spread ratio

Step 3: CONTEXT ASSESSMENT
  ├── Current Wyckoff phase
  ├── Proximity to support/resistance
  ├── Micro-trend direction
  ├── Recent VSA signal history
  └── Multi-timeframe structure state

Step 4: SIGNAL DETECTION
  ├── Check for each VSA pattern
  ├── Apply context filters
  ├── Score confidence
  └── Validate against phase expectations

Step 5: ENTRY/EXIT DECISION
  ├── Match signals to entry models
  ├── Calculate risk parameters
  ├── Validate risk/reward
  └── Generate order if valid

Step 6: LOGGING AND STATE UPDATE
  ├── Record signal for history
  ├── Update cumulative metrics (CVD, SDPI)
  └── Update Weis Wave data

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 11.2 Complete VSA Trading System Pseudocode

```python
class VSATradingSystem:
    """
    Complete VSA-based trading system integrated with Wyckoff and Structure.
    """
    
    def __init__(self, config):
        self.scanner = VSAScanner(config)
        self.weis_waves = []
        self.cvd = 0.0
        self.sdpi_history = []
        
    def process_bar(self, candle, history, wyckoff_state, structure_state):
        """
        Main processing loop for each new bar.
        """
        # Build context
        context = self._build_context(candle, history, wyckoff_state, structure_state)
        
        # Scan for VSA signals
        signals = self.scanner.scan(candle, history, context)
        
        # Update cumulative indicators
        self._update_cvd(candle)
        self._update_sdpi(candle, history)
        
        # Update Weis waves
        atr = self.scanner._calculate_atr(history)
        self.weis_waves = calculate_weis_waves(history, [atr] * len(history))
        
        # Check for Weis wave divergences
        weis_divs = detect_weis_wave_divergence(self.weis_waves)
        
        # Generate entry signals
        entries = vsa_entry_logic(
            signals, 
            wyckoff_state.get('phase', 'UNKNOWN'),
            structure_state.get('trend', 'UNKNOWN'),
            candle, atr
        )
        
        # Add Weis divergence entries
        for div in weis_divs:
            if div['end_idx'] == len(history) - 1:  # Current bar
                entries.append({
                    'direction': 'LONG' if 'BULLISH' in div['type'] else 'SHORT',
                    'trigger': div['type'],
                    'confidence': min(0.85, 0.6 + div['strength'] * 0.1),
                    'entry_price': candle['close'],
                    'stop_loss': candle['low'] - atr if 'BULLISH' in div['type'] \
                                else candle['high'] + atr,
                })
        
        return {
            'signals': signals,
            'weis_divergences': weis_divs,
            'entries': entries,
            'cvd': self.cvd,
            'sdpi': self.sdpi_history[-1] if self.sdpi_history else 1.0,
            'context': context,
        }
    
    def _build_context(self, candle, history, wyckoff_state, structure_state):
        """Build analysis context from all available information."""
        atr = self.scanner._calculate_atr(history)
        
        return {
            'trend': structure_state.get('trend', 'UNKNOWN'),
            'wyckoff_phase': wyckoff_state.get('phase', 'UNKNOWN'),
            'at_support': wyckoff_state.get('near_support', False),
            'at_resistance': wyckoff_state.get('near_resistance', False),
            'support_zone': wyckoff_state.get('support_zone', {'upper': 0, 'lower': 0}),
            'resistance_zone': wyckoff_state.get('resistance_zone', 
                                                  {'upper': 999999, 'lower': 999999}),
            'atr': atr,
        }
    
    def _update_cvd(self, candle):
        """Update Cumulative Volume Delta."""
        close_pos = (candle['close'] - candle['low']) / \
                   (candle['high'] - candle['low']) if candle['high'] != candle['low'] else 0.5
        delta = candle['volume'] * (2 * close_pos - 1)
        self.cvd += delta
    
    def _update_sdpi(self, candle, history, period=20):
        """Update Supply-Demand Pressure Index."""
        recent = history[-period:]
        
        demand_pressure = sum(
            c['volume'] * ((c['close'] - c['low']) / (c['high'] - c['low']))
            * ((c['high'] - c['low']) / self.scanner._calculate_atr(history))
            for c in recent if c['high'] != c['low']
        )
        
        supply_pressure = sum(
            c['volume'] * (1 - (c['close'] - c['low']) / (c['high'] - c['low']))
            * ((c['high'] - c['low']) / self.scanner._calculate_atr(history))
            for c in recent if c['high'] != c['low']
        )
        
        sdpi = demand_pressure / supply_pressure if supply_pressure > 0 else 1.0
        self.sdpi_history.append(sdpi)
```

---

## 12. Forex and Crypto Adaptations

### 12.1 Forex Tick Volume Calibration

Since Forex uses tick volume, VSA thresholds need adjustment:

$$
V_{\text{threshold}}^{\text{forex}} = V_{\text{threshold}}^{\text{standard}} \times \frac{\text{Session\_Factor}(t)}{\text{Max\_Session\_Factor}}
$$

| Session | Tick Volume Factor | Notes |
|---|---|---|
| Asian (low vol) | 0.5 | Reduce thresholds — low vol is the norm |
| London (high vol) | 1.0 | Standard thresholds apply |
| London/NY overlap | 1.2 | Increase thresholds — high vol is the norm |
| NY afternoon | 0.8 | Slightly reduce thresholds |

### 12.2 Crypto Volume Considerations

1. **Aggregated exchange volume**: Use data from multiple exchanges, filtered for wash trading
2. **Perpetual futures OI**: Changes in Open Interest complement spot volume
3. **Funding rate**: Extreme funding rates act as additional volume signals
4. **On-chain volume**: Large on-chain transfers complement exchange volume

### 12.3 Crypto-Specific VSA Adjustments

```python
def crypto_volume_adjustment(exchange_volume, oi_change, funding_rate, on_chain_vol):
    """
    Adjust VSA analysis for crypto-specific data sources.
    """
    # Combined volume signal
    adjusted_volume = exchange_volume
    
    # OI increasing + volume decreasing = hidden accumulation/distribution
    if oi_change > 0 and exchange_volume < avg_volume * 0.7:
        adjusted_volume *= 1.5  # Boost — activity is hidden in futures
    
    # Extreme funding as sentiment overlay
    sentiment_adjustment = 1.0
    if funding_rate > 0.05:  # Very positive = overleveraged longs
        sentiment_adjustment = 0.8  # Reduce bullish VSA confidence
    elif funding_rate < -0.03:  # Negative = overleveraged shorts
        sentiment_adjustment = 0.8  # Reduce bearish VSA confidence
    
    # On-chain confirms exchange action
    on_chain_confirmation = 1.0
    if on_chain_vol > avg_on_chain * 2.0:
        on_chain_confirmation = 1.2  # Boost confidence of any VSA signal
    
    return {
        'adjusted_volume': adjusted_volume,
        'sentiment_adjustment': sentiment_adjustment,
        'on_chain_confirmation': on_chain_confirmation,
    }
```

---

## 13. References

### 13.1 Primary Sources

1. Williams, T. (2005). *Master the Markets: Taking a Professional Approach to Trading & Investing Using Volume Spread Analysis*. TradeGuider Systems.
2. Williams, T. (1993). *The Undeclared Secrets That Drive the Stock Market*. TradeGuider Systems.
3. Wyckoff, R.D. (1910). *Studies in Tape Reading*. The Ticker Publishing Company.

### 13.2 Volume Analysis References

4. Weis, D.H. (2013). *Trades About to Happen: A Modern Adaptation of the Wyckoff Method*. Wiley.
5. Leibovit, M. (2011). *The Trader's Book of Volume*. McGraw-Hill.
6. Buff, G. (2000). "Volume Spread Analysis — A Technical Approach." *Technical Analysis of Stocks and Commodities*.

### 13.3 Academic References

7. Blume, L., Easley, D., & O'Hara, M. (1994). "Market Statistics and Technical Analysis: The Role of Volume." *Journal of Finance*, 49(1), 153–181.
8. Karpoff, J.M. (1987). "The Relation Between Price Changes and Trading Volume: A Survey." *Journal of Financial and Quantitative Analysis*, 22(1), 109–126.
9. Llorente, G., Michaely, R., Saar, G., & Wang, J. (2002). "Dynamic Volume-Return Relation of Individual Stocks." *Review of Financial Studies*, 15(4), 1005–1047.

### 13.4 Modern Tools and Software

10. TradeGuider — Tom Williams's automated VSA software (tradeguider.com)
11. Wyckoff Analytics — Roman Bogomazov's educational platform (wyckoffanalytics.com)
12. Hawkeye Traders — Volume analysis indicators (hawkeyetraders.com)
13. Better Volume Indicator — Open-source VSA indicator for MT4/MT5

---

> **Next Document**: `05_execution_flow.md` — Complete Execution Flow for Wyckoff Trading System
