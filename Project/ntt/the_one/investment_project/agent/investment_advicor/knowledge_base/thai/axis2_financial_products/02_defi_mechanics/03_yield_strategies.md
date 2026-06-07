# กลยุทธ์ผลตอบแทน (Yield Strategies) — เอกสารกลไกฉบับสมบูรณ์

> **Axis 2 — ผลิตภัณฑ์ทางการเงิน | โมดูล 02 — กลไก DeFi**
> เวอร์ชัน: 2.0.0 | อัปเดตล่าสุด: 2026-04-12

---

## สารบัญ

1. [กลไก Yield Farming](#1-กลไก-yield-farming)
2. [คณิตศาสตร์การทบต้น (Auto-Compounding)](#2-คณิตศาสตร์การทบต้น)
3. [กลยุทธ์ Yield Aggregator](#3-กลยุทธ์-yield-aggregator)
4. [���ารเพิ่มประสิทธิภาพการ Harvest](#4-การเพิ่มประสิทธิภาพการ-harvest)
5. [การประเมินความยั่งยืนของ Yield](#5-การประเมินความยั่งยืนของ-yield)
6. [พารามิเตอร์ความเสี่ยง](#6-พารามิเตอร์ความเสี่ยง)
7. [ขั้นตอนการทำงาน](#7-ขั้นตอนการทำงาน)
8. [เอกสารอ้างอิง](#8-เอกสารอ้างอิง)

---

## 1. กลไก Yield Farming

### 1.1 แหล่งผลตอบแทนใน DeFi

| แหล่ง | กลไก | APY ทั่วไป | ความเสี่ยง |
|-------|-------|:----------:|-----------|
| ค่าธรรมเนียมการเทรด | LP fees จาก AMM | 2-20% | IL, Smart contract |
| Token emissions | โปรโตคอลแจกโทเคนให้ LPs | 5-100%+ | Token price decline |
| ดอกเบี้ยการให้กู้ | Utilization-based interest | 1-15% | Default, Smart contract |
| Staking rewards | PoS consensus rewards | 3-8% | Slashing, Lock-up |
| Restaking | AVS rewards จาก EigenLayer | 2-10% (เพิ่มเติม) | Additive slashing |

### 1.2 Yield Farming ทำงานอย่างไร

```
1. ฝากสินทรัพย์ใน protocol (เช่น provide liquidity ใน Uniswap)
2. รับ receipt token (เช่น LP token)
3. Stake receipt token ใน farming contract
4. รับ reward tokens เป็นระยะ
5. เก็บ (harvest) rewards
6. ขาย rewards หรือทบต้นกลับเข้าสถานะ
```

---

## 2. คณิตศาสตร์การท���ต้น

### 2.1 APR vs APY

$$APY = \left(1 + \frac{APR}{n}\right)^n - 1$$

โดยที่ $n$ = จำนวนครั้งที่ทบต้นต่อปี

### 2.2 ผลของความถี่การทบต้น

| ความถี่ | $n$ | APY (APR = 50%) |
|---------|:---:|:---------------:|
| รายปี | 1 | 50.00% |
| รายเดือน | 12 | 63.21% |
| รายสัปดาห์ | 52 | 64.48% |
| รายวัน | 365 | 64.82% |
| ต่อเนื่อง | infinity | $e^{0.5} - 1$ = 64.87% |

### 2.3 ความถี่การทบต้นที่เหมาะสม

ทบต้นเมื่อ:

$$\text{Compound Gain} > \text{Gas Cost}$$

$$\text{Rewards Accumulated} \times \left(\frac{APR}{n}\right) > \text{Gas Cost (USD)}$$

**สูตรความถี่ที่เหมาะสม:**

$$n^* = \sqrt{\frac{\text{APR} \times \text{Position Value}}{2 \times \text{Gas Cost}}}$$

---

## 3. กลยุทธ์ Yield Aggregator

### 3.1 Yearn Finance Model

```
1. ผู้ใช้ฝากเข้า Vault
2. Strategy contract จัดสรรทุนไปยังแหล่งผลตอบแทนที่ดีที่สุด
3. เก็บ rewards อัตโนมัติ
4. ขาย rewards เป็น asset เดิม
5. ทบต้นกลับเข้า position
6. หัก management fee (2%) + performance fee (20%)
```

### 3.2 การเลือกกลยุทธ์

| เกณฑ์ | น้ำหนัก | คำอธิบาย |
|--------|---------|---------|
| APY | 30% | ผลตอบแทนที่ปรับตามความเสี่ยง |
| TVL stability | 20% | TVL ที่เสถียรแสดงถึงความยั่งยืน |
| Protocol age | 15% | เก่ากว่า = ทดสอบจากการใช้งานมากกว่า |
| Audit status | 20% | จำนวนและคุณภาพ audit |
| IL risk | 15% | ความเส��่ยง Impermanent Loss |

---

## 4. การเพิ่มประสิทธิภาพการ Harvest

### 4.1 Gas-Optimal Harvesting

```python
def optimal_harvest_frequency(position_value, apr, gas_cost, gas_price_gwei):
    """
    Calculate optimal harvest frequency to maximize net yield.
    """
    gas_cost_usd = gas_cost * gas_price_gwei * eth_price / 1e9
    
    # Optimal frequency (harvests per year)
    n_optimal = math.sqrt(apr * position_value / (2 * gas_cost_usd))
    
    # Optimal interval in hours
    hours_between = 8760 / n_optimal
    
    # Net APY at optimal frequency
    net_apy = (1 + apr / n_optimal) ** n_optimal - 1 - (n_optimal * gas_cost_usd / position_value)
    
    return {
        'frequency': n_optimal,
        'interval_hours': hours_between,
        'net_apy': net_apy
    }
```

### 4.2 Batch Harvesting

รวม harvest หลาย position ในธุรกรรมเดียวเพื่อประหยัด gas

---

## 5. การประเมินความยั่งยืนของ Yield

### 5.1 แหล่ง Yield ที่ยั่งยืน vs. ไม่ยั่งยืน

| ยั่งยืน | ไม่ยั่งยืน |
|---------|-----------|
| ค่าธรรมเนียมการเทรดจริง | Token emissions ที่ถูกทิ้ง |
| ดอกเบี้ยจากการกู้ยืมจริง | Ponzi-like referral rewards |
| Staking rewards (consensus) | Unsustainable APY > 1000% |
| MEV revenue sharing | Token unlock ที่กำลังจะมา |

### 5.2 สูตรประเมิน Real Yield

$$\text{Real Yield} = \text{Protocol Revenue} - \text{Token Emissions Value}$$

ถ้า Real Yield < 0 → protocol กำลังเผา treasury เพื่อจ่าย yield

---

## 6. พารามิเตอร์ความเสี่ยง

| พารามิเตอร์ | ค่า |
|------------|------|
| APY ขั้นต่ำที่ยอมรับ | 5% (หลังหักค่า gas) |
| Protocol age ขั้นต่ำ | 6 เดือน |
| TVL ขั้นต่ำ | $50M |
| Max allocation ต่อ protocol | 10% |
| Max allocation ต่อ chain | 15% |
| Max composability depth | 3 ชั้น |

---

## 7. ขั้นตอนการท��งาน

```python
class YieldOptimizer:
    """Automated yield optimization across DeFi protocols."""
    
    async def scan_opportunities(self):
        opportunities = []
        for protocol in self.approved_protocols:
            yields = await protocol.get_current_yields()
            for pool in yields:
                if self.passes_risk_checks(pool):
                    score = self.calculate_risk_adjusted_yield(pool)
                    opportunities.append((pool, score))
        
        return sorted(opportunities, key=lambda x: x[1], reverse=True)
    
    async def rebalance(self):
        """Rotate capital to best risk-adjusted yields."""
        current_positions = self.get_current_positions()
        best_opportunities = await self.scan_opportunities()
        
        for position in current_positions:
            current_yield = position.current_apy
            best_yield = best_opportunities[0][1]
            
            # Only rotate if significantly better (> 2% improvement)
            if best_yield - current_yield > 0.02:
                await self.exit_position(position)
                await self.enter_position(best_opportunities[0][0])
```

---

## 8. เอกสารอ้างอิง

1. Yearn Finance Documentation: https://docs.yearn.fi/
2. Beefy Finance Documentation: https://docs.beefy.finance/
3. "DeFi Yield: A Framework for Understanding Sources and Sustainability"

---

> **เอกสารถัดไป**: [04_flash_loans_composability.md](./04_flash_loans_composability.md) — Flash Loans และ Composability
