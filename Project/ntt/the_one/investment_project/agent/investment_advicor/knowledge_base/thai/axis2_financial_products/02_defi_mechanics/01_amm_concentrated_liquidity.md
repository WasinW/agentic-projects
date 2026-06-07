# AMM และ Concentrated Liquidity ��� เอกสารกลไกฉบับสมบูรณ์

> **Axis 2 — ผลิตภัณฑ์ทางการเงิน | โมดูล 02 — กลไก DeFi**
> เวอร์ชัน: 2.0.0 | อัปเดตล่าสุด: 2026-04-12
> การจัดประเภท: KNOWLEDGE BASE — ระบบเทรด AI แบบ MULTI-AGENT

---

## สารบัญ

1. [คณิตศาสตร์ AMM พื้นฐาน](#1-คณิตศาสตร์-amm-พื้นฐาน)
2. [Constant Product Market Maker (CPMM)](#2-constant-product-market-maker)
3. [StableSwap Invariant (Curve)](#3-stableswap-invariant)
4. [Weighted Pools (Balancer)](#4-weighted-pools)
5. [Uniswap V3 Concentrated Liquidity](#5-uniswap-v3-concentrated-liquidity)
6. [กลยุทธ์ LP](#6-กลยุทธ์-lp)
7. [JIT Liquidity](#7-jit-liquidity)
8. [พารามิเตอร์ความเสี่ยง](#8-พารามิเตอร์ความเสี่ยง)
9. [ขั้นตอนการทำงาน](#9-ขั้นตอนการทำงาน)
10. [เอกสารอ้างอิง](#10-เอกสารอ้างอิง)

---

## 1. คณิตศาสตร์ AMM พื้นฐาน

### 1.1 AMM คืออะไร?

Automated Market Maker (AMM) เป็นโปรโตคอล smart contract ที่ให้สภาพคล่องสำหรับการเทรดโดยไม่ต้องมี order book แบบดั้งเดิม แทนที่จะจับคู่ผู้ซื้อกับผู้ขาย AMM ใช้สูตรทางคณิตศาสตร์เพื่อกำหนดราคาตามอัตราส่วนสินทรัพย์ใน liquidity pool

### 1.2 ส่วนประกอบหลัก

- **Liquidity Pool:** สัญญาที่ถือคู่โทเคน (เช่น ETH/USDC)
- **Liquidity Providers (LPs):** ฝากสินทรัพย์เข้าพูลและรับค่าธรรมเนียม
- **Invariant Function:** สูตรที่ควบคุมความสัมพันธ์ระหว่างทุนสำรอง
- **Trading Fee:** ค่าธรรมเนียมต่อสวอปที่ไปยัง LPs

---

## 2. Constant Product Market Maker

### 2.1 สูตรหลัก (Uniswap V2)

$$x \cdot y = k$$

โดยที่:
- $x$ = ทุนสำรองของ token X
- $y$ = ทุนสำรองของ token Y
- $k$ = ค่าคงที่ (ผลคูณต้องคงเดิม)

### 2.2 ราคา

$$P_X = \frac{y}{x}$$

### 2.3 Price Impact ของการสวอป

สำหรับการซื้อ $\Delta x$ ของ token X:

$$\Delta y = \frac{y \cdot \Delta x}{x + \Delta x}$$

Price impact:

$$\text{Impact} = \frac{\Delta x}{x + \Delta x}$$

### 2.4 ข้อจำกัด

- ทุนไม่มีประสิทธิภาพ (สภาพคล่องกระจายจาก 0 ถึง infinity)
- Slippage สูงสำหรับเทรดใหญ่
- Impermanent loss สำหรับ LPs

---

## 3. StableSwap Invariant

### 3.1 สูตร Curve

$$A \cdot n^n \cdot \sum x_i + D = A \cdot D \cdot n^n + \frac{D^{n+1}}{n^n \cdot \prod x_i}$$

โดยที่:
- $A$ = amplification parameter (ควบคุมความ "แบน" ของ curve)
- $n$ = จำนวนโทเคนในพูล
- $D$ = total deposit amount
- $x_i$ = ทุนสำรองของโทเคน $i$

### 3.2 ข้อได้เปรียบ

- Slippage ต่ำมากสำหรับสินทรัพย์ที่มีราคาใกล้เคียง (stablecoins)
- ประสิทธิภาพทุนสูงกว่า CPMM สำหรับ correlated assets

---

## 4. Weighted Pools

### 4.1 สูตร Balancer

$$\prod_{i=1}^{n} B_i^{w_i} = k$$

โดยที่:
- $B_i$ = ยอดโทเคน $i$
- $w_i$ = น้ำหนักของโท��คน $i$ (ผลรวม = 1)

### 4.2 ราคา

$$P_{i/j} = \frac{B_j / w_j}{B_i / w_i}$$

---

## 5. Uniswap V3 Concentrated Liquidity

### 5.1 แนวคิดหลัก

แทนที่จะกระจายสภาพคล่องจาก 0 ถึง infinity Uniswap V3 ให้ LPs เลือกช่วงราคาที่จะวางสภาพคล่อง ทำให้ประสิทธิภาพทุนสูงขึ้นอย่างมาก

### 5.2 Virtual Reserves

สำหรับช่วงราคา $[p_a, p_b]$:

$$L = \frac{\Delta x}{\frac{1}{\sqrt{p}} - \frac{1}{\sqrt{p_b}}} = \frac{\Delta y}{\sqrt{p} - \sqrt{p_a}}$$

โดยที่ $L$ = liquidity

### 5.3 ประสิทธิภาพทุน

$$\text{Capital Efficiency} = \frac{\sqrt{p_b} \cdot \sqrt{p_a}}{\sqrt{p_b} - \sqrt{p_a}} \cdot \frac{2}{(\sqrt{p_b} + \sqrt{p_a})}$$

ตัวอย่าง: ช่วง +/- 5% ให้ประสิทธิภาพทุน ~10x เทียบกับ V2

### 5.4 Fee Tiers

| Fee Tier | ใช้สำหรับ | ตัวอย่าง |
|----------|----------|---------|
| 0.01% | Stablecoin pairs | USDC/USDT |
| 0.05% | Correlated pairs | ETH/stETH |
| 0.30% | Most pairs | ETH/USDC |
| 1.00% | Exotic pairs | Low-cap tokens |

### 5.5 Tick Math

ราคาถูกแบ่งเป็น ticks ที่ห่างกันตาม:

$$p(i) = 1.0001^i$$

แต่ละ tick แทน 1 basis point ของการเปลี่ยนแปลงราคา

---

## 6. กลยุทธ์ LP

### 6.1 กลยุทธ์ Passive (Wide Range)

- วางสภาพคล่องในช่วงกว้าง
- ต้องปรับน้อย
- ประสิทธิภาพทุนต่ำ
- ���หมาะกับสินทรัพย์ที่ผันผวนสูง

### 6.2 กลยุทธ์ Active (Narrow Range)

- วางสภาพคล่องในช่วงแคบรอบราคาปัจจุบัน
- ต้องปรับบ่อย (rebalance)
- ประสิทธิภาพทุนสูง
- เสี่ยง Impermanent Loss สูงกว่า
- เหมาะกับ stablecoin pairs หรือ correlated assets

### 6.3 การคำนวณค่าธรรมเนียม

$$\text{Fee Income} = \frac{L_{position}}{L_{total}} \times V_{daily} \times f$$

โดยที่:
- $L_{position}$ = liquidity ของสถานะเรา
- $L_{total}$ = liquidity รวมในช่วงราคาปัจจุบัน
- $V_{daily}$ = ปริมาณเทรดรายวัน
- $f$ = fee tier

---

## 7. JIT Liquidity

### 7.1 แนวคิด

Just-in-Time (JIT) Liquidity คือการเพิ่ม concentrated liquidity ใน Uniswap V3 pool ก่อนการเทรดใหญ่ (ที่เห็นใน mempool) แล้วถอนออกทันทีหลังจากนั้น

### 7.2 ขั้นตอน

```
1. สังเกตเห็น pending swap ใหญ่ใ�� mempool
2. เพิ่ม concentrated liquidity ในช่วงแคบรอบราคาปัจจุบัน
3. Swap ใหญ่ดำเนินการ จ่ายค่าธรรมเนียมให้ liquidity ของเรา
4. ถอน liquidity ออกทันที
5. กำไร = ค่าธรรมเนียมที่ได้ - ค่า gas
```

### 7.3 ข้อพิจ���รณา

- ต้อง front-run ผู้ให้สภาพคล่องรายอื่น
- เป็น MEV ที่เป็นกลาง (ไม่เบียดเบียนเทรดเดอร์)
- ต้องการ gas สูง (2 ธุรกรรม: mint + burn)

---

## 8. พารามิเตอร์ความเสี่ยง

| พารามิเตอร์ | ค่า | คำอธิบาย |
|------------|------|---------|
| ช่วงราคาสูงสุด | +/- 20% สำหรับ volatile pairs | ป้องกัน IL ที่รุนแรง |
| IL threshold | -5% | ออกหาก IL เกินเกณฑ์ |
| ความถี่ rebalance | เมื่อราคาใกล้ขอบ (5% จากขอบ) | รักษาให้อยู่ในช่วง |
| ขนาดสถานะสูงสุด | 10% ของทุน DeFi | กระจายความเสี่ยง |
| ค่า gas budget | < 15% ของผลตอบแทน | ให้แน่ใจว่าผลตอบแทนสุทธิเป็นบวก |

---

## 9. ขั้นตอนการทำงาน

```python
class AMMStrategyEngine:
    """AMM liquidity provision strategy engine."""
    
    async def manage_position(self, pool, position):
        current_price = await pool.get_current_price()
        
        # Check if position is in range
        if not position.is_in_range(current_price):
            await self.rebalance(pool, position, current_price)
            return
        
        # Check if near boundary
        distance = position.distance_to_boundary(current_price)
        if distance < 0.05:  # Within 5% of boundary
            await self.rebalance(pool, position, current_price)
            return
        
        # Calculate current IL
        il = self.calculate_il(position, current_price)
        if il < -0.05:  # IL exceeds 5%
            await self.exit_position(position)
            return
        
        # Calculate fee APR
        fee_apr = await self.estimate_fee_apr(pool, position)
        if fee_apr < self.min_acceptable_apr:
            await self.rebalance_to_optimal_range(pool, position)
    
    async def rebalance(self, pool, position, current_price):
        """Remove and re-add liquidity in new range."""
        await pool.remove_liquidity(position)
        new_range = self.calculate_optimal_range(pool, current_price)
        await pool.add_liquidity(new_range, position.value)
```

---

## 10. เอกสารอ้างอิง

1. Adams, H., et al. (2021). "Uniswap v3 Core." https://uniswap.org/whitepaper-v3.pdf
2. Egorov, M. (2019). "StableSwap." Curve Finance Whitepaper.
3. Martinelli, F., Mushegian, N. (2019). Balancer Whitepaper.
4. Dan Robinson, "Uniswap V3 LP as a Derivative Position."
5. Guillaume Lambert, "Concentrated Liquidity and Impermanent Loss."

---

> **เอกสารถัดไป**: [02_impermanent_loss.md](./02_impermanent_loss.md) — การวิเคราะห์ Impermanent Loss
