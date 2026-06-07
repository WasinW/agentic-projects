# กลยุทธ์ออปชัน: คู่มือครบถ้วน

> **แกนที่ 2 — ผลิตภัณฑ์ทางการเงิน | โมดูล 03: อนุพันธ์และผลิตภัณฑ์ที่มีโครงสร้าง**
> **เอกสาร 01 — คู่มือกลยุทธ์ออปชันแบบครบถ้วน**
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

### 1.1 พื้นฐานออปชัน

#### 1.1.1 Call Options

Call Option ให้สิทธิ์ผู้ถือในการ **ซื้อ** สินทรัพย์อ้างอิง ณ ราคาใช้สิทธิ์ $K$ ก่อนหรือ ณ วันหมดอายุ $T$

**ผลตอบแทน ณ วันหมดอายุ:**

$$\text{Call Payoff} = \max(S_T - K, 0)$$

$$\text{Call P\&L} = \max(S_T - K, 0) - C_0$$

โดยที่:
- $S_T$ = ราคาสินทรัพย์อ้างอิง ณ วันหมดอายุ
- $K$ = ราคาใช้สิทธิ์ (Strike Price)
- $C_0$ = ค่าพรีเมียมที่จ่ายสำหรับ Call

#### 1.1.2 Put Options

Put Option ให้สิทธิ์ผู้ถือในการ **ขาย** สินทรัพย์อ้างอิง ณ ราคาใช้สิทธิ์ $K$ ก่อนหรือ ณ วันหมดอายุ $T$

**ผลตอบแทน ณ วันหมดอายุ:**

$$\text{Put Payoff} = \max(K - S_T, 0)$$

$$\text{Put P\&L} = \max(K - S_T, 0) - P_0$$

โดยที่ $P_0$ = ค่าพรีเมียมที่จ่ายสำหรับ Put

#### 1.1.3 ออปชันแบบ American เทียบกับ European

| คุณสมบัติ | American | European |
|---|---|---|
| การใช้สิทธิ์ | ได้ทุกเวลาก่อนหมดอายุ | ได้เฉพาะวันหมดอายุ |
| การกำหนดราคา | ซับซ้อนกว่า (Binomial Tree, Finite Difference) | Black-Scholes แบบ Closed-form |
| ค่าพรีเมียม | ≥ European (มี Early Exercise Premium) | ค่าพื้นฐาน |
| พบมากใน | ออปชันหุ้น (ตลาดสหรัฐฯ) | Forex OTC, คริปโต (Deribit) |
| การใช้สิทธิ์ก่อนเวลาเหมาะสมเมื่อ | Deep ITM Puts, หุ้นจ่ายปันผล | ไม่เคยเหมาะสมถ้าไม่มีปันผล |

#### 1.1.4 ลักษณะเฉพาะของออปชันคริปโต

**ลักษณะเฉพาะของตลาดออปชันคริปโต:**

1. **แบบ European เท่านั้น**: ทุกตลาดคริปโตหลัก (Deribit, OKX, Binance) เสนอเฉพาะ European Options
2. **ชำระเป็นเงินสด (Cash Settlement)**: ชำระในคริปโตอ้างอิง (BTC/ETH บน Deribit) หรือ USDC
3. **ราคาชำระ (Settlement Price)**: Deribit ใช้ TWAP 30 นาทีของ Index ณ 08:00 UTC ในวันหมดอายุ
4. **Tick Size**: $0.0005 BTC สำหรับ BTC Options บน Deribit (มูลค่าตามสัญญาขึ้นกับราคา BTC)
5. **ขนาดสัญญา**: 1 BTC ต่อสัญญา (Deribit), 0.01 BTC (Binance)
6. **ตาราง Expiry**: มีทั้งรายวัน รายสัปดาห์ รายเดือน และรายไตรมาส
7. **IV พื้นฐานสูง**: BTC ATM IV ปกติ 50-80%, ETH 60-100% (เทียบกับ SPX 15-25%)
8. **โครงสร้าง Term Structure ของ IV**: มักกลับหัวรอบเหตุการณ์สำคัญ; ปกติเป็นขาขึ้นในตลาดสงบ
9. **Skew**: มี Put Skew อย่างต่อเนื่องใน BTC/ETH (ความต้องการป้องกัน Crash)
10. **Block Trading**: มีผ่าน Paradigm Protocol สำหรับคำสั่งขนาดใหญ่
11. **Portfolio Margin**: Deribit เสนอ Portfolio Margin เพื่อลดเงินทุนที่ต้องใช้

**ขนาดตลาดออปชันคริปโต (ณ ปี 2026):**
- BTC Options Open Interest: >$20B มูลค่าตามสัญญา
- ETH Options Open Interest: >$10B มูลค่าตามสัญญา
- ปริมาณรายวัน: $2-5B มูลค่าตามสัญญา
- ส่วนแบ่งตลาด Deribit: ~80%

### 1.2 แบบจำลอง Black-Scholes-Merton

แบบจำลอง Black-Scholes-Merton (BSM) ให้คำตอบแบบ Closed-form สำหรับการกำหนดราคา European Options ภายใต้สมมติฐานดังนี้:

**สมมติฐาน:**
1. การกระจายผลตอบแทนเป็น Log-normal
2. ความผันผวน $\sigma$ คงที่
3. อัตราดอกเบี้ยปลอดความเสี่ยง $r$ คงที่
4. ไม่มีค่าธรรมเนียมหรือภาษี
5. สามารถเทรดแบบต่อเนื่อง
6. ไม่มีเงินปันผล (ส่วนขยาย Merton รองรับเงินปันผล)
7. ไม่มีโอกาส Arbitrage

**ราคา European Call:**

$$C = S_0 N(d_1) - Ke^{-rT}N(d_2)$$

**ราคา European Put:**

$$P = Ke^{-rT}N(-d_2) - S_0 N(-d_1)$$

**พารามิเตอร์สำคัญ:**

$$d_1 = \frac{\ln(S_0/K) + (r + \sigma^2/2)T}{\sigma\sqrt{T}}$$

$$d_2 = d_1 - \sigma\sqrt{T}$$

โดยที่:
- $S_0$ = ราคา Spot ปัจจุบันของสินทรัพย์อ้างอิง
- $K$ = ราคาใช้สิทธิ์
- $T$ = เวลาจนหมดอายุ (เป็นปี)
- $r$ = อัตราดอกเบี้ยปลอดความเสี่ยง (รายปี)
- $\sigma$ = ความผันผวนของสินทรัพย์อ้างอิง (รายปี)
- $N(\cdot)$ = ฟังก์ชัน Cumulative Standard Normal Distribution

**Put-Call Parity:**

$$C - P = S_0 - Ke^{-rT}$$

