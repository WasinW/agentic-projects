# Portfolio Risk Management Framework

> **Axis 2 — Financial Products | Module 03: Derivatives & Structured Products**
> **Document 05 — Portfolio Risk Management Framework**
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

### 1.1 Risk Management Philosophy

The risk management framework serves as the ultimate gatekeeper for all trading decisions within the Multi-Agent AI Trading System. No position is opened, adjusted, or closed without passing through this framework.

**Core Principles:**
1. **Capital Preservation First**: Survival is paramount. A system that loses all capital cannot recover.
2. **Risk Budgeting**: Every strategy has a defined risk allocation; aggregate risk is bounded.
3. **Tail Risk Awareness**: Traditional risk metrics (VaR) underestimate tail events; use CVaR and stress tests.
4. **Dynamic Adjustment**: Risk limits adapt to market conditions (tighter in volatile regimes).
5. **Independence Verification**: Correlations break in crises; don't assume diversification persists.
6. **Transparency**: All risk metrics are observable, loggable, and auditable in real-time.

### 1.2 Value at Risk (VaR)

#### 1.2.1 Overview

Value at Risk estimates the maximum expected loss over a specified time horizon at a given confidence level.

**Definition:**

$$P(Loss > VaR_\alpha) = 1 - \alpha$$

Where $\alpha$ is the confidence level (typically 95% or 99%).

**Interpretation:** "We are $\alpha$% confident that the portfolio will not lose more than $VaR_\alpha$ over the next [time horizon]."

#### 1.2.2 Historical VaR

**Method:** Use actual historical returns to determine the loss threshold.

**Algorithm:**
1. Collect $n$ historical daily returns: $r_1, r_2, ..., r_n$
2. Sort returns from worst to best
3. VaR at confidence $\alpha$ = the $(1-\alpha) \times n$-th worst return
4. For 95% VaR with 1000 days: the 50th worst return

**Advantages:**
- No distributional assumptions
- Captures fat tails if present in history
- Easy to compute and understand

**Disadvantages:**
- Assumes future will resemble the past
- Limited by available history (crypto has short history)
- Ghost features: Old extreme events drop out of the window
- Does not extrapolate beyond observed history

**Implementation:**

$$VaR_{hist, \alpha} = -\text{Percentile}(R_{portfolio}, 1-\alpha)$$

Where $R_{portfolio}$ is the vector of historical portfolio returns.

**Lookback Periods for Crypto:**
- Short-term: 90 days (captures recent regime)
- Medium-term: 365 days (captures full cycle)
- Long-term: Full available history (captures multiple regimes)
- Recommended: Use weighted combination (EWMA weighting on historical returns)

#### 1.2.3 Parametric VaR (Variance-Covariance Method)

**Assumption:** Portfolio returns are normally distributed.

**Formula:**

$$VaR_\alpha = -(\mu_P - z_\alpha \sigma_P)$$

For daily VaR (assuming $\mu \approx 0$ for daily):

$$VaR_\alpha = z_\alpha \times \sigma_P$$

Where:
- $z_\alpha$ = Standard normal quantile ($z_{0.95} = 1.645$, $z_{0.99} = 2.326$)
- $\sigma_P$ = Portfolio standard deviation
- $\mu_P$ = Portfolio expected return (often set to 0 for short horizons)

**Multi-Asset Portfolio:**

$$\sigma_P^2 = \mathbf{w}^T \Sigma \mathbf{w}$$

Where:
- $\mathbf{w}$ = Vector of portfolio weights
- $\Sigma$ = Covariance matrix of asset returns

**Multi-Day Scaling (Square Root of Time):**

$$VaR_{T-day} = VaR_{1-day} \times \sqrt{T}$$

Valid under i.i.d. returns assumption (approximately holds for short horizons).

**Limitations for Crypto:**
- Crypto returns are NOT normal (fat tails, skewness)
- Significantly underestimates tail risk
- Better as a lower bound or for relative comparison
- Use Cornish-Fisher expansion to adjust for skewness and kurtosis:

$$VaR_{CF} = -\left(\mu + \sigma\left(z + \frac{(z^2-1)S}{6} + \frac{(z^3-3z)K}{24} - \frac{(2z^3-5z)S^2}{36}\right)\right)$$

Where $S$ = skewness, $K$ = excess kurtosis.

#### 1.2.4 Monte Carlo VaR

**Method:** Simulate many possible portfolio return scenarios and derive VaR from the simulated distribution.

**Algorithm:**
1. Estimate return distribution parameters (mean, vol, correlation, skew, kurtosis)
2. Choose a stochastic process (GBM, jump-diffusion, Heston, etc.)
3. Generate $N$ simulated portfolio return paths (e.g., $N = 100,000$)
4. For each path, calculate the portfolio return over the horizon
5. Sort simulated returns
6. VaR = percentile of the simulated distribution

**Advantages:**
- Flexible: Can incorporate any distribution, fat tails, jumps, stochastic vol
- Handles complex portfolios (options, structured products) naturally
- Can model non-linear payoffs

**Disadvantages:**
- Computationally expensive
- Results depend on model assumptions
- Requires careful calibration

**For Options Portfolios:**
Monte Carlo VaR must re-price all options under each scenario:
1. Simulate $S_T$ for each path
2. Re-calculate option prices using BSM/Heston with simulated $S_T$ and $\sigma_T$
3. Calculate portfolio value change
4. This captures the non-linear nature of options

**Pseudo-Code:**
```
FOR i = 1 to N_simulations:
    # Simulate correlated asset returns
    Z = random_normal(n_assets)
    Z_corr = Cholesky(Σ) × Z
    
    # Simulate each asset
    FOR each asset j:
        ΔS_j = S_j × (μ_j×dt + σ_j×√dt×Z_corr_j)  # basic GBM
        # OR use jump-diffusion for crypto:
        ΔS_j += S_j × J_j × Poisson(λ×dt)  # jumps
    
    # Re-price all positions
    portfolio_value_i = Σ(position_k × price_k(new_S, new_σ))
    pnl_i = portfolio_value_i - portfolio_value_current

VaR_α = -Percentile(pnl, 1-α)
```

### 1.3 Expected Shortfall (CVaR)

#### 1.3.1 Definition

Expected Shortfall (also called Conditional VaR or CVaR) measures the expected loss given that the loss exceeds VaR. It answers: "If things go badly (beyond VaR), how bad on average?"

$$ES_\alpha = CVaR_\alpha = -E[R | R \leq -VaR_\alpha]$$

$$CVaR_\alpha = -\frac{1}{1-\alpha}\int_0^{1-\alpha} VaR_u \, du$$

**For Discrete Returns:**

$$CVaR_\alpha = -\frac{1}{\lfloor(1-\alpha)n\rfloor}\sum_{i=1}^{\lfloor(1-\alpha)n\rfloor} r_{(i)}$$

Where $r_{(i)}$ is the $i$-th worst return.

#### 1.3.2 Advantages Over VaR

| Property | VaR | CVaR |
|---|---|---|
| Sub-additivity | No (can violate) | Yes (always) |
| Tail information | None (just a quantile) | Average of tail |
| Coherent risk measure | No | Yes |
| Optimization friendly | Not convex | Convex |
| Regulatory acceptance | Basel (banking) | Preferred by FRTB |

