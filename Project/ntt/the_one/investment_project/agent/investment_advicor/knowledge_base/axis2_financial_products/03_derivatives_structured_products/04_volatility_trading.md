# Volatility Trading: Comprehensive Framework

> **Axis 2 — Financial Products | Module 03: Derivatives & Structured Products**
> **Document 04 — Volatility Trading**
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

### 1.1 Implied vs Realized Volatility

#### 1.1.1 Realized Volatility (Historical Volatility)

Realized volatility (RV) measures the actual historical price fluctuations of an asset over a specified period.

**Close-to-Close Estimator (Standard):**

$$\sigma_{CC} = \sqrt{\frac{252}{n-1} \sum_{i=1}^{n} (r_i - \bar{r})^2}$$

Where $r_i = \ln(S_i/S_{i-1})$ and $\bar{r}$ is the mean return. Factor 252 annualizes for daily data (crypto: use 365).

**Parkinson Estimator (High-Low):**

$$\sigma_P = \sqrt{\frac{1}{4n\ln 2} \sum_{i=1}^{n} (\ln H_i - \ln L_i)^2}$$

More efficient than close-to-close as it uses intraday range information.

**Garman-Klass Estimator:**

$$\sigma_{GK} = \sqrt{\frac{365}{n} \sum_{i=1}^{n} \left[\frac{1}{2}(\ln H_i - \ln L_i)^2 - (2\ln 2 - 1)(\ln C_i - \ln O_i)^2\right]}$$

Uses OHLC data — most efficient estimator under GBM assumptions.

**Yang-Zhang Estimator:**

$$\sigma_{YZ}^2 = \sigma_O^2 + k\sigma_C^2 + (1-k)\sigma_{RS}^2$$

Where:
- $\sigma_O^2$ = Overnight (open-to-close) variance
- $\sigma_C^2$ = Close-to-close variance
- $\sigma_{RS}^2$ = Rogers-Satchell variance
- $k = 0.34 / (1.34 + (n+1)/(n-1))$

Most robust for assets with opening jumps (less relevant for 24/7 crypto but important for FX).

**Realized Volatility Cone:**
For different lookback periods (7d, 14d, 30d, 60d, 90d), compute:
- Current RV
- Percentile rank (where current RV sits vs history)
- Mean, median, 25th, 75th percentile

This creates a "cone" showing typical RV ranges at different horizons.

#### 1.1.2 Implied Volatility

Implied volatility (IV) is the market's consensus expectation of future volatility, extracted from option prices using an options pricing model (BSM).

$$C_{market} = BSM(S, K, T, r, \sigma_{IV})$$

Solve for $\sigma_{IV}$ numerically.

**Key Properties of IV:**
- Forward-looking (market expectation)
- Includes risk premium (typically IV > RV, known as Volatility Risk Premium)
- Varies by strike (smile/skew) and expiry (term structure)
- Mean-reverting over long periods
- Can spike dramatically during crises

**IV in Crypto Markets:**
- BTC ATM IV: Typically 50-80% (calm), 80-120% (volatile), 120-200% (crisis)
- ETH ATM IV: Typically 60-100% (calm), 100-150% (volatile)
- Altcoin IV: Can exceed 200% annualized
- Comparison: SPX typically 12-25%, EUR/USD typically 6-12%

#### 1.1.3 Volatility Risk Premium (VRP)

$$VRP = IV - RV_{subsequent}$$

The VRP represents the excess return earned by volatility sellers. On average, implied volatility exceeds subsequently realized volatility:

**Empirical Findings:**
- Equities (SPX): IV exceeds RV approximately 85% of the time; average VRP ≈ 3-5 vol points
- Crypto (BTC): IV exceeds RV approximately 70-75% of the time; average VRP ≈ 5-15 vol points
- VRP is time-varying and regime-dependent
- VRP can turn negative during crisis periods (realized > implied)

**VRP as Trading Signal:**

$$VRP_t = IV_t - RV_t^{realized}$$

- High VRP (IV >> RV): Selling options is attractive (rich premiums)
- Low/Negative VRP (IV ≤ RV): Selling options is dangerous; consider buying

### 1.2 Volatility Surface Modeling

#### 1.2.1 The Volatility Surface

The volatility surface $\sigma(K, T)$ describes implied volatility as a function of strike price $K$ and time to expiry $T$.

**Dimensions:**
- **Strike dimension** (moneyness): Smile/skew
- **Time dimension** (term structure): Flat, upward-sloping, inverted, or humped

**Moneyness Measures:**
- Strike/Spot: $K/S$
- Log-moneyness: $\ln(K/F)$ where $F$ is the forward
- Delta-based: Strikes defined by their Black-Scholes delta (25Δ put, ATM, 25Δ call)
- Standard deviation: Number of standard deviations from ATM

#### 1.2.2 Volatility Smile and Skew

**Smile:** IV is higher for both OTM puts and OTM calls vs ATM (U-shaped)
- Common in: Crypto, short-dated equity options

**Skew (Risk Reversal):** IV for OTM puts is higher than for OTM calls
- Common in: Equity indices (crash protection demand), crypto (but weaker than equities)

**Crypto Skew Characteristics:**
- Typically moderate put skew (5-10 vol points between 25Δ put and 25Δ call)
- Skew can flip to call skew during extreme euphoria (demand for upside)
- Skew is more volatile than in traditional markets
- Short-dated skew is often more extreme than long-dated

**Skew Metrics:**

$$\text{25Δ Risk Reversal} = \sigma_{25\Delta Call} - \sigma_{25\Delta Put}$$

$$\text{25Δ Butterfly} = \frac{\sigma_{25\Delta Call} + \sigma_{25\Delta Put}}{2} - \sigma_{ATM}$$

$$\text{Skew Ratio} = \frac{\sigma_{25\Delta Put}}{\sigma_{25\Delta Call}}$$

#### 1.2.3 Term Structure

**Normal (Upward-Sloping):** Longer-dated options have higher IV
- Reflects: Uncertainty increases with time horizon
- Common in: Calm crypto markets

**Inverted (Downward-Sloping):** Near-term IV > Far-term IV
- Reflects: Near-term event risk or current high volatility expected to normalize
- Common in: Around major events (FOMC, halvings, ETF decisions)
- Common in: After a vol spike (backwardation as markets expect normalization)

**Humped:** Mid-term IV is highest (peak around specific event date)
- Reflects: Known future event with uncertainty (e.g., regulatory decision on specific date)

### 1.3 SABR Model

The SABR (Stochastic Alpha Beta Rho) model is a stochastic volatility model widely used for modeling the volatility smile, particularly in interest rate and FX markets, and increasingly in crypto.

**SABR Dynamics:**

$$dF = \alpha F^\beta dW_1$$

$$d\alpha = \nu \alpha dW_2$$

$$\text{Corr}(dW_1, dW_2) = \rho$$