ความสัมพันธ์พื้นฐานนี้ต้องเป็นจริงสำหรับ European Options; การละเมิดบ่งชี้โอกาส Arbitrage

**ข้อจำกัดของ BSM สำหรับคริปโต:**
- ผลตอบแทนคริปโตมีหาง (Fat Tails) (Kurtosis > 3)
- ความผันผวนเป็น Stochastic ไม่คงที่
- ความเสี่ยง Jump มีนัยสำคัญ (การถูกแฮ็กตลาด ข่าวกฎระเบียบ)
- เทรด 24/7 กับสภาพคล่องที่ไม่คงที่
- Staking Yields ทำหน้าที่เหมือนเงินปันผลแบบต่อเนื่องสำหรับบางสินทรัพย์

**การปรับในทางปฏิบัติ:**
- ใช้ Implied Volatility แทน Historical Volatility สำหรับการกำหนดราคา
- ใช้แบบจำลอง Stochastic Volatility (Heston, SABR) สำหรับ Greeks ที่แม่นยำกว่า
- ปรับสำหรับ Jump Risk โดยใช้ Merton's Jump-Diffusion Model
- ใช้ตัวประมาณค่า Realized Vol ที่ทนต่อ Microstructure Noise (Yang-Zhang, Garman-Klass)

### 1.3 Greeks — การวิเคราะห์เชิงลึก

#### 1.3.1 Delta (Δ) — ความเสี่ยงด้านทิศทาง

**นิยาม:** อัตราการเปลี่ยนแปลงของราคาออปชันเทียบกับราคาสินทรัพย์อ้างอิง

$$\Delta_{call} = N(d_1) = \frac{\partial C}{\partial S}$$

$$\Delta_{put} = N(d_1) - 1 = \frac{\partial P}{\partial S}$$

**คุณสมบัติ:**
- Call Delta อยู่ระหว่าง 0 ถึง +1
- Put Delta อยู่ระหว่าง -1 ถึง 0
- ออปชัน ATM มี Delta ≈ ±0.50
- Delta เข้าใกล้ ±1 สำหรับออปชันที่ Deep ITM
- Delta เข้าใกล้ 0 สำหรับออปชันที่ Deep OTM
- Delta ประมาณเท่ากับความน่าจะเป็นที่จะหมดอายุแบบ ITM (ภายใต้มาตรวัด Risk-neutral)

**Delta เป็นอัตราส่วนการ Hedge:**
เพื่อ Delta-hedge สถานะ Short Call ให้ซื้อ Δ หน่วยของสินทรัพย์อ้างอิงสำหรับแต่ละออปชันที่ขาย

**ตัวอย่าง:**
- Short 10 BTC Call Options แต่ละตัวมี Delta = 0.45
- Portfolio Delta = -10 × 0.45 = -4.5 BTC
- Hedge: ซื้อ 4.5 BTC ใน Spot/Perp เพื่อให้ได้ Delta-neutral

**กลยุทธ์ Delta-Neutral:**
- Market Maker ทำ Delta-hedge ต่อเนื่องเพื่อแยก Greeks ตัวอื่น
- Delta-neutral ช่วยให้ทำกำไรจาก Gamma, Theta หรือ Vega
- ต้องปรับสมดุลแบบ Dynamic เมื่อ Delta เปลี่ยนไปตามราคา

**Delta ในบริบทคริปโต:**
- การ Delta-hedge ของ BTC ทำผ่านสัญญาถาวร (สภาพคล่องดีที่สุด)
- ต้องนำต้นทุน Funding Rate มาคิดในต้นทุนการ Delta-hedge
- การเคลื่อนไหวของราคาขนาดใหญ่ต้องปรับสมดุลบ่อยเนื่องจาก Gamma สูง

#### 1.3.2 Gamma (Γ) — ความเสี่ยงด้าน Convexity

**นิยาม:** อัตราการเปลี่ยนแปลงของ Delta เทียบกับราคาสินทรัพย์อ้างอิง

