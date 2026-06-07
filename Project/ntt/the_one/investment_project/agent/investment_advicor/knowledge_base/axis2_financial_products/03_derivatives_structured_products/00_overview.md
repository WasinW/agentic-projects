# Derivatives & Structured Products: Overview

> **Axis 2 — Financial Products | Module 03: Derivatives & Structured Products**
> **Document 00 — Overview of Derivatives in Trading**
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

### 1.1 What Are Derivatives?

A derivative is a financial contract whose value is derived from the performance of an underlying asset, index, or rate. In the context of Forex and Cryptocurrency trading, derivatives serve as essential instruments for hedging, speculation, yield enhancement, and portfolio optimization.

The derivative market globally exceeds $600 trillion in notional value (BIS, 2025), with crypto derivatives now representing over 70% of total crypto trading volume across major exchanges.

### 1.2 Types of Derivatives

#### 1.2.1 Futures Contracts

A futures contract is a standardized agreement to buy or sell an asset at a predetermined price at a specified time in the future.

**Key Characteristics:**
- **Standardized**: Exchange-defined contract sizes, expiration dates, and settlement procedures
- **Margined**: Requires initial margin and maintenance margin; subject to daily mark-to-market
- **Settlement**: Physical delivery or cash settlement
- **Expiration**: Fixed expiry dates (quarterly for crypto: March, June, September, December on major exchanges)
- **Counterparty Risk**: Mitigated through clearing houses (traditional) or insurance funds (crypto)

**Forex Futures:**
- Traded on CME, ICE, and other regulated exchanges
- Contract sizes standardized (e.g., EUR/USD = 125,000 EUR per contract)
- Used extensively by corporates for hedging FX exposure

**Crypto Futures:**
- Available on Binance, Deribit, CME, OKX, Bybit
- Contract sizes vary (e.g., 1 BTC, 0.001 BTC for micro contracts)
- Both coin-margined and USDT/USDC-margined variants
- Inverse contracts: margin and settlement in the underlying crypto
- Linear contracts: margin and settlement in stablecoin (USDT/USDC)

#### 1.2.2 Options Contracts

An option gives the holder the right, but not the obligation, to buy (call) or sell (put) an underlying asset at a specified strike price before or at expiration.

**Key Characteristics:**
- **Premium**: Buyer pays premium; seller receives premium
- **Asymmetric Payoff**: Limited downside for buyer, limited upside for seller
- **Greeks**: Sensitivity measures (Delta, Gamma, Theta, Vega, Rho)
- **Implied Volatility**: Market's expectation of future volatility embedded in option prices

**Forex Options:**
- OTC market dominates (interbank)
- Standardized on exchanges (CME, PHLX)
- Commonly quoted in terms of delta (25-delta risk reversal, etc.)
- Barrier options widely used in FX (knock-in, knock-out)

**Crypto Options:**
- Deribit dominates (>85% market share for BTC/ETH options)
- European-style (exercisable only at expiry)
- Cash-settled in the underlying crypto
- Growing DeFi options protocols (Lyra, Hegic, Dopex, Ribbon Finance)
- IV significantly higher than traditional markets (BTC: 50-120% annualized vs S&P 500: 15-30%)

#### 1.2.3 Perpetual Swaps (Perpetual Futures)

Perpetual swaps are unique to cryptocurrency markets — futures contracts with no expiration date, maintained through a funding rate mechanism.

**Key Characteristics:**
- **No Expiry**: Trade continuously without rollover
- **Funding Rate**: Periodic payment between longs and shorts to anchor price to spot
- **Leverage**: Typically 1x-125x available
- **Mark Price**: Used for liquidation calculations, derived from index price
- **Dominant Instrument**: >60% of total crypto derivatives volume

**Funding Rate Mechanism:**
- Positive funding rate: Longs pay shorts (market is bullish/premium)
- Negative funding rate: Shorts pay longs (market is bearish/discount)
- Typically settled every 8 hours (Binance, OKX) or continuously (dYdX)
- Annualized funding rates can range from -100% to +200% in extreme conditions

#### 1.2.4 Structured Products

Structured products combine multiple derivative instruments to create customized risk-return profiles.

**Traditional Structured Products:**
- Principal Protected Notes (PPN)
- Capital-at-risk products
- Autocallable notes
- Range accrual notes