#### 1.3.3 Parametric CVaR (Normal Distribution)

$$CVaR_\alpha = \mu + \sigma \times \frac{\phi(z_\alpha)}{1-\alpha}$$

Where $\phi(z) = \frac{1}{\sqrt{2\pi}}e^{-z^2/2}$ is the standard normal PDF.

**Example:**
- $\sigma = 5\%$ daily, $\alpha = 0.95$
- $VaR_{0.95} = 1.645 \times 5\% = 8.23\%$
- $CVaR_{0.95} = 5\% \times \frac{\phi(1.645)}{0.05} = 5\% \times \frac{0.1031}{0.05} = 10.31\%$

For crypto (daily vol ~3-5%): CVaR can easily be 8-15% for a single-asset position.

### 1.4 Position Sizing

#### 1.4.1 Kelly Criterion

The Kelly Criterion determines the optimal fraction of capital to allocate to a bet/trade to maximize long-term geometric growth.

**Basic Kelly (Binary Outcome):**

$$f^* = \frac{bp - q}{b}$$

Where:
- $f^*$ = Optimal fraction of bankroll
- $b$ = Net odds received (profit/risk ratio)
- $p$ = Probability of winning
- $q$ = 1 - p = Probability of losing

**Continuous Kelly (for continuous returns):**

$$f^* = \frac{\mu - r_f}{\sigma^2}$$

Where:
- $\mu$ = Expected return of the strategy
- $r_f$ = Risk-free rate
- $\sigma^2$ = Variance of returns

**Kelly for a Portfolio (Multiple Assets):**

$$\mathbf{f}^* = \Sigma^{-1}(\boldsymbol{\mu} - r_f \mathbf{1})$$

Where:
- $\mathbf{f}^*$ = Vector of optimal allocations
- $\Sigma^{-1}$ = Inverse covariance matrix
- $\boldsymbol{\mu}$ = Vector of expected returns

#### 1.4.2 Fractional Kelly

Full Kelly maximizes growth but at the cost of extreme volatility and drawdowns. Fractional Kelly uses a fraction of the optimal Kelly size.

$$f_{actual} = \alpha \times f^* \quad \text{where } \alpha \in [0.1, 0.5]$$

**Recommended fractions:**

| Strategy Type | Kelly Fraction | Reasoning |
|---|---|---|
| High-confidence arb | 0.50 | Strong edge, low variance |
| Moderate-edge options | 0.25-0.33 | Reasonable edge, fat tails |
| Directional trades | 0.20-0.25 | Higher uncertainty |
| Speculative/exploratory | 0.10-0.15 | Low confidence in edge estimate |

**Properties of Fractional Kelly:**
- Half-Kelly: 75% of the growth rate, 50% of the variance
- Quarter-Kelly: 50% of the growth rate, 25% of the variance
- Reduces probability of ruin significantly

#### 1.4.3 Fixed Fractional Position Sizing

**Method:** Risk a fixed percentage of portfolio on each trade.

$$\text{Position Size} = \frac{\text{Account Equity} \times \text{Risk Percentage}}{\text{Risk Per Unit (Stop Distance)}}$$

**Example:**
- Account: $100,000
- Risk per trade: 2%
- Stop distance: 5% below entry
- Position size = $100,000 × 0.02 / 0.05 = $40,000 notional

**Advantages:**
- Simple to implement
- Automatic position reduction after losses (protects capital)
- Automatic position increase after gains (compounds)

**For Options:**
- Risk per trade = maximum premium at risk
- For defined-risk spreads: Risk = max loss of the spread
- For undefined-risk: Risk = stop-loss point × position size

#### 1.4.4 Volatility-Adjusted Position Sizing

$$\text{Position Size} = \frac{\text{Target Volatility} \times \text{Account Equity}}{\text{Asset Volatility} \times \text{Price}}$$

**Example:**
- Target portfolio vol contribution: 1% daily per position
- BTC daily vol: 3%
- Account: $100,000
- Position size = 0.01 × $100,000 / 0.03 = $33,333 notional in BTC

This ensures each position contributes equally to portfolio risk regardless of underlying volatility.

### 1.5 Maximum Drawdown Management

#### 1.5.1 Drawdown Definition

$$DD_t = \frac{P_t - P_{peak}}{P_{peak}} = \frac{P_t}{\max_{s \leq t} P_s} - 1$$

$$MDD = \min_t DD_t = \min_t \left(\frac{P_t}{\max_{s \leq t} P_s} - 1\right)$$

**Maximum Drawdown Duration:** The time from peak to recovery of that peak.

#### 1.5.2 Drawdown-Based Risk Controls

```
DRAWDOWN_CONTROLS:

  LEVEL_1 (Yellow): Drawdown reaches 5%
    action:
      - Reduce new position sizes by 25%
      - Tighten stop-losses on existing positions
      - Review and confirm all positions are still valid
      - Alert: "Elevated drawdown - caution mode"

  LEVEL_2 (Orange): Drawdown reaches 10%
    action:
      - Reduce new position sizes by 50%
      - Close weakest positions (lowest conviction)
      - No new speculative trades
      - Only hedging and highest-conviction strategies
      - Alert: "Significant drawdown - defensive mode"

  LEVEL_3 (Red): Drawdown reaches 15%
    action:
      - Halt all new position opening
      - Reduce overall exposure by 50%
      - Only fully hedged positions maintained
      - Manual review required to resume
      - Alert: "CRITICAL drawdown - halt mode"

  LEVEL_4 (Black): Drawdown reaches 25%
    action:
      - FULL SYSTEM HALT
      - Close all positions except long-term holds
      - Manual intervention required
      - Post-mortem analysis before resumption
      - Minimum 48-hour cooling period
      - Alert: "SYSTEM HALT - maximum drawdown breached"
```

#### 1.5.3 Expected Maximum Drawdown

For a strategy with Sharpe ratio $SR$ and time period $T$ (in years):

$$E[MDD] \approx \sigma \times \sqrt{2 \times \ln(SR \times \sqrt{T/2\pi})} / SR$$

**Approximation (for normally distributed returns):**

$$E[MDD] \approx 2\sigma\sqrt{T} / \sqrt{\pi} \quad \text{(for drift = 0)}$$

**Calmar Ratio (return per unit drawdown):**

$$\text{Calmar} = \frac{\text{Annualized Return}}{|MDD|}$$

Target: Calmar > 1.0 (preferably > 2.0)

### 1.6 Correlation Risk

#### 1.6.1 The Correlation Problem in Crypto

Crypto assets exhibit:
- **High correlation during stress**: All crypto drops together in a crash
- **Variable correlation in calm**: Altcoins can diverge from BTC during "alt seasons"
- **Regime-dependent**: Correlation structure shifts dramatically between bull/bear/crisis

**Implications:**
- Diversification benefits are unreliable
- Portfolio risk is underestimated if calm-period correlations are used
- Must stress-test with crisis correlations (ρ → 0.90-0.95 for crypto basket)

#### 1.6.2 Correlation Matrix Estimation

**Sample Correlation (basic):**

$$\rho_{ij} = \frac{\sum_t (r_{i,t} - \bar{r}_i)(r_{j,t} - \bar{r}_j)}{\sqrt{\sum_t(r_{i,t}-\bar{r}_i)^2 \sum_t(r_{j,t}-\bar{r}_j)^2}}$$