$$\Gamma = \frac{\partial^2 V}{\partial S^2} = \frac{N'(d_1)}{S_0 \sigma \sqrt{T}}$$

โดยที่ $N'(x) = \frac{1}{\sqrt{2\pi}}e^{-x^2/2}$

**คุณสมบัติ:**
- เป็นบวกเสมอสำหรับ Long Options (ทั้ง Calls และ Puts)
- สูงสุดสำหรับออปชัน ATM ใกล้หมดอายุ
- แสดงถึงความโค้งของ Payoff ของออปชัน
- Long Gamma = กำไรจากการเคลื่อนไหวขนาดใหญ่ (Convexity)
- Short Gamma = กำไรจากการเคลื่อนไหวเล็กน้อย (Time Decay) มีความเสี่ยงจากการเคลื่อนไหวขนาดใหญ่

**ความเสี่ยง Gamma ใกล้หมดอายุ:**
เมื่อ $T \to 0$ Gamma ของ ATM เข้าสู่อนันต์ สร้าง "Pin Risk" — ความไวสูงมากต่อการเปลี่ยนแปลงราคาเล็กน้อยใกล้วันหมดอายุ

**Dollar Gamma:**
$$\text{Dollar Gamma} = \frac{1}{2} \Gamma S^2 \times (\Delta S / S)^2$$

สำหรับการเคลื่อนไหว 1%: Dollar Gamma ต่อ 1% = $\frac{1}{2} \Gamma S^2 \times 0.01^2$

**Gamma Scalping:**
สถานะ Long Gamma สามารถทำกำไรผ่านการปรับ Delta:
1. เริ่มต้น Delta-neutral ด้วย Long Gamma
2. ราคาขึ้น → Delta เป็นบวก → ขาย Delta (ทำกำไร)
3. ราคาลง → Delta เป็นลบ → ซื้อ Delta (ทำกำไร)
4. ทำซ้ำ; ทำกำไรได้ถ้า Realized Vol > Implied Vol ที่จ่ายไป

#### 1.3.3 Theta (Θ) — Time Decay

**นิยาม:** อัตราการเปลี่ยนแปลงของราคาออปชันเทียบกับเวลา

$$\Theta_{call} = -\frac{S_0 N'(d_1) \sigma}{2\sqrt{T}} - rKe^{-rT}N(d_2)$$

$$\Theta_{put} = -\frac{S_0 N'(d_1) \sigma}{2\sqrt{T}} + rKe^{-rT}N(-d_2)$$

**คุณสมบัติ:**
- เป็นลบสำหรับ Long Options (เวลาทำงานต่อต้านผู้ถือ)
- เป็นบวกสำหรับ Short Options (เวลาทำงานให้ผู้เขียน)
- Theta สูงสุดสำหรับออปชัน ATM
- Theta เร่งตัวเมื่อใกล้หมดอายุ (การสลายตัวไม่เป็นเส้นตรง)
- ความสัมพันธ์ Theta-Gamma: $\Theta + \frac{1}{2}\sigma^2 S^2 \Gamma + rS\Delta = rV$

**เส้นโค้ง Theta Decay:**
- ที่ 60 DTE: Theta ปานกลาง ค่อนข้างคงที่วันต่อวัน
- ที่ 30 DTE: Theta เริ่มเร่งตัว
- ที่ 14 DTE: การเร่งตัวของ Theta เข้มข้นขึ้น
- ที่ 7 DTE: Theta Decay เร็วมากสำหรับออปชัน ATM
- ที่ 1 DTE: มูลค่าเวลาที่เหลือเกือบทั้งหมดหายไป

**ข้อพิจารณา Theta สำหรับคริปโต:**
- ตลาดคริปโตเทรด 24/7 ดังนั้น Theta สลายตัวต่อเนื่อง (ไม่มีวันหยุดสุดสัปดาห์)
- ไม่มี "Weekend Theta" Effect เหมือนออปชันหุ้น
- IV สูงหมายถึงค่า Theta สัมบูรณ์สูง
- ออปชันคริปโตที่ใกล้หมดอายุมี Theta รุนแรงเนื่องจาก IV สูง

#### 1.3.4 Vega (ν) — ความไวต่อความผันผวน

**นิยาม:** อัตราการเปลี่ยนแปลงของราคาออปชันเทียบกับ Implied Volatility

$$\nu = S_0 \sqrt{T} N'(d_1)$$

**คุณสมบัติ:**
- เป็นบวกเสมอสำหรับ Long Options
- สูงสุดสำหรับออปชัน ATM ที่มีเวลาเหลือมาก
- แสดงเป็นการเปลี่ยนแปลงของราคาออปชันต่อ 1% (1 Vol Point) ที่ IV เปลี่ยน
- Long Vega: กำไรเมื่อ IV เพิ่ม
- Short Vega: กำไรเมื่อ IV ลด

**Vega ในคริปโต:**
- BTC Vega มีขนาดใหญ่เนื่องจาก IV พื้นฐานสูง
- ตัวอย่าง: ออปชัน ATM BTC ที่ IV 60%, 30 DTE อาจมี Vega 0.002 BTC ต่อ Vol Point
- การเปลี่ยน IV 5 จุด = 0.01 BTC ต่อสัญญา = มีนัยสำคัญเมื่อ BTC อยู่ที่ $60K
- IV Crush หลังเหตุการณ์ (ETF Decisions, Halvings, FOMC) อาจทำลายสถานะ Long Vega
- IV Expansion ในช่วงไม่แน่นอนเป็นประโยชน์ต่อสถานะ Long Vega

#### 1.3.5 Rho (ρ) — ความไวต่ออัตราดอกเบี้ย

**นิยาม:** อัตราการเปลี่ยนแปลงของราคาออปชันเทียบกับอัตราดอกเบี้ยปลอดความเสี่ยง

$$\rho_{call} = KTe^{-rT}N(d_2)$$

$$\rho_{put} = -KTe^{-rT}N(-d_2)$$

**คุณสมบัติ:**
- เป็นบวกสำหรับ Calls เป็นลบสำหรับ Puts
- มีนัยสำคัญมากขึ้นสำหรับออปชันที่มีอายุยาว
- มีความสำคัญน้อยสำหรับคริปโต (อายุสั้น ความผันผวนสูงมีอิทธิพลมากกว่า)
- เกี่ยวข้องกับออปชัน FX ที่ส่วนต่างอัตราดอกเบี้ยมีความสำคัญ

#### 1.3.6 Greeks ลำดับสูง

**Vanna (∂Δ/∂σ = ∂ν/∂S):**

$$\text{Vanna} = \frac{\nu}{S}\left(1 - \frac{d_1}{\sigma\sqrt{T}}\right)$$

สำคัญสำหรับ: เข้าใจว่า Delta เปลี่ยนอย่างไรกับ IV (สำคัญสำหรับออปชันคริปโตที่ IV ผันผวน)

**Charm (∂Δ/∂t):**

$$\text{Charm} = -N'(d_1)\left(\frac{2(r-q)T - d_2\sigma\sqrt{T}}{2T\sigma\sqrt{T}}\right)$$

สำคัญสำหรับ: เข้าใจว่า Delta เปลี่ยนข้ามคืนอย่างไร; ส่งผลต่อความต้องการ Delta-hedge รายวัน

**Volga/Vomma (∂²V/∂σ²):**

$$\text{Volga} = \nu \cdot \frac{d_1 d_2}{\sigma}$$

สำคัญสำหรับ: เข้าใจ Convexity ของ Vega Exposure; สำคัญสำหรับการจัดการสถานะ Vega ขนาดใหญ่

---

## 1.4 รายการกลยุทธ์

### หมวด A: กลยุทธ์ตามทิศทาง (Directional Strategies)

---

#### A1. Long Call

**คำอธิบาย:** ซื้อ Call Option เพื่อทำกำไรจากการเคลื่อนไหวขาขึ้น

**การสร้างสถานะ:**
- ซื้อ 1 Call ที่ Strike $K$ ด้วยพรีเมียม $C$

**แผนภาพ Payoff:**
```
P&L
  │          ╱
  │         ╱
  │        ╱
  │       ╱
──┼──────●─────── Price
  │      K
  │
 -C ─────────────
  │
```

**สูตร:**
- **กำไรสูงสุด:** ไม่จำกัด = $S_T - K - C$ (เมื่อ $S_T \to \infty$)
- **ขาดทุนสูงสุด:** $C$ (พรีเมียมที่จ่าย)
- **จุดคุ้มทุน:** $S_{BE} = K + C$

**สภาวะตลาดที่เหมาะสม:**
- มีความเชื่อมั่นขาขึ้นแข็งแกร่ง
- สภาวะ IV ต่ำ (พรีเมียมถูก)
- IV Rank < 30 เป็นที่ต้องการ (ซื้อความผันผวนราคาถูก)
- คาดว่าจะเคลื่อนไหวมากกว่าพรีเมียมที่จ่าย

**โปรไฟล์ Greeks:**
| Greek | เครื่องหมาย | ขนาด | นัยยะ |
|---|---|---|---|
| Delta | + | 0 ถึง +1 | ได้ประโยชน์จากราคาเพิ่ม |
| Gamma | + | บวก | Delta เพิ่มเมื่อราคาขึ้น |
| Theta | - | ลบ | Time Decay ทำร้ายสถานะ |
| Vega | + | บวก | ได้ประโยชน์จาก IV เพิ่ม |

**กฎการเข้าสถานะ:**
1. IV Rank < 30 (ซื้อเมื่อ Vol ถูก)
2. สัญญาณขาขึ้นแข็งแกร่งจากการวิเคราะห์ทางเทคนิค/ปัจจัยพื้นฐาน
3. เลือก Strike ตาม Delta ที่ต้องการ:
   - ATM (Δ≈0.50): Gamma สูงสุด ความน่าจะเป็นของกำไรเทียบกับต้นทุนดีที่สุด
   - OTM เล็กน้อย (Δ≈0.30): พรีเมียมถูกกว่า ความน่าจะเป็นต่ำกว่า
   - ITM (Δ≈0.70): ต้นทุนสูงกว่า ความน่าจะเป็นสูงกว่า เลเวอเรจต่ำกว่า
4. เลือก Expiration: 30-60 DTE (สมดุลระหว่าง Theta Decay กับเวลาสำหรับวิทยานิพนธ์)

**กฎการออกจากสถานะ:**
1. เป้าหมายกำไร: 50-100% ผลตอบแทนบนพรีเมียม
2. Stop Loss: สูญเสีย 50% ของพรีเมียม
3. ออกตามเวลา: ปิดที่ 14 DTE ถ้ายังไม่ถึงเป้า (Theta เร่งตัว)
4. ออกจาก IV Crush: ปิดถ้า IV ลดลงอย่างมาก (ขาดทุน Vega เกินกำไรจากทิศทาง)
5. วิทยานิพนธ์ไม่ถูกต้อง: ปิดถ้าสัญญาณขาขึ้นกลับตัว

**พารามิเตอร์ความเสี่ยง:**
```
LONG_CALL_LIMITS:
  max_premium_per_trade: 2% of portfolio
  max_total_long_calls: 5% of portfolio in premium
  min_days_to_expiry: 21 DTE at entry
  max_days_to_expiry: 90 DTE
  preferred_delta_range: [0.30, 0.70]
  profit_target_pct: 50-100%
  stop_loss_pct: 50%
  time_exit_dte: 14
```

---

#### A2. Long Put

**คำอธิบาย:** ซื้อ Put Option เพื่อทำกำไรจากการเคลื่อนไหวขาลง

**การสร้างสถานะ:**
- ซื้อ 1 Put ที่ Strike $K$ ด้วยพรีเมียม $P$

**สูตร:**
- **กำไรสูงสุด:** $K - P$ (สินทรัพย์อ้างอิงไปเป็นศูนย์)
- **ขาดทุนสูงสุด:** $P$ (พรีเมียมที่จ่าย)
- **จุดคุ้มทุน:** $S_{BE} = K - P$

**สภาวะตลาดที่เหมาะสม:**
- มีความเชื่อมั่นขาลงแข็งแกร่ง
- สภาวะ IV ต่ำ (ซื้อถูก)
- IV Rank < 30
- คาดว่าจะมีการเคลื่อนไหวขาลงอย่างมีนัยสำคัญ

**พารามิเตอร์ความเสี่ยง:**
```
LONG_PUT_LIMITS:
  max_premium_per_trade: 2% of portfolio
  max_total_long_puts: 5% of portfolio in premium
  min_days_to_expiry: 21 DTE
  max_days_to_expiry: 90 DTE
  preferred_delta_range: [-0.70, -0.30]
  profit_target_pct: 50-100%
  stop_loss_pct: 50%
  time_exit_dte: 14
```

---

#### A3. Bull Call Spread (Debit Spread)

**คำอธิบาย:** ซื้อ Call ที่ Strike ต่ำ ขาย Call ที่ Strike สูง ลดต้นทุนแต่จำกัดกำไรขาขึ้น

**การสร้างสถานะ:**
- ซื้อ 1 Call ที่ Strike $K_1$ (ต่ำกว่า) จ่ายพรีเมียม $C_1$
- ขาย 1 Call ที่ Strike $K_2$ (สูงกว่า $K_2 > K_1$) รับพรีเมียม $C_2$
- Net Debit = $C_1 - C_2$

**สูตร:**
- **กำไรสูงสุด:** $(K_2 - K_1) - (C_1 - C_2)$ = ความกว้าง Spread - Net Debit
- **ขาดทุนสูงสุด:** $C_1 - C_2$ = Net Debit ที่จ่าย
- **จุดคุ้มทุน:** $S_{BE} = K_1 + (C_1 - C_2)$
- **อัตราส่วนความเสี่ยง/ผลตอบแทน:** Net Debit / (Width - Net Debit)

**พารามิเตอร์ความเสี่ยง:**
```
BULL_CALL_SPREAD_LIMITS:
  max_debit_per_trade: 2% of portfolio
  max_spread_width: 10% of underlying price
  min_reward_to_risk: 1.0
  min_days_to_expiry: 21 DTE
  max_days_to_expiry: 60 DTE
  profit_target_pct_of_max: 50-75%
  stop_loss_pct_of_debit: 50%
```

---

#### A4. Bear Put Spread (Debit Spread)

**คำอธิบาย:** ซื้อ Put ที่ Strike สูง ขาย Put ที่ Strike ต่ำ กลยุทธ์ขาลงที่กำหนดความเสี่ยง

**การสร้างสถานะ:**
- ซื้อ 1 Put ที่ Strike $K_2$ (สูงกว่า) จ่ายพรีเมียม $P_2$
- ขาย 1 Put ที่ Strike $K_1$ (ต่ำกว่า $K_1 < K_2$) รับพรีเมียม $P_1$
- Net Debit = $P_2 - P_1$

**สูตร:**
- **กำไรสูงสุด:** $(K_2 - K_1) - (P_2 - P_1)$ = Width - Net Debit
- **ขาดทุนสูงสุด:** $P_2 - P_1$ = Net Debit ที่จ่าย
- **จุดคุ้มทุน:** $S_{BE} = K_2 - (P_2 - P_1)$

---

### หมวด B: กลยุทธ์ Neutral / สร้างรายได้

---

#### B1. Short Straddle

**คำอธิบาย:** ขายทั้ง Call และ Put ที่ Strike เดียวกัน (ปกติ ATM) เก็บพรีเมียมสูงสุด ความเสี่ยงไม่จำกัด

**การสร้างสถานะ:**
- ขาย 1 ATM Call ที่ Strike $K$ รับพรีเมียม $C$
- ขาย 1 ATM Put ที่ Strike $K$ รับพรีเมียม $P$
- Total Credit = $C + P$

**สูตร:**
- **กำไรสูงสุด:** $C + P$ (ณ วันหมดอายุ $S_T = K$ พอดี)
- **ขาดทุนสูงสุด:** ไม่จำกัด (ขาขึ้น); $K - (C + P)$ ขาลง
- **จุดคุ้มทุน (บน):** $S_{BE,up} = K + C + P$
- **จุดคุ้มทุน (ล่าง):** $S_{BE,down} = K - (C + P)$

**พารามิเตอร์ความเสี่ยง:**
```
SHORT_STRADDLE_LIMITS:
  max_credit_per_trade: 3% of portfolio
  min_iv_rank: 50
  max_portfolio_short_gamma: defined by risk framework
  min_days_to_expiry: 25 DTE at entry
  max_days_to_expiry: 60 DTE
  profit_target_pct: 25-50% of credit
  stop_loss_multiple: 2x credit
  time_exit_dte: 21
  max_delta_drift: 0.20 before adjustment
  REQUIRES_MARGIN: true
  RISK_LEVEL: HIGH
```

---

#### B3. Iron Condor

**คำอธิบาย:** ขาย Strangle แล้วซื้อ Strangle ที่กว้างกว่าเพื่อป้องกัน กลยุทธ์ที่กำหนดความเสี่ยงของ Short Strangle

**การสร้างสถานะ:**
- ซื้อ 1 OTM Put ที่ Strike $K_1$ (ต่ำสุด) จ่าย $P_1$
- ขาย 1 OTM Put ที่ Strike $K_2$ ($K_2 > K_1$) รับ $P_2$
- ขาย 1 OTM Call ที่ Strike $K_3$ ($K_3 > K_2$) รับ $C_3$
- ซื้อ 1 OTM Call ที่ Strike $K_4$ (สูงสุด $K_4 > K_3$) จ่าย $C_4$
- Net Credit = $(P_2 + C_3) - (P_1 + C_4)$

**สูตร:**
- **กำไรสูงสุด:** Net Credit ที่ได้รับ
- **ขาดทุนสูงสุด:** ความกว้าง Spread ที่กว้างกว่า - Net Credit = $(K_2 - K_1) - \text{Net Credit}$ (สมมติความกว้างเท่ากัน)
- **จุดคุ้มทุน (บน):** $S_{BE,up} = K_3 + \text{Net Credit}$
- **จุดคุ้มทุน (ล่าง):** $S_{BE,down} = K_2 - \text{Net Credit}$

**พารามิเตอร์ความเสี่ยง:**
```
IRON_CONDOR_LIMITS:
  max_risk_per_trade: 3% of portfolio (max loss per condor)
  min_iv_rank: 30
  short_strike_delta: 0.16 each side
  wing_width: 1-3 strikes
  min_credit_to_width_ratio: 0.33
  min_days_to_expiry: 25 DTE
  profit_target_pct: 50% of credit
  stop_loss_multiple: 2x credit
  time_exit_dte: 21
  RISK_LEVEL: MODERATE
```

---

#### B5. Covered Call

**คำอธิบาย:** ถือสินทรัพย์อ้างอิง ขาย Call บนสถานะนั้น สร้างรายได้จากสถานะ Long ที่มีอยู่

**การสร้างสถานะ:**
- Long 1 หน่วยสินทรัพย์อ้างอิง
- ขาย 1 Call ที่ Strike $K$ ($K > S_0$) รับพรีเมียม $C$

**สูตร:**
- **กำไรสูงสุด:** $(K - S_0) + C$ (จำกัดที่ Strike)
- **ขาดทุนสูงสุด:** $S_0 - C$ (สินทรัพย์อ้างอิงไปศูนย์ หักด้วยพรีเมียม)
- **จุดคุ้มทุน:** $S_{BE} = S_0 - C$

**การใช้ Covered Call ในคริปโต:**
- ถือ BTC/ETH ใน Spot
- ขาย Calls บน Deribit
- ต้องโอนสินทรัพย์อ้างอิงไป Deribit เป็นหลักประกัน
- ทางเลือก: ใช้โปรโตคอล DOV (Ribbon, Friktion) สำหรับ Covered Call Vault อัตโนมัติ

**พารามิเตอร์ความเสี่ยง:**
```
COVERED_CALL_LIMITS:
  max_position_size: per standard position sizing
  strike_delta: 0.20-0.35 (OTM)
  min_annualized_yield: 15% (crypto), 5% (forex)
  min_days_to_expiry: 14 DTE
  max_days_to_expiry: 45 DTE
  roll_threshold: 75% of credit captured
  RISK_LEVEL: LOW-MODERATE (underlying still has downside)
```

---

#### B6. Cash-Secured Put

**คำอธิบาย:** ขาย Put โดยถือเงินสดเพื่อซื้อสินทรัพย์อ้างอิงหากถูก Assign สร้างรายได้หรือเข้าสถานะเชิงกลยุทธ์

**การสร้างสถานะ:**
- ขาย 1 Put ที่ Strike $K$ ($K \leq S_0$) รับพรีเมียม $P$
- ถือ $K$ เป็นเงินสด/Stablecoin เป็นหลักประกัน

**สูตร:**
- **กำไรสูงสุด:** $P$ (พรีเมียมที่ได้รับ)
- **ขาดทุนสูงสุด:** $K - P$ (สินทรัพย์อ้างอิงไปเป็นศูนย์)
- **จุดคุ้มทุน:** $S_{BE} = K - P$
- **ผลตอบแทนบนเงินทุน:** $P / K$ ต่อรอบ

---

### หมวด C: กลยุทธ์ความผันผวน (Volatility Strategies)

---

#### C1. Long Straddle

**คำอธิบาย:** ซื้อทั้ง Call และ Put ที่ Strike เดียวกัน (ATM) ทำกำไรจากการเคลื่อนไหวขนาดใหญ่ทั้งสองทิศทาง

**การสร้างสถานะ:**
- ซื้อ 1 ATM Call ที่ Strike $K$ จ่าย $C$
- ซื้อ 1 ATM Put ที่ Strike $K$ จ่าย $P$
- Total Debit = $C + P$

**สูตร:**
- **กำไรสูงสุด:** ไม่จำกัด (ทั้งสองทิศทาง)
- **ขาดทุนสูงสุด:** $C + P$ (ณ วันหมดอายุ $S_T = K$)
- **จุดคุ้มทุน (บน):** $K + C + P$
- **จุดคุ้มทุน (ล่าง):** $K - (C + P)$
- **การเคลื่อนไหวที่ต้องการเพื่อคุ้มทุน:** $\pm(C + P) / S_0$ เป็นเปอร์เซ็นต์

---

### หมวด D: กลยุทธ์ป้องกันความเสี่ยง (Hedging Strategies)

---

#### D1. Protective Put

**คำอธิบาย:** ซื้อ Put เพื่อป้องกันสถานะ Long ที่มีอยู่ ทำหน้าที่เป็นประกันป้องกันขาลง

**การสร้างสถานะ:**
- Long 1 หน่วยสินทรัพย์อ้างอิง (สถานะที่มีอยู่)
- ซื้อ 1 Put ที่ Strike $K$ ($K \leq S_0$) จ่าย $P$

**สูตร:**
- **กำไรสูงสุด:** ไม่จำกัด (กำไรขาขึ้นของสินทรัพย์อ้างอิง หักพรีเมียม)
- **ขาดทุนสูงสุด:** $(S_0 - K) + P$ (สินทรัพย์อ้างอิงตกถึง/ต่ำกว่า Strike)
- **จุดคุ้มทุน:** $S_{BE} = S_0 + P$
- **ป้องกันขาลงต่ำกว่า:** $K$
- **ต้นทุนประกัน:** $P / S_0$ เป็นเปอร์เซ็นต์

---

#### D2. Collar

**คำอธิบาย:** Long สินทรัพย์อ้างอิง + Protective Put + Covered Call สุทธิเป็นศูนย์หรือต้นทุนต่ำในการป้องกันขาลง

**การสร้างสถานะ:**
- Long 1 หน่วยสินทรัพย์อ้างอิง
- ซื้อ 1 OTM Put ที่ Strike $K_1$ ($K_1 < S_0$) จ่าย $P$
- ขาย 1 OTM Call ที่ Strike $K_2$ ($K_2 > S_0$) รับ $C$
- Net Cost = $P - C$ (สามารถเป็น Zero-cost ถ้า $P = C$)

**สูตร:**
- **กำไรสูงสุด:** $(K_2 - S_0) - (P - C)$
- **ขาดทุนสูงสุด:** $(S_0 - K_1) + (P - C)$
- **จุดคุ้มทุน:** $S_0 + (P - C)$ (สำหรับ Zero-cost Collar จุดคุ้มทุน = $S_0$)

---

## 1.5 การวิเคราะห์ Implied Volatility

### 1.5.1 IV Rank

$$IV_{Rank} = \frac{IV_{current} - IV_{52w,low}}{IV_{52w,high} - IV_{52w,low}} \times 100$$

- วัดว่า IV ปัจจุบันอยู่ตรงไหนเทียบกับช่วง 52 สัปดาห์
- IV Rank > 50: IV สูงเทียบกับประวัติ → ชอบกลยุทธ์ขาย
- IV Rank < 30: IV ต่ำเทียบกับประวัติ → ชอบกลยุทธ์ซื้อ

### 1.5.2 IV Percentile

$$IV_{Percentile} = \frac{\text{จำนวนวันที่ IV ต่ำกว่า IV ปัจจุบัน}}{\text{จำนวนวันเทรดทั้งหมดใน Lookback}} \times 100$$

- วัดว่าวันกี่เปอร์เซ็นต์มี IV ต่ำกว่า
- แข็งแกร่งกว่า IV Rank (ไม่ได้รับผลกระทบจากวันที่เป็น Outlier เดียว)
- โดยทั่วไปเป็นที่ต้องการสำหรับการเลือกกลยุทธ์

### 1.5.3 การเลือกกลยุทธ์ตามสภาวะ IV

| IV Rank | IV Percentile | กลยุทธ์ที่แนะนำ |
|---|---|---|
| 0-20 | 0-20 | Long Straddle, Long Strangle, Calendar Buy |
| 20-40 | 20-40 | Bull/Bear Spreads, Long Options |
| 40-60 | 40-60 | Iron Condor, Calendar Spread |
| 60-80 | 60-80 | Short Strangle, Iron Butterfly, Covered Call |
| 80-100 | 80-100 | Short Straddle, Short Strangle, CSP, DOV |

---

## 2. ข้อกำหนดทางเทคนิค

### 2.1 ท่อส่งข้อมูลออปชัน (Options Data Pipeline)

```
OPTIONS_DATA_PIPELINE:

  INPUT_DATA:
    - Spot price (real-time, multiple sources)
    - Option chain: all strikes × all expiries
    - Bid/ask for each option
    - Open interest per strike/expiry
    - Volume per strike/expiry
    - Exchange-reported Greeks (Deribit provides mark IV)
    - Historical options data (for backtesting)
    - Events calendar

  PROCESSING:
    1. Data normalization:
       - Convert prices to common denomination (USD or BTC)
       - Synchronize timestamps across exchanges
       - Handle missing data (interpolation)

    2. IV Surface Construction:
       - Extract IV from market prices (Newton-Raphson)
       - Fit smooth surface: SABR or SVI parameterization
       - Detect arbitrage violations (butterfly, calendar spread)
       - Store IV surface as grid: [strike_moneyness × time_to_expiry]

    3. Greeks Calculation:
       - Compute all Greeks from IV surface + BSM
       - Aggregate to position level
       - Aggregate to portfolio level
       - Store time series for attribution

    4. Signal Generation:
       - IV Rank/Percentile computation
       - Skew analysis
       - Term structure analysis
       - Unusual activity detection (volume/OI spikes)
       - Greeks-based opportunity identification

  OUTPUT:
    - Real-time IV surface
    - Position and portfolio Greeks
    - Strategy signals with confidence scores
    - Risk alerts
```

### 2.2 เอนจิ้นดำเนินการกลยุทธ์ออปชัน

```
OPTIONS_EXECUTION_ENGINE:

  ORDER_TYPES:
    single_leg:
      - limit_order: Standard limit
      - market_order: Immediate fill (avoid for options — wide spreads)
      - stop_order: Trigger-based
      - trailing_stop: Dynamic stop

    multi_leg:
      - spread_order: Submit as package (exchange-native if available)
      - leg_by_leg: Execute one leg at a time (legging risk)
      - ratio_order: Unequal leg quantities

  EXECUTION_LOGIC:
    1. Receive strategy signal
    2. Validate against risk limits
    3. Check liquidity:
       - Bid-ask spread < threshold (varies by instrument)
       - Order book depth sufficient for position size
       - Impact cost estimation
    4. Construct order:
       - Multi-leg: Use exchange combo orders when available
       - Single-leg: Use limit orders with smart pricing
    5. Submit order:
       - Start at mid-price
       - Walk toward aggressive side over time
       - Maximum time-to-fill: 60 seconds
       - Cancel and reassess if not filled
    6. Confirmation:
       - All legs filled
       - Actual vs expected fill prices
       - Slippage recording
    7. Position booking:
       - Update position database
       - Recalculate portfolio Greeks
       - Set profit target and stop loss orders
```

---

## 3. แบบจำลองทางคณิตศาสตร์

### 3.1 Black-Scholes-Merton — การอนุพันธ์สมบูรณ์

เริ่มจาก Geometric Brownian Motion:

$$dS = \mu S \, dt + \sigma S \, dW$$

ใช้ Ito's Lemma กับอนุพันธ์ $V(S,t)$:

$$dV = \left(\frac{\partial V}{\partial t} + \mu S \frac{\partial V}{\partial S} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 V}{\partial S^2}\right)dt + \sigma S \frac{\partial V}{\partial S} dW$$

สร้างพอร์ตปลอดความเสี่ยง $\Pi = V - \Delta S$ โดยที่ $\Delta = \frac{\partial V}{\partial S}$:

$$d\Pi = \left(\frac{\partial V}{\partial t} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 V}{\partial S^2}\right)dt$$

โดย No-Arbitrage: $d\Pi = r\Pi \, dt$:

$$\frac{\partial V}{\partial t} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 V}{\partial S^2} + rS\frac{\partial V}{\partial S} - rV = 0$$

