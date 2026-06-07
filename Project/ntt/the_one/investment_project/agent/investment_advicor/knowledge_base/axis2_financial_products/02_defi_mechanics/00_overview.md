# DeFi Advanced Mechanics — Overview

> **Axis 2 — Financial Products | Module 02 — DeFi Mechanics**
> Version: 2.0.0 | Last Updated: 2026-04-12
> Classification: KNOWLEDGE BASE — MULTI-AGENT AI TRADING SYSTEM

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [DeFi Ecosystem Architecture](#2-defi-ecosystem-architecture)
3. [Key Protocols and Their Roles](#3-key-protocols-and-their-roles)
4. [Smart Contract Risk Framework](#4-smart-contract-risk-framework)
5. [Total Value Locked (TVL) Analysis](#5-total-value-locked-tvl-analysis)
6. [DeFi Composability — Money Legos](#6-defi-composability--money-legos)
7. [Why DeFi Matters for Algorithmic Trading](#7-why-defi-matters-for-algorithmic-trading)
8. [Module Map — What This Section Covers](#8-module-map--what-this-section-covers)
9. [Risk Parameters — System-Wide](#9-risk-parameters--system-wide)
10. [Execution Flow — DeFi Opportunity Scanner](#10-execution-flow--defi-opportunity-scanner)
11. [References](#11-references)

---

## 1. Introduction

Decentralized Finance (DeFi) represents a fundamental paradigm shift in financial services:
the replacement of trusted intermediaries with deterministic, auditable smart contract logic
running on public blockchains. For an algorithmic trading system, DeFi is not merely an
alternative venue — it is a programmable financial substrate that enables strategies
impossible in traditional finance.

### 1.1 Scope of This Module

This module (02_defi_mechanics) provides the mathematical, technical, and strategic
foundations required by the Multi-Agent AI Trading System to:

- **Provide liquidity** on Automated Market Makers (AMMs) and earn trading fees.
- **Minimize impermanent loss** through dynamic hedging and range management.
- **Optimize yield** across lending, staking, and farming protocols.
- **Execute flash-loan-based strategies** including arbitrage and collateral restructuring.
- **Manage lending/borrowing positions** with automated health factor monitoring.
- **Stack yields** through liquid staking and restaking mechanisms.

### 1.2 Design Principles

Every document in this module adheres to the following structure:

| Section              | Purpose                                               |
|----------------------|-------------------------------------------------------|
| Core Logic           | Detailed mechanics of the protocol or strategy        |
| Technical Specs      | Precise thresholds, parameters, constants             |
| Mathematical Models  | All formulas in LaTeX notation                        |
| Risk Parameters      | Enumerated risks with severity and mitigation         |
| Execution Flow       | Pseudocode for bot implementation                     |
| References           | Academic papers, whitepapers, protocol documentation  |

---

## 2. DeFi Ecosystem Architecture

### 2.1 Layer Model

The DeFi ecosystem can be understood as a layered architecture, each layer building on
the one below:

```
Layer 5 — Aggregators & Interfaces
         DEX aggregators (1inch, Paraswap), yield aggregators (Yearn),
         portfolio dashboards (Zapper, DeBank)

Layer 4 — Application Protocols
         Lending (Aave, Compound), DEXes (Uniswap, Curve),
         Derivatives (dYdX, GMX), Insurance (Nexus Mutual)

Layer 3 — Asset Layer
         ERC-20 tokens, wrapped assets (WETH, WBTC),
         stablecoins (USDC, DAI), LP tokens, receipt tokens

Layer 2 — Protocol Primitives
         AMM invariants, interest rate models, oracle feeds,
         liquidation engines, governance modules

Layer 1 — Settlement Layer
         Ethereum mainnet, L2 rollups (Arbitrum, Optimism, Base),
         alt-L1s (Solana, Avalanche)

Layer 0 — Consensus & Security
         Proof of Stake validators, MEV supply chain,
         block producers, relay networks
```

### 2.2 Value Flow Diagram

```
Users (Traders, LPs, Borrowers)
    |
    v
Front-ends / Aggregators
    |
    v
Smart Contract Protocols <---> Oracles (Chainlink, Pyth)
    |
    v
Liquidity Pools / Lending Markets
    |
    v
Settlement Layer (L1/L2)
    |
    v
Block Producers / MEV Supply Chain
```

### 2.3 Key Participants

| Participant          | Role                                      | Incentive                    |
|----------------------|-------------------------------------------|------------------------------|
| Liquidity Providers  | Deposit assets into pools                 | Trading fees + token rewards |
| Traders              | Swap tokens via AMM pools                 | Price execution              |
| Borrowers            | Take collateralized loans                 | Leverage, shorting           |
| Lenders              | Supply assets to lending markets          | Interest income              |
| Liquidators          | Close undercollateralized positions        | Liquidation bonus            |
| Arbitrageurs         | Equalize prices across venues             | Price discrepancy profit     |
| Governance holders   | Vote on protocol parameters               | Protocol influence + yield   |
| MEV searchers        | Extract value from transaction ordering   | MEV profit                   |

---

## 3. Key Protocols and Their Roles

### 3.1 Decentralized Exchanges (DEXes)

#### 3.1.1 Uniswap (V2, V3, V4)

- **Mechanism**: Automated Market Maker with constant product (V2) and concentrated
  liquidity (V3/V4).
- **Chain**: Ethereum mainnet + L2 deployments (Arbitrum, Optimism, Base, Polygon).
- **TVL**: Historically $3B-$8B across all deployments.
- **Relevance to Trading System**:
  - Primary venue for long-tail token swaps.
  - LP fee income (0.01%, 0.05%, 0.30%, 1.00% tiers in V3).
  - Concentrated liquidity enables capital-efficient market making.
  - V4 hooks enable custom logic (dynamic fees, TWAMM, limit orders).

#### 3.1.2 Curve Finance

- **Mechanism**: StableSwap invariant optimized for correlated assets.
- **Specialization**: Stablecoin-to-stablecoin and pegged asset swaps.
- **TVL**: Historically $2B-$6B.
- **Key Innovation**: Extremely low slippage for similar-value assets.
- **CRV Wars**: veTokenomics model where protocols compete for CRV emissions
  to direct liquidity to their pools.

#### 3.1.3 Balancer

- **Mechanism**: Generalized weighted pools (any ratio, not just 50/50).
- **Innovation**: Weighted math allows asymmetric exposure.
- **Relevance**: Useful for portfolio-like LP positions (e.g., 80/20 ETH/USDC).

### 3.2 Lending & Borrowing

#### 3.2.1 Aave (V3)

- **Mechanism**: Overcollateralized lending with variable and stable rate options.
- **Key Feature**: E-Mode (efficiency mode) for correlated assets with higher LTV.
- **Flash Loans**: Single-transaction uncollateralized loans.
- **Cross-chain**: Portal feature for cross-chain liquidity.
- **Risk**: Interest rate model, oracle dependence, governance risk.

#### 3.2.2 Compound (V3 — Comet)

- **Mechanism**: Single-borrowable-asset model (e.g., only borrow USDC).
- **Simplification**: Reduced attack surface vs multi-asset markets.
- **COMP Rewards**: Governance token distribution to users.

### 3.3 Liquid Staking

#### 3.3.1 Lido (stETH)

- **Mechanism**: Pooled ETH staking with a liquid derivative token (stETH).
- **Market Share**: ~30% of all staked ETH (dominant liquid staking provider).
- **Yield Source**: Ethereum consensus layer rewards + execution layer tips.
- **Risk**: Smart contract, slashing, stETH/ETH de-peg.

#### 3.3.2 Rocket Pool (rETH)

- **Mechanism**: Decentralized node operator network.
- **Advantage**: More decentralized than Lido.
- **rETH Model**: Appreciating token (value increases vs ETH over time).

### 3.4 Restaking

#### 3.4.1 EigenLayer

- **Mechanism**: Re-use staked ETH security for additional protocols (AVSs).
- **Yield Stacking**: Ethereum staking yield + AVS rewards.
- **Risk**: Additive slashing conditions, smart contract risk, complexity.

### 3.5 Yield Aggregators

#### 3.5.1 Yearn Finance

- **Mechanism**: Automated vault strategies that optimize yield across protocols.
- **Strategy**: Deposit assets -> vault allocates to best yield source.
- **Fee**: Management fee + performance fee on profits.

#### 3.5.2 Beefy Finance

- **Mechanism**: Auto-compounding vaults across multiple chains.
- **Focus**: Harvest rewards -> sell -> compound into LP position.

### 3.6 Derivatives

#### 3.6.1 GMX / dYdX

- **Mechanism**: Perpetual futures with on-chain settlement.
- **Relevance**: Hedging IL, delta-neutral strategies, basis trading.

### 3.7 Protocol Comparison Matrix

| Protocol    | Category    | Fee Model          | Risk Level | Capital Efficiency | Composability |
|-------------|-------------|--------------------|------------|--------------------|---------------|
| Uniswap V3  | DEX         | 0.01-1% per swap   | Medium     | Very High          | Very High     |
| Curve       | DEX         | 0.04% per swap     | Medium     | High (stables)     | Very High     |
| Aave V3     | Lending     | Variable interest  | Medium     | High               | Very High     |
| Lido        | Staking     | 10% of rewards     | Medium     | High               | High          |
| EigenLayer  | Restaking   | AVS-defined        | High       | Medium             | Medium        |
| Yearn       | Aggregator  | 2% + 20% perf      | Medium-High| High               | Medium        |

---

## 4. Smart Contract Risk Framework

### 4.1 Risk Taxonomy

Smart contract risk is the single most important risk category in DeFi. Unlike traditional
finance where counterparty risk is mitigated by regulation and insurance, DeFi risk is
primarily technical.

```
Smart Contract Risk
├── Code-Level Risks
│   ├── Re-entrancy attacks
│   ├── Integer overflow/underflow
│   ├── Access control vulnerabilities
│   ├── Logic errors in state transitions
│   ├── Flash loan attack vectors
│   └── Oracle manipulation
├── Design-Level Risks
│   ├── Economic model failures (death spirals)
│   ├── Governance attacks (vote manipulation)
│   ├── Incentive misalignment
│   └── Composability risk (cascading failures)
├── Infrastructure Risks
│   ├── Bridge exploits (cross-chain risk)
│   ├── Oracle failure or manipulation
│   ├── RPC / node reliability
│   └── MEV extraction (sandwich attacks)
└── Operational Risks
    ├── Admin key compromise
    ├── Upgrade proxy manipulation
    ├── Timelock bypass
    └── Frontend compromise (DNS hijack)
```

### 4.2 Risk Scoring Model

For the trading system, each protocol interaction is scored:

$$
R_{total} = w_1 \cdot R_{audit} + w_2 \cdot R_{tvl} + w_3 \cdot R_{age} + w_4 \cdot R_{complexity} + w_5 \cdot R_{admin}
$$

Where:

| Factor           | Weight ($w_i$) | Score Range | Description                                |
|------------------|----------------|-------------|--------------------------------------------|
| $R_{audit}$      | 0.25           | 0-10        | Number and quality of audits               |
| $R_{tvl}$        | 0.20           | 0-10        | TVL as proxy for battle-testing            |
| $R_{age}$        | 0.15           | 0-10        | Time since deployment without exploit      |
| $R_{complexity}$ | 0.25           | 0-10        | Code complexity, number of external calls  |
| $R_{admin}$      | 0.15           | 0-10        | Degree of admin control / upgradeability   |

**Risk Classification**:

| Score Range | Classification | Max Allocation |
|-------------|----------------|----------------|
| 8.0 - 10.0 | Low Risk       | Up to 30% of DeFi allocation |
| 6.0 - 7.9  | Medium Risk    | Up to 15% of DeFi allocation |
| 4.0 - 5.9  | Elevated Risk  | Up to 5% of DeFi allocation  |
| 0.0 - 3.9  | High Risk      | No allocation (monitoring only) |

### 4.3 Historical Exploit Analysis

| Date       | Protocol       | Loss       | Attack Vector              | Lesson                          |
|------------|----------------|------------|----------------------------|---------------------------------|
| 2022-03    | Ronin Bridge   | $624M      | Compromised validator keys | Centralized bridge risk         |
| 2022-02    | Wormhole       | $320M      | Signature verification bug | Cross-chain complexity          |
| 2022-04    | Beanstalk      | $182M      | Flash loan governance      | Governance attack surface       |
| 2023-03    | Euler Finance  | $197M      | Donation + liquidation     | Novel attack vectors            |
| 2023-07    | Curve Finance  | $73M       | Vyper compiler re-entrancy | Compiler-level vulnerabilities  |

### 4.4 Audit Requirements for Trading System

Before the trading system interacts with any protocol, the following checks must pass:

```
AUDIT CHECKLIST:
[x] At least 2 independent audits by reputable firms
[x] Bug bounty program active (minimum $500K)
[x] TVL > $100M for at least 6 months
[x] No critical exploits in past 12 months
[x] Open-source and verified on block explorer
[x] Timelock on admin functions (minimum 48 hours)
[x] No single admin key — multisig required
[x] Oracle diversity (not single oracle dependency)
```

---

## 5. Total Value Locked (TVL) Analysis

### 5.1 TVL as a Market Health Indicator

Total Value Locked (TVL) represents the aggregate value of assets deposited in DeFi
protocols. It serves as a proxy for:

- **Protocol trust**: Higher TVL implies greater user confidence.
- **Liquidity depth**: More TVL generally means lower slippage for trades.
- **Yield opportunity**: TVL dynamics create yield differentials.
- **Market sentiment**: TVL trends correlate with broader crypto market cycles.

### 5.2 TVL Calculation

$$
TVL_{protocol} = \sum_{i=1}^{N} Q_i \cdot P_i
$$

Where:
- $Q_i$ = quantity of token $i$ deposited in the protocol
- $P_i$ = current USD price of token $i$
- $N$ = total number of token types in the protocol

**Important caveat**: TVL is denominated in USD, so it changes with asset prices even
if no deposits/withdrawals occur. Real TVL analysis should decompose:

$$
\Delta TVL = \Delta TVL_{flow} + \Delta TVL_{price}
$$

Where:
- $\Delta TVL_{flow}$ = TVL change due to actual deposits/withdrawals
- $\Delta TVL_{price}$ = TVL change due to asset price movements

### 5.3 TVL-Yield Relationship

There is generally an inverse relationship between pool TVL and yield:

$$
Y_{fee} \approx \frac{V_{daily} \cdot f}{TVL}
$$

Where:
- $Y_{fee}$ = daily fee yield
- $V_{daily}$ = daily trading volume
- $f$ = fee rate
- $TVL$ = total value locked in the pool

This means:
- **Low TVL + High Volume** = high yield (but also higher risk).
- **High TVL + Low Volume** = low yield (but more stable).

### 5.4 TVL Analysis Signals for Trading

| Signal                                  | Interpretation                           | Action                      |
|-----------------------------------------|------------------------------------------|-----------------------------|
| TVL rising + Volume rising              | Growing protocol, healthy                | Consider LP entry           |
| TVL rising + Volume flat                | Yield farming dilution                   | Monitor yield compression   |
| TVL falling + Volume stable             | Smart money exiting                      | Review risk, consider exit  |
| TVL falling + Volume falling            | Protocol declining                       | Exit positions              |
| Sudden TVL spike                        | Whale deposit or incentive launch        | Analyze sustainability      |
| Sudden TVL drop                         | Potential exploit or fear event          | Immediate risk assessment   |

### 5.5 Cross-Chain TVL Distribution

The trading system monitors TVL distribution across chains to identify:

- **Yield arbitrage**: Same protocol, different chains, different yields.
- **Liquidity migration**: Capital flowing from one chain to another.
- **New chain opportunities**: Early TVL on new chains often means higher yields.

```
TVL Distribution Snapshot (Illustrative):
Ethereum:      55-60% of total DeFi TVL
Tron:          10-12%
BSC:           5-8%
Arbitrum:      4-6%
Solana:        3-5%
Avalanche:     2-3%
Optimism:      2-3%
Base:          2-3%
Polygon:       1-2%
Others:        5-10%
```

---

## 6. DeFi Composability — Money Legos

### 6.1 What Is Composability?

Composability is DeFi's defining advantage over traditional finance. It means that any
protocol can be combined with any other protocol in a single transaction, without
permission. This is possible because:

1. **Open interfaces**: Smart contracts expose public functions callable by anyone.
2. **Shared state**: All protocols read from the same blockchain state.
3. **Atomic execution**: Multiple protocol interactions execute in one transaction
   (all succeed or all revert).
4. **Permissionless integration**: No API keys, no agreements, no approvals needed.

### 6.2 Composability Patterns

#### Pattern 1: Yield Stacking

```
ETH -> Lido (stETH) -> Aave (deposit as collateral) -> Borrow USDC -> Curve (LP)
```

**Yield Sources**:
- Layer 1: ETH staking yield (~3-5% APR)
- Layer 2: Potential Aave supply yield on stETH
- Layer 3: Curve LP fees + CRV rewards on borrowed USDC

**Risk**: Each layer adds smart contract risk and liquidation risk.

#### Pattern 2: Leveraged Yield Farming

```
USDC -> Aave (deposit) -> Borrow ETH -> Uniswap V3 (LP ETH/USDC) -> Fees
                ^                                                      |
                |______________________ Repay loop ____________________|
```

#### Pattern 3: Flash Loan Arbitrage

```
Aave Flash Loan (borrow USDC)
  -> Uniswap (buy ETH cheap)
  -> Curve (sell ETH for more USDC)
  -> Repay flash loan + fee
  -> Profit
```

#### Pattern 4: Collateral Optimization

```
Aave (deposit ETH, borrow USDC)
  -> Flash Loan (borrow DAI)
  -> Swap DAI for ETH
  -> Deposit ETH in Aave (increase collateral)
  -> Borrow more USDC
  -> Repay flash loan
  -> Net: Leveraged long ETH
```

### 6.3 Composability Risk — Cascading Failures

The same composability that enables powerful strategies also creates systemic risk:

```
Failure Cascade Example:

1. Oracle reports incorrect price for Token A
2. Lending protocol allows undercollateralized borrow
3. Borrowed tokens dumped on DEX, crashing price
4. Other lending markets begin liquidations
5. DEX LPs suffer massive impermanent loss
6. Yield farms built on those LP tokens collapse
7. Stablecoin backed by yield farm tokens de-pegs
```

**Historical example**: The Terra/LUNA collapse (May 2022) demonstrated how a
stablecoin failure can cascade through the entire DeFi ecosystem.

### 6.4 Composability Graph for Trading System

The trading system models DeFi composability as a directed acyclic graph (DAG):

```
Nodes: Protocols, assets, positions
Edges: Dependencies, collateral relationships, yield flows
Weight: Risk contribution, yield contribution
```

$$
R_{composite} = 1 - \prod_{i=1}^{N} (1 - R_i)
$$

Where $R_{composite}$ is the composite risk of a multi-protocol strategy and $R_i$ is the
individual risk of each protocol layer. This shows that risk compounds rapidly:

| Layers | Individual Risk | Composite Risk |
|--------|----------------|----------------|
| 1      | 2%             | 2.0%           |
| 2      | 2%             | 3.96%          |
| 3      | 2%             | 5.88%          |
| 4      | 2%             | 7.76%          |
| 5      | 2%             | 9.61%          |

---

## 7. Why DeFi Matters for Algorithmic Trading

### 7.1 Unique Advantages

#### 7.1.1 Programmable Execution

DeFi allows the trading system to encode complex multi-step strategies in a single
atomic transaction. In traditional finance, a strategy involving borrowing, swapping,
and providing liquidity would require multiple counterparties, settlement periods, and
manual coordination. In DeFi, this executes in one block (~12 seconds on Ethereum).

#### 7.1.2 Transparent Order Book / AMM State

All DeFi state is public and queryable. The trading system can:

- Read every pool's reserves in real-time.
- Monitor every pending transaction in the mempool.
- Calculate exact execution prices before submitting.
- Simulate transactions before sending (via `eth_call`).

#### 7.1.3 24/7 Markets with No Gatekeepers

DeFi operates continuously. There are no market hours, no circuit breakers (in most
protocols), and no exchange approvals needed. This enables:

- Continuous yield generation.
- Round-the-clock arbitrage monitoring.
- Instant reaction to market events.

#### 7.1.4 Yield Generation as a Base Layer

Unlike traditional markets where holding assets is passive, DeFi allows every asset to
be productive:

$$
Y_{total} = Y_{staking} + Y_{lending} + Y_{LP} + Y_{farming} + Y_{restaking}
$$

A well-optimized portfolio can earn yield on every component simultaneously.

### 7.2 Challenges for Algorithmic Trading in DeFi

| Challenge              | Description                                       | Mitigation                      |
|------------------------|---------------------------------------------------|---------------------------------|
| MEV                    | Bots front-run, back-run, sandwich trades         | Private mempools (Flashbots)    |
| Gas costs              | Transaction fees eat into profits                 | Gas optimization, L2 deployment |
| Smart contract risk    | Code bugs can drain funds                         | Audit checks, position limits   |
| Oracle latency         | Price feeds lag real market                        | Multiple oracle sources         |
| Liquidity fragmentation| Liquidity spread across chains                    | Cross-chain aggregation         |
| Regulatory uncertainty | Evolving legal landscape                          | Compliance monitoring           |
| Impermanent loss       | LP value < holding value                          | Hedging, dynamic rebalancing    |

### 7.3 DeFi Alpha Sources for the Trading System

```
Alpha Source 1: AMM Liquidity Provision
  - Earn trading fees by providing concentrated liquidity
  - Optimize range for maximum fee capture
  - Hedge directional risk

Alpha Source 2: Cross-Venue Arbitrage
  - DEX-DEX price discrepancies
  - DEX-CEX price discrepancies
  - Cross-chain price discrepancies

Alpha Source 3: Lending Rate Arbitrage
  - Borrow at low rate on Protocol A
  - Lend at higher rate on Protocol B
  - Net interest income

Alpha Source 4: Liquidation
  - Monitor undercollateralized positions
  - Execute liquidations for profit
  - Requires fast execution and capital

Alpha Source 5: Yield Optimization
  - Rotate capital to highest risk-adjusted yield
  - Auto-compound rewards
  - Minimize gas costs

Alpha Source 6: Governance Value Extraction
  - Vote-escrowed tokens (veTokens) direct emissions
  - Bribing platforms (Votium, Hidden Hand)
  - Governance token accumulation
```

---

## 8. Module Map — What This Section Covers

This DeFi Mechanics module contains the following documents:

```
02_defi_mechanics/
├── 00_overview.md                      [THIS FILE]
│   Overview, ecosystem map, risk framework
│
├── 01_amm_concentrated_liquidity.md
│   AMM math (CPMM, StableSwap, Weighted),
│   Uniswap V3 concentrated liquidity deep dive,
│   LP strategy and JIT liquidity
│
├── 02_impermanent_loss.md
│   IL derivation, amplified IL for concentrated LP,
│   hedging strategies, break-even analysis
│
├── 03_yield_strategies.md
│   Yield farming mechanics, auto-compounding math,
│   aggregator strategies, harvest optimization
│
├── 04_flash_loans_composability.md
│   Flash loan mechanics, use cases (arb, collateral swap),
│   attack vectors (for defense), composability patterns
│
├── 05_lending_borrowing.md
│   Interest rate models, utilization rates,
│   liquidation mechanics, recursive lending
│
└── 06_liquid_staking_restaking.md
    Liquid staking (Lido, Rocket Pool),
    restaking (EigenLayer), yield stacking
```

### 8.1 Document Dependencies

```
00_overview ──────────────────────────────────────────────────
    |         |          |           |          |           |
    v         v          v           v          v           v
  01_amm   02_IL    03_yield    04_flash   05_lending  06_staking
    |         |          |           |          |           |
    |    depends on     |      uses 01,05      |      uses 05
    |      01_amm       |           |          |           |
    |         |          |           |          |           |
    v         v          v           v          v           v
   [Combined Strategy Layer — uses all modules]
```

---

## 9. Risk Parameters — System-Wide

### 9.1 Global DeFi Risk Limits

These parameters govern the trading system's overall DeFi exposure:

| Parameter                        | Value    | Rationale                              |
|----------------------------------|----------|----------------------------------------|
| Max DeFi allocation (% of AUM)   | 25%      | Limit smart contract exposure          |
| Max single-protocol allocation    | 10%      | Diversification across protocols       |
| Max single-chain allocation       | 15%      | Chain-level risk mitigation            |
| Min health factor (lending)       | 1.50     | Buffer above liquidation threshold     |
| Max composability depth           | 3 layers | Limit cascading risk                   |
| Max IL tolerance (per position)   | -5%      | Exit if IL exceeds threshold           |
| Gas cost budget (% of yield)      | 15%      | Ensure yield is net-positive after gas |
| Emergency exit trigger            | -10%     | Portfolio-level DeFi drawdown limit    |

### 9.2 Position Monitoring Intervals

| Metric                  | Check Frequency | Alert Threshold          |
|-------------------------|-----------------|--------------------------|
| Health factor           | Every block     | Below 1.80               |
| LP range status         | Every 30 sec    | Price within 5% of range |
| Yield rate change       | Every 5 min     | > 20% change             |
| TVL change              | Every 15 min    | > 10% drop in 1 hour     |
| Smart contract events   | Every block     | Pause events, admin txns |
| Oracle price deviation  | Every block     | > 2% from market price   |
| Gas price               | Every block     | Above profitability limit|

### 9.3 Circuit Breakers

```
IF any of these conditions are met, HALT all DeFi operations:

1. Protocol TVL drops > 25% in 1 hour
2. Oracle price deviates > 5% from multiple sources
3. Unrecognized admin transaction detected
4. Gas price exceeds 500 gwei sustained for 10 minutes
5. System health factor drops below 1.30 on any position
6. Smart contract pause event detected
7. Bridge exploit reported on any connected chain
8. Stablecoin de-peg > 2% (USDC, USDT, DAI)
```

---

## 10. Execution Flow — DeFi Opportunity Scanner

### 10.1 Main Scanner Loop

```python
class DeFiOpportunityScanner:
    """
    Continuously scans DeFi protocols for yield opportunities,
    arbitrage, and risk events.
    """

    def __init__(self, config: DeFiConfig):
        self.protocols = config.approved_protocols
        self.risk_limits = config.risk_limits
        self.positions = PositionManager()
        self.oracle = MultiOracleAggregator()
        self.gas_estimator = GasEstimator()

    async def run_scan_loop(self):
        """Main scanning loop — runs continuously."""
        while True:
            try:
                # Phase 1: Data Collection
                market_state = await self.collect_market_state()

                # Phase 2: Risk Check on Existing Positions
                risk_alerts = await self.check_position_health(market_state)
                if risk_alerts.has_critical():
                    await self.execute_emergency_actions(risk_alerts)
                    continue

                # Phase 3: Opportunity Identification
                opportunities = await self.identify_opportunities(market_state)

                # Phase 4: Risk-Adjusted Ranking
                ranked = self.rank_opportunities(opportunities)

                # Phase 5: Execution Decision
                for opp in ranked:
                    if self.passes_risk_checks(opp):
                        if self.is_profitable_after_gas(opp):
                            await self.execute_opportunity(opp)

                # Phase 6: Position Maintenance
                await self.rebalance_existing_positions(market_state)

                await asyncio.sleep(self.config.scan_interval)

            except Exception as e:
                logger.error(f"Scanner error: {e}")
                await self.alert_system.notify(e)

    async def collect_market_state(self) -> MarketState:
        """Collect state from all monitored protocols in parallel."""
        tasks = []
        for protocol in self.protocols:
            tasks.append(protocol.get_state())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return MarketState(
            pool_states={p.name: r for p, r in zip(self.protocols, results)
                        if not isinstance(r, Exception)},
            gas_price=await self.gas_estimator.get_current(),
            oracle_prices=await self.oracle.get_all_prices(),
            timestamp=time.time()
        )

    async def identify_opportunities(self, state: MarketState) -> List[Opportunity]:
        """Identify all potential opportunities across DeFi."""
        opportunities = []

        # Check yield opportunities
        yield_opps = await self.yield_scanner.scan(state)
        opportunities.extend(yield_opps)

        # Check arbitrage opportunities
        arb_opps = await self.arb_scanner.scan(state)
        opportunities.extend(arb_opps)

        # Check liquidation opportunities
        liq_opps = await self.liquidation_scanner.scan(state)
        opportunities.extend(liq_opps)

        # Check LP rebalancing needs
        rebal_opps = await self.lp_scanner.scan(state)
        opportunities.extend(rebal_opps)

        return opportunities

    def rank_opportunities(self, opportunities: List[Opportunity]) -> List[Opportunity]:
        """Rank by risk-adjusted return."""
        for opp in opportunities:
            opp.score = (
                opp.expected_return
                * (1 - opp.risk_score)
                * opp.confidence
                / max(opp.gas_cost, 0.001)
            )
        return sorted(opportunities, key=lambda o: o.score, reverse=True)

    def passes_risk_checks(self, opp: Opportunity) -> bool:
        """Verify opportunity passes all risk parameters."""
        checks = [
            opp.protocol in self.approved_protocols,
            opp.risk_score <= self.risk_limits.max_risk_score,
            self.positions.exposure(opp.protocol) + opp.size
                <= self.risk_limits.max_protocol_allocation,
            self.positions.chain_exposure(opp.chain) + opp.size
                <= self.risk_limits.max_chain_allocation,
            opp.composability_depth <= self.risk_limits.max_composability_depth,
        ]
        return all(checks)

    def is_profitable_after_gas(self, opp: Opportunity) -> bool:
        """Ensure opportunity is profitable after gas costs."""
        gas_cost_usd = opp.estimated_gas * self.gas_price_gwei * ETH_PRICE / 1e9
        net_profit = opp.expected_return - gas_cost_usd
        return net_profit > self.risk_limits.min_profit_threshold
```

### 10.2 Position Health Monitor

```python
class PositionHealthMonitor:
    """
    Monitors all DeFi positions for risk events.
    Executes protective actions when thresholds breached.
    """

    async def check_all_positions(self, state: MarketState) -> List[RiskAlert]:
        alerts = []

        for position in self.positions.active():
            # Check lending health factor
            if position.type == PositionType.LENDING:
                hf = await self.calculate_health_factor(position, state)
                if hf < self.thresholds.critical_hf:  # 1.30
                    alerts.append(RiskAlert.CRITICAL_HEALTH_FACTOR(position, hf))
                elif hf < self.thresholds.warning_hf:  # 1.80
                    alerts.append(RiskAlert.WARNING_HEALTH_FACTOR(position, hf))

            # Check LP range status
            elif position.type == PositionType.LP:
                current_price = state.oracle_prices[position.pair]
                if not position.is_in_range(current_price):
                    alerts.append(RiskAlert.OUT_OF_RANGE(position, current_price))
                elif position.distance_to_boundary(current_price) < 0.05:
                    alerts.append(RiskAlert.NEAR_RANGE_BOUNDARY(position))

            # Check IL threshold
            if position.type == PositionType.LP:
                il = self.calculate_il(position, state)
                if il < self.thresholds.max_il:  # -5%
                    alerts.append(RiskAlert.IL_THRESHOLD(position, il))

            # Check TVL changes
            pool_tvl = state.get_pool_tvl(position.pool)
            if position.entry_tvl and pool_tvl < position.entry_tvl * 0.75:
                alerts.append(RiskAlert.TVL_DROP(position, pool_tvl))

        return alerts
```

---

## 11. References

### Academic Papers

1. Adams, H., Zinsmeister, N., Robinson, D. (2020). "Uniswap v2 Core."
   https://uniswap.org/whitepaper.pdf

2. Adams, H., Zinsmeister, N., Salem, M., Keefer, R., Robinson, D. (2021).
   "Uniswap v3 Core." https://uniswap.org/whitepaper-v3.pdf

3. Egorov, M. (2019). "StableSwap — Efficient Mechanism for Stablecoin Liquidity."
   Curve Finance Whitepaper.

4. Martinelli, F., Mushegian, N. (2019). "A Non-Custodial Portfolio Manager,
   Liquidity Provider, and Price Sensor." Balancer Whitepaper.

5. Daian, P., Goldfeder, S., Kell, T., et al. (2020). "Flash Boys 2.0:
   Frontrunning in Decentralized Exchanges, Miner Extractable Value, and Consensus
   Instability." IEEE Symposium on Security and Privacy.

6. Gudgeon, L., Perez, D., Harz, D., Livshits, B., Gervais, A. (2020).
   "The Decentralized Financial Crisis." Crypto Valley Conference.

### Protocol Documentation

7. Aave V3 Documentation. https://docs.aave.com/
8. Compound V3 (Comet) Documentation. https://docs.compound.finance/
9. Lido Documentation. https://docs.lido.fi/
10. EigenLayer Documentation. https://docs.eigenlayer.xyz/
11. Yearn Finance Documentation. https://docs.yearn.fi/
12. Curve Finance Documentation. https://resources.curve.fi/

### Data Sources

13. DefiLlama — TVL aggregator. https://defillama.com/
14. Dune Analytics — On-chain data. https://dune.com/
15. Token Terminal — Protocol financials. https://tokenterminal.com/

---

> **Next Document**: [01_amm_concentrated_liquidity.md](./01_amm_concentrated_liquidity.md)
> — Deep dive into AMM mathematics and concentrated liquidity mechanics.
