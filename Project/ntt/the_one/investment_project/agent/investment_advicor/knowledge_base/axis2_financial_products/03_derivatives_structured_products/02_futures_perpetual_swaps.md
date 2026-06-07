# Futures & Perpetual Swaps: Comprehensive Guide

> **Axis 2 — Financial Products | Module 03: Derivatives & Structured Products**
> **Document 02 — Futures & Perpetual Swaps**
> **Version:** 2.0
> **Last Updated:** 2026-04-12
> **Author:** Senior Financial Research Team
> **Classification:** Core Knowledge Base — Multi-Agent AI Trading System

---

## Table of Contents

1. [Core Logic](#1-core-logic)
2. [Technical Specifications](#2-technical-specifications)
3. [Mathematical Models](#3-mathematical-models)
4. [Risk Parameters](#4-risk-parameters)
5. [Execution Flow](#5-execution-flow)
6. [References](#6-references)

---

## 1. Core Logic

### 1.1 Futures Contract Mechanics

A futures contract is a binding agreement between two parties to buy or sell an asset at a predetermined price on a specified future date. Unlike options, both parties are obligated to fulfill the contract.

#### 1.1.1 Key Components

| Component | Description |
|---|---|
| **Underlying** | The asset being traded (BTC, ETH, EUR/USD, etc.) |
| **Contract Size** | Notional value per contract |
| **Tick Size** | Minimum price increment |
| **Expiration Date** | When the contract settles |
| **Settlement Method** | Cash or physical delivery |
| **Margin** | Collateral required to hold position |
| **Mark Price** | Fair value used for margin calculations |
| **Index Price** | Composite spot price from multiple exchanges |

#### 1.1.2 Crypto Futures Types

**Linear Futures (USDT/USDC-margined):**
- Margin and settlement in stablecoin (USDT or USDC)
- P&L calculation is straightforward: $(Exit - Entry) \times Quantity$
- No convexity in P&L (linear relationship with underlying)
- Preferred for beginners and simpler risk management
- Example: BTC-USDT quarterly futures on Binance

**Inverse Futures (Coin-margined):**
- Margin and settlement in the underlying cryptocurrency
- P&L in BTC/ETH: $Contracts \times (\frac{1}{Entry} - \frac{1}{Exit})$
- Contains non-linear (convex) payoff for longs:
  - When BTC rises: profit in BTC, and BTC is worth more (double benefit)
  - When BTC falls: loss in BTC, and BTC is worth less (double pain)
- Preferred by those who want to maximize BTC holdings
- Example: BTC-USD quarterly futures on Deribit, Bybit

**Quanto Futures:**
- Settled in a different currency than the underlying
- Example: ETH/USD quanto settled in BTC
- Contains correlation risk between the underlying and settlement currency

#### 1.1.3 Margin System

**Initial Margin:** The minimum collateral required to open a position.

$$\text{Initial Margin} = \frac{\text{Notional Value}}{\text{Leverage}} + \text{Opening Fee}$$

**Maintenance Margin:** The minimum equity required to keep the position open.

$$\text{Maintenance Margin} = \text{Notional Value} \times \text{Maintenance Rate}$$

Typical maintenance margin rates:
- Binance: 0.4% (tier 1, up to 125x leverage)
- Deribit: 0.575% for BTC
- OKX: 0.4-2% depending on position size tier

**Margin Modes:**

| Mode | Description | Risk |
|---|---|---|
| **Isolated** | Each position has its own margin | Liquidation only affects that position |
| **Cross** | All positions share account balance | One position can be saved by others' profits |
| **Portfolio** | Margin based on overall portfolio risk | Most capital efficient; requires advanced risk |

#### 1.1.4 Settlement Types

**Cash Settlement:**
- No physical delivery of the underlying
- Settlement = Position × (Settlement Price - Entry Price)
- Settlement price typically = index price at expiry (or TWAP)
- Most crypto futures are cash-settled

**Physical Delivery:**
- Actual delivery of the underlying asset
- Common in FX futures (CME) and some commodity futures
- Requires ability to deliver/receive the physical asset

### 1.2 Basis and Contango/Backwardation

#### 1.2.1 Basis Definition

$$\text{Basis} = F_t - S_t$$

Where:
- $F_t$ = Futures price at time $t$
- $S_t$ = Spot price at time $t$

**Annualized Basis (Basis Yield):**

$$\text{Basis Yield (annualized)} = \frac{F_t - S_t}{S_t} \times \frac{365}{T}$$

Where $T$ = days to expiration.

#### 1.2.2 Contango

**Contango** occurs when futures trade above spot: $F > S$ (positive basis).

**Causes in Crypto:**
- Demand for leveraged long exposure exceeds hedging supply
- Positive carry (borrow rate > staking yield)
- Bullish market sentiment
- Institutional demand for futures (CME contango often persists)

**Typical Crypto Contango:**
- Normal market: 5-15% annualized
- Bull market: 20-50% annualized
- Extreme euphoria: 50-100%+ annualized

#### 1.2.3 Backwardation

**Backwardation** occurs when futures trade below spot: $F < S$ (negative basis).

**Causes in Crypto:**
- Bearish sentiment, hedging pressure
- High staking/DeFi yields exceeding borrow rates
- Short-term panic selling
- Forced liquidations of long futures positions

**Typical Crypto Backwardation:**
- Moderate bear: -5% to -15% annualized
- Severe bear/crisis: -20% to -50% annualized
- Flash crash: Can be extreme but short-lived

#### 1.2.4 Term Structure

The term structure shows how basis varies across different expiry dates:

```
Basis%
  │
  │                    ● Quarterly (Dec)
  │              ● Quarterly (Sep)
  │        ● Quarterly (Jun)
  │   ● Monthly (next month)
  │ ● Weekly
──┼──────────────────────────── Time to Expiry
  │
```

**Normal Contango Term Structure:** Longer-dated futures have higher basis (upward-sloping)

**Inverted Term Structure:** Near-term futures have higher basis than far-term (suggests near-term bullishness or squeeze)

**Flat Term Structure:** Similar basis across maturities (low conviction environment)

### 1.3 Perpetual Swap Mechanics

#### 1.3.1 What Is a Perpetual Swap?

A perpetual swap (perp) is a derivative unique to cryptocurrency markets — a futures contract with no expiration date. Position can be held indefinitely, with the price anchored to spot through a funding rate mechanism.

**Key Innovation:** BitMEX (Arthur Hayes) invented the perpetual swap in 2016. It has since become the dominant crypto derivative instrument.

**Market Dominance:**
- Perpetual swaps account for >70% of total crypto derivatives volume
- 24/7 trading with no rollover required
- Primary instrument for speculation and hedging in crypto

#### 1.3.2 Funding Rate Mechanism

The funding rate is a periodic payment exchanged between long and short position holders to keep the perpetual swap price aligned with the spot index price.

**Calculation (Binance model):**

$$\text{Funding Rate} = \text{Average Premium Index} + \text{clamp}(I - P, -d, d)$$

Where:
- $I$ = Interest Rate component (typically 0.01% per 8h for crypto)
- $P$ = Premium Index (measures deviation from spot)
- $d$ = Dampener (typically 0.05%)
- clamp restricts the interest-premium difference to ±d

**Premium Index:**

$$P = \frac{\text{Max}(0, \text{Impact Bid Price} - \text{Index Price}) - \text{Max}(0, \text{Index Price} - \text{Impact Ask Price})}{\text{Index Price}}$$

**Impact Prices:** The price at which a specific notional market order (e.g., 200 BTC on Binance) would fill. Measures actual order book depth.

**Funding Payment:**

$$\text{Payment} = \text{Position Notional} \times \text{Funding Rate}$$

$$\text{Position Notional} = |Quantity| \times \text{Mark Price}$$

**Payment Rules:**
- If Funding Rate > 0: Longs pay Shorts
- If Funding Rate < 0: Shorts pay Longs
- Payment occurs at fixed intervals (every 8 hours on most exchanges)
- dYdX and some DEXs use continuous funding (per-second accrual)

**Funding Rate Intervals:**
| Exchange | Interval | Settlement Times (UTC) |
|---|---|---|
| Binance | 8 hours | 00:00, 08:00, 16:00 |
| OKX | 8 hours | 00:00, 08:00, 16:00 |
| Bybit | 8 hours | 00:00, 08:00, 16:00 |
| Deribit | 8 hours | 00:00, 08:00, 16:00 |
| dYdX | Continuous | Per-second accrual |
| Hyperliquid | 1 hour | Every hour |

**Annualized Funding Rate:**

$$\text{APR}_{funding} = \text{Funding Rate per interval} \times \frac{365 \times 24}{\text{Interval hours}}$$

Example: 0.01% per 8h = 0.01% × 3 × 365 = 10.95% APR

#### 1.3.3 Mark Price vs Last Price

**Mark Price:** A fair-value price calculated using the index price and a moving average of basis. Used for:
- Liquidation calculations
- Unrealized P&L display
- Preventing manipulation-triggered liquidations

$$\text{Mark Price} = \text{Index Price} \times (1 + \text{Funding Basis Rate})$$

Or (Binance method):

$$\text{Mark Price} = \text{Median}(\text{Price 1}, \text{Price 2}, \text{Price 3})$$

Where:
- Price 1 = Index Price × (1 + Funding Rate × Time Until Next Funding)
- Price 2 = Index Price + EMA(Fair Price Basis, 5min)
- Price 3 = Last Price

**Last Price:** The price of the most recent trade. Used for:
- Trigger orders (stop-loss, take-profit)
- Realized P&L calculation
- Can be manipulated in low-liquidity environments

**Why This Matters:**
- A flash crash in last price (e.g., due to thin order book) should NOT liquidate positions
- Mark price uses index (multiple exchange composite) to prevent manipulation
- Traders must understand which price triggers their stop-losses vs liquidations

#### 1.3.4 Insurance Fund

The insurance fund acts as a buffer against socialized losses when liquidated positions cannot be filled at the bankruptcy price.

**How It Works:**
1. When a position is liquidated, it's taken over by the liquidation engine
2. If the liquidation engine closes the position at a price better than bankruptcy price: the surplus goes to the insurance fund
3. If the liquidation engine cannot close at bankruptcy price: the insurance fund covers the deficit
4. If the insurance fund is depleted: Auto-Deleveraging (ADL) occurs — profitable counter-positions are reduced

**Insurance Fund Sizes (approximate, 2026):**
- Binance: >$1B (combined across all futures)
- OKX: >$500M
- Bybit: >$300M

**ADL (Auto-Deleveraging):**
- Last resort when insurance fund cannot cover losses
- Most profitable positions on the opposite side are force-closed
- ADL ranking based on profit percentage and leverage
- Rare in normal conditions; occurs during extreme market moves

### 1.4 Hedging with Futures

#### 1.4.1 Delta Hedging

The simplest hedge: offset the directional exposure of a position using futures.

**Perfect Hedge (1:1):**
- Long 1 BTC spot → Short 1 BTC futures/perp
- Net delta = 0

**Partial Hedge:**
- Long 10 BTC spot → Short 5 BTC futures
- Hedge ratio = 0.5 (50% hedged)
- Remaining delta = 5 BTC

**When to Use:**
- Protect unrealized profits on long-term holdings
- Reduce portfolio delta during uncertain periods
- Achieve market-neutral position while maintaining spot holdings (e.g., for staking)

#### 1.4.2 Cross-Hedging

When a futures contract for the exact asset is unavailable, use a correlated asset's futures.

**Example:** Hedge AAVE exposure using ETH futures (high correlation)

**Cross-Hedge Ratio:**

$$h^* = \rho_{S,F} \times \frac{\sigma_S}{\sigma_F}$$

Where:
- $h^*$ = Optimal hedge ratio
- $\rho_{S,F}$ = Correlation between spot asset and futures
- $\sigma_S$ = Volatility of the asset to be hedged
- $\sigma_F$ = Volatility of the hedging futures

**Hedging Effectiveness:**

$$\text{Hedge Effectiveness} = 1 - \frac{\text{Var(Hedged)}}{\text{Var(Unhedged)}} = \rho^2$$

#### 1.4.3 Minimum Variance Hedge Ratio

The hedge ratio that minimizes the variance of the hedged portfolio:

$$h^* = \frac{\text{Cov}(S, F)}{\text{Var}(F)} = \rho \frac{\sigma_S}{\sigma_F}$$

**Derivation:**
The hedged portfolio return is:

$$R_H = R_S - h \times R_F$$

$$\text{Var}(R_H) = \sigma_S^2 - 2h\rho\sigma_S\sigma_F + h^2\sigma_F^2$$

Minimize by taking derivative with respect to $h$ and setting to zero:

$$\frac{d\text{Var}(R_H)}{dh} = -2\rho\sigma_S\sigma_F + 2h\sigma_F^2 = 0$$

$$h^* = \rho \frac{\sigma_S}{\sigma_F}$$

**Practical Implementation:**
1. Estimate rolling correlation (30-60 day window)
2. Estimate rolling volatilities (EWMA or realized vol)
3. Compute $h^*$
4. Adjust hedge position accordingly
5. Re-estimate periodically (daily or weekly)

### 1.5 Basis Trading Strategies

#### 1.5.1 Cash-and-Carry Arbitrage

**Strategy:** Buy spot, sell futures. Lock in the basis as risk-free profit.

**Construction:**
- Buy 1 BTC at spot price $S_0$
- Sell 1 BTC futures at price $F_0$ (expiry $T$)
- Hold until expiration; both converge at settlement price $S_T$

**P&L:**

$$\text{P\&L} = (F_0 - S_0) - \text{costs}$$

**Costs:**
- Borrowing cost (if financed)
- Opportunity cost of capital
- Transaction fees (spot + futures)
- Margin funding cost

**Annualized Return:**

$$r_{carry} = \frac{F_0 - S_0}{S_0} \times \frac{365}{T_{days}} - \text{cost rate}$$

**When Profitable:**
- Annualized basis > all-in cost of carry
- Typical threshold: basis yield > risk-free rate + 3-5% (in crypto)

**Risks:**
- Margin risk: If BTC drops, futures margin call may require additional capital (even though overall position is profitable)
- Liquidation risk: If using leverage on the short futures leg
- Settlement risk: Exchange failure before settlement
- Basis widening (if exiting early): Basis could widen further, causing MTM loss

#### 1.5.2 Reverse Cash-and-Carry

**Strategy:** Short spot (or borrow and sell), buy futures. Profit from backwardation.

**Construction:**
- Borrow and sell 1 BTC at spot price $S_0$
- Buy 1 BTC futures at price $F_0$ ($F_0 < S_0$, backwardation)
- At expiry: Buy back BTC at $S_T$ to repay loan, futures settle at $S_T$

**P&L:**

$$\text{P\&L} = (S_0 - F_0) - \text{borrow cost} - \text{fees}$$

**When to Use:**
- Futures in backwardation (negative basis)
- Available and affordable BTC borrowing
- Less common in crypto due to high borrow rates

#### 1.5.3 Funding Rate Arbitrage (Cash-and-Carry with Perps)

**Strategy:** The most common basis trade in crypto. Buy spot, short perpetual swap. Collect funding rate.

**Construction:**
- Buy 1 BTC spot (or use staking to earn additional yield)
- Short 1 BTC perpetual swap
- Delta neutral: No directional exposure
- Collect positive funding rate (if funding > 0, shorts receive payment)

**Expected Return:**

$$r_{funding} = \text{Avg Funding Rate} \times 3 \times 365 - \text{costs}$$

(Assuming 8-hour funding intervals)

**Costs:**
- Trading fees (entry + exit for both legs)
- Potential margin/collateral opportunity cost
- Negative funding periods (must survive drawdowns)
- Spread between spot buy and perp sell price

**Key Metrics to Monitor:**
- Current funding rate
- 7-day average funding rate
- 30-day average funding rate
- Funding rate distribution (probability of negative)
- Maximum consecutive negative funding periods (historical)

**Risk Management:**
- Must maintain adequate margin on the short perp leg
- If BTC rises sharply, short perp has unrealized loss → margin call
  - Spot has unrealized gain, but may not be on same exchange
  - Solution: Cross-margined accounts, or maintain excess margin
- Negative funding rate periods reduce overall return
- Exchange risk: If exchange fails, lose both legs

#### 1.5.4 Calendar Spread (Futures Spread)

**Strategy:** Buy one futures expiry, sell another. Profit from basis convergence or divergence.

**Construction:**
- Buy near-term futures at $F_1$ (expiry $T_1$)
- Sell far-term futures at $F_2$ (expiry $T_2$, $T_2 > T_1$)
- Net position: Long the calendar spread

**P&L:**

$$\text{P\&L} = (F_2 - F_1)_{entry} - (F_2 - F_1)_{exit}$$

Profit if the spread narrows (far-term premium decreases relative to near-term).

**When to Use:**
- Expect term structure to flatten
- Lower risk than directional trade (spread has lower vol than outright)
- Relative value opportunity (one expiry mispriced vs another)

**Types:**
- Bull Calendar: Expect spread to narrow (buy near, sell far)
- Bear Calendar: Expect spread to widen (sell near, buy far)

### 1.6 Leverage Management and Liquidation

#### 1.6.1 Leverage Calculation

**Effective Leverage:**

$$\text{Leverage} = \frac{\text{Position Notional}}{\text{Account Equity}}$$

**Position Notional:**
- Linear: $Quantity \times Mark Price$
- Inverse: $Contracts \times Contract Value / Mark Price$ (e.g., for BTC inverse)

#### 1.6.2 Liquidation Price Calculation

**For Long Position (Isolated Margin):**

$$P_{liq,long} = \frac{Entry Price \times (1 - Initial Margin Rate + Maintenance Margin Rate + Taker Fee Rate)}{1 + Maintenance Margin Rate + Taker Fee Rate}$$

Simplified approximation:

$$P_{liq,long} \approx Entry Price \times \left(1 - \frac{1}{Leverage} + MMR\right)$$

**For Short Position (Isolated Margin):**

$$P_{liq,short} = \frac{Entry Price \times (1 + Initial Margin Rate - Maintenance Margin Rate - Taker Fee Rate)}{1 - Maintenance Margin Rate - Taker Fee Rate}$$

Simplified approximation:

$$P_{liq,short} \approx Entry Price \times \left(1 + \frac{1}{Leverage} - MMR\right)$$

Where:
- $MMR$ = Maintenance Margin Rate

**Example (Long BTC at $60,000, 10x leverage):**
- Initial margin = $60,000 / 10 = $6,000
- Maintenance margin rate = 0.4%
- Liquidation price ≈ $60,000 × (1 - 1/10 + 0.004) = $60,000 × 0.904 = $54,240
- Price can drop ~9.6% before liquidation

**For Cross Margin:**
Liquidation considers entire account balance:

$$P_{liq,long,cross} = Entry \times Quantity - (Account Balance - \sum Other Margins) \times (1 - MMR) / Quantity$$

#### 1.6.3 Liquidation Distance

**Definition:** The percentage move required to trigger liquidation.

$$\text{Liquidation Distance} = \frac{|Mark Price - Liquidation Price|}{Mark Price} \times 100\%$$

**Minimum Recommended Distances:**

| Strategy Type | Min Liquidation Distance |
|---|---|
| Scalping | 10% |
| Swing trading | 25% |
| Position trading | 40% |
| Basis trading | 50% |
| Emergency/conservative | 80% |

#### 1.6.4 Liquidation Cascades

A liquidation cascade occurs when forced closures of leveraged positions cause further price moves, triggering additional liquidations in a chain reaction.

**Anatomy of a Cascade:**
1. Large price move triggers first set of liquidations
2. Liquidation orders hit the market as aggressive market orders
3. These orders push price further in the same direction
4. Additional liquidation levels are hit
5. Process continues until buying power absorbs the selling pressure

**Detection Signals:**
- Rapid increase in liquidation volume
- Order book thinning (bids/asks being consumed)
- Funding rate spiking
- Open interest declining rapidly
- Price moving faster than normal with low actual trade volume (just liquidations)

**Bot Behavior During Cascades:**
- Do NOT open new positions into a cascade
- Do NOT set stop-losses that would trigger during a cascade (use mark price, not last price)
- If running basis trades: ensure sufficient margin to survive the spike
- Consider adding to positions AFTER cascade exhausts (contrarian, but only with tight risk)

### 1.7 Funding Rate Strategies

#### 1.7.1 Passive Funding Collection (Delta-Neutral)

**The most reliable funding rate strategy.**

**Setup:**
1. Identify perpetual swaps with consistently positive funding rates
2. Long spot (or long spot equivalent)
3. Short perpetual swap (equal notional)
4. Collect funding payments from shorts

**Expected Return:**
- Typical bull market: 15-40% APR
- Typical neutral market: 5-15% APR
- Bear market: May be negative (strategy paused)

**Enhancements:**
- Use staking/lending on the spot leg for additional yield
- Multi-exchange: Spot on exchange A, short perp on exchange B with higher funding
- Altcoin funding rates are often higher (but less reliable)

#### 1.7.2 Active Funding Rate Trading

**Strategy:** Take directional funding bets based on predicted funding rate changes.

**Signals:**
- Funding rate mean reversion: Extreme positive → expect normalization → long perp
- Funding rate momentum: Rising funding → more bullish sentiment → long spot
- Funding rate divergence across exchanges: Arb opportunity

#### 1.7.3 Funding Rate Arbitrage (Cross-Exchange)

**Strategy:** When funding rates differ significantly across exchanges.

**Construction:**
- Long perp on exchange with negative (or less positive) funding → receive payment or pay less
- Short perp on exchange with positive (or more positive) funding → receive more payment
- Net delta = 0 (if equal notional)
- Net funding income = higher funding received - lower funding paid

**Risks:**
- Margin on both exchanges required (capital intensive)
- Exchange counterparty risk
- Execution timing risk (funding snapshots may differ)
- Basis divergence between exchanges

---

## 2. Technical Specifications

### 2.1 Data Requirements for Futures/Perps Trading

```
FUTURES_DATA_SOURCES:

  real_time:
    spot_price:
      sources: [binance, coinbase, kraken, okx, bybit]
      aggregation: median of top-3 by volume
      update_frequency: 100ms

    perpetual_data:
      mark_price: per exchange, 100ms
      last_price: per exchange, tick-level
      funding_rate:
        current: real-time predicted next funding
        next_settlement: countdown timer
      open_interest: per exchange, 1s update
      long_short_ratio: per exchange, 5min update
      liquidations: real-time feed

    futures_data:
      basis: per expiry, 100ms
      term_structure: all expiries, 1s update
      open_interest_by_expiry: 1min update
      volume_by_expiry: real-time

    order_book:
      depth: L2 (top 20 levels minimum)
      update_frequency: 100ms
      impact_price: calculated for 100K, 500K, 1M USD

  historical:
    funding_rate_history: full history per exchange
    basis_history: all expiries, hourly OHLC
    liquidation_history: aggregate liquidation data
    open_interest_history: daily snapshots
    volume_history: hourly aggregated
```

### 2.2 System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│              FUTURES/PERPS TRADING ENGINE                        │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │  Market Data      │  │  Funding Rate    │  │  Basis       │  │
│  │  Aggregator       │  │  Monitor         │  │  Calculator  │  │
│  │  (multi-exchange) │  │  (prediction)    │  │  (all terms) │  │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬───────┘  │
│           │                     │                    │           │
│  ┌────────▼─────────────────────▼────────────────────▼───────┐  │
│  │              STRATEGY ENGINE                                │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐            │  │
│  │  │ Basis      │ │ Funding    │ │ Directional│            │  │
│  │  │ Trading    │ │ Rate Arb   │ │ Futures    │            │  │
│  │  └────────────┘ └────────────┘ └────────────┘            │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐            │  │
│  │  │ Calendar   │ │ Cross-     │ │ Hedging    │            │  │
│  │  │ Spread     │ │ Exchange   │ │ Engine     │            │  │
│  │  └────────────┘ └────────────┘ └────────────┘            │  │
│  └───────────────────────┬────────────────────────────────────┘  │
│                          │                                       │
│  ┌───────────────────────▼────────────────────────────────────┐  │
│  │              RISK & MARGIN MANAGEMENT                       │  │
│  │  - Liquidation distance monitoring (every 100ms)            │  │
│  │  - Margin utilization tracking                              │  │
│  │  - Cross-exchange exposure reconciliation                   │  │
│  │  - Funding rate P&L tracking                                │  │
│  │  - Leverage enforcement                                     │  │
│  └───────────────────────┬────────────────────────────────────┘  │
│                          │                                       │
│  ┌───────────────────────▼────────────────────────────────────┐  │
│  │              EXECUTION ENGINE                               │  │
│  │  - Smart order routing (best price across exchanges)        │  │
│  │  - Slippage minimization (TWAP, VWAP for large orders)     │  │
│  │  - Multi-exchange coordination                              │  │
│  │  - Margin transfer between accounts                         │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

### 2.3 Exchange Configurations for Futures

```
EXCHANGE_CONFIGS:

  binance_futures:
    linear_perps:
      base_url: https://fapi.binance.com
      ws_url: wss://fstream.binance.com/ws
      contract_type: USDT-margined
      available_assets: 200+
      max_leverage: 125x (BTC), 75x (ETH), varies by asset
      funding_interval: 8h
      fee_maker: 0.02%
      fee_taker: 0.04%
      min_order_notional: $5
      tick_sizes: varies per contract
      margin_modes: [isolated, cross]

    inverse_perps:
      base_url: https://dapi.binance.com
      contract_type: coin-margined
      available_assets: [BTC, ETH, +15]
      funding_interval: 8h

    quarterly_futures:
      base_url: https://dapi.binance.com
      settlement: quarterly (March, June, Sep, Dec)
      contract_type: coin-margined
      delivery_method: cash

  okx_futures:
    base_url: https://www.okx.com/api/v5
    perpetual: USDT and coin-margined
    futures: weekly, bi-weekly, quarterly, bi-quarterly
    margin_modes: [isolated, cross, portfolio_margin]
    max_leverage: 125x
    funding_interval: 8h
    fee_maker: 0.02%
    fee_taker: 0.05%

  deribit_futures:
    base_url: https://www.deribit.com/api/v2
    perpetual: BTC-PERPETUAL, ETH-PERPETUAL
    futures: quarterly (BTC-{DATE}, ETH-{DATE})
    settlement: inverse (in BTC/ETH)
    max_leverage: 50x (BTC), 50x (ETH)
    funding_interval: 8h (continuous interest)
    fee_maker: -0.01% (rebate)
    fee_taker: 0.05%
    settlement_time: "08:00 UTC daily"
    portfolio_margin: available

  cme_crypto:
    base_url: via broker API
    contracts:
      BTC_full: 5 BTC per contract
      BTC_micro: 0.1 BTC per contract
      ETH_full: 50 ETH per contract
      ETH_micro: 0.1 ETH per contract
    settlement: cash (CME CF Bitcoin Reference Rate)
    expiry: monthly (standard), weekly (micro)
    margin: SPAN portfolio margin
    trading_hours: "Sun-Fri 5PM-4PM CT (23h/day)"
    fee: ~$5 per contract (varies by broker)
```

### 2.4 Performance Requirements

```
PERFORMANCE_SPECS:

  latency_requirements:
    market_data_ingestion: <2ms per exchange
    basis_calculation: <1ms
    funding_rate_prediction: <10ms
    liquidation_distance_calc: <1ms
    risk_check: <5ms
    order_submission: <20ms (exchange dependent)
    cross_exchange_sync: <50ms

  throughput:
    market_data_events: 50,000+/second (aggregated)
    order_updates: 10,000/second
    position_recalc: every 100ms

  reliability:
    uptime: 99.99%
    websocket_reconnect: <1 second
    order_reconciliation: every 5 seconds
    margin_check: continuous
```

---

## 3. Mathematical Models

### 3.1 Futures Fair Value Pricing

**Cost of Carry Model:**

$$F_0 = S_0 \times e^{(r - y)T}$$

Where:
- $r$ = Risk-free rate (or borrow rate for crypto)
- $y$ = Yield on the underlying (staking yield, lending rate)
- $T$ = Time to expiration in years

**Crypto-Specific Fair Value:**

$$F_0 = S_0 \times e^{(r_{borrow} - y_{staking} + c_{insurance})T}$$

Where:
- $r_{borrow}$ = Cost of borrowing stablecoin to buy spot
- $y_{staking}$ = Staking/DeFi yield on the crypto asset
- $c_{insurance}$ = Exchange/counterparty risk premium

**Basis Decomposition:**

$$\text{Basis} = F - S = S \times \left(e^{(r-y)T} - 1\right) \approx S \times (r - y) \times T$$

For short-dated contracts (linear approximation valid).

### 3.2 Perpetual Swap Fair Value

The perpetual swap has no expiry, so traditional cost-of-carry doesn't apply directly. Instead, the funding mechanism creates an implicit term structure:

**Implied Rate from Funding:**

$$r_{implied} = \text{Funding Rate} \times \frac{365 \times 24}{\text{Interval (hours)}}$$

**Fair Perpetual Price:**

$$P_{perp,fair} = S_{index} \times (1 + \text{Premium Index})$$

In equilibrium, $P_{perp} \approx S_{index}$, with small deviations corrected by funding payments.

**Funding Rate Fair Value Model:**

Under no-arbitrage between perpetual and quarterly futures:

$$\text{Implied Funding} \approx \frac{F_{quarterly} - S}{S} \times \frac{8h}{T_{quarterly}}$$

If actual funding > implied funding from term structure, there's an opportunity to short perp and long quarterly (or vice versa).

### 3.3 Hedge Ratio Mathematics

**Minimum Variance Hedge Ratio (repeated with full derivation):**

Given a portfolio of asset $S$ to be hedged with futures $F$:

$$\text{Portfolio Value Change} = \Delta S - h \times \Delta F$$

$$\text{Var}(\Delta S - h\Delta F) = \sigma_S^2 - 2h\sigma_{SF} + h^2\sigma_F^2$$

$$\frac{\partial}{\partial h}\text{Var} = -2\sigma_{SF} + 2h\sigma_F^2 = 0$$

$$h^* = \frac{\sigma_{SF}}{\sigma_F^2} = \rho \frac{\sigma_S}{\sigma_F}$$

**Optimal Number of Contracts:**

$$N^* = h^* \times \frac{Q_S}{Q_F}$$

Where:
- $Q_S$ = Size of position being hedged (in units)
- $Q_F$ = Size of one futures contract (in units)

**Time-Varying Hedge Ratio (DCC-GARCH):**

The correlation $\rho_t$ and volatilities $\sigma_{S,t}$, $\sigma_{F,t}$ change over time. Using GARCH models:

$$\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$

$$h_t^* = \hat{\rho}_t \frac{\hat{\sigma}_{S,t}}{\hat{\sigma}_{F,t}}$$

Re-estimate daily for optimal hedging performance.

### 3.4 Liquidation Mathematics

**Isolated Margin — Long Position:**

Account equity after price change:

$$\text{Equity} = \text{Initial Margin} + \text{Unrealized P\&L}$$

$$\text{Equity} = \frac{P_{entry} \times Q}{L} + Q \times (P_{current} - P_{entry})$$

Liquidation occurs when equity = maintenance margin:

$$\frac{P_{entry} \times Q}{L} + Q \times (P_{liq} - P_{entry}) = P_{liq} \times Q \times MMR$$

Solving for $P_{liq}$:

$$P_{liq} = P_{entry} \times \frac{L - 1}{L \times (1 - MMR)}$$

Simplified:

$$P_{liq} \approx P_{entry} \times \left(1 - \frac{1}{L} + MMR\right)$$

**Isolated Margin — Short Position:**

$$P_{liq} = P_{entry} \times \frac{L + 1}{L \times (1 + MMR)}$$

Simplified:

$$P_{liq} \approx P_{entry} \times \left(1 + \frac{1}{L} - MMR\right)$$

**Cross Margin:**

$$P_{liq,long} = P_{entry} - \frac{\text{Available Balance} - \text{Maintenance Margin for All Other Positions}}{Q}$$

### 3.5 Funding Rate Prediction Models

**ARIMA Model for Funding Rate:**

$$FR_t = c + \phi_1 FR_{t-1} + \phi_2 FR_{t-2} + \theta_1 \epsilon_{t-1} + \epsilon_t$$

**Feature-Based ML Model:**

Inputs:
- Current funding rate
- Recent funding rate history (lag 1-8)
- Long/short ratio
- Open interest change
- Spot price momentum
- Options put/call ratio
- Liquidation volume

Output: Predicted next funding rate and confidence interval

**Mean Reversion Model:**

$$FR_t = \mu + \phi(FR_{t-1} - \mu) + \epsilon_t$$

Where:
- $\mu$ = Long-run mean funding rate
- $\phi$ = Mean-reversion speed (|$\phi$| < 1)
- Half-life of mean reversion: $\tau = -\ln(2)/\ln(\phi)$

### 3.6 Basis Spread Models

**Fair Basis Model:**

$$B_{fair}(T) = S_0 \times (e^{(r-y)T} - 1)$$

**Basis Z-Score (for mean-reversion trading):**

$$z_{basis} = \frac{B_{current} - \mu_B}{\sigma_B}$$

Where:
- $\mu_B$ = Rolling mean of basis (e.g., 30-day)
- $\sigma_B$ = Rolling standard deviation of basis

**Trade Signal:**
- $z > 2$: Basis is rich → sell futures, buy spot (cash-and-carry)
- $z < -2$: Basis is cheap → buy futures, sell/short spot (reverse carry)

### 3.7 Optimal Leverage Calculation

**Kelly Criterion for Leveraged Futures:**

$$f^* = \frac{\mu - r_f}{\sigma^2}$$

Where:
- $f^*$ = Optimal leverage
- $\mu$ = Expected return of the strategy
- $r_f$ = Risk-free rate
- $\sigma^2$ = Variance of returns

**Fractional Kelly (conservative):**

$$f_{actual} = \alpha \times f^* \quad \text{where } \alpha \in [0.25, 0.5]$$

**Maximum Leverage Given Drawdown Tolerance:**

$$L_{max} = \frac{D_{max}}{R_{max} \times C}$$

Where:
- $D_{max}$ = Maximum acceptable drawdown (e.g., 25%)
- $R_{max}$ = Maximum expected adverse move (e.g., 30% for BTC daily worst case)
- $C$ = Confidence factor (e.g., 1.5 for safety buffer)

Example: $L_{max} = 0.25 / (0.30 × 1.5) = 0.56x$ → very conservative for BTC

---

## 4. Risk Parameters

### 4.1 Futures/Perps Risk Limits

```
RISK_LIMITS:

  leverage_limits:
    max_effective_leverage: 5x (portfolio level)
    max_single_position_leverage: 10x
    max_basis_trade_leverage: 3x (on each leg)
    max_funding_arb_leverage: 5x (hedged)
    target_liquidation_distance: >30%

  position_limits:
    max_single_position_pct: 20% of portfolio (notional)
    max_futures_notional: 300% of portfolio (gross)
    max_net_exposure: 100% of portfolio (net long or short)
    max_single_exchange_exposure: 50% of portfolio
    max_perp_OI_share: 1% of total exchange OI

  loss_limits:
    max_daily_loss: 3% of portfolio
    max_weekly_loss: 7% of portfolio
    max_single_trade_loss: 2% of portfolio
    max_drawdown: 20% from peak
    trailing_stop_drawdown: 10% from local peak

  funding_rate_limits:
    max_funding_exposure_annual: 5% of portfolio (cost)
    min_avg_funding_for_harvest: 10% APR (net of costs)
    max_consecutive_negative_funding: 7 days (then reassess)

  basis_trade_limits:
    min_annualized_basis_entry: 8% (after costs)
    max_basis_widening_tolerance: 2x entry basis
    min_expiry_for_entry: 14 days
    max_roll_cost: 1% per roll

  margin_management:
    max_margin_utilization: 60% (of available)
    margin_warning_threshold: 50%
    margin_critical_threshold: 70%
    auto_deleverage_trigger: 75%
    collateral_buffer: 40% above maintenance
```

### 4.2 Exchange Risk Management

```
EXCHANGE_RISK:

  counterparty_limits:
    max_single_exchange_pct: 40% of total capital
    min_exchanges_for_diversification: 3
    max_defi_protocol_pct: 20% (smart contract risk)
    insurance_fund_min_ratio: 2% (exchange insurance fund / total OI)

  operational_risk:
    api_failure_protocol:
      primary_exchange_down: switch to backup within 5s
      all_exchanges_down: halt all new orders, maintain existing
      data_staleness_threshold: 5 seconds (trigger alert)
    
    withdrawal_risk:
      max_withdrawal_queue_time: 2 hours (flag concern)
      pre_position_withdrawal_test: monthly
      emergency_withdrawal_plan: documented per exchange

  smart_contract_risk (DeFi):
    max_tvl_pct_single_protocol: 10% of portfolio
    audit_requirement: minimum 2 reputable audits
    protocol_age_minimum: 6 months live
    bug_bounty_minimum: $1M
    insurance_coverage: use Nexus Mutual / InsurAce when available
```

### 4.3 Scenario Analysis for Futures/Perps

```
SCENARIOS:

  flash_crash_20pct:
    price_move: -20% in 15 minutes
    impact:
      naked_long_10x: -200% (liquidated, total loss of margin)
      naked_long_3x: -60% (margin called, not yet liquidated)
      basis_trade_delta_neutral: Mark-to-market loss on short perp margin (~0% P&L if survives)
      funding_arb: Temporary unrealized loss, must survive margin call
    action:
      - All leveraged longs: Ensure liquidation distance > 25%
      - Basis trades: Pre-fund excess margin for 30%+ move
      - Stop-losses: Use mark price, not last price

  sustained_negative_funding:
    duration: 30 days
    avg_funding: -0.05% per 8h (-54% APR)
    impact:
      funding_harvest_strategy: -4.5% over 30 days
      short_perp_hedge: Pays funding (additional cost of hedging)
    action:
      - Pause funding harvest if 7-day avg < -0.01%
      - Switch to quarterly futures for hedging (avoid funding)
      - Reverse: Go long perp + short spot to collect negative funding

  exchange_insolvency:
    probability: low but non-zero (FTX precedent)
    impact: Total loss of funds on that exchange
    action:
      - Never exceed 40% on any single exchange
      - Regular proof-of-reserves monitoring
      - Maintain withdrawal capability at all times
      - Use regulated exchanges (CME, Deribit) for large positions

  liquidation_cascade:
    trigger: Large liquidation cluster at key level
    characteristics:
      - Open interest drops >5% in 1 hour
      - Liquidation volume > 3x normal
      - Order book depth collapses
    action:
      - Do NOT add to positions
      - Widen stop-losses (avoid being swept)
      - Potential contrarian entry AFTER cascade exhausts
      - Monitor insurance fund drain rate
```

---

## 5. Execution Flow

### 5.1 Futures/Perps Strategy Selection Flow

```
STRATEGY_SELECTION:

  ╔══════════════════════════════════════════════════════════╗
  ║  INPUT: Market Conditions Assessment                      ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  1. Compute metrics:                                     ║
  ║     - Annualized basis (all expiries)                    ║
  ║     - Current funding rate + 7d/30d average              ║
  ║     - Term structure shape                               ║
  ║     - Long/short ratio                                   ║
  ║     - Open interest trend                                ║
  ║     - Liquidation heat map                               ║
  ║     - Cross-exchange basis differentials                  ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  DECISION TREE:                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  IF annualized_basis > 15% AND basis_zscore > 1.5:       ║
  ║    → CASH_AND_CARRY (basis is rich, harvest carry)       ║
  ║                                                          ║
  ║  IF annualized_basis < -10% AND basis_zscore < -1.5:     ║
  ║    → REVERSE_CARRY (basis is cheap, expect normalization)║
  ║                                                          ║
  ║  IF avg_funding_7d > 0.03% AND positive_rate_pct > 80%: ║
  ║    → FUNDING_RATE_HARVEST (collect delta-neutral income)  ║
  ║                                                          ║
  ║  IF |funding_exchange_A - funding_exchange_B| > 0.05%:   ║
  ║    → CROSS_EXCHANGE_FUNDING_ARB                          ║
  ║                                                          ║
  ║  IF term_structure_inverted AND near_far_spread > 2σ:    ║
  ║    → CALENDAR_SPREAD (sell near, buy far)                ║
  ║                                                          ║
  ║  IF directional_signal_strong AND confidence > 0.8:      ║
  ║    → DIRECTIONAL_FUTURES (with controlled leverage)      ║
  ║                                                          ║
  ║  IF portfolio_has_spot_exposure AND hedge_needed:         ║
  ║    → DELTA_HEDGE (short perp/futures to reduce delta)    ║
  ║                                                          ║
  ║  IF liquidation_cascade_detected:                        ║
  ║    → DEFENSIVE (reduce exposure, widen stops)            ║
  ║                                                          ║
  ╚══════════════════════════════════════════════════════════╝
```

### 5.2 Basis Trading Bot — Complete Execution Flow

```
BASIS_TRADING_BOT:

  ╔══════════════════════════════════════════════════════════╗
  ║  STEP 1: OPPORTUNITY IDENTIFICATION (every 1 minute)     ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  1.1 Calculate annualized basis for all active expiries  ║
  ║  1.2 Calculate basis Z-score (vs 30-day rolling window)  ║
  ║  1.3 Calculate fair basis using cost-of-carry model      ║
  ║  1.4 Identify mispricing: actual_basis - fair_basis      ║
  ║  1.5 Filter: only consider if |mispricing| > threshold   ║
  ║  1.6 Rank opportunities by expected risk-adjusted return ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 2: ENTRY CRITERIA CHECK                           ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  All must pass:                                          ║
  ║  □ Annualized basis > 8% (after costs)                  ║
  ║  □ Basis Z-score > 1.5 (statistically significant)      ║
  ║  □ Days to expiry > 14 (avoid settlement risk)          ║
  ║  □ Sufficient liquidity on both legs                     ║
  ║  □ Portfolio risk limits not breached                    ║
  ║  □ Exchange diversification maintained                   ║
  ║  □ Margin available for both legs                        ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 3: POSITION SIZING                                 ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  3.1 Calculate max position based on:                    ║
  ║      - Risk budget (max loss per trade)                  ║
  ║      - Margin available                                  ║
  ║      - Liquidity (max 1% of OI)                          ║
  ║      - Portfolio concentration limits                    ║
  ║  3.2 Select conservative of all constraints              ║
  ║  3.3 Split evenly between legs:                          ║
  ║      - Spot leg: buy Q units                             ║
  ║      - Futures leg: sell Q contracts                     ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 4: EXECUTION                                       ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  4.1 Execute simultaneously (minimize leg risk):         ║
  ║      a. Submit spot buy limit order (slightly aggressive)║
  ║      b. Submit futures sell limit order (slightly aggress)║
  ║  4.2 If only one leg fills:                              ║
  ║      - Wait 5 seconds for other leg                     ║
  ║      - If still unfilled, convert to market order        ║
  ║      - Maximum acceptable slippage: 0.1%                ║
  ║  4.3 Confirm both legs filled:                           ║
  ║      - Record entry basis = futures_fill - spot_fill     ║
  ║      - Calculate effective annualized return              ║
  ║  4.4 Set margin buffer:                                  ║
  ║      - Transfer additional collateral to futures exchange║
  ║      - Target: survive 30% adverse spot move             ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 5: POSITION MONITORING (continuous)                ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  5.1 Monitor margin utilization (every 1 second)         ║
  ║  5.2 Monitor basis Z-score:                              ║
  ║      - If Z-score < 0.5: consider early exit (basis     ║
  ║        normalized, profit captured)                      ║
  ║      - If Z-score > 3.0: basis widening (MTM loss but   ║
  ║        hold to expiry — will converge)                   ║
  ║  5.3 Monitor liquidation distance:                       ║
  ║      - Alert if < 40%                                    ║
  ║      - Action if < 30%: transfer collateral or reduce    ║
  ║  5.4 Track days to expiry:                               ║
  ║      - At 3 DTE: prepare for settlement                  ║
  ║      - At 1 DTE: confirm settlement procedures           ║
  ║  5.5 Monitor exchange health:                            ║
  ║      - Insurance fund changes                            ║
  ║      - Withdrawal delays                                 ║
  ║      - Unusual activity                                  ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 6: EXIT                                            ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  EXIT CONDITION A: Hold to expiry (default for carry)    ║
  ║    - Futures converge to spot at settlement              ║
  ║    - P&L = Entry basis - transaction costs               ║
  ║    - No action needed; auto-settled                      ║
  ║                                                          ║
  ║  EXIT CONDITION B: Early exit (basis normalized)         ║
  ║    - Basis Z-score dropped to < 0.3 (mean reverted)     ║
  ║    - Close both legs simultaneously                      ║
  ║    - P&L = (Entry basis - Exit basis) - costs            ║
  ║    - Benefit: free capital for next opportunity          ║
  ║                                                          ║
  ║  EXIT CONDITION C: Risk exit (margin pressure)           ║
  ║    - Margin utilization > 75%                            ║
  ║    - Transfer more collateral if possible                ║
  ║    - Otherwise partial close: reduce position 50%        ║
  ║    - ONLY close entire position as last resort           ║
  ║                                                          ║
  ║  EXIT CONDITION D: Roll (if approaching expiry)          ║
  ║    - Close current futures                               ║
  ║    - Open new futures at next expiry                     ║
  ║    - Cost: spread between expiries (roll cost)           ║
  ║    - Only roll if new basis is attractive                 ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 7: POST-TRADE ANALYSIS                             ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  7.1 Record final P&L:                                   ║
  ║      - Basis captured                                    ║
  ║      - Transaction costs (entry + exit)                  ║
  ║      - Funding costs (if perp leg)                       ║
  ║      - Margin opportunity cost                           ║
  ║      - Net return                                        ║
  ║  7.2 Compare to expected return at entry                 ║
  ║  7.3 Update strategy statistics                          ║
  ║  7.4 Identify lessons learned                            ║
  ║                                                          ║
  ╚══════════════════════════════════════════════════════════╝
```

### 5.3 Funding Rate Harvest Bot — Complete Execution Flow

```
FUNDING_RATE_HARVEST_BOT:

  ╔══════════════════════════════════════════════════════════╗
  ║  STEP 1: SCREENING (every 1 hour)                        ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  For each perpetual swap:                                ║
  ║  1.1 Current predicted funding rate                      ║
  ║  1.2 7-day average funding rate                          ║
  ║  1.3 30-day average funding rate                         ║
  ║  1.4 Percentage of time funding was positive (30d)       ║
  ║  1.5 Maximum consecutive negative funding periods        ║
  ║  1.6 Funding rate volatility                             ║
  ║  1.7 Annualized expected return:                         ║
  ║      APR = avg_funding × 3 × 365 - estimated_costs      ║
  ║                                                          ║
  ║  FILTER CRITERIA:                                        ║
  ║  □ 7d avg funding > 0.01% per 8h (>10.95% APR)         ║
  ║  □ Positive funding % > 70% (30-day lookback)           ║
  ║  □ Max consecutive negative < 3 days                     ║
  ║  □ Sufficient liquidity (OI > $100M)                    ║
  ║  □ Manageable volatility (for margin requirements)       ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 2: ENTRY EXECUTION                                 ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  Preferred setup: Long spot + Short perp (same exchange) ║
  ║                                                          ║
  ║  2.1 Calculate position size:                            ║
  ║      - Based on capital allocation to strategy           ║
  ║      - Account for margin on short perp                  ║
  ║      - Ensure liquidation distance > 50%                ║
  ║  2.2 Execute spot buy (limit order at ask - 1 tick)      ║
  ║  2.3 Execute perp short (limit order at bid + 1 tick)    ║
  ║  2.4 Confirm delta-neutral (spot = perp notional)        ║
  ║  2.5 Record entry:                                       ║
  ║      - Entry basis (perp - spot)                         ║
  ║      - Effective funding rate at entry                   ║
  ║      - Total capital deployed                            ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 3: ONGOING MANAGEMENT (continuous)                 ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  3.1 Funding collection tracking:                        ║
  ║      - Record each funding payment received              ║
  ║      - Cumulative funding income                         ║
  ║      - Compare to expected (track divergence)            ║
  ║                                                          ║
  ║  3.2 Margin monitoring:                                  ║
  ║      - If BTC rises: short perp has unrealized loss      ║
  ║        but spot has gain → cross-margin protects         ║
  ║      - If BTC drops: short perp profits but spot loses   ║
  ║        → no margin issue                                 ║
  ║      - Monitor exchange-specific margin rules            ║
  ║                                                          ║
  ║  3.3 Rebalancing:                                        ║
  ║      - If delta drift > 2% of position:                  ║
  ║        adjust spot or perp to re-neutralize             ║
  ║      - Occurs due to funding payments accumulating       ║
  ║        in perp margin (coin-margined effect)            ║
  ║                                                          ║
  ║  3.4 Funding rate deterioration check:                   ║
  ║      - If 7d avg drops below 0.005% (5.5% APR):        ║
  ║        flag for potential exit                           ║
  ║      - If 3 consecutive negative payments:               ║
  ║        exit the position                                 ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 4: EXIT CONDITIONS                                 ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  EXIT IF:                                                ║
  ║  □ 7d avg funding < 0.005% (return below threshold)     ║
  ║  □ 3+ consecutive negative funding payments             ║
  ║  □ Margin utilization > 70%                              ║
  ║  □ Better opportunity identified elsewhere               ║
  ║  □ Exchange risk concerns arise                          ║
  ║  □ Market regime shift to sustained bear (funding flips) ║
  ║                                                          ║
  ║  EXIT EXECUTION:                                         ║
  ║  1. Close perp short (buy back)                          ║
  ║  2. Sell spot                                            ║
  ║  3. Execute simultaneously to minimize leg risk          ║
  ║  4. Record total P&L:                                    ║
  ║     - Cumulative funding received                        ║
  ║     - Basis change (entry vs exit)                       ║
  ║     - Transaction costs                                  ║
  ║     - Net P&L                                            ║
  ║                                                          ║
  ╚══════════════════════════════════════════════════════════╝
```

### 5.4 Directional Futures Trading Flow

```
DIRECTIONAL_FUTURES_FLOW:

  ENTRY:
    1. Directional signal generated (from technical/fundamental analysis module)
    2. Confirm with market structure:
       - Funding rate alignment (positive for longs, negative for shorts)
       - Open interest trend (rising OI + trend = confirmation)
       - Liquidation map (identify clusters to avoid/target)
    3. Select instrument:
       - Perpetual swap: Preferred for short-term (days)
       - Quarterly futures: Preferred if basis is favorable for direction
    4. Position sizing:
       - Risk per trade = 1-2% of portfolio
       - Leverage = Risk / Stop distance
       - Example: 2% risk, 5% stop → 2.5x effective leverage on that position
    5. Execute:
       - Limit order at desired entry
       - Immediate stop-loss order (mark price trigger)
       - Take-profit order (last price trigger)

  MANAGEMENT:
    1. Trail stop-loss as position moves in favor
    2. Take partial profits at predefined levels:
       - 50% at 1R (risk-reward 1:1)
       - 25% at 2R
       - 25% at 3R or trail
    3. Monitor funding cost (if holding perp for days)
    4. Adjust leverage if volatility changes

  EXIT:
    1. Stop-loss hit → close full position
    2. Take-profit levels hit → partial/full close
    3. Signal reversal → close regardless of P&L
    4. Time-based: Close if no movement in 48 hours (dead trade)
    5. Funding accumulation: Close if holding costs > 0.5% of position
```

### 5.5 Emergency Procedures

```
EMERGENCY_PROTOCOLS:

  MARGIN_CALL_RESPONSE:
    trigger: margin_utilization > 70%
    priority: CRITICAL
    actions:
      1. IMMEDIATELY assess which positions are most at risk
      2. Transfer available funds from other sub-accounts
      3. If transfer not possible: reduce highest-leverage position by 50%
      4. If still critical: close all positions except fully hedged
      5. Log all actions taken
      6. Alert: notify operations team
    time_limit: 60 seconds total response time

  EXCHANGE_API_FAILURE:
    trigger: no response for > 10 seconds
    actions:
      1. Switch to backup API endpoint (if available)
      2. Switch to alternative exchange for new orders
      3. Queue position adjustments for when API recovers
      4. Monitor positions via public data feeds (read-only)
      5. If extended (>5 min): manual intervention required
    note: Never assume position was closed if API timed out — verify

  ABNORMAL_FUNDING_SPIKE:
    trigger: |funding_rate| > 0.5% per interval (182% APR)
    actions:
      1. Do NOT enter new funding arb at extreme levels
      2. Review existing positions for margin impact
      3. Extreme positive: Consider going long (squeeze potential)
      4. Extreme negative: Consider going short (capitulation potential)
      5. Wait for normalization before new entries

  LIQUIDATION_CASCADE_DETECTED:
    trigger: liquidation_volume > 3x 30d_average in 1h
    actions:
      1. HALT all new position opening
      2. Do NOT place stop-losses in cascade zone
      3. Verify all existing positions have safe margin
      4. If positions threatened: manually reduce (don't stop-market)
      5. After cascade stabilizes (15-30 min): reassess
      6. Potential contrarian opportunity after exhaustion
```

---

## 6. References

### Academic Literature

1. **Black, F.** (1976). "The Pricing of Commodity Contracts." *Journal of Financial Economics*, 3(1-2), 167-179.
2. **Cox, J.C., Ingersoll, J.E., & Ross, S.A.** (1981). "The Relation between Forward Prices and Futures Prices." *Journal of Financial Economics*, 9(4), 321-346.
3. **Ederington, L.H.** (1979). "The Hedging Performance of the New Futures Markets." *Journal of Finance*, 34(1), 157-170.
4. **Johnson, L.L.** (1960). "The Theory of Hedging and Speculation in Commodity Futures." *Review of Economic Studies*, 27(3), 139-151.
5. **Engle, R.** (2002). "Dynamic Conditional Correlation: A Simple Class of Multivariate GARCH Models." *Journal of Business & Economic Statistics*, 20(3), 339-350.

### Textbooks

6. **Hull, J.C.** (2022). *Options, Futures, and Other Derivatives* (11th Edition). Pearson.
7. **Taleb, N.N.** (1997). *Dynamic Hedging: Managing Vanilla and Exotic Options*. Wiley.
8. **McDonald, R.L.** (2013). *Derivatives Markets* (3rd Edition). Pearson.
9. **Chance, D.M., & Brooks, R.** (2015). *An Introduction to Derivatives and Risk Management* (10th Edition). Cengage.

### Crypto-Specific Resources

10. **BitMEX Research** — Perpetual swap mechanics and funding rate analysis.
11. **Deribit Documentation** — Futures, perpetual swap, and index specifications.
12. **Binance Futures Documentation** — Margin, liquidation, and funding rate mechanics.
13. **Glassnode Academy** — On-chain derivatives analytics and market structure.
14. **The Block Research** — Crypto derivatives market reports and data.
15. **CoinGlass (formerly Bybt)** — Liquidation data, funding rates, open interest.
16. **Laevitas** — Derivatives analytics, basis, and term structure monitoring.
17. **Velo Data** — Funding rates and perpetual swap analytics.

### Exchange Documentation

18. **Binance Futures** — https://www.binance.com/en/futures — Margin modes, liquidation rules.
19. **OKX** — https://www.okx.com — Portfolio margin, futures specifications.
20. **Deribit** — https://www.deribit.com/kb — BTC-PERPETUAL specifications, index methodology.
21. **Bybit** — https://bybit-exchange.github.io/docs — API documentation, contract specs.
22. **CME Group** — https://www.cmegroup.com — Bitcoin/Ether futures specifications.
23. **dYdX** — https://docs.dydx.exchange — Decentralized perp protocol documentation.
24. **Hyperliquid** — https://hyperliquid.gitbook.io — L1 perpetual exchange documentation.

---

> **Note to AI Agents:** This document covers futures and perpetual swap mechanics comprehensively.
> Key operational priorities:
> 1. Liquidation distance must ALWAYS be monitored (every 100ms)
> 2. Funding rate strategies require survival through negative periods
> 3. Basis trades are "safe" only if margin is sufficient to hold to expiry
> 4. Cross-exchange strategies require counterparty risk management
> 5. Leverage should be conservative (effective portfolio < 5x)
> 6. Emergency procedures must execute within 60 seconds
>
> Related documents:
> - `00_overview.md` — General derivatives overview
> - `01_options_strategies.md` — Options strategies for hedging futures risk
> - `05_risk_management_framework.md` — Portfolio-level risk management