Where:
- $F$ = Forward price
- $\alpha$ = Initial volatility level
- $\beta$ = CEV (Constant Elasticity of Variance) parameter, $\beta \in [0, 1]$
- $\nu$ = Vol-of-vol (volatility of $\alpha$)
- $\rho$ = Correlation between forward and volatility

**SABR Parameters Interpretation:**
- $\alpha$: Overall level of volatility (higher α = higher ATM vol)
- $\beta$: Controls the backbone (how ATM vol changes with spot)
  - $\beta = 1$: Log-normal (constant % vol)
  - $\beta = 0$: Normal (constant bp vol)
  - $\beta = 0.5$: CIR-like behavior
- $\nu$: Controls the smile curvature (higher ν = more pronounced smile)
- $\rho$: Controls the skew (negative ρ = put skew, positive ρ = call skew)

**Hagan's Approximation (Implied Vol from SABR):**

$$\sigma_{SABR}(K,F) \approx \frac{\alpha}{(FK)^{(1-\beta)/2}\left[1 + \frac{(1-\beta)^2}{24}\ln^2(F/K) + ...\right]} \cdot \frac{z}{x(z)} \cdot \left[1 + \left(\frac{(1-\beta)^2\alpha^2}{24(FK)^{1-\beta}} + \frac{\rho\beta\nu\alpha}{4(FK)^{(1-\beta)/2}} + \frac{2-3\rho^2}{24}\nu^2\right)T\right]$$

Where:
$$z = \frac{\nu}{\alpha}(FK)^{(1-\beta)/2}\ln(F/K)$$
$$x(z) = \ln\left(\frac{\sqrt{1-2\rho z + z^2} + z - \rho}{1-\rho}\right)$$

**Calibration:**
- Fit SABR parameters ($\alpha, \beta, \nu, \rho$) to market-observed IV smile for each expiry
- Typically fix $\beta$ (e.g., $\beta = 0.5$ for crypto) and calibrate ($\alpha, \nu, \rho$)
- Minimize: $\sum_i (IV_{SABR}(K_i) - IV_{market}(K_i))^2$

### 1.4 VIX Equivalent for Crypto (DVOL)

#### 1.4.1 Deribit Volatility Index (DVOL)

DVOL is the crypto market's equivalent of VIX — a measure of 30-day expected volatility for BTC and ETH, computed from Deribit options prices.

**Calculation (VIX-like methodology):**

$$DVOL = 100 \times \sqrt{\frac{2}{T}\sum_i \frac{\Delta K_i}{K_i^2} e^{rT} Q(K_i) - \frac{1}{T}\left(\frac{F}{K_0} - 1\right)^2}$$

Where:
- $T$ = Time to expiration (30 days)
- $K_i$ = Strike prices of selected options
- $\Delta K_i$ = Interval between strikes
- $Q(K_i)$ = Mid price of the option at strike $K_i$
- $F$ = Forward price
- $K_0$ = First strike below forward

**DVOL Interpretation:**
- DVOL 50 → Expected 30-day annualized volatility is 50%
- Expected monthly move: $DVOL / \sqrt{12}$ ≈ DVOL × 0.289
  - DVOL 50 → Expected ±14.4% monthly move (1σ)
  - DVOL 80 → Expected ±23.1% monthly move
  - DVOL 120 → Expected ±34.6% monthly move

**Historical DVOL Ranges (BTC):**
- Extreme low: 35-40 (very rare, strong buy vol signal)
- Low: 40-55 (calm markets, potentially good for buying vol)
- Normal: 55-75 (typical range)
- Elevated: 75-100 (active market, premium selling attractive)
- Extreme: 100-150+ (crisis/major events)

#### 1.4.2 DVOL as Trading Signal

| DVOL Level | DVOL Percentile | Action |
|---|---|---|
| < 45 | < 10th | Strong buy vol (straddles, strangles) |
| 45-55 | 10-25th | Buy vol (calendars, ratio spreads) |
| 55-75 | 25-75th | Neutral (balanced approach) |
| 75-90 | 75-90th | Sell vol (iron condors, covered calls) |
| > 90 | > 90th | Aggressive sell vol (but with defined risk) |

### 1.5 Variance Swaps

#### 1.5.1 Overview

A variance swap is an OTC derivative that pays the difference between realized variance and a fixed strike (implied variance). Pure volatility exposure without delta or gamma.

**Payoff:**

$$\text{Payoff} = N_{var} \times (\sigma_{realized}^2 - K_{var})$$

Where:
- $N_{var}$ = Variance notional ($/variance point)
- $\sigma_{realized}^2$ = Realized variance over the period
- $K_{var}$ = Variance strike (implied variance at inception)

**Relationship to Vega Notional:**

$$N_{vega} = N_{var} \times 2K_{vol}$$

Where $K_{vol} = \sqrt{K_{var}}$ is the volatility strike.

#### 1.5.2 Fair Strike

The fair variance swap strike is:

$$K_{var} = \frac{2}{T} \left[rT - \left(\frac{S_0 e^{rT}}{S^*} - 1\right) - \ln\frac{S^*}{S_0} + e^{rT}\int_0^{S^*}\frac{P(K)}{K^2}dK + e^{rT}\int_{S^*}^{\infty}\frac{C(K)}{K^2}dK\right]$$

This shows that the fair variance strike can be replicated by a portfolio of options across all strikes — the theoretical basis for VIX/DVOL calculation.

#### 1.5.3 Variance Swap in Crypto

- Not widely available as a standalone product (few market makers)
- Can be synthesized using a strip of options (static replication)
- Some DeFi protocols offer variance-swap-like products
- Main use: Institutional hedging of vol exposure

### 1.6 Volatility Risk Premium Harvesting

#### 1.6.1 Strategy Overview

Systematic selling of implied volatility to capture the VRP. Since IV > RV on average, selling options is profitable over time (analogous to selling insurance).

**Implementation Methods:**

| Method | Instrument | Complexity | Risk |
|---|---|---|---|
| Short Straddle | Sell ATM call + put | High | Unlimited |
| Short Strangle | Sell OTM call + put | High | Unlimited |
| Iron Condor | Sell OTM spread both sides | Moderate | Defined |
| Covered Call | Sell OTM call on long position | Low | Moderate |
| Variance Swap Short | Pay fixed, receive realized | High | Unlimited |
| DOV Participation | Deposit in DOV vault | Low | Moderate |

#### 1.6.2 VRP Signal Construction

$$VRP_{signal} = \frac{IV_{30d,ATM} - RV_{30d,realized}}{IV_{30d,ATM}}$$

- $VRP_{signal} > 0.15$ (15%): Sell premium aggressively
- $VRP_{signal} \in [0.05, 0.15]$: Sell premium moderately
- $VRP_{signal} \in [-0.05, 0.05]$: Neutral/small positions
- $VRP_{signal} < -0.05$: Buy premium (realized > implied)

### 1.7 Gamma Scalping