**Crypto Structured Products:**
- DeFi Options Vaults (DOV): Ribbon Finance, Friktion, Katana
- Dual Investment Products: Binance, OKX, Bybit
- Shark Fin Products: Binance Earn, OKX Earn
- Snowball Products: Matrixport, Babel Finance
- Accumulator/Decumulator structures

### 1.3 Role of Derivatives in Portfolio Management

#### 1.3.1 Hedging

Derivatives are the primary tool for managing portfolio risk:

| Hedging Objective | Instrument | Strategy |
|---|---|---|
| Downside protection | Put options | Protective put |
| Lock in sell price | Short futures | Forward hedge |
| Reduce cost of hedge | Collar (put + covered call) | Zero-cost collar |
| Tail risk protection | OTM put options | Tail hedge |
| Delta neutralization | Perpetual swaps | Delta hedge |
| Volatility hedging | Variance swaps | Vega hedge |

#### 1.3.2 Speculation

Derivatives provide leveraged exposure to directional and non-directional views:

- **Directional**: Long/short futures, call/put buying
- **Volatility**: Straddles, strangles, calendar spreads
- **Carry**: Funding rate arbitrage, basis trading
- **Relative Value**: Spread trades between correlated assets

#### 1.3.3 Yield Enhancement

Systematic premium collection strategies:

- **Covered Call Writing**: Sell calls against long positions
- **Cash-Secured Put Selling**: Sell puts with cash collateral
- **DOV Participation**: Automated vault strategies for premium income
- **Funding Rate Harvesting**: Collect positive funding on delta-hedged positions

#### 1.3.4 Capital Efficiency

- Futures and swaps provide synthetic exposure without full capital deployment
- Options allow defined-risk positions with known maximum loss
- Cross-margin systems allow portfolio-level margin optimization

### 1.4 Greeks Overview

The Greeks measure the sensitivity of a derivative's price to various factors:

| Greek | Symbol | Measures | Formula | Typical Range |
|---|---|---|---|---|
| Delta | Δ | Price sensitivity to underlying | ∂V/∂S | -1 to +1 |
| Gamma | Γ | Rate of change of delta | ∂²V/∂S² | Always positive for long options |
| Theta | Θ | Time decay | ∂V/∂t | Negative for long options |
| Vega | ν | Volatility sensitivity | ∂V/∂σ | Positive for long options |
| Rho | ρ | Interest rate sensitivity | ∂V/∂r | Positive for calls, negative for puts |
| Vanna | | Delta sensitivity to volatility | ∂²V/∂S∂σ | Varies |
| Charm | | Delta sensitivity to time | ∂²V/∂S∂t | Varies |
| Volga/Vomma | | Vega sensitivity to volatility | ∂²V/∂σ² | Varies |

**Portfolio-Level Greeks:**
- Portfolio delta = Σ (position_i × delta_i)
- Portfolio gamma = Σ (position_i × gamma_i)
- Portfolio theta = Σ (position_i × theta_i)
- Portfolio vega = Σ (position_i × vega_i)

### 1.5 Derivatives in Crypto vs Traditional Markets

| Feature | Traditional (Forex) | Crypto |
|---|---|---|
| **Trading Hours** | 24/5 (Sunday 5PM - Friday 5PM ET) | 24/7/365 |
| **Settlement** | T+2 for spot, daily for futures | Near-instant for spot, real-time for perps |
| **Regulation** | Heavily regulated (CFTC, SEC, FCA) | Varies by jurisdiction; largely unregulated |
| **Counterparty Risk** | Clearing house guarantee | Exchange insurance fund / smart contract risk |
| **Volatility** | Low (EUR/USD: 6-10% annualized) | Very high (BTC: 50-80% annualized) |
| **Leverage** | 50:1 retail (US), 500:1 offshore | 1x-125x (exchange dependent) |
| **Options Style** | Both American and European | Predominantly European |
| **Perpetual Swaps** | Not available | Dominant instrument |
| **Funding Rate** | Not applicable (swap/rollover instead) | Core mechanism |
| **Implied Volatility** | Lower, mean-reverting | Higher, with extreme spikes |
| **Liquidity** | Deep (>$6T daily FX spot) | Growing but thinner, fragmented |
| **Market Maturity** | Decades of data and research | <15 years of data |
| **DeFi Integration** | Not applicable | Composable on-chain derivatives |
| **Option IV Smile** | Risk reversal skew dominant | Strong put skew + high overall IV |
| **Liquidation** | Margin call → time to add funds | Automatic, instant liquidation |

