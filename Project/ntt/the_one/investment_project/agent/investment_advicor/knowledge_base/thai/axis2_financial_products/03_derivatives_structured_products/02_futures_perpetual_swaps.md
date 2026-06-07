# ฟิวเจอร์สและสัญญาถาวร: คู่มือครบถ้วน

> **แกนที่ 2 — ผลิตภัณฑ์ทางการเงิน | โมดูล 03: อนุพันธ์และผลิตภัณฑ์ที่มีโครงสร้าง**
> **เอกสาร 02 — ฟิวเจอร์สและสัญญาถาวร (Futures & Perpetual Swaps)**
> **เวอร์ชัน:** 2.0
> **อัปเดตล่าสุด:** 2026-04-12
> **ผู้เขียน:** ทีมวิจัยการเงินอาวุโส
> **การจัดประเภท:** ฐานความรู้หลัก — ระบบเทรด AI แบบ Multi-Agent

---

## สารบัญ

1. [ตรรกะหลัก](#1-ตรรกะหลัก)
2. [ข้อกำหนดทางเทคนิค](#2-ข้อกำหนดทางเทคนิค)
3. [แบบจำลองทางคณิตศาสตร์](#3-แบบจำลองทางคณิตศาสตร์)
4. [พารามิเตอร์ความเสี่ยง](#4-พารามิเตอร์ความเสี่ยง)
5. [ขั้นตอนการดำเนินการ](#5-ขั้นตอนการดำเนินการ)
6. [เอกสารอ้างอิง](#6-เอกสารอ้างอิง)

---

## 1. ตรรกะหลัก

### 1.1 กลไกสัญญาฟิวเจอร์ส

สัญญาฟิวเจอร์สเป็นข้อตกลงผูกมัดระหว่างสองฝ่ายในการซื้อหรือขายสินทรัพย์ในราคาที่กำหนดไว้ล่วงหน้า ณ วันที่ระบุในอนาคต ต่างจากออปชัน ทั้งสองฝ่ายมีภาระผูกพันต้องปฏิบัติตามสัญญา

#### 1.1.1 องค์ประกอบสำคัญ

| องค์ประกอบ | คำอธิบาย |
|---|---|
| **สินทรัพย์อ้างอิง (Underlying)** | สินทรัพย์ที่เทรด (BTC, ETH, EUR/USD เป็นต้น) |
| **ขนาดสัญญา (Contract Size)** | มูลค่าตามสัญญาต่อหนึ่งสัญญา |
| **Tick Size** | การเปลี่ยนแปลงราคาขั้นต่ำ |
| **วันหมดอายุ (Expiration Date)** | วันที่สัญญาชำระบัญชี |
| **วิธีชำระบัญชี (Settlement Method)** | เงินสดหรือส่งมอบจริง |
| **มาร์จิ้น (Margin)** | หลักประกันที่ต้องวางเพื่อถือสถานะ |
| **Mark Price** | มูลค่ายุติธรรมที่ใช้คำนวณมาร์จิ้น |
| **Index Price** | ราคา Spot แบบรวมจากหลายตลาด |

#### 1.1.2 ประเภทฟิวเจอร์สคริปโต

**ฟิวเจอร์สเชิงเส้น (Linear Futures — USDT/USDC-margined):**
- มาร์จิ้นและชำระบัญชีเป็น Stablecoin (USDT หรือ USDC)
- การคำนวณ P&L ตรงไปตรงมา: $(Exit - Entry) \times Quantity$
- ไม่มี Convexity ใน P&L (ความสัมพันธ์เชิงเส้นกับสินทรัพย์อ้างอิง)
- เหมาะสำหรับผู้เริ่มต้นและการจัดการความเสี่ยงที่ง่ายกว่า

**ฟิวเจอร์สผกผัน (Inverse Futures — Coin-margined):**
- มาร์จิ้นและชำระบัญชีเป็นคริปโตอ้างอิง
- P&L เป็น BTC/ETH: $Contracts \times (\frac{1}{Entry} - \frac{1}{Exit})$
- มี Payoff ไม่เชิงเส้น (Convex) สำหรับฝ่าย Long:
  - เมื่อ BTC ขึ้น: กำไรเป็น BTC และ BTC มีค่ามากขึ้น (ประโยชน์สองทาง)
  - เมื่อ BTC ลง: ขาดทุนเป็น BTC และ BTC มีค่าน้อยลง (เจ็บสองทาง)

#### 1.1.3 ระบบมาร์จิ้น

**มาร์จิ้นเริ่มต้น (Initial Margin):** หลักประกันขั้นต่ำที่ต้องวางเพื่อเปิดสถานะ

$$\text{Initial Margin} = \frac{\text{Notional Value}}{\text{Leverage}} + \text{Opening Fee}$$

**มาร์จิ้นรักษาสภาพ (Maintenance Margin):** ส่วนของเจ้าของขั้นต่ำที่ต้องมีเพื่อรักษาสถานะ

$$\text{Maintenance Margin} = \text{Notional Value} \times \text{Maintenance Rate}$$

**โหมดมาร์จิ้น:**

| โหมด | คำอธิบาย | ความเสี่ยง |
|---|---|---|
| **Isolated** | แต่ละสถานะมีมาร์จิ้นแยกต่างหาก | การล้างสถานะกระทบเฉพาะสถานะนั้น |
| **Cross** | ทุกสถานะแชร์ยอดเงินในบัญชี | สถานะหนึ่งอาจถูกช่วยจากกำไรของสถานะอื่น |
| **Portfolio** | มาร์จิ้นคำนวณจากความเสี่ยงพอร์ตโดยรวม | ใช้เงินทุนอย่างมีประสิทธิภาพที่สุด; ต้องการความเชี่ยวชาญ |

### 1.2 Basis และ Contango/Backwardation

#### 1.2.1 นิยาม Basis

$$\text{Basis} = F_t - S_t$$

**Basis Yield รายปี:**

$$\text{Basis Yield (annualized)} = \frac{F_t - S_t}{S_t} \times \frac{365}{T}$$

โดยที่ $T$ = จำนวนวันจนหมดอายุ

#### 1.2.2 Contango

**Contango** เกิดขึ้นเมื่อฟิวเจอร์สซื้อขายเหนือ Spot: $F > S$ (Basis เป็นบวก)

**สาเหตุในคริปโต:**
- ความต้องการ Leveraged Long Exposure เกินอุปทานจากการ Hedge
- Carry เป็นบวก (อัตราดอกเบี้ยเงินกู้ > Staking Yield)
- ความรู้สึกขาขึ้น
- ความต้องการฟิวเจอร์สจากสถาบัน (Contango ของ CME มักคงอยู่)

**Contango ทั่วไปในคริปโต:**
- ตลาดปกติ: 5-15% ต่อปี
- ตลาดขาขึ้น: 20-50% ต่อปี
- ช่วงตื่นเต้นสูงสุด: 50-100%+ ต่อปี

#### 1.2.3 Backwardation

**Backwardation** เกิดขึ้นเมื่อฟิวเจอร์สซื้อขายต่ำกว่า Spot: $F < S$ (Basis เป็นลบ)

**สาเหตุในคริปโต:**
- ความรู้สึกขาลง แรงกดดันจากการ Hedge
- DeFi/Staking Yields สูงเกินอัตราดอกเบี้ยเงินกู้
- การขายตื่นตกใจระยะสั้น
- การล้างสถานะ Long Futures แบบบังคับ

### 1.3 กลไกสัญญาถาวร (Perpetual Swap)

#### 1.3.1 สัญญาถาวรคืออะไร?

สัญญาถาวร (Perp) เป็นอนุพันธ์เฉพาะของตลาดคริปโต — สัญญาฟิวเจอร์สที่ไม่มีวันหมดอายุ สามารถถือสถานะได้ไม่จำกัด โดยราคาถูกยึดกับ Spot ผ่านกลไก Funding Rate

**นวัตกรรมสำคัญ:** BitMEX (Arthur Hayes) คิดค้นสัญญาถาวรในปี 2016 ตั้งแต่นั้นมาได้กลายเป็นเครื่องมืออนุพันธ์คริปโตหลัก

**การครองตลาด:**
- สัญญาถาวรคิดเป็น >70% ของปริมาณอนุพันธ์คริปโตทั้งหมด
- เทรด 24/7 ไม่ต้อง Rollover
- เครื่องมือหลักสำหรับการเก็งกำไรและ Hedging ในคริปโต

#### 1.3.2 กลไก Funding Rate

Funding Rate คือการจ่ายเงินเป็นระยะระหว่างผู้ถือสถานะ Long และ Short เพื่อรักษาราคาสัญญาถาวรให้ใกล้เคียงกับ Spot Index Price

**การคำนวณ (แบบ Binance):**

$$\text{Funding Rate} = \text{Average Premium Index} + \text{clamp}(I - P, -d, d)$$

โดยที่:
- $I$ = องค์ประกอบอัตราดอกเบี้ย (ปกติ 0.01% ต่อ 8h สำหรับคริปโต)
- $P$ = Premium Index (วัดการเบี่ยงเบนจาก Spot)
- $d$ = Dampener (ปกติ 0.05%)

**การจ่ายเงิน Funding:**

$$\text{Payment} = \text{Position Notional} \times \text{Funding Rate}$$

**กฎการจ่ายเงิน:**
- ถ้า Funding Rate > 0: ฝ่าย Long จ่ายให้ฝ่าย Short
- ถ้า Funding Rate < 0: ฝ่าย Short จ่ายให้ฝ่าย Long

**Funding Rate รายปี:**

$$\text{APR}_{funding} = \text{Funding Rate per interval} \times \frac{365 \times 24}{\text{Interval (hours)}}$$

ตัวอย่าง: 0.01% ต่อ 8h = 0.01% × 3 × 365 = 10.95% APR

### 1.4 การ Hedge ด้วยฟิวเจอร์ส

#### 1.4.1 Delta Hedging

Hedge ที่ง่ายที่สุด: หักล้าง Directional Exposure ของสถานะโดยใช้ฟิวเจอร์ส

**Perfect Hedge (1:1):**
- Long 1 BTC Spot → Short 1 BTC Futures/Perp
- Net Delta = 0

#### 1.4.2 Cross-Hedging

เมื่อไม่มีฟิวเจอร์สสำหรับสินทรัพย์นั้นโดยตรง ให้ใช้ฟิวเจอร์สของสินทรัพย์ที่มีสหสัมพันธ์กัน

**อัตราส่วน Hedge ข้ามสินทรัพย์:**

$$h^* = \rho_{S,F} \times \frac{\sigma_S}{\sigma_F}$$

#### 1.4.3 อัตราส่วน Hedge แบบ Minimum Variance

$$h^* = \frac{\text{Cov}(S, F)}{\text{Var}(F)} = \rho \frac{\sigma_S}{\sigma_F}$$

### 1.5 กลยุทธ์ Basis Trading

#### 1.5.1 Cash-and-Carry Arbitrage

**กลยุทธ์:** ซื้อ Spot ขาย Futures ล็อค Basis เป็นกำไรปลอดความเสี่ยง

**P&L:**

$$\text{P\&L} = (F_0 - S_0) - \text{costs}$$

**ผลตอบแทนรายปี:**

$$r_{carry} = \frac{F_0 - S_0}{S_0} \times \frac{365}{T_{days}} - \text{cost rate}$$

#### 1.5.3 Funding Rate Arbitrage (Cash-and-Carry กับ Perps)

**กลยุทธ์:** การเทรด Basis ที่พบมากที่สุดในคริปโต ซื้อ Spot, Short สัญญาถาวร เก็บ Funding Rate

**การสร้างสถานะ:**
- ซื้อ 1 BTC Spot (หรือใช้ Staking เพื่อรับ Yield เพิ่ม)
- Short 1 BTC สัญญาถาวร
- Delta Neutral: ไม่มี Directional Exposure
- เก็บ Funding Rate บวก (ถ้า Funding > 0 ฝ่าย Short ได้รับ)

**ผลตอบแทนคาดหวัง:**

$$r_{funding} = \text{Avg Funding Rate} \times 3 \times 365 - \text{costs}$$

### 1.6 การจัดการเลเวอเรจและ Liquidation

#### 1.6.1 การคำนวณเลเวอเรจ

$$\text{Leverage} = \frac{\text{Position Notional}}{\text{Account Equity}}$$

#### 1.6.2 การคำนวณราคา Liquidation

**สำหรับสถานะ Long (Isolated Margin):**

$$P_{liq,long} \approx Entry Price \times \left(1 - \frac{1}{Leverage} + MMR\right)$$

**สำหรับสถานะ Short (Isolated Margin):**

$$P_{liq,short} \approx Entry Price \times \left(1 + \frac{1}{Leverage} - MMR\right)$$

#### 1.6.4 Liquidation Cascades

Liquidation Cascade เกิดขึ้นเมื่อการบังคับปิดสถานะที่ใช้เลเวอเรจทำให้ราคาเคลื่อนไหวต่อ ซึ่งกระตุ้นการล้างสถานะเพิ่มเติมแบบลูกโซ่

**พฤติกรรมบอทระหว่าง Cascades:**
- อย่าเปิดสถานะใหม่เข้าไปใน Cascade
- อย่าตั้ง Stop-loss ที่จะถูกกระตุ้นระหว่าง Cascade (ใช้ Mark Price ไม่ใช่ Last Price)
- ถ้ามี Basis Trade: ให้มั่นใจว่ามีมาร์จิ้นเพียงพอเพื่อรอดจากการพุ่งของราคา
- พิจารณาเพิ่มสถานะหลัง Cascade หมดแรง (Contrarian แต่ต้องมีความเสี่ยงเข้มงวด)

---

## 2. ข้อกำหนดทางเทคนิค

### 2.1 ข้อกำหนดข้อมูลสำหรับการเทรดฟิวเจอร์ส/Perps

```
FUTURES_DATA_SOURCES:

  real_time:
    spot_price:
      sources: [binance, coinbase, kraken, okx, bybit]
      aggregation: median of top-3 by volume
      update_frequency: 100ms

    perpetual_data:
      mark_price: per exchange, 100ms
      last_price: per exchange, tick-level
      funding_rate:
        current: real-time predicted next funding
        next_settlement: countdown timer
      open_interest: per exchange, 1s update
      liquidations: real-time feed

    order_book:
      depth: L2 (top 20 levels minimum)
      update_frequency: 100ms
      impact_price: calculated for 100K, 500K, 1M USD
```

### 2.2 สถาปัตยกรรมระบบ

```
┌────────────────────────────────────────────────────────────────┐
│              FUTURES/PERPS TRADING ENGINE                        │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │  Market Data      │  │  Funding Rate    │  │  Basis       │  │
│  │  Aggregator       │  │  Monitor         │  │  Calculator  │  │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬───────┘  │
│           │                     │                    │           │
│  ┌────────▼─────────────────────▼────────────────────▼───────┐  │
│  │              STRATEGY ENGINE                                │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐            │  │
│  │  │ Basis      │ │ Funding    │ │ Directional│            │  │
│  │  │ Trading    │ │ Rate Arb   │ │ Futures    │            │  │
│  │  └────────────┘ └────────────┘ └────────────┘            │  │
│  └───────────────────────┬────────────────────────────────────┘  │
│                          │                                       │
│  ┌───────────────────────▼────────────────────────────────────┐  │
│  │              RISK & MARGIN MANAGEMENT                       │  │
│  │  - Liquidation distance monitoring (every 100ms)            │  │
│  │  - Margin utilization tracking                              │  │
│  │  - Cross-exchange exposure reconciliation                   │  │
│  │  - Leverage enforcement                                     │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## 3. แบบจำลองทางคณิตศาสตร์

### 3.1 การกำหนดราคามูลค่ายุติธรรมของฟิวเจอร์ส

**แบบจำลอง Cost of Carry:**

$$F_0 = S_0 \times e^{(r - y)T}$$

**มูลค่ายุติธรรมเฉพาะคริปโต:**

$$F_0 = S_0 \times e^{(r_{borrow} - y_{staking} + c_{insurance})T}$$

### 3.2 มูลค่ายุติธรรมของสัญญาถาวร

**อัตราโดยนัยจาก Funding:**

$$r_{implied} = \text{Funding Rate} \times \frac{365 \times 24}{\text{Interval (hours)}}$$

### 3.3 คณิตศาสตร์อัตราส่วน Hedge

**อัตราส่วน Hedge แบบ Minimum Variance:**

$$h^* = \frac{\sigma_{SF}}{\sigma_F^2} = \rho \frac{\sigma_S}{\sigma_F}$$

**จำนวนสัญญาที่เหมาะสม:**

$$N^* = h^* \times \frac{Q_S}{Q_F}$$

### 3.4 คณิตศาสตร์ Liquidation

**Isolated Margin — สถานะ Long:**

$$P_{liq} = P_{entry} \times \frac{L - 1}{L \times (1 - MMR)}$$

**Isolated Margin — สถานะ Short:**

$$P_{liq} = P_{entry} \times \frac{L + 1}{L \times (1 + MMR)}$$

### 3.5 แบบจำลองพยากรณ์ Funding Rate

**แบบจำลอง Mean Reversion:**

$$FR_t = \mu + \phi(FR_{t-1} - \mu) + \epsilon_t$$

โดยที่:
- $\mu$ = Funding Rate เฉลี่ยระยะยาว
- $\phi$ = ความเร็ว Mean Reversion (|$\phi$| < 1)
- Half-life ของ Mean Reversion: $\tau = -\ln(2)/\ln(\phi)$

### 3.6 แบบจำลอง Basis Spread

**Basis Z-Score (สำหรับการเทรดแบบ Mean-Reversion):**

$$z_{basis} = \frac{B_{current} - \mu_B}{\sigma_B}$$

**สัญญาณการเทรด:**
- $z > 2$: Basis แพง → ขายฟิวเจอร์ส ซื้อ Spot (Cash-and-Carry)
- $z < -2$: Basis ถูก → ซื้อฟิวเจอร์ส ขาย/Short Spot (Reverse Carry)

### 3.7 การคำนวณเลเวอเรจที่เหมาะสม

**Kelly Criterion สำหรับ Leveraged Futures:**

$$f^* = \frac{\mu - r_f}{\sigma^2}$$

---

## 4. พารามิเตอร์ความเสี่ยง

### 4.1 ขีดจำกัดความเสี่ยงฟิวเจอร์ส/Perps

```
RISK_LIMITS:

  leverage_limits:
    max_effective_leverage: 5x (portfolio level)
    max_single_position_leverage: 10x
    max_basis_trade_leverage: 3x (on each leg)
    target_liquidation_distance: >30%

  position_limits:
    max_single_position_pct: 20% of portfolio (notional)
    max_futures_notional: 300% of portfolio (gross)
    max_net_exposure: 100% of portfolio (net long or short)
    max_single_exchange_exposure: 50% of portfolio

  loss_limits:
    max_daily_loss: 3% of portfolio
    max_weekly_loss: 7% of portfolio
    max_single_trade_loss: 2% of portfolio
    max_drawdown: 20% from peak

  margin_management:
    max_margin_utilization: 60% (of available)
    margin_warning_threshold: 50%
    margin_critical_threshold: 70%
    auto_deleverage_trigger: 75%
    collateral_buffer: 40% above maintenance
```

---

## 5. ขั้นตอนการดำเนินการ

### 5.1 ขั้นตอนการเลือกกลยุทธ์ฟิวเจอร์ส/Perps

```
STRATEGY_SELECTION:

  ╔══════════════════════════════════════════════════════════╗
  ║  DECISION TREE:                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  IF annualized_basis > 15% AND basis_zscore > 1.5:       ║
  ║    → CASH_AND_CARRY (basis is rich, harvest carry)       ║
  ║                                                          ║
  ║  IF annualized_basis < -10% AND basis_zscore < -1.5:     ║
  ║    → REVERSE_CARRY (basis is cheap, expect normalization)║
  ║                                                          ║
  ║  IF avg_funding_7d > 0.03% AND positive_rate_pct > 80%: ║
  ║    → FUNDING_RATE_HARVEST (collect delta-neutral income)  ║
  ║                                                          ║
  ║  IF |funding_exchange_A - funding_exchange_B| > 0.05%:   ║
  ║    → CROSS_EXCHANGE_FUNDING_ARB                          ║
  ║                                                          ║
  ║  IF directional_signal_strong AND confidence > 0.8:      ║
  ║    → DIRECTIONAL_FUTURES (with controlled leverage)      ║
  ║                                                          ║
  ║  IF liquidation_cascade_detected:                        ║
  ║    → DEFENSIVE (reduce exposure, widen stops)            ║
  ╚══════════════════════════════════════════════════════════╝
```

### 5.5 ขั้นตอนฉุกเฉิน

```
EMERGENCY_PROTOCOLS:

  MARGIN_CALL_RESPONSE:
    trigger: margin_utilization > 70%
    priority: CRITICAL
    actions:
      1. IMMEDIATELY assess which positions are most at risk
      2. Transfer available funds from other sub-accounts
      3. If transfer not possible: reduce highest-leverage position by 50%
      4. If still critical: close all positions except fully hedged
    time_limit: 60 seconds total response time

  LIQUIDATION_CASCADE_DETECTED:
    trigger: liquidation_volume > 3x 30d_average in 1h
    actions:
      1. HALT all new position opening
      2. Do NOT place stop-losses in cascade zone
      3. Verify all existing positions have safe margin
      4. After cascade stabilizes (15-30 min): reassess
```

---

## 6. เอกสารอ้างอิง

### วรรณกรรมวิชาการ

1. **Black, F.** (1976). "The Pricing of Commodity Contracts." *Journal of Financial Economics*, 3(1-2), 167-179.
2. **Cox, J.C., Ingersoll, J.E., & Ross, S.A.** (1981). "The Relation between Forward Prices and Futures Prices." *Journal of Financial Economics*, 9(4), 321-346.
3. **Engle, R.** (2002). "Dynamic Conditional Correlation." *Journal of Business & Economic Statistics*, 20(3), 339-350.

### ตำราเรียน

4. **Hull, J.C.** (2022). *Options, Futures, and Other Derivatives* (11th Edition). Pearson.
5. **McDonald, R.L.** (2013). *Derivatives Markets* (3rd Edition). Pearson.

### แหล่งข้อมูลเฉพาะคริปโต

6. **BitMEX Research** — กลไกสัญญาถาวรและการวิเคราะห์ Funding Rate
7. **Deribit Documentation** — ข้อกำหนดฟิวเจอร์ส สัญญาถาวร และ Index
8. **CoinGlass** — ข้อมูล Liquidation, Funding Rates, Open Interest
9. **Laevitas** — การเฝ้าติดตาม Basis และ Term Structure

---

> **หมายเหตุสำหรับ AI Agents:** เอกสารนี้ครอบคลุมกลไกฟิวเจอร์สและสัญญาถาวรอย่างครบถ้วน
> ลำดับความสำคัญการดำเนินงานหลัก:
> 1. ระยะห่างจาก Liquidation ต้องเฝ้าดูตลอดเวลา (ทุก 100ms)
> 2. กลยุทธ์ Funding Rate ต้องอยู่รอดผ่านช่วงลบ
> 3. Basis Trade "ปลอดภัย" ก็ต่อเมื่อมาร์จิ้นเพียงพอที่จะถือจนหมดอายุ
> 4. กลยุทธ์ข้ามตลาดต้องจัดการความเสี่ยงคู่สัญญา
> 5. เลเวอเรจควรอนุรักษ์นิยม (พอร์ตที่แท้จริง < 5x)
> 6. ขั้นตอนฉุกเฉินต้องดำเนินการภายใน 60 วินาที
