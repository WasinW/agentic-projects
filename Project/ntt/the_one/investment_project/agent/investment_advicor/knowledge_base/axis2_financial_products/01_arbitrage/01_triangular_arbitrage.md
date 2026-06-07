# Triangular Arbitrage — Complete Strategy Documentation

> **Document Version:** 2.0
> **Last Updated:** 2026-04-12
> **Classification:** Core Knowledge Base — Axis 2: Financial Products
> **Strategy Type:** Pure (Near Risk-Free) Arbitrage
> **Markets:** Forex, Crypto (CeFi & DeFi)
> **Frequency:** High-Frequency (milliseconds to seconds)

---

## Table of Contents

1. [Core Logic](#1-core-logic)
2. [Currency Pair Selection](#2-currency-pair-selection)
3. [Cross-Rate Calculation](#3-cross-rate-calculation)
4. [Profit Calculation and Fee Structure](#4-profit-calculation-and-fee-structure)
5. [Minimum Profitable Spread Threshold](#5-minimum-profitable-spread-threshold)
6. [Execution Speed Requirements](#6-execution-speed-requirements)
7. [Risk Factors](#7-risk-factors)
8. [Complete Pseudocode Algorithm](#8-complete-pseudocode-algorithm)
9. [Worked Examples with Real Numbers](#9-worked-examples-with-real-numbers)
10. [Risk Parameters and Position Sizing](#10-risk-parameters-and-position-sizing)
11. [Backtesting Framework](#11-backtesting-framework)
12. [Production Deployment Considerations](#12-production-deployment-considerations)
13. [References](#13-references)

---

## 1. Core Logic

### 1.1 What Is Triangular Arbitrage?

Triangular arbitrage exploits pricing inconsistencies among three related currency pairs traded on the same exchange (or across venues). When the cross-rate implied by two currency pairs deviates from the directly quoted third pair, a risk-free profit can be locked in by simultaneously executing three trades that form a closed loop.

### 1.2 The Triangular Relationship

Given three currencies A, B, and C, the no-arbitrage condition requires:

$$\frac{A}{B} = \frac{A}{C} \times \frac{C}{B}$$

Or equivalently:

$$R_{A/B} \times R_{B/C} \times R_{C/A} = 1$$

When this product deviates from 1, an arbitrage opportunity exists.

### 1.3 Step-by-Step Logic

**Direction 1 (Clockwise): A -> B -> C -> A**

```
Step 1: Convert currency A to currency B
        Buy B with A at rate R_{A/B}
        Amount of B = Q_A / R_{A/B}  (if R_{A/B} is price of B in A)
        
Step 2: Convert currency B to currency C
        Buy C with B at rate R_{B/C}
        Amount of C = Q_B / R_{B/C}
        
Step 3: Convert currency C back to currency A
        Buy A with C at rate R_{C/A}
        Amount of A = Q_C / R_{C/A}
        
If final amount of A > initial amount of A (after fees), profit exists.
```

**Direction 2 (Counter-clockwise): A -> C -> B -> A**

```
Step 1: Convert currency A to currency C
Step 2: Convert currency C to currency B
Step 3: Convert currency B back to currency A
```

Both directions must be checked simultaneously because the profitable direction depends on which cross-rate is mispriced.

### 1.4 Detecting the Arbitrage Direction

Compute the implied cross-rate product for the clockwise direction:

$$\Pi_{CW} = R_1 \times R_2 \times R_3$$

And for the counter-clockwise direction:

$$\Pi_{CCW} = \frac{1}{R_1} \times \frac{1}{R_2} \times \frac{1}{R_3} = \frac{1}{\Pi_{CW}}$$

- If $\Pi_{CW} > 1$: Profit exists in the clockwise direction
- If $\Pi_{CW} < 1$: Profit exists in the counter-clockwise direction (equivalently, $\Pi_{CCW} > 1$)
- If $\Pi_{CW} = 1$: No arbitrage opportunity

**Critical Nuance — Using Bid/Ask Prices:**

In practice, you must use the appropriate side of the order book:
- When **selling** currency X for Y: use the **bid** price (you receive the bid)
- When **buying** currency X with Y: use the **ask** price (you pay the ask)

The effective cross-rate product using bid/ask:

$$\Pi_{CW}^{effective} = \frac{bid_1}{1} \times \frac{bid_2}{1} \times \frac{bid_3}{1}$$

(Adjusted based on which side of each pair you trade.)

---

## 2. Currency Pair Selection

### 2.1 Forex Pairs

The most common triangular arbitrage triplets in Forex involve major currencies with high liquidity:

**Tier 1 (Most Liquid — Highest Competition):**

| Triangle | Pair 1 | Pair 2 | Pair 3 |
|----------|--------|--------|--------|
| USD-EUR-GBP | EUR/USD | GBP/USD | EUR/GBP |
| USD-EUR-JPY | EUR/USD | USD/JPY | EUR/JPY |
| USD-GBP-JPY | GBP/USD | USD/JPY | GBP/JPY |
| USD-EUR-CHF | EUR/USD | USD/CHF | EUR/CHF |

**Tier 2 (Moderate Liquidity — More Opportunities):**

| Triangle | Pair 1 | Pair 2 | Pair 3 |
|----------|--------|--------|--------|
| USD-AUD-NZD | AUD/USD | NZD/USD | AUD/NZD |
| USD-EUR-AUD | EUR/USD | AUD/USD | EUR/AUD |
| USD-GBP-CHF | GBP/USD | USD/CHF | GBP/CHF |
| USD-CAD-JPY | USD/CAD | USD/JPY | CAD/JPY |

**Tier 3 (Lower Liquidity — Wider Spreads but More Opportunities):**

| Triangle | Pair 1 | Pair 2 | Pair 3 |
|----------|--------|--------|--------|
| USD-EUR-NOK | EUR/USD | USD/NOK | EUR/NOK |
| USD-GBP-AUD | GBP/USD | AUD/USD | GBP/AUD |
| USD-EUR-SEK | EUR/USD | USD/SEK | EUR/SEK |

### 2.2 Crypto Pairs

Crypto markets offer significantly more triangular arbitrage opportunities due to market fragmentation and lower efficiency.

**Tier 1 (Major Crypto Triangles):**

| Triangle | Pair 1 | Pair 2 | Pair 3 |
|----------|--------|--------|--------|
| USDT-BTC-ETH | BTC/USDT | ETH/USDT | ETH/BTC |
| USDT-BTC-BNB | BTC/USDT | BNB/USDT | BNB/BTC |
| USDT-BTC-SOL | BTC/USDT | SOL/USDT | SOL/BTC |
| USDT-ETH-BNB | ETH/USDT | BNB/USDT | BNB/ETH |

**Tier 2 (Alt-coin Triangles):**

| Triangle | Pair 1 | Pair 2 | Pair 3 |
|----------|--------|--------|--------|
| USDT-BTC-XRP | BTC/USDT | XRP/USDT | XRP/BTC |
| USDT-BTC-ADA | BTC/USDT | ADA/USDT | ADA/BTC |
| USDT-ETH-LINK | ETH/USDT | LINK/USDT | LINK/ETH |
| USDT-BTC-AVAX | BTC/USDT | AVAX/USDT | AVAX/BTC |

**Tier 3 (Cross-Stablecoin Triangles):**

| Triangle | Pair 1 | Pair 2 | Pair 3 |
|----------|--------|--------|--------|
| USDT-USDC-BTC | BTC/USDT | BTC/USDC | USDT/USDC |
| USDT-BUSD-ETH | ETH/USDT | ETH/BUSD | USDT/BUSD |
| USDC-DAI-ETH | ETH/USDC | ETH/DAI | USDC/DAI |

### 2.3 Pair Selection Criteria

For effective triangular arbitrage, selected triplets should satisfy:

1. **Sufficient liquidity:** Average daily volume > $10M per pair (crypto) or > $1B per pair (forex)
2. **Tight spreads:** Bid-ask spread < 5 bps (ideally < 2 bps)
3. **Order book depth:** At least 5 BTC equivalent depth within 10 bps of mid-price
4. **Low correlation of spread movements:** Spreads should not widen simultaneously across all three pairs
5. **Exchange support:** All three pairs available on the same exchange (for single-exchange triangular arb)
6. **API support:** Real-time WebSocket order book feed available

---

## 3. Cross-Rate Calculation

### 3.1 Direct Cross-Rate

For currencies A, B, C where the exchange quotes pairs as A/B, B/C, and A/C:

**Implied cross-rate of A/C from A/B and B/C:**

$$\hat{R}_{A/C} = R_{A/B} \times R_{B/C}$$

**Arbitrage signal:**

$$\delta = \frac{R_{A/C}^{market} - \hat{R}_{A/C}}{\hat{R}_{A/C}}$$

If $|\delta| > \delta_{threshold}$ (where $\delta_{threshold}$ accounts for all fees and costs), an opportunity exists.

### 3.2 Bid-Ask Adjusted Cross-Rate

The effective cross-rates must account for bid-ask spreads:

**For the clockwise direction (buy B with A, buy C with B, sell C for A):**

$$\Pi_{CW} = \frac{1}{ask_{A/B}} \times \frac{1}{ask_{B/C}} \times bid_{A/C}$$

Wait — more precisely, we need to trace the exact sequence of trades.

**Generalized Approach:**

Let us define the three pairs as $P_1$, $P_2$, $P_3$ forming a triangle. For each pair, we have:
- $bid_i$: the price at which we can sell the base currency
- $ask_i$: the price at which we can buy the base currency

For each potential trade:
- If we are buying the base currency: we pay the $ask$ price
- If we are selling the base currency: we receive the $bid$ price

**Example: EUR/USD, GBP/USD, EUR/GBP**

**Clockwise: USD -> EUR -> GBP -> USD**

1. Buy EUR with USD: Pay $ask_{EUR/USD}$ per EUR. Get $\frac{Q_{USD}}{ask_{EUR/USD}}$ EUR.
2. Sell EUR for GBP: Sell EUR at $bid_{EUR/GBP}$. Get $Q_{EUR} \times bid_{EUR/GBP}$ GBP.
3. Sell GBP for USD: Sell GBP at $bid_{GBP/USD}$. Get $Q_{GBP} \times bid_{GBP/USD}$ USD.

**Final USD amount:**

$$Q_{final} = Q_{USD} \times \frac{bid_{EUR/GBP} \times bid_{GBP/USD}}{ask_{EUR/USD}}$$

**Profit condition (before fees):**

$$\frac{bid_{EUR/GBP} \times bid_{GBP/USD}}{ask_{EUR/USD}} > 1$$

### 3.3 Rate Normalization

Different exchanges and markets quote pairs in different conventions. A critical step is normalizing all rates into a consistent format.

**Convention: Base/Quote where rate = price of 1 unit of Base in Quote currency.**

If a pair is quoted as Quote/Base on the exchange, invert it:

$$R_{Base/Quote} = \frac{1}{R_{Quote/Base}}$$

And the bid/ask inversion:

$$bid_{Base/Quote} = \frac{1}{ask_{Quote/Base}}$$
$$ask_{Base/Quote} = \frac{1}{bid_{Quote/Base}}$$

---

## 4. Profit Calculation and Fee Structure

### 4.1 Gross Profit Formula

For a triangular arbitrage starting and ending with quantity $Q_{initial}$ of currency A:

$$Q_{final} = Q_{initial} \times R_1^{eff} \times R_2^{eff} \times R_3^{eff}$$

Where $R_i^{eff}$ is the effective rate for leg $i$ (using the appropriate bid or ask).

$$P_{gross} = Q_{final} - Q_{initial}$$

### 4.2 Fee Structure

#### 4.2.1 Trading Fees (Maker/Taker)

| Exchange | Maker Fee | Taker Fee | VIP Taker Fee |
|----------|:---------:|:---------:|:-------------:|
| **Forex (ECN)** | $0-3/million | $2-5/million | $0-2/million |
| **Binance** | 0.10% | 0.10% | 0.02% (VIP 9) |
| **Coinbase Advanced** | 0.40% | 0.60% | 0.05% (VIP) |
| **OKX** | 0.08% | 0.10% | 0.02% (VIP 7) |
| **Bybit** | 0.10% | 0.10% | 0.02% (VIP) |
| **Kraken** | 0.16% | 0.26% | 0.00% / 0.10% |

**Fee per leg:**

$$F_i = Q_i \times P_i \times f_i$$

Where $f_i$ is the fee rate (maker or taker, depending on order type).

**Total fees for 3-leg arbitrage:**

$$F_{total} = \sum_{i=1}^{3} F_i = \sum_{i=1}^{3} Q_i \times P_i \times f_i$$

For a simplified case where fee rate is the same across all legs:

$$F_{total} \approx 3 \times Q_{initial} \times f$$

(This is approximate because $Q_i$ and $P_i$ vary per leg.)

#### 4.2.2 Spread Costs

The spread cost is implicitly captured when using bid/ask prices. However, for analysis:

$$C_{spread,i} = Q_i \times \frac{ask_i - bid_i}{2}$$

Total spread cost:

$$C_{spread} = \sum_{i=1}^{3} C_{spread,i}$$

#### 4.2.3 Slippage Estimation

Slippage occurs when the executed price differs from the expected price due to order book consumption:

$$C_{slippage,i} = Q_i \times P_i \times s_i$$

Where $s_i$ is the estimated slippage rate, which depends on:
- Order size relative to order book depth
- Market volatility
- Time of day (liquidity varies)

**Slippage estimation model:**

$$s_i = \alpha_i \times \left(\frac{Q_i}{D_i}\right)^{\beta_i}$$

Where:
- $D_i$ = order book depth at the best level
- $\alpha_i$ = scaling constant (calibrated from historical data)
- $\beta_i$ = elasticity parameter (typically 0.5 - 1.5)

### 4.3 Net Profit Formula

The complete net profit formula:

$$P_{net} = (Q_{initial} \times R_1^{eff} \times R_2^{eff} \times R_3^{eff}) - Q_{initial} - F_{total} - C_{slippage}$$

Or equivalently:

$$\boxed{P_{net} = Q_{initial} \times \left(\prod_{i=1}^{3} R_i^{eff} \times (1 - f_i) \times (1 - s_i) - 1\right)}$$

Where:
- $R_i^{eff}$ = effective exchange rate for leg $i$ (bid or ask as appropriate)
- $f_i$ = fee rate for leg $i$
- $s_i$ = estimated slippage rate for leg $i$
- $Q_{initial}$ = initial quantity in the starting currency

### 4.4 Return on Capital

$$r = \frac{P_{net}}{Q_{initial}} = \prod_{i=1}^{3} R_i^{eff} \times (1 - f_i) \times (1 - s_i) - 1$$

The annualized return depends on the frequency of profitable trades:

$$R_{annual} = (1 + r)^{N} - 1$$

Where $N$ is the number of trades per year.

---

## 5. Minimum Profitable Spread Threshold

### 5.1 Derivation

For a triangular arbitrage to be profitable, the cross-rate deviation must exceed all costs:

$$\left|\prod_{i=1}^{3} R_i^{eff} - 1\right| > \sum_{i=1}^{3} (f_i + s_i) + \epsilon$$

Where $\epsilon$ is a safety margin.

**Simplified minimum spread (assuming equal fees and slippage across legs):**

$$\delta_{min} = 3f + 3s + \epsilon$$

**Example for Binance (standard tier):**

$$\delta_{min} = 3 \times 0.001 + 3 \times 0.0002 + 0.0005 = 0.0041 = 41 \text{ bps}$$

**Example for Binance (VIP 9 + BNB discount):**

$$\delta_{min} = 3 \times 0.0002 + 3 \times 0.0001 + 0.0003 = 0.0012 = 12 \text{ bps}$$

### 5.2 Dynamic Threshold Calculation

The minimum threshold should be dynamically calculated based on current market conditions:

```python
def calculate_min_threshold(pair_states, fee_rates, safety_margin=0.0005):
    """
    Calculate the minimum cross-rate deviation for profitable arbitrage.
    
    Args:
        pair_states: List of (bid, ask, depth) for each pair
        fee_rates: List of fee rates for each leg
        safety_margin: Additional buffer (default 5 bps)
    
    Returns:
        Minimum profitable deviation as a decimal
    """
    total_fee_cost = sum(fee_rates)
    
    total_spread_cost = sum(
        (ask - bid) / ((ask + bid) / 2)
        for bid, ask, _ in pair_states
    )
    
    total_slippage_est = sum(
        estimate_slippage(depth)
        for _, _, depth in pair_states
    )
    
    return total_fee_cost + total_spread_cost + total_slippage_est + safety_margin
```

### 5.3 Profitability Heat Map

The following shows typical profitability zones by fee tier and market conditions:

| Fee Tier | Calm Market (spread < 2bps) | Normal (spread 2-5bps) | Volatile (spread > 5bps) |
|----------|:---------------------------:|:----------------------:|:------------------------:|
| Standard (0.10%) | Unprofitable | Rare opportunities | Possible |
| VIP Mid (0.05%) | Rare opportunities | Moderate | Good |
| VIP Top (0.02%) | Moderate | Good | Excellent |
| Market Maker (0.00%) | Good | Excellent | Excellent |

---

## 6. Execution Speed Requirements

### 6.1 Latency Budget

The total time from opportunity detection to full execution must be minimized. A typical latency budget:

| Component | Forex (Target) | Crypto (Target) |
|-----------|:--------------:|:---------------:|
| Market data receipt | < 10 μs | < 1 ms |
| Opportunity detection | < 5 μs | < 0.5 ms |
| Profitability check | < 2 μs | < 0.2 ms |
| Risk check | < 2 μs | < 0.2 ms |
| Order construction | < 1 μs | < 0.1 ms |
| Network transmission | < 50 μs | < 5 ms |
| Exchange matching | < 100 μs | < 10 ms |
| **Total** | **< 170 μs** | **< 17 ms** |

### 6.2 Why Speed Matters

Triangular arbitrage opportunities in liquid markets have a half-life measured in:
- **Forex:** 10-100 milliseconds (major pairs)
- **Crypto (major pairs):** 100ms - 5 seconds
- **Crypto (alt pairs):** 1 - 30 seconds

**Opportunity decay model:**

$$P(opportunity\_available | t) = e^{-\lambda t}$$

Where $\lambda$ is the decay rate. For Forex majors, $\lambda \approx 10-100/s$ (opportunity disappears within ~10-100ms). For crypto, $\lambda \approx 0.2-2/s$.

### 6.3 Optimization Strategies

1. **Pre-computed order templates:** Have orders ready with only price/quantity to fill in
2. **Batch order submission:** Submit all three legs in a single API call if exchange supports it
3. **WebSocket vs. REST:** Use WebSocket for data, REST/WebSocket for order submission
4. **Local order book maintenance:** Maintain a local copy updated via incremental WebSocket messages
5. **Warm connections:** Keep HTTP/WebSocket connections alive and pre-authenticated
6. **Co-location:** Place servers as close to exchange matching engines as possible

---

## 7. Risk Factors

### 7.1 Execution Risk

The primary risk in triangular arbitrage is that not all three legs execute successfully or at the expected prices.

**7.1.1 Partial Fills**

If one or two legs fill but the third does not:
- You are left with an unhedged position
- The remaining position is subject to market risk
- Must be unwound immediately, often at a loss

**Mitigation:**
- Use Fill-or-Kill (FOK) or Immediate-or-Cancel (IOC) orders
- Size orders conservatively relative to order book depth
- Implement automatic unwind logic

**7.1.2 Race Conditions**

Multiple arbitrageurs may detect the same opportunity simultaneously:
- The fastest executor captures the opportunity
- Slower participants face adverse fills or rejections
- This creates a "winner's curse" dynamic

### 7.2 Slippage Risk

**Expected slippage by order size (Crypto, major pairs on Binance):**

| Order Size (USD) | Expected Slippage (bps) | Standard Deviation (bps) |
|:-----------------:|:-----------------------:|:------------------------:|
| $1,000 | 0.1 | 0.05 |
| $10,000 | 0.5 | 0.3 |
| $50,000 | 2.0 | 1.5 |
| $100,000 | 5.0 | 3.0 |
| $500,000 | 15.0 | 10.0 |

### 7.3 Timing Risk

Between detecting an opportunity and executing all three legs:
- Prices may move, invalidating the arbitrage
- Other participants may consume the available liquidity
- Exchange may experience momentary delays

### 7.4 Technology Risk

- API rate limiting (exchanges may reject orders if rate limit exceeded)
- WebSocket disconnections (stale data leads to false signals)
- Exchange maintenance windows
- Software bugs in price calculation or order construction

### 7.5 Counterparty / Exchange Risk

- Exchange insolvency (all pre-positioned capital at risk)
- Trading halts on specific pairs
- Retroactive trade cancellations (exchanges can "bust" trades)
- Account restrictions or freezes

### 7.6 Fee Change Risk

- Exchanges may change fee structures without advance notice
- Volume-based tiers may shift as trading patterns change
- Promotional fee rates may expire

---

## 8. Complete Pseudocode Algorithm

### 8.1 Main Triangular Arbitrage Engine

```python
import asyncio
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum

# ============================================================
# DATA STRUCTURES
# ============================================================

class Direction(Enum):
    CLOCKWISE = "CW"
    COUNTER_CLOCKWISE = "CCW"

@dataclass
class OrderBookLevel:
    price: float
    quantity: float

@dataclass
class OrderBook:
    pair: str
    bids: List[OrderBookLevel]   # sorted descending by price
    asks: List[OrderBookLevel]   # sorted ascending by price
    timestamp: float
    
    @property
    def best_bid(self) -> float:
        return self.bids[0].price if self.bids else 0
    
    @property
    def best_ask(self) -> float:
        return self.asks[0].price if self.asks else float('inf')
    
    @property
    def mid_price(self) -> float:
        return (self.best_bid + self.best_ask) / 2
    
    @property
    def spread_bps(self) -> float:
        return (self.best_ask - self.best_bid) / self.mid_price * 10000

@dataclass
class TriangleLeg:
    pair: str
    side: str                    # "BUY" or "SELL"
    price: float                 # Expected execution price
    quantity: float              # Quantity in base currency
    fee_rate: float              # Fee rate for this leg

@dataclass
class ArbitrageOpportunity:
    triangle: Tuple[str, str, str]    # Three pair symbols
    direction: Direction
    legs: List[TriangleLeg]
    expected_profit: float             # Net profit in quote currency
    expected_profit_bps: float         # Net profit in basis points
    cross_rate_deviation: float        # Deviation from no-arb condition
    timestamp: float

@dataclass
class ExecutionResult:
    opportunity: ArbitrageOpportunity
    fills: List[dict]                  # Actual fill details per leg
    actual_profit: float
    execution_time_ms: float
    success: bool
    error_message: Optional[str]

# ============================================================
# CONFIGURATION
# ============================================================

@dataclass
class TriangularArbConfig:
    # Triangle definitions
    triangles: List[Tuple[str, str, str]]
    
    # Fee parameters
    fee_rates: dict                     # {pair: fee_rate}
    default_fee_rate: float = 0.001     # 10 bps default
    
    # Profitability thresholds
    min_profit_bps: float = 3.0         # Minimum net profit in bps
    safety_margin_bps: float = 1.0      # Additional safety buffer
    
    # Position sizing
    base_order_size_usd: float = 10000  # Base order size in USD
    max_order_size_usd: float = 50000   # Maximum order size in USD
    max_position_usd: float = 100000    # Maximum open position
    
    # Execution parameters
    max_execution_time_ms: float = 500  # Maximum time for all legs
    order_type: str = "LIMIT_IOC"       # LIMIT_IOC, MARKET, LIMIT_FOK
    max_slippage_bps: float = 5.0       # Maximum acceptable slippage
    
    # Risk parameters
    max_daily_loss_usd: float = 500     # Stop trading after this loss
    max_consecutive_losses: int = 5     # Circuit breaker
    max_daily_trades: int = 1000        # Rate limit
    
    # Order book requirements
    min_book_depth_usd: float = 20000   # Minimum depth at best level
    max_book_age_ms: float = 100        # Maximum age of order book data
    
    # Monitoring
    log_all_opportunities: bool = True
    log_executions: bool = True

# ============================================================
# CORE ENGINE
# ============================================================

class TriangularArbitrageEngine:
    """
    Complete triangular arbitrage engine with:
    - Real-time order book monitoring
    - Opportunity detection
    - Profitability checking (including all fees)
    - Simultaneous order execution
    - P&L tracking
    - Risk management
    """
    
    def __init__(self, config: TriangularArbConfig, exchange_client, risk_manager):
        self.config = config
        self.exchange = exchange_client
        self.risk_manager = risk_manager
        
        # State
        self.order_books: dict = {}          # {pair: OrderBook}
        self.daily_pnl: float = 0.0
        self.daily_trades: int = 0
        self.consecutive_losses: int = 0
        self.is_running: bool = False
        self.trade_history: List[ExecutionResult] = []
    
    # ----------------------------------------------------------
    # PHASE 1: MARKET DATA MONITORING
    # ----------------------------------------------------------
    
    async def start(self):
        """Main entry point. Start monitoring and trading."""
        self.is_running = True
        
        # Subscribe to order book updates for all pairs in all triangles
        all_pairs = set()
        for triangle in self.config.triangles:
            all_pairs.update(triangle)
        
        # Start WebSocket subscriptions
        subscription_tasks = [
            self.subscribe_order_book(pair) for pair in all_pairs
        ]
        
        # Start the main monitoring loop
        monitoring_task = asyncio.create_task(self.monitoring_loop())
        
        await asyncio.gather(*subscription_tasks, monitoring_task)
    
    async def subscribe_order_book(self, pair: str):
        """Subscribe to real-time order book updates via WebSocket."""
        async for update in self.exchange.ws_order_book(pair):
            self.order_books[pair] = OrderBook(
                pair=pair,
                bids=update['bids'],
                asks=update['asks'],
                timestamp=time.time()
            )
    
    async def monitoring_loop(self):
        """
        Main monitoring loop.
        Continuously scans for arbitrage opportunities across all triangles.
        """
        while self.is_running:
            # Check circuit breakers
            if self.check_circuit_breakers():
                break
            
            # Scan all triangles
            for triangle in self.config.triangles:
                # Ensure we have fresh order book data for all pairs
                if not self.validate_order_books(triangle):
                    continue
                
                # Detect opportunity
                opportunity = self.detect_opportunity(triangle)
                
                if opportunity is not None:
                    # Execute if profitable
                    result = await self.execute_opportunity(opportunity)
                    
                    if result is not None:
                        self.process_result(result)
            
            # Small sleep to prevent CPU spinning
            # In production, this would be event-driven (triggered by order book updates)
            await asyncio.sleep(0.001)  # 1ms
    
    # ----------------------------------------------------------
    # PHASE 2: OPPORTUNITY DETECTION
    # ----------------------------------------------------------
    
    def validate_order_books(self, triangle: Tuple[str, str, str]) -> bool:
        """Check that order books are available and fresh."""
        now = time.time()
        for pair in triangle:
            if pair not in self.order_books:
                return False
            book = self.order_books[pair]
            age_ms = (now - book.timestamp) * 1000
            if age_ms > self.config.max_book_age_ms:
                return False
            if not book.bids or not book.asks:
                return False
        return True
    
    def detect_opportunity(self, triangle: Tuple[str, str, str]) -> Optional[ArbitrageOpportunity]:
        """
        Detect triangular arbitrage opportunity.
        
        Checks both clockwise and counter-clockwise directions.
        Returns the profitable direction if any, or None.
        """
        pair1, pair2, pair3 = triangle
        book1 = self.order_books[pair1]
        book2 = self.order_books[pair2]
        book3 = self.order_books[pair3]
        
        # Check clockwise direction
        # Example: USDT -> BTC -> ETH -> USDT
        # Leg 1: Buy BTC with USDT (pay ask on BTC/USDT)
        # Leg 2: Sell BTC for ETH, i.e., Buy ETH with BTC (pay ask on ETH/BTC)
        # Leg 3: Sell ETH for USDT (receive bid on ETH/USDT)
        
        cw_product = self.calculate_cross_rate_product(
            book1, book2, book3, Direction.CLOCKWISE
        )
        
        ccw_product = self.calculate_cross_rate_product(
            book1, book2, book3, Direction.COUNTER_CLOCKWISE
        )
        
        # Determine which direction is profitable
        best_direction = None
        best_product = 1.0
        
        if cw_product > best_product:
            best_direction = Direction.CLOCKWISE
            best_product = cw_product
        
        if ccw_product > best_product:
            best_direction = Direction.COUNTER_CLOCKWISE
            best_product = ccw_product
        
        if best_direction is None:
            return None  # No opportunity
        
        # Calculate deviation from no-arb condition
        deviation_bps = (best_product - 1.0) * 10000
        
        # Build legs
        legs = self.build_legs(
            book1, book2, book3, best_direction, self.config.base_order_size_usd
        )
        
        # Calculate expected profit after fees
        expected_profit = self.calculate_net_profit(legs, self.config.base_order_size_usd)
        expected_profit_bps = expected_profit / self.config.base_order_size_usd * 10000
        
        # Check minimum profitability threshold
        if expected_profit_bps < self.config.min_profit_bps:
            return None  # Not profitable after costs
        
        return ArbitrageOpportunity(
            triangle=triangle,
            direction=best_direction,
            legs=legs,
            expected_profit=expected_profit,
            expected_profit_bps=expected_profit_bps,
            cross_rate_deviation=deviation_bps,
            timestamp=time.time()
        )
    
    def calculate_cross_rate_product(
        self,
        book1: OrderBook,
        book2: OrderBook, 
        book3: OrderBook,
        direction: Direction
    ) -> float:
        """
        Calculate the cross-rate product for a given direction.
        
        Uses bid prices when selling (receiving) and ask prices when buying (paying).
        
        The product represents: starting_amount * product = ending_amount
        If product > 1, profit exists in this direction.
        """
        if direction == Direction.CLOCKWISE:
            # Buy pair1 base (pay ask), sell pair2 (specific to triangle configuration)
            # This must be customized based on the specific triangle structure.
            # 
            # Generic formula for triangle A/B, B/C, A/C:
            # CW: Start with A, buy B (pay ask_A/B), buy C with B (pay ask_B/C),
            #     sell C for A (receive bid_A/C)
            # Product = (1/ask1) * (1/ask2) * bid3
            # (Assuming pair1=A/B, pair2=B/C, pair3=A/C and we're going A->B->C->A)
            
            product = (1.0 / book1.best_ask) * (1.0 / book2.best_ask) * book3.best_bid
            
        else:  # COUNTER_CLOCKWISE
            # Reverse direction: A -> C -> B -> A
            # Buy C with A (pay ask_A/C), sell C for B (receive bid_B/C),
            # sell B for A (receive bid_A/B)
            product = (1.0 / book3.best_ask) * book2.best_bid * book1.best_bid
        
        # Apply fee reduction
        fee1 = self.config.fee_rates.get(book1.pair, self.config.default_fee_rate)
        fee2 = self.config.fee_rates.get(book2.pair, self.config.default_fee_rate)
        fee3 = self.config.fee_rates.get(book3.pair, self.config.default_fee_rate)
        
        product *= (1 - fee1) * (1 - fee2) * (1 - fee3)
        
        return product
    
    def build_legs(
        self,
        book1: OrderBook,
        book2: OrderBook,
        book3: OrderBook,
        direction: Direction,
        order_size_usd: float
    ) -> List[TriangleLeg]:
        """Build the three trade legs for the arbitrage."""
        legs = []
        
        if direction == Direction.CLOCKWISE:
            # Leg 1: Buy base of pair1 (market buy)
            fee1 = self.config.fee_rates.get(book1.pair, self.config.default_fee_rate)
            qty1 = order_size_usd / book1.best_ask
            legs.append(TriangleLeg(
                pair=book1.pair, side="BUY",
                price=book1.best_ask, quantity=qty1, fee_rate=fee1
            ))
            
            # Leg 2: Buy base of pair2 with proceeds from leg 1
            fee2 = self.config.fee_rates.get(book2.pair, self.config.default_fee_rate)
            qty2 = qty1 * (1 - fee1) / book2.best_ask
            legs.append(TriangleLeg(
                pair=book2.pair, side="BUY",
                price=book2.best_ask, quantity=qty2, fee_rate=fee2
            ))
            
            # Leg 3: Sell base of pair3 to return to starting currency
            fee3 = self.config.fee_rates.get(book3.pair, self.config.default_fee_rate)
            qty3 = qty2 * (1 - fee2)
            legs.append(TriangleLeg(
                pair=book3.pair, side="SELL",
                price=book3.best_bid, quantity=qty3, fee_rate=fee3
            ))
        else:
            # Counter-clockwise legs (reversed)
            fee3 = self.config.fee_rates.get(book3.pair, self.config.default_fee_rate)
            qty3 = order_size_usd / book3.best_ask
            legs.append(TriangleLeg(
                pair=book3.pair, side="BUY",
                price=book3.best_ask, quantity=qty3, fee_rate=fee3
            ))
            
            fee2 = self.config.fee_rates.get(book2.pair, self.config.default_fee_rate)
            qty2 = qty3 * (1 - fee3) * book2.best_bid
            legs.append(TriangleLeg(
                pair=book2.pair, side="SELL",
                price=book2.best_bid, quantity=qty2, fee_rate=fee2
            ))
            
            fee1 = self.config.fee_rates.get(book1.pair, self.config.default_fee_rate)
            qty1 = qty2 * (1 - fee2) * book1.best_bid
            legs.append(TriangleLeg(
                pair=book1.pair, side="SELL",
                price=book1.best_bid, quantity=qty1, fee_rate=fee1
            ))
        
        return legs
    
    def calculate_net_profit(self, legs: List[TriangleLeg], initial_amount: float) -> float:
        """
        Calculate net profit after all fees and estimated slippage.
        
        P_net = (Q_initial * R1 * R2 * R3) - Q_initial - F_total - C_slippage
        """
        # Trace through the legs to get final amount
        amount = initial_amount
        total_fees = 0
        total_slippage_cost = 0
        
        for leg in legs:
            # Fee cost
            fee_cost = amount * leg.fee_rate
            total_fees += fee_cost
            amount -= fee_cost
            
            # Slippage estimation
            slippage_bps = self.estimate_slippage(leg)
            slippage_cost = amount * slippage_bps / 10000
            total_slippage_cost += slippage_cost
            amount -= slippage_cost
            
            # Price conversion
            if leg.side == "BUY":
                amount = amount / leg.price  # Convert to base currency
            else:
                amount = amount * leg.price  # Convert to quote currency
        
        # Net profit = final amount - initial amount
        net_profit = amount - initial_amount
        return net_profit
    
    def estimate_slippage(self, leg: TriangleLeg) -> float:
        """
        Estimate slippage in basis points based on order book depth.
        
        Uses a power-law model: slippage = alpha * (size/depth)^beta
        """
        book = self.order_books.get(leg.pair)
        if not book:
            return self.config.max_slippage_bps  # Conservative estimate
        
        # Calculate depth at best level (in USD)
        if leg.side == "BUY":
            depth = sum(level.quantity * level.price for level in book.asks[:5])
        else:
            depth = sum(level.quantity * level.price for level in book.bids[:5])
        
        order_size_usd = leg.quantity * leg.price
        
        if depth == 0:
            return self.config.max_slippage_bps
        
        # Power-law slippage model
        alpha = 1.0   # Calibrate from historical data
        beta = 0.8    # Calibrate from historical data
        slippage_bps = alpha * (order_size_usd / depth) ** beta
        
        return min(slippage_bps, self.config.max_slippage_bps)
    
    # ----------------------------------------------------------
    # PHASE 3: EXECUTION
    # ----------------------------------------------------------
    
    async def execute_opportunity(self, opp: ArbitrageOpportunity) -> Optional[ExecutionResult]:
        """
        Execute the arbitrage opportunity by submitting all three legs simultaneously.
        """
        start_time = time.time()
        
        # Final pre-execution checks
        if not self.risk_manager.approve_trade(opp):
            return None
        
        # Submit all three orders simultaneously
        try:
            order_tasks = []
            for leg in opp.legs:
                task = self.exchange.submit_order(
                    pair=leg.pair,
                    side=leg.side,
                    order_type=self.config.order_type,
                    price=leg.price,
                    quantity=leg.quantity
                )
                order_tasks.append(task)
            
            # Wait for all orders to complete
            results = await asyncio.gather(*order_tasks, return_exceptions=True)
            
            execution_time = (time.time() - start_time) * 1000  # ms
            
            # Check for execution timeout
            if execution_time > self.config.max_execution_time_ms:
                # Cancel any pending orders
                await self.cancel_pending_orders(results)
                return ExecutionResult(
                    opportunity=opp,
                    fills=[],
                    actual_profit=0,
                    execution_time_ms=execution_time,
                    success=False,
                    error_message=f"Execution timeout: {execution_time:.1f}ms"
                )
            
            # Process fills
            fills = []
            all_filled = True
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    all_filled = False
                    fills.append({
                        'leg': i, 'status': 'FAILED',
                        'error': str(result)
                    })
                elif result.get('status') == 'FILLED':
                    fills.append({
                        'leg': i, 'status': 'FILLED',
                        'fill_price': result['avg_price'],
                        'fill_qty': result['filled_qty'],
                        'fee': result['fee']
                    })
                else:
                    all_filled = False
                    fills.append({
                        'leg': i, 'status': result.get('status', 'UNKNOWN')
                    })
            
            # Handle partial execution
            if not all_filled:
                await self.handle_partial_execution(opp, fills)
                actual_profit = self.calculate_actual_profit(fills, opp)
                return ExecutionResult(
                    opportunity=opp, fills=fills,
                    actual_profit=actual_profit,
                    execution_time_ms=execution_time,
                    success=False,
                    error_message="Partial execution - unwind attempted"
                )
            
            # Calculate actual profit from fills
            actual_profit = self.calculate_actual_profit(fills, opp)
            
            return ExecutionResult(
                opportunity=opp, fills=fills,
                actual_profit=actual_profit,
                execution_time_ms=execution_time,
                success=True,
                error_message=None
            )
            
        except Exception as e:
            return ExecutionResult(
                opportunity=opp, fills=[],
                actual_profit=0,
                execution_time_ms=(time.time() - start_time) * 1000,
                success=False,
                error_message=str(e)
            )
    
    async def handle_partial_execution(self, opp: ArbitrageOpportunity, fills: List[dict]):
        """
        Handle the case where not all legs were filled.
        Attempt to unwind filled positions to minimize loss.
        """
        filled_legs = [f for f in fills if f['status'] == 'FILLED']
        
        if len(filled_legs) == 0:
            return  # Nothing to unwind
        
        # For each filled leg, submit a reverse order at market price
        for fill in filled_legs:
            leg_idx = fill['leg']
            original_leg = opp.legs[leg_idx]
            
            reverse_side = "SELL" if original_leg.side == "BUY" else "BUY"
            
            try:
                await self.exchange.submit_order(
                    pair=original_leg.pair,
                    side=reverse_side,
                    order_type="MARKET",
                    quantity=fill['fill_qty']
                )
            except Exception as e:
                # Log critical error - we have an unhedged position
                self.log_critical(
                    f"FAILED TO UNWIND LEG {leg_idx}: {e}. "
                    f"Manual intervention required."
                )
    
    def calculate_actual_profit(self, fills: List[dict], opp: ArbitrageOpportunity) -> float:
        """Calculate actual profit from execution fills."""
        total_cost = 0
        total_received = 0
        
        for fill in fills:
            if fill['status'] != 'FILLED':
                continue
            
            leg_idx = fill['leg']
            leg = opp.legs[leg_idx]
            
            notional = fill['fill_price'] * fill['fill_qty']
            fee = fill.get('fee', 0)
            
            if leg.side == "BUY":
                total_cost += notional + fee
            else:
                total_received += notional - fee
        
        return total_received - total_cost
    
    # ----------------------------------------------------------
    # PHASE 4: P&L TRACKING AND RISK MANAGEMENT
    # ----------------------------------------------------------
    
    def process_result(self, result: ExecutionResult):
        """Process execution result: update P&L, risk state, logs."""
        # Update P&L
        self.daily_pnl += result.actual_profit
        self.daily_trades += 1
        self.trade_history.append(result)
        
        # Update consecutive loss counter
        if result.actual_profit < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # Log
        if self.config.log_executions:
            self.log_execution(result)
    
    def check_circuit_breakers(self) -> bool:
        """Check if any circuit breaker conditions are met."""
        # Daily loss limit
        if self.daily_pnl < -self.config.max_daily_loss_usd:
            self.log_warning(f"Daily loss limit reached: ${self.daily_pnl:.2f}")
            return True
        
        # Consecutive losses
        if self.consecutive_losses >= self.config.max_consecutive_losses:
            self.log_warning(
                f"Consecutive loss limit: {self.consecutive_losses} losses"
            )
            return True
        
        # Daily trade limit
        if self.daily_trades >= self.config.max_daily_trades:
            self.log_warning(f"Daily trade limit reached: {self.daily_trades}")
            return True
        
        return False
    
    # ----------------------------------------------------------
    # LOGGING
    # ----------------------------------------------------------
    
    def log_execution(self, result: ExecutionResult):
        """Log execution details."""
        opp = result.opportunity
        print(
            f"[EXECUTION] Triangle={opp.triangle} "
            f"Direction={opp.direction.value} "
            f"Expected={opp.expected_profit_bps:.2f}bps "
            f"Actual={result.actual_profit:.4f} "
            f"Time={result.execution_time_ms:.1f}ms "
            f"Success={result.success}"
        )
    
    def log_warning(self, msg: str):
        print(f"[WARNING] {msg}")
    
    def log_critical(self, msg: str):
        print(f"[CRITICAL] {msg}")
```

### 8.2 Optimized Triangle Scanner

```python
class TriangleScanner:
    """
    Efficiently scans all possible triangles from available pairs.
    Pre-computes triangle relationships for fast lookup.
    """
    
    def __init__(self, pairs: List[str]):
        """
        Args:
            pairs: List of available trading pairs (e.g., ["BTC/USDT", "ETH/USDT", "ETH/BTC"])
        """
        self.pairs = pairs
        self.triangles = self.discover_triangles()
        
    def discover_triangles(self) -> List[Tuple[str, str, str]]:
        """
        Automatically discover all valid triangles from available pairs.
        
        A valid triangle consists of three pairs (A/B, B/C, A/C) such that
        all three currencies form a closed loop.
        """
        # Parse pairs into (base, quote) tuples
        pair_map = {}
        currencies = set()
        for pair in self.pairs:
            base, quote = pair.split('/')
            pair_map[(base, quote)] = pair
            currencies.add(base)
            currencies.add(quote)
        
        triangles = []
        currency_list = list(currencies)
        
        # Check all combinations of 3 currencies
        for i in range(len(currency_list)):
            for j in range(i + 1, len(currency_list)):
                for k in range(j + 1, len(currency_list)):
                    a, b, c = currency_list[i], currency_list[j], currency_list[k]
                    
                    # Check if all three pairs exist (in either direction)
                    ab = pair_map.get((a, b)) or pair_map.get((b, a))
                    bc = pair_map.get((b, c)) or pair_map.get((c, b))
                    ac = pair_map.get((a, c)) or pair_map.get((c, a))
                    
                    if ab and bc and ac:
                        triangles.append((ab, bc, ac))
        
        return triangles
    
    def get_triangles_for_currency(self, currency: str) -> List[Tuple[str, str, str]]:
        """Get all triangles that include a specific currency."""
        return [t for t in self.triangles if currency in str(t)]
```

---

## 9. Worked Examples with Real Numbers

### 9.1 Example 1: Crypto Triangular Arbitrage (BTC/USDT, ETH/USDT, ETH/BTC)

**Market Data (snapshot):**

| Pair | Best Bid | Best Ask | Spread (bps) |
|------|:--------:|:--------:|:------------:|
| BTC/USDT | 65,000.00 | 65,010.00 | 0.15 |
| ETH/USDT | 3,200.00 | 3,201.00 | 0.31 |
| ETH/BTC | 0.049200 | 0.049250 | 1.02 |

**Fee Rate:** 0.10% (taker) per leg on Binance standard tier.

**Step 1: Check Clockwise Direction (USDT -> BTC -> ETH -> USDT)**

```
Leg 1: Buy BTC with 10,000 USDT
  - Pay ask: 65,010.00 USDT/BTC
  - Get: 10,000 / 65,010 = 0.153822 BTC
  - After fee (0.10%): 0.153822 * 0.999 = 0.153668 BTC

Leg 2: Buy ETH with BTC (sell BTC for ETH)
  - Implied: sell BTC, buy ETH using ETH/BTC pair
  - We sell BTC: receive bid price of ETH/BTC = 0.049200
  - Wait: ETH/BTC bid = 0.049200 means 1 ETH = 0.049200 BTC
  - So selling 0.153668 BTC gets: 0.153668 / 0.049200 = 3.12333 ETH
  - After fee (0.10%): 3.12333 * 0.999 = 3.12021 ETH

Leg 3: Sell ETH for USDT
  - Receive bid: 3,200.00 USDT/ETH
  - Get: 3.12021 * 3,200.00 = 9,984.67 USDT
  - After fee (0.10%): 9,984.67 * 0.999 = 9,974.69 USDT
```

**Result (Clockwise):**
- Started: 10,000.00 USDT
- Ended: 9,974.69 USDT
- **Loss: -25.31 USDT (-25.31 bps)**

**Step 2: Check Counter-Clockwise Direction (USDT -> ETH -> BTC -> USDT)**

```
Leg 1: Buy ETH with 10,000 USDT
  - Pay ask: 3,201.00 USDT/ETH
  - Get: 10,000 / 3,201 = 3.12402 ETH
  - After fee (0.10%): 3.12402 * 0.999 = 3.12090 ETH

Leg 2: Buy BTC with ETH (sell ETH for BTC)
  - Sell ETH at ETH/BTC ask... wait, we're selling ETH for BTC.
  - ETH/BTC bid = 0.049200 means we get 0.049200 BTC per ETH sold
  - Hmm, actually: if we SELL ETH on ETH/BTC pair, we receive bid price
  - Get: 3.12090 * 0.049200 = 0.15355 BTC
  - After fee (0.10%): 0.15355 * 0.999 = 0.15339 BTC

Leg 3: Sell BTC for USDT
  - Receive bid: 65,000.00 USDT/BTC
  - Get: 0.15339 * 65,000 = 9,970.35 USDT
  - After fee (0.10%): 9,970.35 * 0.999 = 9,960.38 USDT
```

**Result (Counter-Clockwise):**
- Started: 10,000.00 USDT
- Ended: 9,960.38 USDT
- **Loss: -39.62 USDT (-39.62 bps)**

**Conclusion:** No profitable opportunity exists in this snapshot. The combined fees (30 bps) exceed the cross-rate deviation.

---

### 9.2 Example 2: Profitable Crypto Arbitrage (with mispricing)

**Market Data (hypothetical mispricing):**

| Pair | Best Bid | Best Ask | Spread (bps) |
|------|:--------:|:--------:|:------------:|
| BTC/USDT | 65,000.00 | 65,010.00 | 0.15 |
| ETH/USDT | 3,200.00 | 3,201.00 | 0.31 |
| ETH/BTC | 0.049450 | 0.049500 | 1.01 |

Note: ETH/BTC is slightly overpriced compared to the implied rate from ETH/USDT and BTC/USDT.

**Implied ETH/BTC from the other two pairs:**

$$\hat{R}_{ETH/BTC} = \frac{ETH/USDT_{mid}}{BTC/USDT_{mid}} = \frac{3200.50}{65005.00} = 0.049228$$

**Actual ETH/BTC mid:** 0.049475

**Deviation:** $(0.049475 - 0.049228) / 0.049228 = 0.00502 = 50.2$ bps

**Fee Rate:** 0.02% (VIP tier) per leg.

**Counter-Clockwise: USDT -> ETH -> BTC -> USDT**

Wait, let us check: ETH/BTC is overpriced, so we want to sell ETH/BTC (sell ETH for BTC at the inflated price).

**Clockwise: USDT -> BTC -> ETH -> USDT**

Actually, let's think carefully:
- ETH/BTC bid = 0.049450 is higher than implied (0.049228)
- So selling ETH for BTC (receiving ETH/BTC bid) gives us more BTC than fair value
- Path: USDT -> ETH (buy at fair) -> BTC (sell ETH/BTC at premium) -> USDT (sell BTC)

```
Start: 100,000 USDT

Leg 1: Buy ETH with USDT
  - Pay ask: 3,201.00
  - Get: 100,000 / 3,201 = 31.2402 ETH
  - Fee (0.02%): 31.2402 * 0.9998 = 31.2340 ETH

Leg 2: Sell ETH for BTC (on ETH/BTC pair at premium bid)
  - ETH/BTC bid: 0.049450
  - Get: 31.2340 * 0.049450 = 1.54452 BTC
  - Fee (0.02%): 1.54452 * 0.9998 = 1.54421 BTC

Leg 3: Sell BTC for USDT
  - BTC/USDT bid: 65,000.00
  - Get: 1.54421 * 65,000 = 100,373.65 USDT
  - Fee (0.02%): 100,373.65 * 0.9998 = 100,353.58 USDT
```

**Result:**
- Started: 100,000.00 USDT
- Ended: 100,353.58 USDT
- **Profit: +353.58 USDT (+35.36 bps)**
- Gross deviation: 50.2 bps
- Total fees: 3 * 2 = 6 bps
- Slippage estimate: ~5 bps (for $100K order)
- **Net after estimated slippage: ~24 bps = ~$240**

### 9.3 Example 3: Forex Triangular Arbitrage (EUR/USD, GBP/USD, EUR/GBP)

**Market Data:**

| Pair | Best Bid | Best Ask |
|------|:--------:|:--------:|
| EUR/USD | 1.08500 | 1.08510 |
| GBP/USD | 1.26200 | 1.26215 |
| EUR/GBP | 0.85960 | 0.85975 |

**Implied EUR/GBP:**

$$\hat{R}_{EUR/GBP} = \frac{EUR/USD_{mid}}{GBP/USD_{mid}} = \frac{1.08505}{1.26208} = 0.85974$$

**Market EUR/GBP mid:** 0.85968

**Deviation:** $(0.85974 - 0.85968) / 0.85968 = 0.07$ bps

At 0.07 bps deviation with Forex spreads of ~0.5-1 bps, this is **not profitable**. This illustrates why Forex triangular arbitrage requires institutional-grade infrastructure and near-zero fees.

---

## 10. Risk Parameters and Position Sizing

### 10.1 Position Sizing Model

**Base position size** is determined by:

$$Q_{base} = \min\left(Q_{max}, \frac{C_{available} \times f_{util}}{N_{triangles}}\right)$$

Where:
- $Q_{max}$ = maximum order size per trade
- $C_{available}$ = available capital
- $f_{util}$ = target capital utilization ratio (e.g., 0.5)
- $N_{triangles}$ = number of monitored triangles

**Adaptive position sizing** based on opportunity quality:

$$Q_{trade} = Q_{base} \times \min\left(1, \frac{\delta_{observed} - \delta_{min}}{\delta_{scale}}\right)$$

Where:
- $\delta_{observed}$ = observed cross-rate deviation (bps)
- $\delta_{min}$ = minimum profitable deviation (bps)
- $\delta_{scale}$ = scaling parameter (e.g., 20 bps)

This sizes up for larger opportunities and sizes down for marginal ones.

### 10.2 Maximum Position Relative to Order Book

**Critical constraint:** Never size an order larger than a fraction of available liquidity:

$$Q_{trade} \leq \alpha \times D_{min}$$

Where:
- $D_{min}$ = minimum depth across all three legs (in USD at best 5 levels)
- $\alpha$ = depth utilization ratio (e.g., 0.10 to 0.25)

Using more than 25% of visible depth at the best levels virtually guarantees significant slippage.

### 10.3 Risk Parameter Configuration

```python
TRIANGULAR_ARB_RISK_PARAMS = {
    # Position sizing
    "base_order_usd": 10_000,
    "max_order_usd": 50_000,
    "depth_utilization_ratio": 0.15,      # Max 15% of visible depth
    "capital_utilization_ratio": 0.50,    # Use max 50% of capital
    
    # Profitability
    "min_gross_deviation_bps": 5,         # Minimum before cost check
    "min_net_profit_bps": 3,              # After all costs
    "safety_margin_bps": 1,              # Extra buffer
    
    # Execution
    "max_execution_time_ms": 500,
    "order_book_max_age_ms": 100,
    "use_ioc_orders": True,               # Immediate-or-Cancel
    
    # Stop losses / Circuit breakers
    "max_loss_per_trade_usd": 100,
    "max_daily_loss_usd": 1_000,
    "max_drawdown_pct": 0.03,            # 3% max drawdown
    "max_consecutive_losses": 5,
    "cool_down_after_loss_sec": 60,       # Wait 60s after a loss
    
    # Exchange limits
    "max_capital_per_exchange_pct": 0.40,
    "min_exchange_balance_usd": 5_000,    # Keep minimum balance
    
    # Monitoring
    "alert_on_partial_fill": True,
    "alert_on_unwind": True,
    "log_all_opportunities": True,
}
```

---

## 11. Backtesting Framework

### 11.1 Data Requirements

For accurate backtesting of triangular arbitrage, you need:

1. **Full order book snapshots** at high frequency (minimum 100ms intervals)
2. **Trade data** (tick data) for all three pairs
3. **Fee schedules** (historical, as they may change)
4. **Latency measurements** (historical API response times)

Note: Using only OHLCV data is **insufficient** for triangular arbitrage backtesting because:
- It does not capture bid-ask spreads
- It does not capture order book depth
- It does not capture intra-bar price dynamics

### 11.2 Backtesting Pseudocode

```python
class TriangularArbBacktester:
    """
    Backtester for triangular arbitrage strategies.
    Uses historical order book snapshots.
    """
    
    def __init__(self, config: TriangularArbConfig):
        self.config = config
        self.results = []
    
    def run(self, historical_books: dict):
        """
        Run backtest on historical order book data.
        
        Args:
            historical_books: {timestamp: {pair: OrderBook}}
        """
        timestamps = sorted(historical_books.keys())
        
        for ts in timestamps:
            books = historical_books[ts]
            
            for triangle in self.config.triangles:
                if not all(p in books for p in triangle):
                    continue
                
                # Detect opportunity
                opp = self.detect_opportunity(
                    books[triangle[0]],
                    books[triangle[1]],
                    books[triangle[2]],
                    triangle
                )
                
                if opp and opp.expected_profit_bps > self.config.min_profit_bps:
                    # Simulate execution with realistic latency
                    fill_ts = ts + self.config.simulated_latency_ms / 1000
                    
                    # Get order books at fill time (if available)
                    fill_books = self.get_books_at_time(
                        historical_books, fill_ts, triangle
                    )
                    
                    if fill_books:
                        # Simulate fills with slippage
                        result = self.simulate_execution(opp, fill_books)
                        self.results.append(result)
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate backtest performance report."""
        if not self.results:
            return {"message": "No trades executed"}
        
        profits = [r.actual_profit for r in self.results]
        
        return {
            "total_trades": len(self.results),
            "profitable_trades": sum(1 for p in profits if p > 0),
            "win_rate": sum(1 for p in profits if p > 0) / len(profits),
            "total_pnl": sum(profits),
            "avg_profit_per_trade": sum(profits) / len(profits),
            "max_profit": max(profits),
            "max_loss": min(profits),
            "sharpe_ratio": self.calculate_sharpe(profits),
            "max_drawdown": self.calculate_max_drawdown(profits),
        }
```

---

## 12. Production Deployment Considerations

### 12.1 Exchange API Best Practices

1. **Rate Limiting:** Implement client-side rate limiting to avoid IP bans
   - Binance: 1200 requests/minute (order endpoints)
   - Coinbase: 30 requests/second
   - OKX: 60 requests/2 seconds

2. **WebSocket Management:**
   - Implement automatic reconnection with exponential backoff
   - Monitor heartbeat/ping-pong to detect stale connections
   - Maintain sequence numbers to detect missed messages

3. **Order Management:**
   - Use IOC (Immediate-or-Cancel) orders to avoid hanging limit orders
   - Implement order tracking with unique client order IDs
   - Handle all possible order states (NEW, PARTIALLY_FILLED, FILLED, CANCELED, REJECTED, EXPIRED)

### 12.2 Monitoring Dashboard Metrics

```
Real-Time Metrics:
├── Opportunity Detection Rate (per minute)
├── Execution Success Rate (%)
├── Average Execution Time (ms)
├── P&L (running, daily, weekly, monthly)
├── Slippage vs Expected (bps)
├── Fill Rate by Pair (%)
├── API Latency by Exchange (ms)
├── Order Book Freshness (ms)
├── Capital Utilization (%)
└── Circuit Breaker Status
```

### 12.3 Failure Modes and Recovery

| Failure Mode | Detection | Recovery Action |
|-------------|-----------|-----------------|
| WebSocket disconnect | Heartbeat timeout | Auto-reconnect, rebuild local book |
| API rate limit exceeded | HTTP 429 response | Exponential backoff, reduce frequency |
| Partial fill | Order status != FILLED | Immediate unwind of filled legs |
| Exchange maintenance | HTTP 503 / announcement | Pause trading, alert operator |
| Stale order book | Timestamp check | Skip opportunity, log warning |
| Negative P&L streak | Consecutive loss counter | Circuit breaker, alert operator |
| Balance insufficient | Order rejected | Rebalance or pause pair |

---

## 13. References

### Academic Papers

1. **Aiba, Y., Hatano, N., Takayasu, H., Marumo, K., & Shimizu, T.** (2002). "Triangular Arbitrage as an Interaction Among Foreign Exchange Rates." *Physica A*, 310(3-4), 467-479.

2. **Fenn, D. J., Howison, S. D., McDonald, M., Williams, S., & Johnson, N. F.** (2009). "The Mirage of Triangular Arbitrage in the Spot Foreign Exchange Market." *International Journal of Theoretical and Applied Finance*, 12(8), 1105-1123.

3. **Ito, T., Yamada, K., Takayasu, M., & Takayasu, H.** (2012). "Free Lunch! Arbitrage Opportunities in the Foreign Exchange Markets." *NBER Working Paper No. 18541*.

4. **Kozhan, R., & Tham, W. W.** (2012). "Execution Risk in High-Frequency Arbitrage." *Management Science*, 58(11), 2131-2149.

5. **Makarov, I., & Schoar, A.** (2020). "Trading and Arbitrage in Cryptocurrency Markets." *Journal of Financial Economics*, 135(2), 293-319.

6. **Shleifer, A., & Vishny, R. W.** (1997). "The Limits of Arbitrage." *The Journal of Finance*, 52(1), 35-55.

### Exchange Documentation

- Binance Spot Trading Rules: https://www.binance.com/en/trade-rule
- Binance API (Order Book Streams): https://binance-docs.github.io/apidocs/spot/en/#diff-depth-stream
- Coinbase WebSocket Feed: https://docs.cloud.coinbase.com/exchange/docs/websocket-overview
- OKX WebSocket Public Channel: https://www.okx.com/docs-v5/en/#order-book-trading-market-data-ws-order-book-channel

### Technical Resources

- CCXT Unified API: https://docs.ccxt.com/
- Python asyncio documentation: https://docs.python.org/3/library/asyncio.html
- FIX Protocol (for institutional Forex): https://www.fixtrading.org/

---

> **Related Documents:**
> - [00_overview.md](./00_overview.md) — Arbitrage Overview
> - [03_cross_exchange_arbitrage.md](./03_cross_exchange_arbitrage.md) — Cross-Exchange Arbitrage (extends concepts here)
> - [04_mev_defi_arbitrage.md](./04_mev_defi_arbitrage.md) — DEX Triangular Arbitrage using Flash Loans