### 1.6 Key Differences That Impact Trading Algorithms

**For the AI Trading System, the following crypto-specific factors require dedicated handling:**

1. **24/7 Markets**: No market close, no overnight gaps (but weekend liquidity can thin)
2. **Funding Rate Alpha**: Unique to crypto; must be factored into carry strategies
3. **Higher Base Volatility**: Wider stop-losses, adjusted position sizing
4. **Liquidation Cascades**: Can cause flash crashes; must monitor liquidation levels
5. **Exchange Fragmentation**: Price differences across venues create arb opportunities
6. **Smart Contract Risk**: DeFi derivatives carry code risk in addition to market risk
7. **Regulatory Uncertainty**: Position limits and instrument availability can change rapidly
8. **Correlation Regime Changes**: Crypto-TradFi correlations shift dramatically in crises

---

## 2. Technical Specifications

### 2.1 Data Requirements for Derivative Trading

```
DERIVATIVE_DATA_SOURCES:
  market_data:
    - spot_price: Real-time underlying price (multiple sources for TWAP/VWAP)
    - order_book: L2/L3 book depth for options and futures
    - trades: Tick-level trade data
    - funding_rate: Current and historical funding rates (8h intervals)
    - open_interest: By strike, expiry, and direction
    - implied_volatility: IV surface (by strike × expiry)
    - realized_volatility: Historical volatility (various windows)

  reference_data:
    - contract_specs: Tick size, lot size, margin requirements
    - expiry_calendar: All active expiration dates
    - strike_grid: Available strikes per expiry
    - settlement_rules: Cash vs physical, settlement time
    - fee_schedule: Maker/taker fees per instrument type

  risk_data:
    - mark_price: Exchange-calculated fair price
    - index_price: Composite spot index
    - liquidation_map: Estimated liquidation levels by price
    - insurance_fund: Exchange insurance fund balance
    - maximum_leverage: Per-instrument leverage limits
```

### 2.2 System Architecture for Derivative Trading

```
┌─────────────────────────────────────────────────────────────┐
│                    DERIVATIVE TRADING ENGINE                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │  Market Data │  │  Volatility  │  │  Greeks Engine     │  │
│  │  Aggregator  │──│  Surface     │──│  (Real-time calc)  │  │
│  │             │  │  Builder     │  │                    │  │
│  └──────┬──────┘  └──────┬───────┘  └─────────┬──────────┘  │
│         │                │                     │              │
│  ┌──────▼────────────────▼─────────────────────▼──────────┐  │
│  │              STRATEGY EVALUATION ENGINE                  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │  │
│  │  │ Options  │ │ Futures  │ │ Perp     │ │Structured│  │  │
│  │  │Strategies│ │Strategies│ │Strategies│ │ Products │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │  │
│  └───────────────────────┬─────────────────────────────────┘  │
│                          │                                    │
│  ┌───────────────────────▼─────────────────────────────────┐  │
│  │              RISK MANAGEMENT LAYER                       │  │
│  │  - Position sizing (Kelly/Fractional)                    │  │
│  │  - Portfolio Greeks management                           │  │
│  │  - VaR / CVaR monitoring                                │  │
│  │  - Liquidation distance monitoring                      │  │
│  │  - Correlation risk tracking                            │  │
│  └───────────────────────┬─────────────────────────────────┘  │
│                          │                                    │
│  ┌───────────────────────▼─────────────────────────────────┐  │
│  │              ORDER EXECUTION ENGINE                      │  │
│  │  - Smart order routing                                  │  │
│  │  - Multi-leg execution                                  │  │
│  │  - Slippage management                                  │  │
│  │  - Exchange API integration                             │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Supported Exchanges and Instruments

```
EXCHANGE_CONFIGURATION:
  deribit:
    instruments: [options, futures]
    assets: [BTC, ETH]
    options_style: European
    settlement: crypto
    api_rate_limit: 20 req/s
    websocket: wss://www.deribit.com/ws/api/v2

  binance:
    instruments: [futures, perpetual_swaps]
    assets: [BTC, ETH, +200 altcoins]
    margin_types: [USDT, BUSD, coin-margined]
    max_leverage: 125x
    api_rate_limit: 1200 req/min

  okx:
    instruments: [options, futures, perpetual_swaps, structured_products]
    assets: [BTC, ETH, SOL, +100 altcoins]
    margin_modes: [cross, isolated, portfolio]
    api_rate_limit: 60 req/2s

  cme:
    instruments: [futures, options]
    assets: [BTC, ETH, major FX pairs]
    settlement: cash (crypto), physical (FX)
    regulated: true
    margin_type: portfolio margin (SPAN)

  bybit:
    instruments: [perpetual_swaps, futures, options]
    assets: [BTC, ETH, +200 altcoins]
    margin_types: [USDT, USDC, inverse]
    max_leverage: 100x

  forex_exchanges:
    instruments: [spot, forwards, options, swaps]
    platforms: [EBS, Reuters Matching, Currenex, Hotspot]
    settlement: T+2
