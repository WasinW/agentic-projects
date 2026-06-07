# อนุพันธ์และผลิตภัณฑ์ที่มีโครงสร้าง: ภาพรวม

> **แกนที่ 2 — ผลิตภัณฑ์ทางการเงิน | โมดูล 03: อนุพันธ์และผลิตภัณฑ์ที่มีโครงสร้าง (Derivatives & Structured Products)**
> **เอกสาร 00 — ภาพรวมของอนุพันธ์ในการเทรด**
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

### 1.1 อนุพันธ์คืออะไร?

อนุพันธ์ (Derivative) คือสัญญาทางการเงินที่มูลค่าถูกอนุพันธ์มาจากผลการดำเนินงานของสินทรัพย์อ้างอิง ดัชนี หรืออัตราดอกเบี้ย ในบริบทของการเทรด Forex และคริปโตเคอร์เรนซี อนุพันธ์ทำหน้าที่เป็นเครื่องมือสำคัญสำหรับการป้องกันความเสี่ยง (Hedging) การเก็งกำไร (Speculation) การเพิ่มผลตอบแทน (Yield Enhancement) และการเพิ่มประสิทธิภาพพอร์ตการลงทุน

ตลาดอนุพันธ์ทั่วโลกมีมูลค่าตามสัญญาเกิน 600 ล้านล้านดอลลาร์ (BIS, 2025) โดยอนุพันธ์คริปโตคิดเป็นสัดส่วนมากกว่า 70% ของปริมาณการเทรดคริปโตทั้งหมดในตลาดหลักๆ

### 1.2 ประเภทของอนุพันธ์

#### 1.2.1 สัญญาฟิวเจอร์ส (Futures Contracts)

สัญญาฟิวเจอร์สคือข้อตกลงมาตรฐานในการซื้อหรือขายสินทรัพย์ในราคาที่กำหนดไว้ล่วงหน้า ณ เวลาที่ระบุในอนาคต

**คุณสมบัติหลัก:**
- **มาตรฐาน (Standardized)**: ขนาดสัญญา วันหมดอายุ และขั้นตอนการชำระบัญชีกำหนดโดยตลาด
- **ใช้มาร์จิ้น (Margined)**: ต้องวางมาร์จิ้นเริ่มต้นและมาร์จิ้นรักษาสภาพ; มีการปรับมูลค่าตามราคาตลาดรายวัน (Mark-to-Market)
- **การชำระบัญชี (Settlement)**: ส่งมอบจริงหรือชำระเป็นเงินสด
- **วันหมดอายุ (Expiration)**: มีวันหมดอายุแน่นอน (รายไตรมาสสำหรับคริปโต: มีนาคม มิถุนายน กันยายน ธันวาคม ในตลาดหลัก)
- **ความเสี่ยงคู่สัญญา (Counterparty Risk)**: ลดความเสี่ยงผ่านสำนักหักบัญชี (แบบดั้งเดิม) หรือกองทุนประกัน (คริปโต)

**ฟิวเจอร์ส Forex:**
- ซื้อขายบน CME, ICE และตลาดที่มีการกำกับดูแลอื่นๆ
- ขนาดสัญญาเป็นมาตรฐาน (เช่น EUR/USD = 125,000 EUR ต่อสัญญา)
- ใช้อย่างกว้างขวางโดยบริษัทเพื่อป้องกันความเสี่ยง FX

**ฟิวเจอร์สคริปโต:**
- มีให้บริการบน Binance, Deribit, CME, OKX, Bybit
- ขนาดสัญญาแตกต่างกัน (เช่น 1 BTC, 0.001 BTC สำหรับสัญญาขนาดเล็ก)
- มีทั้งแบบวางมาร์จิ้นด้วยเหรียญ (Coin-margined) และแบบ USDT/USDC-margined
- สัญญาผกผัน (Inverse contracts): มาร์จิ้นและชำระบัญชีเป็นคริปโตอ้างอิง
- สัญญาเชิงเส้น (Linear contracts): มาร์จิ้นและชำระบัญชีเป็น Stablecoin (USDT/USDC)

#### 1.2.2 สัญญาออปชัน (Options Contracts)

สัญญาออปชันให้สิทธิ์แก่ผู้ถือ แต่ไม่มีภาระผูกพัน ในการซื้อ (Call) หรือขาย (Put) สินทรัพย์อ้างอิงที่ราคาใช้สิทธิ์ (Strike Price) ที่กำหนด ก่อนหรือ ณ วันหมดอายุ

**คุณสมบัติหลัก:**
- **ค่าพรีเมียม (Premium)**: ผู้ซื้อจ่ายพรีเมียม; ผู้ขายได้รับพรีเมียม
- **ผลตอบแทนไม่สมมาตร (Asymmetric Payoff)**: ขาดทุนจำกัดสำหรับผู้ซื้อ กำไรจำกัดสำหรับผู้ขาย
- **Greeks**: การวัดความไวต่อปัจจัยต่างๆ (Delta, Gamma, Theta, Vega, Rho)
- **ความผันผวนโดยนัย (Implied Volatility)**: ความคาดหวังของตลาดต่อความผันผวนในอนาคตที่ฝังอยู่ในราคาออปชัน

