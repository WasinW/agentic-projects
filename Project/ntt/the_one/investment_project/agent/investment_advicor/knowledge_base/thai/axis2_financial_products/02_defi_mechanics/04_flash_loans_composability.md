# Flash Loans และ Composability — เอกสารกลไกฉบับสมบูรณ์

> **Axis 2 — ผลิตภัณฑ์ทางการเงิน | โมดูล 02 — กลไก DeFi**
> เวอร์ชัน: 2.0.0 | อัปเดตล่าสุด: 2026-04-12

---

## สารบัญ

1. [กลไก Flash Loan](#1-กลไก-flash-loan)
2. [กรณีการใช้งาน](#2-กรณีการใช้งาน)
3. [เวกเตอร์การโจมตี (สำหรับการป้องกัน)](#3-เวกเตอร์การโจมตี)
4. [รูปแบบ Composability](#4-รูปแบบ-composability)
5. [การดำเนินการทางเทคนิค](#5-การดำเนินการทางเทคนิค)
6. [พารามิเตอร์ความเสี่ยง](#6-พารามิเตอร์ความเสี่ยง)
7. [เอกสารอ้างอิง](#7-เอกสารอ้างอิง)

---

## 1. กลไก Flash Loan

### 1.1 Flash Loan คืออะไร?

Flash loan คือสินเชื่อแบบไม่ต้องมีหลักประกันที่ต้องกู้และคืนภายในธุรกรรมเดียว ถ้าไม่คืน ธุรกรรมทั้งหมดถูก revert เหมือนไม่เคยเกิดขึ้น

### 1.2 ข้อกำหนด

- กู้และคืนในธุรกรรม **เดียวกัน** (atomic)
- จ่ายค่าธรรมเนียม (Aave: 0.09%, dYdX: 0 เมื่อ deposit momentarily)
- ถ้าไม่คืน → ทุกอย่าง revert → ไม่มีความเสี่ย���สำหรับผู้ให้กู้

### 1.3 ผู้ให้บริการ Flash Loan

| ผู้ให้บริการ | ค่าธรรมเนียม | สภาพคล่องสูงสุด | เชน |
|-------------|:----------:|:--------------:|------|
| Aave V3 | 0.09% | $B+ | Ethereum, L2s |
| dYdX | 0% (ฝากชั่วคราว) | $100M+ | Ethereum |
| Balancer | 0% | $500M+ | Ethereum |
| Uniswap V3 | 0.3% (flash swap) | Pool-dependent | Ethereum, L2s |

### 1.4 ขั้นตอนการทำงานของ Flash Loan

```
Transaction Start
│
├── 1. กู้ Flash Loan (เช่น 1M USDC จาก Aave)
│
├── 2. ใช้เงินทำอะไรก็ได้ (arb, collateral swap, etc.)
│       ├── Swap บน DEX A
│       ├── Swap บน DEX B
│       └── ... (กี่ขั้นตอนก็ได้)
│
├── 3. คืน Flash Loan + ค่าธรรมเนียม
│
├── 4a. ถ้าคืนสำเร็จ → Transaction สำเร็จ → เก็บกำไร
│
└── 4b. ถ้าคืนไ��่ได้ → REVERT ทั้งหมด → เหมือนไม่เคยเกิดขึ้น
         (เสียเฉพาะค่า gas)
```

---

## 2. กรณีการใช้งาน

### 2.1 Arbitrage

กู้ → ซื้อราคาถูกบน DEX A → ขายราคาแพงบน DEX B → คืน → เก็บกำไร

### 2.2 Collateral Swap

```
1. Flash loan USDC
2. คืนหนี้ Aave (ปลดล็อกหลักประกัน ETH)
3. ถอน ETH
4. ฝาก ETH บน Compound
5. กู้ USDC จาก Compound
6. คืน flash loan
ผลลัพธ์: ย้ายหลักประกันจาก Aave ไป Compound โดยไม่ต้องมีทุนเพิ่ม
```

### 2.3 Self-Liquidation

```
1. Flash loan USDC
2. คืนหนี้ (หลีกเลี่ยง liquidation penalty)
3. ถอนหลักประกัน
4. ขายหลักประกันบางส่วน
5. คืน flash loan
ผลลัพธ์: ปิดสถานะเสี่ยงโดยไม่โดน liquidation bonus
```

### 2.4 Leveraged Position

```
1. Flash loan DAI
2. ซื้อ ETH
3. ฝาก ETH ใน Aave
4. กู้ DAI จาก Aave
5. คืน flash loan
ผลลัพธ์: เปิดสถานะ leveraged long ETH ในธุ��กรรมเดียว
```

---

## 3. เวกเตอร์การโจมตี

### 3.1 Oracle Manipulation

```
1. Flash loan จำนวนมาก
2. เทรดบน DEX เพื่อปั่น on-chain price
3. ใช้ราคาที่ปั่นเพื่อกู้ยืมเกินมูลค่า
4. คืน flash loan
5. เก็บกำไรจากการกู้เกิน
```

**การป้อ��กัน:** ใช้ TWAP oracles, หลายแหล่ง oracle, delay mechanisms

### 3.2 Governance Attack

```
1. Flash loan governance tokens
2. สร้างและโหวต proposal ที่เป็นอันตราย
3. คืน flash loan
```

**การป้องกัน:** Snapshot voting, minimum holding period, time-locked votes

### 3.3 Re-entrancy via Flash Loan

**การป้องกัน:** Reentrancy guards, checks-effects-interactions pattern

---

## 4. รูปแบบ Composability

### 4.1 Money Legos

DeFi composability = ความสามารถในการรวมโปรโตคอลหลายตัวในธุรกรรมเดียว

### 4.2 ตัวอย่างรูปแบบ

```
Pattern: Leveraged Yield Farming
ETH → Lido (stETH) → Aave (deposit) → Borrow USDC → Curve LP → Stake → Rewards

Pattern: Flash Loan Liquidation
Flash Loan → Repay debt → Receive collateral at discount → Sell → Repay → Profit
```

### 4.3 ความเสี่ยง Composability

$$R_{composite} = 1 - \prod_{i=1}^{N} (1 - R_i)$$

ทุกชั้นเพิ่มความเสี่ยง ไม่ใช่เพิ่มแบบเชิงเส้น แต่เป็นแบบทบต้น

---

## 5. การดำเนินการทางเทคนิค

```solidity
// Flash Loan Receiver Interface (Aave V3)
interface IFlashLoanSimpleReceiver {
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external returns (bool);
}

contract ArbitrageExecutor is IFlashLoanSimpleReceiver {
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        // 1. Decode params for arbitrage route
        // 2. Execute swaps
        // 3. Ensure profit > premium
        // 4. Approve repayment
        uint256 amountOwed = amount + premium;
        IERC20(asset).approve(msg.sender, amountOwed);
        return true;
    }
}
```

---

## 6. พารามิเตอร์ความเสี่ยง

| พารามิเตอร์ | ค่า |
|------------|------|
| กำไรขั้นต่ำต่อ flash loan | > $50 (หลัง gas + fee) |
| Max composability depth | 3 protocols ในธุรกรรมเดียว |
| Gas limit ต่อธุรกรรม | < 1M gas units |
| Simulation ก่อนส่ง | บังคับ (eth_call) |
| Flash loan providers ที่อนุมัติ | Aave, Balancer เท่านั้น |

---

## 7. เอกสารอ้างอิง

1. Aave Flash Loans: https://docs.aave.com/developers/guides/flash-loans
2. "Flash Loans: A Survey" — Academic paper
3. DeFi Composability Risks — Gudgeon et al. (2020)

---

> **เอกสารถัดไป**: [05_lending_borrowing.md](./05_lending_borrowing.md) — กลไกการให้กู้และยืม
