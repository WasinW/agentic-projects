# Wyckoff Distribution Schematic — Complete Analysis

> **Module**: Axis 1 — Trading Strategies
> **Topic**: 02 — Wyckoff Method & Market Structure
> **File**: 02_distribution_schematic.md
> **Version**: 1.0
> **Last Updated**: 2026-04-12
> **Author**: NTT Multi-Agent AI Trading System — Knowledge Base Team

---

## Table of Contents

1. [Introduction to Distribution](#1-introduction-to-distribution)
2. [Distribution Schematic #1 — Standard](#2-distribution-schematic-1--standard)
3. [Distribution Schematic #2 — With UTAD](#3-distribution-schematic-2--with-utad)
4. [Detailed Phase Analysis](#4-detailed-phase-analysis)
5. [Volume Patterns During Distribution](#5-volume-patterns-during-distribution)
6. [Distribution vs Re-Accumulation](#6-distribution-vs-re-accumulation)
7. [Mathematical Models](#7-mathematical-models)
8. [Entry/Exit Logic for Short Trades](#8-entryexit-logic-for-short-trades)
9. [Risk Management During Distribution](#9-risk-management-during-distribution)
10. [Execution Flow](#10-execution-flow)
11. [Forex-Specific Distribution](#11-forex-specific-distribution)
12. [Crypto-Specific Distribution](#12-crypto-specific-distribution)
13. [Common Mistakes](#13-common-mistakes)
14. [References](#14-references)

---

## 1. Introduction to Distribution

### 1.1 Definition

Distribution is the third phase of the Wyckoff market cycle. It represents a **sideways trading range** that forms at the top of an uptrend, during which the Composite Man (CM) systematically distributes (sells) a previously accumulated position at premium prices to uninformed buyers (retail traders attracted by bullish sentiment).

### 1.2 Mirror Relationship to Accumulation

Distribution is the mirror image of accumulation, but with critical asymmetric differences:

| Aspect | Accumulation | Distribution |
|---|---|---|
| Location | Bottom of downtrend | Top of uptrend |
| CM action | Buying (absorbing supply) | Selling (distributing supply) |
| Retail sentiment | Fear, capitulation | Euphoria, FOMO, greed |
| Volume profile | SC = extreme sell volume | BC = extreme buy volume |
| Key shakeout | Spring (false breakdown) | UTAD (false breakout) |
| Confirmation | SOS (strength rally) | SOW (weakness drop) |
| Typical duration | Often longer | Often shorter (greed is impatient) |
| Speed of resolution | Gradual markup | Often sharp markdown |

### 1.3 Why Distribution is Faster and More Violent

Market psychology creates an asymmetry:
- **Accumulation** is slow because fear lingers; sellers must be gradually exhausted
- **Distribution** can be faster because greed attracts eager buyers quickly; once distribution is complete, the absence of demand causes rapid price collapse

$$
\frac{T_{\text{distribution}}}{T_{\text{accumulation}}} \approx 0.6 \text{ to } 0.8
$$

And the resulting markdown is typically steeper than the markup:

$$
\frac{|\text{Rate}_{\text{markdown}}|}{|\text{Rate}_{\text{markup}}|} \approx 1.5 \text{ to } 3.0
$$

### 1.4 Composite Man Behavior During Distribution

```
Composite Man Distribution Playbook:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: CREATE EUPHORIA
  ├── Allow price to make new highs (Buying Climax)
  ├── Media narratives turn maximum bullish
  ├── Retail FOMO attracts new buyers
  └── CM begins selling INTO the strength

Step 2: ABSORB DEMAND
  ├── Price moves sideways despite bullish news
  ├── Each rally to resistance finds CM selling
  ├── Volume on rallies shows distribution (high vol, poor close)
  └── Demand is progressively absorbed by CM supply

Step 3: TRAP BUYERS (UTAD)
  ├── False breakout above range resistance
  ├── Triggers breakout buyers (new demand for CM to sell into)
  ├── Media reports "new all-time high" / "breakout"
  └── CM sells final inventory to breakout buyers

Step 4: CONFIRM WEAKNESS
  ├── Price drops below range support (SOW)
  ├── Last rally attempts fail at lower levels (LPSY)
  ├── Volume confirms supply > demand
  └── Markdown begins

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 2. Distribution Schematic #1 — Standard

### 2.1 ASCII Schematic

```
             Distribution Schematic #1 (Standard — No UTAD)
                    
Price
  │                                                    
  │    ──────────────────────────────────────────── Ice (Resistance)
  │         PSY   BC         ST        ST   LPSY
  │          │   ╱  ╲       ╱╲        ╱╲    ╱╲
  │          ↑  ╱    ╲     ╱  ╲      ╱  ╲  ╱  ╲
  │         ╱  ╱      ╲   ╱    ╲    ╱    ╲╱    ╲
  │        ╱  ╱        ╲ ╱      ╲  ╱              ╲
  │       ╱  ╱    AR    ╲╱       ╲╱       SOW      ╲
  │      ╱  ╱    ╱ ╲         ╱                      ╲
  │     ╱  ╱────╱───╲───────╱─────────────────────── Creek (Support)
  │    ╱       ╱     ╲     ╱
  │   ╱  Markup       ╲   ╱
  │  ╱                  ╲ ╱
  │ ╱                    ╲  ← SOW breaks below Creek
  │╱                      ╲
  │                        ╲
  │                         ╲  Markdown begins
  │                          ╲
  │                           ╲
  │
  │  Prior   │Phase A│    Phase B              │Phase C│ Phase D │Phase E
  │  Markup  │(Stop) │    (Building Cause)     │(Test) │(Trend)  │(Markdown)
  │          │       │                         │       │         │
  └──────────┴───────┴─────────────────────────┴───────┴─────────┴──→ Time
  
  Volume:
  ███   ████   ███    ██    █    ██   █    ███   ████   ██    ███
  HIGH  V.HIGH HIGH   MED  LOW  MED  LOW  HIGH  V.HIGH LOW   HIGH
  (PSY) (BC)   (AR)  (STs)           (STs)(SOW) (SOW) (LPSY) (Break)
```

### 2.2 Key Events Summary

| Event | Abbreviation | Phase | Description |
|---|---|---|---|
| Preliminary Supply | PSY | A | First significant selling after uptrend |
| Buying Climax | BC | A | Climactic buying with extreme volume, reversal |
| Automatic Reaction | AR | A | Sharp selloff from BC, defines support (Creek) |
| Secondary Test | ST | B | Retest of BC area on lower volume |
| Upthrust After Distribution | UTAD | C | False breakout above BC (optional) |
| Sign of Weakness | SOW | D | Breakdown below Creek on volume |
| Last Point of Supply | LPSY | D | Final rally on low volume (entry point) |

---

## 3. Distribution Schematic #2 — With UTAD

### 3.1 ASCII Schematic

```
             Distribution Schematic #2 (With UTAD — Most Common)
                    
Price
  │                              UTAD
  │                             ╱    ╲
  │                            ╱      ╲  ← False breakout above BC
  │    ─────────────────────╱╱────────╲╲──────────────── Ice (Resistance)
  │         PSY   BC       ╱     ST     ╲   LPSY  LPSY
  │          │   ╱  ╲     ╱     ╱╲      ╲  ╱╲    ╱╲
  │          ↑  ╱    ╲   ╱     ╱  ╲      ╲╱  ╲  ╱  ╲
  │         ╱  ╱      ╲ ╱     ╱    ╲          ╲╱    ╲
  │        ╱  ╱        ╳     ╱      ╲    SOW          ╲
  │       ╱  ╱    AR  ╱ ╲   ╱        ╲  ╱              ╲
  │      ╱  ╱    ╱ ╲ ╱   ╲ ╱          ╲╱                ╲
  │     ╱  ╱────╱───╳─────╲╱───────────╲──────────────── Creek (Support)
  │    ╱       ╱            ╲           │╲
  │   ╱  Markup              ╲          │ ╲
  │  ╱                        ╲         │  ╲
  │ ╱                          ╲  SOW breaks below Creek
  │╱                            ╲       │    ╲
  │                              ╲      │     ╲
  │                               ╲     │      ╲ Markdown
  │                                     │
  │                                     │
  │  Prior   │Phase A│    Phase B       │Phase C│ Phase D  │ Phase E
  │  Markup  │(Stop) │   (Bldg Cause)  │(Test) │(Markdown)│
  │          │       │                  │(UTAD) │  Within  │
  └──────────┴───────┴──────────────────┴───────┴──────────┴──→ Time
  
  Volume at UTAD:
  ████ ← High volume on breakout attempt (CM selling into breakout buyers)
  Then rapid volume decline as price reverses (buyers trapped)
```

### 3.2 UTAD Classification

| Type | Depth Above BC | Volume | Speed of Reversal | Trap Quality |
|---|---|---|---|---|
| Type 1 (Weak) | > 3% above | Very high | Slow (5+ bars) | Low — may be genuine breakout |
| Type 2 (Moderate) | 1–3% above | High | Moderate (2–4 bars) | Moderate |
| Type 3 (Best) | < 1% above | Moderate | Fast (1–2 bars) | High — immediate trap and reversal |

---

## 4. Detailed Phase Analysis

### 4.1 Phase A — Stopping the Uptrend

#### 4.1.1 Preliminary Supply (PSY)

**Definition**: The first significant selling pressure that appears after an extended rally. Indicates that supply is beginning to overcome demand at these elevated prices.

**Characteristics:**

| Attribute | Description |
|---|---|
| **Price Action** | Wide-spread bar that closes in the middle or lower portion during uptrend |
| **Volume** | Notably increased — selling into strength |
| **Context** | Occurs after extended uptrend |
| **Close Position** | Closes in middle-to-lower third despite opening higher |
| **Significance** | First warning that uptrend may be exhausting |

```python
def detect_preliminary_supply(candles, i, avg_volume, atr, trend):
    """
    Detect Preliminary Supply (PSY) event.
    """
    if trend != 'UP':
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    conditions = {
        'uptrend': trend == 'UP',
        'increased_volume': c['volume'] > avg_volume * 1.5,
        'wide_spread': spread > atr * 0.8,
        'close_not_at_high': close_position < 0.65,
        'upper_wick': (c['high'] - max(c['open'], c['close'])) > spread * 0.3,
        'prior_rally': candles[i]['close'] > candles[max(0, i-20)]['close'],
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'PSY',
            'phase': 'A',
            'index': i,
            'price': c['close'],
            'price_high': c['high'],
            'volume_ratio': c['volume'] / avg_volume,
            'close_position': close_position,
            'confidence': sum(conditions.values()) / len(conditions),
        }
    return None
```

#### 4.1.2 Buying Climax (BC)

**Definition**: The climactic buying event that establishes the upper boundary of the distribution range. Characterized by extreme volume, wide price spread, often closing near highs but followed immediately by reversal.

**Characteristics:**

| Attribute | Description |
|---|---|
| **Price Action** | Extreme wide-spread up bar, often making new highs |
| **Volume** | Highest volume in the uptrend — often 3-5x average |
| **Close Position** | Initially near highs, then reversal bar closes lower |
| **Context** | Peak euphoria — media extremely bullish |
| **Reversal** | Sharp downward reversal follows (1–3 bars) |
| **Significance** | Defines the top of the trading range (Ice level) |

**Buying Climax Intensity Index:**

$$
\text{BCI} = \frac{V(t)}{\bar{V}_{50}} \times \frac{\text{Spread}(t)}{ATR_{14}} \times \text{CPos}(t)
$$

Where:
- BCI < 3.0: Weak climax — may not define the top
- BCI 3.0–6.0: Moderate climax
- BCI > 6.0: Strong climax — high probability distribution begins

```python
def detect_buying_climax(candles, i, avg_volume_20, avg_volume_50, atr, psy_event):
    """
    Detect Buying Climax (BC) event.
    """
    if psy_event is None:
        return None
    
    if i - psy_event['index'] > 30:
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    # BC should be making new highs
    is_new_high = c['high'] >= max(cc['high'] for cc in candles[max(0, i-50):i])
    
    conditions = {
        'extreme_volume': c['volume'] > avg_volume_20 * 2.5,
        'wide_spread': spread > atr * 1.3,
        'new_high_area': is_new_high or c['high'] >= candles[i-1]['high'],
        'psy_exists': psy_event is not None,
        'climactic_close': close_position > 0.5,  # Initially closes high
    }
    
    # Check for reversal on next bar(s)
    reversal_detected = False
    if i + 1 < len(candles):
        next_bar = candles[i + 1]
        if next_bar['close'] < next_bar['open'] and next_bar['close'] < c['close']:
            reversal_detected = True
    conditions['reversal_hint'] = reversal_detected or close_position < 0.6
    
    # BCI calculation
    bci = (c['volume'] / avg_volume_50) * (spread / atr) * close_position
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'BC',
            'phase': 'A',
            'index': i,
            'price_high': c['high'],
            'price_close': c['close'],
            'volume_ratio': c['volume'] / avg_volume_20,
            'spread_ratio': spread / atr,
            'close_position': close_position,
            'bci': bci,
            'confidence': sum(conditions.values()) / len(conditions),
            'range_top': c['high'],  # Defines Ice level
        }
    return None
```

#### 4.1.3 Automatic Reaction (AR)

**Definition**: The sharp selloff that immediately follows the Buying Climax. It represents the automatic response as profit-taking and short sellers enter. The AR defines the lower boundary of the distribution range (Creek/Support).

**Characteristics:**

| Attribute | Description |
|---|---|
| **Price Action** | Sharp decline with bearish bars |
| **Volume** | Moderate-to-high, decreasing from BC levels |
| **Duration** | Short — typically 3–10 bars |
| **Retracement** | Typically 30–60% of the final rally leg |
| **Significance** | Defines the Creek (support) of the range |

```python
def detect_automatic_reaction(candles, i, bc_event, avg_volume, atr):
    """
    Detect Automatic Reaction (AR) — selloff after BC.
    AR is detected at the swing low following BC.
    """
    if bc_event is None:
        return None
    
    bc_idx = bc_event['index']
    if i - bc_idx > 15 or i - bc_idx < 2:
        return None
    
    current_low = candles[i]['low']
    
    # AR is the first significant swing low after BC
    is_swing_low = current_low <= min(c['low'] for c in candles[bc_idx:i+1])
    
    # Check if price is starting to bounce
    if i + 1 < len(candles):
        bouncing = candles[i+1]['close'] > candles[i]['close']
    else:
        bouncing = candles[i]['close'] > candles[i]['low'] + (candles[i]['high'] - candles[i]['low']) * 0.3
    
    bc_high = bc_event['price_high']
    decline_size = bc_high - current_low
    
    # Calculate retracement of the rally that led to BC
    pre_bc_low = min(c['low'] for c in candles[max(0, bc_idx-20):bc_idx])
    rally_size = bc_high - pre_bc_low
    retracement = decline_size / rally_size if rally_size > 0 else 0
    
    conditions = {
        'follows_bc': (i - bc_idx) >= 2 and (i - bc_idx) <= 15,
        'is_swing_low': is_swing_low,
        'significant_decline': decline_size > atr * 1.5,
        'minimum_retracement': retracement >= 0.25,
        'price_bouncing': bouncing,
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'AR',
            'phase': 'A',
            'index': i,
            'price_low': current_low,
            'decline_size': decline_size,
            'retracement_pct': retracement,
            'confidence': sum(conditions.values()) / len(conditions),
            'range_bottom': current_low,  # Defines Creek level
        }
    return None
```

### 4.2 Phase B — Building the Cause (Distribution)

Phase B is the longest phase where CM distributes inventory. Price oscillates between Ice (BC high) and Creek (AR low).

#### 4.2.1 Secondary Tests (ST) in Distribution

**Definition**: Retests of the BC area on diminished buying volume, confirming that demand is weakening at these levels.

```python
def detect_distribution_st(candles, i, bc_event, ar_event, avg_volume, atr):
    """
    Detect Secondary Test (ST) of the Buying Climax area.
    """
    if bc_event is None or ar_event is None:
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    bc_high = bc_event['price_high']
    range_height = bc_high - ar_event['price_low']
    
    # ST should be near BC high (within 15% of range from top)
    proximity_to_bc = (bc_high - c['high']) / range_height if range_height > 0 else 1.0
    
    conditions = {
        'near_bc_level': abs(proximity_to_bc) < 0.15,
        'lower_volume': c['volume'] < bc_event['volume_ratio'] * avg_volume * 0.7,
        'narrower_spread': spread < bc_event['spread_ratio'] * atr * 0.8,
        'holds_below_bc': c['high'] <= bc_high + atr * 0.3,
        'after_ar': i > ar_event['index'],
        'bearish_or_neutral_close': close_position < 0.7,
    }
    
    # Quality score
    vol_ratio = (bc_event['volume_ratio'] * avg_volume) / c['volume'] if c['volume'] > 0 else 0
    quality = vol_ratio * (1 - proximity_to_bc)
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'ST',
            'phase': 'B',
            'index': i,
            'price_high': c['high'],
            'quality': quality,
            'volume_vs_bc': c['volume'] / (bc_event['volume_ratio'] * avg_volume),
            'proximity_to_bc': proximity_to_bc,
            'confidence': sum(conditions.values()) / len(conditions),
            'interpretation': 'STRONG' if quality > 3.0 else 'MODERATE' if quality > 1.5 else 'WEAK',
        }
    return None
```

#### 4.2.2 Phase B Volume Pattern

```
Phase B — Demand Absorption Pattern (Distribution)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Price   BC/Ice ─────────────────────────────────── Resistance
                ╲     ╱╲        ╱╲       ╱╲
                 ╲   ╱  ╲      ╱  ╲     ╱  ╲╱╲
                  ╲ ╱    ╲    ╱    ╲   ╱       ╲
                   ╲      ╲  ╱      ╲ ╱         ╲
        AR/Creek ───╲──────╲╱────────╲╱──────────╲── Support
                     ╲      ╳
                      ╲    ╱ (possible test below support)
                       ╲  ╱
                      SOW emerging

Volume on RALLIES:  ████  ███   ███   ██    ██   █     ← DECREASING
Volume on DECLINES: ██    ██    ███   ███   ████ ████  ← INCREASING

Key: Effort increasing on DOWN moves, decreasing on UP moves
     = Supply overwhelming demand = DISTRIBUTION CONFIRMED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.3 Phase C — The UTAD (Upthrust After Distribution)

#### 4.3.1 Upthrust After Distribution (UTAD)

**Definition**: A false breakout above the trading range resistance (BC/Ice level) that quickly reverses. The CM pushes price above resistance to trigger buy stops, attract breakout traders, and sell the final inventory at the highest possible prices.

**Characteristics:**

| Attribute | Description |
|---|---|
| **Price Action** | Brief penetration above Ice resistance, followed by rapid reversal |
| **Volume** | Variable — best UTADs show high volume (selling INTO buying) |
| **Duration** | 1–5 bars above resistance before reversal |
| **Depth** | Typically 0.5–3% above Ice level |
| **Purpose** | Trap breakout buyers, allow CM to sell final inventory |
| **Significance** | Highest probability short entry point in distribution |

**UTAD Quality Score:**

$$
\text{UTAD\_Quality} = \frac{V_{\text{UTAD\_bar}}}{\bar{V}_{20}} \times (1 - \text{CPos}_{\text{reversal}}) \times \frac{1}{\text{Depth}^{0.5}}
$$

```python
def detect_utad(candles, i, range_resistance, range_support, avg_volume, atr, st_events):
    """
    Detect Upthrust After Distribution (UTAD) — false breakout above resistance.
    """
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    # Must penetrate above resistance
    if c['high'] <= range_resistance:
        return None
    
    depth = c['high'] - range_resistance
    depth_atr = depth / atr
    
    # Close must show reversal (close back below or near resistance)
    close_below_resistance = c['close'] <= range_resistance
    close_near_resistance = c['close'] <= range_resistance + atr * 0.2
    
    # Classify UTAD type
    if depth_atr < 0.5 and c['volume'] <= avg_volume * 1.5:
        utad_type = 3  # Best — subtle trap
        base_confidence = 0.85
    elif depth_atr < 1.5:
        utad_type = 2  # Moderate
        base_confidence = 0.70
    elif depth_atr < 3.0:
        utad_type = 1  # Deep — might be genuine breakout
        base_confidence = 0.50
    else:
        return None  # Too deep — likely genuine breakout
    
    # Check demand decreasing on prior rallies
    demand_weakening = True
    rally_volumes = [e.get('volume_vs_bc', 1.0) for e in st_events if e.get('event') == 'ST']
    if len(rally_volumes) >= 2:
        demand_weakening = rally_volumes[-1] <= rally_volumes[-2]
    
    conditions = {
        'penetrates_resistance': c['high'] > range_resistance,
        'limited_depth': depth_atr < 2.5,
        'reversal_close': close_below_resistance or close_near_resistance,
        'bearish_close_position': close_position < 0.5,
        'demand_weakening': demand_weakening,
        'volume_present': c['volume'] > avg_volume * 0.8,
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'UTAD',
            'phase': 'C',
            'index': i,
            'utad_type': utad_type,
            'price_high': c['high'],
            'price_close': c['close'],
            'depth': depth,
            'depth_atr': depth_atr,
            'volume_ratio': c['volume'] / avg_volume,
            'close_below_resistance': close_below_resistance,
            'confidence': base_confidence * (sum(conditions.values()) / len(conditions)),
            'trade_action': {
                3: 'AGGRESSIVE_SHORT',
                2: 'SHORT_ON_TEST',
                1: 'WAIT_FOR_CONFIRMATION'
            }[utad_type],
            'stop_loss': c['high'] + atr * 0.5,
        }
    return None
```

#### 4.3.2 Test of UTAD

**Definition**: After the UTAD reversal, price may rally back toward the UTAD high to confirm that supply overwhelms demand at these levels. The test should show lower volume and fail to reach the UTAD high.

```python
def detect_test_of_utad(candles, i, utad_event, avg_volume, atr):
    """
    Detect the Test after a UTAD event — highest conviction short entry.
    """
    if utad_event is None:
        return None
    
    bars_since_utad = i - utad_event['index']
    if bars_since_utad < 2 or bars_since_utad > 15:
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    utad_high = utad_event['price_high']
    proximity = abs(c['high'] - utad_high) / atr
    
    conditions = {
        'near_utad_area': proximity < 1.5,
        'lower_high': c['high'] < utad_high,
        'lower_volume': c['volume'] < utad_event['volume_ratio'] * avg_volume * 0.8,
        'bearish_close': close_position < 0.4,
        'narrower_spread': spread < atr * 1.0,
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'TEST_OF_UTAD',
            'phase': 'C',
            'index': i,
            'price_high': c['high'],
            'price_close': c['close'],
            'distance_from_utad': utad_high - c['high'],
            'volume_vs_utad': c['volume'] / (utad_event['volume_ratio'] * avg_volume),
            'confidence': 0.88 * (sum(conditions.values()) / len(conditions)),
            'trade_action': 'STRONG_SHORT',
            'stop_loss': utad_high + atr * 0.3,
        }
    return None
```

### 4.4 Phase D — Markdown Within the Range

#### 4.4.1 Sign of Weakness (SOW)

**Definition**: A strong decline on increased volume that breaks below the Creek (support). This confirms distribution is complete and markdown is beginning.

**Characteristics:**

| Attribute | Description |
|---|---|
| **Price Action** | Strong bearish move breaking below AR low/Creek support |
| **Volume** | Significantly increased — confirms supply dominance |
| **Spread** | Wide bearish bars |
| **Close** | Near lows of the bars |
| **Significance** | Confirms transition from Distribution to Markdown |

```python
def detect_sign_of_weakness(candles, i, creek_level, avg_volume, atr, range_height):
    """
    Detect Sign of Weakness (SOW) — breakdown below Creek.
    """
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    # Must close below Creek
    if c['close'] >= creek_level:
        return None
    
    breakdown_distance = creek_level - c['close']
    breakdown_atr = breakdown_distance / atr
    
    conditions = {
        'closes_below_creek': c['close'] < creek_level,
        'significant_breakdown': breakdown_atr > 0.3,
        'strong_volume': c['volume'] > avg_volume * 1.5,
        'wide_spread': spread > atr * 0.8,
        'bearish_close': close_position < 0.4,
        'body_below_creek': (c['open'] + c['close']) / 2 < creek_level,
    }
    
    strength = (c['volume'] / avg_volume) * (spread / atr) * (1 - close_position)
    strength *= breakdown_distance / range_height if range_height > 0 else 0
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'SOW',
            'phase': 'D',
            'index': i,
            'price_close': c['close'],
            'price_low': c['low'],
            'breakdown_distance': breakdown_distance,
            'strength': strength,
            'volume_ratio': c['volume'] / avg_volume,
            'confidence': sum(conditions.values()) / len(conditions),
        }
    return None
```

#### 4.4.2 Last Point of Supply (LPSY)

**Definition**: After the SOW, price may rally back toward the Creek (which now acts as resistance). This rally should be weak — on low volume with narrow spread — and represents the last opportunity to sell/short before sustained markdown.

**Characteristics:**

| Attribute | Description |
|---|---|
| **Price Action** | Weak rally toward Creek, failing at or below it |
| **Volume** | Low — significantly lower than SOW volume |
| **Spread** | Narrow — bars getting smaller |
| **Close** | Should close below or at Creek level |
| **Significance** | Best short entry after SOW confirmation |
| **Multiple LPSYs** | May occur several times, each at a lower level |

```python
def detect_last_point_of_supply(candles, i, sow_event, creek_level, avg_volume, atr):
    """
    Detect Last Point of Supply (LPSY) — weak rally after SOW.
    """
    if sow_event is None:
        return None
    
    bars_since_sow = i - sow_event['index']
    if bars_since_sow < 2 or bars_since_sow > 25:
        return None
    
    c = candles[i]
    spread = c['high'] - c['low']
    close_position = (c['close'] - c['low']) / spread if spread > 0 else 0.5
    
    # LPSY should be near Creek but failing to break above
    proximity_to_creek = abs(c['high'] - creek_level) / atr
    
    conditions = {
        'near_creek': proximity_to_creek < 1.5,
        'fails_at_creek': c['high'] <= creek_level + atr * 0.2,
        'declining_volume': c['volume'] < sow_event['volume_ratio'] * avg_volume * 0.5,
        'narrow_spread': spread < atr * 0.8,
        'bearish_close': close_position < 0.5,
        'rally_from_sow': c['high'] > sow_event['price_low'],
    }
    
    if sum(conditions.values()) >= 4:
        return {
            'event': 'LPSY',
            'phase': 'D',
            'index': i,
            'price_high': c['high'],
            'price_close': c['close'],
            'distance_from_creek': creek_level - c['high'],
            'volume_ratio': c['volume'] / avg_volume,
            'confidence': 0.82 * (sum(conditions.values()) / len(conditions)),
            'trade_action': 'SHORT',
            'stop_loss': creek_level + atr * 0.5,
        }
    return None
```

---

## 5. Volume Patterns During Distribution

### 5.1 Volume Signature Table

| Event | Expected Volume | vs 20-SMA | Spread | Close Position | Interpretation |
|---|---|---|---|---|---|
| PSY | Increased | 1.5–2.5x | Wide | Low-Mid | First supply appearance |
| BC | Extreme | 2.5–5.0x | Very Wide | Mid-High (then reversal) | Euphoric buying, CM selling |
| AR | Moderate-High | 1.0–2.0x | Wide | Lower | Profit-taking + short selling |
| ST | Decreased vs BC | 0.5–0.8x | Narrower | Below BC | Demand weakening |
| Phase B rallies | Decreasing | 0.3–0.7x vs BC | Narrowing | Variable | Progressive distribution |
| UTAD | High (selling) | 1.5–3.0x | Moderate-Wide | Below resistance (reversal) | Trap — CM selling to breakout buyers |
| Test of UTAD | Low | 0.3–0.6x | Narrow | Lower | Demand confirmed exhausted |
| SOW | High | 1.5–3.0x | Wide | Near low | Supply overwhelms demand |
| LPSY | Low | 0.3–0.6x | Narrow | Below mid | No demand at higher levels |

### 5.2 Critical Volume Divergence in Distribution

The key volume signature of distribution:

$$
\frac{V_{\text{rallies}}(t)}{V_{\text{declines}}(t)} \rightarrow 0 \quad \text{as} \quad t \rightarrow t_{\text{breakdown}}
$$

In words: **Volume on rallies decreases while volume on declines increases** throughout distribution.

### 5.3 Demand Exhaustion Index (DEI)

Mirror of Supply Exhaustion Index for accumulation:

$$
\text{DEI}(t) = \frac{\sum_{i=t_0}^{t} V_{\text{up}}(i) \cdot |\Delta P_{\text{up}}(i)|}{\sum_{i=t_0}^{t} V_{\text{down}}(i) \cdot |\Delta P_{\text{down}}(i)|}
$$

**Interpretation:**
- DEI > 2.0 at start of range (heavy demand from prior uptrend)
- DEI declining toward 1.0 (demand being absorbed by CM supply)
- DEI < 0.5 near end (demand exhausted — breakdown imminent)

---

## 6. Distribution vs Re-Accumulation

### 6.1 The Critical Distinction

One of the most important and difficult distinctions in Wyckoff analysis is determining whether a trading range at the top of an uptrend represents **distribution** (will break down) or **re-accumulation** (will break up — a "stepping stone" to higher prices).

### 6.2 Key Differentiators

| Feature | Distribution | Re-Accumulation |
|---|---|---|
| **Volume on rallies** | Decreasing over time | Steady or increasing |
| **Volume on declines** | Increasing over time | Decreasing |
| **UTAD behavior** | Rapid reversal, trapped buyers | Shallow or absent |
| **Close positions on rallies** | Deteriorating (closing lower within bars) | Strong (closing at highs) |
| **Response to support** | Weak bounces, breaking on volume | Strong bounces, holding |
| **Trend before range** | Extended uptrend (exhaustion likely) | Moderate uptrend (continuation likely) |
| **Range duration** | Shorter (1/3 to 2/3 of prior markup) | Longer relative to pause |
| **SOW behavior** | Breaks support on high volume | Support holds, fake breaks recover |
| **Broader context** | HTF resistance, extended cycle | HTF mid-trend, pullback |

### 6.3 Distribution vs Re-Accumulation Scoring Model

$$
P(\text{Distribution}) = \sigma\left(\sum_{k=1}^{n} w_k \cdot f_k(\mathbf{x})\right)
$$

| Factor ($f_k$) | Weight ($w_k$) | Favors Distribution When |
|---|---|---|
| Volume on rallies declining | 2.0 | $V_{\text{rally\_slope}} < -0.1$ |
| Volume on declines increasing | 2.0 | $V_{\text{decline\_slope}} > 0.1$ |
| Close positions on rallies | 1.5 | Average CPos on rallies < 0.5 |
| Prior uptrend duration | 1.0 | > 2x the range duration |
| UTAD present with reversal | 2.5 | UTAD detected and failed |
| SOW breaks support | 3.0 | SOW confirmed below Creek |
| HTF at resistance | 1.5 | Price at weekly/monthly resistance |
| Sentiment extreme | 1.0 | Extreme bullish readings |

```python
def distribution_vs_reaccumulation(range_data, htf_context):
    """
    Score whether a trading range is distribution or re-accumulation.
    
    Returns:
        float: probability of distribution [0, 1]
    """
    features = {}
    
    # Feature 1: Volume on rallies trend
    rally_vols = range_data['rally_volumes']
    if len(rally_vols) >= 3:
        slope = np.polyfit(range(len(rally_vols)), rally_vols, 1)[0]
        features['rally_vol_declining'] = max(0, -slope / np.mean(rally_vols))
    else:
        features['rally_vol_declining'] = 0.5
    
    # Feature 2: Volume on declines trend
    decline_vols = range_data['decline_volumes']
    if len(decline_vols) >= 3:
        slope = np.polyfit(range(len(decline_vols)), decline_vols, 1)[0]
        features['decline_vol_increasing'] = max(0, slope / np.mean(decline_vols))
    else:
        features['decline_vol_increasing'] = 0.5
    
    # Feature 3: Close positions on rallies
    rally_cpos = range_data['rally_close_positions']
    features['weak_rally_closes'] = max(0, 1 - np.mean(rally_cpos) * 2) if rally_cpos else 0.5
    
    # Feature 4: Prior uptrend exhaustion
    prior_trend_duration = range_data['prior_uptrend_bars']
    range_duration = range_data['range_bars']
    features['trend_exhausted'] = min(1.0, prior_trend_duration / (range_duration * 3))
    
    # Feature 5: UTAD present
    features['utad_present'] = 1.0 if range_data.get('utad_event') else 0.0
    
    # Feature 6: SOW confirmed
    features['sow_confirmed'] = 1.0 if range_data.get('sow_event') else 0.0
    
    # Feature 7: HTF resistance
    features['htf_resistance'] = 1.0 if htf_context.get('at_htf_resistance') else 0.0
    
    # Weighted sum
    weights = {
        'rally_vol_declining': 2.0,
        'decline_vol_increasing': 2.0,
        'weak_rally_closes': 1.5,
        'trend_exhausted': 1.0,
        'utad_present': 2.5,
        'sow_confirmed': 3.0,
        'htf_resistance': 1.5,
    }
    
    z = sum(weights[k] * features[k] for k in features)
    z_normalized = (z - 6.0) / 3.0  # Center around decision boundary
    
    probability = 1.0 / (1.0 + np.exp(-z_normalized))
    
    return {
        'probability_distribution': probability,
        'probability_reaccumulation': 1 - probability,
        'features': features,
        'recommendation': 'DISTRIBUTION' if probability > 0.65 else \
                         'RE_ACCUMULATION' if probability < 0.35 else 'UNCERTAIN'
    }
```

### 6.4 Decision Matrix

| P(Distribution) | Action | Notes |
|---|---|---|
| > 0.80 | Active short positioning | High confidence distribution |
| 0.65–0.80 | Cautious short, tight stops | Lean bearish but manage risk |
| 0.35–0.65 | **No position** — wait for clarity | Uncertain — do not trade |
| 0.20–0.35 | Cautious long, expect breakout | Lean bullish re-accumulation |
| < 0.20 | Active long positioning | High confidence re-accumulation |

---

## 7. Mathematical Models

### 7.1 Distribution Range Parameters

$$
\text{Range} = [P_{\text{creek}}, P_{\text{ice}}]
$$

Where:
- $P_{\text{ice}} = P_{\text{BC\_high}} \pm \epsilon$ (resistance level)
- $P_{\text{creek}} = P_{\text{AR\_low}} \pm \epsilon$ (support level)

### 7.2 Price Target Projection (Downside)

**Method 1: Range-Based Projection**

$$
\text{Target}_{\text{down}} = P_{\text{creek}} - k \cdot H_{\text{range}} \cdot \sqrt{\frac{T_{\text{range}}}{T_{\text{ref}}}}
$$

**Method 2: ATR-Based Projection**

$$
\text{Target}_{\text{down}} = P_{\text{creek}} - m \cdot ATR \cdot \sqrt{\frac{T_{\text{dist}}}{20}}
$$

Where $m$:
- Conservative: $m = 2.5$
- Moderate: $m = 4.0$
- Aggressive: $m = 6.0$

**Method 3: Fibonacci Extension**

$$
\text{Target}_{1.0} = P_{\text{creek}} - 1.0 \times H_{\text{range}}
$$
$$
\text{Target}_{1.618} = P_{\text{creek}} - 1.618 \times H_{\text{range}}
$$
$$
\text{Target}_{2.618} = P_{\text{creek}} - 2.618 \times H_{\text{range}}
$$

### 7.3 UTAD Probability Model

$$
P(\text{UTAD} | \text{breakout above}) = \sigma\left(\beta_0 + \beta_1 x_V + \beta_2 x_D + \beta_3 x_T + \beta_4 x_C\right)
$$

Where:
- $x_V$ = volume relative to average (high volume with poor close = likely UTAD)
- $x_D$ = depth above resistance (shallow = more likely UTAD)
- $x_T$ = number of prior failed tests of resistance
- $x_C$ = close position of the breakout bar (closing below resistance = likely UTAD)

### 7.4 Distribution Completion Estimator

$$
\text{Completion}(\%) = \frac{\sum_{k=1}^{n} w_k \cdot \mathbb{1}(E_k \text{ detected})}{\sum_{k=1}^{n} w_k} \times 100
$$

| Event ($E_k$) | Weight ($w_k$) |
|---|---|
| PSY detected | 5 |
| BC detected | 15 |
| AR detected | 10 |
| ST(s) detected with declining vol | 15 |
| UTAD detected (or resistance respected) | 20 |
| SOW detected | 20 |
| LPSY detected | 15 |

---

## 8. Entry/Exit Logic for Short Trades

### 8.1 Entry Points (Ranked by Quality)

#### Entry 1: Test of UTAD (Highest Quality Short)

```python
def entry_test_of_utad(utad_event, test_event, atr, range_height):
    """
    Highest quality short entry — after UTAD confirmed by test.
    """
    entry_price = test_event['price_close']
    stop_loss = utad_event['price_high'] + atr * 0.3
    risk = stop_loss - entry_price
    
    return {
        'entry_type': 'TEST_OF_UTAD',
        'direction': 'SHORT',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'risk': risk,
        'targets': [
            entry_price - range_height * 1.0,
            entry_price - range_height * 1.618,
            entry_price - range_height * 2.618,
        ],
        'risk_reward': [(entry_price - t) / risk for t in [
            entry_price - range_height * 1.0,
            entry_price - range_height * 1.618,
            entry_price - range_height * 2.618,
        ]],
        'position_size_pct': 2.0,
        'confidence': 0.88,
    }
```

#### Entry 2: UTAD Direct (Aggressive Short)

```python
def entry_utad_direct(utad_event, atr, range_height):
    """
    Aggressive short directly on UTAD reversal bar.
    """
    entry_price = utad_event['price_close']
    stop_loss = utad_event['price_high'] + atr * 0.5
    risk = stop_loss - entry_price
    
    return {
        'entry_type': 'UTAD_DIRECT',
        'direction': 'SHORT',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'risk': risk,
        'targets': [
            entry_price - range_height * 0.8,
            entry_price - range_height * 1.5,
            entry_price - range_height * 2.5,
        ],
        'position_size_pct': 1.5,
        'confidence': 0.75,
    }
```

#### Entry 3: LPSY (After SOW Confirmation)

```python
def entry_lpsy(lpsy_event, creek_level, atr, range_height):
    """
    Short on weak rally after SOW — for those who missed UTAD.
    """
    entry_price = lpsy_event['price_close']
    stop_loss = creek_level + atr * 0.5
    risk = stop_loss - entry_price
    
    return {
        'entry_type': 'LPSY',
        'direction': 'SHORT',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'risk': risk,
        'targets': [
            entry_price - range_height * 1.0,
            entry_price - range_height * 2.0,
            entry_price - range_height * 3.0,
        ],
        'position_size_pct': 1.5,
        'confidence': 0.80,
    }
```

#### Entry 4: SOW Break Retest

```python
def entry_sow_retest(sow_event, creek_level, atr, range_height):
    """
    Short on retest of broken Creek (support turned resistance).
    """
    entry_price = creek_level  # Entry at broken support (now resistance)
    stop_loss = creek_level + atr * 0.8
    risk = stop_loss - entry_price
    
    return {
        'entry_type': 'SOW_RETEST',
        'direction': 'SHORT',
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'risk': risk,
        'targets': [
            entry_price - range_height * 1.0,
            entry_price - range_height * 2.0,
        ],
        'position_size_pct': 1.0,
        'confidence': 0.82,
    }
```

### 8.2 Position Scaling for Shorts

```
Short Position Scaling During Distribution:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total planned short position: 100%

Entry 1: UTAD (Direct)          → 25% of total position
Entry 2: Test of UTAD           → 25% of total position (add-on)
Entry 3: SOW break              → 25% of total position (add-on)
Entry 4: LPSY / SOW retest      → 25% of total position (add-on)

Average Entry Price: Weighted average of all entries
Combined Stop Loss: Above UTAD high
Combined R:R: Should be >= 3:1 for the complete position

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 8.3 Exit Logic for Shorts

```python
def distribution_exit_logic(position, candle, market_state, atr):
    """
    Exit logic for short positions entered during distribution.
    """
    exit_signals = []
    
    # Hard stop loss (above UTAD or Creek)
    if candle['high'] >= position['stop_loss']:
        exit_signals.append({
            'type': 'STOP_LOSS',
            'action': 'EXIT_ALL',
            'price': position['stop_loss'],
            'reason': 'Stop loss triggered — potential breakout above resistance'
        })
    
    # Target 1 — partial cover
    if candle['low'] <= position['targets'][0] and not position.get('t1_hit'):
        exit_signals.append({
            'type': 'TARGET_1',
            'action': 'COVER_50PCT',
            'price': position['targets'][0],
            'reason': 'First target reached',
            'move_stop': 'BREAKEVEN'
        })
    
    # Target 2 — additional cover
    if candle['low'] <= position['targets'][1] and not position.get('t2_hit'):
        exit_signals.append({
            'type': 'TARGET_2',
            'action': 'COVER_30PCT',
            'price': position['targets'][1],
            'reason': 'Second target reached',
            'move_stop': position['targets'][0]
        })
    
    # Phase change — accumulation detected at lower level
    if market_state.phase == 'ACCUMULATION':
        exit_signals.append({
            'type': 'PHASE_CHANGE',
            'action': 'COVER_ALL',
            'price': candle['close'],
            'reason': 'Accumulation detected — cover shorts'
        })
    
    # Trailing stop during markdown
    if market_state.phase == 'MARKDOWN' and position.get('t1_hit'):
        trail_stop = candle['low'] + atr * 2.5
        if trail_stop < position['stop_loss']:
            exit_signals.append({
                'type': 'TRAIL_STOP_UPDATE',
                'action': 'UPDATE_STOP',
                'new_stop': trail_stop,
                'reason': 'Trailing stop tightened during markdown'
            })
    
    # Climactic selling at bottom (potential selling climax = accumulation starting)
    if candle['volume'] > market_state.avg_volume * 3.0:
        spread = candle['high'] - candle['low']
        close_pos = (candle['close'] - candle['low']) / spread if spread > 0 else 0.5
        if close_pos > 0.4 and spread > atr * 1.5:
            exit_signals.append({
                'type': 'POTENTIAL_SC',
                'action': 'TIGHTEN_STOP',
                'new_stop': candle['high'] + atr * 0.5,
                'reason': 'Potential Selling Climax — tighten stop, possible accumulation forming'
            })
    
    return exit_signals
```

---

## 9. Risk Management During Distribution

### 9.1 Risk Parameters by Entry Type

| Entry Type | Max Risk (%) | Typical SL (ATR) | Min R:R | Confidence Threshold |
|---|---|---|---|---|
| UTAD (Type 3) | 2.0% | 0.5–1.0 | 4:1 | 0.80 |
| UTAD (Type 2) | 1.5% | 1.0–1.5 | 3:1 | 0.70 |
| UTAD (Type 1) | 0.5% | 1.5–2.5 | 5:1 | 0.60 |
| Test of UTAD | 2.0% | 0.5–1.0 | 3:1 | 0.85 |
| SOW Breakdown | 1.5% | 1.5–2.0 | 2:1 | 0.70 |
| LPSY | 1.5% | 0.5–1.0 | 3:1 | 0.75 |
| SOW Retest | 1.0% | 0.5–0.8 | 3:1 | 0.80 |

### 9.2 Distribution-Specific Risk Factors

| Risk Factor | Impact | Mitigation |
|---|---|---|
| **Short squeeze potential** | Sudden spike against shorts | Always use stop losses; max 3x leverage |
| **Positive funding (crypto)** | Cost of holding short | Factor funding rate into expected return |
| **Bullish news surprise** | Can invalidate distribution | Reduce size before known events |
| **Re-accumulation risk** | Pattern might be stepping stone | Use distribution vs re-accum scoring model |
| **Gap risk (Forex)** | Weekend gaps can exceed stops | Reduce position into weekends |

### 9.3 Dynamic Stop Loss Placement

For short positions during distribution:

$$
SL_{\text{initial}} = P_{\text{UTAD\_high}} + k \cdot ATR
$$

Where $k$:
- Aggressive: $k = 0.3$
- Standard: $k = 0.5$
- Conservative: $k = 1.0$

After confirmation (SOW detected):

$$
SL_{\text{confirmed}} = \min(SL_{\text{initial}}, P_{\text{creek}} + 0.5 \cdot ATR)
$$

---

## 10. Execution Flow

### 10.1 Distribution Detection State Machine

```
Distribution Detection State Machine:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

State 0: WATCHING (prior uptrend, no events)
  │
  ├── Detect PSY → State 1: PSY_DETECTED (10%)
  │
State 1: PSY_DETECTED
  │
  ├── Detect BC → State 2: BC_DETECTED (25%)
  ├── Timeout (30 bars) → State 0
  │
State 2: BC_DETECTED
  │
  ├── Detect AR → State 3: RANGE_FORMING (40%)
  ├── New high above BC on expanding vol → State 0 (continuation)
  │
State 3: RANGE_FORMING
  │
  ├── Detect ST with lower volume → State 4: PHASE_B (55%)
  ├── Sustained breakout above BC → State 0 (continuation)
  │
State 4: PHASE_B
  │
  ├── Multiple STs with weakening demand → State 5: DEMAND_EXHAUSTED (65%)
  ├── Strong breakout above BC on volume → State 0 (breakout)
  │
State 5: DEMAND_EXHAUSTED
  │
  ├── Detect UTAD → State 6: UTAD_DETECTED (80%)
  ├── Detect SOW without UTAD → State 7: SOW_DETECTED (75%)
  │
State 6: UTAD_DETECTED
  │
  ├── Test confirms UTAD → State 8: CONFIRMED_DISTRIBUTION (90%)
  ├── Price sustains above → State 0 (genuine breakout)
  │
State 7: SOW_DETECTED
  │
  ├── LPSY rally fails → State 8: CONFIRMED_DISTRIBUTION (85%)
  ├── Price reclaims Creek with volume → State 4 (not yet)
  │
State 8: CONFIRMED_DISTRIBUTION
  │
  ├── Markdown begins → State 9: MARKDOWN (95%)
  │
State 9: MARKDOWN
  └── Track until accumulation begins at lower levels

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 10.2 Complete Distribution Detection Class

```python
class DistributionDetector:
    """
    Complete state machine for detecting Wyckoff distribution.
    """
    
    def __init__(self, config):
        self.config = config
        self.state = 'WATCHING'
        self.confidence = 0.0
        self.events = []
        self.range_support = None  # Creek
        self.range_resistance = None  # Ice
        
    def update(self, candle, index, avg_volume, atr, trend):
        """Process a new candle and update distribution detection."""
        result = {
            'state': self.state,
            'confidence': self.confidence,
            'new_events': [],
            'signals': [],
        }
        
        if self.state == 'WATCHING':
            psy = detect_preliminary_supply(self.candles, index, avg_volume, atr, trend)
            if psy:
                self.events.append(psy)
                self.state = 'PSY_DETECTED'
                self.confidence = 0.10
                result['new_events'].append(psy)
        
        elif self.state == 'PSY_DETECTED':
            bc = detect_buying_climax(
                self.candles, index, avg_volume, avg_volume,
                atr, self._get_event('PSY')
            )
            if bc:
                self.events.append(bc)
                self.state = 'BC_DETECTED'
                self.confidence = 0.25
                self.range_resistance = bc['range_top']
                result['new_events'].append(bc)
        
        elif self.state == 'BC_DETECTED':
            ar = detect_automatic_reaction(
                self.candles, index, self._get_event('BC'), avg_volume, atr
            )
            if ar:
                self.events.append(ar)
                self.state = 'RANGE_FORMING'
                self.confidence = 0.40
                self.range_support = ar['range_bottom']
                result['new_events'].append(ar)
        
        elif self.state in ['RANGE_FORMING', 'PHASE_B']:
            # Check for ST
            st = detect_distribution_st(
                self.candles, index, self._get_event('BC'),
                self._get_event('AR'), avg_volume, atr
            )
            if st:
                self.events.append(st)
                self.state = 'PHASE_B'
                self.confidence = max(self.confidence, 0.55)
                result['new_events'].append(st)
            
            # Check for UTAD
            utad = detect_utad(
                self.candles, index, self.range_resistance,
                self.range_support, avg_volume, atr,
                [e for e in self.events if e['event'] == 'ST']
            )
            if utad:
                self.events.append(utad)
                self.state = 'UTAD_DETECTED'
                self.confidence = 0.80
                result['new_events'].append(utad)
                if utad['utad_type'] == 3:
                    result['signals'].append({
                        'action': 'SELL',
                        'type': 'UTAD_TYPE3',
                        'entry': candle['close'],
                        'stop_loss': utad['stop_loss'],
                        'confidence': utad['confidence'],
                    })
            
            # Check for SOW
            sow = detect_sign_of_weakness(
                self.candles, index, self.range_support,
                avg_volume, atr, self.range_resistance - self.range_support
            )
            if sow:
                self.events.append(sow)
                self.state = 'SOW_DETECTED'
                self.confidence = 0.75
                result['new_events'].append(sow)
        
        elif self.state == 'UTAD_DETECTED':
            test = detect_test_of_utad(
                self.candles, index, self._get_event('UTAD'), avg_volume, atr
            )
            if test:
                self.events.append(test)
                self.state = 'CONFIRMED'
                self.confidence = 0.90
                result['new_events'].append(test)
                result['signals'].append({
                    'action': 'SELL',
                    'type': 'TEST_OF_UTAD',
                    'entry': candle['close'],
                    'stop_loss': test['stop_loss'],
                    'confidence': test['confidence'],
                })
        
        elif self.state == 'SOW_DETECTED':
            lpsy = detect_last_point_of_supply(
                self.candles, index, self._get_event('SOW'),
                self.range_support, avg_volume, atr
            )
            if lpsy:
                self.events.append(lpsy)
                self.state = 'CONFIRMED'
                self.confidence = 0.85
                result['new_events'].append(lpsy)
                result['signals'].append({
                    'action': 'SELL',
                    'type': 'LPSY',
                    'entry': candle['close'],
                    'stop_loss': lpsy['stop_loss'],
                    'confidence': lpsy['confidence'],
                })
        
        result['state'] = self.state
        result['confidence'] = self.confidence
        return result
    
    def _get_event(self, event_type):
        for e in reversed(self.events):
            if e['event'] == event_type:
                return e
        return None
```

---

## 11. Forex-Specific Distribution

### 11.1 Session-Based Distribution Patterns

| Pattern | Description | Frequency |
|---|---|---|
| **London Open Trap** | Price spikes above Asian high (UTAD), then reverses sharply | Very common |
| **NY Session Reversal** | Distribution completes at London close, markdown in NY | Common |
| **Friday Distribution** | Distribution at week's high, markdown the following week | Moderate |
| **News Spike UTAD** | High-impact news creates a spike above range = UTAD | Moderate |

### 11.2 Central Bank Distribution

When central bank policy shifts from dovish to hawkish (or vice versa), the process often follows Wyckoff distribution:

1. **BC** = final rally on dovish expectation
2. **UTAD** = market prices in "more dovish than expected" → spike
3. **SOW** = hawkish surprise or tone change → breakdown
4. **Markdown** = sustained currency weakening

---

## 12. Crypto-Specific Distribution

### 12.1 On-Chain Distribution Signals

| Metric | Distribution Signal | Confidence |
|---|---|---|
| Exchange inflows > outflows | Coins moving TO exchanges for selling | +15% |
| Whale addresses decreasing | Large holders distributing | +15% |
| Long-term holder (LTH) spending | Smart money taking profits | +10% |
| Stablecoin reserves declining | Buying power being depleted | +10% |
| Funding rate extremely positive | Overleveraged longs (contrarian bearish) | +10% |
| Open interest at extremes | Excessive leverage = liquidation risk | +10% |

### 12.2 Exchange-Specific Manipulation

In crypto, exchanges themselves can act as CM:

- **Spoofing**: Large sell walls that disappear before being filled (creates fear)
- **Wash trading**: Artificial volume to attract buyers during distribution
- **Liquidation cascades**: Pushing price to trigger leveraged liquidations
- **Token unlocks**: Vesting schedules create predetermined supply events

### 12.3 Bitcoin Dominance as Distribution Indicator

When BTC.D (Bitcoin Dominance) rises during a distribution range in altcoins:

$$
\text{Altcoin Distribution Probability} = P_{\text{base}} + \alpha \cdot \Delta BTC.D
$$

Rising BTC.D during an altcoin range = capital rotating out = distribution.

---

## 13. Common Mistakes

### 13.1 Distribution Trading Errors

| # | Mistake | Consequence | Solution |
|---|---|---|---|
| 1 | Shorting too early in Phase B | Caught in range chop, stop losses hit | Wait for UTAD or SOW |
| 2 | Confusing re-accumulation for distribution | Short in an uptrend continuation | Use scoring model; HTF context |
| 3 | No stop loss on shorts | Unlimited loss potential | Always place stops above UTAD |
| 4 | Fighting the trend before confirmation | Multiple small losses | Require SOW or UTAD before shorting |
| 5 | Ignoring funding rates (crypto) | Cost of carry eats profits | Factor funding into R:R calculation |
| 6 | Over-sizing on UTAD before confirmation | Large loss if genuine breakout | Scale in; first position small |
| 7 | Not covering at climactic selling | Missing profit on reversal | Take profits when SC signals appear |

### 13.2 Pattern Quality Checklist for Distribution

```
Distribution Quality Checklist:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ ] Prior uptrend exists (minimum 2x the range height)
[ ] Buying Climax has extreme volume (>= 2.5x average)
[ ] Automatic Reaction defines clear support (Creek)
[ ] Secondary Test(s) show declining buying volume
[ ] Range has been in place for minimum 15 bars
[ ] Volume on rallies is progressively decreasing
[ ] Volume on declines is steady or increasing
[ ] UTAD or SOW event detected
[ ] If UTAD: Test occurred with lower volume and lower high
[ ] If SOW: Volume expanded significantly on breakdown
[ ] Higher timeframe trend shows exhaustion signals
[ ] Distribution vs Re-Accumulation score > 0.65

Score: Count checked items / total items
Minimum score to trade: 7/12 (58%)
High confidence: 10+/12 (83%+)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 14. References

### 14.1 Primary Sources

1. Wyckoff, R.D. (1931). *The Richard D. Wyckoff Method of Trading and Investing in Stocks*. — Distribution schematics and principles.
2. Evans, R. (1969). *Wyckoff Course Notes — Distribution Phase Analysis*. Stock Market Institute.
3. Pruden, H.O. (2007). *The Three Skills of Top Trading*. Wiley. — Chapter 5: "Distribution Phase Behavioral Analysis."

### 14.2 Modern Adaptations

4. Williams, T. (2005). *Master the Markets*. TradeGuider Systems. — Chapters on distribution signals via VSA.
5. Weis, D.H. (2013). *Trades About to Happen*. Wiley. — Distribution wave analysis.
6. Bogomazov, R. (2020). "Identifying Distribution — Wyckoff Analytics Webinar Series." wyckoffanalytics.com.

### 14.3 Crypto-Specific

7. Glassnode Academy. "On-Chain Analysis for Distribution Detection." glassnode.com.
8. Willy Woo (2021). "Bitcoin Whale Distribution Metrics." woobull.com.

---

> **Next Document**: `03_market_structure_bos_choch.md` — Break of Structure & Change of Character
