# Yield Farming & Aggregator Strategies

> **Axis 2 — Financial Products | Module 02 — DeFi Mechanics | Document 03**
> Version: 2.0.0 | Last Updated: 2026-04-12
> Classification: KNOWLEDGE BASE — MULTI-AGENT AI TRADING SYSTEM

---

## Table of Contents

1. [Introduction to Yield Farming](#1-introduction-to-yield-farming)
2. [Yield Farming Mechanics](#2-yield-farming-mechanics)
3. [Liquidity Mining Analysis](#3-liquidity-mining-analysis)
4. [Auto-Compounding Mathematics](#4-auto-compounding-mathematics)
5. [Yield Aggregator Strategies](#5-yield-aggregator-strategies)
6. [Leveraged Yield Farming](#6-leveraged-yield-farming)
7. [Real Yield vs Inflationary Yield](#7-real-yield-vs-inflationary-yield)
8. [Risk-Adjusted Yield Comparison](#8-risk-adjusted-yield-comparison)
9. [Optimal Harvest Frequency](#9-optimal-harvest-frequency)
10. [Gas Cost Optimization](#10-gas-cost-optimization)
11. [Multi-Protocol Yield Optimization](#11-multi-protocol-yield-optimization)
12. [Strategy Rotation Algorithm](#12-strategy-rotation-algorithm)
13. [Complete Execution Flow](#13-complete-execution-flow)
14. [Risk Parameters](#14-risk-parameters)
15. [References](#15-references)

---

## 1. Introduction to Yield Farming

### 1.1 Definition

Yield farming is the practice of deploying crypto assets across DeFi protocols to
maximize returns. It encompasses:

- **Providing liquidity** to AMMs (earning trading fees + token rewards).
- **Lending** assets to protocols (earning interest).
- **Staking** in protocol-specific mechanisms (earning protocol revenue or inflation).
- **Participating in incentive programs** (earning governance tokens).

### 1.2 Yield Sources Taxonomy

```
Yield Sources in DeFi
├── Organic Yield (sustainable, from real economic activity)
│   ├── Trading fees (DEX LP)
│   ├── Borrowing interest (lending protocols)
│   ├── Protocol revenue sharing (dividends)
│   ├── MEV capture (protocol-level)
│   └── Validator/staking rewards (consensus)
│
├── Inflationary Yield (token emissions, dilutive)
│   ├── Liquidity mining rewards
│   ├── Governance token distribution
│   ├── Incentive programs
│   └── Ecosystem grants
│
└── Synthetic Yield (derived from financial engineering)
    ├── Points/airdrop farming (speculative)
    ├── Leverage loops (recursive lending)
    ├── Yield tokenization (Pendle)
    └── Options premium (covered calls)
```

### 1.3 Why Yield Farming Matters for the Trading System

The trading system uses yield farming to:

1. **Generate base returns** on idle capital (instead of holding unproductive assets).
2. **Compound earnings** by auto-reinvesting rewards.
3. **Diversify income** across multiple uncorrelated yield sources.
4. **Fund operations** through yield (gas costs, infrastructure).
5. **Offset risks** of other strategies (arbitrage, liquidation) with steady yield.

---

## 2. Yield Farming Mechanics

### 2.1 Basic Yield Farming Flow

```
Step 1: Acquire base assets (e.g., ETH + USDC)
Step 2: Deposit into protocol (e.g., Uniswap LP, Aave lending)
Step 3: Receive receipt token (LP token, aToken, etc.)
Step 4: Stake receipt token in reward contract (if applicable)
Step 5: Accumulate rewards over time
Step 6: Harvest rewards periodically
Step 7: Sell/reinvest rewards (compounding)
Step 8: Monitor position health and yields
Step 9: Exit when yield drops below threshold or risk materializes
```

### 2.2 Receipt Token Economics

When depositing into a protocol, you receive a receipt token that represents your share:

| Protocol    | Receipt Token | Mechanism                          |
|-------------|---------------|-------------------------------------|
| Uniswap V2  | LP tokens     | Proportional share of pool         |
| Uniswap V3  | NFT (ERC-721) | Unique position with range         |
| Aave        | aTokens       | 1:1 rebasing (balance increases)   |
| Compound    | cTokens       | Exchange rate increases over time   |
| Lido        | stETH         | 1:1 rebasing with staking rewards  |
| Yearn       | yTokens       | Exchange rate increases             |
| Curve       | LP tokens     | Proportional share + CRV staking   |

### 2.3 Reward Distribution Mechanisms

#### 2.3.1 Per-Block Emission

```
Rewards per block = Total emission rate / Total staked
User reward = (User stake / Total staked) * Rewards per block * Blocks elapsed
```

Mathematical formulation:

$$
R_{user}(t_1, t_2) = S_{user} \cdot \int_{t_1}^{t_2} \frac{E(t)}{S_{total}(t)} \, dt
$$

Where:
- $R_{user}$ = total rewards for user between $t_1$ and $t_2$
- $S_{user}$ = user's staked amount
- $E(t)$ = emission rate at time $t$
- $S_{total}(t)$ = total staked at time $t$

#### 2.3.2 Accumulator Pattern (Compound/Synthetix Style)

Instead of computing integral, use a running accumulator:

$$
\text{rewardPerToken} = \text{rewardPerToken}_{prev} + \frac{\Delta t \cdot E}{\text{totalStaked}}
$$

$$
\text{earned}_{user} = \text{balance}_{user} \cdot (\text{rewardPerToken} - \text{userRewardPerTokenPaid}_{user})
$$

This is the standard MasterChef / StakingRewards pattern used in most DeFi protocols.

### 2.4 Yield Calculation

**APR (Annual Percentage Rate)** — simple interest:

$$
APR = \frac{\text{Reward Value per Year}}{\text{Staked Value}} = \frac{E_{annual} \cdot P_{reward}}{TVL}
$$

**APY (Annual Percentage Yield)** — compound interest:

$$
APY = \left(1 + \frac{APR}{n}\right)^n - 1
$$

Where $n$ = number of compounding periods per year.

---

## 3. Liquidity Mining Analysis

### 3.1 Economics of Liquidity Mining

Liquidity mining is a token distribution mechanism where protocols distribute their
governance tokens to users who provide liquidity or use the protocol.

**Protocol perspective**:
- Cost: Token dilution (printing new tokens).
- Benefit: Bootstrap liquidity, attract users, decentralize governance.
- Risk: Mercenary capital (leaves when rewards end).

**Farmer perspective**:
- Income: Token rewards.
- Risk: Token price decline, smart contract risk, IL.
- Strategy: Farm and sell, farm and hold, or farm and vote-lock.

### 3.2 Token Emission Schedule Analysis

Most protocols follow a decaying emission schedule:

$$
E(t) = E_0 \cdot \alpha^t
$$

Where:
- $E_0$ = initial emission rate
- $\alpha$ = decay factor (typically 0.5 per year for halving)
- $t$ = time in years

Or a fixed total with linear/cliff distribution:

$$
E(t) = \begin{cases}
E_{rate} & \text{if } t < T_{end} \\
0 & \text{if } t \geq T_{end}
\end{cases}
$$

### 3.3 Farm Yield Projection

To determine if entering a farm is worthwhile:

$$
\text{Net Yield} = \underbrace{\frac{E \cdot P_{token}}{TVL}}_{\text{Farm APR}} - \underbrace{IL}_{\text{if LP}} - \underbrace{\frac{Gas}{V_{position}}}_{\text{Gas cost}} - \underbrace{\text{Token Price Decline}}_{\text{Sell pressure}}
$$

### 3.4 Token Price Impact of Farming

When farmers harvest and sell reward tokens:

$$
\text{Daily Sell Pressure} = E_{daily} \cdot \text{Sell\%} \cdot P_{token}
$$

$$
\text{Price Impact} = \frac{\text{Daily Sell Pressure}}{\text{Market Liquidity}}
$$

If sell pressure exceeds organic demand, the token price declines, reducing the
effective APR — creating a negative feedback loop.

### 3.5 Optimal Farm Entry Timing

```
ENTER farm when:
1. Yield is above market rate (risk-adjusted)
2. Token emission schedule has not peaked
3. TVL growth rate is decelerating (yield stabilizing)
4. Token price has support (not in freefall)
5. Gas costs are reasonable relative to position size

EXIT farm when:
1. Yield drops below opportunity cost
2. Token emission declining significantly
3. TVL spike (yield dilution)
4. Token price breaking key support levels
5. Protocol risk event (governance, exploit)
6. Better opportunity elsewhere
```

---

## 4. Auto-Compounding Mathematics

### 4.1 The Compounding Formula

The fundamental relationship between APR and APY:

$$
APY = \left(1 + \frac{APR}{n}\right)^n - 1
$$

Where $n$ = number of compounding periods per year.

For continuous compounding ($n \to \infty$):

$$
APY_{continuous} = e^{APR} - 1
$$

### 4.2 Compounding Frequency Impact

| APR   | Daily (n=365) | Weekly (n=52) | Monthly (n=12) | Continuous |
|-------|---------------|---------------|----------------|------------|
| 10%   | 10.52%        | 10.51%        | 10.47%         | 10.52%     |
| 25%   | 28.39%        | 28.33%        | 28.07%         | 28.40%     |
| 50%   | 64.87%        | 64.58%        | 63.21%         | 64.87%     |
| 100%  | 171.46%       | 169.26%       | 161.30%        | 171.83%    |
| 200%  | 624.54%       | 601.43%       | 536.51%        | 638.91%    |
| 500%  | 13,780%       | 11,541%       | 7,872%         | 14,741%    |

**Key insight**: At low APR (<20%), compounding frequency matters little. At high APR
(>100%), frequent compounding dramatically increases returns.

### 4.3 Real-World Compounding

In practice, compounding involves:

1. **Claiming** reward tokens from the staking contract.
2. **Selling** reward tokens for base assets (optional, or add as LP).
3. **Depositing** additional base assets back into the position.

Each step incurs gas costs, so optimal compounding frequency is NOT "as often as
possible" — it depends on position size and gas costs.

### 4.4 Compounding with Gas Costs

Net APY considering gas costs:

$$
APY_{net} = \left(1 + \frac{APR}{n} - \frac{G_{cost}}{V_{position}}\right)^n - 1
$$

Where:
- $G_{cost}$ = gas cost per compound transaction
- $V_{position}$ = position value

If gas cost per compound exceeds the yield per period, compounding destroys value:

$$
\text{Compound only if: } \frac{APR}{n} \cdot V_{position} > G_{cost}
$$

### 4.5 Optimal Compounding Frequency

The optimal number of compounds per year maximizes net APY:

$$
n^* = \argmax_n \left\{\left(1 + \frac{APR}{n} - \frac{G}{V}\right)^n - 1\right\}
$$

Taking the derivative and setting to zero (approximation for large $n$):

$$
n^* \approx \sqrt{\frac{APR \cdot V}{2 \cdot G}}
$$

**Examples**:

| Position Value | APR   | Gas Cost/tx | Optimal Compounds/Year | Optimal Interval |
|----------------|-------|-------------|------------------------|------------------|
| $1,000         | 50%   | $5          | 7                      | Every 52 days    |
| $10,000        | 50%   | $5          | 22                     | Every 17 days    |
| $100,000       | 50%   | $5          | 70                     | Every 5 days     |
| $10,000        | 100%  | $5          | 32                     | Every 11 days    |
| $10,000        | 100%  | $50         | 10                     | Every 37 days    |
| $10,000        | 20%   | $5          | 14                     | Every 26 days    |

### 4.6 Auto-Compounder Implementation

```python
class AutoCompounder:
    """
    Auto-compounds yield farming rewards optimally.
    """

    def __init__(self, config: CompoundConfig):
        self.min_reward_value = config.min_reward_value  # Min USD to harvest
        self.gas_threshold = config.gas_threshold  # Max gas price for compound
        self.compound_buffer = config.compound_buffer  # 3x gas cost minimum

    def calculate_optimal_interval(
        self,
        position_value: float,
        apr: float,
        gas_cost: float
    ) -> float:
        """Calculate optimal compounding interval in seconds."""
        if apr <= 0 or position_value <= 0:
            return float('inf')

        # Optimal compounds per year
        optimal_n = math.sqrt(apr * position_value / (2 * gas_cost))
        optimal_n = max(1, min(optimal_n, 365))  # Bound: 1-365 per year

        # Convert to interval in seconds
        interval_seconds = (365.25 * 24 * 3600) / optimal_n
        return interval_seconds

    async def should_compound_now(self, position: YieldPosition) -> CompoundDecision:
        """
        Determine if now is a good time to compound.
        """
        # Get current reward value
        pending_rewards = await position.get_pending_rewards()
        reward_value_usd = await self.price_rewards(pending_rewards)

        # Get current gas cost
        gas_cost_usd = await self.estimate_compound_gas_cost()

        # Calculate time since last compound
        time_elapsed = time.time() - position.last_compound_time
        optimal_interval = self.calculate_optimal_interval(
            position.value, position.current_apr, gas_cost_usd
        )

        # Decision logic
        reasons = []

        # Check 1: Minimum reward threshold
        if reward_value_usd < self.min_reward_value:
            return CompoundDecision(should_compound=False,
                                   reason="Reward below minimum threshold")

        # Check 2: Reward must exceed gas cost by buffer
        if reward_value_usd < gas_cost_usd * self.compound_buffer:
            return CompoundDecision(should_compound=False,
                                   reason=f"Reward ${reward_value_usd:.2f} < "
                                          f"{self.compound_buffer}x gas ${gas_cost_usd:.2f}")

        # Check 3: Time-based (is it time based on optimal interval?)
        if time_elapsed < optimal_interval * 0.8:
            return CompoundDecision(should_compound=False,
                                   reason="Not yet time for optimal compound")

        # Check 4: Gas price acceptable
        gas_price_gwei = await self.gas_estimator.get_current()
        if gas_price_gwei > self.gas_threshold:
            return CompoundDecision(should_compound=False,
                                   reason=f"Gas price {gas_price_gwei} > threshold")

        return CompoundDecision(
            should_compound=True,
            reward_value=reward_value_usd,
            gas_cost=gas_cost_usd,
            net_value=reward_value_usd - gas_cost_usd,
            reason="All conditions met for optimal compound"
        )

    async def execute_compound(self, position: YieldPosition):
        """Execute the compound operation."""
        # Step 1: Harvest rewards
        rewards = await position.harvest()

        # Step 2: Swap rewards to base assets (if needed)
        if position.reward_token != position.deposit_token:
            base_amount = await self.swap_to_base(
                rewards, position.deposit_token
            )
        else:
            base_amount = rewards

        # Step 3: Deposit back into position
        await position.deposit_additional(base_amount)

        # Step 4: Update records
        position.last_compound_time = time.time()
        position.total_compounds += 1
        position.total_gas_spent += await self.get_last_gas_cost()

        logger.info(f"Compounded {position.id}: "
                   f"${base_amount:.2f} reinvested, "
                   f"gas ${position.total_gas_spent:.2f}")
```

---

## 5. Yield Aggregator Strategies

### 5.1 Yearn Finance Model

Yearn Finance vaults implement sophisticated multi-step strategies:

```
Yearn Vault Architecture:
├── Vault (ERC-4626) — User-facing deposit/withdraw
│   ├── Strategy 1 (e.g., Lend on Aave, earn interest)
│   ├── Strategy 2 (e.g., Farm CRV on Curve)
│   ├── Strategy 3 (e.g., Leverage loop on Compound)
│   └── Strategy N (e.g., Provide liquidity on Balancer)
│
├── Strategist — Deploys and manages strategies
├── Guardian — Emergency controls
└── Governance — Parameter updates
```

**Key Mechanics**:

1. Users deposit a single asset (e.g., USDC).
2. Vault distributes across multiple strategies.
3. Each strategy implements `harvest()` to realize gains.
4. Realized gains increase the vault's share price.
5. Users withdraw at the new (higher) share price.

**Vault Share Price**:

$$
P_{share}(t) = \frac{\text{Total Assets}(t)}{\text{Total Shares}}
$$

$$
\text{Total Assets}(t) = \text{Idle Balance} + \sum_i \text{Strategy}_i\text{.totalAssets()}
$$

### 5.2 Beefy Finance Model

Beefy focuses on auto-compounding single strategies:

```
Beefy Vault Flow:
1. User deposits LP tokens (e.g., ETH/USDC Uniswap LP)
2. Vault stakes LP tokens in farm (earning reward tokens)
3. Bot periodically harvests reward tokens
4. Bot sells reward tokens -> base assets
5. Bot adds liquidity (gets more LP tokens)
6. Bot deposits LP tokens back (compounding)
7. Vault share price increases
```

**Fee Structure**:
- Harvest caller fee: 0.01-0.5% of harvest (incentivizes bot operators)
- Performance fee: 3-5% of profits
- Management fee: 0% (no fee on deposits)
- Withdrawal fee: 0-0.1% (discourages frequent withdrawal)

### 5.3 Strategy Selection Algorithm

How does Yearn select which strategy gets capital?

```python
def allocate_capital(vault, strategies):
    """
    Allocate vault capital across strategies.
    Based on risk-adjusted expected return.
    """
    available_capital = vault.total_assets

    # Score each strategy
    scored_strategies = []
    for strategy in strategies:
        expected_apr = strategy.estimate_apr()
        risk_score = strategy.assess_risk()
        capacity = strategy.remaining_capacity()

        # Risk-adjusted score
        score = expected_apr * (1 - risk_score) * min(1, capacity / available_capital)
        scored_strategies.append((strategy, score, capacity))

    # Sort by score descending
    scored_strategies.sort(key=lambda x: x[1], reverse=True)

    # Allocate greedily respecting capacity and diversification
    remaining = available_capital
    allocations = {}

    for strategy, score, capacity in scored_strategies:
        # Max allocation per strategy (diversification limit)
        max_alloc = available_capital * 0.40  # No more than 40% per strategy
        alloc = min(remaining, capacity, max_alloc)

        if alloc > 0 and score > MIN_SCORE_THRESHOLD:
            allocations[strategy] = alloc
            remaining -= alloc

        if remaining <= 0:
            break

    return allocations
```

### 5.4 Vault Performance Metrics

| Metric                   | Formula                                        | Target     |
|--------------------------|------------------------------------------------|------------|
| Net APY                  | $(P_{share}(t)/P_{share}(0))^{365/t} - 1$     | > Risk-free + 5% |
| Sharpe Ratio             | $(APY - r_f)/\sigma_{daily} \cdot \sqrt{365}$  | > 1.5      |
| Max Drawdown             | $\max(1 - P_{share}(t)/P_{share,max})$         | < 5%       |
| Gas Efficiency           | $\text{Profit}/\text{Gas Spent}$               | > 10x      |
| Strategy Utilization     | $\text{Deployed}/\text{Total Assets}$          | > 90%      |

---

## 6. Leveraged Yield Farming

### 6.1 Concept

Leveraged yield farming involves borrowing additional assets to amplify yield farming
returns. The most common model (pioneered by Alpaca Finance):

```
1. Deposit $1000 collateral (e.g., ETH)
2. Borrow $2000 from lending pool (3x leverage)
3. Deploy $3000 total into yield farm
4. Earn yield on $3000 (3x the base yield)
5. Pay borrowing interest on $2000
6. Net yield = (3x farm yield) - (2x borrow rate)
```

### 6.2 Mathematics of Leveraged Farming

For leverage multiple $m$ (e.g., $m = 3$ for 3x):

**Deposited**: $V_{deposit}$ (user's capital)
**Borrowed**: $V_{borrow} = V_{deposit} \cdot (m - 1)$
**Total Position**: $V_{total} = V_{deposit} \cdot m$

$$
\text{Leveraged APR} = m \cdot APR_{farm} - (m-1) \cdot R_{borrow}
$$

$$
\text{Leveraged APY} = \left(1 + \frac{m \cdot APR_{farm} - (m-1) \cdot R_{borrow}}{n}\right)^n - 1
$$

### 6.3 Break-Even Condition

The strategy is profitable when:

$$
m \cdot APR_{farm} > (m-1) \cdot R_{borrow}
$$

$$
APR_{farm} > \frac{m-1}{m} \cdot R_{borrow}
$$

For 3x leverage:
$$
APR_{farm} > \frac{2}{3} \cdot R_{borrow}
$$

### 6.4 Risk: Liquidation

With leverage, positions can be liquidated if value drops:

$$
\text{Debt Ratio} = \frac{V_{borrow}}{V_{total}} = \frac{m-1}{m}
$$

Liquidation occurs when:

$$
\frac{V_{current\_position}}{V_{borrow}} < \text{Liquidation Factor}
$$

For a leveraged LP position, both IL and price decline affect liquidation risk:

$$
V_{current} = V_{total} \cdot (1 + IL) \cdot (1 + \Delta P_{portfolio})
$$

### 6.5 Leverage Optimization

Optimal leverage maximizes risk-adjusted return:

$$
m^* = \argmax_m \frac{m \cdot APR_{farm} - (m-1) \cdot R_{borrow}}{\sigma_{position} \cdot m}
$$

In practice:

| Farm APR | Borrow Rate | Optimal Leverage | Net APR | Risk Level |
|----------|-------------|------------------|---------|------------|
| 20%      | 5%          | 2-3x             | 35-55%  | Medium     |
| 50%      | 10%         | 2-3x             | 80-130% | Medium-High|
| 100%     | 15%         | 3-5x             | 270-455%| High       |
| 10%      | 8%          | 1.5x             | 11%     | Low        |

### 6.6 Delta-Neutral Leveraged Farming

To eliminate directional risk:

```
Strategy:
1. Deposit $1000 in leveraged farm (3x, ETH/USDC LP)
2. Total position = $3000 LP
3. LP has approximately $1500 ETH exposure
4. Short $1500 of ETH on perpetual exchange
5. Net ETH exposure = 0 (delta-neutral)
6. Earn: 3x farm yield - borrow cost - funding rate
```

$$
\text{Delta-Neutral APR} = m \cdot APR_{farm} - (m-1) \cdot R_{borrow} - \frac{m}{2} \cdot R_{funding}
$$

---

## 7. Real Yield vs Inflationary Yield

### 7.1 Classification Framework

**Real Yield**: Generated from actual economic activity.

$$
\text{Real Yield} = \frac{\text{Protocol Revenue} \times \text{Distribution\%}}{\text{Token Market Cap}}
$$

Sources:
- Trading fees distributed to token holders/LPs.
- Borrowing interest distributed to lenders.
- Protocol service fees.
- MEV capture redistributed to stakeholders.

**Inflationary Yield**: Generated from new token minting.

$$
\text{Inflationary Yield} = \frac{\text{New Tokens Minted} \times \text{Token Price}}{\text{TVL}}
$$

The key difference: Inflationary yield dilutes existing holders. If all farmers sell,
the token price drops, and real yield received is much lower than headline APR.

### 7.2 Sustainability Analysis

**Sustainable yield** satisfies:

$$
\text{Fee Revenue} \geq \text{Token Emissions} \times \text{Token Price}
$$

Or equivalently:

$$
P/E_{protocol} = \frac{\text{Token FDV}}{\text{Annual Revenue}} < \text{Reasonable Multiple}
$$

Protocols with P/E > 100 are likely unsustainably distributing inflationary rewards.

### 7.3 Real Yield Protocol Examples

| Protocol   | Revenue Source            | Yield Distribution | Approx. Real Yield |
|------------|---------------------------|--------------------|--------------------|
| Uniswap    | Trading fees (100% to LPs)| LP fees            | 5-30% APR          |
| Aave       | Borrowing interest        | To lenders         | 2-8% APR           |
| GMX        | Trading/borrowing fees    | 70% to GLP/stakers| 10-30% APR         |
| Lido       | Staking rewards - commission| To stETH holders | 3-5% APR           |
| Curve      | Trading fees + bribes     | veCRV holders      | 3-10% APR          |

### 7.4 Yield Quality Score

For the trading system, assign a quality score to each yield source:

$$
Q_{yield} = w_1 \cdot \text{Sustainability} + w_2 \cdot \text{Consistency} + w_3 \cdot \text{Predictability}
$$

Where:
- Sustainability: Is yield from real revenue or inflation?
- Consistency: How stable is the yield over time?
- Predictability: Can we forecast future yield with confidence?

| Score Range | Classification    | Allocation Limit  |
|-------------|-------------------|-------------------|
| 8-10        | Premium Yield     | Up to 30% of farm allocation |
| 6-8         | Standard Yield    | Up to 20% of farm allocation |
| 4-6         | Speculative Yield | Up to 10% of farm allocation |
| 0-4         | Degen Yield       | Up to 3% (or avoid)          |

---

## 8. Risk-Adjusted Yield Comparison

### 8.1 Risk-Adjusted Return Metrics

#### Sharpe Ratio for Yield Farming

$$
S = \frac{APY_{net} - r_f}{\sigma_{daily} \cdot \sqrt{365}}
$$

Where:
- $APY_{net}$ = net yield after all costs
- $r_f$ = risk-free rate (e.g., US Treasury ~4-5%)
- $\sigma_{daily}$ = daily standard deviation of yield returns

#### Sortino Ratio (downside-only risk)

$$
\text{Sortino} = \frac{APY_{net} - r_f}{\sigma_{downside} \cdot \sqrt{365}}
$$

#### Risk-Adjusted Yield (RAY)

A custom metric for comparing across DeFi strategies:

$$
RAY = \frac{APY_{net}}{1 + \sum_i w_i \cdot R_i}
$$

Where $R_i$ are risk factors:
- $R_{sc}$ = smart contract risk (0-1)
- $R_{il}$ = impermanent loss risk (0-1)
- $R_{liq}$ = liquidation risk (0-1)
- $R_{token}$ = reward token price risk (0-1)
- $R_{protocol}$ = protocol failure risk (0-1)

### 8.2 Comparison Framework

```python
class YieldComparator:
    """Compare yield opportunities on a risk-adjusted basis."""

    def compare(self, opportunities: List[YieldOpportunity]) -> pd.DataFrame:
        results = []
        for opp in opportunities:
            # Calculate net yield
            gross_apr = opp.base_apr + opp.reward_apr
            net_apr = gross_apr - opp.gas_cost_apr - opp.il_estimate

            # Convert to APY
            net_apy = (1 + net_apr / opp.compound_frequency) ** opp.compound_frequency - 1

            # Calculate risk score
            risk = self.calculate_risk_score(opp)

            # Risk-adjusted metrics
            ray = net_apy / (1 + risk)
            sharpe = (net_apy - self.risk_free_rate) / opp.volatility

            results.append({
                'protocol': opp.protocol,
                'pool': opp.pool_name,
                'gross_apr': gross_apr,
                'net_apy': net_apy,
                'risk_score': risk,
                'ray': ray,
                'sharpe': sharpe,
                'recommendation': self.get_recommendation(ray, sharpe)
            })

        return pd.DataFrame(results).sort_values('ray', ascending=False)

    def calculate_risk_score(self, opp: YieldOpportunity) -> float:
        """Calculate composite risk score (0-1)."""
        risks = {
            'smart_contract': opp.audit_score * 0.25,
            'impermanent_loss': opp.il_exposure * 0.20,
            'liquidation': opp.liquidation_risk * 0.20,
            'token_emission': opp.emission_dependency * 0.20,
            'protocol': opp.protocol_risk * 0.15,
        }
        return sum(risks.values())
```

### 8.3 Opportunity Comparison Example

| Strategy              | Gross APR | Net APY | Risk Score | RAY    | Decision   |
|-----------------------|-----------|---------|------------|--------|------------|
| stETH staking         | 4.5%      | 4.6%    | 0.15       | 4.0%   | Strong Buy |
| ETH/USDC LP (V3)     | 25%       | 22%     | 0.45       | 15.2%  | Buy        |
| Curve stables LP      | 8%        | 8.3%    | 0.20       | 6.9%   | Buy        |
| Leveraged farm 3x     | 60%       | 75%     | 0.75       | 42.9%  | Speculative|
| New token farm        | 500%      | 1200%   | 0.95       | 615%   | High Risk  |

---

## 9. Optimal Harvest Frequency

### 9.1 Harvest Decision Framework

Harvesting (claiming rewards) should occur when:

$$
\text{Reward Value} \geq k \cdot \text{Gas Cost}
$$

Where $k$ is the minimum multiple (typically 3-10x) to ensure profitability.

### 9.2 Factors Affecting Harvest Timing

1. **Reward token volatility**: Volatile reward tokens should be harvested more
   frequently to reduce exposure to price drops.
2. **Gas prices**: Harvest during low-gas periods (weekends, off-hours).
3. **Compound benefit**: Delay harvesting benefits from continued compounding
   only if rewards are auto-staked.
4. **Tax implications**: In some jurisdictions, each harvest is a taxable event.
5. **Token vesting**: Some rewards have vesting schedules (delay is forced).

### 9.3 Optimal Harvest with Declining Reward Token

If reward token price is expected to decline at rate $d$ per period:

$$
V_{harvest\_now} = R \cdot P_{current}
$$

$$
V_{harvest\_later} = (R + R_{additional}) \cdot P_{current} \cdot (1-d) - G
$$

Harvest now if:

$$
R \cdot P \cdot d > R_{additional} \cdot P \cdot (1-d) - G
$$

For rapidly declining tokens ($d > 5\%$ per day), harvest as frequently as gas allows.

### 9.4 Harvest Timing Algorithm

```python
class HarvestOptimizer:
    """Determines optimal harvest timing for each position."""

    def should_harvest(self, position: FarmPosition) -> HarvestDecision:
        """
        Multi-factor harvest decision.
        """
        # Get pending reward value
        pending = position.get_pending_reward_value()

        # Current gas cost
        gas_cost = self.estimate_harvest_gas()

        # Minimum threshold: 5x gas cost
        if pending < gas_cost * 5:
            return HarvestDecision(harvest=False, reason="Below gas threshold")

        # Check reward token price trend
        token_price_trend = self.get_price_trend(position.reward_token, days=7)

        # If token is declining >2% per day, harvest aggressively
        if token_price_trend < -0.02:
            if pending > gas_cost * 2:  # Lower threshold for declining token
                return HarvestDecision(
                    harvest=True,
                    reason="Declining reward token, harvest to protect value"
                )

        # Check if gas is cheap (below 50th percentile of last 24h)
        gas_percentile = self.get_gas_percentile()
        if gas_percentile < 0.30 and pending > gas_cost * 3:
            return HarvestDecision(
                harvest=True,
                reason="Low gas window, good time to harvest"
            )

        # Time-based: harvest at optimal interval
        time_since_last = time.time() - position.last_harvest_time
        optimal_interval = self.calculate_optimal_interval(position)

        if time_since_last > optimal_interval and pending > gas_cost * 3:
            return HarvestDecision(
                harvest=True,
                reason="Optimal time interval reached"
            )

        return HarvestDecision(harvest=False, reason="No trigger conditions met")
```

---

## 10. Gas Cost Optimization

### 10.1 Gas Cost Impact on Yield

Gas costs directly reduce farming profitability:

$$
APY_{effective} = APY_{gross} - \frac{G_{total}}{V_{position}} \cdot \frac{365}{T_{days}}
$$

Where $G_{total}$ = total gas spent over the farming period.

### 10.2 Gas-Heavy Operations

| Operation                    | Typical Gas (L1) | Cost at 30 gwei ($3000 ETH) |
|------------------------------|------------------|-----------------------------|
| Approve token                | 50,000           | $4.50                       |
| Swap (Uniswap V3)           | 150,000          | $13.50                      |
| Add LP (V3 mint)            | 400,000          | $36.00                      |
| Remove LP (V3 decrease)     | 150,000          | $13.50                      |
| Collect fees (V3)           | 120,000          | $10.80                      |
| Harvest rewards             | 100,000-300,000  | $9-27                       |
| Deposit in vault            | 200,000-500,000  | $18-45                      |
| Complete compound cycle     | 500,000-1,000,000| $45-90                      |

### 10.3 Gas Optimization Strategies

#### 10.3.1 Batch Operations

Combine multiple operations into a single transaction using multicall:

```python
# Instead of separate transactions:
# tx1: harvest()
# tx2: swap()
# tx3: addLiquidity()

# Use multicall:
multicall([
    harvest.encode(),
    swap.encode(),
    addLiquidity.encode()
])
# Saves ~30% gas from reduced base transaction costs
```

#### 10.3.2 Gas Price Timing

```python
class GasTimer:
    """Find optimal gas price windows."""

    def get_cheap_gas_window(self, max_wait_hours=24) -> Optional[TimeWindow]:
        """
        Analyze historical gas patterns to find cheap windows.
        Typically: weekends, early UTC morning (1-6 AM)
        """
        historical = self.get_gas_history(hours=168)  # 1 week

        # Find lowest gas periods
        by_hour = self.group_by_hour(historical)
        cheapest_hours = sorted(by_hour.items(), key=lambda x: x[1])[:6]

        # Find next occurrence of a cheap hour
        now = datetime.utcnow()
        for hour, avg_gas in cheapest_hours:
            next_occurrence = self.next_time_at_hour(now, hour)
            if (next_occurrence - now).total_seconds() / 3600 < max_wait_hours:
                return TimeWindow(
                    start=next_occurrence,
                    expected_gas=avg_gas
                )

        return None
```

#### 10.3.3 L2 Migration

For smaller positions, operate on L2s where gas is 10-100x cheaper:

| Chain       | Typical Gas Cost | Suitable Position Size |
|-------------|------------------|------------------------|
| Ethereum L1 | $10-100/tx       | > $50,000             |
| Arbitrum    | $0.10-1/tx       | > $1,000              |
| Optimism    | $0.10-1/tx       | > $1,000              |
| Base        | $0.01-0.10/tx    | > $100                |
| Polygon     | $0.01-0.05/tx    | > $100                |

#### 10.3.4 Minimum Position Size Formula

The minimum position size for profitable farming on a given chain:

$$
V_{min} = \frac{G_{annual} \cdot (1 + \text{margin})}{\text{Net APR}}
$$

Where $G_{annual}$ = total expected gas costs per year.

**Example**: On Ethereum L1, with $500/year in gas and 15% net APR:

$$
V_{min} = \frac{500 \times 1.5}{0.15} = \$5,000
$$

Positions below $5,000 should use L2.

---

## 11. Multi-Protocol Yield Optimization

### 11.1 Portfolio Approach to Yield Farming

Instead of picking a single farm, the trading system optimizes across multiple
protocols simultaneously:

$$
\max_{\mathbf{w}} \sum_{i=1}^{N} w_i \cdot Y_i - \lambda \cdot \text{Risk}(\mathbf{w})
$$

Subject to:
- $\sum_i w_i = 1$ (fully allocated)
- $w_i \geq 0$ (no shorting yield positions)
- $w_i \leq w_{max}$ (diversification limit)
- $\text{Protocol}_i \in \text{Approved List}$ (risk filter)

### 11.2 Yield Correlation Analysis

Yield from different protocols can be correlated:

| Factor                    | Correlation Impact                       |
|---------------------------|------------------------------------------|
| Same chain, same token    | High correlation                         |
| Same chain, different token| Medium correlation                      |
| Different chain, same token| Low-medium correlation                  |
| Different mechanism        | Low correlation (lending vs LP vs staking)|

The trading system builds a yield correlation matrix:

$$
\Sigma_{yield} = \text{Cov}(Y_1, Y_2, ..., Y_N)
$$

And minimizes portfolio risk:

$$
\text{Risk}(\mathbf{w}) = \mathbf{w}^T \Sigma_{yield} \mathbf{w}
$$

### 11.3 Rebalancing Across Protocols

When yields change, the optimal allocation shifts. Rebalance when:

$$
|\mathbf{w}_{current} - \mathbf{w}_{optimal}| > \text{threshold}
$$

And the expected improvement exceeds rebalancing cost:

$$
\sum_i |w_i^{new} - w_i^{old}| \cdot \text{Gas Cost}(i) < \Delta Y_{expected} \cdot T_{horizon}
$$

### 11.4 Multi-Protocol Strategy Examples

**Conservative (70-80% real yield)**:

```
30% — Lido stETH (staking yield ~4%)
25% — Aave USDC lending (~5%)
20% — Curve 3pool LP (~3-8%)
15% — Uniswap V3 stables (~5-10%)
10% — Cash reserve (gas, opportunities)
```

**Moderate (mix of real + incentivized)**:

```
20% — Lido stETH -> Aave collateral
20% — Uniswap V3 ETH/USDC (concentrated)
20% — Curve + CRV staking (boosted)
15% — GMX GLP (trading fee yield)
15% — Pendle yield tokenization
10% — Cash reserve
```

**Aggressive (high incentive yield)**:

```
25% — Leveraged yield farm (3x)
25% — New protocol liquidity mining
20% — Points farming (airdrop speculation)
15% — High-APR stablecoin farms
10% — Delta-neutral basis trade
5%  — Cash reserve
```

---

## 12. Strategy Rotation Algorithm

### 12.1 Concept

Strategy rotation involves dynamically shifting capital from lower-yielding to
higher-yielding opportunities. The algorithm must balance:

- **Switching cost** (gas + slippage + time out of market)
- **Yield improvement** (must exceed switching cost)
- **Stability** (avoid excessive churning)
- **Information lag** (yields can change rapidly)

### 12.2 Rotation Triggers

```
ROTATE when ALL conditions met:

1. New opportunity yield > Current yield + Minimum Spread
   (Minimum Spread = 5% APR difference)

2. New opportunity has been stable for > 24 hours
   (Avoid chasing flash-in-the-pan yields)

3. Switching cost < 7 days of yield improvement
   (Must recoup switching cost within 1 week)

4. New opportunity passes risk assessment
   (All standard risk checks must pass)

5. Current position has been held for > minimum_hold_time
   (Prevent rapid churning — min 48 hours)
```

### 12.3 Rotation Algorithm

```python
class StrategyRotator:
    """
    Manages rotation between yield strategies
    based on risk-adjusted returns.
    """

    def __init__(self, config: RotationConfig):
        self.min_yield_spread = config.min_yield_spread  # 5% APR
        self.min_hold_time = config.min_hold_time  # 48 hours
        self.max_switching_cost_days = config.max_switching_cost_days  # 7 days
        self.stability_requirement = config.stability_hours  # 24 hours
        self.cooldown_period = config.cooldown  # 6 hours between rotations

    async def evaluate_rotation(
        self,
        current_positions: List[YieldPosition],
        available_opportunities: List[YieldOpportunity]
    ) -> List[RotationPlan]:
        """
        Evaluate which positions should rotate to new opportunities.
        """
        rotations = []

        for position in current_positions:
            # Check minimum hold time
            if position.age_seconds < self.min_hold_time:
                continue

            # Check cooldown
            if position.time_since_last_rotation < self.cooldown_period:
                continue

            # Get current yield (realized, not projected)
            current_yield = position.get_realized_apr(lookback_hours=72)

            # Find best available opportunity for this capital
            best_opp = self.find_best_opportunity(
                capital=position.value,
                current_chain=position.chain,
                exclude_protocols=[position.protocol],
                opportunities=available_opportunities
            )

            if best_opp is None:
                continue

            # Check yield spread
            yield_improvement = best_opp.expected_apr - current_yield
            if yield_improvement < self.min_yield_spread:
                continue

            # Check stability of new opportunity
            if not best_opp.has_been_stable(hours=self.stability_requirement):
                continue

            # Calculate switching cost
            switching_cost = self.calculate_switching_cost(position, best_opp)
            daily_improvement = position.value * yield_improvement / 365
            payback_days = switching_cost / daily_improvement if daily_improvement > 0 else float('inf')

            if payback_days > self.max_switching_cost_days:
                continue

            # All checks passed — recommend rotation
            rotations.append(RotationPlan(
                from_position=position,
                to_opportunity=best_opp,
                yield_improvement=yield_improvement,
                switching_cost=switching_cost,
                payback_days=payback_days,
                priority=yield_improvement / (1 + position.risk_score)
            ))

        # Sort by priority (highest improvement first)
        rotations.sort(key=lambda r: r.priority, reverse=True)
        return rotations

    def calculate_switching_cost(
        self, current: YieldPosition, target: YieldOpportunity
    ) -> float:
        """Calculate total cost of switching from current to target."""
        costs = []

        # Exit cost (gas + slippage for withdrawal)
        costs.append(self.estimate_exit_gas(current))
        costs.append(current.value * current.exit_slippage)

        # Bridge cost (if different chain)
        if current.chain != target.chain:
            costs.append(self.estimate_bridge_cost(current.value))
            costs.append(current.value * 0.001)  # Bridge slippage

        # Swap cost (if different token needed)
        if current.base_token != target.required_token:
            costs.append(self.estimate_swap_gas())
            costs.append(current.value * 0.003)  # Swap slippage

        # Entry cost (gas + slippage for deposit)
        costs.append(self.estimate_entry_gas(target))
        costs.append(current.value * target.entry_slippage)

        # Time out of market (lost yield during transition)
        transition_hours = 1  # Assume 1 hour transition
        lost_yield = current.value * current.get_realized_apr(72) * transition_hours / (365 * 24)
        costs.append(lost_yield)

        return sum(costs)

    async def execute_rotation(self, plan: RotationPlan):
        """Execute a rotation plan."""
        logger.info(
            f"Rotating: {plan.from_position.protocol}/{plan.from_position.pool} "
            f"-> {plan.to_opportunity.protocol}/{plan.to_opportunity.pool} "
            f"(+{plan.yield_improvement:.1%} APR, payback {plan.payback_days:.1f} days)"
        )

        # Step 1: Exit current position
        withdrawn = await self.exit_position(plan.from_position)

        # Step 2: Bridge if needed
        if plan.from_position.chain != plan.to_opportunity.chain:
            withdrawn = await self.bridge_assets(
                withdrawn, plan.to_opportunity.chain
            )

        # Step 3: Swap to required tokens if needed
        if plan.from_position.base_token != plan.to_opportunity.required_token:
            withdrawn = await self.swap_tokens(
                withdrawn, plan.to_opportunity.required_token
            )

        # Step 4: Enter new position
        new_position = await self.enter_position(
            plan.to_opportunity, withdrawn
        )

        logger.info(f"Rotation complete. New position: {new_position.id}")
        return new_position
```

---

## 13. Complete Execution Flow

### 13.1 Yield Farming Bot Architecture

```python
class YieldFarmingBot:
    """
    Complete yield farming bot that manages:
    - Opportunity scanning
    - Position entry/exit
    - Auto-compounding
    - Strategy rotation
    - Risk management
    """

    def __init__(self, config: BotConfig):
        self.scanner = YieldScanner(config.scanner)
        self.compounder = AutoCompounder(config.compound)
        self.rotator = StrategyRotator(config.rotation)
        self.risk_manager = YieldRiskManager(config.risk)
        self.gas_optimizer = GasOptimizer(config.gas)
        self.portfolio = YieldPortfolio()

    async def main_loop(self):
        """Main bot execution loop."""
        while True:
            try:
                # ==========================================
                # PHASE 1: SCAN OPPORTUNITIES
                # ==========================================
                opportunities = await self.scanner.scan_all_protocols()
                opportunities = self.risk_manager.filter(opportunities)
                ranked = self.rank_opportunities(opportunities)

                # ==========================================
                # PHASE 2: MONITOR EXISTING POSITIONS
                # ==========================================
                for position in self.portfolio.active_positions():
                    # Update metrics
                    await position.refresh_state()

                    # Check compound trigger
                    compound_decision = await self.compounder.should_compound_now(position)
                    if compound_decision.should_compound:
                        await self.compounder.execute_compound(position)

                    # Check risk triggers
                    risk_check = self.risk_manager.check_position(position)
                    if risk_check.should_exit:
                        await self.exit_position(position, risk_check.reason)
                        continue

                # ==========================================
                # PHASE 3: EVALUATE ROTATIONS
                # ==========================================
                rotations = await self.rotator.evaluate_rotation(
                    current_positions=self.portfolio.active_positions(),
                    available_opportunities=ranked
                )

                for rotation in rotations[:3]:  # Max 3 rotations per cycle
                    if await self.gas_optimizer.is_good_time():
                        await self.rotator.execute_rotation(rotation)

                # ==========================================
                # PHASE 4: NEW POSITION ENTRY
                # ==========================================
                available_capital = self.portfolio.available_capital()
                if available_capital > self.config.min_deploy_amount:
                    best_opp = self.find_best_new_entry(ranked, available_capital)
                    if best_opp:
                        await self.enter_new_position(best_opp, available_capital)

                # ==========================================
                # PHASE 5: REPORT & SLEEP
                # ==========================================
                await self.report_portfolio_status()
                await asyncio.sleep(self.config.scan_interval)

            except Exception as e:
                logger.error(f"Bot error: {e}")
                await self.alert_system.notify(e)
                await asyncio.sleep(60)

    def rank_opportunities(self, opportunities: List[YieldOpportunity]) -> List:
        """Rank by risk-adjusted yield."""
        for opp in opportunities:
            # Calculate risk-adjusted yield
            risk_score = self.risk_manager.score(opp)
            opp.ray_score = opp.net_apy / (1 + risk_score)

            # Penalize high gas cost relative to position size
            gas_penalty = opp.estimated_annual_gas / opp.min_position_size
            opp.ray_score -= gas_penalty

            # Bonus for yield stability
            if opp.yield_stability_7d > 0.8:
                opp.ray_score *= 1.1

        return sorted(opportunities, key=lambda o: o.ray_score, reverse=True)
```

---

## 14. Risk Parameters

### 14.1 Yield Farming Risk Limits

| Parameter                        | Value     | Rationale                        |
|----------------------------------|-----------|----------------------------------|
| Max single-farm allocation       | 10% AUM   | Diversification                  |
| Max single-protocol allocation   | 15% AUM   | Protocol risk limit              |
| Max leverage multiple            | 3x        | Liquidation buffer               |
| Min position size (L1)           | $5,000    | Gas cost efficiency              |
| Min position size (L2)           | $500      | Lower gas threshold              |
| Max inflationary yield exposure  | 30%       | Limit exposure to token dilution |
| Min yield for entry              | Risk-free + 3% | Must beat alternatives       |
| Max TVL concentration            | 5% of pool| Avoid whale risk                 |
| Harvest minimum (gas multiple)   | 5x        | Gas cost efficiency              |
| Strategy rotation cooldown       | 48 hours  | Prevent churning                 |

### 14.2 Protocol-Specific Risk Parameters

| Protocol Type    | Max Allocation | Required Audit | Min TVL   | Min Age  |
|------------------|----------------|----------------|-----------|----------|
| Blue-chip DeFi   | 15%            | 2+ audits      | $500M     | 2 years  |
| Established DeFi | 10%            | 2+ audits      | $100M     | 1 year   |
| Growth DeFi      | 5%             | 1+ audit       | $20M      | 6 months |
| New DeFi         | 2%             | 1+ audit       | $5M       | 3 months |
| Unaudited        | 0%             | N/A            | N/A       | N/A      |

### 14.3 Stop-Loss Rules

```
EXIT IMMEDIATELY if:
1. Protocol exploit reported (any amount)
2. TVL drops > 30% in 1 hour (potential exploit or bank run)
3. Reward token drops > 50% in 24 hours (death spiral risk)
4. Health factor below 1.30 (leveraged positions)
5. Smart contract pause event detected
6. Governance attack in progress

EXIT WITHIN 24 HOURS if:
1. Yield drops below risk-free rate
2. Better risk-adjusted opportunity available (rotation)
3. Risk score of protocol increases above threshold
4. Correlation with other positions exceeds limit
5. Gas costs consistently exceed yield for 48 hours
```

---

## 15. References

### Research Papers

1. Xu, J., Vavryk, D., Paruch, K., Cousaert, S. (2021). "SoK: Decentralized
   Finance (DeFi) — A Survey." arXiv:2101.08778.

2. Werner, S.M., Perez, D., Gudgeon, L., Klages-Mundt, A., Harz, D., Knottenbelt, W.J.
   (2021). "SoK: Decentralized Finance (DeFi)." arXiv:2101.08778.

3. Cousaert, S., Xu, J., Matsui, T. (2022). "SoK: Yield Aggregators in DeFi."
   IEEE International Conference on Blockchain.

4. Chitra, T., Evans, A. (2022). "Why Stake When You Can Borrow?"
   arXiv:2206.08401.

### Protocol Documentation

5. Yearn Finance Documentation. https://docs.yearn.fi/
6. Beefy Finance Documentation. https://docs.beefy.finance/
7. Alpaca Finance Documentation. https://docs.alpacafinance.org/
8. Convex Finance Documentation. https://docs.convexfinance.com/
9. Pendle Finance Documentation. https://docs.pendle.finance/

### Data Sources

10. DefiLlama Yields. https://defillama.com/yields
11. Vfat Tools. https://vfat.tools/
12. APY Vision. https://apy.vision/
13. Yield Monitor (DeFi Pulse). https://www.defipulse.com/

---

> **Next Document**: [04_flash_loans_composability.md](./04_flash_loans_composability.md)
> — Flash loan mechanics, use cases, and DeFi composability patterns.