**Exponentially Weighted (EWMA):**

$$\hat{\sigma}_{ij,t} = \lambda \hat{\sigma}_{ij,t-1} + (1-\lambda) r_{i,t} r_{j,t}$$

$$\hat{\rho}_{ij,t} = \frac{\hat{\sigma}_{ij,t}}{\hat{\sigma}_{i,t} \hat{\sigma}_{j,t}}$$

Typical $\lambda = 0.94$ (RiskMetrics standard).

**DCC-GARCH (Dynamic Conditional Correlation):**
- Most sophisticated for time-varying correlations
- Captures both volatility clustering and correlation dynamics
- Recommended for production risk systems

#### 1.6.3 Tail Dependence

Even if normal-state correlation is moderate, tail dependence may be high:

$$\lambda_L = \lim_{u \to 0} P(X < F_X^{-1}(u) | Y < F_Y^{-1}(u))$$

For crypto: $\lambda_L \approx 0.5-0.7$ (high left-tail dependence: assets crash together)

Use copulas (Clayton for lower tail, Gumbel for upper tail) to model dependence structure beyond linear correlation.

### 1.7 Portfolio Beta and Hedging

#### 1.7.1 Crypto Beta

$$\beta_i = \frac{Cov(r_i, r_{BTC})}{Var(r_{BTC})}$$

Where $r_{BTC}$ is used as the market return proxy.

**Typical Betas:**
| Asset | Beta to BTC | Note |
|---|---|---|
| ETH | 1.0-1.3 | Slightly higher beta, more volatile |
| SOL | 1.2-1.8 | High beta altcoin |
| LINK | 0.8-1.2 | Moderate beta |
| Stablecoins | 0 | Zero beta (by design) |
| DeFi tokens | 1.0-2.5 | High beta, idiosyncratic risk |
| Meme coins | 1.5-3.0+ | Extreme beta |

**Portfolio Beta:**

$$\beta_P = \sum_i w_i \beta_i$$

#### 1.7.2 Beta Hedging

To achieve target portfolio beta $\beta_{target}$:

$$\text{Hedge Notional} = (\beta_P - \beta_{target}) \times \text{Portfolio Value}$$

If $\beta_{target} = 0$ (market neutral):
- Short BTC/ETH futures with notional = $\beta_P \times$ Portfolio Value
- Rebalance as beta changes (daily or when drift exceeds threshold)

### 1.8 Stress Testing

#### 1.8.1 Methodology

**Historical Scenario Replay:**
Apply actual historical crisis returns to the current portfolio:

| Scenario | BTC | ETH | Altcoins | Description |
|---|---|---|---|---|
| March 2020 COVID | -50% | -60% | -70% | Flash crash, rapid recovery |
| May 2021 China Ban | -53% | -60% | -75% | Multi-week decline |
| Nov 2022 FTX | -25% | -30% | -50% | Exchange collapse |
| Luna/UST May 2022 | -35% | -45% | -60% to -100% | Algorithmic stablecoin death spiral |
| 2018 Bear Market (full) | -84% | -94% | -95%+ | Extended bear over 12 months |

**Hypothetical Scenarios:**
- Flash crash: -30% in 1 hour (liquidation cascade)
- Black swan: -50% in 1 day (unprecedented for BTC but plan for it)
- Regulatory ban: -40% sustained, no recovery for months
- Stablecoin depeg: USDT depegs to $0.90 → all pairs affected
- Exchange hack: 100% loss of funds on affected exchange

**Reverse Stress Test:**
"What scenario would cause the portfolio to lose X%?"
- Work backward from unacceptable loss level
- Determine what market conditions produce that loss
- Assess probability of those conditions
- Ensure position sizing prevents those conditions from being fatal

### 1.9 Risk Budgeting

#### 1.9.1 Risk Parity Approach

Allocate portfolio such that each asset/strategy contributes equally to total portfolio risk.

**Marginal Risk Contribution:**

$$MRC_i = \frac{\partial \sigma_P}{\partial w_i} = \frac{(\Sigma \mathbf{w})_i}{\sigma_P}$$

**Component Risk Contribution:**

$$CRC_i = w_i \times MRC_i = \frac{w_i (\Sigma \mathbf{w})_i}{\sigma_P}$$

**Risk Parity Condition:**

$$CRC_i = CRC_j \quad \forall i, j$$

$$w_i (\Sigma \mathbf{w})_i = w_j (\Sigma \mathbf{w})_j$$

#### 1.9.2 Strategy-Level Risk Budget

```
RISK_BUDGET_ALLOCATION:

  total_risk_budget: 100%  # of allowed portfolio risk

  strategy_allocations:
    basis_trading:
      risk_pct: 25%
      max_var_contribution: 25% of total VaR
      expected_sharpe: 2.0-3.0
      
    options_selling (VRP):
      risk_pct: 20%
      max_var_contribution: 20% of total VaR
      expected_sharpe: 1.0-2.0
      tail_risk: HIGH (manage carefully)
      
    funding_rate_arbitrage:
      risk_pct: 20%
      max_var_contribution: 15% of total VaR
      expected_sharpe: 2.0-4.0
      
    directional_momentum:
      risk_pct: 15%
      max_var_contribution: 25% of total VaR
      expected_sharpe: 0.8-1.5
      
    gamma_scalping:
      risk_pct: 10%
      max_var_contribution: 10% of total VaR
      expected_sharpe: 1.0-2.0
      
    structured_products:
      risk_pct: 10%
      max_var_contribution: 10% of total VaR
      expected_sharpe: 1.5-2.5
      
    reserve (unallocated):
      risk_pct: 0%
      purpose: Buffer for opportunities, rebalancing

  rebalancing:
    frequency: weekly (or when drift > 5% from target)
    method: Reduce overweight strategies, add to underweight
    constraint: Never force-close profitable positions just for rebalancing
```

---

## 2. Technical Specifications

### 2.1 Risk Engine Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    RISK MANAGEMENT ENGINE                        │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  DATA LAYER                                               │   │
│  │  - Real-time positions (all exchanges, all instruments)   │   │
│  │  - Market data (prices, vol surfaces, funding rates)      │   │
│  │  - Historical returns (all assets, all timeframes)        │   │
│  │  - Correlation matrices (rolling, regime-specific)        │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │                                        │
│  ┌──────────────────────▼───────────────────────────────────┐   │
│  │  RISK CALCULATION LAYER                                   │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │ VaR/CVaR │ │ Greeks   │ │ Margin   │ │ Stress   │   │   │
│  │  │ Engine   │ │ Engine   │ │ Monitor  │ │ Tester   │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │ Position │ │ Corr     │ │ Drawdown │ │ Liquidity│   │   │
│  │  │ Sizing   │ │ Monitor  │ │ Tracker  │ │ Risk     │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │                                        │
│  ┌──────────────────────▼───────────────────────────────────┐   │
│  │  DECISION LAYER                                           │   │
│  │  - Pre-trade risk check (approve/reject new orders)       │   │
│  │  - Continuous position monitoring (every 100ms)           │   │
│  │  - Breach detection and alerting                          │   │
│  │  - Automatic risk reduction (rule-based)                  │   │
│  │  - Manual override capability                             │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │                                        │
│  ┌──────────────────────▼───────────────────────────────────┐   │
│  │  ACTION LAYER                                             │   │
│  │  - Risk alerts (tiered: info, warning, critical, halt)    │   │
│  │  - Automatic position reduction orders                    │   │
│  │  - Margin transfer requests                               │   │
│  │  - Strategy pause/resume signals                          │   │
│  │  - System halt trigger                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

