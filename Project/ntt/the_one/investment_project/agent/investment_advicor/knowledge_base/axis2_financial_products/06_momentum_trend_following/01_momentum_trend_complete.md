# Momentum & Trend Following Strategies — Complete Reference

## Document Metadata
| Field | Value |
|---|---|
| Strategy Class | Momentum / Trend Following |
| Asset Classes | Forex, Crypto (Spot & Futures) |
| Timeframe | Intraday to Multi-month |
| Complexity | Intermediate to Advanced |
| Capital Requirement | Medium |
| Last Updated | 2026-04-12 |

---

## Table of Contents
1. [Momentum Factor Research](#1-momentum-factor-research)
2. [Time-Series vs Cross-Sectional Momentum](#2-time-series-vs-cross-sectional-momentum)
3. [Trend Following Systems](#3-trend-following-systems)
4. [Moving Average Systems](#4-moving-average-systems)
5. [Donchian Channel Breakout (Turtle Trading)](#5-donchian-channel-breakout-turtle-trading)
6. [ADX-Based Trend Strength](#6-adx-based-trend-strength)
7. [Parabolic SAR](#7-parabolic-sar)
8. [Supertrend Indicator](#8-supertrend-indicator)
9. [Dual Momentum (Gary Antonacci)](#9-dual-momentum-gary-antonacci)
10. [Momentum Crashes and Tail Risk](#10-momentum-crashes-and-tail-risk)
11. [Position Sizing for Trend Following](#11-position-sizing-for-trend-following)
12. [Regime Detection](#12-regime-detection)
13. [Core Logic — Entry/Exit](#13-core-logic--entryexit)
14. [Technical Specifications](#14-technical-specifications)
15. [Mathematical Models](#15-mathematical-models)
16. [Risk Parameters](#16-risk-parameters)
17. [Execution Flow](#17-execution-flow)
18. [References](#18-references)

---

## 1. Momentum Factor Research

### 1.1 Academic Foundation

The momentum anomaly was formally documented by **Jegadeesh and Titman (1993)**, who showed that buying past winners and selling past losers generates significant abnormal returns over 3-12 month holding periods.

**Key Finding:**
- Portfolios formed by buying stocks with the highest returns over the past 3-12 months and selling stocks with the lowest returns earned approximately **1% per month** in excess returns.

**Momentum Return Definition:**

$$r_{mom,t} = r_{winner,t} - r_{loser,t}$$

Where winners and losers are determined by returns over the formation period $J$ (typically 3, 6, or 12 months).

### 1.2 Momentum in Forex and Crypto

**Forex Momentum:**
- Documented by Okunev & White (2003): currency momentum generates 5-10% annualized excess returns
- Strongest at 1-3 month horizons
- Linked to central bank policy persistence, carry trade flows, and investor herding

**Crypto Momentum:**
- Extremely strong momentum effect (Liu, Tsyvinski & Wu, 2019)
- Short-term (1 week to 1 month) momentum particularly powerful
- Higher volatility amplifies momentum returns but also crash risk
- Cross-sectional momentum among altcoins exploits the "altcoin season" rotation

### 1.3 Sources of Momentum Returns

| Source | Description |
|---|---|
| Behavioral Underreaction | Investors initially underreact to news, creating drift |
| Behavioral Overreaction | Initial underreaction followed by overreaction (delayed overshot) |
| Slow Information Diffusion | Information takes time to propagate across investors |
| Herding | Trend followers amplify existing price movements |
| Risk-Based | Momentum assets carry higher crash risk (compensation for tail risk) |
| Market Microstructure | Order flow persistence, stop-loss cascades |

---

## 2. Time-Series vs Cross-Sectional Momentum

### 2.1 Time-Series Momentum (TSMOM)

Time-series momentum looks at each asset individually: if it has gone up, buy it; if it has gone down, sell/short it.

**Signal:**

$$\text{Signal}_{i,t} = \text{sign}(r_{i,t-J:t})$$

Where $r_{i,t-J:t}$ is asset $i$'s return over the past $J$ periods.

**Scaled Position:**

$$w_{i,t} = \frac{\text{signal}_{i,t} \times \sigma_{target}}{\hat{\sigma}_{i,t}}$$

Where:
- $\sigma_{target}$ = target volatility (e.g., 10% annualized)
- $\hat{\sigma}_{i,t}$ = estimated volatility of asset $i$

**Moskowitz, Ooi, and Pedersen (2012)** documented TSMOM across 58 liquid instruments over 25 years, finding significant excess returns at 1-12 month horizons.

### 2.2 Cross-Sectional Momentum (XSMOM)

Cross-sectional momentum compares assets to each other: go long the top performers and short the bottom performers.

**Signal:**

$$\text{Rank}_{i,t} = \text{percentile\_rank}(r_{i,t-J:t}) \text{ among all assets}$$

**Position:**

$$w_{i,t} = \begin{cases} +1 & \text{if } \text{Rank}_{i,t} > 80\text{th percentile (winner)} \\ -1 & \text{if } \text{Rank}_{i,t} < 20\text{th percentile (loser)} \\ 0 & \text{otherwise} \end{cases}$$

### 2.3 Comparison

| Feature | Time-Series Momentum | Cross-Sectional Momentum |
|---|---|---|
| Benchmark | Asset's own history | Peer group performance |
| Net Exposure | Can be long or short overall | Dollar-neutral (long-short) |
| Best For | Single asset or macro | Large universes (crypto altcoins) |
| Correlation to Market | Moderate | Low (market-neutral) |
| Crash Risk | High when market reverses | Moderate (hedged) |
| Implementation | Simpler | Requires ranking universe |
| Forex Application | Trend following single pairs | Ranking all pairs, long best/short worst |
| Crypto Application | BTC trend following | Altcoin rotation |

### 2.4 Combined Momentum Signal

$$\text{CombinedSignal}_{i,t} = \alpha \times \text{TSMOM}_{i,t} + (1-\alpha) \times \text{XSMOM}_{i,t}$$

Where $\alpha$ is the blending weight (typically 0.5-0.7 favoring TSMOM for simplicity).

---

## 3. Trend Following Systems

### 3.1 Overview of Major Trend Following Systems

| System | Signal Source | Entry | Exit | Complexity |
|---|---|---|---|---|
| MA Crossover | Moving averages | Fast MA crosses slow MA | Reverse crossover | Low |
| Donchian Breakout | Price channels | New high/low breakout | Trailing channel | Low |
| ADX + DI | Directional movement | +DI crosses -DI with ADX > threshold | DI re-cross or ADX decline | Medium |
| Parabolic SAR | Trailing stop dots | Price crosses SAR | SAR catches price | Medium |
| Supertrend | ATR-based bands | Price crosses Supertrend line | Reverse cross | Medium |
| MACD | Signal line cross | MACD crosses signal line | Reverse crossover | Low |
| Ichimoku | Cloud system | Price above cloud, TK cross | Below cloud | High |
| Dual Momentum | Absolute + Relative | Positive absolute + top relative | Either condition fails | Medium |

### 3.2 Common Properties of Trend Following

1. **Right-skewed returns**: Many small losses, few large wins
2. **Low win rate**: Typically 30-45%
3. **High payoff ratio**: Average win >> Average loss
4. **Crisis alpha**: Performs well during market dislocations/crashes
5. **Drawdowns during ranging**: Whipsawed in sideways markets
6. **Long-term positive expectancy**: Edge comes from tail events

**Distribution of Trend Following Returns:**

$$\text{Skewness} > 0 \quad (\text{positive skew})$$
$$\text{Kurtosis} > 3 \quad (\text{fat tails, leptokurtic})$$

---

## 4. Moving Average Systems

### 4.1 Moving Average Types

**Simple Moving Average (SMA):**

$$SMA(n) = \frac{1}{n}\sum_{i=0}^{n-1} P_{t-i}$$

**Exponential Moving Average (EMA):**

$$EMA_t = \alpha P_t + (1-\alpha) EMA_{t-1}$$

Where $\alpha = \frac{2}{n+1}$ is the smoothing factor.

**Double Exponential Moving Average (DEMA):**

$$DEMA_t = 2 \times EMA(n) - EMA(EMA(n))$$

DEMA reduces lag by subtracting a second-order smoothed version.

**Triple Exponential Moving Average (TEMA):**

$$TEMA_t = 3 \times EMA(n) - 3 \times EMA(EMA(n)) + EMA(EMA(EMA(n)))$$

TEMA further reduces lag compared to DEMA.

**Hull Moving Average (HMA):**

$$HMA(n) = WMA(\sqrt{n}, 2 \times WMA(n/2) - WMA(n))$$

Where WMA is the Weighted Moving Average.

### 4.2 Lag Comparison

| MA Type | Lag (relative) | Smoothness | False Signal Rate |
|---|---|---|---|
| SMA | High (1.0x) | High | Low |
| EMA | Medium (0.7x) | Medium | Medium |
| DEMA | Low (0.4x) | Lower | Higher |
| TEMA | Very Low (0.2x) | Lowest | Highest |
| HMA | Low (0.3x) | Medium | Medium |

### 4.3 Moving Average Crossover System

**Golden Cross / Death Cross:**

```
LONG ENTRY:
    Fast MA(n_fast) crosses ABOVE Slow MA(n_slow)
    
SHORT ENTRY:
    Fast MA(n_fast) crosses BELOW Slow MA(n_slow)
    
EXIT:
    Reverse crossover
```

**Common MA Pairs:**

| System | Fast Period | Slow Period | Timeframe | Best For |
|---|---|---|---|---|
| Scalping | 5 | 20 | M5-M15 | Intraday FX |
| Short-Term | 10 | 50 | H1-H4 | Swing trading |
| Medium-Term | 20 | 50 | H4-D1 | Position trading |
| Long-Term | 50 | 200 | D1-W1 | Macro trends |
| Golden/Death Cross | 50 | 200 | D1 | Classic trend signal |

### 4.4 Triple Moving Average System

Uses three MAs to distinguish between short, medium, and long-term trends:

```
STRONG LONG: Fast > Medium > Slow (all aligned upward)
WEAK LONG: Fast > Slow, but Medium not perfectly aligned
NEUTRAL: Mixed ordering
WEAK SHORT: Fast < Slow, but Medium not perfectly aligned
STRONG SHORT: Fast < Medium < Slow (all aligned downward)

ENTRY: Only enter on STRONG signals
EXIT: When STRONG signal degrades to WEAK or NEUTRAL
```

### 4.5 Moving Average Envelope / Percentage Bands

$$\text{Upper Band} = MA(n) \times (1 + p\%)$$
$$\text{Lower Band} = MA(n) \times (1 - p\%)$$

**Trend Entry:**
- Long when price breaks above upper band (strong uptrend)
- Short when price breaks below lower band (strong downtrend)

**Percentage by Timeframe:**

| Timeframe | Envelope % | Application |
|---|---|---|
| M15 | 0.1-0.3% | Intraday FX |
| H1 | 0.3-0.5% | Short-term |
| H4 | 0.5-1.0% | Swing |
| D1 | 1.0-3.0% | Position |

---

## 5. Donchian Channel Breakout (Turtle Trading)

### 5.1 Donchian Channel Construction

$$\text{Upper Channel}(n) = \max(H_{t-1}, H_{t-2}, \ldots, H_{t-n})$$
$$\text{Lower Channel}(n) = \min(L_{t-1}, L_{t-2}, \ldots, L_{t-n})$$
$$\text{Middle} = \frac{\text{Upper} + \text{Lower}}{2}$$

### 5.2 Original Turtle Trading Rules

The Turtle Trading system, developed by Richard Dennis and William Eckhardt in the 1980s, is one of the most famous trend following systems.

**System 1 (Short-Term):**

| Rule | Specification |
|---|---|
| Entry Long | Close > 20-day High |
| Entry Short | Close < 20-day Low |
| Exit Long | Close < 10-day Low |
| Exit Short | Close > 10-day High |
| Skip Rule | Skip entry if previous breakout was profitable |
| Position Sizing | ATR-based (see Section 11) |

**System 2 (Long-Term):**

| Rule | Specification |
|---|---|
| Entry Long | Close > 55-day High |
| Entry Short | Close < 55-day Low |
| Exit Long | Close < 20-day Low |
| Exit Short | Close > 20-day High |
| Skip Rule | None (always enter) |
| Position Sizing | ATR-based |

### 5.3 Turtle Position Sizing (N-Based)

The Turtle system used "N" (20-day ATR) for position sizing:

$$N = ATR(20)$$

$$\text{Unit Size} = \frac{1\% \text{ of Account}}{N \times \text{Dollar per Point}}$$

**Pyramiding Rules:**
- Add 1 unit every $\frac{1}{2}N$ in the direction of the trade
- Maximum 4 units per market
- Maximum 6 units in closely correlated markets
- Maximum 12 units total

### 5.4 Turtle Stops

**Initial Stop:**

$$\text{Stop} = \text{Entry Price} \pm 2N$$

**Trailing Stop (based on exit channel):**
- Long: Trail at 10-day low (System 1) or 20-day low (System 2)
- Short: Trail at 10-day high (System 1) or 20-day high (System 2)

### 5.5 Modified Turtle System for Forex/Crypto

```yaml
modified_turtle:
  entry_channel: 20  # 20-period high/low for entry
  exit_channel: 10   # 10-period high/low for exit
  atr_period: 20
  
  entry_long:
    - Close > Highest High of last 20 bars
    - ADX(14) > 20  # Added trend strength filter
    - Volume > SMA(Volume, 20)  # Volume confirmation
    
  entry_short:
    - Close < Lowest Low of last 20 bars
    - ADX(14) > 20
    - Volume > SMA(Volume, 20)
    
  exit_long:
    - Close < Lowest Low of last 10 bars
    - OR trailing stop at Entry - 2 * ATR(20)
    
  exit_short:
    - Close > Highest High of last 10 bars
    - OR trailing stop at Entry + 2 * ATR(20)
    
  position_sizing:
    risk_per_unit: 1%
    unit_size: (Account * 0.01) / (ATR(20) * pip_value)
    max_units: 4
    pyramid_interval: 0.5 * ATR(20)
    
  filters:
    min_atr_percentile: 30  # Avoid dead markets
    max_correlation: 0.7    # Limit exposure to correlated pairs
```

---

## 6. ADX-Based Trend Strength

### 6.1 ADX Calculation

**Directional Movement:**

$$+DM = H_t - H_{t-1} \quad \text{(if positive and > } |L_{t-1} - L_t|, \text{else 0)}$$
$$-DM = L_{t-1} - L_t \quad \text{(if positive and > } H_t - H_{t-1}, \text{else 0)}$$

**Directional Indicators:**

$$+DI(n) = 100 \times \frac{\text{Smoothed}(+DM, n)}{ATR(n)}$$
$$-DI(n) = 100 \times \frac{\text{Smoothed}(-DM, n)}{ATR(n)}$$

**Average Directional Index:**

$$DX = 100 \times \frac{|+DI - (-DI)|}{+DI + (-DI)}$$
$$ADX(n) = \text{Smoothed}(DX, n)$$

### 6.2 ADX Interpretation

| ADX Value | Trend Strength | Trading Implication |
|---|---|---|
| 0-15 | Absent/Weak | Avoid trend following; use mean reversion |
| 15-25 | Developing | Prepare for entry; watch for DI crossover |
| 25-50 | Strong | Trend following ideal; enter and hold |
| 50-75 | Very Strong | Trend likely mature; watch for exhaustion |
| 75-100 | Extremely Strong | Rare; potential for sharp reversal |

### 6.3 ADX Trading Strategy

```
ENTRY CONDITIONS:
    LONG:
        1. ADX > 25 (strong trend confirmed)
        2. +DI > -DI (uptrend direction)
        3. +DI crosses above -DI (DI crossover signal)
        4. ADX is rising (trend strengthening)
        
    SHORT:
        1. ADX > 25
        2. -DI > +DI (downtrend direction)
        3. -DI crosses above +DI
        4. ADX is rising

EXIT CONDITIONS:
    1. ADX falls below 20 (trend weakening)
    2. DI lines re-cross (direction change)
    3. ADX peaks and starts declining (trend exhaustion)
    4. Trailing stop at 2 * ATR(14)
```

### 6.4 ADX Trend Quality Filter

Use ADX as a filter for other systems (MA crossover, breakout):

```
TREND QUALITY SCORE:
    IF ADX > 40 AND rising:     quality = "HIGH"     → Full position
    IF ADX > 25 AND rising:     quality = "MEDIUM"   → 75% position
    IF ADX > 25 AND flat:       quality = "LOW"       → 50% position
    IF ADX < 25:                quality = "NONE"      → No trend trade
```

---

## 7. Parabolic SAR

### 7.1 Parabolic SAR Calculation

The Parabolic Stop and Reverse (SAR) is a trend-following indicator that provides potential entry and exit points.

**Uptrend SAR:**

$$SAR_{t+1} = SAR_t + AF \times (EP - SAR_t)$$

**Downtrend SAR:**

$$SAR_{t+1} = SAR_t - AF \times (SAR_t - EP)$$

Where:
- $AF$ = Acceleration Factor (starts at 0.02, increases by 0.02 each new EP, max 0.20)
- $EP$ = Extreme Point (highest high in uptrend, lowest low in downtrend)

### 7.2 Parabolic SAR Parameters

| Parameter | Default | Conservative | Aggressive |
|---|---|---|---|
| Initial AF | 0.02 | 0.01 | 0.03 |
| AF Increment | 0.02 | 0.01 | 0.03 |
| Max AF | 0.20 | 0.10 | 0.30 |

- **Lower AF**: Slower, fewer reversals, stays in trends longer, wider stops
- **Higher AF**: Faster, more reversals, captures turns earlier, tighter stops

### 7.3 Parabolic SAR Strategy

```
SIGNALS:
    LONG: Price crosses above SAR (SAR flips below price)
    SHORT: Price crosses below SAR (SAR flips above price)
    
STOP: SAR value itself serves as trailing stop
    Long stop = current SAR value (below price)
    Short stop = current SAR value (above price)

ENHANCEMENTS:
    1. Only take long signals when price > EMA(200) (macro trend filter)
    2. Only take short signals when price < EMA(200)
    3. Combine with ADX > 25 filter
    4. Use lower AF (0.01) for trend following, higher AF (0.03) for scalping
```

### 7.4 Limitations

- Generates excessive signals in sideways markets (whipsaw)
- Fixed acceleration factor doesn't adapt to volatility
- SAR can be too far from price in early stages of trend

---

## 8. Supertrend Indicator

### 8.1 Supertrend Calculation

$$\text{Basic Upper Band} = \frac{H + L}{2} + k \times ATR(n)$$

$$\text{Basic Lower Band} = \frac{H + L}{2} - k \times ATR(n)$$

**Final Bands (with trend persistence):**

$$\text{Final Upper Band}_t = \begin{cases} \text{Basic Upper}_t & \text{if Basic Upper}_t < \text{Final Upper}_{t-1} \text{ OR Close}_{t-1} > \text{Final Upper}_{t-1} \\ \text{Final Upper}_{t-1} & \text{otherwise} \end{cases}$$

$$\text{Final Lower Band}_t = \begin{cases} \text{Basic Lower}_t & \text{if Basic Lower}_t > \text{Final Lower}_{t-1} \text{ OR Close}_{t-1} < \text{Final Lower}_{t-1} \\ \text{Final Lower}_{t-1} & \text{otherwise} \end{cases}$$

**Supertrend:**

$$\text{Supertrend}_t = \begin{cases} \text{Final Lower Band}_t & \text{if Close}_t > \text{Final Upper Band}_{t-1} \text{ (uptrend)} \\ \text{Final Upper Band}_t & \text{if Close}_t < \text{Final Lower Band}_{t-1} \text{ (downtrend)} \\ \text{Supertrend}_{t-1} & \text{otherwise (continue current trend)} \end{cases}$$

### 8.2 Supertrend Parameters

| Parameter | Default | Forex | Crypto |
|---|---|---|---|
| ATR Period ($n$) | 10 | 10-14 | 10-14 |
| Multiplier ($k$) | 3.0 | 2.0-3.0 | 3.0-5.0 |

**Higher $k$**: Fewer whipsaws, wider stops, catches fewer trends
**Lower $k$**: More signals, tighter stops, catches more trends (more whipsaws)

### 8.3 Supertrend Strategy

```
LONG ENTRY:
    Supertrend flips from above price to below price (color change to green/bullish)
    Entry: Close of the bar that triggers the flip
    Stop: Supertrend value (which is the Final Lower Band)
    
SHORT ENTRY:
    Supertrend flips from below price to above price (color change to red/bearish)
    Entry: Close of the bar that triggers the flip
    Stop: Supertrend value (which is the Final Upper Band)

MULTI-TIMEFRAME SUPERTREND:
    Higher TF (D1): Determines trend direction
    Lower TF (H1): Entry timing
    
    IF D1 Supertrend = LONG:
        Only take H1 LONG signals
    IF D1 Supertrend = SHORT:
        Only take H1 SHORT signals
```

### 8.4 Double Supertrend System

Use two Supertrend indicators with different parameters:

```
ST1 = Supertrend(10, 2.0)  # Fast - for entry timing
ST2 = Supertrend(10, 4.0)  # Slow - for trend filter and trailing stop

LONG ENTRY:
    ST2 = bullish (main trend is up)
    AND ST1 flips to bullish (entry timing)
    
    Stop: ST2 value (wider stop from slower indicator)
    Target: Risk-Reward ratio of 2:1 or trail with ST1

SHORT ENTRY:
    ST2 = bearish
    AND ST1 flips to bearish
    
    Stop: ST2 value
    Target: RR 2:1 or trail with ST1
```

---

## 9. Dual Momentum (Gary Antonacci)

### 9.1 Concept

Dual Momentum, developed by Gary Antonacci (2014), combines two types of momentum:

1. **Absolute Momentum (Time-Series)**: Is the asset trending up in absolute terms?
2. **Relative Momentum (Cross-Sectional)**: Is the asset outperforming its alternatives?

### 9.2 Absolute Momentum

$$\text{Absolute Momentum} = r_{asset,t-J:t} - r_{risk-free,t-J:t}$$

If the excess return is positive, the asset has positive absolute momentum.

### 9.3 Relative Momentum

$$\text{Relative Score}_i = r_{i,t-J:t}$$

Rank all candidate assets by their $J$-period return. Select the top $K$ assets.

### 9.4 Dual Momentum Decision Framework

```
Algorithm: Dual Momentum

INPUT:
    assets: list of candidate assets
    lookback: J periods (typically 12 months / 252 days)
    risk_free_rate: current risk-free rate (or T-bill return)
    
FOR each rebalancing period:
    
    1. RELATIVE MOMENTUM:
       - Calculate J-period return for each asset
       - Rank assets by return
       - Select top asset(s)
       
    2. ABSOLUTE MOMENTUM:
       - For selected asset(s), check if J-period return > risk_free_rate
       
    3. DECISION:
       IF relative_winner has positive absolute momentum:
           INVEST in relative_winner
       ELSE:
           INVEST in safe haven (bonds, stablecoins, cash)
           
    4. REBALANCE monthly (or when signal changes)
```

### 9.5 Dual Momentum for Forex

```yaml
dual_momentum_forex:
  universe:
    - EUR/USD
    - GBP/USD
    - AUD/USD
    - USD/JPY (inverse)
    - USD/CHF (inverse)
    - NZD/USD
  
  lookback: 63 trading days (3 months) to 252 trading days (12 months)
  
  absolute_benchmark: cash (0% or money market rate)
  
  rules:
    1. Calculate 3-month return for each pair
    2. Select top 2 pairs by return (relative momentum)
    3. For each selected pair, check if return > 0 (absolute momentum)
    4. Go long selected pairs with positive absolute momentum
    5. If no pair has positive absolute momentum, stay in cash
    6. Rebalance monthly
```

### 9.6 Dual Momentum for Crypto

```yaml
dual_momentum_crypto:
  universe:
    - BTC/USDT
    - ETH/USDT
    - SOL/USDT
    - BNB/USDT
    - AVAX/USDT
    - Top 10 by market cap (rotated quarterly)
  
  lookback: 21 days (1 month) to 63 days (3 months)
  # Shorter lookback for crypto due to faster cycles
  
  absolute_benchmark: stablecoin yield (e.g., USDT lending rate)
  
  rules:
    1. Calculate 1-month return for each asset
    2. Select top 3 by return (relative momentum)
    3. Check each has positive absolute momentum (> stablecoin yield)
    4. Equal-weight or volatility-weight the selected assets
    5. Rebalance weekly or bi-weekly
    6. If fewer than 2 have positive absolute momentum, increase stablecoin allocation
```

---

## 10. Momentum Crashes and Tail Risk

### 10.1 The Momentum Crash Phenomenon

Momentum strategies are prone to sudden, severe drawdowns known as "momentum crashes." These occur when:

1. **Market reversals**: After prolonged trends, losers rebound sharply and winners decline
2. **Volatility spikes**: High-vol environments compress momentum profits
3. **Leverage unwind**: Crowded momentum positions are simultaneously unwound

**Historical Momentum Crashes:**
- 2009 Q1: Post-GFC equity reversal (~40% drawdown for momentum)
- March 2020: COVID crash and rebound
- May 2021: Crypto market crash (60% drawdown for crypto momentum)
- November 2022: FTX collapse (severe altcoin momentum crash)

### 10.2 Statistical Properties of Momentum Crashes

$$\text{Momentum Return} \sim \text{Left-skewed, Fat-tailed}$$

While individual momentum trades are right-skewed (small losses, big wins), the aggregate momentum factor can exhibit left-skew due to crash events:

$$\text{Skewness}_{factor} < 0 \quad (\text{negative skew at factor level})$$

**Conditional Volatility:**

$$\sigma_{mom,t} = f(\text{Market Vol}, \text{Recent Drawdown}, \text{Crowding})$$

Momentum volatility increases dramatically during market stress.

### 10.3 Momentum Crash Mitigation

| Technique | Description | Cost |
|---|---|---|
| Volatility Scaling | Reduce position when vol is high | Reduces returns in high-vol trends |
| Dynamic Hedging | Buy put options on momentum factor | Premium cost |
| Maximum Drawdown Stop | Reduce exposure when DD > threshold | May exit before recovery |
| Diversification | Run momentum across uncorrelated markets | Reduced concentration |
| Holding Period Blending | Combine multiple lookback periods | Smooths returns, reduces extremes |
| Momentum + Value Combo | Combine with mean reversion | Reduces drawdown but may reduce returns |

### 10.4 Volatility-Scaled Momentum

**Barroso and Santa-Clara (2015):**

$$w_t = \frac{\sigma_{target}}{\hat{\sigma}_{mom,t}} \times \text{raw\_momentum\_weight}$$

Where $\hat{\sigma}_{mom,t}$ is the realized volatility of the momentum strategy over the past 6 months.

This "risk-managed momentum" significantly reduces drawdowns and improves Sharpe ratio.

### 10.5 Maximum Loss Model

$$VaR_{1\%} = \mu_{mom} - z_{0.01} \times \sigma_{mom}$$

$$CVaR_{1\%} = E[R | R < VaR_{1\%}]$$

For a typical momentum strategy:
- $VaR_{1\%, daily}$ = -2% to -5%
- $CVaR_{1\%, daily}$ = -3% to -8%
- Maximum observed monthly loss: -15% to -30%

---

## 11. Position Sizing for Trend Following

### 11.1 ATR-Based Position Sizing

The industry-standard approach for trend following position sizing:

$$\text{Position Size} = \frac{\text{Account} \times \text{Risk\%}}{N \times \text{Dollar Per Point}}$$

Where:
- $\text{Account}$ = total account equity
- $\text{Risk\%}$ = percentage of account risked per trade (typically 1-2%)
- $N$ = Average True Range (ATR), a measure of volatility
- $\text{Dollar Per Point}$ = value of one point/pip movement for one unit

### 11.2 Derivation

The goal is to ensure that a $1N$ adverse move results in exactly $\text{Risk\%}$ loss:

$$\text{Loss if price moves } 1N = \text{Position Size} \times N \times \text{Dollar Per Point}$$

Setting this equal to the desired risk:

$$\text{Position Size} \times N \times \text{Dollar Per Point} = \text{Account} \times \text{Risk\%}$$

$$\therefore \text{Position Size} = \frac{\text{Account} \times \text{Risk\%}}{N \times \text{Dollar Per Point}}$$

### 11.3 Position Sizing Examples

**Forex Example (EUR/USD on $100,000 account):**

| Parameter | Value |
|---|---|
| Account | $100,000 |
| Risk per trade | 1% = $1,000 |
| ATR(20) | 0.0080 (80 pips) |
| Dollar per pip (standard lot) | $10 |
| Stop distance | 2N = 160 pips |
| Risk per trade / (Stop in pips * pip value) | $1,000 / (160 * $10) |
| Position size | 0.625 lots (~62,500 units) |

**Crypto Example (BTC/USDT on $50,000 account):**

| Parameter | Value |
|---|---|
| Account | $50,000 |
| Risk per trade | 2% = $1,000 |
| ATR(20) | $2,500 |
| BTC price | $50,000 |
| Stop distance | 2N = $5,000 |
| Position size (USD notional) | $1,000 / ($5,000/$50,000) = $10,000 |
| Position size (BTC) | 0.20 BTC |

### 11.4 Pyramiding (Adding to Winning Positions)

Turtle-style pyramiding adds units as the trade moves favorably:

```
PYRAMIDING RULES:
    Initial entry: 1 unit at Entry Price
    Add 1 unit at: Entry + 0.5N
    Add 1 unit at: Entry + 1.0N
    Add 1 unit at: Entry + 1.5N
    Maximum: 4 units
    
    Stop adjustments:
    After 2nd unit: Move all stops to Entry - 1.5N
    After 3rd unit: Move all stops to Entry - 0.5N
    After 4th unit: Move all stops to Entry + 0.5N (breakeven+)
    
RISK CALCULATION (all units):
    Total risk = sum of (entry_price_i - stop) * position_size_i
    Should not exceed 4-5% of account for all units combined
```

### 11.5 Volatility-Based Portfolio Allocation

For a portfolio of trend-following strategies across multiple assets:

$$w_i = \frac{1/\hat{\sigma}_i}{\sum_j 1/\hat{\sigma}_j}$$

This inverse-volatility weighting ensures equal risk contribution from each position.

**Risk Parity Position Sizing:**

$$\text{Risk Contribution}_i = w_i \times \beta_i \times \sigma_p$$

Where equal risk contributions are targeted:

$$\text{RC}_1 = \text{RC}_2 = \ldots = \text{RC}_n = \frac{\sigma_p}{n}$$

---

## 12. Regime Detection

### 12.1 The Importance of Regime Detection

Trend following performs well in trending regimes but poorly in ranging regimes. Regime detection allows:
- Activating trend following during trending regimes
- Reducing position sizes or switching to mean reversion during ranging regimes
- Avoiding whipsaw losses

### 12.2 ADX-Based Regime Detection

```
REGIME CLASSIFICATION (Simple):
    IF ADX > 25 AND ADX is rising:
        regime = "TRENDING"
        strategy = TREND_FOLLOWING
        
    IF ADX < 20 OR (ADX > 25 AND ADX is falling):
        regime = "RANGING"
        strategy = MEAN_REVERSION or NO_TRADE
        
    IF ADX between 20-25:
        regime = "TRANSITION"
        strategy = REDUCED_SIZE
```

### 12.3 Moving Average Slope Regime

$$\text{MA Slope} = \frac{MA(n)_t - MA(n)_{t-k}}{k}$$

$$\text{Normalized Slope} = \frac{\text{MA Slope}}{ATR(n)}$$

| Normalized Slope | Regime | Action |
|---|---|---|
| > +0.5 | Strong Uptrend | Trend follow long |
| +0.2 to +0.5 | Mild Uptrend | Cautious trend following |
| -0.2 to +0.2 | Ranging | Mean reversion or stand aside |
| -0.5 to -0.2 | Mild Downtrend | Cautious trend following |
| < -0.5 | Strong Downtrend | Trend follow short |

### 12.4 Volatility Regime Detection

$$\sigma_{ratio} = \frac{\sigma_{short}(n_1)}{\sigma_{long}(n_2)}$$

Where $n_1 < n_2$ (e.g., $n_1=10$, $n_2=60$).

| $\sigma_{ratio}$ | Regime | Action |
|---|---|---|
| > 1.5 | Expanding volatility | Reduce size, widen stops |
| 1.0-1.5 | Normal volatility | Standard parameters |
| 0.7-1.0 | Contracting volatility | Prepare for breakout |
| < 0.7 | Low volatility (squeeze) | Expect large move; prepare for trend entry |

### 12.5 Hidden Markov Model (HMM) for Regime Detection

Model the market as having $K$ hidden states (e.g., trending-up, trending-down, ranging):

$$P(\text{State}_t = k | \text{observations}) = \text{Forward-Backward Algorithm}$$

**States:**
- State 1: Low volatility, range-bound (use mean reversion)
- State 2: High volatility, trending (use trend following)
- State 3: Crisis/crash (use defensive positioning)

**Transition Matrix:**

$$A = \begin{bmatrix} P(1 \to 1) & P(1 \to 2) & P(1 \to 3) \\ P(2 \to 1) & P(2 \to 2) & P(2 \to 3) \\ P(3 \to 1) & P(3 \to 2) & P(3 \to 3) \end{bmatrix}$$

Typical persistence: $P(i \to i) > 0.90$ (regimes are "sticky").

### 12.6 Composite Regime Indicator

```
Algorithm: Composite Regime Score

INPUTS:
    adx = ADX(14)
    hurst = Hurst_Exponent(100)
    vol_ratio = sigma_short / sigma_long
    ma_slope = normalized MA slope
    
TRENDING_SCORE:
    ts = 0
    IF adx > 25: ts += 0.3
    IF adx > 35: ts += 0.1
    IF hurst > 0.55: ts += 0.25
    IF abs(ma_slope) > 0.3: ts += 0.2
    IF vol_ratio > 1.2: ts += 0.15
    
RANGING_SCORE:
    rs = 0
    IF adx < 20: rs += 0.3
    IF hurst < 0.45: rs += 0.25
    IF abs(ma_slope) < 0.1: rs += 0.2
    IF vol_ratio < 0.8: rs += 0.15
    IF BBW < percentile_25: rs += 0.1
    
REGIME:
    IF ts > 0.6: "TRENDING"
    ELIF rs > 0.6: "RANGING"
    ELSE: "TRANSITION"
```

---

## 13. Core Logic — Entry/Exit

### 13.1 Universal Trend Following Entry Logic

```
Algorithm: Composite Trend Following Entry

INDICATORS:
    ma_fast = EMA(close, fast_period)
    ma_slow = EMA(close, slow_period)
    adx = ADX(close, 14)
    plus_di = +DI(14)
    minus_di = -DI(14)
    donchian_upper = Highest(high, channel_period)
    donchian_lower = Lowest(low, channel_period)
    supertrend, st_direction = Supertrend(atr_period, st_multiplier)
    atr = ATR(atr_period)
    
REGIME:
    regime = composite_regime_score(close)
    IF regime != "TRENDING": SKIP (no trend entry)

LONG ENTRY (composite scoring):
    score = 0
    
    # MA Crossover
    IF ma_fast > ma_slow AND ma_fast[1] <= ma_slow[1]:  # Fresh crossover
        score += 0.25
    ELIF ma_fast > ma_slow:  # Ongoing uptrend
        score += 0.15
    
    # Donchian Breakout
    IF close > donchian_upper:
        score += 0.25
    
    # ADX + DI
    IF adx > 25 AND plus_di > minus_di:
        score += 0.20
    
    # Supertrend
    IF st_direction == BULLISH:
        score += 0.15
    
    # Price above long-term MA
    IF close > EMA(close, 200):
        score += 0.15
    
    IF score >= 0.60:
        SIGNAL = LONG
        entry = close
        stop = close - 2 * atr
        target = close + 3 * atr  # or trailing
        size = (Account * Risk%) / (2 * atr * dollar_per_point)

SHORT ENTRY (mirror logic):
    score = 0
    IF ma_fast < ma_slow AND ma_fast[1] >= ma_slow[1]:
        score += 0.25
    ELIF ma_fast < ma_slow:
        score += 0.15
    IF close < donchian_lower:
        score += 0.25
    IF adx > 25 AND minus_di > plus_di:
        score += 0.20
    IF st_direction == BEARISH:
        score += 0.15
    IF close < EMA(close, 200):
        score += 0.15
    
    IF score >= 0.60:
        SIGNAL = SHORT
```

### 13.2 Exit and Trail Management

```
Algorithm: Trend Following Exit Management

TRAILING STOP OPTIONS (select one based on strategy):

    Option A: ATR Trailing Stop
        trail_long = max(trail_long_prev, close - k * atr)
        trail_short = min(trail_short_prev, close + k * atr)
        k = 2.0 to 3.0
    
    Option B: Donchian Channel Exit
        trail_long = Lowest(low, exit_channel_period)  # e.g., 10 bars
        trail_short = Highest(high, exit_channel_period)
    
    Option C: Supertrend Exit
        trail_long = supertrend value (when bullish)
        trail_short = supertrend value (when bearish)
    
    Option D: Parabolic SAR
        trail = parabolic_sar value
    
    Option E: Moving Average Exit
        trail_long = EMA(close, exit_ma_period)
        trail_short = EMA(close, exit_ma_period)

EXIT CONDITIONS:
    IF position == LONG:
        IF close < trailing_stop: EXIT
        IF regime changed to RANGING: EXIT (or reduce size)
        IF time_in_trade > max_duration: EVALUATE
        IF unrealized_profit > 5R: Consider partial exit
        
    IF position == SHORT:
        IF close > trailing_stop: EXIT
        IF regime changed to RANGING: EXIT
```

### 13.3 Pyramiding Logic

```
Algorithm: Turtle-Style Pyramiding

PARAMETERS:
    max_units = 4
    pyramid_interval = 0.5 * ATR(20)
    
ON_POSITION_UPDATE:
    IF position is LONG AND num_units < max_units:
        IF close > last_add_price + pyramid_interval:
            # Add another unit
            new_unit_size = base_unit_size  # Same size as initial
            total_position += new_unit_size
            last_add_price = close
            num_units += 1
            
            # Adjust stops for all units
            new_stop = close - 2 * ATR(20)
            FOR each unit:
                unit.stop = max(unit.stop, new_stop)
            
            LOG: "Pyramided to {num_units} units at {close}"
    
    # Ensure total risk doesn't exceed limits
    total_risk = sum((entry_i - stop) * size_i for each unit)
    IF total_risk > max_portfolio_risk * account:
        REDUCE position proportionally
```

---

## 14. Technical Specifications

### 14.1 System Configuration

```yaml
trend_following_config:
  # Moving Average System
  ma_system:
    fast_ma_type: EMA
    fast_period: 20
    slow_ma_type: EMA
    slow_period: 50
    signal_type: crossover  # or price_above_ma
    
  # Donchian Channel
  donchian:
    entry_period: 20
    exit_period: 10
    
  # ADX
  adx:
    period: 14
    trend_threshold: 25
    strong_threshold: 40
    
  # Supertrend
  supertrend:
    atr_period: 10
    multiplier: 3.0
    
  # Position Sizing
  position_sizing:
    method: atr_based
    risk_per_trade: 0.01  # 1% of account
    atr_period: 20
    stop_multiplier: 2.0  # 2N stop
    max_units: 4
    pyramid_interval_N: 0.5
    
  # Trailing Stop
  trailing:
    method: donchian_exit  # or atr_trail, supertrend, parabolic_sar
    atr_multiplier: 2.5
    donchian_exit_period: 10
    
  # Risk Limits
  risk_limits:
    max_portfolio_heat: 0.06  # 6% total portfolio risk
    max_correlated_exposure: 0.04  # 4% in correlated markets
    max_single_market: 0.02  # 2% per market
    max_drawdown_pause: 0.10  # Pause trading at 10% drawdown
```

### 14.2 Asset-Specific Configuration

**Forex:**

```yaml
forex_trend_config:
  pairs:
    EUR/USD:
      min_atr_pips: 40
      max_spread_pips: 1.5
      session_filter: london_ny
      ma_fast: 20
      ma_slow: 50
      
    GBP/JPY:
      min_atr_pips: 80
      max_spread_pips: 3.0
      session_filter: london
      ma_fast: 15
      ma_slow: 40
      
    AUD/USD:
      min_atr_pips: 30
      max_spread_pips: 1.5
      session_filter: sydney_london
      ma_fast: 20
      ma_slow: 50
```

**Crypto:**

```yaml
crypto_trend_config:
  assets:
    BTC/USDT:
      min_atr_pct: 1.5%
      max_spread_pct: 0.05%
      session_filter: none  # 24/7
      supertrend_mult: 3.0
      funding_rate_check: true
      
    ETH/USDT:
      min_atr_pct: 2.0%
      max_spread_pct: 0.05%
      supertrend_mult: 3.5
      
    Altcoins:
      min_atr_pct: 3.0%
      max_spread_pct: 0.10%
      supertrend_mult: 4.0
      liquidity_min_24h_volume: $10M
```

---

## 15. Mathematical Models

### 15.1 Momentum Factor Return Model

The momentum factor return can be modeled as:

$$r_{mom,t} = \alpha + \beta_{mkt} r_{mkt,t} + \beta_{vol} \Delta\sigma_t + \epsilon_t$$

Where:
- $\alpha$ = momentum alpha (excess return)
- $\beta_{mkt}$ = market beta (typically close to 0 for L/S momentum)
- $\beta_{vol}$ = volatility beta (negative — momentum suffers in vol spikes)

### 15.2 Trend Following as a Straddle

Trend following returns approximate a **long straddle** payoff:

$$\text{TF Return} \approx a|r_{mkt}| - c$$

Where:
- $a$ = sensitivity to absolute market moves
- $c$ = cost of whipsaws (like option premium)

This means trend following:
- Profits from large moves in either direction
- Loses during small, choppy moves (the "premium" for the straddle)

**Fung and Hsieh (2001) Lookback Straddle:**

$$\text{TF Factor} = \max(S_T - S^*, 0) + \max(S^{**} - S_T, 0) - \text{Premium}$$

Where $S^*$ and $S^{**}$ are the running maximum and minimum prices.

### 15.3 Breakout Probability Model

The probability of a Donchian channel breakout leading to a sustained trend:

$$P(\text{true breakout}) = P(\text{trend regime}) \times P(\text{breakout | trend})$$

From historical analysis:
- $P(\text{true breakout}) \approx 0.30-0.40$
- Win rate of trend following: ~35%
- Average win / Average loss ratio needed for profitability: > 2.0

**Required Payoff Ratio:**

$$\frac{W_{avg}}{L_{avg}} > \frac{1-p}{p} = \frac{1-0.35}{0.35} = 1.86$$

So the average winning trade must be at least 1.86x the average losing trade.

### 15.4 Optimal Moving Average Period

Brock, Lakonishok, and LeBaron (1992) tested various MA rules. The optimal MA length depends on the dominant cycle:

$$n_{optimal} \approx \frac{T_{cycle}}{2\pi} \times \sqrt{2}$$

Where $T_{cycle}$ is the dominant price cycle length.

**Practical Guideline:**
- For a 40-day dominant cycle: $n_{opt} \approx 9$ bars
- For a 100-day dominant cycle: $n_{opt} \approx 22$ bars
- For a 200-day dominant cycle: $n_{opt} \approx 45$ bars

### 15.5 Sharpe Ratio of Trend Following

The theoretical Sharpe ratio of a pure trend following strategy:

$$SR_{TF} = \frac{|\mu|}{\sigma} \times \rho_{signal}$$

Where:
- $|\mu|/\sigma$ = Sharpe ratio of the underlying asset
- $\rho_{signal}$ = correlation between the signal and future returns

For a simple MA crossover:

$$\rho_{signal} \approx \frac{n_{slow} - n_{fast}}{n_{slow} + n_{fast}} \times \frac{|\mu|}{\sigma}$$

---

## 16. Risk Parameters

### 16.1 Position Sizing Summary

| Approach | Formula | Best For |
|---|---|---|
| Fixed Fractional | $Q = (f \times W) / (\text{Stop Distance})$ | General trend following |
| ATR-Based | $Q = (R\% \times W) / (N \times \$/point)$ | Turtle-style systems |
| Volatility Parity | $w_i = (1/\sigma_i) / \sum(1/\sigma_j)$ | Multi-asset portfolios |
| Kelly Criterion | $f = (pb - q) / b$ | Maximum growth (use half-Kelly) |

### 16.2 Stop Loss Parameters

| System | Initial Stop | Trailing Stop |
|---|---|---|
| MA Crossover | 2-3x ATR from entry | MA cross back (or faster MA) |
| Donchian Breakout | 2N from entry | 10-day low/high (System 1) |
| ADX System | 2x ATR | ADX drops below 20 |
| Parabolic SAR | SAR value | SAR value (auto-trailing) |
| Supertrend | Supertrend band value | Supertrend flip |

### 16.3 Portfolio Heat Limits

$$\text{Portfolio Heat} = \sum_i |\text{Risk}_i| = \sum_i |(\text{Entry}_i - \text{Stop}_i) \times Q_i|$$

| Risk Level | Max Portfolio Heat | Max Per Market | Max Correlated Group |
|---|---|---|---|
| Conservative | 4% | 1% | 2% |
| Moderate | 6% | 1.5% | 3% |
| Aggressive | 10% | 2% | 5% |

### 16.4 Drawdown Management

```
DRAWDOWN RESPONSE PROTOCOL:

DD < 5%:   Normal operations
DD 5-10%:  Reduce position sizes by 25%
DD 10-15%: Reduce position sizes by 50%
DD 15-20%: Reduce position sizes by 75%, no new positions
DD > 20%:  Halt trading, review strategy, possible full exit

RECOVERY:
    After DD peak, restore normal sizing gradually:
    When DD reduces to 50% of peak: Restore to 50% size
    When DD reduces to 25% of peak: Restore to 75% size
    When new equity high: Restore full size
```

### 16.5 Correlation-Based Risk Limits

```yaml
correlation_limits:
  max_pairwise_correlation: 0.70
  # If two positions have > 0.70 correlation, treat as one position for sizing
  
  correlation_groups:
    usd_group: [EUR/USD, GBP/USD, AUD/USD]
    jpy_group: [USD/JPY, EUR/JPY, GBP/JPY]
    crypto_major: [BTC, ETH]
    crypto_alt: [SOL, AVAX, DOT]
    
  max_group_exposure: 3%  # Max risk per correlated group
  max_total_directional: 5%  # Max net directional risk
```

---

## 17. Execution Flow

### 17.1 Complete Trend Following System — Pseudocode

```python
class TrendFollowingSystem:
    """
    Complete Trend Following Trading System
    Supports: MA, Donchian, ADX, Supertrend, Dual Momentum
    Markets: Forex, Crypto
    """
    
    def __init__(self, config):
        self.config = config
        self.positions = {}       # symbol -> position info
        self.portfolio_heat = 0.0
        self.peak_equity = config['initial_capital']
        self.current_equity = config['initial_capital']
        
    def calculate_indicators(self, symbol, data):
        """Step 1: Calculate all trend indicators."""
        close = data['close']
        high = data['high']
        low = data['low']
        
        ind = {}
        
        # Moving Averages
        ind['ema_fast'] = EMA(close, self.config['ma_fast'])
        ind['ema_slow'] = EMA(close, self.config['ma_slow'])
        ind['ema_200'] = EMA(close, 200)
        
        # Donchian Channels
        ind['don_upper'] = rolling_max(high, self.config['donchian_entry'])
        ind['don_lower'] = rolling_min(low, self.config['donchian_entry'])
        ind['don_exit_upper'] = rolling_max(high, self.config['donchian_exit'])
        ind['don_exit_lower'] = rolling_min(low, self.config['donchian_exit'])
        
        # ADX
        ind['adx'], ind['plus_di'], ind['minus_di'] = ADX(high, low, close, 14)
        
        # Supertrend
        ind['supertrend'], ind['st_direction'] = supertrend(
            high, low, close,
            self.config['st_atr_period'],
            self.config['st_multiplier']
        )
        
        # ATR
        ind['atr'] = ATR(high, low, close, self.config['atr_period'])
        
        return ind
    
    def detect_regime(self, symbol, data, indicators):
        """Step 2: Determine market regime."""
        adx = indicators['adx'][-1]
        hurst = calculate_hurst(data['close'][-100:])
        
        trending_score = 0
        if adx > 25: trending_score += 0.35
        if adx > 35: trending_score += 0.15
        if hurst > 0.55: trending_score += 0.25
        ma_slope = (indicators['ema_slow'][-1] - indicators['ema_slow'][-10]) / \
                   (10 * indicators['atr'][-1])
        if abs(ma_slope) > 0.3: trending_score += 0.25
        
        if trending_score > 0.6:
            return 'TRENDING'
        elif trending_score < 0.3:
            return 'RANGING'
        else:
            return 'TRANSITION'
    
    def generate_signal(self, symbol, data, indicators, regime):
        """Step 3: Generate trend following signal."""
        if regime != 'TRENDING':
            return None
            
        close = data['close'][-1]
        score = 0
        direction = None
        
        # Evaluate LONG signals
        long_score = 0
        if indicators['ema_fast'][-1] > indicators['ema_slow'][-1]:
            long_score += 0.20
            if indicators['ema_fast'][-2] <= indicators['ema_slow'][-2]:
                long_score += 0.10  # Fresh crossover bonus
        if close > indicators['don_upper'][-2]:  # Breakout
            long_score += 0.25
        if indicators['adx'][-1] > 25 and indicators['plus_di'][-1] > indicators['minus_di'][-1]:
            long_score += 0.20
        if indicators['st_direction'][-1] == 1:  # Bullish
            long_score += 0.15
        if close > indicators['ema_200'][-1]:
            long_score += 0.10
            
        # Evaluate SHORT signals
        short_score = 0
        if indicators['ema_fast'][-1] < indicators['ema_slow'][-1]:
            short_score += 0.20
            if indicators['ema_fast'][-2] >= indicators['ema_slow'][-2]:
                short_score += 0.10
        if close < indicators['don_lower'][-2]:
            short_score += 0.25
        if indicators['adx'][-1] > 25 and indicators['minus_di'][-1] > indicators['plus_di'][-1]:
            short_score += 0.20
        if indicators['st_direction'][-1] == -1:  # Bearish
            short_score += 0.15
        if close < indicators['ema_200'][-1]:
            short_score += 0.10
        
        # Select direction
        if long_score >= 0.60 and long_score > short_score:
            direction = 'LONG'
            score = long_score
        elif short_score >= 0.60 and short_score > long_score:
            direction = 'SHORT'
            score = short_score
        else:
            return None
            
        atr = indicators['atr'][-1]
        stop_distance = self.config['stop_multiplier'] * atr
        
        return {
            'symbol': symbol,
            'direction': direction,
            'score': score,
            'entry': close,
            'stop': close - stop_distance if direction == 'LONG' else close + stop_distance,
            'atr': atr,
        }
    
    def calculate_position_size(self, signal):
        """Step 4: ATR-based position sizing."""
        risk_amount = self.current_equity * self.config['risk_per_trade']
        stop_distance = abs(signal['entry'] - signal['stop'])
        dollar_per_point = self.get_dollar_per_point(signal['symbol'])
        
        position_size = risk_amount / (stop_distance * dollar_per_point)
        
        # Check portfolio heat limits
        new_heat = self.portfolio_heat + risk_amount
        if new_heat > self.current_equity * self.config['max_portfolio_heat']:
            position_size *= (self.current_equity * self.config['max_portfolio_heat'] - self.portfolio_heat) / risk_amount
        
        # Drawdown adjustment
        dd = (self.peak_equity - self.current_equity) / self.peak_equity
        if dd > 0.10:
            position_size *= 0.50
        elif dd > 0.05:
            position_size *= 0.75
            
        return max(0, position_size)
    
    def manage_positions(self, current_data, indicators):
        """Step 5: Manage open positions — trailing stops and exits."""
        for symbol, pos in list(self.positions.items()):
            close = current_data[symbol]['close'][-1]
            atr = indicators[symbol]['atr'][-1]
            
            # Update trailing stop
            if self.config['trail_method'] == 'atr':
                if pos['direction'] == 'LONG':
                    new_trail = close - self.config['trail_multiplier'] * atr
                    pos['trail_stop'] = max(pos.get('trail_stop', pos['stop']), new_trail)
                else:
                    new_trail = close + self.config['trail_multiplier'] * atr
                    pos['trail_stop'] = min(pos.get('trail_stop', pos['stop']), new_trail)
                    
            elif self.config['trail_method'] == 'donchian':
                if pos['direction'] == 'LONG':
                    pos['trail_stop'] = indicators[symbol]['don_exit_lower'][-1]
                else:
                    pos['trail_stop'] = indicators[symbol]['don_exit_upper'][-1]
            
            # Check exit conditions
            should_exit = False
            reason = ""
            
            if pos['direction'] == 'LONG' and close < pos['trail_stop']:
                should_exit = True
                reason = "Trailing stop hit"
            elif pos['direction'] == 'SHORT' and close > pos['trail_stop']:
                should_exit = True
                reason = "Trailing stop hit"
            
            # Regime change exit
            regime = self.detect_regime(symbol, current_data[symbol], indicators[symbol])
            if regime == 'RANGING' and pos.get('bars_held', 0) > 5:
                should_exit = True
                reason = "Regime changed to ranging"
            
            if should_exit:
                self.close_position(symbol, close, reason)
                
            # Pyramiding check
            elif pos.get('num_units', 1) < self.config['max_units']:
                pyramid_interval = self.config['pyramid_interval_N'] * atr
                if pos['direction'] == 'LONG' and close > pos['last_add_price'] + pyramid_interval:
                    self.add_unit(symbol, close)
                elif pos['direction'] == 'SHORT' and close < pos['last_add_price'] - pyramid_interval:
                    self.add_unit(symbol, close)
    
    def run(self, data_feed):
        """Step 6: Main execution loop."""
        for timestamp, market_data in data_feed:
            all_indicators = {}
            all_regimes = {}
            all_signals = []
            
            # Calculate indicators and signals for all symbols
            for symbol in self.config['symbols']:
                data = market_data[symbol]
                indicators = self.calculate_indicators(symbol, data)
                regime = self.detect_regime(symbol, data, indicators)
                signal = self.generate_signal(symbol, data, indicators, regime)
                
                all_indicators[symbol] = indicators
                all_regimes[symbol] = regime
                if signal:
                    all_signals.append(signal)
            
            # Manage existing positions
            self.manage_positions(market_data, all_indicators)
            
            # Process new signals (sorted by score)
            all_signals.sort(key=lambda s: s['score'], reverse=True)
            
            for signal in all_signals:
                if signal['symbol'] not in self.positions:
                    size = self.calculate_position_size(signal)
                    if size > 0:
                        self.open_position(signal, size)
            
            # Update equity tracking
            self.update_equity(market_data)
            self.peak_equity = max(self.peak_equity, self.current_equity)
```

### 17.2 Execution Flow Diagram

```
┌───────────────────────────────────────────────┐
│      TREND FOLLOWING EXECUTION FLOW           │
├───────────────────────────────────────────────┤
│                                               │
│  1. DATA INGESTION                            │
│     ├─ Receive new bar for all symbols        │
│     └─ Update price history buffers           │
│                                               │
│  2. INDICATOR CALCULATION                     │
│     ├─ EMA Fast/Slow/200                      │
│     ├─ Donchian Channels (entry/exit)         │
│     ├─ ADX, +DI, -DI                         │
│     ├─ Supertrend                             │
│     ├─ ATR                                    │
│     └─ Parabolic SAR (optional)               │
│                                               │
│  3. REGIME DETECTION                          │
│     ├─ ADX threshold check                    │
│     ├─ Hurst exponent                         │
│     ├─ MA slope analysis                      │
│     └─ Classify: TRENDING / RANGING / TRANS   │
│                                               │
│  4. SIGNAL GENERATION                         │
│     ├─ Score MA crossover                     │
│     ├─ Score Donchian breakout                │
│     ├─ Score ADX + DI                         │
│     ├─ Score Supertrend direction             │
│     ├─ Compute composite score                │
│     └─ Generate signal if score >= 0.60       │
│                                               │
│  5. POSITION MANAGEMENT                       │
│     ├─ Update trailing stops                  │
│     ├─ Check exit conditions                  │
│     ├─ Pyramiding opportunities               │
│     └─ Portfolio heat monitoring              │
│                                               │
│  6. POSITION SIZING                           │
│     ├─ ATR-based sizing                       │
│     ├─ Drawdown adjustment                    │
│     ├─ Correlation check                      │
│     └─ Portfolio heat limit check             │
│                                               │
│  7. EXECUTION                                 │
│     ├─ Submit orders                          │
│     ├─ Confirm fills                          │
│     └─ Update position tracking               │
│                                               │
│  8. MONITORING & REPORTING                    │
│     ├─ P&L tracking                           │
│     ├─ Drawdown monitoring                    │
│     ├─ Regime dashboard                       │
│     └─ Performance attribution                │
│                                               │
└───────────────────────────────────────────────┘
```

---

## 18. References

### Academic Papers

1. **Jegadeesh, N., & Titman, S.** (1993). "Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency." *Journal of Finance*, 48(1), 65-91.
2. **Moskowitz, T.J., Ooi, Y.H., & Pedersen, L.H.** (2012). "Time Series Momentum." *Journal of Financial Economics*, 104(2), 228-250.
3. **Asness, C.S., Moskowitz, T.J., & Pedersen, L.H.** (2013). "Value and Momentum Everywhere." *Journal of Finance*, 68(3), 929-985.
4. **Barroso, P., & Santa-Clara, P.** (2015). "Momentum Has Its Moments." *Journal of Financial Economics*, 116(1), 111-120.
5. **Daniel, K., & Moskowitz, T.** (2016). "Momentum Crashes." *Journal of Financial Economics*, 122(2), 221-247.
6. **Fung, W., & Hsieh, D.A.** (2001). "The Risk in Hedge Fund Strategies: Theory and Evidence from Trend Followers." *Review of Financial Studies*, 14(2), 313-341.
7. **Brock, W., Lakonishok, J., & LeBaron, B.** (1992). "Simple Technical Trading Rules and the Stochastic Properties of Stock Returns." *Journal of Finance*, 47(5), 1731-1764.
8. **Okunev, J., & White, D.** (2003). "Do Momentum-Based Strategies Still Work in Foreign Currency Markets?" *Journal of Financial and Quantitative Analysis*, 38(2), 425-447.
9. **Liu, Y., Tsyvinski, A., & Wu, X.** (2019). "Common Risk Factors in Cryptocurrency." *NBER Working Paper 25882*.

### Practitioner Resources

10. **Antonacci, G.** (2014). *Dual Momentum Investing*. McGraw-Hill.
11. **Covel, M.** (2009). *Trend Following: How to Make a Fortune in Bull, Bear, and Black Swan Markets*. FT Press.
12. **Faith, C.** (2007). *Way of the Turtle*. McGraw-Hill. (Original Turtle Trading system.)
13. **Clenow, A.** (2013). *Following the Trend: Diversified Managed Futures Trading*. Wiley.
14. **Wilder, J.W.** (1978). *New Concepts in Technical Trading Systems*. Trend Research. (ADX, Parabolic SAR.)
15. **Kaufman, P.J.** (2013). *Trading Systems and Methods*. 5th Edition. Wiley.

### Mathematical References

16. **Hurst, H.E.** (1951). "Long-Term Storage Capacity of Reservoirs." *Transactions ASCE*, 116, 770-808.
17. **Hamilton, J.D.** (1989). "A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle." *Econometrica*, 57(2), 357-384. (HMM for regime detection.)

---

*This document is part of the Multi-Agent AI Trading System knowledge base. Momentum and trend following strategies are foundational alpha sources that complement mean reversion approaches. The key is proper regime detection to activate the appropriate strategy for current market conditions.*
