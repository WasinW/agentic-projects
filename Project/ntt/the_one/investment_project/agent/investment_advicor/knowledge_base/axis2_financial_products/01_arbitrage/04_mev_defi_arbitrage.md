# MEV & DeFi Arbitrage — Complete Strategy Documentation

> **Document Version:** 2.0
> **Last Updated:** 2026-04-12
> **Classification:** Core Knowledge Base — Axis 2: Financial Products
> **Strategy Type:** Pure Arbitrage (atomic execution via smart contracts)
> **Markets:** DeFi (Ethereum, L2s, Solana, other EVM chains)
> **Frequency:** Per-block (12s Ethereum, 0.4s Solana, 2s L2s)

---

## Table of Contents

1. [Maximal Extractable Value (MEV) — Explained](#1-maximal-extractable-value-mev--explained)
2. [Types of MEV](#2-types-of-mev)
3. [DEX Arbitrage Between AMMs](#3-dex-arbitrage-between-amms)
4. [Flash Loan Arbitrage](#4-flash-loan-arbitrage)
5. [Liquidation Arbitrage](#5-liquidation-arbitrage)
6. [Cross-Chain Arbitrage](#6-cross-chain-arbitrage)
7. [MEV Protection Strategies](#7-mev-protection-strategies)
8. [Smart Contract Architecture](#8-smart-contract-architecture)
9. [Gas Optimization Strategies](#9-gas-optimization-strategies)
10. [Mathematical Models](#10-mathematical-models)
11. [Risk Parameters and Execution Flow](#11-risk-parameters-and-execution-flow)
12. [References](#12-references)

---

## 1. Maximal Extractable Value (MEV) — Explained

### 1.1 Definition

**Maximal Extractable Value (MEV)** refers to the maximum value that can be extracted from block production in excess of the standard block reward and gas fees, by including, excluding, or reordering transactions within a block.

Originally termed "Miner Extractable Value" (when Ethereum used Proof-of-Work), it was renamed to "Maximal Extractable Value" after the transition to Proof-of-Stake, as validators (not miners) now produce blocks.

### 1.2 How MEV Arises

MEV exists because:

1. **Transaction ordering matters:** The sequence in which transactions are included in a block affects economic outcomes
2. **Public mempool:** Pending transactions are visible to all network participants before inclusion
3. **Deterministic execution:** Smart contract outcomes are predictable given the state and transaction order
4. **Block proposer discretion:** The block builder/proposer can choose which transactions to include and in what order

### 1.3 MEV Supply Chain (Post-Merge Ethereum)

```
┌────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   Searcher  │────>│    Builder    │────>│    Relay     │────>│   Proposer   │
│ (finds MEV) │     │ (builds block)│     │(auctions block)│   │(validates)   │
└────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
       │                    │                                        │
  Submits bundles     Constructs optimal     Selects highest      Proposes block
  via Flashbots       block ordering         paying block         to network
```

**Key Actors:**
- **Searchers:** Find MEV opportunities (arbitrage, liquidations) and submit transaction bundles
- **Builders:** Aggregate bundles and transactions into complete blocks
- **Relays:** Act as trusted intermediaries between builders and proposers
- **Proposers (Validators):** Select the most profitable block to propose

### 1.4 MEV Scale

- **Cumulative MEV extracted on Ethereum (since Jan 2020):** > $800M
- **Daily MEV (typical):** $1-5M (varies with market activity)
- **Peak daily MEV:** > $50M (during major market events)
- **MEV types distribution:** ~60% arbitrage, ~30% liquidations, ~10% sandwich attacks

---

## 2. Types of MEV

### 2.1 Taxonomy

```
MEV Types
├── Beneficial MEV (positive externalities)
│   ├── DEX Arbitrage (price alignment)
│   ├── Liquidations (maintaining protocol health)
│   └── Oracle updates (keeping prices current)
│
├── Neutral MEV
│   ├── Backrunning (trade after a large order)
│   └── JIT (Just-in-Time) Liquidity
│
└── Harmful MEV (negative externalities)
    ├── Frontrunning (trade before a victim)
    ├── Sandwich Attacks (frontrun + backrun)
    ├── Time-Bandit Attacks (chain reorgs)
    └── Censorship (excluding transactions)
```

### 2.2 Frontrunning

**Definition:** Observing a pending profitable transaction in the mempool and submitting your own transaction with higher gas to be included first.

**How it works:**

```
1. Victim submits TX: "Buy 100 ETH on Uniswap at market price"
2. Searcher sees TX in mempool
3. Searcher submits TX with higher gas: "Buy ETH before victim"
4. Searcher's TX executes first, pushing price up
5. Victim's TX executes at worse price
6. Searcher profits from the price impact
```

**Mathematical model:**

Let $\Delta P$ be the price impact of the victim's trade:

$$\text{Frontrun Profit} = Q_{frontrunner} \times \Delta P - Gas_{frontrunner}$$

### 2.3 Backrunning

**Definition:** Submitting a transaction immediately after a known large trade to profit from the resulting price dislocation.

**Example:** A large swap moves the Uniswap pool price away from the external market price. A backrunner arbitrages the pool back to the correct price.

### 2.4 Sandwich Attacks

**Definition:** Combination of frontrunning and backrunning around a victim's transaction.

```
Block ordering:
1. Attacker BUY  (frontrun) — pushes price up
2. Victim BUY   (target)   — executes at higher price
3. Attacker SELL (backrun)  — profits from price difference
```

**Profit formula:**

$$\text{Sandwich Profit} = Q_{attacker} \times (P_{after\_victim} - P_{before\_victim}) - 2 \times Gas$$

**Constraint:** The attacker's initial buy must not push the price so high that the victim's transaction reverts (slippage tolerance check).

### 2.5 Just-in-Time (JIT) Liquidity

**Definition:** Adding concentrated liquidity to a Uniswap V3 pool just before a large trade (to earn trading fees), then removing it immediately after.

```
1. Observe large pending swap
2. Add concentrated liquidity in a tight range around current price
3. Large swap executes, paying fees to your liquidity position
4. Remove liquidity immediately
5. Profit = fees earned - gas costs
```

---

## 3. DEX Arbitrage Between AMMs

### 3.1 How AMMs Price Assets

**Constant Product Market Maker (Uniswap V2, SushiSwap):**

$$x \times y = k$$

Where:
- $x$ = reserve of token X
- $y$ = reserve of token Y
- $k$ = constant (the product must remain unchanged)

**Price of token X in terms of Y:**

$$P_X = \frac{y}{x}$$

**Concentrated Liquidity (Uniswap V3):**

$$L = \sqrt{x \times y}$$

Price defined within ticks, with liquidity concentrated in specific ranges.

### 3.2 Why DEX Prices Diverge

Prices on DEXs diverge from each other and from CEXs because:

1. **Isolated liquidity pools:** Each pool/DEX has independent reserves
2. **Block-by-block updates:** Prices only change when transactions are included in blocks
3. **No continuous market making:** Unlike CEX order books, AMM prices are formulaic
4. **Different fee tiers:** Uniswap V3 has 0.01%, 0.05%, 0.30%, 1.00% fee pools
5. **Large swaps:** A big trade on one DEX creates a price dislocation relative to others

### 3.3 Arbitrage Between Two AMMs

**Scenario:** Token A/B trades on Uniswap and SushiSwap at different prices.

$$P_{Uniswap} = \frac{y_U}{x_U}, \quad P_{SushiSwap} = \frac{y_S}{x_S}$$

If $P_{Uniswap} < P_{SushiSwap}$: Buy on Uniswap, sell on SushiSwap.

**Optimal trade size for constant-product AMMs:**

Given Uniswap reserves $(x_U, y_U)$ and SushiSwap reserves $(x_S, y_S)$:

The optimal amount $\Delta x$ to buy on the cheaper DEX satisfies:

$$\frac{y_U - \frac{x_U \times y_U}{x_U + \Delta x \times (1-f_U)}}{1} = \frac{y_S \times \Delta y}{y_S + \Delta y \times (1-f_S)}$$

After simplification, the optimal trade size is:

$$\Delta x^* = \frac{\sqrt{x_U \times y_U \times (1-f_U) \times P_S \times (1-f_S)} - x_U}{1-f_U}$$

(Where $P_S$ is the effective price on the sell side.)

### 3.4 Multi-Hop Arbitrage

Instead of direct arbitrage between two pools, multi-hop routes can be more profitable:

```
Route: USDC -> WETH (Uniswap) -> WBTC (SushiSwap) -> USDC (Curve)

If the net output of USDC > input of USDC (after all fees), profit exists.
```

**Finding optimal routes** requires pathfinding algorithms (e.g., Bellman-Ford for negative cycle detection in the graph of exchange rates).

### 3.5 CEX-DEX Arbitrage

When a CEX price moves but the DEX pool has not yet been updated:

```
CEX: BTC = $65,200
DEX (Uniswap): BTC = $65,000 (stale pool price)

Action: Buy BTC on Uniswap at $65,000, sell on CEX at $65,200
Profit: $200 per BTC (minus gas, DEX fees, and CEX fees)
```

This is one of the most common MEV strategies and serves as the primary price-alignment mechanism for DEXs.

---

## 4. Flash Loan Arbitrage

### 4.1 How Flash Loans Work

A flash loan is an uncollateralized loan that must be borrowed and repaid within a **single atomic transaction**. If the borrower cannot repay the loan plus fees by the end of the transaction, the entire transaction reverts (as if it never happened).

**Key Properties:**
- **Zero collateral required:** No upfront capital needed
- **Atomic execution:** Borrow + arbitrage + repay in one transaction
- **Risk-free for lender:** If repayment fails, the entire TX reverts
- **Capital efficiency:** Enables arbitrage with zero personal capital

### 4.2 Flash Loan Providers

| Protocol | Network | Max Loan | Fee | Gas Overhead |
|----------|---------|:--------:|:---:|:------------:|
| Aave V3 | Ethereum, L2s | Pool liquidity (~$10B+) | 0.05% | ~150K gas |
| dYdX | Ethereum | Pool liquidity | 0% (no fee) | ~200K gas |
| Uniswap V3 | Ethereum, L2s | Pool liquidity | Pool fee rate | ~100K gas |
| Balancer V2 | Ethereum | Pool liquidity | 0% | ~130K gas |
| MakerDAO | Ethereum | DAI supply | 0% | ~200K gas |

### 4.3 Flash Loan Arbitrage Flow

```
Single Transaction (atomic):
┌─────────────────────────────────────────────────────┐
│                                                     │
│  1. Borrow 1000 WETH from Aave (flash loan)        │
│                                                     │
│  2. Swap 1000 WETH -> USDC on Uniswap              │
│     (where WETH is underpriced)                     │
│     Get: 3,210,000 USDC                             │
│                                                     │
│  3. Swap 3,210,000 USDC -> WETH on SushiSwap       │
│     (where WETH is overpriced)                      │
│     Get: 1,003.5 WETH                               │
│                                                     │
│  4. Repay 1000 WETH + 0.5 WETH fee to Aave         │
│     (total: 1000.5 WETH)                            │
│                                                     │
│  5. Profit: 1003.5 - 1000.5 = 3.0 WETH             │
│     (~$9,600 at $3,200/WETH)                        │
│                                                     │
│  If any step fails → entire TX reverts              │
│  Net cost if reverted: only gas fee (~$10-50)       │
└─────────────────────────────────────────────────────┘
```

### 4.4 Profit Calculation

$$\boxed{P_{net} = \text{Output} - \text{Input} - F_{flash} - F_{dex} - F_{gas}}$$

Where:
- $\text{Output}$ = final amount received after all swaps
- $\text{Input}$ = flash loan amount (must be repaid)
- $F_{flash}$ = flash loan fee (e.g., 0.05% for Aave)
- $F_{dex}$ = DEX swap fees across all hops
- $F_{gas}$ = gas cost for the transaction

**Detailed:**

$$P_{net} = Q_{loan} \times \prod_{i=1}^{n} R_i \times (1 - f_i) - Q_{loan} \times (1 + f_{flash}) - Gas \times GasPrice$$

Where:
- $Q_{loan}$ = flash loan amount
- $R_i$ = exchange rate at swap $i$
- $f_i$ = DEX fee at swap $i$
- $f_{flash}$ = flash loan fee rate
- $Gas$ = gas units consumed
- $GasPrice$ = current gas price (in ETH)

### 4.5 Optimal Loan Amount

For a two-DEX constant-product arbitrage:

The profit function with respect to trade size $q$:

$$\Pi(q) = \frac{y_B \times q \times (1-f_A) \times (1-f_B)}{x_B + q \times (1-f_A)} - q \times (1 + f_{flash}) - Gas$$

Wait, more precisely for the full cycle (buy on A, sell on B):

$$\text{Amount out from A} = \frac{y_A \times q \times (1-f_A)}{x_A + q \times (1-f_A)}$$

$$\text{Final amount from B} = \frac{y_B \times \text{AmountOut}_A \times (1-f_B)}{x_B + \text{AmountOut}_A \times (1-f_B)}$$

Optimal $q^*$ is found by setting $\frac{d\Pi}{dq} = 0$:

$$q^* = \frac{\sqrt{x_A \times y_A \times x_B \times y_B \times (1-f_A)^2 \times (1-f_B)^2} - x_A \times x_B}{x_B \times (1-f_A) + \sqrt{...}}$$

In practice, this is solved numerically due to complexity.

### 4.6 Flash Loan Arbitrage Bot Architecture

```python
# Simplified flash loan arbitrage detection logic

class FlashLoanArbitrageFinder:
    """
    Finds profitable flash loan arbitrage opportunities across DEXs.
    """
    
    def __init__(self, web3, dex_pools: List[dict], min_profit_eth: float = 0.01):
        self.web3 = web3
        self.pools = dex_pools
        self.min_profit = min_profit_eth
    
    def find_opportunities(self) -> List[dict]:
        """Scan all pool pairs for profitable routes."""
        opportunities = []
        
        # Get current reserves for all pools
        reserves = self.get_all_reserves()
        
        # Check all pairs of pools for the same token pair
        for i, pool_a in enumerate(self.pools):
            for j, pool_b in enumerate(self.pools):
                if i == j:
                    continue
                if pool_a['token0'] != pool_b['token0'] or pool_a['token1'] != pool_b['token1']:
                    continue
                
                # Check both directions
                for direction in ['buy_a_sell_b', 'buy_b_sell_a']:
                    profit = self.simulate_arbitrage(
                        pool_a, pool_b, reserves, direction
                    )
                    
                    if profit > self.min_profit:
                        opportunities.append({
                            'pool_a': pool_a,
                            'pool_b': pool_b,
                            'direction': direction,
                            'expected_profit': profit,
                            'optimal_size': self.find_optimal_size(
                                pool_a, pool_b, reserves, direction
                            )
                        })
        
        return sorted(opportunities, key=lambda x: x['expected_profit'], reverse=True)
    
    def simulate_arbitrage(self, pool_a, pool_b, reserves, direction) -> float:
        """Simulate arbitrage and return profit in ETH."""
        # Get reserves
        ra_x, ra_y = reserves[pool_a['address']]
        rb_x, rb_y = reserves[pool_b['address']]
        
        # Calculate optimal input
        optimal_input = self.calculate_optimal_input(
            ra_x, ra_y, rb_x, rb_y,
            pool_a['fee'], pool_b['fee'],
            direction
        )
        
        if optimal_input <= 0:
            return 0
        
        # Simulate swaps
        if direction == 'buy_a_sell_b':
            # Buy token on A (swap Y for X), sell on B (swap X for Y)
            amount_x = self.get_amount_out(optimal_input, ra_y, ra_x, pool_a['fee'])
            amount_y_final = self.get_amount_out(amount_x, rb_x, rb_y, pool_b['fee'])
        else:
            amount_x = self.get_amount_out(optimal_input, rb_y, rb_x, pool_b['fee'])
            amount_y_final = self.get_amount_out(amount_x, ra_x, ra_y, pool_a['fee'])
        
        # Profit = output - input - flash loan fee - gas
        flash_fee = optimal_input * 0.0005  # Aave 0.05%
        gas_cost = 300_000 * self.get_gas_price()  # Estimate 300K gas
        
        profit = amount_y_final - optimal_input - flash_fee - gas_cost
        return profit
    
    @staticmethod
    def get_amount_out(amount_in, reserve_in, reserve_out, fee) -> float:
        """Calculate output amount for a constant-product swap."""
        amount_in_with_fee = amount_in * (1 - fee)
        numerator = amount_in_with_fee * reserve_out
        denominator = reserve_in + amount_in_with_fee
        return numerator / denominator
    
    def calculate_optimal_input(self, ra_x, ra_y, rb_x, rb_y, 
                                 fee_a, fee_b, direction) -> float:
        """Calculate optimal input amount for maximum profit."""
        import numpy as np
        from scipy.optimize import minimize_scalar
        
        def neg_profit(q):
            if direction == 'buy_a_sell_b':
                out1 = self.get_amount_out(q, ra_y, ra_x, fee_a)
                out2 = self.get_amount_out(out1, rb_x, rb_y, fee_b)
            else:
                out1 = self.get_amount_out(q, rb_y, rb_x, fee_b)
                out2 = self.get_amount_out(out1, ra_x, ra_y, fee_a)
            return -(out2 - q - q * 0.0005)  # Negative for minimization
        
        result = minimize_scalar(neg_profit, bounds=(0.01, min(ra_y, rb_y) * 0.5), method='bounded')
        
        if -result.fun > 0:
            return result.x
        return 0
```

---

## 5. Liquidation Arbitrage

### 5.1 How Lending Protocol Liquidations Work

DeFi lending protocols (Aave, Compound, MakerDAO) require borrowers to maintain a minimum **collateral ratio**. When the ratio drops below the liquidation threshold, anyone can repay part of the debt and receive the collateral at a discount.

**Health Factor:**

$$HF = \frac{\sum_i C_i \times LT_i}{\sum_j D_j}$$

Where:
- $C_i$ = value of collateral asset $i$
- $LT_i$ = liquidation threshold for asset $i$ (e.g., 0.825 for ETH on Aave)
- $D_j$ = value of debt asset $j$

When $HF < 1$: Position is liquidatable.

### 5.2 Liquidation Bonus

The liquidator receives a bonus (discount) on the collateral:

$$\text{Collateral Received} = \frac{\text{Debt Repaid} \times (1 + \text{Liquidation Bonus})}{P_{collateral}}$$

| Protocol | Typical Liquidation Bonus | Max Liquidation % |
|----------|:-------------------------:|:-----------------:|
| Aave V3 | 5-10% | 50% of debt |
| Compound V3 | 5-8% | 100% |
| MakerDAO | 13% | 100% |
| Venus (BSC) | 10% | 50% |

### 5.3 Liquidation Arbitrage with Flash Loans

```
1. Monitor lending protocols for positions where HF < 1
2. When found:
   a. Flash loan the debt asset (e.g., 1000 USDC)
   b. Repay the undercollateralized position's debt
   c. Receive collateral at discount (e.g., 1050 USDC worth of ETH)
   d. Swap collateral back to debt asset on DEX
   e. Repay flash loan + fee
   f. Keep profit (the liquidation bonus minus fees)
```

**Profit formula:**

$$P_{liquidation} = D_{repaid} \times LB - D_{repaid} \times f_{flash} - Gas - Slippage$$

Where $LB$ = liquidation bonus percentage.

### 5.4 Monitoring Infrastructure

```python
class LiquidationMonitor:
    """
    Monitors DeFi lending protocols for liquidatable positions.
    """
    
    def __init__(self, web3, protocols: List[str]):
        self.web3 = web3
        self.protocols = protocols
        self.positions = {}  # {user_address: position_data}
    
    async def monitor(self):
        """Main monitoring loop."""
        while True:
            # Get all at-risk positions
            for protocol in self.protocols:
                risky_positions = await self.get_risky_positions(protocol)
                
                for position in risky_positions:
                    if position['health_factor'] < 1.0:
                        # Liquidatable!
                        profit = self.estimate_liquidation_profit(position)
                        
                        if profit > self.min_profit_threshold:
                            await self.execute_liquidation(position)
            
            await asyncio.sleep(1)  # Check every block
    
    async def get_risky_positions(self, protocol: str) -> List[dict]:
        """
        Get positions with health factor close to liquidation.
        
        Strategy: Monitor positions with HF < 1.1 (10% buffer)
        as they may become liquidatable with small price moves.
        """
        # Query protocol's lending pool contract
        # Filter for positions with HF < threshold
        pass
    
    def estimate_liquidation_profit(self, position: dict) -> float:
        """Estimate profit from liquidating a position."""
        debt_to_repay = min(
            position['total_debt'] * 0.5,  # Max 50% close factor
            position['total_debt']
        )
        
        liquidation_bonus = position['liquidation_bonus']  # e.g., 0.05 = 5%
        collateral_received = debt_to_repay * (1 + liquidation_bonus)
        
        # Costs
        flash_loan_fee = debt_to_repay * 0.0005  # 0.05%
        gas_cost = 500_000 * self.get_gas_price()  # ~500K gas for liquidation
        swap_fee = collateral_received * 0.003  # 0.30% DEX fee to swap back
        
        profit = collateral_received - debt_to_repay - flash_loan_fee - gas_cost - swap_fee
        return profit
```

---

## 6. Cross-Chain Arbitrage

### 6.1 Concept

Cross-chain arbitrage exploits price differences for the same asset on DEXs deployed on different blockchains (e.g., Uniswap on Ethereum vs. Uniswap on Arbitrum vs. PancakeSwap on BSC).

### 6.2 Challenges

| Challenge | Description | Mitigation |
|-----------|-------------|------------|
| Bridge latency | Cross-chain bridges take minutes to hours | Pre-position on multiple chains |
| Bridge risk | Bridges are frequent hack targets | Use well-audited bridges, limit exposure |
| Gas on multiple chains | Need native tokens for gas on each chain | Maintain gas reserves |
| Different block times | Opportunity may disappear before execution | Fast detection, simultaneous execution |
| Atomic execution impossible | Cannot guarantee both sides fill | Risk management, partial hedging |

### 6.3 Execution Models

**Model A: Pre-Positioned (Recommended)**

```
1. Maintain balances on multiple chains
2. Detect price difference (e.g., ETH cheaper on Arbitrum Uniswap vs Ethereum Uniswap)
3. Buy on cheap chain, sell on expensive chain simultaneously
4. Periodically rebalance via bridges
```

**Model B: Bridge Arbitrage**

```
1. Detect large price difference (must exceed bridge time risk)
2. Buy on cheap chain
3. Bridge asset to expensive chain
4. Sell on expensive chain
5. Risk: price may change during bridge transit
```

### 6.4 Cross-Chain Price Monitoring

```python
class CrossChainArbitrageMonitor:
    """Monitor prices across multiple chains for arbitrage."""
    
    def __init__(self, chains: dict):
        """
        chains: {
            'ethereum': {'rpc': '...', 'pools': [...]},
            'arbitrum': {'rpc': '...', 'pools': [...]},
            'bsc': {'rpc': '...', 'pools': [...]},
        }
        """
        self.chains = chains
        self.prices = {}
    
    async def monitor(self):
        """Monitor prices on all chains simultaneously."""
        tasks = [
            self.monitor_chain(chain_name, config)
            for chain_name, config in self.chains.items()
        ]
        await asyncio.gather(*tasks)
    
    async def monitor_chain(self, chain: str, config: dict):
        """Monitor prices on a specific chain."""
        web3 = Web3(Web3.HTTPProvider(config['rpc']))
        
        while True:
            for pool in config['pools']:
                price = await self.get_pool_price(web3, pool)
                self.prices[(chain, pool['pair'])] = {
                    'price': price,
                    'timestamp': time.time()
                }
                
                # Check for cross-chain opportunity
                self.check_cross_chain_opportunities(pool['pair'])
            
            await asyncio.sleep(1)
    
    def check_cross_chain_opportunities(self, pair: str):
        """Check if cross-chain arbitrage exists for a pair."""
        chain_prices = {
            chain: data['price']
            for (chain, p), data in self.prices.items()
            if p == pair and time.time() - data['timestamp'] < 5
        }
        
        if len(chain_prices) < 2:
            return
        
        # Find min and max
        min_chain = min(chain_prices.items(), key=lambda x: x[1])
        max_chain = max(chain_prices.items(), key=lambda x: x[1])
        
        spread_bps = (max_chain[1] - min_chain[1]) / min_chain[1] * 10000
        
        # Cross-chain requires larger spread (bridge risk premium)
        if spread_bps > 50:  # 50 bps minimum for cross-chain
            self.on_opportunity({
                'pair': pair,
                'buy_chain': min_chain[0],
                'sell_chain': max_chain[0],
                'spread_bps': spread_bps,
                'buy_price': min_chain[1],
                'sell_price': max_chain[1],
            })
```

---

## 7. MEV Protection Strategies

### 7.1 Flashbots

**Flashbots** is a research and development organization focused on mitigating the negative effects of MEV. Their key products:

- **Flashbots Protect:** RPC endpoint that sends transactions directly to block builders, bypassing the public mempool
- **MEV-Share:** Protocol for users to share MEV with searchers while maintaining transaction privacy
- **Flashbots Auction (MEV-Boost):** System for validators to outsource block building to maximize MEV extraction

### 7.2 Using Flashbots Protect for Arbitrage

```python
from web3 import Web3
import requests

class FlashbotsClient:
    """
    Submit transactions via Flashbots to avoid public mempool exposure.
    """
    
    def __init__(self, web3: Web3, private_key: str, flashbots_url: str):
        self.web3 = web3
        self.private_key = private_key
        self.flashbots_url = flashbots_url  # "https://relay.flashbots.net"
    
    async def submit_bundle(self, transactions: List[dict], target_block: int):
        """
        Submit a bundle of transactions to Flashbots.
        
        Bundles are atomic: either all TXs are included or none.
        They are also private: not visible in the public mempool.
        """
        signed_txs = []
        for tx in transactions:
            signed = self.web3.eth.account.sign_transaction(tx, self.private_key)
            signed_txs.append(signed.rawTransaction.hex())
        
        bundle = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_sendBundle",
            "params": [{
                "txs": signed_txs,
                "blockNumber": hex(target_block),
            }]
        }
        
        # Sign the bundle request
        body = json.dumps(bundle)
        signature = self.sign_message(body)
        
        headers = {
            "Content-Type": "application/json",
            "X-Flashbots-Signature": f"{self.address}:{signature}"
        }
        
        response = requests.post(self.flashbots_url, json=bundle, headers=headers)
        return response.json()
    
    async def simulate_bundle(self, transactions: List[dict], block_number: int):
        """
        Simulate bundle execution to verify profitability before submission.
        """
        # ... simulation logic
        pass
```

### 7.3 Private Mempools

| Service | Description | Use Case |
|---------|-------------|----------|
| Flashbots Protect | Free, private TX submission | Avoiding frontrunning |
| MEV Blocker (CoW Protocol) | Rebates from MEV | User protection |
| Eden Network | Private TX inclusion | Priority ordering |
| BloxRoute | Private TX relay | Fast inclusion |
| Alchemy Private Pool | Private mempool | Enterprise users |

### 7.4 MEV Protection for Our Arbitrage

As an arbitrage searcher, we want to:
1. **Protect our arbitrage transactions** from being frontrun by other searchers
2. **Use private channels** (Flashbots) to submit our bundles
3. **Simulate before submitting** to avoid paying gas for failed transactions
4. **Bid accurately** for block space (not overpaying)

---

## 8. Smart Contract Architecture

### 8.1 Flash Loan Arbitrage Contract (Solidity Pseudocode)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@aave/v3-core/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol";
import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title FlashLoanArbitrage
 * @notice Executes atomic arbitrage using Aave V3 flash loans
 * @dev Only callable by owner. Profits sent to owner.
 */
contract FlashLoanArbitrage is FlashLoanSimpleReceiverBase {
    
    address public immutable owner;
    ISwapRouter public immutable uniswapRouter;
    ISwapRouter public immutable sushiswapRouter;
    
    // Minimum profit threshold (in base units of borrowed asset)
    uint256 public minProfitThreshold;
    
    struct ArbParams {
        address tokenBorrow;      // Token to flash loan
        address tokenIntermediate; // Intermediate token in the arb path
        uint256 amountBorrow;     // Amount to flash loan
        address dexBuy;           // DEX to buy on (cheaper)
        address dexSell;          // DEX to sell on (more expensive)
        uint24 feeTierBuy;        // Fee tier for buy DEX pool
        uint24 feeTierSell;       // Fee tier for sell DEX pool
        uint256 minAmountOut;     // Minimum output (slippage protection)
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "NOT_OWNER");
        _;
    }
    
    constructor(
        address _poolProvider,
        address _uniswapRouter,
        address _sushiswapRouter
    ) FlashLoanSimpleReceiverBase(IPoolAddressesProvider(_poolProvider)) {
        owner = msg.sender;
        uniswapRouter = ISwapRouter(_uniswapRouter);
        sushiswapRouter = ISwapRouter(_sushiswapRouter);
        minProfitThreshold = 0; // Set by owner
    }
    
    /**
     * @notice Initiates the flash loan arbitrage
     * @param params Encoded arbitrage parameters
     */
    function executeArbitrage(ArbParams calldata params) external onlyOwner {
        // Encode params for the callback
        bytes memory data = abi.encode(params);
        
        // Request flash loan from Aave
        POOL.flashLoanSimple(
            address(this),           // receiver
            params.tokenBorrow,      // asset to borrow
            params.amountBorrow,     // amount
            data,                    // params passed to callback
            0                        // referral code
        );
    }
    
    /**
     * @notice Aave flash loan callback - executes the arbitrage
     * @dev This is called by Aave after providing the flash loan
     */
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,   // Flash loan fee
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        require(msg.sender == address(POOL), "NOT_AAVE_POOL");
        require(initiator == address(this), "NOT_SELF");
        
        ArbParams memory arbParams = abi.decode(params, (ArbParams));
        
        // Step 1: Swap on buy DEX (cheaper price)
        uint256 amountIntermediate = _swap(
            arbParams.dexBuy,
            asset,
            arbParams.tokenIntermediate,
            amount,
            0,  // No min out for intermediate (final check is enough)
            arbParams.feeTierBuy
        );
        
        // Step 2: Swap back on sell DEX (more expensive price)
        uint256 amountFinal = _swap(
            arbParams.dexSell,
            arbParams.tokenIntermediate,
            asset,
            amountIntermediate,
            arbParams.minAmountOut,
            arbParams.feeTierSell
        );
        
        // Step 3: Verify profit
        uint256 totalDebt = amount + premium;
        require(amountFinal > totalDebt + minProfitThreshold, "NO_PROFIT");
        
        // Step 4: Approve Aave to pull back the loan + premium
        IERC20(asset).approve(address(POOL), totalDebt);
        
        // Step 5: Send profit to owner
        uint256 profit = amountFinal - totalDebt;
        IERC20(asset).transfer(owner, profit);
        
        return true;
    }
    
    /**
     * @notice Internal swap function supporting multiple DEX routers
     */
    function _swap(
        address dexRouter,
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 minAmountOut,
        uint24 feeTier
    ) internal returns (uint256 amountOut) {
        // Approve router
        IERC20(tokenIn).approve(dexRouter, amountIn);
        
        // Execute swap
        ISwapRouter.ExactInputSingleParams memory swapParams = ISwapRouter.ExactInputSingleParams({
            tokenIn: tokenIn,
            tokenOut: tokenOut,
            fee: feeTier,
            recipient: address(this),
            deadline: block.timestamp,
            amountIn: amountIn,
            amountOutMinimum: minAmountOut,
            sqrtPriceLimitX96: 0
        });
        
        amountOut = ISwapRouter(dexRouter).exactInputSingle(swapParams);
    }
    
    /**
     * @notice Emergency withdraw stuck tokens
     */
    function rescueTokens(address token) external onlyOwner {
        uint256 balance = IERC20(token).balanceOf(address(this));
        IERC20(token).transfer(owner, balance);
    }
    
    /**
     * @notice Update minimum profit threshold
     */
    function setMinProfitThreshold(uint256 _threshold) external onlyOwner {
        minProfitThreshold = _threshold;
    }
    
    receive() external payable {}
}
```

### 8.2 Multi-Hop Flash Loan Contract

```solidity
/**
 * @title MultiHopFlashArbitrage
 * @notice Supports arbitrage routes with multiple swaps
 */
contract MultiHopFlashArbitrage is FlashLoanSimpleReceiverBase {
    
    struct SwapStep {
        address dexRouter;
        address tokenIn;
        address tokenOut;
        uint24 feeTier;
        uint256 minAmountOut;  // 0 for intermediate steps
    }
    
    struct MultiHopParams {
        address loanToken;
        uint256 loanAmount;
        SwapStep[] steps;
    }
    
    function executeMultiHopArbitrage(MultiHopParams calldata params) external onlyOwner {
        bytes memory data = abi.encode(params);
        
        POOL.flashLoanSimple(
            address(this),
            params.loanToken,
            params.loanAmount,
            data,
            0
        );
    }
    
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        require(msg.sender == address(POOL), "NOT_AAVE_POOL");
        
        MultiHopParams memory arbParams = abi.decode(params, (MultiHopParams));
        
        uint256 currentAmount = amount;
        
        // Execute each swap step
        for (uint i = 0; i < arbParams.steps.length; i++) {
            SwapStep memory step = arbParams.steps[i];
            
            currentAmount = _swap(
                step.dexRouter,
                step.tokenIn,
                step.tokenOut,
                currentAmount,
                step.minAmountOut,
                step.feeTier
            );
        }
        
        // Verify profit and repay
        uint256 totalDebt = amount + premium;
        require(currentAmount > totalDebt, "UNPROFITABLE");
        
        IERC20(asset).approve(address(POOL), totalDebt);
        
        uint256 profit = currentAmount - totalDebt;
        IERC20(asset).transfer(owner, profit);
        
        return true;
    }
}
```

### 8.3 Contract Security Considerations

1. **Reentrancy protection:** Use OpenZeppelin's ReentrancyGuard
2. **Access control:** Only owner can initiate arbitrage
3. **Minimum profit check:** On-chain verification that profit exceeds threshold
4. **Deadline protection:** Use `block.timestamp` for swap deadlines
5. **Token approval:** Only approve exact amounts needed
6. **Emergency withdrawal:** Include function to rescue stuck tokens
7. **No storage of sensitive data:** All parameters passed at execution time
8. **Audit:** Must be professionally audited before deployment with real funds

---

## 9. Gas Optimization Strategies

### 9.1 Why Gas Matters

For MEV/DeFi arbitrage, gas costs are often the primary constraint on profitability:

$$\text{Gas Cost} = \text{Gas Used} \times \text{Gas Price (gwei)} \times \text{ETH Price}$$

**Example:** 300,000 gas * 30 gwei * $3,200/ETH = $28.80 per transaction

### 9.2 Gas Optimization Techniques

| Technique | Gas Savings | Description |
|-----------|:-----------:|-------------|
| Assembly (Yul) | 20-50% | Direct EVM opcodes instead of Solidity |
| Packed storage | 10-30% | Combine multiple variables into single slots |
| Unchecked math | 5-15% | Skip overflow checks where safe |
| Minimal proxy | 30-40% | EIP-1167 clones for deployment |
| Calldata optimization | 5-10% | Pack parameters efficiently |
| Batch operations | 20-40% | Combine multiple calls into one |
| Precomputed values | 5-20% | Off-chain computation, on-chain verification |

### 9.3 Gas-Optimized Swap Function

```solidity
// Gas-optimized direct pool interaction (bypasses router)
function swapExactInputDirect(
    address pool,
    bool zeroForOne,
    int256 amountIn,
    uint160 sqrtPriceLimitX96
) internal returns (int256 amount0, int256 amount1) {
    // Call pool directly instead of going through router
    // Saves ~30K gas by avoiding router overhead
    
    (amount0, amount1) = IUniswapV3Pool(pool).swap(
        address(this),
        zeroForOne,
        amountIn,
        sqrtPriceLimitX96,
        ""  // No callback data needed for simple swaps
    );
}
```

### 9.4 Gas Price Strategy

```python
class GasPriceStrategy:
    """
    Dynamic gas pricing for MEV transactions.
    
    Key principle: Gas bid should be slightly below expected profit
    to remain competitive while maintaining profitability.
    """
    
    def calculate_gas_bid(self, expected_profit_wei: int, 
                          gas_used: int,
                          competition_level: str) -> int:
        """
        Calculate optimal gas price for transaction.
        
        Strategy: Bid a fraction of expected profit as gas,
        leaving enough margin for actual profit.
        """
        # Maximum we'd pay in gas (as fraction of profit)
        if competition_level == 'high':
            max_gas_fraction = 0.90  # Give up to 90% of profit as gas
        elif competition_level == 'medium':
            max_gas_fraction = 0.70
        else:
            max_gas_fraction = 0.50
        
        max_gas_wei = int(expected_profit_wei * max_gas_fraction)
        
        # Convert to gas price (priority fee)
        optimal_gas_price = max_gas_wei // gas_used
        
        # Ensure above base fee
        base_fee = self.get_current_base_fee()
        total_gas_price = base_fee + optimal_gas_price
        
        return total_gas_price
    
    def should_submit(self, expected_profit_wei: int, gas_cost_wei: int) -> bool:
        """Check if submission is profitable after gas."""
        min_profit_wei = 10**16  # Minimum 0.01 ETH profit
        return expected_profit_wei - gas_cost_wei > min_profit_wei
```

---

## 10. Mathematical Models

### 10.1 Constant Product AMM — Output Calculation

For a Uniswap V2 style pool with reserves $(x, y)$ and fee $f$:

$$\Delta y = \frac{y \times \Delta x \times (1 - f)}{x + \Delta x \times (1 - f)}$$

**Inverse (given desired output, find required input):**

$$\Delta x = \frac{x \times \Delta y}{(y - \Delta y) \times (1 - f)}$$

### 10.2 Price Impact

The price impact of a trade of size $\Delta x$ on a pool with reserve $x$:

$$\text{Price Impact} = \frac{\Delta x}{x + \Delta x}$$

For small trades ($\Delta x \ll x$):

$$\text{Price Impact} \approx \frac{\Delta x}{x}$$

### 10.3 Optimal Arbitrage Size Between Two Pools

Given pool A with reserves $(x_A, y_A)$ and pool B with reserves $(x_B, y_B)$, both with fee $f$:

The optimal input $q^*$ that maximizes profit when buying token X on A and selling on B:

$$q^* = \frac{\sqrt{(1-f)^2 \times x_A \times y_A \times x_B \times y_B} - x_A \times y_B}{(1-f) \times (y_B + (1-f) \times y_A)}$$

(This is a simplified form; the exact formula depends on the specific trade direction and pool configurations.)

### 10.4 Flash Loan Profitability Condition

For a flash loan of amount $L$ with fee rate $\phi$:

$$\prod_{i=1}^{n} \frac{y_i \times (1-f_i)}{x_i + L_i \times (1-f_i)} > 1 + \phi$$

Where the product represents the cumulative exchange rate across all swaps.

### 10.5 Sandwich Attack Profit Model

For a sandwich attack on a victim trade of size $V$ with slippage tolerance $\tau$:

**Frontrun size $q_f$ is bounded by:**

$$P_{after\_frontrun} \leq P_{initial} \times (1 + \tau)$$

This ensures the victim's trade doesn't revert.

**Optimal frontrun size:**

$$q_f^* = \frac{x \times \tau}{1 + \tau} \times \frac{1}{1-f}$$

**Expected profit:**

$$\Pi_{sandwich} = q_f \times \left(\frac{V \times (1-f)}{x + q_f \times (1-f) + V \times (1-f)}\right) \times \frac{y}{x} - 2 \times Gas$$

### 10.6 MEV Auction Theory (Flashbots)

In the Flashbots auction, searchers bid for block space. The equilibrium bid $b^*$ for a searcher with profit $\pi$ and $n$ competing searchers:

$$b^* = \pi \times \frac{n-1}{n}$$

As competition increases ($n \to \infty$): $b^* \to \pi$ (all profit goes to the block builder/validator).

This is why MEV extraction becomes less profitable over time as more searchers enter the market.

### 10.7 Gas Cost Model

$$\text{Total Gas Cost} = (G_{base} + G_{priority}) \times G_{units}$$

Where:
- $G_{base}$ = EIP-1559 base fee (determined by network congestion)
- $G_{priority}$ = priority fee (tip to validator/builder)
- $G_{units}$ = gas units consumed by the transaction

**Gas estimation for different operations:**

| Operation | Approximate Gas |
|-----------|:--------------:|
| Simple ERC20 transfer | 65,000 |
| Uniswap V2 swap | 150,000 |
| Uniswap V3 swap | 180,000 |
| Aave flash loan (borrow) | 150,000 |
| Full arbitrage (flash loan + 2 swaps) | 350,000-500,000 |
| Liquidation (flash loan + repay + swap) | 400,000-600,000 |
| Multi-hop (3+ swaps) | 500,000-800,000 |

---

## 11. Risk Parameters and Execution Flow

### 11.1 Risk Parameters

```python
MEV_DEFI_RISK_PARAMS = {
    # Profitability
    "min_profit_eth": 0.01,              # Minimum 0.01 ETH profit ($32)
    "min_profit_after_gas_pct": 0.20,    # Must keep at least 20% after gas
    "max_gas_fraction": 0.80,            # Max 80% of profit spent on gas
    
    # Gas
    "max_gas_price_gwei": 200,           # Don't execute above 200 gwei
    "max_priority_fee_gwei": 100,        # Cap priority fee
    "gas_buffer_pct": 0.20,              # Add 20% gas buffer for estimation
    
    # Execution
    "max_block_age": 2,                  # Only use data from last 2 blocks
    "simulation_required": True,          # Always simulate before submitting
    "use_flashbots": True,               # Use Flashbots for privacy
    "max_retry_blocks": 3,               # Retry for up to 3 blocks
    
    # Position limits
    "max_flash_loan_eth": 1000,          # Maximum flash loan size
    "max_single_trade_usd": 500_000,     # Maximum trade size
    "max_daily_gas_spend_eth": 1.0,      # Maximum daily gas budget
    
    # Smart contract safety
    "only_audited_protocols": True,       # Only interact with audited protocols
    "max_pool_age_days": 30,             # Minimum pool age
    "min_pool_liquidity_usd": 100_000,   # Minimum pool TVL
    
    # Monitoring
    "alert_on_reverted_tx": True,
    "alert_on_high_gas": True,
    "alert_on_competitor_activity": True,
    "log_all_simulations": True,
    
    # Circuit breakers
    "max_reverted_txs_per_hour": 5,      # Pause if too many reverts
    "max_daily_loss_eth": 0.5,           # Stop after 0.5 ETH daily loss
    "pause_on_contract_anomaly": True,
}
```

### 11.2 Complete Execution Flow

```python
class MEVArbitrageEngine:
    """
    Complete MEV/DeFi arbitrage execution engine.
    
    Flow:
    1. Monitor mempool and DEX pools for opportunities
    2. Detect profitable arbitrage
    3. Simulate transaction
    4. Submit via Flashbots
    5. Track results
    """
    
    def __init__(self, config, web3, flashbots_client, contract):
        self.config = config
        self.web3 = web3
        self.flashbots = flashbots_client
        self.contract = contract  # Deployed arbitrage contract
        self.daily_gas_spent = 0
        self.daily_profit = 0
    
    async def run(self):
        """Main execution loop - runs once per block."""
        
        # Subscribe to new blocks
        async for block in self.web3.eth.subscribe('newHeads'):
            try:
                # Step 1: Get current state
                pools = await self.get_pool_states()
                gas_price = await self.get_gas_price()
                
                # Step 2: Find opportunities
                opportunities = self.find_opportunities(pools, gas_price)
                
                # Step 3: For each opportunity (sorted by profit)
                for opp in sorted(opportunities, key=lambda x: x['profit'], reverse=True):
                    
                    # Check risk limits
                    if not self.check_risk_limits(opp, gas_price):
                        continue
                    
                    # Step 4: Simulate
                    sim_result = await self.simulate(opp)
                    
                    if not sim_result['success']:
                        continue
                    
                    actual_profit = sim_result['profit']
                    actual_gas = sim_result['gas_used']
                    
                    # Step 5: Verify profitability after simulation
                    gas_cost = actual_gas * gas_price
                    net_profit = actual_profit - gas_cost
                    
                    if net_profit < self.config['min_profit_eth']:
                        continue
                    
                    # Step 6: Submit via Flashbots
                    tx = self.build_transaction(opp, actual_gas, gas_price)
                    
                    target_block = block['number'] + 1
                    result = await self.flashbots.submit_bundle(
                        [tx], target_block
                    )
                    
                    # Step 7: Track result
                    self.track_result(opp, result, net_profit, gas_cost)
                    
                    # Only execute one opportunity per block
                    break
                    
            except Exception as e:
                self.handle_error(e)
    
    def find_opportunities(self, pools: dict, gas_price: float) -> List[dict]:
        """
        Find all profitable arbitrage opportunities from current pool states.
        """
        opportunities = []
        
        # Check all pool pairs
        pool_list = list(pools.values())
        
        for i in range(len(pool_list)):
            for j in range(i + 1, len(pool_list)):
                pool_a = pool_list[i]
                pool_b = pool_list[j]
                
                # Must be same token pair
                if pool_a['tokens'] != pool_b['tokens']:
                    continue
                
                # Calculate optimal arbitrage
                arb = self.calculate_arbitrage(pool_a, pool_b, gas_price)
                
                if arb and arb['profit'] > 0:
                    opportunities.append(arb)
        
        # Also check multi-hop routes
        multi_hop = self.find_multi_hop_opportunities(pool_list, gas_price)
        opportunities.extend(multi_hop)
        
        return opportunities
    
    async def simulate(self, opportunity: dict) -> dict:
        """
        Simulate the arbitrage transaction using eth_call or Tenderly.
        """
        # Build the transaction
        tx_data = self.contract.functions.executeArbitrage(
            opportunity['params']
        ).build_transaction({
            'from': self.account,
            'gas': 1_000_000,  # High gas limit for simulation
            'gasPrice': 0,     # Free simulation
        })
        
        try:
            # Simulate using eth_call
            result = await self.web3.eth.call(tx_data)
            
            # Decode result
            profit = self.decode_profit(result)
            gas_estimate = await self.web3.eth.estimate_gas(tx_data)
            
            return {
                'success': True,
                'profit': profit,
                'gas_used': gas_estimate,
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'profit': 0,
                'gas_used': 0,
            }
    
    def build_transaction(self, opportunity: dict, gas_limit: int, 
                          gas_price: float) -> dict:
        """Build the final transaction for submission."""
        # Calculate priority fee (competitive bid)
        profit_wei = int(opportunity['profit'] * 10**18)
        gas_cost_wei = gas_limit * int(gas_price * 10**9)
        
        # Bid fraction of remaining profit as priority fee
        remaining = profit_wei - gas_cost_wei
        priority_fee = int(remaining * 0.7)  # Give 70% to builder
        priority_fee_gwei = priority_fee // gas_limit
        
        tx = self.contract.functions.executeArbitrage(
            opportunity['params']
        ).build_transaction({
            'from': self.account,
            'gas': int(gas_limit * 1.1),  # 10% buffer
            'maxFeePerGas': int((gas_price + priority_fee_gwei) * 10**9),
            'maxPriorityFeePerGas': int(priority_fee_gwei * 10**9),
            'nonce': self.web3.eth.get_transaction_count(self.account),
            'chainId': 1,
        })
        
        return self.web3.eth.account.sign_transaction(tx, self.private_key)
    
    def check_risk_limits(self, opportunity: dict, gas_price: float) -> bool:
        """Check all risk limits before execution."""
        # Daily gas budget
        estimated_gas_cost = 500_000 * gas_price * 10**-9  # In ETH
        if self.daily_gas_spent + estimated_gas_cost > self.config['max_daily_gas_spend_eth']:
            return False
        
        # Gas price limit
        if gas_price > self.config['max_gas_price_gwei']:
            return False
        
        # Pool liquidity check
        if opportunity.get('pool_liquidity', 0) < self.config['min_pool_liquidity_usd']:
            return False
        
        # Loan size limit
        if opportunity.get('loan_amount_eth', 0) > self.config['max_flash_loan_eth']:
            return False
        
        return True
    
    def track_result(self, opportunity, result, net_profit, gas_cost):
        """Track execution results."""
        self.daily_gas_spent += gas_cost
        self.daily_profit += net_profit
        
        print(
            f"[MEV] {'SUCCESS' if result.get('success') else 'FAILED'} | "
            f"Profit: {net_profit:.4f} ETH | "
            f"Gas: {gas_cost:.4f} ETH | "
            f"Route: {opportunity.get('route', 'unknown')}"
        )
```

### 11.3 Monitoring and Alerting

```
MEV Bot Monitoring:
├── Opportunities Detected (per block)
├── Simulations Run / Success Rate
├── Bundles Submitted / Included Rate
├── Profit Per Block (ETH)
├── Gas Spent Per Block (ETH)
├── Competitor Activity (other searchers on same opportunities)
├── Revert Rate
├── Pool States (TVL changes, new pools)
├── Network Conditions (base fee, congestion)
└── Contract Health (balance, approval states)

Alerts:
├── [CRITICAL] Contract exploit detected
├── [HIGH] Revert rate > 50% (possible contract issue)
├── [HIGH] Competitor consistently winning auctions
├── [MEDIUM] Gas price exceeds budget
├── [MEDIUM] Daily loss limit approaching
├── [LOW] New pool detected (potential opportunity)
└── [INFO] Daily summary report
```

---

## 12. References

### Academic Papers

1. **Daian, P., Goldfeder, S., Kell, T., Li, Y., Zhao, X., Bentov, I., Breidenbach, L., & Juels, A.** (2020). "Flash Boys 2.0: Frontrunning in Decentralized Exchanges, Miner Extractable Value, and Consensus Instability." *2020 IEEE Symposium on Security and Privacy (SP)*, 910-927.

2. **Qin, K., Zhou, L., & Gervais, A.** (2022). "Quantifying Blockchain Extractable Value: How Dark is the Forest?" *2022 IEEE Symposium on Security and Privacy (SP)*.

3. **Babel, K., Daian, P., Kelkar, M., & Juels, A.** (2023). "Clockwork Finance: Automated Analysis of Economic Security in Smart Contracts." *2023 IEEE Symposium on Security and Privacy (SP)*.

4. **Park, A.** (2023). "The Conceptual Flaws of Decentralized Automated Market Making." *The Journal of Finance*, 78(4), 2187-2228.

5. **Adams, H., Zinsmeister, N., Salem, M., Keefer, R., & Robinson, D.** (2021). "Uniswap v3 Core." *Uniswap Labs White Paper*.

6. **Shleifer, A., & Vishny, R. W.** (1997). "The Limits of Arbitrage." *The Journal of Finance*, 52(1), 35-55.

### Technical Documentation

- Flashbots Documentation: https://docs.flashbots.net/
- Aave V3 Flash Loans: https://docs.aave.com/developers/guides/flash-loans
- Uniswap V3 Documentation: https://docs.uniswap.org/
- EIP-1559: https://eips.ethereum.org/EIPS/eip-1559
- MEV-Boost: https://boost.flashbots.net/

### Data and Research

- Flashbots MEV-Explore: https://explore.flashbots.net/
- EigenPhi (MEV analytics): https://eigenphi.io/
- Dune Analytics MEV Dashboards: https://dune.com/
- MEV.day Conference Resources: https://flashbots.net/mev-day

### Tools

- Foundry (Smart contract development): https://book.getfoundry.sh/
- Tenderly (Transaction simulation): https://tenderly.co/
- Etherscan (Contract verification): https://etherscan.io/
- OpenZeppelin Contracts: https://docs.openzeppelin.com/contracts/

---

> **Related Documents:**
> - [00_overview.md](./00_overview.md) — Arbitrage Overview
> - [01_triangular_arbitrage.md](./01_triangular_arbitrage.md) — Triangular Arbitrage (DEX variant)
> - [03_cross_exchange_arbitrage.md](./03_cross_exchange_arbitrage.md) — Cross-Exchange (CEX-DEX variant)
