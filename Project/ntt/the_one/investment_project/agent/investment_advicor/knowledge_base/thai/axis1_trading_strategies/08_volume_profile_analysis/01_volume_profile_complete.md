# Volume Profile และ Market Profile — คู่มือฉบับสมบูรณ์

## ข้อมูลเอกสาร (Document Metadata)
| ฟิลด์ | ค่า |
|---|---|
| **รหัสกลยุทธ์ (Strategy ID)** | VP-001 |
| **หมวดหมู่ (Category)** | ทฤษฎีตลาดประมูล / การวิเคราะห์ปริมาณ (Auction Market Theory / Volume Analysis) |
| **ประเภทสินทรัพย์ (Asset Classes)** | Forex, Crypto, หุ้น (Equities), ฟิวเจอร์ส (Futures) |
| **กรอบเวลา (Timeframes)** | ภายในวัน ถึง Monthly (หลัก: รายเซสชัน, Daily, Weekly) |
| **ความซับซ้อน (Complexity)** | ขั้นสูง (Advanced) |
| **ความเหมาะสมกับ AI** | สูงมาก — การวิเคราะห์การกระจายทางสถิติ |
| **เวอร์ชัน** | 2.0 |
| **อัปเดตล่าสุด** | 2026-04-12 |

---

## สารบัญ
1. [บทนำ](#1-บทนำ)
2. [พื้นฐานทฤษฎีตลาดประมูล](#2-พื้นฐานทฤษฎีตลาดประมูล)
3. [แนวคิด Volume Profile](#3-แนวคิด-volume-profile)
4. [Market Profile (TPO Charts)](#4-market-profile-tpo-charts)
5. [Initial Balance](#5-initial-balance)
6. [Single Prints](#6-single-prints)
7. [Poor Highs และ Lows](#7-poor-highs-และ-lows)
8. [กลยุทธ์การเทรดด้วย Volume Profile](#8-กลยุทธ์การเทรดด้วย-volume-profile)
9. [สูตรทางคณิตศาสตร์](#9-สูตรทางคณิตศาสตร์)
10. [ขั้นตอนการดำเนินงานสำหรับ AI](#10-ขั้นตอนการดำเนินงานสำหรับ-ai)
11. [พารามิเตอร์ความเสี่ยง](#11-พารามิเตอร์ความเสี่ยง)
12. [เทคนิคขั้นสูง](#12-เทคนิคขั้นสูง)
13. [หมายเหตุการใช้งาน AI](#13-หมายเหตุการใช้งาน-ai)
14. [อ้างอิง](#14-อ้างอิง)

---

## 1. บทนำ

Volume Profile และ Market Profile เป็นกรอบการวิเคราะห์ที่มีรากฐานจากทฤษฎีตลาดประมูล (Auction Market Theory - AMT) ซึ่งแสดงการกระจายตัวของปริมาณ (หรือเวลา) ที่แต่ละระดับราคา เปิดเผยว่าตลาดยอมรับมูลค่า ณ ที่ใด และปฏิเสธราคา ณ ที่ใด ให้มุมมองที่เป็นเอกลักษณ์เกี่ยวกับกิจกรรมสถาบันและความสมดุลของตลาด

### 1.1 แนวคิดหลัก (Core Thesis)

- ตลาดเป็นการประมูลแบบสองทาง (Two-way Auction) ระหว่างผู้ซื้อและผู้ขาย
- ราคาจะสำรวจทั้งสองทิศทางจนกว่าจะพบระดับที่ทั้งสองฝ่ายเห็นด้วยที่จะซื้อขาย (มูลค่ายุติธรรม / Fair Value)
- พื้นที่ที่มีปริมาณสูงแสดงถึง**มูลค่าที่ได้รับการยอมรับ** — ระดับราคายุติธรรม
- พื้นที่ที่มีปริมาณต่ำแสดงถึง**ราคาที่ถูกปฏิเสธ** — โซนไม่สมดุล
- ราคามีแนวโน้มถูกดึงดูดไปหาพื้นที่ปริมาณสูง (มูลค่า) และถูกผลักออกจากพื้นที่ปริมาณต่ำ

### 1.2 Volume Profile เทียบกับ Volume แบบดั้งเดิม

| คุณลักษณะ | Volume แบบดั้งเดิม | Volume Profile |
|---------|-------------------|---------------|
| **การแสดงผล** | ปริมาณต่อช่วงเวลา (แผนภูมิแท่งใต้ราคา) | ปริมาณต่อระดับราคา (ฮิสโตแกรมแนวนอน) |
| **ข้อมูล** | มีการซื้อขายเท่าไรในช่วงเวลา | ปริมาณกระจุกที่ราคาใด |
| **การใช้งาน** | ยืนยันการเคลื่อนไหว | ระบุมูลค่ายุติธรรม, S/R |
| **ความละเอียด** | ตามเวลา | ตามราคา |

---

## 2. พื้นฐานทฤษฎีตลาดประมูล (Auction Market Theory Foundations)

### 2.1 กระบวนการประมูล (The Auction Process)

ตลาดทำงานเป็นการประมูลคู่แบบต่อเนื่อง:
1. ราคาเคลื่อนขึ้นเพื่อหาผู้ขาย (แนวต้านต่อราคาที่สูงขึ้น)
2. ราคาเคลื่อนลงเพื่อหาผู้ซื้อ (แนวต้านต่อราคาที่ต่ำลง)
3. ช่วงที่ทั้งสองฝ่ายพึงพอใจ = **พื้นที่มูลค่า (Value Area)**

### 2.2 สถานะตลาด (Market States)

| สถานะ | ลักษณะ | ลายเซ็น VP |
|-------|----------------|--------------|
| **สมดุล (Balance)** | ราคาหมุนเวียนภายในช่วง; VP รูประฆัง | พื้นที่มูลค่าแคบ, โปรไฟล์สมมาตร |
| **ไม่สมดุล (Imbalance)** | เป็นแนวโน้ม; ราคาเคลื่อนในทิศทางเดียว | โปรไฟล์เบ้, รูปร่างยาว |
| **เปลี่ยนผ่าน (Transition)** | กำลังเปลี่ยนจากสมดุลเป็นไม่สมดุลหรือกลับกัน | POC หลายจุด, โปรไฟล์รูป p หรือ b |

### 2.3 รูปร่างโปรไฟล์ (Profile Shapes)

| รูปร่าง | คำอธิบาย | นัยยะ |
|-------|-------------|-------------|
| **รูป D (Normal)** | เส้นโค้งระฆัง — ปริมาณมากที่สุดตรงกลาง | ตลาดสมดุล; มีแนวโน้มกลับสู่ค่าเฉลี่ย |
| **รูป P** | ปริมาณกระจุกที่ด้านบน | การประมูลพบผู้ขายที่ด้านบน; นัยยะขาลง |
| **รูป b** | ปริมาณกระจุกที่ด้านล่าง | การประมูลพบผู้ซื้อที่ด้านล่าง; นัยยะขาขึ้น |
| **รูป B (Double Distribution)** | จุดสูงสุดปริมาณสองจุดที่ชัดเจน | ตลาดกำลังเปลี่ยนผ่าน; ดูว่า POC ไหนยืนได้ |
| **บาง/ยาว (Thin/Elongated)** | ปริมาณกระจายในช่วงกว้าง | เป็นแนวโน้ม/ไม่สมดุล; แนวโน้มน่าจะต่อเนื่อง |

---

## 3. แนวคิด Volume Profile (Volume Profile Concepts)

### 3.1 จุดควบคุม (Point of Control — POC)

**จุดควบคุม (Point of Control)** คือระดับราคาที่มีปริมาณการซื้อขายสูงสุดในช่วงโปรไฟล์ที่กำหนด เป็นตัวแทนของราคาที่ "ยุติธรรมที่สุด" ตามฉันทามติตลาด

$$\text{POC} = \arg\max_{p} V(p)$$

โดยที่ $V(p)$ คือปริมาณที่ซื้อขาย ณ ระดับราคา $p$

**คุณสมบัติ**:
- POC ทำหน้าที่เป็นแม่เหล็ก — ราคามีแนวโน้มถูกดึงดูดเข้าหา
- POC ที่ยังไม่ถูกเยี่ยมชม (Naked POC) จากเซสชันก่อนหน้าเป็นระดับ S/R ที่แข็งแกร่ง
- การเคลื่อนย้ายของ POC จากเซสชันหนึ่งไปอีกเซสชันบ่งชี้การเปลี่ยนแปลงมูลค่า

### 3.2 พื้นที่มูลค่า (Value Area — VA)

**พื้นที่มูลค่า** ครอบคลุม 70% ของปริมาณทั้งหมดสำหรับช่วงโปรไฟล์ (1 ส่วนเบี่ยงเบนมาตรฐานของการแจกแจงปกติ)

$$\text{Value Area} = \{p : \text{cumulative volume from POC outward} \leq 0.70 \times V_{\text{total}}\}$$

**ขอบเขต**:
- **VAH (Value Area High)**: ขอบบนของพื้นที่มูลค่า
- **VAL (Value Area Low)**: ขอบล่างของพื้นที่มูลค่า

**อัลกอริทึมการคำนวณ**:
```python
def calculate_value_area(volume_profile, target_pct=0.70):
    """
    Calculate Value Area from a volume profile.
    
    volume_profile: dict of {price_level: volume} sorted by price
    """
    total_volume = sum(volume_profile.values())
    target_volume = total_volume * target_pct
    
    # Find POC
    poc_price = max(volume_profile, key=volume_profile.get)
    poc_idx = sorted(volume_profile.keys()).index(poc_price)
    
    prices = sorted(volume_profile.keys())
    accumulated = volume_profile[poc_price]
    
    upper_idx = poc_idx
    lower_idx = poc_idx
    
    while accumulated < target_volume:
        # Look one level above and one below
        vol_above = volume_profile.get(prices[upper_idx + 1], 0) if upper_idx + 1 < len(prices) else 0
        vol_below = volume_profile.get(prices[lower_idx - 1], 0) if lower_idx - 1 >= 0 else 0
        
        # Add the larger volume side (two-price method)
        if upper_idx + 1 < len(prices) and lower_idx - 1 >= 0:
            # Compare pairs
            above_pair = vol_above + (volume_profile.get(prices[upper_idx + 2], 0) if upper_idx + 2 < len(prices) else 0)
            below_pair = vol_below + (volume_profile.get(prices[lower_idx - 2], 0) if lower_idx - 2 >= 0 else 0)
            
            if above_pair >= below_pair:
                upper_idx += 1
                accumulated += vol_above
            else:
                lower_idx -= 1
                accumulated += vol_below
        elif upper_idx + 1 < len(prices):
            upper_idx += 1
            accumulated += vol_above
        elif lower_idx - 1 >= 0:
            lower_idx -= 1
            accumulated += vol_below
        else:
            break
    
    return {
        "POC": poc_price,
        "VAH": prices[upper_idx],
        "VAL": prices[lower_idx],
        "VA_volume_pct": accumulated / total_volume
    }
```

### 3.3 โหนดปริมาณสูง (High Volume Nodes — HVN)

**HVN** = ระดับราคาที่มีปริมาณสูงอย่างเห็นได้ชัด สร้างจุดสูงสุดบนฮิสโตแกรมโปรไฟล์

**คุณสมบัติ**:
- ทำหน้าที่เป็นแม่เหล็ก — ราคามีแนวโน้มพักตัวรอบ HVN
- แสดงถึงพื้นที่ที่มีสภาพคล่องสูงและการยอมรับ
- ราคาผ่าน HVN ได้ยาก

**การตรวจจับ**:
$$\text{HVN}_i = V(p_i) > \mu_V + k \times \sigma_V$$

โดยที่ $\mu_V$ และ $\sigma_V$ คือค่าเฉลี่ยและส่วนเบี่ยงเบนมาตรฐานของปริมาณในทุกระดับราคา และ $k = 0.5$ ถึง $1.0$

### 3.4 โหนดปริมาณต่ำ (Low Volume Nodes — LVN)

**LVN** = ระดับราคาที่มีปริมาณต่ำอย่างเห็นได้ชัด สร้างร่องลึกบนฮิสโตแกรมโปรไฟล์

**คุณสมบัติ**:
- ทำหน้าที่เป็นอุปสรรค — ราคามีแนวโน้มเคลื่อนผ่าน LVN อย่างรวดเร็ว
- แสดงถึงพื้นที่ของการปฏิเสธและความไม่สมดุล
- ทำหน้าที่เป็นแนวรับ/แนวต้าน (ราคาเร่งตัวเมื่อเข้า LVN)
- แนวคิดคล้ายกับ Fair Value Gaps ใน SMC

**การตรวจจับ**:
$$\text{LVN}_i = V(p_i) < \mu_V - k \times \sigma_V$$

---

## 4. Market Profile (TPO Charts)

### 4.1 TPO (Time-Price Opportunity)

Market Profile (สร้างโดย J. Peter Steidlmayer ที่ CBOT) ใช้**เวลา**แทนปริมาณ แต่ละช่วง 30 นาทีแสดงด้วยตัวอักษร (A, B, C, ...) วางที่แต่ละระดับราคาที่ซื้อขายในช่วงนั้น

### 4.2 จำนวน TPO (TPO Count)

จำนวน TPO ที่แต่ละราคา = จำนวนช่วง 30 นาทีที่ราคานั้นถูกเยี่ยมชม

$$\text{TPO Count}(p) = |\{t : L_t \leq p \leq H_t\}|$$

### 4.3 TPO POC

แนวคิดเดียวกับ Volume POC แต่อิงตามเวลาแทนปริมาณ:
$$\text{TPO\_POC} = \arg\max_p \text{TPO Count}(p)$$

### 4.4 ประเภทโปรไฟล์ตามประเภทวัน (Profile Types by Day Type)

| ประเภทวัน | ลักษณะ | นัยยะ |
|----------|----------------|-------------|
| **วันปกติ (Normal Day)** | กฎ 70%; ช่วง IB คงที่ | สมดุล; เทรดสวนที่จุดสุดขีด |
| **วันปกติแบบแปรผัน (Normal Variation)** | ช่วง IB ขยายครั้งเดียว | มีอคติทิศทางเล็กน้อย |
| **วันแนวโน้ม (Trend Day)** | ช่วง IB ขยายหลายครั้ง; โปรไฟล์ยาว | แนวโน้มแข็งแกร่ง; ถือตำแหน่งตามแนวโน้ม |
| **การกระจายคู่ (Double Distribution)** | พื้นที่มูลค่าแยกสองจุด; รูป B | เปลี่ยนผ่าน; ดูการต่อเนื่อง |
| **วันเป็นกลาง (Neutral Day)** | สมดุลรอบ IB; ไม่มีการขยาย | สมดุลสุดขีด; การทะลุรอดำเนินการ |

### 4.5 Developing POC เทียบกับ Fixed POC

- **Developing POC**: POC ที่พัฒนาขึ้นระหว่างเซสชันปัจจุบัน มันเคลื่อนย้ายเมื่อมีข้อมูลปริมาณ/เวลาใหม่เข้ามา
- **Fixed POC**: POC สุดท้ายของเซสชันที่เสร็จสิ้น

**กฎการเทรด**: ถ้า Developing POC เคลื่อนย้ายอย่างแข็งแกร่งในทิศทางเดียว แสดงว่าตลาดไม่สมดุล — เทรดไปในทิศทางการเคลื่อนย้าย

---

## 5. Initial Balance (IB)

### 5.1 คำจำกัดความ

**Initial Balance** คือช่วงราคาที่เกิดขึ้นในชั่วโมงแรกของการซื้อขาย (สองช่วง 30 นาทีแรก, A และ B ในสัญลักษณ์ TPO)

$$\text{IB\_High} = \max(H_A, H_B)$$
$$\text{IB\_Low} = \min(L_A, L_B)$$
$$\text{IB\_Range} = \text{IB\_High} - \text{IB\_Low}$$

### 5.2 ความสำคัญของ IB

IB แสดงถึงปฏิสัมพันธ์แรกระหว่างตำแหน่ง Overnight/Premarket และเซสชันปกติ ความกว้างของ IB ทำนายประเภทวัน:

| ความกว้าง IB เทียบกับค่าเฉลี่ย | ประเภทวันที่เป็นไปได้ | แนวทางการเทรด |
|---------------------|-----------------|------------------|
| กว้าง (> 1.5x เฉลี่ย) | ปกติ / เป็นกลาง | เทรดสวนที่จุดสุดขีด; กลับสู่ค่าเฉลี่ย |
| ปานกลาง (0.75x–1.5x เฉลี่ย) | ปกติแบบแปรผัน | อคติทิศทางปานกลาง |
| แคบ (< 0.75x เฉลี่ย) | วันแนวโน้ม | เทรดทะลุอย่างเชิงรุก |

### 5.3 กฎการขยาย IB (IB Extension Rules)

- **ขยาย IB ครั้งเดียว (Single IB Extension)**: ราคาทะลุเหนือ IB High หรือใต้ IB Low ไม่เกิน 1x IB Range อคติทิศทางปานกลาง
- **ขยาย IB สองเท่า (Double IB Extension)**: ราคาขยาย 2x IB Range เกิน วันแนวโน้มที่แข็งแกร่ง
- **ขยาย IB ล้มเหลว (Failed IB Extension)**: ราคาทะลุออกแล้วกลับมาอยู่ภายใน IB เทรดเดอร์ติดกับ = เทรดสวนทิศทางทะลุ

### 5.4 กลยุทธ์การเทรด IB

```python
def ib_strategy(session_candles, ib_range_history):
    """
    Initial Balance trading strategy.
    """
    # Calculate today's IB (first hour)
    first_hour = session_candles[:4]  # 4 x 15min = 1 hour (adjust for timeframe)
    ib_high = max(c.high for c in first_hour)
    ib_low = min(c.low for c in first_hour)
    ib_range = ib_high - ib_low
    
    # Compare to average IB range
    avg_ib = np.mean(ib_range_history[-20:])
    
    # Narrow IB → expect trend day → trade breakout
    if ib_range < 0.75 * avg_ib:
        # Set breakout orders
        return {
            "strategy": "BREAKOUT",
            "buy_stop": ib_high + 0.1 * ib_range,
            "sell_stop": ib_low - 0.1 * ib_range,
            "sl_distance": 0.5 * ib_range,
            "tp": 2.0 * ib_range  # Target 2x IB extension
        }
    
    # Wide IB → expect normal day → fade extremes
    elif ib_range > 1.5 * avg_ib:
        return {
            "strategy": "MEAN_REVERSION",
            "buy_limit": ib_low + 0.1 * ib_range,  # Buy near IB low
            "sell_limit": ib_high - 0.1 * ib_range,  # Sell near IB high
            "sl_distance": 0.3 * ib_range,
            "tp": ib_range * 0.5  # Target POC area
        }
    
    else:
        return {"strategy": "WAIT", "note": "Average IB — watch for directional clues"}
```

---

## 6. Single Prints

### 6.1 คำจำกัดความ

**Single Prints** (หรือ Single TPOs) คือระดับราคาที่ถูกเยี่ยมชมเพียงช่วง 30 นาทีเดียว มักเกิดระหว่างการเคลื่อนไหวเร็วออกจากมูลค่า ในแง่ Volume Profile สอดคล้องกับพื้นที่ปริมาณต่ำมากภายในการเคลื่อนไหวตามแนวโน้ม

### 6.2 ความสำคัญ

- Single Prints แสดงถึง**กิจกรรมเชิงรุก (Initiative Activity)** — การซื้อหรือขายเชิงรุกของสถาบัน
- สร้าง "ช่องว่าง" ในโปรไฟล์ที่ราคามักกลับมาเติม (คล้ายกับ FVG ใน SMC)
- ทำหน้าที่เป็น S/R: แนวรับขาลง, แนวต้านขาขึ้น

### 6.3 การตรวจจับ

$$\text{SinglePrint}(p) = \text{TPO Count}(p) = 1 \quad \text{OR} \quad V(p) < 0.2 \times V_{\text{POC}}$$

### 6.4 กฎการเทรด

- **Single Prints ที่ยังไม่ถูกเติมเหนือราคา**: แนวต้าน; โซนขายที่เป็นไปได้เมื่อเข้าใกล้
- **Single Prints ที่ยังไม่ถูกเติมใต้ราคา**: แนวรับ; โซนซื้อที่เป็นไปได้เมื่อเข้าใกล้
- **Single Prints ที่ถูกเติมแล้ว**: เมื่อราคากลับมาเยี่ยมชมและใช้เวลาที่นั่น Single Print ถูก "ซ่อม" และสูญเสียความสำคัญ

---

## 7. Poor Highs และ Lows

### 7.1 คำจำกัดความ

**Poor High** คือจุดสูงสุดของเซสชันที่ตลาดดูเหมือนจะหยุดขึ้นไม่ใช่เพราะแรงขายที่แท้จริง แต่เพราะขาดแรงซื้อเชิงรุก มีลักษณะเป็น TPO หลายตัว (หรือปริมาณ) ที่จุดสูงสุดพอดี — บ่งชี้ว่าตลาด "หยุดนิ่ง" แทนที่จะถูกปฏิเสธ

**Poor Low** คือแนวคิดเดียวกันที่จุดต่ำสุดของเซสชัน

### 7.2 การระบุ

**Poor High**:
- TPO หลายตัวที่ระดับราคาสูงสุดของเซสชัน (มักจะ 3+ TPOs)
- จุดสูงไม่แสดงหางหมดแรงแบบ Single Print
- ปริมาณที่จุดสูงอยู่ระดับปานกลางถึงสูง (ผู้ซื้อหมดแรง ไม่ใช่ถูกผู้ขายผลัก)

**Good/Strong High**:
- Single Print หรือ TPO น้อยมากที่จุดสุดขีด
- แสดงการปฏิเสธเชิงรุก (ไส้เทียนยาว, TPO เดียว)
- แสดงถึงแรงขายที่แท้จริงที่หยุดการขึ้น

### 7.3 นัยยะการเทรด

| ประเภทจุดสูง/ต่ำ | นัยยะ | การดำเนินการ |
|--------------|-------------|--------|
| **Poor High** | มีแนวโน้มจะถูกกลับมาเยี่ยมชม/ทะลุ | อย่าขายที่ระดับนี้; คาดว่าจะทะลุขึ้น |
| **Strong High** | แนวต้านที่แท้จริง | ขายเมื่อรีเทสต์; หรือคาดว่าจะยืนอยู่ |
| **Poor Low** | มีแนวโน้มจะถูกกลับมาเยี่ยมชม/ทะลุ | อย่าซื้อที่ระดับนี้; คาดว่าจะทะลุลง |
| **Strong Low** | แนวรับที่แท้จริง | ซื้อเมื่อรีเทสต์; หรือคาดว่าจะยืนอยู่ |

### 7.4 อัลกอริทึม Poor High/Low

```python
def classify_extreme(profile, session_high, session_low, tpo_data):
    """
    Classify session highs/lows as poor or strong.
    """
    # TPO count at the session high
    tpos_at_high = tpo_data.get(session_high, 0)
    
    # Check for excess (single prints above the profile body)
    excess_above = count_single_prints_at_extreme(tpo_data, "HIGH")
    
    if tpos_at_high >= 3 and excess_above == 0:
        high_type = "POOR"  # Market stalled, not rejected
    elif tpos_at_high <= 1 or excess_above >= 2:
        high_type = "STRONG"  # Genuine rejection
    else:
        high_type = "NEUTRAL"
    
    # Same for low
    tpos_at_low = tpo_data.get(session_low, 0)
    excess_below = count_single_prints_at_extreme(tpo_data, "LOW")
    
    if tpos_at_low >= 3 and excess_below == 0:
        low_type = "POOR"
    elif tpos_at_low <= 1 or excess_below >= 2:
        low_type = "STRONG"
    else:
        low_type = "NEUTRAL"
    
    return {"high_type": high_type, "low_type": low_type}
```

---

## 8. กลยุทธ์การเทรดด้วย Volume Profile

### 8.1 กลยุทธ์ 1: กฎพื้นที่มูลค่า (Value Area Rule / 80% Rule)

**แนวคิด**: ถ้าตลาดเปิดนอกพื้นที่มูลค่าของวันก่อนหน้าแล้วซื้อขายกลับเข้าไปข้างใน มีความน่าจะเป็น 80% ที่จะถึงด้านตรงข้ามของพื้นที่มูลค่า

**เซ็ตอัพซื้อ (Long)**:
1. ตลาดเปิดใต้ VAL ของวันก่อน
2. ราคาซื้อขายกลับเหนือ VAL (การยอมรับ)
3. ซื้อ โดยเป้าหมาย VAH ของวันก่อน
4. SL ใต้การรีเทสต์ VAL

**เซ็ตอัพขาย (Short)**:
1. ตลาดเปิดเหนือ VAH ของวันก่อน
2. ราคาซื้อขายกลับใต้ VAH (การยอมรับ)
3. ขาย โดยเป้าหมาย VAL ของวันก่อน
4. SL เหนือการรีเทสต์ VAH

```python
def value_area_rule(prev_va, current_open, current_price):
    """
    The 80% rule: if price opens outside VA and returns inside,
    expect move to the opposite VA boundary.
    """
    prev_vah = prev_va["VAH"]
    prev_val = prev_va["VAL"]
    prev_poc = prev_va["POC"]
    
    # Open below VAL, now trading above VAL
    if current_open < prev_val and current_price > prev_val:
        return {
            "signal": "LONG",
            "entry": prev_val,
            "target": prev_vah,
            "sl": prev_val - 0.5 * (prev_vah - prev_val),
            "probability": 0.80,
            "note": "80% rule: price accepted back into VA from below"
        }
    
    # Open above VAH, now trading below VAH
    if current_open > prev_vah and current_price < prev_vah:
        return {
            "signal": "SHORT",
            "entry": prev_vah,
            "target": prev_val,
            "sl": prev_vah + 0.5 * (prev_vah - prev_val),
            "probability": 0.80,
            "note": "80% rule: price accepted back into VA from above"
        }
    
    return None
```

### 8.2 กลยุทธ์ 2: การเทรด Naked POC

**แนวคิด**: "Naked POC" คือ POC ของเซสชันก่อนหน้าที่ยังไม่ถูกราคากลับมาเยี่ยมชมในเซสชันต่อมา ทำหน้าที่เป็นแม่เหล็กที่ทรงพลัง

**กฎ**:
1. ระบุ Naked POC จาก 5–20 เซสชันล่าสุด
2. เมื่อราคาเข้าใกล้ Naked POC คาดว่าจะมีปฏิกิริยา (ราคาหยุด, พักตัว, หรือกลับตัว)
3. เทรดปฏิกิริยา: ถ้าราคากำลังมุ่งหน้าไป Naked POC ใช้เป็นเป้าหมาย; ถ้าราคาอยู่ที่ Naked POC เทรดการปฏิเสธ

### 8.3 กลยุทธ์ 3: การทะลุ/ปฏิเสธ LVN

**แนวคิด**: LVN คือระดับราคาที่ตลาดเคลื่อนผ่านอย่างรวดเร็ว — ทำหน้าที่เป็นอุปสรรค ราคาจะเด้งกลับหรือเร่งผ่าน

**เซ็ตอัพทะลุ (Breakout)**:
- ราคาเข้าใกล้ LVN จากภายในพื้นที่มูลค่า
- ถ้าราคาทะลุ LVN ด้วยโมเมนตัม จะเร่งตัวไปยัง HVN ถัดไป
- เข้า: ทะลุผ่าน LVN
- เป้าหมาย: HVN ถัดไป

**เซ็ตอัพปฏิเสธ (Rejection)**:
- ราคาสำรวจเข้าไปใน LVN แต่ไม่สามารถรักษาได้
- เข้า: เทรดกลับไปหา HVN/POC ที่ใกล้ที่สุด
- SL: เลย LVN

### 8.4 กลยุทธ์ 4: การเปลี่ยนแปลงพื้นที่มูลค่าที่กำลังพัฒนา (Developing Value Area Shift)

**แนวคิด**: ตรวจสอบพื้นที่มูลค่าของเซสชันที่กำลังพัฒนา ถ้ามันเคลื่อนออกไปทั้งหมดเหนือหรือใต้พื้นที่มูลค่าของเซสชันก่อน แสดงว่าการเคลื่อนไหวตามทิศทางกำลังเกิดขึ้น

$$\text{VA Shift} = \begin{cases} \text{Bullish} & \text{if } \text{Dev\_VAL} > \text{Prev\_VAH} \\ \text{Bearish} & \text{if } \text{Dev\_VAH} < \text{Prev\_VAL} \\ \text{Overlap} & \text{otherwise (no clear shift)} \end{cases}$$

### 8.5 กลยุทธ์ 5: การวิเคราะห์โปรไฟล์แบบรวม (Composite Profile Analysis)

สร้าง Volume Profile จากหลายเซสชัน (รวม 3–5 วัน, รวมรายสัปดาห์, รวมรายเดือน) เพื่อระบุพื้นที่มูลค่าและ POC ระดับใหญ่สำหรับการเทรดแบบ Swing

---

## 9. สูตรทางคณิตศาสตร์ (Mathematical Formulas)

### 9.1 การสร้าง Volume Profile

จากข้อมูล Tick หรือข้อมูลแท่งเทียน สร้าง Volume Profile โดยรวบรวมปริมาณที่แต่ละระดับราคา:

$$V(p) = \sum_{i=1}^{N} v_i \cdot \mathbb{1}[L_i \leq p \leq H_i] \cdot w_i(p)$$

โดยที่:
- $v_i$ = ปริมาณของแท่งเทียน $i$
- $\mathbb{1}[\cdot]$ = ฟังก์ชันตัวบ่ง (Indicator Function)
- $w_i(p)$ = น้ำหนักการกระจายปริมาณภายในแท่ง $i$

**แบบจำลองการกระจายปริมาณ**:

1. **แบบสม่ำเสมอ (Uniform)**: $w_i(p) = \frac{1}{H_i - L_i}$ (กระจายปริมาณเท่าๆ กันในทุกราคาของช่วง)

2. **แบบสามเหลี่ยม (Triangle / Close-weighted)**: ปริมาณมากขึ้นใกล้ราคาปิด:
$$w_i(p) = \frac{2(1 - |p - C_i| / (H_i - L_i))}{H_i - L_i}$$

3. **แบบแยก (Split / Buy/Sell)**: จัดสรรปริมาณเหนือจุดกลางเป็นการขาย, ใต้เป็นการซื้อ

### 9.2 การแจกแจงความน่าจะเป็นของพื้นที่มูลค่า

สมมติว่าปริมาณมีการแจกแจงแบบเกาส์เซียนรอบ POC:

$$V(p) \approx V_{\text{max}} \cdot e^{-\frac{(p - \text{POC})^2}{2\sigma^2}}$$

โดยที่ $\sigma$ กำหนดความกว้างของพื้นที่มูลค่า:
$$\text{VA Width} \approx 2\sigma \quad \text{(ครอบคลุม 68% ของปริมาณ)}$$
$$\text{70\% VA} \approx 2.07\sigma$$

### 9.3 อัตราการเคลื่อนย้าย POC (POC Migration Rate)

อัตราที่ Developing POC เคลื่อนที่บ่งชี้ความมั่นใจของตลาด:

$$\text{POC\_Migration} = \frac{\Delta \text{POC}}{\Delta t} = \frac{\text{POC}(t) - \text{POC}(t - \Delta t)}{\Delta t}$$

ถ้า $|\text{POC\_Migration}| > 0$ อย่างสม่ำเสมอ ตลาดกำลังเป็นแนวโน้ม

### 9.4 ความสัมพันธ์ VWAP (Volume-Weighted Average Price)

VWAP คือค่าเฉลี่ยถ่วงน้ำหนักปริมาณของราคาที่ซื้อขายทั้งหมดและมีความสัมพันธ์ใกล้ชิดกับ POC:

$$\text{VWAP} = \frac{\sum_{i=1}^{N} P_i \times V_i}{\sum_{i=1}^{N} V_i}$$

แถบส่วนเบี่ยงเบนมาตรฐานรอบ VWAP:
$$\text{VWAP}_{\pm n\sigma} = \text{VWAP} \pm n \times \sqrt{\frac{\sum V_i(P_i - \text{VWAP})^2}{\sum V_i}}$$

### 9.5 การวิเคราะห์ปริมาณสัมพัทธ์ (Relative Volume Analysis)

$$\text{RVOL}(p) = \frac{V(p)}{V_{\text{avg}}(p, \text{lookback})}$$

โดยที่ $V_{\text{avg}}(p, \text{lookback})$ คือปริมาณเฉลี่ย ณ ราคา $p$ ในช่วง Lookback

- $\text{RVOL} > 2$: สูงกว่าค่าเฉลี่ยอย่างมีนัยสำคัญ — การมีส่วนร่วมแข็งแกร่ง
- $\text{RVOL} < 0.5$: ต่ำกว่าค่าเฉลี่ยมาก — ขาดความสนใจ

### 9.6 Volume Delta ที่แต่ละราคา

$$\Delta V(p) = V_{\text{buy}}(p) - V_{\text{sell}}(p)$$

Delta เป็นบวก = การซื้อสุทธิ Delta เป็นลบ = การขายสุทธิ ช่วยกำหนดว่า HVN เกิดจากแรงซื้อหรือแรงขาย

---

## 10. ขั้นตอนการดำเนินงานสำหรับ AI (Execution Flow for AI Implementation)

### 10.1 Pseudocode กลยุทธ์ฉบับสมบูรณ์

```python
def volume_profile_strategy():
    """
    Complete Volume Profile trading strategy.
    Combines multiple VP concepts for trade decisions.
    """
    
    # ================================================
    # PHASE 1: BUILD PROFILES
    # ================================================
    
    for instrument in watchlist:
        # Build session profiles
        prev_session = build_volume_profile(
            fetch_candles(instrument, "M5", session="previous"),
            price_increment=get_tick_size(instrument)
        )
        
        current_session = build_volume_profile(
            fetch_candles(instrument, "M5", session="current"),
            price_increment=get_tick_size(instrument)
        )
        
        # Build composite profiles
        weekly_composite = build_volume_profile(
            fetch_candles(instrument, "M15", days=5),
            price_increment=get_tick_size(instrument)
        )
        
        # Calculate value areas
        prev_va = calculate_value_area(prev_session)
        current_va = calculate_value_area(current_session)
        weekly_va = calculate_value_area(weekly_composite)
        
        # Identify HVNs and LVNs
        hvns = find_hvns(weekly_composite, threshold_sigma=0.5)
        lvns = find_lvns(weekly_composite, threshold_sigma=-0.5)
        
        # Find naked POCs
        naked_pocs = find_naked_pocs(instrument, lookback_sessions=20)
        
        # Classify previous session extremes
        extremes = classify_extreme(prev_session, prev_session_high, prev_session_low, tpo_data)
        
        # ================================================
        # PHASE 2: DETERMINE MARKET STATE
        # ================================================
        
        current_price = get_price(instrument)
        session_open = get_session_open(instrument)
        
        # Relative position
        position = determine_position(current_price, prev_va, weekly_va)
        
        # Day type assessment
        ib = calculate_initial_balance(instrument)
        avg_ib = get_avg_ib_range(instrument, lookback=20)
        day_type_forecast = forecast_day_type(ib, avg_ib)
        
        # Profile shape of developing session
        profile_shape = classify_profile_shape(current_session)
        
        # ================================================
        # PHASE 3: GENERATE SIGNALS
        # ================================================
        
        signals = []
        
        # Strategy 1: 80% Rule
        va_rule_signal = value_area_rule(prev_va, session_open, current_price)
        if va_rule_signal:
            signals.append(va_rule_signal)
        
        # Strategy 2: Naked POC approach
        for npoc in naked_pocs:
            if abs(current_price - npoc["price"]) < 0.5 * atr:
                signals.append({
                    "signal": "NAKED_POC_APPROACH",
                    "direction": "target" if trending_toward(current_price, npoc) else "rejection",
                    "level": npoc["price"],
                    "age_sessions": npoc["age"]
                })
        
        # Strategy 3: LVN breakout/rejection
        for lvn in lvns:
            if abs(current_price - lvn["price"]) < 0.3 * atr:
                signals.append({
                    "signal": "LVN_INTERACTION",
                    "level": lvn["price"],
                    "nearest_hvn": find_nearest_hvn(lvn, hvns)
                })
        
        # Strategy 4: IB breakout (for narrow IB)
        if day_type_forecast == "TREND_DAY":
            if current_price > ib["high"] + 0.1 * ib["range"]:
                signals.append({
                    "signal": "IB_BREAKOUT_LONG",
                    "entry": ib["high"],
                    "target": ib["high"] + 2 * ib["range"]
                })
            elif current_price < ib["low"] - 0.1 * ib["range"]:
                signals.append({
                    "signal": "IB_BREAKOUT_SHORT",
                    "entry": ib["low"],
                    "target": ib["low"] - 2 * ib["range"]
                })
        
        # Strategy 5: Poor high/low retest
        if extremes["high_type"] == "POOR" and current_price > prev_session_high * 0.999:
            signals.append({
                "signal": "POOR_HIGH_BREAK",
                "direction": "LONG",
                "note": "Poor high likely to be exceeded"
            })
        
        if extremes["low_type"] == "POOR" and current_price < prev_session_low * 1.001:
            signals.append({
                "signal": "POOR_LOW_BREAK",
                "direction": "SHORT",
                "note": "Poor low likely to be broken"
            })
        
        # ================================================
        # PHASE 4: SCORE AND EXECUTE BEST SIGNAL
        # ================================================
        
        if not signals:
            continue
        
        # Score each signal
        for signal in signals:
            signal["score"] = score_vp_signal(
                signal, 
                position=position,
                day_type=day_type_forecast,
                weekly_context=weekly_va,
                profile_shape=profile_shape
            )
        
        # Select best
        signals.sort(key=lambda s: s.get("score", 0), reverse=True)
        best = signals[0]
        
        if best["score"] < 0.55:
            continue
        
        # Calculate trade parameters
        entry, sl, tp = calculate_vp_trade_params(best, prev_va, current_va, hvns, lvns, atr)
        
        # Risk validation
        rr = abs(tp - entry) / abs(entry - sl)
        if rr < 2.0:
            continue
        
        # Execute
        size = calculate_position_size(balance, risk_pct=1.0, entry=entry, sl=sl)
        
        trade = execute_trade(
            instrument=instrument,
            direction=best.get("direction", infer_direction(best)),
            entry=entry,
            sl=sl,
            tp=tp,
            size=size,
            metadata={"strategy": "VOLUME_PROFILE", "signal": best}
        )
        
        return trade
    
    return WAIT("No VP signal")
```

---

## 11. พารามิเตอร์ความเสี่ยง (Risk Parameters)

### 11.1 การวาง Stop Loss

| กลยุทธ์ | ตำแหน่ง SL | ตรรกะ |
|----------|-------------|-------|
| กฎ 80% (ซื้อจาก VAL) | ใต้ VAL 0.3 ความกว้าง VA | เลยจุดยอมรับ |
| IB Breakout | กลับเข้า IB 0.5 IB range | การทะลุล้มเหลวเป็นโมฆะ |
| LVN Rejection | เลย LVN 0.5 ATR | ถ้า LVN ไม่ยืนอยู่ ทฤษฎีผิด |
| Naked POC | เลย POC 0.5 ATR | |
| Poor High/Low | เลยจุดสุดขีด 1 ATR | |

### 11.2 ระดับ Take Profit

| กลยุทธ์ | TP1 | TP2 | TP3 |
|----------|-----|-----|-----|
| กฎ 80% | POC | ขอบ VA ตรงข้าม | POC ของเซสชันถัดไป |
| IB Breakout | ขยาย 1x IB | ขยาย 2x IB | HVN ถัดไป |
| LVN → HVN | HVN ที่ใกล้ที่สุด | POC | — |
| Naked POC | ขอบ VA ที่ใกล้ที่สุด | — | — |

### 11.3 การกำหนดขนาดสถานะตามความมั่นใจ

| คะแนนสัญญาณ VP | ความเสี่ยง % |
|----------------|--------|
| $\geq 0.80$ | 1.5% |
| 0.65–0.79 | 1.0% |
| 0.55–0.64 | 0.5% |
| $< 0.55$ | ไม่เทรด |

### 11.4 ขีดจำกัดความเสี่ยงต่อเซสชัน

- สูงสุด 3 เทรด VP ต่อเซสชัน
- ความเสี่ยงรวมสูงสุด 2% ต่อเซสชันจากกลยุทธ์ VP
- ถ้าสองเทรด VP แรกขาดทุน ไม่เทรด VP อีกสำหรับเซสชันนั้น
- กลยุทธ์ VP ทำงานดีที่สุดในช่วงเวลาเซสชันเฉพาะ: ใช้การจับเวลา Kill-zone

---

## 12. เทคนิคขั้นสูง (Advanced Techniques)

### 12.1 Volume Profile Delta (ปริมาณซื้อ เทียบกับ ปริมาณขาย)

แยกปริมาณที่แต่ละระดับราคาเป็นการซื้อเชิงรุกและการขายเชิงรุก:

$$\text{Delta}(p) = V_{\text{buy}}(p) - V_{\text{sell}}(p)$$

**การตีความ**:
- Delta เป็นบวกที่ HVN → ผู้ซื้อควบคุมที่มูลค่ายุติธรรม
- Delta เป็นลบที่ HVN → ผู้ขายควบคุม; อาจเกิดการทะลุลง
- Divergence ระหว่างราคาทำจุดสูงใหม่กับ Delta ที่ลดลง → การกระจายสถานะ (Distribution)

### 12.2 Volume Footprint Charts

Footprint Charts แสดงปริมาณ Bid/Ask ที่แต่ละราคาภายในแต่ละแท่งเทียน รูปแบบสำคัญ:
- **Stacked Imbalances**: หลายระดับราคาติดต่อกันที่ปริมาณซื้อ > 2x ปริมาณขาย (หรือกลับกัน) บ่งชี้กิจกรรมสถาบันเชิงรุก
- **Unfinished Auction**: ระดับราคาสุดท้ายในแท่งเทียนแสดงปริมาณศูนย์ด้านเดียว — แนะนำว่าการประมูลจะดำเนินต่อในทิศทางนั้น

### 12.3 การวิเคราะห์โปรไฟล์รวมหลายเซสชัน (Multi-Session Composite Analysis)

สร้างโปรไฟล์รวมในช่วงเวลาต่างๆ เพื่อระบุมูลค่าหลายกรอบเวลา:

| ช่วงรวม | การใช้งาน |
|-----------------|-----|
| 3 วัน | มูลค่ายุติธรรมระยะสั้นสำหรับ Day Trader |
| สัปดาห์ | มูลค่าระดับกลางสำหรับ Swing Trader |
| เดือน | มูลค่าระดับมหภาคสำหรับ Position Trader |
| ไตรมาส | ตำแหน่งสถาบันระยะยาว |

### 12.4 VP + SMC Integration

Volume Profile เสริมการวิเคราะห์ SMC:
- **Order Blocks ที่มีปริมาณสูง**: OB ที่ตรงกับ HVN แข็งแกร่งกว่า (การยอมรับของสถาบัน)
- **FVG เป็น LVN**: Fair Value Gaps ใน SMC สอดคล้องกับ LVN ใน VP — ตลาดเคลื่อนเร็วเกินไปจนไม่สร้างปริมาณ
- **Liquidity Pools ใกล้ HVN**: การกวาดสภาพคล่องที่เล็งระดับใกล้ HVN มีความน่าจะเป็นสูงกว่า

---

## 13. หมายเหตุการใช้งาน AI (AI Implementation Notes)

### 13.1 ข้อกำหนดข้อมูล

| ประเภทข้อมูล | ขั้นต่ำ | หมายเหตุ |
|-----------|---------|-------|
| ข้อมูล Tick | เหมาะที่สุดสำหรับ VP ที่แม่นยำ | ไม่เสมอจะมีสำหรับ Forex Spot |
| แท่งเทียน M1 พร้อมปริมาณ | ทางเลือกที่ยอมรับได้ | ใช้การกระจายราคาถ่วงน้ำหนักปริมาณ |
| แท่งเทียน M5 พร้อมปริมาณ | ขั้นต่ำที่ใช้งานได้ | แม่นยำน้อยกว่าแต่ใช้งานได้ |
| เวลาเซสชัน | จำเป็น | ต้องการขอบเขตเซสชันสำหรับ IB, ประเภทวัน |

### 13.2 สำหรับตลาด Crypto

VP สำหรับ Crypto มีข้อพิจารณาเฉพาะ:
- **ไม่มีเซสชันตายตัว**: ใช้วัน UTC 24 ชั่วโมง หรือกำหนดเซสชันเอง (เช่น US 13:00–21:00 UTC)
- **ซื้อขาย 24/7**: IB อาจมีความหมายน้อยลง; ใช้ชั่วโมงแรกหลังปิดวัน (00:00 UTC)
- **ปริมาณเฉพาะ Exchange**: ใช้ปริมาณรวมจาก Exchange หลักๆ เพื่อความแม่นยำ
- **เวลา Funding Rate** (Futures): 08:00, 16:00, 00:00 UTC สร้างเซสชันย่อย

### 13.3 ผลงานที่คาดหวัง

| ตัวชี้วัด | ช่วงที่คาดหวัง |
|--------|---------------|
| อัตราชนะ (กฎ 80%) | 55–65% |
| อัตราชนะ (IB Breakout, เฉพาะ IB แคบ) | 50–60% |
| อัตราชนะ (Naked POC) | 55–62% |
| R:R เฉลี่ย | 1.5:1 ถึง 2.5:1 |
| เทรด/วัน/สินทรัพย์ | 1–3 |
| Profit Factor | 1.5–2.2 |

---

## 14. อ้างอิง (References)

### หนังสือ
1. Steidlmayer, J. P., & Hawkins, S. B. (2003). *Steidlmayer on Markets: Trading with Market Profile*. Wiley.
2. Dalton, J. F. (1993). *Mind Over Markets: Power Trading with Market Generated Information*. McGraw-Hill.
3. Dalton, J. F. (2007). *Markets in Profile: Profiting from the Auction Process*. Wiley.
4. Jones, D. L. (2010). *Volume Profile: The Insider's Guide to Trading*. Independently published.
5. Gopalakrishnan, J. (2009). "An Introduction to Market Profile" — *Technical Analysis of Stocks & Commodities*.

### บทความวิชาการ
6. Hagstrom, P. (2019). "Volume Profile Analysis for Algorithmic Trading Systems." *Journal of Trading*, 14(3), 45–58.
7. Cont, R., Kukanov, A., & Stoikov, S. (2014). "The Price Impact of Order Book Events." *Journal of Financial Econometrics*, 12(1), 47–88.
8. Bouchaud, J.-P. (2010). "Price Impact." *Encyclopedia of Quantitative Finance*, Wiley.
9. Kyle, A. S. (1985). "Continuous Auctions and Insider Trading." *Econometrica*, 53(6), 1315–1335.

---

*เอกสารนี้เป็นส่วนหนึ่งของฐานความรู้ระบบเทรด AI แบบหลายตัวแทน (Multi-Agent AI Trading System) ควรอ่านร่วมกับคู่มือแนวคิดเงินอัจฉริยะ (04_smart_money_concepts) และคู่มือการวิเคราะห์หลายกรอบเวลา (11_multi_timeframe_analysis)*
