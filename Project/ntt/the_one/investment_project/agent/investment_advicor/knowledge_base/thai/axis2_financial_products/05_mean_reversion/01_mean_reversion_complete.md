# กลยุทธ์การกลับตัวหาค่าเฉลี่ย (Mean Reversion) --- คู่มือฉบับสมบูรณ์

## ข้อมูลเอกสาร
| หัวข้อ | รายละเอียด |
|---|---|
| ประเภทกลยุทธ์ | การกลับตัวหาค่าเฉลี่ย / การเทรดเชิงสถิติ (Mean Reversion / Statistical Trading) |
| ประเภทสินทรัพย์ | Forex, คริปโต (Spot & Futures) |
| กรอบเวลา | ภายในวันถึงหลายสัปดาห์ |
| ความซับซ้อน | ระดับกลางถึงสูง |
| เงินทุนที่ต้องการ | ปานกลาง |
| อัปเดตล่าสุด | 2026-04-12 |

---

## สารบัญ
1. [พื้นฐานทางสถิติ](#1-พื้นฐานทางสถิติ)
2. [การตรวจจับ Mean Reversion](#2-การตรวจจับ-mean-reversion)
3. [กลยุทธ์ Bollinger Band Mean Reversion](#3-กลยุทธ์-bollinger-band-mean-reversion)
4. [การเข้า/ออกตาม Z-Score](#4-การเข้าออกตาม-z-score)
5. [กลยุทธ์ Keltner Channel](#5-กลยุทธ์-keltner-channel)
6. [RSI Extreme Mean Reversion](#6-rsi-extreme-mean-reversion)
7. [Half-Life ของ Mean Reversion](#7-half-life-ของ-mean-reversion)
8. [การเลือก Lookback Period ที่เหมาะสม](#8-การเลือก-lookback-period-ที่เหมาะสม)
9. [การประยุกต์ใช้กับ Forex และคริปโต](#9-การประยุกต์ใช้กับ-forex-และคริปโต)
10. [ลอจิกหลัก --- การเข้า/ออก](#10-ลอจิกหลัก----การเข้าออก)
11. [ข้อกำหนดทางเทคนิค](#11-ข้อกำหนดทางเทคนิค)
12. [แบบจำลองทางคณิตศาสตร์](#12-แบบจำลองทางคณิตศาสตร์)
13. [พารามิเตอร์ความเสี่ยง](#13-พารามิเตอร์ความเสี่ยง)
14. [ขั้นตอนการทำงาน](#14-ขั้นตอนการทำงาน)
15. [วิธีการทดสอบย้อนหลัง](#15-วิธีการทดสอบย้อนหลัง)
16. [เอกสารอ้างอิง](#16-เอกสารอ้างอิง)

---

## 1. พื้นฐานทางสถิติ

### 1.1 กระบวนการ Ornstein-Uhlenbeck

กลยุทธ์ Mean Reversion มีพื้นฐานจากทฤษฎีที่ว่าราคา (หรือสเปรด) มีแนวโน้มที่จะกลับสู่ระดับสมดุลระยะยาว แบบจำลอง Continuous-time มาตรฐานสำหรับกระบวนการที่กลับตัวหาค่าเฉลี่ยคือ **กระบวนการ Ornstein-Uhlenbeck (OU)**:

$$dX_t = \theta(\mu - X_t)dt + \sigma dW_t$$

โดยที่:
- $X_t$ = ค่าของกระบวนการที่เวลา $t$ (เช่น ราคา, สเปรด, หรือ Log-price)
- $\theta$ = ความเร็วของการกลับตัวหาค่าเฉลี่ย (อัตราที่กระบวนการกลับสู่ $\mu$)
- $\mu$ = ค่าเฉลี่ยระยะยาว (ระดับสมดุล)
- $\sigma$ = ความผันผวนของกระบวนการ
- $W_t$ = กระบวนการ Wiener มาตรฐาน (Brownian Motion)

**การตีความพารามิเตอร์:**

| พารามิเตอร์ | ความหมาย | ช่วงทั่วไป |
|---|---|---|
| $\theta$ | ความเร็ว Mean Reversion | 0.01 - 10 (สูงกว่า = กลับตัวเร็วกว่า) |
| $\mu$ | ระดับสมดุล | ประมาณจากข้อมูล |
| $\sigma$ | ขนาดของ Noise | ประมาณจากข้อมูล |

**คุณสมบัติสำคัญของกระบวนการ OU:**

1. **การแจกแจงคงที่ (Stationary Distribution)**: $X_t \sim \mathcal{N}\left(\mu, \frac{\sigma^2}{2\theta}\right)$ เมื่อ $t \to \infty$
2. **สหสัมพันธ์อัตโนมัติ (Autocorrelation)**: $\text{Corr}(X_t, X_{t+s}) = e^{-\theta s}$
3. **ค่าคาดหวัง**: $E[X_t | X_0] = \mu + (X_0 - \mu)e^{-\theta t}$
4. **ความแปรปรวน**: $\text{Var}(X_t | X_0) = \frac{\sigma^2}{2\theta}(1 - e^{-2\theta t})$

### 1.2 การประมาณค่าแบบ Discrete-Time

กระบวนการ OU สามารถแปลงเป็นแบบจำลอง AR(1) ได้:

$$X_t = a + bX_{t-1} + \epsilon_t$$

โดยที่:
- $a = \mu(1 - e^{-\theta\Delta t})$
- $b = e^{-\theta\Delta t}$
- $\epsilon_t \sim \mathcal{N}(0, \frac{\sigma^2}{2\theta}(1 - e^{-2\theta\Delta t}))$

**การประมาณค่าพารามิเตอร์ด้วย OLS:**

ทำ Regression ของ $X_t$ กับ $X_{t-1}$:

$$X_t = \hat{a} + \hat{b}X_{t-1} + \hat{\epsilon}_t$$

จากนั้นแปลงกลับเป็นพารามิเตอร์ OU:
- $\hat{\theta} = -\frac{\ln(\hat{b})}{\Delta t}$
- $\hat{\mu} = \frac{\hat{a}}{1 - \hat{b}}$
- $\hat{\sigma} = \hat{\sigma}_\epsilon \sqrt{\frac{-2\ln(\hat{b})}{\Delta t(1 - \hat{b}^2)}}$

### 1.3 ทำไม Mean Reversion จึงเกิดขึ้น

| ตลาด | ปัจจัยขับเคลื่อน Mean Reversion |
|---|---|
| Forex | นโยบายธนาคารกลาง, ดุลยภาพอำนาจซื้อ, ดุลยภาพอัตราดอกเบี้ย |
| คริปโต | การ Arbitrage ข้ามตลาด, Funding Rate กลับตัวหาค่าเฉลี่ย, Market Maker ปรับสมดุล Inventory |
| ข้ามสินทรัพย์ | ปฏิกิริยาเกินจริง/ต่ำเกินจริงต่อข่าว, การให้สภาพคล่อง, อคติทางพฤติกรรม |

### 1.4 เปรียบเทียบ Mean Reversion, Random Walk และ Momentum

| คุณสมบัติ | Mean Reversion | Random Walk | Momentum |
|---|---|---|---|
| Hurst Exponent $H$ | $H < 0.5$ | $H = 0.5$ | $H > 0.5$ |
| สหสัมพันธ์อัตโนมัติ | ลบ | ศูนย์ | บวก |
| Variance Ratio | $VR < 1$ | $VR = 1$ | $VR > 1$ |
| ADF Test | ปฏิเสธ Unit Root | ไม่สามารถปฏิเสธ | ไม่สามารถปฏิเสธ |
| กลยุทธ์ที่เหมาะสม | เทรดสวนทางที่จุดสุดโต่ง | ไม่มี Edge | ตามแนวโน้ม |

---

## 2. การตรวจจับ Mean Reversion

### 2.1 Hurst Exponent

Hurst Exponent $H$ วัดระดับของ Mean Reversion หรือ Persistence ในอนุกรมเวลา

**คำจำกัดความ:**

$$E\left[\frac{R(n)}{S(n)}\right] = C \cdot n^H$$

โดยที่ $R(n)/S(n)$ คือ Rescaled Range สำหรับ $n$ ข้อมูล

**การคำนวณ (วิธี R/S):**

```
Algorithm: Hurst Exponent Estimation

INPUT: price_series of length T

1. Compute log returns: r_t = ln(P_t / P_{t-1})

2. For each sub-period length n in {n_min, ..., n_max}:
    a. Divide series into k = floor(T/n) sub-periods
    b. For each sub-period j:
        - Compute mean: m_j = mean(r in sub-period j)
        - Compute cumulative deviations: Y_t = sum_{i=1}^{t}(r_i - m_j)
        - R_j = max(Y) - min(Y)  (range)
        - S_j = std(r in sub-period j) (standard deviation)
    c. RS(n) = mean(R_j / S_j) over all sub-periods

3. Fit: log(RS(n)) = H * log(n) + C via OLS

4. H = slope of regression

OUTPUT: H (Hurst exponent)
```

**การตีความ:**

| ช่วง Hurst | พฤติกรรม | นัยสำหรับการเทรด |
|---|---|---|
| $0 < H < 0.5$ | กลับตัวหาค่าเฉลี่ย | ใช้กลยุทธ์ Mean Reversion |
| $H = 0.5$ | Random Walk | ไม่มี Edge ทางสถิติ |
| $0.5 < H < 1$ | มีแนวโน้ม/Persistent | ใช้กลยุทธ์ Momentum |

**เกณฑ์เชิงปฏิบัติ:**
- $H < 0.4$: สัญญาณ Mean Reversion แรง
- $0.4 \leq H < 0.5$: Mean Reversion อ่อน
- $0.5 \leq H < 0.6$: แนวโน้มอ่อน
- $H \geq 0.6$: สัญญาณแนวโน้มแรง

### 2.2 Augmented Dickey-Fuller (ADF) Test

ADF Test ตรวจสอบว่าอนุกรมเวลามี Unit Root (ไม่คงที่) หรือเป็น Stationary (กลับตัวหาค่าเฉลี่ย)

**สมการ Regression ที่ทดสอบ:**

$$\Delta X_t = \alpha + \beta t + \gamma X_{t-1} + \sum_{i=1}^{p} \delta_i \Delta X_{t-i} + \epsilon_t$$

**สมมติฐาน:**
- $H_0$: $\gamma = 0$ (มี Unit Root, ไม่คงที่)
- $H_1$: $\gamma < 0$ (คงที่, กลับตัวหาค่าเฉลี่ย)

**สถิติทดสอบ:**

$$ADF = \frac{\hat{\gamma}}{SE(\hat{\gamma})}$$

เปรียบเทียบกับค่าวิกฤต (ค่าลบมากขึ้น = ปฏิเสธ Unit Root ได้แข็งแกร่งขึ้น)

| ระดับนัยสำคัญ | ค่าวิกฤต (ไม่มีแนวโน้ม) |
|---|---|
| 1% | -3.43 |
| 5% | -2.86 |
| 10% | -2.57 |

**กฎการตัดสินใจ:**
- หากสถิติ ADF < ค่าวิกฤต: **ปฏิเสธ $H_0$** --- อนุกรมกลับตัวหาค่าเฉลี่ย
- หากสถิติ ADF > ค่าวิกฤต: **ไม่สามารถปฏิเสธ** --- อนุกรมอาจมี Unit Root

### 2.3 Variance Ratio Test

Variance Ratio Test เปรียบเทียบความแปรปรวนของผลตอบแทน $q$-ช่วงกับความแปรปรวนของผลตอบแทน 1-ช่วง:

$$VR(q) = \frac{\text{Var}(r_t^{(q)})}{q \cdot \text{Var}(r_t^{(1)})}$$

โดยที่ $r_t^{(q)} = \ln(P_t/P_{t-q})$

**การตีความ:**
- $VR(q) < 1$: กลับตัวหาค่าเฉลี่ย
- $VR(q) = 1$: Random Walk
- $VR(q) > 1$: มีแนวโน้ม

**สถิติทดสอบ Lo-MacKinlay:**

$$z(q) = \frac{VR(q) - 1}{\sqrt{\frac{2(2q-1)(q-1)}{3qT}}}$$

ภายใต้ $H_0$ (Random Walk), $z(q) \sim \mathcal{N}(0,1)$

### 2.4 KPSS Test (เสริม ADF)

KPSS Test มีสมมติฐานว่างตรงข้ามกับ ADF:
- $H_0$: อนุกรมคงที่ (Stationary)
- $H_1$: อนุกรมมี Unit Root

**แนวปฏิบัติที่ดี: ใช้ทั้งสองการทดสอบร่วมกัน:**

| ผล ADF | ผล KPSS | ข้อสรุป |
|---|---|---|
| ปฏิเสธ $H_0$ | ไม่ปฏิเสธ $H_0$ | **กลับตัวหาค่าเฉลี่ย** (ทั้งสองเห็นด้วย) |
| ไม่ปฏิเสธ $H_0$ | ปฏิเสธ $H_0$ | **มี Unit Root** (ทั้งสองเห็นด้วย) |
| ปฏิเสธ $H_0$ | ปฏิเสธ $H_0$ | ไม่ชัดเจน |
| ไม่ปฏิเสธ $H_0$ | ไม่ปฏิเสธ $H_0$ | ไม่ชัดเจน |

---

## 3. กลยุทธ์ Bollinger Band Mean Reversion

### 3.1 การสร้าง Bollinger Band

**แถบบน:**

$$BB_{upper} = SMA(P, n) + k \times \sigma(P, n)$$

**แถบล่าง:**

$$BB_{lower} = SMA(P, n) - k \times \sigma(P, n)$$

**แถบกลาง (ค่าเฉลี่ย):**

$$BB_{mid} = SMA(P, n) = \frac{1}{n}\sum_{i=0}^{n-1} P_{t-i}$$

โดยที่:
- $n$ = ช่วง Lookback (ค่าเริ่มต้น: 20)
- $k$ = ตัวคูณส่วนเบี่ยงเบนมาตรฐาน (ค่าเริ่มต้น: 2.0)
- $\sigma(P, n)$ = ส่วนเบี่ยงเบนมาตรฐานแบบเลื่อนของราคา

### 3.2 Bollinger Band Width (BBW)

$$BBW = \frac{BB_{upper} - BB_{lower}}{BB_{mid}} = \frac{2k \times \sigma(P, n)}{SMA(P, n)}$$

BBW วัดความผันผวนปัจจุบันเทียบกับค่าเฉลี่ย BBW ต่ำ (Squeeze) มักเกิดก่อนการ Breakout

### 3.3 ตัวบ่งชี้ %B

$$\%B = \frac{P - BB_{lower}}{BB_{upper} - BB_{lower}}$$

| ค่า %B | ตำแหน่ง | การตีความ |
|---|---|---|
| > 1.0 | เหนือแถบบน | ซื้อมากเกินไป (Overbought) |
| 0.5 | ที่แถบกลาง | กลาง |
| < 0.0 | ต่ำกว่าแถบล่าง | ขายมากเกินไป (Oversold) |

### 3.4 กลยุทธ์ Bollinger Band Mean Reversion

**กฎการเข้า:**

| สัญญาณ | เงื่อนไข | การดำเนินการ |
|---|---|---|
| เข้า Long | $P_t < BB_{lower}$ AND $\%B < 0$ | ซื้อ (เทรดสวนทางการลง) |
| เข้า Short | $P_t > BB_{upper}$ AND $\%B > 1$ | ขาย (เทรดสวนทางการขึ้น) |
| ยืนยัน | RSI Divergence หรือปริมาณลดลง | เพิ่มความมั่นใจ |

**กฎการออก:**

| สัญญาณ | เงื่อนไข | การดำเนินการ |
|---|---|---|
| ออก Long (TP) | $P_t \geq BB_{mid}$ | ทำกำไรที่ค่าเฉลี่ย |
| ออก Short (TP) | $P_t \leq BB_{mid}$ | ทำกำไรที่ค่าเฉลี่ย |
| ออก Long (SL) | $P_t < BB_{lower} - k_{SL} \times \sigma$ | Stop Loss |
| ออก Short (SL) | $P_t > BB_{upper} + k_{SL} \times \sigma$ | Stop Loss |

**การเข้าแบบปรับปรุง --- Bollinger Band Bounce:**

```
LONG ENTRY CONDITIONS (ต้องเป็นจริงทั้งหมด):
    1. ราคาแตะหรือปิดต่ำกว่า Lower Bollinger Band (2σ)
    2. ราคาไม่ปิดต่ำกว่าแถบ 3σ (กรองการพังทลายรุนแรง)
    3. BBW > minimum_width (หลีกเลี่ยงสถานการณ์ Squeeze)
    4. RSI(14) < 30 (ยืนยัน Oversold)
    5. ไม่มีข่าวสำคัญภายใน 2 ชั่วโมงข้างหน้า
    6. ปริมาณขาลงลดลง (หมดแรงขาย)
    
ENTRY: ซื้อที่ตลาดหรือ Limit ที่ BB_lower
TARGET: BB_mid (แถบกลาง)
STOP: BB_lower - 1.0 * ATR(14)
```

### 3.5 พารามิเตอร์ Bollinger Band ตามตลาด

| ตลาด | ช่วง ($n$) | ตัวคูณ ($k$) | กรอบเวลา |
|---|---|---|---|
| Forex คู่หลัก | 20 | 2.0 | H1, H4, D1 |
| Forex คู่ข้าม | 20 | 2.0-2.5 | H4, D1 |
| BTC/USDT | 20 | 2.0-2.5 | H1, H4 |
| Altcoins | 20 | 2.5-3.0 | H4, D1 |

---

## 4. การเข้า/ออกตาม Z-Score

### 4.1 คำจำกัดความ Z-Score

Z-Score ปรับมาตรฐานการเบี่ยงเบนของราคาปัจจุบันจากค่าเฉลี่ยเคลื่อนที่:

$$z_t = \frac{P_t - \bar{P}_n}{\sigma_n}$$

โดยที่:
- $\bar{P}_n$ = ค่าเฉลี่ยเคลื่อนที่สำหรับ $n$ ช่วง
- $\sigma_n$ = ส่วนเบี่ยงเบนมาตรฐานสำหรับ $n$ ช่วง

### 4.2 กฎการเทรดตาม Z-Score

**เกณฑ์มาตรฐาน:**

| Z-Score | สัญญาณ | การดำเนินการ |
|---|---|---|
| $z > +2.0$ | ซื้อมากเกินไป | เข้า Short |
| $z > +1.0$ | ซื้อมากเกินไปเล็กน้อย | ทยอยเข้า Short (ทางเลือก) |
| $-0.5 < z < +0.5$ | กลาง | ปิดสถานะ |
| $z < -1.0$ | ขายมากเกินไปเล็กน้อย | ทยอยเข้า Long (ทางเลือก) |
| $z < -2.0$ | ขายมากเกินไป | เข้า Long |

**อัลกอริทึมสร้างสัญญาณ:**

```
Algorithm: Z-Score Mean Reversion

PARAMETERS:
    lookback = 20           # Rolling window for mean and std
    entry_z = 2.0           # Z-score threshold for entry
    exit_z = 0.0            # Z-score threshold for exit (mean)
    stop_z = 3.5            # Z-score threshold for stop loss
    
EACH BAR:
    1. Calculate rolling statistics:
       mean_n = SMA(close, lookback)
       std_n = rolling_std(close, lookback)
       z = (close - mean_n) / std_n
    
    2. Generate signals:
       IF z < -entry_z AND no_position:
           SIGNAL = LONG
           
       IF z > +entry_z AND no_position:
           SIGNAL = SHORT
           
       IF position == LONG AND z >= -exit_z:
           SIGNAL = CLOSE_LONG
           
       IF position == SHORT AND z <= +exit_z:
           SIGNAL = CLOSE_SHORT
           
       IF position == LONG AND z < -stop_z:
           SIGNAL = STOP_LONG  # Mean reversion failed
           
       IF position == SHORT AND z > +stop_z:
           SIGNAL = STOP_SHORT  # Mean reversion failed
```

### 4.3 กลยุทธ์ Z-Score Scaling

แทนที่จะเข้าแบบ Binary ให้ปรับขนาดตำแหน่งตามขนาดของ Z-Score:

$$\text{Position Size} = \text{Base Size} \times \min\left(\frac{|z| - z_{entry}}{z_{max} - z_{entry}}, 1.0\right)$$

| Z-Score | ตำแหน่ง % ของสูงสุด |
|---|---|
| $|z| = 2.0$ | 33% |
| $|z| = 2.5$ | 67% |
| $|z| = 3.0$ | 100% |
| $|z| > 3.5$ | Stop Loss (Mean Reversion ล้มเหลว) |

---

## 5. กลยุทธ์ Keltner Channel

### 5.1 การสร้าง Keltner Channel

**เส้นกลาง:**

$$KC_{mid} = EMA(P, n)$$

**ช่องบน:**

$$KC_{upper} = EMA(P, n) + k \times ATR(m)$$

**ช่องล่าง:**

$$KC_{lower} = EMA(P, n) - k \times ATR(m)$$

โดยที่:
- $EMA(P, n)$ = ค่าเฉลี่ยเคลื่อนที่แบบเอ็กซ์โพเนนเชียลของราคา
- $ATR(m)$ = Average True Range สำหรับ $m$ ช่วง
- $k$ = ตัวคูณ (ค่าเริ่มต้น: 2.0)

### 5.2 Keltner เทียบกับ Bollinger Bands

| คุณสมบัติ | Bollinger Bands | Keltner Channels |
|---|---|---|
| การวัดความผันผวน | ส่วนเบี่ยงเบนมาตรฐาน | Average True Range |
| เส้นกลาง | SMA | EMA |
| การตอบสนอง | ตอบสนองต่อราคาพุ่งมากกว่า | ราบเรียบกว่า ตอบสนองน้อยกว่า |
| ความกว้างแถบ | หดตัว/ขยายตามความผันผวน | กว้างคงที่กว่า |
| สัญญาณหลอก | มากกว่าในตลาด Choppy | น้อยกว่า น่าเชื่อถือกว่า |
| เหมาะสำหรับ | สัญญาณ Mean Reversion ที่แข็งแรง | Mean Reversion ที่กรองแนวโน้ม |

### 5.3 การตรวจจับ Bollinger-Keltner Squeeze

**Squeeze** เกิดขึ้นเมื่อ Bollinger Bands อยู่ภายใน Keltner Channels:

$$\text{Squeeze} = (BB_{upper} < KC_{upper}) \text{ AND } (BB_{lower} > KC_{lower})$$

**นัยสำหรับกลยุทธ์:**
- ระหว่าง Squeeze: **หลีกเลี่ยง Mean Reversion** (มีโอกาส Breakout)
- หลัง Squeeze ปล่อย: **เริ่มต้นสถานะ Trend Following**
- ก่อน Squeeze (แถบกว้าง): **Mean Reversion** เหมาะสม

---

## 6. RSI Extreme Mean Reversion

### 6.1 การคำนวณ RSI

$$RSI = 100 - \frac{100}{1 + RS}$$

$$RS = \frac{\text{กำไรเฉลี่ยใน } n \text{ ช่วง}}{\text{ขาดทุนเฉลี่ยใน } n \text{ ช่วง}}$$

### 6.2 ระดับ RSI สำหรับ Mean Reversion

| ค่า RSI | สถานะ | สัญญาณ |
|---|---|---|
| RSI < 20 | Oversold สุดขีด | Long แรง |
| 20 <= RSI < 30 | Oversold | Long |
| 30 <= RSI < 70 | กลาง | ไม่มีสัญญาณ |
| 70 <= RSI < 80 | Overbought | Short |
| RSI > 80 | Overbought สุดขีด | Short แรง |

### 6.3 RSI Divergence สำหรับ Mean Reversion

**Bullish Divergence (สัญญาณ Long):**
- ราคาทำจุดต่ำสุดใหม่ที่ต่ำกว่า
- RSI ทำจุดต่ำสุดที่สูงขึ้น
- บ่งชี้แรงขายอ่อนลง; มีโอกาสกลับตัวขึ้น

**Bearish Divergence (สัญญาณ Short):**
- ราคาทำจุดสูงสุดใหม่ที่สูงขึ้น
- RSI ทำจุดสูงสุดที่ต่ำลง
- บ่งชี้แรงซื้ออ่อนลง; มีโอกาสกลับตัวลง

---

## 7. Half-Life ของ Mean Reversion

### 7.1 คำจำกัดความและสูตร

Half-Life ของ Mean Reversion คือเวลาที่คาดว่ากระบวนการจะกลับมาครึ่งทางสู่ค่าเฉลี่ยจากระดับปัจจุบัน

จากแบบจำลอง AR(1) แบบ Discrete: $X_t = a + \phi X_{t-1} + \epsilon_t$:

$$t_{half} = -\frac{\ln(2)}{\ln(\phi)}$$

โดยที่ $\phi = e^{-\theta \Delta t}$ คือสัมประสิทธิ์ AR(1)

ในรูปของพารามิเตอร์ความเร็ว OU $\theta$:

$$t_{half} = \frac{\ln(2)}{\theta}$$

### 7.2 ขั้นตอนการประมาณค่า

```
Algorithm: Half-Life Estimation

INPUT: price_series P[] of length T

1. Compute log prices: x = ln(P)
2. Compute first differences: dx = x[1:] - x[:-1]
3. Compute lagged levels: x_lag = x[:-1]
4. Run OLS regression: dx = alpha + beta * x_lag + epsilon
5. Extract coefficient: phi = 1 + beta
   (Note: beta should be negative for mean reversion)
6. Compute half-life:
   IF beta < 0:
       half_life = -ln(2) / ln(1 + beta)
   ELSE:
       half_life = infinity  # Not mean-reverting

OUTPUT: half_life (in units of the data frequency)
```

### 7.3 การตีความ Half-Life

| Half-Life | การตีความ | แนวทางการเทรด |
|---|---|---|
| 1-5 แท่ง | Mean Reversion เร็วมาก | High-frequency, Stop แคบ |
| 5-20 แท่ง | Mean Reversion ปานกลาง | กลยุทธ์ Mean Reversion มาตรฐาน |
| 20-50 แท่ง | Mean Reversion ช้า | ถือครองนานขึ้น |
| 50-100 แท่ง | ช้ามาก | อาจเทรดไม่ได้ (ต้นทุนกัดกินกำไร) |
| > 100 แท่ง หรือ $\infty$ | ไม่มี Mean Reversion | หลีกเลี่ยงกลยุทธ์ Mean Reversion |

### 7.4 การใช้ Half-Life เลือกพารามิเตอร์

Half-Life บอกโดยตรงถึง:
1. **Lookback Period**: ใช้ $n \approx 2 \times t_{half}$ ถึง $4 \times t_{half}$
2. **ระยะเวลาถือครองที่คาดหวัง**: ระยะเวลาเทรดเฉลี่ย $\approx t_{half}$
3. **Stop-Loss ตามเวลา**: หากไม่กลับตัวภายใน $3 \times t_{half}$, thesis อาจผิด
4. **เป้าหมายกำไร**: ตั้งเป้าจับการกลับตัวภายใน $1 \times t_{half}$

---

## 8. การเลือก Lookback Period ที่เหมาะสม

### 8.1 Lookback Dilemma

- **สั้นเกินไป**: ประมาณค่ามีสัญญาณรบกวน สัญญาณหลอกบ่อย
- **ยาวเกินไป**: ปรับตัวช้าต่อสภาวะตลาดที่เปลี่ยน รวมข้อมูลที่ไม่เกี่ยวข้อง

### 8.2 วิธีเลือก Lookback Period

**วิธีที่ 1: ตาม Half-Life**

$$n_{optimal} = \text{round}(2 \times t_{half})$$

**วิธีที่ 2: Information Criterion (AIC/BIC)**

$$AIC(n) = 2k - 2\ln(\hat{L}_n)$$
$$BIC(n) = k\ln(T) - 2\ln(\hat{L}_n)$$

เลือก $n$ ที่ทำให้ AIC หรือ BIC ต่ำสุด

**วิธีที่ 3: Rolling Walk-Forward Optimization**

```
Algorithm: Walk-Forward Lookback Selection

INPUT: price_data, candidate_lookbacks = [10, 15, 20, 30, 50, 75, 100]

FOR each lookback n in candidate_lookbacks:
    FOR each walk-forward window w:
        training_data = price_data[w - train_size : w]
        test_data = price_data[w : w + test_size]
        model = fit_mean_reversion(training_data, lookback=n)
        sharpe = backtest_mean_reversion(model, test_data)
        record(n, w, sharpe)

optimal_n = argmax_n(mean_sharpe(n))

OUTPUT: optimal_n
```

### 8.3 Lookback ที่แนะนำตามสินทรัพย์และกรอบเวลา

| ประเภทสินทรัพย์ | กรอบเวลา | Lookback ที่แนะนำ | เหตุผล |
|---|---|---|---|
| Forex คู่หลัก | H1 | 20-50 แท่ง | ~1-2 วันเทรด |
| Forex คู่หลัก | H4 | 20-30 แท่ง | ~3-5 วันเทรด |
| Forex คู่หลัก | D1 | 15-25 แท่ง | ~3-5 สัปดาห์ |
| BTC/USDT | H1 | 15-30 แท่ง | ผันผวนสูง รอบเร็ว |
| BTC/USDT | H4 | 20-40 แท่ง | 3-7 วัน |
| Altcoins | H1 | 10-20 แท่ง | รอบ Mean Reversion เร็วมาก |
| Altcoins | H4 | 15-30 แท่ง | 2-5 วัน |

---

## 9. การประยุกต์ใช้กับ Forex และคริปโต

### 9.1 Forex Mean Reversion

**คู่เงินที่ดีที่สุดสำหรับ Mean Reversion:**

| คู่เงิน | Hurst Exponent (ทั่วไป) | Half-Life (H4) | ความเหมาะสม |
|---|---|---|---|
| EUR/CHF | 0.35-0.42 | 8-15 แท่ง | ดีเยี่ยม |
| EUR/GBP | 0.38-0.45 | 10-20 แท่ง | ดีมาก |
| AUD/NZD | 0.36-0.43 | 8-18 แท่ง | ดีมาก |
| USD/CAD | 0.40-0.48 | 12-25 แท่ง | ดี |
| EUR/USD | 0.42-0.52 | 15-30 แท่ง | ปานกลาง (ขึ้นกับ Regime) |
| GBP/JPY | 0.50-0.60 | 25-50+ แท่ง | ไม่ดี (แนวโน้มเด่น) |

**ทำไมคู่เงินเหล่านี้จึงกลับตัวหาค่าเฉลี่ย:**
- **EUR/CHF**: การแทรกแซงของ SNB ในอดีต; ความสัมพันธ์ทางเศรษฐกิจ
- **EUR/GBP**: การรวมตัวทางเศรษฐกิจอย่างใกล้ชิด นโยบายการเงินที่สัมพันธ์กัน
- **AUD/NZD**: เศรษฐกิจส่งออกสินค้าโภคภัณฑ์คล้ายกัน ปัจจัยพื้นฐานสัมพันธ์กัน

### 9.2 คริปโต Mean Reversion

**ข้อพิจารณาเฉพาะคริปโต:**

1. **ตลาด 24/7**: ไม่มี Gap ข้ามคืน โอกาส Mean Reversion ต่อเนื่อง
2. **ความผันผวนสูง**: ต้องใช้แถบกว้างขึ้น; ศักยภาพกำไรต่อเทรดมากขึ้น
3. **Funding Rate Mean Reversion**: Funding Rate ของ Perpetual Futures กลับตัวหาศูนย์
4. **ราคาเฉพาะตลาด**: สเปรดระหว่างตลาดกลับตัวหาค่าเฉลี่ย (Cross-exchange Arb)
5. **เมตริก On-Chain**: NVT Ratio, MVRV Z-Score เป็นสัญญาณ Mean Reversion

**กลยุทธ์ Funding Rate Mean Reversion:**
- เมื่อ Funding Rate สูงผิดปกติ (> 0.1%): Long Spot, Short Perp (เก็บ Funding)
- เมื่อ Funding Rate ต่ำผิดปกติ (< -0.1%): Short Spot, Long Perp (เก็บ Funding)
- ออกเมื่อ Funding Rate กลับสู่ปกติใกล้ศูนย์

---

## 10. ลอจิกหลัก --- การเข้า/ออก

### 10.1 ลอจิกการเข้า Mean Reversion แบบรวม

```
Algorithm: Composite Mean Reversion Entry

INDICATORS:
    z_score = (close - SMA(close, lookback)) / STD(close, lookback)
    bb_upper = SMA(close, bb_period) + bb_std * STD(close, bb_period)
    bb_lower = SMA(close, bb_period) - bb_std * STD(close, bb_period)
    bb_mid = SMA(close, bb_period)
    rsi = RSI(close, rsi_period)
    kc_upper = EMA(close, kc_period) + kc_mult * ATR(atr_period)
    kc_lower = EMA(close, kc_period) - kc_mult * ATR(atr_period)
    adf_pvalue = adf_test(close[-lookback:])
    hurst = hurst_exponent(close[-100:])
    half_life = calc_half_life(close[-lookback:])

REGIME FILTER:
    is_mean_reverting = (hurst < 0.45) AND (adf_pvalue < 0.05)
    is_range_bound = ADX(14) < 25
    regime_ok = is_mean_reverting AND is_range_bound

LONG ENTRY (ทุกเงื่อนไข):
    1. regime_ok = True
    2. z_score < -entry_threshold (e.g., -2.0)
    3. close < bb_lower
    4. rsi < rsi_oversold (e.g., 30)
    5. NOT in_squeeze (BB inside KC)
    6. volume_declining (last 3 bars)
    7. half_life < max_half_life (e.g., 50)
    
    ENTRY_PRICE = close (or limit at bb_lower)
    STOP_LOSS = close - sl_multiplier * ATR(14)
    TAKE_PROFIT = bb_mid
    POSITION_SIZE = risk_per_trade * account / (close - stop_loss)
```

### 10.2 ลอจิกการออก

```
Algorithm: Mean Reversion Exit Management

ON EACH BAR (while position is open):
    z_score = current z-score
    bars_held = current_bar - entry_bar
    
    # 1. Target Hit
    IF position == LONG AND close >= take_profit:
        EXIT - "Target reached (mean reversion complete)"
        
    # 2. Stop Loss Hit
    IF position == LONG AND close <= stop_loss:
        EXIT - "Stop loss hit (mean reversion failed)"
    
    # 3. Mean Reversion Failure (Z-Score Expansion)
    IF position == LONG AND z_score < -stop_z_threshold:
        EXIT - "Z-score expanded beyond failure threshold"
    
    # 4. Time Stop
    IF bars_held > max_holding_period:
        EXIT - "Maximum holding period exceeded"
        # max_holding_period = 3 * half_life
    
    # 5. Regime Change
    IF NOT regime_ok:
        EXIT - "Regime changed to trending"
    
    # 6. Trailing Stop (after 50% profit captured)
    IF current_pnl > 0.5 * (take_profit - entry_price) * quantity:
        trailing_stop = entry_price + 0.3 * (close - entry_price)
        IF position == LONG AND close < trailing_stop:
            EXIT - "Trailing stop hit"
```

---

## 11. ข้อกำหนดทางเทคนิค

### 11.1 การตั้งค่าตัวบ่งชี้

```yaml
mean_reversion_indicators:
  bollinger_bands:
    period: 20
    std_dev: 2.0
    source: close
    
  z_score:
    lookback: 20  # calibrated to half-life
    source: close
    
  rsi:
    period: 14
    overbought: 70
    oversold: 30
    
  keltner_channel:
    ema_period: 20
    atr_period: 14
    multiplier: 2.0
    
  adf_test:
    lookback: 100
    significance: 0.05
    
  hurst_exponent:
    lookback: 100
    min_lag: 10
    max_lag: 50
    
  half_life:
    lookback: 100
    recalculation_frequency: 20
```

### 11.2 การให้คะแนนความแข็งแกร่งของสัญญาณ

```yaml
signal_scoring:
  components:
    z_score_signal:
      weight: 0.30
      score: min(1.0, (|z| - entry_z) / (stop_z - entry_z))
      
    rsi_signal:
      weight: 0.20
      score:
        long: (30 - RSI) / 30 if RSI < 30 else 0
        short: (RSI - 70) / 30 if RSI > 70 else 0
        
    bollinger_signal:
      weight: 0.20
      
    volume_signal:
      weight: 0.15
      score: 1.0 if volume_declining else 0.5 if volume_neutral else 0.0
      
    regime_signal:
      weight: 0.15
      score: (0.5 - hurst) / 0.5
      
  total_score: sum(weight_i * score_i)
  minimum_score_to_trade: 0.60
  full_position_score: 0.80
```

---

## 12. แบบจำลองทางคณิตศาสตร์

### 12.1 กำไรที่คาดหวังจาก OU Process

$$E[\text{Profit}] = (X_0 - \mu) \times Q \times P(\text{reversion before stop})$$

**ความน่าจะเป็นของการกลับตัวก่อน Stop:**

$$P(\text{reversion}) = \frac{\Phi\left(\frac{X_0 - X_s}{\sigma/\sqrt{2\theta}}\right)}{\Phi\left(\frac{\mu - X_s}{\sigma/\sqrt{2\theta}}\right)}$$

### 12.2 Kelly Criterion สำหรับ Mean Reversion

$$f^* = \frac{p \times b - q}{b}$$

โดยที่:
- $p$ = ความน่าจะเป็นของการชนะ (Mean Reversion สำเร็จ)
- $q = 1 - p$ = ความน่าจะเป็นของการแพ้ (โดน Stop)
- $b$ = อัตราส่วนกำไร/ขาดทุน

**Half-Kelly (แนะนำ):** $f = f^*/2$

---

## 13. พารามิเตอร์ความเสี่ยง

### 13.1 การกำหนดขนาดตำแหน่ง

**ขนาดตำแหน่งตาม ATR:**

$$\text{Position Size} = \frac{\text{Account} \times \text{Risk\%}}{ATR(14) \times k_{SL}}$$

| ระดับความเสี่ยง | ความเสี่ยงต่อเทรด | สถานะพร้อมกันสูงสุด | ความเสี่ยงพอร์ตสูงสุด |
|---|---|---|---|
| อนุรักษ์นิยม | 0.5% | 3 | 1.5% |
| ปานกลาง | 1.0% | 4 | 4.0% |
| เชิงรุก | 2.0% | 5 | 10.0% |

### 13.2 พารามิเตอร์ Stop Loss

| ประเภท Stop | สูตร | ค่าทั่วไป |
|---|---|---|
| ตาม ATR | Entry $\pm k \times ATR(14)$ | $k = 1.5$ ถึง $2.5$ |
| ตาม Z-Score | Z-Score เกิน $\pm z_{stop}$ | $z_{stop} = 3.0$ ถึง $4.0$ |
| ตามเปอร์เซ็นต์ | Entry $\pm p\%$ | $p = 1.5\%$ ถึง $3.0\%$ |
| ตามเวลา | ออกหลัง $n$ แท่ง | $n = 3 \times t_{half}$ |

### 13.3 พารามิเตอร์ Take Profit

| ประเภทเป้าหมาย | สูตร | หมายเหตุ |
|---|---|---|
| เป้าหมายที่ค่าเฉลี่ย | $BB_{mid}$ หรือ $SMA(n)$ | ใช้บ่อยที่สุดสำหรับ Pure Mean Reversion |
| ครึ่งทางหาค่าเฉลี่ย | Entry + $0.5 \times (Mean - Entry)$ | อนุรักษ์นิยม; ทำกำไรครึ่งที่ 50% |
| แถบตรงข้าม | $BB_{upper}$ (สำหรับ Long) | เชิงรุก; รอการแกว่งตัวเต็ม |
| ตาม Z-Score | $z = 0$ | ปรับมาตรฐานสู่ Z-Score = 0 |

### 13.4 Drawdown สูงสุดที่คาดหวัง

$$DD_{max} = 1 - (1 - R_{loss})^{n_{consecutive}}$$

สำหรับ $R_{loss}$ = 1% ต่อเทรด และ $n_{consecutive}$ = 8 ขาดทุนต่อเนื่อง:

$$DD_{max} = 1 - (1 - 0.01)^{8} = 1 - 0.9227 = 7.73\%$$

---

## 14. ขั้นตอนการทำงาน

### 14.1 แผนภาพขั้นตอนการทำงาน

```
┌─────────────────────────────────────────────┐
│       MEAN REVERSION EXECUTION FLOW         │
├─────────────────────────────────────────────┤
│                                             │
│  1. รับข้อมูล (DATA INGESTION)               │
│     ├─ รับแท่งเทียนใหม่ (OHLCV)              │
│     └─ อัปเดตบัฟเฟอร์ประวัติราคา             │
│                                             │
│  2. คำนวณตัวบ่งชี้ (INDICATORS)             │
│     ├─ Bollinger Bands (20, 2.0)            │
│     ├─ Z-Score (rolling lookback)           │
│     ├─ RSI (14)                             │
│     ├─ Keltner Channels (20, 2.0)           │
│     ├─ ATR (14)                             │
│     └─ ADX (14)                             │
│                                             │
│  3. ตรวจจับ Regime                          │
│     ├─ Hurst Exponent (< 0.48?)             │
│     ├─ ADF Test (p < 0.05?)                 │
│     ├─ Half-Life (สมเหตุสมผล?)              │
│     ├─ ADX (< 25? แกว่งตัวในกรอบ)           │
│     └─ Squeeze Detection                    │
│     IF regime ไม่เหมาะ → ข้ามไปขั้นตอน 5    │
│                                             │
│  4. สร้างสัญญาณ (SIGNAL GENERATION)         │
│     ├─ ตรวจ Z-Score สุดขีด                   │
│     ├─ ตรวจ BB touches                       │
│     ├─ ตรวจ RSI สุดขีด                       │
│     ├─ ตรวจรูปแบบปริมาณ                      │
│     ├─ คะแนนสัญญาณรวม                       │
│     └─ IF คะแนน >= 0.60 → สร้างสัญญาณ      │
│                                             │
│  5. จัดการสถานะ (POSITION MANAGEMENT)       │
│     ├─ ตรวจ Stop Loss (ATR-based)           │
│     ├─ ตรวจ Take Profit (BB mid)            │
│     ├─ ตรวจ Z-Score Failure                 │
│     ├─ ตรวจ Time Stop (3x half-life)        │
│     ├─ ตรวจ Regime Change                   │
│     └─ ตรวจ Trailing Stop                   │
│                                             │
│  6. ดำเนินการ (EXECUTION)                   │
│     ├─ กำหนดขนาดตำแหน่ง (risk-based)        │
│     ├─ วางคำสั่ง (limit or market)           │
│     └─ อัปเดตการติดตามและบันทึก              │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 15. วิธีการทดสอบย้อนหลัง

### 15.1 เมตริกผลการดำเนินงาน

| เมตริก | สูตร | เป้าหมาย |
|---|---|---|
| Net Sharpe Ratio | $(R_{ann} - R_f) / \sigma_{ann}$ | > 1.5 |
| Sortino Ratio | $(R_{ann} - R_f) / \sigma_{downside}$ | > 2.0 |
| Drawdown สูงสุด | Peak-to-Trough ที่ใหญ่ที่สุด | < 15% |
| Calmar Ratio | $R_{ann} / |DD_{max}|$ | > 1.0 |
| Win Rate | เทรดที่ชนะ / เทรดทั้งหมด | > 55% |
| Profit Factor | กำไรรวม / ขาดทุนรวม | > 1.5 |
| เทรดเฉลี่ย | กำไรสุทธิ / จำนวนเทรด | > 2 เท่าของต้นทุนเฉลี่ย |
| Recovery Factor | กำไรสุทธิ / Drawdown สูงสุด | > 3.0 |
| เทรดต่อเดือน | ความถี่เฉลี่ยรายเดือน | 5-30 |

---

## 16. เอกสารอ้างอิง

### บทความวิชาการ

1. **Uhlenbeck, G.E., & Ornstein, L.S.** (1930). "On the Theory of Brownian Motion." *Physical Review*, 36, 823-841.
2. **Dickey, D.A., & Fuller, W.A.** (1979). "Distribution of the Estimators for Autoregressive Time Series with a Unit Root." *JASA*, 74(366), 427-431.
3. **Lo, A.W., & MacKinlay, A.C.** (1988). "Stock Market Prices Do Not Follow Random Walks." *Review of Financial Studies*, 1(1), 41-66.
4. **Hurst, H.E.** (1951). "Long-Term Storage Capacity of Reservoirs." *Transactions ASCE*, 116, 770-808.
5. **Poterba, J.M., & Summers, L.H.** (1988). "Mean Reversion in Stock Prices." *Journal of Financial Economics*, 22(1), 27-59.

### แหล่งข้อมูลสำหรับผู้ปฏิบัติ

6. **Bollinger, J.** (2001). *Bollinger on Bollinger Bands*. McGraw-Hill.
7. **Ernie Chan.** (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley.
8. **Ernie Chan.** (2009). *Quantitative Trading*. Wiley.

---

## ภาคผนวก A: สูตรอ้างอิงด่วน

| สูตร | นิพจน์ |
|---|---|
| กระบวนการ OU | $dX_t = \theta(\mu - X_t)dt + \sigma dW_t$ |
| ความแปรปรวนคงที่ | $\sigma^2_{stat} = \sigma^2 / (2\theta)$ |
| Half-Life | $t_{half} = -\ln(2) / \ln(\phi)$ |
| Z-Score | $z = (P - \bar{P}_n) / \sigma_n$ |
| Bollinger Upper | $BB_{upper} = SMA(n) + k\sigma$ |
| Bollinger Lower | $BB_{lower} = SMA(n) - k\sigma$ |
| %B | $\%B = (P - BB_{lower})/(BB_{upper} - BB_{lower})$ |
| RSI | $RSI = 100 - 100/(1+RS)$ |
| Keltner Upper | $KC_{upper} = EMA(n) + k \times ATR(m)$ |
| ขนาดตำแหน่ง | $Q = (\text{Account} \times R\%) / (ATR \times k_{SL})$ |

---

*เอกสารนี้เป็นส่วนหนึ่งของฐานความรู้ระบบเทรด AI หลายตัวแทน กลยุทธ์ Mean Reversion มีประสิทธิภาพสูงสุดในสภาวะตลาดที่แกว่งตัวในกรอบ และควรใช้ร่วมกับตัวกรอง Regime เพื่อหลีกเลี่ยงการขาดทุนในช่วงที่มีแนวโน้ม*
