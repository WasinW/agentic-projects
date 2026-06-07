# การเทรดรูปแบบฮาร์โมนิก (Harmonic Patterns) — คู่มือฉบับสมบูรณ์

## ข้อมูลเอกสาร
| ฟิลด์ | ค่า |
|---|---|
| **Strategy ID** | HRM-001 |
| **หมวดหมู่** | การจดจำรูปแบบตาม Fibonacci |
| **สินทรัพย์** | Forex, Crypto, หุ้น, สินค้าโภคภัณฑ์ |
| **ไทม์เฟรม** | M15 ถึง Monthly (หลัก: H1–D1) |
| **ความซับซ้อน** | ขั้นสูง |
| **ความเหมาะสมกับ AI** | สูงมาก — การตรวจจับที่แม่นยำทางคณิตศาสตร์ |
| **เวอร์ชัน** | 2.0 |
| **อัปเดตล่าสุด** | 2026-04-12 |

---

## สารบัญ
1. [บทนำ](#1-บทนำ)
2. [กรอบ XABCD](#2-กรอบ-xabcd)
3. [รูปแบบ Gartley](#3-รูปแบบ-gartley)
4. [รูปแบบ Butterfly](#4-รูปแบบ-butterfly)
5. [รูปแบบ Bat](#5-รูปแบบ-bat)
6. [รูปแบบ Crab](#6-รูปแบบ-crab)
7. [รูปแบบ Shark (0-5 Pattern)](#7-รูปแบบ-shark-0-5-pattern)
8. [รูปแบบ Cypher](#8-รูปแบบ-cypher)
9. [รูปแบบ Three Drives](#9-รูปแบบ-three-drives)
10. [อัลกอริทึมตรวจจับรูปแบบ](#10-อัลกอริทึมตรวจจับรูปแบบ)
11. [การคำนวณ Potential Reversal Zone (PRZ)](#11-การคำนวณ-potential-reversal-zone-prz)
12. [กฎการเข้าและออก](#12-กฎการเข้าและออก)
13. [สูตรทางคณิตศาสตร์](#13-สูตรทางคณิตศาสตร์)
14. [พารามิเตอร์ความเสี่ยง](#14-พารามิเตอร์ความเสี่ยง)
15. [ขั้นตอนการดำเนินการ](#15-ขั้นตอนการดำเนินการ)
16. [หมายเหตุการใช้งาน AI](#16-หมายเหตุการใช้งาน-ai)
17. [เอกสารอ้างอิง](#17-เอกสารอ้างอิง)

---

## 1. บทนำ

การเทรดรูปแบบฮาร์โมนิกเป็นระเบียบวิธีที่ใช้อัตราส่วน Fibonacci เฉพาะเจาะจงในการระบุโซนกลับตัวที่มีศักยภาพในตลาดการเงิน บุกเบิกโดย H.M. Gartley ในปี 1935 และปรับปรุงโดย Scott Carney ในช่วง���ลายทศวรรษ 1990 รูปแบบฮาร์โมนิกให้โครงสร้างราคาที่แม่นยำทางคณิตศาสตร์ ซึ่งเมื่อเสร็จสมบูรณ์จะให้เซ็ตอัปกลับตัวที่มี��วามน่าจะเป็นสูง

### 1.1 ทฤษฎีหลัก

- ตลาดการเงินแสดงโครงสร้างราคา���ชิงเรขาคณิตที่ซ้ำในทุกระดับ Fractal
- โครงสร้างเหล่านี้กำหนดโดยความสัมพันธ์อัตราส่วน Fibonacci เฉพาะระหว่าง��าราคา
- เมื่ออัตราส่วน Fibonacci หลายตัวมาบรรจบกันที่โซนราคาเดียว (Potential Reversal Zone) ความน่าจะเป็นของการกลับตัวจะสูงขึ้นอย่างมีนัยสำคัญ
- ความแม่นยำทางคณิตศาสตร์ของรูปแบบฮาร์โมนิกทำให้เหมาะอย่างยิ่งสำหรับการตรวจจับและดำเนินการโดยอัลกอริทึม

### 1.2 อัตราส่วน Fibonacci ที่ใช้

อัตราส่วน Fibonacci หลักที่ใช้ในรูปแบบฮาร์โมนิก:

| อัตราส่วน | ประเภท | ที่มา |
|-------|------|--------|
| 0.236 | Retracement | ประมาณ $\phi^{-4}$ |
| 0.382 | Retracement | $1 - 0.618$ |
| 0.500 | Retracement | จุดกลาง |
| 0.618 | Retracement | $\phi^{-1} = \frac{\sqrt{5} - 1}{2}$ |
| 0.707 | Retracement | $\frac{1}{\sqrt{2}}$ |
| 0.786 | Retracement | $\sqrt{0.618}$ |
| 0.886 | Retracement | $0.618^{0.618}$ หรือ $\sqrt[4]{0.618}$ |
| 1.000 | Extension | ค่า Unity |
| 1.128 | Extension | $\sqrt[4]{1.618}$ |
| 1.272 | Extension | $\sqrt{1.618}$ |
| 1.414 | Extension | $\sqrt{2}$ |
| 1.618 | Extension | $\phi = \frac{1 + \sqrt{5}}{2}$ |
| 2.000 | Extension | Double |
| 2.240 | Extension | $\sqrt{5}$ |
| 2.618 | Extension | $\phi^2$ |
| 3.618 | Extension | $\phi^2 + 1$ |

### 1.3 ระดับ Tolerance

ไม่มีรูปแบบใดบรรลุอัตราส่วน Fibonacci ที่แน่นอน AI agent ต้องใช้หน้าต่าง Tolerance:

$$\text{Valid} = |R_{\text{actual}} - R_{\text{ideal}}| \leq \epsilon \times R_{\text{ideal}}$$

Tolerance เริ่มต้น: $\epsilon = 0.02$ ถึง $0.05$ (2–5%) ขึ้นอยู่กับอัตราส่วนเฉพาะและไทม์เฟรม

---

## 2. กรอบ XABCD

รูปแบบฮาร์โมนิกทั้งหมด (ยกเว้น Three Drives) ใช้กรอบ XABCD — ห้าจุดเชื่อมต่อด้วย��ี่ขาราคา

### 2.1 นิยามจุด

- **X**: จุดเริ่มต้นของรูปแบบ
- **A**: จุดสิ้นสุดขาอิมพัลส์แรก (ขา XA)
- **B**: จุด Retracement ของขา XA
- **C**: จุด Retracement ของขา AB (ขยายเกิน A สำหรับบางรูปแบบ)
- **D**: จุดเสร็จสมบูรณ์ — Potential Reversal Zone (PRZ)

### 2.2 อัตราส่วนขา

แต่ละรูปแบบกำหนดโดยความสัมพันธ์ Fibonacci ระหว่างขา:

$$R_{AB} = \frac{|B - A|}{|A - X|} \quad \text{(AB retracement of XA)}$$

$$R_{BC} = \frac{|C - B|}{|B - A|} \quad \text{(BC retracement of AB)}$$

$$R_{CD} = \frac{|D - C|}{|C - B|} \quad \text{(CD extension of BC)}$$

$$R_{XD} = \frac{|D - X|}{|A - X|} \quad \text{(XD retracement/extension of XA)}$$

### 2.3 ขาขึ้น vs. ขาลง

- **รูปแบบขาขึ้น (Bullish)**: X เป็นจุดต่ำ, A เป็นจุดสูง → D เสร็จที่จุดต่ำ → คาดว่าราคาจะกลับตัวขึ้น
- **รูปแบบขาลง (Bearish)**: X เป็นจุดสูง, A เป็นจุดต่ำ → D เสร็จที่จุดสูง → คาดว่าราคาจะกลับตัวลง

---

## 3. รูปแบบ Gartley

รูปแบบฮาร์โมนิกดั้งเดิม อธิบายโดย H.M. Gartley ใน "Profits in the Stock Market" (1935) และกำหนดอัตราส่วนที่แน่นอนโดย Scott Carney

### 3.1 ข้อกำหนดอัตราส่วน

| ขา | อัตราส่วน Fibonacci | Tolerance |
|-----|----------------|-----------|
| AB = retracement of XA | **0.618** | 0.582 – 0.654 |
| BC = retracement of AB | **0.382 – 0.886** | 0.362 – 0.906 |
| CD = extension of BC | **1.272 – 1.618** | 1.222 – 1.668 |
| XD = retracement of XA | **0.786** | 0.746 – 0.826 |

### 3.2 อัตราส่วนสำคัญ

**อัตราส่วนหลัก** ของ Gartley คือ $R_{XD} = 0.786$ หากอัตราส่วนนี้ไม่อยู่ใน Tolerance รูปแบบจะไม่ถูกต้องโดยไม่คำนึงถึงอัตราส่วนอื่น

### 3.3 เงื่อนไขทางการ

$$\text{Gartley} = \begin{cases} 0.582 \leq R_{AB} \leq 0.654 \\ 0.362 \leq R_{BC} \leq 0.906 \\ 1.222 \leq R_{CD} \leq 1.668 \\ 0.746 \leq R_{XD} \leq 0.826 \\ B \text{ ไม่เกิน } X \end{cases}$$

### 3.4 องค์ประกอบ PRZ

PRZ ของ Gartley เกิดจากการบรรจบของ:
1. $D = X + 0.786 \times (A - X)$ — XA 0.786 retracement
2. $D = C + R_{CD} \times (B - C)$ — BC extension (1.272 ถึง 1.618)
3. ทางเลือ��: จุดเสร็จ AB=CD

### 3.5 กฎการเทรด

**Bullish Gartley**:
- เข้า: Limit Buy ที่หรือภายใน PRZ
- Stop Loss: ต่ำกว่า X
- TP1: 0.382 retracement ของ AD
- TP2: 0.618 retracement ของ AD
- TP3: จุด A (full AD retracement)

**Bearish Gartley**:
- เข้า: Limit Sell ที่หรือภายใน PRZ
- Stop Loss: เหนือ X
- TP1–TP3: กระจกของเป้าหมายขาขึ้น

### 3.6 อัตราชนะทางประวัติศาสตร์

จากการศึกษาเชิงประจักษ์ (Carney, 2010; Pesavento, 1997):
- Win Rate: 60–70% ด้วยการยืนย���น PRZ ที่เหมาะสม
- Average R:R: 2:1 ถึง 3:1

---

## 4. รูปแบบ Butterfly

ค้นพบโดย Bryce Gilmore และกำหนดโดย Scott Carney Butterfly เป็น **รูปแบบ Extension** ที่ D ขยายเกิน X

### 4.1 ข้อกำหนดอัตราส่วน

| ขา | อัตราส่วน Fibonacci | Tolerance |
|-----|----------------|-----------|
| AB = retracement of XA | **0.786** | 0.746 – 0.826 |
| BC = retracement of AB | **0.382 – 0.886** | 0.362 – 0.906 |
| CD = extension of BC | **1.618 – 2.618** | 1.568 – 2.668 |
| XD = extension of XA | **1.272 หรือ 1.618** | 1.222 – 1.668 |

### 4.2 อัตราส่วนสำคัญ

คุณลักษณะหลักคือ $R_{AB} = 0.786$ และ $R_{XD} \geq 1.272$ จุด D **ต้องขยายเกิน X**

### 4.3 เงื่อนไขทางการ

$$\text{Butterfly} = \begin{cases} 0.746 \leq R_{AB} \leq 0.826 \\ 0.362 \leq R_{BC} \leq 0.906 \\ 1.568 \leq R_{CD} \leq 2.668 \\ 1.222 \leq R_{XD} \leq 1.668 \\ D \text{ ขยายเกิน } X \end{cases}$$

### 4.4 กฎการเทรด

**Bullish Butterfly**:
- เข้า: Limit Buy ที่ PRZ (D ต่ำกว่า X)
- Stop Loss: ต่ำกว่า 1.618 XA extension (หรือ ATR buffer คงที่ต่ำกว่า D)
- TP1: ระดับ B
- TP2: ระดับ A
- TP3: ระดับ C

**หมายเหตุ**: เนื่องจาก D อยู��เกิน X, Stop Loss ใช้ XA extension แทน X เอง ใช้ระดับ Fibonacci extension ถัดไป (เช่น ถ้า D ที่ 1.272 XA, SL ที่ 1.414 XA)

---

## 5. รูปแบบ Bat

ค้นพบโดย Scott Carney ในปี 2001 Bat เป็นรูปแบบ Retracement คล้าย Gartley แต่มีจุด D retracement ที่ลึกกว่า

### 5.1 ข้อกำหนดอัตราส่วน

| ขา | อัตราส่วน Fibonacci | Tolerance |
|-----|----------------|-----------|
| AB = retracement of XA | **0.382 – 0.500** | 0.362 – 0.520 |
| BC = retracement of AB | **0.382 – 0.886** | 0.362 – 0.906 |
| CD = extension of BC | **1.618 – 2.618** | 1.568 – 2.668 |
| XD = retracement of XA | **0.886** | 0.846 – 0.926 |

### 5.2 อัตราส่วนสำคัญ

อัตราส่วนหลักคือ $R_{XD} = 0.886$ เป็นรูปแบบ Retracement ที่ลึกที่สุด (ใน 4 แบบคลาสสิก) และให้ Stop Loss ที่แน่น

### 5.3 กฎการเทรด

**Bullish Bat**:
- เข้า: Limit Buy ที่ PRZ
- Stop Loss: ต่ำกว่า X (แน่น — เพราะ D อยู่ที่ 0.886 ของ XA, SL อยู่ห่างเพียง ~11.4% ของขา XA)
- TP1: 0.382 ของ AD
- TP2: 0.618 ของ AD
- TP3: ระดับ A

**ข้อดี**: Bat ให้ SL ที่แน่นที่สุดในบรรดารูปแบบฮาร์โมนิกคลาสสิกเมื่อเทียบกับผลตอ���แทนที่เป็นไปได้ เหมาะสำหรับผลตอบแทนที่ปรับตามความเสี่ยง

---

## 6. รูปแบบ Crab

ค้นพบโดย Scott Carney ในปี 2000 Crab เป็นรูปแบบ Extension สุดขั้วที่ D อยู่ที่ 1.618 XA extension

### 6.1 ข้อกำหนดอัตราส่วน

| ขา | อัตราส่วน Fibonacci | Tolerance |
|-----|----------------|-----------|
| AB = retracement of XA | **0.382 – 0.618** | 0.362 – 0.638 |
| BC = retracement of AB | **0.382 – 0.886** | 0.362 – 0.906 |
| CD = extension of BC | **2.618 – 3.618** | 2.568 – 3.668 |
| XD = extension of XA | **1.618** | 1.568 – 1.668 |

### 6.2 อัตราส่วนสำคัญ

$R_{XD} = 1.618$ — Golden Ratio Extension เป็นรูปแบบที่สุดขีดที่สุด

### 6.3 Deep Crab Variant

**Deep Crab** มี $R_{AB} = 0.886$ แทน 0.382–0.618:

$$\text{DeepCrab} = \begin{cases} 0.846 \leq R_{AB} \leq 0.926 \\ 0.382 \leq R_{BC} \leq 0.886 \\ 2.000 \leq R_{CD} \leq 3.618 \\ 1.618 \leq R_{XD} \leq 1.668 \end{cases}$$

### 6.4 กฎการเทรด

**Bullish Crab**:
- เข้า: Limit Buy ที่ PRZ
- Stop Loss: ต่ำกว่า 2.000 XA extension (ระดับถัดไปเกิน 1.618)
- TP1: ระดับ B
- TP2: ระดับ A
- TP3: เกิน A (เป้าหมายก้าวร้าวเนื่องจาก Extension ที่สุดขีด)

---

## 7. รูปแบบ Shark (0-5 Pattern)

ค้นพบโดย Scott Carney ในปี 2011 ต่างจากรูปแบบ XABCD อื่นๆ Shark ใช้ระบบป้ายกำกับต่างกัน (0-X-A-B-C) และเทรดจุดสมบูรณ์ของ C แทน D

### 7.1 ข้อกำหนดอัตราส่วน

| ขา | อัตราส่วน Fibonacci | Tolerance |
|-----|----------------|-----------|
| XA = retracement of 0X | ค่าใดก็ได้ | — |
| AB = extension of XA | **1.128 – 1.618** | 1.078 – 1.668 |
| BC = extension of 0X | **0.886 หรือ 1.128** | 0.836 – 1.178 |

### 7.2 กฎการเทรด

**Bullish Shark**:
- เข้า: ที่จุดสมบูรณ์ C (PRZ)
- Stop Loss: ต่ำกว่า 1.272 extension ของ 0X
- TP1: 0.382 retracement ของ BC
- TP2: 0.618 retracement ของ BC

**หมายเหตุ**: Shark มักจะแปรเป็นรูปแบบ 5-0 หลังการกลับตัวเริ่มต้นที่ C รูปแบบ 5-0 ให้โอกาสเทรดรอบที่สอง

---

## 8. รูปแบบ Cypher

พัฒนาโดย Darren Oglesbee Cypher ไม่ได้เป็นส่วนของแค็ตตาล็อกดั้งเดิมของ Carney แต่ได้รับการยอมรับอย่างแพร่หลาย

### 8.1 ข้อกำหนดอัตราส่วน

| ขา | อัตราส่วน Fibonacci | Tolerance |
|-----|----------------|-----------|
| AB = retracement of XA | **0.382 – 0.618** | 0.362 – 0.638 |
| BC = extension of XA | **1.272 – 1.414** | 1.222 – 1.464 |
| CD = retracement of XC | **0.786** | 0.746 – 0.826 |

### 8.2 การคำนวณ PRZ

$$D = C - 0.786 \times (C - X) \quad \text{(สำหรับ Bullish Cypher)}$$
$$D = C + 0.786 \times (X - C) \quad \text{(สำหรับ Bearish Cypher)}$$

### 8.3 กฎการเทรด

**Bullish Cypher**:
- เข้า: Buy ที่ D (0.786 XC retracement)
- Stop Loss: ต่ำกว่า X
- TP1: ระดับ A
- TP2: ระดับ C

**Win Rate**: Cypher ถือเป็นหนึ่งในรูปแบบที่น่าเชื่อถือกว่า โดยมีอัตราชนะเชิงประจักษ์ 55–65%

---

## 9. รูปแบบ Three Drives

รูปแบบ Three Drives มีเอกลักษณ์ — ไม่ตามกรอบ XABCD แต่ประกอบด้วยสามขาอิมพัลส์ต่อเนื���องในทิศทางเดียว คั่นด้วย Fibonacci Retracement

### 9.1 โครงสร้าง

```
Bullish Three Drives (กลับตัวจากขาลงเป็นขาขึ้น):
    Drive 1: Swing high ถึง low (ขาลง)
    Retracement 1: 0.618 หรือ 0.786 ของ Drive 1
    Drive 2: ขยายถึง 1.272 หรือ 1.618 ของ Retracement 1
    Retracement 2: 0.618 หรือ 0.786 ของ Drive 2
    Drive 3: ขยายถึง 1.272 หรือ 1.618 ของ Retracement 2
    → สมบูรณ์ที่ Drive 3 = สัญญาณ BUY

Bearish Three Drives (กลับตัวจากขาขึ้นเป็นขาลง):
    Drive 1: Swing low ถึง high (ขาขึ้น)
    Retracement 1: 0.618 หรือ 0.786 ของ Drive 1
    Drive 2: ขยายถึง 1.272 หรือ 1.618 ของ Retracement 1
    Retracement 2: 0.618 หรือ 0.786 ของ Drive 2
    Drive 3: ขยายถึง 1.272 หรือ 1.618 ของ Retracement 2
    → สมบูรณ์ที่ Drive 3 = สัญญาณ SELL
```

### 9.2 ข้อกำหนดความสมมาตร

สาม Drives ควรม���ค่าใกล้เคียงกันใน:
- **ระยะทางราคา**: $|D_1| \approx |D_2| \approx |D_3|$ (ภายใน 20%)
- **ระยะเวลา**: $T_1 \approx T_2 \approx T_3$ (ภายใน 30%)

$$\text{SymmetryScore} = 1 - \frac{\max(|D_i|) - \min(|D_i|)}{\text{mean}(|D_i|)}$$

ความสมมาตรขั้นต่ำ: $\text{SymmetryScore} \geq 0.70$

---

## 10. อัลกอริทึมตรวจจับรูปแบบ

### 10.1 การระบุจุดสวิง

```python
def find_swing_points(candles, lookback=5, min_swing_size_atr=0.5):
    """
    Identify significant swing highs and lows.
    """
    atr = calculate_atr(candles, 14)
    swings = []
    
    for i in range(lookback, len(candles) - lookback):
        # Check swing high
        is_high = all(candles[i].high >= candles[j].high 
                      for j in range(i - lookback, i + lookback + 1) if j != i)
        
        if is_high:
            prev_low = min(c.low for c in candles[i - lookback:i])
            if (candles[i].high - prev_low) >= min_swing_size_atr * atr[i]:
                swings.append({"index": i, "price": candles[i].high, "type": "HIGH"})
        
        # Check swing low
        is_low = all(candles[i].low <= candles[j].low 
                     for j in range(i - lookback, i + lookback + 1) if j != i)
        
        if is_low:
            next_high = max(c.high for c in candles[i:i + lookback + 1])
            if (next_high - candles[i].low) >= min_swing_size_atr * atr[i]:
                swings.append({"index": i, "price": candles[i].low, "type": "LOW"})
    
    return swings
```

### 10.2 XABCD Pattern Scanner

```python
def scan_harmonic_patterns(swings, tolerance=0.04):
    """
    Scan swing points for all harmonic pattern types.
    Returns a list of detected patterns with metadata.
    """
    patterns = []
    
    for i in range(len(swings) - 4):
        X, A, B, C, D = swings[i], swings[i+1], swings[i+2], swings[i+3], swings[i+4]
        
        # Verify alternating types
        types = [s["type"] for s in [X, A, B, C, D]]
        if not is_alternating(types):
            continue
        
        # Calculate ratios
        XA = abs(A["price"] - X["price"])
        AB = abs(B["price"] - A["price"])
        BC = abs(C["price"] - B["price"])
        CD = abs(D["price"] - C["price"])
        XD = abs(D["price"] - X["price"])
        
        if XA == 0:
            continue
        
        r_AB = AB / XA
        r_BC = BC / AB if AB != 0 else 0
        r_CD = CD / BC if BC != 0 else 0
        r_XD = XD / XA
        
        ratios = {"AB": r_AB, "BC": r_BC, "CD": r_CD, "XD": r_XD}
        
        if check_gartley(ratios, tolerance):
            patterns.append(build_pattern("GARTLEY", X, A, B, C, D, ratios))
        if check_butterfly(ratios, tolerance):
            patterns.append(build_pattern("BUTTERFLY", X, A, B, C, D, ratios))
        if check_bat(ratios, tolerance):
            patterns.append(build_pattern("BAT", X, A, B, C, D, ratios))
        if check_crab(ratios, tolerance):
            patterns.append(build_pattern("CRAB", X, A, B, C, D, ratios))
    
    return patterns


def check_gartley(ratios, tol):
    return (within(ratios["AB"], 0.618, tol) and
            within_range(ratios["BC"], 0.382, 0.886, tol) and
            within_range(ratios["CD"], 1.272, 1.618, tol) and
            within(ratios["XD"], 0.786, tol))


def check_butterfly(ratios, tol):
    return (within(ratios["AB"], 0.786, tol) and
            within_range(ratios["BC"], 0.382, 0.886, tol) and
            within_range(ratios["CD"], 1.618, 2.618, tol) and
            within_range(ratios["XD"], 1.272, 1.618, tol))


def check_bat(ratios, tol):
    return (within_range(ratios["AB"], 0.382, 0.500, tol) and
            within_range(ratios["BC"], 0.382, 0.886, tol) and
            within_range(ratios["CD"], 1.618, 2.618, tol) and
            within(ratios["XD"], 0.886, tol))


def check_crab(ratios, tol):
    return (within_range(ratios["AB"], 0.382, 0.618, tol) and
            within_range(ratios["BC"], 0.382, 0.886, tol) and
            within_range(ratios["CD"], 2.618, 3.618, tol) and
            within(ratios["XD"], 1.618, tol))
```

---

## 11. การคำนวณ Potential Reversal Zone (PRZ)

### 11.1 นิยาม PRZ

PRZ คือโซนราคาที่ Fibonacci Projection หลายตัวจากขาต่างๆ ของรูปแบบมาบรรจบกัน เป็นโซนที่คาดว่าการกลับตัวจะเกิดขึ้น

### 11.2 การตรวจสอบความกว้าง PRZ

$$W_{\text{PRZ}} = \frac{|\text{PRZ\_Upper} - \text{PRZ\_Lower}|}{\text{ATR}(14)}$$

| ความกว้าง PRZ (ATR) | คุณภาพ | การดำเนินการ |
|-----------------|---------|--------|
| $\leq 0.5$ | ยอดเยี่ยม — บรรจบแน่น | เทรดด้วยคว��มมั่นใจ |
| 0.5 – 1.0 | ดี | เทรดด้วยขนาดมาตรฐาน |
| 1.0 – 1.5 | ยอมรับได้ | เทรดด้วยขนาดลด |
| $> 1.5$ | แย่ — ระดับกระจายเกิน | ข้ามหรือรอ LTF refinement |

---

## 12. กฎการเข้าและออก

### 12.1 วิธีการเข้า

**วิธีที่ 1: Limit Order ที่ PRZ (ก้าวร้าว)**
- วาง Limit Order ที่จุดกลาง PRZ
- ข้อดี: จุดเข้าดีที่สุด
- ความเสี่ยง: ไม่มีการยืนยัน; D อาจไม่รับ

**วิธีที่ 2: ยืนยัน��้วยแท่งเทียนที่ PRZ (อนุรักษ์นิยม)**
- รอให้ราคาเข้า PRZ
- รอแท่งเทียนกลับตัว (Pin Bar, Engulfing, Doji) ก่อตัวที่ PRZ
- เข้าเมื่อแท่งเทียนยืนยั��ปิด

**วิธีที่ 3: ยืนยันด้วยโครงสร้าง (อนุรักษ์นิยมที่สุด)**
- รอให้ราคาเข้า PRZ
- รอ Break of Structure (BOS) บนไทม์เฟรมเล็กยืนยันการกลับตัว
- เข้าที่ Pullback หลัง BOS

### 12.2 กฎ Stop Loss

| รูปแบบ | SL (Bullish) | SL (Bearish) |
|---------|----------------------|----------------------|
| Gartley | ต่ำกว่า X | เหนือ X |
| Bat | ต่ำกว่า X (แน่นเพราะ 0.886) | เหนือ X |
| Butterfly | ต่ำกว่า 1.618 XA extension | เหนือ 1.618 XA extension |
| Crab | ต่ำกว่า 2.000 XA extension | เหนือ 2.000 XA extension |
| Cypher | ต่ำกว่า X | เหนือ X |
| Shark | ต่ำกว่า 1.272 ของ 0X extension | เหนือ 1.272 ของ 0X extension |

Buffer: เพิ่ม $0.2 \times \text{ATR}(14)$ ให้ระดับ SL

### 12.3 เป้าหมาย Take Profit

ระดับ TP มาตรฐานสำหรับทุกรูปแบบ (วัดเป็น Retracement ของขา AD):

| เป้าหมาย | ระดั�� Fibonacci ของ AD | การดำเนินการ |
|--------|----------------------|--------|
| TP1 | 0.382 AD | ปิด 40% |
| TP2 | 0.618 AD | ปิด 30% |
| TP3 | ระดับ A (1.0 AD) | ปิด 20% |
| Trail | เกิน A | Trail 10% ที่เหลือ |

### 12.4 R:R ที่คาดหวังตามรูปแบบ

| รูปแบบ | R:R ทั่วไป (ถึง TP1) | R:R ทั่วไป (ถึง TP2) |
|---------|----------------------|----------------------|
| Gartley | 1.5:1 | 3:1 |
| Bat | 2:1 | 4:1 |
| Butterfly | 2:1 | 4:1 |
| Crab | 1.5:1 | 3.5:1 |
| Cypher | 1.5:1 | 3:1 |
| Shark | 1.5:1 | 2.5:1 |
| Three Drives | 2:1 | 3.5:1 |

---

## 13. สูตรทางคณิตศาสตร์

### 13.1 การอนุมานอัตราส่วน Fibonacci

Golden Ratio:
$$\phi = \frac{1 + \sqrt{5}}{2} \approx 1.6180339887$$

การอนุมานสำคัญ:
$$\phi^{-1} = \phi - 1 = \frac{\sqrt{5} - 1}{2} \approx 0.618$$
$$\phi^{-2} = 2 - \phi = \frac{3 - \sqrt{5}}{2} \approx 0.382$$
$$\sqrt{\phi^{-1}} = \sqrt{0.618} \approx 0.786$$
$$\sqrt[4]{0.618} \approx 0.886$$
$$\sqrt{\phi} = \sqrt{1.618} \approx 1.272$$
$$\phi^2 = \phi + 1 \approx 2.618$$

### 13.2 ดัชนีความสมม���ตรของรูปแบบ (Pattern Symmetry Index)

$$\text{TSI} = 1 - \frac{1}{2}\left(\frac{|T_{AB} - T_{CD}|}{\max(T_{AB}, T_{CD})} + \frac{|T_{BC} - T_{AD}/2|}{\max(T_{BC}, T_{AD}/2)}\right)$$

### 13.3 ความหนาแน่นการบรรจบ PRZ

$$\rho_{\text{PRZ}} = \frac{N_{\text{levels}}}{\text{PRZ\_Width} / \text{ATR}}$$

ความหนาแน่นสูงกว่า = PRZ แน่นกว่า = คุณภาพสูงกว่า เป้าหมาย: $\rho_{\text{PRZ}} \geq 3$

### 13.4 มูลค่าที่คาดหวังของเทรดฮาร์โมนิก

$$\text{EV} = P_{\text{complete}} \times [P_{\text{win}} \times \text{Avg\_Win} - (1 - P_{\text{win}}) \times \text{Avg\_Loss}]$$

สำหรับ Gartley ทั่วไปที่มี $P_{\text{complete}} = 0.45$, $P_{\text{win}} = 0.65$, $\text{RR} = 2.5$:

$$\text{EV} = 0.45 \times [0.65 \times 2.5R - 0.35 \times R] = 0.45 \times 1.275R = 0.574R$$

---

## 14. พารามิเตอร์ความเสี่ยง

### 14.1 ขนาด��ำแหน่ง

$$\text{Size} = \frac{\text{Balance} \times R\%}{|E - SL| \times \text{Unit Value}}$$

ความเสี่ยงต่อเทรดตามคะแนนรูปแบบ:

| คะแนนรูปแบบ | Risk % |
|--------------|--------|
| $\geq 0.85$ | 1.5% |
| 0.70 – 0.84 | 1.0% |
| 0.55 – 0.69 | 0.5% |
| $< 0.55$ | ไม่เทรด |

### 14.2 ข้อจำกัดพอร์ต

- เทรดรูปแบบฮาร์โมนิกเปิดพร้อมกันสูงสุด 2 ตำแหน่ง
- ความเสี่ยงพอร์ตรวมจากกลยุทธ์ฮาร์โมนิกสูงสุด 3%
- หลีกเลี่ยงการเทรดรูปแบบประเภทเดียวกันหลายต��วพร้อมกัน
- กระจายข้ามสินทรัพย์ที่ไม่สัมพันธ์กันอย่าง���้อย 2 ตัว

---

## 15. ขั้นตอนการดำเนินการ

### 15.1 Complete Strategy Pseudocode

```python
def harmonic_pattern_strategy():
    """
    Complete harmonic pattern trading strategy.
    """
    
    # PHASE 1: PATTERN DETECTION
    for instrument in watchlist:
        for timeframe in ["D1", "H4", "H1"]:
            candles = fetch_candles(instrument, timeframe, count=300)
            atr = calculate_atr(candles, 14)
            swings = find_swing_points(candles, lookback=5, min_swing_size_atr=0.5)
            completed_patterns = scan_harmonic_patterns(swings, tolerance=0.04)
            forming_patterns = scan_forming_patterns(swings, tolerance=0.04)
            
            for pattern in completed_patterns:
                pattern.score = score_pattern(pattern)
                pattern.prz = calculate_prz(pattern)
    
    # PHASE 2: FILTER AND RANK
    tradeable = [p for p in completed_patterns if p.score >= 0.55]
    tradeable = [p for p in tradeable 
                 if (p.prz["upper"] - p.prz["lower"]) / p.atr <= 1.5]
    tradeable.sort(key=lambda p: p.score, reverse=True)
    
    # PHASE 3: ENTRY EVALUATION
    for pattern in tradeable:
        current_price = get_price(pattern.instrument)
        if not price_near_prz(current_price, pattern.prz, threshold=0.3 * pattern.atr):
            if pattern.score >= 0.70:
                set_limit_order(pattern)
            continue
        
        # Price is at PRZ
        if pattern.score >= 0.85:
            entry = prz_midpoint(pattern)
        else:
            confirmation = check_reversal_candle(pattern, candles)
            if not confirmation:
                continue
            entry = confirmation.price
        
        # PHASE 4: RISK CALCULATION
        sl = calculate_sl(pattern)
        tp1, tp2, tp3 = calculate_targets(pattern)
        rr_tp1 = abs(tp1 - entry) / abs(entry - sl)
        
        if rr_tp1 < 1.5:
            continue
        
        # PHASE 5: EXECUTE
        risk_pct = get_risk_pct(pattern.score)
        position_size = calculate_position_size(balance, risk_pct, entry, sl)
        
        trade = execute_order(
            instrument=pattern.instrument,
            direction="BUY" if pattern.bullish else "SELL",
            entry=entry, sl=sl,
            tp_levels=[
                {"price": tp1, "close_pct": 0.40},
                {"price": tp2, "close_pct": 0.30},
                {"price": tp3, "close_pct": 0.20}
            ],
            size=position_size
        )
        return trade
    
    return WAIT("No actionable harmonic pattern")
```

---

## 16. หมายเหตุการใช้งาน AI

### 16.1 ความซับซ้อนในการคำนวณ

- การตรว��จับสวิง: $O(n \times k)$ โดย $n$ = แท่งเทียน, $k$ = lookback
- การสแกนรูปแบบ: $O(s^5)$ โดย $s$ = จำนวนสวิง (กรณีแย่สุด) แต่เงื่อนไข alternation ลดเป็น $O(s)$
- รวมต่อสินทรัพย์/ไทม์เฟรม: $O(n)$ สำหรับ��รวจจับสวิง + $O(s)$ สำหรับสแกน

### 16.2 การจัดการ False Positive

รูปแบบฮาร์โมนิกอาจสร้า��� False Signal ได้ ลดด้วย:
1. **การจัดแนวเทรนด์ HTF**: เทรดเฉพาะรูปแบบที่สอดคล้องกับเทรนด์���ทม์เฟรมใหญ่
2. **การยืนยันวอลุ่ม**: ถ้ามีข้อมูลวอลุ่ม มองหา Volume Spike ที่ D
3. **RSI/Stochastic Divergence ท��่ D**: เพิ่ม Confluence สำหรับการกลับตัว

### 16.3 ข้อกำหนดข้อมูล

| ไทม์เฟรม | ประวัติขั้นต่ำ | ความถี่อัปเดต |
|-----------|-------------|-----------------|
| Monthly | 10 ปี | รายเดือน |
| Weekly | 3 ปี | รายสัปดาห์ |
| Daily | 1 ปี | รายวัน |
| H4 | 6 เดือน | ทุก 4 ชั่วโมง |
| H1 | 3 เดือน | ทุกชั่วโมง |
| M15 | 1 เดือน | ทุก 15 นาที |

---

## 17. เอกสารอ้างอิง

### หนังสือ
1. Gartley, H. M. (1935). *Profits in the Stock Market*. Lambert-Gann Publishing.
2. Carney, S. (1999). *The Harmonic Trader*. HarmonicTrader.com.
3. Carney, S. (2004). *Harmonic Trading, Volume One*. FT Press.
4. Carney, S. (2007). *Harmonic Trading, Volume Two*. FT Press.
5. Carney, S. (2010). *Harmonic Trading, Volume Three*. FT Press.
6. Pesavento, L. (1997). *Fibonacci Ratios with Pattern Recognition*. Traders Press.
7. Gilmore, B. (2000). *Geometry of Markets*. Bryce Gilmore & Associates.

### บทความวิชาการ
8. Bulkowski, T. N. (2005). "Encyclopedia of Chart Patterns." Wiley.
9. Lo, A. W., Mamaysky, H., & Wang, J. (2000). "Foundations of Technical Analysis." *The Journal of Finance*, 55(4), 1705–1765.
10. Friesen, G. C., Weller, P. A., & Dunham, L. M. (2009). "Price Trends and Patterns in Technical Analysis." *Journal of Banking & Finance*, 33(6), 1089–1100.

### แหล่งข้อมูลจากผู้ปฏิบัติ
11. Oglesbee, D. (2013). "The Cypher Pattern" — AntiPattern LLC.
12. HarmonicTrader.com — แหล่งข้อมูลอย่างเป็นทางการของ Scott Carney
13. TradingView. "Harmonic Pattern Indicators" — เครื่องมือตรวจจับจากชุมชน
14. Investopedia. "Harmonic Patterns in the Currency Markets"

---

*เอกสารนี้เป็นส่วนหนึ่งของฐานความรู้ระบบเทรด Multi-Agent AI ควรอ่านร่วมกับคู่มือ Fibonacci Advanced (12_fibonacci_advanced) และคู่มือ Price Action (07_price_action)*