**ออปชัน Forex:**
- ตลาด OTC เป็นหลัก (ระหว่างธนาคาร)
- มาตรฐานบนตลาด (CME, PHLX)
- มักเสนอราคาในรูป Delta (25-delta risk reversal เป็นต้น)
- ออปชันแบบ Barrier ใช้กันอย่างแพร่หลายใน FX (Knock-in, Knock-out)

**ออปชันคริปโต:**
- Deribit ครองตลาด (>85% ส่วนแบ่งตลาดสำหรับ BTC/ETH options)
- แบบ European (ใช้สิทธิ์ได้เฉพาะวันหมดอายุ)
- ชำระบัญชีเป็นเงินสดในคริปโตอ้างอิง
- โปรโตคอล DeFi options กำลังเติบโต (Lyra, Hegic, Dopex, Ribbon Finance)
- IV สูงกว่าตลาดดั้งเดิมอย่างมาก (BTC: 50-120% ต่อปี เทียบกับ S&P 500: 15-30%)

#### 1.2.3 สัญญาถาวร (Perpetual Swaps / Perpetual Futures)

สัญญาถาวรเป็นเอกลักษณ์ของตลาดคริปโตเคอร์เรนซี — เป็นสัญญาฟิวเจอร์สที่ไม่มีวันหมดอายุ รักษาสมดุลผ่านกลไกอัตราการจ่ายเงิน (Funding Rate)

**คุณสมบัติหลัก:**
- **ไม่มีวันหมดอายุ (No Expiry)**: เทรดต่อเนื่องโดยไม่ต้องโรลโอเวอร์
- **Funding Rate**: การจ่ายเงินเป็นระยะระหว่าง Long และ Short เพื่อยึดราคาให้ใกล้เคียงราคา Spot
- **เลเวอเรจ (Leverage)**: โดยทั่วไปมี 1x-125x ให้เลือก
- **Mark Price**: ใช้สำหรับคำนวณการล้างสถานะ (Liquidation) คำนวณจาก Index Price
- **เครื่องมือหลัก (Dominant Instrument)**: >60% ของปริมาณการเทรดอนุพันธ์คริปโตทั้งหมด

**กลไก Funding Rate:**
- Funding Rate เป็นบวก: ฝ่าย Long จ่ายให้ฝ่าย Short (ตลาดเป็นขาขึ้น/มีพรีเมียม)
- Funding Rate เป็นลบ: ฝ่าย Short จ่ายให้ฝ่าย Long (ตลาดเป็นขาลง/มีส่วนลด)
- โดยทั่วไปชำระทุก 8 ชั่วโมง (Binance, OKX) หรือแบบต่อเนื่อง (dYdX)
- Funding Rate เมื่อคำนวณเป็นรายปีอาจอยู่ในช่วง -100% ถึง +200% ในสถานการณ์รุนแรง

#### 1.2.4 ผลิตภัณฑ์ที่มีโครงสร้าง (Structured Products)

ผลิตภัณฑ์ที่มีโครงสร้างรวมเครื่องมืออนุพันธ์หลายตัวเข้าด้วยกันเพื่อสร้างโปรไฟล์ความเสี่ยง-ผลตอบแทนที่ปรับแต่งได้

**ผลิตภัณฑ์ที่มีโครงสร้างแบบดั้งเดิม:**
- ตั๋วเงินคุ้มครองเงินต้น (Principal Protected Notes - PPN)
- ผลิตภัณฑ์ที่เงินต้นมีความเสี่ยง (Capital-at-risk products)
- ตั๋วเงินแบบ Autocallable
- ตั๋วเงินแบบ Range Accrual

**ผลิตภัณฑ์ที่มีโครงสร้างในคริปโต:**
- DeFi Options Vaults (DOV): Ribbon Finance, Friktion, Katana
- ผลิตภัณฑ์ Dual Investment: Binance, OKX, Bybit
- ผลิตภัณฑ์ Shark Fin: Binance Earn, OKX Earn
- ผลิตภัณฑ์ Snowball: Matrixport, Babel Finance
- โครงสร้าง Accumulator/Decumulator

### 1.3 บทบาทของอนุพันธ์ในการจัดการพอร์ตการลงทุน

#### 1.3.1 การป้องกันความเสี่ยง (Hedging)

อนุพันธ์เป็นเครื่องมือหลักสำหรับการบริหารความเสี่ยงของพอร์ต:

| เป้าหมายการป้องกันความเสี่ยง | เครื่องมือ | กลยุทธ์ |
|---|---|---|
| ป้องกันขาลง | ออปชัน Put | Protective Put |
| ล็อคราคาขาย | Short Futures | Forward Hedge |
| ลดต้นทุนการ Hedge | Collar (Put + Covered Call) | Zero-cost Collar |
| ป้องกันความเสี่ยงหาง (Tail Risk) | ออปชัน Put ที่ OTM | Tail Hedge |
| ทำ Delta เป็นกลาง | สัญญาถาวร | Delta Hedge |
| ป้องกันความผันผวน | Variance Swaps | Vega Hedge |

#### 1.3.2 การเก็งกำไร (Speculation)

