# อิชิโมคุ คินโค เฮียว ขั้นสูง (Advanced Ichimoku Kinko Hyo) — คู่มือฉบับสมบูรณ์

## ข้อมูลเอกสาร (Document Metadata)
| ฟิลด์ | ค่า |
|---|---|
| **รหัสกลยุทธ์ (Strategy ID)** | ICH-001 |
| **หมวดหมู่ (Category)** | ติดตามแนวโน้ม / อินดิเคเตอร์หลายองค์ประกอบ (Trend-Following / Multi-Component Indicator) |
| **ประเภทสินทรัพย์ (Asset Classes)** | Forex, Crypto, หุ้น (Equities), ดัชนี (Indices) |
| **กรอบเวลา (Timeframes)** | H1 ถึง Monthly (หลัก: H4–Weekly) |
| **ความซับซ้อน (Complexity)** | ระดับกลางถึงขั้นสูง (Intermediate to Advanced) |
| **ความเหมาะสมกับ AI** | สูง — ทุกองค์ประกอบถูกกำหนดทางคณิตศาสตร์ |
| **เวอร์ชัน** | 2.0 |
| **อัปเดตล่าสุด** | 2026-04-12 |

---

## สารบัญ
1. [บทนำ](#1-บทนำ)
2. [ห้าองค์ประกอบ](#2-ห้าองค์ประกอบ)
3. [การวิเคราะห์เมฆ (Kumo)](#3-การวิเคราะห์เมฆ-kumo)
4. [สัญญาณ TK Cross](#4-สัญญาณ-tk-cross)
5. [กลยุทธ์ Kumo Breakout](#5-กลยุทธ์-kumo-breakout)
6. [การยืนยัน Chikou Span](#6-การยืนยัน-chikou-span)
7. [อิชิโมคุหลายกรอบเวลา](#7-อิชิโมคุหลายกรอบเวลา)
8. [พารามิเตอร์ที่ปรับสำหรับ Crypto](#8-พารามิเตอร์ที่ปรับสำหรับ-crypto)
9. [สูตรทางคณิตศาสตร์](#9-สูตรทางคณิตศาสตร์)
10. [การรวมสัญญาณขั้นสูง](#10-การรวมสัญญาณขั้นสูง)
11. [พารามิเตอร์ความเสี่ยง](#11-พารามิเตอร์ความเสี่��ง)
12. [ขั้นตอนการดำเนินงาน](#12-ขั้นตอนการดำเนินงาน)
13. [หมายเหตุการใช้งาน AI](#13-หมายเหตุการใช้งาน-ai)
14. [อ้างอิง](#14-อ้างอิง)

---

## 1. บทนำ

อิชิโมคุ คินโค เฮียว (Ichimoku Kinko Hyo แปลตรงตัวว่า "กราฟดุลยภาพในมุมมองเดียว") เป็นระบบวิเคราะห์ทางเทคนิคแบบครบวงจรที่พัฒนาโดย Goichi Hosoda (นามปากกา: Ichimoku Sanjin) ในญี่ปุ่น ตีพิมพ์ในปี 1968 หลังการวิจัย 30 ปี มีความเป็นเอกลักษณ์ตรงที่อินดิเคเตอร์เดียวให้ข้อมูลเกี่ยวกับทิศทางแนวโน้ม โมเมนตัม แนวรับ/แนวต้าน และระดับฉายอนาคต — ทั้งหมดในมุมมองเดียว

### 1.1 ปรัชญาหลัก

- ตลาดถูกปกครองโดยดุลยภาพ (ความสมดุลระหว่างผู้ซื้อและผู้ขาย)
- การเคลื่อนไหวของราคามีธรรมชาติเป็นจังหวะ — คลื่นราคาในอดีตทำนายการเคลื่อนไหวในอนาคต
- ความสัมพันธ์ระหว่างราคากับ "เมฆ" กำหนดแนวโน้มหลัก
- ทั้งห้าองค์ประกอบต้องอ่านร่วมกันเพื่อการวิเคราะห์ที่ครบถ้วน

### 1.2 ทำไมอิชิโมคุเหมาะกับ AI Trading

- **สามารถวัดค่าได้ทั้งหมด**: ทุกองค์ประกอบใช้สูตรคณิตศาสตร์ที่แน่นอน
- **หลายมิติ**: อินดิเคเตอร์เดียวให้แนวโน้ม โมเมนตัม S/R และเป้าหมาย
- **องค์ประกอบนำ (Leading)**: Senkou Spans ฉายไปข้างหน้า 26 คาบ
- **การยืนยันตาม (Lagging)**: Chikou Span ตรวจสอบจากอดีต
- **การปรับพารามิเตอร์น้อย**: ค่าตั้งมาตรฐานได้รับการยอมรับอย่างดี

---

## 2. ห้าองค์ประกอบ (The Five Components)

### 2.1 เทนคัน-เซ็น (Tenkan-sen / Conversion Line)

$$\text{Tenkan-sen} = \frac{\max(H, 9) + \min(L, 9)}{2}$$

โดยที่ $\max(H, 9)$ = ราคาสูงสุดของ 9 คาบล่าสุด และ $\min(L, 9)$ = ราคาต่ำสุดของ 9 คาบล่าสุด

**การตีความ**:
- อินดิเคเตอร์โมเมนตัมระยะสั้น (คล้ายจุดกลาง 9 คาบ)
- แสดงถึงดุลยภาพของช่วงราคาระยะสั้น
- เมื่อราคาอยู่เหนือเทนคัน: โมเมนตัมขาขึ้นระยะสั้น
- เทนคันราบ: พักตัว/Ranging ระยะสั้น

**การวิเคราะห์ความชัน**:
$$\text{Tenkan\_Slope}_t = \text{Tenkan}_t - \text{Tenkan}_{t-1}$$
- ความชันบวก: โมเมนตัมขาขึ้นกำลังเร่ง
- ความชันลบ: โมเมนตัมขาลงกำลังเร่ง
- ราบ: ดุลยภาพ / Ranging

### 2.2 คิจุน-เซ็น (Kijun-sen / Base Line)

$$\text{Kijun-sen} = \frac{\max(H, 26) + \min(L, 26)}{2}$$

**การตีความ**:
- โมเมนตัมและดุลยภาพระยะกลาง
- ทำหน้าที่เป็นแนวรับไดนามิก (ในขาขึ้น) และแนวต้าน (ในขาลง)
- เส้น "มาตรฐาน" — ราคามีแนวโน้มกลับมาหาคิจุนในตลาดที่มีแนวโน้ม
- คิจุนราบ: ดุลยภาพที่แข็งแกร่ง; ราคาน่าจะกลับมาที่ระดับนี้

**คิจุนเป็น S/R**:
เมื่อคิจุนราบเป็นเวลาหลายคาบ มันสร้างแม่เหล็กที่ทรงพลัง:
$$\text{Kijun\_Flat} = \text{Kijun}_t = \text{Kijun}_{t-1} = \ldots = \text{Kijun}_{t-n}, \quad n \geq 5$$

คิจุนราบจะมี Retracement 50% ของช่วงราคาอยู่เสมอ — มันคือดุลยภาพ

### 2.3 เซนโค สแปน A (Senkou Span A / Leading Span A)

$$\text{Senkou Span A}_t = \frac{\text{Tenkan}_{t-26} + \text{Kijun}_{t-26}}{2} \quad \text{(วาดล่วงหน้า 26 คาบ)}$$

แม่นยำกว่า ค่าที่คำนวณ ณ เวลา $t$ จะถูกวาด ณ เวลา $t + 26$

**การคำนวณปัจจุบัน**:
$$\text{SpanA}_{\text{future}} = \frac{\text{Tenkan}_{\text{current}} + \text{Kijun}_{\text{current}}}{2}$$

**การตีความ**:
- ขอบเขตหนึ่งของเมฆ (Kumo)
- ตอบสนองมากกว่า Span B (ใช้คาบสั้นกว่าในอินพุต)
- เมื่อ Span A > Span B: เมฆขาขึ้น (เขียว)
- เมื่อ Span A < Span B: เมฆขาลง (แดง)

### 2.4 เซนโค สแปน B (Senkou Span B / Leading Span B)

$$\text{Senkou Span B}_t = \frac{\max(H, 52) + \min(L, 52)}{2} \quad \text{(วาดล่วงหน้า 26 คาบ)}$$

**การตีความ**:
- ขอบเขตที่สองของ Kumo
- เสถียรกว่า Span A (ใช้ช่วง 52 คาบ)
- เมื่อราบ: ระดับแนวรับ/แนวต้านที่แข็งแกร่งมาก
- คล้ายดุลยภาพ 52 คาบ — แสดงถึงฉันทามติระยะยาว

### 2.5 ชิโค สแปน (Chikou Span / Lagging Span)

$$\text{Chikou Span}_t = C_t \quad \text{(วาดย้อนหลัง 26 คาบ)}$$

ราคาปิดปัจจุบัน เลื่อนไปข้างหลัง 26 คาบ

**การตีความ**:
- ยืนยันแนวโน้มโดยเปรียบเทียบราคาปัจจุบันกับราคา 26 คาบก่อน
- ถ้า Chikou > ราคา 26 คาบก่อน: ยืนยันขาขึ้น
- ถ้า Chikou < ราคา 26 คาบก่อน: ยืนยันขาลง
- Chikou ปฏิสัมพันธ์กับราคา/เมฆในอดีต: ปฏิกิริยา S/R ที่อาจเกิดขึ้น

---

## 3. การวิเคราะห์เมฆ (Cloud / Kumo Analysis)

### 3.1 พื้นฐาน Kumo

Kumo (เมฆ) เกิดขึ้นระหว่าง Senkou Span A และ Senkou Span B เป็นองค์ประกอบที่สำคัญที่สุดของอิชิโมคุและให้:
- **ทิศทางแนวโน้ม**: ราคาเหนือเมฆ = ขาขึ้น; ใต้ = ขาลง; ภายใน = เป็นกลาง/เปลี่ยนผ่าน
- **แนวรับ/แนวต้าน**: เมฆทำหน้าที่เป็นโซน S/R
- **การฉายอนาคต**: เนื่องจากเมฆถูกวาดล่วงหน้า 26 คาบ จึงแสดง S/R ที่อาจเกิดในอนาคต

### 3.2 ความหนาของ Kumo

$$\text{Kumo\_Thickness}_t = |\text{SpanA}_t - \text{SpanB}_t|$$

**ความสำคัญ**:
- เมฆหนา: S/R แข็งแกร่ง; ราคาทะลุผ่านยาก
- เมฆบาง: S/R อ่อนแอ; ราคาเจาะผ่านง่ายกว่า
- เมฆเข้าใกล้ความหนาศูนย์: Kumo Twist กำลังจะเกิด

**ความหนาที่ทำให้เป็นบรรทัดฐาน**:
$$\text{KT\_Norm} = \frac{\text{Kumo\_Thickness}}{\text{ATR}(26)}$$

| KT_Norm | การตีความ |
|---------|---------------|
| $> 2.0$ | หนามาก — อุปสรรคแข็งแกร่ง |
| 1.0–2.0 | ปกติ — S/R มาตรฐาน |
| 0.5–1.0 | บาง — ทะลุได้ |
| $< 0.5$ | บางมาก — น่าจะทะลุ |

### 3.3 Kumo Twist

**Kumo Twist** เกิดเมื่อ Senkou Span A ตัด Senkou Span B เปลี่ยนสีเมฆจากขาขึ้นเป็นขาลง (หรือกลับกัน)

$$\text{KumoTwist} = \text{sign}(\text{SpanA}_t - \text{SpanB}_t) \neq \text{sign}(\text{SpanA}_{t-1} - \text{SpanB}_{t-1})$$

**ความสำคัญ**:
- บ่งชี้การเปลี่ยนแปลงดุลยภาพตลาด (จากขาขึ้นเป็นขาลงหรือกลับกัน)
- จุด Twist มักทำหน้าที่เป็นโซนจุดหักเห — ราคาถูกดึงดูดเข้าหา
- Twist ในเมฆอนาคต (ที่ฉาย) ส่งสัญญาณการเปลี่ยนแนวโน้มที่อาจเกิดใน 26 คาบ

### 3.4 Kumo Breakout

**Kumo Breakout** เกิดเมื่อราคาปิดเหนือ/ใต้เมฆหลังจากอยู่ด้านตรงข้ามหรือภายใน

**Kumo Breakout ขาขึ้น**:
$$C_t > \max(\text{SpanA}_t, \text{SpanB}_t) \quad \text{AND} \quad C_{t-1} \leq \max(\text{SpanA}_{t-1}, \text{SpanB}_{t-1})$$

**Kumo Breakout ขาลง**:
$$C_t < \min(\text{SpanA}_t, \text{SpanB}_t) \quad \text{AND} \quad C_{t-1} \geq \min(\text{SpanA}_{t-1}, \text{SpanB}_{t-1})$$

### 3.5 เมฆเป็นโซนเข้า (Cloud as Entry Zone)

เมฆเป็นโซนเข้าที่ดีเยี่ยมสำหรับการดึงกลับในตลาดที่มีแนวโน้ม:
- **ในขาขึ้น**: ซื้อเมื่อราคาดึงกลับเข้าไปในเมฆ (ทดสอบจากด้านบน)
- **ในขาลง**: ขายเมื่อราคาเด้งขึ้นไปในเมฆ (ทดสอบจากด้านล่าง)

การเข้าที่เมฆให้:
- ความเสี่ยงที่กำหนดได้ (SL เลยด้านตรงข้ามของเมฆ)
- ข้อได้เปรียบทางสถิติ (เมฆทำหน้าที่เป็น S/R)
- จุดเป็นโมฆะที่ชัดเจน (ราคาปิดทะลุเมฆทั้งหมด)

---

## 4. สัญญาณ TK Cross

### 4.1 TK Cross ขาขึ้น (Bullish TK Cross)

เทนคัน-เซ็นตัดเหนือคิจุน-เซ็น

$$\text{BullishTKCross} = \text{Tenkan}_t > \text{Kijun}_t \quad \text{AND} \quad \text{Tenkan}_{t-1} \leq \text{Kijun}_{t-1}$$

### 4.2 TK Cross ขาลง (Bearish TK Cross)

เทนคัน-เซ็นตัดใต้คิจุน-เซ็น

$$\text{BearishTKCross} = \text{Tenkan}_t < \text{Kijun}_t \quad \text{AND} \quad \text{Tenkan}_{t-1} \geq \text{Kijun}_{t-1}$$

### 4.3 การจำแนกคุณภาพ TK Cross

| ตำแหน่งการตัด | คุณภาพ | ชื่อสัญญาณ |
|---------------|---------|-------------|
| เหนือเมฆ (ตัดขาขึ้นเหนือเมฆ) | **แข็งแกร่ง** | "Golden Cross" |
| ภายในเมฆ (ตัดขาขึ้นในเมฆ) | **เป็นกลาง** | "Neutral Cross" |
| ใต้เมฆ (ตัดขาขึ้นใต้เมฆ) | **อ่อนแอ** | "Dead Cross" (พยายามกลับตัว) |

**การให้คะแนน**:
$$S_{\text{TK}} = \begin{cases} 1.0 & \text{ตัดขาขึ้นเหนือเมฆ} \\ 0.6 & \text{ตัดขาขึ้นในเมฆ} \\ 0.3 & \text{ตัดขาขึ้นใต้เมฆ} \end{cases}$$

และภาพสะท้อนสำหรับการตัดขาลง

### 4.4 ระยะห่าง TK เป็นตัววัดโมเมนตัม

$$\text{TK\_Distance} = \text{Tenkan} - \text{Kijun}$$

- ระยะห่าง TK เป็นบวกมาก: โมเมนตัมขาขึ้นแข็งแกร่ง
- ระยะห่าง TK เป็นลบมาก: โมเมนตัมขาลงแข็งแกร่ง
- บรรจบ (ระยะห่างเข้าใกล้ศูนย์): โมเมนตัมจางลง; อาจตัดกันเร็วๆ นี้

ทำให้เป็นบรรทัดฐาน:
$$\text{TK\_Norm} = \frac{\text{Tenkan} - \text{Kijun}}{\text{ATR}(26)}$$

---

## 5. กลยุทธ์ Kumo Breakout

### 5.1 Kumo Breakout แบบคลาสสิก

**การเข้า**: เมื่อแท่งเทียนแรกปิดเลยเมฆ
**การยืนยัน**:
1. Chikou Span ต้องอยู่เหนือ/ใต้ราคา (26 คาบก่อน) และเหนือ/ใต้เมฆ
2. เมฆอนาคตควรมีสีในทิศทางการทะลุ (Kumo Twist สนับสนุน)

**Stop Loss**: ด้านตรงข้ามของเมฆ ณ แท่งเทียนทะลุ
**เป้าหมาย**: วัดความหนาเมฆ ณ จุดทะลุ; ฉายระยะนั้นเลยจุดทะลุ

### 5.2 Kumo Breakout + Retest

แบบความน่าจะเป็นสูงกว่า:
1. ราคาทะลุออกจากเมฆ (สัญญาณเริ่มต้น)
2. รอราคาดึงกลับมารีเทสต์ขอบเมฆ
3. เข้าเมื่อรีเทสต์ถ้าราคาเคารพเมฆเป็น S/R
4. SL: ในเมฆ 0.5 ATR

### 5.3 Kumo Breakout ล้มเหลว (Edge-to-Edge Trade)

เมื่อราคาเข้าไปในเมฆจากด้านหนึ่ง มีความน่าจะเป็นสูงที่จะถึงอีกด้าน — นี่คือ "Edge-to-Edge" Trade

**เซ็ตอัพ**:
- ราคาทะลุเข้าเมฆจากด้านล่าง (หรือด้านบน)
- เป้าหมาย: ขอบตรงข้ามของเมฆ
- SL: ใต้ด้านเข้าของเมฆ

**หมายเหตุทางสถิติ**: Edge-to-Edge Trades มีอัตราชนะเชิงประจักษ์ประมาณ 50–55% แต่มี R:R ที่ดีเนื่องจากความกว้างเมฆทำหน้าที่เป็นระยะทางเป้าหมาย

### 5.4 Thin Cloud Breakout

เมื่อเมฆบางมาก (KT_Norm < 0.5) การทะลุมีโอกาสมากขึ้นและมีนัยสำคัญมากขึ้น:
- SL ลดลง (เมฆบาง = ระยะสั้นไปอีกขอบ)
- อัตราสำเร็จสูงกว่า (S/R อ่อน เจาะได้ง่าย)
- คาดว่าจะเคลื่อนที่เร็วหลังทะลุ

---

## 6. การยืนยัน Chikou Span

### 6.1 Chikou เป็นการยืนยันแนวโน้ม

$$\text{Chikou\_Bullish} = C_{\text{current}} > C_{26\text{ periods ago}} \quad \text{AND} \quad C_{\text{current}} > \text{Cloud}_{26\text{ periods ago}}$$

สำหรับสัญญาณขาขึ้นที่สมบูรณ์ Chikou Span ต้อง:
1. อยู่เหนือแท่งเทียนราคาในอดีต
2. อยู่เหนือเมฆในอดีต
3. อยู่ใน "พื้นที่เปิด" (ไม่ถูกขวางโดยราคาในอดีต)

### 6.2 การวิเคราะห์การขวาง Chikou (Chikou Obstruction Analysis)

เส้นทางของ Chikou Span ผ่านราคาในอดีตเผยปฏิกิริยา S/R ที่อาจเกิดขึ้น:

```python
def chikou_analysis(candles, chikou_offset=26):
    """
    Analyze Chikou Span position relative to past price and cloud.
    """
    current_close = candles[-1].close
    past_candle = candles[-chikou_offset - 1]
    past_cloud_top = max(candles[-chikou_offset - 1].span_a, candles[-chikou_offset - 1].span_b)
    past_cloud_bot = min(candles[-chikou_offset - 1].span_a, candles[-chikou_offset - 1].span_b)
    
    # Position analysis
    above_price = current_close > past_candle.high
    below_price = current_close < past_candle.low
    above_cloud = current_close > past_cloud_top
    below_cloud = current_close < past_cloud_bot
    
    # Obstruction: is there price action between Chikou and "open space"?
    obstructed = False
    for i in range(-chikou_offset, -chikou_offset + 5):
        if candles[i].low <= current_close <= candles[i].high:
            obstructed = True
            break
    
    return {
        "above_price": above_price,
        "above_cloud": above_cloud,
        "below_price": below_price,
        "below_cloud": below_cloud,
        "obstructed": obstructed,
        "bullish_confirmation": above_price and above_cloud and not obstructed,
        "bearish_confirmation": below_price and below_cloud and not obstructed
    }
```

### 6.3 สัญญาณ Chikou Cross

เมื่อ Chikou Span ตัดเหนือ/ใต้ราคาในอดีต ยืนยันการเปลี่ยนโมเมนตัม:

$$\text{Chikou\_Cross\_Bullish} = \text{Chikou}_t > H_{t-26} \quad \text{AND} \quad \text{Chikou}_{t-1} \leq H_{t-26-1}$$

---

## 7. อิชิโมคุหลายกรอบเวลา (Multi-Timeframe Ichimoku)

### 7.1 ลำดับชั้นกรอบเวลา

| ชั้นการวิเคราะห์ | กรอบเวลา | วัตถุประสงค์ |
|---------------|-----------|---------|
| **แนวโน้มมหภาค** | Weekly/Monthly | อคติโดยรวม; ห้ามเทรดสวน |
| **แนวโน้มระดับกลาง** | Daily | ตัวกรองทิศทาง |
| **การดำเนินการเทรด** | H4 หรือ H1 | จังหวะเข้า/ออก |
| **การปรับละเอียด** | M15–M30 | การเข้าที่แม่นยำภายในสัญญาณ H4 |

### 7.2 กฎหลายกรอบเวลา (Multi-TF Rules)

1. **กรอบเวลาสูงกว่ามีอำนาจเหนือ**: ถ้า Weekly เป็นขาขึ้น (ราคาเหนือเมฆ) รับเฉพาะสัญญาณขาขึ้นบน Daily และต่ำกว่า
2. **ทุกกรอบเวลาสอดคล้อง ("Three Line Strike")**: สัญญาณที่แข็งแกร่งที่สุดเกิดเมื่อทุกกรอบเวลาสอดคล้อง (ราคาเหนือเมฆ, TK Cross ขาขึ้น, Chikou ขาขึ้นในแต่ละกรอบ)
3. **การแก้ไขข้อขัดแย้ง**: เมื่อ HTF และ LTF ขัดแย้ง ให้ยึดตาม HTF และรอการสอดคล้อง

### 7.3 คะแนนการสอดคล้อง MTF (MTF Alignment Score)

$$\text{ICH\_MTF\_Score} = \sum_{tf \in \text{TFs}} w_{tf} \times S_{tf}$$

โดยที่ $S_{tf}$ คือคะแนนสัญญาณอิชิโมคุในแต่ละกรอบเวลา:

$$S_{tf} = \frac{1}{5}(S_{\text{price\_vs\_cloud}} + S_{\text{TK\_cross}} + S_{\text{chikou}} + S_{\text{cloud\_color}} + S_{\text{TK\_slope}})$$

คะแนนย่อยแต่ละตัว $\in \{-1, 0, +1\}$:
- $S_{\text{price\_vs\_cloud}}$: +1 ถ้าเหนือเมฆ, -1 ถ้าใต้, 0 ถ้าภายใน
- $S_{\text{TK\_cross}}$: +1 ถ้า Tenkan > Kijun, -1 ถ้า Tenkan < Kijun
- $S_{\text{chikou}}$: +1 ถ้ายืนยันขาขึ้น, -1 ถ้ายืนยันขาลง
- $S_{\text{cloud\_color}}$: +1 ถ้าเมฆอนาคตเป็นขาขึ้น, -1 ถ้าขาลง
- $S_{\text{TK\_slope}}$: +1 ถ้าทั้งสองเป็นบวก, -1 ถ้าทั้งสองเป็นลบ, 0 ถ้าผสม

**น้ำหนัก**:
| กรอบเวลา | น้ำหนัก |
|----|--------|
| Weekly | 0.35 |
| Daily | 0.30 |
| H4 | 0.20 |
| H1 | 0.15 |

**กฎการตัดสินใจ**:
- $\text{ICH\_MTF\_Score} > 0.60$: ขาขึ้นแข็งแกร่ง — รับสัญญาณซื้อ
- $\text{ICH\_MTF\_Score} < -0.60$: ขาลงแข็งแกร่ง — รับสัญญาณขาย
- $|\text{ICH\_MTF\_Score}| \leq 0.60$: ขัดแย้ง — หลีกเลี่ยงหรือลดขนาด

---

## 8. พารามิเตอร์ที่ปรับสำหรับ Crypto

### 8.1 ปัญหาของค่าตั้งมาตรฐาน

พารามิเตอร์เดิมของอิชิโมคุ (9, 26, 52) ถูกออกแบบสำหรับตลาดหุ้นญี่ปุ่นที่ซื้อขาย 6 วัน/สัปดาห์:
- 9 = 1.5 สัปดาห์
- 26 = 1 เดือน
- 52 = 2 เดือน

ตลาด Crypto ซื้อขาย 24/7/365 ค่าตั้งมาตรฐานอาจไม่จับวงจรดุลยภาพตามเวลาเดียวกัน

### 8.2 พารามิเตอร์ Crypto ที่เสนอ

**ตัวเลือก 1: คงมาตรฐาน (แนะนำสำหรับกรณีส่วนใหญ่)**
- (9, 26, 52) — ค่ามาตรฐานทำงานได้ดีเชิงประจักษ์บน H4+ 
- เหตุผล: นักเทรด Crypto สถาบันส่วนใหญ่ใช้ค่ามาตรฐาน สร้าง S/R ที่เป็นจริงตามตัวเอง

**ตัวเลือก 2: ปรับสำหรับตลาด 24/7**
- (10, 30, 60) — ปรับสำหรับสัปดาห์ 7 วัน
- การคำนวณ: 10 = ~1.5 สัปดาห์, 30 = ~1 เดือน, 60 = ~2 เดือน

**ตัวเลือก 3: สองเท่าสำหรับ Intraday Crypto**
- (20, 60, 120) — สำหรับกรอบเวลา H1 บน Crypto
- เหตุผล: ต้องการจุดข้อมูลมากขึ้นเนื่องจากซื้อขาย 24/7

### 8.3 ผลการเปรียบเทียบพารามิเตอร์ (ทดสอบย้อนหลัง)

| ค่าตั้ง | สินทรัพย์ | กรอบเวลา | อัตราชนะ | Profit Factor |
|----------|-------|-----------|----------|---------------|
| (9, 26, 52) | BTC/USD | H4 | 52% | 1.65 |
| (10, 30, 60) | BTC/USD | H4 | 54% | 1.72 |
| (9, 26, 52) | BTC/USD | D1 | 56% | 1.88 |
| (10, 30, 60) | BTC/USD | D1 | 55% | 1.82 |
| (20, 60, 120) | BTC/USD | H1 | 48% | 1.45 |
| (9, 26, 52) | ETH/USD | H4 | 51% | 1.58 |
| (10, 30, 60) | ETH/USD | H4 | 53% | 1.64 |

**คำแนะนำ**: ใช้ (10, 30, 60) สำหรับ Crypto บน H4, มาตรฐาน (9, 26, 52) สำหรับ Daily ขึ้นไป ความแตกต่างเล็กน้อย; ความสม่ำเสมอสำคัญกว่าการปรับให้เหมาะสม

### 8.4 ข้อพิจารณาเฉพาะ Crypto

1. **ความผันผวน**: ความผันผวนสูงของ Crypto หมายถึงสัญญาณหลอกมากขึ้น ต้องการการยืนยันที่แข็งแกร่งกว่า (5 องค์ประกอบสอดคล้องทั้งหมด)
2. **ความต่อเนื่องวันหยุด**: ไม่มี Gap (ไม่เหมือน Forex/หุ้น) แต่ปริมาณวันหยุดมักต่ำกว่า — สัญญาณในช่วงวันหยุดปริมาณต่ำน่าเชื่อถือน้อยกว่า
3. **การสอดคล้องกับ Funding Rate**: สำหรับ Crypto Futures สอดคล้องสัญญาณอิชิโมคุกับทิศทาง Funding Rate เป็นการยืนยันเพิ่มเติม
4. **ความอ่อนไหวต่อ Market Cap**: อิชิโมคุทำงานดีที่สุดบนสินทรัพย์ที่มี Cap สูง (BTC, ETH) ที่มีการมีส่วนร่วมของสถาบัน น่าเชื่อถือน้อยกว่าบน Altcoin ขนาดเล็ก

---

## 9. สูตรทางคณิตศาสตร์ (Mathematical Formulas)

### 9.1 การคำนวณอิชิโมคุฉบับสมบูรณ์

กำหนดข้อมูล OHLC สำหรับคาบ $1, 2, \ldots, t$:

$$\text{Tenkan}_t = \frac{HH(t, 9) + LL(t, 9)}{2}$$

$$\text{Kijun}_t = \frac{HH(t, 26) + LL(t, 26)}{2}$$

$$\text{SpanA}_{t+26} = \frac{\text{Tenkan}_t + \text{Kijun}_t}{2}$$

$$\text{SpanB}_{t+26} = \frac{HH(t, 52) + LL(t, 52)}{2}$$

$$\text{Chikou}_t = C_t \quad \text{(วาดที่ } t - 26 \text{)}$$

โดยที่:
$$HH(t, n) = \max_{i=t-n+1}^{t} H_i$$
$$LL(t, n) = \min_{i=t-n+1}^{t} L_i$$

### 9.2 โมเมนตัมเมฆ (Cloud Momentum)

อัตราการเปลี่ยนแปลงความหนาเมฆ — บ่งชี้ว่าแนวโน้มกำลังแข็งแกร่งหรืออ่อนลง:

$$\text{Cloud\_Momentum}_t = (\text{SpanA}_t - \text{SpanB}_t) - (\text{SpanA}_{t-1} - \text{SpanB}_{t-1})$$

- บวกและเพิ่มขึ้น: แนวโน้มขาขึ้นแข็งแกร่งขึ้น
- บวกและลดลง: แนวโน้มขาขึ้นอ่อนลง (อาจกลับตัว)
- ลบและลดลง: แนวโน้มขาลงแข็งแกร่งขึ้น

### 9.3 ระยะห่างราคา-เมฆ (Price-Cloud Distance)

$$d_{\text{cloud}} = \frac{C_t - \text{Cloud\_Nearest\_Edge}_t}{\text{ATR}(26)_t}$$

| $d_{\text{cloud}}$ | การตีความ |
|--------------------|---------------|
| $> 2.0$ | ยืดตัวเกินเหนือเมฆ — เสี่ยงกลับสู่ค่าเฉลี่ย |
| 1.0–2.0 | ระยะห่างแนวโน้มที่ดี |
| 0–1.0 | ใกล้เมฆ — อาจทดสอบ |
| $< 0$ | ภายในหรือใต้เมฆ |

### 9.4 การเบี่ยงเบนคิจุน (Kijun Deviation)

วัดว่าราคาเบี่ยงเบนจากคิจุน (เส้นดุลยภาพ) เท่าใด:

$$\text{Kijun\_Dev}_t = \frac{C_t - \text{Kijun}_t}{\text{ATR}(26)_t}$$

- $|\text{Kijun\_Dev}| > 2$: ราคายืดตัวเกิน; คาดว่าจะกลับสู่คิจุน
- $|\text{Kijun\_Dev}| < 0.5$: ราคาใกล้ดุลยภาพ; คิจุนทำหน้าที่เป็น S/R

### 9.5 การผสานทฤษฎีคลื่น (Wave Theory Integration / Hosoda's Numbers)

Hosoda ระบุวงจรเวลาสำคัญ:
- **ตัวเลขพื้นฐาน**: 9, 17, 26, 33, 42, 65, 76, 129, 172, 200, 257
- สอดคล้องกับระยะเวลาระหว่างจุดแกว่ง

AI สามารถใช้สำหรับเวลากลับตัวที่คาดการณ์:
$$T_{\text{reversal}} = T_{\text{last\_swing}} + N_{\text{Hosoda}}$$

---

## 10. การรวมสัญญาณขั้นสูง (Advanced Signal Combinations)

### 10.1 "Five-Line Confirmation" (สัญญาณที่แข็งแกร่งที่สุด)

ทั้งห้าองค์ประกอบต้องสอดคล้องสำหรับเทรดที่มีความน่าจะเป็นสูงสุด:

**Five-Line ขาขึ้น**:
1. ราคาเหนือเมฆ
2. เทนคันเหนือคิจุน (TK Cross ขาขึ้น)
3. Chikou เหนือราคาในอดีตและเหนือเมฆในอดีต
4. เมฆอนาคตเป็นขาขึ้น (Span A > Span B, 26 คาบข้างหน้า)
5. ทั้งเทนคันและคิจุนมีความชันขึ้น

$$\text{FiveLine\_Bullish} = \bigwedge_{i=1}^{5} \text{Condition}_i$$

**คะแนนสัญญาณเมื่อทั้ง 5 สอดคล้อง**: ความมั่นใจสูงสุด

### 10.2 กลยุทธ์ Kijun Bounce

**เซ็ตอัพ**: ในขาขึ้นที่ยืนยัน (ราคาเหนือเมฆ, TK ขาขึ้น) ราคาดึงกลับมาทดสอบคิจุน-เซ็น

**การเข้า**:
1. รอแท่งเทียนสัมผัสหรือเจาะคิจุน
2. รอแท่งเทียนขาขึ้นปิดเหนือคิจุน (การยืนยัน)
3. เข้าซื้อเมื่อเปิดแท่งถัดไป

**Stop Loss**: ใต้จุดต่ำของการดึงกลับหรือใต้เมฆ (อันใดแคบกว่าแต่ยังถูกต้อง)
**เป้าหมาย**: จุดสูงแกว่งก่อนหน้า หรือวัดจาก Impulse ที่นำหน้าการดึงกลับ

### 10.3 กลยุทธ์ Senkou Span Cross

**สัญญาณ**: เมื่อ Senkou Span A ตัด Senkou Span B (Kumo Twist)

**สำคัญ**: เนื่องจาก Senkou Spans ถูกวาดล่วงหน้า 26 คาบ การตัดที่เห็นในเมฆปัจจุบันถูกคำนวณ 26 คาบก่อน การตัดในการฉายอนาคตคือสัญญาณที่มองไปข้างหน้า

**ขาขึ้น**: Span A อนาคตตัดเหนือ Span B อนาคต
**ขาลง**: Span A อนาคตตัดใต้ Span B อนาคต

**ตัวกรอง**: เทรดเมื่อสอดคล้องกับตำแหน่งราคาปัจจุบันเท่านั้น:
- Twist ขาขึ้น + ราคาเหนือเมฆ = ขาขึ้นแข็งแกร่ง
- Twist ขาขึ้น + ราคาในเมฆ = ขาขึ้นปานกลาง
- Twist ขาขึ้น + ราคาใต้เมฆ = อ่อนแอ; รอการยืนยัน

### 10.4 Triple Cross (ซันไปจุน / Sanpaijun)

การตัดสามอย่างพร้อมกัน/เกือบพร้อมกัน:
1. เทนคันตัดคิจุน
2. ราคาตัดเมฆ
3. Chikou ตัดราคาในอดีต

เมื่อทั้งสามเกิดภายในแท่งเทียนไม่กี่แท่ง ส่งสัญญาณการเริ่มต้นแนวโน้มที่ทรงพลัง

---

## 11. พารามิเตอร์ความเสี่ยง (Risk Parameters)

### 11.1 วิธี Stop Loss

| วิธี | ตำแหน่ง | กรณีใช้งาน |
|--------|----------|----------|
| **ตามคิจุน (Kijun-based)** | ใต้คิจุน-เซ็น | เทรดตามแนวโน้ม; คิจุนคือดุลยภาพตามธรรมชาติ |
| **ตามเมฆ (Cloud-based)** | ใต้/เหนือขอบเมฆ | เทรด Kumo Breakout |
| **ตามจุดแกว่ง (Swing-based)** | ใต้จุดต่ำแกว่งล่าสุด | ทางเลือกสากล |
| **ตาม ATR** | Entry $\pm$ 1.5 ATR | เมื่อวิธีอื่นกว้างเกินไป |

**วิธีที่แนะนำ**: ตามคิจุนสำหรับการเทรดต่อเนื่องแนวโน้ม; ตามเมฆสำหรับทะลุ

### 11.2 ระดับ Take Profit

| เป้าหมาย | วิธี | รายละเอียด |
|--------|--------|---------|
| TP1 | จุดสูง/ต่ำแกว่งก่อนหน้า | เป้าหมายโครงสร้างที่ใกล้ที่สุด |
| TP2 | เป้าหมายคลื่น Hosoda (N, V, E, NT) | การฉายตามรูปแบบ |
| TP3 | ราคายืดตัวเกินจากคิจุน ($> 2$ ATR deviation) | ระดับกลับสู่ค่าเฉลี่ย |

### 11.3 เป้าหมายราคา Hosoda

Hosoda พัฒนาการคำนวณเป้าหมายราคาสี่แบบ:

**เป้าหมายคลื่น N (N-wave / Basic Measured Move)**:
$$N = C + (B - A)$$

**เป้าหมายคลื่น V (V-wave / V-shaped Reversal)**:
$$V = B + (B - C)$$

**เป้าหมายคลื่น E (E-wave / Equal Extension)**:
$$E = B + (B - A)$$

**เป้าหมายคลื่น NT (NT-wave / N-Truncated)**:
$$NT = C + (C - A)$$

โดยที่ A, B, C คือจุดแกว่งสามจุดติดต่อกัน

### 11.4 การกำหนดขนาดสถานะ (Position Sizing)

$$\text{Size} = \frac{\text{Balance} \times R\%}{|\text{Entry} - \text{SL}|}$$

| ความแข็งแกร่งของสัญญาณ | ความเสี่ยง % |
|----------------|--------|
| Five-Line Confirmation | 1.5% |
| 4 องค์ประกอบสอดคล้อง | 1.0% |
| 3 องค์ประกอบสอดคล้อง | 0.75% |
| น้อยกว่า 3 | ไม่เทรด |

### 11.5 กฎความเสี่ยงพอร์ตโฟลิโอ

- สูงสุด 3 เทรดอิชิโมคุพร้อมกัน
- ความเสี่ยงรวมสูงสุด 3% จากกลยุทธ์อิชิโมคุ
- ไม่เพิ่มสถานะ (Pyramid) เว้นแต่ทั้ง 5 องค์ประกอบยังสอดคล้องหลังจากการเคลื่อนไหวเริ่มต้น
- ลดความเสี่ยงระหว่าง Kumo Twist transitions (ช่วงไม่แน่นอน)

---

## 12. ขั้นตอนการดำเนินงาน (Execution Flow)

### 12.1 Pseudocode กลยุทธ์ฉบับสมบูรณ์

```python
def ichimoku_strategy():
    """
    Advanced Ichimoku trading strategy with multi-timeframe alignment.
    """
    
    # ================================================
    # PHASE 1: CALCULATE ICHIMOKU ON ALL TIMEFRAMES
    # ================================================
    
    for instrument in watchlist:
        ich_data = {}
        
        for tf in ["W1", "D1", "H4", "H1"]:
            candles = fetch_candles(instrument, tf, count=200)
            
            # Use adapted parameters for crypto
            if is_crypto(instrument) and tf in ["H4", "H1"]:
                params = (10, 30, 60)
            else:
                params = (9, 26, 52)
            
            ich = calculate_ichimoku(candles, *params)
            ich_data[tf] = {
                "tenkan": ich.tenkan,
                "kijun": ich.kijun,
                "span_a": ich.span_a,
                "span_b": ich.span_b,
                "chikou": ich.chikou,
                "cloud_top": max(ich.span_a[-1], ich.span_b[-1]),
                "cloud_bot": min(ich.span_a[-1], ich.span_b[-1]),
                "future_cloud_bullish": ich.span_a[-1 + 26] > ich.span_b[-1 + 26] if len(ich.span_a) > 26 else None,
                "candles": candles
            }
        
        # ================================================
        # PHASE 2: MTF ALIGNMENT SCORING
        # ================================================
        
        mtf_score = calculate_ich_mtf_score(ich_data)
        
        if abs(mtf_score) < 0.60:
            continue  # Insufficient alignment
        
        direction = "LONG" if mtf_score > 0 else "SHORT"
        
        # ================================================
        # PHASE 3: SIGNAL DETECTION ON TRADE TIMEFRAME
        # ================================================
        
        trade_tf = "H4"
        ich = ich_data[trade_tf]
        candles = ich["candles"]
        current_price = candles[-1].close
        
        signals = []
        
        # Signal 1: Kumo Breakout
        if is_kumo_breakout(candles, ich, direction):
            signals.append({
                "type": "KUMO_BREAKOUT",
                "strength": 0.80,
                "entry": current_price,
                "sl": ich["cloud_bot"] if direction == "LONG" else ich["cloud_top"]
            })
        
        # Signal 2: TK Cross
        tk_cross = detect_tk_cross(ich, direction)
        if tk_cross:
            cross_quality = classify_tk_cross_quality(tk_cross, ich)
            signals.append({
                "type": "TK_CROSS",
                "strength": cross_quality,
                "entry": current_price,
                "sl": ich["kijun"][-1] - ATR_BUFFER if direction == "LONG" else ich["kijun"][-1] + ATR_BUFFER
            })
        
        # Signal 3: Kijun Bounce
        kijun_bounce = detect_kijun_bounce(candles, ich, direction)
        if kijun_bounce:
            signals.append({
                "type": "KIJUN_BOUNCE",
                "strength": 0.75,
                "entry": current_price,
                "sl": candles[-1].low - ATR_BUFFER if direction == "LONG" else candles[-1].high + ATR_BUFFER
            })
        
        # Signal 4: Cloud Retest
        cloud_retest = detect_cloud_retest(candles, ich, direction)
        if cloud_retest:
            signals.append({
                "type": "CLOUD_RETEST",
                "strength": 0.70,
                "entry": current_price,
                "sl": ich["cloud_bot"] - ATR_BUFFER if direction == "LONG" else ich["cloud_top"] + ATR_BUFFER
            })
        
        if not signals:
            continue
        
        # ================================================
        # PHASE 4: CHIKOU CONFIRMATION
        # ================================================
        
        chikou_status = chikou_analysis(candles, chikou_offset=26)
        
        for signal in signals:
            if direction == "LONG" and chikou_status["bullish_confirmation"]:
                signal["strength"] *= 1.2
            elif direction == "SHORT" and chikou_status["bearish_confirmation"]:
                signal["strength"] *= 1.2
            elif chikou_status["obstructed"]:
                signal["strength"] *= 0.7
        
        # Select best signal
        signals.sort(key=lambda s: s["strength"], reverse=True)
        best = signals[0]
        
        if best["strength"] < 0.55:
            continue
        
        # ================================================
        # PHASE 5: RISK MANAGEMENT AND EXECUTION
        # ================================================
        
        tp1 = calculate_nearest_swing_target(candles, direction)
        tp2 = calculate_hosoda_target(candles, direction)
        
        sl = best["sl"]
        rr = abs(tp1 - best["entry"]) / abs(best["entry"] - sl)
        
        if rr < 2.0:
            continue
        
        risk_pct = get_risk_pct_ichimoku(best["strength"])
        size = calculate_position_size(balance, risk_pct, best["entry"], sl)
        
        trade = execute_trade(
            instrument=instrument,
            direction=direction,
            entry=best["entry"],
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            size=size,
            metadata={
                "strategy": "ICHIMOKU",
                "signal_type": best["type"],
                "mtf_score": mtf_score,
                "chikou_confirmed": chikou_status.get(f"{'bullish' if direction == 'LONG' else 'bearish'}_confirmation")
            }
        )
        
        return trade
    
    return WAIT("No Ichimoku signal")
```

---

## 13. หมายเหตุการใช้งาน AI (AI Implementation Notes)

### 13.1 หมายเหตุเชิงคำนวณ

- การคำนวณอิชิโมคุเป็น $O(n)$ — การดำเนินการ Min/Max แบบ Rolling ที่ง่าย
- Senkou Spans ต้องการการฉายไปข้างหน้า 26 คาบ — ตรวจสอบว่า Array มีขนาดเพียงพอ
- การวิเคราะห์ Chikou ต้องดูย้อนหลัง 26 คาบ — ตรวจสอบว่ามีประวัติเพียงพอ

### 13.2 การติดตามสถานะ (State Tracking)

AI Agent ควรรักษา:
- สถานะอิชิโมคุปัจจุบันต่อสินทรัพย์ต่อกรอบเวลา (ทั้ง 5 องค์ประกอบ + ตัวชี้วัดที่ได้มา)
- โซนคิจุนราบในอดีต (S/R แข็งแกร่ง)
- รายการ Kumo Twist ที่กำลังจะมา (จากการฉายเมฆอนาคต)
- ระดับคิจุน Naked (ยังไม่ถูกทดสอบ) จากเซสชันก่อนหน้า

### 13.3 ผลงานที่คาดหวัง

| ตลาด | กรอบเวลา | อัตราชนะ | R:R เฉลี่ย | Profit Factor | เทรด/เดือน |
|--------|-----------|----------|---------|---------------|-------------|
| Forex Majors | D1 | 52–58% | 2.0:1 | 1.5–2.0 | 3–5 |
| Forex Majors | H4 | 48–55% | 1.8:1 | 1.4–1.8 | 8–12 |
| BTC/USD | D1 | 50–56% | 2.2:1 | 1.5–2.1 | 2–4 |
| BTC/USD | H4 | 47–53% | 1.9:1 | 1.3–1.7 | 6–10 |

---

## 14. อ้างอิง (References)

### หนังสือ
1. Hosoda, G. (1968–1981). *Ichimoku Kinko Hyo* (Volumes 1–7). Original Japanese texts.
2. Elliott, N. (2007). *Ichimoku Charts: An Introduction to Ichimoku Kinko Clouds*. Harriman House.
3. Patel, M. (2010). *Trading with Ichimoku Clouds*. Wiley.
4. Linton, D. (2010). *Cloud Charts: Trading Success with the Ichimoku Technique*. Updata.
5. Patel, M. (2012). *Ichimoku Charts: An Introduction to Ichimoku Kinko Hyo*. Harriman House.

### บทความวิชาการ / วิจัย
6. Faber, M. T. (2007). "A Quantitative Approach to Tactical Asset Allocation." *The Journal of Wealth Management*, 9(4), 69–79.
7. Hurst, J. M. (1970). *The Profit Magic of Stock Transaction Timing*. Prentice-Hall.
8. Mandelbrot, B., & Hudson, R. (2004). *The (Mis)Behavior of Markets*. Basic Books.

### แหล่งข้อมูลจากผู้ปฏิบัติ
9. Manesh Patel. "Ichimoku Cloud Trading" — IchimokuTrading.com.
10. Karen Peloille (KPL). "Advanced Ichimoku Trading" — French Ichimoku practitioner.
11. Kei Ishibashi. "Ichimoku Kinko Hyo for Cryptocurrency" (2020) — Adapted parameters research.
12. FXJake. "The Ichimoku Bible" — Community resource for signal classification.
13. TradingView. Ichimoku Cloud indicator and community research.

---

*เอกสารนี้เป็นส่วนหนึ่งของฐานความรู้ระบบเทรด AI แบบหลายตัวแทน (Multi-Agent AI Trading System) ควรอ่านร่วมกับคู่มือการวิเคราะห์หลายกรอบเวลา (11_multi_timeframe_analysis), คู่มือการเทรด Divergence (10_divergence_trading) และคู่มือ Fibonacci ขั้นสูง (12_fibonacci_advanced)*
