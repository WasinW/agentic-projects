# การเทรดตามสหสัมพันธ์ (Correlation Trading) — เอกสารอ้างอิงฉบับสมบูรณ์

## ข้อมูลเอกสาร
| ฟิลด์ | ค่า |
|---|---|
| ประเภทกลยุทธ์ | สหสัมพันธ์ / การเทรดมูลค่าเปรียบเทียบ (Correlation / Relative Value Trading) |
| สินทรัพย์ | Forex, คริปโต, ข้ามสินทรัพย์ (Cross-Asset) |
| กรอบเวลา | หลายวันถึงหลายเดือน |
| ความซับซ้อน | สูง |
| เงินทุนที่ต้องการ | ปานกลางถึงสูง |
| อัปเดตล่าสุด | 2026-04-12 |

---

## สารบัญ
1. [การวิเคราะห์เมทริกซ์สหสัมพันธ์](#1-correlation-matrix-analysis)
2. [สหสัมพันธ์เลื่อนและการเปลี่ยนสภาวะ](#2-rolling-correlation-and-regime-changes)
3. [การพังทลายของสหสัมพันธ์ในช่วงวิกฤต](#3-correlation-breakdown-during-crises)
4. [ทฤษฎี Dollar Smile สำหรับ Forex](#4-dollar-smile-theory-for-forex)
5. [กลุ่มสหสัมพันธ์คริปโต](#5-crypto-correlation-clusters)
6. [การเทรด Dispersion](#6-dispersion-trading)
7. [การป้องกันความเสี่ยงด้วยสินทรัพย์ที่สัมพันธ์กัน](#7-hedging-using-correlated-assets)
8. [การสร้างพอร์ตโฟลิโอด้วยสหสัมพันธ์](#8-portfolio-construction-using-correlation)
9. [ตรรกะหลัก — การเข้า/ออกสถานะ](#9-core-logic--entryexit)
10. [ข้อมูลจำเพาะทางเทคนิค](#10-technical-specifications)
11. [กรอบแนวคิดทางคณิตศาสตร์](#11-mathematical-framework)
12. [พารามิเตอร์ความเสี่ยง](#12-risk-parameters)
13. [ขั้นตอนการดำเนินการ](#13-execution-flow)
14. [เอกสารอ้างอิง](#14-references)

---

## 1. การวิเคราะห์เมทริกซ์สหสัมพันธ์ (Correlation Matrix Analysis)

### 1.1 Correlation Definitions

**Pearson Correlation Coefficient:**

$$\rho_{X,Y} = \frac{\text{Cov}(X, Y)}{\sigma_X \sigma_Y} = \frac{E[(X-\mu_X)(Y-\mu_Y)]}{\sigma_X \sigma_Y}$$

**Sample Correlation:**

$$r_{X,Y} = \frac{\sum_{i=1}^{n}(x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{n}(x_i-\bar{x})^2 \sum_{i=1}^{n}(y_i-\bar{y})^2}}$$

### 1.2 Types of Correlation Measures

| Measure | Use Case | Advantages | Limitations |
|---|---|---|---|
| Pearson | Linear relationships | Standard, well-understood | Sensitive to outliers, linear only |
| Spearman | Monotonic relationships | Rank-based, robust to outliers | Less power for linear |
| Kendall's Tau | Ordinal relationships | Robust, handles ties | Computationally expensive |
| Copula-based | Tail dependence | Captures non-linear tail co-movement | Complex to estimate |
| Dynamic Conditional (DCC) | Time-varying | Adapts to changing regimes | Model complexity |

### 1.3 Forex Correlation Matrix (Typical)

**Major Currency Pairs (relative to USD):**

| | EUR/USD | GBP/USD | AUD/USD | USD/JPY | USD/CHF | USD/CAD |
|---|---|---|---|---|---|---|
| EUR/USD | 1.00 | 0.75 | 0.65 | -0.40 | -0.85 | -0.55 |
| GBP/USD | 0.75 | 1.00 | 0.60 | -0.35 | -0.70 | -0.50 |
| AUD/USD | 0.65 | 0.60 | 1.00 | -0.30 | -0.60 | -0.70 |
| USD/JPY | -0.40 | -0.35 | -0.30 | 1.00 | 0.50 | 0.35 |
| USD/CHF | -0.85 | -0.70 | -0.60 | 0.50 | 1.00 | 0.60 |
| USD/CAD | -0.55 | -0.50 | -0.70 | 0.35 | 0.60 | 1.00 |

**Key Relationships:**
- EUR/USD and USD/CHF: Very high negative correlation (~-0.85) — mirror images of USD strength
- AUD/USD and USD/CAD: High negative correlation (~-0.70) — both commodity currencies
- EUR/USD and GBP/USD: High positive correlation (~0.75) — European currencies vs USD

### 1.4 Crypto Correlation Matrix (Typical)

| | BTC | ETH | SOL | BNB | AVAX | LINK |
|---|---|---|---|---|---|---|
| BTC | 1.00 | 0.85 | 0.75 | 0.70 | 0.72 | 0.70 |
| ETH | 0.85 | 1.00 | 0.82 | 0.75 | 0.80 | 0.78 |
| SOL | 0.75 | 0.82 | 1.00 | 0.70 | 0.78 | 0.72 |
| BNB | 0.70 | 0.75 | 0.70 | 1.00 | 0.68 | 0.65 |
| AVAX | 0.72 | 0.80 | 0.78 | 0.68 | 1.00 | 0.75 |
| LINK | 0.70 | 0.78 | 0.72 | 0.65 | 0.75 | 1.00 |

**Key Observations:**
- Crypto correlations are generally HIGH (0.65-0.90)
- BTC dominates the correlation structure (Factor 1 = "market factor")
- Correlations increase during crashes (contagion effect)
- Lower correlations between different "sectors" (DeFi vs L1 vs Meme)

### 1.5 Correlation Significance Testing

**Test Statistic:**

$$t = r\sqrt{\frac{n-2}{1-r^2}} \sim t_{n-2}$$

**Confidence Interval (Fisher Z-transform):**

$$z = \frac{1}{2}\ln\left(\frac{1+r}{1-r}\right) = \text{arctanh}(r)$$

$$SE(z) = \frac{1}{\sqrt{n-3}}$$

$$CI_{95\%} = \tanh(z \pm 1.96 \times SE(z))$$

---

## 2. สหสัมพันธ์เลื่อนและการเปลี่ยนสภาวะ (Rolling Correlation and Regime Changes)

### 2.1 Rolling Correlation

$$r_{t,window} = \text{Corr}(X_{t-w+1:t}, Y_{t-w+1:t})$$

Where $w$ is the rolling window size.

**Optimal Window Selection:**

| Purpose | Window Size | Rationale |
|---|---|---|
| Short-term trading signals | 20-30 bars | Captures recent regime |
| Medium-term relationship | 60-90 bars | Balanced stability/responsiveness |
| Long-term structure | 180-252 bars | Captures full market cycle |

### 2.2 Exponentially Weighted Correlation (EWMA)

$$r_{t}^{EWMA} = \frac{\text{Cov}_t^{EWMA}(X,Y)}{\sqrt{\text{Var}_t^{EWMA}(X) \times \text{Var}_t^{EWMA}(Y)}}$$

Where:

$$\text{Cov}_t^{EWMA}(X,Y) = \lambda \cdot \text{Cov}_{t-1}^{EWMA} + (1-\lambda) \cdot (x_t - \bar{x})(y_t - \bar{y})$$

$\lambda$ = decay factor (typically 0.94-0.97)

**Advantages:**
- More responsive to recent correlation changes
- Gives higher weight to recent observations
- Standard in RiskMetrics (JP Morgan)

### 2.3 DCC-GARCH Model

The Dynamic Conditional Correlation model (Engle, 2002):

**Step 1: Fit univariate GARCH models:**

$$r_{i,t} = \sigma_{i,t} \epsilon_{i,t}$$
$$\sigma_{i,t}^2 = \omega_i + \alpha_i r_{i,t-1}^2 + \beta_i \sigma_{i,t-1}^2$$

**Step 2: Estimate dynamic correlations:**

$$Q_t = (1-a-b)\bar{Q} + a\epsilon_{t-1}\epsilon_{t-1}' + bQ_{t-1}$$

$$R_t = \text{diag}(Q_t)^{-1/2} Q_t \text{diag}(Q_t)^{-1/2}$$

Where:
- $Q_t$ = quasi-correlation matrix
- $R_t$ = time-varying correlation matrix
- $\bar{Q}$ = unconditional correlation matrix
- $a, b$ = parameters (analogous to GARCH $\alpha, \beta$)

### 2.4 Regime Detection from Correlation Changes

```
Algorithm: Correlation Regime Detection

INPUT: 
    rolling_correlation: time series of rolling correlation
    lookback: periods for regime classification
    
1. Calculate statistics:
    corr_mean = mean(rolling_correlation[-lookback:])
    corr_std = std(rolling_correlation[-lookback:])
    corr_current = rolling_correlation[-1]
    
2. Classify regime:
    IF corr_current > corr_mean + 1.5 * corr_std:
        regime = "HIGH_CORRELATION"
        # Assets moving together more than usual
        # Risk: reduced diversification benefit
        
    ELIF corr_current < corr_mean - 1.5 * corr_std:
        regime = "LOW_CORRELATION" (or "DECORRELATION")
        # Assets decoupling from normal relationship
        # Opportunity: pairs may be diverging (stat arb signal)
        
    ELSE:
        regime = "NORMAL_CORRELATION"
        
3. Detect transitions:
    IF regime changed from previous period:
        ALERT: "Correlation regime shift detected"
        IF previous = "NORMAL" AND current = "HIGH":
            SIGNAL: "Crisis risk — correlations spiking"
        IF previous = "NORMAL" AND current = "LOW":
            SIGNAL: "Decorrelation — pairs trading opportunity"

OUTPUT: regime, regime_change_signal
```

### 2.5 Correlation Instability Metric

$$\text{Correlation Instability} = \text{Std}(r_{t,20}) \quad (\text{over last 60-90 bars})$$

| Instability Level | Value | Interpretation |
|---|---|---|
| Stable | < 0.10 | Correlation is reliable; safe to use for hedging |
| Moderate | 0.10-0.25 | Normal variation; monitor |
| Unstable | 0.25-0.40 | Relationship may be changing; reduce hedge reliance |
| Highly Unstable | > 0.40 | Relationship unreliable; avoid correlation-based trades |

---

## 3. การพังทลายของสหสัมพันธ์ในช่วงวิกฤต (Correlation Breakdown During Crises)

### 3.1 The Correlation Crisis Phenomenon

During market crises, correlations between assets tend to increase dramatically, often approaching 1.0. This is known as "correlation breakdown" (from a diversification perspective) or "correlation contagion."

**Mathematical Framework:**

$$\rho_{crisis} = \rho_{normal} + \Delta\rho_{stress}$$

Where $\Delta\rho_{stress} > 0$ for most asset pairs during crises.

### 3.2 Empirical Evidence

**Correlation Changes During Historical Crises:**

| Event | Normal Correlation (Crypto) | Crisis Correlation | Change |
|---|---|---|---|
| May 2021 Crash | BTC-ETH: 0.80 | 0.95 | +0.15 |
| FTX Collapse 2022 | BTC-Altcoins: 0.70 | 0.92 | +0.22 |
| COVID March 2020 | EUR-GBP: 0.60 | 0.85 | +0.25 |
| GFC 2008 | AUD-NZD: 0.85 | 0.97 | +0.12 |

### 3.3 Asymmetric Correlation

Correlation tends to be higher during down markets than up markets:

$$\rho_{down} > \rho_{up}$$

**Exceedance Correlation (Longin & Solnik, 2001):**

$$\rho(\theta) = \text{Corr}(X, Y | X < F_X^{-1}(\theta), Y < F_Y^{-1}(\theta))$$

Where $\theta$ is the quantile threshold (e.g., $\theta = 0.05$ for the joint 5th percentile).

### 3.4 Lower Tail Dependence

$$\lambda_L = \lim_{u \to 0} P(Y \leq F_Y^{-1}(u) | X \leq F_X^{-1}(u))$$

- $\lambda_L > 0$: Assets crash together (tail dependence)
- $\lambda_L = 0$: No tail dependence (crashes are independent)

Gaussian copula has $\lambda_L = 0$ (underestimates joint tail risk). Student-t and Clayton copulas have $\lambda_L > 0$.

### 3.5 Implications for Trading

| Implication | Action |
|---|---|
| Diversification fails when most needed | Overweight hedging during calm periods |
| Portfolio VaR underestimated during stress | Use stress-adjusted correlation in risk models |
| Pairs trading risk increases | Widen stops during high-correlation regimes |
| Hedging becomes more effective | Less basis risk during crises |
| Factor concentration increases | Reduce leverage when correlations spike |

### 3.6 Correlation-Adjusted Risk Model

**Stress-Adjusted Portfolio Variance:**

$$\sigma_p^2 = \mathbf{w}'\Sigma_{stress}\mathbf{w}$$

Where $\Sigma_{stress}$ uses elevated correlations:

$$\Sigma_{stress} = D \cdot R_{stress} \cdot D$$

$$R_{stress,ij} = \min(1, \rho_{ij,normal} + \Delta\rho_{crisis})$$

Typical $\Delta\rho_{crisis}$ = +0.20 to +0.30 for stress testing.

---

## 4. ทฤษฎี Dollar Smile สำหรับ Forex

### 4.1 The Dollar Smile

The "Dollar Smile" (Stephen Jen, Morgan Stanley) describes the relationship between USD strength and global economic conditions:

```
USD Strength
    ^
    |   Strong       Weak       Strong
    |    USD          USD         USD
    |     *                       *
    |      *                     *
    |       *                   *
    |        *       *   *     *
    |         *     *     *   *
    |          *   *       * *
    |           * *         *
    |            *
    +-----------------------------------------> Economic Conditions
         Risk-Off    Normal    US Boom
        (Global       Growth    (US 
         Crisis)              Outperformance)
```

**Three Regimes:**

| Regime | USD Behavior | Driver | Correlation Pattern |
|---|---|---|---|
| Left Side (Risk-Off) | USD Strong | Safe-haven demand, deleveraging | USD correlates positively with VIX |
| Bottom (Normal Growth) | USD Weak | Yield-seeking, carry trades | USD correlates negatively with risk assets |
| Right Side (US Boom) | USD Strong | US growth outperformance, rate hikes | USD correlates with US equities |

### 4.2 Trading the Dollar Smile

```
REGIME IDENTIFICATION:

Regime 1: RISK-OFF (Dollar Smile Left)
    Signals: VIX > 25, Credit spreads widening, Equity selloff
    USD Position: LONG (safe haven)
    Pairs: Long USD/JPY-crosses, Short EM/USD
    Correlation: USD ↑ with VIX, Gold ↑, Equities ↓
    
Regime 2: GLOBAL GROWTH (Dollar Smile Bottom)
    Signals: VIX < 18, Global PMIs expanding, Risk appetite high
    USD Position: SHORT (carry/risk flows leave USD)
    Pairs: Long AUD/USD, NZD/USD, EM currencies
    Correlation: USD ↓ with equities, Commodities ↑, EM ↑
    
Regime 3: US OUTPERFORMANCE (Dollar Smile Right)
    Signals: US data > expectations, Fed hawkish, US-RoW growth differential
    USD Position: LONG (growth premium)
    Pairs: Long USD/EUR, USD/JPY
    Correlation: USD ↑ with US equities, USD ↑ with US yields

TRANSITION TRADES:
    From Regime 1 → Regime 2: Short USD (most profitable transition for carry)
    From Regime 2 → Regime 3: Long USD (momentum with growth)
    From Regime 3 → Regime 1: USD stays strong initially, then spikes (buy early)
```

### 4.3 Dollar Smile Correlation Framework

**Correlation of USD with Risk Assets by Regime:**

| Regime | USD-Equities Corr | USD-VIX Corr | USD-EM Corr | USD-Gold Corr |
|---|---|---|---|---|
| Risk-Off | -0.3 to -0.6 | +0.4 to +0.7 | -0.5 to -0.8 | -0.2 to +0.3 |
| Normal | -0.1 to -0.3 | -0.1 to -0.3 | +0.0 to +0.3 | -0.3 to -0.5 |
| US Boom | +0.2 to +0.5 | -0.2 to -0.4 | -0.2 to +0.1 | -0.4 to -0.6 |

---

## 5. กลุ่มสหสัมพันธ์คริปโต (Crypto Correlation Clusters)

### 5.1 BTC Dominance and Correlation Structure

Bitcoin dominance (BTC's share of total crypto market cap) fundamentally shapes the crypto correlation structure:

$$\text{BTC Dominance} = \frac{\text{MarketCap}_{BTC}}{\text{MarketCap}_{Total}}$$

| BTC Dominance | Typical Correlation (BTC vs Alts) | Market Phase |
|---|---|---|
| > 55% (Rising) | 0.60-0.80 | BTC leading, alt rotation low |
| 40-55% (Stable) | 0.70-0.85 | Normal correlation |
| < 40% (Falling) | 0.50-0.70 | "Alt season" — alts decoupling upward |
| Crisis (Rising fast) | 0.90-0.98 | Flight to BTC/stables — everything crashes |

### 5.2 Crypto Sector Clusters

```
CLUSTER ANALYSIS:

Cluster 1: "Market" (Macro Factor)
    Assets: BTC, ETH (dominant pair)
    Behavior: Drives overall market direction
    Intra-cluster correlation: 0.85-0.95
    
Cluster 2: "L1 Smart Contract Platforms"
    Assets: ETH, SOL, AVAX, ADA, DOT
    Behavior: Move together on L1 narrative
    Intra-cluster correlation: 0.75-0.90
    vs BTC: 0.70-0.85
    
Cluster 3: "DeFi Protocols"
    Assets: AAVE, UNI, CRV, MKR, COMP
    Behavior: Correlated with ETH TVL, governance narratives
    Intra-cluster correlation: 0.65-0.80
    vs BTC: 0.60-0.75
    
Cluster 4: "Meme/Speculative"
    Assets: DOGE, SHIB, PEPE
    Behavior: Idiosyncratic, social media driven
    Intra-cluster correlation: 0.50-0.70
    vs BTC: 0.40-0.65 (lower in normal, spikes in crisis)
    
Cluster 5: "Infrastructure"
    Assets: LINK, GRT, FIL, AR
    Behavior: Utility-driven, moderate BTC correlation
    Intra-cluster correlation: 0.60-0.75
    vs BTC: 0.55-0.70
```

### 5.3 BTC Dominance-Based Strategy

```
Algorithm: BTC Dominance Rotation

IF BTC_dominance is RISING:
    # Capital flowing into BTC (flight to quality or BTC leadership)
    LONG: BTC (outperforming)
    SHORT: Altcoin basket (underperforming)
    OR: Overweight BTC relative to portfolio benchmark
    
IF BTC_dominance is FALLING:
    # Capital rotating into altcoins ("alt season")
    LONG: Altcoin basket (select by relative strength)
    SHORT: BTC (underperforming relatively)
    OR: Overweight altcoins, underweight BTC
    
IF BTC_dominance SPIKES sharply upward:
    # Risk-off in crypto — everything except BTC crashing
    REDUCE overall crypto exposure
    IF staying in crypto, overweight BTC and stablecoins
    
MEASUREMENT:
    btc_dom_sma_20 = SMA(BTC_dominance, 20)
    btc_dom_sma_50 = SMA(BTC_dominance, 50)
    
    Rising: btc_dom_sma_20 > btc_dom_sma_50 AND current > btc_dom_sma_20
    Falling: btc_dom_sma_20 < btc_dom_sma_50 AND current < btc_dom_sma_20
```

### 5.4 Cross-Cluster Correlation Opportunities

When correlation between clusters drops below normal:

```
DECORRELATION OPPORTUNITY:
    IF corr(Cluster_A, Cluster_B) < historical_mean - 2 * std:
        # Clusters are unusually decorrelated
        # Expect mean reversion of correlation (convergence)
        
        IF Cluster_A underperforming AND Cluster_B outperforming:
            LONG: Cluster_A leaders
            SHORT: Cluster_B leaders
            # Bet on relative convergence
```

---

## 6. การเทรด Dispersion

### 6.1 Concept

Dispersion trading profits from the difference between:
- **Implied correlation** (priced into index/basket options)
- **Realized correlation** (actual correlation during the period)

If implied correlation > realized correlation (common), selling correlation is profitable.

### 6.2 Crypto Dispersion Trading

In traditional markets, dispersion trading uses index options vs single-stock options. In crypto:

**Index Analog:** BTC-weighted crypto basket or DeFi index
**Singles:** Individual tokens (ETH, SOL, AVAX, etc.)

**Strategy:**

$$\text{Dispersion P\&L} = \sigma_{implied,index}^2 - \sum_i w_i^2 \sigma_{realized,i}^2 - 2\sum_{i<j} w_i w_j \rho_{ij,realized} \sigma_i \sigma_j$$

Simplification: If implied correlation > realized correlation:

$$\text{Profit} \propto (\rho_{implied} - \rho_{realized}) \times \text{Vega}$$

### 6.3 Simplified Dispersion Strategy (Without Options)

In crypto where options liquidity is limited, a simplified dispersion approach:

```
DISPERSION PROXY:

1. Calculate cross-sectional dispersion of returns:
   dispersion_t = std(returns of all assets in basket at time t)
   
2. Calculate basket return:
   basket_return = weighted average return of all assets

3. STRATEGY:
   IF realized dispersion < historical average:
       # Assets moving too much together
       # Expect dispersion to increase (mean reversion)
       TRADE: Long individual divergers, Short the basket
       
   IF realized dispersion > historical average:
       # Assets are scattered; expect convergence
       # Correlation likely to increase
       TRADE: Long the basket, Short the biggest divergers
```

### 6.4 Correlation Mean Reversion

Correlations themselves mean-revert over time:

$$d\rho_t = \kappa_\rho(\bar{\rho} - \rho_t)dt + \sigma_\rho dW_t$$

**Half-life of correlation mean reversion:**

For crypto: approximately 10-30 days
For forex: approximately 30-90 days

**Trading Rule:**

$$z_{\rho} = \frac{\rho_{current} - \bar{\rho}_{long\_term}}{\sigma_\rho}$$

- If $z_\rho > 2.0$: Sell correlation (dispersion trade — long singles, short basket)
- If $z_\rho < -2.0$: Buy correlation (convergence trade — short singles, long basket)

---

## 7. การป้องกันความเสี่ยงด้วยสินทรัพย์ที่สัมพันธ์กัน (Hedging Using Correlated Assets)

### 7.1 Hedge Ratio from Correlation

The minimum-variance hedge ratio:

$$\beta_{hedge} = \rho_{X,Y} \times \frac{\sigma_X}{\sigma_Y}$$

Where:
- $X$ = asset to hedge
- $Y$ = hedging instrument
- $\rho_{X,Y}$ = correlation between $X$ and $Y$

**Variance of hedged position:**

$$\sigma_{hedged}^2 = \sigma_X^2(1 - \rho_{X,Y}^2)$$

The hedge eliminates $\rho^2$ percent of the variance.

### 7.2 Hedge Effectiveness

$$R^2 = \rho^2 = 1 - \frac{\sigma_{hedged}^2}{\sigma_{unhedged}^2}$$

| Correlation | Hedge Effectiveness ($R^2$) | Residual Variance |
|---|---|---|
| 0.95 | 90.25% | 9.75% |
| 0.90 | 81.0% | 19.0% |
| 0.80 | 64.0% | 36.0% |
| 0.70 | 49.0% | 51.0% |
| 0.60 | 36.0% | 64.0% |

### 7.3 Cross-Hedge Examples

| Position | Hedge Instrument | Correlation | Use Case |
|---|---|---|---|
| Long ETH | Short BTC-perp | 0.85 | Isolate ETH alpha from crypto market risk |
| Long AUD/USD | Short NZD/USD | 0.80 | Isolate AUD-specific factors |
| Long SOL | Short ETH | 0.75 | Bet on SOL vs ETH without market exposure |
| Long altcoin basket | Short BTC | 0.70 | Isolate "alt season" alpha |
| Long EUR/USD | Short GBP/USD | 0.75 | Bet on EUR vs GBP without USD exposure |

### 7.4 Dynamic Hedge Adjustment

```
Algorithm: Dynamic Correlation-Based Hedging

PARAMETERS:
    hedge_pair: (asset_to_hedge, hedging_instrument)
    rebalance_frequency: daily
    correlation_window: 60 bars
    
EACH REBALANCE PERIOD:
    1. Calculate rolling correlation:
       rho = rolling_corr(returns_X, returns_Y, window=60)
    
    2. Calculate rolling volatility ratio:
       vol_ratio = rolling_std(returns_X, 30) / rolling_std(returns_Y, 30)
    
    3. Update hedge ratio:
       beta_new = rho * vol_ratio
    
    4. Calculate hedge adjustment:
       delta_hedge = (beta_new - beta_current) * position_X
    
    5. IF |delta_hedge| > rebalance_threshold:
       Execute hedge adjustment
       beta_current = beta_new
    
    6. Monitor hedge effectiveness:
       tracking_error = std(returns_X - beta_current * returns_Y)
       IF tracking_error > max_acceptable:
           ALERT: "Hedge breakdown — correlation unstable"
           Consider: Adding more hedging instruments or reducing position
```

### 7.5 Multi-Asset Hedging

When a single hedge instrument is insufficient, use multiple correlated assets:

$$\min_{\beta} \text{Var}(R_X - \sum_j \beta_j R_{Y_j})$$

Solution (OLS regression):

$$\boldsymbol{\beta} = (\mathbf{R}_Y'\mathbf{R}_Y)^{-1}\mathbf{R}_Y'\mathbf{R}_X$$

**Example: Hedging an altcoin portfolio:**
- Hedge instruments: BTC (market factor), ETH (L1 factor), SOL (L1-alt factor)
- The multi-factor hedge captures more variance than any single instrument

---

## 8. การสร้างพอร์ตโฟลิโอด้วยสหสัมพันธ์ (Portfolio Construction Using Correlation)

### 8.1 Minimum Variance Portfolio

$$\mathbf{w}_{MV} = \frac{\Sigma^{-1}\mathbf{1}}{\mathbf{1}'\Sigma^{-1}\mathbf{1}}$$

Where $\Sigma$ is the covariance matrix and $\mathbf{1}$ is a vector of ones.

### 8.2 Maximum Diversification Portfolio

The Maximum Diversification ratio (Choueifaty, 2008):

$$DR = \frac{\mathbf{w}'\boldsymbol{\sigma}}{\sqrt{\mathbf{w}'\Sigma\mathbf{w}}}$$

Where $\boldsymbol{\sigma}$ is the vector of individual volatilities.

Maximize DR to find the portfolio with maximum diversification benefit:

$$\mathbf{w}_{MD} = \arg\max_\mathbf{w} \frac{\mathbf{w}'\boldsymbol{\sigma}}{\sqrt{\mathbf{w}'\Sigma\mathbf{w}}}$$

### 8.3 Risk Parity Portfolio

Equal risk contribution from each asset:

$$\text{RC}_i = w_i \times (\Sigma\mathbf{w})_i = \frac{\sigma_p^2}{n}$$

For each asset $i$:

$$w_i \times \sum_j w_j \sigma_{ij} = \frac{1}{n}\mathbf{w}'\Sigma\mathbf{w}$$

**Approximate Solution (uncorrelated assets):**

$$w_i \propto \frac{1}{\sigma_i}$$

**Exact Solution (correlated assets):** Requires iterative optimization.

### 8.4 Correlation-Informed Position Sizing

```
Algorithm: Correlation-Adjusted Position Sizing

INPUT:
    signals: list of trade signals with direction and strength
    correlation_matrix: current correlation matrix of signal assets
    
1. Start with base position sizes from individual signal strength

2. Calculate portfolio correlation risk:
   FOR each pair (i, j) of concurrent positions:
       IF same_direction(signal_i, signal_j) AND corr(i,j) > threshold:
           # Correlated bets in same direction = concentrated risk
           reduction_factor = 1 - (corr(i,j) - threshold) / (1 - threshold)
           Reduce both positions by reduction_factor
           
       IF opposite_direction(signal_i, signal_j) AND corr(i,j) > threshold:
           # Natural hedge — less risk than it appears
           # Can allow slightly larger positions
           boost_factor = 1 + 0.2 * (corr(i,j) - threshold)
           
3. Ensure total portfolio risk within limits:
   portfolio_vol = sqrt(w' * Sigma * w)
   IF portfolio_vol > max_vol:
       scale_all = max_vol / portfolio_vol
       w = w * scale_all

OUTPUT: adjusted position sizes
```

### 8.5 Hierarchical Risk Parity (HRP)

Lopez de Prado (2016) introduced HRP, which uses correlation-based clustering:

```
Algorithm: Hierarchical Risk Parity

1. CLUSTERING:
   - Compute distance matrix: d(i,j) = sqrt(0.5 * (1 - corr(i,j)))
   - Apply hierarchical clustering (single-linkage or Ward's method)
   - Obtain dendrogram tree structure
   
2. QUASI-DIAGONALIZATION:
   - Reorder covariance matrix according to clustering
   - This places correlated assets next to each other
   
3. RECURSIVE BISECTION:
   - Split assets into two clusters at each level
   - Allocate risk between clusters inversely proportional to their variance
   - Recurse within each cluster
   
RESULT: Weights that respect the hierarchical correlation structure
```

**Advantages over Markowitz:**
- No matrix inversion (more stable with noisy correlation estimates)
- Naturally handles hierarchical correlation structure
- More robust to estimation error

---

## 9. ตรรกะหลัก — การเข้า/ออกสถานะ (Core Logic — Entry/Exit)

### 9.1 Correlation Breakout/Breakdown Trading

```
Algorithm: Correlation Divergence Trading

MONITORING (rolling):
    FOR each asset pair (A, B) in universe:
        corr_30d = rolling_correlation(A, B, window=30)
        corr_90d = rolling_correlation(A, B, window=90)
        corr_long = rolling_correlation(A, B, window=252)
        
        z_corr = (corr_30d - corr_long) / std(rolling_corr_history)

ENTRY — DECORRELATION TRADE (Pair Diverging):
    IF z_corr < -2.0 (correlation much lower than normal):
        # Assets are diverging from their typical relationship
        # Expect correlation to mean-revert (convergence)
        
        relative_return = cumulative_return(A, 20) - cumulative_return(B, 20)
        
        IF relative_return > 0:
            # A outperformed while decorrelating
            LONG B, SHORT A (bet on convergence: B catches up)
        ELSE:
            # B outperformed while decorrelating  
            LONG A, SHORT B (bet on convergence: A catches up)
        
        SIZE: Proportional to |z_corr| / max_z
        STOP: z_corr returns to 0 without price convergence (relationship truly changed)
        TARGET: Relative price converges to historical norm

ENTRY — CORRELATION SPIKE TRADE:
    IF z_corr > +2.0 (correlation much higher than normal):
        # Assets moving too closely together
        # Likely stress event; correlation will normalize
        
        # Wait for stress to pass, then:
        IF assets are at extremes AND stress_indicator declining:
            # Buy the relatively cheaper one, sell the expensive one
            LONG underperformer, SHORT outperformer
            # Expect the stress-induced lockstep to break
            # and relative values to diverge back to fundamentals

EXIT:
    IF z_corr returns to [-0.5, +0.5] range:
        EXIT (correlation normalized)
    IF holding_period > 3 * half_life_of_correlation:
        EXIT (time stop)
    IF loss > max_loss_per_pair:
        EXIT (stop loss)
```

### 9.2 BTC-Dominance Rotation Strategy Entry/Exit

```
Algorithm: BTC Dominance Rotation

SIGNALS:
    btc_dom = current BTC dominance percentage
    btc_dom_ma20 = SMA(btc_dom, 20)
    btc_dom_ma50 = SMA(btc_dom, 50)
    btc_dom_roc = (btc_dom - btc_dom[20 bars ago]) / btc_dom[20 bars ago]
    
ENTRY — ALT SEASON TRADE:
    IF btc_dom_ma20 < btc_dom_ma50 (dominance falling):
        AND btc_dom_roc < -2% (dominance declining meaningfully):
        AND total_market_cap is rising (bullish context):
        
        LONG: Top 3-5 altcoins by relative strength (vs BTC)
        SHORT: BTC (equal dollar amount) — for market-neutral version
        OR: Simply overweight alts vs BTC in portfolio
        
        SIZE: Based on dominance decline rate
        STOP: BTC dominance starts rising (ma20 > ma50)

ENTRY — BTC LEADERSHIP TRADE:
    IF btc_dom_ma20 > btc_dom_ma50 (dominance rising):
        AND btc_dom_roc > +2%:
        
        LONG: BTC
        SHORT: Altcoin basket — or simply overweight BTC
        
        SIZE: Based on dominance increase rate
        STOP: BTC dominance starts falling

EXIT:
    Reverse signal (cross-over of dominance MAs)
    OR time-based rebalancing (bi-weekly)
```

### 9.3 Cross-Asset Correlation Hedge Entry

```
Algorithm: Correlation-Based Hedging Decision

GIVEN: Primary position (e.g., Long ETH)

HEDGE DECISION:
    1. Identify best hedge instrument:
       FOR each candidate hedge H:
           corr = correlation(ETH_returns, H_returns, window=60)
           vol_ratio = vol(ETH) / vol(H)
           beta = corr * vol_ratio
           tracking_error = std(ETH_returns - beta * H_returns)
           hedge_cost = estimated_cost(H) / holding_period
           
       RANK by: (correlation * vol_ratio) / (tracking_error + hedge_cost)
       SELECT: Top ranked instrument
       
    2. Calculate hedge ratio:
       beta_hedge = corr * vol(ETH) / vol(H)
       
    3. Determine hedge amount:
       IF full_hedge:
           hedge_notional = position_notional * beta_hedge
       IF partial_hedge (tail only):
           hedge_notional = position_notional * beta_hedge * tail_hedge_ratio
           
    4. Execute hedge:
       SHORT hedge_instrument at calculated size
       
    5. Monitor:
       Track rolling correlation
       Rebalance if beta changes > threshold
       Unwind hedge when primary position is closed
```

---

## 10. ข้อมูลจำเพาะทางเทคนิค (Technical Specifications)

### 10.1 System Configuration

```yaml
correlation_trading_config:
  # Correlation Calculation
  correlation:
    methods: [pearson, ewma, dcc]
    windows: [20, 30, 60, 90, 252]
    ewma_lambda: 0.94
    update_frequency: daily
    
  # Universe
  universe:
    forex: [EUR/USD, GBP/USD, AUD/USD, NZD/USD, USD/JPY, USD/CHF, USD/CAD]
    crypto: [BTC, ETH, SOL, BNB, AVAX, ADA, DOT, LINK, UNI, AAVE]
    cross_asset: [DXY, SPX, VIX, GOLD, OIL]
    
  # Regime Detection
  regime:
    z_score_window: 252       # Long-term for z-score calculation
    high_corr_threshold: 1.5  # Z-score for "high correlation" regime
    low_corr_threshold: -1.5  # Z-score for "low correlation" regime
    instability_window: 60    # Window for instability metric
    max_instability: 0.35     # Maximum acceptable instability
    
  # Decorrelation Trading
  decorrelation_trade:
    entry_z: 2.0
    exit_z: 0.5
    stop_z: 3.5
    max_holding_bars: 60
    min_pair_correlation_long_term: 0.50  # Only trade pairs that are normally correlated
    
  # Dispersion Trading
  dispersion:
    basket_size: 10
    dispersion_lookback: 20
    entry_zscore: 2.0
    rebalance_frequency: weekly
    
  # Portfolio Construction
  portfolio:
    method: hierarchical_risk_parity  # or min_variance, max_diversification
    rebalance_frequency: weekly
    max_single_asset_weight: 0.25
    min_diversification_ratio: 1.5
    correlation_penalty: true
    
  # Risk
  risk:
    max_portfolio_vol_annual: 0.15
    max_single_pair_risk: 0.02
    max_correlated_cluster_risk: 0.05
    correlation_stress_test: 0.95  # Test with all correlations at 0.95
```

### 10.2 Data Pipeline

```yaml
data_pipeline:
  frequency: 
    correlation_update: hourly
    regime_detection: every 4 hours
    portfolio_rebalance: daily to weekly
    
  sources:
    price_data: exchange APIs (CCXT), Bloomberg, Reuters
    correlation_matrix: computed internally
    btc_dominance: CoinGecko, CoinMarketCap API
    vix: CBOE data feed
    
  storage:
    correlation_history: time-series database (rolling 2 years)
    regime_labels: classified and stored for backtesting
    trade_log: all correlation-based trades with metadata
```

---

## 11. กรอบแนวคิดทางคณิตศาสตร์ (Mathematical Framework)

### 11.1 Portfolio Variance with Correlations

$$\sigma_p^2 = \sum_i w_i^2 \sigma_i^2 + 2\sum_{i<j} w_i w_j \sigma_i \sigma_j \rho_{ij}$$

**Diversification benefit:**

$$\text{Diversification Benefit} = 1 - \frac{\sigma_p}{\sum_i w_i \sigma_i}$$

Maximum diversification occurs when $\rho_{ij} = -1/(n-1)$ (minimum possible for $n$ assets).

### 11.2 Correlation Prediction Model

**Mean-Reverting Correlation (OU for correlation):**

$$d\rho_t = \theta_\rho(\bar{\rho} - \rho_t)dt + \sigma_\rho \sqrt{\rho_t(1-\rho_t)} dW_t$$

This is a bounded OU process (correlation must stay in [-1, 1]).

**Expected Future Correlation:**

$$E[\rho_{t+h}] = \bar{\rho} + (\rho_t - \bar{\rho})e^{-\theta_\rho h}$$

### 11.3 Eigenvalue Decomposition for Correlation

$$\Sigma = V \Lambda V'$$

Where:
- $V$ = matrix of eigenvectors
- $\Lambda$ = diagonal matrix of eigenvalues $\lambda_1 \geq \lambda_2 \geq \ldots \geq \lambda_n$

**Effective Number of Independent Bets:**

$$N_{eff} = \frac{(\sum_i \lambda_i)^2}{\sum_i \lambda_i^2} = \frac{(\text{tr}(\Sigma))^2}{\text{tr}(\Sigma^2)}$$

For a crypto portfolio with high correlations, $N_{eff}$ might be only 2-3 even with 10 assets.

### 11.4 Absorption Ratio

$$AR = \frac{\sum_{i=1}^{k} \lambda_i}{\sum_{i=1}^{n} \lambda_i}$$

Where $k$ is the number of "significant" factors (e.g., first 5 eigenvalues of 20-asset matrix).

| AR Level | Interpretation | Market Condition |
|---|---|---|
| < 0.70 | Low concentration | Normal diversification |
| 0.70-0.85 | Moderate concentration | Correlation rising |
| > 0.85 | High concentration | Systemic risk elevated |
| > 0.90 | Extreme concentration | Crisis-level correlation |

**Trading Signal:**
- AR rising rapidly: Reduce leverage, increase hedges
- AR falling: Safe to increase diversified positions

### 11.5 Correlation-Based Signal Decay

The alpha of a correlation signal decays with the signal's half-life:

$$\alpha_t = \alpha_0 \times e^{-\theta_\rho t}$$

Expected holding period for correlation mean reversion trade:

$$E[\tau] \approx \frac{1}{\theta_\rho} \ln\left(\frac{|z_{entry}|}{|z_{exit}|}\right)$$

### 11.6 Expected Return from Correlation Trade

$$E[R_{corr\_trade}] = E[\Delta\rho] \times \frac{\partial V}{\partial \rho}$$

Where $\frac{\partial V}{\partial \rho}$ is the sensitivity of the trade value to correlation changes.

For a simple pair:

$$E[R] = (z_{entry} - z_{exit}) \times \sigma_{relative} \times Q$$

Where $\sigma_{relative}$ is the volatility of the relative (spread) between the two assets.

---

## 12. พารามิเตอร์ความเสี่ยง (Risk Parameters)

### 12.1 Position Sizing

**Correlation Divergence Trade:**

$$\text{Position Size} = \frac{\text{Account} \times \text{Risk\%}}{\text{Stop Distance} \times \text{Dollar per Point}}$$

Where stop distance is based on the maximum acceptable relative move before correlation thesis is invalidated.

| Trade Type | Risk per Trade | Max Concurrent | Total Risk |
|---|---|---|---|
| Correlation Divergence | 1.0% | 4 | 4% |
| BTC Dominance Rotation | 2.0% | 2 | 4% |
| Dispersion | 1.5% | 3 | 4.5% |
| Cross-Hedge | N/A (reduces risk) | N/A | N/A |

### 12.2 Stop Loss Framework

| Strategy | Stop Type | Level |
|---|---|---|
| Correlation Divergence | Z-score expansion | z_corr beyond 3.5 without price convergence |
| Correlation Divergence | Time stop | 3x expected half-life |
| Correlation Divergence | Dollar stop | 2% of account |
| BTC Dominance | Signal reversal | Dominance MAs re-cross |
| Dispersion | Dispersion expansion | Dispersion continues beyond 3-sigma |
| All | Regime change | Correlation instability > threshold |

### 12.3 Portfolio-Level Correlation Risk

```yaml
portfolio_correlation_risk:
  # Maximum concentration
  max_first_eigenvalue_pct: 70%   # First PC shouldn't explain > 70%
  min_effective_bets: 3           # At least 3 independent positions
  
  # Stress testing
  stress_correlation: 0.95
  stress_portfolio_var: calculated_at_stress_correlation < max_acceptable
  
  # Diversification requirement
  min_diversification_ratio: 1.3
  max_avg_pairwise_correlation: 0.60
  
  # Dynamic limits
  if_absorption_ratio > 0.85:
      reduce_all_positions_by: 30%
      alert: "Systemic correlation risk elevated"
```

---

## 13. ขั้นตอนการดำเนินการ (Execution Flow)

### 13.1 Complete Correlation Trading System — Pseudocode

```python
class CorrelationTradingSystem:
    """
    Complete Correlation Trading System
    Strategies: Decorrelation, Dispersion, BTC Dominance, Portfolio Construction
    Markets: Forex, Crypto
    """
    
    def __init__(self, config):
        self.config = config
        self.correlation_matrix = None
        self.correlation_history = {}
        self.positions = {}
        self.regime = 'NORMAL'
        
    def update_correlation_matrix(self, returns_data):
        """Step 1: Compute and update correlation matrix."""
        # Multiple windows
        self.corr_20 = returns_data.iloc[-20:].corr()
        self.corr_60 = returns_data.iloc[-60:].corr()
        self.corr_252 = returns_data.iloc[-252:].corr() if len(returns_data) >= 252 else returns_data.corr()
        
        # EWMA correlation
        self.corr_ewma = self.compute_ewma_correlation(returns_data, lambda_=0.94)
        
        # Store history
        for i in range(len(returns_data.columns)):
            for j in range(i+1, len(returns_data.columns)):
                pair = (returns_data.columns[i], returns_data.columns[j])
                if pair not in self.correlation_history:
                    self.correlation_history[pair] = []
                self.correlation_history[pair].append(self.corr_20.iloc[i, j])
        
        # Primary correlation matrix for trading
        self.correlation_matrix = self.corr_60
        
        return self.correlation_matrix
    
    def detect_regime(self, returns_data):
        """Step 2: Detect correlation regime."""
        # Absorption ratio
        eigenvalues = np.linalg.eigvalsh(self.correlation_matrix)
        eigenvalues = sorted(eigenvalues, reverse=True)
        ar = sum(eigenvalues[:3]) / sum(eigenvalues)
        
        # Average correlation
        n = len(self.correlation_matrix)
        avg_corr = (self.correlation_matrix.values.sum() - n) / (n * (n-1))
        
        # Effective number of bets
        n_eff = sum(eigenvalues)**2 / sum(e**2 for e in eigenvalues)
        
        # Regime classification
        if ar > 0.85 or avg_corr > 0.80:
            self.regime = 'HIGH_CORRELATION'
        elif ar < 0.60 and avg_corr < 0.50:
            self.regime = 'LOW_CORRELATION'
        else:
            self.regime = 'NORMAL'
        
        return {
            'regime': self.regime,
            'absorption_ratio': ar,
            'avg_correlation': avg_corr,
            'n_effective_bets': n_eff
        }
    
    def scan_decorrelation_opportunities(self):
        """Step 3: Find pairs with unusual correlation changes."""
        opportunities = []
        
        for pair, history in self.correlation_history.items():
            if len(history) < 60:
                continue
                
            current_corr = history[-1]
            long_term_mean = np.mean(history[-252:]) if len(history) >= 252 else np.mean(history)
            long_term_std = np.std(history[-252:]) if len(history) >= 252 else np.std(history)
            
            if long_term_std == 0:
                continue
                
            z_corr = (current_corr - long_term_mean) / long_term_std
            
            # Only trade pairs that are normally significantly correlated
            if abs(long_term_mean) < self.config['decorrelation_trade']['min_pair_correlation_long_term']:
                continue
            
            if abs(z_corr) > self.config['decorrelation_trade']['entry_z']:
                opportunities.append({
                    'pair': pair,
                    'current_corr': current_corr,
                    'long_term_corr': long_term_mean,
                    'z_score': z_corr,
                    'direction': 'DECORRELATION' if z_corr < 0 else 'CONVERGENCE'
                })
        
        return sorted(opportunities, key=lambda o: abs(o['z_score']), reverse=True)
    
    def calculate_dispersion(self, returns_data):
        """Step 4: Calculate cross-sectional dispersion."""
        # Cross-sectional standard deviation of returns
        dispersion = returns_data.iloc[-20:].std(axis=1).mean()
        
        # Historical dispersion for z-score
        historical_dispersions = []
        for t in range(20, len(returns_data)):
            d = returns_data.iloc[t-20:t].std(axis=1).mean()
            historical_dispersions.append(d)
        
        if len(historical_dispersions) < 60:
            return None
            
        z_dispersion = (dispersion - np.mean(historical_dispersions)) / np.std(historical_dispersions)
        
        return {
            'current_dispersion': dispersion,
            'z_score': z_dispersion,
            'signal': 'SELL_DISPERSION' if z_dispersion > 2.0 else
                      'BUY_DISPERSION' if z_dispersion < -2.0 else 'NEUTRAL'
        }
    
    def generate_portfolio_weights(self, returns_data):
        """Step 5: Generate optimal portfolio weights using correlation."""
        if self.config['portfolio']['method'] == 'hierarchical_risk_parity':
            weights = self.hierarchical_risk_parity(returns_data)
        elif self.config['portfolio']['method'] == 'min_variance':
            weights = self.minimum_variance_portfolio(returns_data)
        elif self.config['portfolio']['method'] == 'max_diversification':
            weights = self.maximum_diversification_portfolio(returns_data)
        else:
            weights = self.equal_weight(returns_data)
        
        # Apply constraints
        weights = self.apply_constraints(weights)
        
        return weights
    
    def execute_correlation_trade(self, opportunity, returns_data):
        """Step 6: Execute a correlation-based trade."""
        pair = opportunity['pair']
        asset_a, asset_b = pair
        
        # Determine which asset is cheap/expensive
        relative_perf = (returns_data[asset_a].iloc[-20:].sum() - 
                        returns_data[asset_b].iloc[-20:].sum())
        
        if opportunity['direction'] == 'DECORRELATION':
            # Assets decorrelated — bet on convergence
            if relative_perf > 0:
                # A outperformed: Short A, Long B
                long_asset = asset_b
                short_asset = asset_a
            else:
                # B outperformed: Short B, Long A
                long_asset = asset_a
                short_asset = asset_b
        else:
            # Correlation too high — bet on divergence
            # This is less common; typically wait for specific catalyst
            return None
        
        # Position sizing
        risk_amount = self.account * self.config['decorrelation_trade'].get('risk_per_trade', 0.01)
        relative_vol = np.std(returns_data[asset_a] - returns_data[asset_b]) * np.sqrt(252)
        stop_distance = self.config['decorrelation_trade']['stop_z'] * relative_vol
        
        notional = risk_amount / stop_distance
        
        # Execute
        self.exchange.buy(long_asset, notional / self.get_price(long_asset))
        self.exchange.sell(short_asset, notional / self.get_price(short_asset))
        
        self.positions[f"{asset_a}_{asset_b}_corr"] = {
            'type': 'decorrelation',
            'long': long_asset,
            'short': short_asset,
            'notional': notional,
            'entry_z_corr': opportunity['z_score'],
            'entry_relative_perf': relative_perf,
            'entry_date': datetime.now(),
            'bars_held': 0
        }
    
    def manage_positions(self, returns_data):
        """Step 7: Manage open correlation positions."""
        for pos_id, pos in list(self.positions.items()):
            pos['bars_held'] += 1
            
            if pos['type'] == 'decorrelation':
                # Check if correlation has normalized
                pair = (pos['long'], pos['short'])  # approximate
                current_z = self.get_current_z_corr(pair)
                
                # Exit conditions
                should_exit = False
                reason = ""
                
                if abs(current_z) < self.config['decorrelation_trade']['exit_z']:
                    should_exit = True
                    reason = "Correlation normalized"
                
                if pos['bars_held'] > self.config['decorrelation_trade']['max_holding_bars']:
                    should_exit = True
                    reason = "Time stop"
                
                # Check if trade is profitable (relative price converged)
                current_relative = (returns_data[pos['long']].iloc[-pos['bars_held']:].sum() - 
                                   returns_data[pos['short']].iloc[-pos['bars_held']:].sum())
                
                if current_relative < -self.config['decorrelation_trade'].get('max_loss', 0.05):
                    should_exit = True
                    reason = "Maximum loss exceeded"
                
                if should_exit:
                    self.close_position(pos_id, reason)
    
    def run(self, data_feed):
        """Step 8: Main execution loop."""
        for timestamp, data in data_feed:
            returns_data = self.compute_returns(data)
            
            # Update correlation matrix
            self.update_correlation_matrix(returns_data)
            
            # Detect regime
            regime_info = self.detect_regime(returns_data)
            
            # Manage existing positions
            self.manage_positions(returns_data)
            
            # Generate new signals
            if self.regime != 'HIGH_CORRELATION':  # Avoid new positions during crisis
                opportunities = self.scan_decorrelation_opportunities()
                
                for opp in opportunities[:3]:  # Max 3 new positions per scan
                    if f"{opp['pair'][0]}_{opp['pair'][1]}_corr" not in self.positions:
                        if len(self.positions) < self.config.get('max_positions', 5):
                            self.execute_correlation_trade(opp, returns_data)
            
            # Portfolio rebalancing (if using correlation for portfolio construction)
            if self.should_rebalance(timestamp):
                weights = self.generate_portfolio_weights(returns_data)
                self.rebalance_portfolio(weights)
            
            # Log and monitor
            self.log_status(regime_info, self.positions)
```

### 13.2 Execution Flow Diagram

```
┌───────────────────────────────────────────────────┐
│        CORRELATION TRADING EXECUTION FLOW         │
├───────────────────────────────────────────────────┤
│                                                   │
│  1. DATA & CORRELATION UPDATE (Hourly/Daily)      │
│     ├─ Fetch returns for all universe assets      │
│     ├─ Compute rolling correlation matrices       │
│     │   (20d, 60d, 252d, EWMA)                   │
│     ├─ Store correlation history                  │
│     └─ Compute eigenvalues and metrics            │
│                                                   │
│  2. REGIME DETECTION                              │
│     ├─ Absorption ratio calculation               │
│     ├─ Average correlation level                  │
│     ├─ Effective number of bets                   │
│     ├─ Classify: HIGH / NORMAL / LOW correlation  │
│     └─ Alert if regime changes                    │
│                                                   │
│  3. OPPORTUNITY SCANNING                          │
│     ├─ Calculate z-score of each pair's           │
│     │   correlation vs long-term                  │
│     ├─ Identify decorrelation opportunities       │
│     ├─ Calculate cross-sectional dispersion       │
│     ├─ BTC dominance analysis (crypto)            │
│     └─ Dollar smile regime (forex)                │
│                                                   │
│  4. SIGNAL GENERATION                             │
│     ├─ Filter by minimum long-term correlation    │
│     ├─ Filter by regime appropriateness           │
│     ├─ Rank by z-score magnitude                  │
│     └─ Select top opportunities                   │
│                                                   │
│  5. POSITION MANAGEMENT                           │
│     ├─ Monitor correlation z-scores               │
│     ├─ Check relative price convergence           │
│     ├─ Time stop enforcement                      │
│     ├─ Loss limit monitoring                      │
│     └─ Exit on normalization or failure            │
│                                                   │
│  6. PORTFOLIO CONSTRUCTION                        │
│     ├─ HRP / MinVar / MaxDiv weight calculation   │
│     ├─ Correlation-adjusted position sizing       │
│     ├─ Diversification ratio monitoring           │
│     └─ Periodic rebalancing                       │
│                                                   │
│  7. HEDGING                                       │
│     ├─ Calculate optimal hedge ratios             │
│     ├─ Monitor hedge effectiveness                │
│     ├─ Adjust hedges for correlation drift        │
│     └─ Report tracking error                      │
│                                                   │
│  8. REPORTING & MONITORING                        │
│     ├─ Correlation regime dashboard               │
│     ├─ Trade P&L attribution                      │
│     ├─ Diversification metrics                    │
│     └─ Stress test results                        │
│                                                   │
└───────────────────────────────────────────────────┘
```

---

## 14. เอกสารอ้างอิง (References)

### Academic Papers

1. **Engle, R.F.** (2002). "Dynamic Conditional Correlation: A Simple Class of Multivariate Generalized Autoregressive Conditional Heteroskedasticity Models." *Journal of Business & Economic Statistics*, 20(3), 339-350.
2. **Longin, F., & Solnik, B.** (2001). "Extreme Correlation of International Equity Markets." *Journal of Finance*, 56(2), 649-676.
3. **Lopez de Prado, M.** (2016). "Building Diversified Portfolios that Outperform Out of Sample." *Journal of Portfolio Management*, 42(4), 59-69.
4. **Choueifaty, Y., & Coignard, Y.** (2008). "Toward Maximum Diversification." *Journal of Portfolio Management*, 35(1), 40-51.
5. **Maillard, S., Roncalli, T., & Teiletche, J.** (2010). "The Properties of Equally Weighted Risk Contribution Portfolios." *Journal of Portfolio Management*, 36(4), 60-70.
6. **Kritzman, M., Li, Y., Page, S., & Rigobon, R.** (2011). "Principal Components as a Measure of Systemic Risk." *Journal of Portfolio Management*, 37(4), 112-126.
7. **Bollerslev, T.** (1990). "Modelling the Coherence in Short-Run Nominal Exchange Rates: A Multivariate Generalized ARCH Model." *Review of Economics and Statistics*, 72(3), 498-505.
8. **Ang, A., & Chen, J.** (2002). "Asymmetric Correlations of Equity Portfolios." *Journal of Financial Economics*, 63(3), 443-494.
9. **Forbes, K.J., & Rigobon, R.** (2002). "No Contagion, Only Interdependence: Measuring Stock Market Comovements." *Journal of Finance*, 57(5), 2223-2261.
10. **Jen, S.** (2001). "The Dollar Smile." *Morgan Stanley Research Note*.

### Practitioner Resources

11. **Ilmanen, A.** (2011). *Expected Returns*. Wiley. (Chapter on diversification and correlation.)
12. **Roncalli, T.** (2014). *Introduction to Risk Parity and Budgeting*. Chapman & Hall.
13. **Qian, E.** (2016). *Risk Parity Fundamentals*. CRC Press.
14. **Narang, R.** (2013). *Inside the Black Box*. Wiley. (Correlation in systematic trading.)

### Software and Tools

15. **scikit-learn**: PCA, clustering for correlation analysis
16. **statsmodels**: DCC-GARCH, correlation tests
17. **NetworkX**: Correlation network visualization
18. **scipy.cluster.hierarchy**: Hierarchical clustering for HRP

---

*เอกสารนี้เป็นส่วนหนึ่งของฐานความรู้ระบบเทรด AI แบบ Multi-Agent การเทรดตามสหสัมพันธ์ให้ Alpha โดยใช้ประโยชน์จากการเบี่ยงเบนจากความสัมพันธ์ระหว่างสินทรัพย์ปกติ และช่วยให้สร้างพอร์ตโฟลิโอได้ดีขึ้นผ่านความเข้าใจโครงสร้างสหสัมพันธ์แบบไดนามิกของตลาด*