อนุพันธ์ให้ Exposure แบบมีเลเวอเรจทั้งมุมมองตามทิศทางและไม่ตามทิศทาง:

- **ตามทิศทาง (Directional)**: Long/Short Futures, ซื้อ Call/Put
- **ความผันผวน (Volatility)**: Straddles, Strangles, Calendar Spreads
- **Carry**: Funding Rate Arbitrage, Basis Trading
- **มูลค่าสัมพัทธ์ (Relative Value)**: Spread Trades ระหว่างสินทรัพย์ที่มีความสัมพันธ์กัน

#### 1.3.3 การเพิ่มผลตอบแทน (Yield Enhancement)

กลยุทธ์การเก็บพรีเมียมอย่างเป็นระบบ:

- **Covered Call Writing**: ขาย Call บนสถานะ Long ที่มีอยู่
- **Cash-Secured Put Selling**: ขาย Put โดยมีเงินสดเป็นหลักประกัน
- **การเข้าร่วม DOV**: กลยุทธ์ Vault อัตโนมัติสำหรับรายได้จากพรีเมียม
- **Funding Rate Harvesting**: เก็บ Funding Rate บวกจากสถานะที่ทำ Delta-hedge แล้ว

#### 1.3.4 ประสิทธิภาพของเงินทุน (Capital Efficiency)

- ฟิวเจอร์สและสวอปให้ Exposure สังเคราะห์โดยไม่ต้องใช้เงินทุนเต็มจำนวน
- ออปชันช่วยให้สร้างสถานะที่กำหนดความเสี่ยงได้ โดยรู้ขาดทุนสูงสุดล่วงหน้า
- ระบบ Cross-margin ช่วยเพิ่มประสิทธิภาพมาร์จิ้นในระดับพอร์ต

### 1.4 ภาพรวม Greeks

Greeks วัดความไวของราคาอนุพันธ์ต่อปัจจัยต่างๆ:

| Greek | สัญลักษณ์ | วัดอะไร | สูตร | ช่วงค่าทั่วไป |
|---|---|---|---|---|
| Delta | Δ | ความไวต่อราคาสินทรัพย์อ้างอิง | ∂V/∂S | -1 ถึง +1 |
| Gamma | Γ | อัตราการเปลี่ยนแปลงของ Delta | ∂²V/∂S² | เป็นบวกเสมอสำหรับ Long Options |
| Theta | Θ | การสลายตัวตามเวลา (Time Decay) | ∂V/∂t | เป็นลบสำหรับ Long Options |
| Vega | ν | ความไวต่อความผันผวน | ∂V/∂σ | เป็นบวกสำหรับ Long Options |
| Rho | ρ | ความไวต่ออัตราดอกเบี้ย | ∂V/∂r | บวกสำหรับ Call, ลบสำหรับ Put |
| Vanna | | ความไวของ Delta ต่อความผันผวน | ∂²V/∂S∂σ | แปรผัน |
| Charm | | ความไวของ Delta ต่อเวลา | ∂²V/∂S∂t | แปรผัน |
| Volga/Vomma | | ความไวของ Vega ต่อความผันผวน | ∂²V/∂σ² | แปรผัน |

**Greeks ระดับพอร์ต:**
- Portfolio delta = Σ (position_i × delta_i)
- Portfolio gamma = Σ (position_i × gamma_i)
- Portfolio theta = Σ (position_i × theta_i)
- Portfolio vega = Σ (position_i × vega_i)

### 1.5 อนุพันธ์ในคริปโต เทียบกับ ตลาดดั้งเดิม

| คุณสมบัติ | แบบดั้งเดิม (Forex) | คริปโต |
|---|---|---|
| **ชั่วโมงเทรด** | 24/5 (อาทิตย์ 5PM - ศุกร์ 5PM ET) | 24/7/365 |
| **การชำระบัญชี** | T+2 สำหรับ Spot, รายวันสำหรับ Futures | เกือบทันทีสำหรับ Spot, เรียลไทม์สำหรับ Perps |
| **กฎระเบียบ** | กำกับดูแลอย่างเข้มงวด (CFTC, SEC, FCA) | แตกต่างตามเขตอำนาจศาล; ส่วนใหญ่ยังไม่มีกฎระเบียบ |
| **ความเสี่ยงคู่สัญญา** | การค้ำประกันจากสำนักหักบัญชี | กองทุนประกันของตลาด / ความเสี่ยง Smart Contract |
| **ความผันผวน** | ต่ำ (EUR/USD: 6-10% ต่อปี) | สูงมาก (BTC: 50-80% ต่อปี) |
| **เลเวอเรจ** | 50:1 รายย่อย (สหรัฐฯ), 500:1 นอกชายฝั่ง | 1x-125x (ขึ้นอยู่กับตลาด) |
| **รูปแบบออปชัน** | ทั้ง American และ European | ส่วนใหญ่เป็น European |
| **สัญญาถาวร** | ไม่มี | เครื่องมือหลัก |
| **Funding Rate** | ไม่มี (ใช้ Swap/Rollover แทน) | กลไกหลัก |
| **ความผันผวนโดยนัย** | ต่ำ, กลับสู่ค่าเฉลี่ย | สูง, มีการพุ่งขึ้นรุนแรง |
| **สภาพคล่อง** | ลึก (>$6T ต่อวันใน FX Spot) | เพิ่มขึ้นแต่ยังบาง กระจายตัว |
| **ความเป็นผู้ใหญ่ของตลาด** | มีข้อมูลและงานวิจัยหลายทศวรรษ | ข้อมูล <15 ปี |
| **การรวม DeFi** | ไม่มี | อนุพันธ์แบบ Composable บน on-chain |
| **IV Smile ของออปชัน** | Risk Reversal Skew เป็นหลัก | Put Skew แข็งแรง + IV โดยรวมสูง |
| **การล้างสถานะ (Liquidation)** | Margin Call → มีเวลาเติมเงิน | อัตโนมัติ ล้างทันที |

