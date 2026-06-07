# การวิเคราะห์ Order Book — ข้อมูล Level 2, การตรวจจับความไม่สมดุล (Imbalance) และแผนภูมิ Footprint

> **แกนที่ 1 — กลยุทธ์การเทรด | โมดูล 03 — การไหลของคำสั่งและสภาพคล่อง (Order Flow & Liquidity)**
> เอกสาร: 01_order_book_analysis.md
> เวอร์ชัน: 2.0 | อัปเดตล่าสุด: 2026-04-12
> การจัดประเภท: ฐานความรู้หลัก — ระบบเทรด AI แบบหลายเอเจนต์ (Multi-Agent AI Trading System)

---

## สารบัญ

1. [บทนำ](#1-บทนำ)
2. [การตีความข้อมูล Level 2 (ความลึกตลาด / Market Depth)](#2-การตีความข้อมูล-level-2)
3. [การตรวจจับความไม่สมดุลของ Order Book](#3-การตรวจจับความไม่สมดุลของ-order-book)
4. [การตรวจจับ Spoofing และ Layering](#4-การตรวจจับ-spoofing-และ-layering)
5. [รูปแบบการดูดซับ (Absorption Patterns)](#5-รูปแบบการดูดซับ)
6. [การตรวจจับคำสั่ง Iceberg](#6-การตรวจจับคำสั่ง-iceberg)
7. [โมเดลทางคณิตศาสตร์สำหรับความไม่สมดุลของ Order Book](#7-โมเดลทางคณิตศาสตร์)
8. [Delta — ปริมาณซื้อสะสม กับ ปริมาณขายสะสม](#8-delta)
9. [แผนภูมิ Footprint ของ Order Flow](#9-แผนภูมิ-footprint)
10. [อัลกอริทึมสำหรับนำไปใช้งาน — การวิเคราะห์ Order Book](#10-อัลกอริทึม)
11. [ตรรกะหลัก — การเข้า/ออก (Entry/Exit)](#11-ตรรกะหลัก)
12. [ข้อกำหนดทางเทคนิค](#12-ข้อกำหนดทางเทคนิค)
13. [พารามิเตอร์ความเสี่ยง](#13-พารามิเตอร์ความเสี่ยง)
14. [ขั้นตอนการดำเนินการ — Pseudocode](#14-ขั้นตอนการดำเนินการ)
15. [เอกสารอ้างอิง](#15-เอกสารอ้างอิง)

---

## 1. บทนำ

Order Book — หรือที่เรียกว่า Limit Order Book (LOB) หรือ Depth of Market (DOM) — คือทะเบียนแบบเรียลไทม์ของคำสั่งซื้อและขายแบบ Limit ที่ค้างอยู่ทั้งหมดในระดับราคาต่างๆ เป็นการแสดงอุปสงค์และอุปทานที่ละเอียดที่สุดที่เทรดเดอร์สามารถเข้าถึงได้

### 1.1 ทำไมต้องวิเคราะห์ Order Book?

Order Book เผยให้เห็น:
- **ตำแหน่งที่มีสภาพคล่อง (Liquidity)** — ระดับราคาใดมีคำสั่งรอดำเนินการจำนวนมาก
- **ตำแหน่งที่สภาพคล่องบาง** — ระดับราคาที่อาจเกิดการเคลื่อนไหวอย่างรวดเร็ว
- **แรงกดทิศทาง (Directional Pressure)** — ความไม่สมดุลระหว่างความลึกของ Bid และ Ask
- **ร่องรอยสถาบัน (Institutional Footprints)** — คำสั่งซ่อนขนาดใหญ่ (Iceberg), รูปแบบการดูดซับ (Absorption)
- **สัญญาณการปั่น (Manipulation Signals)** — Spoofing, Layering, Quote Stuffing

### 1.2 ข้อจำกัดของข้อมูล Order Book

| ข้อจำกัด | คำอธิบาย | การแก้ไข |
|-----------|-------------|-----------|
| **ไม่ผูกมัด (Non-binding)** | คำสั่ง Limit สามารถยกเลิกได้ตลอดเวลา | ติดตามอัตราการยกเลิก; ถ่วงน้ำหนักด้วยความน่าจะเป็นที่จะถูกเติม |
| **Spoofing** | คำสั่งปลอมที่วางเพื่อหลอกลวง | ตรวจจับและกรองรูปแบบ Spoof |
| **การกระจาย (Fragmentation)** | หลายแพลตฟอร์มมี Book ต่างกัน | รวมข้อมูลข้ามตลาด |
| **ความหน่วง (Latency)** | ข้อมูลอาจล้าสมัยเมื่อถูกประมวลผล | ลดความหน่วงในการประมวลผล; ใช้ Co-location |
| **สภาพคล่องที่ซ่อน (Hidden Liquidity)** | คำสั่ง Iceberg/ซ่อนไม่มองเห็นเต็ม | ตรวจจับผ่านรูปแบบการเติม |
| **Forex OTC** | ไม่มี Order Book ส่วนกลางสำหรับ Spot FX | ใช้ CME Futures เป็นตัวแทน |

### 1.3 แหล่งข้อมูล

| ตลาด | แหล่งที่มา | อัตราอัปเดต | ระดับความลึก |
|--------|--------|-------------|-------------|
| Forex Futures (CME) | CME MDP 3.0 | Incremental (real-time) | 10 levels (standard), full book (premium) |
| Crypto (Binance) | WebSocket `depth@100ms` | 100ms snapshots | 5, 10, 20 levels; or full 1000+ levels |
| Crypto (Coinbase) | WebSocket `level2` | Real-time incremental | Full book |
| Crypto (dYdX) | WebSocket orderbook | Real-time | Full book (on-chain settlement) |

---

## 2. การตีความข้อมูล Level 2 (ความลึกตลาด / Market Depth)

### 2.1 โครงสร้าง DOM

The Depth of Market shows resting limit orders organized by price level:

```
═══════════════════════════════════════════════════════
 SELL SIDE (ASKS)              │  Cumulative Ask
═══════════════════════════════╪═══════════════════════
 1.10600  │  120  ████████    │     2,180
 1.10580  │  350  ███████████ │     2,060
 1.10560  │  280  ██████████  │     1,710
 1.10540  │  510  ████████████│     1,430  ← Large ask wall
 1.10520  │  170  ████████    │       920
 1.10510  │  180  █████████   │       750
 1.10500  │  320  ██████████  │       570
 1.10490  │  250  █████████   │       250  ← Best Ask (Inside)
═══════════════════════════════╪═══════════════════════
                 SPREAD: 2 pips
═══════════════════════════════╪═══════════════════════
 1.10470  │  310  ██████████  │       310  ← Best Bid (Inside)
 1.10460  │  190  █████████   │       500
 1.10450  │  440  ████████████│       940  ← Large bid support
 1.10440  │  160  ████████    │     1,100
 1.10420  │  200  █████████   │     1,300
 1.10400  │  380  ███████████ │     1,680
 1.10380  │  270  █████████   │     1,950
 1.10360  │  150  ████████    │     2,100
═══════════════════════════════╪═══════════════════════
 BUY SIDE (BIDS)               │  Cumulative Bid
═══════════════════════════════════════════════════════
```

### 2.2 Key Metrics from the DOM

**1. Best Bid/Offer (BBO):**
- Best Bid: Highest price a buyer is willing to pay
- Best Ask: Lowest price a seller is willing to accept
- Mid Price: $(P_{bid}^{(1)} + P_{ask}^{(1)}) / 2$

**2. Spread Metrics:**

$$\text{Absolute Spread} = P_{ask}^{(1)} - P_{bid}^{(1)}$$

$$\text{Relative Spread} = \frac{P_{ask}^{(1)} - P_{bid}^{(1)}}{P_{mid}} \times 10000 \text{ (in bps)}$$

$$\text{Effective Spread} = 2 \times |P_{trade} - P_{mid}|$$

**3. Depth Metrics:**

$$\text{Depth}_k^{bid} = \sum_{i=1}^{k} Q_{bid}^{(i)} \quad \text{(cumulative bid depth, } k \text{ levels)}$$

$$\text{Depth}_k^{ask} = \sum_{i=1}^{k} Q_{ask}^{(i)} \quad \text{(cumulative ask depth, } k \text{ levels)}$$

$$\text{Total Depth}_k = \text{Depth}_k^{bid} + \text{Depth}_k^{ask}$$

### 2.3 Reading the DOM for Trading Signals

**Signal 1: Depth Slope Analysis**

The slope of cumulative depth reveals how quickly liquidity builds away from the mid price:

```
Cumulative    │
Volume        │                            ╱ Ask depth (steep = strong resistance)
              │                          ╱
              │                        ╱
              │                      ╱
              │                    ╱
              │   ╲              ╱
              │     ╲          ╱
              │       ╲      ╱
              │         ╲  ╱
              │          ╲╱ ← Mid price
              └──────────────────────────── Price Level
              
Bid slope < Ask slope → Easier to move price UP (less ask resistance)
Bid slope > Ask slope → Easier to move price DOWN (less bid support)
```

**Signal 2: Wall Detection**

A "wall" is a price level with disproportionately large resting orders:

$$\text{Wall Score}_i = \frac{Q_i}{\text{median}(Q_{i-k}, ..., Q_{i+k})}$$

Where:
- $Q_i$ = Volume at price level $i$
- $k$ = Number of surrounding levels to compare
- Wall Score > 3.0 = Significant wall
- Wall Score > 5.0 = Major wall

**Signal 3: Stacked Bids/Asks**

Multiple consecutive levels with above-average depth indicate strong support/resistance zones:

```python
def detect_stacked_levels(book_side, min_consecutive=3, min_ratio=1.5):
    """Detect zones where multiple consecutive levels have above-average depth."""
    avg_depth = np.mean([level.quantity for level in book_side])
    
    consecutive = 0
    start_price = None
    zones = []
    
    for level in book_side:
        if level.quantity > avg_depth * min_ratio:
            if consecutive == 0:
                start_price = level.price
            consecutive += 1
        else:
            if consecutive >= min_consecutive:
                zones.append({
                    'start': start_price,
                    'end': book_side[book_side.index(level) - 1].price,
                    'total_depth': sum(l.quantity for l in book_side 
                                       if start_price <= l.price <= level.price),
                    'levels': consecutive
                })
            consecutive = 0
    
    return zones
```

### 2.4 DOM Heatmap Interpretation

Modern order flow platforms display the DOM as a heatmap over time, showing how resting orders appear, shift, and disappear:

```
Time →→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→
Price │T1    │T2    │T3    │T4    │T5    │T6
──────┼──────┼──────┼──────┼──────┼──────┼──────
1.106 │ ░░░░ │ ░░░░ │ ████ │ ████ │ ████ │ ░░░░  ← Ask wall appears T3, consumed T6
1.105 │ ░░░░ │ ░░   │ ░░   │ ░░░░ │ ████ │ ████  ← Wall migrates down
1.104 │ ▓▓▓▓ │ ▓▓▓▓ │ ▓▓   │      │      │ ░░    ← Bid wall pulled (bearish!)
1.103 │ ▓▓   │ ▓▓   │ ▓▓▓▓ │ ▓▓▓▓ │ ▓▓   │ ▓▓
1.102 │ ▓    │ ▓▓   │ ▓▓   │ ▓▓▓▓ │ ▓▓▓▓ │ ▓▓▓▓  ← Bid wall migrates down

Legend: ░ = Ask depth, ▓ = Bid depth
        Size: more characters = larger depth

Key observation: Bid wall at 1.104 was pulled at T3 → bearish signal
Ask wall at 1.106 appeared at T3 → resistance forming
Combined signal: BEARISH (passive sellers adding, passive buyers retreating)
```

---

## 3. Order Book Imbalance Detection

### 3.1 Level-1 Imbalance (BBO)

The simplest form of order book imbalance:

$$I_1 = \frac{Q_{bid}^{(1)} - Q_{ask}^{(1)}}{Q_{bid}^{(1)} + Q_{ask}^{(1)}}$$

**Properties:**
- Range: [-1, +1]
- $I_1 > 0$: More volume on bid (bullish pressure)
- $I_1 < 0$: More volume on ask (bearish pressure)
- $I_1 \approx 0$: Balanced book

**Predictive Power:**
Research by Cont, Kukanov, and Stoikov (2014) demonstrates that the Level-1 imbalance is a statistically significant predictor of short-term price changes:

$$E[\Delta P_{t+1} | I_1(t)] = \alpha + \beta \cdot I_1(t)$$

Where $\beta > 0$ (positive imbalance predicts upward price movement).

### 3.2 Multi-Level Weighted Imbalance

More robust than Level-1 because it considers depth across multiple levels:

$$I_{WM} = \frac{\sum_{i=1}^{K} w_i \cdot Q_{bid}^{(i)} - \sum_{i=1}^{K} w_i \cdot Q_{ask}^{(i)}}{\sum_{i=1}^{K} w_i \cdot Q_{bid}^{(i)} + \sum_{i=1}^{K} w_i \cdot Q_{ask}^{(i)}}$$

**Weighting Schemes:**

| Scheme | Formula | Rationale |
|--------|---------|-----------|
| Uniform | $w_i = 1$ | Equal weight to all levels |
| Linear Decay | $w_i = 1 - \frac{i-1}{K}$ | Closer levels more important |
| Exponential Decay | $w_i = e^{-\alpha(i-1)}$ | Strong emphasis on inside levels |
| Price-Distance | $w_i = \frac{1}{|P_i - P_{mid}|}$ | Weight by distance from mid |
| Inverse-Square | $w_i = \frac{1}{i^2}$ | Rapid decay |

**Recommended Default: Exponential Decay with $\alpha = 0.3$**

```python
def weighted_imbalance(bids, asks, alpha=0.3, K=10):
    """
    Calculate multi-level weighted order book imbalance.
    
    Args:
        bids: List of (price, quantity) tuples, sorted by price descending
        asks: List of (price, quantity) tuples, sorted by price ascending
        alpha: Decay parameter (higher = more weight on inside levels)
        K: Number of levels to consider
    
    Returns:
        float: Imbalance score in [-1, +1]
    """
    bid_weighted = sum(
        math.exp(-alpha * i) * bids[i][1]
        for i in range(min(K, len(bids)))
    )
    ask_weighted = sum(
        math.exp(-alpha * i) * asks[i][1]
        for i in range(min(K, len(asks)))
    )
    
    total = bid_weighted + ask_weighted
    if total == 0:
        return 0.0
    
    return (bid_weighted - ask_weighted) / total
```

### 3.3 Volume-at-Price Imbalance (Footprint Imbalance)

This measures the imbalance between buyers and sellers at each individual price level based on actual trades (not resting orders):

$$\text{Imb}_P = \frac{V_{buy}^{(P)} - V_{sell}^{(P)}}{V_{buy}^{(P)} + V_{sell}^{(P)}}$$

A price level is considered to have **significant imbalance** when:

$$\frac{V_{buy}^{(P)}}{V_{sell}^{(P)}} \geq R_{threshold} \quad \text{(buy imbalance, typically } R \geq 3.0\text{)}$$

$$\frac{V_{sell}^{(P)}}{V_{buy}^{(P)}} \geq R_{threshold} \quad \text{(sell imbalance, typically } R \geq 3.0\text{)}$$

**Stacked Imbalance:**
When 3+ consecutive price levels show the same directional imbalance (all buy-dominant or all sell-dominant), this is a **stacked imbalance** — a very strong directional signal.

```
Price   │ Bid Vol │ Ask Vol │ Ratio  │ Signal
────────┼─────────┼─────────┼────────┼─────────
1.1055  │   45    │   180   │  4.0x  │ SELL IMB  ┐
1.1054  │   32    │   165   │  5.2x  │ SELL IMB  ├─ STACKED SELL (3 levels)
1.1053  │   28    │   142   │  5.1x  │ SELL IMB  ┘  → Strong Bearish Signal
1.1052  │   95    │   110   │  1.2x  │ neutral
1.1051  │  156    │    42   │  3.7x  │ BUY IMB   ┐
1.1050  │  210    │    55   │  3.8x  │ BUY IMB   ├─ STACKED BUY (3 levels)
1.1049  │  185    │    38   │  4.9x  │ BUY IMB   ┘  → Strong Bullish Signal
```

### 3.4 Temporal Imbalance (Rate of Change)

Static imbalance is informative, but the **change** in imbalance over time is even more predictive:

$$\dot{I}(t) = \frac{I(t) - I(t - \Delta t)}{\Delta t}$$

A rapidly increasing imbalance (accelerating buying pressure) is a stronger signal than a stable imbalance.

```python
def temporal_imbalance(imbalance_history, window=10):
    """
    Calculate rate of change of imbalance.
    
    Args:
        imbalance_history: Deque of recent imbalance readings
        window: Number of snapshots for regression
    
    Returns:
        float: Slope of imbalance over time
    """
    if len(imbalance_history) < window:
        return 0.0
    
    recent = list(imbalance_history)[-window:]
    x = np.arange(len(recent))
    slope, _, _, _, _ = linregress(x, recent)
    
    return slope
```

### 3.5 Cross-Exchange Imbalance (Crypto-Specific)

For crypto, comparing order book imbalance across exchanges provides additional signal:

$$I_{cross} = \frac{1}{N} \sum_{e=1}^{N} I_e \cdot w_e$$

Where:
- $I_e$ = Imbalance on exchange $e$
- $w_e$ = Weight proportional to exchange volume share
- $N$ = Number of exchanges

If all major exchanges show the same directional imbalance, the signal is much stronger than a single-exchange reading.

---

## 4. Spoofing and Layering Detection

### 4.1 Definition

**Spoofing**: Placing a large order with the intent to cancel before execution, in order to create a false impression of supply or demand.

**Layering**: Placing multiple limit orders at successive price levels to create the appearance of deep liquidity, then cancelling them before they can be filled.

Both are **illegal** in regulated markets (Dodd-Frank Act, Section 747; EU MAR Article 12) but still occur in less regulated crypto markets.

### 4.2 Spoofing Characteristics

| Feature | Spoof Order | Genuine Order |
|---------|------------|---------------|
| Lifetime | <1 second typically | Seconds to hours |
| Size | Very large (10-100x normal) | Normal distribution |
| Cancellation rate | >95% | 20-60% |
| Placement distance | 1-5 levels from BBO | Any distance |
| Timing | Appears before move, disappears during | Persistent |
| Side correlation | Opposite to intended trade | Aligned with intent |

### 4.3 Spoofing Detection Algorithm

```python
class SpoofDetector:
    def __init__(self, config):
        self.size_threshold = config.get('spoof_size_multiple', 5.0)
        self.lifetime_threshold_ms = config.get('spoof_lifetime_ms', 2000)
        self.cancel_rate_threshold = config.get('spoof_cancel_rate', 0.9)
        self.order_tracker = {}  # order_id -> {price, size, timestamp, side}
        self.cancel_history = deque(maxlen=1000)
        self.avg_order_size = ExponentialMovingAverage(span=100)
    
    def on_order_add(self, order_id, price, size, side, timestamp):
        """Track new orders appearing in the book."""
        self.order_tracker[order_id] = {
            'price': price,
            'size': size,
            'side': side,
            'timestamp': timestamp,
            'distance_from_bbo': self._calc_distance(price, side)
        }
        self.avg_order_size.update(size)
    
    def on_order_cancel(self, order_id, timestamp):
        """Evaluate cancelled orders for spoof characteristics."""
        if order_id not in self.order_tracker:
            return None
        
        order = self.order_tracker.pop(order_id)
        lifetime_ms = (timestamp - order['timestamp']) * 1000
        size_ratio = order['size'] / self.avg_order_size.value
        
        spoof_score = 0.0
        
        # Factor 1: Abnormally large size
        if size_ratio > self.size_threshold:
            spoof_score += 0.3 * min(size_ratio / 10.0, 1.0)
        
        # Factor 2: Short lifetime
        if lifetime_ms < self.lifetime_threshold_ms:
            spoof_score += 0.3 * (1.0 - lifetime_ms / self.lifetime_threshold_ms)
        
        # Factor 3: Close to BBO (intended to influence)
        if order['distance_from_bbo'] <= 5:
            spoof_score += 0.2 * (1.0 - order['distance_from_bbo'] / 5.0)
        
        # Factor 4: Historical cancel rate for this size class
        cancel_rate = self._get_cancel_rate(size_ratio > 3.0)
        if cancel_rate > self.cancel_rate_threshold:
            spoof_score += 0.2
        
        self.cancel_history.append({
            'timestamp': timestamp,
            'size_ratio': size_ratio,
            'lifetime_ms': lifetime_ms,
            'spoof_score': spoof_score,
            'side': order['side']
        })
        
        if spoof_score > 0.7:
            return {
                'type': 'SPOOF_DETECTED',
                'confidence': spoof_score,
                'side': order['side'],
                'inferred_direction': 'SELL' if order['side'] == 'BUY' else 'BUY',
                'size': order['size'],
                'lifetime_ms': lifetime_ms
            }
        
        return None
    
    def on_order_fill(self, order_id, fill_size, timestamp):
        """Filled orders are likely genuine — remove from tracking."""
        if order_id in self.order_tracker:
            order = self.order_tracker[order_id]
            order['size'] -= fill_size
            if order['size'] <= 0:
                del self.order_tracker[order_id]
```

### 4.4 Layering Detection

Layering is detected by identifying correlated order placement across multiple levels:

```python
def detect_layering(book_snapshots, min_levels=3, time_window_ms=500):
    """
    Detect layering: multiple large orders placed at successive
    levels within a short time, then cancelled together.
    """
    # Find clusters of large orders appearing simultaneously
    new_orders_by_time = group_by_time(book_snapshots, time_window_ms)
    
    for time_cluster in new_orders_by_time:
        bid_layers = find_consecutive_levels(
            time_cluster, side='BUY', min_levels=min_levels
        )
        ask_layers = find_consecutive_levels(
            time_cluster, side='SELL', min_levels=min_levels
        )
        
        for layer_group in bid_layers + ask_layers:
            # Check if all orders in the group were later cancelled together
            all_cancelled = all(
                order.was_cancelled and order.lifetime_ms < 3000
                for order in layer_group
            )
            
            if all_cancelled:
                yield {
                    'type': 'LAYERING_DETECTED',
                    'side': layer_group[0].side,
                    'levels': len(layer_group),
                    'total_size': sum(o.size for o in layer_group),
                    'avg_lifetime_ms': np.mean([o.lifetime_ms for o in layer_group]),
                    'inferred_direction': opposite_side(layer_group[0].side)
                }
```

### 4.5 Trading Response to Detected Spoofing

When spoofing is detected, our system adjusts behavior:

| Detection | Response |
|-----------|----------|
| Spoof detected on BID side | Inferred direction: BEARISH (spoofer wants to sell) |
| Spoof detected on ASK side | Inferred direction: BULLISH (spoofer wants to buy) |
| Layering on BID + aggressive sell | STRONG BEARISH — manipulation + execution confirmed |
| Layering on ASK + aggressive buy | STRONG BULLISH — manipulation + execution confirmed |
| Repeated spoofing both sides | NO SIGNAL — market maker behavior, not directional |

**Important caveat for crypto**: In unregulated or lightly regulated markets, spoofing is more common and can persist longer. The system should:
1. Log detected spoofing events for post-trade analysis
2. Increase the evidence threshold before acting on spoof signals
3. Never rely solely on spoof detection for trade entry

---

## 5. Absorption Patterns

### 5.1 Definition

**Absorption** occurs when a large resting limit order (or iceberg) absorbs aggressive market orders without the price level being broken. It indicates that a large participant is accumulating or distributing at a specific price.

### 5.2 Visual Representation

```
BULLISH ABSORPTION (at Support):
─────────────────────────────────
Price hits support level → aggressive SELL orders hit the bid
BUT the bid does NOT break → a large buyer is absorbing all selling

Time →→→→→→→→→→→→→→→→→→→→→→→→→→→→→→
│ Sell  │ Sell  │ Sell  │ Sell  │
│ 200   │ 350   │ 280   │ 150   │  ← Aggressive selling
│  ↓    │  ↓    │  ↓    │  ↓    │
│[=====]│[=====]│[=====]│[=====]│  ← Support level (1.1050)
│ Bid:  │ Bid:  │ Bid:  │ Bid:  │
│ 500   │ 450   │ 400   │ 350   │  ← Bid keeps getting refilled!
│       │       │       │       │
│ Price: │ Price: │ Price: │ Price:│
│ 1.1050│ 1.1050│ 1.1050│ 1.1051│  ← Level holds, then bounces

Total absorbed: 200 + 350 + 280 + 150 = 980 lots
Bid refilled 3 times → STRONG ABSORPTION → BULLISH signal
```

```
BEARISH ABSORPTION (at Resistance):
─────────────────────────────────────
Price hits resistance → aggressive BUY orders lift the ask
BUT the ask does NOT break → a large seller is absorbing all buying

│ Buy   │ Buy   │ Buy   │ Buy   │
│ 300   │ 250   │ 400   │ 200   │  ← Aggressive buying
│  ↑    │  ↑    │  ↑    │  ↑    │
│[=====]│[=====]│[=====]│[=====]│  ← Resistance level (1.1100)
│ Ask:  │ Ask:  │ Ask:  │ Ask:  │
│ 600   │ 550   │ 500   │ 450   │  ← Ask keeps getting refilled!
│       │       │       │       │
│ Price: │ Price: │ Price: │ Price:│
│ 1.1100│ 1.1100│ 1.1100│ 1.1099│  ← Level holds, then reverses
```

### 5.3 Absorption Detection Algorithm

```python
class AbsorptionDetector:
    def __init__(self, config):
        self.price_levels = {}  # price -> AbsorptionState
        self.min_aggression_count = config.get('min_aggression', 3)
        self.min_total_absorbed = config.get('min_absorbed_volume', 500)
        self.max_time_window_s = config.get('absorption_window_s', 300)
        self.refill_threshold = config.get('refill_threshold', 0.5)
    
    def on_trade(self, price, volume, side, timestamp, best_bid, best_ask):
        """Process each trade to detect absorption."""
        
        # We only care about aggressive orders AT key levels
        # Aggressive sell at bid → potential bullish absorption
        if side == 'SELL' and abs(price - best_bid) < self.tick_size:
            self._update_absorption(
                price=best_bid,
                aggressor_side='SELL',
                volume=volume,
                timestamp=timestamp,
                absorber_type='BID'
            )
        
        # Aggressive buy at ask → potential bearish absorption
        elif side == 'BUY' and abs(price - best_ask) < self.tick_size:
            self._update_absorption(
                price=best_ask,
                aggressor_side='BUY',
                volume=volume,
                timestamp=timestamp,
                absorber_type='ASK'
            )
    
    def on_book_update(self, price, new_size, side):
        """Track refilling of absorbed levels."""
        if price in self.price_levels:
            state = self.price_levels[price]
            if new_size > state.last_known_size * self.refill_threshold:
                state.refill_count += 1
                state.last_known_size = new_size
    
    def _update_absorption(self, price, aggressor_side, volume, timestamp, absorber_type):
        """Update absorption state for a price level."""
        if price not in self.price_levels:
            self.price_levels[price] = AbsorptionState(
                price=price,
                first_timestamp=timestamp,
                absorber_type=absorber_type
            )
        
        state = self.price_levels[price]
        
        # Check time window
        if timestamp - state.first_timestamp > self.max_time_window_s:
            # Reset if too old
            state.reset(timestamp)
        
        state.aggression_count += 1
        state.total_absorbed += volume
        state.last_timestamp = timestamp
        
        # Check if absorption is significant
        if (state.aggression_count >= self.min_aggression_count and
            state.total_absorbed >= self.min_total_absorbed and
            state.refill_count >= 2):
            
            return {
                'type': 'ABSORPTION_DETECTED',
                'price': price,
                'direction': 'BULLISH' if absorber_type == 'BID' else 'BEARISH',
                'total_absorbed': state.total_absorbed,
                'aggression_count': state.aggression_count,
                'refill_count': state.refill_count,
                'duration_s': timestamp - state.first_timestamp,
                'strength': self._calc_strength(state)
            }
    
    def _calc_strength(self, state):
        """Calculate absorption strength score [0, 1]."""
        volume_score = min(state.total_absorbed / (self.min_total_absorbed * 5), 1.0)
        count_score = min(state.aggression_count / (self.min_aggression_count * 3), 1.0)
        refill_score = min(state.refill_count / 5, 1.0)
        
        return (volume_score * 0.4 + count_score * 0.3 + refill_score * 0.3)
```

### 5.4 Absorption Strength Classification

| Strength | Criteria | Trading Action |
|----------|----------|---------------|
| **Weak** (0.2-0.4) | 3-5 aggressive attempts, moderate volume | Note level, no action yet |
| **Moderate** (0.4-0.6) | 5-10 attempts, significant volume, 2-3 refills | Prepare for trade |
| **Strong** (0.6-0.8) | 10+ attempts, high volume, 3-5 refills | Enter with standard size |
| **Extreme** (0.8-1.0) | 15+ attempts, extreme volume, 5+ refills | Enter with increased size |

### 5.5 Failed Absorption

When absorption eventually fails (the level breaks), it produces the **opposite** signal:

```
FAILED BULLISH ABSORPTION → STRONGLY BEARISH
─────────────────────────────────────────────
The large buyer was absorbing selling at 1.1050
After absorbing 2000 lots of selling, the bid finally breaks
→ The absorber is now offside (underwater)
→ Their stop loss becomes ADDITIONAL selling pressure
→ Expect accelerated move DOWN through the broken level

Signal: If absorption detected AND level subsequently breaks:
  → STRONG reversal signal in the direction of the break
  → The absorbed volume is now "trapped" → adds to momentum
```

---

## 6. Iceberg Order Detection

### 6.1 Definition

An iceberg order displays only a fraction (the "visible" or "show" quantity) of its total size. When the visible portion is filled, a new visible portion automatically appears at the same price.

### 6.2 Iceberg Characteristics

```
VISIBLE ORDER BOOK:
  Ask: 1.1052 — 50 lots (visible)
  
TIME PROGRESSION:
  T1: 50 lots visible, buyer takes 50 → filled
  T2: 50 lots REAPPEAR at 1.1052 → first refill
  T3: Buyer takes 50 → filled
  T4: 50 lots REAPPEAR at 1.1052 → second refill
  T5: Buyer takes 50 → filled
  T6: 50 lots REAPPEAR at 1.1052 → third refill
  ...
  
REALITY: The iceberg has a total size of 500 lots
Only 50 visible at a time → 10 refills needed to consume it
```

### 6.3 Iceberg Detection Algorithm

```python
class IcebergDetector:
    def __init__(self, config):
        self.refill_tolerance = config.get('refill_tolerance_pct', 0.1)
        self.min_refills = config.get('min_refills', 3)
        self.max_refill_delay_ms = config.get('max_refill_delay_ms', 500)
        self.level_tracker = {}  # price -> IcebergState
    
    def on_level_consumed(self, price, consumed_volume, timestamp):
        """Called when a price level is fully consumed."""
        if price not in self.level_tracker:
            self.level_tracker[price] = IcebergState(price=price)
        
        state = self.level_tracker[price]
        state.last_consumed = timestamp
        state.last_consumed_volume = consumed_volume
        state.awaiting_refill = True
    
    def on_level_refilled(self, price, new_volume, timestamp):
        """Called when a new order appears at a previously consumed level."""
        if price not in self.level_tracker:
            return None
        
        state = self.level_tracker[price]
        
        if not state.awaiting_refill:
            return None
        
        refill_delay_ms = (timestamp - state.last_consumed) * 1000
        
        # Check if this looks like an iceberg refill
        volume_match = abs(new_volume - state.last_consumed_volume) / state.last_consumed_volume
        
        if (refill_delay_ms < self.max_refill_delay_ms and 
            volume_match < self.refill_tolerance):
            
            state.refill_count += 1
            state.total_refilled += new_volume
            state.awaiting_refill = False
            
            if state.refill_count >= self.min_refills:
                return {
                    'type': 'ICEBERG_DETECTED',
                    'price': price,
                    'visible_size': new_volume,
                    'estimated_remaining': self._estimate_remaining(state),
                    'refill_count': state.refill_count,
                    'total_consumed_so_far': state.total_refilled,
                    'avg_refill_delay_ms': state.avg_refill_delay(),
                    'side': state.side,
                    'strength': min(state.refill_count / 10, 1.0)
                }
        else:
            state.awaiting_refill = False
        
        return None
    
    def _estimate_remaining(self, state):
        """
        Estimate remaining iceberg volume based on refill pattern.
        This is inherently uncertain — we cannot know the total size.
        
        Heuristic: If the iceberg has refilled N times and is still active,
        estimate at least N more refills remaining.
        """
        return state.last_consumed_volume * state.refill_count  # Conservative estimate
```

### 6.4 Trading with Iceberg Information

| Scenario | Signal | Action |
|----------|--------|--------|
| Iceberg on BID (buyer) | Large hidden buyer at this level | Bullish — support level is stronger than visible |
| Iceberg on ASK (seller) | Large hidden seller at this level | Bearish — resistance level is stronger than visible |
| Iceberg consumed | Large order fully filled, level breaks | Strong move in direction of break |
| Iceberg + absorption | Both hidden and visible orders defending | Very strong level — low probability of breaking |

---

## 7. Mathematical Models for Order Book Imbalance

### 7.1 The Cont-Stoikov-Talreja Model (2010)

This stochastic model describes order book dynamics as a continuous-time Markov chain:

**State Variables:**
- $q_b(t)$ = Queue size at best bid
- $q_a(t)$ = Queue size at best ask
- $s(t)$ = Spread in ticks

**Transition Rates:**

$$\lambda_b^+ = \text{Rate of limit buy orders arriving at best bid}$$
$$\lambda_a^+ = \text{Rate of limit sell orders arriving at best ask}$$
$$\mu_b = \text{Rate of cancellations at best bid}$$
$$\mu_a = \text{Rate of cancellations at best ask}$$
$$\theta_b = \text{Rate of market sell orders}$$
$$\theta_a = \text{Rate of market buy orders}$$

**Queue Dynamics:**

$$dq_b = (\lambda_b^+ - \mu_b - \theta_b) \cdot dt + \text{noise}$$
$$dq_a = (\lambda_a^+ - \mu_a - \theta_a) \cdot dt + \text{noise}$$

**Price Change Probability:**

The probability that the next price change is an uptick:

$$P(\text{uptick}) = \frac{\theta_a \cdot P(q_a \to 0)}{\theta_a \cdot P(q_a \to 0) + \theta_b \cdot P(q_b \to 0)}$$

Where $P(q_a \to 0)$ is the probability that the ask queue is depleted before the bid queue. This depends on the relative sizes:

$$P(q_a \to 0 | q_a, q_b) \approx \frac{q_b}{q_a + q_b} \quad \text{(simplified)}$$

**Implementation Note:** This model provides the theoretical basis for our imbalance signals. The key insight is that the **relative queue sizes** at the best bid and ask are predictive of the direction of the next price change.

### 7.2 The Stoikov Order Book Imbalance Indicator

Building on the above, Stoikov (2018) proposed a practical indicator:

$$\text{OBI} = \frac{q_b - q_a}{q_b + q_a}$$

With the predictive relationship:

$$E[\Delta P_{t+\tau}] = \kappa \cdot \text{OBI}_t$$

Where $\kappa > 0$ is estimated from historical data (typically $\kappa \approx 0.1-0.5$ ticks for liquid markets).

### 7.3 Information-Weighted Imbalance

Not all orders are equally informative. We weight by estimated information content:

$$I_{info} = \frac{\sum_{i} \phi_i \cdot Q_{bid}^{(i)} - \sum_{j} \phi_j \cdot Q_{ask}^{(j)}}{\sum_{i} \phi_i \cdot Q_{bid}^{(i)} + \sum_{j} \phi_j \cdot Q_{ask}^{(j)}}$$

Where $\phi_i$ is the information weight for level $i$, incorporating:

$$\phi_i = f(\text{lifetime}_i, \text{size}_i, \text{cancelRate}_i, \text{distance}_i)$$

- **Lifetime**: Longer-lived orders are more likely genuine
- **Size**: Very large orders may be spoofs; moderate sizes are more informative
- **Cancel rate**: Price levels with high historical cancel rates are discounted
- **Distance**: Closer to BBO = more relevant

### 7.4 The Hasbrouck Lambda Model for Order Book

Extended from Kyle's lambda to the order book setting:

$$\Delta p_t = \lambda_0 + \lambda_1 \cdot \text{OFI}_t + \lambda_2 \cdot \text{OBI}_t + \epsilon_t$$

Where:
- $\text{OFI}_t$ = Order Flow Imbalance (from trades)
- $\text{OBI}_t$ = Order Book Imbalance (from resting orders)

The relative magnitudes of $\lambda_1$ and $\lambda_2$ indicate whether **aggressive flow** (trades) or **passive flow** (resting orders) is more informative in the current regime.

### 7.5 Entropy-Based Order Book Analysis

Order book entropy measures the "disorder" or "uncertainty" in the distribution of liquidity:

$$H_{bid} = -\sum_{i=1}^{K} p_i^{bid} \cdot \ln(p_i^{bid})$$

Where $p_i^{bid} = Q_{bid}^{(i)} / \sum_{j} Q_{bid}^{(j)}$ is the normalized weight of level $i$.

**Interpretation:**
- **Low entropy**: Liquidity concentrated at few levels (large walls) → brittle, can break suddenly
- **High entropy**: Liquidity evenly distributed → robust, gradual price movement

$$\text{Entropy Ratio} = \frac{H_{bid}}{H_{ask}}$$

- Ratio > 1: Ask side more concentrated (resistance may be brittle)
- Ratio < 1: Bid side more concentrated (support may be brittle)

---

## 8. Delta — Cumulative Buy vs Sell Volume

### 8.1 Delta Definition

**Delta** is the difference between buyer-initiated and seller-initiated volume:

$$\Delta_t = V_t^{buy} - V_t^{sell}$$

Where:
- $V_t^{buy}$ = Volume of trades that hit the ask (buyer aggressor)
- $V_t^{sell}$ = Volume of trades that hit the bid (seller aggressor)

### 8.2 Delta per Bar

For each candlestick/bar period:

$$\Delta_{bar} = \sum_{trades \in bar} \mathbb{1}_{buy}(trade) \cdot V_{trade} - \sum_{trades \in bar} \mathbb{1}_{sell}(trade) \cdot V_{trade}$$

**Interpretation:**
| Bar Type | Delta | Meaning |
|----------|-------|---------|
| Green bar | Positive delta | Normal — buyers more aggressive, price up |
| Green bar | Negative delta | **Anomalous** — price up on SELL pressure → distribution |
| Red bar | Negative delta | Normal — sellers more aggressive, price down |
| Red bar | Positive delta | **Anomalous** — price down on BUY pressure → accumulation |

The **anomalous** cases are the most interesting for trading because they reveal hidden activity.

### 8.3 Cumulative Volume Delta (CVD)

$$\text{CVD}_T = \sum_{t=1}^{T} \Delta_t = \sum_{t=1}^{T} (V_t^{buy} - V_t^{sell})$$

CVD tracks the running total of aggressive buying vs selling over time.

**CVD Divergence** (covered in detail in Document 04):
- Price making higher highs + CVD making lower highs = **Bearish divergence**
- Price making lower lows + CVD making higher lows = **Bullish divergence**

### 8.4 Delta at Price (Volume Delta Profile)

Instead of calculating delta per time period, calculate delta at each price level:

$$\Delta(P) = V^{buy}(P) - V^{sell}(P)$$

This shows, at every price traded, whether buyers or sellers were more aggressive.

```
Price   │ Delta Profile
────────┼─────────────────────────────────────
1.1060  │         ████████████  +350  (Buy dominant)
1.1058  │       ██████████  +280
1.1056  │     ████████  +200
1.1054  │   ██████  +140
1.1052  │ ████  +80
1.1050  │ ██  +30        ← Pivot point
1.1048  │     ██████  -160
1.1046  │       ████████  -220
1.1044  │         ██████████  -300
1.1042  │           ████████████  -380  (Sell dominant)
```

---

## 9. Order Flow Footprint Charts

### 9.1 What is a Footprint Chart?

A footprint chart is an enhanced candlestick chart that shows the **actual volume traded** at each price level within the candle, broken down by buyer and seller aggression.

### 9.2 Footprint Types

**Type 1: Bid x Ask Footprint**

Shows volume that hit the bid (sells) on the left and volume that hit the ask (buys) on the right:

```
          ┌──────────────────────────┐
          │    BULLISH CANDLE        │
          │    Open: 1.1040          │
          │    Close: 1.1060         │
          │    High: 1.1065          │
          │    Low: 1.1035           │
          ├──────────────────────────┤
 Price    │  Bid Vol │ Ask Vol       │  Imbalance
──────────┼──────────┼──────────┼────┤
 1.1065   │    15    │    45    │    │  3.0x BUY
 1.1060   │    80    │   250    │ ** │  3.1x BUY ← Close
 1.1058   │   120    │   340    │ ** │  2.8x BUY
 1.1056   │   150    │   420    │ ** │  2.8x BUY
 1.1054   │   180    │   200    │    │  1.1x balanced
 1.1052   │   210    │   180    │    │  0.9x balanced
 1.1050   │   280    │   120    │ ## │  2.3x SELL
 1.1048   │   350    │   100    │ ## │  3.5x SELL
 1.1046   │   220    │    90    │ ## │  2.4x SELL
 1.1044   │   180    │   110    │    │  1.6x SELL
 1.1042   │   120    │    80    │    │  1.5x SELL
 1.1040   │    95    │   160    │    │  1.7x BUY ← Open
 1.1038   │    60    │    30    │    │  2.0x SELL
 1.1035   │    25    │    10    │    │  2.5x SELL
          ├──────────┼──────────┤
          │  Total:  │  Total:  │
          │  2,085   │  2,135   │
          │          │          │
          │  BAR DELTA: +50     │
          └──────────────────────┘

** = Stacked BUY imbalance (3+ consecutive levels with buy > 3x sell)
## = Stacked SELL imbalance
```

**Type 2: Delta Footprint**

Shows the net delta at each price level:

```
Price    │  Delta
─────────┼──────────────────
1.1060   │  ████████ +170
1.1058   │  ███████████ +220
1.1056   │  █████████████ +270
1.1054   │  █ +20
1.1052   │ █ -30
1.1050   │ ████ -160
1.1048   │ ████████ -250
1.1046   │ ███ -130
```

**Type 3: Volume Profile Footprint**

Shows total volume at each price level, colored by delta:

```
Price    │  Volume (colored by delta)
─────────┼──────────────────────────────
1.1060   │  ████████████████████ 330  (green - buy dominant)
1.1058   │  ██████████████████████████ 460  (green)
1.1056   │  ████████████████████████████████ 570  (green)
1.1054   │  ████████████████████ 380  (gray - balanced)
1.1052   │  █████████████████████ 390  (gray)
1.1050   │  ████████████████████████ 400  (red - sell dominant) ← POC
1.1048   │  ██████████████████████████ 450  (red)
1.1046   │  ████████████████████ 310  (red)
```

### 9.3 Footprint Pattern Recognition

**Pattern 1: Finished Auction (Buying Tail / Selling Tail)**

```
BUYING TAIL (Bullish):
Price    │  Bid    │  Ask
─────────┼─────────┼─────
1.1044   │   20    │   15    ← Low volume at bottom
1.1042   │   15    │    8    ← Very low volume
1.1040   │   10    │    5    ← Exhaustion — selling dried up

Interpretation: Sellers could not push price lower. Auction is "finished" 
on the downside. Expect reversal higher.
```

```
SELLING TAIL (Bearish):
Price    │  Bid    │  Ask
─────────┼─────────┼─────
1.1058   │    8    │   12    ← Low volume at top
1.1060   │    5    │   10    ← Very low volume
1.1062   │    3    │    6    ← Exhaustion — buying dried up

Interpretation: Buyers could not push price higher. Auction is "finished"
on the upside. Expect reversal lower.
```

**Pattern 2: Unfinished Auction (No Tail)**

```
UNFINISHED AUCTION (Continuation Expected):
Price    │  Bid    │  Ask
─────────┼─────────┼─────
1.1058   │  120    │  350    ← HIGH volume at extreme
1.1060   │  150    │  380    ← INCREASING volume at edge

Interpretation: Strong demand at the candle's extreme means the move is 
NOT finished. Expect continuation in the same direction next bar.
```

**Pattern 3: Delta Shift**

When delta abruptly changes from one bar to the next:

```
Bar 1: Delta = +500 (strong buying)
Bar 2: Delta = +200 (buying weakening)
Bar 3: Delta = -100 (delta turned negative while price still up)
Bar 4: Delta = -400 (sellers taking control)

→ Delta shift from +500 to -400 = REVERSAL signal
→ Smart money may have finished distributing
```

### 9.4 Footprint Data Structure

```python
@dataclass
class FootprintBar:
    """Represents a single footprint candle."""
    timestamp: datetime
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    delta: float  # Total bar delta
    
    # Per-price-level data
    levels: Dict[float, FootprintLevel]
    
    # Derived metrics
    poc_price: float  # Price with highest volume
    imbalance_zones: List[ImbalanceZone]
    has_buying_tail: bool
    has_selling_tail: bool
    finished_auction_top: bool
    finished_auction_bottom: bool

@dataclass
class FootprintLevel:
    """Data for a single price level within a footprint bar."""
    price: float
    bid_volume: float  # Volume that hit the bid (sells)
    ask_volume: float  # Volume that hit the ask (buys)
    delta: float       # ask_volume - bid_volume
    total_volume: float  # bid_volume + ask_volume
    trade_count: int   # Number of individual trades
    imbalance_ratio: float  # max(bid,ask) / min(bid,ask)
    imbalance_direction: str  # 'BUY', 'SELL', 'NEUTRAL'
```

---

## 10. Implementation Algorithm for Order Book Analysis

### 10.1 Complete Order Book Analyzer

```python
import numpy as np
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import time

@dataclass
class OrderBookState:
    """Represents the current state of the order book."""
    bids: List[Tuple[float, float]]  # [(price, quantity), ...] sorted desc
    asks: List[Tuple[float, float]]  # [(price, quantity), ...] sorted asc
    timestamp: float
    
    @property
    def best_bid(self) -> float:
        return self.bids[0][0] if self.bids else 0.0
    
    @property
    def best_ask(self) -> float:
        return self.asks[0][0] if self.asks else float('inf')
    
    @property
    def mid_price(self) -> float:
        return (self.best_bid + self.best_ask) / 2
    
    @property
    def spread(self) -> float:
        return self.best_ask - self.best_bid
    
    @property
    def spread_bps(self) -> float:
        return (self.spread / self.mid_price) * 10000


class OrderBookAnalyzer:
    """
    Complete order book analysis engine.
    
    Processes L2 market depth data and generates trading signals
    based on imbalance, absorption, spoofing detection, and
    iceberg detection.
    """
    
    def __init__(self, config: dict):
        # Configuration
        self.imbalance_levels = config.get('imbalance_levels', 10)
        self.imbalance_decay = config.get('imbalance_decay', 0.3)
        self.imbalance_threshold = config.get('imbalance_threshold', 0.4)
        self.wall_threshold = config.get('wall_threshold', 3.0)
        self.spread_ma_period = config.get('spread_ma_period', 100)
        self.history_length = config.get('history_length', 500)
        
        # State
        self.current_book = None
        self.imbalance_history = deque(maxlen=self.history_length)
        self.spread_history = deque(maxlen=self.history_length)
        self.mid_price_history = deque(maxlen=self.history_length)
        
        # Sub-analyzers
        self.spoof_detector = SpoofDetector(config)
        self.absorption_detector = AbsorptionDetector(config)
        self.iceberg_detector = IcebergDetector(config)
        
        # Signal output
        self.signals = deque(maxlen=100)
    
    def update(self, book: OrderBookState):
        """
        Process a new order book snapshot.
        
        This is the main entry point, called every time the order book updates.
        """
        self.current_book = book
        
        # 1. Calculate core metrics
        imbalance = self._calc_weighted_imbalance(book)
        spread = book.spread
        mid = book.mid_price
        
        # 2. Update histories
        self.imbalance_history.append({
            'value': imbalance,
            'timestamp': book.timestamp
        })
        self.spread_history.append(spread)
        self.mid_price_history.append(mid)
        
        # 3. Detect walls
        bid_walls = self._detect_walls(book.bids, 'BID')
        ask_walls = self._detect_walls(book.asks, 'ASK')
        
        # 4. Calculate depth slope
        bid_slope = self._calc_depth_slope(book.bids)
        ask_slope = self._calc_depth_slope(book.asks)
        
        # 5. Check for spread anomalies
        spread_signal = self._check_spread_anomaly(spread)
        
        # 6. Calculate entropy
        bid_entropy = self._calc_entropy(book.bids)
        ask_entropy = self._calc_entropy(book.asks)
        
        # 7. Generate composite signal
        signal = self._generate_signal(
            imbalance=imbalance,
            bid_walls=bid_walls,
            ask_walls=ask_walls,
            bid_slope=bid_slope,
            ask_slope=ask_slope,
            spread_signal=spread_signal,
            bid_entropy=bid_entropy,
            ask_entropy=ask_entropy
        )
        
        if signal:
            self.signals.append(signal)
        
        return signal
    
    def _calc_weighted_imbalance(self, book: OrderBookState) -> float:
        """Calculate exponentially-weighted multi-level imbalance."""
        K = min(self.imbalance_levels, len(book.bids), len(book.asks))
        
        if K == 0:
            return 0.0
        
        bid_weighted = 0.0
        ask_weighted = 0.0
        
        for i in range(K):
            weight = np.exp(-self.imbalance_decay * i)
            bid_weighted += weight * book.bids[i][1]
            ask_weighted += weight * book.asks[i][1]
        
        total = bid_weighted + ask_weighted
        if total == 0:
            return 0.0
        
        return (bid_weighted - ask_weighted) / total
    
    def _detect_walls(self, levels: List[Tuple[float, float]], side: str) -> List[dict]:
        """Detect price levels with disproportionately large resting orders."""
        if len(levels) < 5:
            return []
        
        quantities = [q for _, q in levels]
        median_q = np.median(quantities)
        
        if median_q == 0:
            return []
        
        walls = []
        for price, quantity in levels:
            ratio = quantity / median_q
            if ratio >= self.wall_threshold:
                walls.append({
                    'price': price,
                    'quantity': quantity,
                    'ratio': ratio,
                    'side': side,
                    'significance': 'MAJOR' if ratio > 5.0 else 'MINOR'
                })
        
        return walls
    
    def _calc_depth_slope(self, levels: List[Tuple[float, float]]) -> float:
        """
        Calculate the slope of cumulative depth.
        Steeper slope = liquidity builds quickly away from BBO.
        """
        if len(levels) < 3:
            return 0.0
        
        K = min(10, len(levels))
        cumulative = np.cumsum([q for _, q in levels[:K]])
        x = np.arange(K)
        
        if len(x) < 2:
            return 0.0
        
        slope, _, _, _, _ = np.polyfit(x, cumulative, 1, full=False, cov=False)
        return slope if isinstance(slope, float) else float(slope)
    
    def _check_spread_anomaly(self, current_spread: float) -> Optional[dict]:
        """Detect abnormal spread widening or tightening."""
        if len(self.spread_history) < self.spread_ma_period:
            return None
        
        avg_spread = np.mean(list(self.spread_history)[-self.spread_ma_period:])
        std_spread = np.std(list(self.spread_history)[-self.spread_ma_period:])
        
        if std_spread == 0:
            return None
        
        z_score = (current_spread - avg_spread) / std_spread
        
        if z_score > 3.0:
            return {
                'type': 'SPREAD_BLOWOUT',
                'z_score': z_score,
                'current': current_spread,
                'average': avg_spread,
                'action': 'REDUCE_EXPOSURE'
            }
        elif z_score < -2.0:
            return {
                'type': 'SPREAD_COMPRESSION',
                'z_score': z_score,
                'current': current_spread,
                'average': avg_spread,
                'action': 'FAVORABLE_ENTRY'
            }
        
        return None
    
    def _calc_entropy(self, levels: List[Tuple[float, float]]) -> float:
        """Calculate Shannon entropy of liquidity distribution."""
        if len(levels) < 2:
            return 0.0
        
        quantities = np.array([q for _, q in levels])
        total = quantities.sum()
        
        if total == 0:
            return 0.0
        
        probs = quantities / total
        probs = probs[probs > 0]  # Remove zeros for log
        
        return -np.sum(probs * np.log(probs))
    
    def _generate_signal(self, **metrics) -> Optional[dict]:
        """Generate composite order book signal from all metrics."""
        imbalance = metrics['imbalance']
        
        # Score components
        imbalance_score = imbalance  # Already in [-1, 1]
        
        # Slope asymmetry (if bid slope >> ask slope, bullish)
        if metrics['ask_slope'] > 0:
            slope_ratio = metrics['bid_slope'] / metrics['ask_slope']
        else:
            slope_ratio = 1.0
        slope_score = np.clip((slope_ratio - 1.0) * 0.5, -1, 1)
        
        # Wall influence
        wall_score = 0.0
        for wall in metrics['bid_walls']:
            wall_score += 0.1 * wall['ratio']  # Bid walls are bullish
        for wall in metrics['ask_walls']:
            wall_score -= 0.1 * wall['ratio']  # Ask walls are bearish
        wall_score = np.clip(wall_score, -1, 1)
        
        # Entropy asymmetry
        if metrics['ask_entropy'] > 0:
            entropy_ratio = metrics['bid_entropy'] / metrics['ask_entropy']
        else:
            entropy_ratio = 1.0
        # Lower bid entropy = concentrated support = potentially brittle
        entropy_score = np.clip((entropy_ratio - 1.0) * -0.3, -0.5, 0.5)
        
        # Composite score
        composite = (
            0.40 * imbalance_score +
            0.25 * slope_score +
            0.20 * wall_score +
            0.15 * entropy_score
        )
        
        # Only signal if above threshold
        if abs(composite) < 0.2:
            return None
        
        direction = 'LONG' if composite > 0 else 'SHORT'
        strength = abs(composite)
        
        return {
            'type': 'ORDER_BOOK_SIGNAL',
            'direction': direction,
            'strength': strength,
            'composite_score': composite,
            'components': {
                'imbalance': imbalance_score,
                'slope': slope_score,
                'wall': wall_score,
                'entropy': entropy_score
            },
            'spread_signal': metrics['spread_signal'],
            'bid_walls': metrics['bid_walls'],
            'ask_walls': metrics['ask_walls'],
            'timestamp': time.time()
        }
    
    # === Public API ===
    
    def get_imbalance(self) -> float:
        """Get current weighted order book imbalance."""
        if not self.imbalance_history:
            return 0.0
        return self.imbalance_history[-1]['value']
    
    def get_imbalance_trend(self, window: int = 20) -> float:
        """Get trend (slope) of imbalance over recent snapshots."""
        if len(self.imbalance_history) < window:
            return 0.0
        
        recent = [h['value'] for h in list(self.imbalance_history)[-window:]]
        x = np.arange(len(recent))
        coeffs = np.polyfit(x, recent, 1)
        return coeffs[0]  # slope
    
    def get_walls(self) -> dict:
        """Get current bid and ask walls."""
        if not self.current_book:
            return {'bid_walls': [], 'ask_walls': []}
        
        return {
            'bid_walls': self._detect_walls(self.current_book.bids, 'BID'),
            'ask_walls': self._detect_walls(self.current_book.asks, 'ASK')
        }
    
    def get_spread_status(self) -> dict:
        """Get current spread analysis."""
        if not self.current_book or len(self.spread_history) < 10:
            return {'status': 'INSUFFICIENT_DATA'}
        
        current = self.current_book.spread
        avg = np.mean(list(self.spread_history))
        
        return {
            'current_spread': current,
            'average_spread': avg,
            'spread_ratio': current / avg if avg > 0 else 1.0,
            'status': 'WIDE' if current > avg * 1.5 else 'NORMAL' if current > avg * 0.7 else 'TIGHT'
        }
```

### 10.2 Real-Time Data Pipeline

```python
import asyncio
import websockets
import json

class OrderBookPipeline:
    """
    Real-time pipeline for order book data ingestion and analysis.
    Supports both Forex (via CME market data) and Crypto (via exchange WebSocket).
    """
    
    def __init__(self, config):
        self.analyzer = OrderBookAnalyzer(config)
        self.symbol = config['symbol']
        self.exchange = config['exchange']
        self.callbacks = []
    
    async def connect_binance(self):
        """Connect to Binance WebSocket for order book updates."""
        symbol_lower = self.symbol.lower().replace('/', '')
        url = f"wss://stream.binance.com:9443/ws/{symbol_lower}@depth@100ms"
        
        # First, get initial snapshot
        snapshot = await self._get_snapshot_binance(symbol_lower)
        self._init_book_from_snapshot(snapshot)
        
        async with websockets.connect(url) as ws:
            async for message in ws:
                data = json.loads(message)
                book_state = self._process_binance_update(data)
                
                if book_state:
                    signal = self.analyzer.update(book_state)
                    
                    if signal:
                        for callback in self.callbacks:
                            await callback(signal)
    
    async def connect_cme(self, feed_handler):
        """Connect to CME MDP 3.0 for FX futures order book."""
        async for update in feed_handler.subscribe(self.symbol):
            book_state = self._process_cme_update(update)
            
            if book_state:
                signal = self.analyzer.update(book_state)
                
                if signal:
                    for callback in self.callbacks:
                        await callback(signal)
    
    def on_signal(self, callback):
        """Register a callback for order book signals."""
        self.callbacks.append(callback)
```

---

## 11. Core Logic — Entry/Exit

### 11.1 Order Book-Based Entry Signals

| Signal | Condition | Entry | Stop Loss | Take Profit |
|--------|-----------|-------|-----------|-------------|
| Strong Imbalance Long | WImb > 0.6 + delta confirmation | Market buy | Below bid wall | Next ask wall |
| Strong Imbalance Short | WImb < -0.6 + delta confirmation | Market sell | Above ask wall | Next bid wall |
| Absorption Long | Bid absorption detected, strength > 0.6 | Limit buy at absorption | Below absorption level | 2x distance to absorption |
| Absorption Short | Ask absorption detected, strength > 0.6 | Limit sell at absorption | Above absorption level | 2x distance to absorption |
| Wall Break Long | Major ask wall consumed + positive delta | Market buy on break | Below broken wall | Next resistance level |
| Wall Break Short | Major bid wall consumed + negative delta | Market sell on break | Above broken wall | Next support level |
| Spoof Fade Long | Spoof on ASK detected (hidden buyer) | Limit buy on pullback | Below recent low | Previous resistance |
| Spoof Fade Short | Spoof on BID detected (hidden seller) | Limit sell on rally | Above recent high | Previous support |

### 11.2 Order Book-Based Exit Signals

| Exit Condition | Description | Action |
|---------------|-------------|--------|
| Imbalance reversal | WImb crosses zero against position | Partial exit (50%) |
| Opposing wall forms | Large wall appears at profit target | Full exit |
| Spread blow-out | Spread > 3x average | Emergency exit |
| Absorption against | Absorption detected against position direction | Tighten stop to breakeven |
| Delta divergence | CVD diverges from price | Trailing stop activation |
| Volume exhaustion | Trade volume drops >70% from entry bar | Time-based exit |

---

## 12. Technical Specifications

### 12.1 Signal Parameters

| Parameter | Default | Range | Tuning Notes |
|-----------|---------|-------|-------------|
| `imbalance_levels` | 10 | [5, 20] | More levels = smoother signal, less responsive |
| `imbalance_decay` | 0.3 | [0.1, 0.8] | Higher = more weight on BBO; lower = deeper book matters |
| `imbalance_threshold` | 0.4 | [0.2, 0.7] | Higher = fewer signals, higher quality |
| `wall_threshold` | 3.0 | [2.0, 8.0] | Multiple of median depth to qualify as wall |
| `absorption_min_aggression` | 3 | [2, 10] | Min aggressive trades to qualify |
| `absorption_min_volume` | 500 | [100, 5000] | Asset-specific, in lots |
| `absorption_window_s` | 300 | [60, 900] | Time window for absorption detection |
| `iceberg_min_refills` | 3 | [2, 10] | Min refills to confirm iceberg |
| `iceberg_refill_delay_ms` | 500 | [100, 2000] | Max time between fill and refill |
| `spoof_size_multiple` | 5.0 | [3.0, 20.0] | Size vs average to flag as potential spoof |
| `spoof_lifetime_ms` | 2000 | [500, 5000] | Max lifetime for spoof classification |

### 12.2 Latency Requirements

| Component | Target | Maximum | Impact if Exceeded |
|-----------|--------|---------|-------------------|
| Data ingestion | <5ms | <20ms | Stale book state |
| Imbalance calculation | <1ms | <5ms | Delayed signals |
| Absorption detection | <2ms | <10ms | Missed absorption events |
| Signal generation | <1ms | <5ms | Late entry/exit |
| End-to-end | <10ms | <50ms | Reduced edge |

---

## 13. Risk Parameters

### 13.1 Position Sizing for Order Book Strategies

$$\text{Position Size} = \min\left(\frac{\text{Account} \times \text{RiskPct}}{\text{SL Distance}}, \frac{V_{bid}^{(1)} \times \text{MaxParticipation}}{1}\right)$$

Where:
- RiskPct = 0.5-1.0% per trade for microstructure strategies
- SL Distance = Distance to invalidation level (wall, absorption)
- $V_{bid}^{(1)}$ = Volume at best bid (approximate available liquidity)
- MaxParticipation = 0.05 (5% of visible liquidity)

### 13.2 Risk/Reward Targets

| Strategy | Min R:R | Typical R:R | Win Rate Target | Max Hold |
|----------|---------|-------------|----------------|----------|
| Imbalance scalp | 1.5:1 | 2:1 | >55% | 15 min |
| Absorption reversal | 2:1 | 3:1 | >50% | 2 hours |
| Wall break | 2:1 | 4:1 | >45% | 4 hours |
| Iceberg trade | 2:1 | 3:1 | >50% | 1 hour |

### 13.3 Maximum Drawdown Controls

| Parameter | Value | Action on Breach |
|-----------|-------|-----------------|
| Max daily loss | 3% of equity | Stop trading for day |
| Max consecutive losses | 5 | Reduce size by 50% |
| Max open positions | 3 | Wait for exit before new entry |
| Max exposure per pair | 2% of equity | Hard limit |

---

## 14. Execution Flow — Pseudocode

```python
# Complete execution flow for order book-based trading

async def order_book_trading_loop(config, data_feed, executor):
    """
    Main trading loop for order book analysis.
    
    This runs continuously, processing order book updates and
    generating/executing trading signals.
    """
    
    # Initialize components
    analyzer = OrderBookAnalyzer(config)
    risk_mgr = RiskManager(config)
    position_mgr = PositionManager()
    
    async for update in data_feed:
        
        # 1. UPDATE ORDER BOOK STATE
        if update.type == 'BOOK_SNAPSHOT':
            book_state = OrderBookState(
                bids=update.bids,
                asks=update.asks,
                timestamp=update.timestamp
            )
        elif update.type == 'BOOK_DELTA':
            book_state = apply_delta(current_book, update)
        elif update.type == 'TRADE':
            analyzer.absorption_detector.on_trade(
                price=update.price,
                volume=update.volume,
                side=update.side,
                timestamp=update.timestamp,
                best_bid=book_state.best_bid,
                best_ask=book_state.best_ask
            )
            continue  # Trades don't update the book state
        
        # 2. ANALYZE ORDER BOOK
        signal = analyzer.update(book_state)
        
        # 3. CHECK FOR ENTRY SIGNALS
        if signal and not position_mgr.has_position(config['symbol']):
            
            # Validate signal quality
            if signal['strength'] < config['min_signal_strength']:
                continue
            
            # Check risk limits
            if not risk_mgr.can_open_position():
                continue
            
            # Check session filter
            if config.get('session_filter') and not is_active_session():
                continue
            
            # Calculate entry parameters
            entry_price = book_state.best_ask if signal['direction'] == 'LONG' else book_state.best_bid
            
            sl_price = calculate_stop_loss(
                direction=signal['direction'],
                book_state=book_state,
                signal=signal
            )
            
            tp_price = calculate_take_profit(
                direction=signal['direction'],
                entry=entry_price,
                sl=sl_price,
                min_rr=config['min_rr']
            )
            
            position_size = risk_mgr.calculate_size(
                entry=entry_price,
                stop=sl_price,
                book_state=book_state
            )
            
            # Execute entry
            order = await executor.submit_order(
                symbol=config['symbol'],
                side='BUY' if signal['direction'] == 'LONG' else 'SELL',
                size=position_size,
                order_type='LIMIT',  # Use limit for better fill
                price=entry_price,
                stop_loss=sl_price,
                take_profit=tp_price,
                metadata={
                    'signal': signal,
                    'book_imbalance': analyzer.get_imbalance(),
                    'spread_status': analyzer.get_spread_status()
                }
            )
            
            position_mgr.register_position(order)
        
        # 4. CHECK FOR EXIT SIGNALS ON EXISTING POSITIONS
        elif position_mgr.has_position(config['symbol']):
            position = position_mgr.get_position(config['symbol'])
            
            exit_signal = check_exit_conditions(
                position=position,
                analyzer=analyzer,
                book_state=book_state
            )
            
            if exit_signal:
                await executor.close_position(
                    position=position,
                    reason=exit_signal['reason']
                )
                position_mgr.remove_position(config['symbol'])
```

---

## 15. References

### Academic Papers

1. **Cont, R., Kukanov, A., & Stoikov, S.** (2014). "The Price Impact of Order Book Events." *Journal of Financial Econometrics*, 12(1), 47-88. — Order book imbalance as predictive signal.

2. **Cont, R., Stoikov, S., & Talreja, R.** (2010). "A Stochastic Model for Order Book Dynamics." *Operations Research*, 58(3), 549-563. — Queuing theory model for order books.

3. **Gould, M. D., Porter, M. A., Williams, S., McDonald, M., Fenn, D. J., & Howison, S. D.** (2013). "Limit Order Books." *Quantitative Finance*, 13(11), 1709-1748. — Comprehensive review of LOB literature.

4. **Bouchaud, J. P., Mezard, M., & Potters, M.** (2002). "Statistical Properties of Stock Order Books: Empirical Results and Models." *Quantitative Finance*, 2(4), 251-256. — Empirical analysis of order book shape.

5. **Lee, C. M. C., & Ready, M. J.** (1991). "Inferring Trade Direction from Intraday Data." *Journal of Finance*, 46(2), 733-746. — Trade classification algorithm.

6. **Easley, D., Lopez de Prado, M. M., & O'Hara, M.** (2012). "Flow Toxicity and Liquidity in a High-Frequency World." *Review of Financial Studies*, 25(5), 1457-1493.

7. **Stoikov, S.** (2018). "The Micro-Price: A High-Frequency Estimator of Future Prices." *Quantitative Finance*, 18(12), 1959-1966. — Micro-price and order book imbalance.

8. **Huang, R., & Polak, T.** (2011). "LOBSTER: Limit Order Book System." — Tool for reconstructing LOB from NASDAQ ITCH data.

### Practitioner References

9. **Dalton, J. F., Jones, E. T., & Dalton, R. B.** (1993). *Mind Over Markets*. — Market Profile and auction theory foundations.

10. **Jigsaw Trading** — DOM and order flow platform documentation. Concepts of absorption, iceberg detection, and spoofing.

11. **Sierra Chart** — Detailed documentation on order flow analysis, footprint charts, and number bars.

12. **Bookmap** — Heatmap-based order book visualization and liquidity analysis documentation.

13. **Exocharts** — Crypto-specific footprint chart analysis and order flow tools.

14. **CME Group** — "CME Globex Market Data Platform (MDP 3.0)" — Specification for receiving Level 2 futures data.

---

> **Previous Document**: [00_overview.md](./00_overview.md) — Fundamentals of order flow and liquidity analysis
> **Next Document**: [02_liquidity_concepts.md](./02_liquidity_concepts.md) — Liquidity pools, Fair Value Gaps, and ICT liquidity concepts
