# แผนผังการสะสม Wyckoff (Wyckoff Accumulation Schematic) — การวิเคราะห์แบบครบถ้วน

> **โมดูล**: แกนที่ 1 — กลยุทธ์การเทรด
> **หัวข้อ**: 02 — วิธี Wyckoff และโครงสร้างตลาด
> **ไฟล์**: 01_accumulation_schematic.md
> **เวอร์ชัน**: 1.0
> **อัปเดตล่าสุด**: 2026-04-12
> **ผู้เขียน**: ทีมฐานความรู้ — ระบบเทรด AI หลายเอเจนต์ NTT

---

## สารบัญ

1. [บทนำสู่การสะสม (Accumulation)](#1-บทนำสู่การสะสม-accumulation)
2. [แผนผังการสะสม #1 — มาตรฐาน](#2-แผนผังการสะสม-1--มาตรฐาน)
3. [แผนผังการสะสม #2 — แบบมี Spring](#3-แผนผังการสะสม-2--แบบมี-spring)
4. [การวิเคราะห์เฟสอย่างละเอียด](#4-การวิเคราะห์เฟสอย่างละเอียด)
5. [การวิเคราะห์ปริมาณการซื้อขายในแต่ละเฟส](#5-การวิเคราะห์ปริมาณการซื้อขายในแต่ละเฟส)
6. [การระบุแบบเรียลไทม์](#6-การระบุแบบเรียลไทม์)
7. [แบบจำลองทางคณิตศาสตร์](#7-แบบจำลองทางคณิตศาสตร์)
8. [การสะสมเทียบกับขาลงที่ยังดำเนินอยู่](#8-การสะสมเทียบกับขาลงที่ยังดำเนินอยู่)
9. [ตรรกะเข้า/ออกคำสั่ง](#9-ตรรกะเข้าออกคำสั่ง)
10. [พารามิเตอร์ความเสี่ยง](#10-พารามิเตอร์ความเสี่ยง)
11. [ขั้นตอนการดำเนินการ](#11-ขั้นตอนการดำเนินการ)
12. [การสะสมเฉพาะตลาด Forex](#12-การสะสมเฉพาะตลาด-forex)
13. [การสะสมเฉพาะตลาดคริปโต](#13-การสะสมเฉพาะตลาดคริปโต)
14. [ข้อผิดพลาดและกับดักที่พบบ่อย](#14-ข้อผิดพลาดและกับดักที่พบบ่อย)
15. [เอกสารอ้างอิง](#15-เอกสารอ้างอิง)

---

## 1. บทนำสู่การสะสม (Accumulation)

### 1.1 คำจำกัดความ

การสะสม (Accumulation) คือเฟสแรกของวัฏจักรตลาดตามแนวคิด Wyckoff เป็นช่วงที่ราคา **เคลื่อนตัวในกรอบ Sideways** ที่ก่อตัวขึ้นที่จุดต่ำสุดของขาลง ในระหว่างนี้ Composite Man (CM) — ซึ่งเป็นตัวแทนของผู้ประกอบการสถาบันรายใหญ่ — จะทยอยดูดซับอุปทาน (Selling Pressure) ที่มีอยู่อย่างเป็นระบบ และสร้างสถานะ Long ในราคาที่เหมาะสม

### 1.2 วัตถุประสงค์จากมุมมองของ CM

Composite Man จะต้องสะสมสถานะขนาดใหญ่ **โดยไม่** ทำให้ราคาขยับขึ้นอย่างมีนัยสำคัญ เพื่อทำเช่นนั้น CM จะ:

1. **สร้างความกลัว**: ใช้ Selling Climax และ Spring เพื่อสร้างความตื่นตระหนกในหมู่เทรดเดอร์รายย่อย
2. **ดูดซับอุปทาน**: ค่อย ๆ รับซื้อแรงขายที่ระดับแนวรับแต่ละครั้ง
3. **ทดสอบอุปทาน**: ปล่อยให้ราคาตกลงเป็นระยะเพื่อตรวจสอบว่ายังมีอุปทานเหลืออยู่หรือไม่ (หากอุปทานหมดลง การสะสมใกล้สมบูรณ์)
4. **สลัดขา Weak Hands**: ทำ Spring หลุดต่ำกว่าแนวรับเพื่อ Trigger จุดตัดขาดทุนและ Margin Call
5. **ยืนยันความสมบูรณ์**: อนุญาตให้เกิดการปรับตัวขึ้นแบบ Sign of Strength (SOS) ที่ทะลุแนวต้าน ยืนยันว่าอุปสงค์ได้เอาชนะอุปทานแล้ว

### 1.3 ระยะเวลาและสัดส่วน

ตามกฎของเหตุและผล (Law of Cause and Effect) ของ Wyckoff:

$$
\text{Expected Markup Move} \propto \text{Duration of Accumulation} \times \text{Width of Range}
$$

ที่แม่นยำกว่า:

$$
T_{\text{markup}} \approx \beta \cdot \sqrt{T_{\text{accumulation}}}
$$

โดยที่:
- $T_{\text{markup}}$ = ระยะเวลาที่คาดหวังของเฟส Markup
- $T_{\text{accumulation}}$ = ระยะเวลาของเฟสการสะสม (เป็นจำนวนแท่ง)
- $\beta$ = ค่าคงที่ตามสินทรัพย์ (โดยปกติ 2.0–5.0)

---

## 2. แผนผังการสะสม #1 — มาตรฐาน

### 2.1 แผนผัง ASCII

```
                    Accumulation Schematic #1 (Standard — No Spring)
                    
Price
  │
  │   ╲
  │    ╲  Prior Downtrend
  │     ╲
  │      ╲                         AR
  │    PS ╲                       ╱  ╲        SOS
  │    │   ╲                     ╱    ╲      ╱   ╲   
  │    ↓    ╲      ╱────────────╱──────╲────╱─────╲──── Creek (Resistance)
  │          ╲    ╱  ST(b)             ST           LPS  
  │           ╲  ╱     ╲              ╱ ╲         ╱  ╲
  │            ╲╱       ╲            ╱   ╲       ╱    ╲
  │    ────────SC────────╲──────────╱─────╲─────╱──────── Ice (Support)
  │                       ╲       ╱       ╲   ╱
  │                        ╲     ╱     Secondary Test
  │                         ╲   ╱      on higher low
  │                      ST in Phase B
  │
  │  Phase A  │    Phase B                │ Phase C│  Phase D   │Phase E
  │ (Stopping)│    (Building Cause)       │(Test)  │  (Trend)   │(Markup)
  │           │                           │        │            │
  └───────────┴───────────────────────────┴────────┴────────────┴──→ Time
  
  Volume:
  ████      ███      ██    █     ██   █    ████    ██    ████
  HIGH      HIGH    MED   LOW   MED  LOW   HIGH   LOW   HIGH
  (SC)     (ST/AR)        (test)           (SOS)  (LPS)  (BU)
```

### 2.2 เหตุการณ์สำคัญในแผนผัง #1

| เหตุการณ์ | ตัวย่อ | เฟส | ตำแหน่ง | คำอธิบาย |
|---|---|---|---|---|
| แนวรับเบื้องต้น (Preliminary Support) | PS | A | ก่อน SC | แรงซื้อสำคัญแรกหลังขาลงยาวนาน |
| จุดขายสุดขีด (Selling Climax) | SC | A | ด้านล่างของกรอบ | ขายตื่นตระหนกพร้อมปริมาณสุดขีด ช่วงกว้าง กลับตัว |
| การปรับตัวขึ้นอัตโนมัติ (Automatic Rally) | AR | A | ด้านบนของกรอบ | การดีดกลับอย่างรุนแรงจาก SC กำหนดแนวต้าน |
| การทดสอบรอง (Secondary Test) | ST | B | ใกล้ SC | การทดสอบซ้ำที่จุดต่ำ SC ด้วยปริมาณที่ลดลง |
| สัญญาณแห่งความแข็งแกร่ง (Sign of Strength) | SOS | D | เหนือ AR | การปรับตัวที่ทะลุแนวต้านของกรอบซื้อขาย |
| จุดพักรับสุดท้าย (Last Point of Support) | LPS | D | เหนือ SC | การย่อตัวหลัง SOS ด้วยปริมาณต่ำ |
| การย้อนกลับ (Back-Up) | BU | E | ใกล้ AR | การทดสอบซ้ำครั้งสุดท้ายของแนวต้านที่กลายเป็นแนวรับ |

---

## 3. แผนผังการสะสม #2 — แบบมี Spring

### 3.1 แผนผัง ASCII

```
                    Accumulation Schematic #2 (With Spring — Most Common)
                    
Price
  │
  │   ╲
  │    ╲  Prior Downtrend
  │     ╲
  │      ╲                         AR
  │    PS ╲                       ╱  ╲                    SOS
  │    │   ╲                     ╱    ╲     Test        ╱    ╲
  │    ↓    ╲      ╱────────────╱──────╲───╱──╲────────╱──────╲── Creek
  │          ╲    ╱  ST(b)             ST       ╲     ╱    LPS  ╲
  │           ╲  ╱     ╲              ╱ ╲        ╲   ╱     │     BU
  │            ╲╱       ╲            ╱   ╲        ╲ ╱      ↓     ╱
  │    ────────SC────────╲──────────╱─────╲────────╳───────────── Ice
  │                       ╲       ╱       ╲      ╱│╲
  │                        ╲     ╱         ╲    ╱ │ ╲
  │                         ╲   ╱           ╲  ╱  │  ← Test of Spring
  │                      ST in Phase B    Spring   │    (higher low)
  │                                    (shakeout)  │
  │                                                │
  │  Phase A  │    Phase B                │Phase C │  Phase D   │Phase E
  │ (Stopping)│    (Building Cause)       │(Test)  │  (Trend)   │(Markup)
  │           │                           │        │            │
  └───────────┴───────────────────────────┴────────┴────────────┴──→ Time
  
  Volume:
  ████      ███      ██    █     ██  ███  █     ████   ██    ████
  HIGH      HIGH    MED   LOW   MED  HIGH LOW   HIGH  LOW   HIGH
  (SC)     (ST/AR)        (test)   (Spring)(Test)(SOS) (LPS)  (BU)
```

### 3.2 การจำแนกประเภท Spring

Spring ถูกจำแนกตามความลึกของการทะลุต่ำกว่าแนวรับ:

| ประเภท | การทะลุ | ปริมาณ | ความเร็วในการกลับตัว | คุณค่าในการเทรด |
|---|---|---|---|---|
| **Spring #1** | ลึก (> 3% ต่ำกว่า) | สูงมาก | ช้า | ต่ำ — อาจบ่งบอกถึงความอ่อนแอต่อเนื่อง |
| **Spring #2** | ปานกลาง (1–3% ต่ำกว่า) | ปานกลาง-สูง | ปานกลาง-เร็ว | ปานกลาง — ต้องการการยืนยัน |
| **Spring #3** | ตื้น (< 1% ต่ำกว่า) | ต่ำ-ปานกลาง | เร็ว | สูง — Spring ที่ดีที่สุด CM ทดสอบด้วยความพยายามน้อยที่สุด |

$$
\text{Spring Quality Score} = \frac{1}{\text{Depth}^2} \times \frac{V_{\text{reversal\_bar}}}{V_{\text{breakdown\_bar}}} \times \text{Reversal Speed}
$$

โดยที่:
- Depth = การทะลุต่ำกว่าแนวรับเป็น % ของ ATR
- Reversal Speed = จำนวนแท่งที่ใช้กลับเหนือแนวรับ (ยิ่งน้อยยิ่งดี)

---

## 4. การวิเคราะห์เฟสอย่างละเอียด

### 4.1 เฟส A — การหยุดขาลง (Stopping the Downtrend)

เฟส A เป็นจุดสิ้นสุดของขาลงก่อนหน้าและจุดเริ่มต้นของกรอบ Sideways จุดประสงค์คือ **หยุดการร่วงลง** และสร้างขอบเขตแรกของกรอบซื้อขาย

#### 4.1.1 แนวรับเบื้องต้น (Preliminary Support — PS)

**คำจำกัดความ**: แรงซื้อสำคัญแรกที่ปรากฏหลังจากขาลงยาวนาน ราคาอาจทรงตัวชั่วคราว แต่ยังไม่ใช่จุดต่ำสุดสุดท้าย

**ลักษณะเด่น:**

| คุณลักษณะ | คำอธิบาย |
|---|---|
| **พฤติกรรมราคา** | แท่งเทียนลงช่วงกว้างที่ปิดที่ส่วนกลางหรือส่วนบน |
| **ปริมาณ** | เพิ่มขึ้นอย่างเห็นได้ชัดจากแท่งล่าสุด แต่ไม่สุดขีด |
| **บริบท** | เกิดหลังขาลงยาวนาน; ราคาร่วงมาหลายสัปดาห์/เดือน |
| **ตำแหน่งปิด** | ปิดที่ช่วงกลางถึงส่วนบนของกรอบแท่ง |
| **ความสำคัญ** | แจ้งเตือนว่าขาลงอาจใกล้หมดแรง |
| **ความน่าเชื่อถือ** | ต่ำเมื่ออยู่เดี่ยว ๆ — มีความหมายเมื่อตามด้วย SC |

**การตรวจจับทางคณิตศาสตร์:**

$$
\text{PS\_detected} = \begin{cases}
\text{true} & \text{if } V(t) > \bar{V}_{20} \times 1.5 \text{ AND } \text{CPos}(t) > 0.4 \text{ AND trend} = \text{DOWN} \\
\text{false} & \text{otherwise}
\end{cases}
$$

โดยที่ Close Position:
$$
\text{CPos}(t) = \frac{C(t) - L(t)}{H(t) - L(t)}
$$

```python
def detect_preliminary_support(candles, i, avg_volume, atr, trend):
    """
    Detect Preliminary Support (PS) event.
    
    Parameters:
        candles: list of OHLCV candles
        i: current index
        avg_volume: 20-period average volume
        atr: current ATR value
        trend: current detected trend ('DOWN', 'UP', 'SIDEWAYS')
    
    Returns:
        dict or None
    """
    if trend != 'DOWN':
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    # PS conditions
    conditions = {
        'downtrend': trend == 'DOWN',
        'increased_volume': c['volume'] > avg_volume * 1.5,
        'not_extreme_volume': c['volume'] < avg_volume * 3.5,
        'wide_spread': spread > atr * 0.8,
        'close_not_at_low': close_position > 0.35,
        'prior_decline': candles[i]['close'] < candles[max(0, i-20)]['close'],
    }
    
    if all(conditions.values()):
        return {
            'event': 'PS',
            'phase': 'A',
            'index': i,
            'price': c['close'],
            'volume_ratio': c['volume'] / avg_volume,
            'close_position': close_position,
            'confidence': sum(conditions.values()) / len(conditions),
            'conditions': conditions
        }
    
    return None
```

#### 4.1.2 จุดขายสุดขีด (Selling Climax — SC)

**คำจำกัดความ**: เหตุการณ์การขายสุดขีดที่กำหนดขอบเขตล่างของกรอบการสะสม ลักษณะเด่นคือปริมาณสุดขีด ช่วงราคากว้าง และราคาปิดใกล้หรือที่จุดต่ำสุด — ตามด้วยการกลับตัว

**ลักษณะเด่น:**

| คุณลักษณะ | คำอธิบาย |
|---|---|
| **พฤติกรรมราคา** | แท่งเทียนลงช่วงกว้างมาก มักมีหางล่างยาว |
| **ปริมาณ** | สูงที่สุดในขาลง — มักเป็น 3-5 เท่าของค่าเฉลี่ย |
| **ตำแหน่งปิด** | เริ่มปิดที่จุดต่ำ แต่มักฟื้นตัวปิดที่ช่วงล่าง-กลาง |
| **บริบท** | ตามหลัง PS; แสดงถึงการยอมจำนนและการขายตื่นตระหนก |
| **การกลับตัว** | การกลับตัวขึ้นอย่างรุนแรงตามมา (1-3 แท่ง) |
| **ความสำคัญ** | กำหนดจุดต่ำสุดของกรอบซื้อขาย (ระดับ Ice) |
| **ความน่าเชื่อถือ** | สูงเมื่อตามด้วย AR ภายใน 1-5 แท่ง |

**การตรวจจับทางคณิตศาสตร์:**

$$
\text{SC\_detected} = \begin{cases}
\text{true} & \text{if } V(t) > \bar{V}_{20} \times 2.5 \\
& \text{AND } \text{Spread}(t) > ATR \times 1.5 \\
& \text{AND } P(t) < P(t-20) \\
& \text{AND } \text{PS\_exists\_within}(30 \text{ bars}) \\
\text{false} & \text{otherwise}
\end{cases}
$$

ดัชนีความรุนแรงของ Selling Climax (Selling Climax Intensity Index):

$$
\text{SCI} = \frac{V(t)}{\bar{V}_{50}} \times \frac{\text{Spread}(t)}{ATR_{14}} \times (1 - \text{CPos}(t))
$$

โดยที่ค่า SCI ยิ่งสูงบ่งบอกถึง Selling Climax ที่รุนแรงกว่า ช่วงค่าปกติ:
- SCI < 3.0: Climax อ่อน — อาจไม่ยึดไว้ได้
- SCI 3.0–6.0: Climax ปานกลาง — น่าจะกำหนดกรอบได้
- SCI > 6.0: Climax แข็งแกร่ง — ความน่าจะเป็นสูงที่กรอบสะสมจะเกิดขึ้น

```python
def detect_selling_climax(candles, i, avg_volume_20, avg_volume_50, atr, ps_event):
    """
    Detect Selling Climax (SC) event.
    """
    if ps_event is None:
        return None  # PS must precede SC
    
    if i - ps_event['index'] > 30:
        return None  # PS too far away
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    # Core SC conditions
    conditions = {
        'extreme_volume': c['volume'] > avg_volume_20 * 2.5,
        'wide_spread': spread > atr * 1.3,
        'bearish_context': c['low'] < min(cc['low'] for cc in candles[max(0,i-20):i]),
        'ps_exists': ps_event is not None and (i - ps_event['index']) <= 30,
    }
    
    # Reversal confirmation (check next 1-3 bars if available)
    reversal_detected = False
    if i + 1 < len(candles):
        next_bar = candles[i + 1]
        if next_bar['close'] > next_bar['open'] and next_bar['close'] > c['close']:
            reversal_detected = True
    conditions['reversal_hint'] = reversal_detected or close_position > 0.3
    
    # Calculate intensity
    sci = (c['volume'] / avg_volume_50) * (spread / atr) * (1 - close_position)
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'SC',
            'phase': 'A',
            'index': i,
            'price_low': c['low'],
            'price_close': c['close'],
            'volume_ratio': c['volume'] / avg_volume_20,
            'spread_ratio': spread / atr,
            'close_position': close_position,
            'sci': sci,
            'confidence': sum(conditions.values()) / len(conditions),
            'range_bottom': c['low'],  # Defines Ice level
            'conditions': conditions
        }
    
    return None
```

#### 4.1.3 การปรับตัวขึ้นอัตโนมัติ (Automatic Rally — AR)

**คำจำกัดความ**: การปรับตัวขึ้นอย่างรุนแรงที่เกิดขึ้นทันทีหลัง Selling Climax เป็นปฏิกิริยาอัตโนมัติเมื่อผู้ขายชอร์ตปิดสถานะและนักล่าของถูก เข้าซื้อ AR กำหนดขอบเขตบนของกรอบสะสม (ระดับ Creek)

**ลักษณะเด่น:**

| คุณลักษณะ | คำอธิบาย |
|---|---|
| **พฤติกรรมราคา** | การปรับตัวขึ้นอย่างรุนแรงพร้อมแท่งขาขึ้นหลายแท่ง ย้อนกลับ 50–100% ของการร่วงลงของ SC |
| **ปริมาณ** | ปานกลาง-สูง ลดลงจากระดับ SC |
| **ระยะเวลา** | สั้น — โดยปกติ 3–10 แท่ง |
| **ตำแหน่งปิด** | แท่งปิดที่ส่วนบนอย่างสม่ำเสมอ |
| **ความสำคัญ** | กำหนดยอดของกรอบซื้อขาย (Creek/แนวต้าน) |
| **ทำไมจึงหยุด** | อุปทานกลับเข้ามาจากแรงขายด้านบน |

**การตรวจจับทางคณิตศาสตร์:**

$$
\text{AR\_detected} = \begin{cases}
\text{true} & \text{if SC exists within 10 bars} \\
& \text{AND } \sum_{j=\text{SC}}^{t} \Delta P(j) > 0.5 \times |\text{SC decline}| \\
& \text{AND } \text{rally bars} \geq 3 \\
& \text{AND } V_{\text{avg,rally}} > \bar{V}_{20} \times 0.8 \\
\text{false} & \text{otherwise}
\end{cases}
$$

```python
def detect_automatic_rally(candles, i, sc_event, avg_volume, atr):
    """
    Detect Automatic Rally (AR) event.
    AR is detected at the peak of the rally following the SC.
    """
    if sc_event is None:
        return None
    
    sc_idx = sc_event['index']
    if i - sc_idx > 15 or i - sc_idx < 2:
        return None
    
    # Check if we're at a swing high after the SC
    if i + 1 >= len(candles):
        return None
    
    current_high = candles[i]['high']
    prev_high = candles[i-1]['high'] if i > 0 else 0
    next_close = candles[i+1]['close'] if i+1 < len(candles) else candles[i]['close']
    
    # AR is the first significant swing high after SC
    is_swing_high = (candles[i]['high'] >= max(c['high'] for c in candles[sc_idx:i+1]))
    price_reverting = next_close < candles[i]['close']
    
    # Rally magnitude
    sc_low = sc_event['price_low']
    rally_size = current_high - sc_low
    
    # Calculate retracement of the decline that led to SC
    pre_sc_high = max(c['high'] for c in candles[max(0, sc_idx-20):sc_idx])
    sc_decline = pre_sc_high - sc_low
    retracement = rally_size / sc_decline if sc_decline > 0 else 0
    
    conditions = {
        'follows_sc': (i - sc_idx) >= 2 and (i - sc_idx) <= 15,
        'is_swing_high': is_swing_high,
        'significant_rally': rally_size > atr * 1.5,
        'minimum_retracement': retracement >= 0.3,
        'price_starting_to_revert': price_reverting,
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'AR',
            'phase': 'A',
            'index': i,
            'price_high': current_high,
            'rally_size': rally_size,
            'retracement_pct': retracement,
            'confidence': sum(conditions.values()) / len(conditions),
            'range_top': current_high,  # Defines Creek level
            'conditions': conditions
        }
    
    return None
```

### 4.2 เฟส B — การสร้างเหตุ (Building the Cause)

เฟส B เป็นเฟสที่ยาวนานที่สุดของการสะสม จุดประสงค์คือให้ Composite Man **ดูดซับอุปทานที่เหลืออยู่** ภายในกรอบซื้อขาย เฟสนี้สร้าง "เหตุ" ที่จะก่อให้เกิด "ผล" (การขยับขึ้น) ในภายหลัง

#### 4.2.1 การทดสอบรอง (Secondary Test — ST)

**คำจำกัดความ**: การทดสอบซ้ำพื้นที่ Selling Climax ด้วยปริมาณที่ลดลงและช่วงราคาที่แคบลง ยืนยันว่าอุปสงค์กำลังเอาชนะอุปทานที่ระดับเหล่านี้

**ลักษณะเด่น:**

| คุณลักษณะ | คำอธิบาย |
|---|---|
| **พฤติกรรมราคา** | ปรับตัวลงไปใกล้หรือที่จุดต่ำ SC แต่มักยืนเหนือ |
| **ปริมาณ** | ต่ำกว่า SC อย่างมีนัยสำคัญ — นี่คือการยืนยันที่สำคัญ |
| **ช่วงราคา** | แคบกว่าแท่ง SC |
| **ราคาปิด** | ควรปิดเหนือจุดต่ำ SC |
| **ความถี่** | อาจเกิดขึ้น 2–4 ครั้งในเฟส B |
| **จุดประสงค์** | ทดสอบว่าผู้ขายหมดแรงที่ระดับ SC หรือไม่ |

**การประเมินคุณภาพ ST:**

$$
\text{ST\_Quality} = \frac{V_{\text{SC}}}{V_{\text{ST}}} \times \frac{\text{Spread}_{\text{SC}}}{\text{Spread}_{\text{ST}}} \times \left(1 + \frac{P_{\text{ST\_low}} - P_{\text{SC\_low}}}{\text{ATR}}\right)
$$

ค่าที่สูงกว่าบ่งบอกถึง ST คุณภาพดีกว่า (อุปทานถูกดูดซับมากกว่า):
- ST Quality < 1.5: อ่อน — อุปทานยังคงมี
- ST Quality 1.5–3.0: ปานกลาง — อุปทานลดลง
- ST Quality > 3.0: แข็งแกร่ง — อุปทานหมดลงเกือบหมด

```python
def detect_secondary_test(candles, i, sc_event, ar_event, avg_volume, atr):
    """
    Detect Secondary Test (ST) of the Selling Climax.
    """
    if sc_event is None or ar_event is None:
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    sc_low = sc_event['price_low']
    range_height = ar_event['price_high'] - sc_low
    
    # ST should be near SC low (within 15% of range from bottom)
    proximity_to_sc = (c['low'] - sc_low) / range_height if range_height > 0 else 1.0
    
    conditions = {
        'near_sc_level': abs(proximity_to_sc) < 0.15,
        'lower_volume': c['volume'] < sc_event['volume_ratio'] * avg_volume * 0.7,
        'narrower_spread': spread < sc_event['spread_ratio'] * atr * 0.8,
        'holds_above_sc': c['low'] >= sc_low - atr * 0.3,
        'after_ar': i > ar_event['index'],
        'bullish_close': close_position > 0.3,
    }
    
    # Calculate quality
    vol_ratio = (sc_event['volume_ratio'] * avg_volume) / c['volume'] if c['volume'] > 0 else 0
    spread_ratio = (sc_event['spread_ratio'] * atr) / spread if spread > 0 else 0
    level_bonus = 1 + max(0, (c['low'] - sc_low) / atr)
    quality = vol_ratio * spread_ratio * level_bonus
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'ST',
            'phase': 'B',
            'index': i,
            'price_low': c['low'],
            'quality': quality,
            'volume_vs_sc': c['volume'] / (sc_event['volume_ratio'] * avg_volume),
            'proximity_to_sc': proximity_to_sc,
            'confidence': sum(conditions.values()) / len(conditions),
            'interpretation': 'STRONG' if quality > 3.0 else 'MODERATE' if quality > 1.5 else 'WEAK',
            'conditions': conditions
        }
    
    return None
```

#### 4.2.2 ลักษณะเด่นของเฟส B

ในระหว่างเฟส B ราคาแกว่งตัวระหว่างแนวรับ (พื้นที่ SC) และแนวต้าน (พื้นที่ AR) สิ่งที่ต้องสังเกตคือ:

```
Phase B — Supply Absorption Pattern
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Price   AR ─────────────────────────────────────────── Creek
         │  ╱╲      ╱╲         ╱╲        ╱╲  ╱╲
         │ ╱  ╲    ╱  ╲       ╱  ╲      ╱  ╲╱  ╲
         │╱    ╲  ╱    ╲     ╱    ╲    ╱         ╲
         │      ╲╱      ╲   ╱      ╲  ╱           ╲
        SC ──────────────╲─╱────────╲╱──────────── Ice
                          ╳
                   (possible test
                    below support)

Volume  ████  ██  ███  ██  █   ██  █  █   █  ██  █   ██
        HIGH      MED      LOW      LOW      LOW      LOW

         ← Supply being absorbed → ← Supply nearly exhausted →

สิ่งที่สังเกตสำคัญ:
  1. ปริมาณในการทดสอบแนวรับ ลดลง ตามเวลา
  2. ปริมาณในการปรับตัวขึ้น อาจเพิ่มขึ้นหรือคงที่
  3. กรอบอาจแคบลงเมื่อใกล้สิ้นสุด (coiling)
  4. การทดสอบแนวรับแต่ละครั้งพบอุปทานน้อยลง
  5. การปรับตัวขึ้นแต่ละครั้งพบแนวต้านน้อยลง (อุปทานอ่อนตัว)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**การประมาณระยะเวลาเฟส B:**

$$
T_B \approx 0.60 \times T_{\text{total\_accumulation}}
$$

เฟส B โดยปกติคิดเป็น 50–70% ของระยะเวลาการสะสมทั้งหมด

### 4.3 เฟส C — การทดสอบ Spring

เฟส C เป็น **เฟสที่สำคัญที่สุด** สำหรับการเทรด มีเหตุการณ์ Spring — การสลัดครั้งสุดท้ายที่แสดงถึงการทดสอบอุปทานครั้งสุดท้ายของ Composite Man ก่อนเริ่มขาขึ้น

#### 4.3.1 Spring (การสลัด/Shakeout)

**คำจำกัดความ**: การทะลุเท็จต่ำกว่าระดับแนวรับ (พื้นที่ SC) ที่กลับตัวอย่างรวดเร็ว CM ตั้งใจดันราคาให้ต่ำกว่าแนวรับเพื่อ Trigger จุดตัดขาดทุนรายย่อยและสะสมจากการขายที่ราคาต่ำกว่ามูลค่า

**ลักษณะเด่น:**

| คุณลักษณะ | คำอธิบาย |
|---|---|
| **พฤติกรรมราคา** | การทะลุต่ำกว่าแนวรับของกรอบชั่วคราว ตามด้วยการกลับตัวเร็ว |
| **ปริมาณ** | ผันแปร — Spring Type 3 มีปริมาณต่ำ (อุดมคติ) |
| **ระยะเวลา** | เร็ว — ปกติ 1–3 แท่งต่ำกว่าแนวรับก่อนกลับเหนือ |
| **ความลึก** | ไม่ควรเกิน 2–3% ต่ำกว่าแนวรับ (ลึกกว่า = อาจล้มเหลว) |
| **จุดประสงค์** | Trigger Stop Loss สลัดนักลงทุนที่ไม่มั่นคง ทดสอบอุปทานที่เหลือ |
| **ความสำคัญ** | จุดเข้าที่มีความน่าจะเป็นสูงสุดในการสะสมทั้งหมด |

**การจำแนกประเภท Spring (รายละเอียด):**

| ประเภท | ความลึก (% ของ ATR) | ปริมาณ | ราคาปิด | แท่งกลับตัว | การดำเนินการ |
|---|---|---|---|---|---|
| Type 3 (ดีที่สุด) | < 0.5 ATR ต่ำกว่า | ต่ำถึงปานกลาง | ปิดเหนือแนวรับ | 1 แท่ง | ซื้อเชิงรุก |
| Type 2 (ดี) | 0.5–1.5 ATR ต่ำกว่า | ปานกลางถึงสูง | ปิดใกล้/เหนือแนวรับ | 1–3 แท่ง | ซื้อเมื่อทดสอบ |
| Type 1 (เสี่ยง) | > 1.5 ATR ต่ำกว่า | สูงมาก | ปิดต่ำกว่าแนวรับมาก | 3–5+ แท่ง | รอการยืนยัน |

```python
def detect_spring(candles, i, range_support, range_resistance, avg_volume, atr, st_events):
    """
    Detect Spring (shakeout below support).
    """
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    # Must penetrate below support
    if c['low'] >= range_support:
        return None
    
    # Calculate penetration depth
    depth = range_support - c['low']
    depth_atr = depth / atr
    
    # Close must recover (at least partially)
    close_above_support = c['close'] >= range_support
    close_near_support = c['close'] >= range_support - atr * 0.2
    
    # Classify spring type
    if depth_atr < 0.5 and c['volume'] <= avg_volume * 1.3:
        spring_type = 3  # Best
        base_confidence = 0.9
    elif depth_atr < 1.5 and c['volume'] <= avg_volume * 2.0:
        spring_type = 2  # Good
        base_confidence = 0.7
    elif depth_atr < 3.0:
        spring_type = 1  # Risky
        base_confidence = 0.5
    else:
        return None  # Too deep — likely breakdown, not spring
    
    # Volume on spring vs prior ST events
    vol_decreasing_on_tests = True
    if len(st_events) >= 2:
        for j in range(1, len(st_events)):
            if st_events[j].get('volume_vs_sc', 1) >= st_events[j-1].get('volume_vs_sc', 0) * 1.1:
                vol_decreasing_on_tests = False
    
    conditions = {
        'penetrates_support': c['low'] < range_support,
        'limited_depth': depth_atr < 2.0,
        'recovers': close_above_support or close_near_support,
        'not_extreme_volume': c['volume'] < avg_volume * 3.0,
        'decreasing_supply': vol_decreasing_on_tests,
        'bullish_close': close_position > 0.4,
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'SPRING',
            'phase': 'C',
            'index': i,
            'spring_type': spring_type,
            'price_low': c['low'],
            'price_close': c['close'],
            'depth': depth,
            'depth_atr': depth_atr,
            'volume_ratio': c['volume'] / avg_volume,
            'close_above_support': close_above_support,
            'confidence': base_confidence * (sum(conditions.values()) / len(conditions)),
            'trade_action': {
                3: 'AGGRESSIVE_BUY',
                2: 'BUY_ON_TEST',
                1: 'WAIT_FOR_CONFIRMATION'
            }[spring_type],
            'stop_loss': c['low'] - atr * 0.5,
            'conditions': conditions
        }
    
    return None
```

#### 4.3.2 การทดสอบ Spring (Test of the Spring)

**คำจำกัดความ**: หลังจาก Spring ราคาอาจย่อตัวกลับมาใกล้จุดต่ำ Spring เพื่อ **ยืนยัน** ว่าอุปทานหมดลงแล้ว การทดสอบควรมีปริมาณต่ำกว่า Spring และควรยืนเหนือจุดต่ำ Spring

**ลักษณะเด่น:**

| คุณลักษณะ | คำอธิบาย |
|---|---|
| **พฤติกรรมราคา** | ย่อตัวไปใกล้จุดต่ำ Spring แต่ยืนเหนือ (higher low) |
| **ปริมาณ** | ต้องต่ำกว่าปริมาณ Spring — นี่คือการยืนยัน |
| **ระยะเวลา** | 3–10 แท่งหลัง Spring |
| **ราคาปิด** | ควรปิดเหนือระดับแนวรับ |
| **ความสำคัญ** | ยืนยันว่าอุปทานหมดลง — จุดเข้าที่มีความเชื่อมั่นสูงสุด |

```python
def detect_test_of_spring(candles, i, spring_event, avg_volume, atr):
    """
    Detect the Test after a Spring event.
    This is the highest-confidence entry point.
    """
    if spring_event is None:
        return None
    
    # Must be within reasonable time after spring
    bars_since_spring = i - spring_event['index']
    if bars_since_spring < 2 or bars_since_spring > 15:
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    # Price must be near or slightly above spring low
    spring_low = spring_event['price_low']
    proximity = abs(c['low'] - spring_low) / atr
    
    conditions = {
        'near_spring_area': proximity < 1.5,
        'holds_above_spring_low': c['low'] > spring_low,
        'lower_volume': c['volume'] < spring_event['volume_ratio'] * avg_volume * 0.8,
        'bullish_close': close_position > 0.5,
        'narrower_spread': spread < atr * 1.0,
        'higher_low': c['low'] > spring_low,
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'TEST_OF_SPRING',
            'phase': 'C',
            'index': i,
            'price_low': c['low'],
            'price_close': c['close'],
            'distance_from_spring': c['low'] - spring_low,
            'volume_vs_spring': c['volume'] / (spring_event['volume_ratio'] * avg_volume),
            'confidence': 0.90 * (sum(conditions.values()) / len(conditions)),
            'trade_action': 'STRONG_BUY',
            'stop_loss': spring_low - atr * 0.3,
            'conditions': conditions
        }
    
    return None
```

### 4.4 เฟส D — การขยับขึ้นภายในกรอบ (Markup Within the Range)

เฟส D ยืนยันว่าอุปสงค์ได้เอาชนะอุปทานอย่างเด็ดขาด เหตุการณ์ Sign of Strength (SOS) และ Last Point of Support (LPS) เกิดขึ้นที่นี่

#### 4.4.1 สัญญาณแห่งความแข็งแกร่ง (Sign of Strength — SOS)

**คำจำกัดความ**: การปรับตัวขึ้นอย่างแข็งแกร่งพร้อมปริมาณที่เพิ่มขึ้นและช่วงราคาที่กว้างขึ้น ที่ทะลุเหนือแนวต้าน (Creek) ของกรอบซื้อขาย ยืนยันว่าการสะสมสมบูรณ์และ Markup เริ่มต้น

**ลักษณะเด่น:**

| คุณลักษณะ | คำอธิบาย |
|---|---|
| **พฤติกรรมราคา** | การเคลื่อนที่แบบ Impulse ขึ้นอย่างแข็งแกร่ง ทะลุเหนือ AR high/Creek resistance |
| **ปริมาณ** | เพิ่มขึ้นอย่างมาก — สูงที่สุดนับตั้งแต่ SC |
| **ช่วงราคา** | แท่งขาขึ้นกว้าง |
| **ราคาปิด** | ปิดใกล้จุดสูงสุดของแท่งอย่างสม่ำเสมอ |
| **ความสำคัญ** | ยืนยันการเปลี่ยนเฟสจากการสะสมเป็น Markup |
| **การยืนยัน Breakout** | ราคาต้องปิดเหนือ Creek ไม่ใช่แค่ Wick เหนือ |

$$
\text{SOS\_Strength} = \frac{V_{\text{SOS}}}{\bar{V}_{20}} \times \frac{\text{Spread}_{\text{SOS}}}{ATR} \times \text{CPos}_{\text{SOS}} \times \frac{|\Delta P_{\text{SOS}}|}{\text{Range Height}}
$$

```python
def detect_sign_of_strength(candles, i, creek_level, avg_volume, atr, range_height):
    """
    Detect Sign of Strength (SOS) — breakout above Creek.
    """
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    # Must close above Creek resistance
    if c['close'] <= creek_level:
        return None
    
    # Check breakout quality
    breakout_distance = c['close'] - creek_level
    breakout_atr = breakout_distance / atr
    
    conditions = {
        'closes_above_creek': c['close'] > creek_level,
        'significant_breakout': breakout_atr > 0.3,
        'strong_volume': c['volume'] > avg_volume * 1.5,
        'wide_spread': spread > atr * 0.8,
        'bullish_close': close_position > 0.6,
        'body_mostly_above_creek': (c['open'] + c['close']) / 2 > creek_level,
    }
    
    # Calculate SOS strength
    strength = (c['volume'] / avg_volume) * (spread / atr) * close_position
    strength *= breakout_distance / range_height if range_height > 0 else 0
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'SOS',
            'phase': 'D',
            'index': i,
            'price_close': c['close'],
            'price_high': c['high'],
            'breakout_distance': breakout_distance,
            'strength': strength,
            'volume_ratio': c['volume'] / avg_volume,
            'confidence': sum(conditions.values()) / len(conditions),
            'interpretation': 'STRONG' if strength > 2.0 else 'MODERATE' if strength > 1.0 else 'WEAK',
            'conditions': conditions
        }
    
    return None
```

#### 4.4.2 จุดพักรับสุดท้าย (Last Point of Support — LPS)

**คำจำกัดความ**: การย่อตัวหลัง SOS ที่พบแนวรับที่หรือเหนือระดับ Creek (แนวต้านเดิมกลายเป็นแนวรับ) ปริมาณควรลดลงในระหว่างการย่อตัว

**ลักษณะเด่น:**

| คุณลักษณะ | คำอธิบาย |
|---|---|
| **พฤติกรรมราคา** | ย่อตัวไปที่ระดับ Creek; ยืนเหนือหรือที่ Creek |
| **ปริมาณ** | ลดลง — ต่ำกว่าปริมาณ SOS อย่างมาก |
| **ช่วงราคา** | แคบลง — แท่งเทียนเล็กลง |
| **ราคาปิด** | ควรปิดเหนือระดับ Creek |
| **ความสำคัญ** | จุดเข้าที่ดีรองลงมา (หลัง Test of Spring) สำหรับผู้ที่พลาด Spring |
| **จุดตัดขาดทุน** | ต่ำกว่าระดับ Creek |

```python
def detect_last_point_of_support(candles, i, sos_event, creek_level, avg_volume, atr):
    """
    Detect Last Point of Support (LPS) — pullback to Creek after SOS.
    """
    if sos_event is None:
        return None
    
    bars_since_sos = i - sos_event['index']
    if bars_since_sos < 2 or bars_since_sos > 20:
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    # Price should be pulling back toward Creek
    proximity_to_creek = abs(c['low'] - creek_level) / atr
    
    conditions = {
        'near_creek': proximity_to_creek < 1.0,
        'holds_above_creek': c['low'] >= creek_level - atr * 0.2,
        'declining_volume': c['volume'] < sos_event['volume_ratio'] * avg_volume * 0.6,
        'narrow_spread': spread < atr * 0.9,
        'bullish_close': close_position > 0.4,
        'pullback_from_sos': c['close'] < sos_event['price_high'],
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'LPS',
            'phase': 'D',
            'index': i,
            'price_low': c['low'],
            'price_close': c['close'],
            'distance_from_creek': c['low'] - creek_level,
            'volume_ratio': c['volume'] / avg_volume,
            'confidence': 0.80 * (sum(conditions.values()) / len(conditions)),
            'trade_action': 'BUY',
            'stop_loss': creek_level - atr * 0.5,
            'conditions': conditions
        }
    
    return None
```

### 4.5 เฟส E — การเริ่มต้น Markup

#### 4.5.1 การย้อนกลับสู่ขอบ Creek (Back-Up/BU/LPS)

**คำจำกัดความ**: การย่อตัวครั้งสุดท้ายหลังราคาทะลุออกจากกรอบสะสม ราคาย้อนกลับมาที่พื้นที่ Creek ครั้งสุดท้ายก่อนเริ่ม Markup ที่ยั่งยืน

| คุณลักษณะ | คำอธิบาย |
|---|---|
| **พฤติกรรมราคา** | ย่อตัวมาที่พื้นที่ Creek จากด้านบน; อาจเป็นตัวเดียวกับ LPS |
| **ปริมาณ** | ต่ำ — อุปทานหมดลง |
| **ความสำคัญ** | โอกาสสุดท้ายในการเข้าก่อน Markup ที่ยั่งยืน |
| **ความเสี่ยง** | หากราคาตกกลับต่ำกว่า Creek ด้วยปริมาณสูง การสะสมอาจล้มเหลว |

```
Phase E — Markup Beginning
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                                          ╱
                                         ╱
                                        ╱  Markup continues
                                SOS    ╱
                               ╱  ╲   ╱
                              ╱    ╲ ╱
  Creek ─────────────────────╱──────╳─── BU (Back-Up)
                            ╱      LPS
  ════════════════════════╱════════════
                         ╱
        Accumulation    ╱
        Range          ╱
                      ╱
  ════════════════════════════════════
  
  ปริมาณที่ BU: ต่ำ (ยืนยันว่าอุปทานหมดลง)
  จุดเข้า: ซื้อที่ BU โดยมี SL ต่ำกว่า Creek
  เป้าหมาย: การเคลื่อนที่ที่คาดจากการวัดเหตุ (Cause)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. การวิเคราะห์ปริมาณการซื้อขายในแต่ละเฟส

### 5.1 ตารางลักษณะปริมาณ

| เหตุการณ์ | ปริมาณที่คาดหวัง | เทียบกับ 20-SMA | ช่วงราคา | ตำแหน่งปิด | การตีความหลัก |
|---|---|---|---|---|---|
| PS | เพิ่มขึ้น | 1.5–2.5 เท่า | กว้าง | กลาง-บน | อุปสงค์ปรากฏขึ้นครั้งแรก |
| SC | สุดขีด | 2.5–5.0 เท่า | กว้างมาก | ล่าง-กลาง | ขายยอมจำนน CM กำลังซื้อ |
| AR | ปานกลาง-สูง | 1.0–2.0 เท่า | กว้าง | ส่วนบน | ปิด Short + ล่าของถูก |
| ST | ลดลง | 0.5–0.8 เท่า เทียบ SC | แคบกว่า | เหนือกลาง | อุปทานกำลังหมด |
| การทดสอบเฟส B | ลดลงเรื่อย ๆ | 0.3–0.7 เท่า เทียบ SC | แคบลงเรื่อย ๆ | ผันแปร | การดูดซับอย่างต่อเนื่อง |
| Spring | ผันแปร | 0.5–2.0 เท่า | ปานกลาง | ฟื้นตัว | สลัด — ทดสอบอุปทาน |
| การทดสอบ Spring | ต่ำ | 0.3–0.6 เท่า | แคบ | ส่วนบน | ยืนยันอุปทานหมดลง |
| SOS | สูง | 1.5–3.0 เท่า | กว้าง | ใกล้จุดสูงสุด | อุปสงค์เอาชนะอุปทาน |
| LPS | ต่ำ | 0.3–0.6 เท่า | แคบ | เหนือกลาง | ไม่มีอุปทานที่ระดับสูงกว่า |
| BU | ต่ำ | 0.3–0.5 เท่า | แคบ | เหนือกลาง | การทดสอบอุปทานครั้งสุดท้าย |

### 5.2 แนวโน้มปริมาณระหว่างการสะสม

$$
V_{\text{tests}}(k) = V_{\text{SC}} \cdot e^{-\lambda k}
$$

โดยที่:
- $V_{\text{tests}}(k)$ = ปริมาณที่การทดสอบแนวรับครั้งที่ $k$
- $V_{\text{SC}}$ = ปริมาณที่ Selling Climax
- $\lambda$ = อัตราการลดลง (โดยปกติ 0.3–0.6)

การลดลงแบบ Exponential ของปริมาณในการทดสอบที่ต่อเนื่องกันเป็นหนึ่งในสัญญาณยืนยันที่แข็งแกร่งที่สุดของการสะสม

### 5.3 คะแนนความแตกต่างของปริมาณ (Volume Divergence Score)

$$
\text{VDS}(t) = \frac{\sum_{i=1}^{n} [V_{\text{test},i} \cdot \mathbb{1}(P_{\text{test},i} \leq P_{\text{SC}} + \epsilon)]}{\sum_{i=1}^{n} [V_{\text{rally},i} \cdot \mathbb{1}(P_{\text{rally},i} \geq P_{\text{AR}} - \epsilon)]}
$$

โดยที่:
- VDS < 0.5: สัญญาณการสะสมที่แข็งแกร่ง (ปริมาณลดลงในการทดสอบเทียบกับการปรับตัวขึ้น)
- VDS 0.5–1.0: สัญญาณปานกลาง
- VDS > 1.0: สัญญาณอ่อนหรือไม่มีการสะสม

---

## 6. การระบุแบบเรียลไทม์

### 6.1 การตรวจจับเฟสแบบก้าวหน้า

ในการเทรดแบบเรียลไทม์ การสะสมต้องถูกระบุแบบก้าวหน้าตามเหตุการณ์ที่คลี่คลาย:

```
Real-Time Accumulation Detection State Machine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

State 0: WATCHING (ไม่มีเหตุการณ์ที่ตรวจพบ)
  │
  ├── ตรวจพบ PS → State 1: PS_DETECTED (ความเชื่อมั่น 10%)
  │
State 1: PS_DETECTED
  │
  ├── ตรวจพบ SC → State 2: SC_DETECTED (ความเชื่อมั่น 25%)
  ├── หมดเวลา (30 แท่ง) → State 0: WATCHING
  │
State 2: SC_DETECTED
  │
  ├── ตรวจพบ AR → State 3: RANGE_FORMING (ความเชื่อมั่น 40%)
  ├── จุดต่ำใหม่ต่ำกว่า SC → State 0: WATCHING (ล้มเหลว)
  │
State 3: RANGE_FORMING
  │
  ├── ตรวจพบ ST ด้วยปริมาณต่ำกว่า → State 4: PHASE_B (ความเชื่อมั่น 55%)
  ├── ทะลุต่ำกว่า SC ด้วยปริมาณสูง → State 0: WATCHING (ล้มเหลว)
  │
State 4: PHASE_B
  │
  ├── ST หลายครั้งด้วย vol ลดลง → State 5: SUPPLY_ABSORBED (ความเชื่อมั่น 65%)
  ├── ทะลุต่ำกว่า SC ด้วยปริมาณสูง → State 0: WATCHING (ล้มเหลว)
  ├── หมดเวลา (200+ แท่ง) → ทบทวนว่าเป็น Re-distribution
  │
State 5: SUPPLY_ABSORBED
  │
  ├── ตรวจพบ Spring → State 6: SPRING_DETECTED (ความเชื่อมั่น 80%)
  ├── ราคาทะลุเหนือ Creek → State 7: SOS_DETECTED (ความเชื่อมั่น 70%)
  │
State 6: SPRING_DETECTED
  │
  ├── Test of Spring (higher low, vol ต่ำ) → State 8: CONFIRMED (ความเชื่อมั่น 90%)
  ├── ราคาตกต่ำกว่าจุดต่ำ Spring → State 4: PHASE_B (ลดความเชื่อมั่น)
  │
State 7: SOS_DETECTED
  │
  ├── LPS pullback ที่ Creek → State 8: CONFIRMED (ความเชื่อมั่น 85%)
  ├── ราคาตกกลับเข้ากรอบ → State 4: PHASE_B (ลดความเชื่อมั่น)
  │
State 8: CONFIRMED ACCUMULATION
  │
  ├── BU สำเร็จ → State 9: MARKUP (ความเชื่อมั่น 95%)
  ├── ราคาตกกลับต่ำกว่า Creek ด้วยปริมาณ → State 4: PHASE_B (ประเมินใหม่)
  │
State 9: MARKUP_INITIATED
  └── เฟสสมบูรณ์ — เปลี่ยนไปติดตาม Markup

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 การคำนวณความเชื่อมั่นแบบเรียลไทม์

$$
C_{\text{accum}}(t) = \sum_{e \in E_{\text{detected}}} w_e \cdot q_e \cdot d_e(t)
$$

โดยที่:
- $E_{\text{detected}}$ = เซตของเหตุการณ์ Wyckoff ที่ตรวจพบ
- $w_e$ = น้ำหนักของเหตุการณ์ $e$ (ดูตารางด้านล่าง)
- $q_e$ = คะแนนคุณภาพของเหตุการณ์ $e$ [0, 1]
- $d_e(t)$ = ตัวคูณการลดลงตามเวลา: $d_e(t) = e^{-\mu(t - t_e)}$ โดยที่ $\mu$ = อัตราการลดลง

| เหตุการณ์ | น้ำหนัก ($w_e$) | หมายเหตุ |
|---|---|---|
| PS | 0.05 | ระยะเริ่มต้นมาก น้ำหนักต่ำ |
| SC | 0.15 | จำเป็นแต่ต้องการการยืนยัน |
| AR | 0.10 | ยืนยันขอบเขตกรอบ |
| ST (ครั้งที่ 1) | 0.10 | การยืนยันแรกของการดูดซับอุปทาน |
| ST (ครั้งต่อ ๆ มา) | 0.05 ต่อครั้ง | การยืนยันเพิ่มเติม |
| Spring | 0.25 | น้ำหนักสูงสุด — เหตุการณ์ที่สำคัญที่สุด |
| การทดสอบ Spring | 0.15 | ยืนยันความถูกต้องของ Spring |
| SOS | 0.10 | การยืนยัน Breakout |
| LPS | 0.05 | การยืนยันจุดเข้าสุดท้าย |
| **รวมที่เป็นไปได้** | **1.00** | |

---

## 7. แบบจำลองทางคณิตศาสตร์

### 7.1 พารามิเตอร์กรอบการสะสม

จากกรอบการสะสมที่ตรวจพบ:

$$
\text{Range} = [P_{\text{ice}}, P_{\text{creek}}]
$$

โดยที่:
- $P_{\text{ice}} = P_{\text{SC\_low}} \pm \epsilon$ (ระดับแนวรับ)
- $P_{\text{creek}} = P_{\text{AR\_high}} \pm \epsilon$ (ระดับแนวต้าน)
- $\epsilon$ = โซนเผื่อ (โดยปกติ 0.2 ATR)

**ความสูงของกรอบ:**
$$
H_{\text{range}} = P_{\text{creek}} - P_{\text{ice}}
$$

**ระยะเวลากรอบ (เป็นจำนวนแท่ง):**
$$
T_{\text{range}} = t_{\text{SOS}} - t_{\text{PS}}
$$

### 7.2 การประมาณเป้าหมายราคา

**วิธีที่ 1: Point-and-Figure Count (แบบทันสมัย)**

$$
\text{Target}_{\text{up}} = P_{\text{ice}} + \left(\frac{T_{\text{range}}}{T_{\text{bar}}} \times H_{\text{range}} \times \alpha\right)
$$

โดยที่:
- $T_{\text{bar}}$ = ระยะเวลาเฉลี่ยของแท่ง
- $\alpha$ = ตัวคูณปรับขนาด (โดยปกติ 0.5–1.5 ปรับตามสินทรัพย์)

**วิธีที่ 2: การประมาณตาม ATR**

$$
\text{Target}_{\text{up}} = P_{\text{creek}} + k \cdot ATR \cdot \sqrt{\frac{T_{\text{range}}}{20}}
$$

โดยที่ $k$ คือตัวคูณ:
- แบบอนุรักษ์นิยม: $k = 2.0$
- แบบปานกลาง: $k = 3.5$
- แบบเชิงรุก: $k = 5.0$

**วิธีที่ 3: Fibonacci Extension จากกรอบ**

$$
\text{Target}_{1.0} = P_{\text{creek}} + 1.0 \times H_{\text{range}}
$$
$$
\text{Target}_{1.618} = P_{\text{creek}} + 1.618 \times H_{\text{range}}
$$
$$
\text{Target}_{2.618} = P_{\text{creek}} + 2.618 \times H_{\text{range}}
$$

### 7.3 แบบจำลองความน่าจะเป็นของ Spring

ความน่าจะเป็นที่การทะลุต่ำกว่าแนวรับเป็น Spring (เทียบกับการทะลุจริง):

$$
P(\text{Spring} | \text{Break Below}) = \sigma\left(\beta_0 + \beta_1 x_V + \beta_2 x_D + \beta_3 x_T + \beta_4 x_S\right)
$$

โดยที่ $\sigma$ คือฟังก์ชัน Sigmoid และ:
- $x_V$ = ปริมาณที่ปรับขนาดแล้วที่จุดทะลุ (ปริมาณต่ำกว่าเข้าข่าย Spring มากกว่า)
- $x_D$ = ความลึกของการทะลุ (ตื้นกว่าเข้าข่าย Spring มากกว่า)
- $x_T$ = จำนวนการทดสอบแนวรับที่สำเร็จก่อนหน้า (ทดสอบมากกว่าเข้าข่าย Spring มากกว่า)
- $x_S$ = ความชันของปริมาณในการทดสอบต่อเนื่อง (ความชันลดลงเข้าข่าย Spring มากกว่า)

ค่าสัมประสิทธิ์ปกติ (ต้องปรับเทียบ):
- $\beta_0 = 0.5$, $\beta_1 = -0.8$ (ปริมาณต่ำ = น่าจะเป็น Spring มากกว่า)
- $\beta_2 = -1.2$ (ตื้นกว่า = น่าจะเป็น Spring มากกว่า)
- $\beta_3 = 0.4$ (ทดสอบก่อนหน้ามากกว่า = น่าจะเป็น Spring มากกว่า)
- $\beta_4 = -0.6$ (แนวโน้มปริมาณลดลง = น่าจะเป็น Spring มากกว่า)

### 7.4 ดัชนีความหมดลงของอุปทาน (Supply Exhaustion Index)

มาตรวัดสะสมของการดูดซับอุปทานระหว่างการสะสม:

$$
\text{SEI}(t) = \frac{\sum_{i=t_0}^{t} V_{\text{down}}(i) \cdot |\Delta P_{\text{down}}(i)|}{\sum_{i=t_0}^{t} V_{\text{up}}(i) \cdot |\Delta P_{\text{up}}(i)|}
$$

โดยที่:
- $V_{\text{down}}(i)$ = ปริมาณของแท่งลง, $V_{\text{up}}(i)$ = ปริมาณของแท่งขึ้น
- $\Delta P_{\text{down}}(i)$ = การเปลี่ยนแปลงราคาของแท่งลง, $\Delta P_{\text{up}}(i)$ = การเปลี่ยนแปลงราคาของแท่งขึ้น
- $t_0$ = จุดเริ่มต้นของกรอบการสะสม

**การตีความ:**
- SEI > 2.0 ตอนเริ่ม (อุปทานหนัก) → SEI ลดลงเข้าหา 1.0 → SEI < 0.5 ใกล้จบ (อุปทานหมดลง)
- การเปลี่ยนจาก SEI > 1.0 เป็น SEI < 1.0 เป็นจุดเปลี่ยนที่สำคัญ

---

## 8. การสะสมเทียบกับขาลงที่ยังดำเนินอยู่

### 8.1 ตัวแยกความแตกต่างหลัก

ทักษะที่สำคัญที่สุดอย่างหนึ่งคือการแยกแยะการสะสมจริงจากการหยุดพักในขาลงที่ยังดำเนินอยู่ (Re-distribution)

| ลักษณะ | การสะสม (Accumulation) | Re-Distribution (ขาลงต่อเนื่อง) |
|---|---|---|
| ปริมาณที่ SC | สุดขีด (Climactic) | ปานกลาง (ไม่มีการยอมจำนน) |
| แนวโน้มปริมาณในการทดสอบ | ลดลง | คงที่หรือเพิ่มขึ้น |
| พฤติกรรม Spring | กลับตัวเร็ว ยืนได้ | ล้มเหลว — ราคาร่วงต่อ |
| ระยะเวลากรอบ | สัดส่วนกับขาลงก่อนหน้า | มักสั้น อ่อนแอ |
| การปรับตัวขึ้นในกรอบ | แข็งแกร่ง ปริมาณเพิ่มขึ้น | อ่อนแอ ปริมาณต่ำ |
| ตำแหน่งปิดในการทดสอบ | เหนือจุดกลาง | ต่ำกว่าจุดกลาง |
| มี Higher Low เกิดขึ้น | ใช่ ต่อเนื่อง | ไม่ — การทดสอบแต่ละครั้งลึกเท่าหรือลึกกว่า |
| คุณภาพ SOS | Breakout แข็งแกร่ง ปริมาณสูง | Breakout อ่อน ปริมาณต่ำ (ล้มเหลว) |

### 8.2 อัลกอริทึมตรวจจับความล้มเหลว

```python
def detect_accumulation_failure(state, candle, avg_volume, atr):
    """
    Detect if the accumulation pattern is failing (actually re-distribution).
    
    Returns:
        dict with failure signal and new state, or None if no failure
    """
    failures = []
    
    # Failure 1: Price breaks below Spring low on high volume
    if state.spring_event and candle['low'] < state.spring_event['price_low']:
        if candle['volume'] > avg_volume * 1.5:
            failures.append({
                'type': 'SPRING_FAILURE',
                'severity': 'CRITICAL',
                'description': 'Price broke below Spring low on high volume',
                'action': 'EXIT_ALL_LONGS'
            })
    
    # Failure 2: SOS fails — price falls back below Creek on high volume
    if state.sos_event and candle['close'] < state.creek_level:
        if candle['volume'] > avg_volume * 1.2:
            failures.append({
                'type': 'SOS_FAILURE',
                'severity': 'HIGH',
                'description': 'SOS failed — price back below Creek with volume',
                'action': 'EXIT_OR_REDUCE'
            })
    
    # Failure 3: Volume increasing on successive tests (supply not being absorbed)
    if len(state.test_volumes) >= 3:
        vol_slope = np.polyfit(range(len(state.test_volumes)), state.test_volumes, 1)[0]
        if vol_slope > 0:
            failures.append({
                'type': 'INCREASING_SUPPLY',
                'severity': 'MEDIUM',
                'description': 'Volume increasing on tests — supply not being absorbed',
                'action': 'REDUCE_CONFIDENCE'
            })
    
    # Failure 4: Bearish closes on tests (closing at lows)
    if state.recent_tests:
        bearish_closes = sum(1 for t in state.recent_tests[-3:] if t['close_position'] < 0.3)
        if bearish_closes >= 2:
            failures.append({
                'type': 'BEARISH_TESTS',
                'severity': 'MEDIUM',
                'description': 'Tests showing bearish close positions',
                'action': 'REDUCE_CONFIDENCE'
            })
    
    # Failure 5: Time exceeded without progression
    if state.bars_in_phase > state.max_phase_duration:
        failures.append({
            'type': 'TIME_EXHAUSTION',
            'severity': 'LOW',
            'description': f'Phase duration exceeded {state.max_phase_duration} bars',
            'action': 'REASSESS'
        })
    
    return failures if failures else None
```

### 8.3 การให้คะแนน: การสะสมเทียบกับ Re-Distribution

$$
P(\text{Accum}) = \frac{1}{1 + e^{-z}}
$$

โดยที่:

$$
z = w_1 \cdot [\text{Vol declining on tests}] + w_2 \cdot [\text{Spring success}] + w_3 \cdot [\text{Higher lows}] + w_4 \cdot [\text{SOS strength}] - w_5 \cdot [\text{Failure signals}]
$$

น้ำหนักเริ่มต้น: $w_1 = 2.0, w_2 = 3.0, w_3 = 1.5, w_4 = 2.5, w_5 = 4.0$

---

## 9. ตรรกะเข้า/ออกคำสั่ง

### 9.1 จุดเข้า (จัดอันดับตามคุณภาพ)

#### จุดเข้า 1: การทดสอบ Spring (คุณภาพสูงสุด)

```python
def entry_test_of_spring(spring_event, test_event, atr, range_height):
    """
    Highest quality entry — after Spring is confirmed by Test.
    """
    entry_price = test_event['price_close']
    stop_loss = spring_event['price_low'] - atr * 0.3
    risk = entry_price - stop_loss
    
    # Targets based on range projection
    target_1 = entry_price + range_height * 1.0   # Conservative
    target_2 = entry_price + range_height * 1.618  # Moderate
    target_3 = entry_price + range_height * 2.618  # Aggressive
    
    return {
        'entry_type': 'TEST_OF_SPRING',
        'direction': 'LONG',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'risk': risk,
        'targets': [target_1, target_2, target_3],
        'risk_reward': [(t - entry_price) / risk for t in [target_1, target_2, target_3]],
        'position_size_pct': 2.0,  # Full risk allocation
        'confidence': 0.90,
        'max_risk_pct': 2.0,
    }
```

#### จุดเข้า 2: Spring (เข้าโดยตรง)

```python
def entry_spring_direct(spring_event, atr, range_height):
    """
    Aggressive entry directly on Spring bar.
    Best for Type 3 springs with quick reversal.
    """
    entry_price = spring_event['price_close']
    stop_loss = spring_event['price_low'] - atr * 0.5
    risk = entry_price - stop_loss
    
    return {
        'entry_type': 'SPRING_DIRECT',
        'direction': 'LONG',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'risk': risk,
        'targets': [
            entry_price + range_height * 0.8,
            entry_price + range_height * 1.5,
            entry_price + range_height * 2.5,
        ],
        'position_size_pct': 1.5,  # Reduced due to no test confirmation
        'confidence': 0.75,
        'max_risk_pct': 1.5,
        'note': 'Consider adding on successful Test'
    }
```

#### จุดเข้า 3: จุดพักรับสุดท้าย (LPS)

```python
def entry_lps(lps_event, creek_level, atr, range_height):
    """
    Entry on pullback after SOS breakout.
    Good for traders who missed the Spring.
    """
    entry_price = lps_event['price_close']
    stop_loss = creek_level - atr * 0.5
    risk = entry_price - stop_loss
    
    return {
        'entry_type': 'LPS',
        'direction': 'LONG',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'risk': risk,
        'targets': [
            entry_price + range_height * 1.0,
            entry_price + range_height * 2.0,
            entry_price + range_height * 3.0,
        ],
        'position_size_pct': 1.5,
        'confidence': 0.80,
        'max_risk_pct': 1.5,
    }
```

#### จุดเข้า 4: การย้อนกลับ (Back-Up)

```python
def entry_backup(bu_price, creek_level, atr, range_height):
    """
    Entry on final pullback to Creek from above.
    Latest entry with lowest risk but reduced R:R.
    """
    entry_price = bu_price
    stop_loss = creek_level - atr * 0.3
    risk = entry_price - stop_loss
    
    return {
        'entry_type': 'BACKUP',
        'direction': 'LONG',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'risk': risk,
        'targets': [
            entry_price + range_height * 0.8,
            entry_price + range_height * 1.618,
        ],
        'position_size_pct': 1.0,
        'confidence': 0.85,
        'max_risk_pct': 1.0,
    }
```

### 9.2 กลยุทธ์การเพิ่มขนาดสถานะ

```
กลยุทธ์การเพิ่มขนาดจุดเข้าระหว่างการสะสม:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

สถานะที่วางแผนทั้งหมด: 100%

จุดเข้า 1: Spring (โดยตรง)           → 30% ของสถานะทั้งหมด
จุดเข้า 2: การทดสอบ Spring           → 30% ของสถานะทั้งหมด (เพิ่มเติม)
จุดเข้า 3: LPS หรือ BU               → 20% ของสถานะทั้งหมด (เพิ่มเติม)
จุดเข้า 4: Pullback ระหว่าง Markup    → 20% ของสถานะทั้งหมด (เพิ่มเติม)

ราคาเข้าเฉลี่ย: ค่าเฉลี่ยถ่วงน้ำหนักของทุกจุดเข้า
จุดตัดขาดทุนรวม: ต่ำกว่าจุดต่ำ Spring (หรือต่ำกว่า Creek สำหรับจุดเข้าหลัง ๆ)
R:R รวม: ควร >= 3:1 สำหรับสถานะทั้งหมด

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 9.3 ตรรกะการออก

```python
def accumulation_exit_logic(position, candle, market_state, atr):
    """
    Exit logic for positions entered during accumulation.
    """
    exit_signals = []
    
    # Hard stop loss
    if candle['low'] <= position['stop_loss']:
        exit_signals.append({
            'type': 'STOP_LOSS',
            'action': 'EXIT_ALL',
            'price': position['stop_loss'],
            'reason': 'Stop loss triggered'
        })
    
    # Target 1 — partial exit
    if candle['high'] >= position['targets'][0] and not position.get('t1_hit'):
        exit_signals.append({
            'type': 'TARGET_1',
            'action': 'EXIT_50PCT',
            'price': position['targets'][0],
            'reason': 'First target reached — take partial profits',
            'move_stop': 'BREAKEVEN'
        })
    
    # Target 2 — additional exit
    if candle['high'] >= position['targets'][1] and not position.get('t2_hit'):
        exit_signals.append({
            'type': 'TARGET_2',
            'action': 'EXIT_30PCT',
            'price': position['targets'][1],
            'reason': 'Second target reached',
            'move_stop': position['targets'][0]  # Trail to T1
        })
    
    # Target 3 — final exit
    if len(position['targets']) > 2 and candle['high'] >= position['targets'][2]:
        exit_signals.append({
            'type': 'TARGET_3',
            'action': 'EXIT_REMAINING',
            'price': position['targets'][2],
            'reason': 'Final target reached'
        })
    
    # Phase change — distribution detected
    if market_state.phase == 'DISTRIBUTION':
        exit_signals.append({
            'type': 'PHASE_CHANGE',
            'action': 'EXIT_ALL',
            'price': candle['close'],
            'reason': 'Distribution phase detected — exit longs'
        })
    
    # Trailing stop during markup
    if market_state.phase == 'MARKUP' and position.get('t1_hit'):
        trail_stop = candle['high'] - atr * 2.5
        if trail_stop > position['stop_loss']:
            exit_signals.append({
                'type': 'TRAIL_STOP_UPDATE',
                'action': 'UPDATE_STOP',
                'new_stop': trail_stop,
                'reason': 'Trailing stop tightened during markup'
            })
    
    return exit_signals
```

---

## 10. พารามิเตอร์ความเสี่ยง

### 10.1 พารามิเตอร์ความเสี่ยงตามประเภทจุดเข้า

| ประเภทจุดเข้า | ความเสี่ยงสูงสุด (% บัญชี) | SL ปกติ (ATR) | R:R ขั้นต่ำ | สถานะสูงสุด | เกณฑ์ความเชื่อมั่น |
|---|---|---|---|---|---|
| Spring (Type 3) | 2.0% | 0.5–1.0 | 4:1 | 30% ของแผน | 0.80 |
| Spring (Type 2) | 1.5% | 1.0–1.5 | 3:1 | 25% ของแผน | 0.70 |
| Spring (Type 1) | 0.5% | 1.5–2.5 | 5:1 | 10% ของแผน | 0.60 |
| การทดสอบ Spring | 2.0% | 0.5–1.0 | 3:1 | 30% ของแผน | 0.85 |
| SOS Breakout | 1.5% | 1.5–2.0 | 2:1 | 20% ของแผน | 0.70 |
| LPS | 1.5% | 0.5–1.0 | 3:1 | 20% ของแผน | 0.75 |
| BU | 1.0% | 0.3–0.8 | 2:1 | 15% ของแผน | 0.80 |

### 10.2 การปรับความเสี่ยงแบบไดนามิก

$$
R_{\text{adjusted}} = R_{\text{base}} \times \min\left(1.0, \frac{C_{\text{accum}}}{C_{\text{threshold}}}\right) \times F_{\text{volatility}} \times F_{\text{correlation}}
$$

โดยที่:
- $R_{\text{base}}$ = เปอร์เซ็นต์ความเสี่ยงพื้นฐานจากตารางด้านบน
- $C_{\text{accum}}$ = คะแนนความเชื่อมั่นของการสะสม
- $C_{\text{threshold}}$ = เกณฑ์ความเชื่อมั่นขั้นต่ำ (0.65)
- $F_{\text{volatility}}$ = ตัวคูณปรับความผันผวน: $F_V = \frac{ATR_{\text{historical}}}{ATR_{\text{current}}}$ (ลดความเสี่ยงในช่วงผันผวนสูง)
- $F_{\text{correlation}}$ = ตัวคูณปรับสหสัมพันธ์ (ลดลงหากมีสถานะที่สัมพันธ์กัน)

### 10.3 ขีดจำกัด Drawdown สูงสุด

| ช่วงเวลา | Drawdown สูงสุด | การดำเนินการ |
|---|---|---|
| ต่อเทรด | ตาม SL | ออกอัตโนมัติ |
| ต่อวัน | 3% ของบัญชี | หยุดเทรดวันนั้น |
| ต่อสัปดาห์ | 5% ของบัญชี | ลดขนาดสถานะ 50% |
| ต่อเดือน | 8% ของบัญชี | หยุดเทรด ทบทวนระบบ |
| รวม | 15% ของบัญชี | ปิดระบบทั้งหมด ทบทวนด้วยตนเอง |

---

## 11. ขั้นตอนการดำเนินการ

### 11.1 อัลกอริทึมตรวจจับการสะสมแบบครบถ้วน

```python
class AccumulationDetector:
    """
    Complete state machine for detecting Wyckoff accumulation in real-time.
    """
    
    def __init__(self, config):
        self.config = config
        self.state = 'WATCHING'
        self.confidence = 0.0
        self.events = []
        self.range_support = None
        self.range_resistance = None
        self.phase_start_bar = None
        
    def update(self, candle, index, avg_volume, atr, trend):
        """
        Process a new candle and update accumulation detection state.
        
        Returns:
            dict: Current state, confidence, events, and any trade signals
        """
        result = {
            'state': self.state,
            'confidence': self.confidence,
            'new_events': [],
            'signals': [],
            'phase': None
        }
        
        if self.state == 'WATCHING':
            ps = detect_preliminary_support(
                self.candles, index, avg_volume, atr, trend
            )
            if ps:
                self.events.append(ps)
                self.state = 'PS_DETECTED'
                self.confidence = 0.10
                self.phase_start_bar = index
                result['new_events'].append(ps)
        
        elif self.state == 'PS_DETECTED':
            sc = detect_selling_climax(
                self.candles, index, avg_volume, avg_volume,
                atr, self._get_event('PS')
            )
            if sc:
                self.events.append(sc)
                self.state = 'SC_DETECTED'
                self.confidence = 0.25
                self.range_support = sc['range_bottom']
                result['new_events'].append(sc)
            elif index - self.phase_start_bar > 30:
                self._reset()
        
        elif self.state == 'SC_DETECTED':
            ar = detect_automatic_rally(
                self.candles, index, self._get_event('SC'),
                avg_volume, atr
            )
            if ar:
                self.events.append(ar)
                self.state = 'RANGE_FORMING'
                self.confidence = 0.40
                self.range_resistance = ar['range_top']
                result['new_events'].append(ar)
            elif candle['low'] < self.range_support - atr * 2:
                self._reset()  # New low far below SC — not accumulation
        
        elif self.state == 'RANGE_FORMING':
            st = detect_secondary_test(
                self.candles, index, self._get_event('SC'),
                self._get_event('AR'), avg_volume, atr
            )
            if st:
                self.events.append(st)
                self.state = 'PHASE_B'
                self.confidence = 0.55
                result['new_events'].append(st)
        
        elif self.state == 'PHASE_B':
            # Check for additional STs
            st = detect_secondary_test(
                self.candles, index, self._get_event('SC'),
                self._get_event('AR'), avg_volume, atr
            )
            if st:
                self.events.append(st)
                result['new_events'].append(st)
                if st['interpretation'] == 'STRONG':
                    self.confidence = min(0.70, self.confidence + 0.05)
            
            # Check for Spring
            spring = detect_spring(
                self.candles, index, self.range_support,
                self.range_resistance, avg_volume, atr,
                [e for e in self.events if e['event'] == 'ST']
            )
            if spring:
                self.events.append(spring)
                self.state = 'SPRING_DETECTED'
                self.confidence = 0.80
                result['new_events'].append(spring)
                
                if spring['spring_type'] == 3:
                    result['signals'].append({
                        'action': 'BUY',
                        'type': 'SPRING_TYPE3',
                        'entry': candle['close'],
                        'stop_loss': spring['stop_loss'],
                        'confidence': spring['confidence']
                    })
            
            # Check for SOS without Spring
            sos = detect_sign_of_strength(
                self.candles, index, self.range_resistance,
                avg_volume, atr,
                self.range_resistance - self.range_support
            )
            if sos:
                self.events.append(sos)
                self.state = 'SOS_DETECTED'
                self.confidence = 0.70
                result['new_events'].append(sos)
        
        elif self.state == 'SPRING_DETECTED':
            test = detect_test_of_spring(
                self.candles, index, self._get_event('SPRING'),
                avg_volume, atr
            )
            if test:
                self.events.append(test)
                self.state = 'CONFIRMED'
                self.confidence = 0.90
                result['new_events'].append(test)
                result['signals'].append({
                    'action': 'BUY',
                    'type': 'TEST_OF_SPRING',
                    'entry': candle['close'],
                    'stop_loss': test['stop_loss'],
                    'confidence': test['confidence']
                })
            
            spring_low = self._get_event('SPRING')['price_low']
            if candle['close'] < spring_low and candle['volume'] > avg_volume * 1.5:
                self.state = 'PHASE_B'
                self.confidence = max(0.30, self.confidence - 0.30)
        
        elif self.state == 'SOS_DETECTED':
            lps = detect_last_point_of_support(
                self.candles, index, self._get_event('SOS'),
                self.range_resistance, avg_volume, atr
            )
            if lps:
                self.events.append(lps)
                self.state = 'CONFIRMED'
                self.confidence = 0.85
                result['new_events'].append(lps)
                result['signals'].append({
                    'action': 'BUY',
                    'type': 'LPS',
                    'entry': candle['close'],
                    'stop_loss': lps['stop_loss'],
                    'confidence': lps['confidence']
                })
        
        elif self.state == 'CONFIRMED':
            self.confidence = 0.90
            result['phase'] = 'ACCUMULATION_CONFIRMED'
        
        result['state'] = self.state
        result['confidence'] = self.confidence
        return result
    
    def _get_event(self, event_type):
        """Get the most recent event of a given type."""
        for e in reversed(self.events):
            if e['event'] == event_type:
                return e
        return None
    
    def _reset(self):
        """Reset to watching state."""
        self.state = 'WATCHING'
        self.confidence = 0.0
        self.events = []
        self.range_support = None
        self.range_resistance = None
        self.phase_start_bar = None
```

---

## 12. การสะสมเฉพาะตลาด Forex

### 12.1 รูปแบบการสะสมตามเซสชัน

ในตลาด Forex การสะสมมักสัมพันธ์กับการเปลี่ยนเซสชัน:

| รูปแบบ | คำอธิบาย | ความถี่ | คู่สกุลเงินที่ดีที่สุด |
|---|---|---|---|
| **Asian Range Accumulation** | ราคารวมตัวในกรอบแคบระหว่างเซสชัน Asian, Spring ต่ำกว่า Asian Low ที่ London Open | พบบ่อยมาก | EUR/USD, GBP/USD |
| **London Accumulation** | ช่วงต้น London สร้างกรอบ, Spring ที่ช่วง London–NY ซ้อนทับ | พบบ่อย | EUR/USD, EUR/GBP |
| **Weekly Accumulation** | กรอบวันจันทร์–อังคาร, Spring กลางสัปดาห์, SOS วันพฤหัส–ศุกร์ | ปานกลาง | สกุลหลักทุกคู่ |
| **News-Driven Accumulation** | กรอบก่อตัวก่อนข่าวสำคัญ, SC/Spring เมื่อข่าวออก | ปานกลาง | คู่ที่ได้รับผลกระทบ |

### 12.2 การปรับ Tick Volume สำหรับ Forex

เนื่องจาก Forex ใช้ Tick Volume จำเป็นต้องมีการปรับ:

$$
V_{\text{adjusted}}(t) = V_{\text{tick}}(t) \times \frac{\text{Session\_Weight}(t)}{\text{Max\_Session\_Weight}}
$$

น้ำหนักเซสชัน:
- Asian: 0.5
- London: 1.0
- London/NY overlap: 1.0
- NY afternoon: 0.7
- Late NY: 0.3

---

## 13. การสะสมเฉพาะตลาดคริปโต

### 13.1 การยืนยันการสะสมด้วยข้อมูล On-Chain

| เมตริก On-Chain | สัญญาณการสะสม | การเพิ่มความเชื่อมั่น |
|---|---|---|
| เงินไหลออกจากตลาดแลกเปลี่ยน > เงินไหลเข้า | เหรียญย้ายไปกระเป๋าเย็น (ถือระยะยาว) | +10% |
| ที่อยู่วาฬเพิ่มยอดคงเหลือ | ผู้ถือรายใหญ่กำลังสะสม | +15% |
| Miner Reserve เพิ่มขึ้น | นักขุดถือ ไม่ขาย | +5% |
| Stablecoin Reserve บนตลาดแลกเปลี่ยนเพิ่มขึ้น | กำลังซื้อสะสม | +10% |
| Funding Rate ติดลบมาก | ความเชื่อมั่นขาลง (สวนทาง = ขาขึ้น) | +5% |
| Open Interest ลดลง | Leverage ถูกชะล้างออก | +5% |

### 13.2 การกรองปริมาณคริปโต

```python
def filter_wash_trading(exchange_volumes, known_wash_pct):
    """
    Filter suspected wash trading volume from crypto exchanges.
    
    Parameters:
        exchange_volumes: dict of {exchange_name: volume}
        known_wash_pct: dict of {exchange_name: estimated_wash_pct}
    
    Returns:
        float: estimated real volume
    """
    real_volume = 0
    for exchange, volume in exchange_volumes.items():
        wash_pct = known_wash_pct.get(exchange, 0.0)
        real_volume += volume * (1 - wash_pct)
    
    return real_volume
```

### 13.3 กรอบเวลาการสะสมคริปโต

| กรอบเวลา | การใช้งาน | หมายเหตุ |
|---|---|---|
| 1W | การสะสมระดับมหภาค (หลายเดือน) | ดีที่สุดสำหรับการลงทุน Spot |
| 1D | การสะสมระดับกลาง (หลายสัปดาห์) | Swing Trading |
| 4H | การสะสมระยะสั้น (หลายวัน) | Active Trading |
| 1H | การสะสมภายในวัน | Scalp/Day Trading |
| 15M | การสะสมระดับจุลภาค | Scalping พร้อม Leverage |

---

## 14. ข้อผิดพลาดและกับดักที่พบบ่อย

### 14.1 ข้อผิดพลาดที่ควรหลีกเลี่ยง

| # | ข้อผิดพลาด | ผลที่ตามมา | วิธีแก้ |
|---|---|---|---|
| 1 | เข้าที่ SC โดยตรง | SC ไม่ใช่จุดเข้า — มันกำหนดกรอบ | รอ Spring หรือ SOS |
| 2 | ละเลยปริมาณ | การระบุเฟสโดยไม่มีปริมาณไม่น่าเชื่อถือ | ปริมาณเป็นสิ่งจำเป็น |
| 3 | บังคับรูปแบบ | ไม่ใช่ทุกกรอบจะเป็นการสะสม | ต้องการเหตุการณ์หลักทั้งหมด |
| 4 | ผิดกรอบเวลา | การสะสมบน 5M อาจเป็นสัญญาณรบกวนบน 4H | ยืนยันด้วย HTF เสมอ |
| 5 | ละเลย Spring ที่ล้มเหลว | Type 1 Spring ที่ไม่กลับตัวอาจนำไปสู่การทะลุลง | ใช้ Stop Loss |
| 6 | ระบุ SOS ก่อนเวลา | ไม่ใช่ทุกการปรับตัวเหนือแนวต้านจะเป็น SOS | ต้องมีการยืนยันปริมาณ + Spread |
| 7 | ใช้ Leverage เกินที่จุดเข้า Spring | จุดเข้า Spring ยังสามารถล้มเหลวได้ | ความเสี่ยงสูงสุด 2% ต่อเทรด |
| 8 | ละเลยบริบทที่กว้างกว่า | การสะสมในขาลงระดับมหภาคมีอัตราความสำเร็จต่ำกว่า | ตรวจสอบแนวโน้ม HTF |

### 14.2 รายการตรวจสอบคุณภาพรูปแบบ

ก่อนเทรดรูปแบบการสะสม ให้ตรวจสอบ:

```
รายการตรวจสอบคุณภาพการสะสม:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ ] มีขาลงก่อนหน้า (อย่างน้อย 2 เท่าของความสูงกรอบ)
[ ] Selling Climax มีปริมาณสุดขีด (>= 2.5 เท่าของค่าเฉลี่ย)
[ ] Automatic Rally กำหนดแนวต้านที่ชัดเจน
[ ] Secondary Test แสดงปริมาณลดลง
[ ] กรอบอยู่ในตำแหน่งอย่างน้อย 20 แท่ง
[ ] ปริมาณในการทดสอบแนวรับลดลงเรื่อย ๆ
[ ] ตรวจพบเหตุการณ์ Spring หรือ SOS
[ ] หากเป็น Spring: Test เกิดขึ้นด้วยปริมาณต่ำกว่าและ Higher Low
[ ] หากเป็น SOS: ปริมาณขยายตัวอย่างมากใน Breakout
[ ] แนวโน้มกรอบเวลาสูงกว่าไม่เป็นขาลงอย่างแข็งแกร่ง
[ ] ไม่มีสัญญาณขัดแย้งจากวิธีวิเคราะห์อื่น

คะแนน: จำนวนรายการที่ผ่าน / รายการทั้งหมด
คะแนนขั้นต่ำที่จะเทรด: 7/11 (64%)
ความเชื่อมั่นสูง: 9+/11 (82%+)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 15. เอกสารอ้างอิง

### 15.1 แหล่งข้อมูลหลัก

1. Wyckoff, R.D. (1931). *The Richard D. Wyckoff Method of Trading and Investing in Stocks*. Wyckoff Associates.
2. Evans, R. (1969). *Wyckoff Course Notes — Accumulation and Distribution Schematics*. Stock Market Institute.
3. Pruden, H.O. (2007). *The Three Skills of Top Trading*. Wiley. — Chapter 4: "The Wyckoff Method of Market Analysis."

### 15.2 การปรับใช้สมัยใหม่

4. Williams, T. (2005). *Master the Markets*. TradeGuider Systems. — การยืนยันเหตุการณ์สะสมด้วย VSA
5. Weis, D.H. (2013). *Trades About to Happen*. Wiley. — แนวทาง Wave-Volume สมัยใหม่ในการสะสม
6. Schroeder, G. (2015). "Wyckoff Accumulation Schematics #1 and #2." *StockCharts.com Wyckoff Power Charting Series*.

### 15.3 บทความวิจัย

7. Lo, A.W. & Wang, J. (2000). "Trading Volume: Definitions, Data Analysis, and Implications of Portfolio Theory." *Review of Financial Studies*, 13(2), 257–300.
8. Blume, L., Easley, D., & O'Hara, M. (1994). "Market Statistics and Technical Analysis: The Role of Volume." *Journal of Finance*, 49(1), 153–181.

---

> **เอกสารถัดไป**: `02_distribution_schematic.md` — การวิเคราะห์เฟสการกระจาย (Distribution) อย่างละเอียด
