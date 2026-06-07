# Elliott Wave Theory --- Impulse Wave Patterns (Motive Waves)

## Document Metadata
| Field | Value |
|---|---|
| **Strategy ID** | EW-001 |
| **Category** | Axis 1 --- Trading Strategies |
| **Sub-Category** | Elliott Wave Theory --- Impulse Waves |
| **Applicable Markets** | Forex, Crypto |
| **Timeframes** | All (Multi-Timeframe) |
| **Complexity** | Advanced |
| **AI Suitability** | High |
| **Last Updated** | 2026-04-12 |

---

## Table of Contents
1. [Introduction to Impulse Waves](#1-introduction-to-impulse-waves)
2. [The Five-Wave Impulse Structure](#2-the-five-wave-impulse-structure)
3. [Iron Rules (Inviolable Rules)](#3-iron-rules-inviolable-rules)
4. [Guidelines (Tendencies)](#4-guidelines-tendencies)
5. [Detailed Wave-by-Wave Analysis](#5-detailed-wave-by-wave-analysis)
6. [Wave Extensions](#6-wave-extensions)
7. [Leading Diagonals](#7-leading-diagonals)
8. [Ending Diagonals](#8-ending-diagonals)
9. [Fibonacci Relationships Between Waves](#9-fibonacci-relationships-between-waves)
10. [Mathematical Models](#10-mathematical-models)
11. [Technical Conditions for AI Detection](#11-technical-conditions-for-ai-detection)
12. [Core Logic --- Entry/Exit for Each Wave Phase](#12-core-logic----entryexit-for-each-wave-phase)
13. [Risk Parameters](#13-risk-parameters)
14. [Execution Flow](#14-execution-flow)
15. [References](#15-references)

---

## 1. Introduction to Impulse Waves

Impulse waves (also called **motive waves**) are the driving force of market trends. They move in the direction of the trend of the next larger degree and always subdivide into **five waves**. Three of these sub-waves (1, 3, 5) are themselves motive, moving with the trend, while two (2, 4) are corrective, moving against it.

### 1.1 Defining Properties

An impulse wave must satisfy **all** of the following:
1. It subdivides into exactly 5 waves
2. Waves 1, 3, and 5 are motive (subdivide into 5)
3. Waves 2 and 4 are corrective (subdivide into 3)
4. The three Iron Rules are satisfied (see Section 3)
5. The overall wave moves in the direction of the trend at the next higher degree

### 1.2 Where Impulse Waves Appear

Impulse waves appear in the following positions within the Elliott Wave structure:

| Position | Context |
|---|---|
| Waves 1, 3, 5 | Within a larger impulse wave |
| Wave A | Within a zigzag corrective pattern |
| Wave C | Within a zigzag, flat, or expanded flat |
| Wave 1 or 5 of a diagonal | In contracting/expanding diagonals (as wedge-shaped impulse) |

---

## 2. The Five-Wave Impulse Structure

### 2.1 Visual Representation

**Bullish Impulse:**
```
                    (5)
                   / 
            (3)  /   
           /\  /    
     (1) /  \/      
      /\/  (4)      
     /  \           
    /   (2)         
   /                
Origin               
```

**Bearish Impulse:**
```
Origin
   \
    \   (2)
     \  /\
      \/  \   (4)
     (1)   \  /\
            \/  \
           (3)   \
                  \
                  (5)
```

### 2.2 Internal Structure Breakdown

| Wave | Direction | Internal Structure | Sub-waves | Character |
|---|---|---|---|---|
| **Wave 1** | With trend | Impulse (5-wave) | 5 | Initiating move |
| **Wave 2** | Counter-trend | Corrective (3-wave) | 3 | Retracement |
| **Wave 3** | With trend | Impulse (5-wave) | 5 | Strongest move |
| **Wave 4** | Counter-trend | Corrective (3-wave) | 3 | Consolidation |
| **Wave 5** | With trend | Impulse (5-wave) | 5 | Final push |

**Total sub-wave count:** $5 + 3 + 5 + 3 + 5 = 21$ (a Fibonacci number)

### 2.3 Wave Sequence Visualization (Detailed)

```
Complete Impulse Wave with Sub-Wave Decomposition:

Wave 1: [i] - [ii] - [iii] - [iv] - [v]          (5 sub-waves)
Wave 2: [a] - [b] - [c]                            (3 sub-waves)
Wave 3: [i] - [ii] - [iii] - [iv] - [v]           (5 sub-waves)
Wave 4: [a] - [b] - [c]                            (3 sub-waves)
Wave 5: [i] - [ii] - [iii] - [iv] - [v]           (5 sub-waves)

─────────────────────────────────────────────────
                                           [v](5)
                                          /
                              [iii]      [iv]
                     [v](3)  /    \     /
                    /       /      [v] /
           [iii]  [iv]    [ii]    
          /    \ /        /       
   [v](1)/     [iii]    [i]       
    /   [iv]  /                   [c](4)
[iii] /     [ii]              [b]/    \
   \ [ii]  /                  /       [a]
    /     [i]               [a]      /
 [i]/                              [b]
   /  [c](2)                     
  / [b]/                         
 /  / [a]                        
0 [a]/
```

---

## 3. Iron Rules (Inviolable Rules)

These three rules are **absolute**. If any is violated, the proposed wave count is **invalid** and must be rejected. There are no exceptions for standard impulse waves.

### 3.1 Rule 1: Wave 2 Never Retraces More Than 100% of Wave 1

**Formal Statement:**

$$|P_{\text{end}}^{(2)} - P_{\text{end}}^{(1)}| < |P_{\text{end}}^{(1)} - P_{\text{start}}^{(1)}|$$

**In plain terms:**
- In a **bullish** impulse: The low of Wave 2 must remain **above** the start of Wave 1
- In a **bearish** impulse: The high of Wave 2 must remain **below** the start of Wave 1

**Validation Logic:**
```python
def validate_rule_1(wave_1_start, wave_1_end, wave_2_end, direction):
    """
    Rule 1: Wave 2 cannot retrace more than 100% of Wave 1.
    
    Parameters:
        wave_1_start: Price at the origin of Wave 1
        wave_1_end:   Price at the terminus of Wave 1
        wave_2_end:   Price at the terminus of Wave 2
        direction:    'bullish' or 'bearish'
    
    Returns:
        bool: True if rule is satisfied, False if violated
    """
    if direction == 'bullish':
        # Wave 2 low must stay above Wave 1 origin
        return wave_2_end > wave_1_start
    else:
        # Wave 2 high must stay below Wave 1 origin
        return wave_2_end < wave_1_start
```

**Why this rule exists:** If Wave 2 fully retraces Wave 1, then what was labeled as "Wave 1" was not actually an impulse --- the market is still in the prior trend or correction.

**Practical note for Crypto:** In extremely volatile crypto markets, wicks can briefly penetrate the Wave 1 origin on lower timeframes. The convention is to use **closing prices** for rule validation in highly volatile instruments, though this is debated. Our system should flag such occurrences for human review.

### 3.2 Rule 2: Wave 3 Is Never the Shortest Among Waves 1, 3, and 5

**Formal Statement:**

$$\text{Range}_3 \geq \text{Range}_1 \quad \text{OR} \quad \text{Range}_3 \geq \text{Range}_5$$

More precisely, it is **not** the case that:

$$\text{Range}_3 < \text{Range}_1 \quad \text{AND} \quad \text{Range}_3 < \text{Range}_5$$

**In plain terms:** Wave 3 does not have to be the longest, but it can **never** be shorter than **both** Wave 1 and Wave 5.

**Validation Logic:**
```python
def validate_rule_2(wave_1_range, wave_3_range, wave_5_range):
    """
    Rule 2: Wave 3 is never the shortest of Waves 1, 3, and 5.
    
    Parameters:
        wave_1_range: Absolute price range of Wave 1
        wave_3_range: Absolute price range of Wave 3
        wave_5_range: Absolute price range of Wave 5
    
    Returns:
        bool: True if rule is satisfied, False if violated
    """
    # Wave 3 is the shortest only if it is shorter than BOTH Wave 1 and Wave 5
    is_shortest = (wave_3_range < wave_1_range) and (wave_3_range < wave_5_range)
    return not is_shortest
```

**Important Implication:** This rule constrains Wave 5's maximum length when Wave 1 is longer than Wave 3. Specifically:

$$\text{If } \text{Range}_1 > \text{Range}_3, \text{ then } \text{Range}_5 \leq \text{Range}_3$$

This is critical for setting Wave 5 price targets and stop losses.

**Practical note:** In both Forex and Crypto, Wave 3 is **usually** the longest wave. The scenario where Wave 3 is not the longest (but still not the shortest) occurs most often when Wave 5 extends, which is relatively common in crypto due to retail FOMO.

### 3.3 Rule 3: Wave 4 Never Overlaps the Price Territory of Wave 1

**Formal Statement (Bullish):**

$$P_{\text{low}}^{(4)} > P_{\text{high}}^{(1)}$$

**Formal Statement (Bearish):**

$$P_{\text{high}}^{(4)} < P_{\text{low}}^{(1)}$$

**In plain terms:**
- In a **bullish** impulse: The lowest point of Wave 4 must stay **above** the highest point of Wave 1
- In a **bearish** impulse: The highest point of Wave 4 must stay **below** the lowest point of Wave 1

**Validation Logic:**
```python
def validate_rule_3(wave_1_end, wave_4_low, wave_4_high, direction):
    """
    Rule 3: Wave 4 does not overlap Wave 1's price territory.
    
    Parameters:
        wave_1_end:  Price at the terminus (high/low) of Wave 1
        wave_4_low:  Lowest price during Wave 4 (bullish)
        wave_4_high: Highest price during Wave 4 (bearish)
        direction:   'bullish' or 'bearish'
    
    Returns:
        bool: True if rule is satisfied, False if violated
    """
    if direction == 'bullish':
        # Wave 4 low must stay above Wave 1 high
        return wave_4_low > wave_1_end
    else:
        # Wave 4 high must stay below Wave 1 low
        return wave_4_high < wave_1_end
```

**Exception --- Diagonal Triangles:** In leading and ending diagonal patterns, Wave 4 **is allowed** to overlap Wave 1. This is a key distinguishing feature of diagonals (see Sections 7 and 8).

**Practical note for Crypto:** On exchanges with thin order books, flash wicks can temporarily violate this rule. The system should distinguish between:
- A sustained break (multiple closes in Wave 1 territory) --- rule violation, count invalid
- A momentary wick (single candle, immediate recovery) --- potential diagonal or noise

---

## 4. Guidelines (Tendencies)

Unlike the Iron Rules, guidelines are **strong tendencies** that are observed in the majority of cases but are not absolute requirements. Violations of guidelines do not invalidate a wave count but may reduce its probability.

### 4.1 Wave 2 Retracement Guidelines

**Typical retracement: 50%--61.8% of Wave 1**

$$P_{\text{target}}^{(2)} = P_{\text{end}}^{(1)} - r \times (P_{\text{end}}^{(1)} - P_{\text{start}}^{(1)}) \quad \text{where } r \in [0.50, 0.618]$$

| Market | Common Wave 2 Retracement | Notes |
|---|---|---|
| Forex (Majors) | 50%--61.8% | Very consistent |
| Forex (Crosses) | 50%--78.6% | More volatile, deeper retracements |
| Crypto (BTC) | 61.8%--78.6% | Fear-driven deeper pullbacks |
| Crypto (Altcoins) | 61.8%--88.6% | Extreme fear, near-rule-violations common |

**Wave 2 correction types:**
- Most commonly a **zigzag** (sharp, deep correction)
- Can be a **double zigzag** in volatile markets
- Rarely a flat or triangle (these are more common for Wave 4)

### 4.2 Wave 3 Extension Guidelines

**Typical extension: 161.8%--261.8% of Wave 1**

$$P_{\text{target}}^{(3)} = P_{\text{end}}^{(2)} + e \times (P_{\text{end}}^{(1)} - P_{\text{start}}^{(1)}) \quad \text{where } e \in [1.618, 2.618]$$

| Market | Common Wave 3 Extension | Notes |
|---|---|---|
| Forex (Majors) | 161.8%--200% | Well-behaved |
| Forex (Volatile pairs) | 161.8%--261.8% | GBP pairs often extend more |
| Crypto (BTC) | 200%--261.8% | Strong momentum |
| Crypto (Altcoins) | 261.8%--423.6% | Extreme extensions during alt seasons |

**Wave 3 characteristics:**
- **Highest volume** of all impulse waves
- Often contains a **"third of a third"** (sub-wave iii of Wave 3), which is the most powerful price movement
- Usually shows momentum indicator confirmation (RSI > 70 in uptrend, < 30 in downtrend)
- News events often cluster around Wave 3 (confirming the psychological narrative)

### 4.3 Wave 4 Retracement Guidelines

**Typical retracement: 38.2% of Wave 3**

$$P_{\text{target}}^{(4)} = P_{\text{end}}^{(3)} - r \times (P_{\text{end}}^{(3)} - P_{\text{end}}^{(2)}) \quad \text{where } r \approx 0.382$$

| Market | Common Wave 4 Retracement | Notes |
|---|---|---|
| Forex | 23.6%--38.2% of Wave 3 | Shallow, time-consuming |
| Crypto | 38.2%--50% of Wave 3 | Slightly deeper in crypto |

**Wave 4 correction types:**
- Most commonly a **flat**, **triangle**, or **combination**
- Alternation Principle: if Wave 2 was a sharp zigzag, Wave 4 tends to be a sideways pattern
- Often the most time-consuming wave (tests patience)
- Volume diminishes during Wave 4

### 4.4 Wave 5 Guidelines

**Typical length: 61.8%--100% of Wave 1**

$$P_{\text{target}}^{(5)} = P_{\text{end}}^{(4)} + e \times (P_{\text{end}}^{(1)} - P_{\text{start}}^{(1)}) \quad \text{where } e \in [0.618, 1.0]$$

**Alternative: Wave 5 = 61.8% of Wave 1-to-3 net distance**

$$P_{\text{target}}^{(5)} = P_{\text{end}}^{(4)} + 0.618 \times (P_{\text{end}}^{(3)} - P_{\text{start}}^{(1)})$$

| Market | Common Wave 5 Behavior | Notes |
|---|---|---|
| Forex | Often equals Wave 1 | Most common relationship |
| Crypto | Often extends (161.8% of Wave 1) | FOMO-driven blow-off tops |

**Wave 5 characteristics:**
- **Momentum divergence**: RSI/MACD make lower highs while price makes higher highs (bullish) or higher lows while price makes lower lows (bearish)
- Volume is lower than Wave 3 (in equity markets; crypto can be an exception)
- Often shows a **wedge/diagonal** pattern (ending diagonal)
- Retail participation peaks; smart money exits

### 4.5 Guideline of Alternation (Detailed)

| If Wave 2 is... | Then Wave 4 tends to be... |
|---|---|
| Zigzag (5-3-5), sharp | Flat (3-3-5) or Triangle (3-3-3-3-3), sideways |
| Deep (>61.8%) | Shallow (<38.2%) |
| Fast (few bars) | Slow (many bars) |
| Simple (single pattern) | Complex (combination) |
| Flat or combination | Zigzag (sharp) |
| Shallow (<50%) | Deep (>50%) |

### 4.6 Guideline of Equality

When Wave 3 extends (most common case), Waves 1 and 5 tend toward **equality**:

$$\text{Range}_5 \approx \text{Range}_1$$

Or, if not exactly equal, Wave 5 = 61.8% of Wave 1:

$$\text{Range}_5 \approx 0.618 \times \text{Range}_1$$

### 4.7 Guideline of Wave 4 Depth

Wave 4 commonly retraces to the territory of sub-wave iv of Wave 3 (the previous fourth wave of one lesser degree). This provides an additional target zone for Wave 4's terminus.

---

## 5. Detailed Wave-by-Wave Analysis

### 5.1 Wave 1 --- The Initiator

**Character:**
Wave 1 is the beginning of a new trend direction. It is often the hardest wave to identify in real-time because:
- The prior trend is still considered active by most participants
- Fundamentals have not yet shifted (or the shift is not yet recognized)
- Volume is moderate at best
- Many technicians view it as merely a correction of the prior trend

**Internal Structure:**
- Subdivides into 5 sub-waves: i-ii-iii-iv-v
- Sub-wave iii is usually the strongest portion
- Volume tends to increase during sub-waves iii and v

**Identification Criteria for AI:**
```python
def detect_wave_1(price_data, prior_trend):
    """
    Conditions that suggest a Wave 1 is forming:
    1. Five-wave subdivision visible on lower timeframe
    2. Break of significant trendline from prior trend
    3. Volume expansion from recent base
    4. Momentum shift (e.g., MACD crossover)
    5. Prior trend showed 5-wave completion or ABC correction
    """
    conditions = {
        'five_wave_subdivision': check_five_wave_structure(price_data),
        'trendline_break': check_trendline_break(price_data, prior_trend),
        'volume_expansion': check_volume_increase(price_data, threshold=1.2),
        'momentum_shift': check_macd_crossover(price_data),
        'prior_completion': check_prior_trend_completion(price_data, prior_trend),
    }
    confidence = sum(conditions.values()) / len(conditions)
    return confidence >= 0.6  # At least 3 of 5 conditions met
```

**Fibonacci Relationships:**
- Wave 1 has no prior wave to measure against (it is the base measurement)
- Its range becomes the **reference** for all subsequent wave targets

**Trading Wave 1:**
- Generally **not traded** because identification is difficult in real-time
- Exception: if there is strong evidence the prior trend has completed (five waves down + divergence), an aggressive entry can be taken
- If entered, the stop loss is below the prior swing low (start of Wave 1)

### 5.2 Wave 2 --- The Test of Conviction

**Character:**
Wave 2 is a corrective wave that retraces a significant portion of Wave 1. It represents the market's doubt about the new trend. Participants from the old trend see this as a resumption of their expected direction.

**Internal Structure:**
- Subdivides into 3 sub-waves (a-b-c)
- Most commonly takes the form of a **zigzag** (5-3-5)
- Can also be a **double zigzag** (5-3-5-x-5-3-5) in volatile markets
- Rarely a flat (3-3-5)

**Fibonacci Retracement Levels:**

| Level | Probability | Notes |
|---|---|---|
| 38.2% | Low (~15%) | Only in very strong trends |
| 50.0% | Medium (~30%) | Common in Forex majors |
| 61.8% | High (~35%) | Most common level |
| 78.6% | Medium (~15%) | Common in Crypto |
| 88.6% | Low (~5%) | Near invalidation, aggressive |

**Key Formulas:**

$$P_{\text{W2\_target\_50}} = P_{\text{W1\_end}} - 0.500 \times (P_{\text{W1\_end}} - P_{\text{W1\_start}})$$

$$P_{\text{W2\_target\_618}} = P_{\text{W1\_end}} - 0.618 \times (P_{\text{W1\_end}} - P_{\text{W1\_start}})$$

**Identification Criteria for AI:**
```python
def detect_wave_2_completion(wave_1, current_price, indicators):
    """
    Conditions suggesting Wave 2 is complete:
    1. Price at 50%-61.8% Fibonacci retracement of Wave 1
    2. Three-wave corrective structure visible
    3. Momentum indicator shows bullish divergence
    4. Volume diminishes toward end of Wave 2
    5. Key support/demand zone confluence
    6. Reversal candlestick pattern (hammer, engulfing, etc.)
    """
    wave_1_range = abs(wave_1['end'] - wave_1['start'])
    retracement = abs(current_price - wave_1['end']) / wave_1_range
    
    conditions = {
        'fib_zone': 0.50 <= retracement <= 0.786,
        'three_wave': check_three_wave_structure(current_price),
        'divergence': check_bullish_divergence(indicators['rsi']),
        'volume_decline': check_volume_decline(indicators['volume']),
        'support_zone': check_support_confluence(current_price),
        'reversal_candle': check_reversal_pattern(current_price),
    }
    
    score = sum(conditions.values()) / len(conditions)
    return score, conditions
```

### 5.3 Wave 3 --- The Power Move

**Character:**
Wave 3 is typically the **longest and most powerful** wave in an impulse sequence. It represents the phase where the new trend gains broad recognition, and participation expands dramatically.

**Internal Structure:**
- Subdivides into 5 sub-waves: i-ii-iii-iv-v
- Sub-wave iii of Wave 3 is often the single most powerful price movement in the entire sequence (the "third of a third")
- **Never the shortest** of Waves 1, 3, and 5 (Iron Rule 2)

**Fibonacci Extension Levels (measured from Wave 1):**

| Extension | Probability | Notes |
|---|---|---|
| 100.0% (Wave 3 = Wave 1) | Low (~10%) | Minimum expectation |
| 127.2% | Low (~10%) | Below typical |
| 161.8% | High (~35%) | Most common target |
| 200.0% | Medium (~25%) | Strong momentum |
| 261.8% | Medium (~15%) | Extended Wave 3 |
| 423.6% | Low (~5%) | Extremely extended (crypto) |

**Key Formulas:**

$$P_{\text{W3\_target\_1618}} = P_{\text{W2\_end}} + 1.618 \times (P_{\text{W1\_end}} - P_{\text{W1\_start}})$$

$$P_{\text{W3\_target\_2618}} = P_{\text{W2\_end}} + 2.618 \times (P_{\text{W1\_end}} - P_{\text{W1\_start}})$$

**Volume Signature:**
- Significantly higher than Wave 1
- Expanding volume during sub-waves i through iii
- The highest single-bar volume often occurs during sub-wave iii of Wave 3
- Volume may moderate in sub-waves iv and v but remains elevated

**Momentum Signature:**
- RSI reaches extreme levels (>70 bullish, <30 bearish) during sub-wave iii
- MACD histogram peaks during Wave 3
- No divergence between price and momentum (divergence appears only in Wave 5)

**Wave 3 Extension and Price Gaps:**
- Price gaps are common during Wave 3 (Forex: breakaway gaps at session openings; Crypto: rapid moves through thin order book levels)
- These gaps often appear in the sub-wave iii position
- Gaps within Wave 3 are typically **not filled** during the impulse

**Identification Criteria for AI:**
```python
def detect_wave_3_in_progress(wave_1, wave_2, current_data):
    """
    Conditions confirming Wave 3 is underway:
    1. Price has exceeded Wave 1 terminus (break of resistance/support)
    2. Volume is expanding beyond Wave 1 levels
    3. Momentum indicators reaching extremes without divergence
    4. Five-wave subdivision developing on lower timeframe
    5. Breadth expansion (for multi-asset contexts)
    """
    conditions = {
        'break_wave_1': (current_data['price'] > wave_1['end'] if 
                         wave_1['direction'] == 'up' else 
                         current_data['price'] < wave_1['end']),
        'volume_expansion': current_data['volume'] > wave_1['avg_volume'] * 1.5,
        'momentum_extreme': abs(current_data['rsi'] - 50) > 20,
        'no_divergence': not check_divergence(current_data),
        'lower_tf_impulse': check_five_wave_structure(current_data['lower_tf']),
    }
    
    return all(conditions.values())
```

### 5.4 Wave 4 --- The Complex Consolidation

**Character:**
Wave 4 is a corrective pause that often frustrates traders with its complexity and duration. It represents profit-taking by early participants while the broader trend conviction remains intact.

**Internal Structure:**
- Subdivides into 3 sub-waves (or more complex patterns)
- Commonly takes the form of: **flat**, **triangle**, **double/triple three**
- Alternation: if Wave 2 was a simple sharp correction, Wave 4 tends to be complex and sideways
- **Must not overlap Wave 1 territory** (Iron Rule 3)

**Fibonacci Retracement Levels (of Wave 3):**

| Level | Probability | Notes |
|---|---|---|
| 23.6% | Medium (~20%) | Very strong trend |
| 38.2% | High (~40%) | Most common level |
| 50.0% | Medium (~25%) | Common in crypto |
| 61.8% | Low (~10%) | Deep correction, near overlap |
| Beyond 61.8% | Very Low (~5%) | Likely diagonal or miscount |

**Key Formulas:**

$$P_{\text{W4\_target\_382}} = P_{\text{W3\_end}} - 0.382 \times (P_{\text{W3\_end}} - P_{\text{W2\_end}})$$

**Additional Target: Previous Wave iv of one lesser degree:**

$$P_{\text{W4\_target\_alt}} = P_{\text{sub-iv of W3\_end}}$$

**Volume Signature:**
- Volume diminishes significantly compared to Wave 3
- Trading ranges narrow
- Volume spikes may occur at the end of Wave 4 as a "shakeout" before Wave 5

**Time Characteristics:**
- Wave 4 often takes the longest **time** of any wave in the impulse
- In Forex: days to weeks for intraday setups, weeks to months for daily setups
- In Crypto: proportionally shorter but still the most time-consuming

**Identification Criteria for AI:**
```python
def detect_wave_4_completion(wave_1, wave_3, current_price, indicators):
    """
    Conditions suggesting Wave 4 is complete:
    1. Price at 38.2% Fibonacci retracement of Wave 3
    2. Corrective pattern complete (flat, triangle, or combo)
    3. No overlap with Wave 1 territory
    4. Volume contraction followed by expansion
    5. Time proportionality (Wave 4 duration roughly proportional)
    6. Alternation satisfied relative to Wave 2
    """
    wave_3_range = abs(wave_3['end'] - wave_3['start'])
    retracement = abs(current_price - wave_3['end']) / wave_3_range
    
    # Check non-overlap with Wave 1
    if wave_3['direction'] == 'up':
        no_overlap = current_price > wave_1['end']
    else:
        no_overlap = current_price < wave_1['end']
    
    conditions = {
        'fib_zone': 0.236 <= retracement <= 0.618,
        'corrective_complete': check_corrective_pattern_complete(current_price),
        'no_overlap': no_overlap,
        'volume_pattern': check_volume_contraction_expansion(indicators['volume']),
        'time_proportion': check_time_proportion(wave_3, current_wave_4),
        'alternation': check_alternation(wave_2_type, current_wave_4_type),
    }
    
    score = sum(conditions.values()) / len(conditions)
    return score, conditions
```

### 5.5 Wave 5 --- The Final Push

**Character:**
Wave 5 is the final leg of the impulse. It often produces the highest (or lowest) price of the entire move but does so with **diminishing momentum**, creating divergences that signal the impending correction.

**Internal Structure:**
- Subdivides into 5 sub-waves: i-ii-iii-iv-v
- Can be an **ending diagonal** (especially when the entire impulse has been strong)
- Sometimes truncated (fails to exceed Wave 3's extreme)

**Fibonacci Extension Levels:**

**Method 1: Wave 5 relative to Wave 1 (from Wave 4 terminus):**

| Extension | Probability | Notes |
|---|---|---|
| 61.8% of Wave 1 | Medium (~25%) | When Wave 3 extended |
| 100% of Wave 1 | High (~35%) | Equality guideline |
| 161.8% of Wave 1 | Medium (~20%) | Extended Wave 5 |
| 200%+ of Wave 1 | Low (~10%) | Blow-off top (crypto) |

**Method 2: Wave 5 = 61.8% of Wave 1-to-3 net:**

$$P_{\text{W5\_target}} = P_{\text{W4\_end}} + 0.618 \times (P_{\text{W3\_end}} - P_{\text{W1\_start}})$$

**Divergence Patterns (Critical for AI Detection):**

| Indicator | Divergence in Wave 5 (Bullish Impulse) |
|---|---|
| RSI | Price makes new high, RSI makes lower high |
| MACD Histogram | Price makes new high, MACD histogram makes lower peak |
| OBV | Price makes new high, OBV fails to confirm |
| Volume | Price makes new high, volume is lower than Wave 3 |

**Truncated Wave 5 (Failure):**
A truncated fifth wave occurs when Wave 5 fails to exceed the extreme of Wave 3. This signals extreme weakness (in uptrend) or strength (in downtrend) and typically leads to a sharp correction.

$$\text{Truncation condition: } P_{\text{W5\_end}} < P_{\text{W3\_end}} \quad \text{(bullish impulse)}$$

**Identification Criteria for AI:**
```python
def detect_wave_5_completion(wave_1, wave_3, wave_4, current_data):
    """
    Conditions suggesting Wave 5 is complete:
    1. Price reached 61.8%-100% extension of Wave 1 from Wave 4
    2. Five-wave subdivision complete on lower timeframe
    3. RSI divergence present (price vs. RSI)
    4. MACD divergence present
    5. Volume lower than Wave 3 peak
    6. Approaching or touching channel line
    """
    wave_1_range = abs(wave_1['end'] - wave_1['start'])
    wave_5_range = abs(current_data['price'] - wave_4['end'])
    extension = wave_5_range / wave_1_range
    
    conditions = {
        'fib_target_reached': 0.618 <= extension <= 2.618,
        'five_wave_complete': check_five_wave_structure(current_data['lower_tf']),
        'rsi_divergence': check_bearish_divergence(current_data['rsi'], current_data['price']),
        'macd_divergence': check_bearish_divergence(current_data['macd'], current_data['price']),
        'volume_decline': current_data['volume'] < wave_3['peak_volume'],
        'channel_touch': check_channel_touch(wave_1, wave_3, current_data['price']),
    }
    
    score = sum(conditions.values()) / len(conditions)
    return score, conditions
```

---

## 6. Wave Extensions

### 6.1 Definition

A wave **extension** occurs when one of the three motive waves (1, 3, or 5) is significantly longer than the other two and itself subdivides into an elongated five-wave pattern that may be as large as the overall impulse.

### 6.2 Which Wave Extends?

| Market | Most Common Extension | Frequency | Notes |
|---|---|---|---|
| **Equities** | Wave 3 | ~60% | Classic extension |
| **Forex (Majors)** | Wave 3 | ~55% | Most common |
| **Forex (Majors)** | Wave 5 | ~25% | Second most common |
| **Forex (Majors)** | Wave 1 | ~20% | Least common |
| **Crypto (BTC)** | Wave 3 | ~45% | Strong momentum phase |
| **Crypto (BTC)** | Wave 5 | ~35% | FOMO blow-off common |
| **Crypto (Altcoins)** | Wave 5 | ~40% | Retail FOMO dominates |
| **Crypto (Altcoins)** | Wave 3 | ~40% | Equally common |
| **Crypto (Altcoins)** | Wave 1 | ~20% | New narrative launches |

### 6.3 Extended Wave 3

The most common extension. The five sub-waves of Wave 3 are clearly visible and the total range of Wave 3 is typically 161.8%--261.8% of Wave 1.

```
Extended Wave 3:
                                    (5)
                                   /
                            [v]  /
                     (3)   /   (4)
                    /    [iv] /
            [iii] /     /   /
           /    [ii]  /
    (1)  /     /    /
     / [i]   /   /
    /       /  /
   /  (2) / /
  /      //
 /      /
Origin
```

**Fibonacci targets for extended Wave 3:**

$$P_{\text{W3}} = P_{\text{W2\_end}} + k \times \text{Range}_1, \quad k \in \{1.618, 2.000, 2.618, 3.236, 4.236\}$$

### 6.4 Extended Wave 5

More common in crypto markets. The five sub-waves of Wave 5 are clearly visible and the total range exceeds that of Wave 3.

```
Extended Wave 5:
                                              [v](5)
                                             /
                                      [iii] /
                                     /    [iv]
                              [i]  /     /
                    (3)      /  [ii]   /
                   /  \    /        /
            (1)  /    (4)/       /
             /  /       /      /
            /  /       /     /
           /  (2)    /    /
          /         /   /
         /         /  /
        /         / /
       /         //
      /         /
Origin
```

**Fibonacci targets for extended Wave 5:**

$$P_{\text{W5}} = P_{\text{W4\_end}} + k \times \text{Range}_1, \quad k \in \{1.618, 2.618, 4.236\}$$

Or:

$$P_{\text{W5}} = P_{\text{W4\_end}} + k \times (P_{\text{W3\_end}} - P_{\text{W1\_start}}), \quad k \in \{0.618, 1.000, 1.618\}$$

### 6.5 Extension of an Extension

Sometimes the extended wave itself contains an extension (e.g., sub-wave iii of an extended Wave 3 is itself extended). This creates a "nested extension" and can produce extremely long, powerful price moves. This is particularly common in crypto during parabolic phases.

### 6.6 The "Double Retracement" After Extended Wave 5

When Wave 5 extends, a strong guideline holds: the subsequent correction will initially retrace to the beginning of the extension (sub-wave i of the extended Wave 5), then bounce, and then continue lower. This produces a characteristic "double retracement" pattern.

---

## 7. Leading Diagonals

### 7.1 Definition

A **leading diagonal** is a type of motive wave that appears in the **Wave 1** position (or the Wave A position of a zigzag). It has a wedge shape and its internal structure differs from a standard impulse.

### 7.2 Structure

| Sub-Wave | Standard Impulse | Leading Diagonal (Common) | Leading Diagonal (Rare) |
|---|---|---|---|
| Wave 1 | 5-wave impulse | 5-wave impulse | 3-wave corrective |
| Wave 2 | 3-wave corrective | 3-wave corrective | 3-wave corrective |
| Wave 3 | 5-wave impulse | 5-wave impulse | 3-wave corrective |
| Wave 4 | 3-wave corrective | 3-wave corrective | 3-wave corrective |
| Wave 5 | 5-wave impulse | 5-wave impulse | 3-wave corrective |

**Key features:**
- Wave 4 **overlaps** Wave 1 (exception to Iron Rule 3 for standard impulse)
- The pattern forms a **contracting wedge** (converging trendlines)
- Waves 1 and 3 are channeled between converging upper and lower trendlines

```
Leading Diagonal (Bullish):

        (5)
       / |
  (3)/  (4)
   /\ /  |
(1)/ X   |
 /  (2)\  |
/       \ |
Origin    \_  (Note: Wave 4 overlaps Wave 1)
```

### 7.3 Fibonacci Relationships in Leading Diagonals

$$\text{Range}_3 \approx 0.618 \times \text{Range}_1$$

$$\text{Range}_5 \approx 0.618 \times \text{Range}_3$$

Wave 2 retracement: 66%--81% of Wave 1
Wave 4 retracement: 66%--81% of Wave 3

### 7.4 Trading Leading Diagonals

**Signal:** After a leading diagonal completes (as Wave 1 or Wave A), the subsequent correction (Wave 2 or Wave B) should retrace deeply, followed by an explosive Wave 3 or Wave C.

```
Entry:   After Wave 2 correction of the leading diagonal is complete
SL:      Below the origin of the diagonal
Target:  Wave 3 = 161.8%-261.8% extension (often overperforms due to pent-up energy)
RR:      Typically 4:1+ (excellent setup)
```

### 7.5 AI Detection Logic

```python
def detect_leading_diagonal(pivots, direction):
    """
    Conditions for leading diagonal:
    1. Five-wave structure present
    2. Wave 4 overlaps Wave 1 price territory
    3. Converging trendlines (upper and lower)
    4. Each successive wave is shorter than the previous
    5. Appears in Wave 1 or Wave A position only
    """
    wave_ranges = [abs(pivots[i+1] - pivots[i]) for i in range(5)]
    
    conditions = {
        'five_waves': len(pivots) == 6,  # 6 points = 5 waves
        'wave_4_overlaps_1': check_overlap(pivots[1], pivots[4], direction),
        'converging_lines': check_converging_trendlines(pivots),
        'decreasing_ranges': (wave_ranges[0] > wave_ranges[2] > wave_ranges[4]),
        'position_valid': check_position_is_wave_1_or_A(pivots),
    }
    
    return all(conditions.values())
```

---

## 8. Ending Diagonals

### 8.1 Definition

An **ending diagonal** is a type of motive wave that appears in the **Wave 5** position (or the Wave C position of a correction). Like a leading diagonal, it has a wedge shape, but it signals the **exhaustion** of the larger trend.

### 8.2 Structure

| Sub-Wave | Ending Diagonal |
|---|---|
| Wave 1 | 3-wave corrective (a-b-c) |
| Wave 2 | 3-wave corrective (a-b-c) |
| Wave 3 | 3-wave corrective (a-b-c) |
| Wave 4 | 3-wave corrective (a-b-c) |
| Wave 5 | 3-wave corrective (a-b-c) |

**Internal structure: 3-3-3-3-3** (all sub-waves are corrective threes)

**Key features:**
- Wave 4 **overlaps** Wave 1 (exception to Iron Rule 3)
- Pattern forms a **contracting wedge** (most common) or **expanding wedge** (rare)
- Volume diminishes progressively
- Momentum divergence is extreme
- Often called a "rising wedge" (bullish) or "falling wedge" (bearish) in classical TA

```
Ending Diagonal (Bullish, in Wave 5 position):

          _____(5)
         / ___/
   (3)  / / (4)
   /\  / /  /\
(1)/ \/ /  /  \
 /  (2)/  /    \
/     /  /      
     (Wave 4 overlaps Wave 1)
```

### 8.3 Contracting vs. Expanding Endings

| Type | Frequency | Trendline Shape | Post-Diagonal Move |
|---|---|---|---|
| Contracting | ~90% | Converging | Sharp and fast |
| Expanding | ~10% | Diverging | Even more aggressive reversal |

### 8.4 Fibonacci Relationships in Ending Diagonals

$$\text{Range}_3 \approx 0.618 \times \text{Range}_1$$

$$\text{Range}_5 \approx 0.618 \times \text{Range}_3 \quad \text{(contracting)}$$

Wave 2: 66%--81% of Wave 1
Wave 4: 66%--81% of Wave 3

### 8.5 Trading Ending Diagonals

**This is one of the highest-probability reversal setups in Elliott Wave analysis.**

```
Signal:  Ending diagonal completes in Wave 5 position
Entry:   Short (bullish diagonal) or Long (bearish diagonal) at completion
         OR after price breaks below the lower trendline (confirmation)
SL:      Above Wave 5 terminus + buffer (ATR-based)
Target:  At minimum, the origin of the diagonal (Wave 4 of the larger degree)
         Often retraces to 61.8% of the entire impulse
RR:      Typically 3:1 to 5:1+
```

**Post-Diagonal Price Action:**
After an ending diagonal completes, price typically retraces to the origin of the diagonal **very quickly** (often in less time than the diagonal took to form). This creates an excellent risk/reward opportunity.

### 8.6 AI Detection Logic

```python
def detect_ending_diagonal(pivots, wave_position, direction):
    """
    Conditions for ending diagonal:
    1. Five-wave structure where ALL sub-waves are 3-wave (a-b-c)
    2. Wave 4 overlaps Wave 1
    3. Converging trendlines (contracting) or diverging (expanding)
    4. Appears in Wave 5 or Wave C position only
    5. Volume diminishes progressively
    6. Momentum divergence is extreme
    """
    conditions = {
        'five_waves': len(pivots) == 6,
        'all_three_wave': all(check_three_wave(sub) for sub in get_subwaves(pivots)),
        'wave_4_overlaps_1': check_overlap(pivots[1], pivots[4], direction),
        'wedge_shape': check_wedge_trendlines(pivots),
        'position_valid': wave_position in ['wave_5', 'wave_c'],
        'volume_declining': check_progressive_volume_decline(pivots),
        'momentum_divergence': check_extreme_divergence(pivots),
    }
    
    confidence = sum(conditions.values()) / len(conditions)
    is_diagonal = confidence >= 0.71  # At least 5 of 7 conditions
    
    return is_diagonal, confidence, conditions
```

---

## 9. Fibonacci Relationships Between Waves

### 9.1 Complete Fibonacci Ratio Table

| Relationship | Ratio | Formula | Probability |
|---|---|---|---|
| **Wave 2 / Wave 1** | 0.382 | $\text{W2} = 0.382 \times \text{W1}$ | 15% |
| | 0.500 | $\text{W2} = 0.500 \times \text{W1}$ | 30% |
| | 0.618 | $\text{W2} = 0.618 \times \text{W1}$ | 35% |
| | 0.786 | $\text{W2} = 0.786 \times \text{W1}$ | 15% |
| | 0.886 | $\text{W2} = 0.886 \times \text{W1}$ | 5% |
| **Wave 3 / Wave 1** | 1.000 | $\text{W3} = 1.000 \times \text{W1}$ | 10% |
| | 1.272 | $\text{W3} = 1.272 \times \text{W1}$ | 10% |
| | 1.618 | $\text{W3} = 1.618 \times \text{W1}$ | 35% |
| | 2.000 | $\text{W3} = 2.000 \times \text{W1}$ | 20% |
| | 2.618 | $\text{W3} = 2.618 \times \text{W1}$ | 15% |
| | 4.236 | $\text{W3} = 4.236 \times \text{W1}$ | 5% (crypto) |
| **Wave 4 / Wave 3** | 0.236 | $\text{W4} = 0.236 \times \text{W3}$ | 15% |
| | 0.382 | $\text{W4} = 0.382 \times \text{W3}$ | 40% |
| | 0.500 | $\text{W4} = 0.500 \times \text{W3}$ | 25% |
| | 0.618 | $\text{W4} = 0.618 \times \text{W3}$ | 15% |
| **Wave 5 / Wave 1** | 0.382 | $\text{W5} = 0.382 \times \text{W1}$ | 5% |
| | 0.618 | $\text{W5} = 0.618 \times \text{W1}$ | 25% |
| | 1.000 | $\text{W5} = 1.000 \times \text{W1}$ | 35% |
| | 1.618 | $\text{W5} = 1.618 \times \text{W1}$ | 20% |
| | 2.618 | $\text{W5} = 2.618 \times \text{W1}$ | 10% (crypto) |
| **Wave 5 / (W1-to-W3 net)** | 0.382 | $\text{W5} = 0.382 \times (P_{\text{W3}} - P_{\text{W1\_start}})$ | 15% |
| | 0.618 | $\text{W5} = 0.618 \times (P_{\text{W3}} - P_{\text{W1\_start}})$ | 35% |
| | 1.000 | $\text{W5} = 1.000 \times (P_{\text{W3}} - P_{\text{W1\_start}})$ | 20% |

### 9.2 Time Relationships

Fibonacci time relationships are less reliable than price relationships but still informative:

| Relationship | Ratio | Notes |
|---|---|---|
| Wave 2 time / Wave 1 time | 0.382--0.618 | Sharp corrections are faster |
| Wave 3 time / Wave 1 time | 1.000--1.618 | Similar or longer duration |
| Wave 4 time / Wave 3 time | 0.618--1.618 | Often the longest in time |
| Wave 5 time / Wave 1 time | 0.618--1.000 | Similar duration to Wave 1 |

### 9.3 Channel Relationships

Elliott Wave channels provide additional validation:

**Base Channel:** Connect the origin of Wave 1 and the terminus of Wave 2. Draw a parallel through the terminus of Wave 1.

$$\text{Channel Upper (bullish)} = \text{Line through } (P_{\text{W1\_start}}, P_{\text{W2\_end}}) + \text{parallel through } P_{\text{W1\_end}}$$

**Acceleration Channel (after Wave 3):** Connect the termini of Waves 2 and 4. Draw a parallel through the terminus of Wave 3.

$$\text{Channel Upper (bullish)} = \text{Line through } (P_{\text{W2\_end}}, P_{\text{W4\_end}}) + \text{parallel through } P_{\text{W3\_end}}$$

Wave 5 often terminates at or near the upper channel line.

---

## 10. Mathematical Models

### 10.1 Impulse Wave Price Model

For a complete bullish impulse starting at price $P_0$:

$$P_1 = P_0 + \Delta_1$$

$$P_2 = P_1 - r_2 \cdot \Delta_1 \quad \text{where } 0 < r_2 < 1$$

$$P_3 = P_2 + e_3 \cdot \Delta_1 \quad \text{where } e_3 \geq 1$$

$$P_4 = P_3 - r_4 \cdot (P_3 - P_2) \quad \text{where } 0 < r_4 < 1 \text{ and } P_4 > P_1$$

$$P_5 = P_4 + e_5 \cdot \Delta_1 \quad \text{where } e_5 > 0$$

Subject to Iron Rules:

$$\text{Rule 1: } P_2 > P_0 \implies r_2 < 1$$

$$\text{Rule 2: } (P_3 - P_2) \geq (P_1 - P_0) \text{ OR } (P_3 - P_2) \geq (P_5 - P_4)$$

$$\text{Rule 3: } P_4 > P_1$$

### 10.2 Wave Validation Score

For a proposed impulse wave count with pivots $[P_0, P_1, P_2, P_3, P_4, P_5]$:

$$S_{\text{impulse}} = \prod_{i=1}^{3} R_i \times \sum_{j=1}^{N} w_j \cdot G_j$$

where:
- $R_i \in \{0, 1\}$ are the Iron Rule indicators (all must be 1)
- $G_j \in [0, 1]$ are the guideline scores
- $w_j$ are the guideline weights
- $N$ is the number of guidelines checked

If any $R_i = 0$, then $S_{\text{impulse}} = 0$ (invalid count).

### 10.3 Fibonacci Cluster Density

For a set of Fibonacci levels $\{F_1, F_2, ..., F_n\}$ calculated from different wave measurements:

$$D(p) = \sum_{i=1}^{n} \frac{1}{\sigma\sqrt{2\pi}} \exp\left(-\frac{(p - F_i)^2}{2\sigma^2}\right)$$

where $\sigma$ is a tolerance parameter (e.g., 0.5% of price). Peaks in $D(p)$ represent high-probability reversal zones (Fibonacci clusters).

### 10.4 Confidence-Weighted Target

$$P_{\text{target}} = \frac{\sum_{i=1}^{n} C_i \cdot T_i}{\sum_{i=1}^{n} C_i}$$

where:
- $T_i$ = individual Fibonacci target price
- $C_i$ = confidence weight for that target based on historical reliability

---

## 11. Technical Conditions for AI Detection

### 11.1 Wave 1 Detection

```python
WAVE_1_CONDITIONS = {
    # Price structure
    'five_wave_subdivision': {
        'check': 'Lower TF shows 5 clear pivots in trend direction',
        'weight': 0.25,
        'required': True
    },
    # Trend reversal signals
    'prior_trend_exhaustion': {
        'check': 'Prior 5-wave sequence complete OR ABC correction complete',
        'weight': 0.20,
        'required': False
    },
    # Momentum
    'momentum_shift': {
        'check': 'MACD crosses zero line; RSI crosses 50',
        'weight': 0.15,
        'required': False
    },
    # Volume
    'volume_increase': {
        'check': 'Volume > 1.2x average of recent range',
        'weight': 0.15,
        'required': False
    },
    # Trendline
    'trendline_break': {
        'check': 'Break of trendline connecting prior trend\'s impulsive extremes',
        'weight': 0.15,
        'required': False
    },
    # Pattern
    'reversal_pattern': {
        'check': 'Double bottom, inverse H&S, or accumulation pattern',
        'weight': 0.10,
        'required': False
    },
}
```

### 11.2 Wave 2 Detection

```python
WAVE_2_CONDITIONS = {
    'fibonacci_retracement': {
        'check': 'Price at 50%-61.8% retracement of Wave 1',
        'weight': 0.25,
        'required': False
    },
    'three_wave_structure': {
        'check': 'Lower TF shows A-B-C corrective structure',
        'weight': 0.25,
        'required': True
    },
    'does_not_exceed_wave_1_origin': {
        'check': 'Price remains above (bull) / below (bear) Wave 1 start',
        'weight': 0.00,  # Iron Rule --- binary pass/fail
        'required': True  # ABSOLUTE requirement
    },
    'volume_decline': {
        'check': 'Volume declining from Wave 1 peak',
        'weight': 0.15,
        'required': False
    },
    'reversal_signal': {
        'check': 'Bullish divergence on RSI/MACD; reversal candle',
        'weight': 0.20,
        'required': False
    },
    'support_confluence': {
        'check': 'Key S/R level, demand zone, or prior structure aligns',
        'weight': 0.15,
        'required': False
    },
}
```

### 11.3 Wave 3 Detection

```python
WAVE_3_CONDITIONS = {
    'exceeds_wave_1_terminus': {
        'check': 'Price moves beyond Wave 1 extreme',
        'weight': 0.20,
        'required': True
    },
    'strong_momentum': {
        'check': 'RSI > 70 (bull) or < 30 (bear); MACD expanding',
        'weight': 0.20,
        'required': False
    },
    'high_volume': {
        'check': 'Volume > Wave 1 volume by at least 50%',
        'weight': 0.20,
        'required': False
    },
    'five_wave_subdivision': {
        'check': 'Lower TF shows 5-wave impulse structure',
        'weight': 0.20,
        'required': True
    },
    'no_divergence': {
        'check': 'No bearish/bullish divergence on momentum',
        'weight': 0.10,
        'required': False
    },
    'price_gaps': {
        'check': 'Breakaway gaps present (in applicable markets)',
        'weight': 0.10,
        'required': False
    },
}
```

### 11.4 Wave 4 Detection

```python
WAVE_4_CONDITIONS = {
    'fibonacci_retracement': {
        'check': 'Price at 23.6%-50% retracement of Wave 3',
        'weight': 0.25,
        'required': False
    },
    'no_overlap_with_wave_1': {
        'check': 'Price stays above Wave 1 terminus (bull)',
        'weight': 0.00,  # Iron Rule
        'required': True  # ABSOLUTE
    },
    'corrective_structure': {
        'check': 'Flat, triangle, or combination pattern complete',
        'weight': 0.25,
        'required': True
    },
    'volume_contraction': {
        'check': 'Volume significantly lower than Wave 3',
        'weight': 0.15,
        'required': False
    },
    'alternation_with_wave_2': {
        'check': 'Different correction type than Wave 2',
        'weight': 0.15,
        'required': False
    },
    'time_proportion': {
        'check': 'Duration is proportional to the impulse so far',
        'weight': 0.10,
        'required': False
    },
    'wave_iv_of_3_level': {
        'check': 'Reaches sub-wave iv of Wave 3 price zone',
        'weight': 0.10,
        'required': False
    },
}
```

### 11.5 Wave 5 Detection

```python
WAVE_5_CONDITIONS = {
    'fibonacci_target': {
        'check': 'Price at 61.8%-100% of Wave 1 from Wave 4 terminus',
        'weight': 0.20,
        'required': False
    },
    'five_wave_subdivision': {
        'check': 'Lower TF shows 5-wave structure',
        'weight': 0.20,
        'required': True
    },
    'momentum_divergence': {
        'check': 'Bearish RSI divergence (bull) or bullish (bear)',
        'weight': 0.25,
        'required': False
    },
    'volume_divergence': {
        'check': 'Volume lower than Wave 3 peak',
        'weight': 0.15,
        'required': False
    },
    'channel_touch': {
        'check': 'Price touches or approaches the 2-4 channel line',
        'weight': 0.10,
        'required': False
    },
    'wave_3_not_shortest': {
        'check': 'Wave 3 remains not the shortest of 1,3,5',
        'weight': 0.00,  # Iron Rule
        'required': True  # ABSOLUTE
    },
}
```

---

## 12. Core Logic --- Entry/Exit for Each Wave Phase

### 12.1 Wave 2 Entry (Highest Probability Setup)

```
┌─────────────────────────────────────────────────────────────┐
│  WAVE 2 COMPLETION LONG ENTRY (Bullish Impulse)             │
├─────────────────────────────────────────────────────────────┤
│  TRIGGER:                                                    │
│    1. Wave 1 identified (5-wave structure, HTF trend shift)  │
│    2. Wave 2 reaches 50%-61.8% Fibonacci retracement         │
│    3. Three-wave corrective structure visible on LTF         │
│    4. Bullish divergence on RSI(14)                          │
│    5. Reversal candlestick at Fibonacci level                │
│                                                              │
│  ENTRY:                                                      │
│    Buy at market when all conditions met                     │
│    OR Buy limit at 61.8% retracement with confirmation       │
│                                                              │
│  STOP LOSS:                                                  │
│    Below Wave 1 origin - (ATR(14) x 0.5) buffer             │
│    Reason: Wave 2 > 100% invalidation                        │
│                                                              │
│  TAKE PROFIT:                                                │
│    TP1 (40%): Wave 3 at 100% extension of Wave 1             │
│    TP2 (35%): Wave 3 at 161.8% extension of Wave 1           │
│    TP3 (25%): Wave 3 at 261.8% extension of Wave 1           │
│                                                              │
│  TRAIL STOP:                                                 │
│    After TP1 hit, trail stop to breakeven                    │
│    After TP2 hit, trail stop to TP1 level                    │
│                                                              │
│  RISK/REWARD:                                                │
│    Minimum: 3:1 (TP1)                                        │
│    Expected: 5:1+ (weighted average across TPs)              │
└─────────────────────────────────────────────────────────────┘
```

### 12.2 Wave 3 Continuation Entry

```
┌─────────────────────────────────────────────────────────────┐
│  WAVE 3 PULLBACK LONG ENTRY (Bullish Impulse)               │
├─────────────────────────────────────────────────────────────┤
│  TRIGGER:                                                    │
│    1. Wave 3 confirmed (price above Wave 1 terminus)         │
│    2. Sub-wave ii of Wave 3 completes on LTF                 │
│    3. Strong momentum (RSI > 50, MACD positive)              │
│    4. Volume expanding                                       │
│                                                              │
│  ENTRY:                                                      │
│    Buy at completion of sub-wave ii on LTF                   │
│                                                              │
│  STOP LOSS:                                                  │
│    Below sub-wave i of Wave 3                                │
│    OR below Wave 2 terminus (wider stop)                     │
│                                                              │
│  TAKE PROFIT:                                                │
│    TP1 (50%): Sub-wave iii of Wave 3 target                  │
│    TP2 (50%): Wave 3 terminus at 161.8% extension            │
│                                                              │
│  RISK/REWARD: 2:1 to 4:1                                     │
└─────────────────────────────────────────────────────────────┘
```

### 12.3 Wave 4 Completion Entry

```
┌─────────────────────────────────────────────────────────────┐
│  WAVE 4 COMPLETION LONG ENTRY (Bullish Impulse)             │
├─────────────────────────────────────────────────────────────┤
│  TRIGGER:                                                    │
│    1. Wave 3 complete (momentum divergence appears)          │
│    2. Wave 4 reaches 38.2% Fibonacci retracement of Wave 3  │
│    3. Corrective pattern (flat/triangle) nearing completion  │
│    4. Wave 4 stays above Wave 1 terminus                     │
│    5. Volume contraction with signs of expansion              │
│    6. Alternation with Wave 2 type satisfied                 │
│                                                              │
│  ENTRY:                                                      │
│    Buy at corrective pattern completion                      │
│                                                              │
│  STOP LOSS:                                                  │
│    Below Wave 1 terminus - ATR buffer                        │
│    Reason: Wave 4 overlap invalidation                       │
│                                                              │
│  TAKE PROFIT:                                                │
│    TP1 (50%): Wave 5 = 61.8% of Wave 1 from Wave 4          │
│    TP2 (30%): Wave 5 = 100% of Wave 1 from Wave 4           │
│    TP3 (20%): Wave 5 = 161.8% of Wave 1 from Wave 4         │
│                                                              │
│  RISK/REWARD: 2:1 to 3:1                                     │
└─────────────────────────────────────────────────────────────┘
```

### 12.4 Wave 5 Completion Reversal Entry

```
┌─────────────────────────────────────────────────────────────┐
│  WAVE 5 COMPLETION SHORT ENTRY (After Bullish Impulse)      │
├─────────────────────────────────────────────────────────────┤
│  TRIGGER:                                                    │
│    1. Complete 5-wave impulse identified                     │
│    2. Wave 5 reaches Fibonacci target zone                   │
│    3. RSI divergence (price higher high, RSI lower high)     │
│    4. MACD divergence confirmed                              │
│    5. Volume declining relative to Wave 3                    │
│    6. Ending diagonal or wedge pattern (if present)          │
│    7. Reversal candlestick at target zone                    │
│                                                              │
│  ENTRY:                                                      │
│    Sell at market when >= 5 conditions met                   │
│    OR sell on break below Wave 5's sub-wave iv               │
│                                                              │
│  STOP LOSS:                                                  │
│    Above Wave 5 terminus + ATR buffer                        │
│    If W3 is longest: Above 161.8% extension of W3           │
│                                                              │
│  TAKE PROFIT:                                                │
│    TP1 (40%): Wave A target at 38.2% retracement of impulse │
│    TP2 (35%): 50% retracement of entire impulse             │
│    TP3 (25%): 61.8% retracement of entire impulse           │
│                                                              │
│  RISK/REWARD: 2:1 to 3:1                                     │
└─────────────────────────────────────────────────────────────┘
```

### 12.5 Decision Matrix

| Current Wave | Direction | Action | Confidence Required | RR Minimum |
|---|---|---|---|---|
| Wave 1 complete | With trend | Prepare for Wave 2 entry | 0.50 (low - uncertain) | N/A (wait) |
| Wave 2 at 50-61.8% | With trend | **BUY/SELL with trend** | 0.70 | 3:1 |
| Wave 3 in progress | With trend | Add on pullbacks (sub-ii) | 0.65 | 2:1 |
| Wave 4 at 38.2% | With trend | **BUY/SELL with trend** | 0.70 | 2:1 |
| Wave 5 at target | Counter-trend | **SELL/BUY counter-trend** | 0.75 | 2:1 |
| Wave 5 truncated | Counter-trend | **Aggressive reversal** | 0.80 | 3:1 |

---

## 13. Risk Parameters

### 13.1 Stop Loss Calculations

**Wave 2 Entry Stop Loss:**

$$SL = P_{\text{W1\_start}} - k \times ATR(14)$$

where $k = 0.5$ for tight stop, $k = 1.0$ for normal stop.

**Wave 4 Entry Stop Loss:**

$$SL = P_{\text{W1\_end}} - k \times ATR(14) \quad \text{(non-overlap invalidation)}$$

**Wave 5 Reversal Stop Loss:**

$$SL = P_{\text{W5\_end}} + k \times ATR(14)$$

If Wave 1 is longer than Wave 3, then Wave 5 has a maximum possible length (Rule 2):

$$SL_{\text{max}} = P_{\text{W4\_end}} + \text{Range}_3 \quad \text{(Wave 5 cannot exceed Wave 3 length)}$$

### 13.2 Position Size

$$\text{Lots} = \frac{\text{Account} \times R\% \times C_{\text{wave}}}{\text{SL Distance} \times \text{Pip Value}}$$

where:
- $R\%$ = base risk percentage (1%--2%)
- $C_{\text{wave}}$ = wave count confidence (0.65--1.0)

### 13.3 Risk Adjustment by Wave Position

| Wave Entry | Base Risk Multiplier | Rationale |
|---|---|---|
| Wave 2 completion | 1.0x | Highest probability setup |
| Wave 3 continuation | 0.8x | Good but already partially extended |
| Wave 4 completion | 0.7x | Wave 5 is the weakest motive wave |
| Wave 5 reversal | 0.6x | Counter-trend, higher risk |

---

## 14. Execution Flow

### 14.1 Complete Impulse Wave Trading Algorithm

```
FUNCTION trade_impulse_wave(market_data, account, config):

    // Phase 1: Identify current wave position
    wave_count = identify_wave_count(market_data, config.timeframes)
    
    IF wave_count.confidence < config.min_confidence:
        RETURN "NO_TRADE: Insufficient confidence in wave count"
    
    current_wave = wave_count.current_position
    
    // Phase 2: Determine trade setup
    SWITCH current_wave:
        
        CASE "WAVE_2_IN_PROGRESS":
            fib_level = calculate_retracement(wave_count.wave_1)
            IF fib_level BETWEEN 0.50 AND 0.786:
                IF check_reversal_confirmation(market_data):
                    setup = create_wave_2_setup(wave_count, market_data)
                    EXECUTE_TRADE(setup)
        
        CASE "WAVE_3_IN_PROGRESS":
            sub_wave = identify_sub_wave(market_data, wave_count.wave_3)
            IF sub_wave == "SUB_WAVE_II_COMPLETE":
                setup = create_wave_3_continuation_setup(wave_count, market_data)
                EXECUTE_TRADE(setup)
        
        CASE "WAVE_4_IN_PROGRESS":
            fib_level = calculate_retracement_of_wave_3(wave_count)
            IF fib_level BETWEEN 0.236 AND 0.618:
                IF check_non_overlap(wave_count):
                    IF check_corrective_pattern_complete(market_data):
                        setup = create_wave_4_setup(wave_count, market_data)
                        EXECUTE_TRADE(setup)
        
        CASE "WAVE_5_IN_PROGRESS":
            IF check_wave_5_completion_signals(wave_count, market_data):
                setup = create_wave_5_reversal_setup(wave_count, market_data)
                EXECUTE_TRADE(setup)
        
        DEFAULT:
            RETURN "NO_TRADE: No actionable setup detected"

FUNCTION EXECUTE_TRADE(setup):
    // Validate risk parameters
    IF setup.rr_ratio < config.min_rr:
        RETURN "REJECTED: RR ratio below minimum"
    
    IF setup.risk_amount > account.max_risk_per_trade:
        RETURN "REJECTED: Risk exceeds maximum"
    
    // Calculate position size
    position_size = calculate_position_size(
        account.balance,
        setup.risk_percent * setup.confidence,
        setup.stop_loss_distance,
        market_data.pip_value
    )
    
    // Place orders
    PLACE_ORDER(
        type = setup.order_type,     // MARKET or LIMIT
        direction = setup.direction,  // BUY or SELL
        size = position_size,
        stop_loss = setup.stop_loss,
        take_profit = [setup.tp1, setup.tp2, setup.tp3],
        tp_splits = [0.40, 0.35, 0.25]
    )
    
    // Set up monitoring
    MONITOR(setup.invalidation_conditions)
    MONITOR(setup.trailing_stop_conditions)
```

### 14.2 Wave Invalidation Handling

```
FUNCTION handle_wave_invalidation(active_trade, new_market_data):
    
    // Check if current wave count is still valid
    rules_valid = validate_iron_rules(active_trade.wave_count, new_market_data)
    
    IF NOT rules_valid:
        // Wave count is invalidated
        LOG("Wave count invalidated. Closing position.")
        CLOSE_POSITION(active_trade, reason="WAVE_COUNT_INVALIDATION")
        
        // Re-analyze with fresh wave count
        new_count = identify_wave_count(new_market_data)
        IF new_count.has_tradeable_setup:
            NOTIFY_SUPERVISOR("New wave count available after invalidation")
    
    // Check if alternate count becomes preferred
    alternate_scores = score_alternate_counts(new_market_data)
    IF alternate_scores[0] > active_trade.wave_count.confidence:
        NOTIFY_SUPERVISOR("Alternate count now has higher confidence")
        TIGHTEN_STOP(active_trade)  // Reduce risk while maintaining position
```

---

## 15. References

### 15.1 Primary Sources

1. **Elliott, R.N.** (1938). *The Wave Principle*. Original monograph.
2. **Elliott, R.N.** (1946). *Nature's Law: The Secret of the Universe*.
3. **Frost, A.J. & Prechter, R.R.** (1978, 2017). *Elliott Wave Principle: Key to Market Behavior*. 11th Ed. New Classics Library.
4. **Neely, G.** (1988). *Mastering Elliott Wave*. Windsor Books.
5. **Prechter, R.R.** (2002). *Conquer the Crash*. Wiley.

### 15.2 Forex-Specific References

6. **Balan, R.** (1989). *Elliott Wave Principle Applied to the Foreign Exchange Markets*. BBS Publications.
7. **Miner, R.C.** (2009). *High Probability Trading Strategies*. Wiley.
8. **Boroden, C.** (2008). *Fibonacci Trading*. McGraw-Hill.

### 15.3 Technical Analysis Foundations

9. **Murphy, J.J.** (1999). *Technical Analysis of the Financial Markets*. New York Institute of Finance.
10. **Pring, M.J.** (2002). *Technical Analysis Explained*. 4th Ed. McGraw-Hill.

### 15.4 Mathematical References

11. **Mandelbrot, B. & Hudson, R.** (2004). *The (Mis)Behavior of Markets*. Basic Books.
12. **Livio, M.** (2002). *The Golden Ratio*. Broadway Books.

---

## Document Cross-References

| Document | Path | Relationship |
|---|---|---|
| Overview | `00_overview.md` | Foundational concepts |
| Corrective Waves | `02_corrective_waves.md` | Wave 2 and Wave 4 internal patterns |
| Fibonacci Targets | `03_fibonacci_targets.md` | Detailed target calculation methods |
| Wave Counting Algorithm | `04_wave_counting_algorithm.md` | Automated counting implementation |

---

*This document provides comprehensive detail on impulse (motive) wave patterns for the Multi-Agent AI Trading System. It should be read in conjunction with the corrective wave patterns document (02_corrective_waves.md) and the Fibonacci target analysis document (03_fibonacci_targets.md) for complete Elliott Wave implementation.*
