# Volume Profile & Market Profile — Complete Guide

## Document Metadata
| Field | Value |
|---|---|
| **Strategy ID** | VP-001 |
| **Category** | Auction Market Theory / Volume Analysis |
| **Asset Classes** | Forex, Crypto, Equities, Futures |
| **Timeframes** | Intraday to Monthly (primary: Session-based, Daily, Weekly) |
| **Complexity** | Advanced |
| **AI Suitability** | Very High — statistical distribution analysis |
| **Version** | 2.0 |
| **Last Updated** | 2026-04-12 |

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Auction Market Theory Foundations](#2-auction-market-theory-foundations)
3. [Volume Profile Concepts](#3-volume-profile-concepts)
4. [Market Profile (TPO Charts)](#4-market-profile-tpo-charts)
5. [Initial Balance](#5-initial-balance)
6. [Single Prints](#6-single-prints)
7. [Poor Highs and Lows](#7-poor-highs-and-lows)
8. [Volume Profile Trading Strategies](#8-volume-profile-trading-strategies)
9. [Mathematical Formulas](#9-mathematical-formulas)
10. [Execution Flow for AI Implementation](#10-execution-flow-for-ai-implementation)
11. [Risk Parameters](#11-risk-parameters)
12. [Advanced Techniques](#12-advanced-techniques)
13. [AI Implementation Notes](#13-ai-implementation-notes)
14. [References](#14-references)

---

## 1. Introduction

Volume Profile and Market Profile are analytical frameworks rooted in Auction Market Theory (AMT). They display volume (or time) distribution at each price level, revealing where the market has accepted value versus where it has rejected price, providing a unique view into institutional activity and market balance.

### 1.1 Core Thesis

- Markets are two-way auctions between buyers and sellers.
- Price probes in both directions until it finds levels where both parties agree to trade (fair value).
- High-volume price areas represent **accepted value** — fair price levels.
- Low-volume price areas represent **rejected prices** — imbalance zones.
- Price gravitates toward high-volume areas (value) and is repelled from low-volume areas.

### 1.2 Volume Profile vs. Traditional Volume

| Feature | Traditional Volume | Volume Profile |
|---------|-------------------|---------------|
| **Display** | Volume per time period (bar chart below price) | Volume per price level (horizontal histogram) |
| **Information** | How much was traded in a period | At which prices volume concentrated |
| **Use** | Confirming moves | Identifying fair value, S/R |
| **Granularity** | Time-based | Price-based |

---

## 2. Auction Market Theory Foundations

### 2.1 The Auction Process

Markets function as continuous double auctions:
1. Price moves up to find sellers (resistance to higher prices).
2. Price moves down to find buyers (resistance to lower prices).
3. The range within which both sides are satisfied = **Value Area**.

### 2.2 Market States

| State | Characteristics | VP Signature |
|-------|----------------|--------------|
| **Balance** | Price rotating within a range; bell-shaped VP | Tight value area, symmetric profile |
| **Imbalance** | Trending; price moving directionally | Skewed profile, elongated shape |
| **Transition** | Shifting from balance to imbalance or vice versa | Multiple POCs, p-shaped or b-shaped profile |

### 2.3 Profile Shapes

| Shape | Description | Implication |
|-------|-------------|-------------|
| **D-Shape (Normal)** | Bell curve — most volume at center | Balanced market; mean reversion likely |
| **P-Shape** | Volume concentrated at the top | Auction found sellers at top; bearish implication |
| **b-Shape** | Volume concentrated at the bottom | Auction found buyers at bottom; bullish implication |
| **B-Shape (Double Distribution)** | Two distinct volume peaks | Market transitioning; watch which POC holds |
| **Thin/Elongated** | Volume spread across wide range | Trending/imbalanced; trend likely to continue |

---

## 3. Volume Profile Concepts

### 3.1 Point of Control (POC)

The **Point of Control** is the price level with the highest traded volume in a given profile period. It represents the "fairest" price according to market consensus.

$$\text{POC} = \arg\max_{p} V(p)$$

Where $V(p)$ is the volume traded at price level $p$.

**Properties**:
- POC acts as a magnet — price tends to gravitate toward it.
- Unvisited (naked) POCs from previous sessions are strong S/R levels.
- Migration of POC from one session to the next indicates value shift.

### 3.2 Value Area (VA)

The **Value Area** encompasses 70% of total volume for the profile period (1 standard deviation of a normal distribution).

$$\text{Value Area} = \{p : \text{cumulative volume from POC outward} \leq 0.70 \times V_{\text{total}}\}$$

**Boundaries**:
- **VAH (Value Area High)**: Upper boundary of the value area.
- **VAL (Value Area Low)**: Lower boundary of the value area.

**Calculation Algorithm**:
```python
def calculate_value_area(volume_profile, target_pct=0.70):
    """
    Calculate Value Area from a volume profile.
    
    volume_profile: dict of {price_level: volume} sorted by price
    """
    total_volume = sum(volume_profile.values())
    target_volume = total_volume * target_pct
    
    # Find POC
    poc_price = max(volume_profile, key=volume_profile.get)
    poc_idx = sorted(volume_profile.keys()).index(poc_price)
    
    prices = sorted(volume_profile.keys())
    accumulated = volume_profile[poc_price]
    
    upper_idx = poc_idx
    lower_idx = poc_idx
    
    while accumulated < target_volume:
        # Look one level above and one below
        vol_above = volume_profile.get(prices[upper_idx + 1], 0) if upper_idx + 1 < len(prices) else 0
        vol_below = volume_profile.get(prices[lower_idx - 1], 0) if lower_idx - 1 >= 0 else 0
        
        # Add the larger volume side (two-price method)
        if upper_idx + 1 < len(prices) and lower_idx - 1 >= 0:
            # Compare pairs
            above_pair = vol_above + (volume_profile.get(prices[upper_idx + 2], 0) if upper_idx + 2 < len(prices) else 0)
            below_pair = vol_below + (volume_profile.get(prices[lower_idx - 2], 0) if lower_idx - 2 >= 0 else 0)
            
            if above_pair >= below_pair:
                upper_idx += 1
                accumulated += vol_above
            else:
                lower_idx -= 1
                accumulated += vol_below
        elif upper_idx + 1 < len(prices):
            upper_idx += 1
            accumulated += vol_above
        elif lower_idx - 1 >= 0:
            lower_idx -= 1
            accumulated += vol_below
        else:
            break
    
    return {
        "POC": poc_price,
        "VAH": prices[upper_idx],
        "VAL": prices[lower_idx],
        "VA_volume_pct": accumulated / total_volume
    }
```

### 3.3 High Volume Nodes (HVN)

**HVN** = price levels with notably high volume, forming peaks on the profile histogram.

**Properties**:
- Act as magnets — price tends to consolidate around HVNs.
- Represent areas of high liquidity and acceptance.
- Difficult for price to pass through quickly.

**Detection**:
$$\text{HVN}_i = V(p_i) > \mu_V + k \times \sigma_V$$

Where $\mu_V$ and $\sigma_V$ are the mean and standard deviation of volume across all price levels, and $k = 0.5$ to $1.0$.

### 3.4 Low Volume Nodes (LVN)

**LVN** = price levels with notably low volume, forming troughs on the profile histogram.

**Properties**:
- Act as barriers — price tends to move through LVNs quickly.
- Represent areas of rejection and imbalance.
- Function as support/resistance levels (price accelerates when entering LVN).
- Similar concept to Fair Value Gaps in SMC.

**Detection**:
$$\text{LVN}_i = V(p_i) < \mu_V - k \times \sigma_V$$

---

## 4. Market Profile (TPO Charts)

### 4.1 TPO (Time-Price Opportunity)

Market Profile (created by J. Peter Steidlmayer at CBOT) uses **time** instead of volume. Each 30-minute period is represented by a letter (A, B, C, ...) placed at each price level traded during that period.

### 4.2 TPO Count

The number of TPOs at each price = the number of 30-minute periods during which that price was visited.

$$\text{TPO Count}(p) = |\{t : L_t \leq p \leq H_t\}|$$

### 4.3 TPO POC

Same concept as Volume POC but based on time rather than volume:
$$\text{TPO\_POC} = \arg\max_p \text{TPO Count}(p)$$

### 4.4 Profile Types by Day Type

| Day Type | Characteristics | Implication |
|----------|----------------|-------------|
| **Normal Day** | 70% rule; IB range intact | Balance; fade extremes |
| **Normal Variation** | IB range extended once | Slight directional bias |
| **Trend Day** | IB range extended multiple times; elongated profile | Strong trend; hold with-trend positions |
| **Double Distribution** | Two separate value areas; B-shaped | Transition; watch for follow-through |
| **Neutral Day** | Balanced around IB; no extension | Extreme balance; breakout pending |

### 4.5 Developing POC vs. Fixed POC

- **Developing POC**: The POC as it evolves during the current session. It migrates as new volume/time data comes in.
- **Fixed POC**: The final POC of a completed session.

**Trading Rule**: If the developing POC migrates strongly in one direction, it indicates an imbalanced market — trade in the direction of migration.

---

## 5. Initial Balance (IB)

### 5.1 Definition

The **Initial Balance** is the price range established during the first hour of trading (first two 30-minute periods, A and B in TPO notation).

$$\text{IB\_High} = \max(H_A, H_B)$$
$$\text{IB\_Low} = \min(L_A, L_B)$$
$$\text{IB\_Range} = \text{IB\_High} - \text{IB\_Low}$$

### 5.2 IB Significance

The IB represents the first interaction between overnight/premarket positioning and the regular session. Its width predicts the day type:

| IB Width vs. Average | Likely Day Type | Trading Approach |
|---------------------|-----------------|------------------|
| Wide (> 1.5x avg) | Normal / Neutral | Fade extremes; mean reversion |
| Average (0.75x–1.5x avg) | Normal Variation | Moderate directional bias |
| Narrow (< 0.75x avg) | Trend Day | Trade breakouts aggressively |

### 5.3 IB Extension Rules

- **Single IB Extension**: Price breaks above IB High or below IB Low by up to 1x IB Range. Moderate directional bias.
- **Double IB Extension**: Price extends 2x IB Range beyond. Strong trend day.
- **Failed IB Extension**: Price breaks out then returns within the IB. Trapped traders = fade the breakout.

### 5.4 IB Trading Strategy

```python
def ib_strategy(session_candles, ib_range_history):
    """
    Initial Balance trading strategy.
    """
    # Calculate today's IB (first hour)
    first_hour = session_candles[:4]  # 4 x 15min = 1 hour (adjust for timeframe)
    ib_high = max(c.high for c in first_hour)
    ib_low = min(c.low for c in first_hour)
    ib_range = ib_high - ib_low
    
    # Compare to average IB range
    avg_ib = np.mean(ib_range_history[-20:])
    
    # Narrow IB → expect trend day → trade breakout
    if ib_range < 0.75 * avg_ib:
        # Set breakout orders
        return {
            "strategy": "BREAKOUT",
            "buy_stop": ib_high + 0.1 * ib_range,
            "sell_stop": ib_low - 0.1 * ib_range,
            "sl_distance": 0.5 * ib_range,
            "tp": 2.0 * ib_range  # Target 2x IB extension
        }
    
    # Wide IB → expect normal day → fade extremes
    elif ib_range > 1.5 * avg_ib:
        return {
            "strategy": "MEAN_REVERSION",
            "buy_limit": ib_low + 0.1 * ib_range,  # Buy near IB low
            "sell_limit": ib_high - 0.1 * ib_range,  # Sell near IB high
            "sl_distance": 0.3 * ib_range,
            "tp": ib_range * 0.5  # Target POC area
        }
    
    else:
        return {"strategy": "WAIT", "note": "Average IB — watch for directional clues"}
```

---

## 6. Single Prints

### 6.1 Definition

**Single prints** (also called single TPOs) are price levels visited during only one 30-minute period, typically formed during fast moves away from value. In volume profile terms, they correspond to very low volume areas within a trend move.

### 6.2 Significance

- Single prints represent **initiative activity** — aggressive institutional buying or selling.
- They create a "gap" in the profile that price often returns to fill (similar to FVG in SMC).
- They act as S/R: support on the way down, resistance on the way up.

### 6.3 Detection

$$\text{SinglePrint}(p) = \text{TPO Count}(p) = 1 \quad \text{OR} \quad V(p) < 0.2 \times V_{\text{POC}}$$

### 6.4 Trading Rules

- **Unfilled single prints above price**: Resistance; potential sell zone on approach.
- **Unfilled single prints below price**: Support; potential buy zone on approach.
- **Filled single prints**: Once price revisits and spends time there, the single print is "repaired" and loses significance.

---

## 7. Poor Highs and Lows

### 7.1 Definition

A **poor high** is a session high where the market appears to have stopped rising not due to genuine selling pressure but due to a lack of buying initiative. It is characterized by multiple TPOs (or volume) at the exact high — indicating the market "stalled" rather than being rejected.

A **poor low** is the same concept at the session low.

### 7.2 Identification

**Poor High**:
- Multiple TPOs at the session high price level (typically 3+ TPOs).
- The high does not show a single-print exhaustion tail.
- Volume at the high is moderate to high (buyers ran out of energy, not repelled by sellers).

**Good/Strong High**:
- Single print or very few TPOs at the extreme.
- Shows aggressive rejection (long wick, single TPO).
- Represents genuine selling pressure that halted the advance.

### 7.3 Trading Implication

| High/Low Type | Implication | Action |
|--------------|-------------|--------|
| **Poor High** | Likely to be revisited/broken | Do NOT short at this level; expect eventual break higher |
| **Strong High** | Genuine resistance | Short on retest; or expect holding |
| **Poor Low** | Likely to be revisited/broken | Do NOT buy at this level; expect eventual break lower |
| **Strong Low** | Genuine support | Buy on retest; or expect holding |

### 7.4 Poor High/Low Algorithm

```python
def classify_extreme(profile, session_high, session_low, tpo_data):
    """
    Classify session highs/lows as poor or strong.
    """
    # TPO count at the session high
    tpos_at_high = tpo_data.get(session_high, 0)
    
    # Check for excess (single prints above the profile body)
    excess_above = count_single_prints_at_extreme(tpo_data, "HIGH")
    
    if tpos_at_high >= 3 and excess_above == 0:
        high_type = "POOR"  # Market stalled, not rejected
    elif tpos_at_high <= 1 or excess_above >= 2:
        high_type = "STRONG"  # Genuine rejection
    else:
        high_type = "NEUTRAL"
    
    # Same for low
    tpos_at_low = tpo_data.get(session_low, 0)
    excess_below = count_single_prints_at_extreme(tpo_data, "LOW")
    
    if tpos_at_low >= 3 and excess_below == 0:
        low_type = "POOR"
    elif tpos_at_low <= 1 or excess_below >= 2:
        low_type = "STRONG"
    else:
        low_type = "NEUTRAL"
    
    return {"high_type": high_type, "low_type": low_type}
```

---

## 8. Volume Profile Trading Strategies

### 8.1 Strategy 1: Value Area Rule (80% Rule)

**Concept**: If the market opens outside the previous day's Value Area and then trades back into it, there is an 80% probability it will reach the opposite side of the Value Area.

**Long Setup**:
1. Market opens below previous day's VAL.
2. Price trades back above VAL (acceptance).
3. Go long with target at previous day's VAH.
4. SL below the retest of VAL.

**Short Setup**:
1. Market opens above previous day's VAH.
2. Price trades back below VAH (acceptance).
3. Go short with target at previous day's VAL.
4. SL above the retest of VAH.

```python
def value_area_rule(prev_va, current_open, current_price):
    """
    The 80% rule: if price opens outside VA and returns inside,
    expect move to the opposite VA boundary.
    """
    prev_vah = prev_va["VAH"]
    prev_val = prev_va["VAL"]
    prev_poc = prev_va["POC"]
    
    # Open below VAL, now trading above VAL
    if current_open < prev_val and current_price > prev_val:
        return {
            "signal": "LONG",
            "entry": prev_val,  # or current price
            "target": prev_vah,
            "sl": prev_val - 0.5 * (prev_vah - prev_val),
            "probability": 0.80,
            "note": "80% rule: price accepted back into VA from below"
        }
    
    # Open above VAH, now trading below VAH
    if current_open > prev_vah and current_price < prev_vah:
        return {
            "signal": "SHORT",
            "entry": prev_vah,
            "target": prev_val,
            "sl": prev_vah + 0.5 * (prev_vah - prev_val),
            "probability": 0.80,
            "note": "80% rule: price accepted back into VA from above"
        }
    
    return None
```

### 8.2 Strategy 2: Naked POC Trading

**Concept**: A "naked POC" is a previous session's POC that has not been revisited by price in subsequent sessions. These act as powerful magnets.

**Rules**:
1. Identify naked POCs from the last 5–20 sessions.
2. When price approaches a naked POC, expect a reaction (price stalls, consolidates, or reverses).
3. Trade the reaction: if price is trending toward a naked POC, use it as a target; if price is at a naked POC, trade the rejection.

### 8.3 Strategy 3: LVN Breakout/Rejection

**Concept**: LVNs are price levels where the market moved quickly — they act as barriers. Price either bounces off them or accelerates through them.

**Breakout Setup**:
- Price approaches an LVN from within the value area.
- If price breaks through the LVN with momentum, it accelerates to the next HVN.
- Entry: Breakout through LVN.
- Target: Next HVN.

**Rejection Setup**:
- Price probes into an LVN but fails to sustain.
- Entry: Fade back toward the nearest HVN/POC.
- SL: Beyond the LVN.

### 8.4 Strategy 4: Developing Value Area Shift

**Concept**: Monitor the developing session's value area. If it shifts entirely above or below the prior session's value area, a directional move is underway.

$$\text{VA Shift} = \begin{cases} \text{Bullish} & \text{if } \text{Dev\_VAL} > \text{Prev\_VAH} \\ \text{Bearish} & \text{if } \text{Dev\_VAH} < \text{Prev\_VAL} \\ \text{Overlap} & \text{otherwise (no clear shift)} \end{cases}$$

### 8.5 Strategy 5: Composite Profile Analysis

Build a volume profile over multiple sessions (3–5 day composite, weekly composite, monthly composite) to identify larger-scale value areas and POCs for swing trading.

---

## 9. Mathematical Formulas

### 9.1 Volume Profile Construction

Given tick data or candle data, construct a volume profile by aggregating volume at each price level:

$$V(p) = \sum_{i=1}^{N} v_i \cdot \mathbb{1}[L_i \leq p \leq H_i] \cdot w_i(p)$$

Where:
- $v_i$ = volume of candle $i$
- $\mathbb{1}[\cdot]$ = indicator function
- $w_i(p)$ = volume distribution weight within candle $i$

**Volume Distribution Models**:

1. **Uniform**: $w_i(p) = \frac{1}{H_i - L_i}$ (distributes volume equally across all prices in the candle range).

2. **Triangle (Close-weighted)**: More volume attributed to price levels near the close:
$$w_i(p) = \frac{2(1 - |p - C_i| / (H_i - L_i))}{H_i - L_i}$$

3. **Split (Buy/Sell)**: Attribute volume above the midpoint as selling, below as buying.

### 9.2 Value Area Probability Distribution

Assuming volume follows a Gaussian distribution around the POC:

$$V(p) \approx V_{\text{max}} \cdot e^{-\frac{(p - \text{POC})^2}{2\sigma^2}}$$

Where $\sigma$ determines the width of the value area:
$$\text{VA Width} \approx 2\sigma \quad \text{(contains 68% of volume)}$$
$$\text{70\% VA} \approx 2.07\sigma$$

### 9.3 POC Migration Rate

The rate at which the developing POC moves indicates market conviction:

$$\text{POC\_Migration} = \frac{\Delta \text{POC}}{\Delta t} = \frac{\text{POC}(t) - \text{POC}(t - \Delta t)}{\Delta t}$$

If $|\text{POC\_Migration}| > 0$ consistently, the market is trending.

### 9.4 Volume-Weighted Average Price (VWAP) Relationship

VWAP is the volume-weighted mean of all traded prices and closely relates to the POC:

$$\text{VWAP} = \frac{\sum_{i=1}^{N} P_i \times V_i}{\sum_{i=1}^{N} V_i}$$

Standard deviation bands around VWAP:
$$\text{VWAP}_{\pm n\sigma} = \text{VWAP} \pm n \times \sqrt{\frac{\sum V_i(P_i - \text{VWAP})^2}{\sum V_i}}$$

### 9.5 Relative Volume Analysis

$$\text{RVOL}(p) = \frac{V(p)}{V_{\text{avg}}(p, \text{lookback})}$$

Where $V_{\text{avg}}(p, \text{lookback})$ is the average volume at price $p$ over the lookback period.

- $\text{RVOL} > 2$: Significantly above average — strong participation.
- $\text{RVOL} < 0.5$: Well below average — lack of interest.

### 9.6 Volume Delta at Each Price

$$\Delta V(p) = V_{\text{buy}}(p) - V_{\text{sell}}(p)$$

Positive delta = net buying. Negative delta = net selling. This helps determine whether an HVN formed due to buying or selling pressure.

---

## 10. Execution Flow for AI Implementation

### 10.1 Complete Strategy Pseudocode

```python
def volume_profile_strategy():
    """
    Complete Volume Profile trading strategy.
    Combines multiple VP concepts for trade decisions.
    """
    
    # ================================================
    # PHASE 1: BUILD PROFILES
    # ================================================
    
    for instrument in watchlist:
        # Build session profiles
        prev_session = build_volume_profile(
            fetch_candles(instrument, "M5", session="previous"),
            price_increment=get_tick_size(instrument)
        )
        
        current_session = build_volume_profile(
            fetch_candles(instrument, "M5", session="current"),
            price_increment=get_tick_size(instrument)
        )
        
        # Build composite profiles
        weekly_composite = build_volume_profile(
            fetch_candles(instrument, "M15", days=5),
            price_increment=get_tick_size(instrument)
        )
        
        # Calculate value areas
        prev_va = calculate_value_area(prev_session)
        current_va = calculate_value_area(current_session)
        weekly_va = calculate_value_area(weekly_composite)
        
        # Identify HVNs and LVNs
        hvns = find_hvns(weekly_composite, threshold_sigma=0.5)
        lvns = find_lvns(weekly_composite, threshold_sigma=-0.5)
        
        # Find naked POCs
        naked_pocs = find_naked_pocs(instrument, lookback_sessions=20)
        
        # Classify previous session extremes
        extremes = classify_extreme(prev_session, prev_session_high, prev_session_low, tpo_data)
        
        # ================================================
        # PHASE 2: DETERMINE MARKET STATE
        # ================================================
        
        current_price = get_price(instrument)
        session_open = get_session_open(instrument)
        
        # Relative position
        position = determine_position(current_price, prev_va, weekly_va)
        # Returns: "ABOVE_VA", "INSIDE_VA", "BELOW_VA", "AT_VAH", "AT_VAL", "AT_POC"
        
        # Day type assessment
        ib = calculate_initial_balance(instrument)
        avg_ib = get_avg_ib_range(instrument, lookback=20)
        day_type_forecast = forecast_day_type(ib, avg_ib)
        
        # Profile shape of developing session
        profile_shape = classify_profile_shape(current_session)
        
        # ================================================
        # PHASE 3: GENERATE SIGNALS
        # ================================================
        
        signals = []
        
        # Strategy 1: 80% Rule
        va_rule_signal = value_area_rule(prev_va, session_open, current_price)
        if va_rule_signal:
            signals.append(va_rule_signal)
        
        # Strategy 2: Naked POC approach
        for npoc in naked_pocs:
            if abs(current_price - npoc["price"]) < 0.5 * atr:
                signals.append({
                    "signal": "NAKED_POC_APPROACH",
                    "direction": "target" if trending_toward(current_price, npoc) else "rejection",
                    "level": npoc["price"],
                    "age_sessions": npoc["age"]
                })
        
        # Strategy 3: LVN breakout/rejection
        for lvn in lvns:
            if abs(current_price - lvn["price"]) < 0.3 * atr:
                signals.append({
                    "signal": "LVN_INTERACTION",
                    "level": lvn["price"],
                    "nearest_hvn": find_nearest_hvn(lvn, hvns)
                })
        
        # Strategy 4: IB breakout (for narrow IB)
        if day_type_forecast == "TREND_DAY":
            if current_price > ib["high"] + 0.1 * ib["range"]:
                signals.append({
                    "signal": "IB_BREAKOUT_LONG",
                    "entry": ib["high"],
                    "target": ib["high"] + 2 * ib["range"]
                })
            elif current_price < ib["low"] - 0.1 * ib["range"]:
                signals.append({
                    "signal": "IB_BREAKOUT_SHORT",
                    "entry": ib["low"],
                    "target": ib["low"] - 2 * ib["range"]
                })
        
        # Strategy 5: Poor high/low retest
        if extremes["high_type"] == "POOR" and current_price > prev_session_high * 0.999:
            signals.append({
                "signal": "POOR_HIGH_BREAK",
                "direction": "LONG",
                "note": "Poor high likely to be exceeded"
            })
        
        if extremes["low_type"] == "POOR" and current_price < prev_session_low * 1.001:
            signals.append({
                "signal": "POOR_LOW_BREAK",
                "direction": "SHORT",
                "note": "Poor low likely to be broken"
            })
        
        # ================================================
        # PHASE 4: SCORE AND EXECUTE BEST SIGNAL
        # ================================================
        
        if not signals:
            continue
        
        # Score each signal
        for signal in signals:
            signal["score"] = score_vp_signal(
                signal, 
                position=position,
                day_type=day_type_forecast,
                weekly_context=weekly_va,
                profile_shape=profile_shape
            )
        
        # Select best
        signals.sort(key=lambda s: s.get("score", 0), reverse=True)
        best = signals[0]
        
        if best["score"] < 0.55:
            continue
        
        # Calculate trade parameters
        entry, sl, tp = calculate_vp_trade_params(best, prev_va, current_va, hvns, lvns, atr)
        
        # Risk validation
        rr = abs(tp - entry) / abs(entry - sl)
        if rr < 2.0:
            continue
        
        # Execute
        size = calculate_position_size(balance, risk_pct=1.0, entry=entry, sl=sl)
        
        trade = execute_trade(
            instrument=instrument,
            direction=best.get("direction", infer_direction(best)),
            entry=entry,
            sl=sl,
            tp=tp,
            size=size,
            metadata={"strategy": "VOLUME_PROFILE", "signal": best}
        )
        
        return trade
    
    return WAIT("No VP signal")
```

---

## 11. Risk Parameters

### 11.1 Stop Loss Placement

| Strategy | SL Location | Logic |
|----------|-------------|-------|
| 80% Rule (long from VAL) | Below VAL by 0.3 VA width | Beyond the acceptance point |
| IB Breakout | Back inside IB by 0.5 IB range | Failed breakout invalidation |
| LVN Rejection | Beyond the LVN by 0.5 ATR | If LVN doesn't hold, thesis is wrong |
| Naked POC | Beyond the POC by 0.5 ATR | |
| Poor High/Low | Beyond the extreme by 1 ATR | |

### 11.2 Take Profit Levels

| Strategy | TP1 | TP2 | TP3 |
|----------|-----|-----|-----|
| 80% Rule | POC | Opposite VA boundary | Next session's POC |
| IB Breakout | 1x IB extension | 2x IB extension | Next HVN |
| LVN → HVN | Nearest HVN | POC | — |
| Naked POC | Closest VA boundary | — | — |

### 11.3 Position Sizing by Confidence

| VP Signal Score | Risk % |
|----------------|--------|
| $\geq 0.80$ | 1.5% |
| 0.65–0.79 | 1.0% |
| 0.55–0.64 | 0.5% |
| $< 0.55$ | No trade |

### 11.4 Session-Based Risk Limits

- Maximum 3 VP trades per session.
- Maximum 2% total risk per session from VP strategy.
- If first two VP trades lose, no more VP trades for the session.
- VP strategies perform best in specific session windows: apply kill-zone timing.

---

## 12. Advanced Techniques

### 12.1 Volume Profile Delta (Buy vs. Sell Volume)

Separate the volume at each price level into aggressive buys and aggressive sells:

$$\text{Delta}(p) = V_{\text{buy}}(p) - V_{\text{sell}}(p)$$

**Interpretation**:
- Positive delta at HVN → buyers are in control at fair value.
- Negative delta at HVN → sellers are in control; potential breakdown.
- Divergence between price making new highs and delta declining → distribution.

### 12.2 Volume Footprint Charts

Footprint charts show bid/ask volume at each price within each candle. Key patterns:
- **Stacked Imbalances**: Multiple consecutive price levels where buy volume > 2x sell volume (or vice versa). Indicates aggressive institutional activity.
- **Unfinished Auction**: The last price level in a candle shows zero volume on one side — suggests the auction will continue in that direction.

### 12.3 Multi-Session Composite Analysis

Build composites over different periods to identify multi-timeframe value:

| Composite Period | Use |
|-----------------|-----|
| 3-day | Short-term fair value for day traders |
| Weekly | Intermediate value for swing traders |
| Monthly | Macro value for position traders |
| Quarterly | Long-term institutional positioning |

### 12.4 VP + SMC Integration

Volume Profile enhances SMC analysis:
- **Order Blocks with high volume**: OBs that coincide with HVNs are stronger (institutional acceptance).
- **FVGs as LVNs**: Fair Value Gaps in SMC correspond to LVNs in VP — the market moved too fast to build volume.
- **Liquidity pools near HVNs**: Liquidity sweeps that target HVN-adjacent levels are higher probability.

---

## 13. AI Implementation Notes

### 13.1 Data Requirements

| Data Type | Minimum | Notes |
|-----------|---------|-------|
| Tick data | Ideal for precise VP | Not always available for forex spot |
| M1 candles with volume | Acceptable alternative | Use volume-weighted price distribution |
| M5 candles with volume | Minimum viable | Less precise but functional |
| Session times | Required | Need session boundaries for IB, day type |

### 13.2 For Crypto Markets

Crypto VP has unique considerations:
- **No fixed sessions**: Use the 24-hour UTC day, or define custom sessions (e.g., US 13:00–21:00 UTC).
- **24/7 trading**: IB may be less meaningful; use the first hour after the daily close (00:00 UTC).
- **Exchange-specific volume**: Use aggregate volume across major exchanges for accuracy.
- **Funding rate times** (futures): 08:00, 16:00, 00:00 UTC create micro-sessions.

### 13.3 Performance Expectations

| Metric | Expected Range |
|--------|---------------|
| Win Rate (80% rule) | 55–65% |
| Win Rate (IB breakout, narrow IB only) | 50–60% |
| Win Rate (naked POC trades) | 55–62% |
| Average R:R | 1.5:1 to 2.5:1 |
| Trades/Day/Instrument | 1–3 |
| Profit Factor | 1.5–2.2 |

---

## 14. References

### Books
1. Steidlmayer, J. P., & Hawkins, S. B. (2003). *Steidlmayer on Markets: Trading with Market Profile*. Wiley.
2. Dalton, J. F. (1993). *Mind Over Markets: Power Trading with Market Generated Information*. McGraw-Hill.
3. Dalton, J. F. (2007). *Markets in Profile: Profiting from the Auction Process*. Wiley.
4. Jones, D. L. (2010). *Volume Profile: The Insider's Guide to Trading*. Independently published.
5. Gopalakrishnan, J. (2009). "An Introduction to Market Profile" — *Technical Analysis of Stocks & Commodities*.

### Academic Papers
6. Hagstrom, P. (2019). "Volume Profile Analysis for Algorithmic Trading Systems." *Journal of Trading*, 14(3), 45–58.
7. Cont, R., Kukanov, A., & Stoikov, S. (2014). "The Price Impact of Order Book Events." *Journal of Financial Econometrics*, 12(1), 47–88.
8. Bouchaud, J.-P. (2010). "Price Impact." *Encyclopedia of Quantitative Finance*, Wiley.
9. Kyle, A. S. (1985). "Continuous Auctions and Insider Trading." *Econometrica*, 53(6), 1315–1335.

### Practitioner Sources
10. CBOT (Chicago Board of Trade). "Market Profile Handbook" — Original documentation.
11. Auction Vista. "Volume Profile Trading Masterclass" (2022).
12. Trader Dale. "Volume Profile Trading Strategies" (2021).
13. Futures.io community. "Market Profile / Volume Profile Research Threads."
14. TradingView. Volume Profile tools and community scripts.

---

*This document is part of the Multi-Agent AI Trading System knowledge base. It should be read in conjunction with the Order Flow & Liquidity guide (03_order_flow_liquidity), Smart Money Concepts guide (04_smart_money_concepts), and the Multi-Timeframe Analysis guide (11_multi_timeframe_analysis).*