#### 1.7.1 Long Gamma Strategy

**Concept:** Buy options (long gamma) and delta-hedge continuously. Profit from realized volatility exceeding implied volatility.

**Setup:**
1. Buy ATM straddle (long gamma, long vega, short theta)
2. Delta-hedge to maintain delta-neutral
3. As price moves up: Delta becomes positive → sell underlying
4. As price moves down: Delta becomes negative → buy underlying
5. Each rebalance "locks in" a small profit from the move

**P&L Decomposition:**

$$\text{P\&L}_{daily} = \frac{1}{2}\Gamma S^2 \left(\frac{\Delta S}{S}\right)^2 - |\Theta|$$

$$\text{P\&L}_{daily} = \frac{1}{2}\Gamma S^2 (\sigma_{realized}^2 - \sigma_{implied}^2) \times dt$$

**Profitable when:** $\sigma_{realized} > \sigma_{implied}$ (realized vol exceeds what you paid for)

**Gamma P&L per rebalance:**

$$\text{Gamma P\&L} = \frac{1}{2} \Gamma \times (\Delta S)^2$$

Where $\Delta S$ is the price move between rebalances.

**Break-even Realized Vol:**

$$\sigma_{breakeven} = \sigma_{implied}$$

If realized vol = implied vol: Gamma P&L exactly offsets theta decay.

#### 1.7.2 Short Gamma Strategy

**Concept:** Sell options (short gamma) and delta-hedge. Profit from realized volatility being less than implied volatility.

**Setup:**
1. Sell ATM straddle (short gamma, short vega, long theta)
2. Delta-hedge to maintain delta-neutral
3. Collect theta decay daily
4. Pay for gamma when price moves and you must rebalance at a loss

**P&L Decomposition:**

$$\text{P\&L}_{daily} = |\Theta| - \frac{1}{2}|\Gamma| S^2 (\sigma_{realized}^2) \times dt$$

**Profitable when:** $\sigma_{realized} < \sigma_{implied}$ (realized vol less than what you sold)

**Risk:** Unlimited loss if a large move occurs (gamma loss on big moves is quadratic)

#### 1.7.3 Gamma Scalping P&L Calculation

**Continuous Hedging (Theoretical):**

$$\text{Total P\&L} = \frac{1}{2}\int_0^T \Gamma_t S_t^2 (\sigma_{realized,t}^2 - \sigma_{implied}^2) dt$$

**Discrete Hedging (Practical):**

$$\text{Total P\&L} = \sum_{i=1}^{N} \frac{1}{2}\Gamma_i (S_{i+1} - S_i)^2 - \sum_{i=1}^{N} |\Theta_i| \times \Delta t - \text{Transaction Costs}$$

**Hedging Frequency Tradeoff:**
- Hedge too frequently: High transaction costs eat into gamma profits
- Hedge too infrequently: Miss moves, effective gamma capture is lower
- Optimal: Balance gamma capture vs transaction costs
- Rule of thumb: Rebalance when delta exceeds a threshold (e.g., 0.10 per lot)

#### 1.7.4 Optimal Rebalancing Band

**Whalley-Wilmott Approximation:**

$$\Delta_{band} = \left(\frac{3c\Gamma}{2\lambda}\right)^{1/3}$$

Where:
- $c$ = Transaction cost per unit
- $\Gamma$ = Current gamma
- $\lambda$ = Risk aversion parameter

Simpler rule of thumb: Rebalance when |portfolio delta| > $\sqrt{2 \times cost \times time / \Gamma}$

### 1.8 Dispersion Trading

#### 1.8.1 Overview

Dispersion trading exploits the difference between implied volatility of an index/basket and the implied volatilities of its components.

**Core Insight:** Index vol < Weighted-average component vol (due to diversification/correlation)

$$\sigma_{index}^2 \approx \sum_i w_i^2 \sigma_i^2 + 2\sum_{i<j} w_i w_j \rho_{ij} \sigma_i \sigma_j$$

If the market overestimates correlation: Index IV will be too high relative to component IVs.

#### 1.8.2 Crypto Dispersion

**Application:** Crypto market has high correlation during stress, low correlation during calm.

**Setup:**
- Sell volatility on "crypto index" or BTC (as proxy for market)
- Buy volatility on individual altcoins (ETH, SOL, AVAX, etc.)
- Profit if: Components are more volatile than the index (correlation breaks down)

**Crypto-Specific Considerations:**
- No standardized crypto index options (construct synthetic basket)
- BTC dominance acts as correlation proxy:
  - High BTC dominance = high correlation (everything follows BTC)
  - Low BTC dominance = low correlation (dispersion opportunity)
- Altcoin seasons = high dispersion = long individual vol, short market vol

**Implementation:**
- Long straddles on individual altcoins (long gamma/vega on components)
- Short straddle on BTC or a BTC-heavy basket (short gamma/vega on index)
- Sized by vega: Ensure net vega is controlled

---

## 2. Technical Specifications

### 2.1 Volatility Data Pipeline

```
VOLATILITY_DATA_PIPELINE:

  DATA_COLLECTION:
    option_prices:
      source: [deribit, okx, binance_options]
      granularity: tick-level (every trade)
      coverage: all strikes × all expiries
      frequency: continuous (WebSocket)

    spot_prices:
      source: [binance, coinbase, kraken, okx]
      granularity: 100ms
      for: IV extraction and RV calculation

    historical_ohlcv:
      source: database (pre-collected)
      granularity: 1-minute candles
      lookback: 2+ years minimum
      for: Realized vol calculation

  PROCESSING_PIPELINE:

    stage_1_iv_extraction:
      method: Newton-Raphson with Jaeckel initial guess
      for_each: (strike, expiry) pair with valid quote
      output: point IV per option
      frequency: every new quote

    stage_2_surface_construction:
      method: SVI or SABR parameterization
      interpolation: cubic spline in moneyness, linear in sqrt(T)
      extrapolation: flat beyond observed range
      arbitrage_check: calendar spread, butterfly arbitrage
      output: smooth IV surface σ(K, T)
      frequency: every 1 second (or on significant change)

    stage_3_rv_calculation:
      methods: [close_to_close, garman_klass, yang_zhang, parkinson]
      windows: [5d, 7d, 14d, 21d, 30d, 60d, 90d]
      output: RV cone (current + percentiles)
      frequency: every 5 minutes

    stage_4_derived_metrics:
      iv_rank: (current ATM IV - 52w low) / (52w high - 52w low)
      iv_percentile: % of days in lookback with lower IV
      vrp: IV_30d - RV_30d
      skew_25d: IV_25d_put - IV_25d_call
      butterfly_25d: (IV_25d_put + IV_25d_call)/2 - IV_ATM
      term_structure_slope: (IV_90d - IV_7d) / (90 - 7)
      dvol_equivalent: computed from option strip (VIX methodology)
      output: complete metrics dashboard
      frequency: every 10 seconds

    stage_5_signal_generation:
      vol_regime: [low, normal, high, extreme]
      vrp_signal: [buy_vol, neutral, sell_vol, aggressive_sell]
      skew_signal: [extreme_put, normal, extreme_call]
      term_signal: [inverted, flat, normal, steep]
      dispersion_signal: correlation-based
      output: trading signals with confidence
      frequency: every 1 minute
```

