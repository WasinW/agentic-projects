# Price Action Trading — Complete Guide

## Document Metadata
| Field | Value |
|---|---|
| **Strategy ID** | PA-001 |
| **Category** | Technical Analysis / Pure Price Action |
| **Asset Classes** | Forex, Crypto, Equities, Commodities |
| **Timeframes** | M5 to Monthly (primary: H1–D1) |
| **Complexity** | Intermediate |
| **AI Suitability** | High — pattern recognition is algorithmic |
| **Version** | 2.0 |
| **Last Updated** | 2026-04-12 |

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Candlestick Patterns — Single Candle](#2-candlestick-patterns--single-candle)
3. [Candlestick Patterns — Multi-Candle](#3-candlestick-patterns--multi-candle)
4. [Chart Patterns — Reversal](#4-chart-patterns--reversal)
5. [Chart Patterns — Continuation](#5-chart-patterns--continuation)
6. [Trend Lines and Channels](#6-trend-lines-and-channels)
7. [Support and Resistance Identification](#7-support-and-resistance-identification)
8. [Pattern Recognition Algorithms](#8-pattern-recognition-algorithms)
9. [Entry and Exit Logic](#9-entry-and-exit-logic)
10. [Statistical Win Rates](#10-statistical-win-rates)
11. [Mathematical Models](#11-mathematical-models)
12. [Risk Parameters](#12-risk-parameters)
13. [Execution Flow](#13-execution-flow)
14. [AI Implementation Notes](#14-ai-implementation-notes)
15. [References](#15-references)

---

## 1. Introduction

Price Action Trading is the discipline of making trading decisions based solely on the raw price movement displayed on charts, without reliance on lagging indicators. Every candlestick, every swing, and every chart formation tells a story about the battle between buyers and sellers.

### 1.1 Core Philosophy

- Price is the ultimate indicator — it reflects all known information.
- Candlestick formations reveal the psychology of market participants.
- Chart patterns represent the fractal nature of supply/demand imbalances.
- Context (trend, location relative to S/R) is more important than any individual pattern.

### 1.2 The Context Framework

Every price action signal must be evaluated within context:

$$\text{Signal Quality} = f(\text{Pattern}, \text{Trend}, \text{Location}, \text{Momentum})$$

- **Pattern**: The specific candlestick or chart pattern.
- **Trend**: Is the signal with or against the prevailing trend?
- **Location**: Is the signal at a significant level (S/R, round number)?
- **Momentum**: Does the signal have strong or weak follow-through?

---

## 2. Candlestick Patterns — Single Candle

### 2.1 Pin Bar (Hammer / Shooting Star)

**Structure**:
- Long wick (shadow) in one direction — at least 2x the body length.
- Small body at the opposite end of the range.
- Indicates rejection of a price level.

**Bullish Pin Bar (Hammer)**:
- Long lower wick (shadow).
- Small body near the top of the candle.
- Close can be bullish or bearish (bullish preferred).

**Detection Criteria**:
$$\text{BullishPin} = \begin{cases} \text{LowerWick} \geq 2 \times \text{Body} \\ \text{UpperWick} \leq 0.25 \times \text{TotalRange} \\ \text{Body} \leq 0.33 \times \text{TotalRange} \end{cases}$$

Where:
$$\text{Body} = |C - O|$$
$$\text{LowerWick} = \min(O, C) - L$$
$$\text{UpperWick} = H - \max(O, C)$$
$$\text{TotalRange} = H - L$$

**Bearish Pin Bar (Shooting Star)**:
$$\text{BearishPin} = \begin{cases} \text{UpperWick} \geq 2 \times \text{Body} \\ \text{LowerWick} \leq 0.25 \times \text{TotalRange} \\ \text{Body} \leq 0.33 \times \text{TotalRange} \end{cases}$$

**Signal Strength Modifiers**:
- Wick pierces a key S/R level: +30% confidence.
- Pin bar range > 1.5 ATR: strong rejection signal.
- Pin bar at the high/low of the day: +20% confidence.
- Pin bar nose (wick tip) wicks beyond prior candle range: +25% confidence.

### 2.2 Doji

**Structure**: Open and close are virtually the same (body $\leq$ 10% of range).

**Types**:

| Doji Type | Condition | Signal |
|-----------|-----------|--------|
| **Standard Doji** | Body $\leq 10\%$ range, wicks roughly equal | Indecision |
| **Dragonfly Doji** | Long lower wick, no upper wick | Bullish (at lows) |
| **Gravestone Doji** | Long upper wick, no lower wick | Bearish (at highs) |
| **Long-Legged Doji** | Long both wicks, tiny body | Extreme indecision / reversal |

**Detection**:
$$\text{Doji} = \frac{|C - O|}{H - L} \leq 0.10$$

$$\text{DragonflyDoji} = \text{Doji} \text{ AND } \frac{H - \max(O,C)}{H - L} \leq 0.10$$

$$\text{GravestoneDoji} = \text{Doji} \text{ AND } \frac{\min(O,C) - L}{H - L} \leq 0.10$$

### 2.3 Marubozu

**Structure**: Full-bodied candle with minimal or no wicks — indicates strong directional commitment.

$$\text{Marubozu} = \frac{|C - O|}{H - L} \geq 0.90$$

**Bullish Marubozu**: $C \gg O$, no lower/upper wick. Signals strong buying momentum.
**Bearish Marubozu**: $O \gg C$, no lower/upper wick. Signals strong selling momentum.

### 2.4 Spinning Top

**Structure**: Small body with wicks on both sides (longer than body but not as extreme as Doji).

$$\text{SpinningTop} = 0.10 < \frac{|C - O|}{H - L} \leq 0.33 \quad \text{AND} \quad \text{UpperWick} > \text{Body} \quad \text{AND} \quad \text{LowerWick} > \text{Body}$$

**Signal**: Indecision; trend weakening. Most useful after a strong trend move.

---

## 3. Candlestick Patterns — Multi-Candle

### 3.1 Engulfing Pattern

**Bullish Engulfing**:
- Candle 1: Bearish (red/black body).
- Candle 2: Bullish (green/white body) that completely engulfs candle 1's body.

$$\text{BullishEngulfing} = \begin{cases} O_1 > C_1 \quad \text{(candle 1 is bearish)} \\ C_2 > O_2 \quad \text{(candle 2 is bullish)} \\ O_2 \leq C_1 \quad \text{(open 2 at or below close 1)} \\ C_2 \geq O_1 \quad \text{(close 2 at or above open 1)} \end{cases}$$

**Bearish Engulfing**:
$$\text{BearishEngulfing} = \begin{cases} C_1 > O_1 \quad \text{(candle 1 is bullish)} \\ O_2 > C_2 \quad \text{(candle 2 is bearish)} \\ O_2 \geq C_1 \quad \text{(open 2 at or above close 1)} \\ C_2 \leq O_1 \quad \text{(close 2 at or below open 1)} \end{cases}$$

**Quality Enhancement**: The engulfing candle should also engulf the FULL RANGE (high to low) of candle 1, not just the body. This is called a "full engulfing."

### 3.2 Inside Bar

**Structure**: Candle 2's entire range (high to low) is contained within candle 1's range.

$$\text{InsideBar} = H_2 \leq H_1 \quad \text{AND} \quad L_2 \geq L_1$$

**Signal**: Compression/consolidation. Trade the breakout direction.

**Entry Rules**:
- **Long**: Buy stop above $H_1$ (mother bar high).
- **Short**: Sell stop below $L_1$ (mother bar low).
- **SL**: Opposite side of mother bar.

**Stacking**: Multiple consecutive inside bars ("inside bar coil") compress volatility further, leading to explosive breakouts.

### 3.3 Outside Bar (Engulfing Range)

**Structure**: Candle 2's range fully engulfs candle 1's range.

$$\text{OutsideBar} = H_2 > H_1 \quad \text{AND} \quad L_2 < L_1$$

**Signal**: Strong momentum. Trade in the direction of the outside bar's close.

### 3.4 Morning Star / Evening Star

**Morning Star (Bullish Reversal)** — Three-candle pattern:
1. Candle 1: Large bearish candle.
2. Candle 2: Small-bodied candle (star) that gaps below candle 1's close. In forex/crypto (no gaps), the star's body should be small and positioned below candle 1's close.
3. Candle 3: Large bullish candle closing above the midpoint of candle 1.

$$\text{MorningStar} = \begin{cases} |C_1 - O_1| > 0.7 \times \text{ATR} \quad \text{(large bearish)} \\ |C_2 - O_2| < 0.3 \times |C_1 - O_1| \quad \text{(small body)} \\ C_3 > \frac{O_1 + C_1}{2} \quad \text{(closes above midpoint of candle 1)} \\ C_3 > O_3 \quad \text{(candle 3 is bullish)} \end{cases}$$

**Evening Star (Bearish Reversal)**: Mirror image.

### 3.5 Three White Soldiers / Three Black Crows

**Three White Soldiers**:
- Three consecutive bullish candles.
- Each opens within the body of the prior candle.
- Each closes near its high (small upper wicks).
- Each candle's close exceeds the prior candle's close.

$$\text{ThreeWhiteSoldiers} = \begin{cases} C_i > O_i \quad \forall i \in \{1, 2, 3\} \\ O_{i+1} > O_i \text{ AND } O_{i+1} < C_i \quad \forall i \in \{1, 2\} \\ C_{i+1} > C_i \quad \forall i \in \{1, 2\} \\ (H_i - C_i) < 0.25 \times (C_i - O_i) \quad \forall i \quad \text{(small upper wick)} \end{cases}$$

**Three Black Crows**: Mirror image (three consecutive large bearish candles).

### 3.6 Tweezer Top / Bottom

**Tweezer Bottom (Bullish)**:
- Two or more consecutive candles with approximately equal lows.
- Occurs at a support level or after a downtrend.

$$\text{TweezerBottom} = |L_1 - L_2| \leq 0.05 \times \text{ATR}$$

**Tweezer Top (Bearish)**:
$$\text{TweezerTop} = |H_1 - H_2| \leq 0.05 \times \text{ATR}$$

### 3.7 Harami (Inside Day)

**Bullish Harami**:
- Candle 1: Large bearish candle.
- Candle 2: Small bullish candle whose body is entirely within candle 1's body.

$$\text{BullishHarami} = \begin{cases} O_1 > C_1 \quad \text{(bearish mother)} \\ C_2 > O_2 \quad \text{(bullish child)} \\ O_2 > C_1 \text{ AND } C_2 < O_1 \quad \text{(child body within mother body)} \end{cases}$$

---

## 4. Chart Patterns — Reversal

### 4.1 Head and Shoulders

**Structure**:
- Left Shoulder: A swing high followed by a pullback.
- Head: A higher swing high followed by a pullback to approximately the same level as the first pullback.
- Right Shoulder: A lower swing high (approximately level with left shoulder) followed by a break below the neckline.

**Neckline**: The line connecting the two pullback lows (between left shoulder-head and head-right shoulder).

**Detection Algorithm**:
```python
def detect_head_shoulders(swings, tolerance_pct=0.03):
    """
    Detect Head and Shoulders top pattern.
    """
    patterns = []
    
    # Need at least 5 alternating swings: H-L-H-L-H (High-Low-High-Low-High)
    highs = [s for s in swings if s["type"] == "HIGH"]
    lows = [s for s in swings if s["type"] == "LOW"]
    
    for i in range(len(highs) - 2):
        ls, head, rs = highs[i], highs[i+1], highs[i+2]
        
        # Head must be higher than both shoulders
        if not (head["price"] > ls["price"] and head["price"] > rs["price"]):
            continue
        
        # Shoulders should be approximately equal
        shoulder_diff = abs(ls["price"] - rs["price"]) / ls["price"]
        if shoulder_diff > tolerance_pct:
            continue
        
        # Find neckline lows (between LS-Head and Head-RS)
        nl_left = find_low_between(lows, ls["index"], head["index"])
        nl_right = find_low_between(lows, head["index"], rs["index"])
        
        if nl_left is None or nl_right is None:
            continue
        
        # Neckline
        neckline_slope = (nl_right["price"] - nl_left["price"]) / (nl_right["index"] - nl_left["index"])
        neckline_at_rs = nl_left["price"] + neckline_slope * (rs["index"] - nl_left["index"])
        
        patterns.append({
            "type": "HEAD_AND_SHOULDERS",
            "direction": "BEARISH",
            "left_shoulder": ls,
            "head": head,
            "right_shoulder": rs,
            "neckline_left": nl_left,
            "neckline_right": nl_right,
            "neckline_slope": neckline_slope,
            "target": neckline_at_rs - (head["price"] - neckline_at_rs),  # Measured move
            "quality": calculate_hs_quality(ls, head, rs, nl_left, nl_right)
        })
    
    return patterns
```

**Target Calculation (Measured Move)**:
$$\text{Target} = \text{Neckline} - (\text{Head} - \text{Neckline})$$

**Inverse Head and Shoulders** (bullish reversal): Mirror image.

### 4.2 Double Top

**Structure**: Two swing highs at approximately the same level, separated by a pullback.

**Detection**:
$$\text{DoubleTop} = \begin{cases} |H_1 - H_2| \leq 0.02 \times H_1 \\ \text{Pullback between peaks} \geq 0.10 \times (H_1 - \text{prior\_low}) \\ H_2 \text{ fails to exceed } H_1 \text{ with conviction} \end{cases}$$

**Entry**: Short on break below the pullback low (neckline).
**Target**: Neckline - (Peak - Neckline).

### 4.3 Double Bottom

**Structure**: Two swing lows at approximately the same level.

$$\text{DoubleBottom} = |L_1 - L_2| \leq 0.02 \times L_1$$

**Entry**: Long on break above the pullback high.
**Target**: Neckline + (Neckline - Trough).

### 4.4 Triple Top / Triple Bottom

Three tests of approximately the same level. Same logic as double top/bottom but with an additional touch. Higher reliability due to confirmed resistance/support.

### 4.5 Rounding Bottom (Saucer)

A gradual transition from bearish to bullish, forming a U-shape over many candles (30–100+). Best suited for Daily and Weekly timeframes.

**Detection**: Use curve fitting — fit a quadratic function to the lows and check for positive second derivative (concavity).

$$L_i \approx a(i - i_{\text{center}})^2 + L_{\text{min}}$$

Where $a > 0$ indicates a rounding bottom.

---

## 5. Chart Patterns — Continuation

### 5.1 Triangles

**Ascending Triangle (Bullish)**:
- Flat resistance (horizontal upper boundary).
- Rising support (ascending lower boundary).
- Price compresses into the apex.
- Breakout expected to the upside.

**Detection**:
```python
def detect_ascending_triangle(swings, candles, min_touches=2):
    highs = [s for s in swings if s["type"] == "HIGH"]
    lows = [s for s in swings if s["type"] == "LOW"]
    
    # Flat resistance: highs at approximately the same level
    if len(highs) < min_touches:
        return None
    
    resistance_level = np.mean([h["price"] for h in highs[-min_touches:]])
    resistance_flat = all(
        abs(h["price"] - resistance_level) / resistance_level < 0.01 
        for h in highs[-min_touches:]
    )
    
    # Rising support: lows forming an ascending trendline
    if len(lows) < min_touches:
        return None
    
    slope, intercept = np.polyfit(
        [l["index"] for l in lows[-min_touches:]], 
        [l["price"] for l in lows[-min_touches:]], 1
    )
    rising_support = slope > 0
    
    if resistance_flat and rising_support:
        return {
            "type": "ASCENDING_TRIANGLE",
            "resistance": resistance_level,
            "support_slope": slope,
            "support_intercept": intercept,
            "target": resistance_level + (resistance_level - lows[-1]["price"])
        }
    
    return None
```

**Descending Triangle (Bearish)**: Flat support + descending resistance.

**Symmetrical Triangle (Neutral)**: Both boundaries converging. Breakout direction unknown; trade the break.

### 5.2 Wedges

**Rising Wedge (Bearish)**:
- Both support and resistance lines slope upward.
- The support line is steeper than the resistance line (converging).
- Typically breaks to the downside.

**Falling Wedge (Bullish)**:
- Both lines slope downward.
- The resistance line is steeper than the support line.
- Typically breaks to the upside.

**Detection**: Fit linear regression to swing highs and swing lows separately, then compare slopes.

$$\text{RisingWedge} = \begin{cases} \text{Slope}_{\text{highs}} > 0 \\ \text{Slope}_{\text{lows}} > 0 \\ \text{Slope}_{\text{lows}} > \text{Slope}_{\text{highs}} \quad \text{(converging)} \end{cases}$$

### 5.3 Flags

**Bull Flag**:
- Strong impulse move up (the "pole").
- Tight consolidation channel sloping downward (the "flag").
- Breakout above the flag continues the uptrend.

**Detection**:
$$\text{BullFlag} = \begin{cases} \text{Pole}: |\text{impulse}| > 2 \times \text{ATR}(14) \text{ in } \leq 5 \text{ candles} \\ \text{Flag}: \text{consolidation with negative slope, range} < 50\% \text{ of pole} \\ \text{Duration}: \text{Flag } \leq 20 \text{ candles} \end{cases}$$

**Bear Flag**: Mirror image (downward pole, upward-sloping flag).

**Target**: Pole height projected from breakout point.
$$\text{Target} = \text{Breakout Level} + |\text{Pole Height}|$$

### 5.4 Pennants

Similar to flags but the consolidation forms a small symmetrical triangle rather than a parallel channel.

**Detection**: Same as flag but with converging rather than parallel boundaries.

### 5.5 Cup and Handle

**Structure**:
- **Cup**: A rounding bottom formation (U-shape).
- **Handle**: A small pullback (flag or pennant) after the cup completes.
- Breakout above the handle's high = entry.

**Target**:
$$\text{Target} = \text{Cup Rim} + \text{Cup Depth}$$

**Detection**: Fit a parabola to the cup lows, verify the handle forms at the cup rim level.

---

## 6. Trend Lines and Channels

### 6.1 Trend Line Construction

**Uptrend Line**: Connect two or more significant swing lows with a straight line.
**Downtrend Line**: Connect two or more significant swing highs with a straight line.

**Algorithm (Least Squares with Outlier Rejection)**:
```python
def fit_trendline(swing_points, type="support", max_violations=1):
    """
    Fit a trendline through swing points using iterative RANSAC-like approach.
    """
    if type == "support":
        points = [(s["index"], s["price"]) for s in swing_points if s["type"] == "LOW"]
    else:
        points = [(s["index"], s["price"]) for s in swing_points if s["type"] == "HIGH"]
    
    if len(points) < 2:
        return None
    
    best_line = None
    best_inliers = 0
    
    # Try all pairs
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            x1, y1 = points[i]
            x2, y2 = points[j]
            
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            
            # Count inliers (points close to the line)
            inliers = 0
            violations = 0
            
            for px, py in points:
                line_y = slope * px + intercept
                distance = py - line_y if type == "support" else line_y - py
                
                if distance >= -0.001 * abs(line_y):  # On or above for support
                    inliers += 1
                else:
                    violations += 1
            
            if violations <= max_violations and inliers > best_inliers:
                best_inliers = inliers
                best_line = {"slope": slope, "intercept": intercept, "touches": inliers}
    
    return best_line
```

### 6.2 Channel Construction

A channel consists of two parallel trend lines:
- **Ascending Channel**: Support trendline (lower) + parallel resistance line (upper).
- **Descending Channel**: Resistance trendline (upper) + parallel support line (lower).

**Channel Width**:
$$W_{\text{channel}} = \frac{|y_{\text{upper}} - y_{\text{lower}}|_{\text{at any x}}}{\cos(\theta)}$$

Where $\theta = \arctan(\text{slope})$.

### 6.3 Trendline Trading Rules

| Signal | Entry | SL | TP |
|--------|-------|-----|-----|
| Trendline bounce (support) | Buy at trendline + buffer | Below trendline by 1 ATR | Opposite channel boundary |
| Trendline break (support) | Sell on retest of broken trendline | Above broken trendline by 1 ATR | Measured move (channel width projected down) |
| Channel top rejection | Sell at upper boundary | Above upper boundary by 0.5 ATR | Lower channel boundary |

---

## 7. Support and Resistance Identification

### 7.1 Algorithm: Cluster-Based S/R

```python
def identify_sr_levels(candles, lookback=200, min_touches=3, cluster_threshold_atr=0.3):
    """
    Identify significant support/resistance levels using price clustering.
    """
    atr = calculate_atr(candles, 14)[-1]
    
    # Collect all swing highs and lows
    swings = find_swing_points(candles[-lookback:], lookback=5)
    
    # Collect all significant price levels
    levels = [s["price"] for s in swings]
    
    # Add open/close of large-bodied candles
    for c in candles[-lookback:]:
        if abs(c.close - c.open) > 1.5 * atr:
            levels.extend([c.open, c.close])
    
    # Cluster nearby levels
    clusters = []
    levels.sort()
    
    current_cluster = [levels[0]]
    for i in range(1, len(levels)):
        if levels[i] - levels[i-1] <= cluster_threshold_atr * atr:
            current_cluster.append(levels[i])
        else:
            if len(current_cluster) >= min_touches:
                clusters.append({
                    "level": np.median(current_cluster),
                    "touches": len(current_cluster),
                    "strength": len(current_cluster) / min_touches
                })
            current_cluster = [levels[i]]
    
    # Don't forget the last cluster
    if len(current_cluster) >= min_touches:
        clusters.append({
            "level": np.median(current_cluster),
            "touches": len(current_cluster),
            "strength": len(current_cluster) / min_touches
        })
    
    return sorted(clusters, key=lambda x: x["strength"], reverse=True)
```

### 7.2 S/R Strength Factors

$$S_{\text{SR}} = w_1 \cdot T + w_2 \cdot V + w_3 \cdot R + w_4 \cdot A$$

Where:
- $T$ = number of touches (normalized: $\min(T/5, 1)$)
- $V$ = volume at level (if available, normalized)
- $R$ = recency of last touch (exponential decay)
- $A$ = age of the level (older levels that still hold are stronger)

### 7.3 Round Numbers and Psychological Levels

For forex: 00, 20, 50, 80, 00 levels (e.g., 1.0800, 1.0850, 1.0900).
For crypto: Major round numbers (BTC: 50000, 55000, 60000, etc.).

These serve as natural S/R due to cluster of pending orders.

$$\text{RoundNumberLevel}(P, \text{granularity}) = \text{round}(P / \text{granularity}) \times \text{granularity}$$

---

## 8. Pattern Recognition Algorithms

### 8.1 Composite Pattern Detector

```python
class PriceActionDetector:
    def __init__(self, candles, atr_period=14):
        self.candles = candles
        self.atr = calculate_atr(candles, atr_period)
    
    def detect_all_signals(self, index=-1):
        """
        Detect all price action signals at the given candle index.
        Returns a list of signals with type and confidence.
        """
        signals = []
        i = index if index >= 0 else len(self.candles) + index
        c = self.candles
        atr = self.atr[i]
        
        # Single candle patterns
        if self._is_bullish_pin(c[i], atr):
            signals.append({"type": "BULLISH_PIN", "confidence": 0.6, "candle": i})
        
        if self._is_bearish_pin(c[i], atr):
            signals.append({"type": "BEARISH_PIN", "confidence": 0.6, "candle": i})
        
        if self._is_doji(c[i]):
            signals.append({"type": "DOJI", "confidence": 0.3, "candle": i})
        
        # Multi-candle patterns (need i >= 1)
        if i >= 1:
            if self._is_bullish_engulfing(c[i-1], c[i]):
                signals.append({"type": "BULLISH_ENGULFING", "confidence": 0.65, "candle": i})
            
            if self._is_bearish_engulfing(c[i-1], c[i]):
                signals.append({"type": "BEARISH_ENGULFING", "confidence": 0.65, "candle": i})
            
            if self._is_inside_bar(c[i-1], c[i]):
                signals.append({"type": "INSIDE_BAR", "confidence": 0.50, "candle": i})
        
        # Three-candle patterns (need i >= 2)
        if i >= 2:
            if self._is_morning_star(c[i-2], c[i-1], c[i], atr):
                signals.append({"type": "MORNING_STAR", "confidence": 0.70, "candle": i})
            
            if self._is_evening_star(c[i-2], c[i-1], c[i], atr):
                signals.append({"type": "EVENING_STAR", "confidence": 0.70, "candle": i})
            
            if self._is_three_white_soldiers(c[i-2], c[i-1], c[i]):
                signals.append({"type": "THREE_WHITE_SOLDIERS", "confidence": 0.72, "candle": i})
            
            if self._is_three_black_crows(c[i-2], c[i-1], c[i]):
                signals.append({"type": "THREE_BLACK_CROWS", "confidence": 0.72, "candle": i})
        
        # Apply context modifiers
        for signal in signals:
            signal["adjusted_confidence"] = self._apply_context(signal, i)
        
        return signals
    
    def _apply_context(self, signal, index):
        """Apply contextual modifiers to confidence."""
        base = signal["confidence"]
        
        # Trend alignment
        trend = self._determine_trend(index)
        if self._signal_aligns_with_trend(signal, trend):
            base *= 1.2
        elif self._signal_opposes_trend(signal, trend):
            base *= 0.7
        
        # Location (at S/R level)
        if self._at_sr_level(index):
            base *= 1.25
        
        # Momentum (ADX or similar)
        if self._strong_momentum(index):
            base *= 1.1
        
        return min(base, 1.0)
```

---

## 9. Entry and Exit Logic

### 9.1 Candlestick Pattern Entry Rules

| Pattern | Entry Trigger | SL | TP Method |
|---------|--------------|-----|-----------|
| Bullish Pin Bar | Buy stop above pin high | Below pin low | 2R minimum, next S/R |
| Bearish Pin Bar | Sell stop below pin low | Above pin high | 2R minimum, next S/R |
| Bullish Engulfing | Buy on close or buy stop above engulfing high | Below engulfing low | 2R minimum |
| Bearish Engulfing | Sell on close or sell stop below engulfing low | Above engulfing high | 2R minimum |
| Inside Bar | Buy stop above mother high OR sell stop below mother low | Opposite side of mother bar | 2–3R |
| Morning Star | Buy on close of candle 3 | Below candle 2 low | 2R |
| Evening Star | Sell on close of candle 3 | Above candle 2 high | 2R |

### 9.2 Chart Pattern Entry Rules

| Pattern | Entry | SL | TP (Measured Move) |
|---------|-------|-----|-------------------|
| H&S | Break below neckline | Above right shoulder high | Neckline - (Head - Neckline) |
| Inv H&S | Break above neckline | Below right shoulder low | Neckline + (Neckline - Head) |
| Double Top | Break below neckline | Above the two highs | Neckline - (Peak - Neckline) |
| Double Bottom | Break above neckline | Below the two lows | Neckline + (Neckline - Trough) |
| Ascending Triangle | Break above flat resistance | Below last swing low | Height of triangle projected up |
| Descending Triangle | Break below flat support | Above last swing high | Height projected down |
| Bull Flag | Break above flag high | Below flag low | Pole height projected up |
| Bear Flag | Break below flag low | Above flag high | Pole height projected down |
| Cup & Handle | Break above handle high | Below handle low | Cup depth projected up |

### 9.3 Breakout Validation

Not all breakouts are genuine. Validate with:

1. **Volume**: Breakout candle should have above-average volume (if available).
2. **Candle close**: Price must CLOSE beyond the breakout level (not just wick).
3. **Follow-through**: The candle after the breakout should not fully reverse.
4. **Retest**: Ideal breakouts retest the broken level as new S/R.

$$\text{ValidBreakout} = C_i > \text{Level} \quad \text{AND} \quad C_{i+1} > \text{Level} \quad \text{AND} \quad V_i > 1.5 \times V_{\text{avg20}}$$

---

## 10. Statistical Win Rates

### 10.1 Candlestick Pattern Performance (Empirical Data)

Based on Bulkowski (2008) and various backtests across forex/crypto:

| Pattern | Theoretical Edge | Win Rate (With Trend) | Win Rate (Counter-Trend) | Avg R:R |
|---------|-----------------|----------------------|-------------------------|---------|
| Bullish Pin Bar | Strong | 58–65% | 48–53% | 1.5:1 |
| Bearish Pin Bar | Strong | 57–63% | 47–52% | 1.5:1 |
| Bullish Engulfing | Moderate | 55–62% | 45–50% | 1.4:1 |
| Bearish Engulfing | Moderate | 54–60% | 44–49% | 1.4:1 |
| Morning Star | Strong | 60–68% | 50–55% | 1.6:1 |
| Evening Star | Strong | 59–66% | 49–54% | 1.6:1 |
| Inside Bar Breakout | Variable | 52–58% | 45–52% | 1.8:1 |
| Three White Soldiers | Strong | 62–70% | 52–58% | 1.3:1 |

### 10.2 Chart Pattern Performance

| Pattern | Success Rate (Bulkowski) | Avg Profit | Failure Rate |
|---------|-------------------------|-----------|--------------|
| Head & Shoulders | 83% (reach target) | 15–20% | 17% |
| Inv Head & Shoulders | 74% | 20–25% | 26% |
| Double Top | 73% | 15–20% | 27% |
| Double Bottom | 78% | 20–25% | 22% |
| Ascending Triangle (up break) | 75% | 35–40% | 25% |
| Descending Triangle (down break) | 72% | 30–35% | 28% |
| Bull Flag | 67% | 20–25% | 33% |
| Cup & Handle | 65% | 30–40% | 35% |

*Note: These rates assume proper context (trend alignment) and breakout confirmation.*

---

## 11. Mathematical Models

### 11.1 Pattern Confidence Scoring

$$\text{Confidence} = P_{\text{base}} \times M_{\text{trend}} \times M_{\text{location}} \times M_{\text{TF}} \times M_{\text{volume}}$$

Where:
- $P_{\text{base}}$ = base win rate of the pattern from historical data
- $M_{\text{trend}}$ = trend multiplier: $1.2$ (with trend), $1.0$ (neutral), $0.7$ (counter-trend)
- $M_{\text{location}}$ = location multiplier: $1.25$ (at key S/R), $1.0$ (elsewhere)
- $M_{\text{TF}}$ = timeframe multiplier: $1.2$ (D1+), $1.0$ (H1–H4), $0.8$ (M15 and below)
- $M_{\text{volume}}$ = volume confirmation: $1.15$ (high volume), $1.0$ (normal)

### 11.2 Measured Move Calculation

For chart patterns with a measured move target:

$$\text{Target} = \text{Breakout Level} \pm \text{Pattern Height} \times k$$

Where $k$ is the pattern-specific projection factor:

| Pattern | $k$ (conservative) | $k$ (standard) | $k$ (aggressive) |
|---------|-------|----------|------------|
| H&S | 0.75 | 1.00 | 1.272 |
| Double Top/Bottom | 0.75 | 1.00 | 1.618 |
| Triangle | 0.75 | 1.00 | 1.272 |
| Flag | 0.618 | 1.00 | 1.272 |
| Cup & Handle | 0.618 | 1.00 | 1.618 |

### 11.3 Breakout Probability Model

The probability of a successful breakout from a consolidation pattern:

$$P(\text{breakout success}) = \sigma\left(\beta_0 + \beta_1 \cdot V_{\text{ratio}} + \beta_2 \cdot T_{\text{compression}} + \beta_3 \cdot D_{\text{trend}}\right)$$

Where:
- $V_{\text{ratio}}$ = breakout volume / average volume
- $T_{\text{compression}}$ = number of candles in consolidation (normalized)
- $D_{\text{trend}}$ = trend direction alignment (1 = with, 0 = against)

### 11.4 Support/Resistance Decay Model

The strength of an S/R level decays with each touch:

$$S(n) = S_0 \times \alpha^{n-1}$$

Where:
- $S_0$ = initial strength (based on the impulse that created the level)
- $n$ = number of touches
- $\alpha = 0.7$ (each touch absorbs ~30% of remaining orders)

After $n \geq 4$ touches, the level is likely to break:
$$P(\text{break}) = 1 - \alpha^{n-1}$$

---

## 12. Risk Parameters

### 12.1 Stop Loss Strategies

| Strategy | Method | Best For |
|----------|--------|----------|
| **Pattern-Based SL** | Beyond the pattern's invalidation level | All patterns |
| **ATR-Based SL** | Entry $\pm$ $k \times$ ATR(14), $k = 1.0$–$1.5$ | When pattern SL is too tight |
| **Structure-Based SL** | Beyond the nearest swing high/low | Trend continuation trades |
| **Time-Based SL** | Close if no movement within $n$ candles | Breakout trades |

### 12.2 Position Sizing

$$\text{Size} = \frac{\text{Balance} \times R\%}{|\text{Entry} - \text{SL}| \times \text{Pip Value}}$$

Risk allocation by signal confidence:

| Adjusted Confidence | Risk % |
|--------------------|--------|
| $\geq 0.75$ | 1.5% |
| 0.60 – 0.74 | 1.0% |
| 0.45 – 0.59 | 0.5% |
| $< 0.45$ | No trade |

### 12.3 Maximum Exposure Rules

- Maximum 3 trades open simultaneously from price action signals.
- Maximum 4% total risk deployed at any time.
- No more than 2 trades in the same direction on correlated instruments.
- If win rate drops below 40% over the last 20 trades, reduce risk to 0.5% and review.

---

## 13. Execution Flow

### 13.1 Complete Strategy Pseudocode

```python
def price_action_strategy():
    """
    Complete price action trading strategy.
    """
    
    # ================================================
    # PHASE 1: CONTEXT DETERMINATION
    # ================================================
    
    for instrument in watchlist:
        # Determine HTF trend
        htf_candles = fetch_candles(instrument, "D1", count=100)
        htf_trend = determine_trend(htf_candles)  # BULLISH / BEARISH / RANGING
        
        # Identify key S/R levels
        sr_levels = identify_sr_levels(htf_candles)
        
        # ================================================
        # PHASE 2: PATTERN SCANNING
        # ================================================
        
        # Scan trading timeframe for signals
        tf_candles = fetch_candles(instrument, "H4", count=200)
        atr = calculate_atr(tf_candles, 14)
        
        # Candlestick patterns
        detector = PriceActionDetector(tf_candles)
        candle_signals = detector.detect_all_signals()
        
        # Chart patterns
        swings = find_swing_points(tf_candles, lookback=5)
        chart_patterns = detect_chart_patterns(swings, tf_candles)
        
        # ================================================
        # PHASE 3: SIGNAL FILTERING
        # ================================================
        
        all_signals = candle_signals + chart_patterns
        
        # Filter by confidence
        actionable = [s for s in all_signals if s.get("adjusted_confidence", 0) >= 0.45]
        
        # Filter by location (must be near S/R for candlestick patterns)
        for signal in actionable:
            if signal["type"] in CANDLESTICK_PATTERNS:
                if not near_sr_level(tf_candles[-1], sr_levels, atr[-1]):
                    signal["adjusted_confidence"] *= 0.6  # Reduce if not at S/R
        
        # Re-filter after adjustment
        actionable = [s for s in actionable if s.get("adjusted_confidence", 0) >= 0.45]
        
        if not actionable:
            continue
        
        # Sort by confidence
        actionable.sort(key=lambda s: s["adjusted_confidence"], reverse=True)
        best_signal = actionable[0]
        
        # ================================================
        # PHASE 4: TRADE SETUP
        # ================================================
        
        entry, sl, tp = calculate_trade_parameters(best_signal, tf_candles, sr_levels, atr[-1])
        
        # Validate R:R
        rr = abs(tp - entry) / abs(entry - sl)
        min_rr = get_min_rr(best_signal["adjusted_confidence"])
        
        if rr < min_rr:
            continue
        
        # ================================================
        # PHASE 5: RISK CHECK AND EXECUTION
        # ================================================
        
        risk_pct = get_risk_pct(best_signal["adjusted_confidence"])
        position_size = calculate_position_size(balance, risk_pct, entry, sl)
        
        if not check_portfolio_limits(position_size, risk_pct):
            continue
        
        trade = execute_trade(
            instrument=instrument,
            direction=get_direction(best_signal),
            entry=entry,
            sl=sl,
            tp=tp,
            size=position_size,
            metadata={
                "signal_type": best_signal["type"],
                "confidence": best_signal["adjusted_confidence"],
                "htf_trend": htf_trend,
                "timeframe": "H4"
            }
        )
        
        log_trade(trade)
        return trade
    
    return WAIT("No actionable price action signal")
```

### 13.2 Trade Management

```python
def manage_pa_trade(trade):
    """Active management of price action trades."""
    
    current_price = get_price(trade.instrument)
    candles = fetch_candles(trade.instrument, trade.timeframe, count=50)
    
    # Check for opposing signal at current price
    detector = PriceActionDetector(candles)
    signals = detector.detect_all_signals()
    opposing = [s for s in signals if opposes_trade(s, trade)]
    
    if opposing and opposing[0]["adjusted_confidence"] >= 0.65:
        # Strong opposing signal — consider early exit
        if trade.current_pnl > 0:
            close_trade(trade, reason="Strong opposing signal in profit")
            return
    
    # Trailing stop based on new swing points
    if trade.pnl_in_r >= 1.0:  # At least 1R in profit
        trail_behind_structure(trade, candles)
    
    # Time-based management (for breakout trades)
    if trade.metadata["signal_type"] in BREAKOUT_PATTERNS:
        if trade.age_candles > 10 and trade.pnl_in_r < 0.5:
            close_trade(trade, reason="Breakout failed to follow through")
```

---

## 14. AI Implementation Notes

### 14.1 Strengths of AI in Price Action

1. **Consistency**: AI never gets fatigued or emotional; every candle is scanned systematically.
2. **Multi-instrument coverage**: Can scan 50+ instruments simultaneously.
3. **Pattern objectivity**: No subjective "eye-balling" — everything is mathematically defined.
4. **Statistical tracking**: Real-time win rate monitoring per pattern type.

### 14.2 Challenges and Mitigations

| Challenge | Mitigation |
|-----------|-----------|
| Context is nuanced | Use multi-factor confidence scoring with HTF trend, location, and momentum |
| Patterns are not binary | Use gradient confidence scores (0–1) rather than binary yes/no |
| False signals are common | Require minimum confluence (2+ factors) for entry |
| Timeframe selection matters | Default to H4 for trade signals, D1 for context |

### 14.3 Data Requirements

| Timeframe | History Needed | Frequency |
|-----------|---------------|-----------|
| Monthly | 5+ years | Monthly |
| Weekly | 2 years | Weekly |
| Daily | 1 year | Daily |
| H4 | 6 months | 4-hourly |
| H1 | 3 months | Hourly |
| M15 | 2 weeks | Every 15 min |

---

## 15. References

### Books
1. Brooks, A. (2009). *Reading Price Charts Bar by Bar*. Wiley.
2. Brooks, A. (2012). *Trading Price Action Trends*. Wiley.
3. Brooks, A. (2012). *Trading Price Action Trading Ranges*. Wiley.
4. Brooks, A. (2012). *Trading Price Action Reversals*. Wiley.
5. Nison, S. (2001). *Japanese Candlestick Charting Techniques*, 2nd ed. Prentice Hall.
6. Bulkowski, T. N. (2005). *Encyclopedia of Chart Patterns*, 2nd ed. Wiley.
7. Bulkowski, T. N. (2008). *Encyclopedia of Candlestick Charts*. Wiley.
8. Murphy, J. J. (1999). *Technical Analysis of the Financial Markets*. NYIF.
9. Edwards, R. D., & Magee, J. (2007). *Technical Analysis of Stock Trends*, 9th ed. CRC Press.
10. Pring, M. J. (2002). *Technical Analysis Explained*, 4th ed. McGraw-Hill.

### Academic Papers
11. Lo, A. W., Mamaysky, H., & Wang, J. (2000). "Foundations of Technical Analysis." *The Journal of Finance*, 55(4), 1705–1765.
12. Park, C.-H., & Irwin, S. H. (2007). "What Do We Know About the Profitability of Technical Analysis?" *Journal of Economic Surveys*, 21(4), 786–826.
13. Caginalp, G., & Laurent, H. (1998). "The Predictive Power of Price Patterns." *Applied Mathematical Finance*, 5, 181–206.
14. Leigh, W., Modani, N., Purvis, R., & Roberts, T. (2002). "Stock Market Trading Rule Discovery Using Technical Charting Heuristics." *Expert Systems with Applications*, 23(2), 155–159.

### Practitioner Sources
15. Nial Fuller. "Price Action Trading Strategies" — LearnToTradeTheMarket.com.
16. Chris Capre. "Advanced Price Action Course" — 2ndSkiesForex.com.
17. TradingView. Pattern recognition community indicators.

---

*This document is part of the Multi-Agent AI Trading System knowledge base. It should be read in conjunction with the Supply & Demand guide (05_supply_demand_zones), Smart Money Concepts guide (04_smart_money_concepts), and the Multi-Timeframe Analysis guide (11_multi_timeframe_analysis).*
