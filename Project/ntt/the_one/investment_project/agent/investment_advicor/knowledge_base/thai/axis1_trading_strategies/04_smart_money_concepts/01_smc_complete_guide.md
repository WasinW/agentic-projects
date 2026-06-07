# Smart Money Concepts (SMC) — คู่มือการเทรดฉบับสมบูรณ์

## ข้อมูลเอกสาร
| ฟิลด์ | ค่า |
|---|---|
| **Strategy ID** | SMC-001 |
| **หมวดหมู่** | Institutional Order Flow / Smart Money |
| **สินทรัพย์** | Forex, Crypto, ดัชนี |
| **ไทม์เฟรม** | M15 ถึง Weekly (หลัก: H1–H4) |
| **ความซับซ้อน** | ขั้นสูง |
| **ความเหมาะสมกับ AI** | สูง — การระบุโครงสร้างเป็นระบบตามกฎ |
| **เวอร์ชัน** | 2.0 |
| **อัปเดตล่าสุด** | 2026-04-12 |

---

## สารบัญ
1. [บทนำและปรัชญา](#1-บทนำและปรัชญา)
2. [โครงสร้างตลาด](#2-โครงสร้างตลาด)
3. [Order Blocks (OB)](#3-order-blocks-ob)
4. [Breaker Blocks](#4-breaker-blocks)
5. [Mitigation Blocks](#5-mitigation-blocks)
6. [Institutional Order Flow Entry Drill (IOFED)](#6-institutional-order-flow-entry-drill-iofed)
7. [โซนพรีเมียมและดิสเคาท์](#7-โซนพรีเมียมและดิสเคาท์)
8. [จุดสมดุล](#8-จุดสมดุล)
9. [Kill Zones](#9-kill-zones)
10. [Fair Value Gaps (FVG)](#10-fair-value-gaps-fvg)
11. [แนวคิดเรื่องสภาพคล่อง](#11-แนวคิดเรื่องสภาพคล่อง)
12. [โมเดลการเข้าเทรด](#12-โมเดลการเข้าเทรด)
13. [โมเดลทางคณิตศาสตร์](#13-โมเดลทางคณิตศาสตร์)
14. [พารามิเตอร์ความเสี่ยง](#14-พารามิเตอร์ความเสี่ยง)
15. [ขั้นตอนการดำเนินการทั้งหมด](#15-ขั้นตอนการดำเนินการทั้งหมด)
16. [หมายเหตุการใช้งาน AI](#16-หมายเหตุการใช้งาน-ai)
17. [เอกสารอ้างอิง](#17-เอกสารอ้างอิง)

---

## 1. บทนำและปรัชญา

Smart Money Concepts (SMC) เป็นระเบียบวิธีการเทรดที่สร้างขึ้นบนสมมติฐานว่าตลาดการเงินถูกบังคับทิศทางโดยผู้เล่นสถาบันขนาดใหญ่ — ธนาคาร, กองทุนเฮดจ์ฟันด์ และธนาคารกลาง — ซึ่งเรียกรวมว่า "เงินฉลาด" (Smart Money) กรอบแนวคิดนี้วิเคราะห์ย้อนกลับพฤติกรรมสถาบันจากราคาเพียงอย่างเดียว โดยไม่พึ่งพาอินดิเคเตอร์แบบล้าหลัง

### 1.1 ทฤษฎีหลัก

ตลาดไม่ได้เคลื่อนไหวแบบสุ่ม ผู้เล่นสถาบันต้องการ:
1. **สภาพคล่อง (Liquidity)** เพื่อเติมออเดอร์ขนาดใหญ่โดยไม่เกิดสลิปเพจมากเกินไป
2. **ความไม่สมดุล (Imbalance)** หรือ Fair Value Gaps เป็นหลักฐานของกิจกรรมสถาบันแบบก้าวร้าว
3. **Displacement** — การเคลื่อนไหวรุนแรงในทิศทาง��ดียว บ่งบอกถึงการผูกมัดของเงินฉลาด

### 1.2 หลักการสำคัญ

- ราคาจะวิ่งหาสภาพคล่องก่อนจะเคลื่อนไหวจริง
- จุดสูงเท่ากัน/จุดต่ำเท่ากัน (Equal Highs/Lows) คือเป้���หมายสภาพคล่อง ไม่ใช่แนวรับแนวต้าน
- นักเทรดสถาบันสะสมตำแหน่ง���นช่วงสะสม (Range) และกระจายที่จุดสุดขั้ว
- การเคลื่อนไหว "จริง" เริ่มหลังจากที่นักเทรดรายย่อยถูก Stop Out ไปแล้ว

### 1.3 ความสัมพันธ์กับกรอบแนวคิดอื่น

SMC สังเคราะห์แนวคิดจาก:
- **Wyckoff Method** — การสะสม/กระจาย, Composite Operator
- **ICT (Inner Circle Trader)** — Order Blocks, Kill Zones, Optimal Trade Entry
- **Auction Market Theory** — มูลค่ายุติธรรม, ความไม่สมดุล

---

## 2. โครงสร้างตลาด (Market Structure)

โครงสร้างตลาดเป็นชั้นพื้นฐานของการวิเคราะห์ SMC กำหนดทิศทา��แนวโน้มที่การตัดสินใจทั้งหมดขึ้นอยู่กับ

### 2.1 จุดสวิง (Swing Points)

**จุดสวิงไฮ (Swing High)** คือจุดสูงสุดของแท่งเทียนที่สูงกว่าจุดสูงของแท่งเทียนด้านซ้ายและขวา

**จุดสวิงโลว์ (Swing Low)** คือจุดต่ำสุดของแท่งเทียนที่ต่ำกว่าจุดต่ำของแท่งเทียนด้านซ้ายและขวา

สำหรับกา���ใช้งาน���ชิงอัลกอริทึม ใช้พารามิเตอร์ lookback `n` ที่ปรับได้:

$$\text{SwingHigh}_i = \begin{cases} \text{True} & \text{if } H_i > \max(H_{i-n}, \ldots, H_{i-1}) \text{ and } H_i > \max(H_{i+1}, \ldots, H_{i+n}) \\ \text{False} & \text{otherwise} \end{cases}$$

$$\text{SwingLow}_i = \begin{cases} \text{True} & \text{if } L_i < \min(L_{i-n}, \ldots, L_{i-1}) \text{ and } L_i < \min(L_{i+1}, \ldots, L_{i+n}) \\ \text{False} & \text{otherwise} \end{cases}$$

ค่า `n` ที่แนะนำ:
| ไทม์เฟรม | n (แท่งเทียน) |
|-----------|-------------|
| M5–M15 | 3–5 |
| H1 | 5–7 |
| H4 | 5–10 |
| Daily | 3–5 |

### 2.2 โครงสร้างตลาดขาขึ้น (Bullish Market Structure)

- ราคาสร้าง **จุดสูงที่สูงขึ้น (Higher Highs - HH)** และ **จุดต่ำที่สูงขึ้น (Higher Lows - HL)**
- ทุกจุดสวิงไฮใหม่สูงกว่าจุดสวิงไฮก่อนหน้า
- ทุกจุดสวิงโลว์ใหม่อยู่เหนือจุดสวิงโลว์ก่อนหน้า

### 2.3 โครงสร้างตลาดขาลง (Bearish Market Structure)

- ราคาสร้าง **จุดต่ำที่ต่ำลง (Lower Lows - LL)** และ **จุดสูงที่ต่ำลง (Lower Highs - LH)**
- ทุกจุดสวิงโลว์ใหม่ทะลุต่ำกว่าจุดสวิงโลว์ก่อนหน้า
- ทุกจุดสวิงไฮใหม่ไม่สามารถทะลุจุดสวิงไฮก่อนหน้าได้

### 2.4 Break of Structure (BOS)

BOS ยื��ยันการต่อเนื่องของเทรนด์:
- **Bullish BOS**: ราคาปิดเหนือจุดสวิงไฮก่อนหน้า
- **Bearish BOS**: ราคาปิดต่ำกว่าจุดสวิงโลว์ก่อนหน้า

เงื่อนไข (ขาขึ้น):
$$\text{BullishBOS} = C_{\text{current}} > H_{\text{previous\_swing\_high}}$$

### 2.5 Change of Character (CHoCH)

CHoCH ส่งสัญญาณการกลับตัวของเทรนด์:
- ในขาขึ้น ราคาทะลุต่ำกว่า **Higher Low** ล่าสุด → CHoCH ขาลง
- ในขาลง ราคาทะลุเหนือ **Lower High** ล่าสุด → CHoCH ขาขึ้น

$$\text{BearishCHoCH} = C_{\text{current}} < L_{\text{most\_recent\_HL}} \quad \text{(ในเทรนด์ขาขึ้น)}$$

### 2.6 โครงสร้างภายในกับโครงสร้างภายนอก (Internal vs. External Structure)

- **โครงสร้างภายนอก (External)**: จุดสวิงของไทม์เฟรมใหญ่ (H4, Daily)
- **โครงสร้างภายใน (Internal)**: จุดสวิงของไทม์เฟรมเล็ก (M15, H1) ภายในขาของโครงสร้างภายนอก

การทะลุโครงสร้างภายในไม่ได้ทำให้โครงสร้างภายนอกเป็นโมฆะ AI agent ควรติดตามทั้งสองชั้นพร้อมกัน

---

## 3. Order Blocks (OB)

Order Blocks คือร่องรอยของการวางออเดอร์สถาบัน เป็นแท่งเทียนฝั่งตรงข้ามสุดท้าย (หรือกลุ่มแท่งเทียน) ก่อนการเคลื่อนไหว Displacement ที่รุนแรง

### 3.1 Bullish Order Block

**นิยาม**: แท่งเทียนขาลงสุดท้าย (หรือชุดแท่งเทียนขาลงต่อเนื่อง) ก่อนการเคลื่อนไหว Displacement ขาขึ้นที่รุนแรงซึ่งสร้าง Break of Structure

**อัลกอริทึมการระบุ**:
1. ระบุ Bullish BOS (ราคาปิดเหนือจุดสวิงไฮก่อนหน้า)
2. ย้อนกลับไปที่ขาอิมพัลส์ที่ทำให้เกิด BOS
3. หาแท่งเทียนขาลงสุดท้ายก่อนที่ขาอิมพัลส์จะเริ่ม
4. ช่วงของแท่งเทียนนั้น (เปิดถึงต่ำ) กำหนดโซน Bullish OB

**การกำหนดโซน**:
$$\text{BullishOB}_{\text{upper}} = O_{\text{last\_bearish\_candle}}$$
$$\text{BullishOB}_{\text{lower}} = L_{\text{last\_bearish\_candle}}$$

**โซนปรับละเอียด** (สำหรับจุดเข้าที่แคบขึ้น):
$$\text{BullishOB}_{\text{refined\_upper}} = C_{\text{last\_bearish\_candle}}$$
$$\text{BullishOB}_{\text{refined\_lower}} = L_{\text{last\_bearish\_candle}}$$

### 3.2 Bearish Order Block

**นิยาม**: แท่งเทียนขาขึ้นสุดท้าย (หรือชุดแท่งเทียนขาขึ้นต่อเนื่อง) ก่อนการเคลื่อนไหว Displacement ขาลงที่รุนแรงซึ่งสร้าง Break of Structure

**การกำหนดโซน**:
$$\text{BearishOB}_{\text{upper}} = H_{\text{last\_bullish\_candle}}$$
$$\text{BearishOB}_{\text{lower}} = O_{\text{last\_bullish\_candle}}$$

**โซนปรับละเอียด**:
$$\text{BearishOB}_{\text{upper}} = H_{\text{last\_bullish\_candle}}$$
$$\text{BearishOB}_{\text{refined\_lower}} = C_{\text{last\_bullish\_candle}}$$

### 3.3 เกณฑ์ความถูกต้องของ Order Block

OB ถือว่าถูกต้องเมื่อ:

1. **มี Displacement**: การเคลื่อนไหวออกจาก OB ต้องเป็นแบบอิมพัลซีฟ (แท่งเทียนตัวใหญ่ ไส้เทียนน้อย)
   $$\text{Displacement Ratio} = \frac{|C - O|}{\text{ATR}(14)} \geq 1.5$$

2. **สร้าง Imbalance (FVG)**: Displacement ควรทิ้ง Fair Value Gap ไว้

3. **เกิด BOS**: อิมพั��ส์จาก OB ต้องทะลุจุดสวิงก่อนหน้า

4. **ยังไม่ถูก Mitigate**: ราคายังไม่ได้กลับมาทดสอบโซน OB

### 3.4 การให้คะแนนความแข็งแกร่งของ Order Block

$$\text{OB\_Score} = w_1 \cdot S_{\text{displacement}} + w_2 \cdot S_{\text{FVG}} + w_3 \cdot S_{\text{freshness}} + w_4 \cdot S_{\text{HTF\_alignment}}$$

โดยที่:
- $S_{\text{displacement}} = \min\left(\frac{|\text{displacement move}|}{2 \times \text{ATR}(14)}, 1.0\right)$
- $S_{\text{FVG}} \in \{0, 0.5, 1.0\}$ — ไม่มี FVG, FVG บางส่วน, FVG เต็ม
- $S_{\text{freshness}} = e^{-\lambda \cdot t}$ โดย $t$ = แท่งเทียนนับจากเกิด, $\lambda = 0.01$
- $S_{\text{HTF\_alignment}} \in \{0, 1\}$ — 1 ถ้าเทรนด์ HTF สอดค��้อง

น้ำหนักเริ่มต้น: $w_1 = 0.35, w_2 = 0.25, w_3 = 0.20, w_4 = 0.20$

**เกณฑ์ขั้นต่ำ**: $\text{OB\_Score} \geq 0.60$ สำหรับก��รพิจารณาเทรด

---

## 4. Breaker Blocks

Breaker Block เกิดขึ้นเมื่อ Order Block ก่อนหน้าถูก **ละเมิด** (ราคาวิ่งทะลุ) ���ล้วราคากลับตัว OB ที่ถูกละเมิดจะ "กลับขั้ว"

### 4.1 Bullish Breaker Block

**การก่อตัว**:
1. Bearish Order Block ถูกสร้างขึ้น (แท่งเทียนขาขึ้นสุดท้ายก่อนก���รร่วงลง)
2. ราคากลับมาทะลุเหนือ Bearish OB ทั้ง���มด (ละเมิด)
3. Bearish OB ที่ถูกละเมิดกลายเป็น **Bullish Breaker Block**
4. เมื่อราคาดึงกลับมาที่โซนนี้ จะทำหน้าที่เป็นแนวรับ

**ตรรกะ**:
$$\text{BullishBreaker} = \text{BearishOB}_{\text{violated}} \implies \text{zone flips to bullish support}$$

### 4.2 Bearish Breaker Block

**การก่อตัว**:
1. Bullish Order Block ถูกสร้างขึ้น
2. ราคาทะลุต่ำกว่า Bullish OB ทั้งหมด (ละเมิด)
3. Bullish OB ที่ถูกละเมิดกลายเป็น **Bearish Breaker Block**
4. เมื่อร��คาวิ่งขึ้นมาที่โซนนี้ จะทำหน้าที่เป็นแนวต้าน

### 4.3 กฎการเทรด

| กฎ | Bullish Breaker | Bearish Breaker |
|------|----------------|-----------------|
| **ทิศทาง** | Long | Short |
| **โซนเข้าเทรด** | OB high ถึง OB low (กลับขั้วแล้ว) | OB low ถึง OB high (กลับขั้วแล้ว) |
| **การยืนยัน** | LTF bullish CHoCH ภายในโซน | LTF bearish CHoCH ภายในโซน |
| **Stop Loss** | ต่ำกว่า breaker low − buffer | เหนือ breaker high + buffer |
| **เป้าหมาย** | สภาพคล่อง HTF ถัดไป | สภาพคล่อง HTF ถัดไป |

### 4.4 ลำดับความสำคัญ Breaker กับ Order Block

เมื่อทั้ง OB และ Breaker ทับซ้อนกัน **Breaker มีความสำคัญกว่า** เพราะแสดงถึงการเปลี่ยนแปลงเชิงโครงสร้าง (การกลับขั้ว) AI ควรให้ความมั่นใจสูงกว่ากับการเข้าเทรดที่ Breaker เมื่อมีปัจจัยสนั��สนุนหลายอย่าง

---

## 5. Mitigation Blocks

### 5.1 นิยาม

Mitigation Block คือโซนที่ผู้เล่นสถาบันกลับมา "บรรเทา" (ปิดหรือเฮดจ์) ��ำแหน่งที่สะสมไว้ก่อนหน้าซึ่งตอนนี้ขาดทุนอยู่เนื่องจากโครงสร้างเปลี่ยน

### 5.2 การก่อตัว (Bearish Mitigation Block)

1. เทรนด์ขาขึ้นเกิดขึ้น สถาบัน Long อยู่
2. เกิด CHoCH (ขาลง) — โครงสร้างเปลี่ยน
3. สถาบันต้องปิดตำแหน่ง Long ที่ขาดทุน
4. ราคาดึงกลับขึ้นไปยังจุดเริ่มต้นของ **ขาสุดท้ายที่ล้มเหลว** (จุดสวิงไฮที่เป็นจุดเริ่มต้นของการเคลื่อนไหวขาลง)
5. โซนนี้ = Bearish Mitigation Block สถาบันขายที่นี่เพื่อออกจาก Long สร้าง Supply

### 5.3 การก่อตัว (Bullish Mitigation Block)

1. เทรนด์ขาลงเกิดขึ้น สถาบัน Short อยู่
2. เกิด CHoCH (ขาขึ้น)
3. ราคาดึงกลับลงไปยังจุดเริ่มต้นของขาลงสุดท้ายที่ล้มเหลว
4. โซนนี้ = Bullish Mitigation Block สถาบันซื้อที่นี่เพ��่อปิด Short สร้าง Demand

### 5.4 ความแตกต���างหลักจาก Order Blocks

| คุณลักษณะ | Order Block | Mitigation Block |
|---------|-------------|-----------------|
| **วัตถุประสงค์** | เปิดตำแหน่งใหม่ | ปิด/เฮดจ์ตำแหน่งเก่า |
| **ตำแหน่ง** | ก่อนการเคลื่อนไหวอิมพัลส์ | ที่จุดเริ่มต้นของขาโครงสร้างที่ล้มเหลว |
| **ความแข็งแกร่ง** | โดยทั่วไปแข็งแรงกว่า | ปานกลาง — ใช้ได้ครั้งเดียว |
| **การทดสอบซ้ำ** | สามารถรับหลายครั้งได้ | มักจะได้ผลเพียงครั้งเดียว |

---

## 6. Institutional Order Flow Entry Drill (IOFED)

IOFED เป็นกระบวนการเข้าเทรดแบบ Top-Down ที่เป็นระบบ ใช้จัดแนวบริบทมหภาคกับจุดเข้าที่แม่นยำ

### 6.1 กระบวนกา�� IOFED

**ขั้นที่ 1 — HTF Narrative (Daily/Weekly)**
- กำหน��โครงสร้างตลาด HTF (ขาขึ้น/ขาลง)
- ระบุ HTF POI (จุดที่น่าสนใจ): OB, Breaker, FVG, สภาพคล่อง
- กำหนดว่าราคาอยู่ในโซนพรีเมียมหรือดิสเคาท์

**ขั้นที่ 2 — ย��นยันไทม์เฟรมกลาง (H4/H1)**
- รอให้ราคาถึง HTF POI
- มองหา CHoCH หรือ BOS ในไทม์เฟรมกลางที่ยืนยันทิศท��ง HTF
- ระบุ OB/FVG ไทม์เฟรมกลางภายใน HTF POI

**ขั้นที่ 3 — LTF Entry (M15/M5)**
- เจาะลงไป LTF เมื่อการยืนย���นไทม์เฟรมกลางเกิดขึ้น
- ระบุ LTF CHoCH หรือ BOS ในทิศทางของ HTF
- เข้าที่ LTF OB หรือ FVG ที่เกิดหลัง LTF structural shift

**ขั้นที่ 4 — การดำเนินการ**
- วาง Limit Order ที่โซนเข้าเทรด LTF
- Stop Loss ต่ำกว่า/เหนื��จุดสวิง LTF ที่สร้าง CHoCH
- เป้าหมาย: จุดสวิงไทม์เฟรมกลาง → เป้าหมายสภาพคล่อง HTF

### 6.2 IOFED Decision Matrix

```
HTF Bias:    BULLISH
├── ราคาอยู่ในโซน Discount?  → ใช่ → ดำเนินการ
│   └── H4 CHoCH Bullish?   → ใช่ → ดำเนินการ
│       └── M15 CHoCH Bullish? → ใช่ → เข้า LONG ที่ M15 OB
│           ├── SL: ต่ำกว่า M15 swing low
│           ├── TP1: H4 internal swing high
│           └── TP2: HTF external swing high / เป้าหมายสภาพคล่อง
├── ราคาอยู่ในโซน Premium?   → ไม่เทรด (รอ discount)
└── H4 CHoCH Bearish?       → ไม่เทรด (สัญญาณขัดแย้ง)
```

---

## 7. โซนพรีเมียมและดิสเคาท์ (Premium and Discount Zones)

### 7.1 แนวคิด

ทุกขาราคา (จุดสวิงโลว์ถึงสวิงไฮ หรือกลับกัน) สามารถแบ่งเป็นโซนพรีเมียมและดิสเคาท์โดยใช้ระดับ 50% (จุ���สมดุล)

- **โซนพรีเมียม**: เหนือระดับ 50% (แพง) เหมาะสำหรับขาย
- **โซนดิสเคาท์**: ต่ำกว่าระดับ 50% (ถูก) เหมาะสำหรับซื้อ

### 7.2 การคำนวณ

สำหรับ��าขึ้นจากสวิงโลว์ $L$ ถึงสวิงไฮ $H$:

$$\text{Equilibrium} = \frac{H + L}{2}$$

$$\text{Premium Zone} = \left[\frac{H + L}{2}, H\right]$$

$$\text{Discount Zone} = \left[L, \frac{H + L}{2}\right]$$

### 7.3 Fibonacci Overlay

โซนพรีเมียม/ดิสเคาท์ถูกปรับละเอียดเพิ่มเติมโดยใช้ Fibonacci Retracement ของสวิง:

| ระดับ Fibonacci | โซน | ความสำค���ญ |
|----------------|------|--------------|
| 0.0 (Swing High) | พรีเมียมสุดขีด | โอกาส Mean-Reversion สูงสุด |
| 0.236 | พรีเมียม | โซน Pullback ตื้น |
| 0.382 | พรีเมียม | โซน Pullback ปานกลาง |
| 0.500 | จุดสมดุล | มูลค่ายุติธรร�� — เป็นกลาง |
| 0.618 | ดิสเคาท์ | **Optimal Trade Entry (OTE)** |
| 0.705 | ดิสเคาท์ | ดิสเคาท์ลึก |
| 0.786 | ดิสเคาท์ | ดิสเคาท์สุดขีด |
| 1.0 (Swing Low) | ดิสเคาท์สุดขีด | เขตจุดที่เทรดจะเป็นโมฆะ |

### 7.4 กฎการเทรด

- **Long**: เฉพาะที่ระดับดิสเคาท์เท่านั้น (0.618–0.786 แนะนำ = โซน OTE)
- **Short**: เฉพาะที่ระดับพรีเมียมเท่านั้น (0.236–0.382 แนะนำ)
- การเข้าที่จุดสมดุล (0.5) มีความน่าจะเป็นต่ำกว่าและควรหลีกเลี่ยง เว้นแต่มีปัจจัยสนับสนุนที่แข็งแกร่ง

$$\text{OTE\_Zone} = \left[H - 0.786 \times (H - L), \; H - 0.618 \times (H - L)\right]$$

---

## 8. จุดสมดุล (Equilibrium)

### 8.1 นิยาม

จุดสมดุลแสดงถึง "ราคายุติธรรม" ของช่วงราคาที่กำหนด ตลาดแกว่งรอบจุดสมดุลตามธรรมชาติ ทำให้เป็นจุดอ้างอิงที่สำคัญ

$$EQ = \frac{H_{\text{range}} + L_{\text{range}}}{2}$$

### 8.2 การประยุกต์ใช้จุดสมดุล

1. **Range Equilibrium**: จุดกลางของช่วงสะสม ราคาใช้เวลาส่วนใหญ่ใกล้จุดสมดุล (เทียบกับ Market Profile / POC)

2. **Swing Equilibrium**: 50% Retracement ของขาอิมพัลส์ ใช้แบ่งโซนพรีเมียม/ดิสเคาท์

3. **FVG Equilibrium**: จุดกลางของ Fair Value Gap มักทำหน้าที่เป็นแม่เหล็กดึงดูดราคา

$$EQ_{\text{FVG}} = \frac{H_{\text{FVG}} + L_{\text{FVG}}}{2}$$

4. **Order Block Equilibrium**: ระดับ 50% ของ Order Block จุดเข้าปรับละเอียดเล็งที่ระดับนี้

### 8.3 จุดสมดุลเป็นขอบ���ขตการตัดสินใจ

AI agent ใช้จุดสมดุลเป็นตัวกรองแบบไบนารี:

```
IF price_position < equilibrium:
    bias = BULLISH (we are in discount)
    only_look_for = LONG entries
ELIF price_position > equilibrium:
    bias = BEARISH (we are in premium)
    only_look_for = SHORT entries
```

---

## 9. Kill Zones

Kill Zones คือช่วงเวลาเฉพาะที่ผู้เล่นสถาบันมีกิจกรรมมากที่สุด สร้างเซ็ตอัปการเทรดที่มีความน่าจะเป็นสูงสุด

### 9.1 Forex Kill Zones (UTC)

| Kill Zone | เวลา (UTC) | ลักษณะ |
|-----------|-----------|-----------------|
| **Asian Session** | 00:00 – 06:00 | แกว่งตัว; สภาพคล่องสะสมที่ session highs/lows |
| **London Open** | 07:00 – 10:00 | ผันผวนสูงสุด; smart money สะสม/กระจาย |
| **New York Open** | 12:00 – 15:00 | ผันผวนสูงอันดับสอง; มักกลับตัวจากขา London |
| **London Close** | 15:00 – 17:00 | สถาบันปรับพอร์ต; เทรนด์หมดแรง |

### 9.2 Crypto Kill Zones (UTC)

ตลาดคริปโตเปิด 24/7 แต่การรวมตัวของวอลุ่มยังสร้าง kill zones ที่มีประสิทธิภาพ:

| Kill Zone | เวลา (UTC) | เหตุผล |
|-----------|-----------|-----------|
| **Asian Crypto** | 00:00 – 04:00 | นักเทรดสถาบันและรายย่อยจีน/เกาหลี/ญี่ปุ่น |
| **European Crypto** | 07:00 – 10:00 | โต๊ะสถาบันยุโรปเริ่มทำงาน |
| **US Crypto** | 13:00 – 16:00 | จุดสูงสุดสถาบันและรายย่อยสหรัฐ |
| **US Evening** | 20:00 – 23:00 | รายย่อยสหรัฐ + pre-market เอเชีย |

### 9.3 ตรรกะการเทรด Kill Zone

1. **ก่อน Kill Zone**: ระบุช่วง Range ที่เกิดระหว่าง Quiet Session (เช่น Asian Range ก่อน London)
2. **Kill Zone เริ่ม**: เฝ้าดูการกวาดสภาพคล่องของ Quiet Session (Stop Hunt เหนือ/ต่ำกว่า Range)
3. **กลับตัว**: หลังการกวาด มองหา CHoCH บน M5/M15 บ่งบอกขาจริง
4. **เข้าเทรด**: เข้าที่ OB/FVG ที่เกิดหลัง CHoCH

### 9.4 Asian Range Sweep Model

$$\text{Asian High} = \max(H_i) \quad \text{for } i \in [00:00, 06:00] \text{ UTC}$$
$$\text{Asian Low} = \min(L_i) \quad \text{for } i \in [00:00, 06:00] \text{ UTC}$$

**เซ็ตอัปขาขึ้น**: ราคากวาดต่ำกว่า Asian Low ช่วง London Open แล้วกลับตัวพร้อม CHoCH → Long

**เซ็ตอัปขาลง**: ราคากวาดเหนือ Asian High ช่วง London Open แล้วกลับตัวพร้อม CHoCH → Short

---

## 10. Fair Value Gaps (FVG)

### 10.1 นิยาม

Fair Value Gap ��ือรูปแบบ 3 แท่งเทียนที่ไส้เทียนของแท่งที่ 1 ไม่ทับซ้อนกับไส้เทียนของแท่งที่ 3 ทิ้งช่วงราคาที่ "ยังไม่ถูกเติม" ไว้ที่แท่งที่ 2 แสดงถึงกิจกรรมสถาบันแบบก้าว���้าวที่สร้างความไม่สมดุล

### 10.2 Bullish FVG

$$\text{BullishFVG}: L_3 > H_1$$

โซน:
$$\text{FVG\_Upper} = L_3$$
$$\text{FVG\_Lower} = H_1$$

### 10.3 Bearish FVG

$$\text{BearishFVG}: H_3 < L_1$$

โซน:
$$\text{FVG\_Upper} = L_1$$
$$\text{FVG\_Lower} = H_3$$

### 10.4 FVG เป็นโซนเข้าเทรด

- ราคามักจะดึงกลับเข้า FVG ก่อนจะเคลื่อนไหวต่อในทิศทางของอิมพัลส์
- **CE (Consequent Encroachment)** คือระดับ 50% ของ FVG — ระดับที่น่าจะถูกเติมมากที่สุด

$$CE = \frac{\text{FVG\_Upper} + \text{FVG\_Lower}}{2}$$

### 10.5 การจำแนก FVG

| ประเภท | คำอธิบาย | ความสำคัญ |
|------|-------------|--------------|
| **FVG ยังไม่ถูก Mitigate** | ราคายังไม่กลับมาที่ gap | สูง — รอการเติม |
| **Mitigate บางส่วน** | ราคาเติมถึง CE แต่ยังไม่ครบ | ปานกลาง — อาจยังดึงดูดอยู่ |
| **Mitigate เต็ม** | ราคาปิดทะลุ gap ทั้งหมด | ต่ำ — ไม่เกี่ยวข้องอีกแล้ว |
| **Inversion FVG** | FVG ถูก mitigate เต็มแล้วทำหน้าที่เป็นแนวรับ/ต้าน | ปานกลาง-สูง — กลับขั้ว |

---

## 11. แนวคิดเรื่องสภาพคล่อง (Liquidity Concepts)

### 11.1 ประเภทสภาพคล่อง

**Buy-Side Liquidity (BSL)**: ออเดอร์ Stop Loss ของคนที่ Short อยู่เหนือจุดสวิงไฮ สถาบันเล็งเป้า BSL โดยดันราคาขึ้นเพื่อเติมออเดอร์ขาย

**Sell-Side Liquidity (SSL)**: ออเดอร์ Stop Loss ของคนที่ Long อยู่ต่ำกว่าจุดสวิงโลว์ สถาบันเล็งเป้า SSL โดยดันราคาลงเพื่อเติมออเดอร์ซื้อ

### 11.2 การระบุ Liquidity Pool

```python
def identify_liquidity_pools(swing_points, price_data):
    bsl_pools = []
    ssl_pools = []
    
    for sp in swing_points:
        if sp.type == "swing_high":
            # Count how many times this level was tested
            touches = count_touches(price_data, sp.price, tolerance=ATR*0.1)
            if touches >= 2:
                bsl_pools.append({
                    "level": sp.price,
                    "strength": touches,
                    "type": "BSL"
                })
        elif sp.type == "swing_low":
            touches = count_touches(price_data, sp.price, tolerance=ATR*0.1)
            if touches >= 2:
                ssl_pools.append({
                    "level": sp.price,
                    "strength": touches,
                    "type": "SSL"
                })
    
    return bsl_pools, ssl_pools
```

### 11.3 Equal Highs / Equal Lows

Equal Highs (EQH) และ Equal Lows (EQL) เป็นเป้าหมายสภาพคล่องที่มีความน่าจะเป็นสูงสุดเพราะแสดงถึงกลุ่ม Stop Loss ที่ชัดเจน

$$\text{EqualHighs}: |H_a - H_b| \leq \epsilon \quad \text{where } \epsilon = 0.1 \times \text{ATR}(14)$$

### 11.4 Liquidity Sweep (Stop Hunt)

**Liquidity Sweep** เกิดขึ้นเมื่��ราคาเคลื่อนไหวเกิน Liquidity Pool แล้วกลับตัว นี่���ือเอกลักษณ์ของการวิศวกรรมโดยเงินฉลาด — สร้างภาพลวงของ Breakout เพื่อกระตุ้�� Stop ของรายย่อย แล้วกลับตัว

การตรวจจับ:
$$\text{Sweep} = \begin{cases} \text{Bullish Sweep (of SSL)} & \text{if } L_i < \text{SSL\_level} \text{ AND } C_i > \text{SSL\_level} \\ \text{Bearish Sweep (of BSL)} & \text{if } H_i > \text{BSL\_level} \text{ AND } C_i < \text{BSL\_level} \end{cases}$$

---

## 12. โมเดลการเข้าเทรด (Entry Models)

### 12.1 Risk Entry (แบบก้าวร้าว)

Risk Entry วาง **Limit Order** ตรงที่ Point of Interest (OB, Breaker, FVG) โดยไม่รอการยืนยันจากไทม์เฟรมเล็ก

**ข้อดี**: ได้ราคาเข้าดีที่สุด; ระยะ Stop Loss น้อยที่สุด
**ข้อเสีย**: อัตราล้มเหลวสูงกว่���; เสี่ยงโดน Stop Hunt

**ขั้นตอน**:
1. ระบุ HTF POI (เช่น H4 Bullish OB ในโซนดิสเคาท์)
2. วาง Limit Buy ที่จุดกลาง OB (OB Equilibrium) หรือ FVG CE
3. Stop Loss: ต่ำกว่า OB low ลบ 1x ATR buffer ของไทม์เฟรมเข้าเทรด
4. ไม่ต้องรอการยืนยัน LTF

$$\text{Entry}_{\text{risk}} = \frac{O_{\text{OB}} + L_{\text{OB}}}{2}$$

$$\text{SL}_{\text{risk}} = L_{\text{OB}} - k \times \text{ATR}(14)_{\text{entry\_TF}}$$

โดย $k = 0.2$ ถึง $0.5$ ขึ้นอยู่กับความผันผวน

### 12.2 Confirmation Entry (แบบอนุรักษ์นิยม)

Confirmation Entry ต้องการ **การเปลี่ยนแปลงโครงสร้างในไทม์เฟรมเล็ก** (CHoCH) ภายใน POI ก่อนเข้าเทรด

**ข้อดี**: อัตราชนะสูงขึ้น; ยืนยันการมีส่วนร่วมของสถาบัน
**ข้อเสีย**: ได้ราคาเข้าแย่กว่า; Stop Loss กว้างกว่า; อาจพลาดการเคลื่อนไหวเร็ว

**ขั้นตอน**:
1. ระบุ HTF POI
2. รอให้ราคาเข้าโซน POI
3. เปลี่ยนไป LTF (ต่ำกว่า 1-2 ไทม์เฟรม)
4. รอ LTF CHoCH ในทิศ��างของ HTF bias
5. เข้าที่ LTF OB ที่เกิดหลัง CHoCH
6. Stop Loss: ต่ำกว่า/เหนือจุดสวิง LTF ที่สร้าง CHoCH

```
HTF_POI_reached = price_enters_zone(htf_ob)
IF HTF_POI_reached:
    ltf_choch = detect_choch(ltf_candles, direction=htf_bias)
    IF ltf_choch:
        ltf_ob = find_ob_after_choch(ltf_candles, ltf_choch)
        entry = ltf_ob.midpoint
        sl = ltf_choch.swing_extreme + buffer
        EXECUTE TRADE(entry, sl, targets)
```

### 12.3 Hybrid Entry

รวมทั้งสอง: วาง Risk Entry ที��� HTF POI ด้วย 50% ของขนาดตำแหน่ง และเพิ่มอีก 50% เมื่อได้การยืนย��น LTF ช่วยสมดุลระหว่างการจับโอกาสกับการยืนยัน

$$\text{Avg Entry}_{\text{hybrid}} = \frac{0.5 \times E_{\text{risk}} + 0.5 \times E_{\text{confirm}}}{1.0}$$

---

## 13. โมเดลทางคณิตศาสตร์

### 13.1 Order Block Displacement Index (OBDI)

วัดความแข็งแกร่งของ Displacement จาก Order Block:

$$\text{OBDI} = \frac{\sum_{i=1}^{n} |C_i - O_i|}{\sum_{i=1}^{n} (H_i - L_i)} \times \frac{\text{Range}_{\text{impulse}}}{\text{ATR}(14) \times n}$$

โดย $n$ = จำนวนแท่งเทียนในขาอิมพัลส์

การตีความ:
- $\text{OBDI} > 1.5$: Displacement แข็งแรง — OB คุณภาพสูง
- $1.0 < \text{OBDI} \leq 1.5$: Displacement ปานกลาง
- $\text{OBDI} \leq 1.0$: Displacement อ่อน — OB คุณภาพต่ำ

### 13.2 Liquidity-Weighted Bias Score (LWBS)

$$\text{LWBS} = \frac{\sum_{j} \text{BSL}_j \times d_j^{-1}}{\sum_{j} \text{BSL}_j \times d_j^{-1} + \sum_{k} \text{SSL}_k \times d_k^{-1}}$$

โดยที่:
- $\text{BSL}_j$ = ความแข็งแกร่ง (จำน���นครั้งที่แตะ) ของ Buy-Side Liquidity Pool ที่ $j$
- $\text{SSL}_k$ = ความแข็งแกร่งของ Sell-Side Liquidity Pool ที่ $k$
- $d_j, d_k$ = ระยะทางจากราคาปัจจุบันถึง Pool ที่เกี่ยวข้อง

การตีความ:
- $\text{LWBS} > 0.6$: ราคามีแนวโน้มจะวิ่งหา BSL → ทิศทางขาขึ้น
- $\text{LWBS} < 0.4$: ราคามีแนวโน้มจะวิ่งหา SSL → ทิศทางขาลง

### 13.3 FVG Fill Probability Model

จากการสังเกตเชิงประจัก���์ ความน่าจะเป็นที่ FVG จะถูกเติมเป็นไปตามโมเดล Time-Decay:

$$P(\text{fill} \mid t) = 1 - e^{-\alpha \cdot t}$$

โดยที่:
- $t$ = จำน��นแท่งเทียนนับจาก FVG เกิด
- $\alpha$ = พารามิเตอร์อัตราการเติมเฉพาะสินทรัพย์

ค่า $\alpha$ ทั่วไป:
| สินทรัพย์ | $\alpha$ (H1) |
|-------|---------------|
| EUR/USD | 0.015 |
| GBP/USD | 0.018 |
| BTC/USD | 0.012 |
| ETH/USD | 0.014 |

### 13.4 Multi-POI Confluence Score

เมื่อองค์ประกอบ SMC หลายตัวทับซ้อนกัน คุณภาพจุดเข้าเพิ่มขึ้น:

$$\text{Confluence} = \sum_{i=1}^{N} w_i \cdot \mathbb{1}[\text{POI}_i \text{ present in zone}]$$

| องค์ประกอบ POI | น้ำหนัก ($w_i$) |
|-------------|---------------|
| HTF Order Block | 0.25 |
| FVG | 0.20 |
| OTE Zone (0.618–0.786) | 0.20 |
| Liquidity Sweep | 0.15 |
| Breaker Block | 0.10 |
| Kill Zone timing | 0.10 |

**Confluence ขั้นต่ำสำหรับเทรด**: $\text{Confluence} \geq 0.55$

---

## 14. พารามิเตอร์ความเสี่ยง

### 14.1 การกำหนดขนาดตำแหน่ง

$$\text{Position Size} = \frac{\text{Account Balance} \times R\%}{|E - SL| \times \text{Pip Value}}$$

โดย $R\% = 1\%$ ต่อเทรด (สูงสุด 2% สำหรับเซ็ตอัป A+ ที่มี Confluence $\geq 0.80$)

### 14.2 การวาง Stop Loss

| ประเภทการเข้า | ตำแหน่ง SL | Buffer |
|-----------|-------------|--------|
| Risk Entry ที่ OB | ต่ำกว่า OB low (long) / เหนือ OB high (short) | 0.2 × ATR |
| Confirmation Entry | ต่ำกว่า LTF CHoCH swing | 0.1 × ATR |
| FVG Entry | ต่ำกว่าไส้เทียนแท่งที่ 1 ที่กำหนด FVG | 0.15 × ATR |

### 14.3 เป้าหมายทำกำไร (Take Profit)

| เป้าหมาย | ตำแหน่ง | ปิดบางส่วน |
|--------|----------|---------------|
| TP1 | สภาพคล่องภายใน (สวิงฝั่งตรงข้ามใกล้สุด) | 40% ของตำแหน่ง |
| TP2 | สภาพคล่องภายนอก (HTF swing high/low) | 30% ของตำแหน่ง |
| TP3 | เป้าหมายขยาย (HTF liquidity pool ถัดไป) | 20% ของตำแหน่ง |
| Trail | Trailing Stop ตาม HL/LH โครงส���้างใหม่ | 10% ของตำแหน่ง |

### 14.4 ข้อกำหนด Risk-Reward

| คุณภาพเซ็ตอัป | R:R ขั้นต่ำ |
|--------------|-------------|
| A+ (Confluence ≥ 0.80) | 3:1 |
| A (Confluence 0.65–0.79) | 4:1 |
| B+ (Confluence 0.55–0.64) | 5:1 |
| ต่ำกว่า B+ | ไม่เทรด |

### 14.5 ข้อจำกัดความเสี่ยงรายวัน

- ความเสี่ยงรายวันสูงสุด: 3% ของพอร์ต
- จำนวนเทรดพร้อมกันสูงสุด: 3
- ความเสี่ยงที่สัมพันธ์กันสูงสุด: 2% (เช่น สองคู่ USD นับรวมกัน)
- หลังขาดทุนต่อเนื่อง 2 ครั้ง: หยุดพัก 1 Kill Zone session
- หลังขาดทุนต่อเนื่อง 3 ครั้ง: หยุดพัก 24 ชั่วโมง

### 14.6 การจัดการ Drawdown

$$\text{If Drawdown} \geq 5\%: \text{ลด } R\% \text{ เป็น } 0.5\%$$
$$\text{If Drawdown} \geq 8\%: \text{ลด } R\% \text{ เป็น } 0.25\%$$
$$\text{If Drawdown} \geq 10\%: \text{หยุ��เทรด, ทบทวนกลยุทธ์}$$

---

## 15. ขั้นตอนการดำเนินก��รทั้งหมด

### 15.1 Main Loop Pseudocode

```python
def smc_main_loop():
    """
    Main execution loop for the SMC trading strategy.
    Runs continuously during active kill zones.
    """
    
    # ========================================
    # STEP 1: HIGHER TIMEFRAME ANALYSIS (Daily/Weekly)
    # ========================================
    htf_data = fetch_candles(timeframe="D1", count=120)
    
    # 1a. Determine HTF market structure
    htf_swings = identify_swing_points(htf_data, lookback=5)
    htf_structure = classify_structure(htf_swings)  # BULLISH / BEARISH / RANGING
    
    # 1b. Identify HTF POIs
    htf_obs = find_order_blocks(htf_data, htf_swings)
    htf_fvgs = find_fvgs(htf_data)
    htf_breakers = find_breaker_blocks(htf_data, htf_obs)
    htf_liquidity = identify_liquidity_pools(htf_swings, htf_data)
    
    # 1c. Determine premium/discount
    htf_eq = calculate_equilibrium(htf_swings)
    current_zone = "DISCOUNT" if current_price < htf_eq else "PREMIUM"
    
    # 1d. Filter: Only trade in the direction of HTF structure
    if htf_structure == "BULLISH" and current_zone != "DISCOUNT":
        return NO_TRADE("Bullish bias but price in premium — wait for discount")
    if htf_structure == "BEARISH" and current_zone != "PREMIUM":
        return NO_TRADE("Bearish bias but price in discount — wait for premium")
    
    # ========================================
    # STEP 2: INTERMEDIATE TIMEFRAME (H4/H1)
    # ========================================
    itf_data = fetch_candles(timeframe="H4", count=200)
    
    # 2a. Check if price is at an HTF POI
    htf_poi = find_nearest_poi(current_price, htf_obs + htf_fvgs + htf_breakers)
    if not price_in_zone(current_price, htf_poi):
        return WAIT("Price not at HTF POI yet")
    
    # 2b. Look for ITF structural confirmation
    itf_swings = identify_swing_points(itf_data, lookback=7)
    itf_choch = detect_choch(itf_swings, direction=htf_structure)
    itf_bos = detect_bos(itf_swings, direction=htf_structure)
    
    if not (itf_choch or itf_bos):
        return WAIT("No ITF confirmation at HTF POI")
    
    # 2c. Identify ITF POI for refined entry
    itf_obs = find_order_blocks(itf_data, itf_swings)
    itf_fvgs = find_fvgs(itf_data)
    
    # ========================================
    # STEP 3: LOWER TIMEFRAME ENTRY (M15/M5)
    # ========================================
    ltf_data = fetch_candles(timeframe="M15", count=200)
    
    # 3a. Wait for LTF structural shift
    ltf_swings = identify_swing_points(ltf_data, lookback=3)
    ltf_choch = detect_choch(ltf_swings, direction=htf_structure)
    
    if not ltf_choch:
        return WAIT("No LTF CHoCH — no entry trigger")
    
    # 3b. Find LTF entry zone
    ltf_ob = find_ob_after_choch(ltf_data, ltf_choch)
    ltf_fvg = find_fvg_after_choch(ltf_data, ltf_choch)
    entry_zone = ltf_ob if ltf_ob else ltf_fvg
    
    if not entry_zone:
        return WAIT("No valid LTF entry zone after CHoCH")
    
    # ========================================
    # STEP 4: CONFLUENCE SCORING
    # ========================================
    confluence = calculate_confluence(
        htf_ob=htf_poi.type == "OB",
        fvg_present=ltf_fvg is not None,
        ote_zone=is_in_ote(current_price, htf_swings),
        liquidity_swept=detect_sweep(ltf_data, htf_liquidity),
        breaker_present=htf_poi.type == "BREAKER",
        in_kill_zone=is_kill_zone(current_time)
    )
    
    if confluence < 0.55:
        return NO_TRADE(f"Confluence {confluence} below threshold 0.55")
    
    # ========================================
    # STEP 5: RISK MANAGEMENT
    # ========================================
    # 5a. Calculate entry, SL, TP
    entry_price = entry_zone.midpoint
    
    if htf_structure == "BULLISH":
        sl_price = entry_zone.low - ATR_BUFFER
        tp1 = nearest_internal_high(itf_swings)
        tp2 = nearest_external_high(htf_swings)
    else:
        sl_price = entry_zone.high + ATR_BUFFER
        tp1 = nearest_internal_low(itf_swings)
        tp2 = nearest_external_low(htf_swings)
    
    risk_reward = abs(tp1 - entry_price) / abs(entry_price - sl_price)
    
    min_rr = get_min_rr(confluence)
    if risk_reward < min_rr:
        return NO_TRADE(f"R:R {risk_reward:.1f} below minimum {min_rr}")
    
    # 5b. Position sizing
    risk_amount = account_balance * get_risk_percent(drawdown)
    position_size = risk_amount / abs(entry_price - sl_price)
    
    # 5c. Check daily limits
    if daily_risk_used + risk_amount > MAX_DAILY_RISK:
        return NO_TRADE("Daily risk limit reached")
    
    if open_trade_count >= MAX_CONCURRENT:
        return NO_TRADE("Max concurrent trades reached")
    
    # ========================================
    # STEP 6: EXECUTE
    # ========================================
    order = place_limit_order(
        direction="BUY" if htf_structure == "BULLISH" else "SELL",
        entry=entry_price,
        stop_loss=sl_price,
        take_profit_1=tp1,
        take_profit_2=tp2,
        size=position_size,
        expiry=next_kill_zone_end()
    )
    
    log_trade(order, confluence, htf_structure, entry_zone)
    
    return order
```

### 15.2 Trade Management Pseudocode

```python
def manage_open_trade(trade):
    """
    Active management of an open SMC trade.
    """
    ltf_data = fetch_candles(timeframe=trade.entry_tf, count=100)
    
    # Partial close at TP1
    if price_reached(trade.tp1) and not trade.tp1_hit:
        close_partial(trade, percent=40)
        move_sl_to_breakeven(trade)
        trade.tp1_hit = True
    
    # Partial close at TP2
    if price_reached(trade.tp2) and not trade.tp2_hit:
        close_partial(trade, percent=30)  # 30% of original = ~50% of remaining
        trail_sl_behind_structure(trade, ltf_data)
        trade.tp2_hit = True
    
    # Trailing stop on remaining position
    if trade.tp2_hit:
        new_swing = latest_swing_in_direction(ltf_data, trade.direction)
        if new_swing:
            new_sl = new_swing.price - ATR_BUFFER if trade.direction == "BUY" else new_swing.price + ATR_BUFFER
            if is_tighter(new_sl, trade.current_sl, trade.direction):
                update_sl(trade, new_sl)
    
    # Time-based exit: if trade hasn't hit TP1 within 2 kill zone sessions
    if trade.age_in_sessions >= 2 and not trade.tp1_hit:
        close_full(trade, reason="Time expiry — no momentum")
    
    # Structural invalidation
    structure = classify_structure(identify_swing_points(ltf_data))
    if structure_contradicts(structure, trade.direction):
        close_full(trade, reason="LTF structure invalidated")
```

---

## 16. หมายเหตุการใช้งาน AI

### 16.1 ข้อกำ���นดข้อมูล

| ประเภทข้อมูล | ประวัติขั้นต่ำ | ความถี่อัปเดต |
|-----------|----------------|-----------------|
| แท่งเทียน Weekly | 2 ปี | ทุกวันจันทร์ |
| แท่งเทียน Daily | 6 เดือน | ทุกวัน |
| แท่งเทียน H4 | 3 เดือน | ทุก 4 ชั่วโมง |
| แท่งเทียน H1 | 1 เดือน | ทุกชั่วโมง |
| แท่งเทียน M15 | 2 สัปดา��์ | ทุก 15 นาที |
| แท่งเทียน M5 | 1 สัปดาห์ | ทุก 5 นาที |

### 16.2 ลำดับความสำคัญการคำนวณ

1. **HTF structure**: คำนวณใหม่ทุกแท่งเทียน Daily ปิด
2. **HTF POIs**: คำนวณใหม่ทุกแท่งเทียน H4 ปิด
3. **Kill Zone check**: ประเมินทุกนาที
4. **LTF entry**: ประเมินทุกแท่งเทียน M5 ปิดระหว่าง Kill Zone ที่ใช้งานอยู่เท่านั้น

### 16.3 การจัดการ State

Agent ต้อ���ดูแล:
- HTF bias ปัจจุบัน (BULLISH/BEARISH/RANGING)
- รายการ OBs, FVGs, และ Breakers ที่ยังไม่ถูก mitigate ต่อไทม์เฟรม
- Liquidity Pools พร้อมจำนวนครั้งที่แตะ
- โซนปัจจุบัน (PREMIUM/DISCOUNT) ต่อสวิงที่เกี่ยวข้อง
- เทรดที่เปิดอยู่พร้อมสถานะการจัดการ

### 16.4 ข้อพิจารณาการ Backtest

- เซ็ตอัป SMC ค่อนข้างหายาก (5–15 เทรดต่อคู่ต่อเดือนบน H1)
- ต้องการอย่างน้อย 200 เทรดส��หรับความสำคัญทางสถิติ
- ติดตาม: win rate, average R:R, profit factor, max drawdown, Sharpe ratio
- เกณฑ์มาตรฐ��นผลงานที่คาดหวัง:
  - Win Rate: 45–55%
  - Average R:R: 3:1 ถึง 5:1
  - Profit Factor: 1.5–2.5
  - Monthly Return: 3–8% (ด้วย 1% risk ต่อเทรด)

---

## 17. เอกสารอ้างอิง

### งานวิจัยเชิงวิชาการและสถาบัน
1. Menkhoff, L., & Taylor, M. P. (2007). "The Obstinate Passion of Foreign Exchange Professionals: Technical Analysis." *Journal of Economic Literature*, 45(4), 936–972.
2. Osler, C. L. (2003). "Currency Orders and Exchange Rate Dynamics: An Explanation for the Predictive Success of Technical Analysis." *The Journal of Finance*, 58(5), 1791–1819.
3. Kavajecz, K. A., & Odders-White, E. R. (2004). "Technical Analysis and Liquidity Provision." *The Review of Financial Studies*, 17(4), 1043–1071.

### หนังสือ
4. Brooks, A. (2012). *Trading Price Action Trends*. Wiley.
5. Wyckoff, R. D. (1931). *The Richard D. Wyckoff Method of Trading and Investing in Stocks*. Wyckoff Associates.
6. Dalton, J. F. (1993). *Mind Over Markets*. McGraw-Hill.
7. Neill, H. B. (2001). *The Art of Contrary Thinking*. Caxton Press.

### แหล่งข้อมูลจากผู้ปฏิบัติ
8. ICT (The Inner Circle Trader). "ICT Mentorship" lecture series (2016–2024). — แหล่งข้อมูลหลักสำหรับ Order Blocks, Kill Zones, OTE, และ IOFED
9. Michael J. Huddleston. "ICT Charter Price Delivery Algorithm" (2022). — การสร้างโมเดล Institutional Order Flow
10. SmartRisk. "Algorithmic Detection of Order Flow Imbalances in FX Markets" (2021). — การวัด FVG เชิงปริมาณ
11. Axia Futures. "Institutional Order Flow Analysis" (2020). — การตรวจสอบ OB ด้วย Volume

### แหล่งข้อมูล
12. Forex Factory. ป��ิทินเศรษฐกิจสำหรับการจัดแนว Kill Zone กับเหตุการณ์ข่าว
13. CME FedWatch Tool. ความคาดหวังอัตราดอกเบี้ยสำหรับ Macro Bias
14. CoinGlass. ข้อมูลการ Liquidation ของคริปโตสำหรั���การแมป Liquidity Pool
15. TradingView. แพลตฟอร์มวิเคราะห์กราฟและ Backtest

---

*เอกสารนี้เป็นส่วนหนึ่งของฐานความรู้ระบบเทรด Multi-Agent AI ควรอ่านร่วมกับคู่��ือ Wyckoff Market Structure (02_wyckoff_market_structure), คู่มือ Order Flow & Liquidity (03_order_flow_liquidity), และกรอบการจัดการความเสี่ยง (Risk Management)*
