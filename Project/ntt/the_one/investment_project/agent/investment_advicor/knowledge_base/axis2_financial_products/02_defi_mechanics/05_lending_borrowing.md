# Lending & Borrowing Protocols — Complete Mechanics

> **Axis 2 — Financial Products | Module 02 — DeFi Mechanics | Document 05**
> Version: 2.0.0 | Last Updated: 2026-04-12
> Classification: KNOWLEDGE BASE — MULTI-AGENT AI TRADING SYSTEM

---

## Table of Contents

1. [Introduction to DeFi Lending](#1-introduction-to-defi-lending)
2. [Aave and Compound Mechanics](#2-aave-and-compound-mechanics)
3. [Interest Rate Models](#3-interest-rate-models)
4. [Utilization Rate and Its Impact](#4-utilization-rate-and-its-impact)
5. [Collateral Factors and Liquidation Thresholds](#5-collateral-factors-and-liquidation-thresholds)
6. [Health Factor Monitoring](#6-health-factor-monitoring)
7. [Recursive Lending (Leverage Loops)](#7-recursive-lending-leverage-loops)
8. [Liquidation Bot Mechanics](#8-liquidation-bot-mechanics)
9. [Risk Parameters for Lending Strategies](#9-risk-parameters-for-lending-strategies)
10. [Advanced Lending Strategies](#10-advanced-lending-strategies)
11. [Cross-Protocol Lending Optimization](#11-cross-protocol-lending-optimization)
12. [Execution Flow — Automated Lending Manager](#12-execution-flow--automated-lending-manager)
13. [References](#13-references)

---

## 1. Introduction to DeFi Lending

### 1.1 Overview

DeFi lending protocols enable permissionless, overcollateralized borrowing and lending.
Unlike traditional finance where creditworthiness determines loan access, DeFi lending
is entirely collateral-based — anyone can borrow if they provide sufficient collateral.

### 1.2 Key Participants

| Role     | Action                         | Incentive              | Risk                    |
|----------|--------------------------------|------------------------|-------------------------|
| Lender   | Deposits assets into pool      | Earn interest (supply APY) | Smart contract, utilization |
| Borrower | Deposits collateral, borrows   | Leverage, yield, shorting | Liquidation, interest costs |
| Liquidator | Repays undercollateralized debt | Liquidation bonus     | Gas wars, price risk    |
| Protocol | Manages pool parameters        | Protocol fees, governance | Systemic risk, bad debt |

### 1.3 Lending Protocol Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Lending Protocol                     │
│                                                     │
│  ┌───────────┐    ┌──────────────┐    ┌──────────┐ │
│  │ Supply    │    │ Interest Rate│    │ Oracle   │ │
│  │ Pools     │◄──►│ Model        │◄──►│ Module   │ │
│  │ (aTokens) │    └──────────────┘    └──────────┘ │
│  └───────────┘              │                       │
│       │                     │                       │
│       ▼                     ▼                       │
│  ┌───────────┐    ┌──────────────┐                 │
│  │ Borrow    │    │ Liquidation  │                 │
│  │ Positions │◄──►│ Engine       │                 │
│  │ (debt)    │    └──────────────┘                 │
│  └───────────┘                                     │
│                                                     │
│  Governance ──► Risk Parameters ──► Collateral Factors│
└─────────────────────────────────────────────────────┘
```

### 1.4 Market Types

| Type             | Example           | Description                                |
|------------------|-------------------|--------------------------------------------|
| Pooled Lending   | Aave V3, Compound V3 | Shared liquidity pool, algorithmic rates |
| Isolated Markets | Silo Finance, Euler | Separate pools per asset pair             |
| Peer-to-Peer     | Morpho            | Matched lending between individuals        |
| Fixed Rate       | Notional, Term    | Fixed interest rate for fixed duration     |

---

## 2. Aave and Compound Mechanics

### 2.1 Aave V3 Core Mechanics

#### 2.1.1 Supply (Deposit)

When a user supplies an asset to Aave:

1. User deposits token X into the Aave pool.
2. User receives aToken (aX) at 1:1 ratio.
3. aToken balance increases over time (rebasing) reflecting earned interest.
4. Interest compounds automatically every second (continuous).

```
User deposits 1000 USDC
→ Receives 1000 aUSDC
→ After 1 year at 5% APY: Balance shows 1050 aUSDC
→ Withdraw: Burns 1050 aUSDC, receives 1050 USDC
```

#### 2.1.2 aToken Mechanics

aTokens are ERC-20 tokens whose balance automatically increases:

$$
\text{balance}_{aToken}(t) = \text{scaledBalance} \times \text{liquidityIndex}(t)
$$

Where:
- $\text{scaledBalance}$ = user's share (fixed at deposit time)
- $\text{liquidityIndex}(t)$ = cumulative interest multiplier (increases over time)

$$
\text{liquidityIndex}(t) = \text{liquidityIndex}(t_0) \times \left(1 + \frac{R_{supply} \cdot \Delta t}{\text{SECONDS\_PER\_YEAR}}\right)
$$

#### 2.1.3 Borrow Mechanics

When a user borrows:

1. Must have collateral deposited (receiving aTokens).
2. Borrows up to their maximum LTV (Loan-to-Value) ratio.
3. Debt accrues interest over time (variable or stable rate).
4. Debt is represented as variableDebtToken or stableDebtToken.

$$
\text{debt}(t) = \text{scaledDebt} \times \text{variableBorrowIndex}(t)
$$

### 2.2 Compound V3 (Comet) Mechanics

Compound V3 (Comet) is architecturally different from V2:

- **Single borrowable asset** per market (e.g., only USDC can be borrowed).
- **Multiple collateral assets** can back the single borrow.
- **Simplified risk model** (no shared collateral pools).

```
Compound V3 Structure:
┌─────────────────────────────────┐
│ Comet (USDC Market)              │
│                                 │
│ Borrowable: USDC only          │
│                                 │
│ Collateral:                     │
│   - ETH (CF: 82.5%)            │
│   - WBTC (CF: 70%)             │
│   - LINK (CF: 70%)             │
│   - UNI (CF: 68%)              │
│   - COMP (CF: 65%)             │
│                                 │
│ Cannot borrow collateral assets │
│ Simplifies risk management      │
└─────────────────────────────────┘
```

### 2.3 Comparison: Aave V3 vs Compound V3

| Feature              | Aave V3                    | Compound V3 (Comet)        |
|----------------------|----------------------------|----------------------------|
| Borrow assets        | Any listed asset           | Single asset per market    |
| Collateral           | Multi-asset, shared pool   | Multi-asset, isolated      |
| Interest model       | Kinked curve per asset     | Kinked curve (single)      |
| Rate type            | Variable + Stable          | Variable only              |
| Isolation mode       | Yes (for risky assets)     | Built-in (architecture)    |
| E-Mode               | Yes (correlated assets)    | No                         |
| Flash loans          | Yes (all assets)           | No native flash loans      |
| Cross-chain          | Portal (cross-chain credit)| No                         |

### 2.4 E-Mode (Efficiency Mode) — Aave V3

E-Mode allows higher LTV for correlated asset pairs:

```
Normal Mode (ETH collateral, USDC borrow):
  Max LTV: 80%
  Liquidation threshold: 82.5%

E-Mode (stETH collateral, ETH borrow):
  Max LTV: 93%
  Liquidation threshold: 95%
  (Because stETH/ETH are highly correlated)
```

$$
\text{Max Borrow}_{E-mode} = \text{Collateral Value} \times LTV_{E-mode}
$$

E-Mode dramatically increases capital efficiency for correlated pairs.

---

## 3. Interest Rate Models

### 3.1 The Kinked Interest Rate Model

Both Aave and Compound use a **piecewise linear interest rate model** (kinked curve):

$$
R_{borrow} = \begin{cases}
R_{base} + \frac{U}{U_{optimal}} \times R_{slope1} & \text{if } U \leq U_{optimal} \\[10pt]
R_{base} + R_{slope1} + \frac{U - U_{optimal}}{1 - U_{optimal}} \times R_{slope2} & \text{if } U > U_{optimal}
\end{cases}
$$

Where:
- $R_{borrow}$ = current borrow interest rate (annualized)
- $R_{base}$ = base rate (rate when utilization = 0)
- $U$ = current utilization rate ($U = \text{Borrows} / \text{Total Supply}$)
- $U_{optimal}$ = target utilization rate (kink point, typically 80-90%)
- $R_{slope1}$ = rate of increase below optimal (gentle slope)
- $R_{slope2}$ = rate of increase above optimal (steep slope, penalizes over-utilization)

### 3.2 Visual Representation

```
Borrow Rate
    ^
    |                                    /
    |                                   / R_slope2
    |                                  /  (steep)
    |                                 /
    |                    ____________/  <- Kink at U_optimal
    |                   /
    |                  / R_slope1
    |                 /  (gentle)
    |               /
    |   R_base ___/
    |
    +─────────────────────────────────────> Utilization
    0%          U_optimal              100%
                (e.g., 80%)
```

### 3.3 Parameter Examples (Aave V3)

| Asset  | $R_{base}$ | $U_{optimal}$ | $R_{slope1}$ | $R_{slope2}$ | Max Rate     |
|--------|------------|----------------|--------------|--------------|--------------|
| USDC   | 0%         | 90%            | 4%           | 60%          | 64%          |
| USDT   | 0%         | 90%            | 4%           | 72%          | 76%          |
| DAI    | 0%         | 90%            | 4%           | 75%          | 79%          |
| WETH   | 0%         | 80%            | 3.8%         | 80%          | 83.8%        |
| WBTC   | 0%         | 70%            | 4%           | 300%         | 304%         |
| LINK   | 0%         | 45%            | 7%           | 300%         | 307%         |

### 3.4 Supply Rate Derivation

The supply rate is derived from the borrow rate, adjusted for utilization and protocol fees:

$$
R_{supply} = R_{borrow} \times U \times (1 - R_{reserve})
$$

Where:
- $R_{supply}$ = interest rate earned by suppliers
- $R_{borrow}$ = current borrow rate
- $U$ = utilization rate
- $R_{reserve}$ = protocol reserve factor (typically 10-20%)

**Derivation**: Total interest paid by borrowers = Total interest received by suppliers + Protocol fee

$$
R_{borrow} \times \text{TotalBorrowed} = R_{supply} \times \text{TotalSupply} + \text{ProtocolFee}
$$

$$
R_{borrow} \times U \times \text{TotalSupply} = R_{supply} \times \text{TotalSupply} + R_{borrow} \times U \times R_{reserve} \times \text{TotalSupply}
$$

$$
R_{supply} = R_{borrow} \times U \times (1 - R_{reserve})
$$

### 3.5 Interest Accrual (Continuous Compounding)

Interest accrues continuously (per-second in Aave V3):

$$
\text{Debt}(t) = \text{Debt}(t_0) \times \left(1 + \frac{R_{borrow}}{365.25 \times 86400}\right)^{\Delta t}
$$

Where $\Delta t$ is elapsed time in seconds.

For the supply side:

$$
\text{Balance}(t) = \text{Balance}(t_0) \times \left(1 + \frac{R_{supply}}{365.25 \times 86400}\right)^{\Delta t}
$$

### 3.6 Stable vs Variable Rates (Aave)

| Feature    | Variable Rate               | Stable Rate                  |
|------------|-----------------------------|-----------------------------|
| Behavior   | Changes every second        | Fixed until rebalance        |
| Risk       | Rate can spike suddenly     | Rate locked (until rebalance)|
| Cost       | Usually lower (risk premium)| Usually higher (insurance)   |
| Rebalance  | N/A                         | Can be rebalanced by protocol|

**Stable rate rebalance condition**: Protocol can reset stable rate if it is significantly
below the current variable rate (protects liquidity).

### 3.7 APR to APY Conversion

$$
APY = \left(1 + \frac{APR}{n}\right)^n - 1
$$

For per-second compounding ($n$ = 31,536,000 seconds/year):

$$
APY \approx e^{APR} - 1
$$

| APR    | APY (continuous) | Difference |
|--------|------------------|------------|
| 3%     | 3.05%            | +0.05%     |
| 5%     | 5.13%            | +0.13%     |
| 10%    | 10.52%           | +0.52%     |
| 20%    | 22.14%           | +2.14%     |
| 50%    | 64.87%           | +14.87%    |

---

## 4. Utilization Rate and Its Impact

### 4.1 Definition

$$
U = \frac{\text{Total Borrows}}{\text{Total Supply}} = \frac{\text{Total Borrows}}{\text{Total Borrows} + \text{Available Liquidity}}
$$

### 4.2 Impact on Stakeholders

| U Level | Borrower Impact         | Lender Impact          | Protocol Health     |
|---------|-------------------------|------------------------|---------------------|
| 0-50%   | Low rates (cheap borrow)| Low rates (low income) | Healthy, underused  |
| 50-80%  | Moderate rates          | Moderate income        | Optimal             |
| 80-90%  | Rates increasing        | Good income            | Near target         |
| 90-95%  | Rates spiking           | Excellent income       | Liquidity concern   |
| 95-100% | Extreme rates           | Very high income       | Withdrawal difficulty|

### 4.3 Utilization and Withdrawal Risk

When utilization is high, lenders may not be able to withdraw:

$$
\text{Available for Withdrawal} = \text{Total Supply} - \text{Total Borrows} = \text{Total Supply} \times (1 - U)
$$

At $U = 95\%$, only 5% of total supply is available for withdrawal.

**This is why $R_{slope2}$ is steep**: It incentivizes borrowers to repay when
utilization exceeds optimal, freeing liquidity for lenders.

### 4.4 Utilization Monitoring for Trading System

```python
class UtilizationMonitor:
    """
    Monitor utilization rates across lending protocols.
    Signals for lending strategy decisions.
    """

    def analyze_utilization(self, protocol, asset) -> UtilizationAnalysis:
        current_u = protocol.get_utilization(asset)
        u_optimal = protocol.get_optimal_utilization(asset)

        # Determine regime
        if current_u < u_optimal * 0.5:
            regime = "LOW"  # Cheap to borrow, low lending income
        elif current_u < u_optimal:
            regime = "NORMAL"  # Balanced
        elif current_u < u_optimal + 0.05:
            regime = "ELEVATED"  # Rates rising, good for lenders
        else:
            regime = "CRITICAL"  # Very high rates, withdrawal risk

        # Trading signals
        signals = {
            "LOW": {
                "supply_action": "REDUCE",  # Low income
                "borrow_action": "INCREASE",  # Cheap rates
            },
            "NORMAL": {
                "supply_action": "MAINTAIN",
                "borrow_action": "MAINTAIN",
            },
            "ELEVATED": {
                "supply_action": "INCREASE",  # High income
                "borrow_action": "REDUCE",  # Expensive
            },
            "CRITICAL": {
                "supply_action": "MONITOR_EXIT",  # Withdrawal risk
                "borrow_action": "EXIT",  # Emergency repay
            }
        }

        return UtilizationAnalysis(
            current_u=current_u,
            u_optimal=u_optimal,
            regime=regime,
            supply_rate=protocol.get_supply_rate(asset),
            borrow_rate=protocol.get_borrow_rate(asset),
            signals=signals[regime]
        )
```

---

## 5. Collateral Factors and Liquidation Thresholds

### 5.1 Definitions

| Parameter               | Symbol   | Description                                 |
|-------------------------|----------|----------------------------------------------|
| Loan-to-Value (LTV)     | $LTV$    | Max borrow / collateral value ratio          |
| Liquidation Threshold   | $LT$     | Collateral ratio below which liquidation starts |
| Liquidation Bonus       | $LB$     | Discount given to liquidators                |
| Reserve Factor          | $RF$     | % of interest going to protocol treasury     |

Relationship: $LTV < LT$ (always a safety buffer between max borrow and liquidation)

### 5.2 Example Parameters (Aave V3 Ethereum)

| Asset  | Max LTV | Liquidation Threshold | Liquidation Bonus | Reserve Factor |
|--------|---------|----------------------|-------------------|----------------|
| ETH    | 80%     | 82.5%                | 5%                | 15%            |
| WBTC   | 70%     | 75%                  | 6.25%             | 20%            |
| USDC   | 77%     | 80%                  | 4.5%              | 10%            |
| DAI    | 75%     | 80%                  | 4%                | 10%            |
| LINK   | 68%     | 73%                  | 7%                | 20%            |
| AAVE   | 66%     | 73%                  | 7.5%              | 0%             |
| stETH  | 69%     | 81%                  | 7%                | 15%            |

### 5.3 Maximum Borrow Calculation

$$
\text{Max Borrow (USD)} = \sum_{i=1}^{N} \text{Collateral}_i \times P_i \times LTV_i
$$

Where the sum is over all deposited collateral assets.

**Example**:
- Deposit: 10 ETH @ $3000 = $30,000, LTV = 80%
- Deposit: 1 WBTC @ $60,000 = $60,000, LTV = 70%
- Max Borrow: $30,000 \times 0.80 + $60,000 \times 0.70 = $24,000 + $42,000 = $66,000$

### 5.4 Liquidation Trigger Calculation

Liquidation occurs when:

$$
\frac{\text{Total Debt (USD)}}{\sum \text{Collateral}_i \times P_i \times LT_i} \geq 1
$$

Or equivalently: $\text{Health Factor} < 1$

---

## 6. Health Factor Monitoring

### 6.1 Health Factor Definition

$$
HF = \frac{\sum_{i} \text{Collateral}_i \times P_i \times LT_i}{\text{Total Debt (USD)}}
$$

Where:
- $\text{Collateral}_i$ = amount of collateral asset $i$
- $P_i$ = current price of asset $i$
- $LT_i$ = liquidation threshold for asset $i$
- Total Debt = sum of all borrows in USD

### 6.2 Health Factor Interpretation

| HF Range    | Status       | Action                                    |
|-------------|-------------|-------------------------------------------|
| > 3.0       | Very Safe   | Can borrow more if needed                 |
| 2.0 - 3.0   | Safe        | Comfortable buffer                        |
| 1.5 - 2.0   | Moderate    | Monitor closely                           |
| 1.2 - 1.5   | Risky       | Consider adding collateral or repaying    |
| 1.0 - 1.2   | Danger      | Urgent action needed                      |
| < 1.0       | Liquidatable | Position will be/is being liquidated      |

### 6.3 HF Sensitivity Analysis

How much can the collateral price drop before liquidation?

$$
\text{Max Price Drop} = 1 - \frac{1}{HF}
$$

| Current HF | Max Price Drop Before Liquidation |
|------------|----------------------------------|
| 3.0        | 66.7%                            |
| 2.0        | 50.0%                            |
| 1.5        | 33.3%                            |
| 1.3        | 23.1%                            |
| 1.2        | 16.7%                            |
| 1.1        | 9.1%                             |

### 6.4 HF Prediction Model

Predict future HF based on price volatility:

$$
HF(t) = HF_0 \times \frac{P_{collateral}(t)}{P_{collateral}(0)} \times \frac{1}{1 + R_{borrow} \times t}
$$

Expected worst-case HF (VaR approach):

$$
HF_{worst}(T, \alpha) = HF_0 \times e^{-z_\alpha \sigma \sqrt{T}} \times \frac{1}{1 + R_{borrow} \times T}
$$

Where:
- $z_\alpha$ = z-score for confidence level (1.645 for 95%, 2.326 for 99%)
- $\sigma$ = annualized volatility of collateral
- $T$ = time horizon in years

### 6.5 Health Factor Monitor Implementation

```python
class HealthFactorMonitor:
    """
    Monitors health factor for all lending positions.
    Triggers defensive actions when thresholds breached.
    """

    # Threshold levels
    SAFE = 2.0
    WARNING = 1.5
    DANGER = 1.3
    CRITICAL = 1.15
    EMERGENCY = 1.05

    async def monitor_all_positions(self):
        """Monitor HF for all active lending positions."""
        while True:
            for position in self.positions.active():
                hf = await self.calculate_health_factor(position)

                # Update tracking
                position.current_hf = hf
                position.hf_history.append((time.time(), hf))

                # Determine action
                if hf < self.EMERGENCY:
                    await self.emergency_repay(position)
                elif hf < self.CRITICAL:
                    await self.critical_action(position)
                elif hf < self.DANGER:
                    await self.add_collateral_or_repay(position)
                elif hf < self.WARNING:
                    await self.alert_warning(position, hf)

                # Predictive check
                predicted_hf = self.predict_hf(
                    position,
                    time_horizon_hours=24,
                    confidence=0.99
                )
                if predicted_hf < self.DANGER:
                    await self.preemptive_action(position, predicted_hf)

            await asyncio.sleep(12)  # Check every block (~12 seconds)

    async def calculate_health_factor(self, position) -> float:
        """Calculate current health factor using multiple oracle sources."""
        collateral_value_adjusted = 0
        for asset, amount in position.collateral.items():
            price = await self.oracle.get_price(asset)
            lt = self.get_liquidation_threshold(position.protocol, asset)
            collateral_value_adjusted += amount * price * lt

        total_debt = 0
        for asset, amount in position.debt.items():
            price = await self.oracle.get_price(asset)
            total_debt += amount * price

        if total_debt == 0:
            return float('inf')

        return collateral_value_adjusted / total_debt

    def predict_hf(self, position, time_horizon_hours, confidence) -> float:
        """Predict worst-case HF using historical volatility."""
        # Get collateral asset volatility
        vol = self.get_volatility(position.primary_collateral, lookback_days=30)

        # Convert to time horizon
        annual_hours = 365.25 * 24
        vol_period = vol * math.sqrt(time_horizon_hours / annual_hours)

        # Worst-case price decline at confidence level
        z = scipy.stats.norm.ppf(confidence)
        worst_case_decline = math.exp(-z * vol_period)

        # Account for interest accrual
        borrow_rate = position.get_borrow_rate()
        interest_growth = 1 + borrow_rate * time_horizon_hours / annual_hours

        # Predicted worst-case HF
        predicted_hf = position.current_hf * worst_case_decline / interest_growth
        return predicted_hf

    async def emergency_repay(self, position):
        """Emergency: repay debt to prevent liquidation."""
        logger.critical(f"EMERGENCY REPAY: Position {position.id} HF={position.current_hf:.4f}")

        # Option 1: Repay from available balance
        available = await self.get_available_balance(position.debt_asset)
        if available > 0:
            repay_amount = min(available, position.debt_value * 0.3)  # Repay 30%
            await position.protocol.repay(position.debt_asset, repay_amount)
            return

        # Option 2: Flash loan self-liquidation (saves liquidation bonus)
        await self.flash_loan_self_liquidate(position)
```

---

## 7. Recursive Lending (Leverage Loops)

### 7.1 Concept

Recursive lending creates leveraged positions by repeatedly depositing and borrowing:

```
Loop 1: Deposit 1000 USDC → Borrow 800 USDC (80% LTV)
Loop 2: Deposit 800 USDC → Borrow 640 USDC
Loop 3: Deposit 640 USDC → Borrow 512 USDC
Loop 4: Deposit 512 USDC → Borrow 410 USDC
...
Total Supply: 1000 + 800 + 640 + ... = 1000 / (1-0.8) = 5000 USDC
Total Borrow: 800 + 640 + 512 + ... = 4000 USDC
```

### 7.2 Mathematics of Recursive Lending

After $n$ loops with LTV ratio $l$:

$$
\text{Total Supply} = V_0 \cdot \sum_{i=0}^{n-1} l^i = V_0 \cdot \frac{1 - l^n}{1 - l}
$$

$$
\text{Total Borrow} = V_0 \cdot \sum_{i=1}^{n} l^i = V_0 \cdot l \cdot \frac{1 - l^n}{1 - l}
$$

As $n \to \infty$ (maximum recursion):

$$
\text{Total Supply}_{\infty} = \frac{V_0}{1 - l}
$$

$$
\text{Total Borrow}_{\infty} = \frac{V_0 \cdot l}{1 - l}
$$

$$
\text{Effective Leverage} = \frac{1}{1 - l}
$$

| LTV ($l$) | Max Leverage | Max Supply (per $1000 initial) | Max Borrow |
|-----------|-------------|-------------------------------|------------|
| 80%       | 5x          | $5,000                        | $4,000     |
| 85%       | 6.67x       | $6,667                        | $5,667     |
| 90%       | 10x         | $10,000                       | $9,000     |
| 93%       | 14.3x       | $14,286                       | $13,286    |

### 7.3 Net Yield from Recursive Lending

$$
\text{Net Yield} = R_{supply} \times \text{Total Supply} - R_{borrow} \times \text{Total Borrow}
$$

$$
= V_0 \cdot \frac{R_{supply} - l \cdot R_{borrow}}{1 - l}
$$

**Profitable when**: $R_{supply} > l \cdot R_{borrow}$

Or equivalently: $\frac{R_{supply}}{R_{borrow}} > l$

Since $R_{supply} = R_{borrow} \times U \times (1 - RF)$ and $U < 1$, it seems like
this can never be profitable from interest alone. BUT with additional incentives
(COMP, AAVE rewards), the effective supply rate can exceed the borrow rate.

### 7.4 Net Yield with Incentives

$$
\text{Net Yield} = \frac{V_0}{1-l} \cdot (R_{supply} + I_{supply}) - \frac{V_0 \cdot l}{1-l} \cdot (R_{borrow} - I_{borrow})
$$

Where:
- $I_{supply}$ = incentive rate for supplying (e.g., COMP rewards)
- $I_{borrow}$ = incentive rate for borrowing (e.g., COMP rewards for borrowers)

### 7.5 Risk: Health Factor in Recursive Position

$$
HF_{recursive} = \frac{\text{Total Supply} \times LT}{\text{Total Borrow}} = \frac{LT}{l}
$$

For LTV = 80% and LT = 82.5%:
$$
HF = \frac{0.825}{0.80} = 1.03125
$$

**Extremely tight**. Any slight price movement triggers liquidation.

In practice, recursive lending is only safe for:
- **Same-asset loops** (borrow same asset you supply — zero price risk)
- **Correlated asset loops** (stETH supply, ETH borrow — minimal price risk)
- **E-mode** positions (higher LTV available for correlated pairs)

### 7.6 Safe Recursive Lending Strategy

```python
class RecursiveLendingStrategy:
    """
    Implements recursive lending for leveraged yield.
    Only for same-asset or highly correlated pairs.
    """

    def calculate_safe_leverage(
        self,
        supply_asset: str,
        borrow_asset: str,
        correlation: float,
        target_hf: float = 1.5
    ) -> float:
        """Calculate safe leverage given target health factor."""
        lt = self.get_liquidation_threshold(supply_asset)
        ltv = self.get_max_ltv(supply_asset)

        # For same-asset (correlation = 1): HF doesn't change with price
        if supply_asset == borrow_asset or correlation > 0.99:
            # Max leverage = 1 / (1 - ltv)
            # But limit to reasonable level
            max_safe_leverage = lt / (lt - ltv * 0.95)  # 95% of max LTV
            return min(max_safe_leverage, 10)  # Cap at 10x

        # For correlated assets: need buffer for price divergence
        max_divergence = (1 - correlation) * 0.20  # Estimated max divergence
        safe_ltv = ltv * (1 - max_divergence / target_hf)

        leverage = 1 / (1 - safe_ltv)
        return leverage

    async def create_recursive_position(
        self,
        supply_asset: str,
        borrow_asset: str,
        initial_amount: float,
        target_leverage: float,
        protocol: str = "aave"
    ):
        """Create recursive lending position using flash loan for efficiency."""

        # Use flash loan to create position in single transaction
        # (instead of many loop transactions)
        additional_needed = initial_amount * (target_leverage - 1)

        # Flash loan -> deposit all -> borrow -> repay flash loan
        await self.flash_loan_leverage(
            supply_asset=supply_asset,
            borrow_asset=borrow_asset,
            own_capital=initial_amount,
            flash_amount=additional_needed,
            protocol=protocol
        )
```

---

## 8. Liquidation Bot Mechanics

### 8.1 Liquidation Process

When a position's health factor drops below 1.0:

```
Liquidation Process (Aave V3):
1. Liquidator calls liquidationCall(collateralAsset, debtAsset, user, debtToCover)
2. Protocol verifies: HF < 1.0 for the user
3. Protocol calculates collateral to seize:
   collateralAmount = (debtToCover × debtPrice) / collateralPrice × (1 + liquidationBonus)
4. Protocol transfers collateral from user to liquidator
5. Liquidator repays debtToCover of user's debt
6. User's position is partially closed
```

### 8.2 Close Factor

The maximum percentage of debt that can be liquidated in a single transaction:

| Protocol    | Close Factor | Description                          |
|-------------|-------------|---------------------------------------|
| Aave V3     | 50%         | Max 50% of debt per liquidation       |
| Compound V2 | 50%         | Max 50% of debt per liquidation       |
| Compound V3 | Variable    | Based on how underwater the position is|

Exception: If HF < 0.95 (deeply underwater), Aave allows 100% close factor.

### 8.3 Liquidation Profitability

$$
\text{Profit} = \text{Collateral Received (USD)} - \text{Debt Repaid (USD)} - \text{Gas Cost}
$$

$$
= \text{Debt Repaid} \times \frac{\text{Liquidation Bonus}}{1} - \text{Gas Cost}
$$

Wait — more precisely:

$$
\text{Collateral Received} = \frac{\text{Debt Repaid (USD)}}{\text{Collateral Price}} \times (1 + LB)
$$

$$
\text{Profit} = \text{Debt Repaid} \times LB - \text{Swap Slippage} - \text{Gas Cost} - \text{Flash Loan Fee}
$$

### 8.4 Liquidation Bot Architecture

```python
class LiquidationBot:
    """
    Monitors positions across lending protocols and executes
    profitable liquidations using flash loans.
    """

    def __init__(self, config: LiquidationBotConfig):
        self.protocols = config.monitored_protocols
        self.min_profit = config.min_profit_usd  # $50 minimum
        self.gas_estimator = GasEstimator()
        self.flash_loan_provider = FlashLoanProvider()
        self.dex_router = DEXRouter()
        self.position_cache = PositionCache()

    async def main_loop(self):
        """Main liquidation scanning loop."""
        while True:
            # Scan for liquidatable positions
            targets = await self.find_liquidatable_positions()

            for target in targets:
                # Calculate profitability
                profit = await self.calculate_profit(target)

                if profit > self.min_profit:
                    # Attempt liquidation
                    success = await self.execute_liquidation(target)
                    if success:
                        logger.info(f"Liquidated {target.user}: profit ${profit:.2f}")

            await asyncio.sleep(1)  # Check every second for new blocks

    async def find_liquidatable_positions(self) -> List[LiquidationTarget]:
        """Find all positions with HF < 1.0 across protocols."""
        targets = []

        for protocol in self.protocols:
            # Method 1: Event-based (listen for price updates that trigger liquidations)
            new_liquidatable = await protocol.get_liquidatable_positions()

            # Method 2: Cache-based (monitor known at-risk positions)
            at_risk = self.position_cache.get_below_hf(1.05)
            for pos in at_risk:
                current_hf = await protocol.get_health_factor(pos.user)
                if current_hf < 1.0:
                    new_liquidatable.append(pos)

            targets.extend(new_liquidatable)

        return targets

    async def calculate_profit(self, target: LiquidationTarget) -> float:
        """Calculate expected profit from liquidation."""

        # Max debt we can cover (50% close factor)
        max_debt_cover = target.total_debt * 0.5

        # Choose optimal debt amount (might be less than max)
        debt_to_cover = self.optimize_debt_amount(target, max_debt_cover)

        # Calculate collateral received
        collateral_received = (
            debt_to_cover * target.debt_price / target.collateral_price
            * (1 + target.liquidation_bonus)
        )

        # Estimate swap output (selling collateral for debt token)
        swap_output = await self.dex_router.get_quote(
            token_in=target.collateral_asset,
            token_out=target.debt_asset,
            amount_in=collateral_received
        )

        # Calculate costs
        flash_loan_fee = debt_to_cover * 0.0005  # 0.05% Aave fee
        gas_cost = await self.gas_estimator.estimate_liquidation_gas()
        swap_slippage = collateral_received * target.collateral_price * 0.003  # Est. 0.3%

        # Net profit
        profit = swap_output - debt_to_cover - flash_loan_fee - gas_cost - swap_slippage
        return profit

    async def execute_liquidation(self, target: LiquidationTarget) -> bool:
        """Execute liquidation via flash loan."""

        # Build flash loan + liquidation + swap transaction
        params = self.encode_liquidation_params(target)

        # Simulate first
        simulation = await self.simulate_tx(params)
        if not simulation.success:
            logger.debug(f"Simulation failed: {simulation.error}")
            return False

        # Execute via private mempool
        tx_hash = await self.flashbots.send_private_tx(
            self.flash_contract.execute_liquidation(params)
        )

        receipt = await self.web3.wait_for_receipt(tx_hash)
        return receipt.status == 1

    def optimize_debt_amount(self, target, max_amount) -> float:
        """
        Optimize how much debt to cover.
        More debt = more profit but also more slippage.
        """
        # Binary search for optimal amount
        best_profit = 0
        best_amount = 0

        for fraction in [0.1, 0.2, 0.3, 0.4, 0.5]:
            amount = max_amount * fraction
            estimated_profit = self.estimate_profit_for_amount(target, amount)
            if estimated_profit > best_profit:
                best_profit = estimated_profit
                best_amount = amount

        return best_amount
```

### 8.5 Liquidation Competition

Liquidation is highly competitive:

| Factor                    | Impact                              |
|---------------------------|-------------------------------------|
| Gas price bidding         | Higher gas = priority in same block  |
| Private mempool           | Avoids being front-run               |
| Multi-block MEV           | Searchers may hold tx for later block|
| Flashbots bundles         | Atomic inclusion guarantees          |
| Latency                   | Faster detection = first to liquidate|
| Capital efficiency        | Flash loans eliminate capital need   |

---

## 9. Risk Parameters for Lending Strategies

### 9.1 Position-Level Limits

| Parameter                        | Value    | Rationale                         |
|----------------------------------|----------|-----------------------------------|
| Max leverage (same asset)        | 8x       | Limited by LTV and gas costs      |
| Max leverage (correlated asset)  | 4x       | Buffer for price divergence       |
| Max leverage (uncorrelated)      | 2x       | Higher liquidation risk           |
| Target Health Factor             | 1.8-2.5  | Comfortable buffer                |
| Minimum Health Factor (alert)    | 1.5      | Warning trigger                   |
| Minimum Health Factor (action)   | 1.3      | Must add collateral or repay      |
| Maximum single-protocol exposure | 20% AUM  | Diversification                   |
| Maximum utilization for supply   | 85%      | Withdrawal availability           |
| Minimum yield spread             | 2%       | Borrow rate + 2% minimum profit   |

### 9.2 Protocol-Level Risk Assessment

```
LENDING PROTOCOL RISK CHECKLIST:

[x] Multiple independent audits (2+)
[x] Bug bounty > $1M active
[x] Oracle diversity (not single source)
[x] Governance timelock > 48 hours
[x] Interest rate model published and verifiable
[x] TVL > $500M for 12+ months
[x] No bad debt events in past 2 years
[x] Liquidation system proven under stress
[x] Admin keys are multisig (4/7 minimum)
[x] Circuit breakers for extreme price moves
```

### 9.3 Interest Rate Risk

$$
\text{Max Rate Exposure} = \text{Borrowed Amount} \times (\text{Max Possible Rate} - \text{Current Rate})
$$

For variable rate positions, model worst-case rate scenarios:

| Scenario                    | Rate Impact | Action Required              |
|-----------------------------|-------------|-------------------------------|
| Utilization spike (whale withdrawal) | Rate jumps 10x+ | Emergency repay if rate > threshold |
| Market panic (mass borrowing) | Rate increases 2-5x | Reduce position size |
| Incentive ends (reward token) | Net yield drops | Evaluate if still profitable |
| Protocol parameter change     | Rate model changes | Reassess all positions |

---

## 10. Advanced Lending Strategies

### 10.1 Rate Arbitrage Between Protocols

$$
\text{Profit} = V \times (R_{supply,A} - R_{borrow,B})
$$

Where you supply on Protocol A (higher supply rate) and borrow on Protocol B (lower
borrow rate).

**Requirements**:
- Must have collateral on Protocol B.
- Net spread must exceed gas costs of management.
- Must monitor both protocols continuously.

### 10.2 Stable Rate Hunting

When Aave's stable rate is significantly below the current variable rate:

1. Lock in stable borrow rate at low level.
2. When variable rate drops below stable rate, consider switching.
3. When variable rate spikes, the stable rate lock is valuable.

$$
\text{Savings} = V \times (R_{variable,avg} - R_{stable,locked}) \times T
$$

### 10.3 Supply Cap Monitoring

Some protocols have supply caps. When approaching the cap:

- Interest rates may change behavior.
- Early depositors have an advantage.
- Monitor governance proposals for cap increases.

### 10.4 Bad Debt Monitoring

If a protocol accumulates bad debt (undercollateralized positions that cannot be
liquidated profitably), lenders bear the loss. Monitor:

$$
\text{Bad Debt Risk} = \frac{\text{Underwater Positions Value}}{\text{Total Supply}}
$$

If bad debt exceeds protocol reserves, a "haircut" may be applied to all depositors.

### 10.5 Cross-Market Yield Optimization

```python
class CrossMarketOptimizer:
    """
    Optimizes lending/borrowing across multiple protocols.
    """

    def find_optimal_allocation(
        self,
        capital: float,
        protocols: List[LendingProtocol]
    ) -> Dict[str, float]:
        """
        Find optimal lending allocation across protocols.
        Maximize yield subject to risk constraints.
        """
        from scipy.optimize import minimize

        def negative_yield(weights):
            """Negative yield (minimize to maximize yield)."""
            total_yield = 0
            for i, protocol in enumerate(protocols):
                supply_amount = capital * weights[i]
                # Supply rate may depend on how much we supply (changes utilization)
                rate = protocol.estimate_supply_rate_after_deposit(supply_amount)
                total_yield += supply_amount * rate
            return -total_yield

        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: sum(w) - 1},  # Weights sum to 1
        ]

        # Bounds: 0 to max_allocation per protocol
        bounds = [(0, self.max_protocol_allocation) for _ in protocols]

        # Initial guess: equal allocation
        x0 = [1/len(protocols)] * len(protocols)

        result = minimize(negative_yield, x0,
                         bounds=bounds, constraints=constraints)

        return {p.name: w * capital for p, w in zip(protocols, result.x)}
```

---

## 11. Cross-Protocol Lending Optimization

### 11.1 Multi-Protocol Supply Strategy

Deploy capital across multiple lending protocols for:
- **Diversification**: Reduce smart contract risk.
- **Rate optimization**: Chase highest supply rates.
- **Utilization management**: Avoid being locked in high-utilization pools.

$$
\text{Optimal Allocation} = \argmax_{\mathbf{w}} \sum_i w_i \cdot R_{supply,i} - \lambda \cdot \text{Risk}(\mathbf{w})
$$

### 11.2 Borrow Rate Optimization

When borrowing, find the cheapest source:

$$
\text{Cheapest Borrow} = \min_i \{R_{borrow,i} + \text{Gas Cost}_i / T + \text{Risk Premium}_i\}
$$

Where $T$ = expected borrow duration.

### 11.3 Morpho Peer-to-Peer Optimization

Morpho sits on top of Aave/Compound and matches lenders with borrowers directly:

$$
R_{Morpho,supply} = \frac{R_{supply,pool} + R_{borrow,pool}}{2} \quad \text{(P2P matched)}
$$

The matched rate is better for both sides:
- Suppliers earn more than the pool supply rate.
- Borrowers pay less than the pool borrow rate.

### 11.4 Interest Rate Prediction

The trading system predicts future rates based on:

1. **Utilization trends**: Is utilization rising or falling?
2. **Token flow analysis**: Are whales withdrawing? New deposits coming?
3. **Governance proposals**: Upcoming parameter changes?
4. **Market conditions**: Bull markets increase borrow demand.

```python
class RatePredictor:
    """Predicts future lending rates."""

    def predict_rate(self, protocol, asset, horizon_hours) -> RatePrediction:
        # Current state
        current_u = protocol.get_utilization(asset)
        current_rate = protocol.get_borrow_rate(asset)

        # Trend analysis
        u_trend = self.calculate_utilization_trend(protocol, asset, hours=24)

        # Predict utilization
        predicted_u = current_u + u_trend * horizon_hours

        # Clip to valid range
        predicted_u = max(0, min(1, predicted_u))

        # Calculate rate at predicted utilization
        predicted_rate = protocol.calculate_rate_at_utilization(asset, predicted_u)

        return RatePrediction(
            current_rate=current_rate,
            predicted_rate=predicted_rate,
            confidence=self.calculate_confidence(u_trend, horizon_hours),
            direction="up" if predicted_rate > current_rate else "down"
        )
```

---

## 12. Execution Flow — Automated Lending Manager

### 12.1 Complete Lending Management Bot

```python
class AutomatedLendingManager:
    """
    Manages all lending and borrowing positions across protocols.
    Handles:
    - Supply allocation optimization
    - Borrow rate optimization
    - Health factor monitoring
    - Recursive lending management
    - Liquidation protection
    - Rate arbitrage
    """

    def __init__(self, config: LendingConfig):
        self.protocols = config.approved_protocols
        self.hf_monitor = HealthFactorMonitor(config.hf_thresholds)
        self.rate_optimizer = RateOptimizer()
        self.risk_manager = LendingRiskManager(config.risk)
        self.gas_optimizer = GasOptimizer()
        self.positions = LendingPortfolio()

    async def main_loop(self):
        """Main management loop."""
        while True:
            try:
                # ==========================================
                # PHASE 1: HEALTH FACTOR MONITORING (Critical)
                # ==========================================
                hf_alerts = await self.hf_monitor.check_all_positions(self.positions)

                for alert in hf_alerts:
                    if alert.severity == Severity.CRITICAL:
                        await self.handle_critical_hf(alert)
                    elif alert.severity == Severity.WARNING:
                        await self.handle_warning_hf(alert)

                # ==========================================
                # PHASE 2: RATE MONITORING
                # ==========================================
                rate_changes = await self.monitor_rate_changes()

                # Check if any position is now suboptimal
                for position in self.positions.active():
                    current_rate = await position.get_effective_rate()
                    best_available = await self.rate_optimizer.find_best_rate(
                        position.asset, position.type
                    )

                    if position.type == "supply":
                        # Are we earning less than the best available?
                        if best_available > current_rate * 1.15:  # 15% better
                            await self.evaluate_supply_migration(
                                position, best_available
                            )
                    elif position.type == "borrow":
                        # Are we paying more than the best available?
                        if best_available < current_rate * 0.85:  # 15% cheaper
                            await self.evaluate_borrow_migration(
                                position, best_available
                            )

                # ==========================================
                # PHASE 3: UTILIZATION MONITORING
                # ==========================================
                for position in self.positions.supply_positions():
                    utilization = await self.get_pool_utilization(position)

                    if utilization > 0.95:
                        logger.warning(
                            f"High utilization {utilization:.1%} for "
                            f"{position.asset} on {position.protocol}"
                        )
                        # Consider withdrawing before liquidity dries up
                        await self.evaluate_exit_risk(position, utilization)

                # ==========================================
                # PHASE 4: YIELD OPTIMIZATION
                # ==========================================
                available_capital = self.positions.undeployed_capital()
                if available_capital > self.config.min_deploy_amount:
                    best_opportunity = await self.find_best_supply_opportunity(
                        available_capital
                    )
                    if best_opportunity and best_opportunity.net_apy > self.config.min_apy:
                        await self.deploy_capital(best_opportunity, available_capital)

                # ==========================================
                # PHASE 5: RECURSIVE POSITION MANAGEMENT
                # ==========================================
                for position in self.positions.recursive_positions():
                    await self.manage_recursive_position(position)

                # ==========================================
                # PHASE 6: REPORT
                # ==========================================
                await self.generate_report()

                await asyncio.sleep(self.config.check_interval)

            except Exception as e:
                logger.error(f"Lending manager error: {e}")
                await self.alert_system.notify(e)

    async def handle_critical_hf(self, alert: HFAlert):
        """Handle critical health factor event."""
        position = alert.position

        # Strategy 1: Add more collateral
        available_collateral = await self.get_available_collateral(position)
        if available_collateral > 0:
            await position.protocol.supply(
                position.collateral_asset,
                available_collateral
            )
            logger.info(f"Added collateral to {position.id}")
            return

        # Strategy 2: Repay portion of debt
        available_repay = await self.get_available_for_repay(position)
        if available_repay > 0:
            repay_amount = min(available_repay, position.debt * 0.3)
            await position.protocol.repay(position.debt_asset, repay_amount)
            logger.info(f"Repaid {repay_amount} for {position.id}")
            return

        # Strategy 3: Flash loan self-liquidation (last resort)
        logger.warning(f"Flash loan self-liquidation for {position.id}")
        await self.flash_loan_self_liquidate(position)

    async def manage_recursive_position(self, position: RecursivePosition):
        """Manage a recursive lending position."""

        # Check if still profitable
        supply_rate = await position.get_supply_rate()
        borrow_rate = await position.get_borrow_rate()
        incentive_rate = await position.get_incentive_rate()

        net_rate = (supply_rate + incentive_rate) * position.leverage - \
                   borrow_rate * (position.leverage - 1)

        if net_rate < self.config.min_recursive_rate:
            logger.info(f"Recursive position {position.id} no longer profitable "
                       f"(net rate: {net_rate:.2%}). Unwinding.")
            await self.unwind_recursive_position(position)
            return

        # Check health factor
        hf = await self.hf_monitor.calculate_health_factor(position)
        if hf < self.config.recursive_min_hf:
            # Reduce leverage
            target_hf = self.config.recursive_target_hf
            reduction_needed = 1 - (self.config.recursive_min_hf / hf)
            await self.reduce_recursive_leverage(position, reduction_needed)

    async def find_best_supply_opportunity(
        self, capital: float
    ) -> Optional[SupplyOpportunity]:
        """Find the best risk-adjusted supply opportunity."""
        opportunities = []

        for protocol in self.protocols:
            for asset in protocol.get_supported_assets():
                rate = await protocol.get_supply_rate(asset)
                incentive = await protocol.get_supply_incentive(asset)
                utilization = await protocol.get_utilization(asset)
                risk_score = self.risk_manager.assess_protocol(protocol, asset)

                # Risk-adjusted yield
                adjusted_rate = (rate + incentive) * (1 - risk_score)

                # Filter
                if utilization > 0.92:
                    continue  # Too high utilization
                if risk_score > self.config.max_risk_score:
                    continue

                opportunities.append(SupplyOpportunity(
                    protocol=protocol,
                    asset=asset,
                    base_rate=rate,
                    incentive_rate=incentive,
                    total_rate=rate + incentive,
                    risk_adjusted_rate=adjusted_rate,
                    utilization=utilization,
                    risk_score=risk_score
                ))

        if not opportunities:
            return None

        return max(opportunities, key=lambda o: o.risk_adjusted_rate)
```

---

## 13. References

### Protocol Documentation

1. Aave V3 Documentation. https://docs.aave.com/developers/
2. Aave V3 Risk Parameters. https://docs.aave.com/risk/
3. Compound V3 (Comet) Documentation. https://docs.compound.finance/
4. Morpho Documentation. https://docs.morpho.org/
5. Euler Finance Documentation. https://docs.euler.finance/

### Research Papers

6. Gudgeon, L., Perez, D., Harz, D., Livshits, B., Gervais, A. (2020).
   "The Decentralized Financial Crisis." Crypto Valley Conference.

7. Perez, D., Werner, S.M., Xu, J., Livshits, B. (2021). "Liquidations:
   DeFi on a Knife-Edge." Financial Cryptography.

8. Qin, K., Zhou, L., Gamber, Y., Gervais, A. (2021). "Attacking the DeFi
   Ecosystem with Flash Loans for Fun and Profit." Financial Cryptography.

9. Bartoletti, M., Chiang, J.H., Lluch-Lafuente, A. (2021). "SoK: Lending
   Pools in Decentralized Finance." Financial Cryptography Workshops.

### Risk Analysis

10. Gauntlet Network — Protocol Risk Management. https://gauntlet.network/
11. Chaos Labs — Risk Monitoring. https://chaoslabs.xyz/
12. Aave Risk Dashboard. https://governance.aave.com/

### Interest Rate Models

13. Aave Interest Rate Model. https://docs.aave.com/risk/liquidity-risk/borrow-interest-rate
14. Compound Interest Rate Model. https://compound.finance/docs#protocol-math

---

> **Next Document**: [06_liquid_staking_restaking.md](./06_liquid_staking_restaking.md)
> — Liquid staking mechanics, restaking, and yield stacking strategies.
