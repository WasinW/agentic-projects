# การเทรดความผันผวน: กรอบการทำงานครบถ้วน

> **แกนที่ 2 — ผลิตภัณฑ์ทางการเงิน | โมดูล 03: อนุพันธ์และผลิตภัณฑ์ที่มีโครงสร้าง**
> **เอกสาร 04 — การเทรดความผันผวน (Volatility Trading)**
> **เวอร์ชัน:** 2.0
> **อัปเดตล่าสุด:** 2026-04-12
> **ผู้เขียน:** ทีมวิจัยการเงินอาวุโส
> **การจัดประเภท:** ฐานความรู้หลัก — ระบบเทรด AI แบบ Multi-Agent

---

## สารบัญ

1. [ตรรกะหลัก](#1-ตรรกะหลัก)
2. [ข้อกำหนดทางเทคนิค](#2-ข้อกำหนดทางเทคนิค)
3. [แบบจำลองทางคณิตศาสตร์](#3-แบบจำลองทางคณิตศาสตร์)
4. [พารามิเตอร์ความเสี่ยง](#4-พารามิเตอร์ความเสี่ยง)
5. [ขั้นตอนการดำเนินการ](#5-ขั้นตอนการดำเนินการ)
6. [เอกสารอ้างอิง](#6-เอกสารอ้างอิง)

---

## 1. ตรรกะหลัก

### 1.1 Implied vs Realized Volatility

#### 1.1.1 ความผันผวนที่เกิดขึ้นจริง (Realized Volatility)

**ตัวประมาณค่า Close-to-Close (มาตรฐาน):**

$$\sigma_{CC} = \sqrt{\frac{252}{n-1} \sum_{i=1}^{n} (r_i - \bar{r})^2}$$

**ตัวประมาณค่า Garman-Klass:**

$$\sigma_{GK} = \sqrt{\frac{365}{n} \sum_{i=1}^{n} \left[\frac{1}{2}(\ln H_i - \ln L_i)^2 - (2\ln 2 - 1)(\ln C_i - \ln O_i)^2\right]}$$

**ตัวประมาณค่า Yang-Zhang:**

$$\sigma_{YZ}^2 = \sigma_O^2 + k\sigma_C^2 + (1-k)\sigma_{RS}^2$$

#### 1.1.2 ความผันผวนโดยนัย (Implied Volatility)

IV คือฉันทามติของตลาดเกี่ยวกับความคาดหวังของความผันผวนในอนาคต สกัดจากราคาออปชัน

**IV ในตลาดคริปโต:**
- BTC ATM IV: ปกติ 50-80% (สงบ), 80-120% (ผันผวน), 120-200% (วิกฤต)
- ETH ATM IV: ปกติ 60-100% (สงบ), 100-150% (ผันผวน)
- เปรียบเทียบ: SPX ปกติ 12-25%, EUR/USD ปกติ 6-12%

#### 1.1.3 Volatility Risk Premium (VRP)

$$VRP = IV - RV_{subsequent}$$

VRP แสดงผลตอบแทนส่วนเกินที่ได้จากผู้ขายความผันผวน โดยเฉลี่ย IV สูงกว่า RV ที่เกิดขึ้นจริงในภายหลัง

**ข้อค้นพบเชิงประจักษ์:**
- หุ้น (SPX): IV สูงกว่า RV ประมาณ 85% ของเวลา; VRP เฉลี่ย ≈ 3-5 Vol Points
- คริปโต (BTC): IV สูงกว่า RV ประมาณ 70-75% ของเวลา; VRP เฉลี่ย ≈ 5-15 Vol Points

**VRP เป็นสัญญาณการเทรด:**
- VRP สูง (IV >> RV): ขายออปชันน่าสนใจ (พรีเมียมแพง)
- VRP ต่ำ/ลบ (IV ≤ RV): ขายออปชันอันตราย; พิจารณาซื้อ

### 1.2 การสร้างแบบจำลอง Volatility Surface

#### 1.2.1 Volatility Surface

Volatility Surface $\sigma(K, T)$ อธิบาย IV เป็นฟังก์ชันของราคาใช้สิทธิ์ $K$ และเวลาจนหมดอายุ $T$

**มิติ:**
- **มิติ Strike (Moneyness)**: Smile/Skew
- **มิติเวลา (Term Structure)**: แบน ขาขึ้น กลับหัว หรือโค้ง

#### 1.2.2 Volatility Smile และ Skew

**เมตริก Skew:**

$$\text{25Δ Risk Reversal} = \sigma_{25\Delta Call} - \sigma_{25\Delta Put}$$

$$\text{25Δ Butterfly} = \frac{\sigma_{25\Delta Call} + \sigma_{25\Delta Put}}{2} - \sigma_{ATM}$$

### 1.3 แบบจำลอง SABR

**Dynamics ของ SABR:**

$$dF = \alpha F^\beta dW_1$$

$$d\alpha = \nu \alpha dW_2$$

$$\text{Corr}(dW_1, dW_2) = \rho$$

**การตีความพารามิเตอร์ SABR:**
- $\alpha$: ระดับความผันผวนโดยรวม
- $\beta$: ควบคุม Backbone (ค่า ATM Vol เปลี่ยนอย่างไรกับ Spot)
- $\nu$: ควบคุมความโค้ง Smile (ν สูง = Smile ชัดเจนขึ้น)
- $\rho$: ควบคุม Skew (ρ ลบ = Put Skew, ρ บวก = Call Skew)

### 1.4 DVOL — VIX เทียบเท่าสำหรับคริปโต

**ดัชนีความผันผวน Deribit (DVOL):**

$$DVOL = 100 \times \sqrt{\frac{2}{T}\sum_i \frac{\Delta K_i}{K_i^2} e^{rT} Q(K_i) - \frac{1}{T}\left(\frac{F}{K_0} - 1\right)^2}$$

**การตีความ DVOL:**
- DVOL 50 → ความผันผวน 30 วันรายปีที่คาดไว้คือ 50%
- การเคลื่อนไหวรายเดือนที่คาด: $DVOL / \sqrt{12}$ ≈ DVOL × 0.289

**DVOL เป็นสัญญาณการเทรด:**

| ระดับ DVOL | เปอร์เซ็นไทล์ | การดำเนินการ |
|---|---|---|
| < 45 | < 10th | ซื้อ Vol อย่างแข็งแกร่ง (Straddles, Strangles) |
| 45-55 | 10-25th | ซื้อ Vol (Calendars, Ratio Spreads) |
| 55-75 | 25-75th | เป็นกลาง (แนวทางสมดุล) |
| 75-90 | 75-90th | ขาย Vol (Iron Condors, Covered Calls) |
| > 90 | > 90th | ขาย Vol อย่างก้าวร้าว (แต่ต้องกำหนดความเสี่ยง) |

### 1.5 Variance Swaps

**Payoff:**

$$\text{Payoff} = N_{var} \times (\sigma_{realized}^2 - K_{var})$$

### 1.6 การเก็บเกี่ยว Volatility Risk Premium

**สัญญาณ VRP:**

$$VRP_{signal} = \frac{IV_{30d,ATM} - RV_{30d,realized}}{IV_{30d,ATM}}$$

- $VRP_{signal} > 0.15$: ขายพรีเมียมอย่างก้าวร้าว
- $VRP_{signal} \in [0.05, 0.15]$: ขายพรีเมียมปานกลาง
- $VRP_{signal} < -0.05$: ซื้อพรีเมียม (Realized > Implied)

### 1.7 Gamma Scalping

#### 1.7.1 กลยุทธ์ Long Gamma

**การแยกส่วน P&L:**

$$\text{P\&L}_{daily} = \frac{1}{2}\Gamma S^2 \left(\frac{\Delta S}{S}\right)^2 - |\Theta|$$

$$\text{P\&L}_{daily} = \frac{1}{2}\Gamma S^2 (\sigma_{realized}^2 - \sigma_{implied}^2) \times dt$$

**ทำกำไรเมื่อ:** $\sigma_{realized} > \sigma_{implied}$

#### 1.7.4 แถบ Rebalancing ที่เหมาะสม

**Whalley-Wilmott Approximation:**

$$\Delta_{band} = \left(\frac{3c\Gamma}{2\lambda}\right)^{1/3}$$

### 1.8 Dispersion Trading

**แนวคิดหลัก:** Vol ของ Index < ค่าเฉลี่ยถ่วงน้ำหนักของ Vol ขององค์ประกอบ (เนื่องจากการกระจายตัว/สหสัมพันธ์)

$$\sigma_{index}^2 \approx \sum_i w_i^2 \sigma_i^2 + 2\sum_{i<j} w_i w_j \rho_{ij} \sigma_i \sigma_j$$

---

## 2. ข้อกำหนดทางเทคนิค

### 2.1 ท่อส่งข้อมูลความผันผวน

```
VOLATILITY_DATA_PIPELINE:

  stage_1_iv_extraction:
    method: Newton-Raphson with Jaeckel initial guess
    frequency: every new quote

  stage_2_surface_construction:
    method: SVI or SABR parameterization
    frequency: every 1 second

  stage_3_rv_calculation:
    methods: [close_to_close, garman_klass, yang_zhang, parkinson]
    windows: [5d, 7d, 14d, 21d, 30d, 60d, 90d]
    frequency: every 5 minutes

  stage_4_derived_metrics:
    iv_rank, iv_percentile, vrp, skew_25d, butterfly_25d, term_structure_slope
    frequency: every 10 seconds

  stage_5_signal_generation:
    vol_regime: [low, normal, high, extreme]
    vrp_signal: [buy_vol, neutral, sell_vol, aggressive_sell]
    frequency: every 1 minute
```

---

## 3. แบบจำลองทางคณิตศาสตร์

### 3.1 SVI Parameterization

$$w(k) = a + b\left(\rho(k-m) + \sqrt{(k-m)^2 + \sigma^2}\right)$$

### 3.2 แบบจำลอง SABR — กรอบสมบูรณ์

**ATM Implied Volatility:**

$$\sigma_{ATM} \approx \frac{\alpha}{F^{1-\beta}}\left[1 + \left(\frac{(1-\beta)^2\alpha^2}{24F^{2-2\beta}} + \frac{\rho\beta\nu\alpha}{4F^{1-\beta}} + \frac{2-3\rho^2}{24}\nu^2\right)T\right]$$

### 3.3 แบบจำลอง Heston

$$dS_t = rS_t dt + \sqrt{v_t}S_t dW_t^S$$
$$dv_t = \kappa(\theta - v_t)dt + \xi\sqrt{v_t}dW_t^v$$
$$\text{Corr}(dW^S, dW^v) = \rho$$

### 3.5 คณิตศาสตร์ Gamma Scalping

**ความสัมพันธ์ Theta-Gamma:**

$$\text{Daily P\&L} = \Theta_{daily} + \frac{1}{2}\Gamma S^2 \left(\frac{\Delta S}{S}\right)^2$$

**Break-Even Realized Volatility:**

$$\text{Break-even daily move} = S \times \frac{\sigma_I}{\sqrt{365}}$$

### 3.6 Variance Swap Replication

$$K_{var} \approx \frac{2e^{rT}}{T}\sum_i \frac{\Delta K_i}{K_i^2}Q(K_i)$$

---

## 4. พารามิเตอร์ความเสี่ยง

```
VOL_TRADING_RISK_LIMITS:

  vega_limits:
    max_portfolio_vega: 1.5% of NAV per vol point
    max_long_vega: 2% of NAV per vol point
    max_short_vega: 1% of NAV per vol point

  gamma_limits:
    max_long_gamma: 3% of NAV per 1% spot move (squared)
    max_short_gamma: 1.5% of NAV per 1% spot move
    min_DTE_for_short_gamma: 14 days

  gamma_scalping_limits:
    max_daily_hedge_transactions: 50
    max_daily_hedge_cost: 0.1% of NAV
    min_realized_vs_implied_edge: 5 vol points
    mandatory_close_at_DTE: 7
```

---

## 5. ขั้นตอนการดำเนินการ

### 5.1 บอทเทรดความผันผวน — อัลกอริทึมดำเนินการสมบูรณ์

```
VOLATILITY_TRADING_BOT:

  STEP 1: VOLATILITY REGIME IDENTIFICATION (every 5 min)
    1.5 Classify regime:
      REGIME_A: Low IV + Low RV → "Calm" → BUY VOL
      REGIME_B: High IV + Low RV → "Rich Premium" → SELL VOL
      REGIME_C: Low IV + High RV → "Cheap Vol" → BUY VOL
      REGIME_D: High IV + High RV → "Crisis" → CAUTION

  STEP 2: STRATEGY SELECTION
    REGIME_A: → Long straddle/strangle, Calendar spread
    REGIME_B: → Short straddle/strangle, Iron condor, VRP harvesting
    REGIME_C: → Long gamma scalping (rare but very profitable)
    REGIME_D: → CAUTION: Do not sell vol, wait for regime change

  STEP 3: POSITION CONSTRUCTION
  STEP 4: RISK VERIFICATION
  STEP 5: EXECUTION
  STEP 6: ACTIVE MANAGEMENT
  STEP 7: EXIT & POST-TRADE
```

---

## 6. เอกสารอ้างอิง

1. **Hagan, P.S., et al.** (2002). "Managing Smile Risk." *Wilmott Magazine*.
2. **Gatheral, J.** (2006). *The Volatility Surface: A Practitioner's Guide*. Wiley.
3. **Sinclair, E.** (2013). *Volatility Trading* (2nd Edition). Wiley.
4. **Carr, P., & Madan, D.** (1998). "Towards a Theory of Volatility Trading."
5. **Deribit DVOL** — https://www.deribit.com/kb/dvol

---

> **หมายเหตุสำหรับ AI Agents:** เอกสารนี้ครอบคลุมกรอบการเทรดความผันผวน
> ลำดับความสำคัญการดำเนินงานหลัก:
> 1. จัดประเภท Vol Regime เสมอก่อนเทรด (ใช้ IV Rank + เปรียบเทียบ RV)
> 2. การเก็บเกี่ยว VRP เป็นกลยุทธ์ Vol ที่มี Sharpe สูงสุดแต่มี Tail Risk
> 3. Gamma Scalping ต้องจัดการค่าธรรมเนียมอย่างแม่นยำ
> 4. ห้ามขาย Vol ใน REGIME_D (วิกฤต) — รอการเปลี่ยน Regime
> 5. DVOL (VIX เทียบเท่าของคริปโต) เป็นสัญญาณระดับ Vol หลัก
> 6. สถานะ Short Gamma ต้องมี Defined Risk หรือ Stop เข้มงวดเสมอ
