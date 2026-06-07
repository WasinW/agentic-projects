# ระบบ Multi-Agent AI Trading — ฐานความรู้หลัก (ภาษาไทย)

> **วัตถุประสงค์**: เอกสารชุดนี้เป็นฐานข้อมูลหลักสำหรับการสร้างระบบ Multi-Agent AI เพื่อการเทรดในตลาด Forex และ Crypto โดยเปลี่ยน "แนวคิดการเทรด" ให้เป็น "อัลกอริทึมและตรรกะที่จับต้องได้" เน้นที่ความได้เปรียบเชิงสถิติ (Statistical Edge) และการบริหารความเสี่ยงระดับสถาบัน

> **ขอบเขต**: 52 เอกสาร | ~45,000+ บรรทัด | 2 แกนหลัก | 22 หมวดหมู่

---

## มาตรฐานเอกสาร

ทุกเอกสารในฐานความรู้นี้มีโครงสร้างที่สอดคล้องกัน:

| หัวข้อ | คำอธิบาย |
|--------|----------|
| **Core Logic** | ตรรกะการเข้า/ออกออเดอร์อย่างละเอียด |
| **Technical Specs** | เงื่อนไขเชิงปริมาณที่ต้องครบก่อนเปิดสถานะ |
| **Mathematical Models** | สูตรคณิตศาสตร์ในรูปแบบ LaTeX |
| **Risk Parameters** | Stop Loss, Take Profit, Risk-to-Reward พร้อมสถิติรองรับ |
| **Execution Flow** | ขั้นตอนแบบ Pseudocode พร้อมนำไปเขียนโค้ดต่อได้ |
| **References** | บทความวิชาการ หนังสือ และแหล่งอ้างอิง |

---

## แกนที่ 1: กลยุทธ์การเทรดขั้นสูง (Advanced Trading Strategies)

เน้นที่ **การวิเคราะห์กราฟ, Price Action, และ Market Structure** — ชั้นตัดสินใจ "เมื่อไหร่ควรเข้าและออก"

### 01. ทฤษฎีคลื่นเอลเลียต (Elliott Wave Theory)
> การวิเคราะห์คลื่นแบบ Fractal ด้วย Impulse/Corrective patterns และเป้าหมายราคา Fibonacci

| ไฟล์ | คำอธิบาย |
|------|----------|
| [00_overview.md](axis1_trading_strategies/01_elliott_wave/00_overview.md) | ประวัติ ปรัชญา ธรรมชาติแบบ Fractal จุดแข็ง/จุดอ่อนสำหรับ Algo Trading |
| [01_impulse_waves.md](axis1_trading_strategies/01_elliott_wave/01_impulse_waves.md) | โครงสร้างคลื่น 5 ขา, กฎเหล็ก 3 ข้อ, แนวทาง, Wave Extensions, Diagonals |
| [02_corrective_waves.md](axis1_trading_strategies/01_elliott_wave/02_corrective_waves.md) | Zigzag, Flat, Triangle, Complex Corrections (WXY/WXYXZ), กฎการเทรด |
| [03_fibonacci_targets.md](axis1_trading_strategies/01_elliott_wave/03_fibonacci_targets.md) | Retracement/Extension, Time Zones, Cluster Analysis, จุดกลับตัว |
| [04_wave_counting_algorithm.md](axis1_trading_strategies/01_elliott_wave/04_wave_counting_algorithm.md) | อัลกอริทึมนับคลื่นอัตโนมัติ, ZigZag, คะแนนความมั่นใจ, Alternate Counts |

### 02. วิธีไวคอฟฟ์และโครงสร้างตลาด (Wyckoff Method & Market Structure)
> การสะสม/กระจายของสถาบัน พร้อม Volume Confirmation และ Structure Breaks

| ไฟล์ | คำอธิบาย |
|------|----------|
| [00_overview.md](axis1_trading_strategies/02_wyckoff_market_structure/00_overview.md) | กฎ 3 ข้อ, แนวคิด Composite Man, 4 เฟสของตลาด |
| [01_accumulation_schematic.md](axis1_trading_strategies/02_wyckoff_market_structure/01_accumulation_schematic.md) | PS, SC, AR, ST, Spring, Test, SOS, LPS, BU — อัลกอริทึมตรวจจับ |
| [02_distribution_schematic.md](axis1_trading_strategies/02_wyckoff_market_structure/02_distribution_schematic.md) | PSY, BC, AR, ST, UTAD, LPSY, SOW — การให้คะแนน Distribution vs Re-accumulation |
| [03_market_structure_bos_choch.md](axis1_trading_strategies/02_wyckoff_market_structure/03_market_structure_bos_choch.md) | Break of Structure, Change of Character, Internal vs External |
| [04_wyckoff_volume_analysis.md](axis1_trading_strategies/02_wyckoff_market_structure/04_wyckoff_volume_analysis.md) | Volume Spread Analysis (VSA), Effort vs Result, สัญญาณ VSA หลัก |
| [05_execution_flow.md](axis1_trading_strategies/02_wyckoff_market_structure/05_execution_flow.md) | State Machine, Signal Pipeline, กรอบการ Backtest |