นี่คือ **Black-Scholes PDE** โดยมีเงื่อนไขขอบเขตสำหรับ European Call:
- $V(S,T) = \max(S-K, 0)$ ณ วันหมดอายุ
- $V(0,t) = 0$ เมื่อ $S \to 0$
- $V(S,t) \to S$ เมื่อ $S \to \infty$

### 3.2 Greeks — สูตรคณิตศาสตร์สมบูรณ์

**Standard Normal PDF:**

$$n(x) = N'(x) = \frac{1}{\sqrt{2\pi}}e^{-x^2/2}$$

**Delta:**

$$\Delta_C = N(d_1), \quad \Delta_P = N(d_1) - 1$$

**Gamma (เหมือนกันสำหรับ Calls และ Puts):**

$$\Gamma = \frac{n(d_1)}{S\sigma\sqrt{T}}$$

**Theta:**

$$\Theta_C = -\frac{S \cdot n(d_1) \cdot \sigma}{2\sqrt{T}} - rKe^{-rT}N(d_2)$$

$$\Theta_P = -\frac{S \cdot n(d_1) \cdot \sigma}{2\sqrt{T}} + rKe^{-rT}N(-d_2)$$

**Vega (เหมือนกันสำหรับ Calls และ Puts):**

$$\nu = S\sqrt{T} \cdot n(d_1)$$

