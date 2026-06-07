# แหล่งสภาพคล่อง (Liquidity Pools) และการวิเคราะห์สภาพคล่อง — FVG, Breaker Blocks, โซน OTE

> **แกน 1 — กลยุทธ์การเทรด | โมดูล 03 — Order Flow และสภาพคล่อง (Liquidity)**
> เอกสาร: 02_liquidity_concepts.md
> เวอร์ชัน: 2.0 | อัปเดตล่าสุด: 2026-04-12
> การจัดประเภท: ฐานความรู้หลัก — ระบบเทรด AI แบบหลายเอเจนต์ (Multi-Agent AI Trading System)

---

## สารบัญ

1. [บทนำเรื่องสภาพคล่องในการเทรด](#1-บทนำเรื่องสภาพคล่องในการเทรด)
2. [สภาพคล่องฝั่งซื้อ (Buy-Side Liquidity - BSL)](#2-สภาพคล่องฝั่งซื้อ-bsl)
3. [สภาพคล่องฝั่งขาย (Sell-Side Liquidity - SSL)](#3-สภาพคล่องฝั่งขาย-ssl)
4. [ช่องว่างสภาพคล่อง (Liquidity Voids) — ความไม่มีประสิทธิภาพของราคา](#4-ช่องว่างสภาพคล่อง--ความไม่มีประสิทธิภาพของราคา)
5. [Fair Value Gaps (FVG)](#5-fair-value-gaps-fvg)
6. [Consequent Encroachment ของ FVG](#6-consequent-encroachment-ของ-fvg)
7. [Breaker Blocks](#7-breaker-blocks)
8. [Mitigation Blocks](#8-mitigation-blocks)
9. [โซนจุดเข้าเทรดที่เหมาะสม (Optimal Trade Entry - OTE)](#9-โซนจุดเข้าเทรดที่เหมาะสม-ote)
10. [กรอบทางคณิตศาสตร์สำหรับการระบุโซนสภาพคล่อง](#10-กรอบทางคณิตศาสตร์สำหรับการระบุโซนสภาพคล่อง)
11. [อัลกอริทึมสำหรับตรวจจับ FVG แบบโปรแกรม](#11-อัลกอริทึมสำหรับตรวจจับ-fvg-แบบโปรแกรม)
12. [ลอจิกหลัก — จุดเข้า/ออก (Entry/Exit)](#12-ลอจิกหลัก--จุดเข้าออก)
13. [ข้อกำหนดทางเทคนิค](#13-ข้อกำหนดทางเทคนิค)
14. [พารามิเตอร์ความเสี่ยง](#14-พารามิเตอร์ความเสี่ยง)
15. [ขั้นตอนการทำงาน — Pseudocode](#15-ขั้นตอนการทำงาน--pseudocode)
16. [เอกสารอ้างอิง](#16-เอกสารอ้างอิง)

---

## 1. บทนำเรื่องสภาพคล่องในการเทรด

### 1.1 สภาพคล่องคืออะไรในบริบทของ Price Action?

ในบริบทของวิธีการ ICT (Inner Circle Trader) และการเทรดระดับสถาบัน **สภาพคล่อง (Liquidity)** หมายถึงกลุ่มคำสั่ง stop-loss และคำสั่งรอดำเนินการที่อยู่ในระดับราคาที่คาดการณ์ได้ กลุ่มเหล่านี้แทนเงินจริงที่สถาบันสามารถเล็งเป้าเพื่อเติมสถานะขนาดใหญ่ของตนเอง

**ข้อสรุปสำคัญ**: เทรดเดอร์สถาบันต้องการสภาพคล่องจำนวนมาก (ปริมาณคู่สัญญา) เพื่อเข้าและออกสถานะ พวกเขาไม่สามารถเพียงวางคำสั่ง market โดยไม่มี slippage อย่างมีนัยสำคัญ ดังนั้นพวกเขาจึงค้นหาและเล็งเป้าบริเวณที่ stop loss ของรายย่อยรวมตัวกัน

### 1.2 วงจรสภาพคล่อง (The Liquidity Cycle)

```
┌─────────────────────────────────────────────────────────────────┐
│                    วงจรสภาพคล่อง (THE LIQUIDITY CYCLE)           │
│                                                                 │
│  1. SETUP         2. SWEEP           3. REVERSAL    4. TARGET   │
│                                                                 │
│  ราคาสร้าง       ราคาเคลื่อนไป     ราคากลับตัว     ราคา       │
│  จุดสูง/ต่ำ      กวาด stop ที่      อย่างรุนแรง     เล็งเป้า   │
│  ที่ชัดเจน       รวมตัวที่          หลังจากเก็บ     สภาพคล่อง  │
│  ซึ่งรายย่อย     ระดับเหล่านี้      สภาพคล่อง      ฝั่งตรงข้าม │
│  วาง stop                                                      │
│                                                                 │
│  ──── High ─────  ──── Sweep ────  ──── ─────  ──── Target ─── │
│       │                 ╱╲              │              │        │
│       │            ╱╲  ╱  ╲             │              │        │
│  ╱╲   │       ╱╲ ╱  ╲╱    ╲       ╱╲   │         ╱╲   │        │
│ ╱  ╲  │  ╱╲ ╱  ╲         ╲ ╱╲ ╱  ╲  │    ╱╲ ╱  ╲  │        │
│╱    ╲╱╲╱╱  ╲╱              ╲╱  ╲╱    ╲ │ ╱╱  ╲╱    ╲ │        │
│                                      ╲│╱             ╲│        │
│                                       ╲               ╲        │
│  รายย่อย:        รายย่อย:           Smart Money:     SM ออก    │
│  "จะวาง SL      "โดน stop          "Fill ได้ที่     เข้าสู่   │
│  เหนือ high"    ออกแล้ว!"          SL ของพวกเขา"   สภาพคล่อง │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 ประเภทของสภาพคล่อง

| ประเภท | ตำแหน่ง | องค์ประกอบ | การใช้งานของสถาบัน |
|------|----------|-------------|-------------------|
| **สภาพคล่องฝั่งซื้อ (BSL)** | เหนือ swing highs, เหนือ equal highs | Sell stops (เทรดเดอร์ short), buy stop entries | สถาบันขายเข้า buy stops เพื่อ fill short |
| **สภาพคล่องฝั่งขาย (SSL)** | ใต้ swing lows, ใต้ equal lows | Buy stops (เทรดเดอร์ long), sell stop entries | สถาบันซื้อเข้า sell stops เพื่อ fill long |
| **สภาพคล่องภายใน (Internal)** | ภายในช่วงราคา (FVGs, imbalances) | Limit orders, เทรดเดอร์ mean-reversion | ราคาปรับสมดุลเพื่อ fill |
| **สภาพคล่องภายนอก (External)** | นอกสุดขีดของช่วง | Stop losses นอกเหนือระดับที่ชัดเจน | เป้าหมาย sweep สำหรับการสะสม/กระจาย |

### 1.4 สภาพคล่องเป็นแม่เหล็ก

ราคาถูกดึงดูดไปยังสภาพคล่องเหมือนแม่เหล็กเพราะ:

1. **ความจำเป็นของสถาบัน**: คำสั่งขนาดใหญ่ต้องการปริมาณคู่สัญญาเพื่อ fill
2. **แรงจูงใจ market maker**: Market makers มีแรงจูงใจที่จะค้นหาและกระตุ้น stops
3. **Self-fulfilling**: ทุกคนรู้ว่า stops อยู่ที่ไหน สร้างเป้าหมายที่เห็นพ้องกัน
4. **กลไก order flow**: Stops ที่ถูกกระตุ้นสร้างโมเมนตัมเพิ่มเติม (cascading)

---

## 2. สภาพคล่องฝั่งซื้อ (Buy-Side Liquidity - BSL)

### 2.1 คำจำกัดความ

สภาพคล่องฝั่งซื้อ (BSL) ประกอบด้วย **คำสั่ง buy stop** ที่ค้างอยู่เหนือราคาตลาดปัจจุบัน สิ่งเหล่านี้มีอยู่เพราะ:

- ผู้ขาย short วาง stop loss เหนือ high ล่าสุด
- เทรดเดอร์ breakout มี buy-stop entries เหนือแนวต้าน
- เทรดเดอร์ที่มีคำสั่งรอเพื่อ long "เมื่อ breakout"

### 2.2 ตำแหน่งที่ BSL สะสม

```
ตำแหน่งการก่อตัว BSL:
════════════════════════

ตำแหน่ง 1: เหนือ Swing Highs
─────────────────────────────
         BSL ████████████  (sell stops จาก shorts + buy stop entries)
         ───────────── Swing High
    ╱╲
   ╱  ╲    ╱╲
  ╱    ╲  ╱  ╲
 ╱      ╲╱    ╲

ตำแหน่ง 2: เหนือ Equal Highs (Double/Triple Tops)
──────────────────────────────────────────────────
         BSL ████████████████████  (สภาพคล่องพิเศษ — ระดับที่ชัดเจนมาก)
         ─────────────────────── Equal Highs (BSL แข็งแรงมาก)
    ╱╲        ╱╲       ╱╲
   ╱  ╲      ╱  ╲     ╱  ╲
  ╱    ╲    ╱    ╲   ╱    ╲
 ╱      ╲  ╱      ╲ ╱      ╲
╱        ╲╱        ╲╱        ╲

ตำแหน่ง 3: เหนือ Trendline (ขาลง)
────────────────────────────────────────
    BSL กระจายตัวตามและเหนือ trendline
    ╲─────────────────────
     ╲      BSL ████
      ╲
       ╲    BSL ████
        ╲
         ╲  BSL ████

ตำแหน่ง 4: เหนือ High ของวัน/สัปดาห์/เดือนก่อนหน้า
──────────────────────────────────────────────
    BSL ████████████████  (แหล่งสภาพคล่องตามเวลา)
    ─── PDH / PWH / PMH ───
```

### 2.3 ระบบจัดเกรด BSL

BSL ทั้งหมดไม่เท่าเทียมกัน จัดเกรด BSL ตามขนาดที่คาดหวัง:

| เกรด | เงื่อนไข | สภาพคล่องที่คาดหวัง | ตัวอย่าง |
|-------|-----------|-------------------|---------|
| **A+ (พรีเมียม)** | Equal highs หลายจุดบน HTF + swing high สอดคล้อง | สุดขีด | Equal highs รายสัปดาห์กับ swing high รายเดือน |
| **A (แข็งแรง)** | Equal highs หรือ swing high สำคัญบน HTF | สูง | Double top รายวัน, swing high รายสัปดาห์ |
| **B (ปานกลาง)** | Swing high เดี่ยวบน MTF | ปานกลาง | Swing high 4H, swing high รายวัน |
| **C (อ่อน)** | Swing high เดี่ยวบน LTF เท่านั้น | ต่ำ | Swing high 15M/1H |

### 2.4 อัลกอริทึมตรวจจับ BSL

```python
def detect_buy_side_liquidity(candles: List[Candle], config: dict) -> List[LiquidityPool]:
    """
    Detect buy-side liquidity pools above current price.
    
    Identifies:
    1. Swing highs
    2. Equal highs (within tolerance)
    3. HTF key levels (PDH, PWH, PMH)
    """
    pools = []
    lookback = config.get('swing_lookback', 5)
    equal_high_tolerance = config.get('equal_high_tolerance_pct', 0.05)
    
    # 1. Find all swing highs
    swing_highs = []
    for i in range(lookback, len(candles) - lookback):
        is_swing = all(
            candles[i].high > candles[i-j].high and
            candles[i].high > candles[i+j].high
            for j in range(1, lookback + 1)
        )
        if is_swing:
            swing_highs.append({
                'price': candles[i].high,
                'index': i,
                'timestamp': candles[i].timestamp
            })
    
    # 2. Detect equal highs (BSL clusters)
    equal_high_groups = []
    used = set()
    
    for i, sh1 in enumerate(swing_highs):
        if i in used:
            continue
        group = [sh1]
        for j, sh2 in enumerate(swing_highs[i+1:], i+1):
            if j in used:
                continue
            pct_diff = abs(sh1['price'] - sh2['price']) / sh1['price'] * 100
            if pct_diff <= equal_high_tolerance:
                group.append(sh2)
                used.add(j)
        
        if len(group) >= 2:
            equal_high_groups.append(group)
            used.add(i)
    
    # 3. Create liquidity pools
    for group in equal_high_groups:
        avg_price = np.mean([sh['price'] for sh in group])
        pools.append(LiquidityPool(
            type='BSL',
            price=avg_price,
            grade='A' if len(group) >= 3 else 'A' if len(group) == 2 else 'B',
            touch_count=len(group),
            formation='EQUAL_HIGHS',
            first_formed=group[0]['timestamp'],
            last_touched=group[-1]['timestamp'],
            strength=min(len(group) * 0.3 + 0.4, 1.0)
        ))
    
    # 4. Add remaining single swing highs
    for i, sh in enumerate(swing_highs):
        if i not in used:
            pools.append(LiquidityPool(
                type='BSL',
                price=sh['price'],
                grade='B',
                touch_count=1,
                formation='SWING_HIGH',
                first_formed=sh['timestamp'],
                last_touched=sh['timestamp'],
                strength=0.4
            ))
    
    # 5. Sort by strength (strongest first)
    pools.sort(key=lambda p: p.strength, reverse=True)
    
    return pools
```

### 2.5 การเทรด BSL

**สถานการณ์ A: เทรดการ Sweep (กลับตัว)**
- รอให้ราคา sweep BSL
- มองหาการปฏิเสธ (แท่ง bearish, delta divergence, absorption บน ask)
- เข้า SHORT หลังยืนยัน sweep
- Stop loss: เหนือ high ของ sweep
- เป้าหมาย: SSL ถัดไปด้านล่าง

**สถานการณ์ B: เทรดการ Run (ต่อเนื่อง)**
- ถ้า BSL ถูก swept และราคายืนเหนือ → sweep กลายเป็น breakout
- เข้า LONG เมื่อ retest ระดับที่ถูก swept
- Stop loss: ใต้ระดับที่ retest
- เป้าหมาย: BSL ถัดไปด้านบน

---

## 3. สภาพคล่องฝั่งขาย (Sell-Side Liquidity - SSL)

### 3.1 คำจำกัดความ

สภาพคล่องฝั่งขาย (SSL) ประกอบด้วย **คำสั่ง sell stop** ที่ค้างอยู่ใต้ราคาตลาดปัจจุบัน สิ่งเหล่านี้มีอยู่เพราะ:

- เทรดเดอร์ long วาง stop loss ใต้ low ล่าสุด
- เทรดเดอร์ breakout มี sell-stop entries ใต้แนวรับ
- เทรดเดอร์ที่มีคำสั่ง short รอ "เมื่อ breakdown"

### 3.2 ตำแหน่งที่ SSL สะสม

```
ตำแหน่งการก่อตัว SSL:
════════════════════════

ตำแหน่ง 1: ใต้ Swing Lows
────────────────────────────
 ╲      ╱╲    ╱
  ╲    ╱  ╲  ╱
   ╲  ╱    ╲╱
    ╲╱
         ───────────── Swing Low
         SSL ████████████  (buy stops จาก longs + sell stop entries)

ตำแหน่ง 2: ใต้ Equal Lows (Double/Triple Bottoms)
─────────────────────────────────────────────────────
╲        ╱╲        ╱╲        ╱
 ╲      ╱  ╲      ╱  ╲      ╱
  ╲    ╱    ╲    ╱    ╲    ╱
   ╲  ╱      ╲  ╱      ╲  ╱
    ╲╱        ╲╱        ╲╱
         ─────────────────────── Equal Lows (SSL แข็งแรงมาก)
         SSL ████████████████████  (สภาพคล่องสุดขีด)

ตำแหน่ง 3: ใต้ Ascending Trendline
──────────────────────────────────────
             ╱───────────────────
            ╱
      SSL ████  ╱
          ╱
    SSL ████  ╱
        ╱
  SSL ████

ตำแหน่ง 4: ใต้ Low ของวัน/สัปดาห์/เดือนก่อนหน้า
─────────────────────────────────────────────
    ─── PDL / PWL / PML ───
    SSL ████████████████  (แหล่งสภาพคล่องตามเวลา)
```

### 3.3 ระบบจัดเกรด SSL

| เกรด | เงื่อนไข | สภาพคล่องที่คาดหวัง | ความสำคัญทางการเทรด |
|-------|-----------|-------------------|---------------------|
| **A+ (พรีเมียม)** | Equal lows หลายจุดบน HTF + swing low สอดคล้อง | สุดขีด | เป้าหมาย sweep ที่มีความน่าจะเป็นสูง |
| **A (แข็งแรง)** | Equal lows หรือ swing low สำคัญบน HTF | สูง | เป้าหมายหลักสำหรับ long ของสถาบัน |
| **B (ปานกลาง)** | Swing low เดี่ยวบน MTF | ปานกลาง | เป้าหมายรอง |
| **C (อ่อน)** | Swing low เดี่ยวบน LTF เท่านั้น | ต่ำ | เป้าหมายเล็กน้อย อาจไม่ยืน |

### 3.4 อัลกอริทึมตรวจจับ SSL

```python
def detect_sell_side_liquidity(candles: List[Candle], config: dict) -> List[LiquidityPool]:
    """
    Detect sell-side liquidity pools below current price.
    Mirror logic of BSL detection but for lows.
    """
    pools = []
    lookback = config.get('swing_lookback', 5)
    equal_low_tolerance = config.get('equal_low_tolerance_pct', 0.05)
    
    # 1. Find all swing lows
    swing_lows = []
    for i in range(lookback, len(candles) - lookback):
        is_swing = all(
            candles[i].low < candles[i-j].low and
            candles[i].low < candles[i+j].low
            for j in range(1, lookback + 1)
        )
        if is_swing:
            swing_lows.append({
                'price': candles[i].low,
                'index': i,
                'timestamp': candles[i].timestamp
            })
    
    # 2. Detect equal lows (SSL clusters)
    equal_low_groups = []
    used = set()
    
    for i, sl1 in enumerate(swing_lows):
        if i in used:
            continue
        group = [sl1]
        for j, sl2 in enumerate(swing_lows[i+1:], i+1):
            if j in used:
                continue
            pct_diff = abs(sl1['price'] - sl2['price']) / sl1['price'] * 100
            if pct_diff <= equal_low_tolerance:
                group.append(sl2)
                used.add(j)
        
        if len(group) >= 2:
            equal_low_groups.append(group)
            used.add(i)
    
    # 3. Create liquidity pools
    for group in equal_low_groups:
        avg_price = np.mean([sl['price'] for sl in group])
        pools.append(LiquidityPool(
            type='SSL',
            price=avg_price,
            grade='A+' if len(group) >= 3 else 'A',
            touch_count=len(group),
            formation='EQUAL_LOWS',
            first_formed=group[0]['timestamp'],
            last_touched=group[-1]['timestamp'],
            strength=min(len(group) * 0.3 + 0.4, 1.0)
        ))
    
    # 4. Add remaining single swing lows
    for i, sl in enumerate(swing_lows):
        if i not in used:
            pools.append(LiquidityPool(
                type='SSL',
                price=sl['price'],
                grade='B',
                touch_count=1,
                formation='SWING_LOW',
                first_formed=sl['timestamp'],
                last_touched=sl['timestamp'],
                strength=0.4
            ))
    
    pools.sort(key=lambda p: p.strength, reverse=True)
    return pools
```

---

## 4. ช่องว่างสภาพคล่อง (Liquidity Voids) — ความไม่มีประสิทธิภาพของราคา

### 4.1 คำจำกัดความ

**ช่องว่างสภาพคล่อง (Liquidity Void)** (หรือเรียกว่า "volume void" หรือ "price vacuum") คือช่วงราคาที่ถูกผ่านอย่างรวดเร็วมากด้วยปริมาณเทรดน้อยมาก สร้างโซนของความไม่มีประสิทธิภาพที่ราคามีแนวโน้มจะกลับมาเยือนในภายหลังเพื่อ "fill" หรือ "rebalance"

### 4.2 ทำไมช่องว่างสภาพคล่องเกิดขึ้น

```
การก่อตัวของช่องว่างสภาพคล่อง:
══════════════════════════════

Price Action ปกติ:                  การก่อตัวช่องว่างสภาพคล่อง:
(สมดุล, มีประสิทธิภาพ)             (Displacement, ไม่มีประสิทธิภาพ)

ราคาเคลื่อนค่อยๆ                   ราคากระโดดอย่างรวดเร็วผ่าน
ผ่านแต่ละระดับพร้อม                 ระดับต่างๆ โดยมีปริมาณน้อยมาก
ปริมาณทุกราคา                       ที่เทรดในราคาระหว่างกลาง

│████████│ 1.1060                      │██│ 1.1060
│████████│ 1.1058                      │  │ 1.1058  ← VOID
│████████│ 1.1056                      │  │ 1.1056  ← VOID
│████████│ 1.1054                      │  │ 1.1054  ← VOID
│████████│ 1.1052                      │  │ 1.1052  ← VOID
│████████│ 1.1050                      │██│ 1.1050
│████████│ 1.1048                      │████████│ 1.1048

ซ้าย: ปริมาณทุกระดับ                ขวา: ช่องว่างในปริมาณ
      = สมดุล                              = ไม่มีประสิทธิภาพ
      = โอกาสกลับมาน้อย                   = มีโอกาสกลับมา
```

### 4.3 ลักษณะของช่องว่างสภาพคล่อง

| ลักษณะ | คำอธิบาย |
|---------------|-------------|
| **ปริมาณ** | ปริมาณต่ำมากภายในช่วง void |
| **ความเร็ว** | ราคาผ่านช่วงใน 1-3 แท่ง |
| **ตัวแท่ง** | แท่งตัวใหญ่ที่มีไส้เทียนเล็ก |
| **Volume delta** | Delta ทิศทางเดียวสุดขีด |
| **หลังก่อตัว** | ราคามักกลับมา fill 50-100% ของ void |
| **ความเกี่ยวข้องของ timeframe** | Void บน HTF สำคัญกว่า LTF |

### 4.4 การตรวจจับช่องว่างสภาพคล่อง

```python
def detect_liquidity_voids(candles: List[Candle], config: dict) -> List[LiquidityVoid]:
    """
    Detect liquidity voids (rapid price displacement with minimal volume).
    """
    voids = []
    min_body_ratio = config.get('min_body_ratio', 0.7)
    min_displacement_atr = config.get('min_displacement_atr', 2.0)
    volume_ratio_threshold = config.get('volume_void_ratio', 0.3)
    
    atr = calculate_atr(candles, period=14)
    avg_volume = np.mean([c.volume for c in candles[-50:]])
    
    for i in range(1, len(candles)):
        candle = candles[i]
        prev_candle = candles[i-1]
        
        body = abs(candle.close - candle.open)
        range_size = candle.high - candle.low
        
        if range_size == 0:
            continue
        
        body_ratio = body / range_size
        displacement_size = range_size / atr[i]
        
        is_displacement = (
            body_ratio >= min_body_ratio and
            displacement_size >= min_displacement_atr
        )
        
        if is_displacement:
            if candle.close > candle.open:  # Bullish displacement
                void_low = max(prev_candle.high, candle.open)
                void_high = candle.close
                direction = 'BULLISH'
            else:  # Bearish displacement
                void_high = min(prev_candle.low, candle.open)
                void_low = candle.close
                direction = 'BEARISH'
            
            if void_high > void_low:
                voids.append(LiquidityVoid(
                    high=void_high,
                    low=void_low,
                    direction=direction,
                    timestamp=candle.timestamp,
                    candle_index=i,
                    displacement_size=displacement_size,
                    filled_pct=0.0,
                    status='UNFILLED'
                ))
    
    return voids
```

### 4.5 การเทรดช่องว่างสภาพคล่อง

**ลอจิกการเข้า:**
- หลัง bearish void ก่อตัว → คาดว่าราคาจะ retrace ขึ้นเข้าสู่ void
- เข้า SHORT เมื่อราคาเข้า void (ระดับ 50% หรือ CE ของ FVG ที่เกี่ยวข้อง)
- หลัง bullish void ก่อตัว → คาดว่าราคาจะ retrace ลงเข้าสู่ void
- เข้า LONG เมื่อราคาเข้า void (ระดับ 50% หรือ CE ของ FVG ที่เกี่ยวข้อง)

**สำคัญ**: Void ในทิศทางของเทรนด์ timeframe สูงกว่ามีโอกาสถูกเคารพมากกว่า (fill บางส่วนแล้วต่อเนื่อง) มากกว่าจะถูก fill ทั้งหมด

---

## 5. Fair Value Gaps (FVG)

### 5.1 คำจำกัดความ

**Fair Value Gap (FVG)** คือรูปแบบสามแท่งเทียนที่ตัวของแท่งกลางสร้างช่องว่างระหว่างไส้เทียนของแท่งแรกและแท่งที่สาม ช่องว่างนี้แทนความไม่มีประสิทธิภาพของราคาที่ฝั่งหนึ่ง (ผู้ซื้อหรือผู้ขาย) มีอำนาจเหนืออย่างท่วมท้น

### 5.2 กฎการก่อตัวของ FVG

**FVG ขาขึ้น (Bullish FVG - BFVG):**
```
Candle 1 (C1): แท่งใดก็ได้
Candle 2 (C2): แท่ง bullish แข็งแรง (displacement)
Candle 3 (C3): แท่งใดก็ได้

เงื่อนไข: C3.low > C1.high
โซน FVG: จาก C1.high (ด้านล่าง) ถึง C3.low (ด้านบน)

Visual:
              ┌────┐
              │ C3 │
              │    │
              └──┬─┘
   FVG ZONE → │████│ ← ช่องว่างระหว่าง C1.high และ C3.low
              ┌──┴─┐
              │    │
              │ C2 │  ← แท่ง Displacement
              │    │
              └──┬─┘
              ┌──┴─┐
              │ C1 │
              │    │
              └────┘
```

**FVG ขาลง (Bearish FVG - SFVG):**
```
Candle 1 (C1): แท่งใดก็ได้
Candle 2 (C2): แท่ง bearish แข็งแรง (displacement)
Candle 3 (C3): แท่งใดก็ได้

เงื่อนไข: C3.high < C1.low
โซน FVG: จาก C3.high (ด้านล่าง) ถึง C1.low (ด้านบน)

Visual:
              ┌────┐
              │ C1 │
              │    │
              └──┬─┘
              ┌──┴─┐
              │    │
              │ C2 │  ← แท่ง Displacement
              │    │
              └──┬─┘
   FVG ZONE → │████│ ← ช่องว่างระหว่าง C3.high และ C1.low
              ┌──┴─┐
              │ C3 │
              │    │
              └────┘
```

### 5.3 การจำแนกประเภท FVG

| ประเภท | เกณฑ์ | คุณภาพ | ลำดับความสำคัญ |
|------|----------|---------|-----------------|
| **Premium Bullish FVG** | เกิดในโซน premium (เหนือ 50% ของช่วง) ระหว่าง pullback | สูงสุด | ลำดับแรกสำหรับ long |
| **Discount Bullish FVG** | เกิดในโซน discount (ต่ำกว่า 50% ของช่วง) | สูง | เป้าหมาย long หลัก |
| **Premium Bearish FVG** | เกิดในโซน premium | สูง | เป้าหมาย short หลัก |
| **Discount Bearish FVG** | เกิดในโซน discount ระหว่าง pullback | สูงสุด | ลำดับแรกสำหรับ short |
| **Balanced FVG** | ช่องว่างเล็กมาก ถูก fill บางส่วนแล้ว | ต่ำ | ลำดับรอง |

### 5.4 FVG พร้อมการยืนยันปริมาณ

FVG จะ **แข็งแรงกว่า** เมื่อมีสิ่งนี้ประกอบ:

$$\text{FVG Strength} = \alpha \cdot \frac{V_{C2}}{V_{avg}} + \beta \cdot \frac{|\Delta_{C2}|}{\Delta_{avg}} + \gamma \cdot \frac{\text{gap\_size}}{\text{ATR}}$$

โดยที่:
- $V_{C2}$ = ปริมาณของแท่ง displacement (C2)
- $V_{avg}$ = ปริมาณเฉลี่ยในช่วง lookback
- $\Delta_{C2}$ = Delta ของ C2 (ควรมีทิศทางแข็งแรง)
- $\Delta_{avg}$ = ค่าเฉลี่ยสัมบูรณ์ของ delta
- gap_size = ขนาดของ FVG ในหน่วยราคา
- ATR = Average True Range
- $\alpha = 0.35, \beta = 0.35, \gamma = 0.30$ (น้ำหนักเริ่มต้น)

### 5.5 กฎการเทรด FVG

**การเข้าที่ FVG (Mean Reversion):**

```
การเข้า BULLISH FVG:
1. ราคา retrace กลับลงเข้าสู่โซน FVG
2. จุดเข้า: ที่ 50% ของ FVG (Consequent Encroachment) หรือที่ก้น FVG
3. Stop Loss: ใต้ก้น FVG (C1.high)
4. Take Profit: เท่ากับ displacement move หรือ BSL ถัดไป

การเข้า BEARISH FVG:
1. ราคา retrace กลับขึ้นเข้าสู่โซน FVG
2. จุดเข้า: ที่ 50% ของ FVG (Consequent Encroachment) หรือที่ยอด FVG
3. Stop Loss: เหนือยอด FVG (C1.low)
4. Take Profit: เท่ากับ displacement move หรือ SSL ถัดไป
```

### 5.6 การเป็นโมฆะของ FVG (FVG Invalidation)

FVG **เป็นโมฆะ** เมื่อ:
- ราคาปิดทะลุผ่าน FVG ทั้งหมด (ไม่ใช่แค่ไส้เทียนผ่าน)
- โดยเฉพาะ: แท่งหนึ่ง CLOSE เกินขอบไกลของ FVG

```
การเป็นโมฆะของ BULLISH FVG:
─────────────────────────
  FVG top: 1.1060 (C3.low)
  FVG bottom: 1.1050 (C1.high)
  
  เป็นโมฆะถ้า: แท่งใดๆ CLOSE ต่ำกว่า 1.1050
  ยังคงใช้ได้ถ้า: ไส้เทียนลงต่ำกว่า 1.1050 แต่ปิดเหนือ
  
  หมายเหตุ: ไส้เทียนด้านล่างที่กลับตัวจริงๆ เป็นสัญญาณที่แข็งแรงกว่า
  (มัน sweep stops ใต้ FVG แล้วยืน = accumulation)
```

---

## 6. Consequent Encroachment ของ FVG

### 6.1 คำจำกัดความ

**Consequent Encroachment (CE)** คือระดับ 50% (จุดกึ่งกลาง) ของ Fair Value Gap วิธีการ ICT ระบุว่านี่คือจุดที่มีโอกาสมากที่สุดที่ราคาจะตอบสนองภายใน FVG

### 6.2 การคำนวณ

$$\text{CE}_{bullish} = \frac{C1_{high} + C3_{low}}{2} = \frac{\text{FVG bottom} + \text{FVG top}}{2}$$

$$\text{CE}_{bearish} = \frac{C1_{low} + C3_{high}}{2} = \frac{\text{FVG top} + \text{FVG bottom}}{2}$$

### 6.3 ทำไม CE สำคัญ

```
FVG พร้อมระดับ CE:
══════════════════

    FVG Top:    1.1060 ─────────────  ← การ retrace สูงสุดที่คาดหวัง
                                          (ถ้าราคามาถึงนี่ FVG อาจล้มเหลว)
    
    CE:         1.1055 ─ ─ ─ ─ ─ ─ ─  ← ระดับ 50% = จุดเข้าที่เหมาะสม
                                          จุดที่มีโอกาสตอบสนองสูงสุด
    
    FVG Bottom: 1.1050 ─────────────  ← การ retrace ขั้นต่ำที่คาดหวัง
                                          (จุดเข้าแบบ aggressive ที่นี่)
                                          SL อยู่ใต้ระดับนี้

สามสไตล์การเข้า:
┌────────────────┬──────────────┬──────────────┬────────────────┐
│ สไตล์          │ ระดับเข้า    │ อัตราเข้าถึง  │ R:R            │
├────────────────┼──────────────┼──────────────┼────────────────┤
│ อนุรักษ์นิยม   │ FVG Bottom   │ ~80%         │ ต่ำกว่า (SL กว้าง)│
│ ปานกลาง       │ CE (50%)     │ ~65%         │ ปานกลาง        │
│ Aggressive     │ FVG Top      │ ~45%         │ สูงกว่า (SL แคบ)│
└────────────────┴──────────────┴──────────────┴────────────────┘
```

### 6.4 CE ที่สอดคล้องกับ OTE

เมื่อ CE ของ FVG สอดคล้องกับ Fibonacci retracement 62-79% (โซน OTE) โอกาสของการตอบสนองเพิ่มขึ้นอย่างมีนัยสำคัญ:

$$P(\text{reaction}) = P(\text{FVG}) \times P(\text{OTE}) \times \text{confluence\_multiplier}$$

ในทางปฏิบัติ ถ้า CE อยู่ในโซน Fib 62-79% ให้ถือว่าเป็น **setup พรีเมียม**

---

## 7. Breaker Blocks

### 7.1 คำจำกัดความ

**Breaker Block** คือ Order Block ที่ล้มเหลว เมื่อ Order Block (แท่งสุดท้ายก่อนการเคลื่อนไหว) ถูกละเมิดและราคาปิดทะลุผ่าน ฝั่ง ตรงข้ามของแท่งนั้นกลายเป็น Breaker Block — โซนที่มีโอกาสตอบสนองสูง

### 7.2 ลอจิกการก่อตัว

```
การก่อตัว BULLISH BREAKER BLOCK:
═════════════════════════════════

ขั้นตอน 1: Bearish Order Block ก่อตัว (แท่ง up-close สุดท้ายก่อนขาลง)
        ┌─────┐
        │  OB │  ← Bearish Order Block (แท่ง bullish สุดท้ายก่อนขายออก)
        │ (Up)│
        └──┬──┘
           │
           ╲
            ╲
             ╲  ราคาลง

ขั้นตอน 2: ราคาขึ้นกลับมาและ CLOSE ทะลุผ่าน OB → OB ล้มเหลว
        ┌─────┐
        │  OB │ ← ถูกทำลาย (ราคาปิดเหนือ)
        │XXXXX│
        └──┬──┘
           │╱────── ราคาทำลายขึ้น
          ╱│
         ╱

ขั้นตอน 3: ก้นของ OB ที่ถูกทำลายกลายเป็น BULLISH BREAKER BLOCK
        
        ──────────── จุดสูงสุด OB เดิม (สำคัญน้อยกว่า)
        
        ══════════════ BULLISH BREAKER BLOCK (จุดต่ำสุด OB เดิม) ← เทรดตรงนี้
        
        เมื่อราคากลับมาที่ระดับนี้ → เข้า LONG
```

```
การก่อตัว BEARISH BREAKER BLOCK:
═════════════════════════════════

ขั้นตอน 1: Bullish Order Block ก่อตัว (แท่ง down-close สุดท้ายก่อนขาขึ้น)
             ╱
            ╱
           ╱
        ┌──┴──┐
        │  OB │  ← Bullish Order Block (แท่ง bearish สุดท้ายก่อนขาขึ้น)
        │(Down)│
        └─────┘

ขั้นตอน 2: ราคาลงกลับมาและ CLOSE ทะลุผ่าน OB → OB ล้มเหลว
          ╲│
           ╲
        ┌──┬──┐
        │  OB │ ← ถูกทำลาย (ราคาปิดต่ำกว่า)
        │XXXXX│
        └─────┘

ขั้นตอน 3: ยอดของ OB ที่ถูกทำลายกลายเป็น BEARISH BREAKER BLOCK
        
        ══════════════ BEARISH BREAKER BLOCK (จุดสูงสุด OB เดิม) ← เทรดตรงนี้
        
        ──────────── จุดต่ำสุด OB เดิม (สำคัญน้อยกว่า)
        
        เมื่อราคากลับมาที่ระดับนี้ → เข้า SHORT
```

### 7.3 ทำไม Breaker Blocks ใช้ได้ผล

1. **เทรดเดอร์ติดกับดัก**: เทรดเดอร์ที่เข้าบน OB เดิมตอนนี้ขาดทุน Stop losses ของพวกเขาสร้างสภาพคล่อง
2. **แนวรับ/ต้านที่ล้มเหลว**: ระดับ S/R ที่ถูกทำลายมักกลายเป็นฝั่งตรงข้าม Breaker = S/R flip
3. **สถาบันเข้าใหม่**: สถาบันที่ทำให้เกิดการทำลายเดิมมักเข้าใหม่ที่ระดับที่ถูกทำลาย
4. **Self-fulfilling**: เทรดเดอร์ที่มีประสบการณ์จดจำรูปแบบและเพิ่ม confluence

### 7.4 อัลกอริทึมตรวจจับ Breaker Block

```python
def detect_breaker_blocks(candles: List[Candle], 
                          order_blocks: List[OrderBlock]) -> List[BreakerBlock]:
    """
    Detect breaker blocks from failed order blocks.
    
    Logic: An OB becomes a breaker when price closes through it.
    """
    breakers = []
    
    for ob in order_blocks:
        if ob.status != 'ACTIVE':
            continue
        
        for i in range(ob.candle_index + 1, len(candles)):
            candle = candles[i]
            
            if ob.type == 'BEARISH_OB':
                if candle.close > ob.high:
                    breakers.append(BreakerBlock(
                        type='BULLISH_BREAKER',
                        price_level=ob.low,
                        range_high=ob.high,
                        range_low=ob.low,
                        formed_timestamp=candle.timestamp,
                        formed_index=i,
                        original_ob=ob,
                        status='ACTIVE',
                        strength=calculate_breaker_strength(ob, candle, candles)
                    ))
                    ob.status = 'BROKEN'
                    break
            
            elif ob.type == 'BULLISH_OB':
                if candle.close < ob.low:
                    breakers.append(BreakerBlock(
                        type='BEARISH_BREAKER',
                        price_level=ob.high,
                        range_high=ob.high,
                        range_low=ob.low,
                        formed_timestamp=candle.timestamp,
                        formed_index=i,
                        original_ob=ob,
                        status='ACTIVE',
                        strength=calculate_breaker_strength(ob, candle, candles)
                    ))
                    ob.status = 'BROKEN'
                    break
    
    return breakers


def calculate_breaker_strength(ob: OrderBlock, break_candle: Candle, 
                                candles: List[Candle]) -> float:
    """
    Calculate the strength/quality of a breaker block.
    """
    body = abs(break_candle.close - break_candle.open)
    range_size = break_candle.high - break_candle.low
    body_ratio = body / range_size if range_size > 0 else 0
    
    avg_vol = np.mean([c.volume for c in candles[-20:]])
    vol_ratio = min(break_candle.volume / avg_vol, 3.0) / 3.0
    
    strength = 0.5 * body_ratio + 0.3 * vol_ratio + 0.2 * ob.strength
    
    return min(strength, 1.0)
```

### 7.5 การเทรด Breaker Blocks

| ประเภทการเข้า | เงื่อนไข | Stop Loss | เป้าหมาย |
|-----------|-----------|-----------|--------|
| Bullish Breaker | ราคา retrace ถึง breaker low | ใต้ breaker low (1-2 ATR) | Swing high ก่อนหน้าหรือ BSL ถัดไป |
| Bearish Breaker | ราคา retrace ถึง breaker high | เหนือ breaker high (1-2 ATR) | Swing low ก่อนหน้าหรือ SSL ถัดไป |
| Aggressive | เข้าที่ระดับ breaker ด้วย limit | Stop แคบ (50% ของช่วง breaker) | เป้าหมาย 3-5R |
| อนุรักษ์นิยม | รอยืนยัน LTF ที่ breaker | ใต้/เหนือ LTF swing | เป้าหมาย 2-3R |

---

## 8. Mitigation Blocks

### 8.1 คำจำกัดความ

**Mitigation Block** คือจุดกำเนิดของการเคลื่อนไหวที่สร้าง Order Block ซึ่งถูก mitigate (กลับมาถึง) ในภายหลัง มันแทนโซนที่สถาบันวางคำสั่งเดิม และที่พวกเขาอาจเพิ่มหรือจัดการสถานะ

### 8.2 ความแตกต่างจาก Order Blocks

| ลักษณะ | Order Block | Mitigation Block |
|---------|------------|-----------------|
| **การก่อตัว** | แท่งฝั่งตรงข้ามสุดท้ายก่อนการเคลื่อนไหว | จุดกำเนิดของการเคลื่อนไหว |
| **การแตะครั้งแรก** | คาดว่าจะตอบสนองหลัก | อาจถูกแตะไปแล้วครั้งหนึ่ง |
| **วัตถุประสงค์** | การสะสม/กระจายเบื้องต้น | การจัดการสถานะ, การเพิ่มสถานะ |
| **ความแข็งแรงหลังแตะ** | อ่อนลง (อาจกลายเป็น breaker) | ยังสามารถยืนในการแตะครั้งที่สอง |
| **ลำดับ ICT** | ลำดับสูงกว่าในการทดสอบครั้งแรก | ใช้เมื่อ OB ถูกทดสอบแล้ว |

### 8.3 การระบุ

```
การระบุ MITIGATION BLOCK:
═════════════════════════════════

1. ราคาเคลื่อนไหวสำคัญจากจุด A ถึงจุด B
2. การเคลื่อนไหวสร้าง Order Block ที่จุด A
3. ราคา retrace กลับไป OB ที่จุด A → OB "mitigated" (ถูกแตะ)
4. หลัง mitigation ราคาเคลื่อนไหวอีกครั้งจากจุด A ในทิศทางเดียวกัน
5. จุดต่ำสุดของ retracement ที่ mitigate OB = MITIGATION BLOCK

              จุด B
              ╱╲
             ╱  ╲
            ╱    ╲
           ╱      ╲   Retracement
  จุด A  ╱        ╲  ╱╲  ← กลับมาที่ OB
  (OB)  ─╱──────────╲╱──╲─── ← MITIGATION BLOCK (จุดต่ำสุดของ retracement)
                          ╲
                           ╲  ต่อเนื่อง
                            ╲

Mitigation Block คือจุดต่ำสุดที่แน่นอนของ retracement
ที่กลับมาทดสอบ Order Block เดิม
```

### 8.4 การเทรด Mitigation Blocks

การเข้าหลังจากการทดสอบครั้งที่สอง:
- การทดสอบ OB ครั้งแรก = เทรด OB มาตรฐาน
- ถ้าราคากลับมาอีกครั้ง (การทดสอบครั้งที่สอง) เข้าที่ระดับ Mitigation Block
- นี่แทนจุดเข้าครั้งที่สองของสถาบัน
- มักรวมกับ FVG/OTE เพื่อความแม่นยำ

---

## 9. โซนจุดเข้าเทรดที่เหมาะสม (Optimal Trade Entry - OTE)

### 9.1 คำจำกัดความ

โซน **Optimal Trade Entry (OTE)** คือระดับ Fibonacci retracement 62%-79% ของ swing ราคาที่สำคัญ วิธีการ ICT ระบุว่านี่คือโซนที่มีโอกาสสูงสุดสำหรับการเข้าใหม่ของสถาบันระหว่าง retracement

### 9.2 การคำนวณ OTE

สำหรับ OTE ขาขึ้น (ซื้อ retracement ในขาขึ้น):

$$\text{OTE}_{bottom} = \text{Swing High} - 0.79 \times (\text{Swing High} - \text{Swing Low})$$
$$\text{OTE}_{top} = \text{Swing High} - 0.62 \times (\text{Swing High} - \text{Swing Low})$$

สำหรับ OTE ขาลง (ขาย retracement ในขาลง):

$$\text{OTE}_{top} = \text{Swing Low} + 0.79 \times (\text{Swing High} - \text{Swing Low})$$
$$\text{OTE}_{bottom} = \text{Swing Low} + 0.62 \times (\text{Swing High} - \text{Swing Low})$$

### 9.3 ภาพ OTE

```
BULLISH OTE (ซื้อตอน pullback):
═══════════════════════════════════

    Swing High ─── 1.1100 ──── 0% Fib
         │
         │    ──── 1.1076 ──── 23.6% Fib
         │
         │    ──── 1.1062 ──── 38.2% Fib (เริ่มโซน discount)
         │
         │    ──── 1.1050 ──── 50% Fib (จุดสมดุล)
         │
         │    ════ 1.1038 ════ 62% Fib  ┐
         │    ║                  ║      │  โซน OTE
         │    ║   OPTIMAL TRADE  ║      │  (62% - 79%)
         │    ║   ENTRY ZONE     ║      │
         │    ════ 1.1021 ════ 79% Fib  ┘  ← จุดเข้าที่ดีที่สุด
         │
         │    ──── 1.1000 ──── 100% Fib (swing low)
         │
    Swing Low ─── 1.1000
    
    จุดเข้า: Limit buy ที่ 1.1021-1.1038
    Stop Loss: ใต้ Swing Low (1.1000) หรือใต้ 79% (1.1021)
    เป้าหมาย: เหนือ Swing High (1.1100) หรือ BSL ถัดไป
```

### 9.4 OTE พร้อม Confluence

โซน OTE กลายเป็น **setup พรีเมียม** เมื่อสอดคล้องกับ:

| ปัจจัย Confluence | คำอธิบาย | ตัวคูณความแข็งแรง |
|-------------------|-------------|-------------------|
| FVG ภายใน OTE | Fair Value Gap อยู่ภายในโซน OTE | 1.5x |
| Order Block ที่ OTE | OB อยู่ที่ระดับ OTE | 1.4x |
| Breaker ที่ OTE | Breaker Block ตรงกับ OTE | 1.3x |
| โซน S/D HTF ที่ OTE | Supply/Demand ของ timeframe สูงกว่าที่ OTE | 1.5x |
| Volume node ที่ OTE | High volume node จาก volume profile | 1.2x |
| ระดับจิตวิทยาที่ OTE | ตัวเลขกลมๆ ภายใน OTE | 1.1x |

### 9.5 อัลกอริทึมตรวจจับ OTE

```python
def find_ote_zones(candles: List[Candle], config: dict) -> List[OTEZone]:
    """
    Find Optimal Trade Entry zones based on significant swings.
    """
    ote_zones = []
    swing_lookback = config.get('swing_lookback', 10)
    min_swing_size_atr = config.get('min_swing_size_atr', 2.0)
    
    atr = calculate_atr(candles, period=14)
    
    swings = find_significant_swings(candles, swing_lookback, min_swing_size_atr, atr)
    
    for i in range(1, len(swings)):
        prev_swing = swings[i-1]
        curr_swing = swings[i]
        
        swing_range = abs(curr_swing['price'] - prev_swing['price'])
        
        if swing_range < min_swing_size_atr * atr[curr_swing['index']]:
            continue
        
        if prev_swing['type'] == 'LOW' and curr_swing['type'] == 'HIGH':
            ote_top = curr_swing['price'] - 0.62 * swing_range
            ote_bottom = curr_swing['price'] - 0.79 * swing_range
            
            ote_zones.append(OTEZone(
                type='BULLISH_OTE',
                zone_high=ote_top,
                zone_low=ote_bottom,
                swing_high=curr_swing['price'],
                swing_low=prev_swing['price'],
                swing_range=swing_range,
                formed_timestamp=curr_swing['timestamp'],
                ce_level=(ote_top + ote_bottom) / 2,
                status='ACTIVE'
            ))
        
        elif prev_swing['type'] == 'HIGH' and curr_swing['type'] == 'LOW':
            ote_bottom = curr_swing['price'] + 0.62 * swing_range
            ote_top = curr_swing['price'] + 0.79 * swing_range
            
            ote_zones.append(OTEZone(
                type='BEARISH_OTE',
                zone_high=ote_top,
                zone_low=ote_bottom,
                swing_high=prev_swing['price'],
                swing_low=curr_swing['price'],
                swing_range=swing_range,
                formed_timestamp=curr_swing['timestamp'],
                ce_level=(ote_top + ote_bottom) / 2,
                status='ACTIVE'
            ))
    
    return ote_zones
```

---

## 10. กรอบทางคณิตศาสตร์สำหรับการระบุโซนสภาพคล่อง

### 10.1 ฟังก์ชันความหนาแน่นสภาพคล่อง (Liquidity Density Function)

กำหนดความหนาแน่นสภาพคล่องที่ราคา $P$ เป็น:

$$L(P) = \sum_{i=1}^{N} w_i \cdot K\left(\frac{P - P_i}{h}\right)$$

โดยที่:
- $P_i$ = ราคาของ swing high/low ที่ $i$
- $w_i$ = น้ำหนักตามความสำคัญ (timeframe, จำนวนแตะ, ความใหม่)
- $K$ = ฟังก์ชัน Kernel (Gaussian: $K(x) = \frac{1}{\sqrt{2\pi}} e^{-x^2/2}$)
- $h$ = Bandwidth (ควบคุมการ smoothing)

สิ่งนี้สร้าง "liquidity profile" ที่เรียบ แสดงว่า stop orders มีแนวโน้มรวมตัวที่ไหน

### 10.2 คะแนนความน่าดึงดูดของสภาพคล่อง (Liquidity Attractiveness Score)

ความน่าจะเป็นที่ราคาเล็งเป้า liquidity pool เฉพาะ:

$$A(pool) = \frac{L(pool) \cdot D(pool)^{-\beta} \cdot T(pool)^{\gamma}}{\sum_{j} L(j) \cdot D(j)^{-\beta} \cdot T(j)^{\gamma}}$$

โดยที่:
- $L(pool)$ = สภาพคล่องโดยประมาณที่ pool
- $D(pool)$ = ระยะจากราคาปัจจุบันถึง pool
- $T(pool)$ = เวลาตั้งแต่ pool ถูก "แตะ" ครั้งล่าสุด
- $\beta > 0$ = พารามิเตอร์ลดตามระยะ (pool ใกล้กว่ามีโอกาสมากกว่า)
- $\gamma > 0$ = พารามิเตอร์เพิ่มตามความเก่า (pool เก่าที่ยังไม่ถูกทดสอบน่าดึงดูดกว่า)

### 10.3 ความน่าจะเป็นของ FVG ที่ถูก Fill

จากข้อมูลเชิงประจักษ์ ความน่าจะเป็นที่ FVG จะถูก fill (ราคากลับมาถึง):

$$P(\text{fill} | \text{FVG}) = 1 - e^{-\lambda \cdot t}$$

โดยที่:
- $\lambda$ = พารามิเตอร์อัตรา fill (ประมาณจากข้อมูลอดีต โดยทั่วไป 0.02-0.05 ต่อแท่ง)
- $t$ = จำนวนแท่งนับตั้งแต่ FVG ก่อตัว

หมายความว่า:
- หลัง 20 แท่ง: ความน่าจะเป็น fill ~33-63%
- หลัง 50 แท่ง: ความน่าจะเป็น fill ~63-92%
- หลัง 100 แท่ง: ความน่าจะเป็น fill ~86-99%

**FVG ส่วนใหญ่ในที่สุดจะถูก fill** — คำถามคือเมื่อไหร่ และทิศทางเทรนด์กำหนดว่ามันให้โอกาสเทรดหรือไม่

### 10.4 แบบจำลองสภาพคล่องหลายปัจจัย (Multi-Factor Liquidity Model)

รวมแนวคิดสภาพคล่องทั้งหมดเป็นแบบจำลองการให้คะแนนรวม:

$$S_{liquidity}(P, t) = w_1 \cdot \text{BSL}(P) + w_2 \cdot \text{SSL}(P) + w_3 \cdot \text{FVG}(P, t) + w_4 \cdot \text{Breaker}(P) + w_5 \cdot \text{OTE}(P)$$

โดยที่แต่ละองค์ประกอบถูกปรับมาตรฐานเป็น [0, 1] และน้ำหนักรวมเป็น 1

**น้ำหนักเริ่มต้น:**

| องค์ประกอบ | น้ำหนัก | เหตุผล |
|-----------|--------|-----------|
| BSL/SSL | 0.30 | สภาพคล่องภายนอกเป็นแรงดึงดูดหลัก |
| FVG | 0.25 | สภาพคล่องภายใน (การปรับสมดุล) |
| Order Block / Breaker | 0.20 | โซน S/D ของสถาบัน |
| OTE | 0.15 | Confluence ของ Fibonacci |
| Volume Profile | 0.10 | ข้อมูลที่ตลาดสร้างขึ้น |

---

## 11. อัลกอริทึมสำหรับตรวจจับ FVG แบบโปรแกรม

### 11.1 เครื่องยนต์ตรวจจับ FVG แบบสมบูรณ์

```python
from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum
import numpy as np

class FVGType(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"

class FVGStatus(Enum):
    ACTIVE = "ACTIVE"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    INVALIDATED = "INVALIDATED"

@dataclass
class FairValueGap:
    type: FVGType
    top: float
    bottom: float
    ce_level: float
    candle1_index: int
    candle2_index: int
    candle3_index: int
    timestamp: float
    timeframe: str
    gap_size: float
    gap_size_pct: float
    displacement_volume: float
    displacement_delta: float
    strength: float
    status: FVGStatus
    fill_percentage: float
    
    @property
    def is_tradeable(self) -> bool:
        return self.status in (FVGStatus.ACTIVE, FVGStatus.PARTIALLY_FILLED)


class FVGDetector:
    """
    Comprehensive Fair Value Gap detection and tracking engine.
    """
    
    def __init__(self, config: dict):
        self.min_gap_atr_ratio = config.get('min_gap_atr_ratio', 0.5)
        self.volume_weight = config.get('fvg_volume_weight', 0.35)
        self.delta_weight = config.get('fvg_delta_weight', 0.35)
        self.size_weight = config.get('fvg_size_weight', 0.30)
        self.max_active_fvgs = config.get('max_active_fvgs', 50)
        self.timeframe = config.get('timeframe', '1H')
        
        self.active_fvgs: List[FairValueGap] = []
        self.filled_fvgs: List[FairValueGap] = []
    
    def scan(self, candles: List['Candle']) -> List[FairValueGap]:
        """Scan candle data for all FVGs."""
        if len(candles) < 3:
            return []
        
        fvgs = []
        atr = self._calculate_atr(candles, period=14)
        avg_volume = np.mean([c.volume for c in candles[-50:]]) if len(candles) >= 50 else np.mean([c.volume for c in candles])
        avg_delta = np.mean([abs(c.delta) for c in candles[-50:]]) if hasattr(candles[0], 'delta') else 1.0
        
        for i in range(2, len(candles)):
            c1 = candles[i-2]
            c2 = candles[i-1]
            c3 = candles[i]
            
            current_atr = atr[i] if i < len(atr) else atr[-1]
            
            # CHECK FOR BULLISH FVG
            if c3.low > c1.high:
                gap_size = c3.low - c1.high
                
                if gap_size >= current_atr * self.min_gap_atr_ratio:
                    strength = self._calc_fvg_strength(
                        c2=c2, gap_size=gap_size, atr=current_atr,
                        avg_volume=avg_volume, avg_delta=avg_delta,
                        direction='BULLISH'
                    )
                    
                    fvg = FairValueGap(
                        type=FVGType.BULLISH, top=c3.low, bottom=c1.high,
                        ce_level=(c3.low + c1.high) / 2,
                        candle1_index=i-2, candle2_index=i-1, candle3_index=i,
                        timestamp=c3.timestamp, timeframe=self.timeframe,
                        gap_size=gap_size,
                        gap_size_pct=(gap_size / c2.close) * 100,
                        displacement_volume=c2.volume,
                        displacement_delta=getattr(c2, 'delta', 0),
                        strength=strength, status=FVGStatus.ACTIVE,
                        fill_percentage=0.0
                    )
                    fvgs.append(fvg)
            
            # CHECK FOR BEARISH FVG
            if c3.high < c1.low:
                gap_size = c1.low - c3.high
                
                if gap_size >= current_atr * self.min_gap_atr_ratio:
                    strength = self._calc_fvg_strength(
                        c2=c2, gap_size=gap_size, atr=current_atr,
                        avg_volume=avg_volume, avg_delta=avg_delta,
                        direction='BEARISH'
                    )
                    
                    fvg = FairValueGap(
                        type=FVGType.BEARISH, top=c1.low, bottom=c3.high,
                        ce_level=(c1.low + c3.high) / 2,
                        candle1_index=i-2, candle2_index=i-1, candle3_index=i,
                        timestamp=c3.timestamp, timeframe=self.timeframe,
                        gap_size=gap_size,
                        gap_size_pct=(gap_size / c2.close) * 100,
                        displacement_volume=c2.volume,
                        displacement_delta=getattr(c2, 'delta', 0),
                        strength=strength, status=FVGStatus.ACTIVE,
                        fill_percentage=0.0
                    )
                    fvgs.append(fvg)
        
        self.active_fvgs.extend(fvgs)
        self._prune_active_fvgs()
        
        return fvgs
    
    def update(self, candle: 'Candle'):
        """Update FVG statuses based on new price action."""
        for fvg in self.active_fvgs[:]:
            if fvg.type == FVGType.BULLISH:
                self._update_bullish_fvg(fvg, candle)
            else:
                self._update_bearish_fvg(fvg, candle)
    
    def _update_bullish_fvg(self, fvg: FairValueGap, candle: 'Candle'):
        """Update a bullish FVG based on new candle data."""
        if candle.low <= fvg.top:
            if candle.low <= fvg.bottom:
                if candle.close < fvg.bottom:
                    fvg.status = FVGStatus.INVALIDATED
                    fvg.fill_percentage = 1.0
                    self.active_fvgs.remove(fvg)
                    self.filled_fvgs.append(fvg)
                else:
                    fvg.status = FVGStatus.FILLED
                    fvg.fill_percentage = 1.0
            elif candle.low <= fvg.ce_level:
                fvg.status = FVGStatus.PARTIALLY_FILLED
                fill = (fvg.top - candle.low) / fvg.gap_size
                fvg.fill_percentage = max(fvg.fill_percentage, fill)
            else:
                fvg.status = FVGStatus.PARTIALLY_FILLED
                fill = (fvg.top - candle.low) / fvg.gap_size
                fvg.fill_percentage = max(fvg.fill_percentage, fill)
    
    def _update_bearish_fvg(self, fvg: FairValueGap, candle: 'Candle'):
        """Update a bearish FVG based on new candle data."""
        if candle.high >= fvg.bottom:
            if candle.high >= fvg.top:
                if candle.close > fvg.top:
                    fvg.status = FVGStatus.INVALIDATED
                    fvg.fill_percentage = 1.0
                    self.active_fvgs.remove(fvg)
                    self.filled_fvgs.append(fvg)
                else:
                    fvg.status = FVGStatus.FILLED
                    fvg.fill_percentage = 1.0
            elif candle.high >= fvg.ce_level:
                fvg.status = FVGStatus.PARTIALLY_FILLED
                fill = (candle.high - fvg.bottom) / fvg.gap_size
                fvg.fill_percentage = max(fvg.fill_percentage, fill)
            else:
                fvg.status = FVGStatus.PARTIALLY_FILLED
                fill = (candle.high - fvg.bottom) / fvg.gap_size
                fvg.fill_percentage = max(fvg.fill_percentage, fill)
    
    def _calc_fvg_strength(self, c2, gap_size, atr, avg_volume, avg_delta, direction) -> float:
        """Calculate FVG quality/strength score."""
        vol_ratio = c2.volume / avg_volume if avg_volume > 0 else 1.0
        vol_score = min(vol_ratio / 3.0, 1.0)
        
        delta = getattr(c2, 'delta', 0)
        if avg_delta > 0:
            delta_ratio = delta / avg_delta
            if direction == 'BULLISH':
                delta_score = min(max(delta_ratio, 0) / 3.0, 1.0)
            else:
                delta_score = min(max(-delta_ratio, 0) / 3.0, 1.0)
        else:
            delta_score = 0.5
        
        size_ratio = gap_size / atr if atr > 0 else 1.0
        size_score = min(size_ratio / 3.0, 1.0)
        
        strength = (
            self.volume_weight * vol_score +
            self.delta_weight * delta_score +
            self.size_weight * size_score
        )
        
        return round(strength, 4)
    
    def _calculate_atr(self, candles: List['Candle'], period: int = 14) -> np.ndarray:
        """Calculate Average True Range."""
        if len(candles) < 2:
            return np.array([0.0])
        
        trs = []
        for i in range(1, len(candles)):
            tr = max(
                candles[i].high - candles[i].low,
                abs(candles[i].high - candles[i-1].close),
                abs(candles[i].low - candles[i-1].close)
            )
            trs.append(tr)
        
        trs = np.array([trs[0]] + trs)
        
        atr = np.zeros(len(trs))
        atr[0] = trs[0]
        alpha = 2 / (period + 1)
        
        for i in range(1, len(trs)):
            atr[i] = alpha * trs[i] + (1 - alpha) * atr[i-1]
        
        return atr
    
    def _prune_active_fvgs(self):
        """Keep only the most recent/strongest FVGs to prevent memory bloat."""
        if len(self.active_fvgs) > self.max_active_fvgs:
            self.active_fvgs.sort(key=lambda f: f.strength, reverse=True)
            removed = self.active_fvgs[self.max_active_fvgs:]
            self.active_fvgs = self.active_fvgs[:self.max_active_fvgs]
            self.filled_fvgs.extend(removed)
    
    # === Public API ===
    
    def get_active_bullish_fvgs(self, current_price: float) -> List[FairValueGap]:
        """Get active bullish FVGs below current price (tradeable for longs)."""
        return [
            fvg for fvg in self.active_fvgs
            if fvg.type == FVGType.BULLISH 
            and fvg.is_tradeable 
            and fvg.top <= current_price
        ]
    
    def get_active_bearish_fvgs(self, current_price: float) -> List[FairValueGap]:
        """Get active bearish FVGs above current price (tradeable for shorts)."""
        return [
            fvg for fvg in self.active_fvgs
            if fvg.type == FVGType.BEARISH 
            and fvg.is_tradeable 
            and fvg.bottom >= current_price
        ]
    
    def get_nearest_fvg(self, current_price: float, direction: str) -> Optional[FairValueGap]:
        """Get the nearest tradeable FVG in the specified direction."""
        if direction == 'LONG':
            fvgs = self.get_active_bullish_fvgs(current_price)
            if fvgs:
                return min(fvgs, key=lambda f: current_price - f.ce_level)
        elif direction == 'SHORT':
            fvgs = self.get_active_bearish_fvgs(current_price)
            if fvgs:
                return min(fvgs, key=lambda f: f.ce_level - current_price)
        return None
```

---

## 12. ลอจิกหลัก — จุดเข้า/ออก (Entry/Exit)

### 12.1 ตารางสรุปการเข้า/ออก

| Setup | จุดเข้า | Stop Loss | TP1 | TP2 | R:R ขั้นต่ำ |
|-------|-------|-----------|-----|-----|---------|
| FVG Long | ที่ CE หรือ FVG bottom | ใต้ FVG (buffer 1 ATR) | Swing high ก่อนหน้า | BSL ถัดไป | 2:1 |
| FVG Short | ที่ CE หรือ FVG top | เหนือ FVG (buffer 1 ATR) | Swing low ก่อนหน้า | SSL ถัดไป | 2:1 |
| OTE Long | ภายในโซน 62-79% | ใต้ swing low | Swing high | Extension -27% | 3:1 |
| OTE Short | ภายในโซน 62-79% | เหนือ swing high | Swing low | Extension -27% | 3:1 |
| Breaker Long | ที่ระดับ breaker | ใต้ช่วง breaker | High ก่อนหน้า | BSL ถัดไป | 2.5:1 |
| Breaker Short | ที่ระดับ breaker | เหนือช่วง breaker | Low ก่อนหน้า | SSL ถัดไป | 2.5:1 |
| SSL Sweep Long | หลังยืนยัน sweep | ใต้ sweep low | High ก่อนหน้า | สภาพคล่องตรงข้าม | 3:1 |
| BSL Sweep Short | หลังยืนยัน sweep | เหนือ sweep high | Low ก่อนหน้า | สภาพคล่องตรงข้าม | 3:1 |

---

## 13. ข้อกำหนดทางเทคนิค

### 13.1 พารามิเตอร์การตรวจจับ

| พารามิเตอร์ | ค่าเริ่มต้น | ช่วง | คำอธิบาย |
|-----------|---------|-------|-------------|
| `swing_lookback` | 5 | [3, 20] | จำนวนแท่งเพื่อยืนยัน swing H/L |
| `equal_high_tolerance_pct` | 0.05 | [0.01, 0.20] | % ความคลาดเคลื่อนสำหรับ equal highs |
| `equal_low_tolerance_pct` | 0.05 | [0.01, 0.20] | % ความคลาดเคลื่อนสำหรับ equal lows |
| `min_gap_atr_ratio` | 0.5 | [0.2, 2.0] | ขนาด FVG ขั้นต่ำเทียบกับ ATR |
| `fvg_volume_weight` | 0.35 | [0.1, 0.5] | น้ำหนักปริมาณในความแข็งแรง FVG |
| `min_confluence_score` | 0.6 | [0.4, 0.9] | คะแนนขั้นต่ำสำหรับเข้าเทรด |
| `ote_fib_high` | 0.79 | [0.75, 0.85] | ขอบบนของ OTE |
| `ote_fib_low` | 0.62 | [0.55, 0.65] | ขอบล่างของ OTE |
| `breaker_min_strength` | 0.5 | [0.3, 0.8] | คุณภาพ breaker ขั้นต่ำ |
| `max_active_fvgs` | 50 | [20, 200] | จำนวน FVG สูงสุดที่ติดตามพร้อมกัน |

### 13.2 ลำดับชั้น Timeframe

| Timeframe | การใช้งาน | ความเกี่ยวข้องของ FVG | ความสำคัญของ Liquidity Pool |
|-----------|-----|---------------|---------------------------|
| รายเดือน | อคติทิศทาง | FVG หลัก (ยืนหลายสัปดาห์) | Pool พรีเมียม |
| รายสัปดาห์ | ทิศทาง swing | FVG แข็งแรง (ยืนหลายวัน) | สำคัญสูง |
| รายวัน | ทิศทางเข้า | FVG ปานกลาง (ยืนหลายชั่วโมง) | สำคัญปานกลาง |
| 4H | จังหวะเข้า | FVG ระยะสั้น | มาตรฐาน |
| 1H | เข้าแม่นยำ | FVG เร็ว (intraday) | ต่ำกว่า |
| 15M | Scalp entries | Micro FVG | ต่ำสุด |

---

## 14. พารามิเตอร์ความเสี่ยง

### 14.1 ความเสี่ยงต่อเทรดตามคุณภาพ Setup

| คะแนน Confluence | ความเสี่ยง % | ตัวคูณขนาดสถานะ |
|-----------------|--------|-------------------------|
| 0.9+ (พรีเมียม) | 2.0% | 1.5x |
| 0.7-0.9 (แข็งแรง) | 1.5% | 1.0x |
| 0.6-0.7 (ปานกลาง) | 1.0% | 0.75x |
| <0.6 (อ่อน) | ไม่เทรด | 0x |

### 14.2 กฎ Stop Loss

1. **เทรด FVG**: SL ใต้/เหนือขอบ FVG + buffer 0.5 ATR
2. **เทรด OTE**: SL ใต้/เหนือ swing ที่กำหนด OTE
3. **เทรด Breaker**: SL เลยช่วง breaker + buffer 1 ATR
4. **เทรด Sweep**: SL เลยจุดสุดขีดของ sweep + buffer spread

### 14.3 การแบ่ง Take Profit

```
การจัดการสถานะ:
- TP1 (33% ของสถานะ): R:R 1:1 → ย้าย SL เป็น breakeven
- TP2 (33% ของสถานะ): R:R 2:1 → Trail stop
- TP3 (34% ของสถานะ): ปล่อยวิ่งถึงเป้าสภาพคล่องพร้อม trailing stop
```

---

## 15. ขั้นตอนการทำงาน — Pseudocode

```python
async def liquidity_trading_loop(config, data_feed, executor):
    """
    Main loop for liquidity-based trading strategy.
    """
    # Initialize
    fvg_detector = FVGDetector(config)
    liquidity_mapper = LiquidityMapper(config)
    breaker_detector = BreakerDetector(config)
    ote_finder = OTEFinder(config)
    risk_mgr = RiskManager(config)
    
    candle_stores = {
        '1D': CandleStore('1D'),
        '4H': CandleStore('4H'),
        '1H': CandleStore('1H'),
        '15M': CandleStore('15M'),
    }
    
    async for tick in data_feed:
        for tf, store in candle_stores.items():
            new_candle = store.update(tick)
            if new_candle:
                fvg_detector.scan(store.candles)
                fvg_detector.update(new_candle)
        
        current_price = tick.price
        
        # 1. DETERMINE HTF BIAS (Daily)
        htf_bias = determine_bias(candle_stores['1D'].candles)
        
        # 2. MAP LIQUIDITY (4H)
        bsl_pools = liquidity_mapper.detect_bsl(candle_stores['4H'].candles)
        ssl_pools = liquidity_mapper.detect_ssl(candle_stores['4H'].candles)
        
        # 3. IDENTIFY ENTRY CONCEPTS (1H)
        active_fvgs = fvg_detector.active_fvgs
        active_breakers = breaker_detector.get_active_breakers()
        ote_zones = ote_finder.find_ote_zones(candle_stores['1H'].candles)
        
        # 4. CHECK IF PRICE IS AT A CONCEPT LEVEL (15M for precision)
        if htf_bias == 'BULLISH':
            entry = evaluate_long_entry(
                current_price, active_fvgs, ote_zones, 
                active_breakers, ssl_pools, candle_stores['15M'].candles
            )
        elif htf_bias == 'BEARISH':
            entry = evaluate_short_entry(
                current_price, active_fvgs, ote_zones,
                active_breakers, bsl_pools, candle_stores['15M'].candles
            )
        else:
            entry = None
        
        # 5. EXECUTE IF VALID
        if entry and entry['risk_reward'] >= config['min_rr']:
            if risk_mgr.can_open_position():
                size = risk_mgr.calculate_size(
                    entry=entry['entry'],
                    stop=entry['stop_loss']
                )
                await executor.submit_order(
                    side='BUY' if entry['direction'] == 'LONG' else 'SELL',
                    size=size,
                    entry_price=entry['entry'],
                    stop_loss=entry['stop_loss'],
                    take_profit=entry['take_profit'],
                    metadata=entry
                )
```

---

## 16. เอกสารอ้างอิง

### วิชาการและทฤษฎี

1. **Kyle, A. S.** (1985). "Continuous Auctions and Insider Trading." *Econometrica*. — การเทรดข้อมูลภายในและสภาพคล่อง

2. **O'Hara, M.** (1995). *Market Microstructure Theory*. Blackwell. — วิธีที่สภาพคล่องถูกจัดหาและใช้ไป

3. **Glosten, L. R., & Milgrom, P. R.** (1985). "Bid, Ask and Transaction Prices in a Specialist Market." *JFE*. — Adverse selection และสภาพคล่อง

4. **Amihud, Y.** (2002). "Illiquidity and Stock Returns: Cross-Section and Time-Series Effects." *Journal of Financial Markets*. — Illiquidity premium

5. **Easley, D., & O'Hara, M.** (1987). "Price, Trade Size, and Information in Securities Markets." *JFE*. — เนื้อหาข้อมูลของการเทรด

6. **Bouchaud, J. P., et al.** (2009). "How Markets Slowly Digest Changes in Supply and Demand." — ผลกระทบต่อราคาและสภาพคล่อง

### วิธีการ ICT และผู้ปฏิบัติ

7. **ICT (Inner Circle Trader)** — ผลงานครบถ้วนเกี่ยวกับ:
   - สภาพคล่องฝั่งซื้อและฝั่งขาย (Buy-side and sell-side liquidity)
   - Fair Value Gaps
   - Optimal Trade Entry
   - Breaker Blocks
   - Mitigation Blocks
   - Consequent Encroachment
   - Kill Zones และจังหวะสถาบัน

8. **Smart Money Concepts (SMC)** — การขยายแนวคิด ICT ที่พัฒนาโดยชุมชน ประยุกต์ใช้กับ crypto และตลาดสมัยใหม่

9. **Wyckoff, R. D.** (1931). *The Richard D. Wyckoff Method of Trading and Investing in Stocks*. — กรอบการสะสม/กระจายของสถาบันดั้งเดิม

10. **Dalton, J. F.** (1993). *Mind Over Markets*. — ทฤษฎี Auction Market และแนวคิด value area

### ข้อมูลและเครื่องมือ

11. **TradingView** — เอกสาร Pine Script สำหรับการตรวจจับ FVG และสภาพคล่อง
12. **ATAS Platform** — เอกสาร order flow และ footprint chart
13. **Exocharts** — เครื่องมือแสดงผลสภาพคล่องและ FVG เฉพาะ crypto

---

> **เอกสารก่อนหน้า**: [01_order_book_analysis.md](./01_order_book_analysis.md) — ข้อมูล Level 2 และการวิเคราะห์ order book
> **เอกสารถัดไป**: [03_hft_stop_hunting.md](./03_hft_stop_hunting.md) — อัลกอริทึม HFT และกลไกการล่า stop ของสถาบัน
