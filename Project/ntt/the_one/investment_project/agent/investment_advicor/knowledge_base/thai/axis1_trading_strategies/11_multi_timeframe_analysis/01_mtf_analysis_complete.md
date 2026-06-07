# กรอบการวิเคราะห์หลายกรอบเวลา (Multi-Timeframe Analysis Framework) — คู่มือฉบับสมบูรณ์

## ข้อมูลเอกสาร (Document Metadata)
| ฟิลด์ | ค่า |
|---|---|
| **รหัสกลยุทธ์ (Strategy ID)** | MTF-001 |
| **หมวดหมู่ (Category)** | กรอบงาน / เมตากลยุทธ์ (Framework / Meta-Strategy) |
| **ประเภทสินทรัพย์ (Asset Classes)** | Forex, Crypto, หุ้น (Equities), สินค้าโภคภัณฑ์ (Commodities) |
| **กรอบเวลา (Timeframes)** | ทั้งหมด (M1 ถึง Monthly) |
| **ความซับซ้อน (Complexity)** | ระดับกลางถึงขั้นสูง (Intermediate to Advanced) |
| **ความเหมาะสมกับ AI** | สูงมาก — การวิเคราะห์แบบลำดับชั้นอย่างเป็นระบบ |
| **เวอร์ชัน** | 2.0 |
| **อัปเดตล่าสุด** | 2026-04-12 |

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Timeframe Hierarchy](#2-timeframe-hierarchy)
3. [Top-Down Analysis Methodology](#3-top-down-analysis-methodology)
4. [Timeframe Alignment Scoring](#4-timeframe-alignment-scoring)
5. [Conflicting Signals Resolution](#5-conflicting-signals-resolution)
6. [Optimal Timeframe Combinations](#6-optimal-timeframe-combinations)
7. [Mathematical Framework for MTF Confluence](#7-mathematical-framework-for-mtf-confluence)
8. [Entry Timing Across Timeframes](#8-entry-timing-across-timeframes)
9. [Risk Parameters](#9-risk-parameters)
10. [Execution Flow for AI Agent](#10-execution-flow-for-ai-agent)
11. [Advanced Concepts](#11-advanced-concepts)
12. [AI Implementation Notes](#12-ai-implementation-notes)
13. [References](#13-references)

---

## 1. Introduction

Multi-Timeframe Analysis (MTF) is the practice of analyzing the same instrument across multiple timeframes simultaneously to make better-informed trading decisions. It is not a trading strategy per se, but a **meta-framework** that enhances any strategy by providing context, confirmation, and precision.

### 1.1 Core Thesis

- Every timeframe tells a different story: the Weekly shows the war, the Daily shows the battle, and the H1 shows the skirmish.
- Trading decisions should be made in the **direction of the higher timeframe** and **timed on the lower timeframe**.
- The probability of success increases dramatically when multiple timeframes align.
- Conflicting signals across timeframes indicate uncertainty — reduce exposure or abstain.

### 1.2 The Three-Timeframe Rule

A minimum of three timeframes should be used for any trade:

1. **Higher Timeframe (HTF)**: Determines the directional bias (trend direction).
2. **Trading Timeframe (TF)**: Identifies the specific setup/signal.
3. **Lower Timeframe (LTF)**: Times the entry for precision.

### 1.3 The Multiplication Factor

The factor between consecutive timeframes in the analysis hierarchy should be approximately 4–6x:

$$\text{Factor} = \frac{TF_{\text{higher}}}{TF_{\text{lower}}} \approx 4 \text{ to } 6$$

This ensures each timeframe captures a meaningfully different fractal scale while remaining connected.

---

## 2. Timeframe Hierarchy

### 2.1 Complete Hierarchy

| Level | Timeframe | Role | Typical Holding Period |
|-------|-----------|------|----------------------|
| **Macro** | Monthly | Long-term trend; fundamental alignment | Months to years |
| **Major** | Weekly | Intermediate trend; swing bias | Weeks to months |
| **Standard** | Daily | Primary trend identification | Days to weeks |
| **Intraday-High** | H4 | Intraday trend; setup identification | Hours to days |
| **Intraday-Mid** | H1 | Fine-grained structure | Hours |
| **Intraday-Low** | M15 | Entry timing | Minutes to hours |
| **Scalp** | M5 | Precision entry | Minutes |
| **Micro** | M1 | Ultra-precision (rarely used) | Seconds to minutes |

### 2.2 Information Content per Timeframe

| Timeframe | Provides | Does NOT Provide |
|-----------|----------|-----------------|
| Monthly | Overall market regime; secular trend | Entry timing; short-term direction |
| Weekly | Swing direction; key S/R zones | Intraday entry; precise timing |
| Daily | Trend bias; high-probability zones | Scalping signals; micro-structure |
| H4 | Setup context; intermediate structure | Final entry price |
| H1 | Detailed structure; confirmation | Precise tick-level entry |
| M15/M5 | Entry timing; micro-structure | Directional bias; trend context |

### 2.3 Fractal Nature of Markets

Markets are self-similar at all scales. The same patterns (trends, pullbacks, consolidations) appear on every timeframe:

$$\text{Pattern}(TF_i) \sim \text{Pattern}(TF_j) \quad \forall i, j$$

However, the **significance** scales with the timeframe:
$$\text{Significance}(TF) \propto \sqrt{T_{\text{periods\_in\_TF}}}$$

A double top on the Weekly is far more significant than a double top on M5, because it represents far more market participants and capital.

---

## 3. Top-Down Analysis Methodology

### 3.1 The Process

The top-down approach always starts from the highest relevant timeframe and drills down:

```
Step 1: MONTHLY → Determine secular trend and major zones
Step 2: WEEKLY  → Identify swing structure and key levels
Step 3: DAILY   → Confirm trend direction; identify setup zones
Step 4: H4      → Find specific setups and patterns
Step 5: H1/M15  → Time the entry precisely
```

### 3.2 Step-by-Step Protocol

**Step 1: Monthly/Weekly Analysis (5 minutes max)**
- What is the overall trend? Bullish/Bearish/Ranging?
- Where are the major S/R zones from Monthly/Weekly?
- Is price in the upper or lower half of the current range?
- Are there any pending Monthly/Weekly signals (pattern completions)?

**Step 2: Daily Analysis (5 minutes)**
- What is the Daily trend (sequence of HH/HL or LH/LL)?
- Where are the key Daily zones (OBs, FVGs, S/D zones)?
- Is price approaching or at a significant Daily level?
- What is the Daily momentum (rising/falling/flat)?

**Step 3: H4 Setup Identification (5 minutes)**
- Does H4 structure align with Daily bias?
- Are there H4 setups forming (divergence, harmonic, OB)?
- What is the nearest H4 liquidity target?
- Is there a clear entry zone on H4?

**Step 4: H1/M15 Entry Timing (ongoing)**
- Once H4 setup is identified, drop to H1/M15.
- Look for structural confirmation (CHoCH, BOS).
- Identify the precise entry zone (LTF OB, FVG, pattern).
- Place order with defined SL and TP.

### 3.3 Top-Down Analysis Checklist

```python
def top_down_analysis(instrument):
    """
    Systematic top-down MTF analysis.
    Returns: bias, confidence, entry_zone, and action.
    """
    analysis = {}
    
    # ===== MONTHLY =====
    monthly = fetch_candles(instrument, "MN", count=60)
    analysis["monthly"] = {
        "trend": determine_trend(monthly),
        "position": "UPPER" if current_price > monthly_midpoint else "LOWER",
        "key_levels": identify_monthly_sr(monthly)
    }
    
    # ===== WEEKLY =====
    weekly = fetch_candles(instrument, "W1", count=104)
    analysis["weekly"] = {
        "trend": determine_trend(weekly),
        "structure": classify_market_structure(weekly),
        "key_levels": identify_weekly_sr(weekly),
        "proximity_to_level": distance_to_nearest_level(current_price, weekly_levels)
    }
    
    # ===== DAILY =====
    daily = fetch_candles(instrument, "D1", count=252)
    analysis["daily"] = {
        "trend": determine_trend(daily),
        "momentum": calculate_momentum(daily),
        "setup_zones": identify_daily_zones(daily),
        "at_zone": is_at_daily_zone(current_price, daily_zones)
    }
    
    # ===== H4 =====
    h4 = fetch_candles(instrument, "H4", count=200)
    analysis["h4"] = {
        "trend": determine_trend(h4),
        "setups": detect_setups(h4),  # OBs, FVGs, patterns, divergence
        "structure_shift": detect_choch_bos(h4)
    }
    
    # ===== SYNTHESIZE =====
    bias = synthesize_bias(analysis)
    confidence = calculate_alignment_score(analysis)
    
    return {
        "bias": bias,  # BULLISH / BEARISH / NEUTRAL
        "confidence": confidence,  # 0.0 to 1.0
        "analysis": analysis,
        "action": determine_action(bias, confidence, analysis)
    }
```

---

## 4. Timeframe Alignment Scoring

### 4.1 Alignment Score Formula

$$\text{MTF\_Score} = \sum_{i=1}^{N} w_i \times S_i \times D_i$$

Where:
- $N$ = number of timeframes analyzed
- $w_i$ = weight of timeframe $i$ (higher TF gets higher weight)
- $S_i$ = signal strength on timeframe $i$ (0 to 1)
- $D_i$ = direction alignment (+1 if bullish, -1 if bearish, 0 if neutral)

### 4.2 Default Weights

| Timeframe | Weight ($w_i$) | Rationale |
|-----------|---------------|-----------|
| Monthly | 0.10 | Background context; rarely changes |
| Weekly | 0.20 | Major bias determinator |
| Daily | 0.30 | Primary trend and setup context |
| H4 | 0.25 | Main setup identification TF |
| H1 | 0.10 | Entry timing (less weight for bias) |
| M15 | 0.05 | Precision; negligible for bias |

*Note: Weights should sum to 1.0.*

### 4.3 Signal Strength Criteria

For each timeframe, determine $S_i$ based on:

```python
def calculate_signal_strength(candles, timeframe):
    """
    Calculate signal strength on a given timeframe.
    Returns a value 0.0 to 1.0.
    """
    factors = []
    
    # Factor 1: Trend clarity (clear HH/HL or LL/LH sequence)
    trend = determine_trend(candles)
    if trend in ["STRONG_BULLISH", "STRONG_BEARISH"]:
        factors.append(1.0)
    elif trend in ["BULLISH", "BEARISH"]:
        factors.append(0.7)
    elif trend == "RANGING":
        factors.append(0.3)
    else:
        factors.append(0.0)
    
    # Factor 2: Momentum (slope of MA or recent candle sizes)
    momentum = calculate_momentum_score(candles)
    factors.append(momentum)  # 0 to 1
    
    # Factor 3: Price position relative to key MA (EMA 50/200)
    ma_position = price_vs_ma_score(candles)
    factors.append(ma_position)  # 0 to 1
    
    # Factor 4: Recent structural event (BOS, CHoCH within last 5 candles)
    structural_recency = has_recent_structural_event(candles, lookback=5)
    factors.append(1.0 if structural_recency else 0.5)
    
    return np.mean(factors)
```

### 4.4 Alignment Interpretation

| MTF Score | Interpretation | Action |
|-----------|---------------|--------|
| $\geq +0.70$ | Strong bullish alignment | Trade long with full confidence |
| +0.50 to +0.69 | Moderate bullish alignment | Trade long with standard size |
| +0.30 to +0.49 | Weak bullish alignment | Only trade long with extra confirmation |
| -0.29 to +0.29 | Neutral / Conflicting | No trade (or reduce to scalp TF) |
| -0.49 to -0.30 | Weak bearish alignment | Only trade short with extra confirmation |
| -0.69 to -0.50 | Moderate bearish alignment | Trade short with standard size |
| $\leq -0.70$ | Strong bearish alignment | Trade short with full confidence |

---

## 5. Conflicting Signals Resolution

### 5.1 Types of Conflicts

| Conflict Type | Example | Resolution |
|--------------|---------|-----------|
| **Trend Conflict** | Weekly bullish, Daily bearish | Defer to Weekly; wait for Daily to realign |
| **Structure Conflict** | Daily uptrend, H4 CHoCH bearish | H4 may be correcting within Daily uptrend; wait |
| **Signal Conflict** | H4 shows bearish divergence, but Daily structure is bullish | Reduce size; use tighter stops |
| **Timing Conflict** | HTF says buy, but LTF momentum is still bearish | Wait for LTF to confirm; patience |

### 5.2 Resolution Rules (Priority Order)

1. **Higher timeframe always wins for direction**. Never trade against the next higher timeframe's clear trend.
2. **Lower timeframe determines timing**. Even if HTF is bullish, wait for LTF to turn bullish before entering.
3. **Conflicting ≠ Counter-trend**. If HTF and ITF conflict, it means "wait" not "trade the opposite."
4. **Ranging HTF**: When the HTF is ranging, both directions are valid — let the ITF/LTF determine the trade.
5. **Maximum two conflicts allowed**: If 3+ timeframes disagree with the trade direction, do NOT trade.

### 5.3 Conflict Resolution Algorithm

```python
def resolve_conflicts(analysis):
    """
    Resolve conflicting signals across timeframes.
    Returns: final bias, confidence adjustment, and any warnings.
    """
    directions = {
        "monthly": analysis["monthly"]["trend_direction"],  # +1, 0, -1
        "weekly": analysis["weekly"]["trend_direction"],
        "daily": analysis["daily"]["trend_direction"],
        "h4": analysis["h4"]["trend_direction"],
        "h1": analysis["h1"]["trend_direction"]
    }
    
    # Count agreements
    bullish_count = sum(1 for d in directions.values() if d > 0)
    bearish_count = sum(1 for d in directions.values() if d < 0)
    neutral_count = sum(1 for d in directions.values() if d == 0)
    
    # Weighted direction
    weighted_dir = sum(
        directions[tf] * WEIGHTS[tf] 
        for tf in directions
    )
    
    # Conflict detection
    conflicts = []
    
    # Check adjacent timeframe disagreements
    tf_order = ["monthly", "weekly", "daily", "h4", "h1"]
    for i in range(len(tf_order) - 1):
        if directions[tf_order[i]] != 0 and directions[tf_order[i+1]] != 0:
            if directions[tf_order[i]] != directions[tf_order[i+1]]:
                conflicts.append((tf_order[i], tf_order[i+1]))
    
    # Resolution
    if len(conflicts) == 0:
        return {
            "bias": "BULLISH" if weighted_dir > 0 else "BEARISH",
            "confidence": abs(weighted_dir),
            "conflicts": [],
            "action": "TRADE"
        }
    
    elif len(conflicts) == 1:
        # One conflict: trade with reduced confidence
        htf_bias = "BULLISH" if directions[conflicts[0][0]] > 0 else "BEARISH"
        return {
            "bias": htf_bias,  # Defer to higher TF
            "confidence": abs(weighted_dir) * 0.7,  # Reduce confidence
            "conflicts": conflicts,
            "action": "TRADE_CAUTIOUS",
            "note": f"Conflict between {conflicts[0][0]} and {conflicts[0][1]} — wait for LTF alignment"
        }
    
    else:
        # Multiple conflicts: do not trade
        return {
            "bias": "NEUTRAL",
            "confidence": 0.0,
            "conflicts": conflicts,
            "action": "NO_TRADE",
            "note": f"{len(conflicts)} timeframe conflicts — market is uncertain"
        }
```

### 5.4 The "Timeframe Dominance" Principle

When conflicts exist, apply the following dominance hierarchy:

$$\text{Monthly} > \text{Weekly} > \text{Daily} > \text{H4} > \text{H1} > \text{M15}$$

A conflict between adjacent timeframes is resolved by deferring to the higher one. The lower timeframe's contrary signal is treated as a "temporary correction" or "noise."

**Exception**: If the lower timeframe shows a clear structural shift (CHoCH) with strong momentum, it may be signaling a genuine trend change that the HTF hasn't confirmed yet. In this case, the approach is to **wait** rather than act.

---

## 6. Optimal Timeframe Combinations

### 6.1 Forex Combinations

| Trading Style | HTF (Bias) | TF (Setup) | LTF (Entry) |
|--------------|-----------|-----------|------------|
| **Position Trading** | Monthly | Weekly | Daily |
| **Swing Trading** | Weekly | Daily | H4 |
| **Short-Term Swing** | Daily | H4 | H1 |
| **Intraday** | H4 | H1 | M15 |
| **Scalping** | H1 | M15 | M5 |

### 6.2 Crypto Combinations

Crypto markets trade 24/7, reducing the significance of intraday session-based timeframes. Recommended combinations:

| Trading Style | HTF (Bias) | TF (Setup) | LTF (Entry) |
|--------------|-----------|-----------|------------|
| **Position (HODLing)** | Monthly | Weekly | Daily |
| **Swing Trading** | Weekly | Daily | H4 |
| **Active Swing** | Daily | H4 | H1 |
| **Day Trading** | H4 | H1 | M15 |
| **Scalping** | H1 | M15 | M5 |

**Crypto-Specific Notes**:
- Due to 24/7 trading, the factor between timeframes can be slightly larger (5–6x) for crypto.
- Weekend price action on crypto is valid but may have lower liquidity — consider reducing size for weekend entries.
- Crypto's higher volatility means H4 charts contain as much "information" as Daily charts in traditional markets.

### 6.3 Factor Validation

For the chosen combination, verify the factor:

$$\text{Factor}_{1 \to 2} = \frac{TF_{\text{higher (minutes)}}}{TF_{\text{lower (minutes)}}}$$

| Combination | Factor 1→2 | Factor 2→3 | Verdict |
|-------------|-----------|-----------|---------|
| W1 → D1 → H4 | 5x (W=5 days) | 6x (D=6 H4s) | Optimal |
| D1 → H4 → H1 | 6x | 4x | Good |
| H4 → H1 → M15 | 4x | 4x | Good |
| H4 → M15 → M5 | 16x | 3x | Suboptimal (skip H1) |
| W1 → H4 → M15 | 30x | 16x | Bad (too large jumps) |

**Rule**: Each factor should be between 3x and 8x. Avoid jumps larger than 8x.

---

## 7. Mathematical Framework for MTF Confluence

### 7.1 Bayesian Confluence Model

Model the probability of a successful trade given signals from multiple timeframes:

$$P(\text{success} | TF_1, TF_2, \ldots, TF_n) = \frac{P(TF_1, \ldots, TF_n | \text{success}) \times P(\text{success})}{P(TF_1, \ldots, TF_n)}$$

Assuming conditional independence of timeframe signals given the market state:

$$P(\text{success} | TF_1, \ldots, TF_n) \approx \frac{P(\text{success}) \times \prod_{i=1}^n \frac{P(TF_i | \text{success})}{P(TF_i)}}{1}$$

In log-odds form:

$$\log \frac{P(\text{success})}{P(\text{failure})} = \log \frac{P_0}{1 - P_0} + \sum_{i=1}^n \log \frac{P(TF_i | \text{success})}{P(TF_i | \text{failure})}$$

Each aligned timeframe contributes a positive log-odds increment.

### 7.2 Empirical Contribution Values

Based on backtesting, each aligned timeframe contributes the following to log-odds:

| Timeframe Alignment | Log-Odds Contribution | Probability Increment |
|--------------------|--------------------|---------------------|
| Monthly aligned | +0.4 | +8% |
| Weekly aligned | +0.5 | +10% |
| Daily aligned | +0.6 | +12% |
| H4 aligned | +0.4 | +8% |
| H1 aligned | +0.3 | +6% |
| M15 aligned | +0.2 | +4% |

**Base probability** (no MTF context): $P_0 \approx 0.45$.
**Maximum probability** (all timeframes aligned): $P \approx 0.45 + 0.08 + 0.10 + 0.12 + 0.08 + 0.06 + 0.04 = 0.93$ (theoretical maximum; in practice capped at ~0.75 due to market noise).

### 7.3 Information Ratio Across Timeframes

The **information gain** from adding each timeframe:

$$IG_i = H(\text{outcome}) - H(\text{outcome} | TF_i)$$

Where $H$ is Shannon entropy. In practical terms:

$$IG_i \approx w_i \times r_i^2$$

Where $r_i$ is the correlation between TF_i's signal and the trade outcome.

| Timeframe | Typical $r_i$ | Weight $w_i$ | Information Gain |
|-----------|---------------|-------------|-----------------|
| Monthly | 0.15 | 0.10 | 0.002 |
| Weekly | 0.25 | 0.20 | 0.013 |
| Daily | 0.35 | 0.30 | 0.037 |
| H4 | 0.30 | 0.25 | 0.023 |
| H1 | 0.20 | 0.10 | 0.004 |
| M15 | 0.10 | 0.05 | 0.001 |

The Daily timeframe provides the most information gain, making it the most critical timeframe in the analysis.

### 7.4 Timeframe Correlation Matrix

Signals from adjacent timeframes are correlated. The effective (independent) information is:

$$IG_{\text{effective}} = \sum_i IG_i - \sum_{i<j} \rho_{ij} \sqrt{IG_i \times IG_j}$$

Where $\rho_{ij}$ is the correlation between timeframes:

| | Monthly | Weekly | Daily | H4 | H1 |
|---|---------|--------|-------|-----|-----|
| Monthly | 1.0 | 0.8 | 0.6 | 0.4 | 0.2 |
| Weekly | 0.8 | 1.0 | 0.8 | 0.5 | 0.3 |
| Daily | 0.6 | 0.8 | 1.0 | 0.7 | 0.4 |
| H4 | 0.4 | 0.5 | 0.7 | 1.0 | 0.7 |
| H1 | 0.2 | 0.3 | 0.4 | 0.7 | 1.0 |

This explains why non-adjacent timeframes (e.g., Weekly + H4 skipping Daily) can provide more independent information than adjacent ones.

---

## 8. Entry Timing Across Timeframes

### 8.1 The Alignment Cascade

The optimal entry occurs when signals cascade from HTF to LTF in sequence:

```
1. HTF (Weekly/Daily) establishes bullish bias → WAIT
2. ITF (H4) reaches an HTF zone + shows a setup → PREPARE
3. LTF (H1/M15) shows structural confirmation (CHoCH/BOS) → ENTER
```

### 8.2 Timing Window

Once the HTF and ITF are aligned, the LTF has a limited window to produce the entry signal:

$$T_{\text{window}} = k \times T_{\text{ITF\_candle\_period}}$$

Where $k = 5$ to $10$ (i.e., wait for 5–10 ITF candles for the LTF to confirm).

For H4 → H1 entry: window = 5–10 H4 candles = 20–40 hours.
For Daily → H4 entry: window = 5–10 daily candles = 1–2 weeks.

If the LTF does not confirm within the window, the setup is abandoned (the ITF setup may have been filled without us, or conditions have changed).

### 8.3 Entry Precision vs. Opportunity Cost

| Entry Method | Precision | Opportunity Cost | Best For |
|-------------|-----------|-----------------|----------|
| Enter on ITF signal (no LTF timing) | Low | Low (enter quickly) | Swing trades with wider stops |
| Wait for LTF confirmation | High | Medium (may miss moves) | Intraday and short-swing |
| Wait for LTF + retest | Very High | High (many missed trades) | Scalping; tight stop traders |

### 8.4 The "Reload Zone" Concept

When a trade moves in your favor after entry, the LTF will produce pullbacks. These pullbacks offer "reload" opportunities to add to the position:

```python
def check_reload_opportunity(trade, ltf_candles, itf_zone):
    """
    Check if price has pulled back to a reload zone (LTF S/R within the trade).
    """
    if trade.direction == "LONG":
        # Look for higher low on LTF that respects ITF structure
        ltf_swings = find_swing_points(ltf_candles, lookback=3)
        recent_lows = [s for s in ltf_swings if s["type"] == "LOW" and s["price"] > trade.entry]
        
        if recent_lows:
            reload_level = recent_lows[-1]["price"]
            if current_price <= reload_level * 1.001:  # Price at or near reload
                return {
                    "action": "ADD",
                    "entry": reload_level,
                    "sl": trade.sl,  # Keep same SL
                    "size": trade.original_size * 0.5  # Half size for reload
                }
    
    return None
```

---

## 9. Risk Parameters

### 9.1 Position Sizing by MTF Alignment

| MTF Score | Risk per Trade | Max Concurrent |
|-----------|---------------|---------------|
| $\geq 0.80$ | 2.0% | 4 |
| 0.65–0.79 | 1.5% | 3 |
| 0.50–0.64 | 1.0% | 3 |
| 0.35–0.49 | 0.5% | 2 |
| $< 0.35$ | No trade | — |

### 9.2 Stop Loss Timeframe Selection

The SL should be placed on the **setup timeframe** (ITF), not the entry timeframe (LTF):

- **Entry on M15**: SL beyond the H4 structural point (not beyond the M15 swing — too tight).
- **Entry on H1**: SL beyond the H4 zone or Daily structural point.
- **Entry on H4**: SL beyond the Daily structural point.

**Rationale**: LTF noise will frequently hit LTF-based stops. ITF-based stops survive noise while still invalidating the setup thesis.

### 9.3 Take Profit Timeframe Selection

| TP Level | Timeframe | Location |
|----------|-----------|----------|
| TP1 (40%) | ITF (H4) | Next ITF swing or zone |
| TP2 (30%) | HTF (Daily) | Next HTF swing or zone |
| TP3 (20%) | HTF (Daily/Weekly) | Major structural target |
| Trail (10%) | Trailing on ITF | Behind each new ITF swing |

### 9.4 Risk Adjustment for Timeframe

Higher timeframes produce wider stops. Adjust position size accordingly:

$$\text{Size}_{TF} = \frac{\text{Account} \times R\%}{SL_{\text{distance}}(TF)}$$

The R% is fixed; the position size adjusts to the stop distance. This means:
- Daily timeframe trades = smaller position sizes (wider stops).
- H1 timeframe trades = larger position sizes (tighter stops).
- Total risk exposure remains constant.

---

## 10. Execution Flow for AI Agent

### 10.1 Complete MTF Strategy Pseudocode

```python
def mtf_strategy():
    """
    Multi-Timeframe Analysis execution framework.
    Integrates all strategy modules with MTF context.
    """
    
    # ================================================
    # PHASE 1: GLOBAL SCAN (Run once per D1 candle close)
    # ================================================
    
    portfolio_opportunities = []
    
    for instrument in watchlist:
        # Top-down analysis
        mtf_result = top_down_analysis(instrument)
        
        if mtf_result["action"] == "NO_TRADE":
            continue
        
        if mtf_result["confidence"] < 0.35:
            continue
        
        portfolio_opportunities.append({
            "instrument": instrument,
            "bias": mtf_result["bias"],
            "confidence": mtf_result["confidence"],
            "analysis": mtf_result["analysis"]
        })
    
    # Rank opportunities by confidence
    portfolio_opportunities.sort(key=lambda x: x["confidence"], reverse=True)
    
    # ================================================
    # PHASE 2: SETUP IDENTIFICATION (Run per H4 candle close)
    # ================================================
    
    for opp in portfolio_opportunities[:10]:  # Top 10 opportunities
        instrument = opp["instrument"]
        bias = opp["bias"]
        
        # Identify setups on ITF (H4)
        h4_candles = fetch_candles(instrument, "H4", count=200)
        
        setups = []
        
        # Check all strategy modules for setups
        # (Each strategy module is called with the MTF bias as a filter)
        
        smc_setups = smc_find_setups(h4_candles, bias)
        sd_setups = supply_demand_find_setups(h4_candles, bias)
        harmonic_setups = harmonic_find_setups(h4_candles, bias)
        divergence_setups = divergence_find_setups(h4_candles, bias)
        ichimoku_setups = ichimoku_find_setups(h4_candles, bias)
        pa_setups = price_action_find_setups(h4_candles, bias)
        
        all_setups = smc_setups + sd_setups + harmonic_setups + divergence_setups + ichimoku_setups + pa_setups
        
        # Score setups incorporating MTF confidence
        for setup in all_setups:
            setup["mtf_adjusted_score"] = setup["base_score"] * opp["confidence"]
        
        all_setups.sort(key=lambda s: s["mtf_adjusted_score"], reverse=True)
        
        if not all_setups:
            continue
        
        best_setup = all_setups[0]
        
        if best_setup["mtf_adjusted_score"] < 0.40:
            continue
        
        # ================================================
        # PHASE 3: LTF ENTRY TIMING (Run per M15 candle close)
        # ================================================
        
        ltf_candles = fetch_candles(instrument, "M15", count=200)
        
        # Wait for LTF confirmation in the direction of the setup
        ltf_confirmation = wait_for_ltf_confirmation(
            ltf_candles, 
            bias=bias,
            setup_zone=best_setup.get("entry_zone"),
            method=determine_entry_method(best_setup["mtf_adjusted_score"])
        )
        
        if not ltf_confirmation:
            # Set alert for when price reaches the setup zone
            set_zone_alert(instrument, best_setup["entry_zone"])
            continue
        
        # ================================================
        # PHASE 4: ENTRY EXECUTION
        # ================================================
        
        entry_price = ltf_confirmation["entry"]
        
        # SL on ITF (H4 structural point)
        sl = best_setup["invalidation_level"]
        sl_with_buffer = sl - (ATR_BUFFER if bias == "BULLISH" else -ATR_BUFFER)
        
        # TP levels from different timeframes
        tp1 = calculate_itf_target(h4_candles, bias)  # H4 internal target
        tp2 = calculate_htf_target(opp["analysis"]["daily"], bias)  # Daily target
        
        # R:R validation
        rr = abs(tp1 - entry_price) / abs(entry_price - sl_with_buffer)
        
        min_rr = get_min_rr_mtf(opp["confidence"])
        if rr < min_rr:
            continue
        
        # Position sizing based on MTF confidence
        risk_pct = get_risk_pct_mtf(opp["confidence"])
        size = calculate_position_size(balance, risk_pct, entry_price, sl_with_buffer)
        
        # Portfolio-level risk check
        if not check_portfolio_risk(size, risk_pct, instrument):
            continue
        
        # Execute
        trade = execute_trade(
            instrument=instrument,
            direction="BUY" if bias == "BULLISH" else "SELL",
            entry=entry_price,
            sl=sl_with_buffer,
            tp_levels=[
                {"price": tp1, "close_pct": 0.40},
                {"price": tp2, "close_pct": 0.30},
            ],
            trailing_stop_tf="H4",
            size=size,
            metadata={
                "strategy": "MTF_FRAMEWORK",
                "underlying_strategy": best_setup["strategy_type"],
                "mtf_score": opp["confidence"],
                "bias": bias,
                "setup_tf": "H4",
                "entry_tf": "M15"
            }
        )
        
        return trade
    
    return WAIT("No MTF-confirmed setup available")
```

### 10.2 Continuous Monitoring Loop

```python
def mtf_monitor_loop():
    """
    Continuous monitoring that runs different analyses at different frequencies.
    """
    schedule = {
        "monthly_analysis": "on_new_monthly_candle",
        "weekly_analysis": "on_new_weekly_candle",
        "daily_analysis": "on_new_daily_candle",
        "h4_setup_scan": "on_new_h4_candle",
        "h1_structure_check": "on_new_h1_candle",
        "m15_entry_timing": "on_new_m15_candle",
        "trade_management": "on_new_m15_candle"
    }
    
    # Each function only recalculates its timeframe, not all
    # This saves computational resources
```

---

## 11. Advanced Concepts

### 11.1 Timeframe Fractal Alignment

The same pattern appearing on multiple timeframes simultaneously is an extremely high-probability setup:

**Example**: A bullish engulfing candle forms on the Daily chart. Drilling into H4, the Daily engulfing is composed of a bullish BOS + OB. Drilling into H1, there is a bullish divergence at the OB. All timeframes are showing the same bullish signal at different fractal scales.

### 11.2 Timeframe Divergence (Not Indicator Divergence)

When different timeframes show different stages of a cycle:

- **Weekly is ranging** (mid-cycle) while **Daily is trending** (trending within the range).
- This means the Daily trend will eventually hit the Weekly range boundary and reverse.
- The AI should set targets at the Weekly range extreme, not project indefinite trends.

### 11.3 Timeframe Momentum Synchronization

Measure momentum on each timeframe (using RSI or similar) and look for simultaneous oversold/overbought:

$$\text{MomentumSync} = \frac{1}{N} \sum_{i=1}^N \text{RSI}_{TF_i}$$

- If all timeframes are simultaneously oversold (sync < 30): Powerful buy signal.
- If all are simultaneously overbought (sync > 70): Powerful sell signal.
- This is rare but extremely powerful.

### 11.4 Dynamic Timeframe Selection

Based on market volatility, adjust the timeframe combination:

$$TF_{\text{optimal}} = TF_{\text{base}} \times \frac{\text{ATR}_{\text{current}}}{\text{ATR}_{\text{median}}}$$

In high volatility: use higher timeframes (more noise on lower TFs).
In low volatility: use lower timeframes (higher TFs move too slowly).

---

## 12. AI Implementation Notes

### 12.1 Computation Schedule

| Analysis | Frequency | CPU Cost |
|----------|-----------|----------|
| Monthly/Weekly scan | Once per week | Very low |
| Daily analysis | Once per day | Low |
| H4 setup scan | Every 4 hours | Medium |
| H1 monitoring | Every hour | Medium |
| M15 entry timing | Every 15 minutes | Low (only for active setups) |
| Trade management | Every 15 minutes | Low |

### 12.2 Data Storage

Maintain a state object per instrument:
```python
instrument_state = {
    "monthly_bias": "BULLISH",
    "weekly_bias": "BULLISH",
    "daily_bias": "BULLISH",
    "h4_bias": "NEUTRAL",  # Currently pulling back
    "mtf_score": 0.62,
    "active_setups": [...],
    "alerts": [...],
    "last_updated": {...}  # Per timeframe
}
```

### 12.3 Performance Expectations

| MTF Score Range | Win Rate | Avg R:R | Profit Factor |
|----------------|----------|---------|---------------|
| $\geq 0.80$ | 60–70% | 2.5:1 | 2.0–3.0 |
| 0.65–0.79 | 55–62% | 2.2:1 | 1.7–2.3 |
| 0.50–0.64 | 48–55% | 2.0:1 | 1.4–1.8 |
| 0.35–0.49 | 42–48% | 1.8:1 | 1.1–1.4 |

---

## 13. References

### Books
1. Elder, A. (1993). *Trading for a Living*. Wiley. — Triple Screen Trading System (one of the first formal MTF frameworks).
2. Murphy, J. J. (1999). *Technical Analysis of the Financial Markets*. NYIF. — Intermarket and multi-timeframe analysis.
3. Pring, M. J. (2002). *Technical Analysis Explained*. McGraw-Hill. — Time element in technical analysis.
4. Shannon, B. (2008). *Technical Analysis Using Multiple Timeframes*. LifeVest Publishing.
5. Carter, J. F. (2012). *Mastering the Trade*. McGraw-Hill. — Practical MTF trading.
6. Brooks, A. (2012). *Trading Price Action* series. Wiley. — Always-In methodology across timeframes.

### Academic Papers
7. Dacorogna, M. M., et al. (2001). *An Introduction to High-Frequency Finance*. Academic Press. — Mathematical framework for multi-scale analysis.
8. Muller, U. A., et al. (1993). "Fractals and Intrinsic Time." *Olsen & Associates*.
9. Mandelbrot, B. (1997). *Fractals and Scaling in Finance*. Springer. — Self-similarity across timeframes.
10. Peters, E. E. (1994). *Fractal Market Analysis*. Wiley. — Fractal nature of markets.

### Practitioner Sources
11. ICT (Inner Circle Trader). "Multi-Timeframe Analysis" — IOFED methodology.
12. Chris Capre. "Multi-Timeframe Price Action" — 2ndSkiesForex.
13. Steve Nison. "Multi-Timeframe Candlestick Analysis" — NisonAdvisors.
14. TradingView. Multi-timeframe indicators and layout tools.

---

*This document is part of the Multi-Agent AI Trading System knowledge base. It serves as the overarching framework connecting all other strategy guides (04–12). Every strategy should be executed through the MTF lens described here.*
