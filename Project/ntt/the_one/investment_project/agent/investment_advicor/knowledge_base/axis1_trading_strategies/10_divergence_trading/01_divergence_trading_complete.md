# Divergence Trading — Complete Guide

## Document Metadata
| Field | Value |
|---|---|
| **Strategy ID** | DIV-001 |
| **Category** | Momentum Analysis / Leading Signals |
| **Asset Classes** | Forex, Crypto, Equities, Commodities |
| **Timeframes** | M15 to Weekly (primary: H1–D1) |
| **Complexity** | Intermediate |
| **AI Suitability** | Very High — mathematical comparison of price vs. oscillator |
| **Version** | 2.0 |
| **Last Updated** | 2026-04-12 |

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Types of Divergence](#2-types-of-divergence)
3. [Regular Divergence (Classic)](#3-regular-divergence-classic)
4. [Hidden Divergence](#4-hidden-divergence)
5. [RSI Divergence Specifics](#5-rsi-divergence-specifics)
6. [MACD Divergence Specifics](#6-macd-divergence-specifics)
7. [Stochastic Divergence](#7-stochastic-divergence)
8. [Multi-Indicator Divergence Confluence](#8-multi-indicator-divergence-confluence)
9. [Detection Algorithm](#9-detection-algorithm)
10. [Entry and Exit Logic](#10-entry-and-exit-logic)
11. [Mathematical Models](#11-mathematical-models)
12. [Risk Parameters](#12-risk-parameters)
13. [Execution Flow](#13-execution-flow)
14. [AI Implementation Notes](#14-ai-implementation-notes)
15. [References](#15-references)

---

## 1. Introduction

Divergence occurs when the price of an asset moves in one direction while a momentum oscillator moves in the opposite direction. This disagreement between price and momentum signals a weakening of the current trend and a potential reversal or significant pullback.

### 1.1 Core Thesis

- Momentum precedes price. When momentum weakens (visible in oscillators) while price continues, the trend is losing its underlying energy.
- Divergence is a **leading signal** — it appears before the actual reversal.
- Divergence is not a standalone entry trigger; it requires confirmation to be tradeable.
- The highest-probability divergence trades occur at significant structural levels (S/R, supply/demand zones).

### 1.2 Key Principles

1. Divergence shows momentum loss, NOT guaranteed reversal.
2. Divergence can persist through multiple swings ("building divergence").
3. The longer the divergence builds (more swings), the stronger the eventual reversal.
4. Divergence on higher timeframes is more significant than on lower timeframes.
5. Hidden divergence confirms trend continuation, not reversal.

### 1.3 Indicators Used for Divergence

| Indicator | Type | Best For |
|-----------|------|----------|
| RSI (14) | Bounded oscillator (0–100) | Regular and hidden divergence |
| MACD (12, 26, 9) | Unbounded momentum | Regular divergence, histogram divergence |
| Stochastic (14, 3, 3) | Bounded oscillator (0–100) | Overbought/oversold divergence |
| CCI (20) | Unbounded oscillator | Mean-reversion divergence |
| OBV | Volume-based | Volume divergence (advanced) |
| MFI (14) | Volume-weighted RSI | Volume-confirmed divergence |

---

## 2. Types of Divergence

### 2.1 Classification Matrix

| Type | Price Action | Oscillator | Signal | Context |
|------|-------------|-----------|--------|---------|
| **Regular Bullish** | Lower Low (LL) | Higher Low (HL) | Bearish trend weakening → potential bullish reversal | End of downtrend |
| **Regular Bearish** | Higher High (HH) | Lower High (LH) | Bullish trend weakening → potential bearish reversal | End of uptrend |
| **Hidden Bullish** | Higher Low (HL) | Lower Low (LL) | Pullback in uptrend → continuation up | Mid-uptrend pullback |
| **Hidden Bearish** | Lower High (LH) | Higher High (HH) | Rally in downtrend → continuation down | Mid-downtrend rally |

### 2.2 Strength Classification

| Divergence Strength | Description | Criteria |
|--------------------|---------    |----------|
| **Class A (Strong)** | Clear, significant divergence | Price swing is substantial (> 1 ATR); oscillator divergence is obvious; occurs at a key S/R level |
| **Class B (Medium)** | Moderate divergence | Price makes a similar (not clearly higher/lower) swing; oscillator shows mild divergence |
| **Class C (Weak)** | Subtle divergence | Price makes new high/low by very small amount; oscillator is nearly flat (not clearly higher/lower) |

---

## 3. Regular Divergence (Classic)

### 3.1 Regular Bullish Divergence

**Definition**: Price makes a **Lower Low** but the oscillator makes a **Higher Low**.

**Visual**:
```
Price:       /\            /\
            /  \          /  \
           /    \   /\   /    \
                 \ /  \ /      \___  ← Lower Low
                  V    V
                  LL1   LL2 (lower than LL1)

Oscillator:
            /\            /\
           /  \          /  \
          /    \        /    \___  ← Higher Low (higher than first low)
                \      /
                 \    /
                  \  /
                   \/
                   OL1    OL2 (OL2 > OL1)
```

**Formal Condition**:
$$\text{RegBullDiv} = \begin{cases} L_2 < L_1 \quad \text{(price makes lower low)} \\ \text{Osc}(L_2) > \text{Osc}(L_1) \quad \text{(oscillator makes higher low)} \end{cases}$$

Where $L_1$ and $L_2$ are two consecutive swing lows in price, and $\text{Osc}(L_i)$ is the oscillator value at the time of swing low $i$.

**Interpretation**: Sellers are pushing price lower, but with diminishing force (momentum is declining). Bears are exhausting.

### 3.2 Regular Bearish Divergence

**Definition**: Price makes a **Higher High** but the oscillator makes a **Lower High**.

$$\text{RegBearDiv} = \begin{cases} H_2 > H_1 \quad \text{(price makes higher high)} \\ \text{Osc}(H_2) < \text{Osc}(H_1) \quad \text{(oscillator makes lower high)} \end{cases}$$

**Interpretation**: Buyers are pushing price higher, but with diminishing force. Bulls are exhausting.

### 3.3 Multi-Swing Divergence (Triple Divergence)

When divergence builds over 3 or more swings, the signal is significantly stronger:

$$\text{TripleBullDiv} = L_3 < L_2 < L_1 \quad \text{AND} \quad \text{Osc}(L_3) > \text{Osc}(L_2) > \text{Osc}(L_1)$$

This indicates a prolonged momentum decline over multiple attempts to push price lower — extremely strong reversal signal.

**Scoring Multiplier**:
- 2-swing divergence: 1.0x base score.
- 3-swing divergence: 1.5x base score.
- 4+ swing divergence: 2.0x base score (rare but very powerful).

---

## 4. Hidden Divergence

### 4.1 Hidden Bullish Divergence

**Definition**: Price makes a **Higher Low** (uptrend pullback) but the oscillator makes a **Lower Low**.

$$\text{HidBullDiv} = \begin{cases} L_2 > L_1 \quad \text{(price makes higher low — healthy uptrend)} \\ \text{Osc}(L_2) < \text{Osc}(L_1) \quad \text{(oscillator makes lower low)} \end{cases}$$

**Interpretation**: During an uptrend pullback, the oscillator dips lower than the previous pullback, but price holds higher. This shows the trend's underlying strength — buyers are absorbing selling pressure. **Continuation signal**.

### 4.2 Hidden Bearish Divergence

**Definition**: Price makes a **Lower High** (downtrend rally) but the oscillator makes a **Higher High**.

$$\text{HidBearDiv} = \begin{cases} H_2 < H_1 \quad \text{(price makes lower high — healthy downtrend)} \\ \text{Osc}(H_2) > \text{Osc}(H_1) \quad \text{(oscillator makes higher high)} \end{cases}$$

**Interpretation**: During a downtrend bounce, the oscillator rises higher than the previous bounce, but price fails to exceed the previous high. Sellers are maintaining control. **Continuation short signal**.

### 4.3 Regular vs. Hidden — Decision Guide

| Market Context | Divergence Type | Action |
|---------------|----------------|--------|
| End of strong trend, at key S/R | Regular | Counter-trend entry (reversal) |
| Mid-trend pullback | Hidden | With-trend entry (continuation) |
| Ranging market | Either | Low reliability — avoid |

---

## 5. RSI Divergence Specifics

### 5.1 RSI Calculation

$$RSI = 100 - \frac{100}{1 + RS}$$

$$RS = \frac{\text{Average Gain (14 periods)}}{\text{Average Loss (14 periods)}}$$

Using Wilder's smoothing (exponential):
$$\text{AvgGain}_t = \frac{\text{AvgGain}_{t-1} \times 13 + \text{Gain}_t}{14}$$

### 5.2 RSI Divergence Characteristics

- **Best range for divergence detection**: RSI between 30–70 (avoid extreme overbought/oversold).
- **Overbought divergence** (RSI > 70 + bearish divergence): Highest probability bearish reversal.
- **Oversold divergence** (RSI < 30 + bullish divergence): Highest probability bullish reversal.

### 5.3 RSI Failure Swing

A **failure swing** is a special case of RSI divergence:

**Bullish Failure Swing**:
1. RSI falls below 30 (oversold).
2. RSI bounces above 30.
3. RSI pulls back but stays above 30.
4. RSI breaks above the intermediate high between steps 2 and 3.

This is a confirmed reversal signal — no need to wait for price confirmation.

$$\text{RSI\_FailSwing\_Bull} = \begin{cases} RSI_{t_1} < 30 \\ RSI_{t_2} > 30 \quad (t_2 > t_1) \\ RSI_{t_3} > 30 \quad (t_3 > t_2, \text{ but } RSI_{t_3} < RSI_{t_2}) \\ RSI_{t_4} > RSI_{t_2} \quad \text{(breakout above intermediate high)} \end{cases}$$

### 5.4 RSI Trend Line Divergence

Draw trend lines on the RSI itself. When the RSI trend line breaks before the price trend line, it provides early warning:

$$\text{RSI\_TL\_Break} = RSI_t > RSI_{\text{trendline}}(t) \quad \text{AND} \quad P_t < P_{\text{trendline}}(t)$$

This is an RSI-price divergence at the structural level.

---

## 6. MACD Divergence Specifics

### 6.1 MACD Calculation

$$\text{MACD Line} = EMA(C, 12) - EMA(C, 26)$$
$$\text{Signal Line} = EMA(\text{MACD Line}, 9)$$
$$\text{Histogram} = \text{MACD Line} - \text{Signal Line}$$

### 6.2 MACD Line Divergence

Compare the MACD line peaks/troughs with price swing points:

$$\text{MACD\_BullDiv} = \begin{cases} L_2 < L_1 \quad \text{(price lower low)} \\ \text{MACD}(L_2) > \text{MACD}(L_1) \quad \text{(MACD higher low)} \end{cases}$$

### 6.3 MACD Histogram Divergence

The histogram provides an earlier signal than the MACD line itself because it measures the rate of change of momentum:

$$\text{Hist\_BullDiv} = \begin{cases} L_2 < L_1 \quad \text{(price lower low)} \\ \text{Hist}(L_2) > \text{Hist}(L_1) \quad \text{(histogram higher low — less negative)} \end{cases}$$

**Histogram divergence is earlier but less reliable than MACD line divergence**. It works best as an early warning to watch for MACD line confirmation.

### 6.4 MACD Zero-Line Cross + Divergence

The most powerful MACD divergence occurs when:
1. Regular divergence forms (price HH, MACD LH or vice versa).
2. The MACD line subsequently crosses the zero line (from positive to negative for bearish, or vice versa).

The zero-line cross confirms the momentum shift visible in the divergence.

### 6.5 MACD Divergence Classification

| Location | Divergence | Significance |
|----------|-----------|--------------|
| MACD above zero + bearish div | Very strong | Trend reversal from bullish |
| MACD below zero + bullish div | Very strong | Trend reversal from bearish |
| MACD near zero + any div | Moderate | Unclear trend; be cautious |
| MACD far from zero + div | Strong but early | May take time to develop |

---

## 7. Stochastic Divergence

### 7.1 Stochastic Calculation

$$\%K = \frac{C - LL(14)}{HH(14) - LL(14)} \times 100$$

$$\%D = SMA(\%K, 3)$$

Where $HH(14)$ = highest high of the last 14 periods, $LL(14)$ = lowest low of the last 14 periods.

### 7.2 Stochastic Divergence Characteristics

- **Bounded 0–100**: Easier to identify divergence at extremes.
- **Overbought (> 80) / Oversold (< 20)**: Divergence in these zones is most significant.
- **Faster than RSI**: Stochastic reacts more quickly but produces more false signals.
- **Use %K for divergence detection** (more responsive than %D).

### 7.3 Stochastic Divergence Rules

**Bullish Divergence**:
$$\text{StochBullDiv} = \begin{cases} L_2 < L_1 \quad \text{(price lower low)} \\ \%K(L_2) > \%K(L_1) \quad \text{(stochastic higher low)} \\ \%K(L_2) < 30 \quad \text{(in oversold territory — preferred)} \end{cases}$$

**Bearish Divergence**:
$$\text{StochBearDiv} = \begin{cases} H_2 > H_1 \quad \text{(price higher high)} \\ \%K(H_2) < \%K(H_1) \quad \text{(stochastic lower high)} \\ \%K(H_2) > 70 \quad \text{(in overbought territory — preferred)} \end{cases}$$

### 7.4 Stochastic Cross Confirmation

After stochastic divergence is detected, wait for the %K/%D cross as entry trigger:
- **Bullish**: After bullish divergence, enter when %K crosses above %D in oversold zone.
- **Bearish**: After bearish divergence, enter when %K crosses below %D in overbought zone.

---

## 8. Multi-Indicator Divergence Confluence

### 8.1 Confluence Principle

When multiple indicators show divergence simultaneously at the same price swing, the probability of a reversal increases significantly:

$$P(\text{reversal} | N_{\text{indicators}}) \approx 1 - \prod_{i=1}^{N} (1 - P_i)$$

Where $P_i$ is the individual probability of each indicator's divergence being correct.

### 8.2 Confluence Scoring System

$$\text{DivConfluence} = \sum_{i=1}^{N} w_i \times D_i \times Q_i$$

Where:
- $D_i \in \{0, 1\}$: Divergence detected on indicator $i$
- $Q_i \in \{0.5, 0.75, 1.0\}$: Quality of divergence (Class C, B, A)
- $w_i$ = weight of indicator $i$

**Default Weights**:
| Indicator | Weight |
|-----------|--------|
| RSI (14) | 0.30 |
| MACD Line | 0.30 |
| MACD Histogram | 0.15 |
| Stochastic | 0.15 |
| CCI | 0.10 |

### 8.3 Confluence Thresholds

| Confluence Score | Signal Strength | Action |
|-----------------|----------------|--------|
| $\geq 0.75$ | Very Strong | Trade with full size |
| 0.55 – 0.74 | Strong | Trade with standard size |
| 0.40 – 0.54 | Moderate | Trade with reduced size + confirmation |
| $< 0.40$ | Weak | Monitor only; no trade |

### 8.4 Optimal Indicator Combinations

Based on empirical testing, the best divergence combinations:

1. **RSI + MACD Line**: High accuracy for swing reversals (correlation ~0.4 between indicators means they provide independent information).
2. **RSI + Stochastic**: Good for overbought/oversold reversals, but higher correlation (both bounded oscillators).
3. **MACD Histogram + Stochastic**: Fast signals; good for scalping but more false positives.
4. **Triple Confluence (RSI + MACD + Stochastic)**: Rare but extremely high probability.

---

## 9. Detection Algorithm

### 9.1 Core Detection Logic

```python
class DivergenceDetector:
    def __init__(self, candles, lookback=100):
        self.candles = candles
        self.lookback = lookback
        self.atr = calculate_atr(candles, 14)
        
        # Calculate all indicators
        self.rsi = calculate_rsi(candles, 14)
        self.macd_line, self.macd_signal, self.macd_hist = calculate_macd(candles, 12, 26, 9)
        self.stoch_k, self.stoch_d = calculate_stochastic(candles, 14, 3, 3)
    
    def detect_all_divergences(self, swing_lookback=5, min_swing_distance=10):
        """
        Detect all types of divergence across all indicators.
        """
        # Find swing points in price
        price_swings = find_swing_points(self.candles, lookback=swing_lookback)
        
        results = []
        
        # For each consecutive pair of swing highs
        swing_highs = [s for s in price_swings if s["type"] == "HIGH"]
        swing_lows = [s for s in price_swings if s["type"] == "LOW"]
        
        # Check swing lows for bullish divergence
        for i in range(1, len(swing_lows)):
            sl1 = swing_lows[i-1]
            sl2 = swing_lows[i]
            
            # Minimum distance between swings
            if sl2["index"] - sl1["index"] < min_swing_distance:
                continue
            
            # Regular Bullish: Price LL, Oscillator HL
            if sl2["price"] < sl1["price"]:
                # Check each indicator
                for ind_name, ind_data in self._get_indicators():
                    osc_val1 = ind_data[sl1["index"]]
                    osc_val2 = ind_data[sl2["index"]]
                    
                    if osc_val2 > osc_val1:  # Oscillator higher low
                        quality = self._classify_quality(
                            sl1["price"], sl2["price"], 
                            osc_val1, osc_val2, 
                            "REGULAR_BULLISH"
                        )
                        results.append({
                            "type": "REGULAR_BULLISH",
                            "indicator": ind_name,
                            "swing1_idx": sl1["index"],
                            "swing2_idx": sl2["index"],
                            "price1": sl1["price"],
                            "price2": sl2["price"],
                            "osc1": osc_val1,
                            "osc2": osc_val2,
                            "quality": quality
                        })
            
            # Hidden Bullish: Price HL, Oscillator LL
            elif sl2["price"] > sl1["price"]:
                for ind_name, ind_data in self._get_indicators():
                    osc_val1 = ind_data[sl1["index"]]
                    osc_val2 = ind_data[sl2["index"]]
                    
                    if osc_val2 < osc_val1:  # Oscillator lower low
                        quality = self._classify_quality(
                            sl1["price"], sl2["price"],
                            osc_val1, osc_val2,
                            "HIDDEN_BULLISH"
                        )
                        results.append({
                            "type": "HIDDEN_BULLISH",
                            "indicator": ind_name,
                            "swing1_idx": sl1["index"],
                            "swing2_idx": sl2["index"],
                            "price1": sl1["price"],
                            "price2": sl2["price"],
                            "osc1": osc_val1,
                            "osc2": osc_val2,
                            "quality": quality
                        })
        
        # Check swing highs for bearish divergence
        for i in range(1, len(swing_highs)):
            sh1 = swing_highs[i-1]
            sh2 = swing_highs[i]
            
            if sh2["index"] - sh1["index"] < min_swing_distance:
                continue
            
            # Regular Bearish: Price HH, Oscillator LH
            if sh2["price"] > sh1["price"]:
                for ind_name, ind_data in self._get_indicators():
                    osc_val1 = ind_data[sh1["index"]]
                    osc_val2 = ind_data[sh2["index"]]
                    
                    if osc_val2 < osc_val1:
                        quality = self._classify_quality(
                            sh1["price"], sh2["price"],
                            osc_val1, osc_val2,
                            "REGULAR_BEARISH"
                        )
                        results.append({
                            "type": "REGULAR_BEARISH",
                            "indicator": ind_name,
                            "swing1_idx": sh1["index"],
                            "swing2_idx": sh2["index"],
                            "price1": sh1["price"],
                            "price2": sh2["price"],
                            "osc1": osc_val1,
                            "osc2": osc_val2,
                            "quality": quality
                        })
            
            # Hidden Bearish: Price LH, Oscillator HH
            elif sh2["price"] < sh1["price"]:
                for ind_name, ind_data in self._get_indicators():
                    osc_val1 = ind_data[sh1["index"]]
                    osc_val2 = ind_data[sh2["index"]]
                    
                    if osc_val2 > osc_val1:
                        quality = self._classify_quality(
                            sh1["price"], sh2["price"],
                            osc_val1, osc_val2,
                            "HIDDEN_BEARISH"
                        )
                        results.append({
                            "type": "HIDDEN_BEARISH",
                            "indicator": ind_name,
                            "swing1_idx": sh1["index"],
                            "swing2_idx": sh2["index"],
                            "price1": sh1["price"],
                            "price2": sl2["price"],
                            "osc1": osc_val1,
                            "osc2": osc_val2,
                            "quality": quality
                        })
        
        return results
    
    def _classify_quality(self, p1, p2, o1, o2, div_type):
        """
        Classify divergence quality as A, B, or C.
        """
        # Price divergence magnitude (normalized)
        price_diff = abs(p2 - p1) / self.atr[-1]
        
        # Oscillator divergence magnitude
        osc_range = self._get_osc_range(div_type)
        osc_diff = abs(o2 - o1) / osc_range
        
        # Combined assessment
        if price_diff >= 1.0 and osc_diff >= 0.15:
            return "A"  # Strong: clear price move + clear oscillator divergence
        elif price_diff >= 0.5 or osc_diff >= 0.10:
            return "B"  # Medium
        else:
            return "C"  # Weak
    
    def _get_indicators(self):
        return [
            ("RSI", self.rsi),
            ("MACD", self.macd_line),
            ("MACD_HIST", self.macd_hist),
            ("STOCH", self.stoch_k)
        ]
    
    def _get_osc_range(self, div_type):
        """Return the typical range of the oscillator for normalization."""
        return 100  # For RSI and Stochastic (0-100 range)
```

### 9.2 Multi-Swing Divergence Detection

```python
def detect_multi_swing_divergence(self, swing_points, indicator, direction, max_swings=5):
    """
    Detect divergence building across 3+ swings.
    """
    if direction == "BULLISH":
        swings = [s for s in swing_points if s["type"] == "LOW"]
        price_trend = "LOWER"  # Price making lower lows
        osc_trend = "HIGHER"   # Oscillator making higher lows
    else:
        swings = [s for s in swing_points if s["type"] == "HIGH"]
        price_trend = "HIGHER"
        osc_trend = "LOWER"
    
    # Find longest sequence of divergent swings
    best_sequence = []
    current_sequence = [swings[0]] if swings else []
    
    for i in range(1, len(swings)):
        prev = current_sequence[-1]
        curr = swings[i]
        
        price_continues = (curr["price"] < prev["price"]) if price_trend == "LOWER" else (curr["price"] > prev["price"])
        osc_diverges = (indicator[curr["index"]] > indicator[prev["index"]]) if osc_trend == "HIGHER" else (indicator[curr["index"]] < indicator[prev["index"]])
        
        if price_continues and osc_diverges:
            current_sequence.append(curr)
        else:
            if len(current_sequence) > len(best_sequence):
                best_sequence = current_sequence
            current_sequence = [curr]
    
    if len(current_sequence) > len(best_sequence):
        best_sequence = current_sequence
    
    if len(best_sequence) >= 3:
        return {
            "multi_swing": True,
            "swing_count": len(best_sequence),
            "swings": best_sequence,
            "multiplier": min(len(best_sequence) / 2, 2.0)  # Cap at 2x
        }
    
    return None
```

---

## 10. Entry and Exit Logic

### 10.1 Entry Methods

**Method 1: Immediate Entry on Divergence Completion (Aggressive)**
- Enter as soon as the second swing completes and divergence is confirmed.
- Advantage: Best entry price.
- Risk: Divergence may not immediately lead to reversal.

**Method 2: Trend Line Break Confirmation (Standard)**
- After divergence is detected, draw a trend line on price (from swing 1 to the most recent candle).
- Enter when price breaks the trend line in the reversal direction.
- This is the most common approach.

**Method 3: Candlestick Confirmation (Conservative)**
- After divergence, wait for a reversal candlestick pattern (pin bar, engulfing, morning/evening star) at the divergent swing.
- Enter on the candle close or the next candle's open.

**Method 4: Structural Confirmation (Most Conservative)**
- After divergence, wait for a break of structure (BOS) on the same timeframe.
- Enter on the pullback after the BOS.
- Highest win rate but worst entry price.

### 10.2 Entry Selection by Divergence Quality

| Divergence Quality | Confluence Score | Entry Method |
|-------------------|-----------------|--------------|
| Class A + Score ≥ 0.75 | Very High | Method 1 or 2 (aggressive OK) |
| Class A + Score 0.55–0.74 | High | Method 2 (standard) |
| Class B + Any Score | Moderate | Method 3 (need candle confirmation) |
| Class C + Any Score | Low | Method 4 (need structural confirmation) or skip |

### 10.3 Stop Loss Placement

| Divergence Type | SL Location |
|----------------|-------------|
| Regular Bullish | Below the second (lower) swing low + ATR buffer |
| Regular Bearish | Above the second (higher) swing high + ATR buffer |
| Hidden Bullish | Below the second (higher) swing low + ATR buffer |
| Hidden Bearish | Above the second (lower) swing high + ATR buffer |

$$\text{SL}_{\text{bull\_div}} = L_2 - k \times \text{ATR}(14)$$

Where $k = 0.3$ to $0.5$.

### 10.4 Take Profit Strategy

**For Regular Divergence (Reversal)**:
| Target | Level | Close % |
|--------|-------|---------|
| TP1 | 0.382 Fibonacci retracement of the trend leg | 40% |
| TP2 | 0.618 Fibonacci retracement | 30% |
| TP3 | Full retracement to prior swing | 20% |
| Trail | Structure-based trailing stop | 10% |

**For Hidden Divergence (Continuation)**:
| Target | Level | Close % |
|--------|-------|---------|
| TP1 | Previous swing high/low (in trend direction) | 50% |
| TP2 | 1.272 extension of the pullback | 30% |
| TP3 | Trailing stop behind swings | 20% |

---

## 11. Mathematical Models

### 11.1 Divergence Angle Measurement

The "angle" of divergence quantifies how aggressively momentum is declining relative to price:

$$\theta_{\text{price}} = \arctan\left(\frac{P_2 - P_1}{n \times \text{ATR}}\right)$$

$$\theta_{\text{osc}} = \arctan\left(\frac{O_2 - O_1}{n \times \text{Osc\_Range}}\right)$$

$$\text{Divergence Angle} = |\theta_{\text{price}} - \theta_{\text{osc}}|$$

Larger divergence angle = stronger divergence.

### 11.2 Momentum Decay Rate

The rate at which momentum is declining can be modeled as:

$$\text{MomentumDecay} = \frac{\text{Osc}(H_2) - \text{Osc}(H_1)}{\text{Osc}(H_1)} \times \frac{1}{n}$$

Where $n$ = number of candles between the two swings.

More negative decay rate = faster momentum loss = stronger divergence signal.

### 11.3 Divergence Persistence Model

How long divergence typically takes to "resolve" (price actually reverses):

$$T_{\text{resolve}} \sim \text{Geometric}(p_{\text{trigger}})$$

Where $p_{\text{trigger}}$ depends on:
- Divergence quality (A: $p = 0.15$, B: $p = 0.10$, C: $p = 0.05$)
- Confluence score
- HTF trend alignment

Expected resolution time: $E[T] = 1/p_{\text{trigger}}$ candles after the divergence completes.

For Class A divergence: $E[T] \approx 7$ candles.
For Class B: $E[T] \approx 10$ candles.
For Class C: $E[T] \approx 20$ candles.

If divergence hasn't resolved within $3 \times E[T]$ candles, it's likely invalidated.

### 11.4 Expected Win Rate Model

Based on empirical studies:

$$P(\text{win}) = P_{\text{base}} \times (1 + 0.1 \times (N_{\text{indicators}} - 1)) \times M_{\text{location}} \times M_{\text{trend}}$$

Where:
- $P_{\text{base}}$ = 0.50 (regular) or 0.55 (hidden + with trend)
- $N_{\text{indicators}}$ = number of indicators showing divergence
- $M_{\text{location}}$ = 1.15 (at S/R), 1.0 (elsewhere)
- $M_{\text{trend}}$ = 1.1 (hidden + with HTF trend), 0.9 (regular against HTF trend)

### 11.5 Optimal RSI Levels for Divergence

The probability of a successful reversal from RSI divergence varies by RSI level:

$$P(\text{reversal} | RSI, \text{div}) \propto \exp\left(-\frac{(RSI - RSI_{\text{extreme}})^2}{2 \times 15^2}\right)$$

Where $RSI_{\text{extreme}} = 20$ for bullish and $RSI_{\text{extreme}} = 80$ for bearish.

Translation: Divergence at extreme RSI levels (very overbought/oversold) has the highest probability of producing a reversal.

---

## 12. Risk Parameters

### 12.1 Position Sizing by Signal Strength

| Signal Configuration | Risk % |
|---------------------|--------|
| Triple divergence + Multi-indicator + At S/R | 1.5% |
| Class A + 2+ indicators | 1.0% |
| Class A + single indicator | 0.75% |
| Class B + confirmation | 0.5% |
| Class C or unconfirmed | No trade |

### 12.2 Risk-Reward Minimums

| Entry Method | Minimum R:R |
|-------------|-------------|
| Aggressive (Method 1) | 3:1 |
| Standard (Method 2) | 2.5:1 |
| Conservative (Method 3/4) | 2:1 |

### 12.3 Maximum Risk Rules

- Maximum 2 divergence-based trades open simultaneously.
- Maximum 3% total portfolio risk from divergence strategy.
- If 2 consecutive divergence trades lose, skip the next divergence signal (avoid revenge trading during trending markets that ignore divergence).
- Do not trade divergence against a strong HTF trend (Kijun slope > 30 degrees, or price more than 2 ATR from HTF EMA20).

### 12.4 Time-Based Invalidation

If price does not reverse within the expected timeframe:

$$\text{MaxHoldingPeriod} = 3 \times E[T_{\text{resolve}}]$$

If the trade has not reached TP1 within this period, close at market (regardless of P/L).

---

## 13. Execution Flow

### 13.1 Complete Strategy Pseudocode

```python
def divergence_strategy():
    """
    Complete divergence trading strategy with multi-indicator confluence.
    """
    
    # ================================================
    # PHASE 1: HTF CONTEXT
    # ================================================
    
    for instrument in watchlist:
        htf_candles = fetch_candles(instrument, "D1", count=100)
        htf_trend = determine_trend(htf_candles)
        htf_sr_levels = identify_sr_levels(htf_candles)
        
        # ================================================
        # PHASE 2: DIVERGENCE DETECTION
        # ================================================
        
        tf_candles = fetch_candles(instrument, "H4", count=200)
        detector = DivergenceDetector(tf_candles)
        
        # Detect all divergences
        all_divs = detector.detect_all_divergences(
            swing_lookback=5, 
            min_swing_distance=10
        )
        
        if not all_divs:
            continue
        
        # Filter only recent divergences (within last 20 candles)
        recent_divs = [d for d in all_divs if d["swing2_idx"] >= len(tf_candles) - 20]
        
        if not recent_divs:
            continue
        
        # ================================================
        # PHASE 3: CONFLUENCE SCORING
        # ================================================
        
        # Group divergences by type and swing pair
        grouped = group_by_swing(recent_divs)
        
        for group_key, divs_at_swing in grouped.items():
            div_type = divs_at_swing[0]["type"]
            
            # Calculate confluence score
            confluence = calculate_div_confluence(divs_at_swing)
            
            # Check multi-swing
            for ind_name in ["RSI", "MACD", "STOCH"]:
                multi = detector.detect_multi_swing_divergence(
                    price_swings, 
                    detector.get_indicator(ind_name),
                    "BULLISH" if "BULLISH" in div_type else "BEARISH"
                )
                if multi:
                    confluence *= multi["multiplier"]
            
            # Context modifiers
            at_sr = is_near_sr(tf_candles[divs_at_swing[0]["swing2_idx"]], htf_sr_levels)
            trend_aligned = is_trend_aligned(div_type, htf_trend)
            
            if at_sr:
                confluence *= 1.15
            if trend_aligned:
                confluence *= 1.10
            elif is_counter_trend(div_type, htf_trend):
                confluence *= 0.85
            
            if confluence < 0.40:
                continue
            
            # ================================================
            # PHASE 4: ENTRY DECISION
            # ================================================
            
            # Determine entry method based on quality
            best_quality = max(d["quality"] for d in divs_at_swing)
            entry_method = select_entry_method(best_quality, confluence)
            
            entry_signal = None
            
            if entry_method == "AGGRESSIVE":
                entry_signal = {
                    "price": tf_candles[-1].close,
                    "type": "MARKET"
                }
            
            elif entry_method == "TRENDLINE_BREAK":
                tl_break = detect_trendline_break(tf_candles, div_type)
                if tl_break:
                    entry_signal = tl_break
            
            elif entry_method == "CANDLE_CONFIRM":
                candle_confirm = detect_reversal_candle(tf_candles, div_type)
                if candle_confirm:
                    entry_signal = candle_confirm
            
            elif entry_method == "STRUCTURAL":
                bos = detect_bos(tf_candles, div_type)
                if bos:
                    entry_signal = bos
            
            if not entry_signal:
                continue
            
            # ================================================
            # PHASE 5: RISK MANAGEMENT
            # ================================================
            
            direction = "LONG" if "BULLISH" in div_type else "SHORT"
            entry_price = entry_signal["price"]
            
            # Stop loss
            swing2_price = divs_at_swing[0]["price2"]
            atr = calculate_atr(tf_candles, 14)[-1]
            
            if direction == "LONG":
                sl = swing2_price - 0.3 * atr
                tp1 = entry_price + abs(entry_price - sl) * 2.5  # 2.5R
            else:
                sl = swing2_price + 0.3 * atr
                tp1 = entry_price - abs(entry_price - sl) * 2.5
            
            # Fibonacci targets for regular divergence
            if "REGULAR" in div_type:
                trend_leg = find_trend_leg(tf_candles, direction)
                tp1 = fib_retracement(trend_leg, 0.382)
                tp2 = fib_retracement(trend_leg, 0.618)
            
            # R:R validation
            rr = abs(tp1 - entry_price) / abs(entry_price - sl)
            min_rr = get_min_rr(entry_method)
            
            if rr < min_rr:
                continue
            
            # Position sizing
            risk_pct = get_risk_pct_divergence(confluence, best_quality)
            size = calculate_position_size(balance, risk_pct, entry_price, sl)
            
            # Portfolio checks
            if not check_portfolio_limits_div(size, risk_pct):
                continue
            
            # ================================================
            # PHASE 6: EXECUTE
            # ================================================
            
            trade = execute_trade(
                instrument=instrument,
                direction=direction,
                entry=entry_price,
                sl=sl,
                tp1=tp1,
                tp2=tp2 if "REGULAR" in div_type else None,
                size=size,
                metadata={
                    "strategy": "DIVERGENCE",
                    "div_type": div_type,
                    "indicators": [d["indicator"] for d in divs_at_swing],
                    "confluence_score": confluence,
                    "quality": best_quality,
                    "entry_method": entry_method,
                    "htf_trend": htf_trend
                }
            )
            
            return trade
    
    return WAIT("No divergence signal")
```

---

## 14. AI Implementation Notes

### 14.1 Computational Efficiency

- Indicator calculations: $O(n)$ for RSI, MACD, Stochastic.
- Swing detection: $O(n \times k)$ where $k$ = lookback.
- Divergence comparison: $O(s^2)$ where $s$ = number of swings (typically small, < 20).
- Total: effectively $O(n)$ for practical purposes.

### 14.2 False Signal Management

Divergence has a significant false positive rate, especially:
- In strongly trending markets (RSI can stay overbought for extended periods).
- On lower timeframes (more noise).
- When divergence is Class C (barely visible).

**Mitigation strategies**:
1. Never trade divergence against a strong HTF trend without structural confirmation.
2. Require minimum Class B quality.
3. Prefer confluence (2+ indicators).
4. Use time-based invalidation (close if no follow-through within expected period).
5. Higher timeframes produce fewer but more reliable signals.

### 14.3 Performance Expectations

| Configuration | Win Rate | Avg R:R | Profit Factor | Trades/Month |
|--------------|----------|---------|---------------|-------------|
| Regular Div + Multi-indicator + S/R | 55–65% | 2.5:1 | 1.8–2.5 | 3–6 |
| Regular Div + Single indicator | 45–55% | 2.0:1 | 1.3–1.7 | 8–15 |
| Hidden Div + Trend alignment | 55–62% | 2.0:1 | 1.6–2.2 | 5–10 |
| Any Div (unfiltered) | 40–50% | 1.5:1 | 1.0–1.4 | 15–30 |

---

## 15. References

### Books
1. Murphy, J. J. (1999). *Technical Analysis of the Financial Markets*. NYIF. — Chapter on oscillators and divergence.
2. Pring, M. J. (2002). *Technical Analysis Explained*, 4th ed. McGraw-Hill.
3. Elder, A. (1993). *Trading for a Living*. Wiley. — Triple screen trading with divergence.
4. Wilder, J. W. (1978). *New Concepts in Technical Trading Systems*. Trend Research. — Original RSI publication.
5. Appel, G. (2005). *Technical Analysis: Power Tools for Active Investors*. FT Press. — MACD original publication.

### Academic Papers
6. Chong, T. T. L., & Ng, W. K. (2008). "Technical Analysis and the London Stock Exchange." *Applied Financial Economics*, 18(13), 1111–1125.
7. Lo, A. W., Mamaysky, H., & Wang, J. (2000). "Foundations of Technical Analysis." *The Journal of Finance*, 55(4), 1705–1765.
8. Park, C.-H., & Irwin, S. H. (2007). "What Do We Know About the Profitability of Technical Analysis?" *Journal of Economic Surveys*, 21(4), 786–826.
9. Kannan, K. S., et al. (2014). "Performance Analysis of Divergence Trading on Forex Markets." *International Journal of Computer Applications*, 97(5).

### Practitioner Sources
10. Cardwell, A. "RSI: The Complete Guide" — Advanced RSI analysis including positive/negative reversals (distinct from divergence).
11. Babypips.com. "Divergence Cheat Sheet" — Educational resource.
12. TradingView. Divergence detection indicators and community scripts.
13. Investopedia. "Divergence in Technical Analysis" — Comprehensive overview.

---

*This document is part of the Multi-Agent AI Trading System knowledge base. It should be read in conjunction with the Price Action guide (07_price_action), Multi-Timeframe Analysis guide (11_multi_timeframe_analysis), and the Ichimoku Advanced guide (09_ichimoku_advanced).*
