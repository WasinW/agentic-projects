# แผนผังการกระจาย Wyckoff (Wyckoff Distribution Schematic) — การวิเคราะห์แบบครบถ้วน

> **โมดูล**: แกนที่ 1 — กลยุทธ์การเทรด
> **หัวข้อ**: 02 — วิธี Wyckoff และโครงสร้างตลาด
> **ไฟล์**: 02_distribution_schematic.md
> **เวอร์ชัน**: 1.0
> **อัปเดตล่าสุด**: 2026-04-12
> **ผู้เขียน**: ทีมฐานความรู้ — ระบบเทรด AI หลายเอเจนต์ NTT

---

## สารบัญ

1. [บทนำสู่การกระจาย (Distribution)](#1-บทนำสู่การกระจาย-distribution)
2. [แผนผังการกระจาย #1 — มาตรฐาน](#2-แผนผังการกระจาย-1--มาตรฐาน)
3. [แผนผังการกระจาย #2 — แบบมี UTAD](#3-แผนผังการกระจาย-2--แบบมี-utad)
4. [การวิเคราะห์เฟสอย่างละเอียด](#4-การวิเคราะห์เฟสอย่างละเอียด)
5. [รูปแบบปริมาณระหว่างการกระจาย](#5-รูปแบบปริมาณระหว่างการกระจาย)
6. [การกระจายเทียบกับการสะสมซ้ำ (Re-Accumulation)](#6-การกระจายเทียบกับการสะสมซ้ำ-re-accumulation)
7. [แบบจำลองทางคณิตศาสตร์](#7-แบบจำลองทางคณิตศาสตร์)
8. [ตรรกะเข้า/ออกสำหรับเทรด Short](#8-ตรรกะเข้าออกสำหรับเทรด-short)
9. [การจัดการความเสี่ยงระหว่างการกระจาย](#9-การจัดการความเสี่ยงระหว่างการกระจาย)
10. [ขั้นตอนการดำเนินการ](#10-ขั้นตอนการดำเนินการ)
11. [การกระจายเฉพาะตลาด Forex](#11-การกระจายเฉพาะตลาด-forex)
12. [การกระจายเฉพาะตลาดคริปโต](#12-การกระจายเฉพาะตลาดคริปโต)
13. [ข้อผิดพลาดที่พบบ่อย](#13-ข้อผิดพลาดที่พบบ่อย)
14. [เอกสารอ้างอิง](#14-เอกสารอ้างอิง)

---

## 1. บทนำสู่การกระจาย (Distribution)

### 1.1 คำจำกัดความ

การกระจาย (Distribution) คือเฟสที่สามของวัฏจักรตลาดตามแนวคิด Wyckoff เป็นช่วงที่ราคา **เคลื่อนตัวในกรอบ Sideways** ที่ก่อตัวขึ้นที่จุดสูงสุดของขาขึ้น ในระหว่างนี้ Composite Man (CM) จะทยอยกระจาย (ขาย) สถานะที่สะสมไว้ก่อนหน้าให้กับผู้ซื้อที่ไม่มีข้อมูล (เทรดเดอร์รายย่อยที่ถูกดึงดูดโดยความเชื่อมั่นขาขึ้น) ในราคาพรีเมียม

### 1.2 ความสัมพันธ์แบบกระจกกับการสะสม

การกระจายเป็นภาพสะท้อนกลับของการสะสม แต่มีความแตกต่างแบบอสมมาตรที่สำคัญ:

| ด้าน | การสะสม (Accumulation) | การกระจาย (Distribution) |
|---|---|---|
| ตำแหน่ง | ด้านล่างของขาลง | ด้านบนของขาขึ้น |
| การดำเนินการของ CM | ซื้อ (ดูดซับอุปทาน) | ขาย (กระจายอุปทาน) |
| ความเชื่อมั่นรายย่อย | กลัว ยอมจำนน | ตื่นเต้น FOMO โลภ |
| โปรไฟล์ปริมาณ | SC = ปริมาณขายสุดขีด | BC = ปริมาณซื้อสุดขีด |
| การสลัดหลัก | Spring (Breakdown เท็จ) | UTAD (Breakout เท็จ) |
| การยืนยัน | SOS (การปรับตัวแข็งแกร่ง) | SOW (การร่วงลงอ่อนแอ) |
| ระยะเวลาปกติ | มักยาวกว่า | มักสั้นกว่า (ความโลภใจร้อน) |
| ความเร็วในการจบ | Markup ค่อย ๆ เกิด | Markdown มักรุนแรงฉับพลัน |

### 1.3 ทำไมการกระจายจึงเร็วและรุนแรงกว่า

จิตวิทยาตลาดสร้างความไม่สมมาตร:
- **การสะสม** ช้าเพราะความกลัวคงอยู่นาน; ผู้ขายต้องค่อย ๆ หมดแรง
- **การกระจาย** อาจเร็วกว่าเพราะความโลภดึงดูดผู้ซื้อที่กระตือรือร้นอย่างรวดเร็ว; เมื่อการกระจายเสร็จสมบูรณ์ การไม่มีอุปสงค์ทำให้ราคาร่วงลงอย่างรวดเร็ว

$$
\frac{T_{\text{distribution}}}{T_{\text{accumulation}}} \approx 0.6 \text{ to } 0.8
$$

และ Markdown ที่เกิดขึ้นมักชันกว่า Markup:

$$
\frac{|\text{Rate}_{\text{markdown}}|}{|\text{Rate}_{\text{markup}}|} \approx 1.5 \text{ to } 3.0
$$

### 1.4 พฤติกรรมของ Composite Man ระหว่างการกระจาย

```
Composite Man Distribution Playbook:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ขั้นตอน 1: สร้างความตื่นเต้นสุดขีด (CREATE EUPHORIA)
  ├── ปล่อยให้ราคาทำจุดสูงใหม่ (Buying Climax)
  ├── สื่อเปลี่ยนเป็นขาขึ้นสุดขีด
  ├── FOMO ดึงดูดผู้ซื้อรายใหม่
  └── CM เริ่มขายเข้าสู่ความแข็งแกร่ง

ขั้นตอน 2: ดูดซับอุปสงค์ (ABSORB DEMAND)
  ├── ราคาเคลื่อนตัวในกรอบแม้ข่าวดี
  ├── การปรับตัวขึ้นแต่ละครั้งพบ CM ขาย
  ├── ปริมาณในการปรับตัวขึ้นแสดงการกระจาย (vol สูง ปิดไม่ดี)
  └── อุปสงค์ถูกดูดซับโดยอุปทานของ CM

ขั้นตอน 3: ดักผู้ซื้อ (TRAP BUYERS — UTAD)
  ├── Breakout เท็จเหนือแนวต้านกรอบ
  ├── Trigger ผู้ซื้อ Breakout (อุปสงค์ใหม่ให้ CM ขายเข้า)
  ├── สื่อรายงาน "จุดสูงสุดใหม่" / "breakout"
  └── CM ขายสินค้าคงเหลือสุดท้ายให้ผู้ซื้อ Breakout

ขั้นตอน 4: ยืนยันความอ่อนแอ (CONFIRM WEAKNESS)
  ├── ราคาร่วงต่ำกว่าแนวรับกรอบ (SOW)
  ├── การปรับตัวขึ้นครั้งสุดท้ายล้มเหลวที่ระดับต่ำกว่า (LPSY)
  ├── ปริมาณยืนยันอุปทาน > อุปสงค์
  └── Markdown เริ่มต้น

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 2. แผนผังการกระจาย #1 — มาตรฐาน

### 2.1 แผนผัง ASCII

```
             Distribution Schematic #1 (Standard — No UTAD)
                    
Price
  │                                                    
  │    ──────────────────────────────────────────── Ice (Resistance)
  │         PSY   BC         ST        ST   LPSY
  │          │   ╱  ╲       ╱╲        ╱╲    ╱╲
  │          ↑  ╱    ╲     ╱  ╲      ╱  ╲  ╱  ╲
  │         ╱  ╱      ╲   ╱    ╲    ╱    ╲╱    ╲
  │        ╱  ╱        ╲ ╱      ╲  ╱              ╲
  │       ╱  ╱    AR    ╲╱       ╲╱       SOW      ╲
  │      ╱  ╱    ╱ ╲         ╱                      ╲
  │     ╱  ╱────╱───╲───────╱─────────────────────── Creek (Support)
  │    ╱       ╱     ╲     ╱
  │   ╱  Markup       ╲   ╱
  │  ╱                  ╲ ╱
  │ ╱                    ╲  ← SOW breaks below Creek
  │╱                      ╲
  │                        ╲
  │                         ╲  Markdown begins
  │                          ╲
  │                           ╲
  │
  │  Prior   │Phase A│    Phase B              │Phase C│ Phase D │Phase E
  │  Markup  │(Stop) │    (Building Cause)     │(Test) │(Trend)  │(Markdown)
  │          │       │                         │       │         │
  └──────────┴───────┴─────────────────────────┴───────┴─────────┴──→ Time
  
  Volume:
  ███   ████   ███    ██    █    ██   █    ███   ████   ██    ███
  HIGH  V.HIGH HIGH   MED  LOW  MED  LOW  HIGH  V.HIGH LOW   HIGH
  (PSY) (BC)   (AR)  (STs)           (STs)(SOW) (SOW) (LPSY) (Break)
```

### 2.2 สรุปเหตุการณ์สำคัญ

| เหตุการณ์ | ตัวย่อ | เฟส | คำอธิบาย |
|---|---|---|---|
| อุปทานเบื้องต้น (Preliminary Supply) | PSY | A | แรงขายสำคัญแรกหลังขาขึ้น |
| จุดซื้อสุดขีด (Buying Climax) | BC | A | การซื้อสุดขีดด้วยปริมาณสูงมาก กลับตัว |
| ปฏิกิริยาอัตโนมัติ (Automatic Reaction) | AR | A | การร่วงลงอย่างรุนแรงจาก BC กำหนดแนวรับ (Creek) |
| การทดสอบรอง (Secondary Test) | ST | B | การทดสอบซ้ำพื้นที่ BC ด้วยปริมาณต่ำกว่า |
| Upthrust หลังการกระจาย (Upthrust After Distribution) | UTAD | C | Breakout เท็จเหนือ BC (ทางเลือก) |
| สัญญาณแห่งความอ่อนแอ (Sign of Weakness) | SOW | D | การทะลุต่ำกว่า Creek ด้วยปริมาณ |
| จุดอุปทานสุดท้าย (Last Point of Supply) | LPSY | D | การปรับตัวขึ้นครั้งสุดท้ายด้วยปริมาณต่ำ (จุดเข้า) |

---

## 3. แผนผังการกระจาย #2 — แบบมี UTAD

### 3.1 แผนผัง ASCII

```
             Distribution Schematic #2 (With UTAD — Most Common)
                    
Price
  │                              UTAD
  │                             ╱    ╲
  │                            ╱      ╲  ← False breakout above BC
  │    ─────────────────────╱╱────────╲╲──────────────── Ice (Resistance)
  │         PSY   BC       ╱     ST     ╲   LPSY  LPSY
  │          │   ╱  ╲     ╱     ╱╲      ╲  ╱╲    ╱╲
  │          ↑  ╱    ╲   ╱     ╱  ╲      ╲╱  ╲  ╱  ╲
  │         ╱  ╱      ╲ ╱     ╱    ╲          ╲╱    ╲
  │        ╱  ╱        ╳     ╱      ╲    SOW          ╲
  │       ╱  ╱    AR  ╱ ╲   ╱        ╲  ╱              ╲
  │      ╱  ╱    ╱ ╲ ╱   ╲ ╱          ╲╱                ╲
  │     ╱  ╱────╱───╳─────╲╱───────────╲──────────────── Creek (Support)
  │    ╱       ╱            ╲           │╲
  │   ╱  Markup              ╲          │ ╲
  │  ╱                        ╲         │  ╲
  │ ╱                          ╲  SOW breaks below Creek
  │╱                            ╲       │    ╲
  │                              ╲      │     ╲
  │                               ╲     │      ╲ Markdown
  │                                     │
  │                                     │
  │  Prior   │Phase A│    Phase B       │Phase C│ Phase D  │ Phase E
  │  Markup  │(Stop) │   (Bldg Cause)  │(Test) │(Markdown)│
  │          │       │                  │(UTAD) │  Within  │
  └──────────┴───────┴──────────────────┴───────┴──────────┴──→ Time
  
  ปริมาณที่ UTAD:
  ████ ← ปริมาณสูงในความพยายาม Breakout (CM ขายเข้าสู่ผู้ซื้อ Breakout)
  จากนั้นปริมาณลดลงอย่างรวดเร็วเมื่อราคากลับตัว (ผู้ซื้อถูกดัก)
```

### 3.2 การจำแนกประเภท UTAD

| ประเภท | ความลึกเหนือ BC | ปริมาณ | ความเร็วกลับตัว | คุณภาพกับดัก |
|---|---|---|---|---|
| Type 1 (อ่อน) | > 3% เหนือ | สูงมาก | ช้า (5+ แท่ง) | ต่ำ — อาจเป็น Breakout จริง |
| Type 2 (ปานกลาง) | 1–3% เหนือ | สูง | ปานกลาง (2–4 แท่ง) | ปานกลาง |
| Type 3 (ดีที่สุด) | < 1% เหนือ | ปานกลาง | เร็ว (1–2 แท่ง) | สูง — ดักและกลับตัวทันที |

---

## 4. การวิเคราะห์เฟสอย่างละเอียด

### 4.1 เฟส A — การหยุดขาขึ้น

#### 4.1.1 อุปทานเบื้องต้น (Preliminary Supply — PSY)

**คำจำกัดความ**: แรงขายสำคัญแรกที่ปรากฏหลังจากขาขึ้นยาวนาน บ่งบอกว่าอุปทานเริ่มเอาชนะอุปสงค์ที่ราคาสูงเหล่านี้

**ลักษณะเด่น:**

| คุณลักษณะ | คำอธิบาย |
|---|---|
| **พฤติกรรมราคา** | แท่งเทียนช่วงกว้างที่ปิดที่ส่วนกลางหรือส่วนล่างระหว่างขาขึ้น |
| **ปริมาณ** | เพิ่มขึ้นอย่างเห็นได้ชัด — ขายเข้าสู่ความแข็งแกร่ง |
| **บริบท** | เกิดหลังขาขึ้นยาวนาน |
| **ตำแหน่งปิด** | ปิดที่ช่วงกลางถึงส่วนล่างแม้เปิดสูงกว่า |
| **ความสำคัญ** | คำเตือนแรกว่าขาขึ้นอาจหมดแรง |

```python
def detect_preliminary_supply(candles, i, avg_volume, atr, trend):
    """
    Detect Preliminary Supply (PSY) event.
    """
    if trend != 'UP':
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    conditions = {
        'uptrend': trend == 'UP',
        'increased_volume': c['volume'] > avg_volume * 1.5,
        'wide_spread': spread > atr * 0.8,
        'close_not_at_high': close_position < 0.65,
        'upper_wick': (c['high'] - max(c['open'], c['close'])) > spread * 0.3,
        'prior_rally': candles[i]['close'] > candles[max(0, i-20)]['close'],
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'PSY',
            'phase': 'A',
            'index': i,
            'price': c['close'],
            'price_high': c['high'],
            'volume_ratio': c['volume'] / avg_volume,
            'close_position': close_position,
            'confidence': sum(conditions.values()) / len(conditions),
        }
    return None
```

#### 4.1.2 จุดซื้อสุดขีด (Buying Climax — BC)

**คำจำกัดความ**: เหตุการณ์การซื้อสุดขีดที่กำหนดขอบเขตบนของกรอบการกระจาย ลักษณะเด่นคือปริมาณสุดขีด ช่วงราคากว้าง มักปิดใกล้จุดสูงสุดแต่ตามด้วยการกลับตัวทันที

**ลักษณะเด่น:**

| คุณลักษณะ | คำอธิบาย |
|---|---|
| **พฤติกรรมราคา** | แท่งเทียนขึ้นช่วงกว้างมาก มักทำจุดสูงใหม่ |
| **ปริมาณ** | สูงที่สุดในขาขึ้น — มักเป็น 3-5 เท่าของค่าเฉลี่ย |
| **ตำแหน่งปิด** | เริ่มปิดใกล้จุดสูง จากนั้นแท่งกลับตัวปิดต่ำกว่า |
| **บริบท** | ความตื่นเต้นสุดขีด — สื่อขาขึ้นอย่างมาก |
| **การกลับตัว** | การร่วงลงอย่างรุนแรงตามมา (1–3 แท่ง) |
| **ความสำคัญ** | กำหนดยอดของกรอบซื้อขาย (ระดับ Ice) |

**ดัชนีความรุนแรงของ Buying Climax:**

$$
\text{BCI} = \frac{V(t)}{\bar{V}_{50}} \times \frac{\text{Spread}(t)}{ATR_{14}} \times \text{CPos}(t)
$$

โดยที่:
- BCI < 3.0: Climax อ่อน — อาจไม่กำหนดจุดสูงสุด
- BCI 3.0–6.0: Climax ปานกลาง
- BCI > 6.0: Climax แข็งแกร่ง — ความน่าจะเป็นสูงที่การกระจายเริ่มต้น

```python
def detect_buying_climax(candles, i, avg_volume_20, avg_volume_50, atr, psy_event):
    """
    Detect Buying Climax (BC) event.
    """
    if psy_event is None:
        return None
    
    if i - psy_event['index'] > 30:
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    is_new_high = c['high'] >= max(cc['high'] for cc in candles[max(0, i-50):i])
    
    conditions = {
        'extreme_volume': c['volume'] > avg_volume_20 * 2.5,
        'wide_spread': spread > atr * 1.3,
        'new_high_area': is_new_high or c['high'] >= candles[i-1]['high'],
        'psy_exists': psy_event is not None,
        'climactic_close': close_position > 0.5,
    }
    
    reversal_detected = False
    if i + 1 < len(candles):
        next_bar = candles[i + 1]
        if next_bar['close'] < next_bar['open'] and next_bar['close'] < c['close']:
            reversal_detected = True
    conditions['reversal_hint'] = reversal_detected or close_position < 0.6
    
    bci = (c['volume'] / avg_volume_50) * (spread / atr) * close_position
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'BC',
            'phase': 'A',
            'index': i,
            'price_high': c['high'],
            'price_close': c['close'],
            'volume_ratio': c['volume'] / avg_volume_20,
            'spread_ratio': spread / atr,
            'close_position': close_position,
            'bci': bci,
            'confidence': sum(conditions.values()) / len(conditions),
            'range_top': c['high'],
        }
    return None
```

#### 4.1.3 ปฏิกิริยาอัตโนมัติ (Automatic Reaction — AR)

**คำจำกัดความ**: การร่วงลงอย่างรุนแรงที่เกิดขึ้นทันทีหลัง Buying Climax เป็นปฏิกิริยาอัตโนมัติเมื่อเกิดการขายทำกำไรและผู้ขายชอร์ตเข้ามา AR กำหนดขอบเขตล่างของกรอบการกระจาย (Creek/แนวรับ)

**ลักษณะเด่น:**

| คุณลักษณะ | คำอธิบาย |
|---|---|
| **พฤติกรรมราคา** | การร่วงลงอย่างรุนแรงพร้อมแท่งขาลง |
| **ปริมาณ** | ปานกลาง-สูง ลดลงจากระดับ BC |
| **ระยะเวลา** | สั้น — โดยปกติ 3–10 แท่ง |
| **การย้อนกลับ** | โดยปกติ 30–60% ของขาขึ้นสุดท้าย |
| **ความสำคัญ** | กำหนด Creek (แนวรับ) ของกรอบ |

```python
def detect_automatic_reaction(candles, i, bc_event, avg_volume, atr):
    """
    Detect Automatic Reaction (AR) — selloff after BC.
    AR is detected at the swing low following BC.
    """
    if bc_event is None:
        return None
    
    bc_idx = bc_event['index']
    if i - bc_idx > 15 or i - bc_idx < 2:
        return None
    
    current_low = candles[i]['low']
    
    is_swing_low = current_low <= min(c['low'] for c in candles[bc_idx:i+1])
    
    if i + 1 < len(candles):
        bouncing = candles[i+1]['close'] > candles[i]['close']
    else:
        bouncing = candles[i]['close'] > candles[i]['low'] + (candles[i]['high'] - candles[i]['low']) * 0.3
    
    bc_high = bc_event['price_high']
    decline_size = bc_high - current_low
    
    pre_bc_low = min(c['low'] for c in candles[max(0, bc_idx-20):bc_idx])
    rally_size = bc_high - pre_bc_low
    retracement = decline_size / rally_size if rally_size > 0 else 0
    
    conditions = {
        'follows_bc': (i - bc_idx) >= 2 and (i - bc_idx) <= 15,
        'is_swing_low': is_swing_low,
        'significant_decline': decline_size > atr * 1.5,
        'minimum_retracement': retracement >= 0.25,
        'price_bouncing': bouncing,
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'AR',
            'phase': 'A',
            'index': i,
            'price_low': current_low,
            'decline_size': decline_size,
            'retracement_pct': retracement,
            'confidence': sum(conditions.values()) / len(conditions),
            'range_bottom': current_low,
        }
    return None
```

### 4.2 เฟส B — การสร้างเหตุ (Building the Cause — Distribution)

เฟส B เป็นเฟสที่ยาวนานที่สุดที่ CM กระจายสินค้าคงเหลือ ราคาแกว่งตัวระหว่าง Ice (BC high) และ Creek (AR low)

#### 4.2.1 การทดสอบรอง (ST) ในการกระจาย

**คำจำกัดความ**: การทดสอบซ้ำพื้นที่ BC ด้วยปริมาณซื้อที่ลดลง ยืนยันว่าอุปสงค์อ่อนแอลงที่ระดับเหล่านี้

```python
def detect_distribution_st(candles, i, bc_event, ar_event, avg_volume, atr):
    """
    Detect Secondary Test (ST) of the Buying Climax area.
    """
    if bc_event is None or ar_event is None:
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    bc_high = bc_event['price_high']
    range_height = bc_high - ar_event['price_low']
    
    proximity_to_bc = (bc_high - c['high']) / range_height if range_height > 0 else 1.0
    
    conditions = {
        'near_bc_level': abs(proximity_to_bc) < 0.15,
        'lower_volume': c['volume'] < bc_event['volume_ratio'] * avg_volume * 0.7,
        'narrower_spread': spread < bc_event['spread_ratio'] * atr * 0.8,
        'holds_below_bc': c['high'] <= bc_high + atr * 0.3,
        'after_ar': i > ar_event['index'],
        'bearish_or_neutral_close': close_position < 0.7,
    }
    
    vol_ratio = (bc_event['volume_ratio'] * avg_volume) / c['volume'] if c['volume'] > 0 else 0
    quality = vol_ratio * (1 - proximity_to_bc)
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'ST',
            'phase': 'B',
            'index': i,
            'price_high': c['high'],
            'quality': quality,
            'volume_vs_bc': c['volume'] / (bc_event['volume_ratio'] * avg_volume),
            'proximity_to_bc': proximity_to_bc,
            'confidence': sum(conditions.values()) / len(conditions),
            'interpretation': 'STRONG' if quality > 3.0 else 'MODERATE' if quality > 1.5 else 'WEAK',
        }
    return None
```

#### 4.2.2 รูปแบบปริมาณเฟส B

```
Phase B — Demand Absorption Pattern (Distribution)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Price   BC/Ice ─────────────────────────────────── Resistance
                ╲     ╱╲        ╱╲       ╱╲
                 ╲   ╱  ╲      ╱  ╲     ╱  ╲╱╲
                  ╲ ╱    ╲    ╱    ╲   ╱       ╲
                   ╲      ╲  ╱      ╲ ╱         ╲
        AR/Creek ───╲──────╲╱────────╲╱──────────╲── Support
                     ╲      ╳
                      ╲    ╱ (possible test below support)
                       ╲  ╱
                      SOW emerging

ปริมาณขาขึ้น:  ████  ███   ███   ██    ██   █     ← ลดลง
ปริมาณขาลง:    ██    ██    ███   ███   ████ ████  ← เพิ่มขึ้น

สิ่งสำคัญ: ความพยายามเพิ่มขึ้นในขาลง ลดลงในขาขึ้น
     = อุปทานเอาชนะอุปสงค์ = ยืนยันการกระจาย

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.3 เฟส C — UTAD (Upthrust After Distribution)

#### 4.3.1 Upthrust หลังการกระจาย (UTAD)

**คำจำกัดความ**: Breakout เท็จเหนือแนวต้านกรอบซื้อขาย (BC/ระดับ Ice) ที่กลับตัวอย่างรวดเร็ว CM ดันราคาเหนือแนวต้านเพื่อ Trigger Buy Stop ดึงดูดเทรดเดอร์ Breakout และขายสินค้าคงเหลือสุดท้ายในราคาสูงสุด

**ลักษณะเด่น:**

| คุณลักษณะ | คำอธิบาย |
|---|---|
| **พฤติกรรมราคา** | การทะลุเหนือ Ice ชั่วคราว ตามด้วยการกลับตัวเร็ว |
| **ปริมาณ** | ผันแปร — UTAD ที่ดีที่สุดแสดงปริมาณสูง (ขายเข้าสู่การซื้อ) |
| **ระยะเวลา** | 1–5 แท่งเหนือแนวต้านก่อนกลับตัว |
| **ความลึก** | โดยปกติ 0.5–3% เหนือระดับ Ice |
| **จุดประสงค์** | ดักผู้ซื้อ Breakout ให้ CM ขายสินค้าคงเหลือสุดท้าย |
| **ความสำคัญ** | จุดเข้า Short ที่มีความน่าจะเป็นสูงสุดในการกระจาย |

**คะแนนคุณภาพ UTAD:**

$$
\text{UTAD\_Quality} = \frac{V_{\text{UTAD\_bar}}}{\bar{V}_{20}} \times (1 - \text{CPos}_{\text{reversal}}) \times \frac{1}{\text{Depth}^{0.5}}
$$

```python
def detect_utad(candles, i, range_resistance, range_support, avg_volume, atr, st_events):
    """
    Detect Upthrust After Distribution (UTAD) — false breakout above resistance.
    """
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    if c['high'] <= range_resistance:
        return None
    
    depth = c['high'] - range_resistance
    depth_atr = depth / atr
    
    close_below_resistance = c['close'] <= range_resistance
    close_near_resistance = c['close'] <= range_resistance + atr * 0.2
    
    if depth_atr < 0.5 and c['volume'] <= avg_volume * 1.5:
        utad_type = 3
        base_confidence = 0.85
    elif depth_atr < 1.5:
        utad_type = 2
        base_confidence = 0.70
    elif depth_atr < 3.0:
        utad_type = 1
        base_confidence = 0.50
    else:
        return None
    
    demand_weakening = True
    rally_volumes = [e.get('volume_vs_bc', 1.0) for e in st_events if e.get('event') == 'ST']
    if len(rally_volumes) >= 2:
        demand_weakening = rally_volumes[-1] <= rally_volumes[-2]
    
    conditions = {
        'penetrates_resistance': c['high'] > range_resistance,
        'limited_depth': depth_atr < 2.5,
        'reversal_close': close_below_resistance or close_near_resistance,
        'bearish_close_position': close_position < 0.5,
        'demand_weakening': demand_weakening,
        'volume_present': c['volume'] > avg_volume * 0.8,
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'UTAD',
            'phase': 'C',
            'index': i,
            'utad_type': utad_type,
            'price_high': c['high'],
            'price_close': c['close'],
            'depth': depth,
            'depth_atr': depth_atr,
            'volume_ratio': c['volume'] / avg_volume,
            'close_below_resistance': close_below_resistance,
            'confidence': base_confidence * (sum(conditions.values()) / len(conditions)),
            'trade_action': {
                3: 'AGGRESSIVE_SHORT',
                2: 'SHORT_ON_TEST',
                1: 'WAIT_FOR_CONFIRMATION'
            }[utad_type],
            'stop_loss': c['high'] + atr * 0.5,
        }
    return None
```

#### 4.3.2 การทดสอบ UTAD

**คำจำกัดความ**: หลัง UTAD กลับตัว ราคาอาจปรับตัวขึ้นกลับมาที่จุดสูง UTAD เพื่อยืนยันว่าอุปทานเอาชนะอุปสงค์ที่ระดับเหล่านี้ การทดสอบควรมีปริมาณต่ำกว่าและไม่ถึงจุดสูง UTAD

```python
def detect_test_of_utad(candles, i, utad_event, avg_volume, atr):
    """
    Detect the Test after a UTAD event — highest conviction short entry.
    """
    if utad_event is None:
        return None
    
    bars_since_utad = i - utad_event['index']
    if bars_since_utad < 2 or bars_since_utad > 15:
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    utad_high = utad_event['price_high']
    proximity = abs(c['high'] - utad_high) / atr
    
    conditions = {
        'near_utad_area': proximity < 1.5,
        'lower_high': c['high'] < utad_high,
        'lower_volume': c['volume'] < utad_event['volume_ratio'] * avg_volume * 0.8,
        'bearish_close': close_position < 0.4,
        'narrower_spread': spread < atr * 1.0,
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'TEST_OF_UTAD',
            'phase': 'C',
            'index': i,
            'price_high': c['high'],
            'price_close': c['close'],
            'distance_from_utad': utad_high - c['high'],
            'volume_vs_utad': c['volume'] / (utad_event['volume_ratio'] * avg_volume),
            'confidence': 0.88 * (sum(conditions.values()) / len(conditions)),
            'trade_action': 'STRONG_SHORT',
            'stop_loss': utad_high + atr * 0.3,
        }
    return None
```

### 4.4 เฟส D — Markdown ภายในกรอบ

#### 4.4.1 สัญญาณแห่งความอ่อนแอ (Sign of Weakness — SOW)

**คำจำกัดความ**: การร่วงลงอย่างแข็งแกร่งด้วยปริมาณที่เพิ่มขึ้นที่ทะลุต่ำกว่า Creek (แนวรับ) ยืนยันว่าการกระจายเสร็จสมบูรณ์และ Markdown เริ่มต้น

**ลักษณะเด่น:**

| คุณลักษณะ | คำอธิบาย |
|---|---|
| **พฤติกรรมราคา** | การเคลื่อนตัวขาลงแข็งแกร่งทะลุต่ำกว่า AR low/Creek support |
| **ปริมาณ** | เพิ่มขึ้นอย่างมาก — ยืนยันอุปทานเป็นใหญ่ |
| **ช่วงราคา** | แท่งขาลงกว้าง |
| **ราคาปิด** | ใกล้จุดต่ำสุดของแท่ง |
| **ความสำคัญ** | ยืนยันการเปลี่ยนเฟสจากการกระจายเป็น Markdown |

```python
def detect_sign_of_weakness(candles, i, creek_level, avg_volume, atr, range_height):
    """
    Detect Sign of Weakness (SOW) — breakdown below Creek.
    """
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    if c['close'] >= creek_level:
        return None
    
    breakdown_distance = creek_level - c['close']
    breakdown_atr = breakdown_distance / atr
    
    conditions = {
        'closes_below_creek': c['close'] < creek_level,
        'significant_breakdown': breakdown_atr > 0.3,
        'strong_volume': c['volume'] > avg_volume * 1.5,
        'wide_spread': spread > atr * 0.8,
        'bearish_close': close_position < 0.4,
        'body_below_creek': (c['open'] + c['close']) / 2 < creek_level,
    }
    
    strength = (c['volume'] / avg_volume) * (spread / atr) * (1 - close_position)
    strength *= breakdown_distance / range_height if range_height > 0 else 0
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'SOW',
            'phase': 'D',
            'index': i,
            'price_close': c['close'],
            'price_low': c['low'],
            'breakdown_distance': breakdown_distance,
            'strength': strength,
            'volume_ratio': c['volume'] / avg_volume,
            'confidence': sum(conditions.values()) / len(conditions),
        }
    return None
```

#### 4.4.2 จุดอุปทานสุดท้าย (Last Point of Supply — LPSY)

**คำจำกัดความ**: หลัง SOW ราคาอาจปรับตัวขึ้นกลับไปที่ Creek (ซึ่งตอนนี้ทำหน้าที่เป็นแนวต้าน) การปรับตัวนี้ควรอ่อนแอ — ด้วยปริมาณต่ำพร้อมช่วงราคาแคบ — และเป็นโอกาสสุดท้ายในการขาย/Short ก่อน Markdown ที่ยั่งยืน

**ลักษณะเด่น:**

| คุณลักษณะ | คำอธิบาย |
|---|---|
| **พฤติกรรมราคา** | การปรับตัวขึ้นอ่อนแอไปที่ Creek ล้มเหลวที่หรือต่ำกว่า |
| **ปริมาณ** | ต่ำ — ต่ำกว่าปริมาณ SOW อย่างมาก |
| **ช่วงราคา** | แคบ — แท่งเทียนเล็กลง |
| **ราคาปิด** | ควรปิดต่ำกว่าหรือที่ระดับ Creek |
| **ความสำคัญ** | จุดเข้า Short ที่ดีที่สุดหลังยืนยัน SOW |
| **LPSY หลายครั้ง** | อาจเกิดหลายครั้ง แต่ละครั้งที่ระดับต่ำลง |

```python
def detect_last_point_of_supply(candles, i, sow_event, creek_level, avg_volume, atr):
    """
    Detect Last Point of Supply (LPSY) — weak rally after SOW.
    """
    if sow_event is None:
        return None
    
    bars_since_sow = i - sow_event['index']
    if bars_since_sow < 2 or bars_since_sow > 25:
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    proximity_to_creek = abs(c['high'] - creek_level) / atr
    
    conditions = {
        'near_creek': proximity_to_creek < 1.5,
        'fails_at_creek': c['high'] <= creek_level + atr * 0.2,
        'declining_volume': c['volume'] < sow_event['volume_ratio'] * avg_volume * 0.5,
        'narrow_spread': spread < atr * 0.8,
        'bearish_close': close_position < 0.5,
        'rally_from_sow': c['high'] > sow_event['price_low'],
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'LPSY',
            'phase': 'D',
            'index': i,
            'price_high': c['high'],
            'price_close': c['close'],
            'distance_from_creek': creek_level - c['high'],
            'volume_ratio': c['volume'] / avg_volume,
            'confidence': 0.82 * (sum(conditions.values()) / len(conditions)),
            'trade_action': 'SHORT',
            'stop_loss': creek_level + atr * 0.5,
        }
    return None
```

---

## 5. รูปแบบปริมาณระหว่างการกระจาย

### 5.1 ตารางลักษณะปริมาณ

| เหตุการณ์ | ปริมาณที่คาดหวัง | เทียบกับ 20-SMA | ช่วงราคา | ตำแหน่งปิด | การตีความ |
|---|---|---|---|---|---|
| PSY | เพิ่มขึ้น | 1.5–2.5 เท่า | กว้าง | ล่าง-กลาง | อุปทานปรากฏขึ้นครั้งแรก |
| BC | สุดขีด | 2.5–5.0 เท่า | กว้างมาก | กลาง-สูง (จากนั้นกลับตัว) | ซื้อตื่นเต้น CM ขาย |
| AR | ปานกลาง-สูง | 1.0–2.0 เท่า | กว้าง | ส่วนล่าง | ขายทำกำไร + Short |
| ST | ลดลงจาก BC | 0.5–0.8 เท่า | แคบกว่า | ต่ำกว่า BC | อุปสงค์อ่อนแอลง |
| การปรับตัวขึ้นเฟส B | ลดลงเรื่อย ๆ | 0.3–0.7 เท่า เทียบ BC | แคบลง | ผันแปร | การกระจายอย่างต่อเนื่อง |
| UTAD | สูง (ขาย) | 1.5–3.0 เท่า | ปานกลาง-กว้าง | ต่ำกว่าแนวต้าน (กลับตัว) | กับดัก — CM ขายให้ผู้ซื้อ Breakout |
| การทดสอบ UTAD | ต่ำ | 0.3–0.6 เท่า | แคบ | ส่วนล่าง | ยืนยันอุปสงค์หมดลง |
| SOW | สูง | 1.5–3.0 เท่า | กว้าง | ใกล้จุดต่ำ | อุปทานเอาชนะอุปสงค์ |
| LPSY | ต่ำ | 0.3–0.6 เท่า | แคบ | ต่ำกว่ากลาง | ไม่มีอุปสงค์ที่ระดับสูงกว่า |

### 5.2 ความแตกต่างปริมาณที่สำคัญในการกระจาย

ลักษณะปริมาณหลักของการกระจาย:

$$
\frac{V_{\text{rallies}}(t)}{V_{\text{declines}}(t)} \rightarrow 0 \quad \text{as} \quad t \rightarrow t_{\text{breakdown}}
$$

กล่าวคือ: **ปริมาณในขาขึ้นลดลงในขณะที่ปริมาณในขาลงเพิ่มขึ้น** ตลอดช่วงการกระจาย

### 5.3 ดัชนีความหมดลงของอุปสงค์ (Demand Exhaustion Index — DEI)

กระจกของดัชนีความหมดลงของอุปทานสำหรับการสะสม:

$$
\text{DEI}(t) = \frac{\sum_{i=t_0}^{t} V_{\text{up}}(i) \cdot |\Delta P_{\text{up}}(i)|}{\sum_{i=t_0}^{t} V_{\text{down}}(i) \cdot |\Delta P_{\text{down}}(i)|}
$$

**การตีความ:**
- DEI > 2.0 ตอนเริ่มต้นกรอบ (อุปสงค์หนักจากขาขึ้นก่อนหน้า)
- DEI ลดลงเข้าหา 1.0 (อุปสงค์ถูกดูดซับโดยอุปทานของ CM)
- DEI < 0.5 ใกล้จุดจบ (อุปสงค์หมดลง — การทะลุใกล้เกิดขึ้น)

---

## 6. การกระจายเทียบกับการสะสมซ้ำ (Re-Accumulation)

### 6.1 ความแตกต่างที่สำคัญ

หนึ่งในการแยกแยะที่สำคัญและยากที่สุดในการวิเคราะห์ Wyckoff คือการตัดสินว่ากรอบซื้อขายที่ยอดขาขึ้นเป็น **การกระจาย** (จะทะลุลง) หรือ **การสะสมซ้ำ** (จะทะลุขึ้น — "บันไดก้าว" สู่ราคาสูงกว่า)

### 6.2 ตัวแยกความแตกต่างหลัก

| ลักษณะ | การกระจาย (Distribution) | การสะสมซ้ำ (Re-Accumulation) |
|---|---|---|
| **ปริมาณขาขึ้น** | ลดลงตามเวลา | คงที่หรือเพิ่มขึ้น |
| **ปริมาณขาลง** | เพิ่มขึ้นตามเวลา | ลดลง |
| **พฤติกรรม UTAD** | กลับตัวเร็ว ผู้ซื้อถูกดัก | ตื้นหรือไม่มี |
| **ตำแหน่งปิดขาขึ้น** | แย่ลง (ปิดต่ำในแท่ง) | แข็งแกร่ง (ปิดที่จุดสูง) |
| **การตอบสนองที่แนวรับ** | ดีดกลับอ่อน ทะลุด้วยปริมาณ | ดีดกลับแข็ง ยืนได้ |
| **แนวโน้มก่อนกรอบ** | ขาขึ้นยาวนาน (น่าจะหมดแรง) | ขาขึ้นปานกลาง (น่าจะต่อเนื่อง) |
| **ระยะเวลากรอบ** | สั้นกว่า (1/3 ถึง 2/3 ของ Markup ก่อนหน้า) | ยาวกว่าเทียบกับการหยุดพัก |
| **พฤติกรรม SOW** | ทะลุแนวรับด้วยปริมาณสูง | แนวรับยืน Break เท็จฟื้นตัว |
| **บริบทกว้าง** | แนวต้าน HTF วัฏจักรยาว | HTF อยู่กลางแนวโน้ม Pullback |

### 6.3 แบบจำลองให้คะแนนการกระจายเทียบกับการสะสมซ้ำ

$$
P(\text{Distribution}) = \sigma\left(\sum_{k=1}^{n} w_k \cdot f_k(\mathbf{x})\right)
$$

| ปัจจัย ($f_k$) | น้ำหนัก ($w_k$) | เข้าข่ายการกระจายเมื่อ |
|---|---|---|
| ปริมาณขาขึ้นลดลง | 2.0 | $V_{\text{rally\_slope}} < -0.1$ |
| ปริมาณขาลงเพิ่มขึ้น | 2.0 | $V_{\text{decline\_slope}} > 0.1$ |
| ตำแหน่งปิดขาขึ้น | 1.5 | CPos เฉลี่ยขาขึ้น < 0.5 |
| ระยะเวลาขาขึ้นก่อนหน้า | 1.0 | > 2 เท่าของระยะเวลากรอบ |
| มี UTAD พร้อมกลับตัว | 2.5 | ตรวจพบ UTAD และล้มเหลว |
| SOW ทะลุแนวรับ | 3.0 | ยืนยัน SOW ต่ำกว่า Creek |
| HTF ที่แนวต้าน | 1.5 | ราคาที่แนวต้านรายสัปดาห์/รายเดือน |
| ความเชื่อมั่นสุดขีด | 1.0 | ค่าอ่านขาขึ้นสุดขีด |

```python
def distribution_vs_reaccumulation(range_data, htf_context):
    """
    Score whether a trading range is distribution or re-accumulation.
    
    Returns:
        float: probability of distribution [0, 1]
    """
    features = {}
    
    rally_vols = range_data['rally_volumes']
    if len(rally_vols) >= 3:
        slope = np.polyfit(range(len(rally_vols)), rally_vols, 1)[0]
        features['rally_vol_declining'] = max(0, -slope / np.mean(rally_vols))
    else:
        features['rally_vol_declining'] = 0.5
    
    decline_vols = range_data['decline_volumes']
    if len(decline_vols) >= 3:
        slope = np.polyfit(range(len(decline_vols)), decline_vols, 1)[0]
        features['decline_vol_increasing'] = max(0, slope / np.mean(decline_vols))
    else:
        features['decline_vol_increasing'] = 0.5
    
    rally_cpos = range_data['rally_close_positions']
    features['weak_rally_closes'] = max(0, 1 - np.mean(rally_cpos) * 2) if rally_cpos else 0.5
    
    prior_trend_duration = range_data['prior_uptrend_bars']
    range_duration = range_data['range_bars']
    features['trend_exhausted'] = min(1.0, prior_trend_duration / (range_duration * 3))
    
    features['utad_present'] = 1.0 if range_data.get('utad_event') else 0.0
    features['sow_confirmed'] = 1.0 if range_data.get('sow_event') else 0.0
    features['htf_resistance'] = 1.0 if htf_context.get('at_htf_resistance') else 0.0
    
    weights = {
        'rally_vol_declining': 2.0,
        'decline_vol_increasing': 2.0,
        'weak_rally_closes': 1.5,
        'trend_exhausted': 1.0,
        'utad_present': 2.5,
        'sow_confirmed': 3.0,
        'htf_resistance': 1.5,
    }
    
    z = sum(weights[k] * features[k] for k in features)
    z_normalized = (z - 6.0) / 3.0
    
    probability = 1.0 / (1.0 + np.exp(-z_normalized))
    
    return {
        'probability_distribution': probability,
        'probability_reaccumulation': 1 - probability,
        'features': features,
        'recommendation': 'DISTRIBUTION' if probability > 0.65 else \
                         'RE_ACCUMULATION' if probability < 0.35 else 'UNCERTAIN'
    }
```

### 6.4 ตารางการตัดสินใจ

| P(Distribution) | การดำเนินการ | หมายเหตุ |
|---|---|---|
| > 0.80 | เปิดสถานะ Short เชิงรุก | ความเชื่อมั่นสูงว่าเป็นการกระจาย |
| 0.65–0.80 | Short อย่างระมัดระวัง SL แน่น | เอนไปขาลงแต่จัดการความเสี่ยง |
| 0.35–0.65 | **ไม่เปิดสถานะ** — รอความชัดเจน | ไม่แน่นอน — อย่าเทรด |
| 0.20–0.35 | Long อย่างระมัดระวัง คาดว่าจะ Breakout | เอนไปว่าเป็นการสะสมซ้ำ |
| < 0.20 | เปิดสถานะ Long เชิงรุก | ความเชื่อมั่นสูงว่าเป็นการสะสมซ้ำ |

---

## 7. แบบจำลองทางคณิตศาสตร์

### 7.1 พารามิเตอร์กรอบการกระจาย

$$
\text{Range} = [P_{\text{creek}}, P_{\text{ice}}]
$$

โดยที่:
- $P_{\text{ice}} = P_{\text{BC\_high}} \pm \epsilon$ (ระดับแนวต้าน)
- $P_{\text{creek}} = P_{\text{AR\_low}} \pm \epsilon$ (ระดับแนวรับ)

### 7.2 การประมาณเป้าหมายราคา (ขาลง)

**วิธีที่ 1: การประมาณจากกรอบ**

$$
\text{Target}_{\text{down}} = P_{\text{creek}} - k \cdot H_{\text{range}} \cdot \sqrt{\frac{T_{\text{range}}}{T_{\text{ref}}}}
$$

**วิธีที่ 2: การประมาณตาม ATR**

$$
\text{Target}_{\text{down}} = P_{\text{creek}} - m \cdot ATR \cdot \sqrt{\frac{T_{\text{dist}}}{20}}
$$

โดยที่ $m$:
- แบบอนุรักษ์นิยม: $m = 2.5$
- แบบปานกลาง: $m = 4.0$
- แบบเชิงรุก: $m = 6.0$

**วิธีที่ 3: Fibonacci Extension**

$$
\text{Target}_{1.0} = P_{\text{creek}} - 1.0 \times H_{\text{range}}
$$
$$
\text{Target}_{1.618} = P_{\text{creek}} - 1.618 \times H_{\text{range}}
$$
$$
\text{Target}_{2.618} = P_{\text{creek}} - 2.618 \times H_{\text{range}}
$$

### 7.3 แบบจำลองความน่าจะเป็นของ UTAD

$$
P(\text{UTAD} | \text{breakout above}) = \sigma\left(\beta_0 + \beta_1 x_V + \beta_2 x_D + \beta_3 x_T + \beta_4 x_C\right)
$$

โดยที่:
- $x_V$ = ปริมาณเทียบกับค่าเฉลี่ย (ปริมาณสูงพร้อมปิดไม่ดี = น่าจะเป็น UTAD)
- $x_D$ = ความลึกเหนือแนวต้าน (ตื้น = น่าจะเป็น UTAD มากกว่า)
- $x_T$ = จำนวนการทดสอบแนวต้านที่ล้มเหลวก่อนหน้า
- $x_C$ = ตำแหน่งปิดของแท่ง Breakout (ปิดต่ำกว่าแนวต้าน = น่าจะเป็น UTAD)

### 7.4 ตัวประมาณความสมบูรณ์ของการกระจาย

$$
\text{Completion}(\%) = \frac{\sum_{k=1}^{n} w_k \cdot \mathbb{1}(E_k \text{ detected})}{\sum_{k=1}^{n} w_k} \times 100
$$

| เหตุการณ์ ($E_k$) | น้ำหนัก ($w_k$) |
|---|---|
| ตรวจพบ PSY | 5 |
| ตรวจพบ BC | 15 |
| ตรวจพบ AR | 10 |
| ตรวจพบ ST พร้อม vol ลดลง | 15 |
| ตรวจพบ UTAD (หรือแนวต้านยืน) | 20 |
| ตรวจพบ SOW | 20 |
| ตรวจพบ LPSY | 15 |

---

## 8. ตรรกะเข้า/ออกสำหรับเทรด Short

### 8.1 จุดเข้า (จัดอันดับตามคุณภาพ)

#### จุดเข้า 1: การทดสอบ UTAD (Short คุณภาพสูงสุด)

```python
def entry_test_of_utad(utad_event, test_event, atr, range_height):
    """
    Highest quality short entry — after UTAD confirmed by test.
    """
    entry_price = test_event['price_close']
    stop_loss = utad_event['price_high'] + atr * 0.3
    risk = stop_loss - entry_price
    
    return {
        'entry_type': 'TEST_OF_UTAD',
        'direction': 'SHORT',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'risk': risk,
        'targets': [
            entry_price - range_height * 1.0,
            entry_price - range_height * 1.618,
            entry_price - range_height * 2.618,
        ],
        'risk_reward': [(entry_price - t) / risk for t in [
            entry_price - range_height * 1.0,
            entry_price - range_height * 1.618,
            entry_price - range_height * 2.618,
        ]],
        'position_size_pct': 2.0,
        'confidence': 0.88,
    }
```

#### จุดเข้า 2: UTAD โดยตรง (Short เชิงรุก)

```python
def entry_utad_direct(utad_event, atr, range_height):
    """
    Aggressive short directly on UTAD reversal bar.
    """
    entry_price = utad_event['price_close']
    stop_loss = utad_event['price_high'] + atr * 0.5
    risk = stop_loss - entry_price
    
    return {
        'entry_type': 'UTAD_DIRECT',
        'direction': 'SHORT',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'risk': risk,
        'targets': [
            entry_price - range_height * 0.8,
            entry_price - range_height * 1.5,
            entry_price - range_height * 2.5,
        ],
        'position_size_pct': 1.5,
        'confidence': 0.75,
    }
```

#### จุดเข้า 3: LPSY (หลังยืนยัน SOW)

```python
def entry_lpsy(lpsy_event, creek_level, atr, range_height):
    """
    Short on weak rally after SOW — for those who missed UTAD.
    """
    entry_price = lpsy_event['price_close']
    stop_loss = creek_level + atr * 0.5
    risk = stop_loss - entry_price
    
    return {
        'entry_type': 'LPSY',
        'direction': 'SHORT',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'risk': risk,
        'targets': [
            entry_price - range_height * 1.0,
            entry_price - range_height * 2.0,
            entry_price - range_height * 3.0,
        ],
        'position_size_pct': 1.5,
        'confidence': 0.80,
    }
```

#### จุดเข้า 4: SOW Break Retest

```python
def entry_sow_retest(sow_event, creek_level, atr, range_height):
    """
    Short on retest of broken Creek (support turned resistance).
    """
    entry_price = creek_level
    stop_loss = creek_level + atr * 0.8
    risk = stop_loss - entry_price
    
    return {
        'entry_type': 'SOW_RETEST',
        'direction': 'SHORT',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'risk': risk,
        'targets': [
            entry_price - range_height * 1.0,
            entry_price - range_height * 2.0,
        ],
        'position_size_pct': 1.0,
        'confidence': 0.82,
    }
```

### 8.2 กลยุทธ์การเพิ่มขนาดสถานะ Short

```
กลยุทธ์การเพิ่มขนาดสถานะ Short ระหว่างการกระจาย:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

สถานะ Short ที่วางแผนทั้งหมด: 100%

จุดเข้า 1: UTAD (โดยตรง)           → 25% ของสถานะทั้งหมด
จุดเข้า 2: การทดสอบ UTAD           → 25% ของสถานะทั้งหมด (เพิ่มเติม)
จุดเข้า 3: SOW break               → 25% ของสถานะทั้งหมด (เพิ่มเติม)
จุดเข้า 4: LPSY / SOW retest       → 25% ของสถานะทั้งหมด (เพิ่มเติม)

ราคาเข้าเฉลี่ย: ค่าเฉลี่ยถ่วงน้ำหนักของทุกจุดเข้า
จุดตัดขาดทุนรวม: เหนือจุดสูง UTAD
R:R รวม: ควร >= 3:1 สำหรับสถานะทั้งหมด

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 8.3 ตรรกะการออกสำหรับ Short

```python
def distribution_exit_logic(position, candle, market_state, atr):
    """
    Exit logic for short positions entered during distribution.
    """
    exit_signals = []
    
    if candle['high'] >= position['stop_loss']:
        exit_signals.append({
            'type': 'STOP_LOSS',
            'action': 'EXIT_ALL',
            'price': position['stop_loss'],
            'reason': 'Stop loss triggered — potential breakout above resistance'
        })
    
    if candle['low'] <= position['targets'][0] and not position.get('t1_hit'):
        exit_signals.append({
            'type': 'TARGET_1',
            'action': 'COVER_50PCT',
            'price': position['targets'][0],
            'reason': 'First target reached',
            'move_stop': 'BREAKEVEN'
        })
    
    if candle['low'] <= position['targets'][1] and not position.get('t2_hit'):
        exit_signals.append({
            'type': 'TARGET_2',
            'action': 'COVER_30PCT',
            'price': position['targets'][1],
            'reason': 'Second target reached',
            'move_stop': position['targets'][0]
        })
    
    if market_state.phase == 'ACCUMULATION':
        exit_signals.append({
            'type': 'PHASE_CHANGE',
            'action': 'COVER_ALL',
            'price': candle['close'],
            'reason': 'Accumulation detected — cover shorts'
        })
    
    if market_state.phase == 'MARKDOWN' and position.get('t1_hit'):
        trail_stop = candle['low'] + atr * 2.5
        if trail_stop < position['stop_loss']:
            exit_signals.append({
                'type': 'TRAIL_STOP_UPDATE',
                'action': 'UPDATE_STOP',
                'new_stop': trail_stop,
                'reason': 'Trailing stop tightened during markdown'
            })
    
    if candle['volume'] > market_state.avg_volume * 3.0:
        spread = candle['high'] - candle['low']
        close_pos = (candle['close'] - candle['low']) / spread if spread > 0 else 0.5
        if close_pos > 0.4 and spread > atr * 1.5:
            exit_signals.append({
                'type': 'POTENTIAL_SC',
                'action': 'TIGHTEN_STOP',
                'new_stop': candle['high'] + atr * 0.5,
                'reason': 'Potential Selling Climax — tighten stop, possible accumulation forming'
            })
    
    return exit_signals
```

---

## 9. การจัดการความเสี่ยงระหว่างการกระจาย

### 9.1 พารามิเตอร์ความเสี่ยงตามประเภทจุดเข้า

| ประเภทจุดเข้า | ความเสี่ยงสูงสุด (%) | SL ปกติ (ATR) | R:R ขั้นต่ำ | เกณฑ์ความเชื่อมั่น |
|---|---|---|---|---|
| UTAD (Type 3) | 2.0% | 0.5–1.0 | 4:1 | 0.80 |
| UTAD (Type 2) | 1.5% | 1.0–1.5 | 3:1 | 0.70 |
| UTAD (Type 1) | 0.5% | 1.5–2.5 | 5:1 | 0.60 |
| การทดสอบ UTAD | 2.0% | 0.5–1.0 | 3:1 | 0.85 |
| SOW Breakdown | 1.5% | 1.5–2.0 | 2:1 | 0.70 |
| LPSY | 1.5% | 0.5–1.0 | 3:1 | 0.75 |
| SOW Retest | 1.0% | 0.5–0.8 | 3:1 | 0.80 |

### 9.2 ปัจจัยเสี่ยงเฉพาะการกระจาย

| ปัจจัยเสี่ยง | ผลกระทบ | การบรรเทา |
|---|---|---|
| **โอกาส Short Squeeze** | การพุ่งขึ้นอย่างฉับพลันสวนทาง Short | ใช้ Stop Loss เสมอ; Leverage สูงสุด 3 เท่า |
| **Positive Funding (คริปโต)** | ต้นทุนถือสถานะ Short | คำนวณ Funding Rate ในผลตอบแทนที่คาดหวัง |
| **ข่าวดีที่ไม่คาดคิด** | อาจทำให้การกระจายเป็นโมฆะ | ลดขนาดก่อนเหตุการณ์ที่รู้ |
| **ความเสี่ยง Re-Accumulation** | รูปแบบอาจเป็นบันไดก้าว | ใช้แบบจำลองให้คะแนน Distribution vs Re-Accum |
| **Gap Risk (Forex)** | Gap สุดสัปดาห์อาจเกิน Stop | ลดสถานะเข้าสู่สุดสัปดาห์ |

### 9.3 การวาง Stop Loss แบบไดนามิก

สำหรับสถานะ Short ระหว่างการกระจาย:

$$
SL_{\text{initial}} = P_{\text{UTAD\_high}} + k \cdot ATR
$$

โดยที่ $k$:
- เชิงรุก: $k = 0.3$
- มาตรฐาน: $k = 0.5$
- อนุรักษ์นิยม: $k = 1.0$

หลังการยืนยัน (ตรวจพบ SOW):

$$
SL_{\text{confirmed}} = \min(SL_{\text{initial}}, P_{\text{creek}} + 0.5 \cdot ATR)
$$

---

## 10. ขั้นตอนการดำเนินการ

### 10.1 State Machine ตรวจจับการกระจาย

```
Distribution Detection State Machine:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

State 0: WATCHING (ขาขึ้นก่อนหน้า ไม่มีเหตุการณ์)
  │
  ├── ตรวจพบ PSY → State 1: PSY_DETECTED (10%)
  │
State 1: PSY_DETECTED
  │
  ├── ตรวจพบ BC → State 2: BC_DETECTED (25%)
  ├── หมดเวลา (30 แท่ง) → State 0
  │
State 2: BC_DETECTED
  │
  ├── ตรวจพบ AR → State 3: RANGE_FORMING (40%)
  ├── จุดสูงใหม่เหนือ BC ด้วยปริมาณขยาย → State 0 (ต่อเนื่อง)
  │
State 3: RANGE_FORMING
  │
  ├── ตรวจพบ ST ด้วยปริมาณต่ำกว่า → State 4: PHASE_B (55%)
  ├── Breakout ยั่งยืนเหนือ BC → State 0 (ต่อเนื่อง)
  │
State 4: PHASE_B
  │
  ├── ST หลายครั้งด้วยอุปสงค์อ่อนแอลง → State 5: DEMAND_EXHAUSTED (65%)
  ├── Breakout แข็งแกร่งเหนือ BC ด้วยปริมาณ → State 0 (breakout)
  │
State 5: DEMAND_EXHAUSTED
  │
  ├── ตรวจพบ UTAD → State 6: UTAD_DETECTED (80%)
  ├── ตรวจพบ SOW โดยไม่มี UTAD → State 7: SOW_DETECTED (75%)
  │
State 6: UTAD_DETECTED
  │
  ├── Test ยืนยัน UTAD → State 8: CONFIRMED_DISTRIBUTION (90%)
  ├── ราคายืนเหนือ → State 0 (breakout จริง)
  │
State 7: SOW_DETECTED
  │
  ├── LPSY ล้มเหลว → State 8: CONFIRMED_DISTRIBUTION (85%)
  ├── ราคากลับเหนือ Creek ด้วยปริมาณ → State 4 (ยังไม่ถึง)
  │
State 8: CONFIRMED_DISTRIBUTION
  │
  ├── Markdown เริ่ม → State 9: MARKDOWN (95%)
  │
State 9: MARKDOWN
  └── ติดตามจนกว่าจะเริ่มการสะสมที่ระดับต่ำกว่า

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 10.2 คลาสตรวจจับการกระจายแบบสมบูรณ์

```python
class DistributionDetector:
    """
    Complete state machine for detecting Wyckoff distribution.
    """
    
    def __init__(self, config):
        self.config = config
        self.state = 'WATCHING'
        self.confidence = 0.0
        self.events = []
        self.range_support = None  # Creek
        self.range_resistance = None  # Ice
        
    def update(self, candle, index, avg_volume, atr, trend):
        """Process a new candle and update distribution detection."""
        result = {
            'state': self.state,
            'confidence': self.confidence,
            'new_events': [],
            'signals': [],
        }
        
        if self.state == 'WATCHING':
            psy = detect_preliminary_supply(self.candles, index, avg_volume, atr, trend)
            if psy:
                self.events.append(psy)
                self.state = 'PSY_DETECTED'
                self.confidence = 0.10
                result['new_events'].append(psy)
        
        elif self.state == 'PSY_DETECTED':
            bc = detect_buying_climax(
                self.candles, index, avg_volume, avg_volume,
                atr, self._get_event('PSY')
            )
            if bc:
                self.events.append(bc)
                self.state = 'BC_DETECTED'
                self.confidence = 0.25
                self.range_resistance = bc['range_top']
                result['new_events'].append(bc)
        
        elif self.state == 'BC_DETECTED':
            ar = detect_automatic_reaction(
                self.candles, index, self._get_event('BC'), avg_volume, atr
            )
            if ar:
                self.events.append(ar)
                self.state = 'RANGE_FORMING'
                self.confidence = 0.40
                self.range_support = ar['range_bottom']
                result['new_events'].append(ar)
        
        elif self.state in ['RANGE_FORMING', 'PHASE_B']:
            st = detect_distribution_st(
                self.candles, index, self._get_event('BC'),
                self._get_event('AR'), avg_volume, atr
            )
            if st:
                self.events.append(st)
                self.state = 'PHASE_B'
                self.confidence = max(self.confidence, 0.55)
                result['new_events'].append(st)
            
            utad = detect_utad(
                self.candles, index, self.range_resistance,
                self.range_support, avg_volume, atr,
                [e for e in self.events if e['event'] == 'ST']
            )
            if utad:
                self.events.append(utad)
                self.state = 'UTAD_DETECTED'
                self.confidence = 0.80
                result['new_events'].append(utad)
                if utad['utad_type'] == 3:
                    result['signals'].append({
                        'action': 'SELL',
                        'type': 'UTAD_TYPE3',
                        'entry': candle['close'],
                        'stop_loss': utad['stop_loss'],
                        'confidence': utad['confidence'],
                    })
            
            sow = detect_sign_of_weakness(
                self.candles, index, self.range_support,
                avg_volume, atr, self.range_resistance - self.range_support
            )
            if sow:
                self.events.append(sow)
                self.state = 'SOW_DETECTED'
                self.confidence = 0.75
                result['new_events'].append(sow)
        
        elif self.state == 'UTAD_DETECTED':
            test = detect_test_of_utad(
                self.candles, index, self._get_event('UTAD'), avg_volume, atr
            )
            if test:
                self.events.append(test)
                self.state = 'CONFIRMED'
                self.confidence = 0.90
                result['new_events'].append(test)
                result['signals'].append({
                    'action': 'SELL',
                    'type': 'TEST_OF_UTAD',
                    'entry': candle['close'],
                    'stop_loss': test['stop_loss'],
                    'confidence': test['confidence'],
                })
        
        elif self.state == 'SOW_DETECTED':
            lpsy = detect_last_point_of_supply(
                self.candles, index, self._get_event('SOW'),
                self.range_support, avg_volume, atr
            )
            if lpsy:
                self.events.append(lpsy)
                self.state = 'CONFIRMED'
                self.confidence = 0.85
                result['new_events'].append(lpsy)
                result['signals'].append({
                    'action': 'SELL',
                    'type': 'LPSY',
                    'entry': candle['close'],
                    'stop_loss': lpsy['stop_loss'],
                    'confidence': lpsy['confidence'],
                })
        
        result['state'] = self.state
        result['confidence'] = self.confidence
        return result
    
    def _get_event(self, event_type):
        for e in reversed(self.events):
            if e['event'] == event_type:
                return e
        return None
```

---

## 11. การกระจายเฉพาะตลาด Forex

### 11.1 รูปแบบการกระจายตามเซสชัน

| รูปแบบ | คำอธิบาย | ความถี่ |
|---|---|---|
| **London Open Trap** | ราคาพุ่งเหนือ Asian High (UTAD) จากนั้นกลับตัวอย่างรุนแรง | พบบ่อยมาก |
| **NY Session Reversal** | การกระจายเสร็จที่ London Close, Markdown ใน NY | พบบ่อย |
| **Friday Distribution** | การกระจายที่จุดสูงสุดของสัปดาห์, Markdown สัปดาห์ถัดไป | ปานกลาง |
| **News Spike UTAD** | ข่าวสำคัญสร้าง Spike เหนือกรอบ = UTAD | ปานกลาง |

### 11.2 การกระจายจากธนาคารกลาง

เมื่อนโยบายธนาคารกลางเปลี่ยนจาก Dovish เป็น Hawkish (หรือในทางกลับกัน) กระบวนการมักเป็นไปตามการกระจายแบบ Wyckoff:

1. **BC** = การปรับตัวขึ้นครั้งสุดท้ายจากความคาดหวัง Dovish
2. **UTAD** = ตลาดกำหนดราคา "Dovish กว่าที่คาด" → Spike
3. **SOW** = การเซอร์ไพรส์ Hawkish หรือเปลี่ยนโทน → ทะลุลง
4. **Markdown** = สกุลเงินอ่อนค่าอย่างยั่งยืน

---

## 12. การกระจายเฉพาะตลาดคริปโต

### 12.1 สัญญาณ On-Chain ของการกระจาย

| เมตริก | สัญญาณการกระจาย | ความเชื่อมั่น |
|---|---|---|
| เงินไหลเข้าตลาดแลกเปลี่ยน > เงินไหลออก | เหรียญย้ายไปตลาดแลกเปลี่ยนเพื่อขาย | +15% |
| ที่อยู่วาฬลดยอดคงเหลือ | ผู้ถือรายใหญ่กำลังกระจาย | +15% |
| Long-Term Holder (LTH) ใช้จ่าย | Smart Money ขายทำกำไร | +10% |
| Stablecoin Reserve ลดลง | กำลังซื้อถูกหมดไป | +10% |
| Funding Rate บวกมาก | Long Leverage เกิน (สวนทาง = ขาลง) | +10% |
| Open Interest ที่จุดสุดขีด | Leverage มากเกิน = ความเสี่ยงการถูกบังคับขาย | +10% |

### 12.2 การปั่นตลาดเฉพาะตลาดแลกเปลี่ยน

ในคริปโต ตลาดแลกเปลี่ยนเองอาจทำหน้าที่เป็น CM:

- **Spoofing**: Wall ขายขนาดใหญ่ที่หายไปก่อนถูก Fill (สร้างความกลัว)
- **Wash Trading**: ปริมาณปลอมเพื่อดึงดูดผู้ซื้อระหว่างการกระจาย
- **Liquidation Cascades**: ดันราคาเพื่อ Trigger การบังคับขาย Leverage
- **Token Unlocks**: กำหนดการ Vesting สร้างเหตุการณ์อุปทานที่กำหนดไว้ล่วงหน้า

### 12.3 Bitcoin Dominance เป็นตัวชี้วัดการกระจาย

เมื่อ BTC.D (Bitcoin Dominance) เพิ่มขึ้นระหว่างกรอบการกระจายในอัลท์คอยน์:

$$
\text{Altcoin Distribution Probability} = P_{\text{base}} + \alpha \cdot \Delta BTC.D
$$

BTC.D เพิ่มขึ้นระหว่างกรอบอัลท์คอยน์ = เงินทุนหมุนออก = การกระจาย

---

## 13. ข้อผิดพลาดที่พบบ่อย

### 13.1 ข้อผิดพลาดในการเทรดการกระจาย

| # | ข้อผิดพลาด | ผลที่ตามมา | วิธีแก้ |
|---|---|---|---|
| 1 | Short เร็วเกินไปในเฟส B | ติดในกรอบ Stop Loss โดน | รอ UTAD หรือ SOW |
| 2 | สับสน Re-Accumulation กับการกระจาย | Short ในขาขึ้นที่ต่อเนื่อง | ใช้แบบจำลองให้คะแนน; บริบท HTF |
| 3 | ไม่ใส่ Stop Loss ในสถานะ Short | โอกาสขาดทุนไม่จำกัด | วาง Stop เหนือ UTAD เสมอ |
| 4 | สวนทางแนวโน้มก่อนยืนยัน | ขาดทุนเล็ก ๆ สะสม | ต้องมี SOW หรือ UTAD ก่อน Short |
| 5 | ละเลย Funding Rate (คริปโต) | ต้นทุนถือกินกำไร | คำนวณ Funding ใน R:R |
| 6 | ขนาดใหญ่เกินไปที่ UTAD ก่อนยืนยัน | ขาดทุนมากหาก Breakout จริง | เพิ่มขนาดทีละน้อย; สถานะแรกเล็ก |
| 7 | ไม่ปิดกำไรเมื่อมีการขายสุดขีด | พลาดกำไรจากการกลับตัว | ขายทำกำไรเมื่อสัญญาณ SC ปรากฏ |

### 13.2 รายการตรวจสอบคุณภาพรูปแบบการกระจาย

```
รายการตรวจสอบคุณภาพการกระจาย:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ ] มีขาขึ้นก่อนหน้า (อย่างน้อย 2 เท่าของความสูงกรอบ)
[ ] Buying Climax มีปริมาณสุดขีด (>= 2.5 เท่าของค่าเฉลี่ย)
[ ] Automatic Reaction กำหนดแนวรับ (Creek) ที่ชัดเจน
[ ] Secondary Test แสดงปริมาณซื้อลดลง
[ ] กรอบอยู่ในตำแหน่งอย่างน้อย 15 แท่ง
[ ] ปริมาณขาขึ้นลดลงเรื่อย ๆ
[ ] ปริมาณขาลงคงที่หรือเพิ่มขึ้น
[ ] ตรวจพบเหตุการณ์ UTAD หรือ SOW
[ ] หากเป็น UTAD: Test เกิดขึ้นด้วยปริมาณต่ำกว่าและ Lower High
[ ] หากเป็น SOW: ปริมาณขยายตัวอย่างมากใน Breakdown
[ ] แนวโน้มกรอบเวลาสูงกว่าแสดงสัญญาณหมดแรง
[ ] คะแนน Distribution vs Re-Accumulation > 0.65

คะแนน: จำนวนรายการที่ผ่าน / รายการทั้งหมด
คะแนนขั้นต่ำที่จะเทรด: 7/12 (58%)
ความเชื่อมั่นสูง: 10+/12 (83%+)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 14. เอกสารอ้างอิง

### 14.1 แหล่งข้อมูลหลัก

1. Wyckoff, R.D. (1931). *The Richard D. Wyckoff Method of Trading and Investing in Stocks*. — แผนผังและหลักการการกระจาย
2. Evans, R. (1969). *Wyckoff Course Notes — Distribution Phase Analysis*. Stock Market Institute.
3. Pruden, H.O. (2007). *The Three Skills of Top Trading*. Wiley. — Chapter 5: "Distribution Phase Behavioral Analysis."

### 14.2 การปรับใช้สมัยใหม่

4. Williams, T. (2005). *Master the Markets*. TradeGuider Systems. — บทเรื่องสัญญาณการกระจายผ่าน VSA
5. Weis, D.H. (2013). *Trades About to Happen*. Wiley. — การวิเคราะห์ Wave ของการกระจาย
6. Bogomazov, R. (2020). "Identifying Distribution — Wyckoff Analytics Webinar Series." wyckoffanalytics.com.

### 14.3 เฉพาะคริปโต

7. Glassnode Academy. "On-Chain Analysis for Distribution Detection." glassnode.com.
8. Willy Woo (2021). "Bitcoin Whale Distribution Metrics." woobull.com.

---

> **เอกสารถัดไป**: `03_market_structure_bos_choch.md` — การแตกหักโครงสร้าง (Break of Structure) และการเปลี่ยนลักษณะ (Change of Character)