**Vanna:**

$$\text{Vanna} = -\frac{n(d_1) \cdot d_2}{\sigma}$$

**Vomma/Volga:**

$$\text{Vomma} = \nu \cdot \frac{d_1 \cdot d_2}{\sigma}$$

### 3.3 การคำนวณ Implied Volatility

**วิธี Newton-Raphson:**

เพื่อหา $\sigma_{imp}$ ที่ทำให้ $BSM(\sigma_{imp}) = C_{market}$:

$$\sigma_{n+1} = \sigma_n - \frac{BSM(\sigma_n) - C_{market}}{\text{Vega}(\sigma_n)}$$

**เกณฑ์การลู่เข้า:** $|BSM(\sigma_n) - C_{market}| < 10^{-8}$

**ค่าเริ่มต้น:** Brenner-Subrahmanyam Approximation:

$$\sigma_0 \approx \sqrt{\frac{2\pi}{T}} \cdot \frac{C_{market}}{S}$$

### 3.4 Stochastic Volatility — แบบจำลอง Heston

$$dS_t = \mu S_t \, dt + \sqrt{v_t} S_t \, dW_t^S$$

$$dv_t = \kappa(\theta - v_t) \, dt + \xi \sqrt{v_t} \, dW_t^v$$

$$\text{Corr}(dW_t^S, dW_t^v) = \rho$$

