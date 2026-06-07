# กลยุทธ์ Carry Trade — เอกสารอ้างอิงฉบับสมบูรณ์

## ข้อมูลเอกสาร
| ฟิลด์ | ค่า |
|---|---|
| ประเภทกลยุทธ์ | Carry Trade / ส่วนต่างผลตอบแทน (Carry Trade / Yield Differential) |
| สินทรัพย์ | Forex, คริปโต (DeFi, Futures) |
| กรอบเวลา | หลายสัปดาห์ถึงหลายเดือน |
| ความซับซ้อน | ระดับกลาง |
| เงินทุนที่ต้องการ | ปานกลางถึงสูง |
| อัปเดตล่าสุด | 2026-04-12 |

---

## สารบัญ
1. [การเทรดส่วนต่างอัตราดอกเบี้ย](#1-interest-rate-differential-trading)
2. [Forex Carry Trade](#2-forex-carry-trade)
3. [กลยุทธ์ Carry ในคริปโต](#3-crypto-carry-strategies)
4. [Funding Rate Carry](#4-funding-rate-carry)
5. [ส่วนต่างอัตรา Staking และ Lending](#5-staking-and-lending-rate-differentials)
6. [ความเสี่ยง: การคลาย Carry Trade](#6-risk-carry-trade-unwind)
7. [Sharpe Ratio ของกลยุทธ์ Carry](#7-sharpe-ratio-of-carry-strategies)
8. [ตรรกะหลัก — การเข้า/ออกสถานะ](#8-core-logic--entryexit)
9. [ข้อมูลจำเพาะทางเทคนิค](#9-technical-specifications)
10. [แบบจำลองทางคณิตศาสตร์](#10-mathematical-models)
11. [พารามิเตอร์ความเสี่ยง](#11-risk-parameters)
12. [ขั้นตอนการดำเนินการ](#12-execution-flow)
13. [เอกสารอ้างอิง](#13-references)

---

## 1. การเทรดส่วนต่างอัตราดอกเบี้ย (Interest Rate Differential Trading)

### 1.1 Fundamental Principle

The carry trade exploits interest rate differentials between two assets or currencies. The core idea is simple:

> **Borrow in a low-interest-rate currency/asset, invest in a high-interest-rate currency/asset, and profit from the difference (the "carry").**

### 1.2 Carry Return Decomposition

The total return of a carry trade consists of:

$$R_{carry,total} = R_{carry} + R_{spot} + R_{roll}$$

Where:
- $R_{carry}$ = interest rate differential (the carry component)
- $R_{spot}$ = spot price change (exchange rate risk)
- $R_{roll}$ = roll yield from forward contract adjustment

**Expected Carry Return (per period):**

$$E[R_{carry}] = (r_{high} - r_{low}) \times \Delta t$$

Where:
- $r_{high}$ = interest rate of high-yield asset
- $r_{low}$ = interest rate of low-yield (funding) asset
- $\Delta t$ = holding period (in years)

### 1.3 Uncovered Interest Rate Parity (UIP)

UIP states that the expected spot exchange rate change should offset the interest rate differential:

$$E[\Delta S] = r_{domestic} - r_{foreign}$$

**If UIP holds perfectly, carry trades have zero expected profit.**

However, extensive empirical evidence shows that **UIP systematically fails** (the "forward premium puzzle"):
- High-interest-rate currencies tend to appreciate (or depreciate less than predicted)
- This violation of UIP is the source of carry trade returns

### 1.4 Covered Interest Rate Parity (CIP)

CIP is a no-arbitrage condition using forward contracts:

$$F = S \times \frac{(1 + r_d)}{(1 + r_f)}$$

Where:
- $F$ = forward exchange rate
- $S$ = spot exchange rate
- $r_d$ = domestic interest rate
- $r_f$ = foreign interest rate

CIP generally holds (to within transaction costs), meaning the forward rate incorporates the interest rate differential.

### 1.5 Carry as a Risk Premium

| Interpretation | Theory |
|---|---|
| Risk premium for crash risk | High-yield currencies crash during crises (peso problem) |
| Compensation for volatility | High-yielding assets tend to be more volatile |
| Behavioral explanation | Investors are slow to reallocate based on rate changes |
| Liquidity premium | Less liquid currencies offer higher yields |
| Disaster risk premium | Small probability of large loss compensated by steady carry |

---

## 2. Forex Carry Trade (การเทรด Carry ใน Forex)

### 2.1 Classic Forex Carry Pairs

**High-Yield (Long) Currencies:**

| Currency | Typical Rate Range | Characteristics |
|---|---|---|
| AUD (Australian Dollar) | 3-5% | Commodity-linked, China-sensitive |
| NZD (New Zealand Dollar) | 3-5.5% | Commodity-linked, smaller economy |
| MXN (Mexican Peso) | 8-12% | EM, US-linked, political risk |
| ZAR (South African Rand) | 6-9% | EM, commodity-linked |
| TRY (Turkish Lira) | 10-50% | EM, high inflation, political risk |
| BRL (Brazilian Real) | 8-14% | EM, commodity-linked |

**Low-Yield (Short/Funding) Currencies:**

| Currency | Typical Rate Range | Characteristics |
|---|---|---|
| JPY (Japanese Yen) | 0-0.5% | Traditional funding currency |
| CHF (Swiss Franc) | 0-1.5% | Safe haven, low rate |
| EUR (Euro) | 0-4% | Historically low rates (2015-2022) |
| USD | 0-5.5% | Variable; depends on Fed policy cycle |

### 2.2 Popular Carry Pairs

| Long (High Yield) | Short (Low Yield) | Typical Carry (Ann.) | Risk Level |
|---|---|---|---|
| AUD | JPY | 3-5% | Moderate |
| NZD | JPY | 3-5.5% | Moderate |
| MXN | JPY | 8-12% | High |
| ZAR | JPY | 6-9% | High |
| TRY | JPY | 10-40% | Very High |
| AUD | CHF | 2-4% | Low-Moderate |
| NZD | CHF | 2-4.5% | Low-Moderate |

### 2.3 Carry Trade Mechanics (Forex)

**Method 1: Spot + Swap (Rolling Spot)**

```
1. Borrow JPY at 0.25% per annum
2. Convert to AUD at spot rate
3. Invest AUD at 4.25% per annum
4. Net carry = 4.25% - 0.25% = 4.00% p.a.
5. Hold position; collect daily swap (overnight interest)
6. Risk: AUD/JPY exchange rate moves against you
```

**Daily Swap Payment:**

$$\text{Swap}_{daily} = \frac{(r_{long} - r_{short}) \times \text{Position Value}}{365}$$

**Method 2: Forward Contract**

```
1. Enter forward contract to buy AUD/sell JPY at forward rate F
2. F < S (forward discount due to rate differential)
3. If spot at expiry S_T > F: profit from carry + appreciation
4. If spot at expiry S_T < F but S_T > F - carry: still net profitable
5. If spot at expiry S_T < F - carry: loss (carry insufficient to offset depreciation)
```

### 2.4 Carry Trade Portfolio Construction

**G10 Carry Portfolio (Academic Standard):**

1. Sort G10 currencies by forward discount (proxy for interest rate)
2. Long top 3 (highest yield)
3. Short bottom 3 (lowest yield)
4. Equal-weight within each group
5. Rebalance monthly

**Dollar-Neutral Carry:**

$$w_i = \frac{r_i - \bar{r}}{\sum_i |r_i - \bar{r}|}$$

Where $r_i$ is the interest rate of currency $i$ and $\bar{r}$ is the cross-sectional average.

### 2.5 Expected Returns and Historical Performance

| Metric | G10 Carry | EM Carry | G10+EM Combined |
|---|---|---|---|
| Annual Return | 3-6% | 6-12% | 5-9% |
| Volatility | 8-12% | 12-18% | 9-14% |
| Sharpe Ratio | 0.3-0.6 | 0.4-0.7 | 0.4-0.7 |
| Max Drawdown | 15-30% | 25-50% | 20-40% |
| Skewness | Negative | Very Negative | Negative |
| Kurtosis | High (fat tails) | Very High | High |

---

## 3. กลยุทธ์ Carry ในคริปโต (Crypto Carry Strategies)

### 3.1 Overview of Crypto Carry Opportunities

Unlike forex where carry derives from central bank rates, crypto carry comes from multiple structural sources:

| Carry Source | Mechanism | Typical Yield (Ann.) |
|---|---|---|
| Funding Rate | Perp futures premium | 5-30% |
| Spot-Futures Basis | Cash-and-carry arbitrage | 3-20% |
| Staking Yield | PoS network rewards | 3-15% |
| Lending Rate Differential | Borrow low, lend high | 2-10% |
| Liquidity Provision | DEX fee income | 5-50%+ (with IL risk) |

### 3.2 Cash-and-Carry (Basis Trade)

The spot-futures basis trade is the crypto equivalent of a classic carry trade:

**Setup:**
1. Buy asset on spot market
2. Sell equivalent futures contract (at premium)
3. Profit = futures premium at expiry (the "basis")

**Basis Annualized Yield:**

$$\text{Basis Yield}_{ann} = \frac{F - S}{S} \times \frac{365}{T_{days}}$$

Where:
- $F$ = futures price
- $S$ = spot price
- $T_{days}$ = days to futures expiry

**Example (BTC):**
- BTC spot: $50,000
- BTC 3-month futures: $52,000
- Basis = $2,000 / $50,000 = 4.0% for 3 months
- Annualized = 4.0% * (365/90) = 16.2%

**Risk:**
- Requires margin for futures short (liquidation risk)
- Exchange counterparty risk
- Basis can widen temporarily (mark-to-market loss)
- Funding costs may erode profits

### 3.3 Perpetual Funding Rate Carry

Perpetual futures have a funding rate mechanism that keeps the perp price anchored to spot:

$$\text{Funding Rate} = \text{Interest Rate Component} + \text{Premium/Discount Component}$$

**When funding is positive (perps trading at premium to spot):**
- Longs pay shorts
- Strategy: Long spot + Short perp = Collect funding

**When funding is negative (perps trading at discount to spot):**
- Shorts pay longs
- Strategy: Short spot + Long perp = Collect funding

### 3.4 Cross-Protocol Yield Differential

Borrow on one protocol at a lower rate, lend on another at a higher rate:

```
Example:
1. Borrow USDC on Aave at 3.5% APY
2. Lend USDC on a higher-yield protocol at 8.0% APY
3. Net carry = 8.0% - 3.5% = 4.5% APY
4. Risk: Smart contract risk on both protocols, rate changes, liquidation

Enhanced Version (leveraged):
1. Deposit ETH as collateral on Aave
2. Borrow USDC at 3.5%
3. Deposit USDC on high-yield vault at 8.0%
4. Use vault tokens as additional collateral (if supported)
5. Loop 2-3x for leveraged carry
```

---

## 4. การ Carry จาก Funding Rate

### 4.1 Funding Rate Mechanics

On perpetual futures exchanges, funding is exchanged every 8 hours (or 1 hour on some venues):

**Standard Funding Rate (Binance-style):**

$$F = \text{Average Premium Index} + \text{clamp}(\text{Interest Rate} - \text{Premium Index}, -0.05\%, 0.05\%)$$

**Premium Index:**

$$P = \frac{\text{Impact Bid Price} + \text{Impact Ask Price}}{2} - \text{Spot Index Price}$$

### 4.2 Funding Rate Carry Strategy

```
DELTA-NEUTRAL FUNDING RATE CARRY:

IF Funding Rate > threshold (e.g., > 0.03% per 8h = ~41% APY):
    ACTION: Short Perp + Long Spot (delta-neutral)
    PROFIT: Collect positive funding from short position
    DURATION: Hold until funding rate normalizes
    
IF Funding Rate < -threshold (e.g., < -0.03% per 8h):
    ACTION: Long Perp + Short Spot (delta-neutral)
    PROFIT: Collect negative funding from long position
    DURATION: Hold until funding rate normalizes
    
EXIT: When |Funding Rate| < exit_threshold (e.g., 0.01%)
```

### 4.3 Funding Rate Statistics

| Exchange | Asset | Mean Funding (8h) | Std Dev | Median |
|---|---|---|---|---|
| Binance | BTC-PERP | +0.010% | 0.030% | +0.008% |
| Binance | ETH-PERP | +0.012% | 0.040% | +0.009% |
| Bybit | BTC-PERP | +0.011% | 0.035% | +0.008% |
| dYdX | BTC-PERP | +0.009% | 0.025% | +0.007% |

**Annualized Mean Carry (BTC, positive funding):**

$$0.010\% \times 3 \times 365 = 10.95\% \text{ APY}$$

### 4.4 Funding Rate Mean Reversion

Funding rates themselves mean-revert (they are essentially a cost that arbitrageurs keep in check):

**Half-life of Funding Rate:**
- BTC: ~2-5 days (funding spikes revert within a week)
- ETH: ~2-4 days
- Altcoins: ~1-3 days (faster reversion due to more volatile funding)

**Strategy Enhancement: Time Entry with Z-Score of Funding Rate**

$$z_{funding} = \frac{FR_t - \bar{FR}_{30d}}{\sigma_{FR,30d}}$$

- Enter when $z_{funding} > 2.0$ (funding unusually high → expect reversion, collect while high)
- Exit when $z_{funding} < 0.5$ (funding normalized)

### 4.5 Multi-Exchange Funding Arbitrage

Different exchanges have different funding rates for the same asset:

```
IF FR_Binance > FR_Bybit + threshold:
    Long perp on Bybit (pay lower funding or receive if negative)
    Short perp on Binance (receive higher funding)
    Net delta: approximately zero (if same asset)
    Profit: FR_Binance - FR_Bybit per funding period
    
    Risk: 
    - Position sizing mismatch
    - One exchange may liquidate before the other
    - Basis risk between exchanges
    - Capital inefficiency (margin required on both)
```

---

## 5. ส่วนต่างอัตรา Staking และ Lending

### 5.1 Staking Yield Carry

Different PoS networks offer different staking yields. The carry comes from:
1. Holding the higher-yielding staked asset
2. Hedging the price exposure with a futures short

**Staking Carry Formula:**

$$\text{Staking Carry} = r_{staking} - r_{hedge\_cost} - r_{opportunity}$$

Where:
- $r_{staking}$ = network staking reward rate (e.g., 5% for ETH)
- $r_{hedge\_cost}$ = cost of hedging (e.g., futures basis = -8% annualized)
- $r_{opportunity}$ = risk-free rate or alternative yield

**Example (ETH Staking Carry):**
- ETH staking yield: 4.0%
- ETH quarterly futures basis: 3.0% (positive, meaning futures at premium)
- Net carry (hedged staking): 4.0% + 3.0% = 7.0% (both staking yield AND basis collected)

Wait — more carefully:
- Long ETH spot (staking at 4.0%)
- Short ETH futures at 3.0% premium
- Total yield = staking_yield + basis_yield = 4.0% + 3.0% = 7.0%
- This is delta-neutral (spot long offset by futures short)

### 5.2 Lending Rate Differential

**DeFi Lending Carry:**

| Protocol (Lend) | Protocol (Borrow) | Asset | Net Carry | Risk |
|---|---|---|---|---|
| Protocol A (8% APY) | Protocol B (4% APY) | USDC | 4% | Smart contract, depegging |
| Protocol A (12% APY) | Protocol B (6% APY) | ETH | 6% | Smart contract, liquidation |
| Anchor (was 20%) | Aave (3%) | UST/USDC | 17% | Collapse risk (demonstrated) |

**Lessons from UST/Anchor Collapse:**
- Unsustainable high yields are a warning sign
- Protocol risk is the primary risk for DeFi carry
- Diversification across protocols is essential
- "If you can't identify the source of yield, you are the yield"

### 5.3 Liquid Staking Arbitrage

When liquid staking tokens (stETH, rETH) trade at a discount/premium to their underlying:

$$\text{Discount Carry} = \frac{ETH - stETH}{stETH} + r_{staking}$$

If stETH trades at 0.99 ETH (1% discount) and staking yield is 4%:
- Buy stETH at 0.99
- Expected value at redemption: 1.00 + staking rewards
- Annualized bonus from discount capture: depends on redemption timeline

---

## 6. ความเสี่ยง: การคลาย Carry Trade (Carry Trade Unwind)

### 6.1 The Carry Trade Unwind Phenomenon

The most dangerous risk for carry traders is the **sudden unwind** — when carry positions are liquidated simultaneously, causing the high-yield asset to crash against the funding currency.

**Characteristics of Carry Unwinds:**
- Sudden and violent (can happen in hours)
- Self-reinforcing (stops trigger more selling)
- Correlated across all carry pairs (systemic)
- Typically coincide with risk-off events (VIX spike, equity crash)

### 6.2 Historical Carry Trade Crashes

| Event | Date | Impact | Carry Loss |
|---|---|---|---|
| GFC | 2008 | AUD/JPY fell 40% in 3 months | -35% |
| JPY Carry Unwind | Aug 2007 | Rapid JPY appreciation | -10% in days |
| Flash Crash (GBP) | Oct 2016 | GBP/JPY dropped 6% in minutes | -6% in minutes |
| COVID Crash | Mar 2020 | EM currencies crushed | -15-25% |
| JPY Intervention | Oct 2022 | BOJ intervention spike | -5% in hours |
| Crypto Crash (May 2021) | May 2021 | Funding rates went deeply negative | Basis traders caught |

### 6.3 Carry Unwind Indicators

| Indicator | Signal | Source |
|---|---|---|
| VIX > 25 | Rising risk aversion | CBOE |
| JPY appreciation > 2% in a day | Carry unwind in progress | FX markets |
| Credit spreads widening | Risk-off environment | Bond markets |
| Emerging market outflows | Capital flight | Flow data |
| Crypto funding rates sharply negative | Crypto carry unwinding | Exchange data |
| Correlation spike | All carry pairs moving together | Correlation matrix |
| Speculative positioning extreme | Too many carry traders | COT report |

### 6.4 Carry Drawdown Model

The maximum drawdown of a carry trade can be modeled as:

$$DD_{max} = -\frac{R_{carry}}{SR_{carry}^2} \times z_\alpha$$

Where:
- $R_{carry}$ = annual carry return
- $SR_{carry}$ = Sharpe ratio of carry strategy
- $z_\alpha$ = quantile of the loss distribution

For a carry strategy with SR = 0.5, annual carry = 5%, at 99th percentile:

$$DD_{max} \approx -\frac{0.05}{0.25} \times 2.33 = -47\%$$

This illustrates the "picking up pennies in front of a steamroller" nature of carry.

### 6.5 Carry Trade Flash Crash Risk

The distribution of carry trade returns exhibits:

$$\text{Skewness} < 0 \quad (\text{large left tail})$$
$$\text{Kurtosis} > 3 \quad (\text{fat tails})$$

$$P(\text{Loss} > 3\sigma) \gg P_{\text{Normal}}(\text{Loss} > 3\sigma)$$

The probability of extreme losses is significantly higher than a normal distribution would predict.

### 6.6 Hedging Carry Trade Risk

| Hedge | Cost | Effectiveness |
|---|---|---|
| Out-of-money puts on carry pair | 1-3% per annum | High (direct hedge) |
| Long VIX calls | 2-5% per annum | Medium (correlation-based) |
| Long JPY calls | 0.5-2% per annum | High (for JPY-funded carry) |
| Momentum overlay | Variable | Medium (exits before full crash) |
| Dynamic hedging (delta-hedge tail) | 0.5-1% per annum | Medium-High |
| Diversification across uncorrelated carry | No direct cost | Medium (reduces concentration) |
| Position sizing reduction at high VIX | Opportunity cost | High |

---

## 7. Sharpe Ratio ของกลยุทธ์ Carry

### 7.1 Theoretical Sharpe Ratio

$$SR_{carry} = \frac{E[R_{carry}] + E[R_{spot}]}{\sigma_{carry}}$$

Under UIP violation (carry works), $E[R_{spot}] \approx 0$ or slightly positive for carry currencies:

$$SR_{carry} \approx \frac{r_{high} - r_{low}}{\sigma_{FX}}$$

### 7.2 Historical Sharpe Ratios

| Strategy | Period | Sharpe Ratio | Notes |
|---|---|---|---|
| G10 FX Carry | 1990-2023 | 0.4-0.6 | Unlevered |
| EM FX Carry | 2003-2023 | 0.5-0.7 | Higher return, higher vol |
| Crypto Funding Rate Carry | 2020-2025 | 1.0-2.5 | Much higher carry, lower duration risk |
| Crypto Basis Trade | 2020-2025 | 1.5-3.0 | Near-arbitrage when basis is large |
| DeFi Lending Carry | 2021-2025 | 0.5-1.5 | Protocol risk dominates |

### 7.3 Improving Carry Sharpe Ratio

| Enhancement | Expected Improvement | Trade-off |
|---|---|---|
| Volatility-target scaling | +0.2-0.4 SR | Reduces position during high-vol (misses some carry) |
| Momentum filter | +0.1-0.3 SR | Exits carry in downtrends (misses some carry) |
| Diversification (10+ pairs) | +0.2-0.5 SR | Capital spread thin, more complexity |
| Dynamic weighting (by rate level) | +0.1-0.2 SR | More turnover |
| Hedging tail risk (puts) | +0.1-0.3 SR (risk-adjusted) | Costs 1-3% per annum |
| Regime conditioning (risk-on only) | +0.3-0.5 SR | Fewer days in market |

### 7.4 Risk-Adjusted Carry Metric (Burnside, 2012)

$$\text{Risk-Adjusted Carry} = \frac{r_i - r_j}{\sigma_{i/j}}$$

This normalizes carry by the volatility of the exchange rate, giving a "carry Sharpe" per pair.

**Pair Selection Rule:** Select pairs with highest risk-adjusted carry:

$$\text{Pair Score} = \frac{|r_{high} - r_{low}|}{\text{Realized Vol}_{pair}} \times \text{Trend Filter}$$

---

## 8. ตรรกะหลัก — การเข้า/ออกสถานะ (Core Logic — Entry/Exit)

### 8.1 Forex Carry Trade Entry

```
Algorithm: Forex Carry Trade Entry

PRE-TRADE CHECKS:
    1. Identify high-yield and low-yield currencies (from central bank rates)
    2. Calculate carry per pair: carry_annual = rate_high - rate_low
    3. Calculate risk-adjusted carry: RAC = carry_annual / vol_pair
    4. Check risk regime:
       - VIX < 20 (or below 75th percentile)
       - No imminent central bank meetings for either currency
       - Carry pair not at multi-year extreme
    5. Check trend alignment (optional but recommended):
       - High-yield currency in uptrend vs low-yield (or at least not in downtrend)
       - EMA(50) > EMA(200) for the carry pair

ENTRY SIGNAL:
    IF RAC > min_RAC_threshold (e.g., > 0.3):
        AND risk_regime = "FAVORABLE"
        AND (trend_filter = "BULLISH" OR trend_filter = "NEUTRAL"):
        
        ENTER LONG on high-yield pair (e.g., Long AUD/JPY)
        
        Position Size = (Account * risk_pct) / (stop_distance_pips * pip_value)
        Stop Loss = Entry - k * ATR(14) * pip_value
        OR Stop Loss = below recent swing low

EXIT SIGNAL:
    1. Stop loss hit
    2. Carry disappears: rate differential < min_carry (e.g., < 1.5%)
    3. Risk regime deteriorates: VIX > 30 or sharp JPY appreciation
    4. Trend turns bearish: EMA(50) crosses below EMA(200)
    5. Central bank policy change signals rate cut in high-yield currency
    6. Time-based review: Reassess monthly
```

### 8.2 Crypto Funding Rate Carry Entry

```
Algorithm: Crypto Funding Rate Carry

MONITORING (continuous):
    FOR each perpetual futures market:
        FR = current_funding_rate  # Per 8h payment
        FR_ann = FR * 3 * 365     # Annualized
        FR_z = (FR - mean_FR_30d) / std_FR_30d  # Z-score
        cost = 2 * taker_fee + slippage_estimate
        
ENTRY CONDITIONS (POSITIVE CARRY):
    IF FR_ann > min_yield (e.g., > 20% annualized)
    AND FR_z > entry_z (e.g., > 1.5)
    AND days_since_last_entry > cooldown
    AND portfolio_capacity_available:
        
        ACTION: 
            1. Buy spot (or long on margin if needed)
            2. Short equivalent perp (same quantity)
            3. Net delta = 0 (delta-neutral)
        
        POSITION SIZE:
            notional = Account * allocation_pct / n_active_positions
            # Ensure adequate margin for perp short
            margin_required = notional / leverage
            total_capital_required = notional + margin_required + buffer
        
ENTRY CONDITIONS (NEGATIVE CARRY):
    IF FR_ann < -min_yield (e.g., < -20% annualized)
    AND FR_z < -entry_z:
        
        ACTION:
            1. Short spot (borrow and sell) OR exit existing spot
            2. Long equivalent perp
            3. Net delta = 0
            
EXIT CONDITIONS:
    IF |FR_ann| < exit_yield (e.g., < 5% annualized):
        CLOSE both legs (carry no longer sufficient)
        
    IF FR_z returns to zero (mean reversion):
        CLOSE (captured the extreme funding)
        
    IF basis between spot and perp widens > max_basis:
        CLOSE (execution risk)
        
    IF max_holding_period exceeded:
        REASSESS (monthly)
        
    IF margin_ratio < safety_threshold:
        REDUCE position size to increase margin ratio
```

### 8.3 Carry + Momentum Filter

The most effective enhancement to carry trading is adding a momentum/trend filter:

```
CARRY + MOMENTUM COMBINED:

    carry_signal = rate_high - rate_low  (positive carry direction)
    momentum_signal = sign(SMA(50) - SMA(200))  (trend direction)
    
    IF carry_signal > 0 AND momentum_signal > 0:
        ENTER with full size (carry + trend aligned)
        
    IF carry_signal > 0 AND momentum_signal == 0:
        ENTER with half size (carry without trend confirmation)
        
    IF carry_signal > 0 AND momentum_signal < 0:
        NO ENTRY (trend opposes carry — high crash risk)
        
    IF already in position AND momentum_signal turns negative:
        EXIT (trend reversing — potential unwind beginning)
```

---

## 9. ข้อมูลจำเพาะทางเทคนิค (Technical Specifications)

### 9.1 System Configuration

```yaml
carry_trade_config:
  # Forex Carry
  forex:
    pairs:
      - {long: AUD, short: JPY, min_carry: 2.0}
      - {long: NZD, short: JPY, min_carry: 2.0}
      - {long: MXN, short: JPY, min_carry: 5.0}
      - {long: AUD, short: CHF, min_carry: 1.5}
      - {long: NZD, short: CHF, min_carry: 1.5}
      
    entry_conditions:
      min_risk_adjusted_carry: 0.30
      vix_max: 22
      trend_filter: true  # EMA(50) > EMA(200)
      
    exit_conditions:
      carry_min: 1.0%   # Exit if carry drops below this
      vix_exit: 30       # Exit if VIX exceeds
      trend_exit: true   # Exit if EMA(50) < EMA(200)
      stop_loss_atr: 3.0 # ATR multiplier for stop
      
    rebalance_frequency: monthly
    max_pairs: 4
    risk_per_pair: 2.0%
    max_portfolio_carry_risk: 8.0%
    
  # Crypto Carry
  crypto:
    funding_rate:
      assets: [BTC, ETH, SOL, AVAX]
      venues: [Binance, Bybit, OKX]
      min_funding_rate_ann: 15%
      entry_z_score: 1.5
      exit_z_score: 0.5
      exit_funding_rate_ann: 5%
      max_holding_days: 30
      
    basis_trade:
      assets: [BTC, ETH]
      min_basis_ann: 10%
      max_expiry_days: 90
      min_expiry_days: 7
      rollover_threshold: 7  # Roll to next expiry when < 7 days
      
    position_sizing:
      max_per_position: 15%
      max_total_carry: 50%
      leverage_max: 3x
      margin_safety_buffer: 2.0  # 2x minimum margin
```

### 9.2 Data Requirements

```yaml
data_requirements:
  forex:
    - Central bank interest rates (daily update)
    - Forward points / swap rates (real-time from broker)
    - OHLCV price data (H4 and D1)
    - VIX index (real-time)
    - COT report (weekly)
    - Economic calendar (scheduled events)
    
  crypto:
    - Perpetual funding rates (real-time, every 8h)
    - Futures prices and basis (real-time)
    - Spot prices (real-time)
    - Lending rates per protocol (hourly)
    - Staking yields (daily)
    - On-chain metrics (TVL, borrow utilization)
    - Exchange open interest (for crowding detection)
```

---

## 10. แบบจำลองทางคณิตศาสตร์ (Mathematical Models)

### 10.1 Carry Trade Expected Return

$$E[R_{carry}] = (r_H - r_L) - E[\Delta s] + \text{Risk Premium}$$

If UIP fails (empirically established):

$$E[\Delta s] \neq r_H - r_L$$

Typically $E[\Delta s] < r_H - r_L$, meaning the high-yield currency does NOT depreciate enough to eliminate the carry.

**Empirical Forward Premium Regression (Fama, 1984):**

$$\Delta s_{t+1} = \alpha + \beta(f_t - s_t) + \epsilon_t$$

Where $f_t - s_t$ is the forward discount. Fama (1984) found $\hat{\beta} < 1$ (often negative), confirming carry profitability.

### 10.2 Carry Trade Sharpe Decomposition

$$SR_{carry} = \frac{\mu_{carry}}{\sigma_{carry}} = \frac{r_H - r_L - E[\Delta s]}{\sigma_s}$$

For leverage $L$:

$$SR_{leveraged} = SR_{carry} \quad (\text{Sharpe is leverage-invariant})$$

$$E[R_{leveraged}] = L \times E[R_{carry}]$$
$$\sigma_{leveraged} = L \times \sigma_{carry}$$

### 10.3 Funding Rate Carry Return Model

For a delta-neutral funding rate position:

$$R_{funding} = \sum_{t=1}^{N} FR_t \times Q \times P_t - \text{Costs}$$

Where $N$ is the number of funding periods and $FR_t$ is the funding rate at period $t$.

**Expected return per day (3 funding periods):**

$$E[R_{daily}] = 3 \times E[FR] \times Q \times P - 2 \times \text{spread cost} \times Q \times P / T_{hold}$$

The entry/exit spread cost is amortized over the holding period.

### 10.4 Break-Even Holding Period

The minimum holding period for the carry to exceed entry/exit costs:

$$T_{breakeven} = \frac{2 \times C_{entry+exit}}{FR_{per\_period} \times Q \times P}$$

Where $C_{entry+exit}$ includes spread and slippage costs for opening and closing both legs.

**Example:**
- Entry cost (both legs): 0.10% of notional
- Funding rate: 0.03% per 8h
- Break-even: 0.10% / 0.03% = 3.33 periods = ~1 day

### 10.5 Kelly Criterion for Carry

$$f^* = \frac{E[R_{carry}]}{\sigma^2_{carry}} = \frac{\mu}{\sigma^2}$$

For a carry strategy with $\mu = 5\%$ annualized and $\sigma = 10\%$:

$$f^* = \frac{0.05}{0.01} = 5$$

This suggests up to 5x leverage is optimal (Kelly is aggressive; use half-Kelly = 2.5x).

### 10.6 Conditional Value at Risk

$$CVaR_\alpha = -\frac{1}{\alpha}\int_0^{\alpha} VaR_u \, du$$

For carry trades with negative skewness, CVaR is significantly worse than VaR:

$$\frac{CVaR_{1\%}}{VaR_{1\%}} \approx 1.5 - 2.5 \quad (\text{for carry strategies})$$

Compared to $\approx 1.3$ for normally distributed returns.

---

## 11. พารามิเตอร์ความเสี่ยง (Risk Parameters)

### 11.1 Position Sizing

**Forex Carry:**

$$\text{Position Size} = \frac{\text{Account} \times \text{Risk\%}}{ATR(14) \times k \times \text{Pip Value}}$$

| Risk Level | Risk per Pair | Max Leverage | Max Pairs |
|---|---|---|---|
| Conservative | 1.0% | 3x | 3 |
| Moderate | 1.5% | 5x | 4 |
| Aggressive | 2.5% | 10x | 5 |

**Crypto Carry:**

$$\text{Notional per Position} = \text{Account} \times \text{Allocation\%}$$

Ensure margin ratio stays above 3x maintenance margin.

### 11.2 Stop Loss Framework

| Strategy | Stop Type | Level |
|---|---|---|
| Forex Carry | ATR-based | Entry - 3 * ATR(14) |
| Forex Carry | Swing-based | Below previous major swing low |
| Forex Carry | Carry annihilation | When annualized carry < min_threshold |
| Crypto Funding | Funding reversal | When funding turns consistently negative |
| Crypto Funding | Margin-based | When margin ratio < 2x maintenance |
| Crypto Basis | Basis inversion | When basis turns negative |
| Crypto Basis | Expiry risk | Close before expiry if basis narrows to < cost |

### 11.3 Portfolio-Level Carry Risk

```yaml
portfolio_risk_limits:
  max_gross_carry_exposure: 300%  # Of equity (with leverage)
  max_net_directional: 50%        # Net long/short exposure
  max_single_pair_exposure: 25%   # Any single pair
  max_correlated_exposure: 50%    # Correlated pairs combined
  
  drawdown_response:
    dd_5pct: reduce_size_25%
    dd_10pct: reduce_size_50%
    dd_15pct: close_all_carry
    dd_20pct: halt_strategy_review
    
  regime_filters:
    max_vix: 25             # For forex carry
    max_crypto_vol_90d: 100%  # For crypto carry
    min_funding_rate_stability: 0.6  # Autocorrelation of funding
```

### 11.4 Carry Trade Risk Metrics Dashboard

| Metric | Calculation | Alert Level |
|---|---|---|
| Portfolio Carry Yield | Weighted avg carry across positions | < 3% (too low) |
| Risk-Adjusted Carry | Carry / Vol per position | < 0.2 (insufficient) |
| VIX Level | Real-time VIX | > 25 (elevated) |
| Funding Rate Regime | Rolling 7-day avg funding | Switches sign |
| JPY Momentum (for FX) | 20-day JPY return | > +2% (unwind signal) |
| Margin Utilization | Used margin / Available | > 60% (reduce) |
| Position Correlation | Max pairwise correlation | > 0.80 (too concentrated) |
| Days in Position | Current holding period | > max_holding_days |

---

## 12. ขั้นตอนการดำเนินการ (Execution Flow)

### 12.1 Complete Carry Trade System — Pseudocode

```python
class CarryTradeSystem:
    """
    Complete Carry Trade System
    Supports: Forex swap carry, Crypto funding rate, Basis trade
    """
    
    def __init__(self, config):
        self.config = config
        self.positions = {}
        self.risk_monitor = RiskMonitor(config['risk'])
        
    def scan_opportunities(self, market_data):
        """Step 1: Scan for carry trade opportunities."""
        opportunities = []
        
        # Forex carry opportunities
        for pair_config in self.config['forex']['pairs']:
            rate_long = market_data.get_rate(pair_config['long'])
            rate_short = market_data.get_rate(pair_config['short'])
            carry = rate_long - rate_short
            
            if carry > pair_config['min_carry']:
                pair_name = f"{pair_config['long']}/{pair_config['short']}"
                vol = market_data.get_volatility(pair_name, period=30)
                rac = carry / (vol * 100) if vol > 0 else 0
                
                opportunities.append({
                    'type': 'forex_carry',
                    'pair': pair_name,
                    'carry_annual': carry,
                    'volatility': vol,
                    'risk_adjusted_carry': rac,
                    'trend': self.check_trend(pair_name, market_data)
                })
        
        # Crypto funding rate opportunities
        for asset in self.config['crypto']['funding_rate']['assets']:
            for venue in self.config['crypto']['funding_rate']['venues']:
                fr = market_data.get_funding_rate(asset, venue)
                fr_ann = fr * 3 * 365
                fr_history = market_data.get_funding_history(asset, venue, days=30)
                fr_z = (fr - np.mean(fr_history)) / np.std(fr_history)
                
                if abs(fr_ann) > self.config['crypto']['funding_rate']['min_funding_rate_ann']:
                    opportunities.append({
                        'type': 'funding_carry',
                        'asset': asset,
                        'venue': venue,
                        'funding_rate': fr,
                        'funding_ann': fr_ann,
                        'z_score': fr_z,
                        'direction': 'SHORT_PERP' if fr > 0 else 'LONG_PERP'
                    })
        
        # Crypto basis opportunities
        for asset in self.config['crypto']['basis_trade']['assets']:
            spot = market_data.get_spot_price(asset)
            futures = market_data.get_futures_prices(asset)
            
            for expiry, fut_price in futures.items():
                days_to_expiry = (expiry - datetime.now()).days
                if days_to_expiry < self.config['crypto']['basis_trade']['min_expiry_days']:
                    continue
                    
                basis = (fut_price - spot) / spot
                basis_ann = basis * 365 / days_to_expiry
                
                if basis_ann > self.config['crypto']['basis_trade']['min_basis_ann']:
                    opportunities.append({
                        'type': 'basis_carry',
                        'asset': asset,
                        'spot_price': spot,
                        'futures_price': fut_price,
                        'expiry': expiry,
                        'days_to_expiry': days_to_expiry,
                        'basis': basis,
                        'basis_ann': basis_ann
                    })
        
        return sorted(opportunities, key=lambda o: o.get('risk_adjusted_carry', o.get('basis_ann', o.get('funding_ann', 0))), reverse=True)
    
    def evaluate_entry(self, opportunity, market_data):
        """Step 2: Evaluate whether to enter the carry trade."""
        # Check regime
        if opportunity['type'] == 'forex_carry':
            vix = market_data.get_vix()
            if vix > self.config['forex']['entry_conditions']['vix_max']:
                return False, "VIX too high"
            if opportunity['risk_adjusted_carry'] < self.config['forex']['entry_conditions']['min_risk_adjusted_carry']:
                return False, "Risk-adjusted carry too low"
            if self.config['forex']['entry_conditions']['trend_filter']:
                if opportunity['trend'] == 'BEARISH':
                    return False, "Trend opposes carry"
        
        elif opportunity['type'] == 'funding_carry':
            z = opportunity['z_score']
            min_z = self.config['crypto']['funding_rate']['entry_z_score']
            if abs(z) < min_z:
                return False, "Funding rate z-score below threshold"
        
        elif opportunity['type'] == 'basis_carry':
            # Basis trade is nearly always acceptable if basis > min threshold
            pass
        
        # Check portfolio capacity
        if len(self.positions) >= self.config.get('max_positions', 10):
            return False, "Maximum positions reached"
        
        # Check portfolio risk
        if not self.risk_monitor.can_add_position(opportunity):
            return False, "Portfolio risk limit reached"
        
        return True, "Entry approved"
    
    def execute_entry(self, opportunity):
        """Step 3: Execute carry trade entry."""
        if opportunity['type'] == 'forex_carry':
            # Buy the high-yield pair
            size = self.calculate_forex_size(opportunity)
            order = self.broker.buy(opportunity['pair'], size)
            
            self.positions[opportunity['pair']] = {
                'type': 'forex_carry',
                'entry_price': order['fill_price'],
                'size': size,
                'carry_annual': opportunity['carry_annual'],
                'entry_date': datetime.now(),
                'stop_loss': order['fill_price'] - 3 * self.get_atr(opportunity['pair']),
                'accumulated_swap': 0.0
            }
            
        elif opportunity['type'] == 'funding_carry':
            notional = self.calculate_crypto_size(opportunity)
            
            if opportunity['direction'] == 'SHORT_PERP':
                # Long spot + Short perp
                self.exchange.buy_spot(opportunity['asset'], notional)
                self.exchange.sell_perp(opportunity['asset'], notional)
            else:
                # Short spot + Long perp
                self.exchange.sell_spot(opportunity['asset'], notional)
                self.exchange.buy_perp(opportunity['asset'], notional)
            
            self.positions[f"{opportunity['asset']}_{opportunity['venue']}_funding"] = {
                'type': 'funding_carry',
                'asset': opportunity['asset'],
                'venue': opportunity['venue'],
                'notional': notional,
                'entry_funding_rate': opportunity['funding_rate'],
                'direction': opportunity['direction'],
                'entry_date': datetime.now(),
                'accumulated_funding': 0.0
            }
            
        elif opportunity['type'] == 'basis_carry':
            notional = self.calculate_crypto_size(opportunity)
            
            # Long spot + Short futures
            self.exchange.buy_spot(opportunity['asset'], notional)
            self.exchange.sell_futures(opportunity['asset'], opportunity['expiry'], notional)
            
            self.positions[f"{opportunity['asset']}_basis_{opportunity['expiry']}"] = {
                'type': 'basis_carry',
                'asset': opportunity['asset'],
                'notional': notional,
                'entry_basis': opportunity['basis'],
                'expiry': opportunity['expiry'],
                'entry_date': datetime.now()
            }
    
    def monitor_positions(self, market_data):
        """Step 4: Monitor and manage open carry positions."""
        for pos_id, pos in list(self.positions.items()):
            should_exit = False
            reason = ""
            
            if pos['type'] == 'forex_carry':
                # Check carry still exists
                current_carry = self.get_current_carry(pos)
                if current_carry < self.config['forex']['exit_conditions']['carry_min']:
                    should_exit = True
                    reason = "Carry fell below minimum"
                
                # Check VIX
                vix = market_data.get_vix()
                if vix > self.config['forex']['exit_conditions']['vix_exit']:
                    should_exit = True
                    reason = f"VIX exceeded threshold ({vix})"
                
                # Check trend
                if self.config['forex']['exit_conditions']['trend_exit']:
                    trend = self.check_trend(pos_id, market_data)
                    if trend == 'BEARISH':
                        should_exit = True
                        reason = "Trend turned bearish"
                
                # Check stop loss
                current_price = market_data.get_price(pos_id)
                if current_price < pos['stop_loss']:
                    should_exit = True
                    reason = "Stop loss hit"
                    
            elif pos['type'] == 'funding_carry':
                # Check funding rate
                fr = market_data.get_funding_rate(pos['asset'], pos['venue'])
                fr_ann = fr * 3 * 365
                
                if pos['direction'] == 'SHORT_PERP' and fr_ann < self.config['crypto']['funding_rate']['exit_funding_rate_ann']:
                    should_exit = True
                    reason = "Funding rate too low"
                elif pos['direction'] == 'LONG_PERP' and fr_ann > -self.config['crypto']['funding_rate']['exit_funding_rate_ann']:
                    should_exit = True
                    reason = "Negative funding rate normalized"
                
                # Check margin
                margin_ratio = self.exchange.get_margin_ratio(pos['asset'])
                if margin_ratio < self.config['crypto']['position_sizing']['margin_safety_buffer']:
                    should_exit = True
                    reason = "Margin ratio too low"
                
                # Accumulate funding P&L
                pos['accumulated_funding'] += fr * pos['notional']
                
            elif pos['type'] == 'basis_carry':
                # Check expiry
                days_left = (pos['expiry'] - datetime.now()).days
                if days_left < self.config['crypto']['basis_trade']['rollover_threshold']:
                    should_exit = True
                    reason = "Approaching expiry — roll or close"
            
            # Max holding period
            holding_days = (datetime.now() - pos['entry_date']).days
            if holding_days > self.config.get('max_holding_days', 90):
                should_exit = True
                reason = "Maximum holding period reached"
            
            if should_exit:
                self.close_position(pos_id, reason)
    
    def run(self, data_feed):
        """Step 5: Main carry trade loop."""
        for timestamp in data_feed:
            market_data = data_feed.get_current_data()
            
            # Monitor existing positions
            self.monitor_positions(market_data)
            
            # Scan for new opportunities (less frequently)
            if self.should_scan(timestamp):
                opportunities = self.scan_opportunities(market_data)
                
                for opp in opportunities:
                    can_enter, reason = self.evaluate_entry(opp, market_data)
                    if can_enter:
                        self.execute_entry(opp)
                        break  # One entry per scan cycle
            
            # Log portfolio status
            self.log_status(market_data)
```

### 12.2 Execution Flow Diagram

```
┌───────────────────────────────────────────────┐
│          CARRY TRADE EXECUTION FLOW           │
├───────────────────────────────────────────────┤
│                                               │
│  1. OPPORTUNITY SCANNING (Daily/4H)           │
│     ├─ Fetch interest rates (forex)           │
│     ├─ Fetch funding rates (crypto)           │
│     ├─ Calculate basis (futures)              │
│     ├─ Compute risk-adjusted carry            │
│     └─ Rank opportunities                     │
│                                               │
│  2. ENTRY EVALUATION                          │
│     ├─ Check risk regime (VIX, vol)           │
│     ├─ Check trend alignment                  │
│     ├─ Verify carry meets minimum             │
│     ├─ Check portfolio capacity               │
│     └─ Approve or reject entry                │
│                                               │
│  3. EXECUTION                                 │
│     ├─ Forex: Buy high-yield pair             │
│     ├─ Funding: Long spot + Short perp        │
│     │   (or Short spot + Long perp)           │
│     ├─ Basis: Long spot + Short futures       │
│     ├─ Set stop loss                          │
│     └─ Record position details                │
│                                               │
│  4. POSITION MONITORING (Continuous)          │
│     ├─ Track carry accumulation               │
│     ├─ Monitor carry level (still viable?)    │
│     ├─ Check risk regime (VIX, volatility)    │
│     ├─ Check trend (reversal?)                │
│     ├─ Check margin (crypto)                  │
│     ├─ Check expiry (basis trades)            │
│     └─ Stop loss monitoring                   │
│                                               │
│  5. EXIT MANAGEMENT                           │
│     ├─ Close when carry disappears            │
│     ├─ Close on risk regime deterioration     │
│     ├─ Close on trend reversal                │
│     ├─ Close on stop loss hit                 │
│     ├─ Roll basis trades before expiry        │
│     └─ Record final P&L                       │
│                                               │
│  6. REPORTING                                 │
│     ├─ Daily carry P&L attribution            │
│     ├─ Carry vs spot P&L decomposition        │
│     ├─ Risk metric dashboard                  │
│     └─ Opportunity pipeline status            │
│                                               │
└───────────────────────────────────────────────┘
```

---

## 13. เอกสารอ้างอิง (References)

### Academic Papers

1. **Fama, E.F.** (1984). "Forward and Spot Exchange Rates." *Journal of Monetary Economics*, 14, 319-338.
2. **Lustig, H., & Verdelhan, A.** (2007). "The Cross Section of Foreign Currency Risk Premia and Consumption Growth Risk." *American Economic Review*, 97(1), 89-117.
3. **Burnside, C., Eichenbaum, M., Kleshchelski, I., & Rebelo, S.** (2011). "Do Peso Problems Explain the Returns to the Carry Trade?" *Review of Financial Studies*, 24(3), 853-891.
4. **Brunnermeier, M.K., Nagel, S., & Pedersen, L.H.** (2008). "Carry Trades and Currency Crashes." *NBER Macroeconomics Annual*, 23, 313-347.
5. **Menkhoff, L., Sarno, L., Schmeling, M., & Schrimpf, A.** (2012). "Carry Trades and Global Foreign Exchange Volatility." *Journal of Finance*, 67(2), 681-718.
6. **Koijen, R.S.J., Moskowitz, T.J., Pedersen, L.H., & Vrugt, E.B.** (2018). "Carry." *Journal of Financial Economics*, 127(2), 197-225.
7. **Jurek, J.W.** (2014). "Crash-Neutral Currency Carry Trades." *Journal of Financial Economics*, 113(3), 325-347.
8. **Daniel, K., Hodrick, R.J., & Lu, Z.** (2017). "The Carry Trade: Risks and Drawdowns." *Critical Finance Review*, 6, 211-262.

### Practitioner Resources

9. **Ilmanen, A.** (2011). *Expected Returns*. Wiley. (Chapter on carry strategies.)
10. **Narang, R.** (2013). *Inside the Black Box*. Wiley. (Systematic carry implementation.)
11. **AQR Capital Management.** Various research papers on carry as a factor.

### Crypto-Specific

12. **Alexander, C., & Heck, D.** (2020). "Price Discovery in Bitcoin: The Impact of Unregulated Markets." *Journal of Financial Stability*, 50, 100776.
13. **Bianchi, D.** (2020). "Cryptocurrencies as an Asset Class? An Empirical Assessment." *Journal of Alternative Investments*, 23(2), 162-179.

---

*เอกสารนี้เป็นส่วนหนึ่งของฐานความรู้ระบบเทรด AI แบบ Multi-Agent Carry Trade ให้กระแสรายได้สม่ำเสมอในสภาวะที่เอื้ออำนวย แต่ต้องการการบริหารความเสี่ยงอย่างมีวินัยเพื่อเอาตัวรอดจากการคลายสถานะที่หลีกเลี่ยงไม่ได้ การผสม Carry กับตัวกรองเทรนด์/โมเมนตัมช่วยปรับปรุงผลตอบแทนปรับความเสี่ยงอย่างมีนัยสำคัญ*
