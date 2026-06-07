# การเทรดด้วยรูปแบบราคา (Price Action Trading) — คู่มือฉบับสมบูรณ์

## ข้อมูลเอกสาร (Document Metadata)
| ฟิลด์ | ค่า |
|---|---|
| **รหัสกลยุทธ์ (Strategy ID)** | PA-001 |
| **หมวดหมู่ (Category)** | การวิเคราะห์ทางเทคนิค / รูปแบบราคาล้วน (Technical Analysis / Pure Price Action) |
| **ประเภทสินทรัพย์ (Asset Classes)** | Forex, Crypto, หุ้น (Equities), สินค้าโภคภัณฑ์ (Commodities) |
| **กรอบเวลา (Timeframes)** | M5 ถึง Monthly (หลัก: H1–D1) |
| **ความซับซ้อน (Complexity)** | ระดับกลาง (Intermediate) |
| **ความเหมาะสมกับ AI** | สูง — การจดจำรูปแบบสามารถทำได้ด้วยอัลกอริทึม |
| **เวอร์ชัน** | 2.0 |
| **อัปเดตล่าสุด** | 2026-04-12 |

---

## สารบัญ
1. [บทนำ](#1-บทนำ)
2. [รูปแบบแท่งเทียน — แท่งเดียว](#2-รูปแบบแท่งเทียน--แท่งเดียว)
3. [รูปแบบแท่งเทียน — หลายแท่ง](#3-รูปแบบแท่งเทียน--หลายแท่ง)
4. [รูปแบบกราฟ — กลับตัว](#4-รูปแบบกราฟ--กลับตัว)
5. [รูปแบบกราฟ — ต่อเนื่อง](#5-รูปแบบกราฟ--ต่อเนื่อง)
6. [เส้นแนวโน้มและช่องราคา](#6-เส้นแนวโน้มและช่องราคา)
7. [การระบุแนวรับแนวต้าน](#7-การระบุแนวรับแนวต้าน)
8. [อัลกอริทึมจดจำรูปแบบ](#8-อัลกอริทึมจดจำรูปแบบ)
9. [ตรรกะการเข้าและออกจุด](#9-ตรรกะการเข้าและออกจุด)
10. [สถิติอัตราชนะ](#10-สถิติอัตราชนะ)
11. [แบบจำลองทางคณิตศาสตร์](#11-แบบจำลองทางคณิตศาสตร์)
12. [พารามิเตอร์ความเสี่ยง](#12-พารามิเตอร์ความเสี่ยง)
13. [ขั้นตอนการดำเนินงาน](#13-ขั้นตอนการดำเนินงาน)
14. [หมายเหตุการใช้งาน AI](#14-หมายเหตุการใช้งาน-ai)
15. [อ้างอิง](#15-อ้างอิง)

---

## 1. บทนำ

การเทรดด้วยรูปแบบราคา (Price Action Trading) คือวินัยในการตัดสินใจซื้อขายโดยอาศัยเฉพาะการเคลื่อนไหวของราคาดิบที่แสดงบนกราฟ โดยไม่พึ่งพาอินดิเคเตอร์ที่มีความล่าช้า แท่งเทียนทุกแท่ง ทุกจังหวะแกว่ง และทุกรูปแบบกราฟ ล้วนเล่าเรื่องราวของการต่อสู้ระหว่างผู้ซื้อและผู้ขาย

### 1.1 ปรัชญาหลัก

- ราคาคืออินดิเคเตอร์สูงสุด — มันสะท้อนข้อมูลทั้งหมดที่ทราบ
- รูปแบบแท่งเทียนเปิดเผยจิตวิทยาของผู้เข้าร่วมตลาด
- รูปแบบกราฟแสดงถึงธรรมชาติแบบเศษส่วน (Fractal) ของความไม่สมดุลระหว่างอุปสงค์/อุปทาน
- บริบท (แนวโน้ม, ตำแหน่งเทียบกับ S/R) สำคัญกว่ารูปแบบใดรูปแบบหนึ่ง

### 1.2 กรอบการประเมินบริบท (Context Framework)

สัญญาณรูปแบบราคาทุกสัญญาณต้องได้รับการประเมินภายในบริบท:

$$\text{Signal Quality} = f(\text{Pattern}, \text{Trend}, \text{Location}, \text{Momentum})$$

- **รูปแบบ (Pattern)**: รูปแบบแท่งเทียนหรือรูปแบบกราฟเฉพาะ
- **แนวโน้ม (Trend)**: สัญญาณนั้นไปตามหรือสวนทางกับแนวโน้มหลัก?
- **ตำแหน่ง (Location)**: สัญญาณนั้นอยู่ที่ระดับสำคัญหรือไม่ (S/R, ตัวเลขกลมๆ)?
- **โมเมนตัม (Momentum)**: สัญญาณนั้นมีแรงตามมาแข็งแกร่งหรืออ่อนแอ?

---

## 2. รูปแบบแท่งเทียน — แท่งเดียว

### 2.1 แท่งเทียนพินบาร์ (Pin Bar) / แท่งค้อน (Hammer) / ดาวตก (Shooting Star)

**โครงสร้าง**:
- ไส้เทียน (Shadow) ยาวในทิศทางเดียว — อย่างน้อย 2 เท่าของความยาวตัวเทียน
- ตัวเทียนเล็กอยู่ด้านตรงข้ามของช่วงราคา
- บ่งชี้การปฏิเสธระดับราคา

**พินบาร์ขาขึ้น (Bullish Pin Bar / Hammer)**:
- ไส้เทียนล่างยาว
- ตัวเทียนเล็กอยู่ใกล้ยอดแท่ง
- ราคาปิดอาจเป็นขาขึ้นหรือขาลง (ขาขึ้นดีกว่า)

**เกณฑ์การตรวจจับ**:
$$\text{BullishPin} = \begin{cases} \text{LowerWick} \geq 2 \times \text{Body} \\ \text{UpperWick} \leq 0.25 \times \text{TotalRange} \\ \text{Body} \leq 0.33 \times \text{TotalRange} \end{cases}$$

โดยที่:
$$\text{Body} = |C - O|$$
$$\text{LowerWick} = \min(O, C) - L$$
$$\text{UpperWick} = H - \max(O, C)$$
$$\text{TotalRange} = H - L$$

**พินบาร์ขาลง (Bearish Pin Bar / Shooting Star)**:
$$\text{BearishPin} = \begin{cases} \text{UpperWick} \geq 2 \times \text{Body} \\ \text{LowerWick} \leq 0.25 \times \text{TotalRange} \\ \text{Body} \leq 0.33 \times \text{TotalRange} \end{cases}$$

**ปัจจัยเสริมความแข็งแกร่งของสัญญาณ**:
- ไส้เทียนทะลุระดับ S/R สำคัญ: +30% ความมั่นใจ
- ช่วงราคาพินบาร์ > 1.5 ATR: สัญญาณปฏิเสธที่แข็งแกร่ง
- พินบาร์อยู่ที่จุดสูงสุด/ต่ำสุดของวัน: +20% ความมั่นใจ
- ปลายไส้เทียนทะลุเกินช่วงราคาแท่งก่อนหน้า: +25% ความมั่นใจ

### 2.2 โดจิ (Doji)

**โครงสร้าง**: ราคาเปิดและปิดเกือบเท่ากัน (ตัวเทียน $\leq$ 10% ของช่วงราคา)

**ประเภท**:

| ประเภทโดจิ | เงื่อนไข | สัญญาณ |
|-----------|-----------|--------|
| **โดจิมาตรฐาน (Standard Doji)** | ตัวเทียน $\leq 10\%$ ของช่วงราคา, ไส้เทียนยาวเท่าๆ กัน | ลังเล (Indecision) |
| **โดจิแมลงปอ (Dragonfly Doji)** | ไส้เทียนล่างยาว, ไม่มีไส้เทียนบน | ขาขึ้น (ที่จุดต่ำ) |
| **โดจิป่าช้า (Gravestone Doji)** | ไส้เทียนบนยาว, ไม่มีไส้เทียนล่าง | ขาลง (ที่จุดสูง) |
| **โดจิขายาว (Long-Legged Doji)** | ไส้เทียนทั้งสองยาว, ตัวเทียนจิ๋ว | ลังเลสุดขีด / กลับตัว |

**การตรวจจับ**:
$$\text{Doji} = \frac{|C - O|}{H - L} \leq 0.10$$

$$\text{DragonflyDoji} = \text{Doji} \text{ AND } \frac{H - \max(O,C)}{H - L} \leq 0.10$$

$$\text{GravestoneDoji} = \text{Doji} \text{ AND } \frac{\min(O,C) - L}{H - L} \leq 0.10$$

### 2.3 มารุโบซุ (Marubozu)

**โครงสร้าง**: แท่งเทียนเต็มตัวโดยมีไส้เทียนน้อยมากหรือไม่มีเลย — บ่งชี้ความมุ่งมั่นในทิศทางที่แข็งแกร่ง

$$\text{Marubozu} = \frac{|C - O|}{H - L} \geq 0.90$$

**มารุโบซุขาขึ้น (Bullish Marubozu)**: $C \gg O$, ไม่มีไส้เทียนบน/ล่าง แสดงโมเมนตัมซื้อที่แข็งแกร่ง
**มารุโบซุขาลง (Bearish Marubozu)**: $O \gg C$, ไม่มีไส้เทียนบน/ล่าง แสดงโมเมนตัมขายที่แข็งแกร่ง

### 2.4 ลูกข่าง (Spinning Top)

**โครงสร้าง**: ตัวเทียนเล็กมีไส้เทียนทั้งสองด้าน (ยาวกว่าตัวเทียนแต่ไม่สุดโต่งเท่าโดจิ)

$$\text{SpinningTop} = 0.10 < \frac{|C - O|}{H - L} \leq 0.33 \quad \text{AND} \quad \text{UpperWick} > \text{Body} \quad \text{AND} \quad \text{LowerWick} > \text{Body}$$

**สัญญาณ**: ลังเล; แนวโน้มอ่อนตัว มีประโยชน์มากที่สุดหลังจากแนวโน้มแข็งแกร่ง

---

## 3. รูปแบบแท่งเทียน — หลายแท่ง

### 3.1 รูปแบบกลืน (Engulfing Pattern)

**กลืนขาขึ้น (Bullish Engulfing)**:
- แท่ง 1: ขาลง (ตัวแดง/ดำ)
- แท่ง 2: ขาขึ้น (ตัวเขียว/ขาว) ที่กลืนตัวเทียนของแท่ง 1 ทั้งหมด

$$\text{BullishEngulfing} = \begin{cases} O_1 > C_1 \quad \text{(แท่ง 1 เป็นขาลง)} \\ C_2 > O_2 \quad \text{(แท่ง 2 เป็นขาขึ้น)} \\ O_2 \leq C_1 \quad \text{(เปิดแท่ง 2 อยู่ที่หรือต่ำกว่าปิดแท่ง 1)} \\ C_2 \geq O_1 \quad \text{(ปิดแท่ง 2 อยู่ที่หรือสูงกว่าเปิดแท่ง 1)} \end{cases}$$

**กลืนขาลง (Bearish Engulfing)**:
$$\text{BearishEngulfing} = \begin{cases} C_1 > O_1 \quad \text{(แท่ง 1 เป็นขาขึ้น)} \\ O_2 > C_2 \quad \text{(แท่ง 2 เป็นขาลง)} \\ O_2 \geq C_1 \quad \text{(เปิดแท่ง 2 อยู่ที่หรือสูงกว่าปิดแท่ง 1)} \\ C_2 \leq O_1 \quad \text{(ปิดแท่ง 2 อยู่ที่หรือต่ำกว่าเปิดแท่ง 1)} \end{cases}$$

**การเพิ่มคุณภาพ**: แท่งกลืนควรกลืนช่วงราคาทั้งหมด (สูง-ต่ำ) ของแท่ง 1 ด้วย ไม่ใช่แค่ตัวเทียน นี่เรียกว่า "การกลืนแบบเต็ม (Full Engulfing)"

### 3.2 แท่งเทียนภายใน (Inside Bar)

**โครงสร้าง**: ช่วงราคาทั้งหมดของแท่ง 2 (สูง-ต่ำ) อยู่ภายในช่วงราคาของแท่ง 1

$$\text{InsideBar} = H_2 \leq H_1 \quad \text{AND} \quad L_2 \geq L_1$$

**สัญญาณ**: การบีบอัด/การพักตัว เทรดตามทิศทางการทะลุ

**กฎการเข้า**:
- **ซื้อ (Long)**: Buy stop เหนือ $H_1$ (จุดสูงของแท่งแม่)
- **ขาย (Short)**: Sell stop ต่ำกว่า $L_1$ (จุดต่ำของแท่งแม่)
- **SL**: ด้านตรงข้ามของแท่งแม่

**การซ้อนกัน**: แท่งเทียนภายในหลายแท่งติดต่อกัน ("Inside Bar Coil") บีบอัดความผันผวนมากขึ้น นำไปสู่การทะลุที่รุนแรง

### 3.3 แท่งเทียนภายนอก (Outside Bar / Engulfing Range)

**โครงสร้าง**: ช่วงราคาของแท่ง 2 กลืนช่วงราคาของแท่ง 1 ทั้งหมด

$$\text{OutsideBar} = H_2 > H_1 \quad \text{AND} \quad L_2 < L_1$$

**สัญญาณ**: โมเมนตัมแข็งแกร่ง เทรดไปในทิศทางของราคาปิดแท่งเทียนภายนอก

### 3.4 ดาวรุ่ง / ดาวค่ำ (Morning Star / Evening Star)

**ดาวรุ่ง (Morning Star) — กลับตัวขาขึ้น** — รูปแบบสามแท่ง:
1. แท่ง 1: แท่งเทียนขาลงขนาดใหญ่
2. แท่ง 2: แท่งเทียนตัวเล็ก (ดาว) ที่เปิดช่องว่างต่ำกว่าราคาปิดแท่ง 1 ในตลาด Forex/Crypto (ไม่มี Gap) ตัวเทียนของดาวควรเล็กและอยู่ต่ำกว่าราคาปิดแท่ง 1
3. แท่ง 3: แท่งเทียนขาขึ้นขนาดใหญ่ปิดเหนือจุดกึ่งกลางของแท่ง 1

$$\text{MorningStar} = \begin{cases} |C_1 - O_1| > 0.7 \times \text{ATR} \quad \text{(แท่งขาลงขนาดใหญ่)} \\ |C_2 - O_2| < 0.3 \times |C_1 - O_1| \quad \text{(ตัวเทียนเล็ก)} \\ C_3 > \frac{O_1 + C_1}{2} \quad \text{(ปิดเหนือจุดกึ่งกลางแท่ง 1)} \\ C_3 > O_3 \quad \text{(แท่ง 3 เป็นขาขึ้น)} \end{cases}$$

**ดาวค่ำ (Evening Star) — กลับตัวขาลง**: เป็นภาพสะท้อนกลับ

### 3.5 สามทหารขาว / สามอีกาดำ (Three White Soldiers / Three Black Crows)

**สามทหารขาว (Three White Soldiers)**:
- แท่งเทียนขาขึ้นสามแท่งติดต่อกัน
- แต่ละแท่งเปิดภายในตัวเทียนของแท่งก่อนหน้า
- แต่ละแท่งปิดใกล้จุดสูงสุด (ไส้เทียนบนสั้น)
- ราคาปิดของแต่ละแท่งสูงกว่าราคาปิดแท่งก่อนหน้า

$$\text{ThreeWhiteSoldiers} = \begin{cases} C_i > O_i \quad \forall i \in \{1, 2, 3\} \\ O_{i+1} > O_i \text{ AND } O_{i+1} < C_i \quad \forall i \in \{1, 2\} \\ C_{i+1} > C_i \quad \forall i \in \{1, 2\} \\ (H_i - C_i) < 0.25 \times (C_i - O_i) \quad \forall i \quad \text{(ไส้เทียนบนสั้น)} \end{cases}$$

**สามอีกาดำ (Three Black Crows)**: ภาพสะท้อนกลับ (แท่งเทียนขาลงขนาดใหญ่สามแท่งติดต่อกัน)

### 3.6 แหนบบน / แหนบล่าง (Tweezer Top / Bottom)

**แหนบล่าง (Tweezer Bottom) — ขาขึ้น**:
- แท่งเทียนสองแท่งขึ้นไปที่มีจุดต่ำสุดเท่ากันโดยประมาณ
- เกิดที่แนวรับหรือหลังจากแนวโน้มขาลง

$$\text{TweezerBottom} = |L_1 - L_2| \leq 0.05 \times \text{ATR}$$

**แหนบบน (Tweezer Top) — ขาลง**:
$$\text{TweezerTop} = |H_1 - H_2| \leq 0.05 \times \text{ATR}$$

### 3.7 ฮารามิ (Harami / Inside Day)

**ฮารามิขาขึ้น (Bullish Harami)**:
- แท่ง 1: แท่งเทียนขาลงขนาดใหญ่
- แท่ง 2: แท่งเทียนขาขึ้นขนาดเล็กที่ตัวเทียนอยู่ภายในตัวเทียนแท่ง 1 ทั้งหมด

$$\text{BullishHarami} = \begin{cases} O_1 > C_1 \quad \text{(แม่เป็นขาลง)} \\ C_2 > O_2 \quad \text{(ลูกเป็นขาขึ้น)} \\ O_2 > C_1 \text{ AND } C_2 < O_1 \quad \text{(ตัวลูกอยู่ภายในตัวแม่)} \end{cases}$$

---

## 4. รูปแบบกราฟ — กลับตัว (Chart Patterns — Reversal)

### 4.1 ศีรษะและไหล่ (Head and Shoulders)

**โครงสร้าง**:
- ไหล่ซ้าย (Left Shoulder): จุดสูงแกว่งตามด้วยการดึงกลับ
- ศีรษะ (Head): จุดสูงแกว่งที่สูงกว่า ตามด้วยการดึงกลับมาประมาณระดับเดียวกับจุดดึงกลับแรก
- ไหล่ขวา (Right Shoulder): จุดสูงแกว่งที่ต่ำกว่า (ประมาณเท่ากับไหล่ซ้าย) ตามด้วยการทะลุใต้เส้นคอ (Neckline)

**เส้นคอ (Neckline)**: เส้นที่เชื่อมจุดต่ำของการดึงกลับสองจุด (ระหว่างไหล่ซ้าย-ศีรษะ และศีรษะ-ไหล่ขวา)

**อัลกอริทึมการตรวจจับ**:
```python
def detect_head_shoulders(swings, tolerance_pct=0.03):
    """
    Detect Head and Shoulders top pattern.
    """
    patterns = []
    
    # Need at least 5 alternating swings: H-L-H-L-H (High-Low-High-Low-High)
    highs = [s for s in swings if s["type"] == "HIGH"]
    lows = [s for s in swings if s["type"] == "LOW"]
    
    for i in range(len(highs) - 2):
        ls, head, rs = highs[i], highs[i+1], highs[i+2]
        
        # Head must be higher than both shoulders
        if not (head["price"] > ls["price"] and head["price"] > rs["price"]):
            continue
        
        # Shoulders should be approximately equal
        shoulder_diff = abs(ls["price"] - rs["price"]) / ls["price"]
        if shoulder_diff > tolerance_pct:
            continue
        
        # Find neckline lows (between LS-Head and Head-RS)
        nl_left = find_low_between(lows, ls["index"], head["index"])
        nl_right = find_low_between(lows, head["index"], rs["index"])
        
        if nl_left is None or nl_right is None:
            continue
        
        # Neckline
        neckline_slope = (nl_right["price"] - nl_left["price"]) / (nl_right["index"] - nl_left["index"])
        neckline_at_rs = nl_left["price"] + neckline_slope * (rs["index"] - nl_left["index"])
        
        patterns.append({
            "type": "HEAD_AND_SHOULDERS",
            "direction": "BEARISH",
            "left_shoulder": ls,
            "head": head,
            "right_shoulder": rs,
            "neckline_left": nl_left,
            "neckline_right": nl_right,
            "neckline_slope": neckline_slope,
            "target": neckline_at_rs - (head["price"] - neckline_at_rs),  # Measured move
            "quality": calculate_hs_quality(ls, head, rs, nl_left, nl_right)
        })
    
    return patterns
```

**การคำนวณเป้าหมาย (Measured Move)**:
$$\text{Target} = \text{Neckline} - (\text{Head} - \text{Neckline})$$

**ศีรษะและไหล่กลับหัว (Inverse Head and Shoulders)** — กลับตัวขาขึ้น: เป็นภาพสะท้อนกลับ

### 4.2 ดับเบิ้ลท็อป (Double Top)

**โครงสร้าง**: จุดสูงแกว่งสองจุดที่ระดับเดียวกันโดยประมาณ คั่นด้วยการดึงกลับ

**การตรวจจับ**:
$$\text{DoubleTop} = \begin{cases} |H_1 - H_2| \leq 0.02 \times H_1 \\ \text{การดึงกลับระหว่างยอด} \geq 0.10 \times (H_1 - \text{prior\_low}) \\ H_2 \text{ ไม่สามารถเกิน } H_1 \text{ ได้อย่างมั่นใจ} \end{cases}$$

**การเข้า**: ขาย (Short) เมื่อทะลุต่ำกว่าจุดต่ำของการดึงกลับ (เส้นคอ)
**เป้าหมาย**: เส้นคอ - (ยอด - เส้นคอ)

### 4.3 ดับเบิ้ลบอทท่อม (Double Bottom)

**โครงสร้าง**: จุดต่ำแกว่งสองจุดที่ระดับเดียวกันโดยประมาณ

$$\text{DoubleBottom} = |L_1 - L_2| \leq 0.02 \times L_1$$

**การเข้า**: ซื้อ (Long) เมื่อทะลุเหนือจุดสูงของการดึงกลับ
**เป้าหมาย**: เส้นคอ + (เส้นคอ - ก้น)

### 4.4 ทริปเปิ้ลท็อป / ทริปเปิ้ลบอทท่อม (Triple Top / Triple Bottom)

การทดสอบระดับเดียวกันโดยประมาณสามครั้ง ตรรกะเดียวกับ Double Top/Bottom แต่มีการสัมผัสเพิ่มอีกหนึ่งครั้ง ความน่าเชื่อถือสูงกว่าเนื่องจากยืนยันแนวต้าน/แนวรับ

### 4.5 ก้นจานกลม (Rounding Bottom / Saucer)

การเปลี่ยนผ่านทีละน้อยจากขาลงเป็นขาขึ้น สร้างรูปร่าง U ตลอดหลายแท่งเทียน (30–100+) เหมาะที่สุดกับกรอบเวลา Daily และ Weekly

**การตรวจจับ**: ใช้การปรับเส้นโค้ง (Curve Fitting) — ปรับฟังก์ชันกำลังสองกับจุดต่ำสุดและตรวจสอบอนุพันธ์อันดับสองเป็นบวก (ความเว้า)

$$L_i \approx a(i - i_{\text{center}})^2 + L_{\text{min}}$$

โดยที่ $a > 0$ บ่งชี้ก้นจานกลม

---

## 5. รูปแบบกราฟ — ต่อเนื่อง (Chart Patterns — Continuation)

### 5.1 สามเหลี่ยม (Triangles)

**สามเหลี่ยมขาขึ้น (Ascending Triangle) — ขาขึ้น**:
- แนวต้านราบ (ขอบบนแนวนอน)
- แนวรับขึ้น (ขอบล่างขึ้น)
- ราคาบีบอัดเข้าหาจุดยอด
- คาดว่าจะทะลุขึ้น

**การตรวจจับ**:
```python
def detect_ascending_triangle(swings, candles, min_touches=2):
    highs = [s for s in swings if s["type"] == "HIGH"]
    lows = [s for s in swings if s["type"] == "LOW"]
    
    # Flat resistance: highs at approximately the same level
    if len(highs) < min_touches:
        return None
    
    resistance_level = np.mean([h["price"] for h in highs[-min_touches:]])
    resistance_flat = all(
        abs(h["price"] - resistance_level) / resistance_level < 0.01 
        for h in highs[-min_touches:]
    )
    
    # Rising support: lows forming an ascending trendline
    if len(lows) < min_touches:
        return None
    
    slope, intercept = np.polyfit(
        [l["index"] for l in lows[-min_touches:]], 
        [l["price"] for l in lows[-min_touches:]], 1
    )
    rising_support = slope > 0
    
    if resistance_flat and rising_support:
        return {
            "type": "ASCENDING_TRIANGLE",
            "resistance": resistance_level,
            "support_slope": slope,
            "support_intercept": intercept,
            "target": resistance_level + (resistance_level - lows[-1]["price"])
        }
    
    return None
```

**สามเหลี่ยมขาลง (Descending Triangle) — ขาลง**: แนวรับราบ + แนวต้านลง

**สามเหลี่ยมสมมาตร (Symmetrical Triangle) — เป็นกลาง**: ขอบทั้งสองบรรจบกัน ไม่ทราบทิศทางการทะลุ; เทรดตามทิศทางที่ทะลุ

### 5.2 ลิ่ม (Wedges)

**ลิ่มขาขึ้น (Rising Wedge) — ขาลง**:
- ทั้งเส้นแนวรับและแนวต้านลาดขึ้น
- เส้นแนวรับชันกว่าเส้นแนวต้าน (บรรจบ)
- มักจะทะลุลง

**ลิ่มขาลง (Falling Wedge) — ขาขึ้น**:
- ทั้งสองเส้นลาดลง
- เส้นแนวต้านชันกว่าเส้นแนวรับ
- มักจะทะลุขึ้น

**การตรวจจับ**: ปรับเส้นตรง (Linear Regression) กับจุดสูงแกว่งและจุดต่ำแกว่งแยกกัน แล้วเปรียบเทียบความชัน

$$\text{RisingWedge} = \begin{cases} \text{Slope}_{\text{highs}} > 0 \\ \text{Slope}_{\text{lows}} > 0 \\ \text{Slope}_{\text{lows}} > \text{Slope}_{\text{highs}} \quad \text{(บรรจบ)} \end{cases}$$

### 5.3 ธง (Flags)

**ธงกระทิง (Bull Flag)**:
- การเคลื่อนตัวแรง (Impulse) ขึ้น (เสาธง / "Pole")
- ช่องพักตัวแคบลาดลง (ผืนธง / "Flag")
- การทะลุเหนือธงต่อเนื่องแนวโน้มขาขึ้น

**การตรวจจับ**:
$$\text{BullFlag} = \begin{cases} \text{Pole}: |\text{impulse}| > 2 \times \text{ATR}(14) \text{ ภายใน } \leq 5 \text{ แท่ง} \\ \text{Flag}: \text{การพักตัวที่มีความชันลง, ช่วง} < 50\% \text{ ของเสาธง} \\ \text{Duration}: \text{ธง } \leq 20 \text{ แท่ง} \end{cases}$$

**ธงหมี (Bear Flag)**: ภาพสะท้อนกลับ (เสาธงลง, ธงลาดขึ้น)

**เป้าหมาย**: ความสูงเสาธงฉายจากจุดทะลุ
$$\text{Target} = \text{Breakout Level} + |\text{Pole Height}|$$

### 5.4 ธงสามเหลี่ยม (Pennants)

คล้ายกับธงแต่การพักตัวเป็นสามเหลี่ยมสมมาตรขนาดเล็กแทนที่จะเป็นช่องขนาน

**การตรวจจับ**: เหมือนกับธงแต่ขอบบรรจบกันแทนที่จะขนาน

### 5.5 ถ้วยและหูจับ (Cup and Handle)

**โครงสร้าง**:
- **ถ้วย (Cup)**: รูปแบบก้นจานกลม (รูปร่าง U)
- **หูจับ (Handle)**: การดึงกลับเล็กน้อย (ธงหรือธงสามเหลี่ยม) หลังจากถ้วยเสร็จ
- การทะลุเหนือจุดสูงของหูจับ = จุดเข้า

**เป้าหมาย**:
$$\text{Target} = \text{Cup Rim} + \text{Cup Depth}$$

**การตรวจจับ**: ปรับเส้นพาราโบลากับจุดต่ำสุดของถ้วย ตรวจสอบว่าหูจับเกิดที่ระดับขอบถ้วย

---

## 6. เส้นแนวโน้มและช่องราคา (Trend Lines and Channels)

### 6.1 การสร้างเส้นแนวโน้ม

**เส้นแนวโน้มขาขึ้น (Uptrend Line)**: เชื่อมจุดต่ำแกว่งสำคัญสองจุดขึ้นไปด้วยเส้นตรง
**เส้นแนวโน้มขาลง (Downtrend Line)**: เชื่อมจุดสูงแกว่งสำคัญสองจุดขึ้นไปด้วยเส้นตรง

**อัลกอริทึม (Least Squares with Outlier Rejection)**:
```python
def fit_trendline(swing_points, type="support", max_violations=1):
    """
    Fit a trendline through swing points using iterative RANSAC-like approach.
    """
    if type == "support":
        points = [(s["index"], s["price"]) for s in swing_points if s["type"] == "LOW"]
    else:
        points = [(s["index"], s["price"]) for s in swing_points if s["type"] == "HIGH"]
    
    if len(points) < 2:
        return None
    
    best_line = None
    best_inliers = 0
    
    # Try all pairs
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            x1, y1 = points[i]
            x2, y2 = points[j]
            
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            
            # Count inliers (points close to the line)
            inliers = 0
            violations = 0
            
            for px, py in points:
                line_y = slope * px + intercept
                distance = py - line_y if type == "support" else line_y - py
                
                if distance >= -0.001 * abs(line_y):  # On or above for support
                    inliers += 1
                else:
                    violations += 1
            
            if violations <= max_violations and inliers > best_inliers:
                best_inliers = inliers
                best_line = {"slope": slope, "intercept": intercept, "touches": inliers}
    
    return best_line
```

### 6.2 การสร้างช่องราคา (Channel Construction)

ช่องราคาประกอบด้วยเส้นแนวโน้มขนานสองเส้น:
- **ช่องขาขึ้น (Ascending Channel)**: เส้นแนวรับ (ล่าง) + เส้นแนวต้านขนาน (บน)
- **ช่องขาลง (Descending Channel)**: เส้นแนวต้าน (บน) + เส้นแนวรับขนาน (ล่าง)

**ความกว้างช่อง**:
$$W_{\text{channel}} = \frac{|y_{\text{upper}} - y_{\text{lower}}|_{\text{at any x}}}{\cos(\theta)}$$

โดยที่ $\theta = \arctan(\text{slope})$

### 6.3 กฎการเทรดด้วยเส้นแนวโน้ม

| สัญญาณ | จุดเข้า | SL | TP |
|--------|-------|-----|-----|
| แนวโน้มเด้ง (แนวรับ) | ซื้อที่เส้นแนวโน้ม + Buffer | ใต้เส้นแนวโน้ม 1 ATR | ขอบตรงข้ามของช่อง |
| เส้นแนวโน้มหัก (แนวรับ) | ขายเมื่อรีเทสต์เส้นแนวโน้มที่หัก | เหนือเส้นแนวโน้มที่หัก 1 ATR | Measured Move (ความกว้างช่องฉายลง) |
| ถูกปฏิเสธที่ด้านบนช่อง | ขายที่ขอบบน | เหนือขอบบน 0.5 ATR | ขอบล่างของช่อง |

---

## 7. การระบุแนวรับแนวต้าน (Support and Resistance Identification)

### 7.1 อัลกอริทึม: S/R แบบคลัสเตอร์

```python
def identify_sr_levels(candles, lookback=200, min_touches=3, cluster_threshold_atr=0.3):
    """
    Identify significant support/resistance levels using price clustering.
    """
    atr = calculate_atr(candles, 14)[-1]
    
    # Collect all swing highs and lows
    swings = find_swing_points(candles[-lookback:], lookback=5)
    
    # Collect all significant price levels
    levels = [s["price"] for s in swings]
    
    # Add open/close of large-bodied candles
    for c in candles[-lookback:]:
        if abs(c.close - c.open) > 1.5 * atr:
            levels.extend([c.open, c.close])
    
    # Cluster nearby levels
    clusters = []
    levels.sort()
    
    current_cluster = [levels[0]]
    for i in range(1, len(levels)):
        if levels[i] - levels[i-1] <= cluster_threshold_atr * atr:
            current_cluster.append(levels[i])
        else:
            if len(current_cluster) >= min_touches:
                clusters.append({
                    "level": np.median(current_cluster),
                    "touches": len(current_cluster),
                    "strength": len(current_cluster) / min_touches
                })
            current_cluster = [levels[i]]
    
    # Don't forget the last cluster
    if len(current_cluster) >= min_touches:
        clusters.append({
            "level": np.median(current_cluster),
            "touches": len(current_cluster),
            "strength": len(current_cluster) / min_touches
        })
    
    return sorted(clusters, key=lambda x: x["strength"], reverse=True)
```

### 7.2 ปัจจัยความแข็งแกร่งของ S/R

$$S_{\text{SR}} = w_1 \cdot T + w_2 \cdot V + w_3 \cdot R + w_4 \cdot A$$

โดยที่:
- $T$ = จำนวนการสัมผัส (ทำให้เป็นบรรทัดฐาน: $\min(T/5, 1)$)
- $V$ = ปริมาณการซื้อขายที่ระดับนั้น (ถ้ามี, ทำให้เป็นบรรทัดฐาน)
- $R$ = ความใกล้เคียงของการสัมผัสล่าสุด (การลดลงแบบเอกซ์โพเนนเชียล)
- $A$ = อายุของระดับ (ระดับที่เก่ากว่าแต่ยังยืนอยู่ได้จะแข็งแกร่งกว่า)

### 7.3 ตัวเลขกลมๆ และระดับจิตวิทยา (Round Numbers and Psychological Levels)

สำหรับ Forex: ระดับ 00, 20, 50, 80, 00 (เช่น 1.0800, 1.0850, 1.0900)
สำหรับ Crypto: ตัวเลขกลมๆ สำคัญ (BTC: 50000, 55000, 60000 เป็นต้น)

สิ่งเหล่านี้ทำหน้าที่เป็น S/R ตามธรรมชาติเนื่องจากคำสั่งรอดำเนินการจำนวนมากกระจุกตัวอยู่

$$\text{RoundNumberLevel}(P, \text{granularity}) = \text{round}(P / \text{granularity}) \times \text{granularity}$$

---

## 8. อัลกอริทึมจดจำรูปแบบ (Pattern Recognition Algorithms)

### 8.1 ตัวตรวจจับรูปแบบรวม (Composite Pattern Detector)

```python
class PriceActionDetector:
    def __init__(self, candles, atr_period=14):
        self.candles = candles
        self.atr = calculate_atr(candles, atr_period)
    
    def detect_all_signals(self, index=-1):
        """
        Detect all price action signals at the given candle index.
        Returns a list of signals with type and confidence.
        """
        signals = []
        i = index if index >= 0 else len(self.candles) + index
        c = self.candles
        atr = self.atr[i]
        
        # Single candle patterns
        if self._is_bullish_pin(c[i], atr):
            signals.append({"type": "BULLISH_PIN", "confidence": 0.6, "candle": i})
        
        if self._is_bearish_pin(c[i], atr):
            signals.append({"type": "BEARISH_PIN", "confidence": 0.6, "candle": i})
        
        if self._is_doji(c[i]):
            signals.append({"type": "DOJI", "confidence": 0.3, "candle": i})
        
        # Multi-candle patterns (need i >= 1)
        if i >= 1:
            if self._is_bullish_engulfing(c[i-1], c[i]):
                signals.append({"type": "BULLISH_ENGULFING", "confidence": 0.65, "candle": i})
            
            if self._is_bearish_engulfing(c[i-1], c[i]):
                signals.append({"type": "BEARISH_ENGULFING", "confidence": 0.65, "candle": i})
            
            if self._is_inside_bar(c[i-1], c[i]):
                signals.append({"type": "INSIDE_BAR", "confidence": 0.50, "candle": i})
        
        # Three-candle patterns (need i >= 2)
        if i >= 2:
            if self._is_morning_star(c[i-2], c[i-1], c[i], atr):
                signals.append({"type": "MORNING_STAR", "confidence": 0.70, "candle": i})
            
            if self._is_evening_star(c[i-2], c[i-1], c[i], atr):
                signals.append({"type": "EVENING_STAR", "confidence": 0.70, "candle": i})
            
            if self._is_three_white_soldiers(c[i-2], c[i-1], c[i]):
                signals.append({"type": "THREE_WHITE_SOLDIERS", "confidence": 0.72, "candle": i})
            
            if self._is_three_black_crows(c[i-2], c[i-1], c[i]):
                signals.append({"type": "THREE_BLACK_CROWS", "confidence": 0.72, "candle": i})
        
        # Apply context modifiers
        for signal in signals:
            signal["adjusted_confidence"] = self._apply_context(signal, i)
        
        return signals
    
    def _apply_context(self, signal, index):
        """Apply contextual modifiers to confidence."""
        base = signal["confidence"]
        
        # Trend alignment
        trend = self._determine_trend(index)
        if self._signal_aligns_with_trend(signal, trend):
            base *= 1.2
        elif self._signal_opposes_trend(signal, trend):
            base *= 0.7
        
        # Location (at S/R level)
        if self._at_sr_level(index):
            base *= 1.25
        
        # Momentum (ADX or similar)
        if self._strong_momentum(index):
            base *= 1.1
        
        return min(base, 1.0)
```

---

## 9. ตรรกะการเข้าและออกจุด (Entry and Exit Logic)

### 9.1 กฎการเข้าด้วยรูปแบบแท่งเทียน

| รูปแบบ | จุดเข้า (Entry Trigger) | SL | วิธี TP |
|---------|--------------|-----|-----------|
| พินบาร์ขาขึ้น (Bullish Pin Bar) | Buy stop เหนือจุดสูงพินบาร์ | ใต้จุดต่ำพินบาร์ | อย่างน้อย 2R, S/R ถัดไป |
| พินบาร์ขาลง (Bearish Pin Bar) | Sell stop ใต้จุดต่ำพินบาร์ | เหนือจุดสูงพินบาร์ | อย่างน้อย 2R, S/R ถัดไป |
| กลืนขาขึ้น (Bullish Engulfing) | ซื้อตอนปิดหรือ buy stop เหนือจุดสูงแท่งกลืน | ใต้จุดต่ำแท่งกลืน | อย่างน้อย 2R |
| กลืนขาลง (Bearish Engulfing) | ขายตอนปิดหรือ sell stop ใต้จุดต่ำแท่งกลืน | เหนือจุดสูงแท่งกลืน | อย่างน้อย 2R |
| แท่งภายใน (Inside Bar) | Buy stop เหนือจุดสูงแท่งแม่ หรือ sell stop ใต้จุดต่ำแท่งแม่ | ด้านตรงข้ามของแท่งแม่ | 2–3R |
| ดาวรุ่ง (Morning Star) | ซื้อตอนปิดแท่ง 3 | ใต้จุดต่ำแท่ง 2 | 2R |
| ดาวค่ำ (Evening Star) | ขายตอนปิดแท่ง 3 | เหนือจุดสูงแท่ง 2 | 2R |

### 9.2 กฎการเข้าด้วยรูปแบบกราฟ

| รูปแบบ | จุดเข้า | SL | TP (Measured Move) |
|---------|-------|-----|-------------------|
| ศีรษะและไหล่ (H&S) | ทะลุใต้เส้นคอ | เหนือจุดสูงไหล่ขวา | เส้นคอ - (ศีรษะ - เส้นคอ) |
| ศีรษะและไหล่กลับหัว (Inv H&S) | ทะลุเหนือเส้นคอ | ใต้จุดต่ำไหล่ขวา | เส้นคอ + (เส้นคอ - ศีรษะ) |
| ดับเบิ้ลท็อป (Double Top) | ทะลุใต้เส้นคอ | เหนือยอดทั้งสอง | เส้นคอ - (ยอด - เส้นคอ) |
| ดับเบิ้ลบอทท่อม (Double Bottom) | ทะลุเหนือเส้นคอ | ใต้ก้นทั้งสอง | เส้นคอ + (เส้นคอ - ก้น) |
| สามเหลี่ยมขาขึ้น (Ascending Triangle) | ทะลุเหนือแนวต้านราบ | ใต้จุดต่ำแกว่งล่าสุด | ความสูงสามเหลี่ยมฉายขึ้น |
| สามเหลี่ยมขาลง (Descending Triangle) | ทะลุใต้แนวรับราบ | เหนือจุดสูงแกว่งล่าสุด | ความสูงฉายลง |
| ธงกระทิง (Bull Flag) | ทะลุเหนือจุดสูงธง | ใต้จุดต่ำธง | ความสูงเสาธงฉายขึ้น |
| ธงหมี (Bear Flag) | ทะลุใต้จุดต่ำธง | เหนือจุดสูงธง | ความสูงเสาธงฉายลง |
| ถ้วยและหูจับ (Cup & Handle) | ทะลุเหนือจุดสูงหูจับ | ใต้จุดต่ำหูจับ | ความลึกถ้วยฉายขึ้น |

### 9.3 การตรวจสอบความถูกต้องของการทะลุ (Breakout Validation)

ไม่ใช่การทะลุทุกครั้งจะเป็นของจริง ตรวจสอบด้วย:

1. **ปริมาณการซื้อขาย (Volume)**: แท่งเทียนทะลุควรมีปริมาณสูงกว่าค่าเฉลี่ย (ถ้ามี)
2. **ราคาปิดแท่งเทียน**: ราคาต้องปิดเกินระดับทะลุ (ไม่ใช่แค่ไส้เทียน)
3. **การต่อเนื่อง (Follow-through)**: แท่งเทียนหลังจากทะลุไม่ควรกลับตัวเต็มที่
4. **รีเทสต์ (Retest)**: การทะลุที่ดีจะรีเทสต์ระดับที่ถูกทะลุเป็น S/R ใหม่

$$\text{ValidBreakout} = C_i > \text{Level} \quad \text{AND} \quad C_{i+1} > \text{Level} \quad \text{AND} \quad V_i > 1.5 \times V_{\text{avg20}}$$

---

## 10. สถิติอัตราชนะ (Statistical Win Rates)

### 10.1 ผลงานรูปแบบแท่งเทียน (ข้อมูลเชิงประจักษ์)

อ้างอิงจาก Bulkowski (2008) และการทดสอบย้อนหลังต่างๆ บน Forex/Crypto:

| รูปแบบ | ข้อได้เปรียบทางทฤษฎี | อัตราชนะ (ตามแนวโน้ม) | อัตราชนะ (สวนแนวโน้ม) | R:R เฉลี่ย |
|---------|-----------------|----------------------|-------------------------|---------|
| พินบาร์ขาขึ้น (Bullish Pin Bar) | แข็งแกร่ง | 58–65% | 48–53% | 1.5:1 |
| พินบาร์ขาลง (Bearish Pin Bar) | แข็งแกร่ง | 57–63% | 47–52% | 1.5:1 |
| กลืนขาขึ้น (Bullish Engulfing) | ปานกลาง | 55–62% | 45–50% | 1.4:1 |
| กลืนขาลง (Bearish Engulfing) | ปานกลาง | 54–60% | 44–49% | 1.4:1 |
| ดาวรุ่ง (Morning Star) | แข็งแกร่ง | 60–68% | 50–55% | 1.6:1 |
| ดาวค่ำ (Evening Star) | แข็งแกร่ง | 59–66% | 49–54% | 1.6:1 |
| ทะลุแท่งภายใน (Inside Bar Breakout) | ไม่แน่นอน | 52–58% | 45–52% | 1.8:1 |
| สามทหารขาว (Three White Soldiers) | แข็งแกร่ง | 62–70% | 52–58% | 1.3:1 |

### 10.2 ผลงานรูปแบบกราฟ

| รูปแบบ | อัตราความสำเร็จ (Bulkowski) | กำไรเฉลี่ย | อัตราล้มเหลว |
|---------|-------------------------|-----------|--------------|
| ศีรษะและไหล่ (Head & Shoulders) | 83% (ถึงเป้าหมาย) | 15–20% | 17% |
| ศีรษะและไหล่กลับหัว (Inv Head & Shoulders) | 74% | 20–25% | 26% |
| ดับเบิ้ลท็อป (Double Top) | 73% | 15–20% | 27% |
| ดับเบิ้ลบอทท่อม (Double Bottom) | 78% | 20–25% | 22% |
| สามเหลี่ยมขาขึ้น ทะลุขึ้น (Ascending Triangle) | 75% | 35–40% | 25% |
| สามเหลี่ยมขาลง ทะลุลง (Descending Triangle) | 72% | 30–35% | 28% |
| ธงกระทิง (Bull Flag) | 67% | 20–25% | 33% |
| ถ้วยและหูจับ (Cup & Handle) | 65% | 30–40% | 35% |

*หมายเหตุ: อัตราเหล่านี้สมมติว่ามีบริบทที่เหมาะสม (สอดคล้องกับแนวโน้ม) และได้รับการยืนยันการทะลุ*

---

## 11. แบบจำลองทางคณิตศาสตร์ (Mathematical Models)

### 11.1 การให้คะแนนความมั่นใจของรูปแบบ (Pattern Confidence Scoring)

$$\text{Confidence} = P_{\text{base}} \times M_{\text{trend}} \times M_{\text{location}} \times M_{\text{TF}} \times M_{\text{volume}}$$

โดยที่:
- $P_{\text{base}}$ = อัตราชนะพื้นฐานของรูปแบบจากข้อมูลในอดีต
- $M_{\text{trend}}$ = ตัวคูณแนวโน้ม: $1.2$ (ตามแนวโน้ม), $1.0$ (เป็นกลาง), $0.7$ (สวนแนวโน้ม)
- $M_{\text{location}}$ = ตัวคูณตำแหน่ง: $1.25$ (ที่ S/R สำคัญ), $1.0$ (อื่นๆ)
- $M_{\text{TF}}$ = ตัวคูณกรอบเวลา: $1.2$ (D1+), $1.0$ (H1–H4), $0.8$ (M15 และต่ำกว่า)
- $M_{\text{volume}}$ = การยืนยันปริมาณ: $1.15$ (ปริมาณสูง), $1.0$ (ปกติ)

### 11.2 การคำนวณ Measured Move

สำหรับรูปแบบกราฟที่มีเป้าหมายแบบ Measured Move:

$$\text{Target} = \text{Breakout Level} \pm \text{Pattern Height} \times k$$

โดยที่ $k$ คือปัจจัยฉายเฉพาะรูปแบบ:

| รูปแบบ | $k$ (อนุรักษ์) | $k$ (มาตรฐาน) | $k$ (เชิงรุก) |
|---------|-------|----------|------------|
| ศีรษะและไหล่ (H&S) | 0.75 | 1.00 | 1.272 |
| ดับเบิ้ลท็อป/บอทท่อม (Double Top/Bottom) | 0.75 | 1.00 | 1.618 |
| สามเหลี่ยม (Triangle) | 0.75 | 1.00 | 1.272 |
| ธง (Flag) | 0.618 | 1.00 | 1.272 |
| ถ้วยและหูจับ (Cup & Handle) | 0.618 | 1.00 | 1.618 |

### 11.3 แบบจำลองความน่าจะเป็นของการทะลุ (Breakout Probability Model)

ความน่าจะเป็นของการทะลุที่สำเร็จจากรูปแบบพักตัว:

$$P(\text{breakout success}) = \sigma\left(\beta_0 + \beta_1 \cdot V_{\text{ratio}} + \beta_2 \cdot T_{\text{compression}} + \beta_3 \cdot D_{\text{trend}}\right)$$

โดยที่:
- $V_{\text{ratio}}$ = ปริมาณตอนทะลุ / ปริมาณเฉลี่ย
- $T_{\text{compression}}$ = จำนวนแท่งเทียนในช่วงพักตัว (ทำให้เป็นบรรทัดฐาน)
- $D_{\text{trend}}$ = การสอดคล้องกับทิศทางแนวโน้ม (1 = ตาม, 0 = สวน)

### 11.4 แบบจำลองการเสื่อมของแนวรับแนวต้าน (S/R Decay Model)

ความแข็งแกร่งของระดับ S/R เสื่อมลงทุกครั้งที่ถูกสัมผัส:

$$S(n) = S_0 \times \alpha^{n-1}$$

โดยที่:
- $S_0$ = ความแข็งแกร่งเริ่มต้น (อ้างอิงจากแรง Impulse ที่สร้างระดับนั้น)
- $n$ = จำนวนการสัมผัส
- $\alpha = 0.7$ (แต่ละการสัมผัสดูดซับ ~30% ของคำสั่งที่เหลือ)

หลังจาก $n \geq 4$ ครั้ง ระดับมีแนวโน้มที่จะถูกทะลุ:
$$P(\text{break}) = 1 - \alpha^{n-1}$$

---

## 12. พารามิเตอร์ความเสี่ยง (Risk Parameters)

### 12.1 กลยุทธ์ Stop Loss

| กลยุทธ์ | วิธีการ | เหมาะสำหรับ |
|----------|--------|----------|
| **SL ตามรูปแบบ (Pattern-Based SL)** | เลยระดับที่ทำให้รูปแบบเป็นโมฆะ | ทุกรูปแบบ |
| **SL ตาม ATR (ATR-Based SL)** | Entry $\pm$ $k \times$ ATR(14), $k = 1.0$–$1.5$ | เมื่อ SL ตามรูปแบบแคบเกินไป |
| **SL ตามโครงสร้าง (Structure-Based SL)** | เลยจุดสูง/ต่ำแกว่งที่ใกล้ที่สุด | การเทรดต่อเนื่องตามแนวโน้ม |
| **SL ตามเวลา (Time-Based SL)** | ปิดถ้าไม่มีการเคลื่อนไหวภายใน $n$ แท่ง | การเทรดทะลุ |

### 12.2 การกำหนดขนาดสถานะ (Position Sizing)

$$\text{Size} = \frac{\text{Balance} \times R\%}{|\text{Entry} - \text{SL}| \times \text{Pip Value}}$$

การจัดสรรความเสี่ยงตามความมั่นใจของสัญญาณ:

| ความมั่นใจที่ปรับแล้ว | ความเสี่ยง % |
|--------------------|--------|
| $\geq 0.75$ | 1.5% |
| 0.60 – 0.74 | 1.0% |
| 0.45 – 0.59 | 0.5% |
| $< 0.45$ | ไม่เทรด |

### 12.3 กฎการรับความเสี่ยงสูงสุด

- สูงสุด 3 สถานะเปิดพร้อมกันจากสัญญาณรูปแบบราคา
- ความเสี่ยงรวมสูงสุด 4% ในเวลาใดก็ตาม
- ไม่เกิน 2 สถานะในทิศทางเดียวกันบนสินทรัพย์ที่มีความสัมพันธ์กัน
- ถ้าอัตราชนะต่ำกว่า 40% ใน 20 เทรดล่าสุด ลดความเสี่ยงเหลือ 0.5% และทบทวน

---

## 13. ขั้นตอนการดำเนินงาน (Execution Flow)

### 13.1 Pseudocode กลยุทธ์ฉบับสมบูรณ์

```python
def price_action_strategy():
    """
    Complete price action trading strategy.
    """
    
    # ================================================
    # PHASE 1: CONTEXT DETERMINATION
    # ================================================
    
    for instrument in watchlist:
        # Determine HTF trend
        htf_candles = fetch_candles(instrument, "D1", count=100)
        htf_trend = determine_trend(htf_candles)  # BULLISH / BEARISH / RANGING
        
        # Identify key S/R levels
        sr_levels = identify_sr_levels(htf_candles)
        
        # ================================================
        # PHASE 2: PATTERN SCANNING
        # ================================================
        
        # Scan trading timeframe for signals
        tf_candles = fetch_candles(instrument, "H4", count=200)
        atr = calculate_atr(tf_candles, 14)
        
        # Candlestick patterns
        detector = PriceActionDetector(tf_candles)
        candle_signals = detector.detect_all_signals()
        
        # Chart patterns
        swings = find_swing_points(tf_candles, lookback=5)
        chart_patterns = detect_chart_patterns(swings, tf_candles)
        
        # ================================================
        # PHASE 3: SIGNAL FILTERING
        # ================================================
        
        all_signals = candle_signals + chart_patterns
        
        # Filter by confidence
        actionable = [s for s in all_signals if s.get("adjusted_confidence", 0) >= 0.45]
        
        # Filter by location (must be near S/R for candlestick patterns)
        for signal in actionable:
            if signal["type"] in CANDLESTICK_PATTERNS:
                if not near_sr_level(tf_candles[-1], sr_levels, atr[-1]):
                    signal["adjusted_confidence"] *= 0.6  # Reduce if not at S/R
        
        # Re-filter after adjustment
        actionable = [s for s in actionable if s.get("adjusted_confidence", 0) >= 0.45]
        
        if not actionable:
            continue
        
        # Sort by confidence
        actionable.sort(key=lambda s: s["adjusted_confidence"], reverse=True)
        best_signal = actionable[0]
        
        # ================================================
        # PHASE 4: TRADE SETUP
        # ================================================
        
        entry, sl, tp = calculate_trade_parameters(best_signal, tf_candles, sr_levels, atr[-1])
        
        # Validate R:R
        rr = abs(tp - entry) / abs(entry - sl)
        min_rr = get_min_rr(best_signal["adjusted_confidence"])
        
        if rr < min_rr:
            continue
        
        # ================================================
        # PHASE 5: RISK CHECK AND EXECUTION
        # ================================================
        
        risk_pct = get_risk_pct(best_signal["adjusted_confidence"])
        position_size = calculate_position_size(balance, risk_pct, entry, sl)
        
        if not check_portfolio_limits(position_size, risk_pct):
            continue
        
        trade = execute_trade(
            instrument=instrument,
            direction=get_direction(best_signal),
            entry=entry,
            sl=sl,
            tp=tp,
            size=position_size,
            metadata={
                "signal_type": best_signal["type"],
                "confidence": best_signal["adjusted_confidence"],
                "htf_trend": htf_trend,
                "timeframe": "H4"
            }
        )
        
        log_trade(trade)
        return trade
    
    return WAIT("No actionable price action signal")
```

### 13.2 การจัดการสถานะ (Trade Management)

```python
def manage_pa_trade(trade):
    """Active management of price action trades."""
    
    current_price = get_price(trade.instrument)
    candles = fetch_candles(trade.instrument, trade.timeframe, count=50)
    
    # Check for opposing signal at current price
    detector = PriceActionDetector(candles)
    signals = detector.detect_all_signals()
    opposing = [s for s in signals if opposes_trade(s, trade)]
    
    if opposing and opposing[0]["adjusted_confidence"] >= 0.65:
        # Strong opposing signal — consider early exit
        if trade.current_pnl > 0:
            close_trade(trade, reason="Strong opposing signal in profit")
            return
    
    # Trailing stop based on new swing points
    if trade.pnl_in_r >= 1.0:  # At least 1R in profit
        trail_behind_structure(trade, candles)
    
    # Time-based management (for breakout trades)
    if trade.metadata["signal_type"] in BREAKOUT_PATTERNS:
        if trade.age_candles > 10 and trade.pnl_in_r < 0.5:
            close_trade(trade, reason="Breakout failed to follow through")
```

---

## 14. หมายเหตุการใช้งาน AI (AI Implementation Notes)

### 14.1 จุดแข็งของ AI ในการวิเคราะห์รูปแบบราคา

1. **ความสม่ำเสมอ**: AI ไม่มีวันเหนื่อยล้าหรืออารมณ์แปรปรวน; ทุกแท่งเทียนถูกสแกนอย่างเป็นระบบ
2. **ครอบคลุมหลายสินทรัพย์**: สามารถสแกน 50+ สินทรัพย์พร้อมกัน
3. **ความเป็นกลางของรูปแบบ**: ไม่มีการ "ดูด้วยตา" แบบอัตนัย — ทุกอย่างถูกกำหนดทางคณิตศาสตร์
4. **การติดตามสถิติ**: ตรวจสอบอัตราชนะแบบเรียลไทม์ต่อประเภทรูปแบบ

### 14.2 ความท้าทายและการลดผลกระทบ

| ความท้าทาย | การลดผลกระทบ |
|-----------|-----------|
| บริบทมีความละเอียดอ่อน | ใช้การให้คะแนนความมั่นใจหลายปัจจัยร่วมกับแนวโน้ม HTF, ตำแหน่ง และโมเมนตัม |
| รูปแบบไม่ใช่แบบไบนารี | ใช้คะแนนความมั่นใจแบบไล่ระดับ (0–1) แทนที่จะเป็นใช่/ไม่ |
| สัญญาณหลอกเกิดขึ้นบ่อย | ต้องการจุดบรรจบขั้นต่ำ (2+ ปัจจัย) สำหรับการเข้า |
| การเลือกกรอบเวลาสำคัญ | ค่าเริ่มต้น H4 สำหรับสัญญาณเทรด, D1 สำหรับบริบท |

### 14.3 ข้อกำหนดข้อมูล

| กรอบเวลา | ประวัติที่ต้องการ | ความถี่ |
|-----------|---------------|-----------|
| Monthly | 5+ ปี | รายเดือน |
| Weekly | 2 ปี | รายสัปดาห์ |
| Daily | 1 ปี | รายวัน |
| H4 | 6 เดือน | ทุก 4 ชั่วโมง |
| H1 | 3 เดือน | รายชั่วโมง |
| M15 | 2 สัปดาห์ | ทุก 15 นาที |

---

## 15. อ้างอิง (References)

### หนังสือ
1. Brooks, A. (2009). *Reading Price Charts Bar by Bar*. Wiley.
2. Brooks, A. (2012). *Trading Price Action Trends*. Wiley.
3. Brooks, A. (2012). *Trading Price Action Trading Ranges*. Wiley.
4. Brooks, A. (2012). *Trading Price Action Reversals*. Wiley.
5. Nison, S. (2001). *Japanese Candlestick Charting Techniques*, 2nd ed. Prentice Hall.
6. Bulkowski, T. N. (2005). *Encyclopedia of Chart Patterns*, 2nd ed. Wiley.
7. Bulkowski, T. N. (2008). *Encyclopedia of Candlestick Charts*. Wiley.
8. Murphy, J. J. (1999). *Technical Analysis of the Financial Markets*. NYIF.
9. Edwards, R. D., & Magee, J. (2007). *Technical Analysis of Stock Trends*, 9th ed. CRC Press.
10. Pring, M. J. (2002). *Technical Analysis Explained*, 4th ed. McGraw-Hill.

### บทความวิชาการ
11. Lo, A. W., Mamaysky, H., & Wang, J. (2000). "Foundations of Technical Analysis." *The Journal of Finance*, 55(4), 1705–1765.
12. Park, C.-H., & Irwin, S. H. (2007). "What Do We Know About the Profitability of Technical Analysis?" *Journal of Economic Surveys*, 21(4), 786–826.
13. Caginalp, G., & Laurent, H. (1998). "The Predictive Power of Price Patterns." *Applied Mathematical Finance*, 5, 181–206.
14. Leigh, W., Modani, N., Purvis, R., & Roberts, T. (2002). "Stock Market Trading Rule Discovery Using Technical Charting Heuristics." *Expert Systems with Applications*, 23(2), 155–159.

### แหล่งข้อมูลจากผู้ปฏิบัติ
15. Nial Fuller. "Price Action Trading Strategies" — LearnToTradeTheMarket.com.
16. Chris Capre. "Advanced Price Action Course" — 2ndSkiesForex.com.
17. TradingView. Pattern recognition community indicators.

---

*เอกสารนี้เป็นส่วนหนึ่งของฐานความรู้ระบบเทรด AI แบบหลายตัวแทน (Multi-Agent AI Trading System) ควรอ่านร่วมกับคู่มือโซนอุปสงค์อุปทาน (05_supply_demand_zones), คู่มือแนวคิดเงินอัจฉริยะ (04_smart_money_concepts) และคู่มือการวิเคราะห์หลายกรอบเวลา (11_multi_timeframe_analysis)*
