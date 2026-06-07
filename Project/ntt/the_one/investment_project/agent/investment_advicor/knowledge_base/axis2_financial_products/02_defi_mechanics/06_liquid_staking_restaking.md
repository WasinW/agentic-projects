# Liquid Staking & Restaking — Complete Mechanics

> **Axis 2 — Financial Products | Module 02 — DeFi Mechanics | Document 06**
> Version: 2.0.0 | Last Updated: 2026-04-12
> Classification: KNOWLEDGE BASE — MULTI-AGENT AI TRADING SYSTEM

---

## Table of Contents

1. [Introduction to Liquid Staking](#1-introduction-to-liquid-staking)
2. [Ethereum Staking Fundamentals](#2-ethereum-staking-fundamentals)
3. [Lido (stETH) Mechanics](#3-lido-steth-mechanics)
4. [Rocket Pool (rETH) Mechanics](#4-rocket-pool-reth-mechanics)
5. [stETH/ETH Peg Dynamics](#5-stetheth-peg-dynamics)
6. [Restaking — EigenLayer](#6-restaking--eigenlayer)
7. [Yield Stacking Strategies](#7-yield-stacking-strategies)
8. [Risk Analysis](#8-risk-analysis)
9. [Mathematical Yield Models](#9-mathematical-yield-models)
10. [Integration with Other DeFi Strategies](#10-integration-with-other-defi-strategies)
11. [Execution Flow — Staking Management Bot](#11-execution-flow--staking-management-bot)
12. [Risk Parameters](#12-risk-parameters)
13. [References](#13-references)

---

## 1. Introduction to Liquid Staking

### 1.1 The Problem with Native Staking

Ethereum's Proof of Stake requires validators to lock 32 ETH. This creates problems:

| Problem                    | Impact                                    |
|----------------------------|-------------------------------------------|
| Capital lock-up            | 32 ETH locked, cannot use in DeFi         |
| High minimum               | Most users cannot afford 32 ETH           |
| Technical complexity       | Running a validator requires infrastructure|
| Unbonding period           | Withdrawal queue can take days/weeks       |
| Opportunity cost           | Locked ETH cannot earn DeFi yields        |

### 1.2 Liquid Staking Solution

Liquid staking solves all of these problems:

```
Traditional Staking:
  User → Lock 32 ETH → Earn staking yield → Cannot use ETH

Liquid Staking:
  User → Deposit any amount of ETH → Receive liquid token (stETH/rETH)
       → Earn staking yield + Use liquid token in DeFi
```

The liquid staking token (LST) represents the staked ETH plus accumulated rewards.
It can be:
- Traded on DEXes.
- Used as collateral in lending protocols.
- Deployed in liquidity pools.
- Used in yield farming strategies.

### 1.3 Liquid Staking Market Overview

| Protocol       | Token | Market Share (approx.) | Mechanism          | Decentralization |
|----------------|-------|------------------------|--------------------|------------------|
| Lido           | stETH | ~30% of staked ETH     | Rebasing           | Medium           |
| Rocket Pool    | rETH  | ~3-5%                  | Exchange rate       | High             |
| Coinbase       | cbETH | ~8-12%                 | Exchange rate       | Low (centralized)|
| Frax           | sfrxETH| ~2-3%                 | Exchange rate       | Medium           |
| Mantle         | mETH  | ~2-3%                  | Exchange rate       | Medium           |
| Binance        | BETH  | ~5%                    | Exchange rate       | Low (centralized)|
| EtherFi        | eETH  | ~3-5%                  | Rebasing (restaked) | High             |

### 1.4 Why Liquid Staking Matters for the Trading System

1. **Base yield layer**: ~3-5% APR risk-free (relative to ETH).
2. **Capital efficiency**: Staked ETH remains productive in DeFi.
3. **Composability**: LSTs integrate into all DeFi protocols.
4. **Yield stacking**: Layer additional yields on top of staking yield.
5. **Arbitrage**: stETH/ETH peg deviations create trading opportunities.

---

## 2. Ethereum Staking Fundamentals

### 2.1 Staking Yield Sources

Ethereum validators earn from two sources:

$$
Y_{staking} = Y_{consensus} + Y_{execution}
$$

**Consensus Layer Yield** (predictable):
- Block attestation rewards.
- Block proposal rewards.
- Sync committee rewards.

$$
Y_{consensus} = f\left(\frac{1}{\sqrt{N_{validators}}}\right) \approx \frac{C}{\sqrt{\text{Total ETH Staked}}}
$$

Where $C$ is a protocol constant. As more ETH is staked, per-validator rewards decrease.

**Execution Layer Yield** (variable):
- Transaction priority fees (tips).
- MEV (Maximal Extractable Value) captured via MEV-Boost.

$$
Y_{execution} = \frac{\text{Total Priority Fees} + \text{MEV}}{\text{Total Staked ETH}}
$$

### 2.2 Current Yield Breakdown (Approximate)

| Source              | APR (approx.) | Variability  | Description                |
|---------------------|---------------|--------------|----------------------------|
| Consensus rewards   | 2.5-3.5%      | Low          | Based on total staked      |
| Priority fees       | 0.3-1.0%      | Medium       | Based on network activity  |
| MEV                 | 0.5-1.5%      | High         | Based on DeFi activity     |
| **Total**           | **3.5-5.5%**  | Medium       | Varies with market conditions |

### 2.3 Validator Economics

$$
\text{Annual Revenue per Validator} = 32 \times Y_{staking} \times \text{ETH Price}
$$

$$
\text{Annual Cost per Validator} = \text{Infrastructure} + \text{Opportunity Cost} + \text{Slashing Risk}
$$

---

## 3. Lido (stETH) Mechanics

### 3.1 How Lido Works

```
Lido Architecture:
┌─────────────────────────────────────────────┐
│                  Lido Protocol                │
│                                             │
│  User deposits ETH                          │
│       │                                     │
│       ▼                                     │
│  ┌──────────────┐                           │
│  │ stETH Token  │ ← Minted 1:1 at deposit  │
│  │ (Rebasing)   │                           │
│  └──────────────┘                           │
│       │                                     │
│       ▼ (behind the scenes)                 │
│  ┌──────────────┐    ┌────────────────────┐ │
│  │ Node Operator │    │ Node Operator      │ │
│  │ Set (Curated) │    │ Set (DVT Module)   │ │
│  └──────────────┘    └────────────────────┘ │
│       │                                     │
│       ▼                                     │
│  Ethereum Beacon Chain (32 ETH validators)  │
│                                             │
│  Fee: 10% of staking rewards               │
│    └── 5% to node operators                 │
│    └── 5% to Lido DAO treasury              │
│                                             │
└─────────────────────────────────────────────┘
```

### 3.2 stETH Rebasing Mechanism

stETH uses a **rebasing** mechanism: the token balance in your wallet increases daily
to reflect earned staking rewards.

$$
\text{stETH Balance}(t+1) = \text{stETH Balance}(t) \times (1 + r_{daily})
$$

Where $r_{daily}$ is the daily staking reward rate (after Lido's 10% fee):

$$
r_{daily} = \frac{Y_{staking} \times 0.90}{365}
$$

**Example**: If annual staking yield is 4% and Lido takes 10%:
$$
r_{daily} = \frac{0.04 \times 0.90}{365} = 0.00986\% \text{ per day}
$$

For 1000 stETH, daily increase: $1000 \times 0.0000986 = 0.0986$ stETH

### 3.3 wstETH (Wrapped stETH)

Since rebasing tokens are incompatible with some DeFi protocols, Lido offers
**wstETH** — a wrapped version with an increasing exchange rate:

$$
\text{wstETH/stETH rate} = \frac{\text{Total stETH Shares}}{\text{Total stETH Supply}} = \frac{1}{\text{stETH per share}}
$$

wstETH balance stays constant, but each wstETH is worth more stETH over time:

$$
\text{Value in ETH}(t) = \text{wstETH amount} \times \text{wstETH/stETH rate}(t)
$$

| Token  | Balance Changes? | How Yield Accumulates    | DeFi Compatibility |
|--------|-----------------|--------------------------|---------------------|
| stETH  | Yes (rebases)   | Balance increases daily   | Limited (some incompatible) |
| wstETH | No (constant)   | Exchange rate increases   | Full (standard ERC-20)     |

### 3.4 Lido Withdrawal Process

Since the Shanghai/Capella upgrade (April 2023), stETH can be redeemed for ETH:

```
Withdrawal Options:
1. Direct redemption via Lido (queue-based)
   - Submit stETH to withdrawal queue
   - Wait 1-5 days (depends on queue length)
   - Claim ETH at 1:1 ratio

2. Market swap on DEX (instant)
   - Swap stETH -> ETH on Curve, Uniswap, etc.
   - Usually at slight discount (0-0.3%)
   - Instant, no waiting period
```

### 3.5 Lido Fee Structure

$$
\text{Net Yield to stETH Holders} = Y_{total} \times (1 - 0.10)
$$

- 5% to node operators (compensation for running infrastructure)
- 5% to Lido DAO treasury (protocol development, insurance)
- 90% to stETH holders (via daily rebase)

---

## 4. Rocket Pool (rETH) Mechanics

### 4.1 How Rocket Pool Works

Rocket Pool is a **decentralized** liquid staking protocol where anyone can become a
node operator (with lower minimum: 8 ETH instead of 32 ETH).

```
Rocket Pool Architecture:
┌─────────────────────────────────────────────────────┐
│                   Rocket Pool                        │
│                                                     │
│  Regular User (depositor):                          │
│    Deposits ETH → Receives rETH                     │
│                                                     │
│  Node Operator:                                     │
│    Deposits 8 ETH + RPL bond → Creates minipool     │
│    Protocol adds 24 ETH from deposit pool           │
│    Total: 32 ETH validator                          │
│                                                     │
│  ┌─────────────────────────────────────────────┐    │
│  │              Minipool (32 ETH)               │    │
│  │  8 ETH (node operator) + 24 ETH (protocol)  │    │
│  │  Node operator earns commission on the 24    │    │
│  └─────────────────────────────────────────────┘    │
│                                                     │
│  Fee: Variable commission (node operators set 5-20%)│
│    └── Commission on the rETH stakers' share only   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 4.2 rETH Exchange Rate Model

rETH does NOT rebase. Instead, its exchange rate against ETH increases:

$$
\text{rETH/ETH Rate}(t) = \text{rETH/ETH Rate}(t_0) \times \left(1 + \frac{Y_{net}}{365}\right)^{\Delta t_{days}}
$$

$$
\text{rETH/ETH Rate} = \frac{\text{Total ETH in Protocol (staked + rewards)}}{\text{Total rETH Supply}}
$$

The rate only increases (barring slashing events), making rETH an appreciating asset.

### 4.3 rETH vs stETH Comparison

| Feature                | stETH (Lido)           | rETH (Rocket Pool)      |
|------------------------|------------------------|-------------------------|
| Yield mechanism        | Rebasing (balance up)  | Exchange rate increases  |
| DeFi compatibility     | Needs wrapping (wstETH)| Native (no wrapping)     |
| Node operators         | Curated (permissioned) | Permissionless           |
| Decentralization       | Medium                 | High                    |
| Commission             | Fixed 10%              | Variable 5-20%          |
| Liquidity (DEX)        | Very high              | Medium                  |
| Insurance/Bond         | Lido DAO covers        | RPL bond per node op    |
| Smart contract risk    | Large, complex         | Large, complex           |

### 4.4 RPL Token Economics

Node operators must bond RPL tokens (minimum 10% of borrowed ETH value):

$$
\text{Min RPL Bond} = 0.10 \times 24 \text{ ETH} \times \frac{P_{ETH}}{P_{RPL}}
$$

RPL serves as:
- Insurance against slashing (RPL is sold to cover losses).
- Incentive alignment (node operators have skin in the game).
- Governance token.

---

## 5. stETH/ETH Peg Dynamics

### 5.1 Why stETH Trades at a Discount/Premium

The stETH/ETH exchange rate on secondary markets (Curve, Uniswap) can deviate
from the protocol's 1:1 redemption rate.

**Factors causing discount (stETH < ETH)**:
- Large withdrawals / forced selling (e.g., 3AC collapse in 2022).
- Smart contract fear events.
- Withdrawal queue length (opportunity cost of waiting).
- General market fear / risk-off sentiment.

**Factors causing premium (stETH > ETH) — rare**:
- Extremely high demand for stETH in DeFi.
- Deposit queue (cannot mint new stETH fast enough).
- Short squeeze (shorts forced to buy stETH).

### 5.2 Historical Peg Deviations

| Event                    | Date     | Max Discount | Duration      | Cause           |
|--------------------------|----------|--------------|---------------|-----------------|
| 3AC / Luna collapse      | Jun 2022 | -5 to -7%   | ~3 months     | Forced selling  |
| FTX collapse             | Nov 2022 | -2 to -3%   | ~1 month      | Market fear     |
| Normal range (post-Shanghai)| Ongoing| -0.1 to +0.1%| Persistent | Market efficiency|
| Regulatory fear events   | Various  | -0.5 to -1% | Days          | News-driven     |

### 5.3 Peg Arbitrage Mechanism

The peg is maintained by arbitrageurs:

**When stETH trades at discount** (e.g., 0.97 ETH per stETH):
1. Buy stETH at 0.97 ETH on Curve.
2. Redeem stETH via Lido withdrawal queue (1:1 = 1.0 ETH).
3. Wait for withdrawal (~1-5 days).
4. Profit: 3% minus opportunity cost of waiting.

**When stETH trades at premium** (rare, e.g., 1.01 ETH per stETH):
1. Deposit ETH in Lido (receive stETH at 1:1).
2. Sell stETH on Curve at 1.01 ETH.
3. Profit: 1% immediately.

### 5.4 Peg Trading Strategy for the Bot

```python
class StETHPegArbitrage:
    """
    Monitor stETH/ETH peg and execute arbitrage when opportunities arise.
    """

    def __init__(self, config):
        self.min_discount = 0.005  # 0.5% minimum discount to trigger
        self.max_discount = 0.03   # Above 3% = potential smart contract risk
        self.withdrawal_queue_max = 7  # days
        self.min_profit_after_costs = 0.003  # 0.3% min net profit

    async def check_peg_opportunity(self) -> Optional[PegArbitrageOpp]:
        """Check if stETH/ETH peg offers arbitrage opportunity."""

        # Get market price (Curve, Uniswap)
        market_rate = await self.get_market_rate('stETH', 'ETH')

        # Get redemption rate (always 1:1 via protocol withdrawal)
        protocol_rate = 1.0

        # Calculate discount
        discount = 1 - market_rate  # Positive = stETH cheaper than ETH

        if discount > self.max_discount:
            # Too large a discount might indicate real risk
            logger.warning(f"stETH discount {discount:.2%} exceeds safety limit")
            return None

        if discount < self.min_discount:
            return None  # Not enough discount to be profitable

        # Check withdrawal queue length
        queue_length_days = await self.get_lido_withdrawal_queue_time()
        if queue_length_days > self.withdrawal_queue_max:
            return None  # Queue too long

        # Calculate opportunity cost of waiting
        opportunity_cost = self.get_risk_free_rate() * queue_length_days / 365

        # Calculate gas costs
        gas_cost_pct = await self.estimate_gas_cost_pct()

        # Net profit
        net_profit = discount - opportunity_cost - gas_cost_pct

        if net_profit > self.min_profit_after_costs:
            return PegArbitrageOpp(
                discount=discount,
                queue_time=queue_length_days,
                net_profit=net_profit,
                strategy="buy_discount_redeem"
            )

        return None

    async def execute_peg_arbitrage(self, opp: PegArbitrageOpp):
        """Execute peg arbitrage."""

        # Determine position size
        max_size = self.config.max_position_size
        available = await self.get_available_eth()
        size = min(max_size, available)

        if opp.strategy == "buy_discount_redeem":
            # Step 1: Buy stETH on Curve at discount
            steth_received = await self.swap_on_curve(
                token_in='ETH',
                token_out='stETH',
                amount=size,
                min_out=size * (1 + opp.discount * 0.9)  # 90% of discount as min
            )

            # Step 2: Submit to Lido withdrawal queue
            request_id = await self.lido_withdrawal.request_withdrawal(steth_received)

            # Step 3: Record position for monitoring
            self.positions.add(PegArbPosition(
                request_id=request_id,
                eth_spent=size,
                steth_amount=steth_received,
                expected_return=steth_received * 1.0,  # 1:1 redemption
                expected_profit=steth_received - size,
                submitted_at=time.time()
            ))

            logger.info(f"Peg arbitrage: spent {size:.4f} ETH, "
                       f"received {steth_received:.4f} stETH, "
                       f"expected profit: {steth_received - size:.4f} ETH")
```

### 5.5 stETH in DeFi (Composability)

stETH is widely integrated:

| Protocol    | Use Case                         | Yield Layer                     |
|-------------|-----------------------------------|---------------------------------|
| Aave V3     | Collateral for borrowing         | Staking yield + borrow utility  |
| Curve       | stETH/ETH LP                     | Staking yield + LP fees + CRV  |
| Uniswap V3  | wstETH/ETH concentrated LP       | Staking yield + LP fees         |
| Pendle      | Split into PT-stETH + YT-stETH  | Fixed vs variable yield trading |
| EigenLayer  | Restaked for additional yield     | Staking + restaking yield       |
| Lybra       | Collateral for eUSD stablecoin   | Staking yield + minting utility |

---

## 6. Restaking — EigenLayer

### 6.1 What Is Restaking?

Restaking allows staked ETH (or LSTs) to simultaneously secure additional protocols
beyond Ethereum itself. These additional protocols are called **Actively Validated
Services (AVSs)**.

```
Traditional Staking:
  32 ETH → Secures Ethereum only → Earns staking yield

Restaking:
  32 ETH → Secures Ethereum + AVS 1 + AVS 2 + ... → Earns staking yield + AVS rewards
```

### 6.2 EigenLayer Architecture

```
┌──────────────────────────────────────────────────┐
│                  EigenLayer                        │
│                                                  │
│  Restakers (deposit ETH/LSTs)                    │
│       │                                          │
│       ▼                                          │
│  ┌────────────────┐                              │
│  │ EigenLayer     │                              │
│  │ Smart Contracts│                              │
│  └────────────────┘                              │
│       │                                          │
│       ▼ (Delegation)                             │
│  ┌────────────────┐                              │
│  │ Operators      │  ← Run infrastructure        │
│  │ (node runners) │    for multiple AVSs          │
│  └────────────────┘                              │
│       │                                          │
│       ▼ (Validation)                             │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐      │
│  │  AVS 1    │ │  AVS 2    │ │  AVS 3    │      │
│  │ (Oracle)  │ │ (Bridge)  │ │ (DA Layer)│      │
│  └───────────┘ └───────────┘ └───────────┘      │
│                                                  │
│  Slashing: If operator misbehaves on any AVS,   │
│  their staked ETH can be slashed                 │
│                                                  │
└──────────────────────────────────────────────────┘
```

### 6.3 Types of Restaking

| Type                   | Asset Restaked        | Process                         |
|------------------------|----------------------|----------------------------------|
| Native Restaking       | ETH (via validators) | Point Ethereum withdrawal credentials to EigenPod |
| LST Restaking          | stETH, rETH, etc.   | Deposit LSTs into EigenLayer contracts |
| LP Restaking           | LP tokens            | Deposit LP tokens (if approved)  |

### 6.4 AVS (Actively Validated Service) Examples

| AVS Type         | Example           | What It Validates              | Potential Yield |
|------------------|-------------------|--------------------------------|-----------------|
| Oracle network   | Chainlink-like    | Price feeds                    | 1-5% APR       |
| Data availability| EigenDA           | Data blobs for rollups         | 2-6% APR       |
| Bridge           | Cross-chain bridge| Cross-chain message validity   | 3-8% APR       |
| Sequencer        | Decentralized seq.| Transaction ordering            | 2-5% APR       |
| Keeper network   | Automation        | Condition execution             | 1-3% APR       |

### 6.5 Restaking Yield Model

$$
Y_{restaking} = Y_{staking} + \sum_{j=1}^{M} Y_{AVS_j} \times w_j
$$

Where:
- $Y_{staking}$ = base Ethereum staking yield (~3.5-5%)
- $Y_{AVS_j}$ = yield from AVS $j$
- $w_j$ = proportion of stake delegated to AVS $j$
- $M$ = number of AVSs the operator validates

**Total yield projection**:

| Component        | APR Range | Confidence |
|------------------|-----------|------------|
| ETH staking      | 3.5-5.0%  | High       |
| AVS rewards (aggregate) | 2-10% | Medium  |
| **Total**        | **5.5-15%** | Medium   |

### 6.6 Slashing Risk in Restaking

Each AVS introduces additional slashing conditions:

$$
P_{slash} = 1 - \prod_{j=0}^{M} (1 - P_{slash,j})
$$

Where:
- $P_{slash,0}$ = probability of Ethereum consensus slashing
- $P_{slash,j}$ = probability of slashing on AVS $j$

| # AVSs | Individual P(slash) | Combined P(slash) |
|---------|--------------------|--------------------|
| 1 (ETH only) | 0.1%        | 0.1%               |
| 2       | 0.1% each          | 0.20%              |
| 5       | 0.1% each          | 0.50%              |
| 10      | 0.1% each          | 1.00%              |
| 5       | 0.5% each          | 2.47%              |

Risk compounds with more AVSs. Each additional AVS adds marginal risk.

### 6.7 Liquid Restaking Tokens (LRTs)

Protocols like EtherFi, Renzo, and Puffer create liquid representations of restaked ETH:

| Protocol | Token  | Mechanism                                   |
|----------|--------|---------------------------------------------|
| EtherFi  | eETH   | Native restaking with liquid wrapper         |
| Renzo    | ezETH  | Multi-AVS restaking strategy                 |
| Puffer   | pufETH | Anti-slashing technology + restaking         |
| Kelp     | rsETH  | LST restaking aggregator                     |

$$
\text{LRT Value} = \text{Underlying ETH} + \text{Accrued Staking Rewards} + \text{Accrued AVS Rewards} - \text{Slashing Events}
$$

---

## 7. Yield Stacking Strategies

### 7.1 Concept

Yield stacking = layering multiple yield sources on the same capital:

```
Layer 0: Hold ETH (no yield, price exposure only)
Layer 1: Stake ETH (staking yield: +3.5-5%)
Layer 2: Restake (AVS rewards: +2-10%)
Layer 3: Use in DeFi (LP fees, lending interest: +2-20%)
Layer 4: Earn protocol incentives (token rewards: variable)
```

### 7.2 Strategy 1: stETH Leveraged Staking

```
1. Hold 100 ETH
2. Stake via Lido → 100 stETH (earning 3.5% staking yield)
3. Deposit stETH in Aave as collateral
4. Borrow ETH (85% LTV in E-Mode) → 85 ETH
5. Stake borrowed ETH → 85 stETH
6. Repeat (or use flash loan for instant)

Effective position:
  Total stETH: ~667 stETH (6.67x leverage in E-Mode)
  Total ETH debt: ~567 ETH
  Net staking yield: (667 × 3.5%) - (567 × borrow_rate_ETH%)
```

**Net yield calculation**:

$$
Y_{net} = \frac{V_0}{1-l} \times Y_{staking} - \frac{V_0 \times l}{1-l} \times R_{borrow,ETH}
$$

Where $l$ = LTV used (e.g., 0.85 in E-Mode).

For E-Mode with 85% LTV:
$$
Y_{net} = V_0 \times \frac{Y_{staking} - 0.85 \times R_{borrow}}{1 - 0.85} = V_0 \times \frac{Y_{staking} - 0.85 \times R_{borrow}}{0.15}
$$

If $Y_{staking} = 3.5\%$ and $R_{borrow} = 2.5\%$:
$$
Y_{net} = V_0 \times \frac{0.035 - 0.85 \times 0.025}{0.15} = V_0 \times \frac{0.01375}{0.15} = V_0 \times 9.17\%
$$

### 7.3 Strategy 2: Restaked + DeFi Yield

```
1. Deposit 100 ETH into EtherFi → 100 eETH (staking + restaking yield)
2. Wrap eETH → weETH (non-rebasing)
3. Deposit weETH into Aave as collateral
4. Borrow USDC against weETH
5. Deploy USDC into Curve/Uniswap stable pools

Yield layers:
  Layer 1: ETH staking yield (~4%)
  Layer 2: EigenLayer AVS rewards (~3-5%)
  Layer 3: EtherFi loyalty points (speculative)
  Layer 4: Aave borrowing (negative, cost ~4-5%)
  Layer 5: Curve stable LP (~3-8%)
  Net: Approximately 6-12% total (net of borrow costs)
```

### 7.4 Strategy 3: Pendle Yield Tokenization

```
1. Deposit 100 stETH into Pendle
2. Split into:
   - PT-stETH (Principal Token): Fixed yield, matures at expiry
   - YT-stETH (Yield Token): Variable yield until expiry

Strategy A — Fixed Yield Seeker:
  Buy PT-stETH at discount → Redeem at maturity for full stETH
  Example: Buy at 0.95 stETH, receive 1.0 stETH at maturity (6 months)
  Fixed APR: (1/0.95 - 1) × 2 = ~10.5% annualized

Strategy B — Yield Speculator:
  Buy YT-stETH → Earn all staking yield until maturity
  If staking yield increases → YT value increases
  Leveraged bet on future yield rates

Strategy C — Yield Hedging:
  Sell YT-stETH → Lock in current yield level
  Immunize against yield decline
```

### 7.5 Strategy 4: wstETH/ETH Concentrated Liquidity

```
1. Hold 100 ETH worth of assets
2. Split: 50 ETH + 50 wstETH
3. Provide concentrated liquidity in Uniswap V3 wstETH/ETH pool
4. Set very tight range (wstETH/ETH rate is very stable, moves slowly)
   Range: [current_rate - 0.5%, current_rate + 0.5%]
5. Earn:
   - LP trading fees (concentrated = high capital efficiency)
   - stETH staking yield (on the wstETH portion)
   - Minimal IL (correlated pair)

Net yield: Staking yield + concentrated LP fees - minimal gas
Estimated: 5-12% APR
```

### 7.6 Strategy 5: Full Stack (Maximum Yield)

```
1. ETH → Lido → stETH (staking yield)
2. stETH → EigenLayer (restaking yield)
3. Receive liquid restaking token (LRT)
4. LRT → Pendle (split into PT + YT)
5. Sell YT for immediate cash (lock in future yield)
6. PT → Aave collateral → Borrow USDC
7. USDC → Curve stable LP (fees + CRV)

Yield layers:
  - ETH staking: ~4%
  - Restaking: ~3%
  - YT sale premium: ~5% (one-time, amortized)
  - Curve LP: ~4% (on borrowed USDC)
  - CRV incentives: ~2%
  Total: ~18% APR (before costs)
  Costs: Borrow rate (~4%), gas, smart contract risk premium
  Net: ~10-14% APR
```

### 7.7 Strategy Comparison Matrix

| Strategy                  | Expected APR | Risk Level | Complexity | Capital Required |
|---------------------------|-------------|------------|------------|------------------|
| Simple stETH hold         | 3.5-5%      | Low        | Very Low   | Any              |
| Leveraged stETH (E-Mode)  | 8-12%       | Medium     | Medium     | > $10K           |
| Restaked + DeFi           | 6-12%       | Medium-High| High       | > $10K           |
| Pendle fixed yield        | 5-15%       | Low-Medium | Medium     | > $5K            |
| wstETH/ETH conc. LP      | 5-12%       | Low-Medium | Medium     | > $10K           |
| Full stack                | 10-18%      | High       | Very High  | > $50K           |

---

## 8. Risk Analysis

### 8.1 Smart Contract Risk

| Protocol      | Risk Level | Contracts | Audit Status           | Historical Issues    |
|---------------|------------|-----------|------------------------|---------------------|
| Lido          | Medium     | Complex   | Multiple audits, bug bounty | None critical    |
| Rocket Pool   | Medium     | Complex   | Multiple audits        | Minor issues fixed  |
| EigenLayer    | High       | Very complex | Audited, but newer   | No exploits (young) |
| EtherFi      | Medium-High| Complex   | Audited                | No exploits (young) |
| Pendle        | Medium     | Moderate  | Multiple audits        | No exploits         |

### 8.2 Slashing Risk

$$
\text{Expected Loss from Slashing} = P_{slash} \times L_{slash} \times V_{staked}
$$

Where:
- $P_{slash}$ = probability of slashing event per year
- $L_{slash}$ = loss given slashing (fraction of stake lost)
- $V_{staked}$ = value of staked assets

| Risk Type               | P (per year) | Loss Given Event | Expected Annual Loss |
|-------------------------|-------------|------------------|---------------------|
| ETH consensus slash     | 0.01%       | 1-32 ETH (min-max)| 0.001-0.032 ETH   |
| Lido operator slash     | 0.05%       | Covered by insurance| ~0 (socialized)  |
| EigenLayer AVS slash    | 0.1-1%      | Variable (AVS-defined)| 0.1-5% per AVS |

### 8.3 De-Peg Risk

LSTs can trade below fair value during stress:

$$
\text{De-peg Loss} = V_{position} \times |\text{Discount}| \times \mathbf{1}_{forced\_sell}
$$

De-peg only matters if you are forced to sell at the discounted price. If you can
wait for withdrawal queue redemption, the loss is only opportunity cost.

**Maximum historical de-peg**: stETH reached ~7% discount in June 2022.

### 8.4 Leverage-Specific Risks

For leveraged staking strategies:

$$
\text{Liquidation Price} = P_{entry} \times \frac{LT}{l \times HF_{initial}}
$$

For stETH/ETH E-Mode (LT = 95%, initial LTV = 85%):
- HF at entry: $0.95/0.85 = 1.118$
- Liquidation at: stETH/ETH drops to $1/1.118 = 0.894$ (10.6% de-peg)

Since max historical de-peg was ~7%, this has a buffer but is not risk-free.

### 8.5 Risk Mitigation Strategies

```
For the Trading System:

1. DIVERSIFY across LSTs (don't only use Lido)
   - 50% stETH (most liquid, largest)
   - 30% rETH (most decentralized)
   - 20% other (cbETH, sfrxETH)

2. LIMIT leverage on staking positions
   - Max leverage for stETH/ETH: 4x (conservative)
   - Max leverage for LRT/ETH: 2x (newer protocols)

3. MONITOR de-peg risk
   - Alert at 0.5% discount
   - Reduce leverage at 1% discount
   - Exit leveraged positions at 2% discount

4. DIVERSIFY restaking across operators/AVSs
   - No single operator > 20% of restaked capital
   - No single AVS > 30% of restaking exposure

5. MAINTAIN withdrawal options
   - Always have path to exit within 7 days
   - Keep 10% in liquid ETH for emergencies
```

---

## 9. Mathematical Yield Models

### 9.1 Total Staking Yield Model

$$
Y_{total} = \frac{C_1}{\sqrt{E_{staked}}} + \frac{F_{priority} + MEV}{E_{staked}}
$$

Where:
- $C_1$ = consensus reward constant
- $E_{staked}$ = total ETH staked across the network
- $F_{priority}$ = total annual priority fees
- $MEV$ = total annual MEV captured

As more ETH is staked, consensus yield decreases (dilution), but execution yield
is independent of stake amount (it depends on network activity).

### 9.2 Leveraged Staking Yield Model

For leverage multiple $m$ with borrow rate $R_b$:

$$
Y_{leveraged} = m \cdot Y_{staking} - (m-1) \cdot R_b
$$

$$
\text{Leverage Multiplier on Yield} = \frac{Y_{leveraged}}{Y_{staking}} = m - (m-1) \cdot \frac{R_b}{Y_{staking}}
$$

**Break-even leverage** (where leveraged yield = unleveraged yield):

$$
m_{break-even} = \frac{Y_{staking}}{Y_{staking} - R_b}
$$

If $Y_{staking} < R_b$, leveraged staking is always worse than unleveraged.

### 9.3 Restaking Yield Model

$$
Y_{restaking} = Y_{staking} + \sum_{j=1}^{M} r_j \times (1 - P_{slash,j} \times L_j) - C_{gas}
$$

Where:
- $r_j$ = reward rate from AVS $j$
- $P_{slash,j}$ = slashing probability for AVS $j$
- $L_j$ = loss given slashing event on AVS $j$
- $C_{gas}$ = gas cost of claiming rewards

**Risk-adjusted restaking yield**:

$$
Y_{risk-adj} = Y_{staking} + \sum_j r_j - \sum_j P_{slash,j} \cdot L_j \cdot V_{staked} / V_{staked} - C_{gas}
$$

### 9.4 Yield Stacking Compound Model

For a full-stack strategy with $N$ layers:

$$
Y_{total} = \sum_{i=1}^{N} Y_i \times E_i - \sum_{i=1}^{N} C_i
$$

Where:
- $Y_i$ = yield from layer $i$
- $E_i$ = effective exposure (can be > 1x with leverage)
- $C_i$ = cost of layer $i$ (gas, borrow cost, fees)

### 9.5 Optimal Leverage Given Yield Spread

$$
m^* = \argmax_m \frac{m \cdot Y_{staking} - (m-1) \cdot R_b}{\sqrt{m^2 \cdot \sigma_{staking}^2 + (m-1)^2 \cdot \sigma_{borrow}^2}}
$$

This is the Sharpe-optimal leverage, balancing return enhancement with risk increase.

For the simplified case where risk is proportional to leverage:

$$
m^* = \frac{Y_{staking} - R_b}{\sigma^2}
$$

### 9.6 APR to Final Value

For a staking position over time $T$ years:

$$
V(T) = V_0 \times e^{Y_{net} \times T} \quad \text{(continuous compounding)}
$$

For leveraged staking:

$$
V(T) = V_0 \times e^{(m \cdot Y_{staking} - (m-1) \cdot R_b) \times T}
$$

**Example**: $100K at 9% net leveraged yield for 1 year:

$$
V(1) = 100,000 \times e^{0.09} = \$109,417
$$

---

## 10. Integration with Other DeFi Strategies

### 10.1 Staking + LP Strategy

Combine staking yield with LP fees:

```
Portfolio:
├── 40% — wstETH/ETH Uniswap V3 LP (tight range)
│   Yield: Staking (3.5%) + LP fees (3-8%) = 6.5-11.5%
│   Risk: Minimal IL (correlated pair), smart contract
│
├── 30% — stETH as Aave collateral → borrow USDC → Curve stable LP
│   Yield: Staking (3.5%) - borrow (4%) + Curve (5-8%) = 4.5-7.5%
│   Risk: Liquidation if stETH de-pegs, IL on Curve
│
├── 20% — Pendle PT-stETH (fixed yield)
│   Yield: Fixed 6-10% APR (locked at purchase)
│   Risk: Smart contract, cannot exit before maturity easily
│
└── 10% — Liquid stETH (reserve)
    Yield: Staking only (3.5%)
    Risk: Minimal (just holding stETH)
```

### 10.2 Staking + Lending Optimization

```python
class StakingLendingOptimizer:
    """
    Optimize the combination of staking and lending strategies.
    """

    def calculate_optimal_allocation(
        self,
        capital_eth: float,
        staking_yield: float,
        borrow_rate_eth: float,
        stable_supply_rate: float,
        lp_expected_yield: float,
        e_mode_ltv: float = 0.90
    ) -> AllocationPlan:
        """
        Determine optimal split between:
        1. Pure staking (stETH hold)
        2. Leveraged staking (stETH → Aave → borrow ETH → more stETH)
        3. Staking + stable yield (stETH → Aave → borrow USDC → stable LP)
        """

        # Option 1: Pure staking
        yield_pure = staking_yield

        # Option 2: Leveraged staking
        max_leverage = 1 / (1 - e_mode_ltv)  # 10x for 90% LTV
        safe_leverage = min(max_leverage * 0.6, 5)  # Use 60% of max, cap at 5x
        yield_leveraged = safe_leverage * staking_yield - \
                         (safe_leverage - 1) * borrow_rate_eth

        # Option 3: Staking + stable yield
        borrow_capacity_usd = capital_eth * e_mode_ltv * 0.7  # Conservative
        yield_hybrid = staking_yield + \
                      (borrow_capacity_usd / capital_eth) * \
                      (stable_supply_rate - borrow_rate_eth)

        # Option 4: Staking + LP
        yield_lp = staking_yield * 0.5 + lp_expected_yield  # Half in LP

        # Pick best risk-adjusted option
        options = {
            "pure_staking": {"yield": yield_pure, "risk": 0.1},
            "leveraged_staking": {"yield": yield_leveraged, "risk": 0.4},
            "hybrid_stable": {"yield": yield_hybrid, "risk": 0.3},
            "staking_lp": {"yield": yield_lp, "risk": 0.35},
        }

        # Risk-adjusted yields
        for name, opt in options.items():
            opt["risk_adjusted"] = opt["yield"] * (1 - opt["risk"])

        best = max(options.items(), key=lambda x: x[1]["risk_adjusted"])

        return AllocationPlan(
            strategy=best[0],
            expected_yield=best[1]["yield"],
            risk_adjusted_yield=best[1]["risk_adjusted"],
            risk_level=best[1]["risk"]
        )
```

### 10.3 Integration Risk Matrix

| Combined Strategy            | Additional Risks                    | Mitigation           |
|------------------------------|-------------------------------------|----------------------|
| stETH + Aave                 | De-peg liquidation                  | Lower LTV, monitor   |
| Restaked + Pendle            | Smart contract (2 protocols)        | Audit checks         |
| Leveraged staking + LP      | Liquidation + IL                    | Conservative leverage|
| LRT + Aave + Curve           | 4 protocol risk layers              | Small allocation     |
| Full stack (5+ layers)       | Compounding smart contract risk     | Max 5% of portfolio  |

---

## 11. Execution Flow — Staking Management Bot

### 11.1 Complete Staking Bot

```python
class StakingManagementBot:
    """
    Manages liquid staking, restaking, and yield stacking positions.
    """

    def __init__(self, config: StakingConfig):
        self.lido = LidoClient(config.lido)
        self.rocket_pool = RocketPoolClient(config.rocket_pool)
        self.eigenlayer = EigenLayerClient(config.eigenlayer)
        self.pendle = PendleClient(config.pendle)
        self.aave = AaveClient(config.aave)
        self.oracle = PriceOracle()
        self.risk_manager = StakingRiskManager(config.risk)
        self.positions = StakingPortfolio()

    async def main_loop(self):
        """Main staking management loop."""
        while True:
            try:
                # ==========================================
                # PHASE 1: MONITOR EXISTING POSITIONS
                # ==========================================
                await self.monitor_staking_positions()
                await self.monitor_peg_health()
                await self.monitor_restaking_positions()

                # ==========================================
                # PHASE 2: YIELD OPTIMIZATION
                # ==========================================
                current_yields = await self.get_all_current_yields()
                optimal_allocation = self.calculate_optimal_allocation(current_yields)

                # Check if rebalancing is needed
                if self.should_rebalance(optimal_allocation):
                    await self.rebalance_staking_portfolio(optimal_allocation)

                # ==========================================
                # PHASE 3: PEG ARBITRAGE
                # ==========================================
                peg_opps = await self.scan_peg_opportunities()
                for opp in peg_opps:
                    if opp.net_profit > self.config.min_arb_profit:
                        await self.execute_peg_arbitrage(opp)

                # ==========================================
                # PHASE 4: REWARD MANAGEMENT
                # ==========================================
                await self.claim_and_compound_rewards()

                # ==========================================
                # PHASE 5: WITHDRAWAL QUEUE MANAGEMENT
                # ==========================================
                await self.manage_withdrawal_requests()

                await asyncio.sleep(self.config.check_interval)

            except Exception as e:
                logger.error(f"Staking bot error: {e}")
                await self.alert_system.notify(e)

    async def monitor_peg_health(self):
        """Monitor LST/ETH pegs for risk."""
        pegs = {
            "stETH": await self.get_market_price("stETH", "ETH"),
            "rETH": await self.get_market_price("rETH", "ETH"),
            "eETH": await self.get_market_price("eETH", "ETH"),
        }

        for token, market_price in pegs.items():
            fair_value = await self.get_fair_value(token)
            discount = 1 - market_price / fair_value

            if discount > 0.02:  # > 2% discount
                logger.warning(f"{token} de-pegging: {discount:.2%} discount")

                # If we have leveraged positions using this token
                affected = self.positions.get_positions_using(token)
                for pos in affected:
                    if pos.is_leveraged:
                        await self.reduce_leverage_on_depeg(pos, discount)

            elif discount > 0.005:  # > 0.5% discount (opportunity)
                logger.info(f"{token} minor discount: {discount:.2%} — potential arb")

    async def monitor_restaking_positions(self):
        """Monitor EigenLayer restaking positions."""
        for position in self.positions.restaked():
            # Check operator health
            operator = position.operator
            operator_status = await self.eigenlayer.get_operator_status(operator)

            if operator_status.slashing_risk > self.config.max_slash_risk:
                logger.warning(f"Operator {operator.name} high slash risk: "
                             f"{operator_status.slashing_risk}")
                await self.consider_operator_switch(position, operator_status)

            # Check AVS rewards
            pending_rewards = await self.eigenlayer.get_pending_rewards(position)
            if pending_rewards > self.config.min_claim_amount:
                await self.claim_restaking_rewards(position)

    async def calculate_optimal_allocation(
        self, yields: Dict[str, float]
    ) -> AllocationPlan:
        """
        Calculate optimal allocation across staking strategies.
        """
        total_capital = self.positions.total_value_eth()

        # Available strategies and their current yields
        strategies = {
            "steth_hold": {
                "yield": yields.get("steth_staking", 0.04),
                "risk": 0.05,
                "max_alloc": 0.40,
            },
            "reth_hold": {
                "yield": yields.get("reth_staking", 0.038),
                "risk": 0.05,
                "max_alloc": 0.30,
            },
            "leveraged_steth": {
                "yield": self.calculate_leveraged_yield(
                    yields["steth_staking"], yields["eth_borrow_rate"]
                ),
                "risk": 0.30,
                "max_alloc": 0.25,
            },
            "restaking": {
                "yield": yields.get("restaking_total", 0.07),
                "risk": 0.20,
                "max_alloc": 0.20,
            },
            "pendle_fixed": {
                "yield": yields.get("pendle_pt_steth", 0.08),
                "risk": 0.10,
                "max_alloc": 0.20,
            },
            "wsteth_eth_lp": {
                "yield": yields.get("wsteth_eth_lp", 0.08),
                "risk": 0.15,
                "max_alloc": 0.25,
            },
        }

        # Optimize allocation using risk-adjusted yield
        from scipy.optimize import minimize

        def neg_risk_adj_yield(weights):
            total_yield = sum(
                w * s["yield"] * (1 - s["risk"])
                for w, s in zip(weights, strategies.values())
            )
            return -total_yield

        n = len(strategies)
        bounds = [(0, s["max_alloc"]) for s in strategies.values()]
        constraints = [{"type": "eq", "fun": lambda w: sum(w) - 1}]
        x0 = [1/n] * n

        result = minimize(neg_risk_adj_yield, x0,
                         bounds=bounds, constraints=constraints)

        allocation = {
            name: weight * total_capital
            for name, weight in zip(strategies.keys(), result.x)
            if weight > 0.01  # Ignore tiny allocations
        }

        return AllocationPlan(
            allocations=allocation,
            expected_yield=-result.fun,
            total_capital=total_capital
        )

    async def rebalance_staking_portfolio(self, target: AllocationPlan):
        """Rebalance portfolio toward target allocation."""
        current = self.positions.current_allocation()

        for strategy, target_amount in target.allocations.items():
            current_amount = current.get(strategy, 0)
            diff = target_amount - current_amount

            if abs(diff) / target.total_capital < 0.02:
                continue  # Less than 2% difference, skip

            if diff > 0:
                # Need to increase this strategy
                await self.increase_allocation(strategy, diff)
            else:
                # Need to decrease this strategy
                await self.decrease_allocation(strategy, abs(diff))

    async def claim_and_compound_rewards(self):
        """Claim all pending rewards and compound them."""

        # EigenLayer rewards
        eigen_rewards = await self.eigenlayer.get_all_pending_rewards()
        if eigen_rewards.total_value_eth > self.config.min_claim_amount:
            await self.eigenlayer.claim_all_rewards()
            # Restake the rewards
            await self.restake_rewards(eigen_rewards)

        # Pendle rewards
        pendle_rewards = await self.pendle.get_pending_rewards()
        if pendle_rewards.total_value > self.config.min_claim_amount:
            await self.pendle.claim_rewards()
            # Swap to ETH and restake
            eth_amount = await self.swap_to_eth(pendle_rewards)
            await self.stake_eth(eth_amount)

    def calculate_leveraged_yield(
        self, staking_yield: float, borrow_rate: float
    ) -> float:
        """Calculate net yield for leveraged staking strategy."""
        safe_leverage = self.config.max_staking_leverage  # e.g., 3x
        net_yield = safe_leverage * staking_yield - (safe_leverage - 1) * borrow_rate
        return max(0, net_yield)  # Floor at 0
```

---

## 12. Risk Parameters

### 12.1 Staking Position Limits

| Parameter                        | Value    | Rationale                          |
|----------------------------------|----------|-------------------------------------|
| Max staking allocation (% AUM)   | 40%      | Large but capped allocation         |
| Max single LST concentration     | 60%      | Diversify across LST providers      |
| Max leverage on staking          | 4x       | Conservative for correlated pairs   |
| Max restaking exposure           | 20%      | Newer, higher risk                  |
| Max single operator (restaking)  | 20%      | Operator diversification            |
| Max single AVS exposure          | 30%      | AVS risk diversification            |
| Peg alert threshold              | 0.5%     | Early warning for de-peg            |
| Peg action threshold             | 1.5%     | Reduce leveraged positions          |
| Peg emergency threshold          | 3.0%     | Exit all leveraged staking          |
| Min health factor (leveraged)    | 1.5      | Buffer above liquidation            |
| Max withdrawal queue tolerance   | 7 days   | Liquidity constraint                |

### 12.2 Restaking-Specific Limits

| Parameter                          | Value   | Rationale                        |
|------------------------------------|---------|----------------------------------|
| Max total restaking (% staking)    | 50%     | Not all stake should be restaked |
| Max AVS slashing parameter         | 30%     | Won't restake with >30% slash possible |
| Min operator uptime requirement    | 99.5%   | Reliability threshold            |
| Max operator commission            | 20%     | Cost management                  |
| Required operator track record     | 6 months| Minimum operating history        |
| Restaking cool-off after slash     | 30 days | Mandatory pause after any slash event |

### 12.3 Monitoring Frequencies

| Metric                    | Frequency    | Alert Condition              |
|---------------------------|-------------|------------------------------|
| LST/ETH peg              | Every 60 sec | Deviation > 0.3%             |
| Health factor (leveraged) | Every block  | Below 1.8                    |
| Operator status           | Every 5 min  | Slashing event, downtime     |
| Staking yield rate        | Every 1 hour | Drop > 20% from average      |
| Withdrawal queue length   | Every 15 min | Queue > 5 days               |
| AVS rewards accrual       | Every 1 hour | Rewards stop accruing         |
| Smart contract events     | Every block  | Pause, upgrade, admin events  |

---

## 13. References

### Protocol Documentation

1. Lido Documentation. https://docs.lido.fi/
2. Lido Staking APR. https://lido.fi/ethereum
3. Rocket Pool Documentation. https://docs.rocketpool.net/
4. EigenLayer Documentation. https://docs.eigenlayer.xyz/
5. EtherFi Documentation. https://docs.ether.fi/
6. Pendle Finance Documentation. https://docs.pendle.finance/

### Research Papers

7. Neuder, M., Ferreira, D., Kim, T. (2023). "Restaking: An Empirical Analysis
   of the EigenLayer Ecosystem." Working Paper.

8. Chitra, T., Kulkarni, K. (2022). "Improving Proof of Stake Economic Security
   via MEV Redistribution." arXiv.

9. Buterin, V. (2023). "Don't Overload Ethereum's Consensus."
   Vitalik's Blog.

10. Buterin, V. (2024). "The Risks of Liquid Staking Derivatives."
    Ethereum Research Forum.

### Analytics and Data

11. Dune Analytics — Ethereum Staking Dashboard.
    https://dune.com/hildobby/eth2-staking

12. Rated Network — Validator Performance.
    https://www.rated.network/

13. EigenLayer Stats. https://app.eigenlayer.xyz/

14. DefiLlama — Liquid Staking.
    https://defillama.com/lsd

### Technical Resources

15. Ethereum Beacon Chain Spec.
    https://ethereum.github.io/consensus-specs/

16. EIP-4895 — Beacon Chain Withdrawals.
    https://eips.ethereum.org/EIPS/eip-4895

17. Liquid Staking Derivatives Alliance.
    https://lsda.io/

---

> **End of Module 02 — DeFi Mechanics**
>
> This module provides the complete framework for the Multi-Agent AI Trading System
> to operate in DeFi markets. All strategies described herein should be implemented
> with the risk parameters defined and continuously monitored by the system's risk
> management layer.