### 2.2 Real-Time Risk Monitoring Dashboard

```
RISK_DASHBOARD_METRICS:

  portfolio_level:
    update_frequency: 100ms
    metrics:
      - total_portfolio_value (mark-to-market)
      - total_unrealized_pnl
      - total_realized_pnl_today
      - portfolio_delta_dollars
      - portfolio_gamma_dollars_per_1pct
      - portfolio_vega_dollars_per_vol_point
      - portfolio_theta_daily
      - margin_utilization_pct (per exchange)
      - liquidation_distance_min (worst position)
      - drawdown_current_pct
      - drawdown_from_daily_high
      - VaR_95_1day (updated every 5 min)
      - CVaR_95_1day (updated every 5 min)
      - effective_leverage
      - cash_available

  per_position:
    update_frequency: 1s
    metrics:
      - position_value
      - unrealized_pnl
      - position_delta
      - position_gamma
      - position_vega
      - position_theta
      - margin_required
      - liquidation_price
      - liquidation_distance_pct
      - time_in_position
      - max_adverse_excursion
      - risk_contribution_pct

  per_strategy:
    update_frequency: 1 min
    metrics:
      - strategy_pnl_today
      - strategy_pnl_wtd
      - strategy_pnl_mtd
      - strategy_sharpe_30d
      - strategy_win_rate
      - strategy_avg_holding_period
      - strategy_risk_budget_usage
      - strategy_max_drawdown_30d
      - strategy_correlation_to_btc

  alerts:
    tiers:
      INFO: routine notifications (new fills, daily summaries)
      WARNING: approaching limits (60% of threshold)
      CRITICAL: limit breach or rapid deterioration
      HALT: system stop required (maximum drawdown, exchange issue)
```

### 2.3 Risk Data Pipeline

```
RISK_DATA_PIPELINE:

  inputs:
    positions:
      source: Exchange APIs (all connected exchanges)
      frequency: Every 1 second (reconciliation)
      data: instrument, quantity, entry_price, current_mark, margin

    market_data:
      source: Aggregated feed
      frequency: 100ms
      data: spot prices, futures prices, funding rates, IV

    historical:
      source: Database
      lookback: 2+ years
      data: daily returns all assets, correlation matrix, vol history

  processing:
    
    step_1_position_aggregation:
      - Merge positions across all exchanges
      - Net against each other (if same instrument on multiple venues)
      - Calculate total exposure per asset
      - Calculate portfolio-level Greeks
    
    step_2_risk_metrics:
      - VaR calculation (all three methods)
      - CVaR calculation
      - Greeks aggregation
      - Margin check per exchange
      - Liquidation distance per position
      - Drawdown tracking
    
    step_3_limit_checking:
      - Compare all metrics against defined limits
      - Flag any breaches or near-breaches (>80% of limit)
      - Generate alerts as needed
    
    step_4_reporting:
      - Real-time dashboard update
      - Periodic reports (hourly, daily)
      - Breach logging for audit
      - Performance attribution

  output:
    real_time: Dashboard metrics, alerts, pre-trade approvals
    periodic: Risk reports, stress test results, attribution
    on_demand: Scenario analysis, position sizing recommendations
```

### 2.4 Performance Requirements

```
RISK_ENGINE_PERFORMANCE:

  latency:
    pre_trade_check: <20ms (must not delay order submission significantly)
    position_valuation: <50ms (full portfolio)
    greeks_calculation: <10ms per position
    var_parametric: <100ms
    var_historical: <500ms (with 2 years of data)
    var_monte_carlo: <5s (100K paths, background)
    stress_test: <10s (all scenarios)
    alert_generation: <100ms from breach detection

  throughput:
    position_updates: 1000/second (handle all exchange position updates)
    market_data_processing: 50,000 events/second
    risk_metric_recalculation: every 100ms for critical metrics
    full_recalculation: every 5 minutes (all methods)

  reliability:
    uptime: 99.999% (risk engine must always be running)
    failover: <2 seconds (hot standby)
    data_integrity: Reconciliation every 5 seconds
    audit_trail: Every calculation logged with inputs and outputs
```

---

## 3. Mathematical Models

### 3.1 Value at Risk — Complete Formulations

**Parametric VaR (Normal):**

$$VaR_\alpha^{1-day} = z_\alpha \times \sigma_P \times V_P$$

Where $V_P$ is the portfolio value.

**Parametric VaR (Student-t distribution, better for crypto):**

$$VaR_\alpha^{t} = t_{\alpha,\nu}^{-1} \times \hat{\sigma} \times \sqrt{\frac{\nu-2}{\nu}} \times V_P$$

Where:
- $t_{\alpha,\nu}^{-1}$ = Quantile of Student-t distribution with $\nu$ degrees of freedom
- Typical $\nu$ for crypto: 3-5 (heavy tails)
- For $\nu = 4$: 95% quantile = 2.132 (vs 1.645 for normal) — significantly higher VaR

**Cornish-Fisher VaR (skewness and kurtosis adjusted):**

$$z_{CF} = z_\alpha + \frac{1}{6}(z_\alpha^2 - 1)S + \frac{1}{24}(z_\alpha^3 - 3z_\alpha)(K-3) - \frac{1}{36}(2z_\alpha^3 - 5z_\alpha)S^2$$

$$VaR_{CF} = \mu - z_{CF} \times \sigma$$

Where $S$ = skewness, $K$ = kurtosis of the return distribution.

**For a typical BTC distribution:**
- $S \approx -0.5$ (negative skew)
- $K \approx 8$ (excess kurtosis ≈ 5, heavy tails)
- $z_{CF,95\%} \approx 2.1$ (vs 1.645 normal) — 28% higher VaR

### 3.2 Portfolio VaR with Multiple Assets

**Variance-Covariance Method:**

$$\sigma_P^2 = \mathbf{w}^T \Sigma \mathbf{w} = \sum_i \sum_j w_i w_j \sigma_i \sigma_j \rho_{ij}$$

$$VaR_P = z_\alpha \times \sigma_P \times V_P$$

**Component VaR:**

$$CVaR_i = w_i \times \beta_i^P \times VaR_P$$

Where $\beta_i^P = \frac{Cov(r_i, r_P)}{Var(r_P)}$ is the beta of asset $i$ to the portfolio.

**Marginal VaR:**

$$MVaR_i = \frac{\partial VaR_P}{\partial w_i} = z_\alpha \times \frac{(\Sigma\mathbf{w})_i}{\sigma_P}$$

**Incremental VaR (adding a new position):**

$$IVaR = VaR_{P+new} - VaR_P$$

### 3.3 Kelly Criterion — Extended Formulations

**Multi-Asset Kelly (Continuous):**

$$\mathbf{f}^* = \Sigma^{-1}(\boldsymbol{\mu} - r_f\mathbf{1})$$

**Growth Rate under Kelly:**

$$g = r_f + \frac{1}{2}(\boldsymbol{\mu} - r_f)^T \Sigma^{-1}(\boldsymbol{\mu} - r_f)$$

