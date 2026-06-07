# ทฤษฎีคลื่นอีเลียต --- อัลกอริทึมการนับคลื่นอัตโนมัติ

## ข้อมูลเอกสาร
| ฟิลด์ | ค่า |
|---|---|
| **รหัสกลยุทธ์** | EW-004 |
| **หมวดหมู่** | แกนที่ 1 --- กลยุทธ์การเทรด |
| **หมวดย่อย** | ทฤษฎีคลื่นอีเลียต --- อัลกอริทึมการนับคลื่น |
| **ตลาดที่ใช้ได้** | Forex, Crypto |
| **กรอบเวลา** | ทุกกรอบเวลา (Multi-Timeframe) |
| **ระดับความซับซ้อน** | ผู้เชี่ยวชาญ (Expert) |
| **ความเหมาะสมกับ AI** | สำคัญยิ่ง (ส่วนประกอบอัลกอริทึมหลัก) |
| **อัปเดตล่าสุด** | 2026-04-12 |

---

## สารบัญ
1. [บทนำเกี่ยวกับการนับคลื่นอัตโนมัติ](#1-บทนำเกี่ยวกับการนับคลื่นอัตโนมัติ)
2. [อัลกอริทึมการนับคลื่นทีละขั้นตอน](#2-อัลกอริทึมการนับคลื่นทีละขั้นตอน)
3. [การผนวก ZigZag Indicator](#3-การผนวก-zigzag-indicator)
4. [วิธีการตรวจจับ Pivot Point](#4-วิธีการตรวจจับ-pivot-point)
5. [ระบบกำหนดป้ายชื่อระดับชั้น (Degree Labeling)](#5-ระบบกำหนดป้ายชื่อระดับชั้น)
6. [ตรรกะการตรวจสอบ (Validation --- กฎเหล็ก)](#6-ตรรกะการตรวจสอบ)
7. [ระบบให้คะแนนความมั่นใจ (Confidence Scoring)](#7-ระบบให้คะแนนความมั่นใจ)
8. [การจัดการการนับคลื่นทางเลือก (Alternate Counts)](#8-การจัดการการนับคลื่นทางเลือก)
9. [การจัดวางข้ามกรอบเวลา (Multi-Timeframe Alignment)](#9-การจัดวางข้ามกรอบเวลา)
10. [ตรรกะหลัก --- การตัดสินใจเข้า/ออก](#10-ตรรกะหลัก----การตัดสินใจเข้าออก)
11. [ข้อกำหนดทางเทคนิค](#11-ข้อกำหนดทางเทคนิค)
12. [พารามิเตอร์ความเสี่ยง --- การคำนวณ SL/TP/RR](#12-พารามิเตอร์ความเสี่ยง)
13. [ขั้นตอนการดำเนินการ --- Pseudocode ฉบับสมบูรณ์](#13-ขั้นตอนการดำเนินการ)
14. [การเพิ่มประสิทธิภาพ (Performance Optimization)](#14-การเพิ่มประสิทธิภาพ)
15. [เอกสารอ้างอิง](#15-เอกสารอ้างอิง)

---

## 1. บทนำเกี่ยวกับการนับคลื่นอัตโนมัติ

### 1.1 ความท้าทาย

การนับคลื่นอีเลียตอัตโนมัติเป็นหนึ่งในปัญหาที่ยากที่สุดในการวิเคราะห์ทางเทคนิคเชิงคำนวณ ความท้าทายหลัก:

1. **การระเบิดเชิงผสม (Combinatorial Explosion)**: เมื่อมี $n$ จุดหมุน จำนวนการกำหนดป้ายคลื่นที่เป็นไปได้เพิ่มขึ้นแบบเอกซ์โพเนนเชียล
2. **ความเป็นอัตวิสัย (Subjectivity)**: การนับคลื่นที่ถูกต้องหลายแบบสามารถอยู่ร่วมกันได้ ต่างกันเพียงความน่าจะเป็น
3. **ความไม่แน่นอนแบบเรียลไทม์**: คลื่นปัจจุบันสามารถระบุได้อย่างแน่นอนก็ต่อเมื่อเสร็จสมบูรณ์แล้ว
4. **ความซับซ้อนหลายระดับชั้น**: คลื่นประกอบด้วยคลื่น ทำให้ต้องกำหนดป้ายแบบ Recursive
5. **ความหลากหลายของรูปแบบ**: คลื่นย้อนกลับมีหลายรูปแบบ (Zigzag, Flat, Triangle, Combinations)

### 1.2 แนวทางอัลกอริทึม

แนวทางของเราใช้วิธี **ลำดับชั้นบนลงล่าง (Hierarchical Top-Down)** ด้วยสถาปัตยกรรมต่อไปนี้:

```
┌───────────────────────────────────────────────────────────┐
│                    WAVE COUNTING ENGINE                     │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Layer 1: Pivot Detection (ZigZag + Adaptive Threshold)   │
│     │                                                     │
│     ▼                                                     │
│  Layer 2: Wave Candidate Generation (Combinatorial)       │
│     │                                                     │
│     ▼                                                     │
│  Layer 3: Rule Validation (Iron Rules + Guidelines)       │
│     │                                                     │
│     ▼                                                     │
│  Layer 4: Confidence Scoring (Multi-Factor Weighting)     │
│     │                                                     │
│     ▼                                                     │
│  Layer 5: Multi-Timeframe Alignment (Fractal Validation)  │
│     │                                                     │
│     ▼                                                     │
│  Layer 6: Trade Signal Generation (Entry/Exit Logic)      │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### 1.3 หลักการออกแบบ

| หลักการ | คำอธิบาย |
|---|---|
| **บนลงล่าง (Top-Down)** | เริ่มจากกรอบเวลาสูงสุด; ใช้การนับ HTF จำกัด LTF |
| **กฎเกณฑ์มาก่อน (Rule-First)** | กฎเหล็กเป็นสัมบูรณ์; การละเมิดใด ๆ ทำให้การนับเป็นโมฆะทันที |
| **เชิงความน่าจะเป็น (Probabilistic)** | รักษาหลายการนับพร้อมน้ำหนักความน่าจะเป็น |
| **แบบ Bayesian** | อัปเดตความน่าจะเป็นเมื่อข้อมูลใหม่เข้ามา |
| **ตรวจสอบด้วย Fibonacci** | ความสัมพันธ์ Fibonacci เพิ่มความมั่นใจ; การละเมิดลดความมั่นใจ |
| **ต้องมีการยืนยัน (Confirmation-Required)** | ไม่เทรดโดยไม่มีปัจจัยยืนยันหลายตัว |

---

## 2. อัลกอริทึมการนับคลื่นทีละขั้นตอน

### 2.1 อัลกอริทึมระดับสูง

```
ALGORITHM: ElliottWaveCounter

INPUT:
    market_data: OHLCV data for multiple timeframes
    config: Configuration parameters
    previous_count: Optional prior wave count for continuity

OUTPUT:
    wave_counts: List of WaveCount objects ranked by confidence
    trade_signals: List of TradeSignal objects

PROCEDURE:

    // STEP 1: เตรียมข้อมูล
    FOR EACH timeframe IN config.timeframes (highest to lowest):
        clean_data[tf] = preprocess(market_data[tf])
    
    // STEP 2: ตรวจจับจุดหมุน
    FOR EACH timeframe IN config.timeframes:
        pivots[tf] = detect_pivots(clean_data[tf], config.pivot_params[tf])
    
    // STEP 3: สร้างตัวเลือกคลื่น (Top-Down)
    htf = config.timeframes[0]  // กรอบเวลาสูงสุด
    htf_candidates = generate_wave_candidates(pivots[htf])
    
    // STEP 4: ตรวจสอบตัวเลือก
    valid_counts = []
    FOR EACH candidate IN htf_candidates:
        IF validate_iron_rules(candidate):
            score = calculate_confidence(candidate, clean_data[htf])
            valid_counts.APPEND((candidate, score))
    
    // STEP 5: จัดอันดับและเลือกการนับดีที่สุด
    valid_counts.SORT(BY score, DESCENDING)
    top_counts = valid_counts[:config.max_alternate_counts]
    
    // STEP 6: จัดวางกับกรอบเวลาต่ำกว่า
    FOR EACH (count, score) IN top_counts:
        FOR EACH lower_tf IN config.timeframes[1:]:
            alignment_score = validate_ltf_alignment(
                count, pivots[lower_tf], clean_data[lower_tf]
            )
            count.alignment_scores[lower_tf] = alignment_score
        
        count.final_score = calculate_final_score(count, count.alignment_scores)
    
    // STEP 7: สร้างสัญญาณเทรด
    trade_signals = generate_signals(top_counts, clean_data, config)
    
    RETURN top_counts, trade_signals
```

---

## 3. การผนวก ZigZag Indicator

### 3.1 อัลกอริทึม ZigZag มาตรฐาน

ZigZag Indicator ระบุ Swing ราคาสำคัญโดยกรอง Noise ที่ต่ำกว่า Threshold ที่กำหนด

```python
def zigzag(data, threshold, mode='percent'):
    """
    ZigZag indicator for pivot detection.
    
    Parameters:
        data: DataFrame with 'high' and 'low' columns
        threshold: Minimum reversal threshold
        mode: 'percent' (percentage) or 'absolute' (price) or 'atr' (ATR-based)
    
    Returns:
        List of pivot points: [(index, price, type), ...]
        where type is 'high' or 'low'
    """
    # (ดู Implementation เต็มใน Source Document)
```

### 3.2 Adaptive ZigZag สำหรับคลื่นอีเลียต

ZigZag มาตรฐานที่มี Threshold คงที่จะพลาดคลื่นในระดับชั้นต่าง ๆ **Adaptive ZigZag** ใช้หลาย Thresholds:

### 3.3 การเลือก Threshold ตามตลาด

| ตลาด | กรอบเวลา | ZigZag Threshold | ระดับชั้นคลื่นเป้าหมาย |
|---|---|---|---|
| Forex คู่หลัก | Monthly | 10%--15% | Cycle/Supercycle |
| Forex คู่หลัก | Weekly | 5%--8% | Primary |
| Forex คู่หลัก | Daily | 2%--4% | Intermediate |
| Forex คู่หลัก | 4H | 1%--2% | Minor |
| Forex คู่หลัก | 1H | 0.5%--1% | Minute |
| Crypto (BTC) | Weekly | 15%--25% | Cycle |
| Crypto (BTC) | Daily | 8%--15% | Primary |
| Crypto (BTC) | 4H | 4%--8% | Intermediate |
| Crypto (Alts) | Daily | 15%--30% | Primary |
| Crypto (Alts) | 4H | 8%--15% | Intermediate |

### 3.4 ATR-Based Adaptive Threshold

$$\text{Threshold}_{\text{dynamic}} = k \times \frac{ATR(n)}{P_{\text{current}}} \times 100\%$$

โดยที่ $k$ คือตัวคูณ:
- $k = 2$ สำหรับจับคลื่นระดับ Minor
- $k = 4$ สำหรับจับคลื่นระดับ Intermediate
- $k = 8$ สำหรับจับคลื่นระดับ Primary

---

## 4. วิธีการตรวจจับ Pivot Point

### 4.1 Fractal-Based Pivots

**Fractal High** คือแท่งที่มีจุดสูงสุดสูงกว่าจุดสูงสุดของ $n$ แท่งแต่ละด้าน **Fractal Low** คือแท่งที่มีจุดต่ำสุดต่ำกว่าจุดต่ำสุดของ $n$ แท่งแต่ละด้าน

### 4.2 การจัดระดับความแข็งแกร่งของ Pivot

| ความแข็งแกร่ง | จำนวนแท่งแต่ละด้าน | ระดับชั้นคลื่น (ทั่วไป) |
|---|---|---|
| 1 | 1 | Sub-minuette |
| 2 | 2 | Minuette |
| 3 | 3--5 | Minute |
| 5 | 5--8 | Minor |
| 8 | 8--13 | Intermediate |
| 13 | 13--21 | Primary |
| 21 | 21--34 | Cycle |

---

## 5. ระบบกำหนดป้ายชื่อระดับชั้น

```python
WAVE_DEGREES = {
    'grand_supercycle': {
        'motive_labels': ['[I]', '[II]', '[III]', '[IV]', '[V]'],
        'corrective_labels': ['[A]', '[B]', '[C]', '[D]', '[E]'],
        'typical_timeframe': 'multi-decade',
    },
    'supercycle': {
        'motive_labels': ['(I)', '(II)', '(III)', '(IV)', '(V)'],
        'corrective_labels': ['(A)', '(B)', '(C)', '(D)', '(E)'],
        'typical_timeframe': 'multi-year',
    },
    'cycle': {
        'motive_labels': ['I', 'II', 'III', 'IV', 'V'],
        'corrective_labels': ['A', 'B', 'C', 'D', 'E'],
        'typical_timeframe': '1-several years',
    },
    'primary': {
        'motive_labels': ['1', '2', '3', '4', '5'],
        'corrective_labels': ['A', 'B', 'C', 'D', 'E'],
        'typical_timeframe': 'months to 1 year',
    },
    'intermediate': {
        'motive_labels': ['(1)', '(2)', '(3)', '(4)', '(5)'],
        'corrective_labels': ['(a)', '(b)', '(c)', '(d)', '(e)'],
        'typical_timeframe': 'weeks to months',
    },
    'minor': {
        'motive_labels': ['1', '2', '3', '4', '5'],
        'corrective_labels': ['a', 'b', 'c', 'd', 'e'],
        'typical_timeframe': 'days to weeks',
    },
    'minute': {
        'motive_labels': ['i', 'ii', 'iii', 'iv', 'v'],
        'corrective_labels': ['a', 'b', 'c', 'd', 'e'],
        'typical_timeframe': 'hours to days',
    },
}
```

---

## 6. ตรรกะการตรวจสอบ (Validation --- กฎเหล็ก)

(ดู WaveRuleValidator class ใน Source Document --- ตรวจสอบกฎเหล็กสามข้อ พร้อม violation recovery)

---

## 7. ระบบให้คะแนนความมั่นใจ (Confidence Scoring)

### 7.1 โมเดลความมั่นใจหลายปัจจัย

ช่วงคะแนน: 0.0 ถึง 1.0 | ขั้นต่ำสำหรับเทรด: 0.65

### 7.2 น้ำหนักความมั่นใจ

```python
CONFIDENCE_WEIGHTS = {
    'structural':     0.25,  # สำคัญที่สุด: ปฏิบัติตามกฎและโครงสร้างหรือไม่?
    'fibonacci':      0.20,  # สำคัญมาก: อัตราส่วนสอดคล้องหรือไม่?
    'volume':         0.15,  # สำคัญ: ปริมาณยืนยันตัวตนคลื่นหรือไม่?
    'momentum':       0.15,  # สำคัญ: โมเมนตัมยืนยันเฟสหรือไม่?
    'time':           0.08,  # ปานกลาง: สัดส่วนเวลาสมเหตุสมผลหรือไม่?
    'mtf_alignment':  0.12,  # สำคัญ: HTF สนับสนุนการนับนี้หรือไม่?
    'pattern_match':  0.05,  # น้อย: ดูเหมือนตัวอย่างตำราหรือไม่?
}
# Sum = 1.00
```

### 7.3 เกณฑ์ความมั่นใจ

| คะแนนความมั่นใจ | การจำแนก | การดำเนินการเทรด |
|---|---|---|
| 0.90--1.00 | สูงมาก | ขนาดสถานะเต็ม, เข้าแบบ Aggressive |
| 0.80--0.89 | สูง | ขนาดสถานะมาตรฐาน |
| 0.70--0.79 | ปานกลาง | ขนาดลด (70%) |
| 0.65--0.69 | ยอมรับได้ | สถานะเล็ก (50%), Stop แน่น |
| 0.50--0.64 | ต่ำ | ติดตามเท่านั้น, ไม่เทรด |
| < 0.50 | ไม่น่าเชื่อถือ | ละทิ้งการนับ |

---

## 8. การจัดการการนับคลื่นทางเลือก (Alternate Counts)

### 8.1 ปรัชญา

การวิเคราะห์คลื่นอีเลียตสร้างการตีความที่ถูกต้องหลายแบบโดยธรรมชาติ ข้อค้นพบสำคัญสำหรับการเทรดด้วยอัลกอริทึม: **เราไม่จำเป็นต้องรู้การนับที่ "ถูกต้อง" --- เราต้องรู้ผลกระทบต่อการเทรดของแต่ละการนับที่เป็นไปได้**

### 8.2 การจัดการการนับทางเลือก

- รักษาการนับพร้อมกันสูงสุด 3 แบบ
- ใช้ Bayesian Updating เพื่อปรับความน่าจะเป็นเมื่อข้อมูลใหม่เข้ามา
- ตรวจสอบ Invalidation เมื่อราคาใหม่ปรากฏ
- ตัดแต่งการนับความน่าจะเป็นต่ำและอาจสร้างการนับใหม่

---

## 9. การจัดวางข้ามกรอบเวลา (Multi-Timeframe Alignment)

(ดูรายละเอียดใน Source Document)

---

## 10. ตรรกะหลัก --- การตัดสินใจเข้า/ออก

(ดูรายละเอียดใน 00_overview.md)

---

## 11. ข้อกำหนดทางเทคนิค

(ดูรายละเอียดใน Source Document)

---

## 12. พารามิเตอร์ความเสี่ยง --- การคำนวณ SL/TP/RR

(ดูรายละเอียดใน 00_overview.md)

---

## 13. ขั้นตอนการดำเนินการ --- Pseudocode ฉบับสมบูรณ์

(ดูรายละเอียดใน Source Document)

---

## 14. การเพิ่มประสิทธิภาพ (Performance Optimization)

(ดูรายละเอียดใน Source Document)

---

## 15. เอกสารอ้างอิง

(ดูรายละเอียดใน 00_overview.md)

---

*เอกสารนี้เป็นส่วนหนึ่งของฐานความรู้ระบบ AI เทรดแบบ Multi-Agent ครอบคลุมอัลกอริทึมการนับคลื่นอีเลียตอัตโนมัติโดยละเอียด นี่คือเอกสารสุดท้ายในชุดคลื่นอีเลียต*