### 1.6 ความแตกต่างสำคัญที่ส่งผลต่ออัลกอริทึมการเทรด

**สำหรับระบบเทรด AI ปัจจัยเฉพาะของคริปโตต่อไปนี้ต้องได้รับการจัดการเป็นพิเศษ:**

1. **ตลาด 24/7**: ไม่มีตลาดปิด ไม่มี Gap ข้ามคืน (แต่สภาพคล่องอาจบางลงในวันหยุดสุดสัปดาห์)
2. **Funding Rate Alpha**: เฉพาะคริปโต; ต้องนำมาพิจารณาในกลยุทธ์ Carry
3. **ความผันผวนพื้นฐานสูง**: ต้องตั้ง Stop-loss กว้างขึ้น ปรับขนาดสถานะ
4. **Liquidation Cascades**: อาจทำให้เกิด Flash Crash; ต้องเฝ้าดูระดับ Liquidation
5. **ตลาดกระจายตัว (Exchange Fragmentation)**: ราคาแตกต่างกันระหว่างตลาดสร้างโอกาส Arb
6. **ความเสี่ยง Smart Contract**: อนุพันธ์ DeFi มีความเสี่ยงโค้ดเพิ่มเติมนอกเหนือจากความเสี่ยงตลาด
7. **ความไม่แน่นอนด้านกฎระเบียบ**: วงเงินสถานะและเครื่องมือที่ใช้ได้อาจเปลี่ยนแปลงอย่างรวดเร็ว
8. **การเปลี่ยนแปลงสหสัมพันธ์ (Correlation Regime Changes)**: สหสัมพันธ์ระหว่างคริปโตกับตลาดดั้งเดิมเปลี่ยนแปลงอย่างมากในช่วงวิกฤต

---

## 2. ข้อกำหนดทางเทคนิค

### 2.1 ข้อกำหนดข้อมูลสำหรับการเทรดอนุพันธ์

```
DERIVATIVE_DATA_SOURCES:
  market_data:
    - spot_price: Real-time underlying price (multiple sources for TWAP/VWAP)
    - order_book: L2/L3 book depth for options and futures
    - trades: Tick-level trade data
    - funding_rate: Current and historical funding rates (8h intervals)
    - open_interest: By strike, expiry, and direction
    - implied_volatility: IV surface (by strike × expiry)
    - realized_volatility: Historical volatility (various windows)

  reference_data:
    - contract_specs: Tick size, lot size, margin requirements
    - expiry_calendar: All active expiration dates
    - strike_grid: Available strikes per expiry
    - settlement_rules: Cash vs physical, settlement time
    - fee_schedule: Maker/taker fees per instrument type

  risk_data:
    - mark_price: Exchange-calculated fair price
    - index_price: Composite spot index
    - liquidation_map: Estimated liquidation levels by price
    - insurance_fund: Exchange insurance fund balance
    - maximum_leverage: Per-instrument leverage limits
```

### 2.2 สถาปัตยกรรมระบบสำหรับการเทรดอนุพันธ์