### 2.2 Volatility Surface Storage

```
VOL_SURFACE_STORAGE:

  schema:
    timestamp: datetime (UTC, millisecond precision)
    underlying: string (BTC, ETH, etc.)
    surface_type: string (raw, fitted_svi, fitted_sabr)
    
    grid:
      moneyness_axis: [-0.5, -0.4, ..., 0, ..., 0.4, 0.5]  # log(K/F)
      time_axis: [1d, 2d, 3d, 7d, 14d, 21d, 30d, 60d, 90d, 180d, 365d]
      values: 2D array of IV values

    parameters:
      svi: {a, b, rho, m, sigma} per expiry
      sabr: {alpha, beta, nu, rho} per expiry
      
    metadata:
      fit_quality: RMSE per expiry
      arbitrage_free: boolean
      data_points_used: int
      interpolated_points: int

  retention:
    tick_level: 7 days
    1_minute_snapshots: 90 days
    hourly_snapshots: 2 years
    daily_snapshots: unlimited
```

### 2.3 Gamma Scalping Engine

```
GAMMA_SCALPING_ENGINE:

  configuration:
    strategy_mode: [long_gamma, short_gamma]
    underlying: BTC or ETH
    hedge_instrument: perpetual_swap
    
    position_setup:
      option_type: straddle or strangle
      strike_selection: ATM (for maximum gamma)
      expiry_selection: 14-30 DTE (balance gamma vs theta)
      position_size: based on vega budget
    
    rebalancing:
      method: [delta_threshold, time_based, combined]
      delta_threshold: 0.05 (rebalance when |delta| > 5% of notional)
      time_interval: 15 minutes (if time-based)
      min_trade_size: $1000 notional (avoid micro-adjustments)
      max_daily_hedges: 50 (cost control)
    
    cost_management:
      maker_fee: 0.02% (use limit orders for hedge)
      taker_fee: 0.05% (market orders only if urgent)
      funding_rate_impact: tracked per position
      slippage_estimate: 0.01% per hedge trade

  monitoring:
    real_time_metrics:
      - current_delta
      - current_gamma (dollar gamma per 1% move)
      - cumulative_gamma_pnl
      - cumulative_theta_cost
      - cumulative_hedge_costs
      - net_pnl
      - realized_vol_vs_implied
      - hedges_today
      - avg_hedge_slippage

    alerts:
      - delta_threshold_approaching
      - large_move_unhedged (>2% without rebalance)
      - realized_vol_exceeding_implied (for long gamma: good)
      - realized_vol_below_implied (for long gamma: bad, consider closing)
      - funding_rate_accumulating (hedge position cost)
```

### 2.4 Dispersion Trading Engine

```
DISPERSION_ENGINE:

  universe:
    index_proxy: BTC (market beta)
    components: [ETH, SOL, AVAX, LINK, UNI, AAVE, etc.]
    weights: market_cap_weighted or equal_weighted
    min_options_liquidity: $1M daily volume per component

  correlation_monitoring:
    method: [rolling_pearson, DCC_GARCH, realized_correlation]
    window: 30 days
    update_frequency: daily
    
    implied_correlation:
      formula: |
        σ_basket² = Σ wi² σi² + 2 Σ wi wj ρij σi σj
        Solve for implied ρ given basket IV and component IVs

    signal:
      implied_corr_high: (> 80th percentile) → sell correlation (long dispersion)
      implied_corr_low: (< 20th percentile) → buy correlation (short dispersion)

  position_construction:
    long_dispersion:
      index_leg: Sell straddle on BTC (short vol on index)
      component_legs: Buy straddles on components (long vol on each)
      sizing: Vega-neutral overall (total component vega = index vega)
    
    short_dispersion:
      index_leg: Buy straddle on BTC
      component_legs: Sell straddles on components
      sizing: Same vega-neutral principle
```

---

## 3. Mathematical Models

### 3.1 SVI (Stochastic Volatility Inspired) Parameterization

The SVI model parameterizes the total implied variance $w = \sigma^2 T$ as a function of log-moneyness $k = \ln(K/F)$:

**Raw SVI:**

$$w(k) = a + b\left(\rho(k-m) + \sqrt{(k-m)^2 + \sigma^2}\right)$$

**Parameters:**
- $a$: Vertical translation (overall variance level)
- $b$: Curvature intensity (smile amplitude)
- $\rho$: Rotation (skew, $\rho \in [-1, 1]$)
- $m$: Horizontal translation (smile center)
- $\sigma$: Smoothness (curvature at the vertex)

**Constraints for Arbitrage-Free Surface:**
- $b \geq 0$
- $a + b\sigma\sqrt{1-\rho^2} \geq 0$ (ensures $w \geq 0$ at the vertex)
- $|\rho| < 1$
- $\sigma > 0$
- Calendar spread arbitrage: $\partial w / \partial T \geq 0$ for all $k$
- Butterfly arbitrage: $g(k) \geq 0$ where $g$ is derived from $w$

**Natural SVI (SSVI):**
For the full surface, parameterize per slice:

$$w_T(k) = \frac{\theta_T}{2}\left(1 + \rho_T \varphi_T k + \sqrt{(\varphi_T k + \rho_T)^2 + (1-\rho_T^2)}\right)$$

Where:
- $\theta_T = \sigma_{ATM}^2 T$ (ATM total variance)
- $\varphi_T$ = function of $\theta_T$ controlling smile shape
- $\rho_T$ = per-slice skew parameter

### 3.2 SABR Model — Complete Framework

**Dynamics:**

$$dF_t = \alpha_t F_t^\beta dW_1(t)$$
$$d\alpha_t = \nu \alpha_t dW_2(t)$$
$$dW_1 dW_2 = \rho \, dt$$

**ATM Implied Volatility:**

$$\sigma_{ATM} \approx \frac{\alpha}{F^{1-\beta}}\left[1 + \left(\frac{(1-\beta)^2\alpha^2}{24F^{2-2\beta}} + \frac{\rho\beta\nu\alpha}{4F^{1-\beta}} + \frac{2-3\rho^2}{24}\nu^2\right)T\right]$$

**Smile Formula (Hagan et al., 2002):**

For $K \neq F$:

$$\sigma(K) = \frac{\alpha \cdot z / x(z)}{(FK)^{(1-\beta)/2}\left[1 + \frac{(1-\beta)^2}{24}\ln^2\frac{F}{K} + \frac{(1-\beta)^4}{1920}\ln^4\frac{F}{K}\right]} \cdot \left[1 + \epsilon T\right]$$

