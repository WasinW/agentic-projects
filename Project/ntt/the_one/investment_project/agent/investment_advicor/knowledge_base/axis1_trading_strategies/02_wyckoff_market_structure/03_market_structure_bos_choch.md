# Market Structure — Break of Structure (BoS) & Change of Character (ChoCh)

> **Module**: Axis 1 — Trading Strategies
> **Topic**: 02 — Wyckoff Method & Market Structure
> **File**: 03_market_structure_bos_choch.md
> **Version**: 1.0
> **Last Updated**: 2026-04-12
> **Author**: NTT Multi-Agent AI Trading System — Knowledge Base Team

---

## Table of Contents

1. [Market Structure Fundamentals](#1-market-structure-fundamentals)
2. [Swing Point Detection](#2-swing-point-detection)
3. [Break of Structure (BoS)](#3-break-of-structure-bos)
4. [Change of Character (ChoCh)](#4-change-of-character-choch)
5. [Internal vs External Structure](#5-internal-vs-external-structure)
6. [Multi-Timeframe Structure Analysis](#6-multi-timeframe-structure-analysis)
7. [Algorithmic Detection](#7-algorithmic-detection)
8. [Mathematical Framework](#8-mathematical-framework)
9. [Entry Models Based on Structure Breaks](#9-entry-models-based-on-structure-breaks)
10. [Integration with Wyckoff](#10-integration-with-wyckoff)
11. [Risk Parameters](#11-risk-parameters)
12. [Execution Flow](#12-execution-flow)
13. [References](#13-references)

---

## 1. Market Structure Fundamentals

### 1.1 Definition of Market Structure

Market Structure refers to the pattern of **swing highs** and **swing lows** that price creates as it moves through time. It is the most fundamental aspect of price action analysis — the skeleton upon which all other analysis is built.

### 1.2 The Four Structural Configurations

```
1. BULLISH STRUCTURE (Uptrend)        2. BEARISH STRUCTURE (Downtrend)
   ────────────────────────              ────────────────────────────
                                  
         HH                                  
        ╱  ╲        HH                     ╲        
       ╱    ╲      ╱  ╲                     ╲  LH    
      ╱      ╲    ╱    ╲                     ╲╱  ╲      LH
     ╱  HH    ╲  ╱      ╲                        ╲    ╱  ╲
    ╱  ╱  ╲    ╲╱        ╲                        ╲  ╱    ╲
   ╱  ╱    ╲    HL        ╲                        ╲╱      ╲
  ╱  ╱      ╲              ╲                        LL       ╲
 ╱  ╱   HL   ╲              ╲                                ╲
╱  ╱          ╲              ╲                         LL      ╲
  ╱            HL              HL                               ╲
                                                                 LL
   Higher Highs + Higher Lows       Lower Highs + Lower Lows

3. RANGING STRUCTURE                  4. TRANSITIONING STRUCTURE
   ─────────────────────                 ──────────────────────────

   ─────── Resistance ──────              HH
   ╱╲    ╱╲    ╱╲    ╱╲               ╱  ╲
  ╱  ╲  ╱  ╲  ╱  ╲  ╱  ╲            ╱    ╲   ← ChoCh
 ╱    ╲╱    ╲╱    ╲╱    ╲           ╱   HL ╲      LH
╱                          ╲        ╱  ╱     ╲    ╱  ╲
   ─────── Support ─────────       ╱  ╱       ╲  ╱    ╲
                                  ╱  ╱         ╲╱      ╲
   Equal Highs + Equal Lows     ╱  ╱                    LL
                                  Prior Bullish → Now Bearish
```

### 1.3 Formal Definitions

| Term | Abbreviation | Definition |
|---|---|---|
| **Higher High** | HH | A swing high that exceeds the previous swing high |
| **Higher Low** | HL | A swing low that holds above the previous swing low |
| **Lower High** | LH | A swing high that fails to reach the previous swing high |
| **Lower Low** | LL | A swing low that drops below the previous swing low |
| **Equal High** | EH | A swing high at approximately the same level as previous |
| **Equal Low** | EL | A swing low at approximately the same level as previous |

**Structural State Definition:**

$$
\text{Structure}(t) = \begin{cases}
\text{BULLISH} & \text{if last swing high} = HH \text{ AND last swing low} = HL \\
\text{BEARISH} & \text{if last swing high} = LH \text{ AND last swing low} = LL \\
\text{RANGING} & \text{if swings oscillate within a defined range} \\
\text{TRANSITIONING} & \text{if mixed signals (e.g., HH but then LL)}
\end{cases}
$$

---

## 2. Swing Point Detection

### 2.1 What Constitutes a Valid Swing Point

A swing point is a local price extreme (high or low) that represents a meaningful directional commitment. Not every minor fluctuation qualifies.

#### 2.1.1 Swing High Definition

A **swing high** at bar $i$ exists when:

$$
H(i) > H(j) \quad \forall j \in \{i-n, ..., i-1, i+1, ..., i+n\}
$$

Where $n$ is the lookback/lookforward parameter (minimum bars on each side).

#### 2.1.2 Swing Low Definition

A **swing low** at bar $i$ exists when:

$$
L(i) < L(j) \quad \forall j \in \{i-n, ..., i-1, i+1, ..., i+n\}
$$

### 2.2 Swing Significance Filtering

Not all swing points are structurally significant. We filter by:

1. **Minimum swing size** (in ATR multiples)
2. **Minimum bars between swings**
3. **Swing-to-swing retracement threshold**

$$
\text{Valid Swing} = \begin{cases}
\text{true} & \text{if } |P_{\text{swing}} - P_{\text{prev\_swing}}| > \theta \cdot ATR \\
& \text{AND bars since last swing} > \tau \\
\text{false} & \text{otherwise}
\end{cases}
$$

Default parameters:
- $\theta = 0.5$ ATR minimum swing size
- $\tau = 3$ bars minimum between swings
- $n = 3$ bars lookback/lookforward for swing detection

### 2.3 Swing Detection Algorithm

```python
class SwingDetector:
    """
    Detect significant swing highs and swing lows.
    """
    
    def __init__(self, lookback=3, min_swing_atr=0.5, min_bars_between=3):
        self.lookback = lookback
        self.min_swing_atr = min_swing_atr
        self.min_bars_between = min_bars_between
        self.swing_highs = []
        self.swing_lows = []
        
    def detect_swings(self, candles, atr_values):
        """
        Detect all swing highs and swing lows in the candle data.
        
        Parameters:
            candles: list of OHLCV dicts
            atr_values: list of ATR values
        
        Returns:
            tuple: (swing_highs, swing_lows) — each a list of dicts
        """
        n = self.lookback
        swing_highs = []
        swing_lows = []
        
        for i in range(n, len(candles) - n):
            atr = atr_values[i]
            
            # Check for swing high
            is_swing_high = True
            for j in range(i - n, i + n + 1):
                if j == i:
                    continue
                if candles[j]['high'] >= candles[i]['high']:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                # Check minimum size
                if swing_highs:
                    last_low = swing_lows[-1]['price'] if swing_lows else candles[i]['low']
                    swing_size = candles[i]['high'] - last_low
                    if swing_size < self.min_swing_atr * atr:
                        continue
                    if i - (swing_highs[-1]['index'] if swing_highs else 0) < self.min_bars_between:
                        # Check if new high is higher than last (replace)
                        if candles[i]['high'] > swing_highs[-1]['price']:
                            swing_highs[-1] = {
                                'index': i,
                                'price': candles[i]['high'],
                                'bar': candles[i],
                                'type': 'SWING_HIGH'
                            }
                        continue
                
                swing_highs.append({
                    'index': i,
                    'price': candles[i]['high'],
                    'bar': candles[i],
                    'type': 'SWING_HIGH'
                })
            
            # Check for swing low
            is_swing_low = True
            for j in range(i - n, i + n + 1):
                if j == i:
                    continue
                if candles[j]['low'] <= candles[i]['low']:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                if swing_lows:
                    last_high = swing_highs[-1]['price'] if swing_highs else candles[i]['high']
                    swing_size = last_high - candles[i]['low']
                    if swing_size < self.min_swing_atr * atr:
                        continue
                    if i - (swing_lows[-1]['index'] if swing_lows else 0) < self.min_bars_between:
                        if candles[i]['low'] < swing_lows[-1]['price']:
                            swing_lows[-1] = {
                                'index': i,
                                'price': candles[i]['low'],
                                'bar': candles[i],
                                'type': 'SWING_LOW'
                            }
                        continue
                
                swing_lows.append({
                    'index': i,
                    'price': candles[i]['low'],
                    'bar': candles[i],
                    'type': 'SWING_LOW'
                })
        
        self.swing_highs = swing_highs
        self.swing_lows = swing_lows
        return swing_highs, swing_lows
    
    def classify_swings(self):
        """
        Classify each swing as HH, HL, LH, LL, EH, or EL.
        """
        tolerance = 0.001  # 0.1% tolerance for "equal"
        
        for i in range(1, len(self.swing_highs)):
            prev = self.swing_highs[i-1]['price']
            curr = self.swing_highs[i]['price']
            pct_diff = (curr - prev) / prev
            
            if pct_diff > tolerance:
                self.swing_highs[i]['classification'] = 'HH'
            elif pct_diff < -tolerance:
                self.swing_highs[i]['classification'] = 'LH'
            else:
                self.swing_highs[i]['classification'] = 'EH'
        
        for i in range(1, len(self.swing_lows)):
            prev = self.swing_lows[i-1]['price']
            curr = self.swing_lows[i]['price']
            pct_diff = (curr - prev) / prev
            
            if pct_diff > tolerance:
                self.swing_lows[i]['classification'] = 'HL'
            elif pct_diff < -tolerance:
                self.swing_lows[i]['classification'] = 'LL'
            else:
                self.swing_lows[i]['classification'] = 'EL'
        
        return self.swing_highs, self.swing_lows
```

### 2.4 Swing Point Significance Hierarchy

```
Swing Significance Levels:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Level 1: MAJOR STRUCTURE (Monthly/Weekly pivots)
  ├── Defines the macro trend direction
  ├── Break = major trend change
  └── Significance threshold: > 5 ATR swing size

Level 2: INTERMEDIATE STRUCTURE (Daily/4H pivots)  
  ├── Defines the swing/position trade trend
  ├── Break = intermediate trend change
  └── Significance threshold: 2-5 ATR swing size

Level 3: MINOR STRUCTURE (1H/15M pivots)
  ├── Defines the intraday/scalp trend
  ├── Break = short-term direction change
  └── Significance threshold: 0.5-2 ATR swing size

Level 4: MICRO STRUCTURE (5M/1M pivots)
  ├── Defines immediate price flow
  ├── Break = very short-term shift
  └── Significance threshold: < 0.5 ATR swing size

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 3. Break of Structure (BoS)

### 3.1 Definition

A **Break of Structure (BoS)** occurs when price breaks beyond a swing point **in the direction of the existing trend**, confirming trend continuation.

- **Bullish BoS**: Price breaks above a previous swing high (creates a new HH)
- **Bearish BoS**: Price breaks below a previous swing low (creates a new LL)

```
Bullish BoS:                         Bearish BoS:

        BoS ←── Price breaks           Price breaks ──→ BoS
        above swing high                below swing low
              │                                │
    SH₂      │     New HH          SL₂        │     New LL
   ╱  ╲     ─┼─   ╱                 ╲         ─┼─        ╲
  ╱    ╲      │  ╱                    ╲         │          ╲
 ╱  SH₁╲     │ ╱                      ╲   SL₁  │           ╲
╱  ╱  ╲ ╲    │╱                        ╲ ╱  ╲  │            ╲
  ╱    ╲  ╲  ╱╲ HL₃                     ╲    ╲ │╲ LH₃        ╲
 ╱  HL₁ ╲ ╲╱   ╲                            ╲╲│  ╲
╱         ╲HL₂   ╲                             ╲   ╲
            ╲                                   LH₂  ╲

Confirms: Trend is UP                Confirms: Trend is DOWN
(continuation signal)                (continuation signal)
```

### 3.2 BoS Identification Rules

| Condition | Bullish BoS | Bearish BoS |
|---|---|---|
| **Pre-existing trend** | Must already be in uptrend (HH+HL) | Must already be in downtrend (LH+LL) |
| **Break level** | Price closes above previous swing high | Price closes below previous swing low |
| **Confirmation** | Candle body closes beyond level (not just wick) | Candle body closes beyond level (not just wick) |
| **Volume** | Ideally increased (confirms genuine break) | Ideally increased (confirms genuine break) |
| **Significance** | Creates new HH in the trend | Creates new LL in the trend |
| **Trading implication** | Trend continuation — look for pullback longs | Trend continuation — look for pullback shorts |

### 3.3 BoS Confirmation Criteria

A BoS is **confirmed** when:

$$
\text{BoS\_Confirmed} = \begin{cases}
\text{true (bullish)} & \text{if } C(t) > SH_{\text{prev}} \text{ AND } V(t) > \bar{V} \times 1.0 \\
\text{true (bearish)} & \text{if } C(t) < SL_{\text{prev}} \text{ AND } V(t) > \bar{V} \times 1.0 \\
\text{false} & \text{otherwise}
\end{cases}
$$

Additional confirmation grades:

| Grade | Condition | Confidence |
|---|---|---|
| **Strong BoS** | Close clearly beyond level + high volume + full-body candle | 90% |
| **Moderate BoS** | Close beyond level + average volume | 70% |
| **Weak BoS** | Only wick beyond level OR low volume close beyond | 40% |
| **Failed BoS** | Breaks beyond then immediately reverses (becomes liquidity grab) | Reversal signal |

```python
def detect_bos(candles, i, swing_highs, swing_lows, avg_volume, atr, current_trend):
    """
    Detect Break of Structure (BoS) — trend continuation signal.
    
    Parameters:
        candles: price data
        i: current bar index
        swing_highs: list of detected swing highs
        swing_lows: list of detected swing lows
        avg_volume: 20-period average volume
        atr: current ATR
        current_trend: 'BULLISH' or 'BEARISH'
    
    Returns:
        dict with BoS details or None
    """
    c = candles[i]
    
    if current_trend == 'BULLISH' and swing_highs:
        # Look for bullish BoS — break above previous swing high
        prev_sh = swing_highs[-1]
        
        if c['close'] > prev_sh['price']:
            # BoS detected
            break_distance = c['close'] - prev_sh['price']
            break_atr = break_distance / atr
            vol_ratio = c['volume'] / avg_volume
            
            # Grade the BoS
            spread = c['high'] - c['low']
            body = abs(c['close'] - c['open'])
            body_ratio = body / spread if spread > 0 else 0
            close_pos = (c['close'] - c['low']) / spread if spread > 0 else 0.5
            
            if break_atr > 0.5 and vol_ratio > 1.2 and body_ratio > 0.6 and close_pos > 0.7:
                grade = 'STRONG'
                confidence = 0.90
            elif break_atr > 0.2 and vol_ratio > 0.8:
                grade = 'MODERATE'
                confidence = 0.70
            else:
                grade = 'WEAK'
                confidence = 0.40
            
            return {
                'event': 'BOS',
                'direction': 'BULLISH',
                'index': i,
                'break_level': prev_sh['price'],
                'close_price': c['close'],
                'break_distance': break_distance,
                'break_atr': break_atr,
                'volume_ratio': vol_ratio,
                'grade': grade,
                'confidence': confidence,
                'implication': 'TREND_CONTINUATION_UP',
                'trade_action': 'WAIT_FOR_PULLBACK_LONG',
            }
    
    elif current_trend == 'BEARISH' and swing_lows:
        # Look for bearish BoS — break below previous swing low
        prev_sl = swing_lows[-1]
        
        if c['close'] < prev_sl['price']:
            break_distance = prev_sl['price'] - c['close']
            break_atr = break_distance / atr
            vol_ratio = c['volume'] / avg_volume
            
            spread = c['high'] - c['low']
            body = abs(c['close'] - c['open'])
            body_ratio = body / spread if spread > 0 else 0
            close_pos = (c['close'] - c['low']) / spread if spread > 0 else 0.5
            
            if break_atr > 0.5 and vol_ratio > 1.2 and body_ratio > 0.6 and close_pos < 0.3:
                grade = 'STRONG'
                confidence = 0.90
            elif break_atr > 0.2 and vol_ratio > 0.8:
                grade = 'MODERATE'
                confidence = 0.70
            else:
                grade = 'WEAK'
                confidence = 0.40
            
            return {
                'event': 'BOS',
                'direction': 'BEARISH',
                'index': i,
                'break_level': prev_sl['price'],
                'close_price': c['close'],
                'break_distance': break_distance,
                'break_atr': break_atr,
                'volume_ratio': vol_ratio,
                'grade': grade,
                'confidence': confidence,
                'implication': 'TREND_CONTINUATION_DOWN',
                'trade_action': 'WAIT_FOR_PULLBACK_SHORT',
            }
    
    return None
```

### 3.4 Trading After BoS

After a confirmed BoS, the highest probability trade is to **enter on the pullback** to the broken structure level:

```
Bullish BoS → Pullback Entry:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                 New HH (BoS)
                ╱        ╲
               ╱          ╲  ← Pullback
  Prev SH ───╱────────────╲────── Now Support
             ╱              ╲ ╱
            ╱                ╳ ← ENTRY (pullback to broken level)
           ╱                ╱ ╲
    HL    ╱                ╱   ╲
   ╱ ╲  ╱                ╱     Stop Loss below new HL
  ╱   ╲╱                ╱
 ╱     ╲               ╱
╱                      ╱

Entry: At or near the broken swing high (now support)
Stop Loss: Below the most recent higher low
Target: Measured move (distance of previous swing projected from entry)
```

---

## 4. Change of Character (ChoCh)

### 4.1 Definition

A **Change of Character (ChoCh)** occurs when price breaks a swing point **against the existing trend**, signaling a potential trend reversal. This is the critical shift from one market regime to another.

- **Bullish ChoCh** (shift from bearish to bullish): Price breaks above a previous swing high in a downtrend
- **Bearish ChoCh** (shift from bullish to bearish): Price breaks below a previous swing low in an uptrend

### 4.2 ChoCh vs BoS — The Critical Difference

```
The Fundamental Difference:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BoS = Break in the DIRECTION of the trend    → CONTINUATION
ChoCh = Break AGAINST the trend              → REVERSAL

Example in an Uptrend:
                                              
  Break above swing high = BoS (bullish)     ← Same direction as trend
  Break below swing low = ChoCh (bearish)    ← Against the trend
  
Example in a Downtrend:

  Break below swing low = BoS (bearish)      ← Same direction as trend  
  Break above swing high = ChoCh (bullish)   ← Against the trend

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.3 ChoCh Visual Examples

```
Bearish ChoCh (Bullish → Bearish):

     HH₂ ← Last Higher High
    ╱  ╲
   ╱    ╲
  ╱  HH₁ ╲
 ╱  ╱  ╲  ╲
╱  ╱ HL₁╲  ╲   ← ChoCh occurs when price
  ╱       ╲  ╲     breaks below HL₁
 ╱    HL₂  ╲  ╲
╱           ╲  ╲
─────────────╲──╲──────── HL₂ Level
              ╲  ╲
               ╲  ╲  ← Price closes below HL₂
                ╲  ╲    = BEARISH ChoCh
                 ╲  ╲
                  ╲  New LL
                   ╲
                    ╲  Downtrend begins


Bullish ChoCh (Bearish → Bullish):

╲
 ╲
  ╲  LH₁
   ╲╱  ╲
    ╲    ╲
     LL₁  ╲
           ╲  LH₂
            ╲╱  ╲
─────────────╲───╲────── LH₂ Level
              LL₂ ╲
                   ╲   ╱ ← Price closes above LH₂
                    ╲ ╱    = BULLISH ChoCh  
                     ╳
                    ╱ ╲
                   ╱   New HL (confirms)
                  ╱
                 ╱  Uptrend begins
```

### 4.4 ChoCh Detection Algorithm

```python
def detect_choch(candles, i, swing_highs, swing_lows, avg_volume, atr, current_trend):
    """
    Detect Change of Character (ChoCh) — trend reversal signal.
    
    ChoCh = break of a swing point AGAINST the prevailing trend.
    
    Returns:
        dict with ChoCh details or None
    """
    c = candles[i]
    
    if current_trend == 'BULLISH' and swing_lows:
        # Bearish ChoCh — price breaks below last HL in uptrend
        # Find the most recent significant swing low (the HL that matters)
        relevant_sl = None
        for sl in reversed(swing_lows):
            if sl.get('classification') in ['HL', None]:
                relevant_sl = sl
                break
        
        if relevant_sl is None:
            return None
        
        if c['close'] < relevant_sl['price']:
            break_distance = relevant_sl['price'] - c['close']
            break_atr = break_distance / atr
            vol_ratio = c['volume'] / avg_volume
            
            spread = c['high'] - c['low']
            body = abs(c['close'] - c['open'])
            close_pos = (c['close'] - c['low']) / spread if spread > 0 else 0.5
            
            # Grade the ChoCh
            if break_atr > 0.5 and vol_ratio > 1.3 and close_pos < 0.3:
                grade = 'STRONG'
                confidence = 0.85
            elif break_atr > 0.2 and vol_ratio > 0.8:
                grade = 'MODERATE'
                confidence = 0.65
            else:
                grade = 'WEAK'
                confidence = 0.45
            
            return {
                'event': 'CHOCH',
                'direction': 'BEARISH',
                'index': i,
                'break_level': relevant_sl['price'],
                'close_price': c['close'],
                'break_distance': break_distance,
                'break_atr': break_atr,
                'volume_ratio': vol_ratio,
                'grade': grade,
                'confidence': confidence,
                'prev_trend': 'BULLISH',
                'new_trend': 'BEARISH',
                'implication': 'POTENTIAL_TREND_REVERSAL_TO_BEARISH',
                'trade_action': 'LOOK_FOR_SHORT_ENTRY_ON_RETEST',
                'invalidation': swing_highs[-1]['price'] if swing_highs else None,
            }
    
    elif current_trend == 'BEARISH' and swing_highs:
        # Bullish ChoCh — price breaks above last LH in downtrend
        relevant_sh = None
        for sh in reversed(swing_highs):
            if sh.get('classification') in ['LH', None]:
                relevant_sh = sh
                break
        
        if relevant_sh is None:
            return None
        
        if c['close'] > relevant_sh['price']:
            break_distance = c['close'] - relevant_sh['price']
            break_atr = break_distance / atr
            vol_ratio = c['volume'] / avg_volume
            
            spread = c['high'] - c['low']
            close_pos = (c['close'] - c['low']) / spread if spread > 0 else 0.5
            
            if break_atr > 0.5 and vol_ratio > 1.3 and close_pos > 0.7:
                grade = 'STRONG'
                confidence = 0.85
            elif break_atr > 0.2 and vol_ratio > 0.8:
                grade = 'MODERATE'
                confidence = 0.65
            else:
                grade = 'WEAK'
                confidence = 0.45
            
            return {
                'event': 'CHOCH',
                'direction': 'BULLISH',
                'index': i,
                'break_level': relevant_sh['price'],
                'close_price': c['close'],
                'break_distance': break_distance,
                'break_atr': break_atr,
                'volume_ratio': vol_ratio,
                'grade': grade,
                'confidence': confidence,
                'prev_trend': 'BEARISH',
                'new_trend': 'BULLISH',
                'implication': 'POTENTIAL_TREND_REVERSAL_TO_BULLISH',
                'trade_action': 'LOOK_FOR_LONG_ENTRY_ON_RETEST',
                'invalidation': swing_lows[-1]['price'] if swing_lows else None,
            }
    
    return None
```

### 4.5 ChoCh Confirmation vs False Signal

A ChoCh alone does not guarantee a trend reversal. Confirmation is required:

| Confirmation Level | Requirements | Confidence |
|---|---|---|
| **Level 1: ChoCh only** | Break against trend on single timeframe | 45–65% |
| **Level 2: ChoCh + Retest** | ChoCh followed by pullback that holds | 65–80% |
| **Level 3: ChoCh + BoS** | ChoCh followed by a BoS in the new direction | 80–90% |
| **Level 4: MTF ChoCh** | ChoCh confirmed on multiple timeframes | 85–95% |

$$
C_{\text{ChoCh\_final}} = C_{\text{ChoCh\_base}} \times (1 + 0.15 \times \mathbb{1}[\text{retest holds}]) \times (1 + 0.20 \times \mathbb{1}[\text{subsequent BoS}]) \times (1 + 0.15 \times \mathbb{1}[\text{MTF confirms}])
$$

### 4.6 ChoCh vs Failed BoS (Liquidity Grab)

Critical distinction: Sometimes what appears to be a BoS is actually a liquidity grab that reverses — this reversal IS the ChoCh:

```
Failed BoS = ChoCh Signal:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

       HH
      ╱  ╲
     ╱    ╲ ← Price appears to break above HH
    ╱  SH  ╲   (looks like bullish BoS)
   ╱  ╱  ╲ ╲
  ╱  ╱ HL ╲ ╲  ← But then REVERSES sharply
 ╱  ╱      ╲ ╲    and breaks below HL
╱  ╱        ╲ ╲
  ╱      HL₂  ╲ ╲
 ╱              ╲ ╲
╱────────────────╲─╲──── HL₂ Level
                  ╲  ╲
                   ╲  ╲ ← ChoCh confirmed
                    ╲  ╲   (failed BoS became reversal)
                     ╲  LL

This is called: "Inducement" or "Liquidity Grab into ChoCh"
Very high probability setup when:
  1. BoS attempts on low volume or wicks only
  2. Reversal is sharp and on high volume
  3. Occurs at key HTF levels

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. Internal vs External Structure

### 5.1 Definitions

| Structure Type | Definition | Swing Size | Use Case |
|---|---|---|---|
| **External Structure** | Major swing points that define the macro trend | Large (> 2 ATR) | Trend direction, position trades |
| **Internal Structure** | Minor swing points within external moves | Small (0.3–2 ATR) | Entry timing, scalping |

### 5.2 Visual Representation

```
External vs Internal Structure:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXTERNAL (Major):           INTERNAL (Minor, within external):
                                          
      HH_ext                     HH_ext
     ╱    ╲                     ╱  ╲  ╱╲  ← Internal swing points
    ╱      ╲                   ╱ ╲╱╲╱  ╲     within the external move
   ╱        ╲                 ╱          ╲
  ╱   HL_ext ╲              ╱  iHH  iHH  ╲
 ╱    ╱    ╲  ╲            ╱  ╱  ╲╱╲  ╲   ╲
╱    ╱      ╲  ╲          ╱  ╱ iHL ╲iHL╲   ╲
    ╱  HL_ext╲  ╲        ╱  ╱       ╲    ╲   ╲
   ╱          ╲  ╲      ╱  ╱    HL_ext╲   ╲   ╲
  ╱            ╲  ╲    ╱  ╱  ╱╲        ╲   ╲   ╲
 ╱              ╲     ╱  ╱  ╱  ╲╱╲      ╲   ╲
╱                    ╱  ╱  ╱  iLL  ╲      ╲   

External structure         Internal structure provides
gives the DIRECTION        the ENTRY TIMING within
                          the external structure

Key Insight:
- Trade in the direction of EXTERNAL structure
- Time entries using INTERNAL structure breaks
- Internal ChoCh within external trend = pullback entry

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.3 Internal/External Structure Rules

| Rule | Description |
|---|---|
| 1 | External structure determines bias (trade direction) |
| 2 | Internal structure provides entry timing |
| 3 | Internal BoS in direction of external = **continuation entry** |
| 4 | Internal ChoCh against external = **potential reversal** (be cautious) |
| 5 | Internal ChoCh aligned with external = **pullback complete** (entry) |
| 6 | External ChoCh = major trend shift (higher significance) |

### 5.4 Internal Structure for Entry Timing

```python
def internal_structure_entry(external_trend, internal_event, candle, atr):
    """
    Use internal structure to time entries within external trend.
    
    Best entries occur when:
    - External is bullish AND internal shows bullish ChoCh (pullback over)
    - External is bearish AND internal shows bearish ChoCh (pullback over)
    """
    # Internal ChoCh aligning with external trend = optimal entry
    if external_trend == 'BULLISH' and internal_event['event'] == 'CHOCH' \
       and internal_event['direction'] == 'BULLISH':
        # Internal structure shifted back to bullish within external uptrend
        # = pullback is over, trend resuming
        return {
            'signal': 'LONG',
            'type': 'INTERNAL_CHOCH_ALIGNED',
            'entry': candle['close'],
            'stop_loss': internal_event.get('invalidation', candle['low'] - atr),
            'confidence': 0.80,
            'note': 'Internal ChoCh bullish within external uptrend = pullback entry'
        }
    
    elif external_trend == 'BEARISH' and internal_event['event'] == 'CHOCH' \
         and internal_event['direction'] == 'BEARISH':
        return {
            'signal': 'SHORT',
            'type': 'INTERNAL_CHOCH_ALIGNED',
            'entry': candle['close'],
            'stop_loss': internal_event.get('invalidation', candle['high'] + atr),
            'confidence': 0.80,
            'note': 'Internal ChoCh bearish within external downtrend = pullback entry'
        }
    
    # Internal BoS against external = potential major reversal forming
    elif external_trend == 'BULLISH' and internal_event['event'] == 'BOS' \
         and internal_event['direction'] == 'BEARISH':
        return {
            'signal': 'CAUTION',
            'type': 'INTERNAL_BOS_AGAINST_EXTERNAL',
            'confidence': 0.40,
            'note': 'Internal bearish BoS within external uptrend = possible reversal forming'
        }
    
    return None
```

---

## 6. Multi-Timeframe Structure Analysis

### 6.1 Timeframe Hierarchy

```
Multi-Timeframe Structure Hierarchy:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Macro     │ Monthly → Weekly  │ Strategic Direction │ "WHERE are we going?"
          │                   │ Position trades     │
──────────┼───────────────────┼─────────────────────┼──────────────────────
Primary   │ Daily → 4H        │ Trend Direction     │ "WHICH direction?"
          │                   │ Swing trades        │
──────────┼───────────────────┼─────────────────────┼──────────────────────
Secondary │ 4H → 1H           │ Entry Zone          │ "WHERE to enter?"
          │                   │ Day trades          │
──────────┼───────────────────┼─────────────────────┼──────────────────────
Timing    │ 1H → 15M → 5M    │ Precise Entry       │ "WHEN to enter?"
          │                   │ Scalp trades        │

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Multi-Timeframe Confluence Rules

| HTF Structure | MTF Structure | LTF Trigger | Signal Quality | Action |
|---|---|---|---|---|
| Bullish (HH+HL) | Bullish BoS | Bullish ChoCh | **A+** | Strong long |
| Bullish (HH+HL) | Pullback | Bullish ChoCh | **A** | Long on pullback |
| Bullish (HH+HL) | Bearish ChoCh | Bearish BoS | **C** | Avoid (conflicting) |
| Bearish (LH+LL) | Bearish BoS | Bearish ChoCh | **A+** | Strong short |
| Bearish (LH+LL) | Pullback | Bearish ChoCh | **A** | Short on pullback |
| Bearish (LH+LL) | Bullish ChoCh | Bullish BoS | **C** | Avoid (conflicting) |
| Ranging | BoS attempt | Reversal at range boundary | **B** | Range trade |
| ChoCh (transition) | Confirming direction | Entry trigger | **B+** | Trade the new direction |

### 6.3 MTF Structure Agreement Score

$$
\text{MTF\_Score} = \sum_{tf \in \text{Timeframes}} w_{tf} \times D_{tf}
$$

Where:
- $w_{tf}$ = weight of timeframe (higher TF = higher weight)
- $D_{tf}$ = directional score: +1 (bullish structure), -1 (bearish structure), 0 (ranging)

| Timeframe | Weight ($w_{tf}$) |
|---|---|
| Monthly | 0.05 |
| Weekly | 0.10 |
| Daily | 0.20 |
| 4H | 0.25 |
| 1H | 0.20 |
| 15M | 0.15 |
| 5M | 0.05 |

**Interpretation:**
- MTF Score > +0.6: Strong bullish confluence → trade long only
- MTF Score +0.2 to +0.6: Moderate bullish → lean long
- MTF Score -0.2 to +0.2: Mixed → no strong bias
- MTF Score -0.6 to -0.2: Moderate bearish → lean short
- MTF Score < -0.6: Strong bearish confluence → trade short only

### 6.4 MTF Structure Analyzer

```python
class MultiTimeframeStructureAnalyzer:
    """
    Analyzes market structure across multiple timeframes and produces
    a unified directional bias with confidence scoring.
    """
    
    TIMEFRAME_WEIGHTS = {
        'M1': 0.05, 'W1': 0.10, 'D1': 0.20,
        'H4': 0.25, 'H1': 0.20, 'M15': 0.15, 'M5': 0.05
    }
    
    def __init__(self, timeframes=None):
        self.timeframes = timeframes or ['D1', 'H4', 'H1', 'M15']
        self.structure_states = {}
        self.swing_detectors = {tf: SwingDetector() for tf in self.timeframes}
    
    def update(self, timeframe, candles, atr):
        """
        Update structure analysis for a specific timeframe.
        """
        detector = self.swing_detectors[timeframe]
        sh, sl = detector.detect_swings(candles, atr)
        detector.classify_swings()
        
        # Determine structure state
        if len(sh) >= 2 and len(sl) >= 2:
            last_sh_class = sh[-1].get('classification', 'UNKNOWN')
            last_sl_class = sl[-1].get('classification', 'UNKNOWN')
            
            if last_sh_class == 'HH' and last_sl_class == 'HL':
                state = 'BULLISH'
                score = 1.0
            elif last_sh_class == 'LH' and last_sl_class == 'LL':
                state = 'BEARISH'
                score = -1.0
            elif last_sh_class == 'HH' and last_sl_class == 'LL':
                state = 'TRANSITIONING'
                score = 0.0
            elif last_sh_class == 'LH' and last_sl_class == 'HL':
                state = 'RANGING'
                score = 0.0
            else:
                state = 'UNKNOWN'
                score = 0.0
        else:
            state = 'INSUFFICIENT_DATA'
            score = 0.0
        
        self.structure_states[timeframe] = {
            'state': state,
            'score': score,
            'swing_highs': sh,
            'swing_lows': sl,
            'last_update': len(candles)
        }
    
    def get_confluence_score(self):
        """
        Calculate multi-timeframe confluence score.
        
        Returns:
            dict with overall bias, confidence, and per-TF breakdown
        """
        total_score = 0.0
        total_weight = 0.0
        breakdown = {}
        
        for tf in self.timeframes:
            if tf in self.structure_states:
                weight = self.TIMEFRAME_WEIGHTS.get(tf, 0.1)
                score = self.structure_states[tf]['score']
                total_score += weight * score
                total_weight += weight
                breakdown[tf] = {
                    'state': self.structure_states[tf]['state'],
                    'score': score,
                    'weight': weight,
                    'contribution': weight * score
                }
        
        normalized_score = total_score / total_weight if total_weight > 0 else 0.0
        
        # Determine overall bias
        if normalized_score > 0.6:
            bias = 'STRONG_BULLISH'
        elif normalized_score > 0.2:
            bias = 'BULLISH'
        elif normalized_score > -0.2:
            bias = 'NEUTRAL'
        elif normalized_score > -0.6:
            bias = 'BEARISH'
        else:
            bias = 'STRONG_BEARISH'
        
        # Agreement (all TFs aligned)
        states = [s['state'] for s in self.structure_states.values()]
        bullish_count = states.count('BULLISH')
        bearish_count = states.count('BEARISH')
        agreement = max(bullish_count, bearish_count) / len(states) if states else 0
        
        return {
            'score': normalized_score,
            'bias': bias,
            'agreement': agreement,
            'confidence': abs(normalized_score) * agreement,
            'breakdown': breakdown,
            'tradeable': agreement > 0.5 and abs(normalized_score) > 0.3
        }
```

---

## 7. Algorithmic Detection

### 7.1 Complete Market Structure Engine

```python
class MarketStructureEngine:
    """
    Complete engine for detecting BoS, ChoCh, and tracking structure state.
    """
    
    def __init__(self, config):
        self.config = config
        self.swing_detector = SwingDetector(
            lookback=config.get('swing_lookback', 3),
            min_swing_atr=config.get('min_swing_atr', 0.5),
            min_bars_between=config.get('min_bars_between', 3)
        )
        self.current_trend = 'UNKNOWN'
        self.structure_events = []
        self.last_bos = None
        self.last_choch = None
        
    def process_bar(self, candle, index, candles, atr, avg_volume):
        """
        Process a new bar and check for structure events.
        
        Returns:
            dict with current structure state and any new events
        """
        # Update swing detection
        atr_values = [atr] * len(candles)  # simplified; use actual array in production
        sh, sl = self.swing_detector.detect_swings(candles[:index+1], atr_values[:index+1])
        self.swing_detector.classify_swings()
        
        # Determine current trend from swing classification
        self._update_trend()
        
        result = {
            'trend': self.current_trend,
            'swing_highs': sh[-5:],  # Last 5 swing highs
            'swing_lows': sl[-5:],   # Last 5 swing lows
            'new_events': [],
        }
        
        # Check for BoS
        bos = detect_bos(candles, index, sh, sl, avg_volume, atr, self.current_trend)
        if bos:
            self.last_bos = bos
            self.structure_events.append(bos)
            result['new_events'].append(bos)
        
        # Check for ChoCh
        choch = detect_choch(candles, index, sh, sl, avg_volume, atr, self.current_trend)
        if choch:
            self.last_choch = choch
            self.structure_events.append(choch)
            result['new_events'].append(choch)
            # Update trend on ChoCh
            self.current_trend = choch['new_trend']
        
        return result
    
    def _update_trend(self):
        """Update trend based on latest swing classifications."""
        sh = self.swing_detector.swing_highs
        sl = self.swing_detector.swing_lows
        
        if len(sh) < 2 or len(sl) < 2:
            return
        
        last_sh = sh[-1].get('classification', 'UNKNOWN')
        last_sl = sl[-1].get('classification', 'UNKNOWN')
        
        if last_sh == 'HH' and last_sl == 'HL':
            self.current_trend = 'BULLISH'
        elif last_sh == 'LH' and last_sl == 'LL':
            self.current_trend = 'BEARISH'
        elif self.current_trend == 'UNKNOWN':
            # Default based on last swing direction
            if sh[-1]['index'] > sl[-1]['index']:
                self.current_trend = 'BULLISH'
            else:
                self.current_trend = 'BEARISH'
```

### 7.2 Fractal-Based Swing Detection (Alternative Method)

For more precise swing detection, use Williams' fractal approach:

$$
\text{Fractal High at } i = \begin{cases}
\text{true} & \text{if } H(i) > \max(H(i-2), H(i-1), H(i+1), H(i+2)) \\
\text{false} & \text{otherwise}
\end{cases}
$$

$$
\text{Fractal Low at } i = \begin{cases}
\text{true} & \text{if } L(i) < \min(L(i-2), L(i-1), L(i+1), L(i+2)) \\
\text{false} & \text{otherwise}
\end{cases}
$$

### 7.3 Adaptive Swing Detection

For different market conditions, the swing detection parameters should adapt:

$$
\theta_{\text{adaptive}} = \theta_{\text{base}} \times \frac{ATR_{\text{current}}}{ATR_{\text{historical}}} \times f(\text{volatility regime})
$$

Where:
- In high volatility: increase $\theta$ (require larger swings to be significant)
- In low volatility: decrease $\theta$ (smaller swings become meaningful)

---

## 8. Mathematical Framework

### 8.1 Swing Point Formal Model

Let $\{P_t\}_{t=1}^{T}$ be a price series. Define the swing detection function:

$$
\text{SH}(t, n) = \mathbb{1}\left[H(t) = \max_{|j-t| \leq n} H(j)\right]
$$

$$
\text{SL}(t, n) = \mathbb{1}\left[L(t) = \min_{|j-t| \leq n} L(j)\right]
$$

### 8.2 Structure State Transition Model

The market structure can be modeled as a Hidden Markov Model (HMM):

**States**: $S = \{\text{BULLISH}, \text{BEARISH}, \text{RANGING}, \text{TRANSITIONING}\}$

**Transition Matrix:**

$$
A = \begin{bmatrix}
P(B \rightarrow B) & P(B \rightarrow Be) & P(B \rightarrow R) & P(B \rightarrow T) \\
P(Be \rightarrow B) & P(Be \rightarrow Be) & P(Be \rightarrow R) & P(Be \rightarrow T) \\
P(R \rightarrow B) & P(R \rightarrow Be) & P(R \rightarrow R) & P(R \rightarrow T) \\
P(T \rightarrow B) & P(T \rightarrow Be) & P(T \rightarrow R) & P(T \rightarrow T)
\end{bmatrix}
$$

Typical values:

$$
A \approx \begin{bmatrix}
0.80 & 0.02 & 0.08 & 0.10 \\
0.02 & 0.80 & 0.08 & 0.10 \\
0.15 & 0.15 & 0.60 & 0.10 \\
0.30 & 0.30 & 0.15 & 0.25
\end{bmatrix}
$$

### 8.3 BoS Probability Model

$$
P(\text{BoS successful} | \text{break}) = \sigma\left(\beta_0 + \beta_1 V_{\text{norm}} + \beta_2 S_{\text{norm}} + \beta_3 C_{\text{pos}} + \beta_4 T_{\text{agree}}\right)
$$

Where:
- $V_{\text{norm}}$ = normalized volume at break
- $S_{\text{norm}}$ = normalized spread (body size)
- $C_{\text{pos}}$ = close position (1 = at extreme in break direction)
- $T_{\text{agree}}$ = MTF agreement score

### 8.4 ChoCh Reliability Model

The probability that a ChoCh leads to sustained trend reversal:

$$
P(\text{Reversal} | \text{ChoCh}) = P_{\text{base}} \times \prod_{i=1}^{n} (1 + \alpha_i \cdot F_i)
$$

Where $F_i$ are confirmation factors:

| Factor ($F_i$) | $\alpha_i$ | Condition |
|---|---|---|
| Volume confirmation | 0.20 | High volume on break |
| Full body break | 0.15 | Close clearly beyond level |
| HTF support/resistance | 0.25 | ChoCh at HTF key level |
| Prior exhaustion signals | 0.20 | Divergences before ChoCh |
| MTF alignment | 0.20 | Other TFs confirming |
| Retest holds | 0.15 | Pullback to level holds |

### 8.5 Measured Move Projection

After a BoS or ChoCh, project the expected move:

**BoS Projection (Trend Continuation):**

$$
\text{Target}_{\text{BoS}} = P_{\text{break}} + \text{sign}(\text{direction}) \times |P_{\text{prev\_swing}} - P_{\text{origin}}|
$$

**ChoCh Projection (Reversal):**

$$
\text{Target}_{\text{ChoCh}} = P_{\text{break}} + \text{sign}(\text{new\_direction}) \times |P_{\text{origin}} - P_{\text{break}}| \times \phi
$$

Where $\phi$ is the Fibonacci ratio (commonly 1.0, 1.618, or 2.618).

---

## 9. Entry Models Based on Structure Breaks

### 9.1 Entry Model 1: BoS Pullback Entry

The highest probability continuation entry after a confirmed BoS.

```python
def bos_pullback_entry(bos_event, candle, last_swing, atr, avg_volume):
    """
    Entry on pullback to the broken structure level after BoS.
    
    Logic:
    1. BoS confirmed (price breaks swing point)
    2. Wait for pullback to the broken level
    3. Look for reversal candle at the broken level
    4. Enter in direction of BoS
    """
    if bos_event is None:
        return None
    
    direction = bos_event['direction']
    break_level = bos_event['break_level']
    
    if direction == 'BULLISH':
        # Wait for pullback to broken resistance (now support)
        if candle['low'] <= break_level * 1.002:  # Within 0.2% of level
            # Look for bullish reaction
            spread = candle['high'] - candle['low']
            close_pos = (candle['close'] - candle['low']) / spread if spread > 0 else 0.5
            
            if close_pos > 0.5 and candle['close'] > break_level:
                return {
                    'signal': 'LONG',
                    'type': 'BOS_PULLBACK',
                    'entry': candle['close'],
                    'stop_loss': last_swing['price'] - atr * 0.3,
                    'target_1': candle['close'] + abs(bos_event['break_distance']) * 1.0,
                    'target_2': candle['close'] + abs(bos_event['break_distance']) * 2.0,
                    'risk_reward': abs(bos_event['break_distance']) / \
                                  (candle['close'] - last_swing['price'] + atr * 0.3),
                    'confidence': bos_event['confidence'] * 0.85,
                }
    
    elif direction == 'BEARISH':
        if candle['high'] >= break_level * 0.998:
            spread = candle['high'] - candle['low']
            close_pos = (candle['close'] - candle['low']) / spread if spread > 0 else 0.5
            
            if close_pos < 0.5 and candle['close'] < break_level:
                return {
                    'signal': 'SHORT',
                    'type': 'BOS_PULLBACK',
                    'entry': candle['close'],
                    'stop_loss': last_swing['price'] + atr * 0.3,
                    'target_1': candle['close'] - abs(bos_event['break_distance']) * 1.0,
                    'target_2': candle['close'] - abs(bos_event['break_distance']) * 2.0,
                    'risk_reward': abs(bos_event['break_distance']) / \
                                  (last_swing['price'] + atr * 0.3 - candle['close']),
                    'confidence': bos_event['confidence'] * 0.85,
                }
    
    return None
```

### 9.2 Entry Model 2: ChoCh Reversal Entry

```python
def choch_reversal_entry(choch_event, candle, atr, avg_volume):
    """
    Entry after ChoCh — looking for the first pullback in new direction.
    
    Logic:
    1. ChoCh detected (break against prior trend)
    2. Wait for initial impulse to complete
    3. Enter on first pullback that holds above/below ChoCh level
    """
    if choch_event is None:
        return None
    
    direction = choch_event['direction']
    break_level = choch_event['break_level']
    invalidation = choch_event.get('invalidation')
    
    if direction == 'BULLISH':
        # After bullish ChoCh, look for pullback entry
        # Price should be pulling back toward the ChoCh level
        if candle['low'] <= break_level * 1.005 and candle['close'] > break_level:
            spread = candle['high'] - candle['low']
            close_pos = (candle['close'] - candle['low']) / spread if spread > 0 else 0.5
            
            if close_pos > 0.5:
                sl = invalidation - atr * 0.3 if invalidation else break_level - atr * 1.5
                entry = candle['close']
                risk = entry - sl
                
                return {
                    'signal': 'LONG',
                    'type': 'CHOCH_REVERSAL',
                    'entry': entry,
                    'stop_loss': sl,
                    'target_1': entry + risk * 2.0,
                    'target_2': entry + risk * 3.0,
                    'target_3': entry + risk * 5.0,
                    'risk_reward_1': 2.0,
                    'risk_reward_2': 3.0,
                    'confidence': choch_event['confidence'] * 0.80,
                    'invalidation_note': f'If price closes below {sl:.5f}, ChoCh invalidated'
                }
    
    elif direction == 'BEARISH':
        if candle['high'] >= break_level * 0.995 and candle['close'] < break_level:
            spread = candle['high'] - candle['low']
            close_pos = (candle['close'] - candle['low']) / spread if spread > 0 else 0.5
            
            if close_pos < 0.5:
                sl = invalidation + atr * 0.3 if invalidation else break_level + atr * 1.5
                entry = candle['close']
                risk = sl - entry
                
                return {
                    'signal': 'SHORT',
                    'type': 'CHOCH_REVERSAL',
                    'entry': entry,
                    'stop_loss': sl,
                    'target_1': entry - risk * 2.0,
                    'target_2': entry - risk * 3.0,
                    'target_3': entry - risk * 5.0,
                    'risk_reward_1': 2.0,
                    'risk_reward_2': 3.0,
                    'confidence': choch_event['confidence'] * 0.80,
                }
    
    return None
```

### 9.3 Entry Model 3: Failed BoS (Liquidity Grab) Entry

```python
def failed_bos_entry(candles, i, bos_attempt_index, bos_level, direction, atr):
    """
    Entry when a BoS attempt fails and reverses — extremely high probability setup.
    
    This is a liquidity grab: price breaks structure, captures stops,
    then reverses aggressively in the opposite direction.
    """
    c = candles[i]
    
    # A failed bullish BoS (broke above then reversed) = SHORT opportunity
    if direction == 'BULLISH_FAILED':
        # Price broke above swing high but now closing below it
        if c['close'] < bos_level:
            bars_since_break = i - bos_attempt_index
            
            if bars_since_break <= 5:  # Must fail quickly
                spike_high = max(cc['high'] for cc in candles[bos_attempt_index:i+1])
                
                return {
                    'signal': 'SHORT',
                    'type': 'FAILED_BOS_LIQUIDITY_GRAB',
                    'entry': c['close'],
                    'stop_loss': spike_high + atr * 0.3,
                    'target_1': bos_level - (spike_high - bos_level) * 2.0,
                    'target_2': bos_level - (spike_high - bos_level) * 4.0,
                    'confidence': 0.85,
                    'note': 'Failed bullish BoS = liquidity grab above resistance'
                }
    
    elif direction == 'BEARISH_FAILED':
        if c['close'] > bos_level:
            bars_since_break = i - bos_attempt_index
            
            if bars_since_break <= 5:
                spike_low = min(cc['low'] for cc in candles[bos_attempt_index:i+1])
                
                return {
                    'signal': 'LONG',
                    'type': 'FAILED_BOS_LIQUIDITY_GRAB',
                    'entry': c['close'],
                    'stop_loss': spike_low - atr * 0.3,
                    'target_1': bos_level + (bos_level - spike_low) * 2.0,
                    'target_2': bos_level + (bos_level - spike_low) * 4.0,
                    'confidence': 0.85,
                    'note': 'Failed bearish BoS = liquidity grab below support'
                }
    
    return None
```

---

## 10. Integration with Wyckoff

### 10.1 Structure Events Within Wyckoff Phases

| Wyckoff Event | Structure Event | Significance |
|---|---|---|
| **Selling Climax** | Creates a swing low (potential LL) | Defines range bottom |
| **Automatic Rally** | Creates a swing high (temporary) | Defines range top |
| **Spring** | Failed BoS below (breaks then reverses) | Highest probability reversal |
| **SOS** | Bullish BoS above Creek | Confirms accumulation → markup |
| **LPS** | Higher low (HL forming) | Confirms new bullish structure |
| **Buying Climax** | Creates a swing high (potential HH) | Defines range top |
| **UTAD** | Failed BoS above (breaks then reverses) | Highest probability short |
| **SOW** | Bearish BoS below Creek | Confirms distribution → markdown |
| **LPSY** | Lower high (LH forming) | Confirms new bearish structure |

### 10.2 Mapping Wyckoff Phases to Structure States

```
Wyckoff Phase → Structure Transition:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Markdown (LH + LL)                    ← BEARISH STRUCTURE
    │
    ↓ [Selling Climax = extreme LL]
    │
Accumulation (Ranging)                ← RANGING STRUCTURE
    │
    ↓ [Spring = failed bearish BoS]   ← FAILED BOS (reversal signal)
    │
    ↓ [SOS = bullish ChoCh]           ← BULLISH ChoCh
    │
    ↓ [LPS = first HL]               ← First HL confirms
    │
Markup (HH + HL)                      ← BULLISH STRUCTURE
    │
    ↓ [Buying Climax = extreme HH]
    │
Distribution (Ranging)                ← RANGING STRUCTURE
    │
    ↓ [UTAD = failed bullish BoS]     ← FAILED BOS (reversal signal)
    │
    ↓ [SOW = bearish ChoCh]           ← BEARISH ChoCh
    │
    ↓ [LPSY = first LH]              ← First LH confirms
    │
Markdown (LH + LL)                    ← BEARISH STRUCTURE
    │
    ↓ [Cycle repeats]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 10.3 Combined Confidence Model

When Wyckoff analysis and structure analysis agree:

$$
C_{\text{combined}} = 1 - (1 - C_{\text{wyckoff}}) \times (1 - C_{\text{structure}})
$$

This produces a combined confidence that is always higher than either individual confidence when both agree.

| Wyckoff Confidence | Structure Confidence | Combined | Trading Action |
|---|---|---|---|
| 0.80 (Spring) | 0.85 (Bullish ChoCh) | 0.97 | **Maximum position** |
| 0.70 (SOS) | 0.70 (Bullish BoS) | 0.91 | **Strong position** |
| 0.60 (LPS) | 0.65 (HL formed) | 0.86 | **Normal position** |
| 0.50 (Uncertain) | 0.40 (Weak signal) | 0.70 | **Reduced position** |

---

## 11. Risk Parameters

### 11.1 Risk by Structure Event Type

| Event | Direction | Max Risk | SL Placement | Min R:R | Notes |
|---|---|---|---|---|---|
| BoS Pullback | With trend | 1.5% | Below/above last swing | 2:1 | Standard trend trade |
| ChoCh Reversal | Counter (new) | 1.0% | Beyond invalidation | 3:1 | Higher R:R due to counter |
| Failed BoS | Against prior | 2.0% | Beyond spike | 3:1 | High confidence setup |
| Internal ChoCh (aligned) | With HTF | 1.5% | Below internal swing | 2:1 | Pullback timing entry |
| MTF Aligned BoS | With all TFs | 2.0% | Below last HTF swing | 2:1 | Highest confidence |

### 11.2 Stop Loss Rules

$$
SL_{\text{BoS}} = P_{\text{last\_swing}} - k \cdot ATR \quad \text{(for longs)}
$$

$$
SL_{\text{ChoCh}} = P_{\text{invalidation}} - k \cdot ATR \quad \text{(for longs)}
$$

Where $k$:
- Tight: 0.2 (aggressive, higher chance of stop hit)
- Standard: 0.5 (balanced)
- Wide: 1.0 (conservative, lower chance of stop hit)

---

## 12. Execution Flow

### 12.1 Complete Structure Trading Algorithm

```python
class StructureTradingSystem:
    """
    Complete system for trading based on market structure (BoS/ChoCh).
    """
    
    def __init__(self, config):
        self.config = config
        self.structure_engine = MarketStructureEngine(config)
        self.mtf_analyzer = MultiTimeframeStructureAnalyzer(config.get('timeframes'))
        self.positions = []
        self.pending_signals = []
    
    def on_new_bar(self, timeframe, candle, index, candles, atr, avg_volume):
        """
        Process a new bar on a specific timeframe.
        """
        # Update structure for this timeframe
        result = self.structure_engine.process_bar(candle, index, candles, atr, avg_volume)
        
        # Update MTF analyzer
        self.mtf_analyzer.update(timeframe, candles[:index+1], [atr] * (index+1))
        
        # Get MTF confluence
        confluence = self.mtf_analyzer.get_confluence_score()
        
        signals = []
        
        for event in result['new_events']:
            # Process BoS events
            if event['event'] == 'BOS':
                if self._validate_bos_trade(event, confluence):
                    signals.append(self._create_bos_signal(event, candle, atr, confluence))
            
            # Process ChoCh events
            elif event['event'] == 'CHOCH':
                if self._validate_choch_trade(event, confluence):
                    signals.append(self._create_choch_signal(event, candle, atr, confluence))
        
        # Check for pullback entries on pending signals
        for pending in self.pending_signals[:]:
            entry = self._check_pullback_entry(pending, candle, atr)
            if entry:
                signals.append(entry)
                self.pending_signals.remove(pending)
        
        return {
            'structure': result,
            'confluence': confluence,
            'signals': signals,
        }
    
    def _validate_bos_trade(self, bos_event, confluence):
        """Validate if BoS should generate a trade signal."""
        # BoS must align with MTF
        if bos_event['direction'] == 'BULLISH' and confluence['score'] < 0:
            return False
        if bos_event['direction'] == 'BEARISH' and confluence['score'] > 0:
            return False
        # Minimum grade
        if bos_event['grade'] == 'WEAK':
            return False
        return True
    
    def _validate_choch_trade(self, choch_event, confluence):
        """Validate if ChoCh should generate a trade signal."""
        # ChoCh needs at least moderate grade
        if choch_event['grade'] == 'WEAK':
            return False
        # ChoCh should not contradict higher TF
        # (allow if HTF is neutral or transitioning)
        if choch_event['direction'] == 'BULLISH' and confluence['score'] < -0.6:
            return False
        if choch_event['direction'] == 'BEARISH' and confluence['score'] > 0.6:
            return False
        return True
    
    def _create_bos_signal(self, event, candle, atr, confluence):
        """Create a pending signal for BoS pullback entry."""
        signal = {
            'type': 'BOS_PENDING_PULLBACK',
            'direction': 'LONG' if event['direction'] == 'BULLISH' else 'SHORT',
            'break_level': event['break_level'],
            'created_at': event['index'],
            'expires_at': event['index'] + 20,  # 20 bars to pull back
            'confidence': event['confidence'] * confluence['confidence'],
            'atr': atr,
        }
        self.pending_signals.append(signal)
        return signal
    
    def _create_choch_signal(self, event, candle, atr, confluence):
        """Create signal for ChoCh trade."""
        return {
            'type': 'CHOCH_SIGNAL',
            'direction': 'LONG' if event['direction'] == 'BULLISH' else 'SHORT',
            'break_level': event['break_level'],
            'invalidation': event.get('invalidation'),
            'confidence': event['confidence'] * max(0.5, confluence['confidence']),
            'atr': atr,
        }
```

---

## 13. References

### 13.1 Market Structure and Price Action

1. Brooks, A. (2012). *Trading Price Action Trends*. Wiley. — Swing point definitions and trend analysis.
2. Brooks, A. (2012). *Trading Price Action Reversals*. Wiley. — Structure breaks and trend changes.
3. Belaief, M. (2019). *ICT Mentorship — Market Structure Concepts*. innercircletrader.com.

### 13.2 Smart Money Concepts

4. ICT (Inner Circle Trader). "Market Structure, BoS, and ChoCh." YouTube Educational Series (2016–2023).
5. Phantom Trading. "Internal vs External Structure." phantomtradingfx.com (2021).
6. The Trading Hub. "Multi-Timeframe Structure Analysis." (2022).

### 13.3 Academic References

7. Lo, A.W. & MacKinlay, A.C. (1988). "Stock Market Prices Do Not Follow Random Walks." *Review of Financial Studies*, 1(1), 41–66.
8. Brock, W., Lakonishok, J., & LeBaron, B. (1992). "Simple Technical Trading Rules and the Stochastic Properties of Stock Returns." *Journal of Finance*, 47(5), 1731–1764.

### 13.4 Algorithmic Implementation

9. Prado, M.L. de (2018). *Advances in Financial Machine Learning*. Wiley. — Chapter on structural breaks in financial time series.
10. Chan, E.P. (2013). *Algorithmic Trading*. Wiley. — Trend detection and regime switching.

---

> **Next Document**: `04_wyckoff_volume_analysis.md` — Volume Spread Analysis (VSA)
