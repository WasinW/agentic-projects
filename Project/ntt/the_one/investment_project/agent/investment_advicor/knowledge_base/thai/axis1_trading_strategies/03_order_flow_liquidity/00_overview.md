# การวิเคราะห์การไหลของคำสั่ง (Order Flow) และสภาพคล่อง (Liquidity) — ภาพรวม

> **แกนที่ 1 — กลยุทธ์การเทรด | โมดูล 03 — การไหลของคำสั่งและสภาพคล่อง (Order Flow & Liquidity)**
> เวอร์ชัน: 2.0 | อัปเดตล่าสุด: 2026-04-12
> การจัดประเภท: ฐานความรู้หลัก — ระบบเทรด AI แบบหลายเอเจนต์ (Multi-Agent AI Trading System)

---

## สารบัญ

1. [บทนำ](#1-บทนำ)
2. [พื้นฐานจุลภาคของตลาด (Market Microstructure)](#2-พื้นฐานจุลภาคของตลาด)
3. [คำสั่งสร้างการเคลื่อนไหวของราคาอย่างไร](#3-คำสั่งสร้างการเคลื่อนไหวของราคาอย่างไร)
4. [พลวัตของราคาเสนอซื้อ/ขาย (Bid/Ask Dynamics)](#4-พลวัตของราคาเสนอซื้อขาย)
5. [โมเดล Maker กับ Taker](#5-โมเดล-maker-กับ-taker)
6. [เหตุใดการไหลของคำสั่งจึงสำคัญสำหรับการเทรดอัลกอริทึม](#6-เหตุใดการไหลของคำสั่งจึงสำคัญสำหรับการเทรดอัลกอริทึม)
7. [ตรรกะหลัก — กรอบการเข้า/ออก (Entry/Exit Framework)](#7-ตรรกะหลัก--กรอบการเขาออก)
8. [ข้อกำหนดทางเทคนิค](#8-ข้อกำหนดทางเทคนิค)
9. [โมเดลทางคณิตศาสตร์](#9-โมเดลทางคณิตศาสตร์)
10. [พารามิเตอร์ความเสี่ยง](#10-พารามิเตอร์ความเสี่ยง)
11. [ขั้นตอนการดำเนินการ (Execution Flow)](#11-ขั้นตอนการดำเนินการ)
12. [การบูรณาการข้ามโมดูล](#12-การบูรณาการข้ามโมดูล)
13. [เอกสารอ้างอิง](#13-เอกสารอ้างอิง)

---

## 1. บทนำ

การวิเคราะห์การไหลของคำสั่ง (Order Flow Analysis) คือการศึกษาธุรกรรมจริงที่เกิดขึ้นในตลาด ซึ่งก็คือคำสั่งซื้อและขายดิบที่ขับเคลื่อนราคา แตกต่างจากอินดิเคเตอร์ที่มาทีหลังราคา เช่น เส้นค่าเฉลี่ยเคลื่อนที่ (Moving Averages), RSI, MACD การวิเคราะห์การไหลของคำสั่งให้มุมมอง**นำหน้า (Leading)** เกี่ยวกับเจตนาของตลาด โดยการตรวจสอบกลไกของอุปสงค์และอุปทานในระดับที่ละเอียดที่สุด

การวิเคราะห์สภาพคล่อง (Liquidity Analysis) เสริมการวิเคราะห์การไหลของคำสั่งโดยระบุ**ตำแหน่ง**ที่มีกลุ่มคำสั่งรอดำเนินการจำนวนมากอยู่ในตลาด กลุ่มเหล่านี้ทำหน้าที่เหมือนแม่เหล็กดึงดูดราคา เนื่องจากผู้เล่นสถาบันต้องการสภาพคล่องเพียงพอเพื่อเติมเต็มสถานะขนาดใหญ่โดยไม่เกิด Slippage มากเกินไป

### 1.1 เหตุใดโมดูลนี้จึงมีอยู่

การวิเคราะห์ทางเทคนิคแบบดั้งเดิมถือว่าราคาเป็นแหล่งข้อมูลหลัก ซึ่งเป็นแนวคิดที่กลับด้าน ราคาคือ**ผลลัพธ์**ของการไหลของคำสั่ง — เป็นผล ไม่ใช่สาเหตุ การศึกษาการไหลของคำสั่งโดยตรงทำให้ระบบเทรดของเราได้รับ:

- **สัญญาณเชิงคาดการณ์ (Anticipatory Signals)**: ตรวจจับเจตนาของสถาบันก่อนที่ราคาจะขยับ
- **จุดเข้าแม่นยำ (Precision Entries)**: เข้าเทรดที่โซนสภาพคล่องที่เหมาะสม แทนที่จะใช้แนวรับ/แนวต้านแบบสุ่ม
- **ลดสัญญาณหลอก (Reduced False Signals)**: กรองสัญญาณรบกวนด้วยการยืนยันจากข้อมูลธุรกรรมจริง
- **สอดคล้องกับสถาบัน (Institutional Alignment)**: เทรดไปกับ Smart Money แทนที่จะสวนทาง

### 1.2 ขอบเขตของโมดูลนี้

โมดูลนี้ครอบคลุมเอกสารที่เชื่อมโยงกัน 6 ฉบับ:

| เอกสาร | จุดเน้น | แหล่งข้อมูลหลัก |
|----------|-------|-------------------|
| `00_overview.md` | แนวคิดพื้นฐาน | กรอบแนวคิด |
| `01_order_book_analysis.md` | ข้อมูล Level 2, พลวัตของ Order Book | ความลึกตลาด L2, DOM |
| `02_liquidity_concepts.md` | Liquidity Pools, FVG, แนวคิด ICT | Price Action + ปริมาณ |
| `03_hft_stop_hunting.md` | รูปแบบการจัดการโดยสถาบัน | ข้อมูล Tick, ช่วงเวลาในวัน |
| `04_volume_delta_analysis.md` | Volume Delta, CVD, VWAP, Volume Profile | ข้อมูลการซื้อขาย (Time & Sales) |
| `05_execution_flow.md` | ท่อส่งการดำเนินงานแบบครบถ้วน | แหล่งข้อมูลทั้งหมด |

### 1.3 การใช้งานกับตลาดต่างๆ

| ตลาด | คุณภาพข้อมูล Order Flow | ข้อมูล L2 ที่มี | ข้อพิจารณาสำคัญ |
|--------|------------------------|-------------------|-------------------|
| **Forex (Spot)** | ปานกลาง — ตลาด OTC กระจายศูนย์ | จำกัด (เฉพาะ ECN/โบรกเกอร์) | ใช้ข้อมูลรวม; ไม่มี Order Book ส่วนกลางที่แท้จริง |
| **Forex (Futures)** | ดีเยี่ยม — CME รวมศูนย์ | DOM เต็มรูปแบบ | CME FX Futures เป็นตัวแทนของ Spot |
| **Crypto (CEX)** | ดี — เฉพาะแต่ละตลาด | Order Book เต็มรูปแบบผ่าน API | กระจายข้ามตลาด; มีข้อกังวลเรื่อง Wash Trading |
| **Crypto (DEX)** | ปานกลาง — ข้อมูลบนเชน | AMM Liquidity Pools | โครงสร้างจุลภาคแตกต่าง (Constant Product AMM) |

---

## 2. พื้นฐานจุลภาคของตลาด (Market Microstructure)

จุลภาคตลาด (Market Microstructure) เป็นสาขาวิชาการที่ศึกษากระบวนการและผลลัพธ์ของการแลกเปลี่ยนสินทรัพย์ภายใต้กฎเกณฑ์เฉพาะ โดยตรวจสอบว่าความต้องการแฝงจากนักลงทุนถูกแปลงเป็นราคาและปริมาณอย่างไร

### 2.1 กระบวนการค้นพบราคา (Price Discovery)

การค้นพบราคาเป็นกระบวนการต่อเนื่องที่ปฏิสัมพันธ์ระหว่างผู้ซื้อและผู้ขายกำหนดราคาตลาดของสินทรัพย์ กระบวนการนี้เกิดขึ้นผ่าน **เครื่องจับคู่คำสั่ง (Matching Engine)** ซึ่งเป็นส่วนประกอบหลักของตลาดทุกแห่ง

```
                    ┌─────────────────────┐
                    │   MATCHING ENGINE    │
                    │                     │
  Buy Orders ──────►  Price-Time Priority ◄────── Sell Orders
  (Bids)           │                     │        (Asks/Offers)
                    │  ┌───────────────┐  │
                    │  │ Trade Output  │  │
                    │  │ Price: P      │  │
                    │  │ Volume: V     │  │
                    │  │ Time: T       │  │
                    │  │ Aggressor: B/S│  │
                    │  └───────────────┘  │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   PRICE UPDATE       │
                    │   Last: P           │
                    │   Bid: P_bid        │
                    │   Ask: P_ask        │
                    └─────────────────────┘
```

### 2.2 ประเภทคำสั่งและผลกระทบต่อตลาด

#### 2.2.1 คำสั่งตลาด (Market Orders)
- **คำจำกัดความ**: คำสั่งซื้อหรือขายทันทีที่ราคาดีที่สุดที่มีอยู่
- **ผลกระทบ**: ดึงสภาพคล่องออกจาก Order Book; สร้างผลกระทบต่อราคาทันที
- **สัญญาณ**: แสดงถึงความเร่งด่วน — เทรดเดอร์ยินดีข้ามส่วนต่างราคา (Spread)
- **ความรุนแรง**: คำสั่งซื้อตลาดตี Ask; คำสั่งขายตลาดตี Bid

#### 2.2.2 คำสั่งจำกัดราคา (Limit Orders)
- **คำจำกัดความ**: คำสั่งซื้อหรือขายที่ราคาที่กำหนดหรือดีกว่า
- **ผลกระทบ**: เพิ่มสภาพคล่องใน Order Book; สร้างความลึกที่ระดับราคาเฉพาะ
- **สัญญาณ**: แสดงถึงความอดทน — เทรดเดอร์ยินดีรอราคาที่ต้องการ
- **บทบาท**: ทำหน้าที่เป็นกันชนต่อการเคลื่อนไหวของราคา (สภาพคล่องแบบ Passive)

#### 2.2.3 คำสั่งหยุด (Stop Orders)
- **คำจำกัดความ**: คำสั่งที่กลายเป็นคำสั่งตลาดเมื่อราคาถึงจุดที่กำหนด
- **ผลกระทบ**: สร้างเหตุการณ์สภาพคล่องแบบลูกโซ่เมื่อถูกกระตุ้น
- **สัญญาณ**: แสดงถึงการจัดการความเสี่ยง — แต่ยังเป็นแหล่งสภาพคล่องสำหรับสถาบัน
- **จุดอ่อน**: กลุ่มคำสั่งหยุดสามารถมองเห็นได้โดยผู้เล่นระดับสูง และกลายเป็นเป้าหมาย

#### 2.2.4 คำสั่งภูเขาน้ำแข็ง (Iceberg Orders / Hidden Orders)
- **คำจำกัดความ**: คำสั่งขนาดใหญ่ที่ถูกแบ่งเป็นส่วนเล็กๆ ที่มองเห็นได้
- **ผลกระทบ**: อำพรางขนาดคำสั่งจริง; แสดงเพียงเศษส่วนของปริมาณทั้งหมด
- **การตรวจจับ**: มีการเติมซ้ำอย่างต่อเนื่องที่ระดับราคาเดียวกันหลังจากถูกเติมบางส่วน
- **สัญญาณ**: การสะสมหรือกระจายของสถาบันโดยไม่เปิดเผยเจตนา

#### 2.2.5 Fill-or-Kill (FOK) และ Immediate-or-Cancel (IOC)
- **FOK**: ดำเนินการคำสั่งทั้งหมดทันทีหรือยกเลิกทั้งหมด
- **IOC**: ดำเนินการส่วนที่ทำได้ทันที ยกเลิกส่วนที่เหลือ
- **สัญญาณ**: ใช้โดยอัลกอริทึมที่ต้องการเงื่อนไขการเติมเฉพาะ

### 2.3 Order Book แบบ Continuous Limit (CLOB)

CLOB เป็นโมเดลมาตรฐานสำหรับตลาดรวมศูนย์ (หุ้น, ฟิวเจอร์ส, คริปโตแบบรวมศูนย์) การเข้าใจโครงสร้างของมันเป็นพื้นฐานของการวิเคราะห์ Order Flow

```
Price Level    │ Bid Size │ Ask Size │
───────────────┼──────────┼──────────┤
  1.1055       │          │   250    │  ◄── Best Ask (Inside Ask)
  1.1054       │          │   180    │
  1.1053       │          │   420    │
  1.1052       │          │   95     │
───────────────┼──────────┼──────────┤  ◄── Spread = 1.1052 - 1.1050 = 0.0002
  1.1050       │   310    │          │  ◄── Best Bid (Inside Bid)
  1.1049       │   175    │          │
  1.1048       │   560    │          │
  1.1047       │   220    │          │
───────────────┼──────────┼──────────┤
               │  DEPTH   │  DEPTH   │
```

**ตัวชี้วัดสำคัญจาก CLOB:**

| ตัวชี้วัด | สูตร | การตีความ |
|--------|---------|---------------|
| ราคากลาง (Mid Price) | $(P_{ask} + P_{bid}) / 2$ | ค่าประมาณมูลค่ายุติธรรม |
| ส่วนต่างราคา (Spread) | $P_{ask} - P_{bid}$ | ต้นทุนของความทันที |
| ส่วนต่างราคาสัมพัทธ์ (Relative Spread) | $(P_{ask} - P_{bid}) / P_{mid}$ | ตัววัดสภาพคล่องแบบปรับมาตรฐาน |
| ความลึกที่ราคาดีที่สุด (Depth at Best) | $Q_{bid}^{(1)} + Q_{ask}^{(1)}$ | สภาพคล่องทันที |
| ความลึกรวม (Total Depth) | $\sum Q_{bid} + \sum Q_{ask}$ | สภาพคล่องตลาดโดยรวม |

### 2.4 โครงสร้างตลาด Forex แบบกระจายศูนย์

แตกต่างจากตลาดรวมศูนย์ ตลาด Forex สปอตดำเนินการเป็นเครือข่ายนอกตลาด (OTC):

```
           ┌────────────────────────────────────────────┐
           │         INTERBANK MARKET (Tier 1)          │
           │  Deutsche Bank, JPMorgan, Citi, UBS, etc.  │
           │  Average deal size: $5M-$100M+             │
           └─────────────┬──────────────────────────────┘
                         │
           ┌─────────────▼──────────────────────────────┐
           │         ECN / AGGREGATORS (Tier 2)          │
           │  EBS, Reuters Matching, Currenex, Hotspot   │
           │  Aggregate multiple LP quotes               │
           └─────────────┬──────────────────────────────┘
                         │
           ┌─────────────▼──────────────────────────────┐
           │     PRIME BROKERS / PRIME OF PRIME (Tier 3) │
           │  Access to aggregated liquidity             │
           └─────────────┬──────────────────────────────┘
                         │
           ┌─────────────▼──────────────────────────────┐
           │         RETAIL BROKERS (Tier 4)             │
           │  Market Makers or STP/ECN models            │
           │  Often internalize retail flow              │
           └────────────────────────────────────────────┘
```

**นัยสำคัญสำหรับการวิเคราะห์ Order Flow ใน Forex:**
- ไม่มี Order Book "จริง" เพียงแห่งเดียว — แต่ละแพลตฟอร์มมีของตัวเอง
- CME FX Futures เป็นตัวแทนที่ดีที่สุดสำหรับ Order Flow แบบรวมศูนย์
- ข้อมูลโบรกเกอร์รายย่อยมีจำกัดและอาจเบี่ยงเบน (โมเดลดีลเลอร์)
- การไหลของสถาบันถูกอนุมานจากแผนภูมิ Footprint และ Volume Delta

### 2.5 โครงสร้างตลาดคริปโต

ตลาดสกุลเงินดิจิทัลผสมผสานองค์ประกอบทั้งแบบรวมศูนย์และกระจายศูนย์:

```
       ┌──────────────────┐    ┌──────────────────┐
       │   CEX (Binance,  │    │  DEX (Uniswap,   │
       │   Coinbase, OKX) │    │  dYdX, GMX)      │
       │                  │    │                  │
       │  CLOB Model      │    │  AMM Model       │
       │  Maker/Taker fees│    │  LP Pool Model   │
       │  Full L2 data    │    │  On-chain data   │
       └────────┬─────────┘    └────────┬─────────┘
                │                       │
                ▼                       ▼
       ┌────────────────────────────────────────┐
       │        ARBITRAGEURS & MARKET MAKERS     │
       │   Bridge pricing across venues          │
       │   Keep prices aligned cross-exchange    │
       └────────────────────────────────────────┘
```

**ความแตกต่างสำคัญจากตลาดดั้งเดิม:**
- ซื้อขาย 24/7 — ไม่มีเปิด/ปิดเซสชัน (แต่ยังมีรูปแบบสภาพคล่องแบบวัฏจักร)
- สภาพคล่องกระจายข้ามตลาดหลายสิบแห่ง
- Wash Trading ทำให้ปริมาณบวมขึ้น 50-90% ในบางตลาด (Bitwise, 2019)
- ข้อมูลบนเชนให้ความโปร่งใสพิเศษ (กระเป๋า Whale, การไหลของ DEX)
- Funding Rates ใน Perpetual Swaps ให้สัญญาณ Order Flow เพิ่มเติม

---

## 3. คำสั่งสร้างการเคลื่อนไหวของราคาอย่างไร

### 3.1 กลไกพื้นฐาน

ราคาขยับเมื่อ**คำสั่งเชิงรุก (Aggressive Orders)** กินสภาพคล่องที่มีอยู่ที่ระดับราคาหนึ่ง นี่คือแนวคิดสำคัญที่สุดในการวิเคราะห์ Order Flow

```
STATE 1: Equilibrium
Ask: 100 @ 1.1052
Bid: 150 @ 1.1050
→ Mid = 1.10510, Spread = 0.0002

STATE 2: Aggressive Buy (Market Buy 100 lots)
The 100 lot market buy LIFTS the entire ask at 1.1052
Ask: (now) 250 @ 1.1053  [new best ask]
Bid: 150 @ 1.1050         [unchanged]
→ Mid = 1.10515, Price moved UP by 0.0001

STATE 3: Chain Reaction
If more aggressive buying follows:
  - Consecutive ask levels get consumed
  - Bid-side limit orders get placed higher (chase)
  - Stop losses above old highs get triggered (more buying)
  - RESULT: Impulsive price move upward
```

### 3.2 การไหลแบบเชิงรุก (Aggressive) กับ แบบตั้งรับ (Passive)

| ลักษณะ | เชิงรุก (Market Orders) | ตั้งรับ (Limit Orders) |
|---------------|---------------------------|----------------------|
| **การกระทำ** | ข้ามส่วนต่างราคาเพื่อดำเนินการ | รอที่ระดับราคา |
| **ดึง/เพิ่มสภาพคล่อง** | ดึงออก | เพิ่ม |
| **ความเร่งด่วน** | สูง — ต้องการเติมทันที | ต่ำ — ยินดีรอ |
| **ข้อมูล** | มักเป็นผู้มีข้อมูล (เจตนาทิศทาง) | มักไม่มีข้อมูล (การทำตลาด) |
| **โครงสร้างค่าธรรมเนียม** | จ่ายค่าธรรมเนียม Taker | ได้รับส่วนลด Maker |
| **ผลกระทบต่อราคา** | โดยตรง — ทำให้ราคาขยับ | ทางอ้อม — ดูดซับการเคลื่อนไหว |

### 3.3 สามวิธีที่ราคาสามารถขยับได้

**ประเภทที่ 1: การกินสภาพคล่อง (Liquidity Consumption) — คำสั่งเชิงรุก**
- คำสั่งตลาดขนาดใหญ่กินผ่านหลายระดับราคา
- สร้างการเคลื่อนไหวราคาแบบรวดเร็วและรุนแรง
- มักเห็นที่ระดับสำคัญ (Breakouts, Stop Runs)
- ลักษณะเฉพาะ: Delta ขนาดใหญ่, ปริมาณสูง, Order Book บางหลังการเคลื่อนไหว

**ประเภทที่ 2: การถอนสภาพคล่อง (Liquidity Withdrawal) — การยกเลิกคำสั่ง Passive**
- Market Makers ถอนคำสั่ง Limit ออกจากด้านหนึ่ง
- สร้าง "สุญญากาศ" — ราคาตกลงสู่ช่องว่าง
- มักเกิดก่อนเหตุการณ์ข่าวหรือช่วงที่ไม่แน่นอนสูง
- ลักษณะเฉพาะ: Order Book บางลง, Spread กว้างขึ้น, การเคลื่อนไหวปริมาณต่ำ

**ประเภทที่ 3: การเลื่อนสภาพคล่อง (Liquidity Shift) — การย้ายคำสั่ง Passive**
- คำสั่ง Limit เลื่อนจากระดับราคาหนึ่งไปอีกระดับหนึ่ง
- การปรับราคาค่ามูลค่ายุติธรรมอย่างค่อยเป็นค่อยไป
- พบบ่อยในตลาดที่มีแนวโน้ม
- ลักษณะเฉพาะ: ความชันของ Order Book เปลี่ยน, ราคากลางเลื่อนอย่างสม่ำเสมอ

### 3.4 ความไม่สมดุลของ Order Flow และผลกระทบต่อราคา

ความสัมพันธ์ระหว่างความไม่สมดุลของ Order Flow และการเปลี่ยนแปลงราคาเป็นไปตามฟังก์ชันเว้า (รากที่สอง) ตามที่การวิจัยเชิงประจักษ์ยืนยัน:

$$\Delta P \approx \sigma \cdot \sqrt{\frac{Q}{V_{daily}}} \cdot \text{sign}(Q)$$

โดยที่:
- $\Delta P$ = ผลกระทบต่อราคาที่คาดหวัง
- $\sigma$ = ความผันผวนรายวัน
- $Q$ = ขนาดคำสั่ง
- $V_{daily}$ = ปริมาณเฉลี่ยรายวัน

กฎรากที่สอง (Bouchaud et al., 2009) หมายความว่า:
- การเพิ่มขนาดคำสั่งเป็นสองเท่าไม่ได้เพิ่มผลกระทบต่อราคาเป็นสองเท่า
- ผลกระทบเพิ่มขึ้นตามรากที่สองของขนาด
- คำสั่งขนาดใหญ่ต้องถูกแบ่งออก (อัลกอริทึม TWAP, VWAP) เพื่อลดผลกระทบ

### 3.5 โมเดลการไหลของข้อมูล (Kyle, 1985)

โมเดลสำคัญของ Kyle อธิบายว่าเทรดเดอร์ที่มีข้อมูลมีปฏิสัมพันธ์กับ Noise Traders และ Market Maker อย่างไร:

$$p_t = \mu + \lambda \cdot (x_t + u_t) + \epsilon_t$$

โดยที่:
- $p_t$ = ราคาตลาดที่เวลา $t$
- $\mu$ = มูลค่าพื้นฐาน
- $\lambda$ = แลมบ์ดาของ Kyle (สัมประสิทธิ์ผลกระทบต่อราคา)
- $x_t$ = Order Flow ของเทรดเดอร์ที่มีข้อมูล
- $u_t$ = Order Flow ของ Noise Trader
- $\epsilon_t$ = ค่าความผิดพลาด

**แลมบ์ดาของ Kyle ($\lambda$)** เป็นตัววัดคุณภาพตลาดที่สำคัญ:
- $\lambda$ สูง = ผลกระทบต่อราคาสูงต่อหน่วยของ Order Flow (ตลาดไม่มีสภาพคล่อง)
- $\lambda$ ต่ำ = ผลกระทบต่อราคาต่ำต่อหน่วยของ Order Flow (ตลาดมีสภาพคล่อง)

สำหรับระบบเทรดของเรา การประมาณ $\lambda$ แบบเรียลไทม์ให้ตัววัดแบบพลวัตของสภาพคล่องตลาดและความไม่สมมาตรของข้อมูล

---

## 4. พลวัตของราคาเสนอซื้อ/ขาย (Bid/Ask Dynamics)

### 4.1 ส่วนต่างราคา (Spread) เป็นตัววัดคุณภาพตลาด

ส่วนต่างราคาเสนอซื้อ-ขาย (Bid-Ask Spread) มีอยู่เพราะองค์ประกอบสามส่วน (Stoll, 1989):

$$S = S_{inventory} + S_{adverse} + S_{processing}$$

| องค์ประกอบ | คำอธิบาย | สัดส่วนทั่วไป |
|-----------|-------------|-------------------|
| $S_{inventory}$ | ค่าชดเชยความเสี่ยงในการถือสถานะ | 20-40% |
| $S_{adverse}$ | การป้องกันจากเทรดเดอร์ที่มีข้อมูล | 40-60% |
| $S_{processing}$ | ต้นทุนการประมวลผลคำสั่ง | 10-20% |

### 4.2 พลวัตของ Spread ใน Forex

Spread ของ Forex เป็นแบบพลวัตและแตกต่างตาม:

**ระดับสภาพคล่องตามคู่สกุลเงิน:**

| ระดับ | คู่เงิน | Spread ทั่วไป (pips) | ปริมาณรายวัน |
|------|-------|----------------------|-------------|
| ระดับ 1 (Major) | EUR/USD, USD/JPY | 0.1-0.5 | $500B+ |
| ระดับ 2 (Major) | GBP/USD, AUD/USD | 0.3-1.0 | $100-500B |
| ระดับ 3 (Cross) | EUR/GBP, EUR/JPY | 0.5-2.0 | $50-100B |
| ระดับ 4 (Exotic) | USD/TRY, USD/ZAR | 3.0-20.0 | <$50B |

**รูปแบบพฤติกรรมของ Spread:**
```
Spread
  │
  │  ╭─╮                                    ╭─╮
  │ ╭╯ ╰╮                                  ╭╯ ╰╮
  │╭╯   ╰╮          ╭─╮                   ╭╯   ╰╮
  ││     │╭─╮      ╭╯ ╰╮      ╭─╮        │     │
  ││     ╰╯ ╰──────╯   ╰──────╯ ╰────────╯     │
  │╰╮                                          ╭╯
  │ ╰──────────────────────────────────────────╯
  └──┬───────┬──────┬───────┬──────┬───────┬────► Time
   Asian   London  LDN/NY  New York  Asian  London
   Open    Open    Overlap  Close    Open   Open

ข้อสังเกตสำคัญ:
- Spread แคบที่สุดช่วง London/NY ทับซ้อนกัน
- Spread กว้างที่สุดช่วง Asian Session Rollover
- Spread พุ่งสูงในช่วงข่าวสำคัญ
```

### 4.3 พลวัตของ Spread ในคริปโต

Spread ของคริปโตขึ้นอยู่กับ:

| ปัจจัย | ผลกระทบต่อ Spread |
|--------|-----------------|
| ตลาด (Binance vs CEX เล็ก) | ต่างกัน 10-100 เท่า |
| คู่เหรียญ (BTC/USDT vs altcoin/BTC) | ต่างกัน 5-50 เท่า |
| ช่วงเวลา (ชั่วโมง US vs เอเชีย) | ต่างกัน 2-5 เท่า |
| สภาวะความผันผวน | ต่างกัน 3-20 เท่า |
| มูลค่าตลาดของสินทรัพย์ | สัมพันธ์ผกผัน |

### 4.4 สัญญาณความไม่สมดุลของ Bid/Ask

ความไม่สมดุลของ Bid/Ask ที่ด้านบนสุดของ Book เป็นสัญญาณทิศทางระยะสั้นที่ทรงพลัง:

$$\text{Imbalance}_{BA} = \frac{Q_{bid}^{(1)} - Q_{ask}^{(1)}}{Q_{bid}^{(1)} + Q_{ask}^{(1)}}$$

โดยที่:
- $Q_{bid}^{(1)}$ = ปริมาณที่ Best Bid
- $Q_{ask}^{(1)}$ = ปริมาณที่ Best Ask
- ช่วง: [-1, +1]
- บวก = ปริมาณ Bid มากกว่า (แรงกดซื้อ)
- ลบ = ปริมาณ Ask มากกว่า (แรงกดขาย)

**ความไม่สมดุลแบบถ่วงน้ำหนักหลายระดับ (Multi-Level Weighted Imbalance):**

$$\text{WImb} = \frac{\sum_{i=1}^{n} w_i \cdot Q_{bid}^{(i)} - \sum_{i=1}^{n} w_i \cdot Q_{ask}^{(i)}}{\sum_{i=1}^{n} w_i \cdot Q_{bid}^{(i)} + \sum_{i=1}^{n} w_i \cdot Q_{ask}^{(i)}}$$

โดยที่ $w_i = e^{-\alpha \cdot i}$ (การถ่วงน้ำหนักแบบลดลงเชิงเลขชี้กำลัง — ระดับที่ใกล้กว่ามีน้ำหนักมากกว่า)

**สัญญาณการเทรด:**
```
if WImb > +0.6:
    STRONG BUY pressure detected
    → Expect upward price movement
    → Look for long entry confirmation

if WImb < -0.6:
    STRONG SELL pressure detected
    → Expect downward price movement
    → Look for short entry confirmation

if -0.2 < WImb < +0.2:
    BALANCED book
    → No directional edge from order book
    → Wait for imbalance to develop
```

### 4.5 โมเดลการเปลี่ยนผ่าน Bid/Ask (Bid/Ask Transition Model)

สัญญาณจุลภาคที่ทรงพลังคือ **ความน่าจะเป็นในการเปลี่ยนผ่าน (Transition Probability)** — โอกาสที่ Best Bid หรือ Ask จะขยับขึ้นหรือลงเมื่ออยู่ในสถานะปัจจุบัน:

$$P(\text{ask\_down} | \text{large\_bid\_imbalance}) > P(\text{ask\_down} | \text{balanced})$$

หมายความว่า: เมื่อมีปริมาณมากกว่าอย่างมีนัยสำคัญในฝั่ง Bid ความน่าจะเป็นที่ราคา Ask จะลดลงนั้นจริงๆ แล้วต่ำกว่า (เพราะ Bid ให้แนวรับและผู้ซื้อเชิงรุกยก Ask ขึ้น)

---

## 5. โมเดล Maker กับ Taker

### 5.1 คำจำกัดความ

| บทบาท | การกระทำ | ค่าธรรมเนียม | ประเภทคำสั่ง |
|------|--------|-----|-----------|
| **Maker** | วางคำสั่ง Limit ที่เพิ่มสภาพคล่องใน Book | ส่วนลด (ค่าธรรมเนียมติดลบ) หรือค่าธรรมเนียมต่ำกว่า | คำสั่ง Limit ที่ไม่ได้จับคู่ทันที |
| **Taker** | วางคำสั่งที่ดึงสภาพคล่องออกจาก Book | ค่าธรรมเนียมสูงกว่า (Taker Fee) | คำสั่งตลาด หรือคำสั่ง Limit ที่จับคู่ทันที |

### 5.2 โครงสร้างค่าธรรมเนียม

**โครงสร้างค่าธรรมเนียม Forex (ECN) ทั่วไป:**
- ค่าคอมมิชชัน: $3-7 ต่อ Round-Turn Lot (100K หน่วย)
- Spread: Raw Spread จาก LP (0.0-0.3 pips สำหรับคู่หลัก)
- ไม่มีการแยก Maker/Taker อย่างชัดเจนในการตั้งค่ารายย่อยส่วนใหญ่

**โครงสร้างค่าธรรมเนียมคริปโตทั่วไป (Binance เป็นตัวอย่าง):**

| ระดับ VIP | Maker Fee | Taker Fee | ปริมาณ 30 วัน |
|-----------|-----------|-----------|------------|
| Regular | 0.10% | 0.10% | <$1M |
| VIP 1 | 0.09% | 0.10% | $1M-$5M |
| VIP 3 | 0.06% | 0.08% | $25M-$100M |
| VIP 6 | 0.02% | 0.05% | $250M-$1B |
| VIP 9 | 0.00% | 0.02% | >$4B |
| Market Maker | -0.01% | 0.03% | ตามคำขอ |

### 5.3 เหตุใดการแยก Maker/Taker จึงสำคัญสำหรับ Order Flow

โมเดล Maker/Taker สร้างรูปแบบพฤติกรรมเฉพาะ:

**พฤติกรรม Maker (Passive Flow):**
- ให้สภาพคล่องที่ระดับราคาเฉพาะ
- มีแรงจูงใจทางเศรษฐกิจให้เทรดสวนเทรนด์ (Mean Reversion)
- ยกเลิกและวางคำสั่งใหม่อย่างรวดเร็ว (อาจเป็น Quote Stuffing)
- คิดเป็น ~60-80% ของ Order Book ที่มองเห็นได้ในตลาดที่มีสภาพคล่อง
- ส่วนใหญ่ของปริมาณนี้มาจาก HFT Market Makers

**พฤติกรรม Taker (Aggressive Flow):**
- แสดงถึงเจตนาทิศทาง
- ยินดีจ่ายค่าธรรมเนียมสูงกว่าเพื่อดำเนินการทันที
- ส่งสัญญาณความเร่งด่วนและความเชื่อมั่น
- เมื่อเป็นสถาบัน มักนำหน้าการเคลื่อนไหวที่ยั่งยืน
- เป็นข้อมูลนำเข้าสำคัญสำหรับการคำนวณ Volume Delta

### 5.4 Taker Flow เป็นสัญญาณหลัก

สำหรับระบบเทรดของเรา **Taker Flow เป็นสัญญาณ Order Flow หลัก** เพราะ:

1. **เปิดเผยเจตนา**: คนที่ยินดีข้ามส่วนต่างราคาและจ่ายค่าธรรมเนียมสูงกว่ามีความเชื่อมั่นในทิศทาง
2. **ทำให้ราคาขยับ**: เฉพาะคำสั่งเชิงรุกเท่านั้นที่ขยับราคาโดยตรง
3. **ยากที่จะปลอมแปลง**: ในขณะที่คำสั่ง Limit สามารถวางและยกเลิกได้ (Spoofing) แต่การซื้อขายที่ดำเนินการแล้วเป็นของจริง
4. **รวมข้อมูล**: การซื้อ/ขายเชิงรุกสะสมเผยทิศทางสุทธิของการไหลที่มีข้อมูล

$$\text{Net Taker Flow}_t = \sum_{i \in \text{buys}} V_i - \sum_{j \in \text{sells}} V_j$$

โดยที่ Buys คือการซื้อขายที่ตี Ask (ผู้ซื้อเป็นฝ่ายริเริ่ม) และ Sells คือการซื้อขายที่ตี Bid (ผู้ขายเป็นฝ่ายริเริ่ม)

### 5.5 การจำแนกประเภทการซื้อขาย: อัลกอริทึม Lee-Ready

เนื่องจากข้อมูลการซื้อขายดิบมักไม่ระบุว่าเป็นการซื้อหรือขาย เราจึงใช้ **อัลกอริทึม Lee-Ready** (Lee & Ready, 1991):

```
ALGORITHM: Lee-Ready Trade Classification
INPUT: Trade price P_t, Bid B_t, Ask A_t, Midpoint M_t

Step 1: Quote Test
  IF P_t > M_t:
    Classify as BUY (buyer-initiated)
  ELIF P_t < M_t:
    Classify as SELL (seller-initiated)
  ELIF P_t == M_t:
    Go to Step 2

Step 2: Tick Test (fallback)
  IF P_t > P_{t-1}:
    Classify as BUY (uptick)
  ELIF P_t < P_{t-1}:
    Classify as SELL (downtick)
  ELIF P_t == P_{t-1}:
    Use classification of previous trade

NOTE: Lee-Ready has ~85% accuracy on average.
For higher accuracy, use the BVC (Bulk Volume Classification)
method of Easley, Lopez de Prado, and O'Hara (2012).
```

### 5.6 การจำแนกปริมาณรวม (Bulk Volume Classification — BVC)

วิธีการที่ปรับปรุงสำหรับจำแนกปริมาณว่าเป็นฝ่ายซื้อหรือขายริเริ่ม:

$$V_t^{buy} = V_t \cdot \Phi\left(\frac{\Delta P_t}{\sigma_{\Delta P}}\right)$$

$$V_t^{sell} = V_t - V_t^{buy}$$

โดยที่:
- $V_t$ = ปริมาณทั้งหมดในแท่ง $t$
- $\Delta P_t$ = การเปลี่ยนแปลงราคาในแท่ง $t$
- $\sigma_{\Delta P}$ = ส่วนเบี่ยงเบนมาตรฐานของการเปลี่ยนแปลงราคา
- $\Phi$ = CDF ของการแจกแจงปกติมาตรฐาน

วิธีนี้ไม่ต้องการข้อมูลระดับ Tick และใช้งานได้กับแท่งเทียน OHLCV

---

## 6. เหตุใดการไหลของคำสั่งจึงสำคัญสำหรับการเทรดอัลกอริทึม

### 6.1 ความได้เปรียบด้านข้อมูล

Order Flow ให้สิ่งที่ไม่มีอินดิเคเตอร์อื่นใดให้ได้: **มุมมองของอุปสงค์และอุปทานจริงแบบเรียลไทม์**

```
Traditional Analysis (Lagging):
  Price Action → Indicator Calculation → Signal → Decision → Execution
  [Already happened]  [Delayed]         [Late]  [Later]   [Too late?]

Order Flow Analysis (Leading/Coincident):
  Order Book State → Flow Imbalance → Signal → Decision → Execution
  [Real-time]        [Real-time]     [Early]  [Timely]   [Optimal]
```

### 6.2 ประเภทความได้เปรียบจาก Order Flow

| ประเภทความได้เปรียบ | กลไก | กรอบเวลา | Alpha ที่คาดหวัง |
|-----------|-----------|-----------|---------------|
| **จุลภาค (Microstructure)** | ความไม่สมดุลของ Order Book, พลวัตของ Spread | วินาที-นาที | น้อยแต่สม่ำเสมอ |
| **การดูดซับ (Absorption)** | คำสั่ง Passive ขนาดใหญ่ดูดซับแรงรุก | นาที-ชั่วโมง | ปานกลาง |
| **การไหลของสถาบัน (Institutional Flow)** | ระบุการสะสม/กระจายของ Smart Money | ชั่วโมง-วัน | สูง |
| **การกวาดสภาพคล่อง (Liquidity Sweep)** | รูปแบบ Stop Hunting, Liquidity Grabs | นาที-ชั่วโมง | สูง |
| **ความแตกต่าง (Divergence)** | CVD กับราคา Divergence | ชั่วโมง-วัน | ปานกลาง-สูง |

### 6.3 การบูรณาการกับ Price Action

Order Flow ไม่ควรใช้แบบเดี่ยว ระบบของเราบูรณาการกับ:

1. **โครงสร้างตลาด (Market Structure)** (โมดูล 02 — Wyckoff): ยืนยันระยะสะสม/กระจายด้วย Order Flow
2. **แนวคิด Smart Money (SMC)** (โมดูล 04): ตรวจสอบ OB และ FVG ด้วย Volume Delta
3. **โซนอุปสงค์/อุปทาน (Supply/Demand Zones)** (โมดูล 05): ยืนยันความแข็งแกร่งของโซนด้วยความลึกของ Order Book
4. **การวิเคราะห์หลายกรอบเวลา (Multi-Timeframe Analysis)** (โมดูล 11): จัดวางสัญญาณ Order Flow ข้ามกรอบเวลา

### 6.4 ข้อกำหนดข้อมูล

| ประเภทข้อมูล | แหล่งที่มา | กรณีใช้งาน | รูปแบบทั่วไป |
|-----------|--------|----------|---------------|
| **Level 1** (BBO) | ฟีดตลาด, โบรกเกอร์ | วิเคราะห์ Spread, การไหลเบื้องต้น | ราคา, ขนาด, เวลา |
| **Level 2** (Depth) | ฟีดตลาด, DOM | วิเคราะห์ Order Book, ความไม่สมดุล | ระดับราคา + ขนาด |
| **Level 3** (Full Book) | เข้าถึงตลาดโดยตรง | มุมมอง Order-by-Order แบบสมบูรณ์ | ID คำสั่งแต่ละรายการ |
| **Time & Sales** | ฟีดการซื้อขาย | Volume Delta, การจำแนกการซื้อขาย | ราคา, ขนาด, ฝั่ง, เวลา |
| **Tick Data** | ผู้ให้บริการข้อมูล | Backtesting, จุลภาค | ทุกการเปลี่ยนแปลงราคา |

**แหล่งข้อมูลที่แนะนำ:**

| ตลาด | ผู้ให้บริการ | คุณภาพข้อมูล | ราคา |
|--------|----------|-------------|------|
| Forex Futures | CME DataMine, CQG | ดีเยี่ยม | $$$ |
| Forex Spot | TrueFX, Dukascopy | ดี | ฟรี-$$ |
| Crypto CEX | Exchange APIs (Binance, Coinbase) | ดี | ฟรี |
| Crypto Aggregated | Kaiko, CoinAPI, Tardis.dev | ดีเยี่ยม | $$-$$$ |

---

## 7. ตรรกะหลัก — กรอบการเข้า/ออก (Entry/Exit Framework)

### 7.1 โมเดลการยืนยันด้วย Order Flow

ทุกสัญญาณเทรดในระบบของเราผ่านชั้นการยืนยันด้วย Order Flow:

```
┌──────────────────────────────────────────────────────┐
│                SIGNAL GENERATION LAYER                 │
│  (Price Action, SMC, Elliott Wave, Wyckoff, etc.)     │
└──────────────────┬───────────────────────────────────┘
                   │ Raw Signal (Long/Short/Neutral)
                   ▼
┌──────────────────────────────────────────────────────┐
│           ORDER FLOW CONFIRMATION LAYER               │
│                                                      │
│  CHECK 1: Order Book Imbalance Direction             │
│    → Does the book support the signal direction?     │
│                                                      │
│  CHECK 2: Volume Delta Confirmation                  │
│    → Is aggressive flow aligned with the signal?     │
│                                                      │
│  CHECK 3: Liquidity Map                              │
│    → Is there sufficient liquidity for the target?   │
│    → Are there liquidity pools that may act as       │
│      magnets or obstacles?                           │
│                                                      │
│  CHECK 4: Institutional Flow Detection               │
│    → Are large participants aligned with signal?     │
│                                                      │
│  RESULT: CONFIRMED / REJECTED / WAIT                 │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│              EXECUTION & RISK LAYER                   │
│  Entry price, SL, TP, Position size, Order type      │
└──────────────────────────────────────────────────────┘
```

### 7.2 เงื่อนไขการเข้า (ตัวอย่าง Long)

สัญญาณ LONG ได้รับการยืนยันเมื่อ:

```python
def confirm_long_signal(signal, order_flow_data):
    checks = {
        'book_imbalance': order_flow_data.weighted_imbalance > 0.3,
        'delta_positive': order_flow_data.cumulative_delta_slope > 0,
        'absorption_bid': order_flow_data.bid_absorption_detected,
        'no_sell_wall': order_flow_data.ask_wall_ratio < 3.0,
        'liquidity_above': order_flow_data.buy_side_liquidity_distance > min_target,
        'session_ok': is_active_session(current_time),
    }
    
    # Require at least 4 of 6 checks
    score = sum(checks.values())
    
    if score >= 5:
        return 'STRONG_CONFIRM'
    elif score >= 4:
        return 'CONFIRM'
    elif score >= 3:
        return 'WEAK_CONFIRM'
    else:
        return 'REJECT'
```

### 7.3 เงื่อนไขการออก

Order Flow ให้สัญญาณการออกแบบพลวัต:

| สัญญาณออก | เงื่อนไข | การดำเนินการ |
|-------------|-----------|--------|
| Delta Divergence | ราคาทำ High ใหม่แต่ CVD ลดลง | รัด Stop / ออกบางส่วน |
| Absorption Flip | การดูดซับขนาดใหญ่ปรากฏสวนสถานะ | เตรียมพร้อมสำหรับการกลับตัว |
| Liquidity Target Hit | ราคาถึง Liquidity Pool ที่ระบุไว้ | ทำกำไร |
| Spread Blow-out | Spread กว้าง >3 เท่าของค่าปกติ | ออกฉุกเฉิน (วิกฤตสภาพคล่อง) |
| Volume Climax | ปริมาณพุ่งสูงสุดขีดพร้อมแท่งเทียนกลับตัว | ปิดสถานะ |

---

## 8. ข้อกำหนดทางเทคนิค

### 8.1 ข้อกำหนดของระบบ

| องค์ประกอบ | ข้อกำหนด |
|-----------|--------------|
| ความหน่วงของฟีดข้อมูล | <50ms สำหรับ Crypto CEX; <10ms สำหรับ Futures |
| อัตราสแนปชอต Order Book | 100ms ขั้นต่ำ; 10ms ที่แนะนำ |
| ฟีดการซื้อขาย | Tick-by-Tick, หน่วง <20ms |
| การประมวลผล | Streaming แบบเรียลไทม์ (Apache Kafka / Redis Streams) |
| จัดเก็บ | Time-Series DB (TimescaleDB / InfluxDB) |
| ข้อมูล Backtest | ข้อมูล Tick ขั้นต่ำ 2 ปี; แนะนำ 5 ปี |

### 8.2 พารามิเตอร์สัญญาณ

| พารามิเตอร์ | ค่าเริ่มต้น | ช่วง | คำอธิบาย |
|-----------|---------|-------|-------------|
| `imbalance_threshold` | 0.4 | [0.2, 0.8] | ความไม่สมดุลถ่วงน้ำหนักขั้นต่ำสำหรับสัญญาณ |
| `delta_window` | 100 trades | [50, 500] | หน้าต่างสำหรับ Cumulative Delta |
| `absorption_min_size` | 3x avg | [2x, 10x] | ขนาดขั้นต่ำสำหรับตรวจจับ Absorption |
| `liquidity_pool_threshold` | 2x avg vol | [1.5x, 5x] | ปริมาณคลัสเตอร์ขั้นต่ำสำหรับ Pool |
| `session_filter` | True | Bool | เทรดเฉพาะช่วง Kill Zones |
| `spread_max_multiple` | 2.0 | [1.5, 5.0] | Spread สูงสุดเทียบกับค่าเฉลี่ย |

---

## 9. โมเดลทางคณิตศาสตร์

### 9.1 ความเป็นพิษของ Order Flow: VPIN (Volume-Synchronized Probability of Informed Trading)

VPIN (Easley, Lopez de Prado, and O'Hara, 2012) วัดความน่าจะเป็นที่ Order Flow เป็นแบบมีข้อมูล (เป็นพิษ):

$$\text{VPIN} = \frac{\sum_{\tau=1}^{n} |V_{\tau}^{S} - V_{\tau}^{B}|}{n \cdot V}$$

โดยที่:
- $V_{\tau}^{S}$ = ปริมาณขายในถัง Volume $\tau$
- $V_{\tau}^{B}$ = ปริมาณซื้อในถัง Volume $\tau$
- $n$ = จำนวนถัง Volume
- $V$ = ปริมาณต่อถัง

**การตีความ:**
- VPIN > 0.7: ความเป็นพิษสูง — เทรดเดอร์ที่มีข้อมูลกำลังเคลื่อนไหว, Spread ควรกว้างขึ้น
- VPIN 0.3-0.7: ช่วงปกติ
- VPIN < 0.3: ความเป็นพิษต่ำ — ส่วนใหญ่เป็น Noise Trading

### 9.2 Hasbrouck Information Share

วัดการมีส่วนร่วมของแต่ละตลาด/แพลตฟอร์มต่อการค้นพบราคา:

$$IS_j = \frac{\gamma_j^2 \cdot \Omega_{jj}}{\gamma' \Omega \gamma}$$

โดยที่:
- $\gamma_j$ = น้ำหนักปัจจัยร่วมสำหรับตลาด $j$
- $\Omega$ = เมทริกซ์ความแปรปรวนร่วมของนวัตกรรมรูปแบบลดรูป

สำหรับคริปโต สิ่งนี้ช่วยกำหนดว่าตลาดใดนำการค้นพบราคา (โดยทั่วไปคือ Binance สำหรับ BTC)

### 9.3 อัตราส่วนการขาดสภาพคล่องของ Amihud (Amihud Illiquidity Ratio)

ตัววัดที่เรียบง่ายแต่มีประสิทธิภาพของผลกระทบต่อราคาต่อหน่วยของปริมาณ:

$$\text{ILLIQ}_t = \frac{|r_t|}{V_t}$$

โดยที่:
- $r_t$ = ผลตอบแทนในช่วง $t$
- $V_t$ = ปริมาณดอลลาร์ในช่วง $t$

ILLIQ สูงหมายถึงตลาดมีสภาพคล่องน้อยกว่าที่ Order Flow มีผลกระทบมากขึ้น

---

## 10. พารามิเตอร์ความเสี่ยง

### 10.1 การกำหนดขนาดสถานะตามสภาพคล่อง

$$\text{Max Position} = \min\left(\frac{\text{Risk Budget}}{\text{Stop Distance}}, \frac{V_{avg} \cdot \text{Participation Rate}}{1}\right)$$

โดยที่:
- Risk Budget = เงินทุนในบัญชี * ความเสี่ยงต่อเทรด (โดยทั่วไป 1-2%)
- Participation Rate = สัดส่วนสูงสุดของปริมาณเฉลี่ย (โดยทั่วไป 1-5%)

### 10.2 การวาง Stop Loss

การวิเคราะห์ Order Flow ให้ข้อมูลสำหรับการวาง Stop:

| วิธีการ | คำอธิบาย | การใช้งาน |
|--------|-------------|-------------|
| เลยจุดดูดซับ (Beyond Absorption) | วาง Stop เลยระดับ Absorption ที่ระบุ | หลังจากเข้าที่จุดดูดซับ |
| เลย Liquidity Pool | วาง Stop เลยคลัสเตอร์สภาพคล่องถัดไป | การเข้าตามสภาพคล่อง |
| Delta Invalidation | ออกเมื่อ CVD กลับตัว X% | การเข้าตามเทรนด์ |
| ตาม Spread | 3 เท่าของ Spread เฉลี่ยจากจุดเข้า | การเข้า Scalping |

### 10.3 เป้าหมายความเสี่ยง/ผลตอบแทน

| ประเภทกลยุทธ์ | R:R ขั้นต่ำ | R:R ทั่วไป | เวลาถือสูงสุด |
|---------------|-------------|-------------|-----------------|
| Scalping (Microstructure) | 1.5:1 | 2:1 | 5-30 นาที |
| Intraday (Absorption/Sweep) | 2:1 | 3:1 | 1-8 ชั่วโมง |
| Swing (Institutional Flow) | 3:1 | 5:1 | 1-5 วัน |

---

## 11. ขั้นตอนการดำเนินการ (Execution Flow)

### 11.1 สถาปัตยกรรมระบบระดับสูง

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                       │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ L2 Feed  │  │ Trade    │  │ Tick     │  │ Funding  │   │
│  │ (DOM)    │  │ Feed     │  │ Data     │  │ Rate     │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │              │         │
│       ▼              ▼              ▼              ▼         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              MESSAGE BUS (Kafka / Redis)              │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│               PROCESSING LAYER                               │
│                          │                                   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │              ORDER FLOW ENGINE                        │   │
│  │                                                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │ Book        │  │ Delta       │  │ Liquidity   │  │   │
│  │  │ Analyzer    │  │ Calculator  │  │ Mapper      │  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │   │
│  │         │                │                │          │   │
│  │         ▼                ▼                ▼          │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │         SIGNAL AGGREGATOR                    │    │   │
│  │  │   Combines all OF signals into score         │    │   │
│  │  └──────────────────┬───────────────────────────┘    │   │
│  └─────────────────────┼────────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│              DECISION LAYER                                   │
│                          │                                   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │         STRATEGY INTEGRATION                          │   │
│  │   Order Flow Score + Other Module Signals             │   │
│  │   → Final Trade Decision (LONG / SHORT / FLAT)        │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                          │                                   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │         RISK MANAGEMENT                               │   │
│  │   Position sizing, SL/TP, exposure limits             │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│              EXECUTION LAYER                                  │
│                          │                                   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │         ORDER ROUTER                                  │   │
│  │   Smart order routing, venue selection, slippage      │   │
│  │   minimization, iceberg execution                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 11.2 Pseudocode: ลูปหลัก

```python
class OrderFlowSystem:
    def __init__(self, config):
        self.book_analyzer = OrderBookAnalyzer(config)
        self.delta_calc = DeltaCalculator(config)
        self.liquidity_mapper = LiquidityMapper(config)
        self.signal_agg = SignalAggregator(config)
        self.risk_mgr = RiskManager(config)
        self.executor = OrderExecutor(config)
    
    async def main_loop(self):
        while self.running:
            # 1. Receive market data update
            update = await self.data_feed.next()
            
            # 2. Update internal state
            if update.type == 'BOOK_UPDATE':
                self.book_analyzer.update(update)
            elif update.type == 'TRADE':
                self.delta_calc.update(update)
                self.liquidity_mapper.update(update)
            
            # 3. Generate order flow signals
            of_signals = {
                'book_imbalance': self.book_analyzer.get_imbalance(),
                'delta': self.delta_calc.get_cumulative_delta(),
                'delta_divergence': self.delta_calc.check_divergence(),
                'absorption': self.book_analyzer.detect_absorption(),
                'liquidity_pools': self.liquidity_mapper.get_pools(),
                'vpin': self.delta_calc.get_vpin(),
            }
            
            # 4. Aggregate into composite score
            composite = self.signal_agg.score(of_signals)
            
            # 5. Check against existing strategy signals
            if self.strategy_signal_pending:
                decision = self.confirm_signal(
                    self.strategy_signal_pending, composite
                )
                
                if decision == 'CONFIRMED':
                    # 6. Calculate position size
                    size = self.risk_mgr.calculate_size(
                        signal=self.strategy_signal_pending,
                        liquidity=of_signals['liquidity_pools']
                    )
                    
                    # 7. Execute
                    await self.executor.execute(
                        signal=self.strategy_signal_pending,
                        size=size,
                        sl=self.risk_mgr.stop_loss,
                        tp=self.risk_mgr.take_profit
                    )
            
            # 8. Monitor existing positions
            await self.monitor_positions(of_signals)
```

---

## 12. การบูรณาการข้ามโมดูล

### 12.1 แผนที่การบูรณาการ

```
Module 02 (Wyckoff)
  │ Phase identification (Accumulation/Distribution)
  │ Supply/Demand tests
  └──► ORDER FLOW confirms:
       - Volume delta during spring/upthrust
       - Absorption at support/resistance
       - Institutional accumulation patterns

Module 04 (Smart Money Concepts)
  │ Order Blocks, Breaker Blocks, FVGs
  │ Displacement, Inducement
  └──► ORDER FLOW confirms:
       - OB with high delta = stronger zone
       - FVG with volume void = true inefficiency
       - Displacement with extreme taker flow = valid

Module 07 (Price Action)
  │ Candlestick patterns, structure breaks
  └──► ORDER FLOW confirms:
       - Pin bar with absorption = valid reversal
       - Engulfing with delta shift = valid signal
       - Break of structure with volume = true BoS

Module 08 (Volume Profile)
  │ POC, Value Area, Volume Nodes
  └──► ORDER FLOW provides:
       - Real-time flow within profile zones
       - Delta at POC for directional bias
       - Absorption at HVN/LVN boundaries
```

### 12.2 การบูรณาการคะแนนความเชื่อมั่น

แต่ละโมดูลมีส่วนร่วมในคะแนนความเชื่อมั่นรวม:

$$\text{Confidence} = \sum_{m=1}^{M} w_m \cdot S_m$$

โดยที่:
- $w_m$ = น้ำหนักสำหรับโมดูล $m$ (Order Flow มักถ่วงน้ำหนัก 25-35%)
- $S_m$ = คะแนนสัญญาณจากโมดูล $m$ (ปรับมาตรฐานเป็น [0, 1])

**การปรับน้ำหนัก Order Flow:**
- ช่วงความผันผวนสูง: เพิ่มน้ำหนัก Order Flow (น่าเชื่อถือกว่า)
- ช่วงความผันผวนต่ำ: ลดน้ำหนัก Order Flow (สัญญาณน้อยกว่า)
- ช่วงข่าว: ปิดชั่วคราว (การไหลกลายเป็นสัญญาณรบกวน)

---

## 13. เอกสารอ้างอิง

### บทความวิชาการ

1. **Kyle, A. S.** (1985). "Continuous Auctions and Insider Trading." *Econometrica*, 53(6), 1315-1335. — โมเดลพื้นฐานของการเทรดแบบมีข้อมูลและผลกระทบต่อราคา

2. **Glosten, L. R., & Milgrom, P. R.** (1985). "Bid, Ask and Transaction Prices in a Specialist Market with Heterogeneously Informed Traders." *Journal of Financial Economics*, 14(1), 71-100. — โมเดลการเลือกเชิงลบ (Adverse Selection) ของ Spread

3. **O'Hara, M.** (1995). *Market Microstructure Theory*. Blackwell Publishers. — ตำราที่ครอบคลุมเกี่ยวกับจุลภาคตลาด

4. **Hasbrouck, J.** (2007). *Empirical Market Microstructure*. Oxford University Press. — วิธีการเชิงประจักษ์สำหรับการศึกษาจุลภาคตลาด

5. **Lee, C. M. C., & Ready, M. J.** (1991). "Inferring Trade Direction from Intraday Data." *Journal of Finance*, 46(2), 733-746. — อัลกอริทึมจำแนกประเภทการซื้อขาย

6. **Easley, D., Lopez de Prado, M. M., & O'Hara, M.** (2012). "Flow Toxicity and Liquidity in a High-Frequency World." *Review of Financial Studies*, 25(5), 1457-1493. — ระเบียบวิธี VPIN

7. **Bouchaud, J. P., Farmer, J. D., & Lillo, F.** (2009). "How Markets Slowly Digest Changes in Supply and Demand." In *Handbook of Financial Markets: Dynamics and Evolution*, 57-160. — กฎผลกระทบราคาแบบรากที่สอง

8. **Stoll, H. R.** (1989). "Inferring the Components of the Bid-Ask Spread: Theory and Empirical Tests." *Journal of Finance*, 44(1), 115-134. — การแยกองค์ประกอบของ Spread

9. **Cont, R., Stoikov, S., & Talreja, R.** (2010). "A Stochastic Model for Order Book Dynamics." *Operations Research*, 58(3), 549-563. — โมเดลทางคณิตศาสตร์ของพลวัต Order Book

10. **Cartea, A., Jaimungal, S., & Penalva, J.** (2015). *Algorithmic and High-Frequency Trading*. Cambridge University Press. — เอกสารอ้างอิงที่ครอบคลุมเกี่ยวกับการเทรดอัลกอริทึม

### เอกสารอ้างอิงจากอุตสาหกรรมและนักปฏิบัติ

11. **ICT (Inner Circle Trader)** — แนวคิดสภาพคล่อง, Kill Zones, Judas Swing, ระเบียบวิธี Order Flow ของสถาบัน

12. **Dalton, J. F., Jones, E. T., & Dalton, R. B.** (1993). *Mind Over Markets*. — Market Profile และทฤษฎีตลาดประมูล

13. **Bookmap / Exocharts / Quantower** — แพลตฟอร์มการแสดงผล Order Flow และเอกสารเกี่ยวกับ Footprint Charts, Delta Analysis, และ Order Book Heatmaps

14. **CME Group** — "Understanding FX Futures" และเอกสารจุลภาคตลาด

15. **Bitwise Asset Management** (2019). "Presentation to the U.S. Securities and Exchange Commission." — การวิเคราะห์ปริมาณจริงกับปริมาณปลอมในตลาดคริปโต

---

> **เอกสารถัดไป**: [01_order_book_analysis.md](./01_order_book_analysis.md) — เจาะลึกการตีความข้อมูล Level 2, โมเดลความไม่สมดุลของ Order Book, และอัลกอริทึมสำหรับนำไปใช้งาน