### 03. การวิเคราะห์ Order Flow และสภาพคล่อง (Order Flow & Liquidity)
> โครงสร้างจุลภาคของตลาด — Order Book, Liquidity Pools, กระแสเงินสถาบัน

| ไฟล์ | คำอธิบาย |
|------|----------|
| [00_overview.md](axis1_trading_strategies/03_order_flow_liquidity/00_overview.md) | พื้นฐาน Market Microstructure, โมเดล Maker/Taker |
| [01_order_book_analysis.md](axis1_trading_strategies/03_order_flow_liquidity/01_order_book_analysis.md) | L2 Data, Order Book Imbalance, ตรวจจับ Spoofing, Absorption |
| [02_liquidity_concepts.md](axis1_trading_strategies/03_order_flow_liquidity/02_liquidity_concepts.md) | BSL/SSL, Liquidity Voids, Fair Value Gaps, Breaker/Mitigation Blocks, OTE |
| [03_hft_stop_hunting.md](axis1_trading_strategies/03_order_flow_liquidity/03_hft_stop_hunting.md) | กลไก HFT, การล่า Stop Loss, Judas Swing, Kill Zones |
| [04_volume_delta_analysis.md](axis1_trading_strategies/03_order_flow_liquidity/04_volume_delta_analysis.md) | CVD Divergences, POC, VAH/VAL, VWAP Bands |
| [05_execution_flow.md](axis1_trading_strategies/03_order_flow_liquidity/05_execution_flow.md) | ระบบเทรด Order Flow ฉบับสมบูรณ์, Data Pipeline |

### 04. แนวคิด Smart Money (Smart Money Concepts - SMC)
> กระแสเงินสถาบัน — Order Blocks, โซน Premium/Discount, Kill Zones

| ไฟล์ | คำอธิบาย |
|------|----------|
| [01_smc_complete_guide.md](axis1_trading_strategies/04_smart_money_concepts/01_smc_complete_guide.md) | Order Blocks, Breaker Blocks, IOFED, Premium/Discount, โมเดลเข้าเทรด |

### 05. โซนอุปสงค์อุปทาน (Supply & Demand Zones)
> การเทรดตามโซน พร้อมระบบให้คะแนนคุณภาพและวิเคราะห์หลายไทม์เฟรม

| ไฟล์ | คำอธิบาย |
|------|----------|
| [01_supply_demand_complete.md](axis1_trading_strategies/05_supply_demand_zones/01_supply_demand_complete.md) | การระบุโซน, RBR/DBD/RBD/DBR, คะแนนคุณภาพ, โซนซ้อน |

### 06. รูปแบบฮาร์โมนิก (Harmonic Patterns)
> ระบบรู้จำรูปแบบ XABCD ด้วย Fibonacci พร้อมจุดกลับตัวที่เป็นไปได้ (PRZ)

| ไฟล์ | คำอธิบาย |
|------|----------|
| [01_harmonic_patterns_complete.md](axis1_trading_strategies/06_harmonic_patterns/01_harmonic_patterns_complete.md) | Gartley, Butterfly, Bat, Crab, Shark, Cypher, Three Drives |

### 07. การเทรด Price Action
> รูปแบบแท่งเทียน รูปแบบกราฟ และอัลกอริทึมแนวรับแนวต้าน

| ไฟล์ | คำอธิบาย |
|------|----------|
| [01_price_action_complete.md](axis1_trading_strategies/07_price_action/01_price_action_complete.md) | Pin Bar, Engulfing, H&S, สามเหลี่ยม, Wedges, อัลกอริทึมจดจำรูปแบบ |

### 08. การวิเคราะห์ Volume Profile
> Volume-at-Price — POC, Value Area, HVN/LVN, Market Profile

| ไฟล์ | คำอธิบาย |
|------|----------|
| [01_volume_profile_complete.md](axis1_trading_strategies/08_volume_profile_analysis/01_volume_profile_complete.md) | Volume Profile, TPO Charts, Initial Balance, Single Prints |

