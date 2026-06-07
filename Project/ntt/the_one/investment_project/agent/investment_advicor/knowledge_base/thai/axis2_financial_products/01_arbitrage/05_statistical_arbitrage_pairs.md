# การเก็งกำไรเชิงสถิติและการเทรดคู่ (Statistical Arbitrage & Pairs Trading) — เอกสารกลยุทธ์ฉบับสมบูรณ์

> **เวอร์ชันเอกสาร:** 2.0
> **อัปเดตล่าสุด:** 2026-04-12
> **การจัดประเภท:** Core Knowledge Base — Axis 2: ผลิตภัณฑ์ทางการเงิน
> **ประเภทกลยุทธ์:** Statistical Arbitrage (มีความเสี่ยง, Mean-Reversion)
> **ตลาด:** Forex, Crypto (CeFi), หุ้น
> **ความถี่:** Low to Medium Frequency (ชั่วโมงถึงสัปดาห์)

---

## สารบัญ

1. [ตรรกะหลัก — ทฤษฎี Cointegration](#1-ตรรกะหลัก--ทฤษฎี-cointegration)
2. [วิธีการเลือกคู่](#2-วิธีการเลือกคู่)
3. [การคำนวณ Z-Score และสัญญาณการเทรด](#3-การคำนวณ-z-score-และสัญญาณการเทรด)
4. [Mean Reversion Half-Life](#4-mean-reversion-half-life)
5. [Kalman Filter สำหรับ Dynamic Hedge Ratio](#5-kalman-filter-สำหรับ-dynamic-hedge-ratio)
6. [เกณฑ์เข้าและออก](#6-เกณฑ์เข้าและออก)
7. [กรอบทางคณิตศาสตร์](#7-กรอบทางคณิตศาสตร์)
8. [การประยุกต์ใช้กับคู่คริปโตเคอร์เรนซี](#8-การประยุกต์ใช้กับคู่คริปโตเคอร์เรนซี)
9. [ขั้นตอนการดำเนินการฉบับสมบูรณ์](#9-ขั้นตอนการดำเนินการฉบับสมบูรณ์)
10. [พารามิเตอร์ความเสี่ยง](#10-พารามิเตอร์ความเสี่ยง)
11. [Backtesting และการวิเคราะห์ผลงาน](#11-backtesting-และการวิเคราะห์ผลงาน)
12. [เอกสารอ้างอิง](#12-เอกสารอ้างอิง)

---

## 1. ตรรกะหลัก — ทฤษฎี Cointegration

### 1.1 แนวคิดพื้นฐาน

Statistical arbitrage (stat arb) ในการเทรดคู่อิงจากการสังเกตว่าคู่สินทรัพย์บางคู่เคลื่อนไปด้วยกันเมื่อเวลาผ่านไปเนื่องจากความสัมพันธ์ทางเศรษฐกิจ เมื่อพวกมันแยกออกชั่วคราว เราเดิมพันว่าจะบรรจบกัน ต่างจาก pure arbitrage กลยุทธ์นี้มีความเสี่ยงตลาดจริง — สเปรดอาจไม่บรรจบภายในขอบเขตเวลาของเรา

### 1.2 Correlation vs. Cointegration

**ความแตกต่างสำคัญ:**

- **Correlation** วัดความสัมพันธ์เชิงเส้นระหว่างผลตอบแทน: $\rho(R_X, R_Y)$
  - สินทรัพย์สองตัวอาจมี correlation สูงแต่ไม่ cointegrated
  
- **Cointegration** วัดว่า combination เชิงเส้นของ price series สองตัวเป็น stationary หรือไม่:
  - ถ้า $X_t \sim I(1)$ และ $Y_t \sim I(1)$ (ทั้งคู่ non-stationary)
  - แต่ $Z_t = Y_t - \beta X_t \sim I(0)$ (stationary)
  - แล้ว $X$ และ $Y$ เป็น cointegrated ด้วย cointegrating vector $[1, -\beta]$

**เหตุใด cointegration สำคัญ:**
- สินทรัพย์ที่ correlate อาจ drift ออกไปไม่สิ้นสุด
- สินทรัพย์ที่ cointegrated มี **mean-reverting spread** — ต้องบรรจบในที่สุด
- สิ่งนี้ให้ edge ทางสถิติ: เราเทรดสเปรดด้วยความเสี่ยงที่วัดปริมาณได้

### 1.3 กลยุทธ์ Pairs Trading — ทีละขั้น

```
1. IDENTIFY คู่ที่ cointegrated (ทดสอบเชิงสถิติ)
2. ESTIMATE hedge ratio (ปริมาณ Y ที่เทรดต่อหน่วย X)
3. CALCULATE spread: S_t = Y_t - beta * X_t
4. NORMALIZE spread: z_t = (S_t - mean(S)) / std(S)
5. ENTER เมื่อสเปรดเบี่ยงเบนเกินเกณฑ์ (เช่น |z| > 2)
   - ถ้า z > +2: สเปรดกว้างเกิน → SHORT spread (short Y, long X)
   - ถ้า z < -2: สเปรดแคบเกิน → LONG spread (long Y, short X)
6. EXIT เมื่อสเปรดกลับสู่ mean (|z| < 0.5 หรือ z ข้ามศูนย์)
7. STOP LOSS ถ้าสเปรดแยกออกไปอีก (|z| > 4)
```

---

## 2. วิธีการเลือกคู่

### 2.1 การทดสอบ Cointegration

#### วิธี Engle-Granger สองขั้นตอน

**ขั้นตอน 1:** ประมาณ cointegrating regression:

$$Y_t = \alpha + \beta X_t + \epsilon_t$$

ผ่าน OLS regression

**ขั้นตอน 2:** ทดสอบ residuals $\hat{\epsilon}_t$ สำหรับ stationarity โดยใช้ Augmented Dickey-Fuller (ADF) test:

$$\Delta \hat{\epsilon}_t = \gamma \hat{\epsilon}_{t-1} + \sum_{i=1}^{p} \delta_i \Delta \hat{\epsilon}_{t-i} + u_t$$

**Null hypothesis:** $H_0: \gamma = 0$ (unit root, ไม่มี cointegration)
**Alternative:** $H_1: \gamma < 0$ (stationary, cointegrated)

ถ้า p-value < 0.05 → ปฏิเสธ $H_0$ → คู่เป็น cointegrated

#### Johansen Test

$$\Delta \mathbf{Y}_t = \Pi \mathbf{Y}_{t-1} + \sum_{i=1}^{p-1} \Gamma_i \Delta \mathbf{Y}_{t-i} + \mathbf{u}_t$$

### 2.2 โค้ดเลือกคู่

```python
class PairSelector:
    """Systematic pair selection for statistical arbitrage."""
    
    def __init__(self, price_data: pd.DataFrame, min_correlation: float = 0.7,
                 max_pvalue: float = 0.05, min_half_life: float = 1.0,
                 max_half_life: float = 30.0):
        self.prices = price_data
        self.min_corr = min_correlation
        self.max_pval = max_pvalue
    
    def find_pairs(self) -> List[dict]:
        assets = self.prices.columns.tolist()
        valid_pairs = []
        
        for asset_x, asset_y in combinations(assets, 2):
            # Step 1: Correlation pre-screen
            corr = self.prices[asset_x].pct_change().corr(
                self.prices[asset_y].pct_change()
            )
            if corr < self.min_corr:
                continue
            
            # Step 2: Cointegration test
            score, pvalue, _ = coint(self.prices[asset_x], self.prices[asset_y])
            if pvalue > self.max_pval:
                continue
            
            # Step 3: Calculate hedge ratio and half-life
            model = OLS(self.prices[asset_y], self.prices[asset_x]).fit()
            beta = model.params[0]
            spread = self.prices[asset_y] - beta * self.prices[asset_x]
            half_life = self.calculate_half_life(spread)
            
            valid_pairs.append({
                'x': asset_x, 'y': asset_y,
                'correlation': corr,
                'coint_pvalue': pvalue,
                'hedge_ratio': beta,
                'half_life': half_life,
            })
        
        return sorted(valid_pairs, key=lambda p: p['coint_pvalue'])
```

---

## 3. การคำนวณ Z-Score และสัญญาณการเทรด

### 3.1 การคำนวณ Spread

$$S_t = Y_t - \beta \cdot X_t$$

### 3.2 Z-Score

$$z_t = \frac{S_t - \mu_S}{\sigma_S}$$

โดยที่ $\mu_S$ และ $\sigma_S$ คำนวณจากหน้าต่างเลื่อน (rolling window)

### 3.3 สัญญาณการเทรด

- **เข้า Short Spread:** เมื่อ $z_t > +2.0$
- **เข้า Long Spread:** เมื่อ $z_t < -2.0$
- **ออก:** เมื่อ $|z_t| < 0.5$ หรือ $z_t$ ข้ามศูนย์
- **Stop Loss:** เมื่อ $|z_t| > 4.0$

---

## 4. Mean Reversion Half-Life

### 4.1 การคำนวณ

จาก Ornstein-Uhlenbeck process:

$$dS_t = \theta(\mu - S_t)dt + \sigma dW_t$$

Half-life:

$$t_{1/2} = \frac{\ln(2)}{\theta}$$

ประมาณ $\theta$ จาก regression:

$$\Delta S_t = \theta \cdot S_{t-1} + \epsilon_t$$

$$t_{1/2} = -\frac{\ln(2)}{\theta}$$

### 4.2 ช่วง Half-Life ที่ยอมรับ

- **ต่ำเกินไป (< 1 วัน):** ต้นทุนธุรกรรมกินกำไร
- **เหมาะสม (1-30 วัน):** สมดุลระหว่าง turnover และ predictability
- **สูงเกินไป (> 30 วัน):** เสี่ยงว่า relationship จะเปลี่ยน

---

## 5. Kalman Filter สำหรับ Dynamic Hedge Ratio

### 5.1 เหตุใดต้องใช้ Dynamic Hedge Ratio

Hedge ratio ($\beta$) ไม่คงที่ตลอดเวลา Kalman Filter ช่วยประมาณ $\beta$ ที่เปลี่ยนแปลงแบบเรียลไทม์

### 5.2 แบบจำลอง

**State equation:**

$$\beta_t = \beta_{t-1} + w_t, \quad w_t \sim N(0, Q)$$

**Observation equation:**

$$Y_t = \beta_t X_t + v_t, \quad v_t \sim N(0, R)$$

---

## 6. เกณฑ์เข้าและออก

| พารามิเตอร์ | ค่าทั่วไป | คำอธิบาย |
|------------|-----------|---------|
| Entry threshold | $|z| > 2.0$ | เข้าเมื่อเบี่ยงเบนมาก |
| Exit threshold | $|z| < 0.5$ | ออกเมื่อสเปรดกลับ |
| Stop loss | $|z| > 4.0$ | ตัดขาดทุนเมื่อแยกออกไปมาก |
| Lookback window | 20-60 วัน | สำหรับคำนวณ mean/std |
| Maximum holding | 30 วัน | บังคับออกหากไม่กลับ |

---

## 7. กรอบทางคณิตศาสตร์

### 7.1 Ornstein-Uhlenbeck Process

$$dS_t = \theta(\mu - S_t)dt + \sigma dW_t$$

### 7.2 Expected Profit

$$E[\text{Profit}] = (|z_{entry}| - |z_{exit}|) \times \sigma_S \times Q$$

### 7.3 Sharpe Ratio

$$SR = \frac{\mu_{return}}{\sigma_{return}} \times \sqrt{N_{trades/year}}$$

---

## 8. การประยุกต์ใช้กับคู่คริปโตเคอร์เรนซี

### 8.1 คู่ที่น่าสนใจ

| คู่ | เหตุผลทางเศรษฐกิจ | Half-Life ทั่วไป |
|-----|-------------------|:---------------:|
| BTC/ETH | เหรียญชั้นนำ, crypto beta | 5-15 วัน |
| ETH/SOL | L1 alternatives | 3-10 วัน |
| AAVE/COMP | DeFi lending sector | 5-20 วัน |
| BNB/OKB | Exchange tokens | 7-20 วัน |
| stETH/ETH | Pegged relationship | 1-5 วัน |

### 8.2 ความท้าทายเฉพาะคริปโต

- ความผันผวนสูงกว่า = stop losses ถูก hit บ่อยกว่า
- Regime changes รุนแรงกว่า
- Cointegration relationships อาจแตกสลายกะทันหัน
- ค่า funding costs สำหรับ short positions
- สภาพคล่องอาจหายไปกะทันหัน

---

## 9. ขั้นตอนการดำเนินการฉบับสมบูรณ์

```python
class PairsTrader:
    """Complete pairs trading engine."""
    
    def __init__(self, config):
        self.config = config
        self.positions = {}
        self.pair_models = {}
    
    async def run(self):
        while True:
            # 1. Update prices
            prices = await self.fetch_prices()
            
            # 2. For each monitored pair
            for pair in self.pairs:
                spread = self.calculate_spread(pair, prices)
                z_score = self.calculate_zscore(pair, spread)
                
                # 3. Check entry signals
                if pair not in self.positions:
                    if z_score > self.config.entry_threshold:
                        await self.enter_short_spread(pair)
                    elif z_score < -self.config.entry_threshold:
                        await self.enter_long_spread(pair)
                
                # 4. Check exit signals
                else:
                    if self.should_exit(pair, z_score):
                        await self.exit_position(pair)
            
            # 5. Periodic re-calibration
            if self.time_to_recalibrate():
                self.recalibrate_models()
            
            await asyncio.sleep(self.config.check_interval)
```

---

## 10. พารามิเตอร์ความเสี่ยง

| พารามิเตอร์ | ค่า |
|------------|------|
| สถานะสูงสุดต่อคู่ | 5% ของพอร์ต |
| จำนวนคู่สูงสุดพร้อมกัน | 10-20 คู่ |
| ขาดทุนสูงสุดต่อคู่ | 2% ของพอร์ต |
| Drawdown สูงสุดรวม | 10% |
| ระยะเวลาถือสูงสุด | 30 วัน |
| ความถี่ปรับเทียบใหม่ | ทุก 7 วัน |

---

## 11. Backtesting และการวิเคราะห์ผลงาน

### 11.1 เมตริกหลัก

- **Sharpe Ratio:** เป้าหมาย > 1.5
- **Maximum Drawdown:** ไม่เกิน 10%
- **Win Rate:** เป้าหมาย > 55%
- **Average holding period:** 5-15 วัน
- **Profit Factor:** > 1.5

### 11.2 ข้อผิดพลาดทั่วไปใน Backtesting

- Survivorship bias: ใช้เฉพาะเหรียญที่ยังมีอยู่
- Look-ahead bias: ใช้ข้อมูลในอนาคตในการเลือกคู่
- Overfitting: ปรับพารามิเตอร์มากเกินไปกับข้อมูลในอดีต
- ไม่รวมต้นทุนธุรกรรม: slippage, funding costs

---

## 12. เอกสารอ้างอิง

1. Engle, R. F., & Granger, C. W. J. (1987). "Co-Integration and Error Correction."
2. Gatev, E., et al. (2006). "Pairs Trading: Performance of a Relative-Value Arbitrage Rule."
3. Avellaneda, M., & Lee, J. H. (2010). "Statistical Arbitrage in the US Equities Market."
4. Johansen, S. (1991). "Estimation and Hypothesis Testing of Cointegration Vectors."
5. Vidyamurthy, G. (2004). "Pairs Trading: Quantitative Methods and Analysis."
