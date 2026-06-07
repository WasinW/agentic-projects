# กรอบการจัดการความเสี่ยงพอร์ตการลงทุน

> **แกนที่ 2 — ผลิตภัณฑ์ทางการเงิน | โมดูล 03: อนุพันธ์และผลิตภัณฑ์ที่มีโครงสร้าง**
> **เอกสาร 05 — กรอบการจัดการความเสี่ยงพอร์ตการลงทุน (Portfolio Risk Management Framework)**
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

### 1.1 ปรัชญาการจัดการความเสี่ยง

กรอบการจัดการความเสี่ยงทำหน้าที่เป็นผู้ดูแลประตูสูงสุดสำหรับการตัดสินใจเทรดทั้งหมดในระบบเทรด AI แบบ Multi-Agent ไม่มีสถานะใดถูกเปิด ปรับ หรือปิดโดยไม่ผ่านกรอบนี้

**หลักการหลัก:**
1. **รักษาเงินทุนก่อน (Capital Preservation First)**: การอยู่รอดสำคัญที่สุด ระบบที่สูญเสียเงินทุนทั้งหมดไม่สามารถฟื้นตัวได้
2. **การจัดสรรงบประมาณความเสี่ยง (Risk Budgeting)**: ทุกกลยุทธ์มีการจัดสรรความเสี่ยงที่กำหนด; ความเสี่ยงรวมถูกจำกัด
3. **ตระหนักรู้ Tail Risk**: VaR แบบดั้งเดิมประเมินเหตุการณ์หางต่ำเกินไป; ใช้ CVaR และ Stress Tests
4. **การปรับตัวแบบ Dynamic**: ขีดจำกัดความเสี่ยงปรับตามสภาวะตลาด (เข้มงวดขึ้นในช่วงผันผวน)
5. **การตรวจสอบความเป็นอิสระ**: สหสัมพันธ์พังในวิกฤต; อย่าสมมติว่าการกระจายตัวคงอยู่
6. **ความโปร่งใส**: เมตริกความเสี่ยงทั้งหมดสังเกตได้ บันทึกได้ และตรวจสอบได้แบบเรียลไทม์

### 1.2 Value at Risk (VaR)

#### 1.2.1 ภาพรวม

Value at Risk ประมาณการขาดทุนสูงสุดที่คาดไว้ในช่วงเวลาที่กำหนด ณ ระดับความเชื่อมั่นที่กำหนด

$$P(Loss > VaR_\alpha) = 1 - \alpha$$

#### 1.2.2 Historical VaR

ใช้ผลตอบแทนย้อนหลังจริงเพื่อกำหนดเกณฑ์การขาดทุน

$$VaR_{hist, \alpha} = -\text{Percentile}(R_{portfolio}, 1-\alpha)$$

#### 1.2.3 Parametric VaR

$$VaR_\alpha = z_\alpha \times \sigma_P$$

**พอร์ตหลายสินทรัพย์:**

$$\sigma_P^2 = \mathbf{w}^T \Sigma \mathbf{w}$$

**Cornish-Fisher VaR (ปรับสำหรับ Skewness และ Kurtosis):**

$$VaR_{CF} = -\left(\mu + \sigma\left(z + \frac{(z^2-1)S}{6} + \frac{(z^3-3z)K}{24} - \frac{(2z^3-5z)S^2}{36}\right)\right)$$

#### 1.2.4 Monte Carlo VaR

```
FOR i = 1 to N_simulations:
    Z = random_normal(n_assets)
    Z_corr = Cholesky(Σ) × Z
    
    FOR each asset j:
        ΔS_j = S_j × (μ_j×dt + σ_j×√dt×Z_corr_j)
        ΔS_j += S_j × J_j × Poisson(λ×dt)  # jumps
    
    portfolio_value_i = Σ(position_k × price_k(new_S, new_σ))
    pnl_i = portfolio_value_i - portfolio_value_current

VaR_α = -Percentile(pnl, 1-α)
```

### 1.3 Expected Shortfall (CVaR)

$$ES_\alpha = CVaR_\alpha = -E[R | R \leq -VaR_\alpha]$$

$$CVaR_\alpha = -\frac{1}{\lfloor(1-\alpha)n\rfloor}\sum_{i=1}^{\lfloor(1-\alpha)n\rfloor} r_{(i)}$$

**ข้อดีเหนือ VaR:**