### 09. อิชิโมกุขั้นสูง (Ichimoku Kinko Hyo Advanced)
> ระบบ Cloud 5 องค์ประกอบ พร้อมพารามิเตอร์ปรับแต่งสำหรับ Crypto

| ไฟล์ | คำอธิบาย |
|------|----------|
| [01_ichimoku_advanced_complete.md](axis1_trading_strategies/09_ichimoku_advanced/01_ichimoku_advanced_complete.md) | วิเคราะห์ Kumo, TK Cross, Chikou Span, MTF Ichimoku |

### 10. การเทรด Divergence
> ตรวจจับ Divergence หลายตัวชี้วัดสำหรับสัญญาณกลับตัว/ต่อเนื่อง

| ไฟล์ | คำอธิบาย |
|------|----------|
| [01_divergence_trading_complete.md](axis1_trading_strategies/10_divergence_trading/01_divergence_trading_complete.md) | Regular/Hidden Divergence, RSI/MACD/Stochastic, Multi-indicator Confluence |

### 11. การวิเคราะห์หลายไทม์เฟรม (Multi-Timeframe Analysis)
> กรอบการวิเคราะห์จากบนลงล่าง พร้อมคะแนนความสอดคล้องของไทม์เฟรม

| ไฟล์ | คำอธิบาย |
|------|----------|
| [01_mtf_analysis_complete.md](axis1_trading_strategies/11_multi_timeframe_analysis/01_mtf_analysis_complete.md) | ลำดับชั้นไทม์เฟรม, คะแนนความสอดคล้อง, แก้ไขสัญญาณขัดแย้ง |

### 12. เทคนิค Fibonacci ขั้นสูง
> ชุดเครื่องมือ Fibonacci ครบวงจร — Clusters, Time Zones, Fans, Arcs

| ไฟล์ | คำอธิบาย |
|------|----------|
| [01_fibonacci_advanced_complete.md](axis1_trading_strategies/12_fibonacci_advanced/01_fibonacci_advanced_complete.md) | Clusters, AB=CD, Time Zones, Fans/Arcs, บูรณาการกับ Elliott Wave |

---

## แกนที่ 2: ผลิตภัณฑ์ทางการเงินและกลไกสร้าง Alpha (Financial Products & Alpha Mechanisms)

เน้นที่ **เครื่องมือทางการเงิน, Arbitrage, DeFi, และกลยุทธ์พอร์ตโฟลิโอ** — ชั้น "สร้างผลตอบแทนอย่างไร"

### 01. การเก็งกำไรส่วนต่าง (Arbitrage)
> Arbitrage แบบปลอดความเสี่ยงและเชิงสถิติ ข้ามตลาดและโปรโตคอล DeFi

| ไฟล์ | คำอธิบาย |
|------|----------|
| [00_overview.md](axis2_financial_products/01_arbitrage/00_overview.md) | การจำแนก Arbitrage, กฎราคาเดียว, ข้อกำหนดเทคโนโลยี |
| [01_triangular_arbitrage.md](axis2_financial_products/01_arbitrage/01_triangular_arbitrage.md) | คำนวณ Cross-rate, สูตรกำไรสุทธิ, วิเคราะห์ค่าธรรมเนียม |
| [02_funding_rate_arbitrage.md](axis2_financial_products/01_arbitrage/02_funding_rate_arbitrage.md) | กลยุทธ์ Delta Neutral, APY จาก Funding Rate, ความเสี่ยง Basis |
| [03_cross_exchange_arbitrage.md](axis2_financial_products/01_arbitrage/03_cross_exchange_arbitrage.md) | ตรวจจับส่วนต่างราคา, การวาง Position ล่วงหน้า, Latency Arbitrage |
| [04_mev_defi_arbitrage.md](axis2_financial_products/01_arbitrage/04_mev_defi_arbitrage.md) | ประเภท MEV, Flash Loan Arbitrage, Liquidation Arb, Solidity Code |
| [05_statistical_arbitrage_pairs.md](axis2_financial_products/01_arbitrage/05_statistical_arbitrage_pairs.md) | Cointegration, Z-score, Kalman Filter, Hurst Exponent |

### 02. กลไก DeFi ขั้นสูง (DeFi Mechanics)
> AMMs, Lending, Yield Optimization, และ Composability