```

### 2.4 Performance Requirements

```
PERFORMANCE_SPECS:
  latency:
    market_data_processing: <5ms
    greeks_calculation: <10ms per position
    portfolio_greeks: <50ms for full portfolio
    vol_surface_rebuild: <200ms
    risk_check: <20ms
    order_submission: <50ms

  throughput:
    market_data_updates: 10,000+ events/second
    greeks_recalculation: Every 100ms for active positions
    risk_monitoring: Continuous, real-time
    position_reconciliation: Every 1 second

  availability:
    uptime_target: 99.99%
    failover_time: <5 seconds
    data_backup: Real-time replication
```

---

## 3. Mathematical Models

### 3.1 Derivative Pricing Foundations

The fundamental theorem of asset pricing states that in an arbitrage-free market, there exists a risk-neutral probability measure $\mathbb{Q}$ such that the price of any derivative is the discounted expected payoff:

$$V_0 = e^{-rT} \mathbb{E}^{\mathbb{Q}}[\text{Payoff}(S_T)]$$

### 3.2 Black-Scholes-Merton Framework

Under the Black-Scholes assumptions (geometric Brownian motion, constant volatility, continuous trading), the underlying follows:

$$dS = \mu S \, dt + \sigma S \, dW$$

Under the risk-neutral measure:

$$dS = rS \, dt + \sigma S \, dW^{\mathbb{Q}}$$

**European Call Option Price:**

$$C = S_0 N(d_1) - Ke^{-rT}N(d_2)$$

**European Put Option Price:**

$$P = Ke^{-rT}N(-d_2) - S_0 N(-d_1)$$

Where:

$$d_1 = \frac{\ln(S_0/K) + (r + \sigma^2/2)T}{\sigma\sqrt{T}}$$

$$d_2 = d_1 - \sigma\sqrt{T}$$

### 3.3 Futures Pricing

**Cost of Carry Model:**

$$F_0 = S_0 \times e^{(r - q)T}$$

Where:
- $F_0$ = Futures price
- $S_0$ = Spot price
- $r$ = Risk-free rate
- $q$ = Convenience yield (or staking yield in crypto)
- $T$ = Time to expiration

**Crypto Futures Fair Value (with staking yield):**

$$F_0 = S_0 \times e^{(r_{borrow} - y_{staking})T}$$

### 3.4 Perpetual Swap Pricing

The perpetual swap price $P_{perp}$ is anchored to spot through the funding rate:

$$\text{Funding Rate} = \text{Premium Index} + \text{clamp}(\text{Interest Rate} - \text{Premium Index}, -0.05\%, 0.05\%)$$

$$\text{Premium Index} = \frac{\text{Max}(0, \text{Impact Bid} - P_{index}) - \text{Max}(0, P_{index} - \text{Impact Ask})}{P_{index}}$$

**Funding Payment:**

$$\text{Payment} = \text{Position Value} \times \text{Funding Rate}$$

### 3.5 Greeks Formulas

$$\Delta_{call} = N(d_1), \quad \Delta_{put} = N(d_1) - 1$$

$$\Gamma = \frac{N'(d_1)}{S_0 \sigma \sqrt{T}}$$

$$\Theta_{call} = -\frac{S_0 N'(d_1) \sigma}{2\sqrt{T}} - rKe^{-rT}N(d_2)$$

$$\nu = S_0 \sqrt{T} N'(d_1)$$

$$\rho_{call} = KTe^{-rT}N(d_2)$$

Where $N'(x) = \frac{1}{\sqrt{2\pi}}e^{-x^2/2}$ is the standard normal PDF.

### 3.6 Implied Volatility Extraction

Implied volatility $\sigma_{imp}$ is found by numerically solving:

$$C_{market} = BSM(S_0, K, T, r, \sigma_{imp})$$

Common numerical methods:
- **Newton-Raphson**: $\sigma_{n+1} = \sigma_n - \frac{C_{BSM}(\sigma_n) - C_{market}}{\text{Vega}(\sigma_n)}$
- **Brent's Method**: Bracketed root-finding (more robust)
- **Rational Approximation**: Let It Be (Jaeckel, 2017) for near-instant computation

---

## 4. Risk Parameters

### 4.1 Portfolio-Level Risk Limits

```
RISK_PARAMETERS:
  position_limits:
    max_single_position_pct: 10%       # of portfolio
    max_derivatives_exposure: 200%      # notional as % of NAV
    max_options_premium_at_risk: 5%     # of portfolio per trade
    max_futures_leverage: 5x            # effective portfolio leverage
    max_perp_leverage: 3x              # conservative for bot
    max_concentrated_strike: 20%        # of OI at any single strike

  greeks_limits:
    max_portfolio_delta: 0.3            # as fraction of portfolio
    max_portfolio_gamma: 0.05           # per 1% move
    max_portfolio_vega: 2%              # of portfolio per 1 vol point
    max_portfolio_theta: -0.5%          # daily time decay as % of portfolio
    max_single_name_delta: 0.15         # per underlying

  loss_limits:
    max_daily_loss: 3%                  # of portfolio
    max_weekly_loss: 7%                 # of portfolio
    max_monthly_loss: 15%               # of portfolio
    max_drawdown_hard_stop: 25%         # from peak
    max_single_trade_loss: 2%           # of portfolio

  volatility_limits:
    min_iv_rank_for_selling: 30         # percentile
    max_iv_rank_for_buying: 70          # percentile
    max_vega_exposure_event: 50%        # reduce before events
    min_days_to_expiry_sell: 7          # don't sell very short-dated

  liquidation_safety:
    min_margin_ratio: 50%               # maintain 50%+ of initial margin
    liquidation_distance_min: 30%       # price must move 30%+ to liquidate
    auto_deleverage_threshold: 40%      # reduce at 40% margin usage