This is the maximum achievable growth rate (information ratio squared / 2).

**Kelly with Estimation Error:**

Since $\mu$ and $\Sigma$ are estimated with error, use:

$$f_{robust} = \min\left(\alpha f^*, \frac{D_{max}}{VaR_{strategy}}\right)$$

Where:
- $\alpha \in [0.25, 0.5]$ = fractional Kelly multiplier
- $D_{max}$ = Maximum acceptable drawdown
- $VaR_{strategy}$ = VaR of the strategy at full Kelly

**Probability of Ruin at Full Kelly:**

$$P(\text{ruin}) \approx 0$$ (Kelly never goes to zero in theory)

But in practice with estimation error:

$$P(\text{ruin}) \approx e^{-2g/\sigma^2}$$

With estimation error: $P(\text{ruin})$ can be substantial → Use fractional Kelly.

**Kelly for Options Strategies:**

For a strategy with payoff distribution:
- P(max_profit) = $p_1$, profit = $\pi_1$
- P(max_loss) = $p_2$, loss = $\lambda_2$
- P(intermediate) = various

$$f^* = \arg\max_f E[\ln(1 + f \times R)]$$

Solve numerically for complex payoff distributions.

### 3.4 Drawdown Mathematics

**Expected Maximum Drawdown (Magdon-Ismail, 2004):**

For a drift-diffusion process with drift $\mu$ and volatility $\sigma$ over period $T$:

$$E[MDD] \approx \begin{cases} \sqrt{\frac{\pi T}{2}} \times \frac{\sigma}{|\gamma|} \times Q(\gamma\sqrt{T/2}) & \text{if } \mu \neq 0 \\ \sqrt{\frac{\pi T}{2}} \times \sigma & \text{if } \mu = 0 \end{cases}$$

Where $\gamma = \mu/\sigma$ and $Q(\cdot)$ is related to the Mills ratio.

**Simplified Approximation:**

$$E[MDD] \approx 2\sigma\sqrt{T}/\sqrt{\pi} - \mu T/2 \quad \text{(for positive drift)}$$

**Probability of Drawdown Exceeding Level $d$:**

$$P(MDD > d) \approx 2(1 - N(d\sqrt{T}/\sigma))$$

For BTC with daily σ = 3%, over 1 year:
- P(MDD > 30%) ≈ very high (historically, >50% drawdowns have occurred)
- Position sizing must account for this reality

### 3.5 GARCH Volatility Forecasting

**GARCH(1,1) Model:**

$$r_t = \mu + \epsilon_t, \quad \epsilon_t = \sigma_t z_t, \quad z_t \sim N(0,1)$$

$$\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$

**Constraints:** $\omega > 0$, $\alpha \geq 0$, $\beta \geq 0$, $\alpha + \beta < 1$

**Long-run variance:**

$$\sigma_{LR}^2 = \frac{\omega}{1 - \alpha - \beta}$$

**Multi-step forecast:**

$$\hat{\sigma}_{t+h}^2 = \sigma_{LR}^2 + (\alpha + \beta)^{h-1}(\sigma_{t+1}^2 - \sigma_{LR}^2)$$

Volatility forecasts mean-revert to long-run level; speed depends on $\alpha + \beta$ (persistence).

**Typical Parameters for BTC:**
- $\alpha \approx 0.05-0.10$ (shock impact)
- $\beta \approx 0.85-0.92$ (persistence)
- $\alpha + \beta \approx 0.93-0.98$ (high persistence)
- Long-run daily vol: 2.5-3.5%
- Half-life of vol shocks: $\ln(0.5)/\ln(\alpha+\beta) \approx$ 10-50 days

**EGARCH (Asymmetric GARCH, for leverage effect):**

$$\ln(\sigma_t^2) = \omega + \beta\ln(\sigma_{t-1}^2) + \alpha\left(\frac{|\epsilon_{t-1}|}{\sigma_{t-1}} - \sqrt{2/\pi}\right) + \gamma\frac{\epsilon_{t-1}}{\sigma_{t-1}}$$

The $\gamma$ term captures asymmetry: negative returns increase vol more than positive returns.

### 3.6 Copula Models for Tail Dependence

**Clayton Copula (lower tail dependence):**

$$C(u_1, u_2; \theta) = (u_1^{-\theta} + u_2^{-\theta} - 1)^{-1/\theta}$$

Lower tail dependence: $\lambda_L = 2^{-1/\theta}$

**Gumbel Copula (upper tail dependence):**

$$C(u_1, u_2; \theta) = \exp\left(-((-\ln u_1)^\theta + (-\ln u_2)^\theta)^{1/\theta}\right)$$

Upper tail dependence: $\lambda_U = 2 - 2^{1/\theta}$

**For Crypto:**
- Use Clayton copula for crash modeling (strong lower tail dependence)
- Fit $\theta$ from historical extreme co-movements
- Use in Monte Carlo VaR for more realistic tail scenarios

### 3.7 Sharpe Ratio and Performance Metrics

**Sharpe Ratio:**

$$SR = \frac{E[R_P] - R_f}{\sigma_P} = \frac{\mu_P - r_f}{\sigma_P}$$

**Annualized Sharpe (from daily data):**

$$SR_{annual} = SR_{daily} \times \sqrt{365}$$

**Sortino Ratio (downside deviation only):**

$$Sortino = \frac{R_P - R_f}{\sigma_{downside}}$$

Where $\sigma_{downside} = \sqrt{E[\min(R - R_f, 0)^2]}$

**Information Ratio:**

$$IR = \frac{R_P - R_{benchmark}}{\sigma_{R_P - R_{benchmark}}}$$

**Omega Ratio:**

$$\Omega(\theta) = \frac{\int_\theta^\infty (1 - F(r))dr}{\int_{-\infty}^\theta F(r)dr}$$

Where $\theta$ = threshold return, $F$ = CDF of returns. Omega > 1 indicates favorable distribution above threshold.

---

## 4. Risk Parameters

### 4.1 Master Risk Configuration

```
MASTER_RISK_CONFIG:

  portfolio_level:
    max_total_var_95_1day: 5% of NAV
    max_total_cvar_95_1day: 8% of NAV
    max_daily_loss: 3% of NAV (hard stop)
    max_weekly_loss: 7% of NAV (reduced activity)
    max_monthly_loss: 15% of NAV (strategy review)
    max_drawdown: 25% from peak (system halt)
    max_leverage_effective: 5x
    max_leverage_gross: 10x (sum of all positions / equity)
    min_cash_reserve: 20% of NAV (always liquid)
    max_correlation_concentration: 0.8 (no two >30% positions with corr > 0.8)

  per_strategy_limits:
    max_risk_budget: defined per strategy (see Section 1.9)
    max_var_contribution: defined per strategy
    max_drawdown_per_strategy: 10%
    strategy_stop_trigger: 3 consecutive losing weeks at >2% loss each

  per_position_limits:
    max_single_position_var: 2% of NAV
    max_single_position_loss: 2% of NAV
    max_position_concentration: 20% of NAV (single asset)
    max_options_premium_at_risk: 5% of NAV (total)
    max_short_options_margin: 20% of NAV

  greeks_limits:
    max_portfolio_delta: ±30% of NAV
    max_portfolio_gamma: ±3% of NAV per 1% spot move
    max_portfolio_vega: ±1.5% of NAV per vol point
    max_portfolio_theta: ±0.5% of NAV per day
    max_single_name_delta: ±15% of NAV

  exchange_limits:
    max_single_exchange: 40% of NAV
    max_defi_exposure: 15% of NAV
    min_exchange_diversification: 3 exchanges
    max_pending_withdrawals: 10% of NAV

  leverage_limits:
    perpetual_swaps: max 10x per position, 5x portfolio
    futures: max 10x per position, 5x portfolio
    options_margin: per exchange requirements × 1.5 buffer
    structured_products: max 3x effective leverage
```