| คุณสมบัติ | VaR | CVaR |
|---|---|---|
| Sub-additivity | ไม่ (อาจละเมิด) | ใช่ (เสมอ) |
| ข้อมูลหาง | ไม่มี (แค่ Quantile) | ค่าเฉลี่ยของหาง |
| Coherent Risk Measure | ไม่ | ใช่ |
| เป็นมิตรกับ Optimization | ไม่ Convex | Convex |

### 1.4 การกำหนดขนาดสถานะ (Position Sizing)

#### 1.4.1 Kelly Criterion

$$f^* = \frac{bp - q}{b}$$

**Kelly แบบต่อเนื่อง:**

$$f^* = \frac{\mu - r_f}{\sigma^2}$$

**Kelly สำหรับพอร์ตหลายสินทรัพย์:**

$$\mathbf{f}^* = \Sigma^{-1}(\boldsymbol{\mu} - r_f \mathbf{1})$$

#### 1.4.2 Fractional Kelly

$$f_{actual} = \alpha \times f^* \quad \text{where } \alpha \in [0.1, 0.5]$$

| ประเภทกลยุทธ์ | สัดส่วน Kelly | เหตุผล |
|---|---|---|
| Arb ความเชื่อมั่นสูง | 0.50 | Edge แข็งแกร่ง Variance ต่ำ |
| ออปชัน Edge ปานกลาง | 0.25-0.33 | Edge สมเหตุสมผล Fat Tails |
| เทรดตามทิศทาง | 0.20-0.25 | ความไม่แน่นอนสูงกว่า |
| เก็งกำไร/สำรวจ | 0.10-0.15 | ความเชื่อมั่นในการประมาณ Edge ต่ำ |

#### 1.4.3 การกำหนดขนาดปรับตามความผันผวน

$$\text{Position Size} = \frac{\text{Target Volatility} \times \text{Account Equity}}{\text{Asset Volatility} \times \text{Price}}$$

### 1.5 การจัดการ Maximum Drawdown

#### 1.5.1 นิยาม Drawdown

$$MDD = \min_t \left(\frac{P_t}{\max_{s \leq t} P_s} - 1\right)$$

#### 1.5.2 การควบคุมตาม Drawdown

```
DRAWDOWN_CONTROLS:

  LEVEL_1 (Yellow): Drawdown reaches 5%
    action: Reduce new position sizes by 25%, tighten stop-losses

  LEVEL_2 (Orange): Drawdown reaches 10%
    action: Reduce new position sizes by 50%, no new speculative trades

  LEVEL_3 (Red): Drawdown reaches 15%
    action: Halt all new position opening, reduce exposure by 50%

  LEVEL_4 (Black): Drawdown reaches 25%
    action: FULL SYSTEM HALT, close all positions except long-term holds
    Minimum 48-hour cooling period
```

### 1.6 ความเสี่ยงสหสัมพันธ์ (Correlation Risk)

สินทรัพย์คริปโตแสดง:
- **สหสัมพันธ์สูงในช่วง Stress**: คริปโตทั้งหมดตกพร้อมกันเมื่อ Crash
- **สหสัมพันธ์แปรผันในช่วงสงบ**: Altcoins อาจแยกจาก BTC ในช่วง "Alt Season"
- **ขึ้นอยู่กับ Regime**: โครงสร้างสหสัมพันธ์เปลี่ยนแปลงอย่างมากระหว่างขาขึ้น/ขาลง/วิกฤต

**EWMA Correlation:**

$$\hat{\sigma}_{ij,t} = \lambda \hat{\sigma}_{ij,t-1} + (1-\lambda) r_{i,t} r_{j,t}$$

### 1.7 Beta ของพอร์ตและการ Hedge

$$\beta_i = \frac{Cov(r_i, r_{BTC})}{Var(r_{BTC})}$$

**การ Hedge Beta:**

$$\text{Hedge Notional} = (\beta_P - \beta_{target}) \times \text{Portfolio Value}$$

### 1.8 Stress Testing

**สถานการณ์ประวัติศาสตร์:**

| สถานการณ์ | BTC | ETH | Altcoins | คำอธิบาย |
|---|---|---|---|---|
| COVID มี.ค. 2020 | -50% | -60% | -70% | Flash Crash ฟื้นเร็ว |
| จีนแบน พ.ค. 2021 | -53% | -60% | -75% | ขาลงหลายสัปดาห์ |
| FTX พ.ย. 2022 | -25% | -30% | -50% | ตลาดล่มสลาย |
| Luna/UST พ.ค. 2022 | -35% | -45% | -60% ถึง -100% | Stablecoin ล่มสลาย |

