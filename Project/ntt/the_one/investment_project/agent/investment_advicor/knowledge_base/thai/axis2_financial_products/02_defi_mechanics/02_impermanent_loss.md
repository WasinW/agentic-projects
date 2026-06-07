# Impermanent Loss — เอกสารกลไกฉบับสมบูรณ์

> **Axis 2 — ผลิตภัณฑ์ทางการเงิน | โมดูล 02 — กลไก DeFi**
> เวอร์ชัน: 2.0.0 | อัปเดตล่าสุด: 2026-04-12

---

## สารบัญ

1. [การอนุมาน IL](#1-การอนุมาน-il)
2. [IL ที่ขยายสำหรับ Concentrated LP](#2-il-ที่ขยายสำหรับ-concentrated-lp)
3. [กลยุทธ์การเฮดจ์](#3-กลยุทธ์การเฮดจ์)
4. [การวิเคราะห์จุดคุ้มทุน](#4-การวิเคราะห์จุดคุ้มทุน)
5. [เครื่องมือคำนวณและ Pseudocode](#5-เครื่องมือคำนวณและ-pseudocode)
6. [เอกสารอ้างอิง](#6-เอกสารอ้างอิง)

---

## 1. การอนุมาน IL

### 1.1 Impermanent Loss คืออะไร?

Impermanent Loss (IL) คือความแตกต่างระหว่างมูลค่าของสินทรัพย์ที่ถือใน liquidity pool เทียบกับมูลค่าหากเพียงแค่ถือ (HODL) สินทรัพย์เหล่านั้น เรียกว่า "ชั่วคราว" เพราะ IL จะหายไปถ้าราคากลับมาที่เดิม

### 1.2 สูตร IL สำหรับ Constant Product AMM

สำหรับ pool 50/50 ให้ $r$ = อัตราส่วนราคาใหม่ต่อเก่า ($r = P_1/P_0$):

$$IL(r) = \frac{2\sqrt{r}}{1+r} - 1$$

### 1.3 ตาราง IL ตามการเปลี่ยนแปลงราคา

| การเปลี่ยนราคา | อัตราส่วน $r$ | IL |
|:-------------:|:-------------:|:---:|
| -50% | 0.50 | -5.72% |
| -25% | 0.75 | -1.03% |
| -10% | 0.90 | -0.14% |
| 0% | 1.00 | 0% |
| +10% | 1.10 | -0.14% |
| +25% | 1.25 | -0.60% |
| +50% | 1.50 | -2.02% |
| +100% | 2.00 | -5.72% |
| +200% | 3.00 | -13.40% |
| +500% | 6.00 | -30.06% |

### 1.4 การอนุมานทางคณิตศาสตร์

ให้เริ่มด้วย pool ที่มี reserves $(x_0, y_0)$ ณ ราคา $P_0 = y_0/x_0$

หลังราคาเปลี่ยนเป็น $P_1 = r \cdot P_0$:

$$x_1 = x_0 / \sqrt{r}, \quad y_1 = y_0 \cdot \sqrt{r}$$

มูลค่า LP pool:

$$V_{LP} = x_1 \cdot P_1 + y_1 = 2y_0\sqrt{r}$$

มูลค่า HODL:

$$V_{HODL} = x_0 \cdot P_1 + y_0 = y_0(r + 1)$$

$$IL = \frac{V_{LP}}{V_{HODL}} - 1 = \frac{2\sqrt{r}}{1+r} - 1$$

---

## 2. IL ที่ขยายสำหรับ Concentrated LP

### 2.1 IL ของ Uniswap V3

สำหรับ concentrated liquidity ในช่วง $[p_a, p_b]$ IL จะถูก amplify:

$$IL_{V3}(r) = IL_{V2}(r) \times \frac{\sqrt{p_b} - \sqrt{p_a}}{\sqrt{p_b} - \sqrt{p}} \times \frac{\sqrt{p} - \sqrt{p_a}}{\sqrt{p_b} - \sqrt{p_a}}$$

**กฎง่าย:** ช่วงที่แคบกว่า = ค่าธรรมเนียมมากกว่า แต่ IL ที่ขยายมากกว่า

### 2.2 ตัวอย่าง

สำหรับช่วง +/- 10% ($p_a = 0.9P$, $p_b = 1.1P$):
- ประสิทธิภาพทุน ~5x
- IL ที่ขยาย ~5x เช่นกัน

---

## 3. กลยุทธ์การเฮดจ์

### 3.1 Delta Hedging

เฮดจ์ด้วย perpetual short เพื่อหักล้าง directional exposure:

$$\Delta_{LP} = \frac{x_1 \cdot P_1}{V_{LP}} = \frac{1}{1 + \sqrt{r}}$$

### 3.2 Options Hedging

ซื้อ put options เพื่อป้องกัน downside:

$$\text{Cost} = \text{Put Premium} \times \text{Notional}$$

### 3.3 Dynamic Rebalancing

ปรับ hedge ทุกครั้งที่ delta เปลี่ยนอย่างมีนัยสำคัญ:

```python
def rebalance_hedge(position, current_price, threshold=0.05):
    current_delta = calculate_lp_delta(position, current_price)
    hedge_delta = position.hedge_size / position.total_value
    
    if abs(current_delta - hedge_delta) > threshold:
        adjustment = current_delta - hedge_delta
        if adjustment > 0:
            # Need more short hedge
            open_short(adjustment * position.total_value)
        else:
            # Reduce short hedge
            close_short(abs(adjustment) * position.total_value)
```

---

## 4. การวิเคราะห์จุดคุ้มทุน

### 4.1 สมการจุดคุ้มทุน

LP position ทำกำไรเมื่อ:

$$\text{Fee Income} > |IL|$$

$$\frac{L_{pos}}{L_{total}} \times V \times f \times T > |IL(r)| \times V_{LP}$$

### 4.2 เวลาจุดคุ้มทุน

$$T_{breakeven} = \frac{|IL(r)| \times V_{LP}}{\frac{L_{pos}}{L_{total}} \times V_{daily} \times f}$$

---

## 5. เครื่องมือคำนวณและ Pseudocode

```python
def calculate_il(price_ratio: float) -> float:
    """Calculate IL for constant product AMM."""
    r = price_ratio
    return 2 * math.sqrt(r) / (1 + r) - 1

def calculate_il_concentrated(price_ratio, p_a, p_b, current_price):
    """Calculate amplified IL for concentrated liquidity."""
    base_il = calculate_il(price_ratio)
    concentration_factor = (math.sqrt(p_b) - math.sqrt(p_a)) / (math.sqrt(current_price) - math.sqrt(p_a))
    return base_il * concentration_factor

def breakeven_analysis(pool_tvl, daily_volume, fee_rate, position_share, il):
    """Calculate days to breakeven."""
    daily_fees = position_share * daily_volume * fee_rate
    return abs(il * pool_tvl * position_share) / daily_fees
```

---

## 6. เอกสารอ้างอิง

1. "Uniswap v3: A concentrated liquidity AMM" — Uniswap Labs
2. "Impermanent Loss in Uniswap v3" — Guillaume Lambert
3. "On-Chain Options as Hedge for LP Positions" — Various research

---

> **เอกสารถัดไป**: [03_yield_strategies.md](./03_yield_strategies.md) — กลยุทธ์ผลตอบแทน