### 4.2 Dynamic Risk Adjustment Rules

```
DYNAMIC_RISK_ADJUSTMENT:

  volatility_regime_scaling:
    low_vol (DVOL < 50):
      position_size_multiplier: 1.2
      leverage_allowed: standard limits
      var_limit_adjustment: none
      note: "Calm markets → slightly larger positions OK"

    normal_vol (50 ≤ DVOL < 80):
      position_size_multiplier: 1.0
      leverage_allowed: standard limits
      var_limit_adjustment: none
      note: "Normal operations"

    high_vol (80 ≤ DVOL < 110):
      position_size_multiplier: 0.7
      leverage_allowed: 70% of standard
      var_limit_adjustment: tighten by 20%
      note: "Elevated risk → reduce exposure"

    extreme_vol (DVOL ≥ 110):
      position_size_multiplier: 0.4
      leverage_allowed: 50% of standard
      var_limit_adjustment: tighten by 40%
      note: "Crisis → defensive posture"

  drawdown_regime_scaling:
    dd_0_to_5pct:
      action: normal operations
    dd_5_to_10pct:
      action: reduce sizes 25%, tighten stops
    dd_10_to_15pct:
      action: reduce sizes 50%, no new positions
    dd_15_to_25pct:
      action: close 50% of portfolio
    dd_above_25pct:
      action: HALT

  correlation_regime_scaling:
    IF avg_pairwise_correlation > 0.85:
      action: Treat portfolio as single concentrated position
      position_size: Based on concentrated VaR, not diversified
      note: "Diversification is not working — size for worst case"
```

### 4.3 Pre-Trade Risk Check Specification

```
PRE_TRADE_RISK_CHECK:

  checks_performed (ALL must pass for order approval):

    check_1_position_size:
      rule: new_position_var < max_single_position_var
      calculation: VaR of proposed position
      threshold: 2% of NAV
      action_if_fail: REJECT order

    check_2_portfolio_var:
      rule: portfolio_var_after_trade < max_portfolio_var
      calculation: Incremental VaR of new position
      threshold: 5% of NAV
      action_if_fail: REJECT order

    check_3_greeks:
      rule: all portfolio Greeks within limits after trade
      calculation: Add new position Greeks to portfolio
      thresholds: per Greeks limits above
      action_if_fail: REJECT order

    check_4_margin:
      rule: margin_utilization_after_trade < 60%
      calculation: Estimate new margin requirement
      threshold: 60%
      action_if_fail: REJECT order

    check_5_concentration:
      rule: single_asset_exposure < 20% of NAV
      calculation: Total exposure to the underlying
      threshold: 20%
      action_if_fail: REJECT order

    check_6_drawdown:
      rule: current drawdown allows new positions
      calculation: Check drawdown level vs regime
      threshold: Per drawdown control levels
      action_if_fail: REJECT order

    check_7_strategy_budget:
      rule: strategy risk budget not exceeded
      calculation: Strategy VaR contribution
      threshold: Per strategy allocation
      action_if_fail: REJECT order

    check_8_liquidity:
      rule: position < 1% of available liquidity (OI/volume)
      calculation: Size vs market depth
      threshold: 1% of 24h volume or OI
      action_if_fail: REJECT or REDUCE size

  response_time: <20ms
  logging: Every check logged with pass/fail and values
```

---

## 5. Execution Flow

### 5.1 Risk Management System — Complete Algorithm

```
RISK_MANAGEMENT_SYSTEM_FLOW:

  ╔══════════════════════════════════════════════════════════╗
  ║  CONTINUOUS MONITORING LOOP (runs 24/7)                  ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  EVERY 100ms:                                            ║
  ║  ├── Update all position mark-to-market values           ║
  ║  ├── Recalculate portfolio delta (all positions)         ║
  ║  ├── Check liquidation distances (all leveraged pos)     ║
  ║  ├── Check margin utilization (all exchanges)            ║
  ║  ├── Update unrealized P&L                               ║
  ║  └── IF any critical threshold breached → ALERT          ║
  ║                                                          ║
  ║  EVERY 1 second:                                         ║
  ║  ├── Full position reconciliation (API vs internal)      ║
  ║  ├── Greeks recalculation (gamma, vega, theta)           ║
  ║  ├── Drawdown level check                                ║
  ║  ├── Effective leverage calculation                      ║
  ║  └── Strategy P&L tracking                               ║
  ║                                                          ║
  ║  EVERY 5 minutes:                                        ║
  ║  ├── Parametric VaR recalculation                        ║
  ║  ├── CVaR update                                         ║
  ║  ├── Correlation matrix update (EWMA)                    ║
  ║  ├── Risk budget usage per strategy                      ║
  ║  ├── Dynamic regime assessment (DVOL, correlation)       ║
  ║  └── Position sizing parameter updates                   ║
  ║                                                          ║
  ║  EVERY 1 hour:                                           ║
  ║  ├── Historical VaR recalculation                        ║
  ║  ├── Stress test update (all scenarios)                  ║
  ║  ├── Risk report generation                              ║
  ║  ├── Strategy performance attribution                    ║
  ║  └── Risk budget rebalancing check                       ║
  ║                                                          ║
  ║  EVERY 24 hours:                                         ║
  ║  ├── Full Monte Carlo VaR (100K paths)                   ║
  ║  ├── GARCH volatility forecast update                    ║
  ║  ├── Correlation regime classification                   ║
  ║  ├── Comprehensive risk report                           ║
  ║  ├── Backtest risk model accuracy (VaR exceptions)       ║
  ║  └── Parameter recalibration (if needed)                 ║
  ║                                                          ║
  ╚══════════════════════════════════════════════════════════╝
```

### 5.2 Pre-Trade Risk Check Flow