โดยที่:
- $v_t$ = ความแปรปรวนขณะนั้น (Instantaneous Variance)
- $\kappa$ = ความเร็ว Mean Reversion
- $\theta$ = ความแปรปรวนระยะยาว (Long-term Variance)
- $\xi$ = Vol of Vol
- $\rho$ = สหสัมพันธ์ระหว่าง Spot กับ Vol (ปกติเป็นลบ: "Leverage Effect")

**เงื่อนไข Feller (รับประกัน $v_t > 0$):**

$$2\kappa\theta > \xi^2$$

---

## 4. พารามิเตอร์ความเสี่ยง

### 4.1 เมทริกซ์ความเสี่ยงระดับกลยุทธ์

```
STRATEGY_RISK_MATRIX:

  LONG_CALL:
    max_loss: Premium paid (100%)
    max_profit: Unlimited
    margin_required: Premium only
    complexity: Low
    risk_score: 3/10

  SHORT_STRADDLE:
    max_loss: UNLIMITED
    max_profit: Total premium
    margin_required: HIGH (naked)
    complexity: High
    risk_score: 9/10

  IRON_CONDOR:
    max_loss: Width - Credit
    max_profit: Net credit
    margin_required: Width of wider spread
    complexity: Moderate
    risk_score: 5/10

  COVERED_CALL:
    max_loss: S0 - Premium (underlying risk)
    max_profit: (K - S0) + Premium
    margin_required: Underlying purchase
    complexity: Low
    risk_score: 4/10

  PROTECTIVE_PUT:
    max_loss: (S0 - K) + Premium
    max_profit: Unlimited (minus premium)
    margin_required: Premium only
    complexity: Low
    risk_score: 2/10
```