```
┌─────────────────────────────────────────────────────────────┐
│                    DERIVATIVE TRADING ENGINE                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │  Market Data │  │  Volatility  │  │  Greeks Engine     │  │
│  │  Aggregator  │──│  Surface     │──│  (Real-time calc)  │  │
│  │             │  │  Builder     │  │                    │  │
│  └──────┬──────┘  └──────┬───────┘  └─────────┬──────────┘  │
│         │                │                     │              │
│  ┌──────▼────────────────▼─────────────────────▼──────────┐  │
│  │              STRATEGY EVALUATION ENGINE                  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │  │
│  │  │ Options  │ │ Futures  │ │ Perp     │ │Structured│  │  │
│  │  │Strategies│ │Strategies│ │Strategies│ │ Products │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │  │
│  └───────────────────────┬─────────────────────────────────┘  │
│                          │                                    │
│  ┌───────────────────────▼─────────────────────────────────┐  │
│  │              RISK MANAGEMENT LAYER                       │  │
│  │  - Position sizing (Kelly/Fractional)                    │  │
│  │  - Portfolio Greeks management                           │  │
│  │  - VaR / CVaR monitoring                                │  │
│  │  - Liquidation distance monitoring                      │  │
│  │  - Correlation risk tracking                            │  │
│  └───────────────────────┬─────────────────────────────────┘  │
│                          │                                    │
│  ┌───────────────────────▼─────────────────────────────────┐  │
│  │              ORDER EXECUTION ENGINE                      │  │
│  │  - Smart order routing                                  │  │
│  │  - Multi-leg execution                                  │  │
│  │  - Slippage management                                  │  │
│  │  - Exchange API integration                             │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 ตลาดและเครื่องมือที่รองรับ

```
EXCHANGE_CONFIGURATION:
  deribit:
    instruments: [options, futures]
    assets: [BTC, ETH]
    options_style: European
    settlement: crypto
    api_rate_limit: 20 req/s
    websocket: wss://www.deribit.com/ws/api/v2

  binance:
    instruments: [futures, perpetual_swaps]
    assets: [BTC, ETH, +200 altcoins]
    margin_types: [USDT, BUSD, coin-margined]
    max_leverage: 125x
    api_rate_limit: 1200 req/min

  okx:
    instruments: [options, futures, perpetual_swaps, structured_products]
    assets: [BTC, ETH, SOL, +100 altcoins]
    margin_modes: [cross, isolated, portfolio]
    api_rate_limit: 60 req/2s

  cme:
    instruments: [futures, options]
    assets: [BTC, ETH, major FX pairs]
    settlement: cash (crypto), physical (FX)
    regulated: true
    margin_type: portfolio margin (SPAN)

  bybit:
    instruments: [perpetual_swaps, futures, options]
    assets: [BTC, ETH, +200 altcoins]
    margin_types: [USDT, USDC, inverse]
    max_leverage: 100x

  forex_exchanges:
    instruments: [spot, forwards, options, swaps]
    platforms: [EBS, Reuters Matching, Currenex, Hotspot]
    settlement: T+2
```

### 2.4 ข้อกำหนดด้านประสิทธิภาพ

```
PERFORMANCE_SPECS:
  latency:
    market_data_processing: <5ms
    greeks_calculation: <10ms per position
    portfolio_greeks: <50ms for full portfolio
    vol_surface_rebuild: <200ms
    risk_check: <20ms
    order_submission: <50ms

  throughput:
    market_data_updates: 10,000+ events/second
    greeks_recalculation: Every 100ms for active positions
    risk_monitoring: Continuous, real-time
    position_reconciliation: Every 1 second

  availability:
    uptime_target: 99.99%
    failover_time: <5 seconds
    data_backup: Real-time replication