```
PRE_TRADE_FLOW:

  ╔══════════════════════════════════════════════════════════╗
  ║  INPUT: Proposed trade from strategy engine              ║
  ║  {instrument, direction, quantity, leverage, strategy}   ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  STEP 1: BASIC VALIDATION (<1ms)                         ║
  ║  ├── Valid instrument? (exists on connected exchange)     ║
  ║  ├── Valid quantity? (within exchange min/max)            ║
  ║  ├── Valid leverage? (within exchange limits)             ║
  ║  └── Trading enabled? (not in HALT state)                ║
  ║                                                          ║
  ║  IF FAIL → REJECT immediately with reason                ║
  ║                                                          ║
  ║  STEP 2: POSITION SIZING CHECK (<5ms)                    ║
  ║  ├── Calculate notional value of proposed trade           ║
  ║  ├── Calculate risk (VaR) of proposed trade              ║
  ║  ├── Check: risk < max_single_position_risk?             ║
  ║  ├── Check: notional < max_concentration?                ║
  ║  └── Check: leverage within per-position limit?          ║
  ║                                                          ║
  ║  IF FAIL → REJECT or SUGGEST reduced size                ║
  ║                                                          ║
  ║  STEP 3: PORTFOLIO IMPACT CHECK (<10ms)                  ║
  ║  ├── Calculate new portfolio VaR (after trade)           ║
  ║  ├── Calculate incremental VaR                           ║
  ║  ├── Calculate new portfolio Greeks                      ║
  ║  ├── Check all Greeks limits                             ║
  ║  ├── Check total portfolio VaR limit                     ║
  ║  ├── Check correlation impact                            ║
  ║  └── Check risk budget for strategy                      ║
  ║                                                          ║
  ║  IF FAIL → REJECT with specific limit breached           ║
  ║                                                          ║
  ║  STEP 4: MARGIN AND LIQUIDATION CHECK (<5ms)             ║
  ║  ├── Estimate margin required for trade                  ║
  ║  ├── Calculate new margin utilization                    ║
  ║  ├── Calculate liquidation price for new position        ║
  ║  ├── Verify liquidation distance > minimum               ║
  ║  ├── Verify margin utilization < maximum                 ║
  ║  └── Verify sufficient free margin available             ║
  ║                                                          ║
  ║  IF FAIL → REJECT (insufficient margin)                  ║
  ║                                                          ║
  ║  STEP 5: REGIME AND DRAWDOWN CHECK (<2ms)                ║
  ║  ├── Check current drawdown level                        ║
  ║  ├── Apply drawdown-based position scaling               ║
  ║  ├── Check volatility regime scaling                     ║
  ║  ├── Apply any active restrictions                       ║
  ║  └── Verify strategy is allowed in current regime        ║
  ║                                                          ║
  ║  IF FAIL → REJECT (regime restriction)                   ║
  ║                                                          ║
  ║  STEP 6: FINAL APPROVAL (<1ms)                           ║
  ║  ├── All checks passed                                   ║
  ║  ├── Log approval with all risk metrics                  ║
  ║  ├── Set risk monitoring parameters for new position:    ║
  ║  │   - Stop-loss level                                   ║
  ║  │   - Take-profit level                                 ║
  ║  │   - Liquidation alert level                           ║
  ║  │   - Time-based exit                                   ║
  ║  └── Return: APPROVED {trade_id, risk_params}            ║
  ║                                                          ║
  ║  TOTAL LATENCY: <20ms                                    ║
  ║                                                          ║
  ╚══════════════════════════════════════════════════════════╝
```

### 5.3 Breach Response Procedures

```
BREACH_RESPONSE:

  ╔══════════════════════════════════════════════════════════╗
  ║  TIER 1: WARNING (80% of limit reached)                  ║
  ╠══════════════════════════════════════════════════════════╣
  ║  Trigger: Any risk metric reaches 80% of limit           ║
  ║  Response time: Within 1 minute                          ║
  ║  Actions:                                                ║
  ║  1. Log warning with metric details                      ║
  ║  2. Tighten position sizing for new trades (reduce 20%)  ║
  ║  3. Flag positions contributing most to the metric       ║
  ║  4. No forced closures                                   ║
  ║  5. Monitor for improvement or further deterioration     ║
  ╠══════════════════════════════════════════════════════════╣
  ║  TIER 2: BREACH (100% of limit reached)                  ║
  ╠══════════════════════════════════════════════════════════╣
  ║  Trigger: Risk metric breaches defined limit             ║
  ║  Response time: Within 30 seconds                        ║
  ║  Actions:                                                ║
  ║  1. HALT new position opening for affected strategy      ║
  ║  2. Identify contributing positions                      ║
  ║  3. Calculate minimum reduction needed to restore        ║
  ║  4. Begin reducing: Close weakest/most marginal first    ║
  ║  5. Target: Return to 80% of limit within 5 minutes      ║
  ║  6. Log all actions                                      ║
  ╠══════════════════════════════════════════════════════════╣
  ║  TIER 3: CRITICAL BREACH (150% of limit)                 ║
  ╠══════════════════════════════════════════════════════════╣
  ║  Trigger: Risk metric at 1.5x the limit                  ║
  ║  Response time: IMMEDIATE (< 5 seconds)                  ║
  ║  Actions:                                                ║
  ║  1. HALT ALL new orders across entire system             ║
  ║  2. MARKET ORDER close of highest-risk positions         ║
  ║  3. Reduce portfolio by 30-50% immediately               ║
  ║  4. Alert operations team (human in the loop)            ║
  ║  5. Prepare for possible full system halt                ║
  ║  6. Do NOT resume without manual approval                ║
  ╠══════════════════════════════════════════════════════════╣
  ║  TIER 4: SYSTEM HALT (max drawdown or catastrophic)      ║
  ╠══════════════════════════════════════════════════════════╣
  ║  Trigger: Max drawdown (25%) OR exchange failure          ║
  ║  Response time: IMMEDIATE                                ║
  ║  Actions:                                                ║
  ║  1. FULL SYSTEM HALT — no automated trading              ║
  ║  2. Close ALL positions (except long-term holds)         ║
  ║  3. Move all assets to cold storage / safe venues        ║
  ║  4. Full post-mortem required before restart             ║
  ║  5. Minimum 48-hour cooling period                       ║
  ║  6. System restart requires explicit approval             ║
  ║  7. Resume with 50% reduced limits initially             ║
  ╚══════════════════════════════════════════════════════════╝
```

### 5.4 Position Sizing Algorithm

```
POSITION_SIZING_ALGORITHM:

  INPUT:
    strategy_signal: {direction, confidence, expected_return, stop_distance}
    current_portfolio: {equity, positions, drawdown, var_usage}
    market_conditions: {volatility_regime, dvol, correlation}

  STEP 1: Calculate Raw Kelly Size
    mu = expected_return (annualized)
    sigma = asset_volatility (annualized)
    kelly_raw = (mu - risk_free) / sigma^2
    kelly_fraction = 0.25  # Use quarter-Kelly (conservative)
    kelly_size = kelly_raw × kelly_fraction × equity

  STEP 2: Calculate Fixed Fractional Size
    risk_per_trade = 0.02 × equity  # 2% risk
    stop_distance = from strategy signal
    fixed_size = risk_per_trade / stop_distance

  STEP 3: Calculate Vol-Adjusted Size
    target_vol_contribution = 0.01 × equity  # 1% daily vol per position
    asset_daily_vol = sigma / sqrt(365)
    vol_size = target_vol_contribution / (asset_daily_vol × price)

  STEP 4: Calculate VaR-Constrained Size
    remaining_var_budget = max_portfolio_var - current_portfolio_var
    position_var_per_unit = z_alpha × asset_vol × price
    var_size = remaining_var_budget / position_var_per_unit

  STEP 5: Apply Regime Scaling
    regime_multiplier = get_regime_multiplier(dvol_level, drawdown_level)
    # Low vol: 1.2x, Normal: 1.0x, High: 0.7x, Extreme: 0.4x

  STEP 6: Select Final Size
    raw_size = min(kelly_size, fixed_size, vol_size, var_size)
    scaled_size = raw_size × regime_multiplier
    
    # Apply hard caps
    final_size = min(scaled_size, max_single_position_pct × equity)
    final_size = min(final_size, max_exchange_exposure - current_exchange_usage)
    final_size = min(final_size, max_strategy_budget - current_strategy_usage)

  STEP 7: Final Validation
    IF final_size < minimum_viable_position:
      → REJECT (position too small to be worth the overhead)
    IF final_size results in VaR breach:
      → REDUCE to maximum allowable
    
  OUTPUT: final_size (in units), risk_per_trade (in $), leverage_implied
```

