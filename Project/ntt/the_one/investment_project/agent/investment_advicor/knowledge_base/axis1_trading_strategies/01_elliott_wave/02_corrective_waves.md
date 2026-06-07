# Elliott Wave Theory --- Corrective Wave Patterns

## Document Metadata
| Field | Value |
|---|---|
| **Strategy ID** | EW-002 |
| **Category** | Axis 1 --- Trading Strategies |
| **Sub-Category** | Elliott Wave Theory --- Corrective Waves |
| **Applicable Markets** | Forex, Crypto |
| **Timeframes** | All (Multi-Timeframe) |
| **Complexity** | Advanced |
| **AI Suitability** | High (with pattern recognition) |
| **Last Updated** | 2026-04-12 |

---

## Table of Contents
1. [Introduction to Corrective Waves](#1-introduction-to-corrective-waves)
2. [Simple Corrections: Zigzag (5-3-5)](#2-simple-corrections-zigzag-5-3-5)
3. [Simple Corrections: Flat (3-3-5)](#3-simple-corrections-flat-3-3-5)
4. [Simple Corrections: Triangle (3-3-3-3-3)](#4-simple-corrections-triangle-3-3-3-3-3)
5. [Complex Corrections: Double and Triple Zigzags](#5-complex-corrections-double-and-triple-zigzags)
6. [Complex Corrections: Double and Triple Threes (WXY / WXYXZ)](#6-complex-corrections-double-and-triple-threes-wxy--wxyxz)
7. [Running Corrections and Irregular Patterns](#7-running-corrections-and-irregular-patterns)
8. [Fibonacci Retracement Levels for Corrective Patterns](#8-fibonacci-retracement-levels-for-corrective-patterns)
9. [Identifying When a Correction Is Complete](#9-identifying-when-a-correction-is-complete)
10. [Mathematical Models](#10-mathematical-models)
11. [Core Logic --- Trading Rules During Corrections](#11-core-logic----trading-rules-during-corrections)
12. [Technical Conditions for AI Detection](#12-technical-conditions-for-ai-detection)
13. [Risk Parameters](#13-risk-parameters)
14. [Execution Flow](#14-execution-flow)
15. [References](#15-references)

---

## 1. Introduction to Corrective Waves

### 1.1 Definition

Corrective waves move **against** the direction of the trend at the next larger degree. They are inherently more complex, variable, and harder to identify in real-time than motive (impulse) waves. While impulse waves always follow a 5-wave structure, corrections come in a wide variety of patterns.

### 1.2 Fundamental Principle

> **Corrections never have five waves.** Only motive waves have five. An apparent "five-wave" move in the counter-trend direction is either a motive wave of a new trend or part of a more complex correction.

This principle is critical for the AI system: if a counter-trend move subdivides into five waves, it signals that the correction may be over and a new impulse in the counter-trend direction has begun, OR it is Wave A of a zigzag (which has a 5-3-5 structure).

### 1.3 Where Corrections Appear

| Position | Within | Purpose |
|---|---|---|
| Wave 2 | Impulse | Corrects Wave 1 |
| Wave 4 | Impulse | Corrects Wave 3 |
| Wave B | Zigzag, Flat | Counter-move within correction |
| Wave X | Complex correction | Connecting wave between simple corrections |
| Entire A-B-C | After completed impulse | Corrects the entire 5-wave move |

### 1.4 Classification of Corrective Patterns

```
Corrective Patterns
├── Simple (Single) Corrections
│   ├── Zigzag (5-3-5)
│   │   ├── Standard Zigzag
│   │   └── Running Zigzag (rare)
│   ├── Flat (3-3-5)
│   │   ├── Regular Flat
│   │   ├── Expanded (Irregular) Flat
│   │   └── Running Flat
│   └── Triangle (3-3-3-3-3)
│       ├── Contracting Triangle
│       ├── Barrier Triangle
│       ├── Expanding Triangle (rare)
│       └── Running Triangle
│
└── Complex (Combination) Corrections
    ├── Double Zigzag (5-3-5)-(x)-(5-3-5)
    ├── Triple Zigzag (5-3-5)-(x)-(5-3-5)-(x)-(5-3-5)
    ├── Double Three WXY
    │   ├── Zigzag + Flat
    │   ├── Zigzag + Triangle
    │   ├── Flat + Zigzag
    │   ├── Flat + Triangle
    │   └── Flat + Flat
    └── Triple Three WXYXZ
        └── (Any combination of zigzag, flat, triangle)
```

### 1.5 Labeling Convention

| Simple Correction | Labels | Complex Correction | Labels |
|---|---|---|---|
| Zigzag | A-B-C | Double Zigzag | W-X-Y |
| Flat | A-B-C | Triple Zigzag | W-X-Y-X-Z |
| Triangle | A-B-C-D-E | Double Three | W-X-Y |
| | | Triple Three | W-X-Y-X-Z |

---

## 2. Simple Corrections: Zigzag (5-3-5)

### 2.1 Structure

A zigzag consists of three waves labeled **A-B-C** where:

| Wave | Internal Structure | Direction |
|---|---|---|
| Wave A | 5-wave impulse | Against the main trend |
| Wave B | 3-wave corrective | Partial retracement of A |
| Wave C | 5-wave impulse | Same direction as A |

**Total internal sub-waves:** $5 + 3 + 5 = 13$ (a Fibonacci number)

### 2.2 Visual Representation

**Bearish Zigzag (correction after bullish impulse):**
```
Start ───────(B)
   \        / \
    \      /   \
     \    /     \
     (A) /       \
      \ /         \
       ▼           \
                   (C)
                    ▼
```

**Bullish Zigzag (correction after bearish impulse):**
```
                   (C)
                    ▲
       ▲           /
      / \         /
     (A) \       /
     /    \     /
    /      \   /
   /        \ /
Start ───────(B)
```

### 2.3 Rules and Guidelines

**Rules (Inviolable):**
1. Wave A must subdivide into 5 waves (impulse or leading diagonal)
2. Wave B must subdivide into 3 waves (any corrective pattern)
3. Wave C must subdivide into 5 waves (impulse or ending diagonal)
4. Wave B cannot retrace more than 100% of Wave A
5. Wave C must move beyond the end of Wave A

**Guidelines (Tendencies):**
| Guideline | Typical Value | Notes |
|---|---|---|
| Wave B retracement of A | 38.2%--78.6% | Most commonly 50%--61.8% |
| Wave C relative to A | 61.8%--161.8% of A | Most commonly 100% (equality) |
| Wave C relative to A (Forex) | 100%--127.2% of A | Clean relationships |
| Wave C relative to A (Crypto) | 100%--161.8% of A | Often overshoots |

### 2.4 Fibonacci Relationships

$$P_B = P_A + r_B \times (P_{\text{start}} - P_A) \quad \text{where } r_B \in \{0.382, 0.500, 0.618, 0.786\}$$

$$P_C = P_B - e_C \times |P_A - P_{\text{start}}| \quad \text{where } e_C \in \{0.618, 1.000, 1.272, 1.618\}$$

**Wave C targets from Wave A:**

| Ratio | Formula | Probability |
|---|---|---|
| 61.8% | $\|C\| = 0.618 \times \|A\|$ | 15% |
| 100% (equality) | $\|C\| = 1.000 \times \|A\|$ | 35% |
| 127.2% | $\|C\| = 1.272 \times \|A\|$ | 25% |
| 161.8% | $\|C\| = 1.618 \times \|A\|$ | 20% |
| 200% | $\|C\| = 2.000 \times \|A\|$ | 5% |

### 2.5 Trading the Zigzag

**Setup 1: Trade Wave C after Wave B completes**
```
ENTRY:     Sell (bearish zigzag) at Wave B completion (50%-61.8% of A)
STOP:      Above start of zigzag (above Wave B if tight stop)
TARGET:    Wave C terminus at 100%-161.8% of Wave A
RR RATIO:  2:1 to 4:1
```

**Setup 2: Trade the end of the zigzag (reversal)**
```
ENTRY:     Buy at Wave C completion (zigzag termination point)
STOP:      Below Wave C terminus - ATR buffer
TARGET:    New impulse wave in original trend direction
RR RATIO:  3:1 to 5:1+
```

### 2.6 AI Detection Logic

```python
def detect_zigzag(pivots, parent_trend_direction):
    """
    Detect a zigzag pattern (5-3-5).
    
    Parameters:
        pivots: List of significant price points [start, A, B, C]
        parent_trend_direction: 'bullish' or 'bearish'
    
    Returns:
        (is_zigzag, confidence, details)
    """
    if len(pivots) < 4:
        return False, 0.0, "Insufficient pivots"
    
    start, wave_a, wave_b, wave_c = pivots[0], pivots[1], pivots[2], pivots[3]
    
    # Rule checks
    wave_a_is_5_wave = check_five_wave_structure(start, wave_a)
    wave_b_is_3_wave = check_three_wave_structure(wave_a, wave_b)
    wave_c_is_5_wave = check_five_wave_structure(wave_b, wave_c)
    
    range_a = abs(wave_a - start)
    range_b = abs(wave_b - wave_a)
    range_c = abs(wave_c - wave_b)
    
    # Wave B does not retrace more than 100% of A
    b_retracement = range_b / range_a if range_a != 0 else float('inf')
    b_within_limit = b_retracement < 1.0
    
    # Wave C moves beyond Wave A
    if parent_trend_direction == 'bullish':
        # Bearish zigzag correction
        c_beyond_a = wave_c < wave_a
    else:
        # Bullish zigzag correction
        c_beyond_a = wave_c > wave_a
    
    rules_satisfied = all([
        wave_a_is_5_wave,
        wave_b_is_3_wave,
        wave_c_is_5_wave,
        b_within_limit,
        c_beyond_a
    ])
    
    if not rules_satisfied:
        return False, 0.0, "Rules violated"
    
    # Guideline scoring
    b_at_fib = check_fibonacci_level(b_retracement, [0.382, 0.500, 0.618, 0.786])
    c_to_a_ratio = range_c / range_a if range_a != 0 else 0
    c_at_fib = check_fibonacci_level(c_to_a_ratio, [0.618, 1.000, 1.272, 1.618])
    
    confidence = 0.5 + (0.25 * b_at_fib) + (0.25 * c_at_fib)
    
    return True, confidence, {
        'b_retracement': b_retracement,
        'c_to_a_ratio': c_to_a_ratio,
        'pattern_type': 'zigzag'
    }
```

---

## 3. Simple Corrections: Flat (3-3-5)

### 3.1 Structure

A flat consists of three waves labeled **A-B-C** where:

| Wave | Internal Structure | Direction |
|---|---|---|
| Wave A | 3-wave corrective | Against the main trend |
| Wave B | 3-wave corrective | Retraces most or all of A |
| Wave C | 5-wave impulse | Same direction as A |

**Total internal sub-waves:** $3 + 3 + 5 = 11$

### 3.2 Types of Flats

#### 3.2.1 Regular Flat

Wave B retraces **approximately 90%--105%** of Wave A, and Wave C ends **approximately at** the level of Wave A.

```
Regular Flat (Bearish Correction):
Start ──────────── (B) near start level
   \              / \
    \            /   \
     \          /     \
     (A)       /       \
      \       /         \
       \_____/           \
                          (C) near level of A
```

| Feature | Value |
|---|---|
| Wave B retracement of A | 90%--105% |
| Wave C relative to A | ~100% (approximate equality) |
| Overall correction depth | Moderate |

#### 3.2.2 Expanded (Irregular) Flat

Wave B retraces **beyond 100%** of Wave A (exceeds the origin), and Wave C extends **well beyond** Wave A.

```
Expanded Flat (Bearish Correction):
         (B)
         /  \
Start __/    \
   \         \
    \         \
     \         \
     (A)        \
      \          \
       \          \
        \          \
         \         (C) well below A
```

| Feature | Value |
|---|---|
| Wave B retracement of A | 100%--138.2% (typically 115%--127.2%) |
| Wave C relative to A | 127.2%--161.8% of A |
| Overall correction depth | Deep |

**This is the most common type of flat, particularly in Forex markets.**

$$P_B = P_{\text{start}} + e_B \times \text{Range}_A \quad \text{where } e_B \in [0.00, 0.382]$$

(Note: Wave B goes *beyond* start, so this extends past the origin)

$$P_C = P_B - e_C \times \text{Range}_A \quad \text{where } e_C \in [1.272, 1.618, 2.618]$$

#### 3.2.3 Running Flat

Wave B retraces **well beyond 100%** of Wave A, and Wave C **fails to reach** the terminus of Wave A. This creates a pattern where the correction actually ends closer to the direction of the main trend.

```
Running Flat (Bearish Correction in Uptrend):
         (B) <-- beyond start
         /  \
Start __/    \
   \          \(C) <-- above Wave A terminus
    \              
     (A)       
```

| Feature | Value |
|---|---|
| Wave B retracement of A | 105%--161.8% |
| Wave C relative to A | Does NOT reach A's terminus |
| Significance | Strongly bullish --- trend resumes aggressively |

**Running flats are significant because they indicate the main trend is extremely strong.** The correction barely corrects. They are most common as Wave 2 of an extended Wave 3.

### 3.3 Fibonacci Relationships for Flats

**Regular Flat:**
$$|C| \approx |A| \quad \text{(equality)}$$
$$|B| \approx 0.90\text{--}1.05 \times |A|$$

**Expanded Flat:**
$$|C| = e \times |A| \quad \text{where } e \in \{1.272, 1.618, 2.618\}$$
$$|B| = e \times |A| \quad \text{where } e \in \{1.00, 1.127, 1.236, 1.382\}$$

**Running Flat:**
$$|C| < |A|$$
$$|B| > |A| \quad \text{(significantly)}$$

### 3.4 Flat vs. Zigzag Distinction

| Feature | Zigzag | Flat |
|---|---|---|
| Wave A structure | 5-wave impulse | 3-wave corrective |
| Wave B retracement of A | Typically 38.2%--78.6% | Typically 90%--138.2% |
| Correction depth | Deep, sharp | Moderate, sideways |
| Common position | Wave 2 | Wave 4 |
| Character | Sharp and fast | Slow and grinding |
| Sub-wave count | 5-3-5 = 13 | 3-3-5 = 11 |

### 3.5 Trading Flats

**Setup: Trade Wave C of an Expanded Flat**
```
CONDITION: Wave B of flat has retraced beyond 100% of Wave A (expanded flat)
ENTRY:     Sell (in bearish flat) when Wave B completes and Wave C begins
           Confirmation: Break below Wave A's terminus
STOP:      Above Wave B terminus + ATR buffer
TARGET:    Wave C = 127.2%-161.8% of Wave A from Wave B terminus
RR RATIO:  2:1 to 3:1
```

**Setup: Trade the End of a Flat (Reversal)**
```
CONDITION: Complete flat pattern identified at key Fibonacci level
ENTRY:     Buy/Sell in direction of main trend at Wave C terminus
STOP:      Beyond Wave C terminus - Fibonacci extension level
TARGET:    Next impulse wave
RR RATIO:  3:1 to 5:1+
```

### 3.6 AI Detection Logic

```python
def detect_flat(pivots, parent_trend_direction):
    """
    Detect a flat pattern (3-3-5).
    """
    start, wave_a, wave_b, wave_c = pivots[0], pivots[1], pivots[2], pivots[3]
    
    range_a = abs(wave_a - start)
    range_b = abs(wave_b - wave_a)
    range_c = abs(wave_c - wave_b)
    
    # Structure checks
    wave_a_is_3_wave = check_three_wave_structure(start, wave_a)
    wave_b_is_3_wave = check_three_wave_structure(wave_a, wave_b)
    wave_c_is_5_wave = check_five_wave_structure(wave_b, wave_c)
    
    b_retracement = range_b / range_a if range_a != 0 else 0
    c_to_a_ratio = range_c / range_a if range_a != 0 else 0
    
    # Classify flat type
    if 0.90 <= b_retracement <= 1.05:
        flat_type = 'regular'
    elif b_retracement > 1.05:
        if parent_trend_direction == 'bullish':
            c_reaches_a = wave_c <= wave_a  # bearish flat
        else:
            c_reaches_a = wave_c >= wave_a  # bullish flat
        
        if c_reaches_a:
            flat_type = 'expanded'
        else:
            flat_type = 'running'
    else:
        flat_type = 'not_flat'  # B retracement too small, likely a zigzag
        return False, 0.0, {}
    
    rules_satisfied = all([
        wave_a_is_3_wave,
        wave_b_is_3_wave,
        wave_c_is_5_wave,
        b_retracement >= 0.80  # B must retrace at least 80% of A for a flat
    ])
    
    if not rules_satisfied:
        return False, 0.0, "Rules not met"
    
    confidence = 0.6  # Base
    if check_fibonacci_level(c_to_a_ratio, [1.0, 1.272, 1.618]):
        confidence += 0.2
    if flat_type == 'expanded':  # Most common, highest confidence
        confidence += 0.1
    
    return True, confidence, {'flat_type': flat_type, 'b_retracement': b_retracement}
```

---

## 4. Simple Corrections: Triangle (3-3-3-3-3)

### 4.1 Structure

A triangle consists of **five waves** labeled **A-B-C-D-E**, each of which subdivides into **three waves** (corrective).

| Wave | Internal Structure | Direction |
|---|---|---|
| Wave A | 3-wave corrective | Against main trend |
| Wave B | 3-wave corrective | With main trend |
| Wave C | 3-wave corrective | Against main trend |
| Wave D | 3-wave corrective | With main trend |
| Wave E | 3-wave corrective | Against main trend |

**Total internal sub-waves:** $3 \times 5 = 15$

### 4.2 Types of Triangles

#### 4.2.1 Contracting Triangle (Most Common)

Trendlines connecting A-C and B-D converge. Each successive wave is shorter than the previous.

```
Contracting Triangle:
    (A)          
   / \    (C)   
  /   \  / \  (E)
 /     \/   \/  \
/     (B)\  (D)  \___  THRUST →
          \  / \
           \/   
            
Trendlines: A-C line slopes inward, B-D line slopes inward (converging)
```

| Feature | Value |
|---|---|
| Wave A | Longest corrective wave |
| Wave B | Shorter than A; retraces 50%--88.6% of A |
| Wave C | Shorter than B |
| Wave D | Shorter than C |
| Wave E | Shortest; often terminates at 61.8% of A-C trendline |
| Post-triangle thrust | Rapid, decisive move in trend direction |

**Fibonacci Relationships:**

$$|B| \approx 0.618 \times |A|$$
$$|C| \approx 0.618 \times |B| \approx 0.382 \times |A|$$
$$|D| \approx 0.618 \times |C|$$
$$|E| \approx 0.618 \times |D|$$

Each wave is approximately 61.8% of the previous wave.

#### 4.2.2 Barrier Triangle

One of the trendlines is horizontal (flat), while the other converges toward it. Wave B and Wave D end at approximately the same level.

```
Barrier Triangle (Ascending):
    (A)
   / \    (C)
  /   \  / \  (E)
 /     \/   \/   \
/     (B)   (D)   \___ THRUST ↗
─────────────────────── (B-D line is horizontal)
```

#### 4.2.3 Expanding Triangle (Rare)

Trendlines **diverge**. Each successive wave is longer than the previous.

```
Expanding Triangle:
            (E)
           / \
      (C) /   \
     / \ /     \
(A) /   X       \
 / \ (D)\       \___  THRUST →
/  (B)    \
           \ 
```

| Feature | Value |
|---|---|
| Frequency | Rare (~5% of triangles) |
| Wave E | Longest wave (most violent) |
| Thrust after | Can be smaller than expected |

#### 4.2.4 Running Triangle

The triangle slopes in the direction of the main trend. Wave B exceeds the beginning of Wave A.

### 4.3 Where Triangles Appear

Triangles appear **exclusively** in these positions:

| Position | Context | Notes |
|---|---|---|
| Wave 4 | Within an impulse | Most common position |
| Wave B | Within a flat or zigzag | Common |
| Wave X | Within a complex correction | Common |
| Wave E | Within a larger triangle | Rare (triangle within triangle) |
| **Never in** | Wave 2 or Wave A | Triangles do NOT appear in Wave 2 or Wave A positions |

### 4.4 The Post-Triangle Thrust

After a triangle completes, price typically **thrusts** rapidly in the direction of the main trend. The thrust often:

$$\text{Thrust} \approx \text{Range}_A \quad \text{(measured from the apex)}$$

Or more conservatively:

$$\text{Thrust} = \text{Widest part of the triangle (Wave A range)}$$

This thrust is one of the most tradeable signals in Elliott Wave analysis.

### 4.5 Trading Triangles

**Setup 1: Trade the Post-Triangle Thrust**
```
CONDITION: Triangle pattern (A-B-C-D-E) complete; Wave E terminates near B-D trendline
ENTRY:     Buy/Sell in trend direction when price breaks the A-C trendline
           OR enter at Wave E completion with B-D trendline as reference
STOP:      Beyond Wave E terminus (opposite side of triangle)
TARGET:    Thrust target = Wave A range projected from breakout point
RR RATIO:  3:1 to 5:1+ (excellent)
```

**Setup 2: Trade Wave E within the Triangle**
```
CONDITION: Waves A-B-C-D complete; Wave E approaching B-D or A-C trendline
ENTRY:     Trade Wave E in the direction it will move
STOP:      Beyond the converging trendline + buffer
TARGET:    Opposite trendline or 61.8% of Wave D range
RR RATIO:  1.5:1 to 2:1 (moderate)
```

### 4.6 AI Detection Logic

```python
def detect_triangle(pivots, parent_wave_position):
    """
    Detect a triangle pattern (3-3-3-3-3).
    
    Parameters:
        pivots: [start, A, B, C, D, E]
        parent_wave_position: Must be Wave 4, Wave B, or Wave X
    """
    if len(pivots) < 6:
        return False, 0.0, "Need 6 pivots for triangle"
    
    start, a, b, c, d, e = pivots[0:6]
    
    # Position validation
    valid_positions = ['wave_4', 'wave_b', 'wave_x']
    if parent_wave_position not in valid_positions:
        return False, 0.0, "Triangle invalid in this position"
    
    # All sub-waves must be 3-wave structures
    sub_waves = [(start, a), (a, b), (b, c), (c, d), (d, e)]
    all_three_wave = all(check_three_wave_structure(sw[0], sw[1]) for sw in sub_waves)
    
    ranges = [abs(sub_waves[i][1] - sub_waves[i][0]) for i in range(5)]
    
    # Contracting: each wave shorter than previous
    is_contracting = all(ranges[i] > ranges[i+1] for i in range(4))
    
    # Expanding: each wave longer than previous
    is_expanding = all(ranges[i] < ranges[i+1] for i in range(4))
    
    # Check trendline convergence
    ac_slope = calculate_trendline_slope(a, c, e)  # A-C-E trendline
    bd_slope = calculate_trendline_slope(b, d)       # B-D trendline
    
    trendlines_converge = abs(ac_slope - bd_slope) > 0  # Should converge for contracting
    
    # Fibonacci ratios
    fib_ratios_ok = True
    for i in range(1, len(ranges)):
        ratio = ranges[i] / ranges[i-1] if ranges[i-1] != 0 else 0
        if not (0.382 <= ratio <= 0.886):  # Each wave roughly 61.8% of previous (with tolerance)
            fib_ratios_ok = False
    
    if is_contracting:
        triangle_type = 'contracting'
        confidence = 0.75 if all_three_wave else 0.50
    elif is_expanding:
        triangle_type = 'expanding'
        confidence = 0.60 if all_three_wave else 0.40
    else:
        triangle_type = 'barrier_or_irregular'
        confidence = 0.55 if all_three_wave else 0.35
    
    if fib_ratios_ok:
        confidence += 0.15
    
    return True, min(confidence, 1.0), {
        'triangle_type': triangle_type,
        'ranges': ranges,
        'thrust_target': ranges[0]  # Wave A range = thrust estimate
    }
```

---

## 5. Complex Corrections: Double and Triple Zigzags

### 5.1 Double Zigzag (WXY)

When a single zigzag does not achieve sufficient corrective depth, the market may produce a **double zigzag**: two zigzag patterns connected by an intervening wave (Wave X).

**Structure:** Zigzag - X - Zigzag

**Labeling:** W-X-Y (where W and Y are each zigzag patterns, and X is a corrective connector)

| Component | Internal Structure | Sub-Wave Count |
|---|---|---|
| Wave W | Zigzag (5-3-5) | 13 |
| Wave X | Any corrective (3) | 3--13 |
| Wave Y | Zigzag (5-3-5) | 13 |

```
Double Zigzag (Bearish):
Start ──────(B_w)──────── (X) ──────(B_y)
   \        / \        / \        / \
    \      /   \      /   \      /   \
     \    /     \    /     \    /     \
     (A_w)/     (C_w)/     (A_y)/     \
      \ /         \ /         \ /      \
       ▼(W end)    ▼           ▼       (C_y)
                                        ▼ (Y end)
```

### 5.2 Triple Zigzag (WXYXZ)

Even rarer: three zigzag patterns connected by two X waves.

**Structure:** Zigzag - X - Zigzag - X - Zigzag

**Labeling:** W-X-Y-X-Z

### 5.3 Fibonacci Relationships in Double/Triple Zigzags

$$|Y| \approx |W| \quad \text{(equality is most common)}$$

$$|Y| = r \times |W| \quad \text{where } r \in \{0.618, 1.000, 1.618\}$$

**Wave X typically retraces 38.2%--61.8% of Wave W.**

$$|X| = r \times |W| \quad \text{where } r \in \{0.382, 0.500, 0.618\}$$

### 5.4 Guidelines for Double/Triple Zigzags

1. Wave X must be **shallower** than Wave W (X retraces less than 100% of W)
2. Wave Y typically achieves **equality with** or is **61.8%--161.8% of** Wave W
3. The overall pattern is **sharper** and **deeper** than a single zigzag
4. Common in **Wave 2** positions (sharp, deep corrections)
5. Also common as Wave A in larger corrections

### 5.5 Trading Double/Triple Zigzags

```
SETUP: Trade Wave Y completion (end of double zigzag)

CONDITION: 
  - Wave W (zigzag) complete
  - Wave X retracement at 38.2%-61.8% of W
  - Wave Y developing as second zigzag
  - Y approaching equality with W (or 61.8%/161.8% ratio)

ENTRY: Buy/Sell at Wave Y terminus in main trend direction
STOP:  Beyond Y terminus at next Fibonacci level
TARGET: New impulse wave (often Wave 3, which is the strongest)
RR:    3:1 to 5:1+
```

---

## 6. Complex Corrections: Double and Triple Threes (WXY / WXYXZ)

### 6.1 Definition

A **double three** or **triple three** is a sideways combination of two or three corrective patterns, connected by X waves. Unlike double/triple zigzags (which are deep), these combinations are **sideways** and produce the most time-consuming, frustrating corrections.

### 6.2 Double Three (WXY)

**Structure:** Any two simple corrections connected by an X wave

| Component | Possible Patterns |
|---|---|
| Wave W | Zigzag, Flat, or (rarely) Triangle |
| Wave X | Any corrective pattern |
| Wave Y | Zigzag, Flat, or Triangle |

**Key Rule:** Wave Y cannot be another pattern of the same type as Wave W and achieve the same depth. The purpose of a combination is to extend the correction **sideways** in time, not deeper in price.

**Common Combinations:**

| Wave W | Wave X | Wave Y | Frequency |
|---|---|---|---|
| Zigzag | Corrective | Flat | Common |
| Zigzag | Corrective | Triangle | Common |
| Flat | Corrective | Zigzag | Moderate |
| Flat | Corrective | Triangle | Moderate |
| Flat | Corrective | Flat | Less common |

```
Double Three WXY (Sideways Correction):
         (W)                    (Y)
        /\  \      (X)        /  \  /
       /  \  \    /  \      /    \/
      /    \  \  /    \    /      
     /      \  \/      \  /       
    /        \/         \/        
Start                              End
                                   
(Overall sideways movement; contrasts with the deeper double zigzag)
```

### 6.3 Triple Three (WXYXZ)

**Structure:** Three simple corrections connected by two X waves

$$W - X - Y - X - Z$$

| Component | Possible Patterns |
|---|---|
| Wave W | Zigzag or Flat |
| Wave X (first) | Any corrective |
| Wave Y | Zigzag, Flat, or Triangle |
| Wave X (second) | Any corrective |
| Wave Z | Zigzag, Flat, or Triangle |

**Key rule:** A triangle can only appear as the **last** pattern in the combination (Wave Y in WXY, or Wave Z in WXYXZ).

### 6.4 Fibonacci Relationships in Combinations

**Wave X retracement of W:**
$$|X| = r \times |W| \quad \text{where } r \in \{0.382, 0.500, 0.618, 0.786\}$$

**Wave Y relative to W:**
$$|Y| = r \times |W| \quad \text{where } r \in \{0.618, 1.000, 1.618\}$$

**Overall correction depth:**
Combinations typically retrace **38.2%--50%** of the prior impulse (shallower than zigzags).

### 6.5 Where Combinations Appear

| Position | Frequency | Notes |
|---|---|---|
| Wave 4 | Very common | Wave 4 is prone to complex sideways corrections |
| Wave B | Common | Especially in expanded flats |
| Wave X | Common | X waves themselves can be combinations |
| Wave 2 | Rare | Wave 2 is typically sharp, not sideways |

### 6.6 Trading Combinations

Combinations are the **hardest corrections to trade** because:
- They extend sideways for a long time
- Each time a pattern seems complete, a new X wave and correction begin
- They frequently whipsaw traders who attempt to trade the breakout prematurely

**Best Approach for AI:**
```
1. IDENTIFY that a combination is forming (Wave W complete, X wave developing)
2. WAIT for the combination to complete rather than trading within it
3. MONITOR for a triangle as the final component (signals imminent completion)
4. ENTER only after the post-combination thrust confirms the new trend direction
5. Use the triangle thrust or Wave C of the final component as the entry trigger
```

**Conservative Entry:**
```
CONDITION: WXY or WXYXZ complete, with final pattern being a triangle
ENTRY:     Buy/Sell on post-triangle thrust (breakout of triangle)
STOP:      Beyond Wave E of the triangle
TARGET:    Triangle Wave A range (thrust target) as minimum
           Full impulse wave resumption as maximum
RR:        2:1 minimum; often 3:1+
```

---

## 7. Running Corrections and Irregular Patterns

### 7.1 Running Flat (Detailed)

In a running flat, Wave B exceeds the origin of Wave A, and Wave C fails to reach the terminus of Wave A.

**Significance:** Running flats indicate extreme strength in the main trend direction. The correction barely corrects.

**Fibonacci Relationships:**

$$|B| > |A| \quad \text{(B exceeds start of correction)}$$
$$|C| < |A| \quad \text{(C does not reach A's terminus)}$$

Typical:
$$|B| = 1.127\text{--}1.382 \times |A|$$
$$|C| = 0.618\text{--}0.786 \times |A|$$

### 7.2 Running Triangle

A running triangle slopes in the direction of the main trend, with Wave B exceeding the beginning of Wave A.

```
Running Triangle (In Uptrend, Wave 4):
         (B)
        / \   (D)
       /   \ / \
      /    (C)  (E)
     / \       / \___  Thrust upward ↗
    /   (A)   /
   /         /
  /         /
(Start of W4)

Note: The triangle "runs" - its overall trajectory moves with the trend
```

### 7.3 Expanded Flat (B-Wave Traps)

The expanded flat is particularly dangerous for traders because:

1. Wave B's thrust beyond Wave A's origin looks like a trend continuation
2. Traders enter in the trend direction, expecting a breakout
3. Wave C then reverses sharply, stopping out those traders and exceeding Wave A's terminus

**For AI detection:** The key is recognizing that Wave A has a 3-wave structure (not 5-wave). If the initial counter-trend move is a 3-wave pattern, an expanded flat is a strong possibility, and the "breakout" (Wave B exceeding origin) is a trap.

### 7.4 Irregular Corrections in Crypto

Crypto markets produce several irregular correction patterns due to:
- Thin order books causing spike wicks
- Liquidation cascades amplifying moves
- Extreme sentiment swings

| Irregularity | Description | Handling |
|---|---|---|
| B-wave spike beyond 138.2% | Extreme expanded flat | Use 161.8% as outer limit |
| C-wave truncation | Wave C fails to complete | Wait for clear 5-wave C structure |
| Mixed patterns | Part zigzag, part flat characteristics | Default to combination (WXY) |
| Time asymmetry | Corrections much faster than in Forex | Adjust time proportion parameters |

---

## 8. Fibonacci Retracement Levels for Corrective Patterns

### 8.1 Master Retracement Table

| Correction Type | Typical Retracement of Prior Impulse | Fibonacci Levels |
|---|---|---|
| **Zigzag** | Deep | 50%, 61.8%, 78.6% |
| **Double Zigzag** | Very Deep | 61.8%, 78.6%, 88.6% |
| **Regular Flat** | Moderate | 38.2%, 50% |
| **Expanded Flat** | Deep (due to C-wave extension) | 50%, 61.8%, 78.6% |
| **Running Flat** | Shallow | 23.6%, 38.2% |
| **Contracting Triangle** | Shallow to Moderate | 23.6%, 38.2%, 50% |
| **Combination (WXY)** | Moderate | 38.2%, 50% |

### 8.2 Retracement by Wave Position

| Position | As Wave 2 | As Wave 4 |
|---|---|---|
| Zigzag | 50%--78.6% of Wave 1 | Rare in Wave 4 |
| Flat | Possible but uncommon | 23.6%--50% of Wave 3 |
| Triangle | **Never** in Wave 2 | 23.6%--38.2% of Wave 3 |
| Combination | Rare (sideways not typical for W2) | 38.2%--50% of Wave 3 |

### 8.3 Internal Fibonacci Relationships

**Within a Zigzag:**
$$|B_{\text{zigzag}}| = r \times |A_{\text{zigzag}}| \quad r \in \{0.382, 0.500, 0.618, 0.786\}$$
$$|C_{\text{zigzag}}| = e \times |A_{\text{zigzag}}| \quad e \in \{0.618, 1.000, 1.272, 1.618\}$$

**Within a Flat:**
$$|B_{\text{flat}}| \approx |A_{\text{flat}}| \quad \text{(approximately 90%-138.2%)}$$
$$|C_{\text{flat}}| = e \times |A_{\text{flat}}| \quad e \in \{1.000, 1.272, 1.618, 2.618\}$$

**Within a Triangle:**
$$|B| \approx 0.618 \times |A|$$
$$|C| \approx 0.618 \times |B|$$
$$|D| \approx 0.618 \times |C|$$
$$|E| \approx 0.618 \times |D|$$

### 8.4 Fibonacci Cluster Zones for Correction Completion

The AI system should calculate multiple Fibonacci levels from different reference points and identify **clusters** (confluence zones) where several levels converge:

```python
def find_correction_completion_zone(impulse_waves, correction_type):
    """
    Calculate Fibonacci cluster zones for correction completion.
    
    Returns a list of price levels ranked by confluence density.
    """
    levels = []
    
    # Level 1: Retracement of entire impulse (Wave 1 start to Wave 5 end)
    full_range = abs(impulse_waves[5] - impulse_waves[0])
    for r in [0.236, 0.382, 0.500, 0.618, 0.786]:
        level = impulse_waves[5] - r * full_range  # bullish impulse
        levels.append(('impulse_retrace', r, level))
    
    # Level 2: Wave 4 of prior impulse (price support/resistance)
    levels.append(('wave_4_territory', None, impulse_waves[4]))
    
    # Level 3: Extension of Wave A within the correction
    if correction_type in ['zigzag', 'flat']:
        wave_a_range = abs(correction_waves['a_end'] - correction_waves['a_start'])
        for e in [0.618, 1.000, 1.272, 1.618]:
            level = correction_waves['b_end'] - e * wave_a_range
            levels.append(('wave_c_extension', e, level))
    
    # Level 4: Sub-wave iv of Wave 3 (common support)
    levels.append(('wave_3_sub_iv', None, impulse_waves['w3_sub_iv']))
    
    # Find clusters
    clusters = find_price_clusters(levels, tolerance=0.005)  # 0.5% tolerance
    
    return sorted(clusters, key=lambda x: x['density'], reverse=True)
```

---

## 9. Identifying When a Correction Is Complete

### 9.1 Completion Signals

The AI system should monitor for the following signals to determine when a correction is complete:

| Signal | Weight | Description |
|---|---|---|
| **Pattern complete** | 0.30 | A-B-C, A-B-C-D-E, or WXY structure is internally complete |
| **Fibonacci target reached** | 0.25 | Price at key Fibonacci retracement/extension level |
| **Fibonacci cluster** | 0.20 | Multiple Fibonacci levels converge at current price |
| **Momentum divergence** | 0.10 | RSI/MACD shows divergence at correction terminus |
| **Volume climax** | 0.05 | Volume spike (capitulation) at the end of correction |
| **Time proportion** | 0.05 | Correction duration proportional to impulse |
| **Reversal pattern** | 0.05 | Candlestick or chart pattern reversal signal |

### 9.2 Completion Checklist by Pattern Type

**Zigzag Completion:**
- [ ] Wave A shows 5-wave subdivision
- [ ] Wave B retraces 38.2%--78.6% of A (3-wave structure)
- [ ] Wave C shows 5-wave subdivision
- [ ] Wave C extends to 100%--161.8% of Wave A
- [ ] Overall zigzag reaches key Fibonacci retracement of prior impulse
- [ ] Momentum divergence at Wave C terminus

**Flat Completion:**
- [ ] Wave A shows 3-wave subdivision
- [ ] Wave B retraces 90%+ of A (3-wave structure)
- [ ] Wave C shows 5-wave subdivision
- [ ] Wave C extends to 100%--161.8% of Wave A
- [ ] Volume spike at Wave C terminus (shakeout)

**Triangle Completion:**
- [ ] Five waves (A-B-C-D-E) all show 3-wave subdivisions
- [ ] Each successive wave is shorter (contracting) or longer (expanding)
- [ ] Converging trendlines validated
- [ ] Wave E terminates near or at the B-D trendline
- [ ] Volume contracts progressively through the triangle

### 9.3 The "Three Drives" Confirmation

A powerful confirmation that a correction is complete: after the correction terminus, monitor for an initial impulse move (the beginning of the new trend), followed by a corrective pullback that **does not** reach the correction terminus. This confirms:
1. The correction low/high is in place
2. A new impulse sequence has begun
3. The pullback is Wave 2 of the new impulse

### 9.4 False Completion Detection

The AI must guard against false completion signals:

| False Signal | How to Detect | Action |
|---|---|---|
| Zigzag completes but market extends to double zigzag | Wave X develops after apparent completion | Re-label as W-X-Y |
| Flat Wave C appears complete but extends | C-wave subdivision not yet at 5 waves | Wait for clear 5-wave C |
| Triangle Wave E overshoots | E exceeds trendline significantly | May not be a triangle |
| Time truncation | Correction ends faster than expected | Increase caution; may resume |

---

## 10. Mathematical Models

### 10.1 Corrective Wave Price Model

**Zigzag Model (bearish correction in bullish trend):**

$$P_A = P_0 - \Delta_A \quad (\Delta_A > 0)$$

$$P_B = P_A + r_B \cdot \Delta_A \quad \text{where } 0 < r_B < 1$$

$$P_C = P_B - e_C \cdot \Delta_A \quad \text{where } e_C > 0 \text{ and } P_C < P_A$$

**Flat Model (bearish correction in bullish trend):**

$$P_A = P_0 - \Delta_A$$

$$P_B = P_A + r_B \cdot \Delta_A \quad \text{where } r_B \approx 1.0 \text{ (can exceed 1.0)}$$

$$P_C = P_B - e_C \cdot \Delta_A \quad \text{where } e_C \geq 1.0$$

**Triangle Model:**

$$P_{n+1} = P_n + (-1)^n \cdot k^n \cdot \Delta_A \quad \text{where } k \approx 0.618 \text{ (contraction factor)}$$

for $n = 0, 1, 2, 3, 4$ (waves A through E).

### 10.2 Correction Depth Estimator

Given a completed impulse wave with total range $R_{\text{impulse}}$:

$$P_{\text{correction\_target}} = P_{\text{W5}} - d \cdot R_{\text{impulse}}$$

where the depth factor $d$ depends on the expected correction type:

| Expected Type | Depth Factor $d$ | Range |
|---|---|---|
| Running flat | 0.146--0.382 | Shallow |
| Triangle | 0.236--0.382 | Shallow |
| Regular flat | 0.382--0.500 | Moderate |
| Zigzag | 0.500--0.618 | Deep |
| Expanded flat | 0.500--0.786 | Deep |
| Double zigzag | 0.618--0.886 | Very deep |

### 10.3 Correction Completion Probability

$$P(\text{complete} | \text{data}) = \frac{P(\text{data} | \text{complete}) \cdot P(\text{complete})}{P(\text{data})}$$

Using Bayesian updating with priors based on:
- Fibonacci level reached (higher prior at key levels)
- Pattern structure completeness
- Time elapsed relative to impulse
- Volume and momentum conditions

### 10.4 Expected Value of Correction Trade

$$EV = P_{\text{win}} \times R_{\text{win}} - (1 - P_{\text{win}}) \times R_{\text{loss}}$$

where:
- $P_{\text{win}}$ = probability of correction being complete (confidence score)
- $R_{\text{win}}$ = reward if correct (distance to next impulse target)
- $R_{\text{loss}}$ = loss if incorrect (distance to stop loss / invalidation)

A trade should only be taken if $EV > 0$ and $\frac{R_{\text{win}}}{R_{\text{loss}}} \geq 2.0$.

---

## 11. Core Logic --- Trading Rules During Corrections

### 11.1 General Rules

```
┌────────────────────────────────────────────────────────────────┐
│  GOLDEN RULES FOR TRADING CORRECTIONS                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  1. NEVER trade against the main trend during a correction     │
│     unless the correction pattern is crystal clear.            │
│                                                                │
│  2. WAIT for the correction to complete and the new impulse    │
│     to begin. This is the HIGHEST PROBABILITY approach.        │
│                                                                │
│  3. If trading within a correction, only trade the C-wave      │
│     of a zigzag or flat (it is an impulse wave internally).    │
│                                                                │
│  4. REDUCE position size during corrections by 30%-50%         │
│     relative to impulse wave trades.                           │
│                                                                │
│  5. USE tighter stops during corrections due to higher         │
│     probability of whipsaw.                                    │
│                                                                │
│  6. PREFER the post-triangle thrust as the safest correction   │
│     completion trade.                                          │
│                                                                │
│  7. ALWAYS have a clear invalidation level. If the correction  │
│     exceeds expected Fibonacci levels, the count is wrong.     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 11.2 Correction Trading Decision Matrix

| Pattern Identified | Tradeable? | How to Trade | Risk Level |
|---|---|---|---|
| Zigzag forming (A complete, B forming) | Yes | Sell C-wave after B completes | Medium |
| Zigzag near completion | **Yes** | Buy/Sell in trend direction at C terminus | Low-Medium |
| Flat forming | Partially | Trade C-wave after B completes | Medium-High |
| Flat near completion | **Yes** | Trade in trend direction at C terminus | Low-Medium |
| Triangle forming (A-B-C-D visible) | Wait | Prepare for post-E thrust | Low |
| Triangle complete (E done) | **Yes** | Trade the thrust | Low |
| Double/Triple forming | **No** | Wait for completion | High (avoid) |
| Complex correction unclear | **No** | Do not trade; wait for clarity | Very High (avoid) |

### 11.3 Entry Logic for Correction Completion

```python
def evaluate_correction_trade(correction_analysis, market_data, config):
    """
    Evaluate whether to enter a trade at the perceived end of a correction.
    
    Returns: TradeSetup or None
    """
    # Step 1: Pattern completion check
    pattern = correction_analysis['pattern_type']
    completion_score = correction_analysis['completion_confidence']
    
    if completion_score < config['min_correction_confidence']:  # Default: 0.70
        return None  # Not confident enough
    
    # Step 2: Fibonacci confluence check
    fib_cluster = find_fibonacci_cluster(correction_analysis, market_data)
    if fib_cluster['density'] < config['min_fib_cluster_density']:  # Default: 2 levels
        return None  # Insufficient confluence
    
    # Step 3: Confirmation signals
    confirmations = {
        'momentum_divergence': check_divergence(market_data),
        'volume_climax': check_volume_climax(market_data),
        'reversal_candle': check_reversal_pattern(market_data),
        'lower_tf_impulse': check_new_impulse_on_ltf(market_data),
    }
    
    confirmation_count = sum(confirmations.values())
    if confirmation_count < 2:
        return None  # Need at least 2 confirmation signals
    
    # Step 4: Calculate trade parameters
    entry_price = market_data['current_price']
    
    # Stop loss: beyond correction terminus at next Fibonacci level
    sl_distance = calculate_correction_sl(correction_analysis, market_data)
    
    # Take profit: based on expected new impulse wave targets
    tp_levels = calculate_new_impulse_targets(correction_analysis, market_data)
    
    rr_ratio = tp_levels[0]['distance'] / sl_distance  # TP1 RR
    
    if rr_ratio < config['min_rr_ratio']:  # Default: 2.0
        return None  # Insufficient risk/reward
    
    # Step 5: Build trade setup
    setup = TradeSetup(
        direction='long' if correction_analysis['main_trend'] == 'bullish' else 'short',
        entry=entry_price,
        stop_loss=entry_price - sl_distance if correction_analysis['main_trend'] == 'bullish' 
                  else entry_price + sl_distance,
        take_profits=tp_levels,
        confidence=completion_score,
        pattern=pattern,
        rr_ratio=rr_ratio,
    )
    
    return setup
```

---

## 12. Technical Conditions for AI Detection

### 12.1 Corrective Pattern Recognition Pipeline

```
Input: OHLCV Data + Identified Impulse Wave + Pivot Points
                    │
                    ▼
          ┌─────────────────┐
          │ Identify Wave A  │
          │ (first leg of    │
          │  correction)     │
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │ Count A's sub-  │
          │ waves (5 or 3?) │
          └────────┬────────┘
                   │
         ┌─────────┴──────────┐
         │                    │
    A = 5 waves          A = 3 waves
    (Impulse)            (Corrective)
         │                    │
         ▼                    ▼
    ZIGZAG likely         FLAT or TRIANGLE
    (or Wave 1 of           likely
     new impulse)             │
         │               ┌────┴────┐
         │               │         │
         ▼               ▼         ▼
    Wait for B,      B ≈ 100%   B < 75%
    then C(5-wave)   of A       of A
                        │         │
                        ▼         ▼
                    FLAT       Possibly
                    (Regular,  not a flat;
                    Expanded,  re-evaluate
                    Running)   as WXY
```

### 12.2 Pattern Detection Parameters

```python
CORRECTIVE_DETECTION_CONFIG = {
    # Zigzag parameters
    'zigzag': {
        'wave_a_structure': '5-wave',
        'wave_b_max_retrace': 0.999,    # <100% of A (rule)
        'wave_b_typical_retrace': [0.382, 0.500, 0.618, 0.786],
        'wave_c_structure': '5-wave',
        'wave_c_min_extension': 0.618,   # C >= 61.8% of A
        'wave_c_typical_extension': [0.618, 1.000, 1.272, 1.618],
        'c_must_exceed_a': True,          # C goes beyond A's terminus
    },
    
    # Flat parameters
    'flat': {
        'wave_a_structure': '3-wave',
        'wave_b_min_retrace': 0.80,      # B retraces at least 80% of A
        'wave_b_structure': '3-wave',
        'wave_c_structure': '5-wave',
        'regular_b_range': [0.90, 1.05], # Regular flat B range
        'expanded_b_range': [1.05, 1.382],  # Expanded flat B range
        'running_c_less_than_a': True,    # Running: C < A
    },
    
    # Triangle parameters
    'triangle': {
        'num_waves': 5,                   # A-B-C-D-E
        'all_sub_waves': '3-wave',        # Each must be 3-wave
        'valid_positions': ['wave_4', 'wave_b', 'wave_x'],
        'contraction_ratio': 0.618,       # Each wave ~61.8% of previous
        'contraction_tolerance': 0.15,    # +/- tolerance
        'volume_decline': True,           # Volume should diminish
    },
    
    # Complex correction parameters
    'combination': {
        'max_components': 3,              # W-X-Y or W-X-Y-X-Z
        'wave_x_max_retrace': 0.786,     # X usually < 78.6% of W
        'triangle_only_last': True,       # Triangle can only be final pattern
        'y_to_w_ratio': [0.618, 1.000, 1.618],
    },
}
```

### 12.3 Sub-Wave Counting Algorithm

```python
def count_sub_waves(price_data, pivot_threshold):
    """
    Count internal sub-waves to determine if a wave is motive (5) or corrective (3).
    
    This is the most critical function for corrective wave identification.
    """
    # Step 1: Identify pivots using ZigZag with the given threshold
    pivots = zigzag(price_data, threshold=pivot_threshold)
    
    # Step 2: Count alternating high-low pivots
    wave_count = len(pivots) - 1  # Number of waves = pivots - 1
    
    # Step 3: Classify
    if wave_count == 5:
        # Potential motive wave --- check iron rules
        if validate_impulse_rules(pivots):
            return '5-wave', pivots, 'motive'
        else:
            return 'ambiguous', pivots, 'check diagonal'
    
    elif wave_count == 3:
        return '3-wave', pivots, 'corrective'
    
    elif wave_count > 5:
        # Possibly an extended wave or complex correction
        # Try re-counting with larger threshold
        return count_sub_waves(price_data, pivot_threshold * 1.5)
    
    elif wave_count < 3:
        # Insufficient structure --- try smaller threshold
        if pivot_threshold > MIN_THRESHOLD:
            return count_sub_waves(price_data, pivot_threshold * 0.75)
        else:
            return 'insufficient', pivots, 'unclear'
    
    else:  # wave_count == 4 (not valid in EW)
        return 'ambiguous', pivots, 'recheck threshold'
```

---

## 13. Risk Parameters

### 13.1 Stop Loss for Correction Trades

**Trading the end of a correction (entering with trend):**

| Pattern Completed | Stop Loss Level | Distance |
|---|---|---|
| Zigzag | Below/Above Wave C terminus - ATR buffer | Tight |
| Flat | Below/Above Wave C terminus - ATR buffer | Tight |
| Expanded Flat | Below/Above Wave C terminus - 1.5x ATR | Wider (volatile) |
| Triangle | Below/Above Wave E terminus - ATR buffer | Very tight |
| Double Zigzag | Below/Above Wave Y terminus - ATR buffer | Moderate |
| Combination | Below/Above final pattern terminus - ATR | Moderate to wide |

**Trading within a correction (Wave C of zigzag/flat):**

$$SL = P_B + k \times ATR(14) \quad \text{(for bearish correction C-wave short)}$$

where $k = 1.0$ for Forex, $k = 1.5$ for Crypto.

### 13.2 Position Sizing Adjustment

$$\text{Correction Position Size} = \text{Standard Size} \times R_{\text{adj}}$$

where:

| Trade Type | $R_{\text{adj}}$ | Reason |
|---|---|---|
| Post-correction trend entry | 1.0 | Standard --- high confidence |
| C-wave of zigzag | 0.7 | Counter-trend element |
| Post-triangle thrust | 0.9 | High probability but measure uncertainty |
| Within complex correction | 0.5 | High whipsaw risk |

### 13.3 Take Profit Levels for Correction Completion Trades

When entering at the end of a correction (expecting new impulse):

```
TP1 (40%): Wave 1 of new impulse = 38.2% retracement of the correction
TP2 (35%): Wave 3 target = 161.8% extension of new Wave 1
TP3 (25%): Full impulse completion = prior impulse high/low
```

### 13.4 Maximum Risk Per Correction Trade

$$R_{\text{max}} = \text{Account Balance} \times 0.01 \times C_{\text{correction}}$$

where $C_{\text{correction}}$ is the correction completion confidence (0.70--1.0).

This means maximum risk on a correction trade is **0.7%--1.0%** of account balance (lower than the standard 1%--2% for impulse wave trades).

---

## 14. Execution Flow

### 14.1 Correction Identification Algorithm

```
FUNCTION identify_correction(market_data, prior_impulse):

    // Step 1: Detect first counter-trend leg (potential Wave A)
    wave_a = detect_first_corrective_leg(market_data, prior_impulse)
    
    IF wave_a IS NULL:
        RETURN "NO_CORRECTION_YET"
    
    // Step 2: Count Wave A's internal structure
    a_structure = count_sub_waves(wave_a.data)
    
    // Step 3: Branch based on Wave A structure
    IF a_structure == "5-wave":
        // Zigzag path (or new impulse)
        possible_patterns = ["zigzag", "double_zigzag", "new_impulse"]
        
        // Wait for Wave B
        wave_b = detect_counter_move(market_data, wave_a)
        b_retrace = abs(wave_b.range) / abs(wave_a.range)
        
        IF b_retrace > 1.0:
            RETURN "WAVE_A_WAS_ACTUALLY_WAVE_1_OF_NEW_IMPULSE"
        
        IF 0.38 <= b_retrace <= 0.786:
            // Classic zigzag Wave B range
            // Wait for Wave C
            wave_c = detect_impulse_leg(market_data, wave_b, direction=wave_a.direction)
            
            IF wave_c.structure == "5-wave":
                RETURN identify_zigzag_completion(wave_a, wave_b, wave_c)
    
    ELIF a_structure == "3-wave":
        // Flat or Triangle path
        possible_patterns = ["flat", "triangle", "combination"]
        
        wave_b = detect_counter_move(market_data, wave_a)
        b_retrace = abs(wave_b.range) / abs(wave_a.range)
        
        IF b_retrace >= 0.80:
            // Flat path
            flat_type = classify_flat(wave_a, wave_b, b_retrace)
            
            // Wait for Wave C (5-wave structure)
            wave_c = detect_impulse_leg(market_data, wave_b, direction=wave_a.direction)
            
            IF wave_c.structure == "5-wave":
                RETURN identify_flat_completion(wave_a, wave_b, wave_c, flat_type)
        
        ELIF b_retrace < 0.80:
            // Possibly part of a triangle or combination
            // Need more waves to determine
            CONTINUE_MONITORING(possible_patterns=["triangle", "combination"])
```

### 14.2 Correction Trading Execution

```
FUNCTION trade_correction_completion(correction, market_data, account, config):

    // Step 1: Validate correction is complete
    completion = assess_correction_completion(correction, market_data)
    
    IF completion.confidence < config.min_confidence:
        RETURN "WAIT: Correction may not be complete"
    
    // Step 2: Determine entry
    trend_direction = correction.main_trend  // The larger trend direction
    
    IF trend_direction == "BULLISH":
        entry_type = "LONG"
        entry_price = market_data.ask  // Buy at ask
        sl_price = correction.terminus - (config.atr_multiplier * market_data.atr)
    ELSE:
        entry_type = "SHORT"
        entry_price = market_data.bid  // Sell at bid
        sl_price = correction.terminus + (config.atr_multiplier * market_data.atr)
    
    // Step 3: Calculate targets
    impulse_range = abs(prior_impulse.end - prior_impulse.start)
    correction_range = abs(correction.terminus - correction.start)
    
    tp1 = entry_price + (0.382 * correction_range) * direction_multiplier
    tp2 = entry_price + (0.618 * correction_range) * direction_multiplier
    tp3 = entry_price + impulse_range * direction_multiplier  // Full extension
    
    // Step 4: Calculate position size
    sl_distance = abs(entry_price - sl_price)
    rr_ratio = abs(tp1 - entry_price) / sl_distance
    
    IF rr_ratio < config.min_rr:
        RETURN "REJECTED: RR ratio below minimum"
    
    risk_amount = account.balance * config.risk_pct * completion.confidence
    position_size = risk_amount / (sl_distance * market_data.pip_value)
    
    // Step 5: Execute
    PLACE_ORDER(
        type = entry_type,
        size = position_size,
        stop_loss = sl_price,
        take_profits = [
            (tp1, 0.40),  // 40% at TP1
            (tp2, 0.35),  // 35% at TP2
            (tp3, 0.25),  // 25% at TP3
        ]
    )
    
    // Step 6: Monitor for invalidation
    MONITOR_FOR_INVALIDATION(
        condition = "Price exceeds correction.terminus by ATR",
        action = "CLOSE_POSITION with small loss"
    )
```

### 14.3 Complex Correction Handling

```
FUNCTION handle_complex_correction(market_data, initial_correction):
    
    // After initial correction (W) seems complete, monitor for X wave
    potential_x = detect_counter_move(market_data, initial_correction)
    
    IF potential_x IS DETECTED:
        x_retrace = abs(potential_x.range) / abs(initial_correction.range)
        
        IF x_retrace < 0.786:
            // Likely X wave of a complex correction
            LOG("Complex correction developing: W-X in progress")
            
            // Wait for Y wave
            potential_y = detect_next_correction(market_data, potential_x)
            
            IF potential_y.pattern == "TRIANGLE":
                // Triangle is the last pattern in a combination
                LOG("Triangle as Y wave --- correction likely ending after E")
                WAIT_FOR_TRIANGLE_COMPLETION(potential_y)
                TRADE_POST_TRIANGLE_THRUST()
            
            ELIF potential_y.is_complete:
                // Check if another X wave develops
                next_x = detect_counter_move(market_data, potential_y)
                
                IF next_x IS DETECTED:
                    LOG("Triple combination (WXYXZ) forming --- patience required")
                    // Wait for Z wave completion
                ELSE:
                    LOG("Double combination (WXY) complete")
                    TRADE_CORRECTION_COMPLETION(combined_correction)
        
        ELSE:
            // X retraces too much --- initial correction was probably not complete
            LOG("Re-evaluating: initial pattern may be incomplete")
            REASSESS_WAVE_COUNT()
```

---

## 15. References

### 15.1 Primary Sources

1. **Elliott, R.N.** (1938). *The Wave Principle*. Original monograph.
2. **Elliott, R.N.** (1946). *Nature's Law: The Secret of the Universe*.
3. **Frost, A.J. & Prechter, R.R.** (1978, 2017). *Elliott Wave Principle: Key to Market Behavior*. 11th Ed. New Classics Library. (Chapters 2--4 on corrective patterns)
4. **Neely, G.** (1988). *Mastering Elliott Wave*. Windsor Books. (Definitive work on corrective wave classification and rules)

### 15.2 Advanced Corrective Pattern References

5. **Prechter, R.R.** (2005). *Elliott Wave Principle* --- Applied to Corrections. Elliott Wave International Educational Series.
6. **Poser, S.W.** (2003). *Applying Elliott Wave Theory Profitably*. Wiley. (Chapter on corrective wave trading strategies)

### 15.3 Fibonacci and Corrective Patterns

7. **Boroden, C.** (2008). *Fibonacci Trading*. McGraw-Hill. (Fibonacci relationships within corrections)
8. **Miner, R.C.** (2009). *High Probability Trading Strategies*. Wiley. (Time and price Fibonacci analysis)
9. **Pesavento, L.** (1997). *Fibonacci Ratios with Pattern Recognition*. Traders Press.

### 15.4 Forex/Crypto Specific

10. **Balan, R.** (1989). *Elliott Wave Principle Applied to the Foreign Exchange Markets*. (Correction patterns in FX)
11. **Brown, C.** (2012). *Fibonacci Analysis* (Bloomberg Financial). (Modern Fibonacci applications)

### 15.5 Mathematical / Quantitative

12. **Mandelbrot, B.** (1982). *The Fractal Geometry of Nature*. W.H. Freeman. (Mathematical foundation for self-similar patterns)
13. **Peters, E.E.** (1994). *Fractal Market Analysis*. Wiley. (Fractal theory applied to financial markets)

---

## Document Cross-References

| Document | Path | Relationship |
|---|---|---|
| Overview | `00_overview.md` | Foundational concepts and wave hierarchy |
| Impulse Waves | `01_impulse_waves.md` | The motive waves that corrections correct |
| Fibonacci Targets | `03_fibonacci_targets.md` | Detailed Fibonacci calculations for corrections |
| Wave Counting Algorithm | `04_wave_counting_algorithm.md` | Automated pattern recognition |
| Harmonic Patterns | `../06_harmonic_patterns/` | Harmonic completions at correction termini |
| Price Action | `../07_price_action/` | Reversal patterns confirming correction completion |

---

*This document provides comprehensive detail on all corrective wave patterns for the Multi-Agent AI Trading System. Corrective waves are inherently more complex and varied than impulse waves, requiring sophisticated pattern recognition and multiple confirmation signals. The AI system should prioritize pattern completion confidence and Fibonacci confluence before entering correction-completion trades.*
