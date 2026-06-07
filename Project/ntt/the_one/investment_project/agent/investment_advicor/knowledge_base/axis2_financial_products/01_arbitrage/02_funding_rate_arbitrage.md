# Funding Rate Arbitrage (Cash-and-Carry) — Complete Strategy Documentation

> **Document Version:** 2.0
> **Last Updated:** 2026-04-12
> **Classification:** Core Knowledge Base — Axis 2: Financial Products
> **Strategy Type:** Near-Arbitrage (Low Risk, Delta-Neutral)
> **Markets:** Crypto (CeFi Perpetual Swaps)
> **Frequency:** Low-Frequency (position held hours to weeks)

---

## Table of Contents

1. [Core Logic — How Perpetual Swap Funding Rates Work](#1-core-logic--how-perpetual-swap-funding-rates-work)
2. [Delta Neutral Strategy — Detailed Explanation](#2-delta-neutral-strategy--detailed-explanation)
3. [Mathematical Framework](#3-mathematical-framework)
4. [APY Calculation from Funding Rates](#4-apy-calculation-from-funding-rates)
5. [Basis Risk Analysis](#5-basis-risk-analysis)
6. [Margin Requirements and Liquidation Risk](#6-margin-requirements-and-liquidation-risk)
7. [Cross-Exchange Funding Rate Arbitrage](#7-cross-exchange-funding-rate-arbitrage)
8. [Historical Funding Rate Analysis](#8-historical-funding-rate-analysis)
9. [Entry and Exit Conditions](#9-entry-and-exit-conditions)
10. [Complete Execution Flow](#10-complete-execution-flow)
11. [Risk Management](#11-risk-management)
12. [Position Sizing and Capital Allocation](#12-position-sizing-and-capital-allocation)
13. [References](#13-references)

---

## 1. Core Logic — How Perpetual Swap Funding Rates Work

### 1.1 What Is a Perpetual Swap?

A perpetual swap (also called a perpetual future or "perp") is a derivative contract that:
- Tracks the price of an underlying asset (e.g., BTC, ETH)
- Has **no expiration date** (unlike traditional futures)
- Uses a **funding rate mechanism** to anchor the contract price to the spot price
- Allows leverage (typically 1x to 125x)
- Settles in real-time (mark-to-market)

### 1.2 The Funding Rate Mechanism

The funding rate is a periodic payment between long and short position holders, designed to keep the perpetual swap price aligned with the spot price.

**Fundamental Logic:**

- When **perp price > spot price** (premium): Longs pay shorts (positive funding rate)
- When **perp price < spot price** (discount): Shorts pay longs (negative funding rate)

This mechanism creates an economic incentive:
- If perp is trading above spot, longs are penalized -> incentivizes closing longs or opening shorts -> drives perp price down toward spot
- If perp is trading below spot, shorts are penalized -> incentivizes closing shorts or opening longs -> drives perp price up toward spot

### 1.3 Funding Rate Calculation

**Standard Formula (Binance/Bybit/OKX):**

$$\text{Funding Rate} = \text{Premium Index} + \text{clamp}(\text{Interest Rate} - \text{Premium Index}, -0.05\%, +0.05\%)$$

Where:

$$\text{Premium Index} = \frac{\text{Mark Price} - \text{Index Price}}{\text{Index Price}}$$

$$\text{Interest Rate} = \frac{\text{Quote Interest Rate} - \text{Base Interest Rate}}{\text{Funding Interval}}$$

Typically: Interest Rate = 0.01% per 8 hours (0.03% per day) for most exchanges.

**Simplified:**

$$F = \text{clamp}\left(\frac{P_{perp} - P_{spot}}{P_{spot}}, -0.75\%, +0.75\%\right)$$

Most exchanges cap the funding rate at +/- 0.75% per 8-hour interval (some have higher caps during extreme volatility).

### 1.4 Funding Payment Calculation

$$\text{Funding Payment} = \text{Position Size} \times \text{Funding Rate}$$

- If Funding Rate > 0: Longs pay, Shorts receive
- If Funding Rate < 0: Shorts pay, Longs receive

**Payment Schedule:**
| Exchange | Frequency | Times (UTC) |
|----------|-----------|-------------|
| Binance | Every 8 hours | 00:00, 08:00, 16:00 |
| Bybit | Every 8 hours | 00:00, 08:00, 16:00 |
| OKX | Every 8 hours | 00:00, 08:00, 16:00 |
| dYdX | Every 1 hour | Hourly |
| Drift (Solana) | Continuous | Real-time |

### 1.5 What Creates Elevated Funding Rates?

Funding rates spike when there is an imbalance between long and short demand:

| Market Condition | Typical Funding Rate | Cause |
|-----------------|:-------------------:|-------|
| Extreme bull market | +0.1% to +0.3% per 8h | Excessive long leverage |
| Strong bull market | +0.03% to +0.1% per 8h | Moderate long bias |
| Neutral market | -0.01% to +0.01% per 8h | Balanced demand |
| Strong bear market | -0.1% to -0.03% per 8h | Moderate short bias |
| Extreme bear market | -0.3% to -0.1% per 8h | Excessive short leverage |
| Liquidation cascade | +/- 0.5% to 0.75% per 8h | Forced liquidations |

---

## 2. Delta Neutral Strategy — Detailed Explanation

### 2.1 The Core Concept

Funding rate arbitrage is a **delta-neutral** strategy that profits from funding payments without taking directional market exposure. The strategy simultaneously holds:
- A **spot** position (or equivalent)
- An **opposite perpetual swap** position of equal size

The two positions offset each other's price exposure (delta = 0), while the funding rate payments provide a steady income stream.

### 2.2 Strategy A: Long Spot + Short Perpetual (Positive Funding)

**When to use:** When funding rate is positive (perp price > spot price, bullish market sentiment).

```
┌─────────────────────────────────────────┐
│         LONG SPOT + SHORT PERP           │
│                                          │
│  Spot Exchange:    BUY 1 BTC @ $65,000   │
│  Perp Exchange:    SHORT 1 BTC @ $65,200 │
│                                          │
│  Net Delta: +1 BTC - 1 BTC = 0 BTC      │
│  Net Exposure: ZERO (market neutral)     │
│                                          │
│  Income: Receive funding every 8 hours   │
│  (because we are SHORT when funding > 0) │
└─────────────────────────────────────────┘
```

**P&L Components:**

1. **Funding income:** Receive funding payments (shorts receive when funding is positive)
2. **Basis P&L:** If perp-spot spread narrows, gain on convergence; if widens, temporary loss
3. **Spot interest:** Opportunity cost of capital locked in spot (could earn yield elsewhere)
4. **Fees:** Entry/exit trading fees, funding fee (exchange fee on funding payments)

**Step-by-Step Execution:**

```
1. Identify asset with persistently high positive funding rate
2. Buy the asset on spot market (or use existing holdings)
3. Open a short perpetual position of equal notional size
4. Hold the position, collecting funding payments every 8 hours
5. Monitor basis (perp-spot spread) for exit conditions
6. Close both positions when funding drops or basis shifts unfavorably
```

### 2.3 Strategy B: Short Spot (Margin) + Long Perpetual (Negative Funding)

**When to use:** When funding rate is negative (perp price < spot price, bearish sentiment).

```
┌─────────────────────────────────────────┐
│      SHORT SPOT + LONG PERP              │
│                                          │
│  Margin Account:   SHORT 1 BTC @ $65,000 │
│  Perp Exchange:    LONG 1 BTC @ $64,800  │
│                                          │
│  Net Delta: -1 BTC + 1 BTC = 0 BTC      │
│  Net Exposure: ZERO (market neutral)     │
│                                          │
│  Income: Receive funding every 8 hours   │
│  (because we are LONG when funding < 0)  │
└─────────────────────────────────────────┘
```

**Additional considerations for Strategy B:**
- Shorting spot requires margin borrowing (interest cost)
- Some exchanges don't allow spot shorting
- Alternative: Use inverse perpetual or quarterly futures as the spot hedge
- Borrow rate must be less than funding income for net profitability

### 2.4 Strategy C: Cross-Exchange Funding Arbitrage

**When to use:** When funding rates differ significantly across exchanges.

```
┌─────────────────────────────────────────┐
│   CROSS-EXCHANGE FUNDING ARBITRAGE       │
│                                          │
│  Exchange A:  LONG BTC perp              │
│               (funding = -0.02%)         │
│               → We RECEIVE funding       │
│                                          │
│  Exchange B:  SHORT BTC perp             │
│               (funding = +0.08%)         │
│               → We RECEIVE funding       │
│                                          │
│  Net Delta: +1 BTC - 1 BTC = 0 BTC      │
│  Income: 0.02% + 0.08% = 0.10% per 8h   │
└─────────────────────────────────────────┘
```

**Advantage:** Potentially higher yield (receive funding from both sides).
**Disadvantage:** Capital split across two exchanges (counterparty risk), higher margin requirements.

---

## 3. Mathematical Framework

### 3.1 Net P&L Formula

For Strategy A (Long Spot + Short Perp) over holding period $T$:

$$P\&L_{net} = \sum_{t=1}^{N} F_t \times Q \times P_t - C_{entry} - C_{exit} - C_{funding\_fee} - C_{opportunity}$$

Where:
- $F_t$ = funding rate at time $t$
- $Q$ = position quantity (in base asset units)
- $P_t$ = mark price at funding time $t$
- $N$ = number of funding intervals during holding period
- $C_{entry}$ = entry costs (trading fees for opening both legs)
- $C_{exit}$ = exit costs (trading fees for closing both legs)
- $C_{funding\_fee}$ = exchange fee on funding payments (some exchanges charge this)
- $C_{opportunity}$ = opportunity cost of locked capital

### 3.2 Entry Cost Calculation

$$C_{entry} = Q \times P_{spot} \times f_{spot} + Q \times P_{perp} \times f_{perp}$$

Where:
- $f_{spot}$ = spot trading fee rate (maker/taker)
- $f_{perp}$ = perpetual trading fee rate (maker/taker)

### 3.3 Annualized Yield Formula

$$APY = \left(\frac{\sum_{t=1}^{N} F_t}{N}\right) \times \frac{365 \times 24}{h} \times \frac{Q \times \bar{P}}{C_{total}} - \frac{C_{entry} + C_{exit}}{C_{total}} \times \frac{365}{T_{days}}$$

Where:
- $h$ = funding interval in hours (typically 8)
- $\bar{P}$ = average mark price during the period
- $C_{total}$ = total capital deployed (spot capital + margin for perp)
- $T_{days}$ = actual holding period in days

**Simplified APY (ignoring entry/exit costs):**

$$APY_{simple} = \bar{F} \times \frac{365 \times 3}{1} \times \frac{1}{L}$$

Where:
- $\bar{F}$ = average funding rate per 8-hour interval
- $3$ = number of funding intervals per day (for 8-hour funding)
- $L$ = leverage factor for capital efficiency: $L = \frac{C_{total}}{Q \times P}$

For $L = 1$ (fully collateralized): $APY = \bar{F} \times 1095$

For example, if average funding rate is 0.03% per 8 hours:

$$APY = 0.0003 \times 1095 = 0.3285 = 32.85\%$$

### 3.4 Capital Efficiency with Leverage

If you use leverage on the perpetual side:

$$C_{total} = Q \times P_{spot} + \frac{Q \times P_{perp}}{leverage}$$

For a position worth $Q \times P$ with leverage $\ell$ on the perp:

$$C_{total} = Q \times P \times \left(1 + \frac{1}{\ell}\right)$$

$$APY_{leveraged} = \frac{\bar{F} \times 1095 \times Q \times P}{Q \times P \times (1 + 1/\ell)} = \frac{\bar{F} \times 1095}{1 + 1/\ell}$$

**Example:** $\bar{F} = 0.03\%$, $\ell = 5x$

$$APY = \frac{0.0003 \times 1095}{1 + 0.2} = \frac{0.3285}{1.2} = 27.4\%$$

### 3.5 Break-Even Funding Rate

The minimum funding rate needed to cover entry/exit costs over the expected holding period:

$$F_{min} = \frac{(f_{spot} + f_{perp}) \times 2}{N_{expected}}$$

Where:
- Factor of 2: entry + exit costs
- $N_{expected}$ = expected number of funding intervals before exit

**Example:** Fees = 0.05% per side, expected holding = 7 days (21 intervals):

$$F_{min} = \frac{(0.0005 + 0.0005) \times 2}{21} = \frac{0.002}{21} = 0.0095\% \text{ per 8h}$$

This means you need an average funding rate of at least 0.0095% per 8 hours just to break even over 7 days.

### 3.6 Basis Dynamics Model

The basis is defined as:

$$B_t = P_{perp,t} - P_{spot,t}$$

Or in percentage terms:

$$b_t = \frac{P_{perp,t} - P_{spot,t}}{P_{spot,t}}$$

The basis affects P&L when entering/exiting because:

$$P\&L_{basis} = Q \times (B_{exit} - B_{entry})$$

For the long spot + short perp position:
- If $B_{exit} < B_{entry}$: basis converged → gain on basis
- If $B_{exit} > B_{entry}$: basis widened → loss on basis

**Basis mean-reversion model:**

$$b_t = \mu_b + \phi (b_{t-1} - \mu_b) + \epsilon_t$$

Where $\mu_b$ is the long-run mean basis, $\phi$ is the mean-reversion speed, and $\epsilon_t$ is noise.

---

## 4. APY Calculation from Funding Rates

### 4.1 Historical APY Calculation

Given a time series of historical funding rates $\{F_1, F_2, ..., F_N\}$:

**Simple annualization:**

$$APY_{historical} = \left(\prod_{t=1}^{N} (1 + F_t)\right)^{365 \times 3 / N} - 1$$

**Linear approximation (for small funding rates):**

$$APY_{historical} \approx \frac{\sum_{t=1}^{N} F_t}{N} \times 365 \times 3$$

### 4.2 Forward-Looking APY Estimation

Using a rolling window of recent funding rates:

$$APY_{estimated} = \text{EMA}(F_t, \alpha) \times 1095$$

Where $\alpha$ is the EMA smoothing parameter (e.g., $\alpha = 2/(n+1)$ for $n$-period EMA).

### 4.3 Risk-Adjusted APY

$$APY_{risk-adj} = APY_{gross} - C_{entry/exit} - C_{margin} - C_{liquidation\_risk} - C_{basis\_risk}$$

Where:
- $C_{entry/exit}$: Annualized trading costs based on expected turnover
- $C_{margin}$: Cost of margin capital (could earn risk-free rate elsewhere)
- $C_{liquidation\_risk}$: Expected loss from liquidation events (probability * loss given liquidation)
- $C_{basis\_risk}$: Expected loss from basis movements

### 4.4 APY by Asset — Historical Ranges

| Asset | Typical APY (Bull) | Typical APY (Neutral) | Typical APY (Bear) |
|-------|:------------------:|:---------------------:|:------------------:|
| BTC | 15-40% | 5-15% | -5% to 5% (negative funding) |
| ETH | 20-50% | 8-20% | -5% to 8% |
| SOL | 25-80% | 10-30% | -10% to 10% |
| DOGE | 30-100%+ | 5-25% | -20% to 5% |
| High-volatility alts | 50-200%+ | 10-50% | -30% to 10% |

Note: These are illustrative ranges. Actual rates vary significantly by market conditions.

---

## 5. Basis Risk Analysis

### 5.1 What Is Basis Risk?

Basis risk in funding rate arbitrage is the risk that the spread between the perpetual price and spot price changes adversely during the holding period.

**Sources of basis movement:**

1. **Sudden demand shifts:** Large directional bets can push perp premium sharply
2. **Liquidation cascades:** Mass liquidations compress or expand basis rapidly
3. **Funding rate changes:** As funding adjusts, basis may shift
4. **Market structure breaks:** Exchange issues, halts, or API problems

### 5.2 Quantifying Basis Risk

**Basis volatility:**

$$\sigma_b = \text{std}(b_t - b_{t-1})$$

**Value at Risk (VaR) from basis movement:**

$$VaR_{basis} = Q \times P \times z_{\alpha} \times \sigma_b \times \sqrt{T}$$

Where:
- $z_{\alpha}$ = z-score for confidence level (e.g., 2.33 for 99% VaR)
- $T$ = holding period in funding intervals

**Example:** $Q \times P = \$100,000$, $\sigma_b = 0.5\%$ per 8h, $z_{0.99} = 2.33$, $T = 1$ interval:

$$VaR_{basis} = 100,000 \times 2.33 \times 0.005 = \$1,165$$

### 5.3 Basis Scenarios

| Scenario | Basis Change | Impact on Strategy A (Long Spot + Short Perp) |
|----------|:------------:|:----------------------------------------------:|
| Bull euphoria | Basis widens (+2%) | Unrealized loss on short perp (-$2,000 per $100K) |
| Bull momentum | Basis widens (+0.5%) | Minor unrealized loss (-$500 per $100K) |
| Neutral | Basis stable (0%) | No impact |
| Profit taking | Basis narrows (-0.5%) | Unrealized gain (+$500 per $100K) |
| Crash/liquidation | Basis narrows sharply (-3%) | Unrealized gain (+$3,000 per $100K) |
| Flash crash + recovery | Basis swings wildly | Risk of margin call during the spike |

### 5.4 Basis Risk Mitigation

1. **Monitor basis in real-time:** Set alerts for abnormal basis widening
2. **Maintain excess margin:** Keep margin well above maintenance level
3. **Size positions conservatively:** Don't maximize leverage
4. **Set conditional exit orders:** Close if basis exceeds threshold
5. **Diversify across assets:** Different assets have uncorrelated basis movements
6. **Use limit orders for entry:** Enter when basis is near mean, not at extremes

---

## 6. Margin Requirements and Liquidation Risk

### 6.1 Margin Mechanics

For the perpetual swap leg, margin requirements are:

$$\text{Initial Margin} = \frac{\text{Position Notional}}{\text{Leverage}}$$

$$\text{Maintenance Margin} = \text{Position Notional} \times \text{MMR}$$

Where MMR = Maintenance Margin Rate (varies by exchange and position size):

| Exchange | BTC MMR (< $1M) | BTC MMR ($1M-5M) | BTC MMR (> $5M) |
|----------|:----------------:|:-----------------:|:----------------:|
| Binance | 0.40% | 0.50% | 1.00% |
| Bybit | 0.50% | 0.55% | 1.00% |
| OKX | 0.40% | 0.60% | 1.50% |

### 6.2 Liquidation Price Calculation

For a **short** perpetual position:

$$P_{liquidation} = P_{entry} \times \left(1 + \frac{\text{Margin Balance} - \text{Maintenance Margin}}{\text{Position Size} \times P_{entry}}\right)$$

**Simplified (for isolated margin):**

$$P_{liq}^{short} = P_{entry} \times \frac{1}{1 - \frac{1}{leverage} + MMR}$$

Wait, more precisely for a short:

$$P_{liq}^{short} = P_{entry} \times \left(1 + \frac{1}{leverage} - MMR\right)$$

**Example:** Short BTC at $65,000, 5x leverage, MMR = 0.5%:

$$P_{liq}^{short} = 65,000 \times (1 + 0.20 - 0.005) = 65,000 \times 1.195 = \$77,675$$

This means BTC would need to rise ~19.5% before liquidation. Combined with the spot hedge:
- Spot position gains offset perp losses
- BUT: if capital is on different exchanges, you can't instantly move it

### 6.3 Liquidation Risk in Delta-Neutral Context

**Key insight:** Even in a delta-neutral position, liquidation can occur because:
- The spot gain and perp loss are on **separate accounts/exchanges**
- You cannot use spot gains to cover perp margin in real-time
- The perp can be liquidated even while the spot offsets the loss overall

**Critical calculation — Maximum adverse move before liquidation:**

$$\Delta P_{max} = P_{entry} \times \left(\frac{1}{leverage} - MMR\right)$$

$$\Delta P_{max}\% = \frac{1}{leverage} - MMR$$

| Leverage | MMR (0.5%) | Max Move Before Liquidation |
|:--------:|:----------:|:---------------------------:|
| 2x | 0.5% | 49.5% |
| 3x | 0.5% | 32.8% |
| 5x | 0.5% | 19.5% |
| 10x | 0.5% | 9.5% |
| 20x | 0.5% | 4.5% |

**Recommendation:** Use 2-5x leverage for funding rate arbitrage. This provides 20-50% buffer before liquidation, which is sufficient for most market conditions (BTC has only moved >20% in a single day a handful of times in its history).

### 6.4 Auto-Deleverage (ADL) Risk

Some exchanges have an Auto-Deleverage (ADL) mechanism that can force-close profitable positions during extreme market conditions:

- ADL occurs when the insurance fund is depleted
- Profitable traders are ranked and the highest-ranking ones have positions closed first
- In funding rate arb: if your short perp is highly profitable (market crashed), you may be ADL'd
- This removes your hedge, leaving you with an unhedged spot long

**Mitigation:**
- Monitor ADL indicator (most exchanges show a ranked indicator)
- Reduce position size when ADL risk is elevated
- Spread across multiple exchanges

---

## 7. Cross-Exchange Funding Rate Arbitrage

### 7.1 Strategy Description

Different exchanges often quote different funding rates for the same asset due to:
- Different user bases (retail vs. institutional)
- Different position limits and leverage offered
- Different calculation methodologies
- Different market makers

**Exploit:** Go long on the exchange with lower (or negative) funding and short on the exchange with higher (or positive) funding. Collect the differential.

### 7.2 Funding Rate Differentials

**Typical funding rate spread between exchanges (BTC, per 8h):**

| Market Condition | Binance | Bybit | Differential |
|-----------------|:-------:|:-----:|:------------:|
| Bull market | +0.05% | +0.08% | 0.03% |
| Neutral | +0.01% | +0.02% | 0.01% |
| Volatile | +0.10% | +0.15% | 0.05% |
| Extreme | +0.20% | +0.40% | 0.20% |

### 7.3 Capital Requirements

For cross-exchange funding arbitrage, capital must be deployed on both exchanges:

$$C_{total} = \frac{Q \times P}{leverage_A} + \frac{Q \times P}{leverage_B}$$

**Example:** $100K notional on each side, 5x leverage on each:

$$C_{total} = \frac{100,000}{5} + \frac{100,000}{5} = \$40,000$$

**Yield on deployed capital:**

$$APY = \frac{(F_B - F_A) \times 1095 \times Q \times P}{C_{total}}$$

Where $F_B$ = funding rate on the short side, $F_A$ = funding rate on the long side.

### 7.4 Cross-Exchange Risks

1. **Counterparty risk:** Capital exposed to TWO exchanges
2. **Liquidation risk on both sides:** In extreme moves, one side may face liquidation
3. **Funding rate convergence:** Spreads may narrow, eliminating profit
4. **Capital fragmentation:** Cannot easily move capital between exchanges
5. **Asymmetric moves:** If one exchange has an API issue or halt while the other doesn't

---

## 8. Historical Funding Rate Analysis

### 8.1 Analysis Methodology

```python
import pandas as pd
import numpy as np
from scipy import stats

class FundingRateAnalyzer:
    """
    Analyze historical funding rates to assess viability of funding rate arbitrage.
    """
    
    def __init__(self, funding_data: pd.DataFrame):
        """
        Args:
            funding_data: DataFrame with columns ['timestamp', 'symbol', 'funding_rate']
        """
        self.data = funding_data
    
    def calculate_statistics(self, symbol: str) -> dict:
        """Calculate comprehensive statistics for a given symbol."""
        rates = self.data[self.data['symbol'] == symbol]['funding_rate']
        
        return {
            'mean': rates.mean(),
            'median': rates.median(),
            'std': rates.std(),
            'skew': rates.skew(),
            'kurtosis': rates.kurtosis(),
            'min': rates.min(),
            'max': rates.max(),
            'pct_positive': (rates > 0).mean(),
            'pct_negative': (rates < 0).mean(),
            'mean_when_positive': rates[rates > 0].mean(),
            'mean_when_negative': rates[rates < 0].mean(),
            'annualized_yield': rates.mean() * 1095,
            'annualized_vol': rates.std() * np.sqrt(1095),
            'sharpe': (rates.mean() * 1095) / (rates.std() * np.sqrt(1095)),
        }
    
    def calculate_rolling_apy(self, symbol: str, window: int = 30) -> pd.Series:
        """Calculate rolling APY using a window of N funding intervals."""
        rates = self.data[self.data['symbol'] == symbol]['funding_rate']
        rolling_mean = rates.rolling(window).mean()
        return rolling_mean * 1095
    
    def calculate_persistence(self, symbol: str) -> dict:
        """
        Analyze persistence of funding rate sign.
        How many consecutive intervals is funding positive/negative?
        """
        rates = self.data[self.data['symbol'] == symbol]['funding_rate']
        signs = np.sign(rates)
        
        # Calculate run lengths
        runs = []
        current_run = 1
        for i in range(1, len(signs)):
            if signs.iloc[i] == signs.iloc[i-1]:
                current_run += 1
            else:
                runs.append((signs.iloc[i-1], current_run))
                current_run = 1
        runs.append((signs.iloc[-1], current_run))
        
        positive_runs = [r[1] for r in runs if r[0] > 0]
        negative_runs = [r[1] for r in runs if r[0] < 0]
        
        return {
            'avg_positive_run': np.mean(positive_runs) if positive_runs else 0,
            'max_positive_run': max(positive_runs) if positive_runs else 0,
            'avg_negative_run': np.mean(negative_runs) if negative_runs else 0,
            'max_negative_run': max(negative_runs) if negative_runs else 0,
            'autocorrelation_lag1': rates.autocorr(lag=1),
            'autocorrelation_lag3': rates.autocorr(lag=3),
        }
    
    def optimal_entry_threshold(self, symbol: str, holding_periods: list = [7, 14, 30]) -> dict:
        """
        Backtest different entry thresholds to find optimal.
        
        Entry threshold: only enter when funding rate > threshold
        """
        rates = self.data[self.data['symbol'] == symbol]['funding_rate'].values
        results = {}
        
        for period in holding_periods:
            thresholds = np.arange(0, 0.001, 0.00005)  # 0 to 10 bps
            period_results = []
            
            for threshold in thresholds:
                yields = []
                for i in range(len(rates) - period):
                    if rates[i] > threshold:
                        # Simulate holding for 'period' intervals
                        hold_yield = sum(rates[i:i+period])
                        yields.append(hold_yield)
                
                if yields:
                    avg_yield = np.mean(yields)
                    win_rate = sum(1 for y in yields if y > 0) / len(yields)
                    num_trades = len(yields)
                else:
                    avg_yield = 0
                    win_rate = 0
                    num_trades = 0
                
                period_results.append({
                    'threshold': threshold,
                    'avg_yield': avg_yield,
                    'win_rate': win_rate,
                    'num_trades': num_trades,
                    'annualized': avg_yield * (1095 / period),
                })
            
            results[f'{period}_intervals'] = period_results
        
        return results
    
    def regime_detection(self, symbol: str) -> pd.DataFrame:
        """
        Detect funding rate regimes using Hidden Markov Model or threshold-based approach.
        """
        rates = self.data[self.data['symbol'] == symbol]['funding_rate']
        
        # Simple threshold-based regime detection
        conditions = [
            rates > 0.0005,           # High positive
            (rates > 0.0001) & (rates <= 0.0005),  # Moderate positive
            (rates >= -0.0001) & (rates <= 0.0001), # Neutral
            (rates >= -0.0005) & (rates < -0.0001), # Moderate negative
            rates < -0.0005,          # High negative
        ]
        choices = ['high_positive', 'moderate_positive', 'neutral', 
                   'moderate_negative', 'high_negative']
        
        regimes = np.select(conditions, choices, default='neutral')
        
        return pd.DataFrame({
            'timestamp': self.data[self.data['symbol'] == symbol]['timestamp'],
            'funding_rate': rates,
            'regime': regimes
        })
```

### 8.2 Key Statistical Metrics to Monitor

1. **Mean reversion tendency:** Do elevated funding rates persist or quickly revert?
2. **Autocorrelation:** High positive autocorrelation means persistence (good for this strategy)
3. **Regime shifts:** How quickly does funding transition from positive to negative?
4. **Tail risk:** How extreme can funding get? (Liquidation risk during spikes)
5. **Cross-asset correlation:** Do all assets have correlated funding spikes?

---

## 9. Entry and Exit Conditions

### 9.1 Entry Conditions

```python
ENTRY_CONDITIONS = {
    # Primary condition: Funding rate must exceed threshold
    "min_funding_rate": 0.0003,          # 3 bps per 8h (annualized ~33%)
    
    # Confirmation: Recent average should also be high
    "min_avg_funding_24h": 0.0002,       # Average over last 3 intervals
    
    # Market structure checks
    "max_basis_pct": 0.005,              # Don't enter if basis > 0.5%
    "min_open_interest_usd": 100_000_000, # Minimum OI for liquidity
    
    # Volatility check
    "max_1h_volatility": 0.03,           # Don't enter during extreme volatility
    
    # Order book check
    "min_book_depth_usd": 500_000,       # Minimum depth at best 5 levels
    
    # Exchange health
    "max_api_latency_ms": 500,           # API must be responsive
    "exchange_status": "operational",     # No maintenance or issues
    
    # Position limits
    "max_position_per_asset_usd": 200_000,
    "max_total_funding_exposure_usd": 1_000_000,
}
```

### 9.2 Exit Conditions

```python
EXIT_CONDITIONS = {
    # Funding rate reversal
    "exit_if_funding_below": 0.0001,     # Exit if funding drops below 1 bps
    "exit_if_funding_negative": True,     # Exit immediately if funding flips
    "exit_on_consecutive_low": 3,        # Exit after 3 consecutive low fundings
    
    # Basis risk
    "exit_if_basis_widens_pct": 0.01,    # Exit if basis widens by 1%
    "exit_if_basis_exceeds_pct": 0.02,   # Exit if absolute basis > 2%
    
    # Profit taking
    "take_profit_pct": 0.05,             # Take profit at 5% return
    "min_holding_periods": 6,            # Minimum hold: 6 intervals (2 days)
    
    # Stop loss
    "max_unrealized_loss_pct": 0.03,     # Stop if unrealized loss > 3%
    "max_basis_loss_usd": 5_000,         # Absolute dollar stop
    
    # Time-based
    "max_holding_days": 30,              # Maximum holding period
    
    # Risk-based
    "exit_if_liquidation_distance_pct": 0.10, # Exit if within 10% of liquidation
    "exit_on_high_volatility": 0.05,     # Exit if 1h vol exceeds 5%
}
```

### 9.3 Decision Flow

```
ENTRY DECISION:
    IF funding_rate > min_funding_rate
    AND avg_funding_24h > min_avg_funding_24h
    AND basis < max_basis_pct
    AND open_interest > min_open_interest
    AND volatility < max_1h_volatility
    AND position_within_limits
    AND exchange_healthy
    → ENTER POSITION

EXIT DECISION:
    IF funding_rate < exit_if_funding_below (for N consecutive intervals)
    OR funding_rate < 0 (immediate exit)
    OR basis_change > exit_if_basis_widens_pct
    OR unrealized_loss > max_unrealized_loss_pct
    OR holding_period > max_holding_days
    OR liquidation_distance < exit_if_liquidation_distance_pct
    OR volatility > exit_on_high_volatility
    → EXIT POSITION
```

---

## 10. Complete Execution Flow

### 10.1 Full Strategy Pseudocode

```python
import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum

# ============================================================
# DATA STRUCTURES
# ============================================================

class PositionStatus(Enum):
    NONE = "NONE"
    ENTERING = "ENTERING"
    ACTIVE = "ACTIVE"
    EXITING = "EXITING"

@dataclass
class FundingPosition:
    symbol: str
    direction: str                  # "LONG_SPOT_SHORT_PERP" or "SHORT_SPOT_LONG_PERP"
    spot_qty: float
    perp_qty: float
    spot_entry_price: float
    perp_entry_price: float
    entry_time: float
    entry_funding_rate: float
    total_funding_received: float = 0.0
    funding_payments: List[float] = field(default_factory=list)
    status: PositionStatus = PositionStatus.ACTIVE
    
    @property
    def notional_value(self) -> float:
        return self.spot_qty * self.spot_entry_price
    
    @property
    def entry_basis(self) -> float:
        return (self.perp_entry_price - self.spot_entry_price) / self.spot_entry_price

@dataclass
class FundingArbConfig:
    # Strategy parameters
    target_assets: List[str]             # e.g., ["BTC", "ETH", "SOL"]
    
    # Entry thresholds
    min_funding_rate: float = 0.0003     # 3 bps per interval
    min_avg_funding: float = 0.0002      # Average over lookback
    funding_lookback_intervals: int = 6  # 2 days at 8h intervals
    max_entry_basis_pct: float = 0.005   # Max basis at entry
    
    # Position sizing
    position_size_usd: float = 50_000    # Per-asset position size
    max_total_exposure_usd: float = 500_000
    perp_leverage: float = 3.0           # Conservative leverage
    
    # Exit thresholds
    min_exit_funding: float = 0.0001
    max_basis_widening_pct: float = 0.01
    max_holding_days: float = 30
    stop_loss_pct: float = 0.03
    
    # Fees
    spot_fee: float = 0.001              # 10 bps
    perp_fee: float = 0.0005             # 5 bps (maker)
    
    # Risk
    min_liquidation_buffer_pct: float = 0.15  # 15% distance to liquidation
    max_position_per_asset_pct: float = 0.30  # Max 30% in one asset

# ============================================================
# MAIN ENGINE
# ============================================================

class FundingRateArbitrageEngine:
    """
    Complete funding rate arbitrage engine.
    
    Strategy: Collect funding payments via delta-neutral positions.
    - Long Spot + Short Perp when funding is positive
    - Track P&L including funding income, basis P&L, and costs
    """
    
    def __init__(self, config: FundingArbConfig, spot_exchange, perp_exchange, data_feed):
        self.config = config
        self.spot_exchange = spot_exchange
        self.perp_exchange = perp_exchange
        self.data_feed = data_feed
        
        # State
        self.positions: Dict[str, FundingPosition] = {}
        self.funding_history: Dict[str, List[float]] = {}
        self.total_pnl: float = 0.0
        self.is_running: bool = False
    
    # ----------------------------------------------------------
    # MAIN LOOP
    # ----------------------------------------------------------
    
    async def run(self):
        """Main strategy loop."""
        self.is_running = True
        
        # Initialize data feeds
        await self.initialize()
        
        while self.is_running:
            try:
                # Update market data
                await self.update_market_data()
                
                # Check existing positions
                for symbol in list(self.positions.keys()):
                    position = self.positions[symbol]
                    
                    # Check exit conditions
                    if self.should_exit(symbol, position):
                        await self.exit_position(symbol, position)
                    
                    # Update funding received
                    await self.process_funding_payment(symbol, position)
                
                # Check for new entry opportunities
                for symbol in self.config.target_assets:
                    if symbol not in self.positions:
                        if self.should_enter(symbol):
                            await self.enter_position(symbol)
                
                # Monitor margin and liquidation risk
                await self.monitor_risk()
                
                # Sleep until next check (every minute is sufficient)
                await asyncio.sleep(60)
                
            except Exception as e:
                self.handle_error(e)
    
    # ----------------------------------------------------------
    # MARKET DATA
    # ----------------------------------------------------------
    
    async def initialize(self):
        """Initialize connections and load historical funding data."""
        # Load historical funding rates for all target assets
        for symbol in self.config.target_assets:
            history = await self.data_feed.get_funding_history(
                symbol, limit=self.config.funding_lookback_intervals * 10
            )
            self.funding_history[symbol] = history
    
    async def update_market_data(self):
        """Update current funding rates and prices."""
        for symbol in self.config.target_assets:
            # Get current predicted funding rate
            current_funding = await self.data_feed.get_current_funding_rate(symbol)
            self.funding_history.setdefault(symbol, []).append(current_funding)
    
    # ----------------------------------------------------------
    # ENTRY LOGIC
    # ----------------------------------------------------------
    
    def should_enter(self, symbol: str) -> bool:
        """Determine if we should enter a funding rate arbitrage position."""
        
        # Check position limits
        total_exposure = sum(p.notional_value for p in self.positions.values())
        if total_exposure >= self.config.max_total_exposure_usd:
            return False
        
        # Get current funding rate
        history = self.funding_history.get(symbol, [])
        if not history:
            return False
        
        current_rate = history[-1]
        
        # Condition 1: Current funding rate exceeds minimum
        if abs(current_rate) < self.config.min_funding_rate:
            return False
        
        # Condition 2: Average funding over lookback exceeds minimum
        lookback = history[-self.config.funding_lookback_intervals:]
        avg_rate = sum(lookback) / len(lookback) if lookback else 0
        
        if abs(avg_rate) < self.config.min_avg_funding:
            return False
        
        # Condition 3: Basis check
        basis = self.get_current_basis(symbol)
        if abs(basis) > self.config.max_entry_basis_pct:
            return False
        
        # Condition 4: Liquidity check (open interest)
        # ... (implementation depends on exchange API)
        
        return True
    
    async def enter_position(self, symbol: str):
        """
        Enter a funding rate arbitrage position.
        
        Steps:
        1. Determine direction based on funding rate sign
        2. Calculate position size
        3. Execute spot leg
        4. Execute perp leg
        5. Record position
        """
        current_rate = self.funding_history[symbol][-1]
        
        # Determine direction
        if current_rate > 0:
            direction = "LONG_SPOT_SHORT_PERP"
        else:
            direction = "SHORT_SPOT_LONG_PERP"
        
        # Get current prices
        spot_price = await self.spot_exchange.get_price(symbol)
        perp_price = await self.perp_exchange.get_price(symbol)
        
        # Calculate quantity
        quantity = self.config.position_size_usd / spot_price
        
        try:
            if direction == "LONG_SPOT_SHORT_PERP":
                # Leg 1: Buy spot
                spot_fill = await self.spot_exchange.market_buy(
                    symbol=f"{symbol}/USDT",
                    quantity=quantity
                )
                
                # Leg 2: Short perpetual
                perp_fill = await self.perp_exchange.market_sell(
                    symbol=f"{symbol}/USDT:PERP",
                    quantity=quantity,
                    leverage=self.config.perp_leverage
                )
            else:
                # Leg 1: Sell spot (margin short)
                spot_fill = await self.spot_exchange.margin_sell(
                    symbol=f"{symbol}/USDT",
                    quantity=quantity
                )
                
                # Leg 2: Long perpetual
                perp_fill = await self.perp_exchange.market_buy(
                    symbol=f"{symbol}/USDT:PERP",
                    quantity=quantity,
                    leverage=self.config.perp_leverage
                )
            
            # Record position
            self.positions[symbol] = FundingPosition(
                symbol=symbol,
                direction=direction,
                spot_qty=spot_fill['filled_qty'],
                perp_qty=perp_fill['filled_qty'],
                spot_entry_price=spot_fill['avg_price'],
                perp_entry_price=perp_fill['avg_price'],
                entry_time=time.time(),
                entry_funding_rate=current_rate,
                status=PositionStatus.ACTIVE
            )
            
            self.log_entry(symbol, self.positions[symbol])
            
        except Exception as e:
            # Handle partial execution
            await self.handle_entry_failure(symbol, direction, e)
    
    # ----------------------------------------------------------
    # FUNDING PAYMENT PROCESSING
    # ----------------------------------------------------------
    
    async def process_funding_payment(self, symbol: str, position: FundingPosition):
        """
        Check and record funding payments.
        Called periodically to track accumulated funding.
        """
        # Query exchange for recent funding payments
        recent_payments = await self.perp_exchange.get_funding_payments(
            symbol=f"{symbol}/USDT:PERP",
            since=position.entry_time
        )
        
        # Calculate new payments since last check
        known_payments = len(position.funding_payments)
        new_payments = recent_payments[known_payments:]
        
        for payment in new_payments:
            position.funding_payments.append(payment['amount'])
            position.total_funding_received += payment['amount']
            
            self.log_funding(symbol, payment)
    
    # ----------------------------------------------------------
    # EXIT LOGIC
    # ----------------------------------------------------------
    
    def should_exit(self, symbol: str, position: FundingPosition) -> bool:
        """Determine if we should exit the position."""
        
        # Condition 1: Funding rate dropped below minimum
        history = self.funding_history.get(symbol, [])
        if history:
            recent_rates = history[-3:]  # Last 3 intervals
            avg_recent = sum(recent_rates) / len(recent_rates)
            
            if position.direction == "LONG_SPOT_SHORT_PERP":
                if avg_recent < self.config.min_exit_funding:
                    return True
                if history[-1] < 0:  # Funding flipped negative
                    return True
            else:
                if avg_recent > -self.config.min_exit_funding:
                    return True
                if history[-1] > 0:  # Funding flipped positive
                    return True
        
        # Condition 2: Basis widened too much
        current_basis = self.get_current_basis(symbol)
        basis_change = abs(current_basis - position.entry_basis)
        if basis_change > self.config.max_basis_widening_pct:
            return True
        
        # Condition 3: Maximum holding period
        holding_days = (time.time() - position.entry_time) / 86400
        if holding_days > self.config.max_holding_days:
            return True
        
        # Condition 4: Stop loss
        unrealized_pnl = self.calculate_unrealized_pnl(symbol, position)
        unrealized_pct = unrealized_pnl / position.notional_value
        if unrealized_pct < -self.config.stop_loss_pct:
            return True
        
        # Condition 5: Liquidation proximity
        liquidation_distance = self.get_liquidation_distance(symbol, position)
        if liquidation_distance < self.config.min_liquidation_buffer_pct:
            return True
        
        return False
    
    async def exit_position(self, symbol: str, position: FundingPosition):
        """
        Close both legs of the position.
        """
        position.status = PositionStatus.EXITING
        
        try:
            if position.direction == "LONG_SPOT_SHORT_PERP":
                # Close spot: sell
                spot_close = await self.spot_exchange.market_sell(
                    symbol=f"{symbol}/USDT",
                    quantity=position.spot_qty
                )
                
                # Close perp: buy to cover
                perp_close = await self.perp_exchange.market_buy(
                    symbol=f"{symbol}/USDT:PERP",
                    quantity=position.perp_qty,
                    reduce_only=True
                )
            else:
                # Close margin short: buy to cover
                spot_close = await self.spot_exchange.margin_buy(
                    symbol=f"{symbol}/USDT",
                    quantity=position.spot_qty
                )
                
                # Close perp long: sell
                perp_close = await self.perp_exchange.market_sell(
                    symbol=f"{symbol}/USDT:PERP",
                    quantity=position.perp_qty,
                    reduce_only=True
                )
            
            # Calculate final P&L
            final_pnl = self.calculate_final_pnl(
                position, spot_close, perp_close
            )
            
            self.total_pnl += final_pnl
            self.log_exit(symbol, position, final_pnl)
            
            # Remove position
            del self.positions[symbol]
            
        except Exception as e:
            self.handle_exit_failure(symbol, position, e)
    
    # ----------------------------------------------------------
    # RISK MONITORING
    # ----------------------------------------------------------
    
    async def monitor_risk(self):
        """
        Continuous risk monitoring for all positions.
        """
        for symbol, position in self.positions.items():
            # Check margin ratio
            margin_ratio = await self.perp_exchange.get_margin_ratio(
                f"{symbol}/USDT:PERP"
            )
            
            if margin_ratio < 0.1:  # Less than 10% margin ratio
                self.log_warning(
                    f"LOW MARGIN: {symbol} margin ratio = {margin_ratio:.4f}"
                )
                # Add margin or reduce position
                await self.add_margin_or_reduce(symbol, position)
            
            # Check for exchange anomalies
            spread = await self.check_exchange_spread(symbol)
            if spread > 0.02:  # 2% spread indicates issues
                self.log_warning(f"ABNORMAL SPREAD: {symbol} = {spread:.4f}")
    
    async def add_margin_or_reduce(self, symbol: str, position: FundingPosition):
        """Add margin to avoid liquidation or reduce position size."""
        # Strategy: Add margin from spot profits if available
        available_margin = await self.perp_exchange.get_available_balance()
        
        if available_margin > position.notional_value * 0.05:
            # Add 5% of notional as additional margin
            await self.perp_exchange.add_margin(
                symbol=f"{symbol}/USDT:PERP",
                amount=position.notional_value * 0.05
            )
        else:
            # Reduce position by 50%
            await self.reduce_position(symbol, position, 0.5)
    
    # ----------------------------------------------------------
    # P&L CALCULATIONS
    # ----------------------------------------------------------
    
    def calculate_unrealized_pnl(self, symbol: str, position: FundingPosition) -> float:
        """Calculate current unrealized P&L including funding received."""
        # This would use current market prices
        # Simplified: funding_received + basis_pnl - fees
        
        total_funding = position.total_funding_received
        
        # Basis P&L (for long spot + short perp, gain if basis narrows)
        current_basis = self.get_current_basis(symbol)
        basis_pnl = (position.entry_basis - current_basis) * position.notional_value
        
        # Entry costs
        entry_costs = position.notional_value * (self.config.spot_fee + self.config.perp_fee)
        
        return total_funding + basis_pnl - entry_costs
    
    def calculate_final_pnl(self, position, spot_close, perp_close) -> float:
        """Calculate final P&L after closing position."""
        # Spot P&L
        if position.direction == "LONG_SPOT_SHORT_PERP":
            spot_pnl = (spot_close['avg_price'] - position.spot_entry_price) * position.spot_qty
            perp_pnl = (position.perp_entry_price - perp_close['avg_price']) * position.perp_qty
        else:
            spot_pnl = (position.spot_entry_price - spot_close['avg_price']) * position.spot_qty
            perp_pnl = (perp_close['avg_price'] - position.perp_entry_price) * position.perp_qty
        
        # Total = spot P&L + perp P&L + funding received - all fees
        total_fees = (
            position.notional_value * self.config.spot_fee * 2 +  # entry + exit
            position.notional_value * self.config.perp_fee * 2    # entry + exit
        )
        
        return spot_pnl + perp_pnl + position.total_funding_received - total_fees
    
    def get_current_basis(self, symbol: str) -> float:
        """Get current basis (perp - spot) / spot."""
        # Implementation depends on data feed
        # Return cached value from latest market data update
        return 0.0  # Placeholder
    
    def get_liquidation_distance(self, symbol: str, position: FundingPosition) -> float:
        """Calculate distance to liquidation price as a percentage."""
        # Implementation depends on exchange API
        return 0.20  # Placeholder: 20% distance
    
    # ----------------------------------------------------------
    # LOGGING
    # ----------------------------------------------------------
    
    def log_entry(self, symbol: str, position: FundingPosition):
        print(
            f"[ENTRY] {symbol} | {position.direction} | "
            f"Size: ${position.notional_value:,.0f} | "
            f"Basis: {position.entry_basis*100:.3f}% | "
            f"Funding: {position.entry_funding_rate*100:.4f}%"
        )
    
    def log_funding(self, symbol: str, payment: dict):
        print(
            f"[FUNDING] {symbol} | "
            f"Rate: {payment.get('rate', 0)*100:.4f}% | "
            f"Amount: ${payment['amount']:.2f}"
        )
    
    def log_exit(self, symbol: str, position: FundingPosition, final_pnl: float):
        holding_hours = (time.time() - position.entry_time) / 3600
        print(
            f"[EXIT] {symbol} | "
            f"P&L: ${final_pnl:.2f} | "
            f"Funding Collected: ${position.total_funding_received:.2f} | "
            f"Holding: {holding_hours:.1f}h | "
            f"# Payments: {len(position.funding_payments)}"
        )
    
    def log_warning(self, msg: str):
        print(f"[WARNING] {msg}")
    
    def handle_error(self, error: Exception):
        print(f"[ERROR] {error}")
```

---

## 11. Risk Management

### 11.1 Comprehensive Risk Framework

```python
FUNDING_ARB_RISK_PARAMS = {
    # Position Sizing
    "max_single_position_usd": 200_000,
    "max_total_exposure_usd": 1_000_000,
    "max_per_asset_allocation_pct": 0.30,     # Max 30% in one asset
    "max_per_exchange_allocation_pct": 0.50,  # Max 50% on one exchange
    
    # Leverage
    "max_perp_leverage": 5.0,
    "recommended_perp_leverage": 3.0,
    "min_liquidation_distance_pct": 0.15,     # 15% minimum
    
    # Margin Management
    "margin_top_up_threshold": 0.20,          # Add margin if distance < 20%
    "margin_top_up_amount_pct": 0.05,         # Add 5% of notional
    "force_close_threshold": 0.10,            # Emergency close if distance < 10%
    
    # Loss Limits
    "max_loss_per_position_pct": 0.05,        # 5% of position value
    "max_daily_loss_usd": 5_000,
    "max_weekly_loss_usd": 15_000,
    "max_monthly_loss_usd": 30_000,
    "max_drawdown_pct": 0.10,                 # 10% of total capital
    
    # Funding-Specific
    "min_funding_to_enter": 0.0003,           # 3 bps per 8h
    "exit_funding_threshold": 0.0001,         # Exit below 1 bps
    "max_negative_funding_tolerance": -0.0002, # Tolerate -2 bps before exit
    "funding_lookback_for_avg": 6,            # 6 intervals (2 days)
    
    # Basis Risk
    "max_basis_at_entry_pct": 0.005,          # 50 bps
    "max_basis_widening_pct": 0.010,          # 100 bps
    "basis_stop_loss_pct": 0.020,             # 200 bps absolute stop
    
    # Exchange Risk
    "max_capital_per_exchange_pct": 0.40,
    "exchange_health_check_interval_s": 30,
    "pause_on_exchange_issues": True,
    
    # Circuit Breakers
    "pause_on_market_volatility_pct": 0.10,   # 10% move in 1 hour
    "pause_on_api_errors_rate": 0.05,         # 5% error rate
    "max_consecutive_negative_fundings": 5,
}
```

### 11.2 Risk Scenarios and Responses

| Scenario | Trigger | Response |
|----------|---------|----------|
| Basis widens 1% | Position unrealized loss | Monitor, add margin if needed |
| Basis widens 2% | Stop loss triggered | Close position immediately |
| Funding flips negative | Direction change | Close within next interval |
| Flash crash (-20%) | Liquidation risk on short perp | N/A (spot covers); monitor margin |
| Flash pump (+20%) | Margin call on short perp | Transfer funds or reduce position |
| Exchange halt | API returns errors | Pause new entries, monitor existing |
| ADL triggered | Exchange notification | Immediately close spot leg |
| API disconnection | Heartbeat failure | Reconnect, verify positions intact |

### 11.3 Margin Monitoring Algorithm

```python
async def margin_monitoring_loop(self):
    """
    Continuously monitor margin levels for all perp positions.
    Frequency: every 10 seconds.
    """
    while self.is_running:
        for symbol, position in self.positions.items():
            # Get current margin information
            margin_info = await self.perp_exchange.get_position_info(
                f"{symbol}/USDT:PERP"
            )
            
            margin_ratio = margin_info['margin_ratio']      # margin/maintenance
            unrealized_pnl = margin_info['unrealized_pnl']
            liquidation_price = margin_info['liquidation_price']
            mark_price = margin_info['mark_price']
            
            # Calculate distance to liquidation
            if position.direction == "LONG_SPOT_SHORT_PERP":
                # Short perp: liquidation when price goes UP
                distance = (liquidation_price - mark_price) / mark_price
            else:
                # Long perp: liquidation when price goes DOWN
                distance = (mark_price - liquidation_price) / mark_price
            
            # Level 1: Warning (distance < 20%)
            if distance < 0.20:
                self.alert(f"WARNING: {symbol} liquidation distance = {distance:.2%}")
            
            # Level 2: Add margin (distance < 15%)
            if distance < 0.15:
                await self.add_margin_or_reduce(symbol, position)
            
            # Level 3: Emergency close (distance < 10%)
            if distance < 0.10:
                self.alert(f"EMERGENCY: Closing {symbol}, distance = {distance:.2%}")
                await self.exit_position(symbol, position)
        
        await asyncio.sleep(10)
```

---

## 12. Position Sizing and Capital Allocation

### 12.1 Capital Allocation Model

**Total capital deployment:**

$$C_{deployed} = C_{spot} + C_{perp\_margin} + C_{reserve}$$

Where:
- $C_{spot}$ = Capital for spot positions
- $C_{perp\_margin}$ = Initial margin for perpetual positions
- $C_{reserve}$ = Reserve for margin top-ups and unexpected events (recommend 20-30%)

**For Strategy A (Long Spot + Short Perp) with leverage $\ell$:**

$$C_{spot} = Q \times P$$
$$C_{perp\_margin} = \frac{Q \times P}{\ell}$$
$$C_{reserve} = 0.25 \times (C_{spot} + C_{perp\_margin})$$

$$C_{total} = Q \times P \times \left(1 + \frac{1}{\ell}\right) \times 1.25$$

### 12.2 Optimal Leverage Selection

Higher leverage means higher capital efficiency but less distance to liquidation:

$$APY(\ell) = \frac{\bar{F} \times 1095 \times Q \times P}{Q \times P \times (1 + 1/\ell) \times 1.25}$$

$$APY(\ell) = \frac{\bar{F} \times 1095}{(1 + 1/\ell) \times 1.25}$$

| Leverage | Capital Efficiency | Liq. Distance | APY (F=0.03%) | Risk Level |
|:--------:|:------------------:|:-------------:|:-------------:|:----------:|
| 1x (no leverage) | 40% | ~100% | 13.1% | Very Low |
| 2x | 53% | ~49% | 17.5% | Low |
| 3x | 60% | ~33% | 19.7% | Moderate |
| 5x | 67% | ~19% | 21.9% | Moderate-High |
| 10x | 73% | ~9% | 24.0% | High |
| 20x | 76% | ~4% | 24.8% | Very High |

**Recommendation:** 3x leverage provides a good balance between capital efficiency and safety margin.

### 12.3 Multi-Asset Allocation

For a portfolio of $n$ assets with funding rates $\{F_1, ..., F_n\}$:

**Equal weight allocation:**

$$w_i = \frac{1}{n}$$

**Proportional to funding rate:**

$$w_i = \frac{F_i}{\sum_{j=1}^n F_j}$$

**Risk-parity (inversely proportional to basis volatility):**

$$w_i = \frac{1/\sigma_{b,i}}{\sum_{j=1}^n 1/\sigma_{b,j}}$$

Where $\sigma_{b,i}$ is the basis volatility of asset $i$.

---

## 13. References

### Academic Papers

1. **Alexander, C., Choi, J., Park, H., & Sohn, S.** (2020). "BitMEX Bitcoin Derivatives: Price Discovery, Informational Efficiency, and Hedging Effectiveness." *Journal of Futures Markets*, 40(1), 23-43.

2. **Shleifer, A., & Vishny, R. W.** (1997). "The Limits of Arbitrage." *The Journal of Finance*, 52(1), 35-55.

3. **Liu, Y., & Tsyvinski, A.** (2021). "Risks and Returns of Cryptocurrency." *The Review of Financial Studies*, 34(6), 2689-2727.

4. **Makarov, I., & Schoar, A.** (2020). "Trading and Arbitrage in Cryptocurrency Markets." *Journal of Financial Economics*, 135(2), 293-319.

5. **Hull, J. C.** (2022). *Options, Futures, and Other Derivatives* (11th ed.). Pearson. — Chapter on futures pricing and basis risk.

6. **Cartea, A., Jaimungal, S., & Penalva, J.** (2015). *Algorithmic and High-Frequency Trading*. Cambridge University Press.

### Exchange Documentation

- Binance Futures Funding Rate: https://www.binance.com/en/support/faq/funding-rate
- Binance Funding Rate History API: https://binance-docs.github.io/apidocs/futures/en/#get-funding-rate-history
- Bybit Funding Rate: https://www.bybit.com/data/basic/linear/funding-history
- OKX Funding Rate: https://www.okx.com/trade-market/funding-history
- dYdX Perpetuals: https://docs.dydx.exchange/

### Data Sources

- Coinglass Funding Rates: https://www.coinglass.com/FundingRate
- Laevitas Derivatives Analytics: https://app.laevitas.ch/
- The Block Funding Data: https://www.theblock.co/data/crypto-markets/futures

---

> **Related Documents:**
> - [00_overview.md](./00_overview.md) — Arbitrage Overview
> - [01_triangular_arbitrage.md](./01_triangular_arbitrage.md) — Triangular Arbitrage
> - [03_cross_exchange_arbitrage.md](./03_cross_exchange_arbitrage.md) — Cross-Exchange Arbitrage (complementary strategy)