| ไฟล์ | คำอธิบาย |
|------|----------|
| [00_overview.md](axis2_financial_products/02_defi_mechanics/00_overview.md) | ระบบนิเวศ DeFi, การจำแนกโปรโตคอล, คะแนนความเสี่ยง Smart Contract |
| [01_amm_concentrated_liquidity.md](axis2_financial_products/02_defi_mechanics/01_amm_concentrated_liquidity.md) | CPMM, Uniswap V3 Ticks, Concentrated Liquidity, Curve/Balancer, JIT |
| [02_impermanent_loss.md](axis2_financial_products/02_defi_mechanics/02_impermanent_loss.md) | สูตร IL, IL แบบขยาย, กลยุทธ์ Hedging, ปรับ Range แบบ Dynamic |
| [03_yield_strategies.md](axis2_financial_products/02_defi_mechanics/03_yield_strategies.md) | Yield Farming, Auto-compounding, Leverage Farming, หมุนกลยุทธ์ |
| [04_flash_loans_composability.md](axis2_financial_products/02_defi_mechanics/04_flash_loans_composability.md) | กลไก Flash Loan, Solidity Implementation, รูปแบบ Composability |
| [05_lending_borrowing.md](axis2_financial_products/02_defi_mechanics/05_lending_borrowing.md) | โมเดลอัตราดอกเบี้ย, Health Factor, Recursive Lending, Liquidation Bots |
| [06_liquid_staking_restaking.md](axis2_financial_products/02_defi_mechanics/06_liquid_staking_restaking.md) | Lido/Rocket Pool, EigenLayer Restaking, ซ้อน Yield, วิเคราะห์ความเสี่ยง |

### 03. อนุพันธ์และผลิตภัณฑ์ที่มีโครงสร้าง (Derivatives & Structured Products)
> Options, Futures, Perpetual Swaps, Structured Products, และการเทรด Volatility

| ไฟล์ | คำอธิบาย |
|------|----------|
| [00_overview.md](axis2_financial_products/03_derivatives_structured_products/00_overview.md) | การจำแนกอนุพันธ์, ภาพรวม Greeks, เปรียบเทียบ Crypto vs Traditional |
| [01_options_strategies.md](axis2_financial_products/03_derivatives_structured_products/01_options_strategies.md) | Black-Scholes, Greeks ทั้งหมด, 14+ กลยุทธ์ (Directional/Neutral/Vol/Hedge) |
| [02_futures_perpetual_swaps.md](axis2_financial_products/03_derivatives_structured_products/02_futures_perpetual_swaps.md) | กลไก Futures, Perpetual Swaps, Funding Rate, Hedging, Liquidation |
| [03_structured_products.md](axis2_financial_products/03_derivatives_structured_products/03_structured_products.md) | DOV, Shark Fin, Snowball, Barrier/Asian/Lookback Options, Monte Carlo |
| [04_volatility_trading.md](axis2_financial_products/03_derivatives_structured_products/04_volatility_trading.md) | IV vs RV, SABR Model, Variance Swaps, Gamma Scalping, Dispersion |
| [05_risk_management_framework.md](axis2_financial_products/03_derivatives_structured_products/05_risk_management_framework.md) | VaR, CVaR, Kelly Criterion, จัดการ Drawdown, Stress Test, Risk Parity |

### 04. การเทรดแบบกริด (Grid Trading)
> ระบบวางคำสั่งซื้อขายเป็นระเบียบสำหรับตลาด Sideway และ Trending

| ไฟล์ | คำอธิบาย |
|------|----------|
| [01_grid_trading_complete.md](axis2_financial_products/04_grid_trading/01_grid_trading_complete.md) | Arithmetic/Geometric Grid, Spot/Futures/Infinity, DCA Hybrid |

### 05. การกลับตัวหาค่าเฉลี่ย (Mean Reversion)
> กลยุทธ์ Mean Reversion เชิงสถิติ ด้วย Ornstein-Uhlenbeck และ Stationarity Tests

| ไฟล์ | คำอธิบาย |
|------|----------|
| [01_mean_reversion_complete.md](axis2_financial_products/05_mean_reversion/01_mean_reversion_complete.md) | OU Process, Hurst Exponent, Bollinger/Keltner, Z-score, Half-life |

### 06. โมเมนตัมและการตามเทรนด์ (Momentum & Trend Following)
> ระบบตามเทรนด์ — Moving Averages, Turtle Trading, Dual Momentum

| ไฟล์ | คำอธิบาย |
|------|----------|
| [01_momentum_trend_complete.md](axis2_financial_products/06_momentum_trend_following/01_momentum_trend_complete.md) | TSMOM/XSMOM, MA Crossovers, Donchian, ADX, Supertrend, Regime Detection |