### 4.2 ขีดจำกัดความเสี่ยงออปชันระดับพอร์ต

```
PORTFOLIO_OPTIONS_RISK:

  aggregate_limits:
    max_total_premium_at_risk: 10% of portfolio
    max_short_gamma_dollars: 2% of portfolio per 1% move
    max_portfolio_vega: 1% of portfolio per vol point
    max_portfolio_theta: -0.3% daily (long options)
    max_portfolio_theta: +0.5% daily (short options)
    max_single_underlying_delta: 15% of portfolio
    max_total_delta: 30% of portfolio

  concentration_limits:
    max_single_expiry_exposure: 30% of options portfolio
    max_single_strike_exposure: 20% of options portfolio
    max_notional_per_underlying: 20% of portfolio

  liquidity_limits:
    max_position_vs_OI: 2% of open interest at any strike
    min_bid_ask_spread: < 5% of mid price
    min_daily_volume: 10x position size
```

---

## 5. ขั้นตอนการดำเนินการ

### 5.1 บอทเทรดออปชัน — อัลกอริทึมดำเนินการสมบูรณ์

```
OPTIONS_TRADING_BOT_FLOW:

  ╔══════════════════════════════════════════════════════════╗
  ║  STEP 1: DATA COLLECTION (every 1 second)               ║
  ╠══════════════════════════════════════════════════════════╣
  ║  1.1 Fetch spot price from 3+ sources                   ║
  ║  1.2 Fetch full option chain (all strikes × expiries)   ║
  ║  1.3 Compute IV for each option (Newton-Raphson)        ║
  ║  1.4 Build IV surface (SABR/SVI parameterization)       ║
  ║  1.5 Compute IV Rank and IV Percentile                  ║
  ║  1.6 Compute term structure slope                       ║
  ║  1.7 Compute skew (25Δ risk reversal, butterfly)        ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 2: SIGNAL GENERATION (every 5 seconds)            ║
  ╠══════════════════════════════════════════════════════════╣
  ║  2.1 Determine market regime                            ║
  ║  2.2 IV environment assessment                          ║
  ║  2.3 Skew assessment                                    ║
  ║  2.4 Term structure assessment                          ║
  ║  2.5 Unusual activity scan                              ║
  ║  2.6 Generate candidate strategies with scores          ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 3: STRATEGY SELECTION (on signal)                  ║
  ╠══════════════════════════════════════════════════════════╣
  ║  3.1 Rank candidates by expected Sharpe ratio            ║
  ║  3.2 Filter by risk constraints                         ║
  ║  3.3 Select top strategy                                ║
  ║  3.4 Determine optimal strikes and expiry               ║
  ║  3.5 Position sizing (Kelly / Fixed Fractional)         ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 4: PRE-TRADE RISK CHECK                           ║
  ╠══════════════════════════════════════════════════════════╣
  ║  4.1 Calculate new portfolio Greeks after trade          ║
  ║  4.2 Verify all limits satisfied                        ║
  ║  4.3 Stress test: What if spot moves ±10%?             ║
  ║  4.4 Approve or reject                                  ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 5: ORDER EXECUTION                                ║
  ╠══════════════════════════════════════════════════════════╣
  ║  5.1 Check liquidity at target strikes                  ║
  ║  5.2 Construct order(s)                                 ║
  ║  5.3 Submit limit order at mid-price                    ║
  ║  5.4-5.6 Walk price toward aggressive over 60s         ║
  ║  5.7 Confirm all legs filled                            ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 6: POSITION MONITORING (continuous)               ║
  ╠══════════════════════════════════════════════════════════╣
  ║  6.1 Real-time P&L tracking                             ║
  ║  6.2 Greeks monitoring (every 100ms)                    ║
  ║  6.3 Profit target monitoring                           ║
  ║  6.4 Stop loss monitoring                               ║
  ║  6.5 Time-based exit                                    ║
  ║  6.6 Adjustment triggers                                ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 7: EXIT EXECUTION                                 ║
  ╠══════════════════════════════════════════════════════════╣
  ║  7.1-7.7 Close, verify, update, record                 ║
  ╠══════════════════════════════════════════════════════════╣
  ║  STEP 8: POST-TRADE ANALYSIS                            ║
  ╠══════════════════════════════════════════════════════════╣
  ║  8.1 Compare actual vs expected P&L                     ║
  ║  8.2 Decompose P&L by Greek:                            ║
  ║      - Delta P&L: Δ × ΔS                               ║
  ║      - Gamma P&L: ½ × Γ × (ΔS)²                       ║
  ║      - Theta P&L: Θ × Δt                               ║
  ║      - Vega P&L: ν × Δσ                                ║
  ║  8.3 Execution quality analysis                         ║
  ║  8.4 Update strategy statistics                         ║
  ║  8.5 Feed results to ML optimizer                       ║
  ╚══════════════════════════════════════════════════════════╝
```

