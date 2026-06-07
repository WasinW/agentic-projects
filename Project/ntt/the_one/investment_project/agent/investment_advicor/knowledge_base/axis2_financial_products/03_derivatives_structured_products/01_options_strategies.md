# Options Strategies: Comprehensive Guide

> **Axis 2 — Financial Products | Module 03: Derivatives & Structured Products**
> **Document 01 — Options Strategies Comprehensive Guide**
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

### 1.1 Option Fundamentals

#### 1.1.1 Call Options

A call option grants the holder the right to **buy** the underlying asset at the strike price $K$ on or before expiration $T$.

**Payoff at Expiration:**

$$\text{Call Payoff} = \max(S_T - K, 0)$$

$$\text{Call P\&L} = \max(S_T - K, 0) - C_0$$

Where:
- $S_T$ = Underlying price at expiration
- $K$ = Strike price
- $C_0$ = Premium paid for the call

#### 1.1.2 Put Options

A put option grants the holder the right to **sell** the underlying asset at the strike price $K$ on or before expiration $T$.

**Payoff at Expiration:**

$$\text{Put Payoff} = \max(K - S_T, 0)$$

$$\text{Put P\&L} = \max(K - S_T, 0) - P_0$$

Where $P_0$ = Premium paid for the put.

#### 1.1.3 American vs European Options

| Feature | American | European |
|---|---|---|
| Exercise | Any time before expiry | Only at expiry |
| Pricing | More complex (binomial tree, finite difference) | Black-Scholes closed-form |
| Premium | ≥ European (early exercise premium) | Baseline |
| Common In | Equity options (US exchanges) | Forex OTC, Crypto (Deribit) |
| Early Exercise Optimal | Deep ITM puts, dividend-paying stocks | Never optimal without dividends |

#### 1.1.4 Crypto Options Specifics

**Unique characteristics of crypto options markets:**

1. **European Style Only**: All major crypto exchanges (Deribit, OKX, Binance) offer European options
2. **Cash Settlement**: Settled in the underlying cryptocurrency (BTC/ETH on Deribit) or USDC
3. **Settlement Price**: Deribit uses 30-minute TWAP of the index at 08:00 UTC on expiry
4. **Tick Size**: $0.0005 BTC for BTC options on Deribit (notional depends on BTC price)
5. **Contract Size**: 1 BTC per contract (Deribit), 0.01 BTC (Binance)
6. **Expiry Schedule**: Daily, weekly, monthly, quarterly expirations available
7. **High Base IV**: BTC ATM IV typically 50-80%, ETH 60-100% (vs 15-25% for SPX)
8. **IV Term Structure**: Often inverted around events; typically upward-sloping in calm markets
9. **Skew**: Persistent put skew in BTC/ETH (crash protection demand)
10. **Block Trading**: Available via Paradigm protocol for large orders
11. **Portfolio Margin**: Deribit offers portfolio margin for reduced capital requirements

**Crypto Options Market Size (as of 2026):**
- BTC options open interest: >$20B notional
- ETH options open interest: >$10B notional
- Daily volume: $2-5B notional
- Deribit market share: ~80%

### 1.2 Black-Scholes-Merton Model

The Black-Scholes-Merton (BSM) model provides closed-form solutions for European option pricing under the following assumptions:

**Assumptions:**
1. Log-normal distribution of returns
2. Constant volatility $\sigma$
3. Constant risk-free rate $r$
4. No transaction costs or taxes
5. Continuous trading possible
6. No dividends (Merton extension handles dividends)
7. No arbitrage opportunities

**European Call Price:**

$$C = S_0 N(d_1) - Ke^{-rT}N(d_2)$$

**European Put Price:**

$$P = Ke^{-rT}N(-d_2) - S_0 N(-d_1)$$

**Key Parameters:**

$$d_1 = \frac{\ln(S_0/K) + (r + \sigma^2/2)T}{\sigma\sqrt{T}}$$

$$d_2 = d_1 - \sigma\sqrt{T}$$

Where:
- $S_0$ = Current spot price of underlying
- $K$ = Strike price
- $T$ = Time to expiration (in years)
- $r$ = Risk-free interest rate (annualized)
- $\sigma$ = Volatility of the underlying (annualized)
- $N(\cdot)$ = Cumulative standard normal distribution function

**Put-Call Parity:**

$$C - P = S_0 - Ke^{-rT}$$

This fundamental relationship must hold for European options; violations indicate arbitrage opportunities.

**BSM Limitations for Crypto:**
- Crypto returns exhibit fat tails (kurtosis > 3)
- Volatility is stochastic, not constant
- Jump risk is significant (exchange hacks, regulatory news)
- 24/7 trading with variable liquidity
- Staking yields act as continuous dividends for some assets

**Practical Adjustments:**
- Use implied volatility rather than historical volatility for pricing
- Apply stochastic volatility models (Heston, SABR) for more accurate Greeks
- Adjust for jump risk using Merton's jump-diffusion model
- Use realized vol estimators robust to microstructure noise (Yang-Zhang, Garman-Klass)

### 1.3 The Greeks — Detailed Analysis

#### 1.3.1 Delta (Δ) — Directional Risk

**Definition:** Rate of change of option price with respect to the underlying price.

$$\Delta_{call} = N(d_1) = \frac{\partial C}{\partial S}$$

$$\Delta_{put} = N(d_1) - 1 = \frac{\partial P}{\partial S}$$

**Properties:**
- Call delta ranges from 0 to +1
- Put delta ranges from -1 to 0
- ATM options have delta ≈ ±0.50
- Delta approaches ±1 for deep ITM options
- Delta approaches 0 for deep OTM options
- Delta is approximately the probability of expiring ITM (under risk-neutral measure)

**Delta as Hedge Ratio:**
To delta-hedge a short call position, buy Δ shares of the underlying for each option sold.

**Example:**
- Short 10 BTC call options, each with delta = 0.45
- Portfolio delta = -10 × 0.45 = -4.5 BTC
- Hedge: Buy 4.5 BTC in spot/perp to achieve delta-neutral

**Delta-Neutral Strategies:**
- Market makers continuously delta-hedge to isolate other Greeks
- Delta-neutral allows profit from gamma, theta, or vega
- Requires dynamic rebalancing as delta changes with price

**Delta in Crypto Context:**
- BTC delta-hedging is done via perpetual swaps (most liquid)
- Funding rate cost must be factored into delta-hedge cost
- Large spot moves require frequent rebalancing due to high gamma

#### 1.3.2 Gamma (Γ) — Convexity Risk

**Definition:** Rate of change of delta with respect to the underlying price.