### 1.9 การจัดสรรงบประมาณความเสี่ยง

```
RISK_BUDGET_ALLOCATION:

  total_risk_budget: 100%

  strategy_allocations:
    basis_trading: 25% (expected Sharpe: 2.0-3.0)
    options_selling (VRP): 20% (expected Sharpe: 1.0-2.0)
    funding_rate_arbitrage: 20% (expected Sharpe: 2.0-4.0)
    directional_momentum: 15% (expected Sharpe: 0.8-1.5)
    gamma_scalping: 10% (expected Sharpe: 1.0-2.0)
    structured_products: 10% (expected Sharpe: 1.5-2.5)
```

---

## 2. ข้อกำหนดทางเทคนิค

### 2.1 สถาปัตยกรรมเอนจิ้นความเสี่ยง

```
┌────────────────────────────────────────────────────────────────┐
│                    RISK MANAGEMENT ENGINE                        │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  DATA LAYER                                               │   │
│  │  - Real-time positions (all exchanges, all instruments)   │   │
│  │  - Market data (prices, vol surfaces, funding rates)      │   │
│  │  - Historical returns (all assets, all timeframes)        │   │
│  │  - Correlation matrices (rolling, regime-specific)        │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│  ┌──────────────────────▼───────────────────────────────────┐   │
│  │  RISK CALCULATION LAYER                                   │   │
│  │  VaR/CVaR | Greeks | Margin Monitor | Stress Tester       │   │
│  │  Position Sizing | Corr Monitor | Drawdown | Liquidity    │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│  ┌──────────────────────▼───────────────────────────────────┐   │
│  │  DECISION LAYER                                           │   │
│  │  - Pre-trade risk check (approve/reject new orders)       │   │
│  │  - Continuous position monitoring (every 100ms)           │   │
│  │  - Breach detection and alerting                          │   │
│  │  - Automatic risk reduction (rule-based)                  │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│  ┌──────────────────────▼───────────────────────────────────┐   │
│  │  ACTION LAYER                                             │   │
│  │  - Risk alerts (tiered: info, warning, critical, halt)    │   │
│  │  - Automatic position reduction orders                    │   │
│  │  - System halt trigger                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
```

### 2.4 ข้อกำหนดด้านประสิทธิภาพ

```
RISK_ENGINE_PERFORMANCE:

  latency:
    pre_trade_check: <20ms
    position_valuation: <50ms (full portfolio)
    greeks_calculation: <10ms per position
    var_parametric: <100ms
    alert_generation: <100ms from breach detection

  reliability:
    uptime: 99.999% (risk engine must always be running)
    failover: <2 seconds (hot standby)
```

---

## 3. แบบจำลองทางคณิตศาสตร์

### 3.1 VaR — สูตรสมบูรณ์

**Parametric VaR (Student-t สำหรับคริปโต):**

$$VaR_\alpha^{t} = t_{\alpha,\nu}^{-1} \times \hat{\sigma} \times \sqrt{\frac{\nu-2}{\nu}} \times V_P$$

ค่า $\nu$ ทั่วไปสำหรับคริปโต: 3-5 (หางหนา)

### 3.2 Portfolio VaR หลายสินทรัพย์

**Component VaR:**

$$CVaR_i = w_i \times \beta_i^P \times VaR_P$$

**Marginal VaR:**

$$MVaR_i = z_\alpha \times \frac{(\Sigma\mathbf{w})_i}{\sigma_P}$$

### 3.3 Kelly Criterion — สูตรขยาย

**อัตราการเติบโตภายใต้ Kelly:**

$$g = r_f + \frac{1}{2}(\boldsymbol{\mu} - r_f)^T \Sigma^{-1}(\boldsymbol{\mu} - r_f)$$

### 3.5 GARCH Volatility Forecasting

**GARCH(1,1):**

$$\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$

**พารามิเตอร์ทั่วไปสำหรับ BTC:**
- $\alpha \approx 0.05-0.10$ (ผลกระทบจาก Shock)
- $\beta \approx 0.85-0.92$ (Persistence)
- Long-run Daily Vol: 2.5-3.5%

