# Elliott Wave Theory --- Algorithmic Wave Counting

## Document Metadata
| Field | Value |
|---|---|
| **Strategy ID** | EW-004 |
| **Category** | Axis 1 --- Trading Strategies |
| **Sub-Category** | Elliott Wave Theory --- Wave Counting Algorithm |
| **Applicable Markets** | Forex, Crypto |
| **Timeframes** | All (Multi-Timeframe) |
| **Complexity** | Expert |
| **AI Suitability** | Critical (core algorithmic component) |
| **Last Updated** | 2026-04-12 |

---

## Table of Contents
1. [Introduction to Automated Wave Counting](#1-introduction-to-automated-wave-counting)
2. [Step-by-Step Wave Counting Algorithm](#2-step-by-step-wave-counting-algorithm)
3. [ZigZag Indicator Integration](#3-zigzag-indicator-integration)
4. [Pivot Point Detection Methods](#4-pivot-point-detection-methods)
5. [Degree Labeling System](#5-degree-labeling-system)
6. [Validation Logic (Iron Rules)](#6-validation-logic-iron-rules)
7. [Confidence Scoring System](#7-confidence-scoring-system)
8. [Handling Alternate Wave Counts](#8-handling-alternate-wave-counts)
9. [Multi-Timeframe Alignment](#9-multi-timeframe-alignment)
10. [Core Logic --- Entry/Exit Decisions](#10-core-logic----entryexit-decisions)
11. [Technical Specifications](#11-technical-specifications)
12. [Risk Parameters --- SL/TP/RR Calculations](#12-risk-parameters----sltprr-calculations)
13. [Execution Flow --- Complete Pseudocode](#13-execution-flow----complete-pseudocode)
14. [Performance Optimization](#14-performance-optimization)
15. [References](#15-references)

---

## 1. Introduction to Automated Wave Counting

### 1.1 The Challenge

Automated Elliott Wave counting is one of the most difficult problems in computational technical analysis. The primary challenges are:

1. **Combinatorial explosion**: Given $n$ pivot points, the number of possible wave labelings grows exponentially
2. **Subjectivity**: Multiple valid wave counts can coexist, differing only in probability
3. **Real-time uncertainty**: The current wave is only definitively identifiable after it completes
4. **Multi-degree complexity**: Waves contain waves, creating recursive labeling requirements
5. **Pattern variety**: Corrective waves come in many forms (zigzag, flat, triangle, combinations)

### 1.2 Algorithmic Approach

Our approach uses a **hierarchical top-down** methodology with the following architecture:

```
┌───────────────────────────────────────────────────────────┐
│                    WAVE COUNTING ENGINE                     │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Layer 1: Pivot Detection (ZigZag + Adaptive Threshold)   │
│     │                                                     │
│     ▼                                                     │
│  Layer 2: Wave Candidate Generation (Combinatorial)       │
│     │                                                     │
│     ▼                                                     │
│  Layer 3: Rule Validation (Iron Rules + Guidelines)       │
│     │                                                     │
│     ▼                                                     │
│  Layer 4: Confidence Scoring (Multi-Factor Weighting)     │
│     │                                                     │
│     ▼                                                     │
│  Layer 5: Multi-Timeframe Alignment (Fractal Validation)  │
│     │                                                     │
│     ▼                                                     │
│  Layer 6: Trade Signal Generation (Entry/Exit Logic)      │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### 1.3 Design Principles

| Principle | Description |
|---|---|
| **Top-Down** | Start from the highest timeframe; use HTF count to constrain LTF |
| **Rule-First** | Iron Rules are absolute; any violation immediately invalidates a count |
| **Probabilistic** | Maintain multiple counts with probability weights |
| **Bayesian** | Update probabilities as new data arrives |
| **Fibonacci-Validated** | Fibonacci relationships increase confidence; violations decrease it |
| **Confirmation-Required** | No trade without multiple confirmation factors |

---

## 2. Step-by-Step Wave Counting Algorithm

### 2.1 High-Level Algorithm

```
ALGORITHM: ElliottWaveCounter

INPUT:
    market_data: OHLCV data for multiple timeframes
    config: Configuration parameters
    previous_count: Optional prior wave count for continuity

OUTPUT:
    wave_counts: List of WaveCount objects ranked by confidence
    trade_signals: List of TradeSignal objects

PROCEDURE:

    // STEP 1: Prepare Data
    FOR EACH timeframe IN config.timeframes (highest to lowest):
        clean_data[tf] = preprocess(market_data[tf])
    
    // STEP 2: Detect Pivots
    FOR EACH timeframe IN config.timeframes:
        pivots[tf] = detect_pivots(clean_data[tf], config.pivot_params[tf])
    
    // STEP 3: Generate Wave Candidates (Top-Down)
    htf = config.timeframes[0]  // Highest timeframe
    htf_candidates = generate_wave_candidates(pivots[htf])
    
    // STEP 4: Validate Candidates
    valid_counts = []
    FOR EACH candidate IN htf_candidates:
        IF validate_iron_rules(candidate):
            score = calculate_confidence(candidate, clean_data[htf])
            valid_counts.APPEND((candidate, score))
    
    // STEP 5: Rank and Select Top Counts
    valid_counts.SORT(BY score, DESCENDING)
    top_counts = valid_counts[:config.max_alternate_counts]
    
    // STEP 6: Align with Lower Timeframes
    FOR EACH (count, score) IN top_counts:
        FOR EACH lower_tf IN config.timeframes[1:]:
            alignment_score = validate_ltf_alignment(
                count, pivots[lower_tf], clean_data[lower_tf]
            )
            count.alignment_scores[lower_tf] = alignment_score
        
        // Update overall score with alignment
        count.final_score = calculate_final_score(count, count.alignment_scores)
    
    // STEP 7: Generate Trade Signals
    trade_signals = generate_signals(top_counts, clean_data, config)
    
    RETURN top_counts, trade_signals
```

### 2.2 Detailed Sub-Procedures

#### 2.2.1 Data Preprocessing

```
FUNCTION preprocess(raw_data):
    // Remove gaps and anomalies
    data = remove_outlier_wicks(raw_data, threshold=5*ATR)
    
    // Calculate required indicators
    data.rsi = RSI(data.close, period=14)
    data.macd = MACD(data.close, 12, 26, 9)
    data.atr = ATR(data, period=14)
    data.volume_ma = SMA(data.volume, period=20)
    
    RETURN data
```

#### 2.2.2 Wave Candidate Generation

```
FUNCTION generate_wave_candidates(pivots):
    candidates = []
    
    // Try all possible groupings of pivots into 5-wave or 3-wave patterns
    n = LENGTH(pivots)
    
    // For impulse waves (5 waves = 6 pivot points)
    FOR i = 0 TO n-6:
        FOR j = i+1 TO n-5:
            FOR k = j+1 TO n-4:
                FOR l = k+1 TO n-3:
                    FOR m = l+1 TO n-2:
                        candidate = {
                            'type': 'impulse',
                            'pivots': [pivots[i], pivots[j], pivots[k], 
                                      pivots[l], pivots[m], pivots[m+1]],
                            'start_idx': i,
                            'end_idx': m+1
                        }
                        IF quick_validate(candidate):
                            candidates.APPEND(candidate)
    
    // For corrective waves (3 waves = 4 pivot points)
    FOR i = 0 TO n-4:
        FOR j = i+1 TO n-3:
            FOR k = j+1 TO n-2:
                candidate = {
                    'type': 'correction',
                    'pivots': [pivots[i], pivots[j], pivots[k], pivots[k+1]],
                    'start_idx': i,
                    'end_idx': k+1
                }
                IF quick_validate_correction(candidate):
                    candidates.APPEND(candidate)
    
    RETURN candidates
```

**Note:** In practice, this brute-force approach is too slow for large pivot sets. Section 14 (Performance Optimization) describes pruning strategies.

---

## 3. ZigZag Indicator Integration

### 3.1 Standard ZigZag Algorithm

The ZigZag indicator identifies significant price swings by filtering out noise below a specified threshold.

```python
def zigzag(data, threshold, mode='percent'):
    """
    ZigZag indicator for pivot detection.
    
    Parameters:
        data: DataFrame with 'high' and 'low' columns
        threshold: Minimum reversal threshold
        mode: 'percent' (percentage) or 'absolute' (price) or 'atr' (ATR-based)
    
    Returns:
        List of pivot points: [(index, price, type), ...]
        where type is 'high' or 'low'
    """
    pivots = []
    
    if mode == 'percent':
        min_reversal = lambda price: price * threshold
    elif mode == 'absolute':
        min_reversal = lambda price: threshold
    elif mode == 'atr':
        atr = calculate_atr(data, 14)
        min_reversal = lambda price: threshold * atr[len(pivots)]
    
    # Initialize
    current_trend = None  # 'up' or 'down'
    last_high = data['high'].iloc[0]
    last_high_idx = 0
    last_low = data['low'].iloc[0]
    last_low_idx = 0
    
    for i in range(1, len(data)):
        current_high = data['high'].iloc[i]
        current_low = data['low'].iloc[i]
        
        if current_trend is None:
            # Determine initial trend
            if current_high > last_high:
                current_trend = 'up'
                last_high = current_high
                last_high_idx = i
            elif current_low < last_low:
                current_trend = 'down'
                last_low = current_low
                last_low_idx = i
        
        elif current_trend == 'up':
            if current_high > last_high:
                # Continue up
                last_high = current_high
                last_high_idx = i
            elif last_high - current_low >= min_reversal(last_high):
                # Reversal down
                pivots.append((last_high_idx, last_high, 'high'))
                current_trend = 'down'
                last_low = current_low
                last_low_idx = i
        
        elif current_trend == 'down':
            if current_low < last_low:
                # Continue down
                last_low = current_low
                last_low_idx = i
            elif current_high - last_low >= min_reversal(last_low):
                # Reversal up
                pivots.append((last_low_idx, last_low, 'low'))
                current_trend = 'up'
                last_high = current_high
                last_high_idx = i
    
    # Add the last pivot
    if current_trend == 'up':
        pivots.append((last_high_idx, last_high, 'high'))
    else:
        pivots.append((last_low_idx, last_low, 'low'))
    
    return pivots
```

### 3.2 Adaptive ZigZag for Elliott Wave

Standard ZigZag with a fixed threshold misses waves at different degrees. An **adaptive ZigZag** uses multiple thresholds:

```python
def adaptive_zigzag(data, thresholds):
    """
    Run ZigZag at multiple thresholds to capture waves at different degrees.
    
    Parameters:
        data: OHLCV DataFrame
        thresholds: List of thresholds [0.01, 0.03, 0.05, 0.10, 0.15]
                    (representing wave degrees from minute to primary)
    
    Returns:
        Dictionary mapping threshold to pivot list
    """
    results = {}
    
    for threshold in thresholds:
        results[threshold] = zigzag(data, threshold, mode='percent')
    
    return results
```

### 3.3 Threshold Selection by Market

| Market | Timeframe | ZigZag Threshold | Wave Degree Targeted |
|---|---|---|---|
| Forex Majors | Monthly | 10%--15% | Cycle/Supercycle |
| Forex Majors | Weekly | 5%--8% | Primary |
| Forex Majors | Daily | 2%--4% | Intermediate |
| Forex Majors | 4H | 1%--2% | Minor |
| Forex Majors | 1H | 0.5%--1% | Minute |
| Forex Majors | 15M | 0.2%--0.5% | Minuette |
| Crypto (BTC) | Weekly | 15%--25% | Cycle |
| Crypto (BTC) | Daily | 8%--15% | Primary |
| Crypto (BTC) | 4H | 4%--8% | Intermediate |
| Crypto (BTC) | 1H | 2%--4% | Minor |
| Crypto (Alts) | Daily | 15%--30% | Primary |
| Crypto (Alts) | 4H | 8%--15% | Intermediate |
| Crypto (Alts) | 1H | 4%--8% | Minor |

### 3.4 ATR-Based Adaptive Threshold

For dynamic threshold adjustment:

$$\text{Threshold}_{\text{dynamic}} = k \times \frac{ATR(n)}{P_{\text{current}}} \times 100\%$$

where $k$ is a multiplier:
- $k = 2$ for capturing minor degree waves
- $k = 4$ for capturing intermediate degree waves
- $k = 8$ for capturing primary degree waves

---

## 4. Pivot Point Detection Methods

### 4.1 Fractal-Based Pivots

A **fractal high** is a bar whose high is higher than the highs of $n$ bars on each side. A **fractal low** is a bar whose low is lower than the lows of $n$ bars on each side.

```python
def detect_fractals(data, lookback=2):
    """
    Detect Williams fractals (pivot points).
    
    Parameters:
        data: OHLCV DataFrame
        lookback: Number of bars on each side (default 2 = 5-bar fractal)
    
    Returns:
        List of (index, price, type) tuples
    """
    fractals = []
    
    for i in range(lookback, len(data) - lookback):
        # Check for fractal high
        is_high = True
        for j in range(1, lookback + 1):
            if data['high'].iloc[i] <= data['high'].iloc[i-j] or \
               data['high'].iloc[i] <= data['high'].iloc[i+j]:
                is_high = False
                break
        
        if is_high:
            fractals.append((i, data['high'].iloc[i], 'high'))
        
        # Check for fractal low
        is_low = True
        for j in range(1, lookback + 1):
            if data['low'].iloc[i] >= data['low'].iloc[i-j] or \
               data['low'].iloc[i] >= data['low'].iloc[i+j]:
                is_low = False
                break
        
        if is_low:
            fractals.append((i, data['low'].iloc[i], 'low'))
    
    return sorted(fractals, key=lambda x: x[0])
```

### 4.2 Strength-Based Pivot Classification

Not all pivots are equal. Classify pivots by **strength** (number of bars on each side):

| Strength | Bars on Each Side | Wave Degree (Typical) |
|---|---|---|
| 1 | 1 | Sub-minuette |
| 2 | 2 | Minuette |
| 3 | 3--5 | Minute |
| 5 | 5--8 | Minor |
| 8 | 8--13 | Intermediate |
| 13 | 13--21 | Primary |
| 21 | 21--34 | Cycle |

```python
def detect_pivots_with_strength(data, strengths=[2, 3, 5, 8, 13]):
    """
    Detect pivots at multiple strength levels.
    
    Returns:
        Dictionary mapping strength to list of pivots
    """
    all_pivots = {}
    
    for strength in strengths:
        pivots = detect_fractals(data, lookback=strength)
        all_pivots[strength] = pivots
    
    return all_pivots
```

### 4.3 Volume-Confirmed Pivots

Filter pivots by volume to increase significance:

```python
def volume_confirmed_pivots(fractals, data, volume_threshold=1.5):
    """
    Filter pivots to only include those with significant volume.
    
    A confirmed pivot has volume >= volume_threshold * volume_MA(20)
    """
    confirmed = []
    volume_ma = data['volume'].rolling(20).mean()
    
    for idx, price, ptype in fractals:
        if data['volume'].iloc[idx] >= volume_threshold * volume_ma.iloc[idx]:
            confirmed.append((idx, price, ptype, 'volume_confirmed'))
        else:
            confirmed.append((idx, price, ptype, 'unconfirmed'))
    
    return confirmed
```

### 4.4 Merging Pivots Across Methods

```python
def merge_pivot_methods(zigzag_pivots, fractal_pivots, volume_pivots, tolerance):
    """
    Merge pivots from multiple detection methods.
    Pivots confirmed by multiple methods get higher priority.
    """
    merged = []
    
    for zp in zigzag_pivots:
        confirmation_count = 1
        
        # Check if this pivot is also detected by fractals
        for fp in fractal_pivots:
            if abs(zp.price - fp.price) <= tolerance and abs(zp.index - fp.index) <= 2:
                confirmation_count += 1
                break
        
        # Check volume confirmation
        for vp in volume_pivots:
            if abs(zp.price - vp.price) <= tolerance and abs(zp.index - vp.index) <= 2:
                confirmation_count += 1
                break
        
        merged.append({
            'index': zp.index,
            'price': zp.price,
            'type': zp.type,
            'confirmations': confirmation_count,
            'significance': calculate_significance(confirmation_count)
        })
    
    return sorted(merged, key=lambda x: x['significance'], reverse=True)
```

---

## 5. Degree Labeling System

### 5.1 Degree Hierarchy

The Elliott Wave degree system maps wave sizes to named categories:

```python
WAVE_DEGREES = {
    'grand_supercycle': {
        'motive_labels': ['[I]', '[II]', '[III]', '[IV]', '[V]'],
        'corrective_labels': ['[A]', '[B]', '[C]', '[D]', '[E]'],
        'typical_timeframe': 'multi-decade',
        'min_bars_monthly': 120,   # ~10 years on monthly
    },
    'supercycle': {
        'motive_labels': ['(I)', '(II)', '(III)', '(IV)', '(V)'],
        'corrective_labels': ['(A)', '(B)', '(C)', '(D)', '(E)'],
        'typical_timeframe': 'multi-year',
        'min_bars_weekly': 100,    # ~2 years on weekly
    },
    'cycle': {
        'motive_labels': ['I', 'II', 'III', 'IV', 'V'],
        'corrective_labels': ['A', 'B', 'C', 'D', 'E'],
        'typical_timeframe': '1-several years',
        'min_bars_weekly': 26,     # ~6 months on weekly
    },
    'primary': {
        'motive_labels': ['①', '②', '③', '④', '⑤'],
        'corrective_labels': ['Ⓐ', 'Ⓑ', 'Ⓒ', 'Ⓓ', 'Ⓔ'],
        'typical_timeframe': 'months to 1 year',
        'min_bars_daily': 40,      # ~2 months on daily
    },
    'intermediate': {
        'motive_labels': ['(1)', '(2)', '(3)', '(4)', '(5)'],
        'corrective_labels': ['(a)', '(b)', '(c)', '(d)', '(e)'],
        'typical_timeframe': 'weeks to months',
        'min_bars_daily': 10,      # ~2 weeks on daily
    },
    'minor': {
        'motive_labels': ['1', '2', '3', '4', '5'],
        'corrective_labels': ['a', 'b', 'c', 'd', 'e'],
        'typical_timeframe': 'days to weeks',
        'min_bars_4h': 15,         # ~2.5 days on 4H
    },
    'minute': {
        'motive_labels': ['i', 'ii', 'iii', 'iv', 'v'],
        'corrective_labels': ['a', 'b', 'c', 'd', 'e'],
        'typical_timeframe': 'hours to days',
        'min_bars_1h': 10,         # ~10 hours on 1H
    },
    'minuette': {
        'motive_labels': ['(i)', '(ii)', '(iii)', '(iv)', '(v)'],
        'corrective_labels': ['(a)', '(b)', '(c)', '(d)', '(e)'],
        'typical_timeframe': 'minutes to hours',
        'min_bars_15m': 10,        # ~2.5 hours on 15M
    },
    'subminuette': {
        'motive_labels': ['i.', 'ii.', 'iii.', 'iv.', 'v.'],
        'corrective_labels': ['a.', 'b.', 'c.', 'd.', 'e.'],
        'typical_timeframe': 'minutes',
        'min_bars_5m': 8,          # ~40 minutes on 5M
    },
}
```

### 5.2 Degree Assignment Algorithm

```python
def assign_wave_degree(wave_range, wave_duration, market_type, timeframe):
    """
    Assign an appropriate degree label to a wave based on its range and duration.
    
    Parameters:
        wave_range: Price range of the wave (percentage or pips)
        wave_duration: Duration in bars
        market_type: 'forex' or 'crypto'
        timeframe: Current chart timeframe
    
    Returns:
        degree: String name of the wave degree
    """
    # Define degree thresholds by market and timeframe
    if market_type == 'forex':
        thresholds = FOREX_DEGREE_THRESHOLDS[timeframe]
    else:
        thresholds = CRYPTO_DEGREE_THRESHOLDS[timeframe]
    
    for degree, params in thresholds.items():
        if (params['min_range'] <= wave_range <= params['max_range'] and
            params['min_duration'] <= wave_duration <= params['max_duration']):
            return degree
    
    return 'unknown'


# Example threshold definitions
FOREX_DEGREE_THRESHOLDS = {
    'daily': {
        'primary': {'min_range': 500, 'max_range': 5000, 'min_duration': 40, 'max_duration': 500},
        'intermediate': {'min_range': 150, 'max_range': 1500, 'min_duration': 10, 'max_duration': 80},
        'minor': {'min_range': 50, 'max_range': 500, 'min_duration': 3, 'max_duration': 20},
    },
    '4h': {
        'intermediate': {'min_range': 200, 'max_range': 2000, 'min_duration': 30, 'max_duration': 200},
        'minor': {'min_range': 50, 'max_range': 500, 'min_duration': 10, 'max_duration': 50},
        'minute': {'min_range': 15, 'max_range': 150, 'min_duration': 4, 'max_duration': 20},
    },
}
```

### 5.3 Degree Consistency Validation

A key validation: sub-waves must be exactly one degree lower than their parent wave.

```python
def validate_degree_consistency(parent_wave, sub_waves):
    """
    Ensure sub-waves are exactly one degree lower than the parent wave.
    """
    expected_sub_degree = get_next_lower_degree(parent_wave.degree)
    
    for sub_wave in sub_waves:
        if sub_wave.degree != expected_sub_degree:
            return False, f"Sub-wave degree {sub_wave.degree} != expected {expected_sub_degree}"
    
    return True, "Degree consistency validated"
```

---

## 6. Validation Logic (Iron Rules)

### 6.1 Complete Rule Validation Engine

```python
class WaveRuleValidator:
    """
    Validates Elliott Wave counts against the three Iron Rules
    and provides detailed violation reports.
    """
    
    def validate_impulse(self, wave_count, direction='bullish'):
        """
        Validate a proposed impulse wave count.
        
        Parameters:
            wave_count: Dictionary with keys 'w0' through 'w5' (prices at each pivot)
                       w0 = start, w1 = end of wave 1, w2 = end of wave 2, etc.
            direction: 'bullish' or 'bearish'
        
        Returns:
            (is_valid, violations, warnings)
        """
        violations = []
        warnings = []
        
        w0 = wave_count['w0']  # Start of impulse
        w1 = wave_count['w1']  # End of Wave 1
        w2 = wave_count['w2']  # End of Wave 2
        w3 = wave_count['w3']  # End of Wave 3
        w4 = wave_count['w4']  # End of Wave 4
        w5 = wave_count['w5']  # End of Wave 5
        
        # Calculate wave ranges
        range_1 = abs(w1 - w0)
        range_2 = abs(w2 - w1)
        range_3 = abs(w3 - w2)
        range_4 = abs(w4 - w3)
        range_5 = abs(w5 - w4)
        
        # ══════════════════════════════════════════════
        # IRON RULE 1: Wave 2 does not retrace > 100% of Wave 1
        # ══════════════════════════════════════════════
        if direction == 'bullish':
            rule_1_valid = w2 > w0
        else:
            rule_1_valid = w2 < w0
        
        if not rule_1_valid:
            violations.append({
                'rule': 'RULE_1',
                'severity': 'FATAL',
                'message': f'Wave 2 ({w2}) retraces beyond Wave 1 origin ({w0})',
                'retracement_pct': (range_2 / range_1 * 100) if range_1 > 0 else float('inf')
            })
        
        # ══════════════════════════════════════════════
        # IRON RULE 2: Wave 3 is never the shortest
        # ══════════════════════════════════════════════
        rule_2_valid = not (range_3 < range_1 and range_3 < range_5)
        
        if not rule_2_valid:
            violations.append({
                'rule': 'RULE_2',
                'severity': 'FATAL',
                'message': f'Wave 3 ({range_3:.5f}) is shorter than both Wave 1 ({range_1:.5f}) and Wave 5 ({range_5:.5f})',
                'ranges': {'wave_1': range_1, 'wave_3': range_3, 'wave_5': range_5}
            })
        
        # ══════════════════════════════════════════════
        # IRON RULE 3: Wave 4 does not overlap Wave 1
        # ══════════════════════════════════════════════
        if direction == 'bullish':
            # In bullish impulse, Wave 4 low must stay above Wave 1 high
            wave_4_low = wave_count.get('w4_low', w4)  # Use actual low if available
            rule_3_valid = wave_4_low > w1
        else:
            # In bearish impulse, Wave 4 high must stay below Wave 1 low
            wave_4_high = wave_count.get('w4_high', w4)  # Use actual high if available
            rule_3_valid = wave_4_high < w1
        
        if not rule_3_valid:
            violations.append({
                'rule': 'RULE_3',
                'severity': 'FATAL',
                'message': f'Wave 4 overlaps Wave 1 territory',
                'wave_1_terminus': w1,
                'wave_4_extreme': wave_4_low if direction == 'bullish' else wave_4_high
            })
        
        # ══════════════════════════════════════════════
        # ADDITIONAL STRUCTURAL VALIDATIONS
        # ══════════════════════════════════════════════
        
        # Waves 1, 3, 5 must move with the trend
        if direction == 'bullish':
            if w1 <= w0:
                violations.append({'rule': 'STRUCTURE', 'severity': 'FATAL',
                                  'message': 'Wave 1 does not advance (bullish)'})
            if w3 <= w2:
                violations.append({'rule': 'STRUCTURE', 'severity': 'FATAL',
                                  'message': 'Wave 3 does not advance (bullish)'})
            if w5 <= w4:
                warnings.append({'rule': 'STRUCTURE', 'severity': 'WARNING',
                                'message': 'Wave 5 does not advance - possible truncation'})
        else:
            if w1 >= w0:
                violations.append({'rule': 'STRUCTURE', 'severity': 'FATAL',
                                  'message': 'Wave 1 does not advance (bearish)'})
            if w3 >= w2:
                violations.append({'rule': 'STRUCTURE', 'severity': 'FATAL',
                                  'message': 'Wave 3 does not advance (bearish)'})
            if w5 >= w4:
                warnings.append({'rule': 'STRUCTURE', 'severity': 'WARNING',
                                'message': 'Wave 5 does not advance - possible truncation'})
        
        # Wave 3 should exceed Wave 1 terminus
        if direction == 'bullish' and w3 <= w1:
            violations.append({'rule': 'STRUCTURE', 'severity': 'FATAL',
                              'message': 'Wave 3 does not exceed Wave 1 high'})
        elif direction == 'bearish' and w3 >= w1:
            violations.append({'rule': 'STRUCTURE', 'severity': 'FATAL',
                              'message': 'Wave 3 does not exceed Wave 1 low'})
        
        is_valid = len(violations) == 0
        
        return is_valid, violations, warnings
    
    
    def validate_diagonal(self, wave_count, diagonal_type, direction='bullish'):
        """
        Validate a diagonal pattern (leading or ending).
        
        Diagonals allow Wave 4 overlap with Wave 1 but have other constraints.
        """
        violations = []
        warnings = []
        
        w0, w1, w2, w3, w4, w5 = [wave_count[f'w{i}'] for i in range(6)]
        ranges = [abs(wave_count[f'w{i+1}'] - wave_count[f'w{i}']) for i in range(5)]
        
        # Rule 1 still applies: Wave 2 < 100% of Wave 1
        if direction == 'bullish' and w2 <= w0:
            violations.append({'rule': 'RULE_1', 'severity': 'FATAL',
                              'message': 'Wave 2 exceeds Wave 1 origin in diagonal'})
        
        # Rule 2 still applies: Wave 3 not shortest
        if ranges[2] < ranges[0] and ranges[2] < ranges[4]:
            violations.append({'rule': 'RULE_2', 'severity': 'FATAL',
                              'message': 'Wave 3 is shortest in diagonal'})
        
        # Rule 3 is RELAXED: Wave 4 CAN overlap Wave 1 in diagonals
        # But waves should form converging/diverging trendlines
        
        # Contracting diagonal: each successive wave should be shorter
        if diagonal_type == 'contracting':
            for i in range(1, 5):
                if ranges[i] > ranges[i-1] * 1.1:  # Allow 10% tolerance
                    warnings.append({'rule': 'GUIDELINE', 'severity': 'WARNING',
                                    'message': f'Wave {i+1} longer than Wave {i} in contracting diagonal'})
        
        # Ending diagonal: all sub-waves should be 3-wave structures
        if diagonal_type == 'ending':
            # This would require sub-wave counting which is done separately
            pass
        
        is_valid = len(violations) == 0
        return is_valid, violations, warnings
```

### 6.2 Rule Violation Recovery

When a rule is violated, the algorithm must recover:

```python
def handle_rule_violation(violation, current_count, pivots):
    """
    When an Iron Rule is violated, determine the corrective action.
    """
    if violation['rule'] == 'RULE_1':
        # Wave 2 exceeded Wave 1 origin
        # Options:
        # 1. The "Wave 1" was not actually Wave 1 (re-count from earlier pivot)
        # 2. The move is still part of the prior correction
        alternatives = [
            recount_from_earlier_pivot(current_count, pivots),
            reclassify_as_correction(current_count, pivots),
        ]
    
    elif violation['rule'] == 'RULE_2':
        # Wave 3 is the shortest
        # Options:
        # 1. Wave 3 has not completed yet (add more pivots)
        # 2. What was labeled as Wave 5 end is actually part of an extension
        # 3. The entire count is wrong
        alternatives = [
            extend_wave_3(current_count, pivots),
            recombine_waves_4_5(current_count, pivots),
            invalidate_and_recount(current_count, pivots),
        ]
    
    elif violation['rule'] == 'RULE_3':
        # Wave 4 overlaps Wave 1
        # Options:
        # 1. This is a diagonal pattern (check diagonal rules)
        # 2. The count is wrong (what is Wave 3 may be Wave A of a correction)
        alternatives = [
            reclassify_as_diagonal(current_count, pivots),
            reclassify_wave_3_as_correction(current_count, pivots),
        ]
    
    return alternatives
```

---

## 7. Confidence Scoring System

### 7.1 Multi-Factor Confidence Model

```python
class WaveConfidenceScorer:
    """
    Calculates confidence score for a proposed wave count.
    
    Score range: 0.0 to 1.0
    Minimum for trading: 0.65
    """
    
    def __init__(self, config):
        self.weights = config['confidence_weights']
    
    def calculate_confidence(self, wave_count, market_data):
        """
        Calculate overall confidence score.
        
        Components:
            1. Structural validity (rules + sub-wave structure)
            2. Fibonacci alignment (price ratios match expected)
            3. Volume confirmation (volume profile matches wave identity)
            4. Momentum confirmation (RSI/MACD align with wave phase)
            5. Time proportionality (wave durations are reasonable)
            6. Multi-timeframe alignment (HTF/LTF consistency)
            7. Historical pattern match (similar to known wave patterns)
        """
        scores = {}
        
        # 1. Structural Score
        scores['structural'] = self.score_structure(wave_count)
        
        # 2. Fibonacci Score
        scores['fibonacci'] = self.score_fibonacci(wave_count)
        
        # 3. Volume Score
        scores['volume'] = self.score_volume(wave_count, market_data)
        
        # 4. Momentum Score
        scores['momentum'] = self.score_momentum(wave_count, market_data)
        
        # 5. Time Proportionality Score
        scores['time'] = self.score_time_proportion(wave_count)
        
        # 6. MTF Alignment Score
        scores['mtf_alignment'] = self.score_mtf_alignment(wave_count)
        
        # 7. Pattern Match Score
        scores['pattern_match'] = self.score_pattern_match(wave_count)
        
        # Weighted combination
        total_score = sum(
            self.weights[key] * scores[key] 
            for key in scores
        )
        
        return total_score, scores
    
    
    def score_structure(self, wave_count):
        """Score based on structural completeness and sub-wave verification."""
        score = 1.0
        
        # Deductions for structural issues
        if not wave_count.has_five_wave_subdivision_w1:
            score -= 0.15
        if not wave_count.has_three_wave_subdivision_w2:
            score -= 0.15
        if not wave_count.has_five_wave_subdivision_w3:
            score -= 0.15
        if not wave_count.has_three_wave_subdivision_w4:
            score -= 0.15
        if not wave_count.has_five_wave_subdivision_w5:
            score -= 0.15
        
        # Bonus for clear alternation
        if wave_count.alternation_satisfied:
            score += 0.10
        
        return max(0.0, min(1.0, score))
    
    
    def score_fibonacci(self, wave_count):
        """Score based on Fibonacci ratio alignment."""
        score = 0.0
        total_checks = 0
        
        # Wave 2 at Fibonacci level of Wave 1
        w2_retrace = wave_count.wave_2_retracement
        fib_levels_w2 = [0.382, 0.500, 0.618, 0.786]
        tolerance = 0.03  # 3% tolerance
        
        min_distance_w2 = min(abs(w2_retrace - f) for f in fib_levels_w2)
        if min_distance_w2 <= tolerance:
            score += 1.0
        elif min_distance_w2 <= tolerance * 2:
            score += 0.5
        total_checks += 1
        
        # Wave 3 at Fibonacci extension of Wave 1
        w3_extension = wave_count.wave_3_extension
        fib_levels_w3 = [1.000, 1.272, 1.618, 2.000, 2.618, 4.236]
        
        min_distance_w3 = min(abs(w3_extension - f) for f in fib_levels_w3)
        if min_distance_w3 <= tolerance:
            score += 1.0
        elif min_distance_w3 <= tolerance * 2:
            score += 0.5
        total_checks += 1
        
        # Wave 4 at Fibonacci retracement of Wave 3
        w4_retrace = wave_count.wave_4_retracement
        fib_levels_w4 = [0.236, 0.382, 0.500]
        
        min_distance_w4 = min(abs(w4_retrace - f) for f in fib_levels_w4)
        if min_distance_w4 <= tolerance:
            score += 1.0
        elif min_distance_w4 <= tolerance * 2:
            score += 0.5
        total_checks += 1
        
        # Wave 5 relationships
        w5_to_w1 = wave_count.wave_5_range / wave_count.wave_1_range
        fib_levels_w5 = [0.618, 1.000, 1.618]
        
        min_distance_w5 = min(abs(w5_to_w1 - f) for f in fib_levels_w5)
        if min_distance_w5 <= tolerance:
            score += 1.0
        elif min_distance_w5 <= tolerance * 2:
            score += 0.5
        total_checks += 1
        
        return score / total_checks if total_checks > 0 else 0.0
    
    
    def score_volume(self, wave_count, market_data):
        """Score based on volume profile matching expected wave characteristics."""
        score = 0.0
        
        # Wave 3 should have highest volume
        if wave_count.wave_3_avg_volume > wave_count.wave_1_avg_volume:
            score += 0.40
        
        # Wave 5 volume should be less than Wave 3
        if wave_count.wave_5_avg_volume < wave_count.wave_3_avg_volume:
            score += 0.30
        
        # Wave 4 volume should decline
        if wave_count.wave_4_avg_volume < wave_count.wave_3_avg_volume:
            score += 0.30
        
        return score
    
    
    def score_momentum(self, wave_count, market_data):
        """Score based on momentum indicator alignment."""
        score = 0.0
        
        # Wave 3: RSI should reach extreme (>70 bull, <30 bear)
        if wave_count.wave_3_rsi_extreme:
            score += 0.30
        
        # Wave 5: RSI divergence with price
        if wave_count.wave_5_rsi_divergence:
            score += 0.40
        
        # Wave 3: MACD histogram peak
        if wave_count.wave_3_macd_peak:
            score += 0.30
        
        return score
    
    
    def score_time_proportion(self, wave_count):
        """Score based on time relationships between waves."""
        score = 0.0
        
        # Wave 3 duration should be >= Wave 1 duration (usually)
        if wave_count.wave_3_duration >= wave_count.wave_1_duration * 0.8:
            score += 0.25
        
        # Wave 4 duration should be proportional
        if (0.382 * wave_count.wave_3_duration <= wave_count.wave_4_duration <=
            2.618 * wave_count.wave_3_duration):
            score += 0.25
        
        # Wave 2 and Wave 4 should not be extremely disproportionate
        ratio = (wave_count.wave_2_duration / wave_count.wave_4_duration 
                 if wave_count.wave_4_duration > 0 else float('inf'))
        if 0.25 <= ratio <= 4.0:
            score += 0.25
        
        # Overall impulse should take reasonable time
        score += 0.25  # Base score for having identifiable duration
        
        return score
    
    
    def score_mtf_alignment(self, wave_count):
        """Score based on multi-timeframe wave count alignment."""
        if not wave_count.htf_alignment:
            return 0.5  # Neutral if no HTF data
        
        if wave_count.htf_alignment == 'confirmed':
            return 1.0
        elif wave_count.htf_alignment == 'compatible':
            return 0.75
        elif wave_count.htf_alignment == 'neutral':
            return 0.50
        elif wave_count.htf_alignment == 'conflicting':
            return 0.25
        else:
            return 0.0
    
    
    def score_pattern_match(self, wave_count):
        """Score based on similarity to known, validated wave patterns."""
        # This could use ML pattern matching or template comparison
        # Simplified version:
        score = 0.5  # Base score
        
        if wave_count.matches_textbook_proportions:
            score += 0.30
        
        if wave_count.has_clean_channels:
            score += 0.20
        
        return min(1.0, score)
```

### 7.2 Confidence Weight Configuration

```python
CONFIDENCE_WEIGHTS = {
    'structural':     0.25,  # Most important: does it follow the rules and structure?
    'fibonacci':      0.20,  # Very important: do ratios align?
    'volume':         0.15,  # Important: does volume confirm wave identity?
    'momentum':       0.15,  # Important: does momentum confirm phase?
    'time':           0.08,  # Moderate: are time proportions reasonable?
    'mtf_alignment':  0.12,  # Important: does HTF support this count?
    'pattern_match':  0.05,  # Minor: does it look like textbook examples?
}
# Sum = 1.00
```

### 7.3 Confidence Thresholds

| Confidence Score | Classification | Trading Action |
|---|---|---|
| 0.90--1.00 | Very High | Full position size, aggressive entry |
| 0.80--0.89 | High | Standard position size |
| 0.70--0.79 | Moderate | Reduced position (70%) |
| 0.65--0.69 | Acceptable | Small position (50%), tight stops |
| 0.50--0.64 | Low | Monitor only, no trade |
| < 0.50 | Unreliable | Discard count |

---

## 8. Handling Alternate Wave Counts

### 8.1 Philosophy

Elliott Wave analysis inherently produces multiple valid interpretations. The key insight for algorithmic trading is that **we do not need to know the "correct" count---we need to know the trade implications of each plausible count**.

### 8.2 Alternate Count Management

```python
class AlternateCountManager:
    """
    Manages multiple concurrent wave counts with probability weighting.
    Uses Bayesian updating to adjust probabilities as new data arrives.
    """
    
    def __init__(self, max_alternates=3):
        self.max_alternates = max_alternates
        self.counts = []  # List of (WaveCount, probability) tuples
    
    def add_count(self, wave_count, confidence):
        """Add a new wave count with initial probability based on confidence."""
        self.counts.append({
            'count': wave_count,
            'probability': confidence,
            'initial_confidence': confidence,
            'created_at': datetime.now(),
            'update_history': []
        })
        
        # Normalize probabilities
        self.normalize_probabilities()
        
        # Keep only top N counts
        self.counts.sort(key=lambda x: x['probability'], reverse=True)
        self.counts = self.counts[:self.max_alternates]
    
    def update_with_new_data(self, new_price, new_volume, indicators):
        """
        Bayesian update of all alternate counts based on new market data.
        """
        for count_entry in self.counts:
            count = count_entry['count']
            prior = count_entry['probability']
            
            # Calculate likelihood: how well does new data fit this count?
            likelihood = self.calculate_likelihood(count, new_price, new_volume, indicators)
            
            # Bayesian update: P(count|data) proportional to P(data|count) * P(count)
            count_entry['probability'] = prior * likelihood
            count_entry['update_history'].append({
                'time': datetime.now(),
                'price': new_price,
                'prior': prior,
                'likelihood': likelihood,
                'posterior': count_entry['probability']
            })
        
        # Normalize
        self.normalize_probabilities()
        
        # Check for invalidation
        self.check_invalidations(new_price)
        
        # Prune low-probability counts and potentially generate new ones
        self.prune_and_refresh()
    
    def calculate_likelihood(self, count, new_price, new_volume, indicators):
        """
        Calculate P(data|count): how likely is the observed data given this wave count?
        """
        likelihood = 1.0
        
        # Price should be moving in the expected direction for the current wave
        expected_direction = count.expected_current_direction()
        actual_direction = 'up' if new_price > count.last_price else 'down'
        
        if actual_direction == expected_direction:
            likelihood *= 1.2  # Confirming
        else:
            likelihood *= 0.8  # Slightly against
        
        # Price should be within expected range for current wave
        expected_range = count.expected_price_range()
        if expected_range[0] <= new_price <= expected_range[1]:
            likelihood *= 1.3  # Within expected zone
        elif new_price > expected_range[1] * 1.1 or new_price < expected_range[0] * 0.9:
            likelihood *= 0.5  # Significantly outside expected
        
        # Volume should match wave character
        if count.current_wave in [3, 'C'] and new_volume > count.avg_volume * 1.3:
            likelihood *= 1.2  # High volume in Wave 3/C confirms
        elif count.current_wave in [4, 'B'] and new_volume < count.avg_volume:
            likelihood *= 1.1  # Low volume in Wave 4/B confirms
        
        return likelihood
    
    def check_invalidations(self, new_price):
        """Remove counts that are invalidated by Iron Rule violations."""
        valid_counts = []
        
        for count_entry in self.counts:
            is_valid = self.check_rules_still_valid(count_entry['count'], new_price)
            if is_valid:
                valid_counts.append(count_entry)
            else:
                # Log invalidation
                pass
        
        self.counts = valid_counts
    
    def normalize_probabilities(self):
        """Ensure probabilities sum to 1.0."""
        total = sum(c['probability'] for c in self.counts)
        if total > 0:
            for c in self.counts:
                c['probability'] /= total
    
    def get_preferred_count(self):
        """Return the highest-probability count."""
        if self.counts:
            return max(self.counts, key=lambda x: x['probability'])
        return None
    
    def get_trade_consensus(self):
        """
        Determine if all/most alternate counts agree on trade direction.
        This is the most conservative and safest approach.
        """
        if not self.counts:
            return None
        
        directions = []
        for count_entry in self.counts:
            implied_direction = count_entry['count'].implied_trade_direction()
            directions.append((implied_direction, count_entry['probability']))
        
        # Check for consensus
        long_prob = sum(p for d, p in directions if d == 'long')
        short_prob = sum(p for d, p in directions if d == 'short')
        neutral_prob = sum(p for d, p in directions if d == 'neutral')
        
        if long_prob >= 0.70:
            return 'CONSENSUS_LONG', long_prob
        elif short_prob >= 0.70:
            return 'CONSENSUS_SHORT', short_prob
        else:
            return 'NO_CONSENSUS', max(long_prob, short_prob, neutral_prob)
```

### 8.3 When Alternate Counts Diverge

If the preferred count and alternates imply different trade directions:

| Scenario | Action |
|---|---|
| Preferred (70%+) says Long; Alternate says Short | Trade Long with reduced size |
| Preferred (60%) says Long; Alternate (40%) says Short | No trade; wait for clarity |
| All counts agree on Long | Trade Long with full confidence |
| Preferred says trade; Alternates say wait | Trade with reduced size, tight stops |

---

## 9. Multi-Timeframe Alignment

### 9.1 Concept

Multi-timeframe (MTF) alignment is the process of ensuring that wave counts across different timeframes are **fractally consistent**. A valid wave count on one timeframe must decompose properly on lower timeframes and fit within the structure of higher timeframes.

### 9.2 Timeframe Hierarchy

```python
TIMEFRAME_HIERARCHY = {
    'Monthly': {'higher': None, 'lower': 'Weekly', 'bars_per_higher': 4},
    'Weekly': {'higher': 'Monthly', 'lower': 'Daily', 'bars_per_higher': 4},
    'Daily': {'higher': 'Weekly', 'lower': '4H', 'bars_per_higher': 5},
    '4H': {'higher': 'Daily', 'lower': '1H', 'bars_per_higher': 6},
    '1H': {'higher': '4H', 'lower': '15M', 'bars_per_higher': 4},
    '15M': {'higher': '1H', 'lower': '5M', 'bars_per_higher': 3},
    '5M': {'higher': '15M', 'lower': '1M', 'bars_per_higher': 5},
}
```

### 9.3 Alignment Algorithm

```python
def validate_mtf_alignment(htf_count, ltf_count, timeframe_pair):
    """
    Validate that a lower timeframe count is consistent with a higher timeframe count.
    
    Parameters:
        htf_count: Wave count on higher timeframe
        ltf_count: Wave count on lower timeframe
        timeframe_pair: (htf_name, ltf_name)
    
    Returns:
        (alignment_status, alignment_score, details)
    """
    alignment_score = 0.0
    details = []
    
    # Check 1: LTF wave should be within the correct HTF wave
    htf_current_wave = htf_count.current_wave_position
    ltf_position_in_htf = determine_ltf_position_in_htf(ltf_count, htf_count)
    
    if ltf_position_in_htf == htf_current_wave:
        alignment_score += 0.30
        details.append("LTF count is within correct HTF wave")
    else:
        details.append(f"LTF appears to be in HTF {ltf_position_in_htf}, expected {htf_current_wave}")
    
    # Check 2: LTF sub-wave structure matches HTF expectation
    expected_ltf_structure = get_expected_ltf_structure(htf_current_wave)
    actual_ltf_structure = ltf_count.structure_type
    
    if actual_ltf_structure == expected_ltf_structure:
        alignment_score += 0.25
        details.append(f"LTF structure ({actual_ltf_structure}) matches expected")
    else:
        details.append(f"LTF structure ({actual_ltf_structure}) differs from expected ({expected_ltf_structure})")
    
    # Check 3: Direction consistency
    htf_direction = htf_count.current_trend_direction
    ltf_direction = ltf_count.current_trend_direction
    
    # In motive waves (1,3,5), LTF direction should match HTF
    # In corrective waves (2,4), LTF direction should oppose HTF
    htf_wave_type = 'motive' if htf_current_wave in [1, 3, 5] else 'corrective'
    
    if htf_wave_type == 'motive' and ltf_direction == htf_direction:
        alignment_score += 0.25
    elif htf_wave_type == 'corrective' and ltf_direction != htf_direction:
        alignment_score += 0.25
    
    # Check 4: Fibonacci level alignment
    htf_fib_targets = htf_count.current_fibonacci_targets
    ltf_current_price = ltf_count.current_price
    
    for target in htf_fib_targets:
        if abs(ltf_current_price - target['price']) <= target['tolerance']:
            alignment_score += 0.20
            details.append(f"LTF price near HTF Fibonacci target ({target['level']})")
            break
    
    # Categorize alignment
    if alignment_score >= 0.80:
        status = 'confirmed'
    elif alignment_score >= 0.60:
        status = 'compatible'
    elif alignment_score >= 0.40:
        status = 'neutral'
    else:
        status = 'conflicting'
    
    return status, alignment_score, details
```

### 9.4 Top-Down Constraint Propagation

```
FUNCTION propagate_constraints_top_down(timeframes, wave_counts):
    
    FOR EACH tf IN timeframes (highest to lowest):
        IF tf == highest_timeframe:
            CONTINUE  // No higher frame to constrain from
        
        htf = get_higher_timeframe(tf)
        htf_count = wave_counts[htf].preferred_count
        
        // Determine what the HTF count implies for this timeframe
        constraints = derive_ltf_constraints(htf_count, tf)
        
        // constraints include:
        //   - Expected overall direction
        //   - Expected structure type (5-wave or 3-wave)
        //   - Price boundaries (from HTF Fibonacci targets and invalidation levels)
        //   - Approximate time boundaries
        
        // Apply constraints to filter LTF wave candidates
        wave_counts[tf].apply_constraints(constraints)
        
        // Re-score LTF counts with constraint bonus/penalty
        FOR EACH count IN wave_counts[tf].all_counts:
            alignment = validate_mtf_alignment(htf_count, count, (htf, tf))
            count.score *= (0.5 + 0.5 * alignment.score)  // Scale score by alignment
```

---

## 10. Core Logic --- Entry/Exit Decisions

### 10.1 Signal Generation from Wave Count

```python
def generate_trade_signal(preferred_count, alternates, market_data, config):
    """
    Generate trade signal from wave count analysis.
    
    Decision logic:
    1. Determine current wave position
    2. Check if we're at a tradeable juncture
    3. Verify consensus among alternate counts
    4. Calculate entry, SL, TP based on wave context
    5. Validate risk parameters
    """
    
    signal = None
    current_position = preferred_count.current_wave_position
    confidence = preferred_count.confidence_score
    
    # Check alternate count consensus
    consensus, consensus_prob = get_trade_consensus(preferred_count, alternates)
    
    if consensus == 'NO_CONSENSUS':
        return None  # Do not trade when counts disagree
    
    # ─── TRADE SETUP LOGIC ─────────────────────────────────
    
    if current_position == 'WAVE_2_NEAR_COMPLETION':
        if confidence >= 0.70 and check_wave_2_entry_conditions(market_data):
            signal = {
                'type': 'ENTRY',
                'direction': preferred_count.impulse_direction,
                'setup': 'WAVE_2_COMPLETION',
                'entry': market_data['current_price'],
                'stop_loss': preferred_count.wave_1_origin - buffer(market_data),
                'targets': calculate_wave_3_targets(preferred_count),
                'confidence': confidence * consensus_prob,
                'max_risk_pct': 0.015,  # 1.5% for Wave 2 entries
            }
    
    elif current_position == 'WAVE_3_IN_PROGRESS':
        if check_wave_3_pullback_entry(preferred_count, market_data):
            signal = {
                'type': 'ENTRY',
                'direction': preferred_count.impulse_direction,
                'setup': 'WAVE_3_CONTINUATION',
                'entry': market_data['current_price'],
                'stop_loss': preferred_count.last_sub_wave_low - buffer(market_data),
                'targets': calculate_wave_3_extension_targets(preferred_count),
                'confidence': confidence * 0.9,
                'max_risk_pct': 0.012,
            }
    
    elif current_position == 'WAVE_4_NEAR_COMPLETION':
        if confidence >= 0.70 and check_wave_4_entry_conditions(preferred_count, market_data):
            signal = {
                'type': 'ENTRY',
                'direction': preferred_count.impulse_direction,
                'setup': 'WAVE_4_COMPLETION',
                'entry': market_data['current_price'],
                'stop_loss': preferred_count.wave_1_terminus - buffer(market_data),
                'targets': calculate_wave_5_targets(preferred_count),
                'confidence': confidence * consensus_prob,
                'max_risk_pct': 0.012,
            }
    
    elif current_position == 'WAVE_5_NEAR_COMPLETION':
        if confidence >= 0.75 and check_wave_5_reversal_conditions(preferred_count, market_data):
            signal = {
                'type': 'ENTRY',
                'direction': opposite(preferred_count.impulse_direction),
                'setup': 'WAVE_5_REVERSAL',
                'entry': market_data['current_price'],
                'stop_loss': calculate_wave_5_invalidation(preferred_count, market_data),
                'targets': calculate_correction_targets(preferred_count),
                'confidence': confidence * consensus_prob * 0.9,  # Slight discount for counter-trend
                'max_risk_pct': 0.010,
            }
    
    elif current_position == 'CORRECTION_NEAR_COMPLETION':
        if confidence >= 0.70 and check_correction_end_conditions(preferred_count, market_data):
            signal = {
                'type': 'ENTRY',
                'direction': preferred_count.main_trend_direction,
                'setup': 'CORRECTION_END',
                'entry': market_data['current_price'],
                'stop_loss': preferred_count.correction_terminus - buffer(market_data),
                'targets': calculate_new_impulse_targets(preferred_count),
                'confidence': confidence * consensus_prob,
                'max_risk_pct': 0.015,
            }
    
    # Validate signal
    if signal:
        signal = validate_and_enrich_signal(signal, market_data, config)
    
    return signal
```

### 10.2 Position Management Based on Wave Progress

```python
def manage_position_by_wave(active_position, current_count, market_data):
    """
    Manage an existing position based on wave count updates.
    """
    actions = []
    
    wave_progress = current_count.current_wave_position
    
    # If we entered at Wave 2, monitor Wave 3 progress
    if active_position.setup == 'WAVE_2_COMPLETION':
        
        if wave_progress == 'WAVE_3_IN_PROGRESS':
            # Wave 3 confirmed --- hold position
            # Move stop to breakeven after sub-wave i of Wave 3 completes
            if current_count.wave_3_subwave >= 'ii':
                actions.append({
                    'action': 'MOVE_STOP',
                    'new_stop': active_position.entry_price,
                    'reason': 'Wave 3 confirmed, sub-wave ii complete'
                })
        
        elif wave_progress == 'WAVE_3_NEAR_COMPLETION':
            # Partial take profit at Wave 3 target
            actions.append({
                'action': 'PARTIAL_EXIT',
                'percentage': 0.40,
                'reason': 'Wave 3 reaching Fibonacci extension target',
                'trail_stop': True
            })
        
        elif wave_progress == 'WAVE_4_IN_PROGRESS':
            # If still holding from Wave 2 entry
            # Tighten stop to below Wave 4 expected terminus
            actions.append({
                'action': 'TIGHTEN_STOP',
                'new_stop': current_count.wave_1_terminus,
                'reason': 'Wave 4 in progress, protect at non-overlap level'
            })
        
        elif wave_progress == 'WAVE_5_NEAR_COMPLETION':
            # Exit remaining position at Wave 5 target
            actions.append({
                'action': 'EXIT_REMAINING',
                'reason': 'Wave 5 completing, full impulse nearly done'
            })
    
    # If wave count is invalidated
    if current_count.is_invalidated:
        actions.append({
            'action': 'CLOSE_POSITION',
            'urgency': 'IMMEDIATE',
            'reason': f'Wave count invalidated: {current_count.invalidation_reason}'
        })
    
    return actions
```

---

## 11. Technical Specifications

### 11.1 System Requirements

| Component | Specification |
|---|---|
| **Language** | Python 3.10+ (primary), with NumPy/Pandas |
| **Computation** | Multi-threaded for timeframe parallelism |
| **Memory** | ~500MB for full multi-TF analysis of 1 instrument |
| **Latency** | Full re-analysis: < 5 seconds per instrument |
| **Update frequency** | Every new bar close on lowest monitored timeframe |
| **Data storage** | Wave counts persisted for continuity between sessions |

### 11.2 Configuration Parameters

```python
WAVE_COUNTING_CONFIG = {
    # General
    'max_alternate_counts': 3,
    'min_confidence_for_trade': 0.65,
    'min_consensus_probability': 0.70,
    
    # Pivot detection
    'pivot_methods': ['zigzag', 'fractals', 'volume_confirmed'],
    'zigzag_mode': 'atr',
    'zigzag_atr_multiplier': 2.0,
    'fractal_lookback': 2,
    'volume_threshold_for_pivot': 1.3,
    
    # Wave counting
    'max_pivots_per_analysis': 50,
    'max_combinations_to_test': 10000,
    'pruning_threshold': 0.30,  # Discard candidates below 30% initial score
    
    # Timeframes
    'forex_timeframes': ['1M', '1W', '1D', '4H', '1H', '15M'],
    'crypto_timeframes': ['1W', '1D', '4H', '1H', '15M', '5M'],
    'trading_timeframe': '4H',  # Primary decision timeframe
    
    # Fibonacci
    'fibonacci_tolerance': 0.03,  # 3% for level matching
    'cluster_tolerance_atr': 0.5,
    
    # Volume and Momentum
    'rsi_period': 14,
    'rsi_overbought': 70,
    'rsi_oversold': 30,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'volume_ma_period': 20,
    
    # Risk
    'base_risk_pct': 0.01,  # 1% base risk per trade
    'max_risk_pct': 0.02,   # 2% maximum risk per trade
    'min_rr_ratio': 2.0,    # Minimum risk-to-reward
    'atr_sl_multiplier': 1.5,  # ATR multiplier for stop loss buffer
    
    # Performance
    'parallel_timeframes': True,
    'cache_previous_counts': True,
    'incremental_update': True,  # Only re-count from last confirmed pivot
}
```

### 11.3 Data Structures

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

class WaveType(Enum):
    IMPULSE = 'impulse'
    CORRECTION = 'correction'
    DIAGONAL = 'diagonal'

class WaveDirection(Enum):
    BULLISH = 'bullish'
    BEARISH = 'bearish'

class WavePosition(Enum):
    WAVE_1 = 'wave_1'
    WAVE_2 = 'wave_2'
    WAVE_3 = 'wave_3'
    WAVE_4 = 'wave_4'
    WAVE_5 = 'wave_5'
    WAVE_A = 'wave_a'
    WAVE_B = 'wave_b'
    WAVE_C = 'wave_c'
    WAVE_D = 'wave_d'
    WAVE_E = 'wave_e'

@dataclass
class Pivot:
    index: int
    price: float
    pivot_type: str  # 'high' or 'low'
    strength: int
    volume_confirmed: bool
    timestamp: float

@dataclass
class WaveCount:
    wave_type: WaveType
    direction: WaveDirection
    degree: str
    pivots: List[Pivot]
    current_position: WavePosition
    confidence_score: float
    fibonacci_scores: Dict[str, float]
    sub_wave_counts: Optional[Dict[str, 'WaveCount']] = None
    alternate_interpretation: Optional[str] = None
    invalidation_level: Optional[float] = None
    targets: List[Dict[str, float]] = field(default_factory=list)
    
    @property
    def wave_1_range(self):
        return abs(self.pivots[1].price - self.pivots[0].price)
    
    @property
    def wave_3_range(self):
        if len(self.pivots) >= 4:
            return abs(self.pivots[3].price - self.pivots[2].price)
        return None

@dataclass
class TradeSignal:
    direction: str  # 'long' or 'short'
    setup_type: str
    entry_price: float
    stop_loss: float
    take_profits: List[Tuple[float, float]]  # (price, percentage)
    confidence: float
    wave_context: WaveCount
    risk_reward_ratio: float
    position_size_pct: float
    timeframe: str
    expiry_bars: int  # Signal expires after N bars if not triggered
```

---

## 12. Risk Parameters --- SL/TP/RR Calculations

### 12.1 Stop Loss Calculation Engine

```python
def calculate_stop_loss(wave_count, market_data, config):
    """
    Calculate stop loss based on wave context and market conditions.
    
    The stop loss is placed at the level where the wave count would be INVALIDATED.
    """
    direction = wave_count.direction
    atr = market_data['atr']
    buffer = atr * config['atr_sl_multiplier']
    
    if wave_count.current_position == WavePosition.WAVE_2:
        # SL below Wave 1 origin (Rule 1 invalidation)
        if direction == WaveDirection.BULLISH:
            sl = wave_count.pivots[0].price - buffer
        else:
            sl = wave_count.pivots[0].price + buffer
        sl_type = 'RULE_1_INVALIDATION'
    
    elif wave_count.current_position == WavePosition.WAVE_4:
        # SL below Wave 1 terminus (Rule 3 invalidation)
        if direction == WaveDirection.BULLISH:
            sl = wave_count.pivots[1].price - buffer
        else:
            sl = wave_count.pivots[1].price + buffer
        sl_type = 'RULE_3_INVALIDATION'
    
    elif wave_count.current_position == WavePosition.WAVE_5:
        # For reversal: SL above Wave 5 max possible extension
        wave_1_range = wave_count.wave_1_range
        wave_4_end = wave_count.pivots[4].price
        
        if direction == WaveDirection.BULLISH:
            # Short reversal: SL above extended W5
            sl = wave_4_end + 1.618 * wave_1_range + buffer
        else:
            sl = wave_4_end - 1.618 * wave_1_range - buffer
        sl_type = 'WAVE_5_EXTENSION_LIMIT'
    
    elif wave_count.current_position == WavePosition.WAVE_C:
        # SL beyond the next Fibonacci extension
        wave_a_range = abs(wave_count.correction_pivots[1].price - 
                          wave_count.correction_pivots[0].price)
        wave_b_end = wave_count.correction_pivots[2].price
        
        if direction == WaveDirection.BEARISH:  # Bearish correction, buying at C end
            sl = wave_b_end - 1.618 * wave_a_range - buffer
        else:
            sl = wave_b_end + 1.618 * wave_a_range + buffer
        sl_type = 'WAVE_C_EXTENSION_LIMIT'
    
    else:
        # Default: ATR-based stop
        if direction == WaveDirection.BULLISH:
            sl = market_data['current_price'] - 2 * atr
        else:
            sl = market_data['current_price'] + 2 * atr
        sl_type = 'ATR_DEFAULT'
    
    return {
        'price': sl,
        'type': sl_type,
        'distance': abs(market_data['current_price'] - sl),
        'distance_atr': abs(market_data['current_price'] - sl) / atr,
    }
```

### 12.2 Take Profit Calculation Engine

```python
def calculate_take_profits(wave_count, entry_price, market_data, config):
    """
    Calculate multiple take profit levels based on Fibonacci targets.
    """
    targets = []
    direction = wave_count.direction
    
    if wave_count.current_position in [WavePosition.WAVE_2, WavePosition.WAVE_4]:
        # Expecting next impulse wave
        wave_1_range = wave_count.wave_1_range
        reference_price = entry_price
        
        # TP1: Conservative (100% of Wave 1)
        tp1 = reference_price + wave_1_range * (1 if direction == WaveDirection.BULLISH else -1)
        targets.append({'price': tp1, 'ratio': 1.000, 'percentage': 0.40, 'label': 'TP1_W3_100'})
        
        # TP2: Standard (161.8% of Wave 1)
        tp2 = reference_price + 1.618 * wave_1_range * (1 if direction == WaveDirection.BULLISH else -1)
        targets.append({'price': tp2, 'ratio': 1.618, 'percentage': 0.35, 'label': 'TP2_W3_1618'})
        
        # TP3: Extended (261.8% of Wave 1)
        tp3 = reference_price + 2.618 * wave_1_range * (1 if direction == WaveDirection.BULLISH else -1)
        targets.append({'price': tp3, 'ratio': 2.618, 'percentage': 0.25, 'label': 'TP3_W3_2618'})
    
    elif wave_count.current_position == WavePosition.WAVE_5:
        # Expecting correction (reversal trade)
        impulse_range = abs(wave_count.pivots[-1].price - wave_count.pivots[0].price)
        
        # TP1: 38.2% retracement of impulse
        tp1 = entry_price - 0.382 * impulse_range * (1 if direction == WaveDirection.BULLISH else -1)
        targets.append({'price': tp1, 'ratio': 0.382, 'percentage': 0.40, 'label': 'TP1_Retrace_382'})
        
        # TP2: 50% retracement
        tp2 = entry_price - 0.500 * impulse_range * (1 if direction == WaveDirection.BULLISH else -1)
        targets.append({'price': tp2, 'ratio': 0.500, 'percentage': 0.35, 'label': 'TP2_Retrace_500'})
        
        # TP3: 61.8% retracement
        tp3 = entry_price - 0.618 * impulse_range * (1 if direction == WaveDirection.BULLISH else -1)
        targets.append({'price': tp3, 'ratio': 0.618, 'percentage': 0.25, 'label': 'TP3_Retrace_618'})
    
    return targets
```

### 12.3 Risk-to-Reward Calculation

$$RR = \frac{\sum_{i} w_i \times |TP_i - P_{\text{entry}}|}{|P_{\text{entry}} - SL|}$$

where $w_i$ is the percentage of position exited at $TP_i$.

**Weighted Average RR:**
```python
def calculate_weighted_rr(entry, stop_loss, take_profits):
    """
    Calculate weighted-average risk-to-reward ratio.
    """
    sl_distance = abs(entry - stop_loss)
    
    if sl_distance == 0:
        return 0
    
    weighted_reward = sum(
        tp['percentage'] * abs(tp['price'] - entry) 
        for tp in take_profits
    )
    
    return weighted_reward / sl_distance
```

### 12.4 Position Size by Wave Context

$$\text{Lots} = \frac{\text{Account} \times R \times C_{\text{wave}} \times C_{\text{consensus}}}{\text{SL\_Distance} \times \text{Pip\_Value}}$$

| Factor | Range | Description |
|---|---|---|
| $R$ | 0.01--0.02 | Base risk percentage |
| $C_{\text{wave}}$ | 0.65--1.00 | Wave count confidence |
| $C_{\text{consensus}}$ | 0.70--1.00 | Alternate count consensus |

---

## 13. Execution Flow --- Complete Pseudocode

### 13.1 Main Loop

```
ALGORITHM: ElliotWaveTrader_MainLoop

INITIALIZE:
    account = load_account_state()
    config = load_configuration()
    wave_engine = WaveCountingEngine(config)
    signal_generator = SignalGenerator(config)
    risk_manager = RiskManager(account, config)
    position_manager = PositionManager(account, config)
    
    active_positions = load_active_positions()
    alternate_manager = AlternateCountManager(max_alternates=3)

LOOP (on each new bar close):

    // ═══════════════════════════════════════════════════════════
    // PHASE 1: DATA ACQUISITION
    // ═══════════════════════════════════════════════════════════
    
    FOR EACH instrument IN config.instruments:
        FOR EACH timeframe IN config.timeframes:
            market_data[instrument][timeframe] = fetch_latest_data(instrument, timeframe)
    
    // ═══════════════════════════════════════════════════════════
    // PHASE 2: WAVE ANALYSIS
    // ═══════════════════════════════════════════════════════════
    
    FOR EACH instrument IN config.instruments:
        
        // Step 2a: Detect pivots (multi-method)
        pivots = {}
        FOR EACH tf IN config.timeframes:
            pivots[tf] = wave_engine.detect_pivots(market_data[instrument][tf])
        
        // Step 2b: Generate wave counts (top-down)
        wave_counts = {}
        FOR EACH tf IN config.timeframes (highest to lowest):
            candidates = wave_engine.generate_candidates(pivots[tf])
            validated = wave_engine.validate_all(candidates)
            scored = wave_engine.score_all(validated, market_data[instrument][tf])
            wave_counts[tf] = scored
        
        // Step 2c: Align across timeframes
        aligned_counts = wave_engine.align_mtf(wave_counts)
        
        // Step 2d: Update alternate count manager
        alternate_manager.update_counts(aligned_counts, market_data[instrument])
        
        preferred = alternate_manager.get_preferred_count()
        consensus = alternate_manager.get_trade_consensus()
    
    // ═══════════════════════════════════════════════════════════
    // PHASE 3: SIGNAL GENERATION
    // ═══════════════════════════════════════════════════════════
    
    FOR EACH instrument IN config.instruments:
        
        signal = signal_generator.generate(
            preferred_count = alternate_manager.get_preferred_count(),
            alternates = alternate_manager.counts,
            market_data = market_data[instrument],
            config = config
        )
        
        IF signal IS NOT None:
            // Validate risk parameters
            IF risk_manager.validate_signal(signal, account):
                // Check for existing positions in same instrument
                existing = position_manager.get_positions(instrument)
                
                IF existing AND signal.direction == existing.direction:
                    // Same direction: consider adding to position
                    IF risk_manager.can_add_to_position(existing, signal):
                        EXECUTE_ADD(signal)
                
                ELIF existing AND signal.direction != existing.direction:
                    // Opposite direction: close existing and reverse?
                    IF signal.confidence >= 0.80:
                        CLOSE_POSITION(existing, reason="Opposite signal with high confidence")
                        EXECUTE_NEW(signal)
                    ELSE:
                        LOG("Conflicting signal, maintaining existing position")
                
                ELSE:
                    // No existing position: execute new trade
                    EXECUTE_NEW(signal)
    
    // ═══════════════════════════════════════════════════════════
    // PHASE 4: POSITION MANAGEMENT
    // ═══════════════════════════════════════════════════════════
    
    FOR EACH position IN active_positions:
        
        // Update wave context for this position
        current_count = alternate_manager.get_preferred_count()
        
        // Check for wave count invalidation
        IF current_count.is_invalidated:
            CLOSE_POSITION(position, reason="Wave count invalidation")
            CONTINUE
        
        // Manage based on wave progress
        actions = manage_position_by_wave(position, current_count, market_data)
        
        FOR EACH action IN actions:
            EXECUTE_ACTION(action, position)
        
        // Update trailing stop if applicable
        IF position.has_trailing_stop:
            new_trail = calculate_fibonacci_trailing_stop(
                position.entry_price,
                market_data['current_price'],
                position.direction,
                market_data['atr']
            )
            IF new_trail_is_better(new_trail, position.current_stop):
                UPDATE_STOP(position, new_trail)
    
    // ═══════════════════════════════════════════════════════════
    // PHASE 5: REPORTING AND LOGGING
    // ═══════════════════════════════════════════════════════════
    
    LOG_STATE(
        wave_counts = alternate_manager.counts,
        active_positions = active_positions,
        signals_generated = signals,
        account_state = account
    )

END LOOP
```

### 13.2 Trade Execution Sub-Procedure

```
FUNCTION EXECUTE_NEW(signal):
    
    // Calculate final position size
    risk_amount = account.balance * signal.position_size_pct * signal.confidence
    sl_distance = abs(signal.entry_price - signal.stop_loss)
    pip_value = get_pip_value(signal.instrument, account.currency)
    
    position_size = risk_amount / (sl_distance * pip_value)
    position_size = ROUND_TO_LOT(position_size)
    
    // Place orders
    entry_order = PLACE_ORDER(
        instrument = signal.instrument,
        direction = signal.direction,
        size = position_size,
        type = 'MARKET',  // or 'LIMIT' if waiting for exact level
        stop_loss = signal.stop_loss,
    )
    
    // Place take profit orders (OCO/bracket)
    FOR EACH tp IN signal.take_profits:
        tp_size = position_size * tp.percentage
        PLACE_TP_ORDER(
            instrument = signal.instrument,
            direction = OPPOSITE(signal.direction),
            size = tp_size,
            price = tp.price,
            type = 'LIMIT'
        )
    
    // Record position
    new_position = Position(
        instrument = signal.instrument,
        direction = signal.direction,
        entry_price = signal.entry_price,
        size = position_size,
        stop_loss = signal.stop_loss,
        take_profits = signal.take_profits,
        setup_type = signal.setup_type,
        wave_context = signal.wave_context,
        confidence = signal.confidence,
        opened_at = NOW()
    )
    
    active_positions.APPEND(new_position)
    
    RETURN new_position
```

---

## 14. Performance Optimization

### 14.1 Pruning Strategies

The brute-force combinatorial approach in Section 2 is impractical. Key optimization strategies:

**1. Rule-Based Early Pruning**

```python
def quick_validate(candidate):
    """
    Fast pre-filter before full scoring.
    Eliminates obviously invalid candidates.
    """
    # Quick direction check
    if candidate['type'] == 'impulse':
        pivots = candidate['pivots']
        # Waves 1, 3, 5 must be in same direction
        move_1 = pivots[1] - pivots[0]
        move_3 = pivots[3] - pivots[2]
        move_5 = pivots[5] - pivots[4]
        
        if not (same_sign(move_1, move_3) and same_sign(move_1, move_5)):
            return False
        
        # Quick Rule 1 check
        retrace_2 = abs(pivots[2] - pivots[1]) / abs(pivots[1] - pivots[0])
        if retrace_2 >= 1.0:
            return False
        
        # Quick Rule 3 check (non-overlap)
        if move_1 > 0:  # Bullish
            if pivots[4] <= pivots[1]:  # Wave 4 low below Wave 1 high
                return False
        else:  # Bearish
            if pivots[4] >= pivots[1]:
                return False
        
        # Quick Rule 2 check
        range_1 = abs(pivots[1] - pivots[0])
        range_3 = abs(pivots[3] - pivots[2])
        range_5 = abs(pivots[5] - pivots[4])
        if range_3 < range_1 and range_3 < range_5:
            return False
    
    return True
```

**2. Hierarchical Search (Top-Down Constraint)**

Instead of testing all combinations, use the highest timeframe count to constrain lower timeframe searches:

```python
def constrained_search(pivots, htf_constraints):
    """
    Only search for wave patterns within HTF-defined boundaries.
    """
    # HTF tells us approximate start/end of each wave
    search_regions = htf_constraints.get_wave_regions()
    
    candidates = []
    for region in search_regions:
        # Only search pivots within this region
        region_pivots = filter_pivots_by_region(pivots, region)
        # Generate candidates only from filtered pivots
        region_candidates = generate_wave_candidates(region_pivots)
        candidates.extend(region_candidates)
    
    return candidates
```

**3. Incremental Updates**

Don't re-count everything on each bar. Only update from the last confirmed pivot:

```python
def incremental_update(previous_count, new_data):
    """
    Update wave count incrementally rather than full re-analysis.
    """
    # Check if the last pivot in our count is still valid
    last_pivot = previous_count.pivots[-1]
    
    if is_pivot_still_valid(last_pivot, new_data):
        # Just extend the current wave
        previous_count.extend_current_wave(new_data)
    else:
        # A new pivot has formed; partial re-analysis from last confirmed
        confirmed_pivots = previous_count.get_confirmed_pivots()
        new_pivot = detect_new_pivot(new_data)
        
        if new_pivot:
            candidates = generate_candidates_from(confirmed_pivots + [new_pivot])
            # Score and return updated counts
            return score_candidates(candidates, new_data)
    
    return previous_count
```

### 14.2 Caching Strategy

```python
CACHE_POLICY = {
    'pivot_cache_ttl': '1 bar',           # Pivots recalculated each bar
    'htf_count_cache_ttl': '6 bars',      # HTF counts updated less frequently
    'fibonacci_levels_cache_ttl': '1 bar', # Recalc on each bar
    'cluster_map_cache_ttl': '1 bar',     # Recalc on each bar
    'confidence_scores_cache_ttl': '1 bar',
}
```

### 14.3 Parallel Processing

```python
def parallel_wave_analysis(instruments, timeframes, market_data):
    """
    Run wave analysis in parallel across instruments and timeframes.
    """
    from concurrent.futures import ThreadPoolExecutor
    
    results = {}
    
    with ThreadPoolExecutor(max_workers=len(instruments) * len(timeframes)) as executor:
        futures = {}
        
        for instrument in instruments:
            for tf in timeframes:
                key = (instrument, tf)
                futures[key] = executor.submit(
                    analyze_single_timeframe,
                    market_data[instrument][tf],
                    tf
                )
        
        for key, future in futures.items():
            results[key] = future.result()
    
    return results
```

---

## 15. References

### 15.1 Primary Sources

1. **Elliott, R.N.** (1938). *The Wave Principle*. Original monograph.
2. **Elliott, R.N.** (1946). *Nature's Law: The Secret of the Universe*.
3. **Frost, A.J. & Prechter, R.R.** (2017). *Elliott Wave Principle: Key to Market Behavior*. 11th Ed. New Classics Library.
4. **Neely, G.** (1988). *Mastering Elliott Wave*. Windsor Books. (Most rigorous rule-based approach)
5. **Prechter, R.R.** (2005). *Prechter's Perspective*. New Classics Library.

### 15.2 Algorithmic and Computational

6. **Poser, S.W.** (2003). *Applying Elliott Wave Theory Profitably*. Wiley.
7. **Miner, R.C.** (2009). *High Probability Trading Strategies*. Wiley.
8. **Volna, E. et al.** (2013). "Elliott Wave Theory and Neuro-Fuzzy Systems in Stock Market Prediction." *Expert Systems with Applications*.
9. **Li, J. & Shang, P.** (2018). "Elliott Wave Theory in Market Prediction using Convolutional Neural Networks." *Computational Economics*.

### 15.3 Mathematical and Algorithmic Foundations

10. **Mandelbrot, B.** (1982). *The Fractal Geometry of Nature*. W.H. Freeman.
11. **Peters, E.E.** (1994). *Fractal Market Analysis*. Wiley.
12. **Lo, A.W.** (2004). "The Adaptive Markets Hypothesis." *Journal of Portfolio Management*.
13. **Fama, E.F.** (1970). "Efficient Capital Markets." *Journal of Finance*.

### 15.4 Technical Analysis Software References

14. **ELWAVE** (Prognosis Software) --- Commercial Elliott Wave counting software
15. **Advanced GET** (eSignal) --- Automated wave counting with oscillator
16. **WaveBasis** (WaveBasis.com) --- Cloud-based Elliott Wave algorithm

### 15.5 Quantitative Trading

17. **Chan, E.** (2009). *Quantitative Trading*. Wiley.
18. **Narang, R.K.** (2013). *Inside the Black Box: A Simple Guide to Quantitative and High Frequency Trading*. Wiley.
19. **De Prado, M.L.** (2018). *Advances in Financial Machine Learning*. Wiley.

---

## Document Cross-References

| Document | Path | Relationship |
|---|---|---|
| Overview | `00_overview.md` | Conceptual foundation |
| Impulse Waves | `01_impulse_waves.md` | Impulse wave rules and targets |
| Corrective Waves | `02_corrective_waves.md` | Corrective pattern identification |
| Fibonacci Targets | `03_fibonacci_targets.md` | Fibonacci calculation methods |
| Multi-Timeframe | `../11_multi_timeframe_analysis/` | MTF alignment methodology |
| Order Flow | `../03_order_flow_liquidity/` | Volume/order flow confirmation |
| Smart Money | `../04_smart_money_concepts/` | Institutional behavior at wave terminals |

---

## Appendix A: Quick Reference Cheat Sheet

### Iron Rules (Must NEVER be violated)
1. **Wave 2 < 100% of Wave 1** (never goes past origin)
2. **Wave 3 is NOT the shortest** (of 1, 3, and 5)
3. **Wave 4 does NOT overlap Wave 1** (except diagonals)

### Most Common Fibonacci Relationships
| Wave | Target | Most Common |
|---|---|---|
| Wave 2 | Retrace of W1 | 61.8% |
| Wave 3 | Extension of W1 | 161.8% |
| Wave 4 | Retrace of W3 | 38.2% |
| Wave 5 | Ratio to W1 | 100% (equality) |
| Wave C | Ratio to A | 100% (equality) |

### Minimum Confidence for Trading
- **0.65** = Minimum for any trade
- **0.70** = Standard trading threshold
- **0.80** = High-confidence trades (larger size)
- **0.90** = Very high-confidence (maximum allocation)

### Minimum Risk-to-Reward
- **2:1** = Minimum for all trades
- **3:1** = Preferred for counter-trend trades
- **5:1** = Target for Wave 2 entries with Wave 3 target

---

*This document provides the complete algorithmic framework for automated Elliott Wave counting in the Multi-Agent AI Trading System. It should be used in conjunction with all other Elliott Wave documents in this directory. The algorithm is designed for real-time operation with incremental updates, multi-timeframe validation, and robust confidence scoring to ensure only high-probability trades are generated.*
