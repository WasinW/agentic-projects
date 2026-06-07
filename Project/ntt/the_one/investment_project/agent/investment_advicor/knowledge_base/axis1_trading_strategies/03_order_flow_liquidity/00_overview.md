# Order Flow & Liquidity Analysis — Overview

> **Axis 1 — Trading Strategies | Module 03 — Order Flow & Liquidity**
> Version: 2.0 | Last Updated: 2026-04-12
> Classification: Core Knowledge Base — Multi-Agent AI Trading System

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Market Microstructure Fundamentals](#2-market-microstructure-fundamentals)
3. [How Orders Create Price Movement](#3-how-orders-create-price-movement)
4. [Bid/Ask Dynamics](#4-bidask-dynamics)
5. [Maker vs Taker Model](#5-maker-vs-taker-model)
6. [Why Order Flow Matters for Algorithmic Trading](#6-why-order-flow-matters-for-algorithmic-trading)
7. [Core Logic — Entry/Exit Framework](#7-core-logic--entryexit-framework)
8. [Technical Specifications](#8-technical-specifications)
9. [Mathematical Models](#9-mathematical-models)
10. [Risk Parameters](#10-risk-parameters)
11. [Execution Flow](#11-execution-flow)
12. [Cross-Module Integration](#12-cross-module-integration)
13. [References](#13-references)

---

## 1. Introduction

Order Flow Analysis is the study of the actual transactions occurring in the market — the raw buy and sell orders that drive price. Unlike lagging indicators derived from price (moving averages, RSI, MACD), order flow provides a **leading** view of market intent by examining the mechanics of supply and demand at the most granular level.

Liquidity Analysis complements order flow by identifying **where** large pools of resting orders sit in the market. These pools act as magnets for price, as institutional participants require sufficient liquidity to fill their large positions without excessive slippage.

### 1.1 Why This Module Exists

Traditional technical analysis treats price as the primary data source. This is fundamentally backwards. Price is the **output** of order flow — it is the result, not the cause. By studying order flow directly, our trading system gains:

- **Anticipatory signals**: Detect institutional intent before price moves
- **Precision entries**: Enter at optimal liquidity zones rather than arbitrary support/resistance
- **Reduced false signals**: Filter out noise by confirming moves with actual transaction data
- **Institutional alignment**: Trade with smart money rather than against it

### 1.2 Scope of This Module

This module covers six interconnected documents:

| Document | Focus | Primary Data Source |
|----------|-------|-------------------|
| `00_overview.md` | Foundational concepts | Conceptual framework |
| `01_order_book_analysis.md` | Level 2 data, order book dynamics | L2 market depth, DOM |
| `02_liquidity_concepts.md` | Liquidity pools, FVGs, ICT concepts | Price action + volume |
| `03_hft_stop_hunting.md` | Institutional manipulation patterns | Tick data, time-of-day |
| `04_volume_delta_analysis.md` | Volume delta, CVD, VWAP, volume profile | Trade data (Time & Sales) |
| `05_execution_flow.md` | Complete implementation pipeline | All data sources |

### 1.3 Market Applicability

| Market | Order Flow Data Quality | L2 Data Available | Key Considerations |
|--------|------------------------|-------------------|-------------------|
| **Forex (Spot)** | Moderate — decentralized OTC | Limited (ECN/broker-specific) | Use aggregated feeds; no true central order book |
| **Forex (Futures)** | Excellent — CME centralized | Full DOM available | CME FX futures as proxy for spot |
| **Crypto (CEX)** | Good — exchange-specific | Full order book via API | Fragmented across exchanges; wash trading concerns |
| **Crypto (DEX)** | Moderate — on-chain | AMM liquidity pools | Different microstructure (constant product AMM) |

---

## 2. Market Microstructure Fundamentals

Market microstructure is the academic field studying the process and outcomes of exchanging assets under a specific set of rules. It examines how latent demands from investors are ultimately translated into prices and volumes.

### 2.1 The Price Discovery Process

Price discovery is the continuous process through which buyer and seller interactions determine the market price of an asset. This process occurs through the **matching engine** — the core component of any exchange.

```
                    ┌─────────────────────┐
                    │   MATCHING ENGINE    │
                    │                     │
  Buy Orders ──────►  Price-Time Priority ◄────── Sell Orders
  (Bids)           │                     │        (Asks/Offers)
                    │  ┌───────────────┐  │
                    │  │ Trade Output  │  │
                    │  │ Price: P      │  │
                    │  │ Volume: V     │  │
                    │  │ Time: T       │  │
                    │  │ Aggressor: B/S│  │
                    │  └───────────────┘  │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   PRICE UPDATE       │
                    │   Last: P           │
                    │   Bid: P_bid        │
                    │   Ask: P_ask        │
                    └─────────────────────┘
```

### 2.2 Order Types and Their Market Impact

#### 2.2.1 Market Orders
- **Definition**: An order to buy or sell immediately at the best available price
- **Impact**: Removes liquidity from the order book; creates immediate price impact
- **Signal**: Represents urgency — the trader is willing to cross the spread
- **Aggression**: Market buys hit the ask; market sells hit the bid

#### 2.2.2 Limit Orders
- **Definition**: An order to buy or sell at a specified price or better
- **Impact**: Adds liquidity to the order book; creates depth at specific price levels
- **Signal**: Represents patience — the trader is willing to wait for their price
- **Role**: Acts as a buffer against price movement (passive liquidity)

#### 2.2.3 Stop Orders
- **Definition**: An order that becomes a market order when a specified price is reached
- **Impact**: Creates cascading liquidity events when triggered
- **Signal**: Represents risk management — but also a source of liquidity for institutions
- **Vulnerability**: Stop clusters are visible to sophisticated participants and become targets

#### 2.2.4 Iceberg Orders (Hidden Orders)
- **Definition**: A large order that is broken into smaller visible portions
- **Impact**: Disguises true order size; only shows a fraction of total quantity
- **Detection**: Repeated refilling at the same price level after partial fills
- **Signal**: Institutional accumulation or distribution without revealing intent

#### 2.2.5 Fill-or-Kill (FOK) and Immediate-or-Cancel (IOC)
- **FOK**: Execute the entire order immediately or cancel it entirely
- **IOC**: Execute any portion immediately, cancel the remainder
- **Signal**: Used by algorithms seeking specific fill conditions

### 2.3 The Continuous Limit Order Book (CLOB)

The CLOB is the standard model for centralized exchanges (stocks, futures, centralized crypto exchanges). Understanding its structure is fundamental to order flow analysis.

```
Price Level    │ Bid Size │ Ask Size │
───────────────┼──────────┼──────────┤
  1.1055       │          │   250    │  ◄── Best Ask (Inside Ask)
  1.1054       │          │   180    │
  1.1053       │          │   420    │
  1.1052       │          │   95     │
───────────────┼──────────┼──────────┤  ◄── Spread = 1.1052 - 1.1050 = 0.0002
  1.1050       │   310    │          │  ◄── Best Bid (Inside Bid)
  1.1049       │   175    │          │
  1.1048       │   560    │          │
  1.1047       │   220    │          │
───────────────┼──────────┼──────────┤
               │  DEPTH   │  DEPTH   │
```

**Key Metrics from the CLOB:**

| Metric | Formula | Interpretation |
|--------|---------|---------------|
| Mid Price | $(P_{ask} + P_{bid}) / 2$ | Fair value estimate |
| Spread | $P_{ask} - P_{bid}$ | Cost of immediacy |
| Relative Spread | $(P_{ask} - P_{bid}) / P_{mid}$ | Normalized liquidity measure |
| Depth at Best | $Q_{bid}^{(1)} + Q_{ask}^{(1)}$ | Immediate liquidity |
| Total Depth | $\sum Q_{bid} + \sum Q_{ask}$ | Overall market liquidity |

### 2.4 Decentralized Forex Market Structure

Unlike centralized exchanges, the spot Forex market operates as an over-the-counter (OTC) network:

```
           ┌────────────────────────────────────────────┐
           │         INTERBANK MARKET (Tier 1)          │
           │  Deutsche Bank, JPMorgan, Citi, UBS, etc.  │
           │  Average deal size: $5M-$100M+             │
           └─────────────┬──────────────────────────────┘
                         │
           ┌─────────────▼──────────────────────────────┐
           │         ECN / AGGREGATORS (Tier 2)          │
           │  EBS, Reuters Matching, Currenex, Hotspot   │
           │  Aggregate multiple LP quotes               │
           └─────────────┬──────────────────────────────┘
                         │
           ┌─────────────▼──────────────────────────────┐
           │     PRIME BROKERS / PRIME OF PRIME (Tier 3) │
           │  Access to aggregated liquidity             │
           └─────────────┬──────────────────────────────┘
                         │
           ┌─────────────▼──────────────────────────────┐
           │         RETAIL BROKERS (Tier 4)             │
           │  Market Makers or STP/ECN models            │
           │  Often internalize retail flow              │
           └────────────────────────────────────────────┘
```

**Implications for Order Flow Analysis in Forex:**
- No single "true" order book — each venue has its own
- CME FX futures serve as the best proxy for centralized order flow
- Retail broker data is limited and potentially skewed (dealer model)
- Institutional flow is inferred from footprint charts and volume delta

### 2.5 Crypto Market Structure

Cryptocurrency markets blend centralized and decentralized elements:

```
       ┌──────────────────┐    ┌──────────────────┐
       │   CEX (Binance,  │    │  DEX (Uniswap,   │
       │   Coinbase, OKX) │    │  dYdX, GMX)      │
       │                  │    │                  │
       │  CLOB Model      │    │  AMM Model       │
       │  Maker/Taker fees│    │  LP Pool Model   │
       │  Full L2 data    │    │  On-chain data   │
       └────────┬─────────┘    └────────┬─────────┘
                │                       │
                ▼                       ▼
       ┌────────────────────────────────────────┐
       │        ARBITRAGEURS & MARKET MAKERS     │
       │   Bridge pricing across venues          │
       │   Keep prices aligned cross-exchange    │
       └────────────────────────────────────────┘
```

**Key Differences from Traditional Markets:**
- 24/7 trading — no session opens/closes (but still cyclical liquidity patterns)
- Fragmented liquidity across dozens of exchanges
- Wash trading inflates volume on some exchanges by 50-90% (Bitwise, 2019)
- On-chain data provides unique transparency (whale wallets, DEX flows)
- Funding rates in perpetual swaps provide additional order flow signals

---

## 3. How Orders Create Price Movement

### 3.1 The Fundamental Mechanism

Price moves when **aggressive orders** consume available liquidity at a price level. This is the single most important concept in order flow analysis.

```
STATE 1: Equilibrium
Ask: 100 @ 1.1052
Bid: 150 @ 1.1050
→ Mid = 1.10510, Spread = 0.0002

STATE 2: Aggressive Buy (Market Buy 100 lots)
The 100 lot market buy LIFTS the entire ask at 1.1052
Ask: (now) 250 @ 1.1053  [new best ask]
Bid: 150 @ 1.1050         [unchanged]
→ Mid = 1.10515, Price moved UP by 0.0001

STATE 3: Chain Reaction
If more aggressive buying follows:
  - Consecutive ask levels get consumed
  - Bid-side limit orders get placed higher (chase)
  - Stop losses above old highs get triggered (more buying)
  - RESULT: Impulsive price move upward
```

### 3.2 Aggressive vs Passive Flow

| Characteristic | Aggressive (Market Orders) | Passive (Limit Orders) |
|---------------|---------------------------|----------------------|
| **Action** | Crosses the spread to execute | Waits at a price level |
| **Removes/Adds Liquidity** | Removes | Adds |
| **Urgency** | High — wants immediate fill | Low — willing to wait |
| **Information** | Often informed (directional intent) | Often uninformed (market making) |
| **Fee Structure** | Pays taker fee | Receives maker rebate |
| **Impact on Price** | Direct — causes price movement | Indirect — absorbs movement |

### 3.3 The Three Ways Price Can Move

**Move Type 1: Liquidity Consumption (Aggressive Orders)**
- Large market orders eat through multiple price levels
- Creates rapid, impulsive price movement
- Often seen at key levels (breakouts, stop runs)
- Signature: Large delta, high volume, thin post-move order book

**Move Type 2: Liquidity Withdrawal (Passive Order Cancellation)**
- Market makers pull their limit orders from one side
- Creates a "vacuum" — price falls into the void
- Often precedes news events or during high uncertainty
- Signature: Thinning order book, widening spread, low volume move

**Move Type 3: Liquidity Shift (Passive Order Migration)**
- Limit orders shift from one price level to another
- Gradual repricing of fair value
- Common during trending markets
- Signature: Order book slope change, steady mid-price drift

### 3.4 Order Flow Imbalance and Price Impact

The relationship between order flow imbalance and price change follows a concave (square-root) function, as established by empirical research:

$$\Delta P \approx \sigma \cdot \sqrt{\frac{Q}{V_{daily}}} \cdot \text{sign}(Q)$$

Where:
- $\Delta P$ = Expected price impact
- $\sigma$ = Daily volatility
- $Q$ = Order size
- $V_{daily}$ = Average daily volume

This square-root law (Bouchaud et al., 2009) implies:
- Doubling order size does NOT double price impact
- Impact grows as the square root of size
- Large orders must be broken up (TWAP, VWAP algorithms) to minimize impact

### 3.5 Information Flow Model (Kyle, 1985)

Kyle's seminal model describes how informed traders interact with noise traders and a market maker:

$$p_t = \mu + \lambda \cdot (x_t + u_t) + \epsilon_t$$

Where:
- $p_t$ = Market price at time $t$
- $\mu$ = Fundamental value
- $\lambda$ = Kyle's lambda (price impact coefficient)
- $x_t$ = Informed trader's order flow
- $u_t$ = Noise trader's order flow
- $\epsilon_t$ = Noise term

**Kyle's Lambda ($\lambda$)** is a key measure of market quality:
- High $\lambda$ = High price impact per unit of order flow (illiquid market)
- Low $\lambda$ = Low price impact per unit of order flow (liquid market)

For our trading system, estimating $\lambda$ in real-time provides a dynamic measure of market liquidity and information asymmetry.

---

## 4. Bid/Ask Dynamics

### 4.1 The Spread as a Measure of Market Quality

The bid-ask spread exists because of three components (Stoll, 1989):

$$S = S_{inventory} + S_{adverse} + S_{processing}$$

| Component | Description | Typical Proportion |
|-----------|-------------|-------------------|
| $S_{inventory}$ | Compensation for holding inventory risk | 20-40% |
| $S_{adverse}$ | Protection against informed traders | 40-60% |
| $S_{processing}$ | Order processing costs | 10-20% |

### 4.2 Spread Dynamics in Forex

Forex spreads are dynamic and vary by:

**Currency Pair Liquidity Tiers:**

| Tier | Pairs | Typical Spread (pips) | Daily Volume |
|------|-------|----------------------|-------------|
| Tier 1 (Major) | EUR/USD, USD/JPY | 0.1-0.5 | $500B+ |
| Tier 2 (Major) | GBP/USD, AUD/USD | 0.3-1.0 | $100-500B |
| Tier 3 (Cross) | EUR/GBP, EUR/JPY | 0.5-2.0 | $50-100B |
| Tier 4 (Exotic) | USD/TRY, USD/ZAR | 3.0-20.0 | <$50B |

**Spread Behavior Patterns:**
```
Spread
  │
  │  ╭─╮                                    ╭─╮
  │ ╭╯ ╰╮                                  ╭╯ ╰╮
  │╭╯   ╰╮          ╭─╮                   ╭╯   ╰╮
  ││     │╭─╮      ╭╯ ╰╮      ╭─╮        │     │
  ││     ╰╯ ╰──────╯   ╰──────╯ ╰────────╯     │
  │╰╮                                          ╭╯
  │ ╰──────────────────────────────────────────╯
  └──┬───────┬──────┬───────┬──────┬───────┬────► Time
   Asian   London  LDN/NY  New York  Asian  London
   Open    Open    Overlap  Close    Open   Open

Key observations:
- Tightest spreads during London/NY overlap
- Widest spreads during Asian session rollover
- Spike spreads at major news events
```

### 4.3 Spread Dynamics in Crypto

Crypto spreads depend heavily on:

| Factor | Impact on Spread |
|--------|-----------------|
| Exchange (Binance vs small CEX) | 10-100x difference |
| Pair (BTC/USDT vs altcoin/BTC) | 5-50x difference |
| Time of day (US hours vs Asia) | 2-5x difference |
| Volatility regime | 3-20x difference |
| Market cap of asset | Inversely correlated |

### 4.4 Bid/Ask Imbalance Signal

The bid-ask imbalance at the top of the book is a powerful short-term directional signal:

$$\text{Imbalance}_{BA} = \frac{Q_{bid}^{(1)} - Q_{ask}^{(1)}}{Q_{bid}^{(1)} + Q_{ask}^{(1)}}$$

Where:
- $Q_{bid}^{(1)}$ = Volume at best bid
- $Q_{ask}^{(1)}$ = Volume at best ask
- Range: [-1, +1]
- Positive = More bid volume (bullish pressure)
- Negative = More ask volume (bearish pressure)

**Multi-Level Weighted Imbalance:**

$$\text{WImb} = \frac{\sum_{i=1}^{n} w_i \cdot Q_{bid}^{(i)} - \sum_{i=1}^{n} w_i \cdot Q_{ask}^{(i)}}{\sum_{i=1}^{n} w_i \cdot Q_{bid}^{(i)} + \sum_{i=1}^{n} w_i \cdot Q_{ask}^{(i)}}$$

Where $w_i = e^{-\alpha \cdot i}$ (exponential decay weighting — closer levels weighted more heavily).

**Trading Signal:**
```
if WImb > +0.6:
    STRONG BUY pressure detected
    → Expect upward price movement
    → Look for long entry confirmation

if WImb < -0.6:
    STRONG SELL pressure detected
    → Expect downward price movement
    → Look for short entry confirmation

if -0.2 < WImb < +0.2:
    BALANCED book
    → No directional edge from order book
    → Wait for imbalance to develop
```

### 4.5 Bid/Ask Transition Model

A powerful microstructure signal is the **transition probability** — the likelihood that the best bid or ask moves up or down given the current state:

$$P(\text{ask\_down} | \text{large\_bid\_imbalance}) > P(\text{ask\_down} | \text{balanced})$$

This means: when there is significantly more volume on the bid side, the probability of the ask price ticking down is actually LOWER (because the bid provides support and aggressive buyers lift the ask).

---

## 5. Maker vs Taker Model

### 5.1 Definitions

| Role | Action | Fee | Order Type |
|------|--------|-----|-----------|
| **Maker** | Places a limit order that adds liquidity to the book | Rebate (negative fee) or lower fee | Limit order that doesn't immediately match |
| **Taker** | Places an order that removes liquidity from the book | Higher fee (taker fee) | Market order, or limit order that immediately matches |

### 5.2 Fee Structures

**Typical Forex (ECN) Fee Structure:**
- Commission: $3-7 per round-turn lot (100K units)
- Spread: Raw spread from LP (0.0-0.3 pips on majors)
- No explicit maker/taker distinction in most retail setups

**Typical Crypto Fee Structure (Binance, as example):**

| VIP Level | Maker Fee | Taker Fee | 30d Volume |
|-----------|-----------|-----------|------------|
| Regular | 0.10% | 0.10% | <$1M |
| VIP 1 | 0.09% | 0.10% | $1M-$5M |
| VIP 3 | 0.06% | 0.08% | $25M-$100M |
| VIP 6 | 0.02% | 0.05% | $250M-$1B |
| VIP 9 | 0.00% | 0.02% | >$4B |
| Market Maker | -0.01% | 0.03% | By application |

### 5.3 Why Maker/Taker Distinction Matters for Order Flow

The maker/taker model creates specific behavioral patterns:

**Maker Behavior (Passive Flow):**
- Provides liquidity at specific price levels
- Economically incentivized to trade against the trend (mean-reversion)
- Rapid cancellation and re-placement of orders (quote stuffing potential)
- Represents ~60-80% of visible order book in liquid markets
- Much of this volume is from HFT market makers

**Taker Behavior (Aggressive Flow):**
- Represents directional intent
- Willing to pay higher fees for immediate execution
- Signals urgency and conviction
- When institutional, often precedes sustained moves
- Key input for volume delta calculation

### 5.4 Taker Flow as the Primary Signal

For our trading system, **taker flow is the primary order flow signal** because:

1. **It reveals intent**: Someone willing to cross the spread and pay higher fees has directional conviction
2. **It causes price movement**: Only aggressive orders directly move price
3. **It is harder to fake**: While limit orders can be placed and cancelled (spoofing), executed trades are real
4. **It aggregates information**: Cumulative aggressive buying/selling reveals the net direction of informed flow

$$\text{Net Taker Flow}_t = \sum_{i \in \text{buys}} V_i - \sum_{j \in \text{sells}} V_j$$

Where buys are trades that hit the ask (buyer-initiated) and sells are trades that hit the bid (seller-initiated).

### 5.5 Trade Classification: Lee-Ready Algorithm

Since raw trade data often does not label whether a trade was buyer- or seller-initiated, we use the **Lee-Ready Algorithm** (Lee & Ready, 1991):

```
ALGORITHM: Lee-Ready Trade Classification
INPUT: Trade price P_t, Bid B_t, Ask A_t, Midpoint M_t

Step 1: Quote Test
  IF P_t > M_t:
    Classify as BUY (buyer-initiated)
  ELIF P_t < M_t:
    Classify as SELL (seller-initiated)
  ELIF P_t == M_t:
    Go to Step 2

Step 2: Tick Test (fallback)
  IF P_t > P_{t-1}:
    Classify as BUY (uptick)
  ELIF P_t < P_{t-1}:
    Classify as SELL (downtick)
  ELIF P_t == P_{t-1}:
    Use classification of previous trade

NOTE: Lee-Ready has ~85% accuracy on average.
For higher accuracy, use the BVC (Bulk Volume Classification)
method of Easley, Lopez de Prado, and O'Hara (2012).
```

### 5.6 Bulk Volume Classification (BVC)

An improved method for classifying volume as buyer- or seller-initiated:

$$V_t^{buy} = V_t \cdot \Phi\left(\frac{\Delta P_t}{\sigma_{\Delta P}}\right)$$

$$V_t^{sell} = V_t - V_t^{buy}$$

Where:
- $V_t$ = Total volume in bar $t$
- $\Delta P_t$ = Price change in bar $t$  
- $\sigma_{\Delta P}$ = Standard deviation of price changes
- $\Phi$ = Standard normal CDF

This method does not require tick-level data and works with OHLCV bars.

---

## 6. Why Order Flow Matters for Algorithmic Trading

### 6.1 Information Advantage

Order flow provides what no other indicator can: **a view of actual supply and demand in real-time**.

```
Traditional Analysis (Lagging):
  Price Action → Indicator Calculation → Signal → Decision → Execution
  [Already happened]  [Delayed]         [Late]  [Later]   [Too late?]

Order Flow Analysis (Leading/Coincident):
  Order Book State → Flow Imbalance → Signal → Decision → Execution
  [Real-time]        [Real-time]     [Early]  [Timely]   [Optimal]
```

### 6.2 Edge Categories from Order Flow

| Edge Type | Mechanism | Timeframe | Expected Alpha |
|-----------|-----------|-----------|---------------|
| **Microstructure** | Order book imbalance, spread dynamics | Seconds-Minutes | Small but consistent |
| **Absorption** | Large passive orders absorbing aggression | Minutes-Hours | Moderate |
| **Institutional Flow** | Identifying smart money accumulation/distribution | Hours-Days | High |
| **Liquidity Sweep** | Stop hunting patterns, liquidity grabs | Minutes-Hours | High |
| **Divergence** | CVD vs price divergence | Hours-Days | Moderate-High |

### 6.3 Integration with Price Action

Order flow should not be used in isolation. Our system integrates it with:

1. **Market Structure** (Module 02 — Wyckoff): Confirm accumulation/distribution phases with order flow
2. **Smart Money Concepts** (Module 04): Validate OBs and FVGs with volume delta
3. **Supply/Demand Zones** (Module 05): Confirm zone strength with order book depth
4. **Multi-Timeframe Analysis** (Module 11): Align order flow signals across timeframes

### 6.4 Data Requirements

| Data Type | Source | Use Case | Typical Format |
|-----------|--------|----------|---------------|
| **Level 1** (BBO) | Exchange feed, broker | Spread analysis, basic flow | Price, Size, Time |
| **Level 2** (Depth) | Exchange feed, DOM | Order book analysis, imbalance | Price levels + sizes |
| **Level 3** (Full book) | Direct exchange access | Complete order-by-order view | Individual order IDs |
| **Time & Sales** | Exchange trade feed | Volume delta, trade classification | Price, Size, Side, Time |
| **Tick Data** | Data vendors | Backtesting, microstructure | Every price change |

**Recommended Data Sources:**

| Market | Provider | Data Quality | Cost |
|--------|----------|-------------|------|
| Forex Futures | CME DataMine, CQG | Excellent | $$$ |
| Forex Spot | TrueFX, Dukascopy | Good | Free-$$ |
| Crypto CEX | Exchange APIs (Binance, Coinbase) | Good | Free |
| Crypto Aggregated | Kaiko, CoinAPI, Tardis.dev | Excellent | $$-$$$ |

---

## 7. Core Logic — Entry/Exit Framework

### 7.1 Order Flow Confirmation Model

Every trade signal in our system passes through an Order Flow Confirmation Layer:

```
┌──────────────────────────────────────────────────────┐
│                SIGNAL GENERATION LAYER                 │
│  (Price Action, SMC, Elliott Wave, Wyckoff, etc.)     │
└──────────────────┬───────────────────────────────────┘
                   │ Raw Signal (Long/Short/Neutral)
                   ▼
┌──────────────────────────────────────────────────────┐
│           ORDER FLOW CONFIRMATION LAYER               │
│                                                      │
│  CHECK 1: Order Book Imbalance Direction             │
│    → Does the book support the signal direction?     │
│                                                      │
│  CHECK 2: Volume Delta Confirmation                  │
│    → Is aggressive flow aligned with the signal?     │
│                                                      │
│  CHECK 3: Liquidity Map                              │
│    → Is there sufficient liquidity for the target?   │
│    → Are there liquidity pools that may act as       │
│      magnets or obstacles?                           │
│                                                      │
│  CHECK 4: Institutional Flow Detection               │
│    → Are large participants aligned with signal?     │
│                                                      │
│  RESULT: CONFIRMED / REJECTED / WAIT                 │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│              EXECUTION & RISK LAYER                   │
│  Entry price, SL, TP, Position size, Order type      │
└──────────────────────────────────────────────────────┘
```

### 7.2 Entry Conditions (Long Example)

A LONG signal is confirmed when:

```python
def confirm_long_signal(signal, order_flow_data):
    checks = {
        'book_imbalance': order_flow_data.weighted_imbalance > 0.3,
        'delta_positive': order_flow_data.cumulative_delta_slope > 0,
        'absorption_bid': order_flow_data.bid_absorption_detected,
        'no_sell_wall': order_flow_data.ask_wall_ratio < 3.0,
        'liquidity_above': order_flow_data.buy_side_liquidity_distance > min_target,
        'session_ok': is_active_session(current_time),
    }
    
    # Require at least 4 of 6 checks
    score = sum(checks.values())
    
    if score >= 5:
        return 'STRONG_CONFIRM'
    elif score >= 4:
        return 'CONFIRM'
    elif score >= 3:
        return 'WEAK_CONFIRM'
    else:
        return 'REJECT'
```

### 7.3 Exit Conditions

Order flow provides dynamic exit signals:

| Exit Signal | Condition | Action |
|-------------|-----------|--------|
| Delta Divergence | Price making new high but CVD declining | Tighten stop / partial exit |
| Absorption Flip | Large absorption appearing against position | Prepare for reversal |
| Liquidity Target Hit | Price reaches identified liquidity pool | Take profit |
| Spread Blow-out | Spread widens >3x normal | Emergency exit (liquidity crisis) |
| Volume Climax | Extreme volume spike with reversal candle | Exit position |

---

## 8. Technical Specifications

### 8.1 System Requirements

| Component | Specification |
|-----------|--------------|
| Data Feed Latency | <50ms for crypto CEX; <10ms for futures |
| Order Book Snapshot Rate | 100ms minimum; 10ms preferred |
| Trade Feed | Tick-by-tick, <20ms latency |
| Processing | Real-time streaming (Apache Kafka / Redis Streams) |
| Storage | Time-series DB (TimescaleDB / InfluxDB) |
| Backtest Data | Minimum 2 years tick data; 5 years preferred |

### 8.2 Signal Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `imbalance_threshold` | 0.4 | [0.2, 0.8] | Min weighted imbalance for signal |
| `delta_window` | 100 trades | [50, 500] | Window for cumulative delta |
| `absorption_min_size` | 3x avg | [2x, 10x] | Min size for absorption detection |
| `liquidity_pool_threshold` | 2x avg vol | [1.5x, 5x] | Min volume cluster for pool |
| `session_filter` | True | Bool | Only trade during kill zones |
| `spread_max_multiple` | 2.0 | [1.5, 5.0] | Max spread vs average |

---

## 9. Mathematical Models

### 9.1 Order Flow Toxicity: VPIN (Volume-Synchronized Probability of Informed Trading)

VPIN (Easley, Lopez de Prado, and O'Hara, 2012) measures the probability that order flow is informed (toxic):

$$\text{VPIN} = \frac{\sum_{\tau=1}^{n} |V_{\tau}^{S} - V_{\tau}^{B}|}{n \cdot V}$$

Where:
- $V_{\tau}^{S}$ = Sell volume in volume bucket $\tau$
- $V_{\tau}^{B}$ = Buy volume in volume bucket $\tau$
- $n$ = Number of volume buckets
- $V$ = Volume per bucket

**Interpretation:**
- VPIN > 0.7: High toxicity — informed traders are active, spreads should widen
- VPIN 0.3-0.7: Normal range
- VPIN < 0.3: Low toxicity — mostly noise trading

### 9.2 Hasbrouck Information Share

Measures the contribution of each market/venue to price discovery:

$$IS_j = \frac{\gamma_j^2 \cdot \Omega_{jj}}{\gamma' \Omega \gamma}$$

Where:
- $\gamma_j$ = Common factor loading for market $j$
- $\Omega$ = Covariance matrix of reduced-form innovations

For crypto, this helps determine which exchange leads price discovery (typically Binance for BTC).

### 9.3 Amihud Illiquidity Ratio

A simple but effective measure of price impact per unit of volume:

$$\text{ILLIQ}_t = \frac{|r_t|}{V_t}$$

Where:
- $r_t$ = Return in period $t$
- $V_t$ = Dollar volume in period $t$

Higher ILLIQ means less liquid markets where order flow has more impact.

---

## 10. Risk Parameters

### 10.1 Position Sizing Based on Liquidity

$$\text{Max Position} = \min\left(\frac{\text{Risk Budget}}{\text{Stop Distance}}, \frac{V_{avg} \cdot \text{Participation Rate}}{1}\right)$$

Where:
- Risk Budget = Account equity * risk_per_trade (typically 1-2%)
- Participation Rate = Maximum fraction of average volume (typically 1-5%)

### 10.2 Stop Loss Placement

Order flow analysis informs stop placement:

| Method | Description | Application |
|--------|-------------|-------------|
| Beyond Absorption | Place stop beyond identified absorption level | After absorption entry |
| Beyond Liquidity Pool | Place stop beyond the next liquidity cluster | Liquidity-based entry |
| Delta Invalidation | Exit when CVD reverses by X% | Trend-following entries |
| Spread-Based | 3x average spread from entry | Scalping entries |

### 10.3 Risk/Reward Targets

| Strategy Type | Minimum R:R | Typical R:R | Max Holding Time |
|---------------|-------------|-------------|-----------------|
| Scalping (microstructure) | 1.5:1 | 2:1 | 5-30 minutes |
| Intraday (absorption/sweep) | 2:1 | 3:1 | 1-8 hours |
| Swing (institutional flow) | 3:1 | 5:1 | 1-5 days |

---

## 11. Execution Flow

### 11.1 High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                       │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ L2 Feed  │  │ Trade    │  │ Tick     │  │ Funding  │   │
│  │ (DOM)    │  │ Feed     │  │ Data     │  │ Rate     │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │              │         │
│       ▼              ▼              ▼              ▼         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              MESSAGE BUS (Kafka / Redis)              │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│               PROCESSING LAYER                               │
│                          │                                   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │              ORDER FLOW ENGINE                        │   │
│  │                                                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │ Book        │  │ Delta       │  │ Liquidity   │  │   │
│  │  │ Analyzer    │  │ Calculator  │  │ Mapper      │  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │   │
│  │         │                │                │          │   │
│  │         ▼                ▼                ▼          │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │         SIGNAL AGGREGATOR                    │    │   │
│  │  │   Combines all OF signals into score         │    │   │
│  │  └──────────────────┬───────────────────────────┘    │   │
│  └─────────────────────┼────────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│              DECISION LAYER                                   │
│                          │                                   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │         STRATEGY INTEGRATION                          │   │
│  │   Order Flow Score + Other Module Signals             │   │
│  │   → Final Trade Decision (LONG / SHORT / FLAT)        │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                          │                                   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │         RISK MANAGEMENT                               │   │
│  │   Position sizing, SL/TP, exposure limits             │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│              EXECUTION LAYER                                  │
│                          │                                   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │         ORDER ROUTER                                  │   │
│  │   Smart order routing, venue selection, slippage      │   │
│  │   minimization, iceberg execution                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 11.2 Pseudocode: Main Loop

```python
class OrderFlowSystem:
    def __init__(self, config):
        self.book_analyzer = OrderBookAnalyzer(config)
        self.delta_calc = DeltaCalculator(config)
        self.liquidity_mapper = LiquidityMapper(config)
        self.signal_agg = SignalAggregator(config)
        self.risk_mgr = RiskManager(config)
        self.executor = OrderExecutor(config)
    
    async def main_loop(self):
        while self.running:
            # 1. Receive market data update
            update = await self.data_feed.next()
            
            # 2. Update internal state
            if update.type == 'BOOK_UPDATE':
                self.book_analyzer.update(update)
            elif update.type == 'TRADE':
                self.delta_calc.update(update)
                self.liquidity_mapper.update(update)
            
            # 3. Generate order flow signals
            of_signals = {
                'book_imbalance': self.book_analyzer.get_imbalance(),
                'delta': self.delta_calc.get_cumulative_delta(),
                'delta_divergence': self.delta_calc.check_divergence(),
                'absorption': self.book_analyzer.detect_absorption(),
                'liquidity_pools': self.liquidity_mapper.get_pools(),
                'vpin': self.delta_calc.get_vpin(),
            }
            
            # 4. Aggregate into composite score
            composite = self.signal_agg.score(of_signals)
            
            # 5. Check against existing strategy signals
            if self.strategy_signal_pending:
                decision = self.confirm_signal(
                    self.strategy_signal_pending, composite
                )
                
                if decision == 'CONFIRMED':
                    # 6. Calculate position size
                    size = self.risk_mgr.calculate_size(
                        signal=self.strategy_signal_pending,
                        liquidity=of_signals['liquidity_pools']
                    )
                    
                    # 7. Execute
                    await self.executor.execute(
                        signal=self.strategy_signal_pending,
                        size=size,
                        sl=self.risk_mgr.stop_loss,
                        tp=self.risk_mgr.take_profit
                    )
            
            # 8. Monitor existing positions
            await self.monitor_positions(of_signals)
```

---

## 12. Cross-Module Integration

### 12.1 Integration Map

```
Module 02 (Wyckoff)
  │ Phase identification (Accumulation/Distribution)
  │ Supply/Demand tests
  └──► ORDER FLOW confirms:
       - Volume delta during spring/upthrust
       - Absorption at support/resistance
       - Institutional accumulation patterns

Module 04 (Smart Money Concepts)
  │ Order Blocks, Breaker Blocks, FVGs
  │ Displacement, Inducement
  └──► ORDER FLOW confirms:
       - OB with high delta = stronger zone
       - FVG with volume void = true inefficiency
       - Displacement with extreme taker flow = valid

Module 07 (Price Action)
  │ Candlestick patterns, structure breaks
  └──► ORDER FLOW confirms:
       - Pin bar with absorption = valid reversal
       - Engulfing with delta shift = valid signal
       - Break of structure with volume = true BoS

Module 08 (Volume Profile)
  │ POC, Value Area, Volume Nodes
  └──► ORDER FLOW provides:
       - Real-time flow within profile zones
       - Delta at POC for directional bias
       - Absorption at HVN/LVN boundaries
```

### 12.2 Confidence Score Integration

Each module contributes to a unified confidence score:

$$\text{Confidence} = \sum_{m=1}^{M} w_m \cdot S_m$$

Where:
- $w_m$ = Weight for module $m$ (order flow typically weighted 25-35%)
- $S_m$ = Signal score from module $m$ (normalized to [0, 1])

**Order Flow Weight Adjustment:**
- During high volatility: Increase order flow weight (more reliable)
- During low volatility: Decrease order flow weight (less signal)
- During news events: Temporarily disable (flow becomes noisy)

---

## 13. References

### Academic Papers

1. **Kyle, A. S.** (1985). "Continuous Auctions and Insider Trading." *Econometrica*, 53(6), 1315-1335. — Foundational model of informed trading and price impact.

2. **Glosten, L. R., & Milgrom, P. R.** (1985). "Bid, Ask and Transaction Prices in a Specialist Market with Heterogeneously Informed Traders." *Journal of Financial Economics*, 14(1), 71-100. — Adverse selection model of the spread.

3. **O'Hara, M.** (1995). *Market Microstructure Theory*. Blackwell Publishers. — Comprehensive textbook on market microstructure.

4. **Hasbrouck, J.** (2007). *Empirical Market Microstructure*. Oxford University Press. — Empirical methods for studying market microstructure.

5. **Lee, C. M. C., & Ready, M. J.** (1991). "Inferring Trade Direction from Intraday Data." *Journal of Finance*, 46(2), 733-746. — Trade classification algorithm.

6. **Easley, D., Lopez de Prado, M. M., & O'Hara, M.** (2012). "Flow Toxicity and Liquidity in a High-Frequency World." *Review of Financial Studies*, 25(5), 1457-1493. — VPIN methodology.

7. **Bouchaud, J. P., Farmer, J. D., & Lillo, F.** (2009). "How Markets Slowly Digest Changes in Supply and Demand." In *Handbook of Financial Markets: Dynamics and Evolution*, 57-160. — Square-root price impact law.

8. **Stoll, H. R.** (1989). "Inferring the Components of the Bid-Ask Spread: Theory and Empirical Tests." *Journal of Finance*, 44(1), 115-134. — Spread decomposition.

9. **Cont, R., Stoikov, S., & Talreja, R.** (2010). "A Stochastic Model for Order Book Dynamics." *Operations Research*, 58(3), 549-563. — Mathematical model of order book dynamics.

10. **Cartea, A., Jaimungal, S., & Penalva, J.** (2015). *Algorithmic and High-Frequency Trading*. Cambridge University Press. — Comprehensive reference on algorithmic trading.

### Industry & Practitioner References

11. **ICT (Inner Circle Trader)** — Liquidity concepts, kill zones, Judas swing, institutional order flow methodology.

12. **Dalton, J. F., Jones, E. T., & Dalton, R. B.** (1993). *Mind Over Markets*. — Market Profile and auction market theory.

13. **Bookmap / Exocharts / Quantower** — Order flow visualization platforms and their documentation on footprint charts, delta analysis, and order book heatmaps.

14. **CME Group** — "Understanding FX Futures" and market microstructure documentation.

15. **Bitwise Asset Management** (2019). "Presentation to the U.S. Securities and Exchange Commission." — Analysis of real vs fake volume in crypto markets.

---

> **Next Document**: [01_order_book_analysis.md](./01_order_book_analysis.md) — Deep dive into Level 2 data interpretation, order book imbalance models, and implementation algorithms.