```

---

## 3. แบบจำลองทางคณิตศาสตร์

### 3.1 พื้นฐานการกำหนดราคาอนุพันธ์

ทฤษฎีบทพื้นฐานของการกำหนดราคาสินทรัพย์ระบุว่า ในตลาดที่ไม่มีโอกาสอาร์บิทราจ จะมีมาตรวัดความน่าจะเป็นแบบ Risk-neutral $\mathbb{Q}$ ซึ่งราคาของอนุพันธ์ใดๆ คือค่าคาดหวังที่หักลดแล้ว:

$$V_0 = e^{-rT} \mathbb{E}^{\mathbb{Q}}[\text{Payoff}(S_T)]$$

### 3.2 กรอบการทำงาน Black-Scholes-Merton

ภายใต้สมมติฐาน Black-Scholes (การเคลื่อนที่แบบ Geometric Brownian Motion, ความผันผวนคงที่, การเทรดแบบต่อเนื่อง) สินทรัพย์อ้างอิงมีพฤติกรรม:

$$dS = \mu S \, dt + \sigma S \, dW$$

ภายใต้มาตรวัด Risk-neutral:

$$dS = rS \, dt + \sigma S \, dW^{\mathbb{Q}}$$

**ราคา European Call Option:**

$$C = S_0 N(d_1) - Ke^{-rT}N(d_2)$$

**ราคา European Put Option:**

$$P = Ke^{-rT}N(-d_2) - S_0 N(-d_1)$$

โดยที่:

$$d_1 = \frac{\ln(S_0/K) + (r + \sigma^2/2)T}{\sigma\sqrt{T}}$$

$$d_2 = d_1 - \sigma\sqrt{T}$$

### 3.3 การกำหนดราคาฟิวเจอร์ส

**แบบจำลอง Cost of Carry:**

$$F_0 = S_0 \times e^{(r - q)T}$$

โดยที่:
- $F_0$ = ราคาฟิวเจอร์ส
- $S_0$ = ราคา Spot
- $r$ = อัตราดอกเบี้ยปลอดความเสี่ยง
- $q$ = Convenience Yield (หรือ Staking Yield ในคริปโต)
- $T$ = เวลาจนหมดอายุ

**มูลค่ายุติธรรมของคริปโตฟิวเจอร์ส (รวม Staking Yield):**

$$F_0 = S_0 \times e^{(r_{borrow} - y_{staking})T}$$

### 3.4 การกำหนดราคาสัญญาถาวร (Perpetual Swap)

ราคาสัญญาถาวร $P_{perp}$ ถูกยึดกับราคา Spot ผ่าน Funding Rate:

$$\text{Funding Rate} = \text{Premium Index} + \text{clamp}(\text{Interest Rate} - \text{Premium Index}, -0.05\%, 0.05\%)$$

$$\text{Premium Index} = \frac{\text{Max}(0, \text{Impact Bid} - P_{index}) - \text{Max}(0, P_{index} - \text{Impact Ask})}{P_{index}}$$

**การจ่ายเงิน Funding:**

$$\text{Payment} = \text{Position Value} \times \text{Funding Rate}$$

### 3.5 สูตร Greeks

$$\Delta_{call} = N(d_1), \quad \Delta_{put} = N(d_1) - 1$$

$$\Gamma = \frac{N'(d_1)}{S_0 \sigma \sqrt{T}}$$

$$\Theta_{call} = -\frac{S_0 N'(d_1) \sigma}{2\sqrt{T}} - rKe^{-rT}N(d_2)$$

$$\nu = S_0 \sqrt{T} N'(d_1)$$

$$\rho_{call} = KTe^{-rT}N(d_2)$$

โดยที่ $N'(x) = \frac{1}{\sqrt{2\pi}}e^{-x^2/2}$ คือ PDF ของ Standard Normal

### 3.6 การสกัดค่าความผันผวนโดยนัย (Implied Volatility)

ความผันผวนโดยนัย $\sigma_{imp}$ หาได้จากการแก้สมการเชิงตัวเลข:

$$C_{market} = BSM(S_0, K, T, r, \sigma_{imp})$$

วิธีเชิงตัวเลขที่ใช้ทั่วไป:
- **Newton-Raphson**: $\sigma_{n+1} = \sigma_n - \frac{C_{BSM}(\sigma_n) - C_{market}}{\text{Vega}(\sigma_n)}$
- **Brent's Method**: การหาค่ารากแบบ Bracketed (แข็งแกร่งกว่า)
- **Rational Approximation**: Let It Be (Jaeckel, 2017) สำหรับการคำนวณแบบเกือบทันที

---

## 4. พารามิเตอร์ความเสี่ยง

### 4.1 ขีดจำกัดความเสี่ยงระดับพอร์ต

```
RISK_PARAMETERS:
  position_limits:
    max_single_position_pct: 10%       # ของพอร์ต
    max_derivatives_exposure: 200%      # มูลค่าตามสัญญาเป็น % ของ NAV
    max_options_premium_at_risk: 5%     # ของพอร์ตต่อการเทรด
    max_futures_leverage: 5x            # เลเวอเรจพอร์ตที่แท้จริง
    max_perp_leverage: 3x              # อนุรักษ์นิยมสำหรับบอท
    max_concentrated_strike: 20%        # ของ OI ที่ Strike เดียว

  greeks_limits:
    max_portfolio_delta: 0.3            # เป็นสัดส่วนของพอร์ต
    max_portfolio_gamma: 0.05           # ต่อการเคลื่อนไหว 1%
    max_portfolio_vega: 2%              # ของพอร์ตต่อ 1 vol point
    max_portfolio_theta: -0.5%          # Time Decay รายวันเป็น % ของพอร์ต
    max_single_name_delta: 0.15         # ต่อสินทรัพย์อ้างอิง

  loss_limits:
    max_daily_loss: 3%                  # ของพอร์ต
    max_weekly_loss: 7%                 # ของพอร์ต
    max_monthly_loss: 15%               # ของพอร์ต
    max_drawdown_hard_stop: 25%         # จากจุดสูงสุด
    max_single_trade_loss: 2%           # ของพอร์ต

  volatility_limits:
    min_iv_rank_for_selling: 30         # เปอร์เซ็นไทล์
    max_iv_rank_for_buying: 70          # เปอร์เซ็นไทล์
    max_vega_exposure_event: 50%        # ลดก่อนเหตุการณ์สำคัญ
    min_days_to_expiry_sell: 7          # ไม่ขายออปชันที่ใกล้หมดอายุมาก

  liquidation_safety:
    min_margin_ratio: 50%               # รักษา 50%+ ของ Initial Margin
    liquidation_distance_min: 30%       # ราคาต้องเคลื่อนไหว 30%+ จึงจะถูกล้าง
    auto_deleverage_threshold: 40%      # ลดสถานะเมื่อใช้มาร์จิ้น 40%
```

### 4.2 เมตริกแดชบอร์ดเฝ้าติดตามความเสี่ยง

```
MONITORING_METRICS:
  real_time:
    - portfolio_delta_dollars
    - portfolio_gamma_dollars_per_1pct
    - portfolio_theta_daily
    - portfolio_vega_per_vol_point
    - margin_utilization_pct
    - liquidation_distance_pct
    - unrealized_pnl
    - funding_rate_exposure
    - max_loss_scenario (3σ move)

  periodic (every 1 hour):
    - VaR_95_1day
    - CVaR_95_1day
    - correlation_matrix_update
    - volatility_surface_fit_quality
    - basis_vs_fair_value

  daily:
    - realized_pnl_attribution (delta, gamma, theta, vega, rho)
    - sharpe_ratio_rolling_30d
    - max_drawdown_current
    - win_rate_by_strategy
    - avg_holding_period
