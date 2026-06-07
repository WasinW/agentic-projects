# Cross-Exchange Arbitrage — Complete Strategy Documentation

> **Document Version:** 2.0
> **Last Updated:** 2026-04-12
> **Classification:** Core Knowledge Base — Axis 2: Financial Products
> **Strategy Type:** Pure/Near Arbitrage (execution-dependent risk)
> **Markets:** Crypto (CeFi), Forex (ECN-to-ECN)
> **Frequency:** Medium-High Frequency (seconds to minutes)

---

## Table of Contents

1. [Core Logic — Price Discrepancy Detection](#1-core-logic--price-discrepancy-detection)
2. [Transfer Time Considerations](#2-transfer-time-considerations)
3. [Pre-Positioning Strategy](#3-pre-positioning-strategy)
4. [Latency Arbitrage](#4-latency-arbitrage)
5. [Fee Comparison Framework](#5-fee-comparison-framework)
6. [Mathematical Model — Minimum Profitable Spread](#6-mathematical-model--minimum-profitable-spread)
7. [Integration with Exchange APIs](#7-integration-with-exchange-apis)
8. [Complete Execution Algorithm](#8-complete-execution-algorithm)
9. [Risk Management](#9-risk-management)
10. [Performance Analytics](#10-performance-analytics)
11. [Production Deployment](#11-production-deployment)
12. [References](#12-references)

---

## 1. Core Logic — Price Discrepancy Detection

### 1.1 Fundamental Concept

Cross-exchange arbitrage exploits price differences for the same asset across different trading venues. When an asset trades at $P_A$ on Exchange A and $P_B$ on Exchange B, and $P_B > P_A + Costs$, an arbitrageur can buy on A and sell on B for a risk-free profit.

### 1.2 Why Price Discrepancies Exist

Price discrepancies between exchanges arise due to:

1. **Fragmented liquidity:** Each exchange has its own order book with independent price discovery
2. **Different user bases:** Regional exchanges may have different demand/supply dynamics
3. **Withdrawal/deposit delays:** Friction in moving assets between venues creates temporal gaps
4. **Fee structures:** Different fee tiers affect effective trading prices
5. **Fiat on/off ramps:** Different fiat currency access points create price premiums (e.g., "Kimchi premium" in South Korea)
6. **API latency:** Different exchanges process and publish prices at different speeds
7. **Market maker differences:** Different market makers provide different bid/ask quotes
8. **Regulatory differences:** Compliance requirements create access barriers

### 1.3 Types of Cross-Exchange Arbitrage

```
Cross-Exchange Arbitrage
├── Simple Transfer Arbitrage
│   └── Buy on A, transfer to B, sell on B
│   └── Slow, risky (price may change during transfer)
│
├── Pre-Positioned Arbitrage (Recommended)
│   └── Maintain balances on both exchanges
│   └── Buy on A, simultaneously sell on B
│   └── Periodically rebalance between exchanges
│
├── Latency Arbitrage
│   └── Exploit speed differences between exchange price updates
│   └── Stale quote arbitrage
│
├── Cross-Venue (CEX-DEX) Arbitrage
│   └── Price difference between centralized and decentralized exchanges
│   └── Must account for gas fees and block time
│
└── Regional Premium Arbitrage
    └── Exploit price premiums in specific regions
    └── Requires fiat currency access in multiple jurisdictions
```

### 1.4 Step-by-Step Logic

**Pre-Positioned Cross-Exchange Arbitrage:**

```
Prerequisites:
- Maintain balance of Asset X and USDT on both Exchange A and Exchange B
- Continuously monitor prices on both exchanges

Step 1: Detect price discrepancy
  - Exchange A: BTC ask = $65,000
  - Exchange B: BTC bid = $65,200
  - Raw spread = $200 (30.8 bps)

Step 2: Calculate net profit after all costs
  - Fee on A (buy): $65,000 * 0.001 = $65
  - Fee on B (sell): $65,200 * 0.001 = $65.20
  - Estimated slippage: $20 (combined)
  - Total costs: $150.20
  - Net profit: $200 - $150.20 = $49.80 (7.6 bps)

Step 3: Verify profitability threshold
  - $49.80 > minimum threshold ($30) → PROCEED

Step 4: Execute simultaneously
  - Buy 1 BTC on Exchange A at market/limit
  - Sell 1 BTC on Exchange B at market/limit

Step 5: Result
  - Exchange A: -$65,000 USDT, +1 BTC
  - Exchange B: +$65,200 USDT, -1 BTC
  - Net: +$200 USDT (before fees), ~$50 net profit

Step 6: Rebalance (periodic)
  - If imbalanced: transfer assets between exchanges
  - Or: wait for reverse arbitrage opportunity
```

### 1.5 Spread Monitoring Model

**Real-time spread calculation:**

$$\text{Spread}_{A \to B} = \frac{Bid_B - Ask_A}{Ask_A}$$

$$\text{Spread}_{B \to A} = \frac{Bid_A - Ask_B}{Ask_B}$$

**Effective spread (accounting for depth):**

For order size $Q$:

$$\text{Effective Ask}_A = \frac{\sum_{i=1}^{n} P_i^{ask} \times Q_i^{ask}}{\sum_{i=1}^{n} Q_i^{ask}} \quad \text{where} \quad \sum Q_i^{ask} \geq Q$$

$$\text{Effective Bid}_B = \frac{\sum_{i=1}^{n} P_i^{bid} \times Q_i^{bid}}{\sum_{i=1}^{n} Q_i^{bid}} \quad \text{where} \quad \sum Q_i^{bid} \geq Q$$

This accounts for consuming multiple order book levels.

---

## 2. Transfer Time Considerations

### 2.1 Blockchain Confirmation Times

| Asset/Network | Average Block Time | Required Confirmations | Total Time |
|--------------|:------------------:|:---------------------:|:----------:|
| BTC (Bitcoin) | ~10 min | 2-6 | 20-60 min |
| ETH (Ethereum L1) | ~12 sec | 12-35 | 2.5-7 min |
| USDT (Ethereum ERC-20) | ~12 sec | 12-35 | 2.5-7 min |
| USDT (Tron TRC-20) | ~3 sec | 20 | ~1 min |
| SOL (Solana) | ~0.4 sec | 30+ | ~15 sec |
| MATIC (Polygon) | ~2 sec | 60-100 | 2-3 min |
| USDT (Arbitrum) | ~0.25 sec | 1 (+ L1 confirmation) | ~10 min |
| XRP (Ripple) | ~4 sec | 1 | ~5 sec |
| LTC (Litecoin) | ~2.5 min | 6 | ~15 min |

### 2.2 Exchange Processing Time

Beyond blockchain confirmations, exchanges add processing delays:

| Exchange | Deposit Credit Time | Withdrawal Processing |
|----------|:-------------------:|:---------------------:|
| Binance | Near-instant after confirms | 0-30 min |
| Coinbase | Near-instant after confirms | Instant-10 min |
| OKX | Near-instant after confirms | 0-60 min |
| Kraken | 5-30 min after confirms | 0-60 min |
| Bybit | Near-instant after confirms | 0-30 min |

### 2.3 Impact on Arbitrage Strategy

**Simple Transfer Arbitrage (Not Recommended for most cases):**

$$\text{Price Risk} = \sigma_{1min} \times \sqrt{T_{transfer}}$$

Where:
- $\sigma_{1min}$ = 1-minute price volatility
- $T_{transfer}$ = transfer time in minutes

**Example:** BTC 1-min volatility = 0.05%, transfer time = 30 minutes:

$$\text{Price Risk} = 0.0005 \times \sqrt{30} = 0.0027 = 27 \text{ bps}$$

This means you need a spread of at least 27 bps just to cover the expected price movement during transfer — making simple transfers viable only for very large, persistent spreads (like the Kimchi premium that reached 5-50%+).

### 2.4 Optimal Network Selection for Transfers

When rebalancing is needed, choose the network that minimizes:

$$\text{Total Cost} = \text{Network Fee} + \text{Time Risk} \times \text{Position Value}$$

**Decision matrix:**

```python
def select_optimal_network(asset, amount, urgency):
    """
    Select the cheapest/fastest network for cross-exchange transfer.
    
    Returns: (network, estimated_time, estimated_cost)
    """
    networks = get_available_networks(asset)
    
    best = None
    for network in networks:
        fee = get_network_fee(asset, network)
        time_minutes = get_expected_time(network)
        time_risk = calculate_time_risk(asset, time_minutes, amount)
        
        total_cost = fee + time_risk
        
        if urgency == "HIGH":
            # Prioritize speed
            score = time_minutes * 10 + total_cost
        else:
            # Prioritize cost
            score = total_cost + time_minutes * 0.1
        
        if best is None or score < best['score']:
            best = {
                'network': network,
                'fee': fee,
                'time': time_minutes,
                'total_cost': total_cost,
                'score': score
            }
    
    return best
```

---

## 3. Pre-Positioning Strategy

### 3.1 Concept

Pre-positioning eliminates transfer delay risk by maintaining balances on multiple exchanges simultaneously. Instead of transferring assets after detecting an opportunity, you execute trades on both exchanges instantly using existing balances.

### 3.2 Capital Requirements

For $N$ exchanges, each with target balance:

$$C_{total} = \sum_{i=1}^{N} (B_i^{base} \times P + B_i^{quote})$$

Where:
- $B_i^{base}$ = target base asset balance on exchange $i$
- $B_i^{quote}$ = target quote asset balance on exchange $i$
- $P$ = current asset price

**Example:** 2 exchanges, $50K base + $50K quote each:

$$C_{total} = 2 \times (\$50,000 + \$50,000) = \$200,000$$

### 3.3 Balance Rebalancing

Over time, successful arbitrage creates imbalances:
- Exchange where you buy accumulates the base asset
- Exchange where you sell accumulates the quote asset

**Rebalancing triggers:**

$$\text{Imbalance Ratio} = \frac{|B_i^{actual} - B_i^{target}|}{B_i^{target}}$$

Rebalance when $\text{Imbalance Ratio} > \text{threshold}$ (e.g., 30%).

**Rebalancing methods:**

1. **Wait for reverse opportunity:** Eventually the price discrepancy may reverse, naturally rebalancing
2. **Manual transfer:** Transfer assets between exchanges (incurs transfer fees and time)
3. **Internal transfer:** Some exchanges support instant internal transfers between accounts
4. **Stablecoin transfer:** Sell base to stablecoin on one exchange, transfer stablecoin, buy base on the other

### 3.4 Inventory Management Algorithm

```python
class InventoryManager:
    """
    Manages pre-positioned balances across multiple exchanges.
    Ensures sufficient liquidity for arbitrage execution.
    """
    
    def __init__(self, exchanges: List[str], target_balances: dict):
        """
        Args:
            exchanges: List of exchange identifiers
            target_balances: {exchange: {asset: target_amount}}
        """
        self.exchanges = exchanges
        self.targets = target_balances
        self.actual = {}  # Will be populated from exchange APIs
    
    def check_rebalance_needed(self) -> List[dict]:
        """
        Check if any exchange needs rebalancing.
        Returns list of rebalance actions needed.
        """
        actions = []
        
        for exchange in self.exchanges:
            for asset, target in self.targets[exchange].items():
                actual = self.actual.get(exchange, {}).get(asset, 0)
                imbalance = (actual - target) / target if target > 0 else 0
                
                if abs(imbalance) > 0.30:  # 30% threshold
                    # Determine if we need to add or remove
                    deficit = target - actual
                    
                    # Find exchange with surplus
                    surplus_exchange = self.find_surplus(asset, exchange)
                    
                    if surplus_exchange:
                        actions.append({
                            'asset': asset,
                            'from_exchange': surplus_exchange,
                            'to_exchange': exchange,
                            'amount': abs(deficit),
                            'urgency': 'HIGH' if abs(imbalance) > 0.50 else 'LOW'
                        })
        
        return actions
    
    def find_surplus(self, asset: str, deficit_exchange: str) -> Optional[str]:
        """Find an exchange with surplus of the given asset."""
        for exchange in self.exchanges:
            if exchange == deficit_exchange:
                continue
            actual = self.actual.get(exchange, {}).get(asset, 0)
            target = self.targets[exchange].get(asset, 0)
            if actual > target * 1.10:  # Has > 10% surplus
                return exchange
        return None
    
    def can_execute_arb(self, buy_exchange: str, sell_exchange: str, 
                         asset: str, quantity: float) -> bool:
        """Check if we have sufficient balance to execute arbitrage."""
        # Need quote currency on buy exchange
        quote_balance = self.actual.get(buy_exchange, {}).get('USDT', 0)
        # Need base asset on sell exchange
        base_balance = self.actual.get(sell_exchange, {}).get(asset, 0)
        
        # Check with safety margin (keep 10% buffer)
        price = self.get_price(asset)
        required_quote = quantity * price * 1.10  # 10% buffer for slippage
        required_base = quantity * 1.10
        
        return quote_balance >= required_quote and base_balance >= required_base
```

### 3.5 Optimal Capital Split

Given historical spread data, the optimal capital split between exchanges can be determined:

$$w_i^* = \frac{E[\text{profit from exchange } i]}{\sum_j E[\text{profit from exchange } j]}$$

In practice, a simpler approach:
- Equal split (50/50 for 2 exchanges)
- Adjusted for historical opportunity frequency per exchange

---

## 4. Latency Arbitrage

### 4.1 Concept

Latency arbitrage exploits the fact that different exchanges update their prices at different speeds. A faster exchange may reflect new information before a slower exchange adjusts its quotes.

### 4.2 How It Works

```
Time T0: Market event occurs (e.g., large buy on Exchange A)
Time T1: Exchange A updates price to $65,100 (fast)
Time T2: Exchange B still shows old price $65,000 (slow)
Time T3: Arbitrageur buys on B at $65,000, sells on A at $65,100

Gap: T2 - T1 = latency advantage window
Duration: Typically milliseconds to seconds
```

### 4.3 Latency Sources

| Source | Typical Latency | Notes |
|--------|:--------------:|-------|
| Exchange matching engine | 0.1-10 ms | Varies by exchange architecture |
| WebSocket propagation | 1-50 ms | Depends on server location |
| Network path (same region) | 1-5 ms | AWS us-east to exchange |
| Network path (cross-region) | 50-200 ms | US to Asia |
| REST API polling | 100-1000 ms | Not suitable for latency arb |
| Data processing | 0.1-5 ms | Parsing, calculation |
| Order submission | 5-50 ms | Exchange-dependent |

### 4.4 Latency Measurement

```python
class LatencyTracker:
    """
    Measures and tracks latency between exchanges.
    Identifies exploitable speed advantages.
    """
    
    def __init__(self, exchanges: List[str]):
        self.exchanges = exchanges
        self.latency_history = {}  # {(fast, slow): [latency_ms]}
    
    async def measure_relative_latency(self, event_price: float):
        """
        When a significant price move occurs, measure which
        exchange reflects it first.
        """
        timestamps = {}
        
        # Subscribe to both exchanges, record when each reflects the move
        # This requires continuous monitoring of price feeds
        
        for exchange in self.exchanges:
            ts = await self.get_price_update_timestamp(exchange, event_price)
            timestamps[exchange] = ts
        
        # Calculate relative latencies
        sorted_exchanges = sorted(timestamps.items(), key=lambda x: x[1])
        fastest = sorted_exchanges[0]
        
        for exchange, ts in sorted_exchanges[1:]:
            latency_ms = (ts - fastest[1]) * 1000
            pair = (fastest[0], exchange)
            self.latency_history.setdefault(pair, []).append(latency_ms)
    
    def get_average_advantage(self, fast_exchange: str, slow_exchange: str) -> float:
        """Get average latency advantage in milliseconds."""
        pair = (fast_exchange, slow_exchange)
        history = self.latency_history.get(pair, [])
        return sum(history) / len(history) if history else 0
```

### 4.5 Latency Arbitrage Requirements

- **Infrastructure:** Co-located or very low-latency connections to both exchanges
- **Speed:** Must detect stale quotes and execute within milliseconds
- **Capital:** High capital efficiency (many small, fast trades)
- **Risk:** Very low per-trade risk but requires consistent execution
- **Competition:** Extremely competitive (other HFT firms also doing this)

---

## 5. Fee Comparison Framework

### 5.1 Complete Fee Model

For cross-exchange arbitrage, the total cost per round-trip trade includes:

$$C_{total} = C_{buy} + C_{sell} + C_{transfer} + C_{slippage}$$

**Buy-side cost:**

$$C_{buy} = Q \times P_A \times f_A^{taker}$$

**Sell-side cost:**

$$C_{sell} = Q \times P_B \times f_B^{taker}$$

**Transfer cost (for rebalancing):**

$$C_{transfer} = \frac{F_{network}}{N_{trades}}$$

Where $N_{trades}$ is the expected number of trades before the next rebalance.

**Slippage cost:**

$$C_{slippage} = Q \times P \times (s_A + s_B)$$

### 5.2 Exchange Fee Comparison Table

| Exchange | Spot Maker | Spot Taker | Withdrawal (BTC) | Withdrawal (USDT-TRC20) |
|----------|:----------:|:----------:|:-----------------:|:-----------------------:|
| Binance | 0.10% | 0.10% | 0.0001 BTC | 1 USDT |
| Coinbase | 0.40% | 0.60% | Dynamic | Dynamic |
| OKX | 0.08% | 0.10% | 0.0001 BTC | 0.8 USDT |
| Bybit | 0.10% | 0.10% | 0.0002 BTC | 1 USDT |
| Kraken | 0.16% | 0.26% | 0.00015 BTC | 2.5 USDT |
| KuCoin | 0.10% | 0.10% | 0.0004 BTC | 1 USDT |
| Gate.io | 0.10% | 0.10% | 0.001 BTC | 1 USDT |
| MEXC | 0.00% | 0.10% | 0.0003 BTC | 1 USDT |
| HTX (Huobi) | 0.20% | 0.20% | 0.0004 BTC | 1 USDT |

### 5.3 VIP Tier Impact

Most exchanges offer volume-based fee discounts:

| Monthly Volume | Binance Fee | OKX Fee | Bybit Fee |
|:--------------:|:-----------:|:-------:|:---------:|
| < $1M | 0.10%/0.10% | 0.08%/0.10% | 0.10%/0.10% |
| $1M - $5M | 0.09%/0.09% | 0.06%/0.08% | 0.06%/0.06% |
| $5M - $20M | 0.07%/0.08% | 0.05%/0.07% | 0.04%/0.05% |
| $20M - $100M | 0.05%/0.06% | 0.03%/0.05% | 0.03%/0.04% |
| > $100M | 0.02%/0.04% | 0.02%/0.04% | 0.02%/0.03% |

### 5.4 Total Cost Comparison for Different Exchange Pairs

**Example: $50,000 BTC arbitrage trade**

| Exchange Pair | Buy Fee | Sell Fee | Total Fee | Required Spread |
|:------------:|:-------:|:--------:|:---------:|:---------------:|
| Binance ↔ OKX (standard) | $50 | $50 | $100 | > 20 bps |
| Binance ↔ OKX (VIP) | $10 | $10 | $20 | > 4 bps |
| Binance ↔ Coinbase | $50 | $300 | $350 | > 70 bps |
| Binance ↔ Kraken | $50 | $130 | $180 | > 36 bps |
| OKX ↔ Bybit (VIP) | $10 | $10 | $20 | > 4 bps |

---

## 6. Mathematical Model — Minimum Profitable Spread

### 6.1 Minimum Spread Derivation

For a profitable cross-exchange arbitrage between Exchange A (buy) and Exchange B (sell):

$$\text{Net Profit} = Q \times (P_B^{bid} - P_A^{ask}) - C_{total} > 0$$

$$P_B^{bid} - P_A^{ask} > \frac{C_{total}}{Q}$$

In basis points:

$$\text{Spread}_{min} = \frac{C_{total}}{Q \times P_{mid}} \times 10000$$

### 6.2 Detailed Minimum Spread Formula

$$\boxed{\text{Spread}_{min} = f_A + f_B + s_A + s_B + \frac{F_{rebalance}}{Q \times P \times N_{avg}} + \epsilon}$$

Where:
- $f_A$ = fee rate on buy exchange
- $f_B$ = fee rate on sell exchange
- $s_A$ = estimated slippage on buy exchange
- $s_B$ = estimated slippage on sell exchange
- $F_{rebalance}$ = rebalancing cost (transfer fee)
- $N_{avg}$ = average number of trades between rebalances
- $\epsilon$ = safety margin / minimum acceptable profit

### 6.3 Spread Decomposition

$$\text{Observed Spread} = \text{True Spread} + \text{Noise}$$

**True spread** is the persistent component that can be captured.
**Noise** is the temporary component that may disappear before execution.

Signal-to-noise analysis:

$$SNR = \frac{\mu_{spread}}{\sigma_{spread}}$$

If $SNR < 1$, the spread is mostly noise and difficult to capture reliably.

### 6.4 Expected Profit Model

Given spread observations $\{S_1, S_2, ..., S_n\}$ with distribution $S \sim f(s)$:

$$E[\text{Profit per trade}] = \int_{S_{min}}^{\infty} (s - S_{min}) \times f(s) \, ds$$

$$E[\text{Daily Profit}] = E[\text{Profit per trade}] \times N_{opportunities/day} \times P_{execution}$$

Where $P_{execution}$ is the probability of successful execution given opportunity detection.

### 6.5 Optimal Order Size

The optimal order size maximizes profit while accounting for market impact:

$$Q^* = \argmax_Q \left[ Q \times (\text{Spread} - S_{min}) - Q^2 \times \lambda \right]$$

Where $\lambda$ is the market impact parameter. Solution:

$$Q^* = \frac{\text{Spread} - S_{min}}{2\lambda}$$

Market impact parameter estimation:

$$\lambda = \frac{\Delta P}{Q} = \frac{P_{fill} - P_{best}}{Q_{traded}}$$

---

## 7. Integration with Exchange APIs

### 7.1 API Architecture

```python
from abc import ABC, abstractmethod
import asyncio
import aiohttp
import hmac
import hashlib
import time

class ExchangeConnector(ABC):
    """Abstract base class for exchange API integration."""
    
    @abstractmethod
    async def get_order_book(self, symbol: str, depth: int) -> dict:
        pass
    
    @abstractmethod
    async def place_order(self, symbol: str, side: str, 
                          order_type: str, quantity: float, 
                          price: float = None) -> dict:
        pass
    
    @abstractmethod
    async def get_balance(self, asset: str) -> float:
        pass
    
    @abstractmethod
    async def subscribe_order_book(self, symbol: str, callback):
        pass


class BinanceConnector(ExchangeConnector):
    """Binance API integration."""
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.binance.com"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.ws_url = "wss://stream.binance.com:9443/ws"
        self.session = None
    
    async def get_order_book(self, symbol: str, depth: int = 20) -> dict:
        """Get order book snapshot."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/v3/depth"
            params = {"symbol": symbol.replace("/", ""), "limit": depth}
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                return {
                    'bids': [(float(p), float(q)) for p, q in data['bids']],
                    'asks': [(float(p), float(q)) for p, q in data['asks']],
                    'timestamp': time.time()
                }
    
    async def place_order(self, symbol: str, side: str,
                          order_type: str, quantity: float,
                          price: float = None) -> dict:
        """Place an order on Binance."""
        params = {
            "symbol": symbol.replace("/", ""),
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": f"{quantity:.8f}",
            "timestamp": int(time.time() * 1000),
            "recvWindow": 5000,
        }
        
        if price and order_type != "MARKET":
            params["price"] = f"{price:.8f}"
            params["timeInForce"] = "IOC"  # Immediate or Cancel
        
        # Sign request
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        signature = hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        
        headers = {"X-MBX-APIKEY": self.api_key}
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/v3/order"
            async with session.post(url, params=params, headers=headers) as resp:
                return await resp.json()
    
    async def subscribe_order_book(self, symbol: str, callback):
        """Subscribe to real-time order book updates via WebSocket."""
        stream = f"{symbol.lower().replace('/', '')}@depth20@100ms"
        ws_url = f"{self.ws_url}/{stream}"
        
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = msg.json()
                        await callback(data)


class OKXConnector(ExchangeConnector):
    """OKX API integration."""
    
    def __init__(self, api_key: str, secret_key: str, passphrase: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.base_url = "https://www.okx.com"
        self.ws_url = "wss://ws.okx.com:8443/ws/v5/public"
    
    async def get_order_book(self, symbol: str, depth: int = 20) -> dict:
        """Get OKX order book."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/v5/market/books"
            params = {"instId": symbol.replace("/", "-"), "sz": str(depth)}
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                book = data['data'][0]
                return {
                    'bids': [(float(b[0]), float(b[1])) for b in book['bids']],
                    'asks': [(float(a[0]), float(a[1])) for a in book['asks']],
                    'timestamp': float(book['ts']) / 1000
                }
    
    # ... (similar implementation for other methods)
```

### 7.2 Unified Exchange Interface

```python
class UnifiedExchangeManager:
    """
    Manages connections to multiple exchanges with a unified interface.
    Handles rate limiting, error recovery, and connection management.
    """
    
    def __init__(self, exchange_configs: dict):
        self.connectors = {}
        self.rate_limiters = {}
        self.order_books = {}  # {(exchange, symbol): OrderBook}
        
        for name, config in exchange_configs.items():
            self.connectors[name] = self.create_connector(name, config)
            self.rate_limiters[name] = RateLimiter(config.get('rate_limit', 10))
    
    async def get_best_prices(self, symbol: str) -> dict:
        """Get best bid/ask from all exchanges for a symbol."""
        prices = {}
        
        tasks = {
            name: connector.get_order_book(symbol)
            for name, connector in self.connectors.items()
        }
        
        results = await asyncio.gather(
            *[self.fetch_with_rate_limit(name, task) 
              for name, task in tasks.items()],
            return_exceptions=True
        )
        
        for (name, _), result in zip(tasks.items(), results):
            if isinstance(result, Exception):
                continue
            prices[name] = {
                'best_bid': result['bids'][0][0] if result['bids'] else 0,
                'best_ask': result['asks'][0][0] if result['asks'] else float('inf'),
                'bid_depth': sum(q for _, q in result['bids'][:5]),
                'ask_depth': sum(q for _, q in result['asks'][:5]),
                'timestamp': result['timestamp']
            }
        
        return prices
    
    def find_arbitrage(self, prices: dict, min_spread_bps: float) -> Optional[dict]:
        """
        Find the best arbitrage opportunity across exchanges.
        
        Returns the exchange pair with the widest profitable spread.
        """
        best_opportunity = None
        max_spread = 0
        
        exchanges = list(prices.keys())
        
        for i in range(len(exchanges)):
            for j in range(len(exchanges)):
                if i == j:
                    continue
                
                buy_exchange = exchanges[i]
                sell_exchange = exchanges[j]
                
                ask = prices[buy_exchange]['best_ask']
                bid = prices[sell_exchange]['best_bid']
                
                if ask == 0 or bid == 0:
                    continue
                
                spread_bps = (bid - ask) / ask * 10000
                
                if spread_bps > min_spread_bps and spread_bps > max_spread:
                    max_spread = spread_bps
                    best_opportunity = {
                        'buy_exchange': buy_exchange,
                        'sell_exchange': sell_exchange,
                        'buy_price': ask,
                        'sell_price': bid,
                        'spread_bps': spread_bps,
                        'buy_depth': prices[buy_exchange]['ask_depth'],
                        'sell_depth': prices[sell_exchange]['bid_depth'],
                    }
        
        return best_opportunity
```

### 7.3 WebSocket Multi-Exchange Price Feed

```python
class MultiExchangePriceFeed:
    """
    Maintains real-time price data from multiple exchanges simultaneously.
    Triggers callbacks when arbitrage opportunities are detected.
    """
    
    def __init__(self, exchanges: dict, symbols: List[str], on_opportunity):
        self.exchanges = exchanges
        self.symbols = symbols
        self.on_opportunity = on_opportunity
        self.books = {}  # {(exchange, symbol): {bid, ask, depth, timestamp}}
    
    async def start(self):
        """Start all WebSocket connections in parallel."""
        tasks = []
        for exchange_name, connector in self.exchanges.items():
            for symbol in self.symbols:
                task = asyncio.create_task(
                    connector.subscribe_order_book(
                        symbol,
                        lambda data, ex=exchange_name, sym=symbol: 
                            self.on_book_update(ex, sym, data)
                    )
                )
                tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    async def on_book_update(self, exchange: str, symbol: str, data: dict):
        """Called when any exchange's order book updates."""
        # Update local state
        self.books[(exchange, symbol)] = {
            'bid': data['bids'][0][0] if data['bids'] else 0,
            'ask': data['asks'][0][0] if data['asks'] else float('inf'),
            'bid_depth': sum(q for _, q in data['bids'][:5]),
            'ask_depth': sum(q for _, q in data['asks'][:5]),
            'timestamp': time.time()
        }
        
        # Check for arbitrage across exchanges
        self.check_opportunities(symbol)
    
    def check_opportunities(self, symbol: str):
        """Check all exchange pairs for arbitrage on this symbol."""
        exchange_prices = {
            ex: self.books[(ex, symbol)]
            for ex in self.exchanges.keys()
            if (ex, symbol) in self.books
        }
        
        if len(exchange_prices) < 2:
            return
        
        # Find best bid and best ask across all exchanges
        best_bid_exchange = max(exchange_prices.items(), key=lambda x: x[1]['bid'])
        best_ask_exchange = min(exchange_prices.items(), key=lambda x: x[1]['ask'])
        
        if best_bid_exchange[0] == best_ask_exchange[0]:
            return  # Same exchange, not cross-exchange arb
        
        spread = best_bid_exchange[1]['bid'] - best_ask_exchange[1]['ask']
        
        if spread > 0:
            spread_bps = spread / best_ask_exchange[1]['ask'] * 10000
            self.on_opportunity({
                'symbol': symbol,
                'buy_exchange': best_ask_exchange[0],
                'sell_exchange': best_bid_exchange[0],
                'buy_price': best_ask_exchange[1]['ask'],
                'sell_price': best_bid_exchange[1]['bid'],
                'spread_bps': spread_bps,
            })
```

---

## 8. Complete Execution Algorithm

### 8.1 Full Cross-Exchange Arbitrage Engine

```python
import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from collections import deque

# ============================================================
# CONFIGURATION
# ============================================================

@dataclass
class CrossExchangeArbConfig:
    # Exchanges and pairs to monitor
    exchanges: List[str]
    symbols: List[str]
    
    # Fee configuration
    fee_rates: Dict[str, float]          # {exchange: taker_fee_rate}
    withdrawal_fees: Dict[str, float]    # {exchange: withdrawal_fee_usd}
    
    # Profitability thresholds
    min_spread_bps: float = 10.0         # Minimum spread to consider
    min_profit_usd: float = 5.0          # Minimum absolute profit
    safety_margin_bps: float = 2.0       # Extra safety buffer
    
    # Position sizing
    base_order_size_usd: float = 10_000
    max_order_size_usd: float = 100_000
    depth_utilization_pct: float = 0.20  # Max 20% of visible depth
    
    # Balance management
    target_balance_usd: float = 50_000   # Per exchange
    rebalance_threshold_pct: float = 0.30 # Rebalance at 30% imbalance
    min_balance_usd: float = 10_000      # Minimum to continue trading
    
    # Execution
    order_type: str = "LIMIT_IOC"
    max_execution_time_ms: float = 2000
    max_slippage_bps: float = 5.0
    
    # Risk
    max_daily_loss_usd: float = 1_000
    max_consecutive_losses: int = 5
    max_daily_trades: int = 500
    cooldown_after_failure_sec: float = 30

# ============================================================
# MAIN ENGINE
# ============================================================

class CrossExchangeArbitrageEngine:
    """
    Complete cross-exchange arbitrage engine.
    
    Architecture:
    1. Multi-exchange price feed (WebSocket)
    2. Opportunity detection (spread > threshold)
    3. Profitability verification (after all costs)
    4. Simultaneous execution (buy on cheap exchange, sell on expensive)
    5. P&L tracking and risk management
    6. Periodic rebalancing
    """
    
    def __init__(self, config: CrossExchangeArbConfig, exchange_manager, risk_manager):
        self.config = config
        self.exchange_mgr = exchange_manager
        self.risk_mgr = risk_manager
        
        # State
        self.order_books = {}              # {(exchange, symbol): OrderBook}
        self.balances = {}                 # {exchange: {asset: amount}}
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.consecutive_losses = 0
        self.trade_history = deque(maxlen=10000)
        self.is_running = False
        self.last_failure_time = 0
    
    # ----------------------------------------------------------
    # MAIN LOOP
    # ----------------------------------------------------------
    
    async def run(self):
        """Main entry point."""
        self.is_running = True
        
        # Initialize
        await self.initialize_balances()
        
        # Start price feed (event-driven)
        price_feed = MultiExchangePriceFeed(
            exchanges=self.exchange_mgr.connectors,
            symbols=self.config.symbols,
            on_opportunity=self.on_opportunity_detected
        )
        
        # Run price feed and periodic tasks concurrently
        await asyncio.gather(
            price_feed.start(),
            self.periodic_rebalance_check(),
            self.periodic_balance_update(),
        )
    
    async def on_opportunity_detected(self, opportunity: dict):
        """
        Callback triggered when a potential arbitrage is detected.
        This is called from the price feed when spread > 0.
        """
        if not self.is_running:
            return
        
        # Check cooldown
        if time.time() - self.last_failure_time < self.config.cooldown_after_failure_sec:
            return
        
        # Check circuit breakers
        if self.check_circuit_breakers():
            return
        
        symbol = opportunity['symbol']
        buy_exchange = opportunity['buy_exchange']
        sell_exchange = opportunity['sell_exchange']
        buy_price = opportunity['buy_price']
        sell_price = opportunity['sell_price']
        spread_bps = opportunity['spread_bps']
        
        # Step 1: Verify spread exceeds minimum threshold
        min_threshold = self.calculate_min_threshold(buy_exchange, sell_exchange)
        if spread_bps < min_threshold:
            return
        
        # Step 2: Calculate optimal order size
        order_size = self.calculate_order_size(
            symbol, buy_exchange, sell_exchange, buy_price, sell_price
        )
        
        if order_size <= 0:
            return
        
        # Step 3: Verify balances
        if not self.verify_balances(symbol, buy_exchange, sell_exchange, order_size, buy_price):
            return
        
        # Step 4: Final profitability check with exact amounts
        net_profit = self.calculate_net_profit(
            order_size, buy_price, sell_price, buy_exchange, sell_exchange
        )
        
        if net_profit < self.config.min_profit_usd:
            return
        
        # Step 5: Execute
        result = await self.execute_arbitrage(
            symbol, buy_exchange, sell_exchange,
            order_size, buy_price, sell_price
        )
        
        # Step 6: Process result
        self.process_result(result)
    
    # ----------------------------------------------------------
    # OPPORTUNITY ANALYSIS
    # ----------------------------------------------------------
    
    def calculate_min_threshold(self, buy_exchange: str, sell_exchange: str) -> float:
        """Calculate minimum profitable spread in basis points."""
        fee_buy = self.config.fee_rates.get(buy_exchange, 0.001)
        fee_sell = self.config.fee_rates.get(sell_exchange, 0.001)
        
        # Convert to bps
        fees_bps = (fee_buy + fee_sell) * 10000
        slippage_bps = 2.0  # Estimated combined slippage
        safety_bps = self.config.safety_margin_bps
        
        # Amortized rebalance cost (negligible for pre-positioned strategy)
        rebalance_bps = 0.5  # Small allowance for periodic rebalancing
        
        return fees_bps + slippage_bps + safety_bps + rebalance_bps
    
    def calculate_order_size(self, symbol: str, buy_exchange: str,
                             sell_exchange: str, buy_price: float,
                             sell_price: float) -> float:
        """
        Calculate optimal order size considering:
        - Available balance
        - Order book depth
        - Position limits
        """
        # Get available balances
        buy_balance_usd = self.balances.get(buy_exchange, {}).get('USDT', 0)
        sell_balance_base = self.balances.get(sell_exchange, {}).get(
            symbol.split('/')[0], 0
        )
        sell_balance_usd = sell_balance_base * sell_price
        
        # Limit by balance
        max_by_balance = min(buy_balance_usd, sell_balance_usd) * 0.90  # 10% buffer
        
        # Limit by order book depth
        buy_key = (buy_exchange, symbol)
        sell_key = (sell_exchange, symbol)
        
        buy_depth = self.order_books.get(buy_key, {}).get('ask_depth_usd', 0)
        sell_depth = self.order_books.get(sell_key, {}).get('bid_depth_usd', 0)
        
        max_by_depth = min(buy_depth, sell_depth) * self.config.depth_utilization_pct
        
        # Limit by config
        max_by_config = self.config.max_order_size_usd
        
        # Final order size
        order_size_usd = min(
            max_by_balance,
            max_by_depth,
            max_by_config,
            self.config.base_order_size_usd  # Start with base size
        )
        
        # Scale up for larger opportunities
        # (bigger spread = can handle more slippage = larger size)
        spread_multiplier = min(2.0, spread_bps / self.config.min_spread_bps)
        order_size_usd *= spread_multiplier
        
        # Convert to base asset quantity
        order_qty = order_size_usd / buy_price
        
        return order_qty
    
    def calculate_net_profit(self, quantity: float, buy_price: float,
                             sell_price: float, buy_exchange: str,
                             sell_exchange: str) -> float:
        """Calculate net profit after all costs."""
        # Gross profit
        gross = quantity * (sell_price - buy_price)
        
        # Fees
        buy_fee = quantity * buy_price * self.config.fee_rates.get(buy_exchange, 0.001)
        sell_fee = quantity * sell_price * self.config.fee_rates.get(sell_exchange, 0.001)
        
        # Slippage estimate
        slippage = quantity * buy_price * 0.0002  # 2 bps estimate
        
        return gross - buy_fee - sell_fee - slippage
    
    def verify_balances(self, symbol: str, buy_exchange: str,
                        sell_exchange: str, quantity: float,
                        buy_price: float) -> bool:
        """Verify sufficient balances for the trade."""
        base_asset = symbol.split('/')[0]
        
        # Need USDT on buy exchange
        usdt_needed = quantity * buy_price * 1.01  # 1% buffer
        usdt_available = self.balances.get(buy_exchange, {}).get('USDT', 0)
        
        # Need base asset on sell exchange
        base_available = self.balances.get(sell_exchange, {}).get(base_asset, 0)
        
        return usdt_available >= usdt_needed and base_available >= quantity
    
    # ----------------------------------------------------------
    # EXECUTION
    # ----------------------------------------------------------
    
    async def execute_arbitrage(self, symbol: str, buy_exchange: str,
                                sell_exchange: str, quantity: float,
                                buy_price: float, sell_price: float) -> dict:
        """
        Execute cross-exchange arbitrage.
        Submit buy and sell orders simultaneously.
        """
        start_time = time.time()
        
        # Prepare orders
        buy_order = {
            'exchange': buy_exchange,
            'symbol': symbol,
            'side': 'BUY',
            'type': self.config.order_type,
            'quantity': quantity,
            'price': buy_price * 1.001,  # Slightly above ask to ensure fill
        }
        
        sell_order = {
            'exchange': sell_exchange,
            'symbol': symbol,
            'side': 'SELL',
            'type': self.config.order_type,
            'quantity': quantity,
            'price': sell_price * 0.999,  # Slightly below bid to ensure fill
        }
        
        # Submit simultaneously
        try:
            buy_result, sell_result = await asyncio.gather(
                self.exchange_mgr.place_order(buy_exchange, buy_order),
                self.exchange_mgr.place_order(sell_exchange, sell_order),
                return_exceptions=True
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            # Process results
            buy_success = not isinstance(buy_result, Exception) and buy_result.get('status') == 'FILLED'
            sell_success = not isinstance(sell_result, Exception) and sell_result.get('status') == 'FILLED'
            
            if buy_success and sell_success:
                # Both filled - calculate actual profit
                actual_buy_price = buy_result['avg_price']
                actual_sell_price = sell_result['avg_price']
                actual_qty = min(buy_result['filled_qty'], sell_result['filled_qty'])
                
                gross_profit = actual_qty * (actual_sell_price - actual_buy_price)
                fees = (buy_result.get('fee', 0) + sell_result.get('fee', 0))
                net_profit = gross_profit - fees
                
                return {
                    'success': True,
                    'symbol': symbol,
                    'buy_exchange': buy_exchange,
                    'sell_exchange': sell_exchange,
                    'quantity': actual_qty,
                    'buy_price': actual_buy_price,
                    'sell_price': actual_sell_price,
                    'gross_profit': gross_profit,
                    'fees': fees,
                    'net_profit': net_profit,
                    'execution_time_ms': execution_time,
                    'expected_spread_bps': (sell_price - buy_price) / buy_price * 10000,
                    'actual_spread_bps': (actual_sell_price - actual_buy_price) / actual_buy_price * 10000,
                }
            
            elif buy_success and not sell_success:
                # Buy filled, sell failed - need to unwind
                await self.unwind_buy(buy_exchange, symbol, buy_result['filled_qty'])
                return {
                    'success': False,
                    'error': 'sell_failed',
                    'net_profit': -buy_result.get('fee', 0),
                    'execution_time_ms': execution_time,
                }
            
            elif not buy_success and sell_success:
                # Sell filled, buy failed - need to unwind
                await self.unwind_sell(sell_exchange, symbol, sell_result['filled_qty'])
                return {
                    'success': False,
                    'error': 'buy_failed',
                    'net_profit': -sell_result.get('fee', 0),
                    'execution_time_ms': execution_time,
                }
            
            else:
                # Both failed
                return {
                    'success': False,
                    'error': 'both_failed',
                    'net_profit': 0,
                    'execution_time_ms': execution_time,
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'net_profit': 0,
                'execution_time_ms': (time.time() - start_time) * 1000,
            }
    
    async def unwind_buy(self, exchange: str, symbol: str, quantity: float):
        """Unwind a buy order by selling at market."""
        try:
            await self.exchange_mgr.place_order(exchange, {
                'symbol': symbol, 'side': 'SELL',
                'type': 'MARKET', 'quantity': quantity
            })
        except Exception as e:
            self.log_critical(f"FAILED TO UNWIND BUY on {exchange}: {e}")
    
    async def unwind_sell(self, exchange: str, symbol: str, quantity: float):
        """Unwind a sell order by buying at market."""
        try:
            await self.exchange_mgr.place_order(exchange, {
                'symbol': symbol, 'side': 'BUY',
                'type': 'MARKET', 'quantity': quantity
            })
        except Exception as e:
            self.log_critical(f"FAILED TO UNWIND SELL on {exchange}: {e}")
    
    # ----------------------------------------------------------
    # BALANCE AND REBALANCING
    # ----------------------------------------------------------
    
    async def initialize_balances(self):
        """Load initial balances from all exchanges."""
        for exchange in self.config.exchanges:
            self.balances[exchange] = await self.exchange_mgr.get_all_balances(exchange)
    
    async def periodic_balance_update(self):
        """Update balances periodically."""
        while self.is_running:
            await self.initialize_balances()
            await asyncio.sleep(10)  # Every 10 seconds
    
    async def periodic_rebalance_check(self):
        """Check if rebalancing is needed and execute if so."""
        while self.is_running:
            await asyncio.sleep(300)  # Check every 5 minutes
            
            rebalance_actions = self.check_rebalance_needed()
            for action in rebalance_actions:
                await self.execute_rebalance(action)
    
    def check_rebalance_needed(self) -> List[dict]:
        """Determine if any exchange pair needs rebalancing."""
        actions = []
        
        for symbol in self.config.symbols:
            base_asset = symbol.split('/')[0]
            
            for exchange in self.config.exchanges:
                base_balance = self.balances.get(exchange, {}).get(base_asset, 0)
                quote_balance = self.balances.get(exchange, {}).get('USDT', 0)
                
                current_price = self.get_mid_price(symbol, exchange)
                if current_price == 0:
                    continue
                
                base_value = base_balance * current_price
                total_value = base_value + quote_balance
                target_base_value = total_value * 0.5  # 50/50 split
                
                imbalance = abs(base_value - target_base_value) / target_base_value
                
                if imbalance > self.config.rebalance_threshold_pct:
                    if base_value > target_base_value:
                        # Too much base, need to move to exchange with deficit
                        actions.append({
                            'type': 'sell_base',
                            'exchange': exchange,
                            'asset': base_asset,
                            'amount': (base_value - target_base_value) / current_price
                        })
        
        return actions
    
    # ----------------------------------------------------------
    # RISK AND P&L
    # ----------------------------------------------------------
    
    def process_result(self, result: dict):
        """Process trade result."""
        profit = result.get('net_profit', 0)
        self.daily_pnl += profit
        self.daily_trades += 1
        self.trade_history.append(result)
        
        if profit < 0:
            self.consecutive_losses += 1
            self.last_failure_time = time.time()
        else:
            self.consecutive_losses = 0
        
        # Update local balance cache
        if result['success']:
            self.update_balance_cache(result)
        
        self.log_trade(result)
    
    def check_circuit_breakers(self) -> bool:
        """Check if circuit breakers are triggered."""
        if self.daily_pnl < -self.config.max_daily_loss_usd:
            return True
        if self.consecutive_losses >= self.config.max_consecutive_losses:
            return True
        if self.daily_trades >= self.config.max_daily_trades:
            return True
        return False
    
    # ----------------------------------------------------------
    # HELPERS
    # ----------------------------------------------------------
    
    def get_mid_price(self, symbol: str, exchange: str) -> float:
        """Get mid price from cached order book."""
        key = (exchange, symbol)
        book = self.order_books.get(key)
        if book and book.get('bid') and book.get('ask'):
            return (book['bid'] + book['ask']) / 2
        return 0
    
    def update_balance_cache(self, result: dict):
        """Update local balance cache after a trade."""
        symbol = result['symbol']
        base_asset = symbol.split('/')[0]
        
        # Buy exchange: spent USDT, gained base
        buy_ex = result['buy_exchange']
        self.balances.setdefault(buy_ex, {})
        self.balances[buy_ex]['USDT'] = self.balances[buy_ex].get('USDT', 0) - result['quantity'] * result['buy_price']
        self.balances[buy_ex][base_asset] = self.balances[buy_ex].get(base_asset, 0) + result['quantity']
        
        # Sell exchange: gained USDT, spent base
        sell_ex = result['sell_exchange']
        self.balances.setdefault(sell_ex, {})
        self.balances[sell_ex]['USDT'] = self.balances[sell_ex].get('USDT', 0) + result['quantity'] * result['sell_price']
        self.balances[sell_ex][base_asset] = self.balances[sell_ex].get(base_asset, 0) - result['quantity']
    
    def log_trade(self, result: dict):
        """Log trade details."""
        if result['success']:
            print(
                f"[TRADE] {result['symbol']} | "
                f"Buy@{result['buy_exchange']}:{result['buy_price']:.2f} | "
                f"Sell@{result['sell_exchange']}:{result['sell_price']:.2f} | "
                f"Qty:{result['quantity']:.6f} | "
                f"Net P&L: ${result['net_profit']:.2f} | "
                f"Spread: {result['actual_spread_bps']:.1f}bps | "
                f"Time: {result['execution_time_ms']:.0f}ms"
            )
        else:
            print(f"[FAILED] {result.get('error', 'unknown')} | Loss: ${result.get('net_profit', 0):.2f}")
    
    def log_critical(self, msg: str):
        print(f"[CRITICAL] {msg}")
```

---

## 9. Risk Management

### 9.1 Risk Parameter Configuration

```python
CROSS_EXCHANGE_RISK_PARAMS = {
    # Exchange Risk
    "max_capital_per_exchange_pct": 0.35,     # Max 35% on any single exchange
    "exchange_health_check_interval_s": 10,
    "max_api_error_rate": 0.03,              # Pause at 3% error rate
    "max_order_rejection_rate": 0.10,        # Pause at 10% rejection rate
    
    # Execution Risk
    "max_execution_time_ms": 2000,           # Cancel if > 2 seconds
    "max_partial_fill_wait_ms": 5000,        # Wait max 5s for remaining fill
    "min_fill_ratio": 0.80,                  # Minimum 80% fill on each leg
    "max_slippage_bps": 10,                  # Maximum slippage per leg
    
    # Position / Inventory Risk
    "max_imbalance_ratio": 0.50,             # Force rebalance at 50%
    "emergency_rebalance_ratio": 0.70,       # Emergency at 70%
    "min_balance_per_exchange_usd": 5000,    # Minimum working balance
    
    # Loss Limits
    "max_loss_per_trade_usd": 100,
    "max_daily_loss_usd": 2000,
    "max_weekly_loss_usd": 5000,
    "max_drawdown_pct": 0.05,               # 5% of total capital
    
    # Circuit Breakers
    "max_consecutive_losses": 5,
    "cooldown_after_loss_sec": 30,
    "cooldown_after_failure_sec": 60,
    "pause_on_volatility_spike": True,
    "volatility_pause_threshold": 0.05,      # 5% move in 5 minutes
    
    # Withdrawal / Transfer Risk
    "max_pending_withdrawals": 3,
    "max_pending_withdrawal_usd": 100_000,
    "withdrawal_stuck_alert_minutes": 60,
}
```

### 9.2 Key Risks and Mitigations

| Risk | Severity | Probability | Mitigation |
|------|:--------:|:-----------:|------------|
| Exchange insolvency | Critical | Low | Cap exposure per exchange at 35% |
| API downtime | High | Medium | Redundant connections, failover |
| Partial fills (one leg) | High | Medium | IOC orders, immediate unwind |
| Withdrawal suspension | Medium | Medium | Pre-position, diversify |
| Price moved during execution | Medium | High | Fast execution, slippage limits |
| Rate limiting | Low | High | Client-side rate limiter |
| Balance discrepancy | Medium | Low | Periodic reconciliation |
| Network partition | High | Low | Multiple network paths |
| Flash crash | Medium | Low | Pause during extreme volatility |
| Regulatory action (exchange) | Critical | Low | Diversify across jurisdictions |

### 9.3 Exchange Counterparty Risk Management

```python
class ExchangeRiskMonitor:
    """
    Monitors exchange health and counterparty risk.
    """
    
    def __init__(self, exchanges: List[str]):
        self.exchanges = exchanges
        self.health_scores = {ex: 1.0 for ex in exchanges}
        self.incident_history = {}
    
    def update_health_score(self, exchange: str, metrics: dict):
        """
        Update exchange health score based on operational metrics.
        
        Score: 0.0 (critical) to 1.0 (healthy)
        """
        score = 1.0
        
        # API latency check
        if metrics.get('avg_latency_ms', 0) > 500:
            score -= 0.2
        elif metrics.get('avg_latency_ms', 0) > 200:
            score -= 0.1
        
        # Error rate check
        if metrics.get('error_rate', 0) > 0.05:
            score -= 0.3
        elif metrics.get('error_rate', 0) > 0.02:
            score -= 0.1
        
        # Withdrawal status
        if not metrics.get('withdrawals_enabled', True):
            score -= 0.3
        
        # Recent incidents
        if metrics.get('recent_incidents', 0) > 0:
            score -= 0.1 * metrics['recent_incidents']
        
        self.health_scores[exchange] = max(0.0, score)
    
    def should_trade_on(self, exchange: str) -> bool:
        """Check if it's safe to trade on this exchange."""
        return self.health_scores.get(exchange, 0) >= 0.5
    
    def get_max_exposure(self, exchange: str, total_capital: float) -> float:
        """Get maximum safe exposure for an exchange."""
        health = self.health_scores.get(exchange, 0.5)
        base_limit = total_capital * 0.35  # Base limit: 35%
        
        # Reduce limit proportional to health degradation
        return base_limit * health
```

---

## 10. Performance Analytics

### 10.1 Key Performance Metrics

```python
class PerformanceTracker:
    """Track and analyze cross-exchange arbitrage performance."""
    
    def calculate_metrics(self, trades: List[dict], period_days: float) -> dict:
        """Calculate comprehensive performance metrics."""
        if not trades:
            return {}
        
        profits = [t['net_profit'] for t in trades if t.get('success')]
        all_profits = [t.get('net_profit', 0) for t in trades]
        
        successful_trades = [t for t in trades if t.get('success')]
        
        return {
            # P&L Metrics
            'total_pnl': sum(all_profits),
            'avg_profit_per_trade': sum(profits) / len(profits) if profits else 0,
            'median_profit': sorted(profits)[len(profits)//2] if profits else 0,
            'max_profit': max(profits) if profits else 0,
            'max_loss': min(all_profits) if all_profits else 0,
            
            # Win/Loss
            'total_trades': len(trades),
            'successful_trades': len(successful_trades),
            'win_rate': len([p for p in profits if p > 0]) / len(profits) if profits else 0,
            'profit_factor': (
                sum(p for p in profits if p > 0) / abs(sum(p for p in profits if p < 0))
                if any(p < 0 for p in profits) else float('inf')
            ),
            
            # Risk Metrics
            'sharpe_ratio': self.calculate_sharpe(profits, period_days),
            'max_drawdown': self.calculate_max_drawdown(all_profits),
            'avg_daily_pnl': sum(all_profits) / period_days if period_days > 0 else 0,
            
            # Execution Metrics
            'avg_execution_time_ms': (
                sum(t['execution_time_ms'] for t in successful_trades) / len(successful_trades)
                if successful_trades else 0
            ),
            'avg_spread_captured_bps': (
                sum(t.get('actual_spread_bps', 0) for t in successful_trades) / len(successful_trades)
                if successful_trades else 0
            ),
            'fill_rate': len(successful_trades) / len(trades) if trades else 0,
            
            # Opportunity Metrics
            'trades_per_day': len(trades) / period_days if period_days > 0 else 0,
            'capital_turnover': (
                sum(t.get('quantity', 0) * t.get('buy_price', 0) for t in successful_trades)
            ),
        }
    
    def calculate_sharpe(self, profits: List[float], period_days: float) -> float:
        """Calculate annualized Sharpe ratio."""
        if not profits or len(profits) < 2:
            return 0
        
        import numpy as np
        returns = np.array(profits)
        trades_per_day = len(profits) / period_days if period_days > 0 else 1
        
        mean_return = returns.mean()
        std_return = returns.std()
        
        if std_return == 0:
            return float('inf') if mean_return > 0 else 0
        
        # Annualize: multiply by sqrt(trades per year)
        trades_per_year = trades_per_day * 365
        return (mean_return / std_return) * np.sqrt(trades_per_year)
    
    def calculate_max_drawdown(self, profits: List[float]) -> float:
        """Calculate maximum drawdown from cumulative P&L."""
        if not profits:
            return 0
        
        cumulative = []
        running = 0
        for p in profits:
            running += p
            cumulative.append(running)
        
        peak = cumulative[0]
        max_dd = 0
        
        for value in cumulative:
            if value > peak:
                peak = value
            dd = peak - value
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
```

---

## 11. Production Deployment

### 11.1 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION SYSTEM                         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Price      │  │  Arbitrage   │  │    Execution        │ │
│  │   Aggregator │──│  Detector    │──│    Engine           │ │
│  │  (WebSocket) │  │              │  │   (Async Orders)    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│        │                │                    │              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Balance    │  │    Risk     │  │    Rebalancer       │ │
│  │   Monitor    │  │   Manager   │  │   (Periodic)        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Monitoring / Alerting                       │ │
│  │   Grafana | Prometheus | PagerDuty | Slack             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
    ┌────┴────┐    ┌────┴────┐    ┌────┴────┐    ┌────┴────┐
    │ Binance  │    │  OKX    │    │  Bybit  │    │ Coinbase │
    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

### 11.2 Server Location Strategy

| Exchange | Recommended Server Location | Expected Latency |
|----------|:---------------------------:|:-----------------:|
| Binance | AWS Tokyo (ap-northeast-1) | < 5 ms |
| OKX | AWS Singapore (ap-southeast-1) | < 10 ms |
| Bybit | AWS Singapore | < 10 ms |
| Coinbase | AWS us-east-1 | < 5 ms |
| Kraken | AWS eu-west-1 | < 10 ms |

**Multi-region deployment:** Run instances in multiple regions, each optimized for the nearest exchanges.

### 11.3 Monitoring Checklist

```
Real-Time Dashboards:
├── P&L (cumulative, daily, per-exchange, per-symbol)
├── Spread monitoring (current vs historical)
├── Execution metrics (fill rate, slippage, latency)
├── Balance distribution (per exchange, per asset)
├── Exchange health (API latency, error rate, status)
├── Opportunity frequency (detected, executed, profitable)
└── Risk metrics (drawdown, consecutive losses, imbalance)

Alerts (PagerDuty/Slack):
├── [CRITICAL] Unhedged position (partial fill failure)
├── [CRITICAL] Exchange balance < minimum
├── [HIGH] Circuit breaker triggered
├── [HIGH] Balance imbalance > 50%
├── [MEDIUM] API error rate > 3%
├── [MEDIUM] Daily loss > $500
├── [LOW] Execution latency > 1000ms
└── [INFO] Rebalance triggered
```

---

## 12. References

### Academic Papers

1. **Makarov, I., & Schoar, A.** (2020). "Trading and Arbitrage in Cryptocurrency Markets." *Journal of Financial Economics*, 135(2), 293-319.

2. **Kroeger, A., & Sarkar, A.** (2017). "The Law of One Bitcoin Price?" *Federal Reserve Bank of Philadelphia Working Paper*.

3. **Shleifer, A., & Vishny, R. W.** (1997). "The Limits of Arbitrage." *The Journal of Finance*, 52(1), 35-55.

4. **Budish, E., Cramton, P., & Shim, J.** (2015). "The High-Frequency Trading Arms Race: Frequent Batch Auctions as a Market Design Response." *The Quarterly Journal of Economics*, 130(4), 1547-1621.

5. **Foucault, T., Kozhan, R., & Tham, W. W.** (2017). "Toxic Arbitrage." *The Review of Financial Studies*, 30(4), 1053-1094.

6. **Hautsch, N., & Podolskij, M.** (2013). "Preaveraging-Based Estimation of Quadratic Variation in the Presence of Noise and Jumps: Theory, Implementation, and Empirical Evidence." *Journal of Business & Economic Statistics*, 31(2), 165-183.

### Exchange Documentation

- Binance API: https://binance-docs.github.io/apidocs/
- OKX API: https://www.okx.com/docs-v5/
- Bybit API: https://bybit-exchange.github.io/docs/
- Coinbase Advanced API: https://docs.cloud.coinbase.com/advanced-trade-api/
- Kraken API: https://docs.kraken.com/rest/

### Data Sources

- CoinGecko (price comparison): https://www.coingecko.com/
- CryptoCompare (multi-exchange data): https://www.cryptocompare.com/
- Kaiko (institutional market data): https://www.kaiko.com/

---

> **Related Documents:**
> - [00_overview.md](./00_overview.md) — Arbitrage Overview
> - [01_triangular_arbitrage.md](./01_triangular_arbitrage.md) — Triangular Arbitrage (single-exchange)
> - [04_mev_defi_arbitrage.md](./04_mev_defi_arbitrage.md) — MEV/DEX Arbitrage (CEX-DEX variant)
