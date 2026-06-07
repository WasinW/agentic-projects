# Elliott Wave Theory --- Fibonacci Price Targets & Cluster Analysis

## Document Metadata
| Field | Value |
|---|---|
| **Strategy ID** | EW-003 |
| **Category** | Axis 1 --- Trading Strategies |
| **Sub-Category** | Elliott Wave Theory --- Fibonacci Targets |
| **Applicable Markets** | Forex, Crypto |
| **Timeframes** | All (Multi-Timeframe) |
| **Complexity** | Advanced |
| **AI Suitability** | Very High (mathematical precision) |
| **Last Updated** | 2026-04-12 |

---

## Table of Contents
1. [Introduction to Fibonacci in Elliott Wave](#1-introduction-to-fibonacci-in-elliott-wave)
2. [Fibonacci Retracement Levels](#2-fibonacci-retracement-levels)
3. [Fibonacci Extension Levels](#3-fibonacci-extension-levels)
4. [Fibonacci Projection (Measured Move)](#4-fibonacci-projection-measured-move)
5. [Fibonacci Time Zones](#5-fibonacci-time-zones)
6. [Fibonacci Cluster Analysis](#6-fibonacci-cluster-analysis)
7. [Price Targets for Each Wave](#7-price-targets-for-each-wave)
8. [Mathematical Models and Formulas](#8-mathematical-models-and-formulas)
9. [Algorithm for High-Probability Reversal Zones](#9-algorithm-for-high-probability-reversal-zones)
10. [Core Logic --- Entry/Exit Based on Fibonacci Targets](#10-core-logic----entryexit-based-on-fibonacci-targets)
11. [Technical Specifications](#11-technical-specifications)
12. [Risk Parameters](#12-risk-parameters)
13. [Execution Flow](#13-execution-flow)
14. [Market-Specific Considerations](#14-market-specific-considerations)
15. [References](#15-references)

---

## 1. Introduction to Fibonacci in Elliott Wave

### 1.1 The Mathematical Foundation

The Fibonacci sequence, discovered by Leonardo of Pisa (Fibonacci) in 1202, is the mathematical backbone of Elliott Wave Theory. Ralph Nelson Elliott recognized that market waves relate to each other by Fibonacci ratios, connecting human collective behavior to the same mathematical principles that govern natural growth patterns.

**The Fibonacci Sequence:**

$$F_n = F_{n-1} + F_{n-2} \quad \text{where } F_0 = 0, \; F_1 = 1$$

$$0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, ...$$

**The Golden Ratio:**

$$\phi = \lim_{n \to \infty} \frac{F_{n+1}}{F_n} = \frac{1 + \sqrt{5}}{2} = 1.6180339887...$$

### 1.2 Derivation of Key Ratios

All Fibonacci ratios used in technical analysis derive from the sequence:

| Ratio | Derivation | Exact Value |
|---|---|---|
| 0.236 | $\frac{F_n}{F_{n+4}}$ (limit) | $\frac{1}{\phi^4} \approx 0.1459$ is wrong; actually $2 - \phi = 0.382^2 \approx 0.146$; correct: $1 - 0.764 = 0.236$ via $\phi^{-3}$ approximation |
| 0.382 | $\frac{F_n}{F_{n+2}}$ (limit) | $\frac{1}{\phi^2} = \phi - 1 = 2 - \phi = 0.38196...$ |
| 0.500 | $\frac{1}{2}$ (not Fibonacci, but significant) | $0.5$ |
| 0.618 | $\frac{F_n}{F_{n+1}}$ (limit) | $\frac{1}{\phi} = \phi - 1 = 0.61803...$ |
| 0.786 | $\sqrt{0.618}$ | $\frac{1}{\sqrt{\phi}} = 0.78615...$ |
| 0.886 | $\sqrt[4]{0.618}$ or $0.786^{1.5}$ | $\phi^{-1/4} \approx 0.88607...$ |
| 1.000 | Unity | $1.0$ |
| 1.272 | $\sqrt{1.618}$ | $\sqrt{\phi} = 1.27201...$ |
| 1.618 | $\frac{F_{n+1}}{F_n}$ (limit) | $\phi = 1.61803...$ |
| 2.000 | $2$ (not Fibonacci, but significant) | $2.0$ |
| 2.618 | $\phi^2 = \phi + 1$ | $2.61803...$ |
| 4.236 | $\phi^3 = 2\phi + 1$ | $4.23606...$ |

### 1.3 Three Types of Fibonacci Measurements

| Type | What It Measures | Application |
|---|---|---|
| **Retracement** | How far a wave pulls back from the previous wave | Wave 2, Wave 4, Wave B targets |
| **Extension** | How far a wave extends relative to a prior wave | Wave 3, Wave 5, Wave C targets |
| **Projection** | The measured move from one wave projected from another | Alternative targeting method |

---

## 2. Fibonacci Retracement Levels

### 2.1 Definition and Calculation

A Fibonacci retracement measures the percentage of a prior move that is "given back" in a counter-trend correction.

**Bullish Trend (Correction Down):**

$$P_{\text{retrace}}(r) = P_{\text{high}} - r \times (P_{\text{high}} - P_{\text{low}})$$

**Bearish Trend (Correction Up):**

$$P_{\text{retrace}}(r) = P_{\text{low}} + r \times (P_{\text{high}} - P_{\text{low}})$$

where $r \in \{0.236, 0.382, 0.500, 0.618, 0.786, 0.886\}$.

### 2.2 Complete Retracement Level Table

| Level | Ratio | Application in EW | Significance |
|---|---|---|---|
| 23.6% | 0.236 | Very shallow retracement | Strong trend; Wave 4 in powerful impulse |
| 38.2% | 0.382 | Moderate retracement | Wave 4 most common level; moderate correction |
| 50.0% | 0.500 | Halfway retracement | Wave 2 common level; significant psychological |
| 61.8% | 0.618 | Deep retracement (Golden Ratio) | Wave 2 most common; deep but healthy correction |
| 78.6% | 0.786 | Very deep retracement | Common in crypto Wave 2; near invalidation |
| 88.6% | 0.886 | Extreme retracement | Rare; often seen in crypto altcoins |
| 100.0% | 1.000 | Full retracement | Invalidation level for Wave 2 |

### 2.3 Retracement Application by Wave

**Wave 2 Retracement (of Wave 1):**

$$P_{\text{W2}} = P_{\text{W1\_end}} - r \times (P_{\text{W1\_end}} - P_{\text{W1\_start}})$$

| Market | Primary Level | Secondary Level | Notes |
|---|---|---|---|
| Forex Majors | 61.8% | 50.0% | Very consistent |
| Forex Crosses | 61.8% | 78.6% | More volatile |
| BTC/USD | 61.8% | 78.6% | Deeper pullbacks |
| Altcoins | 78.6% | 88.6% | Extreme fear-driven |

**Wave 4 Retracement (of Wave 3):**

$$P_{\text{W4}} = P_{\text{W3\_end}} - r \times (P_{\text{W3\_end}} - P_{\text{W3\_start}})$$

| Market | Primary Level | Secondary Level | Notes |
|---|---|---|---|
| Forex Majors | 38.2% | 23.6% | Shallow, sideways |
| Forex Crosses | 38.2% | 50.0% | Slightly deeper |
| BTC/USD | 38.2% | 50.0% | Standard |
| Altcoins | 50.0% | 61.8% | Can be deep |

**Wave B Retracement (of Wave A in corrections):**

| Correction Type | B Retracement of A | Notes |
|---|---|---|
| Zigzag | 38.2%--78.6% | Typically 50%--61.8% |
| Regular Flat | 90%--105% | Near full retrace |
| Expanded Flat | 105%--138.2% | Exceeds A |
| Running Flat | 105%--161.8% | Significantly exceeds A |

### 2.4 Calculation Example

**Example: EUR/USD Wave 1 from 1.0800 to 1.1200 (400 pips)**

$$\text{Range} = 1.1200 - 1.0800 = 0.0400$$

| Level | Calculation | Price |
|---|---|---|
| 23.6% | $1.1200 - 0.236 \times 0.0400$ | 1.1106 |
| 38.2% | $1.1200 - 0.382 \times 0.0400$ | 1.1047 |
| 50.0% | $1.1200 - 0.500 \times 0.0400$ | 1.1000 |
| 61.8% | $1.1200 - 0.618 \times 0.0400$ | 1.0953 |
| 78.6% | $1.1200 - 0.786 \times 0.0400$ | 1.0886 |

---

## 3. Fibonacci Extension Levels

### 3.1 Definition and Calculation

A Fibonacci extension measures how far a wave **extends beyond** the prior wave's range, measured from the end of the corrective wave.

**Formula (Bullish, Wave 3 target from Wave 2 end):**

$$P_{\text{extension}}(e) = P_{\text{W2\_end}} + e \times (P_{\text{W1\_end}} - P_{\text{W1\_start}})$$

**Formula (Bullish, Wave 5 target from Wave 4 end):**

$$P_{\text{extension}}(e) = P_{\text{W4\_end}} + e \times (P_{\text{W1\_end}} - P_{\text{W1\_start}})$$

### 3.2 Complete Extension Level Table

| Level | Ratio | Application in EW | Significance |
|---|---|---|---|
| 61.8% | 0.618 | Wave 5 minimum when Wave 3 extended | Sub-minimal extension |
| 100.0% | 1.000 | Wave 5 = Wave 1; Wave C = Wave A | Equality relationship |
| 127.2% | 1.272 | Moderate extension | Wave 3 minimum when typical |
| 138.2% | 1.382 | Moderate-strong extension | Between key levels |
| 161.8% | 1.618 | Golden extension | Wave 3 most common target |
| 200.0% | 2.000 | Double extension | Strong Wave 3 target |
| 227.2% | 2.272 | Strong extension | Between key levels |
| 261.8% | 2.618 | Major extension | Extended Wave 3; common in crypto |
| 300.0% | 3.000 | Triple extension | Very strong trends |
| 361.8% | 3.618 | Extreme extension | Parabolic moves |
| 423.6% | 4.236 | Maximum common extension | Extreme crypto parabolic |

### 3.3 Extension Application by Wave

**Wave 3 Extensions (measured from Wave 1 range, projected from Wave 2 end):**

| Target Level | Formula | Probability (Forex) | Probability (Crypto) |
|---|---|---|---|
| 100% | $P_{\text{W2}} + 1.000 \times R_1$ | 10% | 5% |
| 127.2% | $P_{\text{W2}} + 1.272 \times R_1$ | 15% | 10% |
| 161.8% | $P_{\text{W2}} + 1.618 \times R_1$ | 35% | 25% |
| 200% | $P_{\text{W2}} + 2.000 \times R_1$ | 20% | 20% |
| 261.8% | $P_{\text{W2}} + 2.618 \times R_1$ | 15% | 20% |
| 423.6% | $P_{\text{W2}} + 4.236 \times R_1$ | 5% | 20% |

**Wave 5 Extensions (measured from Wave 1 range, projected from Wave 4 end):**

| Target Level | Formula | Probability (Forex) | Probability (Crypto) |
|---|---|---|---|
| 38.2% | $P_{\text{W4}} + 0.382 \times R_1$ | 10% | 5% |
| 61.8% | $P_{\text{W4}} + 0.618 \times R_1$ | 25% | 15% |
| 100% | $P_{\text{W4}} + 1.000 \times R_1$ | 35% | 25% |
| 161.8% | $P_{\text{W4}} + 1.618 \times R_1$ | 20% | 30% |
| 261.8% | $P_{\text{W4}} + 2.618 \times R_1$ | 10% | 25% |

**Wave C Extensions (measured from Wave A range):**

| Target Level | Formula | Pattern Context |
|---|---|---|
| 61.8% | $P_B + 0.618 \times R_A$ | Weak C-wave (running flat) |
| 100% | $P_B + 1.000 \times R_A$ | Regular flat, zigzag standard |
| 127.2% | $P_B + 1.272 \times R_A$ | Common in expanded flat |
| 161.8% | $P_B + 1.618 \times R_A$ | Expanded flat, strong zigzag |
| 200% | $P_B + 2.000 \times R_A$ | Extreme correction |
| 261.8% | $P_B + 2.618 \times R_A$ | Rare; panic/euphoria driven |

### 3.4 Calculation Example

**Example: BTC/USD Wave 1 from $25,000 to $35,000; Wave 2 ends at $29,000**

$$R_1 = \$35,000 - \$25,000 = \$10,000$$

| Wave 3 Target | Calculation | Price |
|---|---|---|
| 100% | $\$29,000 + 1.000 \times \$10,000$ | $39,000 |
| 161.8% | $\$29,000 + 1.618 \times \$10,000$ | $45,180 |
| 200% | $\$29,000 + 2.000 \times \$10,000$ | $49,000 |
| 261.8% | $\$29,000 + 2.618 \times \$10,000$ | $55,180 |
| 423.6% | $\$29,000 + 4.236 \times \$10,000$ | $71,360 |

---

## 4. Fibonacci Projection (Measured Move)

### 4.1 Definition

Fibonacci projection (also called "external retracement" or "measured move") projects the length of one wave from the endpoint of another wave. It differs from extensions in that it uses a **three-point** measurement.

### 4.2 Three-Point Calculation

**Formula (Bullish, projecting Wave 1 range from Wave 2 end):**

$$P_{\text{projection}}(p) = P_{\text{W2\_end}} + p \times (P_{\text{W1\_end}} - P_{\text{W1\_start}})$$

This is mathematically identical to the extension formula but conceptually different: we are projecting a known wave's range from a new starting point.

### 4.3 Alternative Projection: Wave 1-to-3 Net

A powerful projection for Wave 5:

$$P_{\text{W5\_proj}}(p) = P_{\text{W4\_end}} + p \times (P_{\text{W3\_end}} - P_{\text{W1\_start}})$$

This projects the entire net progress of Waves 1 through 3 from Wave 4's end, at Fibonacci ratios.

| Ratio | Common Use |
|---|---|
| 0.382 | Conservative Wave 5 target |
| 0.500 | Moderate Wave 5 target |
| 0.618 | Standard Wave 5 target (most common) |
| 1.000 | Extended Wave 5 target |

### 4.4 A-B Projection for Wave C

$$P_{\text{C\_target}}(p) = P_B + p \times (P_A - P_{\text{start}})$$

| Ratio | Pattern |
|---|---|
| 0.618 | Weak C-wave |
| 1.000 | Standard zigzag/flat |
| 1.272 | Strong C-wave |
| 1.618 | Extended C-wave |

---

## 5. Fibonacci Time Zones

### 5.1 Concept

Fibonacci time zones apply the same Fibonacci ratios to the **time axis**, identifying dates/bars when significant price events (wave completions, reversals) are more likely to occur.

### 5.2 Time Ratio Calculation

**Method 1: Time ratio between waves**

$$T_n = r \times T_{\text{reference}}$$

where $T_{\text{reference}}$ is the duration (in bars) of a reference wave and $r$ is a Fibonacci ratio.

**Method 2: Fibonacci time zones from a starting point**

Project vertical lines at Fibonacci numbers of bars from a significant pivot:

$$t_n = t_{\text{pivot}} + F_n \times \text{bar\_period}$$

where $F_n \in \{1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, ...\}$

### 5.3 Time Relationships Between Waves

| Relationship | Typical Ratio | Notes |
|---|---|---|
| $T_2 / T_1$ | 0.382--0.618 | Wave 2 often shorter than Wave 1 |
| $T_3 / T_1$ | 1.000--1.618 | Wave 3 equal to or longer than Wave 1 |
| $T_4 / T_2$ | 1.000--2.618 | Wave 4 often longer than Wave 2 (alternation) |
| $T_5 / T_1$ | 0.618--1.000 | Wave 5 roughly equal to Wave 1 in time |
| $T_{\text{correction}} / T_{\text{impulse}}$ | 0.382--0.618 | Corrections typically 38.2%--61.8% of impulse duration |

### 5.4 Time/Price Confluence

The highest probability reversal zones occur when both **price** and **time** Fibonacci levels converge:

$$\text{Confluence Score} = w_p \times F_{\text{price}} + w_t \times F_{\text{time}}$$

where $w_p = 0.70$ (price weight) and $w_t = 0.30$ (time weight).

**Price is more reliable than time** in Elliott Wave analysis, but time adds significant confirmation.

### 5.5 Time Zone Implementation

```python
def calculate_fibonacci_time_zones(pivot_time, reference_duration, direction='forward'):
    """
    Calculate Fibonacci time zones from a pivot point.
    
    Parameters:
        pivot_time: datetime of the reference pivot
        reference_duration: duration of the reference wave in bars
        direction: 'forward' or 'backward'
    
    Returns:
        List of (time, fib_number, significance) tuples
    """
    fib_numbers = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]
    fib_ratios = [0.382, 0.500, 0.618, 1.000, 1.272, 1.618, 2.000, 2.618]
    
    time_zones = []
    
    # Method 1: Fibonacci numbers as bar counts
    for f in fib_numbers:
        target_time = pivot_time + f * bar_period
        time_zones.append({
            'time': target_time,
            'method': 'fib_number',
            'value': f,
            'significance': 'high' if f in [8, 13, 21, 34, 55] else 'moderate'
        })
    
    # Method 2: Fibonacci ratios of reference duration
    for r in fib_ratios:
        target_bars = int(reference_duration * r)
        target_time = pivot_time + target_bars * bar_period
        time_zones.append({
            'time': target_time,
            'method': 'fib_ratio',
            'value': r,
            'significance': 'high' if r in [0.618, 1.000, 1.618] else 'moderate'
        })
    
    return sorted(time_zones, key=lambda x: x['time'])
```

---

## 6. Fibonacci Cluster Analysis

### 6.1 Concept

A **Fibonacci cluster** (also called Fibonacci confluence zone) occurs when multiple independent Fibonacci measurements from different reference waves converge at approximately the same price level. These clusters represent high-probability reversal zones.

### 6.2 Why Clusters Work

1. Each Fibonacci level alone has moderate probability of producing a reaction
2. When multiple Fibonacci levels from different measurements converge, the probability of a significant price reaction increases multiplicatively
3. Clusters represent zones where multiple wave relationships simultaneously reach completion

### 6.3 Sources of Fibonacci Levels for Clustering

To build a comprehensive Fibonacci cluster map, calculate levels from **all available reference waves**:

| Source | Measurement Type | Levels to Calculate |
|---|---|---|
| Wave 1 range | Extension from Wave 2 end | 100%, 127.2%, 161.8%, 200%, 261.8% |
| Wave 1 range | Retracement for Wave 2 | 38.2%, 50%, 61.8%, 78.6% |
| Wave 3 range | Retracement for Wave 4 | 23.6%, 38.2%, 50%, 61.8% |
| Wave 1-to-3 net | Projection from Wave 4 | 38.2%, 50%, 61.8%, 100% |
| Wave A range | Extension from Wave B | 100%, 127.2%, 161.8% |
| Prior impulse range | Retracement for correction | 38.2%, 50%, 61.8%, 78.6% |
| Higher TF waves | Extension/Retracement | All standard levels |
| Sub-wave relationships | Internal Fibonacci | Various |

### 6.4 Cluster Density Calculation

**Method: Gaussian Kernel Density**

For a set of $n$ Fibonacci levels $\{F_1, F_2, ..., F_n\}$, the cluster density at price $p$ is:

$$D(p) = \sum_{i=1}^{n} \frac{w_i}{\sigma_i \sqrt{2\pi}} \exp\left(-\frac{(p - F_i)^2}{2\sigma_i^2}\right)$$

where:
- $w_i$ = weight of the $i$-th Fibonacci level (based on reliability)
- $\sigma_i$ = tolerance/bandwidth for the $i$-th level

**Simplified discrete method:**

$$D(p) = \sum_{i=1}^{n} w_i \cdot \mathbb{1}_{[|p - F_i| < \epsilon]}$$

where $\epsilon$ is the tolerance (e.g., 0.5% of price) and $\mathbb{1}$ is the indicator function.

### 6.5 Cluster Significance Scoring

| Number of Levels in Cluster | Significance | Action |
|---|---|---|
| 1 | Low | Note but do not act alone |
| 2 | Moderate | Monitor for confirmation |
| 3 | High | Prepare for entry |
| 4 | Very High | High-confidence trade setup |
| 5+ | Extreme | Maximum confidence zone |

### 6.6 Weighted Cluster Score

$$S_{\text{cluster}} = \sum_{i \in \text{cluster}} w_i \times R_i$$

where $R_i$ is the historical reliability score of each Fibonacci relationship:

| Fibonacci Relationship | Reliability $R_i$ |
|---|---|
| Wave 3 = 161.8% of Wave 1 | 0.90 |
| Wave 2 = 61.8% of Wave 1 | 0.85 |
| Wave 4 = 38.2% of Wave 3 | 0.80 |
| Wave C = 100% of Wave A | 0.75 |
| Wave 5 = 100% of Wave 1 | 0.75 |
| Wave 5 = 61.8% of W1-W3 net | 0.70 |
| Higher TF retracement | 0.85 |
| Time zone confluence | 0.50 |

### 6.7 Implementation

```python
def calculate_fibonacci_clusters(wave_data, current_price, tolerance_pct=0.005):
    """
    Calculate Fibonacci cluster zones from all available wave measurements.
    
    Parameters:
        wave_data: Dictionary containing all identified waves with prices
        current_price: Current market price
        tolerance_pct: Tolerance for clustering (default 0.5% of price)
    
    Returns:
        List of cluster zones ranked by significance
    """
    all_levels = []
    tolerance = current_price * tolerance_pct
    
    # Generate all Fibonacci levels from all available waves
    if 'wave_1' in wave_data:
        w1_range = abs(wave_data['wave_1']['end'] - wave_data['wave_1']['start'])
        w2_end = wave_data.get('wave_2', {}).get('end')
        
        if w2_end:
            # Wave 3 extension targets
            for ratio, weight in [(1.000, 0.7), (1.272, 0.8), (1.618, 0.9), 
                                   (2.000, 0.8), (2.618, 0.7), (4.236, 0.5)]:
                level = w2_end + ratio * w1_range
                all_levels.append({
                    'price': level,
                    'source': f'W3_ext_{ratio}',
                    'weight': weight,
                    'type': 'extension'
                })
    
    if 'wave_3' in wave_data:
        w3_range = abs(wave_data['wave_3']['end'] - wave_data['wave_3']['start'])
        w3_end = wave_data['wave_3']['end']
        
        # Wave 4 retracement targets
        for ratio, weight in [(0.236, 0.7), (0.382, 0.9), (0.500, 0.8), (0.618, 0.7)]:
            level = w3_end - ratio * w3_range
            all_levels.append({
                'price': level,
                'source': f'W4_ret_{ratio}',
                'weight': weight,
                'type': 'retracement'
            })
    
    if 'wave_1' in wave_data and 'wave_3' in wave_data and 'wave_4' in wave_data:
        w1_start = wave_data['wave_1']['start']
        w3_end = wave_data['wave_3']['end']
        w4_end = wave_data['wave_4']['end']
        net_1_to_3 = abs(w3_end - w1_start)
        
        # Wave 5 projection targets
        for ratio, weight in [(0.382, 0.7), (0.618, 0.85), (1.000, 0.8)]:
            level = w4_end + ratio * net_1_to_3
            all_levels.append({
                'price': level,
                'source': f'W5_proj_{ratio}',
                'weight': weight,
                'type': 'projection'
            })
    
    # Higher timeframe levels
    if 'htf_impulse' in wave_data:
        htf_range = abs(wave_data['htf_impulse']['end'] - wave_data['htf_impulse']['start'])
        htf_end = wave_data['htf_impulse']['end']
        
        for ratio, weight in [(0.382, 0.85), (0.500, 0.80), (0.618, 0.90), (0.786, 0.75)]:
            level = htf_end - ratio * htf_range
            all_levels.append({
                'price': level,
                'source': f'HTF_ret_{ratio}',
                'weight': weight,
                'type': 'htf_retracement'
            })
    
    # Cluster identification
    all_levels.sort(key=lambda x: x['price'])
    clusters = []
    used = set()
    
    for i, level in enumerate(all_levels):
        if i in used:
            continue
        
        cluster = [level]
        used.add(i)
        
        for j, other_level in enumerate(all_levels):
            if j in used or j == i:
                continue
            if abs(level['price'] - other_level['price']) <= tolerance:
                cluster.append(other_level)
                used.add(j)
        
        if len(cluster) >= 2:  # At least 2 levels for a cluster
            avg_price = sum(l['price'] for l in cluster) / len(cluster)
            total_weight = sum(l['weight'] for l in cluster)
            
            clusters.append({
                'price': avg_price,
                'num_levels': len(cluster),
                'total_weight': total_weight,
                'sources': [l['source'] for l in cluster],
                'significance': categorize_significance(len(cluster), total_weight),
            })
    
    # Sort by significance (weighted by number of levels and total weight)
    clusters.sort(key=lambda x: x['total_weight'], reverse=True)
    
    return clusters


def categorize_significance(num_levels, total_weight):
    """Categorize cluster significance."""
    if num_levels >= 5 or total_weight >= 4.0:
        return 'extreme'
    elif num_levels >= 4 or total_weight >= 3.0:
        return 'very_high'
    elif num_levels >= 3 or total_weight >= 2.5:
        return 'high'
    elif num_levels >= 2 or total_weight >= 1.5:
        return 'moderate'
    else:
        return 'low'
```

---

## 7. Price Targets for Each Wave

### 7.1 Wave 1 Targets

Wave 1 has no prior wave within the current impulse to measure from. However, targets can be derived from:

**From the prior correction:**
$$P_{\text{W1\_target}} = P_{\text{correction\_end}} + r \times R_{\text{last\_impulse\_of\_prior\_trend}}$$

where $r \in \{0.382, 0.500, 0.618\}$ (Wave 1 is typically 38.2%--61.8% of the prior impulse in the opposite direction).

**From the prior Wave 5 or Wave C:**
$$P_{\text{W1\_target}} = P_{\text{prior\_5\_start}} \quad \text{(equal to prior Wave 4 end)}$$

### 7.2 Wave 2 Targets

$$P_{\text{W2}} = P_{\text{W1\_end}} - r \times R_1$$

| Fibonacci Level | Priority | Market |
|---|---|---|
| 50.0% | Primary target | Forex |
| 61.8% | Primary target | Forex/Crypto |
| 78.6% | Secondary target | Crypto |
| 38.2% | Secondary target | Strong trends |

**Invalidation:** $P_{\text{W2}} < P_{\text{W1\_start}}$ (Wave 2 > 100% of Wave 1)

### 7.3 Wave 3 Targets

**Method 1: Extension of Wave 1 from Wave 2 end**

$$P_{\text{W3}} = P_{\text{W2\_end}} + e \times R_1$$

| Extension | Priority | Probability |
|---|---|---|
| 161.8% | Primary | 35% (Forex), 25% (Crypto) |
| 200.0% | Secondary | 20% (both) |
| 261.8% | Tertiary | 15% (Forex), 20% (Crypto) |
| 423.6% | Extreme | 5% (Forex), 20% (Crypto) |

**Method 2: Using sub-wave structure**

Once Wave 3 begins and sub-wave i of Wave 3 is complete:

$$P_{\text{W3}} = P_{\text{W3\_start}} + \frac{R_{\text{sub\_i}}}{0.236} \approx 4.236 \times R_{\text{sub\_i}} + P_{\text{W3\_start}}$$

(If sub-wave i is approximately 23.6% of the total Wave 3 range)

### 7.4 Wave 4 Targets

$$P_{\text{W4}} = P_{\text{W3\_end}} - r \times R_3$$

| Fibonacci Level | Priority | Pattern Expected |
|---|---|---|
| 23.6% | Primary (strong trend) | Flat or shallow triangle |
| 38.2% | Primary (most common) | Flat, triangle, or combination |
| 50.0% | Secondary | Deep flat or zigzag |
| Sub-wave iv of W3 | High priority alternative | Common support/resistance |

**Non-overlap constraint:**
$$P_{\text{W4\_min}} > P_{\text{W1\_end}} \quad \text{(bullish impulse)}$$

### 7.5 Wave 5 Targets

**Method 1: Wave 5 = Ratio x Wave 1 (from Wave 4 end)**

$$P_{\text{W5}} = P_{\text{W4\_end}} + e \times R_1$$

| Extension | Priority | Condition |
|---|---|---|
| 61.8% | Primary (W3 extended) | When Wave 3 > 161.8% of Wave 1 |
| 100.0% | Primary (equality) | Most common overall |
| 161.8% | Secondary (extended W5) | Common in crypto |

**Method 2: Wave 5 = 61.8% of (Wave 1-to-3 net)**

$$P_{\text{W5}} = P_{\text{W4\_end}} + 0.618 \times (P_{\text{W3\_end}} - P_{\text{W1\_start}})$$

**Method 3: Channel-based target**

Draw a trendline from Wave 2 end through Wave 4 end. Project a parallel from Wave 3 end. Wave 5 typically reaches or approaches this upper parallel.

**Rule 2 constraint (if Wave 1 > Wave 3):**
$$P_{\text{W5\_max}} = P_{\text{W4\_end}} + R_3$$

(Wave 5 cannot exceed Wave 3 range, or Wave 3 becomes the shortest)

### 7.6 Wave A Targets (After Impulse Completion)

$$P_A = P_{\text{W5\_end}} - r \times R_{\text{impulse}}$$

where $R_{\text{impulse}} = |P_{\text{W5\_end}} - P_{\text{W1\_start}}|$

| Level | Priority |
|---|---|
| 38.2% | Primary (moderate correction expected) |
| 50.0% | Secondary |
| Wave 4 territory | High priority (prior support becomes target) |

### 7.7 Wave C Targets

$$P_C = P_B + e \times R_A$$

| Extension | Pattern Type |
|---|---|
| 61.8% | Running flat C-wave |
| 100.0% | Standard zigzag or regular flat |
| 127.2% | Expanded flat |
| 161.8% | Strong correction or expanded flat |
| 261.8% | Extreme correction (crash scenario) |

---

## 8. Mathematical Models and Formulas

### 8.1 Unified Price Target Formula

For any wave $n$ with reference wave $m$:

$$P_{\text{target}}^{(n)} = P_{\text{base}} + \text{sign} \times \phi^k \times R_m$$

where:
- $P_{\text{base}}$ = starting point for measurement (typically end of preceding wave)
- $\text{sign} = +1$ (bullish) or $-1$ (bearish)
- $\phi^k$ = Fibonacci ratio ($k \in \{-3, -2, -1, 0, 1, 2, 3\}$)
- $R_m$ = range of reference wave $m$

### 8.2 Fibonacci Ratio Hierarchy

$$..., \phi^{-3}, \phi^{-2}, \phi^{-1}, \phi^0, \phi^1, \phi^2, \phi^3, ...$$

$$= ..., 0.236, 0.382, 0.618, 1.000, 1.618, 2.618, 4.236, ...$$

### 8.3 Multi-Fibonacci Target Probability

When $n$ independent Fibonacci levels cluster at price $p$:

$$P(\text{reversal at } p) = 1 - \prod_{i=1}^{n} (1 - p_i)$$

where $p_i$ is the individual probability of reversal at the $i$-th Fibonacci level.

**Example:** Three Fibonacci levels converge, each with 30% individual probability:

$$P = 1 - (1 - 0.30)^3 = 1 - 0.343 = 0.657 = 65.7\%$$

### 8.4 Optimal Target Selection

For multiple possible targets $\{T_1, T_2, ..., T_k\}$ with probabilities $\{p_1, p_2, ..., p_k\}$:

**Expected Value Approach:**

$$EV_i = p_i \times (T_i - P_{\text{entry}}) - (1 - p_i) \times (P_{\text{entry}} - P_{\text{SL}})$$

Select the target $T^*$ that maximizes $EV_i$:

$$T^* = \arg\max_i EV_i$$

**Kelly Criterion for Position Sizing:**

$$f^* = \frac{p \cdot b - q}{b}$$

where $b = \frac{T_i - P_{\text{entry}}}{P_{\text{entry}} - P_{\text{SL}}}$ (the reward-to-risk ratio), $p$ = win probability, $q = 1-p$.

### 8.5 Price Target Adjustment for Volatility

In high-volatility environments (crypto, GBP pairs during news), targets should be adjusted:

$$T_{\text{adjusted}} = T_{\text{base}} \times (1 + \alpha \times \frac{\sigma_{\text{current}} - \sigma_{\text{avg}}}{\sigma_{\text{avg}}})$$

where:
- $\sigma_{\text{current}}$ = current ATR or standard deviation
- $\sigma_{\text{avg}}$ = average ATR over lookback period
- $\alpha$ = adjustment factor (typically 0.2--0.5)

### 8.6 Time-Price Square

Combine time and price Fibonacci for a "square" analysis:

$$S(p, t) = w_p \cdot D_{\text{price}}(p) + w_t \cdot D_{\text{time}}(t)$$

where $D_{\text{price}}(p)$ and $D_{\text{time}}(t)$ are the density functions for price and time clusters respectively.

The point $(p^*, t^*)$ that maximizes $S(p, t)$ is the highest-probability reversal zone in both price and time.

---

## 9. Algorithm for High-Probability Reversal Zones

### 9.1 Complete Algorithm

```python
def find_high_probability_reversal_zones(wave_data, market_data, config):
    """
    Master algorithm to identify high-probability price reversal zones
    using Fibonacci cluster analysis combined with Elliott Wave structure.
    
    Returns ranked list of reversal zones with confidence scores.
    """
    
    # Step 1: Calculate all Fibonacci levels from all available wave measurements
    fib_levels = calculate_all_fibonacci_levels(wave_data)
    
    # Step 2: Add higher timeframe levels
    htf_levels = calculate_htf_fibonacci_levels(wave_data['htf'])
    fib_levels.extend(htf_levels)
    
    # Step 3: Add structural levels (prior Wave 4 zones, prior consolidation)
    structural_levels = identify_structural_levels(wave_data, market_data)
    
    # Step 4: Calculate Fibonacci time zones
    time_zones = calculate_fibonacci_time_zones(wave_data)
    
    # Step 5: Build cluster map
    price_tolerance = market_data['atr'] * config['cluster_tolerance_atr']
    clusters = identify_clusters(fib_levels, price_tolerance)
    
    # Step 6: Score each cluster
    scored_zones = []
    for cluster in clusters:
        score = calculate_zone_score(cluster, structural_levels, time_zones, market_data)
        scored_zones.append({
            'price_center': cluster['avg_price'],
            'price_range': (cluster['min_price'], cluster['max_price']),
            'num_levels': cluster['num_levels'],
            'sources': cluster['sources'],
            'score': score,
            'time_alignment': check_time_alignment(cluster, time_zones),
            'structural_alignment': check_structural_alignment(cluster, structural_levels),
        })
    
    # Step 7: Filter and rank
    valid_zones = [z for z in scored_zones if z['score'] >= config['min_zone_score']]
    valid_zones.sort(key=lambda x: x['score'], reverse=True)
    
    return valid_zones[:config['max_zones_returned']]


def calculate_zone_score(cluster, structural_levels, time_zones, market_data):
    """
    Calculate a composite score for a Fibonacci cluster zone.
    """
    score = 0.0
    
    # Base score from number of Fibonacci levels
    level_score = min(cluster['num_levels'] / 5.0, 1.0)  # Normalize to 0-1
    score += 0.30 * level_score
    
    # Weight score from level reliability
    weight_score = min(cluster['total_weight'] / 4.0, 1.0)
    score += 0.25 * weight_score
    
    # Structural alignment (prior S/R, Wave 4 zones)
    struct_match = any(
        abs(cluster['avg_price'] - s['price']) <= market_data['atr'] * 0.5
        for s in structural_levels
    )
    score += 0.20 * (1.0 if struct_match else 0.0)
    
    # Time zone alignment
    time_match = any(
        abs(market_data['current_bar'] - tz['bar']) <= 3
        for tz in time_zones
    )
    score += 0.10 * (1.0 if time_match else 0.0)
    
    # Proximity to current price (zones near current price are more actionable)
    distance = abs(cluster['avg_price'] - market_data['current_price'])
    proximity_score = max(0, 1.0 - distance / (market_data['atr'] * 10))
    score += 0.10 * proximity_score
    
    # Higher timeframe alignment bonus
    htf_match = any('HTF' in s for s in cluster['sources'])
    score += 0.05 * (1.0 if htf_match else 0.0)
    
    return score
```

### 9.2 Reversal Zone Validation

Once a potential reversal zone is identified, validate with:

```python
def validate_reversal_zone(zone, market_data, indicators):
    """
    Validate that a Fibonacci cluster zone is likely to produce a reversal.
    
    Returns: (is_valid, confidence, recommended_action)
    """
    validations = {}
    
    # 1. Price has reached the zone
    in_zone = zone['price_range'][0] <= market_data['price'] <= zone['price_range'][1]
    validations['price_in_zone'] = in_zone
    
    # 2. Momentum divergence present
    if zone['expected_direction'] == 'reversal_up':
        validations['momentum_divergence'] = check_bullish_divergence(
            indicators['rsi'], indicators['price']
        )
    else:
        validations['momentum_divergence'] = check_bearish_divergence(
            indicators['rsi'], indicators['price']
        )
    
    # 3. Volume pattern (climax or exhaustion)
    validations['volume_signal'] = (
        check_volume_climax(indicators['volume']) or 
        check_volume_exhaustion(indicators['volume'])
    )
    
    # 4. Candlestick reversal pattern
    validations['reversal_candle'] = check_reversal_candlestick(
        market_data['candles'][-3:], zone['expected_direction']
    )
    
    # 5. Lower timeframe structure (new impulse beginning)
    validations['ltf_impulse'] = check_ltf_impulse_start(
        market_data['ltf_data'], zone['expected_direction']
    )
    
    # Calculate confidence
    confidence = sum(validations.values()) / len(validations)
    
    is_valid = confidence >= 0.60 and validations['price_in_zone']
    
    recommended_action = None
    if is_valid:
        if confidence >= 0.80:
            recommended_action = 'ENTER_FULL_SIZE'
        elif confidence >= 0.70:
            recommended_action = 'ENTER_HALF_SIZE'
        else:
            recommended_action = 'ENTER_QUARTER_SIZE_WITH_ADD'
    
    return is_valid, confidence, recommended_action
```

---

## 10. Core Logic --- Entry/Exit Based on Fibonacci Targets

### 10.1 Entry Strategy: Fibonacci Cluster Entry

```
┌─────────────────────────────────────────────────────────────────┐
│  FIBONACCI CLUSTER ENTRY STRATEGY                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PRE-CONDITIONS:                                                 │
│    1. Clear Elliott Wave count established (confidence >= 0.65)  │
│    2. Fibonacci cluster identified with >= 3 converging levels   │
│    3. Price approaching or within cluster zone                   │
│                                                                  │
│  ENTRY TRIGGERS (need >= 2):                                     │
│    □ Price reaches cluster zone center +/- tolerance             │
│    □ Momentum divergence at zone (RSI/MACD)                      │
│    □ Reversal candlestick pattern within zone                    │
│    □ Volume climax or exhaustion at zone                         │
│    □ Lower timeframe shows new impulse beginning                 │
│                                                                  │
│  ENTRY EXECUTION:                                                │
│    • Limit order at cluster center                               │
│    • OR market order on confirmation candle close                 │
│                                                                  │
│  STOP LOSS:                                                      │
│    Beyond the next Fibonacci cluster or invalidation level       │
│    Minimum: 1.5 x ATR(14) beyond zone edge                      │
│                                                                  │
│  TAKE PROFIT (scaled):                                           │
│    TP1 (40%): Next minor Fibonacci level in trend direction      │
│    TP2 (35%): Wave target (e.g., Wave 3 at 161.8% extension)    │
│    TP3 (25%): Extended target (trailing stop to lock profits)    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 Exit Strategy: Fibonacci Target Exit

```
┌─────────────────────────────────────────────────────────────────┐
│  FIBONACCI TARGET EXIT STRATEGY                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PARTIAL EXIT TRIGGERS:                                          │
│    TP1: Price reaches first Fibonacci cluster in trend direction │
│         Action: Close 40% of position, move SL to breakeven     │
│                                                                  │
│    TP2: Price reaches second Fibonacci cluster                   │
│         Action: Close 35% of position, trail SL to TP1 level    │
│                                                                  │
│    TP3: Price reaches third Fibonacci cluster OR                 │
│         Shows exhaustion signals (divergence, volume decline)    │
│         Action: Close remaining 25%                              │
│                                                                  │
│  FULL EXIT TRIGGERS:                                             │
│    • Wave count invalidation (Iron Rule violated)                │
│    • Price breaks back through entry cluster in wrong direction  │
│    • Confidence score drops below 0.50                           │
│    • Time-based: no progress toward target within expected time  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 10.3 Fibonacci-Based Trailing Stop

```python
def calculate_fibonacci_trailing_stop(entry_price, current_price, direction, atr):
    """
    Calculate trailing stop using Fibonacci levels of the current profit.
    
    The stop trails at 38.2% of the total unrealized profit.
    """
    if direction == 'long':
        profit = current_price - entry_price
        if profit <= 0:
            return entry_price - 1.5 * atr  # Initial stop
        
        # Trail at 38.2% retracement of profit
        trailing_stop = current_price - 0.382 * profit
        
        # Minimum: breakeven after 2:1 profit reached
        if profit >= 2 * atr:
            trailing_stop = max(trailing_stop, entry_price)
        
        return trailing_stop
    
    else:  # short
        profit = entry_price - current_price
        if profit <= 0:
            return entry_price + 1.5 * atr
        
        trailing_stop = current_price + 0.382 * profit
        
        if profit >= 2 * atr:
            trailing_stop = min(trailing_stop, entry_price)
        
        return trailing_stop
```

---

## 11. Technical Specifications

### 11.1 Fibonacci Calculation Parameters

```python
FIBONACCI_CONFIG = {
    # Core ratios
    'retracement_levels': [0.236, 0.382, 0.500, 0.618, 0.786, 0.886],
    'extension_levels': [0.618, 1.000, 1.272, 1.382, 1.618, 2.000, 2.618, 4.236],
    'projection_levels': [0.382, 0.500, 0.618, 1.000, 1.272, 1.618],
    
    # Cluster parameters
    'cluster_tolerance_pct': 0.005,     # 0.5% price tolerance for clustering
    'cluster_tolerance_atr': 0.5,       # Alternative: 0.5 x ATR
    'min_levels_for_cluster': 2,        # Minimum 2 levels for a valid cluster
    'max_zones_returned': 5,            # Return top 5 zones
    'min_zone_score': 0.50,             # Minimum score threshold
    
    # Weight assignments
    'weights': {
        'wave_3_161': 0.90,             # Wave 3 = 161.8% of Wave 1
        'wave_2_618': 0.85,             # Wave 2 = 61.8% retracement
        'wave_4_382': 0.80,             # Wave 4 = 38.2% retracement
        'wave_c_100': 0.75,             # Wave C = Wave A
        'wave_5_100_w1': 0.75,          # Wave 5 = Wave 1
        'wave_5_618_net': 0.70,         # Wave 5 = 61.8% of W1-W3
        'htf_level': 0.85,             # Higher timeframe level
        'structural': 0.70,             # Prior S/R zone
    },
    
    # Time zone parameters
    'time_fib_numbers': [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144],
    'time_fib_ratios': [0.382, 0.500, 0.618, 1.000, 1.618, 2.618],
    'time_tolerance_bars': 3,           # +/- 3 bars for time zone match
    
    # Market-specific adjustments
    'forex_majors': {
        'primary_retracement': [0.500, 0.618],
        'primary_extension': [1.618, 2.000],
        'cluster_tolerance_pct': 0.003,  # Tighter for less volatile
    },
    'crypto_btc': {
        'primary_retracement': [0.618, 0.786],
        'primary_extension': [2.000, 2.618, 4.236],
        'cluster_tolerance_pct': 0.008,  # Wider for more volatile
    },
    'crypto_alts': {
        'primary_retracement': [0.786, 0.886],
        'primary_extension': [2.618, 4.236],
        'cluster_tolerance_pct': 0.012,  # Widest for highest volatility
    },
}
```

### 11.2 Data Requirements

| Requirement | Specification |
|---|---|
| Minimum bars for Wave 1 identification | 20 bars |
| Minimum bars for Fibonacci calculation | Wave must span >= 5 bars |
| Price precision | 5 decimal places (Forex), 2 (Crypto >$1), 8 (Crypto <$1) |
| Timeframes needed | Current + 1 higher + 1 lower (minimum) |
| Update frequency | Every new bar close + real-time at significant pivots |

---

## 12. Risk Parameters

### 12.1 Stop Loss Based on Fibonacci

**Principle:** Stop loss should be placed beyond the next significant Fibonacci level that would invalidate the trade thesis.

| Entry Type | Stop Loss Placement | Calculation |
|---|---|---|
| Wave 2 entry (long) | Below Wave 1 origin | $SL = P_{\text{W1\_start}} - 0.5 \times ATR$ |
| Wave 4 entry (long) | Below Wave 1 terminus | $SL = P_{\text{W1\_end}} - 0.5 \times ATR$ |
| Wave C entry (long) | Below 78.6% or 88.6% of prior impulse | $SL = P_{\text{W5}} - 0.886 \times R_{\text{impulse}}$ |
| Cluster zone entry | Beyond the next cluster zone | $SL = \text{next\_cluster\_center} - ATR$ |
| Wave 5 reversal (short) | Above 161.8% ext of Wave 1 from Wave 4 | $SL = P_{\text{W4}} + 1.618 \times R_1 + ATR$ |

### 12.2 Risk-to-Reward from Fibonacci

$$RR = \frac{|P_{\text{target}} - P_{\text{entry}}|}{|P_{\text{entry}} - P_{\text{SL}}|}$$

**Minimum acceptable RR by setup:**

| Setup Type | Minimum RR | Rationale |
|---|---|---|
| High-confidence cluster (4+ levels) | 2.0 | Good probability justifies lower RR |
| Moderate cluster (3 levels) | 2.5 | Standard |
| Low-confidence cluster (2 levels) | 3.0 | Need higher RR to compensate |
| Counter-trend entry | 3.0 | Higher risk requires higher reward |
| Trend continuation | 2.0 | Lower risk allows lower threshold |

### 12.3 Position Size by Cluster Confidence

$$\text{Position Size} = \frac{\text{Account} \times R_{\text{base}} \times C_{\text{cluster}}}{\text{SL Distance} \times \text{Point Value}}$$

where:

| Cluster Score | $C_{\text{cluster}}$ | Effect |
|---|---|---|
| Extreme (5+ levels) | 1.00 | Full risk allocation |
| Very High (4 levels) | 0.85 | 85% of standard risk |
| High (3 levels) | 0.70 | 70% of standard risk |
| Moderate (2 levels) | 0.50 | Half of standard risk |

### 12.4 Maximum Fibonacci-Based Exposure

Never risk more than **2% of account** on any single Fibonacci cluster trade, regardless of confidence:

$$R_{\text{max}} = 0.02 \times \text{Account Balance}$$

---

## 13. Execution Flow

### 13.1 Complete Fibonacci Target Analysis Pipeline

```
FUNCTION fibonacci_target_analysis(wave_data, market_data, config):

    // Phase 1: Calculate all Fibonacci levels
    retracement_levels = calculate_retracements(wave_data)
    extension_levels = calculate_extensions(wave_data)
    projection_levels = calculate_projections(wave_data)
    htf_levels = calculate_htf_levels(wave_data.higher_timeframe)
    time_zones = calculate_time_zones(wave_data)
    
    all_levels = MERGE(retracement_levels, extension_levels, 
                       projection_levels, htf_levels)
    
    // Phase 2: Build cluster map
    clusters = identify_clusters(all_levels, config.tolerance)
    
    // Phase 3: Score and rank clusters
    FOR EACH cluster IN clusters:
        cluster.score = calculate_cluster_score(cluster, wave_data, market_data)
        cluster.time_alignment = check_time_alignment(cluster, time_zones)
        cluster.structural_support = check_structural_levels(cluster, market_data)
    
    ranked_clusters = SORT(clusters, BY score, DESCENDING)
    top_clusters = ranked_clusters[:config.max_zones]
    
    // Phase 4: Generate trade setups for actionable clusters
    trade_setups = []
    
    FOR EACH cluster IN top_clusters:
        IF cluster.score >= config.min_score:
            IF is_price_approaching(market_data.price, cluster, direction):
                setup = generate_trade_setup(cluster, wave_data, market_data)
                trade_setups.APPEND(setup)
    
    // Phase 5: Validate and filter
    valid_setups = []
    FOR EACH setup IN trade_setups:
        IF validate_rr_ratio(setup, config.min_rr):
            IF validate_risk_limits(setup, account):
                valid_setups.APPEND(setup)
    
    RETURN valid_setups


FUNCTION generate_trade_setup(cluster, wave_data, market_data):
    
    // Determine direction based on wave context
    IF cluster is a RETRACEMENT target (Wave 2, Wave 4, correction end):
        direction = wave_data.main_trend_direction  // Trade WITH trend
    ELIF cluster is an EXTENSION target (Wave 3 end, Wave 5 end):
        direction = OPPOSITE(wave_data.main_trend_direction)  // Reversal
    
    // Calculate entry
    entry_price = cluster.center_price
    
    // Calculate stop loss (next cluster or invalidation)
    IF direction == LONG:
        sl_candidates = [c.price for c in clusters if c.price < cluster.price]
        stop_loss = max(sl_candidates) - config.atr_buffer * market_data.atr
        IF stop_loss > wave_invalidation_level:
            stop_loss = wave_invalidation_level - config.atr_buffer * market_data.atr
    ELSE:
        sl_candidates = [c.price for c in clusters if c.price > cluster.price]
        stop_loss = min(sl_candidates) + config.atr_buffer * market_data.atr
    
    // Calculate take profits (next clusters in trend direction)
    tp_candidates = [c for c in ranked_clusters 
                     if (c.price > entry_price if direction == LONG else c.price < entry_price)]
    
    tp1 = tp_candidates[0].price if len(tp_candidates) > 0 else None
    tp2 = tp_candidates[1].price if len(tp_candidates) > 1 else None
    tp3 = tp_candidates[2].price if len(tp_candidates) > 2 else None
    
    // Calculate RR ratio
    sl_distance = abs(entry_price - stop_loss)
    tp1_distance = abs(tp1 - entry_price) if tp1 else 0
    rr_ratio = tp1_distance / sl_distance if sl_distance > 0 else 0
    
    RETURN TradeSetup(
        direction=direction,
        entry=entry_price,
        stop_loss=stop_loss,
        take_profits=[tp1, tp2, tp3],
        rr_ratio=rr_ratio,
        confidence=cluster.score,
        cluster_details=cluster
    )
```

### 13.2 Real-Time Monitoring

```
FUNCTION monitor_fibonacci_zones(active_zones, market_data):

    FOR EACH zone IN active_zones:
        
        // Check if price has entered the zone
        IF price_in_zone(market_data.price, zone):
            
            // Trigger confirmation checks
            confirmations = check_all_confirmations(zone, market_data)
            
            IF confirmations.count >= config.min_confirmations:
                EMIT_SIGNAL(
                    type = "FIBONACCI_ZONE_ENTRY",
                    zone = zone,
                    confidence = confirmations.score,
                    recommended_action = determine_action(confirmations)
                )
        
        // Check if zone is invalidated (price blew through)
        ELIF price_beyond_zone(market_data.price, zone, buffer=market_data.atr):
            
            REMOVE_ZONE(zone)
            LOG(f"Zone at {zone.price} invalidated - price moved through")
            
            // Look for the next cluster
            next_zone = find_next_cluster(zone.direction)
            IF next_zone:
                ACTIVATE_ZONE(next_zone)
```

---

## 14. Market-Specific Considerations

### 14.1 Forex Market Fibonacci Behavior

| Characteristic | Description |
|---|---|
| **Precision** | Fibonacci levels are respected with high precision (within 5-15 pips) |
| **Session influence** | London open often triggers moves to/from Fibonacci levels |
| **News events** | NFP, FOMC etc. can push price to extended Fibonacci levels quickly |
| **Carry pairs** | USD/JPY, AUD/JPY tend to respect 38.2% and 50% for Wave 4 |
| **Majors** | EUR/USD, GBP/USD show textbook 61.8% Wave 2 retracements |
| **Spread impact** | Factor in spread when calculating Fibonacci levels for entries |

**Forex-Specific Adjustment:**
$$P_{\text{adjusted}} = P_{\text{fib\_level}} \pm \frac{\text{spread}}{2}$$

### 14.2 Crypto Market Fibonacci Behavior

| Characteristic | Description |
|---|---|
| **Precision** | Fibonacci levels respected within 1%-3% tolerance (wider due to volatility) |
| **Extensions** | Wave 3 often reaches 261.8%-423.6% (far beyond Forex norms) |
| **Retracements** | Wave 2 commonly retraces to 78.6% (deeper than Forex) |
| **Wicks** | Long wicks often touch Fibonacci levels then reverse (use wicks for SL) |
| **24/7 effect** | Fibonacci levels can be hit at any time, including low-liquidity periods |
| **Liquidation cascades** | Can push price temporarily beyond Fibonacci levels |

**Crypto-Specific Adjustments:**
1. Widen cluster tolerance from 0.5% to 1.0%--1.5%
2. Use both wick and close for Fibonacci calculations
3. Add liquidation heatmap data as additional cluster source
4. Consider extended Fibonacci levels (4.236, 6.854) for extreme moves

### 14.3 Cross-Market Fibonacci Confluence

When trading crypto pairs denominated in USD (e.g., BTC/USD), consider:
- Fibonacci levels on BTC/USD chart
- Fibonacci levels on DXY (Dollar Index) chart (inversely correlated)
- Bitcoin dominance chart Fibonacci levels (for altcoins)

$$\text{Cross-Market Confluence} = \text{Asset Fib Level} \cap \text{Correlated Asset Fib Level}$$

---

## 15. References

### 15.1 Primary Sources

1. **Elliott, R.N.** (1946). *Nature's Law: The Secret of the Universe*. (Original Fibonacci-Wave relationship)
2. **Frost, A.J. & Prechter, R.R.** (2017). *Elliott Wave Principle: Key to Market Behavior*. 11th Ed. New Classics Library. (Chapters on Fibonacci relationships)
3. **Neely, G.** (1988). *Mastering Elliott Wave*. Windsor Books. (Precise Fibonacci ratio rules)

### 15.2 Fibonacci-Specific References

4. **Boroden, C.** (2008). *Fibonacci Trading: How to Master the Time and Price Advantage*. McGraw-Hill.
5. **Pesavento, L.** (1997). *Fibonacci Ratios with Pattern Recognition*. Traders Press.
6. **Fischer, R.** (1993). *Fibonacci Applications and Strategies for Traders*. Wiley.
7. **Brown, C.** (2012). *Fibonacci Analysis* (Bloomberg Financial Series). Bloomberg Press.

### 15.3 Mathematical References

8. **Livio, M.** (2002). *The Golden Ratio: The Story of PHI, the World's Most Astonishing Number*. Broadway Books.
9. **Huntley, H.E.** (1970). *The Divine Proportion: A Study in Mathematical Beauty*. Dover.
10. **Koshy, T.** (2001). *Fibonacci and Lucas Numbers with Applications*. Wiley.

### 15.4 Quantitative Trading

11. **Miner, R.C.** (2009). *High Probability Trading Strategies: Entry to Exit Tactics for the Forex, Futures, and Stock Markets*. Wiley.
12. **Grimes, A.** (2012). *The Art and Science of Technical Analysis: Market Structure, Price Action, and Trading Strategies*. Wiley.

### 15.5 Academic

13. **Mandelbrot, B.** (1963). "The Variation of Certain Speculative Prices." *Journal of Business*, 36(4).
14. **Lo, A.W. & MacKinlay, A.C.** (1999). *A Non-Random Walk Down Wall Street*. Princeton University Press.

---

## Document Cross-References

| Document | Path | Relationship |
|---|---|---|
| Overview | `00_overview.md` | Foundational Fibonacci-Wave connections |
| Impulse Waves | `01_impulse_waves.md` | Impulse wave Fibonacci targets |
| Corrective Waves | `02_corrective_waves.md` | Corrective wave Fibonacci targets |
| Wave Counting Algorithm | `04_wave_counting_algorithm.md` | Fibonacci validation in counting |
| Fibonacci Advanced | `../12_fibonacci_advanced/` | Extended Fibonacci techniques |
| Harmonic Patterns | `../06_harmonic_patterns/` | Fibonacci-based harmonic completions |
| Supply/Demand Zones | `../05_supply_demand_zones/` | Zone confluence with Fibonacci |

---

*This document provides the mathematical framework for Fibonacci-based price targeting within the Elliott Wave system. Fibonacci cluster analysis is the primary mechanism for identifying high-probability entry and exit zones. The AI system should calculate clusters across multiple timeframes and wave measurements to maximize confluence and trading confidence.*