$$\Gamma = \frac{\partial^2 V}{\partial S^2} = \frac{N'(d_1)}{S_0 \sigma \sqrt{T}}$$

Where $N'(x) = \frac{1}{\sqrt{2\pi}}e^{-x^2/2}$

**Properties:**
- Always positive for long options (both calls and puts)
- Highest for ATM options near expiry
- Represents the curvature of the option's payoff
- Long gamma = profit from large moves (convexity)
- Short gamma = profit from small moves (time decay), risk from large moves

**Gamma Risk Near Expiry:**
As $T \to 0$, ATM gamma approaches infinity. This creates "pin risk" — extreme sensitivity to small price changes near expiry.

**Dollar Gamma:**
$$\text{Dollar Gamma} = \frac{1}{2} \Gamma S^2 \times (\Delta S / S)^2$$

For a 1% move: Dollar Gamma per 1% = $\frac{1}{2} \Gamma S^2 \times 0.01^2$

**Gamma Scalping:**
Long gamma positions can be monetized through delta rebalancing:
1. Start delta-neutral with long gamma
2. Price rises → delta becomes positive → sell delta (take profit)
3. Price falls → delta becomes negative → buy delta (take profit)
4. Rinse and repeat; profitable if realized vol > implied vol paid

#### 1.3.3 Theta (Θ) — Time Decay

**Definition:** Rate of change of option price with respect to time.

$$\Theta_{call} = -\frac{S_0 N'(d_1) \sigma}{2\sqrt{T}} - rKe^{-rT}N(d_2)$$

$$\Theta_{put} = -\frac{S_0 N'(d_1) \sigma}{2\sqrt{T}} + rKe^{-rT}N(-d_2)$$

**Properties:**
- Negative for long options (time works against the holder)
- Positive for short options (time works in favor of the writer)
- Theta is largest for ATM options
- Theta accelerates as expiration approaches (non-linear decay)
- Theta-gamma tradeoff: $\Theta + \frac{1}{2}\sigma^2 S^2 \Gamma + rS\Delta = rV$

**Theta Decay Curve:**
- At 60 DTE: Theta is moderate, relatively constant day-to-day
- At 30 DTE: Theta begins accelerating
- At 14 DTE: Theta acceleration intensifies
- At 7 DTE: Theta decay is very rapid for ATM options
- At 1 DTE: Nearly all remaining time value lost

**Crypto Theta Considerations:**
- Crypto markets trade 24/7, so theta decays continuously (no weekends)
- No "weekend theta" effect like equity options
- Higher IV means higher absolute theta values
- Short-dated crypto options have extreme theta due to high IV

#### 1.3.4 Vega (ν) — Volatility Sensitivity

**Definition:** Rate of change of option price with respect to implied volatility.

$$\nu = S_0 \sqrt{T} N'(d_1)$$

**Properties:**
- Always positive for long options
- Highest for ATM options with long time to expiry
- Expressed as change in option price per 1% (1 vol point) change in IV
- Long vega: Profit when IV increases
- Short vega: Profit when IV decreases

**Vega in Crypto:**
- BTC vega is substantial due to high base IV
- Example: ATM BTC option at 60% IV, 30 DTE might have vega of 0.002 BTC per vol point
- A 5-point IV change = 0.01 BTC per contract = significant at $60K BTC
- IV crush after events (ETF decisions, halvings, FOMC) can devastate long vega positions
- IV expansion during uncertainty benefits long vega positions

#### 1.3.5 Rho (ρ) — Interest Rate Sensitivity

**Definition:** Rate of change of option price with respect to the risk-free rate.

$$\rho_{call} = KTe^{-rT}N(d_2)$$

$$\rho_{put} = -KTe^{-rT}N(-d_2)$$

**Properties:**
- Positive for calls, negative for puts
- More significant for long-dated options
- Less important for crypto (short-dated, high vol dominates)
- Relevant for FX options where interest rate differentials matter

#### 1.3.6 Higher-Order Greeks

**Vanna (∂Δ/∂σ = ∂ν/∂S):**

$$\text{Vanna} = \frac{\nu}{S}\left(1 - \frac{d_1}{\sigma\sqrt{T}}\right)$$

Important for: Understanding how delta changes with IV (critical for options on crypto with volatile IV)

**Charm (∂Δ/∂t):**

$$\text{Charm} = -N'(d_1)\left(\frac{2(r-q)T - d_2\sigma\sqrt{T}}{2T\sigma\sqrt{T}}\right)$$

Important for: Understanding how delta changes overnight; affects daily delta-hedging requirements

**Volga/Vomma (∂²V/∂σ²):**

$$\text{Volga} = \nu \cdot \frac{d_1 d_2}{\sigma}$$

Important for: Understanding the convexity of vega exposure; critical for managing large vega positions

---

## 1.4 Strategy Catalog

### Category A: Directional Strategies

---

#### A1. Long Call

**Description:** Buy a call option to profit from bullish price movement.

**Construction:**
- Buy 1 Call at strike $K$ with premium $C$

**Payoff Diagram:**
```
P&L
  │          ╱
  │         ╱
  │        ╱
  │       ╱
──┼──────●─────── Price
  │      K
  │
 -C ─────────────
  │
```

**Formulas:**
- **Max Profit:** Unlimited = $S_T - K - C$ (as $S_T \to \infty$)
- **Max Loss:** $C$ (premium paid)
- **Break-even:** $S_{BE} = K + C$

**Optimal Market Conditions:**
- Strong bullish directional conviction
- Low IV environment (cheap premium)
- IV Rank < 30 preferred (buying cheap volatility)
- Expected move larger than premium paid

**Greeks Profile:**
| Greek | Sign | Magnitude | Implication |
|---|---|---|---|
| Delta | + | 0 to +1 | Benefits from price increase |
| Gamma | + | Positive | Delta increases as price rises |
| Theta | - | Negative | Time decay hurts position |
| Vega | + | Positive | Benefits from IV increase |

**Entry Rules:**
1. IV Rank < 30 (buying when vol is cheap)
2. Strong bullish signal from technical/fundamental analysis
3. Select strike based on desired delta:
   - ATM (Δ≈0.50): Maximum gamma, highest probability of profit vs cost
   - Slightly OTM (Δ≈0.30): Cheaper premium, lower probability
   - ITM (Δ≈0.70): Higher cost, higher probability, lower leverage
4. Select expiration: 30-60 DTE (balance between theta decay and time for thesis)

**Exit Rules:**
1. Profit target: 50-100% return on premium
2. Stop loss: 50% of premium lost
3. Time exit: Close at 14 DTE if target not reached (theta acceleration)
4. IV crush exit: Close if IV drops significantly (vega loss exceeds directional gain)
5. Thesis invalidation: Close if bullish signal reverses

**Risk Parameters:**
```
LONG_CALL_LIMITS:
  max_premium_per_trade: 2% of portfolio
  max_total_long_calls: 5% of portfolio in premium
  min_days_to_expiry: 21 DTE at entry
  max_days_to_expiry: 90 DTE
  preferred_delta_range: [0.30, 0.70]
  profit_target_pct: 50-100%
  stop_loss_pct: 50%
  time_exit_dte: 14
```

---

#### A2. Long Put

**Description:** Buy a put option to profit from bearish price movement.

**Construction:**
- Buy 1 Put at strike $K$ with premium $P$

**Payoff Diagram:**
```
P&L
  │
  │ ╲
  │  ╲
  │   ╲
  │    ╲
──┼─────●──────── Price
  │     K
  │
 -P ─────────────
  │
```

**Formulas:**
- **Max Profit:** $K - P$ (underlying goes to zero)
- **Max Loss:** $P$ (premium paid)
- **Break-even:** $S_{BE} = K - P$

**Optimal Market Conditions:**
- Strong bearish directional conviction
- Low IV environment (buy cheap)
- IV Rank < 30
- Expecting significant downside move

**Greeks Profile:**
| Greek | Sign | Magnitude | Implication |
|---|---|---|---|
| Delta | - | -1 to 0 | Benefits from price decrease |
| Gamma | + | Positive | Delta becomes more negative as price falls |
| Theta | - | Negative | Time decay hurts position |
| Vega | + | Positive | Benefits from IV increase (common in selloffs) |

**Entry Rules:**
1. IV Rank < 30 (cheap vol)
2. Bearish signal confirmed (technical breakdown, negative catalyst)
3. Select strike: ATM to slightly OTM (Δ = -0.30 to -0.50)
4. Expiration: 30-60 DTE

**Exit Rules:**
1. Profit target: 50-100% return on premium
2. Stop loss: 50% premium lost
3. Time exit: 14 DTE
4. Thesis invalidation: Bearish signal reverses

**Risk Parameters:**
```
LONG_PUT_LIMITS:
  max_premium_per_trade: 2% of portfolio
  max_total_long_puts: 5% of portfolio in premium
  min_days_to_expiry: 21 DTE
  max_days_to_expiry: 90 DTE
  preferred_delta_range: [-0.70, -0.30]
  profit_target_pct: 50-100%
  stop_loss_pct: 50%
  time_exit_dte: 14
```

---

#### A3. Bull Call Spread (Debit Spread)

**Description:** Buy a call at lower strike, sell a call at higher strike. Reduces cost at the expense of capped upside.

**Construction:**
- Buy 1 Call at strike $K_1$ (lower), pay premium $C_1$
- Sell 1 Call at strike $K_2$ (higher, $K_2 > K_1$), receive premium $C_2$
- Net Debit = $C_1 - C_2$

**Payoff Diagram:**
```
P&L
  │        ┌────────
  │       ╱
  │      ╱
  │     ╱
──┼────●────●────── Price
  │    K1   K2
 Net ──────────────
Debit
```

**Formulas:**
- **Max Profit:** $(K_2 - K_1) - (C_1 - C_2)$ = Width of spread - Net debit
- **Max Loss:** $C_1 - C_2$ = Net debit paid
- **Break-even:** $S_{BE} = K_1 + (C_1 - C_2)$
- **Risk/Reward Ratio:** Net Debit / (Width - Net Debit)

**Optimal Market Conditions:**
- Moderately bullish outlook
- Any IV environment (spread reduces vega exposure)
- When long call is too expensive due to elevated IV
- Defined risk/reward preferred

**Greeks Profile:**
| Greek | Sign | Magnitude | Implication |
|---|---|---|---|
| Delta | + | Moderate (net positive) | Benefits from price increase |
| Gamma | ± | Small (partially offset) | Reduced convexity vs naked call |
| Theta | ± | Small (partially offset) | Less theta drag than naked call |
| Vega | + | Small (partially offset) | Reduced vol sensitivity |

**Entry Rules:**
1. Moderately bullish conviction
2. Buy ATM or slightly ITM call ($K_1$)
3. Sell OTM call ($K_2$) at target price or resistance level
4. Width selection: Narrower = cheaper, lower max profit; wider = more expensive, higher max profit
5. Expiration: 30-45 DTE
6. Target debit: < 50% of spread width (ensures >1:1 reward-to-risk)

**Exit Rules:**
1. Profit target: 50-75% of max profit
2. Stop loss: 50% of debit paid
3. Time exit: 14 DTE
4. If underlying reaches $K_2$ early, consider closing to capture most of max profit

**Risk Parameters:**
```
BULL_CALL_SPREAD_LIMITS:
  max_debit_per_trade: 2% of portfolio
  max_spread_width: 10% of underlying price
  min_reward_to_risk: 1.0
  min_days_to_expiry: 21 DTE
  max_days_to_expiry: 60 DTE
  profit_target_pct_of_max: 50-75%
  stop_loss_pct_of_debit: 50%
```

---

#### A4. Bear Put Spread (Debit Spread)

**Description:** Buy a put at higher strike, sell a put at lower strike. Defined-risk bearish strategy.

**Construction:**
- Buy 1 Put at strike $K_2$ (higher), pay premium $P_2$
- Sell 1 Put at strike $K_1$ (lower, $K_1 < K_2$), receive premium $P_1$
- Net Debit = $P_2 - P_1$

**Payoff Diagram:**
```
P&L
  │
  │ ────────┐
  │          ╲
  │           ╲
──┼────●────●──── Price
  │    K1   K2
 Net ──────────────
Debit
```

**Formulas:**
- **Max Profit:** $(K_2 - K_1) - (P_2 - P_1)$ = Width - Net debit
- **Max Loss:** $P_2 - P_1$ = Net debit paid
- **Break-even:** $S_{BE} = K_2 - (P_2 - P_1)$

**Optimal Market Conditions:**
- Moderately bearish outlook
- Any IV environment
- Defined risk preferred

**Greeks Profile:**
| Greek | Sign | Magnitude | Implication |
|---|---|---|---|
| Delta | - | Moderate (net negative) | Benefits from price decrease |
| Gamma | ± | Small | Reduced convexity |
| Theta | ± | Small | Partially offset |
| Vega | + | Small | Slight benefit from IV rise |

**Entry Rules:**
1. Moderately bearish conviction
2. Buy ATM or slightly ITM put ($K_2$)
3. Sell OTM put ($K_1$) at support level
4. Expiration: 30-45 DTE
5. Target debit: < 50% of spread width

**Exit Rules:**
1. Profit target: 50-75% of max profit
2. Stop loss: 50% of debit
3. Time exit: 14 DTE

**Risk Parameters:**
```
BEAR_PUT_SPREAD_LIMITS:
  max_debit_per_trade: 2% of portfolio
  max_spread_width: 10% of underlying price
  min_reward_to_risk: 1.0
  min_days_to_expiry: 21 DTE
  profit_target_pct_of_max: 50-75%
  stop_loss_pct_of_debit: 50%
```

---

### Category B: Neutral / Income Strategies

---

#### B1. Short Straddle

**Description:** Sell both a call and put at the same strike (typically ATM). Maximum premium collection, unlimited risk.

**Construction:**
- Sell 1 ATM Call at strike $K$, receive premium $C$
- Sell 1 ATM Put at strike $K$, receive premium $P$
- Total Credit = $C + P$

**Payoff Diagram:**
```
P&L
 C+P ──────┐  ┌──────
           ╲╱
            │
──────────●────────── Price
           K
```

**Formulas:**
- **Max Profit:** $C + P$ (at expiration, $S_T = K$ exactly)
- **Max Loss:** Unlimited (to upside); $K - (C + P)$ to downside
- **Break-even (upper):** $S_{BE,up} = K + C + P$
- **Break-even (lower):** $S_{BE,down} = K - (C + P)$
- **Breakeven Range Width:** $2 \times (C + P)$

**Optimal Market Conditions:**
- Range-bound market expectation
- High IV environment (IV Rank > 50, ideally > 70)
- No major catalysts expected before expiry
- Expecting realized vol < implied vol

**Greeks Profile:**
| Greek | Sign | Magnitude | Implication |
|---|---|---|---|
| Delta | ≈ 0 | Near zero at entry | Market neutral |
| Gamma | - | Large negative | Large moves hurt significantly |
| Theta | + | Large positive | Time decay benefits position |
| Vega | - | Large negative | IV decrease benefits position |

**Entry Rules:**
1. IV Rank > 50 (selling expensive volatility)
2. No major events in the next 7 days
3. Strike selection: ATM (maximizes theta and premium)
4. Expiration: 30-45 DTE (optimal theta decay curve)
5. Must have sufficient margin for naked short options

**Exit Rules:**
1. Profit target: 25-50% of max credit (don't wait for full decay)
2. Stop loss: Credit received × 2 (e.g., collected $500, close if loss reaches $1000)
3. Time exit: 21 DTE (gamma risk increases)
4. Delta adjustment: If portfolio delta exceeds ±0.20, adjust with underlying
5. Breach of either breakeven: Immediately reassess

**Risk Parameters:**
```
SHORT_STRADDLE_LIMITS:
  max_credit_per_trade: 3% of portfolio
  min_iv_rank: 50
  max_portfolio_short_gamma: defined by risk framework
  min_days_to_expiry: 25 DTE at entry
  max_days_to_expiry: 60 DTE
  profit_target_pct: 25-50% of credit
  stop_loss_multiple: 2x credit
  time_exit_dte: 21
  max_delta_drift: 0.20 before adjustment
  REQUIRES_MARGIN: true
  RISK_LEVEL: HIGH
```

---

#### B2. Short Strangle

**Description:** Sell an OTM call and OTM put. Wider profit range than straddle, lower premium collected.

**Construction:**
- Sell 1 OTM Call at strike $K_2$ ($K_2 > S_0$), receive premium $C$
- Sell 1 OTM Put at strike $K_1$ ($K_1 < S_0$), receive premium $P$
- Total Credit = $C + P$

**Payoff Diagram:**
```
P&L
 C+P ──┐          ┌──────
       ╲          ╱
        ╲────────╱
──────●──────────●──── Price
      K1         K2
```

**Formulas:**
- **Max Profit:** $C + P$ (if $K_1 \leq S_T \leq K_2$)
- **Max Loss:** Unlimited (to upside); $K_1 - (C + P)$ to downside
- **Break-even (upper):** $S_{BE,up} = K_2 + (C + P)$
- **Break-even (lower):** $S_{BE,down} = K_1 - (C + P)$

**Optimal Market Conditions:**
- Range-bound market
- High IV environment (IV Rank > 50)
- Stable volatility expected
- No major catalysts

**Greeks Profile:**
| Greek | Sign | Magnitude | Implication |
|---|---|---|---|
| Delta | ≈ 0 | Near zero (if symmetric strikes) | Market neutral |
| Gamma | - | Negative (less than straddle) | Large moves hurt |
| Theta | + | Positive | Time decay benefits |
| Vega | - | Negative | IV decrease benefits |

**Entry Rules:**
1. IV Rank > 50
2. Select strikes at 1 standard deviation (16-delta) or further:
   - Call strike: Δ ≈ 0.16 (84% probability OTM)
   - Put strike: Δ ≈ -0.16 (84% probability OTM)
3. This gives approximately 68% probability of both options expiring OTM
4. Expiration: 30-45 DTE
5. Collect minimum 1/3 of the width between strikes

**Exit Rules:**
1. Profit target: 50% of credit received
2. Stop loss: 2x credit received on either side
3. If tested (underlying approaches a strike), roll untested side closer to collect more premium
4. Time exit: 21 DTE

**Risk Parameters:**
```
SHORT_STRANGLE_LIMITS:
  max_credit_per_trade: 3% of portfolio
  min_iv_rank: 50
  min_strike_distance: 1.0 standard deviations
  preferred_delta: 0.16 (each side)
  min_days_to_expiry: 25 DTE
  profit_target_pct: 50% of credit
  stop_loss_multiple: 2x credit
  time_exit_dte: 21
  REQUIRES_MARGIN: true
  RISK_LEVEL: HIGH
```

---

#### B3. Iron Condor

**Description:** Sell a strangle, buy a wider strangle for protection. Defined risk version of short strangle.

**Construction:**
- Buy 1 OTM Put at strike $K_1$ (lowest), pay $P_1$
- Sell 1 OTM Put at strike $K_2$ ($K_2 > K_1$), receive $P_2$
- Sell 1 OTM Call at strike $K_3$ ($K_3 > K_2$), receive $C_3$
- Buy 1 OTM Call at strike $K_4$ (highest, $K_4 > K_3$), pay $C_4$
- Net Credit = $(P_2 + C_3) - (P_1 + C_4)$

**Payoff Diagram:**
```
P&L
 Net  ──┐          ┌──────
Credit  ╲          ╱
         ╲────────╱
────●─────●────────●─────●── Price
    K1    K2       K3    K4
-Width+Credit ──────────────
```

**Formulas:**
- **Max Profit:** Net Credit received
- **Max Loss:** Width of wider spread - Net Credit = $(K_2 - K_1) - \text{Net Credit}$ (assuming equal width)
- **Break-even (upper):** $S_{BE,up} = K_3 + \text{Net Credit}$
- **Break-even (lower):** $S_{BE,down} = K_2 - \text{Net Credit}$
- **Probability of Profit (approx):** Width of profit zone / Total range, or use delta-based estimate

**Optimal Market Conditions:**
- Range-bound market, neutral outlook
- High IV (IV Rank > 30, ideally > 50)
- Expecting low realized volatility
- Prefer to define risk (vs naked strangle)

**Greeks Profile:**
| Greek | Sign | Magnitude | Implication |
|---|---|---|---|
| Delta | ≈ 0 | Near zero at entry | Market neutral |
| Gamma | - | Small to moderate negative | Large moves hurt but loss is capped |
| Theta | + | Positive | Time decay benefits |
| Vega | - | Negative | IV decrease benefits |

**Entry Rules:**
1. IV Rank > 30 (ideally > 50)
2. Short strikes at 1 standard deviation (16-delta):
   - Short put ($K_2$): Δ ≈ -0.16
   - Short call ($K_3$): Δ ≈ 0.16
3. Long wings 1-2 strikes wider (e.g., $5 wide for BTC options)
4. Wing width determines max loss
5. Collect at least 1/3 of wing width as credit
6. Expiration: 30-45 DTE

**Exit Rules:**
1. Profit target: 50% of max credit
2. Stop loss: 2x credit received OR if underlying breaches short strike
3. Time exit: 21 DTE
4. Adjustment: If one side tested, close tested side and potentially reposition

**Risk Parameters:**
```
IRON_CONDOR_LIMITS:
  max_risk_per_trade: 3% of portfolio (max loss per condor)
  min_iv_rank: 30
  short_strike_delta: 0.16 each side
  wing_width: 1-3 strikes
  min_credit_to_width_ratio: 0.33
  min_days_to_expiry: 25 DTE
  profit_target_pct: 50% of credit
  stop_loss_multiple: 2x credit
  time_exit_dte: 21
  RISK_LEVEL: MODERATE
```

---

#### B4. Iron Butterfly

**Description:** Like an iron condor but with short strikes at the same point (ATM). Higher credit, narrower profit range.

**Construction:**
- Buy 1 OTM Put at strike $K_1$, pay $P_1$
- Sell 1 ATM Put at strike $K_2$ (= ATM), receive $P_2$
- Sell 1 ATM Call at strike $K_2$ (= ATM), receive $C_2$
- Buy 1 OTM Call at strike $K_3$, pay $C_3$
- Net Credit = $(P_2 + C_2) - (P_1 + C_3)$

**Formulas:**
- **Max Profit:** Net Credit (at $S_T = K_2$ exactly)
- **Max Loss:** Wing width - Net Credit
- **Break-even (upper):** $K_2 + \text{Net Credit}$
- **Break-even (lower):** $K_2 - \text{Net Credit}$

**Optimal Market Conditions:**
- Very neutral, pinning expected
- Very high IV (IV Rank > 70)
- Expecting minimal movement

**Entry/Exit Rules:** Similar to Iron Condor but:
- Higher credit = more cushion
- Narrower profit zone = needs more precision
- Better suited for short-duration trades (21-30 DTE)

---

#### B5. Covered Call

**Description:** Own the underlying, sell a call against it. Income generation on existing long position.

**Construction:**
- Long 1 unit of underlying (spot or perpetual with no funding cost)
- Sell 1 Call at strike $K$ ($K > S_0$), receive premium $C$

**Payoff Diagram:**
```
P&L
  │       ┌────────────
  │      ╱
  │     ╱
  │    ╱
──┼───╱───●────────── Price
  │  ╱    K
  │ ╱
  │╱
```

**Formulas:**
- **Max Profit:** $(K - S_0) + C$ (capped at strike)
- **Max Loss:** $S_0 - C$ (underlying goes to zero, offset by premium)
- **Break-even:** $S_{BE} = S_0 - C$

**Optimal Market Conditions:**
- Mildly bullish to neutral on the underlying
- High IV (collect more premium)
- Willing to sell underlying at strike price
- Income generation objective

**Greeks Profile:**
| Greek | Sign | Magnitude | Implication |
|---|---|---|---|
| Delta | + | 1 - Δ_call (< 1) | Reduced upside participation |
| Gamma | - | Negative (from short call) | Capped upside |
| Theta | + | Positive (from short call) | Time decay income |
| Vega | - | Negative | IV decrease benefits |

**Entry Rules:**
1. Already hold (or willing to acquire) the underlying
2. Select strike: 0.30 delta OTM call (70% probability of not being called away)
3. Alternative: sell at technical resistance level
4. Expiration: 21-45 DTE (optimal theta curve)
5. Higher strike = less premium, more upside; Lower strike = more premium, less upside

**Exit Rules:**
1. Let expire if OTM (keep premium, keep underlying)
2. If ITM near expiry: either let shares be called away, or roll to next expiry
3. Buy back at 50% profit and resell a new call
4. If underlying drops significantly, buy back call (cheap) and wait, or sell lower strike

**Crypto Covered Call Implementation:**
- Hold BTC/ETH in spot
- Sell calls on Deribit
- Must transfer underlying to Deribit as collateral
- Alternative: Use DOV protocols (Ribbon, Friktion) for automated covered call vaults
- DeFi DOVs typically sell weekly ATM or slightly OTM calls

**Risk Parameters:**
```
COVERED_CALL_LIMITS:
  max_position_size: per standard position sizing
  strike_delta: 0.20-0.35 (OTM)
  min_annualized_yield: 15% (crypto), 5% (forex)
  min_days_to_expiry: 14 DTE
  max_days_to_expiry: 45 DTE
  roll_threshold: 75% of credit captured
  RISK_LEVEL: LOW-MODERATE (underlying still has downside)
```

---

#### B6. Cash-Secured Put

**Description:** Sell a put while holding cash to purchase the underlying if assigned. Income or strategic entry.

**Construction:**
- Sell 1 Put at strike $K$ ($K \leq S_0$), receive premium $P$
- Hold $K$ in cash/stablecoin as collateral

**Payoff Diagram:**
```
P&L
 P ───────────────┐
                   ╲
                    ╲
──────────●──────────── Price
          K
```

**Formulas:**
- **Max Profit:** $P$ (premium received)
- **Max Loss:** $K - P$ (underlying goes to zero)
- **Break-even:** $S_{BE} = K - P$
- **Return on Capital:** $P / K$ per cycle

**Optimal Market Conditions:**
- Neutral to mildly bullish
- High IV (sell expensive puts)
- Willing to own the underlying at strike price
- Yield-seeking (income strategy)

**Entry Rules:**
1. Identify asset you want to own at a discount
2. Sell put at desired purchase price (support level)
3. Delta: -0.20 to -0.35 (70-80% probability of expiring OTM)
4. Expiration: 21-45 DTE
5. IV Rank > 30

**Exit Rules:**
1. Let expire OTM (keep premium, repeat)
2. Buy back at 50% profit and resell
3. If assigned: now own the underlying at effective cost = $K - P$ (begin covered call)
4. "Wheel Strategy": CSP → Assignment → Covered Call → Called Away → CSP repeat

**Risk Parameters:**
```
CASH_SECURED_PUT_LIMITS:
  max_capital_per_trade: 15% of portfolio
  strike_delta: -0.20 to -0.35
  min_annualized_return: 15% (crypto), 5% (forex)
  min_days_to_expiry: 14 DTE
  max_days_to_expiry: 45 DTE
  min_iv_rank: 30
  RISK_LEVEL: MODERATE (downside like owning underlying)
```

---

### Category C: Volatility Strategies

---

#### C1. Long Straddle

**Description:** Buy both a call and put at the same strike (ATM). Profit from large moves in either direction.

**Construction:**
- Buy 1 ATM Call at strike $K$, pay $C$
- Buy 1 ATM Put at strike $K$, pay $P$
- Total Debit = $C + P$

**Payoff Diagram:**
```
P&L
  │  ╲           ╱
  │   ╲         ╱
  │    ╲       ╱
  │     ╲     ╱
──┼──────╲   ╱──── Price
  │       ╲ ╱
-(C+P)─────●───────
           K
```

**Formulas:**
- **Max Profit:** Unlimited (both directions)
- **Max Loss:** $C + P$ (at expiration, $S_T = K$)
- **Break-even (upper):** $K + C + P$
- **Break-even (lower):** $K - (C + P)$
- **Required Move to Breakeven:** $\pm(C + P) / S_0$ as percentage

**Optimal Market Conditions:**
- Expecting large move but uncertain about direction
- Low IV (IV Rank < 20-30) — buying cheap volatility
- Before major events (earnings, regulatory decisions, halvings)
- Expecting realized vol >> implied vol

**Greeks Profile:**
| Greek | Sign | Magnitude | Implication |
|---|---|---|---|
| Delta | ≈ 0 | Near zero at entry | Direction neutral |
| Gamma | + | Large positive | Benefits from large moves |
| Theta | - | Large negative | Significant daily time decay |
| Vega | + | Large positive | Benefits from IV expansion |

**Entry Rules:**
1. IV Rank < 30 (cheap vol)
2. Expected binary event or breakout setup
3. Strike: ATM
4. Expiration: At least 7-14 days after expected event
5. Must expect move > premium paid (both sides)
6. Maximum acceptable daily theta: portfolio-level constraint

**Exit Rules:**
1. Profit target: 25-50% return on debit (realized vol is exceeding IV)
2. Stop loss: 25-35% of debit
3. If move occurs: close the winning side, hold the losing side if more movement expected
4. Time exit: Close before last 14 DTE (theta acceleration kills)
5. Post-event: Close immediately after event if vol was the catalyst

---

#### C2. Long Strangle

**Description:** Buy an OTM call and OTM put. Cheaper than straddle but requires larger move.

**Construction:**
- Buy 1 OTM Put at strike $K_1$ ($K_1 < S_0$), pay $P$
- Buy 1 OTM Call at strike $K_2$ ($K_2 > S_0$), pay $C$
- Total Debit = $C + P$

**Formulas:**
- **Max Profit:** Unlimited
- **Max Loss:** $C + P$
- **Break-even (upper):** $K_2 + C + P$
- **Break-even (lower):** $K_1 - (C + P)$

**Optimal Market Conditions:**
- Same as straddle but:
  - More extreme move expected
  - Tighter budget (lower premium)
  - Wider breakeven range (lower probability of profit)

**Entry Rules:**
1. IV Rank < 25
2. Strikes: 0.25-0.30 delta each side
3. Cost should be < 5% of underlying price
4. Expiration: 30-60 DTE

---

#### C3. Calendar Spread (Time Spread)

**Description:** Sell a near-term option, buy a longer-term option at the same strike. Profit from time decay differential and IV changes.

**Construction (Call Calendar):**
- Sell 1 Call at strike $K$, near-term expiry $T_1$, receive $C_1$
- Buy 1 Call at strike $K$, far-term expiry $T_2$ ($T_2 > T_1$), pay $C_2$
- Net Debit = $C_2 - C_1$

**Formulas:**
- **Max Profit:** Occurs when $S_{T_1} = K$ at near-term expiry (short option expires worthless, long option retains value)
- **Max Loss:** Net debit paid (if underlying moves significantly)
- **Break-even:** Complex; depends on remaining time value of long option at near-term expiry

**Optimal Market Conditions:**
- Stable price near strike price
- Low near-term IV, higher far-term IV (or expected IV increase)
- Range-bound in the near term

**Greeks Profile:**
| Greek | Sign | Magnitude | Implication |
|---|---|---|---|
| Delta | ≈ 0 | Near zero if ATM | Neutral |
| Gamma | - | Slightly negative (net) | Stable price preferred |
| Theta | + | Positive (short decays faster) | Near-term decay benefits |
| Vega | + | Positive (long has more vega) | IV increase benefits |

**Entry Rules:**
1. Select ATM strike for maximum theta capture
2. Near-term expiry: 21-30 DTE
3. Far-term expiry: 45-60 DTE
4. Price should be stable near the strike
5. IV term structure analysis: check for kinks or anomalies

**Exit Rules:**
1. Close entire position at near-term expiry (roll or close both legs)
2. Profit target: 25-40% of debit
3. Close if underlying moves > 1 standard deviation from strike

---

### Category D: Hedging Strategies

---

#### D1. Protective Put

**Description:** Buy a put to protect an existing long position. Insurance against downside.

**Construction:**
- Long 1 unit of underlying (existing position)
- Buy 1 Put at strike $K$ ($K \leq S_0$), pay $P$

**Payoff Diagram:**
```
P&L
  │         ╱
  │        ╱
  │       ╱
  │      ╱
──┼─────●╱────────── Price
  │     K
  │
 -(S0-K)-P ─────────
```

**Formulas:**
- **Max Profit:** Unlimited (upside of underlying minus premium)
- **Max Loss:** $(S_0 - K) + P$ (underlying drops to/below strike)
- **Break-even:** $S_{BE} = S_0 + P$
- **Downside Protected Below:** $K$
- **Cost of Insurance:** $P / S_0$ as percentage

**Optimal Market Conditions:**
- Want to hold long-term position but worried about near-term downside
- Before major events or uncertainty
- Willing to pay for insurance
- Portfolio protection required by risk mandate

**Entry Rules:**
1. Already hold the underlying (long position to protect)
2. Select strike based on acceptable loss level:
   - ATM ($K = S_0$): Maximum protection, most expensive
   - 5-10% OTM: Cheaper, accepts some drawdown
   - 20% OTM: Tail risk hedge only, cheapest
3. Expiration: Match to risk window (event-based or quarterly)
4. Consider cost: 2-5% of position value per quarter is typical for ATM puts in crypto

**Exit Rules:**
1. If underlying drops: Exercise/close put to lock in protection
2. If underlying rises: Let put expire, or sell before expiry to recoup some premium
3. Roll forward before expiry to maintain continuous protection

---

#### D2. Collar

**Description:** Long underlying + protective put + covered call. Net zero or low-cost downside protection.

**Construction:**
- Long 1 unit of underlying
- Buy 1 OTM Put at strike $K_1$ ($K_1 < S_0$), pay $P$
- Sell 1 OTM Call at strike $K_2$ ($K_2 > S_0$), receive $C$
- Net Cost = $P - C$ (can be zero-cost if $P = C$)

**Payoff Diagram:**
```
P&L
  │      ┌──────────
  │     ╱
  │    ╱
  │   ╱
──┼──●───●────── Price
  │  K1  K2
  │
 ──┘ ─────────────
```

**Formulas:**
- **Max Profit:** $(K_2 - S_0) - (P - C)$
- **Max Loss:** $(S_0 - K_1) + (P - C)$
- **Break-even:** $S_0 + (P - C)$ (for zero-cost collar, break-even = $S_0$)
- **Protected Range:** $K_1$ to $K_2$

**Optimal Market Conditions:**
- Want downside protection but unwilling to pay full put premium
- Willing to cap upside
- Long-term hold with protection overlay
- Risk management mandate requires defined downside

**Zero-Cost Collar Construction:**
- Find put strike $K_1$ where put premium $P$
- Find call strike $K_2$ where call premium $C = P$
- Net cost = $0$

**Entry Rules:**
1. Long position exists that needs protection
2. Put strike: -0.20 to -0.30 delta (10-20% OTM typical for crypto)
3. Call strike: Select to offset put cost (may be ATM or OTM depending on skew)
4. Check skew: In crypto, puts are typically more expensive than equidistant calls (put skew), so zero-cost collar may require closer call strike
5. Expiration: Monthly or quarterly, matched to risk horizon

---

## 1.5 Implied Volatility Analysis

### 1.5.1 IV Rank

$$IV_{Rank} = \frac{IV_{current} - IV_{52w,low}}{IV_{52w,high} - IV_{52w,low}} \times 100$$

- Measures where current IV sits relative to its 52-week range
- IV Rank > 50: IV is elevated relative to history → favor selling strategies
- IV Rank < 30: IV is low relative to history → favor buying strategies

### 1.5.2 IV Percentile

$$IV_{Percentile} = \frac{\text{Number of days IV was below current IV}}{\text{Total trading days in lookback}} \times 100$$

- Measures what percentage of days had lower IV
- More robust than IV Rank (not affected by single outlier days)
- Generally preferred for strategy selection

### 1.5.3 Strategy Selection by IV Environment

| IV Rank | IV Percentile | Preferred Strategies |
|---|---|---|
| 0-20 | 0-20 | Long Straddle, Long Strangle, Calendar Buy |
| 20-40 | 20-40 | Bull/Bear Spreads, Long Options |
| 40-60 | 40-60 | Iron Condor, Calendar Spread |
| 60-80 | 60-80 | Short Strangle, Iron Butterfly, Covered Call |
| 80-100 | 80-100 | Short Straddle, Short Strangle, CSP, DOV |

### 1.5.4 Volatility Smile and Skew

**Volatility Smile:** IV varies across strike prices for a given expiry. In crypto:

- **Put Skew**: OTM puts have higher IV than OTM calls (demand for crash protection)
- **Skew Metric**: 25Δ Put IV - 25Δ Call IV (typically positive in crypto = put skew)
- **Butterfly**: 25Δ average IV - ATM IV (measures smile curvature)

**Risk Reversal (25Δ):**

$$RR_{25\Delta} = IV_{25\Delta Call} - IV_{25\Delta Put}$$

- Negative RR = Put skew (bearish sentiment, crash protection demand)
- Positive RR = Call skew (bullish sentiment, upside demand)

**Trading Skew:**
- When skew is extreme (> 2 standard deviations from mean): Mean-reversion trade
- Sell expensive side, buy cheap side (risk reversal trade)
- Use to enhance directional bets (sell expensive OTM puts to fund OTM calls in bullish setup)

---

## 2. Technical Specifications

### 2.1 Options Data Pipeline

```
OPTIONS_DATA_PIPELINE:

  INPUT_DATA:
    - Spot price (real-time, multiple sources)
    - Option chain: all strikes × all expiries
    - Bid/ask for each option
    - Open interest per strike/expiry
    - Volume per strike/expiry
    - Exchange-reported Greeks (Deribit provides mark IV)
    - Historical options data (for backtesting)
    - Events calendar

  PROCESSING:
    1. Data normalization:
       - Convert prices to common denomination (USD or BTC)
       - Synchronize timestamps across exchanges
       - Handle missing data (interpolation)

    2. IV Surface Construction:
       - Extract IV from market prices (Newton-Raphson)
       - Fit smooth surface: SABR or SVI parameterization
       - Detect arbitrage violations (butterfly, calendar spread)
       - Store IV surface as grid: [strike_moneyness × time_to_expiry]

    3. Greeks Calculation:
       - Compute all Greeks from IV surface + BSM
       - Aggregate to position level
       - Aggregate to portfolio level
       - Store time series for attribution

    4. Signal Generation:
       - IV Rank/Percentile computation
       - Skew analysis
       - Term structure analysis
       - Unusual activity detection (volume/OI spikes)
       - Greeks-based opportunity identification

  OUTPUT:
    - Real-time IV surface
    - Position and portfolio Greeks
    - Strategy signals with confidence scores
    - Risk alerts
```

### 2.2 Options Strategy Execution Engine

```
OPTIONS_EXECUTION_ENGINE:

  ORDER_TYPES:
    single_leg:
      - limit_order: Standard limit
      - market_order: Immediate fill (avoid for options — wide spreads)
      - stop_order: Trigger-based
      - trailing_stop: Dynamic stop

    multi_leg:
      - spread_order: Submit as package (exchange-native if available)
      - leg_by_leg: Execute one leg at a time (legging risk)
      - ratio_order: Unequal leg quantities

  EXECUTION_LOGIC:
    1. Receive strategy signal
    2. Validate against risk limits
    3. Check liquidity:
       - Bid-ask spread < threshold (varies by instrument)
       - Order book depth sufficient for position size
       - Impact cost estimation
    4. Construct order:
       - Multi-leg: Use exchange combo orders when available
       - Single-leg: Use limit orders with smart pricing
    5. Submit order:
       - Start at mid-price
       - Walk toward aggressive side over time
       - Maximum time-to-fill: 60 seconds
       - Cancel and reassess if not filled
    6. Confirmation:
       - All legs filled
       - Actual vs expected fill prices
       - Slippage recording
    7. Position booking:
       - Update position database
       - Recalculate portfolio Greeks
       - Set profit target and stop loss orders
```

### 2.3 Exchange-Specific Configurations

```
DERIBIT_OPTIONS_CONFIG:
  api_endpoint: https://www.deribit.com/api/v2
  ws_endpoint: wss://www.deribit.com/ws/api/v2
  settlement_time: "08:00 UTC"
  settlement_method: "30-min TWAP"
  tick_sizes:
    BTC: 0.0005 BTC
    ETH: 0.005 ETH (scaled to BTC equivalent)
  contract_size:
    BTC: 1 BTC
    ETH: 1 ETH
  margin_mode: portfolio_margin
  fee_schedule:
    maker: 0.03% of underlying
    taker: 0.03% of underlying
    delivery: 0.015%
  max_open_orders: 100
  rate_limits:
    matching_engine: 5 req/100ms
    non_matching: 20 req/s

OKX_OPTIONS_CONFIG:
  api_endpoint: https://www.okx.com/api/v5
  settlement_time: "08:00 UTC"
  contract_size:
    BTC: 0.01 BTC
    ETH: 0.1 ETH
  margin_mode: [isolated, cross, portfolio]
  fee_schedule:
    maker: 0.02%
    taker: 0.03%
```

---

## 3. Mathematical Models

### 3.1 Black-Scholes-Merton — Complete Derivation

Starting from geometric Brownian motion:

$$dS = \mu S \, dt + \sigma S \, dW$$

Applying Ito's Lemma to a derivative $V(S,t)$:

$$dV = \left(\frac{\partial V}{\partial t} + \mu S \frac{\partial V}{\partial S} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 V}{\partial S^2}\right)dt + \sigma S \frac{\partial V}{\partial S} dW$$

Construct a riskless portfolio $\Pi = V - \Delta S$ where $\Delta = \frac{\partial V}{\partial S}$:

$$d\Pi = \left(\frac{\partial V}{\partial t} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 V}{\partial S^2}\right)dt$$

By no-arbitrage, $d\Pi = r\Pi \, dt$:

$$\frac{\partial V}{\partial t} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 V}{\partial S^2} + rS\frac{\partial V}{\partial S} - rV = 0$$

This is the **Black-Scholes PDE**. With boundary conditions for a European call:
- $V(S,T) = \max(S-K, 0)$ at expiry
- $V(0,t) = 0$ as $S \to 0$
- $V(S,t) \to S$ as $S \to \infty$

The solution gives the BSM pricing formulas stated in Section 1.2.

### 3.2 Greeks — Complete Mathematical Formulation

**Standard Normal PDF:**

$$n(x) = N'(x) = \frac{1}{\sqrt{2\pi}}e^{-x^2/2}$$

**Delta:**

$$\Delta_C = N(d_1), \quad \Delta_P = N(d_1) - 1$$

**Gamma (same for calls and puts):**

$$\Gamma = \frac{n(d_1)}{S\sigma\sqrt{T}}$$

**Theta:**

$$\Theta_C = -\frac{S \cdot n(d_1) \cdot \sigma}{2\sqrt{T}} - rKe^{-rT}N(d_2)$$

$$\Theta_P = -\frac{S \cdot n(d_1) \cdot \sigma}{2\sqrt{T}} + rKe^{-rT}N(-d_2)$$

**Vega (same for calls and puts):**

$$\nu = S\sqrt{T} \cdot n(d_1)$$

Note: Vega is expressed per 1 unit (100%) change in IV. For per 1% change, divide by 100.

**Rho:**

$$\rho_C = KTe^{-rT}N(d_2)$$

$$\rho_P = -KTe^{-rT}N(-d_2)$$

**Vanna:**

$$\text{Vanna} = -\frac{n(d_1) \cdot d_2}{\sigma}$$

**Charm (Delta Bleed):**

$$\text{Charm}_C = -n(d_1)\left(\frac{2rT - d_2\sigma\sqrt{T}}{2T\sigma\sqrt{T}}\right)$$

**Vomma/Volga:**

$$\text{Vomma} = \nu \cdot \frac{d_1 \cdot d_2}{\sigma}$$

**Speed:**

$$\text{Speed} = -\frac{\Gamma}{S}\left(1 + \frac{d_1}{\sigma\sqrt{T}}\right)$$

**Color:**

$$\text{Color} = -\frac{n(d_1)}{2ST\sigma\sqrt{T}}\left(1 + \frac{2rT - d_2\sigma\sqrt{T}}{\sigma\sqrt{T}} \cdot d_1\right)$$

### 3.3 Implied Volatility Calculation

**Newton-Raphson Method:**

To find $\sigma_{imp}$ such that $BSM(\sigma_{imp}) = C_{market}$:

$$\sigma_{n+1} = \sigma_n - \frac{BSM(\sigma_n) - C_{market}}{\text{Vega}(\sigma_n)}$$

**Convergence criteria:** $|BSM(\sigma_n) - C_{market}| < 10^{-8}$

**Initial guess:** Brenner-Subrahmanyam approximation:

$$\sigma_0 \approx \sqrt{\frac{2\pi}{T}} \cdot \frac{C_{market}}{S}$$

**Jaeckel (2017) Rational Approximation:** "Let's Be Rational" — provides implied volatility with machine-precision accuracy in 2-3 iterations. Preferred for production systems.

### 3.4 Stochastic Volatility — Heston Model

$$dS_t = \mu S_t \, dt + \sqrt{v_t} S_t \, dW_t^S$$

$$dv_t = \kappa(\theta - v_t) \, dt + \xi \sqrt{v_t} \, dW_t^v$$

$$\text{Corr}(dW_t^S, dW_t^v) = \rho$$

Where:
- $v_t$ = Instantaneous variance
- $\kappa$ = Mean reversion speed
- $\theta$ = Long-term variance
- $\xi$ = Vol of vol
- $\rho$ = Correlation between spot and vol (typically negative: "leverage effect")

**Feller Condition (ensures $v_t > 0$):**

$$2\kappa\theta > \xi^2$$

The Heston model produces a volatility smile/skew naturally and is widely used for options pricing when BSM is insufficient.

### 3.5 Multi-Leg Strategy P&L Models

**Iron Condor P&L at Expiration:**

$$\text{P\&L}_{IC} = \text{Credit} - \max(0, S_T - K_3) + \max(0, S_T - K_4) - \max(0, K_2 - S_T) + \max(0, K_1 - S_T)$$

**Straddle P&L at Expiration:**

$$\text{P\&L}_{straddle} = \max(S_T - K, 0) + \max(K - S_T, 0) - (C + P)$$

$$= |S_T - K| - (C + P)$$

**Calendar Spread P&L (at near-term expiry):**

$$\text{P\&L}_{calendar} = V_{long}(S_{T_1}, T_2 - T_1, \sigma_{imp,T_2}) - \max(S_{T_1} - K, 0) - \text{Debit}$$

---

## 4. Risk Parameters

### 4.1 Strategy-Level Risk Matrix

```
STRATEGY_RISK_MATRIX:

  LONG_CALL:
    max_loss: Premium paid (100%)
    max_profit: Unlimited
    margin_required: Premium only
    complexity: Low
    active_management: Low
    event_risk: Theta drag
    best_iv_environment: Low IV
    risk_score: 3/10

  LONG_PUT:
    max_loss: Premium paid (100%)
    max_profit: K - Premium
    margin_required: Premium only
    complexity: Low
    active_management: Low
    event_risk: Theta drag
    best_iv_environment: Low IV
    risk_score: 3/10

  BULL_CALL_SPREAD:
    max_loss: Net debit
    max_profit: Width - Debit
    margin_required: Net debit
    complexity: Low
    active_management: Low
    event_risk: Moderate (both legs)
    best_iv_environment: Any
    risk_score: 3/10

  BEAR_PUT_SPREAD:
    max_loss: Net debit
    max_profit: Width - Debit
    margin_required: Net debit
    complexity: Low
    active_management: Low
    risk_score: 3/10

  SHORT_STRADDLE:
    max_loss: UNLIMITED
    max_profit: Total premium
    margin_required: HIGH (naked)
    complexity: High
    active_management: High (continuous)
    event_risk: EXTREME
    best_iv_environment: High IV
    risk_score: 9/10

  SHORT_STRANGLE:
    max_loss: UNLIMITED
    max_profit: Total premium
    margin_required: HIGH (naked)
    complexity: High
    active_management: High
    risk_score: 8/10

  IRON_CONDOR:
    max_loss: Width - Credit
    max_profit: Net credit
    margin_required: Width of wider spread
    complexity: Moderate
    active_management: Moderate
    risk_score: 5/10

  IRON_BUTTERFLY:
    max_loss: Width - Credit
    max_profit: Net credit
    margin_required: Width of spread
    complexity: Moderate
    active_management: Moderate
    risk_score: 5/10

  COVERED_CALL:
    max_loss: S0 - Premium (underlying risk)
    max_profit: (K - S0) + Premium
    margin_required: Underlying purchase
    complexity: Low
    active_management: Low
    risk_score: 4/10

  CASH_SECURED_PUT:
    max_loss: K - Premium
    max_profit: Premium
    margin_required: Strike price in cash
    complexity: Low
    active_management: Low
    risk_score: 4/10

  LONG_STRADDLE:
    max_loss: Total premium
    max_profit: Unlimited
    margin_required: Premium only
    complexity: Low
    active_management: Moderate
    risk_score: 4/10

  PROTECTIVE_PUT:
    max_loss: (S0 - K) + Premium
    max_profit: Unlimited (minus premium)
    margin_required: Premium only
    complexity: Low
    active_management: Low
    risk_score: 2/10

  COLLAR:
    max_loss: (S0 - K1) + Net cost
    max_profit: (K2 - S0) - Net cost
    margin_required: Minimal (covered)
    complexity: Low
    active_management: Low
    risk_score: 2/10
```

### 4.2 Portfolio-Level Options Risk Limits

```
PORTFOLIO_OPTIONS_RISK:

  aggregate_limits:
    max_total_premium_at_risk: 10% of portfolio
    max_short_gamma_dollars: 2% of portfolio per 1% move
    max_portfolio_vega: 1% of portfolio per vol point
    max_portfolio_theta: -0.3% daily (long options)
    max_portfolio_theta: +0.5% daily (short options)
    max_single_underlying_delta: 15% of portfolio
    max_total_delta: 30% of portfolio

  concentration_limits:
    max_single_expiry_exposure: 30% of options portfolio
    max_single_strike_exposure: 20% of options portfolio
    max_notional_per_underlying: 20% of portfolio

  liquidity_limits:
    max_position_vs_OI: 2% of open interest at any strike
    min_bid_ask_spread: < 5% of mid price
    min_daily_volume: 10x position size

  event_risk:
    pre_event_reduction: 50% of normal sizing
    expiry_week_gamma: Reduce short gamma 50%
    settlement_buffer: Close positions 2 hours before settlement
```

### 4.3 Scenario-Based Risk Assessment

```
OPTIONS_SCENARIOS:

  scenario_1_spot_down_10pct:
    description: "Underlying drops 10% in 1 day"
    iv_change: +15 vol points
    portfolio_impact:
      long_call: -40% to -80% of premium
      long_put: +100% to +300% of premium
      iron_condor: put side tested, -50% to -200% of credit
      covered_call: -8% to -10% of position (partially offset)
      protective_put: put gains offset underlying loss

  scenario_2_spot_up_10pct:
    description: "Underlying rallies 10% in 1 day"
    iv_change: -5 vol points
    portfolio_impact:
      long_call: +100% to +300% of premium
      short_straddle: call side in trouble, significant loss
      covered_call: max profit potentially reached early

  scenario_3_iv_crush_20_points:
    description: "IV drops 20 points (post-event)"
    spot_change: minimal
    portfolio_impact:
      long_straddle: -30% to -60% of premium (devastating)
      short_strangle: +20% to +40% of credit (beneficial)
      iron_condor: +10% to +20% of credit

  scenario_4_iv_spike_30_points:
    description: "IV spikes 30 points (crisis)"
    spot_change: -5% to -15%
    portfolio_impact:
      long_straddle: +50% to +200% of premium
      short_straddle: EXTREME loss (both vega and directional)
      protective_put: large gain on put
```

---

## 5. Execution Flow

### 5.1 Complete Options Trading Bot — Execution Algorithm

```
OPTIONS_TRADING_BOT_FLOW:

  ╔══════════════════════════════════════════════════════════╗
  ║  STEP 1: DATA COLLECTION (every 1 second)               ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  1.1 Fetch spot price from 3+ sources                   ║
  ║  1.2 Fetch full option chain (all strikes × expiries)   ║
  ║  1.3 Compute IV for each option (Newton-Raphson)        ║
  ║  1.4 Build IV surface (SABR/SVI parameterization)       ║
  ║  1.5 Compute IV Rank and IV Percentile                  ║
  ║  1.6 Compute term structure slope                       ║
  ║  1.7 Compute skew (25Δ risk reversal, butterfly)        ║
  ║  1.8 Fetch open interest and volume data                ║
  ║  1.9 Check events calendar                              ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 2: SIGNAL GENERATION (every 5 seconds)            ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  2.1 Determine market regime:                            ║
  ║      - Trending / Range-bound / High-vol / Low-vol      ║
  ║  2.2 IV environment assessment:                          ║
  ║      - IV Rank/Percentile → sell vs buy premium          ║
  ║  2.3 Skew assessment:                                    ║
  ║      - Extreme skew → mean reversion trades             ║
  ║  2.4 Term structure assessment:                          ║
  ║      - Inverted → calendar spread opportunities         ║
  ║  2.5 Unusual activity scan:                              ║
  ║      - Volume spikes, large block trades                ║
  ║  2.6 Generate candidate strategies with scores           ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 3: STRATEGY SELECTION (on signal)                  ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  3.1 Rank candidates by expected Sharpe ratio            ║
  ║  3.2 Filter by risk constraints:                         ║
  ║      - Portfolio Greeks limits                           ║
  ║      - Concentration limits                              ║
  ║      - Margin availability                               ║
  ║  3.3 Select top strategy                                 ║
  ║  3.4 Determine optimal strikes and expiry:               ║
  ║      - Strike selection by delta target                  ║
  ║      - Expiry selection by DTE target                    ║
  ║  3.5 Position sizing (Kelly / Fixed Fractional)          ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 4: PRE-TRADE RISK CHECK                           ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  4.1 Calculate new portfolio Greeks after trade          ║
  ║  4.2 Verify all limits satisfied:                        ║
  ║      □ Max premium at risk                               ║
  ║      □ Max portfolio delta                               ║
  ║      □ Max portfolio gamma                               ║
  ║      □ Max portfolio vega                                ║
  ║      □ Max portfolio theta                               ║
  ║      □ Max single-name concentration                     ║
  ║      □ Margin requirement satisfied                      ║
  ║  4.3 Stress test: What if spot moves ±10%?              ║
  ║  4.4 Approve or reject                                   ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 5: ORDER EXECUTION                                 ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  5.1 Check liquidity at target strikes:                  ║
  ║      - Bid-ask spread acceptable?                        ║
  ║      - Depth sufficient?                                 ║
  ║  5.2 Construct order(s):                                 ║
  ║      - Multi-leg: use combo/RFQ if available             ║
  ║      - Single-leg: sequence from most to least liquid    ║
  ║  5.3 Submit limit order at mid-price                     ║
  ║  5.4 If not filled in 15s: walk price 25% toward aggress ║
  ║  5.5 If not filled in 30s: walk price 50% toward aggress ║
  ║  5.6 If not filled in 60s: cancel, reassess              ║
  ║  5.7 Confirm all legs filled                             ║
  ║  5.8 Log execution details                               ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 6: POSITION MONITORING (continuous)                ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  6.1 Real-time P&L tracking                              ║
  ║  6.2 Greeks monitoring (every 100ms):                    ║
  ║      - Delta drift → hedge if exceeds threshold          ║
  ║      - Gamma exposure → reduce if near expiry           ║
  ║      - Theta collection tracking                         ║
  ║      - Vega exposure vs IV changes                       ║
  ║  6.3 Profit target monitoring:                           ║
  ║      - Credit strategies: close at 50% of max profit    ║
  ║      - Debit strategies: close at 50-100% return        ║
  ║  6.4 Stop loss monitoring:                               ║
  ║      - Credit strategies: close at 200% of credit       ║
  ║      - Debit strategies: close at 50% loss              ║
  ║  6.5 Time-based exit:                                    ║
  ║      - Close credit spreads at 21 DTE                   ║
  ║      - Close debit positions at 14 DTE                  ║
  ║  6.6 Adjustment triggers:                                ║
  ║      - Roll tested side if underlying breaches strike   ║
  ║      - Add hedge leg if delta exceeds limit             ║
  ║      - Convert to different structure if thesis changes  ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 7: EXIT EXECUTION                                  ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  7.1 Trigger identified (profit/loss/time/adjustment)    ║
  ║  7.2 Construct closing order(s)                          ║
  ║  7.3 Execute with same smart routing as entry            ║
  ║  7.4 Verify all legs closed                              ║
  ║  7.5 Update position database                            ║
  ║  7.6 Recalculate portfolio Greeks                        ║
  ║  7.7 Record trade result for performance attribution     ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 8: POST-TRADE ANALYSIS                             ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  8.1 Compare actual vs expected P&L                      ║
  ║  8.2 Decompose P&L by Greek:                             ║
  ║      - Delta P&L: Δ × ΔS                                ║
  ║      - Gamma P&L: ½ × Γ × (ΔS)²                        ║
  ║      - Theta P&L: Θ × Δt                                ║
  ║      - Vega P&L: ν × Δσ                                 ║
  ║      - Residual (higher-order terms + transaction costs) ║
  ║  8.3 Execution quality analysis:                         ║
  ║      - Fill vs mid price at time of order                ║
  ║      - Slippage per leg                                  ║
  ║      - Speed of execution                                ║
  ║  8.4 Update strategy statistics:                         ║
  ║      - Win rate, average profit, average loss            ║
  ║      - Sharpe ratio by strategy type                     ║
  ║      - Performance by IV environment                     ║
  ║  8.5 Feed results to ML optimizer for parameter tuning   ║
  ║                                                          ║
  ╚══════════════════════════════════════════════════════════╝
```

### 5.2 Delta Hedging Execution Flow

```
DELTA_HEDGING_FLOW:

  PARAMETERS:
    hedge_instrument: perpetual_swap  # most liquid for crypto
    rebalance_trigger: delta_threshold OR time_based
    delta_threshold: 0.05 (5% of notional)
    time_interval: 15 minutes (if time-based)
    max_hedge_slippage: 0.1%
    funding_rate_awareness: true

  ALGORITHM:
    WHILE position_is_open:

      1. Calculate current portfolio delta:
         portfolio_delta = Σ(option_delta_i × qty_i × contract_size_i)
         + Σ(perp_position_j) + Σ(spot_position_k)

      2. Calculate target delta:
         target_delta = 0  # for delta-neutral

      3. Calculate hedge needed:
         hedge_qty = target_delta - portfolio_delta

      4. IF |hedge_qty| > delta_threshold:
         a. Check perp liquidity
         b. Submit market/limit order for hedge_qty
         c. IF hedge_qty > 0: BUY perp
            IF hedge_qty < 0: SELL perp
         d. Confirm fill
         e. Update portfolio delta

      5. Record hedge trade:
         - timestamp, qty, price, slippage, new_portfolio_delta

      6. Calculate hedge cost:
         - Transaction cost: qty × fee_rate
         - Funding cost: perp_position × funding_rate × time_held
         - Slippage cost: |fill_price - mid_price| × qty

      7. WAIT for next trigger (time or delta threshold)

  PERFORMANCE_TRACKING:
    - Total hedge trades
    - Average slippage
    - Total transaction costs
    - Total funding costs
    - Gamma P&L realized through hedging
    - Net hedge P&L vs theta collected
```

### 5.3 Rolling and Adjustment Procedures

```
ROLLING_PROCEDURES:

  WHEN_TO_ROLL:
    - Short option at 21 DTE (time exit trigger)
    - Short strike breached (tested)
    - IV environment has changed significantly
    - Theta-to-gamma ratio unfavorable

  HOW_TO_ROLL:
    roll_out:
      description: "Close current, open same strike at later expiry"
      when: Want more time for thesis to play out
      execution: Close near-term, open far-term simultaneously
      cost: Typically a debit (paying for more time)

    roll_up:
      description: "Close current call, open higher strike call"
      when: Underlying has moved up, want to stay OTM
      execution: Close lower strike, open higher strike
      credit_or_debit: Usually a credit (higher strike = cheaper)

    roll_down:
      description: "Close current put, open lower strike put"
      when: Underlying has moved down, want to stay OTM
      execution: Close higher strike put, open lower strike put
      credit_or_debit: Usually a credit

    roll_out_and_up:
      description: "Combine roll out + roll up"
      when: Short call tested, want more time and higher strike
      execution: Close near-term lower strike, open far-term higher strike
      goal: Collect additional credit for the roll

  ADJUSTMENT_DECISION_TREE:
    IF short_strike_tested:
      IF credit_available > 0.33 × original_credit:
        → Roll out and up/down for credit
      ELSE:
        → Close position, accept loss
    IF delta_exceeds_threshold:
      → Add opposing delta (buy/sell underlying)
    IF IV_environment_changed:
      IF IV_dropped AND short_vol_position:
        → Take profits early
      IF IV_spiked AND long_vol_position:
        → Take profits early
      IF IV_spiked AND short_vol_position:
        → Widen strikes, add protection, or close
```

---

## 6. References

### Academic Literature

1. **Black, F., & Scholes, M.** (1973). "The Pricing of Options and Corporate Liabilities." *Journal of Political Economy*, 81(3), 637-654.
2. **Merton, R.C.** (1973). "Theory of Rational Option Pricing." *Bell Journal of Economics and Management Science*, 4(1), 141-183.
3. **Cox, J.C., Ross, S.A., & Rubinstein, M.** (1979). "Option Pricing: A Simplified Approach." *Journal of Financial Economics*, 7(3), 229-263.
4. **Heston, S.L.** (1993). "A Closed-Form Solution for Options with Stochastic Volatility." *Review of Financial Studies*, 6(2), 327-343.
5. **Gatheral, J.** (2006). *The Volatility Surface: A Practitioner's Guide*. Wiley.
6. **Jaeckel, P.** (2017). "Let's Be Rational." *Wilmott Magazine*, January 2017.

### Textbooks

7. **Hull, J.C.** (2022). *Options, Futures, and Other Derivatives* (11th Edition). Pearson.
8. **Natenberg, S.** (2015). *Option Volatility and Pricing* (2nd Edition). McGraw-Hill.
9. **Taleb, N.N.** (1997). *Dynamic Hedging: Managing Vanilla and Exotic Options*. Wiley.
10. **Sinclair, E.** (2013). *Volatility Trading* (2nd Edition). Wiley.
11. **Euan Sinclair** (2020). *Positional Option Trading*. Wiley.
12. **McMillan, L.G.** (2012). *Options as a Strategic Investment* (5th Edition). Prentice Hall.
13. **Cohen, G.** (2005). *The Bible of Options Strategies*. FT Press.

### Crypto-Specific Resources

14. **Deribit Knowledge Base** — Options specifications, settlement, margin. https://www.deribit.com/kb
15. **Paradigm Protocol** — Institutional crypto options block trading.
16. **Amberdata Derivatives** — Crypto volatility surface data.
17. **Laevitas Analytics** — Real-time crypto options flow, Greeks, and OI.
18. **Genesis Volatility** — Crypto options analytics platform.
19. **Block Scholes** — Crypto derivatives research and analytics.

### Implementation References

20. **QuantLib** — Open-source quantitative finance library. https://www.quantlib.org
21. **Vollib** — Python library for option pricing and Greeks. https://github.com/vollib/vollib
22. **py_vollib** — Black-Scholes, Black-76, and implied volatility calculation.
23. **Deribit API v2** — REST and WebSocket API documentation.

---

> **Note to AI Agents:** This document provides the complete options strategy catalog for the trading system.
> All strategies must be filtered through the risk management framework (Document 05) before execution.
> IV Rank/Percentile is the primary filter for strategy selection.
> Position sizing must follow Kelly Criterion with fractional adjustment.
> Delta hedging is required for all short options positions exceeding defined thresholds.
> Multi-leg strategies should use exchange-native combo orders when available to minimize leg risk.
