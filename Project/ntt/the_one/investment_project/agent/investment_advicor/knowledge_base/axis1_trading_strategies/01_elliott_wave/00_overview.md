# Elliott Wave Theory --- Overview

## Document Metadata
| Field | Value |
|---|---|
| **Strategy ID** | EW-000 |
| **Category** | Axis 1 --- Trading Strategies |
| **Sub-Category** | Elliott Wave Theory |
| **Applicable Markets** | Forex, Crypto |
| **Timeframes** | All (Multi-Timeframe) |
| **Complexity** | Advanced |
| **AI Suitability** | High (with proper validation logic) |
| **Last Updated** | 2026-04-12 |

---

## Table of Contents
1. [Historical Background](#1-historical-background)
2. [Philosophical Foundation](#2-philosophical-foundation)
3. [The Fractal Nature of Markets](#3-the-fractal-nature-of-markets)
4. [Core Principle: The Wave Structure](#4-core-principle-the-wave-structure)
5. [Why Elliott Wave Works in Forex Markets](#5-why-elliott-wave-works-in-forex-markets)
6. [Why Elliott Wave Works in Crypto Markets](#6-why-elliott-wave-works-in-crypto-markets)
7. [Strengths for Algorithmic Implementation](#7-strengths-for-algorithmic-implementation)
8. [Limitations and Challenges](#8-limitations-and-challenges)
9. [Integration with Multi-Agent Architecture](#9-integration-with-multi-agent-architecture)
10. [Core Logic --- Entry/Exit Framework](#10-core-logic----entryexit-framework)
11. [Technical Specifications](#11-technical-specifications)
12. [Mathematical Foundation](#12-mathematical-foundation)
13. [Risk Parameters](#13-risk-parameters)
14. [Execution Flow](#14-execution-flow)
15. [References](#15-references)

---

## 1. Historical Background

### 1.1 Ralph Nelson Elliott (1871--1948)

Ralph Nelson Elliott was an American accountant and author who developed the Wave Theory in the 1930s. After a debilitating illness forced his retirement from active professional life, Elliott devoted years to studying 75 years of stock market data across multiple timeframes --- annual, monthly, weekly, daily, hourly, and even half-hourly charts.

His seminal works include:

- **"The Wave Principle"** (1938) --- the original monograph outlining his discovery
- **"Nature's Law: The Secret of the Universe"** (1946) --- his comprehensive treatise linking market behavior to the Fibonacci sequence and natural phenomena

Elliott observed that stock market prices do not move in a random or chaotic manner, but instead follow repetitive, recognizable patterns that reflect the collective psychology of market participants. He identified that these patterns are governed by mathematical relationships rooted in the Fibonacci sequence.

### 1.2 Evolution of the Theory

| Period | Contributor | Contribution |
|---|---|---|
| 1930s--1940s | R.N. Elliott | Original Wave Principle discovery |
| 1950s--1970s | Hamilton Bolton | Kept Elliott's work alive through the *Bolton-Tremblay* supplement |
| 1978 | A.J. Frost & Robert Prechter | Published *Elliott Wave Principle: Key to Market Behavior*, the definitive modern text |
| 1980s--1990s | Robert Prechter | Founded Elliott Wave International; popularized the theory globally |
| 1988 | Glenn Neely | Published *Mastering Elliott Wave*, introducing NeoWave --- a more rigorous, rule-based approach |
| 2000s--Present | Various | Algorithmic implementations, machine learning adaptations, and application to Forex/Crypto markets |

### 1.3 The Socionomic Hypothesis

Robert Prechter extended Elliott's work into **Socionomics** --- the study of how social mood drives social events, including financial markets. Under this framework:

- Markets are not driven by external events (news, earnings, etc.)
- Instead, endogenous social mood --- a herding impulse rooted in human neurobiology --- drives both market prices and social events
- Elliott Wave patterns are the graphical representation of this social mood oscillation

This philosophical underpinning is critical for AI systems because it means:
1. Wave patterns are **self-similar** (fractal) across all timeframes
2. The patterns are **universal** --- they appear in all freely traded markets
3. The patterns are **probabilistic** but not deterministic

---

## 2. Philosophical Foundation

### 2.1 Markets as a Natural Phenomenon

Elliott's central insight was that financial markets behave like natural systems. The same mathematical relationships that govern:
- The spiral of a nautilus shell
- The branching of trees
- The arrangement of sunflower seeds
- The proportions of the human body

...also govern the progression of collective human sentiment as reflected in price charts.

### 2.2 The Fibonacci Connection

The Fibonacci sequence (0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, ...) and the derived Golden Ratio ($\phi = 1.618033...$) are the mathematical backbone of Elliott Wave Theory.

Key relationships:

$$\phi = \frac{1 + \sqrt{5}}{2} \approx 1.6180339887...$$

$$\frac{1}{\phi} = \phi - 1 \approx 0.6180339887...$$

$$\phi^2 = \phi + 1 \approx 2.6180339887...$$

The Fibonacci ratios used in Elliott Wave analysis are derived as follows:

| Ratio | Derivation | Role in EW |
|---|---|---|
| 0.236 | $\frac{F_n}{F_{n+4}}$ as $n \to \infty$ | Shallow retracement |
| 0.382 | $\frac{F_n}{F_{n+2}}$ as $n \to \infty$, i.e., $1 - 0.618$ | Moderate retracement |
| 0.500 | $\frac{1}{2}$ (not Fibonacci, but significant) | Midpoint retracement |
| 0.618 | $\frac{F_n}{F_{n+1}}$ as $n \to \infty$, i.e., $\frac{1}{\phi}$ | Deep retracement |
| 0.786 | $\sqrt{0.618}$ | Very deep retracement |
| 1.000 | Unity | Equality |
| 1.272 | $\sqrt{1.618}$ | Moderate extension |
| 1.618 | $\phi$ | Golden extension |
| 2.000 | $2$ | Double extension |
| 2.618 | $\phi^2$ | Large extension |
| 4.236 | $\phi^3$ | Extreme extension |

### 2.3 Crowd Psychology as Driving Force

Elliott Wave Theory is fundamentally a **crowd psychology model**. Each wave reflects a distinct phase of collective sentiment:

| Wave | Psychological State | Market Characteristic |
|---|---|---|
| Wave 1 | Skeptical accumulation | Low volume, dismissed by most |
| Wave 2 | Fear of return to prior trend | Heavy retracement, high pessimism |
| Wave 3 | Recognition and euphoria | Highest volume, broadest participation |
| Wave 4 | Profit-taking and uncertainty | Complex, time-consuming correction |
| Wave 5 | Greed and overconfidence | Divergences appear, smart money exits |
| Wave A | Denial | Believed to be "just a pullback" |
| Wave B | False hope | Traps late buyers/sellers |
| Wave C | Capitulation | Panic, forced liquidation |

---

## 3. The Fractal Nature of Markets

### 3.1 Self-Similarity Across Timeframes

The most powerful property of Elliott Wave Theory is its **fractal** nature. Each wave is composed of smaller waves of the same type, and each wave is itself a component of a larger wave.

```
Grand Supercycle (multi-decade)
  └── Supercycle (multi-year)
       └── Cycle (1 year to several years)
            └── Primary (months to 1 year)
                 └── Intermediate (weeks to months)
                      └── Minor (days to weeks)
                           └── Minute (hours to days)
                                └── Minuette (minutes to hours)
                                     └── Subminuette (seconds to minutes)
```

### 3.2 Degree Labeling Convention

| Degree | Motive Notation | Corrective Notation | Typical Timeframe |
|---|---|---|---|
| Grand Supercycle | [I] [II] [III] [IV] [V] | [A] [B] [C] | Multi-decade |
| Supercycle | (I) (II) (III) (IV) (V) | (A) (B) (C) | Multi-year |
| Cycle | I II III IV V | A B C | 1--several years |
| Primary | 1 2 3 4 5 | A B C | Months to 1 year |
| Intermediate | (1) (2) (3) (4) (5) | (a) (b) (c) | Weeks to months |
| Minor | 1 2 3 4 5 | a b c | Days to weeks |
| Minute | i ii iii iv v | a b c | Hours to days |
| Minuette | (i) (ii) (iii) (iv) (v) | (a) (b) (c) | Minutes to hours |
| Subminuette | i ii iii iv v | a b c | Seconds to minutes |

### 3.3 Fractal Decomposition

An impulse wave decomposes as follows:

```
5-wave impulse (Motive):
  Wave 1 → 5 sub-waves (impulse)
  Wave 2 → 3 sub-waves (corrective)
  Wave 3 → 5 sub-waves (impulse)
  Wave 4 → 3 sub-waves (corrective)
  Wave 5 → 5 sub-waves (impulse)

Total internal waves: 5 + 3 + 5 + 3 + 5 = 21

3-wave correction (Corrective):
  Wave A → 5 sub-waves (impulse)
  Wave B → 3 sub-waves (corrective)
  Wave C → 5 sub-waves (impulse)

Total internal waves: 5 + 3 + 5 = 13
```

Notice: 21 and 13 are both Fibonacci numbers.

The complete cycle (motive + corrective) contains:
- $21 + 13 = 34$ sub-waves (Fibonacci)
- Decomposing further: $89$ sub-sub-waves (Fibonacci)
- And further: $144$ sub-sub-sub-waves (Fibonacci)

---

## 4. Core Principle: The Wave Structure

### 4.1 The Basic Pattern

Every complete market cycle consists of **8 waves**:

1. **Motive Phase** (5 waves in the direction of the trend): Waves 1, 2, 3, 4, 5
2. **Corrective Phase** (3 waves against the trend): Waves A, B, C

```
         (5)
          /\
    (3)  /  \    (B)
     /\ /    \   /\
(1) /  X  (4) \ /  \
 /\/  / \  /\  X    \
/  (2)   \/  \/  (A) \(C)
```

### 4.2 Wave Characteristics Summary

**Motive Waves** (1, 3, 5, A, C in some structures):
- Move in the direction of the trend of one larger degree
- Always subdivide into 5 waves
- Must obey the three iron rules (see File 01)

**Corrective Waves** (2, 4, B):
- Move against the direction of the trend of one larger degree
- Subdivide into 3 waves (or more complex combinations of 3s)
- Never fully retrace the preceding motive wave

### 4.3 Alternation Principle

One of the most important guidelines in Elliott Wave Theory:

> If Wave 2 is a **sharp** (deep, fast) correction, then Wave 4 will likely be a **sideways** (shallow, slow) correction, and vice versa.

| Wave 2 Type | Expected Wave 4 Type |
|---|---|
| Zigzag (sharp, deep) | Flat/Triangle (sideways, shallow) |
| Flat (sideways) | Zigzag (sharp) |
| Simple | Complex |
| Complex | Simple |

This principle is invaluable for algorithmic prediction because it constrains the set of likely corrective patterns for Wave 4 based on the observed Wave 2.

---

## 5. Why Elliott Wave Works in Forex Markets

### 5.1 High Liquidity and Efficiency

Forex is the world's most liquid market (~$7.5 trillion daily turnover as of recent estimates). This liquidity ensures:

- **Clean wave structures** --- less noise from illiquid price gaps
- **Consistent Fibonacci relationships** --- large participant base creates reliable crowd behavior
- **Multi-timeframe fractal clarity** --- waves are visible from monthly down to 1-minute charts

### 5.2 24/5 Continuous Trading

Unlike equities with gap-prone overnight sessions, Forex trades nearly continuously:
- Wave structures develop without distortion from opening gaps
- Corrective patterns complete more cleanly
- AI systems can monitor wave development in real-time without session-break artifacts

### 5.3 Trending Nature of Currency Pairs

Major currency pairs exhibit strong trending behavior driven by:
- Central bank policy divergence (interest rate differentials)
- Capital flow dynamics
- Carry trade positioning

These trends produce textbook impulse waves, particularly on:
- **EUR/USD** --- most liquid pair, excellent wave clarity
- **GBP/USD** --- volatile, often produces extended Wave 3s
- **USD/JPY** --- strong trending behavior due to carry trade dynamics
- **AUD/USD** --- commodity-linked, clear impulse patterns

### 5.4 Key Forex Considerations

| Factor | Impact on Elliott Wave |
|---|---|
| Session overlaps (London/NY) | Wave 3s often initiate during overlap |
| News events (NFP, FOMC) | Can trigger wave completions/initiations |
| Carry trade unwinding | Produces sharp corrective waves |
| Central bank intervention | Can truncate Wave 5 or extend corrections |

---

## 6. Why Elliott Wave Works in Crypto Markets

### 6.1 Pure Sentiment-Driven Market

Cryptocurrency markets are among the most sentiment-driven in existence:
- No intrinsic cash flows or earnings to anchor valuation
- Price is almost entirely a function of collective belief and momentum
- This makes Elliott Wave patterns particularly prominent

### 6.2 High Volatility Produces Clear Waves

Crypto volatility amplifies wave structures:
- **Wave 3 extensions** are often extreme (261.8%--423.6% of Wave 1)
- **Corrective waves** are sharp and deep (Wave 2 often retraces 61.8%--78.6%)
- **Wave 5s** frequently show blow-off tops with massive retail FOMO

### 6.3 24/7 Trading

Crypto trades around the clock, every day:
- No gaps from market closures
- Wave structures develop continuously
- Ideal for always-on AI monitoring systems

### 6.4 Key Crypto Considerations

| Factor | Impact on Elliott Wave |
|---|---|
| BTC dominance cycles | Supercycle degree waves visible |
| Altcoin correlation to BTC | BTC wave count often dictates altcoin direction |
| DeFi/NFT narrative cycles | Produce distinct impulse waves in specific tokens |
| Exchange liquidation cascades | Accelerate Wave C completions |
| Halving cycles (BTC) | Align with Cycle/Supercycle degree waves |
| Extreme retail participation | Wave 5 blow-offs are more extreme than in Forex |

### 6.5 Crypto-Specific Wave Tendencies

| Wave | Forex Typical Behavior | Crypto Typical Behavior |
|---|---|---|
| Wave 1 | Moderate, often missed | Can be explosive (new narrative) |
| Wave 2 | 50%--61.8% retracement | 61.8%--78.6% retracement (deeper fear) |
| Wave 3 | 161.8%--200% extension | 200%--423.6% extension (euphoria) |
| Wave 4 | 38.2% retracement | 38.2%--50% retracement |
| Wave 5 | Often equal to Wave 1 | Often extended (FOMO-driven) |
| Wave A | Sharp but controlled | Flash crash dynamics |
| Wave B | 50%--78.6% of Wave A | Can exceed Wave 5 high (irregular B) |
| Wave C | Measured, 100%--161.8% of A | 100%--261.8% of A (capitulation) |

---

## 7. Strengths for Algorithmic Implementation

### 7.1 Rule-Based Structure

Elliott Wave Theory has **three inviolable rules** (Iron Rules) that provide clear validation criteria for any proposed wave count:

1. **Wave 2 cannot retrace more than 100% of Wave 1**
2. **Wave 3 cannot be the shortest of Waves 1, 3, and 5**
3. **Wave 4 cannot enter the price territory of Wave 1** (except in diagonal triangles)

These rules are binary (true/false) and can be programmatically enforced with zero ambiguity.

### 7.2 Fibonacci-Based Price Targets

Each wave has mathematically defined target zones based on Fibonacci ratios. This allows an AI system to:
- **Calculate precise entry points** (e.g., buy at the 61.8% retracement of Wave 1 for Wave 2 completion)
- **Set exact take-profit levels** (e.g., Wave 3 target at 161.8% extension of Wave 1)
- **Define invalidation levels** (e.g., if Wave 2 retraces beyond 100%, the count is invalid)

### 7.3 Multi-Timeframe Confirmation

The fractal nature allows the AI to:
- Confirm higher-timeframe wave counts with lower-timeframe subdivisions
- Use degree alignment as a confidence multiplier
- Identify high-probability trades where multiple degrees align

### 7.4 Defined Risk Parameters

Every wave position has a clear invalidation level:

| Position | Stop Loss (Invalidation) | Risk Definition |
|---|---|---|
| Long at Wave 2 bottom | Below start of Wave 1 | 100% of Wave 1 range |
| Long at Wave 4 bottom | Below end of Wave 1 (non-overlap rule) | Wave 4 to Wave 1 range |
| Short at Wave 5 top | Above 161.8% extension of Wave 3 | Depends on wave degree |
| Short at Wave B top | Above Wave 5 terminus | Defined by pattern type |

### 7.5 Probabilistic Framework

Elliott Wave provides a **ranked set of likely outcomes** (preferred count vs. alternate counts), which maps naturally to:
- Bayesian probability frameworks
- Decision trees with weighted branches
- Monte Carlo simulation of possible wave paths

---

## 8. Limitations and Challenges

### 8.1 Subjectivity in Wave Counting

The single greatest challenge: **two skilled analysts can produce different wave counts from the same chart**. This manifests as:

- Ambiguity in identifying the starting point of a wave sequence
- Difficulty distinguishing between corrective patterns in real-time
- Multiple valid wave counts that satisfy all rules but imply different future paths

**Mitigation for AI:** Maintain multiple concurrent wave counts with probability weightings. Update probabilities as new price data arrives (Bayesian updating).

### 8.2 Real-Time vs. Hindsight Analysis

Elliott Wave analysis is significantly easier in hindsight. In real-time:
- The current wave may not be identifiable until it is nearly complete
- Complex corrections can take many forms, and the final form is only clear after completion
- Wave extensions can continue far beyond initial targets

**Mitigation for AI:** Use confirmation signals (volume, momentum divergence, Fibonacci cluster confluence) before committing to a wave interpretation.

### 8.3 Failure Modes

| Failure Mode | Description | Frequency |
|---|---|---|
| Truncated Wave 5 | Wave 5 fails to exceed Wave 3's extreme | Uncommon but significant |
| Extended corrections | Corrections take much longer than expected | Common in ranging markets |
| Wave overlap in leveraged markets | High leverage can cause transient violations | Occasional in Crypto |
| Diagonal triangles | Overlap rules are relaxed, causing confusion | Periodic at trend ends |
| Nested corrections | WXY or WXYXZ patterns that seem to never end | Common in Wave 4 of large degree |

### 8.4 Not a Standalone System

Elliott Wave Theory should **never** be used in isolation. It must be combined with:
- Volume analysis (confirms wave identity)
- Momentum indicators (RSI, MACD divergence for Wave 5)
- Support/Resistance (validates Fibonacci levels)
- Order flow analysis (institutional footprint)
- Sentiment indicators (extreme readings at wave terminals)

### 8.5 Computational Complexity

Automated wave counting is computationally expensive:
- The number of possible wave labelings grows exponentially with the number of pivot points
- Real-time re-evaluation requires efficient algorithms
- Multiple timeframe alignment multiplies the computation

**Mitigation:** Use hierarchical top-down approach (start from highest timeframe, constrain lower timeframe counts) and pruning rules based on the three iron rules.

---

## 9. Integration with Multi-Agent Architecture

### 9.1 Agent Roles

In our Multi-Agent AI Trading System, Elliott Wave analysis should be distributed across specialized agents:

| Agent | Role | Elliott Wave Function |
|---|---|---|
| **Wave Counter Agent** | Primary analysis | Identifies current wave position across multiple timeframes |
| **Fibonacci Agent** | Target calculation | Computes price targets, clusters, and invalidation levels |
| **Confirmation Agent** | Signal validation | Cross-references wave count with volume, momentum, sentiment |
| **Risk Agent** | Position sizing | Calculates stop loss, take profit, and position size based on wave context |
| **Execution Agent** | Order management | Executes entries/exits based on wave-derived signals |
| **Supervisor Agent** | Orchestration | Resolves conflicts between wave counts and other strategy signals |

### 9.2 Data Flow

```
Market Data Stream
       │
       ▼
┌──────────────────┐
│  Wave Counter     │──── Identifies current wave position
│  Agent            │     (preferred + alternate counts)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Fibonacci        │──── Calculates targets and invalidation
│  Agent            │     levels for each wave scenario
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Confirmation     │──── Validates with volume, RSI, MACD,
│  Agent            │     sentiment, order flow
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Risk Agent       │──── Position sizing, SL/TP, RR ratio
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Execution Agent  │──── Order placement and management
└──────────────────┘
```

### 9.3 Knowledge Base Dependencies

This Elliott Wave module depends on and interacts with:

| Module | Interaction |
|---|---|
| `03_order_flow_liquidity` | Validates wave identity via institutional order flow |
| `04_smart_money_concepts` | SMC liquidity sweeps often mark wave terminals |
| `05_supply_demand_zones` | S/D zones that align with Fibonacci levels increase confidence |
| `06_harmonic_patterns` | Harmonic completions can coincide with wave completions |
| `07_price_action` | Candlestick patterns confirm wave reversals |
| `08_volume_profile_analysis` | Volume profiles validate wave character |
| `11_multi_timeframe_analysis` | Essential for fractal wave degree alignment |
| `12_fibonacci_advanced` | Extended Fibonacci techniques for precise targeting |

---

## 10. Core Logic --- Entry/Exit Framework

### 10.1 Primary Trading Setups

Elliott Wave Theory produces several high-probability trading setups:

**Setup 1: Wave 2 Completion (Trend Continuation)**
```
Condition: Wave 1 identified; Wave 2 retraces to 50%-61.8% of Wave 1
Entry:     Long at Wave 2 completion (Fibonacci confluence + reversal signal)
Stop Loss: Below Wave 1 origin (Wave 2 > 100% invalidation)
Target:    Wave 3 = 161.8% extension of Wave 1
RR Ratio:  Typically 3:1 to 5:1
```

**Setup 2: Wave 3 Continuation (Momentum)**
```
Condition: Wave 3 confirmed in progress (break above Wave 1 terminus)
Entry:     Long on pullback within Wave 3 (sub-wave ii or iv)
Stop Loss: Below the most recent sub-wave low
Target:    Wave 3 terminus (161.8%-261.8% of Wave 1)
RR Ratio:  Typically 2:1 to 4:1
```

**Setup 3: Wave 4 Completion (Late Trend Entry)**
```
Condition: Wave 3 complete; Wave 4 retraces to 38.2% of Wave 3
Entry:     Long at Wave 4 completion
Stop Loss: Below Wave 1 terminus (non-overlap rule)
Target:    Wave 5 = 61.8%-100% of Wave 1 (from Wave 4 terminus)
RR Ratio:  Typically 2:1 to 3:1
```

**Setup 4: Wave 5 Completion (Counter-Trend)**
```
Condition: Five-wave impulse complete (divergence on RSI/MACD)
Entry:     Short at Wave 5 completion
Stop Loss: Above 161.8% extension of Wave 3 (or above diagonal upper bound)
Target:    Wave A = 38.2%-61.8% retracement of entire impulse
RR Ratio:  Typically 2:1 to 3:1
```

**Setup 5: Wave C Completion (Trend Resumption)**
```
Condition: ABC correction complete at key Fibonacci level
Entry:     Long at Wave C terminus (if larger trend is up)
Stop Loss: Below the next significant Fibonacci level
Target:    New impulse Wave 1 of higher degree
RR Ratio:  Typically 3:1 to 5:1+
```

### 10.2 Entry Confirmation Checklist

Before entering any Elliott Wave trade, the AI system must verify:

- [ ] Wave count satisfies all three iron rules
- [ ] Fibonacci level confluence (at least 2 Fibonacci relationships aligning)
- [ ] Volume confirms wave identity (Wave 3 highest volume, Wave 5 divergence)
- [ ] Momentum indicator confirmation (RSI divergence, MACD crossover)
- [ ] Higher timeframe wave count alignment
- [ ] Price action confirmation (reversal candlestick pattern at wave terminal)
- [ ] Risk-to-reward ratio >= 2:1

---

## 11. Technical Specifications

### 11.1 Data Requirements

| Data Type | Minimum Requirement | Preferred |
|---|---|---|
| OHLCV candles | 200 candles per timeframe | 500+ candles |
| Timeframes | At least 3 (e.g., 4H, 1H, 15M) | 5+ timeframes |
| Tick data | Not required | Helpful for sub-minute wave counting |
| Volume | Required for confirmation | Essential for Wave 3/5 identification |
| Order book | Optional | Strongly recommended for crypto |

### 11.2 Indicator Dependencies

| Indicator | Purpose | Parameters |
|---|---|---|
| ZigZag | Pivot detection for wave counting | Threshold: 3%-5% (Forex), 5%-10% (Crypto) |
| RSI(14) | Divergence detection for Wave 5 | Standard 14-period |
| MACD(12,26,9) | Momentum confirmation | Standard parameters |
| Volume MA(20) | Volume trend for wave confirmation | 20-period SMA |
| ATR(14) | Volatility for SL calculation | 14-period |
| Fibonacci Retracement | Target calculation | Auto-drawn on identified waves |
| Fibonacci Extension | Projection calculation | Auto-drawn on identified waves |

### 11.3 Wave Detection Parameters

```python
# Configuration for Elliott Wave detection
EW_CONFIG = {
    "zigzag_threshold_forex": 0.03,       # 3% minimum swing for Forex
    "zigzag_threshold_crypto": 0.05,       # 5% minimum swing for Crypto
    "min_wave_bars": 5,                     # Minimum bars per wave
    "max_wave_bars_ratio": 10,              # Max Wave_n bars / Min Wave_n bars
    "fibonacci_tolerance": 0.02,            # 2% tolerance for Fibonacci levels
    "volume_confirmation_threshold": 1.5,   # Wave 3 volume >= 1.5x average
    "rsi_divergence_lookback": 14,          # RSI lookback for divergence
    "min_confidence_score": 0.65,           # Minimum confidence for trade signal
    "max_alternate_counts": 3,              # Track up to 3 alternate counts
    "timeframes": ["1M", "1W", "1D", "4H", "1H", "15M"],
}
```

---

## 12. Mathematical Foundation

### 12.1 Wave Measurement Formulas

**Price Range of a Wave:**

$$\text{Range}_n = |P_{\text{end}}^{(n)} - P_{\text{start}}^{(n)}|$$

where $P_{\text{start}}^{(n)}$ and $P_{\text{end}}^{(n)}$ are the starting and ending prices of wave $n$.

**Fibonacci Retracement Level:**

$$P_{\text{retrace}} = P_{\text{end}}^{(n)} - r \times \text{Range}_n \quad \text{(for bullish wave } n\text{)}$$

$$P_{\text{retrace}} = P_{\text{end}}^{(n)} + r \times \text{Range}_n \quad \text{(for bearish wave } n\text{)}$$

where $r \in \{0.236, 0.382, 0.500, 0.618, 0.786\}$.

**Fibonacci Extension Level:**

$$P_{\text{extension}} = P_{\text{end}}^{(2)} + e \times \text{Range}_1 \quad \text{(for Wave 3 target in uptrend)}$$

where $e \in \{1.000, 1.272, 1.618, 2.000, 2.618, 4.236\}$.

### 12.2 Wave Ratio Validation

For a valid impulse wave:

$$\frac{\text{Range}_3}{\text{Range}_1} \geq 1.0 \quad \text{and} \quad \frac{\text{Range}_3}{\text{Range}_5} \geq 1.0 \quad \text{(Wave 3 not shortest)}$$

$$P_{\text{end}}^{(2)} \neq P_{\text{start}}^{(1)} \quad \text{and} \quad \frac{|P_{\text{end}}^{(2)} - P_{\text{end}}^{(1)}|}{|P_{\text{end}}^{(1)} - P_{\text{start}}^{(1)}|} < 1.0$$

$$P_{\text{end}}^{(4)} > P_{\text{end}}^{(1)} \quad \text{(in uptrend, Wave 4 stays above Wave 1 terminus)}$$

### 12.3 Confidence Score

$$C_{\text{wave}} = w_1 \cdot F_{\text{fib}} + w_2 \cdot F_{\text{vol}} + w_3 \cdot F_{\text{mom}} + w_4 \cdot F_{\text{struct}} + w_5 \cdot F_{\text{time}}$$

where:
- $F_{\text{fib}}$ = Fibonacci alignment score (0--1)
- $F_{\text{vol}}$ = Volume confirmation score (0--1)
- $F_{\text{mom}}$ = Momentum confirmation score (0--1)
- $F_{\text{struct}}$ = Structural validity score (rules satisfied) (0--1)
- $F_{\text{time}}$ = Time proportionality score (0--1)
- $w_1 + w_2 + w_3 + w_4 + w_5 = 1.0$

Recommended weights:

| Weight | Value | Rationale |
|---|---|---|
| $w_1$ (Fibonacci) | 0.30 | Core mathematical foundation |
| $w_2$ (Volume) | 0.20 | Essential for wave identity |
| $w_3$ (Momentum) | 0.15 | Confirms wave phase |
| $w_4$ (Structure) | 0.25 | Rules compliance is critical |
| $w_5$ (Time) | 0.10 | Less reliable but informative |

---

## 13. Risk Parameters

### 13.1 Position Sizing Formula

$$\text{Position Size} = \frac{\text{Account Balance} \times \text{Risk Per Trade}}{\text{Stop Loss Distance (in pips)} \times \text{Pip Value}}$$

For Elliott Wave trades, risk per trade should be adjusted by confidence:

$$\text{Adjusted Risk} = \text{Base Risk} \times C_{\text{wave}}$$

where:
- Base Risk = 1%--2% of account balance (standard)
- $C_{\text{wave}}$ = confidence score (0.65--1.0)

### 13.2 Stop Loss Placement

| Wave Position | Stop Loss Level | Logic |
|---|---|---|
| Long at Wave 2 end | Below Wave 1 origin | Wave 2 > 100% invalidation |
| Long at Wave 4 end | Below Wave 1 terminus | Wave 4 overlap invalidation |
| Short at Wave 5 end | Above Wave 3 x 1.618 from Wave 2 | Extended Wave 5 invalidation |
| Long at Wave C end | Below next Fibonacci cluster | Pattern invalidation |

### 13.3 Take Profit Levels

Use scaled exits:
- **TP1** (40% of position): Conservative Fibonacci target
- **TP2** (35% of position): Standard Fibonacci target
- **TP3** (25% of position): Extended Fibonacci target (trailing stop)

### 13.4 Risk-to-Reward Minimums

| Setup | Minimum RR | Preferred RR |
|---|---|---|
| Wave 2 completion entry | 3:1 | 5:1 |
| Wave 3 continuation | 2:1 | 3:1 |
| Wave 4 completion entry | 2:1 | 3:1 |
| Wave 5 reversal | 2:1 | 3:1 |
| Wave C completion | 3:1 | 5:1 |

---

## 14. Execution Flow

### 14.1 High-Level Algorithm

```
FUNCTION analyze_elliott_wave(market_data, timeframes):
    
    // Step 1: Multi-timeframe pivot detection
    FOR EACH timeframe IN timeframes (highest to lowest):
        pivots[timeframe] = detect_pivots(market_data[timeframe])
    
    // Step 2: Generate wave counts
    FOR EACH timeframe IN timeframes (highest to lowest):
        wave_counts[timeframe] = generate_wave_counts(pivots[timeframe])
        validate_iron_rules(wave_counts[timeframe])
        score_wave_counts(wave_counts[timeframe])
    
    // Step 3: Align across timeframes
    aligned_counts = align_timeframes(wave_counts)
    
    // Step 4: Identify trading opportunities
    setups = identify_setups(aligned_counts)
    
    // Step 5: Calculate targets and risk
    FOR EACH setup IN setups:
        setup.targets = calculate_fibonacci_targets(setup)
        setup.stop_loss = calculate_stop_loss(setup)
        setup.rr_ratio = setup.targets / setup.stop_loss
        setup.position_size = calculate_position_size(setup)
    
    // Step 6: Filter and rank
    valid_setups = FILTER setups WHERE rr_ratio >= 2.0 AND confidence >= 0.65
    ranked_setups = SORT valid_setups BY (confidence * rr_ratio) DESC
    
    RETURN ranked_setups
```

### 14.2 Decision Tree

```
START
  │
  ├── Is there a valid 5-wave impulse on HTF?
  │     ├── YES → Which wave are we currently in?
  │     │     ├── Wave 2 in progress → Monitor for completion at 50%-61.8%
  │     │     ├── Wave 3 in progress → Look for continuation entries on LTF
  │     │     ├── Wave 4 in progress → Monitor for completion at 38.2%
  │     │     ├── Wave 5 in progress → Prepare for reversal setup
  │     │     └── Wave 5 complete → Enter correction trade (short/long)
  │     │
  │     └── NO → Is there a valid corrective pattern?
  │           ├── YES → Which correction type?
  │           │     ├── Zigzag → Trade the C wave
  │           │     ├── Flat → Trade the C wave breakout
  │           │     ├── Triangle → Trade the thrust after completion
  │           │     └── Complex → Wait for clarity
  │           │
  │           └── NO → WAIT (no clear wave structure)
  │
  └── WAIT for clear structure to develop
```

---

## 15. References

### 15.1 Primary Sources

1. **Elliott, R.N.** (1938). *The Wave Principle*. New York.
2. **Elliott, R.N.** (1946). *Nature's Law: The Secret of the Universe*. New York.
3. **Frost, A.J. & Prechter, R.R.** (1978). *Elliott Wave Principle: Key to Market Behavior*. New Classics Library. (11th Edition, 2017)
4. **Prechter, R.R.** (1999). *The Wave Principle of Human Social Behavior and the New Science of Socionomics*. New Classics Library.
5. **Neely, G.** (1988). *Mastering Elliott Wave*. Windsor Books.

### 15.2 Secondary Sources

6. **Poser, S.W.** (2003). *Applying Elliott Wave Theory Profitably*. Wiley Trading.
7. **Miner, R.C.** (2009). *High Probability Trading Strategies*. Wiley.
8. **Balan, R.** (1989). *Elliott Wave Principle Applied to the Foreign Exchange Markets*. BBS Publications.
9. **Bulkowski, T.N.** (2005). *Encyclopedia of Chart Patterns*. Wiley. (Chapter on Elliott Wave)
10. **Murphy, J.J.** (1999). *Technical Analysis of the Financial Markets*. New York Institute of Finance.

### 15.3 Academic Papers

11. **Mandelbrot, B.** (1963). "The Variation of Certain Speculative Prices." *The Journal of Business*, 36(4), 394--419.
12. **Lo, A.W.** (2004). "The Adaptive Markets Hypothesis." *Journal of Portfolio Management*, 30(5), 15--29.
13. **Shiller, R.J.** (2000). *Irrational Exuberance*. Princeton University Press.
14. **Cont, R.** (2001). "Empirical Properties of Asset Returns: Stylized Facts and Statistical Issues." *Quantitative Finance*, 1, 223--236.

### 15.4 Online Resources

15. Elliott Wave International (www.elliottwave.com) --- Educational materials and market analysis
16. TradingView Elliott Wave community --- Crowd-sourced wave counts for validation
17. Fibonacci and Elliott Wave resources at Investopedia

---

## Document Cross-References

| Document | Path | Relationship |
|---|---|---|
| Impulse Waves | `01_impulse_waves.md` | Detailed motive wave patterns |
| Corrective Waves | `02_corrective_waves.md` | Detailed corrective wave patterns |
| Fibonacci Targets | `03_fibonacci_targets.md` | Price target calculations |
| Wave Counting Algorithm | `04_wave_counting_algorithm.md` | Automated counting logic |
| Fibonacci Advanced | `../12_fibonacci_advanced/` | Extended Fibonacci techniques |
| Multi-Timeframe Analysis | `../11_multi_timeframe_analysis/` | HTF/LTF alignment methods |
| Smart Money Concepts | `../04_smart_money_concepts/` | Institutional behavior at wave terminals |

---

*This document is part of the Multi-Agent AI Trading System Knowledge Base. It provides the foundational overview for Elliott Wave Theory implementation. Refer to companion documents for detailed wave patterns, Fibonacci analysis, and algorithmic implementation.*