```

### 4.2 Risk Monitoring Dashboard Metrics

```
MONITORING_METRICS:
  real_time:
    - portfolio_delta_dollars
    - portfolio_gamma_dollars_per_1pct
    - portfolio_theta_daily
    - portfolio_vega_per_vol_point
    - margin_utilization_pct
    - liquidation_distance_pct
    - unrealized_pnl
    - funding_rate_exposure
    - max_loss_scenario (3σ move)

  periodic (every 1 hour):
    - VaR_95_1day
    - CVaR_95_1day
    - correlation_matrix_update
    - volatility_surface_fit_quality
    - basis_vs_fair_value

  daily:
    - realized_pnl_attribution (delta, gamma, theta, vega, rho)
    - sharpe_ratio_rolling_30d
    - max_drawdown_current
    - win_rate_by_strategy
    - avg_holding_period
```

### 4.3 Scenario Analysis

```
STRESS_SCENARIOS:
  crypto_crash:
    btc_move: -30%
    eth_move: -40%
    altcoin_move: -50%
    iv_change: +50 vol points
    funding_rate: -0.1% per 8h
    correlation: 0.95 (all crypto)

  crypto_rally:
    btc_move: +30%
    eth_move: +40%
    altcoin_move: +60%
    iv_change: -10 vol points
    funding_rate: +0.2% per 8h

  vol_explosion:
    spot_move: ±5%
    iv_change: +80 vol points
    term_structure: inverted
    skew_change: +15 points put skew

  liquidity_crisis:
    bid_ask_spread: 5x normal
    order_book_depth: -80%
    exchange_outage_probability: 20%
    liquidation_cascade: active

  fx_black_swan:
    eur_usd_move: ±5% (single day)
    usd_jpy_move: ±8% (single day)
    vol_spike: +200% from baseline
    correlation_break: historical correlations fail