### 3.6 แบบจำลอง Copula สำหรับ Tail Dependence

**Clayton Copula (Lower Tail Dependence):**

$$C(u_1, u_2; \theta) = (u_1^{-\theta} + u_2^{-\theta} - 1)^{-1/\theta}$$

สำหรับคริปโต: ใช้ Clayton Copula สำหรับการสร้างแบบจำลอง Crash (Tail Dependence ข้างล่างสูง)

### 3.7 Sharpe Ratio และเมตริกผลการดำเนินงาน

**Sharpe Ratio:**

$$SR = \frac{E[R_P] - R_f}{\sigma_P}$$

**Sortino Ratio:**

$$Sortino = \frac{R_P - R_f}{\sigma_{downside}}$$

**Omega Ratio:**

$$\Omega(\theta) = \frac{\int_\theta^\infty (1 - F(r))dr}{\int_{-\infty}^\theta F(r)dr}$$

---

## 4. พารามิเตอร์ความเสี่ยง

### 4.1 การกำหนดค่าความเสี่ยงหลัก

```
MASTER_RISK_CONFIG:

  portfolio_level:
    max_total_var_95_1day: 5% of NAV
    max_total_cvar_95_1day: 8% of NAV
    max_daily_loss: 3% of NAV (hard stop)
    max_weekly_loss: 7% of NAV
    max_monthly_loss: 15% of NAV
    max_drawdown: 25% from peak (system halt)
    max_leverage_effective: 5x
    min_cash_reserve: 20% of NAV

  per_position_limits:
    max_single_position_var: 2% of NAV
    max_single_position_loss: 2% of NAV
    max_position_concentration: 20% of NAV

  greeks_limits:
    max_portfolio_delta: ±30% of NAV
    max_portfolio_gamma: ±3% of NAV per 1% spot move
    max_portfolio_vega: ±1.5% of NAV per vol point
    max_portfolio_theta: ±0.5% of NAV per day

  exchange_limits:
    max_single_exchange: 40% of NAV
    max_defi_exposure: 15% of NAV
    min_exchange_diversification: 3 exchanges
```

### 4.2 กฎการปรับความเสี่ยงแบบ Dynamic

```
DYNAMIC_RISK_ADJUSTMENT:

  volatility_regime_scaling:
    low_vol (DVOL < 50): position_size_multiplier: 1.2
    normal_vol (50 ≤ DVOL < 80): position_size_multiplier: 1.0
    high_vol (80 ≤ DVOL < 110): position_size_multiplier: 0.7
    extreme_vol (DVOL ≥ 110): position_size_multiplier: 0.4

  correlation_regime_scaling:
    IF avg_pairwise_correlation > 0.85:
      action: Treat portfolio as single concentrated position
      note: "Diversification is not working — size for worst case"
```

---

## 5. ขั้นตอนการดำเนินการ

### 5.1 ระบบจัดการความเสี่ยง — อัลกอริทึมสมบูรณ์

```
RISK_MANAGEMENT_SYSTEM_FLOW:

  EVERY 100ms:
    ├── Update all position mark-to-market values
    ├── Recalculate portfolio delta
    ├── Check liquidation distances
    ├── Check margin utilization
    └── IF any critical threshold breached → ALERT

  EVERY 1 second:
    ├── Full position reconciliation
    ├── Greeks recalculation
    ├── Drawdown level check
    └── Effective leverage calculation

  EVERY 5 minutes:
    ├── Parametric VaR recalculation
    ├── CVaR update
    ├── Correlation matrix update (EWMA)
    └── Dynamic regime assessment

  EVERY 24 hours:
    ├── Full Monte Carlo VaR (100K paths)
    ├── GARCH volatility forecast update
    ├── Comprehensive risk report
    └── Backtest risk model accuracy
```

### 5.2 ขั้นตอน Pre-Trade Risk Check

```
PRE_TRADE_FLOW:

  STEP 1: BASIC VALIDATION (<1ms)
  STEP 2: POSITION SIZING CHECK (<5ms)
  STEP 3: PORTFOLIO IMPACT CHECK (<10ms)
  STEP 4: MARGIN AND LIQUIDATION CHECK (<5ms)
  STEP 5: REGIME AND DRAWDOWN CHECK (<2ms)
  STEP 6: FINAL APPROVAL (<1ms)

  TOTAL LATENCY: <20ms
```