### 5.5 Daily Risk Report Generation

```
DAILY_RISK_REPORT:

  SECTION 1: PORTFOLIO OVERVIEW
    - Total NAV (mark-to-market)
    - Daily P&L ($ and %)
    - Week-to-date P&L
    - Month-to-date P&L
    - Year-to-date P&L
    - Current drawdown from peak
    - Effective leverage

  SECTION 2: RISK METRICS
    - VaR 95% 1-day (parametric, historical, Monte Carlo)
    - CVaR 95% 1-day
    - Largest potential daily loss (historical worst day stress)
    - Portfolio Sharpe (30-day rolling)
    - Portfolio Sortino (30-day rolling)

  SECTION 3: GREEKS SUMMARY
    - Portfolio delta ($ and as % of NAV)
    - Portfolio gamma ($ per 1% move)
    - Portfolio vega ($ per vol point)
    - Portfolio theta (daily decay/income)
    - Largest single-name delta

  SECTION 4: STRATEGY ATTRIBUTION
    - P&L by strategy (basis, funding, options, directional, etc.)
    - Risk budget usage by strategy
    - Win rate by strategy (30-day)
    - Sharpe by strategy (30-day)

  SECTION 5: LIMIT UTILIZATION
    - VaR limit: X% of maximum
    - Drawdown level: X% (color-coded)
    - Leverage: X of Y maximum
    - Margin: X% utilized
    - Each exchange: % of maximum allocation

  SECTION 6: STRESS TEST RESULTS
    - Impact of each defined scenario on current portfolio
    - Worst-case loss across all scenarios
    - Scenarios that breach loss limits (flagged)

  SECTION 7: RISK ACTIONS TAKEN
    - Any positions closed by risk engine
    - Any limits adjusted
    - Any alerts generated (and resolution)
    - Regime changes detected

  SECTION 8: FORWARD OUTLOOK
    - Expected P&L contribution from theta
    - Upcoming events (expiries, announcements)
    - Correlation regime assessment
    - Recommendations (reduce/increase specific risks)
```

---

## 6. References

### Academic Literature

1. **Markowitz, H.** (1952). "Portfolio Selection." *Journal of Finance*, 7(1), 77-91.
2. **Sharpe, W.F.** (1964). "Capital Asset Prices: A Theory of Market Equilibrium under Conditions of Risk." *Journal of Finance*, 19(3), 425-442.
3. **Kelly, J.L.** (1956). "A New Interpretation of Information Rate." *Bell System Technical Journal*, 35(4), 917-926.
4. **Artzner, P., Delbaen, F., Eber, J.M., & Heath, D.** (1999). "Coherent Measures of Risk." *Mathematical Finance*, 9(3), 203-228.
5. **Rockafellar, R.T., & Uryasev, S.** (2000). "Optimization of Conditional Value-at-Risk." *Journal of Risk*, 2(3), 21-42.
6. **Engle, R.** (2002). "Dynamic Conditional Correlation: A Simple Class of Multivariate GARCH Models." *Journal of Business & Economic Statistics*, 20(3), 339-350.
7. **Bollerslev, T.** (1986). "Generalized Autoregressive Conditional Heteroskedasticity." *Journal of Econometrics*, 31(3), 307-327.
8. **Magdon-Ismail, M., & Atiya, A.** (2004). "Maximum Drawdown." *Risk*, 17(10), 99-102.
9. **McNeil, A.J., Frey, R., & Embrechts, P.** (2015). *Quantitative Risk Management: Concepts, Techniques and Tools* (Revised Edition). Princeton University Press.
10. **Maillard, S., Roncalli, T., & Teiletche, J.** (2010). "The Properties of Equally Weighted Risk Contribution Portfolios." *Journal of Portfolio Management*, 36(4), 60-70.

### Textbooks

11. **Hull, J.C.** (2018). *Risk Management and Financial Institutions* (5th Edition). Wiley.
12. **Jorion, P.** (2006). *Value at Risk: The New Benchmark for Managing Financial Risk* (3rd Edition). McGraw-Hill.
13. **Taleb, N.N.** (2010). *The Black Swan: The Impact of the Highly Improbable* (2nd Edition). Random House.
14. **Vince, R.** (2009). *The Leverage Space Trading Model*. Wiley.
15. **Tharp, V.K.** (2008). *Definitive Guide to Position Sizing*. IITM.

### Practitioner References

16. **RiskMetrics Group** (1996). *RiskMetrics Technical Document* (4th Edition). J.P. Morgan.
17. **Basel Committee** (2019). "Minimum Capital Requirements for Market Risk (FRTB)." Bank for International Settlements.
18. **CFA Institute** (2020). "Quantitative Methods and Risk Management." CFA Program Curriculum.

### Crypto-Specific Risk Resources

19. **CoinGlass** — Real-time liquidation data, open interest, funding rates.
20. **Glassnode** — On-chain risk metrics, exchange flows, miner behavior.
21. **The Block Research** — Crypto market structure and risk analysis.
22. **Deribit Insights** — Options-based risk metrics (DVOL, skew analysis).
23. **Chaos Labs** — DeFi risk management and simulation.
24. **Gauntlet** — Protocol risk management and simulation.

### Implementation References

25. **NumPy/SciPy** — Portfolio optimization, matrix operations.
26. **QuantLib** — VaR calculation, Monte Carlo engines.
27. **Riskfolio-Lib** — Python portfolio optimization with risk constraints.
28. **arch** — GARCH models in Python.
29. **copulas** — Python package for copula modeling.

---

> **Note to AI Agents:** This document is the MASTER RISK FRAMEWORK for the entire trading system.
> ALL strategies and instruments must comply with this framework.
>
> Critical operational rules:
> 1. PRE-TRADE RISK CHECK is MANDATORY — no order bypasses it
> 2. POSITION SIZING uses the minimum of Kelly, fixed-fractional, vol-adjusted, and VaR-constrained
> 3. DRAWDOWN CONTROLS are absolute — system halts at 25% drawdown
> 4. DYNAMIC ADJUSTMENT scales limits by volatility and drawdown regime
> 5. CORRELATION RISK must be monitored — diversification fails in crises
> 6. TAIL RISK (CVaR) is more important than VaR for crypto
> 7. STRESS TESTS must pass BEFORE any new strategy goes live
> 8. EMERGENCY PROCEDURES execute within 60 seconds
> 9. HUMAN OVERRIDE is always available for critical decisions
> 10. Every risk decision is LOGGED for audit and improvement
>
> This framework interacts with ALL other documents in this module:
> - `00_overview.md` — Derivative types covered by this risk framework
> - `01_options_strategies.md` — Options positions subject to Greek limits
> - `02_futures_perpetual_swaps.md` — Leveraged positions subject to liquidation monitoring
> - `03_structured_products.md` — Structured products subject to allocation limits
> - `04_volatility_trading.md` — Vol positions subject to vega/gamma limits