```

---

## 5. Execution Flow

### 5.1 Master Derivative Strategy Selection Flow

```
DERIVATIVE_STRATEGY_SELECTION:

  Step 1: MARKET REGIME IDENTIFICATION
    ├── Collect: spot price, IV surface, funding rates, OI, volume
    ├── Classify regime:
    │   ├── TRENDING_UP: Strong directional bullish momentum
    │   ├── TRENDING_DOWN: Strong directional bearish momentum
    │   ├── RANGE_BOUND: Low volatility, mean-reverting
    │   ├── HIGH_VOLATILITY: Elevated IV, potential breakout
    │   ├── LOW_VOLATILITY: Compressed IV, breakout imminent
    │   └── CRISIS: Extreme moves, liquidation cascades
    └── Output: regime_label, confidence_score

  Step 2: OPPORTUNITY SCREENING
    ├── Scan IV Rank/Percentile across all underlyings
    ├── Identify funding rate anomalies
    ├── Check basis (futures premium/discount)
    ├── Monitor term structure shape (contango/backwardation)
    ├── Evaluate put-call skew
    └── Score each opportunity: [0.0 - 1.0]

  Step 3: STRATEGY MAPPING
    ├── IF regime == TRENDING_UP AND iv_rank < 30:
    │   → Long Call, Bull Call Spread, Short Cash-Secured Put
    ├── IF regime == TRENDING_DOWN AND iv_rank < 30:
    │   → Long Put, Bear Put Spread, Protective Put
    ├── IF regime == RANGE_BOUND AND iv_rank > 50:
    │   → Iron Condor, Short Strangle, Short Straddle
    ├── IF regime == HIGH_VOLATILITY AND iv_rank > 70:
    │   → Sell premium: Iron Condor, Covered Call, DOV
    ├── IF regime == LOW_VOLATILITY AND iv_rank < 20:
    │   → Buy premium: Long Straddle, Long Strangle, Calendar
    ├── IF funding_rate_anomaly:
    │   → Basis trade, Funding rate arbitrage
    └── IF crisis:
        → Hedge existing, tail hedges, reduce exposure

  Step 4: POSITION SIZING
    ├── Calculate Kelly fraction for selected strategy
    ├── Apply fractional Kelly (typically 0.25-0.5x full Kelly)
    ├── Check against all risk limits
    ├── Verify margin requirements
    └── Output: position_size, number_of_contracts

  Step 5: EXECUTION
    ├── Check liquidity at target strikes/expiries
    ├── Use limit orders with smart routing
    ├── For multi-leg strategies: simultaneous execution preferred
    ├── Monitor fill quality and adjust
    └── Confirm all legs filled, log trade

  Step 6: MONITORING & MANAGEMENT
    ├── Continuous Greeks monitoring
    ├── Profit target check (typically 50% of max profit for credit spreads)
    ├── Stop loss check (typically 200% of credit received)
    ├── Time-based exit (close at 21 DTE if opened at 45 DTE)
    ├── Adjustment triggers:
    │   ├── Delta breach: Roll or add hedge
    │   ├── Gamma risk: Reduce near expiry
    │   ├── Vega risk: Adjust if IV regime changes
    │   └── Theta: Harvest or exit
    └── Log all adjustments with reasoning
```

### 5.2 Derivative Lifecycle Management

```
LIFECYCLE_FLOW:

  INITIATION:
    1. Strategy signal generated
    2. Risk pre-check passed
    3. Order constructed (all legs)
    4. Margin verified
    5. Order submitted

  ACTIVE_MANAGEMENT:
    1. Real-time P&L tracking
    2. Greeks monitoring (every 100ms)
    3. Funding rate collection/payment tracking
    4. Margin monitoring
    5. Event calendar awareness (expiry, settlement, announcements)

  EXIT:
    1. Profit target reached → close all legs
    2. Stop loss triggered → close all legs
    3. Time exit → close before expiry risk
    4. Forced exit → margin call / liquidation proximity
    5. Strategy invalidation → regime change detected

  POST-TRADE:
    1. Record actual vs expected P&L
    2. Analyze slippage and execution quality
    3. Update strategy performance statistics
    4. Feed results to ML model for parameter optimization
    5. Adjust risk parameters if needed
