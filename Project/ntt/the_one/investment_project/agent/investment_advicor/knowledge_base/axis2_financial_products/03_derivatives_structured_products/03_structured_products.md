# Structured Products & Exotic Strategies

> **Axis 2 — Financial Products | Module 03: Derivatives & Structured Products**
> **Document 03 — Structured Products & Exotic Strategies**
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

### 1.1 Introduction to Structured Products

Structured products are pre-packaged investment strategies that combine derivatives with traditional assets to create customized risk-return profiles. In cryptocurrency markets, these products have experienced explosive growth, particularly through DeFi protocols and CeFi platforms.

**Market Size (2026 Estimates):**
- Global structured products market: >$7 trillion notional
- Crypto structured products: >$50 billion TVL (CeFi + DeFi combined)
- Growth driver: Demand for yield in a high-volatility, low-yield environment

**Key Value Propositions:**
1. **Yield Enhancement**: Generate returns above passive holding
2. **Risk Shaping**: Customize payoff profiles to specific market views
3. **Capital Protection**: Partial or full principal protection structures
4. **Complexity Packaging**: Complex strategies made accessible as single products

### 1.2 DeFi Options Vaults (DOV)

#### 1.2.1 Overview

DeFi Options Vaults are automated smart-contract-based products that execute systematic options selling strategies on behalf of depositors.

**How DOVs Work:**
1. Users deposit crypto assets (BTC, ETH, USDC) into a vault
2. The vault sells options (typically weekly OTM covered calls or cash-secured puts)
3. Premium income is distributed to depositors
4. Process repeats each cycle (weekly, bi-weekly)

**Major DOV Protocols:**
- **Ribbon Finance**: Pioneer of DOVs, largest TVL historically
- **Friktion** (Solana): Multiple vault strategies
- **Dopex** (Arbitrum): Atlantic options, SSOV
- **Lyra** (Optimism/Arbitrum): AMM-based options with vaults
- **Thetanuts**: Multi-chain structured products
- **Cega**: Exotic structured products on-chain

#### 1.2.2 Covered Call DOV

**Strategy:** Vault holds the underlying crypto and sells weekly OTM calls.

**Mechanics:**
1. Deposit 1 BTC into vault
2. Vault sells 1 BTC call option (typically 10-20% OTM, 7-day expiry)
3. If BTC stays below strike: Option expires worthless, vault keeps premium
4. If BTC exceeds strike: Option exercised, vault delivers BTC at strike price

**Payoff per Cycle:**

$$\text{Return}_{cycle} = \begin{cases} \frac{Premium}{NAV} & \text{if } S_T \leq K \\ \frac{Premium - (S_T - K)}{NAV} & \text{if } S_T > K \end{cases}$$

**Annualized Yield:**

$$APY_{DOV} = \left(1 + r_{cycle}\right)^{52} - 1$$

Where $r_{cycle}$ is the weekly return.

**Typical Performance:**
- Weekly premium: 0.5-3% of NAV (depending on IV and strike)
- Annualized: 25-100%+ nominal (but must account for opportunity cost of capped upside)
- Risk: Underperforms buy-and-hold in strong rallies

#### 1.2.3 Put-Selling DOV

**Strategy:** Vault holds stablecoins and sells weekly OTM puts.

**Mechanics:**
1. Deposit USDC into vault
2. Vault sells BTC/ETH put options (10-20% OTM, 7-day expiry)
3. If BTC stays above strike: Put expires worthless, keep premium
4. If BTC falls below strike: Vault is obligated to buy BTC at strike (loss on assigned value)

**Payoff per Cycle:**

$$\text{Return}_{cycle} = \begin{cases} \frac{Premium}{Capital} & \text{if } S_T \geq K \\ \frac{Premium - (K - S_T)}{Capital} & \text{if } S_T < K \end{cases}$$

**Risk:** Can suffer significant losses during market crashes (selling downside protection in already volatile markets).

### 1.3 Dual Investment Products

#### 1.3.1 Overview

Dual Investment (also called "Dual Currency" or "Win-Win") products let users set a target buy or sell price with enhanced yield. Available on Binance, OKX, Bybit, and others.

**Concept:** Users deposit crypto or stablecoins and set a strike price. They receive enhanced yield regardless of outcome, but the settlement currency depends on whether the strike is reached.

#### 1.3.2 "Sell High" (Covered Call Equivalent)

**Construction:**
- Deposit: BTC
- Strike: Above current spot (e.g., BTC at $60K, strike at $65K)
- Expiry: 1-7 days typically

**Outcomes:**
- If $S_T < K$: Receive BTC back + premium (in BTC)
- If $S_T \geq K$: Receive USDT at strike price + premium (sold BTC at target)

**Payoff:**

$$\text{Return (BTC)} = \begin{cases} BTC_{deposited} \times (1 + APY \times T/365) & \text{if } S_T < K \\ \frac{BTC_{deposited} \times K \times (1 + APY \times T/365)}{S_T} \text{ (in USDT)} & \text{if } S_T \geq K \end{cases}$$

#### 1.3.3 "Buy Low" (Cash-Secured Put Equivalent)

**Construction:**
- Deposit: USDT
- Strike: Below current spot (e.g., BTC at $60K, strike at $55K)
- Expiry: 1-7 days

**Outcomes:**
- If $S_T > K$: Receive USDT back + premium (in USDT)
- If $S_T \leq K$: Receive BTC at strike price + premium equivalent (bought BTC at discount + yield)

**Payoff:**

$$\text{Return (USDT)} = \begin{cases} USDT_{deposited} \times (1 + APY \times T/365) & \text{if } S_T > K \\ \frac{USDT_{deposited} \times (1 + APY \times T/365)}{K} \text{ (in BTC)} & \text{if } S_T \leq K \end{cases}$$

#### 1.3.4 When to Use

- **Sell High**: When you want to accumulate USDT at a target higher price with enhanced yield
- **Buy Low**: When you want to accumulate BTC at a lower price with enhanced yield
- **DCA Enhancement**: Use as systematic strategy alongside DCA for improved entry/exit

### 1.4 Shark Fin Products

#### 1.4.1 Overview