---

## 6. เอกสารอ้างอิง

### วรรณกรรมวิชาการ

1. **Black, F., & Scholes, M.** (1973). "The Pricing of Options and Corporate Liabilities." *Journal of Political Economy*, 81(3), 637-654.
2. **Merton, R.C.** (1973). "Theory of Rational Option Pricing." *Bell Journal of Economics and Management Science*, 4(1), 141-183.
3. **Cox, J.C., Ross, S.A., & Rubinstein, M.** (1979). "Option Pricing: A Simplified Approach." *Journal of Financial Economics*, 7(3), 229-263.
4. **Heston, S.L.** (1993). "A Closed-Form Solution for Options with Stochastic Volatility." *Review of Financial Studies*, 6(2), 327-343.
5. **Gatheral, J.** (2006). *The Volatility Surface: A Practitioner's Guide*. Wiley.
6. **Jaeckel, P.** (2017). "Let's Be Rational." *Wilmott Magazine*, January 2017.

### ตำราเรียน

7. **Hull, J.C.** (2022). *Options, Futures, and Other Derivatives* (11th Edition). Pearson.
8. **Natenberg, S.** (2015). *Option Volatility and Pricing* (2nd Edition). McGraw-Hill.
9. **Taleb, N.N.** (1997). *Dynamic Hedging: Managing Vanilla and Exotic Options*. Wiley.
10. **Sinclair, E.** (2013). *Volatility Trading* (2nd Edition). Wiley.
11. **McMillan, L.G.** (2012). *Options as a Strategic Investment* (5th Edition). Prentice Hall.

### แหล่งข้อมูลเฉพาะคริปโต

12. **Deribit Knowledge Base** — ข้อกำหนดออปชัน การชำระบัญชี มาร์จิ้น. https://www.deribit.com/kb
13. **Paradigm Protocol** — การเทรดออปชันคริปโตแบบ Block ระดับสถาบัน
14. **Amberdata Derivatives** — ข้อมูล Volatility Surface คริปโต
15. **Laevitas Analytics** — การเฝ้าติดตาม Options Flow, Greeks และ OI แบบเรียลไทม์

### เอกสารอ้างอิงการใช้งาน

16. **QuantLib** — ไลบรารี Quantitative Finance แบบ Open-source. https://www.quantlib.org
17. **Vollib** — ไลบรารี Python สำหรับการกำหนดราคาออปชันและ Greeks.
18. **Deribit API v2** — เอกสาร REST และ WebSocket API.

---

> **หมายเหตุสำหรับ AI Agents:** เอกสารนี้เป็นแค็ตตาล็อกกลยุทธ์ออปชันที่สมบูรณ์สำหรับระบบเทรด
> กลยุทธ์ทั้งหมดต้องถูกกรองผ่านกรอบการจัดการความเสี่ยง (เอกสาร 05) ก่อนดำเนินการ
> IV Rank/Percentile เป็นตัวกรองหลักสำหรับการเลือกกลยุทธ์
> การกำหนดขนาดสถานะต้องใช้ Kelly Criterion พร้อมการปรับแบบ Fractional
> Delta Hedging จำเป็นสำหรับสถานะ Short Options ทั้งหมดที่เกินเกณฑ์ที่กำหนด
> กลยุทธ์หลายขาควรใช้คำสั่ง Combo ของตลาดเมื่อมีเพื่อลดความเสี่ยง Leg