### 07. การเก็งกำไรเชิงสถิติ (Statistical Arbitrage)
> Pairs Trading ด้วย Cointegration, Kalman Filters, และ PCA

| ไฟล์ | คำอธิบาย |
|------|----------|
| [01_stat_arb_complete.md](axis2_financial_products/07_statistical_arbitrage/01_stat_arb_complete.md) | Engle-Granger, Johansen, Dynamic Hedge Ratios, ML Enhancements |

### 08. การทำตลาด (Market Making)
> Market Making อัตโนมัติด้วย Avellaneda-Stoikov Optimal Quoting

| ไฟล์ | คำอธิบาย |
|------|----------|
| [01_market_making_complete.md](axis2_financial_products/08_market_making/01_market_making_complete.md) | จัดการ Bid-Ask, ความเสี่ยง Inventory, A-S Model, CEX vs DEX |

### 09. การเทรด Carry (Carry Trade)
> กลยุทธ์ส่วนต่างอัตราดอกเบี้ยและ Yield ใน Forex และ Crypto

| ไฟล์ | คำอธิบาย |
|------|----------|
| [01_carry_trade_complete.md](axis2_financial_products/09_carry_trade/01_carry_trade_complete.md) | ส่วนต่างดอกเบี้ย, Funding Rate Carry, Staking Yield, ความเสี่ยง Unwind |

### 10. การเทรด Correlation
> วิเคราะห์ Correlation ข้ามสินทรัพย์ ตรวจจับ Regime และสร้างพอร์ตโฟลิโอ

| ไฟล์ | คำอธิบาย |
|------|----------|
| [01_correlation_trading_complete.md](axis2_financial_products/10_correlation_trading/01_correlation_trading_complete.md) | Rolling Correlation, DCC-GARCH, Dollar Smile, BTC Dominance, Risk Parity |

---

## วิธีใช้ฐานความรู้นี้

### สำหรับ AI Agents
- **กฎตัดสินใจ** ในรูปแบบ IF conditions THEN action
- **สูตรคณิตศาสตร์** สำหรับการคำนวณที่แม่นยำ
- **Pseudocode** ที่แปลงเป็นโค้ดได้ทันที
- **พารามิเตอร์ความเสี่ยง** พร้อมค่า Default และช่วงที่ใช้ได้

### สำหรับนักพัฒนา
- เริ่มจาก `00_overview.md` ในแต่ละหัวข้อหลัก
- ใช้ **Execution Flow** เป็นแบบแปลนสำหรับ Implementation
- อ้างอิง **Technical Specs** สำหรับการปรับแต่งพารามิเตอร์
- เชื่อมโยงกลยุทธ์ด้วย **Multi-Timeframe Analysis** framework

### สถาปัตยกรรม Agent ที่แนะนำ
```
                    ┌──────────────────────────────┐
                    │   Portfolio Orchestrator       │
                    │   (การจัดการความเสี่ยง)         │
                    └──────────────┬───────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
    ┌─────────▼────────┐ ┌────────▼─────────┐ ┌───────▼────────┐
    │ Strategy Agent    │ │ Alpha Agent       │ │ Execution      │
    │ (แกนที่ 1)        │ │ (แกนที่ 2)        │ │ Agent          │
    │                   │ │                   │ │                │
    │ - Elliott Wave    │ │ - Arbitrage       │ │ - จัดการออเดอร์  │
    │ - Wyckoff         │ │ - DeFi Yield      │ │ - Slippage     │
    │ - Order Flow      │ │ - Options         │ │ - Latency      │
    │ - SMC/PA          │ │ - Grid/Trend      │ │ - Monitoring   │
    └───────────────────┘ └───────────────────┘ └────────────────┘
```

---

## ประวัติเวอร์ชัน

| วันที่ | เวอร์ชัน | การเปลี่ยนแปลง |
|--------|----------|----------------|
| 2026-04-12 | 1.0.0 | สร้างครั้งแรก — 52 เอกสาร 22 หมวดหมู่ (English) |
| 2026-04-12 | 1.0.0-TH | แปลเป็นภาษาไทยครบทั้ง 52 เอกสาร |

---

*สร้างขึ้นเป็นฐานความรู้หลักสำหรับระบบ Multi-Agent AI Trading*
*สูตรคณิตศาสตร์ใช้ LaTeX | Pseudocode พร้อมนำไป Implement*