Where:
$$z = \frac{\nu}{\alpha}(FK)^{(1-\beta)/2}\ln\frac{F}{K}$$
$$x(z) = \ln\left(\frac{\sqrt{1-2\rho z + z^2} + z - \rho}{1-\rho}\right)$$
$$\epsilon = \frac{(1-\beta)^2\alpha^2}{24(FK)^{1-\beta}} + \frac{\rho\beta\nu\alpha}{4(FK)^{(1-\beta)/2}} + \frac{(2-3\rho^2)\nu^2}{24}$$

**Calibration Procedure:**
1. Fix $\beta$ (typically 0.5 for crypto, 0 for rates)
2. Use ATM vol to pin $\alpha$
3. Use 25Δ risk reversal to determine $\rho$
4. Use 25Δ butterfly to determine $\nu$
5. Optimize: minimize $\sum (IV_{SABR} - IV_{market})^2$

### 3.3 Heston Model — Volatility Surface

**Dynamics (under risk-neutral measure):**

$$dS_t = rS_t dt + \sqrt{v_t}S_t dW_t^S$$
$$dv_t = \kappa(\theta - v_t)dt + \xi\sqrt{v_t}dW_t^v$$
$$\text{Corr}(dW^S, dW^v) = \rho$$

**Characteristic Function:**

$$\phi(u) = E[e^{iu\ln S_T}] = \exp(C + D v_0 + iu\ln S_0)$$

Where:
$$C = ri u T + \frac{\kappa\theta}{\xi^2}\left[(\kappa - \rho\xi iu + d)T - 2\ln\frac{1-ge^{dT}}{1-g}\right]$$
$$D = \frac{\kappa - \rho\xi iu + d}{\xi^2} \cdot \frac{1-e^{dT}}{1-ge^{dT}}$$
$$d = \sqrt{(\rho\xi iu - \kappa)^2 + \xi^2(iu + u^2)}$$
$$g = \frac{\kappa - \rho\xi iu + d}{\kappa - \rho\xi iu - d}$$

**Option Pricing via Fourier Transform:**

$$C = S_0 P_1 - Ke^{-rT}P_2$$

Where $P_1, P_2$ are computed by numerical integration of the characteristic function.

**Heston Calibration for Crypto:**
- Start with: $v_0 = ATM\_IV^2$, $\theta = v_0$, $\kappa = 2$, $\xi = 1$, $\rho = -0.7$
- Optimize all 5 parameters to minimize the sum of squared IV errors
- Crypto specifics: Higher $\xi$ (vol of vol), $\rho$ closer to -0.5 (less leverage effect than equities)

### 3.4 Realized Variance and Quadratic Variation

**Discrete Realized Variance:**

$$RV_T = \frac{365}{n} \sum_{i=1}^{n} r_i^2$$

Where $r_i = \ln(S_i/S_{i-1})$ (note: mean removed for variance swap purposes, i.e., assume zero mean).

**Continuous Realized Variance (Quadratic Variation):**

$$\langle \ln S \rangle_T = \int_0^T \sigma_t^2 dt$$

In practice, estimated by sum of squared returns at high frequency (5-minute returns preferred to balance microstructure noise vs information).

**Bipower Variation (robust to jumps):**

$$BV_T = \frac{\pi}{2} \frac{365}{n-1} \sum_{i=2}^{n} |r_i| \cdot |r_{i-1}|$$

Bipower variation estimates the continuous component of variance, excluding jumps. Useful for crypto where jumps are frequent.

**Jump Detection:**

$$J_T = RV_T - BV_T$$

If $J_T$ is statistically significant: Jumps contributed to realized variance.

### 3.5 Gamma Scalping Mathematics

**Theta-Gamma Relationship:**

From the BSM PDE for a delta-hedged option portfolio:

$$\Theta + \frac{1}{2}\sigma^2 S^2 \Gamma = rV - rS\Delta$$

For a delta-neutral position ($\Delta_{net} = 0$):

$$\text{Daily P\&L} = \Theta_{daily} + \frac{1}{2}\Gamma S^2 \left(\frac{\Delta S}{S}\right)^2$$

**Expected P&L over interval $dt$:**

$$E[\text{P\&L}] = \frac{1}{2}\Gamma S^2 (\sigma_R^2 - \sigma_I^2) \cdot dt$$

Where $\sigma_R$ = realized vol, $\sigma_I$ = implied vol.

**Variance of P&L (Gamma risk):**

$$\text{Var}[\text{P\&L}] = \frac{1}{2}\Gamma^2 S^4 \sigma^4 \cdot dt$$

The P&L from gamma scalping has fat tails because gains/losses are proportional to the square of price moves.

**Break-Even Realized Volatility:**

For long gamma position (long options): Break-even when $\sigma_R = \sigma_I$

$$\text{Break-even daily move} = S \times \sigma_I \times \sqrt{dt} = S \times \frac{\sigma_I}{\sqrt{365}}$$

Example: BTC at $60,000, IV = 60%
- Daily break-even move: $60,000 × 0.60 / √365 = $1,883 (3.14%)
- If BTC moves more than ±3.14% daily on average: long gamma profitable

### 3.6 Variance Swap Replication

**Static Replication Using Option Strip:**

$$K_{var} = \frac{2e^{rT}}{T}\left[\int_0^F \frac{P(K)}{K^2}dK + \int_F^{\infty}\frac{C(K)}{K^2}dK\right]$$

**Discrete Approximation:**

$$K_{var} \approx \frac{2e^{rT}}{T}\sum_i \frac{\Delta K_i}{K_i^2}Q(K_i)$$

Where:
- $Q(K_i)$ = Out-of-the-money option price at strike $K_i$
- Use puts for $K_i < F$, calls for $K_i > F$
- Weight each option by $1/K^2$ (more weight on lower strikes — skew captured)

**Mark-to-Market of Variance Swap:**

At time $t$ during the swap's life:

$$V_t = \frac{N_{var}}{T}\left[t \cdot RV_{0,t}^2 + (T-t) \cdot K_{var,t,T}^2 - T \cdot K_{var}^2\right] \times e^{-r(T-t)}$$

Where $K_{var,t,T}$ is the current fair variance strike for the remaining period.

---

## 4. Risk Parameters

### 4.1 Volatility Trading Risk Limits