```

### 4.3 การวิเคราะห์สถานการณ์

```
STRESS_SCENARIOS:
  crypto_crash:
    btc_move: -30%
    eth_move: -40%
    altcoin_move: -50%
    iv_change: +50 vol points
    funding_rate: -0.1% per 8h
    correlation: 0.95 (all crypto)

  crypto_rally:
    btc_move: +30%
    eth_move: +40%
    altcoin_move: +60%
    iv_change: -10 vol points
    funding_rate: +0.2% per 8h

  vol_explosion:
    spot_move: ±5%
    iv_change: +80 vol points
    term_structure: inverted
    skew_change: +15 points put skew

  liquidity_crisis:
    bid_ask_spread: 5x normal
    order_book_depth: -80%
    exchange_outage_probability: 20%
    liquidation_cascade: active

  fx_black_swan:
    eur_usd_move: ±5% (single day)
    usd_jpy_move: ±8% (single day)
    vol_spike: +200% from baseline
    correlation_break: historical correlations fail
```

---

## 5. ขั้นตอนการดำเนินการ

### 5.1 ขั้นตอนการเลือกกลยุทธ์อนุพันธ์หลัก

```
DERIVATIVE_STRATEGY_SELECTION:

  Step 1: MARKET REGIME IDENTIFICATION
    ├── Collect: spot price, IV surface, funding rates, OI, volume
    ├── Classify regime:
    │   ├── TRENDING_UP: Strong directional bullish momentum
    │   ├── TRENDING_DOWN: Strong directional bearish momentum
    │   ├── RANGE_BOUND: Low volatility, mean-reverting
    │   ├── HIGH_VOLATILITY: Elevated IV, potential breakout
    │   ├── LOW_VOLATILITY: Compressed IV, breakout imminent
    │   └── CRISIS: Extreme moves, liquidation cascades
    └── Output: regime_label, confidence_score

  Step 2: OPPORTUNITY SCREENING
    ├── Scan IV Rank/Percentile across all underlyings
    ├── Identify funding rate anomalies
    ├── Check basis (futures premium/discount)
    ├── Monitor term structure shape (contango/backwardation)
    ├── Evaluate put-call skew
    └── Score each opportunity: [0.0 - 1.0]

  Step 3: STRATEGY MAPPING
    ├── IF regime == TRENDING_UP AND iv_rank < 30:
    │   → Long Call, Bull Call Spread, Short Cash-Secured Put
    ├── IF regime == TRENDING_DOWN AND iv_rank < 30:
    │   → Long Put, Bear Put Spread, Protective Put
    ├── IF regime == RANGE_BOUND AND iv_rank > 50:
    │   → Iron Condor, Short Strangle, Short Straddle
    ├── IF regime == HIGH_VOLATILITY AND iv_rank > 70:
    │   → Sell premium: Iron Condor, Covered Call, DOV
    ├── IF regime == LOW_VOLATILITY AND iv_rank < 20:
    │   → Buy premium: Long Straddle, Long Strangle, Calendar
    ├── IF funding_rate_anomaly:
    │   → Basis trade, Funding rate arbitrage
    └── IF crisis:
        → Hedge existing, tail hedges, reduce exposure

  Step 4: POSITION SIZING
    ├── Calculate Kelly fraction for selected strategy
    ├── Apply fractional Kelly (typically 0.25-0.5x full Kelly)
    ├── Check against all risk limits
    ├── Verify margin requirements
    └── Output: position_size, number_of_contracts

  Step 5: EXECUTION
    ├── Check liquidity at target strikes/expiries
    ├── Use limit orders with smart routing
    ├── For multi-leg strategies: simultaneous execution preferred
    ├── Monitor fill quality and adjust
    └── Confirm all legs filled, log trade

  Step 6: MONITORING & MANAGEMENT
    ├── Continuous Greeks monitoring
    ├── Profit target check (typically 50% of max profit for credit spreads)
    ├── Stop loss check (typically 200% of credit received)
    ├── Time-based exit (close at 21 DTE if opened at 45 DTE)
    ├── Adjustment triggers:
    │   ├── Delta breach: Roll or add hedge
    │   ├── Gamma risk: Reduce near expiry
    │   ├── Vega risk: Adjust if IV regime changes
    │   └── Theta: Harvest or exit
    └── Log all adjustments with reasoning
```

### 5.2 การจัดการวงจรชีวิตอนุพันธ์

```
LIFECYCLE_FLOW:

  INITIATION:
    1. Strategy signal generated
    2. Risk pre-check passed
    3. Order constructed (all legs)
    4. Margin verified
    5. Order submitted

  ACTIVE_MANAGEMENT:
    1. Real-time P&L tracking
    2. Greeks monitoring (every 100ms)
    3. Funding rate collection/payment tracking
    4. Margin monitoring
    5. Event calendar awareness (expiry, settlement, announcements)

  EXIT:
    1. Profit target reached → close all legs
    2. Stop loss triggered → close all legs
    3. Time exit → close before expiry risk
    4. Forced exit → margin call / liquidation proximity
    5. Strategy invalidation → regime change detected

  POST-TRADE:
    1. Record actual vs expected P&L
    2. Analyze slippage and execution quality
    3. Update strategy performance statistics
    4. Feed results to ML model for parameter optimization
    5. Adjust risk parameters if needed
