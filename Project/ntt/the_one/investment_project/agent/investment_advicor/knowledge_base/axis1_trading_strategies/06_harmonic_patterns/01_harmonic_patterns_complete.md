# Harmonic Pattern Trading — Complete Guide

## Document Metadata
| Field | Value |
|---|---|
| **Strategy ID** | HRM-001 |
| **Category** | Fibonacci-Based Pattern Recognition |
| **Asset Classes** | Forex, Crypto, Equities, Commodities |
| **Timeframes** | M15 to Monthly (primary: H1–D1) |
| **Complexity** | Advanced |
| **AI Suitability** | Very High — mathematically precise detection |
| **Version** | 2.0 |
| **Last Updated** | 2026-04-12 |

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [XABCD Framework](#2-xabcd-framework)
3. [Gartley Pattern](#3-gartley-pattern)
4. [Butterfly Pattern](#4-butterfly-pattern)
5. [Bat Pattern](#5-bat-pattern)
6. [Crab Pattern](#6-crab-pattern)
7. [Shark Pattern (0-5 Pattern)](#7-shark-pattern-0-5-pattern)
8. [Cypher Pattern](#8-cypher-pattern)
9. [Three Drives Pattern](#9-three-drives-pattern)
10. [Pattern Detection Algorithm](#10-pattern-detection-algorithm)
11. [Potential Reversal Zone (PRZ) Calculation](#11-potential-reversal-zone-prz-calculation)
12. [Entry and Exit Rules](#12-entry-and-exit-rules)
13. [Mathematical Formulas](#13-mathematical-formulas)
14. [Risk Parameters](#14-risk-parameters)
15. [Execution Flow](#15-execution-flow)
16. [AI Implementation Notes](#16-ai-implementation-notes)
17. [References](#17-references)

---

## 1. Introduction

Harmonic pattern trading is a methodology that uses specific Fibonacci ratio alignments to identify potential reversal zones in financial markets. Pioneered by H.M. Gartley in 1935 and refined by Scott Carney in the late 1990s, harmonic patterns provide mathematically precise price structures that, when completed, offer high-probability reversal setups.

### 1.1 Core Thesis

- Financial markets exhibit geometric price structures that repeat at fractal scales.
- These structures are defined by specific Fibonacci ratio relationships between price swings.
- When multiple Fibonacci ratios converge at a single price zone (the Potential Reversal Zone), the probability of a price reversal is significantly elevated.
- The mathematical precision of harmonic patterns makes them exceptionally suited for algorithmic detection and execution.

### 1.2 Fibonacci Ratios Used

The primary Fibonacci ratios used in harmonic patterns:

| Ratio | Type | Origin |
|-------|------|--------|
| 0.236 | Retracement | $\phi^{-4}$ approximation |
| 0.382 | Retracement | $1 - 0.618$ |
| 0.500 | Retracement | Midpoint |
| 0.618 | Retracement | $\phi^{-1} = \frac{\sqrt{5} - 1}{2}$ |
| 0.707 | Retracement | $\frac{1}{\sqrt{2}}$ |
| 0.786 | Retracement | $\sqrt{0.618}$ |
| 0.886 | Retracement | $0.618^{0.618}$ or $\sqrt[4]{0.618}$ |
| 1.000 | Extension | Unity |
| 1.128 | Extension | $\sqrt[4]{1.618}$ |
| 1.272 | Extension | $\sqrt{1.618}$ |
| 1.414 | Extension | $\sqrt{2}$ |
| 1.618 | Extension | $\phi = \frac{1 + \sqrt{5}}{2}$ |
| 2.000 | Extension | Double |
| 2.240 | Extension | $\sqrt{5}$ |
| 2.618 | Extension | $\phi^2$ |
| 3.618 | Extension | $\phi^2 + 1$ |

### 1.3 Tolerance Levels

No pattern achieves exact Fibonacci ratios. The AI agent must use tolerance windows:

$$\text{Valid} = |R_{\text{actual}} - R_{\text{ideal}}| \leq \epsilon \times R_{\text{ideal}}$$

Default tolerance: $\epsilon = 0.02$ to $0.05$ (2–5%) depending on the specific ratio and timeframe.

---

## 2. XABCD Framework

All harmonic patterns (except Three Drives) follow the XABCD framework — five points connected by four price swings.

### 2.1 Point Definitions

- **X**: The starting point of the pattern.
- **A**: The end of the first impulse move (XA leg).
- **B**: The retracement of the XA leg.
- **C**: The retracement of the AB leg (extends beyond A for some patterns).
- **D**: The completion point — the Potential Reversal Zone (PRZ).

### 2.2 Leg Ratios

Each pattern is defined by the Fibonacci relationships between its legs:

$$R_{AB} = \frac{|B - A|}{|A - X|} \quad \text{(AB retracement of XA)}$$

$$R_{BC} = \frac{|C - B|}{|B - A|} \quad \text{(BC retracement of AB)}$$

$$R_{CD} = \frac{|D - C|}{|C - B|} \quad \text{(CD extension of BC)}$$

$$R_{XD} = \frac{|D - X|}{|A - X|} \quad \text{(XD retracement/extension of XA)}$$

### 2.3 Bullish vs. Bearish

- **Bullish pattern**: X is a low, A is a high → D completes at a low → expect price to reverse UP.
- **Bearish pattern**: X is a high, A is a low → D completes at a high → expect price to reverse DOWN.

---

## 3. Gartley Pattern

The original harmonic pattern, described by H.M. Gartley in "Profits in the Stock Market" (1935) and refined with exact ratios by Scott Carney.

### 3.1 Ratio Requirements

| Leg | Fibonacci Ratio | Tolerance |
|-----|----------------|-----------|
| AB = retracement of XA | **0.618** | 0.582 – 0.654 |
| BC = retracement of AB | **0.382 – 0.886** | 0.362 – 0.906 |
| CD = extension of BC | **1.272 – 1.618** | 1.222 – 1.668 |
| XD = retracement of XA | **0.786** | 0.746 – 0.826 |

### 3.2 Critical Ratio

The **defining ratio** of the Gartley is $R_{XD} = 0.786$. If this ratio is not within tolerance, the pattern is not a valid Gartley regardless of other ratios.

### 3.3 Formal Conditions

$$\text{Gartley} = \begin{cases} 0.582 \leq R_{AB} \leq 0.654 \\ 0.362 \leq R_{BC} \leq 0.906 \\ 1.222 \leq R_{CD} \leq 1.668 \\ 0.746 \leq R_{XD} \leq 0.826 \\ B \text{ does not exceed } X \end{cases}$$

### 3.4 PRZ Components

The Gartley PRZ is formed by the convergence of:
1. $D = X + 0.786 \times (A - X)$ — XA 0.786 retracement
2. $D = C + R_{CD} \times (B - C)$ — BC extension (1.272 to 1.618)
3. Optional: AB=CD completion point

### 3.5 Trading Rules

**Bullish Gartley**:
- Entry: Limit buy at or within the PRZ.
- Stop Loss: Below X.
- TP1: 0.382 retracement of AD.
- TP2: 0.618 retracement of AD.
- TP3: A point (full AD retracement).

**Bearish Gartley**:
- Entry: Limit sell at or within the PRZ.
- Stop Loss: Above X.
- TP1–TP3: Mirror of bullish targets.

### 3.6 Historical Win Rate

Based on empirical studies (Carney, 2010; Pesavento, 1997):
- Win Rate: 60–70% with proper PRZ confirmation.
- Average R:R: 2:1 to 3:1.

---

## 4. Butterfly Pattern

Discovered by Bryce Gilmore and defined by Scott Carney. The Butterfly is an **extension pattern** where D extends beyond X.

### 4.1 Ratio Requirements

| Leg | Fibonacci Ratio | Tolerance |
|-----|----------------|-----------|
| AB = retracement of XA | **0.786** | 0.746 – 0.826 |
| BC = retracement of AB | **0.382 – 0.886** | 0.362 – 0.906 |
| CD = extension of BC | **1.618 – 2.618** | 1.568 – 2.668 |
| XD = extension of XA | **1.272 or 1.618** | 1.222 – 1.668 |

### 4.2 Critical Ratio

The defining feature is $R_{AB} = 0.786$ and $R_{XD} \geq 1.272$. Point D **must extend beyond X**.

### 4.3 Formal Conditions

$$\text{Butterfly} = \begin{cases} 0.746 \leq R_{AB} \leq 0.826 \\ 0.362 \leq R_{BC} \leq 0.906 \\ 1.568 \leq R_{CD} \leq 2.668 \\ 1.222 \leq R_{XD} \leq 1.668 \\ D \text{ extends beyond } X \end{cases}$$

### 4.4 PRZ Components

1. $D = X + 1.272 \times (A - X)$ or $D = X + 1.618 \times (A - X)$
2. BC extension: 1.618 to 2.618
3. Optional: AB=CD or alternate AB=CD (1.272 AB=CD)

### 4.5 Trading Rules

**Bullish Butterfly**:
- Entry: Limit buy at PRZ (D below X).
- Stop Loss: Below the 1.618 XA extension (or fixed ATR buffer below D).
- TP1: B level.
- TP2: A level.
- TP3: C level.

**Note**: Because D is beyond X, the stop loss is based on the XA extension rather than X itself. Use the next Fibonacci extension level (e.g., if D at 1.272 XA, SL at 1.414 XA).

---

## 5. Bat Pattern

Discovered by Scott Carney in 2001. The Bat is a retracement pattern similar to the Gartley but with deeper D-point retracement.

### 5.1 Ratio Requirements

| Leg | Fibonacci Ratio | Tolerance |
|-----|----------------|-----------|
| AB = retracement of XA | **0.382 – 0.500** | 0.362 – 0.520 |
| BC = retracement of AB | **0.382 – 0.886** | 0.362 – 0.906 |
| CD = extension of BC | **1.618 – 2.618** | 1.568 – 2.668 |
| XD = retracement of XA | **0.886** | 0.846 – 0.926 |

### 5.2 Critical Ratio

The defining ratio is $R_{XD} = 0.886$. This is the deepest retracement pattern (of the classic four) and offers a tight stop loss placement.

### 5.3 Formal Conditions

$$\text{Bat} = \begin{cases} 0.362 \leq R_{AB} \leq 0.520 \\ 0.362 \leq R_{BC} \leq 0.906 \\ 1.568 \leq R_{CD} \leq 2.668 \\ 0.846 \leq R_{XD} \leq 0.926 \\ B \text{ does not exceed } X \end{cases}$$

### 5.4 PRZ Components

1. $D = X + 0.886 \times (A - X)$
2. BC extension: 1.618 to 2.618
3. Optional: AB=CD completion

### 5.5 Trading Rules

**Bullish Bat**:
- Entry: Limit buy at PRZ.
- Stop Loss: Below X (tight — because D is at 0.886 of XA, SL is only ~11.4% of XA leg away).
- TP1: 0.382 of AD.
- TP2: 0.618 of AD.
- TP3: A level.

**Advantage**: The Bat offers the tightest SL of all classic harmonic patterns relative to potential reward, making it excellent for risk-adjusted returns.

---

## 6. Crab Pattern

Discovered by Scott Carney in 2000. The Crab is an extreme extension pattern with D at the 1.618 XA extension.

### 6.1 Ratio Requirements

| Leg | Fibonacci Ratio | Tolerance |
|-----|----------------|-----------|
| AB = retracement of XA | **0.382 – 0.618** | 0.362 – 0.638 |
| BC = retracement of AB | **0.382 – 0.886** | 0.362 – 0.906 |
| CD = extension of BC | **2.618 – 3.618** | 2.568 – 3.668 |
| XD = extension of XA | **1.618** | 1.568 – 1.668 |

### 6.2 Critical Ratio

$R_{XD} = 1.618$ — the Golden Ratio extension. This is the most extreme of the standard patterns.

### 6.3 Formal Conditions

$$\text{Crab} = \begin{cases} 0.362 \leq R_{AB} \leq 0.638 \\ 0.362 \leq R_{BC} \leq 0.906 \\ 2.568 \leq R_{CD} \leq 3.668 \\ 1.568 \leq R_{XD} \leq 1.668 \\ D \text{ extends significantly beyond } X \end{cases}$$

### 6.4 Deep Crab Variant

The **Deep Crab** has $R_{AB} = 0.886$ instead of 0.382–0.618:

$$\text{DeepCrab} = \begin{cases} 0.846 \leq R_{AB} \leq 0.926 \\ 0.382 \leq R_{BC} \leq 0.886 \\ 2.000 \leq R_{CD} \leq 3.618 \\ 1.618 \leq R_{XD} \leq 1.668 \end{cases}$$

### 6.5 Trading Rules

**Bullish Crab**:
- Entry: Limit buy at PRZ.
- Stop Loss: Below the 2.000 XA extension (next level beyond 1.618).
- TP1: B level.
- TP2: A level.
- TP3: Beyond A (aggressive target due to the extreme extension).

**Note**: The Crab's extreme D point means the reversal, when it occurs, is often powerful. However, the risk is higher because D overshoots X significantly.

---

## 7. Shark Pattern (0-5 Pattern)

Discovered by Scott Carney in 2011. Unlike other XABCD patterns, the Shark uses a different labeling system (0-X-A-B-C) and trades the completion of C rather than D.

### 7.1 Ratio Requirements

| Leg | Fibonacci Ratio | Tolerance |
|-----|----------------|-----------|
| XA = retracement of 0X | Any | — |
| AB = extension of XA | **1.128 – 1.618** | 1.078 – 1.668 |
| BC = extension of 0X | **0.886 or 1.128** | 0.836 – 1.178 |

### 7.2 Critical Ratios

The Shark is defined by:
- AB extends beyond X (i.e., $R_{AB/XA} \geq 1.128$).
- BC terminates at the 0.886 or 1.128 extension of the 0X leg.

### 7.3 Formal Conditions

$$\text{Shark} = \begin{cases} 1.078 \leq R_{AB} \leq 1.668 \quad \text{(AB as extension of XA)} \\ 1.618 \leq R_{BC/AB} \leq 2.240 \quad \text{(BC as extension of AB)} \\ 0.836 \leq R_{BC/0X} \leq 1.178 \quad \text{(BC as ratio of 0X)} \end{cases}$$

### 7.4 Trading Rules

**Bullish Shark**:
- Entry: At C point completion (the PRZ).
- Stop Loss: Below the 1.272 extension of 0X.
- TP1: 0.382 retracement of BC.
- TP2: 0.618 retracement of BC.

**Note**: The Shark often transforms into a 5-0 pattern after the initial reversal at C. The 5-0 pattern provides a secondary trade opportunity.

### 7.5 The 5-0 Pattern (Follow-up to Shark)

After a Shark completes and reverses, the resulting structure forms a 5-0 pattern:
- The 50% retracement of the Shark's BC leg becomes the entry for the 5-0 pattern.
- This is a continuation trade in the direction of the Shark's initial reversal.

---

## 8. Cypher Pattern

Developed by Darren Oglesbee. The Cypher is not part of Carney's original catalog but has gained widespread adoption.

### 8.1 Ratio Requirements

| Leg | Fibonacci Ratio | Tolerance |
|-----|----------------|-----------|
| AB = retracement of XA | **0.382 – 0.618** | 0.362 – 0.638 |
| BC = extension of XA | **1.272 – 1.414** | 1.222 – 1.464 |
| CD = retracement of XC | **0.786** | 0.746 – 0.826 |

### 8.2 Critical Ratios

- C extends beyond A (BC is an extension of XA).
- D is at the 0.786 retracement of the entire XC leg.

### 8.3 Formal Conditions

$$\text{Cypher} = \begin{cases} 0.362 \leq R_{AB/XA} \leq 0.638 \\ C \text{ exceeds } A \\ 1.222 \leq R_{XC/XA} \leq 1.464 \\ 0.746 \leq R_{CD/XC} \leq 0.826 \end{cases}$$

### 8.4 PRZ Calculation

$$D = C - 0.786 \times (C - X) \quad \text{(for bullish Cypher)}$$
$$D = C + 0.786 \times (X - C) \quad \text{(for bearish Cypher)}$$

### 8.5 Trading Rules

**Bullish Cypher**:
- Entry: Buy at D (0.786 XC retracement).
- Stop Loss: Below X.
- TP1: A level.
- TP2: C level.

**Win Rate**: The Cypher is considered one of the more reliable patterns, with empirical win rates of 55–65%.

---

## 9. Three Drives Pattern

The Three Drives pattern is unique — it does not follow the XABCD framework but consists of three consecutive impulse drives in the same direction, each separated by a Fibonacci retracement.

### 9.1 Structure

```
Bullish Three Drives (reversal from bearish to bullish):
    Drive 1: Swing high to low (bearish)
    Retracement 1: 0.618 or 0.786 of Drive 1
    Drive 2: Extends to 1.272 or 1.618 of Retracement 1
    Retracement 2: 0.618 or 0.786 of Drive 2
    Drive 3: Extends to 1.272 or 1.618 of Retracement 2
    → Completion at Drive 3 = BUY signal

Bearish Three Drives (reversal from bullish to bearish):
    Drive 1: Swing low to high (bullish)
    Retracement 1: 0.618 or 0.786 of Drive 1
    Drive 2: Extends to 1.272 or 1.618 of Retracement 1
    Retracement 2: 0.618 or 0.786 of Drive 2
    Drive 3: Extends to 1.272 or 1.618 of Retracement 2
    → Completion at Drive 3 = SELL signal
```

### 9.2 Ratio Requirements

| Component | Fibonacci Ratio | Tolerance |
|-----------|----------------|-----------|
| Retracement 1 = retrace of Drive 1 | **0.618 or 0.786** | 0.582 – 0.826 |
| Drive 2 = extension of Retracement 1 | **1.272 or 1.618** | 1.222 – 1.668 |
| Retracement 2 = retrace of Drive 2 | **0.618 or 0.786** | 0.582 – 0.826 |
| Drive 3 = extension of Retracement 2 | **1.272 or 1.618** | 1.222 – 1.668 |

### 9.3 Symmetry Requirement

The three drives should be approximately equal in:
- **Price distance**: $|D_1| \approx |D_2| \approx |D_3|$ (within 20%).
- **Time duration**: $T_1 \approx T_2 \approx T_3$ (within 30%).

$$\text{SymmetryScore} = 1 - \frac{\max(|D_i|) - \min(|D_i|)}{\text{mean}(|D_i|)}$$

Minimum symmetry: $\text{SymmetryScore} \geq 0.70$.

### 9.4 Trading Rules

- Entry: At the completion of Drive 3.
- Stop Loss: Beyond Drive 3 by 0.272 of Drive 3's range.
- TP1: Start of Drive 3 (Retracement 2 high/low).
- TP2: Start of Drive 2.

---

## 10. Pattern Detection Algorithm

### 10.1 Swing Point Identification

The first step in harmonic pattern detection is identifying significant swing points.

```python
def find_swing_points(candles, lookback=5, min_swing_size_atr=0.5):
    """
    Identify significant swing highs and lows.
    """
    atr = calculate_atr(candles, 14)
    swings = []
    
    for i in range(lookback, len(candles) - lookback):
        # Check swing high
        is_high = all(candles[i].high >= candles[j].high 
                      for j in range(i - lookback, i + lookback + 1) if j != i)
        
        if is_high:
            # Verify minimum swing size
            prev_low = min(c.low for c in candles[i - lookback:i])
            if (candles[i].high - prev_low) >= min_swing_size_atr * atr[i]:
                swings.append({"index": i, "price": candles[i].high, "type": "HIGH"})
        
        # Check swing low
        is_low = all(candles[i].low <= candles[j].low 
                     for j in range(i - lookback, i + lookback + 1) if j != i)
        
        if is_low:
            next_high = max(c.high for c in candles[i:i + lookback + 1])
            if (next_high - candles[i].low) >= min_swing_size_atr * atr[i]:
                swings.append({"index": i, "price": candles[i].low, "type": "LOW"})
    
    return swings
```

### 10.2 XABCD Pattern Scanner

```python
def scan_harmonic_patterns(swings, tolerance=0.04):
    """
    Scan swing points for all harmonic pattern types.
    Returns a list of detected patterns with metadata.
    """
    patterns = []
    
    # Need at least 5 alternating swing points for XABCD
    for i in range(len(swings) - 4):
        X, A, B, C, D = swings[i], swings[i+1], swings[i+2], swings[i+3], swings[i+4]
        
        # Verify alternating types (HIGH-LOW-HIGH-LOW-HIGH or LOW-HIGH-LOW-HIGH-LOW)
        types = [s["type"] for s in [X, A, B, C, D]]
        if not is_alternating(types):
            continue
        
        # Calculate ratios
        XA = abs(A["price"] - X["price"])
        AB = abs(B["price"] - A["price"])
        BC = abs(C["price"] - B["price"])
        CD = abs(D["price"] - C["price"])
        XD = abs(D["price"] - X["price"])
        
        if XA == 0:
            continue
        
        r_AB = AB / XA
        r_BC = BC / AB if AB != 0 else 0
        r_CD = CD / BC if BC != 0 else 0
        r_XD = XD / XA
        
        # Check each pattern type
        ratios = {"AB": r_AB, "BC": r_BC, "CD": r_CD, "XD": r_XD}
        
        # Gartley check
        if check_gartley(ratios, tolerance):
            patterns.append(build_pattern("GARTLEY", X, A, B, C, D, ratios))
        
        # Butterfly check
        if check_butterfly(ratios, tolerance):
            patterns.append(build_pattern("BUTTERFLY", X, A, B, C, D, ratios))
        
        # Bat check
        if check_bat(ratios, tolerance):
            patterns.append(build_pattern("BAT", X, A, B, C, D, ratios))
        
        # Crab check
        if check_crab(ratios, tolerance):
            patterns.append(build_pattern("CRAB", X, A, B, C, D, ratios))
        
        # Cypher check (uses XC ratio instead of standard)
        XC = abs(C["price"] - X["price"])
        r_XC = XC / XA if XA != 0 else 0
        r_CD_XC = CD / XC if XC != 0 else 0
        cypher_ratios = {"AB": r_AB, "XC": r_XC, "CD_XC": r_CD_XC}
        
        if check_cypher(cypher_ratios, tolerance):
            patterns.append(build_pattern("CYPHER", X, A, B, C, D, cypher_ratios))
    
    return patterns


def check_gartley(ratios, tol):
    return (within(ratios["AB"], 0.618, tol) and
            within_range(ratios["BC"], 0.382, 0.886, tol) and
            within_range(ratios["CD"], 1.272, 1.618, tol) and
            within(ratios["XD"], 0.786, tol))


def check_butterfly(ratios, tol):
    return (within(ratios["AB"], 0.786, tol) and
            within_range(ratios["BC"], 0.382, 0.886, tol) and
            within_range(ratios["CD"], 1.618, 2.618, tol) and
            within_range(ratios["XD"], 1.272, 1.618, tol))


def check_bat(ratios, tol):
    return (within_range(ratios["AB"], 0.382, 0.500, tol) and
            within_range(ratios["BC"], 0.382, 0.886, tol) and
            within_range(ratios["CD"], 1.618, 2.618, tol) and
            within(ratios["XD"], 0.886, tol))


def check_crab(ratios, tol):
    return (within_range(ratios["AB"], 0.382, 0.618, tol) and
            within_range(ratios["BC"], 0.382, 0.886, tol) and
            within_range(ratios["CD"], 2.618, 3.618, tol) and
            within(ratios["XD"], 1.618, tol))


def check_cypher(ratios, tol):
    return (within_range(ratios["AB"], 0.382, 0.618, tol) and
            within_range(ratios["XC"], 1.272, 1.414, tol) and
            within(ratios["CD_XC"], 0.786, tol))


def within(actual, ideal, tol):
    return abs(actual - ideal) <= tol * ideal


def within_range(actual, low, high, tol):
    return (low * (1 - tol)) <= actual <= (high * (1 + tol))
```

### 10.3 Pattern Quality Scoring

```python
def score_pattern(pattern, tolerance=0.04):
    """
    Score a detected harmonic pattern based on ratio precision,
    symmetry, and additional confluences.
    """
    # Ratio precision: how close each ratio is to the ideal
    ideal_ratios = PATTERN_IDEALS[pattern.type]
    precision_scores = []
    
    for ratio_name, actual in pattern.ratios.items():
        ideal = ideal_ratios[ratio_name]
        if isinstance(ideal, tuple):
            ideal_mid = (ideal[0] + ideal[1]) / 2
        else:
            ideal_mid = ideal
        
        deviation = abs(actual - ideal_mid) / ideal_mid
        precision = max(0, 1 - deviation / tolerance)
        precision_scores.append(precision)
    
    ratio_score = sum(precision_scores) / len(precision_scores)
    
    # Time symmetry: AB and CD legs should be roughly equal in time
    time_AB = pattern.B.index - pattern.A.index
    time_CD = pattern.D.index - pattern.C.index
    time_symmetry = 1 - abs(time_AB - time_CD) / max(time_AB, time_CD)
    
    # PRZ confluence: number of Fibonacci levels converging at D
    prz_levels = count_prz_confluences(pattern)
    prz_score = min(prz_levels / 3, 1.0)  # Max score at 3+ confluences
    
    # Composite score
    total = 0.50 * ratio_score + 0.25 * time_symmetry + 0.25 * prz_score
    
    return total
```

---

## 11. Potential Reversal Zone (PRZ) Calculation

### 11.1 PRZ Definition

The PRZ is the price zone where multiple Fibonacci projections from different legs of the pattern converge. It is the zone where the reversal is expected to occur.

### 11.2 PRZ Calculation Method

For each pattern, the PRZ is calculated as the intersection of:

1. **XA retracement/extension at D**: The primary ratio defining D relative to XA.
2. **BC projection at D**: The CD extension of BC.
3. **AB=CD completion**: The price level where CD equals AB (optionally adjusted by 1.272 or 1.618).

```python
def calculate_prz(pattern):
    """
    Calculate the Potential Reversal Zone for an XABCD pattern.
    Returns the PRZ as a price range [lower, upper].
    """
    X, A, B, C = pattern.X, pattern.A, pattern.B, pattern.C
    
    prz_levels = []
    
    # Level 1: XA retracement/extension
    xa_ratio = PATTERN_XD_RATIO[pattern.type]
    if isinstance(xa_ratio, tuple):
        for r in xa_ratio:
            level = X.price + r * (A.price - X.price) if pattern.bullish else X.price - r * (X.price - A.price)
            prz_levels.append(level)
    else:
        level = X.price + xa_ratio * (A.price - X.price) if pattern.bullish else X.price - xa_ratio * (X.price - A.price)
        prz_levels.append(level)
    
    # Level 2: BC extension
    bc_ratios = PATTERN_CD_RATIO[pattern.type]
    for r in [bc_ratios] if not isinstance(bc_ratios, tuple) else bc_ratios:
        level = C.price - r * (B.price - C.price) if pattern.bullish else C.price + r * (C.price - B.price)
        prz_levels.append(level)
    
    # Level 3: AB=CD
    ab = abs(A.price - B.price)
    abcd_level = C.price - ab if pattern.bullish else C.price + ab
    prz_levels.append(abcd_level)
    
    # PRZ = range from min to max of converging levels
    prz_lower = min(prz_levels)
    prz_upper = max(prz_levels)
    
    # If PRZ is too wide, use the tightest cluster
    if (prz_upper - prz_lower) > 1.5 * pattern.atr:
        prz_lower, prz_upper = find_tightest_cluster(prz_levels, max_width=1.0 * pattern.atr)
    
    return {"lower": prz_lower, "upper": prz_upper, "levels": prz_levels}
```

### 11.3 PRZ Width Validation

$$W_{\text{PRZ}} = \frac{|\text{PRZ\_Upper} - \text{PRZ\_Lower}|}{\text{ATR}(14)}$$

| PRZ Width (ATR) | Quality | Action |
|-----------------|---------|--------|
| $\leq 0.5$ | Excellent — tight convergence | Trade with confidence |
| 0.5 – 1.0 | Good | Trade with standard size |
| 1.0 – 1.5 | Acceptable | Trade with reduced size |
| $> 1.5$ | Poor — levels too spread | Skip or wait for LTF refinement |

---

## 12. Entry and Exit Rules

### 12.1 Entry Methods

**Method 1: Limit Order at PRZ (Aggressive)**
- Place a limit order at the PRZ midpoint.
- Advantage: Best possible entry.
- Risk: No confirmation; D may not hold.

**Method 2: Candle Confirmation at PRZ (Conservative)**
- Wait for price to enter PRZ.
- Wait for a reversal candlestick (pin bar, engulfing, doji) to form at the PRZ.
- Enter on the close of the confirmation candle.

**Method 3: Structural Confirmation (Most Conservative)**
- Wait for price to enter PRZ.
- Wait for a lower-timeframe break of structure (BOS) confirming reversal.
- Enter on the pullback after the BOS.

### 12.2 Stop Loss Rules

| Pattern | SL Placement (Bullish) | SL Placement (Bearish) |
|---------|----------------------|----------------------|
| Gartley | Below X | Above X |
| Bat | Below X (tight due to 0.886) | Above X |
| Butterfly | Below 1.618 XA extension | Above 1.618 XA extension |
| Crab | Below 2.000 XA extension | Above 2.000 XA extension |
| Cypher | Below X | Above X |
| Shark | Below 1.272 of 0X extension | Above 1.272 of 0X extension |

Buffer: Add $0.2 \times \text{ATR}(14)$ to the SL level.

### 12.3 Take Profit Targets

Standard TP levels for all patterns (measured as retracements of the AD leg):

| Target | Fibonacci Level of AD | Action |
|--------|----------------------|--------|
| TP1 | 0.382 AD | Close 40% |
| TP2 | 0.618 AD | Close 30% |
| TP3 | A level (1.0 AD) | Close 20% |
| Trail | Beyond A | Trail remaining 10% |

For extension patterns (Butterfly, Crab):
| Target | Level | Action |
|--------|-------|--------|
| TP1 | B level | Close 40% |
| TP2 | A level | Close 30% |
| TP3 | C level | Close 20% |
| Trail | Beyond C | Trail 10% |

### 12.4 Pattern-Specific Expected R:R

| Pattern | Typical R:R (to TP1) | Typical R:R (to TP2) |
|---------|----------------------|----------------------|
| Gartley | 1.5:1 | 3:1 |
| Bat | 2:1 | 4:1 |
| Butterfly | 2:1 | 4:1 |
| Crab | 1.5:1 | 3.5:1 |
| Cypher | 1.5:1 | 3:1 |
| Shark | 1.5:1 | 2.5:1 |
| Three Drives | 2:1 | 3.5:1 |

---

## 13. Mathematical Formulas

### 13.1 Fibonacci Ratio Derivations

The Golden Ratio:
$$\phi = \frac{1 + \sqrt{5}}{2} \approx 1.6180339887$$

Key derivations:
$$\phi^{-1} = \phi - 1 = \frac{\sqrt{5} - 1}{2} \approx 0.618$$

$$\phi^{-2} = 2 - \phi = \frac{3 - \sqrt{5}}{2} \approx 0.382$$

$$\sqrt{\phi^{-1}} = \sqrt{0.618} \approx 0.786$$

$$\phi^{-1 \cdot \phi^{-1}} = 0.618^{0.618} \approx 0.724 \quad \text{(sometimes cited as 0.886 origin)}$$

More precisely, $0.886 = \sqrt[4]{0.618} = 0.618^{0.25}$:
$$\sqrt[4]{0.618} \approx 0.886$$

$$\sqrt{\phi} = \sqrt{1.618} \approx 1.272$$

$$\phi^2 = \phi + 1 \approx 2.618$$

### 13.2 Pattern Symmetry Index

Measures how "ideal" the time relationships are within the pattern:

$$\text{TSI} = 1 - \frac{1}{2}\left(\frac{|T_{AB} - T_{CD}|}{\max(T_{AB}, T_{CD})} + \frac{|T_{BC} - T_{AD}/2|}{\max(T_{BC}, T_{AD}/2)}\right)$$

Where $T_{XY}$ is the number of candles between points X and Y.

### 13.3 PRZ Convergence Density

$$\rho_{\text{PRZ}} = \frac{N_{\text{levels}}}{\text{PRZ\_Width} / \text{ATR}}$$

Higher density = tighter PRZ = higher quality. Target: $\rho_{\text{PRZ}} \geq 3$.

### 13.4 Pattern Completion Probability

The probability that a forming pattern will complete (reach D) given that X, A, B, C are established:

$$P(D \mid X, A, B, C) = P_{\text{base}} \times f(R_{AB}) \times f(R_{BC}) \times g(\text{trend alignment})$$

Where:
- $P_{\text{base}} \approx 0.4$ (base probability of completion)
- $f(R) = e^{-10(R - R_{\text{ideal}})^2}$ (Gaussian penalty for ratio deviation)
- $g(\text{trend}) = 1.3$ if with trend, $0.8$ if counter-trend

### 13.5 Expected Value of Harmonic Trade

$$\text{EV} = P_{\text{complete}} \times [P_{\text{win}} \times \text{Avg\_Win} - (1 - P_{\text{win}}) \times \text{Avg\_Loss}]$$

For a typical Gartley with $P_{\text{complete}} = 0.45$, $P_{\text{win}} = 0.65$, $\text{RR} = 2.5$:

$$\text{EV} = 0.45 \times [0.65 \times 2.5R - 0.35 \times R] = 0.45 \times [1.625R - 0.35R] = 0.45 \times 1.275R = 0.574R$$

---

## 14. Risk Parameters

### 14.1 Position Sizing

$$\text{Size} = \frac{\text{Balance} \times R\%}{|E - SL| \times \text{Unit Value}}$$

Risk per trade based on pattern quality:

| Pattern Score | Risk % |
|--------------|--------|
| $\geq 0.85$ | 1.5% |
| 0.70 – 0.84 | 1.0% |
| 0.55 – 0.69 | 0.5% |
| $< 0.55$ | No trade |

### 14.2 Portfolio Constraints

- Maximum 2 harmonic pattern trades open simultaneously.
- Maximum 3% total portfolio risk from harmonic strategies.
- Avoid trading multiple patterns of the same type at the same time (reduces model risk).
- Diversify across at least 2 uncorrelated instruments.

### 14.3 Invalidation Rules

A pattern is invalidated if:
1. Price closes beyond the SL level before the PRZ is reached (pre-entry invalidation).
2. Point C violates pattern rules (e.g., in a Gartley, C cannot exceed A).
3. Time decay: if the CD leg takes more than 3x the time of the AB leg, the pattern loses significance.

---

## 15. Execution Flow

### 15.1 Complete Strategy Pseudocode

```python
def harmonic_pattern_strategy():
    """
    Complete harmonic pattern trading strategy.
    """
    
    # ================================================
    # PHASE 1: PATTERN DETECTION
    # ================================================
    
    for instrument in watchlist:
        for timeframe in ["D1", "H4", "H1"]:
            candles = fetch_candles(instrument, timeframe, count=300)
            atr = calculate_atr(candles, 14)
            
            # Find swing points
            swings = find_swing_points(candles, lookback=5, min_swing_size_atr=0.5)
            
            # Scan for completed patterns
            completed_patterns = scan_harmonic_patterns(swings, tolerance=0.04)
            
            # Scan for forming patterns (XABC complete, waiting for D)
            forming_patterns = scan_forming_patterns(swings, tolerance=0.04)
            
            for pattern in completed_patterns:
                pattern.score = score_pattern(pattern)
                pattern.prz = calculate_prz(pattern)
                pattern.instrument = instrument
                pattern.timeframe = timeframe
                pattern.atr = atr[-1]
    
    # ================================================
    # PHASE 2: FILTER AND RANK
    # ================================================
    
    # Filter by quality
    tradeable = [p for p in completed_patterns if p.score >= 0.55]
    
    # Filter by PRZ width
    tradeable = [p for p in tradeable 
                 if (p.prz["upper"] - p.prz["lower"]) / p.atr <= 1.5]
    
    # Rank by score
    tradeable.sort(key=lambda p: p.score, reverse=True)
    
    # ================================================
    # PHASE 3: ENTRY EVALUATION
    # ================================================
    
    for pattern in tradeable:
        current_price = get_price(pattern.instrument)
        
        # Check if price is in or near the PRZ
        if not price_near_prz(current_price, pattern.prz, threshold=0.3 * pattern.atr):
            if pattern.score >= 0.70:
                # Set limit order at PRZ for high-quality patterns
                set_limit_order(pattern)
            continue
        
        # Price is at the PRZ — look for confirmation
        if pattern.score >= 0.85:
            # A+ pattern: risk entry (limit order at PRZ)
            entry = prz_midpoint(pattern)
        else:
            # Standard: wait for candlestick confirmation
            confirmation = check_reversal_candle(pattern, candles)
            if not confirmation:
                continue
            entry = confirmation.price
        
        # ================================================
        # PHASE 4: RISK CALCULATION
        # ================================================
        
        sl = calculate_sl(pattern)
        tp1, tp2, tp3 = calculate_targets(pattern)
        
        rr_tp1 = abs(tp1 - entry) / abs(entry - sl)
        
        if rr_tp1 < 1.5:
            log(f"R:R {rr_tp1:.1f} too low for {pattern.type}")
            continue
        
        # Position sizing
        risk_pct = get_risk_pct(pattern.score)
        position_size = calculate_position_size(balance, risk_pct, entry, sl)
        
        # Portfolio checks
        if not check_portfolio_limits(pattern, position_size):
            continue
        
        # ================================================
        # PHASE 5: EXECUTE
        # ================================================
        
        trade = execute_order(
            instrument=pattern.instrument,
            direction="BUY" if pattern.bullish else "SELL",
            entry=entry,
            sl=sl,
            tp_levels=[
                {"price": tp1, "close_pct": 0.40},
                {"price": tp2, "close_pct": 0.30},
                {"price": tp3, "close_pct": 0.20}
            ],
            trailing_stop_pct=0.10,
            size=position_size,
            metadata={
                "pattern_type": pattern.type,
                "pattern_score": pattern.score,
                "prz": pattern.prz,
                "ratios": pattern.ratios
            }
        )
        
        log_trade(trade)
        return trade
    
    # ================================================
    # PHASE 6: MANAGE FORMING PATTERNS
    # ================================================
    
    for pattern in forming_patterns:
        prz = project_prz(pattern)  # Project where D should complete
        set_price_alert(pattern.instrument, prz)
        log(f"Forming {pattern.type} on {pattern.instrument} {pattern.timeframe}, "
            f"PRZ projected at {prz}")
    
    return WAIT("No actionable harmonic pattern")
```

---

## 16. AI Implementation Notes

### 16.1 Computational Complexity

- Swing detection: $O(n \times k)$ where $n$ = candles, $k$ = lookback.
- Pattern scanning: $O(s^5)$ where $s$ = number of swings (worst case), but alternation constraint reduces to $O(s)$.
- Overall per instrument/timeframe: $O(n)$ for swing detection + $O(s)$ for scanning.

### 16.2 Optimization Tips

1. Cache swing points and update incrementally (only recalculate when new candles form new swings).
2. Pre-filter: skip pattern checking if the current forming leg clearly violates ratio constraints.
3. Use early termination in ratio checks — check the critical ratio first (e.g., XD for Gartley).

### 16.3 False Positive Management

Harmonic patterns can produce false signals. Mitigate with:
1. **HTF trend alignment**: Only trade patterns that align with the higher-timeframe trend.
2. **Volume confirmation**: If volume data is available, look for volume spike at D.
3. **RSI/Stochastic divergence at D**: Adds confluence for the reversal.
4. **Avoid cluttered PRZs**: If multiple patterns compete at different PRZs, stick with the highest-scoring one.

### 16.4 Data Requirements

| Timeframe | Min History | Update Frequency |
|-----------|-------------|-----------------|
| Monthly | 10 years | Monthly |
| Weekly | 3 years | Weekly |
| Daily | 1 year | Daily |
| H4 | 6 months | Every 4 hours |
| H1 | 3 months | Every hour |
| M15 | 1 month | Every 15 minutes |

---

## 17. References

### Books
1. Gartley, H. M. (1935). *Profits in the Stock Market*. Lambert-Gann Publishing.
2. Carney, S. (1999). *The Harmonic Trader*. HarmonicTrader.com.
3. Carney, S. (2004). *Harmonic Trading, Volume One*. FT Press.
4. Carney, S. (2007). *Harmonic Trading, Volume Two*. FT Press.
5. Carney, S. (2010). *Harmonic Trading, Volume Three*. FT Press.
6. Pesavento, L. (1997). *Fibonacci Ratios with Pattern Recognition*. Traders Press.
7. Gilmore, B. (2000). *Geometry of Markets*. Bryce Gilmore & Associates.

### Academic Papers
8. Bulkowski, T. N. (2005). "Encyclopedia of Chart Patterns." Wiley — Statistical analysis of pattern reliability.
9. Lo, A. W., Mamaysky, H., & Wang, J. (2000). "Foundations of Technical Analysis." *The Journal of Finance*, 55(4), 1705–1765.
10. Friesen, G. C., Weller, P. A., & Dunham, L. M. (2009). "Price Trends and Patterns in Technical Analysis." *Journal of Banking & Finance*, 33(6), 1089–1100.

### Practitioner Sources
11. Oglesbee, D. (2013). "The Cypher Pattern" — AntiPattern LLC.
12. HarmonicTrader.com — Scott Carney's official resource for pattern definitions.
13. TradingView. "Harmonic Pattern Indicators" — Community-built detection tools.
14. Investopedia. "Harmonic Patterns in the Currency Markets" — Overview article.

---

*This document is part of the Multi-Agent AI Trading System knowledge base. It should be read in conjunction with the Fibonacci Advanced guide (12_fibonacci_advanced) and the Price Action guide (07_price_action).*
