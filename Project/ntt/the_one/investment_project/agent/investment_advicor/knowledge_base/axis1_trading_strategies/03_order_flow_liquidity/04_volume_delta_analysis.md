# Volume Delta & Cumulative Delta Analysis — CVD, Volume Profile, VWAP

> **Axis 1 — Trading Strategies | Module 03 — Order Flow & Liquidity**
> Document: 04_volume_delta_analysis.md
> Version: 2.0 | Last Updated: 2026-04-12
> Classification: Core Knowledge Base — Multi-Agent AI Trading System

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Volume Delta Calculation and Interpretation](#2-volume-delta-calculation-and-interpretation)
3. [Cumulative Volume Delta (CVD) Divergences](#3-cumulative-volume-delta-cvd-divergences)
4. [Point of Control (POC)](#4-point-of-control-poc)
5. [Value Area High/Low (VAH/VAL)](#5-value-area-highlow-vahval)
6. [Volume-Weighted Average Price (VWAP) and Bands](#6-volume-weighted-average-price-vwap-and-bands)
7. [Mathematical Formulas](#7-mathematical-formulas)
8. [Trading Signals from Volume Delta](#8-trading-signals-from-volume-delta)
9. [Integration with Price Action](#9-integration-with-price-action)
10. [Core Logic — Entry/Exit](#10-core-logic--entryexit)
11. [Technical Specifications](#11-technical-specifications)
12. [Risk Parameters](#12-risk-parameters)
13. [Execution Flow — Pseudocode](#13-execution-flow--pseudocode)
14. [References](#14-references)

---

## 1. Introduction

### 1.1 Volume Delta as the Core Order Flow Metric

Volume Delta is the most fundamental measurement of **aggression** in the market. While price shows us WHERE the market is, delta tells us WHO is more aggressive — buyers or sellers — and by how much.

$$\Delta = V_{buy} - V_{sell}$$

Where:
- $V_{buy}$ = Volume of trades initiated by buyers (trades that hit the ask)
- $V_{sell}$ = Volume of trades initiated by sellers (trades that hit the bid)

### 1.2 Why Delta Matters More Than Raw Volume

| Metric | What It Shows | Limitation |
|--------|-------------|-----------|
| **Raw Volume** | Total activity (interest) | Does not show direction |
| **Volume Delta** | Net directional aggression | Requires trade classification |
| **Cumulative Delta** | Persistent directional pressure over time | Can diverge from price |
| **Delta per Price** | Where aggression occurred | Requires tick data |

### 1.3 Data Requirements

| Data Type | Minimum for Delta | Ideal |
|-----------|-------------------|-------|
| **Tick Data** | Required for accurate delta | Every trade with aggressor flag |
| **Aggregated Bars** | Can estimate using BVC method | Less accurate |
| **Time & Sales** | Shows individual trades | With side classification |
| **Order Book** | Supplements delta analysis | Full DOM for context |

### 1.4 Trade Classification Methods

For accurate delta calculation, each trade must be classified as buyer- or seller-initiated:

| Method | Accuracy | Data Required | Use Case |
|--------|----------|---------------|----------|
| **Exchange-provided flag** | ~99% | Direct exchange feed | Crypto (Binance, etc.) |
| **Lee-Ready Algorithm** | ~85% | Quote + trade data | Equities, Forex |
| **Tick Rule** | ~75% | Price sequence only | Minimal data environments |
| **BVC (Bulk Volume Classification)** | ~70% | OHLCV bars only | No tick data available |

---

## 2. Volume Delta Calculation and Interpretation

### 2.1 Per-Bar Delta

For each time-based bar (candle), calculate:

$$\Delta_{bar} = \sum_{i \in \text{bar}} V_i \cdot \text{sign}(i)$$

Where:
$$\text{sign}(i) = \begin{cases} +1 & \text{if trade } i \text{ hit the ask (buyer-initiated)} \\ -1 & \text{if trade } i \text{ hit the bid (seller-initiated)} \end{cases}$$

### 2.2 Delta Interpretation Table

```
┌────────────────────────────────────────────────────────────────────┐
│              DELTA + PRICE ACTION MATRIX                            │
├──────────────┬──────────────┬─────────────────────────────────────┤
│  Price       │  Delta       │  Interpretation                     │
├──────────────┼──────────────┼─────────────────────────────────────┤
│  UP (green)  │  POSITIVE    │  NORMAL: Buyers aggressive, price   │
│              │  (large)     │  follows. Healthy trend.            │
├──────────────┼──────────────┼─────────────────────────────────────┤
│  UP (green)  │  NEGATIVE    │  DISTRIBUTION: Price up but sellers │
│              │              │  are more aggressive. Smart money   │
│              │              │  selling into buying. WARNING.      │
├──────────────┼──────────────┼─────────────────────────────────────┤
│  DOWN (red)  │  NEGATIVE    │  NORMAL: Sellers aggressive, price  │
│              │  (large)     │  follows. Healthy downtrend.        │
├──────────────┼──────────────┼─────────────────────────────────────┤
│  DOWN (red)  │  POSITIVE    │  ACCUMULATION: Price down but       │
│              │              │  buyers are more aggressive. Smart  │
│              │              │  money buying the dip. BULLISH.     │
├──────────────┼──────────────┼─────────────────────────────────────┤
│  FLAT        │  POSITIVE    │  ABSORPTION: Buyers accumulating    │
│  (doji/small)│  (large)     │  without moving price. Bullish      │
│              │              │  pressure building.                  │
├──────────────┼──────────────┼─────────────────────────────────────┤
│  FLAT        │  NEGATIVE    │  ABSORPTION: Sellers distributing   │
│  (doji/small)│  (large)     │  without moving price. Bearish      │
│              │              │  pressure building.                  │
└──────────────┴──────────────┴─────────────────────────────────────┘
```

### 2.3 Delta Strength Classification

$$\text{Delta Strength} = \frac{|\Delta_{bar}|}{\text{Total Volume}_{bar}}$$

| Strength | Range | Meaning |
|----------|-------|---------|
| **Extreme** | > 0.7 | One side completely dominates (>85% vs <15%) |
| **Strong** | 0.5 - 0.7 | Clear directional intent |
| **Moderate** | 0.3 - 0.5 | Slight directional bias |
| **Weak** | 0.1 - 0.3 | Nearly balanced, little directional info |
| **Neutral** | < 0.1 | No directional edge |

### 2.4 Delta Rate of Change

The acceleration of delta provides additional signal:

$$\dot{\Delta}(t) = \Delta(t) - \Delta(t-1)$$

$$\ddot{\Delta}(t) = \dot{\Delta}(t) - \dot{\Delta}(t-1)$$

**Interpretation:**
- Positive $\dot{\Delta}$: Buying pressure increasing
- Negative $\dot{\Delta}$: Selling pressure increasing
- Positive $\ddot{\Delta}$: Buying momentum accelerating
- Negative $\ddot{\Delta}$: Selling momentum accelerating

### 2.5 Implementation

```python
class DeltaCalculator:
    """
    Calculates volume delta from raw trade data.
    """
    
    def __init__(self, config: dict):
        self.bar_timeframe_s = config.get('bar_timeframe_s', 3600)  # 1H default
        self.current_bar_delta = 0.0
        self.current_bar_buy_vol = 0.0
        self.current_bar_sell_vol = 0.0
        self.current_bar_start = None
        self.delta_history = []
        self.max_history = config.get('max_delta_history', 1000)
    
    def on_trade(self, price: float, volume: float, side: str, timestamp: float):
        """
        Process a single trade and update delta.
        
        Args:
            price: Trade price
            volume: Trade volume
            side: 'BUY' (hit ask) or 'SELL' (hit bid)
            timestamp: Unix timestamp
        """
        # Check if new bar
        if self.current_bar_start is None:
            self.current_bar_start = timestamp
        
        if timestamp - self.current_bar_start >= self.bar_timeframe_s:
            # Close current bar
            self._close_bar()
            self.current_bar_start = timestamp
        
        # Update current bar
        if side == 'BUY':
            self.current_bar_buy_vol += volume
            self.current_bar_delta += volume
        elif side == 'SELL':
            self.current_bar_sell_vol += volume
            self.current_bar_delta -= volume
    
    def _close_bar(self):
        """Close the current bar and add to history."""
        total_vol = self.current_bar_buy_vol + self.current_bar_sell_vol
        
        bar_data = {
            'delta': self.current_bar_delta,
            'buy_volume': self.current_bar_buy_vol,
            'sell_volume': self.current_bar_sell_vol,
            'total_volume': total_vol,
            'delta_strength': abs(self.current_bar_delta) / total_vol if total_vol > 0 else 0,
            'timestamp': self.current_bar_start
        }
        
        self.delta_history.append(bar_data)
        if len(self.delta_history) > self.max_history:
            self.delta_history.pop(0)
        
        # Reset
        self.current_bar_delta = 0.0
        self.current_bar_buy_vol = 0.0
        self.current_bar_sell_vol = 0.0
    
    def get_cumulative_delta(self, lookback: int = None) -> float:
        """Get cumulative delta over lookback bars."""
        if not self.delta_history:
            return 0.0
        
        if lookback is None:
            return sum(bar['delta'] for bar in self.delta_history)
        
        recent = self.delta_history[-lookback:]
        return sum(bar['delta'] for bar in recent)
    
    def get_delta_divergence(self, prices: List[float], lookback: int = 20) -> Optional[str]:
        """
        Detect divergence between price and cumulative delta.
        
        Returns: 'BULLISH_DIV', 'BEARISH_DIV', or None
        """
        if len(self.delta_history) < lookback or len(prices) < lookback:
            return None
        
        recent_deltas = [bar['delta'] for bar in self.delta_history[-lookback:]]
        recent_prices = prices[-lookback:]
        
        # Calculate slopes
        x = np.arange(lookback)
        price_slope = np.polyfit(x, recent_prices, 1)[0]
        cvd = np.cumsum(recent_deltas)
        cvd_slope = np.polyfit(x, cvd, 1)[0]
        
        # Divergence detection
        if price_slope > 0 and cvd_slope < 0:
            return 'BEARISH_DIV'  # Price up, CVD down
        elif price_slope < 0 and cvd_slope > 0:
            return 'BULLISH_DIV'  # Price down, CVD up
        
        return None
```

---

## 3. Cumulative Volume Delta (CVD) Divergences

### 3.1 CVD Definition

$$\text{CVD}(T) = \sum_{t=1}^{T} \Delta_t = \sum_{t=1}^{T} (V_t^{buy} - V_t^{sell})$$

CVD is a running total of delta over time. It shows the persistent net aggression of buyers vs. sellers.

### 3.2 CVD Trend Analysis

```
CVD UPTREND (Healthy bullish):
─────────────────────────────
Price:  ╱╲  ╱╲  ╱╲  ╱╲  ╱╲
       ╱  ╲╱  ╲╱  ╲╱  ╲╱
                              → Both making higher highs/lows
CVD:   ╱╲  ╱╲  ╱╲  ╱╲  ╱╲
      ╱  ╲╱  ╲╱  ╲╱  ╲╱
      
= CONFIRMED UPTREND (CVD supports price)


CVD BEARISH DIVERGENCE (Reversal warning):
──────────────────────────────────────────
Price:  ╱╲   ╱╲   ╱╲   ← Higher highs
       ╱  ╲ ╱  ╲ ╱
      ╱    ╲╱    ╲╱

CVD:   ╱╲  ╱╲
      ╱  ╲╱  ╲╱╲  ╱╲  ← Lower highs (DIVERGENCE)
                 ╲╱
                 
= WARNING: Price making new highs but buyers are weakening
= Smart money is DISTRIBUTING (selling into the rally)
= Expect reversal DOWN


CVD BULLISH DIVERGENCE (Reversal opportunity):
──────────────────────────────────────────────
Price: ╲    ╱╲
        ╲  ╱  ╲  ╱╲  ← Lower lows
         ╲╱    ╲╱  ╲

CVD:          ╱╲  ╱╲
      ╲  ╱╲ ╱  ╲╱  ╲  ← Higher lows (DIVERGENCE)
       ╲╱  ╲╱

= OPPORTUNITY: Price making new lows but sellers are weakening
= Smart money is ACCUMULATING (buying the dip)
= Expect reversal UP
```

### 3.3 CVD Divergence Types

| Divergence Type | Price | CVD | Meaning | Reliability |
|----------------|-------|-----|---------|-------------|
| **Regular Bearish** | Higher High | Lower High | Buyers weakening at top | High |
| **Regular Bullish** | Lower Low | Higher Low | Sellers weakening at bottom | High |
| **Hidden Bearish** | Lower High | Higher High | Trend continuation setup | Moderate |
| **Hidden Bullish** | Higher Low | Lower Low | Trend continuation setup | Moderate |
| **Exaggerated Bearish** | Equal Highs | Much lower high | Extreme distribution | Very High |
| **Exaggerated Bullish** | Equal Lows | Much higher low | Extreme accumulation | Very High |

### 3.4 CVD Divergence Detection Algorithm

```python
class CVDDivergenceDetector:
    """
    Detects divergences between price and Cumulative Volume Delta.
    """
    
    def __init__(self, config: dict):
        self.min_swing_bars = config.get('min_swing_bars', 5)
        self.divergence_threshold = config.get('divergence_threshold', 0.1)
        self.lookback = config.get('divergence_lookback', 50)
    
    def detect(self, prices: List[float], cvd_values: List[float]) -> List[dict]:
        """
        Scan for divergences between price and CVD.
        
        Args:
            prices: List of close prices
            cvd_values: List of cumulative delta values (same length)
        
        Returns:
            List of detected divergences
        """
        if len(prices) < self.lookback or len(cvd_values) < self.lookback:
            return []
        
        divergences = []
        
        # Find swing highs in price and CVD
        price_highs = self._find_swing_highs(prices)
        price_lows = self._find_swing_lows(prices)
        cvd_highs = self._find_swing_highs(cvd_values)
        cvd_lows = self._find_swing_lows(cvd_values)
        
        # Check for BEARISH divergence (price HH, CVD LH)
        if len(price_highs) >= 2 and len(cvd_highs) >= 2:
            last_price_high = price_highs[-1]
            prev_price_high = price_highs[-2]
            
            # Find corresponding CVD highs (nearest in time)
            last_cvd_high = self._find_nearest(cvd_highs, last_price_high['index'])
            prev_cvd_high = self._find_nearest(cvd_highs, prev_price_high['index'])
            
            if last_cvd_high and prev_cvd_high:
                price_higher = last_price_high['value'] > prev_price_high['value']
                cvd_lower = last_cvd_high['value'] < prev_cvd_high['value']
                
                if price_higher and cvd_lower:
                    strength = self._calc_divergence_strength(
                        last_price_high, prev_price_high,
                        last_cvd_high, prev_cvd_high
                    )
                    
                    divergences.append({
                        'type': 'BEARISH_DIVERGENCE',
                        'price_points': [prev_price_high, last_price_high],
                        'cvd_points': [prev_cvd_high, last_cvd_high],
                        'strength': strength,
                        'bar_index': last_price_high['index'],
                        'signal': 'SELL'
                    })
        
        # Check for BULLISH divergence (price LL, CVD HL)
        if len(price_lows) >= 2 and len(cvd_lows) >= 2:
            last_price_low = price_lows[-1]
            prev_price_low = price_lows[-2]
            
            last_cvd_low = self._find_nearest(cvd_lows, last_price_low['index'])
            prev_cvd_low = self._find_nearest(cvd_lows, prev_price_low['index'])
            
            if last_cvd_low and prev_cvd_low:
                price_lower = last_price_low['value'] < prev_price_low['value']
                cvd_higher = last_cvd_low['value'] > prev_cvd_low['value']
                
                if price_lower and cvd_higher:
                    strength = self._calc_divergence_strength(
                        last_price_low, prev_price_low,
                        last_cvd_low, prev_cvd_low
                    )
                    
                    divergences.append({
                        'type': 'BULLISH_DIVERGENCE',
                        'price_points': [prev_price_low, last_price_low],
                        'cvd_points': [prev_cvd_low, last_cvd_low],
                        'strength': strength,
                        'bar_index': last_price_low['index'],
                        'signal': 'BUY'
                    })
        
        return divergences
    
    def _find_swing_highs(self, data: List[float]) -> List[dict]:
        """Find swing highs in data series."""
        highs = []
        n = self.min_swing_bars
        
        for i in range(n, len(data) - n):
            is_high = all(data[i] > data[i-j] for j in range(1, n+1)) and \
                      all(data[i] > data[i+j] for j in range(1, n+1))
            if is_high:
                highs.append({'index': i, 'value': data[i]})
        
        return highs
    
    def _find_swing_lows(self, data: List[float]) -> List[dict]:
        """Find swing lows in data series."""
        lows = []
        n = self.min_swing_bars
        
        for i in range(n, len(data) - n):
            is_low = all(data[i] < data[i-j] for j in range(1, n+1)) and \
                     all(data[i] < data[i+j] for j in range(1, n+1))
            if is_low:
                lows.append({'index': i, 'value': data[i]})
        
        return lows
    
    def _find_nearest(self, points: List[dict], target_index: int) -> Optional[dict]:
        """Find the point nearest to target_index."""
        if not points:
            return None
        return min(points, key=lambda p: abs(p['index'] - target_index))
    
    def _calc_divergence_strength(self, p1, p2, c1, c2) -> float:
        """
        Calculate divergence strength based on the magnitude of disagreement.
        """
        # Price change direction
        price_change = (p2['value'] - p1['value']) / abs(p1['value'])
        # CVD change direction
        cvd_change = (c2['value'] - c1['value']) / (abs(c1['value']) + 1e-10)
        
        # Strength is based on how much they disagree
        disagreement = abs(price_change - cvd_change)
        
        # Normalize to [0, 1]
        return min(disagreement * 5, 1.0)
```

### 3.5 CVD Reset Considerations

CVD accumulates indefinitely, which can make it hard to interpret over long periods. Solutions:

| Method | Description | When to Use |
|--------|-------------|-------------|
| **Session Reset** | Reset CVD to 0 at each session open | Intraday analysis |
| **Rolling Window** | Only consider last N bars | Medium-term analysis |
| **Anchored CVD** | Reset at specific events (swing H/L) | Event-based analysis |
| **Normalized CVD** | Divide CVD by cumulative volume | Cross-instrument comparison |

$$\text{Normalized CVD}(T) = \frac{\text{CVD}(T)}{\sum_{t=1}^{T} V_t}$$

---

## 4. Point of Control (POC)

### 4.1 Definition

The **Point of Control (POC)** is the price level where the most volume was traded within a given time period. It represents the price of maximum agreement between buyers and sellers — the "fair value" for that period.

$$\text{POC} = \arg\max_{P} V(P)$$

Where $V(P)$ is the total volume traded at price level $P$.

### 4.2 POC Calculation

```python
def calculate_poc(trades: List[Trade], tick_size: float) -> dict:
    """
    Calculate Point of Control from trade data.
    
    Args:
        trades: List of trades within the analysis period
        tick_size: Price granularity for volume profiling
    
    Returns:
        POC information including price, volume, and delta at POC
    """
    # Build volume profile
    volume_at_price = {}
    delta_at_price = {}
    
    for trade in trades:
        # Round to tick size
        price_level = round(trade.price / tick_size) * tick_size
        
        if price_level not in volume_at_price:
            volume_at_price[price_level] = 0.0
            delta_at_price[price_level] = 0.0
        
        volume_at_price[price_level] += trade.volume
        
        if trade.side == 'BUY':
            delta_at_price[price_level] += trade.volume
        else:
            delta_at_price[price_level] -= trade.volume
    
    # Find POC (maximum volume price)
    poc_price = max(volume_at_price, key=volume_at_price.get)
    
    return {
        'price': poc_price,
        'volume': volume_at_price[poc_price],
        'delta': delta_at_price[poc_price],
        'delta_direction': 'BUY' if delta_at_price[poc_price] > 0 else 'SELL',
        'total_volume': sum(volume_at_price.values()),
        'poc_volume_pct': volume_at_price[poc_price] / sum(volume_at_price.values())
    }
```

### 4.3 POC Types and Trading Implications

| POC Type | Description | Trading Implication |
|----------|-------------|-------------------|
| **Developing POC** | Current session's POC (changes in real-time) | Shows evolving fair value |
| **Fixed POC** | Completed session's POC (finalized) | Key S/R level |
| **Virgin POC (VPOC)** | POC that has NEVER been retested by price | Extremely strong S/R; magnet for price |
| **Migrating POC** | POC that shifts during the session | Indicates changing control |
| **Naked POC** | Same as VPOC — untested POC from previous session | High-probability target |

### 4.4 POC as Support/Resistance

```
VIRGIN POC (VPOC) AS MAGNET:
═══════════════════════════

Session 1:  Price creates a profile with POC at 1.1050
            Price closes ABOVE the POC → POC is "naked" below

             │███████│ 1.1070 (VAH)
             │█████████████│ 1.1060
             │████████████████│ 1.1050 ← POC (VPOC)
             │█████████████│ 1.1040
             │███████│ 1.1030 (VAL)

Session 2:  Price opens at 1.1080 (above previous POC)
            The VPOC at 1.1050 acts as a magnet

            Price will likely pull back to test 1.1050 (VPOC)
            If tested: VPOC becomes tested POC (less significant)
            If held: Strong support → continuation UP

TRADING RULE: Unfilled VPOCs are high-probability targets.
Price tends to revisit VPOCs within 1-3 sessions.
```

### 4.5 Delta at POC

The delta at the POC level provides directional bias:

| POC Delta | Interpretation |
|-----------|---------------|
| Strongly positive at POC | Buyers dominated at fair value → bullish bias |
| Strongly negative at POC | Sellers dominated at fair value → bearish bias |
| Neutral at POC | True equilibrium — no directional bias |
| Positive POC + price below POC | Discount buying opportunity |
| Negative POC + price above POC | Premium selling opportunity |

---

## 5. Value Area High/Low (VAH/VAL)

### 5.1 Definition

The **Value Area** is the price range where a specified percentage (typically 70%) of the total volume was traded. It defines the "fair value zone" where most market participants agreed to transact.

$$\text{Value Area} = \{P : \text{cumulative volume from POC includes 70% of total}\}$$

- **VAH (Value Area High)**: Upper boundary of the value area
- **VAL (Value Area Low)**: Lower boundary of the value area

### 5.2 Value Area Calculation Algorithm

```python
def calculate_value_area(volume_profile: Dict[float, float], 
                          poc_price: float,
                          target_pct: float = 0.70) -> dict:
    """
    Calculate Value Area using the TPO (Time Price Opportunity) method.
    
    Method: Starting from POC, add rows above and below,
    always adding the row with higher volume, until
    target_pct of total volume is captured.
    """
    total_volume = sum(volume_profile.values())
    target_volume = total_volume * target_pct
    
    # Sort prices
    sorted_prices = sorted(volume_profile.keys())
    poc_idx = sorted_prices.index(poc_price)
    
    # Start from POC
    captured_volume = volume_profile[poc_price]
    upper_idx = poc_idx
    lower_idx = poc_idx
    
    while captured_volume < target_volume:
        # Look at next row above and below
        can_go_up = upper_idx < len(sorted_prices) - 1
        can_go_down = lower_idx > 0
        
        if not can_go_up and not can_go_down:
            break
        
        vol_above = volume_profile[sorted_prices[upper_idx + 1]] if can_go_up else 0
        vol_below = volume_profile[sorted_prices[lower_idx - 1]] if can_go_down else 0
        
        # Add the side with more volume
        if vol_above >= vol_below and can_go_up:
            upper_idx += 1
            captured_volume += vol_above
        elif can_go_down:
            lower_idx -= 1
            captured_volume += vol_below
        else:
            upper_idx += 1
            captured_volume += vol_above
    
    return {
        'vah': sorted_prices[upper_idx],
        'val': sorted_prices[lower_idx],
        'poc': poc_price,
        'value_area_volume': captured_volume,
        'value_area_pct': captured_volume / total_volume,
        'value_area_width': sorted_prices[upper_idx] - sorted_prices[lower_idx]
    }
```

### 5.3 Trading the Value Area

**Value Area Rules (from Market Profile theory):**

| Scenario | Condition | Action |
|----------|-----------|--------|
| **Trend Day Up** | Price opens above VAH, stays above | Buy pullbacks to VAH |
| **Trend Day Down** | Price opens below VAL, stays below | Sell rallies to VAL |
| **Normal Day** | Price opens within VA, rotates | Buy VAL, sell VAH (range trade) |
| **Failed Auction** | Price opens outside VA, fails to continue | Fade back into VA |
| **Acceptance above** | Price opens above VAH, holds above | Previous VAH becomes support |
| **Acceptance below** | Price opens below VAL, holds below | Previous VAL becomes resistance |

### 5.4 Value Area Opening Strategies

```
80% RULE:
═════════

"If the market opens within the Value Area and then moves
outside the Value Area, there is an 80% chance it will
rotate back to the other side of the Value Area."

Example (Opening within VA, moving above VAH):
─────────────────────────────────────────────

  VAH ─── 1.1070 ───────────────────────────────────────
                              ╱╲          TARGET: VAL
         Opening here ─  ╱╲ ╱  ╲  ╱╲     (80% probability
                        ╱  ╲╱    ╲╱  ╲     of reaching VAL)
  VAL ─── 1.1030 ──────────────────────╲─────────────────
                                         ╲╱  ← Reaches VAL
                                         
  IF: Open within VA
  AND: Price breaks ABOVE VAH (or below VAL)
  AND: Price FAILS to continue (acceptance rejection)
  THEN: Target = opposite side of VA (80% probability)

This is one of the highest-probability setups in volume profile trading.
```

### 5.5 Multi-Session Value Area Analysis

```python
def analyze_value_area_relationship(current_va: dict, 
                                     previous_va: dict,
                                     current_price: float) -> dict:
    """
    Analyze the relationship between current and previous session's
    value areas to determine market type and bias.
    """
    # Determine opening type
    if current_price > previous_va['vah']:
        open_type = 'ABOVE_VA'
    elif current_price < previous_va['val']:
        open_type = 'BELOW_VA'
    else:
        open_type = 'WITHIN_VA'
    
    # Determine VA migration
    va_shift = current_va['poc'] - previous_va['poc']
    va_overlapping = (
        current_va['val'] < previous_va['vah'] and 
        current_va['vah'] > previous_va['val']
    )
    
    # Generate analysis
    if open_type == 'ABOVE_VA':
        bias = 'BULLISH'
        strategy = 'BUY_DIPS_TO_PREV_VAH'
        note = 'Previous VAH is new support. Buy pullbacks.'
    elif open_type == 'BELOW_VA':
        bias = 'BEARISH'
        strategy = 'SELL_RALLIES_TO_PREV_VAL'
        note = 'Previous VAL is new resistance. Sell rallies.'
    else:
        bias = 'NEUTRAL'
        strategy = 'RANGE_TRADE_VA_BOUNDARIES'
        note = 'Trade between VAH and VAL. Apply 80% rule.'
    
    return {
        'open_type': open_type,
        'bias': bias,
        'strategy': strategy,
        'note': note,
        'va_shift': va_shift,
        'va_overlapping': va_overlapping,
        'previous_poc': previous_va['poc'],
        'previous_vah': previous_va['vah'],
        'previous_val': previous_va['val']
    }
```

---

## 6. Volume-Weighted Average Price (VWAP) and Bands

### 6.1 VWAP Definition

VWAP is the average price weighted by volume — the true average price at which the market traded during a period.

$$\text{VWAP}(T) = \frac{\sum_{t=1}^{T} P_t \cdot V_t}{\sum_{t=1}^{T} V_t}$$

Where:
- $P_t$ = Typical price at time $t$ (or trade price for tick data)
- $V_t$ = Volume at time $t$
- $T$ = Current time (cumulative from anchor point)

**Typical Price for bar-based VWAP:**
$$P_{typical} = \frac{High + Low + Close}{3}$$

### 6.2 VWAP Standard Deviation Bands

VWAP bands use the standard deviation of price-volume to create dynamic support/resistance levels:

$$\sigma_{VWAP}(T) = \sqrt{\frac{\sum_{t=1}^{T} V_t \cdot (P_t - \text{VWAP}(T))^2}{\sum_{t=1}^{T} V_t}}$$

**Band Levels:**
- Upper Band 1: $\text{VWAP} + 1\sigma$
- Upper Band 2: $\text{VWAP} + 2\sigma$
- Upper Band 3: $\text{VWAP} + 3\sigma$ (extreme)
- Lower Band 1: $\text{VWAP} - 1\sigma$
- Lower Band 2: $\text{VWAP} - 2\sigma$
- Lower Band 3: $\text{VWAP} - 3\sigma$ (extreme)

### 6.3 VWAP Implementation

```python
class VWAP:
    """
    Volume-Weighted Average Price with standard deviation bands.
    Supports multiple anchor types: session, weekly, monthly, custom.
    """
    
    def __init__(self, anchor_type='SESSION'):
        self.anchor_type = anchor_type
        self.reset()
    
    def reset(self):
        """Reset VWAP calculation (new anchor point)."""
        self.cumulative_volume = 0.0
        self.cumulative_pv = 0.0  # Price * Volume
        self.cumulative_pv_sq = 0.0  # Price^2 * Volume
        self.vwap_value = 0.0
        self.std_dev = 0.0
        self.data_points = 0
    
    def update(self, typical_price: float, volume: float):
        """
        Update VWAP with new data point.
        
        Args:
            typical_price: (H+L+C)/3 or trade price
            volume: Volume for this period/trade
        """
        self.cumulative_volume += volume
        self.cumulative_pv += typical_price * volume
        self.cumulative_pv_sq += (typical_price ** 2) * volume
        self.data_points += 1
        
        if self.cumulative_volume > 0:
            self.vwap_value = self.cumulative_pv / self.cumulative_volume
            
            # Standard deviation
            variance = (
                self.cumulative_pv_sq / self.cumulative_volume - 
                self.vwap_value ** 2
            )
            self.std_dev = np.sqrt(max(variance, 0))
    
    def get_bands(self) -> dict:
        """Get VWAP and all band levels."""
        return {
            'vwap': self.vwap_value,
            'upper_1': self.vwap_value + self.std_dev,
            'upper_2': self.vwap_value + 2 * self.std_dev,
            'upper_3': self.vwap_value + 3 * self.std_dev,
            'lower_1': self.vwap_value - self.std_dev,
            'lower_2': self.vwap_value - 2 * self.std_dev,
            'lower_3': self.vwap_value - 3 * self.std_dev,
            'std_dev': self.std_dev
        }
    
    def get_price_position(self, current_price: float) -> dict:
        """
        Determine where current price sits relative to VWAP bands.
        """
        if self.std_dev == 0:
            return {'z_score': 0, 'zone': 'AT_VWAP'}
        
        z_score = (current_price - self.vwap_value) / self.std_dev
        
        if abs(z_score) < 0.5:
            zone = 'AT_VWAP'
        elif z_score >= 0.5 and z_score < 1.5:
            zone = 'UPPER_1'
        elif z_score >= 1.5 and z_score < 2.5:
            zone = 'UPPER_2'
        elif z_score >= 2.5:
            zone = 'UPPER_3_EXTREME'
        elif z_score <= -0.5 and z_score > -1.5:
            zone = 'LOWER_1'
        elif z_score <= -1.5 and z_score > -2.5:
            zone = 'LOWER_2'
        else:
            zone = 'LOWER_3_EXTREME'
        
        return {
            'z_score': z_score,
            'zone': zone,
            'distance_from_vwap': current_price - self.vwap_value,
            'distance_pct': (current_price - self.vwap_value) / self.vwap_value * 100
        }
```

### 6.4 VWAP Trading Strategies

| Strategy | Condition | Entry | Stop | Target |
|----------|-----------|-------|------|--------|
| **VWAP Mean Reversion** | Price at +2σ or -2σ | Fade towards VWAP | Beyond ±3σ | VWAP |
| **VWAP Trend** | Price persistently above/below VWAP | Buy at VWAP retest (uptrend) | Below VWAP -1σ | +1σ or +2σ |
| **VWAP Breakout** | Price crosses VWAP with volume | Trade in direction of cross | Other side of VWAP | ±1σ |
| **Institutional VWAP** | Expect institution to buy/sell at VWAP | Join the flow at VWAP | Beyond VWAP ±1σ | With trend |
| **VWAP Gap Fill** | Price gaps away from VWAP | Fade gap towards VWAP | Beyond gap extreme | VWAP |

### 6.5 Anchored VWAP

Anchored VWAP starts from a significant event rather than session open:

| Anchor Point | Use Case | Interpretation |
|-------------|----------|---------------|
| Swing High | Bearish anchor | Average SHORT entry since the high |
| Swing Low | Bullish anchor | Average LONG entry since the low |
| News Event | Event analysis | Average entry since news |
| Earnings/Halving | Fundamental anchor | Long-term institutional cost basis |
| Volume Climax | Reversal analysis | Average entry since climax |

**Key Insight**: If price is above an anchored VWAP from a swing low, anyone who bought since that low is in profit on average. If price drops below it, they are underwater — creating potential selling pressure.

### 6.6 Multi-VWAP Analysis

```python
class MultiVWAP:
    """
    Manages multiple VWAP calculations with different anchors.
    """
    
    def __init__(self):
        self.vwaps = {
            'session': VWAP(anchor_type='SESSION'),
            'weekly': VWAP(anchor_type='WEEKLY'),
            'monthly': VWAP(anchor_type='MONTHLY'),
        }
        self.anchored_vwaps = {}  # Custom anchored VWAPs
    
    def add_anchored_vwap(self, name: str, anchor_price: float, anchor_volume: float):
        """Add a new anchored VWAP from a significant level."""
        vwap = VWAP(anchor_type='CUSTOM')
        vwap.update(anchor_price, anchor_volume)
        self.anchored_vwaps[name] = vwap
    
    def update_all(self, typical_price: float, volume: float, timestamp: float):
        """Update all VWAPs with new data."""
        for vwap in self.vwaps.values():
            vwap.update(typical_price, volume)
        
        for vwap in self.anchored_vwaps.values():
            vwap.update(typical_price, volume)
    
    def get_confluence_zones(self, current_price: float) -> List[dict]:
        """
        Find zones where multiple VWAP levels converge.
        Confluence of VWAPs = strong S/R.
        """
        all_levels = []
        
        for name, vwap in {**self.vwaps, **self.anchored_vwaps}.items():
            bands = vwap.get_bands()
            for level_name, price in bands.items():
                if price > 0:
                    all_levels.append({
                        'vwap_name': name,
                        'level_name': level_name,
                        'price': price
                    })
        
        # Find clusters (confluence)
        all_levels.sort(key=lambda x: x['price'])
        clusters = []
        tolerance = current_price * 0.001  # 0.1% tolerance
        
        i = 0
        while i < len(all_levels):
            cluster = [all_levels[i]]
            j = i + 1
            while j < len(all_levels) and all_levels[j]['price'] - all_levels[i]['price'] < tolerance:
                cluster.append(all_levels[j])
                j += 1
            
            if len(cluster) >= 2:
                clusters.append({
                    'price': np.mean([l['price'] for l in cluster]),
                    'strength': len(cluster),
                    'components': cluster,
                    'distance_from_price': abs(current_price - np.mean([l['price'] for l in cluster]))
                })
            
            i = j
        
        return sorted(clusters, key=lambda c: c['distance_from_price'])
```

---

## 7. Mathematical Formulas

### 7.1 Complete Delta Formulas

**Per-Trade Delta:**
$$\delta_i = V_i \cdot \mathbb{1}_{ask}(P_i) - V_i \cdot \mathbb{1}_{bid}(P_i)$$

**Per-Bar Delta:**
$$\Delta_{bar} = \sum_{i \in bar} \delta_i$$

**Cumulative Volume Delta:**
$$\text{CVD}(T) = \sum_{t=0}^{T} \Delta_t$$

**Normalized Delta:**
$$\hat{\Delta}_t = \frac{\Delta_t}{\sqrt{V_t}} \quad \text{(variance-stabilized)}$$

**Delta Momentum:**
$$M_\Delta(t, n) = \text{CVD}(t) - \text{CVD}(t-n)$$

**Delta Rate (per unit time):**
$$R_\Delta(t) = \frac{\Delta_t}{\Delta t_{seconds}}$$

### 7.2 Volume Profile Formulas

**Volume at Price:**
$$V(P) = \sum_{i: P_i = P} V_i$$

**Point of Control:**
$$\text{POC} = \arg\max_P V(P)$$

**Value Area (70% rule):**
$$\text{VA} = \{P : \sum_{P' \in VA} V(P') \geq 0.70 \cdot \sum_{all P} V(P)\}$$

**Volume Profile Skewness:**
$$\gamma_{VP} = \frac{\sum_P V(P) \cdot (P - \text{POC})^3}{\left[\sum_P V(P) \cdot (P - \text{POC})^2\right]^{3/2}}$$

Positive skewness = more volume below POC (bullish bias)
Negative skewness = more volume above POC (bearish bias)

### 7.3 VWAP Formulas

**Standard VWAP:**
$$\text{VWAP}(T) = \frac{\sum_{t=1}^{T} P_t \cdot V_t}{\sum_{t=1}^{T} V_t}$$

**VWAP Standard Deviation:**
$$\sigma_{VWAP} = \sqrt{\frac{\sum_{t=1}^{T} V_t \cdot (P_t - \text{VWAP})^2}{\sum_{t=1}^{T} V_t}}$$

**VWAP Z-Score:**
$$Z_{VWAP} = \frac{P_{current} - \text{VWAP}}{\sigma_{VWAP}}$$

**TWAP (Time-Weighted Average Price):**
$$\text{TWAP}(T) = \frac{1}{T} \sum_{t=1}^{T} P_t$$

**VWAP vs TWAP Divergence:**
$$\text{VT Div} = \text{VWAP} - \text{TWAP}$$

Positive VT Div: Higher prices had more volume (bullish, institutions buying higher)
Negative VT Div: Lower prices had more volume (bearish, institutions selling lower)

### 7.4 Order Flow Imbalance Index (OFII)

A composite measure combining delta, volume profile, and VWAP:

$$\text{OFII}(t) = w_1 \cdot \hat{\Delta}_t + w_2 \cdot \frac{P_t - \text{POC}}{\text{VAH} - \text{VAL}} + w_3 \cdot Z_{VWAP}(t)$$

Where:
- $w_1 = 0.40$ (delta weight)
- $w_2 = 0.30$ (volume profile weight)
- $w_3 = 0.30$ (VWAP weight)

**OFII Interpretation:**
- OFII > 0.5: Strong bullish order flow
- OFII > 1.0: Extreme bullish (may be overextended)
- OFII < -0.5: Strong bearish order flow
- OFII < -1.0: Extreme bearish (may be overextended)

---

## 8. Trading Signals from Volume Delta

### 8.1 Signal Catalog

| Signal Name | Condition | Direction | Strength | Timeframe |
|------------|-----------|-----------|----------|-----------|
| **Delta Confirmation** | Delta and price aligned | With trend | Moderate | All |
| **Delta Divergence** | CVD diverges from price | Counter-trend | High | 1H+ |
| **Absorption Delta** | Large delta, small price move | Reversal | High | 15M-4H |
| **Exhaustion Delta** | Extreme delta at swing extreme | Reversal | Very High | 1H+ |
| **Delta Flip** | CVD slope changes sign | Reversal | Moderate | 4H+ |
| **Delta Acceleration** | $\ddot{\Delta}$ extreme | Momentum | Moderate | 15M-1H |
| **VWAP Reclaim** | Price crosses back above/below VWAP | Trend | Moderate | Intraday |
| **POC Rejection** | Price tests VPOC and bounces | Support/Resistance | High | All |
| **VA Breakout** | Price breaks out of VA with volume | Trend | High | All |

### 8.2 Delta Exhaustion Signal

One of the most powerful reversal signals:

```
DELTA EXHAUSTION (Bearish):
═══════════════════════════

    Price: ───────╱╲──── New High (barely)
               ╱╲╱  ╲
              ╱      ╲

    Delta: ████████ +800  (Bar -3)
           ██████   +600  (Bar -2)
           ███     +300   (Bar -1)
           █      +50     (Current bar) ← EXHAUSTION

    Pattern: Price making new high BUT delta DECLINING sharply
    Each bar has LESS buying aggression than the previous
    
    Signal: STRONG SELL
    Entry: Below current bar's low
    SL: Above current bar's high
    Target: Previous swing low or POC
```

```
DELTA EXHAUSTION (Bullish):
═══════════════════════════

    Delta: ████████ -800  (Bar -3)
           ██████   -600  (Bar -2)
           ███     -300   (Bar -1)
           █      -50     (Current bar) ← EXHAUSTION

    Price: ╲      ╱────── New Low (barely)
            ╲╱╲  ╱
             ╲╱╲╱

    Pattern: Price making new low BUT delta DECLINING (less selling)
    
    Signal: STRONG BUY
```

### 8.3 Delta-Price Divergence Signal Quality

| Divergence Grade | Criteria | Win Rate (historical) | R:R |
|-----------------|----------|----------------------|-----|
| A+ | HTF divergence (D1/W1) + Kill zone + FVG | 70-75% | 4-6:1 |
| A | MTF divergence (4H) + Kill zone | 60-65% | 3-4:1 |
| B | LTF divergence (1H) + Other confluence | 55-60% | 2-3:1 |
| C | LTF divergence only | 50-55% | 1.5-2:1 |
| D | Very short-term (15M) divergence | 45-50% | Skip |

### 8.4 Combined Signals Implementation

```python
class VolumeSignalGenerator:
    """
    Generates trading signals from volume delta, VWAP, and volume profile.
    """
    
    def __init__(self, config):
        self.delta_calc = DeltaCalculator(config)
        self.cvd_detector = CVDDivergenceDetector(config)
        self.vwap = MultiVWAP()
        self.volume_profile = VolumeProfileBuilder(config)
        self.min_signal_strength = config.get('min_signal_strength', 0.5)
    
    def generate_signals(self, candles: List[Candle], 
                          current_price: float) -> List[dict]:
        """Generate all volume-based signals for current state."""
        signals = []
        
        # 1. CVD Divergence
        prices = [c.close for c in candles]
        cvd_values = self._get_cvd_series(candles)
        divergences = self.cvd_detector.detect(prices, cvd_values)
        
        for div in divergences:
            if div['strength'] >= self.min_signal_strength:
                signals.append({
                    'type': 'CVD_DIVERGENCE',
                    'direction': 'LONG' if div['type'] == 'BULLISH_DIVERGENCE' else 'SHORT',
                    'strength': div['strength'],
                    'details': div
                })
        
        # 2. Delta Exhaustion
        exhaustion = self._check_delta_exhaustion(candles[-5:])
        if exhaustion:
            signals.append(exhaustion)
        
        # 3. VWAP Position
        vwap_pos = self.vwap.vwaps['session'].get_price_position(current_price)
        if abs(vwap_pos['z_score']) >= 2.0:
            signals.append({
                'type': 'VWAP_EXTREME',
                'direction': 'SHORT' if vwap_pos['z_score'] > 0 else 'LONG',
                'strength': min(abs(vwap_pos['z_score']) / 3.0, 1.0),
                'z_score': vwap_pos['z_score'],
                'target': self.vwap.vwaps['session'].vwap_value
            })
        
        # 4. POC test
        poc = self.volume_profile.get_previous_session_poc()
        if poc and abs(current_price - poc['price']) / current_price < 0.001:
            signals.append({
                'type': 'POC_TEST',
                'direction': 'LONG' if poc['delta'] > 0 else 'SHORT',
                'strength': 0.6,
                'poc_price': poc['price'],
                'poc_delta': poc['delta']
            })
        
        # 5. Value Area breakout/rejection
        va_signal = self._check_value_area(current_price, candles)
        if va_signal:
            signals.append(va_signal)
        
        return signals
    
    def _check_delta_exhaustion(self, recent_candles: List[Candle]) -> Optional[dict]:
        """Check for delta exhaustion pattern in recent candles."""
        if len(recent_candles) < 4:
            return None
        
        deltas = [getattr(c, 'delta', 0) for c in recent_candles]
        
        # Bullish exhaustion: negative deltas getting smaller at new lows
        if all(d < 0 for d in deltas[:-1]):
            abs_deltas = [abs(d) for d in deltas]
            if all(abs_deltas[i] > abs_deltas[i+1] for i in range(len(abs_deltas)-1)):
                # Declining selling pressure
                prices = [c.low for c in recent_candles]
                if prices[-1] <= min(prices[:-1]):
                    return {
                        'type': 'DELTA_EXHAUSTION',
                        'direction': 'LONG',
                        'strength': 0.8,
                        'delta_sequence': deltas,
                        'signal': 'Selling exhaustion at new low'
                    }
        
        # Bearish exhaustion: positive deltas getting smaller at new highs
        if all(d > 0 for d in deltas[:-1]):
            if all(deltas[i] > deltas[i+1] for i in range(len(deltas)-1)):
                prices = [c.high for c in recent_candles]
                if prices[-1] >= max(prices[:-1]):
                    return {
                        'type': 'DELTA_EXHAUSTION',
                        'direction': 'SHORT',
                        'strength': 0.8,
                        'delta_sequence': deltas,
                        'signal': 'Buying exhaustion at new high'
                    }
        
        return None
```

---

## 9. Integration with Price Action

### 9.1 Delta Confirmation of Price Patterns

| Price Pattern | Delta Confirmation | Meaning |
|--------------|-------------------|---------|
| Bullish Engulfing | Positive delta on engulfing bar | Genuine reversal — strong signal |
| Bullish Engulfing | Negative delta on engulfing bar | Potentially fake — be cautious |
| Pin Bar (hammer) | Extreme positive delta on wick | Real buying at the low — strong |
| Pin Bar (hammer) | Low delta | Just lack of selling, not active buying — weaker |
| Break of Structure (BOS) | Large delta in direction of break | Real break — follow it |
| Break of Structure (BOS) | Low delta on break | Potentially a stop hunt — wait for retest |
| FVG formation | Extreme directional delta on C2 | Strong FVG — high probability of holding |
| FVG formation | Low delta on C2 | Weak FVG — may be filled completely |

### 9.2 Volume Profile + ICT Concepts

```
COMBINING VOLUME PROFILE WITH ICT:
═══════════════════════════════════

HTF Volume Profile:              ICT Concepts:
─────────────────                ─────────────

 │████│ 1.1080 (HVN)  ─────── BSL (stops above this cluster)
 │██████████████│ 1.1070 (VAH)
 │████████████████████│ 1.1060 
 │██████████████████████████│ 1.1050 (POC) ── Order Block at POC = STRONG
 │████████████████████│ 1.1040
 │██████████████│ 1.1030 (VAL)
 │████│ 1.1020 (HVN)  ─────── SSL (stops below this cluster)
 │ │ 1.1010 (LVN)     ─────── Liquidity Void = FVG zone
 │ │ 1.1000 (LVN)     ─────── Price moves fast through LVN
 │████│ 1.0990 (HVN)

KEY INSIGHTS:
1. HVN (High Volume Node) = strong S/R = likely where OBs form
2. LVN (Low Volume Node) = price moves fast through = FVG/void territory
3. POC alignment with OB = premium setup
4. VA boundaries alignment with BSL/SSL = high-probability targets
5. VPOCs act like magnets (similar to FVGs — price tends to revisit)
```

### 9.3 Multi-Tool Confluence Scoring

```python
def calculate_volume_confluence(price: float, 
                                 delta_signal: dict,
                                 vwap_state: dict,
                                 profile_state: dict,
                                 price_action_signal: dict) -> float:
    """
    Calculate a composite confluence score combining all volume
    tools with price action.
    
    Returns: Score from -1 (extreme bearish) to +1 (extreme bullish)
    """
    scores = []
    
    # 1. Delta direction
    if delta_signal:
        delta_score = delta_signal.get('strength', 0) * (
            1 if delta_signal['direction'] == 'LONG' else -1
        )
        scores.append(('delta', delta_score, 0.30))
    
    # 2. VWAP position
    if vwap_state:
        z = vwap_state.get('z_score', 0)
        # Below VWAP = bullish bias (discounted), above = bearish bias
        vwap_score = -np.tanh(z * 0.5)  # Maps z-score to [-1, 1]
        scores.append(('vwap', vwap_score, 0.20))
    
    # 3. Volume Profile
    if profile_state:
        # Price below POC = discounted (bullish), above = premium (bearish)
        if profile_state.get('poc'):
            poc_dist = (price - profile_state['poc']) / profile_state.get('va_width', 1)
            profile_score = -np.tanh(poc_dist)
            scores.append(('profile', profile_score, 0.25))
    
    # 4. Price action alignment
    if price_action_signal:
        pa_score = price_action_signal.get('strength', 0) * (
            1 if price_action_signal['direction'] == 'LONG' else -1
        )
        scores.append(('price_action', pa_score, 0.25))
    
    # Weighted sum
    if not scores:
        return 0.0
    
    total_weight = sum(w for _, _, w in scores)
    composite = sum(score * weight for _, score, weight in scores) / total_weight
    
    return np.clip(composite, -1.0, 1.0)
```

---

## 10. Core Logic — Entry/Exit

### 10.1 Volume Delta Entry Framework

| Setup | Entry Trigger | Delta Condition | VWAP Condition | Profile Condition |
|-------|-------------|----------------|---------------|-----------------|
| **Delta Divergence Long** | Price at support + Bullish CVD divergence | CVD higher low, price lower low | Price below VWAP (discounted) | Near VAL or POC |
| **Delta Divergence Short** | Price at resistance + Bearish CVD divergence | CVD lower high, price higher high | Price above VWAP (premium) | Near VAH or POC |
| **VWAP Bounce Long** | Price touches VWAP from above, bounces | Positive delta on bounce bar | Price at VWAP exactly | Above POC |
| **VWAP Bounce Short** | Price touches VWAP from below, rejected | Negative delta on rejection | Price at VWAP exactly | Below POC |
| **VA Breakout Long** | Price breaks above VAH with volume | Strong positive delta on break | Price above VWAP | Clearing VAH |
| **VA Breakout Short** | Price breaks below VAL with volume | Strong negative delta on break | Price below VWAP | Clearing VAL |
| **POC Magnet Long** | VPOC below current price (untested) | Positive delta developing | N/A | VPOC is target |
| **Exhaustion Reversal** | Delta exhaustion at extreme | Declining absolute delta | At ±2σ band | At VA extreme |

### 10.2 Exit Framework

| Exit Type | Condition | Action |
|-----------|-----------|--------|
| **Target VPOC** | Price reaches naked VPOC target | Take profit (full or partial) |
| **VWAP Reversion** | Price reaches VWAP (if entered from extreme) | Take 50% profit |
| **Delta Flip** | CVD slope flips against position | Close or tighten stop |
| **VA Opposite Side** | Price reaches other side of VA | Take profit |
| **Volume Climax** | Extreme volume + reversal candle | Emergency exit |
| **Time Exit** | End of session (for intraday) | Close position |

---

## 11. Technical Specifications

### 11.1 Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `bar_timeframe_s` | 3600 | [60, 86400] | Delta bar period in seconds |
| `cvd_lookback` | 50 | [20, 200] | Bars for CVD divergence detection |
| `divergence_min_swing_bars` | 5 | [3, 15] | Min bars for swing detection in CVD |
| `divergence_strength_threshold` | 0.5 | [0.3, 0.9] | Min divergence strength to signal |
| `vwap_anchor` | 'SESSION' | ['SESSION','WEEKLY','MONTHLY'] | VWAP reset period |
| `vwap_extreme_z` | 2.0 | [1.5, 3.0] | Z-score for extreme signal |
| `va_pct` | 0.70 | [0.60, 0.80] | Volume percentage for value area |
| `poc_tolerance_pct` | 0.1 | [0.05, 0.3] | % tolerance for POC test |
| `exhaustion_min_bars` | 4 | [3, 7] | Min bars for exhaustion pattern |
| `delta_strength_threshold` | 0.3 | [0.2, 0.6] | Min strength for delta signal |

### 11.2 Data Pipeline

```
RAW TRADE DATA → CLASSIFICATION → AGGREGATION → ANALYSIS → SIGNALS
     │                │               │              │           │
     │ price, vol,    │ Buy/Sell      │ Per-bar     │ CVD,     │ Trading
     │ timestamp      │ classification│ delta, VP   │ VWAP,    │ decisions
     │                │               │ POC, VA     │ Profile  │
     │                │               │             │          │
     ▼                ▼               ▼             ▼          ▼
  Exchange        Lee-Ready        Time-based    Statistical  Rule-based
  WebSocket       or Exchange      aggregation   analysis     engine
                  flag
```

---

## 12. Risk Parameters

### 12.1 Position Sizing by Signal Quality

| Signal Quality | Risk Per Trade | Size Multiplier | Basis |
|---------------|---------------|-----------------|-------|
| A+ (Multi-TF divergence + confluence) | 2.0% | 1.5x | Highest conviction |
| A (HTF divergence + one confluence) | 1.5% | 1.0x | Standard |
| B (MTF signal + weak confluence) | 1.0% | 0.75x | Reduced |
| C (Single signal, no confluence) | 0.5% | 0.5x | Minimum |

### 12.2 Stop Loss Rules for Volume Strategies

| Strategy | Stop Placement | Maximum Stop (ATR) |
|----------|---------------|-------------------|
| CVD Divergence | Beyond the swing that formed the divergence | 2.0 ATR |
| VWAP Mean Reversion | Beyond ±3σ band | 1.5 ATR |
| VA Breakout | Back inside VA (failed breakout) | 1.0 ATR |
| POC Test | Beyond POC + 0.5 ATR buffer | 1.5 ATR |
| Delta Exhaustion | Beyond the exhaustion extreme | 1.0 ATR |

### 12.3 R:R Targets

| Strategy | TP1 | TP2 | TP3 |
|----------|-----|-----|-----|
| CVD Divergence | 1:1 (50% size) | 2:1 (30%) | 3:1+ (20% trail) |
| VWAP Reversion | VWAP (60%) | Opposite band (40%) | — |
| VA Trade | POC (33%) | Opposite VA boundary (33%) | Beyond VA (34%) |
| Exhaustion | 1:1 (50%) | 2.5:1 (30%) | 4:1 (20% trail) |

---

## 13. Execution Flow — Pseudocode

```python
class VolumeDeltaTradingSystem:
    """
    Complete trading system based on volume delta, VWAP, and volume profile.
    """
    
    def __init__(self, config):
        self.delta_calc = DeltaCalculator(config)
        self.cvd_detector = CVDDivergenceDetector(config)
        self.vwap_mgr = MultiVWAP()
        self.profile_builder = VolumeProfileBuilder(config)
        self.signal_gen = VolumeSignalGenerator(config)
        self.risk_mgr = RiskManager(config)
        self.position_mgr = PositionManager()
        
        self.config = config
    
    async def run(self, data_feed):
        """Main execution loop."""
        
        async for event in data_feed:
            
            if event.type == 'TRADE':
                # Update delta calculator with each trade
                self.delta_calc.on_trade(
                    price=event.price,
                    volume=event.volume,
                    side=event.side,
                    timestamp=event.timestamp
                )
                
                # Update VWAP
                self.vwap_mgr.update_all(
                    typical_price=event.price,
                    volume=event.volume,
                    timestamp=event.timestamp
                )
                
                # Update volume profile
                self.profile_builder.add_trade(event)
            
            elif event.type == 'BAR_CLOSE':
                # === NEW BAR ANALYSIS ===
                candles = data_feed.get_candles(self.config['timeframe'], limit=100)
                current_price = candles[-1].close
                
                # Generate signals
                signals = self.signal_gen.generate_signals(candles, current_price)
                
                if not signals:
                    continue
                
                # Filter and rank signals
                valid_signals = [
                    s for s in signals 
                    if s['strength'] >= self.config['min_signal_strength']
                ]
                
                if not valid_signals:
                    continue
                
                # Take the strongest signal
                best_signal = max(valid_signals, key=lambda s: s['strength'])
                
                # === ENTRY LOGIC ===
                if not self.position_mgr.has_open_positions():
                    entry = self._generate_entry(best_signal, candles, current_price)
                    
                    if entry and entry['risk_reward'] >= self.config['min_rr']:
                        size = self.risk_mgr.calculate_size(
                            entry=entry['entry_price'],
                            stop=entry['stop_loss'],
                            signal_quality=best_signal['strength']
                        )
                        
                        await self._execute_entry(entry, size)
                
                # === EXIT LOGIC ===
                else:
                    for position in self.position_mgr.get_open_positions():
                        exit_signal = self._check_exit(
                            position, best_signal, candles, current_price
                        )
                        if exit_signal:
                            await self._execute_exit(position, exit_signal)
    
    def _generate_entry(self, signal: dict, candles: List, current_price: float) -> Optional[dict]:
        """Generate entry parameters from a signal."""
        
        atr = self._calc_atr(candles)
        
        if signal['type'] == 'CVD_DIVERGENCE':
            if signal['direction'] == 'LONG':
                entry_price = current_price
                stop_loss = min(c.low for c in candles[-10:]) - atr
                take_profit = current_price + 3 * (current_price - stop_loss)
            else:
                entry_price = current_price
                stop_loss = max(c.high for c in candles[-10:]) + atr
                take_profit = current_price - 3 * (stop_loss - current_price)
        
        elif signal['type'] == 'VWAP_EXTREME':
            vwap_val = signal.get('target', self.vwap_mgr.vwaps['session'].vwap_value)
            if signal['direction'] == 'LONG':
                entry_price = current_price
                stop_loss = current_price - 1.5 * atr
                take_profit = vwap_val
            else:
                entry_price = current_price
                stop_loss = current_price + 1.5 * atr
                take_profit = vwap_val
        
        elif signal['type'] == 'DELTA_EXHAUSTION':
            if signal['direction'] == 'LONG':
                entry_price = current_price
                stop_loss = candles[-1].low - 0.5 * atr
                take_profit = current_price + 2.5 * (current_price - stop_loss)
            else:
                entry_price = current_price
                stop_loss = candles[-1].high + 0.5 * atr
                take_profit = current_price - 2.5 * (stop_loss - current_price)
        
        else:
            return None
        
        risk_reward = abs(take_profit - entry_price) / abs(entry_price - stop_loss)
        
        return {
            'direction': signal['direction'],
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_reward': risk_reward,
            'signal_type': signal['type'],
            'strength': signal['strength']
        }
    
    def _check_exit(self, position, latest_signal, candles, current_price) -> Optional[dict]:
        """Check if position should be exited."""
        
        # Exit 1: Take profit reached
        if position.direction == 'LONG' and current_price >= position.take_profit:
            return {'reason': 'TP_REACHED', 'price': current_price}
        elif position.direction == 'SHORT' and current_price <= position.take_profit:
            return {'reason': 'TP_REACHED', 'price': current_price}
        
        # Exit 2: Opposing signal
        if latest_signal and latest_signal['direction'] != position.direction:
            if latest_signal['strength'] > 0.7:
                return {'reason': 'OPPOSING_SIGNAL', 'price': current_price}
        
        # Exit 3: VWAP target reached (for mean reversion trades)
        if position.signal_type == 'VWAP_EXTREME':
            vwap = self.vwap_mgr.vwaps['session'].vwap_value
            if position.direction == 'LONG' and current_price >= vwap:
                return {'reason': 'VWAP_REACHED', 'price': current_price}
            elif position.direction == 'SHORT' and current_price <= vwap:
                return {'reason': 'VWAP_REACHED', 'price': current_price}
        
        # Exit 4: Delta flip against position
        recent_delta = self.delta_calc.get_cumulative_delta(lookback=5)
        if position.direction == 'LONG' and recent_delta < -position.entry_delta * 0.5:
            return {'reason': 'DELTA_FLIP', 'price': current_price}
        elif position.direction == 'SHORT' and recent_delta > -position.entry_delta * 0.5:
            return {'reason': 'DELTA_FLIP', 'price': current_price}
        
        return None
```

---

## 14. References

### Academic Papers

1. **Hasbrouck, J.** (2007). *Empirical Market Microstructure*. Oxford University Press. — Foundational text on trade classification and market microstructure measurement.

2. **Lee, C. M. C., & Ready, M. J.** (1991). "Inferring Trade Direction from Intraday Data." *Journal of Finance*. — The Lee-Ready algorithm for trade classification.

3. **Easley, D., Lopez de Prado, M. M., & O'Hara, M.** (2012). "Flow Toxicity and Liquidity in a High-Frequency World." *Review of Financial Studies*. — Volume classification and VPIN.

4. **Bouchaud, J. P., Farmer, J. D., & Lillo, F.** (2009). "How Markets Slowly Digest Changes in Supply and Demand." *Handbook of Financial Markets*. — Price impact of order flow.

5. **Cont, R., Kukanov, A., & Stoikov, S.** (2014). "The Price Impact of Order Book Events." *Journal of Financial Econometrics*. — Order flow imbalance and price prediction.

6. **Kyle, A. S.** (1985). "Continuous Auctions and Insider Trading." *Econometrica*. — Lambda (price impact coefficient).

7. **Madhavan, A.** (2000). "Market Microstructure: A Survey." *Journal of Financial Markets*. — Comprehensive review of market microstructure.

### Practitioner & Methodology

8. **Dalton, J. F., Jones, E. T., & Dalton, R. B.** (1993). *Mind Over Markets*. — Market Profile: POC, Value Area, market types.

9. **Steidlmayer, J. P.** (1986). *Steidlmayer on Markets*. — Original Market Profile creator; TPO and volume distribution concepts.

10. **ICT (Inner Circle Trader)** — Volume analysis within the context of institutional order flow, kill zones, and smart money concepts.

11. **Sierra Chart Documentation** — Detailed technical documentation on volume delta, cumulative delta, footprint charts, and order flow analysis.

12. **Jigsaw Trading** — Practical education on delta, absorption, and order flow trading.

13. **Exocharts / ATAS / Quantower** — Platform-specific documentation on volume profile, delta, and VWAP implementations.

### Data & Implementation

14. **Binance API Documentation** — WebSocket streams for trade data with buyer/seller classification (aggressor flag).

15. **CME Group** — "CME DataMine" documentation for historical tick data with trade classification.

16. **Tardis.dev** — Historical crypto market data with L2 order book and trade data.

---

> **Previous Document**: [03_hft_stop_hunting.md](./03_hft_stop_hunting.md) — HFT algorithms and institutional stop hunting
> **Next Document**: [05_execution_flow.md](./05_execution_flow.md) — Complete execution flow for order flow trading system
