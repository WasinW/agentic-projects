# กลยุทธ์โมเมนตัมและการเทรดตามเทรนด์ (Momentum & Trend Following Strategies) — เอกสารอ้างอิงฉบับสมบูรณ์

## ข้อมูลเอกสาร
| ฟิลด์ | ค่า |
|---|---|
| ประเภทกลยุทธ์ | โมเมนตัม / การเทรดตามเทรนด์ (Momentum / Trend Following) |
| สินทรัพย์ | Forex, คริปโต (Spot & Futures) |
| กรอบเวลา | ระหว่างวันถึงหลายเดือน |
| ความซับซ้อน | ระดับกลางถึงสูง |
| เงินทุนที่ต้องการ | ปานกลาง |
| อัปเดตล่าสุด | 2026-04-12 |

---

## สารบัญ
1. [การวิจัยปัจจัยโมเมนตัม](#1-การวิจัยปัจจัยโมเมนตัม)
2. [โมเมนตัมแบบอนุกรมเวลา vs ภาคตัดขวาง](#2-โมเมนตัมแบบอนุกรมเวลา-vs-ภาคตัดขวาง)
3. [ระบบการเทรดตามเทรนด์](#3-ระบบการเทรดตามเทรนด์)
4. [ระบบค่าเฉลี่ยเคลื่อนที่](#4-ระบบค่าเฉลี่ยเคลื่อนที่)
5. [การเบรกเอาท์ Donchian Channel (Turtle Trading)](#5-การเบรกเอาท์-donchian-channel-turtle-trading)
6. [ความแข็งแกร่งของเทรนด์ด้วย ADX](#6-ความแข็งแกร่งของเทรนด์ด้วย-adx)
7. [Parabolic SAR](#7-parabolic-sar)
8. [อินดิเคเตอร์ Supertrend](#8-อินดิเคเตอร์-supertrend)
9. [Dual Momentum (Gary Antonacci)](#9-dual-momentum-gary-antonacci)
10. [วิกฤตโมเมนตัมและความเสี่ยงปลายหาง](#10-วิกฤตโมเมนตัมและความเสี่ยงปลายหาง)
11. [การกำหนดขนาดสถานะสำหรับเทรดตามเทรนด์](#11-การกำหนดขนาดสถานะสำหรับเทรดตามเทรนด์)
12. [การตรวจจับสภาวะตลาด](#12-การตรวจจับสภาวะตลาด)
13. [ตรรกะหลัก — การเข้า/ออกสถานะ](#13-ตรรกะหลัก--การเข้าออกสถานะ)
14. [ข้อมูลจำเพาะทางเทคนิค](#14-ข้อมูลจำเพาะทางเทคนิค)
15. [แบบจำลองทางคณิตศาสตร์](#15-แบบจำลองทางคณิตศาสตร์)
16. [พารามิเตอร์ความเสี่ยง](#16-พารามิเตอร์ความเสี่ยง)
17. [ขั้นตอนการดำเนินการ](#17-ขั้นตอนการดำเนินการ)
18. [เอกสารอ้างอิง](#18-เอกสารอ้างอิง)

---

## 1. การวิจัยปัจจัยโมเมนตัม

### 1.1 รากฐานทางวิชาการ

ปรากฏการณ์ผิดปกติด้านโมเมนตัม (Momentum Anomaly) ได้รับการบันทึกอย่างเป็นทางการโดย **Jegadeesh and Titman (1993)** ซึ่งแสดงให้เห็นว่าการซื้อหุ้นที่เคยเป็นผู้ชนะในอดีตและขายหุ้นที่เคยเป็นผู้แพ้จะสร้างผลตอบแทนผิดปกติที่มีนัยสำคัญในช่วงถือครอง 3-12 เดือน

**ข้อค้นพบสำคัญ:**
- พอร์ตโฟลิโอที่สร้างจากการซื้อหุ้นที่มีผลตอบแทนสูงสุดในช่วง 3-12 เดือนที่ผ่านมาและขายหุ้นที่มีผลตอบแทนต่ำสุดได้รับผลตอบแทนส่วนเกินประมาณ **1% ต่อเดือน**

**คำจำกัดความผลตอบแทนโมเมนตัม:**

$$r_{mom,t} = r_{winner,t} - r_{loser,t}$$

โดยที่ผู้ชนะและผู้แพ้ถูกกำหนดจากผลตอบแทนในช่วงระยะเวลาก่อตัว $J$ (โดยปกติ 3, 6, หรือ 12 เดือน)

### 1.2 โมเมนตัมใน Forex และคริปโต

**โมเมนตัมใน Forex:**
- บันทึกโดย Okunev & White (2003): โมเมนตัมสกุลเงินสร้างผลตอบแทนส่วนเกินรายปี 5-10%
- แข็งแกร่งที่สุดในช่วงระยะเวลา 1-3 เดือน
- เชื่อมโยงกับความต่อเนื่องของนโยบายธนาคารกลาง กระแสเงินจาก Carry Trade และพฤติกรรมฝูงชนของนักลงทุน

**โมเมนตัมในคริปโต:**
- ผลกระทบโมเมนตัมที่แข็งแกร่งมาก (Liu, Tsyvinski & Wu, 2019)
- โมเมนตัมระยะสั้น (1 สัปดาห์ถึง 1 เดือน) ทรงพลังเป็นพิเศษ
- ความผันผวนสูงขยายผลตอบแทนโมเมนตัมแต่ก็เพิ่มความเสี่ยงวิกฤต
- โมเมนตัมภาคตัดขวางระหว่าง Altcoin ใช้ประโยชน์จากการหมุนเวียน "ฤดู Altcoin"

### 1.3 แหล่งที่มาของผลตอบแทนโมเมนตัม

| แหล่งที่มา | คำอธิบาย |
|---|---|
| การตอบสนองต่ำทางพฤติกรรม (Behavioral Underreaction) | นักลงทุนตอบสนองต่อข่าวช้าในตอนแรก ทำให้เกิดการลอยตัว |
| การตอบสนองเกินทางพฤติกรรม (Behavioral Overreaction) | การตอบสนองต่ำในตอนแรกตามด้วยการตอบสนองเกิน |
| การแพร่กระจายข้อมูลช้า (Slow Information Diffusion) | ข้อมูลใช้เวลาในการแพร่กระจายไปยังนักลงทุน |
| พฤติกรรมฝูงชน (Herding) | ผู้เทรดตามเทรนด์ขยายการเคลื่อนไหวราคาที่มีอยู่ |
| ตามความเสี่ยง (Risk-Based) | สินทรัพย์โมเมนตัมมีความเสี่ยงวิกฤตสูงกว่า (ชดเชยความเสี่ยงปลายหาง) |
| โครงสร้างจุลภาคตลาด (Market Microstructure) | ความต่อเนื่องของ Order Flow, การ Cascade ของ Stop-Loss |

---

## 2. โมเมนตัมแบบอนุกรมเวลา vs ภาคตัดขวาง

### 2.1 โมเมนตัมอนุกรมเวลา (Time-Series Momentum / TSMOM)

โมเมนตัมอนุกรมเวลาดูแต่ละสินทรัพย์เป็นรายตัว: หากมันขึ้น ให้ซื้อ; หากมันลง ให้ขาย/ชอร์ต

**สัญญาณ:**

$$\text{Signal}_{i,t} = \text{sign}(r_{i,t-J:t})$$

โดยที่ $r_{i,t-J:t}$ คือผลตอบแทนของสินทรัพย์ $i$ ในช่วง $J$ งวดที่ผ่านมา

**ขนาดสถานะที่ปรับแล้ว:**

$$w_{i,t} = \frac{\text{signal}_{i,t} \times \sigma_{target}}{\hat{\sigma}_{i,t}}$$

โดยที่:
- $\sigma_{target}$ = ความผันผวนเป้าหมาย (เช่น 10% ต่อปี)
- $\hat{\sigma}_{i,t}$ = ความผันผวนประมาณการของสินทรัพย์ $i$

**Moskowitz, Ooi, and Pedersen (2012)** บันทึก TSMOM ใน 58 ตราสารที่มีสภาพคล่องตลอด 25 ปี พบผลตอบแทนส่วนเกินที่มีนัยสำคัญในช่วง 1-12 เดือน

### 2.2 โมเมนตัมภาคตัดขวาง (Cross-Sectional Momentum / XSMOM)

โมเมนตัมภาคตัดขวางเปรียบเทียบสินทรัพย์ต่าง ๆ กัน: ไปยาวสินทรัพย์ที่ทำผลงานดีที่สุดและชอร์ตสินทรัพย์ที่ทำผลงานแย่ที่สุด

**สัญญาณ:**

$$\text{Rank}_{i,t} = \text{percentile\_rank}(r_{i,t-J:t}) \text{ among all assets}$$

**ขนาดสถานะ:**

$$w_{i,t} = \begin{cases} +1 & \text{if } \text{Rank}_{i,t} > 80\text{th percentile (winner)} \\ -1 & \text{if } \text{Rank}_{i,t} < 20\text{th percentile (loser)} \\ 0 & \text{otherwise} \end{cases}$$

### 2.3 การเปรียบเทียบ

| คุณลักษณะ | โมเมนตัมอนุกรมเวลา | โมเมนตัมภาคตัดขวาง |
|---|---|---|
| เกณฑ์อ้างอิง | ประวัติของตัวสินทรัพย์เอง | ผลงานของกลุ่มเดียวกัน |
| Exposure สุทธิ | อาจเป็นทั้ง Long หรือ Short โดยรวม | Dollar-neutral (Long-Short) |
| เหมาะสำหรับ | สินทรัพย์เดียวหรือมาโคร | จักรวาลสินทรัพย์ขนาดใหญ่ (คริปโต Altcoin) |
| สหสัมพันธ์กับตลาด | ปานกลาง | ต่ำ (เป็นกลางต่อตลาด) |
| ความเสี่ยงวิกฤต | สูงเมื่อตลาดกลับตัว | ปานกลาง (มีการป้องกัน) |
| การนำไปใช้ | ง่ายกว่า | ต้องจัดอันดับจักรวาลสินทรัพย์ |
| การประยุกต์ใน Forex | เทรดตามเทรนด์คู่เดียว | จัดอันดับทุกคู่ ซื้อดีสุด/ขายแย่สุด |
| การประยุกต์ในคริปโต | เทรดตามเทรนด์ BTC | การหมุนเวียน Altcoin |

### 2.4 สัญญาณโมเมนตัมรวม (Combined Momentum Signal)

$$\text{CombinedSignal}_{i,t} = \alpha \times \text{TSMOM}_{i,t} + (1-\alpha) \times \text{XSMOM}_{i,t}$$

โดยที่ $\alpha$ คือน้ำหนักผสม (โดยทั่วไป 0.5-0.7 ให้น้ำหนัก TSMOM มากกว่าเพื่อความเรียบง่าย)

---

## 3. ระบบการเทรดตามเทรนด์

### 3.1 ภาพรวมของระบบเทรดตามเทรนด์หลัก

| ระบบ | แหล่งสัญญาณ | การเข้า | การออก | ความซับซ้อน |
|---|---|---|---|---|
| MA Crossover | ค่าเฉลี่ยเคลื่อนที่ | MA เร็วตัด MA ช้า | Crossover ย้อนกลับ | ต่ำ |
| Donchian Breakout | ช่องราคา | เบรกเอาท์จุดสูง/ต่ำใหม่ | ช่องราคาแบบ Trailing | ต่ำ |
| ADX + DI | การเคลื่อนไหวทิศทาง | +DI ตัด -DI โดย ADX > เกณฑ์ | DI ตัดกลับหรือ ADX ลดลง | กลาง |
| Parabolic SAR | จุด Trailing Stop | ราคาตัด SAR | SAR ไล่ทันราคา | กลาง |
| Supertrend | แถบตาม ATR | ราคาตัดเส้น Supertrend | ตัดย้อนกลับ | กลาง |
| MACD | Signal Line Cross | MACD ตัดเส้น Signal | Crossover ย้อนกลับ | ต่ำ |
| Ichimoku | ระบบเมฆ | ราคาเหนือเมฆ, TK cross | ต่ำกว่าเมฆ | สูง |
| Dual Momentum | Absolute + Relative | Absolute บวก + Relative สูงสุด | เงื่อนไขใดเงื่อนไขหนึ่งล้มเหลว | กลาง |

### 3.2 คุณสมบัติร่วมของการเทรดตามเทรนด์

1. **ผลตอบแทนเบ้ขวา (Right-skewed returns)**: ขาดทุนเล็กน้อยหลายครั้ง กำไรมากไม่กี่ครั้ง
2. **อัตราชนะต่ำ (Low win rate)**: โดยทั่วไป 30-45%
3. **อัตราส่วนผลตอบแทนสูง (High payoff ratio)**: กำไรเฉลี่ย >> ขาดทุนเฉลี่ย
4. **Alpha ในวิกฤต (Crisis alpha)**: ทำผลงานดีในช่วงตลาดผิดปกติ/วิกฤต
5. **ขาดทุนในช่วงตลาด Sideway (Drawdowns during ranging)**: ถูก Whipsaw ในตลาดไม่มีทิศทาง
6. **ความคาดหวังบวกระยะยาว (Long-term positive expectancy)**: ข้อได้เปรียบมาจากเหตุการณ์ปลายหาง

**การกระจายตัวของผลตอบแทนเทรดตามเทรนด์:**

$$\text{Skewness} > 0 \quad (\text{positive skew})$$
$$\text{Kurtosis} > 3 \quad (\text{fat tails, leptokurtic})$$

---

## 4. ระบบค่าเฉลี่ยเคลื่อนที่

### 4.1 ประเภทค่าเฉลี่ยเคลื่อนที่

**ค่าเฉลี่ยเคลื่อนที่อย่างง่าย (Simple Moving Average / SMA):**

$$SMA(n) = \frac{1}{n}\sum_{i=0}^{n-1} P_{t-i}$$

**ค่าเฉลี่ยเคลื่อนที่แบบเอ็กซ์โพเนนเชียล (Exponential Moving Average / EMA):**

$$EMA_t = \alpha P_t + (1-\alpha) EMA_{t-1}$$

โดยที่ $\alpha = \frac{2}{n+1}$ คือตัวประกอบปรับเรียบ

**ค่าเฉลี่ยเคลื่อนที่เอ็กซ์โพเนนเชียลคู่ (Double Exponential Moving Average / DEMA):**

$$DEMA_t = 2 \times EMA(n) - EMA(EMA(n))$$

DEMA ลด Lag โดยการลบเวอร์ชันที่ปรับเรียบอันดับสอง

**ค่าเฉลี่ยเคลื่อนที่เอ็กซ์โพเนนเชียลสาม (Triple Exponential Moving Average / TEMA):**

$$TEMA_t = 3 \times EMA(n) - 3 \times EMA(EMA(n)) + EMA(EMA(EMA(n)))$$

TEMA ลด Lag ได้มากกว่า DEMA

**ค่าเฉลี่ยเคลื่อนที่ Hull (Hull Moving Average / HMA):**

$$HMA(n) = WMA(\sqrt{n}, 2 \times WMA(n/2) - WMA(n))$$

โดยที่ WMA คือค่าเฉลี่ยเคลื่อนที่แบบถ่วงน้ำหนัก (Weighted Moving Average)

### 4.2 การเปรียบเทียบ Lag

| ประเภท MA | Lag (สัมพัทธ์) | ความเรียบ | อัตราสัญญาณหลอก |
|---|---|---|---|
| SMA | สูง (1.0x) | สูง | ต่ำ |
| EMA | กลาง (0.7x) | กลาง | กลาง |
| DEMA | ต่ำ (0.4x) | ต่ำกว่า | สูงกว่า |
| TEMA | ต่ำมาก (0.2x) | ต่ำสุด | สูงสุด |
| HMA | ต่ำ (0.3x) | กลาง | กลาง |

### 4.3 ระบบ Moving Average Crossover

**Golden Cross / Death Cross:**

```
LONG ENTRY:
    Fast MA(n_fast) crosses ABOVE Slow MA(n_slow)
    
SHORT ENTRY:
    Fast MA(n_fast) crosses BELOW Slow MA(n_slow)
    
EXIT:
    Reverse crossover
```

**คู่ MA ที่นิยม:**

| ระบบ | ช่วงเร็ว | ช่วงช้า | กรอบเวลา | เหมาะสำหรับ |
|---|---|---|---|---|
| Scalping | 5 | 20 | M5-M15 | เทรดระหว่างวัน FX |
| ระยะสั้น | 10 | 50 | H1-H4 | Swing Trading |
| ระยะกลาง | 20 | 50 | H4-D1 | Position Trading |
| ระยะยาว | 50 | 200 | D1-W1 | เทรนด์มาโคร |
| Golden/Death Cross | 50 | 200 | D1 | สัญญาณเทรนด์คลาสสิก |

### 4.4 ระบบ Triple Moving Average

ใช้ MA สามตัวเพื่อแยกแยะเทรนด์ระยะสั้น กลาง และยาว:

```
STRONG LONG: Fast > Medium > Slow (all aligned upward)
WEAK LONG: Fast > Slow, but Medium not perfectly aligned
NEUTRAL: Mixed ordering
WEAK SHORT: Fast < Slow, but Medium not perfectly aligned
STRONG SHORT: Fast < Medium < Slow (all aligned downward)

ENTRY: Only enter on STRONG signals
EXIT: When STRONG signal degrades to WEAK or NEUTRAL
```

### 4.5 Moving Average Envelope / แถบเปอร์เซ็นต์

$$\text{Upper Band} = MA(n) \times (1 + p\%)$$
$$\text{Lower Band} = MA(n) \times (1 - p\%)$$

**การเข้าตามเทรนด์:**
- Long เมื่อราคาเบรกเหนือแถบบน (เทรนด์ขึ้นแรง)
- Short เมื่อราคาเบรกใต้แถบล่าง (เทรนด์ลงแรง)

**เปอร์เซ็นต์ตามกรอบเวลา:**

| กรอบเวลา | Envelope % | การประยุกต์ |
|---|---|---|
| M15 | 0.1-0.3% | เทรดระหว่างวัน FX |
| H1 | 0.3-0.5% | ระยะสั้น |
| H4 | 0.5-1.0% | Swing |
| D1 | 1.0-3.0% | Position |

---

## 5. การเบรกเอาท์ Donchian Channel (Turtle Trading)

### 5.1 การสร้าง Donchian Channel

$$\text{Upper Channel}(n) = \max(H_{t-1}, H_{t-2}, \ldots, H_{t-n})$$
$$\text{Lower Channel}(n) = \min(L_{t-1}, L_{t-2}, \ldots, L_{t-n})$$
$$\text{Middle} = \frac{\text{Upper} + \text{Lower}}{2}$$

### 5.2 กฎ Turtle Trading ดั้งเดิม

ระบบ Turtle Trading พัฒนาโดย Richard Dennis และ William Eckhardt ในช่วงทศวรรษ 1980 เป็นหนึ่งในระบบเทรดตามเทรนด์ที่โด่งดังที่สุด

**ระบบที่ 1 (ระยะสั้น):**

| กฎ | ข้อกำหนด |
|---|---|
| เข้า Long | Close > จุดสูง 20 วัน |
| เข้า Short | Close < จุดต่ำ 20 วัน |
| ออก Long | Close < จุดต่ำ 10 วัน |
| ออก Short | Close > จุดสูง 10 วัน |
| กฎข้าม | ข้ามการเข้าหากเบรกเอาท์ก่อนหน้าทำกำไร |
| ขนาดสถานะ | ตาม ATR (ดูหัวข้อ 11) |

**ระบบที่ 2 (ระยะยาว):**

| กฎ | ข้อกำหนด |
|---|---|
| เข้า Long | Close > จุดสูง 55 วัน |
| เข้า Short | Close < จุดต่ำ 55 วัน |
| ออก Long | Close < จุดต่ำ 20 วัน |
| ออก Short | Close > จุดสูง 20 วัน |
| กฎข้าม | ไม่มี (เข้าเสมอ) |
| ขนาดสถานะ | ตาม ATR |

### 5.3 การกำหนดขนาดสถานะแบบ Turtle (ตาม N)

ระบบ Turtle ใช้ "N" (ATR 20 วัน) สำหรับการกำหนดขนาดสถานะ:

$$N = ATR(20)$$

$$\text{Unit Size} = \frac{1\% \text{ of Account}}{N \times \text{Dollar per Point}}$$

**กฎการเพิ่มสถานะ (Pyramiding):**
- เพิ่ม 1 หน่วยทุก $\frac{1}{2}N$ ในทิศทางของการเทรด
- สูงสุด 4 หน่วยต่อตลาด
- สูงสุด 6 หน่วยในตลาดที่มีสหสัมพันธ์สูง
- สูงสุด 12 หน่วยทั้งหมด

### 5.4 Stop ของ Turtle

**Stop เริ่มต้น:**

$$\text{Stop} = \text{Entry Price} \pm 2N$$

**Trailing Stop (ตามช่องราคาออก):**
- Long: Trail ที่จุดต่ำ 10 วัน (ระบบ 1) หรือจุดต่ำ 20 วัน (ระบบ 2)
- Short: Trail ที่จุดสูง 10 วัน (ระบบ 1) หรือจุดสูง 20 วัน (ระบบ 2)

### 5.5 ระบบ Turtle ที่ปรับแต่งสำหรับ Forex/คริปโต

```yaml
modified_turtle:
  entry_channel: 20  # 20-period high/low for entry
  exit_channel: 10   # 10-period high/low for exit
  atr_period: 20
  
  entry_long:
    - Close > Highest High of last 20 bars
    - ADX(14) > 20  # Added trend strength filter
    - Volume > SMA(Volume, 20)  # Volume confirmation
    
  entry_short:
    - Close < Lowest Low of last 20 bars
    - ADX(14) > 20
    - Volume > SMA(Volume, 20)
    
  exit_long:
    - Close < Lowest Low of last 10 bars
    - OR trailing stop at Entry - 2 * ATR(20)
    
  exit_short:
    - Close > Highest High of last 10 bars
    - OR trailing stop at Entry + 2 * ATR(20)
    
  position_sizing:
    risk_per_unit: 1%
    unit_size: (Account * 0.01) / (ATR(20) * pip_value)
    max_units: 4
    pyramid_interval: 0.5 * ATR(20)
    
  filters:
    min_atr_percentile: 30  # Avoid dead markets
    max_correlation: 0.7    # Limit exposure to correlated pairs
```

---

## 6. ความแข็งแกร่งของเทรนด์ด้วย ADX

### 6.1 การคำนวณ ADX

**Directional Movement:**

$$+DM = H_t - H_{t-1} \quad \text{(if positive and > } |L_{t-1} - L_t|, \text{else 0)}$$
$$-DM = L_{t-1} - L_t \quad \text{(if positive and > } H_t - H_{t-1}, \text{else 0)}$$

**Directional Indicators:**

$$+DI(n) = 100 \times \frac{\text{Smoothed}(+DM, n)}{ATR(n)}$$
$$-DI(n) = 100 \times \frac{\text{Smoothed}(-DM, n)}{ATR(n)}$$

**Average Directional Index:**

$$DX = 100 \times \frac{|+DI - (-DI)|}{+DI + (-DI)}$$
$$ADX(n) = \text{Smoothed}(DX, n)$$

### 6.2 การตีความ ADX

| ค่า ADX | ความแข็งแกร่งเทรนด์ | นัยต่อการเทรด |
|---|---|---|
| 0-15 | ไม่มี/อ่อน | หลีกเลี่ยงเทรดตามเทรนด์; ใช้ Mean Reversion |
| 15-25 | กำลังพัฒนา | เตรียมพร้อมเข้า; เฝ้าดู DI Crossover |
| 25-50 | แข็งแกร่ง | เทรดตามเทรนด์เหมาะสม; เข้าและถือ |
| 50-75 | แข็งแกร่งมาก | เทรนด์อาจจะเต็มที่; เฝ้าดูการหมดแรง |
| 75-100 | แข็งแกร่งสุดขีด | พบได้ยาก; อาจกลับตัวรุนแรง |

### 6.3 กลยุทธ์เทรดด้วย ADX

```
ENTRY CONDITIONS:
    LONG:
        1. ADX > 25 (strong trend confirmed)
        2. +DI > -DI (uptrend direction)
        3. +DI crosses above -DI (DI crossover signal)
        4. ADX is rising (trend strengthening)
        
    SHORT:
        1. ADX > 25
        2. -DI > +DI (downtrend direction)
        3. -DI crosses above +DI
        4. ADX is rising

EXIT CONDITIONS:
    1. ADX falls below 20 (trend weakening)
    2. DI lines re-cross (direction change)
    3. ADX peaks and starts declining (trend exhaustion)
    4. Trailing stop at 2 * ATR(14)
```

### 6.4 ตัวกรองคุณภาพเทรนด์ด้วย ADX

ใช้ ADX เป็นตัวกรองสำหรับระบบอื่น (MA Crossover, Breakout):

```
TREND QUALITY SCORE:
    IF ADX > 40 AND rising:     quality = "HIGH"     → Full position
    IF ADX > 25 AND rising:     quality = "MEDIUM"   → 75% position
    IF ADX > 25 AND flat:       quality = "LOW"       → 50% position
    IF ADX < 25:                quality = "NONE"      → No trend trade
```

---

## 7. Parabolic SAR

### 7.1 การคำนวณ Parabolic SAR

Parabolic Stop and Reverse (SAR) เป็นอินดิเคเตอร์เทรดตามเทรนด์ที่ให้จุดเข้าและออกที่เป็นไปได้

**SAR ขาขึ้น:**

$$SAR_{t+1} = SAR_t + AF \times (EP - SAR_t)$$

**SAR ขาลง:**

$$SAR_{t+1} = SAR_t - AF \times (SAR_t - EP)$$

โดยที่:
- $AF$ = Acceleration Factor (เริ่มที่ 0.02, เพิ่ม 0.02 ทุกครั้งที่มี EP ใหม่, สูงสุด 0.20)
- $EP$ = Extreme Point (จุดสูงสุดในขาขึ้น, จุดต่ำสุดในขาลง)

### 7.2 พารามิเตอร์ Parabolic SAR

| พารามิเตอร์ | ค่าเริ่มต้น | แบบอนุรักษ์นิยม | แบบก้าวร้าว |
|---|---|---|---|
| AF เริ่มต้น | 0.02 | 0.01 | 0.03 |
| AF เพิ่มทีละ | 0.02 | 0.01 | 0.03 |
| AF สูงสุด | 0.20 | 0.10 | 0.30 |

- **AF ต่ำ**: ช้ากว่า กลับตัวน้อย อยู่ในเทรนด์นานกว่า Stop กว้างกว่า
- **AF สูง**: เร็วกว่า กลับตัวมาก จับจุดกลับตัวเร็ว Stop แคบกว่า

### 7.3 กลยุทธ์ Parabolic SAR

```
SIGNALS:
    LONG: Price crosses above SAR (SAR flips below price)
    SHORT: Price crosses below SAR (SAR flips above price)
    
STOP: SAR value itself serves as trailing stop
    Long stop = current SAR value (below price)
    Short stop = current SAR value (above price)

ENHANCEMENTS:
    1. Only take long signals when price > EMA(200) (macro trend filter)
    2. Only take short signals when price < EMA(200)
    3. Combine with ADX > 25 filter
    4. Use lower AF (0.01) for trend following, higher AF (0.03) for scalping
```

### 7.4 ข้อจำกัด

- สร้างสัญญาณมากเกินในตลาด Sideway (Whipsaw)
- Acceleration Factor คงที่ไม่ปรับตามความผันผวน
- SAR อาจห่างจากราคามากในช่วงต้นของเทรนด์

---

## 8. อินดิเคเตอร์ Supertrend

### 8.1 การคำนวณ Supertrend

$$\text{Basic Upper Band} = \frac{H + L}{2} + k \times ATR(n)$$

$$\text{Basic Lower Band} = \frac{H + L}{2} - k \times ATR(n)$$

**แถบสุดท้าย (พร้อมการคงอยู่ของเทรนด์):**

$$\text{Final Upper Band}_t = \begin{cases} \text{Basic Upper}_t & \text{if Basic Upper}_t < \text{Final Upper}_{t-1} \text{ OR Close}_{t-1} > \text{Final Upper}_{t-1} \\ \text{Final Upper}_{t-1} & \text{otherwise} \end{cases}$$

$$\text{Final Lower Band}_t = \begin{cases} \text{Basic Lower}_t & \text{if Basic Lower}_t > \text{Final Lower}_{t-1} \text{ OR Close}_{t-1} < \text{Final Lower}_{t-1} \\ \text{Final Lower}_{t-1} & \text{otherwise} \end{cases}$$

**Supertrend:**

$$\text{Supertrend}_t = \begin{cases} \text{Final Lower Band}_t & \text{if Close}_t > \text{Final Upper Band}_{t-1} \text{ (uptrend)} \\ \text{Final Upper Band}_t & \text{if Close}_t < \text{Final Lower Band}_{t-1} \text{ (downtrend)} \\ \text{Supertrend}_{t-1} & \text{otherwise (continue current trend)} \end{cases}$$

### 8.2 พารามิเตอร์ Supertrend

| พารามิเตอร์ | ค่าเริ่มต้น | Forex | คริปโต |
|---|---|---|---|
| คาบ ATR ($n$) | 10 | 10-14 | 10-14 |
| ตัวคูณ ($k$) | 3.0 | 2.0-3.0 | 3.0-5.0 |

**$k$ สูง**: Whipsaw น้อยลง Stop กว้างขึ้น จับเทรนด์น้อยลง
**$k$ ต่ำ**: สัญญาณมากขึ้น Stop แคบขึ้น จับเทรนด์มากขึ้น (Whipsaw มากขึ้น)

### 8.3 กลยุทธ์ Supertrend

```
LONG ENTRY:
    Supertrend flips from above price to below price (color change to green/bullish)
    Entry: Close of the bar that triggers the flip
    Stop: Supertrend value (which is the Final Lower Band)
    
SHORT ENTRY:
    Supertrend flips from below price to above price (color change to red/bearish)
    Entry: Close of the bar that triggers the flip
    Stop: Supertrend value (which is the Final Upper Band)

MULTI-TIMEFRAME SUPERTREND:
    Higher TF (D1): Determines trend direction
    Lower TF (H1): Entry timing
    
    IF D1 Supertrend = LONG:
        Only take H1 LONG signals
    IF D1 Supertrend = SHORT:
        Only take H1 SHORT signals
```

### 8.4 ระบบ Double Supertrend

ใช้ Supertrend สองตัวที่มีพารามิเตอร์ต่างกัน:

```
ST1 = Supertrend(10, 2.0)  # Fast - for entry timing
ST2 = Supertrend(10, 4.0)  # Slow - for trend filter and trailing stop

LONG ENTRY:
    ST2 = bullish (main trend is up)
    AND ST1 flips to bullish (entry timing)
    
    Stop: ST2 value (wider stop from slower indicator)
    Target: Risk-Reward ratio of 2:1 or trail with ST1

SHORT ENTRY:
    ST2 = bearish
    AND ST1 flips to bearish
    
    Stop: ST2 value
    Target: RR 2:1 or trail with ST1
```

---

## 9. Dual Momentum (Gary Antonacci)

### 9.1 แนวคิด

Dual Momentum พัฒนาโดย Gary Antonacci (2014) ผสมผสานโมเมนตัมสองประเภท:

1. **โมเมนตัมสัมบูรณ์ (Absolute Momentum / Time-Series)**: สินทรัพย์มีเทรนด์ขึ้นในเชิงสัมบูรณ์หรือไม่?
2. **โมเมนตัมสัมพัทธ์ (Relative Momentum / Cross-Sectional)**: สินทรัพย์ทำผลงานดีกว่าทางเลือกอื่นหรือไม่?

### 9.2 โมเมนตัมสัมบูรณ์

$$\text{Absolute Momentum} = r_{asset,t-J:t} - r_{risk-free,t-J:t}$$

หากผลตอบแทนส่วนเกินเป็นบวก สินทรัพย์มีโมเมนตัมสัมบูรณ์เป็นบวก

### 9.3 โมเมนตัมสัมพัทธ์

$$\text{Relative Score}_i = r_{i,t-J:t}$$

จัดอันดับสินทรัพย์ผู้สมัครทั้งหมดตามผลตอบแทนช่วง $J$ เลือกสินทรัพย์ $K$ ตัวที่ดีที่สุด

### 9.4 กรอบการตัดสินใจ Dual Momentum

```
Algorithm: Dual Momentum

INPUT:
    assets: list of candidate assets
    lookback: J periods (typically 12 months / 252 days)
    risk_free_rate: current risk-free rate (or T-bill return)
    
FOR each rebalancing period:
    
    1. RELATIVE MOMENTUM:
       - Calculate J-period return for each asset
       - Rank assets by return
       - Select top asset(s)
       
    2. ABSOLUTE MOMENTUM:
       - For selected asset(s), check if J-period return > risk_free_rate
       
    3. DECISION:
       IF relative_winner has positive absolute momentum:
           INVEST in relative_winner
       ELSE:
           INVEST in safe haven (bonds, stablecoins, cash)
           
    4. REBALANCE monthly (or when signal changes)
```

### 9.5 Dual Momentum สำหรับ Forex

```yaml
dual_momentum_forex:
  universe:
    - EUR/USD
    - GBP/USD
    - AUD/USD
    - USD/JPY (inverse)
    - USD/CHF (inverse)
    - NZD/USD
  
  lookback: 63 trading days (3 months) to 252 trading days (12 months)
  
  absolute_benchmark: cash (0% or money market rate)
  
  rules:
    1. Calculate 3-month return for each pair
    2. Select top 2 pairs by return (relative momentum)
    3. For each selected pair, check if return > 0 (absolute momentum)
    4. Go long selected pairs with positive absolute momentum
    5. If no pair has positive absolute momentum, stay in cash
    6. Rebalance monthly
```

### 9.6 Dual Momentum สำหรับคริปโต

```yaml
dual_momentum_crypto:
  universe:
    - BTC/USDT
    - ETH/USDT
    - SOL/USDT
    - BNB/USDT
    - AVAX/USDT
    - Top 10 by market cap (rotated quarterly)
  
  lookback: 21 days (1 month) to 63 days (3 months)
  # Shorter lookback for crypto due to faster cycles
  
  absolute_benchmark: stablecoin yield (e.g., USDT lending rate)
  
  rules:
    1. Calculate 1-month return for each asset
    2. Select top 3 by return (relative momentum)
    3. Check each has positive absolute momentum (> stablecoin yield)
    4. Equal-weight or volatility-weight the selected assets
    5. Rebalance weekly or bi-weekly
    6. If fewer than 2 have positive absolute momentum, increase stablecoin allocation
```

---

## 10. วิกฤตโมเมนตัมและความเสี่ยงปลายหาง

### 10.1 ปรากฏการณ์วิกฤตโมเมนตัม (Momentum Crash)

กลยุทธ์โมเมนตัมมีแนวโน้มที่จะเกิดการขาดทุนอย่างรุนแรงและฉับพลันที่เรียกว่า "Momentum Crashes" สิ่งเหล่านี้เกิดขึ้นเมื่อ:

1. **ตลาดกลับตัว**: หลังเทรนด์ยาวนาน ผู้แพ้ฟื้นตัวอย่างรุนแรงและผู้ชนะร่วง
2. **ความผันผวนพุ่ง**: สภาพแวดล้อมความผันผวนสูงกดผลกำไรโมเมนตัม
3. **Leverage unwind**: สถานะโมเมนตัมที่แออัดถูกคลายพร้อมกัน

**วิกฤตโมเมนตัมในประวัติศาสตร์:**
- Q1 2009: การกลับตัวหลัง GFC ของหุ้น (~40% drawdown สำหรับโมเมนตัม)
- มีนาคม 2020: วิกฤต COVID และการฟื้นตัว
- พฤษภาคม 2021: วิกฤตตลาดคริปโต (60% drawdown สำหรับโมเมนตัมคริปโต)
- พฤศจิกายน 2022: การล่มสลายของ FTX (วิกฤตโมเมนตัม Altcoin รุนแรง)

### 10.2 คุณสมบัติทางสถิติของวิกฤตโมเมนตัม

$$\text{Momentum Return} \sim \text{Left-skewed, Fat-tailed}$$

ในขณะที่การเทรดโมเมนตัมแต่ละครั้งมีความเบ้ขวา (ขาดทุนเล็ก กำไรใหญ่) ปัจจัยโมเมนตัมโดยรวมอาจแสดงความเบ้ซ้ายเนื่องจากเหตุการณ์วิกฤต:

$$\text{Skewness}_{factor} < 0 \quad (\text{negative skew at factor level})$$

**ความผันผวนแบบมีเงื่อนไข:**

$$\sigma_{mom,t} = f(\text{Market Vol}, \text{Recent Drawdown}, \text{Crowding})$$

ความผันผวนของโมเมนตัมเพิ่มขึ้นอย่างมากในช่วงตลาดเครียด

### 10.3 การลดผลกระทบวิกฤตโมเมนตัม

| เทคนิค | คำอธิบาย | ต้นทุน |
|---|---|---|
| การปรับตามความผันผวน (Volatility Scaling) | ลดสถานะเมื่อ Vol สูง | ลดผลตอบแทนในเทรนด์ที่ Vol สูง |
| การป้องกันแบบไดนามิก (Dynamic Hedging) | ซื้อ Put Options บนปัจจัยโมเมนตัม | ค่าพรีเมียม |
| Stop เมื่อ Drawdown สูงสุด | ลด Exposure เมื่อ DD > เกณฑ์ | อาจออกก่อนการฟื้นตัว |
| การกระจายความเสี่ยง | เทรดโมเมนตัมข้ามตลาดที่ไม่สัมพันธ์กัน | ลดการกระจุกตัว |
| การผสมช่วงถือครอง | ผสมหลาย Lookback Period | ทำให้ผลตอบแทนราบรื่น ลดสุดขีด |
| ผสมโมเมนตัม + มูลค่า | ผสมกับ Mean Reversion | ลด Drawdown แต่อาจลดผลตอบแทน |

### 10.4 โมเมนตัมที่ปรับตามความผันผวน (Volatility-Scaled Momentum)

**Barroso and Santa-Clara (2015):**

$$w_t = \frac{\sigma_{target}}{\hat{\sigma}_{mom,t}} \times \text{raw\_momentum\_weight}$$

โดยที่ $\hat{\sigma}_{mom,t}$ คือความผันผวนจริงของกลยุทธ์โมเมนตัมในช่วง 6 เดือนที่ผ่านมา

"โมเมนตัมที่บริหารความเสี่ยง" นี้ลด Drawdown อย่างมีนัยสำคัญและปรับปรุง Sharpe Ratio

### 10.5 แบบจำลองขาดทุนสูงสุด

$$VaR_{1\%} = \mu_{mom} - z_{0.01} \times \sigma_{mom}$$

$$CVaR_{1\%} = E[R | R < VaR_{1\%}]$$

สำหรับกลยุทธ์โมเมนตัมทั่วไป:
- $VaR_{1\%, daily}$ = -2% ถึง -5%
- $CVaR_{1\%, daily}$ = -3% ถึง -8%
- ขาดทุนรายเดือนสูงสุดที่สังเกตได้: -15% ถึง -30%

---

## 11. การกำหนดขนาดสถานะสำหรับเทรดตามเทรนด์

### 11.1 การกำหนดขนาดสถานะตาม ATR

แนวทางมาตรฐานอุตสาหกรรมสำหรับการกำหนดขนาดสถานะเทรดตามเทรนด์:

$$\text{Position Size} = \frac{\text{Account} \times \text{Risk\%}}{N \times \text{Dollar Per Point}}$$

โดยที่:
- $\text{Account}$ = เงินทุนทั้งหมดในบัญชี
- $\text{Risk\%}$ = เปอร์เซ็นต์ของบัญชีที่เสี่ยงต่อการเทรด (โดยทั่วไป 1-2%)
- $N$ = Average True Range (ATR) ตัววัดความผันผวน
- $\text{Dollar Per Point}$ = มูลค่าของการเคลื่อนไหว 1 จุด/pip สำหรับหนึ่งหน่วย

### 11.2 การอนุมาน

เป้าหมายคือเพื่อให้แน่ใจว่าการเคลื่อนไหวตรงข้าม $1N$ จะทำให้ขาดทุนเท่ากับ $\text{Risk\%}$ พอดี:

$$\text{Loss if price moves } 1N = \text{Position Size} \times N \times \text{Dollar Per Point}$$

ตั้งให้เท่ากับความเสี่ยงที่ต้องการ:

$$\text{Position Size} \times N \times \text{Dollar Per Point} = \text{Account} \times \text{Risk\%}$$

$$\therefore \text{Position Size} = \frac{\text{Account} \times \text{Risk\%}}{N \times \text{Dollar Per Point}}$$

### 11.3 ตัวอย่างการกำหนดขนาดสถานะ

**ตัวอย่าง Forex (EUR/USD บนบัญชี $100,000):**

| พารามิเตอร์ | ค่า |
|---|---|
| บัญชี | $100,000 |
| ความเสี่ยงต่อเทรด | 1% = $1,000 |
| ATR(20) | 0.0080 (80 pips) |
| Dollar per pip (standard lot) | $10 |
| ระยะ Stop | 2N = 160 pips |
| ความเสี่ยงต่อเทรด / (Stop in pips * pip value) | $1,000 / (160 * $10) |
| ขนาดสถานะ | 0.625 lots (~62,500 หน่วย) |

**ตัวอย่างคริปโต (BTC/USDT บนบัญชี $50,000):**

| พารามิเตอร์ | ค่า |
|---|---|
| บัญชี | $50,000 |
| ความเสี่ยงต่อเทรด | 2% = $1,000 |
| ATR(20) | $2,500 |
| ราคา BTC | $50,000 |
| ระยะ Stop | 2N = $5,000 |
| ขนาดสถานะ (USD notional) | $1,000 / ($5,000/$50,000) = $10,000 |
| ขนาดสถานะ (BTC) | 0.20 BTC |

### 11.4 การเพิ่มสถานะ (Pyramiding — เพิ่มในสถานะที่กำไร)

การเพิ่มสถานะแบบ Turtle เพิ่มหน่วยเมื่อเทรดเคลื่อนไปในทิศทางที่ดี:

```
PYRAMIDING RULES:
    Initial entry: 1 unit at Entry Price
    Add 1 unit at: Entry + 0.5N
    Add 1 unit at: Entry + 1.0N
    Add 1 unit at: Entry + 1.5N
    Maximum: 4 units
    
    Stop adjustments:
    After 2nd unit: Move all stops to Entry - 1.5N
    After 3rd unit: Move all stops to Entry - 0.5N
    After 4th unit: Move all stops to Entry + 0.5N (breakeven+)
    
RISK CALCULATION (all units):
    Total risk = sum of (entry_price_i - stop) * position_size_i
    Should not exceed 4-5% of account for all units combined
```

### 11.5 การจัดสรรพอร์ตโฟลิโอตามความผันผวน

สำหรับพอร์ตโฟลิโอของกลยุทธ์เทรดตามเทรนด์ข้ามสินทรัพย์หลายตัว:

$$w_i = \frac{1/\hat{\sigma}_i}{\sum_j 1/\hat{\sigma}_j}$$

การถ่วงน้ำหนักความผันผวนแบบผกผัน (Inverse-Volatility Weighting) ทำให้แต่ละสถานะมีส่วนสนับสนุนความเสี่ยงเท่ากัน

**การกำหนดขนาดแบบ Risk Parity:**

$$\text{Risk Contribution}_i = w_i \times \beta_i \times \sigma_p$$

โดยที่เป้าหมายการสนับสนุนความเสี่ยงเท่ากัน:

$$\text{RC}_1 = \text{RC}_2 = \ldots = \text{RC}_n = \frac{\sigma_p}{n}$$

---

## 12. การตรวจจับสภาวะตลาด (Regime Detection)

### 12.1 ความสำคัญของการตรวจจับสภาวะตลาด

การเทรดตามเทรนด์ทำผลงานดีในสภาวะเทรนด์แต่แย่ในสภาวะ Sideway การตรวจจับสภาวะตลาดช่วยให้:
- เปิดใช้เทรดตามเทรนด์ในช่วงเทรนด์
- ลดขนาดสถานะหรือสลับไป Mean Reversion ในช่วง Sideway
- หลีกเลี่ยงการขาดทุนจาก Whipsaw

### 12.2 การตรวจจับสภาวะตลาดด้วย ADX

```
REGIME CLASSIFICATION (Simple):
    IF ADX > 25 AND ADX is rising:
        regime = "TRENDING"
        strategy = TREND_FOLLOWING
        
    IF ADX < 20 OR (ADX > 25 AND ADX is falling):
        regime = "RANGING"
        strategy = MEAN_REVERSION or NO_TRADE
        
    IF ADX between 20-25:
        regime = "TRANSITION"
        strategy = REDUCED_SIZE
```

### 12.3 สภาวะตลาดจากความชันของ Moving Average

$$\text{MA Slope} = \frac{MA(n)_t - MA(n)_{t-k}}{k}$$

$$\text{Normalized Slope} = \frac{\text{MA Slope}}{ATR(n)}$$

| Normalized Slope | สภาวะ | การดำเนินการ |
|---|---|---|
| > +0.5 | เทรนด์ขึ้นแรง | เทรดตามเทรนด์ Long |
| +0.2 ถึง +0.5 | เทรนด์ขึ้นอ่อน | เทรดตามเทรนด์อย่างระมัดระวัง |
| -0.2 ถึง +0.2 | Ranging | Mean Reversion หรืออยู่ข้างสนาม |
| -0.5 ถึง -0.2 | เทรนด์ลงอ่อน | เทรดตามเทรนด์อย่างระมัดระวัง |
| < -0.5 | เทรนด์ลงแรง | เทรดตามเทรนด์ Short |

### 12.4 การตรวจจับสภาวะจากความผันผวน

$$\sigma_{ratio} = \frac{\sigma_{short}(n_1)}{\sigma_{long}(n_2)}$$

โดยที่ $n_1 < n_2$ (เช่น $n_1=10$, $n_2=60$)

| $\sigma_{ratio}$ | สภาวะ | การดำเนินการ |
|---|---|---|
| > 1.5 | ความผันผวนขยายตัว | ลดขนาด ขยาย Stop |
| 1.0-1.5 | ความผันผวนปกติ | พารามิเตอร์มาตรฐาน |
| 0.7-1.0 | ความผันผวนหดตัว | เตรียมสำหรับ Breakout |
| < 0.7 | ความผันผวนต่ำ (Squeeze) | คาดหวังการเคลื่อนไหวใหญ่; เตรียมเข้าเทรนด์ |

### 12.5 Hidden Markov Model (HMM) สำหรับการตรวจจับสภาวะ

จำลองตลาดว่ามี $K$ สถานะซ่อน (เช่น เทรนด์ขึ้น, เทรนด์ลง, Ranging):

$$P(\text{State}_t = k | \text{observations}) = \text{Forward-Backward Algorithm}$$

**สถานะ:**
- สถานะ 1: ความผันผวนต่ำ, Ranging (ใช้ Mean Reversion)
- สถานะ 2: ความผันผวนสูง, มีเทรนด์ (ใช้เทรดตามเทรนด์)
- สถานะ 3: วิกฤต/ตกลงแรง (ใช้การวางตำแหน่งป้องกัน)

**เมทริกซ์การเปลี่ยนผ่าน:**

$$A = \begin{bmatrix} P(1 \to 1) & P(1 \to 2) & P(1 \to 3) \\ P(2 \to 1) & P(2 \to 2) & P(2 \to 3) \\ P(3 \to 1) & P(3 \to 2) & P(3 \to 3) \end{bmatrix}$$

การคงอยู่ทั่วไป: $P(i \to i) > 0.90$ (สภาวะมีความ "เหนียว")

### 12.6 อินดิเคเตอร์สภาวะตลาดแบบผสม

```
Algorithm: Composite Regime Score

INPUTS:
    adx = ADX(14)
    hurst = Hurst_Exponent(100)
    vol_ratio = sigma_short / sigma_long
    ma_slope = normalized MA slope
    
TRENDING_SCORE:
    ts = 0
    IF adx > 25: ts += 0.3
    IF adx > 35: ts += 0.1
    IF hurst > 0.55: ts += 0.25
    IF abs(ma_slope) > 0.3: ts += 0.2
    IF vol_ratio > 1.2: ts += 0.15
    
RANGING_SCORE:
    rs = 0
    IF adx < 20: rs += 0.3
    IF hurst < 0.45: rs += 0.25
    IF abs(ma_slope) < 0.1: rs += 0.2
    IF vol_ratio < 0.8: rs += 0.15
    IF BBW < percentile_25: rs += 0.1
    
REGIME:
    IF ts > 0.6: "TRENDING"
    ELIF rs > 0.6: "RANGING"
    ELSE: "TRANSITION"
```

---

## 13. ตรรกะหลัก — การเข้า/ออกสถานะ

### 13.1 ตรรกะการเข้าเทรดตามเทรนด์แบบสากล

```
Algorithm: Composite Trend Following Entry

INDICATORS:
    ma_fast = EMA(close, fast_period)
    ma_slow = EMA(close, slow_period)
    adx = ADX(close, 14)
    plus_di = +DI(14)
    minus_di = -DI(14)
    donchian_upper = Highest(high, channel_period)
    donchian_lower = Lowest(low, channel_period)
    supertrend, st_direction = Supertrend(atr_period, st_multiplier)
    atr = ATR(atr_period)
    
REGIME:
    regime = composite_regime_score(close)
    IF regime != "TRENDING": SKIP (no trend entry)

LONG ENTRY (composite scoring):
    score = 0
    
    # MA Crossover
    IF ma_fast > ma_slow AND ma_fast[1] <= ma_slow[1]:  # Fresh crossover
        score += 0.25
    ELIF ma_fast > ma_slow:  # Ongoing uptrend
        score += 0.15
    
    # Donchian Breakout
    IF close > donchian_upper:
        score += 0.25
    
    # ADX + DI
    IF adx > 25 AND plus_di > minus_di:
        score += 0.20
    
    # Supertrend
    IF st_direction == BULLISH:
        score += 0.15
    
    # Price above long-term MA
    IF close > EMA(close, 200):
        score += 0.15
    
    IF score >= 0.60:
        SIGNAL = LONG
        entry = close
        stop = close - 2 * atr
        target = close + 3 * atr  # or trailing
        size = (Account * Risk%) / (2 * atr * dollar_per_point)

SHORT ENTRY (mirror logic):
    score = 0
    IF ma_fast < ma_slow AND ma_fast[1] >= ma_slow[1]:
        score += 0.25
    ELIF ma_fast < ma_slow:
        score += 0.15
    IF close < donchian_lower:
        score += 0.25
    IF adx > 25 AND minus_di > plus_di:
        score += 0.20
    IF st_direction == BEARISH:
        score += 0.15
    IF close < EMA(close, 200):
        score += 0.15
    
    IF score >= 0.60:
        SIGNAL = SHORT
```

### 13.2 การจัดการการออกและ Trail

```
Algorithm: Trend Following Exit Management

TRAILING STOP OPTIONS (select one based on strategy):

    Option A: ATR Trailing Stop
        trail_long = max(trail_long_prev, close - k * atr)
        trail_short = min(trail_short_prev, close + k * atr)
        k = 2.0 to 3.0
    
    Option B: Donchian Channel Exit
        trail_long = Lowest(low, exit_channel_period)  # e.g., 10 bars
        trail_short = Highest(high, exit_channel_period)
    
    Option C: Supertrend Exit
        trail_long = supertrend value (when bullish)
        trail_short = supertrend value (when bearish)
    
    Option D: Parabolic SAR
        trail = parabolic_sar value
    
    Option E: Moving Average Exit
        trail_long = EMA(close, exit_ma_period)
        trail_short = EMA(close, exit_ma_period)

EXIT CONDITIONS:
    IF position == LONG:
        IF close < trailing_stop: EXIT
        IF regime changed to RANGING: EXIT (or reduce size)
        IF time_in_trade > max_duration: EVALUATE
        IF unrealized_profit > 5R: Consider partial exit
        
    IF position == SHORT:
        IF close > trailing_stop: EXIT
        IF regime changed to RANGING: EXIT
```

### 13.3 ตรรกะการเพิ่มสถานะ (Pyramiding)

```
Algorithm: Turtle-Style Pyramiding

PARAMETERS:
    max_units = 4
    pyramid_interval = 0.5 * ATR(20)
    
ON_POSITION_UPDATE:
    IF position is LONG AND num_units < max_units:
        IF close > last_add_price + pyramid_interval:
            # Add another unit
            new_unit_size = base_unit_size  # Same size as initial
            total_position += new_unit_size
            last_add_price = close
            num_units += 1
            
            # Adjust stops for all units
            new_stop = close - 2 * ATR(20)
            FOR each unit:
                unit.stop = max(unit.stop, new_stop)
            
            LOG: "Pyramided to {num_units} units at {close}"
    
    # Ensure total risk doesn't exceed limits
    total_risk = sum((entry_i - stop) * size_i for each unit)
    IF total_risk > max_portfolio_risk * account:
        REDUCE position proportionally
```

---

## 14. ข้อมูลจำเพาะทางเทคนิค

### 14.1 การกำหนดค่าระบบ

```yaml
trend_following_config:
  # Moving Average System
  ma_system:
    fast_ma_type: EMA
    fast_period: 20
    slow_ma_type: EMA
    slow_period: 50
    signal_type: crossover  # or price_above_ma
    
  # Donchian Channel
  donchian:
    entry_period: 20
    exit_period: 10
    
  # ADX
  adx:
    period: 14
    trend_threshold: 25
    strong_threshold: 40
    
  # Supertrend
  supertrend:
    atr_period: 10
    multiplier: 3.0
    
  # Position Sizing
  position_sizing:
    method: atr_based
    risk_per_trade: 0.01  # 1% of account
    atr_period: 20
    stop_multiplier: 2.0  # 2N stop
    max_units: 4
    pyramid_interval_N: 0.5
    
  # Trailing Stop
  trailing:
    method: donchian_exit  # or atr_trail, supertrend, parabolic_sar
    atr_multiplier: 2.5
    donchian_exit_period: 10
    
  # Risk Limits
  risk_limits:
    max_portfolio_heat: 0.06  # 6% total portfolio risk
    max_correlated_exposure: 0.04  # 4% in correlated markets
    max_single_market: 0.02  # 2% per market
    max_drawdown_pause: 0.10  # Pause trading at 10% drawdown
```

### 14.2 การกำหนดค่าเฉพาะสินทรัพย์

**Forex:**

```yaml
forex_trend_config:
  pairs:
    EUR/USD:
      min_atr_pips: 40
      max_spread_pips: 1.5
      session_filter: london_ny
      ma_fast: 20
      ma_slow: 50
      
    GBP/JPY:
      min_atr_pips: 80
      max_spread_pips: 3.0
      session_filter: london
      ma_fast: 15
      ma_slow: 40
      
    AUD/USD:
      min_atr_pips: 30
      max_spread_pips: 1.5
      session_filter: sydney_london
      ma_fast: 20
      ma_slow: 50
```

**คริปโต:**

```yaml
crypto_trend_config:
  assets:
    BTC/USDT:
      min_atr_pct: 1.5%
      max_spread_pct: 0.05%
      session_filter: none  # 24/7
      supertrend_mult: 3.0
      funding_rate_check: true
      
    ETH/USDT:
      min_atr_pct: 2.0%
      max_spread_pct: 0.05%
      supertrend_mult: 3.5
      
    Altcoins:
      min_atr_pct: 3.0%
      max_spread_pct: 0.10%
      supertrend_mult: 4.0
      liquidity_min_24h_volume: $10M
```

---

## 15. แบบจำลองทางคณิตศาสตร์

### 15.1 แบบจำลองผลตอบแทนปัจจัยโมเมนตัม

ผลตอบแทนปัจจัยโมเมนตัมสามารถจำลองได้เป็น:

$$r_{mom,t} = \alpha + \beta_{mkt} r_{mkt,t} + \beta_{vol} \Delta\sigma_t + \epsilon_t$$

โดยที่:
- $\alpha$ = Alpha ของโมเมนตัม (ผลตอบแทนส่วนเกิน)
- $\beta_{mkt}$ = Beta ตลาด (โดยทั่วไปใกล้ 0 สำหรับโมเมนตัม L/S)
- $\beta_{vol}$ = Beta ความผันผวน (ลบ — โมเมนตัมเสียหายเมื่อ Vol พุ่ง)

### 15.2 การเทรดตามเทรนด์เป็น Straddle

ผลตอบแทนเทรดตามเทรนด์ประมาณ **Long Straddle** payoff:

$$\text{TF Return} \approx a|r_{mkt}| - c$$

โดยที่:
- $a$ = ความไวต่อการเคลื่อนไหวตลาดสัมบูรณ์
- $c$ = ต้นทุน Whipsaw (เหมือนพรีเมียมออปชัน)

หมายความว่าการเทรดตามเทรนด์:
- กำไรจากการเคลื่อนไหวใหญ่ในทั้งสองทิศทาง
- ขาดทุนในช่วงเคลื่อนไหวเล็กๆ สับไปมา ("พรีเมียม" ของ Straddle)

**Fung and Hsieh (2001) Lookback Straddle:**

$$\text{TF Factor} = \max(S_T - S^*, 0) + \max(S^{**} - S_T, 0) - \text{Premium}$$

โดยที่ $S^*$ และ $S^{**}$ คือราคาสูงสุดและต่ำสุดสะสม

### 15.3 แบบจำลองความน่าจะเป็นของ Breakout

ความน่าจะเป็นที่ Donchian Channel Breakout จะนำไปสู่เทรนด์ต่อเนื่อง:

$$P(\text{true breakout}) = P(\text{trend regime}) \times P(\text{breakout | trend})$$

จากการวิเคราะห์ประวัติศาสตร์:
- $P(\text{true breakout}) \approx 0.30-0.40$
- อัตราชนะของเทรดตามเทรนด์: ~35%
- อัตราส่วน Average Win / Average Loss ที่ต้องการเพื่อทำกำไร: > 2.0

**อัตราส่วนผลตอบแทนที่ต้องการ:**

$$\frac{W_{avg}}{L_{avg}} > \frac{1-p}{p} = \frac{1-0.35}{0.35} = 1.86$$

ดังนั้นเทรดที่ชนะเฉลี่ยต้องมีอย่างน้อย 1.86 เท่าของเทรดที่แพ้เฉลี่ย

### 15.4 ช่วง Moving Average ที่เหมาะสม

Brock, Lakonishok, and LeBaron (1992) ทดสอบกฎ MA ต่างๆ ความยาว MA ที่เหมาะสมขึ้นอยู่กับวัฏจักรหลัก:

$$n_{optimal} \approx \frac{T_{cycle}}{2\pi} \times \sqrt{2}$$

โดยที่ $T_{cycle}$ คือความยาววัฏจักรราคาหลัก

**แนวทางปฏิบัติ:**
- สำหรับวัฏจักรหลัก 40 วัน: $n_{opt} \approx 9$ แท่ง
- สำหรับวัฏจักรหลัก 100 วัน: $n_{opt} \approx 22$ แท่ง
- สำหรับวัฏจักรหลัก 200 วัน: $n_{opt} \approx 45$ แท่ง

### 15.5 Sharpe Ratio ของเทรดตามเทรนด์

Sharpe Ratio ทางทฤษฎีของกลยุทธ์เทรดตามเทรนด์บริสุทธิ์:

$$SR_{TF} = \frac{|\mu|}{\sigma} \times \rho_{signal}$$

โดยที่:
- $|\mu|/\sigma$ = Sharpe Ratio ของสินทรัพย์อ้างอิง
- $\rho_{signal}$ = สหสัมพันธ์ระหว่างสัญญาณกับผลตอบแทนในอนาคต

สำหรับ MA Crossover อย่างง่าย:

$$\rho_{signal} \approx \frac{n_{slow} - n_{fast}}{n_{slow} + n_{fast}} \times \frac{|\mu|}{\sigma}$$

---

## 16. พารามิเตอร์ความเสี่ยง

### 16.1 สรุปการกำหนดขนาดสถานะ

| แนวทาง | สูตร | เหมาะสำหรับ |
|---|---|---|
| Fixed Fractional | $Q = (f \times W) / (\text{Stop Distance})$ | เทรดตามเทรนด์ทั่วไป |
| ตาม ATR | $Q = (R\% \times W) / (N \times \$/point)$ | ระบบแบบ Turtle |
| Volatility Parity | $w_i = (1/\sigma_i) / \sum(1/\sigma_j)$ | พอร์ตโฟลิโอหลายสินทรัพย์ |
| Kelly Criterion | $f = (pb - q) / b$ | การเติบโตสูงสุด (ใช้ Half-Kelly) |

### 16.2 พารามิเตอร์ Stop Loss

| ระบบ | Stop เริ่มต้น | Trailing Stop |
|---|---|---|
| MA Crossover | 2-3x ATR จากจุดเข้า | MA ตัดกลับ (หรือ MA ที่เร็วกว่า) |
| Donchian Breakout | 2N จากจุดเข้า | จุดต่ำ/สูง 10 วัน (ระบบ 1) |
| ระบบ ADX | 2x ATR | ADX ลงต่ำกว่า 20 |
| Parabolic SAR | ค่า SAR | ค่า SAR (Trail อัตโนมัติ) |
| Supertrend | ค่าแถบ Supertrend | Supertrend พลิก |

### 16.3 ขีดจำกัดความเสี่ยงพอร์ตโฟลิโอ (Portfolio Heat)

$$\text{Portfolio Heat} = \sum_i |\text{Risk}_i| = \sum_i |(\text{Entry}_i - \text{Stop}_i) \times Q_i|$$

| ระดับความเสี่ยง | Portfolio Heat สูงสุด | สูงสุดต่อตลาด | สูงสุดกลุ่มสหสัมพันธ์ |
|---|---|---|---|
| อนุรักษ์นิยม | 4% | 1% | 2% |
| ปานกลาง | 6% | 1.5% | 3% |
| ก้าวร้าว | 10% | 2% | 5% |

### 16.4 การจัดการ Drawdown

```
DRAWDOWN RESPONSE PROTOCOL:

DD < 5%:   Normal operations
DD 5-10%:  Reduce position sizes by 25%
DD 10-15%: Reduce position sizes by 50%
DD 15-20%: Reduce position sizes by 75%, no new positions
DD > 20%:  Halt trading, review strategy, possible full exit

RECOVERY:
    After DD peak, restore normal sizing gradually:
    When DD reduces to 50% of peak: Restore to 50% size
    When DD reduces to 25% of peak: Restore to 75% size
    When new equity high: Restore full size
```

### 16.5 ขีดจำกัดความเสี่ยงตามสหสัมพันธ์

```yaml
correlation_limits:
  max_pairwise_correlation: 0.70
  # If two positions have > 0.70 correlation, treat as one position for sizing
  
  correlation_groups:
    usd_group: [EUR/USD, GBP/USD, AUD/USD]
    jpy_group: [USD/JPY, EUR/JPY, GBP/JPY]
    crypto_major: [BTC, ETH]
    crypto_alt: [SOL, AVAX, DOT]
    
  max_group_exposure: 3%  # Max risk per correlated group
  max_total_directional: 5%  # Max net directional risk
```

---

## 17. ขั้นตอนการดำเนินการ

### 17.1 ระบบเทรดตามเทรนด์ฉบับสมบูรณ์ — Pseudocode

```python
class TrendFollowingSystem:
    """
    Complete Trend Following Trading System
    Supports: MA, Donchian, ADX, Supertrend, Dual Momentum
    Markets: Forex, Crypto
    """
    
    def __init__(self, config):
        self.config = config
        self.positions = {}       # symbol -> position info
        self.portfolio_heat = 0.0
        self.peak_equity = config['initial_capital']
        self.current_equity = config['initial_capital']
        
    def calculate_indicators(self, symbol, data):
        """Step 1: Calculate all trend indicators."""
        close = data['close']
        high = data['high']
        low = data['low']
        
        ind = {}
        
        # Moving Averages
        ind['ema_fast'] = EMA(close, self.config['ma_fast'])
        ind['ema_slow'] = EMA(close, self.config['ma_slow'])
        ind['ema_200'] = EMA(close, 200)
        
        # Donchian Channels
        ind['don_upper'] = rolling_max(high, self.config['donchian_entry'])
        ind['don_lower'] = rolling_min(low, self.config['donchian_entry'])
        ind['don_exit_upper'] = rolling_max(high, self.config['donchian_exit'])
        ind['don_exit_lower'] = rolling_min(low, self.config['donchian_exit'])
        
        # ADX
        ind['adx'], ind['plus_di'], ind['minus_di'] = ADX(high, low, close, 14)
        
        # Supertrend
        ind['supertrend'], ind['st_direction'] = supertrend(
            high, low, close,
            self.config['st_atr_period'],
            self.config['st_multiplier']
        )
        
        # ATR
        ind['atr'] = ATR(high, low, close, self.config['atr_period'])
        
        return ind
    
    def detect_regime(self, symbol, data, indicators):
        """Step 2: Determine market regime."""
        adx = indicators['adx'][-1]
        hurst = calculate_hurst(data['close'][-100:])
        
        trending_score = 0
        if adx > 25: trending_score += 0.35
        if adx > 35: trending_score += 0.15
        if hurst > 0.55: trending_score += 0.25
        ma_slope = (indicators['ema_slow'][-1] - indicators['ema_slow'][-10]) / \
                   (10 * indicators['atr'][-1])
        if abs(ma_slope) > 0.3: trending_score += 0.25
        
        if trending_score > 0.6:
            return 'TRENDING'
        elif trending_score < 0.3:
            return 'RANGING'
        else:
            return 'TRANSITION'
    
    def generate_signal(self, symbol, data, indicators, regime):
        """Step 3: Generate trend following signal."""
        if regime != 'TRENDING':
            return None
            
        close = data['close'][-1]
        score = 0
        direction = None
        
        # Evaluate LONG signals
        long_score = 0
        if indicators['ema_fast'][-1] > indicators['ema_slow'][-1]:
            long_score += 0.20
            if indicators['ema_fast'][-2] <= indicators['ema_slow'][-2]:
                long_score += 0.10  # Fresh crossover bonus
        if close > indicators['don_upper'][-2]:  # Breakout
            long_score += 0.25
        if indicators['adx'][-1] > 25 and indicators['plus_di'][-1] > indicators['minus_di'][-1]:
            long_score += 0.20
        if indicators['st_direction'][-1] == 1:  # Bullish
            long_score += 0.15
        if close > indicators['ema_200'][-1]:
            long_score += 0.10
            
        # Evaluate SHORT signals
        short_score = 0
        if indicators['ema_fast'][-1] < indicators['ema_slow'][-1]:
            short_score += 0.20
            if indicators['ema_fast'][-2] >= indicators['ema_slow'][-2]:
                short_score += 0.10
        if close < indicators['don_lower'][-2]:
            short_score += 0.25
        if indicators['adx'][-1] > 25 and indicators['minus_di'][-1] > indicators['plus_di'][-1]:
            short_score += 0.20
        if indicators['st_direction'][-1] == -1:  # Bearish
            short_score += 0.15
        if close < indicators['ema_200'][-1]:
            short_score += 0.10
        
        # Select direction
        if long_score >= 0.60 and long_score > short_score:
            direction = 'LONG'
            score = long_score
        elif short_score >= 0.60 and short_score > long_score:
            direction = 'SHORT'
            score = short_score
        else:
            return None
            
        atr = indicators['atr'][-1]
        stop_distance = self.config['stop_multiplier'] * atr
        
        return {
            'symbol': symbol,
            'direction': direction,
            'score': score,
            'entry': close,
            'stop': close - stop_distance if direction == 'LONG' else close + stop_distance,
            'atr': atr,
        }
    
    def calculate_position_size(self, signal):
        """Step 4: ATR-based position sizing."""
        risk_amount = self.current_equity * self.config['risk_per_trade']
        stop_distance = abs(signal['entry'] - signal['stop'])
        dollar_per_point = self.get_dollar_per_point(signal['symbol'])
        
        position_size = risk_amount / (stop_distance * dollar_per_point)
        
        # Check portfolio heat limits
        new_heat = self.portfolio_heat + risk_amount
        if new_heat > self.current_equity * self.config['max_portfolio_heat']:
            position_size *= (self.current_equity * self.config['max_portfolio_heat'] - self.portfolio_heat) / risk_amount
        
        # Drawdown adjustment
        dd = (self.peak_equity - self.current_equity) / self.peak_equity
        if dd > 0.10:
            position_size *= 0.50
        elif dd > 0.05:
            position_size *= 0.75
            
        return max(0, position_size)
    
    def manage_positions(self, current_data, indicators):
        """Step 5: Manage open positions — trailing stops and exits."""
        for symbol, pos in list(self.positions.items()):
            close = current_data[symbol]['close'][-1]
            atr = indicators[symbol]['atr'][-1]
            
            # Update trailing stop
            if self.config['trail_method'] == 'atr':
                if pos['direction'] == 'LONG':
                    new_trail = close - self.config['trail_multiplier'] * atr
                    pos['trail_stop'] = max(pos.get('trail_stop', pos['stop']), new_trail)
                else:
                    new_trail = close + self.config['trail_multiplier'] * atr
                    pos['trail_stop'] = min(pos.get('trail_stop', pos['stop']), new_trail)
                    
            elif self.config['trail_method'] == 'donchian':
                if pos['direction'] == 'LONG':
                    pos['trail_stop'] = indicators[symbol]['don_exit_lower'][-1]
                else:
                    pos['trail_stop'] = indicators[symbol]['don_exit_upper'][-1]
            
            # Check exit conditions
            should_exit = False
            reason = ""
            
            if pos['direction'] == 'LONG' and close < pos['trail_stop']:
                should_exit = True
                reason = "Trailing stop hit"
            elif pos['direction'] == 'SHORT' and close > pos['trail_stop']:
                should_exit = True
                reason = "Trailing stop hit"
            
            # Regime change exit
            regime = self.detect_regime(symbol, current_data[symbol], indicators[symbol])
            if regime == 'RANGING' and pos.get('bars_held', 0) > 5:
                should_exit = True
                reason = "Regime changed to ranging"
            
            if should_exit:
                self.close_position(symbol, close, reason)
                
            # Pyramiding check
            elif pos.get('num_units', 1) < self.config['max_units']:
                pyramid_interval = self.config['pyramid_interval_N'] * atr
                if pos['direction'] == 'LONG' and close > pos['last_add_price'] + pyramid_interval:
                    self.add_unit(symbol, close)
                elif pos['direction'] == 'SHORT' and close < pos['last_add_price'] - pyramid_interval:
                    self.add_unit(symbol, close)
    
    def run(self, data_feed):
        """Step 6: Main execution loop."""
        for timestamp, market_data in data_feed:
            all_indicators = {}
            all_regimes = {}
            all_signals = []
            
            # Calculate indicators and signals for all symbols
            for symbol in self.config['symbols']:
                data = market_data[symbol]
                indicators = self.calculate_indicators(symbol, data)
                regime = self.detect_regime(symbol, data, indicators)
                signal = self.generate_signal(symbol, data, indicators, regime)
                
                all_indicators[symbol] = indicators
                all_regimes[symbol] = regime
                if signal:
                    all_signals.append(signal)
            
            # Manage existing positions
            self.manage_positions(market_data, all_indicators)
            
            # Process new signals (sorted by score)
            all_signals.sort(key=lambda s: s['score'], reverse=True)
            
            for signal in all_signals:
                if signal['symbol'] not in self.positions:
                    size = self.calculate_position_size(signal)
                    if size > 0:
                        self.open_position(signal, size)
            
            # Update equity tracking
            self.update_equity(market_data)
            self.peak_equity = max(self.peak_equity, self.current_equity)
```

### 17.2 แผนภาพขั้นตอนการดำเนินการ

```
┌───────────────────────────────────────────────┐
│      TREND FOLLOWING EXECUTION FLOW           │
├───────────────────────────────────────────────┤
│                                               │
│  1. DATA INGESTION                            │
│     ├─ Receive new bar for all symbols        │
│     └─ Update price history buffers           │
│                                               │
│  2. INDICATOR CALCULATION                     │
│     ├─ EMA Fast/Slow/200                      │
│     ├─ Donchian Channels (entry/exit)         │
│     ├─ ADX, +DI, -DI                         │
│     ├─ Supertrend                             │
│     ├─ ATR                                    │
│     └─ Parabolic SAR (optional)               │
│                                               │
│  3. REGIME DETECTION                          │
│     ├─ ADX threshold check                    │
│     ├─ Hurst exponent                         │
│     ├─ MA slope analysis                      │
│     └─ Classify: TRENDING / RANGING / TRANS   │
│                                               │
│  4. SIGNAL GENERATION                         │
│     ├─ Score MA crossover                     │
│     ├─ Score Donchian breakout                │
│     ├─ Score ADX + DI                         │
│     ├─ Score Supertrend direction             │
│     ├─ Compute composite score                │
│     └─ Generate signal if score >= 0.60       │
│                                               │
│  5. POSITION MANAGEMENT                       │
│     ├─ Update trailing stops                  │
│     ├─ Check exit conditions                  │
│     ├─ Pyramiding opportunities               │
│     └─ Portfolio heat monitoring              │
│                                               │
│  6. POSITION SIZING                           │
│     ├─ ATR-based sizing                       │
│     ├─ Drawdown adjustment                    │
│     ├─ Correlation check                      │
│     └─ Portfolio heat limit check             │
│                                               │
│  7. EXECUTION                                 │
│     ├─ Submit orders                          │
│     ├─ Confirm fills                          │
│     └─ Update position tracking               │
│                                               │
│  8. MONITORING & REPORTING                    │
│     ├─ P&L tracking                           │
│     ├─ Drawdown monitoring                    │
│     ├─ Regime dashboard                       │
│     └─ Performance attribution                │
│                                               │
└───────────────────────────────────────────────┘
```

---

## 18. เอกสารอ้างอิง

### บทความวิชาการ

1. **Jegadeesh, N., & Titman, S.** (1993). "Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency." *Journal of Finance*, 48(1), 65-91.
2. **Moskowitz, T.J., Ooi, Y.H., & Pedersen, L.H.** (2012). "Time Series Momentum." *Journal of Financial Economics*, 104(2), 228-250.
3. **Asness, C.S., Moskowitz, T.J., & Pedersen, L.H.** (2013). "Value and Momentum Everywhere." *Journal of Finance*, 68(3), 929-985.
4. **Barroso, P., & Santa-Clara, P.** (2015). "Momentum Has Its Moments." *Journal of Financial Economics*, 116(1), 111-120.
5. **Daniel, K., & Moskowitz, T.** (2016). "Momentum Crashes." *Journal of Financial Economics*, 122(2), 221-247.
6. **Fung, W., & Hsieh, D.A.** (2001). "The Risk in Hedge Fund Strategies: Theory and Evidence from Trend Followers." *Review of Financial Studies*, 14(2), 313-341.
7. **Brock, W., Lakonishok, J., & LeBaron, B.** (1992). "Simple Technical Trading Rules and the Stochastic Properties of Stock Returns." *Journal of Finance*, 47(5), 1731-1764.
8. **Okunev, J., & White, D.** (2003). "Do Momentum-Based Strategies Still Work in Foreign Currency Markets?" *Journal of Financial and Quantitative Analysis*, 38(2), 425-447.
9. **Liu, Y., Tsyvinski, A., & Wu, X.** (2019). "Common Risk Factors in Cryptocurrency." *NBER Working Paper 25882*.

### แหล่งข้อมูลสำหรับผู้ปฏิบัติ

10. **Antonacci, G.** (2014). *Dual Momentum Investing*. McGraw-Hill.
11. **Covel, M.** (2009). *Trend Following: How to Make a Fortune in Bull, Bear, and Black Swan Markets*. FT Press.
12. **Faith, C.** (2007). *Way of the Turtle*. McGraw-Hill. (ระบบ Turtle Trading ต้นฉบับ)
13. **Clenow, A.** (2013). *Following the Trend: Diversified Managed Futures Trading*. Wiley.
14. **Wilder, J.W.** (1978). *New Concepts in Technical Trading Systems*. Trend Research. (ADX, Parabolic SAR.)
15. **Kaufman, P.J.** (2013). *Trading Systems and Methods*. 5th Edition. Wiley.

### เอกสารอ้างอิงทางคณิตศาสตร์

16. **Hurst, H.E.** (1951). "Long-Term Storage Capacity of Reservoirs." *Transactions ASCE*, 116, 770-808.
17. **Hamilton, J.D.** (1989). "A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle." *Econometrica*, 57(2), 357-384. (HMM สำหรับการตรวจจับสภาวะตลาด)

---

*เอกสารนี้เป็นส่วนหนึ่งของฐานความรู้ระบบเทรด AI แบบ Multi-Agent กลยุทธ์โมเมนตัมและเทรดตามเทรนด์เป็นแหล่ง Alpha พื้นฐานที่เสริมแนวทาง Mean Reversion กุญแจสำคัญคือการตรวจจับสภาวะตลาดที่ถูกต้องเพื่อเปิดใช้กลยุทธ์ที่เหมาะสมกับสภาพตลาดปัจจุบัน*
