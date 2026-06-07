# Statistical Arbitrage — Complete Reference

## Document Metadata
| Field | Value |
|---|---|
| Strategy Class | Statistical Arbitrage / Pairs Trading |
| Asset Classes | Forex, Crypto (Spot & Futures) |
| Timeframe | Intraday to Multi-week |
| Complexity | Advanced |
| Capital Requirement | High (multiple simultaneous positions) |
| Last Updated | 2026-04-12 |

---

## Table of Contents
1. [Pairs Trading Framework](#1-pairs-trading-framework)
2. [Cointegration Theory](#2-cointegration-theory)
3. [Engle-Granger Two-Step Method](#3-engle-granger-two-step-method)
4. [Johansen Cointegration Test](#4-johansen-cointegration-test)
5. [Spread Modeling and Z-Score](#5-spread-modeling-and-z-score)
6. [Kalman Filter for Dynamic Parameters](#6-kalman-filter-for-dynamic-parameters)
7. [PCA-Based Statistical Arbitrage](#7-pca-based-statistical-arbitrage)
8. [Machine Learning Enhancements](#8-machine-learning-enhancements)
9. [Execution Considerations](#9-execution-considerations)
10. [Transaction Cost Modeling](#10-transaction-cost-modeling)
11. [Core Logic — Entry/Exit](#11-core-logic--entryexit)
12. [Technical Specifications](#12-technical-specifications)
13. [Mathematical Framework](#13-mathematical-framework)
14. [Risk Parameters](#14-risk-parameters)
15. [Execution Flow](#15-execution-flow)
16. [Backtesting Methodology](#16-backtesting-methodology)
17. [References](#17-references)

---

## 1. Pairs Trading Framework

### 1.1 Core Concept

Statistical arbitrage (stat arb) exploits temporary mispricings between related securities. The most common form is **pairs trading**: identifying two assets that historically move together and trading the divergence between them, expecting convergence back to equilibrium.

**Fundamental Principle:**

If assets $A$ and $B$ are cointegrated (share a long-run equilibrium relationship), then:

$$S_t = P_{A,t} - \beta P_{B,t}$$

is a stationary (mean-reverting) process, where $\beta$ is the hedge ratio.

### 1.2 Statistical Arbitrage vs Pure Arbitrage

| Feature | Pure Arbitrage | Statistical Arbitrage |
|---|---|---|
| Risk | Risk-free | Has statistical risk |
| Profit Source | Price discrepancy | Mean reversion of spread |
| Time Horizon | Instantaneous | Hours to weeks |
| Capital Requirement | High (convergence guaranteed) | Medium (convergence expected) |
| Loss Possibility | None (theoretical) | Yes (spread may diverge permanently) |
| Example | Triangular FX arb | EUR/GBP vs EUR/USD * USD/GBP |

### 1.3 Pairs Trading in Forex

**Natural Forex Pairs:**

| Pair 1 | Pair 2 | Relationship |
|---|---|---|
| EUR/USD | GBP/USD | Both USD-denominated European currencies |
| AUD/USD | NZD/USD | Commodity currencies, similar economies |
| EUR/CHF | EUR/GBP | European cross-rate relationship |
| USD/CAD | WTI Crude Oil | Commodity currency vs commodity |
| USD/JPY | US 10Y Yield | Interest rate differential |
| EUR/USD | DXY (inverse) | Dollar index relationship |

**Synthetic Pair Construction:**

The spread between EUR/USD and GBP/USD effectively trades EUR/GBP:

$$\text{Spread} = \text{EUR/USD} - \beta \times \text{GBP/USD} \approx f(\text{EUR/GBP})$$

### 1.4 Pairs Trading in Crypto

**Natural Crypto Pairs:**

| Asset 1 | Asset 2 | Relationship |
|---|---|---|
| BTC | ETH | Market leaders, high correlation |
| ETH | SOL | L1 smart contract platforms |
| BTC | BTC-perp | Spot-futures basis |
| LINK | BAND | Oracle protocols |
| AAVE | COMP | DeFi lending protocols |
| BTC (Exchange A) | BTC (Exchange B) | Cross-exchange spread |

---

## 2. Cointegration Theory

### 2.1 Definition

Two time series $X_t$ and $Y_t$ are cointegrated of order $(d, b)$, written $X_t, Y_t \sim CI(d, b)$, if:
1. Both series are integrated of order $d$ (e.g., $I(1)$ — non-stationary)
2. There exists a linear combination $Z_t = X_t - \beta Y_t$ that is integrated of order $d - b$ (e.g., $I(0)$ — stationary)

### 2.2 Cointegration vs Correlation

| Property | Correlation | Cointegration |
|---|---|---|
| Definition | Linear relationship of returns | Long-run equilibrium of levels |
| Stationarity Required? | Yes (returns) | No (levels can be non-stationary) |
| Time Stability | Can change rapidly | More stable (structural) |
| Spurious? | Common with non-stationary data | Genuine long-run relationship |
| Trading Implication | Hedging (short-term) | Pairs trading (long-term convergence) |
| Test | Pearson/Spearman on returns | Engle-Granger / Johansen on levels |

**Key Insight**: Two assets can have high correlation but NOT be cointegrated (they may drift apart permanently). Conversely, two assets can have moderate correlation but strong cointegration (they always revert to equilibrium).

### 2.3 Economic Rationale for Cointegration

| Market | Rationale |
|---|---|
| Forex | Purchasing Power Parity, Interest Rate Parity, triangular relationships |
| Crypto | Same-sector token fundamentals, shared liquidity pools, common risk factors |
| Cross-Market | Commodity-currency links, interest rate-FX links |

### 2.4 Order of Integration

**Testing procedure:**
1. Test if $X_t$ is $I(1)$: ADF test on $X_t$ (should fail to reject unit root)
2. Test if $Y_t$ is $I(1)$: ADF test on $Y_t$ (should fail to reject unit root)
3. If both are $I(1)$, test if $Z_t = X_t - \beta Y_t$ is $I(0)$: ADF test on $Z_t$ (should reject unit root)

If step 3 passes, $X_t$ and $Y_t$ are cointegrated.

---

## 3. Engle-Granger Two-Step Method

### 3.1 Procedure

**Step 1: Estimate the Cointegrating Regression**

Run OLS regression of one price on the other:

$$Y_t = \alpha + \beta X_t + \epsilon_t$$

Obtain residuals:

$$\hat{\epsilon}_t = Y_t - \hat{\alpha} - \hat{\beta} X_t$$

**Step 2: Test Residuals for Stationarity**

Apply the ADF test to $\hat{\epsilon}_t$:

$$\Delta\hat{\epsilon}_t = \gamma \hat{\epsilon}_{t-1} + \sum_{i=1}^{p} \delta_i \Delta\hat{\epsilon}_{t-i} + u_t$$

Test $H_0: \gamma = 0$ (unit root, not cointegrated) vs $H_1: \gamma < 0$ (stationary, cointegrated).

**Critical Values (Engle-Granger, 2 variables):**

| Significance | Critical Value |
|---|---|
| 1% | -3.90 |
| 5% | -3.34 |
| 10% | -3.04 |

Note: These are more negative than standard ADF critical values because $\beta$ is estimated.

### 3.2 Hedge Ratio Estimation

The OLS coefficient $\hat{\beta}$ from Step 1 is the hedge ratio:

$$\text{Spread}_t = Y_t - \hat{\beta} X_t$$

For every 1 unit of $Y$ held long, hold $\hat{\beta}$ units of $X$ short (or vice versa).

### 3.3 Implementation

```python
def engle_granger_test(series_y, series_x, significance=0.05):
    """
    Engle-Granger two-step cointegration test.
    
    Returns: (is_cointegrated, hedge_ratio, residuals, adf_stat, p_value)
    """
    # Step 1: OLS regression Y = alpha + beta * X
    X = np.column_stack([np.ones(len(series_x)), series_x])
    beta_hat = np.linalg.lstsq(X, series_y, rcond=None)[0]
    alpha = beta_hat[0]
    hedge_ratio = beta_hat[1]
    
    # Compute residuals (spread)
    residuals = series_y - alpha - hedge_ratio * series_x
    
    # Step 2: ADF test on residuals
    adf_stat, p_value, _, _, critical_values, _ = adfuller(residuals, maxlag=10)
    
    is_cointegrated = p_value < significance
    
    return {
        'is_cointegrated': is_cointegrated,
        'hedge_ratio': hedge_ratio,
        'intercept': alpha,
        'residuals': residuals,
        'adf_stat': adf_stat,
        'p_value': p_value,
        'critical_values': critical_values
    }
```

### 3.4 Limitations of Engle-Granger

| Limitation | Description | Mitigation |
|---|---|---|
| Variable ordering | Results depend on which is Y vs X | Run both ways; use TLS |
| Single equation | Only finds one cointegrating vector | Use Johansen for > 2 variables |
| Static hedge ratio | $\beta$ is assumed constant over the estimation window | Use rolling windows or Kalman filter |
| Small sample bias | OLS estimates can be biased in small samples | Minimum 250+ observations |
| Structural breaks | Cointegration may break down | Monitor with rolling tests |

---

## 4. Johansen Cointegration Test

### 4.1 Framework

The Johansen test is superior for systems of more than two variables. It models a VAR system in error correction form:

$$\Delta \mathbf{X}_t = \Pi \mathbf{X}_{t-1} + \sum_{i=1}^{p-1} \Gamma_i \Delta \mathbf{X}_{t-i} + \mathbf{u}_t$$

Where $\Pi = \alpha\beta'$ and:
- $\alpha$ = speed of adjustment matrix
- $\beta$ = cointegrating vectors matrix
- rank($\Pi$) = number of cointegrating relationships

### 4.2 Trace Test and Maximum Eigenvalue Test

**Trace Test:**

$$\lambda_{trace}(r) = -T \sum_{i=r+1}^{n} \ln(1 - \hat{\lambda}_i)$$

Tests $H_0$: number of cointegrating vectors $\leq r$ vs $H_1$: $> r$.

**Maximum Eigenvalue Test:**

$$\lambda_{max}(r, r+1) = -T \ln(1 - \hat{\lambda}_{r+1})$$

Tests $H_0$: exactly $r$ cointegrating vectors vs $H_1$: $r+1$ vectors.

### 4.3 Interpreting Results

For $n$ variables:
- rank($\Pi$) = 0: No cointegration
- 0 < rank($\Pi$) < $n$: Cointegration exists (rank = number of cointegrating vectors)
- rank($\Pi$) = $n$: All variables are stationary (trivial case)

### 4.4 Multi-Asset Application

**Crypto Basket Example (BTC, ETH, SOL):**

```python
def johansen_test_crypto(btc, eth, sol, max_lag=5):
    """
    Test for cointegration among BTC, ETH, SOL.
    May reveal spread trading opportunities in L1 tokens.
    """
    data = np.column_stack([btc, eth, sol])
    
    # Johansen test
    result = coint_johansen(data, det_order=0, k_ar_diff=max_lag)
    
    # Trace statistics and critical values
    trace_stats = result.lr1      # Trace statistics
    trace_crit = result.cvt       # Critical values (90%, 95%, 99%)
    
    # Maximum eigenvalue statistics
    max_eig_stats = result.lr2
    max_eig_crit = result.cvm
    
    # Cointegrating vectors (each row is a vector)
    coint_vectors = result.evec
    
    # Number of cointegrating relationships
    n_coint = sum(trace_stats > trace_crit[:, 1])  # 95% level
    
    return {
        'n_cointegrating': n_coint,
        'vectors': coint_vectors[:n_coint],
        'trace_stats': trace_stats,
        'critical_values_95': trace_crit[:, 1]
    }
```

### 4.5 Constructing the Trading Spread

If the Johansen test finds a cointegrating vector $\beta = [\beta_1, \beta_2, \beta_3]$:

$$\text{Spread}_t = \beta_1 P_{BTC,t} + \beta_2 P_{ETH,t} + \beta_3 P_{SOL,t}$$

This spread is stationary and can be traded using z-score mean reversion.

---

## 5. Spread Modeling and Z-Score

### 5.1 Spread Construction

**Two-Asset Spread:**

$$S_t = P_{Y,t} - \beta P_{X,t} - \alpha$$

Where $(\alpha, \beta)$ are estimated from the cointegrating regression.

**Normalized Spread (Z-Score):**

$$z_t = \frac{S_t - \bar{S}_n}{\sigma_{S,n}}$$

Where:
- $\bar{S}_n$ = rolling mean of the spread over $n$ periods
- $\sigma_{S,n}$ = rolling standard deviation of the spread

### 5.2 Z-Score Trading Rules for Pairs

```
LONG SPREAD (Long Y, Short X * beta):
    Entry: z_t < -entry_threshold (e.g., -2.0)
    Exit: z_t >= exit_threshold (e.g., 0.0)
    Stop: z_t < -stop_threshold (e.g., -4.0)

SHORT SPREAD (Short Y, Long X * beta):
    Entry: z_t > +entry_threshold (e.g., +2.0)
    Exit: z_t <= exit_threshold (e.g., 0.0)
    Stop: z_t > +stop_threshold (e.g., +4.0)
```

### 5.3 Spread Half-Life

Estimate the half-life of the spread to determine expected holding period:

$$\Delta S_t = \lambda S_{t-1} + \epsilon_t$$

$$t_{half} = -\frac{\ln(2)}{\lambda}$$

**Practical Guidance:**
- $t_{half}$ < 5 bars: Very fast reversion; potentially high-frequency opportunity
- $t_{half}$ = 5-30 bars: Good for intraday/swing trading
- $t_{half}$ = 30-100 bars: Multi-day to multi-week holding
- $t_{half}$ > 100 bars: Too slow; transaction costs may erode edge

### 5.4 Spread Stationarity Monitoring

```
Algorithm: Rolling Cointegration Monitor

PARAMETERS:
    estimation_window = 252 bars
    test_frequency = 20 bars  # Re-test every 20 bars
    min_adf_pvalue = 0.05
    max_half_life = 60

EVERY test_frequency BARS:
    1. Re-estimate cointegrating regression on last estimation_window bars
    2. Get new beta, alpha, residuals
    3. Run ADF test on residuals
    4. Calculate half-life
    
    IF adf_pvalue > min_adf_pvalue:
        WARNING: "Cointegration may be breaking down"
        ACTION: Close existing spread positions
        STATUS: DISABLED until cointegration re-establishes
        
    IF half_life > max_half_life:
        WARNING: "Mean reversion too slow"
        ACTION: Reduce position sizes
        
    IF beta changed by > 20% from initial estimate:
        WARNING: "Hedge ratio shift detected"
        ACTION: Rebalance positions to new beta
```

---

## 6. Kalman Filter for Dynamic Parameters

### 6.1 Motivation

The static hedge ratio from OLS may not capture time-varying relationships. The Kalman filter estimates $\beta_t$ dynamically, adapting to structural changes.

### 6.2 State-Space Model

**Observation Equation:**

$$Y_t = \alpha_t + \beta_t X_t + \epsilon_t, \quad \epsilon_t \sim \mathcal{N}(0, R)$$

**State Transition Equations:**

$$\alpha_t = \alpha_{t-1} + \eta_{\alpha,t}, \quad \eta_{\alpha,t} \sim \mathcal{N}(0, Q_\alpha)$$
$$\beta_t = \beta_{t-1} + \eta_{\beta,t}, \quad \eta_{\beta,t} \sim \mathcal{N}(0, Q_\beta)$$

The state vector $\theta_t = [\alpha_t, \beta_t]'$ evolves as a random walk.

### 6.3 Kalman Filter Equations

**Prediction Step:**

$$\hat{\theta}_{t|t-1} = \hat{\theta}_{t-1|t-1}$$
$$P_{t|t-1} = P_{t-1|t-1} + Q$$

**Update Step:**

$$K_t = P_{t|t-1} H_t' (H_t P_{t|t-1} H_t' + R)^{-1}$$
$$\hat{\theta}_{t|t} = \hat{\theta}_{t|t-1} + K_t (Y_t - H_t \hat{\theta}_{t|t-1})$$
$$P_{t|t} = (I - K_t H_t) P_{t|t-1}$$

Where:
- $H_t = [1, X_t]$ (observation matrix)
- $K_t$ = Kalman gain
- $P_t$ = state covariance matrix
- $Q$ = state noise covariance (controls adaptation speed)
- $R$ = observation noise variance

### 6.4 Implementation

```python
class KalmanPairTrading:
    """
    Kalman Filter for dynamic hedge ratio estimation in pairs trading.
    """
    
    def __init__(self, delta=1e-4, R=1e-3):
        """
        delta: Controls state transition noise (higher = more adaptive)
        R: Observation noise variance
        """
        self.delta = delta
        self.R = R
        
        # State: [alpha, beta]
        self.theta = np.zeros(2)
        self.P = np.eye(2)  # State covariance
        self.Q = self.delta * np.eye(2)  # State noise
        
    def update(self, x, y):
        """
        Update Kalman filter with new observation.
        
        x: independent variable (price of asset X)
        y: dependent variable (price of asset Y)
        
        Returns: (alpha, beta, spread, spread_variance)
        """
        # Observation vector
        H = np.array([1.0, x])
        
        # Prediction
        theta_pred = self.theta  # Random walk: theta_t = theta_{t-1}
        P_pred = self.P + self.Q
        
        # Innovation
        y_hat = H @ theta_pred
        innovation = y - y_hat
        
        # Innovation variance
        S = H @ P_pred @ H.T + self.R
        
        # Kalman gain
        K = P_pred @ H.T / S
        
        # Update
        self.theta = theta_pred + K * innovation
        self.P = P_pred - np.outer(K, K) * S
        
        # Extract parameters
        alpha = self.theta[0]
        beta = self.theta[1]
        spread = innovation  # = y - alpha - beta * x
        spread_var = S
        
        return alpha, beta, spread, np.sqrt(spread_var)
    
    def get_zscore(self, spread, spread_std, lookback_spreads):
        """Calculate z-score of current spread."""
        if len(lookback_spreads) < 20:
            return 0.0
        mean_spread = np.mean(lookback_spreads)
        std_spread = np.std(lookback_spreads)
        if std_spread == 0:
            return 0.0
        return (spread - mean_spread) / std_spread
```

### 6.5 Kalman Filter Advantages for Stat Arb

| Advantage | Description |
|---|---|
| Dynamic adaptation | Hedge ratio updates continuously |
| No lookback window | Does not require fixed rolling window |
| Uncertainty quantification | Provides confidence bands on $\beta_t$ |
| Regime change detection | Large Kalman gain indicates instability |
| Spread variance | Directly outputs spread prediction variance |

### 6.6 Tuning the Kalman Filter

| Parameter | Effect of Increasing | Typical Range |
|---|---|---|
| $\delta$ (state noise) | More adaptive, noisier $\beta_t$ | $10^{-5}$ to $10^{-3}$ |
| $R$ (observation noise) | Less reactive to innovations | $10^{-4}$ to $10^{-1}$ |

**Guidelines:**
- For stable pairs (EUR/CHF): Use low $\delta$ ($10^{-5}$)
- For volatile pairs (BTC/ETH): Use higher $\delta$ ($10^{-3}$)
- Cross-validate on historical data to select optimal $\delta$

---

## 7. PCA-Based Statistical Arbitrage

### 7.1 Concept

Principal Component Analysis (PCA) identifies common factors driving a basket of assets. Residuals from these factors are stationary and can be traded as mean-reverting spreads.

### 7.2 Methodology

**Step 1: Construct Return Matrix**

$$\mathbf{R} = \begin{bmatrix} r_{1,1} & r_{2,1} & \cdots & r_{n,1} \\ r_{1,2} & r_{2,2} & \cdots & r_{n,2} \\ \vdots & & & \vdots \\ r_{1,T} & r_{2,T} & \cdots & r_{n,T} \end{bmatrix}$$

Where $r_{i,t}$ is the return of asset $i$ at time $t$.

**Step 2: PCA Decomposition**

$$\mathbf{R} = \mathbf{F}\mathbf{L}' + \mathbf{E}$$

Where:
- $\mathbf{F}$ = factor scores (systematic component)
- $\mathbf{L}$ = factor loadings
- $\mathbf{E}$ = residuals (idiosyncratic component)

**Step 3: Trade Residuals**

The residuals $\epsilon_{i,t}$ represent asset-specific deviations from common factors. If these residuals are stationary, they can be mean-reversion traded.

### 7.3 PCA Stat Arb Algorithm

```python
def pca_stat_arb(returns_matrix, n_factors=3, lookback=60):
    """
    PCA-based statistical arbitrage.
    
    1. Extract common factors via PCA
    2. Compute residuals (idiosyncratic returns)
    3. Cumulate residuals to get "residual prices"
    4. Trade mean reversion of residual prices
    """
    # Step 1: Standardize returns
    returns_std = (returns_matrix - returns_matrix.mean()) / returns_matrix.std()
    
    # Step 2: PCA
    pca = PCA(n_components=n_factors)
    factor_scores = pca.fit_transform(returns_std[-lookback:])
    loadings = pca.components_.T
    
    # Step 3: Compute residuals for each asset
    systematic = returns_std[-lookback:] @ loadings @ loadings.T
    residuals = returns_std[-lookback:] - systematic
    
    # Step 4: Cumulative residuals (residual "price")
    cum_residuals = residuals.cumsum(axis=0)
    
    # Step 5: Z-score of cumulative residuals
    z_scores = (cum_residuals[-1] - cum_residuals.mean(axis=0)) / cum_residuals.std(axis=0)
    
    # Step 6: Generate signals
    signals = {}
    for i, z in enumerate(z_scores):
        if z < -2.0:
            signals[i] = 'LONG'  # Residual is oversold; expect reversion up
        elif z > 2.0:
            signals[i] = 'SHORT'  # Residual is overbought; expect reversion down
            
    return signals, z_scores
```

### 7.4 Factor Selection for Crypto

For a universe of top 20 crypto assets:
- **Factor 1** (50-70% variance): Market factor (BTC dominance)
- **Factor 2** (10-20% variance): L1 vs DeFi rotation
- **Factor 3** (5-10% variance): Large cap vs small cap

Trading the residuals after removing these 3 factors captures pure idiosyncratic mean reversion.

### 7.5 Eigenportfolio Trading

Rather than trading individual residuals, trade the **eigenportfolios** themselves when they deviate from equilibrium:

$$\text{Eigenportfolio}_k = \sum_i w_{k,i} P_i$$

Where $w_{k,i}$ are the factor loading weights for the $k$-th principal component.

---

## 8. Machine Learning Enhancements

### 8.1 Regime Detection with ML

**Hidden Markov Model (HMM) for Spread Regime:**

Model the spread process as having multiple hidden states:
- State 1: Stable cointegration (normal mean reversion)
- State 2: Transition (cointegration weakening)
- State 3: Breakdown (no cointegration)

```python
from hmmlearn import hmm

def hmm_regime_detection(spread_series, n_states=3):
    """
    Detect spread regime using Gaussian HMM.
    """
    model = hmm.GaussianHMM(n_components=n_states, covariance_type="full")
    returns = np.diff(spread_series).reshape(-1, 1)
    model.fit(returns)
    
    hidden_states = model.predict(returns)
    state_probs = model.predict_proba(returns)
    
    # Identify the "mean-reverting" state (lowest variance)
    state_variances = [model.covars_[i][0][0] for i in range(n_states)]
    mean_reverting_state = np.argmin(state_variances)
    
    # Trade only when in mean-reverting state
    tradeable = hidden_states[-1] == mean_reverting_state
    confidence = state_probs[-1][mean_reverting_state]
    
    return tradeable, confidence, hidden_states
```

### 8.2 Random Forest for Pair Selection

Use machine learning to predict which pairs will successfully mean-revert:

**Features:**
- Half-life of mean reversion
- ADF test statistic
- Hurst exponent of spread
- Rolling correlation stability
- Spread volatility ratio (recent/historical)
- Volume ratio of the two assets
- Funding rate differential (crypto)
- Sector similarity score

**Target:** Binary classification (trade profitable within $n$ bars or not)

### 8.3 Deep Learning Spread Prediction

**LSTM for Spread Direction:**

```python
def lstm_spread_predictor(spread_history, features, lookback=50):
    """
    LSTM model to predict spread direction/magnitude.
    
    Input: Last 50 bars of spread + features
    Output: Expected spread return over next 5 bars
    """
    model = Sequential([
        LSTM(64, input_shape=(lookback, n_features), return_sequences=True),
        Dropout(0.2),
        LSTM(32, return_sequences=False),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1, activation='linear')  # Predicted spread return
    ])
    
    model.compile(optimizer='adam', loss='mse')
    return model
```

### 8.4 Reinforcement Learning for Optimal Execution

Use RL to learn optimal entry/exit thresholds and position sizing:

- **State**: (z-score, half-life, regime probability, current position, P&L)
- **Action**: (entry_z, exit_z, position_size) or discrete (buy/sell/hold)
- **Reward**: Risk-adjusted P&L (Sharpe-like)

---

## 9. Execution Considerations

### 9.1 Simultaneous Entry/Exit

For pairs trading, both legs must be executed simultaneously to maintain the hedged spread position.

**Execution Methods:**

| Method | Latency | Cost | Complexity |
|---|---|---|---|
| Two market orders | Lowest latency | Highest cost (both taker) | Low |
| One market + one limit | Medium | Medium | Medium |
| Two limit orders | Highest latency (may not fill) | Lowest cost | High |
| Algorithmic (TWAP/VWAP) | High | Low | Very High |

### 9.2 Leg Risk

**Definition:** The risk of one leg filling while the other does not.

**Mitigation Strategies:**

1. **Simultaneous market orders**: Accept the spread cost for guaranteed fills
2. **Leg-in with timeout**: If second leg doesn't fill within $T$ seconds, market order
3. **Spread-aware limit orders**: Place both limits at spread-favorable prices
4. **IOC (Immediate or Cancel)**: Use IOC orders to avoid partial fills

```
Algorithm: Safe Pair Entry

1. Calculate target spread entry level
2. Place limit order for more liquid leg (Leg A)
3. Upon Leg A fill:
    a. Immediately place market order for Leg B
    b. Set timer: max_leg_delay = 5 seconds
4. If Leg B does not fill within max_leg_delay:
    a. Place aggressive limit order (cross the spread)
    b. If still not filled after 10 seconds:
        - Market order for Leg B
5. If Leg B fill price is worse than max_slippage:
    - Consider unwinding both legs
    - Log: "Excessive slippage on Leg B"
```

### 9.3 Position Ratio Maintenance

Over time, the hedge ratio $\beta_t$ may change, requiring rebalancing:

$$\text{Rebalance Trigger} = |\beta_t - \beta_{entry}| > \delta_{rebal}$$

**Rebalancing Rules:**
- Check $\beta$ every $n$ bars (e.g., daily)
- Rebalance if $\beta$ change > threshold (e.g., 10% relative change)
- Adjust Leg B quantity: $\Delta Q_B = (beta_{new} - \beta_{entry}) \times Q_A$

---

## 10. Transaction Cost Modeling

### 10.1 Cost Components

$$\text{Total Cost per Round-Trip} = 2 \times (C_{spread} + C_{commission} + C_{slippage} + C_{funding})$$

| Component | Forex (typical) | Crypto CEX (typical) | Crypto DEX (typical) |
|---|---|---|---|
| Half-spread | 0.5-1.5 pips | 0.02-0.05% | 0.05-0.30% |
| Commission | 0-$3.50 per lot | 0.02-0.10% | Gas fee |
| Slippage | 0.2-1.0 pips | 0.01-0.05% | 0.10-1.00% |
| Funding (overnight) | Swap rate | 0.01-0.10%/8h | N/A |

### 10.2 Cost Impact on Stat Arb Profitability

**Minimum Spread Move for Profitability:**

$$\Delta S_{min} = \frac{\text{Total Round-Trip Cost}}{Q}$$

**Example (BTC/ETH pair on Binance):**
- Fee rate: 0.1% per trade (maker)
- Two legs, round-trip: 4 trades x 0.1% = 0.4% total
- If total position value = $20,000, cost = $80 per round-trip
- Minimum spread move needed: spread must move > $80 in our favor

### 10.3 Break-Even Analysis

$$\text{Minimum Z-Score Entry} = z_{min} = \frac{\text{Total Cost}}{\sigma_S}$$

For the pair to be tradeable:
- Required spread standard deviation must be large relative to costs
- Rule of thumb: $\sigma_S > 5 \times \text{Total Cost per round-trip}$

### 10.4 Optimal Trading Frequency

Trading too frequently erodes profits through costs. The optimal frequency balances:

$$\text{Optimal Frequency} = \arg\max_f \left[f \times E[\text{Profit per trade}] - f \times \text{Cost per trade}\right]$$

Given mean reversion dynamics:
- Higher frequency captures more mean reversions but pays more costs
- Lower frequency has higher profit per trade but fewer opportunities

**Approximate Optimal Holding Period:**

$$T_{opt} \approx t_{half} \times \sqrt{\frac{\text{Cost}}{\sigma_S}}$$

---

## 11. Core Logic — Entry/Exit

### 11.1 Pairs Trading Entry Logic

```
Algorithm: Statistical Arbitrage Entry

PRE-TRADE CHECKS:
    1. Cointegration valid: ADF p-value < 0.05 on spread (tested within last 20 bars)
    2. Half-life reasonable: 5 < t_half < 60 bars
    3. Spread volatility adequate: sigma_S > 5x round-trip cost
    4. Regime appropriate: HMM state = mean-reverting (or no regime model = always on)
    5. No major event risk: Check economic calendar
    
SIGNAL GENERATION:
    z = (spread - mean_spread) / std_spread
    
    IF z < -entry_z AND NOT in_position:
        SIGNAL = LONG_SPREAD
        Action: Long Y, Short X * beta
        Entry_z = z
        
    IF z > +entry_z AND NOT in_position:
        SIGNAL = SHORT_SPREAD
        Action: Short Y, Long X * beta
        Entry_z = z

POSITION SIZING:
    dollar_risk = account * risk_pct
    spread_risk = stop_z * std_spread * Q  # Where Q is notional per unit z
    position_notional = dollar_risk / ((stop_z - entry_z) * std_spread)
    
    # Split between legs
    Q_Y = position_notional / P_Y
    Q_X = Q_Y * beta
```

### 11.2 Exit Logic

```
Algorithm: Statistical Arbitrage Exit

EACH BAR:
    z = (spread - mean_spread) / std_spread
    
    # 1. Mean reversion target
    IF position == LONG_SPREAD AND z >= exit_z:
        EXIT ALL
        Reason: "Spread reverted to mean"
        
    IF position == SHORT_SPREAD AND z <= -exit_z:
        EXIT ALL
        Reason: "Spread reverted to mean"
    
    # 2. Stop loss (spread divergence)
    IF position == LONG_SPREAD AND z < -stop_z:
        EXIT ALL
        Reason: "Spread diverged further — stop loss"
        
    IF position == SHORT_SPREAD AND z > +stop_z:
        EXIT ALL
        Reason: "Spread diverged further — stop loss"
    
    # 3. Time stop
    IF bars_in_trade > max_holding_bars:
        EXIT ALL
        Reason: "Time stop — spread failed to revert"
    
    # 4. Cointegration breakdown
    IF adf_pvalue > 0.10:  # Rolling ADF on recent data
        EXIT ALL
        Reason: "Cointegration breakdown detected"
    
    # 5. Hedge ratio drift
    IF |beta_current - beta_entry| / beta_entry > 0.20:
        REBALANCE or EXIT
        Reason: "Hedge ratio shifted significantly"
```

### 11.3 Spread Position Management

```
POSITION TRACKING:

For LONG SPREAD position:
    Leg A (Long Y):
        entry_price_Y = fill_price
        quantity_Y = Q_Y
        current_PnL_Y = (current_price_Y - entry_price_Y) * Q_Y
        
    Leg B (Short X):
        entry_price_X = fill_price
        quantity_X = Q_X = Q_Y * beta
        current_PnL_X = (entry_price_X - current_price_X) * Q_X
        
    Total Spread PnL:
        PnL = current_PnL_Y + current_PnL_X - costs
        
    Spread Value:
        entry_spread = entry_price_Y - beta * entry_price_X
        current_spread = current_price_Y - beta * current_price_X
        spread_PnL_theoretical = (current_spread - entry_spread) * dollar_per_spread_unit
```

---

## 12. Technical Specifications

### 12.1 System Configuration

```yaml
stat_arb_config:
  # Cointegration Testing
  cointegration:
    method: engle_granger  # or johansen
    estimation_window: 252
    retest_frequency: 20
    min_adf_pvalue: 0.05
    max_half_life: 60
    min_half_life: 5
    
  # Hedge Ratio
  hedge_ratio:
    method: kalman  # or ols_rolling, tls
    kalman_delta: 1e-4
    kalman_R: 1e-3
    ols_window: 60
    rebalance_threshold: 0.10  # 10% change triggers rebalance
    
  # Z-Score Parameters
  z_score:
    lookback: 20  # For rolling mean/std of spread
    entry_threshold: 2.0
    exit_threshold: 0.0  # Exit at mean
    stop_threshold: 4.0
    scale_entry: true  # Scale position by z-score magnitude
    
  # Position Sizing
  sizing:
    risk_per_trade: 0.015  # 1.5% of account
    max_notional_per_pair: 0.10  # 10% of account per pair
    max_pairs_concurrent: 5
    max_portfolio_risk: 0.06  # 6% total
    
  # Risk Management
  risk:
    max_drawdown: 0.10
    time_stop_bars: 60  # 3x typical half-life
    cointegration_check_freq: 10
    max_correlation_between_pairs: 0.50
    
  # Execution
  execution:
    entry_method: simultaneous_market  # or leg_in_limit
    max_slippage_bps: 10
    leg_timeout_seconds: 5
    rebalance_check_frequency: daily
```

### 12.2 Pair Universe Screening

```yaml
pair_screening:
  universe:
    forex: [EUR/USD, GBP/USD, AUD/USD, NZD/USD, USD/CAD, USD/CHF, USD/JPY]
    crypto: [BTC, ETH, SOL, BNB, ADA, AVAX, DOT, LINK, UNI, AAVE]
    
  filters:
    min_daily_volume: $10M (crypto) / $100M (forex)
    max_spread_pct: 0.10%
    min_correlation: 0.50  # Pre-filter before cointegration test
    min_data_history: 252 bars
    
  screening_process:
    1. Form all possible pairs from universe
    2. Filter by minimum correlation (removes obviously unrelated)
    3. Test each remaining pair for cointegration (EG or Johansen)
    4. For cointegrated pairs, calculate half-life
    5. Filter by half-life (5 < t_half < 60)
    6. Rank by: (ADF stat significance * inverse half-life * spread volatility)
    7. Select top N pairs (e.g., top 5-10)
    8. Re-screen monthly
```

---

## 13. Mathematical Framework

### 13.1 Spread as Ornstein-Uhlenbeck Process

If the spread $S_t$ follows an OU process:

$$dS_t = \theta(\mu_S - S_t)dt + \sigma_S dW_t$$

Then the expected spread at time $t$ given current spread $S_0$:

$$E[S_t | S_0] = \mu_S + (S_0 - \mu_S)e^{-\theta t}$$

And the variance:

$$\text{Var}(S_t | S_0) = \frac{\sigma_S^2}{2\theta}(1 - e^{-2\theta t})$$

### 13.2 Optimal Entry and Exit Thresholds

From the OU framework, the optimal entry/exit thresholds can be derived by solving the optimal stopping problem.

**Bertram (2010) Analytical Solution:**

For a symmetric trading rule with entry at $\pm a$ and exit at $\pm b$ (where $a > b \geq 0$):

The expected profit per trade:

$$E[\text{Profit}] = a - b - c$$

Where $c$ is the round-trip transaction cost.

The expected trade duration:

$$E[\tau] = \frac{1}{\theta}\left[\Phi^{-1}(a) - \Phi^{-1}(b)\right]$$

Where $\Phi^{-1}$ is related to the expected first-passage time of the OU process.

**Simplified Optimization (maximize Sharpe):**

$$\max_{a, b} \frac{E[\text{Profit per unit time}]}{\text{Std of Profit per unit time}}$$

Typical optimal: $a^* \approx 1.5\sigma_S$ to $2.5\sigma_S$, $b^* \approx 0$ to $0.5\sigma_S$.

### 13.3 Error Correction Model (ECM)

The Engle-Granger ECM for the spread:

$$\Delta Y_t = \alpha_1(Y_{t-1} - \beta X_{t-1} - \mu) + \sum_{i=1}^{p}\gamma_i \Delta Y_{t-i} + \sum_{j=1}^{q}\delta_j \Delta X_{t-j} + u_t$$

Where:
- $\alpha_1$ = speed of adjustment (should be negative for mean reversion)
- $(Y_{t-1} - \beta X_{t-1} - \mu)$ = error correction term (= spread)
- Short-run dynamics captured by $\gamma_i$ and $\delta_j$

**Interpretation:**
- $|\alpha_1|$ close to 1: Very fast adjustment (strong mean reversion)
- $|\alpha_1|$ close to 0: Slow adjustment (weak mean reversion)
- $\alpha_1 > 0$: No error correction (spread may be non-stationary)

### 13.4 Total Least Squares (TLS) Hedge Ratio

OLS minimizes vertical distances (Y residuals), which can bias $\beta$ when both X and Y have noise. TLS (orthogonal regression) minimizes perpendicular distances:

$$\hat{\beta}_{TLS} = \frac{\sigma_Y^2 - \sigma_X^2 + \sqrt{(\sigma_Y^2 - \sigma_X^2)^2 + 4\sigma_{XY}^2}}{2\sigma_{XY}}$$

Or equivalently via SVD of the centered data matrix.

### 13.5 Kelly Criterion for Pairs Trading

$$f^* = \frac{\mu_S}{z_{entry} \times \sigma_S^2}$$

Where:
- $\mu_S$ = expected profit per trade (spread movement)
- $\sigma_S^2$ = variance of spread returns
- $z_{entry}$ = z-score at entry

**Half-Kelly (recommended):** $f = f^*/2$

### 13.6 Portfolio of Pairs: Correlation Adjustment

For $n$ pairs with spread return correlation matrix $\Sigma$:

$$w^* = \frac{1}{\gamma}\Sigma^{-1}\alpha$$

Where:
- $\alpha$ = vector of expected spread returns
- $\gamma$ = risk aversion parameter
- $w^*$ = optimal weight vector

This ensures diversification benefit across pairs while accounting for correlations between spreads.

---

## 14. Risk Parameters

### 14.1 Position Sizing

**Per-Pair Sizing:**

$$\text{Notional per pair} = \frac{\text{Account} \times \text{Risk per pair}}{(\text{entry\_z} - \text{stop\_z}) \times \sigma_S \times \text{leverage factor}}$$

| Risk Level | Risk per Pair | Max Pairs | Total Pair Risk |
|---|---|---|---|
| Conservative | 1.0% | 3 | 3% |
| Moderate | 1.5% | 5 | 7.5% |
| Aggressive | 2.0% | 7 | 14% |

### 14.2 Stop Loss Framework

| Stop Type | Condition | Action |
|---|---|---|
| Z-Score Stop | $|z| > z_{stop}$ (typically 3.5-4.5) | Close both legs |
| Dollar Stop | Loss > X% of account | Close both legs |
| Time Stop | Holding period > 3x half-life | Close both legs |
| Cointegration Stop | ADF p-value > 0.10 | Close both legs |
| Hedge Ratio Stop | $\beta$ changed > 20% | Rebalance or close |
| Drawdown Stop | Total spread book DD > 10% | Reduce all pair positions by 50% |

### 14.3 Risk Metrics for Pairs Portfolio

| Metric | Target | Alert |
|---|---|---|
| Net market exposure | < 10% of gross | > 15% |
| Gross exposure | < 3x account | > 4x account |
| Average spread half-life | 10-30 bars | > 50 bars |
| Win rate (completed trades) | > 55% | < 45% |
| Average holding period | 1-3x half-life | > 5x half-life |
| Spread correlation (between pairs) | < 0.50 | > 0.70 |
| Portfolio Sharpe (spread book) | > 1.5 | < 0.8 |

### 14.4 Stress Testing

```
STRESS SCENARIOS:
    1. Correlation breakdown:
       - What if pair correlation drops from 0.8 to 0.3?
       - Expected max loss: full spread notional * max z-score * sigma_S
       
    2. One-leg liquidity crisis:
       - What if one leg becomes illiquid?
       - Maximum slippage: model 10x normal spread
       
    3. Structural break:
       - What if cointegration permanently breaks?
       - Maximum loss: stop_z * sigma_S * position_size
       
    4. Simultaneous pairs failure:
       - What if 3 pairs hit stop loss simultaneously?
       - Maximum portfolio loss: 3 * risk_per_pair = 4.5% (at 1.5% each)
       
    5. Flash crash:
       - Both legs gap adversely
       - Model: 5-sigma event on both legs with 50% correlation
```

---

## 15. Execution Flow

### 15.1 Complete Statistical Arbitrage System — Pseudocode

```python
class StatArbSystem:
    """
    Complete Statistical Arbitrage Trading System
    Supports: Engle-Granger, Johansen, Kalman Filter
    Markets: Forex, Crypto
    """
    
    def __init__(self, config):
        self.config = config
        self.pairs = {}           # (asset_a, asset_b) -> pair_info
        self.positions = {}       # pair_id -> position info
        self.kalman_filters = {}  # pair_id -> KalmanPairTrading instance
        
    def screen_pairs(self, universe_data):
        """Step 1: Identify cointegrated pairs."""
        pairs = []
        symbols = list(universe_data.keys())
        
        # Test all combinations
        for i in range(len(symbols)):
            for j in range(i+1, len(symbols)):
                sym_a, sym_b = symbols[i], symbols[j]
                price_a = universe_data[sym_a]
                price_b = universe_data[sym_b]
                
                # Pre-filter: correlation
                corr = np.corrcoef(np.diff(np.log(price_a)), np.diff(np.log(price_b)))[0, 1]
                if abs(corr) < self.config['min_correlation']:
                    continue
                
                # Cointegration test
                result = engle_granger_test(price_a, price_b)
                
                if result['is_cointegrated']:
                    half_life = calculate_half_life(result['residuals'])
                    
                    if self.config['min_half_life'] < half_life < self.config['max_half_life']:
                        pairs.append({
                            'sym_a': sym_a,
                            'sym_b': sym_b,
                            'hedge_ratio': result['hedge_ratio'],
                            'intercept': result['intercept'],
                            'half_life': half_life,
                            'adf_stat': result['adf_stat'],
                            'adf_pvalue': result['p_value'],
                            'correlation': corr
                        })
        
        # Rank and select top pairs
        pairs.sort(key=lambda p: p['adf_stat'])  # More negative = stronger
        selected = pairs[:self.config['max_pairs_concurrent']]
        
        # Initialize Kalman filters for selected pairs
        for pair in selected:
            pair_id = f"{pair['sym_a']}_{pair['sym_b']}"
            self.pairs[pair_id] = pair
            self.kalman_filters[pair_id] = KalmanPairTrading(
                delta=self.config['kalman_delta'],
                R=self.config['kalman_R']
            )
        
        return selected
    
    def update_spreads(self, current_prices):
        """Step 2: Update spread calculations for all pairs."""
        signals = {}
        
        for pair_id, pair in self.pairs.items():
            price_a = current_prices[pair['sym_a']]
            price_b = current_prices[pair['sym_b']]
            
            # Update Kalman filter
            kf = self.kalman_filters[pair_id]
            alpha, beta, spread, spread_std = kf.update(price_b, price_a)
            
            # Store current spread history
            if 'spread_history' not in pair:
                pair['spread_history'] = []
            pair['spread_history'].append(spread)
            
            # Calculate z-score
            if len(pair['spread_history']) >= self.config['z_lookback']:
                recent_spreads = pair['spread_history'][-self.config['z_lookback']:]
                z_score = (spread - np.mean(recent_spreads)) / np.std(recent_spreads)
            else:
                z_score = 0.0
            
            # Update pair info
            pair['current_spread'] = spread
            pair['current_z'] = z_score
            pair['current_beta'] = beta
            pair['current_alpha'] = alpha
            pair['spread_std'] = spread_std
            
            signals[pair_id] = z_score
        
        return signals
    
    def generate_signals(self, z_scores):
        """Step 3: Generate entry/exit signals."""
        actions = []
        
        for pair_id, z in z_scores.items():
            pair = self.pairs[pair_id]
            
            # Check if already in position
            if pair_id in self.positions:
                action = self.check_exit(pair_id, z)
                if action:
                    actions.append(action)
            else:
                # Check entry
                if abs(z) > self.config['entry_z']:
                    # Verify cointegration still holds
                    if pair.get('adf_pvalue', 1.0) < 0.05:
                        direction = 'LONG_SPREAD' if z < -self.config['entry_z'] else 'SHORT_SPREAD'
                        actions.append({
                            'pair_id': pair_id,
                            'action': 'ENTER',
                            'direction': direction,
                            'z_score': z,
                            'beta': pair['current_beta']
                        })
        
        return actions
    
    def check_exit(self, pair_id, z):
        """Check exit conditions for an open position."""
        pos = self.positions[pair_id]
        pair = self.pairs[pair_id]
        
        # Mean reversion target
        if pos['direction'] == 'LONG_SPREAD' and z >= self.config['exit_z']:
            return {'pair_id': pair_id, 'action': 'EXIT', 'reason': 'Target reached'}
        if pos['direction'] == 'SHORT_SPREAD' and z <= -self.config['exit_z']:
            return {'pair_id': pair_id, 'action': 'EXIT', 'reason': 'Target reached'}
        
        # Stop loss
        if pos['direction'] == 'LONG_SPREAD' and z < -self.config['stop_z']:
            return {'pair_id': pair_id, 'action': 'EXIT', 'reason': 'Stop loss'}
        if pos['direction'] == 'SHORT_SPREAD' and z > self.config['stop_z']:
            return {'pair_id': pair_id, 'action': 'EXIT', 'reason': 'Stop loss'}
        
        # Time stop
        if pos['bars_held'] > self.config['time_stop_bars']:
            return {'pair_id': pair_id, 'action': 'EXIT', 'reason': 'Time stop'}
        
        # Cointegration breakdown
        if pair.get('adf_pvalue', 0) > 0.10:
            return {'pair_id': pair_id, 'action': 'EXIT', 'reason': 'Cointegration breakdown'}
        
        return None
    
    def execute_trade(self, action, current_prices):
        """Step 4: Execute pair trade."""
        pair_id = action['pair_id']
        pair = self.pairs[pair_id]
        
        if action['action'] == 'ENTER':
            # Calculate position size
            notional = self.calculate_notional(pair_id)
            beta = action['beta']
            
            price_a = current_prices[pair['sym_a']]
            price_b = current_prices[pair['sym_b']]
            
            if action['direction'] == 'LONG_SPREAD':
                # Long A, Short B * beta
                qty_a = notional / price_a
                qty_b = qty_a * beta
                
                self.exchange.buy(pair['sym_a'], qty_a)
                self.exchange.sell(pair['sym_b'], qty_b)
                
            else:  # SHORT_SPREAD
                # Short A, Long B * beta
                qty_a = notional / price_a
                qty_b = qty_a * beta
                
                self.exchange.sell(pair['sym_a'], qty_a)
                self.exchange.buy(pair['sym_b'], qty_b)
            
            self.positions[pair_id] = {
                'direction': action['direction'],
                'entry_z': action['z_score'],
                'entry_beta': beta,
                'qty_a': qty_a,
                'qty_b': qty_b,
                'entry_price_a': price_a,
                'entry_price_b': price_b,
                'bars_held': 0,
                'entry_spread': pair['current_spread']
            }
            
        elif action['action'] == 'EXIT':
            pos = self.positions[pair_id]
            
            # Close both legs
            if pos['direction'] == 'LONG_SPREAD':
                self.exchange.sell(pair['sym_a'], pos['qty_a'])
                self.exchange.buy(pair['sym_b'], pos['qty_b'])
            else:
                self.exchange.buy(pair['sym_a'], pos['qty_a'])
                self.exchange.sell(pair['sym_b'], pos['qty_b'])
            
            # Record P&L
            self.record_trade(pair_id, action['reason'], current_prices)
            del self.positions[pair_id]
    
    def run_monitoring_loop(self, data_feed):
        """Step 5: Main execution loop."""
        # Initial pair screening
        initial_data = data_feed.get_history(self.config['estimation_window'])
        self.screen_pairs(initial_data)
        
        rescreen_counter = 0
        
        for timestamp, prices in data_feed:
            # Update spreads and z-scores
            z_scores = self.update_spreads(prices)
            
            # Generate signals
            actions = self.generate_signals(z_scores)
            
            # Execute trades
            for action in actions:
                self.execute_trade(action, prices)
            
            # Update holding periods
            for pair_id in self.positions:
                self.positions[pair_id]['bars_held'] += 1
            
            # Periodic re-screening
            rescreen_counter += 1
            if rescreen_counter >= self.config['retest_frequency']:
                self.validate_cointegration(data_feed.get_recent(self.config['estimation_window']))
                rescreen_counter = 0
            
            # Log portfolio status
            self.log_status(prices, z_scores)
```

### 15.2 Execution Flow Diagram

```
┌───────────────────────────────────────────────────┐
│        STATISTICAL ARBITRAGE EXECUTION FLOW       │
├───────────────────────────────────────────────────┤
│                                                   │
│  1. PAIR SCREENING (Monthly)                      │
│     ├─ Form all pair combinations                 │
│     ├─ Pre-filter by correlation (> 0.50)         │
│     ├─ Run Engle-Granger cointegration test       │
│     ├─ Calculate half-life for each pair          │
│     ├─ Filter by half-life (5-60 bars)            │
│     ├─ Rank by ADF statistic strength             │
│     └─ Select top N pairs for trading             │
│                                                   │
│  2. SPREAD CALCULATION (Each Bar)                 │
│     ├─ Update Kalman filter for each pair         │
│     ├─ Get dynamic hedge ratio (beta_t)           │
│     ├─ Calculate current spread                   │
│     ├─ Calculate rolling z-score                  │
│     └─ Update spread history                      │
│                                                   │
│  3. SIGNAL GENERATION                             │
│     ├─ Check z-score vs entry threshold           │
│     ├─ Verify cointegration still holds           │
│     ├─ Check available capacity (max pairs)       │
│     └─ Generate LONG_SPREAD or SHORT_SPREAD       │
│                                                   │
│  4. EXECUTION                                     │
│     ├─ Calculate position size (risk-based)       │
│     ├─ Determine leg quantities (A and B*beta)    │
│     ├─ Execute both legs simultaneously           │
│     ├─ Confirm fills and record entry             │
│     └─ Handle leg risk (timeout / market order)   │
│                                                   │
│  5. POSITION MANAGEMENT                           │
│     ├─ Monitor z-score for mean reversion         │
│     ├─ Check stop loss (z-score expansion)        │
│     ├─ Check time stop (3x half-life)             │
│     ├─ Check cointegration validity               │
│     ├─ Rebalance if hedge ratio drifts            │
│     └─ Exit when conditions met                   │
│                                                   │
│  6. COINTEGRATION MONITORING (Periodic)           │
│     ├─ Re-run ADF test on spread                  │
│     ├─ Re-estimate half-life                      │
│     ├─ Check for structural breaks                │
│     ├─ HMM regime classification                  │
│     └─ Disable pair if cointegration breaks       │
│                                                   │
│  7. PORTFOLIO MONITORING                          │
│     ├─ Track net market exposure                  │
│     ├─ Monitor cross-pair correlations            │
│     ├─ Drawdown tracking                          │
│     ├─ Performance attribution (per pair)         │
│     └─ Alert on anomalies                         │
│                                                   │
└───────────────────────────────────────────────────┘
```

---

## 16. Backtesting Methodology

### 16.1 Stat Arb Backtesting Protocol

```
1. DATA PREPARATION:
    - Minimum 3 years of clean price data
    - Ensure proper timestamp alignment between assets
    - Account for missing data (holidays, exchange outages)
    - Use mid-prices (not last traded price) where possible
    
2. EXPANDING WINDOW APPROACH:
    - Start with minimum estimation window (252 bars)
    - At each step:
      a. Estimate cointegration on [0:t]
      b. Generate signal at t+1
      c. Track P&L forward from t+1
    - This prevents look-ahead bias in beta estimation
    
3. TRANSACTION COSTS:
    - Model realistic spreads (vary by time of day, volatility)
    - Include commission on all 4 legs (entry A, entry B, exit A, exit B)
    - Include slippage model (function of order size / daily volume)
    - Include funding costs for short positions
    
4. REBALANCING COSTS:
    - When hedge ratio changes, rebalancing has cost
    - Model the frequency and magnitude of rebalances
    
5. CAPACITY CONSTRAINTS:
    - Model maximum position sizes (% of daily volume)
    - Impact: Large positions may move the spread
```

### 16.2 Key Backtest Metrics

| Metric | Formula | Target (Stat Arb) |
|---|---|---|
| Sharpe Ratio | $(R_{ann} - R_f) / \sigma_{ann}$ | > 2.0 |
| Win Rate | Winning trades / Total | > 55% |
| Average Trade Duration | Mean holding period | ~ half-life |
| Profit Factor | Gross wins / Gross losses | > 2.0 |
| Max Drawdown | Peak-to-trough | < 10% |
| Calmar Ratio | Ann. Return / Max DD | > 2.0 |
| Trades per Month | Average frequency | 5-20 |
| Hit Rate (Pair Selection) | Profitable pairs / Total pairs tested | > 40% |
| Sharpe Decay (OOS) | OOS Sharpe / IS Sharpe | > 0.60 |

---

## 17. References

### Academic Papers

1. **Engle, R.F., & Granger, C.W.J.** (1987). "Co-Integration and Error Correction: Representation, Estimation, and Testing." *Econometrica*, 55(2), 251-276.
2. **Johansen, S.** (1991). "Estimation and Hypothesis Testing of Cointegration Vectors in Gaussian Vector Autoregressive Models." *Econometrica*, 59(6), 1551-1580.
3. **Gatev, E., Goetzmann, W., & Rouwenhorst, K.G.** (2006). "Pairs Trading: Performance of a Relative-Value Arbitrage Rule." *Review of Financial Studies*, 19(3), 797-827.
4. **Vidyamurthy, G.** (2004). *Pairs Trading: Quantitative Methods and Analysis*. Wiley.
5. **Avellaneda, M., & Lee, J.H.** (2010). "Statistical Arbitrage in the US Equities Market." *Quantitative Finance*, 10(7), 761-782.
6. **Bertram, W.K.** (2010). "Analytic Solutions for Optimal Statistical Arbitrage Trading." *Physica A*, 389, 2234-2243.
7. **Elliott, R.J., Van der Hoek, J., & Malcolm, W.P.** (2005). "Pairs Trading." *Quantitative Finance*, 5(3), 271-276.
8. **Kalman, R.E.** (1960). "A New Approach to Linear Filtering and Prediction Problems." *Journal of Basic Engineering*, 82(1), 35-45.
9. **Do, B., & Faff, R.** (2010). "Does Simple Pairs Trading Still Work?" *Financial Analysts Journal*, 66(4), 83-95.
10. **Krauss, C.** (2017). "Statistical Arbitrage Pairs Trading Strategies: Review and Outlook." *Journal of Economic Surveys*, 31(2), 513-545.

### Practitioner Resources

11. **Ernie Chan.** (2009). *Quantitative Trading*. Wiley. (Chapters on pairs trading and cointegration.)
12. **Ernie Chan.** (2013). *Algorithmic Trading*. Wiley. (Kalman filter and advanced stat arb.)
13. **Pole, A.** (2007). *Statistical Arbitrage: Algorithmic Trading Insights and Techniques*. Wiley.
14. **Whistler, M.** (2004). *Trading Pairs*. Wiley.

### Software and Tools

15. **statsmodels** (Python): Cointegration tests, VAR models, Kalman filter
16. **pykalman** (Python): Kalman filter implementation
17. **CCXT**: Unified API for crypto exchange execution
18. **Zipline / Backtrader**: Backtesting frameworks with multi-asset support

---

*This document is part of the Multi-Agent AI Trading System knowledge base. Statistical arbitrage provides market-neutral alpha by exploiting temporary mispricings between cointegrated assets, offering diversification from directional strategies.*
