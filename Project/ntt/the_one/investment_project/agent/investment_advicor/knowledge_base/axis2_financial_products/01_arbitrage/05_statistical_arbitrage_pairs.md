# Statistical Arbitrage & Pairs Trading — Complete Strategy Documentation

> **Document Version:** 2.0
> **Last Updated:** 2026-04-12
> **Classification:** Core Knowledge Base — Axis 2: Financial Products
> **Strategy Type:** Statistical Arbitrage (Risk-Bearing, Mean-Reversion)
> **Markets:** Forex, Crypto (CeFi), Equities
> **Frequency:** Low to Medium Frequency (hours to weeks)

---

## Table of Contents

1. [Core Logic — Cointegration Theory](#1-core-logic--cointegration-theory)
2. [Pair Selection Methodology](#2-pair-selection-methodology)
3. [Z-Score Calculation and Trading Signals](#3-z-score-calculation-and-trading-signals)
4. [Mean Reversion Half-Life](#4-mean-reversion-half-life)
5. [Kalman Filter for Dynamic Hedge Ratio](#5-kalman-filter-for-dynamic-hedge-ratio)
6. [Entry and Exit Thresholds](#6-entry-and-exit-thresholds)
7. [Mathematical Framework](#7-mathematical-framework)
8. [Application to Cryptocurrency Pairs](#8-application-to-cryptocurrency-pairs)
9. [Complete Execution Flow](#9-complete-execution-flow)
10. [Risk Parameters](#10-risk-parameters)
11. [Backtesting and Performance Analysis](#11-backtesting-and-performance-analysis)
12. [References](#12-references)

---

## 1. Core Logic — Cointegration Theory

### 1.1 The Fundamental Idea

Statistical arbitrage (stat arb) in pairs trading is based on the observation that certain pairs of assets move together over time due to economic relationships. When they temporarily diverge, we bet on convergence. Unlike pure arbitrage, this carries genuine market risk — the spread may not converge within our time horizon.

### 1.2 Correlation vs. Cointegration

**Critical Distinction:**

- **Correlation** measures the linear relationship between returns: $\rho(R_X, R_Y)$
  - Two assets can be highly correlated but NOT cointegrated
  - Correlation can break down over time (non-stationary)
  
- **Cointegration** measures whether a linear combination of two price series is stationary:
  - If $X_t \sim I(1)$ and $Y_t \sim I(1)$ (both non-stationary/unit-root processes)
  - But $Z_t = Y_t - \beta X_t \sim I(0)$ (stationary)
  - Then $X$ and $Y$ are cointegrated with cointegrating vector $[1, -\beta]$

**Why cointegration matters:**
- Correlated assets may drift apart indefinitely
- Cointegrated assets have a **mean-reverting spread** — they MUST eventually reconverge
- This provides a statistical edge: we can trade the spread with quantifiable risk

### 1.3 Economic Intuition

Assets may be cointegrated because:
1. **Same underlying value driver:** BTC and ETH are both driven by crypto market sentiment
2. **Structural relationship:** Gold mining stocks and gold price
3. **Sector membership:** Coca-Cola and Pepsi (consumer staples)
4. **Cross-listing:** Same stock on different exchanges
5. **Derivatives relationship:** Futures and spot prices

### 1.4 The Pairs Trading Strategy — Step by Step

```
1. IDENTIFY cointegrated pairs (statistical testing)
2. ESTIMATE the hedge ratio (how much of Y to trade per unit of X)
3. CALCULATE the spread: S_t = Y_t - beta * X_t
4. NORMALIZE the spread: z_t = (S_t - mean(S)) / std(S)
5. ENTER when spread deviates beyond threshold (e.g., |z| > 2)
   - If z > +2: spread is too wide → SHORT the spread (short Y, long X)
   - If z < -2: spread is too narrow → LONG the spread (long Y, short X)
6. EXIT when spread reverts to mean (|z| < 0.5 or z crosses zero)
7. STOP LOSS if spread diverges further (|z| > 4)
```

---

## 2. Pair Selection Methodology

### 2.1 Step 1: Universe Definition

Define the universe of candidate pairs based on:
- Same asset class (crypto-crypto, forex-forex)
- Same sector or market segment
- Sufficient liquidity (minimum daily volume)
- Data availability (minimum history)

### 2.2 Step 2: Pre-Screening with Correlation

Filter pairs with minimum correlation threshold:

$$\rho_{X,Y} = \frac{\text{Cov}(R_X, R_Y)}{\sigma_{R_X} \times \sigma_{R_Y}} > \rho_{min}$$

Typical threshold: $\rho_{min} = 0.70$

### 2.3 Step 3: Cointegration Testing

#### Engle-Granger Two-Step Method

**Step 1:** Estimate the cointegrating regression:

$$Y_t = \alpha + \beta X_t + \epsilon_t$$

Via OLS regression.

**Step 2:** Test the residuals $\hat{\epsilon}_t$ for stationarity using the Augmented Dickey-Fuller (ADF) test:

$$\Delta \hat{\epsilon}_t = \gamma \hat{\epsilon}_{t-1} + \sum_{i=1}^{p} \delta_i \Delta \hat{\epsilon}_{t-i} + u_t$$

**Null hypothesis:** $H_0: \gamma = 0$ (unit root, no cointegration)
**Alternative:** $H_1: \gamma < 0$ (stationary, cointegrated)

If p-value < 0.05 (or test statistic exceeds critical value), reject $H_0$ → pair is cointegrated.

**Critical values** (Engle-Granger, 2 variables):

| Significance | Critical Value |
|:------------:|:--------------:|
| 1% | -3.90 |
| 5% | -3.34 |
| 10% | -3.04 |

#### Johansen Test

For testing cointegration among multiple variables simultaneously:

$$\Delta \mathbf{Y}_t = \Pi \mathbf{Y}_{t-1} + \sum_{i=1}^{p-1} \Gamma_i \Delta \mathbf{Y}_{t-i} + \mathbf{u}_t$$

Where $\Pi = \alpha \beta'$ and:
- $\text{rank}(\Pi) = r$ gives the number of cointegrating relationships
- $\beta$ contains the cointegrating vectors
- $\alpha$ contains the adjustment speeds

**Trace test:**

$$\lambda_{trace}(r) = -T \sum_{i=r+1}^{n} \ln(1 - \hat{\lambda}_i)$$

**Maximum eigenvalue test:**

$$\lambda_{max}(r, r+1) = -T \ln(1 - \hat{\lambda}_{r+1})$$

### 2.4 Step 4: Spread Stationarity Verification

Beyond cointegration testing, verify spread properties:

1. **ADF test on the spread** (should reject unit root)
2. **KPSS test** (should NOT reject stationarity)
3. **Hurst exponent** (should be < 0.5 for mean-reverting process)
4. **Half-life** (should be reasonable: 1-30 days)

### 2.5 Step 5: Out-of-Sample Validation

- Split data into in-sample (training) and out-of-sample (validation)
- Re-test cointegration on out-of-sample data
- Verify that hedge ratio is stable
- Paper-trade before live deployment

### 2.6 Pair Selection Code

```python
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint, adfuller
from statsmodels.regression.linear_model import OLS
from itertools import combinations

class PairSelector:
    """
    Systematic pair selection for statistical arbitrage.
    """
    
    def __init__(self, price_data: pd.DataFrame, min_correlation: float = 0.7,
                 max_pvalue: float = 0.05, min_half_life: float = 1.0,
                 max_half_life: float = 30.0):
        """
        Args:
            price_data: DataFrame with asset prices as columns, datetime index
            min_correlation: Minimum correlation threshold
            max_pvalue: Maximum p-value for cointegration test
            min_half_life: Minimum acceptable half-life (days)
            max_half_life: Maximum acceptable half-life (days)
        """
        self.prices = price_data
        self.min_corr = min_correlation
        self.max_pval = max_pvalue
        self.min_hl = min_half_life
        self.max_hl = max_half_life
    
    def find_pairs(self) -> List[dict]:
        """
        Find all valid cointegrated pairs from the price universe.
        
        Returns list of pair dictionaries sorted by quality score.
        """
        assets = self.prices.columns.tolist()
        valid_pairs = []
        
        for asset_x, asset_y in combinations(assets, 2):
            # Step 1: Correlation pre-screen
            returns_x = self.prices[asset_x].pct_change().dropna()
            returns_y = self.prices[asset_y].pct_change().dropna()
            
            correlation = returns_x.corr(returns_y)
            if abs(correlation) < self.min_corr:
                continue
            
            # Step 2: Cointegration test (Engle-Granger)
            score, pvalue, _ = coint(
                self.prices[asset_x], self.prices[asset_y]
            )
            
            if pvalue > self.max_pval:
                continue
            
            # Step 3: Estimate hedge ratio
            hedge_ratio = self.estimate_hedge_ratio(asset_x, asset_y)
            
            # Step 4: Calculate spread
            spread = self.prices[asset_y] - hedge_ratio * self.prices[asset_x]
            
            # Step 5: Test spread stationarity (ADF)
            adf_stat, adf_pval, _, _, _, _ = adfuller(spread, maxlag=20)
            if adf_pval > 0.05:
                continue
            
            # Step 6: Calculate half-life
            half_life = self.calculate_half_life(spread)
            if half_life < self.min_hl or half_life > self.max_hl:
                continue
            
            # Step 7: Calculate Hurst exponent
            hurst = self.calculate_hurst_exponent(spread)
            if hurst >= 0.5:
                continue  # Not mean-reverting
            
            # Step 8: Quality score
            quality_score = self.calculate_quality_score(
                correlation, pvalue, half_life, hurst, spread
            )
            
            valid_pairs.append({
                'asset_x': asset_x,
                'asset_y': asset_y,
                'hedge_ratio': hedge_ratio,
                'correlation': correlation,
                'coint_pvalue': pvalue,
                'coint_score': score,
                'adf_pvalue': adf_pval,
                'half_life_days': half_life,
                'hurst_exponent': hurst,
                'spread_mean': spread.mean(),
                'spread_std': spread.std(),
                'quality_score': quality_score,
            })
        
        # Sort by quality score
        return sorted(valid_pairs, key=lambda x: x['quality_score'], reverse=True)
    
    def estimate_hedge_ratio(self, asset_x: str, asset_y: str) -> float:
        """Estimate hedge ratio via OLS regression."""
        X = self.prices[asset_x].values.reshape(-1, 1)
        Y = self.prices[asset_y].values
        
        # Add constant
        X_with_const = np.column_stack([np.ones(len(X)), X])
        
        # OLS: Y = alpha + beta * X
        model = OLS(Y, X_with_const).fit()
        beta = model.params[1]
        
        return beta
    
    def calculate_half_life(self, spread: pd.Series) -> float:
        """
        Calculate the mean-reversion half-life of the spread.
        
        Uses the Ornstein-Uhlenbeck process model:
        dS = theta * (mu - S) * dt + sigma * dW
        
        Half-life = ln(2) / theta
        """
        spread_lag = spread.shift(1).dropna()
        spread_diff = spread.diff().dropna()
        
        # Align
        spread_lag = spread_lag.iloc[1:]
        spread_diff = spread_diff.iloc[1:]
        
        # Regress: delta_S = theta * (S_{t-1} - mu) + epsilon
        # Or: delta_S = alpha + beta * S_{t-1}
        X = spread_lag.values.reshape(-1, 1)
        X_with_const = np.column_stack([np.ones(len(X)), X])
        Y = spread_diff.values
        
        model = OLS(Y, X_with_const).fit()
        theta = -model.params[1]  # Mean-reversion speed (negative of beta)
        
        if theta <= 0:
            return float('inf')  # Not mean-reverting
        
        half_life = np.log(2) / theta
        return half_life
    
    def calculate_hurst_exponent(self, series: pd.Series, max_lag: int = 100) -> float:
        """
        Calculate the Hurst exponent using the R/S (Rescaled Range) method.
        
        H < 0.5: Mean-reverting (anti-persistent)
        H = 0.5: Random walk (Brownian motion)
        H > 0.5: Trending (persistent)
        """
        lags = range(2, max_lag)
        rs_values = []
        
        for lag in lags:
            # Split series into non-overlapping sub-series of length 'lag'
            n_subseries = len(series) // lag
            rs_per_lag = []
            
            for i in range(n_subseries):
                subseries = series.iloc[i*lag:(i+1)*lag]
                mean_sub = subseries.mean()
                
                # Cumulative deviation from mean
                cumdev = (subseries - mean_sub).cumsum()
                
                # Range
                R = cumdev.max() - cumdev.min()
                
                # Standard deviation
                S = subseries.std()
                
                if S > 0:
                    rs_per_lag.append(R / S)
            
            if rs_per_lag:
                rs_values.append(np.mean(rs_per_lag))
        
        # Fit log(R/S) = H * log(lag) + c
        if len(rs_values) < 2:
            return 0.5
        
        log_lags = np.log(list(lags)[:len(rs_values)])
        log_rs = np.log(rs_values)
        
        # Linear regression
        slope, _ = np.polyfit(log_lags, log_rs, 1)
        
        return slope
    
    def calculate_quality_score(self, correlation, pvalue, half_life, 
                                 hurst, spread) -> float:
        """
        Calculate a composite quality score for the pair.
        
        Higher score = better pair for trading.
        """
        score = 0.0
        
        # Correlation component (higher = better, max 20 points)
        score += abs(correlation) * 20
        
        # Cointegration strength (lower p-value = better, max 30 points)
        score += (1 - pvalue) * 30
        
        # Half-life component (prefer 5-15 days, max 25 points)
        ideal_hl = 10
        hl_score = max(0, 25 - abs(half_life - ideal_hl) * 2)
        score += hl_score
        
        # Hurst exponent (lower = more mean-reverting, max 25 points)
        score += (0.5 - hurst) * 50  # max 25 when hurst = 0
        
        return score
```

---

## 3. Z-Score Calculation and Trading Signals

### 3.1 Spread Construction

Given the cointegrated pair $(X, Y)$ with hedge ratio $\beta$:

$$S_t = Y_t - \beta \cdot X_t$$

Or equivalently (log-price version for better statistical properties):

$$S_t = \ln(Y_t) - \beta \cdot \ln(X_t)$$

### 3.2 Z-Score Normalization

The z-score normalizes the spread to units of standard deviation:

$$z_t = \frac{S_t - \mu_S}{\sigma_S}$$

Where:
- $\mu_S$ = mean of the spread (rolling or expanding window)
- $\sigma_S$ = standard deviation of the spread (rolling or expanding window)

**Rolling window z-score:**

$$z_t = \frac{S_t - \overline{S}_{t,w}}{\hat{\sigma}_{t,w}}$$

Where $\overline{S}_{t,w}$ and $\hat{\sigma}_{t,w}$ are the mean and standard deviation over the last $w$ observations.

**Common window sizes:**
- 20-30 periods for intraday trading
- 60-120 periods for daily trading
- 252 periods (1 year) for long-term strategies

### 3.3 Trading Signals

| Z-Score Value | Signal | Action |
|:-------------:|:------:|--------|
| $z > +2.0$ | Short spread | Short Y, Long $\beta$ units of X |
| $z > +2.5$ | Strong short | Increase short position |
| $-0.5 < z < +0.5$ | Close position | Exit any open position |
| $z < -2.0$ | Long spread | Long Y, Short $\beta$ units of X |
| $z < -2.5$ | Strong long | Increase long position |
| $z > +4.0$ | Stop loss (short) | Close short, potential regime break |
| $z < -4.0$ | Stop loss (long) | Close long, potential regime break |

### 3.4 Signal Generation Code

```python
class PairsTradingSignals:
    """Generate trading signals for pairs trading strategy."""
    
    def __init__(self, config: dict):
        self.entry_threshold = config.get('entry_z', 2.0)
        self.exit_threshold = config.get('exit_z', 0.5)
        self.stop_loss_z = config.get('stop_loss_z', 4.0)
        self.lookback = config.get('lookback', 60)
        self.position = 0  # -1, 0, +1
    
    def calculate_z_score(self, spread: pd.Series) -> pd.Series:
        """Calculate rolling z-score of the spread."""
        rolling_mean = spread.rolling(window=self.lookback).mean()
        rolling_std = spread.rolling(window=self.lookback).std()
        
        z_score = (spread - rolling_mean) / rolling_std
        return z_score
    
    def generate_signals(self, spread: pd.Series) -> pd.DataFrame:
        """
        Generate trading signals based on z-score.
        
        Returns DataFrame with columns: z_score, signal, position
        """
        z = self.calculate_z_score(spread)
        
        signals = pd.DataFrame(index=spread.index)
        signals['spread'] = spread
        signals['z_score'] = z
        signals['signal'] = 0
        signals['position'] = 0
        
        position = 0
        
        for i in range(len(signals)):
            z_val = signals['z_score'].iloc[i]
            
            if np.isnan(z_val):
                signals.iloc[i, signals.columns.get_loc('position')] = 0
                continue
            
            # Entry signals
            if position == 0:
                if z_val > self.entry_threshold:
                    position = -1  # Short spread
                    signals.iloc[i, signals.columns.get_loc('signal')] = -1
                elif z_val < -self.entry_threshold:
                    position = 1   # Long spread
                    signals.iloc[i, signals.columns.get_loc('signal')] = 1
            
            # Exit signals
            elif position == -1:  # Currently short spread
                if z_val < self.exit_threshold:
                    position = 0   # Close
                    signals.iloc[i, signals.columns.get_loc('signal')] = 1  # Buy to close
                elif z_val > self.stop_loss_z:
                    position = 0   # Stop loss
                    signals.iloc[i, signals.columns.get_loc('signal')] = 2  # Stop loss signal
            
            elif position == 1:   # Currently long spread
                if z_val > -self.exit_threshold:
                    position = 0   # Close
                    signals.iloc[i, signals.columns.get_loc('signal')] = -1  # Sell to close
                elif z_val < -self.stop_loss_z:
                    position = 0   # Stop loss
                    signals.iloc[i, signals.columns.get_loc('signal')] = -2  # Stop loss signal
            
            signals.iloc[i, signals.columns.get_loc('position')] = position
        
        return signals
```

---

## 4. Mean Reversion Half-Life

### 4.1 The Ornstein-Uhlenbeck Process

The spread is modeled as an Ornstein-Uhlenbeck (OU) process:

$$dS_t = \theta(\mu - S_t)dt + \sigma dW_t$$

Where:
- $\theta$ = speed of mean reversion (higher = faster reversion)
- $\mu$ = long-run mean of the spread
- $\sigma$ = volatility of the spread
- $dW_t$ = Wiener process (Brownian motion)

### 4.2 Half-Life Derivation

The half-life is the expected time for the spread to revert halfway to its mean:

$$\tau_{1/2} = \frac{\ln(2)}{\theta}$$

### 4.3 Estimating Theta

**Method 1: OLS Regression**

Discretize the OU process:

$$S_t - S_{t-1} = \theta(\mu - S_{t-1})\Delta t + \sigma\sqrt{\Delta t}\epsilon_t$$

$$\Delta S_t = a + b \cdot S_{t-1} + \epsilon_t$$

Where $b = -\theta \cdot \Delta t$ and $a = \theta \cdot \mu \cdot \Delta t$.

Therefore: $\theta = -b / \Delta t$ and $\tau_{1/2} = -\ln(2) \cdot \Delta t / b$

For daily data ($\Delta t = 1$ day): $\tau_{1/2} = -\ln(2) / b$ days.

**Method 2: Maximum Likelihood Estimation (MLE)**

The OU process has a known transition density:

$$S_t | S_{t-1} \sim N\left(\mu + (S_{t-1} - \mu)e^{-\theta \Delta t}, \frac{\sigma^2}{2\theta}(1 - e^{-2\theta \Delta t})\right)$$

MLE provides more efficient estimates but is computationally more intensive.

### 4.4 Half-Life Interpretation

| Half-Life (Days) | Interpretation | Trading Suitability |
|:----------------:|:--------------:|:-------------------:|
| < 1 | Very fast reversion | Intraday only, hard to capture |
| 1-5 | Fast reversion | Short-term swing trading |
| 5-15 | Moderate reversion | **Ideal for pairs trading** |
| 15-30 | Slow reversion | Longer holding period required |
| 30-60 | Very slow | Capital-intensive, higher risk |
| > 60 | Too slow | Not suitable for active trading |

### 4.5 Half-Life Stability Analysis

The half-life should be relatively stable over time. Rolling calculation:

```python
def rolling_half_life(spread: pd.Series, window: int = 120) -> pd.Series:
    """Calculate rolling half-life over time."""
    half_lives = pd.Series(index=spread.index, dtype=float)
    
    for i in range(window, len(spread)):
        window_spread = spread.iloc[i-window:i]
        hl = calculate_half_life(window_spread)
        half_lives.iloc[i] = hl
    
    return half_lives
```

If the half-life varies dramatically over time, the pair may not be reliably cointegrated.

---

## 5. Kalman Filter for Dynamic Hedge Ratio

### 5.1 Why Dynamic Hedge Ratios?

The cointegrating relationship between two assets may change over time:
- Market regime shifts
- Changes in fundamental relationships
- Structural breaks

A static OLS hedge ratio becomes stale. The **Kalman filter** provides an optimal, dynamically updating estimate of the hedge ratio.

### 5.2 State-Space Model

**Observation equation:**

$$Y_t = \beta_t \cdot X_t + \alpha_t + \epsilon_t, \quad \epsilon_t \sim N(0, R)$$

**State transition equation:**

$$\begin{bmatrix} \alpha_t \\ \beta_t \end{bmatrix} = \begin{bmatrix} \alpha_{t-1} \\ \beta_{t-1} \end{bmatrix} + \begin{bmatrix} \eta_t^{\alpha} \\ \eta_t^{\beta} \end{bmatrix}, \quad \begin{bmatrix} \eta^{\alpha} \\ \eta^{\beta} \end{bmatrix} \sim N\left(\mathbf{0}, Q\right)$$

Where:
- $\beta_t$ = time-varying hedge ratio (state variable)
- $\alpha_t$ = time-varying intercept (state variable)
- $R$ = observation noise variance
- $Q$ = state transition noise covariance matrix

### 5.3 Kalman Filter Equations

**Prediction step:**

$$\hat{\mathbf{x}}_{t|t-1} = F \hat{\mathbf{x}}_{t-1|t-1}$$
$$P_{t|t-1} = F P_{t-1|t-1} F^T + Q$$

**Update step:**

$$K_t = P_{t|t-1} H_t^T (H_t P_{t|t-1} H_t^T + R)^{-1}$$
$$\hat{\mathbf{x}}_{t|t} = \hat{\mathbf{x}}_{t|t-1} + K_t (Y_t - H_t \hat{\mathbf{x}}_{t|t-1})$$
$$P_{t|t} = (I - K_t H_t) P_{t|t-1}$$

Where:
- $\mathbf{x}_t = [\alpha_t, \beta_t]^T$ = state vector
- $F = I$ (random walk state transition)
- $H_t = [1, X_t]$ = observation matrix
- $K_t$ = Kalman gain
- $P_t$ = state covariance matrix

### 5.4 Implementation

```python
import numpy as np

class KalmanFilterHedgeRatio:
    """
    Kalman filter for dynamically estimating the hedge ratio.
    
    State: [alpha, beta] where Y = alpha + beta * X + noise
    """
    
    def __init__(self, delta: float = 0.0001, obs_noise: float = 1.0):
        """
        Args:
            delta: State transition noise parameter (smaller = smoother)
            obs_noise: Observation noise variance (Ve)
        """
        self.delta = delta
        self.Ve = obs_noise
        
        # State dimension
        self.n_states = 2  # [alpha, beta]
        
        # Initialize state
        self.theta = np.zeros(self.n_states)  # [alpha_0, beta_0]
        self.P = np.eye(self.n_states) * 1.0  # Initial uncertainty (large)
        
        # State transition noise
        self.Vw = delta / (1 - delta) * np.eye(self.n_states)
        
        # History
        self.beta_history = []
        self.alpha_history = []
        self.spread_history = []
    
    def update(self, x: float, y: float) -> dict:
        """
        Process one observation and update the hedge ratio estimate.
        
        Args:
            x: Price of asset X at time t
            y: Price of asset Y at time t
        
        Returns:
            dict with beta, alpha, spread, and estimation error
        """
        # Observation vector
        F = np.array([1.0, x])  # H_t = [1, X_t]
        
        # Prediction step
        # theta_predicted = theta (random walk, no change)
        # P_predicted = P + Vw
        R = self.P + self.Vw
        
        # Update step
        # Innovation (prediction error)
        y_hat = F.dot(self.theta)
        e = y - y_hat  # Innovation
        
        # Innovation covariance
        S = F.dot(R).dot(F.T) + self.Ve
        
        # Kalman gain
        K = R.dot(F.T) / S
        
        # Update state estimate
        self.theta = self.theta + K * e
        
        # Update covariance
        self.P = R - np.outer(K, F).dot(R)
        
        # Extract results
        alpha = self.theta[0]
        beta = self.theta[1]
        spread = y - beta * x - alpha
        
        # Store history
        self.beta_history.append(beta)
        self.alpha_history.append(alpha)
        self.spread_history.append(spread)
        
        return {
            'beta': beta,
            'alpha': alpha,
            'spread': spread,
            'estimation_error': e,
            'kalman_gain': K,
        }
    
    def get_current_beta(self) -> float:
        """Get current hedge ratio estimate."""
        return self.theta[1]
    
    def get_beta_series(self) -> np.ndarray:
        """Get full history of beta estimates."""
        return np.array(self.beta_history)
    
    def get_spread_series(self) -> np.ndarray:
        """Get full history of Kalman-filtered spread."""
        return np.array(self.spread_history)


class DynamicPairsTrader:
    """
    Pairs trading with Kalman filter-based dynamic hedge ratio.
    """
    
    def __init__(self, config: dict):
        self.kf = KalmanFilterHedgeRatio(
            delta=config.get('delta', 0.0001),
            obs_noise=config.get('obs_noise', 1.0)
        )
        self.entry_z = config.get('entry_z', 2.0)
        self.exit_z = config.get('exit_z', 0.5)
        self.lookback = config.get('lookback', 60)
        self.position = 0
    
    def process_tick(self, price_x: float, price_y: float) -> dict:
        """
        Process one price observation and generate signal.
        """
        # Update Kalman filter
        kf_result = self.kf.update(price_x, price_y)
        
        # Calculate z-score from recent spread history
        spread_series = np.array(self.kf.spread_history)
        
        if len(spread_series) < self.lookback:
            return {'signal': 0, 'z_score': 0, 'beta': kf_result['beta']}
        
        recent_spread = spread_series[-self.lookback:]
        mu = recent_spread.mean()
        sigma = recent_spread.std()
        
        if sigma == 0:
            return {'signal': 0, 'z_score': 0, 'beta': kf_result['beta']}
        
        z_score = (kf_result['spread'] - mu) / sigma
        
        # Generate signal
        signal = self.generate_signal(z_score)
        
        return {
            'signal': signal,
            'z_score': z_score,
            'beta': kf_result['beta'],
            'alpha': kf_result['alpha'],
            'spread': kf_result['spread'],
        }
    
    def generate_signal(self, z: float) -> int:
        """Generate trading signal from z-score."""
        if self.position == 0:
            if z > self.entry_z:
                self.position = -1
                return -1  # Short spread
            elif z < -self.entry_z:
                self.position = 1
                return 1  # Long spread
        elif self.position == -1:
            if z < self.exit_z:
                self.position = 0
                return 1  # Close short (buy to close)
        elif self.position == 1:
            if z > -self.exit_z:
                self.position = 0
                return -1  # Close long (sell to close)
        
        return 0  # No signal
```

---

## 6. Entry and Exit Thresholds

### 6.1 Threshold Optimization

The choice of entry/exit thresholds significantly impacts strategy performance:

| Threshold Pair (Entry/Exit) | Trade Frequency | Win Rate | Avg Profit | Max Drawdown |
|:--------------------------:|:---------------:|:--------:|:----------:|:------------:|
| 1.5 / 0.0 | Very High | 55% | Small | Moderate |
| 2.0 / 0.5 | High | 62% | Moderate | Moderate |
| 2.0 / 0.0 | High | 65% | Moderate | Low-Moderate |
| 2.5 / 0.5 | Moderate | 70% | Large | Low |
| 3.0 / 0.0 | Low | 75% | Very Large | Very Low |
| 3.0 / 1.0 | Low | 72% | Large | Low |

### 6.2 Optimal Threshold Selection

The optimal entry threshold $z^*$ depends on:

1. **Half-life:** Faster mean reversion allows tighter thresholds
2. **Transaction costs:** Higher costs require wider entry thresholds
3. **Spread volatility:** Higher volatility allows wider thresholds
4. **Risk appetite:** Conservative traders use wider thresholds

**Rule of thumb:**

$$z_{entry}^* \approx \frac{C_{roundtrip}}{\sigma_S} + z_{min}$$

Where:
- $C_{roundtrip}$ = total round-trip cost (entry + exit fees + slippage)
- $\sigma_S$ = spread standard deviation (in same units as cost)
- $z_{min}$ = minimum z-score for statistical significance (typically 1.5-2.0)

### 6.3 Asymmetric Thresholds

In some markets, mean reversion is asymmetric:
- Positive deviations may revert faster than negative (or vice versa)
- Use different thresholds for long and short entries

```python
THRESHOLD_CONFIG = {
    # Symmetric thresholds
    'entry_long_z': -2.0,      # Enter long when z < -2.0
    'entry_short_z': 2.0,      # Enter short when z > 2.0
    'exit_long_z': -0.5,       # Exit long when z > -0.5
    'exit_short_z': 0.5,       # Exit short when z < 0.5
    
    # Stop losses (regime break protection)
    'stop_loss_long_z': -4.0,  # Stop long if z < -4.0
    'stop_loss_short_z': 4.0,  # Stop short if z > 4.0
    
    # Scaling thresholds (for pyramiding)
    'scale_in_long_z': -2.5,   # Add to long if z < -2.5
    'scale_in_short_z': 2.5,   # Add to short if z > 2.5
    
    # Time-based exit
    'max_holding_periods': 30,  # Force exit after 30 periods
}
```

### 6.4 Threshold Adaptation

Dynamically adjust thresholds based on market conditions:

$$z_{entry,t} = z_{base} \times \left(1 + k \times \frac{\sigma_{t,short}}{\sigma_{t,long}}\right)$$

Where:
- $\sigma_{t,short}$ = short-term spread volatility
- $\sigma_{t,long}$ = long-term spread volatility
- $k$ = scaling factor

When short-term volatility is elevated relative to long-term, widen thresholds (require larger deviations before entering).

---

## 7. Mathematical Framework

### 7.1 Augmented Dickey-Fuller (ADF) Test

Tests for unit root in the spread:

$$\Delta S_t = \alpha + \gamma S_{t-1} + \sum_{i=1}^{p} \delta_i \Delta S_{t-i} + \epsilon_t$$

**Test statistic:**

$$\text{ADF} = \frac{\hat{\gamma}}{SE(\hat{\gamma})}$$

Reject unit root (confirm stationarity) if ADF statistic < critical value.

### 7.2 KPSS Test

Tests for stationarity (reversed null hypothesis from ADF):

$$H_0$$: Series is stationary
$$H_1$$: Series has a unit root

**Use BOTH ADF and KPSS together:**
- ADF rejects AND KPSS does not reject → Strong evidence of stationarity
- ADF does not reject AND KPSS rejects → Strong evidence of unit root
- Both reject or both fail to reject → Inconclusive

### 7.3 Hurst Exponent

The Hurst exponent characterizes the long-term memory of a time series:

$$E\left[\frac{R(n)}{S(n)}\right] = C \cdot n^H$$

Where:
- $R(n)$ = range of cumulative deviations over $n$ observations
- $S(n)$ = standard deviation over $n$ observations
- $H$ = Hurst exponent

**Interpretation:**
- $H < 0.5$: Mean-reverting (anti-persistent) — **GOOD for pairs trading**
- $H = 0.5$: Random walk (no memory)
- $H > 0.5$: Trending (persistent) — **BAD for pairs trading**

### 7.4 Variance Ratio Test

Tests for mean reversion by comparing variance at different horizons:

$$VR(q) = \frac{\text{Var}(S_t - S_{t-q})}{q \cdot \text{Var}(S_t - S_{t-1})}$$

- $VR(q) = 1$: Random walk
- $VR(q) < 1$: Mean-reverting
- $VR(q) > 1$: Trending

### 7.5 Cointegrating Regression with Error Correction

**Error Correction Model (ECM):**

$$\Delta Y_t = \alpha_Y (Y_{t-1} - \beta X_{t-1} - \mu) + \gamma_Y \Delta X_t + \epsilon_t^Y$$
$$\Delta X_t = \alpha_X (Y_{t-1} - \beta X_{t-1} - \mu) + \gamma_X \Delta Y_t + \epsilon_t^X$$

Where:
- $\alpha_Y, \alpha_X$ = error correction coefficients (speed of adjustment)
- $Y_{t-1} - \beta X_{t-1} - \mu$ = error correction term (deviation from equilibrium)

The ECM tells us how quickly each asset adjusts to restore equilibrium.

### 7.6 Information Ratio of Pairs Strategy

$$IR = \frac{E[R_{strategy}]}{\sigma_{R_{strategy}}} = \frac{\mu_{trade} \times N_{trades/year} - C_{total}}{\sigma_{trade} \times \sqrt{N_{trades/year}}}$$

Where:
- $\mu_{trade}$ = average return per trade
- $\sigma_{trade}$ = standard deviation of return per trade
- $N_{trades/year}$ = number of trades per year
- $C_{total}$ = annual transaction costs

### 7.7 Maximum Likelihood for OU Process

Given discrete observations $\{S_0, S_1, ..., S_T\}$ at intervals $\Delta t$:

**Log-likelihood:**

$$\ell(\theta, \mu, \sigma) = -\frac{T}{2}\ln(2\pi) - \frac{T}{2}\ln(v^2) - \frac{1}{2v^2}\sum_{t=1}^{T}(S_t - S_{t-1}e^{-\theta\Delta t} - \mu(1-e^{-\theta\Delta t}))^2$$

Where $v^2 = \frac{\sigma^2}{2\theta}(1-e^{-2\theta\Delta t})$

MLE estimates:

$$\hat{\theta} = -\frac{\ln(\hat{\rho})}{\Delta t}$$

Where $\hat{\rho}$ is the OLS estimate of the AR(1) coefficient of the spread.

---

## 8. Application to Cryptocurrency Pairs

### 8.1 Crypto-Specific Considerations

1. **24/7 markets:** No overnight gaps or weekend effects
2. **Higher volatility:** Spreads have larger standard deviations
3. **Shorter half-lives:** Mean reversion tends to be faster
4. **Higher transaction costs:** Maker/taker fees of 5-10 bps per leg
5. **Regime changes:** Crypto market structure shifts more frequently
6. **Funding rate interaction:** Holding short positions incurs funding costs
7. **Lower liquidity:** Thinner order books than traditional markets

### 8.2 Promising Crypto Pairs

| Pair | Rationale | Typical Half-Life | Typical Sharpe |
|------|-----------|:-----------------:|:--------------:|
| BTC / ETH | Market leaders, co-move with crypto sentiment | 5-15 days | 1.5-2.5 |
| SOL / AVAX | Competing L1s, similar fundamentals | 3-10 days | 1.0-2.0 |
| LINK / UNI | DeFi infrastructure tokens | 3-8 days | 1.0-1.8 |
| AAVE / COMP | DeFi lending protocols | 2-7 days | 1.2-2.2 |
| MATIC / ARB | L2 scaling solutions | 3-12 days | 1.0-1.5 |
| BNB / FTT (historical) | Exchange tokens (CAUTION: counterparty risk) | 5-20 days | Variable |
| DOGE / SHIB | Meme coins (high volatility, less reliable) | 1-5 days | 0.5-1.5 |
| BTC / BTC.b (Avalanche) | Same asset, different chain | < 1 day | 2.0-4.0 |
| stETH / ETH | Liquid staking derivative | 1-3 days | 2.5-5.0 |

### 8.3 Crypto Pair Quality Assessment

```python
# Crypto-specific pair assessment criteria
CRYPTO_PAIR_CRITERIA = {
    # Minimum requirements
    'min_daily_volume_usd': 10_000_000,      # Each asset
    'min_market_cap_usd': 100_000_000,       # Each asset
    'min_data_history_days': 180,            # Minimum for testing
    'min_cointegration_pvalue': 0.05,        # Maximum p-value
    
    # Ideal ranges
    'ideal_half_life_range': (3, 20),        # Days
    'ideal_hurst_range': (0.2, 0.45),        # Below 0.5
    'ideal_correlation_range': (0.70, 0.95), # High but not 1.0
    
    # Risk filters
    'max_single_day_spread_change_pct': 0.15, # Spread shouldn't jump 15%
    'min_spread_mean_reversion_score': 0.6,   # Custom score 0-1
    'max_funding_rate_impact_bps': 5,         # Max funding drag per day
}
```

### 8.4 BTC/ETH Pairs Trade — Detailed Example

**Data:** 180 days of daily closing prices

**Step 1: Cointegration Test**
```
Engle-Granger test:
  Test statistic: -3.85
  Critical value (5%): -3.34
  P-value: 0.012
  Result: COINTEGRATED at 5% significance
```

**Step 2: Hedge Ratio (OLS)**
```
Regression: ETH = alpha + beta * BTC + epsilon
  beta (hedge ratio) = 0.0492
  alpha (intercept) = -1.50
  R-squared = 0.89
  
Interpretation: For every 1 BTC traded, trade 0.0492 ETH
(or: 1 ETH against 20.3 BTC in dollar-neutral terms)
```

**Step 3: Spread and Z-Score**
```
Spread = ETH_price - 0.0492 * BTC_price
Spread mean: $2.50
Spread std: $45.00
Current spread: $95.00
Current z-score: (95 - 2.5) / 45 = 2.06

Signal: SHORT the spread (short ETH, long 0.0492 BTC per ETH)
```

**Step 4: Position Sizing**
```
Capital: $100,000
Allocation to this pair: 20% = $20,000

Short $10,000 ETH (sell 3.125 ETH at $3,200)
Long $10,000 BTC (buy 0.1538 BTC at $65,000)

Dollar-neutral: +$10,000 BTC, -$10,000 ETH
Beta-neutral: checked (net beta to crypto market ~ 0)
```

**Step 5: Expected Outcome**
```
If spread reverts to mean (z=0):
  Spread change: 95 - 2.5 = $92.50 per unit
  Position profit: ~$92.50 * position_units
  Time to revert (expected): ~10 days (half-life)
  Annualized return: significant
  
Risk: if spread widens further (z > 4), stop loss triggers
```

---

## 9. Complete Execution Flow

### 9.1 Full Strategy Engine

```python
import asyncio
import time
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple

# ============================================================
# CONFIGURATION
# ============================================================

@dataclass
class StatArbConfig:
    # Pair selection
    universe: List[str]                  # Asset universe
    min_correlation: float = 0.70
    max_coint_pvalue: float = 0.05
    min_half_life_days: float = 2.0
    max_half_life_days: float = 25.0
    max_hurst: float = 0.48
    
    # Signal generation
    lookback_z_score: int = 60           # Rolling window for z-score
    entry_z: float = 2.0
    exit_z: float = 0.5
    stop_loss_z: float = 4.0
    
    # Kalman filter
    use_kalman: bool = True
    kalman_delta: float = 0.0001
    kalman_obs_noise: float = 1.0
    
    # Position sizing
    capital_per_pair_usd: float = 50_000
    max_pairs_simultaneously: int = 5
    max_total_exposure_usd: float = 500_000
    
    # Execution
    order_type: str = "LIMIT"
    max_slippage_bps: float = 5.0
    
    # Risk
    max_loss_per_pair_pct: float = 0.05   # 5%
    max_daily_loss_usd: float = 5_000
    max_drawdown_pct: float = 0.10
    max_holding_days: float = 30
    
    # Rebalancing
    rebalance_interval_hours: float = 24   # Re-estimate parameters daily
    retest_cointegration_days: int = 7     # Re-test cointegration weekly

# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class PairPosition:
    pair_id: str
    asset_x: str
    asset_y: str
    direction: int                # +1 = long spread, -1 = short spread
    hedge_ratio: float
    entry_z: float
    entry_time: float
    entry_price_x: float
    entry_price_y: float
    quantity_x: float
    quantity_y: float
    notional_usd: float
    unrealized_pnl: float = 0.0
    max_z_observed: float = 0.0
    
@dataclass
class PairMetrics:
    asset_x: str
    asset_y: str
    hedge_ratio: float
    half_life: float
    hurst: float
    coint_pvalue: float
    correlation: float
    spread_mean: float
    spread_std: float
    quality_score: float
    last_updated: float

# ============================================================
# MAIN ENGINE
# ============================================================

class StatisticalArbitrageEngine:
    """
    Complete statistical arbitrage / pairs trading engine.
    
    Pipeline:
    1. Pair selection and cointegration testing
    2. Dynamic hedge ratio estimation (Kalman filter)
    3. Z-score signal generation
    4. Position management (entry, exit, stop-loss)
    5. Risk management and P&L tracking
    """
    
    def __init__(self, config: StatArbConfig, exchange_client, data_feed):
        self.config = config
        self.exchange = exchange_client
        self.data_feed = data_feed
        
        # State
        self.active_pairs: Dict[str, PairMetrics] = {}
        self.positions: Dict[str, PairPosition] = {}
        self.kalman_filters: Dict[str, KalmanFilterHedgeRatio] = {}
        self.price_history: Dict[str, pd.Series] = {}
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.is_running = False
    
    # ----------------------------------------------------------
    # MAIN LOOP
    # ----------------------------------------------------------
    
    async def run(self):
        """Main strategy loop."""
        self.is_running = True
        
        # Initial pair selection
        await self.select_pairs()
        
        while self.is_running:
            try:
                # Update prices
                await self.update_prices()
                
                # Update Kalman filters and z-scores
                signals = self.generate_signals()
                
                # Process signals
                for pair_id, signal_data in signals.items():
                    await self.process_signal(pair_id, signal_data)
                
                # Monitor existing positions
                await self.monitor_positions()
                
                # Periodic rebalancing
                if self.should_rebalance():
                    await self.rebalance()
                
                # Periodic cointegration re-testing
                if self.should_retest():
                    await self.select_pairs()
                
                # Sleep (depends on trading frequency)
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.handle_error(e)
    
    # ----------------------------------------------------------
    # PAIR SELECTION
    # ----------------------------------------------------------
    
    async def select_pairs(self):
        """
        Select cointegrated pairs from the universe.
        """
        # Load historical prices
        prices_df = await self.data_feed.get_historical_prices(
            self.config.universe, 
            lookback_days=180
        )
        
        # Run pair selection
        selector = PairSelector(
            prices_df,
            min_correlation=self.config.min_correlation,
            max_pvalue=self.config.max_coint_pvalue,
            min_half_life=self.config.min_half_life_days,
            max_half_life=self.config.max_half_life_days
        )
        
        valid_pairs = selector.find_pairs()
        
        # Take top N pairs by quality score
        top_pairs = valid_pairs[:self.config.max_pairs_simultaneously * 2]
        
        # Update active pairs
        self.active_pairs = {}
        for pair in top_pairs:
            pair_id = f"{pair['asset_x']}_{pair['asset_y']}"
            self.active_pairs[pair_id] = PairMetrics(
                asset_x=pair['asset_x'],
                asset_y=pair['asset_y'],
                hedge_ratio=pair['hedge_ratio'],
                half_life=pair['half_life_days'],
                hurst=pair['hurst_exponent'],
                coint_pvalue=pair['coint_pvalue'],
                correlation=pair['correlation'],
                spread_mean=pair['spread_mean'],
                spread_std=pair['spread_std'],
                quality_score=pair['quality_score'],
                last_updated=time.time()
            )
            
            # Initialize Kalman filter for each pair
            if self.config.use_kalman:
                self.kalman_filters[pair_id] = KalmanFilterHedgeRatio(
                    delta=self.config.kalman_delta,
                    obs_noise=self.config.kalman_obs_noise
                )
        
        print(f"[PAIRS] Selected {len(self.active_pairs)} active pairs")
        for pid, metrics in self.active_pairs.items():
            print(f"  {pid}: HL={metrics.half_life:.1f}d, "
                  f"Hurst={metrics.hurst:.3f}, "
                  f"Score={metrics.quality_score:.1f}")
    
    # ----------------------------------------------------------
    # SIGNAL GENERATION
    # ----------------------------------------------------------
    
    def generate_signals(self) -> Dict[str, dict]:
        """Generate trading signals for all active pairs."""
        signals = {}
        
        for pair_id, metrics in self.active_pairs.items():
            # Get latest prices
            price_x = self.get_latest_price(metrics.asset_x)
            price_y = self.get_latest_price(metrics.asset_y)
            
            if price_x is None or price_y is None:
                continue
            
            # Update Kalman filter
            if self.config.use_kalman and pair_id in self.kalman_filters:
                kf = self.kalman_filters[pair_id]
                kf_result = kf.update(price_x, price_y)
                
                current_beta = kf_result['beta']
                spread = kf_result['spread']
            else:
                current_beta = metrics.hedge_ratio
                spread = price_y - current_beta * price_x
            
            # Calculate z-score
            spread_series = self.get_spread_history(pair_id)
            if spread_series is None or len(spread_series) < self.config.lookback_z_score:
                continue
            
            recent = spread_series[-self.config.lookback_z_score:]
            mu = recent.mean()
            sigma = recent.std()
            
            if sigma == 0:
                continue
            
            z_score = (spread - mu) / sigma
            
            signals[pair_id] = {
                'z_score': z_score,
                'spread': spread,
                'beta': current_beta,
                'price_x': price_x,
                'price_y': price_y,
            }
        
        return signals
    
    # ----------------------------------------------------------
    # POSITION MANAGEMENT
    # ----------------------------------------------------------
    
    async def process_signal(self, pair_id: str, signal_data: dict):
        """Process a signal and manage positions."""
        z = signal_data['z_score']
        
        if pair_id in self.positions:
            # Existing position — check for exit
            position = self.positions[pair_id]
            
            if self.should_exit(position, z):
                await self.close_position(pair_id, "signal")
        else:
            # No position — check for entry
            if abs(z) > self.config.entry_z:
                # Check if we can open a new position
                if len(self.positions) >= self.config.max_pairs_simultaneously:
                    return
                
                direction = -1 if z > 0 else 1  # Short spread if z positive
                await self.open_position(pair_id, direction, signal_data)
    
    async def open_position(self, pair_id: str, direction: int, signal_data: dict):
        """Open a new pairs position."""
        metrics = self.active_pairs[pair_id]
        
        price_x = signal_data['price_x']
        price_y = signal_data['price_y']
        beta = signal_data['beta']
        z = signal_data['z_score']
        
        # Calculate position sizes (dollar-neutral)
        half_capital = self.config.capital_per_pair_usd / 2
        
        qty_y = half_capital / price_y
        qty_x = (half_capital * beta) / price_x  # Hedge ratio adjusted
        
        # Execute trades
        try:
            if direction == -1:  # Short spread: short Y, long X
                # Short Y
                order_y = await self.exchange.place_order(
                    symbol=f"{metrics.asset_y}/USDT",
                    side="SELL",
                    quantity=qty_y,
                    order_type=self.config.order_type
                )
                # Long X
                order_x = await self.exchange.place_order(
                    symbol=f"{metrics.asset_x}/USDT",
                    side="BUY",
                    quantity=qty_x,
                    order_type=self.config.order_type
                )
            else:  # Long spread: long Y, short X
                order_y = await self.exchange.place_order(
                    symbol=f"{metrics.asset_y}/USDT",
                    side="BUY",
                    quantity=qty_y,
                    order_type=self.config.order_type
                )
                order_x = await self.exchange.place_order(
                    symbol=f"{metrics.asset_x}/USDT",
                    side="SELL",
                    quantity=qty_x,
                    order_type=self.config.order_type
                )
            
            # Record position
            self.positions[pair_id] = PairPosition(
                pair_id=pair_id,
                asset_x=metrics.asset_x,
                asset_y=metrics.asset_y,
                direction=direction,
                hedge_ratio=beta,
                entry_z=z,
                entry_time=time.time(),
                entry_price_x=price_x,
                entry_price_y=price_y,
                quantity_x=qty_x,
                quantity_y=qty_y,
                notional_usd=self.config.capital_per_pair_usd,
            )
            
            print(
                f"[ENTRY] {pair_id} | Direction={'SHORT' if direction==-1 else 'LONG'} spread | "
                f"Z={z:.2f} | Beta={beta:.4f} | "
                f"Qty_X={qty_x:.4f} @ ${price_x:.2f} | "
                f"Qty_Y={qty_y:.4f} @ ${price_y:.2f}"
            )
            
        except Exception as e:
            self.handle_entry_error(pair_id, e)
    
    def should_exit(self, position: PairPosition, current_z: float) -> bool:
        """Determine if position should be closed."""
        # Mean reversion exit
        if position.direction == -1:  # Short spread
            if current_z < self.config.exit_z:
                return True
        else:  # Long spread
            if current_z > -self.config.exit_z:
                return True
        
        # Stop loss
        if abs(current_z) > self.config.stop_loss_z:
            return True
        
        # Time-based exit
        holding_days = (time.time() - position.entry_time) / 86400
        if holding_days > self.config.max_holding_days:
            return True
        
        # Loss-based exit
        if position.unrealized_pnl < -position.notional_usd * self.config.max_loss_per_pair_pct:
            return True
        
        return False
    
    async def close_position(self, pair_id: str, reason: str):
        """Close an existing pairs position."""
        position = self.positions[pair_id]
        
        try:
            if position.direction == -1:  # Was short spread
                # Buy back Y (close short)
                await self.exchange.place_order(
                    symbol=f"{position.asset_y}/USDT",
                    side="BUY", quantity=position.quantity_y,
                    order_type="MARKET"
                )
                # Sell X (close long)
                await self.exchange.place_order(
                    symbol=f"{position.asset_x}/USDT",
                    side="SELL", quantity=position.quantity_x,
                    order_type="MARKET"
                )
            else:
                await self.exchange.place_order(
                    symbol=f"{position.asset_y}/USDT",
                    side="SELL", quantity=position.quantity_y,
                    order_type="MARKET"
                )
                await self.exchange.place_order(
                    symbol=f"{position.asset_x}/USDT",
                    side="BUY", quantity=position.quantity_x,
                    order_type="MARKET"
                )
            
            # Calculate P&L
            pnl = self.calculate_position_pnl(position)
            self.total_pnl += pnl
            self.daily_pnl += pnl
            
            print(
                f"[EXIT] {pair_id} | Reason={reason} | "
                f"P&L=${pnl:.2f} | "
                f"Holding={(time.time()-position.entry_time)/3600:.1f}h"
            )
            
            del self.positions[pair_id]
            
        except Exception as e:
            self.handle_exit_error(pair_id, e)
    
    # ----------------------------------------------------------
    # MONITORING
    # ----------------------------------------------------------
    
    async def monitor_positions(self):
        """Update unrealized P&L for all positions."""
        for pair_id, position in self.positions.items():
            current_x = self.get_latest_price(position.asset_x)
            current_y = self.get_latest_price(position.asset_y)
            
            if current_x and current_y:
                pnl = self.calculate_unrealized_pnl(position, current_x, current_y)
                position.unrealized_pnl = pnl
    
    def calculate_unrealized_pnl(self, pos: PairPosition, 
                                  current_x: float, current_y: float) -> float:
        """Calculate unrealized P&L for a position."""
        if pos.direction == -1:  # Short Y, Long X
            pnl_y = pos.quantity_y * (pos.entry_price_y - current_y)  # Short Y
            pnl_x = pos.quantity_x * (current_x - pos.entry_price_x)  # Long X
        else:  # Long Y, Short X
            pnl_y = pos.quantity_y * (current_y - pos.entry_price_y)  # Long Y
            pnl_x = pos.quantity_x * (pos.entry_price_x - current_x)  # Short X
        
        return pnl_x + pnl_y
    
    def calculate_position_pnl(self, pos: PairPosition) -> float:
        """Calculate realized P&L (uses current prices)."""
        current_x = self.get_latest_price(pos.asset_x)
        current_y = self.get_latest_price(pos.asset_y)
        return self.calculate_unrealized_pnl(pos, current_x, current_y)
    
    # ----------------------------------------------------------
    # HELPERS
    # ----------------------------------------------------------
    
    def get_latest_price(self, asset: str) -> Optional[float]:
        """Get latest price for an asset."""
        history = self.price_history.get(asset)
        if history is not None and len(history) > 0:
            return history.iloc[-1]
        return None
    
    def get_spread_history(self, pair_id: str) -> Optional[pd.Series]:
        """Get historical spread for a pair."""
        if self.config.use_kalman and pair_id in self.kalman_filters:
            kf = self.kalman_filters[pair_id]
            if kf.spread_history:
                return pd.Series(kf.spread_history)
        return None
    
    def should_rebalance(self) -> bool:
        """Check if it's time to rebalance parameters."""
        # Implementation: check time since last rebalance
        return False  # Placeholder
    
    def should_retest(self) -> bool:
        """Check if it's time to re-test cointegration."""
        return False  # Placeholder
    
    def handle_error(self, e: Exception):
        print(f"[ERROR] {e}")
```

---

## 10. Risk Parameters

### 10.1 Comprehensive Risk Configuration

```python
STAT_ARB_RISK_PARAMS = {
    # Position Sizing
    "max_capital_per_pair_pct": 0.20,        # Max 20% of capital per pair
    "max_total_exposure_pct": 0.80,          # Max 80% deployed
    "max_pairs_simultaneously": 5,
    "min_diversification_pairs": 3,          # Don't trade fewer than 3 pairs
    
    # Entry/Exit
    "entry_z_threshold": 2.0,
    "exit_z_threshold": 0.5,
    "stop_loss_z": 4.0,
    "max_holding_days": 30,
    
    # Loss Limits
    "max_loss_per_pair_pct": 0.05,           # 5% stop per pair
    "max_daily_loss_pct": 0.02,              # 2% daily stop
    "max_weekly_loss_pct": 0.05,             # 5% weekly stop
    "max_drawdown_pct": 0.10,               # 10% total drawdown stop
    
    # Model Risk
    "min_coint_pvalue": 0.05,               # Reject pairs with p > 0.05
    "retest_frequency_days": 7,             # Weekly re-test
    "min_remaining_half_life_pct": 0.50,    # Exit if HL drops below 50% of entry HL
    "max_beta_change_pct": 0.30,            # Close if hedge ratio changes > 30%
    
    # Market Risk
    "max_single_asset_volatility_24h": 0.15, # Pause if 15% daily vol
    "max_correlation_breakdown": 0.20,       # Alert if correlation drops 20%
    "market_regime_filter": True,            # Disable in extreme volatility
    
    # Execution Risk
    "max_slippage_bps": 10,
    "max_execution_time_sec": 5,
    "min_liquidity_usd": 50_000,            # Per leg
    
    # Monitoring
    "pnl_update_frequency_sec": 60,
    "cointegration_check_frequency_hours": 24,
    "alert_on_z_beyond_3": True,
    "alert_on_hedge_ratio_drift": True,
}
```

### 10.2 Regime Detection and Filtering

```python
class RegimeFilter:
    """
    Detect market regimes and disable pairs trading during unfavorable conditions.
    
    Pairs trading performs poorly during:
    - Extreme trending markets (correlations break)
    - Very high volatility (spreads blow out)
    - Liquidity crises (mean reversion breaks)
    """
    
    def __init__(self, lookback: int = 20):
        self.lookback = lookback
    
    def is_safe_to_trade(self, market_data: dict) -> bool:
        """
        Check if current regime is suitable for pairs trading.
        """
        # Check overall market volatility
        btc_vol = market_data.get('btc_24h_vol', 0)
        if btc_vol > 0.10:  # BTC moving > 10% in 24h
            return False
        
        # Check correlation stability
        correlation_change = market_data.get('avg_correlation_change_7d', 0)
        if abs(correlation_change) > 0.20:  # Correlations breaking down
            return False
        
        # Check VIX-equivalent for crypto (if available)
        dvol = market_data.get('dvol', 0)
        if dvol > 100:  # Implied volatility very high
            return False
        
        return True
```

### 10.3 Risk Scenarios

| Scenario | Impact | Probability | Mitigation |
|----------|:------:|:-----------:|------------|
| Spread diverges further (z > 4) | High | Medium | Stop loss at z=4 |
| Cointegration breaks permanently | Critical | Low | Weekly re-testing, time exits |
| One asset delisted/halted | Critical | Very Low | Max 20% per pair, monitoring |
| Flash crash (one asset) | High | Low | Trailing stop, position limits |
| Correlation regime shift | Medium | Medium | Regime filter, gradual exit |
| Liquidity drought | Medium | Medium | Min liquidity checks, smaller sizes |
| Exchange downtime | Medium | Low | Multi-exchange deployment |
| Funding rate drag (short leg) | Low | High | Include in cost model |

---

## 11. Backtesting and Performance Analysis

### 11.1 Backtest Framework

```python
class PairsTradingBacktester:
    """Backtest the pairs trading strategy on historical data."""
    
    def __init__(self, config: StatArbConfig):
        self.config = config
    
    def run_backtest(self, prices: pd.DataFrame, 
                     pair: Tuple[str, str]) -> dict:
        """
        Full backtest for a single pair.
        
        Returns comprehensive performance metrics.
        """
        asset_x, asset_y = pair
        
        # Split into train/test
        split_idx = int(len(prices) * 0.6)
        train = prices.iloc[:split_idx]
        test = prices.iloc[split_idx:]
        
        # Train: estimate parameters
        hedge_ratio = self.estimate_hedge_ratio(train[asset_x], train[asset_y])
        
        # Test: generate signals and simulate trading
        spread = test[asset_y] - hedge_ratio * test[asset_x]
        z_scores = self.calculate_z_scores(spread)
        
        # Simulate trades
        trades = self.simulate_trades(
            test, asset_x, asset_y, hedge_ratio, z_scores
        )
        
        # Calculate metrics
        return self.calculate_metrics(trades, test)
    
    def simulate_trades(self, prices, asset_x, asset_y, 
                         hedge_ratio, z_scores) -> List[dict]:
        """Simulate trade execution on historical data."""
        trades = []
        position = 0  # -1, 0, +1
        entry_data = None
        
        for i in range(len(z_scores)):
            z = z_scores.iloc[i]
            
            if np.isnan(z):
                continue
            
            # Entry
            if position == 0:
                if z > self.config.entry_z:
                    position = -1
                    entry_data = {
                        'entry_idx': i,
                        'entry_z': z,
                        'entry_price_x': prices[asset_x].iloc[i],
                        'entry_price_y': prices[asset_y].iloc[i],
                        'direction': -1,
                    }
                elif z < -self.config.entry_z:
                    position = 1
                    entry_data = {
                        'entry_idx': i,
                        'entry_z': z,
                        'entry_price_x': prices[asset_x].iloc[i],
                        'entry_price_y': prices[asset_y].iloc[i],
                        'direction': 1,
                    }
            
            # Exit
            elif position != 0 and entry_data is not None:
                should_exit = False
                exit_reason = ""
                
                if position == -1 and z < self.config.exit_z:
                    should_exit = True
                    exit_reason = "mean_reversion"
                elif position == 1 and z > -self.config.exit_z:
                    should_exit = True
                    exit_reason = "mean_reversion"
                elif abs(z) > self.config.stop_loss_z:
                    should_exit = True
                    exit_reason = "stop_loss"
                elif i - entry_data['entry_idx'] > self.config.max_holding_days:
                    should_exit = True
                    exit_reason = "time_exit"
                
                if should_exit:
                    exit_price_x = prices[asset_x].iloc[i]
                    exit_price_y = prices[asset_y].iloc[i]
                    
                    # Calculate P&L
                    if position == -1:  # Short Y, Long X
                        pnl_y = (entry_data['entry_price_y'] - exit_price_y)
                        pnl_x = (exit_price_x - entry_data['entry_price_x'])
                    else:
                        pnl_y = (exit_price_y - entry_data['entry_price_y'])
                        pnl_x = (entry_data['entry_price_x'] - exit_price_x)
                    
                    pnl_pct = (pnl_x / entry_data['entry_price_x'] + 
                              pnl_y / entry_data['entry_price_y']) / 2
                    
                    trades.append({
                        **entry_data,
                        'exit_idx': i,
                        'exit_z': z,
                        'exit_price_x': exit_price_x,
                        'exit_price_y': exit_price_y,
                        'pnl_pct': pnl_pct,
                        'holding_days': i - entry_data['entry_idx'],
                        'exit_reason': exit_reason,
                    })
                    
                    position = 0
                    entry_data = None
        
        return trades
    
    def calculate_metrics(self, trades: List[dict], prices: pd.DataFrame) -> dict:
        """Calculate comprehensive performance metrics."""
        if not trades:
            return {'num_trades': 0}
        
        pnls = [t['pnl_pct'] for t in trades]
        
        return {
            'num_trades': len(trades),
            'win_rate': sum(1 for p in pnls if p > 0) / len(pnls),
            'avg_return_pct': np.mean(pnls) * 100,
            'median_return_pct': np.median(pnls) * 100,
            'total_return_pct': sum(pnls) * 100,
            'max_return_pct': max(pnls) * 100,
            'max_loss_pct': min(pnls) * 100,
            'sharpe_ratio': np.mean(pnls) / np.std(pnls) * np.sqrt(252 / np.mean([t['holding_days'] for t in trades])) if np.std(pnls) > 0 else 0,
            'avg_holding_days': np.mean([t['holding_days'] for t in trades]),
            'profit_factor': abs(sum(p for p in pnls if p > 0) / sum(p for p in pnls if p < 0)) if any(p < 0 for p in pnls) else float('inf'),
            'max_drawdown_pct': self.calculate_max_drawdown(pnls) * 100,
            'exit_reasons': {
                reason: sum(1 for t in trades if t['exit_reason'] == reason)
                for reason in set(t['exit_reason'] for t in trades)
            }
        }
    
    def calculate_max_drawdown(self, pnls: List[float]) -> float:
        """Calculate maximum drawdown from trade P&Ls."""
        cumulative = np.cumsum(pnls)
        peak = np.maximum.accumulate(cumulative)
        drawdown = peak - cumulative
        return np.max(drawdown) if len(drawdown) > 0 else 0
```

### 11.2 Expected Performance Benchmarks

| Metric | Conservative | Moderate | Aggressive |
|--------|:-----------:|:--------:|:----------:|
| Annual Return | 8-15% | 15-30% | 30-60% |
| Sharpe Ratio | 1.5-2.0 | 2.0-3.0 | 2.5-4.0 |
| Win Rate | 60-70% | 55-65% | 50-60% |
| Max Drawdown | 3-5% | 5-10% | 10-20% |
| Avg Holding | 10-20 days | 5-15 days | 3-10 days |
| Trades/Year | 50-100 | 100-300 | 300-1000 |
| Profit Factor | 1.8-2.5 | 1.5-2.0 | 1.3-1.8 |

---

## 12. References

### Academic Papers

1. **Engle, R. F., & Granger, C. W. J.** (1987). "Co-Integration and Error Correction: Representation, Estimation, and Testing." *Econometrica*, 55(2), 251-276.

2. **Johansen, S.** (1991). "Estimation and Hypothesis Testing of Cointegration Vectors in Gaussian Vector Autoregressive Models." *Econometrica*, 59(6), 1551-1580.

3. **Gatev, E., Goetzmann, W. N., & Rouwenhorst, K. G.** (2006). "Pairs Trading: Performance of a Relative-Value Arbitrage Rule." *The Review of Financial Studies*, 19(3), 797-827.

4. **Vidyamurthy, G.** (2004). *Pairs Trading: Quantitative Methods and Analysis*. Wiley.

5. **Avellaneda, M., & Lee, J. H.** (2010). "Statistical Arbitrage in the US Equities Market." *Quantitative Finance*, 10(7), 761-782.

6. **Elliott, R. J., van der Hoek, J., & Malcolm, W. P.** (2005). "Pairs Trading." *Quantitative Finance*, 5(3), 271-276.

7. **Shleifer, A., & Vishny, R. W.** (1997). "The Limits of Arbitrage." *The Journal of Finance*, 52(1), 35-55.

8. **Hurst, H. E.** (1951). "Long-Term Storage Capacity of Reservoirs." *Transactions of the American Society of Civil Engineers*, 116(1), 770-799.

9. **Dickey, D. A., & Fuller, W. A.** (1979). "Distribution of the Estimators for Autoregressive Time Series with a Unit Root." *Journal of the American Statistical Association*, 74(366), 427-431.

10. **Kalman, R. E.** (1960). "A New Approach to Linear Filtering and Prediction Problems." *Journal of Basic Engineering*, 82(1), 35-45.

11. **Kwiatkowski, D., Phillips, P. C. B., Schmidt, P., & Shin, Y.** (1992). "Testing the Null Hypothesis of Stationarity Against the Alternative of a Unit Root." *Journal of Econometrics*, 54(1-3), 159-178. — KPSS test.

### Books

- Vidyamurthy, G. (2004). *Pairs Trading*. Wiley.
- Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley.
- Pole, A. (2007). *Statistical Arbitrage*. Wiley.
- Hamilton, J. D. (1994). *Time Series Analysis*. Princeton University Press.

### Software Libraries

- statsmodels (Python): https://www.statsmodels.org/ — ADF, Johansen, cointegration tests
- scipy.optimize: https://docs.scipy.org/ — Optimization for parameter estimation
- pykalman: https://pykalman.github.io/ — Kalman filter implementation
- arch (Python): https://arch.readthedocs.io/ — ARCH/GARCH models, unit root tests

---

> **Related Documents:**
> - [00_overview.md](./00_overview.md) — Arbitrage Overview
> - [01_triangular_arbitrage.md](./01_triangular_arbitrage.md) — Pure Arbitrage (contrast with statistical)
> - [02_funding_rate_arbitrage.md](./02_funding_rate_arbitrage.md) — Another delta-neutral strategy