### 5.3 ขั้นตอนตอบสนองเมื่อเกินขีดจำกัด

```
BREACH_RESPONSE:

  TIER 1: WARNING (80% of limit)
    Response time: Within 1 minute
    Actions: Tighten sizing, flag positions

  TIER 2: BREACH (100% of limit)
    Response time: Within 30 seconds
    Actions: HALT new positions, begin reducing

  TIER 3: CRITICAL BREACH (150% of limit)
    Response time: IMMEDIATE (< 5 seconds)
    Actions: HALT ALL orders, MARKET ORDER close of highest-risk

  TIER 4: SYSTEM HALT (max drawdown or catastrophic)
    Response time: IMMEDIATE
    Actions: FULL SYSTEM HALT, close ALL positions
    Minimum 48-hour cooling period
```

### 5.4 อัลกอริทึมการกำหนดขนาดสถานะ

```
POSITION_SIZING_ALGORITHM:

  STEP 1: Calculate Raw Kelly Size
  STEP 2: Calculate Fixed Fractional Size
  STEP 3: Calculate Vol-Adjusted Size
  STEP 4: Calculate VaR-Constrained Size
  STEP 5: Apply Regime Scaling
  STEP 6: Select Final Size = min(all methods)
  STEP 7: Final Validation

  OUTPUT: final_size, risk_per_trade, leverage_implied
```

---

## 6. เอกสารอ้างอิง

### วรรณกรรมวิชาการ

1. **Markowitz, H.** (1952). "Portfolio Selection." *Journal of Finance*.
2. **Kelly, J.L.** (1956). "A New Interpretation of Information Rate." *Bell System Technical Journal*.
3. **Artzner, P., et al.** (1999). "Coherent Measures of Risk." *Mathematical Finance*.
4. **Rockafellar, R.T., & Uryasev, S.** (2000). "Optimization of Conditional Value-at-Risk." *Journal of Risk*.
5. **Bollerslev, T.** (1986). "Generalized Autoregressive Conditional Heteroskedasticity." *Journal of Econometrics*.

### ตำราเรียน

6. **Hull, J.C.** (2018). *Risk Management and Financial Institutions* (5th Edition). Wiley.
7. **Jorion, P.** (2006). *Value at Risk* (3rd Edition). McGraw-Hill.
8. **McNeil, A.J., Frey, R., & Embrechts, P.** (2015). *Quantitative Risk Management*. Princeton University Press.

### แหล่งข้อมูลเฉพาะคริปโต

9. **CoinGlass** — ข้อมูล Liquidation, Open Interest, Funding Rates แบบเรียลไทม์
10. **Glassnode** — เมตริกความเสี่ยง On-chain, Exchange Flows
11. **Deribit Insights** — เมตริกความเสี่ยงจากออปชัน (DVOL, Skew Analysis)

---

> **หมายเหตุสำหรับ AI Agents:** เอกสารนี้คือกรอบความเสี่ยงหลักสำหรับระบบเทรดทั้งหมด
> กลยุทธ์และเครื่องมือทั้งหมดต้องปฏิบัติตามกรอบนี้
>
> กฎการดำเนินงานสำคัญ:
> 1. PRE-TRADE RISK CHECK บังคับ — ไม่มีคำสั่งใดข้ามได้
> 2. POSITION SIZING ใช้ค่าต่ำสุดของ Kelly, Fixed-Fractional, Vol-Adjusted และ VaR-Constrained
> 3. DRAWDOWN CONTROLS เป็นค่าสัมบูรณ์ — ระบบหยุดที่ 25% Drawdown
> 4. DYNAMIC ADJUSTMENT ปรับขีดจำกัดตาม Regime ความผันผวนและ Drawdown
> 5. CORRELATION RISK ต้องเฝ้าดู — การกระจายตัวล้มเหลวในวิกฤต
> 6. TAIL RISK (CVaR) สำคัญกว่า VaR สำหรับคริปโต
> 7. STRESS TESTS ต้องผ่านก่อนกลยุทธ์ใหม่เริ่มใช้งาน
> 8. ขั้นตอนฉุกเฉินต้องดำเนินการภายใน 60 วินาที
> 9. HUMAN OVERRIDE พร้อมเสมอสำหรับการตัดสินใจสำคัญ
> 10. ทุกการตัดสินใจความเสี่ยงถูกบันทึกเพื่อตรวจสอบและปรับปรุง
