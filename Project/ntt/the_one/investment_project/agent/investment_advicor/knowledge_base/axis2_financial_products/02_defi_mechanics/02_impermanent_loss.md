# Impermanent Loss Analysis — Complete Framework

> **Axis 2 — Financial Products | Module 02 — DeFi Mechanics | Document 02**
> Version: 2.0.0 | Last Updated: 2026-04-12
> Classification: KNOWLEDGE BASE — MULTI-AGENT AI TRADING SYSTEM

---

## Table of Contents

1. [Introduction to Impermanent Loss](#1-introduction-to-impermanent-loss)
2. [IL Derivation from First Principles](#2-il-derivation-from-first-principles)
3. [IL for Concentrated Liquidity](#3-il-for-concentrated-liquidity)
4. [IL vs Trading Fee Income](#4-il-vs-trading-fee-income)
5. [Break-Even Fee Calculation](#5-break-even-fee-calculation)
6. [Hedging IL with Options and Futures](#6-hedging-il-with-options-and-futures)
7. [Dynamic Range Adjustment to Minimize IL](#7-dynamic-range-adjustment-to-minimize-il)
8. [IL for Multi-Asset Pools](#8-il-for-multi-asset-pools)
9. [Complete Mathematical Models](#9-complete-mathematical-models)
10. [Strategy for Maximizing Yield Net of IL](#10-strategy-for-maximizing-yield-net-of-il)
11. [Algorithmic IL Monitoring and Rebalancing](#11-algorithmic-il-monitoring-and-rebalancing)
12. [Risk Parameters](#12-risk-parameters)
13. [Execution Flow — IL Management Bot](#13-execution-flow--il-management-bot)
14. [References](#14-references)

---

## 1. Introduction to Impermanent Loss

### 1.1 Definition

Impermanent Loss (IL) is the difference in value between:
- **Providing liquidity** in an AMM pool (holding LP tokens).
- **Simply holding** the same tokens in a wallet (HODL strategy).

It is called "impermanent" because if the price returns to the original ratio, the loss
disappears. However, if the LP exits at a different price ratio, the loss becomes
permanent ("realized").

### 1.2 Why IL Occurs

In a constant product AMM ($x \cdot y = k$), the pool maintains a fixed ratio between
assets. When external prices change:

1. Arbitrageurs trade against the pool to bring its price in line with the market.
2. This trading shifts the pool's composition — the pool accumulates the depreciating
   asset and loses the appreciating asset.
3. The LP's portfolio is now worth less than if they had simply held the original amounts.

### 1.3 IL Is the Cost of Market Making

IL can be understood as the cost the LP pays for the privilege of being a passive market
maker. In traditional market making, this cost manifests as adverse selection — market
makers lose money to informed traders. In AMMs, this manifests as IL.

### 1.4 Key Insight for the Trading System

$$
\text{LP Profitability} = \text{Fee Income} - \text{Impermanent Loss} - \text{Gas Costs}
$$

The trading system must ensure that fee income exceeds IL for any LP position to be
worthwhile. This requires accurate IL prediction, fee estimation, and proactive
risk management.

---

## 2. IL Derivation from First Principles

### 2.1 Setup

Consider a constant product AMM with:
- Initial reserves: $(x_0, y_0)$ with $x_0 \cdot y_0 = k$
- Initial price: $P_0 = y_0 / x_0$
- Token X price changes to $P_1 = r \cdot P_0$ where $r$ is the price ratio

### 2.2 Derivation

**Step 1**: After price change, arbitrageurs trade until the pool price equals $P_1$.

New reserves must satisfy:
- $x_1 \cdot y_1 = k$ (constant product)
- $y_1 / x_1 = P_1 = r \cdot P_0$ (new price)

**Step 2**: Solve for new reserves.

From the price condition:
$$y_1 = r \cdot P_0 \cdot x_1$$

Substituting into the invariant:
$$x_1 \cdot (r \cdot P_0 \cdot x_1) = k = x_0 \cdot y_0 = x_0^2 \cdot P_0$$

$$x_1^2 \cdot r \cdot P_0 = x_0^2 \cdot P_0$$

$$x_1 = \frac{x_0}{\sqrt{r}}$$

$$y_1 = r \cdot P_0 \cdot \frac{x_0}{\sqrt{r}} = \sqrt{r} \cdot P_0 \cdot x_0 = \sqrt{r} \cdot y_0$$

**Step 3**: Calculate LP portfolio value (in terms of token Y).

Value of LP position at time 1:
$$V_{LP} = x_1 \cdot P_1 + y_1 = \frac{x_0}{\sqrt{r}} \cdot r \cdot P_0 + \sqrt{r} \cdot y_0$$

$$V_{LP} = x_0 \cdot P_0 \cdot \sqrt{r} + y_0 \cdot \sqrt{r} = \sqrt{r}(x_0 P_0 + y_0)$$

Since $x_0 P_0 = y_0$ (initial price implies equal values in a 50/50 pool):

$$V_{LP} = \sqrt{r} \cdot 2y_0 = 2y_0\sqrt{r}$$

**Step 4**: Calculate HODL portfolio value.

Value of holding original tokens at time 1:
$$V_{HODL} = x_0 \cdot P_1 + y_0 = x_0 \cdot r \cdot P_0 + y_0 = r \cdot y_0 + y_0 = y_0(1 + r)$$

**Step 5**: Calculate IL.

$$IL = \frac{V_{LP}}{V_{HODL}} - 1 = \frac{2y_0\sqrt{r}}{y_0(1+r)} - 1$$

$$\boxed{IL = \frac{2\sqrt{r}}{1+r} - 1}$$

Where $r = P_1/P_0$ is the price ratio change.

### 2.3 IL Table

| Price Change ($r$) | IL        | Interpretation                     |
|--------------------|-----------|-------------------------------------|
| 0.25 (75% drop)   | -20.00%   | Severe loss                        |
| 0.50 (50% drop)   | -5.72%    | Significant loss                   |
| 0.75 (25% drop)   | -1.03%    | Moderate loss                      |
| 0.90 (10% drop)   | -0.14%    | Minor loss                         |
| 1.00 (no change)  | 0.00%     | No loss                            |
| 1.10 (10% rise)   | -0.14%    | Minor loss                         |
| 1.25 (25% rise)   | -0.60%    | Moderate loss                      |
| 1.50 (50% rise)   | -2.02%    | Significant loss                   |
| 2.00 (100% rise)  | -5.72%    | Severe loss                        |
| 3.00 (200% rise)  | -13.40%   | Very severe loss                   |
| 5.00 (400% rise)  | -25.46%   | Extreme loss                       |

### 2.4 Key Properties of IL

1. **Symmetric**: IL is the same for $r$ and $1/r$. A 2x increase and 50% decrease both give -5.72%.
2. **Always negative or zero**: IL can never be positive.
3. **Non-linear**: IL accelerates with larger price changes.
4. **Path-independent**: IL depends only on start and end price, not the path taken.
5. **Impermanent**: If $r$ returns to 1, IL returns to 0.

### 2.5 IL Rate of Change

The derivative of IL with respect to $r$:

$$
\frac{dIL}{dr} = \frac{1}{(1+r)^2} \cdot \left(\frac{1}{\sqrt{r}} - \frac{2\sqrt{r}}{1+r}\right) = \frac{1-\sqrt{r}}{(1+r)^2 \cdot \sqrt{r}}
$$

Wait, let me derive this more carefully:

$$IL(r) = \frac{2\sqrt{r}}{1+r} - 1$$

$$\frac{dIL}{dr} = \frac{2 \cdot \frac{1}{2\sqrt{r}} \cdot (1+r) - 2\sqrt{r} \cdot 1}{(1+r)^2}$$

$$= \frac{\frac{1+r}{\sqrt{r}} - 2\sqrt{r}}{(1+r)^2}$$

$$= \frac{1+r - 2r}{(1+r)^2 \sqrt{r}}$$

$$= \frac{1-r}{(1+r)^2 \sqrt{r}}$$

This is:
- Positive when $r < 1$ (IL is increasing toward 0 as price recovers from below)
- Zero when $r = 1$ (at the initial price, IL is minimized at 0)
- Negative when $r > 1$ (IL decreases as price rises above initial)

---

## 3. IL for Concentrated Liquidity

### 3.1 Amplified IL in Concentrated Positions

In Uniswap V3, concentrated liquidity amplifies both fee income AND impermanent loss.
The amplification factor equals the capital efficiency ratio.

For a position with range $[p_a, p_b]$ where the price ratio changes from $p_c$ to
$p_{new}$ (both within the range):

$$
IL_{concentrated} = IL_{v2}(r) \cdot \text{Amplification Factor}
$$

More precisely:

$$
IL_{concentrated} = \frac{V_{LP,concentrated}}{V_{HODL}} - 1
$$

### 3.2 Concentrated IL Derivation

For a Uniswap V3 position in range $[p_a, p_b]$ with initial price $p_0$ within range:

**LP Value at price $p$ (within range)**:

$$
V_{LP}(p) = L \cdot \left(\frac{1}{\sqrt{p}} - \frac{1}{\sqrt{p_b}}\right) \cdot p + L \cdot (\sqrt{p} - \sqrt{p_a})
$$

$$
= L \cdot \left(\sqrt{p} - \frac{p}{\sqrt{p_b}} + \sqrt{p} - \sqrt{p_a}\right)
$$

$$
= L \cdot \left(2\sqrt{p} - \frac{p}{\sqrt{p_b}} - \sqrt{p_a}\right)
$$

**HODL Value** (holding the initial token amounts):

$$
V_{HODL}(p) = \Delta x_0 \cdot p + \Delta y_0
$$

Where:
$$\Delta x_0 = L \cdot \left(\frac{1}{\sqrt{p_0}} - \frac{1}{\sqrt{p_b}}\right)$$

$$\Delta y_0 = L \cdot (\sqrt{p_0} - \sqrt{p_a})$$

So:

$$
V_{HODL}(p) = L \cdot \left(\frac{1}{\sqrt{p_0}} - \frac{1}{\sqrt{p_b}}\right) \cdot p + L \cdot (\sqrt{p_0} - \sqrt{p_a})
$$

$$
= L \cdot \left(\frac{p}{\sqrt{p_0}} - \frac{p}{\sqrt{p_b}} + \sqrt{p_0} - \sqrt{p_a}\right)
$$

**Concentrated IL**:

$$
IL_{conc} = \frac{V_{LP}(p)}{V_{HODL}(p)} - 1 = \frac{2\sqrt{p} - \frac{p}{\sqrt{p_b}} - \sqrt{p_a}}{\frac{p}{\sqrt{p_0}} - \frac{p}{\sqrt{p_b}} + \sqrt{p_0} - \sqrt{p_a}} - 1
$$

### 3.3 Simplified Amplified IL Formula

For a position concentrated in a range that is narrow relative to the price
(i.e., $p_a$ and $p_b$ are close to $p_0$), the IL is approximately:

$$
IL_{conc} \approx IL_{v2}(r) \cdot \frac{\sqrt{p_b}}{\sqrt{p_b} - \sqrt{p_a}} \cdot \frac{\sqrt{p_0}}{\sqrt{p_0}}
$$

The amplification factor for a symmetric range:

$$
A_{IL} \approx \frac{1}{1 - \sqrt{p_a/p_b}}
$$

### 3.4 IL When Price Exits Range

When the price exits the position range:

- **Price below range** ($p < p_a$): Position is 100% token X. The LP holds all of
  the depreciating asset. IL is maximized and continues to grow with price decline.

- **Price above range** ($p > p_b$): Position is 100% token Y. The LP has sold all
  token X and holds token Y. If token X continues to rise, the opportunity cost grows.

**At range boundary**:

When $p = p_a$ (lower boundary hit):
$$
V_{LP} = L \cdot \left(\sqrt{p_a} - \frac{p_a}{\sqrt{p_b}} + 0\right) = L \cdot \sqrt{p_a} \cdot \left(1 - \frac{\sqrt{p_a}}{\sqrt{p_b}}\right)
$$

When $p = p_b$ (upper boundary hit):
$$
V_{LP} = L \cdot (\sqrt{p_b} - \sqrt{p_a})
$$

### 3.5 IL Amplification Table (Concentrated vs V2)

For a position at ETH/USDC with $p_0 = 3000$:

| Range ($\pm$%) | Amplification | IL if price moves 10% | IL if price moves 20% |
|----------------|---------------|----------------------|----------------------|
| Full range (V2)| 1x            | -0.14%               | -0.60%               |
| $\pm$50%       | ~3x           | -0.42%               | -1.80%               |
| $\pm$20%       | ~8x           | -1.12%               | Out of range         |
| $\pm$10%       | ~16x          | Out of range*        | Out of range         |
| $\pm$5%        | ~33x          | Out of range          | Out of range         |

*Note: For $\pm$10% range, a 10% price move puts price at the boundary.

---

## 4. IL vs Trading Fee Income

### 4.1 The Fundamental LP Equation

An LP position is profitable if and only if:

$$
\text{Fee Income} > \text{Impermanent Loss} + \text{Gas Costs}
$$

Or equivalently:

$$
\text{Net APR}_{LP} = \text{Fee APR} - \text{IL APR} - \text{Gas APR} > 0
$$

### 4.2 Fee Income Model

For a constant product AMM:

$$
\text{Fee Income (period T)} = \frac{L_{position}}{L_{total}} \cdot V_T \cdot \gamma
$$

Where:
- $L_{position}$ = liquidity provided by this LP
- $L_{total}$ = total liquidity in the pool
- $V_T$ = trading volume during period $T$
- $\gamma$ = fee rate

As an APR:

$$
\text{Fee APR} = \frac{V_{annual} \cdot \gamma}{TVL} \cdot \frac{L_{position}}{L_{total}} \cdot \frac{TVL}{V_{position}}
$$

For concentrated liquidity where position covers 100% of volume:

$$
\text{Fee APR}_{concentrated} = \frac{V_{annual} \cdot \gamma \cdot E}{V_{position}}
$$

Where $E$ = capital efficiency ratio.

### 4.3 Expected IL Model

Expected IL depends on expected price volatility. For a normally distributed log-return
with volatility $\sigma$ over period $T$:

The expected value of $r = e^{\sigma\sqrt{T} \cdot Z}$ where $Z \sim N(0,1)$.

The expected IL is:

$$
\mathbb{E}[IL] = \mathbb{E}\left[\frac{2\sqrt{r}}{1+r} - 1\right]
$$

This can be approximated for small volatility:

$$
\mathbb{E}[IL] \approx -\frac{\sigma^2 T}{8}
$$

For larger volatility, the exact expectation requires numerical integration:

$$
\mathbb{E}[IL] = \int_{-\infty}^{\infty} \left(\frac{2\sqrt{e^{\sigma\sqrt{T}z}}}{1 + e^{\sigma\sqrt{T}z}} - 1\right) \phi(z) \, dz
$$

Where $\phi(z)$ is the standard normal PDF.

### 4.4 IL vs Fees — Visual Framework

```
Net LP Return
    ^
    |
    |     Fee Income (linear in volume)
    |    /
    |   /
    |  /          Point where Fees = IL
    | /       .--*----.
    |/  .--'          \  IL (grows with volatility)
    +--'----------------\----> Volatility
    |                    \
    |                     \
    |                      \
    v

PROFITABLE ZONE: Left of intersection (fees > IL)
UNPROFITABLE ZONE: Right of intersection (IL > fees)
```

### 4.5 Volume-to-TVL Ratio as Profitability Indicator

A key metric for LP profitability:

$$
\text{Volume/TVL Ratio} = \frac{V_{daily}}{TVL}
$$

Higher ratio means more fee income per unit of capital. Empirical guidelines:

| V/TVL Ratio | Fee APR (0.3% fee) | Typical IL | Net Assessment |
|-------------|-------------------|------------|----------------|
| > 0.50      | > 54.75%          | Variable   | Often profitable |
| 0.20 - 0.50 | 21.9% - 54.75%   | Variable   | Depends on vol |
| 0.10 - 0.20 | 10.95% - 21.9%   | Variable   | Marginal       |
| < 0.10      | < 10.95%          | Variable   | Often unprofitable |

---

## 5. Break-Even Fee Calculation

### 5.1 Break-Even Condition

The minimum trading volume needed for an LP position to break even:

$$
V_{break-even} = \frac{|IL| \cdot TVL}{\gamma \cdot \frac{L_{position}}{L_{total}}}
$$

For a concentrated position:

$$
V_{break-even} = \frac{|IL_{conc}| \cdot V_{position}}{\gamma}
$$

### 5.2 Break-Even Volatility

Given a known volume level, the maximum tolerable volatility:

From $\text{Fee APR} = \text{Expected IL Rate}$:

$$
\frac{V \cdot \gamma}{TVL} = \frac{\sigma^2}{8} \quad \text{(approximation)}
$$

$$
\sigma_{break-even} = \sqrt{\frac{8V\gamma}{TVL}} = \sqrt{\frac{8 \cdot \text{Fee APR}}{365}}
$$

### 5.3 Break-Even Time

How long must an LP position stay active to break even (assuming constant conditions):

$$
T_{break-even} = \frac{\text{Gas Cost}_{entry} + \text{Gas Cost}_{exit}}{\text{Daily Net Fee Income} - \text{Daily Expected IL}}
$$

### 5.4 Break-Even Calculator

```python
def calculate_break_even(
    position_value_usd: float,
    pool_tvl: float,
    daily_volume: float,
    fee_rate: float,
    annualized_volatility: float,
    capital_efficiency: float = 1.0,
    gas_cost_usd: float = 50.0
) -> dict:
    """
    Calculate break-even metrics for an LP position.

    Returns dict with:
    - break_even_days: Days to recover gas costs
    - daily_fee_income: Expected daily fee income
    - daily_il: Expected daily IL
    - daily_net: Net daily income
    - annual_net_apr: Annualized net return
    """

    # Daily fee income
    share_of_pool = position_value_usd / pool_tvl
    daily_fee_income = daily_volume * fee_rate * share_of_pool * capital_efficiency

    # Daily expected IL (approximation)
    daily_volatility = annualized_volatility / math.sqrt(365)
    daily_il_rate = (daily_volatility ** 2) / 8  # Approximation
    daily_il_loss = position_value_usd * daily_il_rate * capital_efficiency

    # Net daily income
    daily_net = daily_fee_income - daily_il_loss

    # Break-even time (to recover gas costs)
    if daily_net > 0:
        break_even_days = (gas_cost_usd * 2) / daily_net  # Entry + exit gas
    else:
        break_even_days = float('inf')  # Never breaks even

    # Annualized net APR
    annual_net_apr = (daily_net * 365) / position_value_usd

    return {
        'break_even_days': break_even_days,
        'daily_fee_income': daily_fee_income,
        'daily_il': daily_il_loss,
        'daily_net': daily_net,
        'annual_net_apr': annual_net_apr,
        'fee_apr': daily_fee_income * 365 / position_value_usd,
        'il_apr': daily_il_loss * 365 / position_value_usd,
    }
```

### 5.5 Break-Even Examples

For ETH/USDC pool with $\gamma = 0.3\%$, TVL = $100M, Daily Volume = $50M:

| Volatility (annual) | Daily Fee APR | Daily IL Rate | Net Daily | Break-Even |
|---------------------|---------------|---------------|-----------|------------|
| 30%                 | 0.041%        | 0.031%        | 0.010%    | ~55 days   |
| 50%                 | 0.041%        | 0.086%        | -0.045%   | Never      |
| 80%                 | 0.041%        | 0.219%        | -0.178%   | Never      |
| 20%                 | 0.041%        | 0.014%        | 0.027%    | ~20 days   |

This shows that at high volatility, simple LP positions are not profitable even
with high volume. Concentrated liquidity can improve the fee side but also amplifies IL.

---

## 6. Hedging IL with Options and Futures

### 6.1 Delta-Neutral Hedging

The most straightforward hedge: eliminate directional exposure.

**LP position delta** (for a 50/50 pool with token X as the risky asset):

At any point, the LP holds some amount of token X. The delta of the LP position:

$$
\Delta_{LP} = \frac{\partial V_{LP}}{\partial P} = \frac{x_1}{2} = \frac{x_0}{2\sqrt{r}}
$$

Wait — let's be more precise. For a V2 position with initial deposit $(x_0, y_0)$:

At price $P$:
$$
x(P) = \sqrt{k/P}
$$

$$
V_{LP}(P) = x(P) \cdot P + y(P) = 2\sqrt{k \cdot P}
$$

$$
\Delta_{LP} = \frac{\partial V_{LP}}{\partial P} = \frac{\sqrt{k}}{\sqrt{P}} = x(P)
$$

So the LP delta equals the current token X amount in the pool.

**Hedge**: Short $x(P)$ units of token X via futures or perps.

$$
\text{Hedged Position Value} = V_{LP}(P) - x(P) \cdot (P - P_0)
$$

This eliminates first-order price exposure but NOT IL (which is second-order).

### 6.2 Gamma Hedging (Second Order)

IL is fundamentally a gamma/convexity cost. The LP position has **negative gamma**
(concave payoff), meaning it underperforms HODL for any price move.

$$
\Gamma_{LP} = \frac{\partial^2 V_{LP}}{\partial P^2} = -\frac{\sqrt{k}}{2P^{3/2}} < 0
$$

To hedge gamma, buy options (which have positive gamma):

**Hedge strategy**: Buy a straddle (call + put) at the current price.

- Long straddle gamma: $\Gamma_{straddle} > 0$
- LP gamma: $\Gamma_{LP} < 0$
- Net gamma: $\Gamma_{net} \approx 0$ (if sized correctly)

**Required option notional**:

$$
\text{Option Notional} = \frac{|\Gamma_{LP}|}{\Gamma_{option}} \cdot \text{LP Value}
$$

### 6.3 Options-Based IL Hedging

#### Strategy 1: Long Straddle

Buy a call and put at the current price with the same expiry.

$$
\text{Cost} = C_{call} + C_{put} = \text{Premium}
$$

The straddle profits from large moves in either direction, offsetting IL.

**Sizing**: The straddle notional should be sized so its P&L offsets IL:

$$
\text{Notional}_{straddle} \approx \frac{V_{LP}}{2}
$$

**Problem**: Option premium (theta decay) may exceed the IL saved.

#### Strategy 2: Long Strangle (Cheaper)

Buy OTM call and OTM put:

$$
\text{Cost} = C_{call}(K_c) + C_{put}(K_p)
$$

Where $K_c > P_0$ and $K_p < P_0$.

Cheaper than straddle but provides less protection for small moves.

#### Strategy 3: Perpetual Options (Power Perpetuals)

Some DeFi protocols offer "power perpetuals" (e.g., Squeeth from Opyn):

$$
\text{Squeeth payoff} = P_{ETH}^2
$$

A short squeeth position has payoff characteristics similar to an LP:

$$
\text{Short Squeeth} \approx \text{Selling Gamma}
$$

Therefore: **Long Squeeth + LP position** creates a partial IL hedge.

### 6.4 Futures-Based Hedging

#### Strategy: Delta Hedge with Perpetual Futures

1. Calculate current LP delta: $\Delta_{LP} = x(P)$
2. Short $\Delta_{LP}$ units of token X on perpetual futures
3. Rebalance delta periodically as price changes

**Net exposure**:
$$
V_{hedged} = V_{LP} + \text{Futures P\&L} = V_{LP} - \Delta_{LP} \cdot (P - P_0) + \text{Funding}
$$

**Considerations**:
- Funding rates on perps can be positive (cost) or negative (income).
- In bullish markets, short positions pay funding.
- Delta needs continuous rebalancing (discrete hedging error).

#### Hedge Effectiveness Analysis

The delta hedge eliminates directional risk but not IL:

$$
\text{Residual IL (after delta hedge)} = V_{LP}(P) - V_{LP}(P_0) - \Delta_{LP} \cdot (P - P_0)
$$

This is approximately:

$$
\text{Residual} \approx \frac{1}{2} \Gamma_{LP} \cdot (P - P_0)^2 = -\frac{\sqrt{k}}{4P_0^{3/2}} \cdot (\Delta P)^2
$$

### 6.5 Cost-Benefit Analysis of Hedging

| Hedge Type      | Cost                  | IL Protection | Complexity |
|-----------------|-----------------------|---------------|------------|
| No hedge        | $0                    | 0%            | None       |
| Delta (futures) | Funding rate + rebal. | ~50%          | Medium     |
| Straddle        | Option premium        | ~80-90%       | Medium     |
| Strangle        | Lower premium         | ~60-70%       | Medium     |
| Power perps     | Funding/premium       | ~70-80%       | High       |
| Full gamma      | High premium          | ~95%          | Very High  |

### 6.6 When to Hedge vs When to Accept IL

Hedging is worthwhile when:

$$
\text{Cost of Hedge} < \text{Expected IL} - \text{Tolerable IL}
$$

Decision framework:

```
IF expected_volatility > break_even_volatility:
    IF hedge_cost < expected_IL - fee_income:
        -> HEDGE (protect against large IL)
    ELSE:
        -> DON'T LP (neither profitable nor cheaply hedgeable)
ELSE:
    -> LP WITHOUT HEDGE (fees cover expected IL)
```

---

## 7. Dynamic Range Adjustment to Minimize IL

### 7.1 Concept

Instead of hedging IL after it occurs, prevent it by dynamically adjusting the
LP range. The key insight:

**IL only crystallizes when price exits the range and the position is rebalanced.**

By adjusting the range to follow price, we can:
- Keep the position always in range (earning fees).
- Reduce the effective IL by frequently resetting the price ratio.

### 7.2 Range Following Strategy

```
Every rebalance_interval:
  1. Check if current price is near range boundary
  2. If within 15% of boundary:
     a. Remove liquidity (collect current tokens + fees)
     b. Calculate new optimal range centered on current price
     c. Swap tokens to correct ratio for new range
     d. Deposit into new range
  3. Record the "realized IL" from this rebalance cycle
```

### 7.3 IL Decomposition with Rebalancing

With $N$ rebalances over period $T$, each sub-period has price change $r_i$:

$$
\text{Total Realized IL} = \sum_{i=1}^{N} IL(r_i) \cdot V_{position,i}
$$

Since IL is convex in $r$, frequent rebalancing (smaller $r_i$ per period) results
in less total IL:

$$
\sum_{i=1}^{N} IL(r_i) < IL\left(\prod_{i=1}^{N} r_i\right) \quad \text{(False! IL is concave in log-returns)}
$$

Actually, careful analysis shows:

$$
IL(r) \approx -\frac{(\ln r)^2}{8} \text{ for small moves}
$$

And the sum of squared log-returns:
$$
\sum_{i=1}^{N} (\ln r_i)^2 \approx \sigma^2 T
$$

regardless of $N$. So frequent rebalancing does NOT reduce expected IL — it just
makes it more predictable (lower variance of IL).

### 7.4 Why Range Adjustment Still Helps

Range adjustment helps through a different mechanism:

1. **Prevents out-of-range positions**: An out-of-range position earns zero fees
   but still has IL exposure. Range adjustment keeps position earning fees.

2. **Tighter ranges earn more fees**: By actively managing range, you can maintain
   a tight, high-efficiency range that earns more fees to offset IL.

3. **Asymmetric adjustment**: If you have a directional view, bias the range to
   reduce IL in the expected direction.

### 7.5 Optimal Rebalancing Frequency

The optimal frequency balances gas costs vs benefits:

$$
f^* = \argmax_f \left\{ \text{Fee Income}(f) - \text{Gas Cost}(f) \right\}
$$

Where:
- Fee Income increases with frequency (tighter ranges possible).
- Gas Cost increases linearly with frequency.

Approximate optimal:

$$
f^* \approx \sqrt{\frac{\text{Daily Fee Income}}{2 \cdot \text{Gas Cost per Rebalance}}}
$$

### 7.6 Bollinger Band Range Strategy

Use volatility bands to set dynamic ranges:

$$
\text{Upper Range} = P_{current} \cdot e^{k \cdot \sigma \cdot \sqrt{T_{rebal}}}
$$

$$
\text{Lower Range} = P_{current} \cdot e^{-k \cdot \sigma \cdot \sqrt{T_{rebal}}}
$$

Where:
- $k$ = confidence multiplier (typically 1.5-2.5)
- $\sigma$ = current realized volatility
- $T_{rebal}$ = expected time until next rebalance

This adapts to market conditions:
- High volatility -> wider range (avoid frequent out-of-range)
- Low volatility -> tighter range (maximize capital efficiency)

---

## 8. IL for Multi-Asset Pools

### 8.1 Generalized IL Formula

For a pool with $n$ tokens with weights $w_1, w_2, ..., w_n$ (summing to 1):

$$
IL = \frac{\prod_{i=1}^{n} r_i^{w_i}}{\sum_{i=1}^{n} w_i \cdot r_i} - 1
$$

Where $r_i = P_i^{new} / P_i^{old}$ is the price ratio for token $i$.

### 8.2 Derivation for Two-Token Weighted Pool

For a pool with weights $(w_x, w_y)$ where $w_x + w_y = 1$:

The invariant: $x^{w_x} \cdot y^{w_y} = k$

After token X price changes by factor $r$ (relative to Y):

$$
V_{LP} = V_0 \cdot r^{w_x}
$$

$$
V_{HODL} = V_0 \cdot (w_x \cdot r + w_y)
$$

$$
IL = \frac{r^{w_x}}{w_x \cdot r + w_y} - 1
$$

For the 50/50 case ($w_x = w_y = 0.5$):

$$
IL = \frac{r^{0.5}}{0.5r + 0.5} - 1 = \frac{2\sqrt{r}}{1+r} - 1
$$

Which matches the standard formula.

### 8.3 IL for 80/20 Pool (Balancer Style)

With $w_x = 0.8$ (risky asset), $w_y = 0.2$ (stable):

$$
IL = \frac{r^{0.8}}{0.8r + 0.2} - 1
$$

| $r$ | IL (80/20) | IL (50/50) | Reduction |
|-----|-----------|-----------|-----------|
| 0.5 | -1.52%    | -5.72%    | 73%       |
| 0.75| -0.15%    | -1.03%    | 85%       |
| 1.5 | -0.52%    | -2.02%    | 74%       |
| 2.0 | -1.52%    | -5.72%    | 73%       |
| 3.0 | -3.68%    | -13.40%   | 73%       |

**Key insight**: 80/20 pools dramatically reduce IL, making them attractive for
long-term liquidity provision on volatile assets.

### 8.4 Three-Token Pool IL

For a three-token pool with equal weights (1/3 each):

$$
IL = \frac{(r_1 \cdot r_2 \cdot r_3)^{1/3}}{\frac{1}{3}(r_1 + r_2 + r_3)} - 1
$$

If we set $r_3 = 1$ (one stable token) and vary $r_1$ and $r_2$:

This is the ratio of geometric mean to arithmetic mean, which is always $\leq 1$
by the AM-GM inequality, confirming IL is always non-positive.

### 8.5 Correlated Assets and IL

When assets are correlated ($\rho > 0$), expected IL is lower because price ratios
stay closer to 1.

For two assets with log-return correlation $\rho$:

The price ratio volatility is:

$$
\sigma_{ratio} = \sqrt{\sigma_1^2 + \sigma_2^2 - 2\rho\sigma_1\sigma_2}
$$

Expected IL depends on $\sigma_{ratio}$:

$$
\mathbb{E}[IL] \approx -\frac{\sigma_{ratio}^2 \cdot T}{8}
$$

| Pair Type               | $\rho$  | $\sigma_{ratio}$ | IL Magnitude |
|-------------------------|---------|-------------------|--------------|
| ETH/BTC                 | ~0.8    | Low               | Low          |
| ETH/USDC               | ~0.0    | High              | High         |
| stETH/ETH              | ~0.99   | Very low          | Very low     |
| USDC/USDT              | ~0.99+  | Minimal           | Minimal      |
| ETH/random altcoin     | ~0.3-0.6| Medium-High       | Medium-High  |

---

## 9. Complete Mathematical Models

### 9.1 Unified IL Framework

**Standard IL (Uniswap V2, 50/50)**:

$$
IL_{v2}(r) = \frac{2\sqrt{r}}{1 + r} - 1
$$

**Weighted IL (Balancer)**:

$$
IL_{weighted}(r, w) = \frac{r^w}{w \cdot r + (1-w)} - 1
$$

**Concentrated IL (Uniswap V3)**:

For price within range $[p_a, p_b]$, current price $p$, entry price $p_0$:

$$
IL_{v3}(p, p_0, p_a, p_b) = \frac{2\sqrt{p} - p/\sqrt{p_b} - \sqrt{p_a}}{p/\sqrt{p_0} - p/\sqrt{p_b} + \sqrt{p_0} - \sqrt{p_a}} - 1
$$

**Multi-asset IL**:

$$
IL_{multi}(\mathbf{r}, \mathbf{w}) = \frac{\prod_{i} r_i^{w_i}}{\sum_{i} w_i r_i} - 1
$$

### 9.2 Expected IL Under Geometric Brownian Motion

If price follows GBM: $dP/P = \mu \, dt + \sigma \, dW$

Then $r = P_T/P_0 = e^{(\mu - \sigma^2/2)T + \sigma W_T}$

Expected IL:

$$
\mathbb{E}[IL] = 2\mathbb{E}\left[\frac{\sqrt{r}}{1+r}\right] - 1
$$

Using the moment generating function of the normal distribution:

$$
\mathbb{E}[\sqrt{r}] = e^{(\mu - \sigma^2/2)T/2 + \sigma^2 T/8} = e^{\mu T/2 - \sigma^2 T/8}
$$

The full expectation requires numerical integration:

$$
\mathbb{E}[IL] = \int_{-\infty}^{\infty} \left(\frac{2e^{z\sigma\sqrt{T}/2 + (\mu-\sigma^2/2)T/2}}{1 + e^{z\sigma\sqrt{T} + (\mu-\sigma^2/2)T}} - 1\right) \frac{e^{-z^2/2}}{\sqrt{2\pi}} \, dz
$$

### 9.3 IL Sensitivity Analysis (Greeks)

**IL Delta** (sensitivity to price):

$$
\frac{\partial IL}{\partial r} = \frac{1 - r}{(1+r)^2 \sqrt{r}}
$$

**IL Gamma** (second-order sensitivity):

$$
\frac{\partial^2 IL}{\partial r^2} = \frac{-3r^2 - 2r + 1}{2r^{3/2}(1+r)^3}
$$

At $r = 1$ (initial price):
$$
\frac{\partial^2 IL}{\partial r^2}\bigg|_{r=1} = \frac{-3 - 2 + 1}{2 \cdot 1 \cdot 8} = -\frac{4}{16} = -\frac{1}{4}
$$

This confirms IL is locally quadratic: $IL \approx -\frac{1}{8}(\Delta \ln P)^2$

**IL Theta** (sensitivity to time, via volatility):

$$
\frac{\partial \mathbb{E}[IL]}{\partial T} \approx -\frac{\sigma^2}{8}
$$

This shows expected IL grows linearly with time (like theta decay in options).

### 9.4 IL Variance

The variance of IL is important for risk management:

$$
\text{Var}[IL] = \mathbb{E}[IL^2] - (\mathbb{E}[IL])^2
$$

For small moves (Taylor expansion):

$$
\text{Var}[IL] \approx \frac{\sigma^4 T^2}{32}
$$

The standard deviation of IL:

$$
\text{Std}[IL] \approx \frac{\sigma^2 T}{4\sqrt{2}}
$$

---

## 10. Strategy for Maximizing Yield Net of IL

### 10.1 Optimal Pool Selection

The objective is to maximize:

$$
\max_{pool \in \mathcal{P}} \left\{ \frac{V_{pool} \cdot \gamma_{pool}}{TVL_{pool}} - \frac{\sigma_{pool}^2}{8} \right\}
$$

This simplifies to selecting pools where:

$$
\frac{V \cdot \gamma}{TVL} > \frac{\sigma^2}{8}
$$

Or equivalently:

$$
\frac{V}{TVL} > \frac{\sigma^2}{8\gamma}
$$

### 10.2 Capital Allocation Across Pools

For multiple pools, solve the optimization:

$$
\max_{\{w_j\}} \sum_j w_j \cdot \text{Net APR}_j
$$

Subject to:
- $\sum_j w_j = 1$
- $w_j \geq 0$
- $\text{Risk}(w_j) \leq R_{max}$

Where $\text{Net APR}_j = \text{Fee APR}_j - \text{Expected IL}_j - \text{Gas APR}_j$

### 10.3 Time-Weighted Strategy

Adjust LP positions based on market regimes:

| Market Regime     | Volatility | Volume | Optimal Action                     |
|-------------------|------------|--------|------------------------------------|
| Low vol, High vol.| Low        | High   | Tight range, aggressive LP         |
| Low vol, Low vol. | Low        | Low    | Wide range or don't LP             |
| High vol, High vol.| High      | High   | Medium range, hedge delta          |
| High vol, Low vol.| High       | Low    | Exit LP, hold assets               |

### 10.4 Fee Tier Optimization

Choose fee tier to maximize net return:

| Pair Type        | Optimal Fee | Reasoning                              |
|------------------|-------------|----------------------------------------|
| Stable/Stable    | 0.01%       | Near-zero IL, high volume per $ of fees|
| Blue-chip/Stable | 0.05-0.30%  | Moderate IL, need fees to compensate   |
| Volatile/Stable  | 0.30-1.00%  | High IL, need high fees                |
| Volatile/Volatile| 1.00%       | Very high IL, maximum fee compensation |

### 10.5 Compound vs Claim Strategy

Should the bot auto-compound fees or claim and hedge?

**Auto-compound** (reinvest fees into LP):
$$
V_{compound}(T) = V_0 \cdot e^{(\text{Fee APR} - \text{IL Rate}) \cdot T}
$$

**Claim and hedge** (remove fees, convert to stables):
$$
V_{claim}(T) = V_0 \cdot e^{-\text{IL Rate} \cdot T} + \text{Fees Accumulated}
$$

Claim-and-hedge is better when you want to lock in fee profits without re-exposing
them to IL.

---

## 11. Algorithmic IL Monitoring and Rebalancing

### 11.1 Real-Time IL Tracker

```python
class ILMonitor:
    """
    Monitors impermanent loss in real-time for all LP positions.
    Triggers alerts and rebalancing actions based on thresholds.
    """

    def __init__(self, config: ILMonitorConfig):
        self.warning_threshold = config.warning_il  # e.g., -2%
        self.critical_threshold = config.critical_il  # e.g., -5%
        self.exit_threshold = config.exit_il  # e.g., -8%
        self.oracle = PriceOracle()
        self.positions = {}

    def calculate_il_v2(self, entry_price: float, current_price: float) -> float:
        """Calculate IL for a V2-style (full range) position."""
        r = current_price / entry_price
        return 2 * math.sqrt(r) / (1 + r) - 1

    def calculate_il_v3(
        self,
        entry_price: float,
        current_price: float,
        range_lower: float,
        range_upper: float
    ) -> float:
        """Calculate IL for a V3 concentrated liquidity position."""
        # Check if price is within range
        if current_price <= range_lower:
            # Position is 100% token X — maximum IL for this direction
            # Compare LP value (all token X) vs HODL
            p = current_price
            p0 = entry_price
            pa = range_lower
            pb = range_upper

            # LP value (all token X at current price)
            # Position was converted fully to token X at range_lower
            lp_value_at_boundary = 2 * math.sqrt(pa) - pa/math.sqrt(pb) - math.sqrt(pa)
            # Needs to be relative calculation
            pass

        elif current_price >= range_upper:
            # Position is 100% token Y
            pass

        else:
            # Within range — use concentrated IL formula
            p = current_price
            p0 = entry_price
            pa = range_lower
            pb = range_upper

            sqrt_p = math.sqrt(p)
            sqrt_p0 = math.sqrt(p0)
            sqrt_pa = math.sqrt(pa)
            sqrt_pb = math.sqrt(pb)

            # LP value (per unit of liquidity L)
            v_lp = 2 * sqrt_p - p / sqrt_pb - sqrt_pa

            # HODL value (per unit of liquidity L)
            v_hodl = (1/sqrt_p0 - 1/sqrt_pb) * p + (sqrt_p0 - sqrt_pa)

            il = v_lp / v_hodl - 1
            return il

    def calculate_il_precise(self, position: LPPosition) -> ILResult:
        """
        Precise IL calculation considering actual token amounts.
        """
        # Get current prices
        price_token0 = self.oracle.get_price(position.token0)
        price_token1 = self.oracle.get_price(position.token1)

        # Current LP value
        amounts = position.get_current_amounts()
        v_lp_current = amounts.token0 * price_token0 + amounts.token1 * price_token1

        # HODL value (what we would have if we just held initial amounts)
        v_hodl = (position.initial_token0 * price_token0 +
                  position.initial_token1 * price_token1)

        # Fees earned
        fees = position.get_unclaimed_fees()
        fee_value = fees.token0 * price_token0 + fees.token1 * price_token1

        # IL calculation
        il_absolute = v_lp_current - v_hodl  # In USD
        il_relative = il_absolute / v_hodl   # As percentage

        # Net P&L including fees
        net_pnl = il_absolute + fee_value

        return ILResult(
            il_absolute=il_absolute,
            il_relative=il_relative,
            fee_income=fee_value,
            net_pnl=net_pnl,
            fee_offset_ratio=fee_value / abs(il_absolute) if il_absolute != 0 else float('inf')
        )

    async def monitor_loop(self):
        """Main monitoring loop."""
        while True:
            for pos_id, position in self.positions.items():
                il_result = self.calculate_il_precise(position)

                # Update tracking
                position.current_il = il_result.il_relative
                position.cumulative_fees = il_result.fee_income

                # Check thresholds
                if il_result.il_relative < self.exit_threshold:
                    await self.trigger_exit(pos_id, position, il_result)
                elif il_result.il_relative < self.critical_threshold:
                    await self.trigger_critical_alert(pos_id, position, il_result)
                elif il_result.il_relative < self.warning_threshold:
                    await self.trigger_warning(pos_id, position, il_result)

                # Check if fees still covering IL
                if il_result.fee_offset_ratio < 0.5:
                    # Fees covering less than 50% of IL
                    await self.evaluate_position_viability(pos_id, position)

            await asyncio.sleep(30)  # Check every 30 seconds
```

### 11.2 Predictive IL Model

```python
class PredictiveILModel:
    """
    Predicts future IL based on volatility forecasts.
    Used for preemptive position management.
    """

    def predict_il(
        self,
        current_price: float,
        volatility_forecast: float,
        time_horizon_days: float,
        confidence_level: float = 0.95
    ) -> ILPrediction:
        """
        Predict IL distribution over time horizon.
        """
        sigma_T = volatility_forecast * math.sqrt(time_horizon_days / 365)

        # Expected IL (center of distribution)
        expected_il = -(sigma_T ** 2) / 8

        # IL at confidence level (VaR-style)
        # Price could move by z * sigma
        z = scipy.stats.norm.ppf(confidence_level)
        worst_case_move = math.exp(z * sigma_T)

        worst_case_il = 2 * math.sqrt(worst_case_move) / (1 + worst_case_move) - 1

        # IL distribution via Monte Carlo
        n_simulations = 10000
        il_distribution = []
        for _ in range(n_simulations):
            z_sim = random.gauss(0, 1)
            r = math.exp(sigma_T * z_sim)
            il_sim = 2 * math.sqrt(r) / (1 + r) - 1
            il_distribution.append(il_sim)

        return ILPrediction(
            expected_il=expected_il,
            il_var_95=sorted(il_distribution)[int(0.05 * n_simulations)],
            il_var_99=sorted(il_distribution)[int(0.01 * n_simulations)],
            worst_case_il=worst_case_il,
            distribution=il_distribution,
            confidence_level=confidence_level
        )

    def should_enter_position(
        self,
        expected_fee_apr: float,
        volatility_forecast: float,
        time_horizon_days: float,
        risk_tolerance: float
    ) -> bool:
        """
        Determine if entering an LP position is worthwhile
        given IL predictions.
        """
        prediction = self.predict_il(
            current_price=1,  # Normalized
            volatility_forecast=volatility_forecast,
            time_horizon_days=time_horizon_days
        )

        # Expected net return
        expected_fee_income = expected_fee_apr * time_horizon_days / 365
        expected_net = expected_fee_income + prediction.expected_il

        # Risk-adjusted return (Sharpe-like)
        il_std = abs(prediction.il_var_95 - prediction.expected_il) / 1.645
        risk_adjusted = expected_net / il_std if il_std > 0 else 0

        return expected_net > 0 and risk_adjusted > risk_tolerance
```

### 11.3 Automated Rebalancing Engine

```python
class ILRebalancingEngine:
    """
    Automatically rebalances LP positions to minimize IL impact.
    """

    def __init__(self, config: RebalanceConfig):
        self.max_il_before_rebalance = config.max_il_trigger  # e.g., -3%
        self.min_benefit_multiple = config.min_benefit_multiple  # e.g., 3x gas
        self.volatility_model = VolatilityModel()
        self.gas_estimator = GasEstimator()

    async def evaluate_rebalance(self, position: LPPosition) -> RebalanceDecision:
        """
        Evaluate whether to rebalance a position and determine new range.
        """
        current_price = await self.get_current_price(position.pool)
        current_il = self.calculate_current_il(position, current_price)

        # Get current volatility regime
        vol = await self.volatility_model.get_current(position.pool)

        # Calculate optimal new range
        new_range = self.calculate_new_range(current_price, vol, position.pool.fee_rate)

        # Estimate benefit of rebalancing
        current_fee_rate = self.estimate_fee_rate(position)
        new_fee_rate = self.estimate_fee_rate_for_range(new_range, position.pool)
        daily_benefit = (new_fee_rate - current_fee_rate) * position.value

        # Estimate time in new range
        time_in_range = self.estimate_time_in_range(new_range, vol)
        total_benefit = daily_benefit * time_in_range

        # Gas cost
        gas_cost = await self.gas_estimator.estimate_rebalance_cost()

        # Decision
        if total_benefit > gas_cost * self.min_benefit_multiple:
            return RebalanceDecision(
                should_rebalance=True,
                new_range=new_range,
                expected_benefit=total_benefit,
                gas_cost=gas_cost,
                reason=f"Expected benefit ${total_benefit:.2f} > "
                       f"{self.min_benefit_multiple}x gas ${gas_cost:.2f}"
            )
        else:
            return RebalanceDecision(
                should_rebalance=False,
                reason=f"Benefit ${total_benefit:.2f} insufficient vs gas ${gas_cost:.2f}"
            )

    def calculate_new_range(
        self, current_price: float, volatility: float, fee_rate: float
    ) -> PriceRange:
        """Calculate optimal range for rebalanced position."""
        # Target: 80% probability of staying in range for 1 rebalance period
        target_prob = 0.80
        z = scipy.stats.norm.ppf((1 + target_prob) / 2)  # ~1.28

        # Expected time between rebalances (in days)
        rebal_period = 3  # days

        # Range width in log space
        half_width = z * volatility * math.sqrt(rebal_period / 365)

        # Adjust for fee rate (higher fees -> can afford tighter)
        fee_adjustment = math.sqrt(fee_rate / 0.003)
        half_width *= fee_adjustment

        # Apply bounds
        half_width = max(0.02, min(half_width, 0.50))

        return PriceRange(
            lower=current_price * math.exp(-half_width),
            upper=current_price * math.exp(half_width)
        )
```

---

## 12. Risk Parameters

### 12.1 IL Risk Limits

| Parameter                          | Value   | Rationale                          |
|------------------------------------|---------|------------------------------------|
| Max IL per position (warning)      | -2%     | Alert for manual review            |
| Max IL per position (critical)     | -5%     | Trigger rebalance evaluation       |
| Max IL per position (exit)         | -8%     | Force exit regardless of fees      |
| Max aggregate IL (portfolio)       | -3%     | Total IL across all LP positions   |
| Max IL velocity (per hour)         | -1%     | Rapid IL increase → high vol event |
| Min fee/IL ratio                   | 0.5     | Fees must cover at least 50% of IL |
| Max vol for new LP entry           | 80%     | Don't enter LP in extreme volatility |

### 12.2 Rebalancing Parameters

| Parameter                         | Value        | Rationale                        |
|-----------------------------------|--------------|----------------------------------|
| Min benefit/gas ratio             | 3x           | Ensure rebalance is worthwhile   |
| Max rebalance frequency           | 1 per hour   | Gas cost management              |
| Min time in position              | 4 hours      | Avoid churning                   |
| Preemptive rebalance trigger      | 85% of range | Rebalance before hitting boundary|
| Gas price cap for rebalance       | 100 gwei     | Delay rebalance in expensive gas |
| Slippage tolerance (rebalance)    | 0.5%         | Max swap slippage                |

### 12.3 Position Sizing

$$
\text{Max Position Size} = \min\left(\frac{\text{IL Budget}}{\text{Expected IL Rate}}, \frac{\text{Pool TVL} \times 0.01}{\text{Capital Efficiency}}\right)
$$

Rule: Never provide more than 1% of a pool's TVL (to avoid excessive market impact on
entry/exit and ensure realistic fee income estimates).

---

## 13. Execution Flow — IL Management Bot

### 13.1 Complete IL Management System

```python
class ILManagementSystem:
    """
    Complete system for managing impermanent loss across all LP positions.
    Integrates monitoring, prediction, hedging, and rebalancing.
    """

    def __init__(self, config: SystemConfig):
        self.monitor = ILMonitor(config.monitor)
        self.predictor = PredictiveILModel()
        self.rebalancer = ILRebalancingEngine(config.rebalance)
        self.hedger = ILHedger(config.hedge)
        self.portfolio = PortfolioManager()

    async def main_loop(self):
        """Main execution loop for IL management."""

        while True:
            # ============================================
            # STEP 1: Monitor all positions
            # ============================================
            for position in self.portfolio.get_lp_positions():
                il_result = self.monitor.calculate_il_precise(position)

                # ============================================
                # STEP 2: Check emergency conditions
                # ============================================
                if il_result.il_relative < self.config.exit_threshold:
                    await self.emergency_exit(position, il_result)
                    continue

                # ============================================
                # STEP 3: Predict future IL
                # ============================================
                vol_forecast = await self.predictor.get_volatility_forecast(
                    position.pool, horizon_days=7
                )
                il_prediction = self.predictor.predict_il(
                    current_price=position.current_price,
                    volatility_forecast=vol_forecast,
                    time_horizon_days=7
                )

                # ============================================
                # STEP 4: Evaluate rebalancing need
                # ============================================
                rebal_decision = await self.rebalancer.evaluate_rebalance(position)
                if rebal_decision.should_rebalance:
                    await self.execute_rebalance(position, rebal_decision)

                # ============================================
                # STEP 5: Evaluate hedging need
                # ============================================
                if il_prediction.il_var_95 < self.config.hedge_trigger:
                    hedge_plan = self.hedger.calculate_hedge(
                        position, il_prediction, vol_forecast
                    )
                    if hedge_plan.is_cost_effective():
                        await self.execute_hedge(position, hedge_plan)

                # ============================================
                # STEP 6: Update portfolio metrics
                # ============================================
                self.portfolio.update_il_metrics(position, il_result, il_prediction)

            # ============================================
            # STEP 7: Portfolio-level IL check
            # ============================================
            total_il = self.portfolio.get_aggregate_il()
            if total_il < self.config.portfolio_il_limit:
                await self.reduce_overall_exposure()

            # ============================================
            # STEP 8: Report metrics
            # ============================================
            await self.report_metrics()

            await asyncio.sleep(30)

    async def emergency_exit(self, position: LPPosition, il_result: ILResult):
        """Emergency exit when IL exceeds maximum threshold."""
        logger.critical(
            f"EMERGENCY EXIT: Position {position.id} "
            f"IL={il_result.il_relative:.2%} exceeds threshold "
            f"{self.config.exit_threshold:.2%}"
        )

        # Remove liquidity immediately
        await self.portfolio.remove_liquidity(position)

        # Close any hedges
        if position.has_hedge:
            await self.hedger.close_hedge(position)

        # Log P&L
        final_pnl = il_result.net_pnl
        logger.info(f"Position {position.id} closed. Net P&L: ${final_pnl:,.2f}")

    async def execute_rebalance(
        self, position: LPPosition, decision: RebalanceDecision
    ):
        """Execute a rebalancing operation."""
        logger.info(f"Rebalancing position {position.id}: {decision.reason}")

        # Check gas conditions
        gas_price = await self.gas_estimator.get_current()
        if gas_price > self.config.max_gas_for_rebalance:
            logger.info("Gas too high, deferring rebalance")
            return

        # Execute rebalance
        await self.rebalancer.execute(position, decision.new_range)

        # Update position records
        position.update_after_rebalance(
            new_range=decision.new_range,
            gas_cost=decision.gas_cost
        )

    async def execute_hedge(self, position: LPPosition, hedge_plan: HedgePlan):
        """Execute IL hedge."""
        logger.info(f"Hedging position {position.id}: {hedge_plan.description}")

        if hedge_plan.type == HedgeType.DELTA_FUTURES:
            await self.hedger.open_short_perp(
                token=position.token0,
                size=hedge_plan.size,
                exchange=hedge_plan.exchange
            )
        elif hedge_plan.type == HedgeType.OPTIONS_STRADDLE:
            await self.hedger.buy_straddle(
                token=position.token0,
                notional=hedge_plan.size,
                expiry=hedge_plan.expiry
            )

        position.hedge = hedge_plan
```

---

## 14. References

### Academic Papers

1. Loesch, S., Hindman, N., Richardson, M.B., Welch, N. (2021).
   "Impermanent Loss in Uniswap v3." arXiv:2111.09192.

2. Aigner, A.A., Dhaliwal, G. (2021). "UNISWAP: Impermanent Loss and Risk Profile
   of a Liquidity Provider." arXiv:2106.14404.

3. Clark, J. (2020). "The Replicating Portfolio of a Constant Product Market."
   SSRN.

4. Lambert, G. (2021). "Uniswap V3 LP Tokens as Perpetual Put and Call Options."
   Lambert Finance Research.

5. Milionis, J., Moallemi, C.C., Roughgarden, T., Zhang, A.L. (2022).
   "Automated Market Making and Loss-Versus-Rebalancing."
   arXiv:2208.06046.

6. Heimbach, L., Wattenhofer, R. (2022). "Risks and Returns of Uniswap V3
   Liquidity Providers." arXiv:2205.08904.

### Protocol Research

7. Uniswap Labs. "Uniswap v3 Core." 2021.
   https://uniswap.org/whitepaper-v3.pdf

8. Paradigm Research. "Understanding Automated Market Maker IL."
   https://research.paradigm.xyz/

9. Delphi Digital. "The Complete Guide to Impermanent Loss."
   Delphi Research Reports.

### Tools and Implementations

10. Revert Finance — Uniswap V3 Analytics. https://revert.finance/
11. Croco Finance — IL Calculator. https://croco.finance/
12. DeFi Lab — IL Simulator. https://defi-lab.xyz/

---

> **Next Document**: [03_yield_strategies.md](./03_yield_strategies.md)
> — Yield farming mechanics, auto-compounding, and aggregator strategies.
