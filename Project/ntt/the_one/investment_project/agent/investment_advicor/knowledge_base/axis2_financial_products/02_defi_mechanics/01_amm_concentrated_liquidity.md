# AMM & Concentrated Liquidity — Deep Dive

> **Axis 2 — Financial Products | Module 02 — DeFi Mechanics | Document 01**
> Version: 2.0.0 | Last Updated: 2026-04-12
> Classification: KNOWLEDGE BASE — MULTI-AGENT AI TRADING SYSTEM

---

## Table of Contents

1. [Introduction to Automated Market Makers](#1-introduction-to-automated-market-makers)
2. [Constant Product Market Maker (CPMM)](#2-constant-product-market-maker-cpmm)
3. [Uniswap V2 Mechanics](#3-uniswap-v2-mechanics)
4. [Uniswap V3 Concentrated Liquidity](#4-uniswap-v3-concentrated-liquidity)
5. [Tick System Deep Dive](#5-tick-system-deep-dive)
6. [Concentrated Liquidity Mathematics](#6-concentrated-liquidity-mathematics)
7. [Capital Efficiency Analysis](#7-capital-efficiency-analysis)
8. [Position Management Strategies](#8-position-management-strategies)
9. [Range Order Strategies](#9-range-order-strategies)
10. [Curve Finance StableSwap](#10-curve-finance-stableswap)
11. [Balancer Weighted Pools](#11-balancer-weighted-pools)
12. [Just-in-Time (JIT) Liquidity](#12-just-in-time-jit-liquidity)
13. [Optimal Liquidity Provision Strategies](#13-optimal-liquidity-provision-strategies)
14. [Complete Mathematical Framework](#14-complete-mathematical-framework)
15. [Execution Flow — LP Management Bot](#15-execution-flow--lp-management-bot)
16. [Risk Parameters](#16-risk-parameters)
17. [References](#17-references)

---

## 1. Introduction to Automated Market Makers

### 1.1 Why AMMs Exist

Traditional order book exchanges require market makers to actively post bids and asks.
In DeFi, this approach faces fundamental challenges:

- **Gas costs**: Posting and canceling orders on-chain is expensive.
- **Latency**: Blockchain block times (12 sec on Ethereum) make HFT-style market
  making impractical on L1.
- **Capital requirements**: Professional market makers need significant infrastructure.

Automated Market Makers solve this by replacing the order book with a **mathematical
pricing function** that deterministically computes prices based on pool reserves.

### 1.2 AMM Classification

| AMM Type              | Formula                        | Best For                    | Example          |
|-----------------------|--------------------------------|-----------------------------|------------------|
| Constant Product      | $x \cdot y = k$               | Volatile pairs              | Uniswap V2       |
| Concentrated Liquidity| Virtual reserves in ranges     | All pairs (capital efficient)| Uniswap V3      |
| StableSwap            | Hybrid constant sum/product    | Pegged assets               | Curve Finance    |
| Weighted              | $\prod x_i^{w_i} = k$         | Portfolio-style exposure    | Balancer          |
| Constant Sum          | $x + y = k$                   | 1:1 pegged (theoretical)   | Rarely used      |
| Proactive MM          | External oracle-driven         | Reducing IL                 | Ambient/CrocSwap |

---

## 2. Constant Product Market Maker (CPMM)

### 2.1 The Invariant

The Constant Product Market Maker is defined by the invariant:

$$
x \cdot y = k
$$

Where:
- $x$ = reserve of token X in the pool
- $y$ = reserve of token Y in the pool
- $k$ = constant (increases only when liquidity is added)

### 2.2 Price Derivation

The marginal price of token X in terms of token Y is the negative derivative of the
invariant curve:

$$
P_X = \frac{y}{x}
$$

$$
P_Y = \frac{x}{y}
$$

This means the price is simply the ratio of reserves.

### 2.3 Swap Output Calculation

When a trader wants to swap $\Delta x$ of token X for token Y:

**Without fees**:

$$
\Delta y = \frac{y \cdot \Delta x}{x + \Delta x}
$$

Derivation:
1. Before swap: $x \cdot y = k$
2. After swap: $(x + \Delta x) \cdot (y - \Delta y) = k$
3. Solving: $y - \Delta y = \frac{k}{x + \Delta x} = \frac{x \cdot y}{x + \Delta x}$
4. Therefore: $\Delta y = y - \frac{x \cdot y}{x + \Delta x} = \frac{y \cdot \Delta x}{x + \Delta x}$

**With fees** (fee rate $\gamma$, e.g., 0.003 for 0.3%):

$$
\Delta y = \frac{y \cdot \Delta x \cdot (1 - \gamma)}{x + \Delta x \cdot (1 - \gamma)}
$$

### 2.4 Price Impact

The effective price paid by the trader:

$$
P_{effective} = \frac{\Delta y}{\Delta x} = \frac{y}{x + \Delta x}
$$

The price impact as a percentage:

$$
\text{Price Impact} = 1 - \frac{P_{effective}}{P_{spot}} = 1 - \frac{x}{x + \Delta x} = \frac{\Delta x}{x + \Delta x}
$$

**Key insight**: Price impact depends only on the trade size relative to the reserve.
A trade of 1% of the reserve results in approximately 1% price impact.

### 2.5 Slippage

Slippage is the difference between the expected price and the actual execution price.
In a CPMM, slippage equals price impact for a single trade but can be worse if other
trades execute first (MEV sandwich attacks).

$$
\text{Slippage} = P_{expected} - P_{actual}
$$

---

## 3. Uniswap V2 Mechanics

### 3.1 Pool Creation and Initialization

When a new Uniswap V2 pool is created:

1. Creator deposits initial amounts of Token X and Token Y.
2. The initial price is set by the deposit ratio: $P_X = \frac{y_0}{x_0}$
3. LP tokens are minted: $LP_{tokens} = \sqrt{x_0 \cdot y_0}$

### 3.2 LP Token Minting (Subsequent Deposits)

For subsequent deposits, LP tokens are minted proportionally:

$$
LP_{new} = LP_{supply} \cdot \min\left(\frac{\Delta x}{x}, \frac{\Delta y}{y}\right)
$$

This ensures new LPs deposit at the current pool ratio.

### 3.3 LP Token Burning (Withdrawal)

When burning LP tokens:

$$
\Delta x_{returned} = x \cdot \frac{LP_{burned}}{LP_{supply}}
$$

$$
\Delta y_{returned} = y \cdot \frac{LP_{burned}}{LP_{supply}}
$$

### 3.4 Fee Accumulation

In Uniswap V2, fees (0.3%) are added to the pool reserves, increasing $k$:

- Before fee swap: $k_0 = x_0 \cdot y_0$
- After fee swap: $k_1 = (x_0 + \Delta x_{fee}) \cdot (y_0 - \Delta y) > k_0$

This means LP tokens represent an ever-growing share of the pool, and fees are
automatically compounded.

### 3.5 Uniswap V2 Limitations

| Limitation                  | Impact                                      |
|-----------------------------|---------------------------------------------|
| Uniform liquidity           | Capital spread across entire price range    |
| Low capital efficiency      | Most liquidity sits idle far from spot price|
| Fixed 0.3% fee              | Cannot optimize for different pair types    |
| No native oracle            | Requires TWAP calculation externally        |
| Single fee tier             | Stables overpay, volatile pairs underpay    |

---

## 4. Uniswap V3 Concentrated Liquidity

### 4.1 Core Innovation

Uniswap V3's breakthrough: LPs can concentrate their liquidity within a **specific
price range** $[p_a, p_b]$ instead of the entire $[0, \infty)$ range.

This means:
- Liquidity is only active when the current price is within the LP's range.
- Capital efficiency can be 100x-4000x higher than V2.
- LPs earn fees only when their range is active.
- Positions become non-fungible (NFTs instead of ERC-20 LP tokens).

### 4.2 Virtual Reserves Concept

In Uniswap V3, a concentrated position behaves as if it has much larger reserves
(virtual reserves) than what was actually deposited.

For a position in range $[p_a, p_b]$ with real reserves $(\Delta x, \Delta y)$:

**Virtual reserves**:

$$
x_{virtual} = \Delta x + \frac{L}{\sqrt{p_b}}
$$

$$
y_{virtual} = \Delta y + L \cdot \sqrt{p_a}
$$

These virtual reserves satisfy the constant product formula:

$$
x_{virtual} \cdot y_{virtual} = L^2
$$

Where $L$ is the **liquidity** parameter.

### 4.3 Liquidity Parameter (L)

The liquidity $L$ is the key parameter in Uniswap V3. It measures the relationship
between the change in reserves and the change in price:

$$
L = \frac{\Delta y}{\Delta \sqrt{P}}
$$

This can be derived from the constant product formula applied to virtual reserves.

### 4.4 Fee Tiers

Uniswap V3 offers multiple fee tiers:

| Fee Tier | Tick Spacing | Typical Use Case                    |
|----------|-------------|--------------------------------------|
| 0.01%    | 1           | Very stable pairs (USDC/USDT)       |
| 0.05%    | 10          | Stable pairs (DAI/USDC)             |
| 0.30%    | 60          | Standard pairs (ETH/USDC)           |
| 1.00%    | 200         | Exotic/volatile pairs               |

---

## 5. Tick System Deep Dive

### 5.1 What Is a Tick?

In Uniswap V3, the continuous price space is discretized into **ticks**. Each tick
represents a specific price point:

$$
p(i) = 1.0001^i
$$

Where $i$ is the tick index (integer). This means each tick represents a 0.01% (1 basis
point) price change.

### 5.2 Tick to Price Conversion

$$
p = 1.0001^i
$$

$$
i = \lfloor \log_{1.0001}(p) \rfloor = \left\lfloor \frac{\ln(p)}{\ln(1.0001)} \right\rfloor
$$

### 5.3 Tick Spacing

Not every tick can be used as a range boundary. **Tick spacing** determines which ticks
are usable:

- Fee tier 0.01%: tick spacing = 1 (every tick usable)
- Fee tier 0.05%: tick spacing = 10
- Fee tier 0.30%: tick spacing = 60
- Fee tier 1.00%: tick spacing = 200

Only ticks that are multiples of the tick spacing can be used as position boundaries.

### 5.4 Tick Bitmap

Uniswap V3 uses a bitmap data structure to track which ticks have liquidity transitions
(where liquidity is added or removed):

```
Tick Bitmap Structure:
- 256-bit words, each bit represents one tick
- Word index = tick / 256
- Bit position = tick % 256
- Bit = 1 means there is a liquidity transition at this tick
```

This enables efficient traversal during swaps — the contract can quickly find the next
initialized tick.

### 5.5 Tick Crossing During Swaps

When a swap crosses a tick boundary:

1. The current tick's liquidity is consumed.
2. The tick boundary is crossed.
3. Liquidity is updated: positions starting at this tick are added, positions ending
   here are removed.
4. The swap continues in the new tick range with updated total liquidity.

$$
L_{new} = L_{current} + \Delta L_{net}
$$

Where $\Delta L_{net}$ is the net liquidity change at the tick boundary.

### 5.6 Tick Math Examples

| Tick Index | Price (Token1/Token0) | Description                       |
|------------|----------------------|---------------------------------------|
| -887272    | ~0                   | Minimum usable tick                   |
| -69082     | ~0.001               | Very low price                        |
| 0          | 1.0                  | Parity                                |
| 69082      | ~1000                | High price                            |
| 887272     | ~$\infty$            | Maximum usable tick                   |

**Example**: For ETH/USDC at $3,000:

$$
i = \frac{\ln(3000)}{\ln(1.0001)} = \frac{8.0064}{0.00009999} \approx 80,071
$$

Adjusted for decimal difference (ETH has 18 decimals, USDC has 6):

$$
i_{adjusted} = \frac{\ln(3000 \times 10^{-12})}{\ln(1.0001)} \approx -197,215
$$

Note: The actual tick depends on which token is token0 vs token1 in the pool contract.

---

## 6. Concentrated Liquidity Mathematics

### 6.1 Liquidity from Token Amounts

Given a price range $[p_a, p_b]$ and current price $p_c$ where $p_a < p_c < p_b$:

**From token X (the quote token with less value at higher prices)**:

$$
L = \frac{\Delta x \cdot \sqrt{p_a} \cdot \sqrt{p_b}}{\sqrt{p_b} - \sqrt{p_a}}
$$

Wait — let us be precise. In Uniswap V3 convention:

- Token X = token0 (lower address)
- Token Y = token1 (higher address)
- Price $p = \frac{y}{x}$ = token1 per token0

**When current price $p_c$ is within range $[p_a, p_b]$**:

From token X (token0) amount:

$$
L_x = \frac{\Delta x \cdot \sqrt{p_c} \cdot \sqrt{p_b}}{\sqrt{p_b} - \sqrt{p_c}}
$$

From token Y (token1) amount:

$$
L_y = \frac{\Delta y}{\sqrt{p_c} - \sqrt{p_a}}
$$

The actual liquidity is: $L = \min(L_x, L_y)$

### 6.2 Token Amounts from Liquidity

Given liquidity $L$ and price range $[p_a, p_b]$ with current price $p_c$:

**Case 1: $p_c \leq p_a$ (price below range — position is 100% token X)**:

$$
\Delta x = L \cdot \left(\frac{1}{\sqrt{p_a}} - \frac{1}{\sqrt{p_b}}\right)
$$

$$
\Delta y = 0
$$

**Case 2: $p_a < p_c < p_b$ (price within range — position has both tokens)**:

$$
\Delta x = L \cdot \left(\frac{1}{\sqrt{p_c}} - \frac{1}{\sqrt{p_b}}\right)
$$

$$
\Delta y = L \cdot \left(\sqrt{p_c} - \sqrt{p_a}\right)
$$

**Case 3: $p_c \geq p_b$ (price above range — position is 100% token Y)**:

$$
\Delta x = 0
$$

$$
\Delta y = L \cdot \left(\sqrt{p_b} - \sqrt{p_a}\right)
$$

### 6.3 Fee Income Calculation

Fees earned by a position depend on:
- The position's share of total liquidity at the current tick.
- The volume that trades through the position's range.

$$
\text{Fees earned} = V_{through\_range} \cdot \gamma \cdot \frac{L_{position}}{L_{total\_at\_tick}}
$$

Where:
- $V_{through\_range}$ = volume that traded through this tick range
- $\gamma$ = fee rate (e.g., 0.003)
- $L_{position}$ = liquidity of this specific position
- $L_{total\_at\_tick}$ = total liquidity from all positions at current tick

### 6.4 Fee APR Estimation

$$
\text{Fee APR} = \frac{V_{daily} \cdot \gamma \cdot \frac{L_{position}}{L_{total}} \cdot 365}{\text{Position Value (USD)}}
$$

### 6.5 Position Value Calculation

The USD value of a concentrated liquidity position:

$$
V_{position} = \Delta x \cdot P_x + \Delta y \cdot P_y
$$

Where $\Delta x$ and $\Delta y$ are computed from Section 6.2 and $P_x$, $P_y$ are
current USD prices.

### 6.6 Swap Execution Within a Tick Range

When a swap occurs entirely within a single tick range (no tick crossings):

For a swap of $\Delta y$ of token Y for token X:

$$
\Delta \sqrt{P} = \frac{\Delta y}{L}
$$

$$
\sqrt{P_{new}} = \sqrt{P_{old}} + \frac{\Delta y}{L}
$$

$$
\Delta x = L \cdot \left(\frac{1}{\sqrt{P_{old}}} - \frac{1}{\sqrt{P_{new}}}\right)
$$

---

## 7. Capital Efficiency Analysis

### 7.1 Capital Efficiency Ratio

The capital efficiency of a concentrated position relative to a full-range (V2-style)
position:

$$
\text{Efficiency} = \frac{L_{concentrated}}{L_{full\_range}} = \frac{\sqrt{p_b} \cdot \sqrt{p_a}}{\sqrt{p_b} - \sqrt{p_a}} \cdot \left(\frac{1}{\sqrt{p_c}} - \frac{1}{\sqrt{p_b}} + \frac{\sqrt{p_c} - \sqrt{p_a}}{p_c}\right)^{-1}
$$

A simpler approximation for a symmetric range around current price:

$$
\text{Efficiency} \approx \frac{1}{\sqrt{r_{upper}} - \sqrt{r_{lower}}}
$$

Where $r_{upper} = p_b/p_c$ and $r_{lower} = p_a/p_c$.

### 7.2 Efficiency Examples

| Range (% around spot) | Approx. Capital Efficiency | Equivalent V2 Capital |
|-----------------------|----------------------------|----------------------|
| $\pm$0.1%             | ~4,000x                   | $4M equivalent from $1K |
| $\pm$1%               | ~400x                     | $400K equivalent from $1K |
| $\pm$5%               | ~80x                      | $80K equivalent from $1K |
| $\pm$10%              | ~40x                      | $40K equivalent from $1K |
| $\pm$25%              | ~15x                      | $15K equivalent from $1K |
| $\pm$50%              | ~8x                       | $8K equivalent from $1K |
| Full range            | 1x                        | Same as V2 |

### 7.3 The Capital Efficiency Tradeoff

Higher capital efficiency comes with:
- **Higher fee income** (per unit of capital) when price stays in range.
- **Higher impermanent loss** when price moves (amplified IL).
- **More frequent rebalancing** needed as price moves out of range.
- **Higher gas costs** from rebalancing transactions.

$$
\text{Net Return} = \text{Fee Income} \times \text{Time In Range} - \text{IL} - \text{Gas Costs}
$$

### 7.4 Optimal Range Width

The optimal range width depends on:

1. **Expected volatility** ($\sigma$): Higher volatility requires wider ranges.
2. **Fee tier**: Higher fee tiers can tolerate wider ranges (more fee income per trade).
3. **Rebalancing cost**: Higher gas costs favor wider ranges.
4. **Time horizon**: Longer horizons need wider ranges.

A heuristic for range width based on expected volatility:

$$
\text{Range Width} \approx 2 \cdot \sigma_{daily} \cdot \sqrt{T} \cdot z_{\alpha}
$$

Where:
- $\sigma_{daily}$ = expected daily volatility
- $T$ = rebalancing period (in days)
- $z_{\alpha}$ = z-score for desired probability of staying in range

**Example**: For ETH/USDC with $\sigma_{daily} = 5\%$, rebalancing every 7 days,
95% confidence:

$$
\text{Range Width} = 2 \times 0.05 \times \sqrt{7} \times 1.96 \approx 51.9\%
$$

This suggests a range of approximately $\pm 26\%$ around the current price.

---

## 8. Position Management Strategies

### 8.1 Strategy 1: Passive Wide Range

```
Configuration:
  Range: +/- 30-50% around current price
  Rebalance: Weekly or when out of range
  Fee tier: 0.30% or 1.00%
  Target: Minimal management, steady fees
```

**Pros**: Low gas costs, infrequent management.
**Cons**: Lower capital efficiency, lower APR.

$$
\text{Expected APR}_{wide} = \frac{V_{daily} \cdot \gamma}{TVL_{range}} \cdot 365 \cdot P(in\_range)
$$

### 8.2 Strategy 2: Active Tight Range

```
Configuration:
  Range: +/- 2-5% around current price
  Rebalance: Every 1-4 hours or on range exit
  Fee tier: 0.05% or 0.30%
  Target: Maximum fee capture, active management
```

**Pros**: Very high capital efficiency, high APR when in range.
**Cons**: High gas costs, frequent rebalancing, amplified IL.

### 8.3 Strategy 3: Asymmetric Range (Directional Bias)

When the trading system has a directional view:

```
Bullish on token X:
  Range lower bound: Current price - 5%
  Range upper bound: Current price + 20%
  Effect: More exposure to token X if price drops (accumulate)
          Less IL if price rises (wider upside range)

Bearish on token X:
  Range lower bound: Current price - 20%
  Range upper bound: Current price + 5%
  Effect: More exposure to token Y if price rises (accumulate Y)
          Position exits range quickly on upside (stop-loss effect)
```

### 8.4 Strategy 4: Multiple Positions (Ladder)

Deploy capital across multiple ranges:

```
Position 1: [p - 1%, p + 1%]  — 30% of capital (tight, high efficiency)
Position 2: [p - 5%, p + 5%]  — 40% of capital (medium range)
Position 3: [p - 20%, p + 20%] — 30% of capital (wide, safety net)
```

This creates a blended return profile:
- Tight position earns high fees when price is stable.
- Medium position provides coverage for moderate moves.
- Wide position ensures some fee income even during volatility.

### 8.5 Strategy 5: Volatility-Adjusted Dynamic Range

```python
def calculate_dynamic_range(current_price, volatility, fee_rate, gas_cost):
    """
    Dynamically adjust LP range based on current market conditions.
    """
    # Higher volatility -> wider range
    vol_factor = volatility / BASE_VOLATILITY

    # Higher fees -> can afford tighter range (more fee income per trade)
    fee_factor = BASE_FEE / fee_rate

    # Higher gas -> need wider range (less frequent rebalancing)
    gas_factor = gas_cost / BASE_GAS

    range_multiplier = vol_factor * fee_factor * gas_factor

    # Base range is +/- 5%
    half_range = 0.05 * range_multiplier

    lower_bound = current_price * (1 - half_range)
    upper_bound = current_price * (1 + half_range)

    return lower_bound, upper_bound
```

### 8.6 Rebalancing Decision Framework

```
REBALANCE when ANY of these conditions are met:

1. Current price exits the active range
   -> Close position, reopen centered on new price

2. Current price reaches within 10% of range boundary
   AND expected volatility suggests range exit is likely
   -> Preemptive rebalance to avoid being out-of-range

3. Accumulated fees exceed gas cost of rebalancing by 3x
   AND a tighter range would be more capital-efficient
   -> Harvest fees and tighten range

4. Volatility regime change detected
   -> Widen range if vol increasing, tighten if decreasing

5. Gas price drops below threshold
   -> Opportunistic rebalance during cheap gas
```

---

## 9. Range Order Strategies

### 9.1 What Are Range Orders?

A range order in Uniswap V3 is a single-sided liquidity position above or below
the current price. It functions like a limit order:

- **Range order above current price**: Deposit token X in range above spot.
  As price rises through the range, token X is converted to token Y.
  Effect: Like a limit sell of token X.

- **Range order below current price**: Deposit token Y in range below spot.
  As price falls through the range, token Y is converted to token X.
  Effect: Like a limit buy of token X.

### 9.2 Range Order vs. Limit Order Comparison

| Feature              | Range Order           | Traditional Limit Order |
|---------------------|-----------------------|-------------------------|
| Execution            | Gradual (across range)| Instant (at price)      |
| Fee income           | Earns fees while crossing | No fee income        |
| Reversibility        | Can reverse if price returns | Filled permanently |
| Precision            | Range width dependent | Exact price              |
| Cost                 | Gas for mint/burn     | Maker fee (often 0)     |

### 9.3 Range Order Implementation

```python
def create_range_order_sell(token_x, amount, target_price, range_width_bps):
    """
    Create a range order to sell token X at target_price.

    Parameters:
        token_x: Token to sell
        amount: Amount to sell
        target_price: Target sell price
        range_width_bps: Width of range in basis points (e.g., 50 = 0.5%)
    """
    lower_tick = price_to_tick(target_price)
    upper_tick = lower_tick + range_width_bps

    # Ensure ticks align with tick spacing
    lower_tick = round_to_tick_spacing(lower_tick, fee_tier)
    upper_tick = round_to_tick_spacing(upper_tick, fee_tier)

    # Deposit only token X (single-sided above current price)
    position = pool.mint(
        recipient=address,
        tick_lower=lower_tick,
        tick_upper=upper_tick,
        amount_token0=amount,  # If token_x is token0
        amount_token1=0
    )

    # Monitor: if price fully crosses the range, remove liquidity
    # (otherwise it will reverse back to token X if price returns)
    return position
```

### 9.4 Critical Note: Range Order Reversal Risk

A range order is NOT automatically removed when fully crossed. If the price moves
through the range and then returns, the position reverses:

```
Scenario: Sell ETH range order at $3000-$3050

1. Price at $2900 — Position: 100% ETH (waiting)
2. Price hits $3025 — Position: 50% ETH, 50% USDC (partially filled)
3. Price hits $3050 — Position: 0% ETH, 100% USDC (fully "filled")
4. *** MUST REMOVE LIQUIDITY HERE ***
5. If not removed and price drops to $2950:
   Position: 100% ETH again (order reversed!)
```

The bot MUST monitor and remove liquidity promptly after a range order is fully crossed.

---

## 10. Curve Finance StableSwap

### 10.1 The StableSwap Invariant

Curve Finance uses a hybrid invariant that combines constant sum ($x + y = D$) and
constant product ($x \cdot y = k$) behavior:

$$
A \cdot n^n \cdot \sum x_i + D = A \cdot D \cdot n^n + \frac{D^{n+1}}{n^n \cdot \prod x_i}
$$

Where:
- $x_i$ = reserve of token $i$
- $D$ = invariant (analogous to total liquidity)
- $n$ = number of tokens in the pool
- $A$ = amplification coefficient (controls curve shape)

### 10.2 Two-Token Simplified Form

For a two-token pool:

$$
A \cdot 4 \cdot (x + y) + D = 4 \cdot A \cdot D + \frac{D^3}{4 \cdot x \cdot y}
$$

### 10.3 Amplification Coefficient (A)

The parameter $A$ controls the curve's behavior:

| A Value    | Behavior                                    |
|------------|---------------------------------------------|
| $A = 0$    | Pure constant product (like Uniswap)        |
| $A \to \infty$ | Pure constant sum (zero slippage)      |
| $A = 100$  | Typical for stablecoin pools                |
| $A = 500$  | Very tight peg (e.g., USDC/USDT)           |

Higher $A$ means:
- Lower slippage near the peg (price ratio ~1:1).
- Sharper slippage increase when prices diverge from peg.
- Greater concentration of liquidity around the peg.

### 10.4 Curve Price Calculation

The marginal price in a Curve pool is computed by implicit differentiation of the
StableSwap invariant:

$$
\frac{dy}{dx} = -\frac{4A \cdot x \cdot y^2 \cdot (4Ax + 4Ay + D - 4AD)}{4A \cdot x^2 \cdot y \cdot (4Ax + 4Ay + D - 4AD) + D^3}
$$

Note: In practice, this is computed iteratively using Newton's method within the
smart contract.

### 10.5 Curve V2 (Cryptoswap)

Curve V2 extends StableSwap for non-pegged volatile assets:

- **Internal oracle**: Tracks an exponential moving average price.
- **Dynamic peg**: The "peg point" moves toward the oracle price.
- **Repegging**: The pool automatically readjusts its concentration around the
  current market price.

This makes Curve V2 competitive with Uniswap V3 for volatile pairs while maintaining
the smooth curve properties of StableSwap.

---

## 11. Balancer Weighted Pools

### 11.1 Weighted Constant Product

Balancer generalizes the constant product formula to support arbitrary token weights:

$$
\prod_{i=1}^{n} x_i^{w_i} = k
$$

Where:
- $x_i$ = reserve of token $i$
- $w_i$ = weight of token $i$ (weights sum to 1)
- $k$ = constant

### 11.2 Two-Token Weighted Pool

For a two-token pool with weights $w_x$ and $w_y$:

$$
x^{w_x} \cdot y^{w_y} = k
$$

The spot price:

$$
P_x = \frac{y / w_y}{x / w_x} = \frac{y \cdot w_x}{x \cdot w_y}
$$

### 11.3 Swap Output in Weighted Pool

For swapping $\Delta x$ of token X for token Y:

$$
\Delta y = y \cdot \left(1 - \left(\frac{x}{x + \Delta x \cdot (1-\gamma)}\right)^{w_x/w_y}\right)
$$

Where $\gamma$ is the swap fee.

### 11.4 Why Weighted Pools Matter

| Weight Configuration | Use Case                                    |
|---------------------|---------------------------------------------|
| 50/50               | Standard pair (equivalent to Uniswap V2)    |
| 80/20               | Maintain 80% exposure to one asset          |
| 60/20/20            | Diversified pool with primary asset         |
| Equal weights (n tokens) | Index-like exposure to multiple assets |

**Key advantage**: An 80/20 ETH/USDC pool gives 80% ETH exposure, meaning less
impermanent loss when ETH price changes compared to a 50/50 pool. The tradeoff
is lower fee income per unit of capital.

### 11.5 Impermanent Loss in Weighted Pools

For a two-token weighted pool:

$$
IL = \frac{r^{w_x}}{w_x \cdot r + w_y} - 1
$$

Where $r = P_{new}/P_{old}$ (price ratio change).

For an 80/20 pool, IL is significantly lower than 50/50:

| Price Change | 50/50 IL  | 80/20 IL  |
|-------------|-----------|-----------|
| 1.25x       | -0.60%    | -0.15%    |
| 1.50x       | -2.02%    | -0.52%    |
| 2.00x       | -5.72%    | -1.52%    |
| 3.00x       | -13.40%   | -3.68%    |
| 0.50x       | -5.72%    | -1.52%    |

---

## 12. Just-in-Time (JIT) Liquidity

### 12.1 What Is JIT Liquidity?

Just-in-Time liquidity is a MEV strategy where a bot:

1. Observes a large pending swap in the mempool.
2. Adds concentrated liquidity in a very tight range around the current price
   **just before** the swap executes (in the same block, earlier position).
3. The swap executes, paying fees to the JIT liquidity.
4. Removes the liquidity **immediately after** the swap (same block, later position).

### 12.2 JIT Profitability

$$
\text{Profit}_{JIT} = V_{swap} \cdot \gamma \cdot \frac{L_{JIT}}{L_{existing} + L_{JIT}} - 2 \cdot \text{Gas}_{mint+burn}
$$

For JIT to be profitable:

$$
V_{swap} > \frac{2 \cdot \text{Gas}_{mint+burn} \cdot (L_{existing} + L_{JIT})}{\gamma \cdot L_{JIT}}
$$

### 12.3 JIT Impact on Regular LPs

JIT liquidity is controversial because it extracts fees from regular LPs:

- **Before JIT**: Regular LP earns 100% of fees from the swap.
- **After JIT**: Regular LP earns only $\frac{L_{regular}}{L_{regular} + L_{JIT}}$
  of fees from that swap.

The JIT provider bears zero impermanent loss (position exists for only one block).

### 12.4 Defense Against JIT

For the trading system as an LP:

1. **Wider ranges**: JIT is most effective against tight-range LPs.
2. **Private mempool submission**: Submit LP transactions via Flashbots to avoid
   being JIT'ed.
3. **Accept it**: Factor JIT dilution into yield expectations.

---

## 13. Optimal Liquidity Provision Strategies

### 13.1 Objective Function

The optimal LP strategy maximizes:

$$
\max_{\{p_a, p_b, \text{rebalance\_frequency}\}} \mathbb{E}\left[\text{Fees} - \text{IL} - \text{Gas} - \text{Opportunity Cost}\right]
$$

Subject to:
- Capital constraints: $\text{Position Value} \leq \text{Allocation Budget}$
- Risk constraints: $\text{Expected IL} \leq \text{IL Tolerance}$
- Gas constraints: $\text{Gas Cost} \leq \alpha \cdot \text{Expected Fees}$

### 13.2 Fee Income Model

Expected fee income over period $T$:

$$
\mathbb{E}[\text{Fees}] = \int_0^T V(t) \cdot \gamma \cdot \frac{L}{L_{total}(t)} \cdot \mathbf{1}_{p(t) \in [p_a, p_b]} \, dt
$$

Where:
- $V(t)$ = trading volume at time $t$
- $\gamma$ = fee rate
- $L$ = position liquidity
- $L_{total}(t)$ = total liquidity at current tick at time $t$
- $\mathbf{1}_{p(t) \in [p_a, p_b]}$ = indicator that price is in range

### 13.3 Time-in-Range Estimation

Assuming price follows a geometric Brownian motion:

$$
P(t) = P(0) \cdot e^{(\mu - \sigma^2/2)t + \sigma W(t)}
$$

The probability of being in range $[p_a, p_b]$ at time $t$:

$$
P(p(t) \in [p_a, p_b]) = \Phi\left(\frac{\ln(p_b/P_0) - (\mu - \sigma^2/2)t}{\sigma\sqrt{t}}\right) - \Phi\left(\frac{\ln(p_a/P_0) - (\mu - \sigma^2/2)t}{\sigma\sqrt{t}}\right)
$$

Where $\Phi$ is the standard normal CDF.

### 13.4 Optimal Range Given Volatility

For a zero-drift ($\mu = 0$) asset, the expected time in range for a symmetric
range $[P_0/r, P_0 \cdot r]$:

$$
\mathbb{E}[\text{Time in Range}] \propto \frac{\ln(r)}{\sigma}
$$

And the fee income scales inversely with range width (tighter = more efficient):

$$
\text{Fee Intensity} \propto \frac{1}{\sqrt{r} - 1/\sqrt{r}}
$$

The optimal $r$ balances these two effects. Numerically, this often yields:

$$
r^* \approx e^{c \cdot \sigma \cdot \sqrt{T}}
$$

Where $c \approx 1.5-2.0$ depending on the fee tier and rebalancing frequency.

### 13.5 Multi-Pool Strategy

The trading system can deploy liquidity across multiple pools simultaneously:

$$
\max_{\{w_j\}} \sum_j w_j \cdot \text{Expected Net Return}_j
$$

Subject to:
- $\sum_j w_j = 1$ (fully invested)
- $w_j \geq 0$ (no negative positions)
- $\text{Risk}_j \leq \text{threshold}_j$ for all $j$

This is a portfolio optimization problem solvable via convex optimization.

---

## 14. Complete Mathematical Framework

### 14.1 Summary of Core Equations

**Constant Product (Uniswap V2)**:

$$
x \cdot y = k
$$

$$
\Delta y = \frac{y \cdot \Delta x \cdot (1 - \gamma)}{x + \Delta x \cdot (1-\gamma)}
$$

**Concentrated Liquidity (Uniswap V3)**:

$$
L = \frac{\Delta x \cdot \sqrt{p_c} \cdot \sqrt{p_b}}{\sqrt{p_b} - \sqrt{p_c}}
$$

$$
L = \frac{\Delta y}{\sqrt{p_c} - \sqrt{p_a}}
$$

$$
\Delta x = L \cdot \left(\frac{1}{\sqrt{p_c}} - \frac{1}{\sqrt{p_b}}\right) \quad \text{(when } p_a < p_c < p_b\text{)}
$$

$$
\Delta y = L \cdot \left(\sqrt{p_c} - \sqrt{p_a}\right) \quad \text{(when } p_a < p_c < p_b\text{)}
$$

**Tick Pricing**:

$$
p(i) = 1.0001^i
$$

$$
i = \left\lfloor \frac{\ln(p)}{\ln(1.0001)} \right\rfloor
$$

**Capital Efficiency** (symmetric range $\pm r$ around spot):

$$
\text{Efficiency} \approx \frac{1}{\sqrt{1+r} - \sqrt{1-r}} \cdot \frac{2}{\sqrt{1+r} + \sqrt{1-r}}
$$

**StableSwap (Curve)**:

$$
An^n \sum x_i + D = ADn^n + \frac{D^{n+1}}{n^n \prod x_i}
$$

**Weighted Pool (Balancer)**:

$$
\prod x_i^{w_i} = k
$$

$$
\Delta y = y \cdot \left(1 - \left(\frac{x}{x + \Delta x(1-\gamma)}\right)^{w_x/w_y}\right)
$$

### 14.2 Price Impact Comparison Across AMMs

For a swap of size $s$ (as fraction of pool reserves):

| AMM Type        | Price Impact (approx.)           |
|-----------------|----------------------------------|
| Constant Product| $\frac{s}{1+s} \approx s$       |
| Concentrated    | $\frac{s}{1+s} \cdot \frac{1}{E}$ (E = efficiency) |
| StableSwap      | $\frac{s}{A \cdot n^n + s}$ (near peg) |
| Weighted (w1/w2)| $1 - (1-s)^{w_1/w_2}$           |

### 14.3 Fee-Adjusted Returns

For any AMM, the LP's net return over period $T$:

$$
R_{net} = \frac{V_{final} + F_{accumulated} - V_{initial}}{V_{initial}}
$$

Where:
- $V_{final}$ = value of LP position at time $T$
- $F_{accumulated}$ = accumulated trading fees
- $V_{initial}$ = initial deposit value

Decomposed:

$$
R_{net} = R_{fees} + R_{IL} + R_{price}
$$

Where:
- $R_{fees}$ = return from fee income
- $R_{IL}$ = impermanent loss (negative)
- $R_{price}$ = return from asset price changes (same as holding)

---

## 15. Execution Flow — LP Management Bot

### 15.1 Main LP Bot Architecture

```python
class LPManagementBot:
    """
    Manages concentrated liquidity positions across Uniswap V3 pools.
    Handles position creation, monitoring, rebalancing, and exit.
    """

    def __init__(self, config: LPBotConfig):
        self.web3 = Web3Provider(config.rpc_url)
        self.position_manager = UniswapV3PositionManager(config.chain)
        self.oracle = PriceOracle(config.oracle_config)
        self.volatility_model = VolatilityEstimator()
        self.gas_estimator = GasEstimator()
        self.risk_manager = RiskManager(config.risk_params)
        self.positions: Dict[int, LPPosition] = {}

    # =========================================================
    # PHASE 1: OPPORTUNITY IDENTIFICATION
    # =========================================================

    async def scan_for_opportunities(self) -> List[LPOpportunity]:
        """Scan all monitored pools for LP opportunities."""
        opportunities = []

        for pool in self.monitored_pools:
            # Get current pool state
            state = await self.get_pool_state(pool)

            # Estimate expected fee APR
            volume_24h = await self.get_volume(pool, period="24h")
            fee_apr = self.estimate_fee_apr(
                volume=volume_24h,
                fee_rate=pool.fee_rate,
                tvl=state.tvl
            )

            # Estimate volatility
            volatility = await self.volatility_model.estimate(
                pool.token0, pool.token1, lookback_days=30
            )

            # Calculate optimal range
            optimal_range = self.calculate_optimal_range(
                current_price=state.current_price,
                volatility=volatility,
                fee_rate=pool.fee_rate,
                rebalance_frequency=self.config.rebalance_interval
            )

            # Estimate net APR after IL and gas
            il_estimate = self.estimate_il(volatility, optimal_range)
            gas_estimate = self.estimate_rebalance_gas(pool)
            net_apr = fee_apr + il_estimate - gas_estimate

            if net_apr > self.config.min_net_apr:
                opportunities.append(LPOpportunity(
                    pool=pool,
                    range=optimal_range,
                    expected_fee_apr=fee_apr,
                    expected_il=il_estimate,
                    expected_net_apr=net_apr,
                    confidence=self.calculate_confidence(state, volatility)
                ))

        return sorted(opportunities, key=lambda o: o.expected_net_apr, reverse=True)

    # =========================================================
    # PHASE 2: POSITION CREATION
    # =========================================================

    async def create_position(self, opportunity: LPOpportunity) -> Optional[int]:
        """Create a new concentrated liquidity position."""

        # Step 1: Risk check
        if not self.risk_manager.approve_new_position(opportunity):
            logger.warning(f"Risk check failed for {opportunity}")
            return None

        # Step 2: Calculate token amounts
        pool = opportunity.pool
        range_lower = opportunity.range.lower
        range_upper = opportunity.range.upper
        allocation = self.risk_manager.calculate_allocation(opportunity)

        token0_amount, token1_amount = self.calculate_deposit_amounts(
            current_price=pool.current_price,
            range_lower=range_lower,
            range_upper=range_upper,
            total_value_usd=allocation
        )

        # Step 3: Approve tokens
        await self.approve_tokens(pool.token0, token0_amount)
        await self.approve_tokens(pool.token1, token1_amount)

        # Step 4: Mint position
        tick_lower = self.price_to_tick(range_lower, pool.tick_spacing)
        tick_upper = self.price_to_tick(range_upper, pool.tick_spacing)

        tx = await self.position_manager.mint(
            token0=pool.token0,
            token1=pool.token1,
            fee=pool.fee_tier,
            tick_lower=tick_lower,
            tick_upper=tick_upper,
            amount0_desired=token0_amount,
            amount1_desired=token1_amount,
            amount0_min=token0_amount * (1 - self.config.slippage_tolerance),
            amount1_min=token1_amount * (1 - self.config.slippage_tolerance),
            deadline=int(time.time()) + 300
        )

        # Step 5: Record position
        receipt = await self.web3.wait_for_receipt(tx)
        token_id = self.extract_token_id(receipt)

        self.positions[token_id] = LPPosition(
            token_id=token_id,
            pool=pool,
            tick_lower=tick_lower,
            tick_upper=tick_upper,
            liquidity=self.extract_liquidity(receipt),
            entry_price=pool.current_price,
            entry_time=time.time(),
            entry_tvl=pool.tvl
        )

        logger.info(f"Created position {token_id} in {pool.name} "
                    f"range [{range_lower:.4f}, {range_upper:.4f}]")
        return token_id

    # =========================================================
    # PHASE 3: POSITION MONITORING
    # =========================================================

    async def monitor_positions(self):
        """Continuous monitoring loop for all active positions."""
        while True:
            for token_id, position in list(self.positions.items()):
                try:
                    state = await self.get_pool_state(position.pool)
                    current_price = state.current_price
                    current_tick = state.current_tick

                    # Check 1: Is position in range?
                    in_range = position.tick_lower <= current_tick <= position.tick_upper
                    if not in_range:
                        logger.warning(f"Position {token_id} OUT OF RANGE")
                        await self.handle_out_of_range(token_id, position, state)
                        continue

                    # Check 2: Distance to range boundary
                    distance_lower = (current_tick - position.tick_lower) / \
                                    (position.tick_upper - position.tick_lower)
                    distance_upper = (position.tick_upper - current_tick) / \
                                    (position.tick_upper - position.tick_lower)

                    if min(distance_lower, distance_upper) < 0.10:
                        logger.info(f"Position {token_id} near boundary "
                                   f"({min(distance_lower, distance_upper):.1%})")
                        await self.consider_preemptive_rebalance(
                            token_id, position, state
                        )

                    # Check 3: IL check
                    il = self.calculate_current_il(position, current_price)
                    if il < self.config.max_il_threshold:
                        logger.warning(f"Position {token_id} IL={il:.2%} "
                                      f"exceeds threshold")
                        await self.handle_il_breach(token_id, position, state)

                    # Check 4: TVL monitoring
                    if state.tvl < position.entry_tvl * 0.75:
                        logger.warning(f"Pool TVL dropped significantly for "
                                      f"position {token_id}")
                        await self.handle_tvl_drop(token_id, position, state)

                    # Check 5: Unclaimed fees
                    fees = await self.get_unclaimed_fees(token_id)
                    if self.should_collect_fees(fees, position):
                        await self.collect_fees(token_id)

                except Exception as e:
                    logger.error(f"Error monitoring position {token_id}: {e}")

            await asyncio.sleep(self.config.monitor_interval)

    # =========================================================
    # PHASE 4: REBALANCING
    # =========================================================

    async def rebalance_position(self, token_id: int, new_range: PriceRange):
        """
        Rebalance a position to a new range.
        Steps: Collect fees -> Remove liquidity -> Swap to correct ratio -> Mint new
        """
        position = self.positions[token_id]

        # Step 1: Collect accumulated fees
        fees = await self.collect_fees(token_id)

        # Step 2: Remove all liquidity
        removed = await self.position_manager.decrease_liquidity(
            token_id=token_id,
            liquidity=position.liquidity,
            amount0_min=0,  # Accept any amount (will get current ratio)
            amount1_min=0,
            deadline=int(time.time()) + 300
        )

        # Step 3: Collect the removed tokens
        collected = await self.position_manager.collect(
            token_id=token_id,
            amount0_max=MAX_UINT128,
            amount1_max=MAX_UINT128
        )

        total_token0 = collected.amount0 + fees.amount0
        total_token1 = collected.amount1 + fees.amount1

        # Step 4: Calculate required ratio for new range
        current_price = await self.get_current_price(position.pool)
        required_ratio = self.calculate_deposit_ratio(
            current_price, new_range.lower, new_range.upper
        )

        # Step 5: Swap to correct ratio
        current_ratio = total_token0 * current_price / total_token1
        if abs(current_ratio - required_ratio) > 0.01:
            await self.swap_to_ratio(
                position.pool, total_token0, total_token1, required_ratio
            )

        # Step 6: Create new position
        del self.positions[token_id]
        new_token_id = await self.create_position(LPOpportunity(
            pool=position.pool,
            range=new_range
        ))

        logger.info(f"Rebalanced {token_id} -> {new_token_id} "
                    f"to range [{new_range.lower:.4f}, {new_range.upper:.4f}]")

    # =========================================================
    # PHASE 5: EXIT
    # =========================================================

    async def exit_position(self, token_id: int, reason: str):
        """Fully exit a position and return assets."""
        position = self.positions[token_id]

        # Collect fees first
        await self.collect_fees(token_id)

        # Remove all liquidity
        await self.position_manager.decrease_liquidity(
            token_id=token_id,
            liquidity=position.liquidity,
            amount0_min=0,
            amount1_min=0,
            deadline=int(time.time()) + 300
        )

        # Collect all tokens
        collected = await self.position_manager.collect(
            token_id=token_id,
            amount0_max=MAX_UINT128,
            amount1_max=MAX_UINT128
        )

        # Calculate P&L
        exit_value = (collected.amount0 * self.get_price(position.pool.token0) +
                     collected.amount1 * self.get_price(position.pool.token1))
        pnl = exit_value - position.entry_value

        logger.info(f"Exited position {token_id}. Reason: {reason}. "
                    f"P&L: ${pnl:,.2f}")

        del self.positions[token_id]
        return collected

    # =========================================================
    # HELPER FUNCTIONS
    # =========================================================

    def calculate_optimal_range(self, current_price, volatility,
                                fee_rate, rebalance_frequency):
        """Calculate optimal LP range based on market conditions."""
        # Use volatility-based range sizing
        # Range should cover expected price movement between rebalances
        # with a confidence margin

        days_between_rebalance = rebalance_frequency / 86400  # convert sec to days
        expected_move = volatility * math.sqrt(days_between_rebalance)

        # Apply confidence multiplier (1.5-2.0x expected move)
        confidence_mult = 1.8
        half_range = expected_move * confidence_mult

        # Adjust for fee tier: higher fees can support tighter ranges
        fee_adjustment = math.sqrt(fee_rate / 0.003)  # normalize to 0.3%
        half_range *= fee_adjustment

        # Apply bounds
        half_range = max(0.01, min(half_range, 0.50))  # 1% to 50%

        return PriceRange(
            lower=current_price * (1 - half_range),
            upper=current_price * (1 + half_range)
        )

    def price_to_tick(self, price, tick_spacing):
        """Convert price to nearest valid tick."""
        raw_tick = math.floor(math.log(price) / math.log(1.0001))
        # Round to tick spacing
        return round(raw_tick / tick_spacing) * tick_spacing

    def calculate_deposit_amounts(self, current_price, range_lower,
                                   range_upper, total_value_usd):
        """
        Calculate token0 and token1 amounts for deposit
        given total USD value and range.
        """
        sqrt_p = math.sqrt(current_price)
        sqrt_pa = math.sqrt(range_lower)
        sqrt_pb = math.sqrt(range_upper)

        # Ratio of token0 value to total value
        if current_price <= range_lower:
            # 100% token0
            token0_value_ratio = 1.0
        elif current_price >= range_upper:
            # 100% token1
            token0_value_ratio = 0.0
        else:
            # Both tokens
            # token0 amount per unit of L: 1/sqrt(p) - 1/sqrt(pb)
            # token1 amount per unit of L: sqrt(p) - sqrt(pa)
            dx_per_L = 1/sqrt_p - 1/sqrt_pb
            dy_per_L = sqrt_p - sqrt_pa

            token0_value = dx_per_L * current_price  # value in USD
            token1_value = dy_per_L  # already in token1 (if token1 = USD)
            total = token0_value + token1_value

            token0_value_ratio = token0_value / total

        token0_usd = total_value_usd * token0_value_ratio
        token1_usd = total_value_usd * (1 - token0_value_ratio)

        token0_amount = token0_usd / current_price  # in token0 units
        token1_amount = token1_usd  # in token1 units (assuming USD-denominated)

        return token0_amount, token1_amount
```

### 15.2 Gas-Optimized Rebalancing

```python
class GasOptimizedRebalancer:
    """
    Optimizes rebalancing decisions based on gas costs.
    Only rebalances when the expected benefit exceeds gas cost.
    """

    def should_rebalance(self, position, current_state) -> bool:
        """Determine if rebalancing is worthwhile."""

        # Calculate expected benefit of rebalancing
        current_fee_rate = self.estimate_current_fee_rate(position, current_state)
        optimal_range = self.calculate_optimal_range(current_state)
        new_fee_rate = self.estimate_fee_rate_for_range(optimal_range, current_state)

        benefit_per_day = (new_fee_rate - current_fee_rate) * position.value
        expected_days_until_next_rebalance = self.estimate_time_in_range(
            optimal_range, current_state.volatility
        )
        total_benefit = benefit_per_day * expected_days_until_next_rebalance

        # Calculate gas cost
        gas_cost = self.estimate_rebalance_gas_cost()

        # Require 3x gas cost to compensate for uncertainty
        return total_benefit > gas_cost * 3

    def estimate_rebalance_gas_cost(self) -> float:
        """Estimate total gas cost for a rebalance operation."""
        # Typical gas usage:
        # - Collect fees: ~120,000 gas
        # - Decrease liquidity: ~150,000 gas
        # - Collect tokens: ~120,000 gas
        # - Swap (if needed): ~150,000 gas
        # - Approve (if needed): ~50,000 gas
        # - Mint new position: ~400,000 gas
        # Total: ~990,000 gas

        total_gas = 990_000
        gas_price_gwei = self.gas_estimator.get_fast_gas_price()
        eth_price = self.oracle.get_eth_price()

        cost_usd = total_gas * gas_price_gwei * 1e-9 * eth_price
        return cost_usd
```

---

## 16. Risk Parameters

### 16.1 LP Position Risk Limits

| Parameter                      | Value    | Rationale                          |
|-------------------------------|----------|------------------------------------|
| Max single position size       | 5% of AUM | Diversification                  |
| Max single pool allocation     | 10% of AUM | Pool-level risk limit           |
| Max IL per position            | -5%      | Exit trigger for IL               |
| Min time in range (target)     | 70%      | Range should be active >70% of time |
| Max rebalance frequency        | 1/hour   | Limit gas expenditure             |
| Min net APR (after costs)      | 5%       | Floor for position entry          |
| Max fee tier for stables       | 0.05%    | Stables should use low fee tiers  |
| Min fee tier for volatile pairs| 0.30%    | Volatile pairs need higher fees   |
| Slippage tolerance             | 0.5%     | Max acceptable slippage on rebalance |
| Gas budget (% of fees)         | 15%      | Cap gas costs relative to income  |

### 16.2 Pool Selection Criteria

```
POOL MUST MEET ALL CRITERIA:

[x] Pool TVL > $10M
[x] 24h volume > $1M
[x] Volume/TVL ratio > 0.10 (ensures sufficient fee generation)
[x] Both tokens have reliable oracle feeds
[x] Pool has been active for > 30 days
[x] No governance proposals to change pool parameters pending
[x] Fee tier appropriate for pair type
[x] No evidence of consistent JIT liquidity domination (>50% of fees)
```

### 16.3 Emergency Procedures

| Trigger                           | Action                              |
|----------------------------------|-------------------------------------|
| Pool TVL drops >30% in 1 hour   | Immediately exit all positions      |
| Smart contract pause event       | Immediately exit (if possible)      |
| Oracle deviation >3%            | Pause new entries, monitor exits    |
| Gas price >500 gwei sustained   | Pause rebalancing, widen ranges     |
| IL exceeds -8% on any position  | Force exit regardless of gas cost   |
| Protocol governance attack       | Emergency exit all positions        |

---

## 17. References

### Protocol Whitepapers

1. Adams, H., Zinsmeister, N., Robinson, D. (2020). "Uniswap v2 Core."
   https://uniswap.org/whitepaper.pdf

2. Adams, H., Zinsmeister, N., Salem, M., Keefer, R., Robinson, D. (2021).
   "Uniswap v3 Core." https://uniswap.org/whitepaper-v3.pdf

3. Adams, H. et al. (2024). "Uniswap v4 Core."
   https://github.com/Uniswap/v4-core

4. Egorov, M. (2019). "StableSwap — Efficient Mechanism for Stablecoin Liquidity."
   Curve Finance.

5. Egorov, M. (2021). "Automatic Market-Making with Dynamic Peg."
   Curve Finance (Crypto Pools).

6. Martinelli, F., Mushegian, N. (2019). "A Non-Custodial Portfolio Manager,
   Liquidity Provider, and Price Sensor." Balancer.

### Academic Papers

7. Angeris, G., Chitra, T. (2020). "Improved Price Oracles: Constant Function
   Market Makers." ACM Advances in Financial Technologies.

8. Angeris, G., Kao, H.T., Chiang, R., Noyes, C., Chitra, T. (2019). "An Analysis
   of Uniswap Markets." Cryptoeconomic Systems.

9. Loesch, S., Hindman, N., Richardson, M.B., Welch, N. (2021). "Impermanent Loss
   in Uniswap v3." arXiv:2111.09192.

10. Fan, B., Hartz, D., Leung, K.S. (2022). "Optimal Liquidity Provision in
    Uniswap v3." Working paper.

### Technical Documentation

11. Uniswap V3 Development Book. https://uniswapv3book.com/
12. Uniswap V3 SDK Documentation. https://docs.uniswap.org/sdk/v3/overview
13. Curve Finance Technical Docs. https://resources.curve.fi/
14. Balancer V2 Documentation. https://docs.balancer.fi/

---

> **Next Document**: [02_impermanent_loss.md](./02_impermanent_loss.md)
> — Complete impermanent loss analysis with derivation, hedging, and algorithmic management.
