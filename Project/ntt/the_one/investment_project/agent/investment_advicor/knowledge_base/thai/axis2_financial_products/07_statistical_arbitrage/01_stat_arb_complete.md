# การเก็งกำไรทางสถิติ (Statistical Arbitrage) — เอกสารอ้างอิงฉบับสมบูรณ์

## ข้อมูลเอกสาร
| ฟิลด์ | ค่า |
|---|---|
| ประเภทกลยุทธ์ | การเก็งกำไรทางสถิติ / การเทรดคู่ (Statistical Arbitrage / Pairs Trading) |
| สินทรัพย์ | Forex, คริปโต (Spot & Futures) |
| กรอบเวลา | ระหว่างวันถึงหลายสัปดาห์ |
| ความซับซ้อน | สูง |
| เงินทุนที่ต้องการ | สูง (สถานะพร้อมกันหลายตัว) |
| อัปเดตล่าสุด | 2026-04-12 |

---

## สารบัญ
1. [กรอบแนวคิดการเทรดคู่](#1-กรอบแนวคิดการเทรดคู่)
2. [ทฤษฎี Cointegration](#2-ทฤษฎี-cointegration)
3. [วิธี Engle-Granger สองขั้นตอน](#3-วิธี-engle-granger-สองขั้นตอน)
4. [การทดสอบ Johansen Cointegration](#4-การทดสอบ-johansen-cointegration)
5. [การสร้างแบบจำลอง Spread และ Z-Score](#5-การสร้างแบบจำลอง-spread-และ-z-score)
6. [Kalman Filter สำหรับพารามิเตอร์ไดนามิก](#6-kalman-filter-สำหรับพารามิเตอร์ไดนามิก)
7. [การเก็งกำไรทางสถิติด้วย PCA](#7-การเก็งกำไรทางสถิติด้วย-pca)
8. [การเสริมด้วย Machine Learning](#8-การเสริมด้วย-machine-learning)
9. [ข้อควรพิจารณาในการดำเนินการ](#9-ข้อควรพิจารณาในการดำเนินการ)
10. [การสร้างแบบจำลองต้นทุนธุรกรรม](#10-การสร้างแบบจำลองต้นทุนธุรกรรม)
11. [ตรรกะหลัก — การเข้า/ออกสถานะ](#11-ตรรกะหลัก--การเข้าออกสถานะ)
12. [ข้อมูลจำเพาะทางเทคนิค](#12-ข้อมูลจำเพาะทางเทคนิค)
13. [กรอบแนวคิดทางคณิตศาสตร์](#13-กรอบแนวคิดทางคณิตศาสตร์)
14. [พารามิเตอร์ความเสี่ยง](#14-พารามิเตอร์ความเสี่ยง)
15. [ขั้นตอนการดำเนินการ](#15-ขั้นตอนการดำเนินการ)
16. [วิธีการ Backtest](#16-วิธีการ-backtest)
17. [เอกสารอ้างอิง](#17-เอกสารอ้างอิง)

---

## 1. กรอบแนวคิดการเทรดคู่

### 1.1 แนวคิดหลัก

การเก็งกำไรทางสถิติ (Stat Arb) ใช้ประโยชน์จากการกำหนดราคาผิดชั่วคราวระหว่างหลักทรัพย์ที่เกี่ยวข้อง รูปแบบที่พบมากที่สุดคือ **การเทรดคู่ (Pairs Trading)**: การระบุสินทรัพย์สองตัวที่เคลื่อนไหวไปด้วยกันในอดีตและเทรดการแยกตัวระหว่างพวกมัน โดยคาดว่าจะกลับมาบรรจบที่สมดุล

**หลักการพื้นฐาน:**

หากสินทรัพย์ $A$ และ $B$ มี Cointegration (มีความสัมพันธ์สมดุลระยะยาว) แล้ว:

$$S_t = P_{A,t} - \beta P_{B,t}$$

จะเป็นกระบวนการที่นิ่ง (Mean-Reverting) โดยที่ $\beta$ คืออัตราส่วนป้องกันความเสี่ยง (Hedge Ratio)

### 1.2 การเก็งกำไรทางสถิติ vs การเก็งกำไรบริสุทธิ์

| คุณลักษณะ | การเก็งกำไรบริสุทธิ์ (Pure Arbitrage) | การเก็งกำไรทางสถิติ (Statistical Arbitrage) |
|---|---|---|
| ความเสี่ยง | ไม่มีความเสี่ยง | มีความเสี่ยงทางสถิติ |
| แหล่งกำไร | ส่วนต่างราคา | การกลับสู่ค่าเฉลี่ยของ Spread |
| กรอบเวลา | ทันที | ชั่วโมงถึงสัปดาห์ |
| เงินทุนที่ต้องการ | สูง (รับประกันการบรรจบ) | ปานกลาง (คาดว่าจะบรรจบ) |
| โอกาสขาดทุน | ไม่มี (ทางทฤษฎี) | มี (Spread อาจแยกตัวถาวร) |
| ตัวอย่าง | Triangular FX Arb | EUR/GBP vs EUR/USD * USD/GBP |

### 1.3 การเทรดคู่ใน Forex

**คู่ Forex ตามธรรมชาติ:**

| คู่ที่ 1 | คู่ที่ 2 | ความสัมพันธ์ |
|---|---|---|
| EUR/USD | GBP/USD | สกุลเงินยุโรปที่อ้างอิง USD ทั้งคู่ |
| AUD/USD | NZD/USD | สกุลเงินสินค้าโภคภัณฑ์ เศรษฐกิจคล้ายกัน |
| EUR/CHF | EUR/GBP | ความสัมพันธ์ Cross-Rate ยุโรป |
| USD/CAD | WTI Crude Oil | สกุลเงินสินค้าโภคภัณฑ์ vs สินค้าโภคภัณฑ์ |
| USD/JPY | US 10Y Yield | ส่วนต่างอัตราดอกเบี้ย |
| EUR/USD | DXY (ผกผัน) | ความสัมพันธ์ดัชนีดอลลาร์ |

**การสร้างคู่สังเคราะห์:**

Spread ระหว่าง EUR/USD และ GBP/USD เท่ากับการเทรด EUR/GBP:

$$\text{Spread} = \text{EUR/USD} - \beta \times \text{GBP/USD} \approx f(\text{EUR/GBP})$$

### 1.4 การเทรดคู่ในคริปโต

**คู่คริปโตตามธรรมชาติ:**

| สินทรัพย์ 1 | สินทรัพย์ 2 | ความสัมพันธ์ |
|---|---|---|
| BTC | ETH | ผู้นำตลาด สหสัมพันธ์สูง |
| ETH | SOL | แพลตฟอร์ม Smart Contract L1 |
| BTC | BTC-perp | Spot-Futures Basis |
| LINK | BAND | โปรโตคอล Oracle |
| AAVE | COMP | โปรโตคอลให้สินเชื่อ DeFi |
| BTC (Exchange A) | BTC (Exchange B) | Spread ข้าม Exchange |

---

## 2. ทฤษฎี Cointegration

### 2.1 คำจำกัดความ

อนุกรมเวลาสองตัว $X_t$ และ $Y_t$ มี Cointegration ลำดับ $(d, b)$ เขียนว่า $X_t, Y_t \sim CI(d, b)$ ถ้า:
1. ทั้งสองอนุกรมเป็น Integrated ลำดับ $d$ (เช่น $I(1)$ — ไม่นิ่ง)
2. มีการรวมเชิงเส้น $Z_t = X_t - \beta Y_t$ ที่เป็น Integrated ลำดับ $d - b$ (เช่น $I(0)$ — นิ่ง)

### 2.2 Cointegration vs สหสัมพันธ์

| คุณสมบัติ | สหสัมพันธ์ (Correlation) | Cointegration |
|---|---|---|
| คำจำกัดความ | ความสัมพันธ์เชิงเส้นของผลตอบแทน | สมดุลระยะยาวของระดับราคา |
| ต้องนิ่งหรือไม่? | ใช่ (ผลตอบแทน) | ไม่ (ระดับราคาอาจไม่นิ่ง) |
| ความเสถียรตามเวลา | เปลี่ยนแปลงได้เร็ว | มีเสถียรภาพมากกว่า (เชิงโครงสร้าง) |
| หลอก? | พบได้ทั่วไปกับข้อมูลไม่นิ่ง | ความสัมพันธ์ระยะยาวที่แท้จริง |
| นัยต่อการเทรด | การป้องกัน (ระยะสั้น) | เทรดคู่ (การบรรจบระยะยาว) |
| การทดสอบ | Pearson/Spearman บนผลตอบแทน | Engle-Granger / Johansen บนระดับราคา |

**ข้อสังเกตสำคัญ**: สินทรัพย์สองตัวอาจมีสหสัมพันธ์สูงแต่ไม่มี Cointegration (อาจลอยตัวแยกกันถาวร) ในทางกลับกัน สินทรัพย์สองตัวอาจมีสหสัมพันธ์ปานกลางแต่มี Cointegration แข็งแกร่ง (กลับสู่สมดุลเสมอ)

### 2.3 เหตุผลทางเศรษฐศาสตร์สำหรับ Cointegration

| ตลาด | เหตุผล |
|---|---|
| Forex | Purchasing Power Parity, Interest Rate Parity, ความสัมพันธ์สามเหลี่ยม |
| คริปโต | ปัจจัยพื้นฐาน Token ในกลุ่มเดียวกัน, Liquidity Pool ร่วม, ปัจจัยความเสี่ยงร่วม |
| ข้ามตลาด | ความเชื่อมโยงสินค้าโภคภัณฑ์-สกุลเงิน, อัตราดอกเบี้ย-FX |

### 2.4 ลำดับของ Integration

**ขั้นตอนการทดสอบ:**
1. ทดสอบว่า $X_t$ เป็น $I(1)$: ทดสอบ ADF บน $X_t$ (ไม่ควรปฏิเสธ Unit Root)
2. ทดสอบว่า $Y_t$ เป็น $I(1)$: ทดสอบ ADF บน $Y_t$ (ไม่ควรปฏิเสธ Unit Root)
3. ถ้าทั้งคู่เป็น $I(1)$ ทดสอบว่า $Z_t = X_t - \beta Y_t$ เป็น $I(0)$: ทดสอบ ADF บน $Z_t$ (ควรปฏิเสธ Unit Root)

ถ้าขั้นตอนที่ 3 ผ่าน $X_t$ และ $Y_t$ มี Cointegration

---

## 3. วิธี Engle-Granger สองขั้นตอน

### 3.1 ขั้นตอน

**ขั้นที่ 1: ประมาณการ Cointegrating Regression**

รัน OLS Regression ของราคาหนึ่งบนอีกตัว:

$$Y_t = \alpha + \beta X_t + \epsilon_t$$

ได้ Residual:

$$\hat{\epsilon}_t = Y_t - \hat{\alpha} - \hat{\beta} X_t$$

**ขั้นที่ 2: ทดสอบ Residual ว่านิ่งหรือไม่**

ใช้ทดสอบ ADF กับ $\hat{\epsilon}_t$:

$$\Delta\hat{\epsilon}_t = \gamma \hat{\epsilon}_{t-1} + \sum_{i=1}^{p} \delta_i \Delta\hat{\epsilon}_{t-i} + u_t$$

ทดสอบ $H_0: \gamma = 0$ (Unit Root, ไม่มี Cointegration) vs $H_1: \gamma < 0$ (นิ่ง, มี Cointegration)

**ค่าวิกฤต (Engle-Granger, 2 ตัวแปร):**

| ระดับนัยสำคัญ | ค่าวิกฤต |
|---|---|
| 1% | -3.90 |
| 5% | -3.34 |
| 10% | -3.04 |

หมายเหตุ: ค่าเหล่านี้เป็นลบมากกว่าค่าวิกฤต ADF มาตรฐานเพราะ $\beta$ ถูกประมาณการ

### 3.2 การประมาณ Hedge Ratio

สัมประสิทธิ์ OLS $\hat{\beta}$ จากขั้นที่ 1 คือ Hedge Ratio:

$$\text{Spread}_t = Y_t - \hat{\beta} X_t$$

สำหรับทุก 1 หน่วยของ $Y$ ที่ถือ Long ให้ถือ $\hat{\beta}$ หน่วยของ $X$ Short (หรือกลับกัน)

### 3.3 การนำไปใช้

```python
def engle_granger_test(series_y, series_x, significance=0.05):
    """
    Engle-Granger two-step cointegration test.
    
    Returns: (is_cointegrated, hedge_ratio, residuals, adf_stat, p_value)
    """
    # Step 1: OLS regression Y = alpha + beta * X
    X = np.column_stack([np.ones(len(series_x)), series_x])
    beta_hat = np.linalg.lstsq(X, series_y, rcond=None)[0]
    alpha = beta_hat[0]
    hedge_ratio = beta_hat[1]
    
    # Compute residuals (spread)
    residuals = series_y - alpha - hedge_ratio * series_x
    
    # Step 2: ADF test on residuals
    adf_stat, p_value, _, _, critical_values, _ = adfuller(residuals, maxlag=10)
    
    is_cointegrated = p_value < significance
    
    return {
        'is_cointegrated': is_cointegrated,
        'hedge_ratio': hedge_ratio,
        'intercept': alpha,
        'residuals': residuals,
        'adf_stat': adf_stat,
        'p_value': p_value,
        'critical_values': critical_values
    }
```

### 3.4 ข้อจำกัดของ Engle-Granger

| ข้อจำกัด | คำอธิบาย | การแก้ไข |
|---|---|---|
| ลำดับตัวแปร | ผลลัพธ์ขึ้นกับว่าตัวใดเป็น Y vs X | รันทั้งสองทาง; ใช้ TLS |
| สมการเดียว | หาได้เพียง Cointegrating Vector เดียว | ใช้ Johansen สำหรับ > 2 ตัวแปร |
| Hedge Ratio คงที่ | $\beta$ ถือว่าคงที่ตลอดหน้าต่างประมาณการ | ใช้หน้าต่างเลื่อนหรือ Kalman Filter |
| อคติตัวอย่างเล็ก | ค่าประมาณ OLS อาจมีอคติในตัวอย่างเล็ก | ขั้นต่ำ 250+ การสังเกต |
| การเปลี่ยนแปลงโครงสร้าง | Cointegration อาจพังทลาย | เฝ้าดูด้วยการทดสอบแบบเลื่อน |

---

## 4. การทดสอบ Johansen Cointegration

### 4.1 กรอบแนวคิด

การทดสอบ Johansen เหมาะกว่าสำหรับระบบที่มีมากกว่าสองตัวแปร โดยจำลองระบบ VAR ในรูปแบบ Error Correction:

$$\Delta \mathbf{X}_t = \Pi \mathbf{X}_{t-1} + \sum_{i=1}^{p-1} \Gamma_i \Delta \mathbf{X}_{t-i} + \mathbf{u}_t$$

โดยที่ $\Pi = \alpha\beta'$ และ:
- $\alpha$ = เมทริกซ์ความเร็วการปรับตัว (Speed of Adjustment)
- $\beta$ = เมทริกซ์ Cointegrating Vectors
- rank($\Pi$) = จำนวน Cointegrating Relationships

### 4.2 Trace Test และ Maximum Eigenvalue Test

**Trace Test:**

$$\lambda_{trace}(r) = -T \sum_{i=r+1}^{n} \ln(1 - \hat{\lambda}_i)$$

ทดสอบ $H_0$: จำนวน Cointegrating Vectors $\leq r$ vs $H_1$: $> r$

**Maximum Eigenvalue Test:**

$$\lambda_{max}(r, r+1) = -T \ln(1 - \hat{\lambda}_{r+1})$$

ทดสอบ $H_0$: มี Cointegrating Vectors $r$ ตัวพอดี vs $H_1$: $r+1$ ตัว

### 4.3 การตีความผลลัพธ์

สำหรับ $n$ ตัวแปร:
- rank($\Pi$) = 0: ไม่มี Cointegration
- 0 < rank($\Pi$) < $n$: มี Cointegration (rank = จำนวน Cointegrating Vectors)
- rank($\Pi$) = $n$: ตัวแปรทั้งหมดนิ่ง (กรณีไม่น่าสนใจ)

### 4.4 การประยุกต์ใช้กับหลายสินทรัพย์

**ตัวอย่างตะกร้าคริปโต (BTC, ETH, SOL):**

```python
def johansen_test_crypto(btc, eth, sol, max_lag=5):
    """
    Test for cointegration among BTC, ETH, SOL.
    May reveal spread trading opportunities in L1 tokens.
    """
    data = np.column_stack([btc, eth, sol])
    
    # Johansen test
    result = coint_johansen(data, det_order=0, k_ar_diff=max_lag)
    
    # Trace statistics and critical values
    trace_stats = result.lr1      # Trace statistics
    trace_crit = result.cvt       # Critical values (90%, 95%, 99%)
    
    # Maximum eigenvalue statistics
    max_eig_stats = result.lr2
    max_eig_crit = result.cvm
    
    # Cointegrating vectors (each row is a vector)
    coint_vectors = result.evec
    
    # Number of cointegrating relationships
    n_coint = sum(trace_stats > trace_crit[:, 1])  # 95% level
    
    return {
        'n_cointegrating': n_coint,
        'vectors': coint_vectors[:n_coint],
        'trace_stats': trace_stats,
        'critical_values_95': trace_crit[:, 1]
    }
```

### 4.5 การสร้าง Spread สำหรับเทรด

ถ้าการทดสอบ Johansen พบ Cointegrating Vector $\beta = [\beta_1, \beta_2, \beta_3]$:

$$\text{Spread}_t = \beta_1 P_{BTC,t} + \beta_2 P_{ETH,t} + \beta_3 P_{SOL,t}$$

Spread นี้นิ่งและสามารถเทรดด้วย Z-Score Mean Reversion ได้

---

## 5. การสร้างแบบจำลอง Spread และ Z-Score

### 5.1 การสร้าง Spread

**Spread สองสินทรัพย์:**

$$S_t = P_{Y,t} - \beta P_{X,t} - \alpha$$

โดยที่ $(\alpha, \beta)$ ประมาณจาก Cointegrating Regression

**Spread ที่ปรับมาตรฐาน (Z-Score):**

$$z_t = \frac{S_t - \bar{S}_n}{\sigma_{S,n}}$$

โดยที่:
- $\bar{S}_n$ = ค่าเฉลี่ยเลื่อนของ Spread ใน $n$ งวด
- $\sigma_{S,n}$ = ส่วนเบี่ยงเบนมาตรฐานเลื่อนของ Spread

### 5.2 กฎเทรดด้วย Z-Score สำหรับคู่

```
LONG SPREAD (Long Y, Short X * beta):
    Entry: z_t < -entry_threshold (e.g., -2.0)
    Exit: z_t >= exit_threshold (e.g., 0.0)
    Stop: z_t < -stop_threshold (e.g., -4.0)

SHORT SPREAD (Short Y, Long X * beta):
    Entry: z_t > +entry_threshold (e.g., +2.0)
    Exit: z_t <= exit_threshold (e.g., 0.0)
    Stop: z_t > +stop_threshold (e.g., +4.0)
```

### 5.3 ครึ่งชีวิตของ Spread (Half-Life)

ประมาณครึ่งชีวิตของ Spread เพื่อกำหนดระยะเวลาถือครองที่คาดหวัง:

$$\Delta S_t = \lambda S_{t-1} + \epsilon_t$$

$$t_{half} = -\frac{\ln(2)}{\lambda}$$

**แนวทางปฏิบัติ:**
- $t_{half}$ < 5 แท่ง: การกลับตัวเร็วมาก; อาจเป็นโอกาส High-Frequency
- $t_{half}$ = 5-30 แท่ง: ดีสำหรับเทรดระหว่างวัน/Swing
- $t_{half}$ = 30-100 แท่ง: ถือครองหลายวันถึงหลายสัปดาห์
- $t_{half}$ > 100 แท่ง: ช้าเกินไป; ต้นทุนธุรกรรมอาจกัดกินข้อได้เปรียบ

### 5.4 การเฝ้าดูความนิ่งของ Spread

```
Algorithm: Rolling Cointegration Monitor

PARAMETERS:
    estimation_window = 252 bars
    test_frequency = 20 bars  # Re-test every 20 bars
    min_adf_pvalue = 0.05
    max_half_life = 60

EVERY test_frequency BARS:
    1. Re-estimate cointegrating regression on last estimation_window bars
    2. Get new beta, alpha, residuals
    3. Run ADF test on residuals
    4. Calculate half-life
    
    IF adf_pvalue > min_adf_pvalue:
        WARNING: "Cointegration may be breaking down"
        ACTION: Close existing spread positions
        STATUS: DISABLED until cointegration re-establishes
        
    IF half_life > max_half_life:
        WARNING: "Mean reversion too slow"
        ACTION: Reduce position sizes
        
    IF beta changed by > 20% from initial estimate:
        WARNING: "Hedge ratio shift detected"
        ACTION: Rebalance positions to new beta
```

---

## 6. Kalman Filter สำหรับพารามิเตอร์ไดนามิก

### 6.1 แรงจูงใจ

Hedge Ratio คงที่จาก OLS อาจไม่จับความสัมพันธ์ที่เปลี่ยนแปลงตามเวลาได้ Kalman Filter ประมาณ $\beta_t$ แบบไดนามิก ปรับตัวตามการเปลี่ยนแปลงเชิงโครงสร้าง

### 6.2 แบบจำลอง State-Space

**สมการการสังเกต (Observation Equation):**

$$Y_t = \alpha_t + \beta_t X_t + \epsilon_t, \quad \epsilon_t \sim \mathcal{N}(0, R)$$

**สมการการเปลี่ยนสถานะ (State Transition Equations):**

$$\alpha_t = \alpha_{t-1} + \eta_{\alpha,t}, \quad \eta_{\alpha,t} \sim \mathcal{N}(0, Q_\alpha)$$
$$\beta_t = \beta_{t-1} + \eta_{\beta,t}, \quad \eta_{\beta,t} \sim \mathcal{N}(0, Q_\beta)$$

เวกเตอร์สถานะ $\theta_t = [\alpha_t, \beta_t]'$ วิวัฒนาการเป็น Random Walk

### 6.3 สมการ Kalman Filter

**ขั้นตอนทำนาย (Prediction Step):**

$$\hat{\theta}_{t|t-1} = \hat{\theta}_{t-1|t-1}$$
$$P_{t|t-1} = P_{t-1|t-1} + Q$$

**ขั้นตอนอัปเดต (Update Step):**

$$K_t = P_{t|t-1} H_t' (H_t P_{t|t-1} H_t' + R)^{-1}$$
$$\hat{\theta}_{t|t} = \hat{\theta}_{t|t-1} + K_t (Y_t - H_t \hat{\theta}_{t|t-1})$$
$$P_{t|t} = (I - K_t H_t) P_{t|t-1}$$

โดยที่:
- $H_t = [1, X_t]$ (เมทริกซ์การสังเกต)
- $K_t$ = Kalman Gain
- $P_t$ = เมทริกซ์ความแปรปรวนร่วมสถานะ
- $Q$ = ความแปรปรวนร่วมของ Noise สถานะ (ควบคุมความเร็วการปรับตัว)
- $R$ = ความแปรปรวนของ Noise การสังเกต

### 6.4 การนำไปใช้

```python
class KalmanPairTrading:
    """
    Kalman Filter for dynamic hedge ratio estimation in pairs trading.
    """
    
    def __init__(self, delta=1e-4, R=1e-3):
        """
        delta: Controls state transition noise (higher = more adaptive)
        R: Observation noise variance
        """
        self.delta = delta
        self.R = R
        
        # State: [alpha, beta]
        self.theta = np.zeros(2)
        self.P = np.eye(2)  # State covariance
        self.Q = self.delta * np.eye(2)  # State noise
        
    def update(self, x, y):
        """
        Update Kalman filter with new observation.
        
        x: independent variable (price of asset X)
        y: dependent variable (price of asset Y)
        
        Returns: (alpha, beta, spread, spread_variance)
        """
        # Observation vector
        H = np.array([1.0, x])
        
        # Prediction
        theta_pred = self.theta  # Random walk: theta_t = theta_{t-1}
        P_pred = self.P + self.Q
        
        # Innovation
        y_hat = H @ theta_pred
        innovation = y - y_hat
        
        # Innovation variance
        S = H @ P_pred @ H.T + self.R
        
        # Kalman gain
        K = P_pred @ H.T / S
        
        # Update
        self.theta = theta_pred + K * innovation
        self.P = P_pred - np.outer(K, K) * S
        
        # Extract parameters
        alpha = self.theta[0]
        beta = self.theta[1]
        spread = innovation  # = y - alpha - beta * x
        spread_var = S
        
        return alpha, beta, spread, np.sqrt(spread_var)
    
    def get_zscore(self, spread, spread_std, lookback_spreads):
        """Calculate z-score of current spread."""
        if len(lookback_spreads) < 20:
            return 0.0
        mean_spread = np.mean(lookback_spreads)
        std_spread = np.std(lookback_spreads)
        if std_spread == 0:
            return 0.0
        return (spread - mean_spread) / std_spread
```

### 6.5 ข้อดีของ Kalman Filter สำหรับ Stat Arb

| ข้อดี | คำอธิบาย |
|---|---|
| การปรับตัวไดนามิก | Hedge Ratio อัปเดตอย่างต่อเนื่อง |
| ไม่ต้องกำหนดหน้าต่าง Lookback | ไม่ต้องการหน้าต่างเลื่อนคงที่ |
| วัดความไม่แน่นอน | ให้ช่วงความเชื่อมั่นบน $\beta_t$ |
| ตรวจจับการเปลี่ยนสภาวะ | Kalman Gain ที่สูงบ่งชี้ความไม่เสถียร |
| ความแปรปรวนของ Spread | ให้ค่าความแปรปรวนการทำนาย Spread โดยตรง |

### 6.6 การปรับจูน Kalman Filter

| พารามิเตอร์ | ผลของการเพิ่มค่า | ช่วงค่าทั่วไป |
|---|---|---|
| $\delta$ (State Noise) | ปรับตัวมากขึ้น $\beta_t$ มี Noise มากขึ้น | $10^{-5}$ ถึง $10^{-3}$ |
| $R$ (Observation Noise) | ตอบสนองต่อ Innovation น้อยลง | $10^{-4}$ ถึง $10^{-1}$ |

**แนวทาง:**
- สำหรับคู่เสถียร (EUR/CHF): ใช้ $\delta$ ต่ำ ($10^{-5}$)
- สำหรับคู่ผันผวน (BTC/ETH): ใช้ $\delta$ สูงกว่า ($10^{-3}$)
- Cross-Validate บนข้อมูลประวัติเพื่อเลือก $\delta$ ที่เหมาะสม

---

## 7. การเก็งกำไรทางสถิติด้วย PCA

### 7.1 แนวคิด

การวิเคราะห์องค์ประกอบหลัก (Principal Component Analysis / PCA) ระบุปัจจัยร่วมที่ขับเคลื่อนตะกร้าสินทรัพย์ Residual จากปัจจัยเหล่านี้นิ่งและสามารถเทรดเป็น Spread ที่กลับสู่ค่าเฉลี่ย

### 7.2 วิธีการ

**ขั้นที่ 1: สร้างเมทริกซ์ผลตอบแทน**

$$\mathbf{R} = \begin{bmatrix} r_{1,1} & r_{2,1} & \cdots & r_{n,1} \\ r_{1,2} & r_{2,2} & \cdots & r_{n,2} \\ \vdots & & & \vdots \\ r_{1,T} & r_{2,T} & \cdots & r_{n,T} \end{bmatrix}$$

โดยที่ $r_{i,t}$ คือผลตอบแทนของสินทรัพย์ $i$ ณ เวลา $t$

**ขั้นที่ 2: PCA Decomposition**

$$\mathbf{R} = \mathbf{F}\mathbf{L}' + \mathbf{E}$$

โดยที่:
- $\mathbf{F}$ = Factor Scores (องค์ประกอบเชิงระบบ)
- $\mathbf{L}$ = Factor Loadings
- $\mathbf{E}$ = Residuals (องค์ประกอบเฉพาะตัว)

**ขั้นที่ 3: เทรด Residuals**

Residuals $\epsilon_{i,t}$ แสดงถึงการเบี่ยงเบนเฉพาะสินทรัพย์จากปัจจัยร่วม ถ้า Residuals นิ่ง สามารถเทรด Mean Reversion ได้

### 7.3 อัลกอริทึม PCA Stat Arb

```python
def pca_stat_arb(returns_matrix, n_factors=3, lookback=60):
    """
    PCA-based statistical arbitrage.
    
    1. Extract common factors via PCA
    2. Compute residuals (idiosyncratic returns)
    3. Cumulate residuals to get "residual prices"
    4. Trade mean reversion of residual prices
    """
    # Step 1: Standardize returns
    returns_std = (returns_matrix - returns_matrix.mean()) / returns_matrix.std()
    
    # Step 2: PCA
    pca = PCA(n_components=n_factors)
    factor_scores = pca.fit_transform(returns_std[-lookback:])
    loadings = pca.components_.T
    
    # Step 3: Compute residuals for each asset
    systematic = returns_std[-lookback:] @ loadings @ loadings.T
    residuals = returns_std[-lookback:] - systematic
    
    # Step 4: Cumulative residuals (residual "price")
    cum_residuals = residuals.cumsum(axis=0)
    
    # Step 5: Z-score of cumulative residuals
    z_scores = (cum_residuals[-1] - cum_residuals.mean(axis=0)) / cum_residuals.std(axis=0)
    
    # Step 6: Generate signals
    signals = {}
    for i, z in enumerate(z_scores):
        if z < -2.0:
            signals[i] = 'LONG'  # Residual is oversold; expect reversion up
        elif z > 2.0:
            signals[i] = 'SHORT'  # Residual is overbought; expect reversion down
            
    return signals, z_scores
```

### 7.4 การเลือกปัจจัยสำหรับคริปโต

สำหรับจักรวาลคริปโตยอดนิยม 20 ตัว:
- **ปัจจัยที่ 1** (50-70% ความแปรปรวน): ปัจจัยตลาด (BTC Dominance)
- **ปัจจัยที่ 2** (10-20% ความแปรปรวน): การหมุนเวียน L1 vs DeFi
- **ปัจจัยที่ 3** (5-10% ความแปรปรวน): Large Cap vs Small Cap

การเทรด Residuals หลังลบปัจจัย 3 ตัวนี้จะจับ Mean Reversion เฉพาะตัวที่บริสุทธิ์

### 7.5 การเทรด Eigenportfolio

แทนที่จะเทรด Residuals แต่ละตัว เทรด **Eigenportfolios** เมื่อเบี่ยงเบนจากสมดุล:

$$\text{Eigenportfolio}_k = \sum_i w_{k,i} P_i$$

โดยที่ $w_{k,i}$ คือน้ำหนัก Factor Loading สำหรับ Principal Component ที่ $k$

---

## 8. การเสริมด้วย Machine Learning

### 8.1 การตรวจจับสภาวะด้วย ML

**Hidden Markov Model (HMM) สำหรับสภาวะ Spread:**

จำลองกระบวนการ Spread ว่ามีหลายสถานะซ่อน:
- สถานะ 1: Cointegration เสถียร (Mean Reversion ปกติ)
- สถานะ 2: ช่วงเปลี่ยนผ่าน (Cointegration อ่อนลง)
- สถานะ 3: พังทลาย (ไม่มี Cointegration)

```python
from hmmlearn import hmm

def hmm_regime_detection(spread_series, n_states=3):
    """
    Detect spread regime using Gaussian HMM.
    """
    model = hmm.GaussianHMM(n_components=n_states, covariance_type="full")
    returns = np.diff(spread_series).reshape(-1, 1)
    model.fit(returns)
    
    hidden_states = model.predict(returns)
    state_probs = model.predict_proba(returns)
    
    # Identify the "mean-reverting" state (lowest variance)
    state_variances = [model.covars_[i][0][0] for i in range(n_states)]
    mean_reverting_state = np.argmin(state_variances)
    
    # Trade only when in mean-reverting state
    tradeable = hidden_states[-1] == mean_reverting_state
    confidence = state_probs[-1][mean_reverting_state]
    
    return tradeable, confidence, hidden_states
```

### 8.2 Random Forest สำหรับการเลือกคู่

ใช้ Machine Learning เพื่อทำนายคู่ที่จะกลับสู่ค่าเฉลี่ยสำเร็จ:

**ฟีเจอร์:**
- ครึ่งชีวิตของ Mean Reversion
- ค่าสถิติทดสอบ ADF
- Hurst Exponent ของ Spread
- ความเสถียรของสหสัมพันธ์เลื่อน
- อัตราส่วนความผันผวน Spread (ล่าสุด/ประวัติ)
- อัตราส่วนปริมาณซื้อขายของสองสินทรัพย์
- ส่วนต่าง Funding Rate (คริปโต)
- คะแนนความคล้ายคลึงของกลุ่ม

**เป้าหมาย:** การจำแนกแบบ Binary (เทรดทำกำไรภายใน $n$ แท่งหรือไม่)

### 8.3 การทำนาย Spread ด้วย Deep Learning

**LSTM สำหรับทิศทาง Spread:**

```python
def lstm_spread_predictor(spread_history, features, lookback=50):
    """
    LSTM model to predict spread direction/magnitude.
    
    Input: Last 50 bars of spread + features
    Output: Expected spread return over next 5 bars
    """
    model = Sequential([
        LSTM(64, input_shape=(lookback, n_features), return_sequences=True),
        Dropout(0.2),
        LSTM(32, return_sequences=False),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1, activation='linear')  # Predicted spread return
    ])
    
    model.compile(optimizer='adam', loss='mse')
    return model
```

### 8.4 Reinforcement Learning สำหรับการดำเนินการที่เหมาะสม

ใช้ RL เพื่อเรียนรู้เกณฑ์เข้า/ออกและขนาดสถานะที่เหมาะสม:

- **State**: (Z-Score, ครึ่งชีวิต, ความน่าจะเป็นสภาวะ, สถานะปัจจุบัน, P&L)
- **Action**: (entry_z, exit_z, position_size) หรือแบบ Discrete (ซื้อ/ขาย/ถือ)
- **Reward**: P&L ปรับความเสี่ยง (คล้าย Sharpe)

---

## 9. ข้อควรพิจารณาในการดำเนินการ

### 9.1 การเข้า/ออกพร้อมกัน

สำหรับเทรดคู่ ทั้งสองขาต้องดำเนินการพร้อมกันเพื่อรักษาสถานะ Spread ที่ป้องกัน

**วิธีการดำเนินการ:**

| วิธี | Latency | ต้นทุน | ความซับซ้อน |
|---|---|---|---|
| Market Order สองคำสั่ง | ต่ำสุด | สูงสุด (ทั้งคู่เป็น Taker) | ต่ำ |
| Market หนึ่ง + Limit หนึ่ง | ปานกลาง | ปานกลาง | กลาง |
| Limit Order สองคำสั่ง | สูงสุด (อาจไม่ถูก Fill) | ต่ำสุด | สูง |
| อัลกอริทึม (TWAP/VWAP) | สูง | ต่ำ | สูงมาก |

### 9.2 ความเสี่ยงของขา (Leg Risk)

**คำจำกัดความ:** ความเสี่ยงที่ขาหนึ่งถูก Fill ในขณะที่อีกขาไม่ถูก Fill

**กลยุทธ์ลดความเสี่ยง:**

1. **Market Order พร้อมกัน**: ยอมรับต้นทุน Spread เพื่อรับประกัน Fill
2. **เข้าทีละขาพร้อม Timeout**: ถ้าขาที่สองไม่ถูก Fill ภายใน $T$ วินาที ใช้ Market Order
3. **Limit Order ที่คำนึงถึง Spread**: วางทั้ง Limit ที่ราคาที่เอื้อต่อ Spread
4. **IOC (Immediate or Cancel)**: ใช้ IOC Order เพื่อหลีกเลี่ยง Partial Fill

```
Algorithm: Safe Pair Entry

1. Calculate target spread entry level
2. Place limit order for more liquid leg (Leg A)
3. Upon Leg A fill:
    a. Immediately place market order for Leg B
    b. Set timer: max_leg_delay = 5 seconds
4. If Leg B does not fill within max_leg_delay:
    a. Place aggressive limit order (cross the spread)
    b. If still not filled after 10 seconds:
        - Market order for Leg B
5. If Leg B fill price is worse than max_slippage:
    - Consider unwinding both legs
    - Log: "Excessive slippage on Leg B"
```

### 9.3 การรักษาอัตราส่วนสถานะ

เมื่อเวลาผ่านไป Hedge Ratio $\beta_t$ อาจเปลี่ยนแปลง ต้องปรับสมดุล:

$$\text{Rebalance Trigger} = |\beta_t - \beta_{entry}| > \delta_{rebal}$$

**กฎการปรับสมดุล:**
- ตรวจสอบ $\beta$ ทุก $n$ แท่ง (เช่น รายวัน)
- ปรับสมดุลถ้า $\beta$ เปลี่ยน > เกณฑ์ (เช่น 10% ของการเปลี่ยนแปลงสัมพัทธ์)
- ปรับปริมาณขา B: $\Delta Q_B = (beta_{new} - \beta_{entry}) \times Q_A$

---

## 10. การสร้างแบบจำลองต้นทุนธุรกรรม

### 10.1 องค์ประกอบต้นทุน

$$\text{Total Cost per Round-Trip} = 2 \times (C_{spread} + C_{commission} + C_{slippage} + C_{funding})$$

| องค์ประกอบ | Forex (ทั่วไป) | Crypto CEX (ทั่วไป) | Crypto DEX (ทั่วไป) |
|---|---|---|---|
| Half-Spread | 0.5-1.5 pips | 0.02-0.05% | 0.05-0.30% |
| ค่าคอมมิชชัน | 0-$3.50 ต่อ Lot | 0.02-0.10% | ค่า Gas |
| Slippage | 0.2-1.0 pips | 0.01-0.05% | 0.10-1.00% |
| ค่าทุน (ข้ามคืน) | อัตรา Swap | 0.01-0.10%/8ชม. | ไม่มี |

### 10.2 ผลกระทบต้นทุนต่อกำไร Stat Arb

**การเคลื่อนไหว Spread ขั้นต่ำเพื่อทำกำไร:**

$$\Delta S_{min} = \frac{\text{Total Round-Trip Cost}}{Q}$$

**ตัวอย่าง (คู่ BTC/ETH บน Binance):**
- อัตราค่าธรรมเนียม: 0.1% ต่อเทรด (Maker)
- สองขา, Round-Trip: 4 เทรด x 0.1% = 0.4% รวม
- ถ้ามูลค่าสถานะรวม = $20,000, ต้นทุน = $80 ต่อ Round-Trip
- การเคลื่อนไหว Spread ขั้นต่ำ: Spread ต้องเคลื่อนที่ > $80 ในทิศทางเรา

### 10.3 การวิเคราะห์จุดคุ้มทุน

$$\text{Minimum Z-Score Entry} = z_{min} = \frac{\text{Total Cost}}{\sigma_S}$$

เพื่อให้คู่เทรดได้:
- ส่วนเบี่ยงเบนมาตรฐาน Spread ต้องใหญ่เมื่อเทียบกับต้นทุน
- กฎทั่วไป: $\sigma_S > 5 \times \text{Total Cost per round-trip}$

### 10.4 ความถี่เทรดที่เหมาะสม

การเทรดถี่เกินจะกัดกินกำไรผ่านต้นทุน ความถี่ที่เหมาะสมสร้างสมดุลระหว่าง:

$$\text{Optimal Frequency} = \arg\max_f \left[f \times E[\text{Profit per trade}] - f \times \text{Cost per trade}\right]$$

เมื่อพิจารณาพลศาสตร์ Mean Reversion:
- ความถี่สูงจับ Mean Reversion มากขึ้นแต่จ่ายต้นทุนมากขึ้น
- ความถี่ต่ำมีกำไรต่อเทรดสูงกว่าแต่โอกาสน้อยกว่า

**ระยะเวลาถือครองที่เหมาะสมโดยประมาณ:**

$$T_{opt} \approx t_{half} \times \sqrt{\frac{\text{Cost}}{\sigma_S}}$$

---

## 11. ตรรกะหลัก — การเข้า/ออกสถานะ

### 11.1 ตรรกะการเข้าเทรดคู่

```
Algorithm: Statistical Arbitrage Entry

PRE-TRADE CHECKS:
    1. Cointegration valid: ADF p-value < 0.05 on spread (tested within last 20 bars)
    2. Half-life reasonable: 5 < t_half < 60 bars
    3. Spread volatility adequate: sigma_S > 5x round-trip cost
    4. Regime appropriate: HMM state = mean-reverting (or no regime model = always on)
    5. No major event risk: Check economic calendar
    
SIGNAL GENERATION:
    z = (spread - mean_spread) / std_spread
    
    IF z < -entry_z AND NOT in_position:
        SIGNAL = LONG_SPREAD
        Action: Long Y, Short X * beta
        Entry_z = z
        
    IF z > +entry_z AND NOT in_position:
        SIGNAL = SHORT_SPREAD
        Action: Short Y, Long X * beta
        Entry_z = z

POSITION SIZING:
    dollar_risk = account * risk_pct
    spread_risk = stop_z * std_spread * Q  # Where Q is notional per unit z
    position_notional = dollar_risk / ((stop_z - entry_z) * std_spread)
    
    # Split between legs
    Q_Y = position_notional / P_Y
    Q_X = Q_Y * beta
```

### 11.2 ตรรกะการออก

```
Algorithm: Statistical Arbitrage Exit

EACH BAR:
    z = (spread - mean_spread) / std_spread
    
    # 1. Mean reversion target
    IF position == LONG_SPREAD AND z >= exit_z:
        EXIT ALL
        Reason: "Spread reverted to mean"
        
    IF position == SHORT_SPREAD AND z <= -exit_z:
        EXIT ALL
        Reason: "Spread reverted to mean"
    
    # 2. Stop loss (spread divergence)
    IF position == LONG_SPREAD AND z < -stop_z:
        EXIT ALL
        Reason: "Spread diverged further — stop loss"
        
    IF position == SHORT_SPREAD AND z > +stop_z:
        EXIT ALL
        Reason: "Spread diverged further — stop loss"
    
    # 3. Time stop
    IF bars_in_trade > max_holding_bars:
        EXIT ALL
        Reason: "Time stop — spread failed to revert"
    
    # 4. Cointegration breakdown
    IF adf_pvalue > 0.10:  # Rolling ADF on recent data
        EXIT ALL
        Reason: "Cointegration breakdown detected"
    
    # 5. Hedge ratio drift
    IF |beta_current - beta_entry| / beta_entry > 0.20:
        REBALANCE or EXIT
        Reason: "Hedge ratio shifted significantly"
```

### 11.3 การจัดการสถานะ Spread

```
POSITION TRACKING:

For LONG SPREAD position:
    Leg A (Long Y):
        entry_price_Y = fill_price
        quantity_Y = Q_Y
        current_PnL_Y = (current_price_Y - entry_price_Y) * Q_Y
        
    Leg B (Short X):
        entry_price_X = fill_price
        quantity_X = Q_X = Q_Y * beta
        current_PnL_X = (entry_price_X - current_price_X) * Q_X
        
    Total Spread PnL:
        PnL = current_PnL_Y + current_PnL_X - costs
        
    Spread Value:
        entry_spread = entry_price_Y - beta * entry_price_X
        current_spread = current_price_Y - beta * current_price_X
        spread_PnL_theoretical = (current_spread - entry_spread) * dollar_per_spread_unit
```

---

## 12. ข้อมูลจำเพาะทางเทคนิค

### 12.1 การกำหนดค่าระบบ

```yaml
stat_arb_config:
  # Cointegration Testing
  cointegration:
    method: engle_granger  # or johansen
    estimation_window: 252
    retest_frequency: 20
    min_adf_pvalue: 0.05
    max_half_life: 60
    min_half_life: 5
    
  # Hedge Ratio
  hedge_ratio:
    method: kalman  # or ols_rolling, tls
    kalman_delta: 1e-4
    kalman_R: 1e-3
    ols_window: 60
    rebalance_threshold: 0.10  # 10% change triggers rebalance
    
  # Z-Score Parameters
  z_score:
    lookback: 20  # For rolling mean/std of spread
    entry_threshold: 2.0
    exit_threshold: 0.0  # Exit at mean
    stop_threshold: 4.0
    scale_entry: true  # Scale position by z-score magnitude
    
  # Position Sizing
  sizing:
    risk_per_trade: 0.015  # 1.5% of account
    max_notional_per_pair: 0.10  # 10% of account per pair
    max_pairs_concurrent: 5
    max_portfolio_risk: 0.06  # 6% total
    
  # Risk Management
  risk:
    max_drawdown: 0.10
    time_stop_bars: 60  # 3x typical half-life
    cointegration_check_freq: 10
    max_correlation_between_pairs: 0.50
    
  # Execution
  execution:
    entry_method: simultaneous_market  # or leg_in_limit
    max_slippage_bps: 10
    leg_timeout_seconds: 5
    rebalance_check_frequency: daily
```

### 12.2 การคัดกรองจักรวาลคู่

```yaml
pair_screening:
  universe:
    forex: [EUR/USD, GBP/USD, AUD/USD, NZD/USD, USD/CAD, USD/CHF, USD/JPY]
    crypto: [BTC, ETH, SOL, BNB, ADA, AVAX, DOT, LINK, UNI, AAVE]
    
  filters:
    min_daily_volume: $10M (crypto) / $100M (forex)
    max_spread_pct: 0.10%
    min_correlation: 0.50  # Pre-filter before cointegration test
    min_data_history: 252 bars
    
  screening_process:
    1. Form all possible pairs from universe
    2. Filter by minimum correlation (removes obviously unrelated)
    3. Test each remaining pair for cointegration (EG or Johansen)
    4. For cointegrated pairs, calculate half-life
    5. Filter by half-life (5 < t_half < 60)
    6. Rank by: (ADF stat significance * inverse half-life * spread volatility)
    7. Select top N pairs (e.g., top 5-10)
    8. Re-screen monthly
```

---

## 13. กรอบแนวคิดทางคณิตศาสตร์

### 13.1 Spread เป็น Ornstein-Uhlenbeck Process

ถ้า Spread $S_t$ เป็นไปตาม OU Process:

$$dS_t = \theta(\mu_S - S_t)dt + \sigma_S dW_t$$

แล้วค่าคาดหวังของ Spread ณ เวลา $t$ ที่กำหนด Spread ปัจจุบัน $S_0$:

$$E[S_t | S_0] = \mu_S + (S_0 - \mu_S)e^{-\theta t}$$

และความแปรปรวน:

$$\text{Var}(S_t | S_0) = \frac{\sigma_S^2}{2\theta}(1 - e^{-2\theta t})$$

### 13.2 เกณฑ์เข้าและออกที่เหมาะสม

จากกรอบ OU เกณฑ์เข้า/ออกที่เหมาะสมสามารถหาได้จากปัญหา Optimal Stopping

**Bertram (2010) คำตอบเชิงวิเคราะห์:**

สำหรับกฎเทรดแบบสมมาตรที่เข้าที่ $\pm a$ และออกที่ $\pm b$ (โดยที่ $a > b \geq 0$):

กำไรที่คาดหวังต่อเทรด:

$$E[\text{Profit}] = a - b - c$$

โดยที่ $c$ คือต้นทุนธุรกรรม Round-Trip

ระยะเวลาเทรดที่คาดหวัง:

$$E[\tau] = \frac{1}{\theta}\left[\Phi^{-1}(a) - \Phi^{-1}(b)\right]$$

โดยที่ $\Phi^{-1}$ เกี่ยวข้องกับเวลาผ่านครั้งแรกที่คาดหวังของ OU Process

**การหาค่าเหมาะสมแบบง่าย (สูงสุด Sharpe):**

$$\max_{a, b} \frac{E[\text{Profit per unit time}]}{\text{Std of Profit per unit time}}$$

ค่าเหมาะสมทั่วไป: $a^* \approx 1.5\sigma_S$ ถึง $2.5\sigma_S$, $b^* \approx 0$ ถึง $0.5\sigma_S$

### 13.3 Error Correction Model (ECM)

ECM ของ Engle-Granger สำหรับ Spread:

$$\Delta Y_t = \alpha_1(Y_{t-1} - \beta X_{t-1} - \mu) + \sum_{i=1}^{p}\gamma_i \Delta Y_{t-i} + \sum_{j=1}^{q}\delta_j \Delta X_{t-j} + u_t$$

โดยที่:
- $\alpha_1$ = ความเร็วการปรับตัว (ควรเป็นลบสำหรับ Mean Reversion)
- $(Y_{t-1} - \beta X_{t-1} - \mu)$ = Error Correction Term (= Spread)
- พลศาสตร์ระยะสั้นจับโดย $\gamma_i$ และ $\delta_j$

**การตีความ:**
- $|\alpha_1|$ ใกล้ 1: การปรับตัวเร็วมาก (Mean Reversion แข็งแกร่ง)
- $|\alpha_1|$ ใกล้ 0: การปรับตัวช้า (Mean Reversion อ่อน)
- $\alpha_1 > 0$: ไม่มี Error Correction (Spread อาจไม่นิ่ง)

### 13.4 Total Least Squares (TLS) Hedge Ratio

OLS ลดระยะทางแนวตั้ง (Y Residuals) ซึ่งอาจทำให้ $\beta$ มีอคติเมื่อทั้ง X และ Y มี Noise TLS (Orthogonal Regression) ลดระยะทางตั้งฉาก:

$$\hat{\beta}_{TLS} = \frac{\sigma_Y^2 - \sigma_X^2 + \sqrt{(\sigma_Y^2 - \sigma_X^2)^2 + 4\sigma_{XY}^2}}{2\sigma_{XY}}$$

หรือเทียบเท่าผ่าน SVD ของเมทริกซ์ข้อมูลที่จัดกลาง

### 13.5 Kelly Criterion สำหรับเทรดคู่

$$f^* = \frac{\mu_S}{z_{entry} \times \sigma_S^2}$$

โดยที่:
- $\mu_S$ = กำไรที่คาดหวังต่อเทรด (การเคลื่อนไหว Spread)
- $\sigma_S^2$ = ความแปรปรวนของผลตอบแทน Spread
- $z_{entry}$ = Z-Score ณ จุดเข้า

**Half-Kelly (แนะนำ):** $f = f^*/2$

### 13.6 พอร์ตโฟลิโอของคู่: การปรับตามสหสัมพันธ์

สำหรับ $n$ คู่ที่มีเมทริกซ์สหสัมพันธ์ผลตอบแทน Spread $\Sigma$:

$$w^* = \frac{1}{\gamma}\Sigma^{-1}\alpha$$

โดยที่:
- $\alpha$ = เวกเตอร์ผลตอบแทน Spread ที่คาดหวัง
- $\gamma$ = พารามิเตอร์ Risk Aversion
- $w^*$ = เวกเตอร์น้ำหนักที่เหมาะสม

สิ่งนี้รับประกันผลประโยชน์การกระจายข้ามคู่ขณะคำนึงถึงสหสัมพันธ์ระหว่าง Spread

---

## 14. พารามิเตอร์ความเสี่ยง

### 14.1 การกำหนดขนาดสถานะ

**ต่อคู่:**

$$\text{Notional per pair} = \frac{\text{Account} \times \text{Risk per pair}}{(\text{entry\_z} - \text{stop\_z}) \times \sigma_S \times \text{leverage factor}}$$

| ระดับความเสี่ยง | ความเสี่ยงต่อคู่ | คู่สูงสุด | ความเสี่ยงคู่รวม |
|---|---|---|---|
| อนุรักษ์นิยม | 1.0% | 3 | 3% |
| ปานกลาง | 1.5% | 5 | 7.5% |
| ก้าวร้าว | 2.0% | 7 | 14% |

### 14.2 กรอบ Stop Loss

| ประเภท Stop | เงื่อนไข | การดำเนินการ |
|---|---|---|
| Z-Score Stop | $|z| > z_{stop}$ (โดยทั่วไป 3.5-4.5) | ปิดทั้งสองขา |
| Dollar Stop | ขาดทุน > X% ของบัญชี | ปิดทั้งสองขา |
| Time Stop | ระยะถือครอง > 3x ครึ่งชีวิต | ปิดทั้งสองขา |
| Cointegration Stop | ADF p-value > 0.10 | ปิดทั้งสองขา |
| Hedge Ratio Stop | $\beta$ เปลี่ยน > 20% | ปรับสมดุลหรือปิด |
| Drawdown Stop | DD รวมของ Spread Book > 10% | ลดสถานะคู่ทั้งหมด 50% |

### 14.3 ตัวชี้วัดความเสี่ยงสำหรับพอร์ตคู่

| ตัวชี้วัด | เป้าหมาย | แจ้งเตือน |
|---|---|---|
| Net Market Exposure | < 10% ของ Gross | > 15% |
| Gross Exposure | < 3x บัญชี | > 4x บัญชี |
| ครึ่งชีวิต Spread เฉลี่ย | 10-30 แท่ง | > 50 แท่ง |
| อัตราชนะ (เทรดสำเร็จ) | > 55% | < 45% |
| ระยะถือครองเฉลี่ย | 1-3x ครึ่งชีวิต | > 5x ครึ่งชีวิต |
| สหสัมพันธ์ Spread (ระหว่างคู่) | < 0.50 | > 0.70 |
| Sharpe พอร์ต (Spread Book) | > 1.5 | < 0.8 |

### 14.4 การทดสอบภาวะวิกฤต (Stress Testing)

```
STRESS SCENARIOS:
    1. Correlation breakdown:
       - What if pair correlation drops from 0.8 to 0.3?
       - Expected max loss: full spread notional * max z-score * sigma_S
       
    2. One-leg liquidity crisis:
       - What if one leg becomes illiquid?
       - Maximum slippage: model 10x normal spread
       
    3. Structural break:
       - What if cointegration permanently breaks?
       - Maximum loss: stop_z * sigma_S * position_size
       
    4. Simultaneous pairs failure:
       - What if 3 pairs hit stop loss simultaneously?
       - Maximum portfolio loss: 3 * risk_per_pair = 4.5% (at 1.5% each)
       
    5. Flash crash:
       - Both legs gap adversely
       - Model: 5-sigma event on both legs with 50% correlation
```

---

## 15. ขั้นตอนการดำเนินการ

### 15.1 ระบบ Statistical Arbitrage ฉบับสมบูรณ์ — Pseudocode

```python
class StatArbSystem:
    """
    Complete Statistical Arbitrage Trading System
    Supports: Engle-Granger, Johansen, Kalman Filter
    Markets: Forex, Crypto
    """
    
    def __init__(self, config):
        self.config = config
        self.pairs = {}           # (asset_a, asset_b) -> pair_info
        self.positions = {}       # pair_id -> position info
        self.kalman_filters = {}  # pair_id -> KalmanPairTrading instance
        
    def screen_pairs(self, universe_data):
        """Step 1: Identify cointegrated pairs."""
        pairs = []
        symbols = list(universe_data.keys())
        
        for i in range(len(symbols)):
            for j in range(i+1, len(symbols)):
                sym_a, sym_b = symbols[i], symbols[j]
                price_a = universe_data[sym_a]
                price_b = universe_data[sym_b]
                
                corr = np.corrcoef(np.diff(np.log(price_a)), np.diff(np.log(price_b)))[0, 1]
                if abs(corr) < self.config['min_correlation']:
                    continue
                
                result = engle_granger_test(price_a, price_b)
                
                if result['is_cointegrated']:
                    half_life = calculate_half_life(result['residuals'])
                    
                    if self.config['min_half_life'] < half_life < self.config['max_half_life']:
                        pairs.append({
                            'sym_a': sym_a, 'sym_b': sym_b,
                            'hedge_ratio': result['hedge_ratio'],
                            'intercept': result['intercept'],
                            'half_life': half_life,
                            'adf_stat': result['adf_stat'],
                            'adf_pvalue': result['p_value'],
                            'correlation': corr
                        })
        
        pairs.sort(key=lambda p: p['adf_stat'])
        selected = pairs[:self.config['max_pairs_concurrent']]
        
        for pair in selected:
            pair_id = f"{pair['sym_a']}_{pair['sym_b']}"
            self.pairs[pair_id] = pair
            self.kalman_filters[pair_id] = KalmanPairTrading(
                delta=self.config['kalman_delta'], R=self.config['kalman_R'])
        
        return selected
    
    def update_spreads(self, current_prices):
        """Step 2: Update spread calculations for all pairs."""
        signals = {}
        for pair_id, pair in self.pairs.items():
            price_a = current_prices[pair['sym_a']]
            price_b = current_prices[pair['sym_b']]
            kf = self.kalman_filters[pair_id]
            alpha, beta, spread, spread_std = kf.update(price_b, price_a)
            if 'spread_history' not in pair:
                pair['spread_history'] = []
            pair['spread_history'].append(spread)
            if len(pair['spread_history']) >= self.config['z_lookback']:
                recent_spreads = pair['spread_history'][-self.config['z_lookback']:]
                z_score = (spread - np.mean(recent_spreads)) / np.std(recent_spreads)
            else:
                z_score = 0.0
            pair['current_spread'] = spread
            pair['current_z'] = z_score
            pair['current_beta'] = beta
            pair['current_alpha'] = alpha
            pair['spread_std'] = spread_std
            signals[pair_id] = z_score
        return signals
    
    def generate_signals(self, z_scores):
        """Step 3: Generate entry/exit signals."""
        actions = []
        for pair_id, z in z_scores.items():
            pair = self.pairs[pair_id]
            if pair_id in self.positions:
                action = self.check_exit(pair_id, z)
                if action:
                    actions.append(action)
            else:
                if abs(z) > self.config['entry_z']:
                    if pair.get('adf_pvalue', 1.0) < 0.05:
                        direction = 'LONG_SPREAD' if z < -self.config['entry_z'] else 'SHORT_SPREAD'
                        actions.append({
                            'pair_id': pair_id, 'action': 'ENTER',
                            'direction': direction, 'z_score': z,
                            'beta': pair['current_beta']
                        })
        return actions
    
    def check_exit(self, pair_id, z):
        """Check exit conditions for an open position."""
        pos = self.positions[pair_id]
        pair = self.pairs[pair_id]
        if pos['direction'] == 'LONG_SPREAD' and z >= self.config['exit_z']:
            return {'pair_id': pair_id, 'action': 'EXIT', 'reason': 'Target reached'}
        if pos['direction'] == 'SHORT_SPREAD' and z <= -self.config['exit_z']:
            return {'pair_id': pair_id, 'action': 'EXIT', 'reason': 'Target reached'}
        if pos['direction'] == 'LONG_SPREAD' and z < -self.config['stop_z']:
            return {'pair_id': pair_id, 'action': 'EXIT', 'reason': 'Stop loss'}
        if pos['direction'] == 'SHORT_SPREAD' and z > self.config['stop_z']:
            return {'pair_id': pair_id, 'action': 'EXIT', 'reason': 'Stop loss'}
        if pos['bars_held'] > self.config['time_stop_bars']:
            return {'pair_id': pair_id, 'action': 'EXIT', 'reason': 'Time stop'}
        if pair.get('adf_pvalue', 0) > 0.10:
            return {'pair_id': pair_id, 'action': 'EXIT', 'reason': 'Cointegration breakdown'}
        return None
    
    def execute_trade(self, action, current_prices):
        """Step 4: Execute pair trade."""
        pair_id = action['pair_id']
        pair = self.pairs[pair_id]
        if action['action'] == 'ENTER':
            notional = self.calculate_notional(pair_id)
            beta = action['beta']
            price_a = current_prices[pair['sym_a']]
            price_b = current_prices[pair['sym_b']]
            if action['direction'] == 'LONG_SPREAD':
                qty_a = notional / price_a
                qty_b = qty_a * beta
                self.exchange.buy(pair['sym_a'], qty_a)
                self.exchange.sell(pair['sym_b'], qty_b)
            else:
                qty_a = notional / price_a
                qty_b = qty_a * beta
                self.exchange.sell(pair['sym_a'], qty_a)
                self.exchange.buy(pair['sym_b'], qty_b)
            self.positions[pair_id] = {
                'direction': action['direction'], 'entry_z': action['z_score'],
                'entry_beta': beta, 'qty_a': qty_a, 'qty_b': qty_b,
                'entry_price_a': price_a, 'entry_price_b': price_b,
                'bars_held': 0, 'entry_spread': pair['current_spread']
            }
        elif action['action'] == 'EXIT':
            pos = self.positions[pair_id]
            if pos['direction'] == 'LONG_SPREAD':
                self.exchange.sell(pair['sym_a'], pos['qty_a'])
                self.exchange.buy(pair['sym_b'], pos['qty_b'])
            else:
                self.exchange.buy(pair['sym_a'], pos['qty_a'])
                self.exchange.sell(pair['sym_b'], pos['qty_b'])
            self.record_trade(pair_id, action['reason'], current_prices)
            del self.positions[pair_id]
    
    def run_monitoring_loop(self, data_feed):
        """Step 5: Main execution loop."""
        initial_data = data_feed.get_history(self.config['estimation_window'])
        self.screen_pairs(initial_data)
        rescreen_counter = 0
        for timestamp, prices in data_feed:
            z_scores = self.update_spreads(prices)
            actions = self.generate_signals(z_scores)
            for action in actions:
                self.execute_trade(action, prices)
            for pair_id in self.positions:
                self.positions[pair_id]['bars_held'] += 1
            rescreen_counter += 1
            if rescreen_counter >= self.config['retest_frequency']:
                self.validate_cointegration(data_feed.get_recent(self.config['estimation_window']))
                rescreen_counter = 0
            self.log_status(prices, z_scores)
```

### 15.2 แผนภาพขั้นตอนการดำเนินการ

```
┌───────────────────────────────────────────────────┐
│        STATISTICAL ARBITRAGE EXECUTION FLOW       │
├───────────────────────────────────────────────────┤
│                                                   │
│  1. PAIR SCREENING (Monthly)                      │
│     ├─ Form all pair combinations                 │
│     ├─ Pre-filter by correlation (> 0.50)         │
│     ├─ Run Engle-Granger cointegration test       │
│     ├─ Calculate half-life for each pair          │
│     ├─ Filter by half-life (5-60 bars)            │
│     ├─ Rank by ADF statistic strength             │
│     └─ Select top N pairs for trading             │
│                                                   │
│  2. SPREAD CALCULATION (Each Bar)                 │
│     ├─ Update Kalman filter for each pair         │
│     ├─ Get dynamic hedge ratio (beta_t)           │
│     ├─ Calculate current spread                   │
│     ├─ Calculate rolling z-score                  │
│     └─ Update spread history                      │
│                                                   │
│  3. SIGNAL GENERATION                             │
│     ├─ Check z-score vs entry threshold           │
│     ├─ Verify cointegration still holds           │
│     ├─ Check available capacity (max pairs)       │
│     └─ Generate LONG_SPREAD or SHORT_SPREAD       │
│                                                   │
│  4. EXECUTION                                     │
│     ├─ Calculate position size (risk-based)       │
│     ├─ Determine leg quantities (A and B*beta)    │
│     ├─ Execute both legs simultaneously           │
│     ├─ Confirm fills and record entry             │
│     └─ Handle leg risk (timeout / market order)   │
│                                                   │
│  5. POSITION MANAGEMENT                           │
│     ├─ Monitor z-score for mean reversion         │
│     ├─ Check stop loss (z-score expansion)        │
│     ├─ Check time stop (3x half-life)             │
│     ├─ Check cointegration validity               │
│     ├─ Rebalance if hedge ratio drifts            │
│     └─ Exit when conditions met                   │
│                                                   │
│  6. COINTEGRATION MONITORING (Periodic)           │
│     ├─ Re-run ADF test on spread                  │
│     ├─ Re-estimate half-life                      │
│     ├─ Check for structural breaks                │
│     ├─ HMM regime classification                  │
│     └─ Disable pair if cointegration breaks       │
│                                                   │
│  7. PORTFOLIO MONITORING                          │
│     ├─ Track net market exposure                  │
│     ├─ Monitor cross-pair correlations            │
│     ├─ Drawdown tracking                          │
│     ├─ Performance attribution (per pair)         │
│     └─ Alert on anomalies                         │
│                                                   │
└───────────────────────────────────────────────────┘
```

---

## 16. วิธีการ Backtest

### 16.1 ระเบียบวิธี Backtest สำหรับ Stat Arb

```
1. DATA PREPARATION:
    - Minimum 3 years of clean price data
    - Ensure proper timestamp alignment between assets
    - Account for missing data (holidays, exchange outages)
    - Use mid-prices (not last traded price) where possible
    
2. EXPANDING WINDOW APPROACH:
    - Start with minimum estimation window (252 bars)
    - At each step:
      a. Estimate cointegration on [0:t]
      b. Generate signal at t+1
      c. Track P&L forward from t+1
    - This prevents look-ahead bias in beta estimation
    
3. TRANSACTION COSTS:
    - Model realistic spreads (vary by time of day, volatility)
    - Include commission on all 4 legs (entry A, entry B, exit A, exit B)
    - Include slippage model (function of order size / daily volume)
    - Include funding costs for short positions
    
4. REBALANCING COSTS:
    - When hedge ratio changes, rebalancing has cost
    - Model the frequency and magnitude of rebalances
    
5. CAPACITY CONSTRAINTS:
    - Model maximum position sizes (% of daily volume)
    - Impact: Large positions may move the spread
```

### 16.2 ตัวชี้วัด Backtest สำคัญ

| ตัวชี้วัด | สูตร | เป้าหมาย (Stat Arb) |
|---|---|---|
| Sharpe Ratio | $(R_{ann} - R_f) / \sigma_{ann}$ | > 2.0 |
| อัตราชนะ | เทรดชนะ / ทั้งหมด | > 55% |
| ระยะเวลาเทรดเฉลี่ย | ระยะถือครองเฉลี่ย | ~ ครึ่งชีวิต |
| Profit Factor | กำไรรวม / ขาดทุนรวม | > 2.0 |
| Max Drawdown | จุดสูงสุดถึงจุดต่ำสุด | < 10% |
| Calmar Ratio | ผลตอบแทนรายปี / Max DD | > 2.0 |
| เทรดต่อเดือน | ความถี่เฉลี่ย | 5-20 |
| อัตราสำเร็จ (การเลือกคู่) | คู่ที่ทำกำไร / คู่ที่ทดสอบ | > 40% |
| Sharpe Decay (OOS) | OOS Sharpe / IS Sharpe | > 0.60 |

---

## 17. เอกสารอ้างอิง

### บทความวิชาการ

1. **Engle, R.F., & Granger, C.W.J.** (1987). "Co-Integration and Error Correction: Representation, Estimation, and Testing." *Econometrica*, 55(2), 251-276.
2. **Johansen, S.** (1991). "Estimation and Hypothesis Testing of Cointegration Vectors in Gaussian Vector Autoregressive Models." *Econometrica*, 59(6), 1551-1580.
3. **Gatev, E., Goetzmann, W., & Rouwenhorst, K.G.** (2006). "Pairs Trading: Performance of a Relative-Value Arbitrage Rule." *Review of Financial Studies*, 19(3), 797-827.
4. **Vidyamurthy, G.** (2004). *Pairs Trading: Quantitative Methods and Analysis*. Wiley.
5. **Avellaneda, M., & Lee, J.H.** (2010). "Statistical Arbitrage in the US Equities Market." *Quantitative Finance*, 10(7), 761-782.
6. **Bertram, W.K.** (2010). "Analytic Solutions for Optimal Statistical Arbitrage Trading." *Physica A*, 389, 2234-2243.
7. **Elliott, R.J., Van der Hoek, J., & Malcolm, W.P.** (2005). "Pairs Trading." *Quantitative Finance*, 5(3), 271-276.
8. **Kalman, R.E.** (1960). "A New Approach to Linear Filtering and Prediction Problems." *Journal of Basic Engineering*, 82(1), 35-45.
9. **Do, B., & Faff, R.** (2010). "Does Simple Pairs Trading Still Work?" *Financial Analysts Journal*, 66(4), 83-95.
10. **Krauss, C.** (2017). "Statistical Arbitrage Pairs Trading Strategies: Review and Outlook." *Journal of Economic Surveys*, 31(2), 513-545.

### แหล่งข้อมูลสำหรับผู้ปฏิบัติ

11. **Ernie Chan.** (2009). *Quantitative Trading*. Wiley. (บทเกี่ยวกับเทรดคู่และ Cointegration)
12. **Ernie Chan.** (2013). *Algorithmic Trading*. Wiley. (Kalman Filter และ Stat Arb ขั้นสูง)
13. **Pole, A.** (2007). *Statistical Arbitrage: Algorithmic Trading Insights and Techniques*. Wiley.
14. **Whistler, M.** (2004). *Trading Pairs*. Wiley.

### ซอฟต์แวร์และเครื่องมือ

15. **statsmodels** (Python): การทดสอบ Cointegration, แบบจำลอง VAR, Kalman Filter
16. **pykalman** (Python): การนำ Kalman Filter ไปใช้
17. **CCXT**: API แบบรวมสำหรับการดำเนินการบน Crypto Exchange
18. **Zipline / Backtrader**: กรอบ Backtesting ที่รองรับหลายสินทรัพย์

---

*เอกสารนี้เป็นส่วนหนึ่งของฐานความรู้ระบบเทรด AI แบบ Multi-Agent การเก็งกำไรทางสถิติให้ Alpha ที่เป็นกลางต่อตลาดโดยใช้ประโยชน์จากการกำหนดราคาผิดชั่วคราวระหว่างสินทรัพย์ที่มี Cointegration ให้การกระจายความเสี่ยงจากกลยุทธ์เทรดตามทิศทาง*
