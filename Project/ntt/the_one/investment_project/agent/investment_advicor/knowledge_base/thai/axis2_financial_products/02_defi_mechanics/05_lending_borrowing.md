# กลไกการให้กู้และยืม (Lending & Borrowing) — เอกสารกลไกฉบับสมบูรณ์

> **Axis 2 — ผลิตภัณฑ์ทางการเงิน | โมดูล 02 — กลไก DeFi**
> เวอร์ชัน: 2.0.0 | อัปเดตล่าสุด: 2026-04-12

---

## สารบัญ

1. [แบบจำลองอัตราดอกเบี้ย](#1-แบบจำลองอัตราดอกเบี้ย)
2. [Utilization Rate](#2-utilization-rate)
3. [กลไกการ Liquidation](#3-กลไกการ-liquidation)
4. [Recursive Lending (Leveraged Lending)](#4-recursive-lending)
5. [Health Factor และการจัดการสถานะ](#5-health-factor-และการจัดการสถานะ)
6. [E-Mode (Efficiency Mode)](#6-e-mode)
7. [พารามิเตอร์ความเสี่ยง](#7-พารามิเตอร์ความเสี่ยง)
8. [ขั้นตอนการทำงาน](#8-ขั้นตอนการทำงาน)
9. [เอกสารอ้างอิง](#9-เอกสารอ้างอิง)

---

## 1. แบบจำลองอัตราดอกเบี้ย

### 1.1 แบบจำลองแบบ Kinked (Aave/Compound)

อัตราดอกเบี้ยเปลี่ยนตาม utilization:

**เมื่อ $U < U_{optimal}$:**

$$R_{borrow} = R_{base} + \frac{U}{U_{optimal}} \times R_{slope1}$$

**เมื่อ $U \geq U_{optimal}$:**

$$R_{borrow} = R_{base} + R_{slope1} + \frac{U - U_{optimal}}{1 - U_{optimal}} \times R_{slope2}$$

โดยที่:
- $U$ = utilization rate
- $U_{optimal}$ = จุดเปลี่ยน (ปกติ 80-90%)
- $R_{base}$ = อัตราฐาน
- $R_{slope1}$ = ความชัน 1 (ก่อนจุดเปลี่ยน)
- $R_{slope2}$ = ความชัน 2 (หลังจุดเปลี่ยน, ชันมาก)

### 1.2 ตัวอย่างพารามิเตอร์ (Aave V3 — USDC)

| พารามิเตอร์ | ค่า |
|------------|------|
| $R_{base}$ | 0% |
| $R_{slope1}$ | 3.5% |
| $R_{slope2}$ | 60% |
| $U_{optimal}$ | 90% |

### 1.3 อัตราดอกเบี้ยผู้ฝาก (Supply Rate)

$$R_{supply} = R_{borrow} \times U \times (1 - \text{Reserve Factor})$$

---

## 2. Utilization Rate

### 2.1 คำจำกัดความ

$$U = \frac{\text{Total Borrows}}{\text{Total Deposits}}$$

### 2.2 ความสำคัญ

- $U$ ต่ำ = สภาพคล่องเยอะ, อัตราดอกเบี้ยต่ำ, ผู้ฝากได้น้อย
- $U$ สูง = สภาพคล่องน้อย, อัตราดอกเบี้ยสูง, เสี่ยงสภาพคล่อง
- $U$ เกิน optimal = อัตราพุ่งสูงเพื่อจูงใจให้ฝากเพิ่ม/กู้คืน

---

## 3. กลไกการ Liquidation

### 3.1 Health Factor

$$HF = \frac{\sum (\text{Collateral}_i \times P_i \times LT_i)}{\text{Total Debt (in USD)}}$$

โดยที่:
- $\text{Collateral}_i$ = ปริมาณหลักประกันของสินทรัพย์ $i$
- $P_i$ = ราคาของสินทรัพย์ $i$
- $LT_i$ = Liquidation Threshold ของสินทรัพย์ $i$

**เมื่อ $HF < 1$**: สถานะสามารถถูก liquidate ได้

### 3.2 ขั้นตอน Liquidation

```
1. Monitor: Health factor ของผู้กู้ < 1
2. Liquidator คืนหนี้บางส่วน (สูงสุด 50% ใน Aave)
3. Liquidator รับหลักประกันพร้อมโบนัส (5-15%)
4. Health factor ของผู้กู้เพิ่มขึ้น
```

### 3.3 กำไรจาก Liquidation

$$\text{Profit} = \text{Debt Repaid} \times \text{Liquidation Bonus} - \text{Gas Cost}$$

### 3.4 พารามิเตอร์ Liquidation ตามสินทรัพย์ (Aave V3)

| สินทรัพย์ | LTV | Liquidation Threshold | Liquidation Bonus |
|----------|:---:|:---------------------:|:-----------------:|
| ETH | 80% | 82.5% | 5% |
| WBTC | 70% | 75% | 10% |
| USDC | 77% | 80% | 4.5% |
| stETH | 69% | 81% | 7% |

---

## 4. Recursive Lending (Leveraged Lending)

### 4.1 แนวคิด

เพิ่มผลตอบแทนจากการให้กู้โดยใช้เลเวอเรจ:

```
1. ฝาก $10,000 USDC
2. กู้ $7,700 USDC (77% LTV)
3. ฝาก $7,700 USDC กลับ
4. กู้ $5,929 USDC
5. ทำซ้ำ...
```

### 4.2 คณิตศาสตร์

Effective deposit หลัง $n$ รอบ:

$$D_{eff} = D_0 \times \frac{1 - LTV^{n+1}}{1 - LTV}$$

Effective borrow:

$$B_{eff} = D_0 \times LTV \times \frac{1 - LTV^n}{1 - LTV}$$

### 4.3 Effective leverage

$$\text{Leverage} = \frac{1}{1 - LTV}$$

สำหรับ LTV = 77%: Leverage = 4.35x

### 4.4 Net APY

$$\text{Net APY} = R_{supply} \times \text{Leverage} - R_{borrow} \times (\text{Leverage} - 1) + \text{Token Rewards}$$

---

## 5. Health Factor และการจัดการสถานะ

### 5.1 เกณฑ์ Health Factor

| HF Range | สถานะ | การดำเนินการ |
|----------|--------|-------------|
| > 2.0 | ปลอดภัย | ไม่ต้องทำอะไร |
| 1.5 - 2.0 | ระวัง | ติดตามอย่างใกล้ชิด |
| 1.3 - 1.5 | เตือนภัย | พิจารณาเพิ่มหลักประกัน |
| 1.0 - 1.3 | วิกฤต | เพิ่มหลักประกันหรือคืนหนี้ทันที |
| < 1.0 | Liquidation | ถูก liquidate |

### 5.2 การติดตามอัตโนมัติ

```python
class HealthFactorMonitor:
    """Monitor lending positions for liquidation risk."""
    
    async def check_health(self, position):
        hf = await self.calculate_health_factor(position)
        
        if hf < 1.30:
            await self.emergency_repay(position)
        elif hf < 1.50:
            await self.alert_critical(position, hf)
        elif hf < 1.80:
            await self.alert_warning(position, hf)
    
    async def emergency_repay(self, position):
        """Auto-repay to restore health factor."""
        target_hf = 1.80
        repay_amount = self.calculate_repay_for_target_hf(position, target_hf)
        await self.execute_repay(position, repay_amount)
```

---

## 6. E-Mode (Efficiency Mode)

### 6.1 แนวคิด

E-Mode ใน Aave V3 อนุญาตให้กู้ยืมด้วย LTV สูงขึ้นสำหรับสินทรัพย์ที่สัมพันธ์กัน

### 6.2 ตัวอย่าง

| หมวด E-Mode | สินทรัพย์ | LTV | Liquidation Threshold |
|-------------|----------|:---:|:---------------------:|
| Stablecoins | USDC, USDT, DAI | 97% | 97.5% |
| ETH Correlated | ETH, wstETH, cbETH | 93% | 95% |

### 6.3 ข้อได้เปรียบ

- LTV สูงขึ้น = ต้องใช้หลักประกันน้อยกว่า
- เหมาะสำหรับ looping strategies กับ correlated assets
- ความเสี่ยง liquidation ต่ำกว่า (สินทรัพย์เคลื่อนไปด้วยกัน)

---

## 7. พารามิเตอร์ความเสี่ยง

| พารามิเตอร์ | ค่า |
|------------|------|
| Health factor ขั้นต่ำ | 1.50 |
| เลเวอเรจสูงสุด (recursive) | 3x |
| Utilization rate สูงสุด (ออก) | 95% (เสี่ยงถอนไม่ได้) |
| การจัดสรร lending สูงสุด | 15% ของพอร์ต DeFi |
| ความถี่ตรวจสอบ HF | ทุกบล็อก |
| Alert threshold | HF < 1.80 |

---

## 8. ขั้นตอนการทำงาน

```python
class LendingManager:
    """Manage lending/borrowing positions across protocols."""
    
    async def optimize_positions(self):
        for position in self.active_positions:
            # 1. Check health
            hf = await self.get_health_factor(position)
            if hf < self.min_health_factor:
                await self.deleverage(position)
                continue
            
            # 2. Check rate efficiency
            current_rate = await self.get_borrow_rate(position)
            best_rate = await self.find_best_rate(position.asset)
            
            # 3. Migrate if significantly better
            if current_rate - best_rate > 0.02:  # > 2% improvement
                await self.migrate_position(position, best_rate.protocol)
            
            # 4. Adjust leverage
            optimal_leverage = self.calculate_optimal_leverage(position)
            await self.adjust_leverage(position, optimal_leverage)
```

---

## 9. เอกสารอ้างอิง

1. Aave V3 Documentation: https://docs.aave.com/
2. Compound V3 Documentation: https://docs.compound.finance/
3. "Interest Rate Models in DeFi" — Various research papers
4. "Liquidation Risk in DeFi Lending" — Academic research

---

> **เอกสารถัดไป**: [06_liquid_staking_restaking.md](./06_liquid_staking_restaking.md) — Liquid Staking และ Restaking