```

### 5.3 ขั้นตอนฉุกเฉิน

```
EMERGENCY_PROTOCOLS:

  LIQUIDATION_PROXIMITY:
    trigger: margin_ratio < 40%
    action:
      1. Alert: CRITICAL
      2. Reduce position by 50% immediately (market orders)
      3. Close most leveraged positions first
      4. Transfer additional collateral if available
      5. Halt new position opening

  EXCHANGE_OUTAGE:
    trigger: API connection lost > 30 seconds
    action:
      1. Switch to backup exchange if available
      2. Queue pending orders for retry
      3. Calculate exposure without real-time data
      4. Prepare hedges on alternative venues
      5. Alert operations team

  FLASH_CRASH:
    trigger: >10% move in <5 minutes
    action:
      1. Halt all new orders
      2. Verify positions and margin
      3. Do NOT panic-sell into cascading liquidations
      4. Wait for price stabilization (5-15 min)
      5. Assess damage, adjust hedges
      6. Resume only after volatility normalizes

  BLACK_SWAN:
    trigger: >20% move in <1 hour
    action:
      1. Full system halt
      2. Manual override required
      3. Close all leveraged positions
      4. Maintain only hedged/covered positions
      5. Do not re-enter for minimum 24 hours
```

---

## 6. เอกสารอ้างอิง

### วรรณกรรมวิชาการ

1. **Black, F., & Scholes, M.** (1973). "The Pricing of Options and Corporate Liabilities." *Journal of Political Economy*, 81(3), 637-654.
2. **Merton, R.C.** (1973). "Theory of Rational Option Pricing." *Bell Journal of Economics and Management Science*, 4(1), 141-183.
3. **Cox, J.C., Ross, S.A., & Rubinstein, M.** (1979). "Option Pricing: A Simplified Approach." *Journal of Financial Economics*, 7(3), 229-263.
4. **Heston, S.L.** (1993). "A Closed-Form Solution for Options with Stochastic Volatility with Applications to Bond and Currency Options." *Review of Financial Studies*, 6(2), 327-343.
5. **Dupire, B.** (1994). "Pricing with a Smile." *Risk*, 7(1), 18-20.

### ตำราเรียน

6. **Hull, J.C.** (2022). *Options, Futures, and Other Derivatives* (11th Edition). Pearson.
7. **Natenberg, S.** (2015). *Option Volatility and Pricing* (2nd Edition). McGraw-Hill.
8. **Taleb, N.N.** (1997). *Dynamic Hedging: Managing Vanilla and Exotic Options*. Wiley.
9. **Sinclair, E.** (2013). *Volatility Trading* (2nd Edition). Wiley.
10. **Haug, E.G.** (2007). *The Complete Guide to Option Pricing Formulas* (2nd Edition). McGraw-Hill.

### แหล่งข้อมูลเฉพาะคริปโต

11. **Deribit Documentation** — ข้อกำหนด Options และ Futures. https://www.deribit.com/kb
12. **Binance Futures Documentation** — กลไกสัญญาถาวร. https://www.binance.com/en/support
13. **Paradigm Protocol** — การเทรดออปชันคริปโตระดับสถาบัน
14. **Amberdata Derivatives** — ข้อมูลวิเคราะห์อนุพันธ์คริปโต
15. **Laevitas Analytics** — การเฝ้าติดตาม Flow ออปชันคริปโตและ Greeks
16. **The Block Research** — รายงานโครงสร้างตลาดอนุพันธ์คริปโต

### เอกสารตลาด

17. **CME Group** — ข้อกำหนดฟิวเจอร์ส/ออปชัน Bitcoin และ Ether
18. **OKX** — เอกสารผลิตภัณฑ์ที่มีโครงสร้างและอนุพันธ์
19. **Bybit** — เอกสารสัญญาถาวรและออปชัน
20. **dYdX** — เอกสารโปรโตคอลสัญญาถาวรแบบกระจายศูนย์

---

> **หมายเหตุสำหรับ AI Agents:** เอกสารนี้เป็นภาพรวมพื้นฐานสำหรับโมดูลอนุพันธ์
> รายละเอียดการใช้งานสำหรับอนุพันธ์แต่ละประเภทอยู่ในเอกสารถัดไป:
> - `01_options_strategies.md` — กลยุทธ์ออปชันแบบครบถ้วน
> - `02_futures_perpetual_swaps.md` — การเทรดฟิวเจอร์สและสัญญาถาวร
> - `03_structured_products.md` — ผลิตภัณฑ์ที่มีโครงสร้างและกลยุทธ์ Exotic
> - `04_volatility_trading.md` — กรอบการเทรดความผันผวน
> - `05_risk_management_framework.md` — การจัดการความเสี่ยงพอร์ต
>
> กลยุทธ์ทั้งหมดต้องผ่านกรอบการจัดการความเสี่ยงก่อนดำเนินการ
> การกำหนดขนาดสถานะต้องใช้ Kelly Criterion พร้อมการปรับแบบ Fractional
> ขั้นตอนฉุกเฉินมีอำนาจเหนือตรรกะกลยุทธ์ทั้งหมด
