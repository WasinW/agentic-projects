# การวิเคราะห์ Volume Delta และ Cumulative Delta — CVD, Volume Profile, VWAP

> **แกน 1 — กลยุทธ์การเทรด | โมดูล 03 — Order Flow และสภาพคล่อง (Liquidity)**
> เอกสาร: 04_volume_delta_analysis.md
> เวอร์ชัน: 2.0 | อัปเดตล่าสุด: 2026-04-12
> การจัดประเภท: ฐานความรู้หลัก — ระบบเทรด AI แบบหลายเอเจนต์ (Multi-Agent AI Trading System)

---

## สารบัญ

1. [บทนำ](#1-introduction)
2. [การคำนวณและการตีความ Volume Delta](#2-volume-delta-calculation-and-interpretation)
3. [Divergence ของ Cumulative Volume Delta (CVD)](#3-cumulative-volume-delta-cvd-divergences)
4. [Point of Control (POC)](#4-point-of-control-poc)
5. [Value Area High/Low (VAH/VAL)](#5-value-area-highlow-vahval)
6. [Volume-Weighted Average Price (VWAP) และ Bands](#6-volume-weighted-average-price-vwap-and-bands)
7. [สูตรทางคณิตศาสตร์](#7-mathematical-formulas)
8. [สัญญาณการเทรดจาก Volume Delta](#8-trading-signals-from-volume-delta)
9. [การบูรณาการกับ Price Action](#9-integration-with-price-action)
10. [ลอจิกหลัก — จุดเข้า/ออก](#10-core-logic--entryexit)
11. [ข้อกำหนดทางเทคนิค](#11-technical-specifications)
12. [พารามิเตอร์ความเสี่ยง](#12-risk-parameters)
13. [ขั้นตอนการทำงาน — Pseudocode](#13-execution-flow--pseudocode)
14. [เอกสารอ้างอิง](#14-references)

---

## 1. บทนำ

### 1.1 Volume Delta ในฐานะตัวชี้วัด Order Flow หลัก

Volume Delta คือการวัดพื้นฐานที่สุดของ **ความรุก (aggression)** ในตลาด ในขณะที่ราคาแสดงให้เราเห็นว่าตลาดอยู่ที่ไหน delta บอกเราว่าใครรุกมากกว่า — ผู้ซื้อหรือผู้ขาย — และมากแค่ไหน

$$\Delta = V_{buy} - V_{sell}$$

โดยที่:
- $V_{buy}$ = ปริมาณเทรดที่ริเริ่มโดยผู้ซื้อ (เทรดที่ตี ask)
- $V_{sell}$ = ปริมาณเทรดที่ริเริ่มโดยผู้ขาย (เทรดที่ตี bid)

### 1.2 ทำไม Delta สำคัญกว่าปริมาณดิบ

| ตัวชี้วัด | สิ่งที่แสดง | ข้อจำกัด |
|--------|-------------|-----------|
| **ปริมาณดิบ (Raw Volume)** | กิจกรรมรวม (ความสนใจ) | ไม่แสดงทิศทาง |
| **Volume Delta** | ความรุกทิศทางสุทธิ | ต้องการการจำแนกเทรด |
| **Cumulative Delta** | แรงกดทิศทางต่อเนื่องตามเวลา | อาจ diverge จากราคา |
| **Delta ต่อราคา** | ตำแหน่งที่ความรุกเกิดขึ้น | ต้องการข้อมูล tick |

### 1.3 ข้อกำหนดข้อมูล

| ประเภทข้อมูล | ขั้นต่ำสำหรับ Delta | เหมาะสม |
|-----------|-------------------|-------|
| **ข้อมูล Tick** | จำเป็นสำหรับ delta ที่แม่นยำ | ทุกเทรดพร้อม aggressor flag |
| **แท่งรวม (Aggregated Bars)** | ประมาณได้ด้วยวิธี BVC | แม่นยำน้อยกว่า |
| **Time & Sales** | แสดงเทรดรายตัว | พร้อมการจำแนกฝั่ง |
| **Order Book** | เสริมการวิเคราะห์ delta | Full DOM สำหรับบริบท |

### 1.4 วิธีจำแนกเทรด (Trade Classification Methods)

สำหรับการคำนวณ delta ที่แม่นยำ แต่ละเทรดต้องถูกจำแนกว่าริเริ่มโดยผู้ซื้อหรือผู้ขาย:

| วิธี | ความแม่นยำ | ข้อมูลที่ต้องการ | กรณีใช้งาน |
|--------|----------|---------------|----------|
| **Exchange-provided flag** | ~99% | Direct exchange feed | Crypto (Binance, etc.) |
| **Lee-Ready Algorithm** | ~85% | ข้อมูล Quote + trade | หุ้น, Forex |
| **Tick Rule** | ~75% | ลำดับราคาเท่านั้น | สภาพแวดล้อมข้อมูลน้อย |
| **BVC (Bulk Volume Classification)** | ~70% | แท่ง OHLCV เท่านั้น | ไม่มีข้อมูล tick |

---

## 2. การคำนวณและการตีความ Volume Delta

### 2.1 Delta ต่อแท่ง (Per-Bar Delta)

สำหรับแต่ละแท่งเวลา (candle) คำนวณ:

$$\Delta_{bar} = \sum_{i \in \text{bar}} V_i \cdot \text{sign}(i)$$

โดยที่:
$$\text{sign}(i) = \begin{cases} +1 & \text{if trade } i \text{ hit the ask (buyer-initiated)} \\ -1 & \text{if trade } i \text{ hit the bid (seller-initiated)} \end{cases}$$

### 2.2 ตารางการตีความ Delta

```
┌────────────────────────────────────────────────────────────────────┐
│              ตาราง DELTA + PRICE ACTION                             │
├──────────────┬──────────────┬─────────────────────────────────────┤
│  ราคา        │  Delta       │  การตีความ                          │
├──────────────┼──────────────┼─────────────────────────────────────┤
│  ขึ้น (เขียว) │  บวก         │  ปกติ: ผู้ซื้อรุก ราคาตาม          │
│              │  (มาก)       │  เทรนด์สุขภาพดี                     │
├──────────────┼──────────────┼─────────────────────────────────────┤
│  ขึ้น (เขียว) │  ลบ          │  กระจาย: ราคาขึ้นแต่ผู้ขายรุกกว่า │
│              │              │  Smart money ขายเข้าการซื้อ เตือน    │
├──────────────┼──────────────┼─────────────────────────────────────┤
│  ลง (แดง)    │  ลบ          │  ปกติ: ผู้ขายรุก ราคาตาม            │
│              │  (มาก)       │  ขาลงสุขภาพดี                       │
├──────────────┼──────────────┼─────────────────────────────────────┤
│  ลง (แดง)    │  บวก         │  สะสม: ราคาลงแต่ผู้ซื้อรุกกว่า     │
│              │              │  Smart money ซื้อตอนลง BULLISH       │
├──────────────┼──────────────┼─────────────────────────────────────┤
│  ทรงตัว      │  บวก         │  ดูดซับ: ผู้ซื้อสะสมโดยไม่ขยับราคา │
│  (doji/เล็ก) │  (มาก)       │  แรงกด bullish สะสม                 │
├──────────────┼──────────────┼─────────────────────────────────────┤
│  ทรงตัว      │  ลบ          │  ดูดซับ: ผู้ขายกระจายโดยไม่ขยับราคา│
│  (doji/เล็ก) │  (มาก)       │  แรงกด bearish สะสม                 │
└──────────────┴──────────────┴─────────────────────────────────────┘
```

### 2.3 การจำแนกความแข็งแรงของ Delta

$$\text{Delta Strength} = \frac{|\Delta_{bar}|}{\text{Total Volume}_{bar}}$$

| ความแข็งแรง | ช่วง | ความหมาย |
|----------|-------|---------|
| **สุดขีด (Extreme)** | > 0.7 | ฝั่งหนึ่งครอบงำสมบูรณ์ (>85% vs <15%) |
| **แข็งแรง (Strong)** | 0.5 - 0.7 | เจตนาทิศทางชัดเจน |
| **ปานกลาง (Moderate)** | 0.3 - 0.5 | อคติทิศทางเล็กน้อย |
| **อ่อน (Weak)** | 0.1 - 0.3 | เกือบสมดุล ข้อมูลทิศทางน้อย |
| **เป็นกลาง (Neutral)** | < 0.1 | ไม่มีขอบได้เปรียบทิศทาง |

### 2.4 อัตราการเปลี่ยนแปลงของ Delta

การเร่งตัวของ delta ให้สัญญาณเพิ่มเติม:

$$\dot{\Delta}(t) = \Delta(t) - \Delta(t-1)$$

$$\ddot{\Delta}(t) = \dot{\Delta}(t) - \dot{\Delta}(t-1)$$

**การตีความ:**
- $\dot{\Delta}$ บวก: แรงกดซื้อเพิ่มขึ้น
- $\dot{\Delta}$ ลบ: แรงกดขายเพิ่มขึ้น
- $\ddot{\Delta}$ บวก: โมเมนตัมซื้อเร่งตัว
- $\ddot{\Delta}$ ลบ: โมเมนตัมขายเร่งตัว

### 2.5 การนำไปใช้

```python
class DeltaCalculator:
    """Calculates volume delta from raw trade data."""
    
    def __init__(self, config: dict):
        self.bar_timeframe_s = config.get('bar_timeframe_s', 3600)
        self.current_bar_delta = 0.0
        self.current_bar_buy_vol = 0.0
        self.current_bar_sell_vol = 0.0
        self.current_bar_start = None
        self.delta_history = []
        self.max_history = config.get('max_delta_history', 1000)
    
    def on_trade(self, price: float, volume: float, side: str, timestamp: float):
        """Process a single trade and update delta."""
        if self.current_bar_start is None:
            self.current_bar_start = timestamp
        
        if timestamp - self.current_bar_start >= self.bar_timeframe_s:
            self._close_bar()
            self.current_bar_start = timestamp
        
        if side == 'BUY':
            self.current_bar_buy_vol += volume
            self.current_bar_delta += volume
        elif side == 'SELL':
            self.current_bar_sell_vol += volume
            self.current_bar_delta -= volume
    
    def _close_bar(self):
        """Close the current bar and add to history."""
        total_vol = self.current_bar_buy_vol + self.current_bar_sell_vol
        
        bar_data = {
            'delta': self.current_bar_delta,
            'buy_volume': self.current_bar_buy_vol,
            'sell_volume': self.current_bar_sell_vol,
            'total_volume': total_vol,
            'delta_strength': abs(self.current_bar_delta) / total_vol if total_vol > 0 else 0,
            'timestamp': self.current_bar_start
        }
        
        self.delta_history.append(bar_data)
        if len(self.delta_history) > self.max_history:
            self.delta_history.pop(0)
        
        self.current_bar_delta = 0.0
        self.current_bar_buy_vol = 0.0
        self.current_bar_sell_vol = 0.0
    
    def get_cumulative_delta(self, lookback: int = None) -> float:
        """Get cumulative delta over lookback bars."""
        if not self.delta_history:
            return 0.0
        if lookback is None:
            return sum(bar['delta'] for bar in self.delta_history)
        recent = self.delta_history[-lookback:]
        return sum(bar['delta'] for bar in recent)
    
    def get_delta_divergence(self, prices: List[float], lookback: int = 20) -> Optional[str]:
        """Detect divergence between price and cumulative delta."""
        if len(self.delta_history) < lookback or len(prices) < lookback:
            return None
        
        recent_deltas = [bar['delta'] for bar in self.delta_history[-lookback:]]
        recent_prices = prices[-lookback:]
        
        x = np.arange(lookback)
        price_slope = np.polyfit(x, recent_prices, 1)[0]
        cvd = np.cumsum(recent_deltas)
        cvd_slope = np.polyfit(x, cvd, 1)[0]
        
        if price_slope > 0 and cvd_slope < 0:
            return 'BEARISH_DIV'
        elif price_slope < 0 and cvd_slope > 0:
            return 'BULLISH_DIV'
        
        return None
```

---

## 3. Divergence ของ Cumulative Volume Delta (CVD)

### 3.1 คำจำกัดความ CVD

$$\text{CVD}(T) = \sum_{t=1}^{T} \Delta_t = \sum_{t=1}^{T} (V_t^{buy} - V_t^{sell})$$

CVD คือผลรวมสะสมของ delta ตามเวลา แสดงความรุกสุทธิต่อเนื่องของผู้ซื้อเทียบกับผู้ขาย

### 3.2 การวิเคราะห์เทรนด์ CVD

```
CVD ขาขึ้น (Bullish สุขภาพดี):
─────────────────────────────
Price:  ╱╲  ╱╲  ╱╲  ╱╲  ╱╲
       ╱  ╲╱  ╲╱  ╲╱  ╲╱
                              → ทั้งสองทำ higher highs/lows
CVD:   ╱╲  ╱╲  ╱╲  ╱╲  ╱╲
      ╱  ╲╱  ╲╱  ╲╱  ╲╱
      
= ขาขึ้นที่ยืนยัน (CVD สนับสนุนราคา)


CVD BEARISH DIVERGENCE (เตือนกลับตัว):
──────────────────────────────────────────
Price:  ╱╲   ╱╲   ╱╲   ← Higher highs
       ╱  ╲ ╱  ╲ ╱
      ╱    ╲╱    ╲╱

CVD:   ╱╲  ╱╲
      ╱  ╲╱  ╲╱╲  ╱╲  ← Lower highs (DIVERGENCE)
                 ╲╱
                 
= เตือน: ราคาทำ high ใหม่แต่ผู้ซื้ออ่อนลง
= Smart money กำลังกระจาย (ขายเข้าขาขึ้น)
= คาดว่าจะกลับตัวลง


CVD BULLISH DIVERGENCE (โอกาสกลับตัว):
──────────────────────────────────────────────
Price: ╲    ╱╲
        ╲  ╱  ╲  ╱╲  ← Lower lows
         ╲╱    ╲╱  ╲

CVD:          ╱╲  ╱╲
      ╲  ╱╲ ╱  ╲╱  ╲  ← Higher lows (DIVERGENCE)
       ╲╱  ╲╱

= โอกาส: ราคาทำ low ใหม่แต่ผู้ขายอ่อนลง
= Smart money กำลังสะสม (ซื้อตอนลง)
= คาดว่าจะกลับตัวขึ้น
```

### 3.3 ประเภท CVD Divergence

| ประเภท Divergence | ราคา | CVD | ความหมาย | ความน่าเชื่อถือ |
|----------------|-------|-----|---------|-------------|
| **Regular Bearish** | Higher High | Lower High | ผู้ซื้ออ่อนที่ยอด | สูง |
| **Regular Bullish** | Lower Low | Higher Low | ผู้ขายอ่อนที่ก้น | สูง |
| **Hidden Bearish** | Lower High | Higher High | Setup ต่อเนื่องเทรนด์ | ปานกลาง |
| **Hidden Bullish** | Higher Low | Lower Low | Setup ต่อเนื่องเทรนด์ | ปานกลาง |
| **Exaggerated Bearish** | Equal Highs | Lower high มาก | กระจายสุดขีด | สูงมาก |
| **Exaggerated Bullish** | Equal Lows | Higher low มาก | สะสมสุดขีด | สูงมาก |

### 3.4 อัลกอริทึมตรวจจับ CVD Divergence

```python
class CVDDivergenceDetector:
    """Detects divergences between price and Cumulative Volume Delta."""
    
    def __init__(self, config: dict):
        self.min_swing_bars = config.get('min_swing_bars', 5)
        self.divergence_threshold = config.get('divergence_threshold', 0.1)
        self.lookback = config.get('divergence_lookback', 50)
    
    def detect(self, prices: List[float], cvd_values: List[float]) -> List[dict]:
        """Scan for divergences between price and CVD."""
        if len(prices) < self.lookback or len(cvd_values) < self.lookback:
            return []
        
        divergences = []
        
        price_highs = self._find_swing_highs(prices)
        price_lows = self._find_swing_lows(prices)
        cvd_highs = self._find_swing_highs(cvd_values)
        cvd_lows = self._find_swing_lows(cvd_values)
        
        # Check for BEARISH divergence (price HH, CVD LH)
        if len(price_highs) >= 2 and len(cvd_highs) >= 2:
            last_price_high = price_highs[-1]
            prev_price_high = price_highs[-2]
            
            last_cvd_high = self._find_nearest(cvd_highs, last_price_high['index'])
            prev_cvd_high = self._find_nearest(cvd_highs, prev_price_high['index'])
            
            if last_cvd_high and prev_cvd_high:
                price_higher = last_price_high['value'] > prev_price_high['value']
                cvd_lower = last_cvd_high['value'] < prev_cvd_high['value']
                
                if price_higher and cvd_lower:
                    strength = self._calc_divergence_strength(
                        last_price_high, prev_price_high,
                        last_cvd_high, prev_cvd_high
                    )
                    divergences.append({
                        'type': 'BEARISH_DIVERGENCE',
                        'price_points': [prev_price_high, last_price_high],
                        'cvd_points': [prev_cvd_high, last_cvd_high],
                        'strength': strength,
                        'bar_index': last_price_high['index'],
                        'signal': 'SELL'
                    })
        
        # Check for BULLISH divergence (price LL, CVD HL)
        if len(price_lows) >= 2 and len(cvd_lows) >= 2:
            last_price_low = price_lows[-1]
            prev_price_low = price_lows[-2]
            
            last_cvd_low = self._find_nearest(cvd_lows, last_price_low['index'])
            prev_cvd_low = self._find_nearest(cvd_lows, prev_price_low['index'])
            
            if last_cvd_low and prev_cvd_low:
                price_lower = last_price_low['value'] < prev_price_low['value']
                cvd_higher = last_cvd_low['value'] > prev_cvd_low['value']
                
                if price_lower and cvd_higher:
                    strength = self._calc_divergence_strength(
                        last_price_low, prev_price_low,
                        last_cvd_low, prev_cvd_low
                    )
                    divergences.append({
                        'type': 'BULLISH_DIVERGENCE',
                        'price_points': [prev_price_low, last_price_low],
                        'cvd_points': [prev_cvd_low, last_cvd_low],
                        'strength': strength,
                        'bar_index': last_price_low['index'],
                        'signal': 'BUY'
                    })
        
        return divergences
    
    def _find_swing_highs(self, data: List[float]) -> List[dict]:
        """Find swing highs in data series."""
        highs = []
        n = self.min_swing_bars
        for i in range(n, len(data) - n):
            is_high = all(data[i] > data[i-j] for j in range(1, n+1)) and \
                      all(data[i] > data[i+j] for j in range(1, n+1))
            if is_high:
                highs.append({'index': i, 'value': data[i]})
        return highs
    
    def _find_swing_lows(self, data: List[float]) -> List[dict]:
        """Find swing lows in data series."""
        lows = []
        n = self.min_swing_bars
        for i in range(n, len(data) - n):
            is_low = all(data[i] < data[i-j] for j in range(1, n+1)) and \
                     all(data[i] < data[i+j] for j in range(1, n+1))
            if is_low:
                lows.append({'index': i, 'value': data[i]})
        return lows
    
    def _find_nearest(self, points: List[dict], target_index: int) -> Optional[dict]:
        """Find the point nearest to target_index."""
        if not points:
            return None
        return min(points, key=lambda p: abs(p['index'] - target_index))
    
    def _calc_divergence_strength(self, p1, p2, c1, c2) -> float:
        """Calculate divergence strength based on magnitude of disagreement."""
        price_change = (p2['value'] - p1['value']) / abs(p1['value'])
        cvd_change = (c2['value'] - c1['value']) / (abs(c1['value']) + 1e-10)
        disagreement = abs(price_change - cvd_change)
        return min(disagreement * 5, 1.0)
```

### 3.5 ข้อพิจารณาการ Reset CVD

CVD สะสมต่อเนื่องไม่จำกัด ซึ่งอาจทำให้ตีความยากในช่วงเวลายาว ทางออก:

| วิธี | คำอธิบาย | เมื่อใดควรใช้ |
|--------|-------------|-------------|
| **Session Reset** | Reset CVD เป็น 0 ที่เปิดแต่ละ session | การวิเคราะห์ intraday |
| **Rolling Window** | พิจารณาเฉพาะ N แท่งล่าสุด | การวิเคราะห์ระยะกลาง |
| **Anchored CVD** | Reset ที่เหตุการณ์เฉพาะ (swing H/L) | การวิเคราะห์ตามเหตุการณ์ |
| **Normalized CVD** | หาร CVD ด้วยปริมาณสะสม | การเปรียบเทียบข้ามเครื่องมือ |

$$\text{Normalized CVD}(T) = \frac{\text{CVD}(T)}{\sum_{t=1}^{T} V_t}$$

---

## 4. Point of Control (POC)

### 4.1 คำจำกัดความ

**Point of Control (POC)** คือระดับราคาที่มีปริมาณเทรดมากที่สุดภายในช่วงเวลาที่กำหนด แทน "มูลค่าที่เป็นธรรม" ของราคาที่ผู้ซื้อและผู้ขายเห็นพ้องต้องกันมากที่สุดในช่วงนั้น

$$\text{POC} = \arg\max_{P} V(P)$$

โดยที่ $V(P)$ คือปริมาณรวมที่เทรดที่ระดับราคา $P$

### 4.2 การคำนวณ POC

```python
def calculate_poc(trades: List[Trade], tick_size: float) -> dict:
    """Calculate Point of Control from trade data."""
    volume_at_price = {}
    delta_at_price = {}
    
    for trade in trades:
        price_level = round(trade.price / tick_size) * tick_size
        
        if price_level not in volume_at_price:
            volume_at_price[price_level] = 0.0
            delta_at_price[price_level] = 0.0
        
        volume_at_price[price_level] += trade.volume
        
        if trade.side == 'BUY':
            delta_at_price[price_level] += trade.volume
        else:
            delta_at_price[price_level] -= trade.volume
    
    poc_price = max(volume_at_price, key=volume_at_price.get)
    
    return {
        'price': poc_price,
        'volume': volume_at_price[poc_price],
        'delta': delta_at_price[poc_price],
        'delta_direction': 'BUY' if delta_at_price[poc_price] > 0 else 'SELL',
        'total_volume': sum(volume_at_price.values()),
        'poc_volume_pct': volume_at_price[poc_price] / sum(volume_at_price.values())
    }
```

### 4.3 ประเภท POC และนัยยะทางการเทรด

| ประเภท POC | คำอธิบาย | นัยยะทางการเทรด |
|----------|-------------|-------------------|
| **Developing POC** | POC ของ session ปัจจุบัน (เปลี่ยนแบบ real-time) | แสดงมูลค่าเป็นธรรมที่เปลี่ยนไป |
| **Fixed POC** | POC ของ session ที่เสร็จแล้ว (สรุปแล้ว) | ระดับ S/R สำคัญ |
| **Virgin POC (VPOC)** | POC ที่ไม่เคยถูก retest โดยราคา | S/R แข็งแรงสุดขีด; แม่เหล็กของราคา |
| **Migrating POC** | POC ที่เลื่อนระหว่าง session | บ่งบอกการเปลี่ยนการควบคุม |
| **Naked POC** | เหมือน VPOC — POC ที่ยังไม่ถูกทดสอบจาก session ก่อน | เป้าหมายที่มีโอกาสสูง |

### 4.4 POC เป็นแนวรับ/แนวต้าน

```
VIRGIN POC (VPOC) เป็นแม่เหล็ก:
═══════════════════════════

Session 1:  ราคาสร้าง profile ด้วย POC ที่ 1.1050
            ราคาปิดเหนือ POC → POC เป็น "naked" ด้านล่าง

             │███████│ 1.1070 (VAH)
             │█████████████│ 1.1060
             │████████████████│ 1.1050 ← POC (VPOC)
             │█████████████│ 1.1040
             │███████│ 1.1030 (VAL)

Session 2:  ราคาเปิดที่ 1.1080 (เหนือ POC ก่อนหน้า)
            VPOC ที่ 1.1050 ทำหน้าที่เป็นแม่เหล็ก

            ราคาจะมีโอกาสย่อกลับทดสอบ 1.1050 (VPOC)
            ถ้าถูกทดสอบ: VPOC กลายเป็น tested POC (สำคัญน้อยลง)
            ถ้ายืน: แนวรับแข็งแรง → ต่อเนื่องขึ้น

กฎการเทรด: VPOCs ที่ยังไม่ fill เป็นเป้าหมายที่มีโอกาสสูง
ราคามีแนวโน้มกลับมาเยือน VPOCs ภายใน 1-3 sessions
```

### 4.5 Delta ที่ POC

Delta ที่ระดับ POC ให้อคติทิศทาง:

| POC Delta | การตีความ |
|-----------|---------------|
| บวกแข็งแรงที่ POC | ผู้ซื้อครอบงำที่มูลค่าเป็นธรรม → อคติ bullish |
| ลบแข็งแรงที่ POC | ผู้ขายครอบงำที่มูลค่าเป็นธรรม → อคติ bearish |
| เป็นกลางที่ POC | สมดุลจริง — ไม่มีอคติทิศทาง |
| POC บวก + ราคาต่ำกว่า POC | โอกาสซื้อส่วนลด |
| POC ลบ + ราคาสูงกว่า POC | โอกาสขายที่พรีเมียม |

---

## 5. Value Area High/Low (VAH/VAL)

### 5.1 คำจำกัดความ

**Value Area** คือช่วงราคาที่เปอร์เซ็นต์ที่กำหนด (โดยทั่วไป 70%) ของปริมาณรวมถูกเทรด กำหนด "โซนมูลค่าเป็นธรรม" ที่ผู้เข้าร่วมตลาดส่วนใหญ่ตกลงทำธุรกรรม

$$\text{Value Area} = \{P : \text{cumulative volume from POC includes 70% of total}\}$$

- **VAH (Value Area High)**: ขอบบนของ value area
- **VAL (Value Area Low)**: ขอบล่างของ value area

### 5.2 การเทรด Value Area

**กฎ Value Area (จากทฤษฎี Market Profile):**

| สถานการณ์ | เงื่อนไข | การดำเนินการ |
|----------|-----------|--------|
| **Trend Day Up** | ราคาเปิดเหนือ VAH อยู่เหนือ | ซื้อ pullbacks ถึง VAH |
| **Trend Day Down** | ราคาเปิดต่ำกว่า VAL อยู่ต่ำกว่า | ขาย rallies ถึง VAL |
| **Normal Day** | ราคาเปิดภายใน VA หมุนวน | ซื้อ VAL ขาย VAH (เทรด range) |
| **Failed Auction** | ราคาเปิดนอก VA ล้มเหลวที่จะต่อเนื่อง | Fade กลับเข้า VA |
| **Acceptance เหนือ** | ราคาเปิดเหนือ VAH ยืนเหนือ | VAH ก่อนหน้ากลายเป็นแนวรับ |
| **Acceptance ใต้** | ราคาเปิดต่ำกว่า VAL ยืนต่ำกว่า | VAL ก่อนหน้ากลายเป็นแนวต้าน |

### 5.3 กลยุทธ์เปิดที่ Value Area

```
กฎ 80%:
═════════

"ถ้าตลาดเปิดภายใน Value Area แล้วเคลื่อนไหวออกนอก
Value Area มีโอกาส 80% ที่จะหมุนกลับไปอีกด้านของ Value Area"

ตัวอย่าง (เปิดภายใน VA เคลื่อนเหนือ VAH):
─────────────────────────────────────────────

  VAH ─── 1.1070 ───────────────────────────────────────
                              ╱╲          เป้าหมาย: VAL
         เปิดตรงนี้ ─  ╱╲ ╱  ╲  ╱╲     (โอกาส 80%
                        ╱  ╲╱    ╲╱  ╲     ที่จะถึง VAL)
  VAL ─── 1.1030 ──────────────────────╲─────────────────
                                         ╲╱  ← ถึง VAL
                                         
  ถ้า: เปิดภายใน VA
  และ: ราคาทำลายเหนือ VAH (หรือใต้ VAL)
  และ: ราคาล้มเหลวที่จะต่อเนื่อง (ปฏิเสธ acceptance)
  แล้ว: เป้าหมาย = ฝั่งตรงข้ามของ VA (โอกาส 80%)

นี่เป็นหนึ่งใน setup ที่มีโอกาสสูงสุดในการเทรด volume profile
```

---

## 6. Volume-Weighted Average Price (VWAP) และ Bands

### 6.1 คำจำกัดความ VWAP

VWAP คือราคาเฉลี่ยที่ถ่วงน้ำหนักด้วยปริมาณ — ราคาเฉลี่ยที่แท้จริงที่ตลาดเทรดในช่วงเวลาหนึ่ง

$$\text{VWAP}(T) = \frac{\sum_{t=1}^{T} P_t \cdot V_t}{\sum_{t=1}^{T} V_t}$$

โดยที่:
- $P_t$ = Typical price ที่เวลา $t$ (หรือราคาเทรดสำหรับข้อมูล tick)
- $V_t$ = ปริมาณที่เวลา $t$
- $T$ = เวลาปัจจุบัน (สะสมจากจุดยึด)

**Typical Price สำหรับ VWAP แบบแท่ง:**
$$P_{typical} = \frac{High + Low + Close}{3}$$

### 6.2 VWAP Standard Deviation Bands

VWAP bands ใช้ส่วนเบี่ยงเบนมาตรฐานของราคา-ปริมาณเพื่อสร้างระดับแนวรับ/ต้านแบบไดนามิก:

$$\sigma_{VWAP}(T) = \sqrt{\frac{\sum_{t=1}^{T} V_t \cdot (P_t - \text{VWAP}(T))^2}{\sum_{t=1}^{T} V_t}}$$

**ระดับ Band:**
- Upper Band 1: $\text{VWAP} + 1\sigma$
- Upper Band 2: $\text{VWAP} + 2\sigma$
- Upper Band 3: $\text{VWAP} + 3\sigma$ (สุดขีด)
- Lower Band 1: $\text{VWAP} - 1\sigma$
- Lower Band 2: $\text{VWAP} - 2\sigma$
- Lower Band 3: $\text{VWAP} - 3\sigma$ (สุดขีด)

### 6.3 การนำ VWAP ไปใช้

```python
class VWAP:
    """Volume-Weighted Average Price with standard deviation bands."""
    
    def __init__(self, anchor_type='SESSION'):
        self.anchor_type = anchor_type
        self.reset()
    
    def reset(self):
        """Reset VWAP calculation (new anchor point)."""
        self.cumulative_volume = 0.0
        self.cumulative_pv = 0.0
        self.cumulative_pv_sq = 0.0
        self.vwap_value = 0.0
        self.std_dev = 0.0
        self.data_points = 0
    
    def update(self, typical_price: float, volume: float):
        """Update VWAP with new data point."""
        self.cumulative_volume += volume
        self.cumulative_pv += typical_price * volume
        self.cumulative_pv_sq += (typical_price ** 2) * volume
        self.data_points += 1
        
        if self.cumulative_volume > 0:
            self.vwap_value = self.cumulative_pv / self.cumulative_volume
            variance = (
                self.cumulative_pv_sq / self.cumulative_volume - 
                self.vwap_value ** 2
            )
            self.std_dev = np.sqrt(max(variance, 0))
    
    def get_bands(self) -> dict:
        """Get VWAP and all band levels."""
        return {
            'vwap': self.vwap_value,
            'upper_1': self.vwap_value + self.std_dev,
            'upper_2': self.vwap_value + 2 * self.std_dev,
            'upper_3': self.vwap_value + 3 * self.std_dev,
            'lower_1': self.vwap_value - self.std_dev,
            'lower_2': self.vwap_value - 2 * self.std_dev,
            'lower_3': self.vwap_value - 3 * self.std_dev,
            'std_dev': self.std_dev
        }
    
    def get_price_position(self, current_price: float) -> dict:
        """Determine where current price sits relative to VWAP bands."""
        if self.std_dev == 0:
            return {'z_score': 0, 'zone': 'AT_VWAP'}
        
        z_score = (current_price - self.vwap_value) / self.std_dev
        
        if abs(z_score) < 0.5:
            zone = 'AT_VWAP'
        elif z_score >= 0.5 and z_score < 1.5:
            zone = 'UPPER_1'
        elif z_score >= 1.5 and z_score < 2.5:
            zone = 'UPPER_2'
        elif z_score >= 2.5:
            zone = 'UPPER_3_EXTREME'
        elif z_score <= -0.5 and z_score > -1.5:
            zone = 'LOWER_1'
        elif z_score <= -1.5 and z_score > -2.5:
            zone = 'LOWER_2'
        else:
            zone = 'LOWER_3_EXTREME'
        
        return {
            'z_score': z_score,
            'zone': zone,
            'distance_from_vwap': current_price - self.vwap_value,
            'distance_pct': (current_price - self.vwap_value) / self.vwap_value * 100
        }
```

### 6.4 กลยุทธ์การเทรด VWAP

| กลยุทธ์ | เงื่อนไข | จุดเข้า | Stop | เป้าหมาย |
|----------|-----------|-------|------|--------|
| **VWAP Mean Reversion** | ราคาที่ +2σ หรือ -2σ | Fade เข้าหา VWAP | เกิน ±3σ | VWAP |
| **VWAP Trend** | ราคาอยู่เหนือ/ใต้ VWAP ต่อเนื่อง | ซื้อที่ VWAP retest (ขาขึ้น) | ต่ำกว่า VWAP -1σ | +1σ หรือ +2σ |
| **VWAP Breakout** | ราคาข้าม VWAP พร้อมปริมาณ | เทรดทิศทาง cross | อีกด้านของ VWAP | ±1σ |
| **Institutional VWAP** | คาดว่าสถาบันจะซื้อ/ขายที่ VWAP | เข้าร่วม flow ที่ VWAP | เกิน VWAP ±1σ | ตามเทรนด์ |
| **VWAP Gap Fill** | ราคา gap ห่างจาก VWAP | Fade gap เข้าหา VWAP | เกินจุดสุดขีด gap | VWAP |

### 6.5 Anchored VWAP

Anchored VWAP เริ่มจากเหตุการณ์สำคัญแทนที่จะเปิด session:

| จุดยึด | กรณีใช้งาน | การตีความ |
|-------------|----------|---------------|
| Swing High | จุดยึด bearish | ราคาเข้า SHORT เฉลี่ยตั้งแต่ high |
| Swing Low | จุดยึด bullish | ราคาเข้า LONG เฉลี่ยตั้งแต่ low |
| เหตุการณ์ข่าว | การวิเคราะห์เหตุการณ์ | ราคาเข้าเฉลี่ยตั้งแต่ข่าว |
| Earnings/Halving | จุดยึดพื้นฐาน | ต้นทุนฐานสถาบันระยะยาว |
| Volume Climax | การวิเคราะห์กลับตัว | ราคาเข้าเฉลี่ยตั้งแต่ climax |

**ข้อสรุปสำคัญ**: ถ้าราคาอยู่เหนือ anchored VWAP จาก swing low ใครก็ตามที่ซื้อตั้งแต่ low นั้นมีกำไรโดยเฉลี่ย ถ้าราคาลงต่ำกว่า พวกเขาขาดทุน — สร้างแรงขายที่อาจเกิด

---

## 7. สูตรทางคณิตศาสตร์

### 7.1 สูตร Delta แบบสมบูรณ์

**Per-Trade Delta:**
$$\delta_i = V_i \cdot \mathbb{1}_{ask}(P_i) - V_i \cdot \mathbb{1}_{bid}(P_i)$$

**Per-Bar Delta:**
$$\Delta_{bar} = \sum_{i \in bar} \delta_i$$

**Cumulative Volume Delta:**
$$\text{CVD}(T) = \sum_{t=0}^{T} \Delta_t$$

**Normalized Delta:**
$$\hat{\Delta}_t = \frac{\Delta_t}{\sqrt{V_t}} \quad \text{(variance-stabilized)}$$

**Delta Momentum:**
$$M_\Delta(t, n) = \text{CVD}(t) - \text{CVD}(t-n)$$

**Delta Rate (ต่อหน่วยเวลา):**
$$R_\Delta(t) = \frac{\Delta_t}{\Delta t_{seconds}}$$

### 7.2 สูตร Volume Profile

**Volume at Price:**
$$V(P) = \sum_{i: P_i = P} V_i$$

**Point of Control:**
$$\text{POC} = \arg\max_P V(P)$$

**Value Area (กฎ 70%):**
$$\text{VA} = \{P : \sum_{P' \in VA} V(P') \geq 0.70 \cdot \sum_{all P} V(P)\}$$

**Volume Profile Skewness:**
$$\gamma_{VP} = \frac{\sum_P V(P) \cdot (P - \text{POC})^3}{\left[\sum_P V(P) \cdot (P - \text{POC})^2\right]^{3/2}}$$

Skewness บวก = ปริมาณมากกว่าอยู่ใต้ POC (อคติ bullish)
Skewness ลบ = ปริมาณมากกว่าอยู่เหนือ POC (อคติ bearish)

### 7.3 สูตร VWAP

**Standard VWAP:**
$$\text{VWAP}(T) = \frac{\sum_{t=1}^{T} P_t \cdot V_t}{\sum_{t=1}^{T} V_t}$$

**VWAP Standard Deviation:**
$$\sigma_{VWAP} = \sqrt{\frac{\sum_{t=1}^{T} V_t \cdot (P_t - \text{VWAP})^2}{\sum_{t=1}^{T} V_t}}$$

**VWAP Z-Score:**
$$Z_{VWAP} = \frac{P_{current} - \text{VWAP}}{\sigma_{VWAP}}$$

**TWAP (Time-Weighted Average Price):**
$$\text{TWAP}(T) = \frac{1}{T} \sum_{t=1}^{T} P_t$$

**VWAP vs TWAP Divergence:**
$$\text{VT Div} = \text{VWAP} - \text{TWAP}$$

VT Div บวก: ราคาสูงกว่ามีปริมาณมากกว่า (bullish, สถาบันซื้อสูงกว่า)
VT Div ลบ: ราคาต่ำกว่ามีปริมาณมากกว่า (bearish, สถาบันขายต่ำกว่า)

### 7.4 Order Flow Imbalance Index (OFII)

ตัวชี้วัดรวมที่ผสม delta, volume profile, และ VWAP:

$$\text{OFII}(t) = w_1 \cdot \hat{\Delta}_t + w_2 \cdot \frac{P_t - \text{POC}}{\text{VAH} - \text{VAL}} + w_3 \cdot Z_{VWAP}(t)$$

โดยที่:
- $w_1 = 0.40$ (น้ำหนัก delta)
- $w_2 = 0.30$ (น้ำหนัก volume profile)
- $w_3 = 0.30$ (น้ำหนัก VWAP)

**การตีความ OFII:**
- OFII > 0.5: Order flow bullish แข็งแรง
- OFII > 1.0: Bullish สุดขีด (อาจยืดเกินไป)
- OFII < -0.5: Order flow bearish แข็งแรง
- OFII < -1.0: Bearish สุดขีด (อาจยืดเกินไป)

---

## 8. สัญญาณการเทรดจาก Volume Delta

### 8.1 แคตตาล็อกสัญญาณ

| ชื่อสัญญาณ | เงื่อนไข | ทิศทาง | ความแข็งแรง | Timeframe |
|------------|-----------|-----------|----------|-----------|
| **Delta Confirmation** | Delta และราคาสอดคล้อง | ตามเทรนด์ | ปานกลาง | ทั้งหมด |
| **Delta Divergence** | CVD diverge จากราคา | สวนเทรนด์ | สูง | 1H+ |
| **Absorption Delta** | Delta มาก, ราคาเคลื่อนน้อย | กลับตัว | สูง | 15M-4H |
| **Exhaustion Delta** | Delta สุดขีดที่จุดสุดขีด swing | กลับตัว | สูงมาก | 1H+ |
| **Delta Flip** | ความชัน CVD เปลี่ยนเครื่องหมาย | กลับตัว | ปานกลาง | 4H+ |
| **Delta Acceleration** | $\ddot{\Delta}$ สุดขีด | โมเมนตัม | ปานกลาง | 15M-1H |
| **VWAP Reclaim** | ราคาข้ามกลับเหนือ/ใต้ VWAP | เทรนด์ | ปานกลาง | Intraday |
| **POC Rejection** | ราคาทดสอบ VPOC และเด้ง | แนวรับ/ต้าน | สูง | ทั้งหมด |
| **VA Breakout** | ราคาทำลายออกจาก VA พร้อมปริมาณ | เทรนด์ | สูง | ทั้งหมด |

### 8.2 สัญญาณ Delta Exhaustion

หนึ่งในสัญญาณกลับตัวที่ทรงพลังที่สุด:

```
DELTA EXHAUSTION (Bearish):
═══════════════════════════

    Price: ───────╱╲──── High ใหม่ (แทบไม่ถึง)
               ╱╲╱  ╲
              ╱      ╲

    Delta: ████████ +800  (แท่ง -3)
           ██████   +600  (แท่ง -2)
           ███     +300   (แท่ง -1)
           █      +50     (แท่งปัจจุบัน) ← EXHAUSTION

    รูปแบบ: ราคาทำ high ใหม่แต่ delta ลดลงอย่างรุนแรง
    แต่ละแท่งมีความรุกซื้อน้อยกว่าแท่งก่อนหน้า
    
    สัญญาณ: STRONG SELL
    จุดเข้า: ใต้ low ของแท่งปัจจุบัน
    SL: เหนือ high ของแท่งปัจจุบัน
    เป้าหมาย: Swing low ก่อนหน้าหรือ POC
```

```
DELTA EXHAUSTION (Bullish):
═══════════════════════════

    Delta: ████████ -800  (แท่ง -3)
           ██████   -600  (แท่ง -2)
           ███     -300   (แท่ง -1)
           █      -50     (แท่งปัจจุบัน) ← EXHAUSTION

    Price: ╲      ╱────── Low ใหม่ (แทบไม่ถึง)
            ╲╱╲  ╱
             ╲╱╲╱

    รูปแบบ: ราคาทำ low ใหม่แต่ delta ลดลง (ขายน้อยลง)
    
    สัญญาณ: STRONG BUY
```

### 8.3 คุณภาพสัญญาณ Delta-Price Divergence

| เกรด Divergence | เกณฑ์ | Win Rate (ประวัติ) | R:R |
|-----------------|----------|----------------------|-----|
| A+ | HTF divergence (D1/W1) + Kill zone + FVG | 70-75% | 4-6:1 |
| A | MTF divergence (4H) + Kill zone | 60-65% | 3-4:1 |
| B | LTF divergence (1H) + Confluence อื่น | 55-60% | 2-3:1 |
| C | LTF divergence เท่านั้น | 50-55% | 1.5-2:1 |
| D | Divergence ระยะสั้นมาก (15M) | 45-50% | ข้าม |

---

## 9. การบูรณาการกับ Price Action

### 9.1 Delta ยืนยัน Price Patterns

| Price Pattern | Delta ยืนยัน | ความหมาย |
|--------------|-------------------|---------|
| Bullish Engulfing | Delta บวกบนแท่ง engulfing | กลับตัวจริง — สัญญาณแข็งแรง |
| Bullish Engulfing | Delta ลบบนแท่ง engulfing | อาจเป็นของปลอม — ระวัง |
| Pin Bar (hammer) | Delta บวกสุดขีดบนไส้เทียน | การซื้อจริงที่จุดต่ำ — แข็งแรง |
| Pin Bar (hammer) | Delta ต่ำ | แค่ขาดการขาย ไม่ใช่การซื้อเชิงรุก — อ่อนกว่า |
| Break of Structure (BOS) | Delta มากทิศทาง break | Break จริง — ตามไป |
| Break of Structure (BOS) | Delta ต่ำตอน break | อาจเป็น stop hunt — รอ retest |
| FVG ก่อตัว | Delta ทิศทางสุดขีดบน C2 | FVG แข็งแรง — โอกาสยืนสูง |
| FVG ก่อตัว | Delta ต่ำบน C2 | FVG อ่อน — อาจถูก fill ทั้งหมด |

### 9.2 Volume Profile + แนวคิด ICT

```
การรวม VOLUME PROFILE กับ ICT:
═══════════════════════════════════

HTF Volume Profile:              แนวคิด ICT:
─────────────────                ─────────────

 │████│ 1.1080 (HVN)  ─────── BSL (stops เหนือกลุ่มนี้)
 │██████████████│ 1.1070 (VAH)
 │████████████████████│ 1.1060 
 │██████████████████████████│ 1.1050 (POC) ── Order Block ที่ POC = แข็งแรง
 │████████████████████│ 1.1040
 │██████████████│ 1.1030 (VAL)
 │████│ 1.1020 (HVN)  ─────── SSL (stops ใต้กลุ่มนี้)
 │ │ 1.1010 (LVN)     ─────── Liquidity Void = โซน FVG
 │ │ 1.1000 (LVN)     ─────── ราคาเคลื่อนเร็วผ่าน LVN
 │████│ 1.0990 (HVN)

ข้อสรุปสำคัญ:
1. HVN (High Volume Node) = S/R แข็งแรง = ที่ที่ OBs มักก่อตัว
2. LVN (Low Volume Node) = ราคาเคลื่อนเร็วผ่าน = พื้นที่ FVG/void
3. POC สอดคล้องกับ OB = setup พรีเมียม
4. ขอบ VA สอดคล้องกับ BSL/SSL = เป้าหมายที่มีโอกาสสูง
5. VPOCs ทำหน้าที่เหมือนแม่เหล็ก (คล้าย FVGs — ราคามักกลับมา)
```

---

## 10. ลอจิกหลัก — จุดเข้า/ออก

### 10.1 กรอบการเข้า Volume Delta

| Setup | Trigger เข้า | เงื่อนไข Delta | เงื่อนไข VWAP | เงื่อนไข Profile |
|-------|-------------|----------------|---------------|-----------------|
| **Delta Divergence Long** | ราคาที่แนวรับ + Bullish CVD divergence | CVD higher low, ราคา lower low | ราคาต่ำกว่า VWAP (ส่วนลด) | ใกล้ VAL หรือ POC |
| **Delta Divergence Short** | ราคาที่แนวต้าน + Bearish CVD divergence | CVD lower high, ราคา higher high | ราคาเหนือ VWAP (พรีเมียม) | ใกล้ VAH หรือ POC |
| **VWAP Bounce Long** | ราคาแตะ VWAP จากเหนือ เด้ง | Delta บวกบนแท่งเด้ง | ราคาที่ VWAP พอดี | เหนือ POC |
| **VWAP Bounce Short** | ราคาแตะ VWAP จากใต้ ถูกปฏิเสธ | Delta ลบบนแท่งปฏิเสธ | ราคาที่ VWAP พอดี | ใต้ POC |
| **VA Breakout Long** | ราคาทำลายเหนือ VAH พร้อมปริมาณ | Delta บวกแข็งแรงตอน break | ราคาเหนือ VWAP | ผ่าน VAH |
| **VA Breakout Short** | ราคาทำลายใต้ VAL พร้อมปริมาณ | Delta ลบแข็งแรงตอน break | ราคาใต้ VWAP | ผ่าน VAL |
| **POC Magnet Long** | VPOC ใต้ราคาปัจจุบัน (ยังไม่ทดสอบ) | Delta บวกกำลังก่อตัว | N/A | VPOC คือเป้าหมาย |
| **Exhaustion Reversal** | Delta exhaustion ที่จุดสุดขีด | Delta สัมบูรณ์ลดลง | ที่ band ±2σ | ที่ขีดสุด VA |

### 10.2 กรอบการออก

| ประเภทออก | เงื่อนไข | การดำเนินการ |
|-----------|-----------|--------|
| **เป้าหมาย VPOC** | ราคาถึง naked VPOC เป้าหมาย | Take profit (ทั้งหมดหรือบางส่วน) |
| **VWAP Reversion** | ราคาถึง VWAP (ถ้าเข้าจากจุดสุดขีด) | Take profit 50% |
| **Delta Flip** | ความชัน CVD พลิกต่อต้านสถานะ | ปิดหรือเพิ่ม stop |
| **VA ฝั่งตรงข้าม** | ราคาถึงอีกด้านของ VA | Take profit |
| **Volume Climax** | ปริมาณสุดขีด + แท่งกลับตัว | ออกฉุกเฉิน |
| **ออกตามเวลา** | สิ้นสุด session (สำหรับ intraday) | ปิดสถานะ |

---

## 11. ข้อกำหนดทางเทคนิค

### 11.1 พารามิเตอร์

| พารามิเตอร์ | ค่าเริ่มต้น | ช่วง | คำอธิบาย |
|-----------|---------|-------|-------------|
| `bar_timeframe_s` | 3600 | [60, 86400] | ช่วง delta bar เป็นวินาที |
| `cvd_lookback` | 50 | [20, 200] | จำนวนแท่งสำหรับตรวจจับ CVD divergence |
| `divergence_min_swing_bars` | 5 | [3, 15] | จำนวนแท่งขั้นต่ำสำหรับตรวจจับ swing ใน CVD |
| `divergence_strength_threshold` | 0.5 | [0.3, 0.9] | ความแข็งแรง divergence ขั้นต่ำเพื่อส่งสัญญาณ |
| `vwap_anchor` | 'SESSION' | ['SESSION','WEEKLY','MONTHLY'] | ช่วง reset VWAP |
| `vwap_extreme_z` | 2.0 | [1.5, 3.0] | Z-score สำหรับสัญญาณสุดขีด |
| `va_pct` | 0.70 | [0.60, 0.80] | เปอร์เซ็นต์ปริมาณสำหรับ value area |
| `poc_tolerance_pct` | 0.1 | [0.05, 0.3] | % ความคลาดเคลื่อนสำหรับทดสอบ POC |
| `exhaustion_min_bars` | 4 | [3, 7] | จำนวนแท่งขั้นต่ำสำหรับรูปแบบ exhaustion |
| `delta_strength_threshold` | 0.3 | [0.2, 0.6] | ความแข็งแรงขั้นต่ำสำหรับสัญญาณ delta |

---

## 12. พารามิเตอร์ความเสี่ยง

### 12.1 ขนาดสถานะตามคุณภาพสัญญาณ

| คุณภาพสัญญาณ | ความเสี่ยงต่อเทรด | ตัวคูณขนาด | พื้นฐาน |
|---------------|---------------|-----------------|-------|
| A+ (Multi-TF divergence + confluence) | 2.0% | 1.5x | ความเชื่อมั่นสูงสุด |
| A (HTF divergence + หนึ่ง confluence) | 1.5% | 1.0x | มาตรฐาน |
| B (MTF signal + confluence อ่อน) | 1.0% | 0.75x | ลดลง |
| C (สัญญาณเดี่ยว ไม่มี confluence) | 0.5% | 0.5x | ขั้นต่ำ |

### 12.2 กฎ Stop Loss สำหรับกลยุทธ์ปริมาณ

| กลยุทธ์ | การวาง Stop | Stop สูงสุด (ATR) |
|----------|---------------|-------------------|
| CVD Divergence | เกิน swing ที่ก่อ divergence | 2.0 ATR |
| VWAP Mean Reversion | เกิน band ±3σ | 1.5 ATR |
| VA Breakout | กลับเข้า VA (failed breakout) | 1.0 ATR |
| POC Test | เกิน POC + buffer 0.5 ATR | 1.5 ATR |
| Delta Exhaustion | เกินจุดสุดขีด exhaustion | 1.0 ATR |

### 12.3 เป้าหมาย R:R

| กลยุทธ์ | TP1 | TP2 | TP3 |
|----------|-----|-----|-----|
| CVD Divergence | 1:1 (50% ขนาด) | 2:1 (30%) | 3:1+ (20% trail) |
| VWAP Reversion | VWAP (60%) | Band ตรงข้าม (40%) | — |
| VA Trade | POC (33%) | ขอบ VA ตรงข้าม (33%) | เกิน VA (34%) |
| Exhaustion | 1:1 (50%) | 2.5:1 (30%) | 4:1 (20% trail) |

---

## 13. ขั้นตอนการทำงาน — Pseudocode

```python
class VolumeDeltaTradingSystem:
    """Complete trading system based on volume delta, VWAP, and volume profile."""
    
    def __init__(self, config):
        self.delta_calc = DeltaCalculator(config)
        self.cvd_detector = CVDDivergenceDetector(config)
        self.vwap_mgr = MultiVWAP()
        self.profile_builder = VolumeProfileBuilder(config)
        self.signal_gen = VolumeSignalGenerator(config)
        self.risk_mgr = RiskManager(config)
        self.position_mgr = PositionManager()
        self.config = config
    
    async def run(self, data_feed):
        """Main execution loop."""
        async for event in data_feed:
            
            if event.type == 'TRADE':
                self.delta_calc.on_trade(
                    price=event.price, volume=event.volume,
                    side=event.side, timestamp=event.timestamp
                )
                self.vwap_mgr.update_all(
                    typical_price=event.price, volume=event.volume,
                    timestamp=event.timestamp
                )
                self.profile_builder.add_trade(event)
            
            elif event.type == 'BAR_CLOSE':
                candles = data_feed.get_candles(self.config['timeframe'], limit=100)
                current_price = candles[-1].close
                
                signals = self.signal_gen.generate_signals(candles, current_price)
                
                if not signals:
                    continue
                
                valid_signals = [
                    s for s in signals 
                    if s['strength'] >= self.config['min_signal_strength']
                ]
                
                if not valid_signals:
                    continue
                
                best_signal = max(valid_signals, key=lambda s: s['strength'])
                
                if not self.position_mgr.has_open_positions():
                    entry = self._generate_entry(best_signal, candles, current_price)
                    
                    if entry and entry['risk_reward'] >= self.config['min_rr']:
                        size = self.risk_mgr.calculate_size(
                            entry=entry['entry_price'],
                            stop=entry['stop_loss'],
                            signal_quality=best_signal['strength']
                        )
                        await self._execute_entry(entry, size)
                
                else:
                    for position in self.position_mgr.get_open_positions():
                        exit_signal = self._check_exit(
                            position, best_signal, candles, current_price
                        )
                        if exit_signal:
                            await self._execute_exit(position, exit_signal)
```

---

## 14. เอกสารอ้างอิง

### บทความวิชาการ

1. **Hasbrouck, J.** (2007). *Empirical Market Microstructure*. Oxford University Press. — ตำราพื้นฐานเรื่องการจำแนกเทรดและการวัดโครงสร้างจุลภาคตลาด
2. **Lee, C. M. C., & Ready, M. J.** (1991). "Inferring Trade Direction from Intraday Data." *Journal of Finance*. — อัลกอริทึม Lee-Ready สำหรับจำแนกเทรด
3. **Easley, D., Lopez de Prado, M. M., & O'Hara, M.** (2012). "Flow Toxicity and Liquidity in a High-Frequency World." *RFS*. — การจำแนกปริมาณและ VPIN
4. **Bouchaud, J. P., Farmer, J. D., & Lillo, F.** (2009). "How Markets Slowly Digest Changes in Supply and Demand." *Handbook of Financial Markets*. — ผลกระทบราคาของ order flow
5. **Cont, R., Kukanov, A., & Stoikov, S.** (2014). "The Price Impact of Order Book Events." *JFE*. — ความไม่สมดุล order flow และการทำนายราคา
6. **Kyle, A. S.** (1985). "Continuous Auctions and Insider Trading." *Econometrica*. — Lambda (สัมประสิทธิ์ผลกระทบราคา)

### ผู้ปฏิบัติและวิธีการ

8. **Dalton, J. F., Jones, E. T., & Dalton, R. B.** (1993). *Mind Over Markets*. — Market Profile: POC, Value Area, ประเภทตลาด
9. **Steidlmayer, J. P.** (1986). *Steidlmayer on Markets*. — ผู้สร้าง Market Profile ดั้งเดิม; แนวคิด TPO และการกระจายปริมาณ
10. **ICT (Inner Circle Trader)** — การวิเคราะห์ปริมาณในบริบท order flow สถาบัน, kill zones, และแนวคิด smart money
11. **Sierra Chart Documentation** — เอกสารเทคนิคละเอียดเรื่อง volume delta, cumulative delta, footprint charts
12. **Jigsaw Trading** — การศึกษาเชิงปฏิบัติเรื่อง delta, absorption, และการเทรด order flow

### ข้อมูลและการนำไปใช้

14. **Binance API Documentation** — WebSocket streams สำหรับข้อมูลเทรดพร้อมการจำแนกผู้ซื้อ/ผู้ขาย (aggressor flag)
15. **CME Group** — "CME DataMine" เอกสารสำหรับข้อมูล tick ประวัติพร้อมการจำแนกเทรด
16. **Tardis.dev** — ข้อมูลตลาด crypto ประวัติพร้อม L2 order book และข้อมูลเทรด

---

> **เอกสารก่อนหน้า**: [03_hft_stop_hunting.md](./03_hft_stop_hunting.md) — อัลกอริทึม HFT และการล่า stop ของสถาบัน
> **เอกสารถัดไป**: [05_execution_flow.md](./05_execution_flow.md) — ขั้นตอนการทำงานครบถ้วนสำหรับระบบเทรด order flow
