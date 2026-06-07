# กลไก DeFi ขั้นสูง — ภาพรวม

> **Axis 2 — ผลิตภัณฑ์ทางการเงิน | โมดูล 02 — กลไก DeFi**
> เวอร์ชัน: 2.0.0 | อัปเดตล่าสุด: 2026-04-12
> การจัดประเภท: KNOWLEDGE BASE — ระบบเทรด AI แบบ MULTI-AGENT

---

## สารบัญ

1. [บทนำ](#1-บทนำ)
2. [สถาปัตยกรรมระบบนิเวศ DeFi](#2-สถาปัตยกรรมระบบนิเวศ-defi)
3. [โปรโตคอลหลักและบทบาท](#3-โปรโตคอลหลักและบทบาท)
4. [กรอบความเสี่ยงของ Smart Contract](#4-กรอบความเสี่ยงของ-smart-contract)
5. [การวิเคราะห์มูลค่ารวมที่ถูกล็อก (TVL)](#5-การวิเคราะห์มูลค่ารวมที่ถูกล็อก-tvl)
6. [ความสามารถในการประกอบร่วมของ DeFi — Money Legos](#6-ความสามารถในการประกอบร่วมของ-defi--money-legos)
7. [เหตุใด DeFi จึงสำคัญต่อการเทรดแบบอัลกอริทึม](#7-เหตุใด-defi-จึงสำคัญต่อการเทรดแบบอัลกอริทึม)
8. [แผนผังโมดูล — เนื้อหาที่ครอบคลุม](#8-แผนผังโมดูล--เนื้อหาที่ครอบคลุม)
9. [พารามิเตอร์ความเสี่ยง — ทั่วทั้งระบบ](#9-พารามิเตอร์ความเสี่ยง--ทั่วทั้งระบบ)
10. [ขั้นตอนการทำงาน — เครื่องสแกนโอกาส DeFi](#10-ขั้นตอนการทำงาน--เครื่องสแกนโอกาส-defi)
11. [เอกสารอ้างอิง](#11-เอกสารอ้างอิง)

---

## 1. บทนำ

การเงินแบบกระจายศูนย์ (Decentralized Finance หรือ DeFi) เป็นการเปลี่ยนแปลงกระบวนทัศน์อย่างมูลฐานในบริการทางการเงิน: การแทนที่ตัวกลางที่ต้องเชื่อถือด้วยตรรกะ Smart Contract ที่กำหนดได้แน่นอน ตรวจสอบได้ และทำงานบนบล็อกเชนสาธารณะ สำหรับระบบเทรดแบบอัลกอริทึม DeFi ไม่ได้เป็นเพียงช่องทางทางเลือก — แต่เป็นโครงสร้างพื้นฐานทางการเงินที่โปรแกรมได้ ซึ่งเปิดโอกาสให้ใช้กลยุทธ์ที่เป็นไปไม่ได้ในการเงินแบบดั้งเดิม

### 1.1 ขอบเขตของโมดูลนี้

โมดูลนี้ (02_defi_mechanics) ให้พื้นฐานทางคณิตศาสตร์ เทคนิค และกลยุทธ์ที่จำเป็นสำหรับระบบเทรด AI แบบ Multi-Agent เพื่อ:

- **ให้สภาพคล่อง** บน Automated Market Maker (AMM) และรับค่าธรรมเนียมการเทรด
- **ลด Impermanent Loss ให้น้อยที่สุด** ผ่านการเฮดจ์แบบไดนามิกและการจัดการช่วงราคา
- **เพิ่มประสิทธิภาพผลตอบแทน** จากโปรโตคอลการให้กู้ การ Staking และการทำ Farming
- **ดำเนินกลยุทธ์ที่ใช้ Flash Loan** รวมถึงการทำ Arbitrage และการปรับโครงสร้างหลักประกัน
- **จัดการสถานะการให้กู้/ยืม** ด้วยการติดตาม Health Factor แบบอัตโนมัติ
- **สะสมผลตอบแทน** ผ่านกลไก Liquid Staking และ Restaking

### 1.2 หลักการออกแบบ

เอกสารทุกฉบับในโมดูลนี้ยึดตามโครงสร้างดังนี้:

| หมวด | วัตถุประสงค์ |
|------|-------------|
| ตรรกะหลัก | กลไกโดยละเอียดของโปรโตคอลหรือกลยุทธ์ |
| ข้อกำหนดทางเทคนิค | เกณฑ์ พารามิเตอร์ ค่าคงที่ที่แม่นยำ |
| แบบจำลองทางคณิตศาสตร์ | สูตรทั้งหมดในรูปแบบ LaTeX |
| พารามิเตอร์ความเสี่ยง | ความเสี่ยงที่ระบุพร้อมระดับความรุนแรงและการบรรเทา |
| ขั้นตอนการทำงาน | Pseudocode สำหรับการนำบอทไปใช้งาน |
| เอกสารอ้างอิง | บทความวิชาการ Whitepaper เอกสารโปรโตคอล |

---

## 2. สถาปัตยกรรมระบบนิเวศ DeFi

### 2.1 แบบจำลองชั้น (Layer Model)

ระบบนิเวศ DeFi สามารถเข้าใจได้เป็นสถาปัตยกรรมแบบชั้น โดยแต่ละชั้นสร้างบนชั้นด้านล่าง:

```
Layer 5 — ตัวรวบรวมและอินเทอร์เฟซ (Aggregators & Interfaces)
         DEX aggregators (1inch, Paraswap), yield aggregators (Yearn),
         portfolio dashboards (Zapper, DeBank)

Layer 4 — โปรโตคอลแอปพลิเคชัน (Application Protocols)
         Lending (Aave, Compound), DEXes (Uniswap, Curve),
         Derivatives (dYdX, GMX), Insurance (Nexus Mutual)

Layer 3 — ชั้นสินทรัพย์ (Asset Layer)
         ERC-20 tokens, wrapped assets (WETH, WBTC),
         stablecoins (USDC, DAI), LP tokens, receipt tokens

Layer 2 — พื้นฐานของโปรโตคอล (Protocol Primitives)
         AMM invariants, interest rate models, oracle feeds,
         liquidation engines, governance modules

Layer 1 — ชั้นการชำระเงิน (Settlement Layer)
         Ethereum mainnet, L2 rollups (Arbitrum, Optimism, Base),
         alt-L1s (Solana, Avalanche)

Layer 0 — ฉันทามติและความปลอดภัย (Consensus & Security)
         Proof of Stake validators, MEV supply chain,
         block producers, relay networks
```

### 2.2 แผนผังการไหลของมูลค่า

```
Users (Traders, LPs, Borrowers)
    |
    v
Front-ends / Aggregators
    |
    v
Smart Contract Protocols <---> Oracles (Chainlink, Pyth)
    |
    v
Liquidity Pools / Lending Markets
    |
    v
Settlement Layer (L1/L2)
    |
    v
Block Producers / MEV Supply Chain
```

### 2.3 ผู้มีส่วนร่วมหลัก

| ผู้มีส่วนร่วม | บทบาท | แรงจูงใจ |
|---------------|--------|---------|
| ผู้ให้สภาพคล่อง (Liquidity Providers) | ฝากสินทรัพย์เข้าพูล | ค่าธรรมเนียมการเทรด + รางวัลโทเคน |
| เทรดเดอร์ (Traders) | สวอปโทเคนผ่าน AMM pools | การดำเนินการด้านราคา |
| ผู้กู้ (Borrowers) | กู้เงินโดยมีหลักประกัน | เลเวอเรจ, ชอร์ต |
| ผู้ให้กู้ (Lenders) | ให้สินทรัพย์แก่ตลาดการให้กู้ | รายได้ดอกเบี้ย |
| ผู้ชำระบัญชี (Liquidators) | ปิดสถานะที่มีหลักประกันไม่เพียงพอ | โบนัสจากการ Liquidate |
| นักอาร์บิทราจ (Arbitrageurs) | ทำให้ราคาเท่ากันข้ามตลาด | กำไรจากส่วนต่างราคา |
| ผู้ถือ Governance | โหวตพารามิเตอร์ของโปรโตคอล | อิทธิพลต่อโปรโตคอล + ผลตอบแทน |
| MEV searchers | ดึงมูลค่าจากการจัดลำดับธุรกรรม | กำไร MEV |

---

## 3. โปรโตคอลหลักและบทบาท

### 3.1 ตลาดแลกเปลี่ยนแบบกระจายศูนย์ (DEXes)

#### 3.1.1 Uniswap (V2, V3, V4)

- **กลไก**: Automated Market Maker ที่มี constant product (V2) และ concentrated liquidity (V3/V4)
- **เชน**: Ethereum mainnet + การ deploy บน L2 (Arbitrum, Optimism, Base, Polygon)
- **TVL**: ในอดีต $3B-$8B ทั่วทุก deployment
- **ความเกี่ยวข้องกับระบบเทรด**:
  - ช่องทางหลักสำหรับการสวอปโทเคน long-tail
  - รายได้จากค่าธรรมเนียม LP (ระดับ 0.01%, 0.05%, 0.30%, 1.00% ใน V3)
  - Concentrated liquidity ช่วยให้การทำตลาดมีประสิทธิภาพทุน
  - V4 hooks เปิดให้ใช้ตรรกะกำหนดเอง (ค่าธรรมเนียมแบบไดนามิก, TWAMM, limit orders)

#### 3.1.2 Curve Finance

- **กลไก**: StableSwap invariant ที่ปรับให้เหมาะสำหรับสินทรัพย์ที่มีราคาสัมพันธ์กัน
- **ความเชี่ยวชาญ**: การสวอป stablecoin-to-stablecoin และสินทรัพย์ที่ผูกค่า
- **TVL**: ในอดีต $2B-$6B
- **นวัตกรรมหลัก**: Slippage ต่ำมากสำหรับสินทรัพย์ที่มีมูลค่าใกล้เคียงกัน
- **CRV Wars**: รูปแบบ veTokenomics ที่โปรโตคอลต่างๆ แข่งขันเพื่อ CRV emissions เพื่อนำสภาพคล่องไปยังพูลของตน

#### 3.1.3 Balancer

- **กลไก**: พูลแบบถ่วงน้ำหนักทั่วไป (อัตราส่วนใดก็ได้ ไม่จำกัดแค่ 50/50)
- **นวัตกรรม**: คณิตศาสตร์แบบถ่วงน้ำหนักช่วยให้มีการเปิดรับความเสี่ยงแบบไม่สมมาตร
- **ความเกี่ยวข้อง**: เหมาะสำหรับสถานะ LP แบบพอร์ตโฟลิโอ (เช่น 80/20 ETH/USDC)

### 3.2 การให้กู้และยืม (Lending & Borrowing)

#### 3.2.1 Aave (V3)

- **กลไก**: การให้กู้แบบมีหลักประกันเกินมูลค่า พร้อมอัตราดอกเบี้ยแบบลอยตัวและคงที่
- **ฟีเจอร์หลัก**: E-Mode (efficiency mode) สำหรับสินทรัพย์ที่สัมพันธ์กัน ให้ LTV สูงกว่า
- **Flash Loans**: สินเชื่อแบบไม่ต้องมีหลักประกันในธุรกรรมเดียว
- **ข้ามเชน**: ฟีเจอร์ Portal สำหรับสภาพคล่องข้ามเชน
- **ความเสี่ยง**: แบบจำลองอัตราดอกเบี้ย, การพึ่งพา Oracle, ความเสี่ยงด้าน Governance

#### 3.2.2 Compound (V3 — Comet)

- **กลไก**: โมเดลสินทรัพย์กู้ยืมเดี่ยว (เช่น กู้ได้เฉพาะ USDC)
- **ความเรียบง่าย**: ลดพื้นผิวการโจมตีเทียบกับตลาดแบบหลายสินทรัพย์
- **COMP Rewards**: การแจกจ่ายโทเคน Governance ให้ผู้ใช้

### 3.3 Liquid Staking

#### 3.3.1 Lido (stETH)

- **กลไก**: การ Stake ETH แบบรวมพูลพร้อมโทเคนอนุพันธ์สภาพคล่อง (stETH)
- **ส่วนแบ่งตลาด**: ~30% ของ ETH ที่ถูก Stake ทั้งหมด (ผู้ให้บริการ liquid staking ชั้นนำ)
- **แหล่งผลตอบแทน**: รางวัลจากชั้น consensus ของ Ethereum + ค่าธรรมเนียมจากชั้น execution
- **ความเสี่ยง**: Smart contract, การถูก Slash, stETH/ETH de-peg

#### 3.3.2 Rocket Pool (rETH)

- **กลไก**: เครือข่าย node operator แบบกระจายศูนย์
- **ข้อได้เปรียบ**: กระจายศูนย์มากกว่า Lido
- **โมเดล rETH**: โทเคนที่มูลค่าเพิ่มขึ้น (มูลค่าเพิ่มเทียบกับ ETH เมื่อเวลาผ่านไป)

### 3.4 Restaking

#### 3.4.1 EigenLayer

- **กลไก**: นำ ETH ที่ Stake แล้วมาใช้ซ้ำเพื่อรักษาความปลอดภัยให้โปรโตคอลเพิ่มเติม (AVSs)
- **การสะสมผลตอบแทน**: ผลตอบแทนจาก Ethereum staking + รางวัล AVS
- **ความเสี่ยง**: เงื่อนไขการ Slash ที่เพิ่มขึ้น, ความเสี่ยง Smart contract, ความซับซ้อน

### 3.5 ตัวรวบรวมผลตอบแทน (Yield Aggregators)

#### 3.5.1 Yearn Finance

- **กลไก**: กลยุทธ์ Vault อัตโนมัติที่เพิ่มประสิทธิภาพผลตอบแทนข้ามโปรโตคอล
- **กลยุทธ์**: ฝากสินทรัพย์ -> vault จัดสรรไปยังแหล่งผลตอบแทนที่ดีที่สุด
- **ค่าธรรมเนียม**: ค่าธรรมเนียมการจัดการ + ค่าธรรมเนียมผลงานจากกำไร

#### 3.5.2 Beefy Finance

- **กลไก**: Vault ทบต้นอัตโนมัติข้ามหลายเชน
- **โฟกัส**: เก็บรางวัล -> ขาย -> ทบต้นเข้าสถานะ LP

### 3.6 อนุพันธ์ (Derivatives)

#### 3.6.1 GMX / dYdX

- **กลไก**: Perpetual futures ที่ชำระบัญชีบนเชน
- **ความเกี่ยวข้อง**: การเฮดจ์ IL, กลยุทธ์ delta-neutral, basis trading

### 3.7 ตารางเปรียบเทียบโปรโตคอล

| โปรโตคอล | หมวด | โมเดลค่าธรรมเนียม | ระดับความเสี่ยง | ประสิทธิภาพทุน | ความสามารถในการประกอบร่วม |
|----------|------|-------------------|---------------|---------------|------------------------|
| Uniswap V3 | DEX | 0.01-1% ต่อการสวอป | ปานกลาง | สูงมาก | สูงมาก |
| Curve | DEX | 0.04% ต่อการสวอป | ปานกลาง | สูง (stables) | สูงมาก |
| Aave V3 | Lending | ดอกเบี้ยลอยตัว | ปานกลาง | สูง | สูงมาก |
| Lido | Staking | 10% ของรางวัล | ปานกลาง | สูง | สูง |
| EigenLayer | Restaking | กำหนดโดย AVS | สูง | ปานกลาง | ปานกลาง |
| Yearn | Aggregator | 2% + 20% perf | ปานกลาง-สูง | สูง | ปานกลาง |

---

## 4. กรอบความเสี่ยงของ Smart Contract

### 4.1 อนุกรมวิธานความเสี่ยง (Risk Taxonomy)

ความเสี่ยงจาก Smart contract เป็นหมวดความเสี่ยงที่สำคัญที่สุดใน DeFi แตกต่างจากการเงินแบบดั้งเดิมที่ความเสี่ยงจากคู่สัญญาถูกบรรเทาด้วยกฎระเบียบและประกัน ความเสี่ยงใน DeFi เป็นเรื่องทางเทคนิคเป็นหลัก

```
Smart Contract Risk
├── ความเสี่ยงระดับโค้ด (Code-Level Risks)
│   ├── Re-entrancy attacks
│   ├── Integer overflow/underflow
│   ├── Access control vulnerabilities
│   ├── Logic errors in state transitions
│   ├── Flash loan attack vectors
│   └── Oracle manipulation
├── ความเสี่ยงระดับการออกแบบ (Design-Level Risks)
│   ├── Economic model failures (death spirals)
│   ├── Governance attacks (vote manipulation)
│   ├── Incentive misalignment
│   └── Composability risk (cascading failures)
├── ความเสี่ยงด้านโครงสร้างพื้นฐาน (Infrastructure Risks)
│   ├── Bridge exploits (cross-chain risk)
│   ├── Oracle failure or manipulation
│   ├── RPC / node reliability
│   └── MEV extraction (sandwich attacks)
└── ความเสี่ยงด้านปฏิบัติการ (Operational Risks)
    ├── Admin key compromise
    ├── Upgrade proxy manipulation
    ├── Timelock bypass
    └── Frontend compromise (DNS hijack)
```

### 4.2 แบบจำลองการให้คะแนนความเสี่ยง

สำหรับระบบเทรด การโต้ตอบกับแต่ละโปรโตคอลจะถูกให้คะแนน:

$$
R_{total} = w_1 \cdot R_{audit} + w_2 \cdot R_{tvl} + w_3 \cdot R_{age} + w_4 \cdot R_{complexity} + w_5 \cdot R_{admin}
$$

โดยที่:

| ปัจจัย | น้ำหนัก ($w_i$) | ช่วงคะแนน | คำอธิบาย |
|--------|----------------|-----------|---------|
| $R_{audit}$ | 0.25 | 0-10 | จำนวนและคุณภาพของการตรวจสอบ |
| $R_{tvl}$ | 0.20 | 0-10 | TVL เป็นตัวแทนของการทดสอบจากการใช้งานจริง |
| $R_{age}$ | 0.15 | 0-10 | ระยะเวลาตั้งแต่ deploy โดยไม่ถูกโจมตี |
| $R_{complexity}$ | 0.25 | 0-10 | ความซับซ้อนของโค้ด จำนวน external calls |
| $R_{admin}$ | 0.15 | 0-10 | ระดับการควบคุมของ admin / ความสามารถในการอัปเกรด |

**การจัดประเภทความเสี่ยง**:

| ช่วงคะแนน | การจัดประเภท | การจัดสรรสูงสุด |
|-----------|-------------|----------------|
| 8.0 - 10.0 | ความเสี่ยงต่ำ | สูงสุด 30% ของการจัดสรร DeFi |
| 6.0 - 7.9 | ความเสี่ยงปานกลาง | สูงสุด 15% ของการจัดสรร DeFi |
| 4.0 - 5.9 | ความเสี่ยงสูงขึ้น | สูงสุด 5% ของการจัดสรร DeFi |
| 0.0 - 3.9 | ความเสี่ยงสูง | ไม่จัดสรร (ติดตามเท่านั้น) |

### 4.3 การวิเคราะห์การโจมตีในอดีต

| วันที่ | โปรโตคอล | ความเสียหาย | เวกเตอร์การโจมตี | บทเรียน |
|--------|----------|------------|------------------|---------|
| 2022-03 | Ronin Bridge | $624M | Compromised validator keys | ความเสี่ยง bridge แบบรวมศูนย์ |
| 2022-02 | Wormhole | $320M | Signature verification bug | ความซับซ้อนของข้ามเชน |
| 2022-04 | Beanstalk | $182M | Flash loan governance | พื้นผิวการโจมตีด้าน Governance |
| 2023-03 | Euler Finance | $197M | Donation + liquidation | เวกเตอร์การโจมตีรูปแบบใหม่ |
| 2023-07 | Curve Finance | $73M | Vyper compiler re-entrancy | ช่องโหว่ระดับคอมไพเลอร์ |

### 4.4 ข้อกำหนดการตรวจสอบสำหรับระบบเทรด

ก่อนที่ระบบเทรดจะโต้ตอบกับโปรโตคอลใดๆ การตรวจสอบต่อไปนี้ต้องผ่าน:

```
AUDIT CHECKLIST:
[x] At least 2 independent audits by reputable firms
[x] Bug bounty program active (minimum $500K)
[x] TVL > $100M for at least 6 months
[x] No critical exploits in past 12 months
[x] Open-source and verified on block explorer
[x] Timelock on admin functions (minimum 48 hours)
[x] No single admin key — multisig required
[x] Oracle diversity (not single oracle dependency)
```

---

## 5. การวิเคราะห์มูลค่ารวมที่ถูกล็อก (TVL)

### 5.1 TVL ในฐานะตัวชี้วัดสุขภาพตลาด

มูลค่ารวมที่ถูกล็อก (Total Value Locked หรือ TVL) แสดงถึงมูลค่ารวมของสินทรัพย์ที่ถูกฝากไว้ในโปรโตคอล DeFi ซึ่งทำหน้าที่เป็นตัวแทนของ:

- **ความเชื่อมั่นในโปรโตคอล**: TVL ที่สูงกว่าหมายถึงความมั่นใจของผู้ใช้ที่มากกว่า
- **ความลึกของสภาพคล่อง**: TVL ที่มากขึ้นโดยทั่วไปหมายถึง slippage ที่ต่ำลงสำหรับการเทรด
- **โอกาสด้านผลตอบแทน**: ไดนามิกส์ของ TVL สร้างส่วนต่างของผลตอบแทน
- **อารมณ์ตลาด**: แนวโน้ม TVL สัมพันธ์กับวงจรตลาดคริปโตที่กว้างขึ้น

### 5.2 การคำนวณ TVL

$$
TVL_{protocol} = \sum_{i=1}^{N} Q_i \cdot P_i
$$

โดยที่:
- $Q_i$ = ปริมาณของโทเคน $i$ ที่ถูกฝากในโปรโตคอล
- $P_i$ = ราคา USD ปัจจุบันของโทเคน $i$
- $N$ = จำนวนประเภทโทเคนทั้งหมดในโปรโตคอล

**ข้อควรระวังสำคัญ**: TVL คิดเป็น USD ดังนั้นจะเปลี่ยนแปลงตามราคาสินทรัพย์แม้ว่าจะไม่มีการฝาก/ถอน การวิเคราะห์ TVL ที่แท้จริงควรแยกส่วน:

$$
\Delta TVL = \Delta TVL_{flow} + \Delta TVL_{price}
$$

โดยที่:
- $\Delta TVL_{flow}$ = การเปลี่ยนแปลง TVL จากการฝาก/ถอนจริง
- $\Delta TVL_{price}$ = การเปลี่ยนแปลง TVL จากการเคลื่อนไหวของราคาสินทรัพย์

### 5.3 ความสัมพันธ์ระหว่าง TVL กับผลตอบแทน

โดยทั่วไปมีความสัมพันธ์ผกผันระหว่าง TVL ของพูลและผลตอบแทน:

$$
Y_{fee} \approx \frac{V_{daily} \cdot f}{TVL}
$$

โดยที่:
- $Y_{fee}$ = ผลตอบแทนจากค่าธรรมเนียมรายวัน
- $V_{daily}$ = ปริมาณการเทรดรายวัน
- $f$ = อัตราค่าธรรมเนียม
- $TVL$ = มูลค่ารวมที่ถูกล็อกในพูล

หมายความว่า:
- **TVL ต่ำ + ปริมาณสูง** = ผลตอบแทนสูง (แต่ความเสี่ยงสูงกว่า)
- **TVL สูง + ปริมาณต่ำ** = ผลตอบแทนต่ำ (แต่เสถียรกว่า)

### 5.4 สัญญาณจากการวิเคราะห์ TVL สำหรับการเทรด

| สัญญาณ | การตีความ | การดำเนินการ |
|--------|----------|-------------|
| TVL เพิ่ม + ปริมาณเพิ่ม | โปรโตคอลเติบโต สุขภาพดี | พิจารณาเข้า LP |
| TVL เพิ่ม + ปริมาณคงที่ | การเจือจางจาก yield farming | ติดตาม yield compression |
| TVL ลด + ปริมาณเสถียร | เงินฉลาดกำลังออก | ทบทวนความเสี่ยง พิจารณาออก |
| TVL ลด + ปริมาณลด | โปรโตคอลกำลังเสื่อม | ออกจากสถานะ |
| TVL พุ่งกะทันหัน | วาฬฝาก หรือเปิด incentive | วิเคราะห์ความยั่งยืน |
| TVL ลดกะทันหัน | อาจถูก exploit หรือเกิดความกลัว | ประเมินความเสี่ยงทันที |

### 5.5 การกระจายตัวของ TVL ข้ามเชน

ระบบเทรดติดตามการกระจายตัวของ TVL ข้ามเชนเพื่อระบุ:

- **Yield arbitrage**: โปรโตคอลเดียวกัน เชนต่างกัน ผลตอบแทนต่างกัน
- **การย้ายสภาพคล่อง**: ทุนไหลจากเชนหนึ่งไปอีกเชนหนึ่ง
- **โอกาสบนเชนใหม่**: TVL ช่วงแรกบนเชนใหม่มักหมายถึงผลตอบแทนที่สูงกว่า

```
TVL Distribution Snapshot (Illustrative):
Ethereum:      55-60% of total DeFi TVL
Tron:          10-12%
BSC:           5-8%
Arbitrum:      4-6%
Solana:        3-5%
Avalanche:     2-3%
Optimism:      2-3%
Base:          2-3%
Polygon:       1-2%
Others:        5-10%
```

---

## 6. ความสามารถในการประกอบร่วมของ DeFi — Money Legos

### 6.1 Composability คืออะไร?

Composability เป็นข้อได้เปรียบที่กำหนดลักษณะของ DeFi เทียบกับการเงินแบบดั้งเดิม หมายความว่าโปรโตคอลใดๆ สามารถรวมกับโปรโตคอลอื่นใดในธุรกรรมเดียว โดยไม่ต้องขออนุญาต เป็นไปได้เพราะ:

1. **อินเทอร์เฟซแบบเปิด**: Smart contract เปิดฟังก์ชันสาธารณะที่ใครก็เรียกได้
2. **สถานะร่วม (Shared state)**: ทุกโปรโตคอลอ่านจากสถานะบล็อกเชนเดียวกัน
3. **การทำงานแบบ Atomic**: การโต้ตอบกับหลายโปรโตคอลดำเนินการในธุรกรรมเดียว (สำเร็จทั้งหมดหรือย้อนกลับทั้งหมด)
4. **การรวมแบบไม่ต้องขออนุญาต**: ไม่ต้องใช้ API keys ไม่ต้องมีข้อตกลง ไม่ต้องมีการอนุมัติ

### 6.2 รูปแบบ Composability

#### รูปแบบที่ 1: การสะสมผลตอบแทน (Yield Stacking)

```
ETH -> Lido (stETH) -> Aave (deposit as collateral) -> Borrow USDC -> Curve (LP)
```

**แหล่งผลตอบแทน**:
- ชั้นที่ 1: ผลตอบแทนจากการ Stake ETH (~3-5% APR)
- ชั้นที่ 2: ผลตอบแทนจาก Aave supply ที่อาจได้สำหรับ stETH
- ชั้นที่ 3: ค่าธรรมเนียม Curve LP + รางวัล CRV บน USDC ที่กู้มา

**ความเสี่ยง**: แต่ละชั้นเพิ่มความเสี่ยง Smart contract และความเสี่ยงการ Liquidation

#### รูปแบบที่ 2: Leveraged Yield Farming

```
USDC -> Aave (deposit) -> Borrow ETH -> Uniswap V3 (LP ETH/USDC) -> Fees
                ^                                                      |
                |______________________ Repay loop ____________________|
```

#### รูปแบบที่ 3: Flash Loan Arbitrage

```
Aave Flash Loan (borrow USDC)
  -> Uniswap (buy ETH cheap)
  -> Curve (sell ETH for more USDC)
  -> Repay flash loan + fee
  -> Profit
```

#### รูปแบบที่ 4: การเพิ่มประสิทธิภาพหลักประกัน (Collateral Optimization)

```
Aave (deposit ETH, borrow USDC)
  -> Flash Loan (borrow DAI)
  -> Swap DAI for ETH
  -> Deposit ETH in Aave (increase collateral)
  -> Borrow more USDC
  -> Repay flash loan
  -> Net: Leveraged long ETH
```

### 6.3 ความเสี่ยง Composability — การล่มสลายแบบต่อเนื่อง (Cascading Failures)

Composability ที่เปิดโอกาสให้กลยุทธ์ทรงพลัง ยังสร้างความเสี่ยงเชิงระบบด้วย:

```
Failure Cascade Example:

1. Oracle รายงานราคาผิดสำหรับ Token A
2. โปรโตคอลการให้กู้อนุญาตให้กู้โดยมีหลักประกันไม่เพียงพอ
3. โทเคนที่กู้มาถูกทิ้งบน DEX ทำให้ราคาร่วง
4. ตลาดให้กู้อื่นเริ่ม Liquidation
5. LP ของ DEX รับ Impermanent Loss มหาศาล
6. Yield farm ที่สร้างบน LP tokens เหล่านั้นล่มสลาย
7. Stablecoin ที่มี yield farm tokens เป็นหลักหนุนเกิด de-peg
```

**ตัวอย่างในอดีต**: การล่มสลายของ Terra/LUNA (พฤษภาคม 2022) แสดงให้เห็นว่า stablecoin ที่ล้มเหลวสามารถลุกลามไปทั่วทั้งระบบนิเวศ DeFi ได้

### 6.4 กราฟ Composability สำหรับระบบเทรด

ระบบเทรดจำลอง DeFi composability เป็นกราฟไม่มีวงจรแบบมีทิศทาง (Directed Acyclic Graph หรือ DAG):

```
Nodes: Protocols, assets, positions
Edges: Dependencies, collateral relationships, yield flows
Weight: Risk contribution, yield contribution
```

$$
R_{composite} = 1 - \prod_{i=1}^{N} (1 - R_i)
$$

โดยที่ $R_{composite}$ คือความเสี่ยงแบบประกอบของกลยุทธ์หลายโปรโตคอล และ $R_i$ คือความเสี่ยงเฉพาะของแต่ละชั้นโปรโตคอล สิ่งนี้แสดงว่าความเสี่ยงทบต้นอย่างรวดเร็ว:

| จำนวนชั้น | ความเสี่ยงเฉพาะ | ความเสี่ยงแบบประกอบ |
|-----------|----------------|-------------------|
| 1 | 2% | 2.0% |
| 2 | 2% | 3.96% |
| 3 | 2% | 5.88% |
| 4 | 2% | 7.76% |
| 5 | 2% | 9.61% |

---

## 7. เหตุใด DeFi จึงสำคัญต่อการเทรดแบบอัลกอริทึม

### 7.1 ข้อได้เปรียบที่เป็นเอกลักษณ์

#### 7.1.1 การดำเนินการที่โปรแกรมได้ (Programmable Execution)

DeFi ช่วยให้ระบบเทรดเข้ารหัสกลยุทธ์หลายขั้นตอนที่ซับซ้อนในธุรกรรม atomic เดียว ในการเงินแบบดั้งเดิม กลยุทธ์ที่เกี่ยวข้องกับการกู้ การสวอป และการให้สภาพคล่องจะต้องมีคู่สัญญาหลายราย ระยะเวลาชำระ และการประสานงานด้วยมือ ใน DeFi ดำเนินการได้ในบล็อกเดียว (~12 วินาทีบน Ethereum)

#### 7.1.2 Order Book / สถานะ AMM ที่โปร่งใส

สถานะ DeFi ทั้งหมดเป็นสาธารณะและสอบถามได้ ระบบเทรดสามารถ:

- อ่านทุนสำรองของทุกพูลแบบเรียลไทม์
- ติดตามทุกธุรกรรมที่รอดำเนินการใน mempool
- คำนวณราคาดำเนินการที่แน่นอนก่อนส่ง
- จำลองธุรกรรมก่อนส่ง (ผ่าน `eth_call`)

#### 7.1.3 ตลาด 24/7 ที่ไม่มีผู้เฝ้าประตู

DeFi ทำงานอย่างต่อเนื่อง ไม่มีชั่วโมงทำการตลาด ไม่มี circuit breakers (ในโปรโตคอลส่วนใหญ่) และไม่ต้องการการอนุมัติจากตลาด ซึ่งเปิดโอกาสให้:

- สร้างผลตอบแทนอย่างต่อเนื่อง
- ติดตาม arbitrage ตลอดเวลา
- ตอบสนองต่อเหตุการณ์ตลาดทันที

#### 7.1.4 การสร้างผลตอบแทนเป็นชั้นพื้นฐาน

ต่างจากตลาดแบบดั้งเดิมที่การถือสินทรัพย์เป็น passive DeFi ช่วยให้ทุกสินทรัพย์ทำงานได้:

$$
Y_{total} = Y_{staking} + Y_{lending} + Y_{LP} + Y_{farming} + Y_{restaking}
$$

พอร์ตโฟลิโอที่ปรับแต่งอย่างดีสามารถสร้างผลตอบแทนจากทุกส่วนประกอบพร้อมกัน

### 7.2 ความท้าทายสำหรับการเทรดแบบอัลกอริทึมใน DeFi

| ความท้าทาย | คำอธิบาย | การบรรเทา |
|------------|----------|----------|
| MEV | บอท front-run, back-run, sandwich การเทรด | Private mempools (Flashbots) |
| ค่า Gas | ค่าธรรมเนียมธุรกรรมกินกำไร | Gas optimization, deploy บน L2 |
| ความเสี่ยง Smart contract | บั๊กในโค้ดทำให้เงินถูกดูด | ตรวจสอบ audit, จำกัดสถานะ |
| Oracle latency | ราคาฟีดช้ากว่าตลาดจริง | ใช้หลายแหล่ง oracle |
| สภาพคล่องกระจัดกระจาย | สภาพคล่องกระจายข้ามเชน | การรวบรวมข้ามเชน |
| ความไม่แน่นอนด้านกฎระเบียบ | ภูมิทัศน์กฎหมายที่เปลี่ยนแปลง | ติดตามการปฏิบัติตาม |
| Impermanent loss | มูลค่า LP < มูลค่าการถือ | เฮดจ์, ปรับสมดุลแบบไดนามิก |

### 7.3 แหล่ง Alpha จาก DeFi สำหรับระบบเทรด

```
Alpha Source 1: AMM Liquidity Provision
  - รับค่าธรรมเนียมการเทรดจากการให้ concentrated liquidity
  - เพิ่มประสิทธิภาพช่วงราคาเพื่อเก็บค่าธรรมเนียมสูงสุด
  - เฮดจ์ความเสี่ยงทิศทาง

Alpha Source 2: Cross-Venue Arbitrage
  - ส่วนต่างราคาระหว่าง DEX-DEX
  - ส่วนต่างราคาระหว่าง DEX-CEX
  - ส่วนต่างราคาข้ามเชน

Alpha Source 3: Lending Rate Arbitrage
  - กู้ในอัตราต่ำบน Protocol A
  - ให้กู้ในอัตราสูงกว่าบน Protocol B
  - รายได้ดอกเบี้ยสุทธิ

Alpha Source 4: Liquidation
  - ติดตามสถานะที่มีหลักประกันไม่เพียงพอ
  - ดำเนินการ Liquidation เพื่อกำไร
  - ต้องการการดำเนินการที่รวดเร็วและทุน

Alpha Source 5: Yield Optimization
  - หมุนทุนไปยังผลตอบแทนที่ปรับตามความเสี่ยงสูงสุด
  - ทบต้นรางวัลอัตโนมัติ
  - ลดค่า Gas ให้น้อยที่สุด

Alpha Source 6: Governance Value Extraction
  - โทเคนแบบ vote-escrowed (veTokens) ควบคุม emissions
  - แพลตฟอร์มสินบน (Votium, Hidden Hand)
  - การสะสมโทเคน Governance
```

---

## 8. แผนผังโมดูล — เนื้อหาที่ครอบคลุม

โมดูล DeFi Mechanics นี้ประกอบด้วยเอกสารดังนี้:

```
02_defi_mechanics/
├── 00_overview.md                      [ไฟล์นี้]
│   ภาพรวม แผนผังระบบนิเวศ กรอบความเสี่ยง
│
├── 01_amm_concentrated_liquidity.md
│   คณิตศาสตร์ AMM (CPMM, StableSwap, Weighted),
│   Uniswap V3 concentrated liquidity เชิงลึก,
│   กลยุทธ์ LP และ JIT liquidity
│
├── 02_impermanent_loss.md
│   การอนุมาน IL, IL ที่ขยายสำหรับ concentrated LP,
│   กลยุทธ์การเฮดจ์, การวิเคราะห์จุดคุ้มทุน
│
├── 03_yield_strategies.md
│   กลไก Yield farming, คณิตศาสตร์การทบต้น,
│   กลยุทธ์ตัวรวบรวม, การเพิ่มประสิทธิภาพการ harvest
│
├── 04_flash_loans_composability.md
│   กลไก Flash loan, กรณีการใช้งาน (arb, collateral swap),
│   เวกเตอร์การโจมตี (สำหรับการป้องกัน), รูปแบบ composability
│
├── 05_lending_borrowing.md
│   แบบจำลองอัตราดอกเบี้ย, utilization rates,
│   กลไกการ Liquidation, recursive lending
│
└── 06_liquid_staking_restaking.md
    Liquid staking (Lido, Rocket Pool),
    restaking (EigenLayer), yield stacking
```

### 8.1 การพึ่งพาของเอกสาร

```
00_overview ──────────────────────────────────────────────────
    |         |          |           |          |           |
    v         v          v           v          v           v
  01_amm   02_IL    03_yield    04_flash   05_lending  06_staking
    |         |          |           |          |           |
    |    depends on     |      uses 01,05      |      uses 05
    |      01_amm       |           |          |           |
    |         |          |           |          |           |
    v         v          v           v          v           v
   [Combined Strategy Layer — uses all modules]
```

---

## 9. พารามิเตอร์ความเสี่ยง — ทั่วทั้งระบบ

### 9.1 ขีดจำกัดความเสี่ยง DeFi ระดับโลก

พารามิเตอร์เหล่านี้ควบคุมการเปิดรับ DeFi โดยรวมของระบบเทรด:

| พารามิเตอร์ | ค่า | เหตุผล |
|------------|------|--------|
| การจัดสรร DeFi สูงสุด (% ของ AUM) | 25% | จำกัดการเปิดรับ smart contract |
| การจัดสรรโปรโตคอลเดี่ยวสูงสุด | 10% | การกระจายข้ามโปรโตคอล |
| การจัดสรรเชนเดี่ยวสูงสุด | 15% | การบรรเทาความเสี่ยงระดับเชน |
| Health factor ขั้นต่ำ (lending) | 1.50 | บัฟเฟอร์เหนือเกณฑ์ liquidation |
| ความลึก composability สูงสุด | 3 ชั้น | จำกัดความเสี่ยงแบบต่อเนื่อง |
| ขีดจำกัดความทนทาน IL (ต่อสถานะ) | -5% | ออกหาก IL เกินเกณฑ์ |
| งบค่า Gas (% ของผลตอบแทน) | 15% | ให้แน่ใจว่าผลตอบแทนสุทธิเป็นบวกหลังหักค่า Gas |
| ทริกเกอร์ออกฉุกเฉิน | -10% | ขีดจำกัด drawdown ระดับพอร์ต DeFi |

### 9.2 ช่วงเวลาการติดตามสถานะ

| เมตริก | ความถี่การตรวจสอบ | เกณฑ์การแจ้งเตือน |
|--------|------------------|------------------|
| Health factor | ทุกบล็อก | ต่ำกว่า 1.80 |
| สถานะช่วงราคา LP | ทุก 30 วินาที | ราคาอยู่ภายใน 5% ของช่วง |
| การเปลี่ยนแปลงอัตราผลตอบแทน | ทุก 5 นาที | เปลี่ยน > 20% |
| การเปลี่ยนแปลง TVL | ทุก 15 นาที | ลด > 10% ใน 1 ชั่วโมง |
| เหตุการณ์ Smart contract | ทุกบล็อก | Pause events, admin txns |
| ส่วนเบี่ยงเบนราคา Oracle | ทุกบล็อก | > 2% จากราคาตลาด |
| ราคา Gas | ทุกบล็อก | เหนือขีดจำกัดความสามารถในการทำกำไร |

### 9.3 Circuit Breakers

```
IF any of these conditions are met, HALT all DeFi operations:

1. Protocol TVL drops > 25% in 1 hour
2. Oracle price deviates > 5% from multiple sources
3. Unrecognized admin transaction detected
4. Gas price exceeds 500 gwei sustained for 10 minutes
5. System health factor drops below 1.30 on any position
6. Smart contract pause event detected
7. Bridge exploit reported on any connected chain
8. Stablecoin de-peg > 2% (USDC, USDT, DAI)
```

---

## 10. ขั้นตอนการทำงาน — เครื่องสแกนโอกาส DeFi

### 10.1 Main Scanner Loop

```python
class DeFiOpportunityScanner:
    """
    Continuously scans DeFi protocols for yield opportunities,
    arbitrage, and risk events.
    """

    def __init__(self, config: DeFiConfig):
        self.protocols = config.approved_protocols
        self.risk_limits = config.risk_limits
        self.positions = PositionManager()
        self.oracle = MultiOracleAggregator()
        self.gas_estimator = GasEstimator()

    async def run_scan_loop(self):
        """Main scanning loop — runs continuously."""
        while True:
            try:
                # Phase 1: Data Collection
                market_state = await self.collect_market_state()

                # Phase 2: Risk Check on Existing Positions
                risk_alerts = await self.check_position_health(market_state)
                if risk_alerts.has_critical():
                    await self.execute_emergency_actions(risk_alerts)
                    continue

                # Phase 3: Opportunity Identification
                opportunities = await self.identify_opportunities(market_state)

                # Phase 4: Risk-Adjusted Ranking
                ranked = self.rank_opportunities(opportunities)

                # Phase 5: Execution Decision
                for opp in ranked:
                    if self.passes_risk_checks(opp):
                        if self.is_profitable_after_gas(opp):
                            await self.execute_opportunity(opp)

                # Phase 6: Position Maintenance
                await self.rebalance_existing_positions(market_state)

                await asyncio.sleep(self.config.scan_interval)

            except Exception as e:
                logger.error(f"Scanner error: {e}")
                await self.alert_system.notify(e)

    async def collect_market_state(self) -> MarketState:
        """Collect state from all monitored protocols in parallel."""
        tasks = []
        for protocol in self.protocols:
            tasks.append(protocol.get_state())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return MarketState(
            pool_states={p.name: r for p, r in zip(self.protocols, results)
                        if not isinstance(r, Exception)},
            gas_price=await self.gas_estimator.get_current(),
            oracle_prices=await self.oracle.get_all_prices(),
            timestamp=time.time()
        )

    async def identify_opportunities(self, state: MarketState) -> List[Opportunity]:
        """Identify all potential opportunities across DeFi."""
        opportunities = []

        # Check yield opportunities
        yield_opps = await self.yield_scanner.scan(state)
        opportunities.extend(yield_opps)

        # Check arbitrage opportunities
        arb_opps = await self.arb_scanner.scan(state)
        opportunities.extend(arb_opps)

        # Check liquidation opportunities
        liq_opps = await self.liquidation_scanner.scan(state)
        opportunities.extend(liq_opps)

        # Check LP rebalancing needs
        rebal_opps = await self.lp_scanner.scan(state)
        opportunities.extend(rebal_opps)

        return opportunities

    def rank_opportunities(self, opportunities: List[Opportunity]) -> List[Opportunity]:
        """Rank by risk-adjusted return."""
        for opp in opportunities:
            opp.score = (
                opp.expected_return
                * (1 - opp.risk_score)
                * opp.confidence
                / max(opp.gas_cost, 0.001)
            )
        return sorted(opportunities, key=lambda o: o.score, reverse=True)

    def passes_risk_checks(self, opp: Opportunity) -> bool:
        """Verify opportunity passes all risk parameters."""
        checks = [
            opp.protocol in self.approved_protocols,
            opp.risk_score <= self.risk_limits.max_risk_score,
            self.positions.exposure(opp.protocol) + opp.size
                <= self.risk_limits.max_protocol_allocation,
            self.positions.chain_exposure(opp.chain) + opp.size
                <= self.risk_limits.max_chain_allocation,
            opp.composability_depth <= self.risk_limits.max_composability_depth,
        ]
        return all(checks)

    def is_profitable_after_gas(self, opp: Opportunity) -> bool:
        """Ensure opportunity is profitable after gas costs."""
        gas_cost_usd = opp.estimated_gas * self.gas_price_gwei * ETH_PRICE / 1e9
        net_profit = opp.expected_return - gas_cost_usd
        return net_profit > self.risk_limits.min_profit_threshold
```

### 10.2 Position Health Monitor

```python
class PositionHealthMonitor:
    """
    Monitors all DeFi positions for risk events.
    Executes protective actions when thresholds breached.
    """

    async def check_all_positions(self, state: MarketState) -> List[RiskAlert]:
        alerts = []

        for position in self.positions.active():
            # Check lending health factor
            if position.type == PositionType.LENDING:
                hf = await self.calculate_health_factor(position, state)
                if hf < self.thresholds.critical_hf:  # 1.30
                    alerts.append(RiskAlert.CRITICAL_HEALTH_FACTOR(position, hf))
                elif hf < self.thresholds.warning_hf:  # 1.80
                    alerts.append(RiskAlert.WARNING_HEALTH_FACTOR(position, hf))

            # Check LP range status
            elif position.type == PositionType.LP:
                current_price = state.oracle_prices[position.pair]
                if not position.is_in_range(current_price):
                    alerts.append(RiskAlert.OUT_OF_RANGE(position, current_price))
                elif position.distance_to_boundary(current_price) < 0.05:
                    alerts.append(RiskAlert.NEAR_RANGE_BOUNDARY(position))

            # Check IL threshold
            if position.type == PositionType.LP:
                il = self.calculate_il(position, state)
                if il < self.thresholds.max_il:  # -5%
                    alerts.append(RiskAlert.IL_THRESHOLD(position, il))

            # Check TVL changes
            pool_tvl = state.get_pool_tvl(position.pool)
            if position.entry_tvl and pool_tvl < position.entry_tvl * 0.75:
                alerts.append(RiskAlert.TVL_DROP(position, pool_tvl))

        return alerts
```

---

## 11. เอกสารอ้างอิง

### บทความวิชาการ

1. Adams, H., Zinsmeister, N., Robinson, D. (2020). "Uniswap v2 Core."
   https://uniswap.org/whitepaper.pdf

2. Adams, H., Zinsmeister, N., Salem, M., Keefer, R., Robinson, D. (2021).
   "Uniswap v3 Core." https://uniswap.org/whitepaper-v3.pdf

3. Egorov, M. (2019). "StableSwap — Efficient Mechanism for Stablecoin Liquidity."
   Curve Finance Whitepaper.

4. Martinelli, F., Mushegian, N. (2019). "A Non-Custodial Portfolio Manager,
   Liquidity Provider, and Price Sensor." Balancer Whitepaper.

5. Daian, P., Goldfeder, S., Kell, T., et al. (2020). "Flash Boys 2.0:
   Frontrunning in Decentralized Exchanges, Miner Extractable Value, and Consensus
   Instability." IEEE Symposium on Security and Privacy.

6. Gudgeon, L., Perez, D., Harz, D., Livshits, B., Gervais, A. (2020).
   "The Decentralized Financial Crisis." Crypto Valley Conference.

### เอกสารโปรโตคอล

7. Aave V3 Documentation. https://docs.aave.com/
8. Compound V3 (Comet) Documentation. https://docs.compound.finance/
9. Lido Documentation. https://docs.lido.fi/
10. EigenLayer Documentation. https://docs.eigenlayer.xyz/
11. Yearn Finance Documentation. https://docs.yearn.fi/
12. Curve Finance Documentation. https://resources.curve.fi/

### แหล่งข้อมูล

13. DefiLlama — TVL aggregator. https://defillama.com/
14. Dune Analytics — On-chain data. https://dune.com/
15. Token Terminal — Protocol financials. https://tokenterminal.com/

---

> **เอกสารถัดไป**: [01_amm_concentrated_liquidity.md](./01_amm_concentrated_liquidity.md)
> — การเจาะลึกคณิตศาสตร์ AMM และกลไก Concentrated Liquidity
