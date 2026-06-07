# การเก็งกำไรจาก Funding Rate (Cash-and-Carry) — เอกสารกลยุทธ์ฉบับสมบูรณ์

> **เวอร์ชันเอกสาร:** 2.0
> **อัปเดตล่าสุด:** 2026-04-12
> **การจัดประเภท:** Core Knowledge Base — Axis 2: ผลิตภัณฑ์ทางการเงิน
> **ประเภทกลยุทธ์:** Near-Arbitrage (ความเสี่ยงต่ำ, Delta-Neutral)
> **ตลาด:** Crypto (CeFi Perpetual Swaps)
> **ความถี่:** Low-Frequency (ถือสถานะชั่วโมงถึงสัปดาห์)

---

## สารบัญ

1. [ตรรกะหลัก — กลไก Funding Rate ของ Perpetual Swap](#1-ตรรกะหลัก--กลไก-funding-rate-ของ-perpetual-swap)
2. [กลยุทธ์ Delta Neutral — คำอธิบายโดยละเอียด](#2-กลยุทธ์-delta-neutral--คำอธิบายโดยละเอียด)
3. [กรอบทางคณิตศาสตร์](#3-กรอบทางคณิตศาสตร์)
4. [การคำนวณ APY จาก Funding Rates](#4-การคำนวณ-apy-จาก-funding-rates)
5. [การวิเคราะห์ความเสี่ยง Basis](#5-การวิเคราะห์ความเสี่ยง-basis)
6. [ข้อกำหนดมาร์จิ้นและความเสี่ยง Liquidation](#6-ข้อกำหนดมาร์จิ้นและความเสี่ยง-liquidation)
7. [Cross-Exchange Funding Rate Arbitrage](#7-cross-exchange-funding-rate-arbitrage)
8. [การวิเคราะห์ Funding Rate ในอดีต](#8-การวิเคราะห์-funding-rate-ในอดีต)
9. [เงื่อนไขเข้าและออก](#9-เงื่อนไขเข้าและออก)
10. [ขั้นตอนการดำเนินการฉบับสมบูรณ์](#10-ขั้นตอนการดำเนินการฉบับสมบูรณ์)
11. [การจัดการความเสี่ยง](#11-การจัดการความเสี่ยง)
12. [Position Sizing และการจัดสรรทุน](#12-position-sizing-และการจัดสรรทุน)
13. [เอกสารอ้างอิง](#13-เอกสารอ้างอิง)

---

## 1. ตรรกะหลัก — กลไก Funding Rate ของ Perpetual Swap

### 1.1 Perpetual Swap คืออะไร?

Perpetual swap (เรียกอีกว่า perpetual future หรือ "perp") คือสัญญาอนุพันธ์ที่:
- ติดตามราคาของสินทรัพย์อ้างอิง (เช่น BTC, ETH)
- **ไม่มีวันหมดอายุ** (ต่างจาก futures แบบดั้งเดิม)
- ใช้**กลไก funding rate** เพื่อยึดราคาสัญญากับราคา spot
- อนุญาตให้ใช้เลเวอเรจ (ปกติ 1x ถึง 125x)
- ชำระแบบเรียลไทม์ (mark-to-market)

### 1.2 กลไก Funding Rate

Funding rate คือการจ่ายเป็นระยะระหว่างผู้ถือสถานะ long และ short ออกแบบมาเพื่อรักษาราคา perpetual swap ให้สอดคล้องกับราคา spot

**ตรรกะพื้นฐาน:**

- เมื่อ **ราคา perp > ราคา spot** (premium): Long จ่าย Short (funding rate เป็นบวก)
- เมื่อ **ราคา perp < ราคา spot** (discount): Short จ่าย Long (funding rate เป็นลบ)

### 1.3 สูตรคำนวณ Funding Rate

**สูตรมาตรฐาน (Binance/Bybit/OKX):**

$$\text{Funding Rate} = \text{Premium Index} + \text{clamp}(\text{Interest Rate} - \text{Premium Index}, -0.05\%, +0.05\%)$$

โดยที่:

$$\text{Premium Index} = \frac{\text{Mark Price} - \text{Index Price}}{\text{Index Price}}$$

$$\text{Interest Rate} = \frac{\text{Quote Interest Rate} - \text{Base Interest Rate}}{\text{Funding Interval}}$$

### 1.4 การคำนวณ Funding Payment

$$\text{Funding Payment} = \text{Position Size} \times \text{Funding Rate}$$

- ถ้า Funding Rate > 0: Long จ่าย, Short รับ
- ถ้า Funding Rate < 0: Short จ่าย, Long รับ

**ตาราง Payment:**

| ตลาด | ความถี่ | เวลา (UTC) |
|------|---------|------------|
| Binance | ทุก 8 ชั่วโมง | 00:00, 08:00, 16:00 |
| Bybit | ทุก 8 ชั่วโมง | 00:00, 08:00, 16:00 |
| OKX | ทุก 8 ชั่วโมง | 00:00, 08:00, 16:00 |
| dYdX | ทุก 1 ชั่วโมง | รายชั่วโมง |
| Drift (Solana) | ต่อเนื่อง | เรียลไทม์ |

### 1.5 อะไรสร้าง Funding Rates ที่สูง?

| สภาวะตลาด | Funding Rate ทั่วไป | สาเหตุ |
|-----------|:-------------------:|--------|
| ตลาดกระทิงรุนแรง | +0.1% ถึง +0.3% ต่อ 8h | เลเวอเรจ long มากเกิน |
| ตลาดกระทิงแข็ง | +0.03% ถึง +0.1% ต่อ 8h | อคติ long ปานกลาง |
| ตลาดเป็นกลาง | -0.01% ถึง +0.01% ต่อ 8h | อุปสงค์สมดุล |
| ตลาดหมีแข็ง | -0.1% ถึง -0.03% ต่อ 8h | อคติ short ปานกลาง |
| ตลาดหมีรุนแรง | -0.3% ถึง -0.1% ต่อ 8h | เลเวอเรจ short มากเกิน |
| Liquidation cascade | +/- 0.5% ถึง 0.75% ต่อ 8h | Forced liquidations |

---

## 2. กลยุทธ์ Delta Neutral — คำอธิบายโดยละเอียด

### 2.1 แนวคิดหลัก

Funding rate arbitrage เป็นกลยุทธ์ **delta-neutral** ที่ทำกำไรจาก funding payments โดยไม่รับความเสี่ยงทิศทางตลาด กลยุทธ์ถือพร้อมกัน:
- สถานะ **spot** (หรือเทียบเท่า)
- สถานะ **perpetual swap ตรงข้าม** ขนาดเท่ากัน

สองสถานะหักล้างการเปิดรับราคาของกันและกัน (delta = 0) ขณะที่ funding rate payments ให้กระแสรายได้ที่สม่ำเสมอ

### 2.2 กลยุทธ์ A: Long Spot + Short Perpetual (Funding เป็นบวก)

**เมื่อใช้:** เมื่อ funding rate เป็นบวก (ราคา perp > ราคา spot, อารมณ์ตลาดกระทิง)

```
┌─────────────────────────────────────────┐
│         LONG SPOT + SHORT PERP           │
│                                          │
│  Spot Exchange:    BUY 1 BTC @ $65,000   │
│  Perp Exchange:    SHORT 1 BTC @ $65,200 │
│                                          │
│  Net Delta: +1 BTC - 1 BTC = 0 BTC      │
│  Net Exposure: ZERO (market neutral)     │
│                                          │
│  Income: Receive funding every 8 hours   │
│  (because we are SHORT when funding > 0) │
└─────────────────────────────────────────┘
```

### 2.3 กลยุทธ์ B: Short Spot (Margin) + Long Perpetual (Funding เป็นลบ)

**เมื่อใช้:** เมื่อ funding rate เป็นลบ (ราคา perp < ราคา spot, อารมณ์หมี)

### 2.4 กลยุทธ์ C: Cross-Exchange Funding Arbitrage

**เมื่อใช้:** เมื่อ funding rates ต่างกันอย่างมีนัยสำคัญข้ามตลาด

```
┌─────────────────────────────────────────┐
│   CROSS-EXCHANGE FUNDING ARBITRAGE       │
│                                          │
│  Exchange A:  LONG BTC perp              │
│               (funding = -0.02%)         │
│               → เรา RECEIVE funding      │
│                                          │
│  Exchange B:  SHORT BTC perp             │
│               (funding = +0.08%)         │
│               → เรา RECEIVE funding      │
│                                          │
│  Net Delta: +1 BTC - 1 BTC = 0 BTC      │
│  Income: 0.02% + 0.08% = 0.10% per 8h   │
└─────────────────────────────────────────┘
```

---

## 3. กรอบทางคณิตศาสตร์

### 3.1 สูตร P&L สุทธิ

สำหรับกลยุทธ์ A (Long Spot + Short Perp) ตลอดระยะเวลาถือ $T$:

$$P\&L_{net} = \sum_{t=1}^{N} F_t \times Q \times P_t - C_{entry} - C_{exit} - C_{funding\_fee} - C_{opportunity}$$

โดยที่:
- $F_t$ = funding rate ณ เวลา $t$
- $Q$ = ปริมาณสถานะ (ในหน่วยสินทรัพย์อ้างอิง)
- $P_t$ = mark price ณ เวลา funding $t$
- $N$ = จำนวน funding intervals ระหว่างระยะเวลาถือ

### 3.2 สูตร APY แบบรายปี

$$APY = \left(\frac{\sum_{t=1}^{N} F_t}{N}\right) \times \frac{365 \times 24}{h} \times \frac{Q \times \bar{P}}{C_{total}} - \frac{C_{entry} + C_{exit}}{C_{total}} \times \frac{365}{T_{days}}$$

**APY แบบง่าย:**

$$APY_{simple} = \bar{F} \times \frac{365 \times 3}{1} \times \frac{1}{L}$$

สำหรับ $L = 1$ (fully collateralized): $APY = \bar{F} \times 1095$

ตัวอย่าง ถ้า average funding rate คือ 0.03% ต่อ 8 ชั่วโมง:

$$APY = 0.0003 \times 1095 = 0.3285 = 32.85\%$$

### 3.3 ประสิทธิภาพทุนด้วยเลเวอเรจ

$$C_{total} = Q \times P \times \left(1 + \frac{1}{\ell}\right)$$

$$APY_{leveraged} = \frac{\bar{F} \times 1095}{1 + 1/\ell}$$

### 3.4 Break-Even Funding Rate

$$F_{min} = \frac{(f_{spot} + f_{perp}) \times 2}{N_{expected}}$$

### 3.5 Basis Dynamics Model

$$B_t = P_{perp,t} - P_{spot,t}$$

$$b_t = \frac{P_{perp,t} - P_{spot,t}}{P_{spot,t}}$$

**Basis mean-reversion model:**

$$b_t = \mu_b + \phi (b_{t-1} - \mu_b) + \epsilon_t$$

---

## 4. การคำนวณ APY จาก Funding Rates

### 4.1 APY ย้อนหลัง

$$APY_{historical} = \left(\prod_{t=1}^{N} (1 + F_t)\right)^{365 \times 3 / N} - 1$$

### 4.2 APY ที่ปรับตามความเสี่ยง

$$APY_{risk-adj} = APY_{gross} - C_{entry/exit} - C_{margin} - C_{liquidation\_risk} - C_{basis\_risk}$$

### 4.3 APY ตามสินทรัพย์ — ช่วงในอดีต

| สินทรัพย์ | APY ทั่วไป (กระทิง) | APY ทั่วไป (เป็นกลาง) | APY ทั่วไป (หมี) |
|-----------|:------------------:|:---------------------:|:------------------:|
| BTC | 15-40% | 5-15% | -5% ถึง 5% |
| ETH | 20-50% | 8-20% | -5% ถึง 8% |
| SOL | 25-80% | 10-30% | -10% ถึง 10% |
| DOGE | 30-100%+ | 5-25% | -20% ถึง 5% |
| Alt ความผันผวนสูง | 50-200%+ | 10-50% | -30% ถึง 10% |

---

## 5. การวิเคราะห์ความเสี่ยง Basis

### 5.1 Basis Risk คืออะไร?

ความเสี่ยง basis ใน funding rate arbitrage คือความเสี่ยงที่สเปรดระหว่างราคา perpetual และราคา spot เปลี่ยนแปลงในทิศทางที่ไม่เอื้อระหว่างระยะเวลาถือ

### 5.2 การวัด Basis Risk

**Value at Risk (VaR) จากการเคลื่อนตัวของ basis:**

$$VaR_{basis} = Q \times P \times z_{\alpha} \times \sigma_b \times \sqrt{T}$$

### 5.3 การบรรเทา Basis Risk

1. ติดตาม basis แบบเรียลไทม์: ตั้ง alerts สำหรับ basis widening ที่ผิดปกติ
2. รักษา margin เกินขีด: รักษา margin สูงกว่าระดับ maintenance
3. ขนาดสถานะแบบอนุรักษ์: ไม่ maximize leverage
4. ตั้ง conditional exit orders: ปิดหาก basis เกินเกณฑ์
5. กระจายข้ามสินทรัพย์: สินทรัพย์ต่างๆ มี basis movements ที่ไม่สัมพันธ์กัน

---

## 6. ข้อกำหนดมาร์จิ้นและความเสี่ยง Liquidation

### 6.1 กลไกมาร์จิ้น

$$\text{Initial Margin} = \frac{\text{Position Notional}}{\text{Leverage}}$$

$$\text{Maintenance Margin} = \text{Position Notional} \times \text{MMR}$$

### 6.2 การคำนวณราคา Liquidation

สำหรับสถานะ **short** perpetual:

$$P_{liq}^{short} = P_{entry} \times \left(1 + \frac{1}{leverage} - MMR\right)$$

| เลเวอเรจ | MMR (0.5%) | การเคลื่อนสูงสุดก่อน Liquidation |
|:--------:|:----------:|:---------------------------:|
| 2x | 0.5% | 49.5% |
| 3x | 0.5% | 32.8% |
| 5x | 0.5% | 19.5% |
| 10x | 0.5% | 9.5% |
| 20x | 0.5% | 4.5% |

**คำแนะนำ:** ใช้เลเวอเรจ 2-5x สำหรับ funding rate arbitrage ให้บัฟเฟอร์ 20-50% ก่อน liquidation

---

## 7. Cross-Exchange Funding Rate Arbitrage

### 7.1 คำอธิบายกลยุทธ์

ตลาดต่างๆ มักเสนอ funding rates ที่แตกต่างกันสำหรับสินทรัพย์เดียวกัน

**ใช้ประโยชน์:** Long บนตลาดที่ funding ต่ำกว่า (หรือลบ) และ Short บนตลาดที่ funding สูงกว่า (หรือบวก) เก็บส่วนต่าง

### 7.2 ข้อกำหนดทุน

$$C_{total} = \frac{Q \times P}{leverage_A} + \frac{Q \times P}{leverage_B}$$

### 7.3 ความเสี่ยง Cross-Exchange

1. ความเสี่ยงคู่สัญญา: ทุนเปิดรับกับสองตลาด
2. ความเสี่ยง Liquidation ทั้งสองฝั่ง
3. Funding rate convergence: สเปรดอาจลดลง
4. ทุนกระจัดกระจาย: ย้ายทุนระหว่างตลาดไม่ง่าย

---

## 8. การวิเคราะห์ Funding Rate ในอดีต

```python
class FundingRateAnalyzer:
    """
    Analyze historical funding rates to assess viability of funding rate arbitrage.
    """
    
    def __init__(self, funding_data: pd.DataFrame):
        self.data = funding_data
    
    def calculate_statistics(self, symbol: str) -> dict:
        rates = self.data[self.data['symbol'] == symbol]['funding_rate']
        return {
            'mean': rates.mean(),
            'median': rates.median(),
            'std': rates.std(),
            'pct_positive': (rates > 0).mean(),
            'annualized_yield': rates.mean() * 1095,
            'sharpe': (rates.mean() * 1095) / (rates.std() * np.sqrt(1095)),
        }
    
    def calculate_persistence(self, symbol: str) -> dict:
        """Analyze persistence of funding rate sign."""
        rates = self.data[self.data['symbol'] == symbol]['funding_rate']
        signs = np.sign(rates)
        # Calculate run lengths
        runs = []
        current_run = 1
        for i in range(1, len(signs)):
            if signs.iloc[i] == signs.iloc[i-1]:
                current_run += 1
            else:
                runs.append((signs.iloc[i-1], current_run))
                current_run = 1
        return {
            'autocorrelation_lag1': rates.autocorr(lag=1),
            'autocorrelation_lag3': rates.autocorr(lag=3),
        }
```

---

## 9. เงื่อนไขเข้าและออก

### 9.1 เงื่อนไขเข้า

- Funding rate > เกณฑ์ขั้นต่ำ (เช่น > 0.03% ต่อ 8h)
- Funding rate เป็นบวกอย่างน้อย 3 ช่วงติดต่อกัน
- Basis ไม่อยู่ที่จุดสูงสุด (ไม่เข้าเมื่อ basis กว้างผิดปกติ)
- สภาพคล่องเพียงพอบนทั้ง spot และ perp
- ไม่มีเหตุการณ์ตลาดสำคัญที่กำลังจะมา

### 9.2 เงื่อนไขออก

- Funding rate ลดลงต่ำกว่าจุดคุ้มทุน
- Funding rate กลับทิศ (กลายเป็นลบ)
- Basis ขยายตัวเกินเกณฑ์ความทนทาน
- ถึงเป้าหมายกำไร
- Circuit breaker ทำงาน

---

## 10. ขั้นตอนการดำเนินการฉบับสมบูรณ์

```python
class FundingRateArbitrage:
    """
    Complete funding rate arbitrage execution engine.
    """
    
    async def execute_entry(self, symbol: str, size: float):
        """Enter delta-neutral position."""
        # 1. Buy spot
        spot_order = await self.spot_exchange.buy(symbol, size)
        
        # 2. Open short perp (same size)
        perp_order = await self.perp_exchange.short(symbol, size)
        
        # 3. Verify delta neutrality
        assert abs(spot_order.filled - perp_order.filled) < tolerance
        
        # 4. Record entry
        self.position = Position(
            symbol=symbol,
            spot_size=spot_order.filled,
            perp_size=perp_order.filled,
            entry_basis=self.get_basis(symbol),
            entry_time=time.time()
        )
    
    async def monitor_position(self):
        """Continuous position monitoring."""
        while self.position.is_active:
            # Check funding collection
            funding = await self.collect_funding()
            self.position.total_funding += funding
            
            # Check exit conditions
            if self.should_exit():
                await self.execute_exit()
                break
            
            # Check health
            if self.margin_at_risk():
                await self.add_margin_or_reduce()
            
            await asyncio.sleep(60)  # Check every minute
```

---

## 11. การจัดการความเสี่ยง

| พารามิเตอร์ | ค่า | เหตุผล |
|------------|------|--------|
| เลเวอเรจสูงสุด | 5x | บัฟเฟอร์ 19.5% ก่อน liquidation |
| ขนาดสถานะสูงสุดต่อสินทรัพย์ | 20% ของทุน | การกระจาย |
| Basis alert threshold | +/- 2% | เตือนเมื่อ basis ขยาย |
| Stop loss (basis) | +/- 5% | ออกหาก basis ขยายเกิน |
| ระยะเวลาถือสูงสุด | 30 วัน | ประเมินใหม่เป็นระยะ |

---

## 12. Position Sizing และการจัดสรรทุน

$$\text{Position Size} = \frac{\text{Capital} \times \text{Allocation \%}}{1 + 1/\text{leverage}}$$

---

## 13. เอกสารอ้างอิง

1. Binance Futures Documentation: https://www.binance.com/en/futures
2. Bybit Perpetual Documentation: https://www.bybit.com/
3. "The Basis Trade" — Various crypto research papers
4. Coinglass Funding Rate Data: https://www.coinglass.com/FundingRate

---

> **เอกสารถัดไป**: [03_cross_exchange_arbitrage.md](./03_cross_exchange_arbitrage.md) — Cross-Exchange Arbitrage
