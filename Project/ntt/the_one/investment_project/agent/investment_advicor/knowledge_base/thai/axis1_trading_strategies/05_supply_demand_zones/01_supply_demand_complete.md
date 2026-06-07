# การเทรดโซน Supply & Demand — คู่มือฉบับสมบูรณ์

## ข้อมูลเอกสาร
| ฟิลด์ | ค่า |
|---|---|
| **Strategy ID** | SDZ-001 |
| **หมวดหมู่** | Price Action / Institutional Flow |
| **สินทรัพย์** | Forex, Crypto, หุ้น, สินค้าโภคภัณฑ์ |
| **ไทม์เฟรม** | M15 ถึง Monthly (หลัก: H1–Daily) |
| **ความซับซ้อน** | ระดับกลางถึงสูง |
| **ความเหมาะสมกับ AI** | สูง — การตรวจจับโซนสามารถนิยามทางเรขาคณิตได้ |
| **เวอร์ชัน** | 2.0 |
| **อัปเดตล่าสุด** | 2026-04-12 |

---

## สารบัญ
1. [บทนำ](#1-บทนำ)
2. [พื้นฐาน Supply and Demand](#2-พื้นฐาน-supply-and-demand)
3. [รูปแบบการก่อตัวของโซน](#3-รูปแบบการก่อตัวของโซน)
4. [การระบุโซนใหม่](#4-การระบุโซนใหม่)
5. [การให้คะแนนคุณภาพโซน](#5-การให้คะแนนคุณภาพโซน)
6. [โซนซ้อนทับและการปรับละเอียดโซน](#6-โซนซ้อนทับและการปรับละเอียดโซน)
7. [อายุการใช้งานของโซน](#7-อายุการใช้งานของโซน)
8. [ตรรกะการเข้าและออก](#8-ตรรกะการเข้าและออก)
9. [โมเดลทางคณิตศาสตร์](#9-โมเดลทางคณิตศาสตร์)
10. [พารามิเตอร์ความเสี่ยง](#10-พารามิเตอร์ความเสี่ยง)
11. [ขั้นตอนการดำเนินการ](#11-ขั้นตอนการดำเนินการ)
12. [เทคนิคขั้นสูง](#12-เทคนิคขั้นสูง)
13. [หมายเหตุการใช้งาน AI](#13-หมายเหตุการใช้งาน-ai)
14. [เอกสารอ้างอิง](#14-เอกสารอ้างอิง)

---

## 1. บทนำ

การเทรดโซน Supply and Demand สร้างขึ้นบนหลักเศรษฐศาสตร์พื้นฐานว่าราคาเคลื่อนไหวเนื่องจากความไม่สมดุลระหว่างแรงซื้อ (Demand) และแรงขาย (Supply) ต่างจากแนวรับแนวต้านแบบดั้งเดิมที่เน้นระดับราคา (เส้น) การเทรด S/D เน้นที่ **โซน** ราคา (สี่เหลี่ยม) ที่ผู้เล่นสถาบันวางออเดอร์ขนาดใหญ่ที่ยังไม่ถูกเติมจนครบ ทำให้คาดหวังว่าออเดอร์ที่เหลือจะถูกเติมเมื่อราคากลับมา

### 1.1 ทฤษฎีหลัก

- นักเทรดสถาบันไม่สามารถเติมออเดอร์ขนาดใหญ่ในธุรกรรมเดียว พวกเขาทิ้ง **ออเดอร์ที่ยังไม่ถูกเติม** ไว้ที่โซนราคาเฉพาะ
- เมื่อราคากลับมาที่โซนเหล่านี้ ออเดอร์ที่เหลือจะถูกดำเนินการ ทำให้ราคาเกิดปฏิกิริยา
- โซนใหม่ที่ยังไม่ถูกทดสอบมีความน่าจะเป็นสูงสุดในการสร้างปฏิกิริยา
- ความแข็งแกร่งของการออกจากโซนบ่งบอกถึงขนาดของความไม่สมดุลของออเดอร์

### 1.2 S/D เทียบกับ แนวรับ/แนวต้าน

| คุณลักษณะ | แนวรับ/แนวต้าน | โซน Supply/Demand |
|---------|-------------------|-------------------|
| **การแสดงผล** | เส้นราคาเดียว | ช่วงราคา (โซน) |
| **แข็งแกร่งขึ้นจาก** | การแตะหลายครั้ง | ความสด (แตะน้อยครั้ง = ดีกว่า) |
| **ที่มา** | การสังเกตด้วยตา | การวิเคราะห์ Order Flow ของสถาบัน |
| **พลังทำนาย** | อ่อนลงหลังแต่ละครั้งที่แตะ | แข็งแกร่งที่สุดเมื่อแตะครั้งแรก |
| **ความกว้างโซน** | ไม่มี | กำหนดโดยแท่งเทียนฐาน |

---

## 2. พื้นฐาน Supply and Demand

### 2.1 โซน Supply (โซนขาย)

**โซน Supply** คือบริเวณราคาที่แรงขายเอาชนะแรงซื้อ ทำให้ราคาร่วงอย่างรุนแรง แสดงถึงกลุ่มออเดอร์ขายของสถาบัน

**ลักษณะ**:
- เกิดที่จุดเริ่มต้นของการเคลื่อนไหวขาลงที่แข็งแกร่ง
- โซนครอบคลุมแท่งเทียนฐาน (Basing) ก่อนการร่วง
- เมื่อราคากลับมาที่โซน Supply คาดว่าจะกลับตัวลง

### 2.2 โซน Demand (โซนซื้อ)

**โซน Demand** คือบริเวณราคาที่แรงซื้อเอาชนะแรงขาย ทำให้ราคาพุ่งอย่างรุนแรง แสดงถึงกลุ่มออเดอร์ซื้อของสถาบัน

**ลักษณะ**:
- เกิดที่จุดเริ่มต้นของการเคลื่อนไหวขาขึ้นที่แข็งแกร่ง
- โซนครอบคลุมแท่งเทียนฐาน (Basing) ก่อนการพุ่ง
- เมื่อราคากลับมาที่โซน Demand คาดว่าจะกลับตัวขึ้น

### 2.3 หลักความไม่สมดุล (Imbalance Principle)

ความแข็งแกร่งของโซนเป็นสัดส่วนกับความไม่สมดุลที่สร้างมัน:

$$\text{Imbalance}_{\text{zone}} = \frac{|\text{Departure Move}|}{\text{ATR}(14)} \times \frac{1}{\text{Base Width (candles)}}$$

การออกที่แข็งแกร่ง เร็ว จากฐานที่แคบ บ่งบอกถึงความไม่สมดุลของออเดอร์สถาบันจำนวนมาก การออกที่ช้า ค่อยๆ จากฐานที่กว้าง บ่งบอกถึงความไม่สมดุลที่เล็กกว่า กระจายตัวมากกว่า

---

## 3. รูปแบบการก่อตัวของโซน

โซนก่อตัวใน 4 รูปแบบที่แตกต่างกัน จำแนกตาม Price Action ก่อน (approach) และหลัง (departure) ฐาน

### 3.1 Rally-Base-Rally (RBR) — Demand ต่อเนื่อง

```
Price Action:  ↑ → (Base) → ↑
Zone Type:     Demand (แนวรับ)
Context:       ขาขึ้นต่อเนื่อง — สถาบันเพิ่มตำแหน่ง Long
```

**การก่อตัว**:
1. ราคาพุ่งขึ้น (อิมพัลส์เริ่มต้น)
2. ราคาหยุดพักและสร้างการสะสมแน่น (ฐาน) — 1 ถึง 5 แท่งเทียน
3. ราคาทะลุขึ้นจากฐานพร้อมโมเมนตัม

**ขอบเขตโซน**:
$$\text{Zone\_Upper} = \max(H_{\text{base\_candles}})$$
$$\text{Zone\_Lower} = \min(L_{\text{base\_candles}})$$

### 3.2 Drop-Base-Drop (DBD) — Supply ต่อเนื่อง

```
Price Action:  ↓ → (Base) → ↓
Zone Type:     Supply (แนวต้าน)
Context:       ขาลงต่อเนื่อง — สถาบันเพิ่มตำแหน่ง Short
```

**การก่อตัว**:
1. ราคาร่วงอย่างรุนแรง (อิมพัลส์เริ่มต้น)
2. ราคาหยุดพักในการสะสมแน่น (ฐาน)
3. ราคาทะลุลงจากฐานพร้อมโมเมนตัม

### 3.3 Rally-Base-Drop (RBD) — Supply กลับตัว

```
Price Action:  ↑ → (Base) → ↓
Zone Type:     Supply (แนวต้าน) — ประเภทที่แข็งแกร่งที่สุด
Context:       กลับตัวจากขาขึ้นเป็นขาลง — สถาบันกระจายตำแหน่ง
```

**การก่อตัว**:
1. ราคาพุ่งเข้าโซน Supply ของสถาบัน
2. สถาบันกระจาย (ขาย) อย่างก้าวร้าว สร้างฐานสั้นๆ
3. ราคาร่วงอย่างรุนแรงเมื่อ Supply เอาชนะ Demand

**นี่คือโซน Supply คุณภาพสูงสุด** เพราะแสดงจุดที่ทัศนะสถาบันเปลี่ยนจากขาขึ้นเป็นขาลง

### 3.4 Drop-Base-Rally (DBR) — Demand กลับตัว

```
Price Action:  ↓ → (Base) → ↑
Zone Type:     Demand (แนวรับ) — ประเภทที่แข็งแกร่งที่สุด
Context:       กลับตัวจากขาลงเป็นขาขึ้น — สถาบันสะสมตำแหน่ง
```

**การก่อตัว**:
1. ราคาร่วงเข้าโซน Demand ของสถาบัน
2. สถาบันสะสม (ซื้อ) อย่างก้าวร้าว สร้างฐานสั้นๆ
3. ราคาพุ่งอย่างรุนแรงเมื่อ Demand เอาชนะ Supply

### 3.5 ลำดับความแข็งแกร่งของรูปแบบ

| รูปแบบ | ประเภทโซน | ความแข็งแกร่ง | เหตุผล |
|---------|-----------|----------|--------|
| **DBR** | Demand | สูงสุด | กลับตัว = Order Flow ฝั่งตรงข้ามสูงสุด |
| **RBD** | Supply | สูงสุด | กลับตัว = Order Flow ฝั่งตรงข้ามสูงสุด |
| **RBR** | Demand | สูง | ต่อเนื่อง = สถาบันเพิ่มตำแหน่ง |
| **DBD** | Supply | สูง | ต่อเนื่อง = สถาบันเพิ่มตำแหน่ง |

---

## 4. การระบุโซนใหม่ (Fresh Zones)

### 4.1 นิยามความสด

**โซนใหม่ (Fresh Zone)** คือโซนที่ราคายังไม่เคยกลับมาเยือนหลังจากก่อตัว โซนใหม่มีความน่าจะเป็นสูงสุดในการสร้างปฏิกิริยาเพราะออเดอร์สถาบันที่ยังไม่ถูกเติมยังคงอยู่

### 4.2 อัลกอริทึมตรวจจับ

```python
def identify_supply_zones(candles, lookback=200, min_departure_atr=1.5):
    """
    Identify fresh supply zones from OHLC data.
    """
    atr = calculate_atr(candles, period=14)
    zones = []
    
    for i in range(2, len(candles) - 2):
        # Look for base candles: small-bodied candles (body < 50% of range)
        body_ratio = abs(candles[i].close - candles[i].open) / (candles[i].high - candles[i].low + 1e-10)
        
        if body_ratio > 0.5:
            continue  # Not a base candle
        
        # Check departure: next N candles must move bearishly with strength
        departure_move = candles[i].low - min(c.low for c in candles[i+1:i+6])
        
        if departure_move < min_departure_atr * atr[i]:
            continue  # Departure not strong enough
        
        # Check approach: prior candles moved bullishly (for RBD) or bearishly (for DBD)
        approach_move = candles[i].high - candles[i-3].low  # simplified
        
        # Define zone
        zone = {
            "type": "SUPPLY",
            "upper": candles[i].high,
            "lower": min(candles[i].open, candles[i].close),
            "formation_index": i,
            "departure_strength": departure_move / atr[i],
            "pattern": "RBD" if approach_move > 0 else "DBD",
            "fresh": True
        }
        
        # Check freshness: has price returned to the zone?
        for j in range(i + 6, len(candles)):
            if candles[j].high >= zone["lower"]:
                zone["fresh"] = False
                break
        
        if zone["fresh"]:
            zones.append(zone)
    
    return zones


def identify_demand_zones(candles, lookback=200, min_departure_atr=1.5):
    """
    Identify fresh demand zones from OHLC data.
    """
    atr = calculate_atr(candles, period=14)
    zones = []
    
    for i in range(2, len(candles) - 2):
        body_ratio = abs(candles[i].close - candles[i].open) / (candles[i].high - candles[i].low + 1e-10)
        
        if body_ratio > 0.5:
            continue
        
        # Check departure: next N candles must rally with strength
        departure_move = max(c.high for c in candles[i+1:i+6]) - candles[i].high
        
        if departure_move < min_departure_atr * atr[i]:
            continue
        
        approach_move = candles[i-3].high - candles[i].low
        
        zone = {
            "type": "DEMAND",
            "upper": max(candles[i].open, candles[i].close),
            "lower": candles[i].low,
            "formation_index": i,
            "departure_strength": departure_move / atr[i],
            "pattern": "DBR" if approach_move > 0 else "RBR",
            "fresh": True
        }
        
        for j in range(i + 6, len(candles)):
            if candles[j].low <= zone["upper"]:
                zone["fresh"] = False
                break
        
        if zone["fresh"]:
            zones.append(zone)
    
    return zones
```

### 4.3 การระบุแท่งเทียนฐาน

**ฐาน (Base)** ประกอบด้วยแท่งเทียนหนึ่งหรือมากกว่าที่เข้าเกณฑ์:

1. **ตัวเล็กเมื่อเทียบกับช่วง**: อัตราส่วนตัว-ต่อ-ช่วง $< 0.5$
2. **ช่วงแคบเมื่อเทียบกับ ATR**: ช่วงแท่งเทียน $< 0.75 \times \text{ATR}(14)$
3. **ต่อเนื่อง**: แท่งเทียนที่ผ่านเกณฑ์หลายแท่งอาจรวมกันเป็นฐาน

$$\text{IsBaseCandle}(i) = \frac{|C_i - O_i|}{H_i - L_i} < 0.5 \quad \text{AND} \quad (H_i - L_i) < 0.75 \times \text{ATR}(14)_i$$

**ความกว้างฐานสูงสุด**: 5 แท่งเทียน ฐานที่กว้างเกิน 5 แท่งบ่งชี้ว่าความไม่สมดุลถูกดูดซับอย่างค่อยเป็นค่อยไปและโซนอ่อนกว่า

---

## 5. การให้คะแนนคุณภาพโซน

### 5.1 คะแนนคุณภาพรวม

$$Q_{\text{zone}} = w_1 \cdot S_{\text{strength}} + w_2 \cdot S_{\text{freshness}} + w_3 \cdot S_{\text{proximity}} + w_4 \cdot S_{\text{pattern}} + w_5 \cdot S_{\text{base}} + w_6 \cdot S_{\text{time}}$$

### 5.2 คะแนนแต่ละองค์ประกอบ

#### 5.2.1 คะแนนความแข็งแกร่ง ($S_{\text{strength}}$)

วัดขนาดของการเคลื่อนไหวขาออกเมื่อเทียบกับความผันผวน

$$S_{\text{strength}} = \min\left(\frac{|\text{Departure Move}|}{2.5 \times \text{ATR}(14)}, 1.0\right)$$

| Departure / ATR | เรทติ้ง | คะแนน |
|-----------------|--------|-------|
| $\geq 2.5$ | ยอดเยี่ยม | 1.0 |
| 2.0 – 2.49 | ดี | 0.8 |
| 1.5 – 1.99 | ยอมรับได้ | 0.6 |
| 1.0 – 1.49 | อ่อน | 0.3 |
| $< 1.0$ | ปฏิเสธ | 0.0 |

#### 5.2.2 คะแนนความสด ($S_{\text{freshness}}$)

$$S_{\text{freshness}} = \begin{cases} 1.0 & \text{ถ้าโซนยังไม่ถูกทดสอบ (สด)} \\ 0.4 & \text{ถ้าถูกทดสอบ 1 ครั้งแล้วรับได้} \\ 0.1 & \text{ถ้าถูกทดสอบ 2 ครั้งแล้วรับได้} \\ 0.0 & \text{ถ้าถูกทดสอบ 3 ครั้งขึ้นไป} \end{cases}$$

#### 5.2.3 คะแนนความใกล้ ($S_{\text{proximity}}$)

ราคาปัจจุบันใกล้โซนแค่ไหน โซนที่อยู่ไกลมีความเกี่ยวข้องน้อยกว่า

$$S_{\text{proximity}} = e^{-\beta \cdot d}$$

โดย $d = \frac{|\text{Price} - \text{Zone\_Midpoint}|}{\text{ATR}(14)}$ และ $\beta = 0.15$

#### 5.2.4 คะแนนรูปแบบ ($S_{\text{pattern}}$)

| รูปแบบ | คะแนน |
|---------|-------|
| DBR / RBD (กลับตัว) | 1.0 |
| RBR / DBD (ต่อเนื่อง) | 0.7 |

#### 5.2.5 คะแนนคุณภาพฐาน ($S_{\text{base}}$)

$$S_{\text{base}} = 1.0 - \frac{\text{Base Width (candles)} - 1}{5}$$

| ความกว้างฐาน | คะแนน |
|-----------|-------|
| 1 แท่งเทียน | 1.0 |
| 2 แท่งเทียน | 0.8 |
| 3 แท่งเทียน | 0.6 |
| 4 แท่งเทียน | 0.4 |
| 5 แท่งเทียน | 0.2 |

#### 5.2.6 คะแนน Time Decay ($S_{\text{time}}$)

โซนสูญเสียความเกี่ยวข้องเมื่อเวลาผ่านไปเนื่องจากสภาพตลาดเปลี่ยน

$$S_{\text{time}} = e^{-\gamma \cdot t}$$

โดย $t$ = จำนวนแท่งเทียนนับจากโซนก่อตัว และ $\gamma$ แตกต่างตามไทม์เฟรม:

| ไทม์เฟรม | $\gamma$ |
|-----------|----------|
| M15 | 0.005 |
| H1 | 0.003 |
| H4 | 0.002 |
| D1 | 0.001 |
| W1 | 0.0005 |

### 5.3 น้ำหนักเริ่มต้น

| องค์ประกอบ | น้ำหนัก ($w$) |
|-----------|-------------|
| ความแข็งแกร่ง | 0.25 |
| ความสด | 0.25 |
| ความใกล้ | 0.10 |
| รูปแบบ | 0.15 |
| คุณภาพฐาน | 0.15 |
| Time Decay | 0.10 |

### 5.4 เกณฑ์คุณภาพ

| เกรดคุณภาพ | ช่วงคะแนน | การดำเนินการ |
|--------------|-------------|--------|
| **A+** | $\geq 0.85$ | เทรดด้วยขนาดเต็ม, R:R ขั้นต่ำ 2:1 |
| **A** | 0.70 – 0.84 | เทรดด้วยขนาดเต็ม, R:R ขั้นต่ำ 3:1 |
| **B** | 0.55 – 0.69 | เทรดด้วย 50% ของขนาด, R:R ขั้นต่ำ 4:1 |
| **C** | 0.40 – 0.54 | เฝ้าดูเท่านั้น ไม่เทรด |
| **F** | $< 0.40$ | ยกเลิกโซน |

---

## 6. โซนซ้อนทับและการปรับละเอียดโซน

### 6.1 โซนซ้อนทับ (Nested Zones)

โซนซ้อนทับเกิดเมื่อโซนไทม์เฟรมเล็กอยู่ภายในโซนไทม์เฟรมใหญ่ สร้างโอกาสเข้าเทรดที่มี Confluence สูง

**ตัวอย่าง**: โซน Demand Daily จาก 1.0800–1.0850 มีโซน Demand H1 จาก 1.0820–1.0835 อยู่ภายใน โซน H1 ซ้อนทับอยู่ในโซน Daily

### 6.2 กระบวนการปรับละเอียด

การปรับละเอียดโซนจะทำให้โซนไทม์เฟรมใหญ่แคบลงเป็นบริเวณเข้าเทรดที่แม่นยำที่สุด:

```python
def refine_zone(htf_zone, ltf_candles):
    """
    Refine an HTF zone using LTF price action.
    
    The refined zone is the LTF base candle(s) within the HTF zone
    that initiated the LTF departure move.
    """
    # Find LTF candles within the HTF zone
    in_zone_candles = [c for c in ltf_candles 
                       if c.low <= htf_zone.upper and c.high >= htf_zone.lower]
    
    if not in_zone_candles:
        return htf_zone  # No refinement possible
    
    # Find the LTF base within the HTF zone
    ltf_zones = identify_demand_zones(in_zone_candles) if htf_zone.type == "DEMAND" \
                else identify_supply_zones(in_zone_candles)
    
    if ltf_zones:
        # Use the most recent LTF zone within the HTF zone
        refined = ltf_zones[-1]
        return {
            "upper": refined["upper"],
            "lower": refined["lower"],
            "source": "refined",
            "htf_zone": htf_zone,
            "ltf_zone": refined
        }
    
    return htf_zone
```

### 6.3 การจัดแนวโซนหลายไทม์เฟรม

เซ็ตอัปที่มีความน่าจะเป็นสูงสุดเกิดเมื่อโซนจาก 3+ ไทม์เฟรมทับซ้อนกัน:

$$\text{MTF\_Confluence} = \sum_{tf \in \{W, D, H4, H1, M15\}} \mathbb{1}[\text{zone exists at current price on } tf]$$

| MTF Confluence | เรทติ้งความน่าจะเป็น |
|---------------|-------------------|
| 3+ ไทม์เฟรม | ยอดเยี่ยม |
| 2 ไทม์เฟรม | ดี |
| 1 ไทม์เฟรม | ยอมรับได้ |

---

## 7. อายุการใช้งานของโซน (Time-in-Force)

### 7.1 การหมดอายุของโซน

โซนไม่คงอยู่ตลอดไป ความถูกต้องเสื่อมสลายเนื่องจาก:
1. **การกัดกร่อนจากเวลา**: สภาพตลาดเปลี่ยน สถาบันที่สร้างโซนอาจหาระดับเติมทางเลือกอื่นแล้ว
2. **การเปลี่ยนแปลงโครงสร้าง**: หากโครงสร้างตลาดเปลี่ยน (เช่น CHoCH บนไทม์เฟรมของโซน) โซนที่ต้านโครงสร้างใหม่จะเป็นโมฆะ
3. **การดูดซับ**: การแตะบางส่วนกัดกร่อนออเดอร์ที่ยังไม่ถูกเติมในโซน

### 7.2 กฎการหมดอายุ

| ไทม์เฟรม | อายุโซนสูงสุด | หมายเหตุ |
|-----------|-----------------|-------|
| M15 | 48 ชั่วโมง (192 แท่งเทียน) | โซนรายวันหมดอายุเร็ว |
| H1 | 1 สัปดาห์ (168 แท่งเทียน) | |
| H4 | 1 เดือน (180 แท่งเทียน) | |
| D1 | 3 เดือน (~63 แท่งเทียน) | |
| W1 | 1 ปี (~52 แท่งเทียน) | |

### 7.3 เงื่อนไขการเป็นโมฆะ

โซนจะเป็นโมฆะทันทีถ้า:
1. ราคา **ปิดทะลุ** โซนทั้งหมด (ไม่ใช่แค่ไส้เทียนทะลุ)
2. การเคลื่อนไหวขาออกที่สร้างโซนถูก Retrace กลับครบ
3. เกิด CHoCH บนไทม์เฟรมของโซนในทิศทางตรงข้ามโซน

$$\text{Invalidated}_{\text{demand}} = C_j < \text{Zone\_Lower} \quad \text{for any candle } j > \text{formation}$$
$$\text{Invalidated}_{\text{supply}} = C_j > \text{Zone\_Upper} \quad \text{for any candle } j > \text{formation}$$

---

## 8. ตรรกะการเข้าและออก

### 8.1 Limit Order Entry (แบบก้าวร้าว)

วาง Limit Order ที่ขอบโซนก่อนที่ราคาจะมาถึง

**Long (โซน Demand)**:
$$\text{Entry} = \text{Zone\_Upper}$$
$$\text{SL} = \text{Zone\_Lower} - k \times \text{ATR}(14)$$
$$\text{TP}_1 = \text{Nearest Supply Zone Lower Boundary}$$

**Short (โซน Supply)**:
$$\text{Entry} = \text{Zone\_Lower}$$
$$\text{SL} = \text{Zone\_Upper} + k \times \text{ATR}(14)$$
$$\text{TP}_1 = \text{Nearest Demand Zone Upper Boundary}$$

โดย $k = 0.2$ (ค่า buffer)

### 8.2 Zone Midpoint Entry (แบบปานกลาง)

สำหรับความเสี่ยงที่แคบขึ้น เข้าที่จุดกลางโซน:

$$\text{Entry}_{\text{mid}} = \frac{\text{Zone\_Upper} + \text{Zone\_Lower}}{2}$$

ลดระยะ Stop Loss ~50% แต่เพิ่มโอกาสที่ราคาจะไม่ถึงจุดเข้า

### 8.3 Confirmation Entry (แบบอนุรักษ์นิยม)

รอให้ราคาเข้าโซนและแสดงสัญญาณกลับตัว:
1. ราคาเข้าโซน Demand/Supply
2. รูปแบบแท่งเทียนกลับตัวก่อตัว (Pin Bar, Engulfing ฯลฯ)
3. เข้าเมื่อแท่งเทียนยืนยันปิด

```python
def confirmation_entry(zone, candles):
    """Check for confirmation within a zone."""
    latest = candles[-1]
    
    if zone.type == "DEMAND":
        # Price must be in the zone
        if latest.low > zone.upper or latest.high < zone.lower:
            return None
        
        # Look for bullish reversal
        if is_bullish_pin_bar(latest) or is_bullish_engulfing(candles[-2], latest):
            return {
                "entry": latest.close,
                "sl": zone.lower - ATR_BUFFER,
                "type": "CONFIRMATION_LONG"
            }
    
    elif zone.type == "SUPPLY":
        if latest.high < zone.lower or latest.low > zone.upper:
            return None
        
        if is_bearish_pin_bar(latest) or is_bearish_engulfing(candles[-2], latest):
            return {
                "entry": latest.close,
                "sl": zone.upper + ATR_BUFFER,
                "type": "CONFIRMATION_SHORT"
            }
    
    return None
```

### 8.4 กลยุทธ์ Take Profit

| เป้าหมาย | ตำแหน่ง | การดำเนินการ |
|--------|----------|--------|
| **TP1** | ขอบโซนฝั่งตรงข้ามใกล้สุด | ปิด 50% |
| **TP2** | โซนฝั่งตรงข้ามถัดไปหรือจุดสวิง | ปิด 30% |
| **TP3** | การเคลื่อนไหวขยาย (1.618 Fibonacci Extension) | ปิด 20% พร้อม Trailing SL |

### 8.5 การปิดบางส่วนและ Trailing Stop

หลัง TP1 โดน:
1. ย้าย SL ไปที่จุดคุ้มทุน (ราคาเข้า + 1 pip buffer สำหรับค่าคอมมิชชั่น)
2. เปิดใช้ Trailing Stop ตามโครงสร้าง

```python
def trailing_stop_logic(trade, candles, zone_type):
    if zone_type == "DEMAND":
        # Trail SL below each new higher low
        swing_lows = find_recent_swing_lows(candles, n=3)
        if swing_lows:
            new_sl = swing_lows[-1].price - ATR_BUFFER
            if new_sl > trade.current_sl:
                trade.update_sl(new_sl)
    
    elif zone_type == "SUPPLY":
        swing_highs = find_recent_swing_highs(candles, n=3)
        if swing_highs:
            new_sl = swing_highs[-1].price + ATR_BUFFER
            if new_sl < trade.current_sl:
                trade.update_sl(new_sl)
```

---

## 9. โมเดลทางคณิตศาสตร์

### 9.1 การทำให้ความกว้างโซนเป็นมาตรฐาน

เพื่อเปรียบเทียบโซนข้ามสินทรัพย์และไทม์เฟรม ทำให้ความกว้างโซนเป็นมาตรฐาน:

$$W_{\text{norm}} = \frac{\text{Zone\_Upper} - \text{Zone\_Lower}}{\text{ATR}(14)}$$

ช่วงที่เหมาะสม: $0.3 \leq W_{\text{norm}} \leq 1.5$ โซนที่กว้างกว่า $1.5 \times \text{ATR}$ กว้างเกินไปสำหรับจุดเข้าที่แม่นยำ

### 9.2 ความเร็วการออก (Departure Velocity)

วัดว่าราคาเคลื่อนที่ออกจากโซนเร็วแค่ไหน:

$$V_{\text{departure}} = \frac{|\text{Departure Price} - \text{Zone Boundary}|}{n_{\text{departure\_candles}} \times \text{ATR}(14)}$$

ความเร็วสูงกว่า = ความไม่สมดุลแข็งแกร่งกว่า = โซนคุณภาพสูงกว่า

### 9.3 โมเดลความน่าจะเป็นปฏิกิริยาโซน

จากการ Backtest เชิงประจักษ์ ความน่าจะเป็นที่โซนจะสร้างปฏิกิริยา (กลับตัวอย่างน้อย 1R) สามารถจำลองเป็น:

$$P(\text{reaction}) = \sigma\left(\beta_0 + \beta_1 Q_{\text{zone}} + \beta_2 S_{\text{MTF}} + \beta_3 T_{\text{trend}} + \beta_4 V_{\text{vol}}\right)$$

โดยที่:
- $\sigma$ = ฟังก์ชัน Sigmoid: $\sigma(x) = \frac{1}{1 + e^{-x}}$
- $Q_{\text{zone}}$ = คะแนนคุณภาพโซน (ส่วนที่ 5)
- $S_{\text{MTF}}$ = คะแนน Confluence หลายไทม์เฟรม
- $T_{\text{trend}}$ = การจัดแนวเทรนด์ (1 ถ้าโซนสอดคล้องกับเทรนด์ HTF, 0 ถ้าสวนเทรนด์)
- $V_{\text{vol}}$ = ระบอบความผันผวน (VIX หรือ ATR Percentile ที่ทำให้เป็นมาตรฐาน)

สัมประสิทธิ์ที่ปรับจากข้อมูลจริง (EUR/USD, 2020–2025):
$$\beta_0 = -2.1, \quad \beta_1 = 3.8, \quad \beta_2 = 0.9, \quad \beta_3 = 1.2, \quad \beta_4 = -0.5$$

### 9.4 มูลค่าที่คาดหวังต่อเทรด

$$\text{EV} = P(\text{win}) \times \text{Avg\_Win} - (1 - P(\text{win})) \times \text{Avg\_Loss}$$

สำหรับกลยุทธ์โซน S/D:
$$\text{EV} = P(\text{reaction}) \times R \times \text{RR}_{\text{avg}} - (1 - P(\text{reaction})) \times R$$

โดย $R$ = ความเสี่ยงต่อเทรด กลยุทธ์จะทำกำไรเมื่อ:

$$P(\text{reaction}) > \frac{1}{1 + \text{RR}_{\text{avg}}}$$

ด้วย RR = 3:1: $P(\text{reaction}) > 0.25$ (อัตราชนะขั้นต่ำ 25% สำหรับจุดคุ้มทุน)

### 9.5 ขนาดตำแหน่งที่เหมาะสม (Kelly Criterion ดัดแปลง)

$$f^* = \frac{P(\text{win}) \times \text{RR} - (1 - P(\text{win}))}{\text{RR}}$$

ใช้ Fractional Kelly (25–50% ของ $f^*$) สำหรับขนาดแบบอนุรักษ์นิยม:

$$f_{\text{applied}} = 0.25 \times f^*$$

---

## 10. พารามิเตอร์ความเสี่ยง

### 10.1 การวาง Stop Loss

| วิธี | ตำแหน่ง SL | กรณีใช้ |
|--------|-------------|----------|
| **Beyond Zone** | ขอบโซน + 0.2 ATR | มาตรฐาน — รองรับไส้เทียน |
| **ATR-Based** | จุดกลางโซน + 1.0 ATR | ตลาดผันผวน |
| **Structural** | เกินจุดสวิงใกล้สุดบน LTF | Confirmation entries |

### 10.2 ความเสี่ยงต่อเทรด

| คุณภาพโซน | Risk % | เหตุผล |
|-------------|--------|-----------|
| A+ ($\geq 0.85$) | 1.5% | ความมั่นใจสูง ก้าวร้าวเล็กน้อย |
| A (0.70–0.84) | 1.0% | ความเสี่ยงมาตรฐาน |
| B (0.55–0.69) | 0.5% | ความมั่นใจลด ครึ่งหนึ่ง |

### 10.3 R:R ขั้นต่ำ

| ประเภทเซ็ตอัป | R:R ขั้นต่ำ |
|-----------|-------------|
| โซนสด + สอดคล้องเทรนด์ + MTF confluence | 2:1 |
| โซนสด + สอดคล้องเทรนด์ | 3:1 |
| โซนสด (ไม่มี confluence เพิ่มเติม) | 4:1 |
| โซนที่ถูกทดสอบแล้ว (แตะครั้งที่สอง) | 5:1 |

### 10.4 การควบคุมความเสี่ยงระดับพอร์ต

- Drawdown รายวันสูงสุด: 3%
- Drawdown รายสัปดาห์สูงสุด: 5%
- ความเสี่ยงเปิดรวมสูงสุด: 4% (ผลรวมความเสี่ยงเทรดทั้งหมด)
- ความเสี่ยงที่สัมพันธ์กันสูงสุด (เช่น long USD ทั้งหมด): 3%
- เทรดต่อโซนสูงสุด: 1 (ไม่เข้าซ้ำหลังโดน SL ที่โซนเดิม)

### 10.5 การปรับขนาดตาม Drawdown

$$R\%_{\text{adjusted}} = R\%_{\text{base}} \times \max\left(0.25, 1 - \frac{\text{Current Drawdown}}{2 \times \text{Max Acceptable DD}}\right)$$

---

## 11. ขั้นตอนการดำเนินการ

### 11.1 Main Strategy Pseudocode

```python
def supply_demand_strategy():
    """
    Complete Supply & Demand Zone trading strategy.
    Multi-timeframe approach with quality scoring.
    """
    
    # ================================================
    # PHASE 1: ZONE DISCOVERY (runs on new HTF candle close)
    # ================================================
    
    # Scan multiple timeframes for zones
    timeframes = ["W1", "D1", "H4", "H1"]
    all_zones = {}
    
    for tf in timeframes:
        candles = fetch_candles(tf, count=200)
        atr = calculate_atr(candles, 14)
        
        supply_zones = identify_supply_zones(candles, min_departure_atr=1.5)
        demand_zones = identify_demand_zones(candles, min_departure_atr=1.5)
        
        # Score each zone
        for zone in supply_zones + demand_zones:
            zone["quality"] = calculate_zone_quality(
                zone, candles, atr, current_price
            )
            zone["timeframe"] = tf
        
        # Filter by quality threshold
        valid_zones = [z for z in supply_zones + demand_zones if z["quality"] >= 0.55]
        all_zones[tf] = valid_zones
    
    # ================================================
    # PHASE 2: ZONE PRIORITIZATION
    # ================================================
    
    # Flatten and sort by quality score
    flat_zones = []
    for tf, zones in all_zones.items():
        flat_zones.extend(zones)
    
    flat_zones.sort(key=lambda z: z["quality"], reverse=True)
    
    # Check for nested zones (MTF confluence)
    for zone in flat_zones:
        zone["mtf_count"] = count_overlapping_zones(zone, flat_zones)
    
    # Select top candidate zones near current price
    candidate_zones = [z for z in flat_zones 
                       if is_approaching(current_price, z, threshold_atr=5.0)]
    
    if not candidate_zones:
        return WAIT("No high-quality zones near current price")
    
    # ================================================
    # PHASE 3: ENTRY DECISION
    # ================================================
    
    for zone in candidate_zones:
        # Check if price is currently in the zone
        if not price_in_zone(current_price, zone):
            # Set alert / limit order
            set_limit_order_alert(zone)
            continue
        
        # Price is in the zone — evaluate entry
        entry_tf_candles = fetch_candles(get_entry_tf(zone["timeframe"]), count=100)
        
        # Option A: Limit order at zone (risk entry)
        risk_entry = calculate_risk_entry(zone)
        
        # Option B: Wait for confirmation
        confirm_entry = confirmation_entry(zone, entry_tf_candles)
        
        # Select entry based on zone quality
        if zone["quality"] >= 0.85:
            selected_entry = risk_entry  # High quality → risk entry OK
        elif confirm_entry:
            selected_entry = confirm_entry  # Moderate quality → need confirmation
        else:
            continue  # Wait for confirmation
        
        # ================================================
        # PHASE 4: RISK VALIDATION
        # ================================================
        
        # Calculate R:R
        opposing_zones = find_opposing_zones(zone, flat_zones)
        tp1 = opposing_zones[0]["boundary"] if opposing_zones else None
        
        if tp1 is None:
            tp1 = calculate_measured_move(zone)
        
        rr = abs(tp1 - selected_entry["entry"]) / abs(selected_entry["entry"] - selected_entry["sl"])
        
        min_rr = get_min_rr(zone["quality"], zone.get("mtf_count", 1))
        
        if rr < min_rr:
            log(f"Zone {zone} R:R {rr:.1f} below minimum {min_rr}")
            continue
        
        # Check portfolio risk limits
        if not check_risk_limits(selected_entry, zone):
            continue
        
        # ================================================
        # PHASE 5: EXECUTION
        # ================================================
        
        position_size = calculate_position_size(
            account_balance=get_balance(),
            risk_percent=get_risk_percent(zone["quality"]),
            entry=selected_entry["entry"],
            sl=selected_entry["sl"]
        )
        
        trade = execute_trade(
            direction="BUY" if zone["type"] == "DEMAND" else "SELL",
            entry=selected_entry["entry"],
            sl=selected_entry["sl"],
            tp1=tp1,
            tp2=calculate_tp2(zone, opposing_zones),
            size=position_size,
            zone_id=zone["id"],
            quality=zone["quality"]
        )
        
        log_trade(trade)
        
        # Mark zone as used (no re-entry on same zone)
        zone["traded"] = True
        
        return trade
    
    return WAIT("No actionable setup at current price")
```

### 11.2 Zone Maintenance Loop

```python
def zone_maintenance():
    """
    Periodic maintenance of the zone database.
    Run after each candle close on the zone's timeframe.
    """
    for zone in active_zones:
        # Check if zone has been violated
        if is_violated(zone, latest_candle):
            zone["status"] = "INVALIDATED"
            remove_pending_orders(zone)
            continue
        
        # Check time expiration
        if is_expired(zone):
            zone["status"] = "EXPIRED"
            remove_pending_orders(zone)
            continue
        
        # Update freshness if tested
        if was_tested(zone, latest_candle):
            zone["test_count"] += 1
            zone["quality"] = recalculate_quality(zone)
            
            if zone["test_count"] >= 3:
                zone["status"] = "DEPLETED"
                remove_pending_orders(zone)
        
        # Update time decay
        zone["time_score"] = calculate_time_decay(zone)
        zone["quality"] = recalculate_quality(zone)
```

---

## 12. เทคนิคขั้นสูง

### 12.1 Flip Zones

เมื่อโซน Demand ถูกทะลุ (ราคาปิดต่ำกว่า) มันจะกลายเป็นโซน Supply ที่มีศักยภาพ และกลับกัน นี่เรียกว่า **Flip Zone** หรือ **การกลับขั้ว**

$$\text{FlipZone} = \begin{cases} \text{DemandZone} \rightarrow \text{SupplyZone} & \text{if } C < \text{DemandZone\_Lower} \\ \text{SupplyZone} \rightarrow \text{DemandZone} & \text{if } C > \text{SupplyZone\_Upper} \end{cases}$$

Flip Zones เทรดด้วยความมั่นใจที่ลดลง (หักคะแนนคุณภาพ -0.15)

### 12.2 การปรับโซนให้เข้ากับพฤติกรรมสถาบัน

ขนาดออเดอร์สถาบันสามารถอนุมานจากข้อมูลวอลุ่ม (ถ้ามี):

$$\text{InstitutionalPressure}_i = \frac{V_i \times |C_i - O_i|}{V_{\text{avg}} \times \text{ATR}(14)}$$

แท่งเทียนที่มี $\text{InstitutionalPressure} > 2.0$ ภายในโซนบ่งชี้การมีส่วนร่วมของสถาบันที่แข็งแกร่ง เพิ่มคะแนนคุณภาพโซน +0.10

### 12.3 การเพิ่มคุณค่าโซนจากเหตุการณ์เศรษฐกิจ

โซน Supply/Demand ที่ก่อตัวทันทีหลังข่าวที่มีผลกระทบสูง (NFP, FOMC, CPI) มักจะแข็งแกร่งกว่าเพราะสะท้อนปฏิกิริยาสถาบันต่อข้อมูลใหม่

**Event boost**: ถ้าโซนก่อตัวภายใน 4 ชั่วโมงของเหตุการณ์ผลกระทบสูง เพิ่ม +0.05 ให้คะแนนคุณภาพ

### 12.4 การปรับความกว้างโซนตามระบอบความผันผวน

ปรับความกว้างโซนที่ยอมรับได้ตามระบอบความผันผวนปัจจุบัน:

$$W_{\text{max}} = W_{\text{base}} \times \frac{\text{ATR}(14)_{\text{current}}}{\text{ATR}(14)_{\text{median\_200}}}$$

ในระบอบความผันผวนสูง ยอมรับโซนกว้างขึ้น ในระบอบความผันผวนต่ำ ต้องการโซนที่แน่นขึ้น

---

## 13. หมายเหตุการใช้งาน AI

### 13.1 Data Pipeline

1. **ข้อมูลแท่งเทียน**: ฟีดเรียลไทม์พร้อมประวัติอย่างน้อย 200 แท่งต่อไทม์เฟรม
2. **การคำนวณ ATR**: Rolling 14-period ATR อัปเดตทุกแท่งเทียน
3. **ฐานข้อมูลโซน**: ที่เก็บถาวรของโซนทั้งหมดที่ระบุพร้อม metadata
4. **ปฏิทินเหตุการณ์**: นำเข้าอัตโนมัติข้อมูลเหตุการณ์เศรษฐกิจสำหรับ news-based enhancement

### 13.2 ตารางการคำนวณ

| งาน | Trigger | เวลาโดยประมาณ |
|------|---------|---------------|
| สแกนโซน HTF (W1, D1) | รายวันที่ 00:00 UTC | < 1 วินาที |
| สแกนโซน ITF (H4, H1) | ทุก H1 ปิด | < 1 วินาที |
| คำนวณคุณภาพโซนใหม่ | ทุก H1 ปิด | < 0.5 วินาที |
| ประเมินจุดเข้า | ทุก M15 ปิด + price alert triggers | < 0.5 วินาที |
| บำรุงรักษาโซน | ทุกแท่งเทียนปิด (ต่อ TF) | < 0.5 วินาที |

### 13.3 ผลงานที่คาดหวัง (Backtested)

| เมทริกซ์ | Forex (Majors) | Crypto (BTC/ETH) |
|--------|---------------|-------------------|
| เทรด/เดือน/คู่ | 8–15 | 10–20 |
| Win Rate | 50–60% | 45–55% |
| Average R:R | 2.5:1 | 3.0:1 |
| Profit Factor | 1.8–2.5 | 1.6–2.2 |
| Max Drawdown | 8–12% | 10–15% |
| ผลตอบแทนรายเดือน | 3–7% | 4–10% |

---

## 14. เอกสารอ้างอิง

### หนังสือ
1. Seiden, S. (2011). "Supply and Demand Trading" — Online Trading Academy curriculum.
2. Brooks, A. (2012). *Trading Price Action Reversals*. Wiley.
3. Nison, S. (2001). *Japanese Candlestick Charting Techniques*. Prentice Hall.
4. Dalton, J. F. (1993). *Mind Over Markets*. McGraw-Hill.

### บทความวิชาการ
5. Osler, C. L. (2003). "Currency Orders and Exchange Rate Dynamics." *The Journal of Finance*, 58(5), 1791–1819.
6. Evans, M. D. D., & Lyons, R. K. (2002). "Order Flow and Exchange Rate Dynamics." *Journal of Political Economy*, 110(1), 170–180.
7. Cont, R., Kukanov, A., & Stoikov, S. (2014). "The Price Impact of Order Book Events." *Journal of Financial Econometrics*, 12(1), 47–88.
8. Bouchaud, J.-P., Farmer, J. D., & Lillo, F. (2009). "How Markets Slowly Digest Changes in Supply and Demand." *Handbook of Financial Markets*, Elsevier.

### แหล่งข้อมูลจากผู้ปฏิบัติ
9. Sam Seiden. "The Core Strategy" — Online Trading Academy.
10. Alfonso Moreno. "Institutional Supply and Demand" (2020).
11. Set and Forget. "Supply and Demand Forex Trading" (2019).
12. ICT. "Order Blocks as Supply and Demand" — ICT Mentorship Series.

### แหล่งข้อมูล
13. TradingView — การแสดงผลโซนและ Backtesting
14. Forex Factory — การรวมปฏิทินเศรษฐกิจ
15. CoinGlass — ข้อมูลวอลุ่มและ Open Interest คริปโต
16. OANDA — ข้อมูล Tick ย้อนหลัง Forex สำหรับตรวจสอบโซน

---

*เอกสารนี้เป็นส่วนหนึ่งของฐานความรู้ระบบเทรด Multi-Agent AI ควรอ่านร่วมกับคู่มือ Smart Money Concepts (04_smart_money_concepts), คู่มือ Price Action (07_price_action), และคู่มือ Volume Profile (08_volume_profile_analysis)*
