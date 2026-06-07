# กลยุทธ์การทำตลาด (Market Making Strategies) — เอกสารอ้างอิงฉบับสมบูรณ์

## ข้อมูลเอกสาร
| ฟิลด์ | ค่า |
|---|---|
| ประเภทกลยุทธ์ | การทำตลาด / การให้สภาพคล่อง (Market Making / Liquidity Provision) |
| สินทรัพย์ | Forex, คริปโต (CEX & DEX) |
| กรอบเวลา | ต่ำกว่าวินาทีถึงนาที (High-Frequency) |
| ความซับซ้อน | สูงถึงระดับผู้เชี่ยวชาญ |
| เงินทุนที่ต้องการ | สูง |
| อัปเดตล่าสุด | 2026-04-12 |

---

## สารบัญ
1. [พื้นฐานการทำตลาด](#1-พื้นฐานการทำตลาด)
2. [การจัดการ Bid-Ask Spread](#2-การจัดการ-bid-ask-spread)
3. [การบริหารความเสี่ยงสินค้าคงคลัง](#3-การบริหารความเสี่ยงสินค้าคงคลัง)
4. [แบบจำลอง Avellaneda-Stoikov](#4-แบบจำลอง-avellaneda-stoikov)
5. [การวางราคาเสนอที่เหมาะสม](#5-การวางราคาเสนอที่เหมาะสม)
6. [การจัดการ Adverse Selection](#6-การจัดการ-adverse-selection)
7. [การทำตลาดบน CEX vs DEX](#7-การทำตลาดบน-cex-vs-dex)
8. [ข้อพิจารณา High-Frequency](#8-ข้อพิจารณา-high-frequency)
9. [ตรรกะหลัก — การเข้า/ออกสถานะ](#9-ตรรกะหลัก--การเข้าออกสถานะ)
10. [ข้อมูลจำเพาะทางเทคนิค](#10-ข้อมูลจำเพาะทางเทคนิค)
11. [แบบจำลองทางคณิตศาสตร์](#11-แบบจำลองทางคณิตศาสตร์)
12. [พารามิเตอร์ความเสี่ยง](#12-พารามิเตอร์ความเสี่ยง)
13. [ขั้นตอนการดำเนินการ](#13-ขั้นตอนการดำเนินการ)
14. [เอกสารอ้างอิง](#14-เอกสารอ้างอิง)

---

## 1. พื้นฐานการทำตลาด (Market Making Fundamentals)

### 1.1 Definition

A market maker continuously provides liquidity by posting both bid (buy) and ask (sell) limit orders on an order book. The market maker profits from the bid-ask spread while managing the inventory risk that arises from filled orders.

### 1.2 Role in Market Microstructure

| Function | Description |
|---|---|
| Liquidity Provision | Ensures other participants can trade at any time |
| Price Discovery | Continuous quoting reflects fair value assessment |
| Spread Compression | Competition among MMs narrows spreads |
| Volatility Dampening | Absorbs short-term order imbalances |

### 1.3 Revenue and Cost Model

**Revenue Sources:**
1. **Spread capture**: Buying at bid, selling at ask
2. **Maker rebates**: Exchange fees rebated to liquidity providers
3. **Information advantage**: Faster reaction to market moves

**Cost Sources:**
1. **Adverse selection**: Informed traders pick off stale quotes
2. **Inventory holding cost**: Exposure to directional moves while holding inventory
3. **Technology costs**: Infrastructure, co-location, data feeds
4. **Exchange fees**: Taker fees when hedging, maker fees on some venues

### 1.4 P&L Decomposition

$$PnL_{MM} = PnL_{spread} + PnL_{inventory} + PnL_{rebates} - Cost_{adverse} - Cost_{tech}$$

$$PnL_{spread} = N_{roundtrips} \times Q \times S_{effective}$$

Where:
- $N_{roundtrips}$ = number of completed bid-ask cycles
- $Q$ = quantity per round-trip
- $S_{effective}$ = effective spread captured (actual fill spread, not quoted)

$$PnL_{inventory} = \sum_t \Delta P_t \times I_t$$

Where $I_t$ is the inventory at time $t$ and $\Delta P_t$ is the price change.

---

## 2. การจัดการ Bid-Ask Spread

### 2.1 Components of the Spread

The bid-ask spread can be decomposed into three components (Roll, 1984; Glosten & Harris, 1988):

$$S = S_{adverse} + S_{inventory} + S_{order\_processing}$$

| Component | Description | Proportion (typical) |
|---|---|---|
| Adverse Selection ($S_{adverse}$) | Compensation for trading against informed traders | 30-50% |
| Inventory Risk ($S_{inventory}$) | Compensation for holding unbalanced inventory | 20-40% |
| Order Processing ($S_{order\_processing}$) | Fixed costs, technology, exchange fees | 10-30% |

### 2.2 Spread Setting Factors

| Factor | Effect on Spread | Reasoning |
|---|---|---|
| Higher volatility ($\sigma$) | Wider spread | More inventory risk, more adverse selection |
| Higher volume | Narrower spread | More round-trips, faster inventory turnover |
| Wider tick size | Wider spread | Minimum price increment constrains |
| More competition | Narrower spread | MM must be competitive to get fills |
| Larger inventory | Wider spread (skewed) | Need to reduce inventory |
| Higher adverse selection | Wider spread | More informed trader risk |

### 2.3 Optimal Spread Formula (Simple)

Under the assumption of a constant probability of execution:

$$S^* = 2\gamma\sigma^2 T + \frac{2}{\gamma}\ln\left(1 + \frac{\gamma}{\kappa}\right)$$

Where:
- $\gamma$ = risk aversion parameter
- $\sigma$ = volatility
- $T$ = remaining time horizon
- $\kappa$ = order arrival intensity

### 2.4 Dynamic Spread Adjustment

```
Algorithm: Dynamic Spread Sizing

INPUT:
    sigma: current realized volatility (e.g., 1-min realized vol)
    inventory: current net position
    max_inventory: maximum allowed inventory
    base_spread: minimum viable spread (covers costs)
    order_flow_imbalance: recent buy/sell ratio
    
CALCULATE:
    # Volatility component
    vol_spread = k_vol * sigma * sqrt(delta_t)
    
    # Inventory component (widen on side to reduce inventory)
    inv_ratio = abs(inventory) / max_inventory
    inv_spread = k_inv * inv_ratio * sigma
    
    # Order flow component
    if order_flow_imbalance > threshold:
        # Many buyers → widen ask, tighten bid (or vice versa)
        imbalance_adj = k_imb * (order_flow_imbalance - 1.0)
    else:
        imbalance_adj = 0
    
    # Total spread
    spread = max(base_spread, vol_spread + inv_spread)
    
    # Asymmetric adjustment
    ask_spread = spread / 2 + imbalance_adj
    bid_spread = spread / 2 - imbalance_adj
    
OUTPUT: (bid_spread, ask_spread)
```

---

## 3. การบริหารความเสี่ยงสินค้าคงคลัง (Inventory Risk Management)

### 3.1 Inventory Dynamics

Market making naturally accumulates inventory as orders are filled asymmetrically:

$$I_t = I_{t-1} + Q_{bid\_fill,t} - Q_{ask\_fill,t}$$

The inventory creates directional exposure:

$$\text{Inventory Risk} = I_t \times \sigma \times \sqrt{\Delta t}$$

### 3.2 Inventory Limits

| Inventory Level | Action | Spread Adjustment |
|---|---|---|
| $|I| < 0.3 \times I_{max}$ | Normal quoting | Symmetric spread |
| $0.3 \times I_{max} < |I| < 0.6 \times I_{max}$ | Skew quotes | Widen against inventory direction |
| $0.6 \times I_{max} < |I| < 0.9 \times I_{max}$ | Aggressive skew | Heavily favor inventory reduction |
| $|I| > 0.9 \times I_{max}$ | Market order to reduce | Take liquidity to flatten |
| $|I| > I_{max}$ | Emergency flatten | Immediate market order, cancel all |

### 3.3 Inventory Skewing

To reduce inventory, skew the quotes away from market center:

$$P_{bid} = P_{mid} - \frac{S}{2} - \alpha \times I_t$$
$$P_{ask} = P_{mid} + \frac{S}{2} - \alpha \times I_t$$

Where $\alpha$ is the inventory sensitivity parameter.

Effect:
- **Long inventory** ($I > 0$): Both bid and ask shift downward → more likely to sell → inventory reduces
- **Short inventory** ($I < 0$): Both bid and ask shift upward → more likely to buy → inventory reduces

### 3.4 Inventory Mean Reversion Target

$$\text{Target Inventory} = 0 \quad (\text{zero inventory target, most common})$$

Or for carry-aware MM:

$$\text{Target Inventory} = I^* = \frac{\mu}{\gamma\sigma^2}$$

Where $\mu$ is the expected drift (e.g., positive for an asset expected to appreciate).

### 3.5 Hedging Strategies

| Strategy | Description | Cost |
|---|---|---|
| Internal hedging | Offset inventory across multiple pairs | Low |
| Futures hedging | Hedge spot inventory with futures short | Funding cost |
| Cross-exchange hedging | Offset on another venue | Spread + fees |
| Options hedging | Buy puts/calls for tail risk | Premium |
| Periodic flattening | Market order to zero every N minutes | Spread crossing |

---

## 4. แบบจำลอง Avellaneda-Stoikov

### 4.1 The Model

The **Avellaneda-Stoikov (2008)** model is the foundational continuous-time framework for optimal market making. It solves for optimal bid and ask quotes that maximize expected utility of terminal wealth.

### 4.2 Model Setup

**Price Process:**

$$dS_t = \sigma dW_t$$

(Arithmetic Brownian motion — no drift assumption for the reference price.)

**Inventory Process:**

$$dI_t = dN_t^{bid} - dN_t^{ask}$$

Where $N_t^{bid}$ and $N_t^{ask}$ are Poisson processes for order arrivals at the market maker's quotes.

**Order Arrival Intensity:**

The probability of a market order hitting the MM's quote decreases with the distance from mid-price:

$$\lambda^{bid}(\delta^{bid}) = A \exp(-\kappa \delta^{bid})$$
$$\lambda^{ask}(\delta^{ask}) = A \exp(-\kappa \delta^{ask})$$

Where:
- $\delta^{bid}$ = distance of bid below mid-price
- $\delta^{ask}$ = distance of ask above mid-price
- $A$ = base arrival rate
- $\kappa$ = decay parameter (market order sensitivity to price)

### 4.3 Optimal Quotes — Closed-Form Solution

The optimal bid and ask offsets from the "indifference price" are:

$$\delta^{bid*} = \delta^{ask*} = \frac{1}{\gamma}\ln\left(1 + \frac{\gamma}{\kappa}\right) + \frac{(2q+1)\gamma\sigma^2(T-t)}{2}$$

Wait — more precisely, the full Avellaneda-Stoikov solution gives:

**Reservation (Indifference) Price:**

$$r_t = S_t - q\gamma\sigma^2(T-t)$$

Where:
- $q$ = current inventory (positive = long, negative = short)
- $\gamma$ = risk aversion parameter
- $\sigma$ = volatility
- $T-t$ = time remaining until end of trading period

**Optimal Spread (symmetric component):**

$$\delta^{bid*} = \delta^{ask*} = \frac{1}{\gamma}\ln\left(1+\frac{\gamma}{\kappa}\right) + \frac{\gamma\sigma^2(T-t)}{2}$$

**Optimal Bid and Ask Prices:**

$$P_{bid}^* = r_t - \delta^{bid*} = S_t - q\gamma\sigma^2(T-t) - \frac{1}{\gamma}\ln\left(1+\frac{\gamma}{\kappa}\right) - \frac{\gamma\sigma^2(T-t)}{2}$$

$$P_{ask}^* = r_t + \delta^{ask*} = S_t - q\gamma\sigma^2(T-t) + \frac{1}{\gamma}\ln\left(1+\frac{\gamma}{\kappa}\right) + \frac{\gamma\sigma^2(T-t)}{2}$$

### 4.4 Parameter Interpretation

| Parameter | Meaning | Effect of Increasing |
|---|---|---|
| $\gamma$ | Risk aversion | Wider spread, faster inventory reduction |
| $\kappa$ | Order arrival sensitivity | Narrower optimal spread (more arrivals per unit spread) |
| $\sigma$ | Volatility | Wider spread (more inventory risk) |
| $T-t$ | Time remaining | Wider spread early, narrows near end |
| $q$ | Inventory | Shifts reservation price away from mid |

### 4.5 Practical Implementation

```python
class AvellanedaStoikov:
    """
    Implementation of the Avellaneda-Stoikov market making model.
    """
    
    def __init__(self, gamma, kappa, sigma, T):
        """
        gamma: Risk aversion parameter (higher = wider spread, less inventory)
        kappa: Order arrival decay rate
        sigma: Volatility (annualized or per-period, must be consistent with T)
        T: Trading horizon (e.g., 1.0 for one trading day)
        """
        self.gamma = gamma
        self.kappa = kappa
        self.sigma = sigma
        self.T = T
        
    def reservation_price(self, mid_price, inventory, time_remaining):
        """
        Calculate the reservation (indifference) price.
        Shifts away from mid based on inventory risk.
        """
        return mid_price - inventory * self.gamma * self.sigma**2 * time_remaining
    
    def optimal_spread(self, time_remaining):
        """
        Calculate the optimal symmetric spread component.
        """
        spread = (1.0 / self.gamma) * np.log(1 + self.gamma / self.kappa)
        spread += 0.5 * self.gamma * self.sigma**2 * time_remaining
        return spread
    
    def optimal_quotes(self, mid_price, inventory, time_remaining):
        """
        Calculate optimal bid and ask prices.
        
        Returns: (bid_price, ask_price, reservation_price, spread)
        """
        r = self.reservation_price(mid_price, inventory, time_remaining)
        delta = self.optimal_spread(time_remaining)
        
        bid = r - delta
        ask = r + delta
        
        return {
            'bid': bid,
            'ask': ask,
            'reservation_price': r,
            'spread': ask - bid,
            'mid_offset': r - mid_price  # How far reservation is from mid
        }
    
    def update_parameters(self, realized_vol, arrival_rate, fill_rate):
        """
        Dynamically update model parameters based on market conditions.
        """
        # Update volatility estimate
        self.sigma = realized_vol
        
        # Update kappa based on observed fill rate vs spread
        # kappa = -ln(fill_rate / A) / delta
        if fill_rate > 0 and self.last_delta > 0:
            self.kappa = -np.log(fill_rate / arrival_rate) / self.last_delta
```

### 4.6 Extensions of Avellaneda-Stoikov

| Extension | Modification | Author(s) |
|---|---|---|
| Multi-asset MM | Multiple correlated assets | Gueant, Lehalle, Fernandez-Tapia (2013) |
| Non-zero drift | GBM instead of ABM | Cartea, Jaimungal (2015) |
| Adverse selection | Informed trader probability | Cartea, Donnelly, Jaimungal (2018) |
| Order book dynamics | LOB simulation | Cont, Stoikov, Talreja (2010) |
| Regime-switching | Time-varying $\sigma$, $\kappa$ | Fodra, Pham (2015) |

---

## 5. การวางราคาเสนอที่เหมาะสม (Optimal Quote Placement)

### 5.1 Order Book Level Placement

The market maker must decide not just the spread, but the exact price levels to quote:

**Tick-Constrained Quotes:**

$$P_{bid}^{actual} = \text{floor}(P_{bid}^{optimal} / \text{tick}) \times \text{tick}$$
$$P_{ask}^{actual} = \text{ceil}(P_{ask}^{optimal} / \text{tick}) \times \text{tick}$$

### 5.2 Queue Priority Considerations

On exchanges with price-time priority:
- Being first in the queue at a price level is crucial
- Canceling and re-placing loses queue position
- Strategy: Place orders early, adjust only when necessary

**Queue Position Value:**

$$V_{queue} = P(\text{fill within } \Delta t) \times E[\text{profit if filled}]$$

$$P(\text{fill}) = \frac{\text{Position in queue}}{\text{Queue depth}} \times P(\text{market order arrives at this level})$$

### 5.3 Multiple Level Quoting

Quote at multiple price levels to capture different types of flow:

```
MULTI-LEVEL QUOTING STRATEGY:

Level 1 (Inside Bid/Ask): 
    Quantity: 30% of total
    Spread: Minimum viable (1-2 ticks above cost)
    Purpose: Capture regular flow, maintain BBO presence

Level 2 (One level deeper):
    Quantity: 40% of total
    Spread: 2-3x Level 1
    Purpose: Capture larger orders that sweep Level 1

Level 3 (Deep book):
    Quantity: 30% of total
    Spread: 4-5x Level 1
    Purpose: Capture aggressive sweeps, wider profit per fill
```

### 5.4 Order Size Optimization

$$Q_{optimal}(level) = \frac{\text{Target Fill Rate} \times \text{Expected Volume at Level}}{\text{Total Volume}}$$

**Constraints:**
- Minimum order size: Exchange minimum
- Maximum order size: < 10% of visible depth at that level (avoid manipulation detection)
- Total inventory limit: Sum of all quoted quantities < maximum inventory

---

## 6. การจัดการ Adverse Selection

### 6.1 Definition

Adverse selection occurs when a market maker's quotes are filled by informed traders who possess superior information about future price direction. The MM then holds inventory at an unfavorable price.

### 6.2 Detecting Adverse Selection

**Indicators of Adverse Selection:**

| Signal | Detection Method | Action |
|---|---|---|
| Large order flow imbalance | Buy/sell volume ratio > threshold | Widen spread, skew quotes |
| Price moving through levels | Multiple levels swept in same direction | Cancel all, reassess |
| Fills on one side only | Consecutive same-side fills > threshold | Pull that side's quotes |
| Post-fill adverse move | Average mark-to-market P&L per fill < 0 | Widen spread |
| Correlation with other markets | Lagged correlation with index/BTC | Pre-empt with faster signals |

### 6.3 Adverse Selection Cost Estimation

$$C_{adverse} = E[P_{fill} - P_{mid,after}]$$

Where $P_{mid,after}$ is the mid-price shortly after the fill (e.g., 1 second, 10 seconds, 1 minute).

If the mid-price consistently moves against the MM after fills, the adverse selection cost is positive.

**Glosten-Milgrom decomposition:**

$$S = 2\lambda(V_H - V_L) + 2(1-\lambda) \times 0$$

Where:
- $\lambda$ = probability the counterparty is informed
- $V_H$ = true value conditional on buy (informed buyer knows value is high)
- $V_L$ = true value conditional on sell

### 6.4 Anti-Adverse-Selection Strategies

```
1. LATENCY PROTECTION:
   - Monitor reference price feeds (multiple exchanges)
   - If reference price moves > threshold before our fill:
     → Cancel quote immediately (stale quote protection)
   - "Last look" equivalent for crypto MM

2. FLOW TOXICITY DETECTION (VPIN):
   Volume-synchronized Probability of Informed Trading:
   VPIN = |V_buy - V_sell| / (V_buy + V_sell)
   
   IF VPIN > 0.5: Widen spread by 50%
   IF VPIN > 0.7: Pull quotes entirely

3. ADAPTIVE SPREAD:
   - Track rolling win/loss ratio of fills
   - IF win_rate < 40% over last 100 fills:
     → Adverse selection detected
     → Widen minimum spread by 20%
   - IF win_rate > 60%:
     → Low adverse selection
     → Can tighten spread

4. ORDER FLOW PREDICTION:
   - Use ML model to predict next market order direction
   - IF P(next_order = buy) > 0.7:
     → Widen ask, tighten bid
   - Features: recent trade sequence, order book imbalance,
     correlated asset moves, time of day
```

### 6.5 VPIN (Volume-Synchronized Probability of Informed Trading)

$$VPIN = \frac{\sum_{\tau=1}^{n} |V_{B,\tau} - V_{S,\tau}|}{n \times V_{bar}}$$

Where:
- $V_{B,\tau}$ = buy volume in bar $\tau$ (classified by trade direction)
- $V_{S,\tau}$ = sell volume in bar $\tau$
- $V_{bar}$ = volume per bar (volume bars, not time bars)
- $n$ = number of bars in estimation window

**VPIN Thresholds:**

| VPIN Level | Interpretation | MM Action |
|---|---|---|
| < 0.3 | Low toxicity | Normal quoting, tight spread |
| 0.3 - 0.5 | Moderate toxicity | Slightly wider spread |
| 0.5 - 0.7 | High toxicity | Wide spread, reduced size |
| > 0.7 | Extreme toxicity | Pull quotes, wait for calm |

---

## 7. การทำตลาดบน CEX vs DEX

### 7.1 Centralized Exchange (CEX) Market Making

**Venues:** Binance, OKX, Bybit, Coinbase, Kraken

**Order Book Structure:** Central Limit Order Book (CLOB)

| Feature | Description |
|---|---|
| Order Types | Limit, Market, IOC, FOK, Post-Only |
| Matching Engine | Price-Time priority |
| Latency | 1-50ms (co-located: <1ms) |
| Fees | Maker: -0.01% to 0.02%, Taker: 0.03-0.10% |
| Risk | Exchange counterparty risk, liquidation risk |
| Inventory | Held on exchange (hot wallet) |
| Data | Real-time L2/L3 order book, trades |

**CEX MM Strategy:**

```yaml
cex_market_making:
  venue: Binance
  pair: BTC/USDT
  
  quoting:
    spread_model: avellaneda_stoikov
    gamma: 0.1
    kappa: estimated from fill data
    min_spread_bps: 2  # Minimum 0.02%
    levels: 3
    refresh_rate_ms: 100  # Update quotes every 100ms
    
  inventory:
    max_inventory_usd: 50000
    target_inventory: 0
    skew_factor: 0.5  # bps per $1000 of inventory
    flatten_threshold: 0.8  # Flatten at 80% of max
    
  risk:
    max_loss_per_hour: 500 USD
    kill_switch_loss: 2000 USD (daily)
    max_adverse_fill_streak: 10
```

### 7.2 Decentralized Exchange (DEX) Market Making

**Venues:** Uniswap, Curve, Raydium, dYdX (v4)

**Two Types:**

**A. AMM-Based (Uniswap, Curve):**

Providing liquidity to automated market maker pools:

$$x \times y = k \quad (\text{Uniswap V2: constant product})$$

$$\text{Impermanent Loss} = 2\frac{\sqrt{r}}{1+r} - 1$$

Where $r = P_{new}/P_{old}$ is the price ratio since deposit.

| Feature | Description |
|---|---|
| Order Type | Liquidity provision (LP tokens) |
| Matching | Algorithm-based (AMM formula) |
| Latency | Block time (12s on ETH, 0.4s on Solana) |
| Fees | 0.01% - 1.0% of swap volume (earned by LPs) |
| Risk | Impermanent loss, smart contract risk |
| Capital | Always fully utilized (no idle capital) |
| Range | Concentrated (V3) or full-range (V2) |

**B. Order Book DEX (dYdX v4, Serum successor):**

Similar to CEX but on-chain/appchain:

| Feature | Description |
|---|---|
| Order Type | Limit orders on-chain |
| Matching | Price-Time (same as CEX) |
| Latency | 1-2 seconds (appchain: 100ms) |
| Fees | Maker: 0-0.02%, Taker: 0.02-0.05% |
| Risk | Smart contract risk, gas costs |

### 7.3 CEX vs DEX Comparison for Market Makers

| Dimension | CEX | DEX (AMM) | DEX (Order Book) |
|---|---|---|---|
| Capital Efficiency | High (leverage) | Medium (concentrated) | High |
| Latency | <50ms | 1-12 seconds | 100ms-2s |
| Adverse Selection | Moderate | High (MEV/sandwiching) | Lower (private mempool) |
| Counterparty Risk | Exchange risk | Smart contract risk | Smart contract risk |
| Transparency | Opaque (exchange controls) | Fully transparent | Mostly transparent |
| KYC Required | Yes | No | Usually No |
| Maker Rebates | Yes | Pool fees | Yes |

### 7.4 DEX-Specific Risks

| Risk | Description | Mitigation |
|---|---|---|
| Impermanent Loss | Price divergence reduces LP value | Active rebalancing, concentrated ranges |
| MEV/Sandwich Attacks | Frontrunning/backrunning LP transactions | Private mempools, Flashbots |
| Smart Contract Bugs | Code vulnerability leading to fund loss | Audit, insurance, diversification |
| Gas Costs | High gas erodes profits (Ethereum) | L2, Solana, or batch transactions |
| Oracle Manipulation | Price oracle attacks affecting pools | Use TWAP oracles, multiple sources |

---

## 8. ข้อพิจารณาสำหรับ High-Frequency

### 8.1 Latency Requirements

| Activity | Acceptable Latency | Impact of Extra 1ms |
|---|---|---|
| Quote update | < 10ms | 5-10% fewer fills at best price |
| Cancel stale quote | < 5ms | Increased adverse selection |
| Hedge execution | < 50ms | Inventory risk |
| Market data processing | < 1ms | Stale signals |
| Risk check | < 1ms | Cannot afford delay |

### 8.2 Infrastructure Requirements

```yaml
hft_infrastructure:
  connectivity:
    - Co-location at exchange datacenter
    - Low-latency network (kernel bypass, FPGA NIC)
    - Multiple redundant connections
    - Direct market access (DMA)
    
  hardware:
    - FPGA for order routing (sub-microsecond)
    - High-clock-speed CPUs for strategy logic
    - Sufficient RAM for in-memory order book
    - NVMe storage for logging
    
  software:
    - Lock-free data structures
    - Zero-garbage-collection languages (C++, Rust)
    - Custom networking stack (bypass kernel)
    - Deterministic execution paths
    
  data:
    - Full L3 order book (individual orders)
    - Trade-by-trade feed (tick data)
    - Cross-exchange aggregated feed
    - News/event feed (sub-second delivery)
```

### 8.3 Crypto-Specific HFT Considerations

| Factor | Impact | Strategy |
|---|---|---|
| 24/7 markets | No overnight break | Automated monitoring, redundancy |
| Multiple exchanges | Latency varies per venue | Priority-based venue routing |
| WebSocket limits | Rate limiting on connections | Efficient message parsing |
| API rate limits | 1000-6000 requests/minute typically | Batch updates, smart throttling |
| Blockchain latency | DEX inherently slow | Focus on CEX for speed-sensitive |
| Mempool visibility | Others see pending DEX txns | Private transactions, MEV protection |

### 8.4 Market Maker Performance Metrics (HFT)

| Metric | Definition | Target |
|---|---|---|
| Fill Rate | Orders filled / Orders placed | 5-30% |
| Capture Ratio | Realized spread / Quoted spread | > 50% |
| Position Turnover | Volume / Avg position size | > 10x per hour |
| Adverse Selection | Post-fill mid-price move against MM | < 30% of spread |
| Time at BBO | % of time with best bid or offer | > 50% |
| Quote Uptime | % of time quotes are live | > 99.5% |
| Sharpe Ratio (daily) | Daily P&L / Daily P&L std | > 3.0 |

---

## 9. ตรรกะหลัก — การเข้า/ออกสถานะ (Core Logic — Entry/Exit)

### 9.1 Market Making Core Logic

Unlike directional strategies, market making does not have traditional "entry" and "exit." Instead, it continuously quotes bid and ask, and manages the resulting inventory.

```
Algorithm: Core Market Making Loop

INITIALIZATION:
    Set parameters: gamma, kappa, sigma, max_inventory, min_spread
    Initialize inventory = 0
    Initialize P&L tracking
    
CONTINUOUS LOOP (every tick_interval):

    1. UPDATE MARKET STATE:
       mid_price = get_mid_price()
       sigma = estimate_volatility(recent_trades, method='realized')
       kappa = estimate_arrival_rate(recent_fills)
       order_flow = compute_order_flow_imbalance()
       vpin = compute_vpin()
       
    2. RISK CHECKS:
       IF |inventory| > max_inventory:
           ACTION: Flatten immediately (market order)
           GOTO STEP 1
       IF daily_pnl < kill_switch_threshold:
           ACTION: Cancel all orders, halt trading
           ALERT: "Kill switch triggered"
           HALT
       IF vpin > toxicity_threshold:
           ACTION: Pull all quotes
           WAIT until vpin < safe_threshold
           GOTO STEP 1
    
    3. CALCULATE OPTIMAL QUOTES (Avellaneda-Stoikov):
       time_remaining = T - elapsed_time
       reservation_price = mid_price - inventory * gamma * sigma^2 * time_remaining
       spread = (1/gamma) * ln(1 + gamma/kappa) + 0.5 * gamma * sigma^2 * time_remaining
       
       bid_price = reservation_price - spread
       ask_price = reservation_price + spread
       
       # Enforce minimum spread
       IF (ask_price - bid_price) < min_spread:
           ask_price = mid_price + min_spread / 2
           bid_price = mid_price - min_spread / 2
       
       # Enforce tick size
       bid_price = floor_to_tick(bid_price)
       ask_price = ceil_to_tick(ask_price)
    
    4. CALCULATE ORDER SIZES:
       base_size = target_fill_rate * expected_volume / refresh_rate
       
       # Adjust for inventory
       IF inventory > 0:  # Long: want to sell more
           ask_size = base_size * (1 + inv_skew_factor * inventory/max_inventory)
           bid_size = base_size * (1 - inv_skew_factor * inventory/max_inventory)
       ELSE:  # Short: want to buy more
           bid_size = base_size * (1 + inv_skew_factor * abs(inventory)/max_inventory)
           ask_size = base_size * (1 - inv_skew_factor * abs(inventory)/max_inventory)
    
    5. UPDATE QUOTES:
       IF existing quotes are within tolerance of new quotes:
           DO NOTHING (preserve queue position)
       ELSE:
           Cancel existing orders
           Place new bid at bid_price, quantity = bid_size
           Place new ask at ask_price, quantity = ask_size
    
    6. HANDLE FILLS:
       FOR each new fill:
           IF fill is BID (we bought):
               inventory += fill_quantity
               record_buy(fill_price, fill_quantity)
           IF fill is ASK (we sold):
               inventory -= fill_quantity
               record_sell(fill_price, fill_quantity)
           
           # Immediate quote update after fill
           TRIGGER quote recalculation
           
           # Track spread capture
           IF completed a round-trip (buy + sell matched):
               realized_pnl += (sell_price - buy_price) * quantity - fees
               
    7. LOG AND MONITOR:
       Log: mid_price, bid, ask, spread, inventory, realized_pnl, unrealized_pnl
       
    REPEAT from STEP 1
```

### 9.2 Quote Management State Machine

```
States:
    QUOTING_NORMAL    - Both bid and ask live, symmetric or mildly skewed
    QUOTING_SKEWED    - Heavy inventory; aggressive skew to one side
    QUOTES_PULLED     - No quotes live (high toxicity, news event)
    FLATTENING        - Using market orders to reduce inventory
    HALTED            - Kill switch activated; no activity

Transitions:
    QUOTING_NORMAL -> QUOTING_SKEWED:
        |inventory| > 0.5 * max_inventory
        
    QUOTING_NORMAL -> QUOTES_PULLED:
        VPIN > 0.7 OR news_event OR exchange_issue
        
    QUOTING_SKEWED -> FLATTENING:
        |inventory| > 0.9 * max_inventory
        
    QUOTING_SKEWED -> QUOTING_NORMAL:
        |inventory| < 0.3 * max_inventory
        
    QUOTES_PULLED -> QUOTING_NORMAL:
        VPIN < 0.4 AND no_news AND exchange_ok
        
    FLATTENING -> QUOTING_NORMAL:
        |inventory| < 0.2 * max_inventory
        
    ANY -> HALTED:
        daily_pnl < kill_switch OR system_error
```

---

## 10. ข้อมูลจำเพาะทางเทคนิค (Technical Specifications)

### 10.1 System Configuration

```yaml
market_making_config:
  # Model Parameters
  model:
    type: avellaneda_stoikov
    gamma: 0.1                    # Risk aversion
    kappa: 1.5                    # Order arrival rate decay
    sigma_window: 300             # 5-minute window for vol estimation (seconds)
    T: 86400                      # Trading horizon (seconds in a day)
    
  # Quoting Parameters
  quoting:
    min_spread_bps: 2             # Minimum spread (basis points)
    max_spread_bps: 50            # Maximum spread (cap)
    tick_size: 0.01               # Minimum price increment
    levels: 3                     # Number of quote levels per side
    size_per_level: [0.3, 0.4, 0.3]  # Size distribution across levels
    quote_refresh_ms: 200         # Minimum time between quote updates
    queue_tolerance_bps: 0.5      # Don't update if change < this
    
  # Inventory Management
  inventory:
    max_inventory_base: 1.0       # Maximum inventory in base currency
    max_inventory_usd: 50000      # Maximum inventory in USD
    target_inventory: 0.0         # Target inventory level
    skew_factor: 0.3              # BPS adjustment per unit of normalized inventory
    flatten_threshold: 0.9        # Flatten at 90% of max
    flatten_method: market        # Use market orders to flatten
    
  # Risk Controls
  risk:
    max_loss_per_hour_usd: 200    
    max_loss_daily_usd: 1000      
    max_adverse_streak: 15        # Consecutive adverse fills
    vpin_pull_threshold: 0.70     
    vpin_resume_threshold: 0.40   
    max_position_time_s: 300      # Force flatten after 5 min holding
    
  # Execution
  execution:
    order_type: POST_ONLY         # Ensure maker fills only
    cancel_on_disconnect: true    # Auto-cancel if connection drops
    heartbeat_interval_ms: 1000   # Exchange heartbeat
    max_open_orders: 20           # Maximum simultaneous orders
```

### 10.2 Performance Benchmarks

| Metric | Minimum | Good | Excellent |
|---|---|---|---|
| Daily Sharpe | 1.0 | 3.0 | 5.0+ |
| Win Rate (per fill) | 45% | 55% | 65% |
| Capture Ratio | 30% | 50% | 70% |
| Max Hourly DD | < 0.5% | < 0.2% | < 0.1% |
| Inventory Turnover | 5x/hr | 15x/hr | 30x/hr |
| Uptime | 95% | 99% | 99.9% |
| Fill-to-Adverse Ratio | 1.0 | 1.5 | 2.0+ |

---

## 11. แบบจำลองทางคณิตศาสตร์ (Mathematical Models)

### 11.1 Spread Decomposition (Kyle, 1985)

In Kyle's model with a single informed trader:

$$\lambda = \frac{1}{2}\sqrt{\frac{\sigma_v^2}{\sigma_u^2}}$$

Where:
- $\lambda$ = Kyle's lambda (price impact per unit of order flow)
- $\sigma_v^2$ = variance of fundamental value changes
- $\sigma_u^2$ = variance of noise trader order flow

The spread is proportional to $\lambda$:

$$S \propto \lambda$$

### 11.2 Glosten-Milgrom (1985) Sequential Trade Model

The bid and ask prices account for the probability of informed trading:

$$A_t = E[V | \text{buy order}] = (1-\pi)V_{public} + \pi V_H$$
$$B_t = E[V | \text{sell order}] = (1-\pi)V_{public} + \pi V_L$$

Where:
- $\pi$ = probability the counterparty is informed
- $V_H$ = value if informed buyer (knows it's worth more)
- $V_L$ = value if informed seller (knows it's worth less)

Spread due to adverse selection:

$$S_{adverse} = A_t - B_t = \pi(V_H - V_L)$$

### 11.3 Expected P&L per Quote Cycle

$$E[PnL_{cycle}] = P(\text{roundtrip}) \times S_{effective} - P(\text{adverse}) \times L_{adverse}$$

Where:
- $P(\text{roundtrip})$ = probability both bid and ask fill (completing a round-trip)
- $S_{effective}$ = actual spread captured
- $P(\text{adverse})$ = probability of adverse selection event
- $L_{adverse}$ = average loss from adverse selection

### 11.4 Optimal Gamma Selection

The risk aversion parameter $\gamma$ can be calibrated based on target Sharpe ratio:

$$\gamma^* = \frac{\sigma}{\sqrt{V_0 \times SR_{target}^2 / N_{trades}}}$$

Where:
- $V_0$ = initial capital
- $SR_{target}$ = desired Sharpe ratio
- $N_{trades}$ = expected number of round-trips

### 11.5 Inventory P&L Variance

$$\text{Var}(PnL_{inventory}) = \sigma^2 \sum_t I_t^2 \Delta t$$

To keep inventory P&L variance bounded:

$$\bar{I}^2 \leq \frac{\text{Max Var}_{allowed}}{\sigma^2 T}$$

This gives the maximum average squared inventory (MSI) constraint.

### 11.6 Mean-Variance Optimal Market Making

The market maker maximizes:

$$\max_{(\delta^b, \delta^a)} E[W_T] - \frac{\gamma}{2}\text{Var}(W_T)$$

Subject to:
- Inventory constraints: $|I_t| \leq I_{max}$
- Spread constraints: $\delta^b, \delta^a \geq \delta_{min}$
- Fill rate constraints: Expected fills > minimum threshold

---

## 12. พารามิเตอร์ความเสี่ยง (Risk Parameters)

### 12.1 Position Limits

| Parameter | Conservative | Moderate | Aggressive |
|---|---|---|---|
| Max Inventory (USD) | $10,000 | $50,000 | $200,000 |
| Max Inventory (% of capital) | 10% | 25% | 50% |
| Max Position Time | 60s | 300s | 1800s |
| Flatten Trigger | 60% of max | 80% of max | 90% of max |

### 12.2 P&L-Based Controls

```yaml
pnl_controls:
  # Kill switches
  daily_loss_limit: -1000 USD     # Stop trading for the day
  hourly_loss_limit: -300 USD     # Pause for 15 minutes
  per_fill_loss_limit: -50 USD    # Alert and widen spread
  
  # Profit targets (optional)
  daily_profit_target: 2000 USD   # Consider reducing size after target
  
  # Drawdown from peak
  intraday_max_dd: -500 USD       # Reduce size by 50%
  
  # Consecutive loss handling
  consecutive_loss_count: 5       # After 5 consecutive losing fills
  consecutive_loss_action: widen_spread_50%
```

### 12.3 Market Condition Triggers

| Condition | Detection | Action |
|---|---|---|
| Flash crash | Price moves > 5% in 1 minute | Pull all quotes immediately |
| Exchange outage | No heartbeat for > 5s | Cancel all, switch venue |
| Extreme volatility | Realized vol > 3x normal | Widen spread 3x, reduce size |
| Low liquidity | Book depth < threshold | Widen spread, reduce size |
| News event | Calendar + NLP detection | Pull quotes 30s before, 60s after |
| System lag | Quote update latency > 500ms | Pull quotes until latency resolves |

### 12.4 Counterparty and Venue Risk

| Risk | Limit | Action |
|---|---|---|
| Single exchange exposure | < 30% of total MM capital | Diversify across venues |
| Hot wallet balance | < 50% of total capital | Keep rest in cold storage |
| Withdrawal cooldown | Test withdrawals daily | Immediate escalation if delayed |
| API key compromise | Separate keys per bot | IP whitelist, regular rotation |

---

## 13. ขั้นตอนการดำเนินการ (Execution Flow)

### 13.1 Complete Market Making System — Pseudocode

```python
class MarketMakingSystem:
    """
    Complete Market Making System
    Model: Avellaneda-Stoikov with extensions
    Markets: Crypto CEX
    """
    
    def __init__(self, config):
        self.config = config
        self.model = AvellanedaStoikov(
            gamma=config['gamma'],
            kappa=config['kappa'],
            sigma=config['initial_sigma'],
            T=config['T']
        )
        self.inventory = 0.0
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.open_orders = {}  # order_id -> order_info
        self.fill_history = []
        self.state = 'QUOTING_NORMAL'
        self.start_time = time.time()
        
    def estimate_parameters(self, recent_data):
        """Estimate model parameters from recent market data."""
        # Realized volatility (per-second, then scale)
        returns = np.diff(np.log(recent_data['mid_prices']))
        sigma = np.std(returns) * np.sqrt(1.0 / self.config['tick_interval_s'])
        
        # Order arrival rate
        recent_fills = [f for f in self.fill_history if f['time'] > time.time() - 300]
        if len(recent_fills) > 0:
            avg_spread_at_fill = np.mean([f['distance_from_mid'] for f in recent_fills])
            fill_rate = len(recent_fills) / 300.0  # fills per second
            # kappa = -ln(fill_rate / base_rate) / avg_distance
            kappa = max(0.1, -np.log(fill_rate / self.config['base_arrival_rate']) / avg_spread_at_fill)
        else:
            kappa = self.config['kappa']
        
        # VPIN
        buy_volume = sum(t['qty'] for t in recent_data['trades'] if t['side'] == 'buy')
        sell_volume = sum(t['qty'] for t in recent_data['trades'] if t['side'] == 'sell')
        total_volume = buy_volume + sell_volume
        vpin = abs(buy_volume - sell_volume) / total_volume if total_volume > 0 else 0
        
        return sigma, kappa, vpin
    
    def calculate_quotes(self, mid_price, sigma, kappa, time_remaining):
        """Calculate optimal bid and ask prices."""
        # Update model parameters
        self.model.sigma = sigma
        self.model.kappa = kappa
        
        # Get Avellaneda-Stoikov optimal quotes
        result = self.model.optimal_quotes(mid_price, self.inventory, time_remaining)
        
        bid_price = result['bid']
        ask_price = result['ask']
        
        # Enforce minimum spread
        min_spread = mid_price * self.config['min_spread_bps'] / 10000
        if (ask_price - bid_price) < min_spread:
            ask_price = mid_price + min_spread / 2
            bid_price = mid_price - min_spread / 2
        
        # Enforce maximum spread
        max_spread = mid_price * self.config['max_spread_bps'] / 10000
        if (ask_price - bid_price) > max_spread:
            ask_price = mid_price + max_spread / 2
            bid_price = mid_price - max_spread / 2
        
        # Round to tick size
        tick = self.config['tick_size']
        bid_price = math.floor(bid_price / tick) * tick
        ask_price = math.ceil(ask_price / tick) * tick
        
        return bid_price, ask_price
    
    def calculate_sizes(self, bid_price, ask_price):
        """Calculate order sizes with inventory skewing."""
        base_size = self.config['base_order_size']
        inv_ratio = self.inventory / self.config['max_inventory']
        skew = self.config['skew_factor']
        
        # Skew sizes to favor inventory reduction
        bid_size = base_size * (1 - skew * inv_ratio)
        ask_size = base_size * (1 + skew * inv_ratio)
        
        # Clamp to min/max
        bid_size = max(self.config['min_order_size'], min(bid_size, self.config['max_order_size']))
        ask_size = max(self.config['min_order_size'], min(ask_size, self.config['max_order_size']))
        
        # Don't increase inventory beyond max
        if self.inventory + bid_size > self.config['max_inventory']:
            bid_size = max(0, self.config['max_inventory'] - self.inventory)
        if -self.inventory + ask_size > self.config['max_inventory']:
            ask_size = max(0, self.config['max_inventory'] + self.inventory)
        
        return bid_size, ask_size
    
    def should_update_quotes(self, new_bid, new_ask, new_bid_size, new_ask_size):
        """Determine if quotes should be updated (preserve queue position)."""
        if not self.open_orders:
            return True
            
        current_bid = self.open_orders.get('bid', {}).get('price', 0)
        current_ask = self.open_orders.get('ask', {}).get('price', float('inf'))
        
        tolerance = self.config['queue_tolerance_bps'] / 10000
        
        bid_change = abs(new_bid - current_bid) / current_bid if current_bid > 0 else 1.0
        ask_change = abs(new_ask - current_ask) / current_ask if current_ask > 0 else 1.0
        
        return bid_change > tolerance or ask_change > tolerance
    
    def handle_fill(self, fill):
        """Process a filled order."""
        if fill['side'] == 'buy':
            self.inventory += fill['quantity']
            self.fill_history.append({
                'time': time.time(),
                'side': 'buy',
                'price': fill['price'],
                'qty': fill['quantity'],
                'distance_from_mid': abs(fill['mid_at_fill'] - fill['price'])
            })
        else:  # sell
            self.inventory -= fill['quantity']
            self.fill_history.append({
                'time': time.time(),
                'side': 'sell',
                'price': fill['price'],
                'qty': fill['quantity'],
                'distance_from_mid': abs(fill['price'] - fill['mid_at_fill'])
            })
        
        # Check for completed round-trips
        self.match_fills_fifo()
        
        # Immediate re-quote after fill
        self.trigger_requote = True
    
    def risk_check(self, mid_price, vpin):
        """Perform risk checks and update state."""
        # Kill switch
        total_pnl = self.realized_pnl + self.inventory * (mid_price - self.avg_entry_price())
        if total_pnl < self.config['daily_loss_limit']:
            self.state = 'HALTED'
            self.cancel_all_orders()
            return False
        
        # VPIN toxicity
        if vpin > self.config['vpin_pull_threshold']:
            self.state = 'QUOTES_PULLED'
            self.cancel_all_orders()
            return False
        
        # Inventory check
        if abs(self.inventory) > self.config['flatten_threshold'] * self.config['max_inventory']:
            self.state = 'FLATTENING'
            self.flatten_inventory(mid_price)
            return False
        
        # Resume normal if pulled
        if self.state == 'QUOTES_PULLED' and vpin < self.config['vpin_resume_threshold']:
            self.state = 'QUOTING_NORMAL'
        
        return True
    
    def run(self, market_data_feed):
        """Main market making loop."""
        self.state = 'QUOTING_NORMAL'
        
        for tick in market_data_feed:
            # 1. Get current market state
            mid_price = tick['mid_price']
            time_remaining = max(0.001, self.config['T'] - (time.time() - self.start_time))
            
            # 2. Estimate parameters
            sigma, kappa, vpin = self.estimate_parameters(tick['recent_data'])
            
            # 3. Risk checks
            if not self.risk_check(mid_price, vpin):
                continue
            
            # 4. Handle any new fills
            for fill in tick.get('new_fills', []):
                self.handle_fill(fill)
            
            # 5. Calculate optimal quotes
            if self.state in ['QUOTING_NORMAL', 'QUOTING_SKEWED']:
                bid_price, ask_price = self.calculate_quotes(mid_price, sigma, kappa, time_remaining)
                bid_size, ask_size = self.calculate_sizes(bid_price, ask_price)
                
                # 6. Update quotes if necessary
                if self.should_update_quotes(bid_price, ask_price, bid_size, ask_size) or self.trigger_requote:
                    self.cancel_all_orders()
                    
                    if bid_size > 0:
                        self.place_order('buy', bid_price, bid_size, post_only=True)
                    if ask_size > 0:
                        self.place_order('sell', ask_price, ask_size, post_only=True)
                    
                    self.trigger_requote = False
            
            # 7. Log
            self.log_tick(mid_price, sigma, vpin, self.inventory, self.realized_pnl)
```

### 13.2 Execution Flow Diagram

```
┌─────────────────────────────────────────────┐
│       MARKET MAKING EXECUTION FLOW          │
├─────────────────────────────────────────────┤
│                                             │
│  1. MARKET DATA (Every tick/100ms)          │
│     ├─ Update mid-price                     │
│     ├─ Update order book depth              │
│     ├─ Process new trades                   │
│     └─ Compute microstructure signals       │
│                                             │
│  2. PARAMETER ESTIMATION                    │
│     ├─ Realized volatility (5-min window)   │
│     ├─ Order arrival rate (kappa)           │
│     ├─ VPIN (flow toxicity)                 │
│     └─ Order book imbalance                 │
│                                             │
│  3. RISK CHECKS                             │
│     ├─ P&L limits (hourly/daily)            │
│     ├─ Inventory limits                     │
│     ├─ VPIN toxicity threshold              │
│     ├─ System health (latency, connection)  │
│     └─ IF FAIL → Pull quotes or halt        │
│                                             │
│  4. QUOTE CALCULATION                       │
│     ├─ Avellaneda-Stoikov reservation price │
│     ├─ Optimal spread calculation           │
│     ├─ Inventory skew adjustment            │
│     ├─ Tick size rounding                   │
│     └─ Min/max spread enforcement           │
│                                             │
│  5. QUOTE UPDATE DECISION                   │
│     ├─ Compare new quotes vs current        │
│     ├─ IF change > tolerance → Update       │
│     ├─ IF change < tolerance → Hold         │
│     └─ Queue position preservation          │
│                                             │
│  6. ORDER MANAGEMENT                        │
│     ├─ Cancel stale orders                  │
│     ├─ Place new bid/ask (POST_ONLY)        │
│     ├─ Handle partial fills                 │
│     └─ Confirm placements                   │
│                                             │
│  7. FILL HANDLING                           │
│     ├─ Update inventory                     │
│     ├─ Match round-trips (FIFO)             │
│     ├─ Calculate realized P&L               │
│     ├─ Trigger immediate re-quote           │
│     └─ Adverse selection tracking           │
│                                             │
│  8. MONITORING                              │
│     ├─ Real-time P&L dashboard              │
│     ├─ Fill rate and capture ratio          │
│     ├─ Inventory aging                      │
│     └─ Alert on anomalies                   │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 14. เอกสารอ้างอิง (References)

### Academic Papers

1. **Avellaneda, M., & Stoikov, S.** (2008). "High-Frequency Trading in a Limit Order Book." *Quantitative Finance*, 8(3), 217-224.
2. **Gueant, O., Lehalle, C.A., & Fernandez-Tapia, J.** (2013). "Dealing with the Inventory Risk: A Solution to the Market Making Problem." *Mathematics and Financial Economics*, 7(4), 477-507.
3. **Cartea, A., Jaimungal, S., & Penalva, J.** (2015). *Algorithmic and High-Frequency Trading*. Cambridge University Press.
4. **Kyle, A.S.** (1985). "Continuous Auctions and Insider Trading." *Econometrica*, 53(6), 1315-1335.
5. **Glosten, L.R., & Milgrom, P.R.** (1985). "Bid, Ask and Transaction Prices in a Specialist Market with Heterogeneously Informed Traders." *Journal of Financial Economics*, 14(1), 71-100.
6. **Glosten, L.R., & Harris, L.E.** (1988). "Estimating the Components of the Bid/Ask Spread." *Journal of Financial Economics*, 21(1), 123-142.
7. **Roll, R.** (1984). "A Simple Implicit Measure of the Effective Bid-Ask Spread in an Efficient Market." *Journal of Finance*, 39(4), 1127-1139.
8. **Cont, R., Stoikov, S., & Talreja, R.** (2010). "A Stochastic Model for Order Book Dynamics." *Operations Research*, 58(3), 549-563.
9. **Easley, D., Lopez de Prado, M., & O'Hara, M.** (2012). "Flow Toxicity and Liquidity in a High-Frequency World." *Review of Financial Studies*, 25(5), 1457-1493. (VPIN paper.)
10. **Fodra, P., & Pham, H.** (2015). "High Frequency Trading and Asymmetric Effects of Stochastic Volatility." *Applied Mathematical Finance*, 22(6), 518-545.

### Practitioner Resources

11. **Hummingbot Documentation.** "Pure Market Making Strategy." Open-source market making bot.
12. **Wintermute Research.** Crypto market making insights.
13. **Cartea, A., & Jaimungal, S.** (2015). "Risk Metrics and Fine Tuning of High-Frequency Trading Strategies." *Mathematical Finance*, 25(3), 576-611.
14. **CoinRoutes.** Smart Order Routing and Market Making Infrastructure.

### Software and Tools

15. **Hummingbot**: Open-source crypto market making framework (Python)
16. **CCXT Pro**: WebSocket-based real-time exchange data
17. **River**: Low-latency Rust framework for trading
18. **TradingView**: Market visualization and strategy testing

---

*เอกสารนี้เป็นส่วนหนึ่งของฐานความรู้ระบบเทรด AI แบบ Multi-Agent การทำตลาดเป็นกลยุทธ์ที่ซับซ้อนและใช้เงินทุนสูง ให้ผลตอบแทนสม่ำเสมอจากการจับ Spread แต่ต้องการโครงสร้างพื้นฐานที่ยอดเยี่ยม การบริหารความเสี่ยง และการลดผลกระทบจาก Adverse Selection เพื่อให้ทำกำไรได้*