```
VOL_TRADING_RISK_LIMITS:

  vega_limits:
    max_portfolio_vega: 1.5% of NAV per vol point
    max_single_underlying_vega: 0.75% of NAV per vol point
    max_long_vega: 2% of NAV per vol point
    max_short_vega: 1% of NAV per vol point (asymmetric — short vol more dangerous)

  gamma_limits:
    max_long_gamma: 3% of NAV per 1% spot move (squared)
    max_short_gamma: 1.5% of NAV per 1% spot move (more conservative short)
    max_short_gamma_near_expiry: 0.5% (gamma explosion risk)
    min_DTE_for_short_gamma: 14 days

  theta_limits:
    max_daily_theta_cost: 0.3% of NAV (long gamma)
    max_daily_theta_income: 0.5% of NAV (short gamma)
    note: "Theta income = payment for bearing gamma risk"

  position_limits:
    max_straddle_notional: 10% of NAV per position
    max_total_vol_positions: 20% of NAV (by premium)
    max_dispersion_position: 5% of NAV (complexity risk)
    max_calendar_spread_vega: 0.5% per vol point per position

  vrp_strategy_limits:
    min_iv_rank_to_sell: 40 (don't sell cheap vol)
    max_iv_rank_to_buy: 60 (don't buy expensive vol)
    min_vrp_to_sell: 5 vol points (enough edge to cover costs + risk)
    max_holding_period: 45 days per position
    profit_target: 50% of theoretical VRP captured
    stop_loss: 200% of expected theta income

  gamma_scalping_limits:
    max_position_gamma_dollars: 2% of NAV per 1% move
    max_daily_hedge_transactions: 50
    max_daily_hedge_cost: 0.1% of NAV (transaction costs)
    min_realized_vs_implied_edge: 5 vol points (to justify costs)
    rebalance_delta_threshold: 0.05 per lot
    mandatory_close_at_DTE: 7 (avoid expiry gamma explosion)
```

### 4.2 Scenario Analysis for Volatility Strategies

```
VOL_STRATEGY_SCENARIOS:

  scenario_1_vol_crush_20pts:
    description: "IV drops 20 vol points suddenly (e.g., after FOMC/event)"
    impact:
      long_gamma_straddle: -20 × vega per contract (large loss)
      short_gamma_straddle: +20 × vega per contract (large gain)
      long_calendar: depends on term structure change
      dispersion_long: index vol down → gain on short leg; component vol down → loss on long legs; net depends
    action:
      long_gamma: Close immediately if thesis (event catalyst) has passed
      short_gamma: Take profits (50%+ of max credit)

  scenario_2_vol_spike_30pts:
    description: "IV spikes 30 vol points (market panic, black swan)"
    impact:
      long_gamma_straddle: +30 × vega + gamma gains from directional move
      short_gamma_straddle: -30 × vega + gamma losses (CATASTROPHIC)
      covered_call: Limited benefit (already short vega)
    action:
      long_gamma: Excellent — take partial profits, trail
      short_gamma: EMERGENCY close, accept loss, do NOT average down
      key_lesson: "One vol spike can erase months of short gamma profits"

  scenario_3_low_realized_vol:
    description: "Market barely moves for 2 weeks (RV << IV)"
    impact:
      long_gamma: Theta decay without gamma P&L → consistent bleeding
      short_gamma: Maximum theta collection → ideal scenario
      iron_condors: Maximum decay → approaching max profit
    action:
      long_gamma: Reduce position or close (thesis failed)
      short_gamma: Let theta accumulate, tighten profit target

  scenario_4_high_realized_choppy:
    description: "Market moves 3-5% daily in both directions (high RV, mean-reverting)"
    impact:
      long_gamma with hedging: IDEAL — gamma scalping profits exceed theta cost
      short_gamma: Challenging but not catastrophic if defined risk (iron condor)
      straddle_no_hedge: Depends on net direction
    action:
      long_gamma: Continue scalping, ensure hedge frequency is optimal
      short_gamma: Monitor closely, may need to widen or close

  scenario_5_trending_market:
    description: "Market moves 20% in one direction over 10 days"
    impact:
      long_gamma_hedged: Moderate gain (hedging caps directional profit)
      long_gamma_unhedged: Large gain on one leg, loss on other (net depends on premium paid)
      short_gamma: Catastrophic if unhedged; managed if iron condor (capped loss)
    action:
      long_gamma: If hedging, gamma profits from each step are captured
      short_gamma: Defined-risk structures survive; naked positions may be stopped out
```

### 4.3 Greeks Risk Attribution

```
GREEKS_ATTRIBUTION:

  daily_pnl_decomposition:
    delta_pnl: Δ × ΔS (directional component)
    gamma_pnl: 0.5 × Γ × (ΔS)² (convexity component)
    theta_pnl: Θ × Δt (time decay component)
    vega_pnl: ν × Δσ (vol change component)
    vanna_pnl: Vanna × ΔS × Δσ (cross term)
    volga_pnl: 0.5 × Volga × (Δσ)² (vol convexity)
    rho_pnl: ρ × Δr (rate change, usually minimal for crypto)
    residual: Total P&L - sum of above (higher-order + transaction costs)

  target_attribution:
    for_gamma_scalping:
      primary_income: gamma_pnl (should be positive if RV > IV)
      primary_cost: theta_pnl (should be negative for long gamma)
      secondary: hedge_transaction_costs
      target: gamma_pnl > |theta_pnl| + transaction_costs

    for_vrp_harvesting:
      primary_income: theta_pnl (time decay collected)
      primary_cost: gamma_pnl (losses from moves against)
      secondary: vega_pnl (changes in IV level)
      target: theta_pnl > |gamma_pnl| + |adverse_vega_pnl|

    for_dispersion:
      primary_income: correlation_premium (implicit in index vs component pricing)
      target: net_vega_pnl from correlation reversion
```

---

## 5. Execution Flow

### 5.1 Volatility Trading Bot — Complete Execution Algorithm

