# Liquid Staking และ Restaking — เอกสารกลไกฉบับสมบูรณ์

> **Axis 2 — ผลิตภัณฑ์ทางการเงิน | โมดูล 02 — กลไก DeFi**
> เวอร์ชัน: 2.0.0 | อัปเดตล่าสุด: 2026-04-12

---

## สารบัญ

1. [Liquid Staking — พื้นฐาน](#1-liquid-staking--พื้นฐาน)
2. [Lido (stETH)](#2-lido-steth)
3. [Rocket Pool (rETH)](#3-rocket-pool-reth)
4. [Restaking — EigenLayer](#4-restaking--eigenlayer)
5. [Yield Stacking](#5-yield-stacking)
6. [ความเสี่ยงและการบรรเทา](#6-ความเสี่ยงและการบรรเทา)
7. [แบบจำลองทางคณิตศาสตร์](#7-แบบจำลองทางคณิตศาสตร์)
8. [พารามิเตอร์ความเสี่ยง](#8-พารามิเตอร์ความเสี่ยง)
9. [ขั้นตอนการทำงาน](#9-ขั้นตอนการทำงาน)
10. [เอกสารอ้างอิง](#10-เอกสารอ้างอิง)

---

## 1. Liquid Staking — พื้นฐาน

### 1.1 ปัญหาของ Traditional Staking

- ETH ที่ stake ถูกล็อก (ไม่สามารถใช้ใน DeFi)
- ต้องมี 32 ETH เพื่อเป็น validator เดี่ยว
- ต้องดูแล node infrastructure

### 1.2 Liquid Staking แก้ปัญหาอย่างไร

```
ผู้ใช้ฝาก ETH → Liquid Staking Protocol → ได้ Liquid Staking Token (LST)
                                                    |
                                                    v
                                    ใช้ LST ได้ใน DeFi (ให้กู้, LP, หลักประกัน)
                                                    +
                                    ยังได้ staking rewards
```

### 1.3 ประเภท LST

| ประเภท | ตัวอย่าง | กลไก |
|--------|---------|-------|
| Rebasing | stETH (Lido) | ยอดเพิ่มขึ้นทุกวัน |
| Appreciating | rETH (Rocket Pool), cbETH | มูลค่าต่อโทเคนเพิ่มขึ้น |
| Wrapped | wstETH | Wrap stETH เพื่อใช้ใน DeFi ที่ไม่รองรับ rebase |

---

## 2. Lido (stETH)

### 2.1 กลไก

- ฝาก ETH → ได้ stETH 1:1
- stETH rebase ทุกวัน (ยอดเพิ่มตาม staking rewards)
- Lido รับ 10% ของ rewards (5% node operators, 5% treasury)

### 2.2 ผลตอบแทน

$$APY_{stETH} = APY_{consensus} + APY_{execution} - \text{Lido Fee (10\%)}$$

ปกติ: ~3-5% APR

### 2.3 stETH/ETH Peg

- ปกติ stETH ≈ ETH (< 0.5% deviation)
- อาจ depeg ในสภาวะตลาดรุนแรง (เช่น พ.ค. 2022: depeg ถึง 5%)
- สาเหตุ depeg: forced selling, withdrawal queue ยาว, ความกลัวทั่วไป

### 2.4 การใช้งานใน DeFi

| โปรโตคอล | การใช้ stETH | ผลตอบแทนเพิ่มเติม |
|----------|-------------|-------------------|
| Aave | หลักประกัน | กู้ stablecoins |
| Curve | LP (stETH/ETH pool) | Trading fees + CRV rewards |
| Lido wstETH | Compound-compatible | ใช้ที่ไหนก็ได้ |
| EigenLayer | Restake | AVS rewards |

---

## 3. Rocket Pool (rETH)

### 3.1 กลไก

- กระจายศูนย์มากกว่า Lido (permissionless node operators)
- ฝาก ETH → ได้ rETH (อัตราส่วนไม่ใช่ 1:1)
- rETH เป็น appreciating token (มูลค่าเพิ่มเทียบกับ ETH)

### 3.2 อัตราแลกเปลี่ยน rETH/ETH

$$\text{rETH/ETH rate} = \frac{\text{Total ETH staked + rewards}}{\text{Total rETH supply}}$$

อัตราส่วนเพิ่มขึ้นตลอดเวลา (เช่น 1 rETH = 1.05 ETH หลัง 1 ปี)

### 3.3 ข้อดีเทียบกับ Lido

- กระจายศูนย์มากกว่า
- ไม่มี rebasing (ง่ายกว่าสำหรับ DeFi integrations)
- Node operators ต้องวาง ETH เป็นหลักประกัน

---

## 4. Restaking — EigenLayer

### 4.1 แนวคิด

EigenLayer อนุญาตให้ staked ETH (หรือ LSTs) ถูกใช้ซ้ำเพื่อรักษาความปลอดภัยให้โปรโตคอลเพิ่มเติม ที่เรียกว่า Actively Validated Services (AVSs)

### 4.2 การทำงาน

```
ETH Staker
    |
    v
Ethereum PoS (ชั้นที่ 1: Consensus rewards)
    |
    v
EigenLayer Restaking (ชั้นที่ 2: ลงทะเบียน AVS)
    |
    v
AVS 1 (Oracle network)     → Rewards
AVS 2 (Data availability)  → Rewards
AVS 3 (Bridge validation)  → Rewards
```

### 4.3 ประเภทการ Restake

| ประเภท | วิธีการ | ความเสี่ยง |
|--------|---------|-----------|
| Native Restaking | Point validator credentials ไปที่ EigenLayer | Additive slashing |
| LST Restaking | ฝาก stETH/rETH ใน EigenLayer | Smart contract + slashing |

### 4.4 ความเสี่ยงเพิ่มเติม

- **Additive slashing:** ถูก slash ได้ทั้งจาก Ethereum PoS และ AVS
- **Smart contract risk:** เพิ่มอีกชั้นของ smart contract risk
- **ความซับซ้อน:** ยากต่อการประเมินความเสี่ยงทั้งหมด
- **AVS risk:** AVS แต่ละตัวมีเงื่อนไข slashing ต่างกัน

---

## 5. Yield Stacking

### 5.1 แนวคิด

รวมผลตอบแทนจากหลายชั้นพร้อมกัน:

$$Y_{total} = Y_{staking} + Y_{restaking} + Y_{DeFi}$$

### 5.2 ตัวอย่างกลยุทธ์

```
ชั้นที่ 1: ETH Staking via Lido → stETH (3-5% APR)
ชั้นที่ 2: Restake via EigenLayer → AVS rewards (+2-5% APR)
ชั้นที่ 3: ใช้ wstETH เป็นหลักประกัน Aave → กู้ USDC
ชั้นที่ 4: ให้กู้ USDC บน Compound → interest (3-8% APR)

Total Yield = Staking + Restaking + Lending spread
```

### 5.3 ผลตอบแทนเทียบกับความเสี่ยง

| กลยุทธ์ | ผลตอบแทนประมาณ | จำนวนชั้น | ระดับความเสี่ยง |
|---------|:-------------:|:---------:|:-------------:|
| ETH staking เดี่ยว | 3-5% | 1 | ต่ำ |
| stETH + Restaking | 5-10% | 2 | ปานกลาง |
| stETH + Aave + Lending | 8-15% | 3 | ปานกลาง-สูง |
| Full stack (4 ชั้น) | 12-25% | 4 | สูง |

---

## 6. ความเสี่ยงและการบรรเทา

### 6.1 ตารางความเสี่ยง

| ความเสี่ยง | คำอธิบาย | ความรุนแรง | การบรรเทา |
|------------|---------|:----------:|----------|
| Slashing | Validator ทำผิดกฎ | สูง | เลือก operator ดี, กระจาย |
| Smart contract | บั๊กใน LST/restaking contracts | วิกฤต | Audit verification, position limits |
| De-peg | LST ลดค่าเทียบ ETH | ปานกลาง | Monitor peg, exit triggers |
| Withdrawal delay | คิวถอนยาว | ปานกลาง | รักษาสภาพคล่องสำรอง |
| AVS slashing | ถูก slash จาก AVS | สูง | เลือก AVS อย่างระมัดระวัง |
| Composability cascade | ปัญหาลุกลามข้ามชั้น | วิกฤต | จำกัดจำนวนชั้น |

### 6.2 กฎ Position Limits

$$\text{Max Position} = \frac{\text{Risk Budget}}{\text{Number of Layers} \times \text{Per-Layer Risk}}$$

---

## 7. แบบจำลองทางคณิตศาสตร์

### 7.1 ผลตอบแทน Staking

$$APY_{staking} = \frac{R_{base}}{\sqrt{S_{total}}} \times (1 - f_{protocol})$$

โดยที่:
- $R_{base}$ = issuance rate ของ Ethereum
- $S_{total}$ = ETH ที่ stake ทั้งหมด
- $f_{protocol}$ = ค่าธรรมเนียมโปรโตคอล

### 7.2 ความเสี่ยงรวมของ Yield Stack

$$R_{total} = 1 - \prod_{i=1}^{N} (1 - R_i)$$

สำหรับ 4 ชั้นที่แต่ละชั้นมีความเสี่ยง 2%:

$$R_{total} = 1 - (0.98)^4 = 7.76\%$$

---

## 8. พารามิเตอร์ความเสี่ยง

| พารามิเตอร์ | ค่า |
|------------|------|
| จำนวนชั้น yield stacking สูงสุด | 3 |
| การจัดสรร LST สูงสุด | 20% ของพอร์ต |
| Max peg deviation ก่อนออก | 2% |
| Min protocol age สำหรับ restaking | 6 เดือน |
| Slashing insurance required | ใช่ (ถ้ามี) |
| Monitoring frequency | ทุกบล็อก |

---

## 9. ขั้นตอนการทำงาน

```python
class LiquidStakingManager:
    """Manage liquid staking and restaking positions."""
    
    async def monitor_positions(self):
        for position in self.positions:
            # 1. Check peg health
            peg = await self.check_lst_peg(position.lst_token)
            if peg.deviation > 0.02:  # > 2% depeg
                await self.exit_to_eth(position)
                continue
            
            # 2. Check slashing events
            slashing_events = await self.check_slashing(position)
            if slashing_events:
                await self.evaluate_and_respond(position, slashing_events)
            
            # 3. Check yield optimization
            current_yield = position.total_apy
            alternatives = await self.find_better_strategies()
            if alternatives and alternatives[0].apy > current_yield * 1.2:
                await self.migrate(position, alternatives[0])
            
            # 4. Check composability health
            for layer in position.layers:
                health = await layer.check_health()
                if health < self.min_health:
                    await self.unwind_layer(position, layer)
    
    async def check_lst_peg(self, token):
        """Monitor LST/ETH peg."""
        dex_price = await self.get_dex_price(token, "ETH")
        oracle_price = await self.get_oracle_price(token, "ETH")
        deviation = abs(dex_price - oracle_price) / oracle_price
        return PegStatus(deviation=deviation, healthy=deviation < 0.01)
```

---

## 10. เอกสารอ้างอิง

1. Lido Documentation: https://docs.lido.fi/
2. Rocket Pool Documentation: https://docs.rocketpool.net/
3. EigenLayer Documentation: https://docs.eigenlayer.xyz/
4. "Liquid Staking Derivatives: Market Structure and Risks" — Various research
5. "Restaking and the Future of Shared Security" — EigenLayer Whitepaper

---

> **จบโมดูล 02: DeFi Mechanics**
> กลับไปที่: [00_overview.md](./00_overview.md)