Shark Fin products are principal-protected or enhanced-yield structures with a "knocked-out" upside. Named for the shape of the payoff diagram (resembles a shark's dorsal fin).

**Structure:** Combines a zero-coupon bond (or principal protection) with a knock-out barrier option.

#### 1.4.2 Bullish Shark Fin

**Construction:**
- Buy zero-coupon component (principal protection)
- Buy an up-and-out call option with:
  - Strike $K_1$ (near ATM or slightly OTM)
  - Barrier $K_2$ (upper barrier, $K_2 > K_1$)

**Payoff:**

$$\text{Return} = \begin{cases} r_{base} & \text{if } S_T \leq K_1 \text{ (below strike)} \\ r_{base} + (r_{max} - r_{base}) \times \frac{S_T - K_1}{K_2 - K_1} & \text{if } K_1 < S_T < K_2 \text{ (in the fin)} \\ r_{base} & \text{if } S_T \geq K_2 \text{ (barrier knocked out)} \end{cases}$$

Where:
- $r_{base}$ = Guaranteed minimum return (e.g., 1-3%)
- $r_{max}$ = Maximum enhanced return (e.g., 20-50% annualized)

**Payoff Diagram:**
```
Return
  │        /\
  │       /  \
r_max   /    \
  │    /      \___________
  │   /
r_base ─────────────────── Barrier knocked
  │
──┼────K1────K2──────────── Price
```

**Key Feature:** If the price rallies too strongly (breaks barrier), the enhanced return is knocked out, and only the base return is received. This makes the product cheaper to construct.

#### 1.4.3 Bearish Shark Fin

**Construction:** Same concept but with a down-and-out put:
- Strike $K_1$ (near ATM or slightly OTM put)
- Barrier $K_2$ (lower barrier, $K_2 < K_1$)
- Enhanced return as price falls toward barrier
- Knocked out if price crashes below barrier

**When to Use:**
- Mild directional view (bullish/bearish but not extreme)
- Want principal protection
- Accept capped upside in exchange for guaranteed minimum
- Believe volatility will be moderate (not break barriers)

### 1.5 Snowball Structured Products

#### 1.5.1 Overview

Snowball products (popular in Asia, rapidly growing in crypto) are autocallable structures that pay enhanced yield as long as the underlying stays above a "knock-in" barrier. If the barrier is breached, the investor has downside exposure.

**Structure:**
- Autocall barrier: $K_{auto}$ (above entry, e.g., 103% of spot)
- Knock-in barrier: $K_{in}$ (below entry, e.g., 75% of spot)
- Coupon: Enhanced yield paid periodically (e.g., 2-4% per month)
- Observation dates: Monthly (or weekly)
- Term: 3-12 months

#### 1.5.2 Mechanics

**Observation at Each Period:**

1. **Autocall Triggered** ($S_t \geq K_{auto}$):
   - Product terminates early
   - Investor receives: Principal + accumulated coupon
   - Best outcome for investor

2. **Between Barriers** ($K_{in} < S_t < K_{auto}$):
   - Product continues
   - Coupon accrues (may or may not be paid)
   - "Snowball" effect: longer survival = more coupon accumulated

3. **Knock-In Triggered** ($S_t \leq K_{in}$):
   - Downside protection removed
   - At maturity, if still below entry:
     - Investor bears the loss: Final Payout = Principal × (S_T / S_0)
   - At maturity, if recovered above entry:
     - Investor receives: Principal + accumulated coupon (knock-in "heals")

#### 1.5.3 Payoff Summary

$$\text{Final Payout} = \begin{cases} P \times (1 + c \times n) & \text{if autocalled at observation } n \\ P \times (1 + c \times N) & \text{if survived to maturity without knock-in} \\ P \times \frac{S_T}{S_0} + c \times n_{survived} & \text{if knocked-in and } S_T < S_0 \\ P \times (1 + c \times N) & \text{if knocked-in but } S_T \geq S_0 \text{ at maturity} \end{cases}$$

Where:
- $P$ = Principal
- $c$ = Coupon per period
- $n$ = Number of periods survived
- $N$ = Total periods
- $S_0$ = Entry price
- $S_T$ = Final price

#### 1.5.4 Risk Analysis

| Risk Factor | Impact |
|---|---|
| Large downside move | Knock-in triggered, bear full downside loss |
| Extended bear market | High probability of knock-in, coupon doesn't compensate |
| Quick autocall | Limits total return (short participation) |
| Volatility spike | Increases knock-in probability |
| Low volatility | Reduces coupon (less premium available) but also reduces knock-in risk |

**Crypto-Specific Risks:**
- 30-50% drops are not uncommon → knock-in at 75% is realistic risk
- Snowball products on BTC are MUCH riskier than on traditional assets
- Typical crypto snowball knock-in: 70-80% (adjusted for higher vol)

### 1.6 Accumulator / Decumulator

#### 1.6.1 Accumulator ("I Kill You Later")

An accumulator obligates the buyer to purchase a fixed quantity of an asset at a discounted price periodically, as long as the price stays below a "knock-out" barrier.

**Structure:**
- Strike/Accumulation Price: $K_{acc}$ (at a discount, e.g., 95% of spot)
- Knock-Out Barrier: $K_{KO}$ (above spot, e.g., 105% of spot)
- Observation: Daily
- Duration: 3-12 months
- Gearing: May require 2x quantity purchase when price < strike

**Daily Mechanics:**

$$\text{Daily Obligation} = \begin{cases} \text{Buy } Q \text{ at } K_{acc} & \text{if } K_{acc} \leq S_t < K_{KO} \\ \text{Buy } 2Q \text{ at } K_{acc} & \text{if } S_t < K_{acc} \text{ (geared)} \\ \text{Product terminated} & \text{if } S_t \geq K_{KO} \end{cases}$$

**P&L:**

$$\text{P\&L}_{daily} = Q \times (S_t - K_{acc}) \quad \text{(if accumulated)}$$

$$\text{Total P\&L} = \sum_{t=1}^{T} Q_t \times (S_T - K_{acc}) - \text{carry costs}$$

**Risk:**
- If price drops significantly, obligated to keep buying at above-market prices
- Gearing doubles the pain: 2x quantity when price is already below strike
- Unlimited downside risk if market crashes
- "I Kill You Later" nickname from the 2008 crisis where accumulators caused massive losses

#### 1.6.2 Decumulator

The opposite: obligated to sell a fixed quantity at a premium price, as long as price stays above a knock-out barrier.

**Use Case:** For crypto miners/holders who want to systematically sell at premium but risk being "decumulated" into a rally (selling at below-market prices if market rallies past the knock-out).

### 1.7 Range Accrual

#### 1.7.1 Overview

Range accrual products pay an enhanced coupon for each day (or observation period) that the underlying stays within a predefined range.

**Structure:**
- Lower barrier: $L$
- Upper barrier: $U$
- Coupon rate: $c$ per day within range
- Term: Fixed (e.g., 30 days)
- Principal: Protected (typically)

**Payoff:**

$$\text{Total Return} = c \times \frac{N_{in}}{N_{total}} \times \frac{T}{365}$$

Where:
- $N_{in}$ = Number of observation days within range $[L, U]$
- $N_{total}$ = Total observation days
- $T$ = Product term in days

**Example:**
- BTC at $60,000
- Range: [$55,000, $65,000]
- Coupon: 80% APR (when in range)
- Term: 30 days
- If BTC stays in range 20 out of 30 days:
  - Return = 80% × (20/30) × (30/365) = 4.38%

#### 1.7.2 Optimal Conditions

- Low volatility environment
- Range-bound market expectation
- Higher coupon compensates for risk of breaking range
- Best used when IV is elevated but realized vol is expected to be low

### 1.8 Barrier Options

#### 1.8.1 Knock-In Options

An option that comes into existence ("knocks in") only when the underlying hits a specified barrier level.

**Types:**
- **Down-and-In Call**: Call activates when price falls to barrier (cheap crash protection that activates when needed)
- **Down-and-In Put**: Put activates when price falls to barrier (even cheaper put — only live after a drop)
- **Up-and-In Call**: Call activates when price rises to barrier
- **Up-and-In Put**: Put activates when price rises to barrier

**Pricing (Down-and-In Call, H < K):**

$$C_{DI} = S_0 (H/S_0)^{2\lambda} N(y) - Ke^{-rT}(H/S_0)^{2\lambda - 2} N(y - \sigma\sqrt{T})$$

Where:
- $H$ = Barrier level
- $\lambda = (r - q + \sigma^2/2) / \sigma^2$
- $y = \frac{\ln(H^2/(S_0 K))}{\sigma\sqrt{T}} + \lambda\sigma\sqrt{T}$

**Key Relationship (In-Out Parity):**

$$C_{vanilla} = C_{knock-in} + C_{knock-out}$$

A knock-in + knock-out with same barrier = vanilla option.

#### 1.8.2 Knock-Out Options

An option that ceases to exist ("knocks out") when the underlying hits the barrier.

**Types:**
- **Down-and-Out Call**: Call dies if price falls to barrier (cheap upside bet, dies in crash)
- **Down-and-Out Put**: Put dies if price falls to barrier (limited protection)
- **Up-and-Out Call**: Call dies if price rises too much (capped upside)
- **Up-and-Out Put**: Put dies if price rises to barrier

**Pricing (Down-and-Out Call, H < S_0):**

$$C_{DO} = C_{vanilla} - C_{DI}$$

**Use Cases in Crypto:**
- Knock-out calls: Cheap directional bet with protection cost savings (if you don't think it'll crash first)
- Knock-in puts: Cheap tail protection that only activates in a real crash (avoid time decay in calm markets)
- Barrier structures embedded in Shark Fin and other structured products

#### 1.8.3 Monitoring Requirements

- **Continuous Monitoring**: Barrier options require tick-level monitoring
- **Rebate**: Some barrier options pay a rebate if knocked out (partial premium return)
- **Digital Risk at Barrier**: Greeks become extreme near the barrier (gamma and vega spikes)
- **Gap Risk**: In crypto, despite 24/7 trading, thin liquidity can cause gaps through barriers

### 1.9 Asian Options

#### 1.9.1 Overview

Asian options have payoff based on the average price over a period, rather than the terminal price. This averaging reduces volatility and makes them cheaper than vanilla options.

**Types:**
- **Average Price Option**: Payoff based on average of underlying
- **Average Strike Option**: Strike is set to the average price

#### 1.9.2 Average Price Call

$$\text{Payoff} = \max(\bar{S} - K, 0)$$

Where $\bar{S}$ is the arithmetic or geometric average:

**Arithmetic Average:**

$$\bar{S}_{arith} = \frac{1}{n}\sum_{i=1}^{n} S_{t_i}$$

**Geometric Average:**

$$\bar{S}_{geom} = \left(\prod_{i=1}^{n} S_{t_i}\right)^{1/n}$$

#### 1.9.3 Pricing

**Geometric Average (closed-form under BSM):**

The geometric average of a log-normal process is also log-normal, enabling closed-form pricing:

$$C_{geometric} = e^{-rT}\left[e^{(\hat{\mu} + \hat{\sigma}^2/2)T}N(\hat{d}_1) - KN(\hat{d}_2)\right]$$

Where:
$$\hat{\mu} = \frac{r - \sigma^2/2}{2} + \frac{\ln S_0}{T}$$
$$\hat{\sigma}^2 = \frac{\sigma^2}{3}$$

**Arithmetic Average (no closed-form):**
- Monte Carlo simulation (most common)
- Moment-matching approximation (treat as shifted log-normal)
- Turnbull-Wakeman approximation

#### 1.9.4 Use Cases in Crypto

- **TWAP Execution**: Asian options naturally hedge TWAP order execution
- **DeFi Integration**: Many DeFi protocols use time-weighted averages (TWAP oracles)
- **Reduced Manipulation Risk**: Averaging window makes manipulation more difficult/expensive
- **Lower Premium**: Cheaper than vanilla due to reduced effective volatility ($\sigma/\sqrt{3}$ for geometric)

### 1.10 Lookback Options

#### 1.10.1 Overview

Lookback options have payoff based on the maximum or minimum price achieved during the option's life. Gives the holder the benefit of hindsight.

**Types:**
- **Fixed Strike Lookback Call**: $\text{Payoff} = \max(S_{max} - K, 0)$
- **Fixed Strike Lookback Put**: $\text{Payoff} = \max(K - S_{min}, 0)$
- **Floating Strike Lookback Call**: $\text{Payoff} = S_T - S_{min}$ (bought at the lowest price)
- **Floating Strike Lookback Put**: $\text{Payoff} = S_{max} - S_T$ (sold at the highest price)

#### 1.10.2 Pricing (Floating Strike Lookback Call)

Under BSM assumptions:

$$C_{lookback} = S_0 N(a_1) - S_0 \frac{\sigma^2}{2r}N(-a_1) - S_{min}e^{-rT}\left[N(a_2) - \frac{\sigma^2}{2r}e^{Y_1}N(-a_3)\right]$$

Where:
$$a_1 = \frac{\ln(S_0/S_{min}) + (r + \sigma^2/2)T}{\sigma\sqrt{T}}$$
$$a_2 = a_1 - \sigma\sqrt{T}$$
$$a_3 = \frac{\ln(S_0/S_{min}) + (-r + \sigma^2/2)T}{\sigma\sqrt{T}}$$
$$Y_1 = \frac{-2(r - \sigma^2/2)\ln(S_0/S_{min})}{\sigma^2}$$

#### 1.10.3 Practical Considerations

- **Very Expensive**: Lookback options cost 2-3x vanilla options (guaranteed best outcome)
- **Discrete Monitoring**: In practice, monitored at discrete intervals (reduces price vs continuous)
- **Useful For**: Benchmarking trading performance against "perfect timing"
- **Crypto Application**: Some structured products embed lookback features for "best of" payoffs

---

## 2. Technical Specifications

### 2.1 Structured Products Data Pipeline

```
STRUCTURED_PRODUCTS_PIPELINE:

  DATA_INPUTS:
    market_data:
      - Spot prices (real-time, all relevant underlyings)
      - Implied volatility surface (full term structure and skew)
      - Interest rates / DeFi lending rates
      - Staking yields
      - Funding rates

    product_data:
      - Available products (strike, barrier, term, coupon)
      - Historical product performance
      - Competition analysis (yields across platforms)
      - Protocol TVL and utilization

    risk_data:
      - Barrier distances (% from current spot)
      - Knock-in/knock-out probabilities
      - Monte Carlo scenario analysis
      - Historical drawdown analysis

  PROCESSING:
    1. Product screening:
       - Filter by risk tolerance
       - Filter by expected return threshold
       - Filter by duration preference
    
    2. Fair value assessment:
       - Compute theoretical fair value using options pricing
       - Compare to offered yield
       - Identify edge (offered yield vs fair value)
    
    3. Risk assessment:
       - Monte Carlo simulation (10,000+ paths)
       - Probability of knock-in/knock-out
       - Expected loss in adverse scenarios
       - CVaR at 95% confidence
    
    4. Portfolio integration:
       - Correlation with existing positions
       - Contribution to portfolio Greeks
       - Margin/collateral requirements
       - Concentration limits

  OUTPUT:
    - Recommended products with scores
    - Risk metrics per product
    - Optimal allocation
    - Monitoring parameters
```

### 2.2 Pricing Engine Architecture

```
STRUCTURED_PRODUCT_PRICING_ENGINE:

  ┌─────────────────────────────────────────────────────────┐
  │                PRICING ENGINE                             │
  ├─────────────────────────────────────────────────────────┤
  │                                                           │
  │  ┌─────────────────────────────────────────────────────┐ │
  │  │  INPUT LAYER                                         │ │
  │  │  - Spot price, IV surface, rates, yields, barriers  │ │
  │  └──────────────────────┬──────────────────────────────┘ │
  │                         │                                 │
  │  ┌──────────────────────▼──────────────────────────────┐ │
  │  │  MODEL SELECTION                                     │ │
  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐           │ │
  │  │  │ BSM      │ │ Heston   │ │ Local    │           │ │
  │  │  │ (vanilla)│ │ (stoch   │ │ Vol      │           │ │
  │  │  │          │ │  vol)    │ │ (Dupire) │           │ │
  │  │  └──────────┘ └──────────┘ └──────────┘           │ │
  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐           │ │
  │  │  │ Jump     │ │ SABR     │ │ Monte    │           │ │
  │  │  │ Diffusion│ │ (FX/     │ │ Carlo    │           │ │
  │  │  │ (Merton) │ │  crypto) │ │ (general)│           │ │
  │  │  └──────────┘ └──────────┘ └──────────┘           │ │
  │  └──────────────────────┬──────────────────────────────┘ │
  │                         │                                 │
  │  ┌──────────────────────▼──────────────────────────────┐ │
  │  │  NUMERICAL METHODS                                   │ │
  │  │  - Monte Carlo (barrier, Asian, lookback, snowball)  │ │
  │  │  - Finite Difference (barrier, American)             │ │
  │  │  - Binomial/Trinomial Tree (American, barriers)      │ │
  │  │  - Analytical (where available: vanilla, geo Asian)  │ │
  │  └──────────────────────┬──────────────────────────────┘ │
  │                         │                                 │
  │  ┌──────────────────────▼──────────────────────────────┐ │
  │  │  OUTPUT                                              │ │
  │  │  - Fair value                                        │ │
  │  │  - Greeks (delta, gamma, vega, theta, barrier risk)  │ │
  │  │  - Probability analysis                              │ │
  │  │  - Scenario P&L                                      │ │
  │  └─────────────────────────────────────────────────────┘ │
  │                                                           │
  └─────────────────────────────────────────────────────────┘
```

### 2.3 Monte Carlo Engine Specifications

```
MONTE_CARLO_CONFIG:

  simulation_parameters:
    num_paths: 100,000 (production), 10,000 (real-time screening)
    time_steps_per_day: 24 (hourly for crypto barriers)
    random_seed: deterministic for reproducibility
    variance_reduction:
      - antithetic_variates: true
      - control_variate: geometric_asian (for arithmetic Asian)
      - importance_sampling: for barrier options near barrier
      - stratified_sampling: true

  process_models:
    geometric_brownian_motion:
      dS = (r - q)S dt + sigma S dW
      use_for: vanilla equivalents, simple structures

    heston_stochastic_vol:
      dS = (r-q)S dt + sqrt(v)S dW_S
      dv = kappa(theta - v)dt + xi sqrt(v) dW_v
      corr(dW_S, dW_v) = rho
      use_for: barrier options, structured products with vol sensitivity

    jump_diffusion:
      dS = (r - q - lambda*k)S dt + sigma S dW + J S dN
      J ~ LogNormal(mu_J, sigma_J)
      N ~ Poisson(lambda)
      use_for: crypto products (jumps are significant)

  performance:
    single_product_pricing: <500ms (100K paths)
    batch_screening: <5s (1000 products × 10K paths each)
    greek_calculation: finite_difference (bump and reprice)
    confidence_interval: 95% CI reported with every price
```

### 2.4 Platform Integration

```
PLATFORM_CONFIGS:

  binance_earn:
    products: [dual_investment, shark_fin, range_accrual]
    api: https://www.binance.com/bapi/earn
    min_deposit: varies by product
    settlement: automatic at expiry
    risks: exchange counterparty

  okx_earn:
    products: [dual_investment, shark_fin, snowball]
    api: https://www.okx.com/api/v5/finance
    min_deposit: varies
    auto_rollover: optional

  ribbon_finance:
    chain: ethereum, solana
    products: [covered_call_vault, put_selling_vault]
    contract_addresses: [documented per vault]
    epoch_duration: 7 days
    strike_selection: algorithmic (10-25% OTM)
    risks: smart_contract, oracle_manipulation

  cega_finance:
    chain: ethereum, solana
    products: [exotic_options_vaults, fixed_coupon_notes]
    epoch_duration: 27 days
    features: multi-asset baskets, barrier structures

  matrixport:
    products: [dual_currency, shark_fin, snowball, accumulator]
    type: CeFi (custodial)
    min_investment: $100
    settlement: automatic
    risks: counterparty, regulatory
```

---

## 3. Mathematical Models

### 3.1 Barrier Option Pricing Framework

**Continuous Monitoring, Constant Volatility (Analytical Solutions)**

For a down-and-out call ($H < S_0$, $H < K$):

$$C_{DO} = C_{vanilla} - (S_0/H)^{1-2r/\sigma^2} \times C^*$$

Where $C^*$ is a vanilla call with adjusted parameters (reflection principle).

**General Barrier Formula (Rubinstein & Reiner, 1991):**

For various barrier types, the price is expressed as combinations of terms $A, B, C, D, E, F$:

$$A = \phi S e^{-qT} N(\phi x_1) - \phi K e^{-rT} N(\phi x_1 - \phi\sigma\sqrt{T})$$

$$B = \phi S e^{-qT} N(\phi x_2) - \phi K e^{-rT} N(\phi x_2 - \phi\sigma\sqrt{T})$$

$$C = \phi S e^{-qT} (H/S)^{2(\mu+1)} N(\eta y_1) - \phi K e^{-rT} (H/S)^{2\mu} N(\eta y_1 - \eta\sigma\sqrt{T})$$

$$D = \phi S e^{-qT} (H/S)^{2(\mu+1)} N(\eta y_2) - \phi K e^{-rT} (H/S)^{2\mu} N(\eta y_2 - \eta\sigma\sqrt{T})$$

Where:
$$x_1 = \frac{\ln(S/K)}{\sigma\sqrt{T}} + (1+\mu)\sigma\sqrt{T}$$
$$x_2 = \frac{\ln(S/H)}{\sigma\sqrt{T}} + (1+\mu)\sigma\sqrt{T}$$
$$y_1 = \frac{\ln(H^2/(SK))}{\sigma\sqrt{T}} + (1+\mu)\sigma\sqrt{T}$$
$$y_2 = \frac{\ln(H/S)}{\sigma\sqrt{T}} + (1+\mu)\sigma\sqrt{T}$$
$$\mu = \frac{r - q - \sigma^2/2}{\sigma^2}$$
$$\phi = +1 \text{ for calls}, -1 \text{ for puts}$$
$$\eta = +1 \text{ for down barriers}, -1 \text{ for up barriers}$$

### 3.2 Snowball Product Pricing

Snowball products require Monte Carlo simulation due to path-dependency:

**Algorithm:**

```
For each path p = 1 to N:
    Generate price path: S_0, S_1, ..., S_T (monthly observations)
    knocked_in = False
    autocalled = False
    
    For each observation t = 1 to T:
        # Check continuous knock-in (between observations)
        If min(S_path between t-1 and t) <= K_in:
            knocked_in = True
        
        # Check autocall at observation date
        If S_t >= K_auto AND NOT autocalled:
            autocalled = True
            payout[p] = Principal * (1 + coupon * t)
            break
    
    If NOT autocalled:
        If knocked_in:
            If S_T >= S_0:
                payout[p] = Principal * (1 + coupon * T)  # healed
            Else:
                payout[p] = Principal * (S_T / S_0)  # bear loss
        Else:
            payout[p] = Principal * (1 + coupon * T)  # survived

Fair_Value = mean(payout) * exp(-r*T)
```

**Key Pricing Sensitivities:**
- Higher vol → higher knock-in probability → lower product value for investor
- Higher vol → higher autocall probability → shorter expected duration
- Net effect depends on barrier levels and vol regime

### 3.3 Asian Option Pricing

**Turnbull-Wakeman Approximation (Arithmetic Average):**

Match the first two moments of the arithmetic average distribution:

$$M_1 = \frac{S_0}{(r-q)T}\left(e^{(r-q)T} - 1\right)$$

$$M_2 = \frac{2S_0^2 e^{(2r-2q+\sigma^2)T}}{(r-q+\sigma^2)(2r-2q+\sigma^2)T^2} + \frac{2S_0^2}{(r-q)T^2}\left(\frac{1}{2(r-q)+\sigma^2} - \frac{e^{(r-q)T}}{r-q+\sigma^2}\right)$$

Then:
$$\sigma_A^2 = \frac{1}{T}\ln\left(\frac{M_2}{M_1^2}\right)$$

Price using BSM with $M_1$ as the forward and $\sigma_A$ as the adjusted volatility.

### 3.4 Lookback Option Pricing

**Floating Strike Lookback Call (Continuous Monitoring):**

$$C = S_0 N(d_1') - S_0\frac{\sigma^2}{2r}N(-d_1') - S_{min}e^{-rT}\left(N(d_2') - \frac{\sigma^2}{2r}e^{r_1}N(-d_3')\right)$$

Where:
$$d_1' = \frac{\ln(S_0/S_{min}) + (r+\sigma^2/2)T}{\sigma\sqrt{T}}$$
$$d_2' = d_1' - \sigma\sqrt{T}$$
$$d_3' = \frac{\ln(S_0/S_{min}) + (-r+\sigma^2/2)T}{\sigma\sqrt{T}}$$
$$r_1 = \frac{-2(r-\sigma^2/2)\ln(S_0/S_{min})}{\sigma^2}$$

### 3.5 Range Accrual Pricing

Each observation day is a binary option (digital) on whether the underlying is within range:

$$V_{accrual} = c \times \sum_{i=1}^{N} e^{-r t_i} \times P(L \leq S_{t_i} \leq U)$$

The probability of being in range on day $i$:

$$P(L \leq S_{t_i} \leq U) = N\left(\frac{\ln(U/S_0) - (r-\sigma^2/2)t_i}{\sigma\sqrt{t_i}}\right) - N\left(\frac{\ln(L/S_0) - (r-\sigma^2/2)t_i}{\sigma\sqrt{t_i}}\right)$$

**Adjustment for Path Dependency:** If the range is checked continuously (not just end of day), use barrier option techniques.

### 3.6 Accumulator Pricing

An accumulator can be decomposed into a portfolio of:
- Daily forward contracts (obligation to buy at $K_{acc}$)
- Up-and-out feature (knock-out at $K_{KO}$)
- Gearing below strike (additional forward below $K_{acc}$)

**Fair Value (simplified):**

$$V_{acc} = \sum_{t=1}^{T} e^{-rt}\left[E[(S_t - K_{acc})^+ \cdot \mathbb{1}(\max_{s\leq t} S_s < K_{KO})] - E[(K_{acc} - S_t)^+ \cdot g \cdot \mathbb{1}(\max_{s\leq t} S_s < K_{KO})]\right]$$

Where $g$ = gearing factor (typically 2).

**Requires Monte Carlo with:**
- Daily path generation
- Running maximum tracking (for knock-out)
- Conditional accumulation based on barrier status

### 3.7 DOV Fair Value Assessment

**Is the DOV Yield Fair?**

For a covered call DOV selling weekly $\Delta$-delta calls:

$$\text{Fair Premium} = BSM(S_0, K_\Delta, 7/365, r, \sigma_{imp})$$

$$\text{APY}_{fair} = \frac{\text{Fair Premium}}{S_0} \times 52$$

**Edge to Depositor:**

$$\text{Edge} = APY_{offered} - APY_{fair} - \text{Protocol Fees}$$

- If Edge > 0: Protocol is somehow subsidizing (token rewards, etc.)
- If Edge < 0: Protocol takes a spread (typical)
- Typical protocol fee: 10-20% of premium (performance fee)

**Structural Consideration:**
- DOVs often sell at market-determined strikes (auction)
- The actual yield depends on market-clearing premium
- Historical backtests may overstate yields (does not account for the DOV's own selling pressure suppressing IV)
- Large DOV TVLs can suppress option premiums for their own products

---

## 4. Risk Parameters

### 4.1 Product-Level Risk Assessment

```
STRUCTURED_PRODUCT_RISK_MATRIX:

  DOV_COVERED_CALL:
    max_loss_scenario: "BTC rallies 50%+ in a week"
    actual_loss: Opportunity cost (capped at strike)
    principal_at_risk: BTC price decline risk (same as holding BTC)
    liquidity_risk: Weekly lockup (can't exit mid-epoch)
    smart_contract_risk: HIGH (for DeFi DOVs)
    recommended_allocation: 10-30% of crypto holdings
    risk_score: 4/10

  DOV_PUT_SELLING:
    max_loss_scenario: "BTC crashes 30%+ in a week"
    actual_loss: Buy BTC at strike when market price is lower
    principal_at_risk: Full USDC deposit potentially converted to declining BTC
    liquidity_risk: Weekly lockup
    smart_contract_risk: HIGH
    recommended_allocation: 5-15% of stablecoin holdings
    risk_score: 6/10

  DUAL_INVESTMENT:
    max_loss_scenario: "Large move against you at settlement"
    actual_loss: Converted at unfavorable rate
    principal_at_risk: Conversion risk (not actual loss of principal)
    liquidity_risk: Term-locked (1-7 days typically)
    recommended_allocation: 10-20% of holdings
    risk_score: 3/10

  SHARK_FIN:
    max_loss_scenario: "Barrier breached → only base return"
    actual_loss: Minimal (principal protected)
    principal_at_risk: LOW (base return guaranteed)
    opportunity_cost: Could have held through the move
    recommended_allocation: 20-40% of yield-seeking capital
    risk_score: 2/10

  SNOWBALL:
    max_loss_scenario: "BTC drops 30%+ and stays below entry"
    actual_loss: Full downside exposure below knock-in
    principal_at_risk: HIGH (once knocked in)
    liquidity_risk: 3-12 month lockup
    complexity_risk: HIGH (path-dependent)
    recommended_allocation: 5-10% of portfolio MAX
    risk_score: 7/10

  ACCUMULATOR:
    max_loss_scenario: "Sustained price decline with gearing"
    actual_loss: Forced buying above market at 2x rate
    principal_at_risk: VERY HIGH (unlimited downside with gearing)
    liquidity_risk: Cannot exit mid-term
    recommended_allocation: 2-5% of portfolio MAX
    risk_score: 9/10

  RANGE_ACCRUAL:
    max_loss_scenario: "Price breaks range consistently"
    actual_loss: Zero coupon days (but principal typically protected)
    principal_at_risk: LOW (usually protected)
    opportunity_cost: Could have invested elsewhere
    recommended_allocation: 15-30% of yield-seeking capital
    risk_score: 2/10

  BARRIER_OPTIONS (as hedge):
    max_loss_scenario: "Barrier not triggered → option never activates"
    actual_loss: Premium paid (for knock-in) or option knocked out (for knock-out)
    principal_at_risk: Premium only
    recommended_allocation: 1-5% of portfolio (hedging budget)
    risk_score: 3/10
```

### 4.2 Portfolio-Level Structured Product Limits

```
PORTFOLIO_LIMITS:

  allocation_limits:
    max_structured_products_total: 30% of portfolio
    max_single_product: 10% of portfolio
    max_single_protocol_defi: 10% of portfolio
    max_single_platform_cefi: 15% of portfolio
    max_locked_capital: 40% of portfolio (across all durations)

  duration_limits:
    max_avg_duration: 30 days (weighted by allocation)
    max_single_product_duration: 90 days
    min_liquid_reserves: 60% of portfolio (always accessible)

  risk_limits:
    max_knock_in_probability: 20% (per product at entry)
    max_portfolio_knock_in_exposure: 15% of portfolio
    min_annualized_return_threshold: 8% (otherwise not worth complexity)
    max_correlation_between_products: 0.7 (diversification)
    
  counterparty_limits:
    max_single_exchange: 30% of structured capital
    max_defi_protocol: 15% of structured capital
    require_audit: true (for DeFi)
    require_insurance: preferred (Nexus Mutual coverage)

  scenario_limits:
    max_loss_30pct_crash: 10% of total portfolio
    max_loss_vol_spike_50pts: 5% of total portfolio
    max_opportunity_cost_50pct_rally: 15% of total portfolio
```

### 4.3 Scenario Analysis

```
STRUCTURED_PRODUCT_SCENARIOS:

  scenario_1_btc_crash_25pct:
    impact_by_product:
      covered_call_dov: "-25% + premium collected ≈ -23% for the week"
      put_selling_dov: "Assigned at strike, loss = (strike - market) - premium"
      dual_investment_sell_high: "Keep BTC (now worth 25% less) + premium"
      dual_investment_buy_low: "Likely assigned → buy BTC at strike (still above market if strike > market)"
      shark_fin_bullish: "Only base return (below strike)"
      snowball: "Possible knock-in if below 75% → full downside exposure"
      accumulator: "Buying at above-market price with 2x gearing → severe loss"
      range_accrual: "Out of range → no coupon"

  scenario_2_btc_rally_30pct:
    impact_by_product:
      covered_call_dov: "Capped at strike → miss ~20% of rally above strike"
      put_selling_dov: "Keep full premium → best outcome"
      dual_investment_sell_high: "Sold at strike → miss additional upside"
      shark_fin_bullish: "Possibly knocked out (above barrier) → only base return"
      snowball: "Likely autocalled → receive principal + accumulated coupon (good outcome)"
      accumulator: "Knocked out → stop accumulating (miss further upside)"
      range_accrual: "Out of range (above upper) → no coupon"

  scenario_3_range_bound_10pct:
    impact_by_product:
      covered_call_dov: "Best case → keep premium, keep BTC"
      put_selling_dov: "Best case → keep premium"
      shark_fin_bullish: "Enhanced return (in the fin range)"
      snowball: "Continue accruing coupon → excellent"
      range_accrual: "Fully in range → maximum coupon"
    note: "Range-bound is the ideal scenario for most structured products"
```

---

## 5. Execution Flow

### 5.1 Structured Product Selection Algorithm

```
STRUCTURED_PRODUCT_SELECTION:

  ╔══════════════════════════════════════════════════════════╗
  ║  STEP 1: MARKET ENVIRONMENT ASSESSMENT                   ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  1.1 Current IV Rank/Percentile                          ║
  ║  1.2 Market regime (trending, range-bound, volatile)     ║
  ║  1.3 Funding rate environment                            ║
  ║  1.4 Term structure shape                                ║
  ║  1.5 Available product yields vs fair value              ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 2: PRODUCT SCREENING                               ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  For each available product:                             ║
  ║  2.1 Calculate fair value (pricing engine)               ║
  ║  2.2 Calculate edge = offered_yield - fair_yield - fees  ║
  ║  2.3 Calculate risk metrics:                             ║
  ║      - Probability of adverse outcome                    ║
  ║      - Expected loss in adverse scenario                 ║
  ║      - Sharpe ratio equivalent                           ║
  ║  2.4 Score = edge × (1 - P(adverse)) / vol              ║
  ║                                                          ║
  ║  FILTER:                                                 ║
  ║  □ Edge > 0 (product not overpriced)                    ║
  ║  □ P(adverse) < 20%                                     ║
  ║  □ Annualized return > 8%                               ║
  ║  □ Platform risk acceptable                              ║
  ║  □ Duration within limits                                ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 3: REGIME-BASED STRATEGY MAPPING                   ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  IF high_iv AND range_bound:                             ║
  ║    → DOV covered calls (premium is rich)                 ║
  ║    → Range accrual (likely stays in range)               ║
  ║    → Iron condor equivalents via structured products     ║
  ║                                                          ║
  ║  IF low_iv AND expected_breakout:                        ║
  ║    → AVOID selling strategies                            ║
  ║    → Consider barrier option hedges (cheap)              ║
  ║    → Shark fin (principal protected, benefit if moves)   ║
  ║                                                          ║
  ║  IF bullish_moderate:                                    ║
  ║    → Bullish shark fin                                   ║
  ║    → Dual investment "sell high"                         ║
  ║    → Snowball (autocall upside + carry)                  ║
  ║                                                          ║
  ║  IF bearish_moderate:                                    ║
  ║    → Bearish shark fin                                   ║
  ║    → Dual investment "buy low"                           ║
  ║    → Put-selling DOV (sell puts at desired buy price)    ║
  ║                                                          ║
  ║  IF uncertain_high_vol:                                  ║
  ║    → Avoid complex structures (knock-in risk)            ║
  ║    → Principal-protected only                            ║
  ║    → Short duration (1-7 days max)                       ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 4: ALLOCATION & SIZING                             ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  4.1 Determine total structured product budget           ║
  ║  4.2 Allocate across selected products:                  ║
  ║      - Weight by score (risk-adjusted edge)              ║
  ║      - Enforce diversification limits                    ║
  ║      - Check duration constraints                        ║
  ║  4.3 Verify portfolio-level risk:                        ║
  ║      - Total knock-in exposure < 15%                    ║
  ║      - Total locked capital < 40%                       ║
  ║      - Max loss in crash scenario < 10%                 ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 5: EXECUTION                                       ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  For CeFi products:                                      ║
  ║  5.1 Subscribe via exchange API                          ║
  ║  5.2 Confirm allocation and terms                        ║
  ║  5.3 Record position details                             ║
  ║                                                          ║
  ║  For DeFi DOVs:                                          ║
  ║  5.4 Approve token spending                              ║
  ║  5.5 Deposit into vault (before epoch deadline)          ║
  ║  5.6 Verify transaction confirmation                     ║
  ║  5.7 Record position and epoch schedule                  ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 6: MONITORING & MANAGEMENT                         ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  6.1 Track P&L per product per epoch                     ║
  ║  6.2 Monitor barrier distances:                          ║
  ║      - Alert if within 5% of knock-in barrier           ║
  ║      - Alert if within 5% of knock-out barrier          ║
  ║  6.3 Monitor protocol health (DeFi):                     ║
  ║      - TVL changes                                       ║
  ║      - Smart contract events                             ║
  ║      - Oracle health                                     ║
  ║  6.4 Rebalancing decisions:                              ║
  ║      - Renew at next epoch? (check if conditions still)  ║
  ║      - Withdraw? (if regime changed)                     ║
  ║      - Switch product? (if better opportunity)           ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 7: SETTLEMENT & REINVESTMENT                       ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  7.1 At product maturity:                                ║
  ║      - Record final payout vs expected                   ║
  ║      - Compare to benchmark (holding, staking, etc.)     ║
  ║      - Assess if assignment occurred (dual investment)   ║
  ║  7.2 Reinvestment decision:                              ║
  ║      - Re-enter same product? (auto-roll if available)   ║
  ║      - Switch to different product? (conditions changed) ║
  ║      - Exit to spot? (no attractive opportunities)       ║
  ║  7.3 Performance attribution:                            ║
  ║      - Premium income                                    ║
  ║      - Assignment impact                                 ║
  ║      - Opportunity cost vs holding                       ║
  ║      - Protocol fees                                     ║
  ║      - Net alpha generated                               ║
  ║                                                          ║
  ╚══════════════════════════════════════════════════════════╝
```

### 5.2 DOV Vault Management Flow

```
DOV_MANAGEMENT_FLOW:

  PRE_EPOCH:
    1. Check current epoch deadline
    2. Assess market conditions:
       - Is IV still elevated? (premium will be rich)
       - Any major events before next expiry?
       - Current P&L of vault vs benchmark
    3. Decision: Deposit/Withdraw/Maintain
       - IF IV Rank > 40 AND no major events: MAINTAIN/DEPOSIT
       - IF IV Rank < 20 OR major event imminent: WITHDRAW
       - IF recent losses > 3 consecutive epochs: REASSESS
    4. If depositing: Transfer funds before deadline

  DURING_EPOCH:
    1. Monitor strike vs spot:
       - Track how far OTM the sold option is
       - If approaching strike: No action possible (locked)
       - If far from strike: Position is safe
    2. Hedge externally (advanced):
       - If strike approached, can buy a cheaper option elsewhere as partial hedge
       - Cost-benefit: hedge cost vs vault premium

  POST_EPOCH:
    1. Check outcome:
       - Option expired OTM: Full premium captured
       - Option expired ITM: Position assigned/loss from strike breach
    2. Record performance
    3. Decide on next epoch participation

  YIELD_OPTIMIZATION:
    1. Compare vaults across protocols:
       - Ribbon vs Thetanuts vs Dopex
       - Different strike selection algorithms
       - Different fee structures
    2. Multi-vault diversification:
       - Split across BTC covered call + ETH covered call + put-selling
       - Different expiry cycles (weekly vs monthly)
    3. Token incentive awareness:
       - Some DOVs offer governance token rewards
       - Factor total APY = premium yield + token rewards
```

### 5.3 Snowball Product Lifecycle

```
SNOWBALL_LIFECYCLE:

  ENTRY_ASSESSMENT:
    1. Calculate knock-in probability:
       - Monte Carlo with current vol surface
       - Historical simulation (how often did BTC drop X% in Y months?)
    2. Calculate expected return:
       - P(autocall) × autocall_payout × avg_time_to_autocall
       + P(survive_without_knockin) × full_coupon_payout
       - P(knockin_loss) × expected_loss_given_knockin
    3. Compare to alternatives:
       - Simple holding: Expected return of BTC over same period
       - Staking: Guaranteed yield, lower risk
       - Other structured: Shark fin, range accrual
    4. Enter only if:
       - Risk-adjusted return > alternatives
       - Knock-in probability < 15-20%
       - Comfortable with worst-case loss

  DURING_PRODUCT:
    monthly_observation:
      check_autocall:
        IF spot >= autocall_barrier:
          → Product terminates
          → Receive: Principal + accumulated_coupon × months_elapsed
          → Result: PROFITABLE
      
      check_knock_in:
        IF spot <= knock_in_barrier:
          → Protection removed
          → Now have full downside exposure
          → Must hope for recovery by maturity
          → ALERT: HIGH RISK
      
      normal:
        IF knock_in < spot < autocall:
          → Coupon accrues ("snowballing")
          → Continue to next observation
          → Monitor distance to barriers

    hedging_during_product:
      IF spot approaching knock_in (within 10%):
        → Consider buying protective put externally
        → Cost vs probability assessment
        → May not be possible/worth it at that point
      
      IF knocked_in already:
        → Consider shorting BTC to lock in current level
        → Trade-off: If BTC recovers, short loses but product heals
        → Generally: Accept fate, don't over-hedge

  MATURITY:
    IF autocalled (at any observation):
      → Already settled, record profit
    
    IF survived_without_knockin:
      → Receive: Principal + full_coupon × N_months
      → Best non-autocall outcome
    
    IF knocked_in AND S_T >= S_0:
      → Product "healed": Receive Principal + coupon (or partial)
      → Lucky outcome
    
    IF knocked_in AND S_T < S_0:
      → Loss: Principal × (S_T / S_0)
      → Worst outcome: Bear the full decline
      → Record loss, assess portfolio impact
```

---

## 6. References

### Academic Literature

1. **Rubinstein, M., & Reiner, E.** (1991). "Breaking Down the Barriers." *Risk*, 4(8), 28-35.
2. **Haug, E.G.** (2007). *The Complete Guide to Option Pricing Formulas* (2nd Edition). McGraw-Hill.
3. **Taleb, N.N.** (1997). *Dynamic Hedging: Managing Vanilla and Exotic Options*. Wiley.
4. **Zhang, P.G.** (1998). *Exotic Options: A Guide to Second Generation Options*. World Scientific.
5. **Turnbull, S.M., & Wakeman, L.M.** (1991). "A Quick Algorithm for Pricing European Average Options." *Journal of Financial and Quantitative Analysis*, 26(3), 377-389.
6. **Goldman, M.B., Sosin, H.B., & Gatto, M.A.** (1979). "Path Dependent Options: Buy at the Low, Sell at the High." *Journal of Finance*, 34(5), 1111-1127.
7. **Conze, A., & Viswanathan, R.** (1991). "Path Dependent Options: The Case of Lookback Options." *Journal of Finance*, 46(5), 1893-1907.

### Textbooks

8. **Hull, J.C.** (2022). *Options, Futures, and Other Derivatives* (11th Edition). Pearson.
9. **Wilmott, P.** (2006). *Paul Wilmott on Quantitative Finance* (2nd Edition). Wiley.
10. **Bouzoubaa, M., & Osseiran, A.** (2010). *Exotic Options and Hybrids: A Guide to Structuring, Pricing and Trading*. Wiley.
11. **Natenberg, S.** (2015). *Option Volatility and Pricing* (2nd Edition). McGraw-Hill.

### Crypto Structured Products Resources

12. **Ribbon Finance Documentation** — https://docs.ribbon.finance — DOV mechanics and vault specifications.
13. **Dopex Documentation** — https://docs.dopex.io — Single Staking Option Vaults (SSOV).
14. **Cega Finance** — https://docs.cega.fi — Exotic structured vaults.
15. **Thetanuts Finance** — https://docs.thetanuts.finance — Multi-chain structured products.
16. **Binance Earn** — Dual Investment and Shark Fin product specifications.
17. **OKX Structured Products** — Snowball and dual currency documentation.
18. **Matrixport** — Structured product offerings and methodology papers.
19. **Paradigm** — Institutional crypto structured products trading.

### Industry Reports

20. **The Block Research** — "State of Crypto Structured Products" (annual reports).
21. **Delphi Digital** — DeFi Options Vault analysis and performance tracking.
22. **Messari** — Structured products protocol analysis.
23. **DefiLlama** — TVL tracking for DOV protocols.

---

> **Note to AI Agents:** This document covers structured products comprehensively.
> Critical implementation notes:
> 1. ALWAYS compute fair value before entering any structured product
> 2. NEVER allocate >10% of portfolio to any single structured product
> 3. Snowball and accumulator products carry tail risk — size conservatively
> 4. DeFi products have smart contract risk ON TOP of market risk
> 5. Principal-protected products (shark fin, range accrual) are preferred for larger allocations
> 6. Monitor barrier distances continuously — adjust hedges if barriers approach
> 7. Compare structured product yields to simple alternatives (staking, lending)
> 8. Factor in lockup periods — maintain minimum 60% portfolio liquidity
>
> Related documents:
> - `01_options_strategies.md` — Underlying options strategies that compose these products
> - `04_volatility_trading.md` — Vol trading framework for DOV strike/timing decisions
> - `05_risk_management_framework.md` — Portfolio integration and risk limits
