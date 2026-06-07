# MEV & DeFi Arbitrage — เอกสารกลยุทธ์ฉบ��บสมบูรณ์

> **เวอร์ชันเอกสาร:** 2.0
> **อัป���ดตล่าสุด:** 2026-04-12
> **การจัดประเภท:** Core Knowledge Base — Axis 2: ผลิตภัณฑ์ทางการเงิน
> **ประเภทกลย���ทธ์:** Pure Arbitrage (การดำเนินการแบบ atomic ผ่าน smart contracts)
> **ตลาด:** DeFi (Ethereum, L2s, Solana, EVM chains อื่นๆ)
> **ความถี่:** ต่อบล็อก (12s Ethereum, 0.4s Solana, 2s L2s)

---

## สารบัญ

1. [Maximal Extractable Value (MEV) — อธิบาย](#1-maximal-extractable-value-mev--อธิ��าย)
2. [ประเภทของ MEV](#2-ประเภทของ-mev)
3. [DEX Arbitrage ระหว่าง AMMs](#3-dex-arbitrage-ระหว่าง-amms)
4. [Flash Loan Arbitrage](#4-flash-loan-arbitrage)
5. [Liquidation Arbitrage](#5-liquidation-arbitrage)
6. [Cross-Chain Arbitrage](#6-cross-chain-arbitrage)
7. [กล���ุทธ์ป้องกัน MEV](#7-กลยุทธ์ป้องกัน-mev)
8. [สถาปัตยกรรม Smart Contract](#8-สถาปัตยกรรม-smart-contract)
9. [กลยุทธ์เพิ่มประสิทธิภาพ Gas](#9-กลยุทธ์เพิ่มประสิทธ��ภาพ-gas)
10. [แบบจำลองทางคณิตศาสตร์](#10-แ���บจำลองทางคณิตศาสตร์)
11. [พารามิเตอร์ความเสี่ยงและขั้นตอนการทำงาน](#11-พารามิเตอร์ความเสี่ยงและขั้นตอนการทำงาน)
12. [เอกสาร���้างอิง](#12-เอกสารอ้างอิง)

---

## 1. Maximal Extractable Value (MEV) — อธิบ���ย

### 1.1 คำจำกัดความ

**Maximal Extractable Value (MEV)** หมายถึงมูลค่าสูงสุดที่สามารถดึงออกจากการผลิตบล็อกเกินกว่ารางวัลบล็อกมาตรฐานและค่า gas โดยการรวม ไม่รวม หรือเรียงลำดับธุรกรรมภายในบล็อก

### 1.2 MEV เกิดขึ้นอย่างไร

1. **ลำดับธุรกรรมมีความสำคัญ:** ลำดับที่ธุรกรรมถูกรวมในบล็อกส่งผลต่อผลลัพธ์ทางเศรษฐกิจ
2. **Mempool สาธารณะ:** ธุรกรรมที่รออยู่มองเห็นได้โดยผู้เข้าร่วมเครือข่ายทุกคนก่อนการรวม
3. **การดำเนินการที่กำหนดได้:** ผล���ัพธ์ smart contract คาดเดาได้จากสถานะและลำดับธุร��รรม
4. **ดุลพินิจของ block proposer:** ผู้สร้างบล็อกสามารถเลือกธุรกรรมที่จะรวมและในลำดับใด

### 1.3 MEV Supply Chain (Post-Merge Ethereum)

```
┌────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────���────────┐
│   Searcher  │────>│    Builder    │────>│    Relay     │────>│   Proposer   │
│ (finds MEV) │     │ (builds block)│     │(auctions block)│   │(validates)   │
└────────────┘     └─────���────────┘     └────────────���┘     └──────��───────┘
```

**ผู้มีบทบาทหลัก:**
- **Searchers:** ค้นหาโอกาส MEV (arbitrage, liquidations) และส่ง transaction bundles
- **Builders:** รวม bundles และธุรกรรมเป็นบล็อกสม��ูรณ์
- **Relays:** ทำหน้าที่เป็นตัวกลางที่เชื่อถือได้ระหว่าง builders และ proposers
- **Proposers (Validators):** เลือกบล็อกที่ให้กำไรมากที่สุดเพื่อเสนอ

### 1.4 ขนาดของ MEV

- **MEV สะสมบน Ethereum (ตั้งแต่ ม.ค. 2020):** > $800M
- **MEV รายวัน (ปกติ):** $1-5M
- **MEV รายวันสูงสุด:** > $50M (ระหว่างเหตุการณ์ตลาดสำคัญ)
- **การกระจายประเภท MEV:** ~60% arbitrage, ~30% liquidations, ~10% sandwich attacks

---

## 2. ประเภทของ MEV

### 2.1 อนุกรมวิธาน

```
MEV Types
├── MEV ที่เป็นประโยชน์ (positive externalities)
│   ├── DEX Arbitrage (การจัดเรียงราคา)
│   ├── Liquidations (รักษาสุขภาพโปรโตคอล)
│   └── Oracle updates (รักษาราคาให้ทันสมัย)
│
├── MEV ที่เป็นกลาง
│   ├── Backrunning (เทรดหลังคำสั่งใหญ่)
│   └── JIT (Just-in-Time) Liquidity
���
└── MEV ที่เป็นอันตราย (negative externalities)
    ├── Frontrunning (เทรดก่อนเหยื่อ)
    ├── Sandwich Attacks (frontrun + backrun)
    ├── Time-Bandit Attacks (chain reorgs)
    └── Censorship (ไม่รวมธุรกรรม)
```

### 2.2 Sandwich Attacks

```
Block ordering:
1. Attacker BUY  (frontrun) — ดันราคาขึ้น
2. Victim BUY   (target)   — ดำเนินการที่ราคาสูงกว่า
3. Attacker SELL (backrun)  — ทำกำไรจากส่วนต่างราคา
```

**สูตรกำไร:**

$$\text{Sandwich Profit} = Q_{attacker} \times (P_{after\_victim} - P_{before\_victim}) - 2 \times Gas$$

---

## 3. DEX Arbitrage ระหว่าง AMMs

### 3.1 AMMs กำหนดราคาอย่างไร

**Constant Product Market Maker (Uniswap V2, SushiSwap):**

$$x \times y = k$$

**ราคาของ token X ในหน่วย Y:**

$$P_X = \frac{y}{x}$$

### 3.2 เหตุใดราคา DEX จึงเบี่ยงเบน

1. **Liquidity pools อิสระ:** แต่ละ pool/DEX มีทุนสำรองอิส��ะ
2. **อัปเดตทีละบล็อก:** ราคาเปลี่ยนเมื่อธุรกรรมถูกรวมในบล็อกเท่านั้น
3. **ไม่มี continuous market making:** ต่างจาก CEX order books ราคา AMM เป็นสูตร
4. **Fee tiers ต่างกัน:** Uniswap V3 มีพูล 0.01%, 0.05%, 0.30%, 1.00%
5. **Swaps ใหญ่:** การเทรดใหญ่บน DEX หนึ่งสร้างการเคลื่อนตัวราคาเทียบกับอื่น

### 3.3 ขนาดเทรดที่เหมาะสมสำหรับ constant-product AMMs

สำห���ับ Uniswap reserves $(x_U, y_U)$ และ SushiSwap reserves $(x_S, y_S)$:

จำนวน $\Delta x$ ที่เหมาะสมเพื่อซื้อบน DEX ที่ถูกกว่าต้องตอบสนอง:

$$\frac{y_U - \frac{x_U \times y_U}{x_U + \Delta x \times (1-f_U)}}{1} = \frac{y_S \times \Delta y}{y_S + \Delta y \times (1-f_S)}$$

---

## 4. Flash Loan Arbitrage

### 4.1 แนวคิด

Flash loans อนุญาตให้กู้ยืมสินทรัพย์โดยไม่ต้องมีหลักประกัน ภายในธุรกรรมเดียว ถ้าไม่คืนในบล็อกเดียวกัน ธุรกรรมทั้งหมดถูก revert

### 4.2 ขั้นตอนการทำงาน

```
1. กู้ Flash Loan จาก Aave/dYdX (เช่น 1M USDC)
2. สวอปบน DEX ที่ราคาถูก (ซื้อ ETH ราคาถูก)
3. สวอปบน DEX ที่ราคาแพง (ขาย ETH ราคาแพง)
4. คืน flash loan + fee (0.09%)
5. เก็บกำไร
```

### 4.3 ข้อได้เปรียบ

- ไม่ต้องใช้ทุน (capital-free)
- ปลอดความเสี่ยง (atomic — สำเร็จทั้งหมดหรือ revert ทั้งหมด)
- เลเวอเรจไม่จำกัดในทางทฤษฎี

### 4.4 ข้อจำกัด

- ต้องทำกำไรหลังหักค่า gas + flash loan fee
- แข่งขันสูง (MEV searchers หลายรายเห็นโอกาสเดียวกัน)
- โอกาสมักมีอยู่เพียงหนึ่งบล็อก

---

## 5. Liquidation Arbitrage

### 5.1 ���นวคิด

ติดตามสถานะที่มีหลักประกันไม่เพียงพอบนโปรโตคอลการให้กู้ (Aave, Compound) และดำเนินการ liquidation เพื่อรับโบนัส

### 5.2 กำไรจาก Liquidation

$$\text{Profit} = \text{Debt Repaid} \times \text{Liquidation Bonus} - \text{Gas Cost}$$

Liquidation bonus ทั่วไป: 5-15% ขึ้นอยู่กับสินทรัพย์

### 5.3 ความท้าทาย

- ต้องมีทุนเพื่อคืนหนี้ (หรือใช้ flash loan)
- แข่งขันสูง: ใครส่งธุรกรรมก่อนได้โบนัส
- Gas price wars: priority fee สูงเพื่อรวมในบล็��ก

---

## 6. Cross-Chain Arbitrage

### 6.1 แนวคิด

ใช้ประโยชน์จากส่วนต่างราคาของสินทรัพย์เดียวกันบนเชนที่ต่างกัน

### 6.2 ความท้าทาย

- เวลา bridge: นาทีถึงชั่วโมง
- ความเสี่ยง bridge: exploits, ความล่าช้า
- ไม่เป็น atomic: ไม่สามารถรับประกันทั้งสองฝั่ง

---

## 7. กลยุทธ์ป้องกัน MEV

### 7.1 สำหรับเทรดเดอร์ (ป้องกันตัวจาก MEV)

- ใช้ private mempools (Flashbots Protect)
- ตั้ง slippage tolerance ต่ำ
- ใช้ limit orders แทน market orders
- เทรดบน DEX ที่มี MEV protection (CoWSwap)

### 7.2 สำหรับ Searchers (ดึง MEV)

- ใช้ Flashbots Bundle
- เพิ่มประสิทธิภาพ gas
- สร้าง smart contract เฉพาะทาง
- ติดตาม mempool แบบเรี���ลไทม์

---

## 8. สถาปัตยกรรม Smart Contract

```solidity
// Simplified arbitrage contract
contract FlashLoanArbitrage {
    function executeArbitrage(
        address flashLoanProvider,
        address dexA,
        address dexB,
        address tokenIn,
        address tokenOut,
        uint256 amount
    ) external {
        // 1. Borrow via flash loan
        // 2. Swap on DEX A (buy cheap)
        // 3. Swap on DEX B (sell expensive)
        // 4. Repay flash loan + fee
        // 5. Keep profit
    }
}
```

---

## 9. กลย��ทธ์เพิ่มประสิทธิภาพ Gas

- ลด storage operations (SSTORE เป็นราคาแพงที่สุด)
- ใช้ assembly สำหรับ hot paths
- Batch หลายการดำเนินการในธุรกรรมเด���ยว
- ใช้ EIP-1559 priority fees อย่างมีกลยุทธ์
- Pre-compute ผลลัพธ์ off-chain

---

## 10. แบบจำลองทางคณิตศาสตร์

### 10.1 กำไร AMM Arbitrage ที่เหมาะสม

สำหรับ constant product AMM ที่มี reserves $(x, y)$ และ fee $f$:

$$\Delta x^* = \sqrt{\frac{x \times y \times (1-f)}{P_{external}}} - x$$

### 10.2 เงื่อนไขกำไร

$$\text{Profit} = \text{Revenue from arb} - \text{Gas cost} - \text{Flash loan fee} > 0$$

$$\text{Min profitable spread} = \frac{\text{Gas}_{\text{USD}} + \text{Flash fee}}{Q \times P}$$

---

## 11. พารามิเตอร์ความเสี่ยงและขั้นตอนการทำงาน

| พารามิเตอร์ | ค่า |
|------------|------|
| กำไรขั้นต่ำต่อการเทรด | > $50 (หลังหัก gas) |
| Gas price สูงสุดที่ยอมรับ | ข��้นอยู่กับขนาดโอกาส |
| Slippage tolerance | 0.5-1% |
| Flash loan providers | Aave, dYdX, Balancer |
| ช่องทางส่งธุรกรรม | Flashbots, private mempools |

---

## 12. เอกสารอ้างอิง

1. Daian, P., et al. (2020). "Flash Boys 2.0." IEEE S&P.
2. Flashbots Documentation: https://docs.flashbots.net/
3. Uniswap V3 Documentation: https://docs.uniswap.org/
4. Aave Flash Loans: https://docs.aave.com/

---

> **เอกสารถัดไป**: [05_statistical_arbitrage_pairs.md](./05_statistical_arbitrage_pairs.md) — Statistical Arbitrage & Pairs Trading
