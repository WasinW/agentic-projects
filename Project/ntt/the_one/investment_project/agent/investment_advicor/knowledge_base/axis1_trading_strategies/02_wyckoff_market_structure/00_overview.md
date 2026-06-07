# Wyckoff Method & Market Structure — Overview

> **Module**: Axis 1 — Trading Strategies
> **Topic**: 02 — Wyckoff Method & Market Structure
> **File**: 00_overview.md
> **Version**: 1.0
> **Last Updated**: 2026-04-12
> **Author**: NTT Multi-Agent AI Trading System — Knowledge Base Team

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Historical Context](#2-historical-context)
3. [The Three Fundamental Laws of Wyckoff](#3-the-three-fundamental-laws-of-wyckoff)
4. [The Composite Man Concept](#4-the-composite-man-concept)
5. [Four Market Phases](#5-four-market-phases)
6. [Wyckoff Market Cycle — Complete Diagram](#6-wyckoff-market-cycle--complete-diagram)
7. [Relevance to Modern Forex Markets](#7-relevance-to-modern-forex-markets)
8. [Relevance to Modern Crypto Markets](#8-relevance-to-modern-crypto-markets)
9. [Wyckoff vs Other Methodologies](#9-wyckoff-vs-other-methodologies)
10. [Core Logic — Entry/Exit Framework](#10-core-logic--entryexit-framework)
11. [Technical Specifications](#11-technical-specifications)
12. [Mathematical Models](#12-mathematical-models)
13. [Risk Parameters](#13-risk-parameters)
14. [Execution Flow](#14-execution-flow)
15. [Integration with Multi-Agent System](#15-integration-with-multi-agent-system)
16. [References](#16-references)

---

## 1. Introduction

The Wyckoff Method is a technical analysis approach developed by Richard Demille Wyckoff (1873–1934), one of the most influential figures in the history of technical analysis. Unlike indicator-based systems that react to past price data, the Wyckoff Method reads the underlying supply and demand dynamics driving price movement, identifying the footprint of large institutional operators — the "smart money."

This knowledge base module provides the AI trading system with a complete framework for:

- **Identifying** the current market phase (accumulation, markup, distribution, markdown)
- **Detecting** the transition signals between phases
- **Generating** high-probability trade entries aligned with institutional activity
- **Managing** risk through phase-aware position sizing and stop placement
- **Integrating** Wyckoff analysis with modern market structure concepts (BoS, ChoCh)

### 1.1 Why Wyckoff for Algorithmic Trading

The Wyckoff Method is particularly suited for algorithmic implementation because:

1. **Rule-based**: Each phase has specific, identifiable price-volume characteristics
2. **State-machine compatible**: The market cycle maps directly to a finite state machine
3. **Volume-driven**: Volume data provides quantifiable confirmation signals
4. **Fractal**: The same patterns repeat across all timeframes, enabling multi-timeframe analysis
5. **Universal**: Applicable to any liquid market — Forex, Crypto, Equities, Commodities

### 1.2 Scope of This Module

| Sub-Document | Content |
|---|---|
| `01_accumulation_schematic.md` | Accumulation phase — all sub-phases, entry logic, volume analysis |
| `02_distribution_schematic.md` | Distribution phase — all sub-phases, mirror analysis, risk management |
| `03_market_structure_bos_choch.md` | Break of Structure, Change of Character, multi-timeframe analysis |
| `04_wyckoff_volume_analysis.md` | Volume Spread Analysis (VSA), effort/result, climactic volume |
| `05_execution_flow.md` | Complete algorithm, state machine, pseudocode, position sizing |

---

## 2. Historical Context

### 2.1 Richard D. Wyckoff (1873–1934)

Richard Wyckoff began his Wall Street career at age 15 as a stock runner for a New York brokerage. By age 25, he owned his own brokerage firm. He founded *The Magazine of Wall Street* (1907), which at its peak had over 200,000 subscribers.

Wyckoff was a contemporary of Jesse Livermore, J.P. Morgan, and Charles Dow. Unlike these figures, Wyckoff dedicated his later career to educating the public about how markets actually worked — specifically, how large operators manipulated prices to their advantage.

### 2.2 Key Publications

| Year | Publication | Significance |
|---|---|---|
| 1910 | *Studies in Tape Reading* | Foundation of price-volume analysis |
| 1924 | *How I Trade and Invest in Stocks and Bonds* | Practical trading methodology |
| 1931 | *The Richard D. Wyckoff Method of Trading and Investing in Stocks* | Complete methodology codification |
| 1937 | *Wall Street Ventures and Adventures* (posthumous) | Autobiographical context |

### 2.3 Evolution of the Method

```
Wyckoff (1930s)          → Pure tape reading, price-volume analysis
    │
    ├── Robert Evans      → Formalized schematics (1960s–1970s)
    │
    ├── Hank Pruden       → Academic framework, behavioral finance link (1990s–2010s)
    │
    ├── Tom Williams       → Volume Spread Analysis (VSA) (1990s–2000s)
    │
    ├── David Weis        → Weis Wave, modern volume tools (2000s–2020s)
    │
    └── SMC/ICT Community → Integration with Order Blocks, Fair Value Gaps (2010s–present)
```

### 2.4 The Wyckoff Method in the Digital Age

The method has experienced a renaissance in modern trading due to:

- **Crypto markets**: 24/7 trading with extreme volatility mirrors early 1900s stock manipulation
- **Order flow tools**: Modern platforms allow real-time volume profiling that Wyckoff could only approximate
- **Algorithmic detection**: Machine learning can identify Wyckoff patterns faster than manual analysis
- **Social media**: Retail crowding creates predictable liquidity pools that Composite Man exploits

---

## 3. The Three Fundamental Laws of Wyckoff

### 3.1 Law 1: The Law of Supply and Demand

> *"When demand exceeds supply, prices rise. When supply exceeds demand, prices fall."*

This is the foundational principle. While seemingly obvious, Wyckoff's insight was that **price alone does not reveal the supply/demand balance** — volume and price spread together reveal the truth.

#### Mathematical Expression

The instantaneous supply-demand imbalance can be modeled as:

$$
\Delta_{SD}(t) = D(t) - S(t)
$$

Where:
- $D(t)$ = demand pressure at time $t$
- $S(t)$ = supply pressure at time $t$

In practice, we approximate this using volume-price relationships:

$$
\Delta_{SD}(t) \approx V(t) \cdot \text{sign}(\Delta P(t)) \cdot \frac{|\Delta P(t)|}{\text{ATR}(n)}
$$

Where:
- $V(t)$ = volume at bar $t$
- $\Delta P(t) = C(t) - O(t)$ (close minus open)
- $\text{ATR}(n)$ = Average True Range over $n$ periods

#### Key Principles

| Condition | Volume | Spread | Close | Interpretation |
|---|---|---|---|---|
| Demand dominant | High | Wide | Near high | Strong buying — continuation up |
| Supply dominant | High | Wide | Near low | Strong selling — continuation down |
| Demand drying up | Low | Narrow | Middle | No demand — potential reversal down |
| Supply drying up | Low | Narrow | Middle | No supply — potential reversal up |
| Absorption | High | Narrow | Near high | Supply being absorbed by demand |
| Distribution | High | Narrow | Near low | Demand being absorbed by supply |

#### Algorithm: Supply/Demand Classification

```python
def classify_supply_demand(candle, atr):
    """
    Classify the supply/demand balance for a single candle.
    
    Parameters:
        candle: dict with 'open', 'high', 'low', 'close', 'volume'
        atr: float, current ATR value
    
    Returns:
        str: classification label
        float: strength score [-1.0, 1.0]
    """
    spread = candle['high'] - candle['low']
    body = abs(candle['close'] - candle['open'])
    close_position = (candle['close'] - candle['low']) / spread if spread > 0 else 0.5
    
    relative_spread = spread / atr
    relative_volume = candle['volume'] / avg_volume  # normalized
    
    # Effort: volume * spread (normalized)
    effort = relative_volume * relative_spread
    
    # Result: body / spread (how much of the effort translated to directional move)
    result = body / spread if spread > 0 else 0
    
    # Direction
    bullish = candle['close'] > candle['open']
    
    # Classify
    if relative_volume > 1.5 and relative_spread > 1.2 and close_position > 0.7:
        return "STRONG_DEMAND", min(effort * result, 1.0)
    elif relative_volume > 1.5 and relative_spread > 1.2 and close_position < 0.3:
        return "STRONG_SUPPLY", -min(effort * result, 1.0)
    elif relative_volume < 0.6 and relative_spread < 0.7:
        if close_position > 0.5:
            return "NO_SUPPLY", 0.3
        else:
            return "NO_DEMAND", -0.3
    elif relative_volume > 1.5 and relative_spread < 0.7 and close_position > 0.6:
        return "ABSORPTION_DEMAND", 0.6
    elif relative_volume > 1.5 and relative_spread < 0.7 and close_position < 0.4:
        return "ABSORPTION_SUPPLY", -0.6
    else:
        strength = (close_position - 0.5) * 2 * relative_volume * result
        return "NEUTRAL", max(-1.0, min(1.0, strength))
```

### 3.2 Law 2: The Law of Cause and Effect

> *"The effect (price move) is directly proportional to the cause (accumulation/distribution period)."*

This law establishes a quantitative relationship between the duration/intensity of a trading range (cause) and the subsequent trending move (effect).

#### Point-and-Figure Count Method

Wyckoff used Point-and-Figure (P&F) charts to measure the "cause" and project the "effect":

$$
\text{Price Target} = P_{\text{base}} \pm (n_{\text{columns}} \times \text{box\_size} \times \text{reversal})
$$

Where:
- $P_{\text{base}}$ = base price of the trading range
- $n_{\text{columns}}$ = number of P&F columns in the trading range (horizontal count)
- $\text{box\_size}$ = P&F box size
- $\text{reversal}$ = P&F reversal amount (typically 3)

#### Modern Adaptation — Range-Duration Model

For algorithmic purposes, we use a modernized version:

$$
\text{Projected Move} = \alpha \cdot W_{\text{range}} \cdot \sqrt{\frac{T_{\text{range}}}{T_{\text{ref}}}} \cdot \frac{V_{\text{avg\_range}}}{V_{\text{avg\_prior}}}
$$

Where:
- $\alpha$ = calibration constant (asset-specific, typically 1.0–3.0)
- $W_{\text{range}}$ = width (price range) of the consolidation
- $T_{\text{range}}$ = duration of the consolidation (in bars)
- $T_{\text{ref}}$ = reference period (e.g., 20 bars)
- $V_{\text{avg\_range}}$ = average volume during consolidation
- $V_{\text{avg\_prior}}$ = average volume before consolidation

#### Interpretation for the Trading System

| Cause Duration | Cause Intensity (Volume) | Expected Effect |
|---|---|---|
| Short (< 20 bars) | Low volume | Minor move (1–2 ATR) |
| Medium (20–80 bars) | Average volume | Moderate move (3–5 ATR) |
| Long (80–200 bars) | High volume | Major move (5–10 ATR) |
| Extended (> 200 bars) | Very high volume | Trend-defining move (10+ ATR) |

### 3.3 Law 3: The Law of Effort vs. Result

> *"The result (price change) should be proportional to the effort (volume). When they diverge, a change is imminent."*

This is the most actionable law for algorithmic detection. Divergences between effort and result signal manipulation or exhaustion.

#### Mathematical Framework

**Effort-Result Ratio:**

$$
ER(t) = \frac{\text{Result}(t)}{\text{Effort}(t)} = \frac{|P_{\text{close}}(t) - P_{\text{close}}(t-1)|}{V(t) / \bar{V}(n)}
$$

**Cumulative Effort-Result Divergence (over window $w$):**

$$
\text{ERD}(t, w) = \sum_{i=t-w}^{t} \left[ \frac{\Delta P_{\text{norm}}(i)}{V_{\text{norm}}(i)} \right] - \mu_{\text{ER}}
$$

Where:
- $\Delta P_{\text{norm}}(i) = \frac{P(i) - P(i-1)}{\text{ATR}(n)}$
- $V_{\text{norm}}(i) = \frac{V(i)}{\bar{V}(n)}$
- $\mu_{\text{ER}}$ = long-term mean of the effort-result ratio

#### Divergence Detection

```
Effort-Result Divergence Types:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type 1: High Effort, Low Result (Absorption)
   ├── Bullish: Price barely drops on high volume → demand absorbing supply
   └── Bearish: Price barely rises on high volume → supply absorbing demand

Type 2: Low Effort, High Result (Ease of Movement)
   ├── Bullish: Price rises significantly on low volume → no resistance
   └── Bearish: Price falls significantly on low volume → no support

Type 3: Increasing Effort, Diminishing Result (Exhaustion)
   ├── Up-trend: Each new high requires more volume → buyers exhausting
   └── Down-trend: Each new low requires more volume → sellers exhausting
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### Algorithm: Effort-Result Divergence Scanner

```python
def detect_effort_result_divergence(prices, volumes, atr, lookback=20):
    """
    Detect effort vs result divergences over a lookback window.
    
    Returns:
        list of dicts with divergence type, location, and strength
    """
    divergences = []
    avg_vol = np.mean(volumes[-lookback*2:-lookback])  # prior average
    
    for i in range(len(prices) - lookback, len(prices)):
        price_change = abs(prices[i] - prices[i-1]) / atr[i]
        vol_ratio = volumes[i] / avg_vol if avg_vol > 0 else 1.0
        
        # Type 1: High effort, low result
        if vol_ratio > 1.8 and price_change < 0.3:
            direction = "BULLISH" if prices[i] <= prices[i-1] else "BEARISH"
            divergences.append({
                'type': 'ABSORPTION',
                'index': i,
                'direction': direction,
                'strength': vol_ratio / (price_change + 0.01),
                'volume_ratio': vol_ratio,
                'price_change_atr': price_change
            })
        
        # Type 2: Low effort, high result
        elif vol_ratio < 0.5 and price_change > 1.0:
            direction = "BULLISH" if prices[i] > prices[i-1] else "BEARISH"
            divergences.append({
                'type': 'EASE_OF_MOVEMENT',
                'index': i,
                'direction': direction,
                'strength': price_change / (vol_ratio + 0.01),
                'volume_ratio': vol_ratio,
                'price_change_atr': price_change
            })
    
    # Type 3: Trend exhaustion (requires swing analysis)
    swing_highs = find_swing_highs(prices, lookback)
    if len(swing_highs) >= 2:
        for j in range(1, len(swing_highs)):
            prev_idx, curr_idx = swing_highs[j-1], swing_highs[j]
            price_higher = prices[curr_idx] > prices[prev_idx]
            vol_higher = volumes[curr_idx] > volumes[prev_idx]
            
            if price_higher and not vol_higher:
                divergences.append({
                    'type': 'EXHAUSTION',
                    'index': curr_idx,
                    'direction': 'BEARISH',
                    'strength': (volumes[prev_idx] / volumes[curr_idx]) * \
                                (prices[curr_idx] - prices[prev_idx]) / atr[curr_idx],
                    'note': 'Higher high on lower volume — uptrend exhaustion'
                })
    
    return divergences
```

---

## 4. The Composite Man Concept

### 4.1 Definition

> *"All the fluctuations in the market and in all the various stocks should be studied as if they were the result of one man's operations. Let us call him the Composite Man, who, in theory, sits behind the scenes and manipulates the stocks to your disadvantage if you do not understand the game as he plays it; and to your great profit if you do understand it."*
> — Richard D. Wyckoff

The Composite Man (CM) represents the aggregate behavior of all large, informed market participants:

- **Forex**: Central banks, major commercial banks, hedge funds, sovereign wealth funds
- **Crypto**: Whales, market makers, exchange operators, OTC desks, venture funds

### 4.2 Composite Man Behavior Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPOSITE MAN CYCLE                          │
│                                                                 │
│   Phase 1: ACCUMULATION                                         │
│   ├── CM buys quietly during fear/panic                         │
│   ├── Uses selling climax to buy at discount                    │
│   ├── Tests supply with "springs" (shakeouts)                   │
│   └── Builds position without moving price up                   │
│                                                                 │
│   Phase 2: MARKUP                                               │
│   ├── CM allows price to rise (withdraws supply)                │
│   ├── Creates pullbacks for additional buying                   │
│   ├── Media narratives turn bullish (attracts retail)           │
│   └── Volume confirms demand > supply                           │
│                                                                 │
│   Phase 3: DISTRIBUTION                                         │
│   ├── CM sells quietly during euphoria/greed                    │
│   ├── Uses buying climax to sell at premium                     │
│   ├── Tests demand with "upthrusts" (fakeouts)                  │
│   └── Unloads position without moving price down                │
│                                                                 │
│   Phase 4: MARKDOWN                                             │
│   ├── CM allows price to fall (withdraws demand)                │
│   ├── Creates rallies for additional selling                    │
│   ├── Media narratives turn bearish (causes retail panic)       │
│   └── Volume confirms supply > demand                           │
│                                                                 │
│   ← Cycle repeats ─────────────────────────────────────────→    │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Detecting Composite Man Activity

The trading system detects CM activity through the following signals:

| Signal | Detection Method | Confidence |
|---|---|---|
| **Unusual volume** | Volume > 2.5 standard deviations from mean | High |
| **Volume-price divergence** | High volume, narrow spread (absorption) | High |
| **Stop hunts** | Price pierces key level then reverses sharply | Medium-High |
| **Accumulation footprint** | Repeated tests of support with decreasing volume | High |
| **Distribution footprint** | Repeated tests of resistance with decreasing volume | High |
| **Climactic action** | Extreme volume + wide spread + reversal | Very High |
| **Spring/Upthrust** | False break of range boundary with reversal | Very High |

### 4.4 Composite Man in Forex

In Forex markets, the Composite Man manifests through:

1. **Central bank interventions**: Direct or verbal intervention creating climactic volume
2. **Interbank order flow**: Large orders placed at key levels creating absorption patterns
3. **Liquidity sweeps**: Price briefly penetrates major support/resistance to trigger stops before reversing
4. **Session transitions**: Accumulation during Asian session, markup during London session — or vice versa
5. **News-driven manipulation**: Using high-impact news releases to create selling/buying climaxes

### 4.5 Composite Man in Crypto

Crypto markets exhibit more pronounced CM behavior due to:

1. **Lower liquidity**: Easier to manipulate with smaller capital
2. **24/7 markets**: Low-liquidity periods (weekends, off-hours) enable cheaper manipulation
3. **Transparent order books**: Spoofing and layering to create false supply/demand walls
4. **On-chain visibility**: Whale wallet movements can be tracked (but often obfuscated)
5. **Exchange manipulation**: Wash trading, self-trading to simulate volume
6. **Funding rate manipulation**: In perpetual futures, CM can exploit funding rate mechanics

#### Algorithm: Composite Man Activity Score

```python
def composite_man_activity_score(candles, lookback=50):
    """
    Calculate a normalized score [0, 100] indicating the likelihood
    that the Composite Man is actively operating in the current range.
    
    High scores suggest accumulation or distribution in progress.
    """
    score = 0.0
    max_score = 0.0
    
    prices = [c['close'] for c in candles[-lookback:]]
    volumes = [c['volume'] for c in candles[-lookback:]]
    spreads = [c['high'] - c['low'] for c in candles[-lookback:]]
    
    avg_vol = np.mean(volumes)
    std_vol = np.std(volumes)
    avg_spread = np.mean(spreads)
    price_range = max(prices) - min(prices)
    
    # Factor 1: Unusual volume spikes (weight: 25)
    max_score += 25
    vol_spikes = sum(1 for v in volumes if v > avg_vol + 2 * std_vol)
    score += min(25, vol_spikes * 5)
    
    # Factor 2: Volume-price divergence (weight: 25)
    max_score += 25
    absorption_count = 0
    for i in range(1, len(candles[-lookback:])):
        if volumes[i] > avg_vol * 1.5 and spreads[i] < avg_spread * 0.6:
            absorption_count += 1
    score += min(25, absorption_count * 4)
    
    # Factor 3: Range contraction (consolidation) (weight: 20)
    max_score += 20
    recent_range = max(prices[-10:]) - min(prices[-10:])
    full_range = max(prices) - min(prices)
    if full_range > 0:
        contraction = 1 - (recent_range / full_range)
        score += contraction * 20
    
    # Factor 4: Multiple tests of support/resistance (weight: 15)
    max_score += 15
    support_level = min(prices)
    resistance_level = max(prices)
    support_threshold = support_level + price_range * 0.05
    resistance_threshold = resistance_level - price_range * 0.05
    
    support_tests = sum(1 for p in prices if p <= support_threshold)
    resistance_tests = sum(1 for p in prices if p >= resistance_threshold)
    score += min(15, max(support_tests, resistance_tests) * 2.5)
    
    # Factor 5: Decreasing volume on tests (weight: 15)
    max_score += 15
    test_volumes = []
    for i in range(len(prices)):
        if prices[i] <= support_threshold or prices[i] >= resistance_threshold:
            test_volumes.append(volumes[i])
    
    if len(test_volumes) >= 3:
        vol_trend = np.polyfit(range(len(test_volumes)), test_volumes, 1)[0]
        if vol_trend < 0:  # decreasing volume on tests
            score += min(15, abs(vol_trend) / avg_vol * 100)
    
    return min(100, (score / max_score) * 100) if max_score > 0 else 0
```

---

## 5. Four Market Phases

### 5.1 Phase Overview

```
Price
  │
  │                    ┌──────────────────┐
  │                   ╱│   DISTRIBUTION   │╲
  │                  ╱ │   (Phase 3)      │ ╲
  │                 ╱  └──────────────────┘  ╲
  │                ╱                          ╲
  │    MARKUP     ╱                            ╲    MARKDOWN
  │   (Phase 2)  ╱                              ╲  (Phase 4)
  │             ╱                                ╲
  │            ╱                                  ╲
  │           ╱                                    ╲
  │ ┌────────────────────┐               ┌────────────────────┐
  │ │   ACCUMULATION     │               │   ACCUMULATION     │
  │ │   (Phase 1)        │               │   (Phase 1 — next) │
  │ └────────────────────┘               └────────────────────┘
  │
  └──────────────────────────────────────────────────────────→ Time
```

### 5.2 Phase 1: Accumulation

**Definition**: A sideways trading range at the bottom of a downtrend where the Composite Man builds a long position.

| Characteristic | Description |
|---|---|
| **Price Action** | Consolidation range after downtrend; support tested multiple times |
| **Volume** | High at selling climax, then progressively decreasing on subsequent tests |
| **Duration** | Proportional to the size of the subsequent markup move |
| **Key Events** | Selling Climax (SC), Spring, Sign of Strength (SOS) |
| **Sentiment** | Fear, capitulation, despair among retail traders |
| **CM Behavior** | Absorbing supply at low prices, creating false breakdowns to shake out weak hands |

**Detailed analysis**: See `01_accumulation_schematic.md`

### 5.3 Phase 2: Markup

**Definition**: An uptrend following accumulation where price moves higher as demand exceeds supply.

| Characteristic | Description |
|---|---|
| **Price Action** | Higher highs and higher lows; pullbacks are shallow and bought |
| **Volume** | Increases on advances, decreases on pullbacks |
| **Structure** | May include re-accumulation ranges (stepping stones) |
| **Key Events** | Back-up to Creek (BU), Sign of Strength (SOS), higher pivots |
| **Sentiment** | Skepticism → cautious optimism → confidence |
| **CM Behavior** | Allowing price to rise, buying on pullbacks, supporting price at key levels |

**Markup Trading Logic:**

```python
def markup_trade_logic(market_state, candle, indicators):
    """
    Entry logic during confirmed markup phase.
    Buy pullbacks to support in an uptrend.
    """
    if market_state.phase != 'MARKUP':
        return None
    
    conditions = {
        'higher_low': candle['low'] > market_state.prev_swing_low,
        'pullback_to_support': candle['low'] <= market_state.dynamic_support * 1.005,
        'volume_decreasing': candle['volume'] < market_state.avg_volume * 0.8,
        'bullish_close': candle['close'] > (candle['high'] + candle['low']) / 2,
        'above_ema': candle['close'] > indicators['ema_20'],
    }
    
    if all(conditions.values()):
        return {
            'action': 'BUY',
            'entry': candle['close'],
            'stop_loss': market_state.prev_swing_low - market_state.atr * 0.5,
            'take_profit_1': candle['close'] + market_state.atr * 2.0,
            'take_profit_2': candle['close'] + market_state.atr * 4.0,
            'confidence': sum(conditions.values()) / len(conditions),
            'phase': 'MARKUP',
            'sub_type': 'PULLBACK_BUY'
        }
    
    return None
```

### 5.4 Phase 3: Distribution

**Definition**: A sideways trading range at the top of an uptrend where the Composite Man unloads a long position (or builds a short position).

| Characteristic | Description |
|---|---|
| **Price Action** | Consolidation range after uptrend; resistance tested multiple times |
| **Volume** | High at buying climax, then progressively decreasing on subsequent tests |
| **Duration** | Proportional to the size of the subsequent markdown move |
| **Key Events** | Buying Climax (BC), Upthrust After Distribution (UTAD), Sign of Weakness (SOW) |
| **Sentiment** | Euphoria, greed, FOMO among retail traders |
| **CM Behavior** | Distributing supply at high prices, creating false breakouts to attract buyers |

**Detailed analysis**: See `02_distribution_schematic.md`

### 5.5 Phase 4: Markdown

**Definition**: A downtrend following distribution where price moves lower as supply exceeds demand.

| Characteristic | Description |
|---|---|
| **Price Action** | Lower highs and lower lows; rallies are shallow and sold into |
| **Volume** | Increases on declines, decreases on rallies |
| **Structure** | May include re-distribution ranges |
| **Key Events** | Last Point of Supply (LPSY), lower pivots, widening spreads down |
| **Sentiment** | Denial → anxiety → fear → capitulation |
| **CM Behavior** | Allowing price to fall, selling on rallies, placing supply at key levels |

**Markdown Trading Logic:**

```python
def markdown_trade_logic(market_state, candle, indicators):
    """
    Entry logic during confirmed markdown phase.
    Sell rallies to resistance in a downtrend.
    """
    if market_state.phase != 'MARKDOWN':
        return None
    
    conditions = {
        'lower_high': candle['high'] < market_state.prev_swing_high,
        'rally_to_resistance': candle['high'] >= market_state.dynamic_resistance * 0.995,
        'volume_decreasing': candle['volume'] < market_state.avg_volume * 0.8,
        'bearish_close': candle['close'] < (candle['high'] + candle['low']) / 2,
        'below_ema': candle['close'] < indicators['ema_20'],
    }
    
    if all(conditions.values()):
        return {
            'action': 'SELL',
            'entry': candle['close'],
            'stop_loss': market_state.prev_swing_high + market_state.atr * 0.5,
            'take_profit_1': candle['close'] - market_state.atr * 2.0,
            'take_profit_2': candle['close'] - market_state.atr * 4.0,
            'confidence': sum(conditions.values()) / len(conditions),
            'phase': 'MARKDOWN',
            'sub_type': 'RALLY_SELL'
        }
    
    return None
```

---

## 6. Wyckoff Market Cycle — Complete Diagram

```
                                DISTRIBUTION
                            ┌────────────────────┐
                     PSY   BC  AR  ST  UTAD LPSY SOW
                      │    │   │   │    │    │    │
Price                 │    │   │   │    │    │    │
  │                   ↑    ↑↓  ↓   ↑↓   ↑↓   ↓    ↓
  │                 ╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╲
  │                ╱  ┌─↑──↓──↑──↓──↑──↓──↓──↓──┐ ╲
  │               ╱   │  Resistance ═══════════  │  ╲
  │              ╱    │           Trading Range   │   ╲
  │   M         ╱     │  Support ════════════════ │    ╲     M
  │   A        ╱      └──────────────────────────┘     ╲    A
  │   R       ╱                                         ╲   R
  │   K      ╱                                           ╲  K
  │   U     ╱        ← Law of Cause and Effect →          ╲ D
  │   P    ╱           (width = projected move)             ╲O
  │       ╱                                                  ╲W
  │      ╱                                                    ╲N
  │     ╱                                                      ╲
  │ ┌──────────────────────────┐                    ┌──────────────────┐
  │ │   Resistance ═══════════ │                    │                  │
  │ │         Trading Range    │                    │  Next Cycle      │
  │ │   Support ══════════════ │                    │  Accumulation    │
  │ └──────────────────────────┘                    └──────────────────┘
  │  PS SC AR ST  Spring Test SOS LPS BU
  │  │  │  │  │    │    │    │   │   │
  │  ↓  ↓↑ ↑  ↓↑   ↓↑   ↑    ↑   ↓↑  ↑
  │  ╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╱
  │        ACCUMULATION
  │
  └──────────────────────────────────────────────────────────→ Time
```

### 6.1 Phase Transition Signals

| Transition | From → To | Key Signal | Volume Confirmation |
|---|---|---|---|
| **Accumulation → Markup** | Phase 1 → 2 | SOS breaks above trading range resistance | Volume expansion on breakout |
| **Markup → Distribution** | Phase 2 → 3 | Price enters new trading range after uptrend | Volume spike at Buying Climax |
| **Distribution → Markdown** | Phase 3 → 4 | SOW breaks below trading range support | Volume expansion on breakdown |
| **Markdown → Accumulation** | Phase 4 → 1 | Price enters new trading range after downtrend | Volume spike at Selling Climax |

### 6.2 State Transition Matrix

$$
T = \begin{bmatrix}
P(A \rightarrow A) & P(A \rightarrow M_u) & P(A \rightarrow D) & P(A \rightarrow M_d) \\
P(M_u \rightarrow A) & P(M_u \rightarrow M_u) & P(M_u \rightarrow D) & P(M_u \rightarrow M_d) \\
P(D \rightarrow A) & P(D \rightarrow M_u) & P(D \rightarrow D) & P(D \rightarrow M_d) \\
P(M_d \rightarrow A) & P(M_d \rightarrow M_u) & P(M_d \rightarrow D) & P(M_d \rightarrow M_d)
\end{bmatrix}
$$

Typical probability values:

$$
T \approx \begin{bmatrix}
0.70 & 0.25 & 0.00 & 0.05 \\
0.05 & 0.65 & 0.25 & 0.05 \\
0.00 & 0.05 & 0.70 & 0.25 \\
0.25 & 0.05 & 0.05 & 0.65
\end{bmatrix}
$$

Where: $A$ = Accumulation, $M_u$ = Markup, $D$ = Distribution, $M_d$ = Markdown

Note: The $P(A \rightarrow M_d) = 0.05$ represents failed accumulation (scheme failure), and similarly $P(D \rightarrow M_u) = 0.05$ represents failed distribution.

---

## 7. Relevance to Modern Forex Markets

### 7.1 Why Wyckoff Works in Forex

The Forex market is a $7.5 trillion/day market dominated by institutional players — the perfect environment for Wyckoff analysis:

1. **Centralized liquidity pools**: Major pairs (EUR/USD, GBP/USD, USD/JPY) have deep order books where CM activity is detectable
2. **Session-based structure**: Asian → London → New York sessions create natural accumulation/distribution cycles
3. **Central bank influence**: Policy decisions create climactic volume events that define phase boundaries
4. **Carry trade dynamics**: Interest rate differentials create persistent flows that map to markup/markdown phases
5. **Technical level clustering**: Institutional orders cluster at round numbers, Fibonacci levels, and prior swing points

### 7.2 Forex-Specific Adaptations

| Standard Wyckoff | Forex Adaptation |
|---|---|
| Daily volume | Tick volume as proxy (or real volume from futures/ECN) |
| Single timeframe | Multi-session analysis (Asian accumulation → London markup) |
| Absolute price levels | Pip-based measurements relative to ATR |
| General CM concept | Central bank + interbank dealer model |
| P&F projections | ATR-based and Fibonacci-based projections |

### 7.3 Forex Session-Wyckoff Mapping

```
Intraday Wyckoff Cycle (Common Pattern):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

00:00 ── 08:00 UTC │ Asian Session     │ ACCUMULATION
                    │ Low volatility    │ Range-bound, CM builds position
                    │ Tick vol: LOW     │ at session highs/lows
                    │                   │
08:00 ── 12:00 UTC │ London Open       │ MARKUP / MARKDOWN
                    │ High volatility   │ Breakout from Asian range
                    │ Tick vol: HIGH    │ SOS or SOW from Asian range
                    │                   │
12:00 ── 16:00 UTC │ London/NY Overlap │ CONTINUATION or DISTRIBUTION
                    │ Peak volatility   │ Trend continuation or reversal
                    │ Tick vol: PEAK    │ at London session extreme
                    │                   │
16:00 ── 21:00 UTC │ NY Afternoon      │ DISTRIBUTION / RE-ACCUMULATION
                    │ Declining vol     │ Profit-taking or new range
                    │ Tick vol: MEDIUM  │ formation
                    │                   │
21:00 ── 00:00 UTC │ Late NY / Pre-Asia│ QUIET RANGE
                    │ Minimal vol       │ No significant CM activity
                    │ Tick vol: VERY LOW│

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 7.4 Forex Volume Considerations

Since spot Forex lacks centralized volume data, the system uses:

1. **Tick volume**: Number of price changes per bar (correlated ~0.85 with real volume)
2. **Futures volume**: CME currency futures provide real volume data
3. **ECN volume**: Some brokers provide aggregated ECN volume
4. **CoT data**: Commitment of Traders reports for weekly positioning analysis

$$
V_{\text{proxy}}(t) = w_1 \cdot V_{\text{tick}}(t) + w_2 \cdot V_{\text{futures}}(t) + w_3 \cdot V_{\text{ECN}}(t)
$$

Where $w_1 + w_2 + w_3 = 1$ and weights are calibrated per broker/data source.

---

## 8. Relevance to Modern Crypto Markets

### 8.1 Why Wyckoff is Critical for Crypto

Cryptocurrency markets are arguably the most Wyckoff-compatible markets in existence:

1. **Extreme manipulation**: Lower regulation means CM operates with fewer constraints
2. **24/7 trading**: Manipulation occurs during low-liquidity periods (2–6 AM UTC on weekends)
3. **Transparent volume**: Real exchange volume is available (after filtering wash trades)
4. **On-chain data**: Whale movements provide additional CM detection signals
5. **Retail-dominated**: High retail participation creates predictable liquidity pools for CM
6. **Leverage**: Pervasive leverage creates forced liquidation cascades that mimic climactic action

### 8.2 Bitcoin Wyckoff Case Studies

The Bitcoin price history contains textbook Wyckoff patterns:

| Period | Phase | Key Event | Duration | Subsequent Move |
|---|---|---|---|---|
| Mar–Oct 2020 | Accumulation | COVID crash = SC, $3.8K spring | ~7 months | +1,500% markup to $64K |
| May–Jul 2021 | Re-accumulation | $30K range, spring to $28.8K | ~3 months | +130% markup to $69K |
| Nov 2021–Jan 2022 | Distribution | $69K BC, $67K UTAD | ~3 months | -77% markdown to $15.5K |
| Jun–Nov 2022 | Accumulation | FTX collapse = spring, $15.5K low | ~5 months | +360% markup to $73K |
| Mar–Oct 2023 | Re-accumulation | $25K–$30K range | ~7 months | +140% markup |

### 8.3 Crypto-Specific Adaptations

| Standard Wyckoff | Crypto Adaptation |
|---|---|
| Business hours volume | 24/7 volume with session-weighted analysis |
| CM = institutions | CM = whales + exchanges + market makers |
| Volume from exchanges | Aggregated volume from top exchanges (filtered) |
| P&F projections | Hash-rate-adjusted, funding-rate-adjusted projections |
| Single instrument | Cross-pair correlation (BTC.D, ETH/BTC as CM signals) |

### 8.4 On-Chain Wyckoff Integration

```python
class CryptoWyckoffEnhancer:
    """
    Enhances standard Wyckoff analysis with crypto-specific on-chain data.
    """
    
    def __init__(self, chain_data_provider):
        self.chain = chain_data_provider
    
    def get_whale_accumulation_signal(self, asset, timeframe):
        """
        Detect whale accumulation/distribution via on-chain metrics.
        """
        signals = {}
        
        # Exchange netflow (negative = accumulation, positive = distribution)
        netflow = self.chain.get_exchange_netflow(asset, timeframe)
        signals['exchange_netflow'] = {
            'value': netflow,
            'interpretation': 'ACCUMULATION' if netflow < 0 else 'DISTRIBUTION',
            'strength': min(1.0, abs(netflow) / self.chain.get_avg_netflow(asset))
        }
        
        # Whale wallet changes (addresses holding > 1000 BTC)
        whale_change = self.chain.get_whale_balance_change(asset, timeframe)
        signals['whale_balance'] = {
            'value': whale_change,
            'interpretation': 'ACCUMULATION' if whale_change > 0 else 'DISTRIBUTION',
            'strength': min(1.0, abs(whale_change) / self.chain.get_avg_whale_change(asset))
        }
        
        # UTXO age distribution (for Bitcoin)
        if asset == 'BTC':
            hodl_waves = self.chain.get_hodl_waves(timeframe)
            long_term_pct = hodl_waves.get('1y_plus', 0)
            signals['hodl_waves'] = {
                'value': long_term_pct,
                'interpretation': 'ACCUMULATION' if long_term_pct > 0.65 else 'DISTRIBUTION',
                'strength': abs(long_term_pct - 0.5) * 2
            }
        
        # Funding rate (perpetual futures)
        funding = self.chain.get_funding_rate(asset)
        signals['funding_rate'] = {
            'value': funding,
            'interpretation': 'BEARISH_SENTIMENT' if funding < -0.01 else \
                            'BULLISH_SENTIMENT' if funding > 0.01 else 'NEUTRAL',
            'note': 'Extreme negative funding during accumulation = spring opportunity'
        }
        
        return signals
```

---

## 9. Wyckoff vs Other Methodologies

### 9.1 Comparative Analysis

| Feature | Wyckoff | Elliott Wave | Dow Theory | SMC/ICT | VSA |
|---|---|---|---|---|---|
| **Foundation** | Supply/Demand | Wave patterns | Trend following | Institutional order flow | Volume-price |
| **Volume role** | Central | Secondary | Confirmatory | Secondary | Central |
| **Predictive** | High | High | Medium | High | Medium |
| **Subjectivity** | Medium | High | Low | Medium | Low |
| **Algo-friendly** | High | Medium | High | High | Very High |
| **Best for** | Phase identification | Wave counting | Trend direction | Entry precision | Bar-by-bar reading |
| **Timeframe** | All | All | Daily+ | All | All |
| **Learning curve** | Steep | Very steep | Moderate | Steep | Moderate |

### 9.2 Synergies with Other Methods

The trading system combines Wyckoff with complementary methods:

```
Wyckoff (Phase Identification)
    │
    ├── + Elliott Wave → Wave count confirms Wyckoff phase
    │     (e.g., Wave 1 = SOS after accumulation)
    │
    ├── + SMC/ICT → Order blocks at Wyckoff event points
    │     (e.g., Order block at Spring = high-prob entry)
    │
    ├── + VSA → Bar-by-bar confirmation of Wyckoff events
    │     (e.g., No Supply bar at Last Point of Support)
    │
    ├── + Fibonacci → Retracement targets within Wyckoff phases
    │     (e.g., Spring at 127.2% extension of prior range)
    │
    └── + Market Profile → Value area mapping within Wyckoff ranges
          (e.g., Volume Point of Control at mid-range)
```

---

## 10. Core Logic — Entry/Exit Framework

### 10.1 Entry Logic Summary

| Phase | Entry Type | Trigger | Confirmation | Confidence |
|---|---|---|---|---|
| **Accumulation** | Long | Spring (false breakdown) | Bullish reversal bar + volume increase | 85% |
| **Accumulation** | Long | Test of Spring | Low volume retest of Spring low | 90% |
| **Accumulation** | Long | SOS breakout | High volume break above resistance | 75% |
| **Accumulation** | Long | BU (Back-Up) | Pullback to broken resistance (now support) | 80% |
| **Markup** | Long | Pullback buy | Higher low + decreasing volume | 70% |
| **Markup** | Long | Re-accumulation breakout | Break above stepping-stone range | 75% |
| **Distribution** | Short | UTAD (false breakout) | Bearish reversal bar + volume increase | 85% |
| **Distribution** | Short | Test of UTAD | Low volume retest of UTAD high | 90% |
| **Distribution** | Short | SOW breakdown | High volume break below support | 75% |
| **Distribution** | Short | LPSY (Last Point of Supply) | Rally to lower high on declining volume | 80% |
| **Markdown** | Short | Rally sell | Lower high + decreasing volume | 70% |
| **Markdown** | Short | Re-distribution breakdown | Break below stepping-stone range | 75% |

### 10.2 Exit Logic Summary

| Condition | Action | Priority |
|---|---|---|
| Stop loss hit | Exit entire position | Immediate |
| Phase change detected | Evaluate: close, reduce, or hold | High |
| Target 1 reached | Close 50% of position | Medium |
| Target 2 reached | Close remaining position | Medium |
| Opposing Wyckoff event | Close position | High |
| Volume divergence against position | Tighten stop to breakeven | Medium |
| Time stop (phase exceeded expected duration) | Reduce position by 50% | Low |

---

## 11. Technical Specifications

### 11.1 System Parameters

| Parameter | Default | Range | Description |
|---|---|---|---|
| `lookback_period` | 200 | 100–500 | Bars for phase identification |
| `volume_avg_period` | 20 | 10–50 | Volume moving average period |
| `atr_period` | 14 | 7–21 | ATR period for normalization |
| `swing_threshold` | 0.5 ATR | 0.2–1.0 ATR | Min swing size for structure detection |
| `volume_spike_threshold` | 2.0σ | 1.5–3.0σ | Volume spike detection threshold |
| `spring_depth` | 0.5% | 0.2–2.0% | Max penetration below support for Spring |
| `sos_strength` | 1.5 ATR | 1.0–3.0 ATR | Min SOS rally above resistance |
| `phase_min_bars` | 20 | 10–50 | Minimum bars for phase identification |
| `phase_max_bars` | 300 | 100–500 | Maximum bars before phase timeout |
| `confidence_threshold` | 0.65 | 0.5–0.9 | Min confidence for signal generation |

### 11.2 Timeframe Configuration

| Timeframe | Use Case | Phase Detection | Entry Timing |
|---|---|---|---|
| Monthly (1M) | Macro phase identification | Primary | No |
| Weekly (1W) | Phase confirmation | Primary | No |
| Daily (1D) | Phase events (SC, Spring, SOS) | Primary | Yes |
| 4-Hour (4H) | Sub-phase identification | Secondary | Yes |
| 1-Hour (1H) | Entry/exit timing | Timing | Yes |
| 15-Minute (15M) | Precise entry placement | Timing | Yes |
| 5-Minute (5M) | Scalp entries within phases | Timing | Optional |

---

## 12. Mathematical Models

### 12.1 Phase Probability Model

The probability of being in phase $\phi$ given observed features $\mathbf{x}$:

$$
P(\phi | \mathbf{x}) = \frac{P(\mathbf{x} | \phi) \cdot P(\phi)}{\sum_{\phi' \in \Phi} P(\mathbf{x} | \phi') \cdot P(\phi')}
$$

Where:
- $\Phi = \{A, M_u, D, M_d\}$ (the four phases)
- $\mathbf{x} = [x_{\text{trend}}, x_{\text{vol}}, x_{\text{range}}, x_{\text{structure}}, x_{\text{sentiment}}]$
- $P(\phi)$ = prior probability from state transition matrix

### 12.2 Feature Vector Components

$$
x_{\text{trend}} = \frac{EMA_{20} - EMA_{50}}{ATR_{14}}
$$

$$
x_{\text{vol}} = \frac{V_{\text{current}} - \bar{V}_{20}}{\sigma_{V,20}}
$$

$$
x_{\text{range}} = \frac{H_{\text{max},N} - L_{\text{min},N}}{ATR_{14} \cdot \sqrt{N}}
$$

$$
x_{\text{structure}} = \frac{\text{count}(HH) + \text{count}(HL) - \text{count}(LH) - \text{count}(LL)}{N_{\text{swings}}}
$$

### 12.3 Composite Confidence Score

$$
C_{\text{total}} = \sum_{i=1}^{n} w_i \cdot c_i \cdot r_i
$$

Where:
- $w_i$ = weight of factor $i$ (sum to 1.0)
- $c_i$ = individual confidence score [0, 1]
- $r_i$ = reliability factor based on historical accuracy [0, 1]

---

## 13. Risk Parameters

### 13.1 Default Risk Parameters by Phase

| Phase | Risk per Trade | Max SL (ATR) | Min RR | Max Concurrent | Max Daily Loss |
|---|---|---|---|---|---|
| Accumulation (Spring) | 2.0% | 1.5 | 3:1 | 2 | 4% |
| Accumulation (SOS) | 1.5% | 2.0 | 2:1 | 2 | 4% |
| Markup (Pullback) | 1.0% | 1.5 | 2:1 | 3 | 3% |
| Distribution (UTAD) | 2.0% | 1.5 | 3:1 | 2 | 4% |
| Distribution (SOW) | 1.5% | 2.0 | 2:1 | 2 | 4% |
| Markdown (Rally) | 1.0% | 1.5 | 2:1 | 3 | 3% |
| Uncertain Phase | 0.5% | 1.0 | 3:1 | 1 | 1% |

### 13.2 Position Sizing Formula

$$
\text{Position Size} = \frac{\text{Account Balance} \times \text{Risk Percentage}}{|\text{Entry Price} - \text{Stop Loss}| \times \text{Pip Value}}
$$

With confidence adjustment:

$$
\text{Adjusted Size} = \text{Position Size} \times \min(1.0, \frac{C_{\text{total}}}{C_{\text{threshold}}})
$$

---

## 14. Execution Flow

### 14.1 High-Level Algorithm

```
┌─────────────────────────────────────────────┐
│           WYCKOFF TRADING SYSTEM            │
│              Main Loop                       │
├─────────────────────────────────────────────┤
│                                             │
│  1. FETCH market data (OHLCV + tick data)   │
│     │                                       │
│  2. UPDATE indicators (ATR, EMA, Volume)    │
│     │                                       │
│  3. DETECT market structure (swings, BoS)   │
│     │                                       │
│  4. IDENTIFY Wyckoff phase                  │
│     │                                       │
│  5. CHECK for phase events (SC, Spring...)  │
│     │                                       │
│  6. GENERATE signals if confidence > threshold│
│     │                                       │
│  7. VALIDATE against risk parameters        │
│     │                                       │
│  8. EXECUTE trades or update existing       │
│     │                                       │
│  9. MANAGE open positions (trail, exit)     │
│     │                                       │
│ 10. LOG state and update phase tracker      │
│     │                                       │
│     └── LOOP ──────────────────────────→    │
│                                             │
└─────────────────────────────────────────────┘
```

### 14.2 Pseudocode

```python
class WyckoffTradingSystem:
    def __init__(self, config):
        self.config = config
        self.phase_detector = WyckoffPhaseDetector(config)
        self.structure_analyzer = MarketStructureAnalyzer(config)
        self.volume_analyzer = VolumeSpreadAnalyzer(config)
        self.signal_generator = SignalGenerator(config)
        self.risk_manager = RiskManager(config)
        self.position_manager = PositionManager(config)
    
    def on_new_bar(self, candle, timeframe):
        # Step 1-2: Update core data
        self.update_indicators(candle)
        
        # Step 3: Market structure
        structure = self.structure_analyzer.update(candle)
        
        # Step 4: Phase identification
        phase = self.phase_detector.identify_phase(
            candles=self.candle_history,
            structure=structure,
            volume_analysis=self.volume_analyzer.analyze(candle)
        )
        
        # Step 5: Event detection
        events = self.phase_detector.detect_events(phase)
        
        # Step 6: Signal generation
        for event in events:
            signal = self.signal_generator.generate(event, phase, structure)
            if signal and signal.confidence >= self.config.confidence_threshold:
                
                # Step 7: Risk validation
                if self.risk_manager.validate(signal):
                    
                    # Step 8: Execute
                    self.position_manager.execute(signal)
        
        # Step 9: Manage positions
        self.position_manager.manage_positions(candle, phase, structure)
        
        # Step 10: Log
        self.log_state(phase, events, structure)
```

---

## 15. Integration with Multi-Agent System

### 15.1 Agent Communication Protocol

The Wyckoff analysis module communicates with other agents through standardized messages:

```python
class WyckoffStateMessage:
    """
    Standard message format for inter-agent communication.
    """
    def __init__(self):
        self.timestamp = None
        self.symbol = None
        self.timeframe = None
        self.phase = None              # ACCUMULATION, MARKUP, DISTRIBUTION, MARKDOWN
        self.sub_phase = None          # PS, SC, AR, ST, SPRING, SOS, etc.
        self.phase_confidence = 0.0    # [0.0, 1.0]
        self.phase_progress = 0.0      # [0.0, 1.0] how far through the phase
        self.bias = None               # LONG, SHORT, NEUTRAL
        self.key_levels = {}           # support, resistance, creek, etc.
        self.active_events = []        # recent Wyckoff events
        self.volume_profile = {}       # VSA analysis results
        self.structure = {}            # BoS, ChoCh, swing points
        self.signals = []              # trade signals if any
        self.risk_params = {}          # phase-specific risk parameters
```

### 15.2 Agent Dependencies

```
┌──────────────────────────────────────────────────────────────┐
│                     AGENT HIERARCHY                          │
│                                                              │
│  Data Agent ──→ Wyckoff Phase Agent ──→ Signal Agent         │
│       │              │        │              │               │
│       │              ▼        │              ▼               │
│       │    Volume Analysis    │    Risk Management Agent     │
│       │         Agent         │              │               │
│       │              │        │              ▼               │
│       │              ▼        │    Execution Agent            │
│       └──→ Market Structure ──┘              │               │
│              Agent                           ▼               │
│                                    Position Management       │
│                                         Agent                │
└──────────────────────────────────────────────────────────────┘
```

### 15.3 Multi-Timeframe Consensus

The system requires multi-timeframe agreement before generating high-confidence signals:

| HTF Phase | MTF Phase | LTF Signal | Action | Confidence Modifier |
|---|---|---|---|---|
| Accumulation | SOS detected | Pullback buy | **STRONG BUY** | x1.5 |
| Accumulation | Still in range | Spring detected | **BUY** | x1.0 |
| Markup | Healthy pullback | Bullish reversal | **BUY** | x1.2 |
| Markup | Distribution forming | Bearish signal | **AVOID** (conflict) | x0.3 |
| Distribution | SOW detected | Rally sell | **STRONG SELL** | x1.5 |
| Distribution | Still in range | UTAD detected | **SELL** | x1.0 |
| Markdown | Healthy rally | Bearish reversal | **SELL** | x1.2 |
| Markdown | Accumulation forming | Bullish signal | **AVOID** (conflict) | x0.3 |

---

## 16. References

### 16.1 Primary Sources

1. Wyckoff, R.D. (1931). *The Richard D. Wyckoff Method of Trading and Investing in Stocks — A Course of Instruction in Stock Market Science and Technique*. Wyckoff Associates.
2. Wyckoff, R.D. (1910). *Studies in Tape Reading*. The Ticker Publishing Company.
3. Wyckoff, R.D. (1924). *How I Trade and Invest in Stocks and Bonds*. The Magazine of Wall Street.

### 16.2 Secondary Sources

4. Pruden, H.O. (2007). *The Three Skills of Top Trading: Behavioral Systems Building, Pattern Recognition, and Mental State Management*. Wiley.
5. Williams, T. (2005). *Master the Markets: Taking a Professional Approach to Trading & Investing Using Volume Spread Analysis*. TradeGuider Systems.
6. Weis, D.H. (2013). *Trades About to Happen: A Modern Adaptation of the Wyckoff Method*. Wiley.
7. Schroeder, G. (2015). *Wyckoff Power Charting*. StockCharts.com.

### 16.3 Academic References

8. Pruden, H.O. & Belletante, B. (2006). "Wyckoff Schematics: Visual Templates for Market Timing Decisions." *Journal of Technical Analysis*, 63, 38–48.
9. Lo, A.W. (2004). "The Adaptive Markets Hypothesis." *Journal of Portfolio Management*, 30(5), 15–29.
10. Easley, D. & O'Hara, M. (1987). "Price, Trade Size, and Information in Securities Markets." *Journal of Financial Economics*, 19(1), 69–90.

### 16.4 Modern Resources

11. Wyckoff Analytics (wyckoffanalytics.com) — Roman Bogomazov's courses and webinars
12. StockCharts.com — Wyckoff Power Charting series by Bruce Fraser
13. ReadTheMarket.com — David Weis's modern Wyckoff adaptation
14. TradeGuider.com — Tom Williams's VSA methodology

---

> **Next Document**: `01_accumulation_schematic.md` — Detailed Accumulation Phase Analysis
