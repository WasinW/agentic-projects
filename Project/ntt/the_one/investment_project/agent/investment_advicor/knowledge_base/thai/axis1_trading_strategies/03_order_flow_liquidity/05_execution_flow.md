# ขั้นตอนการทำงานครบถ้วนสำหรับระบบเทรด Order Flow

> **แกน 1 — กลยุทธ์การเทรด | โมดูล 03 — Order Flow และสภาพคล่อง (Liquidity)**
> เอกสาร: 05_execution_flow.md
> เวอร์ชัน: 2.0 | อัปเดตล่าสุด: 2026-04-12
> การจัดประเภท: ฐานความรู้หลัก — ระบบเทรด AI แบบหลายเอเจนต์ (Multi-Agent AI Trading System)

---

## สารบัญ

1. [บทนำ](#1-introduction)
2. [อัลกอริทึมทีละขั้นตอน](#2-step-by-step-algorithm)
3. [ข้อกำหนดข้อมูล](#3-data-requirements)
4. [Pipeline การสร้างสัญญาณ](#4-signal-generation-pipeline)
5. [พารามิเตอร์ความเสี่ยงสำหรับกลยุทธ์ Order Flow](#5-risk-parameters-for-order-flow-strategies)
6. [แบบจำลองการกำหนดขนาดสถานะ](#6-position-sizing-models)
7. [Pseudocode สำหรับการนำไปใช้แบบเต็ม](#7-pseudocode-for-full-implementation)
8. [ข้อพิจารณา Latency: Crypto เทียบกับ Forex](#8-latency-considerations-crypto-vs-forex)
9. [สถาปัตยกรรมระบบ](#9-system-architecture)
10. [กรอบ Backtesting](#10-backtesting-framework)
11. [การติดตามและการแจ้งเตือน](#11-monitoring--alerting)
12. [ตัวชี้วัดประสิทธิภาพ](#12-performance-metrics)
13. [โหมดล้มเหลวและการกู้คืน](#13-failure-modes--recovery)
14. [การตั้งค่า Deployment](#14-deployment-configuration)
15. [เอกสารอ้างอิง](#15-references)

---

## 1. บทนำ

### 1.1 วัตถุประสงค์

เอกสารนี้ให้ขั้นตอนการทำงานครบถ้วนพร้อมใช้งานจริง (production-ready) สำหรับระบบเทรด Order Flow และสภาพคล่อง มันรวมแนวคิดทั้งหมดจากเอกสาร 00-04 เป็น pipeline รวมที่สามารถนำไปใช้งานเป็นส่วนหนึ่งของระบบเทรด AI แบบหลายเอเจนต์

### 1.2 ขอบเขตระบบ

```
SYSTEM BOUNDARY:
═══════════════

INPUTS:                          SYSTEM:                    OUTPUTS:
─────────                        ───────                    ────────
┌──────────────┐    ┌─────────────────────────────────┐    ┌──────────┐
│ Market Data  │───►│                                 │───►│ Orders   │
│ • L2 Book   │    │    ORDER FLOW TRADING ENGINE     │    │ • Entry  │
│ • Trades    │    │                                 │    │ • Exit   │
│ • Tick Data │    │  ┌───────────────────────────┐  │    │ • Modify │
│              │    │  │ Signal Generation Layer   │  │    └──────────┘
│ Config/State │───►│  │ • Book Analysis (Doc 01)  │  │
│ • Parameters│    │  │ • Liquidity Map (Doc 02)  │  │    ┌──────────┐
│ • Positions │    │  │ • Hunt Detection (Doc 03) │  │───►│ Logs &   │
│ • Risk State│    │  │ • Volume Delta (Doc 04)   │  │    │ Metrics  │
│              │    │  └───────────────────────────┘  │    └──────────┘
│ External    │───►│  ┌───────────────────────────┐  │
│ • Calendar  │    │  │ Decision & Risk Layer     │  │    ┌──────────┐
│ • Sessions  │    │  │ • Signal aggregation      │  │───►│ Alerts   │
│ • Other Mods│    │  │ • Risk management         │  │    └──────────┘
└──────────────┘    │  │ • Position sizing         │  │
                    │  └───────────────────────────┘  │
                    │  ┌───────────────────────────┐  │
                    │  │ Execution Layer           │  │
                    │  │ • Order routing           │  │
                    │  │ • Slippage control        │  │
                    │  │ • Fill management         │  │
                    │  └───────────────────────────┘  │
                    └─────────────────────────────────┘
```

### 1.3 โหมดการทำงาน

| โหมด | คำอธิบาย | แหล่งข้อมูล | เป้าหมาย Latency |
|------|-------------|-------------|---------------|
| **Live Trading** | การทำงานเวลาจริงกับตลาดจริง | Exchange feeds | <100ms end-to-end |
| **Paper Trading** | การทำงานจำลองด้วยข้อมูลจริง | Exchange feeds | <100ms (pipeline เดียวกัน) |
| **Backtesting** | การจำลองประวัติ | ข้อมูล tick/L2 ที่จัดเก็บ | เร็วที่สุดเท่าที่จะได้ |
| **Research** | การพัฒนาและวิเคราะห์กลยุทธ์ | ประวัติ + จำลอง | N/A |

---

## 2. อัลกอริทึมทีละขั้นตอน

### 2.1 Flow ระดับสูง

```
┌────────────────────────────────────────────────────────────────────┐
│ ขั้นตอน 1: การเตรียมก่อน SESSION                                    │
│ • กำหนดอคติ HTF (โครงสร้าง Daily/Weekly)                           │
│ • ทำแผนที่ liquidity pools (BSL/SSL) บน 4H/1D                     │
│ • ระบุ FVGs, OBs, Breakers ที่ active บน 4H/1H                   │
│ • จดบันทึกเหตุการณ์เวลาสำคัญ (ข่าว, เปิด session)                  │
│ • กำหนดตาราง kill zone                                             │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│ ขั้นตอน 2: การรับข้อมูล (ต่อเนื่อง)                                │
│ • รับอัปเดต L2 order book                                         │
│ • รับ trade feed (Time & Sales)                                    │
│ • อัปเดต VWAP, Volume Profile, Delta ต่อเนื่อง                    │
│ • สร้าง order book state ใหม่ทุกครั้งที่อัปเดต                     │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│ ขั้นตอน 3: การสร้างสัญญาณ (ทุกอัปเดต/ปิดแท่ง)                     │
│                                                                     │
│ 3a. สัญญาณ Order Book:                                             │
│     • Weighted imbalance                                            │
│     • การตรวจจับ wall                                               │
│     • รูปแบบ absorption                                             │
│     • การตรวจจับ spoofing                                           │
│     • การตรวจจับ iceberg                                            │
│                                                                     │
│ 3b. สัญญาณสภาพคล่อง:                                              │
│     • ความใกล้ชิดและการตรวจจับ sweep ของ BSL/SSL                    │
│     • การก่อตัวและติดตาม fill ของ FVG                               │
│     • ราคาเข้าโซน OTE                                              │
│     • การทดสอบ Breaker Block                                       │
│                                                                     │
│ 3c. สัญญาณ Flow สถาบัน:                                           │
│     • การตรวจจับ Judas Swing                                       │
│     • การระบุเฟส AMD                                               │
│     • การยืนยันจังหวะ Kill zone                                    │
│     • การตรวจจับ Stop hunt                                         │
│                                                                     │
│ 3d. สัญญาณ Volume Delta:                                           │
│     • ทิศทาง delta ต่อแท่ง                                         │
│     • CVD divergence                                                │
│     • Delta exhaustion                                              │
│     • ตำแหน่ง VWAP                                                 │
│     • การวิเคราะห์ Volume Profile (POC/VA)                         │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│ ขั้นตอน 4: การรวมสัญญาณและการให้คะแนน                              │
│ • รวมสัญญาณทั้งหมดเป็นคะแนนทิศทางรวม                              │
│ • ใช้ฟิลเตอร์อคติ HTF (ปฏิเสธสัญญาณที่สวนเทรนด์ HTF)             │
│ • ใช้ฟิลเตอร์ kill zone (ปฏิเสธสัญญาณนอกโซนที่ active)           │
│ • คำนวณคะแนน confluence                                           │
│ • เปรียบเทียบกับเกณฑ์ขั้นต่ำ                                      │
│ • จัดอันดับสัญญาณที่แข่งขันตามคุณภาพ                               │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│ ขั้นตอน 5: การตรวจสอบความเสี่ยง                                    │
│ • ตรวจขีดจำกัดขาดทุนรายวัน (ไม่เกิน)                              │
│ • ตรวจสถานะเปิดสูงสุด                                             │
│ • ตรวจ correlation กับสถานะที่มีอยู่                               │
│ • ตรวจสอบ R:R ตรงตามขั้นต่ำ (>2:1)                                │
│ • คำนวณขนาดสถานะ                                                  │
│ • ยืนยัน margin/ทุนเพียงพอ                                        │
│ • ตรวจปฏิทินข่าว (ไม่มี high-impact ภายใน buffer)                  │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│ ขั้นตอน 6: การส่งคำสั่ง                                             │
│ • กำหนดประเภทคำสั่ง (limit vs market)                               │
│ • ตั้งราคาเข้า (CE ของ FVG, ระดับ OTE, etc.)                      │
│ • ตั้ง stop loss (anti-hunt placement)                              │
│ • ตั้งระดับ take profit (TP1, TP2, TP3)                            │
│ • ส่งคำสั่งไป exchange                                             │
│ • ยืนยัน fill                                                      │
│ • เริ่มติดตามสถานะ                                                 │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│ ขั้นตอน 7: การจัดการสถานะ (ต่อเนื่องขณะสถานะเปิด)                  │
│ • ติดตามสัญญาณออก                                                  │
│ • จัดการออกบางส่วนที่ระดับ TP                                      │
│ • ปรับ trailing stop ตาม order flow                                │
│ • ติดตามสัญญาณที่เป็นลบ (delta flip, absorption ตรงข้าม)           │
│ • การจัดการตามเวลา (สิ้นสุด session, ออก kill zone)                │
│ • ออกฉุกเฉินเมื่อ spread พุ่งหรือวิกฤตสภาพคล่อง                   │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│ ขั้นตอน 8: การวิเคราะห์หลังเทรดและการบันทึก                        │
│ • บันทึกพารามิเตอร์และผลลัพธ์เทรดทั้งหมด                          │
│ • อัปเดตตัวชี้วัดประสิทธิภาพ                                      │
│ • ประเมินคุณภาพสัญญาณ (สัญญาณถูกหรือไม่?)                        │
│ • ป้อนผลลัพธ์กลับสำหรับการปรับพารามิเตอร์                         │
│ • สร้างรายงานประสิทธิภาพรายวัน/รายสัปดาห์                        │
└────────────────────────────────────────────────────────────────────┘
```

### 2.2 Decision Tree

```python
def main_decision_flow(state: SystemState) -> Action:
    """
    Top-level decision tree for the order flow trading system.
    Called on each significant market update.
    """
    
    # GATE 1: Are we in an active trading period?
    if not state.kill_zone_active:
        if state.has_open_positions:
            return manage_positions_passively(state)
        return Action.WAIT
    
    # GATE 2: Are risk limits intact?
    if state.daily_loss_exceeded or state.max_positions_reached:
        if state.has_open_positions:
            return manage_positions_defensively(state)
        return Action.WAIT
    
    # GATE 3: Is there a tradeable signal?
    signal = state.best_signal
    if not signal or signal.confluence_score < state.config.min_confluence:
        if state.has_open_positions:
            return manage_positions_normally(state)
        return Action.WAIT
    
    # GATE 4: Does signal align with HTF bias?
    if not signal_aligns_with_bias(signal, state.htf_bias):
        return Action.WAIT
    
    # GATE 5: Is R:R acceptable?
    trade_params = calculate_trade_params(signal, state)
    if trade_params.risk_reward < state.config.min_rr:
        return Action.WAIT
    
    # GATE 6: No conflicting news?
    if high_impact_news_imminent(state.calendar, buffer_minutes=15):
        return Action.WAIT
    
    # ALL GATES PASSED → EXECUTE
    return Action.ENTER_TRADE(trade_params)
```

---

## 3. ข้อกำหนดข้อมูล

### 3.1 ประเภทและแหล่งข้อมูล

| ประเภทข้อมูล | คำอธิบาย | แหล่ง (Forex) | แหล่ง (Crypto) | อัตราอัปเดต |
|-----------|-------------|---------------|----------------|-------------|
| **L2 Order Book** | คำสั่งค้างที่แต่ละระดับราคา | CME MDP 3.0, ECN feeds | Exchange WebSocket (depth) | 10-100ms |
| **Trade Feed** | เทรดที่ execute พร้อม aggressor | CME, broker feed | Exchange WebSocket (trade) | เวลาจริง |
| **OHLCV Bars** | ข้อมูลราคา/ปริมาณรวม | Broker API, TradingView | Exchange REST/WS | ต่อแท่ง |
| **Tick Data** | ทุกการเปลี่ยนแปลงราคา | CQG, TrueFX | Exchange trade stream | เวลาจริง |
| **Funding Rate** | Funding ของ perpetual swap | N/A | Exchange API | ทุก 8 ชม. |
| **Open Interest** | สัญญาเปิดทั้งหมด | CME | Exchange API | 1-5 นาที |
| **Liquidation Data** | การปิดสถานะบังคับ | N/A | Exchange WS (ทางเลือก) | เวลาจริง |
| **Economic Calendar** | เหตุการณ์ข่าวที่กำหนด | ForexFactory, Investing.com | API | Static + alerts |
| **Session Times** | ขอบเขต session ตลาด | Static configuration | Static configuration | Static |

### 3.2 ข้อกำหนดคุณภาพข้อมูล

| ตัวชี้วัด | ข้อกำหนด | ผลกระทบหากไม่ตรง |
|--------|-------------|-------------------|
| **Latency** | <50ms จาก exchange ถึงสัญญาณ | สัญญาณล้าสมัย, fill แย่กว่า |
| **ความสมบูรณ์** | >99.9% การส่งข้อความ | ขาดเทรด → delta ผิด |
| **ลำดับ** | Timestamps เพิ่มขึ้นแบบ monotonic | สร้างสถานะใหม่ไม่ถูก |
| **ความแม่นยำ** | ไม่มีเทรดซ้ำ | ค่า delta สูงเกินจริง |
| **Uptime** | >99.5% feed availability | ช่วงมืด, พลาดสัญญาณ |

### 3.3 Schema การจัดเก็บข้อมูล

```sql
-- Trades table (primary data source for delta)
CREATE TABLE trades (
    id BIGSERIAL PRIMARY KEY,
    exchange VARCHAR(20) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    price DECIMAL(20, 10) NOT NULL,
    quantity DECIMAL(20, 10) NOT NULL,
    side VARCHAR(4) NOT NULL,  -- 'BUY' or 'SELL'
    trade_id VARCHAR(50),
    
    INDEX idx_symbol_time (symbol, timestamp),
    INDEX idx_exchange_symbol (exchange, symbol)
);

-- Order book snapshots (for replay/backtesting)
CREATE TABLE order_book_snapshots (
    id BIGSERIAL PRIMARY KEY,
    exchange VARCHAR(20) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    bids JSONB NOT NULL,
    asks JSONB NOT NULL,
    
    INDEX idx_symbol_time (symbol, timestamp)
);

-- Signals generated
CREATE TABLE signals (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(50) NOT NULL,
    direction VARCHAR(5) NOT NULL,
    strength DECIMAL(5, 4) NOT NULL,
    confluence_score DECIMAL(5, 4),
    parameters JSONB,
    acted_on BOOLEAN DEFAULT FALSE,
    outcome VARCHAR(20),
    
    INDEX idx_symbol_time (symbol, timestamp)
);

-- Positions and trades
CREATE TABLE positions (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(5) NOT NULL,
    entry_price DECIMAL(20, 10),
    entry_time TIMESTAMPTZ,
    exit_price DECIMAL(20, 10),
    exit_time TIMESTAMPTZ,
    size DECIMAL(20, 10),
    stop_loss DECIMAL(20, 10),
    take_profit DECIMAL(20, 10),
    status VARCHAR(20),
    pnl DECIMAL(20, 10),
    pnl_pct DECIMAL(10, 6),
    signal_id BIGINT REFERENCES signals(id),
    metadata JSONB
);
```

### 3.4 ข้อกำหนดข้อมูลประวัติสำหรับ Backtesting

| สินทรัพย์ | ประวัติขั้นต่ำ | ประวัติเหมาะสม | ความละเอียดข้อมูล |
|-------|----------------|---------------|-----------------|
| Forex Major | 2 ปี | 5-10 ปี | ข้อมูล tick หรือแท่ง 1 วินาที |
| Forex Cross | 2 ปี | 5 ปี | แท่ง 1 นาทีขั้นต่ำ |
| BTC/USDT | 2 ปี | 4-5 ปี (ตั้งแต่มีสภาพคล่อง) | ข้อมูล tick ดีกว่า |
| ETH/USDT | 2 ปี | 3-4 ปี | ข้อมูล tick ดีกว่า |
| Altcoins | 1 ปี | 2 ปี | แท่ง 1 นาทีขั้นต่ำ |

---

## 4. Pipeline การสร้างสัญญาณ

### 4.1 สถาปัตยกรรม Pipeline

```
RAW DATA STREAMS
      │
      ├── L2 Book Updates ──┐
      │                      │
      ├── Trade Feed ────────┤
      │                      │
      ├── Bar Close ─────────┤
      │                      │
      ▼                      ▼
┌─────────────────────────────────────────────────┐
│          DATA NORMALIZATION LAYER                 │
│  • การจัดแนว timestamp                           │
│  • การปรับมาตรฐาน symbol                         │
│  • การแปลงหน่วย (lots/contracts/coins)           │
│  • การตรวจจับและลบข้อมูลซ้ำ                      │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│          FEATURE CALCULATION LAYER               │
│                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │ Order Book  │ │   Delta     │ │  Volume   │ │
│  │ Features    │ │  Features   │ │  Profile  │ │
│  │             │ │             │ │  Features │ │
│  │ • Imbalance │ │ • Bar delta │ │ • POC     │ │
│  │ • Walls     │ │ • CVD      │ │ • VAH/VAL │ │
│  │ • Spread    │ │ • Delta ROC│ │ • HVN/LVN │ │
│  │ • Depth     │ │ • Strength │ │           │ │
│  │ • Entropy   │ │ • BVC      │ │           │ │
│  └──────┬──────┘ └──────┬─────┘ └─────┬─────┘ │
│         │               │             │         │
│  ┌──────┴──────┐ ┌──────┴─────┐ ┌─────┴─────┐ │
│  │ Liquidity  │ │    VWAP    │ │  Session  │ │
│  │ Features   │ │  Features  │ │  Features │ │
│  │             │ │            │ │           │ │
│  │ • BSL/SSL  │ │ • Value    │ │ • KZ flag │ │
│  │ • FVG list │ │ • Z-score  │ │ • AMD     │ │
│  │ • OTE zone │ │ • Bands    │ │ • Judas   │ │
│  │ • Breakers │ │ • Anchored │ │ • Phase   │ │
│  └──────┬──────┘ └──────┬─────┘ └─────┬─────┘ │
└─────────┼───────────────┼─────────────┼────────┘
          │               │             │
          ▼               ▼             ▼
┌─────────────────────────────────────────────────┐
│          SIGNAL DETECTION LAYER                  │
│                                                 │
│  แต่ละชุด feature สร้างสัญญาณอิสระ:             │
│                                                 │
│  • Book Imbalance Signal (ทิศทาง + ความแข็งแรง) │
│  • Absorption Signal (ระดับ + ทิศทาง)            │
│  • Delta Divergence Signal (ประเภท + ความแข็งแรง)│
│  • FVG Entry Signal (ระดับ + ทิศทาง)             │
│  • Stop Hunt Signal (ทิศทาง + ความมั่นใจ)        │
│  • Judas Swing Signal (ทิศทาง + เป้าหมาย)        │
│  • VWAP Extreme Signal (ทิศทาง + เป้าหมาย)       │
│  • POC Test Signal (ทิศทาง + ระดับ)              │
│  • Exhaustion Signal (ทิศทาง + ความแข็งแรง)       │
│                                                 │
└──────────────────────┬──────────────────────────┘
                       │ รายการสัญญาณอิสระ
                       ▼
┌─────────────────────────────────────────────────┐
│          SIGNAL AGGREGATION LAYER                │
│                                                 │
│  1. กรองตามทิศทาง (ต้องสอดคล้อง HTF)            │
│  2. กรองตาม kill zone (ต้อง active)              │
│  3. กรองตามความแข็งแรงขั้นต่ำ                    │
│  4. คำนวณ confluence (สัญญาณที่ระดับเดียวกัน)    │
│  5. ให้คะแนนทิศทางรวม                           │
│  6. เลือกโอกาสที่ดีที่สุด                         │
│                                                 │
│  OUTPUT: สัญญาณเทรดสุดท้าย                       │
│  • ทิศทาง: LONG / SHORT / NEUTRAL               │
│  • ระดับเข้า                                     │
│  • คะแนนความมั่นใจ [0, 1]                        │
│  • สัญญาณที่มีส่วน (สำหรับ logging)              │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
              [Risk & Execution Layer]
```

### 4.2 ลอจิกรวมสัญญาณ

```python
class SignalAggregator:
    """Combines multiple independent signals into a final trade decision."""
    
    SIGNAL_WEIGHTS = {
        'STOP_HUNT': 0.20,
        'CVD_DIVERGENCE': 0.18,
        'JUDAS_SWING': 0.15,
        'FVG_ENTRY': 0.12,
        'DELTA_EXHAUSTION': 0.10,
        'BOOK_IMBALANCE': 0.08,
        'ABSORPTION': 0.07,
        'VWAP_EXTREME': 0.05,
        'POC_TEST': 0.05,
    }
    
    def __init__(self, config):
        self.min_confluence = config.get('min_confluence_score', 0.55)
        self.min_signals = config.get('min_concurrent_signals', 2)
    
    def aggregate(self, signals: List[dict], htf_bias: str, 
                  kill_zone: bool) -> Optional[dict]:
        """Aggregate multiple signals into a final trade decision."""
        if not signals or not kill_zone:
            return None
        
        # FILTER: HTF Alignment
        aligned_signals = []
        for signal in signals:
            if htf_bias == 'NEUTRAL':
                aligned_signals.append(signal)
            elif signal['direction'] == ('LONG' if htf_bias == 'BULLISH' else 'SHORT'):
                aligned_signals.append(signal)
            elif signal['strength'] > 0.8:
                signal['strength'] *= 0.7
                aligned_signals.append(signal)
        
        if len(aligned_signals) < self.min_signals:
            return None
        
        # CALCULATE CONFLUENCE SCORE
        direction_scores = {'LONG': 0.0, 'SHORT': 0.0}
        
        for signal in aligned_signals:
            weight = self.SIGNAL_WEIGHTS.get(signal['type'], 0.05)
            score_contribution = weight * signal['strength']
            direction_scores[signal['direction']] += score_contribution
        
        if direction_scores['LONG'] > direction_scores['SHORT']:
            final_direction = 'LONG'
            final_score = direction_scores['LONG']
        else:
            final_direction = 'SHORT'
            final_score = direction_scores['SHORT']
        
        max_possible = sum(self.SIGNAL_WEIGHTS.values())
        confluence_score = final_score / max_possible
        
        if confluence_score < self.min_confluence:
            return None
        
        entry_levels = [
            s.get('entry_level', s.get('level')) 
            for s in aligned_signals 
            if s['direction'] == final_direction and (s.get('entry_level') or s.get('level'))
        ]
        
        entry_level = np.median(entry_levels) if entry_levels else None
        
        return {
            'direction': final_direction,
            'confluence_score': confluence_score,
            'entry_level': entry_level,
            'contributing_signals': [
                {'type': s['type'], 'strength': s['strength'], 'direction': s['direction']}
                for s in aligned_signals if s['direction'] == final_direction
            ],
            'signal_count': len([s for s in aligned_signals if s['direction'] == final_direction]),
            'htf_aligned': htf_bias != 'NEUTRAL' and final_direction == ('LONG' if htf_bias == 'BULLISH' else 'SHORT'),
            'timestamp': time.time()
        }
```

### 4.3 กฎลำดับความสำคัญสัญญาณ

เมื่อมีสัญญาณที่ valid หลายตัวพร้อมกัน:

| ลำดับ | กฎ | เหตุผล |
|----------|------|-----------|
| 1 | คะแนน confluence สูงสุดชนะ | ยิ่งยืนยันมาก = โอกาสสูงกว่า |
| 2 | เสมอ: สัญญาณที่สอดคล้อง HTF ชนะ | เทรดตามเทรนด์ปลอดภัยกว่า |
| 3 | เสมอ: สัญญาณที่มี R:R ดีกว่าชนะ | ผลตอบแทนต่อหน่วยความเสี่ยงดีกว่า |
| 4 | เสมอ: สัญญาณใกล้ระดับเข้ากว่าชนะ | Execute เร็วกว่า |
| 5 | เสมอ: สัญญาณที่มาก่อนชนะ | ข้อได้เปรียบจากการตรวจจับเร็ว |

---

## 5. พารามิเตอร์ความเสี่ยงสำหรับกลยุทธ์ Order Flow

### 5.1 การควบคุมความเสี่ยงระดับบัญชี

```python
class RiskManager:
    """Manages all risk parameters for the order flow trading system."""
    
    MAX_DAILY_LOSS_PCT = 0.04
    MAX_WEEKLY_LOSS_PCT = 0.08
    MAX_MONTHLY_LOSS_PCT = 0.15
    MAX_OPEN_POSITIONS = 3
    MAX_CORRELATED_POSITIONS = 2
    MAX_SINGLE_TRADE_RISK_PCT = 0.02
    DEFAULT_TRADE_RISK_PCT = 0.01
    
    STRATEGY_LIMITS = {
        'STOP_HUNT_REVERSAL': {'max_risk': 0.015, 'max_positions': 2, 'min_rr': 2.5},
        'CVD_DIVERGENCE': {'max_risk': 0.015, 'max_positions': 2, 'min_rr': 2.0},
        'JUDAS_SWING': {'max_risk': 0.020, 'max_positions': 1, 'min_rr': 3.0},
        'FVG_ENTRY': {'max_risk': 0.010, 'max_positions': 3, 'min_rr': 2.0},
        'VWAP_REVERSION': {'max_risk': 0.010, 'max_positions': 2, 'min_rr': 1.5},
        'BOOK_IMBALANCE': {'max_risk': 0.005, 'max_positions': 2, 'min_rr': 1.5},
    }
    
    def __init__(self, config):
        self.account_equity = config['initial_equity']
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0
        self.monthly_pnl = 0.0
        self.open_positions = []
        self.consecutive_losses = 0
```

### 5.2 Flow การคำนวณความเสี่ยงต่อเทรด

```
RISK CALCULATION FLOW:
═══════════════════════

                    Account Equity: $100,000
                           │
                           ▼
            ┌──────────────────────────────┐
            │ Base Risk: 1% = $1,000       │
            └──────────────┬───────────────┘
                           │
              ┌────────────┼────────────────┐
              │            │                │
              ▼            ▼                ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │ ความแข็งแรง │ │ Kill Zone   │ │ Consecutive │
    │ สัญญาณ      │ │ Multiplier  │ │ Loss Adj    │
    │             │ │             │ │             │
    │ 0.8 = 80%  │ │ London=1.5x│ │ 0 losses=1x│
    │             │ │ NY=1.3x    │ │ 2 losses=.75│
    │             │ │ Asian=0.7x │ │ 3+ loss=.5x│
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
           ▼               ▼               ▼
    ┌─────────────────────────────────────────────┐
    │ Adjusted Risk = $1,000 * 0.8 * 1.5 * 1.0   │
    │              = $1,200                        │
    └──────────────────────┬──────────────────────┘
                           │
                           ▼
    ┌─────────────────────────────────────────────┐
    │ SL Distance = |Entry - Stop| = 30 pips     │
    │ Pip Value = $10 per pip (standard lot)      │
    │                                             │
    │ Position Size = $1,200 / (30 * $10)         │
    │              = 4.0 mini lots                 │
    │              = 0.40 standard lots            │
    └─────────────────────────────────────────────┘
```

---

## 6. แบบจำลองการกำหนดขนาดสถานะ

### 6.1 แบบจำลอง Fixed Fractional (ค่าเริ่มต้น)

$$\text{Size} = \frac{f \cdot E}{|P_{entry} - P_{stop}| \cdot \text{PipValue}}$$

โดยที่:
- $f$ = สัดส่วนความเสี่ยง (0.01-0.02)
- $E$ = Equity บัญชีปัจจุบัน
- $P_{entry}$ = ราคาเข้า
- $P_{stop}$ = ราคา stop loss
- PipValue = มูลค่าดอลลาร์ต่อ pip ของเครื่องมือ

### 6.2 Kelly Criterion (Aggressive — ใช้ด้วยความระวัง)

$$f^* = \frac{p \cdot b - q}{b}$$

โดยที่:
- $p$ = ความน่าจะเป็นชนะ (จาก backtesting)
- $q$ = 1 - p (ความน่าจะเป็นแพ้)
- $b$ = อัตราชนะ/แพ้ (กำไรเฉลี่ย / ขาดทุนเฉลี่ย)

**ในทางปฏิบัติ ใช้ fractional Kelly (25-50% ของ Kelly optimal) เพื่อลด variance:**

$$f_{practical} = 0.25 \cdot f^*$$

### 6.3 การกำหนดขนาดปรับด้วยความผันผวน (Volatility-Adjusted)

$$\text{Size} = \frac{f \cdot E}{\text{ATR}_{14} \cdot \text{ATR\_Multiple} \cdot \text{PipValue}}$$

สิ่งนี้ปรับขนาดสถานะเล็กลงโดยอัตโนมัติในตลาดที่ผันผวนและใหญ่ขึ้นในตลาดที่สงบ

### 6.4 การกำหนดขนาดจำกัดด้วยสภาพคล่อง (Liquidity-Constrained)

$$\text{Size} = \min\left(\text{Size}_{risk}, \text{ADV} \cdot \text{MaxParticipation}\right)$$

โดยที่:
- $\text{ADV}$ = ปริมาณเฉลี่ยรายวัน
- MaxParticipation = เปอร์เซ็นต์สูงสุดของปริมาณรายวัน (1-5%)

สิ่งนี้ป้องกันไม่ให้ระบบเปิดสถานะใหญ่เกินไปเทียบกับสภาพคล่องที่มี

---

## 7. Pseudocode สำหรับการนำไปใช้แบบเต็ม

### 7.1 การนำระบบไปใช้แบบสมบูรณ์

```python
"""
ORDER FLOW TRADING SYSTEM — COMPLETE IMPLEMENTATION
===================================================
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from collections import deque
import numpy as np

from .order_book_analyzer import OrderBookAnalyzer, OrderBookState
from .liquidity_mapper import LiquidityMapper, LiquidityPool, FVGDetector
from .stop_hunt_detector import StopHuntDetector, JudasSwingDetector
from .volume_delta import DeltaCalculator, CVDDivergenceDetector, VWAP, VolumeProfileBuilder
from .kill_zones import KillZoneManager
from .risk_manager import RiskManager, PositionSizer
from .signal_aggregator import SignalAggregator
from .execution import OrderExecutor
from .data_feed import DataFeed, CandleStore


@dataclass
class SystemConfig:
    """Configuration for the order flow trading system."""
    symbol: str = 'EUR/USD'
    market_type: str = 'FOREX'
    
    htf_timeframe: str = '1D'
    mtf_timeframe: str = '4H'
    entry_timeframe: str = '1H'
    precision_timeframe: str = '15M'
    
    min_confluence_score: float = 0.55
    min_signal_strength: float = 0.5
    min_risk_reward: float = 2.0
    min_concurrent_signals: int = 2
    
    risk_per_trade: float = 0.01
    max_daily_loss: float = 0.04
    max_positions: int = 3
    
    use_limit_orders: bool = True
    max_slippage_pips: float = 2.0
    order_timeout_seconds: float = 300.0
    
    kill_zone_only: bool = True
    news_buffer_minutes: int = 15


class OrderFlowTradingSystem:
    """
    Main class implementing the complete order flow trading system.
    """
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.logger = logging.getLogger('OrderFlowSystem')
        
        # Sub-systems
        self.book_analyzer = OrderBookAnalyzer({...})
        self.liquidity_mapper = LiquidityMapper({...})
        self.fvg_detector = FVGDetector({...})
        self.hunt_detector = StopHuntDetector({...})
        self.judas_detector = JudasSwingDetector({...})
        self.delta_calc = DeltaCalculator({...})
        self.cvd_detector = CVDDivergenceDetector({...})
        self.vwap = VWAP(anchor_type='SESSION')
        self.volume_profile = VolumeProfileBuilder({})
        self.kill_zone_mgr = KillZoneManager(config.market_type)
        self.signal_aggregator = SignalAggregator({...})
        self.risk_mgr = RiskManager({...})
        self.position_sizer = PositionSizer({...})
        self.executor = OrderExecutor({...})
        
        # State
        self.candle_stores = {}
        self.htf_bias = 'NEUTRAL'
        self.session_analysis = None
        self.is_running = False
    
    async def start(self, data_feed: DataFeed):
        """Start the trading system."""
        self.is_running = True
        self.logger.info(f"Starting Order Flow Trading System for {self.config.symbol}")
        
        for tf in [self.config.htf_timeframe, self.config.mtf_timeframe,
                   self.config.entry_timeframe, self.config.precision_timeframe]:
            self.candle_stores[tf] = CandleStore(tf, max_candles=500)
        
        await self._load_initial_state(data_feed)
        
        try:
            await self._main_loop(data_feed)
        except Exception as e:
            self.logger.error(f"System error: {e}", exc_info=True)
            await self._emergency_shutdown()
    
    async def _main_loop(self, data_feed: DataFeed):
        """Main processing loop."""
        async for event in data_feed.stream():
            if not self.is_running:
                break
            
            current_time = datetime.fromtimestamp(event.timestamp, tz=timezone.utc)
            
            if self._is_new_session(current_time):
                await self._run_pre_session_analysis(data_feed, current_time)
            
            if event.type == 'BOOK_UPDATE':
                self._process_book_update(event)
            elif event.type == 'TRADE':
                self._process_trade(event)
            elif event.type == 'BAR_CLOSE':
                await self._process_bar_close(event, data_feed, current_time)
    
    async def stop(self):
        """Gracefully stop the trading system."""
        self.is_running = False
        self.logger.info("Stopping Order Flow Trading System")
    
    async def _emergency_shutdown(self):
        """Emergency shutdown — close all positions immediately."""
        self.logger.warning("EMERGENCY SHUTDOWN initiated")
        for position in self.risk_mgr.open_positions:
            await self.executor.close_position(position, reason='EMERGENCY')
        self.is_running = False
```

---

## 8. ข้อพิจารณา Latency: Crypto เทียบกับ Forex

### 8.1 งบประมาณ Latency

```
TOTAL LATENCY BUDGET: 100ms (เป้าหมาย)
═══════════════════════════════════════

Component           │ Crypto (CEX) │ Forex (Futures) │ หมายเหตุ
────────────────────┼──────────────┼─────────────────┼──────────
Data Feed Latency   │  5-20ms      │  1-5ms          │ Exchange → System
Deserialization     │  1-2ms       │  1-2ms          │ JSON/FIX parsing
Feature Calculation │  2-5ms       │  2-5ms          │ Imbalance, delta
Signal Detection    │  3-10ms      │  3-10ms         │ Pattern matching
Aggregation         │  1-2ms       │  1-2ms          │ Score calculation
Risk Check          │  1-2ms       │  1-2ms          │ Position limits
Order Construction  │  1-2ms       │  1-2ms          │ Price, size, type
Order Submission    │  5-30ms      │  1-10ms         │ System → Exchange
────────────────────┼──────────────┼─────────────────┼──────────
TOTAL               │  20-75ms     │  12-40ms        │
────────────────────┼──────────────┼─────────────────┼──────────
FILL CONFIRMATION   │  +20-100ms   │  +5-50ms        │ Round-trip
```

### 8.2 ปัจจัย Latency เฉพาะ Crypto

| ปัจจัย | ผลกระทบ | วิธีบรรเทา |
|--------|--------|-----------|
| WebSocket reconnection | ช่วงมืด 1-5 วินาที | การเชื่อมต่อซ้ำซ้อน |
| Rate limits (Binance: 1200/min) | การ throttle คำขอ | Batch updates, smart polling |
| Latency ข้าม exchange | 50-200ms ระหว่าง exchange | Co-locate กับ exchange หลัก |
| API overload ตอนผันผวน | ความเสื่อม 100-5000ms | Queue management, retry logic |

### 8.3 ปัจจัย Latency เฉพาะ Forex

| ปัจจัย | ผลกระทบ | วิธีบรรเทา |
|--------|--------|-----------|
| Last look (LP rejection) | ล่าช้า 200-2000ms หรือปฏิเสธ | ใช้ venue ไม่มี last-look |
| ECN bridge latency | 5-50ms | Direct market access (DMA) |
| Requotes | คำสั่งถูกปฏิเสธ ต้องส่งใหม่ | ใช้ market orders หรือ aggressive limits |
| Slippage ระหว่างข่าว | 5-50+ pips | หลีกเลี่ยงเทรด 15 นาทีรอบข่าว |
| Weekend gap | ออกสถานะไม่ได้ | ลด exposure ศุกร์บ่าย |

---

## 9. สถาปัตยกรรมระบบ

### 9.1 แผนภาพส่วนประกอบ

```
┌─────────────────────────────────────────────────────────────────┐
│                        INFRASTRUCTURE                             │
│                                                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │   Redis       │  │  TimescaleDB  │  │   Kafka       │       │
│  │  (State/Cache)│  │  (Historical) │  │  (Streaming)  │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
└─────────────────────────────────────────────────────────────────┘
        │                     │                    │
        ▼                     ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                             │
│                                                                 │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │  Data Ingestion │  │  Trading Engine   │  │  Monitoring   │  │
│  │  Service        │  │  (เอกสารนี้)      │  │  Service      │  │
│  │                 │  │                   │  │               │  │
│  │  • WS Clients  │  │  • Signal Gen     │  │  • Metrics    │  │
│  │  • Normalizers  │  │  • Aggregation    │  │  • Alerts     │  │
│  │  • Publishers   │  │  • Risk Mgmt     │  │  • Dashboard  │  │
│  │                 │  │  • Execution      │  │               │  │
│  └────────┬────────┘  └────────┬─────────┘  └───────┬───────┘  │
│           │                    │                     │           │
│           ▼                    ▼                     ▼           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              EXCHANGE CONNECTIVITY LAYER                     ││
│  │  • REST API Clients (order management)                      ││
│  │  • WebSocket Clients (market data)                          ││
│  │  • FIX Protocol (สำหรับ institutional forex)                ││
│  │  • Rate Limiting & Connection Management                    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 แบบจำลอง Deployment

| แบบจำลอง | กรณีใช้งาน | โครงสร้างพื้นฐาน | ต้นทุน |
|-------|----------|---------------|------|
| **Single Process** | พัฒนา, paper trading | เครื่องภายใน | ฟรี |
| **Docker Compose** | Live trading ขนาดเล็ก | VPS เดี่ยว | $20-100/เดือน |
| **Kubernetes** | หลาย symbol, หลาย exchange | Cloud cluster | $200-1000/เดือน |
| **Co-located** | ไวต่อ latency (HFT) | Data center ของ exchange | $1000+/เดือน |

---

## 10. กรอบ Backtesting

### 10.1 ข้อพิจารณา Backtesting สำคัญ

| ข้อพิจารณา | ความสำคัญ | การนำไปใช้ |
|---------------|-----------|----------------|
| **Slippage ที่สมจริง** | สำคัญมาก | จำลองจาก spread ประวัติ + ปริมาณ |
| **Partial fills** | สำคัญ | จำลองตามสภาพคล่องที่มี |
| **Look-ahead bias** | สำคัญมาก | ตรวจสอบไม่มีข้อมูลอนาคตรั่วเข้าสัญญาณ |
| **Survivorship bias** | ปานกลาง | รวมคู่/โทเคนที่ถูก delist |
| **Regime changes** | สำคัญ | ทดสอบข้ามหลายสภาพตลาด |
| **Transaction costs** | สำคัญ | รวม spread + commission + swap |
| **Order book replay** | เหมาะสม | Replay ข้อมูล L2 สำหรับสัญญาณ book-based |

---

## 11. การติดตามและการแจ้งเตือน

### 11.1 ตัวชี้วัดการติดตามเวลาจริง

| ตัวชี้วัด | ความถี่อัปเดต | เกณฑ์แจ้งเตือน |
|--------|-----------------|----------------|
| System latency (P99) | ต่อเหตุการณ์ | >100ms |
| สถานะ data feed | 1 วินาที | ขาดการเชื่อมต่อ >5 วินาที |
| P&L เปิด | เวลาจริง | > -3% equity |
| P&L รายวัน | ต่อเทรด | > -4% equity |
| Spread | เวลาจริง | > 3 เท่าค่าเฉลี่ย |
| อัตราสร้างสัญญาณ | 1 นาที | < 1 ต่อชั่วโมง หรือ > 100 ต่อชั่วโมง |
| อัตรา fill | ต่อคำสั่ง | < 80% |
| การใช้ CPU/Memory | 10 วินาที | > 80% |

### 11.2 ระดับการแจ้งเตือน

| ระดับ | เงื่อนไข | การดำเนินการ |
|-------|-----------|--------|
| **INFO** | สร้างสัญญาณใหม่, เปิดสถานะ | บันทึก |
| **WARNING** | Spread กว้างขึ้น, ใกล้ขีดจำกัดรายวัน | ลด exposure |
| **CRITICAL** | Data feed หาย, ถึงขีดจำกัดรายวัน | หยุดเทรด |
| **EMERGENCY** | ระบบ error, exchange ล่ม | ปิดสถานะทั้งหมด |

---

## 12. ตัวชี้วัดประสิทธิภาพ

### 12.1 เป้าหมายประสิทธิภาพที่คาดหวัง

| ตัวชี้วัด | เป้าหมายอนุรักษ์นิยม | เป้าหมาย Optimistic |
|--------|-------------------|-------------------|
| ผลตอบแทนรายปี | 15-25% | 30-50% |
| Max Drawdown | < 15% | < 10% |
| Sharpe Ratio | > 1.5 | > 2.5 |
| Win Rate | > 50% | > 60% |
| R:R เฉลี่ย | > 2.0 | > 3.0 |
| Profit Factor | > 1.5 | > 2.5 |
| เทรดต่อเดือน | 20-40 | 15-30 |
| เวลาถือเฉลี่ย | 2-8 ชั่วโมง | 1-6 ชั่วโมง |

### 12.2 การระบุที่มาของประสิทธิภาพ (Performance Attribution)

ติดตามประสิทธิภาพตาม:
- ประเภทสัญญาณ (สัญญาณไหนให้ผลตอบแทนดีที่สุด?)
- Kill zone (session ไหนทำงานดีที่สุด?)
- สภาพตลาด (เทรนด์ vs sideways)
- วันในสัปดาห์
- สอดคล้อง/สวนอคติ HTF
- ช่วงคะแนน confluence

---

## 13. โหมดล้มเหลวและการกู้คืน

### 13.1 สถานการณ์ล้มเหลว

| ความล้มเหลว | การตรวจจับ | การกู้คืน |
|---------|-----------|----------|
| Data feed ขาดการเชื่อมต่อ | Heartbeat timeout | เชื่อมต่อใหม่, gap-fill, แจ้งเตือน |
| Exchange API error | HTTP error code | Retry แบบ backoff, failover |
| Fill ไม่ถูกต้อง | สถานะไม่ตรง | ปรับกับ exchange, แก้ไข |
| ระบบ crash | Process monitor | Restart, โหลดสถานะจาก DB |
| กลยุทธ์เสื่อมประสิทธิภาพ | เกณฑ์ drawdown | ลดขนาด, หยุด, ทบทวน |
| Flash crash | ราคาเคลื่อนสุดขีด | ออกฉุกเฉิน, รอเสถียร |

### 13.2 Protocol การกู้คืน

```python
async def recovery_protocol(system, failure_type: str):
    """Standard recovery protocol for system failures."""
    
    if failure_type == 'DATA_FEED_LOSS':
        # 1. จดเวลาข้อมูลที่ valid ล่าสุด
        # 2. พยายามเชื่อมต่อใหม่ (3 ครั้ง, exponential backoff)
        # 3. ถ้าเชื่อมต่อได้: gap-fill ข้อมูลที่พลาด, คำนวณสถานะใหม่
        # 4. ถ้าไม่ได้: เปลี่ยนไป secondary feed หรือหยุดเทรด
        pass
    
    elif failure_type == 'EXCHANGE_ERROR':
        # 1. บันทึกรายละเอียด error
        # 2. ตรวจสอบว่าสถานะได้รับผลกระทบหรือไม่
        # 3. ปรับสถานะกับ exchange
        # 4. ดำเนินต่อหรือ escalate
        pass
    
    elif failure_type == 'SYSTEM_CRASH':
        # 1. โหลดสถานะล่าสุดจาก database
        # 2. ปรับสถานะกับ exchange
        # 3. ตรวจสัญญาณ/ออกที่พลาด
        # 4. ดำเนินต่อในโหมดความเสี่ยงลด (50% ขนาด)
        pass
    
    elif failure_type == 'STRATEGY_DEGRADATION':
        # 1. คำนวณตัวชี้วัดประสิทธิภาพล่าสุด
        # 2. ถ้า drawdown > เกณฑ์: ลดขนาดสถานะ 50%
        # 3. ถ้ายังคง: หยุดเพื่อทบทวน
        # 4. วิเคราะห์สัญญาณไหนที่ทำงานต่ำกว่า
        # 5. พิจารณาปรับพารามิเตอร์
        pass
```

---

## 14. การตั้งค่า Deployment

### 14.1 ตัวแปร Environment

```yaml
# config/production.yaml
system:
  name: "OrderFlowTrader"
  mode: "LIVE"  # LIVE, PAPER, BACKTEST
  
market:
  symbol: "EUR/USD"
  type: "FOREX"
  exchange: "CME"

data:
  l2_feed: "cme_mdp3"
  trade_feed: "cme_mdp3"
  tick_data: true
  snapshot_interval_ms: 100

strategy:
  htf_timeframe: "1D"
  entry_timeframe: "1H"
  precision_timeframe: "15M"
  min_confluence: 0.55
  min_risk_reward: 2.0
  kill_zone_only: true

risk:
  risk_per_trade: 0.01
  max_daily_loss: 0.04
  max_weekly_loss: 0.08
  max_positions: 3
  max_correlated: 2

execution:
  order_type: "LIMIT"
  max_slippage_pips: 2.0
  timeout_seconds: 300
  
monitoring:
  log_level: "INFO"
  metrics_port: 9090
  alert_webhook: "${ALERT_WEBHOOK_URL}"
```

### 14.2 การตั้งค่าหลาย Symbol

```yaml
# config/multi_symbol.yaml
symbols:
  - name: "EUR/USD"
    type: "FOREX"
    risk_allocation: 0.30
    preferred_kill_zones: ["LONDON", "NEW_YORK"]
    
  - name: "GBP/USD"
    type: "FOREX"
    risk_allocation: 0.20
    preferred_kill_zones: ["LONDON"]
    
  - name: "BTC/USDT"
    type: "CRYPTO"
    risk_allocation: 0.25
    preferred_kill_zones: ["US_OPEN", "EUROPE_OPEN"]
    
  - name: "ETH/USDT"
    type: "CRYPTO"
    risk_allocation: 0.25
    preferred_kill_zones: ["US_OPEN", "EUROPE_OPEN"]

correlation_groups:
  - ["EUR/USD", "GBP/USD"]
  - ["BTC/USDT", "ETH/USDT"]
```

---

## 15. เอกสารอ้างอิง

### การออกแบบระบบและสถาปัตยกรรม

1. **Cartea, A., Jaimungal, S., & Penalva, J.** (2015). *Algorithmic and High-Frequency Trading*. Cambridge University Press. — การออกแบบระบบครบถ้วนสำหรับเทรด
2. **Lopez de Prado, M. M.** (2018). *Advances in Financial Machine Learning*. Wiley. — การประมวลผลสัญญาณ, วิธี backtesting, การกำหนดขนาดสถานะ
3. **Chan, E. P.** (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. — การนำ algorithmic trading ไปใช้จริง
4. **Narang, R. K.** (2013). *Inside the Black Box*. Wiley.

### Order Flow และโครงสร้างจุลภาคตลาด

5. **O'Hara, M.** (1995). *Market Microstructure Theory*. Blackwell. — พื้นฐานทฤษฎี
6. **Hasbrouck, J.** (2007). *Empirical Market Microstructure*. Oxford University Press. — วิธีการวัด
7. **Cont, R., Stoikov, S., & Talreja, R.** (2010). "A Stochastic Model for Order Book Dynamics." *Operations Research*.
8. **Easley, D., Lopez de Prado, M. M., & O'Hara, M.** (2012). "Flow Toxicity and Liquidity in a High-Frequency World." *RFS*.

### การจัดการความเสี่ยง

9. **Tharp, V. K.** (2006). *Trade Your Way to Financial Freedom*. McGraw-Hill. — การกำหนดขนาดสถานะและ expectancy
10. **Vince, R.** (1992). *The Mathematics of Money Management*. Wiley. — Kelly criterion และ optimal f

### โครงสร้างพื้นฐาน

11. **Apache Kafka Documentation** — สถาปัตยกรรมข้อมูล streaming
12. **TimescaleDB Documentation** — การจัดเก็บ time-series สำหรับข้อมูลการเงิน
13. **Redis Documentation** — การจัดการสถานะ in-memory
14. **Binance API Documentation** — WebSocket และ REST API สำหรับ crypto
15. **CME Group** — "CME Globex MDP 3.0" — ข้อกำหนดข้อมูลตลาด FX futures

### วิธีการ ICT

16. **ICT (Inner Circle Trader)** — วิธีการครบถ้วนรวมถึง kill zones, แบบจำลอง AMD, แนวคิดสภาพคล่อง, Judas swing, และจังหวะเวลา order flow ของสถาบัน

---

## ภาคผนวก A: ข้อมูลอ้างอิงด่วน — ประเภทสัญญาณและพารามิเตอร์

| ประเภทสัญญาณ | ความแข็งแรงขั้นต่ำ | น้ำหนักเริ่มต้น | R:R ขั้นต่ำ | Win Rate ทั่วไป |
|------------|-------------|---------------|---------|-----------------|
| STOP_HUNT | 0.6 | 0.20 | 2.5:1 | 60-65% |
| CVD_DIVERGENCE | 0.5 | 0.18 | 2.0:1 | 55-62% |
| JUDAS_SWING | 0.6 | 0.15 | 3.0:1 | 58-65% |
| FVG_ENTRY | 0.5 | 0.12 | 2.0:1 | 55-60% |
| DELTA_EXHAUSTION | 0.7 | 0.10 | 2.0:1 | 55-60% |
| BOOK_IMBALANCE | 0.4 | 0.08 | 1.5:1 | 52-57% |
| ABSORPTION | 0.6 | 0.07 | 2.0:1 | 55-60% |
| VWAP_EXTREME | 0.5 | 0.05 | 1.5:1 | 55-60% |
| POC_TEST | 0.5 | 0.05 | 1.5:1 | 52-58% |

## ภาคผนวก B: ข้อมูลอ้างอิงด่วน Kill Zone

| โซน | UTC เริ่ม | UTC สิ้นสุด | ระดับวัน | ตัวคูณสถานะ |
|------|-----------|---------|------------|---------------|
| London | 02:00 | 05:00 | อ.-พฤ. ดีที่สุด | 1.5x |
| NY | 07:00 | 10:00 | อ.-พฤ. ดีที่สุด | 1.3x |
| London Close | 10:00 | 12:00 | ทุกวัน | 1.0x |
| Asian | 00:00 | 04:00 | ทุกวัน | 0.7x |
| Off-Hours | — | — | — | 0.0x (ไม่เทรด) |

---

> **เอกสารก่อนหน้า**: [04_volume_delta_analysis.md](./04_volume_delta_analysis.md) — Volume Delta, CVD, VWAP, Volume Profile
> **โมดูลเสร็จสมบูรณ์**: นี่คือจุดสิ้นสุดของโมดูล Order Flow และสภาพคล่อง (Module 03) ของฐานความรู้กลยุทธ์การเทรด
