# Flash Loans & DeFi Composability

> **Axis 2 — Financial Products | Module 02 — DeFi Mechanics | Document 04**
> Version: 2.0.0 | Last Updated: 2026-04-12
> Classification: KNOWLEDGE BASE — MULTI-AGENT AI TRADING SYSTEM

---

## Table of Contents

1. [Introduction to Flash Loans](#1-introduction-to-flash-loans)
2. [Flash Loan Mechanics](#2-flash-loan-mechanics)
3. [Aave Flash Loan Implementation](#3-aave-flash-loan-implementation)
4. [Use Case 1: Arbitrage](#4-use-case-1-arbitrage)
5. [Use Case 2: Collateral Swap](#5-use-case-2-collateral-swap)
6. [Use Case 3: Self-Liquidation](#6-use-case-3-self-liquidation)
7. [Use Case 4: Leverage and Deleverage](#7-use-case-4-leverage-and-deleverage)
8. [Flash Loan Attack Vectors](#8-flash-loan-attack-vectors)
9. [Flash Mint](#9-flash-mint)
10. [DeFi Composability Patterns](#10-defi-composability-patterns)
11. [Gas Estimation and Optimization](#11-gas-estimation-and-optimization)
12. [Smart Contract Pseudocode](#12-smart-contract-pseudocode)
13. [Mathematical Models for Profitability](#13-mathematical-models-for-profitability)
14. [Risk Parameters](#14-risk-parameters)
15. [Execution Flow — Flash Loan Bot](#15-execution-flow--flash-loan-bot)
16. [References](#16-references)

---

## 1. Introduction to Flash Loans

### 1.1 Definition

A flash loan is an uncollateralized loan that must be borrowed and repaid within a
single blockchain transaction. If the borrower cannot repay the loan plus fee by the
end of the transaction, the entire transaction reverts — as if it never happened.

### 1.2 Why Flash Loans Are Possible

Flash loans exploit the atomic nature of blockchain transactions:

```
Transaction Execution (atomic):
├── Step 1: Borrow 1,000,000 USDC (no collateral)
├── Step 2: Use 1,000,000 USDC in some profitable operation
├── Step 3: End up with 1,001,000 USDC (profit from operation)
├── Step 4: Repay 1,000,900 USDC (principal + 0.09% fee)
├── Step 5: Keep 100 USDC profit
└── IF Step 4 fails → ENTIRE TRANSACTION REVERTS (Steps 1-5 never happened)
```

**Key insight**: From the protocol's perspective, the loan is risk-free. Either the
borrower repays within the same transaction, or nothing happened. There is no state
between "borrowed" and "repaid" that persists across blocks.

### 1.3 Flash Loan Providers

| Provider        | Fee      | Max Amount       | Token Support            |
|-----------------|----------|------------------|--------------------------|
| Aave V3         | 0.05%*   | Pool liquidity   | All Aave-listed tokens   |
| Aave V2         | 0.09%    | Pool liquidity   | All Aave-listed tokens   |
| dYdX            | 0%       | Pool liquidity   | ETH, USDC, DAI           |
| Uniswap V2/V3   | 0.3%**  | Pool reserves    | Any pool token           |
| Balancer         | 0%***   | Vault balance    | All Balancer vault tokens|
| Maker (flash mint)| 0%    | Unlimited DAI    | DAI only                 |

*Aave V3 fee for flash loans used within Aave ecosystem is 0%, otherwise 0.05%.
**Uniswap "flash swaps" require returning either tokens or equivalent value.
***Balancer flash loans have zero fee (funded by protocol governance).

### 1.4 Significance for Algorithmic Trading

Flash loans enable the trading system to:
- Execute capital-efficient arbitrage without requiring large capital reserves.
- Restructure lending positions in a single transaction.
- Perform liquidations without holding the repayment capital.
- Test strategy profitability risk-free (if unprofitable, tx reverts).

---

## 2. Flash Loan Mechanics

### 2.1 Transaction Flow

```
Block N:
┌─────────────────────────────────────────────────────────┐
│ Transaction (single atomic execution)                    │
│                                                         │
│  1. flashLoan(amount) called                            │
│     └── Protocol transfers 'amount' to borrower         │
│                                                         │
│  2. executeOperation() callback triggered               │
│     └── Borrower's contract executes arbitrary logic    │
│         ├── Swap on DEX A                               │
│         ├── Deposit in Protocol B                       │
│         ├── Borrow from Protocol C                      │
│         └── (any sequence of operations)                │
│                                                         │
│  3. Repayment check                                     │
│     └── Protocol verifies: balance >= amount + fee      │
│         ├── IF true: Transaction succeeds               │
│         └── IF false: Transaction REVERTS               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Atomicity Guarantee

The atomicity guarantee means:

$$
\text{Outcome} = \begin{cases}
\text{Success: All state changes persist} & \text{if repayment condition met} \\
\text{Revert: No state changes persist} & \text{if repayment condition NOT met}
\end{cases}
$$

The only cost of a failed flash loan attempt is the gas fee for the reverted transaction.

### 2.3 Flash Loan vs Traditional Loan

| Feature              | Flash Loan               | Traditional Loan        |
|---------------------|--------------------------|-------------------------|
| Collateral required  | None                     | 100-150% overcollateral |
| Duration            | Single transaction (~15s) | Days to years           |
| Interest/Fee        | 0-0.09% flat             | APR-based (2-20%)       |
| Default risk        | Zero (atomic)            | Non-zero (liquidation)  |
| Max amount          | Protocol liquidity       | Based on collateral     |
| Use cases           | Arb, restructure, liquidate | General borrowing    |
| Access              | Anyone (permissionless)  | Credit check / collateral|

---

## 3. Aave Flash Loan Implementation

### 3.1 Aave V3 Flash Loan Interface

```solidity
// IPool.sol - Aave V3 Flash Loan Interface
interface IPool {
    /**
     * @notice Execute a flash loan
     * @param receiverAddress Contract that will receive and return the funds
     * @param assets Array of token addresses to borrow
     * @param amounts Array of amounts to borrow
     * @param interestRateModes Array of interest rate modes (0 = no debt, 1 = stable, 2 = variable)
     * @param onBehalfOf Address that will receive the debt (if mode != 0)
     * @param params Arbitrary data passed to executeOperation callback
     * @param referralCode Referral code for tracking
     */
    function flashLoan(
        address receiverAddress,
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata interestRateModes,
        address onBehalfOf,
        bytes calldata params,
        uint16 referralCode
    ) external;
}
```

### 3.2 Flash Loan Receiver Contract

```solidity
// FlashLoanReceiver.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {IFlashLoanSimpleReceiver} from "@aave/v3-core/contracts/flashloan-simple/IFlashLoanSimpleReceiver.sol";
import {IPoolAddressesProvider} from "@aave/v3-core/contracts/interfaces/IPoolAddressesProvider.sol";
import {IPool} from "@aave/v3-core/contracts/interfaces/IPool.sol";

contract FlashLoanArbitrage is IFlashLoanSimpleReceiver {
    IPoolAddressesProvider public immutable ADDRESSES_PROVIDER;
    IPool public immutable POOL;

    constructor(IPoolAddressesProvider provider) {
        ADDRESSES_PROVIDER = provider;
        POOL = IPool(provider.getPool());
    }

    /**
     * @notice Called by Aave Pool after flash loan funds are transferred
     * @param asset The token borrowed
     * @param amount The amount borrowed
     * @param premium The fee to repay (amount * 0.05%)
     * @param initiator Who initiated the flash loan
     * @param params Custom parameters
     */
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        // Ensure caller is the Aave Pool
        require(msg.sender == address(POOL), "Caller must be pool");
        require(initiator == address(this), "Initiator must be this contract");

        // ========================================
        // CUSTOM LOGIC HERE
        // Execute arbitrage, collateral swap, etc.
        // ========================================

        // Decode custom parameters
        (address dexA, address dexB, uint256 minProfit) = abi.decode(
            params, (address, address, uint256)
        );

        // Example: Buy cheap on DEX A, sell expensive on DEX B
        uint256 received = _swapOnDex(dexA, asset, amount);
        uint256 finalAmount = _swapOnDex(dexB, received);

        // Verify profitability
        uint256 totalDebt = amount + premium;
        require(finalAmount >= totalDebt + minProfit, "Not profitable");

        // ========================================
        // REPAYMENT
        // Approve the Pool to pull the repayment
        // ========================================
        IERC20(asset).approve(address(POOL), totalDebt);

        return true;  // Signals successful execution
    }

    /**
     * @notice Initiate flash loan
     */
    function executeFlashLoan(
        address asset,
        uint256 amount,
        bytes calldata params
    ) external {
        POOL.flashLoanSimple(
            address(this),  // receiver
            asset,          // token to borrow
            amount,         // amount to borrow
            params,         // custom data
            0               // referral code
        );
    }
}
```

### 3.3 Multi-Asset Flash Loan

Aave V3 supports borrowing multiple assets in a single flash loan:

```solidity
function executeMultiAssetFlashLoan() external {
    address[] memory assets = new address[](2);
    assets[0] = USDC;
    assets[1] = WETH;

    uint256[] memory amounts = new uint256[](2);
    amounts[0] = 1_000_000e6;   // 1M USDC
    amounts[1] = 500e18;         // 500 WETH

    uint256[] memory modes = new uint256[](2);
    modes[0] = 0;  // Must repay USDC
    modes[1] = 0;  // Must repay WETH

    POOL.flashLoan(
        address(this),
        assets,
        amounts,
        modes,
        address(this),
        abi.encode(/* custom params */),
        0
    );
}
```

---

## 4. Use Case 1: Arbitrage

### 4.1 DEX-DEX Arbitrage with Flash Loans

The most common flash loan use case — exploit price discrepancies between DEXes:

```
Flash Loan Flow (Arbitrage):
1. Borrow 1,000,000 USDC from Aave
2. Buy ETH on Uniswap at $2,950 (338.98 ETH)
3. Sell ETH on SushiSwap at $2,960 (1,003,389 USDC)
4. Repay 1,000,500 USDC (principal + 0.05% fee)
5. Profit: 2,889 USDC
```

### 4.2 Profitability Calculation

$$
\text{Profit} = \text{Amount} \cdot \left(\frac{P_{sell}}{P_{buy}} - 1\right) - \text{Fee}_{flash} - \text{Gas Cost}
$$

Where:
- $P_{sell}$ = price on the selling DEX
- $P_{buy}$ = price on the buying DEX
- $\text{Fee}_{flash}$ = flash loan fee (e.g., 0.05% of amount)

More precisely, including swap fees and price impact:

$$
\text{Profit} = A \cdot \left(\frac{P_B \cdot (1-f_B)}{P_A \cdot (1+f_A)} \cdot (1-\text{Impact}_A) \cdot (1-\text{Impact}_B) - 1\right) - A \cdot f_{flash} - G
$$

Where:
- $A$ = flash loan amount
- $P_A$, $P_B$ = prices on DEX A (buy) and DEX B (sell)
- $f_A$, $f_B$ = swap fees on each DEX
- $\text{Impact}_{A,B}$ = price impact on each DEX
- $f_{flash}$ = flash loan fee rate
- $G$ = gas cost in USD

### 4.3 Optimal Flash Loan Amount

The optimal amount maximizes profit. Price impact is the limiting factor:

For a constant product AMM, price impact grows with trade size:

$$
\text{Impact}(A) = \frac{A}{R + A}
$$

Where $R$ = relevant reserve. The profit function becomes concave and has an
optimal maximum.

$$
\frac{d\text{Profit}}{dA} = 0
$$

Solving (for simple case with one AMM buy and one AMM sell):

$$
A^* = \sqrt{R_A \cdot R_B \cdot \frac{P_B(1-f_B)}{P_A(1+f_A)}} - R_A
$$

### 4.4 Multi-Hop Arbitrage

When direct arbitrage is not available, multi-hop paths can be profitable:

```
Flash Loan: 1M USDC
├── Swap USDC -> WETH on Uniswap V3 (0.05% pool)
├── Swap WETH -> WBTC on Curve (tricrypto)
├── Swap WBTC -> USDC on SushiSwap
└── Repay 1M + fee, keep difference
```

Finding optimal paths requires graph search algorithms:

$$
\text{Maximize: } \prod_{i=1}^{n} (1 - f_i)(1 - \text{impact}_i) \cdot \frac{P_{out,i}}{P_{in,i}} - 1 - f_{flash}
$$

### 4.5 Triangular Arbitrage

A special case of multi-hop that exploits pricing inconsistencies:

```
USDC -> ETH -> BTC -> USDC

If: (USDC/ETH price) * (ETH/BTC price) * (BTC/USDC price) != 1
Then: Triangular arbitrage opportunity exists
```

$$
\text{Opportunity} = P_{A/B} \cdot P_{B/C} \cdot P_{C/A} - 1
$$

If this product > total fees, arbitrage is profitable.

---

## 5. Use Case 2: Collateral Swap

### 5.1 Problem

A user has a lending position:
- Collateral: 100 ETH (at $3000 = $300K)
- Debt: 200,000 USDC
- They want to switch collateral from ETH to WBTC

**Without flash loan**: Must first repay debt, withdraw ETH, swap to WBTC, deposit
WBTC, re-borrow. Multiple transactions, risk of liquidation during transition.

**With flash loan**: Single atomic transaction, zero liquidation risk.

### 5.2 Collateral Swap Flow

```
Step 1: Flash loan 200,000 USDC
Step 2: Repay 200,000 USDC debt on Aave
Step 3: Withdraw 100 ETH collateral (now free)
Step 4: Swap 100 ETH -> 4.5 WBTC on Uniswap
Step 5: Deposit 4.5 WBTC as collateral on Aave
Step 6: Borrow 200,000 USDC against WBTC
Step 7: Repay flash loan (200,000 + 100 USDC fee)
Step 8: Result: Position now collateralized by WBTC instead of ETH
```

### 5.3 Collateral Swap Contract

```solidity
contract CollateralSwap is IFlashLoanSimpleReceiver {

    function executeOperation(
        address asset,      // USDC
        uint256 amount,     // 200,000 USDC
        uint256 premium,    // Flash loan fee
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        (address oldCollateral, address newCollateral, uint256 debtAmount) =
            abi.decode(params, (address, address, uint256));

        // Step 1: Repay user's debt
        IERC20(asset).approve(address(POOL), debtAmount);
        POOL.repay(asset, debtAmount, 2, msg.sender);  // 2 = variable rate

        // Step 2: Withdraw old collateral
        uint256 withdrawnAmount = POOL.withdraw(
            oldCollateral, type(uint256).max, address(this)
        );

        // Step 3: Swap old -> new collateral
        uint256 newAmount = _swap(oldCollateral, newCollateral, withdrawnAmount);

        // Step 4: Deposit new collateral
        IERC20(newCollateral).approve(address(POOL), newAmount);
        POOL.supply(newCollateral, newAmount, msg.sender, 0);

        // Step 5: Borrow to repay flash loan
        POOL.borrow(asset, amount + premium, 2, 0, msg.sender);

        // Step 6: Approve repayment
        IERC20(asset).approve(address(POOL), amount + premium);

        return true;
    }
}
```

---

## 6. Use Case 3: Self-Liquidation

### 6.1 Problem

A user's position is approaching liquidation:
- Collateral: 100 ETH ($300K)
- Debt: 250,000 USDC
- Health Factor: 1.05 (dangerously close to 1.0)
- If liquidated by external liquidator: 5-10% penalty

**Self-liquidation via flash loan**: Close the position without penalty.

### 6.2 Self-Liquidation Flow

```
Step 1: Flash loan 250,000 USDC
Step 2: Repay ALL debt (250,000 USDC)
Step 3: Withdraw ALL collateral (100 ETH)
Step 4: Swap enough ETH to USDC to repay flash loan
        (Swap ~83.5 ETH -> 250,125 USDC at market price)
Step 5: Repay flash loan (250,000 + 125 USDC fee)
Step 6: Keep remaining ~16.5 ETH (~$49,500)
```

**Savings vs external liquidation**:
- External liquidation penalty: ~$15,000-$30,000
- Flash loan self-liquidation cost: ~$125 (fee) + gas
- Net saving: $15,000-$30,000

### 6.3 When to Self-Liquidate

$$
\text{Self-liquidate when: } \text{Penalty}_{external} > \text{Cost}_{flash\_loan} + \text{Slippage}_{swap}
$$

Since external liquidation penalties are typically 5-15% and flash loan costs are
<0.1%, self-liquidation is almost always preferable when a position must be closed.

---

## 7. Use Case 4: Leverage and Deleverage

### 7.1 Instant Leverage via Flash Loan

Instead of looping through deposit-borrow-deposit cycles:

```
Target: Create a 3x leveraged long ETH position

WITHOUT flash loan (multiple transactions):
  Tx 1: Deposit 10 ETH, borrow 20,000 USDC
  Tx 2: Buy 6.67 ETH, deposit, borrow 13,333 USDC
  Tx 3: Buy 4.44 ETH, deposit, borrow 8,889 USDC
  ... (many iterations to approach 3x)

WITH flash loan (single transaction):
  Step 1: Flash loan 20 ETH
  Step 2: Deposit 30 ETH total (10 own + 20 borrowed)
  Step 3: Borrow 60,000 USDC against 30 ETH
  Step 4: Buy 20 ETH with 60,000 USDC
  Step 5: Repay 20 ETH flash loan
  Result: 30 ETH collateral, 60,000 USDC debt = 3x exposure
```

### 7.2 Leverage Mathematics

For leverage multiple $m$ with initial capital $V_0$:

$$
\text{Collateral} = V_0 \cdot m
$$

$$
\text{Debt} = V_0 \cdot (m - 1) \cdot P_{asset}
$$

$$
\text{Health Factor} = \frac{\text{Collateral} \cdot P_{asset} \cdot LTV_{liquidation}}{\text{Debt}}
$$

For a 3x leveraged ETH position at $3000:
- Collateral: 30 ETH
- Debt: 60,000 USDC
- HF: $(30 \times 3000 \times 0.825) / 60000 = 1.2375$

### 7.3 Deleverage (Instant Unwind)

```
Starting: 30 ETH collateral, 60,000 USDC debt

Step 1: Flash loan 60,000 USDC
Step 2: Repay 60,000 USDC debt
Step 3: Withdraw 30 ETH (all collateral)
Step 4: Sell 20 ETH -> 60,030 USDC (market price)
Step 5: Repay flash loan (60,000 + 30 USDC fee)
Step 6: Keep 10 ETH (original capital + any profit)
```

### 7.4 Flash Loan Leverage Bot

```python
class FlashLoanLeverageBot:
    """
    Manages leveraged positions using flash loans for
    instant leverage and deleverage.
    """

    async def create_leverage_position(
        self,
        asset: str,
        amount: float,
        target_leverage: float,
        lending_protocol: str = "aave"
    ) -> LeveragedPosition:
        """Create leveraged position in single transaction."""

        # Calculate required flash loan amount
        flash_amount = amount * (target_leverage - 1)

        # Simulate to verify profitability and health factor
        simulation = await self.simulate_leverage(
            asset, amount, flash_amount, lending_protocol
        )

        if simulation.health_factor < 1.3:
            raise RiskError(f"Health factor too low: {simulation.health_factor}")

        # Build transaction
        params = encode_params(asset, amount, flash_amount, target_leverage)

        # Execute flash loan
        tx = await self.flash_loan_contract.execute_flash_loan(
            asset=self.get_borrow_asset(lending_protocol),
            amount=flash_amount,
            params=params
        )

        receipt = await self.web3.wait_for_receipt(tx)
        return self.parse_position(receipt)

    async def deleverage_position(
        self,
        position: LeveragedPosition,
        target_leverage: float = 1.0
    ):
        """Reduce leverage or fully close position."""

        # Calculate debt to repay
        current_debt = await position.get_debt()
        target_debt = position.collateral_value * (target_leverage - 1) / target_leverage

        repay_amount = current_debt - target_debt

        if repay_amount <= 0:
            return  # Already at or below target leverage

        # Flash loan the repayment amount
        tx = await self.flash_loan_contract.execute_deleverage(
            position=position,
            repay_amount=repay_amount
        )

        return await self.web3.wait_for_receipt(tx)
```

---

## 8. Flash Loan Attack Vectors

### 8.1 Purpose of This Section

Understanding flash loan attack vectors is essential for the trading system to:
1. **Defend** our own positions against flash loan attacks.
2. **Identify** vulnerable protocols to avoid.
3. **Detect** attacks in progress for early warning.

### 8.2 Attack Type 1: Oracle Manipulation

```
Attack Flow:
1. Flash loan large amount of token A
2. Dump token A on a DEX (crashing the price on that DEX)
3. A lending protocol uses that DEX price as oracle
4. Protocol thinks collateral (token A) is now worthless
5. Attacker's position on that protocol is now "overcollateralized"
   (because they borrowed token A at the old price)
6. Attacker borrows more / liquidates others at manipulated price
7. Repay flash loan
8. Profit from mispriced borrows/liquidations
```

**Defense for trading system**:
- Only use protocols with TWAP oracles (not spot price)
- Verify oracle freshness and deviation checks
- Monitor for sudden large swaps on oracle-source pools

### 8.3 Attack Type 2: Governance Manipulation

```
Attack Flow:
1. Flash loan governance tokens of a DAO
2. Submit + vote on malicious governance proposal
   (if instant governance / no timelock)
3. Proposal passes (attacker has majority)
4. Drain treasury / change protocol parameters
5. Return governance tokens
6. Repay flash loan
```

**Defense**:
- Only interact with protocols that have timelocks (48hr+)
- Monitor governance proposals for malicious activity
- Avoid protocols with low governance token market cap

### 8.4 Attack Type 3: Reentrancy + Flash Loan

```
Attack Flow:
1. Flash loan tokens
2. Deposit into vulnerable protocol
3. Exploit reentrancy during withdrawal
4. Extract more than deposited
5. Repay flash loan with extracted funds
6. Profit from reentrancy exploit
```

### 8.5 Attack Type 4: Price Manipulation + Liquidation

```
Attack Flow:
1. Flash loan large amount
2. Manipulate price on a DEX (used as oracle)
3. Trigger liquidations on a lending protocol that references that oracle
4. Buy liquidated collateral at discount
5. Let price recover (remove manipulation)
6. Sell collateral at fair price
7. Repay flash loan
```

### 8.6 Defense Checklist for Trading System

```
PROTOCOL SAFETY CHECKS (against flash loan attacks):

[x] Oracle uses TWAP (not spot) or Chainlink (off-chain)
[x] Governance has minimum 48-hour timelock
[x] No flash-loan-borrow-then-vote possible
[x] Collateral factors have safety margins
[x] Protocol has circuit breakers for rapid price changes
[x] Liquidation process resistant to single-block manipulation
[x] Contracts audited specifically for flash loan vectors
[x] Price deviation checks before state changes
```

---

## 9. Flash Mint

### 9.1 Concept

Flash mint allows the creation (minting) of tokens from thin air within a single
transaction, as long as they are burned (destroyed) by the end.

**Most notable**: MakerDAO's DAI flash mint — allows minting unlimited DAI in a
single transaction, as long as it is all returned.

### 9.2 DAI Flash Mint

```solidity
// MakerDAO Flash Mint
// Can mint any amount of DAI (no upper limit beyond max uint256)
// Fee: 0% (governance-set, currently zero)

interface IDssFlash {
    function flashLoan(
        IERC3156FlashBorrower receiver,
        address token,         // Must be DAI
        uint256 amount,        // Any amount
        bytes calldata data
    ) external returns (bool);
}
```

### 9.3 Advantages of Flash Mint vs Flash Loan

| Feature          | Flash Loan              | Flash Mint              |
|------------------|-------------------------|-------------------------|
| Amount limit     | Pool liquidity          | Unlimited (max uint256) |
| Fee              | 0.05-0.09%             | 0% (DAI)               |
| Available tokens | Protocol-listed         | Only mintable tokens    |
| Backing          | Real deposits           | Temporary (destroyed)   |

### 9.4 Flash Mint Use Cases

1. **Unlimited arbitrage capital**: No cap on borrowed amount.
2. **Stress testing**: Test protocol behavior with extreme amounts.
3. **DAI-centric strategies**: Any strategy requiring large DAI amounts.

---

## 10. DeFi Composability Patterns

### 10.1 Pattern 1: Lending + DEX + Yield

```
Strategy: Leverage yield farming via composability

Flash Loan: 100,000 USDC
├── Deposit USDC in Aave (receive aUSDC)
├── Borrow ETH from Aave against aUSDC
├── Swap half ETH for USDC on Uniswap
├── Provide ETH/USDC liquidity on Uniswap V3
├── Stake LP position in reward farm
└── [Position maintained across blocks — NOT repaid in same tx]

Wait... this doesn't work as a flash loan.
Flash loans must be repaid same tx.

CORRECT composability (non-flash-loan):
Tx 1: Deposit USDC -> Borrow ETH -> LP -> Farm
Tx 2 (flash loan for leverage): Flash loan more USDC -> deposit -> borrow more -> LP
```

### 10.2 Pattern 2: Multi-Hop Flash Loan Arbitrage

```
Flash Loan: 1M USDC from Aave
├── Swap USDC -> WETH on Uniswap V3 (0.05% pool, tight range = low impact)
├── Swap WETH -> stETH on Curve (0.04% fee, minimal slippage)
├── Swap stETH -> USDC on Balancer (weighted pool)
├── Net: Started with 1M USDC, end with 1.002M USDC
└── Repay 1,000,500 USDC (1M + 0.05% fee)
    Profit: 1,500 USDC
```

### 10.3 Pattern 3: Cross-Protocol Liquidation

```
Flash Loan: 500,000 USDC from Balancer (0% fee)
├── Liquidate undercollateralized position on Aave
│   ├── Repay 500,000 USDC of borrower's debt
│   └── Receive 166.67 ETH (at 5% liquidation bonus)
├── Swap 166.67 ETH -> 503,340 USDC on Uniswap
└── Repay 500,000 USDC to Balancer (0% fee)
    Profit: 3,340 USDC
```

### 10.4 Pattern 4: Yield Token Arbitrage (Pendle)

```
Flash Loan: 100 stETH from Aave
├── Split stETH into PT-stETH + YT-stETH on Pendle
│   (Principal Token + Yield Token)
├── If PT + YT market price > stETH:
│   └── Sell PT and YT separately on Pendle AMM
│       Combined value: 101.5 stETH equivalent
├── Buy back 100 stETH on Curve
└── Repay 100.05 stETH (flash loan + fee)
    Profit: 1.45 stETH
```

### 10.5 Pattern 5: Collateral Optimization Loop

```
Goal: Maximize yield on idle collateral

Flash Loan: 1M USDC from Aave
├── Deposit 1M USDC in Compound (earn supply APY)
├── Borrow 800K DAI from Compound (80% LTV)
├── Deposit 800K DAI in Aave (earn supply APY)
├── Borrow 640K USDC from Aave (80% LTV)
├── Deposit 640K USDC in Compound (earn supply APY)
├── ... (continue loop until marginal benefit < gas)
├── Final: Earn supply APY on full leveraged amount
│   Pay borrow APY on borrowed amounts
└── If Supply APY > Borrow APY: NET POSITIVE YIELD

Note: This is set up as a series of transactions, not repaid in same tx.
The flash loan is used only for the INITIAL deployment to skip the iterative loop.
```

### 10.6 Composability Risk: Protocol Dependencies

```
Dependency Graph:

Yield Strategy A
├── Depends on: Protocol X (lending)
├── Depends on: Protocol Y (DEX)
├── Depends on: Oracle Z
└── Depends on: Stablecoin S

If any dependency fails:
- Protocol X exploit → collateral at risk
- Protocol Y liquidity drain → cannot swap
- Oracle Z manipulation → incorrect liquidation
- Stablecoin S depeg → collateral value drops

RISK FORMULA:
P(strategy_failure) = 1 - ∏(1 - P(dependency_i_failure))
```

---

## 11. Gas Estimation and Optimization

### 11.1 Flash Loan Transaction Gas Costs

| Operation                          | Gas Estimate    | Notes                   |
|------------------------------------|----------------|--------------------------|
| Aave flash loan overhead           | ~80,000        | Fixed overhead           |
| Single swap (Uniswap V3)          | ~120,000-180,000| Depends on tick crossings |
| Single swap (Curve)               | ~150,000-300,000| Depends on pool complexity|
| Aave deposit                       | ~120,000       |                          |
| Aave borrow                        | ~180,000       |                          |
| Aave repay                         | ~150,000       |                          |
| ERC-20 approve                     | ~50,000        | If not already approved  |
| Total (simple arb, 2 swaps)       | ~500,000       |                          |
| Total (collateral swap)           | ~800,000       |                          |
| Total (leverage loop, 5 steps)    | ~1,200,000     |                          |
| Total (complex multi-hop)         | ~1,500,000     |                          |

### 11.2 Gas Optimization Techniques

#### 11.2.1 Pre-Approve Tokens

```solidity
// Approve max amount once, save 50K gas per future transaction
IERC20(token).approve(spender, type(uint256).max);
```

#### 11.2.2 Use Balancer for Zero-Fee Flash Loans

When possible, prefer Balancer (0% fee) over Aave (0.05% fee):

$$
\text{Savings} = \text{Amount} \times 0.0005 - \text{Extra Gas} \times \text{Gas Price}
$$

For amounts > ~$100K, Balancer saves significant money.

#### 11.2.3 Minimize Storage Operations

Each `SSTORE` (storage write) costs 20,000-5,000 gas. Minimize state changes:

```solidity
// BAD: Multiple storage writes
storage.value1 = x;
storage.value2 = y;
storage.value3 = z;

// BETTER: Compute in memory, write once if possible
// Or batch state changes to minimize cold/warm storage operations
```

#### 11.2.4 Assembly Optimization for Hot Paths

For frequently executed flash loan contracts, use Yul/assembly:

```solidity
// Optimized swap call using low-level assembly
assembly {
    // Load function selector for swap()
    mstore(0x00, 0x022c0d9f) // swap selector
    mstore(0x04, amount0Out)
    mstore(0x24, amount1Out)
    mstore(0x44, to)
    mstore(0x64, 0x80)

    let success := call(gas(), pair, 0, 0x00, 0xa4, 0, 0)
    if iszero(success) { revert(0, 0) }
}
```

### 11.3 Profitability Threshold

Minimum profit for a flash loan operation:

$$
\text{Min Profit} = \text{Gas} \times \text{Gas Price (gwei)} \times 10^{-9} \times P_{ETH} + \text{Flash Fee} + \text{Safety Margin}
$$

**Example** at 30 gwei, ETH = $3000, 500K gas:

$$
\text{Min Profit} = 500000 \times 30 \times 10^{-9} \times 3000 + \text{Flash Fee} = \$45 + \text{Flash Fee}
$$

For a $1M flash loan at 0.05%: Flash Fee = $500.

Total minimum profit: $545. Add 50% safety margin: **$818 minimum profit target.**

---

## 12. Smart Contract Pseudocode

### 12.1 Generic Flash Loan Executor

```solidity
// GenericFlashLoanExecutor.sol
// Flexible framework for executing various flash loan strategies

contract FlashLoanExecutor is IFlashLoanSimpleReceiver {

    // Strategy registry
    mapping(bytes4 => address) public strategies;

    struct FlashLoanParams {
        bytes4 strategyId;      // Which strategy to execute
        bytes strategyData;     // Strategy-specific parameters
        uint256 minProfit;      // Minimum profit threshold
        address profitToken;    // Token to measure profit in
    }

    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        require(msg.sender == address(POOL));

        // Decode parameters
        FlashLoanParams memory flashParams = abi.decode(params, (FlashLoanParams));

        // Record starting balance
        uint256 startBalance = IERC20(flashParams.profitToken).balanceOf(address(this));

        // Execute strategy via delegatecall
        address strategy = strategies[flashParams.strategyId];
        (bool success,) = strategy.delegatecall(
            abi.encodeWithSignature("execute(bytes)", flashParams.strategyData)
        );
        require(success, "Strategy execution failed");

        // Verify profit
        uint256 endBalance = IERC20(flashParams.profitToken).balanceOf(address(this));
        uint256 totalOwed = amount + premium;

        if (flashParams.profitToken == asset) {
            require(
                endBalance >= startBalance + totalOwed + flashParams.minProfit,
                "Insufficient profit"
            );
        }

        // Approve repayment
        IERC20(asset).approve(address(POOL), totalOwed);
        return true;
    }
}
```

### 12.2 Arbitrage Strategy Module

```solidity
// ArbitrageStrategy.sol

contract ArbitrageStrategy {

    struct ArbParams {
        address tokenIn;
        address tokenOut;
        uint256 amountIn;
        address dexBuy;       // DEX to buy on (cheaper)
        bytes buyCalldata;    // Encoded swap call
        address dexSell;      // DEX to sell on (more expensive)
        bytes sellCalldata;   // Encoded swap call
    }

    function execute(bytes calldata data) external {
        ArbParams memory params = abi.decode(data, (ArbParams));

        // Step 1: Buy cheap
        IERC20(params.tokenIn).approve(params.dexBuy, params.amountIn);
        (bool success,) = params.dexBuy.call(params.buyCalldata);
        require(success, "Buy swap failed");

        // Step 2: Sell expensive
        uint256 tokenOutBalance = IERC20(params.tokenOut).balanceOf(address(this));
        IERC20(params.tokenOut).approve(params.dexSell, tokenOutBalance);
        (success,) = params.dexSell.call(params.sellCalldata);
        require(success, "Sell swap failed");

        // Profit remains in contract (verified by executor)
    }
}
```

### 12.3 Liquidation Strategy Module

```solidity
// LiquidationStrategy.sol

contract LiquidationStrategy {

    struct LiquidationParams {
        address lendingPool;
        address collateralAsset;
        address debtAsset;
        address user;             // User to liquidate
        uint256 debtToCover;
        bool receiveAToken;       // Receive aToken or underlying
        address sellDex;          // DEX to sell received collateral
        bytes sellCalldata;
    }

    function execute(bytes calldata data) external {
        LiquidationParams memory params = abi.decode(data, (LiquidationParams));

        // Step 1: Approve debt token for liquidation
        IERC20(params.debtAsset).approve(params.lendingPool, params.debtToCover);

        // Step 2: Execute liquidation
        IPool(params.lendingPool).liquidationCall(
            params.collateralAsset,
            params.debtAsset,
            params.user,
            params.debtToCover,
            params.receiveAToken
        );

        // Step 3: Sell received collateral back to debt token
        uint256 collateralReceived = IERC20(params.collateralAsset)
            .balanceOf(address(this));
        IERC20(params.collateralAsset).approve(params.sellDex, collateralReceived);
        (bool success,) = params.sellDex.call(params.sellCalldata);
        require(success, "Collateral sell failed");

        // Profit = collateral value (with bonus) - debt covered
    }
}
```

---

## 13. Mathematical Models for Profitability

### 13.1 Arbitrage Profit Model

For a two-venue arbitrage:

$$
\Pi = A \cdot \left[\frac{R_B}{R_B + A \cdot (1-f_B)} \cdot \frac{R_A + A \cdot (1-f_A)}{R_A} \cdot (1-f_A)(1-f_B) - 1\right] - A \cdot f_{flash} - G
$$

Where:
- $A$ = trade amount
- $R_A$, $R_B$ = reserves on DEX A (buy) and DEX B (sell)
- $f_A$, $f_B$ = swap fees
- $f_{flash}$ = flash loan fee
- $G$ = gas cost

### 13.2 Optimal Arbitrage Size

Maximizing $\Pi$ with respect to $A$:

$$
\frac{d\Pi}{dA} = 0
$$

For constant product AMMs, this yields:

$$
A^* = \frac{\sqrt{R_A \cdot R_B \cdot P_B/P_A \cdot (1-f_A)(1-f_B)} - R_A}{(1-f_A)}
$$

Where $P_A$, $P_B$ are the current prices on each DEX.

### 13.3 Liquidation Profit Model

$$
\Pi_{liq} = D \cdot \frac{\text{Bonus}}{1 + \text{Bonus}} \cdot (1 - f_{swap}) - D \cdot f_{flash} - G
$$

Where:
- $D$ = debt amount being liquidated
- Bonus = liquidation bonus (e.g., 5% = 0.05)
- $f_{swap}$ = DEX swap fee for selling collateral
- $f_{flash}$ = flash loan fee
- $G$ = gas cost

**Example**: Liquidating $100K debt with 5% bonus:

$$
\Pi = 100000 \cdot \frac{0.05}{1.05} \cdot (1-0.003) - 100000 \cdot 0.0005 - 50 = \$4,698 - \$50 - \$50 = \$4,598
$$

### 13.4 Collateral Swap Cost Model

$$
\text{Cost}_{swap} = V_{collateral} \cdot f_{swap} + V_{debt} \cdot f_{flash} + G
$$

**Savings vs manual process**:

$$
\text{Savings} = \text{Liquidation Risk Value} - \text{Cost}_{swap}
$$

Where Liquidation Risk Value = potential loss if liquidated during manual multi-tx swap.

### 13.5 Expected Value of Flash Loan Attempt

Since failed flash loans only cost gas:

$$
EV = P_{success} \cdot \Pi_{success} - P_{failure} \cdot G_{failure}
$$

Where:
- $P_{success}$ = probability the arbitrage is still profitable when tx executes
- $\Pi_{success}$ = profit if successful
- $P_{failure}$ = probability tx reverts (arb taken by someone else, price moved)
- $G_{failure}$ = gas cost of failed transaction

For the trading system, it is worth attempting flash loans when:

$$
EV > 0 \implies P_{success} > \frac{G_{failure}}{\Pi_{success} + G_{failure}}
$$

---

## 14. Risk Parameters

### 14.1 Flash Loan Operation Limits

| Parameter                        | Value      | Rationale                     |
|----------------------------------|------------|-------------------------------|
| Max flash loan amount            | $5M        | Limit exposure per transaction|
| Max gas per transaction          | 3M gas     | Prevent runaway gas costs     |
| Min profit threshold             | $200       | Must cover gas + risk premium |
| Max profit expectation           | $50K       | Sanity check (if too high, likely error) |
| Max failed tx per hour           | 10         | Limit gas waste              |
| Max daily gas budget (flash ops) | $5,000     | Cap total daily gas spend     |
| Simulation required              | Always     | Must simulate before execution|
| Max slippage tolerance           | 1%         | Limit execution risk          |
| Blacklisted protocols            | Maintained | Known vulnerable protocols    |

### 14.2 Smart Contract Safety

```
BEFORE deploying flash loan contract:

[x] Audited by 2+ firms
[x] Formal verification of repayment logic
[x] Access control on strategy registration
[x] Reentrancy guards on all external calls
[x] Slippage protection on all swaps
[x] Deadline protection on all operations
[x] Emergency withdrawal function (admin only)
[x] Profit recipient cannot be changed without timelock
[x] No delegatecall to unregistered contracts
[x] Max flash loan amount enforced at contract level
```

### 14.3 MEV Protection

Flash loan transactions are particularly vulnerable to MEV:

| Attack Type     | Risk                               | Mitigation                    |
|-----------------|-------------------------------------|-------------------------------|
| Front-running   | Another bot takes the opportunity   | Private mempool (Flashbots)   |
| Sandwich        | Swap slippage exploited             | Tight slippage limits         |
| Back-running    | Copies strategy after execution     | Speed (first-mover advantage) |
| Salmonella      | Token with hidden tax/trap          | Token whitelist only          |

**Required**: All flash loan transactions MUST be submitted via private mempool
(Flashbots Protect, MEV Blocker, etc.) to prevent front-running.

---

## 15. Execution Flow — Flash Loan Bot

### 15.1 Complete Flash Loan Arbitrage Bot

```python
class FlashLoanArbitrageBot:
    """
    Monitors DEX prices for arbitrage opportunities
    and executes them via flash loans.
    """

    def __init__(self, config: FlashBotConfig):
        self.web3 = Web3Provider(config.rpc_url)
        self.flash_contract = FlashLoanContract(config.contract_address)
        self.dex_monitor = MultiDEXMonitor(config.monitored_pools)
        self.gas_estimator = GasEstimator()
        self.profitability_checker = ProfitabilityChecker()
        self.flashbots = FlashbotsProvider(config.flashbots_key)
        self.risk_limits = config.risk_limits

    async def main_loop(self):
        """Main arbitrage scanning loop."""
        while True:
            try:
                # ==========================================
                # STEP 1: Monitor prices across DEXes
                # ==========================================
                price_matrix = await self.dex_monitor.get_all_prices()

                # ==========================================
                # STEP 2: Identify arbitrage opportunities
                # ==========================================
                opportunities = self.find_opportunities(price_matrix)

                if not opportunities:
                    await asyncio.sleep(0.5)  # 500ms between scans
                    continue

                # ==========================================
                # STEP 3: Evaluate profitability
                # ==========================================
                for opp in opportunities:
                    # Calculate optimal size
                    optimal_size = self.calculate_optimal_size(opp)
                    opp.size = optimal_size

                    # Estimate gas
                    gas_estimate = await self.gas_estimator.estimate(opp)
                    opp.gas_cost = gas_estimate

                    # Calculate expected profit
                    opp.expected_profit = self.profitability_checker.calculate(opp)

                # Filter profitable opportunities
                profitable = [o for o in opportunities
                             if o.expected_profit > self.risk_limits.min_profit]

                if not profitable:
                    await asyncio.sleep(0.5)
                    continue

                # ==========================================
                # STEP 4: Simulate transaction
                # ==========================================
                best_opp = max(profitable, key=lambda o: o.expected_profit)

                simulation = await self.simulate_flash_loan(best_opp)
                if not simulation.success:
                    logger.debug(f"Simulation failed: {simulation.reason}")
                    continue

                if simulation.profit < self.risk_limits.min_profit:
                    logger.debug(f"Simulated profit too low: {simulation.profit}")
                    continue

                # ==========================================
                # STEP 5: Execute via Flashbots (private mempool)
                # ==========================================
                tx = self.build_flash_loan_tx(best_opp)
                bundle = self.flashbots.build_bundle([tx])

                result = await self.flashbots.send_bundle(
                    bundle,
                    target_block=await self.web3.get_block_number() + 1
                )

                if result.success:
                    logger.info(
                        f"Flash loan arb executed! "
                        f"Profit: ${simulation.profit:.2f} "
                        f"Path: {best_opp.path}"
                    )
                    self.record_trade(best_opp, result)
                else:
                    logger.debug(f"Bundle not included: {result.reason}")

            except Exception as e:
                logger.error(f"Flash loan bot error: {e}")
                await asyncio.sleep(1)

    def find_opportunities(self, price_matrix: PriceMatrix) -> List[ArbOpportunity]:
        """
        Find price discrepancies across DEXes.
        Uses Bellman-Ford algorithm for multi-hop detection.
        """
        opportunities = []

        # Direct two-leg arbitrage
        for token_pair in price_matrix.pairs():
            prices = price_matrix.get_prices(token_pair)
            min_price = min(prices, key=lambda p: p.price)
            max_price = max(prices, key=lambda p: p.price)

            spread = (max_price.price - min_price.price) / min_price.price

            if spread > 0.002:  # > 0.2% spread (enough to cover fees)
                opportunities.append(ArbOpportunity(
                    token_pair=token_pair,
                    buy_venue=min_price.venue,
                    sell_venue=max_price.venue,
                    buy_price=min_price.price,
                    sell_price=max_price.price,
                    spread=spread,
                    path=[min_price.venue, max_price.venue]
                ))

        # Multi-hop (Bellman-Ford on -log(price) graph)
        multi_hop = self.bellman_ford_arbitrage(price_matrix)
        opportunities.extend(multi_hop)

        return sorted(opportunities, key=lambda o: o.spread, reverse=True)

    def calculate_optimal_size(self, opp: ArbOpportunity) -> float:
        """
        Calculate optimal flash loan size considering price impact.
        """
        # Get reserves of relevant pools
        buy_reserves = self.dex_monitor.get_reserves(opp.buy_venue, opp.token_pair)
        sell_reserves = self.dex_monitor.get_reserves(opp.sell_venue, opp.token_pair)

        # Optimal size formula (simplified for CPMM)
        r_a = buy_reserves.base_reserve
        r_b = sell_reserves.base_reserve
        p_ratio = opp.sell_price / opp.buy_price
        fee_mult = (1 - opp.buy_venue.fee) * (1 - opp.sell_venue.fee)

        optimal = math.sqrt(r_a * r_b * p_ratio * fee_mult) - r_a
        optimal = max(0, optimal)

        # Apply risk limits
        optimal = min(optimal, self.risk_limits.max_flash_amount)

        return optimal

    async def simulate_flash_loan(self, opp: ArbOpportunity) -> SimulationResult:
        """
        Simulate the flash loan transaction using eth_call.
        Returns expected profit without actually executing.
        """
        # Build transaction calldata
        calldata = self.flash_contract.build_calldata(
            strategy_id=ARBITRAGE_STRATEGY,
            flash_amount=opp.size,
            params=self.encode_arb_params(opp)
        )

        # Simulate via eth_call (state override if needed)
        try:
            result = await self.web3.eth_call(
                to=self.flash_contract.address,
                data=calldata,
                block='latest'
            )
            profit = self.decode_profit(result)
            return SimulationResult(success=True, profit=profit)
        except Exception as e:
            return SimulationResult(success=False, reason=str(e), profit=0)

    def bellman_ford_arbitrage(self, price_matrix: PriceMatrix) -> List[ArbOpportunity]:
        """
        Use Bellman-Ford algorithm to detect negative cycles
        (= profitable circular arbitrage paths).
        """
        # Build graph: nodes = tokens, edges = -log(exchange_rate)
        graph = {}
        for pair in price_matrix.pairs():
            for price_info in price_matrix.get_prices(pair):
                token_a, token_b = pair
                rate = price_info.price * (1 - price_info.fee)
                weight = -math.log(rate)

                if token_a not in graph:
                    graph[token_a] = []
                graph[token_a].append((token_b, weight, price_info.venue))

        # Bellman-Ford for each starting node
        opportunities = []
        for start_token in graph:
            cycle = self._find_negative_cycle(graph, start_token)
            if cycle:
                opportunities.append(self._cycle_to_opportunity(cycle))

        return opportunities
```

### 15.2 Flash Loan Liquidation Bot

```python
class FlashLoanLiquidationBot:
    """
    Monitors lending protocols for undercollateralized positions
    and liquidates them using flash loans.
    """

    async def scan_for_liquidations(self) -> List[LiquidationOpportunity]:
        """Scan all monitored lending protocols for liquidation opportunities."""
        opportunities = []

        for protocol in self.monitored_protocols:
            # Get all positions near liquidation
            at_risk = await protocol.get_positions_below_hf(
                max_health_factor=1.0  # Already liquidatable
            )

            for position in at_risk:
                # Calculate liquidation profit
                max_liquidation = min(
                    position.debt * 0.5,  # Max 50% close factor (Aave)
                    self.risk_limits.max_flash_amount
                )

                bonus = position.collateral_asset.liquidation_bonus
                collateral_received = max_liquidation * (1 + bonus) / position.collateral_price

                # Estimate swap output (selling collateral)
                swap_output = await self.estimate_swap(
                    position.collateral_asset,
                    position.debt_asset,
                    collateral_received
                )

                profit = swap_output - max_liquidation - self.estimate_gas() - \
                         max_liquidation * self.flash_loan_fee

                if profit > self.risk_limits.min_profit:
                    opportunities.append(LiquidationOpportunity(
                        protocol=protocol,
                        position=position,
                        debt_to_cover=max_liquidation,
                        expected_profit=profit,
                        collateral_received=collateral_received
                    ))

        return sorted(opportunities, key=lambda o: o.expected_profit, reverse=True)
```

---

## 16. References

### Technical Papers

1. Qin, K., Zhou, L., Gervais, A. (2021). "Quantifying Blockchain Extractable Value:
   How Dark is the Forest?" IEEE Symposium on Security and Privacy.

2. Wang, D., Wu, S., Lin, Z., et al. (2021). "Towards Understanding Flash Loan and
   its Applications in DeFi Ecosystem." arXiv:2010.12252.

3. Cao, Y., Zou, C., Cheng, X. (2021). "Flashot: A Snapshot of Flash Loan Attack
   on DeFi Ecosystem." arXiv:2102.00626.

4. Daian, P., Goldfeder, S., Kell, T., et al. (2020). "Flash Boys 2.0:
   Frontrunning, Transaction Reordering, and Consensus Instability in Decentralized
   Exchanges." IEEE S&P.

### Protocol Documentation

5. Aave V3 Flash Loan Documentation. https://docs.aave.com/developers/guides/flash-loans
6. Balancer Flash Loan Documentation. https://docs.balancer.fi/reference/contracts/flash-loans.html
7. dYdX Flash Loan Documentation. https://docs.dydx.exchange/
8. MakerDAO Flash Mint. https://docs.makerdao.com/smart-contract-modules/flash-mint-module
9. Uniswap V3 Flash Swap. https://docs.uniswap.org/contracts/v3/guides/flash-integrations

### MEV Resources

10. Flashbots Documentation. https://docs.flashbots.net/
11. MEV Explore. https://explore.flashbots.net/
12. EigenPhi — MEV Analysis. https://eigenphi.io/

---

> **Next Document**: [05_lending_borrowing.md](./05_lending_borrowing.md)
> — Lending and borrowing protocol mechanics with interest rate models.
