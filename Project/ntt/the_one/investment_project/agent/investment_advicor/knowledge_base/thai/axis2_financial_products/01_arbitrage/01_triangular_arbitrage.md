# การเก็งกำไรสามเหลี่ยม (Triangular Arbitrage) — เอกสารกลยุทธ์ฉบั��สมบูรณ์

> **เวอร์ชันเอกสาร:** 2.0
> **อัปเดตล่าสุด:** 2026-04-12
> **การจัดประเภท:** Core Knowledge Base — Axis 2: ผลิตภัณฑ์ทางการเงิน
> **ประเภทกลยุทธ์:** Pure (Near Risk-Free) Arbitrage
> **ตลาด:** Forex, Crypto (CeFi & DeFi)
> **ความถี่:** High-Frequency (มิลลิวินาทีถึงวินาที)

---

## สารบัญ

1. [ตรรกะหลัก](#1-ตรรกะหลัก)
2. [การเลือกคู่สกุลเงิน](#2-การเลือกคู่สกุลเงิน)
3. [การคำนวณ Cross-Rate](#3-การคำนวณ-cross-rate)
4. [การคำนวณกำไรและโครงสร้างค่าธรรมเนียม](#4-การคำนวณกำไรและโครงสร้างค่าธรรมเนียม)
5. [เกณฑ์สเปรดขั้นต่ำที่ทำกำไร](#5-เกณฑ์สเปรดขั้นต่ำที่ทำกำไร)
6. [ข้อกำหนดความเร็วในการดำเนินการ](#6-ข้อกำหนดความเร็วในการดำเนินการ)
7. [ปัจจัยความเสี่ยง](#7-ปัจจัยความเสี่ยง)
8. [อัลกอริทึม Pseudocode ฉบับสมบูรณ์](#8-อัลกอริทึม-pseudocode-ฉบับสมบูรณ์)
9. [ตัวอย่างพร้อมตัวเลขจริง](#9-ตัวอย่างพร้อมตัวเลขจริง)
10. [พารามิเตอร์ความเสี่ยงและ Position Sizing](#10-พารามิเตอร์ความเสี่ยงและ-position-sizing)
11. [กรอบ Backtesting](#11-กรอบ-backtesting)
12. [ข้อพิจารณาสำหรับ Production Deployment](#12-ข้อพิจารณาสำหรับ-production-deployment)
13. [เอกสารอ้างอิง](#13-เอกสารอ้างอิง)

---

## 1. ตรรกะหลัก

### 1.1 Triangular Arbitrage คืออะไร?

การเก็งกำไรสามเหลี่ยม (Triangular Arbitrage) ใช้ประโยชน์จากความไม่สอดคล้องของราคาระหว่างคู่สกุลเงินที่เกี่ยวข้องสามคู่ที่ซื้อขายบนตลาดเดียวกัน (หรือข้ามช่องทาง) เมื่อ cross-rate ที่โดยนัยจากคู่สกุลเงินสองคู่เบี่ยงเบนจากคู่ที่สามที่เสนอราคาโดยตรง สามารถล็อกกำไรปลอดความเสี่ยงได้โดยดำเนินการเทรดสามรายการที่สร้างวงปิดพร้อมกัน

### 1.2 ความสัมพันธ์สามเหลี่ยม

กำหนดสกุลเงินสาม A, B, และ C เงื่อนไข no-arbitrage ต้องการ:

$$\frac{A}{B} = \frac{A}{C} \times \frac{C}{B}$$

หรือเทียบเท่า:

$$R_{A/B} \times R_{B/C} \times R_{C/A} = 1$$

เมื่อผลคูณนี้เบี่ยงเบนจาก 1 โอกาส arbitrage มีอยู่

### 1.3 ตรรกะทีละขั้น

**ทิศทางที่ 1 (ตามเข็มนาฬิกา): A -> B -> C -> A**

```
Step 1: แปลงสกุลเงิน A เป็นสกุลเงิน B
        ซื้อ B ด้วย A ที่อัตรา R_{A/B}
        จำนวน B = Q_A / R_{A/B}  (ถ้า R_{A/B} คือราคาของ B ในหน่วย A)
        
Step 2: แปลงสกุลเงิน B เป็นสกุลเงิน C
        ซื้อ C ด้วย B ที่อัตรา R_{B/C}
        จำนวน C = Q_B / R_{B/C}
        
Step 3: แปลงสกุลเงิน C กลับเป็นสกุลเงิน A
        ซื้อ A ด้วย C ที่อัตรา R_{C/A}
        จำนวน A = Q_C / R_{C/A}
        
ถ้าจำนวน A สุดท้าย > จำนวน A เริ่มต้น (หลังหักค่าธรรมเนียม) = มีกำไร
```

**ทิศทางที่ 2 (ทวนเข็มนาฬิกา): A -> C -> B -> A**

```
Step 1: แปลงสกุลเงิน A เป็นสกุลเงิน C
Step 2: แปลงสกุลเงิน C เป็นสกุลเงิน B
Step 3: แปลงสกุลเงิน B กลับเป็นสกุลเงิน A
```

ทั้งสองทิศทางต้องตรวจสอบพร้อมกัน เพราะทิศทางที่ทำกำไรขึ้นอยู่กับ cross-rate ที่ถูกตั้งราคาผิด

### 1.4 การตรวจจับทิศทาง Arbitrage

คำนวณผลคูณ implied cross-rate สำหรับทิศทางตามเข็มนาฬิกา:

$$\Pi_{CW} = R_1 \times R_2 \times R_3$$

และสำหรับทิศทางทวนเข็มนาฬิกา:

$$\Pi_{CCW} = \frac{1}{R_1} \times \frac{1}{R_2} \times \frac{1}{R_3} = \frac{1}{\Pi_{CW}}$$

- ถ้า $\Pi_{CW} > 1$: กำไรมีอยู่ในทิศทางตามเข็มนาฬิกา
- ถ้า $\Pi_{CW} < 1$: กำไรมีอยู่ในทิศทางทวนเข็มนาฬิกา (เทียบเท่า $\Pi_{CCW} > 1$)
- ถ้า $\Pi_{CW} = 1$: ไม่มีโอกาส arbitrage

**ประเด็นสำคัญ — การใช้ราคา Bid/Ask:**

ในทางปฏิบัติ คุณต้องใช้ด้านที่เหมาะสมของ order book:
- เมื่อ **ขาย** สกุลเงิน X เป็น Y: ใช้ราคา **bid** (คุณได้รับ bid)
- เมื่อ **ซื้อ** สกุลเงิน X ด้วย Y: ใช้ราคา **ask** (คุณจ่าย ask)

---

## 2. การเลือกคู่สกุลเงิน

### 2.1 คู่ Forex

สามเหลี่ยม triangular arbitrage ที่พบบ่อยที่สุดใน Forex เกี่ยวข้องกับสกุลเงินหลักที่มีสภาพคล่องสูง:

**ระดับ 1 (สภาพคล่องสูงสุด — การแข่งขันสูงสุด):**

| สามเหลี่ยม | คู่ 1 | คู่ 2 | คู่ 3 |
|-----------|-------|-------|-------|
| USD-EUR-GBP | EUR/USD | GBP/USD | EUR/GBP |
| USD-EUR-JPY | EUR/USD | USD/JPY | EUR/JPY |
| USD-GBP-JPY | GBP/USD | USD/JPY | GBP/JPY |
| USD-EUR-CHF | EUR/USD | USD/CHF | EUR/CHF |

**ระดับ 2 (สภาพคล่องปานกลาง — โอกาสมากกว่า):**

| สามเหลี่ยม | คู่ 1 | คู่ 2 | คู่ 3 |
|-----------|-------|-------|-------|
| USD-AUD-NZD | AUD/USD | NZD/USD | AUD/NZD |
| USD-EUR-AUD | EUR/USD | AUD/USD | EUR/AUD |
| USD-GBP-CHF | GBP/USD | USD/CHF | GBP/CHF |
| USD-CAD-JPY | USD/CAD | USD/JPY | CAD/JPY |

### 2.2 คู่ Crypto

ตลาดคริปโตเสนอโอกาส triangular arbitrage ที่มากกว่าอย่างมีนัยสำคัญ เนื่องจากตลาดกระจัดกระจายและมีประสิทธิภาพต่ำกว่า

**ระดับ 1 (สามเหลี่ยมคริปโตหลัก):**

| สามเหลี่ยม | คู่ 1 | คู่ 2 | คู่ 3 |
|-----------|-------|-------|-------|
| USDT-BTC-ETH | BTC/USDT | ETH/USDT | ETH/BTC |
| USDT-BTC-BNB | BTC/USDT | BNB/USDT | BNB/BTC |
| USDT-BTC-SOL | BTC/USDT | SOL/USDT | SOL/BTC |
| USDT-ETH-BNB | ETH/USDT | BNB/USDT | BNB/ETH |

**ระดับ 2 (สามเหลี่ยม Alt-coin):**

| สามเหลี่ยม | คู่ 1 | คู่ 2 | คู่ 3 |
|-----------|-------|-------|-------|
| USDT-BTC-XRP | BTC/USDT | XRP/USDT | XRP/BTC |
| USDT-BTC-ADA | BTC/USDT | ADA/USDT | ADA/BTC |
| USDT-ETH-LINK | ETH/USDT | LINK/USDT | LINK/ETH |
| USDT-BTC-AVAX | BTC/USDT | AVAX/USDT | AVAX/BTC |

**ระดับ 3 (สามเหลี่ยม Cross-Stablecoin):**

| สามเหลี่ยม | คู่ 1 | คู่ 2 | คู่ 3 |
|-----------|-------|-------|-------|
| USDT-USDC-BTC | BTC/USDT | BTC/USDC | USDT/USDC |
| USDT-BUSD-ETH | ETH/USDT | ETH/BUSD | USDT/BUSD |
| USDC-DAI-ETH | ETH/USDC | ETH/DAI | USDC/DAI |

### 2.3 เกณฑ์การเลือกคู่

สำหรับ triangular arbitrage ที่มีประสิทธิภาพ สามเหลี่ยมที่เลือกควรเป็นไปตาม:

1. **สภาพคล่องเพียงพอ:** ปริมาณเฉลี่ยรายวัน > $10M ต่อคู่ (คริปโต) หรือ > $1B ต่อคู่ (forex)
2. **สเปรดแคบ:** Bid-ask spread < 5 bps (ดีที่สุด < 2 bps)
3. **ความลึก Order book:** อย่างน้อย 5 BTC equivalent depth ภายใน 10 bps ของ mid-price
4. **ความสัมพันธ์ต่ำของการเคลื่อนตัวสเปรด:** สเปรดไม่ควรขยายพร้อมกันทั้งสามคู่
5. **รองรับโดยตลาด:** ทั้งสามคู่มีให้บริการบนตลาดเดียวกัน
6. **รองรับ API:** มี real-time WebSocket order book feed

---

## 3. การคำนวณ Cross-Rate

### 3.1 Cross-Rate โดยตรง

สำหรับสกุลเงิน A, B, C ที่ตลาดเสนอคู่เป็น A/B, B/C, และ A/C:

**Implied cross-rate ของ A/C จาก A/B และ B/C:**

$$\hat{R}_{A/C} = R_{A/B} \times R_{B/C}$$

**สัญญาณ Arbitrage:**

$$\delta = \frac{R_{A/C}^{market} - \hat{R}_{A/C}}{\hat{R}_{A/C}}$$

ถ้า $|\delta| > \delta_{threshold}$ (ที่ $\delta_{threshold}$ รวมค่าธรรมเนียมและต้นทุนทั้งหมด) โอกาสมีอยู่

### 3.2 Cross-Rate ที่ปรับด้วย Bid-Ask

Cross-rates ที่ใช้ได้ต้องรวม bid-ask spreads:

**สำหรับทิศทางตามเข็มนาฬิกา (ซื้อ B ด้วย A, ซื้อ C ด้วย B, ขาย C เป็น A):**

**ตัวอย่าง: EUR/USD, GBP/USD, EUR/GBP**

**ตามเข็มนาฬิกา: USD -> EUR -> GBP -> USD**

1. ซื้อ EUR ด้วย USD: จ่าย $ask_{EUR/USD}$ ต่อ EUR ได้ $\frac{Q_{USD}}{ask_{EUR/USD}}$ EUR
2. ขาย EUR เป็น GBP: ขาย EUR ที่ $bid_{EUR/GBP}$ ได้ $Q_{EUR} \times bid_{EUR/GBP}$ GBP
3. ขาย GBP เป็น USD: ขาย GBP ที่ $bid_{GBP/USD}$ ได้ $Q_{GBP} \times bid_{GBP/USD}$ USD

**จำนวน USD สุดท้าย:**

$$Q_{final} = Q_{USD} \times \frac{bid_{EUR/GBP} \times bid_{GBP/USD}}{ask_{EUR/USD}}$$

**เงื่อนไขกำไร (ก่อนค่าธรรมเนียม):**

$$\frac{bid_{EUR/GBP} \times bid_{GBP/USD}}{ask_{EUR/USD}} > 1$$

### 3.3 การปรับอัตราให้เป็นมาตรฐาน (Rate Normalization)

ตลาดต่างๆ เสนอคู่ในรูปแบบที่แตกต่างกัน ขั้นตอนสำคัญคือการปรับอัตราทั้งหมดให้อยู่ในรูปแบบที่สอดคล้อง

**หลักเกณฑ์: Base/Quote ที่อัตรา = ราคาของ 1 หน่วย Base ในสกุล Quote**

ถ้าคู่ถูกเสนอเป็น Quote/Base บนตลาด ให้กลับค่า:

$$R_{Base/Quote} = \frac{1}{R_{Quote/Base}}$$

และการกลับค่า bid/ask:

$$bid_{Base/Quote} = \frac{1}{ask_{Quote/Base}}$$
$$ask_{Base/Quote} = \frac{1}{bid_{Quote/Base}}$$

---

## 4. การคำนวณกำไรและโครงสร้างค่าธรรมเนียม

### 4.1 สูตรกำไรขั้นต้น

สำหรับ triangular arbitrage ที่เริ่มต้นและสิ้นสุดด้วยปริมาณ $Q_{initial}$ ของสกุลเงิน A:

$$Q_{final} = Q_{initial} \times R_1^{eff} \times R_2^{eff} \times R_3^{eff}$$

โดยที่ $R_i^{eff}$ คืออัตราที่ใช้ได้สำหรับขา $i$ (ใช้ bid หรือ ask ที่เหมาะสม)

$$P_{gross} = Q_{final} - Q_{initial}$$

### 4.2 โครงสร้างค่าธรรมเนียม

#### 4.2.1 ค่าธรรมเนียมการเทรด (Maker/Taker)

| ตลาด | Maker Fee | Taker Fee | VIP Taker Fee |
|------|:---------:|:---------:|:-------------:|
| **Forex (ECN)** | $0-3/million | $2-5/million | $0-2/million |
| **Binance** | 0.10% | 0.10% | 0.02% (VIP 9) |
| **Coinbase Advanced** | 0.40% | 0.60% | 0.05% (VIP) |
| **OKX** | 0.08% | 0.10% | 0.02% (VIP 7) |
| **Bybit** | 0.10% | 0.10% | 0.02% (VIP) |
| **Kraken** | 0.16% | 0.26% | 0.00% / 0.10% |

**ค่าธรรมเนียมต่อขา:**

$$F_i = Q_i \times P_i \times f_i$$

**ค่าธรรมเนียมรวมสำหรับ 3-leg arbitrage:**

$$F_{total} = \sum_{i=1}^{3} F_i = \sum_{i=1}^{3} Q_i \times P_i \times f_i$$

สำหรับกรณีง่ายที่อัตราค่าธรรมเนียมเท่ากันทุกขา:

$$F_{total} \approx 3 \times Q_{initial} \times f$$

#### 4.2.2 ต้นทุนสเปรด

$$C_{spread,i} = Q_i \times \frac{ask_i - bid_i}{2}$$

ต้นทุนสเปรดรวม:

$$C_{spread} = \sum_{i=1}^{3} C_{spread,i}$$

#### 4.2.3 การประมาณ Slippage

$$C_{slippage,i} = Q_i \times P_i \times s_i$$

**แบบจำลองการประมาณ Slippage:**

$$s_i = \alpha_i \times \left(\frac{Q_i}{D_i}\right)^{\beta_i}$$

โดยที่:
- $D_i$ = ความลึก order book ที่ระดับดีที่สุด
- $\alpha_i$ = ค่าคงที่การปรับขนาด (ปรับเทียบจากข้อมูลในอดีต)
- $\beta_i$ = พารามิเตอร์ความยืดหยุ่น (ปกติ 0.5 - 1.5)

### 4.3 สูตรกำไรสุทธิ

สูตรกำไรสุทธิฉบับสมบูรณ์:

$$\boxed{P_{net} = Q_{initial} \times \left(\prod_{i=1}^{3} R_i^{eff} \times (1 - f_i) \times (1 - s_i) - 1\right)}$$

โดยที่:
- $R_i^{eff}$ = อัตราแลกเปลี่ยนที่ใช้ได้สำหรับขา $i$ (bid หรือ ask ตามเหมาะสม)
- $f_i$ = อัตราค่าธรรมเนียมสำหรับขา $i$
- $s_i$ = อัตรา slippage ประมาณสำหรับขา $i$
- $Q_{initial}$ = ปริมาณเริ่มต้นในสกุลเงินเริ่มต้น

### 4.4 ผลตอบแทนต่อทุน (Return on Capital)

$$r = \frac{P_{net}}{Q_{initial}} = \prod_{i=1}^{3} R_i^{eff} \times (1 - f_i) \times (1 - s_i) - 1$$

ผลตอบแทนรายปีขึ้นอยู่กับความถี่ของการเทรดที่ทำกำไร:

$$R_{annual} = (1 + r)^{N} - 1$$

โดยที่ $N$ คือจำนวนการเทรดต่อปี

---

## 5. เกณฑ์สเปรดขั้นต่ำที่ทำกำไร

### 5.1 การอนุมาน

สำหรับ triangular arbitrage ที่จะทำกำไร cross-rate deviation ต้องเกินต้นทุนทั้งหมด:

$$\left|\prod_{i=1}^{3} R_i^{eff} - 1\right| > \sum_{i=1}^{3} (f_i + s_i) + \epsilon$$

โดยที่ $\epsilon$ คือ safety margin

**สเปรดขั้นต่ำแบบง่าย (สมมติค่าธรรมเนียมและ slippage เท่ากันทุกขา):**

$$\delta_{min} = 3f + 3s + \epsilon$$

**ตัวอย่างสำหรับ Binance (standard tier):**

$$\delta_{min} = 3 \times 0.001 + 3 \times 0.0002 + 0.0005 = 0.0041 = 41 \text{ bps}$$

**ตัวอย่างสำหรับ Binance (VIP 9 + ส่วนลด BNB):**

$$\delta_{min} = 3 \times 0.0002 + 3 \times 0.0001 + 0.0003 = 0.0012 = 12 \text{ bps}$$

### 5.2 การคำนวณเกณฑ์แบบไดนามิก

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

### 5.3 Heat Map ความสามารถในการทำกำไร

| Fee Tier | ตลาดสงบ (spread < 2bps) | ปกติ (spread 2-5bps) | ผันผวน (spread > 5bps) |
|----------|:---------------------------:|:----------------------:|:------------------------:|
| Standard (0.10%) | ไม่ทำกำไร | โอกาสหายาก | เป็นไปได้ |
| VIP Mid (0.05%) | โอกาสหายาก | ปานกลาง | ดี |
| VIP Top (0.02%) | ปานกลาง | ดี | ดีเยี่ยม |
| Market Maker (0.00%) | ดี | ดีเยี่ยม | ดีเยี่ยม |

---

## 6. ข้อกำหนดความเร็วในการดำเนินการ

### 6.1 งบประมาณ Latency

| ส่วนประกอบ | Forex (เป้าหมาย) | Crypto (เป้าหมาย) |
|-----------|:--------------:|:---------------:|
| รับข้อมูลตลาด | < 10 us | < 1 ms |
| ตรวจจับโอกาส | < 5 us | < 0.5 ms |
| ตรวจสอบความสามารถทำกำไร | < 2 us | < 0.2 ms |
| ตรวจสอบความเสี่ยง | < 2 us | < 0.2 ms |
| สร้างคำสั่ง | < 1 us | < 0.1 ms |
| ส่งผ่านเครือข่าย | < 50 us | < 5 ms |
| Exchange matching | < 100 us | < 10 ms |
| **รวม** | **< 170 us** | **< 17 ms** |

### 6.2 เหตุใดความเร็วจึงสำคัญ

โอกาส Triangular arbitrage ในตลาดที่มีสภาพคล่องมีครึ่งชีวิตวัดเป็น:
- **Forex:** 10-100 มิลลิวินาที (คู่หลัก)
- **Crypto (คู่หลัก):** 100ms - 5 วินาที
- **Crypto (คู่ alt):** 1 - 30 วินาที

**แบบจำลองการสลายตัวของโอกาส:**

$$P(opportunity\_available | t) = e^{-\lambda t}$$

โดยที่ $\lambda$ คืออัตราการสลายตัว สำหรับ Forex majors $\lambda \approx 10-100/s$ สำหรับ crypto $\lambda \approx 0.2-2/s$

---

## 7. ปัจจัยความเสี่ยง

### 7.1 ความเสี่ยงการดำเนินการ (Execution Risk)

ความเสี่ยงหลักใน triangular arbitrage คือไม่ทุกขาจะดำเนินการสำเร็จหรือที่ราคาที่คาดหวัง

**7.1.1 Partial Fills**

ถ้าหนึ่งหรือสองขาเติมเต็มแต่ขาที่สามไม่:
- คุณถูกทิ้งไว้กับสถานะที่ไม่ได้เฮดจ์
- สถานะที่เหลืออยู่ภายใต้ความเสี่ยงตลาด
- ต้องปิดทันที มักเกิดขาดทุน

**การบรรเทา:**
- ใช้คำสั่ง Fill-or-Kill (FOK) หรือ Immediate-or-Cancel (IOC)
- ขนาดคำสั่งอนุรักษ์เทียบกับความลึก order book
- ติดตั้งตรรกะปิดสถานะอัตโนมัติ

### 7.2 ความเสี่ยง Slippage

**Slippage ที่คาดหวังตามขนาดคำสั่ง (Crypto, คู่หลักบน Binance):**

| ขนาดคำสั่ง (USD) | Slippage ที่คาดหวัง (bps) | ส่วนเบี่ยงเบนมาตรฐาน (bps) |
|:-----------------:|:-----------------------:|:------------------------:|
| $1,000 | 0.1 | 0.05 |
| $10,000 | 0.5 | 0.3 |
| $50,000 | 2.0 | 1.5 |
| $100,000 | 5.0 | 3.0 |
| $500,000 | 15.0 | 10.0 |

### 7.3 ความเสี่ยงจังหวะเวลา (Timing Risk)

ระหว่างการตรวจจับโอกาสและการดำเนินการทั้งสามขา:
- ราคาอาจเคลื่อน ทำให้ arbitrage เป็นโมฆะ
- ผู้เข้าร่วมอื่นอาจดูดซับสภาพคล่องที่มีอยู่
- ตลาดอาจมีความล่าช้าชั่วขณะ

### 7.4 ความเสี่ยงเทคโนโลยี

- API rate limiting (ตลาดอาจปฏิเสธคำสั่งหากเกิน rate limit)
- WebSocket disconnections (ข้อมูลเก่านำไปสู่สัญญาณเท็จ)
- Exchange maintenance windows
- บั๊กซอฟต์แวร์ในการคำนวณราคาหรือสร้างคำสั่ง

---

## 8. อัลกอริทึม Pseudocode ฉบับสมบูรณ์

### 8.1 เครื่องยนต์ Triangular Arbitrage หลัก

```python
import asyncio
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum

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
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    timestamp: float
    
    @property
    def best_bid(self) -> float:
        return self.bids[0].price if self.bids else 0
    
    @property
    def best_ask(self) -> float:
        return self.asks[0].price if self.asks else float('inf')
    
    @property
    def spread_bps(self) -> float:
        return (self.best_ask - self.best_bid) / self.mid_price * 10000

@dataclass
class TriangularArbConfig:
    triangles: List[Tuple[str, str, str]]
    fee_rates: dict
    default_fee_rate: float = 0.001
    min_profit_bps: float = 3.0
    safety_margin_bps: float = 1.0
    base_order_size_usd: float = 10000
    max_order_size_usd: float = 50000
    max_execution_time_ms: float = 500
    order_type: str = "LIMIT_IOC"
    max_slippage_bps: float = 5.0
    max_daily_loss_usd: float = 500
    max_consecutive_losses: int = 5
    min_book_depth_usd: float = 20000
    max_book_age_ms: float = 100

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
        self.order_books: dict = {}
        self.daily_pnl: float = 0.0
        self.daily_trades: int = 0
        self.consecutive_losses: int = 0
        self.is_running: bool = False
    
    async def start(self):
        """Main entry point."""
        self.is_running = True
        all_pairs = set()
        for triangle in self.config.triangles:
            all_pairs.update(triangle)
        
        subscription_tasks = [
            self.subscribe_order_book(pair) for pair in all_pairs
        ]
        monitoring_task = asyncio.create_task(self.monitoring_loop())
        await asyncio.gather(*subscription_tasks, monitoring_task)
    
    async def monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_running:
            if self.check_circuit_breakers():
                break
            
            for triangle in self.config.triangles:
                if not self.validate_order_books(triangle):
                    continue
                
                opportunity = self.detect_opportunity(triangle)
                if opportunity is not None:
                    result = await self.execute_opportunity(opportunity)
                    if result is not None:
                        self.process_result(result)
            
            await asyncio.sleep(0.001)
    
    def detect_opportunity(self, triangle):
        """Detect triangular arbitrage opportunity."""
        pair1, pair2, pair3 = triangle
        book1, book2, book3 = (
            self.order_books[pair1],
            self.order_books[pair2],
            self.order_books[pair3]
        )
        
        cw_product = self.calculate_cross_rate_product(
            book1, book2, book3, Direction.CLOCKWISE
        )
        ccw_product = self.calculate_cross_rate_product(
            book1, book2, book3, Direction.COUNTER_CLOCKWISE
        )
        
        best_direction = None
        best_product = 1.0
        
        if cw_product > best_product:
            best_direction = Direction.CLOCKWISE
            best_product = cw_product
        if ccw_product > best_product:
            best_direction = Direction.COUNTER_CLOCKWISE
            best_product = ccw_product
        
        if best_direction is None:
            return None
        
        deviation_bps = (best_product - 1.0) * 10000
        if deviation_bps < self.config.min_profit_bps:
            return None
        
        return ArbitrageOpportunity(
            triangle=triangle,
            direction=best_direction,
            expected_profit_bps=deviation_bps,
            timestamp=time.time()
        )
    
    def calculate_cross_rate_product(self, book1, book2, book3, direction):
        """Calculate the cross-rate product for a given direction."""
        if direction == Direction.CLOCKWISE:
            product = (1.0 / book1.best_ask) * (1.0 / book2.best_ask) * book3.best_bid
        else:
            product = (1.0 / book3.best_ask) * book2.best_bid * book1.best_bid
        
        fee1 = self.config.fee_rates.get(book1.pair, self.config.default_fee_rate)
        fee2 = self.config.fee_rates.get(book2.pair, self.config.default_fee_rate)
        fee3 = self.config.fee_rates.get(book3.pair, self.config.default_fee_rate)
        
        product *= (1 - fee1) * (1 - fee2) * (1 - fee3)
        return product
```

---

## 9. ตัวอย่างพร้อมตัวเลขจริง

### 9.1 ตัวอย่าง Crypto: USDT-BTC-ETH บน Binance

**ข้อมูลตลาด:**
- BTC/USDT: bid = 65,000, ask = 65,010
- ETH/USDT: bid = 3,400, ask = 3,401
- ETH/BTC: bid = 0.05230, ask = 0.05232

**ทิศทางตามเข็มนาฬิกา: USDT -> BTC -> ETH -> USDT**
1. ซื้อ BTC ด้วย USDT: $10,000 / 65,010 = 0.15382 BTC
2. ขาย BTC ซื้อ ETH: 0.15382 / 0.05232 = 2.9401 ETH
3. ขาย ETH เป็น USDT: 2.9401 * 3,400 = $9,996.34

กำไรขั้นต้น: $9,996.34 - $10,000 = -$3.66 (ขาดทุน ในทิศทางนี้)

**ทิศทางทวนเข็มนาฬิกา: USDT -> ETH -> BTC -> USDT**
1. ซื้อ ETH ด้วย USDT: $10,000 / 3,401 = 2.9403 ETH
2. ขาย ETH ซื้อ BTC: 2.9403 * 0.05230 = 0.15378 BTC
3. ขาย BTC เป็น USDT: 0.15378 * 65,000 = $9,995.70

กำไรขั้นต้น: -$4.30 (ไม่มีโอกาสในทั้งสองทิศทาง — ปกติของตลาดที่มีประสิทธิภาพ)

---

## 10. พารามิเตอร์ความเสี่ยงและ Position Sizing

### 10.1 ขนาดคำสั่งที่เหมาะสม

$$Q^* = \min\left(\frac{D_{min}}{3}, Q_{max}, \frac{Capital \times f^*}{P}\right)$$

โดยที่:
- $D_{min}$ = ความลึกขั้นต่ำข้ามสามคู่
- $Q_{max}$ = ขนาดคำสั่งสูงสุดที่ตั้งค่า
- $f^*$ = สัดส่วน Kelly (หรือ fractional Kelly)

### 10.2 ขีดจำกัดรายวัน

- ขาดทุนสูงสุดรายวัน: $500
- จำนวนเทรดสูงสุดรายวัน: 1,000
- การขาดทุนต่อเนื่องสูงสุด: 5 ครั้งก่อนหยุด

---

## 11. กรอบ Backtesting

### 11.1 ข้อกำหนดข้อมูล

- ข้อมูล order book ย้อนหลัง (tick-level)
- ข้อมูล trade ย้อนหลัง
- ตาราง fee ในอดีต
- ข้อมูล latency ในอดีต

### 11.2 เมตริกหลัก

- Sharpe Ratio
- Maximum Drawdown
- Win Rate
- Average Profit per Trade
- Profit Factor
- ปริมาณโอกาสต่อวัน

---

## 12. ข้อพิจารณาสำหรับ Production Deployment

- ใช้ WebSocket สำหรับ real-time data
- รักษา local order book copy
- Pre-compute order templates
- ใช้ concurrent execution สำหรับทั้ง 3 ขา
- ติดตั้ง automatic position unwind
- ติดตาม API rate limits
- จัดเก็บ trade logs สำหรับการวิเคราะห์ post-trade

---

## 13. เอกสารอ้างอิง

1. Fenn, D. J., et al. (2009). "The mirage of triangular arbitrage in the spot foreign exchange market." International Journal of Theoretical and Applied Finance.
2. Aiba, Y., et al. (2002). "Triangular arbitrage as an interaction among foreign exchange rates." Physica A.
3. Binance API Documentation: https://binance-docs.github.io/apidocs/
4. CCXT Library: https://docs.ccxt.com/

---

> **เอกสารถัดไป**: [02_funding_rate_arbitrage.md](./02_funding_rate_arbitrage.md) — Funding Rate Arbitrage (Cash-and-Carry)
