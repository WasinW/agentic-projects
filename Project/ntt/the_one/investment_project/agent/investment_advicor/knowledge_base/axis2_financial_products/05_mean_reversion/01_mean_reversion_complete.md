# Mean Reversion Strategies — Complete Reference

## Document Metadata
| Field | Value |
|---|---|
| Strategy Class | Mean Reversion / Statistical Trading |
| Asset Classes | Forex, Crypto (Spot & Futures) |
| Timeframe | Intraday to Multi-week |
| Complexity | Intermediate to Advanced |
| Capital Requirement | Medium |
| Last Updated | 2026-04-12 |

---

## Table of Contents
1. [Statistical Foundations](#1-statistical-foundations)
2. [Mean Reversion Detection](#2-mean-reversion-detection)
3. [Bollinger Band Mean Reversion](#3-bollinger-band-mean-reversion)
4. [Z-Score Based Entry/Exit](#4-z-score-based-entryexit)
5. [Keltner Channel Strategies](#5-keltner-channel-strategies)
6. [RSI Extreme Mean Reversion](#6-rsi-extreme-mean-reversion)
7. [Half-Life of Mean Reversion](#7-half-life-of-mean-reversion)
8. [Optimal Lookback Period Selection](#8-optimal-lookback-period-selection)
9. [Application to Forex and Crypto](#9-application-to-forex-and-crypto)
10. [Core Logic — Entry/Exit](#10-core-logic--entryexit)
11. [Technical Specifications](#11-technical-specifications)
12. [Mathematical Models](#12-mathematical-models)
13. [Risk Parameters](#13-risk-parameters)
14. [Execution Flow](#14-execution-flow)
15. [Backtesting Methodology](#15-backtesting-methodology)
16. [References](#16-references)

---

## 1. Statistical Foundations

### 1.1 The Ornstein-Uhlenbeck Process

Mean reversion strategies are grounded in the theory that prices (or spreads) tend to revert to a long-run equilibrium level. The canonical continuous-time model for mean-reverting processes is the **Ornstein-Uhlenbeck (OU) process**:

$$dX_t = \theta(\mu - X_t)dt + \sigma dW_t$$

Where:
- $X_t$ = the process value at time $t$ (e.g., price, spread, or log-price)
- $\theta$ = speed of mean reversion (rate at which the process reverts to $\mu$)
- $\mu$ = long-run mean (equilibrium level)
- $\sigma$ = volatility of the process
- $W_t$ = standard Wiener process (Brownian motion)

**Interpretation of Parameters:**

| Parameter | Meaning | Typical Range |
|---|---|---|
| $\theta$ | Mean reversion speed | 0.01 - 10 (higher = faster reversion) |
| $\mu$ | Equilibrium level | Estimated from data |
| $\sigma$ | Noise magnitude | Estimated from data |

**Key Properties of the OU Process:**

1. **Stationary Distribution**: $X_t \sim \mathcal{N}\left(\mu, \frac{\sigma^2}{2\theta}\right)$ as $t \to \infty$
2. **Autocorrelation**: $\text{Corr}(X_t, X_{t+s}) = e^{-\theta s}$
3. **Expected Value**: $E[X_t | X_0] = \mu + (X_0 - \mu)e^{-\theta t}$
4. **Variance**: $\text{Var}(X_t | X_0) = \frac{\sigma^2}{2\theta}(1 - e^{-2\theta t})$

### 1.2 Discrete-Time Approximation

The OU process can be discretized as an AR(1) model:

$$X_t = a + bX_{t-1} + \epsilon_t$$

Where:
- $a = \mu(1 - e^{-\theta\Delta t})$
- $b = e^{-\theta\Delta t}$
- $\epsilon_t \sim \mathcal{N}(0, \frac{\sigma^2}{2\theta}(1 - e^{-2\theta\Delta t}))$

**Parameter Estimation via OLS:**

Regress $X_t$ on $X_{t-1}$:

$$X_t = \hat{a} + \hat{b}X_{t-1} + \hat{\epsilon}_t$$

Then recover OU parameters:
- $\hat{\theta} = -\frac{\ln(\hat{b})}{\Delta t}$
- $\hat{\mu} = \frac{\hat{a}}{1 - \hat{b}}$
- $\hat{\sigma} = \hat{\sigma}_\epsilon \sqrt{\frac{-2\ln(\hat{b})}{\Delta t(1 - \hat{b}^2)}}$

### 1.3 Why Mean Reversion Occurs

| Market | Mean Reversion Driver |
|---|---|
| Forex | Central bank policy anchoring, purchasing power parity, interest rate parity |
| Crypto | Arbitrage across exchanges, funding rate mean reversion, market maker inventory rebalancing |
| Cross-asset | Overreaction/underreaction to news, liquidity provision, behavioral biases |

### 1.4 Mean Reversion vs Random Walk vs Momentum

| Property | Mean Reversion | Random Walk | Momentum |
|---|---|---|---|
| Hurst Exponent $H$ | $H < 0.5$ | $H = 0.5$ | $H > 0.5$ |
| Autocorrelation | Negative | Zero | Positive |
| Variance Ratio | $VR < 1$ | $VR = 1$ | $VR > 1$ |
| ADF Test | Rejects unit root | Fails to reject | Fails to reject |
| Optimal Strategy | Fade extremes | No edge | Follow trend |

---

## 2. Mean Reversion Detection

### 2.1 Hurst Exponent

The Hurst exponent $H$ quantifies the degree of mean reversion or persistence in a time series.

**Definition:**

$$E\left[\frac{R(n)}{S(n)}\right] = C \cdot n^H$$

Where $R(n)/S(n)$ is the rescaled range over $n$ observations.

**Calculation (R/S Method):**

```
Algorithm: Hurst Exponent Estimation

INPUT: price_series of length T

1. Compute log returns: r_t = ln(P_t / P_{t-1})

2. For each sub-period length n in {n_min, ..., n_max}:
    a. Divide series into k = floor(T/n) sub-periods
    b. For each sub-period j:
        - Compute mean: m_j = mean(r in sub-period j)
        - Compute cumulative deviations: Y_t = sum_{i=1}^{t}(r_i - m_j)
        - R_j = max(Y) - min(Y)  (range)
        - S_j = std(r in sub-period j) (standard deviation)
    c. RS(n) = mean(R_j / S_j) over all sub-periods

3. Fit: log(RS(n)) = H * log(n) + C via OLS

4. H = slope of regression

OUTPUT: H (Hurst exponent)
```

**Interpretation:**

| Hurst Range | Behavior | Trading Implication |
|---|---|---|
| $0 < H < 0.5$ | Mean-reverting | Apply mean reversion strategies |
| $H = 0.5$ | Random walk | No statistical edge |
| $0.5 < H < 1$ | Trending/persistent | Apply momentum strategies |

**Practical Thresholds:**
- $H < 0.4$: Strong mean reversion signal
- $0.4 \leq H < 0.5$: Weak mean reversion
- $0.5 \leq H < 0.6$: Weak trend
- $H \geq 0.6$: Strong trend signal

### 2.2 Augmented Dickey-Fuller (ADF) Test

The ADF test checks whether a time series has a unit root (non-stationary) versus being stationary (mean-reverting).

**Test Regression:**

$$\Delta X_t = \alpha + \beta t + \gamma X_{t-1} + \sum_{i=1}^{p} \delta_i \Delta X_{t-i} + \epsilon_t$$

**Hypotheses:**
- $H_0$: $\gamma = 0$ (unit root, non-stationary)
- $H_1$: $\gamma < 0$ (stationary, mean-reverting)

**Test Statistic:**

$$ADF = \frac{\hat{\gamma}}{SE(\hat{\gamma})}$$

Compare with critical values (more negative = stronger rejection of unit root).

| Significance | Critical Value (no trend) |
|---|---|
| 1% | -3.43 |
| 5% | -2.86 |
| 10% | -2.57 |

**Decision Rule:**
- If ADF statistic < critical value: **Reject $H_0$** — series is mean-reverting
- If ADF statistic > critical value: **Fail to reject** — series may have unit root

### 2.3 Variance Ratio Test

The variance ratio test compares the variance of $q$-period returns to the variance of 1-period returns:

$$VR(q) = \frac{\text{Var}(r_t^{(q)})}{q \cdot \text{Var}(r_t^{(1)})}$$

Where $r_t^{(q)} = \ln(P_t/P_{t-q})$.

**Interpretation:**
- $VR(q) < 1$: Mean-reverting
- $VR(q) = 1$: Random walk
- $VR(q) > 1$: Trending

**Lo-MacKinlay Test Statistic:**

$$z(q) = \frac{VR(q) - 1}{\sqrt{\frac{2(2q-1)(q-1)}{3qT}}}$$

Under $H_0$ (random walk), $z(q) \sim \mathcal{N}(0,1)$.

### 2.4 KPSS Test (Complement to ADF)

The KPSS test has opposite null hypothesis to ADF:
- $H_0$: Series is stationary
- $H_1$: Series has unit root

**Best Practice: Use both tests together:**

| ADF Result | KPSS Result | Conclusion |
|---|---|---|
| Reject $H_0$ | Fail to reject $H_0$ | **Mean-reverting** (both agree) |
| Fail to reject $H_0$ | Reject $H_0$ | **Unit root** (both agree) |
| Reject $H_0$ | Reject $H_0$ | Inconclusive |
| Fail to reject $H_0$ | Fail to reject $H_0$ | Inconclusive |

---

## 3. Bollinger Band Mean Reversion

### 3.1 Bollinger Band Construction

**Upper Band:**

$$BB_{upper} = SMA(P, n) + k \times \sigma(P, n)$$

**Lower Band:**

$$BB_{lower} = SMA(P, n) - k \times \sigma(P, n)$$

**Middle Band (Mean):**

$$BB_{mid} = SMA(P, n) = \frac{1}{n}\sum_{i=0}^{n-1} P_{t-i}$$

Where:
- $n$ = lookback period (default: 20)
- $k$ = standard deviation multiplier (default: 2.0)
- $\sigma(P, n)$ = rolling standard deviation of price over $n$ periods

### 3.2 Bollinger Band Width (BBW)

$$BBW = \frac{BB_{upper} - BB_{lower}}{BB_{mid}} = \frac{2k \times \sigma(P, n)}{SMA(P, n)}$$

BBW measures current volatility relative to the mean. Low BBW (squeeze) often precedes breakouts.

### 3.3 %B Indicator

$$\%B = \frac{P - BB_{lower}}{BB_{upper} - BB_{lower}}$$

| %B Value | Position | Interpretation |
|---|---|---|
| > 1.0 | Above upper band | Overbought |
| 0.5 | At middle band | Neutral |
| < 0.0 | Below lower band | Oversold |

### 3.4 Bollinger Band Mean Reversion Strategy

**Entry Rules:**

| Signal | Condition | Action |
|---|---|---|
| Long Entry | $P_t < BB_{lower}$ AND $\%B < 0$ | Buy (fade the sell-off) |
| Short Entry | $P_t > BB_{upper}$ AND $\%B > 1$ | Sell (fade the rally) |
| Confirmation | RSI divergence or volume decrease | Increases conviction |

**Exit Rules:**

| Signal | Condition | Action |
|---|---|---|
| Long Exit (TP) | $P_t \geq BB_{mid}$ | Take profit at mean |
| Short Exit (TP) | $P_t \leq BB_{mid}$ | Take profit at mean |
| Long Exit (SL) | $P_t < BB_{lower} - k_{SL} \times \sigma$ | Stop loss |
| Short Exit (SL) | $P_t > BB_{upper} + k_{SL} \times \sigma$ | Stop loss |

**Enhanced Entry — Bollinger Band Bounce:**

```
LONG ENTRY CONDITIONS (all must be true):
    1. Price touches or closes below lower Bollinger Band (2σ)
    2. Price does NOT close below 3σ band (filter extreme breakdowns)
    3. BBW > minimum_width (avoid squeeze situations)
    4. RSI(14) < 30 (confirming oversold)
    5. No major news event within next 2 hours
    6. Volume on down move is declining (exhaustion)
    
ENTRY: Buy at market or limit at BB_lower
TARGET: BB_mid (middle band)
STOP: BB_lower - 1.0 * ATR(14)
```

### 3.5 Bollinger Band Parameters by Market

| Market | Period ($n$) | Multiplier ($k$) | Timeframe |
|---|---|---|---|
| Forex Major | 20 | 2.0 | H1, H4, D1 |
| Forex Cross | 20 | 2.0-2.5 | H4, D1 |
| BTC/USDT | 20 | 2.0-2.5 | H1, H4 |
| Altcoins | 20 | 2.5-3.0 | H4, D1 |

---

## 4. Z-Score Based Entry/Exit

### 4.1 Z-Score Definition

The z-score normalizes the current price deviation from its moving average:

$$z_t = \frac{P_t - \bar{P}_n}{\sigma_n}$$

Where:
- $\bar{P}_n$ = moving average over $n$ periods
- $\sigma_n$ = standard deviation over $n$ periods

### 4.2 Z-Score Trading Rules

**Standard Thresholds:**

| Z-Score | Signal | Action |
|---|---|---|
| $z > +2.0$ | Overbought | Enter Short |
| $z > +1.0$ | Mildly Overbought | Scale into Short (optional) |
| $-0.5 < z < +0.5$ | Neutral | Close positions |
| $z < -1.0$ | Mildly Oversold | Scale into Long (optional) |
| $z < -2.0$ | Oversold | Enter Long |

**Entry/Exit Signal Generation:**

```
Algorithm: Z-Score Mean Reversion

PARAMETERS:
    lookback = 20           # Rolling window for mean and std
    entry_z = 2.0           # Z-score threshold for entry
    exit_z = 0.0            # Z-score threshold for exit (mean)
    stop_z = 3.5            # Z-score threshold for stop loss
    
EACH BAR:
    1. Calculate rolling statistics:
       mean_n = SMA(close, lookback)
       std_n = rolling_std(close, lookback)
       z = (close - mean_n) / std_n
    
    2. Generate signals:
       IF z < -entry_z AND no_position:
           SIGNAL = LONG
           entry_price = close
           
       IF z > +entry_z AND no_position:
           SIGNAL = SHORT
           entry_price = close
           
       IF position == LONG AND z >= -exit_z:
           SIGNAL = CLOSE_LONG
           
       IF position == SHORT AND z <= +exit_z:
           SIGNAL = CLOSE_SHORT
           
       IF position == LONG AND z < -stop_z:
           SIGNAL = STOP_LONG  # Mean reversion failed
           
       IF position == SHORT AND z > +stop_z:
           SIGNAL = STOP_SHORT  # Mean reversion failed
```

### 4.3 Z-Score Scaling Strategy

Instead of binary entry, scale position size based on z-score magnitude:

$$\text{Position Size} = \text{Base Size} \times \min\left(\frac{|z| - z_{entry}}{z_{max} - z_{entry}}, 1.0\right)$$

| Z-Score | Position % of Max |
|---|---|
| $|z| = 2.0$ | 33% |
| $|z| = 2.5$ | 67% |
| $|z| = 3.0$ | 100% |
| $|z| > 3.5$ | Stop loss (mean reversion failed) |

### 4.4 Z-Score Applied to Spreads (Pairs Trading)

For a spread $S_t = P_{A,t} - \beta P_{B,t}$:

$$z_{spread} = \frac{S_t - \bar{S}_n}{\sigma_{S,n}}$$

This is the foundation of statistical arbitrage (covered in detail in the stat arb document).

---

## 5. Keltner Channel Strategies

### 5.1 Keltner Channel Construction

**Middle Line:**

$$KC_{mid} = EMA(P, n)$$

**Upper Channel:**

$$KC_{upper} = EMA(P, n) + k \times ATR(m)$$

**Lower Channel:**

$$KC_{lower} = EMA(P, n) - k \times ATR(m)$$

Where:
- $EMA(P, n)$ = Exponential Moving Average of price over $n$ periods
- $ATR(m)$ = Average True Range over $m$ periods
- $k$ = multiplier (default: 2.0)

**True Range:**

$$TR = \max(H - L, |H - C_{prev}|, |L - C_{prev}|)$$

$$ATR(m) = \frac{1}{m}\sum_{i=1}^{m} TR_i$$

### 5.2 Keltner vs Bollinger Bands

| Feature | Bollinger Bands | Keltner Channels |
|---|---|---|
| Volatility Measure | Standard deviation | Average True Range |
| Center Line | SMA | EMA |
| Responsiveness | More reactive to price spikes | Smoother, less reactive |
| Band Width | Contracts/expands with vol | More stable width |
| False Signals | More in choppy markets | Fewer, more reliable |
| Best For | Strong mean reversion setups | Trend-filtered mean reversion |

### 5.3 Keltner Channel Mean Reversion Strategy

```
LONG ENTRY:
    1. Price closes below KC_lower (2x ATR)
    2. Price is above KC_lower at 3x ATR (not extreme breakdown)
    3. EMA(20) slope is flat or slightly positive (not strong downtrend)
    4. Volume is declining on the pullback
    
    Entry: Limit order at KC_lower
    Target: KC_mid (EMA)
    Stop: KC_lower - 1.0 * ATR(14)

SHORT ENTRY:
    1. Price closes above KC_upper (2x ATR)
    2. Price is below KC_upper at 3x ATR
    3. EMA(20) slope is flat or slightly negative
    4. Volume is declining on the rally
    
    Entry: Limit order at KC_upper
    Target: KC_mid (EMA)
    Stop: KC_upper + 1.0 * ATR(14)
```

### 5.4 Bollinger-Keltner Squeeze Detection

The **squeeze** occurs when Bollinger Bands are inside Keltner Channels:

$$\text{Squeeze} = (BB_{upper} < KC_{upper}) \text{ AND } (BB_{lower} > KC_{lower})$$

**Strategy Implication:**
- During squeeze: **Avoid mean reversion** (breakout likely)
- After squeeze releases: **Initiate trend-following** positions
- Before squeeze (wide bands): **Mean reversion** is favorable

---

## 6. RSI Extreme Mean Reversion

### 6.1 RSI Calculation

$$RSI = 100 - \frac{100}{1 + RS}$$

$$RS = \frac{\text{Average Gain over } n \text{ periods}}{\text{Average Loss over } n \text{ periods}}$$

Using Wilder's smoothing:

$$\text{Avg Gain}_t = \frac{\text{Avg Gain}_{t-1} \times (n-1) + \text{Gain}_t}{n}$$

### 6.2 RSI Mean Reversion Levels

| RSI Value | Condition | Signal |
|---|---|---|
| RSI < 20 | Extremely Oversold | Strong Long |
| 20 <= RSI < 30 | Oversold | Long |
| 30 <= RSI < 70 | Neutral | No signal |
| 70 <= RSI < 80 | Overbought | Short |
| RSI > 80 | Extremely Overbought | Strong Short |

### 6.3 RSI Divergence Mean Reversion

**Bullish Divergence (Long Signal):**
- Price makes a lower low
- RSI makes a higher low
- Indicates weakening selling pressure; potential mean reversion up

**Bearish Divergence (Short Signal):**
- Price makes a higher high
- RSI makes a lower high
- Indicates weakening buying pressure; potential mean reversion down

**Detection Algorithm:**

```
Algorithm: RSI Divergence Detection

INPUT: price[], rsi[], lookback=20

FOR each bar t:
    # Find recent price swing lows/highs
    price_lows = find_swing_lows(price, lookback)
    price_highs = find_swing_highs(price, lookback)
    rsi_lows = find_swing_lows(rsi, lookback)
    rsi_highs = find_swing_highs(rsi, lookback)
    
    # Bullish divergence
    IF price_lows[-1] < price_lows[-2]:          # Price lower low
        IF rsi_lows[-1] > rsi_lows[-2]:           # RSI higher low
            IF rsi[-1] < 30:                       # In oversold zone
                SIGNAL = BULLISH_DIVERGENCE
    
    # Bearish divergence
    IF price_highs[-1] > price_highs[-2]:         # Price higher high
        IF rsi_highs[-1] < rsi_highs[-2]:          # RSI lower high
            IF rsi[-1] > 70:                        # In overbought zone
                SIGNAL = BEARISH_DIVERGENCE
```

### 6.4 ConnorsRSI (Enhanced RSI for Mean Reversion)

ConnorsRSI combines three components:

$$\text{ConnorsRSI} = \frac{RSI(3) + RSI(\text{streak}, 2) + \text{PercentRank}(100)}{3}$$

Where:
- $RSI(3)$ = 3-period RSI of price
- $RSI(\text{streak}, 2)$ = 2-period RSI of the up/down streak length
- $\text{PercentRank}(100)$ = percentile rank of today's return over last 100 bars

**Trading Rules:**
- Buy when ConnorsRSI < 10
- Sell when ConnorsRSI > 90
- Exit at ConnorsRSI crossing 50

---

## 7. Half-Life of Mean Reversion

### 7.1 Definition and Formula

The half-life of mean reversion is the expected time for the process to revert halfway to the mean from its current level.

From the discrete AR(1) model $X_t = a + \phi X_{t-1} + \epsilon_t$:

$$t_{half} = -\frac{\ln(2)}{\ln(\phi)}$$

Where $\phi = e^{-\theta \Delta t}$ is the AR(1) coefficient.

Equivalently, in terms of the OU speed parameter $\theta$:

$$t_{half} = \frac{\ln(2)}{\theta}$$

### 7.2 Estimation Procedure

```
Algorithm: Half-Life Estimation

INPUT: price_series P[] of length T

1. Compute log prices: x = ln(P)

2. Compute first differences: dx = x[1:] - x[:-1]

3. Compute lagged levels: x_lag = x[:-1]

4. Run OLS regression: dx = alpha + beta * x_lag + epsilon
   (This is the Dickey-Fuller regression)

5. Extract coefficient: phi = 1 + beta
   (Note: beta should be negative for mean reversion)

6. Compute half-life:
   IF beta < 0:
       half_life = -ln(2) / ln(1 + beta)
       # Equivalently: half_life = -ln(2) / beta (approximation for small beta)
   ELSE:
       half_life = infinity  # Not mean-reverting

OUTPUT: half_life (in units of the data frequency)
```

### 7.3 Interpreting Half-Life

| Half-Life | Interpretation | Trading Approach |
|---|---|---|
| 1-5 bars | Very fast mean reversion | High-frequency, tight stops |
| 5-20 bars | Moderate mean reversion | Standard mean reversion |
| 20-50 bars | Slow mean reversion | Longer holding periods |
| 50-100 bars | Very slow | May not be tradeable (costs erode edge) |
| > 100 bars or $\infty$ | No mean reversion | Avoid mean reversion strategies |

### 7.4 Using Half-Life for Parameter Selection

The half-life directly informs:

1. **Lookback period for statistics**: Use $n \approx 2 \times t_{half}$ to $4 \times t_{half}$
2. **Expected holding period**: Average trade duration $\approx t_{half}$
3. **Stop-loss timing**: If position hasn't reverted within $3 \times t_{half}$, mean reversion thesis may be broken
4. **Profit target**: Set target to capture reversion within $1 \times t_{half}$

### 7.5 Rolling Half-Life

Compute half-life on a rolling window to detect regime changes:

$$t_{half,rolling}(w) = -\frac{\ln(2)}{\hat{\beta}_w}$$

Where $\hat{\beta}_w$ is estimated from the most recent $w$ observations.

**Regime Detection:**
- If $t_{half}$ is increasing: Mean reversion weakening (possible transition to trending)
- If $t_{half}$ is decreasing: Mean reversion strengthening (favorable for strategy)
- If $t_{half}$ becomes undefined ($\beta > 0$): Trending regime, disable mean reversion

---

## 8. Optimal Lookback Period Selection

### 8.1 The Lookback Dilemma

- **Too short**: Noisy estimates, frequent false signals
- **Too long**: Slow to adapt to changing market conditions, includes irrelevant data

### 8.2 Methods for Selecting Lookback Period

**Method 1: Half-Life Based**

$$n_{optimal} = \text{round}(2 \times t_{half})$$

Rationale: The lookback should capture at least one full mean-reversion cycle.

**Method 2: Information Criterion (AIC/BIC)**

For each candidate lookback $n$:

$$AIC(n) = 2k - 2\ln(\hat{L}_n)$$

$$BIC(n) = k\ln(T) - 2\ln(\hat{L}_n)$$

Where $k$ is the number of parameters and $\hat{L}_n$ is the maximized likelihood.

Select $n$ that minimizes AIC or BIC.

**Method 3: Rolling Walk-Forward Optimization**

```
Algorithm: Walk-Forward Lookback Selection

INPUT: price_data, candidate_lookbacks = [10, 15, 20, 30, 50, 75, 100]

FOR each lookback n in candidate_lookbacks:
    FOR each walk-forward window w:
        training_data = price_data[w - train_size : w]
        test_data = price_data[w : w + test_size]
        
        # Fit mean reversion model on training
        model = fit_mean_reversion(training_data, lookback=n)
        
        # Test on out-of-sample
        sharpe = backtest_mean_reversion(model, test_data)
        record(n, w, sharpe)

# Select lookback with best average out-of-sample Sharpe
optimal_n = argmax_n(mean_sharpe(n))

OUTPUT: optimal_n
```

**Method 4: Entropy-Based Selection**

Select $n$ that maximizes the predictability (minimum entropy) of the z-score:

$$H(z, n) = -\sum_i p(z_i; n) \ln(p(z_i; n))$$

$$n_{optimal} = \arg\min_n H(z, n)$$

### 8.3 Recommended Lookback by Asset and Timeframe

| Asset Class | Timeframe | Recommended Lookback | Rationale |
|---|---|---|---|
| Forex Major | H1 | 20-50 bars | ~1-2 trading days |
| Forex Major | H4 | 20-30 bars | ~3-5 trading days |
| Forex Major | D1 | 15-25 bars | ~3-5 weeks |
| BTC/USDT | H1 | 15-30 bars | Higher vol, faster cycles |
| BTC/USDT | H4 | 20-40 bars | 3-7 days |
| Altcoins | H1 | 10-20 bars | Very fast mean reversion cycles |
| Altcoins | H4 | 15-30 bars | 2-5 days |

---

## 9. Application to Forex and Crypto

### 9.1 Forex Mean Reversion

**Best Currency Pairs for Mean Reversion:**

| Pair | Hurst Exponent (Typical) | Half-Life (H4) | Suitability |
|---|---|---|---|
| EUR/CHF | 0.35-0.42 | 8-15 bars | Excellent |
| EUR/GBP | 0.38-0.45 | 10-20 bars | Very Good |
| AUD/NZD | 0.36-0.43 | 8-18 bars | Very Good |
| USD/CAD | 0.40-0.48 | 12-25 bars | Good |
| EUR/USD | 0.42-0.52 | 15-30 bars | Moderate (regime-dependent) |
| GBP/JPY | 0.50-0.60 | 25-50+ bars | Poor (trending tendency) |

**Why These Pairs Mean-Revert:**
- **EUR/CHF**: Swiss National Bank floor/ceiling interventions historically; economic ties
- **EUR/GBP**: Close economic integration, correlated monetary policies
- **AUD/NZD**: Similar commodity-exporting economies, correlated fundamentals

**Forex Mean Reversion Setup (EUR/CHF, H4):**

```yaml
strategy: "EUR/CHF Bollinger Mean Reversion"
pair: EUR/CHF
timeframe: H4
parameters:
  bb_period: 20
  bb_std: 2.0
  rsi_period: 14
  rsi_oversold: 25
  rsi_overbought: 75
  lookback: 20
  
entry_long:
  - Close < BB_lower
  - RSI(14) < 25
  - Spread < 2.0 pips
  - Not within 1 hour of major CHF news
  
entry_short:
  - Close > BB_upper
  - RSI(14) > 75
  - Spread < 2.0 pips
  - Not within 1 hour of major EUR/CHF news
  
exit:
  target: BB_mid
  stop: 1.5 * ATR(14) beyond entry
  time_stop: 3 * half_life bars (~60 H4 bars = 10 days)
  
risk:
  risk_per_trade: 1%
  max_concurrent: 3
  max_daily_loss: 3%
```

### 9.2 Crypto Mean Reversion

**Crypto-Specific Considerations:**

1. **24/7 Markets**: No overnight gaps, continuous mean reversion opportunities
2. **Higher Volatility**: Wider bands required; larger profit potential per trade
3. **Funding Rate Mean Reversion**: Perpetual futures funding rates revert to zero
4. **Exchange-Specific Pricing**: Spread between exchanges mean-reverts (cross-exchange arb)
5. **On-Chain Metrics**: NVT ratio, MVRV z-score as mean reversion signals

**Funding Rate Mean Reversion:**

The funding rate on perpetual futures tends to mean-revert around zero:

$$\text{Funding Rate} = \text{Premium Index} + \text{clamp}(\text{Interest Rate} - \text{Premium Index}, -0.05\%, +0.05\%)$$

**Strategy:**
- When funding rate is extremely positive (> 0.1%): Long spot, short perp (collect funding)
- When funding rate is extremely negative (< -0.1%): Short spot, long perp (collect funding)
- Exit when funding rate normalizes near zero

**Crypto Mean Reversion Setup (BTC/USDT, H1):**

```yaml
strategy: "BTC Z-Score Mean Reversion"
pair: BTC/USDT
timeframe: H1
parameters:
  z_lookback: 24  # 24-hour rolling window
  z_entry: 2.0
  z_exit: 0.0
  z_stop: 3.5
  rsi_period: 14
  volume_confirmation: true
  
entry_long:
  - Z-score < -2.0
  - RSI(14) < 30
  - Volume declining on last 3 candles
  - No scheduled major news (FOMC, CPI)
  - Funding rate not extremely negative (>-0.05%)
  
entry_short:
  - Z-score > 2.0
  - RSI(14) > 70
  - Volume declining on last 3 candles
  - Funding rate not extremely positive (<0.05%)
  
exit:
  target: Z-score crosses 0 (mean)
  stop: Z-score exceeds 3.5 (mean reversion failure)
  time_stop: 48 hours (2 * half_life)
  trailing_stop: activate at 50% of profit, trail at 1.0 * ATR
  
risk:
  risk_per_trade: 1.5%
  max_concurrent: 2
  max_daily_loss: 4%
  position_size: ATR-based
```

### 9.3 Multi-Timeframe Mean Reversion

```
MULTI-TIMEFRAME FILTER:

Higher Timeframe (D1):
    - Determine if asset is in a range (sideways regime)
    - BBW < threshold = range-bound → enable mean reversion
    - ADX < 25 = no strong trend → enable mean reversion
    
Medium Timeframe (H4):
    - Calculate Hurst exponent (rolling 100 bars)
    - If H < 0.45 → mean-reverting regime confirmed
    - Calculate half-life for parameter calibration
    
Lower Timeframe (H1):
    - Execute mean reversion signals
    - Use Z-score, Bollinger Band, or RSI triggers
    - Apply tighter stops and targets

COMBINED SIGNAL:
    IF D1_range AND H4_mean_reverting AND H1_signal:
        EXECUTE with full position size
    ELIF H4_mean_reverting AND H1_signal:
        EXECUTE with 50% position size (no D1 confirmation)
    ELSE:
        NO TRADE
```

---

## 10. Core Logic — Entry/Exit

### 10.1 Universal Mean Reversion Entry Logic

```
Algorithm: Composite Mean Reversion Entry

INPUT:
    price_data: OHLCV data
    config: strategy parameters
    
INDICATORS:
    z_score = (close - SMA(close, lookback)) / STD(close, lookback)
    bb_upper = SMA(close, bb_period) + bb_std * STD(close, bb_period)
    bb_lower = SMA(close, bb_period) - bb_std * STD(close, bb_period)
    bb_mid = SMA(close, bb_period)
    rsi = RSI(close, rsi_period)
    kc_upper = EMA(close, kc_period) + kc_mult * ATR(atr_period)
    kc_lower = EMA(close, kc_period) - kc_mult * ATR(atr_period)
    adf_pvalue = adf_test(close[-lookback:])
    hurst = hurst_exponent(close[-100:])
    half_life = calc_half_life(close[-lookback:])

REGIME FILTER:
    is_mean_reverting = (hurst < 0.45) AND (adf_pvalue < 0.05)
    is_range_bound = ADX(14) < 25
    regime_ok = is_mean_reverting AND is_range_bound

LONG ENTRY (all conditions):
    1. regime_ok = True
    2. z_score < -entry_threshold (e.g., -2.0)
    3. close < bb_lower
    4. rsi < rsi_oversold (e.g., 30)
    5. NOT in_squeeze (BB inside KC)
    6. volume_declining (last 3 bars)
    7. half_life < max_half_life (e.g., 50)
    
    ENTRY_PRICE = close (or limit at bb_lower)
    STOP_LOSS = close - sl_multiplier * ATR(14)
    TAKE_PROFIT = bb_mid
    POSITION_SIZE = risk_per_trade * account / (close - stop_loss)

SHORT ENTRY (all conditions):
    1. regime_ok = True
    2. z_score > +entry_threshold
    3. close > bb_upper
    4. rsi > rsi_overbought (e.g., 70)
    5. NOT in_squeeze
    6. volume_declining
    7. half_life < max_half_life
    
    ENTRY_PRICE = close (or limit at bb_upper)
    STOP_LOSS = close + sl_multiplier * ATR(14)
    TAKE_PROFIT = bb_mid
    POSITION_SIZE = risk_per_trade * account / (stop_loss - close)
```

### 10.2 Exit Logic

```
Algorithm: Mean Reversion Exit Management

ON EACH BAR (while position is open):

    # Update indicators
    z_score = current z-score
    bars_held = current_bar - entry_bar
    current_pnl = (close - entry_price) * position_direction * quantity
    
    # 1. Target Hit
    IF position == LONG AND close >= take_profit:
        EXIT at take_profit
        Reason: "Target reached (mean reversion complete)"
        
    IF position == SHORT AND close <= take_profit:
        EXIT at take_profit
        Reason: "Target reached (mean reversion complete)"
    
    # 2. Stop Loss Hit
    IF position == LONG AND close <= stop_loss:
        EXIT at market
        Reason: "Stop loss hit (mean reversion failed)"
        
    IF position == SHORT AND close >= stop_loss:
        EXIT at market
        Reason: "Stop loss hit (mean reversion failed)"
    
    # 3. Mean Reversion Failure (Z-Score Expansion)
    IF position == LONG AND z_score < -stop_z_threshold:
        EXIT at market
        Reason: "Z-score expanded beyond failure threshold"
        
    IF position == SHORT AND z_score > +stop_z_threshold:
        EXIT at market
        Reason: "Z-score expanded beyond failure threshold"
    
    # 4. Time Stop
    IF bars_held > max_holding_period:
        EXIT at market
        Reason: "Maximum holding period exceeded"
        # max_holding_period = 3 * half_life
    
    # 5. Regime Change
    IF NOT regime_ok:  # Hurst crossed above 0.5, or ADX > 30
        EXIT at market
        Reason: "Regime changed to trending — mean reversion disabled"
    
    # 6. Trailing Stop (optional, after 50% profit captured)
    IF current_pnl > 0.5 * (take_profit - entry_price) * quantity:
        trailing_stop = entry_price + 0.3 * (close - entry_price)
        IF position == LONG AND close < trailing_stop:
            EXIT at market
            Reason: "Trailing stop hit"
```

---

## 11. Technical Specifications

### 11.1 Indicator Configuration

```yaml
mean_reversion_indicators:
  bollinger_bands:
    period: 20
    std_dev: 2.0
    source: close
    
  z_score:
    lookback: 20  # calibrated to half-life
    source: close
    
  rsi:
    period: 14
    overbought: 70
    oversold: 30
    
  keltner_channel:
    ema_period: 20
    atr_period: 14
    multiplier: 2.0
    
  adf_test:
    lookback: 100
    significance: 0.05
    
  hurst_exponent:
    lookback: 100
    min_lag: 10
    max_lag: 50
    
  half_life:
    lookback: 100
    recalculation_frequency: 20  # Recalc every 20 bars
```

### 11.2 Signal Strength Scoring

```yaml
signal_scoring:
  components:
    z_score_signal:
      weight: 0.30
      score: min(1.0, (|z| - entry_z) / (stop_z - entry_z))
      
    rsi_signal:
      weight: 0.20
      score:
        long: (30 - RSI) / 30 if RSI < 30 else 0
        short: (RSI - 70) / 30 if RSI > 70 else 0
        
    bollinger_signal:
      weight: 0.20
      score:
        long: max(0, -percent_b)  # How far below lower band
        short: max(0, percent_b - 1)  # How far above upper band
        
    volume_signal:
      weight: 0.15
      score: 1.0 if volume_declining else 0.5 if volume_neutral else 0.0
      
    regime_signal:
      weight: 0.15
      score: (0.5 - hurst) / 0.5  # Stronger signal for lower Hurst
      
  total_score: sum(weight_i * score_i)
  minimum_score_to_trade: 0.60
  full_position_score: 0.80
  
  position_scaling:
    IF total_score >= 0.80: position_pct = 100%
    ELIF total_score >= 0.70: position_pct = 75%
    ELIF total_score >= 0.60: position_pct = 50%
    ELSE: no_trade
```

### 11.3 Filter Configuration

```yaml
filters:
  regime_filter:
    adx_max: 25           # No strong trend
    hurst_max: 0.48        # Mean-reverting
    adf_pvalue_max: 0.05   # Statistically significant stationarity
    
  volatility_filter:
    bbw_min: 0.005         # Minimum BB width (avoid dead markets)
    bbw_max: 0.10          # Maximum BB width (avoid crisis vol)
    atr_percentile_min: 20 # Above 20th percentile of ATR
    atr_percentile_max: 90 # Below 90th percentile of ATR
    
  time_filter:
    forex_active_sessions: ["london", "new_york", "london_ny_overlap"]
    crypto: "24/7"  # No time filter for crypto
    avoid_news_window_minutes: 30  # Before/after major news
    
  spread_filter:
    max_spread_pct: 0.05%  # For forex
    max_spread_pct_crypto: 0.10%
```

---

## 12. Mathematical Models

### 12.1 Ornstein-Uhlenbeck Expected Profit

Given an OU process with parameters $(\theta, \mu, \sigma)$, the expected profit from a mean reversion trade entered at $X_0$ with target $\mu$:

**Expected Time to Mean:**

$$E[\tau_{mean}] = \frac{1}{\theta}\ln\left(\frac{|X_0 - \mu|}{\delta}\right)$$

Where $\delta$ is a small threshold around $\mu$.

**Expected Profit (Long from Oversold):**

$$E[\text{Profit}] = (X_0 - \mu) \times Q \times P(\text{reversion before stop})$$

**Probability of Reversion Before Stop:**

For an OU process starting at $X_0 < \mu$ with stop at $X_s < X_0$:

$$P(\text{reversion}) = \frac{\Phi\left(\frac{X_0 - X_s}{\sigma/\sqrt{2\theta}}\right)}{\Phi\left(\frac{\mu - X_s}{\sigma/\sqrt{2\theta}}\right)}$$

Where $\Phi$ is the standard normal CDF.

### 12.2 Optimal Entry Threshold

The optimal z-score entry threshold balances:
- Higher threshold → fewer trades but higher win rate
- Lower threshold → more trades but lower win rate

**Expected Sharpe Ratio as a function of entry threshold $z_e$:**

$$SR(z_e) = \frac{E[R | |z| > z_e] \times E[N_{trades}(z_e)]}{\sigma[R | |z| > z_e] \times \sqrt{E[N_{trades}(z_e)]}}$$

**Analytical Approximation (assuming normal z-score distribution):**

$$SR(z_e) \approx \frac{z_e \times (1 - \Phi(z_e))}{\sqrt{\Phi(z_e)(1-\Phi(z_e))}}$$

Maximum Sharpe is typically achieved at $z_e \approx 1.5$ to $2.5$ depending on the specific asset's mean reversion characteristics.

### 12.3 Kelly Criterion for Mean Reversion

**Optimal fraction of capital to risk:**

$$f^* = \frac{p \times b - q}{b}$$

Where:
- $p$ = probability of winning (mean reversion completing)
- $q = 1 - p$ = probability of losing (stop hit)
- $b$ = win/loss ratio (reward/risk)

**For typical mean reversion parameters:**
- $p \approx 0.60-0.70$ (based on historical backtest)
- $b \approx 1.0-1.5$ (target at mean, stop at $k \times$ ATR)

$$f^* = \frac{0.65 \times 1.2 - 0.35}{1.2} = \frac{0.78 - 0.35}{1.2} = 0.358$$

**Half-Kelly (recommended):** $f = 0.179$ or ~18% of capital per trade.

### 12.4 Covariance-Based Position Sizing

For a portfolio of mean reversion trades:

$$w = \Sigma^{-1} \alpha$$

Where:
- $w$ = vector of position weights
- $\Sigma$ = covariance matrix of the mean reversion signals
- $\alpha$ = vector of expected returns per signal

This ensures diversification across correlated mean reversion trades.

---

## 13. Risk Parameters

### 13.1 Position Sizing

**ATR-Based Position Size:**

$$\text{Position Size} = \frac{\text{Account} \times \text{Risk\%}}{ATR(14) \times k_{SL}}$$

Where $k_{SL}$ is the ATR multiplier for the stop loss (typically 1.5-2.5).

| Risk Level | Risk per Trade | Max Concurrent | Max Portfolio Risk |
|---|---|---|---|
| Conservative | 0.5% | 3 | 1.5% |
| Moderate | 1.0% | 4 | 4.0% |
| Aggressive | 2.0% | 5 | 10.0% |

### 13.2 Stop Loss Parameters

| Stop Type | Formula | Typical Value |
|---|---|---|
| ATR-Based | Entry $\pm k \times ATR(14)$ | $k = 1.5$ to $2.5$ |
| Z-Score Based | Z-score exceeds $\pm z_{stop}$ | $z_{stop} = 3.0$ to $4.0$ |
| Percentage | Entry $\pm p\%$ | $p = 1.5\%$ to $3.0\%$ |
| Time Stop | Exit after $n$ bars | $n = 3 \times t_{half}$ |
| Volatility Adjusted | Entry $\pm k \times \sigma_{realized}$ | $k = 3.0$ |

### 13.3 Take Profit Parameters

| Target Type | Formula | Notes |
|---|---|---|
| Mean Target | $BB_{mid}$ or $SMA(n)$ | Most common for pure mean reversion |
| Partial Mean | Entry + $0.5 \times (Mean - Entry)$ | Conservative; take half at 50% reversion |
| Opposite Band | $BB_{upper}$ (for longs) | Aggressive; wait for full oscillation |
| Z-Score Target | $z = 0$ (or $z = -0.5$ for conservative) | Normalize to z-score = 0 |
| R-Multiple | Entry + $R \times (Entry - Stop)$ | Typical $R = 1.5$ to $2.0$ |

### 13.4 Risk-Reward Analysis

| Scenario | Win Rate | Avg Win | Avg Loss | R:R | Expected Value |
|---|---|---|---|---|---|
| Conservative (exit at mean) | 65% | 1.0R | 1.0R | 1:1 | +0.30R per trade |
| Moderate (exit at mean + trail) | 55% | 1.5R | 1.0R | 1.5:1 | +0.38R per trade |
| Aggressive (exit at opposite band) | 40% | 2.5R | 1.0R | 2.5:1 | +0.40R per trade |

### 13.5 Maximum Drawdown Budget

$$DD_{max} = 1 - (1 - R_{loss})^{n_{consecutive}}$$

For $R_{loss}$ = 1% risk per trade and $n_{consecutive}$ = 8 consecutive losses:

$$DD_{max} = 1 - (1 - 0.01)^{8} = 1 - 0.9227 = 7.73\%$$

**Maximum consecutive losses to expect (95% confidence):**

$$n_{max} \approx \frac{\ln(0.05)}{\ln(1-p)} \approx \frac{3.0}{\ln(1/0.35)} \approx 2.86/1.05 \approx 6-8$$

For a 65% win rate strategy.

---

## 14. Execution Flow

### 14.1 Complete Mean Reversion System — Pseudocode

```python
class MeanReversionSystem:
    """
    Complete Mean Reversion Trading System
    Supports: Bollinger, Z-Score, Keltner, RSI strategies
    Markets: Forex, Crypto
    """
    
    def __init__(self, config):
        self.lookback = config['lookback']
        self.bb_period = config['bb_period']
        self.bb_std = config['bb_std']
        self.rsi_period = config['rsi_period']
        self.entry_z = config['entry_z']
        self.exit_z = config['exit_z']
        self.stop_z = config['stop_z']
        self.risk_per_trade = config['risk_per_trade']
        self.max_concurrent = config['max_concurrent']
        self.max_holding_bars = config['max_holding_bars']
        
        self.positions = []
        self.trade_log = []
        
    def calculate_indicators(self, data):
        """Step 1: Calculate all mean reversion indicators."""
        close = data['close']
        
        indicators = {}
        
        # Bollinger Bands
        indicators['bb_mid'] = SMA(close, self.bb_period)
        indicators['bb_std'] = rolling_std(close, self.bb_period)
        indicators['bb_upper'] = indicators['bb_mid'] + self.bb_std * indicators['bb_std']
        indicators['bb_lower'] = indicators['bb_mid'] - self.bb_std * indicators['bb_std']
        indicators['percent_b'] = (close - indicators['bb_lower']) / (indicators['bb_upper'] - indicators['bb_lower'])
        
        # Z-Score
        indicators['z_score'] = (close - SMA(close, self.lookback)) / rolling_std(close, self.lookback)
        
        # RSI
        indicators['rsi'] = RSI(close, self.rsi_period)
        
        # Keltner Channels
        indicators['kc_mid'] = EMA(close, 20)
        atr = ATR(data['high'], data['low'], close, 14)
        indicators['kc_upper'] = indicators['kc_mid'] + 2.0 * atr
        indicators['kc_lower'] = indicators['kc_mid'] - 2.0 * atr
        indicators['atr'] = atr
        
        # Squeeze detection
        indicators['squeeze'] = (indicators['bb_upper'] < indicators['kc_upper']) & \
                                (indicators['bb_lower'] > indicators['kc_lower'])
        
        # ADX for regime
        indicators['adx'] = ADX(data['high'], data['low'], close, 14)
        
        return indicators
    
    def check_regime(self, data):
        """Step 2: Determine if mean reversion is appropriate."""
        close = data['close'][-100:]
        
        # Hurst exponent
        hurst = calculate_hurst(close)
        
        # ADF test
        adf_stat, adf_pvalue = adf_test(close)
        
        # Half-life
        half_life = calculate_half_life(close)
        
        # ADX
        adx = self.indicators['adx'][-1]
        
        regime = {
            'hurst': hurst,
            'adf_pvalue': adf_pvalue,
            'half_life': half_life,
            'adx': adx,
            'is_mean_reverting': hurst < 0.48 and adf_pvalue < 0.05,
            'is_range_bound': adx < 25,
            'regime_ok': (hurst < 0.48) and (adf_pvalue < 0.05) and (adx < 25)
        }
        
        return regime
    
    def generate_signal(self, indicators, regime):
        """Step 3: Generate trading signals."""
        if not regime['regime_ok']:
            return None
            
        if indicators['squeeze'][-1]:
            return None  # Avoid trading during squeeze
        
        z = indicators['z_score'][-1]
        rsi = indicators['rsi'][-1]
        close = indicators['close'][-1]
        bb_lower = indicators['bb_lower'][-1]
        bb_upper = indicators['bb_upper'][-1]
        
        # Score the signal
        score = 0.0
        
        # LONG SIGNAL
        if z < -self.entry_z:
            score += 0.30 * min(1.0, (abs(z) - self.entry_z) / (self.stop_z - self.entry_z))
            
            if rsi < 30:
                score += 0.20 * (30 - rsi) / 30
                
            if close < bb_lower:
                score += 0.20
                
            if self.volume_declining(indicators):
                score += 0.15
                
            score += 0.15 * (0.5 - regime['hurst']) / 0.5
            
            if score >= 0.60:
                return {
                    'direction': 'LONG',
                    'score': score,
                    'entry': close,
                    'target': indicators['bb_mid'][-1],
                    'stop': close - 2.0 * indicators['atr'][-1],
                    'half_life': regime['half_life']
                }
        
        # SHORT SIGNAL
        if z > self.entry_z:
            score += 0.30 * min(1.0, (abs(z) - self.entry_z) / (self.stop_z - self.entry_z))
            
            if rsi > 70:
                score += 0.20 * (rsi - 70) / 30
                
            if close > bb_upper:
                score += 0.20
                
            if self.volume_declining(indicators):
                score += 0.15
                
            score += 0.15 * (0.5 - regime['hurst']) / 0.5
            
            if score >= 0.60:
                return {
                    'direction': 'SHORT',
                    'score': score,
                    'entry': close,
                    'target': indicators['bb_mid'][-1],
                    'stop': close + 2.0 * indicators['atr'][-1],
                    'half_life': regime['half_life']
                }
        
        return None
    
    def calculate_position_size(self, signal, account_balance):
        """Step 4: Determine position size based on risk."""
        risk_amount = account_balance * self.risk_per_trade
        stop_distance = abs(signal['entry'] - signal['stop'])
        
        if stop_distance == 0:
            return 0
            
        position_size = risk_amount / stop_distance
        
        # Scale by signal score
        if signal['score'] >= 0.80:
            size_multiplier = 1.0
        elif signal['score'] >= 0.70:
            size_multiplier = 0.75
        else:
            size_multiplier = 0.50
            
        return position_size * size_multiplier
    
    def manage_position(self, position, current_bar, indicators):
        """Step 5: Manage open positions."""
        z = indicators['z_score'][-1]
        close = indicators['close'][-1]
        bars_held = current_bar - position['entry_bar']
        
        # Check exit conditions in priority order
        
        # 1. Stop loss
        if position['direction'] == 'LONG' and close <= position['stop']:
            return 'EXIT', 'Stop loss hit'
        if position['direction'] == 'SHORT' and close >= position['stop']:
            return 'EXIT', 'Stop loss hit'
        
        # 2. Take profit
        if position['direction'] == 'LONG' and close >= position['target']:
            return 'EXIT', 'Target reached'
        if position['direction'] == 'SHORT' and close <= position['target']:
            return 'EXIT', 'Target reached'
        
        # 3. Z-score failure
        if position['direction'] == 'LONG' and z < -self.stop_z:
            return 'EXIT', 'Z-score failure'
        if position['direction'] == 'SHORT' and z > self.stop_z:
            return 'EXIT', 'Z-score failure'
        
        # 4. Time stop
        if bars_held > 3 * position['half_life']:
            return 'EXIT', 'Time stop'
        
        # 5. Regime change
        regime = self.check_regime(indicators['data'])
        if not regime['regime_ok']:
            return 'EXIT', 'Regime change'
        
        # 6. Trailing stop (after 50% profit)
        entry = position['entry']
        target = position['target']
        profit_pct = (close - entry) / (target - entry) if position['direction'] == 'LONG' \
                     else (entry - close) / (entry - target)
        
        if profit_pct > 0.5:
            trail_level = entry + 0.3 * (close - entry) if position['direction'] == 'LONG' \
                         else entry - 0.3 * (entry - close)
            if position['direction'] == 'LONG' and close < trail_level:
                return 'EXIT', 'Trailing stop'
            if position['direction'] == 'SHORT' and close > trail_level:
                return 'EXIT', 'Trailing stop'
        
        return 'HOLD', None
    
    def run(self, data_stream):
        """Step 6: Main execution loop."""
        for bar in data_stream:
            # Calculate indicators
            indicators = self.calculate_indicators(bar.history)
            
            # Check regime
            regime = self.check_regime(bar.history)
            
            # Manage existing positions
            for pos in self.positions[:]:
                action, reason = self.manage_position(pos, bar.index, indicators)
                if action == 'EXIT':
                    self.close_position(pos, bar.close, reason)
                    self.positions.remove(pos)
            
            # Generate new signals if capacity available
            if len(self.positions) < self.max_concurrent:
                signal = self.generate_signal(indicators, regime)
                if signal:
                    size = self.calculate_position_size(signal, self.account_balance)
                    if size > 0:
                        self.open_position(signal, size, bar.index)
            
            # Log status
            self.log_status(bar, indicators, regime)
```

### 14.2 Execution Flow Diagram

```
┌─────────────────────────────────────────────┐
│       MEAN REVERSION EXECUTION FLOW         │
├─────────────────────────────────────────────┤
│                                             │
│  1. DATA INGESTION                          │
│     ├─ Receive new bar (OHLCV)              │
│     └─ Update price history buffer          │
│                                             │
│  2. INDICATOR CALCULATION                   │
│     ├─ Bollinger Bands (20, 2.0)            │
│     ├─ Z-Score (rolling lookback)           │
│     ├─ RSI (14)                             │
│     ├─ Keltner Channels (20, 2.0)           │
│     ├─ ATR (14)                             │
│     └─ ADX (14)                             │
│                                             │
│  3. REGIME DETECTION                        │
│     ├─ Hurst Exponent (< 0.48?)             │
│     ├─ ADF Test (p < 0.05?)                 │
│     ├─ Half-Life (reasonable?)              │
│     ├─ ADX (< 25? range-bound)             │
│     └─ Squeeze Detection                    │
│     IF regime NOT ok → Skip to step 5       │
│                                             │
│  4. SIGNAL GENERATION                       │
│     ├─ Check Z-score extremes               │
│     ├─ Check BB touches                     │
│     ├─ Check RSI extremes                   │
│     ├─ Check volume pattern                 │
│     ├─ Score composite signal               │
│     └─ IF score >= 0.60 → Generate signal   │
│                                             │
│  5. POSITION MANAGEMENT                     │
│     ├─ Check stop loss (ATR-based)          │
│     ├─ Check take profit (BB mid)           │
│     ├─ Check z-score failure                │
│     ├─ Check time stop (3x half-life)       │
│     ├─ Check regime change                  │
│     └─ Check trailing stop                  │
│                                             │
│  6. EXECUTION                               │
│     ├─ Size position (risk-based)           │
│     ├─ Place orders (limit or market)       │
│     └─ Update tracking and logs             │
│                                             │
│  7. LOGGING & MONITORING                    │
│     ├─ Record trade in journal              │
│     ├─ Update P&L tracker                   │
│     ├─ Monitor regime metrics               │
│     └─ Alert on anomalies                   │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 15. Backtesting Methodology

### 15.1 Backtesting Protocol

```
1. DATA PREPARATION:
    - Minimum 2 years of clean OHLCV data
    - Split: 60% training / 20% validation / 20% test
    - Ensure no look-ahead bias in indicator calculations
    
2. PARAMETER OPTIMIZATION (Training Set):
    - Grid search or Bayesian optimization over:
      - Lookback period: [10, 15, 20, 30, 50]
      - Entry z-score: [1.5, 2.0, 2.5, 3.0]
      - Stop z-score: [3.0, 3.5, 4.0]
      - BB period: [15, 20, 30]
      - BB std: [1.5, 2.0, 2.5]
    - Optimize for: Sharpe ratio (primary), max drawdown (constraint)
    
3. VALIDATION:
    - Run optimized parameters on validation set
    - Check for overfitting: validation Sharpe should be > 60% of training Sharpe
    - If overfit, reduce parameter complexity
    
4. OUT-OF-SAMPLE TEST:
    - Run final parameters on test set (unseen data)
    - This is the true performance estimate
    
5. TRANSACTION COST MODELING:
    - Include spread costs (bid-ask)
    - Include commission fees
    - Include slippage estimate (0.5-1 pip for forex, 0.05-0.1% for crypto)
    - Include funding costs for overnight/multi-day positions
```

### 15.2 Performance Metrics

| Metric | Formula | Target |
|---|---|---|
| Net Sharpe Ratio | $(R_{ann} - R_f) / \sigma_{ann}$ | > 1.5 |
| Sortino Ratio | $(R_{ann} - R_f) / \sigma_{downside}$ | > 2.0 |
| Max Drawdown | Largest peak-to-trough | < 15% |
| Calmar Ratio | $R_{ann} / |DD_{max}|$ | > 1.0 |
| Win Rate | Winning trades / Total trades | > 55% |
| Profit Factor | Gross profit / Gross loss | > 1.5 |
| Average Trade | Net profit / Number of trades | > 2x avg cost |
| Expectancy | $p \times W_{avg} - q \times L_{avg}$ | > 0 |
| Recovery Factor | Net profit / Max drawdown | > 3.0 |
| Trades per Month | Average monthly frequency | 5-30 |

### 15.3 Regime-Conditional Backtesting

```
FOR each regime in [MEAN_REVERTING, TRENDING, TRANSITION]:
    1. Identify regime periods using:
       - Hurst exponent rolling classification
       - ADX-based classification
       - Hidden Markov Model classification
       
    2. Backtest mean reversion strategy ONLY during mean-reverting periods
    
    3. Compare:
       - Performance during mean-reverting regime
       - Performance during trending regime (should be bad)
       - Performance with regime filter ON vs OFF
       
    4. Report regime-conditional metrics:
       - Sharpe during mean-reverting: should be > 2.0
       - Sharpe during trending: likely negative
       - Overall Sharpe with filter: should improve over no filter
```

---

## 16. References

### Academic Papers

1. **Uhlenbeck, G.E., & Ornstein, L.S.** (1930). "On the Theory of Brownian Motion." *Physical Review*, 36, 823-841.
2. **Dickey, D.A., & Fuller, W.A.** (1979). "Distribution of the Estimators for Autoregressive Time Series with a Unit Root." *Journal of the American Statistical Association*, 74(366), 427-431.
3. **Kwiatkowski, D., Phillips, P.C.B., Schmidt, P., & Shin, Y.** (1992). "Testing the Null Hypothesis of Stationarity Against the Alternative of a Unit Root." *Journal of Econometrics*, 54(1-3), 159-178.
4. **Lo, A.W., & MacKinlay, A.C.** (1988). "Stock Market Prices Do Not Follow Random Walks: Evidence from a Simple Specification Test." *Review of Financial Studies*, 1(1), 41-66.
5. **Hurst, H.E.** (1951). "Long-Term Storage Capacity of Reservoirs." *Transactions of the American Society of Civil Engineers*, 116, 770-808.
6. **Poterba, J.M., & Summers, L.H.** (1988). "Mean Reversion in Stock Prices: Evidence and Implications." *Journal of Financial Economics*, 22(1), 27-59.
7. **Bondarenko, O.** (2003). "Statistical Arbitrage and Securities Prices." *Review of Financial Studies*, 16(3), 875-919.
8. **Connors, L., & Alvarez, C.** (2009). *Short Term Trading Strategies That Work*. TradingMarkets.

### Practitioner Resources

9. **Bollinger, J.** (2001). *Bollinger on Bollinger Bands*. McGraw-Hill.
10. **Keltner, C.** (1960). *How to Make Money in Commodities*. Keltner Statistical Service.
11. **Wilder, J.W.** (1978). *New Concepts in Technical Trading Systems*. Trend Research.
12. **Ernie Chan.** (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley.
13. **Ernie Chan.** (2009). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*. Wiley.

### Mathematical References

14. **Hamilton, J.D.** (1994). *Time Series Analysis*. Princeton University Press.
15. **Tsay, R.S.** (2010). *Analysis of Financial Time Series*. 3rd Edition. Wiley.
16. **Shreve, S.E.** (2004). *Stochastic Calculus for Finance II: Continuous-Time Models*. Springer.

---

## Appendix A: Quick Reference Formulas

| Formula | Expression |
|---|---|
| OU Process | $dX_t = \theta(\mu - X_t)dt + \sigma dW_t$ |
| Stationary Variance | $\sigma^2_{stat} = \sigma^2 / (2\theta)$ |
| Half-Life | $t_{half} = -\ln(2) / \ln(\phi)$ |
| Z-Score | $z = (P - \bar{P}_n) / \sigma_n$ |
| Bollinger Upper | $BB_{upper} = SMA(n) + k\sigma$ |
| Bollinger Lower | $BB_{lower} = SMA(n) - k\sigma$ |
| %B | $\%B = (P - BB_{lower})/(BB_{upper} - BB_{lower})$ |
| RSI | $RSI = 100 - 100/(1+RS)$ |
| Keltner Upper | $KC_{upper} = EMA(n) + k \times ATR(m)$ |
| ADF Statistic | $ADF = \hat{\gamma} / SE(\hat{\gamma})$ |
| Variance Ratio | $VR(q) = Var(r^{(q)}) / (q \cdot Var(r^{(1)}))$ |
| Hurst Exponent | $E[R(n)/S(n)] = C \cdot n^H$ |
| Position Size | $Q = (\text{Account} \times R\%) / (ATR \times k_{SL})$ |

---

*This document is part of the Multi-Agent AI Trading System knowledge base. Mean reversion strategies are most effective in range-bound market regimes and should be combined with regime detection filters to avoid losses during trending periods.*