```

### 5.3 Emergency Procedures

```
EMERGENCY_PROTOCOLS:

  LIQUIDATION_PROXIMITY:
    trigger: margin_ratio < 40%
    action:
      1. Alert: CRITICAL
      2. Reduce position by 50% immediately (market orders)
      3. Close most leveraged positions first
      4. Transfer additional collateral if available
      5. Halt new position opening

  EXCHANGE_OUTAGE:
    trigger: API connection lost > 30 seconds
    action:
      1. Switch to backup exchange if available
      2. Queue pending orders for retry
      3. Calculate exposure without real-time data
      4. Prepare hedges on alternative venues
      5. Alert operations team

  FLASH_CRASH:
    trigger: >10% move in <5 minutes
    action:
      1. Halt all new orders
      2. Verify positions and margin
      3. Do NOT panic-sell into cascading liquidations
      4. Wait for price stabilization (5-15 min)
      5. Assess damage, adjust hedges
      6. Resume only after volatility normalizes

  BLACK_SWAN:
    trigger: >20% move in <1 hour
    action:
      1. Full system halt
      2. Manual override required
      3. Close all leveraged positions
      4. Maintain only hedged/covered positions
      5. Do not re-enter for minimum 24 hours
```

---

## 6. References

### Academic Literature

1. **Black, F., & Scholes, M.** (1973). "The Pricing of Options and Corporate Liabilities." *Journal of Political Economy*, 81(3), 637-654.
2. **Merton, R.C.** (1973). "Theory of Rational Option Pricing." *Bell Journal of Economics and Management Science*, 4(1), 141-183.
3. **Cox, J.C., Ross, S.A., & Rubinstein, M.** (1979). "Option Pricing: A Simplified Approach." *Journal of Financial Economics*, 7(3), 229-263.
4. **Heston, S.L.** (1993). "A Closed-Form Solution for Options with Stochastic Volatility with Applications to Bond and Currency Options." *Review of Financial Studies*, 6(2), 327-343.
5. **Dupire, B.** (1994). "Pricing with a Smile." *Risk*, 7(1), 18-20.

### Textbooks

6. **Hull, J.C.** (2022). *Options, Futures, and Other Derivatives* (11th Edition). Pearson.
7. **Natenberg, S.** (2015). *Option Volatility and Pricing* (2nd Edition). McGraw-Hill.
8. **Taleb, N.N.** (1997). *Dynamic Hedging: Managing Vanilla and Exotic Options*. Wiley.
9. **Sinclair, E.** (2013). *Volatility Trading* (2nd Edition). Wiley.
10. **Haug, E.G.** (2007). *The Complete Guide to Option Pricing Formulas* (2nd Edition). McGraw-Hill.

### Crypto-Specific Resources

11. **Deribit Documentation** — Options and Futures specifications. https://www.deribit.com/kb
12. **Binance Futures Documentation** — Perpetual swap mechanics. https://www.binance.com/en/support
13. **Paradigm Protocol** — Institutional crypto options trading.
14. **Amberdata Derivatives** — Crypto derivatives analytics and data.
15. **Laevitas Analytics** — Crypto options flow and Greeks monitoring.
16. **The Block Research** — Crypto derivatives market structure reports.

### Exchange Documentation

17. **CME Group** — Bitcoin and Ether futures/options specifications.
18. **OKX** — Structured products and derivatives documentation.
19. **Bybit** — Perpetual swap and options documentation.
20. **dYdX** — Decentralized perpetual swap protocol documentation.

---

> **Note to AI Agents:** This document serves as the foundational overview for the derivatives module.
> Detailed implementation for each derivative type is covered in subsequent documents:
> - `01_options_strategies.md` — Comprehensive options strategies
> - `02_futures_perpetual_swaps.md` — Futures and perpetual swap trading
> - `03_structured_products.md` — Structured products and exotic strategies
> - `04_volatility_trading.md` — Volatility trading framework
> - `05_risk_management_framework.md` — Portfolio risk management
>
> All strategies must pass through the risk management framework before execution.
> Position sizing must use Kelly Criterion with fractional adjustment.
> Emergency procedures override all strategy logic.