```
VOLATILITY_TRADING_BOT:

  ╔══════════════════════════════════════════════════════════╗
  ║  STEP 1: VOLATILITY REGIME IDENTIFICATION (every 5 min)  ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  1.1 Calculate current IV metrics:                       ║
  ║      - ATM IV (30-day): primary volatility level         ║
  ║      - IV Rank (52-week)                                 ║
  ║      - IV Percentile (252-day)                           ║
  ║      - DVOL level                                        ║
  ║                                                          ║
  ║  1.2 Calculate realized vol metrics:                     ║
  ║      - RV windows: 5d, 7d, 14d, 21d, 30d               ║
  ║      - RV estimators: CC, Parkinson, GK, YZ             ║
  ║      - RV percentile                                     ║
  ║                                                          ║
  ║  1.3 Calculate Volatility Risk Premium:                  ║
  ║      - VRP = IV_30d - RV_30d                            ║
  ║      - VRP_normalized = VRP / IV_30d                     ║
  ║      - VRP percentile (vs historical)                    ║
  ║                                                          ║
  ║  1.4 Calculate surface metrics:                          ║
  ║      - 25Δ Risk Reversal                                 ║
  ║      - 25Δ Butterfly                                     ║
  ║      - Term structure slope                              ║
  ║      - Surface fit quality (RMSE)                        ║
  ║                                                          ║
  ║  1.5 Classify regime:                                    ║
  ║      REGIME_A: Low IV + Low RV → "Calm" → BUY VOL       ║
  ║      REGIME_B: High IV + Low RV → "Rich Premium" → SELL ║
  ║      REGIME_C: Low IV + High RV → "Cheap Vol" → BUY     ║
  ║      REGIME_D: High IV + High RV → "Crisis" → CAUTION   ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 2: STRATEGY SELECTION                              ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  REGIME_A (Calm, Low IV):                                ║
  ║  → Long straddle/strangle (buy cheap vol)                ║
  ║  → Calendar spread (buy far-dated cheap vol)             ║
  ║  → Expect vol expansion                                  ║
  ║                                                          ║
  ║  REGIME_B (Rich Premium, High IV + Low RV):              ║
  ║  → Short straddle/strangle (sell rich vol)               ║
  ║  → Iron condor (defined risk vol selling)                ║
  ║  → VRP harvesting (systematic selling)                   ║
  ║  → DOV participation (sell premium passively)            ║
  ║                                                          ║
  ║  REGIME_C (Cheap Vol, Low IV + High RV):                 ║
  ║  → Long gamma scalping (RV > IV = gamma profits)         ║
  ║  → Buy straddles and actively hedge                      ║
  ║  → This regime is RARE but very profitable for long vol  ║
  ║                                                          ║
  ║  REGIME_D (Crisis, High IV + High RV):                   ║
  ║  → CAUTION: Do not initiate new vol selling              ║
  ║  → If already long gamma: Let it ride (profits accruing) ║
  ║  → If already short gamma: CLOSE or tightly manage       ║
  ║  → Consider hedging tail risk (buy OTM puts)             ║
  ║  → Wait for regime change before new positions           ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 3: POSITION CONSTRUCTION                           ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  3.1 FOR VRP SELLING (Iron Condor example):              ║
  ║      a. Select expiry: 30-45 DTE                         ║
  ║      b. Select short strikes: 1σ OTM (16Δ each side)    ║
  ║      c. Select wing width: 50-100% of short strike dist  ║
  ║      d. Size: Max risk = 2% of portfolio per trade       ║
  ║      e. Expected edge = VRP × remaining_time             ║
  ║                                                          ║
  ║  3.2 FOR GAMMA SCALPING (Long Straddle + Hedge):         ║
  ║      a. Select expiry: 21-30 DTE                         ║
  ║      b. Strike: ATM (maximum gamma)                      ║
  ║      c. Size: Based on theta budget (max 0.3% daily)     ║
  ║      d. Hedge instrument: Perpetual swap                 ║
  ║      e. Rebalance threshold: |delta| > 0.05 per lot      ║
  ║                                                          ║
  ║  3.3 FOR CALENDAR SPREAD:                                ║
  ║      a. Near-term: Sell 14-21 DTE                        ║
  ║      b. Far-term: Buy 45-60 DTE                          ║
  ║      c. Strike: ATM                                      ║
  ║      d. Net debit = long premium - short premium         ║
  ║      e. Profit from: Near-term faster theta decay        ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 4: RISK VERIFICATION                               ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  □ Portfolio vega within limits                          ║
  ║  □ Portfolio gamma within limits                         ║
  ║  □ Portfolio theta within limits                         ║
  ║  □ Scenario analysis passed:                             ║
  ║    - Spot ±10%: P&L acceptable                           ║
  ║    - IV ±20 pts: P&L acceptable                          ║
  ║    - Combined: Spot -15% AND IV +30pts: survivable       ║
  ║  □ Margin available                                      ║
  ║  □ Concentration limits OK                               ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 5: EXECUTION                                       ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  5.1 Multi-leg execution:                                ║
  ║      - Use combo orders if available (Deribit supports)   ║
  ║      - If not: execute most liquid leg first              ║
  ║      - Mid-price start, walk toward aggressive over 30s  ║
  ║                                                          ║
  ║  5.2 Gamma scalping initial hedge:                       ║
  ║      - After straddle is filled                          ║
  ║      - Calculate initial delta                           ║
  ║      - Hedge to delta-neutral via perp                   ║
  ║                                                          ║
  ║  5.3 Confirm:                                            ║
  ║      - All legs filled                                   ║
  ║      - Net Greeks match expected                         ║
  ║      - Hedge in place (if applicable)                    ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 6: ACTIVE MANAGEMENT                               ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  FOR VRP SELLING:                                        ║
  ║  6.1 Monitor P&L vs target (50% of credit → close)      ║
  ║  6.2 Monitor IV changes (if IV drops, position gains)    ║
  ║  6.3 Stop loss: 2x credit received                       ║
  ║  6.4 Time exit: 21 DTE (gamma risk increases)            ║
  ║  6.5 Adjustment if tested: Roll untested side closer     ║
  ║                                                          ║
  ║  FOR GAMMA SCALPING:                                     ║
  ║  6.1 Continuous delta monitoring (every tick)             ║
  ║  6.2 When |delta| > threshold: REBALANCE                 ║
  ║      a. Calculate hedge quantity                          ║
  ║      b. Submit hedge order (limit at mid)                ║
  ║      c. Record gamma P&L from the rebalance              ║
  ║  6.3 Track cumulative:                                   ║
  ║      - Gamma P&L (from all rebalances)                   ║
  ║      - Theta cost (daily decay)                          ║
  ║      - Transaction costs (from hedging)                  ║
  ║      - Net P&L = Gamma - Theta - Costs                   ║
  ║  6.4 Daily assessment:                                   ║
  ║      - Is realized vol > implied vol? (Strategy working) ║
  ║      - If RV < IV for 5+ days: Consider closing          ║
  ║                                                          ║
  ║  FOR CALENDAR SPREAD:                                    ║
  ║  6.1 Monitor spot vs strike (want to stay near strike)   ║
  ║  6.2 Monitor term structure changes                      ║
  ║  6.3 Near-term expiry approaching: close or roll         ║
  ║  6.4 Profit target: 25-40% of debit                     ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 7: EXIT & POST-TRADE                               ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  7.1 Exit conditions met (profit/loss/time/regime)       ║
  ║  7.2 Close all legs + hedges simultaneously              ║
  ║  7.3 Record:                                             ║
  ║      - Entry IV vs Exit IV                               ║
  ║      - Realized vol during holding period                ║
  ║      - VRP captured vs expected                          ║
  ║      - Greeks P&L attribution                            ║
  ║      - Transaction costs total                           ║
  ║  7.4 Update strategy metrics:                            ║
  ║      - Sharpe ratio of vol strategy                      ║
  ║      - Win rate by regime                                ║
  ║      - Average holding period                            ║
  ║      - VRP capture efficiency                            ║
  ║  7.5 Feed to optimizer:                                  ║
  ║      - Optimal hedge frequency (gamma scalping)          ║
  ║      - Optimal DTE selection                             ║
  ║      - Optimal delta threshold                           ║
  ║      - IV Rank thresholds for entry/exit                 ║
  ║                                                          ║
  ╚══════════════════════════════════════════════════════════╝
```

### 5.2 Real-Time Volatility Surface Monitoring

