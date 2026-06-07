# การเก็งกำไรข้ามตลาด (Cross-Exchange Arbitrage) — เอกสารกลยุทธ์ฉบับสมบูรณ์

> **เวอร์ชันเอกสาร:** 2.0
> **อัปเดตล่าสุด:** 2026-04-12
> **การจัดประเภท:** Core Knowledge Base — Axis 2: ผลิตภัณฑ์ทางการเงิน
> **ประเภทกลยุทธ์:** Pure/Near Arbitrage (ความเสี่ยงขึ้นอยู่กับการดำเนินการ)
> **ตลาด:** Crypto (CeFi), Forex (ECN-to-ECN)
> **ความถี่:** Medium-High Frequency (วินาทีถึงนาที)

---

## สารบัญ

1. [ตรรกะหลัก — การตรวจจับส่วนต่างราคา](#1-ตรรกะหลัก--การตรวจจับส่วนต่างราคา)
2. [ข้อพิจารณาเวลาโอน](#2-ข้อพิจารณาเวลาโอน)
3. [กลยุทธ์ Pre-Positioning](#3-กลยุทธ์-pre-positioning)
4. [Latency Arbitrage](#4-latency-arbitrage)
5. [กรอบเปรียบเทียบค่าธรรมเนียม](#5-กรอบเปรียบเทียบค่าธรรมเนียม)
6. [แบบจำลองทางคณิตศาสตร์ — Minimum Profitable Spread](#6-แบบจำลองทางคณิตศาสตร์--minimum-profitable-spread)
7. [การเชื่อมต่อกับ Exchange APIs](#7-การเชื่อมต่อกับ-exchange-apis)
8. [อัลกอริทึมการดำเนินการฉบับสมบูรณ์](#8-อัลกอริทึมการดำเนินการฉบับสมบูรณ์)
9. [การจัดการความเสี่ยง](#9-การจัดการความเสี่ยง)
10. [การวิเคราะห์ผลงาน](#10-การวิเคราะห์ผลงาน)
11. [Production Deployment](#11-production-deployment)
12. [เอกสารอ้างอิง](#12-เอกสารอ้างอิง)

---

## 1. ตรรกะหลัก — การตรวจจับส่วนต่างราคา

### 1.1 แนวคิดพื้นฐาน

Cross-exchange arbitrage ใช้ประโยชน์จากความแตกต่างของราคาสำหรับสินทรัพย์เดียวกันข้ามช่องทางการเทรดที่แตกต่าง เมื่อสินทรัพย์ซื้อขายที่ $P_A$ บน Exchange A และ $P_B$ บน Exchange B และ $P_B > P_A + Costs$ นัก arbitrageur สามารถซื้อบน A และขายบน B เพื่อกำไรปลอดความเสี่ยง

### 1.2 เหตุใดส่วนต่างราคาจึงมีอยู่

1. **สภาพคล่องกระจัดกระจาย:** แต่ละตลาดมี order book อิสระ
2. **ฐานผู้ใช้ต่างกัน:** ตลาดระดับภูมิภาคอาจมีอุปสงค์/อุปทานต่างกัน
3. **ความล่าช้าในการฝาก/ถอน:** แรงเสียดทานในการย้ายสินทรัพย์ระหว่างช่องทาง
4. **โครงสร้างค่าธรรมเนียม:** ระดับ fee ที่แตกต่างส่งผลต่อราคาเทรดที่ใช้ได้จริง
5. **Fiat on/off ramps:** จุดเข้าถึงสกุลเงิน fiat ต่างกันสร้าง price premiums (เช่น "Kimchi premium" ในเกาหลีใต้)
6. **API latency:** ตลาดต่างๆ ประมวลผลและเผยแพร่ราคาด้วยความเร็วต่างกัน

### 1.3 ประเภทของ Cross-Exchange Arbitrage

```
Cross-Exchange Arbitrage
├── Simple Transfer Arbitrage
│   └── ซื้อบน A, โอนไป B, ขายบน B
│   └── ช้า, เสี่ยง (ราคาอาจเปลี่ยนระหว่างโอน)
│
├── Pre-Positioned Arbitrage (แนะนำ)
│   └── รักษายอดบนทั้งสองตลาด
│   └── ซื้อบน A, ขายบน B พร้อมกัน
│   └── ปรับสมดุลเป็นระยะ
│
├── Latency Arbitrage
│   └── ใช้ประโยชน์จากความเร็วต่างระหว่างการอัปเดตราคา
│
├── Cross-Venue (CEX-DEX) Arbitrage
│   └── ส่วนต่างราคาระหว่างตลาดแบบรวมศูนย์และกระจายศูนย์
│
└── Regional Premium Arbitrage
    └── ใช้ประโยชน์จาก price premiums ในภูมิภาคเฉพาะ
```

### 1.4 แบบจำลองติดตามสเปรด

$$\text{Spread}_{A \to B} = \frac{Bid_B - Ask_A}{Ask_A}$$

$$\text{Spread}_{B \to A} = \frac{Bid_A - Ask_B}{Ask_B}$$

**Effective spread (รวมความลึก):**

$$\text{Effective Ask}_A = \frac{\sum_{i=1}^{n} P_i^{ask} \times Q_i^{ask}}{\sum_{i=1}^{n} Q_i^{ask}} \quad \text{where} \quad \sum Q_i^{ask} \geq Q$$

---

## 2. ข้อพิจารณาเวลาโอน

### 2.1 เวลายืนยัน Blockchain

| สินทรัพย์/เครือข่าย | Block Time เฉลี่ย | การยืนยันที่ต้องการ | เวลารวม |
|---------------------|:------------------:|:---------------------:|:----------:|
| BTC (Bitcoin) | ~10 นาที | 2-6 | 20-60 นาที |
| ETH (Ethereum L1) | ~12 วินาที | 12-35 | 2.5-7 นาที |
| USDT (Tron TRC-20) | ~3 วินาที | 20 | ~1 นาที |
| SOL (Solana) | ~0.4 วินาที | 30+ | ~15 วินาที |
| XRP (Ripple) | ~4 วินาที | 1 | ~5 วินาที |

### 2.2 ผลกระทบต่อกลยุทธ์ Arbitrage

$$\text{Price Risk} = \sigma_{1min} \times \sqrt{T_{transfer}}$$

---

## 3. กลยุทธ์ Pre-Positioning

### 3.1 แนวคิด

Pre-positioning ขจัดความเสี่ยงจากความล่าช้าในการโอนโดยรักษายอดคงเหลือบนหลายตลาดพร้อมกัน แทนที่จะโอนสินทรัพย์หลังตรวจพบโอกาส คุณดำเนินการเทรดบนทั้งสองตลาดทันทีโดยใช้ยอดที่มีอยู่

### 3.2 ข้อกำหนดทุน

$$C_{total} = \sum_{i=1}^{N} (B_i^{base} \times P + B_i^{quote})$$

### 3.3 การปรับสมดุลยอด

**ทริกเกอร์การปรับสมดุล:**

$$\text{Imbalance Ratio} = \frac{|B_i^{actual} - B_i^{target}|}{B_i^{target}}$$

ปรับสมดุลเมื่อ $\text{Imbalance Ratio} > \text{threshold}$ (เช่น 30%)

### 3.4 อัลกอริทึมจัดการสินค้าคงคลัง

```python
class InventoryManager:
    """
    Manages pre-positioned balances across multiple exchanges.
    """
    
    def __init__(self, exchanges: List[str], target_balances: dict):
        self.exchanges = exchanges
        self.targets = target_balances
        self.actual = {}
    
    def check_rebalance_needed(self) -> List[dict]:
        actions = []
        for exchange in self.exchanges:
            for asset, target in self.targets[exchange].items():
                actual = self.actual.get(exchange, {}).get(asset, 0)
                imbalance = (actual - target) / target if target > 0 else 0
                
                if abs(imbalance) > 0.30:
                    deficit = target - actual
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
    
    def can_execute_arb(self, buy_exchange, sell_exchange, asset, quantity) -> bool:
        quote_balance = self.actual.get(buy_exchange, {}).get('USDT', 0)
        base_balance = self.actual.get(sell_exchange, {}).get(asset, 0)
        price = self.get_price(asset)
        return (quote_balance >= quantity * price * 1.10 and 
                base_balance >= quantity * 1.10)
```

---

## 4. Latency Arbitrage

### 4.1 แนวคิด

Latency arbitrage ใช้ประโยชน์จากความจริงที่ว่าตลาดต่างๆ อัปเดตราคาด้วยความเร็วต่างกัน ตลาดที่เร็วกว่าอาจสะท้อนข้อมูลใหม่ก่อนที่ตลาดที่ช้ากว่าจะปรับราคา

### 4.2 แหล่งที่มาของ Latency

| แหล่ง | Latency ทั่วไป | หมายเหตุ |
|--------|:--------------:|---------|
| Exchange matching engine | 0.1-10 ms | แตกต่างตามสถาปัตยกรรม |
| WebSocket propagation | 1-50 ms | ขึ้นอยู่กับตำแหน่งเซิร์ฟเวอร์ |
| Network path (same region) | 1-5 ms | AWS us-east to exchange |
| Network path (cross-region) | 50-200 ms | US ถึง Asia |
| Order submission | 5-50 ms | ขึ้นอยู่กับตลาด |

---

## 5. กรอบเปรียบเทียบค่าธรรมเนียม

### 5.1 แบบจำลองค่าธรรมเนียมครบถ้วน

$$C_{total} = C_{buy} + C_{sell} + C_{transfer} + C_{slippage}$$

### 5.2 ตารางเปรียบเทียบค่าธรรมเนียม

| ตลาด | Spot Maker | Spot Taker | ถอน (BTC) | ถอน (USDT-TRC20) |
|------|:----------:|:----------:|:---------:|:---------:|
| Binance | 0.10% | 0.10% | 0.0001 BTC | 1 USDT |
| Coinbase | 0.40% | 0.60% | Dynamic | Dynamic |
| OKX | 0.08% | 0.10% | 0.0001 BTC | 0.8 USDT |
| Bybit | 0.10% | 0.10% | 0.0002 BTC | 1 USDT |
| Kraken | 0.16% | 0.26% | 0.00015 BTC | 2.5 USDT |

---

## 6. แบบจำลองทางคณิตศาสตร์ — Minimum Profitable Spread

### 6.1 สูตร Minimum Spread

$$\boxed{\text{Spread}_{min} = f_A + f_B + s_A + s_B + \frac{F_{rebalance}}{Q \times P \times N_{avg}} + \epsilon}$$

โดยที่:
- $f_A$ = อัตราค่าธรรมเนียมฝั่งซื้อ
- $f_B$ = อัตราค่าธรรมเนียมฝั่งขาย
- $s_A, s_B$ = slippage ประมาณ
- $F_{rebalance}$ = ต้นทุนปรับสมดุล
- $N_{avg}$ = จำนวนเทรดเฉลี่ยระหว่างการปรับสมดุล
- $\epsilon$ = safety margin

### 6.2 ขนาดคำสั่งที่เหมาะสม

$$Q^* = \frac{\text{Spread} - S_{min}}{2\lambda}$$

โดยที่ $\lambda$ คือพารามิเตอร์ market impact

---

## 7. การเชื่อมต่อกับ Exchange APIs

```python
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

class BinanceConnector(ExchangeConnector):
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.binance.com"
        self.ws_url = "wss://stream.binance.com:9443/ws"

class OKXConnector(ExchangeConnector):
    def __init__(self, api_key: str, secret_key: str, passphrase: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://www.okx.com"
```

---

## 8. อัลกอริทึมการดำเนินการฉบับสมบูรณ์

```python
class CrossExchangeArbitrage:
    """
    Complete cross-exchange arbitrage engine.
    """
    
    async def scan_and_execute(self):
        while self.is_running:
            for pair in self.monitored_pairs:
                spread = self.calculate_spread(pair)
                
                if spread > self.min_spread:
                    if self.inventory.can_execute(pair, self.order_size):
                        result = await self.execute_arb(pair, spread)
                        self.update_pnl(result)
            
            await asyncio.sleep(0.01)
    
    async def execute_arb(self, pair, spread):
        """Execute simultaneous buy and sell."""
        buy_task = self.buy_exchange.place_order(pair, "BUY", ...)
        sell_task = self.sell_exchange.place_order(pair, "SELL", ...)
        
        buy_result, sell_result = await asyncio.gather(buy_task, sell_task)
        return self.calculate_result(buy_result, sell_result)
```

---

## 9. การจัดการความเสี่ยง

| ความเสี่ยง | การบรรเทา |
|------------|----------|
| ส่วนต่างราคาหายก่อนดำเนินการ | ใช้คำสั่ง IOC, ตรวจสอบ order book ก่อน |
| Partial fill | Unwind logic อัตโนมัติ |
| ตลาดล้มละลาย | จำกัดทุนต่อตลาด (< 30%) |
| การระงับการถอน | ติดตามสถานะตลาด, กระจายข้ามหลายตลาด |
| ยอดไม่สมดุล | ทริกเกอร์ปรับสมดุลอัตโนมัติ |

---

## 10. การวิเคราะห์ผลงาน

- ติดตาม: กำไรต่อการเทรด, win rate, Sharpe ratio
- การวิเคราะห์ spread: ขนาด, ระยะเวลา, ความถี่ตามเวลาของวัน
- ประสิทธิภาพการดำเนินการ: latency, fill rate, slippage จริง vs. ประมาณ

---

## 11. Production Deployment

- Cloud VPS ใกล้ตลาดหลัก (AWS Tokyo, Singapore)
- WebSocket connections ที่มี heartbeat monitoring
- ระบบ failover และ redundancy
- การตรวจสอบ rate limits แบบเรียลไทม์
- Alert system สำหรับสถานการณ์ผิดปกติ

---

## 12. เอกสารอ้างอิง

1. Makarov, I., & Schoar, A. (2020). "Trading and Arbitrage in Cryptocurrency Markets."
2. Binance API: https://binance-docs.github.io/apidocs/
3. OKX API: https://www.okx.com/docs/
4. CCXT: https://docs.ccxt.com/

---

> **เอกสารถัดไป**: [04_mev_defi_arbitrage.md](./04_mev_defi_arbitrage.md) — MEV & DeFi Arbitrage