```
VOL_SURFACE_MONITOR:

  CONTINUOUS_CHECKS (every 10 seconds):
    
    1. ATM IV change alert:
       IF |IV_current - IV_5min_ago| > 3 vol points:
         → ALERT: Significant IV move
         → Reassess all vol positions
    
    2. Skew change alert:
       IF |RR_25d_current - RR_25d_1hour_ago| > 2 vol points:
         → ALERT: Skew shifting
         → Check if positions are skew-exposed
    
    3. Term structure change:
       IF term_structure flips (contango → backwardation or vice versa):
         → ALERT: Term structure inversion
         → Calendar spreads may be affected
    
    4. Arbitrage detection:
       IF calendar_spread_arbitrage_detected:
         → ALERT: Trade opportunity
         → Submit spread order immediately
       IF butterfly_arbitrage_detected:
         → ALERT: Trade opportunity
    
    5. Unusual activity:
       IF option_volume > 5x average at specific strike:
         → ALERT: Large flow detected
         → Analyze: Is this hedging or positioning?
         → May front-run vol impact

  DAILY_TASKS:
    
    1. Recalibrate SABR/SVI parameters to closing surface
    2. Update volatility cone (RV percentiles)
    3. Compute IV vs RV divergence signal
    4. Generate vol regime classification
    5. Report: Portfolio vega, gamma, theta attribution for the day
    6. Backtest: Would today's signals have been profitable historically?
```

### 5.3 Dispersion Trading Flow

```
DISPERSION_TRADING_FLOW:

  STEP 1: CORRELATION ASSESSMENT (daily)
    1.1 Calculate 30-day realized correlation matrix
    1.2 Calculate implied correlation from options (index vs components)
    1.3 Compute correlation risk premium:
        CRP = implied_correlation - realized_correlation
    1.4 Signal: IF CRP > historical 75th percentile → long dispersion

  STEP 2: TRADE CONSTRUCTION
    2.1 Index leg: Short ATM straddle on BTC (or basket)
    2.2 Component legs: Long ATM straddles on ETH, SOL, AVAX, etc.
    2.3 Sizing: Vega-neutral overall
        Σ(component_vega × weight) = index_vega_sold
    2.4 Verify: Net portfolio delta ≈ 0, net vega ≈ 0
        (Dispersion trade should be pure correlation bet)

  STEP 3: MONITORING
    3.1 Track realized correlation daily
    3.2 Compare: Is correlation declining? (profitable for long dispersion)
    3.3 Rebalance if correlation exposure drifts
    3.4 Profit target: 2-3% of capital deployed
    3.5 Stop loss: 3-4% of capital deployed

  STEP 4: EXIT
    4.1 Correlation normalizes (CRP returns to median) → take profit
    4.2 Stop loss triggered → close all legs
    4.3 Approaching expiry → close to avoid gamma risk
    4.4 All legs must be closed simultaneously
```

---

## 6. References

### Academic Literature

1. **Hagan, P.S., Kumar, D., Lesniewski, A.S., & Woodward, D.E.** (2002). "Managing Smile Risk." *Wilmott Magazine*, September 2002, 84-108.
2. **Gatheral, J.** (2004). "A Parsimonious Arbitrage-Free Implied Volatility Parameterization with Application to the Valuation of Volatility Derivatives." Presentation at Global Derivatives & Risk Management, Madrid.
3. **Heston, S.L.** (1993). "A Closed-Form Solution for Options with Stochastic Volatility." *Review of Financial Studies*, 6(2), 327-343.
4. **Dupire, B.** (1994). "Pricing with a Smile." *Risk*, 7(1), 18-20.
5. **Carr, P., & Madan, D.** (1998). "Towards a Theory of Volatility Trading." In *Volatility: New Estimation Techniques for Pricing Derivatives*, Risk Books.
6. **Demeterfi, K., Derman, E., Kamal, M., & Zou, J.** (1999). "A Guide to Volatility and Variance Swaps." *Journal of Derivatives*, 6(4), 9-32.
7. **Bollerslev, T., Tauchen, G., & Zhou, H.** (2009). "Expected Stock Returns and Variance Risk Premia." *Review of Financial Studies*, 22(11), 4463-4492.
8. **Whalley, A.E., & Wilmott, P.** (1997). "An Asymptotic Analysis of an Optimal Hedging Model for Option Pricing with Transaction Costs." *Mathematical Finance*, 7(3), 307-324.

### Textbooks

9. **Gatheral, J.** (2006). *The Volatility Surface: A Practitioner's Guide*. Wiley.
10. **Sinclair, E.** (2013). *Volatility Trading* (2nd Edition). Wiley.
11. **Taleb, N.N.** (1997). *Dynamic Hedging: Managing Vanilla and Exotic Options*. Wiley.
12. **Natenberg, S.** (2015). *Option Volatility and Pricing* (2nd Edition). McGraw-Hill.
13. **Bennett, C.** (2014). *Trading Volatility: Trading Volatility, Correlation, Term Structure and Skew*. CreateSpace.
14. **Bossu, S.** (2014). *Advanced Equity Derivatives: Volatility and Correlation*. Wiley.
15. **Rebonato, R.** (2004). *Volatility and Correlation: The Perfect Hedger and the Fox* (2nd Edition). Wiley.

### Crypto Volatility Resources

16. **Deribit DVOL** — Methodology documentation. https://www.deribit.com/kb/dvol
17. **Amberdata** — Crypto volatility surface data and analytics.
18. **Block Scholes** — Crypto derivatives analytics, IV surfaces.
19. **Laevitas** — Real-time crypto options analytics and vol monitoring.
20. **The Block Research** — Crypto volatility studies and market structure.
21. **Paradigm** — Institutional crypto vol trading platform.

### Implementation References

22. **QuantLib** — Heston model, SABR calibration, variance swap pricing.
23. **Vollib** — Python implied vol calculation and Greeks.
24. **arch** — Python package for GARCH models (volatility forecasting).
25. **Jaeckel, P.** (2017). "Let's Be Rational" — Efficient implied vol computation.

---

> **Note to AI Agents:** This document covers the volatility trading framework.
> Key operational priorities:
> 1. ALWAYS classify the vol regime before trading (use IV Rank + RV comparison)
> 2. VRP harvesting is the highest-Sharpe vol strategy but has tail risk
> 3. Gamma scalping requires precise transaction cost management
> 4. NEVER sell vol in REGIME_D (crisis) — wait for regime change
> 5. Dispersion trading is capital-intensive and requires multi-asset liquidity
> 6. DVOL (crypto VIX equivalent) is the primary vol-level signal
> 7. Short gamma positions must ALWAYS have defined risk or tight stops
> 8. Vol surfaces must be rebuilt every second for real-time trading
>
> Related documents:
> - `01_options_strategies.md` — Options strategies used in vol trading
> - `03_structured_products.md` — Products that monetize vol selling
> - `05_risk_management_framework.md` — Portfolio risk limits for vol exposure
